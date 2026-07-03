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
    drawdown,
    finite_corr,
    load_numeric_for_queue,
    nonoverlap_metric,
    rank_pct,
    sharpe,
    signal_to_weights,
    sortino,
    turnover_cost,
)


DATE = "20260703"
STAGE = "A7SEARCH6-JUNE-BLIND-ADAPTER"
DEFAULT_INPUT = REPO / "runtime" / "a7search6_validation_pack_r2_20260702" / "a7search6_validation_accepted_summary.csv"
DEFAULT_SOURCE_GATE = REPO / "runtime" / "a7search6_v3_source_contract_audit_20260703" / "a7search6_v3_formula_source_gate.csv"
DEFAULT_RUNTIME = REPO / "runtime" / "a7search6_june_blind_adapter_20260703"
DEFAULT_REPORT = REPO / "reports" / "CRYPTO_A7SEARCH6_JUNE_BLIND_ADAPTER_20260703.md"

JUNE_SPLIT = "blind_june2026_20260601_20260611"
JUNE_START = pd.Timestamp("2026-06-01 00:00:00")
JUNE_END = pd.Timestamp("2026-06-11 23:00:00")
TRAIN_END = pd.Timestamp("2024-12-31 23:00:00")


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(frame: pd.DataFrame, max_rows: int = 40) -> str:
    if frame.empty:
        return "`<empty>`"
    view = frame.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    try:
        return view.to_markdown(index=False)
    except Exception:
        return "```text\n" + view.to_string(index=False) + "\n```"


