from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from alphafactory_crypto.broad_search import search_engine_v1 as engine
from alphafactory_crypto.broad_search.compositional18m import CandidateSpec
from alphafactory_crypto.broad_search.temporal_frontier_pocket_search_v1 import _sha
from alphafactory_crypto.broad_search.temporal_hypothesis_frontier_v1 import P5, P6


ALLOWED_DECISIONS = {
    "BOTH_POCKETS_MATURED", "P6_POCKET_MATURED", "P5_POCKET_MATURED",
    "P6_ONLY_MATURED", "P5_ONLY_MATURED", "POCKETS_PARTIAL",
    "FRONTIER_POCKETS_NOT_MATURABLE", "RESEARCH_INVALID",
}


def check(repo_root: Path, runtime_id: str) -> dict:
    root = repo_root.resolve()
    runtime = root / "runtime" / runtime_id
    run = engine._read_json(runtime / "run_complete.json")
    analysis = engine._read_json(runtime / "analysis.json")
    assurance = engine._read_json(runtime / "assurance_snapshot.json")
    frame = pd.read_parquet(runtime / "candidate_ledger.parquet")
    errors = []
    if run.get("run_result_sha256") != _sha({key: value for key, value in run.items() if key != "run_result_sha256"}):
        errors.append("run_hash")
    if analysis.get("analysis_sha256") != _sha({key: value for key, value in analysis.items() if key != "analysis_sha256"}):
        errors.append("analysis_hash")
    if len(frame) != int(run.get("strict", -1)) or len(frame) > 20_000:
        errors.append("strict")
    if set(frame["program_family_id"].astype(str)) - {P5, P6}:
        errors.append("family_scope")
    if any(int(run.get(key, -1)) != 0 for key in ("validation_reads", "oos_reads", "holdout_reads", "forward_reads", "promotion_reads", "sealed_reads")):
        errors.append("forbidden_reads")
    if any(int(analysis.get(key, -1)) != 0 for key in ("validation_reads", "oos_reads", "holdout_reads", "forward_reads", "promotion_reads", "sealed_reads")):
        errors.append("analysis_forbidden_reads")
    if run.get("next_decision") not in ALLOWED_DECISIONS:
        errors.append("next_decision")
    for row in frame.to_dict("records"):
        candidate = CandidateSpec.from_dict(json.loads(str(row["candidate_spec_json"])))
        family = str(row["program_family_id"])
        genes = candidate.generation_genes
        primitive = dict(genes["temporal_transform"])["primitive_id"]
        operator = str(genes["mechanism_spec"]["payload_operator"])
        if candidate.mapping_id != "CROSS_SECTIONAL_ZERO_NET" or genes["matched_control_schema"] != "DUAL_AXIS_A_B_AB":
            errors.append("mapping_or_control")
            break
        if (family == P5 and (primitive != "Persistence" or operator != "SafeDiv")) or (family == P6 and (primitive != "Transition" or operator != "Residual")):
            errors.append("pocket_core")
            break
        if family == P6 and not str(genes["left_field"]).startswith("bybit__"):
            errors.append("p6_venue")
            break
    if assurance["p5_sparse_event_falsification"]["classification"] == "P5_SPARSE_FIELD_ARTIFACT_RISK" and int((frame["program_family_id"].astype(str) == P5).sum()) != 0:
        errors.append("artifact_p5_budget")
    boundaries = sorted(int(path.stem.rsplit("_", 1)[1]) for path in runtime.glob("stage_decision_*.json"))
    if boundaries != list(range(2_000, len(frame) + 1, 2_000)):
        errors.append("checkpoint_boundaries")
    for path in sorted((runtime / "checkpoints").glob("checkpoint_*")):
        if engine._read_json(path / "manifest.json").get("restore_verified") is not True:
            errors.append("checkpoint_restore")
            break
    result = {
        "schema_version": 1,
        "status": "PASS" if not errors else "FAIL",
        "errors": sorted(set(errors)),
        "strict": len(frame),
        "p1_strict": 0,
        "p2_strict": 0,
        "p3_strict": 0,
        "validation_reads": 0,
        "oos_reads": 0,
        "holdout_reads": 0,
        "forward_reads": 0,
        "promotion_reads": 0,
        "sealed_reads": 0,
    }
    result = {**result, "checker_sha256": _sha(result)}
    engine._write_json(runtime / "checker.json", result)
    if errors:
        raise RuntimeError("CANONICAL_CHECKER_FAIL:" + ",".join(sorted(set(errors))))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--runtime-id", required=True)
    args = parser.parse_args()
    print(json.dumps(check(args.repo_root, args.runtime_id), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
