"""Provenance-safe capture helpers for Binance native forceOrder messages.

Capture records preserve the exact received text plus the parsed exchange
payload and local receive time.  They are raw ingress evidence only: this
module does not normalize, stitch, aggregate, or authorize research use.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping


CAPTURE_SCHEMA_VERSION = 1
SOURCE_ID = "BINANCE_NATIVE_FORCE_ORDER_WS"


def utc_iso_from_ns(value: int) -> str:
    seconds, nanoseconds = divmod(int(value), 1_000_000_000)
    timestamp = datetime.fromtimestamp(seconds, tz=timezone.utc) + timedelta(
        microseconds=nanoseconds // 1_000
    )
    return timestamp.isoformat(
        timespec="microseconds"
    ).replace("+00:00", "Z")


def build_capture_record(
    raw_text: str,
    *,
    received_time_ns: int,
    connection_id: str,
    endpoint: str,
) -> dict[str, Any]:
    """Bind an exact WS message to receive provenance without changing payload."""

    payload = json.loads(raw_text)
    if not isinstance(payload, Mapping):
        raise ValueError("forceOrder payload must be a JSON object")
    if payload.get("e") != "forceOrder":
        raise ValueError("unexpected Binance event type")
    order = payload.get("o")
    if not isinstance(order, Mapping) or not order.get("s"):
        raise ValueError("forceOrder payload is missing its order object or symbol")
    raw_bytes = raw_text.encode("utf-8")
    return {
        "capture_schema_version": CAPTURE_SCHEMA_VERSION,
        "source_id": SOURCE_ID,
        "stream": "!forceOrder@arr",
        "endpoint": endpoint,
        "connection_id": connection_id,
        "received_time_ns": int(received_time_ns),
        "received_time_utc": utc_iso_from_ns(int(received_time_ns)),
        "raw_sha256": hashlib.sha256(raw_bytes).hexdigest().upper(),
        "raw_text": raw_text,
        "payload": dict(payload),
    }


def capture_partition_path(root: Path, received_time_ns: int) -> Path:
    timestamp = datetime.fromtimestamp(
        received_time_ns / 1_000_000_000, tz=timezone.utc
    )
    return (
        root
        / f"date={timestamp:%Y-%m-%d}"
        / f"hour={timestamp:%H}"
        / "force_orders.jsonl"
    )


def append_capture_record(path: Path, record: Mapping[str, Any]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = (
        json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + "\n"
    ).encode("utf-8")
    with path.open("ab", buffering=0) as handle:
        handle.write(encoded)
    return len(encoded)


@dataclass(frozen=True, slots=True)
class CaptureIdentity:
    endpoint: str
    output_root: str
    stream: str = "!forceOrder@arr"
    source_id: str = SOURCE_ID

    def sha256(self) -> str:
        payload = json.dumps(
            {
                "endpoint": self.endpoint,
                "output_root": self.output_root,
                "source_id": self.source_id,
                "stream": self.stream,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(payload).hexdigest().upper()


__all__ = [
    "CAPTURE_SCHEMA_VERSION",
    "SOURCE_ID",
    "CaptureIdentity",
    "append_capture_record",
    "build_capture_record",
    "capture_partition_path",
    "utc_iso_from_ns",
]
