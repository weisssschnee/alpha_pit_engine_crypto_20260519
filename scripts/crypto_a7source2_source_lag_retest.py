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
    control_signal,
    dense_shift_matrix,
    load_numeric_for_queue,
)
from scripts.crypto_a7search6_june_blind_adapter import (  # noqa: E402
    JUNE_END,
    JUNE_START,
    TRAIN_END,
    forward_label,
    orient_on_train,
    split_metric_one,
)


STAGE = "A7SOURCE-2-SOURCE-LAG-RETEST"
DEFAULT_INPUT = REPO / "runtime" / "a7search6_june_blind_adapter_20260703" / "a7search6_june_blind_original_summary.csv"
DEFAULT_SOURCE1 = REPO / "runtime" / "a7source1_field_timing_proof_20260703" / "a7source1_formula_proof_gate.csv"
DEFAULT_RUNTIME = REPO / "runtime" / "a7source2_source_lag_retest_20260703"
DEFAULT_REPORT = REPO / "reports" / "CRYPTO_A7SOURCE2_SOURCE_LAG_RETEST_20260703.md"
JUNE_SPLIT = "blind_june2026_20260601_20260611"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(frame: pd.DataFrame, max_rows: int = 50) -> str:
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


def build_queue(input_path: Path, max_rows: int) -> pd.DataFrame:
    frame = read_csv_or_empty(input_path)
    if frame.empty:
        raise RuntimeError(f"missing june summary: {input_path}")
    if "june_gate_pass_diagnostic" in frame.columns:
        frame = frame[frame["june_gate_pass_diagnostic"].astype(str).str.lower().eq("true")].copy()
    if frame.empty:
        raise RuntimeError("no June diagnostic pass rows to retest")
    frame = frame.sort_values(["nonoverlap_floor_sortino", "sortino"], ascending=False).head(max_rows).copy()
    frame["expression"] = frame["formula"].astype(str)
    frame["candidate_role"] = "source_lag_retest"
    frame["semantic_pair"] = "a7source2"
    frame["motif"] = "source_lag_retest"
    frame["skeleton_key"] = "source_lag_retest"
    return frame


