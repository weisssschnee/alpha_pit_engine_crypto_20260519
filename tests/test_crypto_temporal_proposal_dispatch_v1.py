from __future__ import annotations

import pandas as pd

from alphafactory_crypto.broad_search.search_engine_v1 import MechanismEvolutionV2
from alphafactory_crypto.broad_search.temporal_proposal_dispatch_checker_v1 import (
    _dispatched_rejection_count,
)
from alphafactory_crypto.broad_search.temporal_proposal_dispatch_v1 import (
    build_train_only_historical_prior,
    configure_policy_dispatcher_v1,
    dispatcher_state_hash,
    observe_dispatcher_v1,
    propose_with_dispatcher_v1,
    seal_historical_prior,
    select_mutation_target_v1,
)
from alphafactory_crypto.broad_search.temporal_proposal_dispatch_search_v1 import (
    CHECKPOINT_SIZE,
    LANE_SEEDS,
    STRICT_CAP,
)
from alphafactory_crypto.broad_search.temporal_realization_v2 import ARCHIVE_ID
from alphafactory_crypto.broad_search.temporal_representation_successor_v1 import (
    build_compatibility_inventory,
)

from test_crypto_temporal_representation_successor_v1 import _catalogs
from test_crypto_temporal_program_v1 import CONFIG
from test_crypto_temporal_targeted_deepening_v1 import (
    _synthetic_target_parent_pool,
    _targeted_parent_candidates,
)


def _prior(turnover_attempts: int = 200) -> dict:
    empty = {
        "attempts": 0,
        "matched_positive": 0,
        "basin_retained": 0,
        "new_realization": 0,
        "new_hq_realization": 0,
        "positive_reward": 0,
        "reward_sum": 0.0,
    }
    return seal_historical_prior(
        {
            "schema_version": 1,
            "status": "TRAIN_ONLY_PROPOSAL_PRIOR_READY",
            "campaigns": ["synthetic_train_only"],
            "global": {
                **empty,
                "attempts": 400,
                "matched_positive": 80,
                "basin_retained": 200,
                "new_realization": 60,
                "new_hq_realization": 30,
                "positive_reward": 120,
            },
            "tables": {
                "mutation_target": {
                    "turnover": {**empty, "attempts": turnover_attempts},
                    "mapped_weight": {
                        **empty,
                        "attempts": 100,
                        "matched_positive": 40,
                        "basin_retained": 60,
                        "new_realization": 20,
                        "new_hq_realization": 12,
                        "positive_reward": 50,
                    },
                },
                "edit_type": {
                    "binding": {
                        **empty,
                        "attempts": 100,
                        "matched_positive": 55,
                        "basin_retained": 70,
                        "new_realization": 25,
                        "new_hq_realization": 15,
                        "positive_reward": 60,
                    },
                    "component": {**empty, "attempts": 50},
                },
            },
            "forbidden_fields_verified": True,
            "validation_reads": 0,
            "oos_reads": 0,
            "holdout_reads": 0,
            "forward_reads": 0,
            "promotion_reads": 0,
            "sealed_reads": 0,
        }
    )


def _policy() -> tuple[MechanismEvolutionV2, dict]:
    registry, catalog, parameters, candidates = _targeted_parent_candidates(8)
    pool = _synthetic_target_parent_pool(candidates)
    policy = MechanismEvolutionV2(
        20260815,
        registry,
        tuple(mechanism for mechanism, _ in catalog),
        {**parameters, "duplicate_resample_limit": 64},
    )
    policy.configure_targeted_parent_pool(pool)
    baseline_rows = {}
    for candidate_id, record in pool["parent_records"].items():
        baseline_rows[candidate_id] = {
            "mapped_weight_descriptor_id": "mapped-0",
            "turnover_path_descriptor_id": "turnover-0",
            "raw_fields_json": "[\"oi\"]",
            "selected_asset_overlap_id": "assets-0",
            "realization_cell_id": "cell-0",
            "matched_positive": True,
            "lineage_depth": 0,
            **record,
        }
    policy.realization_v2_state = {
        "schema_version": 1,
        "archive_id": ARCHIVE_ID,
        "target_parent_pool_sha256": pool["target_parent_pool_sha256"],
        "baseline_rows": baseline_rows,
        "descendants": {},
        "p1_basin_selection_weight": 2,
        "generic_parameter_mutation_probability": 0.25,
        "mutation_target_counts": {},
        "admission_counts": {},
    }
    configure_policy_dispatcher_v1(policy, historical_prior=_prior())
    return policy, pool


def test_dispatcher_builds_scores_and_selects_one_legal_unseen_candidate() -> None:
    policy, pool = _policy()
    temporal, mechanism = _catalogs()
    inventory = build_compatibility_inventory(temporal, mechanism)
    candidate, metadata = propose_with_dispatcher_v1(
        policy,
        scale_contract=CONFIG["time_scale_authority"],
        inventory=inventory,
    )
    receipt = metadata["dispatch_receipt"]
    assert candidate.candidate_id in policy.seen
    assert receipt["legal_candidates_scored"] >= 1
    assert 1 <= receipt["selected_rank"] <= receipt["legal_candidates_scored"]
    assert set(receipt["score_components"]) == {
        "economic_prior",
        "novelty_value",
        "exploration_bonus",
        "known_failure_penalty",
        "total",
    }
    assert metadata["targeted_parent_pool_sha256"] == pool["target_parent_pool_sha256"]
    assert receipt["candidate_feature_hash"]


