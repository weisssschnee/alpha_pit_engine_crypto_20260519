from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "runtime" / "a7z_failure_registry_and_route"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7Z_FAILURE_REGISTRY_AND_NEXT_DATA_DECISION_20260522.md"


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    return df.head(max_rows).to_markdown(index=False)


def evidence_refs() -> dict[str, dict[str, Any]]:
    return {
        "A7V7": read_json(ROOT / "runtime" / "a7v7_failure_attribution" / "a7v7_authorization_matrix.json"),
        "A7X4": read_json(ROOT / "runtime" / "a7x4_failure_forensic" / "a7x4_authorization_matrix.json"),
        "A7S4": read_json(ROOT / "runtime" / "a7s4_crowding_robustness_audit" / "a7s4_authorization_matrix.json"),
        "A7Y2": read_json(ROOT / "runtime" / "a7y2_interaction_clue_forensic" / "a7y2_authorization_matrix.json"),
        "A7Q2": read_json(ROOT / "runtime" / "a7q2_route_selection" / "a7q2_selected_route.json"),
        "A7S0": read_json(ROOT / "runtime" / "a7s0_data_horizon_contract" / "a7s0_authorization_matrix.json"),
    }


def build_blocked_motif_registry(refs: dict[str, dict[str, Any]]) -> pd.DataFrame:
    rows = [
        {
            "motif_id": "activity_liquidity_self_reproduction",
            "source_stages": "A7V7,A7X4",
            "status": "BLOCKED_FOR_PROMOTION",
            "allowed_role": "failure_map_only",
            "blocked_role": "standalone_alpha_or_expanded_replay",
            "evidence": "A7V7: all pre-May clues fail May stress; A7X4: same-family expansion rejected.",
            "primary_blockers": "may_stress_fail; matched_control_contamination; family_concentration",
            "required_before_reuse": "new objective and matched-control dominance; do not expand old A7V positives",
        },
        {
            "motif_id": "aggtrades_standalone_activity_liquidity",
            "source_stages": "A7V7,A7X4",
            "status": "WEAK_PRIOR_ONLY",
            "allowed_role": "state_feature_or_interaction_feature",
            "blocked_role": "single-source standalone candidate family",
            "evidence": "aggTrades source trace is clean, but standalone activity/liquidity family did not survive controls and May stress.",
            "primary_blockers": "control_contamination; may_negative; symbol_state_mismatch",
            "required_before_reuse": "must be interacted with independent state and pass control dominance, cost, lag, symbol/month LOO",
        },
        {
            "motif_id": "metrics_standalone_global_long_short_crowding",
            "source_stages": "A7S3,A7S4",
            "status": "BLOCKED_FOR_PROMOTION",
            "allowed_role": "crowding_state_or_exposure_control",
            "blocked_role": "standalone_crowding_alpha",
            "evidence": "A7S4 rejected the global-long-short crowding motif after 20bps, symbol LOO, and month LOO failures.",
            "primary_blockers": "cost20_fail; symbol_loo_fail; month_loo_fail; single_formula_family",
            "required_before_reuse": "use as regime/exposure feature only; require residual and LOO proof before any candidate status",
        },
        {
            "motif_id": "core3_agg_metrics_interaction_small_clues",
            "source_stages": "A7Y1,A7Y2",
            "status": "BLOCKED_FOR_EXPANDED_REPLAY",
            "allowed_role": "interaction_clue_for_design",
            "blocked_role": "expanded_replay_or_research_candidate_pool",
            "evidence": "A7Y2 found zero robust interaction clues; symbol/month LOO weakness remained.",
            "primary_blockers": "no_robust_clues; symbol_loo_weak; month_loo_weak",
            "required_before_reuse": "new family contract; do not replay the same four A7Y1 clues as proof objects",
        },
        {
            "motif_id": "core12_oi_vol_interaction_single_clue",
            "source_stages": "A7Y1,A7Y2",
            "status": "WEAK_PRIOR_ONLY",
            "allowed_role": "state_interaction_hypothesis",
            "blocked_role": "standalone_core12_candidate",
            "evidence": "One core12 OI x volatility clue survived simple screens but failed robustness via symbol/month LOO.",
            "primary_blockers": "symbol_loo_weak; month_loo_weak",
            "required_before_reuse": "must pass symbol/month LOO and cost/lag under a fixed non-May objective",
        },
        {
            "motif_id": "current_1h_non_may_high_score_objective",
            "source_stages": "A7P,A7Q",
            "status": "BLOCKED_AS_PRIMARY_OBJECTIVE",
            "allowed_role": "diagnostic_baseline",
            "blocked_role": "primary_search_ranking_objective",
            "evidence": "A7P/A7Q froze rank inversion: top non-May decile had 0% post-May eligibility while bottom decile was higher.",
            "primary_blockers": "may_stress_rank_inversion; productivity_too_low",
            "required_before_reuse": "objective reset or new data/horizon contract; no W2/full L1 continuation",
        },
    ]
    for row in rows:
        decision = None
        for stage in str(row["source_stages"]).split(","):
            decision = refs.get(stage, {}).get("decision")
            if decision:
                break
        if decision:
            row["source_decision"] = decision
        else:
            row["source_decision"] = "see_referenced_stage_reports"
    return pd.DataFrame(rows)


