"""Bounded P1 generation-2 temporal semantics on the existing V2.1 DAG."""

from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .compositional18m import (
    BETAS,
    CandidateSpec,
    MechanismSpec,
    _mechanism_binding_expression,
    _payload_sha,
    _sample_role_binding,
    _validate_mechanism_binding,
    infer_family,
    mapping_id_for_mechanism_spec,
    mechanism_role_domains,
    operator_path,
)
from .expression import NORMALIZERS, Expression, TypedExpressionRegistry, ablate_expression
from .temporal_program_v1 import (
    PROGRAM_GENE_KEYS,
    TemporalProgramSpec,
    _component,
    _component_parameters,
    _outer_expression,
    _role_scale,
)


P1 = "P1_POSITION_STATE_CHANGE_TO_RESPONSE"
REPRESENTATION = "TEMPORAL_PROGRAM_P1_G2"
CONTROL_SCHEMA = "HIERARCHICAL_A_B_AB_ABC"
SEMANTIC_GENERATION = 2
CONDITION_OPERATORS = frozenset({"ConditionGate", "StateModulation"})
CONDITION_MODES = {
    "ConditionGate": frozenset({None, "NEGATIVE"}),
    "StateModulation": frozenset(
        {None, "ABSOLUTE_MAGNITUDE", "POSITIVE_MAGNITUDE", "NEGATIVE_MAGNITUDE", "SIGN_ROUTING"}
    ),
}
G2_GENE_KEYS = frozenset(
    {
        *PROGRAM_GENE_KEYS,
        "semantic_generation",
        "parent_program_id",
        "parent_program_spec",
        "condition_field",
        "condition_auxiliary_field",
        "condition_normalizer",
        "condition_normalizer_window",
        "condition_window",
        "condition_long_window",
        "condition_threshold",
    }
)


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode()).hexdigest().upper()


def _role_width(role: str) -> int:
    return 2 if role in {"BASIS_BUNDLE", "CROSS_VENUE_OI_BUNDLE"} else 1


