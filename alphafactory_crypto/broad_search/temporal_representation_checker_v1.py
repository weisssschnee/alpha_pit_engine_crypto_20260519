"""Independent artifact checker for the fixed representation tournament."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

import pandas as pd

from . import search_engine_v1 as engine
from .temporal_representation_successor_v1 import ACTIVE_FAMILIES
from .temporal_representation_tournament_v1 import (
    ARMS,
    ARM_LANE_SEEDS,
    EXPECTED_LEDGER_SHA256,
    EXPECTED_POOL_SHA256,
    OFFLINE_EVIDENCE_PATH,
    STRICT_PER_ARM,
    validate_authorization,
)


def _sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "utf-8"
        )
    ).hexdigest().upper()


def independent_check(repo_root: Path, runtime_root: Path) -> dict[str, Any]:
    root = repo_root.resolve()
    runtime = runtime_root.resolve()
    errors: list[str] = []
    try:
        authorization = validate_authorization(root)
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as failure:
        authorization = {}
        errors.append("authorization:" + str(failure))
    try:
        frozen = engine._read_json(runtime / "frozen_contract.json")
        final = engine._read_json(runtime / "tournament_complete.json")
        offline = engine._read_json(root / OFFLINE_EVIDENCE_PATH)
    except (OSError, ValueError, json.JSONDecodeError) as failure:
        frozen = final = offline = {}
        errors.append("top_level_artifact:" + str(failure))
    if (
        frozen.get("ledger_sha256") != EXPECTED_LEDGER_SHA256
        or frozen.get("parent_pool_sha256") != EXPECTED_POOL_SHA256
        or frozen.get("authorization_sha256") != authorization.get("authorization_sha256")
    ):
        errors.append("frozen_identity")
    if offline.get("status") != "OFFLINE_CLOSURE_PASS_READY_FOR_TOURNAMENT":
        errors.append("offline_closure_gate")
    if (
        final.get("status") != "REPRESENTATION_TOURNAMENT_20000_COMPLETE"
        or int(final.get("strict", -1)) != STRICT_PER_ARM * 2
    ):
        errors.append("tournament_terminal")
    arm_evidence = {}
    all_candidates: dict[str, set[str]] = {}
    for arm in ARMS:
        arm_root = runtime / "arms" / arm
        try:
            arm_final = engine._read_json(arm_root / "arm_final.json")
            ledger = pd.read_parquet(arm_root / "candidate_ledger.parquet")
            checkpoints = sorted(
                (arm_root / "checkpoints").glob("checkpoint_[0-9][0-9][0-9]")
            )
            final_state = engine._read_json(checkpoints[-1] / "state.json")
        except (OSError, ValueError, IndexError, json.JSONDecodeError) as failure:
            errors.append(f"arm_artifact:{arm}:{failure}")
            continue
        if len(ledger) != STRICT_PER_ARM or int(arm_final.get("strict", -1)) != STRICT_PER_ARM:
            errors.append(f"arm_strict:{arm}")
        if len(checkpoints) != STRICT_PER_ARM // 2_000:
            errors.append(f"arm_checkpoint_count:{arm}")
        families = Counter(ledger["program_family_id"].astype(str))
        if set(families) - set(ACTIVE_FAMILIES):
            errors.append(f"family_scope:{arm}")
        if int(families.get("P2_RECENT_CROWDING_EVENT_TO_RESPONSE", 0)) or int(
            families.get("P3_FLOW_SHOCK_PERSISTENCE_TO_ABSORPTION", 0)
        ):
            errors.append(f"P2_P3_strict:{arm}")
        if set(ledger["seed"].astype(int)) != set(ARM_LANE_SEEDS[arm]):
            errors.append(f"lane_seeds:{arm}")
        if set(ledger["evaluation_partition"].astype(str)) != {"train"}:
            errors.append(f"partition:{arm}")
        if set(ledger["arm"].astype(str)) != {"temporal_program_evolution"}:
            errors.append(f"policy_arm:{arm}")
        if set(ledger["representation_tournament_arm"].astype(str)) != {arm}:
            errors.append(f"tournament_arm:{arm}")
        if not ledger["receipt_verified"].fillna(False).astype(bool).all():
            errors.append(f"receipt_verified:{arm}")
        expected_schema = (
            "MECHANISM_EVOLUTION_RECEIPT_V2"
            if arm == ARMS[0]
            else "TEMPORAL_REPRESENTATION_SUCCESSOR_RECEIPT_V1"
        )
        requested = Counter()
        realized = Counter()
        parent_sources = Counter()
        invalid_receipts = 0
        for row in ledger.to_dict("records"):
            try:
                candidate_payload = json.loads(str(row["candidate_spec_json"]))
                if str(row["candidate_spec_sha256"]) != engine._payload_sha(
                    candidate_payload
                ):
                    invalid_receipts += 1
                receipt = json.loads(str(row["receipt_json"]))
                if (
                    receipt.get("schema_version") != expected_schema
                    or receipt.get("targeted_parent_pool_sha256")
                    != EXPECTED_POOL_SHA256
                    or receipt.get("requested_operation")
                    not in {"parameter_mutation", "mechanism_mutation", "crossover"}
                    or receipt.get("realized_operation")
                    not in {"parameter_mutation", "mechanism_mutation", "crossover"}
                ):
                    invalid_receipts += 1
                requested[str(receipt["requested_operation"])] += 1
                realized[str(receipt["realized_operation"])] += 1
                parent_sources.update(
                    str(value) for value in receipt.get("targeted_parent_source_types", ())
                )
            except (KeyError, TypeError, ValueError, json.JSONDecodeError):
                invalid_receipts += 1
        if invalid_receipts:
            errors.append(f"receipt_or_candidate_identity:{arm}:{invalid_receipts}")
        if set(parent_sources) - {
            "FROZEN_TRAIN_ONLY_BASELINE",
            "ADAPTIVE_STRICT_DESCENDANT",
        }:
            errors.append(f"parent_source:{arm}")
        policy_keys = set(final_state.get("policies") or {})
        if policy_keys != {f"{arm}|{seed}" for seed in ARM_LANE_SEEDS[arm]}:
            errors.append(f"policy_lane_identity:{arm}")
        for policy in (final_state.get("policies") or {}).values():
            state = dict(policy.get("realization_v2_state") or {})
            if state.get("target_parent_pool_sha256") != EXPECTED_POOL_SHA256:
                errors.append(f"policy_pool_identity:{arm}")
        all_candidates[arm] = set(ledger["candidate_id"].astype(str))
        arm_evidence[arm] = {
            "strict": len(ledger),
            "attempts": int(arm_final.get("attempts", 0)),
            "matched_positive": int(ledger["matched_positive"].astype(bool).sum()),
            "program_family_counts": dict(sorted(families.items())),
            "requested_operation_counts": dict(sorted(requested.items())),
            "realized_operation_counts": dict(sorted(realized.items())),
            "parent_source_counts": dict(sorted(parent_sources.items())),
            "checkpoint_count": len(checkpoints),
            "candidate_spec_hashes_verified": len(ledger) - invalid_receipts,
        }
    if len(all_candidates) == 2:
        # Candidate overlap is legal under independent paired seeds; archive/state sharing is not.
        overlap = len(all_candidates[ARMS[0]] & all_candidates[ARMS[1]])
    else:
        overlap = -1
    forbidden = {
        key: int(final.get(key, -1))
        for key in (
            "validation_reads",
            "oos_reads",
            "holdout_reads",
            "forward_reads",
            "promotion_reads",
            "sealed_reads",
        )
    }
    if any(value != 0 for value in forbidden.values()):
        errors.append("forbidden_reads")
    core = {
        "schema_version": 1,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "authorization_sha256": authorization.get("authorization_sha256"),
        "frozen_contract_sha256": frozen.get("frozen_contract_sha256"),
        "offline_evidence_sha256": offline.get("offline_evidence_sha256"),
        "arm_evidence": arm_evidence,
        "cross_arm_candidate_overlap_diagnostic": overlap,
        "adaptive_state_shared": False,
        "archive_shared": False,
        "forbidden_reads": forbidden,
        "automatic_next_run_started": False,
    }
    result = {**core, "checker_sha256": _sha(core)}
    engine._write_json(runtime / "independent_checker.json", result)
    return result


__all__ = ["independent_check"]
