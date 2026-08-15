"""Final train-only economic and dispatch attribution for Proposal Dispatcher V1."""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

import pandas as pd

from . import search_engine_v1 as engine
from .temporal_proposal_dispatch_search_v1 import HISTORICAL_PRIOR_PATH


DECISIONS = {
    "PROPOSAL_DISPATCH_SUCCESSOR_PASS",
    "PROPOSAL_DISPATCH_PARTIAL",
    "SEMANTIC_SUPPLY_BOTTLENECK",
    "P1_SEMANTIC_SUPPLY_BOTTLENECK",
    "SEARCH_POLICY_COLLAPSE",
    "RESEARCH_INVALID",
}


def _sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest().upper()


def _group_attribution(frame: pd.DataFrame, key: str, generated: Mapping[str, Any]) -> dict[str, Any]:
    output = {}
    values = set(str(value) for value in generated) | set(frame[key].fillna("").astype(str))
    for value in sorted(values):
        rows = frame[frame[key].fillna("").astype(str) == value]
        output[value] = {
            "generated": int(generated.get(value, 0)),
            "selected": len(rows),
            "strict": len(rows),
            "matched_positive": int(rows["matched_positive"].astype(bool).sum()),
            "basin_retained": int(rows["dispatch_basin_retained"].astype(bool).sum()),
            "new_realization": int(rows["dispatch_new_realization"].astype(bool).sum()),
            "new_HQ_realization": int(rows["dispatch_new_hq_realization"].astype(bool).sum()),
        }
    return output


def _score_bands(frame: pd.DataFrame) -> dict[str, Any]:
    ranked = frame.copy()
    ranked["quality_band"] = pd.qcut(
        ranked["dispatch_selected_score"].rank(method="first"),
        10,
        labels=False,
    )
    bands = {"bottom": {0}, "middle": {4, 5}, "top": {9}}
    output = {}
    for label, values in bands.items():
        rows = ranked[ranked["quality_band"].isin(values)]
        output[label] = {
            "strict": len(rows),
            "score_mean": float(rows["dispatch_selected_score"].mean()),
            "matched_density": float(rows["matched_positive"].astype(bool).mean()),
            "basin_retention_rate": float(rows["dispatch_basin_retained"].astype(bool).mean()),
            "new_realization_rate": float(rows["dispatch_new_realization"].astype(bool).mean()),
            "new_HQ_realization_rate": float(rows["dispatch_new_hq_realization"].astype(bool).mean()),
        }
    return output


