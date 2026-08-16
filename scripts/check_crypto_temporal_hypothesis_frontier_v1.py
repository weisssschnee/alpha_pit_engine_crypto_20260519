from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from alphafactory_crypto.broad_search import search_engine_v1 as engine
from alphafactory_crypto.broad_search.expression import FieldContract, TypedExpressionRegistry
from alphafactory_crypto.broad_search.temporal_hypothesis_frontier_search_v1 import RAW_ATTEMPT_TERMINAL, STRICT_CAP
from alphafactory_crypto.broad_search.temporal_hypothesis_frontier_v1 import P4, P5, P6
from alphafactory_crypto.broad_search.temporal_program_search_v1 import CONFIG_PATH, _limits


def _sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest().upper()


def check(root: Path, runtime_id: str) -> dict[str, Any]:
    runtime = root / "runtime" / runtime_id; run = engine._read_json(runtime / "run_complete.json"); analysis = engine._read_json(runtime / "frontier_analysis.json"); frame = pd.read_parquet(runtime / "candidate_ledger.parquet")
    errors = []
    run_core = {key: value for key, value in run.items() if key != "run_result_sha256"}
    if run.get("run_result_sha256") != _sha(run_core): errors.append("run_result_hash")
    if int(run.get("strict", -1)) != len(frame): errors.append("strict_row_count")
    if run.get("status") == "TEMPORAL_HYPOTHESIS_FRONTIER_30000_COMPLETE" and len(frame) != STRICT_CAP: errors.append("hard_cap")
    if run.get("status") not in {"TEMPORAL_HYPOTHESIS_FRONTIER_30000_COMPLETE", RAW_ATTEMPT_TERMINAL}: errors.append("terminal_status")
    families = set(frame["program_family_id"].astype(str))
    if not families <= {P5, P6, P4} or not {P5, P6, P4} <= families: errors.append("family_scope")
    if any(int(run.get(name, -1)) != 0 for name in ("validation_reads", "oos_reads", "holdout_reads", "forward_reads", "promotion_reads", "sealed_reads")): errors.append("forbidden_reads")
    if not frame["matched_control_valid"].astype(bool).all() or not frame["strict_cost_evaluated"].astype(bool).all(): errors.append("strict_boundary_integrity")
    shares = frame["semantic_lane"].value_counts(normalize=True).to_dict()
    if len(frame) == STRICT_CAP and any(abs(float(shares.get(lane, 0.0)) - target) > 0.01 for lane, target in {"P5": 0.4, "P6": 0.4, "P4": 0.2}.items()): errors.append("lane_allocation")
    config = engine._read_json(root / CONFIG_PATH); rows = engine._read_json(root / "runtime/crypto_search_engine_v1_4_oi_flow_20260728/aligned_carrier_manifest.json")["contracts"]
    registry = TypedExpressionRegistry(tuple(FieldContract(str(row["field_id"]), str(row["value_type"]), str(row["unit"]), int(row["observable_lag_hours"]), str(row["pit_authority"])) for row in rows), **_limits(config))
    rebuild_failures = 0
    for raw in frame["candidate_spec_json"].astype(str):
        candidate = engine.CandidateSpec.from_dict(json.loads(raw))
        rebuild_failures += int(not engine._candidate_rebuild_verified(registry, candidate, {}))
    if rebuild_failures: errors.append("candidate_rebuild")
    analysis_core = {key: value for key, value in analysis.items() if key != "analysis_sha256"}
    if analysis.get("analysis_sha256") != _sha(analysis_core): errors.append("analysis_hash")
    core = {
        "schema_version": 1, "status": "PASS" if not errors else "FAIL",
        "runtime_id": runtime_id, "strict": len(frame), "attempts": int(run["attempts"]),
        "family_counts": frame["program_family_id"].value_counts().sort_index().to_dict(),
        "lane_shares": {str(key): float(value) for key, value in shares.items()},
        "candidate_rebuild_failures": rebuild_failures, "canonical_analysis_sha256": analysis.get("analysis_sha256"),
        "next_decision": analysis.get("next_decision"), "errors": errors,
        "validation_reads": 0, "oos_reads": 0, "holdout_reads": 0, "forward_reads": 0, "promotion_reads": 0, "sealed_reads": 0,
    }
    return {**core, "checker_sha256": _sha(core)}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--repo-root", type=Path, required=True); parser.add_argument("--runtime-id", required=True); parser.add_argument("--output", type=Path)
    args = parser.parse_args(); result = check(args.repo_root.resolve(), args.runtime_id); output = args.output or args.repo_root / "runtime" / args.runtime_id / "canonical_checker.json"; engine._write_json(output, result); print(json.dumps(result, sort_keys=True, separators=(",", ":"))); return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__": raise SystemExit(main())
