from __future__ import annotations

import unittest

import pandas as pd

from alphafactory_crypto.funding_events import canonicalize_funding_events
from alphafactory_crypto.funding_qualification import (
    FundingQualificationError,
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
    def test_exact_observation_set_qualifies(self) -> None:
        truth = events()
        result = qualify_production_funding(truth, truth.copy(), source_integrity_verified=True, tolerance="1s")
        self.assertEqual(result.summary["decision"], "PRODUCTION_FUNDING_OBSERVATION_QUALIFIED")
        self.assertEqual(result.summary["recall"], 1.0)
        self.assertEqual(result.summary["precision"], 1.0)
        self.assertEqual(result.summary["symbol_month_coverage_ratio"], 1.0)
        self.assertEqual(result.summary["rate_mismatch_events"], 0)

    def test_miss_is_classified_and_only_partially_qualifies(self) -> None:
        truth = events()
        detected = truth.drop(index=2).reset_index(drop=True)
        result = qualify_production_funding(truth, detected, source_integrity_verified=True, tolerance="1s")
        self.assertEqual(result.summary["decision"], "PRODUCTION_FUNDING_OBSERVATION_PARTIALLY_QUALIFIED")
        self.assertEqual(result.summary["missed_events"], 1)
        self.assertEqual(result.misses.iloc[0]["miss_classification"], "NO_DETECTED_EVENT_WITHIN_TOLERANCE")

    def test_forbidden_price_or_return_columns_fail_closed(self) -> None:
        with self.assertRaises(FundingQualificationError):
            validate_observation_columns(["symbol", "fundingTime", "markPrice"], {"symbol", "fundingTime", "fundingRate"})
        with self.assertRaises(FundingQualificationError):
            validate_observation_columns(["symbol", "timestamp", "fwd_ret_1"], {"symbol", "timestamp", "fundingTime_ms"})


if __name__ == "__main__":
    unittest.main()
