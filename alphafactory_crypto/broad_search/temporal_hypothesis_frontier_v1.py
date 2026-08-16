"""Bounded P5/P6 frontier semantics compiled by the existing mechanism DAG."""

from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .compositional18m import (
    CandidateSpec,
    MechanismSpec,
    mechanism_candidate_from_genes,
    mechanism_role_domains,
    sample_mechanism_candidate,
    temporal_mechanism_candidate_from_genes,
)
from .expression import PRIMITIVE_PARAMETER_OPTIONS, TypedExpressionRegistry


P5 = "P5_FLOW_PARTICIPATION_CONVICTION"
P6 = "P6_DERIVATIVE_CROWDING_RELATIVE_PRESSURE"
P4 = "P4_MULTISCALE_STATE_X_TRANSITION_ROUTING"
FRONTIER_FAMILIES = (P5, P6)
ACTIVE_FAMILIES = (P5, P6, P4)
CONTROL_BINARY = "DUAL_AXIS_A_B_AB"
CONTROL_HIERARCHICAL = "HIERARCHICAL_A_B_AB_ABC"


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode()).hexdigest().upper()


@dataclass(frozen=True, slots=True)
class FrontierProgramSpec:
    program_id: str
    family_id: str
    motif_id: str
    hypothesis: str
    parent_template_id: str
    left_role: str
    right_role: str
    payload_operator: str
    payload_mode: str | None
    temporal_primitive: str | None
    temporal_axis: str | None
    condition_role: str | None
    condition_operator: str | None
    condition_mode: str | None
    mapping_class: str
    matched_control_schema: str
    semantic_generation: int = 1

    def semantic_payload(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "family_id": self.family_id,
            "motif_id": self.motif_id,
            "parent_template_id": self.parent_template_id,
            "left_role": self.left_role,
            "right_role": self.right_role,
            "payload_operator": self.payload_operator,
            "payload_mode": self.payload_mode,
            "temporal_primitive": self.temporal_primitive,
            "temporal_axis": self.temporal_axis,
            "condition_role": self.condition_role,
            "condition_operator": self.condition_operator,
            "condition_mode": self.condition_mode,
            "mapping_class": self.mapping_class,
            "matched_control_schema": self.matched_control_schema,
            "semantic_generation": self.semantic_generation,
        }

    def to_dict(self) -> dict[str, Any]:
        return {"program_id": self.program_id, "hypothesis": self.hypothesis, **self.semantic_payload()}

    @classmethod
    def build(cls, **values: Any) -> "FrontierProgramSpec":
        semantic = {
            "schema_version": 1,
            "family_id": str(values["family_id"]),
            "motif_id": str(values["motif_id"]),
            "parent_template_id": str(values["parent_template_id"]),
            "left_role": str(values["left_role"]),
            "right_role": str(values["right_role"]),
            "payload_operator": str(values["payload_operator"]),
            "payload_mode": values.get("payload_mode"),
            "temporal_primitive": values.get("temporal_primitive"),
            "temporal_axis": values.get("temporal_axis"),
            "condition_role": values.get("condition_role"),
            "condition_operator": values.get("condition_operator"),
            "condition_mode": values.get("condition_mode"),
            "mapping_class": str(values["mapping_class"]),
            "matched_control_schema": str(values["matched_control_schema"]),
            "semantic_generation": int(values.get("semantic_generation", 1)),
        }
        if semantic["family_id"] not in FRONTIER_FAMILIES:
            raise ValueError("frontier family is outside P5/P6")
        if bool(semantic["temporal_primitive"]) != bool(semantic["temporal_axis"]):
            raise ValueError("frontier temporal primitive and axis must be paired")
        if semantic["temporal_axis"] not in {None, "left", "right"}:
            raise ValueError("frontier temporal axis changed")
        hierarchical = bool(semantic["condition_role"])
        if hierarchical != bool(semantic["condition_operator"]):
            raise ValueError("frontier condition role and operator must be paired")
        expected_control = CONTROL_HIERARCHICAL if hierarchical else CONTROL_BINARY
        if semantic["matched_control_schema"] != expected_control:
            raise ValueError("frontier matched-control schema changed")
        if hierarchical and semantic["temporal_primitive"]:
            raise ValueError("frontier V1 does not combine a third axis with a temporal primitive")
        program_id = "TEMPORAL_FRONTIER_V1_" + _sha(semantic)[:32]
        return cls(program_id, hypothesis=str(values["hypothesis"]), **{
            key: semantic[key] for key in semantic if key != "schema_version"
        })

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "FrontierProgramSpec":
        built = cls.build(**payload)
        if built.program_id != str(payload["program_id"]):
            raise ValueError("frontier semantic identity changed")
        return built


