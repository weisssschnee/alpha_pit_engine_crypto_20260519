"""Fixed train-only A/B tournament for the temporal representation successor."""

from __future__ import annotations

import concurrent.futures
import hashlib
import json
import os
import subprocess
import time
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

import pandas as pd

from . import search_engine_v1 as engine
from .compositional18m import compile_mechanism_catalog
from .experiment_authority import resolve_search_economic_receipt
from .pair18m import PAIRED_DIAGNOSTIC_BLOCK_ROLE, validate_pair_evaluation_request
from .temporal_program_search_v1 import (
    CONFIG_PATH,
    _limits,
    _load_checkpoint,
    _make_policy,
    _new_state,
    _observe_candidate,
    _write_checkpoint,
)
from .temporal_program_v1 import compile_temporal_program_catalog, program_catalog_payload
from .temporal_realization_v2 import (
    archive_diagnostics,
    configure_policy_realization_v2,
    propose_targeted_realization_v2,
)
from .temporal_representation_successor_v1 import (
    ACTIVE_FAMILIES,
    build_compatibility_inventory,
    propose_representation_successor,
)
from .temporal_successor_v1 import verify_successor_market_inputs
from .temporal_targeted_deepening_v1 import (
    build_frozen_target_parent_pool,
    targeted_diagnostics,
)


