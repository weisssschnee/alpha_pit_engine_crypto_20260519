from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_ROOT = ROOT / "archive" / "deprecated_crypto_a7_20260527"


DEPRECATED_SCRIPT_PREFIXES = (
    "crypto_a1_",
    "crypto_a2",
    "crypto_a3_",
    "crypto_a4_",
    "crypto_a5",
    "crypto_a6",
    "crypto_a7_",
    "crypto_a7b",
    "crypto_a7c",
    "crypto_a7d",
    "crypto_a7f",
    "crypto_a7g",
    "crypto_a7h",
    "crypto_a7i",
    "crypto_a7j",
    "crypto_a7k",
    "crypto_a7l",
    "crypto_a7m",
    "crypto_a7n",
    "crypto_a7o",
    "crypto_a7p",
    "crypto_a7q",
    "crypto_a7r",
    "crypto_a7aa",
    "crypto_a7ab",
    "crypto_a7ac",
    "crypto_a7ad",
    "crypto_a7ae",
    "crypto_a7af",
    "crypto_a7ag",
    "crypto_a7v",
    "crypto_a7x",
    "crypto_a7y",
    "crypto_a7z",
    "crypto_alpha_smoke_v0",
    "crypto_alpha_preflight",
    "crypto_method_gate_check",
)


ACTIVE_SCRIPT_PREFIXES = (
    "crypto_a7ah",
    "crypto_a7ai",
    "crypto_a7aj",
    "crypto_a7ak",
    "crypto_a7al",
    "crypto_a7am",
    "crypto_a7ao",
    "crypto_a7ap",
    "crypto_a7ar",
    "crypto_a7s",
    "crypto_a7t",
    "crypto_a7u",
    "crypto_a7w",
    "build_crypto",
    "run_binance",
)


DEPRECATED_RUNTIME_PREFIXES = (
    "a1_",
    "a2",
    "a3_",
    "a4_",
    "a5",
    "a6",
    "a7_method_validation",
    "a7b",
    "a7c",
    "a7d",
    "a7f",
    "a7g",
    "a7h",
    "a7i",
    "a7j",
    "a7k",
    "a7l",
    "a7m",
    "a7n",
    "a7o",
    "a7p",
    "a7q",
    "a7r",
    "a7aa",
    "a7ab",
    "a7ac",
    "a7ad",
    "a7ae",
    "a7af",
    "a7ag",
    "a7v",
    "a7x",
    "a7y",
    "a7z",
)


ACTIVE_RUNTIME_PREFIXES = (
    "a7ah",
    "a7ai",
    "a7aj",
    "a7ak",
    "a7al",
    "a7am",
    "a7ao",
    "a7ap",
    "a7ar",
    "a7s",
    "a7t",
    "a7u",
    "a7w",
    "baselines",
)


DEPRECATED_REPORT_PREFIXES = (
    "CRYPTO_A1",
    "CRYPTO_A2",
    "CRYPTO_A3",
    "CRYPTO_A4",
    "CRYPTO_A5",
    "CRYPTO_A6",
    "CRYPTO_A7_",
    "CRYPTO_A7B",
    "CRYPTO_A7C",
    "CRYPTO_A7D",
    "CRYPTO_A7E",
    "CRYPTO_A7F",
    "CRYPTO_A7G",
    "CRYPTO_A7H",
    "CRYPTO_A7I",
    "CRYPTO_A7J",
    "CRYPTO_A7K",
    "CRYPTO_A7L",
    "CRYPTO_A7M",
    "CRYPTO_A7N",
    "CRYPTO_A7O",
    "CRYPTO_A7P",
    "CRYPTO_A7Q",
    "CRYPTO_A7R",
    "CRYPTO_A7AA",
    "CRYPTO_A7AB",
    "CRYPTO_A7AC",
    "CRYPTO_A7AD",
    "CRYPTO_A7AE",
    "CRYPTO_A7AF",
    "CRYPTO_A7AG",
    "CRYPTO_A7V",
    "CRYPTO_A7X",
    "CRYPTO_A7Y",
    "CRYPTO_A7Z",
    "CRYPTO_ALPHA_SMOKE",
    "CRYPTO_ALPHAFACTORY_PREFLIGHT",
    "CRYPTO_METHOD_GATE_CHECK",
    "crypto_alpha_smoke",
    "crypto_alphafactory_preflight",
    "crypto_method_gate_check",
)


