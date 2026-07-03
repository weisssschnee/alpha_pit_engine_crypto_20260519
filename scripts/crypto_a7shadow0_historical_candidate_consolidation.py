from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CANDIDATE_SOURCES = [
    ("A7DEDUP1_RECENT_CANONICAL", "runtime/a7dedup1_canonical_reward_queue_20260703/a7dedup1_canonical_selected_queue.csv", "strict_reward_dedup"),
    ("A7REWARD3_RECENT_MECH", "runtime/a7reward3_oi_funding_mechanism_strict_reward_20260703/a7reward1_accepted_for_next_search.csv", "strict_reward"),
    ("A7REWARD2_SOURCE_LAG_SURVIVOR", "runtime/a7reward2_source_lag_survivor_strict_reward_20260703/a7reward1_accepted_for_next_search.csv", "strict_reward"),
    ("A7SEARCH6_VALIDATION_R2", "runtime/a7search6_validation_pack_reward_r2_aggregate_20260702/a7v3s0_reward_accepted_enriched.csv", "strict_reward"),
    ("A7SEARCH6_SELECTED_R1", "runtime/a7search6_selected_full_reward_r1_aggregate_20260702/a7v3s0_reward_accepted_enriched.csv", "strict_reward"),
    ("A7V3S10_BASELINE", "runtime/a7v3s10_accepted_candidate_validation_20260614/baseline_reward_runtime/a7reward1_accepted_for_next_search.csv", "strict_reward"),
    ("A7V3S9_ACCEPTED", "runtime/a7v3s9_selected_full_reward_aggregate_20260614/a7v3s0_reward_accepted_enriched.csv", "strict_reward"),
    ("A7REWARD1_OLD_ACCEPTED", "runtime/a7reward1_portfolio_reward_model_20260610/a7reward1_accepted_for_next_search.csv", "strict_reward_legacy"),
    ("A7LS30_SELECTED_TOP", "runtime/a7ls30_productive_numeric_acceptance_20260610/a7ls30_selected_top240.csv", "diagnostic_numeric"),
    ("A7LS29_SELECTED_TOP", "runtime/a7ls29_productive_numeric_acceptance_20260610/a7ls29_selected_top160.csv", "diagnostic_numeric"),
]

SOURCE_LAG_FILES = [
    "runtime/a7shadow1_historical_source_lag_retest_20260703/a7source4_source_lag_summary.csv",
    "runtime/a7mech2_oi_funding_source_lag_retest_20260703/a7source4_source_lag_summary.csv",
    "runtime/a7source4_batch_source_lag_retest_20260703/a7source4_source_lag_summary.csv",
    "runtime/a7search6_source_lag_retest_20260703/a7search6_source_lag_retest_sensitivity.csv",
]

NUMERIC_KEYS = [
    "objective_pass_count",
    "min_oos_floor_sortino",
    "min_oos_sortino",
    "validation_sortino",
    "test_sortino",
    "recent_sortino",
    "stress_floor_sortino",
    "recent_rankic",
    "train_sortino",
    "recent_sharpe",
]

OUTPUT_FIELDS = [
    "shadow_rank",
    "consolidated_decision",
    "decision_reasons",
    "evidence_tier",
    "source_count",
    "source_ids",
    "source_kinds",
    "source_lag_status",
    "source_lag_required",
    "canonical_key",
    "canonical_expression",
    "canonical_skeleton",
    "blueprint_id",
    "semantic_pair",
    "motif",
    "horizon_h",
    "expression",
    "skeleton_key",
    "train_sortino",
    "validation_sortino",
    "test_sortino",
    "recent_sortino",
    "min_oos_sortino",
    "min_oos_floor_sortino",
    "stress_floor_sortino",
    "recent_sharpe",
    "recent_rankic",
    "recent_avg_turnover",
    "recent_control_ratio",
    "recent_shuffle_control_ratio",
    "oos_control_dominated_count",
    "oos_lag_stale_dominated_count",
    "hard_reject",
    "hard_reject_reasons",
    "gate_pass",
    "pareto_rank",
    "source_file",
]


def canonical_expression(expr: str) -> str:
    return re.sub(r"\s+", "", expr or "").lower()


def canonical_skeleton(row: dict[str, str]) -> str:
    raw = row.get("skeleton_key") or row.get("expression") or row.get("formula") or ""
    return re.sub(r"\s+", "", raw).lower()


