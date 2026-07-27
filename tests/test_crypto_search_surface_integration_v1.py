from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pytest

from alphafactory_crypto.broad_search.compositional18m import (
    compiler_reachability_proofs,
    field_role_surface,
)
from alphafactory_crypto.broad_search.expression import (
    FieldContract,
    TypedExpressionRegistry,
)
from alphafactory_crypto.broad_search.panel18m import RawPanelStore
from alphafactory_crypto.data_admission_v1 import (
    AGGTRADES_SEARCH_FIELDS,
    aggregate_aggtrades_search_hourly,
    contracts_from_core3_tokens,
    contracts_from_oi_mark_schema,
)


def test_partial_data_plane_selects_only_compatible_skeletons() -> None:
    contracts = (
        FieldContract("close_to_open_bps", "BPS", "bps", 1, "TEST"),
        FieldContract("notional", "NOTIONAL", "quote_asset", 1, "TEST"),
    )
    surface = field_role_surface(contracts)
    assert surface["full_grammar_supported"] is False
    assert "PRICE_ACTIVITY_RESPONSE" in surface["compatible_mechanism_families"]
    assert "TOP_GLOBAL_CROWDING" not in surface["compatible_mechanism_families"]
    assert surface["all_fields_reachable"]

    registry = TypedExpressionRegistry(contracts)
    proofs = compiler_reachability_proofs(registry, surface_id="TEST_SURFACE")
    assert {row["field_id"] for row in proofs} == {
        "close_to_open_bps",
        "notional",
    }
    assert all(row["compiler_valid"] for row in proofs)
    assert all(row["matched_control_constructible"] for row in proofs)
    assert all(row["deterministic_replay"] for row in proofs)


