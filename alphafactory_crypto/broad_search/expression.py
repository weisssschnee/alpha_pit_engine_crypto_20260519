"""Small unit-, domain-, and PIT-aware compositional expression DAG.

This is an experimental representation surface.  It is deliberately separate
from the accepted single-field canary grammar and cannot authorize a search.
Expressions are materialized lazily from field readers; no derived full panel
is persisted or precomputed.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Sequence

import numpy as np


VALUE_TYPES = frozenset(
    {
        "COUNT",
        "VOLUME",
        "NOTIONAL",
        "PRICE",
        "BPS",
        "SIGNED_FLOW",
        "RATIO",
        "UNIT_INTERVAL",
        "VOLATILITY",
        "STATE",
        "EVENT",
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
    }
)

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
    parameters: Mapping[str, float | int | str] = field(default_factory=dict)

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


def _same_unit(left: ExpressionAssurance, right: ExpressionAssurance) -> None:
    if left.unit != right.unit:
        raise ValueError(f"incompatible units: {left.unit} and {right.unit}")


class TypedExpressionRegistry:
    """Validate bounded expression DAGs without authorizing their execution."""

    MAX_DEPTH = 4
    MAX_RAW_INPUTS = 4
    MAX_ROLLING_WINDOWS = 3
    MAX_CROSS_ASSET_NORMALIZATIONS = 1
    MAX_REGIME_GATES = 1

    def __init__(self, fields: Sequence[FieldContract]) -> None:
        self.fields = {item.field_id: item for item in fields}
        if not self.fields or len(self.fields) != len(tuple(fields)):
            raise ValueError("field contracts must be non-empty and unique")

    def validate(self, expression: Expression) -> ExpressionAssurance:
        assurance = self._validate(expression)
        if assurance.depth > self.MAX_DEPTH:
            raise ValueError("expression depth exceeds four")
        if not 1 <= len(assurance.raw_fields) <= self.MAX_RAW_INPUTS:
            raise ValueError("expression must use one to four raw inputs")
        if len(assurance.rolling_windows) > self.MAX_ROLLING_WINDOWS:
            raise ValueError("expression uses more than three rolling windows")
        if assurance.cross_asset_normalizations > self.MAX_CROSS_ASSET_NORMALIZATIONS:
            raise ValueError("expression uses more than one cross-asset normalization")
        if assurance.regime_gates > self.MAX_REGIME_GATES:
            raise ValueError("expression uses more than one regime gate")
        return assurance

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
            if expression.operator == "CrossSectionalRank":
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

        if expression.operator not in BINARY_OPERATORS or len(children) != 2:
            raise ValueError(f"unsupported or non-binary operator: {expression.operator}")
        left, right = children
        raw_fields = tuple(dict.fromkeys((*left.raw_fields, *right.raw_fields)))
        windows = tuple(dict.fromkeys((*left.rolling_windows, *right.rolling_windows)))
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
            if right.value_type not in {"STATE", "EVENT", "RATIO", "UNIT_INTERVAL"}:
                raise ValueError("ConditionGate requires state-like second input")
            output_type, output_unit = left.value_type, left.unit
            gates += 1
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
                "raw_inputs": [1, self.MAX_RAW_INPUTS],
                "depth": [1, self.MAX_DEPTH],
                "rolling_windows": self.MAX_ROLLING_WINDOWS,
                "cross_asset_normalizations": self.MAX_CROSS_ASSET_NORMALIZATIONS,
                "regime_gates": self.MAX_REGIME_GATES,
            },
            "value_types": sorted(VALUE_TYPES),
            "normalizers": sorted(NORMALIZERS),
            "binary_operators": sorted(BINARY_OPERATORS),
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


def _cross_sectional_rank(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, axis=0, kind="mergesort")
    ranks = np.argsort(order, axis=0, kind="mergesort").astype(float)
    return ranks / max(1, values.shape[0] - 1)


def materialize_expression(
    expression: Expression,
    *,
    registry: TypedExpressionRegistry,
    field_reader: Callable[[str], np.ndarray],
    epsilon: float = 1e-12,
) -> np.ndarray:
    """Lazily evaluate one validated DAG using only past/current observations."""

    registry.validate(expression)
    cache: dict[str, np.ndarray] = {}

    def evaluate(node: Expression) -> np.ndarray:
        if node.expression_id in cache:
            return cache[node.expression_id]
        if node.operator == "Raw":
            result = np.asarray(field_reader(str(node.field_id)), dtype=float)
        else:
            children = [evaluate(value) for value in node.inputs]
            left = children[0]
            right = children[1] if len(children) == 2 else None
            window = int(node.parameters.get("window", 0))
            if node.operator == "Log":
                result = np.log(np.maximum(left, epsilon))
            elif node.operator == "SignedLog":
                result = np.sign(left) * np.log1p(np.abs(left))
            elif node.operator == "RollingZScore":
                mean = _rolling_view(left, window, lambda x: np.mean(x, axis=1))
                std = _rolling_view(left, window, lambda x: np.std(x, axis=1))
                result = (left - mean) / np.maximum(std, epsilon)
            elif node.operator == "RobustScale":
                median = _rolling_view(left, window, lambda x: np.median(x, axis=1))
                mad = _rolling_view(left, window, lambda x: np.median(np.abs(x - np.median(x, axis=1, keepdims=True)), axis=1))
                result = (left - median) / np.maximum(1.4826 * mad, epsilon)
            elif node.operator == "VolatilityScale":
                scale = _rolling_view(left, window, lambda x: np.std(x, axis=1))
                result = left / np.maximum(scale, epsilon)
            elif node.operator in {"NotionalScale", "TradeCountScale"}:
                scale = _rolling_view(left, window, lambda x: np.mean(np.abs(x), axis=1))
                result = left / np.maximum(scale, epsilon)
            elif node.operator == "HistoricalPercentile":
                result = _rolling_view(left, window, lambda x: np.mean(x <= x[:, -1:], axis=1))
            elif node.operator == "CrossSectionalRank":
                result = _cross_sectional_rank(left)
            elif node.operator == "SafeAdd":
                result = left + right
            elif node.operator in {"SafeSub", "ShortMinusLong"}:
                result = left - right
            elif node.operator == "SafeMul":
                result = left * right
            elif node.operator in {"SafeDiv", "FlowPerTrade", "FlowPerNotional", "PriceImpactRatio"}:
                result = left / np.where(np.abs(right) > epsilon, right, np.where(right < 0, -epsilon, epsilon))
            elif node.operator == "NormalizedDifference":
                result = (left - right) / (np.abs(left) + np.abs(right) + epsilon)
            elif node.operator == "Residual":
                beta = float(node.parameters.get("beta", 1.0))
                result = left - beta * right
            elif node.operator == "ConditionGate":
                threshold = float(node.parameters.get("threshold", 0.0))
                result = np.where(right > threshold, left, 0.0)
            elif node.operator == "CrossAssetRelative":
                result = left - np.nanmedian(right, axis=0, keepdims=True)
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
        "SafeMul",
        "CrossAssetRelative",
        "ConditionGate",
    }:
        return expression.inputs[0]
    if expression.operator == "NormalizedDifference":
        return Expression("SafeSub", expression.inputs)
    if expression.operator == "Residual":
        return expression.inputs[0]
    raise ValueError("expression has no registered matched ablation")


__all__ = [
    "BINARY_OPERATORS",
    "NORMALIZERS",
    "VALUE_TYPES",
    "Expression",
    "ExpressionAssurance",
    "FieldContract",
    "TypedExpressionRegistry",
    "ablate_expression",
    "materialize_expression",
]