def to_float(value: Any, default: float = float("-inf")) -> float:
    try:
        if value is None or value == "":
            return default
        text = str(value).strip()
        if text.lower() == "true":
            return 1.0
        if text.lower() == "false":
            return 0.0
        return float(text)
    except Exception:
        return default


def truthy(value: Any, default: bool = False) -> bool:
    if value is None or value == "":
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


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


def infer_source_required(row: dict[str, Any]) -> bool:
    text = " ".join(
        str(row.get(key, ""))
        for key in ["expression", "semantic_pair", "source_lag_required_fields", "source_lag_required_families"]
    ).lower()
    tokens = [
        "open_interest",
        "funding_rate_delta_state",
        "account_position",
        "top_long_short",
        "long_short",
        "positioning",
    ]
    return any(token in text for token in tokens)


def source_lag_lookup(repo: Path) -> dict[tuple[str, str], str]:
    lookup: dict[tuple[str, str], str] = {}
    for rel in SOURCE_LAG_FILES:
        path = repo / rel
        for row in read_csv(path):
            expr = row.get("formula") or row.get("expression") or ""
            horizon = str(row.get("horizon_h") or "")
            key = (canonical_expression(expr), horizon)
            gate = row.get("source_lag_gate") or ""
            if not gate and str(row.get("lag_gate_pass", "")).lower() == "true":
                gate = "PASS_SOURCE_LAG_DIAGNOSTIC"
            if gate:
                old = lookup.get(key, "")
                if gate.startswith("PASS") or (not old):
                    lookup[key] = gate
    return lookup


def row_score(row: dict[str, Any]) -> tuple[float, ...]:
    return tuple(to_float(row.get(key)) for key in NUMERIC_KEYS)


def normalize_row(source_id: str, source_path: str, source_kind: str, row: dict[str, str], lag_lookup: dict[tuple[str, str], str]) -> dict[str, Any]:
    expression = row.get("expression") or row.get("formula") or ""
    horizon = str(row.get("horizon_h") or row.get("label_horizon_h") or "")
    canonical = canonical_expression(expression)
    source_lag_required = infer_source_required({**row, "expression": expression})
    embedded_gate = row.get("source_lag_gate") or ""
    lookup_gate = lag_lookup.get((canonical, horizon), "")
    source_lag_status = embedded_gate or lookup_gate
    if source_lag_required and not source_lag_status:
        source_lag_status = "HOLD_SOURCE_LAG_NOT_TESTED"
    elif source_lag_required and not source_lag_status.startswith("PASS"):
        source_lag_status = source_lag_status or "HOLD_SOURCE_LAG_NOT_PASSED"
    elif not source_lag_required:
        source_lag_status = "NOT_REQUIRED_OR_CONTROLLED_FIELD"

    out: dict[str, Any] = dict(row)
    out.update(
        {
            "source_id": source_id,
            "source_file": source_path,
            "source_kind": source_kind,
            "expression": expression,
            "horizon_h": horizon,
            "canonical_expression": canonical,
            "canonical_skeleton": canonical_skeleton(row),
            "canonical_key": f"{canonical}|h={horizon}",
            "source_lag_required": source_lag_required,
            "source_lag_status": source_lag_status,
        }
    )
    return out


def hard_gate(row: dict[str, Any]) -> tuple[str, list[str]]:
    reasons: list[str] = []
    source_kind = row.get("source_kind", "")
    strict = source_kind.startswith("strict_reward")
    if not strict:
        return "DIAGNOSTIC_NUMERIC_ONLY", ["not_strict_reward_validated"]

    if str(row.get("hard_reject", "False")).lower() == "true":
        reasons.append("hard_reject")
    if "gate_pass" in row and not truthy(row.get("gate_pass"), default=True):
        reasons.append("gate_fail")
    if to_float(row.get("min_oos_floor_sortino"), 0.0) <= 0:
        reasons.append("min_oos_floor_not_positive")
    if to_float(row.get("min_oos_sortino"), 0.0) <= 0:
        reasons.append("min_oos_sortino_not_positive")
    if to_float(row.get("stress_floor_sortino"), 0.0) <= 0:
        reasons.append("stress_floor_not_positive")
    if to_float(row.get("oos_control_dominated_count"), 0.0) > 0:
        reasons.append("oos_control_dominated")
    if to_float(row.get("oos_lag_stale_dominated_count"), 0.0) > 0:
        reasons.append("oos_lag_stale_dominated")
    if to_float(row.get("recent_shuffle_control_ratio"), 0.0) >= 1:
        reasons.append("shuffle_control_dominated_recent")
    if row.get("source_lag_required") and not str(row.get("source_lag_status", "")).startswith("PASS"):
        reasons.append("source_lag_required_not_proven")

    if reasons:
        if reasons == ["source_lag_required_not_proven"]:
            return "SOURCE_LAG_RETEST_REQUIRED", reasons
        return "HOLD_REVIEW_REQUIRED", reasons
    return "SHADOW_READINESS_REVIEW_CANDIDATE", ["strict_reward_gate_passed"]