def build_weak_prior_registry() -> pd.DataFrame:
    rows = [
        {
            "feature_or_family": "agg_flow_imbalance_notional_24h",
            "source": "aggTrades enhanced_v1",
            "independent_source": "aggTrades",
            "allowed_role": "flow_state_interactor",
            "blocked_role": "standalone_activity_alpha",
            "must_report": "matched controls; 20bps; lag1/lag2; symbol/month LOO; May stress-only label",
        },
        {
            "feature_or_family": "agg_signed_flow_z_24h",
            "source": "aggTrades enhanced_v1",
            "independent_source": "aggTrades",
            "allowed_role": "signed_flow_state_interactor",
            "blocked_role": "single-field replay expansion",
            "must_report": "control dominance; turnover/cost; post-selection May label",
        },
        {
            "feature_or_family": "agg_cross_symbol_signed_flow_share",
            "source": "aggTrades enhanced_v1",
            "independent_source": "aggTrades",
            "allowed_role": "cross_symbol_flow_state",
            "blocked_role": "core3-only proof object",
            "must_report": "symbol-tier attribution; BTC/ETH/SOL asymmetry; controls",
        },
        {
            "feature_or_family": "open_interest_change_24h",
            "source": "Binance Vision daily metrics",
            "independent_source": "metrics/openInterest",
            "allowed_role": "positioning_state_interactor",
            "blocked_role": "single OI alpha without LOO",
            "must_report": "vendor 5m warnings; residual vs FundingCore/Core4; cost/lag; LOO",
        },
        {
            "feature_or_family": "global_long_short_account_ratio_zscore_168h",
            "source": "Binance Vision daily metrics",
            "independent_source": "metrics/globalLongShortAccountRatio",
            "allowed_role": "crowding_state_or_exposure_control",
            "blocked_role": "standalone crowding alpha",
            "must_report": "A7S4 blocker check; matched controls; symbol/month LOO",
        },
        {
            "feature_or_family": "top_long_short_position_ratio_zscore_168h",
            "source": "Binance Vision daily metrics",
            "independent_source": "metrics/topLongShortPositionRatio",
            "allowed_role": "large_account_positioning_state",
            "blocked_role": "standalone positioning alpha before robustness",
            "must_report": "PIT vendor warnings; residual/cost/lag/LOO",
        },
        {
            "feature_or_family": "agg_features_available / metrics_features_available",
            "source": "unified panel masks",
            "independent_source": "availability metadata",
            "allowed_role": "sample_mask_and_coverage_control",
            "blocked_role": "predictive signal",
            "must_report": "coverage by symbol/month; no selection leakage",
        },
    ]
    return pd.DataFrame(rows)


