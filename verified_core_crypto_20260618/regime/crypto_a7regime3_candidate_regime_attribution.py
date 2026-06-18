from __future__ import annotations

import argparse
import json
import math
import os
import sys
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
    load_numeric_for_queue,
    nonoverlap_metric,
    sharpe,
    signal_to_weights,
    sortino,
    split_for_timestamps,
    turnover_cost,
)


DATE = "20260612"
STAGE = "A7REGIME-3"
DEFAULT_QUEUE = REPO / "runtime" / "a7reward1_portfolio_reward_model_20260610" / "a7reward1_accepted_for_next_search.csv"
REGIME_RUNTIME = REPO / "runtime" / "a7regime2_mechanism_regime_audit_20260612"
STATE_PANEL = REGIME_RUNTIME / "a7regime2_hourly_mechanism_state_panel.csv"
STATE_PRIORITY = REGIME_RUNTIME / "a7regime2_regime_priority_recommendations.csv"
RUNTIME = REPO / "runtime" / "a7regime3_candidate_regime_attribution_20260612"
REPORT = REPO / "reports" / "CRYPTO_A7REGIME3_CANDIDATE_REGIME_ATTRIBUTION_20260612.md"

CORE_STATES = [
    "basis_dislocation_p95",
    "basis_dislocation_p90",
    "taker_flow_imbalance_p90",
    "perp_pressure_proxy",
    "funding_boundary_8h_proxy",
    "pre_funding_1h_proxy",
    "post_funding_1h_proxy",
    "oi_expansion_24h_p90",
    "oi_contraction_24h_p10",
    "liquidity_shock_low_volume",
    "volume_burst",
    "funding_negative_extreme",
    "market_crash_like",
    "extreme_vol_168h_p95",
    "extreme_drawdown_30d_p05",
    "is_weekend",
]


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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
    except Exception:
        return "```text\n" + view.to_string(index=False) + "\n```"


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path)


def annualization(horizon: int) -> float:
    return 24.0 * 365.0 / max(1, int(horizon))


def choose_orientation(signal: np.ndarray, label: np.ndarray, split: np.ndarray, quote_volume: np.ndarray, cost_bps: float) -> float:
    train = split == "train_2024"
    if not np.any(train):
        return 1.0
    scores = []
    for orient in [1.0, -1.0]:
        weights = signal_to_weights(signal * orient)
        gross = np.nansum(weights * label, axis=0)
        net = gross - turnover_cost(weights, cost_bps)
        scores.append(float(np.nanmean(net[train])) if np.isfinite(net[train]).any() else -np.inf)
    return 1.0 if scores[0] >= scores[1] else -1.0


def ret_metrics(ret: np.ndarray, horizon: int) -> dict[str, float]:
    finite = ret[np.isfinite(ret)]
    periods = annualization(horizon)
    if finite.size == 0:
        return {
            "n_obs": 0,
            "net_sum": np.nan,
            "net_mean": np.nan,
            "sortino": np.nan,
            "sharpe": np.nan,
            "nonoverlap_median_sortino": np.nan,
            "nonoverlap_floor_sortino": np.nan,
            "positive_rate": np.nan,
        }
    median_sortino, floor_sortino = nonoverlap_metric(ret, horizon, lambda x: sortino(x, periods))
    return {
        "n_obs": int(finite.size),
        "net_sum": float(np.nansum(finite)),
        "net_mean": float(np.nanmean(finite)),
        "sortino": sortino(ret, periods),
        "sharpe": sharpe(ret, periods),
        "nonoverlap_median_sortino": median_sortino,
        "nonoverlap_floor_sortino": floor_sortino,
        "positive_rate": float(np.nanmean(finite > 0)),
    }


def load_state_panel(timestamps: pd.DatetimeIndex) -> tuple[pd.DataFrame, list[str]]:
    states = pd.read_csv(STATE_PANEL)
    states["timestamp"] = pd.to_datetime(states["timestamp"], utc=True)
    states = states.drop_duplicates("timestamp").set_index("timestamp").sort_index()
    priority = read_csv(STATE_PRIORITY)
    priority_states = priority.loc[
        priority["recommended_action"].astype(str).str.contains("promote|high_interest|selector", regex=True, na=False),
        "state",
    ].astype(str).tolist() if not priority.empty else []
    state_names = []
    for state in [*CORE_STATES, *priority_states]:
        if state in states.columns and state not in state_names:
            state_names.append(state)
    aligned = states.reindex(timestamps)
    for state in state_names:
        aligned[state] = aligned[state].fillna(False).astype(bool)
    return aligned, state_names


