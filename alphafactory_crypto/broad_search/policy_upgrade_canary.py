"""Bounded current-field canary for real CEM and typed evolutionary upgrades.

This module is intentionally not a new search control plane.  It reuses the
frozen Broad compiler, adaptive evaluator, mapping, cost model, and raw cache.
It may qualify policy implementation and spent-development productivity only.
"""

from __future__ import annotations

import json
import math
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd
import psutil

from alphafactory_crypto.instrument_canary.release import sha256_file

from .compositional18m import CandidateSpec
from .expression import FieldContract, TypedExpressionRegistry
from .panel18m import RawPanelStore
from .runner18m import (
    ADAPTIVE_END,
    ADAPTIVE_START,
    POLICY_UPGRADE_CANARY_POLICIES,
    LanePolicy,
    _adaptive_surface_qualification,
    _compiler_binding,
    _contracts_from_payload,
    _contracts_payload,
    _current_field_surface_binding,
    _directory_bundle,
    _environment_fingerprint,
    _git_clean,
    _git_sha,
    _parallel_lanes,
    _payload_sha,
    _read_json,
    _write_json,
)


EPOCH_ID = "CRYPTO_CURRENT_FIELD_POLICY_UPGRADE_CANARY_V1"
CANARY_POLICIES = POLICY_UPGRADE_CANARY_POLICIES
CANARY_SEEDS = (20260716, 20260717, 20260718, 20260719)
PAIRS_PER_LANE = 128
RUNTIME_FILES = (
    "POLICY_UPGRADE_CANARY_CONTRACT.json",
    "POLICY_COMPILE_REPLAY.json",
    "POLICY_UPGRADE_PAIR_RESULTS.parquet",
    "POLICY_UPGRADE_BEHAVIOR_AUDIT.json",
    "POLICY_UPGRADE_DECISION.json",
    "POLICY_UPGRADE_RESOURCE_AUDIT.json",
)
MANIFEST_FILE = "manifest.json"


def validate_canary_config(config: Mapping[str, Any]) -> None:
    budget = config.get("budget", {})
    boundaries = config.get("boundaries", {})
    if config.get("epoch_id") != EPOCH_ID:
        raise ValueError("unexpected policy canary epoch")
    exact_budget = (
        tuple(budget.get("policies", ())) == CANARY_POLICIES
        and tuple(int(value) for value in budget.get("seeds", ())) == CANARY_SEEDS
        and int(budget.get("pairs_per_lane", -1)) == PAIRS_PER_LANE
        and int(budget.get("lane_count", -1)) == 20
        and int(budget.get("strict_pairs", -1)) == 2560
        and int(budget.get("report_only_pairs", -1)) == 0
        and int(budget.get("hard_cap_standalone_evaluations", -1)) == 5120
        and int(budget.get("hard_cap_incremental_sleeve_evaluations", -1)) == 2560
    )
    if not exact_budget:
        raise ValueError("frozen canary budget changed")
    required_false = (
        "sealed_reads_allowed",
        "report_only_reads_allowed",
        "formal_performance_search",
        "candidate_promotion",
        "cross_sprint_adaptive_memory",
        "challenge_open",
        "forward_open",
    )
    if any(boundaries.get(name) is not False for name in required_false):
        raise PermissionError("policy canary boundary opened")
    if boundaries.get("development_block_role") != "SPENT_DEVELOPMENT_ENGINEERING_CANARY":
        raise PermissionError("policy canary may use only the spent development block")
    if config.get("fresh_policy_state") is not True:
        raise PermissionError("policy canary requires fresh lane state")
    parent = config.get("parent_evidence", {})
    if any(
        parent.get(name) is not False
        for name in ("candidate_reuse", "policy_state_import", "report_only_reuse")
    ):
        raise PermissionError("policy canary cannot import prior adaptive state")
    parameters = config.get("policy_parameters", {})
    if set(parameters) != {"cem_distribution_v1", "evolutionary_typed_v1"}:
        raise ValueError("policy parameter surface changed")