def build_source_gap_matrix(a7s0_sources: pd.DataFrame) -> pd.DataFrame:
    base_rows: list[dict[str, Any]] = []
    if not a7s0_sources.empty:
        for _, row in a7s0_sources.iterrows():
            base_rows.append(
                {
                    "source_id": row.get("source_id"),
                    "status": row.get("current_status"),
                    "independent_information": source_independence(str(row.get("source_id", ""))),
                    "historical_proof_allowed": row.get("historical_proof_allowed"),
                    "forward_only": row.get("forward_only"),
                    "priority": priority_for_source(str(row.get("source_id", ""))),
                    "next_decision": next_decision_for_source(str(row.get("source_id", "")), str(row.get("current_status", ""))),
                    "required_contract": row.get("pit_requirements"),
                }
            )
    extra = [
        {
            "source_id": "liquidation_force_order_historical",
            "status": "CONTRACT_REQUIRED_SOURCE_NOT_VALIDATED",
            "independent_information": "yes: forced liquidation / deleveraging event flow not derivable from OHLCV or aggTrades",
            "historical_proof_allowed": False,
            "forward_only": False,
            "priority": "high",
            "next_decision": "A7AA-0 liquidation source availability + PIT/source contract",
            "required_contract": "event_time, side convention, price/qty/notional, publication lag, venue coverage, raw checksum/source trace",
        },
        {
            "source_id": "historical_orderbook_depth",
            "status": "CONTRACT_REQUIRED_OR_FORWARD_ONLY",
            "independent_information": "yes: displayed liquidity, spread, depth imbalance not recoverable from trades",
            "historical_proof_allowed": False,
            "forward_only": True,
            "priority": "high_if_historical_source_exists",
            "next_decision": "A7AA-0 depth source feasibility; otherwise A7T forward-only observation",
            "required_contract": "observable_time, exchange update_time, depth level, snapshot cadence, missingness, no backfill into historical proof",
        },
        {
            "source_id": "cross_exchange_basis_funding_premium",
            "status": "CONTRACT_REQUIRED_SOURCE_NOT_VALIDATED",
            "independent_information": "yes: venue dispersion and relative funding/basis state",
            "historical_proof_allowed": False,
            "forward_only": False,
            "priority": "high",
            "next_decision": "A7AA-0 venue/PIT/symbol mapping contract",
            "required_contract": "venue timestamp semantics, mark/index/funding availability, settlement timing, fees, symbol mapping",
        },
    ]
    existing = {str(row.get("source_id")) for row in base_rows}
    for row in extra:
        if row["source_id"] not in existing:
            base_rows.append(row)
    return pd.DataFrame(base_rows)


def source_independence(source_id: str) -> str:
    if "aggtrades" in source_id:
        return "yes: trade-level aggressor flow, but current standalone family is weak"
    if "metrics" in source_id or "positioning" in source_id:
        return "yes: positioning/open-interest state"
    if "orderbook" in source_id:
        return "yes: displayed depth/spread state"
    if "liquidation" in source_id:
        return "yes: forced-flow event state"
    if "cross_exchange" in source_id:
        return "yes: venue dispersion state"
    if "base_core12" in source_id:
        return "baseline market/funding/mark/index only"
    return "unknown_or_metadata"


def priority_for_source(source_id: str) -> str:
    if "liquidation" in source_id or "cross_exchange" in source_id:
        return "high"
    if "orderbook" in source_id:
        return "high_forward_or_if_historical_available"
    if "metrics" in source_id or "aggtrades" in source_id:
        return "completed_data_line"
    return "medium"


def next_decision_for_source(source_id: str, status: str) -> str:
    if "READY" in status:
        return "use only under weak-prior registry and controlled diagnostics"
    if "FORWARD_ONLY" in status:
        return "A7T forward observation only; no historical proof"
    if "MISSING" in status:
        return "data-line backfill allowed; experiment waits for source trace pass"
    if "CONTRACT_REQUIRED" in status or "NOT_PRESENT" in status:
        return "write PIT/source contract before any search"
    return "review_required"


