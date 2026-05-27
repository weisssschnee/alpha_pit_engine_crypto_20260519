from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "runtime"
REPORT_DIR = ROOT / "reports"
DATE_TAG = "20260521"

A7P3_PATH = RUNTIME_DIR / "a7p3_protected_w2_pilot_decision" / "a7p3_decision_record.json"
A7P4_PATH = RUNTIME_DIR / "a7p4_productivity_forensic" / "a7p4_decision_record.json"
A7P5_PATH = RUNTIME_DIR / "a7p5_non_may_rank_repair_audit" / "a7p5_decision_record.json"

A7P_FINAL_DIR = RUNTIME_DIR / "a7p_final_failure_decision"
A7Q1_DIR = RUNTIME_DIR / "a7q1_failure_hypothesis_matrix"
A7Q2_DIR = RUNTIME_DIR / "a7q2_route_selection"
A7Q3_DIR = RUNTIME_DIR / "a7q3_next_stage_definition"


def utc_stamp() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]] | pd.DataFrame) -> pd.DataFrame:
    path.parent.mkdir(parents=True, exist_ok=True)
    df = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
    df.to_csv(path, index=False)
    return df


def table(df: pd.DataFrame, max_rows: int = 40) -> str:
    if df.empty:
        return "`<empty>`"
    return df.head(max_rows).to_markdown(index=False)


