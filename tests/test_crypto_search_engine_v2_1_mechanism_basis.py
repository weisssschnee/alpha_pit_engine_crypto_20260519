from __future__ import annotations

import json
import random
from pathlib import Path

import numpy as np

from alphafactory_crypto.broad_search.compositional18m import (
    compile_mechanism_catalog,
    mechanism_candidate_from_genes,
    mechanism_role_domains,
    sample_mechanism_candidate,
)
from alphafactory_crypto.broad_search.expression import (
    Expression,
    FieldContract,
    TypedExpressionRegistry,
    materialize_expression,
)
from alphafactory_crypto.broad_search.experiment_authority import (
    resolve_search_economic_receipt,
)
from alphafactory_crypto.broad_search.search_engine_v1 import (
    MECHANISM_SEARCH_V21_ARMS,
    MECHANISM_SEARCH_V21_CAMPAIGN,
    MECHANISM_SEARCH_V21_SEEDS,
    MechanismEvolutionV2,
    MechanismRandomV2,
    _economic_campaign_seeds,
    _load_mechanism_v21_contract,
    _mechanism_v21_checkpoint_allocation,
    _mechanism_v21_train_gate,
    _policy_inflight_limit,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def _contracts() -> tuple[FieldContract, ...]:
    rows = json.loads(
        (
            REPO_ROOT
            / "runtime/crypto_search_engine_v1_4_oi_flow_20260728/"
            "aligned_carrier_manifest.json"
        ).read_text(encoding="utf-8")
    )["contracts"]
    return tuple(
        FieldContract(
            str(row["field_id"]),
            str(row["value_type"]),
            str(row["unit"]),
            int(row["observable_lag_hours"]),
            str(row["pit_authority"]),
        )
        for row in rows
    )


def test_v21_catalog_is_a_strict_existing_ast_expansion() -> None:
    config, legacy, expanded, knowledge = _load_mechanism_v21_contract(REPO_ROOT)
    assert len(legacy) == 184
    assert len(expanded) == 786
    assert {item.mechanism_id for item in legacy}.issubset(
        {item.mechanism_id for item in expanded}
    )
    assert {item.payload_mode for item in expanded if item.payload_mode} == {
        "SIGN_CONFIRMATION",
        "SIGN_DISAGREEMENT",
    }
    assert {item.condition_mode for item in expanded if item.condition_mode} == {
        "NEGATIVE",
        "ABSOLUTE_MAGNITUDE",
        "POSITIVE_MAGNITUDE",
        "NEGATIVE_MAGNITUDE",
        "SIGN_ROUTING",
    }
    assert config["search"]["strict_evaluated_target"] == 10_000
    assert knowledge["usage_contract"]["sampling_probability_prior"] is False
    assert knowledge["usage_contract"]["candidate_or_reward_import"] is False


def test_gate_and_modulation_modes_have_frozen_numeric_semantics() -> None:
    fields = (
        FieldContract("left", "RATIO", "dimensionless"),
        FieldContract("right", "RATIO", "dimensionless"),
    )
    registry = TypedExpressionRegistry(fields)
    left = np.array([[-2.0, -1.0, 1.0, 2.0]])
    right = np.array([[-1.0, 1.0, -1.0, 2.0]])
    reader = {"left": left, "right": right}.__getitem__

    confirmation = Expression(
        "ConditionGate",
        (Expression.raw("left"), Expression.raw("right")),
        parameters={"threshold": 0.0, "mode": "SIGN_CONFIRMATION"},
    )
    disagreement = Expression(
        "ConditionGate",
        (Expression.raw("left"), Expression.raw("right")),
        parameters={"threshold": 0.0, "mode": "SIGN_DISAGREEMENT"},
    )
    negative = Expression(
        "ConditionGate",
        (Expression.raw("left"), Expression.raw("right")),
        parameters={"threshold": 0.0, "mode": "NEGATIVE"},
    )
    magnitude = Expression(
        "StateModulation",
        (Expression.raw("left"), Expression.raw("right")),
        parameters={"mode": "ABSOLUTE_MAGNITUDE"},
    )
    routing = Expression(
        "StateModulation",
        (Expression.raw("left"), Expression.raw("right")),
        parameters={"mode": "SIGN_ROUTING"},
    )
    assert materialize_expression(
        confirmation, registry=registry, field_reader=reader
    ).tolist() == [[-2.0, 0.0, 0.0, 2.0]]
    assert materialize_expression(
        disagreement, registry=registry, field_reader=reader
    ).tolist() == [[0.0, -1.0, 1.0, 0.0]]
    assert materialize_expression(
        negative, registry=registry, field_reader=reader
    ).tolist() == [[-2.0, 0.0, 1.0, 0.0]]
    assert materialize_expression(
        magnitude, registry=registry, field_reader=reader
    ).tolist() == [[-2.0, -1.0, 1.0, 4.0]]
    assert materialize_expression(
        routing, registry=registry, field_reader=reader
    ).tolist() == [[2.0, -1.0, -1.0, 2.0]]


def test_nested_confirmation_and_regime_gate_replay_through_existing_genome() -> None:
    registry = TypedExpressionRegistry(_contracts())
    _, _, catalog, _ = _load_mechanism_v21_contract(REPO_ROOT)
    spec = next(
        item
        for item in catalog
        if item.payload_mode == "SIGN_CONFIRMATION"
        and item.condition_mode == "NEGATIVE"
    )
    candidate = sample_mechanism_candidate(
        registry=registry,
        spec=spec,
        domains=mechanism_role_domains(tuple(registry.fields.values())),
        rng=random.Random(2021),
    )
    assurance = registry.validate(candidate.expression)
    replay = mechanism_candidate_from_genes(
        registry,
        genes=candidate.generation_genes,
        domains=mechanism_role_domains(tuple(registry.fields.values())),
    )
    assert assurance.depth <= 4
    assert assurance.regime_gates == 2
    assert replay.candidate_id == candidate.candidate_id
    assert replay.expression.expression_id == candidate.expression.expression_id


def test_v21_budget_seed_and_stage_contract_are_exact() -> None:
    assert _economic_campaign_seeds(MECHANISM_SEARCH_V21_CAMPAIGN) == (
        MECHANISM_SEARCH_V21_SEEDS
    )
    expected = (
        {"legacy_mechanism_random_v2": 2_000},
        {
            "expanded_mechanism_random_v2_1": 1_000,
            "mechanism_evolution_v2_1": 1_000,
        },
        {
            "expanded_mechanism_random_v2_1": 1_000,
            "mechanism_evolution_v2_1": 1_000,
        },
        {
            "expanded_mechanism_random_v2_1": 1_000,
            "mechanism_evolution_v2_1": 1_000,
        },
        {
            "expanded_mechanism_random_v2_1": 1_000,
            "mechanism_evolution_v2_1": 1_000,
        },
    )
    for checkpoint_index, nonzero in enumerate(expected):
        allocation = _mechanism_v21_checkpoint_allocation(
            checkpoint_index,
            repo_root=REPO_ROOT,
            seeds=MECHANISM_SEARCH_V21_SEEDS,
        )
        assert set(allocation) == set(MECHANISM_SEARCH_V21_ARMS)
        assert {key: value for key, value in allocation.items() if value} == nonzero


def test_v21_scheduler_fills_random_slots_without_lookahead_in_adaptive_lanes() -> None:
    registry = TypedExpressionRegistry(_contracts())
    config, legacy, expanded, _ = _load_mechanism_v21_contract(REPO_ROOT)
    random_policy = MechanismRandomV2(
        MECHANISM_SEARCH_V21_SEEDS[0], registry, legacy
    )
    evolution_policy = MechanismEvolutionV2(
        MECHANISM_SEARCH_V21_SEEDS[0],
        registry,
        expanded,
        dict(config["policy_parameters"]["mechanism_evolution_v2_1"]),
    )
    assert _policy_inflight_limit(
        campaign=MECHANISM_SEARCH_V21_CAMPAIGN,
        policy=random_policy,
        workers=8,
        active_lane_count=4,
    ) == 2
    assert _policy_inflight_limit(
        campaign=MECHANISM_SEARCH_V21_CAMPAIGN,
        policy=evolution_policy,
        workers=8,
        active_lane_count=8,
    ) == 1


def test_v21_random_lookahead_preserves_rng_sequence_and_state_chain() -> None:
    registry = TypedExpressionRegistry(_contracts())
    _, legacy, _, _ = _load_mechanism_v21_contract(REPO_ROOT)
    sequential = MechanismRandomV2(MECHANISM_SEARCH_V21_SEEDS[0], registry, legacy)
    lookahead = MechanismRandomV2(MECHANISM_SEARCH_V21_SEEDS[0], registry, legacy)
    expected = [sequential.propose() for _ in range(3)]
    actual = [lookahead.propose() for _ in range(3)]
    assert [value[0].candidate_id for value in actual] == [
        value[0].candidate_id for value in expected
    ]
    for previous, current in zip(actual, actual[1:]):
        assert previous[1]["policy_state_hash_after_proposal"] == current[1][
            "policy_state_hash_before"
        ]
    assert lookahead.state_hash() == sequential.state_hash()


def test_v21_receipt_is_narrow_fresh_state_authority() -> None:
    receipt = resolve_search_economic_receipt(
        REPO_ROOT,
        "config/crypto_search_mechanism_v2_1_receipt.json",
    )
    assert receipt["result"] == "RUN_AUTHORIZED_CONDITIONAL_DEVELOPMENT"
    assert receipt["run_authorized"] is True
    assert receipt["search_campaign"]["strict_evaluated_target"] == 10_000
    assert receipt["search_campaign"]["seed_set"] == list(
        MECHANISM_SEARCH_V21_SEEDS
    )
    raw = json.loads(
        (REPO_ROOT / "config/crypto_search_mechanism_v2_1_receipt.json").read_text(
            encoding="utf-8"
        )
    )
    assert all(value is False for value in raw["fresh_state"].values())
    assert raw["boundaries"]["sealed_reads"] == 0
    assert receipt["formal_claims_authorized"] is False


def test_v21_evolution_checkpoint_is_fresh_and_exact() -> None:
    registry = TypedExpressionRegistry(_contracts())
    config, _, catalog, _ = _load_mechanism_v21_contract(REPO_ROOT)
    policy = MechanismEvolutionV2(
        MECHANISM_SEARCH_V21_SEEDS[0],
        registry,
        catalog,
        dict(config["policy_parameters"]["mechanism_evolution_v2_1"]),
    )
    assert policy.population == {}
    candidate, _ = policy.propose()
    assert candidate.candidate_id in policy.seen
    restored = MechanismEvolutionV2.from_state(registry, policy.export_state())
    expected, _ = policy.propose()
    replayed, _ = restored.propose()
    assert replayed.candidate_id == expected.candidate_id
    assert restored.state_hash() == policy.state_hash()


def test_train_gate_uses_equal_count_and_all_frozen_conditions() -> None:
    rows = []
    for arm, base, positive_count in (
        ("expanded_mechanism_random_v2_1", -0.20, 80),
        ("mechanism_evolution_v2_1", -0.10, 240),
    ):
        for index in range(4_000):
            reward = 0.10 if index < positive_count else base
            rows.append(
                {
                    "arm": arm,
                    "arm_completion_ordinal": index + 1,
                    "candidate_id": f"{arm}:{index:04d}",
                    "behavior_family_id": f"{arm}:family:{index:04d}",
                    "search_reward": reward,
                }
            )
    gate = _mechanism_v21_train_gate(repo_root=REPO_ROOT, ledger=rows)
    assert gate["status"] == "PASS"
    assert gate["validation_authorized_by_gate"] is True
    assert all(gate["checks"].values())
    assert gate["expanded_random"]["matched_evaluated_count"] == 4_000
    assert gate["evolution"]["matched_evaluated_count"] == 4_000