def test_candidate_support_is_field_local_not_full_surface_intersection(
    tmp_path: Path,
) -> None:
    root = tmp_path / "cache"
    (root / "fields").mkdir(parents=True)
    metadata = {
        "assets": 3,
        "timestamps": 2,
        "symbol_ids": ["A", "B", "C"],
        "field_ids": ["left", "right", "unrelated_sparse"],
        "target_horizons_hours": [1],
    }
    (root / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    np.save(root / "timestamp_ns.npy", np.arange(2, dtype=np.int64))
    np.save(root / "base_eligible.npy", np.ones((3, 2), dtype=bool))
    np.save(root / "observed.npy", np.ones((3, 2), dtype=bool))
    np.save(root / "fields" / "left.npy", np.ones((3, 2), dtype=np.float32))
    np.save(root / "fields" / "right.npy", np.ones((3, 2), dtype=np.float32))
    sparse = np.ones((3, 2), dtype=np.float32)
    sparse[:, 0] = np.nan
    np.save(root / "fields" / "unrelated_sparse.npy", sparse)
    np.save(root / "target_return_1h.npy", np.ones((3, 2), dtype=np.float32))

    store = RawPanelStore.open(root)
    support = store.candidate_support(("left", "right"))
    full_surface = store.candidate_support(
        ("left", "right", "unrelated_sparse")
    )
    assert support.all()
    assert not full_surface[:, 0].any()
    assert full_surface[:, 1].all()


def test_full_aggtrades_physical_surface_aggregates_without_zero_fill() -> None:
    timestamps = pd.date_range("2024-01-01", periods=60, freq="min", tz="UTC")
    frame = pd.DataFrame(
        {
            "timestamp": timestamps,
            "agg_trade_count": np.ones(60, dtype=int),
            "underlying_trade_count": np.full(60, 2.0),
            "quantity": np.full(60, 3.0),
            "notional": np.full(60, 30.0),
            "buy_agg_trade_count": np.ones(60, dtype=int),
            "sell_agg_trade_count": np.zeros(60, dtype=int),
            "buy_underlying_trade_count": np.full(60, 2.0),
            "sell_underlying_trade_count": np.zeros(60),
            "buy_quantity": np.full(60, 3.0),
            "sell_quantity": np.zeros(60),
            "buy_notional": np.full(60, 30.0),
            "sell_notional": np.zeros(60),
            "signed_aggressor_quantity": np.full(60, 3.0),
            "signed_aggressor_notional": np.full(60, 30.0),
            "trade_count_le_100": np.ones(60, dtype=int),
            "trade_count_100_1k": np.zeros(60, dtype=int),
            "trade_count_1k_10k": np.zeros(60, dtype=int),
            "trade_count_10k_100k": np.zeros(60, dtype=int),
            "trade_count_100k_1m": np.zeros(60, dtype=int),
            "trade_count_gt_1m": np.zeros(60, dtype=int),
            "notional_le_100": np.full(60, 30.0),
            "notional_100_1k": np.zeros(60),
            "notional_1k_10k": np.zeros(60),
            "notional_10k_100k": np.zeros(60),
            "notional_100k_1m": np.zeros(60),
            "notional_gt_1m": np.zeros(60),
            "high_price": np.full(60, 11.0),
            "low_price": np.full(60, 9.0),
            "max_trade_notional": np.full(60, 30.0),
            "open_price": np.full(60, 10.0),
            "close_price": np.full(60, 10.5),
            "large_trade_count_100k_plus": np.zeros(60, dtype=int),
            "large_notional_100k_plus": np.zeros(60),
            "feature_available_time": timestamps + pd.Timedelta(minutes=1),
            "execution_time_min": timestamps + pd.Timedelta(minutes=2),
        }
    )
    hourly = aggregate_aggtrades_search_hourly(frame)
    assert len(hourly) == 1
    assert set(AGGTRADES_SEARCH_FIELDS).issubset(hourly.columns)
    row = hourly.iloc[0]
    assert bool(row["complete_and_pit_safe"])
    assert row["agg_trade_count"] == 60
    assert row["underlying_trade_count"] == 120
    assert row["notional"] == 1800
    assert row["vwap"] == 10
    assert row["volume_imbalance"] == 1
    assert row["price_range_bps"] == pytest.approx(2222.222222222222)
    assert row["close_to_open_bps"] == 500


def test_context_contracts_remain_separate_and_oi_fields_are_venue_qualified() -> None:
    tokens = {
        "tokens": [
            {
                "field_id": "broad",
                "token_id": "FIELD:broad",
                "token_kind": "BASE",
                "context_id": "BROAD_PANEL_BASELINE",
                "family": "price_return",
                "feature_available_lag_bars": 1,
            },
            {
                "field_id": "agg_notional",
                "token_id": "FIELD:agg_notional",
                "token_kind": "BASE",
                "context_id": "CORE3_MICROSTRUCTURE_PILOT",
                "family": "activity_liquidity",
                "feature_available_lag_bars": 1,
            },
            {
                "field_id": "Delta_4h__agg_notional",
                "token_id": "FIELD:agg_notional|TRANSFORM:DELTA|WINDOW:4H",
                "token_kind": "DERIVED",
                "context_id": "CORE3_MICROSTRUCTURE_PILOT",
                "family": "rolling_self_reproduction",
                "feature_available_lag_bars": 4,
            },
        ]
    }
    core = contracts_from_core3_tokens(tokens)
    assert [row.field_id for row in core] == [
        "agg_notional",
        "Delta_4h__agg_notional",
    ]
    assert [row.observable_lag_hours for row in core] == [1, 4]

    schema = pa.schema(
        [
            pa.field("venue", pa.string()),
            pa.field("base_asset", pa.string()),
            pa.field("timestamp", pa.timestamp("us", tz="UTC")),
            pa.field("open_interest_last", pa.float64()),
            pa.field("mark_price_last", pa.float64()),
            pa.field("funding_rate_last", pa.float64()),
            pa.field("feature_available_time", pa.timestamp("us", tz="UTC")),
            pa.field("execution_time_min", pa.timestamp("us", tz="UTC")),
        ]
    )
    oi = contracts_from_oi_mark_schema("bybit", schema)
    assert [row.field_id for row in oi] == [
        "bybit__open_interest_last",
        "bybit__mark_price_last",
        "bybit__funding_rate_last",
    ]
    assert all(row.observable_lag_hours == 1 for row in oi)
