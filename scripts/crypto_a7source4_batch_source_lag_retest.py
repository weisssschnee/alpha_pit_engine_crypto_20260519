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
    compute_safediv_diagnostics,
    control_signal,
    dense_shift_matrix,
    load_numeric_for_queue,
    signal_to_weights,
)
from alphafactory_crypto.engines.signal_identity import signal_identity_payload  # noqa: E402
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


STAGE = "A7SOURCE-4-BATCH-SOURCE-LAG-RETEST"
DEFAULT_INPUT = REPO / "runtime" / "a7search6_validation_pack_r2_20260702" / "a7search6_validation_accepted_summary.csv"
DEFAULT_RUNTIME = REPO / "runtime" / "a7source4_batch_source_lag_retest_20260703"
DEFAULT_REPORT = REPO / "reports" / "CRYPTO_A7SOURCE4_BATCH_SOURCE_LAG_RETEST_20260703.md"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_csv_or_empty(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size <= 2:
        return pd.DataFrame()
    try:
        return pd.read_csv(path, low_memory=False)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def normalize_queue(path: Path, max_rows: int) -> pd.DataFrame:
    frame = read_csv_or_empty(path)
    if frame.empty:
        raise RuntimeError(f"missing input queue: {path}")
    frame = frame.copy()
    if "formula" not in frame.columns and "expression" in frame.columns:
        frame["formula"] = frame["expression"]
    if "expression" not in frame.columns:
        frame["expression"] = frame["formula"].astype(str)
    if "source_blueprint_id" not in frame.columns:
        frame["source_blueprint_id"] = frame.get("blueprint_id", "")
    if "horizon_h" not in frame.columns:
        raise RuntimeError("input queue requires horizon_h")
    sort_cols = [col for col in ["min_oos_floor_sortino", "recent_sortino", "nonoverlap_floor_sortino", "sortino"] if col in frame.columns]
    for col in sort_cols:
        frame[col] = pd.to_numeric(frame[col], errors="coerce")
    if sort_cols:
        frame = frame.sort_values(sort_cols, ascending=[False] * len(sort_cols))
    frame = frame.head(max_rows).copy()
    frame["candidate_role"] = "source_lag_retest"
    frame["semantic_pair"] = frame.get("semantic_pair", "a7source4")
    frame["motif"] = "batch_source_lag_retest"
    frame["skeleton_key"] = "whole_signal_source_lag"
    return frame.reset_index(drop=True)


def summarize(metrics: pd.DataFrame) -> pd.DataFrame:
    if metrics.empty:
        return pd.DataFrame()
    index_columns = ["source_blueprint_id", "blueprint_id", "horizon_h", "formula"]
    metadata_columns = [
        column
        for column in [
            "signal_weight_exact_fingerprint",
            "signal_weight_quantized_fingerprint",
            "signal_weight_similarity_sketch",
            "safediv_node_count",
            "safediv_denominator_min_abs_q01",
            "safediv_denominator_min_abs_q05",
            "safediv_denominator_min_q01_to_median",
            "safediv_denominator_max_near_zero_ratio",
            "safediv_local_rank_stability_min",
            "signal_abs_p99_to_median",
            "signal_top1pct_abs_mass_share",
            "safediv_review_flag",
            "safediv_review_reasons",
        ]
        if column in metrics.columns
    ]
    metadata = metrics[index_columns + metadata_columns].drop_duplicates(index_columns, keep="first")
    pivot = metrics.pivot_table(
        index=index_columns,
        columns="variant",
        values=["sortino", "nonoverlap_floor_sortino", "rankic_mean"],
        aggfunc="first",
    )
    pivot.columns = [f"{a}_{b}" for a, b in pivot.columns]
    out = pivot.reset_index().merge(metadata, on=index_columns, how="left")
    required = [
        "sortino_source_lag_1h",
        "sortino_source_lag_2h",
        "nonoverlap_floor_sortino_source_lag_1h",
        "nonoverlap_floor_sortino_source_lag_2h",
    ]
    for col in required:
        if col not in out.columns:
            out[col] = np.nan
    out["source_lag_gate"] = np.where(
        (out["sortino_source_lag_1h"] > 0)
        & (out["sortino_source_lag_2h"] > 0)
        & (out["nonoverlap_floor_sortino_source_lag_1h"] > 0)
        & (out["nonoverlap_floor_sortino_source_lag_2h"] > 0),
        "PASS_SOURCE_LAG_1H_2H_DIAGNOSTIC",
        "HOLD_SOURCE_LAG_FRAGILE",
    )
    if "nonoverlap_floor_sortino_original" in out.columns:
        for lag in ["1h", "2h", "4h"]:
            col = f"nonoverlap_floor_sortino_source_lag_{lag}"
            if col in out.columns:
                out[f"floor_retention_source_lag_{lag}"] = out[col] / out["nonoverlap_floor_sortino_original"].abs().replace(0, np.nan)
    out["_source_lag_gate_rank"] = np.where(out["source_lag_gate"].eq("PASS_SOURCE_LAG_1H_2H_DIAGNOSTIC"), 0, 1)
    out = out.sort_values(
        ["_source_lag_gate_rank", "nonoverlap_floor_sortino_source_lag_2h", "sortino_source_lag_2h"],
        ascending=[True, False, False],
    ).drop(columns=["_source_lag_gate_rank"])
    return out


def write_outputs(runtime: Path, report: Path, queue: pd.DataFrame, metrics: pd.DataFrame, errors: pd.DataFrame) -> dict[str, Any]:
    summary = summarize(metrics)
    metrics.to_csv(runtime / "a7source4_source_lag_metrics.csv", index=False)
    errors.to_csv(runtime / "a7source4_eval_errors.csv", index=False)
    summary.to_csv(runtime / "a7source4_source_lag_summary.csv", index=False)
    pass_count = int(summary["source_lag_gate"].eq("PASS_SOURCE_LAG_1H_2H_DIAGNOSTIC").sum()) if not summary.empty else 0
    decision = "PASS_A7SOURCE4_BATCH_SOURCE_LAG_SURVIVORS_FOUND" if pass_count > 0 and errors.empty else "HOLD_A7SOURCE4_BATCH_SOURCE_LAG_FRAGILE"
    manifest = {
        "stage": STAGE,
        "generated_at": now_utc(),
        "decision": decision,
        "runtime": str(runtime),
        "report": str(report),
        "queue_rows": int(queue.shape[0]),
        "metric_rows": int(metrics.shape[0]),
        "eval_error_rows": int(errors.shape[0]),
        "source_lag_pass_count": pass_count,
        "signal_identity_rows": int(summary["signal_weight_exact_fingerprint"].notna().sum()) if "signal_weight_exact_fingerprint" in summary else 0,
        "safediv_review_rows": int(summary["safediv_review_flag"].fillna(False).astype(bool).sum()) if "safediv_review_flag" in summary else 0,
        "authorizes_next_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(runtime / "a7source4_manifest.json", manifest)
    lines = [
        "# CRYPTO A7SOURCE-4 Batch Source-Lag Retest",
        "",
        f"Generated: `{manifest['generated_at']}`",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "This retests accepted formulas after delaying the whole signal by 1h, 2h, and 4h. It is a leakage-sensitivity diagnostic, not alpha proof.",
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
        md_table(summary, 80),
        "",
        "## Errors",
        "",
        md_table(errors, 40),
        "",
        "## Boundary",
        "",
        "Passing this retest does not prove vendor publication timing. It only identifies formulas whose signal remains positive after conservative signal delay.",
        "",
    ]
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return manifest


def run(input_path: Path, runtime: Path, report: Path, cost_bps: float, max_rows: int) -> dict[str, Any]:
    runtime.mkdir(parents=True, exist_ok=True)
    queue = normalize_queue(input_path, max_rows)
    queue.to_csv(runtime / "a7source4_source_lag_queue.csv", index=False)
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
    variants = {"original": 0, "source_lag_1h": 1, "source_lag_2h": 2, "source_lag_4h": 4}
    for idx, rec in enumerate(queue.to_dict("records"), start=1):
        try:
            signal = evaluator.eval(str(rec["expression"]))
            identity = signal_identity_payload(signal_to_weights(signal))
            safediv_diagnostics = compute_safediv_diagnostics(evaluator, str(rec["expression"]), signal)
            diagnostics = {**identity, **safediv_diagnostics}
            orientation, pos_mean, neg_mean = orient_on_train(signal, train_label_24, train_mask, quote_volume, cost_bps)
            horizon = int(rec["horizon_h"])
            for variant, lag in variants.items():
                sig = dense_shift_matrix(signal, lag) if lag else signal
                metric = split_metric_one(rec, horizon, variant, sig, labels[horizon], june_mask, quote_volume, cost_bps, orientation)
                metric["source_lag_hours"] = lag
                metric["orientation"] = orientation
                metric["train_orientation_pos_net_mean_24h"] = pos_mean
                metric["train_orientation_neg_net_mean_24h"] = neg_mean
                metric.update(diagnostics)
                rows.append(metric)
            ctrl = control_signal(signal, "one_bar_lag", rng)
            metric = split_metric_one(rec, horizon, "control_one_bar_lag", ctrl, labels[horizon], june_mask, quote_volume, cost_bps, orientation)
            metric["source_lag_hours"] = 1
            metric["orientation"] = orientation
            metric.update(diagnostics)
            rows.append(metric)
        except Exception as exc:
            errors.append(
                {
                    "source_blueprint_id": rec.get("source_blueprint_id", ""),
                    "blueprint_id": rec.get("blueprint_id", ""),
                    "horizon_h": rec.get("horizon_h", ""),
                    "formula": rec.get("formula", rec.get("expression", "")),
                    "error": repr(exc),
                }
            )
        finally:
            evaluator.cache.clear()
        write_outputs(runtime, report, queue.iloc[:idx].copy(), pd.DataFrame(rows), pd.DataFrame(errors))
        print(f"[A7SOURCE4] checkpoint {idx}/{len(queue)}", flush=True)
    return write_outputs(runtime, report, queue, pd.DataFrame(rows), pd.DataFrame(errors))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--runtime", type=Path, default=DEFAULT_RUNTIME)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--cost-bps", type=float, default=5.0)
    parser.add_argument("--max-rows", type=int, default=80)
    args = parser.parse_args()
    manifest = run(args.input, args.runtime, args.report, args.cost_bps, args.max_rows)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
