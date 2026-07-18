from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from alphafactory_crypto.binance_force_order_capture import CaptureIdentity  # noqa: E402


def _git_sha() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8", newline="\n")


def snapshot(config_path: Path, output_path: Path, report_path: Path) -> dict[str, Any]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    capture_root = Path(config["output_root"])
    state_path = ROOT / config["state_root"] / "collector_state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    files = sorted(capture_root.glob("date=*/hour=*/force_orders.jsonl"))
    if not files:
        raise FileNotFoundError("collector has no captured forceOrder records")
    records = 0
    invalid_json = 0
    raw_hash_failures = 0
    contract_failures = 0
    source_failures = 0
    symbols: set[str] = set()
    event_types: Counter[str] = Counter()
    symbol_types: Counter[str] = Counter()
    received_times: list[str] = []
    file_rows = []
    for path in files:
        digest = hashlib.sha256()
        prefix_bytes = 0
        local_records = 0
        with path.open("rb") as handle:
            for raw_line in handle:
                digest.update(raw_line)
                prefix_bytes += len(raw_line)
                try:
                    row = json.loads(raw_line)
                except json.JSONDecodeError:
                    invalid_json += 1
                    continue
                records += 1
                local_records += 1
                raw_text = str(row.get("raw_text") or "")
                if hashlib.sha256(raw_text.encode("utf-8")).hexdigest().upper() != row.get("raw_sha256"):
                    raw_hash_failures += 1
                payload = row.get("payload") or {}
                order = payload.get("o") or {}
                event_types[str(payload.get("e"))] += 1
                symbol_types[str(order.get("st", payload.get("st", "MISSING")))] += 1
                if order.get("s"):
                    symbols.add(str(order["s"]))
                if row.get("received_time_utc"):
                    received_times.append(str(row["received_time_utc"]))
                if payload.get("e") != "forceOrder" or not order.get("s"):
                    contract_failures += 1
                if row.get("source_id") != "BINANCE_NATIVE_FORCE_ORDER_WS":
                    source_failures += 1
        file_rows.append(
            {
                "path": path.as_posix(),
                "prefix_bytes": prefix_bytes,
                "prefix_sha256": digest.hexdigest().upper(),
                "records": local_records,
            }
        )
    supplier_end = "2026-07-13"
    first_received = min(received_times) if received_times else None
    no_current_overlap = bool(first_received and first_received[:10] > supplier_end)
    checks = {
        "collector_running": state.get("status") == "RUNNING",
        "connected": int(state.get("counts", {}).get("connections", 0)) >= 1,
        "captured_records": records > 0,
        "json_valid": invalid_json == 0,
        "raw_hashes_valid": raw_hash_failures == 0,
        "force_order_contract": contract_failures == 0,
        "source_identity": source_failures == 0,
        "no_parse_failures": int(state.get("counts", {}).get("parse_failures", 0)) == 0,
    }
    result = {
        "schema_version": 1,
        "snapshot_id": "BINANCE_FORCE_ORDER_FORWARD_CAPTURE_SNAPSHOT_20260718",
        "status": "FORWARD_CAPTURE_ACTIVE_NO_CURRENT_PACKAGE_OVERLAP" if all(checks.values()) and no_current_overlap else "FORWARD_CAPTURE_NEEDS_ATTENTION",
        "source_sha": _git_sha(),
        "created_at": _now(),
        "capture_identity_sha256": CaptureIdentity(config["endpoint"], capture_root.as_posix()).sha256(),
        "endpoint": config["endpoint"],
        "stream": config["stream"],
        "collector_state": state,
        "observed": {
            "records": records,
            "files": len(files),
            "unique_symbols": len(symbols),
            "event_types": dict(sorted(event_types.items())),
            "symbol_types": dict(sorted(symbol_types.items())),
            "first_received_time_utc": first_received,
            "last_received_time_utc": max(received_times) if received_times else None,
            "invalid_json": invalid_json,
            "raw_hash_failures": raw_hash_failures,
            "contract_failures": contract_failures,
            "source_failures": source_failures,
        },
        "file_prefix_manifest": file_rows,
        "checks": checks,
        "current_supplier_release_end": supplier_end,
        "current_supplier_release_overlap": not no_current_overlap,
        "claim_boundary": "FORWARD_RAW_PROVENANCE_ONLY_NOT_HISTORICAL_OVERLAP_OR_RESEARCH_ADMISSION",
        "boundaries": config["boundaries"],
    }
    _write_json(output_path, result)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        "\n".join(
            [
                "# Binance forceOrder forward capture activation",
                "",
                f"- Status: `{result['status']}`",
                f"- Source SHA: `{result['source_sha']}`",
                f"- Endpoint: `{result['endpoint']}`",
                f"- Records at snapshot: {records}",
                f"- Unique symbols: {len(symbols)}",
                f"- Raw hash failures: {raw_hash_failures}",
                f"- Parse failures: {state.get('counts', {}).get('parse_failures', 0)}",
                "",
                "The capture begins after the current CryptoHFT release end, so it cannot validate that historical package. It is canonical forward provenance for a future overlapping supplier release only.",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=ROOT / "config/binance_force_order_capture_v1.json")
    parser.add_argument("--output", type=Path, default=ROOT / "runtime/binance_force_order_capture_activation_20260718/snapshot.json")
    parser.add_argument("--report", type=Path, default=ROOT / "reports/BINANCE_FORCE_ORDER_CAPTURE_ACTIVATION_20260718.md")
    args = parser.parse_args()
    print(json.dumps(snapshot(args.config, args.output, args.report), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
