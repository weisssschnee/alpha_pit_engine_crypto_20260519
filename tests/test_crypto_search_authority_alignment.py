from __future__ import annotations

import numpy as np
import pytest

from alphafactory_crypto.broad_search.audit import (
    freeze_search_behavior_contract,
    search_behavior_descriptor,
    turnover_path,
)
from alphafactory_crypto.broad_search.compositional18m import CandidateSpec
from alphafactory_crypto.broad_search.expression import (
    Expression,
    FieldContract,
    TypedExpressionRegistry,
    ablate_expression,
    materialize_expression,
)
from alphafactory_crypto.broad_search.pair18m import _series_metrics, evaluate_pair
from alphafactory_crypto.instrument_capability.mapping import (
    CROSS_SECTIONAL_ZERO_NET,
    DEFAULT_MAPPING_CONTRACTS,
    map_portfolio,
)


def _active_universe(asset_count: int, hour_count: int) -> np.ndarray:
    return np.full((asset_count, hour_count), float(asset_count), dtype=float)


def test_four_hour_behavior_uses_t_minus_four_not_t_minus_one() -> None:
    weights = np.asarray(
        [[0.0, 1.0, 0.0, 0.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]
    )

    path, attribution = turnover_path(weights, 4)

    assert path[5] == pytest.approx(0.5)
    assert path[6] == pytest.approx(0.0)
    assert attribution["entry_l1"] == pytest.approx(0.5)
    assert attribution["transition_exit_l1"] == pytest.approx(0.5)
    assert attribution["total_turnover_l1"] == pytest.approx(float(path.sum()))


def test_behavior_turnover_exactly_matches_evaluator_turnover() -> None:
    weights = np.asarray(
        [
            [0.0, 0.4, 0.0, 0.0, 0.2, -0.3, 0.0, 0.0, 0.1, 0.0, 0.0, 0.0],
            [0.0, -0.4, 0.0, 0.0, -0.2, 0.3, 0.0, 0.0, -0.1, 0.0, 0.0, 0.0],
        ],
        dtype=float,
    )
    signal = weights.copy()
    eligible = np.ones_like(weights, dtype=bool)
    months = np.asarray(["2023-07"] * weights.shape[1])
    active_universe = _active_universe(*weights.shape)
    contract = freeze_search_behavior_contract(active_universe, eligible)

    descriptor = search_behavior_descriptor(
        signal=signal,
        weights=weights,
        eligible_mask=eligible,
        month_labels=months,
        timestamp_ns=np.arange(weights.shape[1], dtype=np.int64),
        active_universe_size=active_universe,
        horizon_hours=4,
        mapping_id=CROSS_SECTIONAL_ZERO_NET,
        contract=contract,
    )
    metrics = _series_metrics(
        weights=weights,
        target=np.zeros_like(weights),
        months=months,
        evaluation_mask=np.ones(weights.shape[1], dtype=bool),
        horizon=4,
    )
    path, attribution = turnover_path(weights, 4)

    assert descriptor["turnover_path_sha256"] == metrics["turnover_path_sha256"]
    assert metrics["total_turnover_l1"] == pytest.approx(float(path.sum()))
    assert metrics["total_turnover_l1"] == pytest.approx(
        attribution["total_turnover_l1"]
    )


class _BehaviorStore:
    def __init__(self) -> None:
        self.shape = (3, 12)
        hours = np.arange(self.shape[1], dtype=float)
        self._fields = {
            "a": np.vstack((hours + 1.0, 13.0 - hours, 2.0 + (hours % 3.0))),
            "b": np.vstack(
                (
                    np.where(hours % 2.0 == 0.0, 2.0, -1.0),
                    np.where(hours % 3.0 == 0.0, -2.0, 1.5),
                    np.where(hours % 4.0 < 2.0, 0.5, -2.5),
                )
            ),
            "active_universe_size": _active_universe(*self.shape),
        }
        self._eligible = np.ones(self.shape, dtype=bool)
        self._target = np.zeros(self.shape, dtype=float)
        start = np.datetime64("2023-07-01T00:00:00", "ns").astype(np.int64)
        self.timestamp_ns = (
            start
            + np.arange(self.shape[1], dtype=np.int64) * 3_600_000_000_000
        )

    def field(self, name: str) -> np.ndarray:
        return self._fields[name]

    def base_eligible(self) -> np.ndarray:
        return self._eligible

    def target_return(self, horizon: int) -> np.ndarray:
        assert horizon == 1
        return self._target

    def block_slice(self, start: str, end: str) -> slice:
        return slice(0, self.shape[1])


def test_behavior_family_uses_incremental_delta_weights() -> None:
    store = _BehaviorStore()
    registry = TypedExpressionRegistry(
        (
            FieldContract("a", "RATIO", "dimensionless"),
            FieldContract("b", "RATIO", "dimensionless"),
        )
    )
    primary_expression = Expression(
        "RatioInteraction", (Expression.raw("a"), Expression.raw("b"))
    )
    control_expression = ablate_expression(primary_expression)
    assurance = registry.validate(primary_expression)
    candidate = CandidateSpec(
        "candidate",
        "skeleton",
        "OI_ACTIVITY_INTERACTION",
        primary_expression,
        control_expression,
        1,
        CROSS_SECTIONAL_ZERO_NET,
        assurance.raw_fields,
        ("family_a", "family_b"),
        assurance.rolling_windows,
        assurance.depth,
        "RatioInteraction(Raw,Raw)",
    )
    active_universe = store.field("active_universe_size")
    contract = freeze_search_behavior_contract(
        active_universe, store.base_eligible()
    )
    result = evaluate_pair(
        store=store,
        registry=registry,
        candidate=candidate,
        block_start="2023-07-01T00:00:00Z",
        block_end="2023-07-01T12:00:00Z",
        block_role="DEVELOPMENT_ADAPTIVE_FEEDBACK",
        behavior_contract=contract,
    )

    raw = {"a": store.field("a"), "b": store.field("b")}
    primary_signal = materialize_expression(
        primary_expression,
        registry=registry,
        field_reader=raw.__getitem__,
        eligible_mask=store.base_eligible(),
    )
    control_signal = materialize_expression(
        control_expression,
        registry=registry,
        field_reader=raw.__getitem__,
        eligible_mask=store.base_eligible(),
    )
    mapping = DEFAULT_MAPPING_CONTRACTS[CROSS_SECTIONAL_ZERO_NET]
    primary_weight = np.asarray(map_portfolio(primary_signal, mapping).weights)
    control_weight = np.asarray(map_portfolio(control_signal, mapping).weights)
    descriptor_kwargs = {
        "eligible_mask": store.base_eligible(),
        "month_labels": np.asarray(["2023-07"] * store.shape[1]),
        "timestamp_ns": store.timestamp_ns,
        "active_universe_size": active_universe,
        "horizon_hours": 1,
        "mapping_id": CROSS_SECTIONAL_ZERO_NET,
        "contract": contract,
    }
    primary_behavior = search_behavior_descriptor(
        signal=primary_signal,
        weights=primary_weight,
        **descriptor_kwargs,
    )
    control_behavior = search_behavior_descriptor(
        signal=control_signal,
        weights=control_weight,
        **descriptor_kwargs,
    )
    incremental_behavior = search_behavior_descriptor(
        signal=primary_signal - control_signal,
        weights=primary_weight - control_weight,
        **descriptor_kwargs,
    )

    behavior = result["behavior"]
    assert behavior["primary_behavior_id"] == primary_behavior["behavior_family_id"]
    assert behavior["control_behavior_id"] == control_behavior["behavior_family_id"]
    assert (
        behavior["incremental_behavior_id"]
        == incremental_behavior["behavior_family_id"]
    )
    assert behavior["behavior_family_id"] == behavior["incremental_behavior_id"]
    assert (
        behavior["mapped_weight_descriptor_id"]
        == incremental_behavior["mapped_weight_descriptor_id"]
    )
    assert (
        behavior["turnover_path_descriptor_id"]
        == incremental_behavior["turnover_path_descriptor_id"]
    )
    assert behavior["identity_excludes"] == ["gross", "net", "cost", "pair_reward"]


def test_behavior_contract_rejects_self_proving_partial_active_support() -> None:
    observed_support = np.ones((3, 4), dtype=bool)
    active_universe = np.asarray(
        [
            [2.0, 2.0, 2.0, 2.0],
            [2.0, 2.0, 2.0, 2.0],
            [np.nan, np.nan, np.nan, np.nan],
        ]
    )

    with pytest.raises(ValueError, match="must exactly match observed_support"):
        freeze_search_behavior_contract(active_universe, observed_support)


def test_behavior_contract_rejects_stale_active_values_outside_observed_support() -> None:
    observed_support = np.asarray(
        [
            [True, True, True, True],
            [True, True, True, True],
            [False, False, False, False],
        ]
    )
    active_universe = np.full((3, 4), 2.0, dtype=float)

    with pytest.raises(ValueError, match="must exactly match observed_support"):
        freeze_search_behavior_contract(active_universe, observed_support)