def evaluate_regime_attribution(queue: pd.DataFrame, hours_per_split: int, train_hours_per_split: int, cost_bps: float) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    queue = queue.copy()
    queue["horizon_h"] = pd.to_numeric(queue["horizon_h"], errors="coerce").fillna(24).astype(int)
    # One row per blueprint+horizon; accepted queue can repeat formulas at different horizons.
    queue = queue.drop_duplicates(["blueprint_id", "horizon_h", "expression"]).reset_index(drop=True)
    timestamps, split, numeric, groups = load_numeric_for_queue(queue, hours_per_split, train_hours_per_split)
    state_panel, state_names = load_state_panel(timestamps)
    evaluator = A7AB4Evaluator(numeric, groups)
    quote_volume = numeric["trade_quote_volume"]
    labels = {h: horizon_label(numeric["trade_close"], timestamps, split, h) for h in sorted(queue["horizon_h"].unique())}

    state_rows: list[dict[str, Any]] = []
    loo_rows: list[dict[str, Any]] = []
    concentration_rows: list[dict[str, Any]] = []
    error_rows: list[dict[str, Any]] = []

    for idx, row in enumerate(queue.to_dict("records"), start=1):
        cid = str(row.get("blueprint_id", f"row_{idx}"))
        horizon = int(row["horizon_h"])
        print(f"[A7REGIME3] {idx}/{len(queue)} {cid} h={horizon}", flush=True)
        try:
            signal = evaluator.eval(str(row["expression"]))
            label = labels[horizon]
            orientation = choose_orientation(signal, label, split, quote_volume, cost_bps)
            weights = signal_to_weights(signal * orientation)
            gross = np.nansum(weights * label, axis=0)
            net = gross - turnover_cost(weights, cost_bps)
            base_fields = {
                "blueprint_id": cid,
                "semantic_pair": row.get("semantic_pair", ""),
                "motif": row.get("motif", ""),
                "skeleton_key": row.get("skeleton_key", ""),
                "expression": row.get("expression", ""),
                "horizon_h": horizon,
                "orientation": orientation,
            }
            for split_name in sorted(set(split.tolist())):
                split_mask = split == split_name
                if not np.any(split_mask):
                    continue
                total = ret_metrics(net[split_mask], horizon)
                split_abs_total = abs(total["net_sum"]) if np.isfinite(total["net_sum"]) else np.nan
                state_contribs = []
                for state in state_names:
                    state_mask = split_mask & state_panel[state].to_numpy(dtype=bool)
                    off_mask = split_mask & ~state_panel[state].to_numpy(dtype=bool)
                    on = ret_metrics(net[state_mask], horizon)
                    off = ret_metrics(net[off_mask], horizon)
                    contribution_share = abs(on["net_sum"]) / (split_abs_total + 1e-12) if np.isfinite(split_abs_total) else np.nan
                    lift = on["net_mean"] - off["net_mean"] if np.isfinite(on["net_mean"]) and np.isfinite(off["net_mean"]) else np.nan
                    row_out = {
                        **base_fields,
                        "split": split_name,
                        "state": state,
                        "state_hours": int(state_mask.sum()),
                        "off_hours": int(off_mask.sum()),
                        "state_net_mean": on["net_mean"],
                        "off_net_mean": off["net_mean"],
                        "state_sortino": on["sortino"],
                        "off_sortino": off["sortino"],
                        "state_nonoverlap_floor_sortino": on["nonoverlap_floor_sortino"],
                        "off_nonoverlap_floor_sortino": off["nonoverlap_floor_sortino"],
                        "state_positive_rate": on["positive_rate"],
                        "off_positive_rate": off["positive_rate"],
                        "state_vs_off_net_mean_lift": lift,
                        "state_abs_net_contribution_share": contribution_share,
                        "split_total_net_mean": total["net_mean"],
                        "split_total_sortino": total["sortino"],
                        "split_total_nonoverlap_floor_sortino": total["nonoverlap_floor_sortino"],
                    }
                    state_rows.append(row_out)
                    if np.isfinite(contribution_share):
                        state_contribs.append((state, contribution_share, row_out))
                    loo = ret_metrics(net[off_mask], horizon)
                    loo_rows.append(
                        {
                            **base_fields,
                            "split": split_name,
                            "left_out_state": state,
                            "remaining_hours": int(off_mask.sum()),
                            "remaining_net_mean": loo["net_mean"],
                            "remaining_sortino": loo["sortino"],
                            "remaining_nonoverlap_floor_sortino": loo["nonoverlap_floor_sortino"],
                            "passes_positive_remaining": bool(np.isfinite(loo["net_mean"]) and loo["net_mean"] > 0 and np.isfinite(loo["nonoverlap_floor_sortino"]) and loo["nonoverlap_floor_sortino"] > 0),
                        }
                    )
                if state_contribs:
                    top_state, top_share, top_row = max(state_contribs, key=lambda x: x[1])
                    concentration_rows.append(
                        {
                            **base_fields,
                            "split": split_name,
                            "top_contribution_state": top_state,
                            "top_abs_net_contribution_share": top_share,
                            "top_state_hours": top_row["state_hours"],
                            "split_total_net_mean": total["net_mean"],
                            "split_total_nonoverlap_floor_sortino": total["nonoverlap_floor_sortino"],
                            "concentration_decision": "HOLD_SINGLE_REGIME_CONCENTRATION"
                            if top_share >= 0.60 and top_row["state_hours"] >= max(24, horizon * 3)
                            else "PASS_NO_SINGLE_REGIME_DOMINANCE",
                        }
                    )
        except Exception as exc:
            error_rows.append({"blueprint_id": cid, "horizon_h": horizon, "error": repr(exc), "expression": row.get("expression", "")})
    return pd.DataFrame(state_rows), pd.DataFrame(loo_rows), pd.DataFrame(concentration_rows), pd.DataFrame(error_rows)


