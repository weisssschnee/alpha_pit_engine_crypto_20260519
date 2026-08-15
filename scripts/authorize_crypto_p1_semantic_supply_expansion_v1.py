from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from alphafactory_crypto.broad_search import search_engine_v1 as engine
from alphafactory_crypto.broad_search.temporal_p1_semantic_expansion_search_v1 import (
    AUTHORIZATION_PATH,
    CHECKPOINT_SIZE,
    EXECUTION_MODE,
    G2_CATALOG_PATH,
    HISTORICAL_PRIOR_PATH,
    LANE_SEEDS,
    LANE_TARGETS,
    RAW_ATTEMPT_CAP,
    REQUIRED_EXECUTION_COMPONENT_PATHS,
    SOURCE_GAP_PATH,
    STRICT_CAP,
    WORKERS,
    authorization_content_sha,
)
from alphafactory_crypto.broad_search.temporal_representation_successor_v1 import ACTIVE_FAMILIES
from alphafactory_crypto.broad_search.temporal_representation_tournament_v1 import (
    EXPECTED_AUTHORITY_IDENTITY,
    EXPECTED_LEDGER_SHA256,
    EXPECTED_MARKET_INPUT_IDENTITY,
    EXPECTED_PC2_EXECUTOR_IDENTITY,
    EXPECTED_POOL_SHA256,
    EXPECTED_PREAUTH_RECEIPT_SHA256,
)


def _git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()


def _file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--runtime-id", required=True)
    parser.add_argument("--decision-id", required=True)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    if _git(root, "status", "--porcelain=v1"):
        raise RuntimeError("implementation checkout must be clean before authorization")
    if _git(root, "rev-parse", "HEAD") != _git(root, "rev-parse", "@{upstream}"):
        raise RuntimeError("implementation commit must be tracking before authorization")
    implementation_sha = _git(root, "rev-parse", "HEAD").lower()
    components = {
        relative: _git(root, "rev-parse", f"{implementation_sha}:{relative}").lower()
        for relative in REQUIRED_EXECUTION_COMPONENT_PATHS
    }
    prior = engine._read_json(root / HISTORICAL_PRIOR_PATH)
    source_gap = engine._read_json(root / SOURCE_GAP_PATH)
    catalog = engine._read_json(root / G2_CATALOG_PATH)
    payload = {
        "schema_version": 1,
        "authorization_id": "CRYPTO_TEMPORAL_P1_SEMANTIC_SUPPLY_EXPANSION_V1_AUTHORIZATION",
        "decision_id": args.decision_id,
        "authority": "CURRENT_USER_INSTRUCTION",
        "execution_mode": EXECUTION_MODE,
        "status": "RUN_AUTHORIZED_ONE_TIME_P1_SEMANTIC_EXPANSION_20000",
        "run_authorized": True,
        "consumed": False,
        "implementation_source_sha": implementation_sha,
        "runtime_id": args.runtime_id,
        "budget": {
            "strict_evaluated_maximum": STRICT_CAP,
            "raw_generation_attempts_maximum": RAW_ATTEMPT_CAP,
            "checkpoint_size": CHECKPOINT_SIZE,
            "diagnostic_boundary": 10_000,
            "workers": WORKERS,
        },
        "lane_seeds": list(LANE_SEEDS),
        "lane_targets": LANE_TARGETS,
        "active_program_families": list(ACTIVE_FAMILIES),
        "search_policy": {
            "p1_g2_clear_majority": True,
            "p1_g1_reference": True,
            "p4_frozen_health_reference": True,
            "proposal_dispatcher": "TEMPORAL_PROPOSAL_DISPATCHER_V1",
            "adaptive_basin_local_qd": True,
            "new_basin_discovery_allowed": True,
            "automatic_budget_expansion": False,
        },
        "frozen_inputs": {
            "ledger_rows": 50_000,
            "ledger_sha256": EXPECTED_LEDGER_SHA256,
            "matched_positive": 302,
            "target_basins": 23,
            "frozen_parents": 228,
            "parent_pool_sha256": EXPECTED_POOL_SHA256,
            "preauthorization_receipt_sha256": EXPECTED_PREAUTH_RECEIPT_SHA256,
        },
        "historical_prior_path": HISTORICAL_PRIOR_PATH,
        "historical_prior_file_sha256": _file_sha(root / HISTORICAL_PRIOR_PATH),
        "historical_prior_sha256": prior["prior_sha256"],
        "source_gap_path": SOURCE_GAP_PATH,
        "source_gap_file_sha256": _file_sha(root / SOURCE_GAP_PATH),
        "source_gap_sha256": source_gap["source_gap_sha256"],
        "p1_g2_catalog_path": G2_CATALOG_PATH,
        "p1_g2_catalog_file_sha256": _file_sha(root / G2_CATALOG_PATH),
        "p1_g2_catalog_sha256": catalog["catalog_sha256"],
        "authority_identity": EXPECTED_AUTHORITY_IDENTITY,
        "market_input_identity": EXPECTED_MARKET_INPUT_IDENTITY,
        "pc2_executor_identity": EXPECTED_PC2_EXECUTOR_IDENTITY,
        "execution_component_blob_oids": components,
        "forbidden_reads": {"validation": 0, "oos": 0, "holdout": 0, "forward": 0, "promotion": 0, "sealed": 0},
        "run_authorization": {"decision_id": args.decision_id, "scope": EXECUTION_MODE, "one_time": True},
    }
    payload["authorization_sha256"] = authorization_content_sha(payload)
    engine._write_json(root / AUTHORIZATION_PATH, payload)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
