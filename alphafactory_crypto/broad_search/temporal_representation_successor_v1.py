"""Factorized search-time representation for existing temporal programs.

The successor deliberately compiles back through ``TemporalProgramSpec``,
``MechanismSpec`` and the existing candidate builder.  It is not an execution
grammar and owns no mapping, target, cost, reward, or evaluator semantics.
"""

from __future__ import annotations

import hashlib
import json
import random
from collections import Counter, defaultdict
from dataclasses import dataclass
from statistics import mean, median
from typing import Any, Mapping, Sequence

import numpy as np

from . import search_engine_v1 as engine
from .compositional18m import (
    BETAS,
    CandidateSpec,
    MechanismSpec,
    _payload_sha,
    _validate_mechanism_binding,
    mechanism_role_domains,
)
from .temporal_program_v1 import (
    PROGRAM_GENE_KEYS,
    TemporalProgramSpec,
    program_gene_groups,
    temporal_program_candidate_from_genes,
)
from .temporal_realization_v2 import (
    mutation_target,
    next_targeted_basin,
    next_targeted_parent,
)


REPRESENTATION_ID = "FACTORIZED_TEMPORAL_PROGRAM_GENOME_V1"
ACTIVE_FAMILIES = (
    "P1_POSITION_STATE_CHANGE_TO_RESPONSE",
    "P4_MULTISCALE_STATE_X_TRANSITION_ROUTING",
)
SEMANTIC_BLOCKS = ("role", "component", "operator")
CANDIDATE_BLOCKS = ("binding", "normalization", "temporal_parameter")
ALL_BLOCKS = SEMANTIC_BLOCKS + CANDIDATE_BLOCKS


def _json_clone(value: Any) -> Any:
    return json.loads(json.dumps(value))


def _sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "utf-8"
        )
    ).hexdigest().upper()


@dataclass(frozen=True, slots=True)
class FactorizedTemporalProgramGenome:
    """Thin, serializable search genome whose output is an existing candidate."""

    family_id: str
    left_role: str
    right_role: str
    left_components: tuple[str, ...]
    right_components: tuple[str, ...]
    inner_operator: str | None
    outer_operator: str
    outer_mode: str | None
    candidate_genes: dict[str, Any]

    @classmethod
    def from_candidate(cls, candidate: CandidateSpec) -> "FactorizedTemporalProgramGenome":
        genes = _json_clone(candidate.generation_genes)
        if set(genes) != PROGRAM_GENE_KEYS or genes.get("representation") != "TEMPORAL_PROGRAM":
            raise ValueError("factorization requires an exact temporal program candidate")
        program = TemporalProgramSpec.from_dict(genes["program_spec"])
        return cls(
            family_id=program.family_id,
            left_role=program.left_role,
            right_role=program.right_role,
            left_components=program.left_components,
            right_components=program.right_components,
            inner_operator=program.inner_operator,
            outer_operator=program.outer_operator,
            outer_mode=program.outer_mode,
            candidate_genes=genes,
        )

    def with_block_from(
        self, donor: "FactorizedTemporalProgramGenome", block: str
    ) -> "FactorizedTemporalProgramGenome":
        if self.family_id != donor.family_id:
            raise ValueError("semantic blocks cannot cross temporal families")
        values = {
            "family_id": self.family_id,
            "left_role": self.left_role,
            "right_role": self.right_role,
            "left_components": self.left_components,
            "right_components": self.right_components,
            "inner_operator": self.inner_operator,
            "outer_operator": self.outer_operator,
            "outer_mode": self.outer_mode,
            "candidate_genes": _json_clone(self.candidate_genes),
        }
        if block == "role":
            values.update(left_role=donor.left_role, right_role=donor.right_role)
        elif block == "component":
            values.update(
                left_components=donor.left_components,
                right_components=donor.right_components,
                inner_operator=donor.inner_operator,
            )
        elif block == "operator":
            values.update(outer_operator=donor.outer_operator, outer_mode=donor.outer_mode)
        else:
            keys = {
                "binding": (
                    "left_field",
                    "left_auxiliary_field",
                    "right_field",
                    "right_auxiliary_field",
                ),
                "normalization": (
                    "left_normalizer",
                    "right_normalizer",
                    "left_normalizer_window",
                    "right_normalizer_window",
                ),
                "temporal_parameter": (
                    "left_window",
                    "left_long_window",
                    "left_threshold",
                    "left_outer_window",
                    "left_outer_threshold",
                    "right_window",
                    "right_long_window",
                    "right_threshold",
                    "outer_threshold",
                    "beta",
                ),
            }.get(block)
            if keys is None:
                raise ValueError(f"unknown factorized block: {block}")
            for key in keys:
                values["candidate_genes"][key] = _json_clone(donor.candidate_genes[key])
        return FactorizedTemporalProgramGenome(**values)


@dataclass(frozen=True, slots=True)
class TemporalRepresentationInventory:
    programs_by_family: dict[str, tuple[TemporalProgramSpec, ...]]
    legal_semantics: frozenset[str]
    family_hypothesis: dict[str, str]
    family_axis_labels: dict[str, tuple[str, str]]
    compatible_mechanism_donors: tuple[MechanismSpec, ...]
    compatible_mechanism_donor_ids: tuple[str, ...]
    rejected_mechanism_donor_reasons: dict[str, int]


