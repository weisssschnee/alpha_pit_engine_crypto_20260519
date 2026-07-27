from __future__ import annotations

import json
import random
from collections import Counter

import pytest

from alphafactory_crypto.broad_search.compositional18m import (
    candidate_from_genes,
    generate_effective_candidate,
    generate_candidate,
    skeleton_registry,
)
from alphafactory_crypto.broad_search.expression import (
    FieldContract,
    TypedExpressionRegistry,
)
from alphafactory_crypto.broad_search.search_engine_v1 import (
    BehaviorArchive,
    HierarchicalTypedCEMV2,
    SEEDS,
    TypedEvolutionV2,
    _final_decision,
)


def _registry() -> TypedExpressionRegistry:
    return TypedExpressionRegistry(
        (
            FieldContract("open_interest_last_change_1h", "RETURN", "dimensionless"),
            FieldContract("open_interest_value_last", "NOTIONAL", "quote_asset"),
            FieldContract("trade_return_1h", "RETURN", "dimensionless"),
            FieldContract("trade_quote_volume", "NOTIONAL", "quote_asset"),
            FieldContract("mark_trade_basis_bps", "BPS", "bps"),
            FieldContract(
                "trade_close",
                "PRICE",
                "quote_per_base",
                pit_authority="CURRENT_FIELD_SURFACE_BINDING",
            ),
            FieldContract(
                "top_long_short_account_ratio_last", "RATIO", "dimensionless"
            ),
            FieldContract(
                "global_long_short_account_ratio_last", "RATIO", "dimensionless"
            ),
            FieldContract(
                "top_long_short_position_ratio_last", "RATIO", "dimensionless"
            ),
            FieldContract("account_position_divergence", "RATIO", "dimensionless"),
            FieldContract("listing_age_days", "AGE", "days"),
            FieldContract("active_universe_size", "STATE", "assets"),
        )
    )


def _cem_row(candidate, reward: float, local_count: int = 1) -> dict:
    return {
        "pair_reward": reward,
        "policy_local_family_count_at_completion": local_count,
        "candidate_id": candidate.candidate_id,
        "candidate_spec_json": json.dumps(candidate.to_dict(), sort_keys=True),
    }


def test_cem_checkpoint_update_does_not_double_count_prior_elites() -> None:
    registry = _registry()
    parameters = {
        "elite_fraction": 1.0,
        "smoothing": 0.35,
        "minimum_probability": 0.002,
        "entropy_floor_ratio": 0.0,
        "minimum_observation_count": 1,
        "count_pseudocount": 0.50,
        "duplicate_resample_limit": 64,
    }
    policy = HierarchicalTypedCEMV2(7, registry, parameters)
    first = generate_candidate(
        registry, skeleton=skeleton_registry()[0], rng=random.Random(1)
    )
    second = generate_candidate(
        registry, skeleton=skeleton_registry()[5], rng=random.Random(2)
    )
    policy.update([_cem_row(first, 1.0)])
    prior = dict(policy.tables["mechanism_family"]["G"]["probabilities"])
    policy.update([_cem_row(second, 1.0)])

    values = tuple(
        sorted(
            {
                first.mechanism_family,
                second.mechanism_family,
            }
        )
    )
    current = Counter({second.mechanism_family: 1})
    empirical = {
        value: (current[value] + 0.5) / (1 + 0.5 * len(values))
        for value in values
    }
    blended = {
        value: 0.65 * prior.get(value, 1.0 / len(values))
        + 0.35 * empirical[value]
        for value in values
    }
    expected = policy._regularized(values, blended)
    assert policy.tables["mechanism_family"]["G"]["probabilities"] == pytest.approx(
        expected
    )
    assert policy.tables["mechanism_family"]["G"]["counts"] == {
        first.mechanism_family: 1,
        second.mechanism_family: 1,
    }


def test_evolution_next_proposal_is_invariant_to_other_arm_history() -> None:
    registry = _registry()
    parameters = {
        **TypedEvolutionV2(1, registry).parameters,
        "warmup": 2,
    }
    policy = TypedEvolutionV2(11, registry, parameters)
    for index, skeleton in enumerate(skeleton_registry()[:2]):
        candidate = generate_candidate(
            registry, skeleton=skeleton, rng=random.Random(100 + index)
        )
        policy.observe(
            candidate,
            {
                "behavior_family_id": f"family-{index}",
                "pair_reward": float(index),
                "operation": "TYPED_RANDOM_WARMUP",
                "parent_ids": [],
            },
        )
    first = TypedEvolutionV2.from_state(registry, policy.export_state())
    second = TypedEvolutionV2.from_state(registry, policy.export_state())
    quiet_archive = BehaviorArchive()
    noisy_archive = BehaviorArchive()
    noisy_archive.family_counts.update({"family-0": 10_000, "family-x": 50_000})
    left, _ = first.propose(quiet_archive)
    right, _ = second.propose(noisy_archive)
    assert left.candidate_id == right.candidate_id


