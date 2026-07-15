"""Lazy finite structural grammar for the bounded real-data canary.

The grammar counts and addresses candidates by mixed-radix coordinates.  It
never constructs the full candidate universe.  Small immutable registries of
fields, representations, primitive parameter routes, and mechanism families
are the only precomputed structures.
"""

from __future__ import annotations

import bisect
import hashlib
import random
from dataclasses import dataclass, replace
from types import MappingProxyType
from typing import Iterator, Mapping, Sequence

from .contracts import CandidateGenome, MutationReceipt, canonical_json_bytes


CROSS_SECTIONAL_RELATIVE = "CROSS_SECTIONAL_RELATIVE"
DIRECTIONAL_STATEFUL = "DIRECTIONAL_STATEFUL"
SPARSE_EVENT_CARRY = "SPARSE_EVENT_CARRY"

MECHANISM_FAMILIES = (
    CROSS_SECTIONAL_RELATIVE,
    DIRECTIONAL_STATEFUL,
    SPARSE_EVENT_CARRY,
)

MECHANISM_MAPPING: Mapping[str, str] = MappingProxyType(
    {
        CROSS_SECTIONAL_RELATIVE: "CROSS_SECTIONAL_ZERO_NET",
        DIRECTIONAL_STATEFUL: "TIME_SERIES_DIRECTIONAL_STATEFUL",
        SPARSE_EVENT_CARRY: "SPARSE_EVENT_OR_CARRY",
    }
)

WINDOWLESS_PRIMITIVES = frozenset(
    {"Duration", "StateAge", "TimeSince", "LastHit", "FirstHit", "Transition"}
)
SPARSE_PRIMITIVES = frozenset(
    {
        "Persistence",
        "Duration",
        "StateAge",
        "TimeSince",
        "LastHit",
        "FirstHit",
        "Transition",
        "EventWindow",
    }
)
CANONICAL_PRIMITIVE_IDS = (
    "Delta",
    "Slope",
    "Acceleration",
    "Persistence",
    "Duration",
    "StateAge",
    "TimeSince",
    "LastHit",
    "FirstHit",
    "Transition",
    "PathShape",
    "EventWindow",
    "MultiScaleRelation",
)
TARGET_HORIZONS_HOURS = (1, 4)
MINIMUM_SUPPORT_SIZE = 8192

GENOME_GENE_FIELDS = (
    "field_id",
    "representation_id",
    "primitive_id",
    "window",
    "long_window",
    "threshold",
    "mechanism_family",
    "target_horizon_hours",
)


@dataclass(frozen=True, slots=True)
class RepresentationSpec:
    representation_id: str
    formula: str
    input_domain: str
    nonlinear: bool


@dataclass(frozen=True, slots=True)
class FieldSpec:
    field_id: str
    field_family: str
    value_domain: str
    representations: tuple[RepresentationSpec, ...]


def _representations(
    value_domain: str, nonlinear_id: str, formula: str
) -> tuple[RepresentationSpec, ...]:
    return (
        RepresentationSpec("identity", "x", value_domain, False),
        RepresentationSpec(nonlinear_id, formula, value_domain, True),
    )


_NONNEGATIVE = _representations("NON_NEGATIVE", "log1p_nonnegative", "log1p(max(x,0))")
_POSITIVE = _representations("STRICT_POSITIVE", "log_positive", "log(max(x,1e-12))")
_SIGNED = _representations("SIGNED", "signed_log1p_abs", "sign(x)*log1p(abs(x))")
_BOUNDED_SIGNED = _representations(
    "BOUNDED_SIGNED",
    "atanh_clip_0_999",
    "atanh(x); exact endpoints +/-1 use +/-0.999 for numerical finiteness",
)
_UNIT_INTERVAL = _representations(
    "UNIT_INTERVAL",
    "logit_clip_1e6",
    "log(x/(1-x)); exact endpoints 0/1 use 1e-6/(1-1e-6)",
)


