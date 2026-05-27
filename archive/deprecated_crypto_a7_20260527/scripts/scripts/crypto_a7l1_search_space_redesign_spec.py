from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from crypto_a7_validation_utils import REPORT_DIR, RUNTIME_DIR, stable_hash


DATE_TAG = "20260520"
A7L0_DIR = RUNTIME_DIR / "a7l0_search_space_coverage_audit"
A7L1_DIR = RUNTIME_DIR / "a7l1_search_space_redesign_spec"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def source_snapshot() -> dict[str, Any]:
    manifest_path = A7L0_DIR / f"crypto_a7l0_manifest_{DATE_TAG}.json"
    summary_path = A7L0_DIR / "a7l0_search_space_coverage_summary.csv"
    manifest = read_json(manifest_path)
    summary = read_csv_dicts(summary_path)
    return {
        "a7l0_manifest_path": str(manifest_path),
        "a7l0_summary_path": str(summary_path),
        "a7l0_decision": manifest.get("decision", "UNKNOWN"),
        "a7l0_blockers": manifest.get("blockers", []),
        "a7l0_authorizes_budget_ladder_level1": manifest.get("authorizes_budget_ladder_level1", False),
        "coverage_summary": summary,
    }


def arm_contract_rows() -> list[dict[str, Any]]:
    return [
        {
            "arm": "L0_cost_aware_low_turnover",
            "purpose": "Generate structures whose first objective is 20bps and 1bar-lag survival, not raw recent return.",
            "primary_families": "price;volatility;liquidity",
            "required_horizons": "12;24;48",
            "ranking_terms": "raw_validation_recent;cost20_survival;lag1_survival;turnover_cost_penalty",
            "blocked_patterns": "high_turnover_near_close_edge;residual_only_hedge;zero_activity",
            "preflight_min_field_combo_count": 6,
            "preflight_min_preselection_rate": 0.10,
        },
        {
            "arm": "L1_residual_orthogonal_basis",
            "purpose": "Explore basis/premium expressions with mandatory residual value beyond FundingCore/Core4.",
            "primary_families": "basis;price;volatility;liquidity",
            "required_horizons": "12;24;48",
            "ranking_terms": "residual_vs_fundingcore;residual_vs_core4;raw_validation_recent;cost20_survival",
            "blocked_patterns": "spot_perp_basis_without_core6_lane;funding_beta_wrapper;basis_zero_activity",
            "preflight_min_field_combo_count": 8,
            "preflight_min_preselection_rate": 0.10,
        },
        {
            "arm": "L2_cross_symbol_relative",
            "purpose": "Test cross-symbol relative strength, dispersion, and crowding instead of single-field directional carry.",
            "primary_families": "cross_symbol;price;volatility;liquidity;basis",
            "required_horizons": "6;12;24;48",
            "ranking_terms": "cross_sectional_stability;residual_vs_fundingcore;symbol_loo_stability;cost20_survival",
            "blocked_patterns": "single_symbol_proxy;future_universe;current_constituent_survivorship",
            "preflight_min_field_combo_count": 8,
            "preflight_min_preselection_rate": 0.08,
        },
        {
            "arm": "L3_regime_conditional_no_may",
            "purpose": "Generate validation/recent-defined regime-conditioned candidates without using May for tuning.",
            "primary_families": "regime;volatility;liquidity;basis;price",
            "required_horizons": "12;24;48",
            "ranking_terms": "validation_regime_robustness;recent_regime_robustness;raw_validation_recent;residual_survival",
            "blocked_patterns": "may_tuned_gate;may_selected_threshold;too_low_active_ratio",
            "preflight_min_field_combo_count": 6,
            "preflight_min_preselection_rate": 0.08,
        },
        {
            "arm": "L4_microstructure_lite_lag_stable",
            "purpose": "Retest flow/volume/volatility interactions only when they survive 1bar lag and cost stress.",
            "primary_families": "flow;liquidity;volatility;price",
            "required_horizons": "6;12;24",
            "ranking_terms": "lag1_survival;cost20_survival;top_loss_dispersion;raw_validation_recent",
            "blocked_patterns": "taker_standalone;lag_fragile_flow;May_only_rescue",
            "preflight_min_field_combo_count": 8,
            "preflight_min_preselection_rate": 0.08,
        },
        {
            "arm": "L5_placebo_random_control",
            "purpose": "Negative control arm that must not produce comparable research candidates.",
            "primary_families": "placebo",
            "required_horizons": "12;24;48",
            "ranking_terms": "none",
            "blocked_patterns": "any_research_candidate_is_blocker",
            "preflight_min_field_combo_count": 4,
            "preflight_min_preselection_rate": 0.00,
        },
    ]


