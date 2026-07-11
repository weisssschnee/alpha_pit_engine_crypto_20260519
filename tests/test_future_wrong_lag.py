from __future__ import annotations

import unittest

import numpy as np

from alphafactory_crypto.negative_controls import audit_future_wrong_lag, future_wrong_lag


class FutureWrongLagTests(unittest.TestCase):
    def test_future_shift_is_negative_lag_without_wraparound(self) -> None:
        values = np.arange(6, dtype=float).reshape(1, 6)
        shifted = future_wrong_lag(values, periods=2)
        np.testing.assert_allclose(shifted[:, :4], np.array([[2.0, 3.0, 4.0, 5.0]]))
        self.assertTrue(np.isnan(shifted[:, 4:]).all())

    def test_future_dominance_fails(self) -> None:
        audit = audit_future_wrong_lag(0.8, 1.5)
        self.assertTrue(audit.future_dominates)
        self.assertEqual(audit.status, "FAIL_FUTURE_WRONG_LAG_DOMINATES")

    def test_weaker_future_control_passes(self) -> None:
        audit = audit_future_wrong_lag(1.2, -0.1)
        self.assertFalse(audit.future_dominates)
        self.assertEqual(audit.status, "PASS_FUTURE_WRONG_LAG_WEAKER")


if __name__ == "__main__":
    unittest.main()