def read_csv_or_empty(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size <= 2:
        return pd.DataFrame()
    try:
        return pd.read_csv(path, low_memory=False)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def forward_label(close: np.ndarray, timestamps: pd.DatetimeIndex, horizon: int, split_end: pd.Timestamp | None = None) -> np.ndarray:
    values = np.where(close > 0, close, np.nan)
    label = dense_shift_matrix(np.log(values), -horizon) - np.log(values)
    if split_end is not None:
        ts = pd.DatetimeIndex(timestamps).tz_localize(None)
        label_end = ts + pd.Timedelta(hours=horizon)
        label[:, label_end > split_end] = np.nan
    return label


def split_metric_one(
    row: dict[str, Any],
    horizon: int,
    variant: str,
    signal: np.ndarray,
    label: np.ndarray,
    mask: np.ndarray,
    quote_volume: np.ndarray,
    cost_bps: float,
    orientation: float,
) -> dict[str, Any]:
    weights = signal_to_weights(signal * orientation)
    gross_forward = np.nansum(weights * label, axis=0)
    cost = turnover_cost(weights, cost_bps)
    net = gross_forward - cost
    periods_per_year = 24.0 * 365.0 / max(1, horizon)
    ret = net[mask]
    cap = np.nansum(np.abs(weights) * quote_volume, axis=0)[mask]
    rank_signal = rank_pct(signal * orientation)[:, mask]
    rank_label = rank_pct(label)[:, mask]
    raw_label = label[:, mask]
    ic_values = [finite_corr(rank_signal[:, i], raw_label[:, i]) for i in range(rank_signal.shape[1])]
    rankic_values = [finite_corr(rank_signal[:, i], rank_label[:, i]) for i in range(rank_signal.shape[1])]
    no_sortino_median, no_sortino_floor = nonoverlap_metric(ret, horizon, lambda x: sortino(x, periods_per_year))
    no_sharpe_median, no_sharpe_floor = nonoverlap_metric(ret, horizon, lambda x: sharpe(x, periods_per_year))
    return {
        "source_blueprint_id": row.get("source_blueprint_id", ""),
        "blueprint_id": row.get("blueprint_id", ""),
        "horizon_h": horizon,
        "variant": variant,
        "split": JUNE_SPLIT,
        "formula": row.get("formula", ""),
        "n_obs": int(np.isfinite(ret).sum()),
        "net_mean": float(np.nanmean(ret)) if np.isfinite(ret).any() else np.nan,
        "net_median": float(np.nanmedian(ret)) if np.isfinite(ret).any() else np.nan,
        "sharpe": sharpe(ret, periods_per_year),
        "sortino": sortino(ret, periods_per_year),
        "nonoverlap_median_sortino": no_sortino_median,
        "nonoverlap_floor_sortino": no_sortino_floor,
        "nonoverlap_median_sharpe": no_sharpe_median,
        "nonoverlap_floor_sharpe": no_sharpe_floor,
        "max_drawdown": drawdown(ret),
        "positive_rate": float(np.nanmean(ret > 0)) if np.isfinite(ret).any() else np.nan,
        "avg_cost": float(np.nanmean(cost[mask])) if np.isfinite(cost[mask]).any() else np.nan,
        "avg_turnover": float(np.nanmean(cost[mask]) / (cost_bps / 10000.0)) if cost_bps > 0 and np.isfinite(cost[mask]).any() else np.nan,
        "ic_mean": float(np.nanmean(ic_values)) if np.isfinite(ic_values).any() else np.nan,
        "rankic_mean": float(np.nanmean(rankic_values)) if np.isfinite(rankic_values).any() else np.nan,
        "capacity_proxy_median_quote_volume": float(np.nanmedian(cap)) if np.isfinite(cap).any() else np.nan,
    }


def orient_on_train(signal: np.ndarray, label: np.ndarray, train_mask: np.ndarray, quote_volume: np.ndarray, cost_bps: float) -> tuple[float, float, float]:
    pos = split_metric_one({}, 24, "orientation_probe_pos", signal, label, train_mask, quote_volume, cost_bps, 1.0)
    neg = split_metric_one({}, 24, "orientation_probe_neg", signal, label, train_mask, quote_volume, cost_bps, -1.0)
    pos_mean = float(pos.get("net_mean", np.nan))
    neg_mean = float(neg.get("net_mean", np.nan))
    orientation = 1.0 if pos_mean >= neg_mean else -1.0
    return orientation, pos_mean, neg_mean


def build_queue(input_path: Path, source_gate_path: Path) -> pd.DataFrame:
    accepted = read_csv_or_empty(input_path)
    if accepted.empty:
        raise RuntimeError(f"missing accepted summary: {input_path}")
    accepted = accepted.copy()
    accepted["expression"] = accepted["formula"].astype(str)
    accepted["candidate_role"] = "june_blind_diagnostic"
    accepted["semantic_pair"] = accepted.get("validation_group", "canonical")
    accepted["motif"] = "a7search6_june_blind"
    accepted["skeleton_key"] = "accepted_formula"
    if source_gate_path.exists():
        gate = pd.read_csv(source_gate_path)
        join_cols = ["source_blueprint_id", "blueprint_id", "horizon_h", "formula_source_gate"]
        if set(join_cols).issubset(gate.columns):
            accepted = accepted.merge(gate[join_cols], on=["source_blueprint_id", "blueprint_id", "horizon_h"], how="left")
    return accepted


def evaluate(input_path: Path, source_gate_path: Path, runtime: Path, report: Path, cost_bps: float) -> dict[str, Any]:
    runtime.mkdir(parents=True, exist_ok=True)
    queue = build_queue(input_path, source_gate_path)
    queue.to_csv(runtime / "a7search6_june_blind_queue.csv", index=False)
    timestamps, old_split, numeric, groups = load_numeric_for_queue(queue, hours_per_split=0, train_hours_per_split=0)
    ts = pd.DatetimeIndex(timestamps).tz_localize(None)
    june_mask = (ts >= JUNE_START) & (ts <= JUNE_END)
    train_mask = ts <= TRAIN_END
    evaluator = A7AB4Evaluator(numeric, groups)
    quote_volume = numeric["trade_quote_volume"]
    labels = {h: forward_label(numeric["trade_close"], timestamps, h, JUNE_END) for h in sorted(queue["horizon_h"].astype(int).unique())}
    train_label_24 = forward_label(numeric["trade_close"], timestamps, 24, TRAIN_END)
    rng = np.random.default_rng(20260703)

    rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for idx, rec in enumerate(queue.to_dict("records"), start=1):
        try:
            signal = evaluator.eval(str(rec["expression"]))
            orientation, train_pos_mean, train_neg_mean = orient_on_train(signal, train_label_24, train_mask, quote_volume, cost_bps)
            horizon = int(rec["horizon_h"])
            base = split_metric_one(rec, horizon, "original", signal, labels[horizon], june_mask, quote_volume, cost_bps, orientation)
            base["orientation"] = orientation
            base["train_orientation_pos_net_mean_24h"] = train_pos_mean
            base["train_orientation_neg_net_mean_24h"] = train_neg_mean
            rows.append(base)
            for variant in CONTROL_VARIANTS:
                ctrl = control_signal(signal, variant, rng)
                metric = split_metric_one(rec, horizon, variant, ctrl, labels[horizon], june_mask, quote_volume, cost_bps, orientation)
                metric["orientation"] = orientation
                metric["train_orientation_pos_net_mean_24h"] = train_pos_mean
                metric["train_orientation_neg_net_mean_24h"] = train_neg_mean
                rows.append(metric)
        except Exception as exc:
            errors.append(
                {
                    "source_blueprint_id": rec.get("source_blueprint_id", ""),
                    "blueprint_id": rec.get("blueprint_id", ""),
                    "horizon_h": rec.get("horizon_h", ""),
                    "formula": rec.get("formula", ""),
                    "error": repr(exc),
                }
            )
        finally:
            evaluator.cache.clear()
        if idx % 4 == 0:
            print(f"[A7SEARCH6-JUNE] evaluated {idx}/{len(queue)}", flush=True)

    metrics = pd.DataFrame(rows)
    errors_df = pd.DataFrame(errors)
    if not metrics.empty:
        original = metrics[metrics["variant"].eq("original")].copy()
        controls = metrics[metrics["variant"].isin(CONTROL_DOMINANCE_VARIANTS)].copy()
        ctrl_summary = (
            controls.groupby(["source_blueprint_id", "blueprint_id", "horizon_h"], as_index=False)
            .agg(max_control_floor_sortino=("nonoverlap_floor_sortino", "max"), max_control_sortino=("sortino", "max"))
        )
        original = original.merge(ctrl_summary, on=["source_blueprint_id", "blueprint_id", "horizon_h"], how="left")
        original["june_control_floor_ratio"] = original["max_control_floor_sortino"] / original["nonoverlap_floor_sortino"].abs().replace(0, np.nan)
        original["june_gate_pass_diagnostic"] = (
            (original["sortino"] > 0)
            & (original["nonoverlap_floor_sortino"] > 0)
            & (original["june_control_floor_ratio"].fillna(99) < 1.0)
        )
        original = original.sort_values(["june_gate_pass_diagnostic", "nonoverlap_floor_sortino", "sortino"], ascending=[False, False, False])
    else:
        original = pd.DataFrame()

    metrics.to_csv(runtime / "a7search6_june_blind_split_metrics.csv", index=False)
    original.to_csv(runtime / "a7search6_june_blind_original_summary.csv", index=False)
    errors_df.to_csv(runtime / "a7search6_june_blind_eval_errors.csv", index=False)

    accepted_diag = int(original["june_gate_pass_diagnostic"].sum()) if "june_gate_pass_diagnostic" in original else 0
    decision = "PASS_A7SEARCH6_JUNE_BLIND_DIAGNOSTIC_NONEMPTY" if accepted_diag > 0 and errors_df.empty else "HOLD_A7SEARCH6_JUNE_BLIND_DIAGNOSTIC"
    manifest = {
        "stage": STAGE,
        "generated_at": now_utc(),
        "decision": decision,
        "input": str(input_path),
        "source_gate": str(source_gate_path),
        "runtime": str(runtime),
        "report": str(report),
        "panel_root": str(DEFAULT_PANEL_ROOT),
        "cost_bps": float(cost_bps),
        "queue_rows": int(queue.shape[0]),
        "metric_rows": int(metrics.shape[0]),
        "eval_error_rows": int(errors_df.shape[0]),
        "june_timestamps": int(june_mask.sum()),
        "train_timestamps_for_orientation": int(train_mask.sum()),
        "diagnostic_pass_rows": accepted_diag,
        "authorizes_next_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "notes": [
            "June split is evaluation-only and is not used for orientation or search selection.",
            "Source contract HOLD from A7SEARCH6-V3 remains in force; this adapter is diagnostic only.",
        ],
    }
    write_json(runtime / "a7search6_june_blind_manifest.json", manifest)

    lines = [
        "# CRYPTO A7SEARCH6 June Blind Adapter",
        "",
        f"Generated: `{manifest['generated_at']}`",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "This evaluates accepted A7SEARCH6 formulas on the available June 2026 patch as a diagnostic blind split. It does not authorize alpha proof, search expansion, shadow, paper, or live.",
        "",
        "## Counts",
        "",
        f"- queue_rows: `{manifest['queue_rows']}`",
        f"- metric_rows: `{manifest['metric_rows']}`",
        f"- eval_error_rows: `{manifest['eval_error_rows']}`",
        f"- june_timestamps: `{manifest['june_timestamps']}`",
        f"- diagnostic_pass_rows: `{manifest['diagnostic_pass_rows']}`",
        "",
        "## Original Formula June Summary",
        "",
        md_table(
            original[
                [
                    "source_blueprint_id",
                    "horizon_h",
                    "june_gate_pass_diagnostic",
                    "n_obs",
                    "sortino",
                    "nonoverlap_floor_sortino",
                    "june_control_floor_ratio",
                    "rankic_mean",
                    "formula",
                ]
            ]
            if not original.empty
            else original,
            max_rows=40,
        ),
        "",
        "## Errors",
        "",
        md_table(errors_df, max_rows=20),
        "",
        "## Required Next Action",
        "",
        "- Keep source-contract HOLD in force. Use this only to prioritize which formulas deserve source timestamp repair first.",
        "",
    ]
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--source-gate", type=Path, default=DEFAULT_SOURCE_GATE)
    parser.add_argument("--runtime", type=Path, default=DEFAULT_RUNTIME)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--cost-bps", type=float, default=5.0)
    args = parser.parse_args()
    manifest = evaluate(args.input, args.source_gate, args.runtime, args.report, args.cost_bps)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