def evidence_tier(row: dict[str, Any], source_count: int) -> str:
    if row.get("consolidated_decision") == "SHADOW_READINESS_REVIEW_CANDIDATE":
        if source_count >= 3:
            return "TIER1_REPEATED_STRICT_EVIDENCE"
        if str(row.get("source_lag_status", "")).startswith("PASS"):
            return "TIER1_SOURCE_LAG_STRICT"
        return "TIER2_STRICT_CONTROLLED_FIELD"
    if row.get("consolidated_decision") == "SOURCE_LAG_RETEST_REQUIRED":
        return "TIER3_STRICT_NEEDS_SOURCE_LAG"
    if row.get("consolidated_decision") == "DIAGNOSTIC_NUMERIC_ONLY":
        return "TIER4_DIAGNOSTIC_NUMERIC"
    return "TIER5_HOLD"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--runtime-dir", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()

    repo = Path(args.repo_root).resolve()
    runtime_dir = Path(args.runtime_dir)
    report_path = Path(args.report)
    runtime_dir.mkdir(parents=True, exist_ok=True)

    lag_lookup = source_lag_lookup(repo)
    source_inventory: list[dict[str, Any]] = []
    normalized: list[dict[str, Any]] = []
    for source_id, rel, kind in CANDIDATE_SOURCES:
        path = repo / rel
        rows = read_csv(path)
        source_inventory.append({"source_id": source_id, "path": rel, "source_kind": kind, "exists": path.exists(), "rows": len(rows)})
        for row in rows:
            if not (row.get("expression") or row.get("formula")):
                continue
            normalized.append(normalize_row(source_id, rel, kind, row, lag_lookup))

    grouped: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in normalized:
        grouped[str(row["canonical_key"])].append(row)

    consolidated: list[dict[str, Any]] = []
    for key, group in grouped.items():
        group.sort(key=row_score, reverse=True)
        best = dict(group[0])
        source_ids = sorted({str(r["source_id"]) for r in group})
        source_kinds = sorted({str(r["source_kind"]) for r in group})
        decision, reasons = hard_gate(best)
        best["consolidated_decision"] = decision
        best["decision_reasons"] = ";".join(reasons)
        best["source_count"] = len(source_ids)
        best["source_ids"] = "|".join(source_ids)
        best["source_kinds"] = "|".join(source_kinds)
        best["evidence_tier"] = evidence_tier(best, len(source_ids))
        consolidated.append(best)

    tier_rank = {
        "SHADOW_READINESS_REVIEW_CANDIDATE": 0,
        "SOURCE_LAG_RETEST_REQUIRED": 1,
        "HOLD_REVIEW_REQUIRED": 2,
        "DIAGNOSTIC_NUMERIC_ONLY": 3,
    }
    consolidated.sort(key=lambda r: (tier_rank.get(str(r.get("consolidated_decision")), 9), -int(r.get("source_count", 0)), tuple(-x for x in row_score(r))))
    for idx, row in enumerate(consolidated, start=1):
        row["shadow_rank"] = idx if row.get("consolidated_decision") == "SHADOW_READINESS_REVIEW_CANDIDATE" else ""

    review = [r for r in consolidated if r.get("consolidated_decision") == "SHADOW_READINESS_REVIEW_CANDIDATE"]
    source_retest = [r for r in consolidated if r.get("consolidated_decision") == "SOURCE_LAG_RETEST_REQUIRED"]
    hold = [r for r in consolidated if r.get("consolidated_decision") not in {"SHADOW_READINESS_REVIEW_CANDIDATE", "SOURCE_LAG_RETEST_REQUIRED"}]

    write_csv(runtime_dir / "a7shadow0_source_inventory.csv", source_inventory, ["source_id", "path", "source_kind", "exists", "rows"])
    all_fields = sorted({k for row in normalized for k in row.keys()})
    write_csv(runtime_dir / "a7shadow0_all_candidates_normalized.csv", normalized, all_fields)
    write_csv(runtime_dir / "a7shadow0_consolidated_candidates.csv", consolidated, OUTPUT_FIELDS)
    write_csv(runtime_dir / "a7shadow0_shadow_readiness_review_queue.csv", review, OUTPUT_FIELDS)
    write_csv(runtime_dir / "a7shadow0_source_lag_retest_required_queue.csv", source_retest, OUTPUT_FIELDS)
    write_csv(runtime_dir / "a7shadow0_hold_or_diagnostic_queue.csv", hold, OUTPUT_FIELDS)

    family_counter: Counter[tuple[str, str]] = Counter()
    for row in consolidated:
        family_counter[(str(row.get("consolidated_decision")), str(row.get("semantic_pair") or "unknown"))] += 1
    family_rows = [
        {"consolidated_decision": decision, "semantic_pair": pair, "count": count}
        for (decision, pair), count in family_counter.most_common()
    ]
    write_csv(runtime_dir / "a7shadow0_family_summary.csv", family_rows, ["consolidated_decision", "semantic_pair", "count"])

    decision_counts = Counter(str(row.get("consolidated_decision")) for row in consolidated)
    manifest = {
        "stage": "A7SHADOW-0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "decision": "PASS_A7SHADOW0_HISTORICAL_STRONG_CANDIDATES_CONSOLIDATED",
        "input_source_count": len(CANDIDATE_SOURCES),
        "input_rows": len(normalized),
        "consolidated_unique_formula_horizon_rows": len(consolidated),
        "shadow_readiness_review_rows": len(review),
        "source_lag_retest_required_rows": len(source_retest),
        "hold_or_diagnostic_rows": len(hold),
        "decision_counts": dict(decision_counts),
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "authorizes_shadow_readiness_review": True,
        "next_required": [
            "run signal-correlation and overlap dedup on shadow review queue",
            "run execution realism/cost-capacity replay on review queue",
            "build live data adapter health check before any shadow book",
        ],
    }
    (runtime_dir / "a7shadow0_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    top_lines = []
    for row in review[:12]:
        top_lines.append(
            f"| {row.get('shadow_rank')} | `{row.get('semantic_pair')}` | {row.get('horizon_h')} | "
            f"{row.get('source_count')} | `{row.get('evidence_tier')}` | {row.get('train_sortino')} | "
            f"{row.get('validation_sortino')} | {row.get('test_sortino')} | {row.get('recent_sortino')} | "
            f"{row.get('min_oos_floor_sortino')} | {row.get('stress_floor_sortino')} | `{row.get('expression')}` |"
        )
    report = f"""# CRYPTO A7SHADOW0 Historical Strong Candidate Consolidation

Generated: {manifest['generated_at']}

## Decision

`{manifest['decision']}`

This stage consolidates historical strong candidates into a shadow-readiness review queue. It does not authorize alpha proof, paper trading, shadow trading, or live trading.

## Counts

- input_sources: `{manifest['input_source_count']}`
- input_rows: `{manifest['input_rows']}`
- consolidated_unique_formula_horizon_rows: `{manifest['consolidated_unique_formula_horizon_rows']}`
- shadow_readiness_review_rows: `{manifest['shadow_readiness_review_rows']}`
- source_lag_retest_required_rows: `{manifest['source_lag_retest_required_rows']}`
- hold_or_diagnostic_rows: `{manifest['hold_or_diagnostic_rows']}`

## Shadow-Readiness Review Queue

| rank | semantic_pair | horizon_h | sources | tier | train_sortino | validation_sortino | test_sortino | recent_sortino | min_oos_floor | stress_floor | expression |
|---:|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---|
{chr(10).join(top_lines)}

## Interpretation

Historical strong evidence is concentrated in a small number of mechanisms: OI/funding, OI/positioning, and basis/premium. The review queue is suitable for shadow-readiness engineering checks, not for direct shadow deployment.

## Outputs

- source_inventory: `{runtime_dir / 'a7shadow0_source_inventory.csv'}`
- consolidated: `{runtime_dir / 'a7shadow0_consolidated_candidates.csv'}`
- shadow_review_queue: `{runtime_dir / 'a7shadow0_shadow_readiness_review_queue.csv'}`
- source_lag_retest_queue: `{runtime_dir / 'a7shadow0_source_lag_retest_required_queue.csv'}`
- hold_or_diagnostic_queue: `{runtime_dir / 'a7shadow0_hold_or_diagnostic_queue.csv'}`
- family_summary: `{runtime_dir / 'a7shadow0_family_summary.csv'}`
- manifest: `{runtime_dir / 'a7shadow0_manifest.json'}`
"""
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
