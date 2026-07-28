from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
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
from alphafactory_crypto.broad_search.runner18m import (
    _directory_bundle,
    _payload_sha,
    load_search_surface_carrier,
)
from alphafactory_crypto.data_admission_v1 import (
    AGGTRADES_SEARCH_FIELDS,
    _active_surface_rows,
    _compact_compatible_surfaces,
    _oi_mark_surface,
    aggregate_aggtrades_search_hourly,
    contracts_from_core3_tokens,
    contracts_from_oi_mark_schema,
)


def test_surface_decision_summary_does_not_duplicate_role_maps() -> None:
    contracts = (
        FieldContract("close_to_open_bps", "BPS", "bps", 1, "TEST"),
        FieldContract("notional", "NOTIONAL", "quote_asset", 1, "TEST"),
    )
    surface = field_role_surface(contracts)
    summary = _compact_compatible_surfaces({"TEST": surface})["TEST"]
    assert summary["declared_field_count"] == 2
    assert summary["reachable_field_count"] == 2
    assert "roles" not in summary
    assert "declared_fields" not in summary


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


def test_runtime_reachability_proof_reads_real_raw_panel_fields(
    tmp_path: Path,
) -> None:
    root = tmp_path / "runtime-cache"
    (root / "fields").mkdir(parents=True)
    shape = (3, 800)
    metadata = {
        "assets": shape[0],
        "timestamps": shape[1],
        "symbol_ids": ["A", "B", "C"],
        "field_ids": ["close_to_open_bps", "notional"],
        "target_horizons_hours": [1, 4],
        "minimum_assets_per_timestamp": 3,
    }
    (root / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    np.save(root / "timestamp_ns.npy", np.arange(shape[1], dtype=np.int64))
    np.save(root / "observed.npy", np.ones(shape, dtype=bool))
    np.save(root / "base_eligible.npy", np.ones(shape, dtype=bool))
    grid = np.arange(np.prod(shape), dtype=np.float32).reshape(shape) + 1
    np.save(root / "fields" / "close_to_open_bps.npy", grid)
    np.save(root / "fields" / "notional.npy", grid * 10)
    store = RawPanelStore.open(root)
    contracts = (
        FieldContract("close_to_open_bps", "BPS", "bps", 1, "TEST"),
        FieldContract("notional", "NOTIONAL", "quote_asset", 1, "TEST"),
    )
    rows, proofs, _ = _active_surface_rows(
        surface_id="TEST_RUNTIME",
        contracts=contracts,
        finite_ratios={
            "close_to_open_bps": 1.0,
            "notional": 1.0,
        },
        store=store,
    )
    assert len(proofs) == 2
    assert all(row["runtime_materialized"] for row in rows)
    assert all(row["candidate_support_coordinates"] > 0 for row in rows)


def test_runner_loads_content_bound_independent_search_carrier(
    tmp_path: Path,
) -> None:
    root = tmp_path / "carrier"
    (root / "fields").mkdir(parents=True)
    shape = (3, 8)
    metadata = {
        "schema_version": 2,
        "identity_sha256": "A" * 64,
        "assets": shape[0],
        "timestamps": shape[1],
        "symbol_ids": ["A", "B", "C"],
        "field_ids": ["notional"],
        "target_horizons_hours": [1, 4],
    }
    (root / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    np.save(root / "timestamp_ns.npy", np.arange(shape[1], dtype=np.int64))
    np.save(root / "observed.npy", np.ones(shape, dtype=bool))
    np.save(root / "base_eligible.npy", np.ones(shape, dtype=bool))
    np.save(root / "source_segment.npy", np.ones(shape, dtype=np.int8))
    np.save(root / "target_return_1h.npy", np.zeros(shape, dtype=np.float32))
    np.save(root / "target_return_4h.npy", np.zeros(shape, dtype=np.float32))
    np.save(root / "fields" / "notional.npy", np.ones(shape, dtype=np.float32))
    contracts = [
        {
            "field_id": "notional",
            "value_type": "NOTIONAL",
            "unit": "quote_asset",
            "observable_lag_hours": 1,
            "pit_authority": "TEST",
        }
    ]
    manifest = {
        "schema_version": 1,
        "minimum_assets_per_timestamp": 3,
        "carriers": {
            "TEST": {
                "cache_root": str(root),
                "cache_identity_sha256": metadata["identity_sha256"],
                "directory_bundle": _directory_bundle(root),
                "contracts": contracts,
                "contracts_sha256": _payload_sha(contracts),
            }
        },
    }
    manifest_path = tmp_path / "search_carriers.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    store, loaded, evidence = load_search_surface_carrier(
        tmp_path,
        carrier_manifest_path=manifest_path,
        surface_id="TEST",
    )
    assert store.candidate_support(("notional",)).all()
    assert [item.field_id for item in loaded] == ["notional"]
    assert evidence["minimum_assets_per_timestamp"] == 3


def test_candidate_support_is_field_local_not_full_surface_intersection(
    tmp_path: Path,
) -> None:
    root = tmp_path / "cache"
    (root / "fields").mkdir(parents=True)
    metadata = {
        "assets": 3,
        "timestamps": 2,
        "symbol_ids": ["A", "B", "C"],
        "field_ids": ["left", "right", "unrelated_sparse", "two_only"],
        "target_horizons_hours": [1],
        "minimum_assets_per_timestamp": 3,
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
    two_only = np.ones((3, 2), dtype=np.float32)
    two_only[-1, :] = np.nan
    np.save(root / "fields" / "two_only.npy", two_only)
    np.save(root / "target_return_1h.npy", np.ones((3, 2), dtype=np.float32))

    store = RawPanelStore.open(root)
    support = store.candidate_support(("left", "right"))
    full_surface = store.candidate_support(
        ("left", "right", "unrelated_sparse")
    )
    assert support.all()
    assert not full_surface[:, 0].any()
    assert full_surface[:, 1].all()
    assert not store.candidate_support(("two_only",)).any()


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


def test_oi_materialization_probe_skips_schemafixed_empty_partition(
    tmp_path: Path,
) -> None:
    venue = tmp_path / "compact_1h" / "bybit"
    empty_path = venue / "date=2025-06-28" / "part.parquet"
    full_path = venue / "date=2025-06-29" / "part.parquet"
    empty_path.parent.mkdir(parents=True)
    full_path.parent.mkdir(parents=True)
    schema = pa.schema(
        [
            pa.field("venue", pa.string()),
            pa.field("base_asset", pa.string()),
            pa.field("timestamp", pa.timestamp("us", tz="UTC")),
            pa.field("open_interest_last", pa.float64()),
            pa.field("feature_available_time", pa.timestamp("us", tz="UTC")),
            pa.field("execution_time_min", pa.timestamp("us", tz="UTC")),
        ]
    )
    pq.write_table(pa.Table.from_pylist([], schema=schema), empty_path)
    pq.write_table(
        pa.Table.from_pylist(
            [
                {
                    "venue": "bybit",
                    "base_asset": "BTC",
                    "timestamp": pd.Timestamp("2025-06-29T00:00:00Z"),
                    "open_interest_last": 1.0,
                    "feature_available_time": pd.Timestamp(
                        "2025-06-29T01:00:00Z"
                    ),
                    "execution_time_min": pd.Timestamp(
                        "2025-06-29T01:01:00Z"
                    ),
                }
            ],
            schema=schema,
        ),
        full_path,
    )
    contracts, stats, evidence = _oi_mark_surface(tmp_path)
    assert [row.field_id for row in contracts] == [
        "bybit__open_interest_last"
    ]
    assert stats == {"bybit__open_interest_last": 1.0}
    assert evidence[0]["sample_rows"] == 1
    assert evidence[0]["sample_path"] == str(full_path)


def test_raw_panel_store_normalizes_legacy_microsecond_timestamps(
    tmp_path: Path,
) -> None:
    root = tmp_path / "carrier"
    root.mkdir()
    (root / "metadata.json").write_text(
        json.dumps(
            {
                "assets": 1,
                "timestamps": 2,
                "symbol_ids": ["A"],
                "field_ids": [],
            }
        ),
        encoding="utf-8",
    )
    np.save(
        root / "timestamp_ns.npy",
        np.asarray(
            [1_704_067_200_000_000, 1_704_070_800_000_000],
            dtype=np.int64,
        ),
    )
    store = RawPanelStore.open(root)
    assert store.timestamp_ns.tolist() == [
        1_704_067_200_000_000_000,
        1_704_070_800_000_000_000,
    ]