EXECUTION_MODE = "TEMPORAL_REPRESENTATION_SUCCESSOR_V1_TOURNAMENT"
CAMPAIGN = "crypto_temporal_representation_successor_v1"
AUTHORIZATION_PATH = "config/crypto_temporal_representation_successor_v1_authorization.json"
OFFLINE_EVIDENCE_PATH = "config/crypto_temporal_representation_successor_v1_offline_evidence.json"
IMPLEMENTATION_AUDIT_PATH = "config/crypto_temporal_representation_successor_v1_implementation_audit.json"
BASELINE_PATH = "config/crypto_temporal_targeted_p1_p4_basin_deepening_v1_baseline.json"
MECHANISM_CATALOG_PATH = "config/crypto_typed_mechanism_catalog_v2_1.json"
ARMS = (
    "LEGACY_REALIZATION_V2_CONTROL",
    "TEMPORAL_REPRESENTATION_SUCCESSOR",
)
STRICT_PER_ARM = 10_000
CHECKPOINT_SIZE = 2_000
RAW_ATTEMPT_CAP_PER_ARM = 100_000
EVOLUTION_PROBABILITIES = {
    "parameter_mutation_probability": 0.62,
    "mechanism_mutation_probability": 0.03,
    "crossover_probability": 0.35,
}
EXPECTED_LEDGER_SHA256 = "5171CD9655944CCED18D35CCB413C725E9542889260A135E8F95F4BE7B401B46"
EXPECTED_POOL_SHA256 = "A08112ED1765A432D15D259A70F308C2DE5BA7B617D294BFB8349020EC61AA49"
EXPECTED_PREAUTH_RECEIPT_SHA256 = "86CF72BEF57E56F0CC7EAB8ACAED6FB6173A049806E76E70B574E4E0866D50C4"
EXPECTED_AUTHORITY_IDENTITY = {
    "behavior_contract_sha256": "E3E41C3D9820558AE11E79C0767854B9AADDDFED4955F0F1B1CA9FD458BC8088",
    "economic_receipt_sha256": "244ADFC59AD7AAB453928365B68CAAB6B8537CDF55795EC9F97629F1B15A46AC",
    "market_contract_sha256": "E104F1A18901FC2370BE2CEE26D66BEE23EC3B33CE0719AC212F1BCADC161618",
    "optimizer_reward_and_matched_attribution_sha256": "23DC1B680613C558154E9D83DAC95EE0D944F834E26C37C77BA4E6B7F78E593B",
    "portfolio_mapping_and_cost_sha256": "C868E17F941E6677114920F63E7CD9BB45453106D8211E2B080787A2BC4367CF",
    "target_contract_sha256": "2EBC07A444C98465C49EC042890EB9DCEEAA7956E45D38F48830F130AAB66A60",
    "target_execution_sha256": "1D409B1580DC9AAF90C7A3C4E619F9C0998AA727AA4DC9204CCDB3538CC04630",
}
EXPECTED_MARKET_INPUT_IDENTITY = {
    "carrier": {
        "files": 122,
        "bytes": 598_775_942,
        "bundle_sha256": "340C01BEB680E776F9B2C6024FDD09AB3CDF09B608A4372C3E355AECF7F0CD97",
        "identity_sha256": "E8BFD15AF1EA58807A75868D52AD3535126DFB77CEDEB404EEE8E690AA58F2BA",
    },
    "target": {
        "files": 3,
        "bytes": 10_170_182,
        "bundle_sha256": "1B37684AB7442FF4BDBA37666FEC63DB4FFB01AF08623A1C04F4C06DD973B0A3",
        "identity_sha256": "27F780D458CBA50D6C82393F7DFDA396AC3994724645D112C4F8EF0ACDA865F0",
    },
}
EXPECTED_PC2_EXECUTOR_IDENTITY = {
    "host": "desktop-a2h3a2g",
    "user": "desktop-a2h3a2g\\suri",
    "workspace": "C:\\HermesWorker\\workspace\\crypto_temporal_search_core_realization_v2_20260814",
    "python": "D:\\HermesWorker\\workspace\\crypto_line\\.venv_b251733\\Scripts\\python.exe",
}
REQUIRED_EXECUTION_COMPONENT_PATHS = (
    "alphafactory_crypto/broad_search/compositional18m.py",
    "alphafactory_crypto/broad_search/experiment_authority.py",
    "alphafactory_crypto/broad_search/expression.py",
    "alphafactory_crypto/broad_search/pair18m.py",
    "alphafactory_crypto/broad_search/search_engine_v1.py",
    "alphafactory_crypto/broad_search/temporal_activation_v1.py",
    "alphafactory_crypto/broad_search/temporal_development_expansion_v1.py",
    "alphafactory_crypto/broad_search/temporal_program_search_v1.py",
    "alphafactory_crypto/broad_search/temporal_program_v1.py",
    "alphafactory_crypto/broad_search/temporal_realization_v2.py",
    "alphafactory_crypto/broad_search/temporal_representation_analysis_v1.py",
    "alphafactory_crypto/broad_search/temporal_representation_checker_v1.py",
    "alphafactory_crypto/broad_search/temporal_representation_successor_v1.py",
    "alphafactory_crypto/broad_search/temporal_representation_tournament_v1.py",
    "alphafactory_crypto/broad_search/temporal_successor_v1.py",
    "alphafactory_crypto/broad_search/temporal_targeted_deepening_v1.py",
    "config/crypto_search_engine_v1_4_binance_target_replay.json",
    "config/crypto_search_replication_aware_gate_v1.json",
    "config/crypto_search_replication_aware_gate_v1_r3_receipt.json",
    "config/crypto_temporal_mechanism_program_v1.json",
    "config/crypto_typed_mechanism_catalog_v2_1.json",
    "runtime/crypto_search_engine_v1_4_oi_flow_20260728/aligned_carrier_manifest.json",
    "scripts/analyze_crypto_temporal_representation_successor_v1.py",
    "scripts/check_crypto_temporal_representation_successor_v1.py",
    "scripts/run_crypto_temporal_representation_successor_v1.py",
    "scripts/run_crypto_temporal_representation_successor_v1_pc2.ps1",
)


def _sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "utf-8"
        )
    ).hexdigest().upper()


def _file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def authorization_content_sha(payload: Mapping[str, Any]) -> str:
    return _sha({key: value for key, value in payload.items() if key != "authorization_sha256"})


def derive_arm_lane_seeds(lane_count: int = 4) -> dict[str, tuple[int, ...]]:
    output = {}
    for arm in ARMS:
        seeds = tuple(
            int.from_bytes(
                hashlib.sha256(f"{EXECUTION_MODE}|{arm}|{index}".encode("ascii")).digest()[:4],
                "big",
            )
            for index in range(int(lane_count))
        )
        if len(set(seeds)) != int(lane_count):
            raise RuntimeError("tournament lane seed collision")
        output[arm] = seeds
    if set(output[ARMS[0]]) & set(output[ARMS[1]]):
        raise RuntimeError("tournament arms share a lane seed")
    return output


ARM_LANE_SEEDS = derive_arm_lane_seeds()


def _git(repo_root: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=repo_root, text=True).strip()