def _synthetic_reward(seed: int, step: int, candidate_id: str) -> float:
    identity_term = int(candidate_id[:8], 16) / 0xFFFFFFFF
    return float(math.sin((seed % 997 + 1) * (step + 1)) * 0.01 + identity_term * 0.001)


def compile_replay_audit(
    registry: TypedExpressionRegistry, config: Mapping[str, Any]
) -> dict[str, Any]:
    policies = tuple(str(value) for value in config["budget"]["policies"])
    seeds = tuple(int(value) for value in config["budget"]["seeds"])
    steps = int(config["compile_replay"]["steps_per_lane"])
    parameters = config.get("policy_parameters", {})
    lane_rows: list[dict[str, Any]] = []
    candidate_replay = True
    state_replay = True
    receipts_verified = True
    receipt_count = 0
    cem_updates = 0
    for seed in seeds:
        for policy_name in policies:
            left = LanePolicy(
                policy_name,
                seed,
                registry,
                dict(parameters.get(policy_name, {})),
            )
            right = LanePolicy(
                policy_name,
                seed,
                registry,
                dict(parameters.get(policy_name, {})),
            )
            transcript: list[dict[str, Any]] = []
            for step in range(steps):
                left_candidate, left_metadata = left.propose()
                right_candidate, right_metadata = right.propose()
                registry.validate(left_candidate.expression)
                registry.validate(left_candidate.control)
                candidate_replay &= left_candidate.candidate_id == right_candidate.candidate_id
                state_replay &= (
                    left_metadata["policy_state_hash_before"]
                    == right_metadata["policy_state_hash_before"]
                    and left_metadata == right_metadata
                )
                receipt = left_metadata.get("mutation_receipt")
                if receipt is not None and policy_name == "evolutionary_typed_v1":
                    receipt_count += 1
                    receipts_verified &= left_metadata.get("mutation_receipt_verified") is True
                reward = _synthetic_reward(seed, step, left_candidate.candidate_id)
                left.update(left_candidate, reward)
                right.update(right_candidate, reward)
                after_left = left.state_hash()
                after_right = right.state_hash()
                state_replay &= after_left == after_right
                transcript.append(
                    {
                        "step": step,
                        "candidate_id": left_candidate.candidate_id,
                        "state_before": left_metadata["policy_state_hash_before"],
                        "state_after": after_left,
                        "receipt_sha256": receipt.get("receipt_sha256") if receipt else None,
                        "reward": reward,
                    }
                )
            if policy_name == "cem_distribution_v1":
                cem_updates += left.cem_update_count
            lane_rows.append(
                {
                    "policy": policy_name,
                    "seed": seed,
                    "steps": steps,
                    "final_state_hash": left.state_hash(),
                    "transcript_sha256": _payload_sha(transcript),
                    "cem_update_count": left.cem_update_count,
                    "typed_mutation_receipt_count": sum(
                        row["receipt_sha256"] is not None for row in transcript
                    ),
                }
            )
    passed = candidate_replay and state_replay and receipts_verified
    return {
        "schema_version": 1,
        "result": "PASS" if passed else "FAIL",
        "feedback": "DETERMINISTIC_SYNTHETIC_POLICY_ONLY",
        "steps_per_lane": steps,
        "lane_count": len(lane_rows),
        "all_candidate_ids_replayed": bool(candidate_replay),
        "all_state_hashes_replayed": bool(state_replay),
        "all_mutation_receipts_verified": bool(receipts_verified),
        "real_cem_update_count": int(cem_updates),
        "typed_mutation_receipt_count": int(receipt_count),
        "lanes": lane_rows,
        "claim_scope": "COMPILER_AND_POLICY_DETERMINISM_ONLY",
    }


def _candidate_raw_fields(row: Mapping[str, Any]) -> tuple[str, ...]:
    payload = json.loads(str(row["candidate_spec_json"]))
    return tuple(str(value) for value in payload.get("raw_fields", ()))


def _top_mean(values: Sequence[float], fraction: float) -> float:
    count = max(1, int(math.ceil(len(values) * fraction)))
    return float(np.mean(sorted(values, reverse=True)[:count]))


