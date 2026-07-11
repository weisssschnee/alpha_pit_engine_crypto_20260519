from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from alphafactory_crypto.nextgen_fabric import NO_FEEDBACK, materialize_states


def fixture() -> pd.DataFrame:
    rows = []
    for symbol, offset in (("BTCUSDT", 0.0), ("ETHUSDT", 10.0)):
        for i, timestamp in enumerate(pd.date_range("2026-01-01", periods=48, freq="h", tz="UTC")):
            rows.append({
                "symbol": symbol, "timestamp": timestamp,
                "observable_time": timestamp + pd.Timedelta(hours=1),
                "maturity_time": timestamp + pd.Timedelta(hours=1),
                "funding_rate": (i // 8) * 0.0001,
                "mark_trade_basis_bps": offset + i % 7,
                "mark_index_basis_bps": offset + i % 5,
                "open_interest_value_last": 1000.0 + offset + i,
                "kline_taker_buy_quote_share": 0.4 + (i % 4) / 20,
                "trade_quote_volume": 1_000_000.0 + i * 100,
                "trade_close": 100.0 + offset + i,
            })
    return pd.DataFrame(rows)


ROLES = {
    "funding_rate": "condition-only", "mark_trade_basis_bps": "state-only",
    "mark_index_basis_bps": "primary", "open_interest_value_last": "interaction-only",
    "kline_taker_buy_quote_share": "state-only", "trade_quote_volume": "condition-only",
    "trade_close": "benchmark-only",
}


class NextgenFabricTests(unittest.TestCase):
    def test_materialization_is_batch_order_invariant(self) -> None:
        frame = fixture()
        left = materialize_states(frame, ROLES, source_release_hash="R", field_registry_hash="F", production_scope="DEV")
        right = materialize_states(frame.sample(frac=1, random_state=7), ROLES, source_release_hash="R", field_registry_hash="F", production_scope="DEV")
        self.assertEqual(left.artifact_hash, right.artifact_hash)
        self.assertTrue((left.frame["feedback_permission"] == NO_FEEDBACK).all())

    def test_missing_unapproved_sources_are_explicit_not_proxied(self) -> None:
        result = materialize_states(fixture(), ROLES, source_release_hash="R", field_registry_hash="F", production_scope="DEV")
        status = {item.state_id: item.status for item in result.availability}
        self.assertEqual(status["liquidation_cluster"], "UNAVAILABLE_NO_APPROVED_SOURCE")
        self.assertEqual(status["depth_liquidity_state"], "UNAVAILABLE_NO_APPROVED_SOURCE")
        self.assertTrue(result.frame["liquidation_cluster"].isna().all())

    def test_scoped_top_of_book_source_materializes_liquidity_without_claiming_multilevel_depth(self) -> None:
        frame = fixture()
        frame["top_of_book_quote_notional_mean"] = 100_000.0 + np.arange(len(frame), dtype=float) * 25.0
        roles = dict(ROLES, top_of_book_quote_notional_mean="state-only")
        result = materialize_states(frame, roles, source_release_hash="BOOK", field_registry_hash="F", production_scope="DEV")
        availability = {item.state_id: item for item in result.availability}
        self.assertEqual(availability["depth_liquidity_state"].status, "MATERIALIZED")
        self.assertEqual(availability["depth_liquidity_state"].required_fields, ("top_of_book_quote_notional_mean",))
        self.assertTrue(result.frame["depth_liquidity_state"].notna().any())

    def test_source_or_registry_change_changes_lineage_hash(self) -> None:
        frame = fixture()
        left = materialize_states(frame, ROLES, source_release_hash="R1", field_registry_hash="F", production_scope="DEV")
        right = materialize_states(frame, ROLES, source_release_hash="R2", field_registry_hash="F", production_scope="DEV")
        self.assertNotEqual(left.artifact_hash, right.artifact_hash)

    def test_duplicate_and_wrong_lag_fail_closed(self) -> None:
        frame = fixture()
        with self.assertRaises(ValueError):
            materialize_states(pd.concat([frame, frame.iloc[[0]]]), ROLES, source_release_hash="R", field_registry_hash="F", production_scope="DEV")
        frame.loc[0, "observable_time"] = frame.loc[0, "timestamp"] - pd.Timedelta(hours=1)
        with self.assertRaises(ValueError):
            materialize_states(frame, ROLES, source_release_hash="R", field_registry_hash="F", production_scope="DEV")


if __name__ == "__main__":
    unittest.main()