def _normalized_blob_oid(repo_root: Path, path: str) -> str:
    return _git(repo_root, "hash-object", f"--path={path}", path).lower()


def validate_authorization(repo_root: Path) -> dict[str, Any]:
    path = repo_root / AUTHORIZATION_PATH
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    errors = []
    if (
        payload.get("schema_version") != 1
        or payload.get("execution_mode") != EXECUTION_MODE
        or payload.get("status") != "RUN_AUTHORIZED_ONE_TIME_REPRESENTATION_TOURNAMENT"
        or payload.get("run_authorized") is not True
        or payload.get("consumed") is not False
        or payload.get("authorization_sha256") != authorization_content_sha(payload)
    ):
        errors.append("authorization_hash_or_status")
    if dict(payload.get("strict_budget") or {}) != {
        ARMS[0]: STRICT_PER_ARM,
        ARMS[1]: STRICT_PER_ARM,
        "total": STRICT_PER_ARM * 2,
    }:
        errors.append("strict_budget")
    if dict(payload.get("requested_operation_probabilities") or {}) != EVOLUTION_PROBABILITIES:
        errors.append("operation_probabilities")
    if {
        key: tuple(int(value) for value in values)
        for key, values in dict(payload.get("arm_lane_seeds") or {}).items()
    } != ARM_LANE_SEEDS:
        errors.append("arm_lane_seeds")
    frozen = dict(payload.get("frozen_inputs") or {})
    if (
        frozen.get("ledger_sha256") != EXPECTED_LEDGER_SHA256
        or int(frozen.get("ledger_rows", -1)) != 50_000
        or int(frozen.get("matched_positive", -1)) != 302
        or int(frozen.get("target_basins", -1)) != 23
        or int(frozen.get("frozen_parents", -1)) != 228
        or frozen.get("parent_pool_sha256") != EXPECTED_POOL_SHA256
        or frozen.get("preauthorization_receipt_sha256")
        != EXPECTED_PREAUTH_RECEIPT_SHA256
    ):
        errors.append("frozen_inputs")
    if dict(payload.get("forbidden_reads") or {}) != {
        "validation": 0,
        "oos": 0,
        "holdout": 0,
        "forward": 0,
        "promotion": 0,
        "sealed": 0,
    }:
        errors.append("forbidden_reads")
    if dict(payload.get("authority_identity") or {}) != EXPECTED_AUTHORITY_IDENTITY:
        errors.append("authority_identity")
    if dict(payload.get("market_input_identity") or {}) != EXPECTED_MARKET_INPUT_IDENTITY:
        errors.append("market_input_identity")
    if dict(payload.get("pc2_executor_identity") or {}) != EXPECTED_PC2_EXECUTOR_IDENTITY:
        errors.append("pc2_executor_identity")
    implementation_sha = str(payload.get("implementation_source_sha") or "").lower()
    components = dict(payload.get("execution_component_blob_oids") or {})
    if set(components) != set(REQUIRED_EXECUTION_COMPONENT_PATHS):
        errors.append("execution_component_set")
    for relative, expected in components.items():
        try:
            committed = _git(repo_root, "rev-parse", f"{implementation_sha}:{relative}").lower()
            observed = _normalized_blob_oid(repo_root, relative)
        except (OSError, subprocess.CalledProcessError):
            errors.append(f"execution_component_missing:{relative}")
            continue
        if committed != str(expected).lower() or observed != committed:
            errors.append(f"execution_component_drift:{relative}")
    head = _git(repo_root, "rev-parse", "HEAD").lower()
    tracking = _git(repo_root, "rev-parse", "@{upstream}").lower()
    if _git(repo_root, "rev-parse", "HEAD^").lower() != implementation_sha:
        errors.append("authorization_not_direct_successor")
    changed = set(
        _git(repo_root, "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD").splitlines()
    )
    if changed != {AUTHORIZATION_PATH}:
        errors.append("authorization_commit_not_pure")
    if head != tracking or _git(repo_root, "status", "--porcelain=v1"):
        errors.append("checkout_or_tracking_not_clean")
    if _file_sha(repo_root / OFFLINE_EVIDENCE_PATH) != str(
        payload.get("offline_evidence_sha256") or ""
    ):
        errors.append("offline_evidence")
    if _file_sha(repo_root / IMPLEMENTATION_AUDIT_PATH) != str(
        payload.get("implementation_audit_sha256") or ""
    ):
        errors.append("implementation_audit")
    if errors:
        raise RuntimeError("FAIL_CLOSED_BEFORE_MARKET_READ:" + ",".join(sorted(errors)))
    return payload


