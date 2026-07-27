from __future__ import annotations

import json
from pathlib import Path

import pytest

from alphafactory_crypto.broad_search.expression import (
    FieldContract,
    TypedExpressionRegistry,
)
from alphafactory_crypto.broad_search.search_engine_v1 import (
    AGGTRADES_SYSTEM_CANARY_FIELDS,
    SEEDS,
    V21_PARAMETERS,
    V12_ARMS,
    V22_PARAMETERS,
    BehaviorArchive,
    TypedEvolutionV2,
    _initial_policies,
    _v12_final_decision,
    _v12_report_text,
    _validate_v12_config,
    run_engine,
)


def _registry() -> TypedExpressionRegistry:
    return TypedExpressionRegistry(
        (
            FieldContract(
                "open_interest_last_change_1h", "RETURN", "dimensionless"
            ),
            FieldContract(
                "open_interest_value_last", "NOTIONAL", "quote_asset"
            ),
            FieldContract("trade_return_1h", "RETURN", "dimensionless"),
            FieldContract(
                "trade_quote_volume", "NOTIONAL", "quote_asset"
            ),
            FieldContract("mark_trade_basis_bps", "BPS", "bps"),
            FieldContract(
                "top_long_short_account_ratio_last", "RATIO", "dimensionless"
            ),
            FieldContract(
                "global_long_short_account_ratio_last",
                "RATIO",
                "dimensionless",
            ),
            FieldContract(
                "top_long_short_position_ratio_last",
                "RATIO",
                "dimensionless",
            ),
            FieldContract(
                "account_position_divergence", "RATIO", "dimensionless"
            ),
            FieldContract("listing_age_days", "AGE", "days"),
            FieldContract("active_universe_size", "STATE", "assets"),
        )
    )


def test_v12_profile_freezes_balanced_fresh_state_collision_control() -> None:
    root = Path(__file__).resolve().parents[1]
    config = json.loads(
        (root / "config/crypto_search_engine_v1_2.json").read_text(
            encoding="utf-8"
        )
    )
    _validate_v12_config(config)
    assert tuple(config["search"]["arms_per_checkpoint"]) == V12_ARMS
    assert config["search"]["strict_evaluated_target"] == 2_000
    assert config["search"]["balanced_micro_batch_size"] == 8
    assert config["search"]["one_inflight_candidate_per_seed_lane"] is True
    assert config["search"]["rotating_seed_lane_submission_order"] is True
    assert config["boundaries"]["future_arm_qualification"] is False
    policies = _initial_policies(_registry(), arms=V12_ARMS)
    evolution = [
        policy
        for key, policy in policies.items()
        if key.startswith("collision_controlled_evolution_v2_2|")
    ]
    assert len(evolution) == len(SEEDS)
    assert all(isinstance(policy, TypedEvolutionV2) for policy in evolution)
    assert all(
        policy.parameters["campaign_local_transition_collision_control"] is True
        and policy.parameters["transition_block_after_collisions"] == 1
        for policy in evolution
    )
    assert V22_PARAMETERS["collision_controlled_evolution_v2_2"][
        "operator_productivity_adaptation"
    ] is True
    assert "blocked_transition_skips" in evolution[0].export_state()
    legacy = TypedEvolutionV2(
        SEEDS[0],
        _registry(),
        V21_PARAMETERS["behavior_niched_evolution_v2_1"],
    )
    assert "blocked_transition_skips" not in legacy.export_state()


