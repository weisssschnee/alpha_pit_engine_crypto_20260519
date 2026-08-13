from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import pandas as pd

from alphafactory_crypto.broad_search import search_engine_v1 as engine
from alphafactory_crypto.broad_search.temporal_targeted_deepening_v1 import (
    ACTIVE_PROGRAM_FAMILIES,
    AUTHORIZATION_PATH,
    AUTHORIZATION_SCOPE,
    AUTHORIZED_STATUS,
    CHECKPOINT_SIZE,
    COMPONENT_PATHS,
    EVOLUTION_OPERATION_PROBABILITIES,
    EXECUTION_MODE,
    FIXED_ALLOCATION_PER_10000,
    LANE_SEEDS,
    RAW_ATTEMPT_CAP,
    SATURATION_BOUNDARY,
    STRICT_CAP,
    WALL_SECONDS_CAP,
    authorization_content_sha,
    build_diagnostic_baseline,
    committed_file_sha,
    file_sha256,
)


PRIOR_AUTHORIZATION = (
    "config/crypto_temporal_large_development_expansion_v1_authorization.json"
)
BASELINE_LEDGER_PATH = (
    "runtime/crypto_temporal_large_development_expansion_v1_20260812r1/"
    "candidate_ledger.parquet"
)
BASELINE_LEDGER_SHA256 = (
    "5171CD9655944CCED18D35CCB413C725E9542889260A135E8F95F4BE7B401B46"
)
BASELINE_OUTPUT_PATH = (
    "config/crypto_temporal_targeted_p1_p4_basin_deepening_v1_baseline.json"
)


def _workspace_identity(host: str, workspace: str) -> dict[str, str]:
    normalized = workspace.replace("\\", "/").casefold()
    return {
        "host": host.strip().casefold(),
        "workspace_path_sha256": hashlib.sha256(
            normalized.encode("utf-8")
        ).hexdigest().upper(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--executor-host", required=True)
    parser.add_argument("--executor-workspace", required=True)
    parser.add_argument("--runtime-id", required=True)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    branch = subprocess.check_output(
        ["git", "branch", "--show-current"], cwd=repo_root, text=True
    ).strip()
    head = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=repo_root, text=True
    ).strip().lower()
    if subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        cwd=repo_root,
        text=True,
    ).strip():
        raise RuntimeError("tracked worktree must be clean before authorization")

    source = repo_root / BASELINE_LEDGER_PATH
    if not source.is_file() or file_sha256(source) != BASELINE_LEDGER_SHA256:
        raise RuntimeError("verified 50k development baseline ledger changed")
    ledger = pd.read_parquet(source)
    matched_rows = ledger.loc[ledger["matched_positive"].fillna(False).astype(bool)]
    baseline = build_diagnostic_baseline(
        matched_rows.to_dict("records"),
        source_ledger_path=BASELINE_LEDGER_PATH,
        source_ledger_sha256=BASELINE_LEDGER_SHA256,
        source_strict_count=len(ledger),
    )
    if len(ledger) != 50_000 or int(baseline["matched_positive_count"]) != 302:
        raise RuntimeError("verified 50k development baseline shape changed")
    baseline_output = repo_root / BASELINE_OUTPUT_PATH
    engine._write_json(baseline_output, baseline)

    prior = json.loads(
        (repo_root / PRIOR_AUTHORIZATION).read_text(encoding="utf-8-sig")
    )
    authority_identity = dict(prior["authority_identity"])
    role_bindings = {
        role: dict(value)
        for role, value in dict(prior["receipt_bound_role_bindings"]).items()
    }
    payload = {
        "schema_version": 2,
        "authorization_id": (
            "CRYPTO_TEMPORAL_TARGETED_P1_P4_BASIN_DEEPENING_V1_AUTHORIZATION"
        ),
        "execution_mode": EXECUTION_MODE,
        "status": AUTHORIZED_STATUS,
        "run_authorized": True,
        "consumed": False,
        "expected_branch": branch,
        "authorized_implementation_sha": head,
        "authorized_component_sha256": {
            path: committed_file_sha(repo_root, path) for path in COMPONENT_PATHS
        },
        "runtime_id": args.runtime_id,
        "executor_identity": _workspace_identity(
            args.executor_host, args.executor_workspace
        ),
        "lane_seeds": list(LANE_SEEDS),
        "active_program_families": list(ACTIVE_PROGRAM_FAMILIES),
        "paused_program_families": [
            "P2_RECENT_CROWDING_EVENT_TO_RESPONSE",
            "P3_FLOW_SHOCK_PERSISTENCE_TO_ABSORPTION",
        ],
        "allocation_per_10000": dict(FIXED_ALLOCATION_PER_10000),
        "evolution_operation_probabilities": dict(
            EVOLUTION_OPERATION_PROBABILITIES
        ),
        "budget": {
            "strict_evaluated_maximum": STRICT_CAP,
            "raw_generation_attempts_maximum": RAW_ATTEMPT_CAP,
            "wall_time_seconds_maximum": WALL_SECONDS_CAP,
            "checkpoint_size": CHECKPOINT_SIZE,
            "workers_default": 10,
            "workers_memory_fallback": 8,
        },
        "saturation_rule": {
            "strict_boundary": SATURATION_BOUNDARY,
            "new_economic_clusters_since_10000_maximum": 0,
            "new_high_quality_deepened_basins_since_10000_maximum": 0,
            "new_high_quality_concrete_realizations_since_10000_maximum": 0,
            "realization_depth_increase_since_10000_maximum": 0,
        },
        "boundaries": {
            "train_only": True,
            "validation": False,
            "oos": False,
            "holdout": False,
            "forward": False,
            "promotion": False,
            "automatic_expansion": False,
            "family_concentration_can_stop": False,
            "sealed_reads": 0,
        },
        "diagnostic_baseline_path": BASELINE_OUTPUT_PATH,
        "diagnostic_baseline_sha256": file_sha256(baseline_output),
        "diagnostic_baseline_policy_feedback": False,
        "authority_identity": authority_identity,
        "receipt_bound_role_bindings": role_bindings,
        "run_authorization": {
            "authority": "CURRENT_USER_INSTRUCTION",
            "decision_id": "AUTHORIZE_TARGETED_P1_P4_BASIN_DEEPENING_20260813",
            "scope": AUTHORIZATION_SCOPE,
        },
        "evidence_to_add": (
            "P1/P4 train-only evidence separating behavior family, economic "
            "similarity cluster, program basin, and concrete realization depth"
        ),
        "decision_to_change": (
            "Whether targeted deepening is sufficient to wait for forward, should "
            "continue, or exposes a Search Core realization bottleneck"
        ),
        "automatic_next_run_started": False,
    }
    payload["authorization_sha256"] = authorization_content_sha(payload)
    engine._write_json(repo_root / AUTHORIZATION_PATH, payload)
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    main()
