from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_INPUT = "runtime/a7shadow2_signal_overlap_dedup_20260703/a7shadow2_keep_queue.csv"
DEFAULT_RUNTIME = "runtime/a7shadow3_reward_queue_adapter_20260703"
DEFAULT_REPORT = "reports/CRYPTO_A7SHADOW3_REWARD_QUEUE_ADAPTER_20260703.md"


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists() or path.stat().st_size <= 2:
        return []
    with path.open("r", newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def build(repo: Path, input_path: Path, runtime: Path, report: Path) -> dict[str, Any]:
    rows = read_csv(input_path)
    out_rows: list[dict[str, Any]] = []
    missing_expression = 0
    for idx, row in enumerate(rows, start=1):
        candidate_id = row.get("candidate_id") or f"a7shadow3_c{idx:03d}"
        expression = row.get("expression") or row.get("formula") or ""
        if not expression:
            missing_expression += 1
            continue
        out = dict(row)
        out["blueprint_id"] = row.get("blueprint_id") or candidate_id
        out["source_blueprint_id"] = row.get("source_blueprint_id") or candidate_id
        out["candidate_id"] = candidate_id
        out["expression"] = expression
        out["formula"] = expression
        out["semantic_pair"] = row.get("semantic_pair", "")
        out["motif"] = row.get("motif", "")
        out["skeleton_key"] = row.get("skeleton_key") or row.get("operator_tokens") or ""
        out["horizon_h"] = row.get("horizon_h", "")
        out_rows.append(out)

    fields = [
        "blueprint_id",
        "source_blueprint_id",
        "candidate_id",
        "cluster_id",
        "semantic_pair",
        "motif",
        "skeleton_key",
        "horizon_h",
        "expression",
        "formula",
        "field_tokens",
        "operator_tokens",
        "evidence_tier",
        "source_count",
        "source_lag_status",
        "dedup_decision",
        "dedup_reason",
    ]
    output = runtime / "a7shadow3_reward_input_queue.csv"
    write_csv(output, out_rows, fields)

    duplicate_ids = len(out_rows) - len({row["blueprint_id"] for row in out_rows})
    decision = "PASS_A7SHADOW3_REWARD_QUEUE_ADAPTED" if out_rows and duplicate_ids == 0 and missing_expression == 0 else "HOLD_A7SHADOW3_QUEUE_ADAPTER_ISSUE"
    manifest = {
        "stage": "A7SHADOW-3-QUEUE-ADAPTER",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "input": str(input_path),
        "output": str(output),
        "input_rows": len(rows),
        "output_rows": len(out_rows),
        "missing_expression_rows": missing_expression,
        "duplicate_blueprint_id_rows": duplicate_ids,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "authorizes_reward_rerun": decision.startswith("PASS"),
    }
    (runtime / "a7shadow3_queue_adapter_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "# CRYPTO A7SHADOW3 Reward Queue Adapter",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "This adapter converts A7SHADOW-2 keep leaders into an A7REWARD-compatible queue. It assigns stable non-empty `blueprint_id` values from `candidate_id` to prevent reward grouping from collapsing multiple candidates into one blank id.",
        "",
        "## Counts",
        "",
        f"- input_rows: `{manifest['input_rows']}`",
        f"- output_rows: `{manifest['output_rows']}`",
        f"- missing_expression_rows: `{manifest['missing_expression_rows']}`",
        f"- duplicate_blueprint_id_rows: `{manifest['duplicate_blueprint_id_rows']}`",
        "",
        "## Outputs",
        "",
        f"- reward_input_queue: `{output}`",
        f"- manifest: `{runtime / 'a7shadow3_queue_adapter_manifest.json'}`",
    ]
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--input", default=DEFAULT_INPUT)
    parser.add_argument("--runtime", default=DEFAULT_RUNTIME)
    parser.add_argument("--report", default=DEFAULT_REPORT)
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    manifest = build(repo, repo / args.input, repo / args.runtime, repo / args.report)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
