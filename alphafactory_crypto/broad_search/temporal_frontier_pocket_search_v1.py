"""Evidence-conditioned, train-only maturation run for the P5/P6 singleton pockets."""

from __future__ import annotations

import concurrent.futures
import hashlib
import json
import random
import subprocess
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

import pandas as pd

from . import search_engine_v1 as engine
from .experiment_authority import resolve_search_economic_receipt
from .pair18m import PAIRED_DIAGNOSTIC_BLOCK_ROLE, validate_pair_evaluation_request
from .temporal_frontier_pocket_v1 import (
    ANCHORS,
    classify_against_anchor,
    load_anchor_rows,
    propose_local,
    realization_id,
    rebuild_anchors,
)
from .temporal_hypothesis_frontier_v1 import P5, P6
from .temporal_program_search_v1 import CONFIG_PATH, _limits, _new_state, _observe_candidate, _write_checkpoint
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


EXECUTION_MODE = "FRONTIER_POCKET_MATURATION_V1"
AUTHORIZATION_PATH = "config/crypto_temporal_frontier_pocket_maturation_v1_authorization.json"
ASSURANCE_PATH = "config/crypto_temporal_frontier_pocket_maturation_v1_assurance.json"
STRICT_CAP = 20_000
CHECKPOINT_SIZE = 2_000
RAW_ATTEMPT_CAP = 1_250_000
WORKERS = 8
SEEDS = {
    family: [
        int.from_bytes(hashlib.sha256(f"{EXECUTION_MODE}|{family}|{lane}".encode()).digest()[:4], "big")
        for lane in range(4)
    ]
    for family in (P5, P6)
}
REQUIRED_EXECUTION_COMPONENT_PATHS = (
    "alphafactory_crypto/broad_search/compositional18m.py",
    "alphafactory_crypto/broad_search/expression.py",
    "alphafactory_crypto/broad_search/experiment_authority.py",
    "alphafactory_crypto/broad_search/pair18m.py",
    "alphafactory_crypto/broad_search/search_engine_v1.py",
    "alphafactory_crypto/broad_search/temporal_program_search_v1.py",
    "alphafactory_crypto/broad_search/temporal_hypothesis_frontier_v1.py",
    "alphafactory_crypto/broad_search/temporal_targeted_deepening_v1.py",
    "alphafactory_crypto/broad_search/temporal_frontier_pocket_v1.py",
    "alphafactory_crypto/broad_search/temporal_frontier_pocket_assurance_v1.py",
    "alphafactory_crypto/broad_search/temporal_frontier_pocket_search_v1.py",
    "config/crypto_search_engine_v1_4_binance_target_replay.json",
    "config/crypto_search_replication_aware_gate_v1.json",
    "config/crypto_search_replication_aware_gate_v1_r3_receipt.json",
    "config/crypto_p1_g2_block_robust_ordering_v2.json",
    "runtime/crypto_search_engine_v1_4_oi_flow_20260728/aligned_carrier_manifest.json",
    "scripts/assure_crypto_temporal_frontier_pocket_v1.py",
    "scripts/run_crypto_temporal_frontier_pocket_maturation_v1.py",
    "scripts/analyze_crypto_temporal_frontier_pocket_maturation_v1.py",
    "scripts/check_crypto_temporal_frontier_pocket_maturation_v1.py",
    "scripts/run_crypto_temporal_frontier_pocket_maturation_v1_pc2.ps1",
)


def _sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str).encode()).hexdigest().upper()


def _file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()


def authorization_content_sha(payload: Mapping[str, Any]) -> str:
    return _sha({key: value for key, value in payload.items() if key != "authorization_sha256"})