def build_compatibility_inventory(
    temporal_catalog: Sequence[tuple[MechanismSpec, TemporalProgramSpec]],
    mechanism_catalog: Sequence[MechanismSpec],
) -> TemporalRepresentationInventory:
    families = tuple(sorted({program.family_id for _, program in temporal_catalog}))
    programs_by_family = {
        family: tuple(
            sorted(
                (program for _, program in temporal_catalog if program.family_id == family),
                key=lambda item: item.program_id,
            )
        )
        for family in families
    }
    if len(programs_by_family) != 4 or any(
        not programs_by_family[family] for family in programs_by_family
    ):
        raise ValueError("temporal family catalog is incomplete")
    legal_semantics = frozenset(
        _sha(program.semantic_payload())
        for programs in programs_by_family.values()
        for program in programs
    )
    accepted: list[MechanismSpec] = []
    rejected: Counter[str] = Counter()
    legal_modules = {
        family: {
            (
                program.left_role,
                program.right_role,
                program.outer_operator,
                program.outer_mode,
            )
            for program in programs
        }
        for family, programs in programs_by_family.items()
    }
    for mechanism in mechanism_catalog:
        reasons = []
        if mechanism.condition_role or mechanism.condition_operator or mechanism.condition_mode:
            reasons.append("CONDITION_LAYER_NOT_TEMPORAL_DUAL_AXIS")
        if mechanism.matched_control_schema != "DUAL_AXIS_A_B_AB":
            reasons.append("MATCHED_CONTROL_SCHEMA_INCOMPATIBLE")
        compatible_family = any(
            (
                mechanism.left_role,
                mechanism.right_role,
                mechanism.payload_operator,
                mechanism.payload_mode,
            )
            in modules
            for modules in legal_modules.values()
        )
        if not compatible_family:
            reasons.append("NO_P1_P4_TEMPORAL_MODULE_MATCH")
        if reasons:
            rejected.update(set(reasons))
        else:
            accepted.append(mechanism)
    return TemporalRepresentationInventory(
        programs_by_family=programs_by_family,
        legal_semantics=legal_semantics,
        family_hypothesis={
            family: programs[0].hypothesis for family, programs in programs_by_family.items()
        },
        family_axis_labels={
            family: programs[0].axis_labels for family, programs in programs_by_family.items()
        },
        compatible_mechanism_donors=tuple(
            sorted(accepted, key=lambda item: item.mechanism_id)
        ),
        compatible_mechanism_donor_ids=tuple(
            sorted(item.mechanism_id for item in accepted)
        ),
        rejected_mechanism_donor_reasons=dict(sorted(rejected.items())),
    )


def compatibility_inventory_payload(
    inventory: TemporalRepresentationInventory,
    *,
    total_temporal_programs: int,
    total_mechanisms: int,
) -> dict[str, Any]:
    core = {
        "schema_version": 1,
        "representation_id": REPRESENTATION_ID,
        "temporal_program_count": int(total_temporal_programs),
        "active_temporal_program_count": sum(
            len(values) for values in inventory.programs_by_family.values()
        ),
        "mechanism_donor_count": int(total_mechanisms),
        "compatible_mechanism_donor_count": len(
            inventory.compatible_mechanism_donor_ids
        ),
        "rejected_mechanism_donor_reasons": inventory.rejected_mechanism_donor_reasons,
        "compatible_mechanism_donor_ids": list(
            inventory.compatible_mechanism_donor_ids
        ),
        "validation_reads": 0,
        "oos_reads": 0,
        "sealed_reads": 0,
        "market_arrays_read": 0,
        "candidate_evaluations": 0,
    }
    return {**core, "inventory_sha256": _sha(core)}


def _role_scale(role: str) -> str:
    return (
        "FLOW_FAST"
        if role in {"FLOW_IMBALANCE", "PRICE_RESPONSE", "TRADE_INTENSITY", "LARGE_TRADE"}
        else "POSITIONING_SLOW"
    )


def _binding_pairs(role: str, domains: Mapping[str, Sequence[Any]]) -> tuple[tuple[str, str], ...]:
    output = []
    for value in domains[role]:
        if role in {"BASIS_BUNDLE", "CROSS_VENUE_OI_BUNDLE"}:
            output.append((str(value[0]), str(value[1])))
        else:
            output.append((str(value), ""))
    return tuple(sorted(output))


def _threshold_domain(
    normalizer: str, role: str, scale_contract: Mapping[str, Any]
) -> tuple[float, ...]:
    if role in {"BASIS_BUNDLE", "CROSS_VENUE_OI_BUNDLE"}:
        return (0.0,)
    key = "percentile_thresholds" if normalizer == "HistoricalPercentile" else "thresholds_after_normalization"
    return tuple(float(value) for value in scale_contract[key])


def _component_domain(
    component: str,
    *,
    role: str,
    normalizer: str,
    scale_contract: Mapping[str, Any],
    outer_persistence: bool = False,
) -> tuple[tuple[int | None, int | None, float | None], ...]:
    scale = dict(scale_contract[_role_scale(role)])
    thresholds = _threshold_domain(normalizer, role, scale_contract)
    if component == "MultiScaleRelation":
        return tuple(
            (int(short), int(long), threshold)
            for short in scale["short_hours"]
            for long in scale["long_hours"]
            if int(short) < int(long)
            for threshold in thresholds
        )
    if component in {"Delta", "Slope", "Acceleration", "PathShape"}:
        return tuple(
            (int(window), None, threshold)
            for window in scale["short_hours"]
            for threshold in thresholds
        )
    if component in {"Persistence", "EventWindow"}:
        windows = scale["event_memory_hours"] if outer_persistence else scale["short_hours"]
        return tuple(
            (int(window), None, threshold)
            for window in windows
            for threshold in thresholds
        )
    if component in {"Duration", "StateAge", "TimeSince", "Transition", "FirstHit", "LastHit"}:
        return tuple((None, None, threshold) for threshold in thresholds)
    raise ValueError(f"unsupported temporal component: {component}")


def _derived_program(
    genome: FactorizedTemporalProgramGenome,
    inventory: TemporalRepresentationInventory,
) -> TemporalProgramSpec:
    family = genome.family_id
    mapping_class = (
        "CROSS_SECTIONAL_RELATIVE"
        if family == ACTIVE_FAMILIES[0]
        else (
            "SPARSE_EVENT_CARRY"
            if family == "P2_RECENT_CROWDING_EVENT_TO_RESPONSE"
            or (family == ACTIVE_FAMILIES[1] and genome.outer_operator == "ConditionGate")
            else "DIRECTIONAL_STATEFUL"
        )
    )
    program = TemporalProgramSpec.build(
        family_id=family,
        hypothesis=inventory.family_hypothesis[family],
        left_role=genome.left_role,
        right_role=genome.right_role,
        left_components=genome.left_components,
        right_components=genome.right_components,
        inner_operator=genome.inner_operator,
        outer_operator=genome.outer_operator,
        outer_mode=genome.outer_mode,
        mapping_class=mapping_class,
        axis_labels=inventory.family_axis_labels[family],
    )
    if _sha(program.semantic_payload()) not in inventory.legal_semantics:
        raise ValueError("factorized semantic combination is outside the frozen P1/P4 basis")
    return program


