from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from alphafactory_crypto.bitfinex_liquidation_ingress import (
    classify_symbol,
    preflight_bitfinex_release,
)


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fixture(tmp_path: Path) -> dict:
    root = tmp_path / "bitfinex"
    resolutions = ["1min", "5min", "15min", "1h"]
    for month, end in (("2024-01", "2024-01-31"), ("2024-02", "2024-02-29")):
        start = pd.Timestamp(f"{month}-01", tz="UTC")
        silver = pd.DataFrame(
            [
                {
                    "timestamp": start + pd.Timedelta(minutes=minute),
                    "venue": "bitfinex_derivatives",
                    "symbol": symbol,
                    "side": side,
                    "quantity": quantity,
                    "price": price,
                    "notional": quantity * price,
                    "position_id": 1000 + index,
                    "is_match": 1,
                    "is_market_sold": int(side == "LONG"),
                    "source_observable_time": start + pd.Timedelta(minutes=minute),
                }
                for index, (minute, symbol, side, quantity, price) in enumerate(
                    (
                        (5, "tBTCF0:USTF0", "LONG", 1.0, 20_000.0),
                        (6, "tETHF0:USTF0", "SHORT", 10.0, 2_000.0),
                        (7, "tETHF0:BTCF0", "LONG", 2.0, 0.05),
                    )
                )
            ]
        )
        silver_path = root / "silver" / f"month={month}" / "part.parquet"
        silver_path.parent.mkdir(parents=True, exist_ok=True)
        silver.to_parquet(silver_path, index=False)
        raw_path = root / "raw" / f"bitfinex_liquidations_{month}.json.gz"
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        with gzip.open(raw_path, "wt", encoding="utf-8") as handle:
            json.dump([{"row": index} for index in range(3)], handle)
        gold_counts = {}
        for resolution in resolutions:
            work = silver.copy()
            work["timestamp"] = work["timestamp"].dt.floor(resolution)
            work["long"] = work.notional.where(work.side.eq("LONG"), 0.0)
            work["short"] = work.notional.where(work.side.eq("SHORT"), 0.0)
            gold = (
                work.groupby(["venue", "symbol", "timestamp"], sort=True)
                .agg(
                    liquidation_count=("notional", "size"),
                    liquidation_notional=("notional", "sum"),
                    max_liquidation_notional=("notional", "max"),
                    long_liquidation_notional=("long", "sum"),
                    short_liquidation_notional=("short", "sum"),
                )
                .reset_index()
            )
            gold["liquidation_imbalance"] = np.where(
                gold.liquidation_notional.gt(0),
                (gold.short_liquidation_notional - gold.long_liquidation_notional)
                / gold.liquidation_notional,
                0.0,
            )
            gold["feature_available_time"] = gold.timestamp + pd.Timedelta(resolution)
            gold["execution_time_min"] = gold.feature_available_time + pd.Timedelta(hours=1)
            gold_path = root / "gold" / resolution / f"month={month}" / "part.parquet"
            gold_path.parent.mkdir(parents=True, exist_ok=True)
            gold.to_parquet(gold_path, index=False)
            gold_counts[resolution] = len(gold)
        manifest = {
            "status": "ok",
            "month": month,
            "start": f"{month}-01",
            "end": end,
            "raw_rows": 3,
            "silver_rows": 3,
            "gold_rows": gold_counts,
            "raw_sha256": _hash(raw_path),
            "source": "https://api-pub.bitfinex.com/v2/liquidations/hist",
        }
        manifest_path = root / "manifests" / f"{month}.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    (root / "status.json").write_text(
        json.dumps({"status": "complete", "completed_months": 2, "total_months": 2}),
        encoding="utf-8",
    )
    return {
        "release": {
            "release_id": "TEST_BITFINEX",
            "root": root.as_posix(),
            "start_date": "2024-01-01",
            "end_date": "2024-02-29",
            "source": "https://api-pub.bitfinex.com/v2/liquidations/hist",
            "publication_time_available": False,
            "source_interval_coverage_ledger": None,
        },
        "gold_resolutions": resolutions,
        "schemas": {
            "silver_required": [
                "timestamp",
                "venue",
                "symbol",
                "side",
                "quantity",
                "price",
                "notional",
                "position_id",
                "is_match",
                "is_market_sold",
                "source_observable_time",
            ]
        },
        "large_event_thresholds": [10000, 100000],
        "event_data_adequacy": {
            "minimum_eligible_events": 1,
            "minimum_active_event_dates": 1,
            "minimum_eligible_symbols": 2,
            "minimum_effective_months": 1.0,
            "minimum_effective_symbols": 1.0,
            "minimum_price_label_match_ratio": 0.8,
            "minimum_turnover_observations": 10,
        },
        "boundaries": {"research_input_allowed": False},
    }


def test_internal_layers_pass_but_source_coverage_and_research_remain_unqualified(
    tmp_path: Path,
) -> None:
    result = preflight_bitfinex_release(_fixture(tmp_path)).evidence
    assert result["internal_file_and_aggregation_checks_pass"] is True
    assert result["status"] == "FILE_INTEGRITY_QUALIFIED_SOURCE_COVERAGE_UNVERIFIED"
    assert result["source_interval_completeness_verified"] is False
    assert result["data_adequacy"]["status"] == "DATA_ADEQUACY_UNDERPOWERED"
    assert result["research_admitted"] is False
    assert result["binance_reference_allowed"] is False
    assert result["cryptohft_coverage_validation_allowed"] is False


def test_symbol_semantics_quarantine_non_ust_and_test_contracts() -> None:
    assert classify_symbol("tBTCF0:USTF0") == "USTF0_QUOTE_PROXY"
    assert classify_symbol("tETHF0:BTCF0") == "NON_UST_DERIVATIVE_QUOTE_QUARANTINED"
    assert classify_symbol("TESTBTCF0:TESTUSDTF0") == "TEST_SYMBOL_QUARANTINED"
    assert classify_symbol("tBTCUSD") == "LEGACY_OR_UNKNOWN_SYMBOL_QUARANTINED"


def test_raw_hash_drift_fails_preflight(tmp_path: Path) -> None:
    config = _fixture(tmp_path)
    root = Path(config["release"]["root"])
    path = root / "raw/bitfinex_liquidations_2024-01.json.gz"
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        json.dump([{"row": index, "drift": True} for index in range(3)], handle)
    result = preflight_bitfinex_release(config).evidence
    assert result["status"] == "INGRESS_PREFLIGHT_FAILED"
    assert "RAW_SHA256_MISMATCH:2024-01" in result["failures"]


def test_gold_delay_drift_fails_preflight(tmp_path: Path) -> None:
    config = _fixture(tmp_path)
    root = Path(config["release"]["root"])
    path = root / "gold/1h/month=2024-01/part.parquet"
    frame = pd.read_parquet(path)
    frame["feature_available_time"] = frame["timestamp"]
    frame.to_parquet(path, index=False)
    result = preflight_bitfinex_release(config).evidence
    assert result["status"] == "INGRESS_PREFLIGHT_FAILED"
    assert "GOLD_1h_FEATURE_AVAILABLE_TIME_DRIFT" in result["failures"]
