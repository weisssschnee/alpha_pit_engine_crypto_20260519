from __future__ import annotations

import numpy as np
import pytest

from alphafactory_crypto.broad_search.audit import FIELD_CONTRACTS, qualify_data_mode
from alphafactory_crypto.broad_search.expression import (
    Expression,
    FieldContract,
    TypedExpressionRegistry,
    ablate_expression,
    materialize_expression,
)


def test_unit_incompatible_add_is_rejected() -> None:
    registry = TypedExpressionRegistry(FIELD_CONTRACTS)
    expression = Expression(
        "SafeAdd", (Expression.raw("notional"), Expression.raw("trade_count"))
    )
    with pytest.raises(ValueError, match="incompatible units"):
        registry.validate(expression)


def test_flow_per_notional_is_lazy_and_matched_ablation_removes_interaction() -> None:
    registry = TypedExpressionRegistry(FIELD_CONTRACTS)
    expression = Expression(
        "FlowPerNotional",
        (Expression.raw("signed_aggressor_notional"), Expression.raw("notional")),
    )
    calls: list[str] = []
    fields = {
        "signed_aggressor_notional": np.array([[2.0, -4.0], [1.0, 3.0]]),
        "notional": np.array([[4.0, 8.0], [2.0, 6.0]]),
    }

    values = materialize_expression(
        expression,
        registry=registry,
        field_reader=lambda name: calls.append(name) or fields[name],
    )

    assert calls == ["signed_aggressor_notional", "notional"]
    assert np.allclose(values, [[0.5, -0.5], [0.5, 0.5]])
    control = ablate_expression(expression)
    assert control.operator == "SupportMatchedPayload"
    assert registry.validate(control).raw_fields == registry.validate(expression).raw_fields


def test_division_preserves_missing_denominator_support() -> None:
    registry = TypedExpressionRegistry(
        (
            FieldContract("numerator", "RATIO", "dimensionless"),
            FieldContract("denominator", "RATIO", "dimensionless"),
        )
    )
    expression = Expression(
        "SafeDiv",
        (Expression.raw("numerator"), Expression.raw("denominator")),
    )
    fields = {
        "numerator": np.array([[2.0, 3.0, 4.0]]),
        "denominator": np.array([[2.0, np.nan, 0.0]]),
    }

    values = materialize_expression(
        expression,
        registry=registry,
        field_reader=fields.__getitem__,
    )

    assert values[0, 0] == 1.0
    assert np.isnan(values[0, 1])
    assert np.isfinite(values[0, 2])


def test_condition_gate_preserves_both_child_support() -> None:
    registry = TypedExpressionRegistry(
        (
            FieldContract("payload", "RATIO", "dimensionless"),
            FieldContract("state", "STATE", "dimensionless"),
        )
    )
    expression = Expression(
        "ConditionGate",
        (Expression.raw("payload"), Expression.raw("state")),
        parameters={"threshold": 0.0},
    )
    fields = {
        "payload": np.array([[1.0, 2.0, np.nan, 4.0]]),
        "state": np.array([[1.0, -1.0, -1.0, np.nan]]),
    }

    values = materialize_expression(
        expression,
        registry=registry,
        field_reader=fields.__getitem__,
    )

    assert values[0, 0] == 1.0
    assert values[0, 1] == 0.0
    assert np.isnan(values[0, 2])
    assert np.isnan(values[0, 3])


def test_data_gate_does_not_promote_six_month_archive() -> None:
    import pandas as pd

    months = [f"2023-{value:02d}" for value in range(7, 13)]
    coverage = pd.DataFrame(
        [
            {
                "asset": f"A{asset}",
                "month": month,
                "source_family": "OFFICIAL_BINANCE_VISION_1M_KLINE_AGGREGATED_FLOW",
                "missing_rate_calendar": 0.0,
                "native_aggtrades_available": False,
            }
            for asset in range(50)
            for month in months
        ]
        + [
            {
                "asset": f"C{asset}",
                "month": month,
                "source_family": "NATIVE_AGGTRADES_CORE10_DEVELOPMENT",
                "missing_rate_calendar": 0.0,
                "native_aggtrades_available": True,
            }
            for asset in range(10)
            for month in months
        ]
    )
    eligibility = pd.DataFrame(
        [{"pit_qualified": False} for _ in range(50 * len(months))]
    )

    result = qualify_data_mode(coverage, eligibility)

    assert result["qualified_mode"] is None
    assert result["gate_result"] == "CRYPTO_DATA_UNIVERSE_NOT_RESEARCH_QUALIFIED"
    assert "TIME_HISTORY_TOO_SHORT" in result["failure_classes"]
    assert "SURVIVORSHIP_OR_ELIGIBILITY_UNRESOLVED" in result["failure_classes"]


def test_trailing_scale_has_no_future_influence() -> None:
    registry = TypedExpressionRegistry(FIELD_CONTRACTS)
    expression = Expression(
        "NotionalScale",
        (Expression.raw("notional"),),
        parameters={"window": 2},
    )
    original = np.array([[1.0, 2.0, 3.0, 4.0]])
    changed_future = np.array([[1.0, 2.0, 3.0, 4000.0]])

    left = materialize_expression(
        expression, registry=registry, field_reader=lambda _: original
    )
    right = materialize_expression(
        expression, registry=registry, field_reader=lambda _: changed_future
    )

    assert np.allclose(left[:, :3], right[:, :3], equal_nan=True)
    assert not np.allclose(left[:, 3:], right[:, 3:])
