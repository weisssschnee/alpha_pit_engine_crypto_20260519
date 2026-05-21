from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from crypto_a7_validation_utils import (
    clean_float,
    forward_funding_cost,
    funding_event_rate,
    load_core4_context,
    load_core4_specs,
    next_open_return,
    orient_signal,
    position_matrix,
    return_components,
    split_mask,
    summarize_returns,
)
from crypto_a7b_funding_baseline_audit import scale_book
from crypto_a7c_fundingcore_narrow_audit import fundingcore_specs, stable_shift_signal
from crypto_a7h1_nonfunding_masked_loo_audit import raw_book_from_specs_masked
from crypto_a7m2_equal_budget_engine_bakeoff import residualize_arrays, scaled_arrays_from_components
from crypto_a7o_l1_pilot_shard import (
    A7OExpressionContext,
    apply_signal_mode,
    active_hour_count,
)
from crypto_a7o_search_space_and_fold_replay import build_fold_masks


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "runtime"
REPORT_DIR = ROOT / "reports"
DATE_TAG = "20260521"
SOURCE_CHECKPOINT = "A7P3_W2PILOT"
SOURCE_DIR = RUNTIME_DIR / f"a7o_l1_checkpoint_{SOURCE_CHECKPOINT}"
SOURCE_DEEP = SOURCE_DIR / f"a7o_l1_checkpoint_{SOURCE_CHECKPOINT}_deep_audit_scoreboard.csv"
OUT_R0 = RUNTIME_DIR / "a7r0_horizon_reframing_contract"
OUT_R1 = RUNTIME_DIR / "a7r1_horizon_reframing"
OUT_S0 = RUNTIME_DIR / "a7s0_data_horizon_contract"

HORIZONS = [4, 8, 12, 24, 48, 72, 96]
EXECUTION_LAGS = [0, 1, 2, 3]
COST_BPS = [10, 20, 30]
PRIMARY_COST = 10
SEVERE_COST = 20
STRESS_GATE_MIN_GROSS_EXPOSURE = 0.05
STRESS_GATE_MIN_ACTIVE_HOURS = 10


def utc_stamp() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def table(df: pd.DataFrame, max_rows: int = 40) -> str:
    if df.empty:
        return "`<empty>`"
    return df.head(max_rows).to_markdown(index=False)


def split_stats(index: pd.DatetimeIndex, values: np.ndarray, turnover: np.ndarray, gross: np.ndarray) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for split in ["validation_2025H1", "recent_oos_2025H2_2026Apr", "fresh_forward_2026May"]:
        mask = split_mask(index, split)
        stats = summarize_returns(values[mask])
        out[f"{split}__annualized_mean"] = stats["annualized_mean"]
        out[f"{split}__hit_rate"] = stats["hit_rate"]
        out[f"{split}__max_dd"] = stats["additive_max_dd"]
        out[f"{split}__turnover"] = clean_float(np.nanmean(turnover[mask]))
        out[f"{split}__gross_exposure"] = clean_float(np.nanmean(gross[mask]))
        out[f"{split}__active_hour_count"] = active_hour_count(gross[mask])
    return out


def fold_min(index: pd.DatetimeIndex, values: np.ndarray, turnover: np.ndarray, gross: np.ndarray, fold_masks: dict[str, np.ndarray]) -> dict[str, Any]:
    anns = []
    positives = []
    active = []
    gross_values = []
    for _, mask in fold_masks.items():
        stats = summarize_returns(values[mask])
        ann = clean_float(stats["annualized_mean"])
        if ann is not None:
            anns.append(float(ann))
            positives.append(float(ann > 0))
        active.append(active_hour_count(gross[mask]))
        gross_values.append(clean_float(np.nanmean(gross[mask])) or 0.0)
    return {
        "fold_min_ann": min(anns) if anns else None,
        "fold_positive_rate": float(np.mean(positives)) if positives else None,
        "fold_min_active_hours": int(min(active)) if active else 0,
        "fold_min_gross_exposure": float(min(gross_values)) if gross_values else 0.0,
    }


