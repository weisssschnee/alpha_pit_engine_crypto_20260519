"""One productive train-only P1 G2 expansion search with frozen P4 health."""

from __future__ import annotations

import concurrent.futures
import hashlib
import json
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
from .temporal_p1_semantic_expansion_v1 import (
    P1,
    compile_p1_generation2_catalog,
    p1_generation2_catalog_payload,
)
from .temporal_p1_semantic_proposal_v1 import (
    propose_p1_generation2_with_dispatcher,
)
from .temporal_proposal_dispatch_v1 import (
    configure_policy_dispatcher_v1,
    dispatcher_diagnostics,
    observe_dispatcher_v1,
    propose_with_dispatcher_v1,
)
from .temporal_realization_v2 import archive_diagnostics, configure_policy_realization_v2
from .temporal_representation_successor_v1 import ACTIVE_FAMILIES, build_compatibility_inventory
from .temporal_representation_tournament_v1 import (
    EXPECTED_AUTHORITY_IDENTITY,
    EXPECTED_LEDGER_SHA256,
    EXPECTED_MARKET_INPUT_IDENTITY,
    EXPECTED_PC2_EXECUTOR_IDENTITY,
    EXPECTED_POOL_SHA256,
    EXPECTED_PREAUTH_RECEIPT_SHA256,
    _load_frozen_inputs,
)
from .temporal_successor_v1 import verify_successor_market_inputs
from .temporal_targeted_deepening_v1 import targeted_diagnostics


EXECUTION_MODE = "P1_SEMANTIC_SUPPLY_EXPANSION_V1"
CAMPAIGN = "crypto_temporal_p1_semantic_supply_expansion_v1"
AUTHORIZATION_PATH = "config/crypto_temporal_p1_semantic_supply_expansion_v1_authorization.json"
HISTORICAL_PRIOR_PATH = "config/crypto_temporal_proposal_dispatch_v1_historical_prior.json"
SOURCE_GAP_PATH = "config/crypto_p1_semantic_supply_expansion_v1_source_gap.json"
G2_CATALOG_PATH = "config/crypto_p1_semantic_supply_expansion_v1_catalog.json"
BLOCK_ROBUST_V2_CONTRACT_PATH = "config/crypto_p1_g2_block_robust_ordering_v2.json"
BLOCK_ROBUST_V2_AUTHORITY = "DEVELOPMENT_THREE_BLOCK_ROBUST_ORDERING_V2"
PRIOR_INCOMPATIBILITY_EVIDENCE_PATH = (
    "reports/evidence/crypto_p1_semantic_supply_expansion_v1_20260816r1/"
    "control_incompatibility_closure.json"
)
STRICT_CAP = 20_000
CHECKPOINT_SIZE = 2_000
RAW_ATTEMPT_CAP = 500_000
WORKERS = 8
LANE_COUNT = 4
P4 = "P4_MULTISCALE_STATE_X_TRANSITION_ROUTING"
LANE_TARGETS = {"P1_G2": 0.70, "P1_G1": 0.15, "P4": 0.15}
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
    "alphafactory_crypto/broad_search/temporal_p1_semantic_expansion_v1.py",
    "alphafactory_crypto/broad_search/temporal_p1_semantic_proposal_v1.py",
    "alphafactory_crypto/broad_search/temporal_p1_semantic_expansion_search_v1.py",
    "alphafactory_crypto/broad_search/temporal_proposal_dispatch_v1.py",
    "alphafactory_crypto/broad_search/temporal_proposal_dispatch_search_v1.py",
    "alphafactory_crypto/broad_search/temporal_realization_v2.py",
    "alphafactory_crypto/broad_search/temporal_representation_successor_v1.py",
    "alphafactory_crypto/broad_search/temporal_representation_tournament_v1.py",
    "alphafactory_crypto/broad_search/temporal_successor_v1.py",
    "alphafactory_crypto/broad_search/temporal_targeted_deepening_v1.py",
    "config/crypto_search_engine_v1_4_binance_target_replay.json",
    "config/crypto_search_replication_aware_gate_v1.json",
    "config/crypto_search_replication_aware_gate_v1_r3_receipt.json",
    BLOCK_ROBUST_V2_CONTRACT_PATH,
    "config/crypto_temporal_mechanism_program_v1.json",
    "config/crypto_typed_mechanism_catalog_v2_1.json",
    HISTORICAL_PRIOR_PATH,
    SOURCE_GAP_PATH,
    G2_CATALOG_PATH,
    PRIOR_INCOMPATIBILITY_EVIDENCE_PATH,
    "runtime/crypto_search_engine_v1_4_oi_flow_20260728/aligned_carrier_manifest.json",
    "scripts/analyze_crypto_p1_semantic_supply_expansion_v1.py",
    "scripts/check_crypto_p1_semantic_supply_expansion_v1.py",
    "scripts/run_crypto_p1_semantic_supply_expansion_v1.py",
    "scripts/run_crypto_p1_semantic_supply_expansion_v1_pc2.ps1",
)