def _derived_mechanism(program: TemporalProgramSpec) -> MechanismSpec:
    return MechanismSpec.build(
        template_id=program.family_id,
        generation=1,
        hypothesis=program.hypothesis,
        left_role=program.left_role,
        right_role=program.right_role,
        payload_operator=program.outer_operator,
        payload_mode=program.outer_mode,
        condition_role=None,
        condition_operator=None,
        condition_mode=None,
        mapping_class=program.mapping_class,
        matched_control_schema="DUAL_AXIS_A_B_AB",
        program_id=program.program_id,
    )


def complete_factorized_genome(
    genome: FactorizedTemporalProgramGenome,
    *,
    registry: Any,
    scale_contract: Mapping[str, Any],
    inventory: TemporalRepresentationInventory,
    module_sources: Mapping[str, str] | None = None,
) -> tuple[CandidateSpec, dict[str, Any]]:
    """Minimally repair dependent genes and compile through existing authority."""

    program = _derived_program(genome, inventory)
    mechanism = _derived_mechanism(program)
    genes = _json_clone(genome.candidate_genes)
    repairs: list[dict[str, Any]] = []

    def set_if_invalid(
        names: Sequence[str], legal: Sequence[Sequence[Any]], reason: str
    ) -> None:
        observed = tuple(genes[name] for name in names)
        legal_values = tuple(tuple(value) for value in legal)
        if observed in legal_values:
            return
        replacement = legal_values[0]
        for name, value in zip(names, replacement, strict=True):
            if genes[name] != value:
                repairs.append(
                    {
                        "gene": name,
                        "preserved": False,
                        "old": genes[name],
                        "new": value,
                        "reason": reason,
                        "legal_domain_size": len(legal_values),
                    }
                )
                genes[name] = value

    role_domains = mechanism_role_domains(tuple(registry.fields.values()))
    set_if_invalid(
        ("left_field", "left_auxiliary_field"),
        _binding_pairs(program.left_role, role_domains),
        "LEFT_ROLE_BINDING_INCOMPATIBLE",
    )
    set_if_invalid(
        ("right_field", "right_auxiliary_field"),
        _binding_pairs(program.right_role, role_domains),
        "RIGHT_ROLE_BINDING_INCOMPATIBLE",
    )
    normalizers = tuple(str(value) for value in scale_contract["normalizers"])
    for side, role in (("left", program.left_role), ("right", program.right_role)):
        if str(genes[f"{side}_normalizer"]) not in normalizers:
            set_if_invalid(
                (f"{side}_normalizer",),
                tuple((value,) for value in sorted(normalizers)),
                f"{side.upper()}_NORMALIZER_INCOMPATIBLE",
            )
        windows = tuple(
            (int(value),)
            for value in sorted(
                int(item)
                for item in scale_contract[_role_scale(role)]["normalizer_hours"]
            )
        )
        set_if_invalid(
            (f"{side}_normalizer_window",),
            windows,
            f"{side.upper()}_NORMALIZER_WINDOW_INCOMPATIBLE",
        )
    left_domain = _component_domain(
        program.left_components[0],
        role=program.left_role,
        normalizer=str(genes["left_normalizer"]),
        scale_contract=scale_contract,
    )
    set_if_invalid(
        ("left_window", "left_long_window", "left_threshold"),
        left_domain,
        "LEFT_COMPONENT_PARAMETER_INCOMPATIBLE",
    )
    if len(program.left_components) == 2:
        outer_domain = _component_domain(
            program.left_components[1],
            role=program.left_role,
            normalizer=str(genes["left_normalizer"]),
            scale_contract=scale_contract,
            outer_persistence=True,
        )
    else:
        outer_domain = ((None, None, None),)
    set_if_invalid(
        ("left_outer_window", "left_outer_threshold"),
        tuple((window, threshold) for window, _, threshold in outer_domain),
        "LEFT_OUTER_COMPONENT_PARAMETER_INCOMPATIBLE",
    )
    right_domain = _component_domain(
        program.right_components[0],
        role=program.right_role,
        normalizer=str(genes["right_normalizer"]),
        scale_contract=scale_contract,
    )
    set_if_invalid(
        ("right_window", "right_long_window", "right_threshold"),
        right_domain,
        "RIGHT_COMPONENT_PARAMETER_INCOMPATIBLE",
    )
    set_if_invalid(
        ("outer_threshold",), ((0.0,),), "OUTER_THRESHOLD_DERIVED"
    )
    set_if_invalid(
        ("beta",), tuple((float(value),) for value in BETAS), "BETA_OUTSIDE_FROZEN_DOMAIN"
    )
    genes.update(
        {
            "representation": "TEMPORAL_PROGRAM",
            "program_id": program.program_id,
            "program_spec": program.to_dict(),
            "mechanism_id": mechanism.mechanism_id,
            "mechanism_spec": mechanism.to_dict(),
            "matched_control_schema": "DUAL_AXIS_A_B_AB",
            "horizon_hours": 4,
        }
    )
    candidate = temporal_program_candidate_from_genes(
        registry, genes=genes, domains=role_domains
    )
    repaired_names = {row["gene"] for row in repairs}
    preserved = sorted(
        key
        for key in PROGRAM_GENE_KEYS
        if key not in {
            "program_id",
            "program_spec",
            "mechanism_id",
            "mechanism_spec",
            "matched_control_schema",
            "horizon_hours",
        }
        and key not in repaired_names
        and genes.get(key) == genome.candidate_genes.get(key)
    )
    receipt = {
        "schema_version": 1,
        "representation_id": REPRESENTATION_ID,
        "semantic_module_sources": dict(sorted((module_sources or {}).items())),
        "semantic_modules_changed": sorted(
            key for key, value in (module_sources or {}).items() if value != "PARENT_A"
        ),
        "candidate_genes_preserved": preserved,
        "candidate_gene_repairs": repairs,
        "repair_size": len(repairs),
        "completion_attempts": 1,
        "compiled_program_id": program.program_id,
        "compiled_mechanism_id": mechanism.mechanism_id,
        "child_candidate_id": candidate.candidate_id,
    }
    return candidate, {**receipt, "completion_receipt_sha256": _sha(receipt)}


