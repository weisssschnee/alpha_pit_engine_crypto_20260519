from __future__ import annotations

import json
import random
from collections import Counter
from pathlib import Path

import pytest

from alphafactory_crypto.broad_search.compositional18m import (
    CandidateSpec,
    mechanism_role_domains,
)
from alphafactory_crypto.broad_search.expression import (
    FieldContract,
    TypedExpressionRegistry,
)
from alphafactory_crypto.broad_search.search_engine_v1 import (
    MECHANISM_EVOLUTION_OPERATIONS,
    MechanismCEMV2,
    MechanismEvolutionV2,
    MechanismRandomV2,
)
from alphafactory_crypto.broad_search.temporal_program_v1 import (
    PROGRAM_BUILDER_ID,
    compile_temporal_program_catalog,
    program_catalog_payload,
    sample_temporal_program_candidate,
    static_counterpart,
    temporal_program_candidate_from_genes,
)
from alphafactory_crypto.broad_search.temporal_program_search_v1 import (
    _stage0_checkpoint_lane_targets,
    _stage0_lane_targets,
    stage0_family_decisions,
    validate_config,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads(
    (REPO_ROOT / "config/crypto_temporal_mechanism_program_v1.json").read_text(
        encoding="utf-8"
    )
)


def _contracts() -> tuple[FieldContract, ...]:
    rows = json.loads(
        (
            REPO_ROOT
            / "runtime/crypto_search_engine_v1_4_oi_flow_20260728/aligned_carrier_manifest.json"
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


def _registry() -> TypedExpressionRegistry:
    limits = CONFIG["expression_limits"]
    return TypedExpressionRegistry(
        _contracts(),
        max_depth=int(limits["maximum_depth"]),
        max_raw_inputs=int(limits["maximum_raw_fields"]),
        max_rolling_windows=int(limits["maximum_rolling_windows"]),
        max_canonical_primitive_nodes=int(
            limits["maximum_canonical_primitive_nodes"]
        ),
        max_cross_asset_normalizations=int(
            limits["maximum_cross_asset_normalizations"]
        ),
        max_regime_gates=int(limits["maximum_regime_gates"]),
    )


def _catalog():
    return compile_temporal_program_catalog(CONFIG)


def _policy_parameters(catalog):
    return {
        "candidate_builder": PROGRAM_BUILDER_ID,
        "temporal_program_specs": [program.to_dict() for _, program in catalog],
        "time_scale_authority": CONFIG["time_scale_authority"],
        "allowed_horizons": [4],
        "balanced_template_sampling": True,
        "duplicate_resample_limit": 128,
    }


def test_catalog_is_content_addressed_balanced_and_not_the_old_canary_box() -> None:
    catalog = _catalog()
    counts = Counter(program.family_id for _, program in catalog)
    assert len(catalog) == 464
    assert counts == {
        "P1_POSITION_STATE_CHANGE_TO_RESPONSE": 180,
        "P2_RECENT_CROWDING_EVENT_TO_RESPONSE": 96,
        "P3_FLOW_SHOCK_PERSISTENCE_TO_ABSORPTION": 8,
        "P4_MULTISCALE_STATE_X_TRANSITION_ROUTING": 180,
    }
    assert len({program.program_id for _, program in catalog}) == len(catalog)
    assert len({mechanism.mechanism_id for mechanism, _ in catalog}) == len(catalog)
    payload = program_catalog_payload(catalog)
    assert payload["builder_id"] == PROGRAM_BUILDER_ID
    assert len(payload["catalog_sha256"]) == 64
    assert max(CONFIG["time_scale_authority"]["POSITIONING_SLOW"]["long_hours"]) == 720


@pytest.mark.parametrize(
    "family_id",
    [
        "P1_POSITION_STATE_CHANGE_TO_RESPONSE",
        "P2_RECENT_CROWDING_EVENT_TO_RESPONSE",
        "P3_FLOW_SHOCK_PERSISTENCE_TO_ABSORPTION",
        "P4_MULTISCALE_STATE_X_TRANSITION_ROUTING",
    ],
)
def test_each_family_compiles_replays_and_has_a_distinct_static_pair(
    family_id: str,
) -> None:
    registry = _registry()
    domains = {**mechanism_role_domains(_contracts()), "__HORIZONS__": (4,)}
    mechanism, program = next(
        pair for pair in _catalog() if pair[1].family_id == family_id
    )
    candidate = sample_temporal_program_candidate(
        registry=registry,
        mechanism=mechanism,
        program=program,
        domains=domains,
        scale_contract=CONFIG["time_scale_authority"],
        rng=random.Random(20260807),
    )
    replay = temporal_program_candidate_from_genes(
        registry, genes=candidate.generation_genes, domains=domains
    )
    static = static_counterpart(registry, candidate, domains=domains)
    assert replay.to_dict() == candidate.to_dict()
    assert static.candidate_id != candidate.candidate_id
    assert static.raw_fields == candidate.raw_fields
    assert static.mapping_id == candidate.mapping_id
    assert static.horizon_hours == candidate.horizon_hours == 4
    assert len(candidate.expression.canonical_dict()) > 0


def test_program_nesting_requires_explicit_run_local_registry_limits() -> None:
    registry = _registry()
    mechanism, program = next(
        pair for pair in _catalog() if pair[1].family_id.startswith("P3_")
    )
    candidate = sample_temporal_program_candidate(
        registry=registry,
        mechanism=mechanism,
        program=program,
        domains=mechanism_role_domains(_contracts()),
        scale_contract=CONFIG["time_scale_authority"],
        rng=random.Random(13),
    )
    with pytest.raises(ValueError, match="canonical primitive"):
        TypedExpressionRegistry(_contracts()).validate(candidate.expression)
    registry.validate(candidate.expression)


def test_random_cem_and_evolution_replay_the_program_genome() -> None:
    registry = _registry()
    catalog = _catalog()
    mechanisms = tuple(mechanism for mechanism, _ in catalog)
    parameters = _policy_parameters(catalog)

    random_policy = MechanismRandomV2(17, registry, mechanisms, parameters)
    first, metadata = random_policy.propose()
    assert metadata["operation"] == "EXTENSIBLE_MECHANISM_TYPED_RANDOM"
    restored = MechanismRandomV2.from_state(registry, random_policy.export_state())
    assert restored.state_hash() == random_policy.state_hash()
    assert temporal_program_candidate_from_genes(
        registry, genes=first.generation_genes
    ).candidate_id == first.candidate_id

    cem = MechanismCEMV2(
        19,
        registry,
        mechanisms,
        {
            **parameters,
            "minimum_observation_count": 1,
            "elite_fraction": 0.5,
            "smoothing": 0.35,
            "minimum_probability": 0.002,
            "entropy_floor_ratio": 0.6,
            "count_pseudocount": 0.5,
        },
    )
    cem_candidate, _ = cem.propose()
    cem.update(
        [
            {
                "candidate_id": cem_candidate.candidate_id,
                "candidate_spec_json": json.dumps(cem_candidate.to_dict()),
                "search_reward": 1.0,
            }
        ]
    )
    assert cem.update_count == 1
    assert MechanismCEMV2.from_state(registry, cem.export_state()).state_hash() == cem.state_hash()

    evolution = MechanismEvolutionV2(
        23,
        registry,
        mechanisms,
        {
            **parameters,
            "warmup": 2,
            "population_limit": 16,
            "tournament_size": 2,
            "parameter_mutation_probability": 1.0,
            "mechanism_mutation_probability": 0.0,
            "crossover_probability": 0.0,
            "selection_authority": "CRYPTO_TRAIN_JOINT_PRIMARY_MATCHED_SORTINO_V2",
        },
    )
    for index in range(2):
        parent, _ = evolution.propose()
        evolution.observe(
            parent,
            {
                "behavior_family_id": f"family-{index}",
                "search_reward": float(index),
                "search_reward_authority": "CRYPTO_TRAIN_JOINT_PRIMARY_MATCHED_SORTINO_V2",
                "policy_local_family_count_at_completion": 1,
                "operation": "MECHANISM_EVOLUTION_TYPED_RANDOM_WARMUP",
            },
        )
    child, child_metadata = evolution.propose()
    assert child_metadata["operation"] in MECHANISM_EVOLUTION_OPERATIONS
    assert child_metadata["receipt_verified"] is True
    assert child.candidate_id not in {
        CandidateSpec.from_dict(row["candidate"]).candidate_id
        for row in evolution.population.values()
    }
    assert MechanismEvolutionV2.from_state(
        registry, evolution.export_state()
    ).state_hash() == evolution.state_hash()


def test_contract_is_sequential_development_only_and_not_an_all_family_veto() -> None:
    validate_config(CONFIG)
    budget = CONFIG["search_budget"]
    assert budget["strict_evaluated_maximum"] == 50_000
    assert budget["checkpoint_size"] == 2_000
    assert budget["release_boundaries_strict"] == [
        10_000,
        20_000,
        30_000,
        40_000,
        50_000,
    ]
    gate = CONFIG["continuation_gates"]["stage_10000"]
    assert gate["family_continues_when_any_primary_route_passes"] is True
    assert gate["minimum_continuing_family_count"] == 1
    assert all(value is False for value in CONFIG["boundaries"].values()) is False
    for key in ("validation", "oos", "holdout", "promotion", "rescue_rerun"):
        assert CONFIG["boundaries"][key] is False


def test_pc2_runner_treats_native_exit_code_as_authority_not_stderr() -> None:
    runner = (
        REPO_ROOT / "scripts/run_crypto_temporal_mechanism_program_v1_pc2.ps1"
    ).read_text(encoding="utf-8")
    assert "function Invoke-PythonChecked" in runner
    assert '$ErrorActionPreference = "Continue"' in runner
    assert "2>&1 | ForEach-Object { Write-Output $_ }" in runner
    assert 'if ($nativeExitCode -ne 0)' in runner
    assert runner.count("Invoke-PythonChecked -Arguments") == 3
    assert "& $PythonExe -m alphafactory_crypto" not in runner


def test_stage0_checkpoint_allocation_is_exact_without_rounding_underfill() -> None:
    cumulative: Counter[str] = Counter()
    for checkpoint_index in range(5):
        local = _stage0_checkpoint_lane_targets(CONFIG, checkpoint_index)
        assert sum(local.values()) == 1_000
        assert {
            key.split("|", 2)[1]
            for key in local
        } == {
            row["family_id"] for row in CONFIG["program_families"]
        }
        cumulative.update(local)
    assert dict(cumulative) == _stage0_lane_targets(CONFIG)


def test_stage0_continuation_is_family_local_or_plus_breadth_not_all_family_veto() -> None:
    rows = []
    for family_index, family in enumerate(CONFIG["program_families"]):
        family_id = family["family_id"]
        for index in range(1_250):
            positive = family_index == 0 and index % 2 == 0
            delta = 0.2 if positive else (-0.1 if family_index else -0.01)
            rows.append(
                {
                    "program_family_id": family_id,
                    "program_id": f"{family_id}|{index % 4}",
                    "paired_worst_axis_net_delta": delta,
                    "static_dual_axis_net_positive": False,
                    "temporal_dual_axis_net_positive": positive,
                    "static_replicated_2_of_3": False,
                    "temporal_replicated_2_of_3": positive,
                    "static_matched_positive": False,
                    "temporal_matched_positive": positive,
                }
            )
    decision = stage0_family_decisions(rows, CONFIG)
    assert decision["status"] == "CONTINUE"
    assert decision["continuing_families"] == [
        "P1_POSITION_STATE_CHANGE_TO_RESPONSE"
    ]
