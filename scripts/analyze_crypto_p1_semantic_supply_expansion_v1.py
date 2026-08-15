from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from alphafactory_crypto.broad_search import search_engine_v1 as engine
from alphafactory_crypto.broad_search.temporal_representation_tournament_v1 import _load_frozen_inputs
from alphafactory_crypto.broad_search.temporal_targeted_deepening_v1 import (
    CANONICAL_SIMILARITY_THRESHOLD,
    _cluster_labels,
    _cluster_summary,
    _fingerprint_matrix,
    _realization_id,
    _stable_row_id,
)


ALLOWED_DECISIONS = {
    "P1_SEMANTIC_EXPANSION_PASS",
    "P1_SEMANTIC_EXPANSION_PARTIAL",
    "P1_HYPOTHESIS_FAMILY_WEAK",
    "BLOCK_ROBUST_V2_INVALID",
    "GLOBAL_SEARCH_CORE_REGRESSION",
    "RESEARCH_INVALID",
}


def _sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest().upper()


def _bool(row: Mapping[str, Any], key: str) -> bool:
    value = row.get(key)
    return value.strip().lower() == "true" if isinstance(value, str) else bool(value)


def _dual(row: Mapping[str, Any]) -> bool:
    return float(row.get("left_incremental_net_mean") or 0.0) > 0.0 and float(row.get("right_incremental_net_mean") or 0.0) > 0.0


def _cluster_assignments(
    baseline_rows: Sequence[Mapping[str, Any]], current: Sequence[Mapping[str, Any]]
) -> tuple[dict[str, str], dict[str, dict[str, Any]]]:
    matched = [row for row in current if _bool(row, "matched_positive")]
    combined = [{**dict(row), "_origin": "baseline"} for row in baseline_rows] + [{**dict(row), "_origin": "current"} for row in matched]
    combined.sort(key=_stable_row_id)
    labels = _cluster_labels(_fingerprint_matrix(combined), CANONICAL_SIMILARITY_THRESHOLD)
    groups: dict[int, list[Mapping[str, Any]]] = defaultdict(list)
    for label, row in zip(labels, combined, strict=True):
        groups[int(label)].append(row)
    ordered = sorted(groups.values(), key=lambda rows: min(_stable_row_id(row) for row in rows))
    assignment: dict[str, str] = {}
    metadata: dict[str, dict[str, Any]] = {}
    for index, rows in enumerate(ordered, start=1):
        cluster_id = f"ECO_090_{index:03d}"
        baseline = [row for row in rows if row["_origin"] == "baseline"]
        active = [row for row in rows if row["_origin"] == "current"]
        metadata[cluster_id] = {
            "baseline_count": len(baseline),
            "current_count": len(active),
            "is_new": not baseline and bool(active),
            "baseline_high_quality": len(baseline) >= 2,
            "current_realizations": len({_realization_id(row) for row in active}),
            "new_realizations": len({_realization_id(row) for row in active} - {_realization_id(row) for row in baseline}),
        }
        for row in active:
            assignment[str(row["candidate_id"])] = cluster_id
    return assignment, metadata


def _group_rows(
    rows: Sequence[Mapping[str, Any]], key: str, assignments: Mapping[str, str], clusters: Mapping[str, Mapping[str, Any]]
) -> list[dict[str, Any]]:
    groups: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[str(row.get(key) or "NONE")].append(row)
    output = []
    for value, local in sorted(groups.items()):
        matched = [row for row in local if _bool(row, "matched_positive")]
        cluster_ids = {assignments[str(row["candidate_id"])] for row in matched if str(row["candidate_id"]) in assignments}
        output.append(
            {
                key: value,
                "strict": len(local),
                "matched": len(matched),
                "matched_density": len(matched) / max(1, len(local)),
                "dual_positive": sum(_dual(row) for row in local),
                "replicated": sum(_bool(row, "replicated_candidate") for row in local),
                "hq": len(matched),
                "new_hq_realization": sum(_bool(row, "dispatch_new_hq_realization") for row in local),
                "economic_clusters": len(cluster_ids),
                "new_economic_clusters": sum(bool(clusters[cluster]["is_new"]) for cluster in cluster_ids),
            }
        )
    return output


