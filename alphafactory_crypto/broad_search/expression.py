"""Small unit-, domain-, and PIT-aware compositional expression DAG.

This is an experimental representation surface.  It is deliberately separate
from the accepted single-field canary grammar and cannot authorize a search.
Expressions are materialized lazily from field readers; no derived full panel
is persisted or precomputed.
"""

from __future__ import annotations

import hashlib
import json
import warnings
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Sequence

import numpy as np

from alphafactory_crypto.instrument_canary.grammar import (
    PRIMITIVE_PARAMETER_OPTIONS,
)
from alphafactory_crypto.instrument_capability.primitives import (
    CANONICAL_PRIMITIVES,
    evaluate_primitive,
)


VALUE_TYPES = frozenset(
    {
        "COUNT",
        "VOLUME",
        "NOTIONAL",
        "PRICE",
        "RETURN",
        "BPS",
        "SIGNED_FLOW",
        "RATIO",
        "UNIT_INTERVAL",
        "VOLATILITY",
        "STATE",
        "EVENT",
        "AGE",
    }
)

NORMALIZERS = frozenset(
    {
        "Log",
        "SignedLog",
        "RollingZScore",
        "CrossSectionalRank",
        "RobustScale",
        "VolatilityScale",
        "NotionalScale",
        "TradeCountScale",
        "HistoricalPercentile",
        "CrossSectionalRobustZScore",
    }
)

CANONICAL_TEMPORAL_PRIMITIVE_IDS_V1 = frozenset(
    {
        "Delta",
        "Acceleration",
        "Persistence",
        "Transition",
        "EventWindow",
        "MultiScaleRelation",
    }
)
CANONICAL_PRIMITIVE_OPERATOR = "CanonicalPrimitive"
TEMPORAL_PROGRAM_COMPONENT_AUTHORITY_V1 = "TEMPORAL_MECHANISM_PROGRAM_V1"

BINARY_OPERATORS = frozenset(
    {
        "SafeAdd",
        "SafeSub",
        "SafeMul",
        "SafeDiv",
        "NormalizedDifference",
        "Residual",
        "FlowPerTrade",
        "FlowPerNotional",
        "PriceImpactRatio",
        "ShortMinusLong",
        "ConditionGate",
        "CrossAssetRelative",
        "RatioInteraction",
        "StateModulation",
    }
)

CONTROL_OPERATORS = frozenset({"SupportMatchedPayload"})

CONDITION_GATE_MODES = frozenset(
    {
        "POSITIVE",
        "NEGATIVE",
        "SIGN_CONFIRMATION",
        "SIGN_DISAGREEMENT",
    }
)

STATE_MODULATION_MODES = frozenset(
    {
        "SIGNED_LINEAR",
        "ABSOLUTE_MAGNITUDE",
        "POSITIVE_MAGNITUDE",
        "NEGATIVE_MAGNITUDE",
        "SIGN_ROUTING",
    }
)


@dataclass(frozen=True, slots=True)
class FieldContract:
    field_id: str
    value_type: str
    unit: str
    observable_lag_hours: int = 1
    pit_authority: str = "SOURCE_OBSERVABLE_TIME"

    def __post_init__(self) -> None:
        if self.value_type not in VALUE_TYPES:
            raise ValueError(f"unknown value type: {self.value_type}")
        if not self.field_id or not self.unit:
            raise ValueError("field contract requires identity and unit")
        if self.observable_lag_hours < 0:
            raise ValueError("observable lag must be non-negative")


