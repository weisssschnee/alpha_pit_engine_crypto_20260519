from __future__ import annotations

import json
import random
from collections import Counter
from pathlib import Path

import pandas as pd
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
    ECONOMIC_SEARCH_V2_CAMPAIGN,
    HierarchicalTypedCEMV2,
    SEEDS,
    TypedEvolutionV2,
    _budget_exhausted_decision,
    _budget_exhausted_report_text,
    _economic_campaign_config,
    _final_decision,
    _initial_policies,
    _proposal_liveness_preflight,
    _search_ordering_reward,
    _validation_blocked_decision,
    _validation_blocked_report_text,
)
from alphafactory_crypto.broad_search.pair18m import SEARCH_REWARD_AUTHORITY


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
        "search_reward": reward,
        "search_reward_authority": SEARCH_REWARD_AUTHORITY,
        "pair_reward": reward,
        "policy_local_family_count_at_completion": local_count,
        "candidate_id": candidate.candidate_id,
        "candidate_spec_json": json.dumps(candidate.to_dict(), sort_keys=True),
    }


def test_frozen_v1_controls_reuse_partial_carrier_role_surface() -> None:
    registry = TypedExpressionRegistry(
        (
            FieldContract(
                "bybit__mark_price_last", "PRICE", "quote_per_base"
            ),
            FieldContract(
                "bybit__funding_rate_last", "RETURN", "dimensionless"
            ),
            FieldContract(
                "signed_aggressor_notional", "NOTIONAL", "quote_asset"
            ),
        )
    )
    policies = _initial_policies(
        registry,
        arms=("cem_distribution_v1", "evolutionary_typed_v1"),
        seeds=(20260716,),
    )

    for policy in policies.values():
        candidate, _ = policy.propose()
        assert candidate.raw_fields
        assert set(candidate.raw_fields).issubset(registry.fields)


def test_all_policy_lanes_pass_zero_market_proposal_liveness_preflight() -> None:
    registry = TypedExpressionRegistry(
        (
            FieldContract(
                "bybit__mark_price_last", "PRICE", "quote_per_base"
            ),
            FieldContract(
                "bybit__funding_rate_last", "RETURN", "dimensionless"
            ),
            FieldContract(
                "signed_aggressor_notional", "NOTIONAL", "quote_asset"
            ),
        )
    )
    result = _proposal_liveness_preflight(
        registry,
        arms=(
            "canonical_typed_random",
            "cem_distribution_v1",
            "evolutionary_typed_v1",
            "hierarchical_typed_cem_v2",
            "typed_evolution_v2",
        ),
        seeds=SEEDS,
    )

    assert result["status"] == "PASS"
    assert result["lane_count_expected"] == 5 * len(SEEDS)
    assert result["lane_count_passed"] == result["lane_count_expected"]
    assert result["market_evaluations"] == 0
    assert result["reward_reads"] == 0
    assert all(row["matched_control_constructible"] for row in result["records"])
    assert all(row["deterministic_replay_verified"] for row in result["records"])


def test_v2_campaign_uses_independent_runtime_and_receipt() -> None:
    config = _economic_campaign_config(ECONOMIC_SEARCH_V2_CAMPAIGN)

    assert config == {
        "epoch_id": "CRYPTO_SEARCH_ECONOMIC_V2_20260731",
        "runtime_date": "20260731",
        "runtime_prefix": "crypto_search_economic_v2",
        "report_prefix": "CRYPTO_SEARCH_ECONOMIC_V2",
        "report_title": "Crypto Search Economic V2",
        "receipt_path": "config/crypto_search_economic_receipt_v2.json",
        "cli_suffix": "economic-v2",
    }


def test_proposal_liveness_preflight_fails_closed_on_unexpected_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_proposal(*_args, **_kwargs):
        raise ValueError("deterministic role resolver defect")

    monkeypatch.setattr(
        "alphafactory_crypto.broad_search.search_engine_v1._policy_propose",
        fail_proposal,
    )
    with pytest.raises(RuntimeError, match="PROPOSAL_LIVENESS_PREFLIGHT_FAILED"):
        _proposal_liveness_preflight(
            _registry(),
            arms=("canonical_typed_random",),
            seeds=(SEEDS[0],),
        )


