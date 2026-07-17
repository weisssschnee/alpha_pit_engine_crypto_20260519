from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from alphafactory_crypto.liquidation_ingress import (
    classify_contract,
    preflight_supplier_release,
    qualify_overlap,
)


def _fixture(tmp_path: Path) -> tuple[dict, Path]:
    root = tmp_path / "release"
    rows = []
    for date in ("2025-06-28", "2025-06-29"):
        start = pd.Timestamp(date, tz="UTC")
        events = pd.DataFrame(
            [
                {
                    "event_time_utc": start + pd.Timedelta(minutes=5),
                    "observable_time": start + pd.Timedelta(minutes=5, seconds=1),
                    "symbol": symbol,
                    "side": side,
                    "effective_quantity": quantity,
                    "effective_price": price,
                    "liquidation_notional": quantity * price,
                    "liquidation_direction": direction,
                    "source_key": f"supplier/{date}/{symbol}",
                }
                for symbol, side, quantity, price, direction in (
                    ("BTCUSDT", "BUY", 1.0, 20_000.0, "SHORT_LIQUIDATION"),
                    ("ETHUSDT", "SELL", 10.0, 2_000.0, "LONG_LIQUIDATION"),
                    ("BTCUSD_PERP", "BUY", 100.0, 20_000.0, "SHORT_LIQUIDATION"),
                )
            ]
        )
        silver_path = root / "silver/events_daily" / f"date={date}" / "part-000.parquet"
        silver_path.parent.mkdir(parents=True, exist_ok=True)
        events.to_parquet(silver_path, index=False)
        gold_rows = []
        for event in events.itertuples():
            timestamp = start
            gold_rows.append(
                {
                    "symbol": event.symbol,
                    "timestamp": timestamp,
                    "liquidation_event_count": 1,
                    "liquidation_buy_count": int(event.side == "BUY"),
                    "liquidation_sell_count": int(event.side == "SELL"),
                    "liquidation_total_notional": event.liquidation_notional,
                    "liquidation_event_notional_max": event.liquidation_notional,
                    "first_observable_time": event.observable_time,
                    "last_observable_time": event.observable_time,
                    "feature_available_time": timestamp + pd.Timedelta(hours=1),
                    "execution_time_min": timestamp + pd.Timedelta(hours=2),
                    "exact_duplicate_rows_dropped": 0,
                }
            )
        gold_path = root / "gold/hourly_sparse" / f"date={date}" / "part-000.parquet"
        gold_path.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(gold_rows).to_parquet(gold_path, index=False)
        rows.extend(events.to_dict("records"))
    summary = {
        "status": "complete",
        "parse_error_count": 0,
        "unknown_side_count": 0,
        "source_date_mismatch_count": 0,
    }
    (root / "summary.json").write_text(json.dumps(summary), encoding="utf-8")
    config = {
        "release": {
            "release_id": "TEST_RELEASE",
            "root": root.as_posix(),
            "start_date": "2025-06-28",
            "end_date": "2025-06-29",
            "silver_layer": "silver/events_daily",
            "gold_layer": "gold/hourly_sparse",
            "expected_summary": {
                "daily_partition_count": 2,
                "silver_rows": 6,
                "gold_rows": 6,
                "symbol_count": 3,
                "event_count": 6,
                "parse_error_count": 0,
                "unknown_side_count": 0,
                "source_date_mismatch_count": 0,
            },
        },
        "hash_workers": 2,
        "schemas": {
            "silver_required": list(pd.DataFrame(rows).columns),
            "gold_required": list(pd.read_parquet(gold_path).columns),
        },
        "overlap_gate": {
            "minimum_overlap_days": 2,
            "minimum_common_symbols": 2,
            "minimum_ws_events": 4,
            "minimum_large_events_per_threshold": 1,
            "minimum_event_count_coverage": 0.8,
            "minimum_notional_coverage": 0.8,
            "minimum_large_count_coverage": 0.75,
            "large_notional_thresholds": [10000],
            "vendor_mapping": {
                "event_time": ["event_time_utc"],
                "symbol": ["symbol"],
                "side": ["side"],
                "notional": ["liquidation_notional"],
                "quantity": ["effective_quantity"],
                "price": ["effective_price"],
            },
            "ws_mapping": {
                "event_time": ["event_time_utc", "E", "T"],
                "symbol": ["symbol", "o.s"],
                "side": ["side", "o.S"],
                "notional": ["liquidation_notional"],
                "quantity": ["effective_quantity", "o.z", "o.q"],
                "price": ["effective_price", "o.ap", "o.p"],
            },
        },
        "boundaries": {"research_input_allowed": False},
    }
    return config, root


