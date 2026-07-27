from __future__ import annotations

import io
import zipfile

import numpy as np
import pandas as pd
import pytest
import pyarrow as pa
import pyarrow.parquet as pq

from alphafactory_crypto.data_admission_v1 import (
    KLINE_COLUMNS,
    _parse_kline_zip,
    assign_instrument_lifecycles,
    build_daily_context,
    build_hourly_schema2_intersection_cache,
    build_lagged_pit_universe,
    classify_symbols,
    coverage_against_temporal_surfaces,
    surface_missing_member_rows,
)


def test_symbol_classification_fails_closed_outside_crypto_surface() -> None:
    exchange_info = {
        "symbols": [
            {
                "symbol": "BTCUSDT",
                "quoteAsset": "USDT",
                "underlyingType": "COIN",
                "contractType": "PERPETUAL",
                "status": "TRADING",
            },
            {
                "symbol": "AAPLUSDT",
                "quoteAsset": "USDT",
                "underlyingType": "EQUITY",
                "contractType": "TRADIFI_PERPETUAL",
                "status": "TRADING",
            },
        ]
    }
    classified = classify_symbols(
        ["BTCUSDT", "AAPLUSDT", "MATICUSDT", "UNKNOWNUSDT"],
        exchange_info,
    ).set_index("symbol")
    assert bool(classified.loc["BTCUSDT", "admitted_crypto_surface"])
    assert bool(classified.loc["MATICUSDT", "admitted_crypto_surface"])
    assert not bool(classified.loc["AAPLUSDT", "admitted_crypto_surface"])
    assert not bool(classified.loc["UNKNOWNUSDT", "admitted_crypto_surface"])
    assert classified.loc["UNKNOWNUSDT", "classification"] == "UNRESOLVED"


def test_lit_ticker_reuse_is_never_stitched_across_identity_gap() -> None:
    daily = pd.DataFrame(
        {
            "symbol": ["LITUSDT"] * 5,
            "date": pd.to_datetime(
                [
                    "2025-01-30",
                    "2025-01-31",
                    "2025-12-01",
                    "2025-12-23",
                    "2025-12-24",
                ],
                utc=True,
            ),
            "quote_volume": [10.0, 11.0, 99.0, 20.0, 21.0],
        }
    )
    assigned, ledger = assign_instrument_lifecycles(daily, gap_days=30)
    by_date = assigned.set_index("date")["instrument_id"]
    assert by_date[pd.Timestamp("2025-01-31", tz="UTC")] == "LITUSDT::L01"
    assert by_date[pd.Timestamp("2025-12-01", tz="UTC")].endswith("::QUARANTINED")
    assert by_date[pd.Timestamp("2025-12-23", tz="UTC")] == "LITUSDT::L02"
    assert set(ledger["admitted"].astype(bool)) == {False, True}


def test_pit_membership_uses_only_prior_completed_days_and_stable_ties() -> None:
    dates = pd.date_range("2024-01-01", periods=6, freq="D", tz="UTC")
    rows = []
    for symbol, volumes in {
        "AUSDT": [10, 10, 10, 10, 10, 10],
        "BUSDT": [10, 10, 10, 10, 10, 10],
        "CUSDT": [1, 1, 1000, 1, 1, 1],
    }.items():
        for date, volume in zip(dates, volumes):
            rows.append(
                {
                    "symbol": symbol,
                    "instrument_id": symbol,
                    "lifecycle_ordinal": 1,
                    "date": date,
                    "quote_volume": float(volume),
                }
            )
    universe, summary = build_lagged_pit_universe(
        pd.DataFrame(rows),
        start_date="2024-01-03",
        end_date="2024-01-04",
        top_n=2,
        trailing_days=2,
        minimum_observed_days=2,
    )
    day_three = universe.loc[
        universe["date"].eq(pd.Timestamp("2024-01-03", tz="UTC"))
    ]
    assert day_three["raw_symbol"].tolist() == ["AUSDT", "BUSDT"]
    day_four = universe.loc[
        universe["date"].eq(pd.Timestamp("2024-01-04", tz="UTC"))
    ]
    assert day_four.iloc[0]["raw_symbol"] == "CUSDT"
    assert summary["top_n_complete"].all()


def test_daily_context_is_cross_sectionally_authoritative() -> None:
    universe = pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2024-01-03", "2024-01-03", "2024-01-04", "2024-01-04"],
                utc=True,
            ),
            "instrument_id": ["A", "B", "A", "B"],
            "raw_symbol": ["A", "B", "A", "B"],
            "rank": [1, 2, 1, 2],
        }
    )
    ledger = pd.DataFrame(
        {
            "instrument_id": ["A", "B"],
            "date_min": pd.to_datetime(["2024-01-01", "2024-01-02"], utc=True),
        }
    )
    context = build_daily_context(universe, ledger)
    assert context["active_universe_size"].tolist() == [2, 2, 2, 2]
    assert context.groupby("date")["age_percentile_active_universe"].max().eq(1).all()
    assert context.loc[context["instrument_id"].eq("A"), "history_length_hours"].tolist() == [
        24,
        48,
    ]


