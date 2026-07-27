from __future__ import annotations

import hashlib
import io
import json
import tarfile
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from alphafactory_crypto.broad_search.expression import TypedExpressionRegistry
from alphafactory_crypto.broad_search.panel18m import RawPanelStore, infer_family
from alphafactory_crypto.broad_search.search_engine_v1 import (
    AGGTRADES_CANARY_ARMS,
    SEEDS,
    _aggtrades_canary_contracts,
    _broad39_registry_contracts,
    _initial_policies,
    _validate_aggtrades_canary_config,
)
from alphafactory_crypto.data_admission_v1 import (
    AGGTRADES_SEARCH_FIELDS,
    AGGTRADES_SYSTEM_CANARY_FIELDS,
    build_aggtrades_search_surface_cache,
    build_aggtrades_system_canary_cache,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_source_cache(root: Path, symbols: list[str]) -> None:
    root.mkdir()
    (root / "fields").mkdir()
    timestamps = pd.date_range(
        "2024-01-01T00:00:00Z", periods=2, freq="h"
    ).asi8
    shape = (len(symbols), len(timestamps))
    fields = (
        "active_universe_size",
        "age_percentile_active_universe",
        "history_length_hours",
        "listing_age_hours",
        "trade_count",
    )
    np.save(root / "timestamp_ns.npy", timestamps)
    np.save(root / "observed.npy", np.ones(shape, dtype=bool))
    np.save(root / "base_eligible.npy", np.ones(shape, dtype=bool))
    np.save(root / "source_segment.npy", np.ones(shape, dtype=np.int8))
    for field in fields:
        values = np.ones(shape, dtype=np.float32)
        if field == "listing_age_hours":
            values = np.arange(len(symbols), dtype=np.float32)[:, None] + np.ones(
                shape, dtype=np.float32
            )
        np.save(root / "fields" / f"{field}.npy", values)
    for horizon in (1, 4):
        np.save(
            root / f"target_return_{horizon}h.npy",
            np.full(shape, 0.001 * horizon, dtype=np.float32),
        )
    metadata = {
        "schema_version": 1,
        "surface_id": "TEST_SOURCE",
        "identity_sha256": "A" * 64,
        "assets": len(symbols),
        "timestamps": len(timestamps),
        "symbol_ids": symbols,
        "field_ids": list(fields),
        "target_horizons_hours": [1, 4],
        "target_formula": "test",
    }
    (root / "metadata.json").write_text(
        json.dumps(metadata), encoding="utf-8"
    )


def _minute_frame(symbol_index: int, *, drop_last: bool) -> pd.DataFrame:
    timestamp = pd.date_range(
        "2024-01-01T00:00:00Z", periods=120, freq="min"
    )
    if drop_last:
        timestamp = timestamp[:-1]
    rows = len(timestamp)
    return pd.DataFrame(
        {
            "timestamp": timestamp,
            "agg_trade_count": np.ones(rows, dtype=np.int64),
            "underlying_trade_count": np.full(rows, 2.0),
            "quantity": np.full(rows, 2.0),
            "notional": np.full(rows, 20.0),
            "buy_agg_trade_count": np.ones(rows, dtype=np.int64),
            "sell_agg_trade_count": np.ones(rows, dtype=np.int64),
            "buy_underlying_trade_count": np.ones(rows, dtype=np.int64),
            "sell_underlying_trade_count": np.ones(rows, dtype=np.int64),
            "buy_quantity": np.full(rows, 1.2),
            "sell_quantity": np.full(rows, 0.8),
            "buy_notional": np.full(rows, 12.0),
            "sell_notional": np.full(rows, 8.0),
            "signed_aggressor_quantity": np.full(rows, 0.4),
            "signed_aggressor_notional": np.full(rows, 4.0),
            "trade_count_le_100": np.ones(rows, dtype=np.int64),
            "trade_count_100_1k": np.ones(rows, dtype=np.int64),
            "trade_count_1k_10k": np.ones(rows, dtype=np.int64),
            "trade_count_10k_100k": np.ones(rows, dtype=np.int64),
            "trade_count_100k_1m": np.ones(rows, dtype=np.int64),
            "trade_count_gt_1m": np.ones(rows, dtype=np.int64),
            "notional_le_100": np.full(rows, 1.0),
            "notional_100_1k": np.full(rows, 2.0),
            "notional_1k_10k": np.full(rows, 3.0),
            "notional_10k_100k": np.full(rows, 4.0),
            "notional_100k_1m": np.full(rows, 5.0),
            "notional_gt_1m": np.full(rows, 5.0),
            "high_price": np.full(rows, 11.0 + symbol_index * 0.001),
            "low_price": np.full(rows, 9.0),
            "open_price": np.full(rows, 10.0),
            "close_price": np.full(rows, 10.5),
            "max_trade_notional": np.full(rows, 7.0),
            "large_trade_count_100k_plus": np.zeros(rows, dtype=np.int64),
            "large_notional_100k_plus": np.zeros(rows),
            "feature_available_time": timestamp + pd.Timedelta(minutes=1),
            "execution_time_min": timestamp + pd.Timedelta(minutes=2),
        }
    )


def _write_tar(path: Path, symbols: list[str], *, first_symbol_incomplete: bool) -> None:
    root = path.stem
    with tarfile.open(path, "w:") as archive:
        for index, symbol in enumerate(symbols):
            frame = _minute_frame(
                index, drop_last=first_symbol_incomplete and index == 0
            )
            sink = io.BytesIO()
            pq.write_table(pa.Table.from_pandas(frame, preserve_index=False), sink)
            payload = sink.getvalue()
            member = tarfile.TarInfo(
                f"{root}/compact_1m/symbol={symbol}/month=2024-01/part.parquet"
            )
            member.size = len(payload)
            archive.addfile(member, io.BytesIO(payload))
    Path(str(path) + ".sha256").write_text(
        f"{_sha256(path)} *{path.name}\n", encoding="utf-8"
    )


def test_aggtrades_cache_bridge_is_hourly_pit_safe_and_missingness_preserving(
    tmp_path: Path,
) -> None:
    symbols = [f"S{index:03d}USDT" for index in range(50)]
    source = tmp_path / "source"
    _write_source_cache(source, symbols)
    top = tmp_path / "top100.tar"
    ranks = tmp_path / "ranks101_200.tar"
    _write_tar(top, symbols[:25], first_symbol_incomplete=True)
    _write_tar(ranks, symbols[25:], first_symbol_incomplete=False)
    output = tmp_path / "canary"
    metadata = build_aggtrades_system_canary_cache(
        source_cache_root=source,
        top100_tar=top,
        ranks101_200_tar=ranks,
        output_cache_root=output,
        broad_field_ids=[
            "active_universe_size",
            "age_percentile_active_universe",
            "history_length_hours",
            "listing_age_hours",
            "trade_count",
        ],
        start="2024-01-01T00:00:00Z",
        end_exclusive="2024-01-01T02:00:00Z",
        producer_source_sha="B" * 40,
        verify_tar_sha256=True,
    )
    store = RawPanelStore.open(output)
    observed = np.asarray(store.observed())
    assert metadata["assets"] == 50
    assert metadata["timestamps"] == 2
    assert not observed[0, 1]
    assert int(observed[:, 1].sum()) == 49
    assert float(store.field("active_universe_size")[1, 1]) == 49.0
    assert float(store.field("agg_trade_count")[1, 0]) == 60.0
    assert np.isnan(store.field("agg_trade_count")[0, 1])
    assert set(AGGTRADES_SYSTEM_CANARY_FIELDS).issubset(
        set(store.metadata["field_ids"])
    )
    assert build_aggtrades_system_canary_cache(
        source_cache_root=source,
        top100_tar=top,
        ranks101_200_tar=ranks,
        output_cache_root=output,
        broad_field_ids=["trade_count"],
        start="2024-01-01T00:00:00Z",
        end_exclusive="2024-01-01T02:00:00Z",
        producer_source_sha="B" * 40,
    ) == metadata


def test_aggtrades_search_surface_cache_materializes_all_delivered_fields(
    tmp_path: Path,
) -> None:
    symbols = [f"S{index:03d}USDT" for index in range(50)]
    source = tmp_path / "source"
    _write_source_cache(source, symbols)
    top = tmp_path / "top100.tar"
    ranks = tmp_path / "ranks101_200.tar"
    _write_tar(top, symbols[:25], first_symbol_incomplete=False)
    _write_tar(ranks, symbols[25:], first_symbol_incomplete=False)
    output = tmp_path / "search_surface"

    metadata = build_aggtrades_search_surface_cache(
        source_cache_root=source,
        top100_tar=top,
        ranks101_200_tar=ranks,
        output_cache_root=output,
        broad_field_ids=[
            "active_universe_size",
            "age_percentile_active_universe",
            "history_length_hours",
            "listing_age_hours",
            "trade_count",
        ],
        start="2024-01-01T00:00:00Z",
        end_exclusive="2024-01-01T02:00:00Z",
        producer_source_sha="C" * 40,
        verify_tar_sha256=True,
    )

    store = RawPanelStore.open(output)
    assert metadata["cache_role"] == (
        "AGGTRADES_TOP200_SEARCH_SURFACE_RAW_PANEL_STORE"
    )
    assert set(AGGTRADES_SEARCH_FIELDS).issubset(
        set(store.metadata["field_ids"])
    )
    for field_id in AGGTRADES_SEARCH_FIELDS:
        assert np.isfinite(float(store.field(field_id)[0, 0])), field_id


def test_canary_profile_is_three_arm_fresh_state_and_typed() -> None:
    root = Path(__file__).resolve().parents[1]
    config = json.loads(
        (root / "config/crypto_aggtrades_system_canary_v1.json").read_text(
            encoding="utf-8"
        )
    )
    _validate_aggtrades_canary_config(config)
    contracts = _aggtrades_canary_contracts()
    assert {item.field_id for item in contracts} == set(
        AGGTRADES_SYSTEM_CANARY_FIELDS
    )
    assert infer_family("agg_trade_count") == "quote_volume_activity"
    assert infer_family("vwap") == "price_level"
    assert infer_family("close_to_open_bps") == "price_return"
    broad_contracts, _, _ = _broad39_registry_contracts(root)
    policies = _initial_policies(
        TypedExpressionRegistry((*broad_contracts, *contracts)),
        arms=AGGTRADES_CANARY_ARMS,
        seeds=SEEDS,
    )
    assert len(policies) == len(AGGTRADES_CANARY_ARMS) * len(SEEDS)
    assert not any("cem_distribution_v1" in key for key in policies)
    assert not any("evolutionary_typed_v1" in key for key in policies)
