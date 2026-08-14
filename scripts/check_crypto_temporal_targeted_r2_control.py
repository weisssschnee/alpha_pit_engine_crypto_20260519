from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping

import pandas as pd

from alphafactory_crypto.broad_search import search_engine_v1 as engine
from alphafactory_crypto.broad_search import temporal_program_search_v1 as runner
from alphafactory_crypto.broad_search.temporal_program_v1 import (
    compile_temporal_program_catalog,
)
from alphafactory_crypto.broad_search.temporal_targeted_deepening_v1 import (
    ACTIVE_PROGRAM_FAMILIES,
    AUTHORIZATION_PATH,
    BASELINE_ROW_FIELDS,
    ECONOMIC_FINGERPRINT_FIELDS,
    build_frozen_target_parent_pool,
    file_sha256,
    load_diagnostic_baseline,
    validate_authorization,
    _realization_id,
)


IMPLEMENTATION_SHA = "46a8dd48f1dc0183ba590bd67edc17f7e62cd359"
RUNTIME_ID = "crypto_temporal_targeted_p1_p4_basin_deepening_v1_20260813r3"
PARENT_POOL_SHA256 = (
    "A08112ED1765A432D15D259A70F308C2DE5BA7B617D294BFB8349020EC61AA49"
)
CONTROL_PATHS = {
    ".planning/STATE.md",
    ".planning/graphs/current.html",
    ".planning/graphs/current.json",
    "config/architecture_overlay.json",
    AUTHORIZATION_PATH,
    "scripts/check_crypto_temporal_targeted_r2_control.py",
}
OPERATION_NAMES = {
    "MECHANISM_PARAMETER_GROUP_MUTATION_1_TO_3": "parameter_mutation",
    "COMPATIBLE_MECHANISM_SPEC_MUTATION": "mechanism_mutation",
    "ONE_POINT_TYPED_MECHANISM_CROSSOVER": "crossover",
}


class _TracedProposalFailure(Exception):
    def __init__(self, cause: Exception, audit: Mapping[str, Any]) -> None:
        super().__init__(str(cause))
        self.cause = cause
        self.audit = dict(audit)


def _git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()


def _blob_oid_at(root: Path, revision: str, path: str) -> str:
    return _git(root, "rev-parse", f"{revision}:{path}").lower()


def _normalized_worktree_blob_oid(root: Path, path: str) -> str:
    return subprocess.check_output(
        ["git", "hash-object", f"--path={path}", str(root / path)],
        cwd=root,
        text=True,
    ).strip().lower()