def _sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest().upper()


def _git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()


def _file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def authorization_content_sha(payload: Mapping[str, Any]) -> str:
    return _sha({key: value for key, value in payload.items() if key != "authorization_sha256"})


def derive_lane_seeds() -> tuple[int, ...]:
    values = tuple(
        int.from_bytes(
            hashlib.sha256(f"{EXECUTION_MODE}|LANE|{index}".encode("ascii")).digest()[:4],
            "big",
        )
        for index in range(LANE_COUNT)
    )
    if len(set(values)) != LANE_COUNT:
        raise RuntimeError("dispatcher lane seed collision")
    return values


LANE_SEEDS = derive_lane_seeds()


def validate_authorization(repo_root: Path) -> dict[str, Any]:
    root = repo_root.resolve()
    payload = engine._read_json(root / AUTHORIZATION_PATH)
    errors: list[str] = []
    if (
        payload.get("schema_version") != 1
        or payload.get("execution_mode") != EXECUTION_MODE
        or payload.get("status") != "RUN_AUTHORIZED_ONE_TIME_P1_SEMANTIC_EXPANSION_20000"
        or payload.get("run_authorized") is not True
        or payload.get("consumed") is not False
        or payload.get("authorization_sha256") != authorization_content_sha(payload)
    ):
        errors.append("authorization_hash_or_status")
    if dict(payload.get("budget") or {}) != {
        "strict_evaluated_maximum": STRICT_CAP,
        "raw_generation_attempts_maximum": RAW_ATTEMPT_CAP,
        "checkpoint_size": CHECKPOINT_SIZE,
        "diagnostic_boundary": 10_000,
        "workers": WORKERS,
    }:
        errors.append("budget")
    if tuple(int(value) for value in payload.get("lane_seeds") or ()) != LANE_SEEDS:
        errors.append("lane_seeds")
    if tuple(payload.get("active_program_families") or ()) != tuple(ACTIVE_FAMILIES):
        errors.append("family_scope")
    if dict(payload.get("lane_targets") or {}) != LANE_TARGETS:
        errors.append("lane_targets")
    if (
        int(payload.get("legacy_p1_g1_identity_count", -1)) != 180
        or int(payload.get("accepted_p1_g2_semantic_count", -1)) != 171
        or dict(payload.get("search_policy") or {}).get("optimizer_feedback")
        != BLOCK_ROBUST_V2_AUTHORITY
    ):
        errors.append("semantic_supply_or_optimizer_authority")
    block_contract = engine._read_json(root / BLOCK_ROBUST_V2_CONTRACT_PATH)
    if (
        block_contract.get("authority") != BLOCK_ROBUST_V2_AUTHORITY
        or _file_sha(root / BLOCK_ROBUST_V2_CONTRACT_PATH)
        != payload.get("block_robust_v2_contract_file_sha256")
        or payload.get("block_robust_v2_authority") != BLOCK_ROBUST_V2_AUTHORITY
    ):
        errors.append("block_robust_v2_contract")
    prior_incompatibility = engine._read_json(root / PRIOR_INCOMPATIBILITY_EVIDENCE_PATH)
    if (
        _file_sha(root / PRIOR_INCOMPATIBILITY_EVIDENCE_PATH)
        != payload.get("prior_incompatibility_evidence_file_sha256")
        or int(prior_incompatibility.get("search", {}).get("persisted_strict", -1)) != 0
        or int(prior_incompatibility.get("launches", {}).get(
            "candidate_evaluations_exact_by_completed_future_batches", -1
        )) != 16
    ):
        errors.append("prior_incompatibility_evidence")
    forbidden = dict(payload.get("forbidden_reads") or {})
    if forbidden != {"validation": 0, "oos": 0, "holdout": 0, "forward": 0, "promotion": 0, "sealed": 0}:
        errors.append("forbidden_reads")
    frozen = dict(payload.get("frozen_inputs") or {})
    if (
        frozen.get("ledger_sha256") != EXPECTED_LEDGER_SHA256
        or int(frozen.get("ledger_rows", -1)) != 50_000
        or int(frozen.get("matched_positive", -1)) != 302
        or int(frozen.get("target_basins", -1)) != 23
        or int(frozen.get("frozen_parents", -1)) != 228
        or frozen.get("parent_pool_sha256") != EXPECTED_POOL_SHA256
        or frozen.get("preauthorization_receipt_sha256") != EXPECTED_PREAUTH_RECEIPT_SHA256
    ):
        errors.append("frozen_inputs")
    if dict(payload.get("authority_identity") or {}) != EXPECTED_AUTHORITY_IDENTITY:
        errors.append("authority_identity")
    if dict(payload.get("market_input_identity") or {}) != EXPECTED_MARKET_INPUT_IDENTITY:
        errors.append("market_input_identity")
    if dict(payload.get("pc2_executor_identity") or {}) != EXPECTED_PC2_EXECUTOR_IDENTITY:
        errors.append("pc2_executor_identity")
    prior = engine._read_json(root / HISTORICAL_PRIOR_PATH)
    if (
        _file_sha(root / HISTORICAL_PRIOR_PATH) != payload.get("historical_prior_file_sha256")
        or prior.get("prior_sha256") != payload.get("historical_prior_sha256")
        or prior.get("forbidden_fields_verified") is not True
    ):
        errors.append("historical_prior")
    source_gap = engine._read_json(root / SOURCE_GAP_PATH)
    catalog_payload = engine._read_json(root / G2_CATALOG_PATH)
    if (
        _file_sha(root / SOURCE_GAP_PATH) != payload.get("source_gap_file_sha256")
        or source_gap.get("source_gap_sha256") != payload.get("source_gap_sha256")
        or _file_sha(root / G2_CATALOG_PATH) != payload.get("p1_g2_catalog_file_sha256")
        or catalog_payload.get("catalog_sha256") != payload.get("p1_g2_catalog_sha256")
    ):
        errors.append("p1_g2_catalog_or_source_gap")
    implementation_sha = str(payload.get("implementation_source_sha") or "").lower()
    components = dict(payload.get("execution_component_blob_oids") or {})
    if set(components) != set(REQUIRED_EXECUTION_COMPONENT_PATHS):
        errors.append("execution_component_set")
    for relative, expected in components.items():
        try:
            committed = _git(root, "rev-parse", f"{implementation_sha}:{relative}").lower()
            observed = _git(root, "hash-object", f"--path={relative}", relative).lower()
        except (OSError, subprocess.CalledProcessError):
            errors.append("execution_component_missing:" + relative)
            continue
        if committed != str(expected).lower() or observed != committed:
            errors.append("execution_component_drift:" + relative)
    if _git(root, "rev-parse", "HEAD^").lower() != implementation_sha:
        errors.append("authorization_not_direct_successor")
    changed = set(_git(root, "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD").splitlines())
    if changed != {AUTHORIZATION_PATH}:
        errors.append("authorization_commit_not_pure")
    if payload.get("implementation_remote_sync_state") not in {
        "SYNCHRONIZED", "REMOTE_SYNC_PENDING"
    }:
        errors.append("remote_sync_state")
    if _git(root, "status", "--porcelain=v1"):
        errors.append("worktree")
    if errors:
        raise RuntimeError("FAIL_CLOSED_BEFORE_MARKET_READ:" + ",".join(sorted(errors)))
    return payload


