from __future__ import annotations

import json
import random
from pathlib import Path

import pytest

from alphafactory_crypto.broad_search.compositional18m import (
    generate_candidate,
    skeleton_registry,
)
from alphafactory_crypto.broad_search.expression import (
    FieldContract,
    TypedExpressionRegistry,
)
from alphafactory_crypto.broad_search.search_engine_v1 import (
    AGGTRADES_SYSTEM_CANARY_FIELDS,
    V11_ARMS,
    V11_DEFAULT_RUNTIME_DATE,
    V21_PARAMETERS,
    BehaviorArchive,
    HierarchicalTypedCEMV2,
    TypedEvolutionV2,
    _initial_policies,
    _v11_final_decision,
    _v11_report_text,
    _validate_v11_config,
    run_engine,
)
from alphafactory_crypto.broad_search.pair18m import SEARCH_REWARD_AUTHORITY


def _registry() -> TypedExpressionRegistry:
    return TypedExpressionRegistry(
        (
            FieldContract(
                "open_interest_last_change_1h",
                "RETURN",
                "dimensionless",
            ),
            FieldContract(
                "open_interest_value_last",
                "NOTIONAL",
                "quote_asset",
            ),
            FieldContract("trade_return_1h", "RETURN", "dimensionless"),
            FieldContract(
                "trade_quote_volume",
                "NOTIONAL",
                "quote_asset",
            ),
            FieldContract("mark_trade_basis_bps", "BPS", "bps"),
            FieldContract(
                "trade_close",
                "PRICE",
                "quote_per_base",
                pit_authority="CURRENT_FIELD_SURFACE_BINDING",
            ),
            FieldContract(
                "top_long_short_account_ratio_last",
                "RATIO",
                "dimensionless",
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
                "account_position_divergence",
                "RATIO",
                "dimensionless",
            ),
            FieldContract("listing_age_days", "AGE", "days"),
            FieldContract("active_universe_size", "STATE", "assets"),
        )
    )


def _cem_row(
    candidate,
    *,
    reward: float,
    family_id: str,
) -> dict:
    return {
        "search_reward": reward,
        "search_reward_authority": SEARCH_REWARD_AUTHORITY,
        "pair_reward": reward,
        "policy_local_family_count_at_completion": 1,
        "candidate_id": candidate.candidate_id,
        "candidate_spec_json": json.dumps(candidate.to_dict(), sort_keys=True),
        "behavior_family_id": family_id,
    }


def test_v11_profile_is_equal_count_fresh_state_system_search() -> None:
    root = Path(__file__).resolve().parents[1]
    config = json.loads(
        (root / "config/crypto_search_engine_v1_1.json").read_text(
            encoding="utf-8"
        )
    )
    _validate_v11_config(config)
    assert tuple(config["search"]["arms_per_checkpoint"]) == V11_ARMS
    assert set(config["search"]["arms_per_checkpoint"].values()) == {500}
    assert config["search"]["strict_evaluated_target"] == 3_000
    assert config["search"]["checkpoint_count"] == 2
    assert config["boundaries"]["system_behavior_only"] is True
    assert config["boundaries"]["future_arm_qualification"] is False
    policies = _initial_policies(_registry(), arms=V11_ARMS)
    assert len(policies) == len(V11_ARMS) * 4
    assert all(
        policy.parameters.get("behavior_family_champion_elites") is True
        for key, policy in policies.items()
        if key.startswith("behavior_niched_cem_v2_1|")
    )
    assert all(
        policy.parameters.get("operator_productivity_adaptation") is True
        for key, policy in policies.items()
        if key.startswith("behavior_niched_evolution_v2_1|")
    )


