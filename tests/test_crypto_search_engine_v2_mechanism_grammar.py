from __future__ import annotations

import json
import random
from pathlib import Path

import numpy as np

from alphafactory_crypto.broad_search.compositional18m import (
    MechanismSpec,
    compile_mechanism_catalog,
    mechanism_candidate_from_genes,
    mechanism_role_domains,
    sample_mechanism_candidate,
    skeleton_registry,
)
from alphafactory_crypto.broad_search.expression import (
    FieldContract,
    TypedExpressionRegistry,
)
from alphafactory_crypto.broad_search.pair18m import evaluate_pair
from alphafactory_crypto.broad_search.pair18m import SEARCH_REWARD_AUTHORITY
from alphafactory_crypto.broad_search.experiment_authority import (
    resolve_search_economic_receipt,
)
from alphafactory_crypto.broad_search.search_engine_v1 import (
    MECHANISM_EVOLUTION_OPERATIONS,
    MechanismCEMV2,
    MechanismEvolutionV2,
    MechanismRandomV2,
    _load_mechanism_v2_contract,
    _mechanism_v2_checkpoint_allocation,
    _mechanism_v2_frozen_contract,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


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


def _catalog() -> tuple[MechanismSpec, ...]:
    payload = json.loads(
        (REPO_ROOT / "config/crypto_typed_mechanism_catalog_v2.json").read_text(
            encoding="utf-8"
        )
    )
    return compile_mechanism_catalog(payload)


def test_catalog_expands_beyond_the_legacy_fixed_skeleton_box() -> None:
    catalog = _catalog()
    ids = [item.mechanism_id for item in catalog]
    assert len(catalog) > len(skeleton_registry()) * 3
    assert len(ids) == len(set(ids))
    assert {item.generation for item in catalog} == {1, 2}
    assert {item.matched_control_schema for item in catalog} == {
        "DUAL_AXIS_A_B_AB",
        "HIERARCHICAL_A_B_AB_ABC",
    }
    assert any(item.condition_operator == "ConditionGate" for item in catalog)
    assert any(item.condition_operator == "StateModulation" for item in catalog)


def test_frozen_campaign_contract_has_continuous_stage_allocation() -> None:
    config, catalog = _load_mechanism_v2_contract(REPO_ROOT)
    assert len(catalog) == 184
    assert config["search"] == {
        "strict_evaluated_target": 12_000,
        "checkpoint_size": 2_000,
        "checkpoint_count": 6,
        "raw_generation_attempts_maximum": 100_000,
        "wall_time_seconds_maximum": 64_800,
        "workers_default": 10,
        "workers_memory_fallback": 8,
        "workers_12_forbidden": True,
    }
    assert _mechanism_v2_checkpoint_allocation(
        0, repo_root=REPO_ROOT, seeds=(1, 2, 3, 4)
    ) == {
        "canonical_typed_random": 2_000,
        "extensible_mechanism_random_v2": 0,
        "mechanism_level_cem_v2": 0,
        "mechanism_evolution_v2": 0,
    }
    assert _mechanism_v2_checkpoint_allocation(
        1, repo_root=REPO_ROOT, seeds=(1, 2, 3, 4)
    )[
        "extensible_mechanism_random_v2"
    ] == 2_000
    assert _mechanism_v2_checkpoint_allocation(
        3, repo_root=REPO_ROOT, seeds=(1, 2, 3, 4)
    ) == {
        "canonical_typed_random": 0,
        "extensible_mechanism_random_v2": 0,
        "mechanism_level_cem_v2": 1_000,
        "mechanism_evolution_v2": 1_000,
    }

    frozen = _mechanism_v2_frozen_contract(
        repo_root=REPO_ROOT,
        source_sha="A" * 40,
        compiler_binding={"bundle_sha256": "B" * 64},
        behavior_contract={"schema_version": 1},
        input_identities={"carrier": "frozen"},
        environment={"workers": 10},
        contracts=_contracts(),
        carrier_id="OI_MARK_RANKS51_200_X_AGGTRADES_TOP200_ALIGNED",
    )
    assert {
        "arm_contract",
        "v1_controls",
        "v2_parameters",
        "cem",
        "evolution",
        "qualification_gate",
    }.isdisjoint(frozen)
    assert frozen["budget"]["strict_evaluated_target"] == 12_000
    assert frozen["stages"] == config["stages"]


def test_mechanism_receipt_authorizes_independent_final_arm_validation() -> None:
    receipt = resolve_search_economic_receipt(
        REPO_ROOT,
        "config/crypto_search_mechanism_v2_receipt.json",
    )
    assert receipt["result"] == "RUN_AUTHORIZED_CONDITIONAL_DEVELOPMENT"
    assert receipt["search_campaign"]["strict_evaluated_target"] == 12_000
    assert receipt["search_campaign"]["checkpoint_count"] == 6
    assert receipt["mechanism"]["economic_hypothesis_field"] == "hypothesis"
    assert receipt["validation_kill_line"][
        "random_control_survival_required"
    ] is False
    assert receipt["validation_kill_line"]["continuation_action"] == (
        "NO_ADDITIONAL_BUDGET_FINAL_PER_ARM_QUALIFICATION"
    )


def test_mechanism_identity_is_structural_not_a_field_or_parameter_identity() -> None:
    registry = TypedExpressionRegistry(_contracts())
    domains = mechanism_role_domains(tuple(registry.fields.values()))
    spec = next(
        item
        for item in _catalog()
        if item.template_id == "OI_FLOW_CONFIRMATION_V2"
        and item.payload_operator == "RatioInteraction"
        and item.condition_operator is None
    )
    first = sample_mechanism_candidate(
        registry=registry,
        spec=spec,
        domains=domains,
        rng=random.Random(17),
    )
    second = sample_mechanism_candidate(
        registry=registry,
        spec=spec,
        domains=domains,
        rng=random.Random(19),
    )
    assert first.generation_genes["mechanism_id"] == spec.mechanism_id
    assert second.generation_genes["mechanism_id"] == spec.mechanism_id
    assert first.candidate_id != second.candidate_id
    assert first.skeleton_id == second.skeleton_id == spec.mechanism_id


def test_binary_and_conditional_specs_compile_through_existing_registry_and_replay() -> None:
    registry = TypedExpressionRegistry(_contracts())
    domains = mechanism_role_domains(tuple(registry.fields.values()))
    catalog = _catalog()
    selected = (
        next(item for item in catalog if item.condition_operator is None),
        next(item for item in catalog if item.condition_operator == "ConditionGate"),
        next(item for item in catalog if item.condition_operator == "StateModulation"),
    )
    for index, spec in enumerate(selected):
        candidate = sample_mechanism_candidate(
            registry=registry,
            spec=spec,
            domains=domains,
            rng=random.Random(101 + index),
        )
        assurance = registry.validate(candidate.expression)
        control_assurance = registry.validate(candidate.control)
        assert assurance.depth <= 4
        assert len(assurance.raw_fields) <= 4
        assert len(assurance.rolling_windows) <= 3
        assert set(assurance.raw_fields) == set(control_assurance.raw_fields)
        replay = mechanism_candidate_from_genes(
            registry,
            genes=candidate.generation_genes,
            domains=domains,
        )
        assert replay.candidate_id == candidate.candidate_id
        assert replay.expression.expression_id == candidate.expression.expression_id
        assert replay.control.expression_id == candidate.control.expression_id


def test_mapping_is_derived_from_mechanism_semantics() -> None:
    catalog = _catalog()
    gated = next(item for item in catalog if item.condition_operator == "ConditionGate")
    directional = next(
        item
        for item in catalog
        if item.template_id == "FLOW_PRICE_ABSORPTION"
        and item.condition_operator is None
    )
    relative = next(
        item
        for item in catalog
        if item.template_id == "OI_FLOW_CONFIRMATION_V2"
        and item.condition_operator is None
    )
    assert gated.mapping_class == "SPARSE_EVENT_CARRY"
    assert directional.mapping_class == "DIRECTIONAL_STATEFUL"
    assert relative.mapping_class == "CROSS_SECTIONAL_RELATIVE"


class _ProbeStore:
    def __init__(self, fields: dict[str, np.ndarray]) -> None:
        self._fields = fields
        self._base = np.ones_like(next(iter(fields.values())), dtype=bool)
        self.timestamp_ns = (
            np.datetime64("2025-09-01T00:00:00", "ns").astype("int64")
            + np.arange(self._base.shape[1], dtype=np.int64) * 3_600_000_000_000
        )
        self._target = np.random.default_rng(901).normal(
            0.0, 0.001, size=self._base.shape
        )

    def block_slice(self, start: str, end: str) -> slice:
        del start, end
        return slice(None)

    def base_eligible(self) -> np.ndarray:
        return self._base

    def field(self, field_id: str) -> np.ndarray:
        return self._fields[field_id]

    def candidate_support(
        self, field_ids: tuple[str, ...], block: slice
    ) -> np.ndarray:
        del block
        output = self._base.copy()
        for field_id in field_ids:
            output &= np.isfinite(self._fields[field_id])
        return output

    def target_return(self, horizon: int) -> np.ndarray:
        del horizon
        return self._target


def test_generalized_hierarchical_controls_accept_existing_operator_basis() -> None:
    registry = TypedExpressionRegistry(_contracts())
    domains = mechanism_role_domains(tuple(registry.fields.values()))
    spec = next(
        item
        for item in _catalog()
        if item.template_id == "OI_FLOW_CONFIRMATION_V2"
        and item.payload_operator == "NormalizedDifference"
        and item.condition_operator == "ConditionGate"
        and item.condition_role == "FUNDING"
    )
    candidate = sample_mechanism_candidate(
        registry=registry,
        spec=spec,
        domains=domains,
        rng=random.Random(711),
    )
    rng = np.random.default_rng(712)
    fields: dict[str, np.ndarray] = {}
    for field_id in candidate.raw_fields:
        contract = registry.fields[field_id]
        if contract.value_type == "SIGNED_FLOW":
            fields[field_id] = rng.normal(0.0, 1.0, size=(8, 420))
        else:
            fields[field_id] = rng.lognormal(0.0, 0.5, size=(8, 420))
    evaluation = evaluate_pair(
        store=_ProbeStore(fields),
        registry=registry,
        candidate=candidate,
        block_start="2025-09-01",
        block_end="2025-10-01",
        block_role="TEST",
    )
    assert evaluation["hierarchical_three_axis"] is True
    assert evaluation["interaction_left_incremental"] is not None
    assert evaluation["interaction_right_incremental"] is not None
    assert evaluation["conditional_incremental"] is not None


def test_mechanism_random_and_cem_checkpoint_replay_are_exact() -> None:
    registry = TypedExpressionRegistry(_contracts())
    catalog = _catalog()
    random_policy = MechanismRandomV2(301, registry, catalog)
    random_policy.propose()
    restored_random = MechanismRandomV2.from_state(
        registry, random_policy.export_state()
    )
    expected, _ = random_policy.propose()
    replayed, _ = restored_random.propose()
    assert replayed.candidate_id == expected.candidate_id
    assert restored_random.state_hash() == random_policy.state_hash()

    cem = MechanismCEMV2(
        302,
        registry,
        catalog,
        {
            "duplicate_resample_limit": 64,
            "minimum_observation_count": 8,
            "elite_fraction": 0.25,
            "smoothing": 0.35,
            "minimum_probability": 0.002,
            "entropy_floor_ratio": 0.60,
            "count_pseudocount": 0.50,
        },
    )
    rows = []
    for index in range(16):
        candidate, _ = cem.propose()
        rows.append(
            {
                "candidate_id": candidate.candidate_id,
                "behavior_family_id": f"FAMILY_{index}",
                "search_reward": float(index),
                "search_reward_authority": SEARCH_REWARD_AUTHORITY,
                "candidate_spec_json": json.dumps(candidate.to_dict()),
            }
        )
    before = dict(cem.template_probabilities)
    cem.update(rows)
    assert cem.update_count == 1
    assert cem.template_probabilities != before
    restored_cem = MechanismCEMV2.from_state(registry, cem.export_state())
    expected, _ = cem.propose()
    replayed, _ = restored_cem.propose()
    assert replayed.candidate_id == expected.candidate_id
    assert restored_cem.state_hash() == cem.state_hash()


def test_mechanism_evolution_receipts_and_checkpoint_replay_are_exact() -> None:
    registry = TypedExpressionRegistry(_contracts())
    policy = MechanismEvolutionV2(
        401,
        registry,
        _catalog(),
        {
            "duplicate_resample_limit": 64,
            "warmup": 4,
            "tournament_size": 3,
            "population_limit": 32,
            "parameter_mutation_probability": 0.50,
            "mechanism_mutation_probability": 0.30,
            "crossover_probability": 0.20,
        },
    )
    for index in range(4):
        candidate, metadata = policy.propose()
        policy.observe(
            candidate,
            {
                "behavior_family_id": f"WARMUP_{index}",
                "search_reward": float(index),
                "search_reward_authority": SEARCH_REWARD_AUTHORITY,
                "family_member_count": 1,
                "operation": metadata["operation"],
            },
        )
    child, metadata = policy.propose()
    assert metadata["operation"] in MECHANISM_EVOLUTION_OPERATIONS
    assert metadata["receipt_verified"] is True
    assert mechanism_candidate_from_genes(
        registry,
        genes=child.generation_genes,
        domains=mechanism_role_domains(tuple(registry.fields.values())),
    ).candidate_id == child.candidate_id
    policy.observe(
        child,
        {
            "behavior_family_id": "CHILD",
            "search_reward": 9.0,
            "search_reward_authority": SEARCH_REWARD_AUTHORITY,
            "family_member_count": 1,
            "operation": metadata["operation"],
        },
    )
    restored = MechanismEvolutionV2.from_state(registry, policy.export_state())
    expected, _ = policy.propose()
    replayed, _ = restored.propose()
    assert replayed.candidate_id == expected.candidate_id
    assert restored.state_hash() == policy.state_hash()


def test_mechanism_evolution_memory_is_policy_local() -> None:
    registry = TypedExpressionRegistry(_contracts())
    parameters = {
        "duplicate_resample_limit": 64,
        "warmup": 4,
        "tournament_size": 3,
        "population_limit": 32,
        "parameter_mutation_probability": 0.50,
        "mechanism_mutation_probability": 0.30,
        "crossover_probability": 0.20,
    }
    first = MechanismEvolutionV2(777, registry, _catalog(), parameters)
    second = MechanismEvolutionV2(777, registry, _catalog(), parameters)
    for index in range(4):
        first_candidate, first_metadata = first.propose()
        second_candidate, second_metadata = second.propose()
        assert first_candidate.candidate_id == second_candidate.candidate_id
        shared = {
            "behavior_family_id": f"LOCAL_{index}",
            "search_reward": float(index),
            "search_reward_authority": SEARCH_REWARD_AUTHORITY,
            "policy_local_family_count_at_completion": 1,
        }
        first.observe(
            first_candidate,
            {
                **shared,
                "family_member_count": 1,
                "operation": first_metadata["operation"],
            },
        )
        second.observe(
            second_candidate,
            {
                **shared,
                "family_member_count": 100 + index,
                "operation": second_metadata["operation"],
            },
        )
    assert first.state_hash() == second.state_hash()
    assert all(
        record["family_count"] == 1 for record in first.population.values()
    )


def test_mechanism_mutation_receipt_verifies_deterministic_beta_remap() -> None:
    registry = TypedExpressionRegistry(_contracts())
    compatible = {}
    for spec in _catalog():
        key = (spec.left_role, spec.right_role, spec.condition_role)
        compatible.setdefault(key, []).append(spec)
    source = target = None
    for specs in compatible.values():
        residual = next(
            (item for item in specs if item.payload_operator == "Residual"),
            None,
        )
        non_residual = next(
            (item for item in specs if item.payload_operator != "Residual"),
            None,
        )
        if residual is not None and non_residual is not None:
            source, target = residual, non_residual
            break
    assert source is not None and target is not None
    parent = sample_mechanism_candidate(
        registry=registry,
        spec=source,
        domains=mechanism_role_domains(tuple(registry.fields.values())),
        rng=random.Random(991),
    )
    genes = dict(parent.generation_genes)
    genes["beta"] = 1.0
    parent = mechanism_candidate_from_genes(
        registry,
        genes=genes,
        domains=mechanism_role_domains(tuple(registry.fields.values())),
    )
    policy = MechanismEvolutionV2(
        992,
        registry,
        (source, target),
        {"duplicate_resample_limit": 64},
    )
    child, receipt = policy._mutate_mechanism(parent)
    assert child.generation_genes["beta"] == 0.5
    assert receipt["remapped_gene_names"] == ["beta"]
    assert policy.verify_receipt((parent,), child, receipt) is True
