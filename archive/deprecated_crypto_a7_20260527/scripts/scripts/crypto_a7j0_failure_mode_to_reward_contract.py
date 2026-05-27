from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from crypto_a7_validation_utils import REPORT_DIR, RUNTIME_DIR


A7J0_DIR = RUNTIME_DIR / "a7j0_failure_mode_to_reward_contract"
DATE_TAG = "20260520"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def main() -> int:
    A7J0_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_now()

    contract = {
        "contract_id": "CRYPTO_A7J_REWARD_GENERATOR_REDESIGN_FROM_FAILURE_MODES_V1",
        "generated_at": now,
        "decision": "PASS_A7J0_FAILURE_MODE_TO_REWARD_CONTRACT",
        "executes_search": False,
        "authorizes_a7j1": True,
        "authorizes_a7j2": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "objective": (
            "Translate A7I failure modes into a redesigned reward/generator contract "
            "without using May 2026 for ranking, threshold tuning, weight selection, or candidate selection."
        ),
        "source_evidence": {
            "a7i_final_decision": "HOLD_CRYPTO_A7I_NO_ALPHA_PROOF",
            "a7i1c_dominant_failure": "raw_may_severely_negative",
            "a7i2_unique_candidate_failure": [
                "raw_may_materially_negative",
                "cost20_recent_negative",
                "lag1_may_severely_negative",
                "may_symbol_loo_weak",
            ],
            "placebo_contamination": "not_observed",
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
            ],
            "mechanical_checks_required": [
                "score_components_have_no_may_columns",
                "selection_trace_has_no_may_derived_threshold_or_weight",
                "delete_may_columns_does_not_change_ranking",
                "shuffle_may_labels_does_not_change_ranking",
            ],
        },
        "reward_terms": {
            "positive_terms": [
                "raw_validation_recent_score",
                "residual_vs_fundingcore_validation_recent_score",
                "residual_vs_core4_recent_score",
                "cost20_validation_recent_survival_score",
                "execution_lag1_validation_recent_survival_score",
                "symbol_month_stability_score",
            ],
            "negative_terms": [
                "funding_beta_penalty",
                "core4_beta_penalty",
                "turnover_cost_penalty",
                "drawdown_penalty",
                "top_loss_concentration_penalty",
                "duplicate_family_penalty",
            ],
            "explicitly_excluded_terms": [
                "raw_may_score",
                "residual_may_score",
                "may_symbol_loo_score",
                "may_threshold_optimization",
            ],
        },
        "candidate_label_policy": {
            "A7J_RESEARCH_CANDIDATE": {
                "requires": [
                    "raw_validation_10bps_positive",
                    "raw_recent_10bps_positive",
                    "residual_funding_validation_recent_positive",
                    "residual_core4_recent_positive",
                    "cost20_recent_nonnegative",
                    "lag1_recent_nonnegative",
                    "not_funding_or_core4_baseline",
                    "not_residual_only_hedge_clue",
                    "placebo_negative",
                    "duplicate_family_cap_pass",
                ],
                "may_handling": "May stress can veto or label after selection, but cannot create rank advantage.",
            },
            "A7J_CLUE_ONLY": {
                "examples": [
                    "positive residual but standalone raw negative",
                    "positive 10bps but cost20 or lag fragile",
                    "May stress severe fail after selection",
                ]
            },
            "NEGATIVE_CONTROL": {
                "examples": ["random_noise", "row_shuffle", "time_shuffle", "sign_flip", "wrong_lag_placebo"]
            },
        },
        "known_object_expected_classification": {
            "FundingCore": "MANDATORY_BASELINE_NOT_CANDIDATE",
            "Core4": "RESEARCH_BENCHMARK_NOT_CANDIDATE",
            "Rank(taker_imbalance)": "HOLD_RESIDUAL_ONLY_HEDGE_CLUE",
            "i2_microstructure_lite_113": "A7J_CLUE_ONLY_COST_LAG_MAY_FRAGILE",
            "placebo_random": "NEGATIVE_CONTROL",
        },
        "a7j2_budget_if_a7j1_passes": {
            "arms": {
                "I0_basis_premium": {"generated": 250, "selected": 64},
                "I1_flow_liquidity": {"generated": 250, "selected": 64},
                "I2_microstructure_lite": {"generated": 250, "selected": 64},
                "I3_placebo_random": {"generated": 250, "selected": 64},
            },
            "frequency": "1h_only",
            "primary_cost": "10bps",
            "severe_cost": "20bps",
            "execution_lag1_stress_required": True,
            "budget_expansion_allowed": False,
        },
    }

    contract_path = A7J0_DIR / f"crypto_a7j0_reward_generator_contract_{DATE_TAG}.json"
    write_json(contract_path, contract)

    manifest = {
        "generated_at": now,
        "decision": contract["decision"],
        "contract": str(contract_path),
        "authorizes_a7j1": True,
        "authorizes_a7j2": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    manifest_path = A7J0_DIR / f"crypto_a7j0_manifest_{DATE_TAG}.json"
    write_json(manifest_path, manifest)

    report_path = REPORT_DIR / f"CRYPTO_A7J0_FAILURE_MODE_TO_REWARD_CONTRACT_{DATE_TAG}.md"
    lines = [
        "# Crypto A7J-0 Failure-Mode-to-Reward Contract",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{contract['decision']}`",
        "- executes_search: `False`",
        "- authorizes_a7j1: `True`",
        "- authorizes_a7j2: `False`",
        "- authorizes_alpha_proof: `False`",
        "",
        "## Hard Boundary",
        "",
        "- May 2026 is a known adversarial stress set.",
        "- May cannot enter ranking, reward score, threshold tuning, weight selection, candidate selection, or generator tuning.",
        "- May may only appear as post-selection stress label / veto / failure attribution.",
        "",
        "## Reward Redesign",
        "",
        "Positive terms: raw validation/recent, residual vs FundingCore/Core4, 20bps cost survival, 1bar lag survival, symbol/month stability.",
        "",
        "Penalty terms: FundingCore/Core4 beta, turnover/cost, drawdown, top-loss concentration, duplicate family concentration.",
        "",
        "## Expected Known-Object Classification",
        "",
        "| object | expected classification |",
        "|---|---|",
    ]
    for obj, label in contract["known_object_expected_classification"].items():
        lines.append(f"| `{obj}` | `{label}` |")
    lines += [
        "",
        "## Next",
        "",
        "Run A7J-1 redesigned runner preflight. Do not run A7J-2 until known-object classification and May-exclusion checks pass.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    decision_path = REPORT_DIR / f"CRYPTO_A7J0_DECISION_RECORD_{DATE_TAG}.md"
    decision_path.write_text(
        "\n".join(
            [
                "# Crypto A7J-0 Decision Record",
                "",
                f"- decision: `{contract['decision']}`",
                "- alpha_proof_status: `NOT_ALPHA_PROOF`",
                "- search_executed: `False`",
                "- A7J-1: `AUTHORIZED`",
                "- A7J-2: `NOT_AUTHORIZED_UNTIL_A7J1_PASS`",
                "",
                "A7J-0 freezes the redesigned reward/generator boundary from A7I failure modes. May remains stress-only.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print("A7J0_REPORT=" + str(report_path))
    print("A7J0_DECISION_RECORD=" + str(decision_path))
    print("A7J0_CONTRACT=" + str(contract_path))
    print("DECISION=" + contract["decision"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
