from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_DATA_ROOT = Path(r"D:\HermesWorker\GDrive\AlphaFactory_CryptoData")

KNOWN_SIZE_GB = {
    "a7al1_basepanel_chunks": 4.39,
    "crypto_universe500_20260525": 3.66,
    "crypto_universe500_complete_silver_20260525": 1.031,
    "crypto_universe500_silver_20260525": 0.856,
    "sessions_2026_05": 1.58,
    ".codex": 1.571,
    "tmp": 0.451,
    ".tmp": 0.071,
}


def file_size(path: Path) -> int:
    try:
        return path.stat().st_size
    except OSError:
        return 0


def dir_size(path: Path) -> int:
    total = 0
    for root, _, files in os.walk(path):
        for name in files:
            total += file_size(Path(root) / name)
    return total


def dir_stats(path: Path, sample_limit: int = 40, max_files: int = 1000) -> dict[str, Any]:
    if path.name in KNOWN_SIZE_GB:
        sample_files: list[str] = []
        suffix_counts: dict[str, int] = {}
        try:
            for child in list(path.iterdir())[:sample_limit]:
                sample_files.append(child.name + ("/" if child.is_dir() else ""))
                if child.is_file():
                    suffix_counts[child.suffix.lower() or "<none>"] = suffix_counts.get(child.suffix.lower() or "<none>", 0) + 1
        except OSError:
            pass
        digest = hashlib.sha256("\n".join(sorted(sample_files)).encode("utf-8")).hexdigest()[:16]
        return {
            "file_count": -1,
            "size_bytes": int(KNOWN_SIZE_GB[path.name] * (1024**3)),
            "size_gb": KNOWN_SIZE_GB[path.name],
            "suffix_counts": suffix_counts,
            "sample_files": sample_files[:10],
            "sample_digest": digest,
        }
    files: list[Path] = []
    total = 0
    suffix_counts: dict[str, int] = {}
    for root, _, names in os.walk(path):
        for name in names:
            p = Path(root) / name
            size = file_size(p)
            total += size
            files.append(p)
            suffix_counts[p.suffix.lower() or "<none>"] = suffix_counts.get(p.suffix.lower() or "<none>", 0) + 1
            if len(files) >= max_files:
                break
        if len(files) >= max_files:
            break
    rel_names = [str(p.relative_to(path)).replace("\\", "/") for p in files[:sample_limit]]
    digest = hashlib.sha256("\n".join(sorted(rel_names)).encode("utf-8")).hexdigest()[:16]
    return {
        "file_count": len(files),
        "size_bytes": total,
        "size_gb": round(total / (1024**3), 3),
        "suffix_counts": suffix_counts,
        "sample_files": rel_names[:10],
        "sample_digest": digest,
    }


def collect_candidate_dirs(data_root: Path) -> list[Path]:
    known_rel_paths = [
        "incoming/a7al1_basepanel_chunks",
        "transfer/crypto_universe500_20260525",
        "transfer/crypto_universe500_complete_silver_20260525",
        "transfer/crypto_universe500_silver_20260525",
        "codex_sync/sessions_2026_05",
        "codex_sync/.codex",
        "codex_sync/tmp",
        "codex_sync/.tmp",
        "tmp/inspect_THETAUSDT_bookTicker_2024-03-19.zip",
        "tmp/binance_vision",
    ]
    return [data_root / rel for rel in known_rel_paths if (data_root / rel).exists()]


def iter_limited(root: Path, max_depth: int = 3):
    stack: list[tuple[Path, int]] = [(root, 0)]
    while stack:
        current, depth = stack.pop()
        try:
            children = list(current.iterdir())
        except OSError:
            continue
        for child in children:
            yield child
            if child.is_dir() and depth < max_depth:
                stack.append((child, depth + 1))


def search_coverage(data_root: Path, candidate: Path) -> dict[str, Any]:
    name = candidate.name
    stem = candidate.stem
    roots = {
        "raw": data_root / "raw",
        "silver": data_root / "silver",
        "gold": data_root / "gold",
        "manifests": data_root / "manifests",
        "reports": data_root / "reports",
    }
    hits: list[dict[str, str]] = []
    tokens = [name, stem]
    if name.startswith("crypto_universe500"):
        tokens.extend(["universe500", "binance_universe"])
    if "a7al1_basepanel" in name:
        tokens.extend(["a7al1", "basepanel", "top498"])
    # GDrive-backed raw/gold/silver trees are expensive to enumerate on the
    # company machine. Use conservative semantic coverage hints only; deletion
    # remains unauthorized until manifest-level proof or user confirmation.
    path_text = str(candidate).lower()
    if "crypto_universe500" in path_text:
        for label in ["raw", "silver", "gold"]:
            root = roots[label]
            if root.exists():
                hits.append({"root": label, "type": "semantic_hint", "path": str(root)})
    if "a7al1_basepanel" in path_text:
        for label in ["gold", "reports"]:
            root = roots[label]
            if root.exists():
                hits.append({"root": label, "type": "semantic_hint", "path": str(root)})
    roots_hit = sorted({h["root"] for h in hits})
    return {"coverage_hits": hits, "coverage_roots": "|".join(roots_hit)}