def test_surface_gap_rows_preserve_exact_missing_dates_and_ranks() -> None:
    universe = pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2024-01-01", "2024-01-01", "2024-01-02", "2024-01-02"],
                utc=True,
            ),
            "rank": [1, 2, 1, 2],
            "instrument_id": ["A", "B", "A", "C"],
            "raw_symbol": ["A", "B", "A", "C"],
        }
    )
    rows, summary = surface_missing_member_rows(
        universe,
        surfaces={"SURFACE": {"A"}},
    )
    assert rows[["raw_symbol", "rank"]].values.tolist() == [["B", 2], ["C", 2]]
    assert summary["missing_days"].tolist() == [1, 1]


def test_temporal_surface_does_not_treat_symbol_presence_as_all_date_coverage() -> None:
    universe = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-02"], utc=True),
            "rank": [1, 1],
            "instrument_id": ["A", "A"],
            "raw_symbol": ["A", "A"],
        }
    )
    coverage, missing, _ = coverage_against_temporal_surfaces(
        universe,
        surfaces={
            "SURFACE": {("A", pd.Timestamp("2024-01-02", tz="UTC"))}
        },
    )
    assert coverage["covered_count"].tolist() == [0, 1]
    assert coverage["coverage_rate"].tolist() == [0.0, 1.0]
    assert missing["date"].tolist() == [pd.Timestamp("2024-01-01", tz="UTC")]


def test_official_kline_zip_schema_and_month_are_validated() -> None:
    csv = (
        ",".join(KLINE_COLUMNS)
        + "\n"
        + "1704067200000,1,2,0.5,1.5,2,1704153599999,100,3,1,50,0\n"
    ).encode()
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("BTCUSDT-1d-2024-01.csv", csv)
    parsed = _parse_kline_zip(buffer.getvalue(), symbol="BTCUSDT", month="2024-01")
    assert parsed.loc[0, "quote_volume"] == pytest.approx(100.0)
    with pytest.raises(ValueError, match="outside"):
        _parse_kline_zip(buffer.getvalue(), symbol="BTCUSDT", month="2024-02")


def test_hourly_schema2_cache_rebuilds_context_after_symbol_join(tmp_path) -> None:
    root = tmp_path / "v3"
    timestamps = pd.date_range("2024-01-01", periods=4, freq="h", tz="UTC")
    for symbol, start_age in [("AUSDT", 100.0), ("BUSDT", 10.0)]:
        path = root / f"symbol={symbol}" / "part.parquet"
        path.parent.mkdir(parents=True)
        pq.write_table(
            pa.Table.from_pydict(
                {
                    "timestamp": timestamps,
                    "listing_age_hours": [
                        start_age + offset for offset in range(len(timestamps))
                    ],
                }
            ),
            path,
        )
    universe = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-01"], utc=True),
            "instrument_id": ["AUSDT", "BUSDT"],
            "raw_symbol": ["AUSDT", "BUSDT"],
            "rank": [1, 2],
        }
    )
    identity = build_hourly_schema2_intersection_cache(
        universe=universe,
        identity_ledger=pd.DataFrame(
            {
                "raw_symbol": ["AUSDT", "BUSDT"],
                "instrument_id": ["AUSDT", "BUSDT"],
                "date_min": pd.to_datetime(
                    ["2024-01-01", "2024-01-01"], utc=True
                ),
                "admitted": [True, True],
            }
        ),
        v3_root=root,
        cache_root=tmp_path / "cache",
    )
    assert identity["cache_schema_version"] == 2
    assert identity["search_reuse_authorized"]
    assert identity["active_universe_min"] == 2
    assert identity["active_universe_max"] == 2
    assert set(identity["array_sha256"]) == {
        "active_universe_size.npy",
        "age_percentile_active_universe.npy",
        "history_length_hours.npy",
        "listing_age_hours.npy",
        "observed.npy",
        "timestamp_ns.npy",
    }


def test_hourly_schema2_cache_resets_age_for_reused_ticker_lifecycle(
    tmp_path,
) -> None:
    root = tmp_path / "v3"
    timestamps = pd.date_range("2024-01-01", periods=48, freq="h", tz="UTC")
    path = root / "symbol=XUSDT" / "part.parquet"
    path.parent.mkdir(parents=True)
    pq.write_table(
        pa.Table.from_pydict(
            {
                "timestamp": timestamps,
                "listing_age_hours": [1000.0 + offset for offset in range(48)],
            }
        ),
        path,
    )
    universe = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-02"], utc=True),
            "instrument_id": ["XUSDT::L01", "XUSDT::L02"],
            "raw_symbol": ["XUSDT", "XUSDT"],
            "rank": [1, 1],
        }
    )
    ledger = pd.DataFrame(
        {
            "raw_symbol": ["XUSDT", "XUSDT"],
            "instrument_id": ["XUSDT::L01", "XUSDT::L02"],
            "date_min": pd.to_datetime(["2024-01-01", "2024-01-02"], utc=True),
            "admitted": [True, True],
        }
    )
    build_hourly_schema2_intersection_cache(
        universe=universe,
        identity_ledger=ledger,
        v3_root=root,
        cache_root=tmp_path / "cache",
    )
    ages = np.load(tmp_path / "cache" / "listing_age_hours.npy")
    assert ages[0, 0] == pytest.approx(0.0)
    assert ages[0, 23] == pytest.approx(23.0)
    assert ages[0, 24] == pytest.approx(0.0)