def write_report(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def a7p_failure_freeze(now: str, a7p3: dict[str, Any], a7p4: dict[str, Any], a7p5: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    m3 = a7p3["metrics"]
    m4 = a7p4["metrics"]
    m5 = a7p5["metrics"]
    evidence_rows = [
        {
            "evidence_item": "runner_stability",
            "status": "validated",
            "value": f"eval_failure_count={m3['eval_failure_count']}",
            "interpretation": "Protected W2 pilot executed without evaluator failures.",
        },
        {
            "evidence_item": "fold_replay_stability",
            "status": "validated",
            "value": f"fold_metric_missing_rate={m3['fold_metric_missing_rate']}",
            "interpretation": "Fold replay metrics were present for the pilot shard.",
        },
        {
            "evidence_item": "negative_controls",
            "status": "validated",
            "value": f"strict={m3['strict_negative_control_research_like']}, dominance={m3['negative_control_dominance_failures']}, placebo={m3['placebo_or_null_research_candidates']}",
            "interpretation": "Negative controls did not penetrate after the A7P runner gate repair.",
        },
        {
            "evidence_item": "diversity_caps",
            "status": "validated",
            "value": f"liqvol={m3['liquidity_volatility_deep_share']}, cluster={m3['single_return_corr_cluster_share']}",
            "interpretation": "A7M/A7N-style single-cluster and liquidity-volatility collapse did not recur in the protected pilot.",
        },
        {
            "evidence_item": "productivity",
            "status": "failed",
            "value": f"post_may_eligible={m4['post_may_eligible_deep_survivors']}/{m4['deep_audit_selected']}={m4['post_may_eligible_rate']:.6f}",
            "interpretation": "Post-May eligible productivity is below the 15% continuation target.",
        },
        {
            "evidence_item": "rank_alignment",
            "status": "failed",
            "value": f"top_decile={m4['top_decile_post_may_eligible_rate']}, bottom_decile={m4['bottom_decile_post_may_eligible_rate']}",
            "interpretation": "The current non-May rank score is directionally inverted against post-selection stress survival.",
        },
        {
            "evidence_item": "stress_analog_repair",
            "status": "failed",
            "value": f"stress_analog_top_decile={m5['stress_analog_top_decile_post_may_eligible_rate']}, overall={m5['overall_post_may_eligible_rate']}",
            "interpretation": "A simple non-May difficult-fold stress analog did not repair the rank inversion.",
        },
    ]
    evidence_df = write_csv(A7P_FINAL_DIR / "a7p_failure_evidence_summary.csv", evidence_rows)

    blocker_rows = [
        {
            "blocker": "post_may_eligible_productivity_low",
            "source": "A7P-3/A7P-4",
            "severity": "blocking",
            "blocks": "W2 continuation, full L1, alpha proof",
            "does_not_block": "failure analysis, route decision, data/horizon contracts",
        },
        {
            "blocker": "non_may_rank_inverted_vs_post_may_stress",
            "source": "A7P-4",
            "severity": "blocking",
            "blocks": "current high-score objective reuse",
            "does_not_block": "objective reset analysis",
        },
        {
            "blocker": "stress_analog_top_decile_weak",
            "source": "A7P-5",
            "severity": "blocking",
            "blocks": "simple worst-fold-rank repair",
            "does_not_block": "new horizon/data contract",
        },
    ]
    blocker_df = write_csv(A7P_FINAL_DIR / "a7p_blocker_matrix.csv", blocker_rows)

    authorization = {
        "generated_at": now,
        "decision": "HOLD_CRYPTO_A7P_PRODUCTIVITY_AND_OBJECTIVE_FAILURE",
        "validated": [
            "runner_stability",
            "fold_replay_stability",
            "May_stress_only_policy",
            "negative_control_blocker",
            "diversity_cap_behavior",
        ],
        "not_validated": [
            "current_non_may_ranking_objective",
            "W2_continuation",
            "full_L1",
            "alpha_proof",
        ],
        "authorizes_a7q": True,
        "authorizes_w2_continuation": False,
        "authorizes_full_l1": False,
        "authorizes_l2_or_l3": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "may_policy": a7p4.get("may_policy", {}),
        "source_decisions": {
            "A7P3": a7p3["decision"],
            "A7P4": a7p4["decision"],
            "A7P5": a7p5["decision"],
        },
    }
    write_json(A7P_FINAL_DIR / "a7p_final_decision_record.json", authorization)

    report = [
        "# Crypto A7P Final Failure Decision Record",
        "",
        f"- generated_at: `{now}`",
        "- decision: `HOLD_CRYPTO_A7P_PRODUCTIVITY_AND_OBJECTIVE_FAILURE`",
        "- executes_search: `False`",
        "- executes_replay: `False`",
        "- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`",
        "",
        "## Evidence Summary",
        "",
        table(evidence_df),
        "",
        "## Blocker Matrix",
        "",
        table(blocker_df),
        "",
        "## Interpretation",
        "",
        "A7P is an engineering and audit-system success, but a search-objective failure. The protected W2 pilot ran cleanly after the runner gate repair, yet the eligible pool stayed too small and the non-May rank selected May-vetoed structures.",
        "",
        "May remains stress-only and is not authorized for ranking, reward, generation, allocation, mutation, threshold tuning, or surrogate targets.",
    ]
    write_report(REPORT_DIR / f"CRYPTO_A7P_FINAL_FAILURE_DECISION_RECORD_{DATE_TAG}.md", report)
    return evidence_df, blocker_df, authorization


def a7q1_hypothesis_matrix(now: str, a7p4: dict[str, Any], a7p5: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    hypotheses = [
        {
            "hypothesis_id": "H1_objective_misalignment",
            "hypothesis": "Current non-May rank objective is directionally misaligned with post-selection stress survival.",
            "support": "A7P-4 top rank decile post-May eligible is 0% while bottom decile is 25%; A7P-5 stress-analog top decile is also 0%.",
            "contradiction": "Pipeline and negative controls are clean, so this is not explained by evaluator failure.",
            "evidence_strength": "strong",
            "next_cheapest_test": "A7R-0 constraint-first counterfactual on existing A7P-3 deep pool.",
            "overfit_risk": "high if May labels influence future selection; keep May stress-only.",
            "route_implication": "Do not reuse high-score objective as main route.",
        },
        {
            "hypothesis_id": "H2_feature_universe_insufficient",
            "hypothesis": "1h OHLCV/funding/basis lacks state variables needed to explain the stress failure.",
            "support": "Severe May failure remains broad after diversity and control gates; simple non-May fold proxy does not recover eligible ranking.",
            "contradiction": "Some post-May eligible rows exist, so the universe is not entirely empty.",
            "evidence_strength": "strong",
            "next_cheapest_test": "A7S-0 data contract for OI, liquidation, depth, cross-exchange basis/funding.",
            "overfit_risk": "medium; new fields require PIT contracts before alpha search.",
            "route_implication": "Prioritize data/horizon contract before more current-space search.",
        },
        {
            "hypothesis_id": "H3_horizon_mismatch",
            "hypothesis": "1h framing and short-to-medium horizons are too sensitive to cost, lag, and regime shocks.",
            "support": "A7P failures are stress-sensitive; longer horizons may reduce turnover and lag fragility.",
            "contradiction": "A7P-3 post-May eligible rows include some H48/H72 objects; horizon alone may not fix the objective.",
            "evidence_strength": "medium",
            "next_cheapest_test": "A7R horizon reframing diagnostic using existing candidates or <=64 cells.",
            "overfit_risk": "medium; horizon change must not be May-tuned.",
            "route_implication": "Allow small horizon diagnostic, not full search.",
        },
        {
            "hypothesis_id": "H4_market_state_unobserved",
            "hypothesis": "Missing OI/liquidation/orderbook/cross-exchange state causes stress regime blindness.",
            "support": "May failure is not explained by runner, caps, negative controls, or simple non-May stress folds.",
            "contradiction": "Data availability and PIT safety are not yet established.",
            "evidence_strength": "strong",
            "next_cheapest_test": "A7S field semantics and timestamp contract.",
            "overfit_risk": "medium-high if event fields are not PIT-clean.",
            "route_implication": "Primary route should be new-data contract.",
        },
        {
            "hypothesis_id": "H5_known_stress_overused",
            "hypothesis": "May has been used heavily for forensic work and cannot be used for proof selection.",
            "support": "A7F/A7G/A7H/A7I/A7O/A7P all examined May as stress.",
            "contradiction": "May still has value as a post-selection veto and failure label.",
            "evidence_strength": "strong",
            "next_cheapest_test": "Forward-locked observation on future unseen windows.",
            "overfit_risk": "high if May enters ranking or generator tuning.",
            "route_implication": "Run append-only forward observation in parallel.",
        },
        {
            "hypothesis_id": "H6_candidate_space_over_regularized",
            "hypothesis": "Gates may be too strict, reducing productivity despite a valid search space.",
            "support": "Post-May eligible rate is low after strict v3 gate.",
            "contradiction": "Negative controls and zero-exposure bugs were real; loosening gates would reintroduce False positives.",
            "evidence_strength": "weak",
            "next_cheapest_test": "Only diagnostic sensitivity, no promotion; do not relax May/cost/lag gates for proof.",
            "overfit_risk": "high",
            "route_implication": "Not a main route.",
        },
        {
            "hypothesis_id": "H7_crypto_formula_search_low_edge",
            "hypothesis": "Current data-layer formula search may have intrinsically low edge.",
            "support": "Multiple A7 branches found no alpha proof object.",
            "contradiction": "Broader data/horizon space has not been tested with PIT-safe additional fields.",
            "evidence_strength": "unresolved",
            "next_cheapest_test": "A7S data/horizon contract, then decide whether to pause.",
            "overfit_risk": "low for diagnosis; opportunity-cost risk high if ignored.",
            "route_implication": "Keep as a contingency, not final conclusion.",
        },
    ]
    hyp_df = write_csv(A7Q1_DIR / "a7q1_failure_hypothesis_matrix.csv", hypotheses)

    evidence_rows = [
        {
            "evidence": "A7P-3 pipeline clean",
            "value": "eval failures 0, fold missing 0, controls clean",
            "supports": "rules out engineering as primary blocker",
            "source": "A7P-3",
        },
        {
            "evidence": "A7P-4 productivity low",
            "value": f"eligible_rate={a7p4['metrics']['post_may_eligible_rate']:.6f}",
            "supports": "current W2 registry not productive enough",
            "source": "A7P-4",
        },
        {
            "evidence": "A7P-4 rank inversion",
            "value": f"top={a7p4['metrics']['top_decile_post_may_eligible_rate']}, bottom={a7p4['metrics']['bottom_decile_post_may_eligible_rate']}",
            "supports": "objective misalignment",
            "source": "A7P-4",
        },
        {
            "evidence": "A7P-5 stress analog weak",
            "value": f"stress_top={a7p5['metrics']['stress_analog_top_decile_post_may_eligible_rate']}",
            "supports": "simple non-May worst-fold repair insufficient",
            "source": "A7P-5",
        },
    ]
    ev_df = write_csv(A7Q1_DIR / "a7q1_evidence_by_hypothesis.csv", evidence_rows)

    decision = {
        "generated_at": now,
        "decision": "PASS_A7Q1_OBJECTIVE_CONTRADICTION_CONFIRMED",
        "executes_search": False,
        "executes_replay": False,
        "authorizes_new_search": False,
        "authorizes_alpha_proof": False,
        "primary_supported_hypotheses": [
            "H1_objective_misalignment",
            "H2_feature_universe_insufficient",
            "H4_market_state_unobserved",
            "H5_known_stress_overused",
        ],
        "secondary_hypotheses": ["H3_horizon_mismatch"],
        "weak_or_unresolved": ["H6_candidate_space_over_regularized", "H7_crypto_formula_search_low_edge"],
    }
    write_json(A7Q1_DIR / "a7q1_decision_record.json", decision)

    report = [
        "# Crypto A7Q-1 Failure Hypothesis Matrix",
        "",
        f"- generated_at: `{now}`",
        "- decision: `PASS_A7Q1_OBJECTIVE_CONTRADICTION_CONFIRMED`",
        "- executes_search: `False`",
        "- executes_replay: `False`",
        "- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`",
        "",
        "## Hypothesis Matrix",
        "",
        table(hyp_df),
        "",
        "## Evidence",
        "",
        table(ev_df),
        "",
        "## Interpretation",
        "",
        "The strongest explanation is objective misalignment combined with insufficient observed market-state variables. A simple non-May stress-fold analog did not repair the inversion, so continuing W2 or full L1 is not authorized.",
    ]
    write_report(REPORT_DIR / f"CRYPTO_A7Q1_FAILURE_HYPOTHESIS_MATRIX_{DATE_TAG}.md", report)
    return hyp_df, ev_df, decision


def a7q2_route_selection(now: str) -> tuple[pd.DataFrame, dict[str, Any]]:
    routes = [
        {
            "route_id": "A",
            "route": "current-data objective reset",
            "description": "Repair current 1h non-May objective on existing OHLCV/funding/basis data.",
            "expected_edge": "low",
            "cost": "low",
            "risk": "high",
            "priority": "low",
            "decision": "diagnostic_only",
            "rationale": "A7P-5 showed a simple non-May stress analog is weak; do not use as main route.",
        },
        {
            "route_id": "B",
            "route": "horizon reframing diagnostic",
            "description": "Test 4h/8h/24h or slower execution framing to reduce cost/lag/stress fragility.",
            "expected_edge": "medium_low",
            "cost": "low_mid",
            "risk": "medium",
            "priority": "medium",
            "decision": "authorize_small_diagnostic",
            "rationale": "Cheap test for horizon mismatch, but cannot solve missing state variables alone.",
        },
        {
            "route_id": "C",
            "route": "new data layer contract",
            "description": "Write PIT contracts for OI, liquidation, depth, cross-exchange basis/funding, and related state variables.",
            "expected_edge": "medium_high",
            "cost": "medium_high",
            "risk": "medium",
            "priority": "high",
            "decision": "primary_route",
            "rationale": "Most likely route to explain stress regimes not visible in current 1h feature set.",
        },
        {
            "route_id": "D",
            "route": "append-only forward wait",
            "description": "Freeze current runner/gates and observe future windows without tuning.",
            "expected_edge": "low_discovery_high_evidence",
            "cost": "low",
            "risk": "low",
            "priority": "high_parallel",
            "decision": "parallel_route",
            "rationale": "Needed to avoid further May-overfit and test whether stress behavior repeats.",
        },
        {
            "route_id": "E",
            "route": "pause crypto formula search",
            "description": "Freeze crypto formula search and redirect resources until new data or horizon contracts are ready.",
            "expected_edge": "conditional",
            "cost": "low",
            "risk": "low",
            "priority": "conditional",
            "decision": "fallback",
            "rationale": "Appropriate if data/horizon contracts are unavailable or fail PIT review.",
        },
    ]
    route_df = write_csv(A7Q2_DIR / "a7q2_route_scorecard.csv", routes)
    selected = {
        "generated_at": now,
        "decision": "PASS_A7Q_ROUTE_SELECTED_NEW_DATA_AND_FORWARD_WAIT",
        "primary_route": "C_new_data_layer_contract",
        "parallel_route": "D_append_only_forward_wait",
        "optional_diagnostic": "B_horizon_reframing_diagnostic",
        "route_a_status": "diagnostic_only_not_mainline",
        "route_e_status": "fallback_if_contracts_fail",
        "authorizes_a7r_small_horizon_diagnostic": True,
        "authorizes_a7s_data_horizon_contract": True,
        "authorizes_a7t_forward_locked_observation": True,
        "authorizes_w2_continuation": False,
        "authorizes_full_l1": False,
        "authorizes_l2_or_l3": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "may_policy": {
            "allowed": ["post_selection_stress_label", "post_selection_veto", "failure_attribution", "forward_observation_reporting"],
            "forbidden": ["score", "ranking", "threshold", "generation", "allocation", "mutation", "surrogate_target"],
        },
    }
    write_json(A7Q2_DIR / "a7q2_selected_route.json", selected)

    report = [
        "# Crypto A7Q-2 Route Selection Record",
        "",
        f"- generated_at: `{now}`",
        "- decision: `PASS_A7Q_ROUTE_SELECTED_NEW_DATA_AND_FORWARD_WAIT`",
        "- primary: `Route C - new data layer contract`",
        "- parallel: `Route D - append-only forward wait`",
        "- optional diagnostic: `Route B - horizon reframing`",
        "- full L1 / alpha proof / shadow / paper / live: `NOT_AUTHORIZED`",
        "",
        "## Route Scorecard",
        "",
        table(route_df),
        "",
        "## Decision",
        "",
        "Route C is selected as the primary next step because A7P indicates the current 1h OHLCV/funding/basis feature set does not expose enough market state to predict the known stress failure. Route D runs in parallel to create clean forward evidence. Route B is allowed only as a small diagnostic. Route A is not mainline.",
    ]
    write_report(REPORT_DIR / f"CRYPTO_A7Q2_ROUTE_SELECTION_RECORD_{DATE_TAG}.md", report)
    return route_df, selected


def a7q3_next_stage(now: str, selected: dict[str, Any]) -> tuple[pd.DataFrame, dict[str, Any]]:
    tasks = [
        {
            "stage": "A7R-0",
            "name": "horizon reframing contract",
            "type": "optional_diagnostic",
            "executes_search": False,
            "executes_replay": False,
            "objective": "Define 4h/8h/24h and slower execution framing test without May tuning.",
            "authorization": "allowed_small_contract_only",
        },
        {
            "stage": "A7R-1",
            "name": "horizon reframing small audit",
            "type": "optional_diagnostic",
            "executes_search": False,
            "executes_replay": "limited_existing_candidates_or_<=64_cells_only",
            "objective": "Check whether slower horizon improves cost/lag and post-May eligible productivity.",
            "authorization": "requires_A7R0_contract",
        },
        {
            "stage": "A7S-0",
            "name": "new data and horizon contract",
            "type": "primary",
            "executes_search": False,
            "executes_replay": False,
            "objective": "Create PIT contracts for OI, liquidation, depth, cross-exchange basis/funding, and longer horizons.",
            "authorization": "authorized",
        },
        {
            "stage": "A7T-0",
            "name": "forward-locked observation contract",
            "type": "parallel",
            "executes_search": False,
            "executes_replay": False,
            "objective": "Freeze runner/gates and define append-only future observation protocol.",
            "authorization": "authorized",
        },
    ]
    task_df = write_csv(A7Q3_DIR / "a7q3_next_task_registry.csv", tasks)
    auth = {
        "generated_at": now,
        "decision": "PASS_A7Q3_NEXT_STAGE_DEFINED",
        "selected_route_decision": selected["decision"],
        "authorized_next_tasks": ["A7S-0", "A7T-0", "A7R-0"],
        "not_authorized": ["W2_continuation", "full_L1", "L2", "L3", "alpha_proof", "shadow", "paper", "live"],
    }
    write_json(A7Q3_DIR / "a7q3_authorization_matrix.json", auth)

    report = [
        "# Crypto A7Q-3 Next Stage Definition",
        "",
        f"- generated_at: `{now}`",
        "- decision: `PASS_A7Q3_NEXT_STAGE_DEFINED`",
        "- authorized: `A7S-0`, `A7T-0`, `A7R-0`",
        "- not authorized: `W2`, `full L1`, `L2/L3`, `alpha proof`, `shadow/paper/live`",
        "",
        "## Task Registry",
        "",
        table(task_df),
        "",
        "## Boundary",
        "",
        "A7S-0 and A7T-0 are contracts, not alpha searches. A7R is optional and diagnostic. May remains stress-only and cannot enter ranking, reward, generation, allocation, mutation, threshold tuning, or surrogate targets.",
    ]
    write_report(REPORT_DIR / f"CRYPTO_A7Q3_NEXT_STAGE_DEFINITION_{DATE_TAG}.md", report)
    return task_df, auth


def main() -> int:
    now = utc_stamp()
    for path in [A7P_FINAL_DIR, A7Q1_DIR, A7Q2_DIR, A7Q3_DIR, REPORT_DIR]:
        path.mkdir(parents=True, exist_ok=True)

    a7p3 = load_json(A7P3_PATH)
    a7p4 = load_json(A7P4_PATH)
    a7p5 = load_json(A7P5_PATH)

    a7p_failure_freeze(now, a7p3, a7p4, a7p5)
    a7q1_hypothesis_matrix(now, a7p4, a7p5)
    _, selected = a7q2_route_selection(now)
    a7q3_next_stage(now, selected)

    manifest = {
        "generated_at": now,
        "decision": "PASS_A7Q_ROUTE_SELECTED_NEW_DATA_AND_FORWARD_WAIT",
        "executes_search": False,
        "executes_replay": False,
        "source_artifacts": {
            "a7p3": str(A7P3_PATH),
            "a7p4": str(A7P4_PATH),
            "a7p5": str(A7P5_PATH),
        },
        "outputs": {
            "a7p_final_report": f"reports/CRYPTO_A7P_FINAL_FAILURE_DECISION_RECORD_{DATE_TAG}.md",
            "a7q1_report": f"reports/CRYPTO_A7Q1_FAILURE_HYPOTHESIS_MATRIX_{DATE_TAG}.md",
            "a7q2_report": f"reports/CRYPTO_A7Q2_ROUTE_SELECTION_RECORD_{DATE_TAG}.md",
            "a7q3_report": f"reports/CRYPTO_A7Q3_NEXT_STAGE_DEFINITION_{DATE_TAG}.md",
        },
        "authorizes": {
            "A7S_0_data_horizon_contract": True,
            "A7T_0_forward_locked_observation_contract": True,
            "A7R_0_horizon_diagnostic_contract": True,
            "W2_continuation": False,
            "full_L1": False,
            "L2_or_L3": False,
            "alpha_proof": False,
            "shadow_paper_live": False,
        },
    }
    write_json(RUNTIME_DIR / "a7q_reset_decision_manifest.json", manifest)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

