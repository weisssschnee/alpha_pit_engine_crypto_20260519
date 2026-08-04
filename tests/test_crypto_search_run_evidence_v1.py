from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from alphafactory_crypto.broad_search.compositional18m import CandidateSpec
from alphafactory_crypto.broad_search.expression import Expression
from alphafactory_crypto.broad_search.pair18m import (
    SEARCH_REWARD_AUTHORITY,
    mechanism_realization_provenance,
)
from alphafactory_crypto.broad_search.experiment_authority import (
    resolve_search_economic_receipt,
)
from alphafactory_crypto.broad_search.search_engine_v1 import (
    SEARCH_EVIDENCE_V1_ARMS,
    SEARCH_EVIDENCE_V1_CAMPAIGN,
    SEARCH_EVIDENCE_V1_SEEDS,
    SEARCH_EVIDENCE_V11_ARMS,
    SEARCH_EVIDENCE_V11_CAMPAIGN,
    SEARCH_EVIDENCE_V11_SEEDS,
    _economic_campaign_seeds,
    _ledger_row,
    _load_search_evidence_v1_contract,
    _payload_sha,
    _search_evidence_provenance_errors,
    _search_evidence_repair_assessment,
    _search_evidence_v1_expected_checkpoint_allocations,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def _comparison(equal: bool, difference_fraction: float) -> dict[str, object]:
    return {
        "stages": {"SIGNAL": {"equal": equal}},
        "signal_difference_fraction": difference_fraction,
    }


def test_hierarchical_mechanism_realization_uses_ablation_axes() -> None:
    candidate = CandidateSpec(
        candidate_id="candidate",
        skeleton_id="skeleton",
        mechanism_family="CONDITIONAL_TEST",
        expression=Expression(
            "StateModulation",
            (
                Expression(
                    "RatioInteraction",
                    (Expression.raw("a"), Expression.raw("b")),
                ),
                Expression.raw("c"),
            ),
        ),
        control=Expression.raw("a"),
        horizon_hours=1,
        mapping_id="CROSS_SECTIONAL_ZERO_NET",
        raw_fields=("a", "b", "c"),
        field_families=("a", "b", "c"),
        rolling_windows=(),
        expression_depth=3,
        operator_path="StateModulation(RatioInteraction(Raw,Raw),Raw)",
    )
    provenance = {
        "comparisons": {
            "primary_vs_left_control": _comparison(False, 0.25),
            "primary_vs_right_control": _comparison(False, 0.50),
            "ab_vs_interaction_left_control": _comparison(False, 0.75),
            "ab_vs_interaction_right_control": _comparison(True, 0.0),
        }
    }
    provenance["provenance_sha256"] = _payload_sha(provenance)

    result = mechanism_realization_provenance(
        candidate=candidate,
        hierarchical_three_axis=True,
        control_provenance=provenance,
    )

    assert result["declared_axis_count"] == 3
    assert result["active_axis_count"] == 2
    assert result["status"] == "PARTIAL_DECLARED_AXES_ACTIVE"
    assert result["condition_effect_rate"] == 0.25
    assert [row["active"] for row in result["axes"]] == [False, True, True]
    assert len(str(result["provenance_sha256"])) == 64


def test_evidence_campaign_reuses_v23_policy_with_new_fresh_seeds() -> None:
    config, catalog, _ = _load_search_evidence_v1_contract(REPO_ROOT)
    allocations = _search_evidence_v1_expected_checkpoint_allocations(
        stages=config["stages"],
        seeds=SEARCH_EVIDENCE_V1_SEEDS,
    )

    assert len(catalog) > 0
    assert _economic_campaign_seeds(SEARCH_EVIDENCE_V1_CAMPAIGN) == (
        SEARCH_EVIDENCE_V1_SEEDS
    )
    assert set(allocations) == {0, 1, 2, 3}
    assert all(
        allocation == {arm: 1000 for arm in SEARCH_EVIDENCE_V1_ARMS}
        for allocation in allocations.values()
    )
    assert config["validation"]["authorized"] is False
    assert config["evidence_contract"]["passive_diagnostics_only"] is True
    assert config["boundaries"]["search_policy_change"] is False


def test_evidence_campaign_receipt_is_consumed_after_verification_failure() -> None:
    receipt = resolve_search_economic_receipt(
        REPO_ROOT,
        "config/crypto_search_run_evidence_v1_receipt.json",
    )

    assert receipt["result"] == (
        "RUN_AUTHORIZATION_CONSUMED_ENGINE_VERIFICATION_FAILED"
    )
    assert receipt["run_authorized"] is False
    assert receipt["run_outcome"] == {
        "status": "ENGINE_VERIFICATION_FAILED",
        "reason": "LEDGER_EVIDENCE_COLUMNS_MISSING",
        "runtime": "runtime/crypto_search_run_evidence_v1_20260804",
        "producer_source_sha": (
            "fea74611c491d2d9a77d8013bc6cdaf427b4fd8c"
        ),
        "generation_attempts": 12_034,
        "strict_evaluated_count": 8_000,
        "checkpoint": "checkpoint_003",
        "artifact_bundle_sha256": (
            "04FB3B25295F44C741333431904A0FDED064CCA1D122A9EEEEE40D1C3C76B2CF"
        ),
        "checker_result": "FAIL",
        "sealed_reads": 0,
        "rescue_rerun_started": False,
    }
    assert receipt["search_campaign"]["runner_campaign"] == (
        SEARCH_EVIDENCE_V1_CAMPAIGN
    )
    assert receipt["validation"]["role"] == "NOT_AUTHORIZED"
    assert receipt["holdout"]["read_allowed"] is False


def test_evidence_v11_freezes_one_fresh_checkpoint_without_policy_change() -> None:
    config, catalog, _ = _load_search_evidence_v1_contract(
        REPO_ROOT, campaign=SEARCH_EVIDENCE_V11_CAMPAIGN
    )
    allocations = _search_evidence_v1_expected_checkpoint_allocations(
        stages=config["stages"],
        seeds=SEARCH_EVIDENCE_V11_SEEDS,
        arms=SEARCH_EVIDENCE_V11_ARMS,
        checkpoint_size=2000,
        checkpoint_count=1,
    )

    assert len(catalog) > 0
    assert _economic_campaign_seeds(SEARCH_EVIDENCE_V11_CAMPAIGN) == (
        SEARCH_EVIDENCE_V11_SEEDS
    )
    assert allocations == {
        0: {arm: 1000 for arm in SEARCH_EVIDENCE_V11_ARMS}
    }
    expected_search_values = {
        "strict_evaluated_target": 2000,
        "checkpoint_size": 2000,
        "checkpoint_count": 1,
        "raw_generation_attempts_maximum": 12500,
        "wall_time_seconds_maximum": 10800,
    }
    assert {
        key: config["search"][key] for key in expected_search_values
    } == expected_search_values
    assert config["validation"]["authorized"] is False
    assert config["boundaries"]["automatic_expansion"] is False
    assert config["question_scope"]["Q03_ACTUAL_EXPOSURE"] == "IN_SCOPE"
    assert config["question_scope"]["Q15_MIGRATION"].startswith(
        "NOT_AUTHORIZED"
    )


def test_evidence_v11_receipt_is_one_time_authorized_and_hash_bound() -> None:
    receipt = resolve_search_economic_receipt(
        REPO_ROOT,
        "config/crypto_search_run_evidence_v1_1_receipt.json",
    )

    assert receipt["result"] == "RUN_AUTHORIZED_CONDITIONAL_DEVELOPMENT"
    assert receipt["run_authorized"] is True
    assert receipt["run_outcome"] == {}
    assert receipt["search_campaign"] == {
        "runner_campaign": SEARCH_EVIDENCE_V11_CAMPAIGN,
        "runtime_date": "20260805",
        "carrier_id": "OI_MARK_RANKS51_200_X_AGGTRADES_TOP200_ALIGNED",
        "carrier_manifest": (
            "runtime/crypto_search_engine_v1_4_oi_flow_20260728/"
            "aligned_carrier_manifest.json"
        ),
        "carrier_cache_identity_sha256": (
            "E8BFD15AF1EA58807A75868D52AD3535126DFB77CEDEB404EEE8E690AA58F2BA"
        ),
        "field_count": 115,
        "strict_evaluated_target": 2000,
        "checkpoint_size": 2000,
        "checkpoint_count": 1,
        "fresh_state": True,
        "seed_set": list(SEARCH_EVIDENCE_V11_SEEDS),
        "seed_derivation": (
            "SHA256_U32_BIG_ENDIAN(epoch_id|seed|ordinal_0_TO_1)"
        ),
    }
    assert receipt["validation"]["role"] == "NOT_AUTHORIZED"
    assert receipt["holdout"]["read_allowed"] is False


def test_strict_ledger_row_persists_observed_behavior_provenance() -> None:
    candidate = CandidateSpec(
        candidate_id="candidate",
        skeleton_id="skeleton",
        mechanism_family="BINARY_TEST",
        expression=Expression(
            "RatioInteraction",
            (Expression.raw("a"), Expression.raw("b")),
        ),
        control=Expression.raw("a"),
        horizon_hours=1,
        mapping_id="CROSS_SECTIONAL_ZERO_NET",
        raw_fields=("a", "b"),
        field_families=("a", "b"),
        rolling_windows=(),
        expression_depth=2,
        operator_path="RatioInteraction(Raw,Raw)",
    )

    def comparison(primary_label: str, control_label: str) -> dict[str, object]:
        stage_order = [
            "SIGNAL",
            "ORIENTED_SIGNAL",
            "RANK",
            "NORMALIZED_SCORE",
            "SELECTION",
            "CAPPED_WEIGHT",
            "MAPPED_WEIGHT",
            "EXECUTABLE_WEIGHT",
        ]
        payload: dict[str, object] = {
            "schema_version": "CRYPTO_CONTROL_DEGENERACY_PROVENANCE_V1",
            "primary_label": primary_label,
            "control_label": control_label,
            "mapping_id": candidate.mapping_id,
            "stage_order": stage_order,
            "stages": {
                stage: {
                    "primary_identity_sha256": "1" * 64,
                    "control_identity_sha256": "2" * 64,
                    "equal": False,
                }
                for stage in stage_order
            },
            "first_equal_stage": None,
            "first_divergent_stage": "SIGNAL",
            "first_reconverged_stage": None,
            "signal_difference_fraction": 1.0,
            "final_weight_equal": False,
            "final_behavior_equal": False,
        }
        payload["provenance_sha256"] = _payload_sha(payload)
        return payload

    candidate_spec_sha256 = _payload_sha(candidate.to_dict())
    control_provenance = {
        "schema_version": "CRYPTO_PAIR_CONTROL_PROVENANCE_V1",
        "candidate_id": candidate.candidate_id,
        "candidate_spec_sha256": candidate_spec_sha256,
        "comparisons": {
            "primary_vs_left_control": comparison("primary", "left_control"),
            "primary_vs_right_control": comparison("primary", "right_control"),
        },
    }
    control_provenance["provenance_sha256"] = _payload_sha(control_provenance)
    realization = {
        "schema_version": "CRYPTO_MECHANISM_REALIZATION_PROVENANCE_V1",
        "candidate_id": candidate.candidate_id,
        "mechanism_family": candidate.mechanism_family,
        "skeleton_id": candidate.skeleton_id,
        "operator_path": candidate.operator_path,
        "hierarchical_three_axis": False,
        "declared_axis_count": 2,
        "active_axis_count": 2,
        "axes": [
            {
                "axis_id": "A",
                "evidence_comparison": "primary_vs_right_control",
                "active": True,
                "signal_difference_fraction": 1.0,
            },
            {
                "axis_id": "B",
                "evidence_comparison": "primary_vs_left_control",
                "active": True,
                "signal_difference_fraction": 1.0,
            },
        ],
        "condition_effect_rate": None,
        "status": "ALL_DECLARED_AXES_ACTIVE",
        "control_degeneracy_provenance_sha256": control_provenance[
            "provenance_sha256"
        ],
        "authority": (
            "OUTCOME_FREE_SIGNAL_ABLATION_COMPARISONS_ON_SHARED_SUPPORT_MAPPING_"
            "HORIZON_AND_EXECUTION"
        ),
    }
    realization["provenance_sha256"] = _payload_sha(realization)
    economic = {
        "gross_mean": 0.01,
        "net_mean": 0.005,
        "net_lcb": 0.001,
        "turnover_mean": 0.1,
        "cost_mean": 0.0005,
        "support": 100,
        "month_metrics": [],
    }
    evaluation = {
        "search_reward": 1.0,
        "search_reward_authority": SEARCH_REWARD_AUTHORITY,
        "search_reward_feedback": {},
        "pair_reward": 0.5,
        "matched_positive": True,
        "feedback": {"violations": [], "left_axis": {}, "right_axis": {}},
        "primary": economic,
        "control": economic,
        "incremental": economic,
        "behavior": {
            "behavior_family_id": "family",
            "primary_behavior_id": "primary",
            "control_behavior_id": "control",
            "incremental_behavior_id": "incremental",
            "coordinate_data_binding_id": "coordinate",
            "rank_descriptor_id": "rank",
            "selected_asset_overlap_id": "selection",
            "mapped_weight_descriptor_id": "mapped",
            "turnover_path_descriptor_id": "turnover",
            "pit_regime_descriptor_id": "pit",
            "descriptor_contract_sha256": "D" * 64,
        },
        "control_degeneracy_provenance": control_provenance,
        "mechanism_realization_provenance": realization,
        "timings": {},
    }
    proposal = {
        "checkpoint_completion_ordinal": 1,
        "generation_attempt_ordinal": 1,
        "arm": "expanded_mechanism_random_v2_3",
        "seed": SEARCH_EVIDENCE_V1_SEEDS[0],
        "semantic_carriers": ["OI_MARK", "AGGTRADES"],
        "operation": "RANDOM_SAMPLE",
        "parent_ids": [],
        "expression_hash_verified": True,
        "policy_state_hash_before": "before",
        "family_member_count_at_completion": 1,
        "proposal_cpu_seconds": 0.01,
    }
    row = _ledger_row(
        candidate=candidate,
        evaluation=evaluation,
        proposal=proposal,
        archive_row={"is_family_champion": True},
        new_family=True,
        state_hash_after="after",
        checkpoint_index=0,
        completion_ordinal=1,
        arm_completion_ordinal=1,
        worker={
            "process_cpu_seconds": 0.02,
            "wall_seconds": 0.03,
            "worker_rss_bytes": 1,
            "worker_private_bytes": 1,
        },
    )

    assert row["control_degeneracy_provenance_sha256"] == (
        control_provenance["provenance_sha256"]
    )
    assert row["mechanism_realization_sha256"] == realization["provenance_sha256"]
    assert row["declared_axis_count"] == 2
    assert row["active_axis_count"] == 2
    assert row["mechanism_realization_status"] == "ALL_DECLARED_AXES_ACTIVE"
    assert row["strict_evaluated"] is True
    assert _search_evidence_provenance_errors(pd.DataFrame([row])) == []

    degenerate_row = dict(row)
    degenerate_control = json.loads(row["control_degeneracy_provenance_json"])
    left_comparison = degenerate_control["comparisons"][
        "primary_vs_left_control"
    ]
    for stage in left_comparison["stage_order"]:
        stage_row = left_comparison["stages"][stage]
        stage_row["control_identity_sha256"] = stage_row[
            "primary_identity_sha256"
        ]
        stage_row["equal"] = True
    left_comparison["final_weight_equal"] = True
    left_comparison["final_behavior_equal"] = True
    left_comparison["first_equal_stage"] = "SIGNAL"
    left_comparison["first_divergent_stage"] = None
    left_comparison["first_reconverged_stage"] = None
    left_comparison.pop("provenance_sha256")
    left_comparison["provenance_sha256"] = _payload_sha(left_comparison)
    degenerate_control.pop("provenance_sha256")
    degenerate_control["provenance_sha256"] = _payload_sha(degenerate_control)
    degenerate_realization = json.loads(row["mechanism_realization_json"])
    degenerate_realization["control_degeneracy_provenance_sha256"] = (
        degenerate_control["provenance_sha256"]
    )
    degenerate_realization.pop("provenance_sha256")
    degenerate_realization["provenance_sha256"] = _payload_sha(
        degenerate_realization
    )
    degenerate_row["control_degeneracy_provenance_json"] = json.dumps(
        degenerate_control, sort_keys=True, separators=(",", ":")
    )
    degenerate_row["control_degeneracy_provenance_sha256"] = (
        degenerate_control["provenance_sha256"]
    )
    degenerate_row["mechanism_realization_json"] = json.dumps(
        degenerate_realization, sort_keys=True, separators=(",", ":")
    )
    degenerate_row["mechanism_realization_sha256"] = degenerate_realization[
        "provenance_sha256"
    ]
    assert "ledger_evidence:strict_control_degenerate" in (
        _search_evidence_provenance_errors(pd.DataFrame([degenerate_row]))
    )

    missing_provenance = dict(evaluation)
    missing_provenance.pop("control_degeneracy_provenance")
    with pytest.raises(RuntimeError, match="SEARCH_EVIDENCE_PROVENANCE_REQUIRED"):
        _ledger_row(
            candidate=candidate,
            evaluation=missing_provenance,
            proposal=proposal,
            archive_row={"is_family_champion": True},
            new_family=True,
            state_hash_after="after",
            checkpoint_index=0,
            completion_ordinal=1,
            arm_completion_ordinal=1,
            worker={
                "process_cpu_seconds": 0.02,
                "wall_seconds": 0.03,
                "worker_rss_bytes": 1,
                "worker_private_bytes": 1,
            },
            require_evidence_provenance=True,
        )


def test_evidence_checker_rejects_non_observed_placeholder_provenance() -> None:
    placeholder = pd.DataFrame(
        [
            {
                "candidate_id": "candidate",
                "control_degeneracy_provenance_json": "NOT_OBSERVED",
                "control_degeneracy_provenance_sha256": "A" * 64,
                "mechanism_realization_json": "NOT_OBSERVED",
                "mechanism_realization_sha256": "B" * 64,
                "declared_axis_count": 2,
                "active_axis_count": 2,
                "mechanism_realization_status": "ALL_DECLARED_AXES_ACTIVE",
            }
        ]
    )

    assert "ledger_evidence:provenance_json" in (
        _search_evidence_provenance_errors(placeholder)
    )


def test_market_free_repair_fails_closed_when_strict_provenance_was_discarded() -> None:
    ledger = pd.DataFrame(
        [{"candidate_id": "strict", "pair_reward": 1.0, "search_reward": 1.0}]
    )
    evidence = pd.DataFrame(
        [
            {
                "candidate_id": "strict",
                "proposal_status": "STRICT_EVALUATED",
                "control_degeneracy_provenance_json": None,
                "control_degeneracy_provenance_sha256": None,
                "mechanism_realization_json": None,
                "mechanism_realization_sha256": None,
                "declared_axis_count": None,
                "active_axis_count": None,
                "mechanism_realization_status": None,
            },
            {
                "candidate_id": "degenerate",
                "proposal_status": "CONTROL_DEGENERATE",
                "control_degeneracy_provenance_json": "{}",
                "control_degeneracy_provenance_sha256": "A" * 64,
                "mechanism_realization_json": "{}",
                "mechanism_realization_sha256": "B" * 64,
                "declared_axis_count": 2,
                "active_axis_count": 1,
                "mechanism_realization_status": "PARTIAL_DECLARED_AXES_ACTIVE",
            },
        ]
    )
    failures = evidence.loc[
        evidence["proposal_status"].eq("CONTROL_DEGENERATE")
    ].reset_index(drop=True)

    result = _search_evidence_repair_assessment(ledger, evidence, failures)

    assert result["repair_status"] == "MARKET_FREE_REPAIR_NOT_POSSIBLE"
    assert result["strict_evaluated_count"] == 1
    assert result["strict_provenance_observed_count"] == 0
    assert result["control_degenerate_provenance_observed_count"] == 0
    assert result["fully_joined_strict_observation_count"] == 0
    assert result["market_reevaluation_required_for_missing_rows"] is True