def _json_sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            default=str,
        ).encode("utf-8")
    ).hexdigest().upper()


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def premarket(root: Path, output: Path) -> dict[str, Any]:
    root = root.resolve()
    head = _git(root, "rev-parse", "HEAD").lower()
    branch = _git(root, "branch", "--show-current")
    tracking = _git(root, "rev-parse", f"origin/{branch}").lower()
    status = _git(root, "status", "--porcelain=v1", "--untracked-files=all")
    authorization = validate_authorization(root, expected_source_sha=head)
    baseline = load_diagnostic_baseline(root, authorization)
    pool = build_frozen_target_parent_pool(root, baseline)

    changed = {
        value
        for value in _git(root, "diff", "--name-only", IMPLEMENTATION_SHA, head).splitlines()
        if value
    }
    component_errors = []
    component_identity = []
    expected_components = dict(authorization.get("execution_component_git_identities") or {})
    for path, expected in expected_components.items():
        at_implementation = _blob_oid_at(root, IMPLEMENTATION_SHA, path)
        at_head = _blob_oid_at(root, head, path)
        observed = _normalized_worktree_blob_oid(root, path)
        match = expected == at_implementation == at_head == observed
        component_identity.append({
            "path": path,
            "expected_committed_blob_oid": expected,
            "observed_normalized_worktree_blob_oid": observed,
            "match": match,
        })
        if not match:
            component_errors.append(path)

    ledger_path = root / baseline["source_ledger_path"]
    ledger = pd.read_parquet(ledger_path)
    source_by_id = {
        str(row["candidate_id"]): row for row in ledger.to_dict("records")
    }
    source_mismatches = []
    for baseline_row in baseline["matched_positive_rows"]:
        source_row = source_by_id.get(str(baseline_row["candidate_id"]))
        if source_row is None:
            source_mismatches.append([baseline_row["candidate_id"], "missing"])
            continue
        for field in BASELINE_ROW_FIELDS:
            left = baseline_row.get(field)
            right = source_row.get(field)
            if pd.isna(left) and pd.isna(right):
                continue
            if str(left) != str(right):
                source_mismatches.append([baseline_row["candidate_id"], field])

    expected_pool = dict(authorization.get("frozen_parent_pool_identity") or {})
    expected_accounting = dict(authorization.get("operation_accounting") or {})
    errors = []
    if head != tracking or status:
        errors.append("checkout_or_tracking_not_clean")
    if str(authorization.get("authorized_implementation_sha") or "").lower() != IMPLEMENTATION_SHA:
        errors.append("implementation_sha")
    if changed - CONTROL_PATHS:
        errors.append("non_control_plane_diff")
    if set(expected_components) != set(authorization["authorized_component_sha256"]):
        errors.append("execution_component_identity_set")
    if component_errors:
        errors.append("EXECUTION_COMPONENT_DRIFT")
    if len(ledger) != 50_000 or file_sha256(ledger_path) != str(
        baseline["source_ledger_sha256"]
    ):
        errors.append("baseline_ledger_identity")
    if int(baseline["matched_positive_count"]) != 302 or source_mismatches:
        errors.append("baseline_parent_recovery")
    if (
        int(pool["target_basin_count"]) != 23
        or int(pool["frozen_parent_candidate_count"]) != 228
        or str(pool["target_parent_pool_sha256"]) != PARENT_POOL_SHA256
        or expected_pool
        != {
            "baseline_matched_positive_count": 302,
            "frozen_parent_candidate_count": 228,
            "source_ledger_row_count": 50_000,
            "source_ledger_sha256": str(baseline["source_ledger_sha256"]),
            "target_basin_count": 23,
            "target_parent_pool_sha256": PARENT_POOL_SHA256,
        }
    ):
        errors.append("frozen_parent_pool_identity")
    if {row["program_family_id"] for row in pool["target_basins"]} != set(
        ACTIVE_PROGRAM_FAMILIES
    ):
        errors.append("program_family_scope")
    if any(int(pool[key]) != 0 for key in (
        "market_arrays_read", "candidate_evaluations", "validation_reads", "oos_reads", "sealed_reads"
    )):
        errors.append("premarket_read_boundary")
    if expected_accounting.get("checker_path") != "scripts/check_crypto_temporal_targeted_r2_control.py":
        errors.append("operation_accounting_contract")
    preauthorization = dict(authorization.get("preauthorization_deployment_receipt") or {})
    receipt_path = Path(str(preauthorization.get("path") or ""))
    try:
        receipt = engine._read_json(receipt_path)
    except (OSError, ValueError, json.JSONDecodeError):
        errors.append("preauthorization_deployment_receipt")
    else:
        if (
            file_sha256(receipt_path) != str(preauthorization.get("sha256") or "")
            or receipt.get("status") != preauthorization.get("status")
            or receipt.get("evidence_sha256") != preauthorization.get("evidence_sha256")
        ):
            errors.append("preauthorization_deployment_receipt")
    if (root / f"runtime/{RUNTIME_ID}").exists():
        errors.append("non_fresh_r2_runtime")

    core = {
        "schema_version": 1,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "branch": branch,
        "head": head,
        "tracking": tracking,
        "worktree_clean": not bool(status),
        "implementation_sha": IMPLEMENTATION_SHA,
        "changed_paths_since_implementation": sorted(changed),
        "execution_component_count": len(authorization["authorized_component_sha256"]),
        "execution_component_identity": component_identity,
        "execution_component_errors": component_errors,
        "baseline_ledger_sha256": file_sha256(ledger_path),
        "baseline_ledger_rows": len(ledger),
        "baseline_matched_positive_count": int(baseline["matched_positive_count"]),
        "baseline_source_field_mismatch_count": len(source_mismatches),
        "target_basin_count": int(pool["target_basin_count"]),
        "frozen_parent_candidate_count": int(pool["frozen_parent_candidate_count"]),
        "target_parent_pool_sha256": str(pool["target_parent_pool_sha256"]),
        "program_families": sorted({row["program_family_id"] for row in pool["target_basins"]}),
        "market_arrays_read": 0,
        "candidate_evaluations": 0,
        "validation_reads": 0,
        "oos_reads": 0,
        "sealed_reads": 0,
    }
    payload = {**core, "evidence_sha256": _json_sha(core)}
    _write_json(output, payload)
    if errors:
        raise RuntimeError("FAIL_CLOSED_BEFORE_MARKET_READ:" + ",".join(errors))
    return payload