def validate_authorization(repo_root: Path) -> dict[str, Any]:
    root = repo_root.resolve()
    payload = engine._read_json(root / AUTHORIZATION_PATH)
    errors = []
    if (
        payload.get("schema_version") != 1
        or payload.get("execution_mode") != EXECUTION_MODE
        or payload.get("status") != "RUN_AUTHORIZED_ONE_TIME_FRONTIER_POCKET_MATURATION_V1"
        or payload.get("run_authorized") is not True
        or payload.get("consumed") is not False
        or payload.get("authorization_sha256") != authorization_content_sha(payload)
    ):
        errors.append("authorization_hash_or_status")
    if dict(payload.get("budget") or {}) != {
        "strict_evaluated_maximum": STRICT_CAP,
        "raw_generation_attempts_maximum": RAW_ATTEMPT_CAP,
        "checkpoint_size": CHECKPOINT_SIZE,
        "workers": WORKERS,
    }:
        errors.append("budget")
    if dict(payload.get("lane_seeds") or {}) != SEEDS:
        errors.append("lane_seeds")
    if tuple(payload.get("active_program_families") or ()) != (P5, P6):
        errors.append("family_scope")
    if dict(payload.get("forbidden_reads") or {}) != {"validation": 0, "oos": 0, "holdout": 0, "forward": 0, "promotion": 0, "sealed": 0}:
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
    assurance = engine._read_json(root / ASSURANCE_PATH)
    if (
        assurance.get("status") != "FRONTIER_POCKET_PREAUTH_ASSURANCE_PASS"
        or _file_sha(root / ASSURANCE_PATH) != payload.get("assurance_file_sha256")
        or assurance.get("assurance_receipt_sha256") != payload.get("assurance_receipt_sha256")
        or int(assurance.get("new_strict", -1)) != 0
    ):
        errors.append("assurance")
    frontier = dict(payload.get("frontier_source") or {})
    source_path = root / str(frontier.get("relative_ledger_path") or "")
    if not source_path.is_file() or source_path.stat().st_size != int(frontier.get("ledger_bytes", -1)) or _file_sha(source_path) != frontier.get("ledger_sha256"):
        errors.append("frontier_source_ledger")
    implementation = str(payload.get("implementation_source_sha") or "").lower()
    components = dict(payload.get("execution_component_blob_oids") or {})
    if set(components) != set(REQUIRED_EXECUTION_COMPONENT_PATHS):
        errors.append("execution_component_set")
    for relative, expected in components.items():
        try:
            committed = _git(root, "rev-parse", f"{implementation}:{relative}").lower()
            observed = _git(root, "hash-object", f"--path={relative}", relative).lower()
        except (OSError, subprocess.CalledProcessError):
            errors.append("execution_component_missing:" + relative)
            continue
        if committed != str(expected).lower() or observed != committed:
            errors.append("execution_component_drift:" + relative)
    if _git(root, "rev-parse", "HEAD^").lower() != implementation:
        errors.append("authorization_not_direct_successor")
    changed = set(_git(root, "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD").splitlines())
    if changed != {AUTHORIZATION_PATH}:
        errors.append("authorization_commit_not_pure")
    if _git(root, "status", "--porcelain=v1", "--untracked-files=no"):
        errors.append("worktree")
    if errors:
        raise RuntimeError("FAIL_CLOSED_BEFORE_MARKET_READ:" + ",".join(sorted(errors)))
    return payload


def preflight(repo_root: Path, *, runtime_id: str) -> dict[str, Any]:
    root = repo_root.resolve()
    authorization = validate_authorization(root)
    if runtime_id != authorization.get("runtime_id"):
        raise RuntimeError("FAIL_CLOSED_BEFORE_MARKET_READ:runtime_id")
    if (root / "runtime" / runtime_id).exists():
        raise RuntimeError("FAIL_CLOSED_BEFORE_MARKET_READ:runtime_exists")
    market = verify_successor_market_inputs(root)
    baseline, pool = _load_frozen_inputs(root)
    return {
        "schema_version": 1,
        "status": "FRONTIER_POCKET_MINIMAL_LAUNCH_PREFLIGHT_PASS",
        "authorization_sha256": authorization["authorization_sha256"],
        "market_preflight_sha256": _sha(market),
        "ledger_rows": baseline["source_strict_count"],
        "ledger_sha256": baseline["source_ledger_sha256"],
        "target_basins": pool["target_basin_count"],
        "frozen_parents": pool["frozen_parent_candidate_count"],
        "parent_pool_sha256": pool["target_parent_pool_sha256"],
        "market_arrays_read": 0,
        "candidate_evaluations": 0,
        "validation_reads": 0,
        "oos_reads": 0,
        "holdout_reads": 0,
        "forward_reads": 0,
        "promotion_reads": 0,
        "sealed_reads": 0,
    }