def analyze(root: Path, runtime_id: str) -> dict[str, Any]:
    runtime = root / "runtime" / runtime_id
    ledger = pd.read_parquet(runtime / "candidate_ledger.parquet").to_dict("records")
    complete = engine._read_json(runtime / "run_complete.json")
    baseline, _ = _load_frozen_inputs(root)
    basin = dict(complete["basin_diagnostics"])
    catalog = engine._read_json(root / "config/crypto_p1_semantic_supply_expansion_v1_catalog.json")
    assignments, cluster_meta = _cluster_assignments(baseline["matched_positive_rows"], ledger)
    g2 = [row for row in ledger if str(row.get("semantic_lane")) == "P1_G2"]
    g1 = [row for row in ledger if str(row.get("semantic_lane")) == "P1_G1"]
    p4 = [row for row in ledger if str(row.get("semantic_lane")) == "P4"]
    g2_clusters = {assignments[str(row["candidate_id"])] for row in g2 if _bool(row, "matched_positive") and str(row["candidate_id"]) in assignments}
    thresholds = dict(basin["economic_cluster_summary"]["thresholds"])
    dispatch = dict(complete["dispatcher_diagnostics"])

    def score_region(name: str, allowed: set[int]) -> dict[str, Any]:
        local = [row for row in g2 if int(row.get("dispatch_selected_score_decile") or 0) in allowed]
        return {"region": name, "strict": len(local), "matched": sum(_bool(row, "matched_positive") for row in local), "matched_density": sum(_bool(row, "matched_positive") for row in local) / max(1, len(local))}

    g2_density = sum(_bool(row, "matched_positive") for row in g2) / max(1, len(g2))
    g1_density = sum(_bool(row, "matched_positive") for row in g1) / max(1, len(g1))
    p4_matched = sum(_bool(row, "matched_positive") for row in p4)
    boundaries = [complete.get(name, 0) for name in ("validation_reads", "oos_reads", "holdout_reads", "forward_reads", "promotion_reads", "sealed_reads")]
    if any(int(value) for value in boundaries) or int(complete.get("p2_strict", -1)) or int(complete.get("p3_strict", -1)):
        decision = "RESEARCH_INVALID"
    elif not g2:
        decision = "BLOCK_ROBUST_V2_INVALID"
    elif p4 and p4_matched == 0:
        decision = "GLOBAL_SEARCH_CORE_REGRESSION"
    elif (
        sum(_bool(row, "matched_positive") for row in g2) >= 2
        and len(g2_clusters) >= 2
        and g2_density > g1_density
        and (
            any(bool(cluster_meta[value]["is_new"]) for value in g2_clusters)
            or int(basin["p1_vs_p4"]["P1_POSITION_STATE_CHANGE_TO_RESPONSE"]["high_quality_basins_deepened"]) >= 2
        )
    ):
        decision = "P1_SEMANTIC_EXPANSION_PASS"
    elif sum(_bool(row, "matched_positive") for row in g2) > 0 and g2_clusters:
        decision = "P1_SEMANTIC_EXPANSION_PARTIAL"
    else:
        decision = "P1_HYPOTHESIS_FAMILY_WEAK"
    if decision not in ALLOWED_DECISIONS:
        raise AssertionError(decision)

    low_generated = dict(dispatch.get("edit_generated") or {})
    core = {
        "schema_version": 1,
        "status": "P1_SEMANTIC_SUPPLY_EXPANSION_FINAL_ANALYSIS",
        "runtime_id": runtime_id,
        "catalog": catalog,
        "search": {
            "strict": len(ledger),
            "attempts": int(complete["attempts"]),
            "lane_outcomes": complete["semantic_lane_outcomes"],
            "p2_strict": 0,
            "p3_strict": 0,
            "matched_positive": int(complete["matched_positive"]),
        },
        "p1_g2_attribution": {
            "by_parent_p1_payload": _group_rows(g2, "parent_p1_program_id", assignments, cluster_meta),
            "by_condition_role": _group_rows(g2, "condition_role", assignments, cluster_meta),
            "by_condition_primitive": _group_rows(g2, "condition_primitive", assignments, cluster_meta),
            "by_condition_operator": _group_rows(g2, "condition_operator", assignments, cluster_meta),
            "by_condition_mode": _group_rows(g2, "condition_mode", assignments, cluster_meta),
            "by_semantic_combination": _group_rows(g2, "program_id", assignments, cluster_meta),
        },
        "p1_semantic_breadth": {
            "economic_clusters_0_95_0_90_0_85": {threshold: int(thresholds[threshold]["economic_cluster_count"]) for threshold in ("0.95", "0.90", "0.85")},
            "new_clusters_0_95_0_90_0_85": {threshold: int(thresholds[threshold]["new_economic_cluster_count"]) for threshold in ("0.95", "0.90", "0.85")},
            "p1_g2_economic_clusters_0_90": len(g2_clusters),
            "p1_g2_new_economic_clusters_0_90": sum(bool(cluster_meta[value]["is_new"]) for value in g2_clusters),
            "existing_hq_basins_deepened": int(basin["p1_vs_p4"]["P1_POSITION_STATE_CHANGE_TO_RESPONSE"]["high_quality_basins_deepened"]),
            "new_hq_concrete_realizations": sum(_bool(row, "dispatch_new_hq_realization") for row in g2),
            "concrete_realizations": len({_realization_id(row) for row in g2 if _bool(row, "matched_positive")}),
            "depth": basin["basin_realization_depth"],
            "depth_increase": basin["basin_realization_depth_increase"],
            "turnover_is_diagnostic": True,
        },
        "p4_health": {"strict": len(p4), "matched_positive": p4_matched, "matched_density": p4_matched / max(1, len(p4)), "frozen_semantic_basis": True},
        "dispatch_efficiency": {
            "legal_generated": int(dispatch["dispatch_counters"]["legal_generated"]),
            "selected": int(dispatch["dispatch_counters"]["dispatches"]),
            "strict_evaluated": len(ledger),
            "proposal_cpu_seconds": sum(float(row.get("proposal_compile_cpu_seconds") or 0.0) for row in ledger),
            "score_regions": [score_region("top", {0, 1, 2}), score_region("middle", {3, 4, 5, 6}), score_region("bottom", {7, 8, 9})],
            "known_low_value_generation": {key: int(low_generated.get(key, 0)) for key in ("role", "operator", "component")},
        },
        "next_decision": decision,
        "validation_reads": 0,
        "oos_reads": 0,
        "holdout_reads": 0,
        "forward_reads": 0,
        "promotion_reads": 0,
        "sealed_reads": 0,
        "automatic_next_run_started": False,
    }
    return {**core, "analysis_sha256": _sha(core)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--runtime-id", required=True)
    args = parser.parse_args()
    result = analyze(args.repo_root.resolve(), args.runtime_id)
    path = args.repo_root.resolve() / "runtime" / args.runtime_id / "final_analysis.json"
    engine._write_json(path, result)
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
