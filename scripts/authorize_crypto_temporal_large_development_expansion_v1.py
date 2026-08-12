from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import pandas as pd

from alphafactory_crypto.broad_search import search_engine_v1 as engine
from alphafactory_crypto.broad_search.temporal_development_expansion_v1 import (
    ALL_PROGRAM_FAMILIES,
    AUTHORIZATION_PATH,
    AUTHORIZATION_SCOPE,
    AUTHORIZED_STATUS,
    CHECKPOINT_SIZE,
    COMPONENT_PATHS,
    EXECUTION_MODE,
    FIXED_ALLOCATION_PER_10000,
    LANE_SEEDS,
    RAW_ATTEMPT_CAP,
    STRICT_CAP,
    WALL_SECONDS_CAP,
    authorization_content_sha,
    committed_file_sha,
    file_sha256,
)


PRIOR_SUCCESSOR_AUTHORIZATION = (
    "config/crypto_temporal_program_30k_to_50k_successor_v1_authorization.json"
)
BASELINE_LEDGER_PATH = (
    "runtime/crypto_temporal_program_30k_to_50k_successor_v1_20260811r2/"
    "candidate_ledger.parquet"
)


def _workspace_identity(host: str, workspace: str) -> dict[str, str]:
    normalized = workspace.replace("\\", "/").casefold()
    return {
        "host": host.strip().casefold(),
        "workspace_path_sha256": hashlib.sha256(
            normalized.encode("utf-8")
        ).hexdigest().upper(),
    }


def _freeze_baseline(source: Path, output: Path) -> dict[str, object]:
    ledger = pd.read_parquet(source)
    required = {
        "behavior_family_id",
        "program_id",
        "left_incremental_net_mean",
        "right_incremental_net_mean",
    }
    if len(ledger) != 50_000 or not required.issubset(ledger.columns):
        raise RuntimeError("prior development baseline ledger is not the verified 50k shape")
    dual = ledger.loc[
        (pd.to_numeric(ledger["left_incremental_net_mean"], errors="coerce") > 0.0)
        & (pd.to_numeric(ledger["right_incremental_net_mean"], errors="coerce") > 0.0)
    ]
    payload = {
        "schema_version": 1,
        "status": "DIAGNOSTIC_BASELINE_ONLY_NO_POLICY_FEEDBACK",
        "source_ledger_sha256": file_sha256(source),
        "source_strict_count": int(len(ledger)),
        "economic_behavior_family_ids": sorted(
            {str(value) for value in dual["behavior_family_id"]}
        ),
        "positive_program_ids": sorted({str(value) for value in dual["program_id"]}),
        "validation_rows": 0,
        "oos_rows": 0,
        "sealed_reads": 0,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    engine._write_json(output, payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--baseline-ledger", type=Path, required=True)
    parser.add_argument("--baseline-output", type=Path, required=True)
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

    baseline_output = args.baseline_output
    if not baseline_output.is_absolute():
        baseline_output = repo_root / baseline_output
    expected_baseline = (repo_root / BASELINE_LEDGER_PATH).resolve()
    if args.baseline_ledger.resolve() != expected_baseline:
        raise RuntimeError("diagnostic baseline must be the verified 50k development ledger")
    _freeze_baseline(expected_baseline, baseline_output.resolve())
    baseline_relative = baseline_output.resolve().relative_to(repo_root).as_posix()

    prior = json.loads(
        (repo_root / PRIOR_SUCCESSOR_AUTHORIZATION).read_text(encoding="utf-8")
    )
    authority_identity = dict(prior["authority_identity"])
    role_bindings = {
        role: dict(value)
        for role, value in dict(prior["receipt_bound_role_bindings"]).items()
    }
    payload = {
        "schema_version": 2,
        "authorization_id": "CRYPTO_TEMPORAL_LARGE_DEVELOPMENT_EXPANSION_V1_AUTHORIZATION",
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
        "active_program_families": list(ALL_PROGRAM_FAMILIES),
        "allocation_per_10000": dict(FIXED_ALLOCATION_PER_10000),
        "budget": {
            "strict_evaluated_maximum": STRICT_CAP,
            "raw_generation_attempts_maximum": RAW_ATTEMPT_CAP,
            "wall_time_seconds_maximum": WALL_SECONDS_CAP,
            "checkpoint_size": CHECKPOINT_SIZE,
            "workers_default": 10,
            "workers_memory_fallback": 8,
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
        "diagnostic_baseline_path": baseline_relative,
        "diagnostic_baseline_sha256": file_sha256(baseline_output),
        "diagnostic_baseline_policy_feedback": False,
        "authority_identity": authority_identity,
        "receipt_bound_role_bindings": role_bindings,
        "run_authorization": {
            "authority": "CURRENT_USER_INSTRUCTION",
            "decision_id": "AUTHORIZE_LARGE_TEMPORAL_DEVELOPMENT_DISCOVERY_20260812",
            "scope": AUTHORIZATION_SCOPE,
        },
        "evidence_to_add": (
            "Independent 50k train-only Temporal Program economic cluster discovery "
            "under fixed Random/CEM/Evolution 20/20/60 allocation"
        ),
        "decision_to_change": (
            "Whether development discovery should continue, enter saturation review, "
            "or require Search Core review"
        ),
        "automatic_next_run_started": False,
    }
    payload["authorization_sha256"] = authorization_content_sha(payload)
    output = repo_root / AUTHORIZATION_PATH
    engine._write_json(output, payload)
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    main()