@dataclass(frozen=True, slots=True)
class P1Generation2ProgramSpec:
    program_id: str
    family_id: str
    hypothesis: str
    parent_program_id: str
    left_role: str
    right_role: str
    left_component: str
    right_component: str
    payload_operator: str
    payload_mode: str | None
    condition_role: str
    condition_component: str
    condition_operator: str
    condition_mode: str | None
    mapping_class: str
    matched_control_schema: str
    semantic_generation: int

    def semantic_payload(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "family_id": self.family_id,
            "parent_program_id": self.parent_program_id,
            "left_role": self.left_role,
            "right_role": self.right_role,
            "left_component": self.left_component,
            "right_component": self.right_component,
            "payload_operator": self.payload_operator,
            "payload_mode": self.payload_mode,
            "condition_role": self.condition_role,
            "condition_component": self.condition_component,
            "condition_operator": self.condition_operator,
            "condition_mode": self.condition_mode,
            "mapping_class": self.mapping_class,
            "matched_control_schema": self.matched_control_schema,
            "semantic_generation": self.semantic_generation,
        }

    def to_dict(self) -> dict[str, Any]:
        return {"program_id": self.program_id, "hypothesis": self.hypothesis, **self.semantic_payload()}

    @classmethod
    def build(
        cls,
        *,
        parent: TemporalProgramSpec,
        condition_role: str,
        condition_component: str,
        condition_operator: str,
        condition_mode: str | None,
    ) -> "P1Generation2ProgramSpec":
        if parent.family_id != P1 or len(parent.left_components) != 1 or len(parent.right_components) != 1:
            raise ValueError("P1 G2 requires one canonical P1 G1 payload")
        if condition_operator not in CONDITION_OPERATORS or condition_mode not in CONDITION_MODES[condition_operator]:
            raise ValueError("P1 G2 condition operator or mode is outside V2.1 authority")
        mapping_class = "SPARSE_EVENT_CARRY" if condition_operator == "ConditionGate" else parent.mapping_class
        hypothesis = (
            f"{parent.hypothesis} The observed {condition_role} {condition_component} state "
            f"{('gates' if condition_operator == 'ConditionGate' else 'modulates')} that payload."
        )
        semantic = {
            "schema_version": 1,
            "family_id": P1,
            "parent_program_id": parent.program_id,
            "left_role": parent.left_role,
            "right_role": parent.right_role,
            "left_component": parent.left_components[0],
            "right_component": parent.right_components[0],
            "payload_operator": parent.outer_operator,
            "payload_mode": parent.outer_mode,
            "condition_role": str(condition_role),
            "condition_component": str(condition_component),
            "condition_operator": str(condition_operator),
            "condition_mode": condition_mode,
            "mapping_class": mapping_class,
            "matched_control_schema": CONTROL_SCHEMA,
            "semantic_generation": SEMANTIC_GENERATION,
        }
        program_id = "TEMPORAL_P1_G2_" + _sha(semantic)[:32]
        return cls(program_id, P1, hypothesis, parent.program_id, parent.left_role, parent.right_role,
                   parent.left_components[0], parent.right_components[0], parent.outer_operator,
                   parent.outer_mode, str(condition_role), str(condition_component),
                   str(condition_operator), condition_mode, mapping_class, CONTROL_SCHEMA,
                   SEMANTIC_GENERATION)

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "P1Generation2ProgramSpec":
        parent = TemporalProgramSpec.build(
            family_id=P1,
            hypothesis=str(payload["parent_hypothesis"]),
            left_role=str(payload["left_role"]),
            right_role=str(payload["right_role"]),
            left_components=(str(payload["left_component"]),),
            right_components=(str(payload["right_component"]),),
            inner_operator=None,
            outer_operator=str(payload["payload_operator"]),
            outer_mode=payload.get("payload_mode"),
            mapping_class=str(payload["parent_mapping_class"]),
            axis_labels=("position_state_change", "observed_response"),
        )
        if parent.program_id != str(payload["parent_program_id"]):
            raise ValueError("P1 G2 parent identity changed")
        built = cls.build(
            parent=parent,
            condition_role=str(payload["condition_role"]),
            condition_component=str(payload["condition_component"]),
            condition_operator=str(payload["condition_operator"]),
            condition_mode=payload.get("condition_mode"),
        )
        if built.program_id != str(payload["program_id"]):
            raise ValueError("P1 G2 semantic identity changed")
        return built

    def catalog_dict(self, parent: TemporalProgramSpec) -> dict[str, Any]:
        return {
            **self.to_dict(),
            "parent_hypothesis": parent.hypothesis,
            "parent_mapping_class": parent.mapping_class,
        }


def _condition_options(parent: TemporalProgramSpec) -> tuple[tuple[str, tuple[str, ...]], ...]:
    if parent.left_role in {"OI_LEVEL", "OI_NOTIONAL"}:
        if parent.right_role == "FLOW_IMBALANCE":
            return (("FUNDING", ("Persistence", "Transition")), ("BASIS_BUNDLE", ("Transition", "Persistence")))
        if parent.right_role == "PRICE_RESPONSE":
            return (("TRADE_INTENSITY", ("EventWindow", "Persistence")), ("FUNDING", ("Persistence", "Transition")))
        return (("FLOW_IMBALANCE", ("Persistence", "EventWindow")), ("FUNDING", ("Persistence", "Transition")))
    if parent.left_role == "FUNDING":
        return (("OI_LEVEL", ("MultiScaleRelation", "Persistence")), ("CROSS_VENUE_OI_BUNDLE", ("MultiScaleRelation", "Transition")))
    if parent.left_role == "BASIS_BUNDLE":
        return (("OI_LEVEL", ("MultiScaleRelation", "Persistence")), ("FUNDING", ("Persistence", "Transition")))
    return (("FUNDING", ("Persistence", "Transition")), ("BASIS_BUNDLE", ("Transition", "Persistence")))