def semantic_block_children(
    first: CandidateSpec,
    second: CandidateSpec,
    *,
    registry: Any,
    scale_contract: Mapping[str, Any],
    inventory: TemporalRepresentationInventory,
    seen: set[str] | None = None,
) -> tuple[dict[str, tuple[CandidateSpec, dict[str, Any]]], dict[str, Any]]:
    a = FactorizedTemporalProgramGenome.from_candidate(first)
    b = FactorizedTemporalProgramGenome.from_candidate(second)
    if a.family_id != b.family_id:
        return {}, {
            "enumerated_recombination_count": 0,
            "legal_child_count": 0,
            "completion_failure_count": 0,
            "parent_identical_count": 0,
            "duplicate_count": 0,
            "repair_sizes": [],
        }
    legal: dict[str, tuple[CandidateSpec, dict[str, Any]]] = {}
    failures = parent_identical = duplicates = 0
    repair_sizes: list[int] = []
    for mask in range(1, (1 << len(ALL_BLOCKS)) - 1):
        selected = [ALL_BLOCKS[index] for index in range(len(ALL_BLOCKS)) if mask & (1 << index)]
        child_genome = a
        sources = {block: "PARENT_A" for block in ALL_BLOCKS}
        for block in selected:
            child_genome = child_genome.with_block_from(b, block)
            sources[block] = "PARENT_B"
        try:
            child, completion = complete_factorized_genome(
                child_genome,
                registry=registry,
                scale_contract=scale_contract,
                inventory=inventory,
                module_sources=sources,
            )
        except ValueError:
            failures += 1
            continue
        if child.candidate_id in {first.candidate_id, second.candidate_id}:
            parent_identical += 1
            continue
        if child.candidate_id in legal or (seen is not None and child.candidate_id in seen):
            duplicates += 1
            continue
        completion["selected_blocks_from_parent_b"] = selected
        legal[child.candidate_id] = (child, completion)
        repair_sizes.append(int(completion["repair_size"]))
    details = {
        "enumerated_recombination_count": (1 << len(ALL_BLOCKS)) - 2,
        "legal_child_count": len(legal),
        "completion_failure_count": failures,
        "parent_identical_count": parent_identical,
        "duplicate_count": duplicates,
        "repair_sizes": repair_sizes,
    }
    return legal, details


def representation_successor_children(
    first: CandidateSpec,
    second: CandidateSpec,
    *,
    registry: Any,
    scale_contract: Mapping[str, Any],
    inventory: TemporalRepresentationInventory,
    seen: set[str] | None = None,
    include_child_ids: bool = False,
) -> tuple[dict[str, tuple[CandidateSpec, dict[str, Any]]], dict[str, Any]]:
    """Return the lossless legacy splice closure plus factorized semantic closure."""

    semantic, semantic_details = semantic_block_children(
        first,
        second,
        registry=registry,
        scale_contract=scale_contract,
        inventory=inventory,
        seen=seen,
    )
    legal = dict(semantic)
    legacy_enumerated = legacy_parent_identical = legacy_duplicate = legacy_invalid = 0
    legacy_added = 0
    legacy_ids: set[str] = set()
    legacy_semantic_overlap = 0
    first_mechanism = MechanismSpec.from_dict(first.generation_genes["mechanism_spec"])
    second_mechanism = MechanismSpec.from_dict(second.generation_genes["mechanism_spec"])
    compatible = (
        first_mechanism.left_role,
        first_mechanism.right_role,
        first_mechanism.condition_role,
    ) == (
        second_mechanism.left_role,
        second_mechanism.right_role,
        second_mechanism.condition_role,
    )
    if compatible:
        groups = list(program_gene_groups(first))
        legacy_enumerated = (1 << len(groups)) - 2
        for mask in range(1, (1 << len(groups)) - 1):
            selected = [index for index in range(len(groups)) if mask & (1 << index)]
            genes = _json_clone(first.generation_genes)
            for index in selected:
                for name in groups[index]:
                    genes[name] = _json_clone(second.generation_genes[name])
            try:
                child = temporal_program_candidate_from_genes(registry, genes=genes)
            except ValueError:
                legacy_invalid += 1
                continue
            if child.candidate_id in {first.candidate_id, second.candidate_id}:
                legacy_parent_identical += 1
                continue
            if child.candidate_id in legacy_ids or (
                seen is not None and child.candidate_id in seen
            ):
                legacy_duplicate += 1
                continue
            legacy_ids.add(child.candidate_id)
            if child.candidate_id in legal:
                legacy_semantic_overlap += 1
                continue
            completion = {
                "schema_version": 1,
                "representation_id": REPRESENTATION_ID,
                "semantic_module_sources": {
                    block: "PARENT_A" for block in SEMANTIC_BLOCKS
                },
                "semantic_modules_changed": [],
                "candidate_genes_preserved": sorted(
                    set(PROGRAM_GENE_KEYS)
                    - {name for index in selected for name in groups[index]}
                ),
                "candidate_gene_repairs": [],
                "repair_size": 0,
                "completion_attempts": 1,
                "compiled_program_id": child.generation_genes["program_id"],
                "compiled_mechanism_id": child.generation_genes["mechanism_id"],
                "child_candidate_id": child.candidate_id,
                "selected_legacy_gene_groups_from_parent_b": [
                    list(groups[index]) for index in selected
                ],
                "selected_blocks_from_parent_b": ["legacy_parameter_subblock"],
                "semantic_edit_type": "legacy_parameter_subblock_crossover",
            }
            completion["completion_receipt_sha256"] = _sha(completion)
            legal[child.candidate_id] = (child, completion)
            legacy_added += 1
    details = {
        **semantic_details,
        "semantic_legal_child_count": int(semantic_details["legal_child_count"]),
        "legacy_parameter_enumerated_count": legacy_enumerated,
        "legacy_parameter_legal_child_count": len(legacy_ids),
        "legacy_parameter_semantic_overlap_count": legacy_semantic_overlap,
        "legacy_parameter_parent_identical_count": legacy_parent_identical,
        "legacy_parameter_duplicate_count": legacy_duplicate,
        "legacy_parameter_build_invalid_count": legacy_invalid,
        "legal_child_count": len(legal),
        "enumerated_recombination_count": int(
            semantic_details["enumerated_recombination_count"]
        )
        + legacy_enumerated,
        "parent_identical_count": int(semantic_details["parent_identical_count"])
        + legacy_parent_identical,
        "duplicate_count": int(semantic_details["duplicate_count"])
        + legacy_duplicate,
        "completion_failure_count": int(
            semantic_details["completion_failure_count"]
        )
        + legacy_invalid,
        "repair_sizes": list(semantic_details["repair_sizes"])
        + [0] * legacy_added,
    }
    if include_child_ids:
        details["legacy_parameter_child_ids"] = sorted(legacy_ids)
    return legal, details