def test_semantically_invalid_normalizer_is_rejected() -> None:
    registry = _registry()
    skeleton = next(
        item
        for item in skeleton_registry()
        if item.mechanism_family == "CROSS_ASSET_RELATIVE_STATE"
    )
    candidate = generate_candidate(registry, skeleton=skeleton, rng=random.Random(4))
    genes = dict(candidate.generation_genes)
    genes["left_field"] = "trade_close"
    genes["left_normalizer"] = "VolatilityScale"
    with pytest.raises(ValueError, match="field-family representation"):
        candidate_from_genes(registry, skeleton=skeleton, genes=genes)


def test_ineffective_genes_are_not_sampled_or_counted() -> None:
    registry = _registry()
    non_residual = next(
        item
        for item in skeleton_registry()
        if item.to_dict()["operator_DAG"] != "Residual"
    )
    for seed in range(20):
        candidate = generate_effective_candidate(
            registry, skeleton=non_residual, rng=random.Random(seed)
        )
        assert candidate.generation_genes["beta"] == 0.5

    first = generate_candidate(
        registry, skeleton=skeleton_registry()[0], rng=random.Random(101)
    )
    second = generate_candidate(
        registry, skeleton=skeleton_registry()[1], rng=random.Random(202)
    )
    policy = TypedEvolutionV2(20260721, registry)
    _, receipt = policy._crossover(first, second)
    assert "beta" not in receipt["gene_order"]


def test_lineage_collapse_metrics_are_persisted() -> None:
    registry = _registry()
    policy = TypedEvolutionV2(
        12,
        registry,
        {
            **TypedEvolutionV2(12, registry).parameters,
            "warmup": 1,
            "population_limit": 8,
            "mechanism_cell_limit": 2,
        },
    )
    root = generate_candidate(
        registry, skeleton=skeleton_registry()[0], rng=random.Random(301)
    )
    policy.observe(
        root,
        {
            "behavior_family_id": "root-family",
            "pair_reward": 1.0,
            "operation": "TYPED_RANDOM_WARMUP",
            "parent_ids": [],
        },
    )
    child, receipt = policy._mutate_genes(root)
    policy.observe(
        child,
        {
            "behavior_family_id": "child-family",
            "pair_reward": 2.0,
            "operation": receipt["operation"],
            "parent_ids": [root.candidate_id],
        },
    )
    diagnostics = policy.population_diagnostics()
    assert diagnostics["effective_parent_count"] == 2
    assert diagnostics["top_root_lineage_share"] == pytest.approx(1.0)
    assert diagnostics["mechanism_occupancy"] == {"OI_PRICE_DIVERGENCE": 2}
    restored = TypedEvolutionV2.from_state(registry, policy.export_state())
    assert restored.population_diagnostics() == diagnostics


def test_arm_cannot_qualify_on_compute_density_alone(tmp_path) -> None:
    for checkpoint_index in range(10):
        checkpoint = tmp_path / "checkpoints" / f"checkpoint_{checkpoint_index:03d}"
        checkpoint.mkdir(parents=True)
        (checkpoint / "manifest.json").write_text(
            json.dumps({"restore_verified": True}), encoding="utf-8"
        )
    metrics = []
    for checkpoint_index in range(10):
        metrics.extend(
            (
                {
                    "checkpoint_index": checkpoint_index,
                    "arm": "canonical_typed_random",
                    "valid_exact_unique_per_cpu_hour": 100.0,
                    "new_behavior_families_per_1k_evaluations": 800.0,
                    "mean_pair_reward_at_matched_count": 0.0,
                    "top_decile_pair_reward_at_matched_count": 1.0,
                    "behavior_duplicate_rate": 0.10,
                },
                {
                    "checkpoint_index": checkpoint_index,
                    "arm": "hierarchical_typed_cem_v2",
                    "valid_exact_unique_per_cpu_hour": 101.0,
                    "new_behavior_families_per_1k_evaluations": 700.0,
                    "mean_pair_reward_at_matched_count": -0.1,
                    "top_decile_pair_reward_at_matched_count": 0.9,
                    "behavior_duplicate_rate": 0.10,
                },
            )
        )
    ledger = []
    for seed in SEEDS:
        ledger.extend(
            (
                {
                    "arm": "canonical_typed_random",
                    "seed": seed,
                    "arm_completion_ordinal": 1,
                    "pair_reward": 0.0,
                    "family_member_count_at_completion": 1,
                },
                {
                    "arm": "hierarchical_typed_cem_v2",
                    "seed": seed,
                    "arm_completion_ordinal": 1,
                    "pair_reward": -0.1,
                    "family_member_count_at_completion": 1,
                },
            )
        )
    decision = _final_decision(
        source_sha="a" * 40,
        state={
            "arm_states": {
                "hierarchical_typed_cem_v2": "ACTIVE",
                "typed_evolution_v2": "EXITED",
            },
            "generation_attempts": len(ledger),
            "wall_elapsed_seconds": 1.0,
        },
        ledger=ledger,
        archive=BehaviorArchive(),
        metrics=metrics,
        runtime_root=tmp_path,
    )
    assert "hierarchical_typed_cem_v2" not in decision[
        "future_new_data_arena_qualified_arms"
    ]
    assert not decision["search_strategy_qualification_evidence"][
        "hierarchical_typed_cem_v2"
    ]["checkpoint_gates"][-1]["reward_not_worse"]