def test_v12_final_decision_uses_frozen_engineering_gates_only(
    tmp_path: Path,
) -> None:
    checkpoints = tmp_path / "checkpoints"
    for index in range(2):
        checkpoint = checkpoints / f"checkpoint_{index:03d}"
        checkpoint.mkdir(parents=True)
        (checkpoint / "manifest.json").write_text(
            json.dumps({"restore_verified": True}),
            encoding="utf-8",
        )
    ledger = []
    operations = (
        "EFFECTIVE_GENE_MUTATION_1_TO_3",
        "COMPATIBLE_SKELETON_VARIANT_MUTATION",
        "ONE_POINT_HOMOLOGOUS_GENE_BUNDLE_CROSSOVER",
    )
    for batch_index in range(250):
        lanes = [(arm, seed) for arm in V12_ARMS for seed in SEEDS]
        offset = batch_index % len(lanes)
        rotated_lanes = lanes[offset:] + lanes[:offset]
        for slot, (arm, seed) in enumerate(rotated_lanes):
            ledger.append(
                {
                    "arm": arm,
                    "seed": seed,
                    "raw_fields_json": json.dumps(
                        [AGGTRADES_SYSTEM_CANARY_FIELDS[0]]
                    ),
                    "matched_positive": False,
                    "operation": (
                        operations[batch_index % len(operations)]
                        if arm == "collision_controlled_evolution_v2_2"
                        else "CANONICAL_TYPED_RANDOM_SAMPLE"
                    ),
                    "receipt_verified": (
                        arm == "collision_controlled_evolution_v2_2"
                    ),
                    "balanced_batch_index": batch_index,
                    "balanced_batch_slot": slot,
                    "balanced_batch_size": 8,
                }
            )
    metrics = [
        {
            "checkpoint_index": 1,
            "arm": "canonical_typed_random",
            "matched_reward_comparison_count": 1_000,
            "strict_per_raw_attempt": 0.50,
            "balanced_valid_exact_unique_per_cpu_hour": 100.0,
            "new_behavior_families_per_cpu_hour": 100.0,
            "new_behavior_families_per_1k_evaluations": 1_000.0,
            "mean_pair_reward_at_matched_count": -1.0,
            "top_decile_pair_reward_at_matched_count": -0.5,
            "behavior_duplicate_rate": 0.0,
            "operator_update_count": 0,
            "operator_probabilities_json": "{}",
            "operator_productivity_json": "{}",
            "transition_productivity_json": "{}",
            "blocked_transition_count": 0,
            "blocked_transition_skips": 0,
        },
        {
            "checkpoint_index": 1,
            "arm": "collision_controlled_evolution_v2_2",
            "matched_reward_comparison_count": 1_000,
            "strict_per_raw_attempt": 0.63,
            "balanced_valid_exact_unique_per_cpu_hour": 101.0,
            "new_behavior_families_per_cpu_hour": 101.0,
            "new_behavior_families_per_1k_evaluations": 980.0,
            "mean_pair_reward_at_matched_count": -0.8,
            "top_decile_pair_reward_at_matched_count": -0.3,
            "behavior_duplicate_rate": 0.02,
            "operator_update_count": 1,
            "operator_probabilities_json": json.dumps(
                {operation: 1 / 3 for operation in operations}
            ),
            "operator_productivity_json": json.dumps({}),
            "transition_productivity_json": json.dumps(
                {"TRANSITION": {"trials": 1, "collisions": 1}}
            ),
            "blocked_transition_count": 1,
            "blocked_transition_skips": 2,
        },
    ]
    archive = BehaviorArchive(
        champion_by_family={
            f"family-{index}": index for index in range(1_980)
        }
    )
    decision = _v12_final_decision(
        source_sha="a" * 40,
        state={"generation_attempts": 3_800, "wall_elapsed_seconds": 12.0},
        ledger=ledger,
        archive=archive,
        metrics=metrics,
        runtime_root=tmp_path,
    )
    report = _v12_report_text(decision)
    assert decision["status"] == "PASS_SEARCH_ENGINE_V1_2_COMPLETED"
    assert decision["balanced_batch_integrity"] is True
    assert decision["rotating_submission_integrity"] is True
    assert all(decision["frozen_engineering_gate"].values())
    assert decision["future_new_data_arena_qualified_arms"] == []
    assert decision["promotion"] == "FORBIDDEN"
    assert "Future new-data Arena arms: `[]`" in report


def test_v12_rejects_an_alternate_runtime_identity(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="authorized only for runtime date"):
        run_engine(
            tmp_path,
            runtime_date="20260728",
            campaign="search_engine_v1_2",
        )