def _mapping(operator: str, condition_operator: str | None) -> str:
    if operator == "ConditionGate" or condition_operator == "ConditionGate":
        return "SPARSE_EVENT_CARRY"
    return "CROSS_SECTIONAL_RELATIVE"


def compile_frontier_catalog(
    mechanism_basis: Sequence[MechanismSpec], source_gap: Mapping[str, Any]
) -> tuple[tuple[MechanismSpec, FrontierProgramSpec], ...]:
    core = {key: value for key, value in source_gap.items() if key != "source_gap_sha256"}
    if (
        source_gap.get("status") != "TEMPORAL_HYPOTHESIS_FRONTIER_SOURCE_GAP_READY"
        or source_gap.get("source_gap_sha256") != _sha(core)
        or any(int(source_gap.get(name, -1)) != 0 for name in (
            "validation_reads", "oos_reads", "holdout_reads", "forward_reads",
            "promotion_reads", "sealed_reads",
        ))
    ):
        raise ValueError("frontier source-gap identity or boundary changed")
    parents = {spec.template_id: spec for spec in mechanism_basis if spec.generation == 1}
    output: list[tuple[MechanismSpec, FrontierProgramSpec]] = []
    seen: set[tuple[Any, ...]] = set()
    for row in source_gap["accepted_motif_plan"]:
        template_id = str(row["parent_template_id"])
        parent = parents.get(template_id)
        if parent is None:
            raise ValueError("frontier motif references an absent V2.1 template")
        for operator in row["payload_operators"]:
            payload_modes = row.get("payload_modes", {}).get(operator, [None])
            for payload_mode in payload_modes:
                for transform in row["temporal_variants"]:
                    temporal_primitive = transform.get("primitive")
                    temporal_axis = transform.get("axis")
                    key = (
                        row["family_id"], template_id, operator, payload_mode,
                        temporal_primitive, temporal_axis, None, None, None,
                    )
                    if key in seen:
                        continue
                    seen.add(key)
                    program = FrontierProgramSpec.build(
                        family_id=row["family_id"], motif_id=row["motif_id"],
                        hypothesis=row["hypothesis"], parent_template_id=template_id,
                        left_role=parent.left_role, right_role=parent.right_role,
                        payload_operator=operator, payload_mode=payload_mode,
                        temporal_primitive=temporal_primitive, temporal_axis=temporal_axis,
                        condition_role=None, condition_operator=None, condition_mode=None,
                        mapping_class=_mapping(operator, None),
                        matched_control_schema=CONTROL_BINARY,
                    )
                    mechanism = MechanismSpec.build(
                        template_id=row["family_id"], generation=1,
                        hypothesis=program.hypothesis, left_role=program.left_role,
                        right_role=program.right_role, payload_operator=operator,
                        payload_mode=payload_mode, condition_role=None,
                        condition_operator=None, condition_mode=None,
                        mapping_class=program.mapping_class,
                        matched_control_schema=CONTROL_BINARY,
                        program_id=program.program_id,
                        parent_mechanism_ids=(parent.mechanism_id,),
                    )
                    output.append((mechanism, program))
                for condition in row.get("condition_variants", []):
                    key = (
                        row["family_id"], template_id, operator, payload_mode, None, None,
                        condition["role"], condition["operator"], condition.get("mode"),
                    )
                    if key in seen:
                        continue
                    seen.add(key)
                    program = FrontierProgramSpec.build(
                        family_id=row["family_id"], motif_id=row["motif_id"],
                        hypothesis=row["hypothesis"], parent_template_id=template_id,
                        left_role=parent.left_role, right_role=parent.right_role,
                        payload_operator=operator, payload_mode=payload_mode,
                        temporal_primitive=None, temporal_axis=None,
                        condition_role=condition["role"],
                        condition_operator=condition["operator"],
                        condition_mode=condition.get("mode"),
                        mapping_class=_mapping(operator, condition["operator"]),
                        matched_control_schema=CONTROL_HIERARCHICAL,
                        semantic_generation=2,
                    )
                    mechanism = MechanismSpec.build(
                        template_id=row["family_id"], generation=2,
                        hypothesis=program.hypothesis, left_role=program.left_role,
                        right_role=program.right_role, payload_operator=operator,
                        payload_mode=payload_mode, condition_role=program.condition_role,
                        condition_operator=program.condition_operator,
                        condition_mode=program.condition_mode,
                        mapping_class=program.mapping_class,
                        matched_control_schema=CONTROL_HIERARCHICAL,
                        program_id=program.program_id,
                        parent_mechanism_ids=(parent.mechanism_id,),
                    )
                    output.append((mechanism, program))
    output.sort(key=lambda value: value[1].program_id)
    if not output or {program.family_id for _, program in output} != set(FRONTIER_FAMILIES):
        raise ValueError("frontier catalog family coverage changed")
    return tuple(output)