def _load_frozen_inputs(repo_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    baseline = json.loads((repo_root / BASELINE_PATH).read_text(encoding="utf-8-sig"))
    pool = build_frozen_target_parent_pool(repo_root, baseline)
    if (
        int(baseline.get("source_strict_count", -1)) != 50_000
        or baseline.get("source_ledger_sha256") != EXPECTED_LEDGER_SHA256
        or int(baseline.get("matched_positive_count", -1)) != 302
        or int(pool.get("target_basin_count", -1)) != 23
        or int(pool.get("frozen_parent_candidate_count", -1)) != 228
        or pool.get("target_parent_pool_sha256") != EXPECTED_POOL_SHA256
    ):
        raise RuntimeError("FAIL_CLOSED_BEFORE_MARKET_READ:frozen_development_identity")
    return baseline, pool


def preflight(repo_root: Path, *, runtime_id: str) -> dict[str, Any]:
    root = repo_root.resolve()
    authorization = validate_authorization(root)
    if runtime_id != str(authorization.get("runtime_id") or ""):
        raise RuntimeError("FAIL_CLOSED_BEFORE_MARKET_READ:runtime_id")
    runtime_root = root / "runtime" / runtime_id
    if runtime_root.exists() and not (runtime_root / "launch_claim.json").is_file():
        raise RuntimeError("FAIL_CLOSED_BEFORE_MARKET_READ:nonempty_unclaimed_runtime")
    market_preflight = verify_successor_market_inputs(root)
    baseline, pool = _load_frozen_inputs(root)
    return {
        "schema_version": 1,
        "status": "MINIMAL_LAUNCH_PREFLIGHT_PASS",
        "runtime_id": runtime_id,
        "authorization_sha256": authorization["authorization_sha256"],
        "market_preflight_sha256": _sha(market_preflight),
        "ledger_rows": int(baseline["source_strict_count"]),
        "ledger_sha256": baseline["source_ledger_sha256"],
        "matched_positive": int(baseline["matched_positive_count"]),
        "target_basins": int(pool["target_basin_count"]),
        "frozen_parents": int(pool["frozen_parent_candidate_count"]),
        "parent_pool_sha256": pool["target_parent_pool_sha256"],
        "existing_launch_claim": (runtime_root / "launch_claim.json").is_file(),
        "market_arrays_read": 0,
        "candidate_evaluations": 0,
        "validation_reads": 0,
        "oos_reads": 0,
        "holdout_reads": 0,
        "forward_reads": 0,
        "promotion_reads": 0,
        "sealed_reads": 0,
    }


def _arm_state(source_sha: str, frozen_hash: str, config: Mapping[str, Any], arm: str) -> dict[str, Any]:
    state = _new_state(source_sha, frozen_hash, config)
    state["skip_stage0"] = True
    state["active_program_families"] = list(ACTIVE_FAMILIES)
    state["arm_states"] = {"temporal_program_evolution": "ACTIVE"}
    template = next(iter(state["arm_counters"].values()))
    state["arm_counters"] = {"temporal_program_evolution": dict(template)}
    state["representation_tournament_arm"] = arm
    state["authorized_strict_cap"] = STRICT_PER_ARM
    return state


def _make_arm_policies(
    *,
    arm: str,
    registry: Any,
    config: Mapping[str, Any],
    catalog: Sequence[Any],
    pool: Mapping[str, Any],
    baseline: Mapping[str, Any],
) -> dict[str, engine.MechanismEvolutionV2]:
    output = {}
    for seed in ARM_LANE_SEEDS[arm]:
        policy = _make_policy(
            arm="temporal_program_evolution",
            seed=seed,
            registry=registry,
            config=config,
            catalog=catalog,
        )
        if not isinstance(policy, engine.MechanismEvolutionV2):
            raise RuntimeError("tournament policy type changed")
        configure_policy_realization_v2(policy, pool=pool, baseline=baseline)
        output[f"{arm}|{seed}"] = policy
    return output


def _write_arm_final(
    arm_root: Path,
    *,
    arm: str,
    state: Mapping[str, Any],
    policies: Mapping[str, Any],
    ledger: Sequence[Mapping[str, Any]],
    archive: engine.BehaviorArchive,
    baseline: Mapping[str, Any],
) -> dict[str, Any]:
    diagnostic = targeted_diagnostics(ledger, baseline=baseline, strict_boundary=len(ledger))
    archive_result = archive_diagnostics(policies)
    frame = pd.DataFrame(list(ledger))
    result = {
        "schema_version": 1,
        "status": "ARM_STRICT_CAP_COMPLETE",
        "arm": arm,
        "strict": len(ledger),
        "attempts": int(state["generation_attempts"]),
        "matched_positive": int(frame["matched_positive"].astype(bool).sum()),
        "matched_positive_density": float(frame["matched_positive"].astype(bool).mean()),
        "program_family_counts": dict(sorted(Counter(frame["program_family_id"].astype(str)).items())),
        "requested_operation_counts": dict(
            sorted(Counter(frame["requested_operation"].fillna("").astype(str)).items())
        ),
        "realized_operation_counts": dict(
            sorted(Counter(frame["realized_operation"].fillna("").astype(str)).items())
        ),
        "crossover_fallback_count": int(frame["crossover_fallback"].fillna(False).astype(bool).sum()),
        "basin_diagnostics": diagnostic,
        "archive_diagnostics": archive_result,
        "validation_reads": 0,
        "oos_reads": 0,
        "holdout_reads": 0,
        "forward_reads": 0,
        "promotion_reads": 0,
        "sealed_reads": 0,
    }
    result = {**result, "arm_result_sha256": _sha(result)}
    engine._write_json(arm_root / "arm_final.json", result)
    engine._write_parquet(arm_root / "candidate_ledger.parquet", ledger)
    engine._write_parquet(arm_root / "behavior_archive.parquet", archive.rows)
    engine._write_json(arm_root / "basin_diagnostics_final.json", diagnostic)
    engine._write_json(arm_root / "realization_archive_final.json", archive_result)
    return result


def _run_arm(
    *,
    arm_root: Path,
    arm: str,
    source_sha: str,
    frozen_hash: str,
    identities: Mapping[str, Any],
    registry: Any,
    config: Mapping[str, Any],
    catalog: Sequence[Any],
    pool: Mapping[str, Any],
    baseline: Mapping[str, Any],
    inventory: Any,
    executor: concurrent.futures.ProcessPoolExecutor,
) -> dict[str, Any]:
    if (arm_root / "arm_final.json").is_file():
        result = engine._read_json(arm_root / "arm_final.json")
        if result.get("arm") == arm and int(result.get("strict", -1)) == STRICT_PER_ARM:
            return result
        raise RuntimeError("completed tournament arm identity changed")
    arm_root.mkdir(parents=True, exist_ok=True)
    checkpoints = sorted((arm_root / "checkpoints").glob("checkpoint_[0-9][0-9][0-9]"))
    if checkpoints:
        state, policies, ledger, archive, _, metrics, rejected = _load_checkpoint(
            checkpoints[-1],
            registry=registry,
            expected_source=source_sha,
            expected_frozen=frozen_hash,
            expected_identities=identities,
        )
    else:
        state = _arm_state(source_sha, frozen_hash, config, arm)
        policies = _make_arm_policies(
            arm=arm,
            registry=registry,
            config=config,
            catalog=catalog,
            pool=pool,
            baseline=baseline,
        )
        ledger = []
        archive = engine.BehaviorArchive()
        metrics = []
        rejected = []
    attempted = set(str(value) for value in state.get("attempted_exact_ids", ()))
    lane_order = sorted(policies)
    started = time.perf_counter()
    for checkpoint_index in range(len(checkpoints), STRICT_PER_ARM // CHECKPOINT_SIZE):
        checkpoint_target = (checkpoint_index + 1) * CHECKPOINT_SIZE
        lane_cursor = 0
        while len(ledger) < checkpoint_target:
            proposals = []
            while len(proposals) < 8 and len(ledger) + len(proposals) < checkpoint_target:
                policy_key = lane_order[lane_cursor % len(lane_order)]
                lane_cursor += 1
                policy = policies[policy_key]
                seed = int(policy_key.rsplit("|", 1)[1])
                proposal_started = time.process_time()
                try:
                    if arm == ARMS[0]:
                        candidate, metadata = propose_targeted_realization_v2(policy)
                    else:
                        candidate, metadata = propose_representation_successor(
                            policy,
                            scale_contract=config["time_scale_authority"],
                            inventory=inventory,
                        )
                except (ValueError, RuntimeError) as failure:
                    attempts = int(getattr(failure, "raw_attempts", 1))
                    state["generation_attempts"] += attempts
                    if int(state["generation_attempts"]) > RAW_ATTEMPT_CAP_PER_ARM:
                        raise RuntimeError("RESEARCH_INVALID:RAW_ATTEMPT_CAP_PER_ARM")
                    rejected.append(
                        {
                            "checkpoint_index": checkpoint_index,
                            "policy_key": policy_key,
                            "status": "PROPOSAL_REJECT",
                            "error": type(failure).__name__ + ":" + str(failure),
                            "raw_attempts": attempts,
                        }
                    )
                    continue
                attempts = int(metadata.get("raw_attempts", 1))
                state["generation_attempts"] += attempts
                if int(state["generation_attempts"]) > RAW_ATTEMPT_CAP_PER_ARM:
                    raise RuntimeError("RESEARCH_INVALID:RAW_ATTEMPT_CAP_PER_ARM")
                if candidate.candidate_id in attempted or not engine._candidate_rebuild_verified(
                    registry, candidate, {}
                ):
                    attempted.add(candidate.candidate_id)
                    rejected.append(
                        {
                            "checkpoint_index": checkpoint_index,
                            "policy_key": policy_key,
                            "status": "EXACT_OR_REPLAY_REJECT",
                            "candidate_id": candidate.candidate_id,
                            "raw_attempts": attempts,
                        }
                    )
                    continue
                attempted.add(candidate.candidate_id)
                proposals.append(
                    {
                        "policy_key": policy_key,
                        "policy": policy,
                        "seed": seed,
                        "candidate": candidate,
                        "metadata": metadata,
                        "proposal_cpu_seconds": time.process_time() - proposal_started,
                    }
                )
            futures = {
                executor.submit(engine._worker_evaluate, row["candidate"].to_dict()): row
                for row in proposals
            }
            results = [(futures[future], future.result()) for future in concurrent.futures.as_completed(futures)]
            for row, worker in sorted(results, key=lambda value: value[0]["candidate"].candidate_id):
                if worker.get("system_error") or worker.get("memory_error"):
                    raise RuntimeError("REPAIRABLE_FAULT:WORKER:" + str(worker.get("error")))
                if worker.get("evaluation") is None:
                    rejected.append(
                        {
                            "checkpoint_index": checkpoint_index,
                            "policy_key": row["policy_key"],
                            "status": "PAIR_REJECTED",
                            "candidate_id": row["candidate"].candidate_id,
                            "error": worker.get("error"),
                        }
                    )
                    continue
                metadata = row["metadata"]
                proposal = {
                    "arm": "temporal_program_evolution",
                    "representation_tournament_arm": arm,
                    "seed": row["seed"],
                    "policy_key": row["policy_key"],
                    "checkpoint_completion_ordinal": len(ledger) % CHECKPOINT_SIZE + 1,
                    "generation_attempt_ordinal": int(state["generation_attempts"]),
                    "operation": metadata["operation"],
                    "parent_ids": metadata["parent_ids"],
                    "receipt": metadata.get("receipt"),
                    "receipt_verified": metadata.get("receipt_verified"),
                    "expression_hash_verified": True,
                    "policy_state_hash_before": metadata["policy_state_hash_before"],
                    "policy_state_hash_after_proposal": "",
                    "proposal_cpu_seconds": row["proposal_cpu_seconds"],
                }
                _observe_candidate(
                    candidate=row["candidate"],
                    evaluation=worker["evaluation"],
                    proposal=proposal,
                    worker=worker,
                    archive=archive,
                    policy=row["policy"],
                    state=state,
                    ledger=ledger,
                    checkpoint_index=checkpoint_index,
                )
                ledger[-1]["representation_tournament_arm"] = arm
                state["arm_counters"]["temporal_program_evolution"][
                    "exact_unique"
                ] += 1
        state["attempted_exact_ids"] = sorted(attempted)
        state["wall_elapsed_seconds"] = float(state.get("wall_elapsed_seconds", 0.0)) + (
            time.perf_counter() - started
        )
        state["next_checkpoint_index"] = checkpoint_index + 1
        diagnostic = targeted_diagnostics(
            ledger, baseline=baseline, strict_boundary=len(ledger)
        )
        _write_checkpoint(
            arm_root,
            checkpoint_index=checkpoint_index,
            state=state,
            policies=policies,
            ledger=ledger,
            archive=archive,
            pair_rows=[],
            metrics=metrics,
            rejected=rejected,
            identities=identities,
            discovery_diagnostic=diagnostic,
        )
        engine._write_json(
            arm_root / f"diagnostic_{len(ledger):06d}.json",
            {
                "schema_version": 1,
                "status": "DIAGNOSTIC_ONLY",
                "strict": len(ledger),
                "continue_unless_research_invalid": len(ledger) < STRICT_PER_ARM,
                "validation_reads": 0,
                "oos_reads": 0,
                "sealed_reads": 0,
            },
        )
        started = time.perf_counter()
    return _write_arm_final(
        arm_root,
        arm=arm,
        state=state,
        policies=policies,
        ledger=ledger,
        archive=archive,
        baseline=baseline,
    )


def run(repo_root: Path, *, runtime_id: str) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    authorization = validate_authorization(repo_root)
    if runtime_id != str(authorization.get("runtime_id") or ""):
        raise RuntimeError("FAIL_CLOSED_BEFORE_MARKET_READ:runtime_id")
    runtime_root = repo_root / "runtime" / runtime_id
    launch_claim_path = runtime_root / "launch_claim.json"
    if runtime_root.exists() and not launch_claim_path.is_file():
        raise RuntimeError("FAIL_CLOSED_BEFORE_MARKET_READ:nonempty_unclaimed_runtime")
    runtime_root.mkdir(parents=True, exist_ok=True)
    market_preflight = verify_successor_market_inputs(repo_root)
    baseline, pool = _load_frozen_inputs(repo_root)
    config = engine._read_json(repo_root / CONFIG_PATH)
    config = json.loads(json.dumps(config))
    config["seed_authority"] = {
        **dict(config["seed_authority"]),
        "campaign": EXECUTION_MODE,
        "derivation": "FIRST_UINT32_SHA256_EXECUTION_MODE_ARM_LANE",
        "seeds": list(ARM_LANE_SEEDS[ARMS[0]]),
        "old_campaign_seed_reuse": False,
    }
    config["policy_parameters"]["temporal_program_evolution"].update(
        EVOLUTION_PROBABILITIES
    )
    config["search_budget"].update(
        {
            "strict_evaluated_maximum": STRICT_PER_ARM * 2,
            "raw_generation_attempts_maximum": RAW_ATTEMPT_CAP_PER_ARM * 2,
            "checkpoint_count_maximum": 10,
            "release_boundaries_strict": [STRICT_PER_ARM, STRICT_PER_ARM * 2],
        }
    )
    source_sha = _git(repo_root, "rev-parse", "HEAD").lower()
    launch_claim = {
        "schema_version": 1,
        "status": "ONE_TIME_REPRESENTATION_TOURNAMENT_LAUNCHED",
        "authorization_sha256": authorization["authorization_sha256"],
        "source_sha": source_sha,
        "runtime_id": runtime_id,
        "market_preflight_sha256": _sha(market_preflight),
        "parent_pool_sha256": pool["target_parent_pool_sha256"],
        "strict_at_claim": 0,
        "candidate_evaluations_at_claim": 0,
        "validation_reads": 0,
        "oos_reads": 0,
        "sealed_reads": 0,
    }
    if launch_claim_path.is_file():
        if engine._read_json(launch_claim_path) != launch_claim:
            raise RuntimeError("FAIL_CLOSED_BEFORE_MARKET_READ:launch_claim_changed")
    else:
        engine._write_json(launch_claim_path, launch_claim)
    economic = resolve_search_economic_receipt(
        repo_root, str(config["source_authorities"]["economic_receipt_template"])
    )
    train = dict(economic["evidence_partition"]["train"])
    validate_pair_evaluation_request(
        block_start=str(train["start"]),
        block_end=str(train["end_exclusive"]),
        block_role=PAIRED_DIAGNOSTIC_BLOCK_ROLE,
        economic_receipt=economic,
        include_paired_diagnostic_paths=True,
    )
    store, contracts, behavior, identities, _ = engine._load_v14_inputs(
        repo_root, behavior_window=train
    )
    registry = engine.TypedExpressionRegistry(contracts, **_limits(config))
    temporal_catalog = compile_temporal_program_catalog(config)
    active_catalog = tuple(
        pair for pair in temporal_catalog if pair[1].family_id in set(ACTIVE_FAMILIES)
    )
    mechanism_catalog = compile_mechanism_catalog(
        engine._read_json(repo_root / MECHANISM_CATALOG_PATH)
    )
    inventory = build_compatibility_inventory(temporal_catalog, mechanism_catalog)
    frozen = {
        "schema_version": 1,
        "execution_mode": EXECUTION_MODE,
        "source_sha": source_sha,
        "authorization_sha256": authorization["authorization_sha256"],
        "market_preflight": market_preflight,
        "ledger_sha256": baseline["source_ledger_sha256"],
        "parent_pool_sha256": pool["target_parent_pool_sha256"],
        "program_catalog_sha256": program_catalog_payload(temporal_catalog)["catalog_sha256"],
        "arm_lane_seeds": {key: list(values) for key, values in ARM_LANE_SEEDS.items()},
        "input_identities": identities,
        "validation_reads": 0,
        "oos_reads": 0,
        "sealed_reads": 0,
    }
    frozen_hash = _sha(frozen)
    frozen = {**frozen, "frozen_contract_sha256": frozen_hash}
    frozen_path = runtime_root / "frozen_contract.json"
    if frozen_path.is_file():
        if engine._read_json(frozen_path) != frozen:
            raise RuntimeError("RESEARCH_INVALID:FROZEN_CONTRACT_CHANGED")
    else:
        engine._write_json(frozen_path, frozen)
        engine._write_json(runtime_root / "authorization_snapshot.json", authorization)
        engine._write_json(runtime_root / "market_input_preflight.json", market_preflight)
        engine._write_json(runtime_root / "frozen_parent_pool.json", pool)
    cache_root = repo_root / str(identities["raw_cache"]["root"])
    block_contract = engine._read_json(
        repo_root / str(config["source_authorities"]["development_blocks_config"])
    )["block_robust_contract"]
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=8,
        initializer=engine._worker_initialize,
        initargs=(
            str(cache_root),
            engine._contracts_payload(contracts),
            behavior,
            str(train["start"]),
            str(train["end_exclusive"]),
            PAIRED_DIAGNOSTIC_BLOCK_ROLE,
            economic,
            True,
            block_contract,
            str(runtime_root / "process_evidence"),
            _limits(config),
        ),
    ) as executor:
        arm_results = {
            arm: _run_arm(
                arm_root=runtime_root / "arms" / arm,
                arm=arm,
                source_sha=source_sha,
                frozen_hash=frozen_hash,
                identities=identities,
                registry=registry,
                config=config,
                catalog=active_catalog,
                pool=pool,
                baseline=baseline,
                inventory=inventory,
                executor=executor,
            )
            for arm in ARMS
        }
    final = {
        "schema_version": 1,
        "status": "REPRESENTATION_TOURNAMENT_20000_COMPLETE",
        "strict": sum(int(value["strict"]) for value in arm_results.values()),
        "attempts": sum(int(value["attempts"]) for value in arm_results.values()),
        "arms": arm_results,
        "diagnostic_boundary_10000_only": True,
        "validation_reads": 0,
        "oos_reads": 0,
        "holdout_reads": 0,
        "forward_reads": 0,
        "promotion_reads": 0,
        "sealed_reads": 0,
        "automatic_next_run_started": False,
    }
    final = {**final, "tournament_result_sha256": _sha(final)}
    engine._write_json(runtime_root / "tournament_complete.json", final)
    return final


__all__ = [
    "ARM_LANE_SEEDS",
    "ARMS",
    "AUTHORIZATION_PATH",
    "CAMPAIGN",
    "EXECUTION_MODE",
    "STRICT_PER_ARM",
    "authorization_content_sha",
    "derive_arm_lane_seeds",
    "preflight",
    "run",
    "validate_authorization",
]
