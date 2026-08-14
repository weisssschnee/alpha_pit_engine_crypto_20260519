from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
from pathlib import Path

from alphafactory_crypto.broad_search import search_engine_v1 as engine
from alphafactory_crypto.broad_search.temporal_development_expansion_v1 import (
    authorization_content_sha,
    file_sha256,
)
from alphafactory_crypto.broad_search.temporal_realization_v2 import (
    ACTIVE_PROGRAM_FAMILIES,
    AUDIT_PATH,
    AUTHORIZATION_PATH,
    AUTHORIZATION_SCOPE,
    AUTHORIZED_STATUS,
    CHECKPOINT_SIZE,
    COMPONENT_PATHS,
    DECISION_BOUNDARY,
    EVOLUTION_OPERATION_PROBABILITIES,
    EXECUTION_MODE,
    FIXED_ALLOCATION_PER_10000,
    LANE_SEEDS,
    STRICT_CAP,
)
from alphafactory_crypto.broad_search.temporal_successor_v1 import (
    verify_successor_market_inputs,
)
from alphafactory_crypto.broad_search.temporal_targeted_deepening_v1 import (
    build_frozen_target_parent_pool,
    load_diagnostic_baseline,
)


OFFLINE_PATH = "config/crypto_temporal_search_core_realization_v2_offline_verification.json"
PRIOR_AUTHORIZATION = "config/crypto_temporal_targeted_p1_p4_basin_deepening_v1_authorization.json"


def blob_oid(root: Path, source_sha: str, path: str) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", f"{source_sha}:{path}"], cwd=root, text=True
    ).strip().lower()


def workspace_identity(root: Path) -> dict[str, str]:
    normalized = str(root.resolve()).replace("\\", "/").casefold()
    return {
        "host": platform.node().strip().casefold(),
        "workspace_path_sha256": hashlib.sha256(normalized.encode("utf-8")).hexdigest().upper(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--diagnostic-baseline", type=Path, required=True)
    parser.add_argument("--runtime-id", required=True)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    if subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        cwd=root,
        text=True,
    ).strip():
        raise RuntimeError("tracked worktree must be clean before authorization")
    implementation_sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True
    ).strip().lower()
    branch = subprocess.check_output(
        ["git", "branch", "--show-current"], cwd=root, text=True
    ).strip()
    audit_path = root / AUDIT_PATH
    offline_path = root / OFFLINE_PATH
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    offline = json.loads(offline_path.read_text(encoding="utf-8"))
    if audit.get("status") != "PASS" or offline.get("status") != "PASS":
        raise RuntimeError("offline authority evidence is not PASS")
    baseline_path = args.diagnostic_baseline.resolve()
    baseline_receipt = {"diagnostic_baseline_path": str(baseline_path)}
    baseline = load_diagnostic_baseline(root, baseline_receipt)
    pool = build_frozen_target_parent_pool(root, baseline)
    if (
        baseline.get("source_strict_count") != 50_000
        or baseline.get("matched_positive_count") != 302
        or baseline.get("source_ledger_sha256")
        != "5171CD9655944CCED18D35CCB413C725E9542889260A135E8F95F4BE7B401B46"
        or pool.get("target_basin_count") != 23
        or pool.get("frozen_parent_candidate_count") != 228
        or pool.get("target_parent_pool_sha256")
        != "A08112ED1765A432D15D259A70F308C2DE5BA7B617D294BFB8349020EC61AA49"
    ):
        raise RuntimeError("frozen development identity changed")
    prior = json.loads((root / PRIOR_AUTHORIZATION).read_text(encoding="utf-8-sig"))
    authority_identity = dict(prior["authority_identity"])
    role_bindings = {
        role: dict(value)
        for role, value in dict(prior["receipt_bound_role_bindings"]).items()
    }
    payload = {
        "schema_version": 1,
        "authorization_id": "CRYPTO_TEMPORAL_SEARCH_CORE_REALIZATION_V2_CANARY_AUTHORIZATION",
        "execution_mode": EXECUTION_MODE,
        "status": AUTHORIZED_STATUS,
        "run_authorized": True,
        "consumed": False,
        "expected_branch": branch,
        "authorized_implementation_sha": implementation_sha,
        "execution_component_git_identities": {
            path: blob_oid(root, implementation_sha, path) for path in COMPONENT_PATHS
        },
        "runtime_id": args.runtime_id,
        "executor_identity": workspace_identity(root),
        "market_input_preflight": verify_successor_market_inputs(root),
        "operator_audit_path": AUDIT_PATH,
        "operator_audit_sha256": file_sha256(audit_path),
        "offline_verification_path": OFFLINE_PATH,
        "offline_verification_sha256": file_sha256(offline_path),
        "diagnostic_baseline_path": str(baseline_path),
        "diagnostic_baseline_sha256": file_sha256(baseline_path),
        "frozen_parent_pool_identity": {
            "target_basin_count": 23,
            "frozen_parent_candidate_count": 228,
            "target_parent_pool_sha256": pool["target_parent_pool_sha256"],
        },
        "lane_seeds": list(LANE_SEEDS),
        "active_program_families": list(ACTIVE_PROGRAM_FAMILIES),
        "paused_program_families": [
            "P2_RECENT_CROWDING_EVENT_TO_RESPONSE",
            "P3_FLOW_SHOCK_PERSISTENCE_TO_ABSORPTION",
        ],
        "allocation_per_10000": dict(FIXED_ALLOCATION_PER_10000),
        "evolution_operation_probabilities": dict(EVOLUTION_OPERATION_PROBABILITIES),
        "budget": {
            "strict_evaluated_maximum": STRICT_CAP,
            "raw_generation_attempts_maximum": 100_000,
            "wall_time_seconds_maximum": 36_000,
            "checkpoint_size": CHECKPOINT_SIZE,
            "checkpoint_boundary": DECISION_BOUNDARY,
            "workers_default": 10,
            "workers_memory_fallback": 8,
        },
        "r3_first_10000_gate_baseline": {
            "crossover_requested": 1_260,
            "crossover_realized": 572,
            "evolution_strict": 6_000,
            "evolution_matched_positive": 1_220,
        },
        "boundaries": {
            "train_only": True,
            "validation": False,
            "oos": False,
            "holdout": False,
            "forward": False,
            "promotion": False,
            "automatic_expansion": False,
            "mapping_change": False,
            "cost_change": False,
            "evaluator_change": False,
            "reward_change": False,
            "target_change": False,
            "grammar_change": False,
            "sealed_reads": 0,
        },
        "authority_identity": authority_identity,
        "receipt_bound_role_bindings": role_bindings,
        "run_authorization": {
            "authority": "CURRENT_USER_INSTRUCTION",
            "decision_id": "AUTHORIZE_TEMPORAL_SEARCH_CORE_REALIZATION_V2_20260814",
            "scope": AUTHORIZATION_SCOPE,
        },
        "evidence_to_add": "P1/P4 train-only evidence for constructive crossover, basin-local realization archive, and dimension-aware mutation",
        "decision_to_change": "Whether Search Core Realization V2 improves economically viable within-basin realization production without quality collapse",
        "premarket_counters": {
            "market_arrays_read": 0,
            "candidate_evaluations": 0,
            "validation_reads": 0,
            "oos_reads": 0,
            "sealed_reads": 0,
        },
        "automatic_next_run_started": False,
    }
    payload["authorization_sha256"] = authorization_content_sha(payload)
    engine._write_json(root / AUTHORIZATION_PATH, payload)
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    main()