def _operator_modes(role: str, primitive: str) -> tuple[tuple[str, str | None], ...]:
    gate_mode = "NEGATIVE" if role in {"FUNDING", "BASIS_BUNDLE"} else None
    if primitive == "EventWindow":
        return (("ConditionGate", gate_mode),)
    modulation_mode = "SIGN_ROUTING" if primitive in {"Transition", "MultiScaleRelation"} else "ABSOLUTE_MAGNITUDE"
    return (("ConditionGate", gate_mode), ("StateModulation", modulation_mode))


def compile_p1_generation2_catalog(
    parent_catalog: Sequence[tuple[MechanismSpec, TemporalProgramSpec]],
    source_gap: Mapping[str, Any],
) -> tuple[tuple[MechanismSpec, P1Generation2ProgramSpec], ...]:
    if source_gap.get("status") != "P1_TRAIN_ONLY_SEMANTIC_SOURCE_GAP_READY":
        raise ValueError("P1 source-gap receipt is not ready")
    core = {key: value for key, value in source_gap.items() if key != "source_gap_sha256"}
    if source_gap.get("source_gap_sha256") != _sha(core) or any(
        int(source_gap.get(name, -1)) != 0
        for name in ("validation_reads", "oos_reads", "holdout_reads", "forward_reads", "promotion_reads", "sealed_reads")
    ):
        raise ValueError("P1 source-gap identity or data boundary changed")
    parents = {program.program_id: program for _, program in parent_catalog if program.family_id == P1}
    selected = [str(row["program_id"]) for row in source_gap["selected_parent_programs"]]
    if len(selected) != 24 or len(set(selected)) != len(selected) or any(value not in parents for value in selected):
        raise ValueError("P1 selected parent basis changed")
    output: list[tuple[MechanismSpec, P1Generation2ProgramSpec]] = []
    seen = set()
    for parent_id in selected:
        parent = parents[parent_id]
        for role, primitives in _condition_options(parent):
            if _role_width(parent.left_role) + _role_width(parent.right_role) + _role_width(role) > 4:
                continue
            for primitive in primitives:
                if role == parent.left_role and primitive == parent.left_components[0]:
                    continue
                if role == parent.right_role and primitive == parent.right_components[0]:
                    continue
                for operator, mode in _operator_modes(role, primitive):
                    program = P1Generation2ProgramSpec.build(
                        parent=parent,
                        condition_role=role,
                        condition_component=primitive,
                        condition_operator=operator,
                        condition_mode=mode,
                    )
                    mechanism = MechanismSpec.build(
                        template_id=P1,
                        generation=2,
                        hypothesis=program.hypothesis,
                        left_role=program.left_role,
                        right_role=program.right_role,
                        payload_operator=program.payload_operator,
                        payload_mode=program.payload_mode,
                        condition_role=program.condition_role,
                        condition_operator=program.condition_operator,
                        condition_mode=program.condition_mode,
                        mapping_class=program.mapping_class,
                        matched_control_schema=CONTROL_SCHEMA,
                        program_id=program.program_id,
                        parent_mechanism_ids=(next(mechanism.mechanism_id for mechanism, candidate in parent_catalog if candidate.program_id == parent_id),),
                    )
                    identity = (program.program_id, mechanism.mechanism_id)
                    if identity in seen:
                        continue
                    seen.add(identity)
                    output.append((mechanism, program))
    return tuple(sorted(output, key=lambda row: row[1].program_id))


def p1_generation2_catalog_payload(
    catalog: Sequence[tuple[MechanismSpec, P1Generation2ProgramSpec]],
    parent_catalog: Sequence[tuple[MechanismSpec, TemporalProgramSpec]],
) -> dict[str, Any]:
    parents = {program.program_id: program for _, program in parent_catalog}
    rows = [
        {"mechanism_spec": mechanism.to_dict(), "program_spec": program.catalog_dict(parents[program.parent_program_id])}
        for mechanism, program in catalog
    ]
    return {"schema_version": 1, "catalog_id": "P1_SEMANTIC_SUPPLY_EXPANSION_V1", "rows": rows, "catalog_sha256": _sha(rows)}