def preflight(repo_root: Path, *, runtime_id: str) -> dict[str, Any]:
    root = repo_root.resolve()
    authorization = validate_authorization(root)
    if runtime_id != str(authorization.get("runtime_id") or ""):
        raise RuntimeError("FAIL_CLOSED_BEFORE_MARKET_READ:runtime_id")
    runtime_root = root / "runtime" / runtime_id
    if runtime_root.exists() and not (runtime_root / "launch_claim.json").is_file():
        raise RuntimeError("FAIL_CLOSED_BEFORE_MARKET_READ:nonempty_unclaimed_runtime")
    market = verify_successor_market_inputs(root)
    baseline, pool = _load_frozen_inputs(root)
    return {
        "schema_version": 1,
        "status": "MINIMAL_LAUNCH_PREFLIGHT_PASS",
        "runtime_id": runtime_id,
        "authorization_sha256": authorization["authorization_sha256"],
        "historical_prior_sha256": authorization["historical_prior_sha256"],
        "source_gap_sha256": authorization["source_gap_sha256"],
        "p1_g2_catalog_sha256": authorization["p1_g2_catalog_sha256"],
        "block_robust_v2_authority": authorization["block_robust_v2_authority"],
        "block_robust_v2_contract_file_sha256": authorization[
            "block_robust_v2_contract_file_sha256"
        ],
        "market_preflight_sha256": _sha(market),
        "ledger_rows": int(baseline["source_strict_count"]),
        "ledger_sha256": baseline["source_ledger_sha256"],
        "matched_positive": int(baseline["matched_positive_count"]),
        "target_basins": int(pool["target_basin_count"]),
        "frozen_parents": int(pool["frozen_parent_candidate_count"]),
        "parent_pool_sha256": pool["target_parent_pool_sha256"],
        "market_arrays_read": 0,
        "candidate_evaluations": 0,
        "validation_reads": 0,
        "oos_reads": 0,
        "sealed_reads": 0,
    }