def budget_rows() -> list[dict[str, Any]]:
    return [
        {
            "level": "L0_observed",
            "generated_total": 1000,
            "status": "completed_hold",
            "advance_condition": "not_applicable",
            "hard_stop_if": "A7L0 blockers remain unresolved",
        },
        {
            "level": "L1_small_ladder",
            "generated_total": 4000,
            "status": "not_authorized_until_A7L1B",
            "advance_condition": "A7L1B implementation preflight passes and level stop rules pass",
            "hard_stop_if": "unique_expr_ratio<0.90 or preselection_rate<0.10 or placebo_research>0",
        },
        {
            "level": "L2_medium_ladder",
            "generated_total": 16000,
            "status": "not_authorized",
            "advance_condition": "L1 shows diverse near-miss pool and improving non-May attrition",
            "hard_stop_if": "cluster diversity stalls or selected May severe fail remains homogeneous",
        },
        {
            "level": "L3_large_ladder",
            "generated_total": 64000,
            "status": "not_authorized",
            "advance_condition": "L2 produces non-placebo research candidates or diverse near-miss families",
            "hard_stop_if": "L2 repeats A7K failure modes",
        },
    ]


def preflight_rows() -> list[dict[str, Any]]:
    return [
        {
            "check_id": "may_exclusion_mechanical",
            "required": True,
            "description": "May columns must be absent from rank score, reward, threshold, weight, selected_for_replay, and generator tuning.",
        },
        {
            "check_id": "coverage_activity",
            "required": True,
            "description": "Validation and recent windows must have sufficient observations and mean gross exposure before candidate selection.",
        },
        {
            "check_id": "cost_lag_static_screen",
            "required": True,
            "description": "20bps and 1bar-lag validation/recent screens must be measurable before budget ladder execution.",
        },
        {
            "check_id": "residual_baseline_screen",
            "required": True,
            "description": "Candidate scoring must report residual vs FundingCore/Core4 and beta penalties.",
        },
        {
            "check_id": "family_diversity_cap",
            "required": True,
            "description": "No family may exceed 25% of shortlist unless explicitly designated as placebo diagnostics.",
        },
        {
            "check_id": "evaluator_extension_gate",
            "required": True,
            "description": "Any new operator beyond Rank/ZScore/Mul/nested Mul requires separate evaluator timing and leakage preflight.",
        },
        {
            "check_id": "return_corr_cluster_dedup",
            "required": True,
            "description": "Selected candidates must be clustered/deduped before research-candidate claims.",
        },
        {
            "check_id": "positioning_recent_only_policy",
            "required": True,
            "description": "OI/long-short/taker positioning recent-only fields are prohibited from 2024-2026 historical proof until enough forward history exists.",
        },
    ]


