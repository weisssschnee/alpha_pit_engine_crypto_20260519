from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from alphafactory_crypto.broad_search import search_engine_v1 as engine
from alphafactory_crypto.broad_search.temporal_hypothesis_frontier_v1 import P4, P5, P6
from alphafactory_crypto.broad_search.temporal_representation_tournament_v1 import _load_frozen_inputs
from alphafactory_crypto.broad_search.temporal_targeted_deepening_v1 import (
    _cluster_labels, _cluster_summary, _fingerprint_matrix, _stable_row_id,
    targeted_diagnostics,
)


def _sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest().upper()


def _as_bool(series: pd.Series) -> pd.Series:
    return series.astype(str).str.lower().isin({"1", "true", "yes"})


def _slice(frame: pd.DataFrame, columns: list[str]) -> list[dict[str, Any]]:
    output = []
    for keys, local in frame.groupby(columns, dropna=False, sort=True):
        values = keys if isinstance(keys, tuple) else (keys,)
        output.append({
            **{column: (None if pd.isna(value) else str(value)) for column, value in zip(columns, values)},
            "strict": len(local), "matched_positive": int(_as_bool(local["matched_positive"]).sum()),
            "matched_density": float(_as_bool(local["matched_positive"]).mean()),
            "replicated": int(_as_bool(local["replicated_candidate"]).sum()),
            "block_robust_reward_mean": float(local["search_reward"].astype(float).mean()),
        })
    return output


def analyze(root: Path, runtime_id: str) -> dict[str, Any]:
    runtime = root / "runtime" / runtime_id; ledger_path = runtime / "candidate_ledger.parquet"
    frame = pd.read_parquet(ledger_path); rows = frame.to_dict("records"); baseline, _ = _load_frozen_inputs(root)
    overall = targeted_diagnostics(rows, baseline=baseline, strict_boundary=len(frame))
    family = {}
    for family_id in (P5, P6, P4):
        local = frame.loc[frame["program_family_id"].astype(str) == family_id]
        matched_rows = local.loc[_as_bool(local["matched_positive"])].to_dict("records")
        clusters = _cluster_summary(list(baseline["matched_positive_rows"]), matched_rows)
        family[family_id] = {
            "strict": len(local), "matched_positive": len(matched_rows),
            "matched_density": len(matched_rows) / max(1, len(local)),
            "replicated": int(_as_bool(local["replicated_candidate"]).sum()),
            "clusters": {threshold: {
                "economic_cluster_count": int(values["economic_cluster_count"]),
                "new_economic_cluster_count": int(values["new_economic_cluster_count"]),
            } for threshold, values in clusters["thresholds"].items() if threshold in {"0.95", "0.90", "0.85"}},
        }
    current_matched = frame.loc[_as_bool(frame["matched_positive"])].to_dict("records")
    ordered_matched = sorted(current_matched, key=_stable_row_id)
    labels = (
        _cluster_labels(_fingerprint_matrix(ordered_matched), 0.90)
        if ordered_matched else []
    )
    overlap = Counter()
    independent = Counter()
    memberships: dict[int, set[str]] = {}
    for label, row in zip(labels, ordered_matched, strict=True):
        memberships.setdefault(int(label), set()).add(str(row.get("program_family_id") or ""))
    for family_set in memberships.values():
        families = sorted(family_set - {""})
        if len(families) == 1:
            independent[families[0]] += 1
        elif len(families) > 1:
            overlap["+".join(families)] += 1
    p5_productive = family[P5]["clusters"]["0.90"]["new_economic_cluster_count"] > 0 and family[P5]["matched_positive"] > 0
    p6_productive = family[P6]["clusters"]["0.90"]["new_economic_cluster_count"] > 0 and family[P6]["matched_positive"] > 0
    p4_healthy = family[P4]["strict"] >= 5_000 and family[P4]["matched_density"] >= 0.05
    if not p4_healthy:
        decision = "GLOBAL_SEARCH_CORE_REGRESSION"
    elif p5_productive and p6_productive:
        decision = "HYPOTHESIS_FRONTIER_PASS"
    elif p5_productive:
        decision = "P5_PRODUCTIVE_P6_WEAK"
    elif p6_productive:
        decision = "P6_PRODUCTIVE_P5_WEAK"
    elif any(item["matched_positive"] for item in family.values() if item is not family[P4]):
        decision = "FRONTIER_PARTIAL"
    else:
        decision = "FRONTIER_SEMANTIC_SUPPLY_WEAK"
    catalog = engine._read_json(root / "config/crypto_temporal_hypothesis_frontier_v1_catalog.json")
    source_gap = engine._read_json(root / "config/crypto_temporal_hypothesis_frontier_v1_source_gap.json")
    run_complete = engine._read_json(runtime / "run_complete.json")
    core = {
        "schema_version": 1, "status": "TEMPORAL_HYPOTHESIS_FRONTIER_ANALYSIS_COMPLETE",
        "runtime_id": runtime_id, "strict": len(frame), "attempts": int(run_complete["attempts"]),
        "frontier_catalog": {"raw_possibilities": source_gap["raw_possible_combinations"], "accepted_semantics": catalog["accepted_semantics"], "family_counts": catalog["family_counts"], "rejection_reasons": source_gap["rejection_reasons"], "historical_provenance": source_gap["historical_provenance"]},
        "family_outcomes": family,
        "economic_breadth": overall["economic_cluster_summary"],
        "basin_realization_depth": overall["basin_realization_depth"],
        "basin_realization_depth_increase": overall["basin_realization_depth_increase"],
        "cross_family_overlap_0_90": dict(sorted(overlap.items())),
        "independent_current_clusters_0_90": dict(sorted(independent.items())),
        "p5_semantic_attribution": _slice(frame.loc[frame["program_family_id"].astype(str) == P5], ["semantic_motif", "temporal_primitive", "condition_role", "operator_path"]),
        "p6_semantic_attribution": _slice(frame.loc[frame["program_family_id"].astype(str) == P6], ["semantic_motif", "temporal_primitive", "condition_role", "operator_path"]),
        "dispatch_efficiency": {
            "legal_generated": int(frame["dispatch_legal_generated"].sum()), "legal_scored": int(frame["dispatch_legal_scored"].sum()),
            "selected": len(frame), "score_deciles": _slice(frame, ["dispatch_selected_score_decile", "semantic_lane"]),
            "construction_routes": dict(sorted(Counter(frame["dispatch_construction_route"].astype(str)).items())),
        },
        "p4_health": {**family[P4], "healthy": p4_healthy},
        "boundaries": {name: int(run_complete[name]) for name in ("validation_reads", "oos_reads", "holdout_reads", "forward_reads", "promotion_reads", "sealed_reads")},
        "next_decision": decision, "automatic_next_run_started": False,
    }
    return {**core, "analysis_sha256": _sha(core)}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--repo-root", type=Path, required=True); parser.add_argument("--runtime-id", required=True); parser.add_argument("--output", type=Path)
    args = parser.parse_args(); result = analyze(args.repo_root.resolve(), args.runtime_id); output = args.output or args.repo_root / "runtime" / args.runtime_id / "frontier_analysis.json"; engine._write_json(output, result); print(json.dumps(result, sort_keys=True, separators=(",", ":"))); return 0


if __name__ == "__main__": raise SystemExit(main())