def semantic_block_mutation(
    parent: CandidateSpec,
    *,
    donor_program: TemporalProgramSpec,
    block: str,
    registry: Any,
    scale_contract: Mapping[str, Any],
    inventory: TemporalRepresentationInventory,
) -> tuple[CandidateSpec, dict[str, Any]]:
    source = FactorizedTemporalProgramGenome.from_candidate(parent)
    if donor_program.family_id != source.family_id or block not in SEMANTIC_BLOCKS:
        raise ValueError("semantic mutation must remain within P1/P4 family")
    donor = FactorizedTemporalProgramGenome(
        donor_program.family_id,
        donor_program.left_role,
        donor_program.right_role,
        donor_program.left_components,
        donor_program.right_components,
        donor_program.inner_operator,
        donor_program.outer_operator,
        donor_program.outer_mode,
        _json_clone(source.candidate_genes),
    )
    mutated = source.with_block_from(donor, block)
    child, completion = complete_factorized_genome(
        mutated,
        registry=registry,
        scale_contract=scale_contract,
        inventory=inventory,
        module_sources={
            name: ("CATALOG_DONOR" if name == block else "PARENT_A")
            for name in ALL_BLOCKS
        },
    )
    if child.candidate_id == parent.candidate_id:
        raise ValueError("semantic mutation produced parent-identical child")
    completion["semantic_mutation_block"] = block
    completion["semantic_donor_program_id"] = donor_program.program_id
    return child, completion


def semantic_mechanism_donor_mutation(
    parent: CandidateSpec,
    *,
    donor: MechanismSpec,
    block: str,
    registry: Any,
    scale_contract: Mapping[str, Any],
    inventory: TemporalRepresentationInventory,
) -> tuple[CandidateSpec, dict[str, Any]]:
    """Use a compatible V2.1 role or operator module as a semantic donor."""

    if block not in {"role", "operator"}:
        raise ValueError("mechanism donors only own role/operator modules")
    source = FactorizedTemporalProgramGenome.from_candidate(parent)
    values = {
        "family_id": source.family_id,
        "left_role": donor.left_role if block == "role" else source.left_role,
        "right_role": donor.right_role if block == "role" else source.right_role,
        "left_components": source.left_components,
        "right_components": source.right_components,
        "inner_operator": source.inner_operator,
        "outer_operator": donor.payload_operator if block == "operator" else source.outer_operator,
        "outer_mode": donor.payload_mode if block == "operator" else source.outer_mode,
        "candidate_genes": _json_clone(source.candidate_genes),
    }
    mutated = FactorizedTemporalProgramGenome(**values)
    child, completion = complete_factorized_genome(
        mutated,
        registry=registry,
        scale_contract=scale_contract,
        inventory=inventory,
        module_sources={
            name: ("MECHANISM_V2_1_DONOR" if name == block else "PARENT_A")
            for name in ALL_BLOCKS
        },
    )
    if child.candidate_id == parent.candidate_id:
        raise ValueError("mechanism donor mutation produced parent-identical child")
    completion["semantic_mutation_block"] = block
    completion["semantic_donor_mechanism_id"] = donor.mechanism_id
    completion["semantic_donor_catalog"] = "MECHANISM_V2_1"
    return child, completion


def _receipt(
    *,
    operation: str,
    parents: Sequence[CandidateSpec],
    child: CandidateSpec,
    details: Mapping[str, Any],
) -> dict[str, Any]:
    core = {
        **dict(details),
        "schema_version": "TEMPORAL_REPRESENTATION_SUCCESSOR_RECEIPT_V1",
        "operation": operation,
        "parent_ids": [value.candidate_id for value in parents],
        "child_id": child.candidate_id,
        "parent_expression_sha256": [
            _payload_sha(value.expression.canonical_dict()) for value in parents
        ],
        "child_expression_sha256": _payload_sha(child.expression.canonical_dict()),
        "child_control_sha256": _payload_sha(child.control.canonical_dict()),
        "child_genome_sha256": _payload_sha(child.generation_genes),
    }
    return {**core, "receipt_sha256": _payload_sha(core)}


def verify_successor_receipt(
    registry: Any,
    parents: Sequence[CandidateSpec],
    child: CandidateSpec,
    receipt: Mapping[str, Any],
) -> bool:
    try:
        core = {key: value for key, value in receipt.items() if key != "receipt_sha256"}
        rebuilt = temporal_program_candidate_from_genes(
            registry, genes=child.generation_genes
        )
        return bool(
            receipt.get("schema_version")
            == "TEMPORAL_REPRESENTATION_SUCCESSOR_RECEIPT_V1"
            and receipt.get("parent_ids") == [value.candidate_id for value in parents]
            and receipt.get("child_id") == child.candidate_id
            and receipt.get("parent_expression_sha256")
            == [_payload_sha(value.expression.canonical_dict()) for value in parents]
            and receipt.get("child_expression_sha256")
            == _payload_sha(child.expression.canonical_dict())
            and receipt.get("child_control_sha256")
            == _payload_sha(child.control.canonical_dict())
            and receipt.get("child_genome_sha256") == _payload_sha(child.generation_genes)
            and receipt.get("receipt_sha256") == _payload_sha(core)
            and rebuilt.candidate_id == child.candidate_id
        )
    except (KeyError, TypeError, ValueError):
        return False


def _successor_second_parent(
    policy: engine.MechanismEvolutionV2, basin_id: str, first: CandidateSpec
) -> CandidateSpec | None:
    members = policy._targeted_members(basin_id)
    first_record = policy._targeted_parent_record(first.candidate_id)
    first_realization = str(first_record.get("concrete_realization_id") or "")
    start = int(policy.targeted_parent_cursors.get(basin_id, 0))
    choices = []
    for offset in range(len(members)):
        candidate_id = members[(start + offset) % len(members)]
        if candidate_id == first.candidate_id:
            continue
        record = policy._targeted_parent_record(candidate_id)
        candidate = policy._candidate(record)
        if (
            candidate.generation_genes["program_spec"]["family_id"]
            != first.generation_genes["program_spec"]["family_id"]
        ):
            continue
        same_realization = str(record.get("concrete_realization_id") or "") == first_realization
        choices.append((same_realization, offset, candidate))
    if not choices:
        return None
    choices.sort(key=lambda row: (row[0], row[1], row[2].candidate_id))
    policy.targeted_parent_cursors[basin_id] = start + choices[0][1] + 1
    return choices[0][2]


