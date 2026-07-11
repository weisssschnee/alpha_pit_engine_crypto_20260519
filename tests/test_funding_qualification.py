from __future__ import annotations

import unittest

import pandas as pd

from alphafactory_crypto.funding_events import canonicalize_funding_events
from alphafactory_crypto.funding_qualification import (
    DETECTOR_QUALIFICATION_COLUMNS,
    FundingQualificationError,
    TRUTH_QUALIFICATION_COLUMNS,
    hourly_bar_close_observable_time,
    qualify_production_funding,
    validate_observation_columns,
)


def events() -> pd.DataFrame:
    return canonicalize_funding_events(
        pd.DataFrame(
            {
                "symbol": ["BTCUSDT", "ETHUSDT", "BTCUSDT", "ETHUSDT"],
                "funding_time": [
                    "2026-01-01 00:00Z",
                    "2026-01-01 00:00Z",
                    "2026-02-01 00:00Z",
                    "2026-02-01 00:00Z",
                ],
                "funding_rate": [0.0001, -0.0002, 0.0003, 0.0],
            }
        )
    )


class FundingQualificationTests(unittest.TestCase):
    def test_hourly_observable_time_is_pit_bar_close(self) -> None:
        native = pd.Series(
            pd.to_datetime(["2026-01-01T00:00:00Z", "2026-01-01T00:00:00.001Z"], utc=True, format="mixed")
        )
        observable = hourly_bar_close_observable_time(native)
        self.assertEqual(observable.iloc[0], pd.Timestamp("2026-01-01T00:59:59.999Z"))
        self.assertEqual(observable.iloc[1], pd.Timestamp("2026-01-01T01:59:59.999Z"))

    def test_exact_observation_set_qualifies(self) -> None:
        truth = events()
        result = qualify_production_funding(truth, truth.copy(), source_integrity_verified=True, tolerance="1s")
        self.assertEqual(result.summary["decision"], "PRODUCTION_FUNDING_OBSERVATION_QUALIFIED")
        self.assertEqual(result.summary["recall"], 1.0)
        self.assertEqual(result.summary["precision"], 1.0)
        self.assertEqual(result.summary["symbol_month_coverage_ratio"], 1.0)
        self.assertEqual(result.summary["rate_mismatch_events"], 0)
        self.assertEqual(result.summary["observable_time_error_abs_seconds_max"], 0.0)

    def test_precanonical_source_duplicate_blocks_full_qualification(self) -> None:
        truth = events()
        result = qualify_production_funding(
            truth,
            truth.copy(),
            source_integrity_verified=True,
            truth_source_duplicate_rows=2,
            tolerance="1s",
        )
        self.assertEqual(result.summary["decision"], "PRODUCTION_FUNDING_OBSERVATION_PARTIALLY_QUALIFIED")
        self.assertEqual(result.summary["truth_source_duplicate_rows"], 2)

    def test_miss_is_classified_and_only_partially_qualifies(self) -> None:
        truth = events()
        detected = truth.drop(index=2).reset_index(drop=True)
        result = qualify_production_funding(truth, detected, source_integrity_verified=True, tolerance="1s")
        self.assertEqual(result.summary["decision"], "PRODUCTION_FUNDING_OBSERVATION_PARTIALLY_QUALIFIED")
        self.assertEqual(result.summary["missed_events"], 1)
        self.assertEqual(result.misses.iloc[0]["miss_classification"], "NO_DETECTED_EVENT_WITHIN_TOLERANCE")

    def test_forbidden_price_or_return_columns_fail_closed(self) -> None:
        with self.assertRaises(FundingQualificationError):
            validate_observation_columns(["symbol", "fundingTime", "markPrice"], set(TRUTH_QUALIFICATION_COLUMNS))
        with self.assertRaises(FundingQualificationError):
            validate_observation_columns(["symbol", "timestamp", "fwd_ret_1"], set(DETECTOR_QUALIFICATION_COLUMNS))


if __name__ == "__main__":
    unittest.main()