def _requested_operation(draw: float, parameters: Mapping[str, Any]) -> str:
    parameter = float(parameters["parameter_mutation_probability"])
    mechanism = float(parameters["mechanism_mutation_probability"])
    if draw < parameter:
        return "parameter_mutation"
    if draw < parameter + mechanism:
        return "mechanism_mutation"
    return "crossover"


def _trace_targeted_proposal(
    policy: engine.MechanismEvolutionV2,
) -> tuple[Any, dict[str, Any], dict[str, Any]]:
    before = policy.state_hash()
    limit = int(policy.parameters.get("duplicate_resample_limit", 64))
    for duplicate_attempt in range(1, limit + 2):
        basin_id = policy._next_targeted_basin()
        first = policy._next_targeted_parent(basin_id)
        draw = policy.rng.random()
        requested = _requested_operation(draw, policy.parameters)
        fallback_reason = None
        try:
            if requested == "parameter_mutation":
                child, receipt = policy._mutate_parameters(first)
                parents = (first,)
            elif requested == "mechanism_mutation":
                child, receipt = policy._mutate_mechanism(first)
                parents = (first,)
            else:
                second = policy._targeted_crossover_parent(basin_id, first)
                if second is None:
                    child, receipt = policy._mutate_parameters(first)
                    parents = (first,)
                    fallback_reason = "NO_COMPATIBLE_SAME_BASIN_PARENT"
                else:
                    try:
                        child, receipt = policy._crossover(first, second)
                        parents = (first, second)
                    except engine._ProposalGenerationFailure:
                        child, receipt = policy._mutate_parameters(first)
                        parents = (first,)
                        fallback_reason = "CROSSOVER_PROPOSAL_GENERATION_FAILURE"
        except (ValueError, RuntimeError, engine._ProposalGenerationFailure) as failure:
            raise _TracedProposalFailure(
                failure,
                {
                    "requested_operation": requested,
                    "realized_operation": None,
                    "crossover_fallback": False,
                    "fallback_reason": None,
                    "proposal_failure": type(failure).__name__ + ":" + str(failure),
                    "targeted_economic_basin_id": basin_id,
                },
            ) from failure
        receipt = policy._bind_targeted_receipt(receipt, basin_id=basin_id, parents=parents)
        if child.candidate_id in policy.seen:
            continue
        if not policy.verify_receipt(parents, child, receipt):
            raise RuntimeError("replayed targeted receipt verification failed")
        policy.seen.add(child.candidate_id)
        policy.step += 1
        metadata = {
            "policy_state_hash_before": before,
            "operation": str(receipt["operation"]),
            "parent_ids": [value.candidate_id for value in parents],
            "receipt": receipt,
            "receipt_verified": True,
            "raw_attempts": duplicate_attempt
            + int(receipt.get("internal_generation_attempts", 1))
            - 1,
            "compile_valid_attempts": int(receipt.get("compile_valid_attempts", 1)),
            "targeted_economic_basin_id": basin_id,
            "targeted_parent_pool_sha256": str(
                policy.targeted_parent_pool_payload["target_parent_pool_sha256"]
            ),
        }
        audit = {
            "requested_operation": requested,
            "realized_operation": OPERATION_NAMES[str(receipt["operation"])],
            "crossover_fallback": fallback_reason is not None,
            "fallback_reason": fallback_reason,
            "targeted_economic_basin_id": basin_id,
        }
        return child, metadata, audit
    raise engine._ProposalGenerationFailure(
        "targeted mechanism evolution duplicate resample limit exhausted",
        raw_attempts=limit + 1,
    )


