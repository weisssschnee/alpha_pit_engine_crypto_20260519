from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from alphafactory_crypto.broad_search import search_engine_v1 as engine
from alphafactory_crypto.broad_search.temporal_frontier_pocket_v1 import load_anchor_rows
from alphafactory_crypto.broad_search.temporal_frontier_pocket_search_v1 import _sha
from alphafactory_crypto.broad_search.temporal_hypothesis_frontier_v1 import P5, P6
from alphafactory_crypto.broad_search.temporal_targeted_deepening_v1 import _cluster_summary


def analyze(repo_root: Path, runtime_id: str) -> dict:
    root = repo_root.resolve()
    runtime = root / "runtime" / runtime_id
    run = engine._read_json(runtime / "run_complete.json")
    auth = engine._read_json(runtime / "authorization_snapshot.json")
    assurance = engine._read_json(runtime / "assurance_snapshot.json")
    rows = pd.read_parquet(runtime / "candidate_ledger.parquet").to_dict("records")
    anchor_rows = load_anchor_rows(root / auth["frontier_source"]["relative_ledger_path"])
    clusters = {}
    for family in (P5, P6):
        current = [row for row in rows if str(row.get("program_family_id")) == family and bool(row.get("matched_positive"))]
        summary = _cluster_summary([anchor_rows[family]], current)
        clusters[family] = {
            threshold: {
                "economic_cluster_count": int(summary["thresholds"][threshold]["economic_cluster_count"]),
                "anchor_cluster_members": max((int(cluster["row_count"]) for cluster in summary["thresholds"][threshold]["clusters"] if int(cluster["baseline_row_count"]) == 1), default=1),
                "anchor_cluster_new_realizations": max((int(cluster["new_concrete_realization_count"]) for cluster in summary["thresholds"][threshold]["clusters"] if int(cluster["baseline_row_count"]) == 1), default=0),
            }
            for threshold in ("0.95", "0.90", "0.85")
        }
    checkpoints = []
    for decision_path in sorted(runtime.glob("stage_decision_*.json")):
        decision = engine._read_json(decision_path)
        checkpoints.append({
            "strict": int(decision["strict"]),
            "live": list(decision["live_before_scale_decision"]),
            "interval": decision["interval"],
            "successor_near_miss_mode": bool(decision["successor_near_miss_mode"]),
        })
    result = {
        "schema_version": 1,
        "status": "FRONTIER_POCKET_MATURATION_ANALYSIS_COMPLETE",
        "strict": int(run["strict"]),
        "attempts": int(run["attempts"]),
        "budget_path": [int(row["strict"]) for row in checkpoints],
        "p5_anchor_classification": assurance["p5_sparse_event_falsification"]["classification"],
        "p5_sparse_event_falsification": assurance["p5_sparse_event_falsification"],
        "p6_field_and_provenance_assurance": assurance["p6_field_and_provenance_assurance"],
        "pocket_outcomes": run["pocket_outcomes"],
        "anchor_continuity": clusters,
        "marginal_checkpoints": checkpoints,
        "p6_portability": run["p6_portability"],
        "next_decision": run["next_decision"],
        "pocket_validation_cohort_ready": bool(run["pocket_validation_cohort_ready"]),
        "validation_reads": 0,
        "oos_reads": 0,
        "holdout_reads": 0,
        "forward_reads": 0,
        "promotion_reads": 0,
        "sealed_reads": 0,
    }
    result = {**result, "analysis_sha256": _sha(result)}
    engine._write_json(runtime / "analysis.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--runtime-id", required=True)
    args = parser.parse_args()
    print(json.dumps(analyze(args.repo_root, args.runtime_id), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
