from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.crypto_a7aa1_primitive_response_map import horizon_label  # noqa: E402
from scripts.crypto_a7ab4_materialization_preflight import A7AB4Evaluator  # noqa: E402
from scripts.crypto_a7reward1_portfolio_reward_model import (  # noqa: E402
    ALL_EVAL_SPLITS,
    HORIZONS,
    load_numeric_for_queue,
    rank_pct,
    signal_to_weights,
    sortino,
    sharpe,
    drawdown,
)


DEFAULT_QUEUE = "runtime/a7shadow3_execution_realism_summary_20260703/a7shadow3_execution_accepted.csv"
DEFAULT_RUNTIME = "runtime/a7shadow4_live_capacity_correlation_20260704"
DEFAULT_REPORT = "reports/CRYPTO_A7SHADOW4_LIVE_CAPACITY_CORRELATION_20260704.md"
FIELD_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
OPERATORS = {
    "Abs",
    "Add",
    "CSRank",
    "Decay",
    "Delta",
    "Mean",
    "Mul",
    "Neg",
    "Rank",
    "SafeDiv",
    "Sign",
    "Sub",
    "TSRank",
    "ZScore",
    "abs",
    "add",
    "csrank",
    "decay",
    "delta",
    "mean",
    "mul",
    "neg",
    "rank",
    "safediv",
    "sign",
    "sub",
    "tsrank",
    "zscore",
}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 40) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    try:
        return view.to_markdown(index=False)
    except ImportError:
        return "```text\n" + view.to_string(index=False) + "\n```"


def expression_fields(expression: str) -> set[str]:
    return {tok for tok in FIELD_RE.findall(str(expression)) if tok not in OPERATORS and tok.lower() not in {"nan", "inf"}}


def finite_corr(x: np.ndarray, y: np.ndarray) -> float:
    a = np.asarray(x, dtype=np.float64).reshape(-1)
    b = np.asarray(y, dtype=np.float64).reshape(-1)
    m = np.isfinite(a) & np.isfinite(b)
    if int(m.sum()) < 10:
        return np.nan
    aa = a[m]
    bb = b[m]
    if float(np.nanstd(aa)) <= 1e-12 or float(np.nanstd(bb)) <= 1e-12:
        return np.nan
    return float(np.corrcoef(aa, bb)[0, 1])


def one_way_turnover(weights: np.ndarray) -> np.ndarray:
    prev = np.zeros((weights.shape[0], 1), dtype=np.float64)
    delta = np.diff(np.concatenate([prev, weights], axis=1), axis=1)
    return np.nansum(np.abs(delta), axis=0) / 2.0


def choose_orientation(signal: np.ndarray, label: np.ndarray, split: np.ndarray, quote_volume: np.ndarray, cost_bps: float) -> float:
    train = split == "train_2024"
    best_orientation = 1.0
    best_mean = -np.inf
    for orientation in [1.0, -1.0]:
        weights = signal_to_weights(signal * orientation)
        gross = np.nansum(weights * label, axis=0)
        net = gross - one_way_turnover(weights) * cost_bps / 10000.0
        mean = float(np.nanmean(net[train])) if np.isfinite(net[train]).any() else -np.inf
        if mean > best_mean:
            best_mean = mean
            best_orientation = orientation
    return best_orientation