def _policy_upgrade_audit(
    rows: Sequence[Mapping[str, Any]], config: Mapping[str, Any]
) -> dict[str, Any]:
    policies = tuple(str(value) for value in config["budget"]["policies"])
    seeds = tuple(int(value) for value in config["budget"]["seeds"])
    expected_count = int(config["budget"]["pairs_per_lane"])
    qualification = config["qualification"]
    top_fraction = float(qualification["top_fraction"])
    summaries: list[dict[str, Any]] = []
    errors: list[str] = []
    by_lane: dict[tuple[str, int], list[Mapping[str, Any]]] = {}
    for policy_name in policies:
        for seed in seeds:
            lane = sorted(
                (
                    row
                    for row in rows
                    if str(row["policy"]) == policy_name and int(row["seed"]) == seed
                ),
                key=lambda row: int(row["proposal_step"]),
            )
            by_lane[(policy_name, seed)] = lane
            lane_errors: list[str] = []
            if len(lane) != expected_count:
                lane_errors.append("PAIR_COUNT")
            if [int(row["proposal_step"]) for row in lane] != list(range(expected_count)):
                lane_errors.append("PROPOSAL_STEPS")
            if any(str(row["pair_evaluation_status"]) != "PASS" for row in lane):
                lane_errors.append("EVALUATOR_FAILURE")
            candidate_ids = [str(row["candidate_id"]) for row in lane]
            unique_rate = len(set(candidate_ids)) / max(1, len(candidate_ids))
            skeletons = {str(row["skeleton_id"]) for row in lane}
            families = {str(row["mechanism_family"]) for row in lane}
            fields = {
                field_id for row in lane for field_id in _candidate_raw_fields(row)
            }
            if unique_rate < float(qualification["minimum_unique_rate"]):
                lane_errors.append("UNIQUE_RATE")
            if len(skeletons) < int(qualification["minimum_skeleton_coverage"]):
                lane_errors.append("SKELETON_COVERAGE")
            if len(families) < int(qualification["minimum_family_coverage"]):
                lane_errors.append("FAMILY_COVERAGE")
            if len(fields) < int(qualification["minimum_field_coverage"]):
                lane_errors.append("FIELD_COVERAGE")
            verified_mutations = sum(
                row.get("mutation_receipt_verified") is not None
                and not pd.isna(row.get("mutation_receipt_verified"))
                and bool(row.get("mutation_receipt_verified"))
                for row in lane
            )
            cem_updates = max(
                (
                    int(json.loads(str(row["policy_diagnostics_json"])).get("cem_update_count", 0))
                    for row in lane
                ),
                default=0,
            )
            if (
                policy_name == "cem_distribution_v1"
                and cem_updates < int(qualification["minimum_cem_updates_per_lane"])
            ):
                lane_errors.append("CEM_DISTRIBUTION_UPDATES")
            if (
                policy_name == "evolutionary_typed_v1"
                and verified_mutations
                < int(qualification["minimum_verified_mutations_per_lane"])
            ):
                lane_errors.append("TYPED_MUTATION_RECEIPTS")
            rewards = [float(row["pair_reward"]) for row in lane]
            summaries.append(
                {
                    "policy": policy_name,
                    "seed": seed,
                    "pair_count": len(lane),
                    "pass_count": sum(
                        str(row["pair_evaluation_status"]) == "PASS" for row in lane
                    ),
                    "unique_rate": unique_rate,
                    "skeleton_coverage": len(skeletons),
                    "family_coverage": len(families),
                    "field_coverage": len(fields),
                    "mean_pair_reward": float(np.mean(rewards)) if rewards else None,
                    "top_fraction": top_fraction,
                    "top_mean_pair_reward": _top_mean(rewards, top_fraction)
                    if rewards
                    else None,
                    "cem_update_count": cem_updates,
                    "verified_mutation_receipts": verified_mutations,
                    "implementation_errors": lane_errors,
                }
            )
            errors.extend(f"{policy_name}:{seed}:{value}" for value in lane_errors)

    summary_index = {
        (str(row["policy"]), int(row["seed"])): row for row in summaries
    }
    reference = str(qualification["reference_policy"])
    comparisons: dict[str, list[dict[str, Any]]] = {}
    decisions: dict[str, dict[str, Any]] = {}
    for real_policy, lite_policy in qualification["comparisons"].items():
        seed_rows: list[dict[str, Any]] = []
        for seed in seeds:
            real = summary_index[(str(real_policy), seed)]
            random_control = summary_index[(reference, seed)]
            lite = summary_index[(str(lite_policy), seed)]
            mean_vs_random = float(real["mean_pair_reward"] - random_control["mean_pair_reward"])
            top_vs_random = float(
                real["top_mean_pair_reward"] - random_control["top_mean_pair_reward"]
            )
            mean_vs_lite = float(real["mean_pair_reward"] - lite["mean_pair_reward"])
            top_vs_lite = float(
                real["top_mean_pair_reward"] - lite["top_mean_pair_reward"]
            )
            jointly_positive = all(
                value > 0.0
                for value in (
                    mean_vs_random,
                    top_vs_random,
                    mean_vs_lite,
                    top_vs_lite,
                )
            )
            seed_rows.append(
                {
                    "seed": seed,
                    "mean_margin_vs_random": mean_vs_random,
                    "top_mean_margin_vs_random": top_vs_random,
                    "mean_margin_vs_lite": mean_vs_lite,
                    "top_mean_margin_vs_lite": top_vs_lite,
                    "jointly_positive": jointly_positive,
                }
            )
        positive = sum(row["jointly_positive"] for row in seed_rows)
        policy_implementation_errors = [
            value for value in errors if value.startswith(f"{real_policy}:")
        ]
        qualified = (
            not policy_implementation_errors
            and positive >= int(qualification["minimum_positive_seed_count"])
        )
        comparisons[str(real_policy)] = seed_rows
        decisions[str(real_policy)] = {
            "reference_policy": reference,
            "corresponding_lite_policy": str(lite_policy),
            "positive_seed_count_vs_random_and_lite": positive,
            "required_positive_seed_count": int(
                qualification["minimum_positive_seed_count"]
            ),
            "implementation_valid": not policy_implementation_errors,
            "decision": (
                "KEEP_FOR_FUTURE_NEW_DATA_ARENA"
                if qualified
                else "EVICT_EXPERIMENTAL_UPGRADE"
            ),
            "does_not_authorize": [
                "FRESH_PERFORMANCE_SEARCH",
                "OOS_OR_FORWARD_READ",
                "CANDIDATE_PROMOTION",
            ],
        }
    return {
        "schema_version": 1,
        "implementation_result": "PASS" if not errors else "FAIL",
        "implementation_errors": errors,
        "lane_summaries": summaries,
        "matched_seed_comparisons": comparisons,
        "upgrade_decisions": decisions,
        "claim_scope": "SPENT_DEVELOPMENT_POLICY_PRODUCTIVITY_DIRECTION_ONLY",
    }


