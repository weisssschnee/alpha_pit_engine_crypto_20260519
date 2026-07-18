from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

from alphafactory_crypto.binance_force_order_capture import (
    CaptureIdentity,
    append_capture_record,
    build_capture_record,
    capture_partition_path,
)
from alphafactory_crypto.liquidation_ingress import normalize_events


def _raw() -> str:
    return json.dumps(
        {
            "e": "forceOrder",
            "E": 1568014460893,
            "o": {
                "s": "BTCUSDT",
                "S": "SELL",
                "q": "0.014",
                "p": "9910",
                "ap": "9910",
                "z": "0.014",
                "T": 1568014460893,
            },
            "ps": "BTCUSDT",
            "st": 1,
        },
        separators=(",", ":"),
    )


def test_capture_record_preserves_exact_exchange_text_and_receive_time() -> None:
    raw = _raw()
    record = build_capture_record(
        raw,
        received_time_ns=1_752_806_400_123_456_789,
        connection_id="connection-1",
        endpoint="wss://fstream.binance.com/market/ws/!forceOrder@arr",
    )
    assert record["raw_text"] == raw
    assert record["raw_sha256"] == hashlib.sha256(raw.encode()).hexdigest().upper()
    assert record["received_time_utc"] == "2025-07-18T02:40:00.123456Z"
    assert record["payload"]["st"] == 1


def test_capture_partition_and_ingress_replay_are_compatible(tmp_path: Path) -> None:
    raw = _raw()
    received = 1_752_806_400_123_456_789
    record = build_capture_record(
        raw,
        received_time_ns=received,
        connection_id="connection-1",
        endpoint="wss://fstream.binance.com/market/ws/!forceOrder@arr",
    )
    path = capture_partition_path(tmp_path, received)
    append_capture_record(path, record)
    frame = pd.read_json(path, lines=True)
    normalized = normalize_events(
        frame,
        {
            "event_time": ["E", "T"],
            "symbol": ["s", "o.s"],
            "side": ["S", "o.S"],
            "notional": ["notional"],
            "quantity": ["z", "q", "o.z", "o.q"],
            "price": ["ap", "p", "o.ap", "o.p"],
        },
    )
    assert normalized.loc[0, "symbol"] == "BTCUSDT"
    assert normalized.loc[0, "notional"] == 0.014 * 9910


def test_capture_identity_is_stable() -> None:
    first = CaptureIdentity("wss://example", "G:/raw").sha256()
    second = CaptureIdentity("wss://example", "G:/raw").sha256()
    assert first == second
