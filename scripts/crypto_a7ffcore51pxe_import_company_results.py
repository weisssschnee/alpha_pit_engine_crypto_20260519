from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore51pxe_company_sharded_replay_import"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE51PXE_COMPANY_SHARDED_REPLAY_IMPORT_20260602.md"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, help="External CORE51PXE output directory")
    args = parser.parse_args()
    out = Path(args.out)
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    aggregate = read_json(out / "a7ffcore51pxe_aggregate_manifest.json")
    if not aggregate:
        raise SystemExit(f"missing aggregate manifest under {out}")
    label_summary = pd.read_csv(out / "a7ffcore51pxe_label_summary.csv") if (out / "a7ffcore51pxe_label_summary.csv").exists() else pd.DataFrame()
    family_summary = pd.read_csv(out / "a7ffcore51pxe_family_operator_summary.csv") if (out / "a7ffcore51pxe_family_operator_summary.csv").exists() else pd.DataFrame()
    shard_summary = pd.read_csv(out / "a7ffcore51pxe_shard_manifest_summary.csv") if (out / "a7ffcore51pxe_shard_manifest_summary.csv").exists() else pd.DataFrame()

    label_summary.to_csv(RUNTIME / "a7ffcore51pxe_label_summary.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ffcore51pxe_family_operator_summary.csv", index=False)
    shard_summary.to_csv(RUNTIME / "a7ffcore51pxe_shard_manifest_summary.csv", index=False)

    decision = (
        "PASS_A7FFCORE51PXE_COMPANY_RESULTS_IMPORTED_READY_FOR_CORE52_ARBITRATION"
        if aggregate.get("decision") == "PASS_A7FFCORE51PXE_COMPANY_SHARDED_REPLAY_AGGREGATED"
        else "HOLD_A7FFCORE51PXE_COMPANY_RESULTS_IMPORT_INCOMPLETE"
    )
    manifest = {
        "stage": "A7FF-CORE51PXE-IMPORT",
        "generated_at": now_utc(),
        "source_output_dir": str(out).replace("\\", "/"),
        "source_decision": aggregate.get("decision"),
        "decision": decision,
        "completed_shards": aggregate.get("completed_shards"),
        "metric_rows": aggregate.get("metric_rows"),
        "control_clean_positive_seed_count": aggregate.get("control_clean_positive_seed_count"),
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core52_arbitration": decision.startswith("PASS_"),
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ffcore51pxe_import_manifest.json", manifest)
    lines = [
        "# CRYPTO A7FF-CORE51PXE COMPANY SHARDED REPLAY IMPORT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "This imports external company-machine shard results into repo runtime. It does not execute replay/search/proof.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Label Summary",
        "",
        md_table(label_summary),
        "",
        "## Family Summary",
        "",
        md_table(family_summary),
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
