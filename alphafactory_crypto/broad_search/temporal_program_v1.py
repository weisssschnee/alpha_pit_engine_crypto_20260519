"""Economically explicit temporal programs compiled through the existing DAG.

This is a declarative search grammar, not a second AST or evaluator.  Every
program becomes the existing :class:`Expression` and :class:`CandidateSpec`,
then uses the existing typed registry, matched controls, mapping and economics.
"""

from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from alphafactory_crypto.broad_search.compositional18m import (
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
from alphafactory_crypto.broad_search.expression import (
    NORMALIZERS,
    Expression,
    TemporalProgramComponentAdapterV1,
    TypedExpressionRegistry,
    ablate_expression,
)


PROGRAM_BUILDER_ID = "TEMPORAL_MECHANISM_PROGRAM_V1"
PROGRAM_REPRESENTATIONS = frozenset({"STATIC_BASELINE", "TEMPORAL_PROGRAM"})
PROGRAM_GENE_KEYS = frozenset(
    {
        "representation",
        "program_id",
        "program_spec",
        "mechanism_id",
        "mechanism_spec",
        "left_field",
        "left_auxiliary_field",
        "right_field",
        "right_auxiliary_field",
        "left_normalizer",
        "right_normalizer",
        "left_normalizer_window",
        "right_normalizer_window",
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
        "horizon_hours",
        "matched_control_schema",
    }
)


def _canonical(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True, slots=True)
class TemporalProgramSpec:
    program_id: str
    family_id: str
    hypothesis: str
    left_role: str
    right_role: str
    left_components: tuple[str, ...]
    right_components: tuple[str, ...]
    inner_operator: str | None
    outer_operator: str
    outer_mode: str | None
    mapping_class: str
    axis_labels: tuple[str, str]

    def semantic_payload(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "family_id": self.family_id,
            "left_role": self.left_role,
            "right_role": self.right_role,
            "left_components": list(self.left_components),
            "right_components": list(self.right_components),
            "inner_operator": self.inner_operator,
            "outer_operator": self.outer_operator,
            "outer_mode": self.outer_mode,
            "mapping_class": self.mapping_class,
            "axis_labels": list(self.axis_labels),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "program_id": self.program_id,
            "hypothesis": self.hypothesis,
            **self.semantic_payload(),
        }

    @classmethod
    def build(
        cls,
        *,
        family_id: str,
        hypothesis: str,
        left_role: str,
        right_role: str,
        left_components: Sequence[str],
        right_components: Sequence[str],
        inner_operator: str | None,
        outer_operator: str,
        outer_mode: str | None,
        mapping_class: str,
        axis_labels: Sequence[str],
    ) -> "TemporalProgramSpec":
        semantic = {
            "schema_version": 1,
            "family_id": str(family_id),
            "left_role": str(left_role),
            "right_role": str(right_role),
            "left_components": [str(value) for value in left_components],
            "right_components": [str(value) for value in right_components],
            "inner_operator": str(inner_operator) if inner_operator else None,
            "outer_operator": str(outer_operator),
            "outer_mode": str(outer_mode) if outer_mode else None,
            "mapping_class": str(mapping_class),
            "axis_labels": [str(value) for value in axis_labels],
        }
        if len(semantic["axis_labels"]) != 2:
            raise ValueError("temporal program requires two logical control axes")
        program_id = "TEMPORAL_PROGRAM_V1_" + hashlib.sha256(
            _canonical(semantic).encode("utf-8")
        ).hexdigest()[:32].upper()
        return cls(
            program_id,
            str(family_id),
            str(hypothesis),
            str(left_role),
            str(right_role),
            tuple(str(value) for value in left_components),
            tuple(str(value) for value in right_components),
            semantic["inner_operator"],
            str(outer_operator),
            semantic["outer_mode"],
            str(mapping_class),
            tuple(semantic["axis_labels"]),
        )

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "TemporalProgramSpec":
        built = cls.build(
            family_id=str(payload["family_id"]),
            hypothesis=str(payload["hypothesis"]),
            left_role=str(payload["left_role"]),
            right_role=str(payload["right_role"]),
            left_components=payload["left_components"],
            right_components=payload["right_components"],
            inner_operator=payload.get("inner_operator"),
            outer_operator=str(payload["outer_operator"]),
            outer_mode=payload.get("outer_mode"),
            mapping_class=str(payload["mapping_class"]),
            axis_labels=payload["axis_labels"],
        )
        if built.program_id != str(payload["program_id"]):
            raise ValueError("temporal program semantic identity changed")
        return built


def compile_temporal_program_catalog(
    contract: Mapping[str, Any],
) -> tuple[tuple[MechanismSpec, TemporalProgramSpec], ...]:
    """Compile the frozen declarative families into content-addressed specs."""

    families = {str(row["family_id"]): dict(row) for row in contract["program_families"]}
    expected = {
        "P1_POSITION_STATE_CHANGE_TO_RESPONSE",
        "P2_RECENT_CROWDING_EVENT_TO_RESPONSE",
        "P3_FLOW_SHOCK_PERSISTENCE_TO_ABSORPTION",
        "P4_MULTISCALE_STATE_X_TRANSITION_ROUTING",
    }
    if set(families) != expected:
        raise ValueError("temporal program family set changed")
    output: list[tuple[MechanismSpec, TemporalProgramSpec]] = []

    def add(
        row: Mapping[str, Any],
        *,
        left_role: str,
        right_role: str,
        left_components: Sequence[str],
        right_components: Sequence[str],
        inner_operator: str | None,
        outer_operator: str,
        outer_mode: str | None,
        mapping_class: str,
        axis_labels: Sequence[str],
    ) -> None:
        program = TemporalProgramSpec.build(
            family_id=str(row["family_id"]),
            hypothesis=str(row["economic_semantics"]),
            left_role=left_role,
            right_role=right_role,
            left_components=left_components,
            right_components=right_components,
            inner_operator=inner_operator,
            outer_operator=outer_operator,
            outer_mode=outer_mode,
            mapping_class=mapping_class,
            axis_labels=axis_labels,
        )
        mechanism = MechanismSpec.build(
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
        output.append((mechanism, program))

    p1 = families["P1_POSITION_STATE_CHANGE_TO_RESPONSE"]
    for left_role in p1["left_roles"]:
        for right_role in p1["right_roles"]:
            for left_component in p1["left_component"]:
                for right_component in p1["right_component"]:
                    for outer in p1["outer_operators"]:
                        add(
                            p1,
                            left_role=left_role,
                            right_role=right_role,
                            left_components=(left_component,),
                            right_components=(right_component,),
                            inner_operator=None,
                            outer_operator=outer,
                            outer_mode=None,
                            mapping_class="CROSS_SECTIONAL_RELATIVE",
                            axis_labels=("position_state_change", "observed_response"),
                        )

    p2 = families["P2_RECENT_CROWDING_EVENT_TO_RESPONSE"]
    for left_role in p2["left_roles"]:
        for right_role in p2["right_roles"]:
            for left_component in p2["left_component"]:
                modes = (
                    ("NEGATIVE",)
                    if left_component == "TimeSince"
                    else ("POSITIVE",)
                    if left_component == "EventWindow"
                    else tuple(p2["gate_modes"])
                )
                for right_component in p2["right_component"]:
                    for mode in modes:
                        add(
                            p2,
                            left_role=left_role,
                            right_role=right_role,
                            left_components=(left_component,),
                            right_components=(right_component,),
                            inner_operator=None,
                            outer_operator="ConditionGate",
                            outer_mode=mode,
                            mapping_class="SPARSE_EVENT_CARRY",
                            axis_labels=("observed_response", "recent_crowding_event"),
                        )

    p3 = families["P3_FLOW_SHOCK_PERSISTENCE_TO_ABSORPTION"]
    for left_role in p3["left_roles"]:
        for right_role in p3["right_roles"]:
            for inner in p3["inner_absorption_operators"]:
                for outer in p3["outer_operators"]:
                    add(
                        p3,
                        left_role=left_role,
                        right_role=right_role,
                        left_components=tuple(p3["left_component"]),
                        right_components=tuple(p3["right_component"]),
                        inner_operator=inner,
                        outer_operator=outer,
                        outer_mode=("POSITIVE_MAGNITUDE" if outer == "StateModulation" else None),
                        mapping_class="DIRECTIONAL_STATEFUL",
                        axis_labels=("price_absorption", "shock_persistence"),
                    )

    p4 = families["P4_MULTISCALE_STATE_X_TRANSITION_ROUTING"]
    for left_role in p4["left_roles"]:
        for right_role in p4["right_roles"]:
            for left_component in p4["left_component"]:
                for right_component in p4["right_component"]:
                    for outer in p4["outer_operators"]:
                        modes = (
                            ("SIGN_CONFIRMATION", "SIGN_DISAGREEMENT")
                            if outer == "ConditionGate"
                            else ("SIGN_ROUTING",)
                        )
                        for mode in modes:
                            add(
                                p4,
                                left_role=left_role,
                                right_role=right_role,
                                left_components=(left_component,),
                                right_components=(right_component,),
                                inner_operator=None,
                                outer_operator=outer,
                                outer_mode=mode,
                                mapping_class=(
                                    "SPARSE_EVENT_CARRY"
                                    if outer == "ConditionGate"
                                    else "DIRECTIONAL_STATEFUL"
                                ),
                                axis_labels=("multiscale_state", "transition_routing"),
                            )

    identities = [(mechanism.mechanism_id, program.program_id) for mechanism, program in output]
    if len(identities) != len(set(identities)):
        raise ValueError("temporal program catalog has semantic duplicates")
    return tuple(sorted(output, key=lambda pair: (pair[1].family_id, pair[0].mechanism_id)))


def program_catalog_payload(
    catalog: Sequence[tuple[MechanismSpec, TemporalProgramSpec]],
) -> dict[str, Any]:
    rows = [
        {"mechanism_spec": mechanism.to_dict(), "program_spec": program.to_dict()}
        for mechanism, program in catalog
    ]
    return {
        "schema_version": 1,
        "builder_id": PROGRAM_BUILDER_ID,
        "catalog_sha256": _payload_sha(rows),
        "rows": rows,
    }


def _role_scale(role: str) -> str:
    return (
        "FLOW_FAST"
        if role in {"FLOW_IMBALANCE", "PRICE_RESPONSE", "TRADE_INTENSITY", "LARGE_TRADE"}
        else "POSITIONING_SLOW"
    )


def _normalizer_thresholds(
    normalizer: str, role: str, scale_contract: Mapping[str, Any]
) -> tuple[float, ...]:
    if role in {"BASIS_BUNDLE", "CROSS_VENUE_OI_BUNDLE"}:
        return (0.0,)
    if normalizer == "HistoricalPercentile":
        return tuple(float(value) for value in scale_contract["percentile_thresholds"])
    return tuple(float(value) for value in scale_contract["thresholds_after_normalization"])


def _component_parameters(
    *,
    primitive_id: str,
    role: str,
    normalizer: str,
    scale_contract: Mapping[str, Any],
    rng: random.Random,
    outer_persistence: bool = False,
) -> tuple[int | None, int | None, float | None]:
    scale = dict(scale_contract[_role_scale(role)])
    threshold = rng.choice(_normalizer_thresholds(normalizer, role, scale_contract))
    if primitive_id == "MultiScaleRelation":
        short_domain = tuple(int(value) for value in scale["short_hours"])
        long_domain = tuple(int(value) for value in scale["long_hours"])
        legal = tuple((short, long) for short in short_domain for long in long_domain if short < long)
        short, long = rng.choice(legal)
        return short, long, threshold
    if primitive_id in {"Delta", "Slope", "Acceleration", "PathShape"}:
        return rng.choice(tuple(int(value) for value in scale["short_hours"])), None, threshold
    if primitive_id in {"Persistence", "EventWindow"}:
        domain = scale["event_memory_hours"] if outer_persistence else scale["short_hours"]
        return rng.choice(tuple(int(value) for value in domain)), None, threshold
    if primitive_id in {"Duration", "StateAge", "TimeSince", "Transition", "FirstHit", "LastHit"}:
        return None, None, threshold
    raise ValueError(f"unsupported temporal program component: {primitive_id}")


def _component(
    source: Expression,
    primitive_id: str,
    *,
    window: int | None,
    long_window: int | None,
    threshold: float | None,
) -> Expression:
    return TemporalProgramComponentAdapterV1.expression(
        source,
        primitive_id=primitive_id,
        window=window,
        long_window=long_window,
        threshold=threshold,
    )


def _outer_expression(
    spec: TemporalProgramSpec,
    *,
    left_base: Expression,
    right_base: Expression,
    genes: Mapping[str, Any],
    temporal: bool,
) -> Expression:
    left = left_base
    right = right_base
    left_inner = left_base
    if temporal:
        left_inner = _component(
            left,
            spec.left_components[0],
            window=genes["left_window"],
            long_window=genes["left_long_window"],
            threshold=genes["left_threshold"],
        )
        left = left_inner
        if len(spec.left_components) == 2:
            left = _component(
                left,
                spec.left_components[1],
                window=genes["left_outer_window"],
                long_window=None,
                threshold=genes["left_outer_threshold"],
            )
        right = _component(
            right,
            spec.right_components[0],
            window=genes["right_window"],
            long_window=genes["right_long_window"],
            threshold=genes["right_threshold"],
        )

    if spec.family_id == "P3_FLOW_SHOCK_PERSISTENCE_TO_ABSORPTION":
        absorption_parameters = (
            {"beta": float(genes["beta"])}
            if spec.inner_operator == "Residual"
            else {}
        )
        absorption = Expression(
            str(spec.inner_operator),
            (right, left_inner if temporal else left_base),
            parameters=absorption_parameters,
        )
        left_axis, right_axis = absorption, left
    elif spec.family_id == "P2_RECENT_CROWDING_EVENT_TO_RESPONSE":
        left_axis, right_axis = right, left
    else:
        left_axis, right_axis = left, right

    parameters: dict[str, float | str] = {}
    if spec.outer_operator == "Residual":
        parameters["beta"] = float(genes["beta"])
    if spec.outer_operator == "ConditionGate":
        parameters["threshold"] = (
            float(genes["outer_threshold"]) if temporal else 0.0
        )
    if spec.outer_mode:
        parameters["mode"] = spec.outer_mode
    return Expression(spec.outer_operator, (left_axis, right_axis), parameters=parameters)


def temporal_program_candidate_from_genes(
    registry: TypedExpressionRegistry,
    *,
    genes: Mapping[str, Any],
    domains: Mapping[str, Sequence[Any]] | None = None,
) -> CandidateSpec:
    if set(genes) != PROGRAM_GENE_KEYS:
        raise ValueError("temporal program generation genes are not exact")
    representation = str(genes["representation"])
    if representation not in PROGRAM_REPRESENTATIONS:
        raise ValueError("unknown temporal program representation")
    program = TemporalProgramSpec.from_dict(dict(genes["program_spec"]))
    mechanism = MechanismSpec.from_dict(dict(genes["mechanism_spec"]))
    if (
        str(genes["program_id"]) != program.program_id
        or mechanism.program_id != program.program_id
        or str(genes["mechanism_id"]) != mechanism.mechanism_id
        or mechanism.template_id != program.family_id
        or mechanism.left_role != program.left_role
        or mechanism.right_role != program.right_role
        or mechanism.payload_operator != program.outer_operator
        or mechanism.payload_mode != program.outer_mode
        or str(genes["matched_control_schema"]) != "DUAL_AXIS_A_B_AB"
        or int(genes["horizon_hours"]) != 4
    ):
        raise ValueError("temporal program identity or market contract changed")
    role_domains = domains or mechanism_role_domains(tuple(registry.fields.values()))
    for role, field_key, auxiliary_key in (
        (program.left_role, "left_field", "left_auxiliary_field"),
        (program.right_role, "right_field", "right_auxiliary_field"),
    ):
        _validate_mechanism_binding(
            role=role,
            field_id=str(genes[field_key]),
            auxiliary_field_id=str(genes[auxiliary_key]),
            domains=role_domains,
        )
    for key in ("left_normalizer", "right_normalizer"):
        if str(genes[key]) not in NORMALIZERS:
            raise ValueError("temporal program normalizer is not registered")
    if float(genes["beta"]) not in BETAS:
        raise ValueError("temporal program beta changed")

    left_base = _mechanism_binding_expression(
        role=program.left_role,
        field_id=str(genes["left_field"]),
        auxiliary_field_id=str(genes["left_auxiliary_field"]),
        window=int(genes["left_normalizer_window"]),
        normalizer=str(genes["left_normalizer"]),
    )
    right_base = _mechanism_binding_expression(
        role=program.right_role,
        field_id=str(genes["right_field"]),
        auxiliary_field_id=str(genes["right_auxiliary_field"]),
        window=int(genes["right_normalizer_window"]),
        normalizer=str(genes["right_normalizer"]),
    )
    expression = _outer_expression(
        program,
        left_base=left_base,
        right_base=right_base,
        genes=genes,
        temporal=representation == "TEMPORAL_PROGRAM",
    )
    assurance = registry.validate(expression)
    control = ablate_expression(expression)
    control_assurance = registry.validate(control)
    if set(assurance.raw_fields) != set(control_assurance.raw_fields):
        raise AssertionError("temporal program matched control changed raw inputs")
    mapping_id = mapping_id_for_mechanism_spec(mechanism)
    genome = dict(genes)
    payload = {
        "representation": representation,
        "program_id": program.program_id,
        "mechanism_id": mechanism.mechanism_id,
        "expression": expression.canonical_dict(),
        "control": control.canonical_dict(),
        "horizon_hours": 4,
        "mapping_id": mapping_id,
    }
    return CandidateSpec(
        _payload_sha(payload),
        mechanism.mechanism_id,
        f"{representation}_{program.family_id}",
        expression,
        control,
        4,
        mapping_id,
        assurance.raw_fields,
        tuple(infer_family(field_id) for field_id in assurance.raw_fields),
        assurance.rolling_windows,
        assurance.depth,
        operator_path(expression),
        genome,
    )


def sample_temporal_program_candidate(
    *,
    registry: TypedExpressionRegistry,
    mechanism: MechanismSpec,
    program: TemporalProgramSpec,
    domains: Mapping[str, Sequence[Any]] | None,
    scale_contract: Mapping[str, Any],
    rng: random.Random,
    representation: str = "TEMPORAL_PROGRAM",
) -> CandidateSpec:
    role_domains = domains or mechanism_role_domains(tuple(registry.fields.values()))
    left, left_auxiliary = _sample_role_binding(program.left_role, role_domains, rng)
    right, right_auxiliary = _sample_role_binding(program.right_role, role_domains, rng)
    normalizers = tuple(str(value) for value in scale_contract["normalizers"])
    left_normalizer = rng.choice(normalizers)
    right_normalizer = rng.choice(normalizers)
    left_scale = dict(scale_contract[_role_scale(program.left_role)])
    right_scale = dict(scale_contract[_role_scale(program.right_role)])
    left_normalizer_window = rng.choice(tuple(int(value) for value in left_scale["normalizer_hours"]))
    right_normalizer_window = rng.choice(tuple(int(value) for value in right_scale["normalizer_hours"]))
    left_window, left_long_window, left_threshold = _component_parameters(
        primitive_id=program.left_components[0],
        role=program.left_role,
        normalizer=left_normalizer,
        scale_contract=scale_contract,
        rng=rng,
    )
    left_outer_window = None
    left_outer_threshold = None
    if len(program.left_components) == 2:
        left_outer_window, _, left_outer_threshold = _component_parameters(
            primitive_id=program.left_components[1],
            role=program.left_role,
            normalizer=left_normalizer,
            scale_contract=scale_contract,
            rng=rng,
            outer_persistence=True,
        )
    right_window, right_long_window, right_threshold = _component_parameters(
        primitive_id=program.right_components[0],
        role=program.right_role,
        normalizer=right_normalizer,
        scale_contract=scale_contract,
        rng=rng,
    )
    outer_threshold = 0.0
    if program.family_id == "P2_RECENT_CROWDING_EVENT_TO_RESPONSE" and program.left_components[0] == "TimeSince":
        outer_threshold = float(rng.choice(tuple(int(value) for value in left_scale["event_memory_hours"])))
    genes = {
        "representation": str(representation),
        "program_id": program.program_id,
        "program_spec": program.to_dict(),
        "mechanism_id": mechanism.mechanism_id,
        "mechanism_spec": mechanism.to_dict(),
        "left_field": left,
        "left_auxiliary_field": left_auxiliary,
        "right_field": right,
        "right_auxiliary_field": right_auxiliary,
        "left_normalizer": left_normalizer,
        "right_normalizer": right_normalizer,
        "left_normalizer_window": int(left_normalizer_window),
        "right_normalizer_window": int(right_normalizer_window),
        "left_window": left_window,
        "left_long_window": left_long_window,
        "left_threshold": left_threshold,
        "left_outer_window": left_outer_window,
        "left_outer_threshold": left_outer_threshold,
        "right_window": right_window,
        "right_long_window": right_long_window,
        "right_threshold": right_threshold,
        "outer_threshold": outer_threshold,
        "beta": rng.choice(BETAS),
        "horizon_hours": 4,
        "matched_control_schema": "DUAL_AXIS_A_B_AB",
    }
    return temporal_program_candidate_from_genes(
        registry, genes=genes, domains=role_domains
    )


def static_counterpart(
    registry: TypedExpressionRegistry,
    candidate: CandidateSpec,
    *,
    domains: Mapping[str, Sequence[Any]] | None = None,
) -> CandidateSpec:
    genes = dict(candidate.generation_genes)
    if str(genes.get("representation")) != "TEMPORAL_PROGRAM":
        raise ValueError("static counterpart requires a temporal program candidate")
    genes["representation"] = "STATIC_BASELINE"
    return temporal_program_candidate_from_genes(registry, genes=genes, domains=domains)


def program_gene_groups(candidate: CandidateSpec) -> tuple[tuple[str, ...], ...]:
    if str(candidate.generation_genes.get("representation")) != "TEMPORAL_PROGRAM":
        raise ValueError("program gene groups require a temporal candidate")
    return (
        ("left_field", "left_auxiliary_field"),
        ("right_field", "right_auxiliary_field"),
        ("left_normalizer", "left_normalizer_window"),
        ("right_normalizer", "right_normalizer_window"),
        ("left_window", "left_long_window", "left_threshold"),
        ("left_outer_window", "left_outer_threshold"),
        ("right_window", "right_long_window", "right_threshold"),
        ("outer_threshold",),
        ("beta",),
    )


__all__ = [
    "PROGRAM_BUILDER_ID",
    "PROGRAM_GENE_KEYS",
    "TemporalProgramSpec",
    "compile_temporal_program_catalog",
    "program_catalog_payload",
    "program_gene_groups",
    "sample_temporal_program_candidate",
    "static_counterpart",
    "temporal_program_candidate_from_genes",
]
