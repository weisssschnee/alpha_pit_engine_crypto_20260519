from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from alphafactory_crypto.broad_search import search_engine_v1 as engine
from alphafactory_crypto.broad_search.temporal_hypothesis_frontier_search_v1 import ACTIVE_FAMILIES, AUTHORIZATION_PATH, BLOCK_ROBUST_V2_AUTHORITY, CHECKPOINT_SIZE, EXECUTION_MODE, LANE_SEEDS, LANE_TARGETS, RAW_ATTEMPT_CAP, REQUIRED_EXECUTION_COMPONENT_PATHS, STRICT_CAP, WORKERS, _file_sha, authorization_content_sha
from alphafactory_crypto.broad_search.temporal_representation_tournament_v1 import EXPECTED_AUTHORITY_IDENTITY, EXPECTED_LEDGER_SHA256, EXPECTED_MARKET_INPUT_IDENTITY, EXPECTED_PC2_EXECUTOR_IDENTITY, EXPECTED_POOL_SHA256, EXPECTED_PREAUTH_RECEIPT_SHA256


def _git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--repo-root", type=Path, required=True); parser.add_argument("--runtime-id", required=True); parser.add_argument("--offline-receipt", type=Path, required=True)
    args = parser.parse_args(); root = args.repo_root.resolve(); target = root / AUTHORIZATION_PATH
    if target.exists() or _git(root, "status", "--porcelain=v1", "--untracked-files=no") or _git(root, "rev-parse", "HEAD") != _git(root, "rev-parse", "@{upstream}"):
        raise RuntimeError("authorization requires clean synchronized implementation and absent authorization")
    offline = engine._read_json(args.offline_receipt)
    if offline.get("status") != "TEMPORAL_HYPOTHESIS_FRONTIER_PREAUTHORIZATION_OFFLINE_PASS" or int(offline.get("candidate_evaluations", -1)) != 0:
        raise RuntimeError("offline receipt not authorized")
    implementation = _git(root, "rev-parse", "HEAD").lower()
    if str(offline.get("head") or "").lower() != implementation:
        raise RuntimeError("offline receipt is not bound to the implementation HEAD")
    source_gap = engine._read_json(root / "config/crypto_temporal_hypothesis_frontier_v1_source_gap.json"); catalog = engine._read_json(root / "config/crypto_temporal_hypothesis_frontier_v1_catalog.json"); prior = engine._read_json(root / "config/crypto_temporal_proposal_dispatch_v1_historical_prior.json")
    components = {path: _git(root, "rev-parse", f"{implementation}:{path}").lower() for path in REQUIRED_EXECUTION_COMPONENT_PATHS}
    core = {
        "schema_version": 1, "execution_mode": EXECUTION_MODE, "status": "RUN_AUTHORIZED_ONE_TIME_TEMPORAL_HYPOTHESIS_FRONTIER_30000", "run_authorized": True, "consumed": False,
        "runtime_id": args.runtime_id, "implementation_source_sha": implementation,
        "active_program_families": list(ACTIVE_FAMILIES), "lane_targets": LANE_TARGETS, "lane_seeds": list(LANE_SEEDS),
        "budget": {"strict_evaluated_maximum": STRICT_CAP, "raw_generation_attempts_maximum": RAW_ATTEMPT_CAP, "checkpoint_size": CHECKPOINT_SIZE, "diagnostic_boundaries": [10_000, 20_000], "workers": WORKERS},
        "block_robust_v2_authority": BLOCK_ROBUST_V2_AUTHORITY,
        "frozen_inputs": {"ledger_sha256": EXPECTED_LEDGER_SHA256, "ledger_rows": 50_000, "matched_positive": 302, "target_basins": 23, "frozen_parents": 228, "parent_pool_sha256": EXPECTED_POOL_SHA256, "preauthorization_receipt_sha256": EXPECTED_PREAUTH_RECEIPT_SHA256},
        "authority_identity": EXPECTED_AUTHORITY_IDENTITY, "market_input_identity": EXPECTED_MARKET_INPUT_IDENTITY, "pc2_executor_identity": EXPECTED_PC2_EXECUTOR_IDENTITY,
        "source_gap_file_sha256": _file_sha(root / "config/crypto_temporal_hypothesis_frontier_v1_source_gap.json"), "source_gap_sha256": source_gap["source_gap_sha256"],
        "frontier_catalog_file_sha256": _file_sha(root / "config/crypto_temporal_hypothesis_frontier_v1_catalog.json"), "frontier_catalog_sha256": catalog["catalog_sha256"],
        "historical_prior_file_sha256": _file_sha(root / "config/crypto_temporal_proposal_dispatch_v1_historical_prior.json"), "historical_prior_sha256": prior["prior_sha256"],
        "offline_preflight_sha256": offline["offline_preflight_sha256"], "execution_component_blob_oids": components,
        "forbidden_reads": {"validation": 0, "oos": 0, "holdout": 0, "forward": 0, "promotion": 0, "sealed": 0},
        "automatic_next_run_authorized": False,
    }
    payload = {**core, "authorization_sha256": authorization_content_sha(core)}
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "authorization_sha256": payload["authorization_sha256"], "implementation_source_sha": implementation, "runtime_id": args.runtime_id}, sort_keys=True)); return 0


if __name__ == "__main__": raise SystemExit(main())