def test_budget_exhausted_closure_preserves_partial_evidence_boundaries() -> None:
    rows = pd.DataFrame(
        (
            {
                "arm": "canonical_typed_random",
                "search_reward": 0.1,
                "pair_reward": -1.0,
                "behavior_family_id": "family-a",
                "operation": "CANONICAL_TYPED_RANDOM_SAMPLE",
                "matched_positive": False,
                "cost_killed": True,
                "turnover_killed": False,
            },
            {
                "arm": "typed_evolution_v2",
                "search_reward": 0.2,
                "pair_reward": -0.5,
                "behavior_family_id": "family-a",
                "operation": "EFFECTIVE_GENE_MUTATION_1_TO_3",
                "matched_positive": False,
                "cost_killed": False,
                "turnover_killed": False,
            },
        )
    )
    state = {
        "archive_duplicate_replacements": 1,
        "failure_counts": {
            "cem_distribution_v1:PROPOSAL_ValueError": 10,
        },
        "arm_counters": {
            "canonical_typed_random": {
                "generation_attempts": 1,
                "compile_valid": 1,
                "exact_unique": 1,
                "matched_control_valid": 1,
                "strict_evaluated": 1,
                "cpu_seconds": 1.0,
            },
            "typed_evolution_v2": {
                "generation_attempts": 1,
                "compile_valid": 1,
                "exact_unique": 1,
                "matched_control_valid": 1,
                "strict_evaluated": 1,
                "cpu_seconds": 1.0,
            },
        },
    }
    decision = _budget_exhausted_decision(
        decision={
            "status": "ENGINE_BUDGET_EXHAUSTED",
            "reason": "RAW_GENERATION_ATTEMPT_LIMIT",
            "generation_attempts": 12,
            "active_wall_seconds": 3.0,
            "checkpoint": "checkpoint_budget_exhausted",
        },
        source_sha="a" * 40,
        state=state,
        ledger=rows,
        archive=rows,
        checkpoint_restore_verified=True,
        closure_source_sha="b" * 40,
    )
    report = _budget_exhausted_report_text(decision)

    assert decision["strict_evaluated_count"] == 2
    assert decision["future_new_data_arena_qualified_arms"] == []
    assert decision["next_arena_started"] is False
    assert decision["positive_pair_reward_count"] == 0
    assert decision["research_decision"] == "HOLD_INCOMPLETE_IMBALANCED_CAMPAIGN"
    assert "layer defect" in report
    assert "No seed, parameter, or rescue rerun was used." in report


def test_validation_blocked_decision_preserves_checkpoint_without_research_claim() -> None:
    archive = BehaviorArchive()
    decision = _validation_blocked_decision(
        source_sha="a" * 40,
        closure_source_sha="b" * 40,
        state={"generation_attempts": 2_280, "next_checkpoint_index": 1},
        ledger=({"candidate_id": "candidate-1"},),
        archive=archive,
        checkpoint=Path("checkpoint_000"),
        failure={
            "reason": "CONTROL_BEHAVIOR_EQUALS_PRIMARY",
            "arm": "canonical_typed_random",
            "candidate_id": "candidate-1",
            "horizon_hours": 1,
            "selection_rank": 1,
        },
        campaign=ECONOMIC_SEARCH_V2_CAMPAIGN,
    )
    report = _validation_blocked_report_text(decision)

    assert decision["status"] == "ENGINE_VALIDATION_BLOCKED"
    assert decision["research_decision"] == "HOLD_ENGINE_VALIDATION_BLOCKED"
    assert decision["future_new_data_arena_qualified_arms"] == []
    assert decision["alpha_claim"] is False
    assert decision["rescue_rerun_started"] is False
    assert decision["sealed_reads"] == 0
    assert "not an Alpha or" in report
    assert "No adaptive continuation" in report


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