def _state(source_sha: str, frozen_hash: str, config: Mapping[str, Any]) -> dict[str, Any]:
    state = _new_state(source_sha, frozen_hash, config)
    state["skip_stage0"] = True
    state["active_program_families"] = list(ACTIVE_FAMILIES)
    state["arm_states"] = {"temporal_program_evolution": "ACTIVE"}
    template = next(iter(state["arm_counters"].values()))
    state["arm_counters"] = {"temporal_program_evolution": dict(template)}
    state["execution_mode"] = EXECUTION_MODE
    state["authorized_strict_cap"] = STRICT_CAP
    return state


def _make_policies(
    *, registry: Any, config: Mapping[str, Any], catalog: Sequence[Any],
    pool: Mapping[str, Any], baseline: Mapping[str, Any], prior: Mapping[str, Any],
    source_gap: Mapping[str, Any],
) -> dict[str, engine.MechanismEvolutionV2]:
    output = {}
    for seed in LANE_SEEDS:
        policy = _make_policy(
            arm="temporal_program_evolution", seed=seed, registry=registry,
            config=config, catalog=catalog,
        )
        if not isinstance(policy, engine.MechanismEvolutionV2):
            raise RuntimeError("dispatcher policy type changed")
        policy.parameters["selection_authority"] = BLOCK_ROBUST_V2_AUTHORITY
        configure_policy_realization_v2(policy, pool=pool, baseline=baseline)
        configure_policy_dispatcher_v1(
            policy, historical_prior=prior, p1_g2_source_gap=source_gap
        )
        output[f"DISPATCH|{seed}"] = policy
    return output


def _realizations(policy: engine.MechanismEvolutionV2, basin_id: str) -> set[str]:
    state = dict(policy.realization_v2_state or {})
    return {
        str(row.get("concrete_realization_id") or "")
        for row in dict(state.get("descendants") or {}).values()
        if str(row.get("economic_similarity_cluster_id") or "") == basin_id
    }


def _next_semantic_lane(
    ledger: Sequence[Mapping[str, Any]], proposals: Sequence[Mapping[str, Any]]
) -> str:
    counts = Counter(str(row.get("semantic_lane") or "") for row in ledger)
    counts.update(str(row.get("semantic_lane") or "") for row in proposals)
    target_total = len(ledger) + len(proposals) + 1
    return max(
        LANE_TARGETS,
        key=lambda lane: (
            float(LANE_TARGETS[lane]) * target_total - int(counts[lane]),
            float(LANE_TARGETS[lane]),
            lane,
        ),
    )


def _write_final(
    runtime_root: Path, *, state: Mapping[str, Any], policies: Mapping[str, Any],
    ledger: Sequence[Mapping[str, Any]], archive: engine.BehaviorArchive,
    baseline: Mapping[str, Any],
) -> dict[str, Any]:
    frame = pd.DataFrame(list(ledger))
    basin = targeted_diagnostics(ledger, baseline=baseline, strict_boundary=len(ledger))
    dispatch = dispatcher_diagnostics(policies)
    lane_counts = Counter(frame["semantic_lane"].astype(str))
    lane_outcomes = {
        lane: {
            "strict": int(len(local)),
            "matched_positive": int(local["matched_positive"].astype(bool).sum()),
            "matched_density": float(local["matched_positive"].astype(bool).mean()),
        }
        for lane, local in frame.groupby("semantic_lane", sort=True)
    }
    family_counts = dict(sorted(Counter(frame["program_family_id"].astype(str)).items()))
    if any(int(family_counts.get(family, 0)) for family in (
        "P2_RECENT_CROWDING_EVENT_TO_RESPONSE",
        "P3_FLOW_SHOCK_PERSISTENCE_TO_ABSORPTION",
    )):
        raise RuntimeError("RESEARCH_INVALID:P2_P3_SCOPE_CONTAMINATION")
    result = {
        "schema_version": 1,
        "status": "P1_SEMANTIC_SUPPLY_EXPANSION_20000_COMPLETE",
        "strict": len(ledger),
        "attempts": int(state["generation_attempts"]),
        "matched_positive": int(frame["matched_positive"].astype(bool).sum()),
        "matched_positive_density": float(frame["matched_positive"].astype(bool).mean()),
        "semantic_lane_counts": dict(sorted(lane_counts.items())),
        "semantic_lane_outcomes": lane_outcomes,
        "program_family_counts": family_counts,
        "p2_strict": 0,
        "p3_strict": 0,
        "basin_diagnostics": basin,
        "archive_diagnostics": archive_diagnostics(policies),
        "dispatcher_diagnostics": dispatch,
        "diagnostic_boundary_10000_only": True,
        "continued_to_20000_unless_research_invalid": True,
        "hard_cap_20000": True,
        "validation_reads": 0, "oos_reads": 0, "holdout_reads": 0,
        "forward_reads": 0, "promotion_reads": 0, "sealed_reads": 0,
        "automatic_next_run_started": False,
    }
    result = {**result, "run_result_sha256": _sha(result)}
    engine._write_parquet(runtime_root / "candidate_ledger.parquet", ledger)
    engine._write_parquet(runtime_root / "behavior_archive.parquet", archive.rows)
    engine._write_json(runtime_root / "basin_diagnostics_final.json", basin)
    engine._write_json(runtime_root / "realization_archive_final.json", result["archive_diagnostics"])
    engine._write_json(runtime_root / "dispatcher_diagnostics_final.json", dispatch)
    engine._write_json(runtime_root / "run_complete.json", result)
    return result