ACTIVE_REPORT_PREFIXES = (
    "CRYPTO_A7AH",
    "CRYPTO_A7AI",
    "CRYPTO_A7AJ",
    "CRYPTO_A7AK",
    "CRYPTO_A7AL",
    "CRYPTO_A7AM",
    "CRYPTO_A7AO",
    "CRYPTO_A7AP",
    "CRYPTO_A7AR",
    "CRYPTO_A7S",
    "CRYPTO_A7T",
    "CRYPTO_A7U",
    "CRYPTO_A7W",
    "CRYPTO_BRONZE",
    "CRYPTO_ALPHAFACTORY_METHOD",
    "crypto_bronze",
)


def starts_with_any(name: str, prefixes: tuple[str, ...]) -> bool:
    lowered = name.lower()
    return any(lowered.startswith(prefix.lower()) for prefix in prefixes)


def classify_script(path: Path) -> bool:
    name = path.name
    if starts_with_any(name, ACTIVE_SCRIPT_PREFIXES):
        return False
    return starts_with_any(name, DEPRECATED_SCRIPT_PREFIXES)


def classify_runtime(path: Path) -> bool:
    name = path.name
    if starts_with_any(name, ACTIVE_RUNTIME_PREFIXES):
        return False
    return starts_with_any(name, DEPRECATED_RUNTIME_PREFIXES)


def classify_report(path: Path) -> bool:
    name = path.name
    if starts_with_any(name, ACTIVE_REPORT_PREFIXES):
        return False
    return starts_with_any(name, DEPRECATED_REPORT_PREFIXES)


def safe_relative(path: Path) -> str:
    resolved = path.resolve()
    root = ROOT.resolve()
    if root not in resolved.parents and resolved != root:
        raise RuntimeError(f"path escapes repo: {path}")
    return str(resolved.relative_to(root)).replace("\\", "/")


def move_path(path: Path, bucket: str, manifest_rows: list[dict[str, Any]]) -> None:
    rel = safe_relative(path)
    destination = ARCHIVE_ROOT / bucket / rel
    if destination.exists():
        raise RuntimeError(f"archive destination already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(path), str(destination))
    manifest_rows.append(
        {
            "bucket": bucket,
            "original_path": rel,
            "archive_path": safe_relative(destination),
            "kind": "directory" if destination.is_dir() else "file",
        }
    )


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = ["bucket", "original_path", "archive_path", "kind"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def main() -> None:
    manifest_rows: list[dict[str, Any]] = []
    for path in sorted((ROOT / "scripts").glob("*")):
        if path.is_file() and classify_script(path):
            move_path(path, "scripts", manifest_rows)
    for path in sorted((ROOT / "reports").glob("*")):
        if path.is_file() and classify_report(path):
            move_path(path, "reports", manifest_rows)
    for path in sorted((ROOT / "runtime").glob("*")):
        if path.is_dir() and classify_runtime(path):
            move_path(path, "runtime", manifest_rows)

    write_csv(ARCHIVE_ROOT / "deprecated_archive_manifest.csv", manifest_rows)
    summary = {
        "decision": "PASS_CRYPTO_DEPRECATED_ACTIVE_TREE_ARCHIVE_20260527",
        "archive_root": safe_relative(ARCHIVE_ROOT),
        "moved_count": len(manifest_rows),
        "buckets": {
            bucket: sum(1 for row in manifest_rows if row["bucket"] == bucket)
            for bucket in sorted({row["bucket"] for row in manifest_rows})
        },
        "active_retained": [
            "A7AJ/A7AK/A7AL top498 and latent-neutral contracts",
            "A7AO/A7AP cross-exchange acceptance and repaired overlay",
            "A7AR CN-engine inheritance adapters",
            "A7S/A7U data-source and source-trace contracts",
            "A7T forward telemetry contracts",
            "A7W post-source-trace status",
            "build/run data utilities",
        ],
        "not_deleted": True,
        "cn_repo_touched": False,
    }
    (ARCHIVE_ROOT / "deprecated_archive_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    (ARCHIVE_ROOT / "README.md").write_text(
        "\n".join(
            [
                "# Deprecated Crypto A7 Archive 2026-05-27",
                "",
                "This archive removes obsolete exploratory scripts/reports/runtime outputs from the active tree.",
                "",
                "Archived items are retained for audit history, but are not active execution entrypoints.",
                "",
                "Current active line is A7AJ/A7AK/A7AL/A7AO/A7AP/A7AR/A7S/A7T/A7U/A7W.",
                "",
                "CN repo was not modified. CN memory payloads are not inherited.",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
