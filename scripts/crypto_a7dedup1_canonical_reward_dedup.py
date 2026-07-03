from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


NUMERIC_SORT_KEYS = [
    "objective_pass_count",
    "pareto_front",
    "min_oos_floor_sortino",
    "min_oos_sortino",
    "validation_sortino",
    "test_sortino",
    "recent_sortino",
    "stress_floor_sortino",
    "recent_rankic",
    "train_sortino",
]


def canonical_expression(expr: str) -> str:
    return re.sub(r"\s+", "", expr or "").lower()


def canonical_skeleton(row: dict[str, str]) -> str:
    skeleton = row.get("skeleton_key") or row.get("expression") or ""
    return re.sub(r"\s+", "", skeleton).lower()


def to_float(value: Any, default: float = float("-inf")) -> float:
    try:
        if value is None or value == "":
            return default
        if isinstance(value, bool):
            return 1.0 if value else 0.0
        text = str(value).strip()
        if text.lower() == "true":
            return 1.0
        if text.lower() == "false":
            return 0.0
        return float(text)
    except Exception:
        return default


def score_tuple(row: dict[str, str]) -> tuple[float, ...]:
    return tuple(to_float(row.get(key)) for key in NUMERIC_SORT_KEYS)


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def main() -> int:
    parser = argparse.ArgumentParser(description="A7DEDUP-1 canonical accepted-queue dedup and family cap")
    parser.add_argument("--input", required=True)
    parser.add_argument("--runtime-dir", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--max-per-expression", type=int, default=1)
    parser.add_argument("--max-per-skeleton", type=int, default=1)
    parser.add_argument("--max-per-semantic-pair", type=int, default=2)
    parser.add_argument("--max-per-base-family", type=int, default=2)
    args = parser.parse_args()

    input_path = Path(args.input)
    runtime_dir = Path(args.runtime_dir)
    report_path = Path(args.report)
    rows = read_csv(input_path)

    enriched: list[dict[str, Any]] = []
    for idx, row in enumerate(rows):
        item: dict[str, Any] = dict(row)
        item["_input_order"] = idx
        item["canonical_expression"] = canonical_expression(row.get("expression", ""))
        item["canonical_skeleton"] = canonical_skeleton(row)
        item["semantic_pair_key"] = (row.get("semantic_pair") or "unknown").lower()
        item["base_family_key"] = (row.get("source_lag_required_families") or row.get("semantic_pair") or "unknown").lower()
        enriched.append(item)

    enriched.sort(key=score_tuple, reverse=True)

    expr_counts: Counter[str] = Counter()
    skeleton_counts: Counter[str] = Counter()
    semantic_counts: Counter[str] = Counter()
    family_counts: Counter[str] = Counter()
    selected: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []

    for row in enriched:
        reasons: list[str] = []
        if expr_counts[row["canonical_expression"]] >= args.max_per_expression:
            reasons.append("exact_expression_cap")
        if skeleton_counts[row["canonical_skeleton"]] >= args.max_per_skeleton:
            reasons.append("skeleton_cap")
        if semantic_counts[row["semantic_pair_key"]] >= args.max_per_semantic_pair:
            reasons.append("semantic_pair_cap")
        if family_counts[row["base_family_key"]] >= args.max_per_base_family:
            reasons.append("base_family_cap")

        if reasons:
            out = dict(row)
            out["dedup_reject_reasons"] = ";".join(reasons)
            rejected.append(out)
            continue

        expr_counts[row["canonical_expression"]] += 1
        skeleton_counts[row["canonical_skeleton"]] += 1
        semantic_counts[row["semantic_pair_key"]] += 1
        family_counts[row["base_family_key"]] += 1
        out = dict(row)
        out["dedup_rank"] = len(selected) + 1
        out["dedup_reject_reasons"] = ""
        selected.append(out)

    fieldnames = list(rows[0].keys()) if rows else []
    extra_fields = [
        "canonical_expression",
        "canonical_skeleton",
        "semantic_pair_key",
        "base_family_key",
        "dedup_rank",
        "dedup_reject_reasons",
    ]
    output_fields = fieldnames + [f for f in extra_fields if f not in fieldnames]

    selected_path = runtime_dir / "a7dedup1_canonical_selected_queue.csv"
    rejected_path = runtime_dir / "a7dedup1_dedup_rejections.csv"
    write_csv(selected_path, selected, output_fields)
    write_csv(rejected_path, rejected, output_fields)

    summary_rows: list[dict[str, Any]] = []
    grouped: defaultdict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in enriched:
        grouped[(row["semantic_pair_key"], row["base_family_key"], row["canonical_skeleton"])].append(row)
    for (semantic, family, skeleton), group in sorted(grouped.items(), key=lambda kv: len(kv[1]), reverse=True):
        summary_rows.append(
            {
                "semantic_pair_key": semantic,
                "base_family_key": family,
                "canonical_skeleton": skeleton,
                "input_count": len(group),
                "unique_expression_count": len({r["canonical_expression"] for r in group}),
                "selected_count": sum(1 for r in selected if r["canonical_skeleton"] == skeleton),
            }
        )
    summary_path = runtime_dir / "a7dedup1_group_summary.csv"
    write_csv(summary_path, summary_rows, ["semantic_pair_key", "base_family_key", "canonical_skeleton", "input_count", "unique_expression_count", "selected_count"])

    exact_duplicate_groups = sum(1 for count in Counter(r["canonical_expression"] for r in enriched).values() if count > 1)
    decision = "PASS_A7DEDUP1_CANONICAL_QUEUE_BUILT" if selected else "HOLD_A7DEDUP1_NO_SELECTED_ROWS"
    manifest = {
        "stage": "A7DEDUP-1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "input_path": str(input_path),
        "input_rows": len(rows),
        "selected_rows": len(selected),
        "rejected_rows": len(rejected),
        "exact_duplicate_groups": exact_duplicate_groups,
        "max_per_expression": args.max_per_expression,
        "max_per_skeleton": args.max_per_skeleton,
        "max_per_semantic_pair": args.max_per_semantic_pair,
        "max_per_base_family": args.max_per_base_family,
        "selected_output": str(selected_path),
        "rejected_output": str(rejected_path),
        "summary_output": str(summary_path),
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_required": [
            "feed selected queue into mechanism expansion only as seeds",
            "enforce canonical expression and skeleton caps inside future selector/search queues",
            "audit whether OI-only dominance is real mechanism or family concentration artifact",
        ],
    }
    manifest_path = runtime_dir / "a7dedup1_manifest.json"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    top_lines = []
    for row in selected[:10]:
        top_lines.append(
            f"| {row.get('dedup_rank')} | {row.get('blueprint_id')} | {row.get('horizon_h')} | "
            f"{row.get('train_sortino')} | {row.get('validation_sortino')} | {row.get('test_sortino')} | "
            f"{row.get('recent_sortino')} | `{row.get('expression')}` |"
        )

    report = f"""# CRYPTO A7DEDUP1 Canonical Reward Queue Dedup

Generated: {manifest['generated_at']}

## Decision

`{decision}`

A7DEDUP-1 canonicalizes strict-reward accepted formulas and applies exact-expression, skeleton, semantic-pair, and base-family caps before the next mechanism expansion. This is a queue hygiene gate, not alpha proof.

## Counts

- input_rows: `{len(rows)}`
- selected_rows: `{len(selected)}`
- rejected_rows: `{len(rejected)}`
- exact_duplicate_groups: `{exact_duplicate_groups}`
- max_per_expression: `{args.max_per_expression}`
- max_per_skeleton: `{args.max_per_skeleton}`
- max_per_semantic_pair: `{args.max_per_semantic_pair}`
- max_per_base_family: `{args.max_per_base_family}`

## Selected Queue

| rank | blueprint_id | horizon_h | train_sortino | validation_sortino | test_sortino | recent_sortino | expression |
|---:|---|---:|---:|---:|---:|---:|---|
{chr(10).join(top_lines)}

## Interpretation

The accepted A7REWARD-3 queue contains repeated OI-only expressions under different blueprint IDs. Dedup keeps the strongest canonical representatives and prevents the next search from mistaking duplicate OI structures for independent breadth.

## Outputs

- selected_queue: `{selected_path}`
- rejected_rows: `{rejected_path}`
- group_summary: `{summary_path}`
- manifest: `{manifest_path}`
"""
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