def build_final_analysis(
    repo_root: Path,
    runtime_root: Path,
    *,
    decision: str,
    rationale: Sequence[str],
) -> dict[str, Any]:
    if decision not in DECISIONS:
        raise ValueError("unknown proposal dispatcher decision")
    root, runtime = repo_root.resolve(), runtime_root.resolve()
    checker = engine._read_json(runtime / "independent_checker.json")
    if checker.get("status") != "PASS" and decision != "RESEARCH_INVALID":
        raise ValueError("non-invalid conclusion requires checker PASS")
    final = engine._read_json(runtime / "run_complete.json")
    dispatch = engine._read_json(runtime / "dispatcher_diagnostics_final.json")
    prior = engine._read_json(root / HISTORICAL_PRIOR_PATH)
    frame = pd.read_parquet(runtime / "candidate_ledger.parquet")
    basin = dict(final["basin_diagnostics"])
    clusters = dict(basin["economic_cluster_summary"]["thresholds"])
    edit = _group_attribution(frame, "dispatch_semantic_edit_type", dispatch["edit_generated"])
    target = _group_attribution(frame, "dispatch_mutation_target", dispatch["target_generated"])
    for value, evidence in target.items():
        evidence["attempts"] = evidence["generated"]
        evidence["descriptor_change"] = evidence["selected"] if value != "generic" else 0
    strict = len(frame)
    search_result = {
        "strict": strict,
        "attempts": int(final["attempts"]),
        "matched_positive": int(frame["matched_positive"].astype(bool).sum()),
        "matched_density": float(frame["matched_positive"].astype(bool).mean()),
        "P1_P4": basin["p1_vs_p4"],
        "P2_strict": int((frame["program_family_id"] == "P2_RECENT_CROWDING_EVENT_TO_RESPONSE").sum()),
        "P3_strict": int((frame["program_family_id"] == "P3_FLOW_SHOCK_PERSISTENCE_TO_ABSORPTION").sum()),
        "economic_clusters": {
            threshold: {
                "count": int(clusters[threshold]["economic_cluster_count"]),
                "new": int(clusters[threshold]["new_economic_cluster_count"]),
            }
            for threshold in ("0.95", "0.90", "0.85")
        },
        "HQ_basins_deepened": int(basin["basin_realization_depth"]["high_quality_basins_deepened"]),
        "new_HQ_realizations": int(basin["basin_realization_depth"]["new_high_quality_concrete_realizations"]),
        "wide_realizations": sum(
            int(value["concrete_realization_count"]) for value in basin["p1_vs_p4"].values()
        ),
        "depth_increments": basin["basin_realization_depth_increase"],
    }
    selected_scores = frame["dispatch_selected_score"].astype(float)
    dispatch_result = {
        "legal_candidates_generated": int(frame["dispatch_legal_generated"].sum()),
        "legal_candidates_scored": int(frame["dispatch_legal_scored"].sum()),
        "strict_selected": strict,
        "average_pool_size": float(frame["dispatch_legal_scored"].mean()),
        "median_pool_size": float(frame["dispatch_legal_scored"].median()),
        "selected_rank_distribution": dispatch["selected_rank_counts"],
        "exploitation_percent": 100.0 * float((~frame["dispatch_exploration_selected"].astype(bool)).mean()),
        "exploration_percent": 100.0 * float(frame["dispatch_exploration_selected"].astype(bool).mean()),
        "score_distribution": {
            "minimum": float(selected_scores.min()),
            "median": float(selected_scores.median()),
            "mean": float(selected_scores.mean()),
            "maximum": float(selected_scores.max()),
        },
        "source_generated": dispatch["source_generated"],
        "source_selected": dispatch["source_selected"],
        "pool_under_eight": int(dispatch["dispatch_counters"].get("pool_under_eight", 0)),
    }
    efficiency = {
        "current": {
            "matched_positive_per_1k": 1000.0 * search_result["matched_positive"] / strict,
            "new_HQ_per_1k": 1000.0 * search_result["new_HQ_realizations"] / strict,
            "new_realization_per_1k": 1000.0 * int(frame["dispatch_new_realization"].astype(bool).sum()) / strict,
            "new_economic_clusters_090_per_1k": 1000.0 * search_result["economic_clusters"]["0.90"]["new"] / strict,
        },
        "historical_train_only_campaigns": {
            str(campaign["campaign_id"]): {
                "strict": int(campaign["row_count"]),
                "matched_positive_per_1k": 1000.0 * int(campaign["outcomes"]["matched_positive"]) / max(1, int(campaign["row_count"])),
                "new_HQ_per_1k": 1000.0 * int(campaign["outcomes"]["new_hq_realization"]) / max(1, int(campaign["row_count"])),
                "new_realization_per_1k": 1000.0 * int(campaign["outcomes"]["new_realization"]) / max(1, int(campaign["row_count"])),
            }
            for campaign in prior["campaigns"]
        },
        "comparison_is_descriptive_reused_development_data": True,
    }
    core = {
        "schema_version": 1,
        "status": "FINAL_ANALYSIS_COMPLETE",
        "NEXT_DECISION": decision,
        "decision_rationale": list(rationale),
        "search_result": search_result,
        "dispatch": dispatch_result,
        "edit_attribution": edit,
        "mutation_target_attribution": target,
        "proposal_prior_quality": _score_bands(frame),
        "search_efficiency": efficiency,
        "historical_calibration": prior["calibration"],
        "canonical_checker": checker,
        "validation_reads": 0, "oos_reads": 0, "holdout_reads": 0,
        "forward_reads": 0, "promotion_reads": 0, "sealed_reads": 0,
        "automatic_next_run_started": False,
    }
    result = {**core, "final_analysis_sha256": _sha(core)}
    engine._write_json(runtime / "final_analysis.json", result)
    return result


__all__ = ["DECISIONS", "build_final_analysis"]