def summarize_decision(concentration: pd.DataFrame, loo: pd.DataFrame) -> tuple[str, pd.DataFrame]:
    rows: list[dict[str, Any]] = []
    if concentration.empty:
        return "HOLD_A7REGIME3_NO_ATTRIBUTION_ROWS", pd.DataFrame()
    key_splits = ["validation_2025H1", "test_2025H2", "recent_oos_2026JanApr", "known_may2026_stress"]
    for (cid, horizon), group in concentration.groupby(["blueprint_id", "horizon_h"], sort=False):
        key = group[group["split"].isin(key_splits)]
        holds = int(key["concentration_decision"].eq("HOLD_SINGLE_REGIME_CONCENTRATION").sum())
        max_share = float(pd.to_numeric(key["top_abs_net_contribution_share"], errors="coerce").max()) if not key.empty else np.nan
        top_states = "|".join(key.sort_values("top_abs_net_contribution_share", ascending=False)["top_contribution_state"].head(3).astype(str).tolist())
        loo_key = loo[(loo["blueprint_id"].eq(cid)) & (loo["horizon_h"].eq(horizon)) & (loo["split"].isin(key_splits))]
        loo_fail_count = int((~loo_key["passes_positive_remaining"].astype(bool)).sum()) if not loo_key.empty else 0
        decision = "PASS_REGIME_ROBUST_ATTRIBUTION"
        if holds >= 2 or (np.isfinite(max_share) and max_share >= 0.85):
            decision = "HOLD_REGIME_CONCENTRATED"
        elif loo_fail_count > max(3, len(loo_key) // 3):
            decision = "HOLD_LEAVE_STATE_OUT_FRAGILE"
        rows.append(
            {
                "blueprint_id": cid,
                "horizon_h": int(horizon),
                "concentrated_split_count": holds,
                "max_top_abs_net_contribution_share": max_share,
                "top_contribution_states": top_states,
                "leave_state_out_fail_count": loo_fail_count,
                "decision": decision,
            }
        )
    summary = pd.DataFrame(rows).sort_values(["decision", "max_top_abs_net_contribution_share"], ascending=[True, False])
    if summary["decision"].eq("PASS_REGIME_ROBUST_ATTRIBUTION").any():
        decision = "PASS_A7REGIME3_SOME_CANDIDATES_REGIME_ROBUST"
    else:
        decision = "HOLD_A7REGIME3_ACCEPTED_QUEUE_REGIME_CONCENTRATED"
    return decision, summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue", default=str(DEFAULT_QUEUE))
    parser.add_argument("--runtime", default=str(RUNTIME))
    parser.add_argument("--report", default=str(REPORT))
    parser.add_argument("--hours-per-split", type=int, default=int(os.environ.get("A7REGIME3_HOURS_PER_SPLIT", "0")))
    parser.add_argument("--train-hours-per-split", type=int, default=int(os.environ.get("A7REGIME3_TRAIN_HOURS_PER_SPLIT", "0")))
    parser.add_argument("--cost-bps", type=float, default=float(os.environ.get("A7REGIME3_COST_BPS", "5.0")))
    args = parser.parse_args()

    runtime = Path(args.runtime)
    report = Path(args.report)
    runtime.mkdir(parents=True, exist_ok=True)
    report.parent.mkdir(parents=True, exist_ok=True)

    queue = read_csv(Path(args.queue))
    if queue.empty:
        raise RuntimeError(f"empty queue: {args.queue}")
    state_metrics, loo, concentration, errors = evaluate_regime_attribution(queue, args.hours_per_split, args.train_hours_per_split, args.cost_bps)
    decision, summary = summarize_decision(concentration, loo)

    state_metrics.to_csv(runtime / "a7regime3_state_conditional_candidate_metrics.csv", index=False)
    loo.to_csv(runtime / "a7regime3_leave_state_out_metrics.csv", index=False)
    concentration.to_csv(runtime / "a7regime3_regime_concentration_summary.csv", index=False)
    summary.to_csv(runtime / "a7regime3_candidate_regime_decisions.csv", index=False)
    errors.to_csv(runtime / "a7regime3_eval_errors.csv", index=False)

    manifest = {
        "stage": STAGE,
        "generated_at": now_utc(),
        "decision": decision,
        "queue": str(Path(args.queue)),
        "queue_rows": int(queue.shape[0]),
        "state_metric_rows": int(state_metrics.shape[0]),
        "leave_state_out_rows": int(loo.shape[0]),
        "concentration_rows": int(concentration.shape[0]),
        "candidate_decision_rows": int(summary.shape[0]),
        "error_rows": int(errors.shape[0]),
        "hours_per_split": int(args.hours_per_split),
        "train_hours_per_split": int(args.train_hours_per_split),
        "cost_bps": float(args.cost_bps),
        "outputs": {
            "state_conditional_candidate_metrics": str((runtime / "a7regime3_state_conditional_candidate_metrics.csv").relative_to(REPO)),
            "leave_state_out_metrics": str((runtime / "a7regime3_leave_state_out_metrics.csv").relative_to(REPO)),
            "regime_concentration_summary": str((runtime / "a7regime3_regime_concentration_summary.csv").relative_to(REPO)),
            "candidate_regime_decisions": str((runtime / "a7regime3_candidate_regime_decisions.csv").relative_to(REPO)),
            "eval_errors": str((runtime / "a7regime3_eval_errors.csv").relative_to(REPO)),
            "report": str(report.relative_to(REPO)),
        },
    }
    write_json(runtime / "a7regime3_manifest.json", manifest)

    top_conc = concentration.sort_values("top_abs_net_contribution_share", ascending=False).head(30) if not concentration.empty else concentration
    report.write_text(
        "\n".join(
            [
                "# CRYPTO A7REGIME3 Candidate Regime Attribution 20260612",
                "",
                "## Decision",
                "",
                f"`{decision}`",
                "",
                "This is a regime attribution and robustness audit. It does not authorize alpha proof, shadow, paper, live execution, or formula search.",
                "",
                "## Scope",
                "",
                f"- queue: `{args.queue}`",
                f"- queue_rows: `{queue.shape[0]}`",
                f"- state_metric_rows: `{state_metrics.shape[0]}`",
                f"- leave_state_out_rows: `{loo.shape[0]}`",
                f"- error_rows: `{errors.shape[0]}`",
                f"- hours_per_split: `{args.hours_per_split}`",
                f"- train_hours_per_split: `{args.train_hours_per_split}`",
                "",
                "## Candidate Decisions",
                "",
                md_table(summary, 30),
                "",
                "## Highest Single-State Contribution Cases",
                "",
                md_table(top_conc[[
                    "blueprint_id",
                    "horizon_h",
                    "split",
                    "top_contribution_state",
                    "top_abs_net_contribution_share",
                    "top_state_hours",
                    "concentration_decision",
                ]] if not top_conc.empty else top_conc, 30),
                "",
                "## Interpretation",
                "",
                "A candidate is treated as regime-fragile if too much of its OOS/stress net contribution comes from a single mechanism state or if leave-state-out removes the positive edge. This protects the search loop from mistaking a basis/taker/funding event fingerprint for general alpha.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(decision)
    print(report)


if __name__ == "__main__":
    main()