def p1_generation2_candidate_from_genes(
    registry: TypedExpressionRegistry,
    *,
    genes: Mapping[str, Any],
    domains: Mapping[str, Sequence[Any]] | None = None,
) -> CandidateSpec:
    if set(genes) != G2_GENE_KEYS or str(genes["representation"]) != REPRESENTATION or int(genes["semantic_generation"]) != 2:
        raise ValueError("P1 G2 generation genes are not exact")
    program = P1Generation2ProgramSpec.from_dict(dict(genes["program_spec"]))
    parent = TemporalProgramSpec.from_dict(dict(genes["parent_program_spec"]))
    mechanism = MechanismSpec.from_dict(dict(genes["mechanism_spec"]))
    if (
        str(genes["program_id"]) != program.program_id
        or str(genes["parent_program_id"]) != parent.program_id
        or parent.program_id != program.parent_program_id
        or str(genes["mechanism_id"]) != mechanism.mechanism_id
        or mechanism.program_id != program.program_id
        or mechanism.generation != 2
        or mechanism.condition_role != program.condition_role
        or mechanism.condition_operator != program.condition_operator
        or mechanism.condition_mode != program.condition_mode
        or mechanism.mapping_class != program.mapping_class
        or str(genes["matched_control_schema"]) != CONTROL_SCHEMA
        or int(genes["horizon_hours"]) != 4
    ):
        raise ValueError("P1 G2 program, mechanism, or market identity changed")
    role_domains = domains or mechanism_role_domains(tuple(registry.fields.values()))
    for role, field_key, auxiliary_key in (
        (parent.left_role, "left_field", "left_auxiliary_field"),
        (parent.right_role, "right_field", "right_auxiliary_field"),
        (program.condition_role, "condition_field", "condition_auxiliary_field"),
    ):
        _validate_mechanism_binding(role=role, field_id=str(genes[field_key]), auxiliary_field_id=str(genes[auxiliary_key]), domains=role_domains)
    for name in ("left_normalizer", "right_normalizer", "condition_normalizer"):
        if str(genes[name]) not in NORMALIZERS:
            raise ValueError("P1 G2 normalizer is outside authority")
    if float(genes["beta"]) not in BETAS:
        raise ValueError("P1 G2 beta is outside authority")
    left_base = _mechanism_binding_expression(role=parent.left_role, field_id=str(genes["left_field"]), auxiliary_field_id=str(genes["left_auxiliary_field"]), window=int(genes["left_normalizer_window"]), normalizer=str(genes["left_normalizer"]))
    right_base = _mechanism_binding_expression(role=parent.right_role, field_id=str(genes["right_field"]), auxiliary_field_id=str(genes["right_auxiliary_field"]), window=int(genes["right_normalizer_window"]), normalizer=str(genes["right_normalizer"]))
    payload = _outer_expression(parent, left_base=left_base, right_base=right_base, genes=genes, temporal=True)
    condition_base = _mechanism_binding_expression(role=program.condition_role, field_id=str(genes["condition_field"]), auxiliary_field_id=str(genes["condition_auxiliary_field"]), window=int(genes["condition_normalizer_window"]), normalizer=str(genes["condition_normalizer"]))
    condition = _component(condition_base, program.condition_component, window=genes["condition_window"], long_window=genes["condition_long_window"], threshold=genes["condition_threshold"])
    parameters: dict[str, Any] = {"threshold": 0.0} if program.condition_operator == "ConditionGate" else {}
    if program.condition_mode is not None:
        parameters["mode"] = program.condition_mode
    expression = Expression(program.condition_operator, (payload, condition), parameters=parameters)
    assurance = registry.validate(expression)
    control = ablate_expression(expression)
    control_assurance = registry.validate(control)
    if control.operator != "SupportMatchedPayload" or set(assurance.raw_fields) != set(control_assurance.raw_fields):
        raise AssertionError("P1 G2 hierarchical control changed raw inputs")
    mapping_id = mapping_id_for_mechanism_spec(mechanism)
    candidate_payload = {"representation": REPRESENTATION, "program_id": program.program_id, "mechanism_id": mechanism.mechanism_id, "expression": expression.canonical_dict(), "control": control.canonical_dict(), "horizon_hours": 4, "mapping_id": mapping_id}
    return CandidateSpec(_payload_sha(candidate_payload), mechanism.mechanism_id, f"CONDITIONAL_V2_{P1}", expression, control, 4, mapping_id, assurance.raw_fields, tuple(infer_family(field) for field in assurance.raw_fields), assurance.rolling_windows, assurance.depth, operator_path(expression), dict(genes))