def metric_row(
    candidate: dict[str, Any],
    signal: np.ndarray,
    label: np.ndarray,
    split: np.ndarray,
    quote_volume: np.ndarray,
    cost_bps: float,
    orientation: float,
    split_name: str,
) -> dict[str, Any]:
    weights = signal_to_weights(signal * orientation)
    gross = np.nansum(weights * label, axis=0)
    turnover = one_way_turnover(weights)
    cost = turnover * cost_bps / 10000.0
    net = gross - cost
    capacity = np.nansum(np.abs(weights) * quote_volume, axis=0)
    traded_liquidity = np.nansum(np.abs(np.diff(np.concatenate([np.zeros((weights.shape[0], 1)), weights], axis=1), axis=1)) * quote_volume, axis=0)
    mask = split == split_name
    x = net[mask]
    cap = capacity[mask]
    traded = traded_liquidity[mask]
    periods_per_year = 24.0 * 365.0 / max(1, int(candidate["horizon_h"]))
    return {
        "blueprint_id": candidate["blueprint_id"],
        "horizon_h": int(candidate["horizon_h"]),
        "expression": candidate["expression"],
        "cost_bps": cost_bps,
        "split": split_name,
        "n_obs": int(np.isfinite(x).sum()),
        "net_mean": float(np.nanmean(x)) if np.isfinite(x).any() else np.nan,
        "sharpe": sharpe(x, periods_per_year),
        "sortino": sortino(x, periods_per_year),
        "max_drawdown": drawdown(x),
        "positive_rate": float(np.nanmean(x[np.isfinite(x)] > 0)) if np.isfinite(x).any() else np.nan,
        "avg_turnover": float(np.nanmean(turnover[mask])) if np.isfinite(turnover[mask]).any() else np.nan,
        "avg_cost": float(np.nanmean(cost[mask])) if np.isfinite(cost[mask]).any() else np.nan,
        "capacity_proxy_median_quote_volume": float(np.nanmedian(cap)) if np.isfinite(cap).any() else np.nan,
        "capacity_proxy_p10_quote_volume": float(np.nanpercentile(cap[np.isfinite(cap)], 10)) if np.isfinite(cap).any() else np.nan,
        "traded_liquidity_proxy_median": float(np.nanmedian(traded)) if np.isfinite(traded).any() else np.nan,
    }


