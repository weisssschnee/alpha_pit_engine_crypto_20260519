from __future__ import annotations

import unittest

import numpy as np

from alphafactory_crypto.instrument_canary.evaluator import evaluate_real_mapping
from alphafactory_crypto.instrument_capability.mapping import (
    DEFAULT_MAPPING_CONTRACTS,
    MappingResult,
    TIME_SERIES_DIRECTIONAL_STATEFUL,
    mapping_contract_sha256,
)


class RealCanaryEvaluatorTests(unittest.TestCase):
    @staticmethod
    def _mapped(weights: np.ndarray) -> MappingResult:
        return MappingResult(
            TIME_SERIES_DIRECTIONAL_STATEFUL,
            mapping_contract_sha256(
                DEFAULT_MAPPING_CONTRACTS[TIME_SERIES_DIRECTIONAL_STATEFUL]
            ),
            weights,
            np.ones(weights.shape[1], dtype=bool),
            tuple(("MAPPED",) for _ in range(weights.shape[1])),
            {},
        )

    def test_four_hour_target_uses_four_equal_capital_nonoverlapping_sleeves(self) -> None:
        weights = np.ones((1, 8), dtype=float)
        target = np.full((1, 8), 0.04, dtype=float)
        result = evaluate_real_mapping(
            self._mapped(weights),
            weights,
            target,
            np.array(["2024-01"] * 8),
            target_horizon_hours=4,
        )
        self.assertEqual(result.execution_model_id, "EQUAL_CAPITAL_HORIZON_OFFSET_SLEEVES")
        self.assertEqual(result.overlapping_sleeves, 4)
        self.assertAlmostEqual(result.gross_mean, 0.01)
        self.assertAlmostEqual(result.initial_establishment_l1, 1.0)
        self.assertAlmostEqual(result.subsequent_entry_l1, 0.0)
        self.assertAlmostEqual(result.terminal_liquidation_l1, 1.0)
        self.assertAlmostEqual(result.total_turnover_l1, 2.0)
        self.assertAlmostEqual(result.total_cost, 0.001)

    def test_reentry_and_sign_flip_attribution_closes_to_full_l1(self) -> None:
        weights = np.array([[0.0, 1.0, 0.0, -1.0, -1.0]], dtype=float)
        target = np.full(weights.shape, 0.01)
        result = evaluate_real_mapping(
            self._mapped(weights),
            weights,
            target,
            np.array(["2024-01"] * weights.shape[1]),
            target_horizon_hours=1,
        )
        attributed = (
            result.initial_establishment_l1
            + result.subsequent_entry_l1
            + result.rebalance_l1
            + result.transition_exit_l1
            + result.terminal_liquidation_l1
        )
        self.assertAlmostEqual(attributed, result.total_turnover_l1)
        self.assertGreater(result.subsequent_entry_l1, 0.0)

    def test_noncanonical_mapping_hash_and_incomplete_blocks_fail_closed(self) -> None:
        weights = np.ones((1, 8), dtype=float)
        bad = MappingResult(
            TIME_SERIES_DIRECTIONAL_STATEFUL,
            "forged",
            weights,
            np.ones(8, dtype=bool),
            tuple(("MAPPED",) for _ in range(8)),
            {},
        )
        with self.assertRaisesRegex(ValueError, "not canonical"):
            evaluate_real_mapping(
                bad,
                weights,
                np.full_like(weights, 0.01),
                np.array(["2024-01"] * 8),
                target_horizon_hours=1,
            )
        with self.assertRaisesRegex(ValueError, "blocks are incomplete"):
            evaluate_real_mapping(
                self._mapped(weights),
                weights,
                np.full_like(weights, 0.01),
                np.array(["2024-01"] * 8),
                target_horizon_hours=1,
                expected_months=("2024-01", "2024-02"),
            )


if __name__ == "__main__":
    unittest.main()