def main() -> int:
    A7L1_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_now()
    source = source_snapshot()
    arms = arm_contract_rows()
    budget = budget_rows()
    preflight = preflight_rows()

    contract: dict[str, Any] = {
        "contract_id": "CRYPTO_A7L_SEARCH_SPACE_REDESIGN_SPEC_V1",
        "generated_at": now,
        "decision": "PASS_A7L1_SEARCH_SPACE_REDESIGN_SPEC",
        "alpha_proof_status": "NOT_ALPHA_PROOF",
        "executes_search": False,
        "executes_replay": False,
        "authorizes_a7l1b_implementation_preflight": True,
        "authorizes_budget_ladder_level1": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "source_context": source,
        "objective": (
            "Convert A7L-0's negative coverage result into a measurable broader search-space contract. "
            "The contract blocks same-generator blind budget expansion while preserving broader crypto formula search as an unfalsified route."
        ),
        "may_policy": {
            "status": "known_adversarial_stress_set",
            "allowed_uses": ["post_selection_stress_label", "final_veto_label", "failure_attribution"],
            "forbidden_uses": [
                "ranking",
                "reward_score",
                "threshold_tuning",
                "weight_selection",
                "candidate_selection",
                "generator_parameter_tuning",
                "generator_family_design",
                "budget_ladder_advance_decision_except_as_stress_summary",
            ],
        },
        "evaluator_scope": {
            "currently_safe_grammar": ["Rank", "ZScore", "Mul", "nested_Mul"],
            "extension_track_not_authorized_until_preflight": [
                "Add",
                "Sub",
                "Div",
                "SignedPower",
                "Clip",
                "TSMean",
                "TSStd",
                "TSRank",
                "Delta",
                "Decay",
                "Neutralize",
            ],
            "extension_required_checks": [
                "feature_time_before_execution",
                "rolling_window_past_only",
                "same_bar_execution_forbidden",
                "cost20_and_lag1_metrics_available",
                "residual_metrics_available",
            ],
        },
        "feature_policy": {
            "historical_allowed": [
                "price",
                "volatility",
                "liquidity",
                "flow_from_trade_bars",
                "basis",
                "funding_observable_only",
                "cross_symbol_relative",
                "validation_recent_regime_state",
            ],
            "diagnostic_or_future_only": [
                "positioning_recent_only_open_interest",
                "positioning_recent_only_long_short",
                "positioning_recent_only_taker_ratio",
                "liquidation_data_not_present",
                "orderbook_l2_not_present",
                "cross_exchange_flow_not_present",
            ],
            "frequency_policy": {
                "primary": "1h",
                "allowed_after_preflight": ["3h", "6h", "12h", "24h", "48h labels from 1h panel"],
                "not_authorized_yet": ["5m_search", "15m_search", "multi_frequency_evidence_stacking"],
            },
        },
        "arms": arms,
        "budget_ladder": budget,
        "mandatory_preflight_before_level1": preflight,
        "level1_stop_rules": {
            "unique_expr_ratio_min": 0.90,
            "field_family_combo_min": 24,
            "operator_combo_min": 12,
            "non_may_preselection_pass_rate_min": 0.10,
            "placebo_research_candidates_max": 0,
            "same_family_shortlist_share_max": 0.25,
            "selected_may_severe_fail_share_warn": 0.75,
            "near_miss_nonplacebo_min": 10,
            "near_miss_family_min": 3,
            "non_flow_or_taker_near_miss_min": 1,
            "return_corr_cluster_growth_required": True,
        },
        "allowed_labels": [
            "A7L_RESEARCH_CANDIDATE",
            "A7L_NEAR_MISS_COST_FAIL",
            "A7L_NEAR_MISS_LAG_FAIL",
            "A7L_NEAR_MISS_MAY_STRESS_FAIL",
            "A7L_RESIDUAL_ONLY_CLUE",
            "A7L_REJECTED",
        ],
        "blocked_labels": ["ALPHA_PROOF", "SHADOW_READY", "PAPER_READY", "LIVE_READY", "PRODUCTION_READY"],
        "next_step": "A7L-1B implementation preflight only; do not run level1 budget ladder yet.",
    }
    contract["stable_contract_hash"] = stable_hash(
        {k: v for k, v in contract.items() if k not in {"generated_at", "stable_contract_hash"}}
    )

    contract_path = A7L1_DIR / f"crypto_a7l1_search_space_contract_{DATE_TAG}.json"
    ladder_path = A7L1_DIR / f"crypto_a7l1_budget_ladder_contract_{DATE_TAG}.json"
    manifest_path = A7L1_DIR / f"crypto_a7l1_manifest_{DATE_TAG}.json"
    arm_path = A7L1_DIR / "a7l1_arm_contract.csv"
    preflight_path = A7L1_DIR / "a7l1_required_preflight_checks.csv"
    stop_path = A7L1_DIR / "a7l1_budget_ladder_stop_rules.csv"

    write_json(contract_path, contract)
    write_json(
        ladder_path,
        {
            "generated_at": now,
            "source_contract": str(contract_path),
            "budget_ladder": budget,
            "level1_stop_rules": contract["level1_stop_rules"],
            "authorizes_budget_ladder_level1": False,
            "stable_contract_hash": stable_hash({"budget_ladder": budget, "stop_rules": contract["level1_stop_rules"]}),
        },
    )
    write_csv(
        arm_path,
        arms,
        [
            "arm",
            "purpose",
            "primary_families",
            "required_horizons",
            "ranking_terms",
            "blocked_patterns",
            "preflight_min_field_combo_count",
            "preflight_min_preselection_rate",
        ],
    )
    write_csv(preflight_path, preflight, ["check_id", "required", "description"])
    write_csv(
        stop_path,
        [
            {"rule": key, "value": value}
            for key, value in contract["level1_stop_rules"].items()
        ],
        ["rule", "value"],
    )

    manifest = {
        "generated_at": now,
        "decision": contract["decision"],
        "alpha_proof_status": contract["alpha_proof_status"],
        "executes_search": False,
        "executes_replay": False,
        "authorizes_a7l1b_implementation_preflight": True,
        "authorizes_budget_ladder_level1": False,
        "authorizes_alpha_proof": False,
        "source_a7l0_decision": source["a7l0_decision"],
        "source_a7l0_blockers": source["a7l0_blockers"],
        "stable_contract_hash": contract["stable_contract_hash"],
        "outputs": {
            "contract": str(contract_path),
            "budget_ladder_contract": str(ladder_path),
            "arm_contract": str(arm_path),
            "required_preflight_checks": str(preflight_path),
            "budget_ladder_stop_rules": str(stop_path),
        },
    }
    write_json(manifest_path, manifest)

    report_path = REPORT_DIR / f"CRYPTO_A7L1_SEARCH_SPACE_REDESIGN_SPEC_{DATE_TAG}.md"
    lines = [
        "# Crypto A7L-1 Search-Space Redesign Spec",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{contract['decision']}`",
        "- alpha_proof_status: `NOT_ALPHA_PROOF`",
        "- executes_search: `False`",
        "- executes_replay: `False`",
        "- authorizes_a7l1b_implementation_preflight: `True`",
        "- authorizes_budget_ladder_level1: `False`",
        f"- stable_contract_hash: `{contract['stable_contract_hash']}`",
        "",
        "## Source State",
        "",
        f"- A7L-0 decision: `{source['a7l0_decision']}`",
        f"- A7L-0 blockers: `{source['a7l0_blockers']}`",
        "",
        "A7K did not falsify broader crypto formula search. It falsified the current narrow generator/gate combination and blocked same-generator blind budget expansion.",
        "",
        "## Boundary",
        "",
        "- May 2026 remains a known adversarial stress set.",
        "- May is forbidden in ranking, reward, thresholds, weights, candidate selection, and generator tuning.",
        "- A7L-1 only authorizes implementation preflight, not level-1 budget ladder search.",
        "",
        "## Proposed Arms",
        "",
        "| arm | purpose | primary families | blocked patterns |",
        "|---|---|---|---|",
    ]
    for row in arms:
        lines.append(
            f"| `{row['arm']}` | {row['purpose']} | `{row['primary_families']}` | `{row['blocked_patterns']}` |"
        )
    lines += [
        "",
        "## Budget Ladder",
        "",
        "| level | generated_total | status | hard stop |",
        "|---|---:|---|---|",
    ]
    for row in budget:
        lines.append(
            f"| `{row['level']}` | {row['generated_total']} | `{row['status']}` | {row['hard_stop_if']} |"
        )
    lines += [
        "",
        "## Level-1 Stop Rules",
        "",
        f"- unique expression ratio >= `{contract['level1_stop_rules']['unique_expr_ratio_min']}`",
        f"- field-family combo count >= `{contract['level1_stop_rules']['field_family_combo_min']}`",
        f"- operator combo count >= `{contract['level1_stop_rules']['operator_combo_min']}`",
        f"- non-May preselection pass rate >= `{contract['level1_stop_rules']['non_may_preselection_pass_rate_min']}`",
        "- placebo research candidates must remain 0.",
        "- near-miss pool must be non-placebo, diverse, and not only flow/taker.",
        "- return-corr cluster diversity must grow with budget.",
        "",
        "## Decision",
        "",
        "A7L-1 passes as a search-space redesign spec. It does not authorize a 4000-candidate run. The next valid work is A7L-1B implementation preflight.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    decision_path = REPORT_DIR / f"CRYPTO_A7L1_DECISION_RECORD_{DATE_TAG}.md"
    decision_path.write_text(
        "\n".join(
            [
                "# Crypto A7L-1 Decision Record",
                "",
                f"- decision: `{contract['decision']}`",
                "- alpha_proof_status: `NOT_ALPHA_PROOF`",
                "- search_executed: `False`",
                "- replay_executed: `False`",
                "- authorizes_a7l1b_implementation_preflight: `True`",
                "- authorizes_budget_ladder_level1: `False`",
                "- authorizes_shadow_paper_live: `False`",
                "",
                "## Confirmed",
                "",
                "- Same-generator blind budget expansion remains blocked.",
                "- Broader crypto formula search remains unfalsified by A7K.",
                "- A7L budget ladder requires measurable coverage, diversity, non-May preselection, placebo, cost, lag, residual, and cluster-growth checks.",
                "",
                "## Not Confirmed",
                "",
                "- No alpha proof.",
                "- No research candidate.",
                "- No shadow, paper, live, or production readiness.",
                "- No authorization to run the 4000-candidate level-1 ladder before A7L-1B.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