def build_next_route_scorecard() -> pd.DataFrame:
    rows = [
        {
            "route_id": "A7AA-0",
            "route": "new independent source feasibility + PIT contract",
            "priority": "primary",
            "authorized": True,
            "scope": "liquidation, historical depth if available, cross-exchange basis/funding/premium",
            "why": "Existing public Binance historical fields are now usable state layers but current signal families remain HOLD.",
            "not_authorized": "search/replay/alpha proof before field contract passes",
        },
        {
            "route_id": "A7T-0",
            "route": "forward-locked observation",
            "priority": "parallel",
            "authorized": True,
            "scope": "orderbook forward snapshots, positioning forward collectors, current runner/gate telemetry",
            "why": "May is a known stress set; new evidence must come from append-only windows.",
            "not_authorized": "historical proof from forward-only fields",
        },
        {
            "route_id": "A7R/A7X diagnostic",
            "route": "small horizon/objective diagnostic on existing fields",
            "priority": "low_optional",
            "authorized": True,
            "scope": "<= small controlled diagnostic only; no broad replay",
            "why": "Can test horizon mismatch cheaply, but repeated standalone/interaction families failed robustness.",
            "not_authorized": "expanded replay of A7V/A7S/A7Y positives",
        },
        {
            "route_id": "same_family_expansion",
            "route": "expand A7V/A7S/A7Y positive clues",
            "priority": "blocked",
            "authorized": False,
            "scope": "activity/liquidity, standalone crowding, small interaction clues",
            "why": "Blocked by May stress, control contamination, cost/LOO, and robustness failures.",
            "not_authorized": "any promotion or larger replay",
        },
        {
            "route_id": "alpha_shadow_paper_live",
            "route": "alpha proof / shadow / paper / live",
            "priority": "blocked",
            "authorized": False,
            "scope": "all current crypto objects",
            "why": "No robust crypto alpha proof object exists.",
            "not_authorized": "all",
        },
    ]
    return pd.DataFrame(rows)


def build_authorization_matrix() -> dict[str, Any]:
    return {
        "decision": "PASS_A7Z_FAILURE_REGISTRY_COMPLETE_NEXT_DATA_CONTRACT_REQUIRED",
        "executes_search": False,
        "executes_replay": False,
        "authorizes_a7aa0_new_source_contract": True,
        "authorizes_a7t_forward_locked_observation_contract": True,
        "authorizes_small_existing_field_diagnostic": True,
        "authorizes_expanded_replay_of_a7v_a7s_a7y_clues": False,
        "authorizes_full_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "blockers_to_promotion": [
            "A7V/A7X activity-liquidity family failed May/control robustness",
            "A7S standalone crowding motif failed 20bps, symbol LOO, and month LOO",
            "A7Y interaction clues have zero robust clue count",
            "Current 1h high-score objective was previously frozen after May-stress rank inversion",
        ],
        "required_next": [
            "A7AA-0 liquidation/depth/cross-exchange source feasibility and PIT contract",
            "A7T-0 forward-locked observation contract for forward-only orderbook/positioning fields",
            "Do not treat change/zscore/interaction columns as independent sources",
        ],
        "generated_at": utc_stamp(),
    }