# Exact searchable surface of the approved native aggTrades development view.
FROZEN_FIELD_SPECS = (
    FieldSpec("trade_count", "COUNT", "NON_NEGATIVE", _NONNEGATIVE),
    FieldSpec("underlying_trade_count", "COUNT", "NON_NEGATIVE", _NONNEGATIVE),
    FieldSpec("quantity", "VOLUME_OR_NOTIONAL", "NON_NEGATIVE", _NONNEGATIVE),
    FieldSpec("notional", "VOLUME_OR_NOTIONAL", "NON_NEGATIVE", _NONNEGATIVE),
    FieldSpec("buy_agg_trade_count", "COUNT", "NON_NEGATIVE", _NONNEGATIVE),
    FieldSpec("sell_agg_trade_count", "COUNT", "NON_NEGATIVE", _NONNEGATIVE),
    FieldSpec("buy_quantity", "VOLUME_OR_NOTIONAL", "NON_NEGATIVE", _NONNEGATIVE),
    FieldSpec("sell_quantity", "VOLUME_OR_NOTIONAL", "NON_NEGATIVE", _NONNEGATIVE),
    FieldSpec("buy_notional", "VOLUME_OR_NOTIONAL", "NON_NEGATIVE", _NONNEGATIVE),
    FieldSpec("sell_notional", "VOLUME_OR_NOTIONAL", "NON_NEGATIVE", _NONNEGATIVE),
    FieldSpec("signed_aggressor_quantity", "SIGNED_FLOW", "SIGNED", _SIGNED),
    FieldSpec("signed_aggressor_notional", "SIGNED_FLOW", "SIGNED", _SIGNED),
    FieldSpec("vwap", "PRICE", "STRICT_POSITIVE", _POSITIVE),
    FieldSpec("buy_vwap", "PRICE", "STRICT_POSITIVE", _POSITIVE),
    FieldSpec("sell_vwap", "PRICE", "STRICT_POSITIVE", _POSITIVE),
    FieldSpec("volume_imbalance", "SIGNED_BOUNDED_RATIO", "BOUNDED_SIGNED", _BOUNDED_SIGNED),
    FieldSpec("buy_sell_notional_ratio", "POSITIVE_RATIO", "NON_NEGATIVE", _NONNEGATIVE),
    FieldSpec("price_range_bps", "NONNEGATIVE_BPS", "NON_NEGATIVE", _NONNEGATIVE),
    FieldSpec("close_to_open_bps", "SIGNED_BPS", "SIGNED", _SIGNED),
    FieldSpec(
        "large_trade_count_ratio_100k_plus",
        "BOUNDED_RATIO",
        "UNIT_INTERVAL",
        _UNIT_INTERVAL,
    ),
    FieldSpec("large_notional_ratio_100k_plus", "BOUNDED_RATIO", "UNIT_INTERVAL", _UNIT_INTERVAL),
)

FROZEN_RELEASE_FIELDS = tuple(spec.field_id for spec in FROZEN_FIELD_SPECS)


PrimitiveParameters = tuple[int | None, int | None, float | None]


def _primitive_parameter_registry() -> Mapping[str, tuple[PrimitiveParameters, ...]]:
    windows = (2, 4, 8, 12, 24)
    path_windows = tuple(window for window in windows if window >= 3)
    long_windows = (8, 12, 24, 48)
    multi_scale = tuple(
        (short, long, None)
        for short in windows
        for long in long_windows
        if short < long
    )
    registry: dict[str, tuple[PrimitiveParameters, ...]] = {
        "Delta": tuple((window, None, None) for window in windows),
        "Slope": tuple((window, None, None) for window in windows if window >= 2),
        "Acceleration": tuple((window, None, None) for window in windows),
        "Persistence": tuple((window, None, 0.0) for window in windows),
        "PathShape": tuple((window, None, None) for window in path_windows),
        "EventWindow": tuple((window, None, 0.0) for window in windows),
        "MultiScaleRelation": multi_scale,
    }
    for primitive_id in WINDOWLESS_PRIMITIVES:
        registry[primitive_id] = ((None, None, 0.0),)
    if set(registry) != set(CANONICAL_PRIMITIVE_IDS):
        raise AssertionError("primitive parameter registry diverged from canonical IDs")
    return MappingProxyType(registry)


PRIMITIVE_PARAMETER_OPTIONS = _primitive_parameter_registry()


@dataclass(frozen=True, slots=True)
class GrammarCell:
    mechanism_family: str
    primitive_id: str
    parameter_options: tuple[PrimitiveParameters, ...]


@dataclass(frozen=True, slots=True)
class GrammarFilter:
    """Optional structural restriction used without materializing candidates."""

    field_ids: frozenset[str] | None = None
    representation_ids: frozenset[str] | None = None
    primitive_ids: frozenset[str] | None = None
    mechanism_families: frozenset[str] | None = None
    target_horizons_hours: frozenset[int] | None = None
    windows: frozenset[int | None] | None = None
    long_windows: frozenset[int | None] | None = None
    thresholds: frozenset[float | None] | None = None