def evaluate(repo: Path, queue_path: Path, runtime: Path, report: Path, hours_per_split: int, train_hours_per_split: int) -> dict[str, Any]:
    runtime.mkdir(parents=True, exist_ok=True)
    report.parent.mkdir(parents=True, exist_ok=True)
    raw_queue = read_csv(queue_path)
    if raw_queue.empty:
        raise SystemExit(f"empty queue: {queue_path}")

    queue = raw_queue.drop_duplicates(["blueprint_id", "expression", "horizon_h"]).copy()
    timestamps, split, numeric, groups = load_numeric_for_queue(queue, hours_per_split, train_hours_per_split)
    evaluator = A7AB4Evaluator(numeric, groups)
    quote_volume = numeric["trade_quote_volume"]

    field_rows: list[dict[str, Any]] = []
    requested_fields = sorted(set().union(*(expression_fields(expr) for expr in queue["expression"].astype(str))))
    for field in requested_fields:
        values = numeric.get(field)
        if values is None:
            field_rows.append({"field": field, "status": "MISSING", "overall_finite_ratio": np.nan, "recent_finite_ratio": np.nan, "stress_finite_ratio": np.nan})
            continue
        recent = split == "recent_oos_2026JanApr"
        stress = split == "known_may2026_stress"
        field_rows.append(
            {
                "field": field,
                "status": "OK",
                "overall_finite_ratio": float(np.isfinite(values).mean()),
                "recent_finite_ratio": float(np.isfinite(values[:, recent]).mean()) if np.any(recent) else np.nan,
                "stress_finite_ratio": float(np.isfinite(values[:, stress]).mean()) if np.any(stress) else np.nan,
            }
        )
    pd.DataFrame(field_rows).to_csv(runtime / "a7shadow4_live_field_health.csv", index=False)

    signals: dict[str, np.ndarray] = {}
    weights: dict[str, np.ndarray] = {}
    net_returns: dict[str, np.ndarray] = {}
    metric_rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for row in queue.to_dict("records"):
        key = f"{row['blueprint_id']}|h{int(row['horizon_h'])}"
        try:
            signal = evaluator.eval(str(row["expression"]))
            horizon = int(row["horizon_h"])
            label = horizon_label(numeric["trade_close"], timestamps, split, horizon)
            orientation = choose_orientation(signal, label, split, quote_volume, 5.0)
            oriented_signal = signal * orientation
            signals[key] = rank_pct(oriented_signal)
            w = signal_to_weights(oriented_signal)
            weights[key] = w
            gross = np.nansum(w * label, axis=0)
            net_returns[key] = gross - one_way_turnover(w) * 5.0 / 10000.0
            for cost in [5.0, 10.0, 20.0, 30.0]:
                for split_name in ALL_EVAL_SPLITS:
                    metric_rows.append(metric_row(row, signal, label, split, quote_volume, cost, orientation, split_name))
        except Exception as exc:
            errors.append({"blueprint_id": row.get("blueprint_id", ""), "horizon_h": row.get("horizon_h", ""), "expression": row.get("expression", ""), "error": repr(exc)})
        finally:
            evaluator.cache.clear()

    pd.DataFrame(metric_rows).to_csv(runtime / "a7shadow4_cost_capacity_ladder.csv", index=False)
    pd.DataFrame(errors).to_csv(runtime / "a7shadow4_eval_errors.csv", index=False)

    signal_corr_rows: list[dict[str, Any]] = []
    return_corr_rows: list[dict[str, Any]] = []
    keys = list(signals)
    for i, left in enumerate(keys):
        for right in keys[i + 1 :]:
            signal_corr_rows.append({"left": left, "right": right, "signal_corr": finite_corr(signals[left], signals[right])})
            for split_name in ALL_EVAL_SPLITS:
                mask = split == split_name
                return_corr_rows.append(
                    {
                        "left": left,
                        "right": right,
                        "split": split_name,
                        "net_return_corr": finite_corr(net_returns[left][mask], net_returns[right][mask]),
                    }
                )
    signal_corr = pd.DataFrame(signal_corr_rows)
    return_corr = pd.DataFrame(return_corr_rows)
    signal_corr.to_csv(runtime / "a7shadow4_signal_correlation.csv", index=False)
    return_corr.to_csv(runtime / "a7shadow4_net_return_correlation.csv", index=False)

    cost_frame = pd.DataFrame(metric_rows)
    recent_ladder = cost_frame[cost_frame["split"].eq("recent_oos_2026JanApr")].copy()
    stress_ladder = cost_frame[cost_frame["split"].eq("known_may2026_stress")].copy()
    accepted_20bps = recent_ladder[(recent_ladder["cost_bps"].eq(20.0)) & (recent_ladder["sortino"] > 0)]["blueprint_id"].nunique()
    accepted_30bps = recent_ladder[(recent_ladder["cost_bps"].eq(30.0)) & (recent_ladder["sortino"] > 0)]["blueprint_id"].nunique()

    family_counts = Counter()
    for expr in queue["expression"].astype(str):
        for field in expression_fields(expr):
            if "open_interest" in field:
                family_counts["open_interest"] += 1
            elif "premium" in field or "basis" in field:
                family_counts["premium_basis"] += 1
            elif "funding" in field:
                family_counts["funding"] += 1
            else:
                family_counts["other"] += 1

    max_signal_corr = float(signal_corr["signal_corr"].abs().max()) if not signal_corr.empty else np.nan
    mean_signal_corr = float(signal_corr["signal_corr"].abs().mean()) if not signal_corr.empty else np.nan
    max_recent_return_corr = float(return_corr[return_corr["split"].eq("recent_oos_2026JanApr")]["net_return_corr"].abs().max()) if not return_corr.empty else np.nan
    field_health = pd.DataFrame(field_rows)
    field_health_min_recent = float(field_health["recent_finite_ratio"].min()) if field_rows else np.nan
    field_health_min_stress = float(field_health["stress_finite_ratio"].min()) if field_rows else np.nan
    blockers: list[str] = []
    warnings: list[str] = []
    if errors:
        blockers.append("eval_errors_present")
    if np.isfinite(field_health_min_recent) and field_health_min_recent < 0.95:
        blockers.append("recent_field_coverage_below_95pct")
    if np.isfinite(field_health_min_stress) and field_health_min_stress < 0.95:
        blockers.append("stress_field_coverage_below_95pct")
    if np.isfinite(max_signal_corr) and max_signal_corr > 0.85:
        warnings.append("max_signal_corr_gt_0_85")
    if np.isfinite(max_recent_return_corr) and max_recent_return_corr > 0.85:
        warnings.append("max_recent_net_return_corr_gt_0_85")
    if family_counts.get("open_interest", 0) >= 3:
        warnings.append("open_interest_family_concentrated")
    if accepted_20bps < 2:
        warnings.append("few_blueprints_survive_recent_20bps_positive_sortino")

    if blockers:
        decision = "HOLD_A7SHADOW4_BLOCKING_HEALTH_OR_EVAL_ISSUE"
    else:
        decision = "PASS_A7SHADOW4_ENGINEERING_REVIEW_PACKET_BUILT"

    if blockers:
        next_required = [
            "repair May-stress coverage for funding_rate_delta_state_24h or exclude funding-delta candidates from stress claims",
            "rerun A7SHADOW-4 after stress field coverage repair",
            "family diversification repair before further large search",
            "explicit orderbook/spread slippage model before any shadow book",
        ]
    else:
        next_required = [
            "forward-locked live adapter probe on accepted blueprints",
            "family diversification repair before further large search",
            "explicit orderbook/spread slippage model before any shadow book",
        ]
    if blockers:
        interpretation = (
            "The surviving candidates remain an engineering-review packet, not a deployable book. "
            "This stage is on HOLD because at least one hard health/evaluation blocker remains. "
            "Recent-window metrics may still be useful for diagnosis, but blocked rows must not be "
            "treated as stress-clean or deployment-ready."
        )
    else:
        interpretation = (
            "The surviving candidates form an engineering-review packet with field coverage and "
            "evaluation health passing this stage. This still does not authorize alpha proof, shadow, "
            "paper, or live trading. The main residual risks are signal/return overlap, family "
            "concentration, and missing explicit orderbook/spread slippage modelling."
        )

    manifest = {
        "stage": "A7SHADOW-4",
        "generated_at": now_utc(),
        "decision": decision,
        "input_rows": int(raw_queue.shape[0]),
        "unique_candidate_horizon_rows": int(queue.shape[0]),
        "eval_error_rows": len(errors),
        "field_count": len(field_rows),
        "field_health_min_recent": field_health_min_recent,
        "field_health_min_stress": field_health_min_stress,
        "max_abs_signal_corr": max_signal_corr,
        "mean_abs_signal_corr": mean_signal_corr,
        "max_abs_recent_net_return_corr": max_recent_return_corr,
        "recent_20bps_positive_sortino_blueprints": int(accepted_20bps),
        "recent_30bps_positive_sortino_blueprints": int(accepted_30bps),
        "family_counts": dict(family_counts),
        "blockers": blockers,
        "warnings": warnings,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "authorizes_shadow_book": False,
        "authorizes_live_adapter_probe": decision.startswith("PASS"),
        "next_required": next_required,
    }
    write_json(runtime / "a7shadow4_manifest.json", manifest)

    lines = [
        "# CRYPTO A7SHADOW4 Live Capacity Correlation Review",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7SHADOW-4 rematerializes the A7SHADOW-3 accepted rows and audits live-field availability, signal overlap, net-return overlap, cost ladder, and capacity proxies. It does not authorize alpha proof, shadow, paper, or live trading.",
        "",
        "## Counts",
        "",
        f"- input_rows: `{manifest['input_rows']}`",
        f"- unique_candidate_horizon_rows: `{manifest['unique_candidate_horizon_rows']}`",
        f"- eval_error_rows: `{manifest['eval_error_rows']}`",
        f"- field_health_min_recent: `{manifest['field_health_min_recent']}`",
        f"- field_health_min_stress: `{manifest['field_health_min_stress']}`",
        f"- max_abs_signal_corr: `{manifest['max_abs_signal_corr']}`",
        f"- mean_abs_signal_corr: `{manifest['mean_abs_signal_corr']}`",
        f"- max_abs_recent_net_return_corr: `{manifest['max_abs_recent_net_return_corr']}`",
        f"- recent_20bps_positive_sortino_blueprints: `{manifest['recent_20bps_positive_sortino_blueprints']}`",
        f"- recent_30bps_positive_sortino_blueprints: `{manifest['recent_30bps_positive_sortino_blueprints']}`",
        "",
        "## Field Health",
        "",
        md_table(pd.DataFrame(field_rows), 40),
        "",
        "## Signal Correlation",
        "",
        md_table(signal_corr, 40),
        "",
        "## Recent Cost Ladder",
        "",
        md_table(recent_ladder[recent_ladder["cost_bps"].isin([5.0, 20.0, 30.0])], 80),
        "",
        "## Stress Cost Ladder",
        "",
        md_table(stress_ladder[stress_ladder["cost_bps"].isin([5.0, 20.0, 30.0])], 80),
        "",
        "## Interpretation",
        "",
        interpretation,
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
    ]
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=str(REPO))
    parser.add_argument("--queue", default=DEFAULT_QUEUE)
    parser.add_argument("--runtime", default=DEFAULT_RUNTIME)
    parser.add_argument("--report", default=DEFAULT_REPORT)
    parser.add_argument("--hours-per-split", type=int, default=720)
    parser.add_argument("--train-hours-per-split", type=int, default=0)
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    evaluate(repo, repo / args.queue, repo / args.runtime, repo / args.report, args.hours_per_split, args.train_hours_per_split)


if __name__ == "__main__":
    main()