def write_report(
    refs: dict[str, dict[str, Any]],
    blocked: pd.DataFrame,
    weak: pd.DataFrame,
    gaps: pd.DataFrame,
    routes: pd.DataFrame,
    auth: dict[str, Any],
) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# CRYPTO A7Z Failure Registry And Next Data Decision",
        "",
        f"Generated: {auth['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{auth['decision']}`",
        "",
        "A7Z does not run search or replay. It freezes failed crypto signal motifs into a registry and routes the next work to independent data-source contracts and forward-locked observation.",
        "",
        "## Current State",
        "",
        "- Data line: PASS for aggTrades enhanced source trace and Binance metrics source trace, with documented vendor 5m warnings for metrics.",
        "- Signal line: HOLD. A7V/A7X activity-liquidity, A7S standalone crowding, and A7Y interaction clues are not promotable.",
        "- Promotion boundary: no alpha proof, no expanded replay, no full search, no shadow/paper/live.",
        "",
        "## Evidence Decisions",
        "",
        "| Stage | Decision | Key blockers |",
        "|---|---|---|",
    ]
    for stage, payload in refs.items():
        if not payload:
            continue
        blockers = payload.get("blockers", payload.get("warnings", []))
        if isinstance(blockers, list):
            blockers_text = "; ".join(str(x) for x in blockers)
        else:
            blockers_text = str(blockers)
        lines.append(f"| {stage} | `{payload.get('decision', '<no-decision>')}` | {blockers_text or '<none>'} |")
    lines.extend(
        [
            "",
            "## Blocked Motif Registry",
            "",
            table(blocked),
            "",
            "## Weak-Prior Feature Registry",
            "",
            table(weak),
            "",
            "## Source Gap Matrix",
            "",
            table(gaps, max_rows=120),
            "",
            "## Next Route Scorecard",
            "",
            table(routes),
            "",
            "## Authorization",
            "",
            table(pd.DataFrame([auth])),
            "",
            "## Required Next Action",
            "",
            "1. Run `A7AA-0` as a source feasibility and PIT contract for liquidation/force-order, historical orderbook depth if available, and cross-exchange basis/funding/premium.",
            "2. Keep `A7T-0` forward-locked observation for forward-only orderbook and positioning collectors.",
            "3. Do not expand A7V/A7S/A7Y positives. They are weak-prior or blocked motifs, not alpha proof objects.",
            "4. Treat derived `change`, `zscore`, and interaction columns as transforms, not independent data sources.",
            "",
            "## Bias Audit Boundary",
            "",
            "- Feature availability, timestamp semantics, and source trace remain required before any new field enters replay.",
            "- Existing May stress remains post-selection stress/failure attribution only. It must not enter ranking, reward, generator tuning, allocation, or mutation.",
            "- Any future result without cost, lag, residual-vs-FundingCore/Core4, controls, and symbol/month LOO is `HOLD_RESEARCH` at best.",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    refs = evidence_refs()
    a7s0_sources = read_csv(ROOT / "runtime" / "a7s0_data_horizon_contract" / "a7s0_candidate_data_sources.csv")
    blocked = build_blocked_motif_registry(refs)
    weak = build_weak_prior_registry()
    gaps = build_source_gap_matrix(a7s0_sources)
    routes = build_next_route_scorecard()
    auth = build_authorization_matrix()
    manifest = {
        "decision": auth["decision"],
        "generated_at": auth["generated_at"],
        "blocked_motif_count": int(len(blocked)),
        "weak_prior_count": int(len(weak)),
        "source_gap_count": int(len(gaps)),
        "next_route_count": int(len(routes)),
        "executes_search": False,
        "executes_replay": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "inputs": {
            "a7v7": "runtime/a7v7_failure_attribution/a7v7_authorization_matrix.json",
            "a7x4": "runtime/a7x4_failure_forensic/a7x4_authorization_matrix.json",
            "a7s4": "runtime/a7s4_crowding_robustness_audit/a7s4_authorization_matrix.json",
            "a7y2": "runtime/a7y2_interaction_clue_forensic/a7y2_authorization_matrix.json",
            "a7q2": "runtime/a7q2_route_selection/a7q2_selected_route.json",
            "a7s0_sources": "runtime/a7s0_data_horizon_contract/a7s0_candidate_data_sources.csv",
        },
    }
    blocked.to_csv(OUT_DIR / "a7z_blocked_motif_registry.csv", index=False)
    weak.to_csv(OUT_DIR / "a7z_weak_prior_feature_registry.csv", index=False)
    gaps.to_csv(OUT_DIR / "a7z_source_gap_matrix.csv", index=False)
    routes.to_csv(OUT_DIR / "a7z_next_route_scorecard.csv", index=False)
    write_json(OUT_DIR / "a7z_authorization_matrix.json", auth)
    write_json(OUT_DIR / "a7z_manifest.json", manifest)
    write_report(refs, blocked, weak, gaps, routes, auth)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