def propose_representation_successor(
    policy: engine.MechanismEvolutionV2,
    *,
    scale_contract: Mapping[str, Any],
    inventory: TemporalRepresentationInventory,
) -> tuple[CandidateSpec, dict[str, Any]]:
    before = policy.state_hash()
    limit = int(policy.parameters.get("duplicate_resample_limit", 64))
    for duplicate_attempt in range(1, limit + 2):
        basin_id = next_targeted_basin(policy)
        first = next_targeted_parent(policy, basin_id)
        draw = policy.rng.random()
        parameter_probability = float(policy.parameters["parameter_mutation_probability"])
        mechanism_probability = float(policy.parameters["mechanism_mutation_probability"])
        fallback_reason = None
        details: dict[str, Any] = {}
        if draw < parameter_probability:
            requested = "parameter_mutation"
            target = mutation_target(policy, basin_id)
            child, legacy_receipt = policy._mutate_parameters(first, target_dimension=target)
            parents = (first,)
            operation = engine.MECHANISM_EVOLUTION_OPERATIONS[0]
            details = {
                "semantic_edit_type": "temporal_parameter_change",
                "mutation_target": target,
                "changed_gene_groups": legacy_receipt.get("changed_gene_groups", []),
                "completion_attempts": legacy_receipt.get("internal_generation_attempts", 1),
                "repair_size": 0,
            }
        elif draw < parameter_probability + mechanism_probability:
            requested = "mechanism_mutation"
            source_family = str(first.generation_genes["program_spec"]["family_id"])
            donors: list[tuple[str, Any, str]] = [
                ("TEMPORAL_PROGRAM_V1", donor, block)
                for donor in inventory.programs_by_family[source_family]
                for block in SEMANTIC_BLOCKS
            ] + [
                ("MECHANISM_V2_1", donor, block)
                for donor in inventory.compatible_mechanism_donors
                for block in ("role", "operator")
            ]
            policy.rng.shuffle(donors)
            child = None
            completion = None
            for donor_catalog, donor, block in donors:
                try:
                    if donor_catalog == "TEMPORAL_PROGRAM_V1":
                        candidate, receipt = semantic_block_mutation(
                            first,
                            donor_program=donor,
                            block=block,
                            registry=policy.registry,
                            scale_contract=scale_contract,
                            inventory=inventory,
                        )
                    else:
                        candidate, receipt = semantic_mechanism_donor_mutation(
                            first,
                            donor=donor,
                            block=block,
                            registry=policy.registry,
                            scale_contract=scale_contract,
                            inventory=inventory,
                        )
                except ValueError:
                    continue
                if candidate.candidate_id not in policy.seen:
                    child, completion = candidate, receipt
                    break
            if child is None or completion is None:
                fallback_reason = "SEMANTIC_MUTATION_LEGAL_CHILD_SET_EMPTY"
                target = mutation_target(policy, basin_id)
                child, legacy_receipt = policy._mutate_parameters(first, target_dimension=target)
                operation = engine.MECHANISM_EVOLUTION_OPERATIONS[0]
                details = {
                    "semantic_edit_type": "temporal_parameter_change",
                    "mutation_target": target,
                    "changed_gene_groups": legacy_receipt.get("changed_gene_groups", []),
                    "completion_attempts": legacy_receipt.get("internal_generation_attempts", 1),
                    "repair_size": 0,
                }
            else:
                operation = engine.MECHANISM_EVOLUTION_OPERATIONS[1]
                details = {
                    **completion,
                    "semantic_edit_type": completion["semantic_mutation_block"] + "_change",
                }
            parents = (first,)
        else:
            requested = "crossover"
            second = _successor_second_parent(policy, basin_id, first)
            if second is None:
                legal = {}
                crossover = {
                    "enumerated_recombination_count": 0,
                    "legal_child_count": 0,
                    "completion_failure_count": 0,
                    "parent_identical_count": 0,
                    "duplicate_count": 0,
                    "repair_sizes": [],
                }
                fallback_reason = "NO_SAME_BASIN_FAMILY_PARENT"
            else:
                legal, crossover = representation_successor_children(
                    first,
                    second,
                    registry=policy.registry,
                    scale_contract=scale_contract,
                    inventory=inventory,
                    seen=policy.seen,
                )
                if not legal:
                    fallback_reason = "LEGAL_CHILD_SET_EMPTY"
            if fallback_reason:
                target = mutation_target(policy, basin_id)
                child, legacy_receipt = policy._mutate_parameters(first, target_dimension=target)
                parents = (first,)
                operation = engine.MECHANISM_EVOLUTION_OPERATIONS[0]
                details = {
                    **crossover,
                    "semantic_edit_type": "temporal_parameter_change",
                    "mutation_target": target,
                    "changed_gene_groups": legacy_receipt.get("changed_gene_groups", []),
                    "completion_attempts": legacy_receipt.get("internal_generation_attempts", 1),
                    "repair_size": 0,
                }
            else:
                candidate_id = sorted(legal)[policy.rng.randrange(len(legal))]
                child, completion = legal[candidate_id]
                parents = (first, second)
                operation = engine.MECHANISM_EVOLUTION_OPERATIONS[2]
                changed = completion.get("selected_blocks_from_parent_b", [])
                details = {
                    **crossover,
                    **completion,
                    "semantic_edit_type": "+".join(changed),
                }
        realized = {
            engine.MECHANISM_EVOLUTION_OPERATIONS[0]: "parameter_mutation",
            engine.MECHANISM_EVOLUTION_OPERATIONS[1]: "mechanism_mutation",
            engine.MECHANISM_EVOLUTION_OPERATIONS[2]: "crossover",
        }[operation]
        receipt = _receipt(
            operation=operation,
            parents=parents,
            child=child,
            details={
                **details,
                "requested_operation": requested,
                "realized_operation": realized,
                "operation_fallback": bool(fallback_reason),
                "crossover_fallback": requested == "crossover" and bool(fallback_reason),
                "fallback_reason": fallback_reason,
                "internal_generation_attempts": int(details.get("completion_attempts", 1)),
                "compile_valid_attempts": 1,
            },
        )
        receipt = policy._bind_targeted_receipt(receipt, basin_id=basin_id, parents=parents)
        if child.candidate_id in policy.seen:
            continue
        if not verify_successor_receipt(policy.registry, parents, child, receipt):
            raise RuntimeError("representation successor receipt verification failed")
        policy.seen.add(child.candidate_id)
        policy.step += 1
        return child, {
            "policy_state_hash_before": before,
            "operation": operation,
            "parent_ids": [value.candidate_id for value in parents],
            "receipt": receipt,
            "receipt_verified": True,
            "raw_attempts": duplicate_attempt + int(receipt.get("internal_generation_attempts", 1)) - 1,
            "compile_valid_attempts": int(receipt.get("compile_valid_attempts", 1)),
            "targeted_economic_basin_id": basin_id,
            "targeted_parent_pool_sha256": str(
                policy.targeted_parent_pool_payload["target_parent_pool_sha256"]
            ),
        }
    raise engine._ProposalGenerationFailure(
        "representation successor duplicate resample limit exhausted", raw_attempts=limit + 1
    )


