from __future__ import annotations

import unittest

import numpy as np

from alphafactory_crypto.instrument_capability.mapping import (
    CROSS_SECTIONAL_ZERO_NET,
    DEFAULT_MAPPING_CONTRACTS,
    _average_ranks,
    _capped_allocation,
    map_portfolio,
)
from alphafactory_crypto.instrument_capability.primitives import (
    _rolling_apply,
    evaluate_primitive,
)


def _slow_cross_sectional(signal: np.ndarray):
    contract = DEFAULT_MAPPING_CONTRACTS[CROSS_SECTIONAL_ZERO_NET]
    parameters = contract.parameters
    gross_target = float(parameters["gross_target"])
    cap = float(parameters["position_cap"])
    minimum = int(parameters["minimum_asset_count"])
    weights = np.zeros(signal.shape, dtype=float)
    feasible = np.zeros(signal.shape[1], dtype=bool)
    reasons: list[tuple[str, ...]] = []
    achieved: list[float] = []
    for column in range(signal.shape[1]):
        finite_index = np.flatnonzero(np.isfinite(signal[:, column]))
        if len(finite_index) < minimum:
            reasons.append(("MINIMUM_ASSET_COUNT_NOT_MET",))
            achieved.append(0.0)
            continue
        values = signal[finite_index, column]
        centered = _average_ranks(values)
        centered -= centered.mean()
        positive = centered > 0
        negative = centered < 0
        if not positive.any() or not negative.any():
            reasons.append(("NO_CROSS_SECTIONAL_DISPERSION",))
            achieved.append(0.0)
            continue
        requested = gross_target / 2.0
        side = min(requested, cap * int(positive.sum()), cap * int(negative.sum()))
        local = _capped_allocation(
            np.where(positive, centered, 0.0), side, cap
        ) - _capped_allocation(np.where(negative, -centered, 0.0), side, cap)
        weights[finite_index, column] = local
        feasible[column] = True
        achieved.append(float(np.abs(local).sum()))
        reasons.append(
            ("GROSS_REDUCED_FOR_CAP_FEASIBILITY",)
            if side < requested - 1e-12
            else ("MAPPED",)
        )
    return weights, feasible, tuple(reasons), achieved


class AccelerationParityTests(unittest.TestCase):
    def test_vectorized_cross_sectional_mapping_is_exact_to_frozen_reference(self) -> None:
        for seed in range(5):
            values = np.random.default_rng(seed).normal(size=(10, 97))
            values[:, ::17] = 1.0
            values[0, ::13] = np.nan
            expected = _slow_cross_sectional(values)
            observed = map_portfolio(
                values, DEFAULT_MAPPING_CONTRACTS[CROSS_SECTIONAL_ZERO_NET]
            )
            np.testing.assert_array_equal(observed.weights, expected[0])
            np.testing.assert_array_equal(observed.feasible, expected[1])
            self.assertEqual(observed.transition_reasons, expected[2])
            self.assertEqual(observed.diagnostics["achieved_gross"], expected[3])

    def test_vectorized_rolling_primitives_match_slow_reference(self) -> None:
        values = np.random.default_rng(7).normal(size=(4, 73))
        values[1, 19] = np.nan
        window = 8
        long_window = 24
        axis = np.arange(window, dtype=float)
        centered = axis - axis.mean()
        denominator = float(np.sum(centered * centered))
        cases = {
            "Slope": _rolling_apply(
                values,
                window,
                lambda segment: np.sum(centered * segment) / denominator,
            ),
            "Persistence": _rolling_apply(
                values, window, lambda segment: np.mean(segment > 0.0)
            ),
            "PathShape": _rolling_apply(
                values,
                window,
                lambda segment: np.mean(segment[-(window // 3) :])
                - np.mean(segment[: window // 3]),
            ),
            "MultiScaleRelation": np.where(
                np.isfinite(_rolling_apply(values, window, np.mean))
                & np.isfinite(_rolling_apply(values, long_window, np.mean)),
                _rolling_apply(values, window, np.mean)
                - _rolling_apply(values, long_window, np.mean),
                np.nan,
            ),
        }
        for primitive_id, expected in cases.items():
            with self.subTest(primitive_id=primitive_id):
                observed = evaluate_primitive(
                    primitive_id,
                    values,
                    window=window,
                    long_window=long_window,
                    threshold=0.0,
                )
                np.testing.assert_array_equal(observed, expected)


if __name__ == "__main__":
    unittest.main()