def sample_p1_generation2_candidate(
    *,
    registry: TypedExpressionRegistry,
    mechanism: MechanismSpec,
    program: P1Generation2ProgramSpec,
    parent: CandidateSpec,
    parent_program: TemporalProgramSpec,
    scale_contract: Mapping[str, Any],
    rng: random.Random,
    domains: Mapping[str, Sequence[Any]] | None = None,
) -> CandidateSpec:
    if str(parent.generation_genes.get("program_id")) != parent_program.program_id or parent_program.program_id != program.parent_program_id:
        raise ValueError("P1 G2 sampled parent semantic changed")
    role_domains = domains or mechanism_role_domains(tuple(registry.fields.values()))
    condition_field, condition_auxiliary = _sample_role_binding(program.condition_role, role_domains, rng)
    normalizer = rng.choice(tuple(str(value) for value in scale_contract["normalizers"]))
    scale = dict(scale_contract[_role_scale(program.condition_role)])
    normalizer_window = rng.choice(tuple(int(value) for value in scale["normalizer_hours"]))
    window, long_window, threshold = _component_parameters(primitive_id=program.condition_component, role=program.condition_role, normalizer=normalizer, scale_contract=scale_contract, rng=rng)
    genes = {
        **dict(parent.generation_genes),
        "representation": REPRESENTATION,
        "program_id": program.program_id,
        "program_spec": program.catalog_dict(parent_program),
        "mechanism_id": mechanism.mechanism_id,
        "mechanism_spec": mechanism.to_dict(),
        "semantic_generation": 2,
        "parent_program_id": parent_program.program_id,
        "parent_program_spec": parent_program.to_dict(),
        "condition_field": condition_field,
        "condition_auxiliary_field": condition_auxiliary,
        "condition_normalizer": normalizer,
        "condition_normalizer_window": int(normalizer_window),
        "condition_window": window,
        "condition_long_window": long_window,
        "condition_threshold": threshold,
        "matched_control_schema": CONTROL_SCHEMA,
    }
    return p1_generation2_candidate_from_genes(registry, genes=genes, domains=role_domains)


def p1_generation2_gene_groups(candidate: CandidateSpec) -> tuple[tuple[str, ...], ...]:
    if int(candidate.generation_genes.get("semantic_generation", 0)) != 2:
        raise ValueError("P1 G2 gene groups require generation 2")
    return (
        ("left_field", "left_auxiliary_field"),
        ("right_field", "right_auxiliary_field"),
        ("left_normalizer", "left_normalizer_window"),
        ("right_normalizer", "right_normalizer_window"),
        ("left_window", "left_long_window", "left_threshold"),
        ("right_window", "right_long_window", "right_threshold"),
        ("condition_field", "condition_auxiliary_field"),
        ("condition_normalizer", "condition_normalizer_window"),
        ("condition_window", "condition_long_window", "condition_threshold"),
        ("beta",),
    )


__all__ = [
    "CONTROL_SCHEMA",
    "G2_GENE_KEYS",
    "P1Generation2ProgramSpec",
    "REPRESENTATION",
    "compile_p1_generation2_catalog",
    "p1_generation2_candidate_from_genes",
    "p1_generation2_catalog_payload",
    "p1_generation2_gene_groups",
    "sample_p1_generation2_candidate",
]