def lossless_embedding_benchmark(
    *,
    registry: Any,
    temporal_catalog: Sequence[tuple[MechanismSpec, TemporalProgramSpec]],
    scale_contract: Mapping[str, Any],
    inventory: TemporalRepresentationInventory,
    seed: int = 20260814,
) -> dict[str, Any]:
    from .temporal_program_v1 import sample_temporal_program_candidate

    semantic_failures = []
    expression_failures = []
    preexisting_unconstructible = []
    for index, (mechanism, program) in enumerate(temporal_catalog):
        semantic_genome = FactorizedTemporalProgramGenome(
            program.family_id,
            program.left_role,
            program.right_role,
            program.left_components,
            program.right_components,
            program.inner_operator,
            program.outer_operator,
            program.outer_mode,
            {},
        )
        try:
            embedded_program = _derived_program(semantic_genome, inventory)
        except ValueError as failure:
            semantic_failures.append(
                {"program_id": program.program_id, "error": str(failure)}
            )
            continue
        if (
            embedded_program.program_id != program.program_id
            or embedded_program.semantic_payload() != program.semantic_payload()
        ):
            semantic_failures.append(
                {"program_id": program.program_id, "error": "SEMANTIC_IDENTITY_CHANGED"}
            )
            continue
        candidate = None
        for attempt in range(64):
            try:
                candidate = sample_temporal_program_candidate(
                    registry=registry,
                    mechanism=mechanism,
                    program=program,
                    domains=None,
                    scale_contract=scale_contract,
                    rng=random.Random(seed + index * 64 + attempt),
                )
                break
            except ValueError:
                continue
        if candidate is None:
            preexisting_unconstructible.append(
                {"program_id": program.program_id, "error": "NO_CONSTRUCTIBLE_SAMPLE"}
            )
            continue
        factorized = FactorizedTemporalProgramGenome.from_candidate(candidate)
        try:
            replay, receipt = complete_factorized_genome(
                factorized,
                registry=registry,
                scale_contract=scale_contract,
                inventory=inventory,
                module_sources={block: "PARENT_A" for block in ALL_BLOCKS},
            )
        except ValueError as failure:
            expression_failures.append(
                {"program_id": program.program_id, "error": str(failure)}
            )
            continue
        if (
            replay.candidate_id != candidate.candidate_id
            or replay.expression.expression_id != candidate.expression.expression_id
            or replay.control.expression_id != candidate.control.expression_id
            or receipt["repair_size"] != 0
        ):
            expression_failures.append(
                {"program_id": program.program_id, "error": "IDENTITY_CHANGED"}
            )
    result = {
        "schema_version": 1,
        "programs_tested": len(temporal_catalog),
        "exact_semantic_identity_matches": len(temporal_catalog)
        - len(semantic_failures),
        "constructible_expression_programs_tested": len(temporal_catalog)
        - len(semantic_failures)
        - len(preexisting_unconstructible),
        "exact_expression_identity_matches": len(temporal_catalog)
        - len(semantic_failures)
        - len(preexisting_unconstructible)
        - len(expression_failures),
        "semantic_failures": semantic_failures,
        "expression_failures": expression_failures,
        "preexisting_unconstructible_programs": preexisting_unconstructible,
        "pass": not semantic_failures and not expression_failures,
        "market_arrays_read": 0,
        "candidate_evaluations": 0,
        "validation_reads": 0,
        "oos_reads": 0,
        "sealed_reads": 0,
    }
    return {**result, "benchmark_sha256": _sha(result)}


def _distribution(values: Sequence[int]) -> dict[str, float]:
    return {
        "mean": float(mean(values)) if values else 0.0,
        "median": float(median(values)) if values else 0.0,
        "p90": float(np.percentile(values, 90)) if values else 0.0,
    }


