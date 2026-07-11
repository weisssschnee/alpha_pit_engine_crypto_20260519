from __future__ import annotations

import unittest

import pandas as pd

from alphafactory_crypto.funding_events import (
    FundingEventContractError,
    audit_cashflow_semantics,
    audit_funding_event_detection,
    canonicalize_funding_events,
    funding_event_flags_from_last_time,
)


class FundingEventTests(unittest.TestCase):
    def test_dense_last_known_rate_is_not_repeated_event(self) -> None:
        frame = pd.DataFrame(
            {
                "symbol": ["BTCUSDT"] * 5,
                "timestamp": pd.date_range("2026-01-01 00:00", periods=5, freq="h", tz="UTC"),
                "last_funding_time": [
                    "2026-01-01 00:00Z",
                    "2026-01-01 00:00Z",
                    "2026-01-01 00:00Z",
                    "2026-01-01 03:00Z",
                    "2026-01-01 03:00Z",
                ],
                "last_funding_rate": [0.0001] * 5,
            }
        )
        flags = funding_event_flags_from_last_time(frame)
        self.assertEqual(flags.tolist(), [True, False, False, True, False])

    def test_native_event_identity_keeps_equal_rates_at_different_times(self) -> None:
        raw = pd.DataFrame(
            {
                "symbol": ["BTCUSDT", "BTCUSDT"],
                "funding_time": ["2026-01-01 00:00Z", "2026-01-01 08:00Z"],
                "funding_rate": [0.0001, 0.0001],
            }
        )
        events = canonicalize_funding_events(raw)
        self.assertEqual(len(events), 2)
        self.assertEqual(events["event_id"].nunique(), 2)

    def test_observable_delay_and_cashflow_semantics(self) -> None:
        raw = pd.DataFrame(
            {
                "symbol": ["BTCUSDT", "ETHUSDT"],
                "funding_time": ["2026-01-01 00:00Z", "2026-01-01 00:00Z"],
                "funding_rate": [0.0001, -0.0002],
            }
        )
        events = canonicalize_funding_events(raw)
        delay = events["observable_time_utc"] - events["funding_time_utc"]
        self.assertTrue(delay.eq(pd.Timedelta("1h")).all())
        self.assertEqual(events["payer_side"].tolist(), ["LONG", "SHORT"])
        self.assertTrue(audit_cashflow_semantics(events)["pass"])

    def test_one_to_one_tolerance_audit_exposes_miss(self) -> None:
        expected = canonicalize_funding_events(
            pd.DataFrame(
                {
                    "symbol": ["BTCUSDT"] * 3,
                    "funding_time": ["2026-01-01 00:00Z", "2026-01-01 08:00Z", "2026-01-01 16:00Z"],
                    "funding_rate": [0.0001, -0.0001, 0.0002],
                }
            )
        )
        detected = expected.iloc[:2].copy()
        detected.loc[1, "funding_time_utc"] += pd.Timedelta("20m")
        audit = audit_funding_event_detection(expected, detected, tolerance="30m")
        self.assertEqual(audit.summary["matched_events"], 2)
        self.assertEqual(audit.summary["missed_events"], 1)
        self.assertAlmostEqual(audit.summary["recall"], 2 / 3)
        self.assertEqual(audit.summary["timing_error_abs_seconds_max"], 1200.0)

    def test_conflicting_duplicate_event_fails_closed(self) -> None:
        raw = pd.DataFrame(
            {
                "symbol": ["BTCUSDT", "BTCUSDT"],
                "funding_time": ["2026-01-01 00:00Z", "2026-01-01 00:00Z"],
                "funding_rate": [0.0001, 0.0002],
            }
        )
        with self.assertRaises(FundingEventContractError):
            canonicalize_funding_events(raw)


if __name__ == "__main__":
    unittest.main()