def retest(input_path: Path, source1_path: Path, runtime: Path, report: Path, cost_bps: float, max_rows: int) -> dict[str, Any]:
    runtime.mkdir(parents=True, exist_ok=True)
    queue = build_queue(input_path, max_rows)
    queue.to_csv(runtime / "a7source2_source_lag_queue.csv", index=False)
    source1 = read_csv_or_empty(source1_path)
    timestamps, _, numeric, groups = load_numeric_for_queue(queue, hours_per_split=0, train_hours_per_split=0)
    ts = pd.DatetimeIndex(timestamps).tz_localize(None)
    june_mask = (ts >= JUNE_START) & (ts <= JUNE_END)
    train_mask = ts <= TRAIN_END
    evaluator = A7AB4Evaluator(numeric, groups)
    quote_volume = numeric["trade_quote_volume"]
    horizons = sorted(queue["horizon_h"].astype(int).unique())
    labels = {h: forward_label(numeric["trade_close"], timestamps, h, JUNE_END) for h in horizons}
    train_label_24 = forward_label(numeric["trade_close"], timestamps, 24, TRAIN_END)
    rng = np.random.default_rng(20260703)
    rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    lag_variants = {"original": 0, "source_lag_1h": 1, "source_lag_2h": 2, "source_lag_4h": 4}
    for idx, rec in enumerate(queue.to_dict("records"), start=1):
        try:
            signal = evaluator.eval(str(rec["expression"]))
            orientation, pos_mean, neg_mean = orient_on_train(signal, train_label_24, train_mask, quote_volume, cost_bps)
            horizon = int(rec["horizon_h"])
            for variant, lag in lag_variants.items():
                sig = dense_shift_matrix(signal, lag) if lag else signal
                metric = split_metric_one(rec, horizon, variant, sig, labels[horizon], june_mask, quote_volume, cost_bps, orientation)
                metric["source_lag_hours"] = lag
                metric["orientation"] = orientation
                metric["train_orientation_pos_net_mean_24h"] = pos_mean
                metric["train_orientation_neg_net_mean_24h"] = neg_mean
                rows.append(metric)
            ctrl = control_signal(signal, "one_bar_lag", rng)
            metric = split_metric_one(rec, horizon, "control_one_bar_lag", ctrl, labels[horizon], june_mask, quote_volume, cost_bps, orientation)
            metric["source_lag_hours"] = 1
            metric["orientation"] = orientation
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
        print(f"[A7SOURCE2] evaluated {idx}/{len(queue)}", flush=True)

    metrics = pd.DataFrame(rows)
    errors_df = pd.DataFrame(errors)
    metrics.to_csv(runtime / "a7source2_source_lag_metrics.csv", index=False)
    errors_df.to_csv(runtime / "a7source2_eval_errors.csv", index=False)
    if metrics.empty:
        summary = pd.DataFrame()
    else:
        pivot = metrics.pivot_table(
            index=["source_blueprint_id", "blueprint_id", "horizon_h", "formula"],
            columns="variant",
            values=["sortino", "nonoverlap_floor_sortino", "rankic_mean"],
            aggfunc="first",
        )
        pivot.columns = [f"{a}_{b}" for a, b in pivot.columns]
        summary = pivot.reset_index()
        for col in [
            "nonoverlap_floor_sortino_source_lag_1h",
            "nonoverlap_floor_sortino_source_lag_2h",
            "sortino_source_lag_1h",
            "sortino_source_lag_2h",
        ]:
            if col not in summary.columns:
                summary[col] = np.nan
        summary["source_lag_gate"] = np.where(
            (summary["nonoverlap_floor_sortino_source_lag_1h"] > 0)
            & (summary["nonoverlap_floor_sortino_source_lag_2h"] > 0)
            & (summary["sortino_source_lag_1h"] > 0)
            & (summary["sortino_source_lag_2h"] > 0),
            "PASS_SOURCE_LAG_1H_2H_DIAGNOSTIC",
            "HOLD_SOURCE_LAG_FRAGILE",
        )
        if not source1.empty and "source_blueprint_id" in source1.columns:
            summary = summary.merge(
                source1[["source_blueprint_id", "horizon_h", "formula_decision", "field_proof_decisions"]].drop_duplicates(),
                on=["source_blueprint_id", "horizon_h"],
                how="left",
            )
        summary = summary.sort_values(
            ["source_lag_gate", "nonoverlap_floor_sortino_source_lag_2h", "sortino_source_lag_2h"],
            ascending=[True, False, False],
        )
    summary.to_csv(runtime / "a7source2_source_lag_summary.csv", index=False)

    pass_count = int(summary["source_lag_gate"].eq("PASS_SOURCE_LAG_1H_2H_DIAGNOSTIC").sum()) if not summary.empty else 0
    decision = "PASS_A7SOURCE2_SOURCE_LAG_SURVIVORS_FOUND" if pass_count > 0 and errors_df.empty else "HOLD_A7SOURCE2_SOURCE_LAG_FRAGILE"
    manifest = {
        "stage": STAGE,
        "generated_at": now_utc(),
        "decision": decision,
        "input": str(input_path),
        "source1": str(source1_path),
        "runtime": str(runtime),
        "report": str(report),
        "panel_root": str(DEFAULT_PANEL_ROOT),
        "queue_rows": int(queue.shape[0]),
        "metric_rows": int(metrics.shape[0]),
        "eval_error_rows": int(errors_df.shape[0]),
        "source_lag_pass_count": pass_count,
        "june_timestamps": int(june_mask.sum()),
        "authorizes_next_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(runtime / "a7source2_manifest.json", manifest)
    lines = [
        "# CRYPTO A7SOURCE-2 Source-Lag Retest",
        "",
        f"Generated: `{manifest['generated_at']}`",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "This retests June-diagnostic survivors after delaying the whole signal by 1h, 2h, and 4h. It is diagnostic only and does not override A7SOURCE-1 source-contract holds.",
        "",
        "## Counts",
        "",
        f"- queue_rows: `{manifest['queue_rows']}`",
        f"- metric_rows: `{manifest['metric_rows']}`",
        f"- eval_error_rows: `{manifest['eval_error_rows']}`",
        f"- source_lag_pass_count: `{manifest['source_lag_pass_count']}`",
        "",
        "## Source-Lag Summary",
        "",
        md_table(summary, max_rows=20),
        "",
        "## Errors",
        "",
        md_table(errors_df, max_rows=20),
        "",
    ]
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--source1", type=Path, default=DEFAULT_SOURCE1)
    parser.add_argument("--runtime", type=Path, default=DEFAULT_RUNTIME)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--cost-bps", type=float, default=5.0)
    parser.add_argument("--max-rows", type=int, default=3)
    args = parser.parse_args()
    manifest = retest(args.input, args.source1, args.runtime, args.report, args.cost_bps, args.max_rows)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