def offline_closure_benchmark(
    *,
    policies: Mapping[str, engine.MechanismEvolutionV2],
    pool: Mapping[str, Any],
    registry: Any,
    scale_contract: Mapping[str, Any],
    inventory: TemporalRepresentationInventory,
    pairs_per_basin: int = 24,
    descendant_records: Mapping[str, Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Compare legacy and successor legal closure without market evaluation."""

    policy = policies[sorted(policies)[0]]
    rows = []
    descendant_by_basin: dict[str, list[CandidateSpec]] = defaultdict(list)
    descendant_source_counts: Counter[str] = Counter()
    for record in (descendant_records or {}).values():
        candidate = CandidateSpec.from_dict(record["candidate"])
        descendant_by_basin[str(record["economic_similarity_cluster_id"])].append(
            candidate
        )
        descendant_source_counts[str(record.get("source") or "UNKNOWN")] += 1
    proposal_axis_counts: Counter[str] = Counter()
    for basin in pool["target_basins"]:
        basin_id = str(basin["economic_similarity_cluster_id"])
        members = [
            policy._candidate(policy._targeted_parent_record(candidate_id))
            for candidate_id in policy._targeted_members(basin_id)
        ] + sorted(
            descendant_by_basin.get(basin_id, ()), key=lambda item: item.candidate_id
        )
        members = list({candidate.candidate_id: candidate for candidate in members}.values())
        pairs = [
            (members[left], members[right])
            for left in range(len(members))
            for right in range(left + 1, len(members))
        ]
        pairs.sort(key=lambda pair: _sha([basin_id, pair[0].candidate_id, pair[1].candidate_id]))
        for first, second in pairs[: int(pairs_per_basin)]:
            successor, successor_details = representation_successor_children(
                first,
                second,
                registry=registry,
                scale_contract=scale_contract,
                inventory=inventory,
                seen=policy.seen,
                include_child_ids=True,
            )
            legacy = {
                "enumerated_splice_count": int(
                    successor_details["legacy_parameter_enumerated_count"]
                ),
                "legal_splice_count": int(
                    successor_details["legacy_parameter_legal_child_count"]
                ),
                "duplicate_splice_count": int(
                    successor_details["legacy_parameter_duplicate_count"]
                ),
                "parent_identical_count": int(
                    successor_details["legacy_parameter_parent_identical_count"]
                ),
                "build_invalid_count": int(
                    successor_details["legacy_parameter_build_invalid_count"]
                ),
                "repair_sizes": [],
            }
            for child, completion in successor.values():
                selected = set(completion.get("selected_blocks_from_parent_b") or ())
                if selected & {"role", "operator", "normalization", "temporal_parameter"}:
                    proposal_axis_counts["mapped_weight_related_variation"] += 1
                if selected & {"component", "operator", "binding", "normalization", "temporal_parameter"}:
                    proposal_axis_counts["turnover_related_variation"] += 1
                if child.raw_fields not in {first.raw_fields, second.raw_fields}:
                    proposal_axis_counts["raw_field_variation"] += 1
                if selected & {"role", "component", "binding", "temporal_parameter"}:
                    proposal_axis_counts["asset_selection_variation"] += 1
            rows.append(
                {
                    "basin_id": basin_id,
                    "program_family_id": first.generation_genes["program_spec"]["family_id"],
                    "parent_ids": [first.candidate_id, second.candidate_id],
                    "legacy": legacy,
                    "successor": successor_details,
                    "legacy_child_ids": successor_details[
                        "legacy_parameter_child_ids"
                    ],
                    "successor_child_ids": sorted(successor),
                }
            )

    def summarize(name: str) -> dict[str, Any]:
        key = "legal_splice_count" if name == "legacy" else "legal_child_count"
        counts = [int(row[name].get(key, 0)) for row in rows]
        unique = {
            candidate_id
            for row in rows
            for candidate_id in (
                row["legacy_child_ids"]
                if name == "legacy"
                else row["successor_child_ids"]
            )
        }
        parent_identical = sum(int(row[name].get("parent_identical_count", 0)) for row in rows)
        duplicate = sum(
            int(
                row[name].get(
                    "duplicate_splice_count" if name == "legacy" else "duplicate_count", 0
                )
            )
            for row in rows
        )
        enumerated = sum(
            int(
                row[name].get(
                    "enumerated_splice_count"
                    if name == "legacy"
                    else "enumerated_recombination_count",
                    0,
                )
            )
            for row in rows
        )
        failures = sum(
            int(
                row[name].get(
                    "build_invalid_count"
                    if name == "legacy"
                    else "completion_failure_count",
                    0,
                )
            )
            for row in rows
        )
        repair_sizes = [
            int(value) for row in rows for value in row[name].get("repair_sizes", [])
        ]
        return {
            "pairs_tested": len(rows),
            "pairs_with_legal_non_parent_child": sum(value > 0 for value in counts),
            "legal_child_existence_rate": sum(value > 0 for value in counts) / max(1, len(rows)),
            "legal_children_per_pair": _distribution(counts),
            "unique_child_count": len(unique),
            "parent_identical_rejection_rate": parent_identical / max(1, enumerated),
            "duplicate_rejection_rate": duplicate / max(1, enumerated),
            "completion_failure_rate": failures / max(1, enumerated),
            "semantic_repair_size": _distribution(repair_sizes),
        }

    family = {}
    for family_id in ACTIVE_FAMILIES:
        local = [row for row in rows if row["program_family_id"] == family_id]
        family[family_id] = {
            "pairs_tested": len(local),
            "legacy_legal_child_existence_rate": sum(
                int(row["legacy"].get("legal_splice_count", 0)) > 0 for row in local
            )
            / max(1, len(local)),
            "successor_legal_child_existence_rate": sum(
                int(row["successor"].get("legal_child_count", 0)) > 0 for row in local
            )
            / max(1, len(local)),
        }
    legacy_summary = summarize("legacy")
    successor_summary = summarize("successor")
    result = {
        "schema_version": 1,
        "representation_id": REPRESENTATION_ID,
        "same_basin_pairs_tested": len(rows),
        "basins_tested": len({row["basin_id"] for row in rows}),
        "persisted_descendants_in_inventory": sum(descendant_source_counts.values()),
        "persisted_descendant_source_counts": dict(
            sorted(descendant_source_counts.items())
        ),
        "legacy_realization_v2": legacy_summary,
        "representation_successor": successor_summary,
        "P1_P4": family,
        "expanded_legal_support": bool(
            successor_summary["pairs_with_legal_non_parent_child"]
            > legacy_summary["pairs_with_legal_non_parent_child"]
            or successor_summary["legal_children_per_pair"]["median"]
            > legacy_summary["legal_children_per_pair"]["median"]
        ),
        "proposal_only_axis_coverage": dict(sorted(proposal_axis_counts.items())),
        "market_arrays_read": 0,
        "candidate_evaluations": 0,
        "validation_reads": 0,
        "oos_reads": 0,
        "sealed_reads": 0,
    }
    return {**result, "benchmark_sha256": _sha(result)}


__all__ = [
    "ACTIVE_FAMILIES",
    "ALL_BLOCKS",
    "FactorizedTemporalProgramGenome",
    "REPRESENTATION_ID",
    "TemporalRepresentationInventory",
    "build_compatibility_inventory",
    "compatibility_inventory_payload",
    "complete_factorized_genome",
    "lossless_embedding_benchmark",
    "offline_closure_benchmark",
    "propose_representation_successor",
    "representation_successor_children",
    "semantic_block_children",
    "semantic_block_mutation",
    "semantic_mechanism_donor_mutation",
    "verify_successor_receipt",
]