def sample_frontier_candidate(
    *, registry: TypedExpressionRegistry, mechanism: MechanismSpec,
    program: FrontierProgramSpec, rng: random.Random,
    domains: Mapping[str, Sequence[Any]] | None = None,
) -> CandidateSpec:
    if mechanism.program_id != program.program_id:
        raise ValueError("frontier program/mechanism binding changed")
    role_domains = domains or mechanism_role_domains(tuple(registry.fields.values()))
    base = sample_mechanism_candidate(
        registry=registry, spec=mechanism, domains=role_domains, rng=rng
    )
    if program.temporal_primitive is None:
        return base
    options = tuple(PRIMITIVE_PARAMETER_OPTIONS[program.temporal_primitive])
    window, long_window, threshold = rng.choice(options)
    role = program.left_role if program.temporal_axis == "left" else program.right_role
    placement = (
        "POST_TYPED_BUNDLE_PRE_OUTER"
        if role in {"BASIS_BUNDLE", "CROSS_VENUE_OI_BUNDLE"}
        else "PRE_NORMALIZER"
        if program.temporal_primitive in {"Delta", "Acceleration", "MultiScaleRelation"}
        else "POST_NORMALIZER"
    )
    genes = {
        **dict(base.generation_genes),
        "temporal_transform": {
            "temporal_family_id": program.family_id,
            "primitive_id": program.temporal_primitive,
            "axis": program.temporal_axis,
            "window": window,
            "long_window": long_window,
            "threshold": threshold,
            "placement": placement,
        },
    }
    return temporal_mechanism_candidate_from_genes(registry, genes=genes, domains=role_domains)


def rebuild_frontier_candidate(
    registry: TypedExpressionRegistry, candidate: CandidateSpec,
    domains: Mapping[str, Sequence[Any]] | None = None,
) -> CandidateSpec:
    genes = candidate.generation_genes
    if "temporal_transform" in genes:
        return temporal_mechanism_candidate_from_genes(registry, genes=genes, domains=domains)
    return mechanism_candidate_from_genes(registry, genes=genes, domains=domains)


def frontier_catalog_payload(
    catalog: Sequence[tuple[MechanismSpec, FrontierProgramSpec]],
    source_gap_sha256: str,
) -> dict[str, Any]:
    rows = [
        {"mechanism_spec": mechanism.to_dict(), "program_spec": program.to_dict()}
        for mechanism, program in catalog
    ]
    core = {
        "schema_version": 1,
        "status": "TEMPORAL_HYPOTHESIS_FRONTIER_V1_CATALOG_FROZEN",
        "catalog_id": "TEMPORAL_HYPOTHESIS_FRONTIER_V1",
        "source_gap_sha256": source_gap_sha256,
        "accepted_semantics": len(rows),
        "family_counts": {
            family: sum(program.family_id == family for _, program in catalog)
            for family in FRONTIER_FAMILIES
        },
        "semantic_rows": rows,
        "validation_reads": 0, "oos_reads": 0, "holdout_reads": 0,
        "forward_reads": 0, "promotion_reads": 0, "sealed_reads": 0,
    }
    return {**core, "catalog_sha256": _sha(core)}


__all__ = [
    "ACTIVE_FAMILIES", "FRONTIER_FAMILIES", "P4", "P5", "P6",
    "FrontierProgramSpec", "compile_frontier_catalog", "frontier_catalog_payload",
    "rebuild_frontier_candidate", "sample_frontier_candidate",
]