def _pocket_stats(ledger: Sequence[Mapping[str, Any]], family: str, anchor_row: Mapping[str, Any], *, start: int = 0) -> dict[str, Any]:
    rows = [row for row in ledger[start:] if str(row.get("program_family_id")) == family]
    anchor_rows = [row for row in rows if row.get("pocket_classification") == "ANCHOR_POCKET"]
    realizations = {realization_id(anchor_row)} | {str(row.get("concrete_realization_id")) for row in anchor_rows}
    def unique(key: str) -> int:
        return len({str(row.get(key) or "NOT_AVAILABLE") for row in anchor_rows})
    return {
        "strict": len(rows),
        "matched_positive": sum(bool(row.get("matched_positive")) for row in rows),
        "anchor_pocket_matched": len(anchor_rows),
        "local_new_basin_matched": sum(row.get("pocket_classification") == "LOCAL_NEW_BASIN" for row in rows),
        "near_miss": sum(row.get("pocket_classification") == "NEAR_MISS" for row in rows),
        "replicated_3_of_3": sum(int(row.get("replicated_positive_block_count") or 0) == 3 for row in rows),
        "new_concrete_realizations": max(0, len(realizations) - 1),
        "total_anchor_pocket_members": 1 + len(anchor_rows),
        "total_concrete_realizations": len(realizations),
        "seed_count": unique("seed"),
        "binding_count": unique("binding_class"),
        "mapped_weight_descriptor_count": unique("mapped_weight_descriptor_id"),
        "turnover_descriptor_count": unique("turnover_path_descriptor_id"),
        "asset_descriptor_count": unique("selected_asset_overlap_id"),
        "exact_anchor_binding_strict": sum(row.get("binding_class") == "EXACT_ANCHOR_BINDING" for row in rows),
        "same_source_neighbor_strict": sum(row.get("binding_class") == "SAME_SOURCE_OR_VENUE_NEIGHBOR" for row in rows),
        "exact_anchor_binding_matched": sum(row.get("binding_class") == "EXACT_ANCHOR_BINDING" and bool(row.get("matched_positive")) for row in rows),
        "same_source_neighbor_matched": sum(row.get("binding_class") == "SAME_SOURCE_OR_VENUE_NEIGHBOR" and bool(row.get("matched_positive")) for row in rows),
        "matured": 1 + len(anchor_rows) >= 3 and len(realizations) >= 2,
    }


def _next_family(ledger: Sequence[Mapping[str, Any]], batch: Sequence[Mapping[str, Any]], target: Mapping[str, int]) -> str:
    counts = Counter(str(row.get("program_family_id")) for row in ledger)
    counts.update(str(row.get("family")) for row in batch)
    live = [family for family in (P5, P6) if int(target.get(family, 0)) > counts[family]]
    if not live:
        raise RuntimeError("POCKET_STAGE_TARGET_EXHAUSTED")
    return max(live, key=lambda family: (int(target[family]) - counts[family], family))