def _execute(
    runtime_root: Path, *, source_sha: str, frozen_hash: str,
    identities: Mapping[str, Any], registry: Any, config: Mapping[str, Any],
    catalog: Sequence[Any], pool: Mapping[str, Any], baseline: Mapping[str, Any],
    inventory: Any, prior: Mapping[str, Any], source_gap: Mapping[str, Any],
    g2_catalog: Sequence[Any], executor: concurrent.futures.ProcessPoolExecutor,
) -> dict[str, Any]:
    if (runtime_root / "run_complete.json").is_file():
        result = engine._read_json(runtime_root / "run_complete.json")
        if int(result.get("strict", -1)) == STRICT_CAP:
            return result
        raise RuntimeError("completed dispatcher runtime identity changed")
    checkpoints = sorted((runtime_root / "checkpoints").glob("checkpoint_[0-9][0-9][0-9]"))
    if checkpoints:
        state, policies, ledger, archive, _, metrics, rejected = _load_checkpoint(
            checkpoints[-1], registry=registry, expected_source=source_sha,
            expected_frozen=frozen_hash, expected_identities=identities,
        )
    else:
        state = _state(source_sha, frozen_hash, config)
        policies = _make_policies(
            registry=registry, config=config, catalog=catalog, pool=pool,
            baseline=baseline, prior=prior, source_gap=source_gap,
        )
        ledger, archive, metrics, rejected = [], engine.BehaviorArchive(), [], []
    attempted = set(str(value) for value in state.get("attempted_exact_ids", ()))
    lane_order = sorted(policies)
    lane_cursor = len(ledger)
    started = time.perf_counter()
    for checkpoint_index in range(len(checkpoints), STRICT_CAP // CHECKPOINT_SIZE):
        target = (checkpoint_index + 1) * CHECKPOINT_SIZE
        while len(ledger) < target:
            proposals = []
            while len(proposals) < WORKERS and len(ledger) + len(proposals) < target:
                semantic_lane = _next_semantic_lane(ledger, proposals)
                policy_key = lane_order[lane_cursor % len(lane_order)]
                lane_cursor += 1
                policy = policies[policy_key]
                policy.seen.update(attempted)
                seed = int(policy_key.rsplit("|", 1)[1])
                proposal_started = time.process_time()
                try:
                    if semantic_lane == "P1_G2":
                        candidate, metadata = propose_p1_generation2_with_dispatcher(
                            policy,
                            catalog=g2_catalog,
                            scale_contract=config["time_scale_authority"],
                        )
                    else:
                        candidate, metadata = propose_with_dispatcher_v1(
                            policy,
                            scale_contract=config["time_scale_authority"],
                            inventory=inventory,
                            allowed_families=(P1 if semantic_lane == "P1_G1" else P4,),
                        )
                except (ValueError, RuntimeError) as failure:
                    attempts = int(getattr(failure, "raw_attempts", 1))
                    state["generation_attempts"] += attempts
                    if int(state["generation_attempts"]) > RAW_ATTEMPT_CAP:
                        raise RuntimeError("RESEARCH_INVALID:RAW_ATTEMPT_CAP")
                    rejected.append({"checkpoint_index": checkpoint_index, "policy_key": policy_key,
                                     "status": "PROPOSAL_REJECT", "error": type(failure).__name__ + ":" + str(failure),
                                     "raw_attempts": attempts})
                    continue
                attempts = int(metadata.get("raw_attempts", 1))
                state["generation_attempts"] += attempts
                if int(state["generation_attempts"]) > RAW_ATTEMPT_CAP:
                    raise RuntimeError("RESEARCH_INVALID:RAW_ATTEMPT_CAP")
                if candidate.candidate_id in attempted or not engine._candidate_rebuild_verified(registry, candidate, {}):
                    attempted.add(candidate.candidate_id)
                    rejected.append({"checkpoint_index": checkpoint_index, "policy_key": policy_key,
                                     "status": "EXACT_OR_REPLAY_REJECT", "candidate_id": candidate.candidate_id})
                    continue
                attempted.add(candidate.candidate_id)
                proposals.append({"policy_key": policy_key, "policy": policy, "seed": seed,
                                  "candidate": candidate, "metadata": metadata,
                                  "semantic_lane": semantic_lane,
                                  "proposal_cpu_seconds": time.process_time() - proposal_started})
            futures = {executor.submit(engine._worker_evaluate, row["candidate"].to_dict()): row for row in proposals}
            results = [(futures[future], future.result()) for future in concurrent.futures.as_completed(futures)]
            for item, worker in sorted(results, key=lambda value: value[0]["candidate"].candidate_id):
                if worker.get("system_error") or worker.get("memory_error"):
                    raise RuntimeError("REPAIRABLE_FAULT:WORKER:" + str(worker.get("error")))
                if worker.get("evaluation") is None:
                    rejected.append({"checkpoint_index": checkpoint_index, "policy_key": item["policy_key"],
                                     "status": "PAIR_REJECTED", "candidate_id": item["candidate"].candidate_id,
                                     "error": worker.get("error")})
                    continue
                metadata = item["metadata"]
                dispatch_receipt = dict(metadata["dispatch_receipt"])
                basin_id = str(metadata["targeted_economic_basin_id"])
                before_realizations = _realizations(item["policy"], basin_id)
                proposal = {
                    "arm": "temporal_program_evolution", "seed": item["seed"],
                    "policy_key": item["policy_key"],
                    "checkpoint_completion_ordinal": len(ledger) % CHECKPOINT_SIZE + 1,
                    "generation_attempt_ordinal": int(state["generation_attempts"]),
                    "operation": metadata["operation"], "parent_ids": metadata["parent_ids"],
                    "receipt": metadata["receipt"], "receipt_verified": metadata["receipt_verified"],
                    "expression_hash_verified": True,
                    "policy_state_hash_before": metadata["policy_state_hash_before"],
                    "policy_state_hash_after_proposal": "",
                    "proposal_cpu_seconds": item["proposal_cpu_seconds"],
                }
                _observe_candidate(candidate=item["candidate"], evaluation=worker["evaluation"], proposal=proposal,
                                   worker=worker, archive=archive, policy=item["policy"], state=state,
                                   ledger=ledger, checkpoint_index=checkpoint_index)
                descendant = dict((item["policy"].realization_v2_state or {}).get("descendants") or {}).get(item["candidate"].candidate_id)
                retained = isinstance(descendant, Mapping)
                realization_id = str(dict(descendant or {}).get("concrete_realization_id") or "")
                new_realization = retained and realization_id not in before_realizations
                outcomes = observe_dispatcher_v1(
                    item["policy"], ledger_row=ledger[-1], dispatch_receipt=dispatch_receipt,
                    basin_retained=retained, new_realization=new_realization,
                    new_hq_realization=new_realization and bool(ledger[-1]["matched_positive"]),
                )
                ledger[-1].update({
                    "semantic_lane": item["semantic_lane"],
                    "semantic_generation": int(
                        dispatch_receipt["candidate_features"].get(
                            "semantic_generation", 1
                        )
                    ),
                    "parent_p1_program_id": dispatch_receipt["candidate_features"].get(
                        "parent_p1_program_id"
                    ),
                    "condition_role": dispatch_receipt["candidate_features"].get(
                        "condition_role"
                    ),
                    "condition_primitive": dispatch_receipt["candidate_features"].get(
                        "condition_primitive"
                    ),
                    "condition_operator": dispatch_receipt["candidate_features"].get(
                        "condition_operator"
                    ),
                    "condition_mode": dispatch_receipt["candidate_features"].get(
                        "condition_mode"
                    ),
                    "proposal_dispatcher_id": dispatch_receipt["dispatcher_id"],
                    "dispatch_receipt_json": json.dumps(dispatch_receipt, sort_keys=True, separators=(",", ":")),
                    "dispatch_receipt_sha256": dispatch_receipt["dispatch_receipt_sha256"],
                    "dispatch_legal_generated": int(dispatch_receipt["legal_candidates_generated"]),
                    "dispatch_legal_scored": int(dispatch_receipt["legal_candidates_scored"]),
                    "dispatch_selected_rank": int(dispatch_receipt["selected_rank"]),
                    "dispatch_selected_score": float(dispatch_receipt["selected_score"]),
                    "dispatch_selected_score_decile": int(dispatch_receipt["selected_score_decile"]),
                    "dispatch_exploration_selected": bool(dispatch_receipt["exploration_selected"]),
                    "dispatch_construction_route": dispatch_receipt["construction_route"],
                    "dispatch_semantic_edit_type": dispatch_receipt["candidate_features"]["semantic_edit_type"],
                    "dispatch_mutation_target": dispatch_receipt["candidate_features"]["mutation_target"],
                    "dispatch_basin_retained": bool(outcomes["basin_retained"]),
                    "dispatch_new_realization": bool(outcomes["new_realization"]),
                    "dispatch_new_hq_realization": bool(outcomes["new_hq_realization"]),
                    "policy_state_hash_after_dispatch_feedback": item["policy"].state_hash(),
                })
                state["arm_counters"]["temporal_program_evolution"]["exact_unique"] += 1
        state["attempted_exact_ids"] = sorted(attempted)
        state["wall_elapsed_seconds"] = float(state.get("wall_elapsed_seconds", 0.0)) + time.perf_counter() - started
        state["next_checkpoint_index"] = checkpoint_index + 1
        diagnostic = targeted_diagnostics(ledger, baseline=baseline, strict_boundary=len(ledger))
        _write_checkpoint(runtime_root, checkpoint_index=checkpoint_index, state=state, policies=policies,
                          ledger=ledger, archive=archive, pair_rows=[], metrics=metrics, rejected=rejected,
                          identities=identities, discovery_diagnostic=diagnostic)
        engine._write_json(runtime_root / f"diagnostic_{len(ledger):06d}.json", {
            "schema_version": 1, "status": "DIAGNOSTIC_ONLY", "strict": len(ledger),
            "continue_unless_research_invalid": len(ledger) < STRICT_CAP,
            "dispatcher": dispatcher_diagnostics(policies),
            "validation_reads": 0, "oos_reads": 0, "sealed_reads": 0,
        })
        started = time.perf_counter()
    return _write_final(runtime_root, state=state, policies=policies, ledger=ledger,
                        archive=archive, baseline=baseline)


def run(repo_root: Path, *, runtime_id: str) -> dict[str, Any]:
    root = repo_root.resolve()
    authorization = validate_authorization(root)
    if runtime_id != str(authorization.get("runtime_id") or ""):
        raise RuntimeError("FAIL_CLOSED_BEFORE_MARKET_READ:runtime_id")
    runtime_root = root / "runtime" / runtime_id
    claim_path = runtime_root / "launch_claim.json"
    if runtime_root.exists() and not claim_path.is_file():
        raise RuntimeError("FAIL_CLOSED_BEFORE_MARKET_READ:nonempty_unclaimed_runtime")
    runtime_root.mkdir(parents=True, exist_ok=True)
    market = verify_successor_market_inputs(root)
    baseline, pool = _load_frozen_inputs(root)
    prior = engine._read_json(root / HISTORICAL_PRIOR_PATH)
    source_gap = engine._read_json(root / SOURCE_GAP_PATH)
    committed_g2_catalog = engine._read_json(root / G2_CATALOG_PATH)
    config = json.loads(json.dumps(engine._read_json(root / CONFIG_PATH)))
    config["seed_authority"] = {**dict(config["seed_authority"]), "campaign": EXECUTION_MODE,
                                "derivation": "FIRST_UINT32_SHA256_EXECUTION_MODE_LANE",
                                "seeds": list(LANE_SEEDS), "old_campaign_seed_reuse": False}
    config["search_budget"].update({"strict_evaluated_maximum": STRICT_CAP,
                                    "raw_generation_attempts_maximum": RAW_ATTEMPT_CAP,
                                    "checkpoint_count_maximum": STRICT_CAP // CHECKPOINT_SIZE,
                                    "release_boundaries_strict": [10_000, STRICT_CAP]})
    source_sha = _git(root, "rev-parse", "HEAD").lower()
    claim = {"schema_version": 1, "status": "ONE_TIME_P1_SEMANTIC_EXPANSION_SEARCH_LAUNCHED",
             "authorization_sha256": authorization["authorization_sha256"], "source_sha": source_sha,
             "runtime_id": runtime_id, "historical_prior_sha256": prior["prior_sha256"],
             "source_gap_sha256": source_gap["source_gap_sha256"],
             "p1_g2_catalog_sha256": committed_g2_catalog["catalog_sha256"],
             "market_preflight_sha256": _sha(market), "parent_pool_sha256": pool["target_parent_pool_sha256"],
             "strict_at_claim": 0, "candidate_evaluations_at_claim": 0,
             "validation_reads": 0, "oos_reads": 0, "sealed_reads": 0}
    if claim_path.is_file():
        if engine._read_json(claim_path) != claim:
            raise RuntimeError("FAIL_CLOSED_BEFORE_MARKET_READ:launch_claim_changed")
    else:
        engine._write_json(claim_path, claim)
    economic = resolve_search_economic_receipt(root, str(config["source_authorities"]["economic_receipt_template"]))
    train = dict(economic["evidence_partition"]["train"])
    validate_pair_evaluation_request(block_start=str(train["start"]), block_end=str(train["end_exclusive"]),
                                     block_role=PAIRED_DIAGNOSTIC_BLOCK_ROLE, economic_receipt=economic,
                                     include_paired_diagnostic_paths=True)
    _, contracts, behavior, identities, _ = engine._load_v14_inputs(root, behavior_window=train)
    registry = engine.TypedExpressionRegistry(contracts, **_limits(config))
    temporal_catalog = compile_temporal_program_catalog(config)
    active_catalog = tuple(pair for pair in temporal_catalog if pair[1].family_id in set(ACTIVE_FAMILIES))
    g2_catalog = compile_p1_generation2_catalog(temporal_catalog, source_gap)
    compiled_g2_payload = p1_generation2_catalog_payload(g2_catalog, temporal_catalog)
    if (
        committed_g2_catalog.get("status") != "P1_G2_SEMANTIC_CATALOG_FROZEN"
        or committed_g2_catalog.get("catalog_sha256")
        != compiled_g2_payload["catalog_sha256"]
        or int(committed_g2_catalog.get("accepted_semantics", -1)) != len(g2_catalog)
        or committed_g2_catalog.get("source_gap_sha256")
        != source_gap["source_gap_sha256"]
    ):
        raise RuntimeError("RESEARCH_INVALID:P1_G2_CATALOG_CHANGED")
    mechanism_catalog = compile_mechanism_catalog(engine._read_json(root / "config/crypto_typed_mechanism_catalog_v2_1.json"))
    inventory = build_compatibility_inventory(temporal_catalog, mechanism_catalog)
    frozen = {"schema_version": 1, "execution_mode": EXECUTION_MODE, "source_sha": source_sha,
              "authorization_sha256": authorization["authorization_sha256"], "market_preflight": market,
              "ledger_sha256": baseline["source_ledger_sha256"], "parent_pool_sha256": pool["target_parent_pool_sha256"],
              "historical_prior_sha256": prior["prior_sha256"],
              "source_gap_sha256": source_gap["source_gap_sha256"],
              "p1_g2_catalog_sha256": compiled_g2_payload["catalog_sha256"],
              "block_robust_v2_authority": BLOCK_ROBUST_V2_AUTHORITY,
              "block_robust_v2_contract_file_sha256": _file_sha(
                  root / BLOCK_ROBUST_V2_CONTRACT_PATH
              ),
              "program_catalog_sha256": program_catalog_payload(temporal_catalog)["catalog_sha256"],
              "lane_targets": LANE_TARGETS,
              "lane_seeds": list(LANE_SEEDS), "input_identities": identities,
              "validation_reads": 0, "oos_reads": 0, "sealed_reads": 0}
    frozen_hash = _sha(frozen)
    frozen = {**frozen, "frozen_contract_sha256": frozen_hash}
    frozen_path = runtime_root / "frozen_contract.json"
    if frozen_path.is_file():
        if engine._read_json(frozen_path) != frozen:
            raise RuntimeError("RESEARCH_INVALID:FROZEN_CONTRACT_CHANGED")
    else:
        engine._write_json(frozen_path, frozen)
        engine._write_json(runtime_root / "authorization_snapshot.json", authorization)
        engine._write_json(runtime_root / "market_input_preflight.json", market)
        engine._write_json(runtime_root / "frozen_parent_pool.json", pool)
        engine._write_json(runtime_root / "historical_prior_snapshot.json", prior)
        engine._write_json(runtime_root / "source_gap_snapshot.json", source_gap)
        engine._write_json(runtime_root / "p1_g2_catalog_snapshot.json", compiled_g2_payload)
    cache_root = root / str(identities["raw_cache"]["root"])
    block_contract = engine._read_json(root / BLOCK_ROBUST_V2_CONTRACT_PATH)
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=WORKERS, initializer=engine._worker_initialize,
        initargs=(str(cache_root), engine._contracts_payload(contracts), behavior,
                  str(train["start"]), str(train["end_exclusive"]), PAIRED_DIAGNOSTIC_BLOCK_ROLE,
                  economic, True, block_contract, str(runtime_root / "process_evidence"), _limits(config)),
    ) as executor:
        return _execute(runtime_root, source_sha=source_sha, frozen_hash=frozen_hash,
                        identities=identities, registry=registry, config=config, catalog=active_catalog,
                        pool=pool, baseline=baseline, inventory=inventory, prior=prior,
                        source_gap=source_gap, g2_catalog=g2_catalog, executor=executor)


__all__ = ["AUTHORIZATION_PATH", "BLOCK_ROBUST_V2_AUTHORITY",
           "BLOCK_ROBUST_V2_CONTRACT_PATH", "CAMPAIGN", "EXECUTION_MODE",
           "HISTORICAL_PRIOR_PATH", "PRIOR_INCOMPATIBILITY_EVIDENCE_PATH",
           "SOURCE_GAP_PATH", "G2_CATALOG_PATH", "LANE_TARGETS",
           "LANE_SEEDS", "REQUIRED_EXECUTION_COMPONENT_PATHS", "STRICT_CAP",
           "authorization_content_sha", "preflight", "run", "validate_authorization"]