def make_contracts(now: str) -> None:
    OUT_R0.mkdir(parents=True, exist_ok=True)
    OUT_S0.mkdir(parents=True, exist_ok=True)

    horizon_contract = pd.DataFrame(
        [
            {"horizon_id": f"H{h}", "target_horizon_hours": h, "status": "authorized_for_A7R1_diagnostic", "notes": "No formula search; existing candidates only."}
            for h in HORIZONS
        ]
        + [
            {"horizon_id": "mixed_H12_H48", "target_horizon_hours": "contract_only", "status": "not_executed_in_A7R1", "notes": "Reserved for future contract; not used in this cheap audit."},
            {"horizon_id": "mixed_H24_H96", "target_horizon_hours": "contract_only", "status": "not_executed_in_A7R1", "notes": "Reserved for future contract; not used in this cheap audit."},
        ]
    )
    horizon_contract.to_csv(OUT_R0 / "a7r0_horizon_contract.csv", index=False)

    execution_contract = pd.DataFrame(
        [{"execution_lag_bars": lag, "status": "authorized_for_A7R1_diagnostic", "notes": "Lag is applied by shifting the signal forward by lag bars before position construction."} for lag in EXECUTION_LAGS]
    )
    execution_contract.to_csv(OUT_R0 / "a7r0_execution_lag_contract.csv", index=False)

    cost_contract = pd.DataFrame(
        [{"cost_bps": bps, "status": "authorized_for_A7R1_diagnostic", "notes": "Fee drag applied through scaled array evaluator."} for bps in COST_BPS]
    )
    cost_contract.to_csv(OUT_R0 / "a7r0_cost_contract.csv", index=False)

    may_policy = {
        "allowed": ["post_selection_stress_label", "post_selection_veto", "failure_attribution"],
        "forbidden": ["ranking", "threshold_tuning", "horizon_selection", "weight_selection", "reward", "generation", "mutation", "surrogate_target"],
    }
    write_json(
        OUT_R0 / "a7r0_authorization_matrix.json",
        {
            "generated_at": now,
            "decision": "PASS_A7R0_HORIZON_REFRAMING_CONTRACT",
            "executes_search": False,
            "executes_replay": False,
            "authorizes_a7r1_small_audit": True,
            "authorizes_new_search": False,
            "authorizes_alpha_proof": False,
            "authorizes_shadow_paper_live": False,
            "horizons": HORIZONS,
            "execution_lags": EXECUTION_LAGS,
            "cost_bps": COST_BPS,
            "may_policy": may_policy,
        },
    )

    data_sources = pd.DataFrame(
        [
            {"source": "open_interest", "priority": 1, "status": "contract_required", "pit_risk": "medium", "expected_value": "market_state_and_leverage"},
            {"source": "liquidation_events_or_volume", "priority": 2, "status": "contract_required", "pit_risk": "high", "expected_value": "forced_flow_state"},
            {"source": "orderbook_depth_spread_imbalance", "priority": 3, "status": "contract_required", "pit_risk": "high", "expected_value": "tradability_and_short_horizon_stress"},
            {"source": "cross_exchange_basis_premium", "priority": 4, "status": "contract_required", "pit_risk": "medium_high", "expected_value": "venue_relative_value_state"},
            {"source": "cross_exchange_funding", "priority": 5, "status": "contract_required", "pit_risk": "medium_high", "expected_value": "funding_dispersion_state"},
            {"source": "long_short_account_or_position_ratio", "priority": 6, "status": "contract_required", "pit_risk": "medium", "expected_value": "crowding_state"},
        ]
    )
    data_sources.to_csv(OUT_S0 / "a7s0_candidate_data_sources.csv", index=False)

    pit_contract = pd.DataFrame(
        [
            {"field": "observable_time", "required": True, "description": "Timestamp when the value is available for signal generation."},
            {"field": "event_time", "required": True, "description": "Exchange or vendor event timestamp."},
            {"field": "publication_delay", "required": True, "description": "Delay between event and observability."},
            {"field": "symbol_coverage", "required": True, "description": "Per-symbol availability and missingness."},
            {"field": "aggregation_lag", "required": True, "description": "Lag added before joining to 1h/4h/24h panels."},
            {"field": "survivorship_policy", "required": True, "description": "Handling of listing, delisting, and inactive markets."},
        ]
    )
    pit_contract.to_csv(OUT_S0 / "a7s0_pit_timestamp_contract.csv", index=False)

    write_json(
        OUT_S0 / "a7s0_authorization_matrix.json",
        {
            "generated_at": now,
            "decision": "PASS_A7S0_DATA_HORIZON_CONTRACT_SKELETON",
            "executes_search": False,
            "executes_replay": False,
            "authorizes_data_download": False,
            "authorizes_alpha_search": False,
            "authorizes_alpha_proof": False,
            "next_required": ["field_semantics_review", "source_cost_and_access_review", "PIT_timestamp_contract_completion"],
        },
    )

    write_report(
        REPORT_DIR / f"CRYPTO_A7R0_HORIZON_REFRAMING_CONTRACT_{DATE_TAG}.md",
        [
            "# Crypto A7R-0 Horizon Reframing Contract",
            "",
            f"- generated_at: `{now}`",
            "- decision: `PASS_A7R0_HORIZON_REFRAMING_CONTRACT`",
            "- executes_search: `False`",
            "- executes_replay: `False`",
            "- authorizes: `A7R-1 small audit only`",
            "- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`",
            "",
            "## Horizons",
            "",
            table(horizon_contract),
            "",
            "## Execution Lag Contract",
            "",
            table(execution_contract),
            "",
            "## Cost Contract",
            "",
            table(cost_contract),
            "",
            "## Boundary",
            "",
            "A7R-1 may only reuse existing A7P-3 deep candidates or a <=64-cell audit. May remains stress-only and cannot enter ranking, threshold tuning, horizon selection, reward, generation, mutation, or surrogate targets.",
        ],
    )
    write_report(
        REPORT_DIR / f"CRYPTO_A7S0_DATA_HORIZON_CONTRACT_SKELETON_{DATE_TAG}.md",
        [
            "# Crypto A7S-0 Data / Horizon Contract Skeleton",
            "",
            f"- generated_at: `{now}`",
            "- decision: `PASS_A7S0_DATA_HORIZON_CONTRACT_SKELETON`",
            "- executes_search: `False`",
            "- executes_replay: `False`",
            "- data download / alpha search / alpha proof: `NOT_AUTHORIZED`",
            "",
            "## Candidate Data Sources",
            "",
            table(data_sources),
            "",
            "## PIT Timestamp Contract Fields",
            "",
            table(pit_contract),
            "",
            "## Boundary",
            "",
            "This skeleton does not authorize data acquisition or alpha search. Each candidate source must pass field semantics, timestamp observability, publication delay, coverage, and cost review before use.",
        ],
    )