def _initial_evolution_policies(root: Path, pool: Mapping[str, Any]) -> dict[str, Any]:
    base = engine._read_json(root / runner.CONFIG_PATH)
    config = runner._targeted_effective_config(base)
    contracts = runner._contracts_from_manifest(root, config)
    registry = runner.TypedExpressionRegistry(contracts, **runner._limits(config))
    catalog = compile_temporal_program_catalog(config)
    policies = runner._later_policies(
        registry=registry,
        config=config,
        catalog=catalog,
        active_families=ACTIVE_PROGRAM_FAMILIES,
    )
    selected = {
        key: policy
        for key, policy in policies.items()
        if key.startswith("temporal_program_evolution|")
    }
    for policy in selected.values():
        policy.configure_targeted_parent_pool(pool)
    return selected


def _observe_replayed_strict_rows(
    policy: engine.MechanismEvolutionV2,
    rows: list[Mapping[str, Any]],
) -> None:
    for row in sorted(rows, key=lambda value: int(value["completion_ordinal"])):
        archive_row = dict(row)
        block_ordering = row.get("block_robust_ordering_json")
        archive_row["block_robust_ordering"] = (
            json.loads(str(block_ordering))
            if block_ordering is not None and not pd.isna(block_ordering)
            else None
        )
        candidate = engine.CandidateSpec.from_dict(
            json.loads(str(row["candidate_spec_json"]))
        )
        policy.observe(candidate, archive_row)


def verify_operation_tracer(root: Path, count_per_lane: int) -> dict[str, Any]:
    authorization = engine._read_json(root / AUTHORIZATION_PATH)
    baseline = load_diagnostic_baseline(root, authorization)
    pool = build_frozen_target_parent_pool(root, baseline)
    policies = _initial_evolution_policies(root, pool)
    checked = 0
    for policy in policies.values():
        traced = copy.deepcopy(policy)
        canonical = copy.deepcopy(policy)
        for _ in range(count_per_lane):
            try:
                left, left_meta, _ = _trace_targeted_proposal(traced)
                left_failure = None
            except _TracedProposalFailure as failure:
                left = left_meta = None
                left_failure = failure
            try:
                right, right_meta = canonical.propose()
                right_failure = None
            except (ValueError, RuntimeError, engine._ProposalGenerationFailure) as failure:
                right = right_meta = None
                right_failure = failure
            if (left_failure is None) != (right_failure is None):
                raise RuntimeError("operation tracer success/failure diverged")
            if left_failure is not None and right_failure is not None:
                if (
                    type(left_failure.cause) is not type(right_failure)
                    or str(left_failure.cause) != str(right_failure)
                ):
                    raise RuntimeError("operation tracer failure diverged")
            elif (
                left.candidate_id != right.candidate_id
                or left_meta["operation"] != right_meta["operation"]
                or left_meta["receipt"] != right_meta["receipt"]
            ):
                raise RuntimeError("operation tracer proposal diverged")
            if traced.export_state() != canonical.export_state():
                raise RuntimeError("operation tracer state diverged")
            checked += 1
    return {"status": "PASS", "lanes": len(policies), "proposals_checked": checked}