def test_supplier_release_is_qualified_but_quarantined(tmp_path: Path) -> None:
    config, _ = _fixture(tmp_path)
    result = preflight_supplier_release(config).evidence
    assert result["status"] == "QUALIFIED_QUARANTINED"
    assert result["research_admitted"] is False
    assert result["partition_files"] == 4
    assert result["observed"]["event_count"] == 6
    assert "BTCUSD_PERP" in result["quarantined_notional_symbols"]


def test_contract_classification_does_not_treat_inverse_quantity_as_base_asset() -> None:
    assert classify_contract("BTCUSDT") == "LINEAR_QUOTE_MARGIN"
    assert classify_contract("BTCUSDC") == "LINEAR_QUOTE_MARGIN"
    assert classify_contract("BTCUSD_PERP") == "INVERSE_OR_DELIVERY"
    assert classify_contract("BTCUSD_260925") == "INVERSE_OR_DELIVERY"


def test_overlap_is_blocked_without_ws_input(tmp_path: Path) -> None:
    config, _ = _fixture(tmp_path)
    preflight = preflight_supplier_release(config).evidence
    result, comparison = qualify_overlap(config, preflight, None)
    assert result["status"] == "STITCHING_BLOCKED_NO_WS_OVERLAP_INPUT"
    assert result["stitching_allowed"] is False
    assert comparison.empty


def test_equivalent_ws_overlap_passes_but_never_auto_stitches(tmp_path: Path) -> None:
    config, root = _fixture(tmp_path)
    preflight = preflight_supplier_release(config).evidence
    ws_root = tmp_path / "ws"
    ws_root.mkdir()
    vendor = pd.concat(
        [pd.read_parquet(path) for path in sorted((root / "silver/events_daily").glob("date=*/part-000.parquet"))],
        ignore_index=True,
    )
    vendor.loc[vendor.symbol.isin(["BTCUSDT", "ETHUSDT"])].to_parquet(
        ws_root / "events.parquet", index=False
    )
    result, comparison = qualify_overlap(config, preflight, ws_root)
    assert result["status"] == "STITCHING_ELIGIBLE_PENDING_EXPLICIT_ACTIVATION"
    assert result["comparison_pass"] is True
    assert result["stitching_allowed"] is False
    assert len(comparison) == 4

    drift = pd.read_parquet(ws_root / "events.parquet")
    drift["liquidation_notional"] *= 10
    drift.to_parquet(ws_root / "events.parquet", index=False)
    failed, _ = qualify_overlap(config, preflight, ws_root)
    assert failed["comparison_pass"] is False


def test_binance_nested_force_order_payload_is_supported(tmp_path: Path) -> None:
    config, root = _fixture(tmp_path)
    preflight = preflight_supplier_release(config).evidence
    ws_root = tmp_path / "ws"
    ws_root.mkdir()
    vendor = pd.concat(
        [
            pd.read_parquet(path)
            for path in sorted(
                (root / "silver/events_daily").glob("date=*/part-000.parquet")
            )
        ],
        ignore_index=True,
    )
    linear = vendor.loc[vendor.symbol.isin(["BTCUSDT", "ETHUSDT"])]
    payloads = [
        {
            "e": "forceOrder",
            "E": int(row.event_time_utc.timestamp() * 1000),
            "o": {
                "s": row.symbol,
                "S": row.side,
                "z": str(row.effective_quantity),
                "ap": str(row.effective_price),
            },
        }
        for row in linear.itertuples()
    ]
    (ws_root / "force_orders.jsonl").write_text(
        "\n".join(json.dumps(row) for row in payloads) + "\n", encoding="utf-8"
    )
    result, _ = qualify_overlap(config, preflight, ws_root)
    assert result["comparison_pass"] is True


def test_pit_drift_fails_preflight(tmp_path: Path) -> None:
    config, root = _fixture(tmp_path)
    path = root / "gold/hourly_sparse/date=2025-06-28/part-000.parquet"
    frame = pd.read_parquet(path)
    frame["feature_available_time"] = frame["timestamp"]
    frame.to_parquet(path, index=False)
    result = preflight_supplier_release(config).evidence
    assert result["status"] == "INGRESS_PREFLIGHT_FAILED"
    assert "FEATURE_AVAILABLE_TIME_DRIFT" in result["failures"]