def test_dispatcher_feedback_is_checkpointed_inside_policy_state() -> None:
    policy, _ = _policy()
    before = dispatcher_state_hash(policy)
    receipt = {
        "schema_version": 1,
        "dispatcher_id": "TEMPORAL_PROPOSAL_DISPATCHER_V1",
        "candidate_features": {
            "program_family_id": "P1_POSITION_STATE_CHANGE_TO_RESPONSE",
            "economic_basin_id": "ECO_090_001",
            "semantic_edit_type": "binding",
            "mutation_target": "mapped_weight",
            "operator_path": "Delta",
            "field_signature": "oi",
            "construction_route": "DIMENSION_AWARE_PARAMETER_MUTATION",
        },
        "selected_score_decile": 0,
    }
    receipt = {**receipt, "dispatch_receipt_sha256": seal_historical_prior(receipt)["prior_sha256"]}
    outcomes = observe_dispatcher_v1(
        policy,
        ledger_row={"matched_positive": True, "search_reward": 1.25},
        dispatch_receipt=receipt,
        basin_retained=True,
        new_realization=True,
        new_hq_realization=True,
    )
    assert all(outcomes[name] for name in ("matched_positive", "basin_retained", "new_realization", "new_hq_realization", "positive_reward"))
    assert dispatcher_state_hash(policy) != before
    restored = MechanismEvolutionV2.from_state(policy.registry, policy.export_state())
    assert restored.state_hash() == policy.state_hash()


def test_turnover_with_zero_historical_conversion_is_not_primary_target() -> None:
    policy, _ = _policy()
    draws = [select_mutation_target_v1(policy, "ECO_090_001") for _ in range(200)]
    assert draws.count("turnover") < draws.count("mapped_weight")
    assert draws.count("turnover") > 0


def test_historical_prior_uses_only_predeclared_train_fields() -> None:
    rows = [
        {
            "candidate_id": f"candidate-{index}",
            "program_family_id": "P4_LIQUIDATION_STATE_TO_RESPONSE",
            "targeted_economic_basin_id": "ECO_090_001",
            "semantic_edit_type": edit,
            "matched_positive": matched,
            "search_reward": 1.0 if matched else -1.0,
            "validation_label": "MUST_NOT_BE_CONSUMED",
            "oos_reward": 999.0,
            "sealed_label": True,
        }
        for index, (edit, matched) in enumerate(
            (("binding", True), ("normalization", True), ("component", False), ("operator", False))
        )
    ]
    prior = build_train_only_historical_prior(
        [{"campaign_id": "train-a", "rows": rows[:2]}, {"campaign_id": "train-b", "rows": rows[2:]}]
    )
    assert prior["forbidden_fields_verified"] is True
    assert prior["validation_reads"] == prior["oos_reads"] == prior["sealed_reads"] == 0
    assert prior["calibration"]["strong_edit_ranked_above_weak"] is True
    assert prior["calibration"]["severe_basin_concentration"] is True
    assert "validation_label" not in prior["safe_fields"]


def test_dispatch_sequence_and_checkpoint_restore_are_deterministic() -> None:
    temporal, mechanism = _catalogs()
    inventory = build_compatibility_inventory(temporal, mechanism)
    first, _ = _policy()
    second, _ = _policy()
    first_ids = []
    second_ids = []
    for _ in range(8):
        first_ids.append(
            propose_with_dispatcher_v1(
                first, scale_contract=CONFIG["time_scale_authority"], inventory=inventory
            )[0].candidate_id
        )
        second_ids.append(
            propose_with_dispatcher_v1(
                second, scale_contract=CONFIG["time_scale_authority"], inventory=inventory
            )[0].candidate_id
        )
    assert first_ids == second_ids
    restored = MechanismEvolutionV2.from_state(first.registry, first.export_state())
    assert restored.state_hash() == first.state_hash()
    next_first = propose_with_dispatcher_v1(
        first, scale_contract=CONFIG["time_scale_authority"], inventory=inventory
    )
    next_restored = propose_with_dispatcher_v1(
        restored, scale_contract=CONFIG["time_scale_authority"], inventory=inventory
    )
    assert next_first[0].candidate_id == next_restored[0].candidate_id
    assert next_first[1]["dispatch_receipt"] == next_restored[1]["dispatch_receipt"]


def test_search_budget_is_one_20k_lane_with_10k_diagnostic_only() -> None:
    assert STRICT_CAP == 20_000
    assert CHECKPOINT_SIZE == 2_000
    assert len(LANE_SEEDS) == len(set(LANE_SEEDS)) == 4


def test_dispatch_count_includes_selected_pre_strict_rejections() -> None:
    rejected = pd.DataFrame(
        {
            "status": [
                "PROPOSAL_REJECT",
                "EXACT_OR_REPLAY_REJECT",
                "PAIR_REJECTED",
                "PAIR_REJECTED",
            ]
        }
    )

    assert _dispatched_rejection_count(rejected) == 3