def test_behavior_niched_cem_elites_are_family_unique_and_skeleton_stratified() -> None:
    registry = _registry()
    parameters = {
        **V21_PARAMETERS["behavior_niched_cem_v2_1"],
        "elite_fraction": 0.60,
        "minimum_observation_count": 1,
        "entropy_floor_ratio": 0.0,
    }
    policy = HierarchicalTypedCEMV2(7, registry, parameters)
    skeletons = skeleton_registry()
    first = generate_candidate(
        registry, skeleton=skeletons[0], rng=random.Random(11)
    )
    duplicate_family = generate_candidate(
        registry, skeleton=skeletons[0], rng=random.Random(12)
    )
    second = generate_candidate(
        registry, skeleton=skeletons[1], rng=random.Random(13)
    )
    same_mechanism_frontier = generate_candidate(
        registry, skeleton=skeletons[2], rng=random.Random(15)
    )
    third = generate_candidate(
        registry, skeleton=skeletons[5], rng=random.Random(14)
    )
    elites = policy._select_elites(
        (
            _cem_row(first, reward=4.0, family_id="family-a"),
            _cem_row(
                duplicate_family,
                reward=3.0,
                family_id="family-a",
            ),
            _cem_row(
                same_mechanism_frontier,
                reward=3.0,
                family_id="family-d",
            ),
            _cem_row(second, reward=2.0, family_id="family-b"),
            _cem_row(third, reward=1.0, family_id="family-c"),
        )
    )
    assert [row["behavior_family_id"] for row in elites] == [
        "family-a",
        "family-d",
        "family-c",
    ]
    assert len(
        {
            json.loads(row["candidate_spec_json"])["skeleton_id"]
            for row in elites
        }
    ) == 3
    assert len(
        {
            json.loads(row["candidate_spec_json"])["mechanism_family"]
            for row in elites
        }
    ) == 2
    assert policy.last_elite_mechanism_count == 2


def test_cem_failed_proposal_reports_every_raw_attempt() -> None:
    registry = _registry()
    parameters = {
        **V21_PARAMETERS["behavior_niched_cem_v2_1"],
        "duplicate_resample_limit": 2,
    }
    preview = HierarchicalTypedCEMV2(31, registry, parameters)
    attempted = {preview._sample_candidate().candidate_id for _ in range(3)}
    policy = HierarchicalTypedCEMV2(31, registry, parameters)
    policy.seen.update(attempted)
    with pytest.raises(RuntimeError) as caught:
        policy.propose()
    assert getattr(caught.value, "raw_attempts") == 3


def test_behavior_niched_evolution_adapts_only_from_family_productivity() -> None:
    registry = _registry()
    policy = TypedEvolutionV2(
        19,
        registry,
        V21_PARAMETERS["behavior_niched_evolution_v2_1"],
    )
    rows = []
    rows.extend(
        {
            "operation": "EFFECTIVE_GENE_MUTATION_1_TO_3",
            "new_policy_local_behavior_family_at_completion": False,
        }
        for _ in range(10)
    )
    rows.extend(
        {
            "operation": "COMPATIBLE_SKELETON_VARIANT_MUTATION",
            "new_policy_local_behavior_family_at_completion": True,
        }
        for _ in range(10)
    )
    rows.extend(
        {
            "operation": "ONE_POINT_HOMOLOGOUS_GENE_BUNDLE_CROSSOVER",
            "new_policy_local_behavior_family_at_completion": index < 5,
        }
        for index in range(10)
    )
    policy.update_operator_productivity(rows)
    probabilities = policy.operation_probabilities
    assert probabilities["COMPATIBLE_SKELETON_VARIANT_MUTATION"] > (
        probabilities["ONE_POINT_HOMOLOGOUS_GENE_BUNDLE_CROSSOVER"]
    )
    assert probabilities["ONE_POINT_HOMOLOGOUS_GENE_BUNDLE_CROSSOVER"] > (
        probabilities["EFFECTIVE_GENE_MUTATION_1_TO_3"]
    )
    assert sum(probabilities.values()) == pytest.approx(1.0)
    assert min(probabilities.values()) >= 0.15 - 1.0e-12
    policy.update_operator_productivity(
        [
            {
                "operation": "EFFECTIVE_GENE_MUTATION_1_TO_3",
                "new_policy_local_behavior_family_at_completion": True,
            }
            for _ in range(10)
        ]
    )
    assert policy.operator_productivity[
        "COMPATIBLE_SKELETON_VARIANT_MUTATION"
    ]["trials"] == 0
    assert policy.operation_probabilities[
        "EFFECTIVE_GENE_MUTATION_1_TO_3"
    ] > policy.operation_probabilities[
        "COMPATIBLE_SKELETON_VARIANT_MUTATION"
    ]
    restored = TypedEvolutionV2.from_state(registry, policy.export_state())
    assert restored.export_state() == policy.export_state()