@dataclass(frozen=True, slots=True)
class Expression:
    operator: str
    inputs: tuple["Expression", ...] = ()
    field_id: str | None = None
    parameters: Mapping[str, float | int | str | None] = field(default_factory=dict)

    @classmethod
    def raw(cls, field_id: str) -> "Expression":
        return cls("Raw", field_id=field_id)

    def canonical_dict(self) -> dict[str, Any]:
        return {
            "operator": self.operator,
            "field_id": self.field_id,
            "parameters": dict(sorted(self.parameters.items())),
            "inputs": [value.canonical_dict() for value in self.inputs],
        }

    @property
    def expression_id(self) -> str:
        payload = json.dumps(
            self.canonical_dict(), sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        return hashlib.sha256(payload).hexdigest().upper()


@dataclass(frozen=True, slots=True)
class ExpressionAssurance:
    value_type: str
    unit: str
    depth: int
    raw_fields: tuple[str, ...]
    rolling_windows: tuple[int, ...]
    cross_asset_normalizations: int
    regime_gates: int
    observable_lag_hours: int


class CanonicalTemporalPrimitiveAdapterV1:
    """Thin typed adapter over the existing canonical primitive authority."""

    PARAMETER_KEYS = frozenset(
        {"primitive_id", "window", "long_window", "threshold"}
    )

    @classmethod
    def normalized_parameters(
        cls, parameters: Mapping[str, Any]
    ) -> tuple[str, int | None, int | None, float | None]:
        if set(parameters) != cls.PARAMETER_KEYS:
            raise ValueError("CanonicalPrimitive parameters must be exact")
        primitive_id = str(parameters["primitive_id"])
        if primitive_id not in CANONICAL_TEMPORAL_PRIMITIVE_IDS_V1:
            raise ValueError("primitive is outside the temporal V1 search binding")
        if primitive_id not in CANONICAL_PRIMITIVES:
            raise ValueError("primitive is absent from canonical authority")

        def optional_int(value: Any) -> int | None:
            return None if value is None else int(value)

        def optional_float(value: Any) -> float | None:
            return None if value is None else float(value)

        window = optional_int(parameters["window"])
        long_window = optional_int(parameters["long_window"])
        threshold = optional_float(parameters["threshold"])
        coordinate = (window, long_window, threshold)
        if coordinate not in PRIMITIVE_PARAMETER_OPTIONS[primitive_id]:
            raise ValueError("primitive parameters are outside canonical authority")
        return primitive_id, window, long_window, threshold

    @classmethod
    def expression(
        cls,
        source: Expression,
        *,
        primitive_id: str,
        window: int | None,
        long_window: int | None,
        threshold: float | None,
    ) -> Expression:
        parameters = {
            "primitive_id": str(primitive_id),
            "window": None if window is None else int(window),
            "long_window": None if long_window is None else int(long_window),
            "threshold": None if threshold is None else float(threshold),
        }
        cls.normalized_parameters(parameters)
        return Expression(
            CANONICAL_PRIMITIVE_OPERATOR,
            (source,),
            parameters=parameters,
        )

    @staticmethod
    def effective_window_widths(
        primitive_id: str,
        window: int | None,
        long_window: int | None,
    ) -> tuple[int, ...]:
        if primitive_id == "Delta":
            assert window is not None
            return (window + 1,)
        if primitive_id == "Acceleration":
            assert window is not None
            return (2 * window + 1,)
        if primitive_id in {"Persistence", "EventWindow"}:
            assert window is not None
            return (window,)
        if primitive_id == "MultiScaleRelation":
            assert window is not None and long_window is not None
            return (window, long_window)
        return ()

    @staticmethod
    def output_contract(
        primitive_id: str, child: ExpressionAssurance
    ) -> tuple[str, str]:
        if primitive_id in {"Delta", "Acceleration", "MultiScaleRelation"}:
            return child.value_type, child.unit
        if primitive_id == "Persistence":
            return "UNIT_INTERVAL", "dimensionless"
        if primitive_id == "Transition":
            return "EVENT", "dimensionless"
        if primitive_id == "EventWindow":
            return "COUNT", "dimensionless"
        raise AssertionError(primitive_id)

    @staticmethod
    def materialize(
        values: np.ndarray,
        *,
        primitive_id: str,
        window: int | None,
        long_window: int | None,
        threshold: float | None,
    ) -> np.ndarray:
        return evaluate_primitive(
            primitive_id,
            values,
            window=1 if window is None else int(window),
            long_window=1 if long_window is None else int(long_window),
            threshold=0.0 if threshold is None else float(threshold),
        )


class TemporalProgramComponentAdapterV1:
    """Typed binding for canonical primitives used as program components.

    Unlike the V1 one-axis adapter, this binding is not coupled to the old
    aggTrades canary parameter table.  The program compiler owns the frozen,
    role-aware coordinate domain; this layer independently enforces canonical
    primitive identity, parameter shape, and numeric safety.
    """

    PARAMETER_KEYS = frozenset(
        {"authority", "primitive_id", "window", "long_window", "threshold"}
    )
    WINDOW_PRIMITIVES = frozenset(
        {"Delta", "Slope", "Acceleration", "Persistence", "PathShape", "EventWindow"}
    )
    WINDOWLESS_PRIMITIVES = frozenset(
        {"Duration", "StateAge", "TimeSince", "Transition", "FirstHit", "LastHit"}
    )

    @classmethod
    def normalized_parameters(
        cls, parameters: Mapping[str, Any]
    ) -> tuple[str, int | None, int | None, float | None]:
        if set(parameters) != cls.PARAMETER_KEYS:
            raise ValueError("Temporal program component parameters must be exact")
        if str(parameters["authority"]) != TEMPORAL_PROGRAM_COMPONENT_AUTHORITY_V1:
            raise ValueError("temporal program component authority changed")
        primitive_id = str(parameters["primitive_id"])
        if primitive_id not in CANONICAL_PRIMITIVES:
            raise ValueError("temporal program component is not canonical")

        def optional_int(value: Any) -> int | None:
            if value is None:
                return None
            result = int(value)
            if result <= 0:
                raise ValueError("temporal program windows must be positive")
            return result

        def optional_float(value: Any) -> float | None:
            if value is None:
                return None
            result = float(value)
            if not np.isfinite(result):
                raise ValueError("temporal program threshold must be finite")
            return result

        window = optional_int(parameters["window"])
        long_window = optional_int(parameters["long_window"])
        threshold = optional_float(parameters["threshold"])
        if primitive_id == "MultiScaleRelation":
            if window is None or long_window is None or window >= long_window:
                raise ValueError("MultiScaleRelation requires short window < long window")
        elif primitive_id in cls.WINDOW_PRIMITIVES:
            if window is None or long_window is not None:
                raise ValueError(f"{primitive_id} requires one window")
            if primitive_id == "PathShape" and window < 3:
                raise ValueError("PathShape requires window >= 3")
        elif primitive_id in cls.WINDOWLESS_PRIMITIVES:
            if window is not None or long_window is not None:
                raise ValueError(f"{primitive_id} does not accept a window")
        else:  # pragma: no cover - canonical authority and sets move together
            raise ValueError("unsupported temporal program primitive")
        return primitive_id, window, long_window, threshold

    @classmethod
    def expression(
        cls,
        source: Expression,
        *,
        primitive_id: str,
        window: int | None = None,
        long_window: int | None = None,
        threshold: float | None = None,
    ) -> Expression:
        parameters = {
            "authority": TEMPORAL_PROGRAM_COMPONENT_AUTHORITY_V1,
            "primitive_id": str(primitive_id),
            "window": None if window is None else int(window),
            "long_window": None if long_window is None else int(long_window),
            "threshold": None if threshold is None else float(threshold),
        }
        cls.normalized_parameters(parameters)
        return Expression(CANONICAL_PRIMITIVE_OPERATOR, (source,), parameters=parameters)

    @staticmethod
    def effective_window_widths(
        primitive_id: str,
        window: int | None,
        long_window: int | None,
    ) -> tuple[int, ...]:
        if primitive_id == "Delta":
            assert window is not None
            return (window + 1,)
        if primitive_id == "Acceleration":
            assert window is not None
            return (2 * window + 1,)
        if primitive_id in {"Slope", "Persistence", "PathShape", "EventWindow"}:
            assert window is not None
            return (window,)
        if primitive_id == "MultiScaleRelation":
            assert window is not None and long_window is not None
            return (window, long_window)
        return ()

    @staticmethod
    def output_contract(
        primitive_id: str, child: ExpressionAssurance
    ) -> tuple[str, str]:
        if primitive_id in {
            "Delta",
            "Slope",
            "Acceleration",
            "PathShape",
            "MultiScaleRelation",
        }:
            return child.value_type, child.unit
        if primitive_id == "Persistence":
            return "UNIT_INTERVAL", "dimensionless"
        if primitive_id in {"Duration", "StateAge", "TimeSince", "LastHit"}:
            return "AGE", "dimensionless"
        if primitive_id in {"Transition", "FirstHit"}:
            return "EVENT", "dimensionless"
        if primitive_id == "EventWindow":
            return "COUNT", "dimensionless"
        raise AssertionError(primitive_id)

    @staticmethod
    def materialize(
        values: np.ndarray,
        *,
        primitive_id: str,
        window: int | None,
        long_window: int | None,
        threshold: float | None,
    ) -> np.ndarray:
        return evaluate_primitive(
            primitive_id,
            values,
            window=1 if window is None else int(window),
            long_window=1 if long_window is None else int(long_window),
            threshold=0.0 if threshold is None else float(threshold),
        )


def _canonical_primitive_adapter(
    parameters: Mapping[str, Any],
) -> type[CanonicalTemporalPrimitiveAdapterV1] | type[TemporalProgramComponentAdapterV1]:
    if set(parameters) == CanonicalTemporalPrimitiveAdapterV1.PARAMETER_KEYS:
        return CanonicalTemporalPrimitiveAdapterV1
    if set(parameters) == TemporalProgramComponentAdapterV1.PARAMETER_KEYS:
        return TemporalProgramComponentAdapterV1
    raise ValueError("CanonicalPrimitive parameters do not match an authority")


def _same_unit(left: ExpressionAssurance, right: ExpressionAssurance) -> None:
    if left.unit != right.unit:
        raise ValueError(f"incompatible units: {left.unit} and {right.unit}")


class TypedExpressionRegistry:
    """Validate bounded expression DAGs without authorizing their execution."""

    MAX_DEPTH = 4
    MAX_RAW_INPUTS = 4
    MAX_ROLLING_WINDOWS = 3
    MAX_CROSS_ASSET_NORMALIZATIONS = 1
    # One AB confirmation/disagreement gate may be nested under one frozen
    # third-axis regime operator without changing the existing AST shape.
    MAX_REGIME_GATES = 2

    def __init__(
        self,
        fields: Sequence[FieldContract],
        *,
        max_depth: int | None = None,
        max_raw_inputs: int | None = None,
        max_rolling_windows: int | None = None,
        max_canonical_primitive_nodes: int = 1,
        max_cross_asset_normalizations: int | None = None,
        max_regime_gates: int | None = None,
    ) -> None:
        self.fields = {item.field_id: item for item in fields}
        if not self.fields or len(self.fields) != len(tuple(fields)):
            raise ValueError("field contracts must be non-empty and unique")
        self.max_depth = self.MAX_DEPTH if max_depth is None else int(max_depth)
        self.max_raw_inputs = (
            self.MAX_RAW_INPUTS if max_raw_inputs is None else int(max_raw_inputs)
        )
        self.max_rolling_windows = (
            None if max_rolling_windows is None else int(max_rolling_windows)
        )
        self.max_canonical_primitive_nodes = int(max_canonical_primitive_nodes)
        self.max_cross_asset_normalizations = (
            self.MAX_CROSS_ASSET_NORMALIZATIONS
            if max_cross_asset_normalizations is None
            else int(max_cross_asset_normalizations)
        )
        self.max_regime_gates = (
            self.MAX_REGIME_GATES if max_regime_gates is None else int(max_regime_gates)
        )
        if min(
            self.max_depth,
            self.max_raw_inputs,
            self.max_canonical_primitive_nodes,
            self.max_cross_asset_normalizations,
            self.max_regime_gates,
        ) < 0 or self.max_depth < 1 or self.max_raw_inputs < 1:
            raise ValueError("expression registry limits are invalid")
        if self.max_rolling_windows is not None and self.max_rolling_windows < 0:
            raise ValueError("expression rolling-window limit is invalid")

    def validate(self, expression: Expression) -> ExpressionAssurance:
        assurance = self._validate(expression)
        temporal_nodes = self._operator_count(
            expression, CANONICAL_PRIMITIVE_OPERATOR
        )
        if temporal_nodes > self.max_canonical_primitive_nodes:
            raise ValueError(
                "expression uses more than one canonical primitive"
                if self.max_canonical_primitive_nodes == 1
                else "expression uses too many canonical primitives"
            )
        if assurance.depth > self.max_depth:
            raise ValueError("expression depth exceeds its frozen limit")
        if not 1 <= len(assurance.raw_fields) <= self.max_raw_inputs:
            raise ValueError("expression must use one to four raw inputs")
        rolling_limit = (
            self.MAX_ROLLING_WINDOWS + (1 if temporal_nodes else 0)
            if self.max_rolling_windows is None
            else self.max_rolling_windows
        )
        if len(assurance.rolling_windows) > rolling_limit:
            raise ValueError("expression exceeds its rolling-window limit")
        if assurance.cross_asset_normalizations > self.max_cross_asset_normalizations:
            raise ValueError("expression uses more than one cross-asset normalization")
        if assurance.regime_gates > self.max_regime_gates:
            raise ValueError("expression uses more than one regime gate")
        return assurance

    @staticmethod
    def _operator_count(expression: Expression, operator: str) -> int:
        return int(expression.operator == operator) + sum(
            TypedExpressionRegistry._operator_count(child, operator)
            for child in expression.inputs
        )

    def _validate(self, expression: Expression) -> ExpressionAssurance:
        if expression.operator == "Raw":
            if expression.inputs or not expression.field_id:
                raise ValueError("Raw requires exactly one field identity")
            try:
                source = self.fields[expression.field_id]
            except KeyError as error:
                raise ValueError(f"unregistered raw field: {expression.field_id}") from error
            return ExpressionAssurance(
                source.value_type,
                source.unit,
                1,
                (source.field_id,),
                (),
                0,
                0,
                source.observable_lag_hours,
            )

        if expression.field_id is not None:
            raise ValueError("non-Raw nodes cannot carry field_id")
        children = tuple(self._validate(value) for value in expression.inputs)
        if expression.operator == CANONICAL_PRIMITIVE_OPERATOR:
            if len(children) != 1:
                raise ValueError("CanonicalPrimitive requires one input")
            child = children[0]
            adapter = _canonical_primitive_adapter(expression.parameters)
            primitive_id, window, long_window, threshold = adapter.normalized_parameters(
                expression.parameters
            )
            output_type, output_unit = (
                adapter.output_contract(primitive_id, child)
            )
            widths = adapter.effective_window_widths(
                primitive_id, window, long_window
            )
            return ExpressionAssurance(
                output_type,
                output_unit,
                child.depth + 1,
                child.raw_fields,
                (*child.rolling_windows, *widths),
                child.cross_asset_normalizations,
                child.regime_gates,
                child.observable_lag_hours,
            )
        if expression.operator in NORMALIZERS:
            if len(children) != 1:
                raise ValueError(f"{expression.operator} requires one input")
            child = children[0]
            windows = child.rolling_windows
            cross_asset = child.cross_asset_normalizations
            if expression.operator == "Log" and child.value_type not in {
                "COUNT",
                "VOLUME",
                "NOTIONAL",
                "PRICE",
                "UNIT_INTERVAL",
                "VOLATILITY",
            }:
                raise ValueError("Log requires a non-negative or positive domain")
            if expression.operator in {
                "RollingZScore",
                "RobustScale",
                "VolatilityScale",
                "NotionalScale",
                "TradeCountScale",
                "HistoricalPercentile",
            }:
                window = int(expression.parameters.get("window", 0))
                if window < 2:
                    raise ValueError(f"{expression.operator} requires window >= 2")
                windows = (*windows, window)
            if expression.operator in {"CrossSectionalRank", "CrossSectionalRobustZScore"}:
                cross_asset += 1
            output_type = "RATIO" if expression.operator != "HistoricalPercentile" else "UNIT_INTERVAL"
            return ExpressionAssurance(
                output_type,
                "dimensionless",
                child.depth + 1,
                child.raw_fields,
                windows,
                cross_asset,
                child.regime_gates,
                child.observable_lag_hours,
            )

        if expression.operator not in BINARY_OPERATORS | CONTROL_OPERATORS or len(children) != 2:
            raise ValueError(f"unsupported or non-binary operator: {expression.operator}")
        left, right = children
        raw_fields = tuple(dict.fromkeys((*left.raw_fields, *right.raw_fields)))
        windows = (*left.rolling_windows, *right.rolling_windows)
        cross_asset = left.cross_asset_normalizations + right.cross_asset_normalizations
        gates = left.regime_gates + right.regime_gates
        output_type = "RATIO"
        output_unit = "dimensionless"

        if expression.operator in {"SafeAdd", "SafeSub", "ShortMinusLong"}:
            _same_unit(left, right)
            output_type, output_unit = left.value_type, left.unit
        elif expression.operator == "SafeMul":
            if "dimensionless" not in {left.unit, right.unit}:
                raise ValueError("SafeMul requires at least one dimensionless operand")
            selected = right if left.unit == "dimensionless" else left
            output_type, output_unit = selected.value_type, selected.unit
        elif expression.operator == "SafeDiv":
            output_unit = (
                "dimensionless"
                if left.unit == right.unit
                else f"{left.unit}/{right.unit}"
            )
        elif expression.operator == "NormalizedDifference":
            _same_unit(left, right)
        elif expression.operator == "FlowPerTrade":
            if left.value_type not in {"SIGNED_FLOW", "NOTIONAL", "VOLUME"} or right.value_type != "COUNT":
                raise ValueError("FlowPerTrade requires flow/notional/volume over count")
            output_unit = f"{left.unit}/trade"
        elif expression.operator == "FlowPerNotional":
            if left.value_type not in {"SIGNED_FLOW", "NOTIONAL"} or right.value_type != "NOTIONAL":
                raise ValueError("FlowPerNotional requires flow over notional")
        elif expression.operator == "PriceImpactRatio":
            if left.value_type not in {"BPS", "PRICE", "VOLATILITY"} or right.value_type not in {"SIGNED_FLOW", "NOTIONAL", "VOLUME", "RATIO"}:
                raise ValueError("PriceImpactRatio requires price response over flow")
        elif expression.operator == "Residual":
            if left.unit != right.unit and "dimensionless" not in {left.unit, right.unit}:
                raise ValueError("Residual inputs must be unit-compatible or normalized")
            output_type, output_unit = left.value_type, left.unit
        elif expression.operator == "ConditionGate":
            if right.value_type not in {
                "STATE",
                "EVENT",
                "COUNT",
                "RATIO",
                "UNIT_INTERVAL",
            }:
                raise ValueError("ConditionGate requires state-like second input")
            mode = str(expression.parameters.get("mode", "POSITIVE"))
            if mode not in CONDITION_GATE_MODES:
                raise ValueError("ConditionGate mode is outside the frozen grammar")
            output_type, output_unit = left.value_type, left.unit
            gates += 1
        elif expression.operator == "StateModulation":
            if left.unit != "dimensionless":
                raise ValueError("StateModulation payload must be normalized")
            if right.value_type not in {"STATE", "EVENT", "RATIO", "UNIT_INTERVAL", "AGE"}:
                raise ValueError("StateModulation requires state-like second input")
            mode = str(expression.parameters.get("mode", "SIGNED_LINEAR"))
            if mode not in STATE_MODULATION_MODES:
                raise ValueError("StateModulation mode is outside the frozen grammar")
            output_type, output_unit = left.value_type, left.unit
            gates += 1
        elif expression.operator == "RatioInteraction":
            if left.unit != "dimensionless" or right.unit != "dimensionless":
                raise ValueError("RatioInteraction requires dimensionless operands")
        elif expression.operator == "SupportMatchedPayload":
            output_type, output_unit = left.value_type, left.unit
        elif expression.operator == "CrossAssetRelative":
            _same_unit(left, right)
            if right.value_type not in {"RATIO", "UNIT_INTERVAL", "STATE", left.value_type}:
                raise ValueError("CrossAssetRelative requires comparable market context")
            output_type, output_unit = left.value_type, left.unit
            cross_asset += 1

        return ExpressionAssurance(
            output_type,
            output_unit,
            max(left.depth, right.depth) + 1,
            raw_fields,
            windows,
            cross_asset,
            gates,
            max(left.observable_lag_hours, right.observable_lag_hours),
        )

    def contract_payload(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "lifecycle": "EXPERIMENTAL",
            "authority": "NON_FORMAL_REPRESENTATION_ONLY",
            "limits": {
                "raw_inputs": [1, self.max_raw_inputs],
                "depth": [1, self.max_depth],
                "rolling_windows": (
                    self.MAX_ROLLING_WINDOWS
                    if self.max_rolling_windows is None
                    else self.max_rolling_windows
                ),
                "canonical_primitive_nodes": self.max_canonical_primitive_nodes,
                "cross_asset_normalizations": self.max_cross_asset_normalizations,
                "regime_gates": self.max_regime_gates,
            },
            "value_types": sorted(VALUE_TYPES),
            "normalizers": sorted(NORMALIZERS),
            "binary_operators": sorted(BINARY_OPERATORS),
            "control_operators": sorted(CONTROL_OPERATORS),
            "pit_rules": [
                "Every rolling operator uses the trailing window ending at t",
                "No normalizer may estimate scale from future coordinates",
                "Expression observable lag is the maximum lag of its raw inputs",
                "Cross-sectional transforms use only the current observable cross-section",
            ],
            "operator_contracts": {
                "Log": "non-negative or positive domain only",
                "NotionalScale": "trailing window required",
                "TradeCountScale": "trailing window required",
                "SafeAdd/SafeSub/NormalizedDifference": "matching units required",
                "SafeMul": "at least one dimensionless operand required",
                "SupportMatchedPayload": "control-only; left payload with right input retained in the support contract",
            },
            "fields": [
                {
                    "field_id": item.field_id,
                    "value_type": item.value_type,
                    "unit": item.unit,
                    "observable_lag_hours": item.observable_lag_hours,
                    "pit_authority": item.pit_authority,
                }
                for item in sorted(self.fields.values(), key=lambda value: value.field_id)
            ],
        }


def _rolling_view(values: np.ndarray, window: int, reducer: Callable[[np.ndarray], np.ndarray]) -> np.ndarray:
    output = np.full(values.shape, np.nan, dtype=float)
    for index in range(window - 1, values.shape[1]):
        output[:, index] = reducer(values[:, index - window + 1 : index + 1])
    return output


def _rolling_moments(values: np.ndarray, window: int) -> tuple[np.ndarray, np.ndarray]:
    """Trailing mean/std with a complete-window requirement and no future reads."""

    finite = np.isfinite(values)
    safe = np.where(finite, values, 0.0)
    count = np.pad(np.cumsum(finite, axis=1, dtype=np.int32), ((0, 0), (1, 0)))
    total = np.pad(np.cumsum(safe, axis=1, dtype=np.float64), ((0, 0), (1, 0)))
    square = np.pad(np.cumsum(safe * safe, axis=1, dtype=np.float64), ((0, 0), (1, 0)))
    rolling_count = count[:, window:] - count[:, :-window]
    rolling_total = total[:, window:] - total[:, :-window]
    rolling_square = square[:, window:] - square[:, :-window]
    mean = np.full(values.shape, np.nan, dtype=float)
    std = np.full(values.shape, np.nan, dtype=float)
    complete = rolling_count == window
    local_mean = rolling_total / float(window)
    local_variance = np.maximum(rolling_square / float(window) - local_mean * local_mean, 0.0)
    mean[:, window - 1 :] = np.where(complete, local_mean, np.nan)
    std[:, window - 1 :] = np.where(complete, np.sqrt(local_variance), np.nan)
    return mean, std


def _rolling_robust_scale(values: np.ndarray, window: int) -> tuple[np.ndarray, np.ndarray]:
    """Trailing median/IQR scale with a complete-window requirement."""

    import pandas as pd

    frame = pd.DataFrame(values.T)
    rolling = frame.rolling(window=window, min_periods=window)
    median = rolling.median().to_numpy(dtype=float).T
    q25 = rolling.quantile(0.25).to_numpy(dtype=float).T
    q75 = rolling.quantile(0.75).to_numpy(dtype=float).T
    return median, (q75 - q25) / 1.349


def _cross_sectional_rank(values: np.ndarray) -> np.ndarray:
    import pandas as pd

    ranks = pd.DataFrame(values).rank(axis=0, method="average", na_option="keep")
    count = np.isfinite(values).sum(axis=0)
    denominator = np.maximum(count - 1, 1)
    return (ranks.to_numpy(dtype=float) - 1.0) / denominator[None, :]


def _cross_sectional_robust_zscore(values: np.ndarray, epsilon: float) -> np.ndarray:
    # An all-ineligible timestamp is a valid dynamic-universe state.  NumPy's
    # all-NaN warning is therefore expected here and the output remains NaN.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        median = np.nanmedian(values, axis=0, keepdims=True)
        mad = np.nanmedian(np.abs(values - median), axis=0, keepdims=True)
    return (values - median) / np.maximum(1.4826 * mad, epsilon)


def materialize_expression(
    expression: Expression,
    *,
    registry: TypedExpressionRegistry,
    field_reader: Callable[[str], np.ndarray],
    eligible_mask: np.ndarray | None = None,
    candidate_cache: dict[str, np.ndarray] | None = None,
    epsilon: float = 1e-12,
) -> np.ndarray:
    """Lazily evaluate one validated DAG using only past/current observations."""

    registry.validate(expression)
    cache = candidate_cache if candidate_cache is not None else {}
    eligible = None if eligible_mask is None else np.asarray(eligible_mask, dtype=bool)

    def evaluate(node: Expression) -> np.ndarray:
        if node.expression_id in cache:
            return cache[node.expression_id]
        if node.operator == "Raw":
            result = np.asarray(field_reader(str(node.field_id)), dtype=float)
            if eligible is not None:
                if eligible.shape != result.shape:
                    raise ValueError("eligible mask and raw field shape mismatch")
                result = np.where(eligible, result, np.nan)
        else:
            children = [evaluate(value) for value in node.inputs]
            left = children[0]
            right = children[1] if len(children) == 2 else None
            raw_window = node.parameters.get("window", 0)
            window = 0 if raw_window is None else int(raw_window)
            if node.operator == "Log":
                result = np.log(np.maximum(left, epsilon))
            elif node.operator == "SignedLog":
                result = np.sign(left) * np.log1p(np.abs(left))
            elif node.operator == "RollingZScore":
                mean, std = _rolling_moments(left, window)
                result = (left - mean) / np.maximum(std, epsilon)
            elif node.operator == "RobustScale":
                median, scale = _rolling_robust_scale(left, window)
                result = (left - median) / np.maximum(scale, epsilon)
            elif node.operator == "VolatilityScale":
                _, scale = _rolling_moments(left, window)
                result = left / np.maximum(scale, epsilon)
            elif node.operator in {"NotionalScale", "TradeCountScale"}:
                scale, _ = _rolling_moments(np.abs(left), window)
                result = left / np.maximum(scale, epsilon)
            elif node.operator == "HistoricalPercentile":
                import pandas as pd

                result = (
                    pd.DataFrame(left.T)
                    .rolling(window=window, min_periods=window)
                    .rank(method="average", pct=True)
                    .to_numpy(dtype=float)
                    .T
                )
            elif node.operator == CANONICAL_PRIMITIVE_OPERATOR:
                adapter = _canonical_primitive_adapter(node.parameters)
                primitive_id, primitive_window, long_window, threshold = (
                    adapter.normalized_parameters(node.parameters)
                )
                result = adapter.materialize(
                    left,
                    primitive_id=primitive_id,
                    window=primitive_window,
                    long_window=long_window,
                    threshold=threshold,
                )
            elif node.operator == "CrossSectionalRank":
                result = _cross_sectional_rank(left)
            elif node.operator == "CrossSectionalRobustZScore":
                result = _cross_sectional_robust_zscore(left, epsilon)
            elif node.operator == "SafeAdd":
                result = left + right
            elif node.operator in {"SafeSub", "ShortMinusLong"}:
                result = left - right
            elif node.operator in {"SafeMul", "RatioInteraction"}:
                result = left * right
            elif node.operator in {"SafeDiv", "FlowPerTrade", "FlowPerNotional", "PriceImpactRatio"}:
                denominator = np.where(
                    np.isfinite(right),
                    np.where(
                        np.abs(right) > epsilon,
                        right,
                        np.where(right < 0, -epsilon, epsilon),
                    ),
                    np.nan,
                )
                result = left / denominator
            elif node.operator == "NormalizedDifference":
                result = (left - right) / (np.abs(left) + np.abs(right) + epsilon)
            elif node.operator == "Residual":
                beta = float(node.parameters.get("beta", 1.0))
                result = left - beta * right
            elif node.operator == "ConditionGate":
                threshold = float(node.parameters.get("threshold", 0.0))
                mode = str(node.parameters.get("mode", "POSITIVE"))
                finite_support = np.isfinite(left) & np.isfinite(right)
                if mode == "POSITIVE":
                    active = right > threshold
                elif mode == "NEGATIVE":
                    active = right < threshold
                elif mode == "SIGN_CONFIRMATION":
                    active = left * right > 0.0
                elif mode == "SIGN_DISAGREEMENT":
                    active = left * right < 0.0
                else:  # pragma: no cover - validator owns this branch
                    raise ValueError(mode)
                result = np.where(
                    finite_support,
                    np.where(active, left, 0.0),
                    np.nan,
                )
            elif node.operator == "StateModulation":
                mode = str(node.parameters.get("mode", "SIGNED_LINEAR"))
                if mode == "SIGNED_LINEAR":
                    multiplier = right
                elif mode == "ABSOLUTE_MAGNITUDE":
                    multiplier = np.abs(right)
                elif mode == "POSITIVE_MAGNITUDE":
                    multiplier = np.maximum(right, 0.0)
                elif mode == "NEGATIVE_MAGNITUDE":
                    multiplier = np.maximum(-right, 0.0)
                elif mode == "SIGN_ROUTING":
                    multiplier = np.where(right >= 0.0, 1.0, -1.0)
                else:  # pragma: no cover - validator owns this branch
                    raise ValueError(mode)
                result = left * multiplier
            elif node.operator == "CrossAssetRelative":
                result = left - _cross_sectional_robust_zscore(right, epsilon)
            elif node.operator == "SupportMatchedPayload":
                result = np.where(np.isfinite(right), left, np.nan)
            else:  # pragma: no cover - validator owns this branch
                raise ValueError(node.operator)
        if result.ndim != 2:
            raise ValueError("expression values must be [asset,time]")
        result = np.asarray(result, dtype=float)
        cache[node.expression_id] = result
        return result

    return evaluate(expression)


def ablate_expression(expression: Expression) -> Expression:
    """Remove one core interaction while preserving the raw-input surface."""

    if expression.operator in {
        "PriceImpactRatio",
        "FlowPerTrade",
        "FlowPerNotional",
        "SafeDiv",
        "SafeMul",
        "RatioInteraction",
        "StateModulation",
        "CrossAssetRelative",
        "ConditionGate",
    }:
        return Expression("SupportMatchedPayload", expression.inputs)
    if expression.operator in {"NormalizedDifference", "Residual", "SafeSub", "ShortMinusLong"}:
        return Expression("SupportMatchedPayload", expression.inputs)
    raise ValueError("expression has no registered matched ablation")


__all__ = [
    "BINARY_OPERATORS",
    "CANONICAL_PRIMITIVE_OPERATOR",
    "CANONICAL_TEMPORAL_PRIMITIVE_IDS_V1",
    "CanonicalTemporalPrimitiveAdapterV1",
    "TemporalProgramComponentAdapterV1",
    "TEMPORAL_PROGRAM_COMPONENT_AUTHORITY_V1",
    "CONDITION_GATE_MODES",
    "CONTROL_OPERATORS",
    "NORMALIZERS",
    "STATE_MODULATION_MODES",
    "VALUE_TYPES",
    "Expression",
    "ExpressionAssurance",
    "FieldContract",
    "TypedExpressionRegistry",
    "ablate_expression",
    "materialize_expression",
]
