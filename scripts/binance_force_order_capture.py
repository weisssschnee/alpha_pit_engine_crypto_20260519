from __future__ import annotations

import argparse
import asyncio
import json
import os
import random
import signal
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from alphafactory_crypto.binance_force_order_capture import (  # noqa: E402
    CaptureIdentity,
    append_capture_record,
    build_capture_record,
    capture_partition_path,
)


def _write_json_atomic(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    os.replace(temporary, path)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00", "Z"
    )


async def collect(
    config: dict[str, Any], *, max_messages: int | None, max_seconds: float | None
) -> dict[str, Any]:
    import websockets

    endpoint = str(config["endpoint"])
    if endpoint not in {
        "wss://fstream.binance.com/market/ws/!forceOrder@arr",
        "wss://stream.binancefuture.com/market/ws/!forceOrder@arr",
    }:
        raise ValueError("endpoint is outside the frozen Binance forceOrder allowlist")
    output_root = Path(config["output_root"])
    if not output_root.is_absolute():
        output_root = ROOT / output_root
    state_root = ROOT / config["state_root"]
    state_path = state_root / "collector_state.json"
    identity = CaptureIdentity(endpoint, output_root.as_posix())
    started = time.monotonic()
    started_at = _now()
    stop = asyncio.Event()
    counts = {
        "connections": 0,
        "messages": 0,
        "bytes_written": 0,
        "parse_failures": 0,
        "connection_failures": 0,
    }
    last_received = None
    current_file = None
    last_error = None

    def request_stop(*_: object) -> None:
        stop.set()

    loop = asyncio.get_running_loop()
    for name in ("SIGINT", "SIGTERM"):
        if hasattr(signal, name):
            try:
                loop.add_signal_handler(getattr(signal, name), request_stop)
            except (NotImplementedError, RuntimeError):
                pass

    def state(status: str) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "status": status,
            "capture_id": config["capture_id"],
            "capture_identity_sha256": identity.sha256(),
            "pid": os.getpid(),
            "started_at": started_at,
            "checked_at": _now(),
            "endpoint": endpoint,
            "stream": config["stream"],
            "output_root": output_root.as_posix(),
            "current_file": current_file,
            "last_received_time_utc": last_received,
            "last_error": last_error,
            "counts": dict(counts),
            "boundaries": config["boundaries"],
        }

    _write_json_atomic(state_path, state("STARTING"))
    backoff = float(config["connection"]["minimum_reconnect_seconds"])
    maximum_backoff = float(config["connection"]["maximum_reconnect_seconds"])
    while not stop.is_set():
        if max_seconds is not None and time.monotonic() - started >= max_seconds:
            break
        connection_id = uuid.uuid4().hex
        try:
            async with websockets.connect(
                endpoint,
                ping_interval=float(config["connection"]["ping_interval_seconds"]),
                ping_timeout=float(config["connection"]["ping_timeout_seconds"]),
                close_timeout=float(config["connection"]["close_timeout_seconds"]),
                max_size=int(config["connection"]["maximum_message_bytes"]),
            ) as websocket:
                counts["connections"] += 1
                backoff = float(config["connection"]["minimum_reconnect_seconds"])
                last_error = None
                _write_json_atomic(state_path, state("RUNNING"))
                while not stop.is_set():
                    remaining = None
                    if max_seconds is not None:
                        remaining = max_seconds - (time.monotonic() - started)
                        if remaining <= 0:
                            stop.set()
                            break
                    try:
                        raw = await asyncio.wait_for(
                            websocket.recv(), timeout=min(30.0, remaining) if remaining else 30.0
                        )
                    except asyncio.TimeoutError:
                        _write_json_atomic(state_path, state("RUNNING"))
                        continue
                    if isinstance(raw, bytes):
                        raw = raw.decode("utf-8")
                    received_ns = time.time_ns()
                    try:
                        record = build_capture_record(
                            raw,
                            received_time_ns=received_ns,
                            connection_id=connection_id,
                            endpoint=endpoint,
                        )
                    except (ValueError, json.JSONDecodeError) as exc:
                        counts["parse_failures"] += 1
                        last_error = f"{type(exc).__name__}:{exc}"
                        _write_json_atomic(state_path, state("RUNNING_WITH_PARSE_FAILURE"))
                        continue
                    path = capture_partition_path(output_root, received_ns)
                    counts["bytes_written"] += append_capture_record(path, record)
                    counts["messages"] += 1
                    current_file = path.as_posix()
                    last_received = record["received_time_utc"]
                    _write_json_atomic(state_path, state("RUNNING"))
                    if max_messages is not None and counts["messages"] >= max_messages:
                        stop.set()
                        break
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # network failures must remain visible and reconnectable
            counts["connection_failures"] += 1
            last_error = f"{type(exc).__name__}:{exc}"
            _write_json_atomic(state_path, state("RECONNECTING"))
            delay = min(maximum_backoff, backoff) * random.uniform(0.9, 1.1)
            try:
                await asyncio.wait_for(stop.wait(), timeout=delay)
            except asyncio.TimeoutError:
                pass
            backoff = min(maximum_backoff, max(backoff * 2.0, 1.0))
    final_status = "STOPPED" if counts["connections"] else "FAILED_NO_CONNECTION"
    final = state(final_status)
    _write_json_atomic(state_path, final)
    return final


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "config/binance_force_order_capture_v1.json",
    )
    parser.add_argument("--max-messages", type=int)
    parser.add_argument("--max-seconds", type=float)
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    result = asyncio.run(
        collect(config, max_messages=args.max_messages, max_seconds=args.max_seconds)
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] == "FAILED_NO_CONNECTION":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