def _final(runtime_root: Path, *, terminal: str, state: Mapping[str, Any], ledger: Sequence[Mapping[str, Any]], archive: engine.BehaviorArchive, anchor_rows: Mapping[str, Mapping[str, Any]], assurance: Mapping[str, Any], stage_decisions: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    families = dict(Counter(str(row.get("program_family_id")) for row in ledger))
    forbidden = {family: int(families.get(family, 0)) for family in ("P1_POSITION_STATE_CHANGE_TO_RESPONSE", "P2_RECENT_CROWDING_EVENT_TO_RESPONSE", "P3_FLOW_SHOCK_PERSISTENCE_TO_ABSORPTION")}
    if any(forbidden.values()):
        raise RuntimeError("RESEARCH_INVALID:FAMILY_SCOPE_CONTAMINATION")
    outcomes = {family: _pocket_stats(ledger, family, anchor_rows[family]) for family in (P5, P6)}
    matured = {family: bool(values["matured"]) for family, values in outcomes.items()}
    if all(matured.values()):
        decision = "BOTH_POCKETS_MATURED"
    elif matured[P6]:
        decision = "P6_ONLY_MATURED"
    elif matured[P5]:
        decision = "P5_ONLY_MATURED"
    elif any(values["anchor_pocket_matched"] or values["local_new_basin_matched"] for values in outcomes.values()):
        decision = "POCKETS_PARTIAL"
    else:
        decision = "FRONTIER_POCKETS_NOT_MATURABLE"
    result = {
        "schema_version": 1,
        "status": terminal,
        "strict": len(ledger),
        "attempts": int(state["generation_attempts"]),
        "pocket_outcomes": outcomes,
        "p5_anchor_classification": assurance["p5_sparse_event_falsification"]["classification"],
        "p6_portability": "NOT_EXECUTED_UNLESS_STRONGLY_MATURED",
        "stage_decisions": list(stage_decisions),
        "inactive_family_strict": forbidden,
        "next_decision": decision,
        "pocket_validation_cohort_ready": bool(any(matured.values())),
        "validation_reads": 0,
        "oos_reads": 0,
        "holdout_reads": 0,
        "forward_reads": 0,
        "promotion_reads": 0,
        "sealed_reads": 0,
        "automatic_next_run_started": False,
    }
    result = {**result, "run_result_sha256": _sha(result)}
    engine._write_parquet(runtime_root / "candidate_ledger.parquet", ledger)
    engine._write_parquet(runtime_root / "behavior_archive.parquet", archive.rows)
    engine._write_json(runtime_root / "stage_decisions.json", {"decisions": list(stage_decisions)})
    engine._write_json(runtime_root / "run_complete.json", result)
    return result


def _execute(runtime_root: Path, *, source_sha: str, frozen_hash: str, identities: Mapping[str, Any], registry: Any, anchors: Mapping[str, Any], anchor_rows: Mapping[str, Mapping[str, Any]], assurance: Mapping[str, Any], executor: concurrent.futures.ProcessPoolExecutor) -> dict[str, Any]:
    config = engine._read_json(runtime_root / "effective_config.json")
    state = _new_state(source_sha, frozen_hash, config)
    state.update({"execution_mode": EXECUTION_MODE, "active_program_families": [P5, P6], "arm_states": {"frontier_pocket_local": "ACTIVE"}})
    template = next(iter(state["arm_counters"].values()))
    state["arm_counters"] = {"frontier_pocket_local": dict(template)}
    ledger: list[dict[str, Any]] = []
    archive = engine.BehaviorArchive()
    rejected: list[dict[str, Any]] = []
    attempted: set[str] = set(ANCHORS[family]["candidate_id"] for family in (P5, P6))
    rng = {family: [random.Random(seed) for seed in SEEDS[family]] for family in (P5, P6)}
    lane_cursor = {family: 0 for family in (P5, P6)}
    live = set(assurance["live_initial_pockets"])
    saturation = {family: 0 for family in (P5, P6)}
    stage_decisions: list[dict[str, Any]] = []
    target_total = 2_000
    scale_phase_end = 2_000
    stage_target = {P6: 1_500, P5: 500} if P5 in live else {P6: 2_000, P5: 0}
    successor = False
    started = time.perf_counter()
    checkpoint_index = 0
    while len(ledger) < min(target_total, STRICT_CAP):
        while len(ledger) < target_total:
            proposals = []
            while len(proposals) < WORKERS and len(ledger) + len(proposals) < target_total:
                family = _next_family(ledger, proposals, stage_target)
                attempts = 0
                candidate = None
                while candidate is None:
                    attempts += 1
                    state["generation_attempts"] += 1
                    if state["generation_attempts"] > RAW_ATTEMPT_CAP:
                        return _final(runtime_root, terminal="OPERATIONAL_PROPOSAL_SUPPLY_EXHAUSTED", state=state, ledger=ledger, archive=archive, anchor_rows=anchor_rows, assurance=assurance, stage_decisions=stage_decisions)
                    try:
                        lane = lane_cursor[family] % len(rng[family])
                        lane_cursor[family] += 1
                        local = propose_local(registry, anchors[family], family, rng[family][lane], exact_binding_weight=0.20 if successor else 0.60)
                    except ValueError as failure:
                        rejected.append({"status": "PROPOSAL_REJECT", "family": family, "error": str(failure)})
                        continue
                    if local.candidate_id in attempted or not engine._candidate_rebuild_verified(registry, local, {}):
                        attempted.add(local.candidate_id)
                        continue
                    candidate = local
                attempted.add(candidate.candidate_id)
                proposals.append({"family": family, "candidate": candidate, "attempts": attempts, "seed": SEEDS[family][lane]})
            futures = {executor.submit(engine._worker_evaluate, row["candidate"].to_dict()): row for row in proposals}
            results = [(futures[future], future.result()) for future in concurrent.futures.as_completed(futures)]
            for item, worker in sorted(results, key=lambda value: value[0]["candidate"].candidate_id):
                if worker.get("system_error") or worker.get("memory_error"):
                    raise RuntimeError("REPAIRABLE_FAULT:WORKER:" + str(worker.get("error")))
                if worker.get("evaluation") is None:
                    rejected.append({"status": "PAIR_REJECTED", "family": item["family"], "candidate_id": item["candidate"].candidate_id, "error": worker.get("error")})
                    continue
                family = item["family"]
                candidate = item["candidate"]
                receipt_core = {"schema_version": 1, "operation": "FRONTIER_POCKET_LOCAL_SAMPLE", "anchor_candidate_id": ANCHORS[family]["candidate_id"], "child_id": candidate.candidate_id, "family": family, "successor_near_miss_mode": successor}
                proposal = {
                    "arm": "frontier_pocket_local",
                    "seed": item["seed"],
                    "policy_key": "POCKET|" + family,
                    "generation_attempt_ordinal": int(state["generation_attempts"]),
                    "operation": "FRONTIER_POCKET_LOCAL_SAMPLE",
                    "parent_ids": [ANCHORS[family]["candidate_id"]],
                    "receipt": {**receipt_core, "receipt_sha256": _sha(receipt_core)},
                    "receipt_verified": True,
                    "expression_hash_verified": True,
                    "policy_state_hash_before": _sha({"family": family, "before": len(ledger)}),
                    "policy_state_hash_after_proposal": _sha({"family": family, "candidate": candidate.candidate_id}),
                    "proposal_cpu_seconds": 0.0,
                }
                _observe_candidate(candidate=candidate, evaluation=worker["evaluation"], proposal=proposal, worker=worker, archive=archive, policy=None, state=state, ledger=ledger, checkpoint_index=checkpoint_index)
                classification, similarity = classify_against_anchor(anchor_rows[family], ledger[-1])
                expected_fields = tuple(anchors[family].raw_fields)
                binding_class = "EXACT_ANCHOR_BINDING" if tuple(candidate.raw_fields) == expected_fields else "SAME_SOURCE_OR_VENUE_NEIGHBOR"
                ledger[-1].update({"semantic_lane": family, "pocket_classification": classification, "economic_similarity_to_anchor": similarity, "concrete_realization_id": realization_id(ledger[-1]), "binding_class": binding_class, "successor_near_miss_mode": successor})
                state["arm_counters"]["frontier_pocket_local"]["exact_unique"] += 1
        state["attempted_exact_ids"] = sorted(attempted)
        state["strict_evaluated"] = len(ledger)
        state["next_checkpoint_index"] = checkpoint_index + 1
        state["wall_elapsed_seconds"] = float(state.get("wall_elapsed_seconds", 0.0)) + time.perf_counter() - started
        current = {family: _pocket_stats(ledger, family, anchor_rows[family]) for family in (P5, P6)}
        previous_boundary = max(0, len(ledger) - CHECKPOINT_SIZE)
        interval = {family: _pocket_stats(ledger, family, anchor_rows[family], start=previous_boundary) for family in (P5, P6)}
        for family in tuple(live):
            saturation[family] = saturation[family] + 1 if interval[family]["anchor_pocket_matched"] == 0 and interval[family]["new_concrete_realizations"] == 0 else 0
            if saturation[family] >= 2:
                live.discard(family)
        decision = {"strict": len(ledger), "live_before_scale_decision": sorted(live), "cumulative": current, "interval": interval, "saturation_intervals": dict(saturation), "successor_near_miss_mode": successor}
        if len(ledger) == 2_000:
            live = {family for family in live if current[family]["anchor_pocket_matched"] > 0 or current[family]["local_new_basin_matched"] > 0 or current[family]["near_miss"] >= 5}
            next_total = 4_000 if live else 2_000
            scale_phase_end = next_total
        elif len(ledger) == 4_000:
            live = {family for family in live if current[family]["anchor_pocket_matched"] >= 1 and current[family]["new_concrete_realizations"] >= 1}
            scale_phase_end = 10_000 if live else 4_000
            next_total = min(len(ledger) + CHECKPOINT_SIZE, scale_phase_end)
        elif len(ledger) == 10_000:
            live = {family for family in live if interval[family]["anchor_pocket_matched"] > 0 or interval[family]["new_concrete_realizations"] > 0}
            scale_phase_end = 20_000 if live else 10_000
            next_total = min(len(ledger) + CHECKPOINT_SIZE, scale_phase_end)
        elif len(ledger) >= 20_000:
            next_total = len(ledger)
        else:
            next_total = min(len(ledger) + CHECKPOINT_SIZE, scale_phase_end)
        if not live and len(ledger) <= 10_000 and not successor:
            scores = {family: current[family]["near_miss"] for family in (P5, P6)}
            chosen = max(scores, key=lambda family: (scores[family], family))
            if scores[chosen] > 0 and len(ledger) + 2_000 <= STRICT_CAP:
                successor = True
                live = {chosen}
                next_total = len(ledger) + 2_000
                scale_phase_end = next_total
                decision["near_miss_autopsy"] = {"status": "ZERO_NEW_STRICT_AUTOPSY_COMPLETE", "selected_successor_family": chosen, "near_miss_count": scores[chosen]}
        stage_decisions.append(decision)
        engine._write_json(runtime_root / f"stage_decision_{len(ledger):06d}.json", decision)
        _write_checkpoint(runtime_root, checkpoint_index=checkpoint_index, state=state, policies={}, ledger=ledger, archive=archive, pair_rows=[], metrics=[], rejected=rejected, identities=identities, discovery_diagnostic=decision)
        if next_total <= len(ledger) or not live:
            terminal = "POCKET_SATURATED" if any(value >= 2 for value in saturation.values()) else "FRONTIER_POCKET_EVIDENCE_STOP"
            return _final(runtime_root, terminal=terminal, state=state, ledger=ledger, archive=archive, anchor_rows=anchor_rows, assurance=assurance, stage_decisions=stage_decisions)
        remaining = next_total - len(ledger)
        total_weight = sum(max(current[family]["anchor_pocket_matched"], 1) for family in live)
        allocated = 0
        stage_target = {P5: Counter(str(row.get("program_family_id")) for row in ledger)[P5], P6: Counter(str(row.get("program_family_id")) for row in ledger)[P6]}
        ordered = sorted(live)
        for family in ordered[:-1]:
            share = remaining * max(current[family]["anchor_pocket_matched"], 1) // total_weight
            stage_target[family] += share
            allocated += share
        stage_target[ordered[-1]] += remaining - allocated
        target_total = next_total
        checkpoint_index += 1
        started = time.perf_counter()
    return _final(runtime_root, terminal="FRONTIER_POCKET_20000_HARD_CAP", state=state, ledger=ledger, archive=archive, anchor_rows=anchor_rows, assurance=assurance, stage_decisions=stage_decisions)


def run(repo_root: Path, *, runtime_id: str) -> dict[str, Any]:
    root = repo_root.resolve()
    authorization = validate_authorization(root)
    if runtime_id != authorization.get("runtime_id"):
        raise RuntimeError("FAIL_CLOSED_BEFORE_MARKET_READ:runtime_id")
    runtime_root = root / "runtime" / runtime_id
    if runtime_root.exists():
        raise RuntimeError("FAIL_CLOSED_BEFORE_MARKET_READ:runtime_exists")
    runtime_root.mkdir(parents=True)
    market = verify_successor_market_inputs(root)
    baseline, pool = _load_frozen_inputs(root)
    assurance = engine._read_json(root / ASSURANCE_PATH)
    frontier_path = root / str(authorization["frontier_source"]["relative_ledger_path"])
    anchor_rows = load_anchor_rows(frontier_path)
    config = json.loads(json.dumps(engine._read_json(root / CONFIG_PATH)))
    config["search_budget"].update({"strict_evaluated_maximum": STRICT_CAP, "raw_generation_attempts_maximum": RAW_ATTEMPT_CAP, "checkpoint_count_maximum": STRICT_CAP // CHECKPOINT_SIZE})
    economic = resolve_search_economic_receipt(root, str(config["source_authorities"]["economic_receipt_template"]))
    train = dict(economic["evidence_partition"]["train"])
    validate_pair_evaluation_request(block_start=str(train["start"]), block_end=str(train["end_exclusive"]), block_role=PAIRED_DIAGNOSTIC_BLOCK_ROLE, economic_receipt=economic, include_paired_diagnostic_paths=True)
    _, contracts, behavior, identities, _ = engine._load_v14_inputs(root, behavior_window=train)
    registry = engine.TypedExpressionRegistry(contracts, **_limits(config))
    anchors = rebuild_anchors(registry, anchor_rows)
    source_sha = _git(root, "rev-parse", "HEAD").lower()
    claim = {"schema_version": 1, "status": "ONE_TIME_FRONTIER_POCKET_MATURATION_LAUNCHED", "authorization_sha256": authorization["authorization_sha256"], "source_sha": source_sha, "runtime_id": runtime_id, "strict_at_claim": 0, "validation_reads": 0, "oos_reads": 0, "sealed_reads": 0}
    engine._write_json(runtime_root / "launch_claim.json", claim)
    frozen = {"schema_version": 1, "execution_mode": EXECUTION_MODE, "source_sha": source_sha, "authorization_sha256": authorization["authorization_sha256"], "assurance_receipt_sha256": assurance["assurance_receipt_sha256"], "frontier_ledger_sha256": authorization["frontier_source"]["ledger_sha256"], "ledger_sha256": baseline["source_ledger_sha256"], "parent_pool_sha256": pool["target_parent_pool_sha256"], "market_preflight_sha256": _sha(market), "lane_seeds": SEEDS, "input_identities": identities, "validation_reads": 0, "oos_reads": 0, "holdout_reads": 0, "forward_reads": 0, "promotion_reads": 0, "sealed_reads": 0}
    frozen_hash = _sha(frozen)
    engine._write_json(runtime_root / "frozen_contract.json", {**frozen, "frozen_contract_sha256": frozen_hash})
    engine._write_json(runtime_root / "authorization_snapshot.json", authorization)
    engine._write_json(runtime_root / "assurance_snapshot.json", assurance)
    engine._write_json(runtime_root / "market_input_preflight.json", market)
    engine._write_json(runtime_root / "effective_config.json", config)
    block_contract = engine._read_json(root / "config/crypto_p1_g2_block_robust_ordering_v2.json")
    cache_root = root / str(identities["raw_cache"]["root"])
    with concurrent.futures.ProcessPoolExecutor(max_workers=WORKERS, initializer=engine._worker_initialize, initargs=(str(cache_root), engine._contracts_payload(contracts), behavior, str(train["start"]), str(train["end_exclusive"]), PAIRED_DIAGNOSTIC_BLOCK_ROLE, economic, True, block_contract, str(runtime_root / "process_evidence"), _limits(config))) as executor:
        return _execute(runtime_root, source_sha=source_sha, frozen_hash=frozen_hash, identities=identities, registry=registry, anchors=anchors, anchor_rows=anchor_rows, assurance=assurance, executor=executor)


__all__ = ["AUTHORIZATION_PATH", "ASSURANCE_PATH", "EXECUTION_MODE", "REQUIRED_EXECUTION_COMPONENT_PATHS", "authorization_content_sha", "preflight", "run", "validate_authorization"]