def _validate_inputs(
    repo_root: Path, config: Mapping[str, Any]
) -> tuple[RawPanelStore, dict[str, Any], dict[str, Any]]:
    parent_record = config["parent_evidence"]
    parent_path = repo_root / str(parent_record["manifest_path"])
    if not parent_path.is_file() or sha256_file(parent_path) != str(
        parent_record["manifest_sha256"]
    ).upper():
        raise ValueError("parent evidence manifest identity changed")
    parent = _read_json(parent_path)
    if (
        parent.get("bundle_sha256") != str(parent_record["bundle_sha256"]).upper()
        or parent.get("producer_source_sha") != str(parent_record["producer_source_sha"]).lower()
    ):
        raise ValueError("parent evidence binding changed")
    cache_root = repo_root / str(config["cache_root"])
    if not cache_root.is_dir():
        raise FileNotFoundError(f"pinned raw cache is unavailable: {cache_root}")
    metadata = _read_json(cache_root / "metadata.json")
    reuse = config["cache_reuse"]
    if metadata.get("identity_sha256") != str(reuse["expected_identity_sha256"]).upper():
        raise ValueError("pinned raw cache identity changed")
    if metadata.get("source_sha") != str(reuse["expected_producer_source_sha"]).lower():
        raise ValueError("pinned raw cache producer changed")
    bundle = _directory_bundle(cache_root)
    expected = reuse["directory_bundle"]
    if bundle != {
        "file_count": int(expected["file_count"]),
        "bytes": int(expected["bytes"]),
        "bundle_sha256": str(expected["bundle_sha256"]).upper(),
    }:
        raise ValueError("pinned raw cache content bundle changed")
    return RawPanelStore.open(cache_root), bundle, parent


