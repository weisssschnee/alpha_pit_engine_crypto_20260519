"""Independent artifact checker for Proposal Dispatcher V1."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd

from . import search_engine_v1 as engine
from .temporal_proposal_dispatch_search_v1 import (
    AUTHORIZATION_PATH,
    LANE_SEEDS,
    REQUIRED_EXECUTION_COMPONENT_PATHS,
    STRICT_CAP,
    _git,
    authorization_content_sha,
)
from .temporal_representation_successor_v1 import ACTIVE_FAMILIES
from .temporal_representation_tournament_v1 import EXPECTED_LEDGER_SHA256, EXPECTED_POOL_SHA256


def _sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest().upper()


def _dispatched_rejection_count(rejected: pd.DataFrame) -> int:
    """Count proposals selected by the dispatcher but rejected before strict evaluation."""
    if rejected.empty or "status" not in rejected:
        return 0
    return int(
        rejected["status"]
        .astype(str)
        .isin({"EXACT_OR_REPLAY_REJECT", "PAIR_REJECTED"})
        .sum()
    )


def _validate_runtime_authorization(root: Path, runtime: Path) -> dict[str, Any]:
    authorization = engine._read_json(runtime / "authorization_snapshot.json")
    claim = engine._read_json(runtime / "launch_claim.json")
    source_sha = str(claim.get("source_sha") or "").lower()
    implementation_sha = str(authorization.get("implementation_source_sha") or "").lower()
    if (
        authorization.get("status") != "RUN_AUTHORIZED_ONE_TIME_PROPOSAL_DISPATCH_20000"
        or authorization_content_sha(authorization)
        != authorization.get("authorization_sha256")
        or _git(root, "rev-parse", f"{source_sha}^").lower() != implementation_sha
        or set(
            _git(root, "diff-tree", "--no-commit-id", "--name-only", "-r", source_sha).splitlines()
        )
        != {AUTHORIZATION_PATH}
    ):
        raise RuntimeError("runtime_authorization_identity")
    committed_authorization = json.loads(_git(root, "show", f"{source_sha}:{AUTHORIZATION_PATH}"))
    if committed_authorization != authorization:
        raise RuntimeError("runtime_authorization_snapshot")
    components = dict(authorization.get("execution_component_blob_oids") or {})
    if set(components) != set(REQUIRED_EXECUTION_COMPONENT_PATHS):
        raise RuntimeError("runtime_execution_component_set")
    for relative, expected in components.items():
        if _git(root, "rev-parse", f"{implementation_sha}:{relative}").lower() != str(expected).lower():
            raise RuntimeError("runtime_execution_component_identity:" + relative)
    return authorization


def independent_check(repo_root: Path, runtime_root: Path) -> dict[str, Any]:
    root, runtime = repo_root.resolve(), runtime_root.resolve()
    errors: list[str] = []
    try:
        authorization = _validate_runtime_authorization(root, runtime)
        frozen = engine._read_json(runtime / "frozen_contract.json")
        final = engine._read_json(runtime / "run_complete.json")
        dispatch = engine._read_json(runtime / "dispatcher_diagnostics_final.json")
        ledger = pd.read_parquet(runtime / "candidate_ledger.parquet")
        checkpoints = sorted((runtime / "checkpoints").glob("checkpoint_[0-9][0-9][0-9]"))
        final_state = engine._read_json(checkpoints[-1] / "state.json")
        rejected = pd.read_parquet(checkpoints[-1] / "rejected_candidate_ledger.parquet")
    except (OSError, ValueError, RuntimeError, IndexError, json.JSONDecodeError) as failure:
        authorization = frozen = final = dispatch = final_state = {}
        ledger, rejected, checkpoints = pd.DataFrame(), pd.DataFrame(), []
        errors.append("artifact_or_authorization:" + str(failure))
    if (
        frozen.get("ledger_sha256") != EXPECTED_LEDGER_SHA256
        or frozen.get("parent_pool_sha256") != EXPECTED_POOL_SHA256
        or frozen.get("authorization_sha256") != authorization.get("authorization_sha256")
        or frozen.get("historical_prior_sha256") != authorization.get("historical_prior_sha256")
    ):
        errors.append("frozen_identity")
    if final.get("status") != "PROPOSAL_DISPATCH_SUCCESSOR_20000_COMPLETE" or len(ledger) != STRICT_CAP:
        errors.append("terminal_or_strict")
    if len(checkpoints) != STRICT_CAP // 2_000:
        errors.append("checkpoint_count")
    families = Counter(ledger.get("program_family_id", pd.Series(dtype=str)).astype(str))
    if set(families) - set(ACTIVE_FAMILIES):
        errors.append("family_scope")
    if int(families.get("P2_RECENT_CROWDING_EVENT_TO_RESPONSE", 0)) or int(
        families.get("P3_FLOW_SHOCK_PERSISTENCE_TO_ABSORPTION", 0)
    ):
        errors.append("P2_P3_strict")
    if not ledger.empty:
        if set(ledger["evaluation_partition"].astype(str)) != {"train"}:
            errors.append("partition")
        if set(ledger["seed"].astype(int)) != set(LANE_SEEDS):
            errors.append("lane_seeds")
        if not ledger["receipt_verified"].fillna(False).astype(bool).all():
            errors.append("receipt_verified")
        invalid = 0
        for row in ledger.to_dict("records"):
            try:
                candidate = json.loads(str(row["candidate_spec_json"]))
                receipt = json.loads(str(row["dispatch_receipt_json"]))
                core = {key: value for key, value in receipt.items() if key != "dispatch_receipt_sha256"}
                if (
                    str(row["candidate_spec_sha256"]) != engine._payload_sha(candidate)
                    or receipt.get("dispatch_receipt_sha256") != _sha(core)
                    or row.get("dispatch_receipt_sha256") != receipt.get("dispatch_receipt_sha256")
                    or receipt.get("dispatcher_id") != "TEMPORAL_PROPOSAL_DISPATCHER_V1"
                    or int(receipt.get("legal_candidates_scored", 0)) < 1
                    or int(receipt.get("selected_rank", 0)) < 1
                    or int(receipt.get("selected_rank", 0)) > int(receipt.get("legal_candidates_scored", 0))
                ):
                    invalid += 1
            except (KeyError, TypeError, ValueError, json.JSONDecodeError):
                invalid += 1
        if invalid:
            errors.append(f"candidate_or_dispatch_receipt:{invalid}")
    policy_keys = set(final_state.get("policies") or {})
    if policy_keys != {f"DISPATCH|{seed}" for seed in LANE_SEEDS}:
        errors.append("policy_lane_identity")
    for policy in (final_state.get("policies") or {}).values():
        realization = dict(policy.get("realization_v2_state") or {})
        dispatcher = dict(realization.get("proposal_dispatcher_v1") or {})
        if (
            realization.get("target_parent_pool_sha256") != EXPECTED_POOL_SHA256
            or dispatcher.get("historical_prior_sha256") != authorization.get("historical_prior_sha256")
        ):
            errors.append("policy_frozen_identity")
    counters = dict(dispatch.get("dispatch_counters") or {})
    dispatched_rejections = _dispatched_rejection_count(rejected)
    expected_dispatches = len(ledger) + dispatched_rejections
    if (
        int(counters.get("dispatches", -1)) != expected_dispatches
        or int(counters.get("exploration_selected", -1))
        + int(counters.get("exploitation_selected", -1))
        != expected_dispatches
    ):
        errors.append("dispatch_count")
    forbidden = {
        key: int(final.get(key, -1))
        for key in ("validation_reads", "oos_reads", "holdout_reads", "forward_reads", "promotion_reads", "sealed_reads")
    }
    if any(value != 0 for value in forbidden.values()):
        errors.append("forbidden_reads")
    core = {
        "schema_version": 1,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "strict": len(ledger),
        "attempts": int(final.get("attempts", 0)),
        "program_family_counts": dict(sorted(families.items())),
        "checkpoint_count": len(checkpoints),
        "dispatch_counters": counters,
        "dispatched_rejections": dispatched_rejections,
        "historical_prior_sha256": authorization.get("historical_prior_sha256"),
        "frozen_contract_sha256": frozen.get("frozen_contract_sha256"),
        "forbidden_reads": forbidden,
        "automatic_next_run_started": False,
    }
    result = {**core, "checker_sha256": _sha(core)}
    engine._write_json(runtime / "independent_checker.json", result)
    return result


__all__ = ["independent_check"]
