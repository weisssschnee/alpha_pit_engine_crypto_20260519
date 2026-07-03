from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_INPUT = "runtime/a7shadow0_historical_strong_candidate_consolidation_20260703/a7shadow0_shadow_readiness_review_queue.csv"
DEFAULT_RUNTIME = "runtime/a7shadow2_signal_overlap_dedup_20260703"
DEFAULT_REPORT = "reports/CRYPTO_A7SHADOW2_SIGNAL_OVERLAP_DEDUP_20260703.md"

OPERATORS = {
    "abs",
    "add",
    "clip",
    "csrank",
    "decay",
    "delta",
    "mean",
    "mul",
    "neg",
    "rank",
    "safediv",
    "sign",
    "sub",
    "tsrank",
    "zscore",
}


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


def to_float(value: Any, default: float = float("-inf")) -> float:
    try:
        if value is None or value == "":
            return default
        return float(str(value).strip())
    except Exception:
        return default


def canonical_expression(expr: str) -> str:
    return re.sub(r"\s+", "", expr or "").lower()


def parameterless_signature(expr: str) -> str:
    text = canonical_expression(expr)
    return re.sub(r"\d+", "N", text)


def tokens(expr: str) -> list[str]:
    return [tok.lower() for tok in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", expr or "")]


def operator_set(expr: str) -> set[str]:
    return {tok for tok in tokens(expr) if tok in OPERATORS}


def field_set(expr: str) -> set[str]:
    out = set()
    for tok in tokens(expr):
        if tok in OPERATORS:
            continue
        if tok in {"true", "false", "nan", "inf"}:
            continue
        out.add(tok)
    return out


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


def score_row(row: dict[str, Any]) -> tuple[float, ...]:
    return (
        to_float(row.get("min_oos_floor_sortino"), 0.0),
        to_float(row.get("stress_floor_sortino"), 0.0),
        to_float(row.get("test_sortino"), 0.0),
        to_float(row.get("validation_sortino"), 0.0),
        to_float(row.get("source_count"), 0.0),
        -to_float(row.get("recent_avg_turnover"), 0.0),
    )


class UnionFind:
    def __init__(self, values: list[str]) -> None:
        self.parent = {v: v for v in values}

    def find(self, value: str) -> str:
        parent = self.parent[value]
        if parent != value:
            self.parent[value] = self.find(parent)
        return self.parent[value]

    def union(self, a: str, b: str) -> None:
        ra = self.find(a)
        rb = self.find(b)
        if ra != rb:
            self.parent[rb] = ra


def overlap_decision(a: dict[str, Any], b: dict[str, Any]) -> tuple[str, str]:
    exact = a["canonical_expression"] == b["canonical_expression"]
    parameterless = a["parameterless_signature"] == b["parameterless_signature"]
    same_semantic = a["semantic_pair"] == b["semantic_pair"]
    same_horizon = str(a["horizon_h"]) == str(b["horizon_h"])
    field_j = jaccard(a["_fields"], b["_fields"])
    op_j = jaccard(a["_operators"], b["_operators"])

    if exact:
        return "DUPLICATE_EXACT_EXPRESSION", "same_expression"
    if parameterless and same_semantic:
        return "DUPLICATE_PARAMETER_VARIANT", "same_parameterless_signature_and_semantic_pair"
    if same_semantic and same_horizon and field_j >= 0.75 and op_j >= 0.60:
        return "NEAR_DUPLICATE_SAME_MECHANISM", "same_semantic_horizon_high_field_operator_overlap"
    if field_j >= 0.80 and op_j >= 0.70:
        return "HIGH_OVERLAP_REVIEW", "high_field_operator_overlap"
    if same_semantic and field_j >= 0.50:
        return "MECHANISM_CLUSTER_REVIEW", "same_semantic_pair_partial_field_overlap"
    return "DISTINCT_OR_LOW_OVERLAP", "low_overlap"


def build(repo: Path, input_path: Path, runtime: Path, report: Path) -> dict[str, Any]:
    rows = read_csv(input_path)
    enriched: list[dict[str, Any]] = []
    for idx, row in enumerate(rows, start=1):
        expr = row.get("expression") or row.get("formula") or ""
        fields = field_set(expr)
        ops = operator_set(expr)
        item: dict[str, Any] = dict(row)
        item.update(
            {
                "candidate_id": f"a7shadow2_c{idx:03d}",
                "canonical_expression": canonical_expression(expr),
                "parameterless_signature": parameterless_signature(expr),
                "field_tokens": "|".join(sorted(fields)),
                "operator_tokens": "|".join(sorted(ops)),
                "field_count": len(fields),
                "operator_count": len(ops),
                "_fields": fields,
                "_operators": ops,
            }
        )
        enriched.append(item)

    ids = [row["candidate_id"] for row in enriched]
    uf = UnionFind(ids)
    pair_rows: list[dict[str, Any]] = []
    by_id = {row["candidate_id"]: row for row in enriched}

    for i, left in enumerate(enriched):
        for right in enriched[i + 1 :]:
            decision, reason = overlap_decision(left, right)
            if decision != "DISTINCT_OR_LOW_OVERLAP":
                uf.union(left["candidate_id"], right["candidate_id"])
            pair_rows.append(
                {
                    "left_candidate_id": left["candidate_id"],
                    "right_candidate_id": right["candidate_id"],
                    "left_rank": left.get("shadow_rank"),
                    "right_rank": right.get("shadow_rank"),
                    "left_expression": left.get("expression"),
                    "right_expression": right.get("expression"),
                    "left_semantic_pair": left.get("semantic_pair"),
                    "right_semantic_pair": right.get("semantic_pair"),
                    "left_horizon_h": left.get("horizon_h"),
                    "right_horizon_h": right.get("horizon_h"),
                    "field_jaccard": f"{jaccard(left['_fields'], right['_fields']):.6f}",
                    "operator_jaccard": f"{jaccard(left['_operators'], right['_operators']):.6f}",
                    "same_expression": left["canonical_expression"] == right["canonical_expression"],
                    "same_parameterless_signature": left["parameterless_signature"] == right["parameterless_signature"],
                    "overlap_decision": decision,
                    "overlap_reason": reason,
                }
            )

    cluster_members: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in enriched:
        cluster_members[uf.find(row["candidate_id"])].append(row)

    cluster_id_map: dict[str, str] = {}
    for n, root in enumerate(sorted(cluster_members), start=1):
        cluster_id_map[root] = f"a7shadow2_cluster_{n:02d}"

    keep_rows: list[dict[str, Any]] = []
    duplicate_rows: list[dict[str, Any]] = []
    cluster_summary: list[dict[str, Any]] = []
    review_rows: list[dict[str, Any]] = []

    for root, members in cluster_members.items():
        cluster_id = cluster_id_map[root]
        ordered = sorted(members, key=score_row, reverse=True)
        leader = ordered[0]
        semantic_counts = Counter(str(m.get("semantic_pair", "")) for m in members)
        field_counts = Counter()
        operator_counts = Counter()
        for member in members:
            field_counts.update(member["_fields"])
            operator_counts.update(member["_operators"])

        if len(members) == 1:
            cluster_decision = "KEEP_UNIQUE_MECHANISM_REVIEW"
        else:
            cluster_decision = "KEEP_CLUSTER_LEADER_HOLD_OVERLAP_VARIANTS"

        cluster_summary.append(
            {
                "cluster_id": cluster_id,
                "cluster_decision": cluster_decision,
                "member_count": len(members),
                "leader_candidate_id": leader["candidate_id"],
                "leader_shadow_rank": leader.get("shadow_rank"),
                "leader_expression": leader.get("expression"),
                "semantic_pairs": "|".join(f"{k}:{v}" for k, v in semantic_counts.most_common()),
                "dominant_fields": "|".join(f"{k}:{v}" for k, v in field_counts.most_common()),
                "dominant_operators": "|".join(f"{k}:{v}" for k, v in operator_counts.most_common()),
                "leader_min_oos_floor_sortino": leader.get("min_oos_floor_sortino"),
                "leader_stress_floor_sortino": leader.get("stress_floor_sortino"),
                "leader_test_sortino": leader.get("test_sortino"),
            }
        )

        for rank_in_cluster, member in enumerate(ordered, start=1):
            out = dict(member)
            out["cluster_id"] = cluster_id
            out["cluster_rank"] = rank_in_cluster
            out["dedup_decision"] = "KEEP_FOR_NEXT_REVIEW" if rank_in_cluster == 1 else "HOLD_OVERLAP_VARIANT"
            out["dedup_reason"] = "best_cluster_score" if rank_in_cluster == 1 else f"overlaps_cluster_leader:{leader['candidate_id']}"
            review_rows.append(out)
            if rank_in_cluster == 1:
                keep_rows.append(out)
            else:
                duplicate_rows.append(out)

    review_rows = sorted(review_rows, key=lambda r: int(str(r.get("shadow_rank") or "999")))
    keep_rows = sorted(keep_rows, key=score_row, reverse=True)
    duplicate_rows = sorted(duplicate_rows, key=lambda r: (r.get("cluster_id", ""), int(str(r.get("cluster_rank") or "999"))))

    public_fields = [
        "candidate_id",
        "cluster_id",
        "cluster_rank",
        "dedup_decision",
        "dedup_reason",
        "shadow_rank",
        "evidence_tier",
        "source_count",
        "semantic_pair",
        "motif",
        "horizon_h",
        "expression",
        "field_tokens",
        "operator_tokens",
        "train_sortino",
        "validation_sortino",
        "test_sortino",
        "recent_sortino",
        "min_oos_floor_sortino",
        "stress_floor_sortino",
        "recent_control_ratio",
        "recent_shuffle_control_ratio",
        "source_lag_status",
    ]

    for row in review_rows:
        row.pop("_fields", None)
        row.pop("_operators", None)
    for row in pair_rows:
        pass

    write_csv(runtime / "a7shadow2_review_queue_dedup.csv", review_rows, public_fields)
    write_csv(runtime / "a7shadow2_keep_queue.csv", keep_rows, public_fields)
    write_csv(runtime / "a7shadow2_hold_overlap_variants.csv", duplicate_rows, public_fields)
    write_csv(
        runtime / "a7shadow2_pairwise_overlap.csv",
        pair_rows,
        [
            "left_candidate_id",
            "right_candidate_id",
            "left_rank",
            "right_rank",
            "left_expression",
            "right_expression",
            "left_semantic_pair",
            "right_semantic_pair",
            "left_horizon_h",
            "right_horizon_h",
            "field_jaccard",
            "operator_jaccard",
            "same_expression",
            "same_parameterless_signature",
            "overlap_decision",
            "overlap_reason",
        ],
    )
    write_csv(
        runtime / "a7shadow2_cluster_summary.csv",
        sorted(cluster_summary, key=lambda r: r["cluster_id"]),
        [
            "cluster_id",
            "cluster_decision",
            "member_count",
            "leader_candidate_id",
            "leader_shadow_rank",
            "leader_expression",
            "semantic_pairs",
            "dominant_fields",
            "dominant_operators",
            "leader_min_oos_floor_sortino",
            "leader_stress_floor_sortino",
            "leader_test_sortino",
        ],
    )

    field_family_counts = Counter()
    for row in rows:
        for part in str(row.get("semantic_pair", "")).split("|"):
            if part:
                field_family_counts[part] += 1

    manifest = {
        "stage": "A7SHADOW-2",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "decision": "PASS_A7SHADOW2_SIGNAL_OVERLAP_DEDUP_BUILT",
        "input": str(input_path),
        "input_rows": len(rows),
        "dedup_keep_rows": len(keep_rows),
        "hold_overlap_variant_rows": len(duplicate_rows),
        "cluster_count": len(cluster_members),
        "pairwise_rows": len(pair_rows),
        "field_family_counts": dict(field_family_counts.most_common()),
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "authorizes_execution_realism_replay": True,
        "next_required": [
            "run execution realism and cost-capacity replay on a7shadow2_keep_queue",
            "run live data adapter health check before any shadow book",
        ],
    }
    (runtime / "a7shadow2_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    report.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# CRYPTO A7SHADOW2 Signal Overlap Dedup",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "This stage deduplicates the historical shadow-readiness review queue by formula expression, field tokens, operator tokens, semantic family, and horizon. It does not authorize alpha proof, paper trading, shadow trading, or live trading.",
        "",
        "## Counts",
        "",
        f"- input_rows: `{manifest['input_rows']}`",
        f"- cluster_count: `{manifest['cluster_count']}`",
        f"- dedup_keep_rows: `{manifest['dedup_keep_rows']}`",
        f"- hold_overlap_variant_rows: `{manifest['hold_overlap_variant_rows']}`",
        "",
        "## Cluster Leaders",
        "",
        "| cluster | members | decision | semantic_pairs | leader_expression | min_oos_floor | stress_floor | test_sortino |",
        "|---|---:|---|---|---|---:|---:|---:|",
    ]
    for row in sorted(cluster_summary, key=lambda r: r["cluster_id"]):
        lines.append(
            "| {cluster_id} | {member_count} | `{cluster_decision}` | `{semantic_pairs}` | `{leader_expression}` | {leader_min_oos_floor_sortino} | {leader_stress_floor_sortino} | {leader_test_sortino} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The historical review queue is not a broad independent alpha set yet. It is a small set of OI, premium, funding, and basis mechanisms with several parameter or expression-near variants. This points to both a feature-supply bottleneck and a generation/search-space bottleneck: the pipeline can generate many formulas, but the strict gates repeatedly promote the same information families.",
            "",
            "## Outputs",
            "",
            f"- review_queue_dedup: `{runtime / 'a7shadow2_review_queue_dedup.csv'}`",
            f"- keep_queue: `{runtime / 'a7shadow2_keep_queue.csv'}`",
            f"- hold_overlap_variants: `{runtime / 'a7shadow2_hold_overlap_variants.csv'}`",
            f"- pairwise_overlap: `{runtime / 'a7shadow2_pairwise_overlap.csv'}`",
            f"- cluster_summary: `{runtime / 'a7shadow2_cluster_summary.csv'}`",
            f"- manifest: `{runtime / 'a7shadow2_manifest.json'}`",
        ]
    )
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
    input_path = repo / args.input
    runtime = repo / args.runtime
    report = repo / args.report
    manifest = build(repo, input_path, runtime, report)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
