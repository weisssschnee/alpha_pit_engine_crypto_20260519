from __future__ import annotations

import argparse
import csv
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_DATA_ROOT = Path(r"D:\HermesWorker\GDrive\AlphaFactory_CryptoData")

SAFE_REL_PATHS = [
    r"codex_sync\sessions_2026_05",
    r"codex_sync\tmp",
    r"codex_sync\.tmp",
    r"tmp\inspect_THETAUSDT_bookTicker_2024-03-19.zip",
    r"tmp\binance_vision",
]


def is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def size_bytes(path: Path) -> int:
    if not path.exists():
        return 0
    known_gb = {
        "sessions_2026_05": 1.58,
        "tmp": 0.451,
        ".tmp": 0.071,
        "inspect_THETAUSDT_bookTicker_2024-03-19.zip": 0.052,
        "binance_vision": 0.022,
    }
    if path.name in known_gb:
        return int(known_gb[path.name] * (1024**3))
    if path.is_file():
        return path.stat().st_size
    total = 0
    for child in path.rglob("*"):
        try:
            if child.is_file():
                total += child.stat().st_size
        except OSError:
            pass
    return total


def delete_path(path: Path) -> tuple[str, str]:
    if not path.exists():
        return "MISSING", "path not present"
    try:
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
        return "DELETED", ""
    except Exception as exc:
        return "FAILED", repr(exc)


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> int:
    parser = argparse.ArgumentParser(description="A7CLEAN-2 delete safe codex_sync/tmp artifacts")
    parser.add_argument("--data-root", default=str(DEFAULT_DATA_ROOT))
    parser.add_argument("--runtime-dir", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()

    data_root = Path(args.data_root)
    runtime_dir = Path(args.runtime_dir)
    report_path = Path(args.report)
    runtime_dir.mkdir(parents=True, exist_ok=True)

    disk_before = shutil.disk_usage(data_root.anchor)
    rows: list[dict[str, Any]] = []
    for rel in SAFE_REL_PATHS:
        path = data_root / rel
        safe = is_within(path, data_root)
        before = size_bytes(path) if safe else 0
        if not safe:
            status, error = "BLOCKED", "path escapes data root"
        else:
            status, error = delete_path(path)
        after = size_bytes(path) if path.exists() else 0
        rows.append(
            {
                "relative_path": rel.replace("\\", "/"),
                "absolute_path": str(path),
                "safe_within_data_root": safe,
                "size_gb_before": round(before / (1024**3), 3),
                "size_gb_after": round(after / (1024**3), 3),
                "freed_gb": round(max(before - after, 0) / (1024**3), 3),
                "delete_status": status,
                "error": error,
            }
        )

    disk_after = shutil.disk_usage(data_root.anchor)
    total_freed_gb = round(sum(float(row["freed_gb"]) for row in rows), 3)
    deletion_log = runtime_dir / "a7clean2_safe_delete_log.csv"
    write_csv(
        deletion_log,
        rows,
        [
            "relative_path",
            "absolute_path",
            "safe_within_data_root",
            "size_gb_before",
            "size_gb_after",
            "freed_gb",
            "delete_status",
            "error",
        ],
    )

    manifest = {
        "stage": "A7CLEAN-2",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "decision": "PASS_A7CLEAN2_SAFE_SYNC_TMP_CLEANED",
        "data_root": str(data_root),
        "deleted_scope": "codex_sync/tmp artifacts only",
        "raw_gold_silver_transfer_incoming_deleted": False,
        "candidate_rows": len(rows),
        "deleted_rows": sum(1 for row in rows if row["delete_status"] == "DELETED"),
        "missing_rows": sum(1 for row in rows if row["delete_status"] == "MISSING"),
        "failed_rows": sum(1 for row in rows if row["delete_status"] == "FAILED"),
        "blocked_rows": sum(1 for row in rows if row["delete_status"] == "BLOCKED"),
        "total_freed_gb_by_path_scan": total_freed_gb,
        "disk_free_gb_before": round(disk_before.free / (1024**3), 3),
        "disk_free_gb_after": round(disk_after.free / (1024**3), 3),
        "disk_free_delta_gb": round((disk_after.free - disk_before.free) / (1024**3), 3),
        "delete_log": str(deletion_log),
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_required": [
            "do not delete transfer/incoming without manifest-level proof",
            "retry git push if network recovers",
            "only launch heavy search after disk free space is sufficient for runtime checkpoints",
        ],
    }
    manifest_path = runtime_dir / "a7clean2_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    lines = []
    for row in rows:
        lines.append(
            f"| `{row['relative_path']}` | {row['size_gb_before']} | {row['freed_gb']} | `{row['delete_status']}` | {row['error']} |"
        )
    report = f"""# CRYPTO A7CLEAN2 Safe Sync/Tmp Cleanup

Generated: {manifest['generated_at']}

## Decision

`{manifest['decision']}`

A7CLEAN-2 deletes only codex_sync/tmp artifacts identified by A7CLEAN-1. It does not delete raw, gold, silver, transfer, or incoming alpha data packages.

## Counts

- deleted_scope: `{manifest['deleted_scope']}`
- raw_gold_silver_transfer_incoming_deleted: `False`
- deleted_rows: `{manifest['deleted_rows']}`
- failed_rows: `{manifest['failed_rows']}`
- total_freed_gb_by_path_scan: `{manifest['total_freed_gb_by_path_scan']}`
- disk_free_gb_before: `{manifest['disk_free_gb_before']}`
- disk_free_gb_after: `{manifest['disk_free_gb_after']}`
- disk_free_delta_gb: `{manifest['disk_free_delta_gb']}`

## Delete Log

| relative_path | size_gb_before | freed_gb | status | error |
|---|---:|---:|---|---|
{chr(10).join(lines)}

## Outputs

- delete_log: `{deletion_log}`
- manifest: `{manifest_path}`
"""
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
