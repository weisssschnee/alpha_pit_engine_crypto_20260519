from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


DEFAULT_PANEL_ROOT = Path(
    os.environ.get(
        "A7SEARCH6_JUNE_PANEL_ROOT",
        r"G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v3_patch_age_20260613",
    )
)
os.environ.setdefault("A7AL_BASE_PANEL_ROOT", str(DEFAULT_PANEL_ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from scripts.crypto_a7reward1_portfolio_reward_model import (  # noqa: E402
    A7AB4Evaluator,
    CONTROL_DOMINANCE_VARIANTS,
    CONTROL_VARIANTS,
    control_signal,
    dense_shift_matrix,
    expression_fields,
    load_numeric_for_queue,
)
from scripts.crypto_a7search6_june_blind_adapter import (  # noqa: E402
    JUNE_END,
    JUNE_START,
    TRAIN_END,
    forward_label,
    md_table,
    orient_on_train,
    split_metric_one,
    write_json,
)


DATE = "20260703"
STAGE = "A7SEARCH6-SOURCE-LAG-RETEST"
DEFAULT_INPUT = REPO / "runtime" / "a7search6_june_blind_adapter_20260703" / "a7search6_june_blind_original_summary.csv"
DEFAULT_RUNTIME = REPO / "runtime" / "a7search6_source_lag_retest_20260703"
DEFAULT_REPORT = REPO / "reports" / "CRYPTO_A7SEARCH6_SOURCE_LAG_RETEST_20260703.md"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_csv_or_empty(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size <= 2:
        return pd.DataFrame()
    try:
        return pd.read_csv(path, low_memory=False)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def field_family(field: str) -> str:
    if "funding" in field:
        return "funding_state"
    if "open_interest" in field:
        return "open_interest"
    if "long_short" in field or "position" in field:
        return "positioning"
    if "stress_proxy" in field or "regime" in field or "state" in field:
        return "regime_state"
    if "basis" in field or "premium" in field or "mark" in field or "index" in field:
        return "basis_premium"
    if "taker" in field:
        return "taker_flow"
    if "volume" in field or "liquidity" in field:
        return "liquidity"
    return "other"


RISK_FAMILIES = {"open_interest", "funding_state", "positioning", "regime_state"}


def risk_fields_for_expression(expr: str, target: str) -> list[str]:
    fields = expression_fields(expr)
    out = []
    for field in fields:
        fam = field_family(field)
        if target == "all_risk" and fam in RISK_FAMILIES:
            out.append(field)
        elif target == fam:
            out.append(field)
    return sorted(set(out))


def load_queue(input_path: Path) -> pd.DataFrame:
    frame = read_csv_or_empty(input_path)
    if frame.empty:
        raise RuntimeError(f"missing input: {input_path}")
    if "june_gate_pass_diagnostic" in frame.columns:
        frame = frame[frame["june_gate_pass_diagnostic"].astype(str).str.lower().eq("true")].copy()
    frame = frame.copy()
    frame["expression"] = frame["formula"].astype(str)
    frame["candidate_role"] = "source_lag_retest"
    frame["semantic_pair"] = "a7search6_june_survivor"
    frame["motif"] = "source_lag_retest"
    frame["skeleton_key"] = "accepted_formula_source_lag"
    return frame.reset_index(drop=True)


def variant_specs() -> list[dict[str, Any]]:
    return [
        {"variant": "original", "target": "none", "lag_hours": 0},
        {"variant": "all_risk_lag1h", "target": "all_risk", "lag_hours": 1},
        {"variant": "all_risk_lag2h", "target": "all_risk", "lag_hours": 2},
        {"variant": "all_risk_lag8h", "target": "all_risk", "lag_hours": 8},
        {"variant": "open_interest_lag1h", "target": "open_interest", "lag_hours": 1},
        {"variant": "funding_state_lag1h", "target": "funding_state", "lag_hours": 1},
        {"variant": "positioning_lag1h", "target": "positioning", "lag_hours": 1},
        {"variant": "regime_state_lag1h", "target": "regime_state", "lag_hours": 1},
    ]


def shifted_numeric(numeric: dict[str, np.ndarray], fields: list[str], lag_hours: int) -> dict[str, np.ndarray]:
    if lag_hours <= 0 or not fields:
        return numeric
    out = dict(numeric)
    for field in fields:
        if field in out:
            out[field] = dense_shift_matrix(out[field], lag_hours)
    return out


def evaluate(input_path: Path, runtime: Path, report: Path, cost_bps: float) -> dict[str, Any]:
    runtime.mkdir(parents=True, exist_ok=True)
    queue = load_queue(input_path)
    queue.to_csv(runtime / "a7search6_source_lag_retest_queue.csv", index=False)
    timestamps, old_split, numeric, groups = load_numeric_for_queue(queue, hours_per_split=0, train_hours_per_split=0)
    ts = pd.DatetimeIndex(timestamps).tz_localize(None)
    june_mask = (ts >= JUNE_START) & (ts <= JUNE_END)
    train_mask = ts <= TRAIN_END
    quote_volume = numeric["trade_quote_volume"]
    horizons = sorted(queue["horizon_h"].astype(int).unique())
    labels = {h: forward_label(numeric["trade_close"], timestamps, h, JUNE_END) for h in horizons}
    train_label_24 = forward_label(numeric["trade_close"], timestamps, 24, TRAIN_END)

    metric_rows: list[dict[str, Any]] = []
    sensitivity_rows: list[dict[str, Any]] = []
    error_rows: list[dict[str, Any]] = []

    for rec in queue.to_dict("records"):
        expr = str(rec["expression"])
        horizon = int(rec["horizon_h"])
        for spec in variant_specs():
            lagged_fields = risk_fields_for_expression(expr, str(spec["target"]))
            if spec["variant"] != "original" and not lagged_fields:
                continue
            try:
                num = shifted_numeric(numeric, lagged_fields, int(spec["lag_hours"]))
                evaluator = A7AB4Evaluator(num, groups)
                signal = evaluator.eval(expr)
                orientation, train_pos_mean, train_neg_mean = orient_on_train(
                    signal,
                    train_label_24,
                    train_mask,
                    quote_volume,
                    cost_bps,
                )
                base = split_metric_one(rec, horizon, str(spec["variant"]), signal, labels[horizon], june_mask, quote_volume, cost_bps, orientation)
                base["lagged_fields"] = "|".join(lagged_fields)
                base["lag_hours"] = int(spec["lag_hours"])
                base["lag_target"] = str(spec["target"])
                base["orientation"] = orientation
                base["train_orientation_pos_net_mean_24h"] = train_pos_mean
                base["train_orientation_neg_net_mean_24h"] = train_neg_mean
                metric_rows.append(base)
                rng = np.random.default_rng(20260703 + int(spec["lag_hours"]))
                for control in CONTROL_VARIANTS:
                    ctrl = control_signal(signal, control, rng)
                    row = split_metric_one(rec, horizon, f"{spec['variant']}::{control}", ctrl, labels[horizon], june_mask, quote_volume, cost_bps, orientation)
                    row["lagged_fields"] = "|".join(lagged_fields)
                    row["lag_hours"] = int(spec["lag_hours"])
                    row["lag_target"] = str(spec["target"])
                    metric_rows.append(row)
            except Exception as exc:
                error_rows.append(
                    {
                        "source_blueprint_id": rec.get("source_blueprint_id", ""),
                        "blueprint_id": rec.get("blueprint_id", ""),
                        "horizon_h": horizon,
                        "variant": spec["variant"],
                        "lagged_fields": "|".join(lagged_fields),
                        "error": repr(exc),
                        "formula": expr,
                    }
                )

    metrics = pd.DataFrame(metric_rows)
    errors = pd.DataFrame(error_rows)
    if not metrics.empty:
        base_variants = metrics[~metrics["variant"].astype(str).str.contains("::", regex=False)].copy()
        controls = metrics[metrics["variant"].astype(str).str.contains("::", regex=False)].copy()
        controls["base_variant"] = controls["variant"].astype(str).str.split("::", n=1).str[0]
        controls["control_variant"] = controls["variant"].astype(str).str.split("::", n=1).str[1]
        ctrl = (
            controls[controls["control_variant"].isin(CONTROL_DOMINANCE_VARIANTS)]
            .groupby(["source_blueprint_id", "blueprint_id", "horizon_h", "base_variant"], as_index=False)
            .agg(max_control_floor_sortino=("nonoverlap_floor_sortino", "max"), max_control_sortino=("sortino", "max"))
            .rename(columns={"base_variant": "variant"})
        )
        base_variants = base_variants.merge(ctrl, on=["source_blueprint_id", "blueprint_id", "horizon_h", "variant"], how="left")
        base_variants["control_floor_ratio"] = base_variants["max_control_floor_sortino"] / base_variants["nonoverlap_floor_sortino"].abs().replace(0, np.nan)
        base_variants["lag_gate_pass"] = (
            (base_variants["sortino"] > 0)
            & (base_variants["nonoverlap_floor_sortino"] > 0)
            & (base_variants["control_floor_ratio"].fillna(99) < 1.0)
        )
        originals = base_variants[base_variants["variant"].eq("original")][
            ["source_blueprint_id", "horizon_h", "sortino", "nonoverlap_floor_sortino"]
        ].rename(columns={"sortino": "original_sortino", "nonoverlap_floor_sortino": "original_floor_sortino"})
        sensitivity = base_variants.merge(originals, on=["source_blueprint_id", "horizon_h"], how="left")
        sensitivity["floor_retention_ratio"] = sensitivity["nonoverlap_floor_sortino"] / sensitivity["original_floor_sortino"].abs().replace(0, np.nan)
        sensitivity = sensitivity.sort_values(
            ["source_blueprint_id", "horizon_h", "variant"],
            ascending=[True, True, True],
        )
    else:
        base_variants = pd.DataFrame()
        sensitivity = pd.DataFrame()

    metrics.to_csv(runtime / "a7search6_source_lag_retest_metrics.csv", index=False)
    base_variants.to_csv(runtime / "a7search6_source_lag_retest_base_variants.csv", index=False)
    sensitivity.to_csv(runtime / "a7search6_source_lag_retest_sensitivity.csv", index=False)
    errors.to_csv(runtime / "a7search6_source_lag_retest_errors.csv", index=False)

    all_risk_lag1 = sensitivity[sensitivity["variant"].eq("all_risk_lag1h")] if not sensitivity.empty else pd.DataFrame()
    all_risk_lag2 = sensitivity[sensitivity["variant"].eq("all_risk_lag2h")] if not sensitivity.empty else pd.DataFrame()
    pass_lag1 = int(all_risk_lag1["lag_gate_pass"].sum()) if "lag_gate_pass" in all_risk_lag1 else 0
    pass_lag2 = int(all_risk_lag2["lag_gate_pass"].sum()) if "lag_gate_pass" in all_risk_lag2 else 0
    decision = "PASS_A7SEARCH6_SOURCE_LAG_SURVIVORS_FOUND" if pass_lag1 > 0 and errors.empty else "HOLD_A7SEARCH6_SOURCE_LAG_FRAGILE"
    manifest = {
        "stage": STAGE,
        "generated_at": now_utc(),
        "decision": decision,
        "input": str(input_path),
        "runtime": str(runtime),
        "report": str(report),
        "panel_root": str(DEFAULT_PANEL_ROOT),
        "queue_rows": int(queue.shape[0]),
        "metric_rows": int(metrics.shape[0]),
        "error_rows": int(errors.shape[0]),
        "all_risk_lag1_pass_rows": pass_lag1,
        "all_risk_lag2_pass_rows": pass_lag2,
        "authorizes_source_contract_repair_priority": True,
        "authorizes_next_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(runtime / "a7search6_source_lag_retest_manifest.json", manifest)

    lines = [
        "# CRYPTO A7SEARCH6 Source Lag Retest",
        "",
        f"Generated: `{manifest['generated_at']}`",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "This retests only June diagnostic survivors under delayed source-field variants. It is a leakage-sensitivity diagnostic, not alpha proof.",
        "",
        "## Counts",
        "",
        f"- queue_rows: `{manifest['queue_rows']}`",
        f"- metric_rows: `{manifest['metric_rows']}`",
        f"- error_rows: `{manifest['error_rows']}`",
        f"- all_risk_lag1_pass_rows: `{manifest['all_risk_lag1_pass_rows']}`",
        f"- all_risk_lag2_pass_rows: `{manifest['all_risk_lag2_pass_rows']}`",
        "",
        "## Sensitivity Summary",
        "",
        md_table(
            sensitivity[
                [
                    "source_blueprint_id",
                    "horizon_h",
                    "variant",
                    "lagged_fields",
                    "lag_gate_pass",
                    "sortino",
                    "nonoverlap_floor_sortino",
                    "floor_retention_ratio",
                    "control_floor_ratio",
                    "formula",
                ]
            ]
            if not sensitivity.empty
            else sensitivity,
            max_rows=80,
        ),
        "",
        "## Errors",
        "",
        md_table(errors, max_rows=20),
        "",
        "## Decision Boundary",
        "",
        "- Passing this retest does not prove source timing. It only means delayed-source versions remain worth source timestamp repair.",
        "- Broad search remains blocked until source contracts for OI, positioning, funding-state, and regime-state are wired into the loader.",
        "",
    ]
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--runtime", type=Path, default=DEFAULT_RUNTIME)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--cost-bps", type=float, default=5.0)
    args = parser.parse_args()
    manifest = evaluate(args.input, args.runtime, args.report, args.cost_bps)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
