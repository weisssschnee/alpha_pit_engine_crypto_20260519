from __future__ import annotations

import unittest

from alphafactory_crypto.bz import assert_bz_use_allowed, create_benchmark_zero


class BenchmarkZeroTests(unittest.TestCase):
    def test_bz_accepts_only_benchmark_inputs(self) -> None:
        bz = create_benchmark_zero(["trade_close"], ["benchmark-only"])
        self.assertEqual(bz.object_id, "bz:benchmark-zero:v1")
        self.assertEqual(bz.feedback_permission, "NONE")
        self.assertEqual(bz.expected_alpha, 0.0)

    def test_bz_rejects_primary_input(self) -> None:
        with self.assertRaises(ValueError):
            create_benchmark_zero(["signal_x"], ["primary"])

    def test_bz_cannot_promote(self) -> None:
        with self.assertRaises(PermissionError):
            assert_bz_use_allowed("promotion")


if __name__ == "__main__":
    unittest.main()
