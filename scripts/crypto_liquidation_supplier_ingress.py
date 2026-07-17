from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from alphafactory_crypto.liquidation_ingress import (
    canonical_sha256,
    preflight_supplier_release,
    qualify_overlap,
    sha256_file,
)


def _git_sha() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def _report(preflight: dict[str, Any], overlap: dict[str, Any], manifest: dict[str, Any]) -> str:
    observed = preflight["observed"]
    classes = pd.DataFrame(preflight["contract_classification"])
    lines = [
        "# Crypto liquidation supplier ingress",
        "",
        "This is source ingress and compatibility evidence only. It is not research, OOS, or economic evidence.",
        "",
        f"- Source SHA: `{manifest['source_sha']}`",
        f"- Release: `{preflight['release_id']}`",
        f"- Preflight: `{preflight['status']}`",
        f"- Stitching: `{overlap['status']}`",
        f"- Partition files: {preflight['partition_files']}",
        f"- Events: {observed['event_count']:,}",
        f"- Symbols: {observed['symbol_count']}",
        f"- Range: {observed['first_timestamp']} through {observed['last_timestamp']}",
        "",
        "## Contract classes",
        "",
        classes.to_markdown(index=False),
        "",
        "Only symbols matching `^[A-Z0-9]+(?:USDT|USDC)$` are notional-comparable. "
        "Inverse, delivery, and unknown contracts remain quarantined until a multiplier contract exists.",
        "",
        "## Overlap gate",
        "",
        f"- Status: `{overlap['status']}`",
        f"- Comparison pass: `{overlap.get('comparison_pass', False)}`",
        f"- Automatic stitching allowed: `False`",
        "",
        "A passing comparison only makes the sources eligible for an explicit activation decision. "
        "It never joins them automatically.",
        "",
        "## Boundaries",
        "",
        "The release contains 2025-2026 observations and is quarantined from research consumers. "
        "No challenge, forward, recent, May-stress, promotion, performance-search, or adaptive-memory boundary was opened.",
        "",
    ]
    return "\n".join(lines)


def run(config_path: Path, ws_root: Path | None = None) -> dict[str, Any]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    output_root = ROOT / config["outputs"]["runtime_root"]
    report_path = ROOT / config["outputs"]["report"]
    output_root.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    supplier = preflight_supplier_release(config)
    overlap, comparison = qualify_overlap(config, supplier.evidence, ws_root)
    preflight_path = output_root / "release_preflight.json"
    partitions_path = output_root / "partition_manifest.json"
    overlap_path = output_root / "overlap_qualification.json"
    comparison_path = output_root / "overlap_daily_symbol.csv"
    manifest_path = output_root / "run_manifest.json"
    _write_json(preflight_path, supplier.evidence)
    _write_json(partitions_path, {"records": supplier.partition_records})
    _write_json(overlap_path, overlap)
    if not comparison.empty:
        comparison.to_csv(comparison_path, index=False, lineterminator="\n")
    elif comparison_path.exists():
        comparison_path.unlink()

    manifest: dict[str, Any] = {
        "schema_version": 1,
        "run_id": config["run_id"],
        "source_sha": _git_sha(),
        "config_sha256": sha256_file(config_path),
        "release_identity_sha256": supplier.evidence["release_identity_sha256"],
        "preflight_status": supplier.evidence["status"],
        "overlap_status": overlap["status"],
        "research_admitted": False,
        "stitching_allowed": False,
        "ws_root": None if ws_root is None else ws_root.resolve().as_posix(),
        "boundaries": config["boundaries"],
        "files": {},
    }
    manifest["run_identity_sha256"] = canonical_sha256(
        {key: value for key, value in manifest.items() if key != "files"}
    )
    report_path.write_text(_report(supplier.evidence, overlap, manifest), encoding="utf-8")
    paths = [preflight_path, partitions_path, overlap_path, report_path]
    if comparison_path.exists():
        paths.append(comparison_path)
    for path in paths:
        manifest["files"][path.relative_to(ROOT).as_posix()] = sha256_file(path)
    _write_json(manifest_path, manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "config/crypto_liquidation_supplier_ingress_v1.json",
    )
    parser.add_argument("--ws-root", type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.config, args.ws_root), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