def _replay_persisted_rows(
    rows: Sequence[Mapping[str, Any]],
    registry: TypedExpressionRegistry,
    config: Mapping[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    parameters = config.get("policy_parameters", {})
    for seed in config["budget"]["seeds"]:
        for policy_name in config["budget"]["policies"]:
            lane = sorted(
                (
                    row
                    for row in rows
                    if str(row["policy"]) == str(policy_name)
                    and int(row["seed"]) == int(seed)
                ),
                key=lambda row: int(row["proposal_step"]),
            )
            policy = LanePolicy(
                str(policy_name),
                int(seed),
                registry,
                dict(parameters.get(policy_name, {})),
            )
            for row in lane:
                candidate, metadata = policy.propose()
                prefix = f"{policy_name}:{seed}:{row['proposal_step']}"
                if candidate.candidate_id != str(row["candidate_id"]):
                    errors.append(prefix + ":candidate_id")
                if metadata["policy_state_hash_before"] != str(
                    row["policy_state_hash_before"]
                ):
                    errors.append(prefix + ":state_before")
                if json.dumps(metadata.get("mutation_receipt"), sort_keys=True) != str(
                    row["mutation_receipt_json"]
                ):
                    errors.append(prefix + ":mutation_receipt")
                persisted_spec = json.loads(str(row["candidate_spec_json"]))
                if candidate.to_dict() != persisted_spec:
                    errors.append(prefix + ":candidate_spec")
                policy.update(candidate, float(row["pair_reward"]))
                if policy.state_hash() != str(row["policy_state_hash_after"]):
                    errors.append(prefix + ":state_after")
    return {
        "result": "PASS" if not errors else "FAIL",
        "errors": errors,
        "lane_count": len(config["budget"]["policies"])
        * len(config["budget"]["seeds"]),
        "pair_count": len(rows),
    }


def _report_text(
    source_sha: str, audit: Mapping[str, Any], resource: Mapping[str, Any]
) -> str:
    lines = [
        "# Crypto Policy Upgrade Canary V1",
        "",
        f"- source SHA: `{source_sha}`",
        f"- implementation result: `{audit['implementation_result']}`",
        f"- strict pairs: `{resource['strict_pairs']}`",
        f"- wall seconds: `{resource['wall_seconds']:.3f}`",
        "- evidence scope: spent-development policy implementation/productivity only",
        "- sealed/report-only/forward reads: `0`",
        "- candidate promotion: `FORBIDDEN`",
        "",
        "## Upgrade decisions",
        "",
    ]
    for policy_name, decision in audit["upgrade_decisions"].items():
        lines.append(
            f"- `{policy_name}`: `{decision['decision']}` "
            f"({decision['positive_seed_count_vs_random_and_lite']}/"
            f"{decision['required_positive_seed_count']} matched seeds)"
        )
    lines.extend(
        [
            "",
            "These decisions do not establish alpha, OOS validity, or promotion eligibility.",
            "",
        ]
    )
    return "\n".join(lines)


def build_canary(
    repo_root: Path, *, config_path: Path, source_sha: str | None = None
) -> dict[str, Any]:
    config = _read_json(config_path)
    validate_canary_config(config)
    if not _git_clean(repo_root):
        raise RuntimeError("policy canary source tree must be clean")
    observed_sha = _git_sha(repo_root)
    if source_sha is not None and observed_sha != source_sha.lower():
        raise ValueError("checked-out source SHA differs from requested source")
    source_sha = observed_sha
    runtime_root = repo_root / str(config["outputs"]["runtime_root"])
    report_path = repo_root / str(config["outputs"]["report"])
    if runtime_root.exists() or report_path.exists():
        raise FileExistsError("policy canary output already exists")
    runtime_root.mkdir(parents=True)
    for name, value in config["resources"]["thread_caps"].items():
        os.environ[str(name)] = str(value)
    environment = _environment_fingerprint()
    if (
        environment["python_version"] != config["expected_environment"]["python_version"]
        or environment["packages"] != config["expected_environment"]["packages"]
    ):
        raise RuntimeError("execution environment differs from frozen canary contract")
    free_memory = int(psutil.virtual_memory().available)
    if free_memory < int(config["resources"]["minimum_free_memory_bytes"]):
        raise RuntimeError("insufficient free memory for policy canary")
    store, cache_before, parent = _validate_inputs(repo_root, config)
    field_binding, field_ids = _current_field_surface_binding(repo_root, config)
    if field_ids is None:
        raise ValueError("policy canary requires the current Broad field surface")
    train_config = _read_json(repo_root / str(config["train_surface_config"]))
    field_audit, field_registry, contracts, _ = _adaptive_surface_qualification(
        store,
        field_ids=field_ids,
        current_runtime_fields=train_config["runtime_fields"],
    )
    if field_registry.get("field_count") != 39 or set(
        field_audit["admission_status"]
    ) != {"ADMITTED"}:
        raise RuntimeError("current 39-field surface failed adaptive-only qualification")
    registry = TypedExpressionRegistry(contracts)
    compiler = _compiler_binding(repo_root)
    contract = {
        "schema_version": 1,
        "epoch_id": EPOCH_ID,
        "producer_source_sha": source_sha,
        "config_path": config_path.relative_to(repo_root).as_posix(),
        "config_sha256": sha256_file(config_path),
        "compiler": compiler,
        "parent_evidence": {
            "manifest_path": config["parent_evidence"]["manifest_path"],
            "manifest_sha256": config["parent_evidence"]["manifest_sha256"],
            "bundle_sha256": parent["bundle_sha256"],
            "policy_state_import": False,
        },
        "raw_cache": {
            "identity_sha256": store.metadata["identity_sha256"],
            "producer_source_sha": store.metadata["source_sha"],
            "directory_bundle": cache_before,
        },
        "field_surface": field_binding,
        "field_registry": field_registry,
        "field_contracts": _contracts_payload(contracts),
        "adaptive_block": {
            "start": ADAPTIVE_START,
            "end_exclusive": ADAPTIVE_END,
            "role": "SPENT_DEVELOPMENT_ENGINEERING_CANARY",
        },
        "budget": config["budget"],
        "policy_parameters": config["policy_parameters"],
        "boundaries": config["boundaries"],
        "sealed_reads": 0,
    }
    _write_json(runtime_root / RUNTIME_FILES[0], contract)
    compile_audit = compile_replay_audit(registry, config)
    if compile_audit["result"] != "PASS":
        raise RuntimeError("compile/replay preflight failed")
    _write_json(runtime_root / RUNTIME_FILES[1], compile_audit)
    lanes = [
        (policy_name, int(seed))
        for seed in config["budget"]["seeds"]
        for policy_name in config["budget"]["policies"]
    ]
    started = time.perf_counter()
    rows, worker_resources = _parallel_lanes(
        cache_root=repo_root / str(config["cache_root"]),
        contracts=contracts,
        lanes=lanes,
        count_per_lane=int(config["budget"]["pairs_per_lane"]),
        max_workers=int(config["resources"]["max_workers"]),
        policy_parameters=config["policy_parameters"],
        policy_order=config["budget"]["policies"],
    )
    wall_seconds = time.perf_counter() - started
    frame = pd.DataFrame(rows)
    frame.to_parquet(runtime_root / RUNTIME_FILES[2], index=False)
    audit = _policy_upgrade_audit(rows, config)
    replay = _replay_persisted_rows(rows, registry, config)
    if replay["result"] != "PASS":
        audit["implementation_errors"].extend(
            "REPLAY:" + value for value in replay["errors"]
        )
        audit["implementation_result"] = "FAIL"
    audit["persisted_reward_replay"] = replay
    _write_json(runtime_root / RUNTIME_FILES[3], audit)
    cache_after = _directory_bundle(repo_root / str(config["cache_root"]))
    resource = {
        "schema_version": 1,
        "execution_host": config["resources"]["execution_host"],
        "environment": environment,
        "free_memory_before_bytes": free_memory,
        "max_workers": int(config["resources"]["max_workers"]),
        "strict_pairs": len(rows),
        "wall_seconds": wall_seconds,
        "maximum_wall_seconds": int(config["resources"]["maximum_wall_seconds"]),
        "worker_resources": worker_resources,
        "maximum_worker_peak_rss_bytes": max(
            int(row["peak_rss_bytes"]) for row in worker_resources
        ),
        "raw_cache_bundle_before": cache_before,
        "raw_cache_bundle_after": cache_after,
        "raw_cache_unchanged": cache_before == cache_after,
    }
    if wall_seconds > int(config["resources"]["maximum_wall_seconds"]):
        audit["implementation_errors"].append("RESOURCE:WALL_SECONDS")
        audit["implementation_result"] = "FAIL"
    if resource["maximum_worker_peak_rss_bytes"] > int(
        config["resources"]["maximum_worker_peak_rss_bytes"]
    ):
        audit["implementation_errors"].append("RESOURCE:WORKER_RSS")
        audit["implementation_result"] = "FAIL"
    if not resource["raw_cache_unchanged"]:
        audit["implementation_errors"].append("RESOURCE:RAW_CACHE_DRIFT")
        audit["implementation_result"] = "FAIL"
    _write_json(runtime_root / RUNTIME_FILES[3], audit)
    _write_json(runtime_root / RUNTIME_FILES[5], resource)
    decision = {
        "schema_version": 1,
        "epoch_id": EPOCH_ID,
        "main_status": (
            "POLICY_UPGRADE_CANARY_COMPLETE"
            if audit["implementation_result"] == "PASS"
            else "POLICY_UPGRADE_CANARY_IMPLEMENTATION_FAILED"
        ),
        "implementation_result": audit["implementation_result"],
        "upgrade_decisions": audit["upgrade_decisions"],
        "strict_pairs": len(rows),
        "report_only_pairs": 0,
        "sealed_reads": 0,
        "candidate_promotion": "FORBIDDEN",
        "forward": "SEALED",
        "cross_sprint_adaptive_memory": "FORBIDDEN",
        "economic_claim": "NOT_EVALUATED_ON_FRESH_OR_OOS_DATA",
    }
    _write_json(runtime_root / RUNTIME_FILES[4], decision)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        _report_text(source_sha, audit, resource), encoding="utf-8", newline="\n"
    )
    artifacts = [runtime_root / name for name in RUNTIME_FILES] + [report_path]
    artifact_rows = [
        {
            "path": path.relative_to(repo_root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in artifacts
    ]
    manifest = {
        "schema_version": 1,
        "epoch_id": EPOCH_ID,
        "producer_source_sha": source_sha,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "sealed_reads": 0,
        "expected_artifact_paths": [row["path"] for row in artifact_rows],
        "artifacts": artifact_rows,
        "bundle_sha256": _payload_sha(artifact_rows),
    }
    _write_json(runtime_root / MANIFEST_FILE, manifest)
    return {
        "result": "PASS" if audit["implementation_result"] == "PASS" else "FAIL",
        "main_status": decision["main_status"],
        "source_sha": source_sha,
        "strict_pairs": len(rows),
        "wall_seconds": wall_seconds,
        "upgrade_decisions": audit["upgrade_decisions"],
        "bundle_sha256": manifest["bundle_sha256"],
    }


def check_canary(repo_root: Path, *, config_path: Path) -> dict[str, Any]:
    config = _read_json(config_path)
    validate_canary_config(config)
    runtime_root = repo_root / str(config["outputs"]["runtime_root"])
    manifest_path = runtime_root / MANIFEST_FILE
    if not manifest_path.is_file():
        return {"result": "FAIL", "errors": ["missing manifest"]}
    manifest = _read_json(manifest_path)
    errors: list[str] = []
    expected_paths = [
        (runtime_root / name).relative_to(repo_root).as_posix()
        for name in RUNTIME_FILES
    ] + [str(config["outputs"]["report"])]
    if manifest.get("expected_artifact_paths") != expected_paths:
        errors.append("expected_artifact_paths")
    if [row.get("path") for row in manifest.get("artifacts", [])] != expected_paths:
        errors.append("manifest_artifact_paths")
    for record in manifest.get("artifacts", []):
        path = repo_root / str(record["path"])
        if not path.is_file():
            errors.append("missing:" + str(record["path"]))
        elif (
            path.stat().st_size != int(record["bytes"])
            or sha256_file(path) != str(record["sha256"])
        ):
            errors.append("identity:" + str(record["path"]))
    if _payload_sha(manifest.get("artifacts", [])) != manifest.get("bundle_sha256"):
        errors.append("bundle_sha256")
    contract = _read_json(runtime_root / RUNTIME_FILES[0])
    if contract.get("config_sha256") != sha256_file(config_path):
        errors.append("config_sha256")
    if contract.get("compiler") != _compiler_binding(repo_root):
        errors.append("compiler_binding")
    if contract.get("sealed_reads") != 0 or manifest.get("sealed_reads") != 0:
        errors.append("sealed_reads")
    if _directory_bundle(repo_root / str(config["cache_root"])) != contract.get(
        "raw_cache", {}
    ).get("directory_bundle"):
        errors.append("raw_cache_bundle")
    registry = TypedExpressionRegistry(
        _contracts_from_payload(contract.get("field_contracts", []))
    )
    compile_observed = _read_json(runtime_root / RUNTIME_FILES[1])
    if compile_observed != compile_replay_audit(registry, config):
        errors.append("compile_replay")
    frame = pd.read_parquet(runtime_root / RUNTIME_FILES[2])
    rows = frame.to_dict("records")
    replay = _replay_persisted_rows(rows, registry, config)
    if replay["result"] != "PASS":
        errors.extend("persisted_replay:" + value for value in replay["errors"])
    observed_audit = _read_json(runtime_root / RUNTIME_FILES[3])
    recomputed_audit = _policy_upgrade_audit(rows, config)
    recomputed_audit["persisted_reward_replay"] = replay
    if observed_audit != recomputed_audit:
        errors.append("behavior_audit")
    decision = _read_json(runtime_root / RUNTIME_FILES[4])
    if (
        decision.get("upgrade_decisions") != observed_audit.get("upgrade_decisions")
        or decision.get("strict_pairs") != 2560
        or decision.get("report_only_pairs") != 0
        or decision.get("sealed_reads") != 0
        or decision.get("candidate_promotion") != "FORBIDDEN"
    ):
        errors.append("decision")
    resource = _read_json(runtime_root / RUNTIME_FILES[5])
    if (
        resource.get("raw_cache_unchanged") is not True
        or resource.get("strict_pairs") != 2560
        or resource.get("max_workers") != 8
    ):
        errors.append("resource")
    try:
        subprocess.check_call(
            ["git", "cat-file", "-e", f"{manifest['producer_source_sha']}^{{commit}}"],
            cwd=repo_root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except (KeyError, subprocess.CalledProcessError):
        errors.append("producer_source_sha")
    return {
        "result": "PASS" if not errors else "FAIL",
        "errors": errors,
        "main_status": decision.get("main_status"),
        "producer_source_sha": manifest.get("producer_source_sha"),
        "strict_pairs": decision.get("strict_pairs"),
        "bundle_sha256": manifest.get("bundle_sha256"),
    }


__all__ = [
    "CANARY_POLICIES",
    "EPOCH_ID",
    "build_canary",
    "check_canary",
    "compile_replay_audit",
    "validate_canary_config",
]
