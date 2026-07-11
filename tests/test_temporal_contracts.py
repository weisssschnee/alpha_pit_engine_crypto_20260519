from __future__ import annotations

import unittest

import pandas as pd

from alphafactory_crypto.temporal_contracts import (
    PrimitiveSpec,
    TemporalObservation,
    canonicalize_primitive,
    temporal_equivalent,
)


class TemporalContractTests(unittest.TestCase):
    def test_usable_time_is_max_observable_and_maturity(self) -> None:
        observation = TemporalObservation(
            pd.Timestamp("2026-01-01 00:00Z"),
            pd.Timestamp("2026-01-01 01:00Z"),
            pd.Timestamp("2026-01-01 00:30Z"),
        )
        self.assertEqual(observation.usable_time, pd.Timestamp("2026-01-01 01:00Z"))
        with self.assertRaises(PermissionError):
            observation.assert_usable_at(pd.Timestamp("2026-01-01 00:59Z"))
        observation.assert_usable_at(pd.Timestamp("2026-01-01 01:00Z"))

    def test_observable_time_cannot_precede_event(self) -> None:
        observation = TemporalObservation(
            pd.Timestamp("2026-01-01 01:00Z"),
            pd.Timestamp("2026-01-01 00:00Z"),
            pd.Timestamp("2026-01-01 01:00Z"),
        )
        with self.assertRaises(ValueError):
            observation.validate()

    def test_lag_zero_canonicalizes_to_identity(self) -> None:
        canonical = canonicalize_primitive(PrimitiveSpec("lag", "field:x", {"period": "0h"}))
        self.assertEqual(canonical["primitive_id"], "identity")

    def test_equivalence_depends_on_observable_and_maturity_contract(self) -> None:
        left = PrimitiveSpec("lag", "field:x", {"period": "1h"}, observable_policy="plus_1h")
        same = PrimitiveSpec("lag", "field:x", {"period": "60m"}, observable_policy="plus_1h")
        different = PrimitiveSpec("lag", "field:x", {"period": "1h"}, observable_policy="same_bar")
        self.assertTrue(temporal_equivalent(left, same))
        self.assertFalse(temporal_equivalent(left, different))

    def test_negative_legal_lag_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            canonicalize_primitive(PrimitiveSpec("lag", "field:x", {"period": "-1h"}))


if __name__ == "__main__":
    unittest.main()