def postrun(root: Path, output: Path) -> dict[str, Any]:
    authorization = engine._read_json(root / AUTHORIZATION_PATH)
    runtime = root / f"runtime/{RUNTIME_ID}"
    baseline = load_diagnostic_baseline(root, authorization)
    pool = build_frozen_target_parent_pool(root, baseline)
    ledger = pd.read_parquet(runtime / "candidate_ledger.parquet")
    rejected = pd.read_parquet(runtime / "rejected_candidate_ledger.parquet")
    final = engine._read_json(runtime / "final_decision.json")
    checker = engine._read_json(runtime / "independent_checker.json")
    frozen_runtime = engine._read_json(runtime / "targeted_frozen_parent_pool.json")
    errors = []
    if frozen_runtime != pool:
        errors.append("runtime_parent_pool_not_independently_reconstructed")
    if checker.get("status") != "PASS":
        errors.append("canonical_independent_checker")
    if set(str(value) for value in ledger["program_family_id"]) - set(
        ACTIVE_PROGRAM_FAMILIES
    ):
        errors.append("program_family_scope")
    diagnostics = dict(final.get("targeted_deepening_diagnostics") or {})
    if (
        bool(final.get("validation"))
        or bool(final.get("oos"))
        or int(final.get("sealed_reads", -1)) != 0
        or any(
            int(diagnostics.get(key, -1)) != 0
            for key in ("validation_reads", "oos_reads", "sealed_reads")
        )
    ):
        errors.append("sealed_evaluation_boundary")

    proposal_rows = []
    for path in sorted((runtime / "process_evidence").glob("producer_batch_*.json")):
        payload = engine._read_json(path)
        for slot, row in enumerate(payload.get("proposals", ())):
            if str(row.get("arm") or "") == "temporal_program_evolution":
                proposal_rows.append(
                    {
                        **dict(row),
                        "checkpoint_index": int(payload["checkpoint_index"]),
                        "evaluation_batch_index": int(payload["evaluation_batch_index"]),
                        "batch_slot": slot,
                    }
                )
    proposal_rows.sort(
        key=lambda row: (
            int(row["checkpoint_index"]),
            int(row["evaluation_batch_index"]),
            int(row["batch_slot"]),
        )
    )
    observed_by_checkpoint_lane: dict[tuple[int, str], list[dict[str, Any]]] = defaultdict(list)
    for row in proposal_rows:
        observed_by_checkpoint_lane[
            (int(row["checkpoint_index"]), str(row["policy_key"]))
        ].append(row)

    rejected_evolution = rejected.loc[
        rejected.get("policy_key", pd.Series(dtype=str))
        .fillna("")
        .astype(str)
        .str.startswith("temporal_program_evolution|")
    ]
    exact_reject_ids = Counter(
        str(value)
        for value in rejected_evolution.loc[
            rejected_evolution["status"].astype(str).eq("EXACT_OR_REPLAY_REJECT"),
            "candidate_id",
        ].dropna()
    )
    expected_proposal_rejects = int(
        rejected_evolution["status"].astype(str).eq("PROPOSAL_REJECT").sum()
    )
    policies = _initial_evolution_policies(root, pool)
    trace_rows = []
    strict_by_id = {
        str(row["candidate_id"]): row
        for row in ledger.loc[
            ledger["arm"].astype(str).eq("temporal_program_evolution")
        ].to_dict("records")
    }
    proposal_rejects = 0
    consumed_exact_rejects: Counter[str] = Counter()
    checkpoints = sorted(int(value) for value in ledger["checkpoint_index"].unique())
    for checkpoint_index in checkpoints:
        for policy_key, policy in sorted(policies.items()):
            observed = observed_by_checkpoint_lane.get((checkpoint_index, policy_key), [])
            pending_strict_rows: list[Mapping[str, Any]] = []
            pending_batch_index: int | None = None
            for expected in observed:
                batch_index = int(expected["evaluation_batch_index"])
                if (
                    pending_batch_index is not None
                    and batch_index != pending_batch_index
                ):
                    _observe_replayed_strict_rows(
                        policy, pending_strict_rows
                    )
                    pending_strict_rows = []
                pending_batch_index = batch_index
                for _ in range(100_000):
                    try:
                        candidate, metadata, audit = _trace_targeted_proposal(policy)
                    except _TracedProposalFailure as failure:
                        proposal_rejects += 1
                        trace_rows.append(
                            {
                                **failure.audit,
                                "checkpoint_index": checkpoint_index,
                                "policy_key": policy_key,
                                "seed": int(policy_key.rsplit("|", 1)[1]),
                                "candidate_id": None,
                                "realized_operation_raw": None,
                                "submitted": False,
                                "strict": False,
                                "matched_positive": False,
                            }
                        )
                        continue
                    traced = {
                        **audit,
                        "checkpoint_index": checkpoint_index,
                        "policy_key": policy_key,
                        "seed": int(policy_key.rsplit("|", 1)[1]),
                        "candidate_id": candidate.candidate_id,
                        "realized_operation_raw": str(metadata["operation"]),
                        "submitted": False,
                        "strict": False,
                        "matched_positive": False,
                    }
                    trace_rows.append(traced)
                    if candidate.candidate_id == str(expected["candidate_id"]):
                        traced["submitted"] = True
                        if str(metadata["operation"]) != str(expected["operation"]):
                            errors.append("process_evidence_realized_operation")
                        strict_row = strict_by_id.get(candidate.candidate_id)
                        if strict_row is not None and (
                            str(strict_row.get("operation") or "")
                            != str(metadata["operation"])
                            or str(strict_row.get("policy_state_hash_before") or "")
                            != str(metadata["policy_state_hash_before"])
                        ):
                            errors.append("strict_ledger_replay_identity")
                        if strict_row is not None:
                            traced["strict"] = True
                            traced["matched_positive"] = bool(
                                strict_row.get("matched_positive", False)
                            )
                            pending_strict_rows.append(strict_row)
                        break
                    consumed_exact_rejects[candidate.candidate_id] += 1
                    if consumed_exact_rejects[candidate.candidate_id] > exact_reject_ids[
                        candidate.candidate_id
                    ]:
                        errors.append("unexplained_unsubmitted_proposal")
                        break
                else:
                    errors.append("proposal_replay_limit")
            _observe_replayed_strict_rows(policy, pending_strict_rows)
    if consumed_exact_rejects != exact_reject_ids:
        errors.append("exact_reject_reconciliation")
    if proposal_rejects != expected_proposal_rejects:
        errors.append("proposal_reject_reconciliation")
    if len(proposal_rows) != sum(bool(row["submitted"]) for row in trace_rows):
        errors.append("submitted_proposal_reconciliation")

    baseline_by_id = {
        str(row["candidate_id"]): row for row in baseline["matched_positive_rows"]
    }
    basin_baseline: dict[str, list[Mapping[str, Any]]] = {}
    for basin in pool["target_basins"]:
        basin_baseline[str(basin["economic_similarity_cluster_id"])] = [
            baseline_by_id[str(candidate_id)]
            for candidate_id in basin["member_candidate_ids"]
        ]
    dimension_fields = {
        "mapped_weight": "mapped_weight_descriptor_id",
        "turnover": "turnover_path_descriptor_id",
        "raw_field": "raw_fields_json",
        "asset_selection": "selected_asset_overlap_id",
    }
    baseline_sets = {
        basin_id: {
            dimension: {str(row.get(field) or "NOT_AVAILABLE") for row in rows}
            for dimension, field in dimension_fields.items()
        }
        for basin_id, rows in basin_baseline.items()
    }
    baseline_realizations = {
        basin_id: {_realization_id(row) for row in rows}
        for basin_id, rows in basin_baseline.items()
    }
    operation_summary: dict[str, dict[str, Any]] = {}
    for operation in ("parameter_mutation", "mechanism_mutation", "crossover"):
        local_trace = [row for row in trace_rows if row["realized_operation"] == operation]
        strict_ids = {row["candidate_id"] for row in local_trace if row["strict"]}
        matched_rows = [strict_by_id[value] for value in strict_ids if bool(strict_by_id[value].get("matched_positive", False))]
        deepened = set()
        for row in matched_rows:
            receipt = json.loads(str(row.get("receipt_json") or "{}"))
            basin_id = str(receipt.get("targeted_economic_basin_id") or "")
            if basin_id not in baseline_sets:
                errors.append("matched_parent_basin_identity")
                continue
            if _realization_id(row) not in baseline_realizations[basin_id] or any(
                str(row.get(field) or "NOT_AVAILABLE") not in baseline_sets[basin_id][dimension]
                for dimension, field in dimension_fields.items()
            ):
                deepened.add(basin_id)
        operation_summary[operation] = {
            "proposal_count": len(local_trace),
            "submitted_count": sum(bool(row["submitted"]) for row in local_trace),
            "strict_count": len(strict_ids),
            "matched_positive_count": len(matched_rows),
            "basin_deepening_contribution_count": len(deepened),
            "basin_ids": sorted(deepened),
        }

    requested_counts = Counter(row["requested_operation"] for row in trace_rows)
    realized_counts = Counter(
        row["realized_operation"]
        for row in trace_rows
        if row["realized_operation"] is not None
    )
    fallback_reasons = Counter(
        str(row["fallback_reason"])
        for row in trace_rows
        if bool(row["crossover_fallback"])
    )
    requested_crossovers = int(requested_counts["crossover"])
    fallback_count = sum(fallback_reasons.values())
    matched_all = ledger.loc[ledger["matched_positive"].fillna(False).astype(bool)]
    current_sets = {
        basin_id: {dimension: set(values) for dimension, values in dimensions.items()}
        for basin_id, dimensions in baseline_sets.items()
    }
    current_realizations = {key: set(value) for key, value in baseline_realizations.items()}
    deepened_basins = set()
    for row in matched_all.to_dict("records"):
        receipt = json.loads(str(row.get("receipt_json") or "{}"))
        basin_id = str(receipt.get("targeted_economic_basin_id") or "")
        if basin_id not in current_sets:
            continue
        before = sum(len(values) for values in current_sets[basin_id].values()) + len(current_realizations[basin_id])
        for dimension, field in dimension_fields.items():
            current_sets[basin_id][dimension].add(str(row.get(field) or "NOT_AVAILABLE"))
        current_realizations[basin_id].add(_realization_id(row))
        after = sum(len(values) for values in current_sets[basin_id].values()) + len(current_realizations[basin_id])
        if after > before:
            deepened_basins.add(basin_id)
    depth_increments = {
        dimension: sum(
            len(current_sets[basin_id][dimension]) - len(baseline_sets[basin_id][dimension])
            for basin_id in baseline_sets
        )
        for dimension in dimension_fields
    }
    new_realizations = sum(
        len(current_realizations[basin_id] - baseline_realizations[basin_id])
        for basin_id in baseline_realizations
    )
    trace_frame = pd.DataFrame(trace_rows)
    trace_path = output.with_name("operation_trace.parquet")
    trace_frame.to_parquet(trace_path, index=False)
    core = {
        "schema_version": 1,
        "status": "PASS" if not errors else "FAIL",
        "errors": sorted(set(errors)),
        "runtime_id": RUNTIME_ID,
        "implementation_sha": IMPLEMENTATION_SHA,
        "target_parent_pool_sha256": PARENT_POOL_SHA256,
        "requested_operation_counts": dict(sorted(requested_counts.items())),
        "realized_operation_counts": dict(sorted(realized_counts.items())),
        "crossover_requested_count": requested_crossovers,
        "crossover_fallback_count": fallback_count,
        "crossover_fallback_rate": fallback_count / max(requested_crossovers, 1),
        "crossover_fallback_reasons": dict(sorted(fallback_reasons.items())),
        "operation_attribution": operation_summary,
        "target_basin_count": 23,
        "actual_deepened_basin_count": len(deepened_basins),
        "actual_deepened_basin_ids": sorted(deepened_basins),
        "new_concrete_realizations": new_realizations,
        "depth_increments": depth_increments,
        "proposal_generation_failure_count": proposal_rejects,
        "trace_row_count": len(trace_rows),
        "operation_trace_path": trace_path.relative_to(root).as_posix(),
        "validation_reads": int(diagnostics.get("validation_reads", 0)),
        "oos_reads": int(diagnostics.get("oos_reads", 0)),
        "sealed_reads": int(final.get("sealed_reads", 0)),
    }
    payload = {**core, "evidence_sha256": _json_sha(core)}
    _write_json(output, payload)
    if errors:
        raise RuntimeError("TARGETED_R3_CONTROL_CHECK_FAIL:" + ",".join(sorted(set(errors))))
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("premarket", "tracer-self-test", "postrun"))
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--count-per-lane", type=int, default=100)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    if args.mode == "premarket":
        if args.output is None:
            raise ValueError("--output is required")
        print(json.dumps(premarket(root, args.output), sort_keys=True))
    elif args.mode == "tracer-self-test":
        print(json.dumps(verify_operation_tracer(root, args.count_per_lane), sort_keys=True))
    else:
        if args.output is None:
            raise ValueError("--output is required")
        print(json.dumps(postrun(root, args.output), sort_keys=True))


if __name__ == "__main__":
    main()
