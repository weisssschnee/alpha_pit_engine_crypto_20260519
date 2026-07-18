from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from alphafactory_crypto.bitfinex_liquidation_ingress import (  # noqa: E402
    canonical_sha256,
    preflight_bitfinex_release,
    sha256_file,
)


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _git_context() -> tuple[str, bool]:
    sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    dirty = bool(
        subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    )
    return sha, dirty


def _report(evidence: dict[str, Any], manifest: dict[str, Any]) -> str:
    observed = evidence["observed"]
    adequacy = evidence["data_adequacy"]
    failed_checks = [
        name for name, row in adequacy["checks"].items() if not row["pass"]
    ]
    tail_months = sum(
        row["tail_without_events_days"] >= 7 for row in evidence["month_diagnostics"]
    )
    page_like = sum(
        row["page_boundary_like_raw_count"] for row in evidence["month_diagnostics"]
    )
    lines = [
        "# Bitfinex liquidation ingress preflight",
        "",
        "## Decision",
        "",
        f"- File/aggregation integrity: `{'PASS' if evidence['internal_file_and_aggregation_checks_pass'] else 'FAIL'}`",
        f"- Ingress status: `{evidence['status']}`",
        f"- Event Data Adequacy: `{adequacy['status']}`",
        "- Research admission: `False`",
        "- Binance/CryptoHFT reference use: `PROHIBITED`",
        "",
        "The directory contains all 18 declared monthly bundles and its silver/gold "
        "layers reconcile internally. It does not contain a request/page ledger proving "
        "that event-free portions of each requested month were queried. Therefore "
        "`complete` is accepted only as downloader/file completion, not as verified "
        "continuous source coverage.",
        "",
        "## Observed data",
        "",
        f"- Requested period: `{evidence['requested_interval']['start']}` to `{evidence['requested_interval']['end']}` ({evidence['requested_interval']['calendar_days']} days)",
        f"- Files: `{evidence['file_count']}`; bundle SHA256: `{evidence['bundle_sha256']}`",
        f"- Raw rows: `{observed['raw_rows']:,}`; silver matched rows: `{observed['silver_rows']:,}`",
        f"- All-symbol active event dates: `{observed['active_event_dates']}` ({observed['active_date_ratio']:.1%} of requested calendar days)",
        f"- USTF0 proxy subset: `{observed['eligible_ustf0_rows']:,}` rows, `{observed['eligible_ustf0_symbols']}` symbols, `{observed['eligible_active_dates']}` active dates",
        f"- Concentration-adjusted effective months/symbols: `{observed['eligible_effective_months']:.2f}` / `{observed['eligible_effective_symbols']:.2f}`",
        f"- Top-symbol event share: `{observed['eligible_top_symbol_event_share']:.1%}`",
        f"- Months with at least seven trailing event-free days: `{tail_months}/18`",
        f"- Months with page-boundary-like raw counts: `{page_like}/18`",
        "",
        "An event-free tail is not by itself proof of a missing download. In combination "
        "with absent request receipts and page-boundary-like counts, it prevents a "
        "claim of continuous interval coverage.",
        "",
        "## Data Adequacy gaps",
        "",
        *[f"- `{name}`" for name in failed_checks],
        "",
        "The package has no linked price/label bridge and no authorized portfolio "
        "mapping, so it cannot yet support the proposed large-event return study or "
        "turnover/cost evaluation.",
        "",
        "## Semantic boundary",
        "",
        "Only symbols matching `t...F0:USTF0` are retained as an event-study proxy "
        "subset. Even there, quantity-times-price remains a supplier-derived quote "
        "proxy, not a universally qualified common USD notional. Test, legacy, "
        "cross-quote, and unknown symbols remain quarantined.",
        "",
        "Bitfinex historical REST events are venue-specific and cannot validate "
        "Binance WebSocket or CryptoHFT coverage. No stitching, research admission, "
        "economic evaluation, sealed read, or promotion boundary was opened.",
        "",
        "## Reproduction",
        "",
        "```powershell",
        "python scripts/crypto_bitfinex_liquidation_ingress.py",
        "```",
        "",
        f"- Run identity SHA256: `{manifest['run_identity_sha256']}`",
        f"- Source SHA: `{manifest['source_sha']}` (dirty at execution: `{manifest['source_dirty']}`)",
        f"- Runtime seconds: `{manifest['actual_runtime_seconds']}`",
        "",
    ]
    return "\n".join(lines)


def run(config_path: Path) -> dict[str, Any]:
    started = time.perf_counter()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    source_sha, source_dirty = _git_context()
    output_root = ROOT / config["outputs"]["runtime_root"]
    report_path = ROOT / config["outputs"]["report"]
    output_root.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    result = preflight_bitfinex_release(config)
    evidence_path = output_root / "release_preflight.json"
    files_path = output_root / "input_file_manifest.json"
    manifest_path = output_root / "run_manifest.json"
    _write_json(evidence_path, result.evidence)
    _write_json(files_path, {"records": result.file_records})

    module_path = ROOT / "alphafactory_crypto/bitfinex_liquidation_ingress.py"
    script_path = Path(__file__).resolve()
    manifest: dict[str, Any] = {
        "schema_version": 1,
        "experiment_id": config["run_id"],
        "objective": config["objective"],
        "status": "completed",
        "mode": "light_ingress_preflight",
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "source_sha": source_sha,
        "source_dirty": source_dirty,
        "implementation_sha256": canonical_sha256(
            {
                "module": sha256_file(module_path),
                "script": sha256_file(script_path),
            }
        ),
        "config_sha256": sha256_file(config_path),
        "input_bundle_sha256": result.evidence["bundle_sha256"],
        "release_identity_sha256": result.evidence["release_identity_sha256"],
        "preflight_status": result.evidence["status"],
        "data_adequacy_status": result.evidence["data_adequacy"]["status"],
        "research_admitted": False,
        "binance_reference_allowed": False,
        "cryptohft_coverage_validation_allowed": False,
        "command": "python scripts/crypto_bitfinex_liquidation_ingress.py",
        "estimated_runtime_seconds": 60,
        "actual_runtime_seconds": round(time.perf_counter() - started, 3),
        "reproducible": True,
        "continuation": (
            "Obtain and independently qualify a source request/page coverage ledger, "
            "then add a PIT-safe price/label bridge and rerun this fixed gate before "
            "any event experiment."
        ),
        "failure": None,
        "boundaries": config["boundaries"],
        "files": {},
    }
    manifest["run_identity_sha256"] = canonical_sha256(
        {key: value for key, value in manifest.items() if key not in {"files", "completed_at", "actual_runtime_seconds"}}
    )
    report_path.write_text(_report(result.evidence, manifest), encoding="utf-8")
    for path in (evidence_path, files_path, report_path):
        manifest["files"][path.relative_to(ROOT).as_posix()] = sha256_file(path)
    _write_json(manifest_path, manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "config/crypto_bitfinex_liquidation_ingress_v1.json",
    )
    args = parser.parse_args()
    print(json.dumps(run(args.config), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