def write_report(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def evaluate_horizons(now: str) -> dict[str, Any]:
    OUT_R1.mkdir(parents=True, exist_ok=True)
    candidates = pd.read_csv(SOURCE_DEEP)
    candidates = candidates[~candidates["object_type"].astype(str).eq("placebo")].copy()
    candidates["base_candidate_id"] = candidates["candidate_id"]

    extra_fields = sorted({field for text in candidates["source_fields"].dropna().astype(str) for field in text.split(";") if field})
    for field in [
        "ret_6",
        "ret_12",
        "ret_24",
        "realized_vol_6",
        "realized_vol_12",
        "realized_vol_24",
        "quote_volume_mean_12",
        "quote_volume_mean_24",
        "mark_index_ratio",
        "premium_index",
        "latest_known_funding_rate",
        "funding_rate_persistence_3",
        "mark_minus_index",
    ]:
        if field not in extra_fields:
            extra_fields.append(field)
    index, _, matrices, _ = load_core4_context(extra_features=extra_fields)
    fold_def, fold_masks = build_fold_masks(index, matrices)
    ctx = A7OExpressionContext(matrices, fold_masks)

    funding_raw = raw_book_from_specs_masked(index=index, matrices=matrices, ctx=ctx, specs=fundingcore_specs())
    core4_raw = raw_book_from_specs_masked(index=index, matrices=matrices, ctx=ctx, specs=load_core4_specs())
    funding_net = scale_book(funding_raw, PRIMARY_COST)["net_return"].to_numpy(dtype=float)
    core4_net = scale_book(core4_raw, PRIMARY_COST)["net_return"].to_numpy(dtype=float)
    train_mask = split_mask(index, "train_2024")
    funding_cost_base = funding_event_rate(matrices)

    rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for i, (_, row) in enumerate(candidates.iterrows(), start=1):
        base_id = str(row["candidate_id"])
        try:
            base_signal = ctx.eval(str(row["expression"]))
            for target_horizon in HORIZONS:
                gross_target = next_open_return(matrices["open"], int(target_horizon))
                funding_cost = forward_funding_cost(funding_cost_base, int(target_horizon))
                target = gross_target - funding_cost
                orientation, train_ic = orient_signal(index, base_signal, target)
                signal = apply_signal_mode(base_id, str(row.get("signal_mode", "original")), base_signal, orientation)
                if str(row.get("signal_mode", "")) == "sign_flip":
                    orientation = -orientation
                horizon_row: dict[str, Any] = {
                    "candidate_id": f"{base_id}__A7R_H{target_horizon}",
                    "base_candidate_id": base_id,
                    "target_horizon_hours": int(target_horizon),
                    "cell_id": row["cell_id"],
                    "hypothesis_family": row["hypothesis_family"],
                    "feature_family_set": row["feature_family_set"],
                    "operator_motif": row["operator_motif"],
                    "original_temporal_horizon_class": row["temporal_horizon_class"],
                    "source_field_families": row["source_field_families"],
                    "expression": row["expression"],
                    "orientation": orientation,
                    "train_ic_mean": train_ic,
                }
                primary_pos = None
                primary_raw10 = None
                for lag in EXECUTION_LAGS:
                    lag_signal = stable_shift_signal(signal, lag) if lag else signal
                    pos = position_matrix(lag_signal, target, orientation)
                    comp = return_components(pos, gross_target, funding_cost, 0.0)
                    if lag == 0:
                        primary_pos = pos
                    for cost in COST_BPS:
                        arr = scaled_arrays_from_components(comp, cost)
                        prefix = f"lag{lag}_cost{cost}"
                        split = split_stats(index, arr["net_return"], arr["turnover"], arr["gross_exposure"])
                        for key, value in split.items():
                            horizon_row[f"{prefix}__{key}"] = value
                        if lag == 0 and cost == PRIMARY_COST:
                            primary_raw10 = arr
                            fold = fold_min(index, arr["net_return"], arr["turnover"], arr["gross_exposure"], fold_masks)
                            for key, value in fold.items():
                                horizon_row[f"{prefix}__{key}"] = value
                if primary_raw10 is None:
                    raise RuntimeError("primary raw10 missing")
                residual_funding, beta_funding, _ = residualize_arrays(primary_raw10["net_return"], funding_net, train_mask)
                residual_core4, beta_core4, _ = residualize_arrays(primary_raw10["net_return"], core4_net, train_mask)
                for name, values in [("residual_funding", residual_funding), ("residual_core4", residual_core4)]:
                    split = split_stats(index, values, primary_raw10["turnover"], primary_raw10["gross_exposure"])
                    for key, value in split.items():
                        horizon_row[f"{name}__{key}"] = value
                    fold = fold_min(index, values, primary_raw10["turnover"], primary_raw10["gross_exposure"], fold_masks)
                    for key, value in fold.items():
                        horizon_row[f"{name}__{key}"] = value
                horizon_row["beta_funding"] = beta_funding
                horizon_row["beta_core4"] = beta_core4
                rows.append(horizon_row)
        except Exception as exc:
            failures.append({"candidate_id": base_id, "error": type(exc).__name__, "message": str(exc)[:500]})
        finally:
            ctx.expr_cache.clear()
        if i % 25 == 0:
            print(f"A7R evaluated candidates {i}/{len(candidates)}", flush=True)

    metrics = pd.DataFrame(rows)
    metrics.to_csv(OUT_R1 / "a7r1_candidate_horizon_metrics.csv", index=False)
    pd.DataFrame(failures).to_csv(OUT_R1 / "a7r1_eval_failures.csv", index=False)
    fold_def.to_csv(OUT_R1 / "a7r1_fold_definition.csv", index=False)

    decision_rows = []
    for _, row in metrics.iterrows():
        reasons = []
        if row["lag0_cost10__validation_2025H1__annualized_mean"] <= 0:
            reasons.append("raw_validation_nonpositive")
        if row["lag0_cost10__recent_oos_2025H2_2026Apr__annualized_mean"] <= 0:
            reasons.append("raw_recent_nonpositive")
        if row["lag0_cost20__recent_oos_2025H2_2026Apr__annualized_mean"] <= 0:
            reasons.append("cost20_recent_nonpositive")
        if row["lag0_cost30__recent_oos_2025H2_2026Apr__annualized_mean"] <= 0:
            reasons.append("cost30_recent_nonpositive")
        for lag in [1, 2, 3]:
            if row[f"lag{lag}_cost10__recent_oos_2025H2_2026Apr__annualized_mean"] <= 0:
                reasons.append(f"lag{lag}_recent_nonpositive")
        if row["residual_funding__recent_oos_2025H2_2026Apr__annualized_mean"] <= 0:
            reasons.append("residual_funding_recent_nonpositive")
        if row["residual_core4__recent_oos_2025H2_2026Apr__annualized_mean"] <= 0:
            reasons.append("residual_core4_recent_nonpositive")

        may_reasons = []
        if row["lag0_cost10__fresh_forward_2026May__gross_exposure"] <= STRESS_GATE_MIN_GROSS_EXPOSURE:
            may_reasons.append("may_raw_gross_below_min")
        if row["residual_funding__fresh_forward_2026May__gross_exposure"] <= STRESS_GATE_MIN_GROSS_EXPOSURE:
            may_reasons.append("may_residual_gross_below_min")
        if row["lag0_cost10__fresh_forward_2026May__active_hour_count"] < STRESS_GATE_MIN_ACTIVE_HOURS:
            may_reasons.append("may_raw_active_below_min")
        if row["residual_funding__fresh_forward_2026May__active_hour_count"] < STRESS_GATE_MIN_ACTIVE_HOURS:
            may_reasons.append("may_residual_active_below_min")
        if row["lag0_cost10__fresh_forward_2026May__annualized_mean"] < -0.5:
            may_reasons.append("may_raw_severe_fail")
        if row["residual_funding__fresh_forward_2026May__annualized_mean"] < 0:
            may_reasons.append("may_residual_funding_negative")
        label = "A7R_HORIZON_RESEARCH_CANDIDATE_DIAGNOSTIC" if not reasons and not may_reasons else "A7R_HORIZON_HOLD"
        if not reasons and may_reasons:
            label = "A7R_HORIZON_MAY_VETOED"
        decision_rows.append(
            {
                "candidate_id": row["candidate_id"],
                "base_candidate_id": row["base_candidate_id"],
                "target_horizon_hours": row["target_horizon_hours"],
                "decision": label,
                "reject_reasons": ";".join(reasons + may_reasons),
                "pre_may_pass": not reasons,
                "post_may_eligible": not reasons and not may_reasons,
            }
        )
    decisions = pd.DataFrame(decision_rows)
    decisions.to_csv(OUT_R1 / "a7r1_horizon_decisions.csv", index=False)

    joined = metrics.merge(decisions[["candidate_id", "decision", "reject_reasons", "pre_may_pass", "post_may_eligible"]], on="candidate_id", how="left")
    summary = (
        joined.groupby("target_horizon_hours")
        .agg(
            rows=("candidate_id", "count"),
            post_may_eligible_count=("post_may_eligible", "sum"),
            pre_may_pass_count=("pre_may_pass", "sum"),
            median_raw_recent=("lag0_cost10__recent_oos_2025H2_2026Apr__annualized_mean", "median"),
            median_cost20_recent=("lag0_cost20__recent_oos_2025H2_2026Apr__annualized_mean", "median"),
            median_cost30_recent=("lag0_cost30__recent_oos_2025H2_2026Apr__annualized_mean", "median"),
            median_lag1_recent=("lag1_cost10__recent_oos_2025H2_2026Apr__annualized_mean", "median"),
            median_lag2_recent=("lag2_cost10__recent_oos_2025H2_2026Apr__annualized_mean", "median"),
            median_lag3_recent=("lag3_cost10__recent_oos_2025H2_2026Apr__annualized_mean", "median"),
            median_raw_may=("lag0_cost10__fresh_forward_2026May__annualized_mean", "median"),
            median_residual_may=("residual_funding__fresh_forward_2026May__annualized_mean", "median"),
            median_fold_min=("lag0_cost10__fold_min_ann", "median"),
        )
        .reset_index()
    )
    summary["post_may_eligible_rate"] = summary["post_may_eligible_count"] / summary["rows"]
    summary["pre_may_pass_rate"] = summary["pre_may_pass_count"] / summary["rows"]
    summary.to_csv(OUT_R1 / "a7r1_post_may_eligible_by_horizon.csv", index=False)

    rank_rows = []
    for horizon, part in joined.groupby("target_horizon_hours"):
        rank_score = (
            part["lag0_cost10__recent_oos_2025H2_2026Apr__annualized_mean"].clip(-2, 2)
            + part["residual_funding__recent_oos_2025H2_2026Apr__annualized_mean"].clip(-2, 2)
            + part["lag0_cost20__recent_oos_2025H2_2026Apr__annualized_mean"].clip(-2, 2)
            + part["lag1_cost10__recent_oos_2025H2_2026Apr__annualized_mean"].clip(-2, 2)
            - 0.25 * part["lag0_cost10__recent_oos_2025H2_2026Apr__turnover"].fillna(0.0)
        )
        tmp = part.assign(a7r_rank_score=rank_score)
        tmp["rank_order"] = tmp["a7r_rank_score"].rank(method="first", ascending=False)
        tmp["rank_decile"] = pd.qcut(tmp["rank_order"], 10, labels=False, duplicates="drop") + 1
        for decile, dec in tmp.groupby("rank_decile"):
            rank_rows.append(
                {
                    "target_horizon_hours": horizon,
                    "rank_decile": int(decile),
                    "rows": len(dec),
                    "post_may_eligible_count": int(dec["post_may_eligible"].sum()),
                    "post_may_eligible_rate": float(dec["post_may_eligible"].mean()),
                    "median_rank_score": float(dec["a7r_rank_score"].median()),
                    "median_raw_may": float(dec["lag0_cost10__fresh_forward_2026May__annualized_mean"].median()),
                    "median_raw_recent": float(dec["lag0_cost10__recent_oos_2025H2_2026Apr__annualized_mean"].median()),
                }
            )
    rank_deciles = pd.DataFrame(rank_rows)
    rank_deciles.to_csv(OUT_R1 / "a7r1_rank_decile_alignment_by_horizon.csv", index=False)

    best = summary.sort_values(["post_may_eligible_rate", "post_may_eligible_count"], ascending=[False, False]).head(1)
    best_rate = float(best["post_may_eligible_rate"].iloc[0]) if not best.empty else 0.0
    best_horizon = int(best["target_horizon_hours"].iloc[0]) if not best.empty else None
    top_decile = rank_deciles[rank_deciles["rank_decile"].eq(1)]
    top_decile_max = float(top_decile["post_may_eligible_rate"].max()) if not top_decile.empty else 0.0
    blockers = []
    if best_rate < 0.15:
        blockers.append("post_may_eligible_rate_below_15pct_all_horizons")
    if top_decile_max <= 0:
        blockers.append("top_decile_post_may_eligible_still_zero")
    if failures:
        blockers.append("eval_failures_present")
    decision = "PASS_A7R1_HORIZON_REFRAMING_DIAGNOSTIC_CANDIDATE" if not blockers else "HOLD_A7R1_HORIZON_ONLY_INSUFFICIENT"

    decision_payload = {
        "generated_at": now,
        "decision": decision,
        "executes_search": False,
        "executes_replay": True,
        "source_checkpoint": SOURCE_CHECKPOINT,
        "input_deep_candidates": int(len(candidates)),
        "evaluated_rows": int(len(metrics)),
        "horizons": HORIZONS,
        "execution_lags": EXECUTION_LAGS,
        "cost_bps": COST_BPS,
        "best_horizon_hours": best_horizon,
        "best_post_may_eligible_rate": best_rate,
        "top_decile_max_post_may_eligible_rate": top_decile_max,
        "authorizes_new_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "blockers": blockers,
        "may_policy": {
            "allowed": ["post_selection_stress_label", "post_selection_veto", "failure_attribution"],
            "forbidden": ["ranking", "threshold_tuning", "horizon_selection", "reward", "generation", "mutation", "surrogate_target"],
        },
    }
    write_json(OUT_R1 / "a7r1_decision_record.json", decision_payload)

    write_report(
        REPORT_DIR / f"CRYPTO_A7R1_HORIZON_REFRAMING_SMALL_AUDIT_{DATE_TAG}.md",
        [
            "# Crypto A7R-1 Horizon Reframing Small Audit",
            "",
            f"- generated_at: `{now}`",
            f"- decision: `{decision}`",
            "- executes_search: `False`",
            "- executes_replay: `True`",
            "- input: `A7P-3 192 deep candidates`",
            "- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`",
            f"- blockers: `{blockers}`",
            "",
            "## Horizon Summary",
            "",
            table(summary),
            "",
            "## Rank Decile Alignment By Horizon",
            "",
            table(rank_deciles, 80),
            "",
            "## Interpretation",
            "",
            "A7R-1 is a diagnostic replay only. A PASS would only indicate that slower target horizons deserve a controlled redesign. It would not authorize alpha proof or search promotion. May is used only as post-selection stress label and veto.",
        ],
    )
    return decision_payload


def main() -> int:
    now = utc_stamp()
    make_contracts(now)
    decision = evaluate_horizons(now)
    manifest = {
        "generated_at": now,
        "decision": decision["decision"],
        "executes_search": False,
        "executes_replay": True,
        "source_checkpoint": SOURCE_CHECKPOINT,
        "outputs": {
            "a7r0_report": f"reports/CRYPTO_A7R0_HORIZON_REFRAMING_CONTRACT_{DATE_TAG}.md",
            "a7r1_report": f"reports/CRYPTO_A7R1_HORIZON_REFRAMING_SMALL_AUDIT_{DATE_TAG}.md",
            "a7s0_report": f"reports/CRYPTO_A7S0_DATA_HORIZON_CONTRACT_SKELETON_{DATE_TAG}.md",
        },
        "authorizes": {
            "new_search": False,
            "alpha_proof": False,
            "shadow_paper_live": False,
        },
    }
    write_json(RUNTIME_DIR / "a7r_a7s_manifest.json", manifest)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