def test_behavior_niched_evolution_population_has_family_and_skeleton_caps() -> None:
    registry = _registry()
    parameters = {
        **V21_PARAMETERS["behavior_niched_evolution_v2_1"],
        "population_limit": 8,
        "mechanism_cell_limit": 8,
        "skeleton_cell_limit": 1,
        "warmup": 1,
    }
    policy = TypedEvolutionV2(29, registry, parameters)
    for index, skeleton in enumerate(skeleton_registry()[:4]):
        for repeat in range(2):
            candidate = generate_candidate(
                registry,
                skeleton=skeleton,
                rng=random.Random(1_000 + index * 10 + repeat),
            )
            policy.observe(
                candidate,
                {
                    "behavior_family_id": f"family-{index}-{repeat}",
                    "search_reward": float(repeat),
                    "search_reward_authority": SEARCH_REWARD_AUTHORITY,
                    "pair_reward": float(repeat),
                    "operation": "TYPED_RANDOM_WARMUP",
                    "parent_ids": [],
                },
            )
    diagnostics = policy.population_diagnostics()
    assert diagnostics["duplicate_family_slots"] == 0
    assert max(diagnostics["skeleton_occupancy"].values()) == 1


def test_v11_final_decision_remains_system_only(
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
    for arm in V11_ARMS:
        ledger.extend(
            {
                "arm": arm,
                "raw_fields_json": json.dumps(
                    [AGGTRADES_SYSTEM_CANARY_FIELDS[0]]
                ),
                "matched_positive": False,
                "operation": "EFFECTIVE_GENE_MUTATION_1_TO_3",
                "receipt_verified": True,
            }
            for _ in range(1_000)
        )
    metrics = []
    for arm in V11_ARMS:
        metrics.append(
            {
                "checkpoint_index": 1,
                "arm": arm,
                "matched_reward_comparison_count": 1_000,
                "valid_exact_unique_per_cpu_hour": 100.0,
                "new_behavior_families_per_1k_evaluations": 900.0,
                "mean_search_reward_at_matched_count": -0.01,
                "top_decile_search_reward_at_matched_count": 0.01,
                "mean_pair_reward_at_matched_count": -0.01,
                "top_decile_pair_reward_at_matched_count": 0.01,
                "behavior_duplicate_rate": 0.04,
                "operator_update_count": (
                    1 if arm == "behavior_niched_evolution_v2_1" else 0
                ),
                "operator_probabilities_json": json.dumps(
                    {"EFFECTIVE_GENE_MUTATION_1_TO_3": 1.0}
                ),
                "operator_productivity_json": json.dumps({}),
            }
        )
    archive = BehaviorArchive(
        champion_by_family={f"family-{index}": index for index in range(2_900)}
    )
    decision = _v11_final_decision(
        source_sha="a" * 40,
        state={"generation_attempts": 3_500, "wall_elapsed_seconds": 12.0},
        ledger=ledger,
        archive=archive,
        metrics=metrics,
        runtime_root=tmp_path,
    )
    report = _v11_report_text(decision)
    assert decision["status"] == "PASS_SEARCH_ENGINE_V1_1_COMPLETED"
    assert decision["future_new_data_arena_qualified_arms"] == []
    assert decision["promotion"] == "FORBIDDEN"
    assert decision["next_arena_started"] is False
    assert "Future new-data Arena arms: `[]`" in report
    assert "evaluates search capability only" in report
    exhausted = _v11_final_decision(
        source_sha="a" * 40,
        state={
            "generation_attempts": 3_500,
            "wall_elapsed_seconds": 14_401.0,
        },
        ledger=ledger,
        archive=archive,
        metrics=metrics,
        runtime_root=tmp_path,
    )
    assert exhausted["status"] == "ENGINE_BUDGET_EXHAUSTED"


def test_v11_rejects_an_alternate_runtime_identity(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="authorized only for runtime date"):
        run_engine(
            tmp_path,
            runtime_date="20260728",
            campaign="search_engine_v1_1",
        )


def test_v11_direct_runner_requires_economic_preflight(tmp_path: Path) -> None:
    with pytest.raises(
        RuntimeError,
        match="ECONOMIC_RECEIPT_PREFLIGHT_REQUIRED",
    ):
        run_engine(
            tmp_path,
            runtime_date=V11_DEFAULT_RUNTIME_DATE,
            campaign="search_engine_v1_1",
        )
