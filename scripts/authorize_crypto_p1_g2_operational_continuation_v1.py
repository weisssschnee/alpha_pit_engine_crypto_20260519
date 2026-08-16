from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from alphafactory_crypto.broad_search import search_engine_v1 as engine
from alphafactory_crypto.broad_search.temporal_p1_g2_operational_continuation_v1 import (
    AUTHORIZATION_PATH,
    CONTINUATION_COMPONENT_PATHS,
    CONTINUATION_ID,
    IMPORTED_STRICT,
    RAW_ATTEMPT_CAP,
    RAW_ATTEMPT_TERMINAL,
    SOURCE_RECEIPT_PATH,
)
from alphafactory_crypto.broad_search.temporal_p1_semantic_expansion_search_v1 import (
    BLOCK_ROBUST_V2_AUTHORITY,
    CHECKPOINT_SIZE,
    LANE_SEEDS,
    LANE_TARGETS,
    STRICT_CAP,
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
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
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
    implementation = _git(root, "rev-parse", "HEAD").lower()
    source = engine._read_json(root / SOURCE_RECEIPT_PATH)
    components = {
        relative: _git(root, "rev-parse", f"{implementation}:{relative}").lower()
        for relative in CONTINUATION_COMPONENT_PATHS
    }
    payload = {
        "schema_version": 1,
        "authorization_id": "CRYPTO_P1_G2_OPERATIONAL_CONTINUATION_V1_AUTHORIZATION",
        "decision_id": args.decision_id,
        "authority": "CURRENT_USER_INSTRUCTION",
        "continuation_id": CONTINUATION_ID,
        "status": "RUN_AUTHORIZED_ONE_TIME_OPERATIONAL_CONTINUATION_12000_TO_20000",
        "run_authorized": True,
        "consumed": False,
        "implementation_source_sha": implementation,
        "runtime_id": args.runtime_id,
        "budget": {
            "imported_strict": IMPORTED_STRICT,
            "strict_evaluated_maximum": STRICT_CAP,
            "remaining_strict_maximum": STRICT_CAP - IMPORTED_STRICT,
            "raw_generation_attempts_maximum_total": RAW_ATTEMPT_CAP,
            "checkpoint_size": CHECKPOINT_SIZE,
            "automatic_further_increase": False,
            "terminal_if_exhausted": RAW_ATTEMPT_TERMINAL,
        },
        "active_program_families": list(ACTIVE_FAMILIES),
        "lane_seeds": list(LANE_SEEDS),
        "lane_targets": LANE_TARGETS,
        "optimizer_feedback": BLOCK_ROBUST_V2_AUTHORITY,
        "source_checkpoint_receipt_path": SOURCE_RECEIPT_PATH,
        "source_checkpoint_receipt_file_sha256": _file_sha(root / SOURCE_RECEIPT_PATH),
        "source_runtime_id": source["source_runtime_id"],
        "source_checkpoint": source["source_checkpoint"],
        "source_checkpoint_manifest_file_sha256": source["source_checkpoint_manifest_file_sha256"],
        "source_frozen_contract_sha256": source["source_frozen_contract_sha256"],
        "source_durable_strict": source["durable_strict"],
        "source_durable_generation_attempts": source["durable_generation_attempts"],
        "continuation_from_existing_valid_checkpoint": True,
        "source_strict": IMPORTED_STRICT,
        "source_generation_attempts": 479_114,
        "target_strict": STRICT_CAP,
        "raw_attempt_ceiling": RAW_ATTEMPT_CAP,
        "scientific_contract_changed": False,
        "adaptive_state_reset": False,
        "fresh_restart": False,
        "exact_state_migration_required": True,
        "old_runtime_immutable": True,
        "native_checkpoint_labels": [
            "checkpoint_006", "checkpoint_007", "checkpoint_008", "checkpoint_009"
        ],
        "frozen_inputs": {
            "ledger_rows": 50_000,
            "ledger_sha256": EXPECTED_LEDGER_SHA256,
            "matched_positive": 302,
            "target_basins": 23,
            "frozen_parents": 228,
            "parent_pool_sha256": EXPECTED_POOL_SHA256,
            "preauthorization_receipt_sha256": EXPECTED_PREAUTH_RECEIPT_SHA256,
        },
        "authority_identity": EXPECTED_AUTHORITY_IDENTITY,
        "market_input_identity": EXPECTED_MARKET_INPUT_IDENTITY,
        "pc2_executor_identity": EXPECTED_PC2_EXECUTOR_IDENTITY,
        "execution_component_blob_oids": components,
        "forbidden_reads": {
            "validation": 0, "oos": 0, "holdout": 0, "forward": 0,
            "promotion": 0, "sealed": 0,
        },
        "scientific_contract_unchanged": {
            "search_core": True,
            "economic_contract": True,
            "semantic_catalog": True,
            "dispatcher": True,
            "reward": True,
            "mapping": True,
            "cost": True,
            "evaluator": True,
        },
    }
    payload["authorization_sha256"] = authorization_content_sha(payload)
    engine._write_json(root / AUTHORIZATION_PATH, payload)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