def _changed_genes(parent: CandidateGenome, child: CandidateGenome) -> tuple[str, ...]:
    left = parent.canonical_dict()
    right = child.canonical_dict()
    return tuple(field for field in GENOME_GENE_FIELDS if left[field] != right[field])


def _decode_mixed_radix(value: int, radices: Sequence[int]) -> tuple[int, ...]:
    if any(radix <= 0 for radix in radices):
        raise ValueError("mixed-radix axes must be non-empty")
    digits = [0] * len(radices)
    remainder = value
    for index in range(len(radices) - 1, -1, -1):
        digits[index] = remainder % radices[index]
        remainder //= radices[index]
    if remainder:
        raise IndexError("mixed-radix coordinate exceeds its support")
    return tuple(digits)


def _encode_mixed_radix(digits: Sequence[int], radices: Sequence[int]) -> int:
    if len(digits) != len(radices):
        raise ValueError("mixed-radix digits/radices length mismatch")
    value = 0
    for digit, radix in zip(digits, radices):
        if radix <= 0 or digit < 0 or digit >= radix:
            raise ValueError("mixed-radix digit outside its axis")
        value = value * radix + digit
    return value


class FrozenGrammar:
    """Exact finite grammar with O(number-of-cells) count/decode operations."""

    def __init__(
        self,
        *,
        field_specs: Sequence[FieldSpec] = FROZEN_FIELD_SPECS,
        target_horizons_hours: Sequence[int] = TARGET_HORIZONS_HOURS,
        minimum_support_size: int = MINIMUM_SUPPORT_SIZE,
    ) -> None:
        self._field_specs = tuple(field_specs)
        self._target_horizons = tuple(int(value) for value in target_horizons_hours)
        if len(self._field_specs) != len({spec.field_id for spec in self._field_specs}):
            raise ValueError("field IDs must be unique")
        if not self._field_specs or not self._target_horizons:
            raise ValueError("grammar requires fields and target horizons")
        if len(self._target_horizons) != len(set(self._target_horizons)) or any(
            value <= 0 for value in self._target_horizons
        ):
            raise ValueError("target horizons must be unique positive hours")
        self._field_representations = tuple(
            (field.field_id, representation.representation_id)
            for field in self._field_specs
            for representation in field.representations
        )
        if len(self._field_representations) != len(set(self._field_representations)):
            raise ValueError("field/representation identities must be unique")
        self._cells = tuple(
            GrammarCell(mechanism, primitive_id, PRIMITIVE_PARAMETER_OPTIONS[primitive_id])
            for mechanism in MECHANISM_FAMILIES
            for primitive_id in CANONICAL_PRIMITIVE_IDS
            if mechanism != SPARSE_EVENT_CARRY or primitive_id in SPARSE_PRIMITIVES
        )
        self._cell_offsets = self._offsets(
            self._cells, self._field_representations, self._target_horizons
        )
        self._support_size = self._cell_offsets[-1]
        if self._support_size < int(minimum_support_size):
            raise ValueError(
                f"legal grammar support {self._support_size} is below required {minimum_support_size}"
            )
        self._contract_sha256 = self._build_contract_sha256()

    @classmethod
    def default(cls) -> "FrozenGrammar":
        return cls()

    @staticmethod
    def _offsets(
        cells: Sequence[GrammarCell],
        field_representations: Sequence[tuple[str, str]],
        horizons: Sequence[int],
    ) -> tuple[int, ...]:
        offsets = [0]
        for cell in cells:
            offsets.append(
                offsets[-1]
                + len(field_representations) * len(cell.parameter_options) * len(horizons)
            )
        return tuple(offsets)

    def _build_contract_sha256(self) -> str:
        payload = {
            "schema_version": 1,
            "fields": [
                {
                    "field_id": field.field_id,
                    "field_family": field.field_family,
                    "value_domain": field.value_domain,
                    "representations": [
                        {
                            "representation_id": representation.representation_id,
                            "formula": representation.formula,
                            "input_domain": representation.input_domain,
                            "nonlinear": representation.nonlinear,
                        }
                        for representation in field.representations
                    ],
                }
                for field in self._field_specs
            ],
            "cells": [
                {
                    "mechanism_family": cell.mechanism_family,
                    "primitive_id": cell.primitive_id,
                    "parameter_options": [list(option) for option in cell.parameter_options],
                }
                for cell in self._cells
            ],
            "target_horizons_hours": list(self._target_horizons),
            "mechanism_mapping": dict(MECHANISM_MAPPING),
        }
        return hashlib.sha256(canonical_json_bytes(payload)).hexdigest().upper()

    @property
    def support_size(self) -> int:
        return self._support_size

    @property
    def contract_sha256(self) -> str:
        return self._contract_sha256

    @property
    def field_specs(self) -> tuple[FieldSpec, ...]:
        return self._field_specs

    @property
    def field_representations(self) -> tuple[tuple[str, str], ...]:
        return self._field_representations

    @property
    def field_families(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(spec.field_family for spec in self._field_specs))

    def field_spec(self, field_id: str) -> FieldSpec:
        try:
            return next(spec for spec in self._field_specs if spec.field_id == field_id)
        except StopIteration as error:
            raise ValueError(f"unknown frozen field: {field_id}") from error

    def field_family_for(self, field_id: str) -> str:
        return self.field_spec(field_id).field_family

    def field_representations_for_family(
        self, field_family: str
    ) -> tuple[tuple[str, str], ...]:
        if field_family not in self.field_families:
            raise ValueError(f"unknown field family: {field_family}")
        fields = {
            spec.field_id for spec in self._field_specs if spec.field_family == field_family
        }
        return tuple(value for value in self._field_representations if value[0] in fields)

    @property
    def target_horizons_hours(self) -> tuple[int, ...]:
        return self._target_horizons

    @property
    def cells(self) -> tuple[GrammarCell, ...]:
        return self._cells

    def cells_for_mechanism(self, mechanism_family: str) -> tuple[GrammarCell, ...]:
        if mechanism_family not in MECHANISM_FAMILIES:
            raise ValueError(f"unknown mechanism_family: {mechanism_family}")
        return tuple(
            cell for cell in self._cells if cell.mechanism_family == mechanism_family
        )

    def parameter_options(self, primitive_id: str) -> tuple[PrimitiveParameters, ...]:
        try:
            return PRIMITIVE_PARAMETER_OPTIONS[primitive_id]
        except KeyError as error:
            raise ValueError(f"unknown canonical primitive: {primitive_id}") from error

    def mapping_for(self, genome: CandidateGenome) -> str:
        self.validate(genome)
        return MECHANISM_MAPPING[genome.mechanism_family]

    def validate(self, genome: CandidateGenome) -> None:
        if not isinstance(genome, CandidateGenome):
            raise TypeError("grammar accepts CandidateGenome only")
        if (genome.field_id, genome.representation_id) not in self._field_representations:
            raise ValueError("unapproved field/representation identity")
        if genome.mechanism_family not in MECHANISM_FAMILIES:
            raise ValueError("unknown mechanism family")
        if genome.primitive_id not in CANONICAL_PRIMITIVE_IDS:
            raise ValueError("unknown or deprecated primitive")
        if (
            genome.mechanism_family == SPARSE_EVENT_CARRY
            and genome.primitive_id not in SPARSE_PRIMITIVES
        ):
            raise ValueError("sparse mechanism accepts event/state primitives only")
        parameters = (genome.window, genome.long_window, genome.threshold)
        if parameters not in PRIMITIVE_PARAMETER_OPTIONS[genome.primitive_id]:
            raise ValueError("primitive parameters are outside the frozen semantic route")
        if genome.primitive_id in WINDOWLESS_PRIMITIVES and (
            genome.window is not None or genome.long_window is not None
        ):
            raise ValueError("windowless primitive requires the unique N/A window")
        if genome.primitive_id == "MultiScaleRelation" and not (
            genome.window is not None
            and genome.long_window is not None
            and genome.window < genome.long_window
        ):
            raise ValueError("MultiScaleRelation requires short window < long window")
        if genome.target_horizon_hours not in self._target_horizons:
            raise ValueError("target horizon is outside the frozen contract")

    def is_legal(self, genome: CandidateGenome) -> bool:
        try:
            self.validate(genome)
        except (TypeError, ValueError):
            return False
        return True

    def decode(self, index: int) -> CandidateGenome:
        if isinstance(index, bool) or int(index) != index or not 0 <= index < self.support_size:
            raise IndexError("candidate index outside grammar support")
        cell_index = bisect.bisect_right(self._cell_offsets, int(index)) - 1
        local = int(index) - self._cell_offsets[cell_index]
        cell = self._cells[cell_index]
        field_index, parameter_index, horizon_index = _decode_mixed_radix(
            local,
            (
                len(self._field_representations),
                len(cell.parameter_options),
                len(self._target_horizons),
            ),
        )
        field_id, representation_id = self._field_representations[field_index]
        window, long_window, threshold = cell.parameter_options[parameter_index]
        return CandidateGenome(
            field_id=field_id,
            representation_id=representation_id,
            primitive_id=cell.primitive_id,
            window=window,
            long_window=long_window,
            threshold=threshold,
            mechanism_family=cell.mechanism_family,
            target_horizon_hours=self._target_horizons[horizon_index],
        )

    def encode(self, genome: CandidateGenome) -> int:
        self.validate(genome)
        cell_index = next(
            index
            for index, cell in enumerate(self._cells)
            if cell.mechanism_family == genome.mechanism_family
            and cell.primitive_id == genome.primitive_id
        )
        cell = self._cells[cell_index]
        field_index = self._field_representations.index(
            (genome.field_id, genome.representation_id)
        )
        parameter_index = cell.parameter_options.index(
            (genome.window, genome.long_window, genome.threshold)
        )
        horizon_index = self._target_horizons.index(genome.target_horizon_hours)
        return self._cell_offsets[cell_index] + _encode_mixed_radix(
            (field_index, parameter_index, horizon_index),
            (
                len(self._field_representations),
                len(cell.parameter_options),
                len(self._target_horizons),
            ),
        )

    def _filtered_axes(
        self, grammar_filter: GrammarFilter | None
    ) -> tuple[
        tuple[tuple[str, str], ...],
        tuple[GrammarCell, ...],
        tuple[int, ...],
        tuple[int, ...],
    ]:
        selected = grammar_filter or GrammarFilter()
        field_representations = tuple(
            value
            for value in self._field_representations
            if (selected.field_ids is None or value[0] in selected.field_ids)
            and (
                selected.representation_ids is None
                or value[1] in selected.representation_ids
            )
        )
        horizons = tuple(
            value
            for value in self._target_horizons
            if selected.target_horizons_hours is None
            or value in selected.target_horizons_hours
        )
        cells: list[GrammarCell] = []
        for cell in self._cells:
            if (
                selected.primitive_ids is not None
                and cell.primitive_id not in selected.primitive_ids
            ) or (
                selected.mechanism_families is not None
                and cell.mechanism_family not in selected.mechanism_families
            ):
                continue
            options = tuple(
                option
                for option in cell.parameter_options
                if (selected.windows is None or option[0] in selected.windows)
                and (selected.long_windows is None or option[1] in selected.long_windows)
                and (selected.thresholds is None or option[2] in selected.thresholds)
            )
            if options:
                cells.append(replace(cell, parameter_options=options))
        frozen_cells = tuple(cells)
        offsets = self._offsets(frozen_cells, field_representations, horizons)
        return field_representations, frozen_cells, horizons, offsets

    def filtered_support_size(self, grammar_filter: GrammarFilter | None = None) -> int:
        return self._filtered_axes(grammar_filter)[-1][-1]

    def decode_filtered(
        self, index: int, grammar_filter: GrammarFilter | None = None
    ) -> CandidateGenome:
        fields, cells, horizons, offsets = self._filtered_axes(grammar_filter)
        support = offsets[-1]
        if isinstance(index, bool) or int(index) != index or not 0 <= index < support:
            raise IndexError("filtered candidate index outside support")
        cell_index = bisect.bisect_right(offsets, int(index)) - 1
        local = int(index) - offsets[cell_index]
        cell = cells[cell_index]
        field_index, parameter_index, horizon_index = _decode_mixed_radix(
            local, (len(fields), len(cell.parameter_options), len(horizons))
        )
        field_id, representation_id = fields[field_index]
        window, long_window, threshold = cell.parameter_options[parameter_index]
        genome = CandidateGenome(
            field_id,
            representation_id,
            cell.primitive_id,
            window,
            long_window,
            threshold,
            cell.mechanism_family,
            horizons[horizon_index],
        )
        self.validate(genome)
        return genome

    def iter_filtered(
        self, grammar_filter: GrammarFilter | None = None
    ) -> Iterator[CandidateGenome]:
        """Yield filtered candidates lazily; callers opt into any traversal."""

        for index in range(self.filtered_support_size(grammar_filter)):
            yield self.decode_filtered(index, grammar_filter)

    def sample(
        self, rng: random.Random, grammar_filter: GrammarFilter | None = None
    ) -> CandidateGenome:
        support = self.filtered_support_size(grammar_filter)
        if support <= 0:
            raise ValueError("cannot sample an empty grammar filter")
        return self.decode_filtered(rng.randrange(support), grammar_filter)

    def mutate(
        self, parent: CandidateGenome, rng: random.Random
    ) -> tuple[CandidateGenome, MutationReceipt]:
        """Generate a legal child directly from a parent genome."""

        self.validate(parent)
        operations: list[tuple[str, tuple[object, ...]]] = []

        field_alternatives = tuple(
            value
            for value in self._field_representations
            if value != (parent.field_id, parent.representation_id)
        )
        if field_alternatives:
            operations.append(("MUTATE_FIELD_REPRESENTATION", field_alternatives))

        route_alternatives = tuple(
            (cell.primitive_id, parameters)
            for cell in self.cells_for_mechanism(parent.mechanism_family)
            for parameters in cell.parameter_options
            if (cell.primitive_id, parameters)
            != (
                parent.primitive_id,
                (parent.window, parent.long_window, parent.threshold),
            )
        )
        if route_alternatives:
            operations.append(("MUTATE_PRIMITIVE_ROUTE", route_alternatives))

        mechanism_alternatives = tuple(
            mechanism
            for mechanism in MECHANISM_FAMILIES
            if mechanism != parent.mechanism_family
            and (
                mechanism != SPARSE_EVENT_CARRY
                or parent.primitive_id in SPARSE_PRIMITIVES
            )
        )
        if mechanism_alternatives:
            operations.append(("MUTATE_MECHANISM_FAMILY", mechanism_alternatives))

        horizon_alternatives = tuple(
            value
            for value in self._target_horizons
            if value != parent.target_horizon_hours
        )
        if horizon_alternatives:
            operations.append(("MUTATE_TARGET_HORIZON", horizon_alternatives))

        if not operations:
            raise ValueError("parent has no legal mutation")
        operator, choices = operations[rng.randrange(len(operations))]
        choice = choices[rng.randrange(len(choices))]
        if operator == "MUTATE_FIELD_REPRESENTATION":
            field_id, representation_id = choice  # type: ignore[misc]
            child = replace(
                parent,
                field_id=str(field_id),
                representation_id=str(representation_id),
            )
        elif operator == "MUTATE_PRIMITIVE_ROUTE":
            primitive_id, parameters = choice  # type: ignore[misc]
            window, long_window, threshold = parameters
            child = replace(
                parent,
                primitive_id=str(primitive_id),
                window=window,
                long_window=long_window,
                threshold=threshold,
            )
        elif operator == "MUTATE_MECHANISM_FAMILY":
            child = replace(parent, mechanism_family=str(choice))
        else:
            child = replace(parent, target_horizon_hours=int(choice))

        self.validate(child)
        changed = _changed_genes(parent, child)
        if not changed or child.candidate_id == parent.candidate_id:
            raise AssertionError("mutation failed to create a structurally distinct child")
        receipt = MutationReceipt(
            operator=operator,
            parent_id=parent.candidate_id,
            child_id=child.candidate_id,
            changed_genes=changed,
            parent_genome=parent.canonical_dict(),
            child_genome=child.canonical_dict(),
        )
        return child, receipt


__all__ = [
    "CANONICAL_PRIMITIVE_IDS",
    "CROSS_SECTIONAL_RELATIVE",
    "DIRECTIONAL_STATEFUL",
    "FROZEN_FIELD_SPECS",
    "FROZEN_RELEASE_FIELDS",
    "FieldSpec",
    "FrozenGrammar",
    "GENOME_GENE_FIELDS",
    "GrammarCell",
    "GrammarFilter",
    "MECHANISM_FAMILIES",
    "MECHANISM_MAPPING",
    "MINIMUM_SUPPORT_SIZE",
    "PRIMITIVE_PARAMETER_OPTIONS",
    "RepresentationSpec",
    "SPARSE_EVENT_CARRY",
    "SPARSE_PRIMITIVES",
    "TARGET_HORIZONS_HOURS",
    "WINDOWLESS_PRIMITIVES",
]
