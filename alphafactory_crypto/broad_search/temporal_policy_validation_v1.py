"""Frozen development validation for the Temporal Program search-policy arms.

The gate samples train-only economic behavior clusters at equal arm, family,
and lane counts, then evaluates the unchanged candidates on one untouched
development-validation partition and three equal contiguous sub-blocks.  It
never generates candidates, updates optimizer state, writes an Archive, reads
holdout/OOS data, or promotes an Alpha candidate.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, Mapping, Sequence

import pandas as pd
from alphafactory_crypto.broad_search.experiment_authority import (
    require_real_experiment_authority,
    resolve_search_economic_receipt,
)
from alphafactory_crypto.broad_search.search_engine_v2_4 import (
    _v24_checkpoint_files,
    _v24_worker_evaluate,
    _v24_worker_initialize,
    _v24_write_batch_projections,
)
from alphafactory_crypto.broad_search.search_evidence_validation_v1 import (
    _augment_projection,
)


RECEIPT_PATH = "config/crypto_temporal_policy_validation_v1_authorization.json"
RUNTIME_PREFIX = "crypto_temporal_policy_validation_v1"
DEFAULT_RUNTIME_DATE = "20260812"
ARMS = (
    "temporal_program_random",
    "temporal_program_cem",
    "temporal_program_evolution",
)
PROGRAM_FAMILIES = (
    "P1_POSITION_STATE_CHANGE_TO_RESPONSE",
    "P4_MULTISCALE_STATE_X_TRANSITION_ROUTING",
)
POLICY_VALIDATION_SCOPE = (
    "ONE_EQUAL_COUNT_TEMPORAL_POLICY_DEVELOPMENT_VALIDATION_NO_FEEDBACK"
)

def canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest().upper()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while block := handle.read(8 * 1024 * 1024):
            digest.update(block)
    return digest.hexdigest().upper()


def committed_file_sha256(repo_root: Path, relative_path: str) -> str:
    object_id = subprocess.check_output(
        ["git", "rev-parse", f"HEAD:{relative_path}"], cwd=repo_root, text=True
    ).strip()
    payload = subprocess.check_output(
        ["git", "cat-file", "blob", object_id], cwd=repo_root
    )
    return hashlib.sha256(payload).hexdigest().upper()


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".tmp-{os.getpid()}")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def _hours(start: str, end: str) -> int:
    return int((pd.Timestamp(end) - pd.Timestamp(start)).total_seconds() // 3600)


def validate_split_contract(receipt: Mapping[str, Any]) -> dict[str, Any]:
    split = dict(receipt["split_contract"])
    train = dict(split["train"])
    validation = dict(split["validation"])
    blocks = [dict(value) for value in split["validation_blocks"]]
    purge = int(split["partition_tail_purge_hours"])
    train_raw = _hours(train["start"], train["end_exclusive"])
    validation_raw = _hours(validation["start"], validation["end_exclusive"])
    train_effective = train_raw - purge
    validation_effective = validation_raw - purge
    effective_total = train_effective + validation_effective
    block_raw = [_hours(row["start"], row["end_exclusive"]) for row in blocks]
    boundaries = [train["end_exclusive"], validation["start"]]
    if (
        boundaries[0] != boundaries[1]
        or len(blocks) != 3
        or blocks[0]["start"] != validation["start"]
        or blocks[-1]["end_exclusive"] != validation["end_exclusive"]
        or any(
            blocks[index]["end_exclusive"] != blocks[index + 1]["start"]
            for index in range(2)
        )
        or len(set(block_raw)) != 1
        or train_raw != 1_529
        or validation_raw != 1_464
        or train_effective != 1_523
        or validation_effective != 1_458
        or any(value - purge != 482 for value in block_raw)
    ):
        raise RuntimeError("TEMPORAL_POLICY_VALIDATION_SPLIT_INVALID")
    train_share = train_effective / effective_total
    validation_share = validation_effective / effective_total
    if not (0.45 <= train_share <= 0.55 and 0.45 <= validation_share <= 0.55):
        raise RuntimeError("TEMPORAL_POLICY_VALIDATION_SPLIT_IMBALANCED")
    if int(split["maximum_feature_warmup_hours"]) != 720:
        raise RuntimeError("TEMPORAL_POLICY_VALIDATION_WARMUP_CHANGED")
    return {
        "train_raw_hours": train_raw,
        "validation_raw_hours": validation_raw,
        "train_effective_hours": train_effective,
        "validation_effective_hours": validation_effective,
        "train_effective_share": train_share,
        "validation_effective_share": validation_share,
        "validation_block_raw_hours": block_raw[0],
        "validation_block_effective_hours": block_raw[0] - purge,
        "maximum_feature_warmup_hours": 720,
        "warmup_rows_in_labels_or_metrics": False,
    }


def load_receipt(
    repo_root: Path,
    *,
    require_authorized: bool | None = None,
    receipt_path: str = RECEIPT_PATH,
) -> dict[str, Any]:
    path = Path(repo_root) / receipt_path
    receipt = json.loads(path.read_text(encoding="utf-8-sig"))
    blockers: list[str] = []
    if receipt.get("schema_version") != 2:
        blockers.append("schema_version")
    if receipt.get("receipt_id") != "CRYPTO_TEMPORAL_POLICY_VALIDATION_V1":
        blockers.append("receipt_id")
    if require_authorized is not None and bool(receipt.get("run_authorized")) is not bool(
        require_authorized
    ):
        blockers.append("run_authorized")
    authorization = dict(receipt.get("run_authorization") or {})
    if authorization.get("scope") != POLICY_VALIDATION_SCOPE:
        blockers.append("scope")
    if receipt.get("authorization_sha256") != canonical_sha256(
        {key: value for key, value in receipt.items() if key != "authorization_sha256"}
    ):
        blockers.append("authorization_sha256")
    selection = dict(receipt.get("selection") or {})
    if (
        int(selection.get("candidate_count_per_arm", -1)) != 120
        or int(selection.get("candidate_count_total", -1)) != 360
        or int(selection.get("candidate_count_per_family_lane", -1)) != 15
        or selection.get("program_families") != list(PROGRAM_FAMILIES)
        or len(str(selection.get("selection_sha256") or "")) != 64
    ):
        blockers.append("selection")
    compute = dict(receipt.get("compute") or {})
    if (
        int(compute.get("workers_default", -1)) != 10
        or int(compute.get("workers_fallback", -1)) != 8
        or int(compute.get("evaluation_passes", -1)) != 4
    ):
        blockers.append("compute")
    continuation = dict(receipt.get("continuation") or {})
    if (
        continuation.get("mode")
        != "REUSE_VERIFIED_FULL_PASS_EVALUATE_MISSING_BLOCKS"
        or int(continuation.get("reused_pair_evaluation_count", -1)) != 360
        or int(continuation.get("new_pair_evaluation_count", -1)) != 1_080
        or len(str(continuation.get("full_pass_candidate_ledger_sha256") or ""))
        != 64
    ):
        blockers.append("continuation")
    boundaries = dict(receipt.get("boundaries") or {})
    for key in (
        "candidate_generation",
        "optimizer_feedback",
        "policy_memory_write",
        "archive_write",
        "validation_selection",
        "backfill",
        "restart",
        "reseed",
        "parameter_tuning",
        "rescue_rerun",
        "holdout_read",
        "oos",
        "promotion",
        "automatic_search_after_qualification",
    ):
        if boundaries.get(key) is not False:
            blockers.append(key)
    validate_split_contract(receipt)
    if blockers:
        raise RuntimeError("TEMPORAL_POLICY_VALIDATION_RECEIPT_INVALID:" + ",".join(blockers))
    return receipt


def validate_execution_source(repo_root: Path, receipt: Mapping[str, Any]) -> str:
    root = Path(repo_root)
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip().lower()
    implementation = str(receipt["source_implementation_sha"]).lower()
    if subprocess.run(
        ["git", "merge-base", "--is-ancestor", implementation, head],
        cwd=root,
        check=False,
    ).returncode:
        raise RuntimeError("TEMPORAL_POLICY_VALIDATION_IMPLEMENTATION_NOT_ANCESTOR")
    changed = sorted(
        line.replace("\\", "/")
        for line in subprocess.check_output(
            ["git", "diff", "--name-only", f"{implementation}..{head}"],
            cwd=root,
            text=True,
        ).splitlines()
        if line.strip()
    )
    if changed != sorted(str(value) for value in receipt["allowed_post_implementation_paths"]):
        raise RuntimeError("TEMPORAL_POLICY_VALIDATION_POST_IMPLEMENTATION_SOURCE_DRIFT")
    if subprocess.run(["git", "diff", "--quiet"], cwd=root, check=False).returncode or subprocess.run(
        ["git", "diff", "--cached", "--quiet"], cwd=root, check=False
    ).returncode:
        raise RuntimeError("TEMPORAL_POLICY_VALIDATION_WORKTREE_DIRTY")
    for component in dict(receipt["source_components"]).values():
        if committed_file_sha256(root, str(component["path"])) != str(
            component["sha256"]
        ):
            raise RuntimeError(
                f"TEMPORAL_POLICY_VALIDATION_COMPONENT_CHANGED:{component['path']}"
            )
    return head


def _sampling_key(salt: str, row: Mapping[str, Any]) -> str:
    value = "|".join(
        (
            salt,
            str(row["arm"]),
            str(row["program_family_id"]),
            str(row["lane_index"]),
            str(row["behavior_family_id"]),
            str(row["candidate_id"]),
        )
    )
    return hashlib.sha256(value.encode("utf-8")).hexdigest().upper()


def selection_projection(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "candidate_id": str(row["candidate_id"]),
            "candidate_spec_sha256": str(row["candidate_spec_sha256"]),
            "behavior_family_id": str(row["behavior_family_id"]),
            "arm": str(row["arm"]),
            "program_family_id": str(row["program_family_id"]),
            "program_id": str(row["program_id"]),
            "seed": int(row["seed"]),
            "lane_index": int(row["lane_index"]),
            "completion_ordinal": int(row["completion_ordinal"]),
            "train_orientation": float(row["train_orientation"]),
        }
        for row in sorted(rows, key=lambda item: str(item["candidate_id"]))
    ]


def select_equal_count_cohort(
    repo_root: Path,
    *,
    receipt: Mapping[str, Any] | None = None,
    receipt_path: str = RECEIPT_PATH,
    verify_expected_hash: bool = True,
) -> list[dict[str, Any]]:
    root = Path(repo_root)
    receipt = dict(receipt or load_receipt(root, receipt_path=receipt_path))
    source = dict(receipt["source_evidence"])
    ledger_path = root / str(source["candidate_ledger_path"])
    if (
        file_sha256(ledger_path) != str(source["candidate_ledger_sha256"])
        or int(source["candidate_ledger_row_count"]) != 50_000
    ):
        raise RuntimeError("TEMPORAL_POLICY_VALIDATION_LEDGER_CHANGED")
    ledger = pd.read_parquet(ledger_path)
    if len(ledger) != 50_000:
        raise RuntimeError("TEMPORAL_POLICY_VALIDATION_LEDGER_COUNT_CHANGED")
    prefix_boundary = int(source["valid_prefix_boundary"])
    suffix_end = int(source["valid_suffix_end"])
    prefix_families = set(
        ledger.loc[
            ledger["completion_ordinal"].le(prefix_boundary), "behavior_family_id"
        ].astype(str)
    )
    suffix = ledger.loc[
        ledger["completion_ordinal"].gt(prefix_boundary)
        & ledger["completion_ordinal"].le(suffix_end)
        & ledger["arm"].isin(ARMS)
        & ledger["program_family_id"].isin(PROGRAM_FAMILIES)
        & ledger["left_incremental_net_mean"].gt(0.0)
        & ledger["right_incremental_net_mean"].gt(0.0)
    ].copy()
    suffix = suffix.loc[~suffix["behavior_family_id"].astype(str).isin(prefix_families)]
    suffix = suffix.sort_values(
        ["completion_ordinal", "candidate_id"], kind="stable"
    ).drop_duplicates("behavior_family_id", keep="first")
    lane_maps = {
        arm: {seed: index for index, seed in enumerate(sorted(group["seed"].unique()))}
        for arm, group in suffix.groupby("arm", sort=True)
    }
    if any(len(value) != 4 for value in lane_maps.values()) or set(lane_maps) != set(ARMS):
        raise RuntimeError("TEMPORAL_POLICY_VALIDATION_LANES_CHANGED")
    suffix["lane_index"] = [
        lane_maps[str(arm)][int(seed)] for arm, seed in zip(suffix["arm"], suffix["seed"])
    ]
    salt = str(receipt["selection"]["sampling_salt"])
    selected: list[dict[str, Any]] = []
    quota = int(receipt["selection"]["candidate_count_per_family_lane"])
    for arm in ARMS:
        for family in PROGRAM_FAMILIES:
            for lane_index in range(4):
                cell = suffix.loc[
                    suffix["arm"].eq(arm)
                    & suffix["program_family_id"].eq(family)
                    & suffix["lane_index"].eq(lane_index)
                ].copy()
                rows = cell.to_dict("records")
                rows.sort(key=lambda row: (_sampling_key(salt, row), str(row["candidate_id"])))
                if len(rows) < quota:
                    raise RuntimeError(
                        f"TEMPORAL_POLICY_VALIDATION_CELL_UNDERFILLED:{arm}:{family}:{lane_index}"
                    )
                selected.extend(rows[:quota])
    if (
        len(selected) != 360
        or len({str(row["candidate_id"]) for row in selected}) != 360
        or len({str(row["behavior_family_id"]) for row in selected}) != 360
    ):
        raise RuntimeError("TEMPORAL_POLICY_VALIDATION_SELECTION_COUNT_CHANGED")
    for row in selected:
        row["candidate"] = json.loads(str(row["candidate_spec_json"]))
        row["source_arm"] = str(row["arm"])
    projection = selection_projection(selected)
    if verify_expected_hash and canonical_sha256(projection) != str(
        receipt["selection"]["selection_sha256"]
    ):
        raise RuntimeError("TEMPORAL_POLICY_VALIDATION_SELECTION_CHANGED")
    return selected


def freeze_selection(
    runtime_root: Path,
    *,
    source_sha: str,
    receipt: Mapping[str, Any],
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    projection = selection_projection(rows)
    payload = {
        "schema_version": 1,
        "status": "SELECTION_FROZEN_BEFORE_VALIDATION_READ",
        "producer_source_sha": source_sha,
        "candidate_count": len(projection),
        "selection_sha256": canonical_sha256(projection),
        "selection": projection,
        "market_arrays_read_before_freeze": 0,
        "validation_rows_read_before_freeze": 0,
        "holdout_rows_read": 0,
    }
    payload["receipt_sha256"] = canonical_sha256(payload)
    write_json(runtime_root / "selection_receipt.json", payload)
    return payload


def sweep_temporal_program_constructibility(
    *,
    selected_rows: Sequence[Mapping[str, Any]],
    contract_rows: Sequence[Mapping[str, Any]],
    expression_registry_limits: Mapping[str, Any],
) -> dict[str, Any]:
    """Rebuild frozen Temporal Program candidates without reading market arrays."""

    from alphafactory_crypto.broad_search.compositional18m import (
        CandidateSpec,
        TypedExpressionRegistry,
        mechanism_role_domains,
    )
    from alphafactory_crypto.broad_search.runner18m import _contracts_from_payload
    from alphafactory_crypto.broad_search.temporal_program_v1 import (
        temporal_program_candidate_from_genes,
    )

    registry = TypedExpressionRegistry(
        _contracts_from_payload(contract_rows),
        **dict(expression_registry_limits),
    )
    domains = mechanism_role_domains(tuple(registry.fields.values()))
    proofs: list[dict[str, Any]] = []
    seen: set[str] = set()
    for ordinal, raw in enumerate(selected_rows):
        selected = dict(raw)
        payload = dict(selected["candidate"])
        stored = CandidateSpec.from_dict(payload)
        rebuilt = temporal_program_candidate_from_genes(
            registry,
            genes=stored.generation_genes,
            domains=domains,
        )
        genes = stored.generation_genes
        program_spec = dict(genes.get("program_spec") or {})
        candidate_id = str(selected["candidate_id"])
        if (
            candidate_id in seen
            or stored.candidate_id != candidate_id
            or rebuilt.to_dict() != stored.to_dict()
            or canonical_sha256(payload) != str(selected["candidate_spec_sha256"])
            or stored.expression.expression_id == stored.control.expression_id
            or str(genes.get("representation")) != "TEMPORAL_PROGRAM"
            or str(genes.get("program_id")) != str(selected["program_id"])
            or str(program_spec.get("family_id"))
            != str(selected["program_family_id"])
            or stored.horizon_hours != 4
        ):
            raise RuntimeError(
                f"TEMPORAL_PROGRAM_CONSTRUCTIBILITY_CHANGED:{ordinal}:{candidate_id}"
            )
        seen.add(candidate_id)
        proofs.append(
            {
                "source_ordinal": int(ordinal),
                "candidate_id": candidate_id,
                "candidate_spec_sha256": str(selected["candidate_spec_sha256"]),
                "expression_id": stored.expression.expression_id,
                "control_expression_id": stored.control.expression_id,
                "program_id": str(genes["program_id"]),
                "program_family_id": str(program_spec["family_id"]),
            }
        )
    return {
        "schema_version": 1,
        "status": "PASS_TEMPORAL_PROGRAM_CONSTRUCTIBILITY_SWEEP",
        "market_read_performed": False,
        "candidate_count": len(proofs),
        "unique_candidate_count": len(seen),
        "proofs_sha256": canonical_sha256(proofs),
    }


def _expression_registry_limits(config: Mapping[str, Any]) -> dict[str, int]:
    values = dict(config["expression_limits"])
    return {
        "max_depth": int(values["maximum_depth"]),
        "max_raw_inputs": int(values["maximum_raw_fields"]),
        "max_rolling_windows": int(values["maximum_rolling_windows"]),
        "max_canonical_primitive_nodes": int(
            values["maximum_canonical_primitive_nodes"]
        ),
        "max_cross_asset_normalizations": int(
            values["maximum_cross_asset_normalizations"]
        ),
        "max_regime_gates": int(values["maximum_regime_gates"]),
    }


def _economic_context(
    repo_root: Path,
    *,
    receipt: Mapping[str, Any],
    receipt_path: str,
    target_identity_sha256: str,
) -> dict[str, Any]:
    source = dict(receipt["source_evidence"])
    base = resolve_search_economic_receipt(
        repo_root, str(source["economic_receipt_path"])
    )
    validation = {
        "role": str(receipt["split_contract"]["validation"]["role"]),
        "start": str(receipt["split_contract"]["validation"]["start"]),
        "end_exclusive": str(receipt["split_contract"]["validation"]["end_exclusive"]),
        "optimizer_feedback_allowed": False,
        "policy_memory_write_allowed": False,
        "candidate_generation_allowed": False,
    }
    return {
        **base,
        "run_authorized": True,
        "run_authorization": dict(receipt["run_authorization"]),
        "evidence_partition": {
            **{key: dict(value) for key, value in dict(base["evidence_partition"]).items()},
            "validation": validation,
        },
        "validation": validation,
        "execution": {
            **dict(base["execution"]),
            "target_cache_path": str(receipt["carrier"]["target_cache"]),
            "target_cache_identity_sha256": target_identity_sha256,
        },
        "receipt_sha256": file_sha256(repo_root / receipt_path),
    }


def _economic_context_for_interval(
    economic: Mapping[str, Any],
    *,
    interval: Mapping[str, Any],
    receipt: Mapping[str, Any],
) -> dict[str, Any]:
    allowed = {
        (
            "full",
            str(receipt["split_contract"]["validation"]["start"]),
            str(receipt["split_contract"]["validation"]["end_exclusive"]),
        ),
        *{
            (
                str(row["label"]),
                str(row["start"]),
                str(row["end_exclusive"]),
            )
            for row in receipt["split_contract"]["validation_blocks"]
        },
    }
    identity = (
        str(interval["label"]),
        str(interval["start"]),
        str(interval["end_exclusive"]),
    )
    if identity not in allowed:
        raise RuntimeError("TEMPORAL_POLICY_VALIDATION_INTERVAL_NOT_RECEIPT_BOUND")
    validation = {
        **dict(economic["validation"]),
        "start": identity[1],
        "end_exclusive": identity[2],
    }
    return {
        **dict(economic),
        "evidence_partition": {
            **{
                key: dict(value)
                for key, value in dict(economic["evidence_partition"]).items()
            },
            "validation": validation,
        },
        "validation": validation,
    }


def _load_reused_full_pass(
    repo_root: Path,
    *,
    runtime_root: Path,
    selected: Sequence[Mapping[str, Any]],
    receipt: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    continuation = dict(receipt.get("continuation") or {})
    source_path = repo_root / str(continuation.get("full_pass_candidate_ledger_path") or "")
    if (
        continuation.get("mode")
        != "REUSE_VERIFIED_FULL_PASS_EVALUATE_MISSING_BLOCKS"
        or not source_path.is_file()
        or file_sha256(source_path)
        != str(continuation.get("full_pass_candidate_ledger_sha256") or "")
    ):
        raise RuntimeError("TEMPORAL_POLICY_VALIDATION_REUSED_FULL_PASS_CHANGED")
    frame = pd.read_parquet(source_path)
    expected = {
        str(row["candidate_id"]): str(row["candidate_spec_sha256"])
        for row in selected
    }
    actual = dict(
        zip(
            frame["candidate_id"].astype(str),
            frame["candidate_spec_sha256"].astype(str),
        )
    )
    allowed_statuses = {"EVALUATED", "CANDIDATE_LOCAL_FAILURE"}
    if (
        len(frame) != 360
        or frame["candidate_id"].nunique() != 360
        or actual != expected
        or set(frame["validation_status"].astype(str)) - allowed_statuses
        or not frame["evaluation_partition"].eq("validation").all()
        or frame["candidate_generation_performed"].ne(False).any()
        or frame["optimizer_feedback_written"].ne(False).any()
        or frame["archive_written"].ne(False).any()
    ):
        raise RuntimeError("TEMPORAL_POLICY_VALIDATION_REUSED_FULL_PASS_INVALID")
    destination = runtime_root / "passes" / "full" / "candidate_ledger.parquet"
    destination.parent.mkdir(parents=True)
    shutil.copy2(source_path, destination)
    reuse = {
        "schema_version": 1,
        "status": "REUSED_VERIFIED_FULL_PASS",
        "source_runtime": str(continuation["source_runtime"]),
        "source_task_id": str(continuation["source_task_id"]),
        "source_producer_sha": str(continuation["source_producer_sha"]),
        "source_candidate_ledger_path": str(
            continuation["full_pass_candidate_ledger_path"]
        ),
        "source_candidate_ledger_sha256": file_sha256(source_path),
        "reused_candidate_count": 360,
        "strict_evaluated_count": int(frame["strict_evaluated"].eq(True).sum()),
        "candidate_local_failure_count": int(
            frame["validation_status"].eq("CANDIDATE_LOCAL_FAILURE").sum()
        ),
        "new_market_evaluation_count": 0,
    }
    reuse["receipt_sha256"] = canonical_sha256(reuse)
    write_json(runtime_root / "full_pass_reuse_receipt.json", reuse)
    return frame.to_dict("records"), reuse


def _evaluate_interval(
    *,
    cache_root: Path,
    target_root: Path,
    contract_rows: Sequence[Mapping[str, Any]],
    economic: Mapping[str, Any],
    start: str,
    end: str,
    role: str,
    payloads: Sequence[Mapping[str, Any]],
    workers: int,
    expression_registry_limits: Mapping[str, Any],
) -> list[dict[str, Any]]:
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=workers,
        initializer=_v24_worker_initialize,
        initargs=(
            str(cache_root),
            str(target_root),
            list(contract_rows),
            dict(economic),
            start,
            end,
            role,
            dict(expression_registry_limits),
        ),
    ) as executor:
        return list(executor.map(_v24_worker_evaluate, payloads, chunksize=1))


def _project_pass(
    output_root: Path,
    *,
    selected: Sequence[Mapping[str, Any]],
    workers: Sequence[Mapping[str, Any]],
    economic_receipt_sha256: str,
) -> list[dict[str, Any]]:
    output_root.mkdir(parents=True)
    projections = _v24_write_batch_projections(
        output_root,
        base_ordinal=0,
        selected_rows=list(selected),
        worker_rows=list(workers),
        economic_receipt_sha256=economic_receipt_sha256,
        persist_candidate_local_failures=True,
    )
    rows = [
        _augment_projection(item, selected=selected[index], worker=workers[index])
        for index, item in enumerate(projections)
    ]
    pd.DataFrame(rows).to_parquet(output_root / "candidate_ledger.parquet", index=False)
    return rows


def _arm_summary(frame: pd.DataFrame, train_yield: float) -> dict[str, Any]:
    full_positive = frame["validation_left_incremental_net_mean"].gt(0.0) & frame[
        "validation_right_incremental_net_mean"
    ].gt(0.0)
    replicated = frame["replicated_positive_block_count"].ge(2)
    survivors = frame.loc[replicated]
    return {
        "candidate_count": int(len(frame)),
        "strict_evaluated_count": int(frame["strict_evaluated"].eq(True).sum()),
        "full_window_dual_net_positive_count": int(full_positive.sum()),
        "full_window_dual_net_positive_rate": float(full_positive.mean()),
        "replicated_2_of_3_count": int(replicated.sum()),
        "replicated_2_of_3_rate": float(replicated.mean()),
        "validation_matched_positive_count": int(
            frame["validation_matched_positive"].eq(True).sum()
        ),
        "train_economic_cluster_yield_per_1k": float(train_yield),
        "migrated_replicated_cluster_yield_per_1k": float(
            train_yield * replicated.mean()
        ),
        "replicated_program_family_count": int(
            survivors["program_family_id"].nunique()
        ),
        "replicated_lane_count": int(survivors["lane_index"].nunique()),
        "replicated_program_id_count": int(survivors["program_id"].nunique()),
    }


def build_decision(frame: pd.DataFrame, receipt: Mapping[str, Any]) -> dict[str, Any]:
    yields = dict(receipt["decision_contract"]["train_economic_cluster_yield_per_1k"])
    summaries = {
        arm: _arm_summary(frame.loc[frame["arm"].eq(arm)].copy(), float(yields[arm]))
        for arm in ARMS
    }
    evolution = summaries["temporal_program_evolution"]
    controls = [summaries["temporal_program_random"], summaries["temporal_program_cem"]]
    control_max = max(row["migrated_replicated_cluster_yield_per_1k"] for row in controls)
    allowed_statuses = {"EVALUATED", "CANDIDATE_LOCAL_FAILURE"}
    integrity = {
        "exact_equal_arm_counts": all(row["candidate_count"] == 120 for row in summaries.values()),
        "all_full_and_block_evaluation_attempts_complete": bool(
            len(frame) == 360
            and frame["candidate_id"].nunique() == 360
            and set(frame["validation_status"].astype(str)) <= allowed_statuses
            and all(
                set(frame[f"block_{index}_validation_status"].astype(str))
                <= allowed_statuses
                for index in range(1, 4)
            )
        ),
        "split_contract_valid": True,
    }
    gates = {
        "minimum_evolution_replicated_count": evolution["replicated_2_of_3_count"] >= 6,
        "end_to_end_yield_advantage": evolution[
            "migrated_replicated_cluster_yield_per_1k"
        ] > 1.5 * control_max,
        "both_program_families_survive": evolution["replicated_program_family_count"] == 2,
        "at_least_three_lanes_survive": evolution["replicated_lane_count"] >= 3,
        "at_least_four_program_basins_survive": evolution["replicated_program_id_count"] >= 4,
    }
    passed = all(integrity.values()) and all(gates.values())
    return {
        "schema_version": 1,
        "status": "TEMPORAL_POLICY_VALIDATION_COMPLETE",
        "decision": (
            "QUALIFY_20_20_60_FIXED_DEVELOPMENT_FLOW" if passed else "HOLD_CURRENT_FIXED_FLOW"
        ),
        "policy_validation_pass": passed,
        "arm_summaries": summaries,
        "integrity_gates": integrity,
        "economic_migration_gates": gates,
        "alpha_qualification": "HOLD",
        "fixed_flow_allocation_if_qualified": dict(
            receipt["fixed_flow_transition"]["allocation_per_10000"]
        ),
        "automatic_search_started": False,
        "oos": False,
        "promotion_authorized": False,
    }


def run_gate(
    repo_root: Path,
    *,
    runtime_date: str = DEFAULT_RUNTIME_DATE,
    receipt_path: str = RECEIPT_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    receipt = load_receipt(root, require_authorized=True, receipt_path=receipt_path)
    source_sha = validate_execution_source(root, receipt)
    runtime_root = root / "runtime" / f"{RUNTIME_PREFIX}_{runtime_date}"
    if runtime_root.exists():
        raise RuntimeError("TEMPORAL_POLICY_VALIDATION_RUNTIME_ALREADY_EXISTS")
    runtime_root.mkdir(parents=True)
    selected = select_equal_count_cohort(root, receipt=receipt, receipt_path=receipt_path)
    selection = freeze_selection(
        runtime_root, source_sha=source_sha, receipt=receipt, rows=selected
    )
    authorization = dict(receipt["run_authorization"])
    authority = require_real_experiment_authority(
        root,
        evidence_to_add=str(receipt["evidence_to_add"]),
        decision_to_change=str(receipt["decision_to_change"]),
        economic_receipt_required=False,
        receipt_bound_non_formal_authorization={
            "decision_id": str(authorization["decision_id"]),
            "authority": "CURRENT_USER_INSTRUCTION",
            "scope": POLICY_VALIDATION_SCOPE,
            "receipt_path": receipt_path,
            "receipt_sha256": canonical_sha256(receipt),
            "run_authorized": True,
        },
    )
    write_json(runtime_root / "authority_preflight.json", authority)
    split_evidence = validate_split_contract(receipt)
    write_json(runtime_root / "split_evidence.json", split_evidence)
    carrier_manifest = json.loads(
        (root / str(receipt["carrier"]["manifest_path"])).read_text(encoding="utf-8")
    )
    contract_rows = list(carrier_manifest["contracts"])
    program_config = json.loads(
        (root / "config" / "crypto_temporal_mechanism_program_v1.json").read_text(
            encoding="utf-8"
        )
    )
    expression_registry_limits = _expression_registry_limits(program_config)
    target_metadata = json.loads(
        (root / str(receipt["carrier"]["target_cache"]) / "metadata.json").read_text(
            encoding="utf-8"
        )
    )
    if (
        len(contract_rows) != 115
        or canonical_sha256(carrier_manifest)
        != str(receipt["carrier"]["manifest_sha256"])
        or str(carrier_manifest["cache_identity_sha256"])
        != str(receipt["carrier"]["cache_identity_sha256"])
        or str(target_metadata["identity_sha256"])
        != str(receipt["carrier"]["target_identity_sha256"])
    ):
        raise RuntimeError("TEMPORAL_POLICY_VALIDATION_CARRIER_OR_TARGET_CHANGED")
    static = sweep_temporal_program_constructibility(
        selected_rows=selected,
        contract_rows=contract_rows,
        expression_registry_limits=expression_registry_limits,
    )
    write_json(runtime_root / "static_constructibility.json", static)
    economic = _economic_context(
        root,
        receipt=receipt,
        receipt_path=receipt_path,
        target_identity_sha256=str(target_metadata["identity_sha256"]),
    )
    payloads = [
        {
            "candidate": row["candidate"],
            "frozen_train_orientation": float(row["train_orientation"]),
        }
        for row in selected
    ]
    cache_root = root / str(receipt["carrier"]["aligned_cache"])
    target_root = root / str(receipt["carrier"]["target_cache"])
    role = str(receipt["split_contract"]["validation"]["role"])
    passes = [dict(row) for row in receipt["split_contract"]["validation_blocks"]]
    started = time.perf_counter()
    active_workers = int(receipt["compute"]["workers_default"])
    reused_full_rows, reuse = _load_reused_full_pass(
        root,
        runtime_root=runtime_root,
        selected=selected,
        receipt=receipt,
    )
    pass_rows: dict[str, list[dict[str, Any]]] = {"full": reused_full_rows}
    for index, interval in enumerate(passes, start=1):
        write_json(
            runtime_root / "producer_status.json",
            {
                "schema_version": 1,
                "status": "VALIDATION_RUNNING",
                "producer_pid": os.getpid(),
                "producer_source_sha": source_sha,
                "selection_frozen": True,
                "pass_index": index,
                "pass_label": interval["label"],
                "workers": active_workers,
                "heartbeat_utc": pd.Timestamp.now(tz="UTC").isoformat(),
                "holdout_read_count": 0,
            },
        )
        worker_rows = _evaluate_interval(
            cache_root=cache_root,
            target_root=target_root,
            contract_rows=contract_rows,
            economic=_economic_context_for_interval(
                economic,
                interval=interval,
                receipt=receipt,
            ),
            start=str(interval["start"]),
            end=str(interval["end_exclusive"]),
            role=role,
            payloads=payloads,
            workers=active_workers,
            expression_registry_limits=expression_registry_limits,
        )
        memory_indexes = [
            position for position, row in enumerate(worker_rows) if bool(row.get("memory_error"))
        ]
        if memory_indexes:
            active_workers = int(receipt["compute"]["workers_fallback"])
            retried = _evaluate_interval(
                cache_root=cache_root,
                target_root=target_root,
                contract_rows=contract_rows,
                economic=_economic_context_for_interval(
                    economic,
                    interval=interval,
                    receipt=receipt,
                ),
                start=str(interval["start"]),
                end=str(interval["end_exclusive"]),
                role=role,
                payloads=[payloads[position] for position in memory_indexes],
                workers=active_workers,
                expression_registry_limits=expression_registry_limits,
            )
            for position, row in zip(memory_indexes, retried):
                worker_rows[position] = row
        if any(bool(row.get("memory_error")) for row in worker_rows):
            raise RuntimeError("TEMPORAL_POLICY_VALIDATION_MEMORY_FALLBACK_EXHAUSTED")
        pass_root = runtime_root / "passes" / str(interval["label"])
        pass_rows[str(interval["label"])] = _project_pass(
            pass_root,
            selected=selected,
            workers=worker_rows,
            economic_receipt_sha256=str(economic["receipt_sha256"]),
        )
    full = pd.DataFrame(pass_rows["full"])
    for block_index in range(1, 4):
        block = pd.DataFrame(pass_rows[f"block_{block_index}"]).set_index("candidate_id")
        for column in (
            "validation_status",
            "strict_evaluated",
            "validation_left_incremental_net_mean",
            "validation_right_incremental_net_mean",
            "validation_left_incremental_net_lcb",
            "validation_right_incremental_net_lcb",
            "validation_matched_positive",
            "validation_search_reward",
        ):
            full[f"block_{block_index}_{column}"] = full["candidate_id"].map(block[column])
    full["replicated_positive_block_count"] = sum(
        full[f"block_{index}_validation_left_incremental_net_mean"].gt(0.0)
        & full[f"block_{index}_validation_right_incremental_net_mean"].gt(0.0)
        for index in range(1, 4)
    )
    full["replicated_candidate"] = full["replicated_positive_block_count"].ge(2)
    ledger_path = runtime_root / "candidate_ledger.parquet"
    full.to_parquet(ledger_path, index=False)
    decision = build_decision(full, receipt)
    decision.update(
        {
            "producer_source_sha": source_sha,
            "selection_receipt_sha256": selection["receipt_sha256"],
            "split_evidence": split_evidence,
            "authority_result": authority["result"],
            "full_pass_reuse_receipt_sha256": reuse["receipt_sha256"],
        }
    )
    write_json(runtime_root / "final_decision.json", decision)
    report_path = root / "reports" / f"CRYPTO_TEMPORAL_POLICY_VALIDATION_V1_{runtime_date}.md"
    report_path.parent.mkdir(exist_ok=True)
    report_path.write_text(
        "# Crypto Temporal Policy Development Validation V1\n\n"
        f"- Decision: `{decision['decision']}`\n"
        f"- Policy validation pass: `{decision['policy_validation_pass']}`\n"
        "- Evaluation lineage: reused the hash-bound completed 360-candidate full pass; "
        "evaluated only the three previously missing frozen validation blocks.\n"
        f"- Split: `{split_evidence['train_effective_hours']}` train effective hours / "
        f"`{split_evidence['validation_effective_hours']}` validation effective hours\n"
        "- Boundary: development validation only; no OOS, holdout, promotion, optimizer feedback, or automatic search.\n\n"
        "```json\n"
        + json.dumps(decision["arm_summaries"], indent=2, sort_keys=True)
        + "\n```\n",
        encoding="utf-8",
    )
    elapsed = time.perf_counter() - started
    manifest = {
        "schema_version": 1,
        "status": "TEMPORAL_POLICY_VALIDATION_COMPLETE",
        "producer_source_sha": source_sha,
        "runtime": str(runtime_root.relative_to(root).as_posix()),
        "report": str(report_path.relative_to(root).as_posix()),
        "candidate_count": 360,
        "evaluation_passes": 4,
        "pair_evaluation_count": 1_440,
        "reused_pair_evaluation_count": 360,
        "new_pair_evaluation_count": 1_080,
        "reused_pass_count": 1,
        "new_pass_count": 3,
        "active_wall_seconds": elapsed,
        "pair_evaluated_per_hour": 1_080 * 3_600.0 / elapsed,
        "workers": active_workers,
        "candidate_generation_performed": False,
        "optimizer_feedback_written": False,
        "archive_written": False,
        "holdout_read_count": 0,
        "oos": False,
        "promotion_authorized": False,
        "automatic_search_started": False,
        "files": [
            {
                "path": str(path.relative_to(root).as_posix()),
                "bytes": path.stat().st_size,
                "sha256": file_sha256(path),
            }
            for path in (
                runtime_root / "selection_receipt.json",
                runtime_root / "split_evidence.json",
                runtime_root / "full_pass_reuse_receipt.json",
                ledger_path,
                runtime_root / "final_decision.json",
                report_path,
            )
        ],
    }
    manifest["bundle_sha256"] = canonical_sha256(manifest)
    write_json(runtime_root / "run_manifest.json", manifest)
    write_json(
        runtime_root / "producer_status.json",
        {
            "schema_version": 1,
            "status": "TEMPORAL_POLICY_VALIDATION_COMPLETE",
            "producer_pid": os.getpid(),
            "producer_source_sha": source_sha,
            "workers": active_workers,
            "heartbeat_utc": pd.Timestamp.now(tz="UTC").isoformat(),
            "pair_evaluated_per_hour": manifest["pair_evaluated_per_hour"],
            "policy_validation_pass": decision["policy_validation_pass"],
            "holdout_read_count": 0,
        },
    )
    return decision


def check_gate(
    repo_root: Path,
    *,
    runtime_date: str = DEFAULT_RUNTIME_DATE,
    receipt_path: str = RECEIPT_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    receipt = load_receipt(root, receipt_path=receipt_path)
    runtime_root = root / "runtime" / f"{RUNTIME_PREFIX}_{runtime_date}"
    manifest = json.loads((runtime_root / "run_manifest.json").read_text(encoding="utf-8"))
    decision = json.loads((runtime_root / "final_decision.json").read_text(encoding="utf-8"))
    selection = json.loads((runtime_root / "selection_receipt.json").read_text(encoding="utf-8"))
    errors: list[str] = []
    if manifest.get("status") != "TEMPORAL_POLICY_VALIDATION_COMPLETE":
        errors.append("manifest_status")
    if int(manifest.get("candidate_count", -1)) != 360 or int(
        manifest.get("pair_evaluation_count", -1)
    ) != 1_440:
        errors.append("counts")
    if (
        int(manifest.get("reused_pair_evaluation_count", -1)) != 360
        or int(manifest.get("new_pair_evaluation_count", -1)) != 1_080
        or int(manifest.get("reused_pass_count", -1)) != 1
        or int(manifest.get("new_pass_count", -1)) != 3
    ):
        errors.append("continuation_counts")
    if selection.get("selection_sha256") != receipt["selection"]["selection_sha256"]:
        errors.append("selection")
    if manifest.get("holdout_read_count") != 0 or manifest.get("automatic_search_started") is not False:
        errors.append("boundary")
    for row in manifest.get("files") or ():
        path = root / str(row["path"])
        if not path.is_file() or file_sha256(path) != str(row["sha256"]):
            errors.append(f"file:{row.get('path')}")
    frame = pd.read_parquet(runtime_root / "candidate_ledger.parquet")
    rebuilt = build_decision(frame, receipt)
    if rebuilt["decision"] != decision.get("decision") or rebuilt["arm_summaries"] != decision.get(
        "arm_summaries"
    ):
        errors.append("decision_rebuild")
    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "decision": decision.get("decision"),
        "policy_validation_pass": bool(decision.get("policy_validation_pass")),
        "runtime": str(runtime_root),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("select", "run", "check"))
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--runtime-date", default=DEFAULT_RUNTIME_DATE)
    parser.add_argument("--receipt-path", default=RECEIPT_PATH)
    args = parser.parse_args(argv)
    if args.command == "select":
        receipt = load_receipt(args.repo_root, receipt_path=args.receipt_path)
        rows = select_equal_count_cohort(
            args.repo_root, receipt=receipt, receipt_path=args.receipt_path
        )
        print(json.dumps(selection_projection(rows), indent=2))
        return 0
    if args.command == "run":
        print(
            json.dumps(
                run_gate(
                    args.repo_root,
                    runtime_date=args.runtime_date,
                    receipt_path=args.receipt_path,
                ),
                indent=2,
            )
        )
        return 0
    result = check_gate(
        args.repo_root,
        runtime_date=args.runtime_date,
        receipt_path=args.receipt_path,
    )
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