def test_search_reward_not_pair_reward_orders_all_adaptive_state() -> None:
    registry = _registry()
    first = generate_candidate(
        registry, skeleton=skeleton_registry()[0], rng=random.Random(901)
    )
    second = generate_candidate(
        registry, skeleton=skeleton_registry()[1], rng=random.Random(902)
    )
    rows = (
        {
            **_cem_row(first, 10.0),
            "search_reward": -1.0,
            "behavior_family_id": "family-first",
        },
        {
            **_cem_row(second, -10.0),
            "search_reward": 1.0,
            "behavior_family_id": "family-second",
        },
    )
    cem = HierarchicalTypedCEMV2(
        7,
        registry,
        {
            **HierarchicalTypedCEMV2(7, registry).parameters,
            "elite_fraction": 0.5,
        },
    )
    assert cem._select_elites(rows)[0]["candidate_id"] == second.candidate_id

    evolution = TypedEvolutionV2(
        11,
        registry,
        {
            **TypedEvolutionV2(11, registry).parameters,
            "warmup": 1,
            "tournament_size": 2,
        },
    )
    for candidate, row in zip((first, second), rows, strict=True):
        evolution.observe(
            candidate,
            {
                **row,
                "operation": "TYPED_RANDOM_WARMUP",
                "parent_ids": [],
            },
        )
    assert evolution._parent().candidate_id == second.candidate_id

    archive = BehaviorArchive()
    for ordinal, (candidate, row) in enumerate(
        zip((first, second), rows, strict=True),
        start=1,
    ):
        archive.observe(
            candidate=candidate,
            evaluation={
                "search_reward": row["search_reward"],
                "search_reward_authority": SEARCH_REWARD_AUTHORITY,
                "pair_reward": row["pair_reward"],
                "matched_positive": False,
                "incremental": {
                    "gross_mean": 0.0,
                    "net_mean": 0.0,
                    "cost_mean": 0.0,
                },
                "behavior": {"behavior_family_id": "shared-family"},
            },
            arm="test",
            seed=1,
            completion_ordinal=ordinal,
            checkpoint_index=0,
        )
    champion = archive.rows[archive.champion_by_family["shared-family"]]
    assert champion["exact_expression_id"] == second.candidate_id
    assert champion["search_reward"] == 1.0
    assert champion["pair_reward"] == -10.0


def test_legacy_primary_only_reward_authority_cannot_seed_fresh_search() -> None:
    with pytest.raises(ValueError, match="legacy reward state cannot seed"):
        _search_ordering_reward(
            {
                "search_reward": 1.0,
                "search_reward_authority": (
                    "PHASE3CM_STYLE_TRAIN_PORTFOLIO_SORTINO_V1"
                ),
            }
        )


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
                    "search_reward": float(index),
                    "search_reward_authority": SEARCH_REWARD_AUTHORITY,
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
            "search_reward": 1.0,
            "search_reward_authority": SEARCH_REWARD_AUTHORITY,
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
            "search_reward": 2.0,
            "search_reward_authority": SEARCH_REWARD_AUTHORITY,
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
                    "mean_search_reward_at_matched_count": 0.0,
                    "top_decile_search_reward_at_matched_count": 1.0,
                    "mean_pair_reward_at_matched_count": 0.0,
                    "top_decile_pair_reward_at_matched_count": 1.0,
                    "behavior_duplicate_rate": 0.10,
                },
                {
                    "checkpoint_index": checkpoint_index,
                    "arm": "hierarchical_typed_cem_v2",
                    "valid_exact_unique_per_cpu_hour": 101.0,
                    "new_behavior_families_per_1k_evaluations": 700.0,
                    "mean_search_reward_at_matched_count": -0.1,
                    "top_decile_search_reward_at_matched_count": 0.9,
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
                        "search_reward": 0.0,
                        "pair_reward": 0.0,
                    "family_member_count_at_completion": 1,
                },
                {
                    "arm": "hierarchical_typed_cem_v2",
                    "seed": seed,
                        "arm_completion_ordinal": 1,
                        "search_reward": -0.1,
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
