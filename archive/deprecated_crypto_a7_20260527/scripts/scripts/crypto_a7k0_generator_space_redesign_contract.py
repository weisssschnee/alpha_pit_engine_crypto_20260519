from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from crypto_a7_validation_utils import REPORT_DIR, RUNTIME_DIR, stable_hash


A7K0_DIR = RUNTIME_DIR / "a7k0_generator_space_redesign_contract"
DATE_TAG = "20260520"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def main() -> int:
    A7K0_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_now()

    contract: dict[str, Any] = {
        "contract_id": "CRYPTO_A7K_GENERATOR_SPACE_REDESIGN_V1",
        "generated_at": now,
        "decision": "PASS_A7K0_GENERATOR_SPACE_REDESIGN_CONTRACT",
        "executes_search": False,
        "executes_replay": False,
        "authorizes_a7k1": True,
        "authorizes_a7k2": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "objective": (
            "Redesign the crypto generator space after A7J exposed low-activity, cost-fragile, "
            "lag-fragile, funding-packaged, and duplicate-family candidate failure modes."
        ),
        "source_decision": {
            "a7j_final": "HOLD_CRYPTO_A7J_NO_RESEARCH_CANDIDATE",
            "same_generator_budget_expansion": "NOT_RECOMMENDED",
            "required_next_step": "generator_space_contract_then_preflight",
        },
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
            ],
        },
        "global_preselection_gates": {
            "coverage_activity": {
                "validation_min_n": 250,
                "recent_min_n": 250,
                "validation_min_gross_exposure": 0.10,
                "recent_min_gross_exposure": 0.10,
                "zero_activity_candidate": "reject_before_selection",
            },
            "raw_viability": {
                "raw_validation_10bps_positive": True,
                "raw_recent_10bps_positive": True,
            },
            "cost_and_lag": {
                "cost20_validation_nonnegative": True,
                "cost20_recent_nonnegative": True,
                "lag1_validation_nonnegative": True,
                "lag1_recent_nonnegative": True,
            },
            "baseline_residual": {
                "residual_vs_fundingcore_validation_positive": True,
                "residual_vs_fundingcore_recent_positive": True,
                "residual_vs_core4_recent_positive": True,
                "max_abs_funding_beta_recent": 0.50,
                "max_abs_core4_beta_recent": 0.50,
            },
            "family_dedup": {
                "formula_fingerprint_dedup_required": True,
                "max_same_family_share_in_shortlist": 0.25,
                "duplicate_expression_variant_stack": "reject_or_downweight",
            },
        },
        "generator_space": {
            "K0_basis_premium_clean": {
                "status": "allowed_with_coverage_and_residual_gates",
                "allowed_features": [
                    "mark_index_ratio",
                    "mark_minus_index",
                    "premium_index",
                    "cs_z_mark_index_ratio",
                    "cs_z_premium_index",
                ],
                "blocked_features": [
                    "spot_perp_basis_unless_core6_lane_explicit",
                    "future_mark_or_index",
                    "next_funding_rate",
                ],
                "required_checks": [
                    "basis_field_contract_centered",
                    "core12_coverage_or_explicit_core6_lane",
                    "residual_vs_fundingcore",
                ],
            },
            "K1_flow_liquidity_clean": {
                "status": "allowed_but_not_taker_standalone",
                "allowed_features": [
                    "quote_asset_volume",
                    "number_of_trades",
                    "avg_trade_size_quote",
                    "quote_volume_mean_6",
                    "quote_volume_mean_12",
                    "quote_volume_mean_24",
                    "taker_buy_ratio",
                    "taker_imbalance",
                ],
                "blocked_patterns": [
                    "residual_only_taker_hedge_as_standalone_alpha",
                    "future_volume",
                    "same_bar_execution_volume_if_not_lagged",
                ],
                "required_checks": [
                    "raw_viability_before_residual_credit",
                    "cost20_survival",
                    "lag1_survival",
                ],
            },
            "K2_microstructure_lite_latency_robust": {
                "status": "allowed_with_execution_lag_gate",
                "allowed_features": [
                    "realized_vol_6",
                    "realized_vol_12",
                    "realized_vol_24",
                    "hl_range",
                    "abs_ret_1",
                    "quote_volume_mean_12",
                    "avg_trade_size_quote",
                ],
                "blocked_patterns": [
                    "near-close_same-bar_edge_without_lag_survival",
                    "high_turnover_cost20_fragile",
                ],
                "required_checks": [
                    "execution_lag1_validation_recent_nonnegative",
                    "cost20_validation_recent_nonnegative",
                    "top_loss_concentration_audit",
                ],
            },
            "K3_placebo_random_control": {
                "status": "mandatory_negative_control",
                "allowed_features": ["seeded_random", "row_shuffle", "time_shuffle", "symbol_shuffle"],
                "required_checks": ["zero_research_candidate"],
            },
        },
        "blocked_from_a7k": [
            "same_generator_budget_expansion_without_space_redesign",
            "May_robust_generator",
            "FundingCore_or_Core4_rescue",
            "taker_imbalance_rescue_as_standalone_alpha",
            "5m_rescue",
            "shadow_paper_live_promotion",
        ],
        "a7k1_preflight_required_outputs": [
            "a7k1_generator_space_manifest.json",
            "a7k1_feature_coverage_audit.csv",
            "a7k1_activity_exposure_audit.csv",
            "a7k1_family_diversity_audit.csv",
            "a7k1_cost_lag_preselection_audit.csv",
            "a7k1_funding_core4_beta_screen.csv",
            "a7k1_may_exclusion_audit.csv",
        ],
        "a7k2_budget_if_a7k1_and_new_space_generator_pass": {
            "arms": 4,
            "generated_per_arm": 250,
            "selected_per_arm": 64,
            "frequency": "1h_only",
            "primary_cost": "10bps",
            "severe_cost": "20bps",
            "execution_lag1_required": True,
            "budget_expansion_allowed": False,
        },
    }
    contract["stable_contract_hash"] = stable_hash(
        {k: v for k, v in contract.items() if k not in {"generated_at", "stable_contract_hash"}}
    )

    contract_path = A7K0_DIR / f"crypto_a7k0_generator_space_contract_{DATE_TAG}.json"
    write_json(contract_path, contract)

    manifest = {
        "generated_at": now,
        "decision": contract["decision"],
        "contract": str(contract_path),
        "stable_contract_hash": contract["stable_contract_hash"],
        "authorizes_a7k1": True,
        "authorizes_a7k2": False,
        "authorizes_alpha_proof": False,
    }
    manifest_path = A7K0_DIR / f"crypto_a7k0_manifest_{DATE_TAG}.json"
    write_json(manifest_path, manifest)

    report_path = REPORT_DIR / f"CRYPTO_A7K0_GENERATOR_SPACE_REDESIGN_CONTRACT_{DATE_TAG}.md"
    lines = [
        "# Crypto A7K-0 Generator-Space Redesign Contract",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{contract['decision']}`",
        "- executes_search: `False`",
        "- executes_replay: `False`",
        "- authorizes_a7k1: `True`",
        "- authorizes_a7k2: `False`",
        "- authorizes_alpha_proof: `False`",
        f"- stable_contract_hash: `{contract['stable_contract_hash']}`",
        "",
        "## Boundary",
        "",
        "- A7J is frozen as method success / alpha discovery failure.",
        "- A7K cannot expand the same generator budget directly.",
        "- May 2026 remains stress-only and cannot enter ranking, reward, threshold tuning, candidate selection, or generator tuning.",
        "",
        "## Generator Space",
        "",
        "| arm | status | key required gate |",
        "|---|---|---|",
    ]
    for arm, spec in contract["generator_space"].items():
        required = ", ".join(spec.get("required_checks", []))
        lines.append(f"| `{arm}` | `{spec['status']}` | `{required}` |")
    lines += [
        "",
        "## Preselection Gates",
        "",
        "- Coverage/activity gate rejects zero-activity and low-exposure candidates before selection.",
        "- Raw validation/recent, 20bps validation/recent, and 1bar-lag validation/recent must be viable before research labeling.",
        "- Residual vs FundingCore/Core4 is mandatory, but residual-only hedge clues are not standalone alphas.",
        "",
        "## Next",
        "",
        "Run A7K-1 generator-space preflight. Do not run A7K-2 until A7K-1 confirms coverage/activity, cost/lag, residual, family diversity, and May-exclusion checks.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    decision_path = REPORT_DIR / f"CRYPTO_A7K0_DECISION_RECORD_{DATE_TAG}.md"
    decision_path.write_text(
        "\n".join(
            [
                "# Crypto A7K-0 Decision Record",
                "",
                f"- decision: `{contract['decision']}`",
                "- alpha_proof_status: `NOT_ALPHA_PROOF`",
                "- search_executed: `False`",
                "- A7K-1: `AUTHORIZED`",
                "- A7K-2: `NOT_AUTHORIZED_UNTIL_A7K1_AND_NEW_SPACE_GENERATOR_PASS`",
                "",
                "A7K-0 converts A7J failure modes into a redesigned generator-space contract. It does not run search or replay.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print("A7K0_REPORT=" + str(report_path))
    print("A7K0_DECISION_RECORD=" + str(decision_path))
    print("A7K0_CONTRACT=" + str(contract_path))
    print("DECISION=" + contract["decision"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