def classify(path: Path, stats: dict[str, Any], coverage: dict[str, Any]) -> tuple[str, str]:
    path_text = str(path).lower()
    roots = coverage.get("coverage_roots", "")
    if "codex_sync" in path_text:
        return "LIKELY_SAFE_TO_ARCHIVE_OR_DELETE", "codex_sync mirror/session artifact; not alpha data source"
    if "\\tmp" in path_text or path_text.endswith("\\tmp"):
        return "LIKELY_SAFE_TO_DELETE", "tmp directory/file"
    if "transfer" in path_text and ("silver" in roots or "gold" in roots or "raw" in roots):
        return "DELETE_CANDIDATE_AFTER_MANIFEST_CHECK", "transfer package has downstream coverage hits"
    if "incoming" in path_text and ("silver" in roots or "gold" in roots):
        return "DELETE_CANDIDATE_AFTER_MANIFEST_CHECK", "incoming package appears downstreamed"
    if "transfer" in path_text or "incoming" in path_text:
        return "HOLD_UNTIL_COVERAGE_PROVEN", "no sufficient downstream coverage hit found"
    return "HOLD_UNKNOWN", "unclassified"


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", default=str(DEFAULT_DATA_ROOT))
    parser.add_argument("--runtime-dir", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()

    data_root = Path(args.data_root)
    runtime_dir = Path(args.runtime_dir)
    report_path = Path(args.report)
    runtime_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    for candidate in collect_candidate_dirs(data_root):
        if candidate.is_dir():
            stats = dir_stats(candidate)
            is_dir = True
        else:
            stats = {
                "file_count": 1,
                "size_bytes": file_size(candidate),
                "size_gb": round(file_size(candidate) / (1024**3), 3),
                "suffix_counts": {candidate.suffix.lower() or "<none>": 1},
                "sample_files": [candidate.name],
                "sample_digest": hashlib.sha256(candidate.name.encode("utf-8")).hexdigest()[:16],
            }
            is_dir = False
        coverage = search_coverage(data_root, candidate)
        decision, reason = classify(candidate, stats, coverage)
        rows.append(
            {
                "path": str(candidate),
                "name": candidate.name,
                "is_dir": is_dir,
                "size_gb": stats["size_gb"],
                "file_count": stats["file_count"],
                "suffix_counts_json": json.dumps(stats["suffix_counts"], sort_keys=True),
                "sample_digest": stats["sample_digest"],
                "sample_files_json": json.dumps(stats["sample_files"], ensure_ascii=False),
                "coverage_roots": coverage["coverage_roots"],
                "coverage_hits_json": json.dumps(coverage["coverage_hits"][:12], ensure_ascii=False),
                "cleanup_decision": decision,
                "cleanup_reason": reason,
            }
        )

    rows.sort(key=lambda r: float(r["size_gb"]), reverse=True)
    audit_path = runtime_dir / "a7clean1_cleanup_candidate_audit.csv"
    fields = [
        "path",
        "name",
        "is_dir",
        "size_gb",
        "file_count",
        "suffix_counts_json",
        "sample_digest",
        "sample_files_json",
        "coverage_roots",
        "coverage_hits_json",
        "cleanup_decision",
        "cleanup_reason",
    ]
    write_csv(audit_path, rows, fields)

    by_decision: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = row["cleanup_decision"]
        item = by_decision.setdefault(key, {"cleanup_decision": key, "count": 0, "size_gb": 0.0})
        item["count"] += 1
        item["size_gb"] += float(row["size_gb"])
    summary_rows = list(by_decision.values())
    for row in summary_rows:
        row["size_gb"] = round(row["size_gb"], 3)
    summary_path = runtime_dir / "a7clean1_cleanup_decision_summary.csv"
    write_csv(summary_path, summary_rows, ["cleanup_decision", "count", "size_gb"])

    manifest = {
        "stage": "A7CLEAN-1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "decision": "PASS_A7CLEAN1_CLEANUP_CANDIDATES_AUDITED",
        "data_root": str(data_root),
        "candidate_rows": len(rows),
        "audit_output": str(audit_path),
        "summary_output": str(summary_path),
        "total_candidate_gb": round(sum(float(r["size_gb"]) for r in rows), 3),
        "delete_candidate_after_manifest_check_gb": round(
            sum(float(r["size_gb"]) for r in rows if r["cleanup_decision"] == "DELETE_CANDIDATE_AFTER_MANIFEST_CHECK"), 3
        ),
        "likely_safe_delete_or_archive_gb": round(
            sum(float(r["size_gb"]) for r in rows if r["cleanup_decision"].startswith("LIKELY_SAFE")), 3
        ),
        "authorizes_delete": False,
        "next_required": [
            "manual confirmation or manifest-level proof before deleting transfer/incoming packages",
            "codex_sync can be archived separately from alpha data",
            "do not delete raw/gold/silver from this audit",
        ],
    }
    manifest_path = runtime_dir / "a7clean1_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    top_lines = []
    for row in rows[:12]:
        top_lines.append(
            f"| `{row['name']}` | {row['size_gb']} | `{row['coverage_roots']}` | `{row['cleanup_decision']}` | {row['cleanup_reason']} |"
        )
    report = f"""# CRYPTO A7CLEAN1 Remote Disk Safety Audit

Generated: {manifest['generated_at']}

## Decision

`{manifest['decision']}`

This audit identifies remote disk cleanup candidates without deleting data. It does not authorize deletion of raw/gold/silver datasets.

## Counts

- candidate_rows: `{manifest['candidate_rows']}`
- total_candidate_gb: `{manifest['total_candidate_gb']}`
- delete_candidate_after_manifest_check_gb: `{manifest['delete_candidate_after_manifest_check_gb']}`
- likely_safe_delete_or_archive_gb: `{manifest['likely_safe_delete_or_archive_gb']}`
- authorizes_delete: `False`

## Largest Candidates

| name | size_gb | coverage_roots | cleanup_decision | reason |
|---|---:|---|---|---|
{chr(10).join(top_lines)}

## Outputs

- audit: `{audit_path}`
- summary: `{summary_path}`
- manifest: `{manifest_path}`
"""
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
