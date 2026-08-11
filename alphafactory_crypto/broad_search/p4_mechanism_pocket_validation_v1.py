"""One-shot fresh-development validation for the frozen P4/P1 pocket cohort.

This adapter reuses the existing 115-field carrier, typed compiler, Binance
target, portfolio mapping, dual-axis pair evaluator, reward, and V2.4 worker
projection.  It cannot generate candidates or write optimizer/archive state.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import math
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, Mapping, Sequence

import pandas as pd

from alphafactory_crypto.broad_search.search_engine_v1 import (
    _contracts_payload,
    _evaluation_audit_fields,
    _load_v14_config,
    _search_ordering_reward,
    _v14_carrier_contracts,
)
from alphafactory_crypto.broad_search.search_engine_v2_4 import (
    _v24_checkpoint_files,
    _v24_worker_evaluate,
    _v24_worker_initialize,
    _v24_write_batch_projections,
    sweep_v24_static_constructibility,
)
from alphafactory_crypto.broad_search.search_evidence_validation_v1 import (
    _merge_raw_panel_stores,
)


RECEIPT_PATH = "config/crypto_p4_mechanism_pocket_validation_v1_receipt.json"
RUNTIME_PREFIX = "crypto_p4_mechanism_pocket_validation_v1"
DEFAULT_RUNTIME_DATE = "20260811"
SELECTION_PATH = (
    "runtime/crypto_p4_mechanism_pocket_validation_v1_20260811/"
    "behavior_family_selection_receipt.json"
)
EXPECTED_SELECTION_SHA256 = (
    "E9AB5D4D27B3BC20C0AB6AB673DE7FE6D505084B7B98F910E21CCB606D3916C8"
)
EXPECTED_SELECTION_RECEIPT_SHA256 = (
    "F80DA0531A46660766423B90073F1F861DA89F56A00F3869939BF7CFFCDE6858"
)
GROUPS = (
    "discovery_matched_positive",
    "evolution_near_miss_control",
    "random_near_miss_control",
)


def canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest().upper()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while block := handle.read(8 * 1024 * 1024):
            digest.update(block)
    return digest.hexdigest().upper()


def verify_retained_oi_payload(
    repo_root: Path,
    *,
    source_root: Path,
    receipt: Mapping[str, Any],
) -> dict[str, Any]:
    """Verify the exact immutable OI payload reused by a replacement run."""

    authority = dict(receipt.get("retained_oi_payload") or {})
    if authority.get("reuse_authorized") is not True:
        raise RuntimeError("P4_POCKET_RETAINED_OI_REUSE_NOT_AUTHORIZED")
    root = Path(source_root).resolve()
    expected_root = Path(str(authority["source_root"])).resolve()
    if os.path.normcase(str(root)) != os.path.normcase(str(expected_root)):
        raise RuntimeError("P4_POCKET_RETAINED_OI_SOURCE_ROOT_CHANGED")
    manifest_path = Path(repo_root) / str(authority["manifest_path"])
    if file_sha256(manifest_path) != str(authority["manifest_file_sha256"]):
        raise RuntimeError("P4_POCKET_RETAINED_OI_MANIFEST_FILE_CHANGED")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    saved_manifest_sha = str(manifest.pop("manifest_sha256", ""))
    if (
        canonical_sha256(manifest) != saved_manifest_sha
        or saved_manifest_sha != str(authority["manifest_sha256"])
        or manifest.get("status") != "RETAINED_OI_PAYLOAD_HASH_BOUND"
    ):
        raise RuntimeError("P4_POCKET_RETAINED_OI_MANIFEST_CHANGED")
    rows = sorted(
        (dict(row) for row in manifest.get("files") or ()),
        key=lambda row: str(row["path"]),
    )
    actual_paths = sorted(
        path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()
    )
    expected_paths = [str(row["path"]) for row in rows]
    if actual_paths != expected_paths:
        raise RuntimeError("P4_POCKET_RETAINED_OI_FILE_SET_CHANGED")
    for row in rows:
        path = root / str(row["path"])
        if path.stat().st_size != int(row["bytes"]):
            raise RuntimeError("P4_POCKET_RETAINED_OI_FILE_SIZE_CHANGED")
        if file_sha256(path) != str(row["sha256"]):
            raise RuntimeError("P4_POCKET_RETAINED_OI_FILE_HASH_CHANGED")
    bundle = "\n".join(
        f"{row['path']}|{row['bytes']}|{row['sha256']}" for row in rows
    ).encode("utf-8")
    bundle_sha = hashlib.sha256(bundle).hexdigest().upper()
    if (
        bundle_sha != str(manifest["artifact_bundle_sha256"])
        or bundle_sha != str(authority["artifact_bundle_sha256"])
        or len(rows) != int(authority["file_count"])
        or sum(int(row["bytes"]) for row in rows) != int(authority["total_bytes"])
    ):
        raise RuntimeError("P4_POCKET_RETAINED_OI_BUNDLE_CHANGED")
    return {
        "status": "RETAINED_OI_PAYLOAD_REVERIFIED",
        "manifest_file_sha256": str(authority["manifest_file_sha256"]),
        "manifest_sha256": saved_manifest_sha,
        "artifact_bundle_sha256": bundle_sha,
        "file_count": len(rows),
        "total_bytes": sum(int(row["bytes"]) for row in rows),
    }


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".tmp-{os.getpid()}")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def _git_head(root: Path) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True
    ).strip().lower()


def _validate_execution_source(root: Path, receipt: Mapping[str, Any]) -> str:
    head = _git_head(root)
    implementation = str(receipt["source_implementation_sha"]).lower()
    if subprocess.run(
        ["git", "merge-base", "--is-ancestor", implementation, head],
        cwd=root,
        check=False,
    ).returncode:
        raise RuntimeError("P4_POCKET_IMPLEMENTATION_NOT_ANCESTOR")
    changed = sorted(
        line.replace("\\", "/")
        for line in subprocess.check_output(
            ["git", "diff", "--name-only", f"{implementation}..{head}"],
            cwd=root,
            text=True,
        ).splitlines()
        if line.strip()
    )
    allowed = sorted(str(item) for item in receipt["allowed_post_implementation_paths"])
    if changed != allowed:
        raise RuntimeError("P4_POCKET_POST_IMPLEMENTATION_SOURCE_DRIFT")
    if subprocess.run(["git", "diff", "--quiet"], cwd=root, check=False).returncode:
        raise RuntimeError("P4_POCKET_WORKTREE_DIRTY")
    if subprocess.run(
        ["git", "diff", "--cached", "--quiet"], cwd=root, check=False
    ).returncode:
        raise RuntimeError("P4_POCKET_INDEX_DIRTY")
    return head


def load_receipt(
    repo_root: Path,
    *,
    require_authorized: bool | None = None,
    receipt_path: str = RECEIPT_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    path = root / receipt_path
    receipt = json.loads(path.read_text(encoding="utf-8"))
    blockers: list[str] = []
    if receipt.get("receipt_id") != "CRYPTO_P4_MECHANISM_POCKET_VALIDATION_V1":
        blockers.append("receipt_id")
    if require_authorized is not None and bool(receipt.get("run_authorized")) is not bool(
        require_authorized
    ):
        blockers.append("run_authorized")
    if receipt.get("selection_receipt_path") != SELECTION_PATH:
        blockers.append("selection_receipt_path")
    if receipt.get("selection_sha256") != EXPECTED_SELECTION_SHA256:
        blockers.append("selection_sha256")
    if receipt.get("selection_receipt_sha256") != EXPECTED_SELECTION_RECEIPT_SHA256:
        blockers.append("selection_receipt_sha256")
    interval = dict(receipt.get("development_fresh_interval") or {})
    if interval != {
        "feature_warmup_start": "2026-07-18T00:00:00Z",
        "evaluation_start": "2026-08-01T00:00:00Z",
        "evaluation_end_exclusive": "2026-08-10T00:00:00Z",
        "role": "DEVELOPMENT_FRESH_NO_FEEDBACK_NOT_OOS",
        "warmup_rows_cannot_enter_labels_or_metrics": True,
    }:
        blockers.append("development_fresh_interval")
    compute = dict(receipt.get("compute") or {})
    if (
        int(compute.get("workers_default", -1)) != 10
        or int(compute.get("workers_fallback", -1)) != 8
        or int(compute.get("candidate_count", -1)) != 80
    ):
        blockers.append("compute")
    decision = dict(receipt.get("decision_contract") or {})
    if decision.get("behavior_deoverlap_rule") != (
        "HIGHEST_TRAIN_SEARCH_REWARD_THEN_CANDIDATE_ID"
    ):
        blockers.append("decision_contract")
    boundaries = dict(receipt.get("boundaries") or {})
    for key in (
        "candidate_generation",
        "optimizer_feedback",
        "policy_memory_write",
        "archive_write",
        "parameter_tuning",
        "rescue_rerun",
        "second_run",
        "validation_oos_holdout_read",
        "promotion",
        "automatic_expansion",
    ):
        if boundaries.get(key) is not False:
            blockers.append(key)
    retained = receipt.get("retained_oi_payload")
    if retained is not None:
        retained = dict(retained)
        if (
            retained.get("reuse_authorized") is not True
            or len(str(retained.get("manifest_file_sha256") or "")) != 64
            or len(str(retained.get("manifest_sha256") or "")) != 64
            or len(str(retained.get("artifact_bundle_sha256") or "")) != 64
            or int(retained.get("file_count", -1)) < 1
            or int(retained.get("total_bytes", -1)) < 1
        ):
            blockers.append("retained_oi_payload")
    if blockers:
        raise RuntimeError("P4_POCKET_RECEIPT_INVALID:" + ",".join(blockers))
    return receipt


def load_selection(repo_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    root = Path(repo_root)
    path = root / SELECTION_PATH
    receipt = json.loads(path.read_text(encoding="utf-8"))
    saved = str(receipt.pop("receipt_sha256", ""))
    if (
        canonical_sha256(receipt) != saved
        or saved != EXPECTED_SELECTION_RECEIPT_SHA256
        or receipt.get("selection_sha256") != EXPECTED_SELECTION_SHA256
        or receipt.get("market_payload_read") is not False
        or receipt.get("validation_or_oos_read") is not False
    ):
        raise RuntimeError("P4_POCKET_SELECTION_RECEIPT_CHANGED")
    raw = list(receipt.get("selected_candidates") or ())
    if len(raw) != 80 or len({str(row["candidate_id"]) for row in raw}) != 80:
        raise RuntimeError("P4_POCKET_SELECTION_COUNT_CHANGED")
    if {str(row["selection_group"]) for row in raw} != set(GROUPS):
        raise RuntimeError("P4_POCKET_SELECTION_GROUP_CHANGED")
    prepared: list[dict[str, Any]] = []
    for row in sorted(raw, key=lambda item: int(item["selection_ordinal"])):
        orientation = float(row["train_orientation"])
        candidate = dict(row["candidate_spec"])
        if orientation not in {-1.0, 1.0}:
            raise RuntimeError("P4_POCKET_TRAIN_ORIENTATION_CHANGED")
        prepared.append(
            {
                **dict(row),
                "candidate": candidate,
                "arm": str(row["source_arm"]),
                "source_arm": str(row["source_arm"]),
                "seed": int(row["source_seed"]),
                "horizon_hours": 4,
                "search_reward": float(row["train_search_reward"]),
                "declared_axis_count": 2,
            }
        )
    return {**receipt, "receipt_sha256": saved}, prepared


def prepare_carrier(
    repo_root: Path,
    *,
    new_oi_source_root: Path,
    previous_extended_cache: Path,
    top100_tar: Path,
    ranks101_200_tar: Path,
    runtime_date: str = DEFAULT_RUNTIME_DATE,
    receipt_path: str = RECEIPT_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    receipt = load_receipt(root, require_authorized=True, receipt_path=receipt_path)
    source_sha = _validate_execution_source(root, receipt)
    selection, selected = load_selection(root)
    retained_oi_proof = None
    if receipt.get("retained_oi_payload") is not None:
        retained_oi_proof = verify_retained_oi_payload(
            root,
            source_root=Path(new_oi_source_root),
            receipt=receipt,
        )
    runtime_root = root / "runtime" / f"{RUNTIME_PREFIX}_{runtime_date}"
    if not runtime_root.exists():
        runtime_root.mkdir(parents=True)
        shutil.copy2(root / SELECTION_PATH, runtime_root / "behavior_family_selection_receipt.json")
    if (runtime_root / "aligned_carrier_manifest.json").exists():
        raise RuntimeError("P4_POCKET_CARRIER_ALREADY_PREPARED")

    from alphafactory_crypto.broad_search.replay_v14_binance_target import (
        build_binance_target_cache,
    )
    from alphafactory_crypto.broad_search.runner18m import RawPanelStore
    from alphafactory_crypto.data_admission_v1 import (
        build_aggtrades_search_surface_cache,
        build_oi_mark_search_carrier,
    )

    previous = RawPanelStore.open(Path(previous_extended_cache))
    expected_previous = str(receipt["carrier"]["previous_extended_identity_sha256"])
    if str(previous.metadata["identity_sha256"]) != expected_previous:
        raise RuntimeError("P4_POCKET_PREVIOUS_CARRIER_IDENTITY_CHANGED")
    v14_config, _ = _load_v14_config(root)
    oi_contracts, agg_contracts, _, _ = _v14_carrier_contracts(root, v14_config)
    contracts = tuple((*oi_contracts, *agg_contracts))
    if len(contracts) != 115:
        raise RuntimeError("P4_POCKET_FIELD_CONTRACT_COUNT_CHANGED")
    contract_rows = _contracts_payload(contracts)
    static = sweep_v24_static_constructibility(
        selected_rows=selected, contract_rows=contract_rows
    )
    if int(static["candidate_count"]) != 80:
        raise RuntimeError("P4_POCKET_STATIC_CONSTRUCTIBILITY_CHANGED")
    write_json(runtime_root / "static_constructibility.json", static)

    carrier = dict(receipt["carrier"])
    source_binding = canonical_sha256(
        {
            "run_receipt_sha256": file_sha256(root / receipt_path),
            "selection_receipt_sha256": selection["receipt_sha256"],
            "new_oi_source_root": str(Path(new_oi_source_root)),
        }
    )
    new_oi_cache = root / str(carrier["new_oi_cache"])
    oi_metadata, active_oi_contracts, _, oi_evidence = build_oi_mark_search_carrier(
        source_root=Path(new_oi_source_root),
        output_root=new_oi_cache,
        source_binding_sha256=source_binding,
    )
    if {item.field_id for item in active_oi_contracts} != {
        item.field_id for item in oi_contracts
    }:
        raise RuntimeError("P4_POCKET_OI_FIELD_SET_CHANGED")
    new_aligned_cache = root / str(carrier["new_aligned_cache"])
    new_aligned_metadata = build_aggtrades_search_surface_cache(
        source_cache_root=new_oi_cache,
        top100_tar=Path(top100_tar),
        ranks101_200_tar=Path(ranks101_200_tar),
        output_cache_root=new_aligned_cache,
        broad_field_ids=[item.field_id for item in oi_contracts],
        start=str(receipt["development_fresh_interval"]["evaluation_start"]),
        end_exclusive=str(
            receipt["development_fresh_interval"]["evaluation_end_exclusive"]
        ),
        producer_source_sha=source_sha,
        verify_tar_sha256=True,
    )
    extended_cache = root / str(carrier["extended_aligned_cache"])
    extended_metadata = _merge_raw_panel_stores(
        segment_roots=(Path(previous_extended_cache), new_aligned_cache),
        output_root=extended_cache,
        source_binding_sha256=source_binding,
    )
    target_config = json.loads(
        (root / "config/crypto_search_engine_v1_4_binance_target_replay.json").read_text(
            encoding="utf-8"
        )
    )
    target_root = root / str(carrier["target_cache"])
    target_metadata = build_binance_target_cache(
        root,
        source_store=RawPanelStore.open(extended_cache),
        config=target_config,
        target_cache_root=target_root,
    )
    manifest = {
        "schema_version": 1,
        "status": "P4_POCKET_CARRIER_READY",
        "producer_source_sha": source_sha,
        "selection_receipt_sha256": selection["receipt_sha256"],
        "development_fresh_interval": dict(receipt["development_fresh_interval"]),
        "contracts": contract_rows,
        "contracts_sha256": canonical_sha256(contract_rows),
        "field_count": len(contract_rows),
        "new_oi_cache": {
            "path": str(new_oi_cache),
            "identity_sha256": oi_metadata["identity_sha256"],
            "evidence": oi_evidence,
        },
        "new_aligned_cache": {
            "path": str(new_aligned_cache),
            "identity_sha256": new_aligned_metadata["identity_sha256"],
        },
        "extended_aligned_cache": {
            "path": str(extended_cache),
            "identity_sha256": extended_metadata["identity_sha256"],
        },
        "target_cache": {
            "path": str(target_root),
            "identity_sha256": target_metadata["identity_sha256"],
        },
        "top100_tar_sha256": file_sha256(Path(top100_tar)),
        "ranks101_200_tar_sha256": file_sha256(Path(ranks101_200_tar)),
        "market_payload_read_after_selection_freeze": True,
        "missing_value_fill": None,
        "candidate_generation_performed": False,
        "retained_oi_payload": retained_oi_proof,
    }
    manifest["manifest_sha256"] = canonical_sha256(manifest)
    write_json(runtime_root / "aligned_carrier_manifest.json", manifest)
    return manifest


def _economic_context(
    root: Path,
    receipt: Mapping[str, Any],
    *,
    target_identity_sha256: str,
    receipt_path: str,
) -> dict[str, Any]:
    from alphafactory_crypto.broad_search.experiment_authority import (
        resolve_search_economic_receipt,
    )

    base = resolve_search_economic_receipt(root, str(receipt["economic_receipt_path"]))
    interval = dict(receipt["development_fresh_interval"])
    validation = {
        "role": str(interval["role"]),
        "start": str(interval["evaluation_start"]),
        "end_exclusive": str(interval["evaluation_end_exclusive"]),
        "optimizer_feedback_allowed": False,
        "policy_memory_write_allowed": False,
        "candidate_generation_allowed": False,
    }
    return {
        **base,
        "run_authorized": True,
        "run_authorization": {
            "decision_id": str(receipt["decision_id"]),
            "authority": "CURRENT_USER_INSTRUCTION",
            "scope": "ONE_FROZEN_80_CANDIDATE_P4_POCKET_FRESH_DEVELOPMENT_GATE",
            "parameter_tuning_allowed": False,
            "seed_change_allowed": False,
            "rescue_rerun_allowed": False,
        },
        "evidence_partition": {
            **{
                key: dict(value)
                for key, value in dict(base["evidence_partition"]).items()
            },
            "validation": validation,
        },
        "validation": validation,
        "execution": {
            **dict(base["execution"]),
            "target_cache_path": str(receipt["carrier"]["target_cache"]),
            "target_cache_identity_sha256": str(target_identity_sha256),
        },
        "receipt_sha256": file_sha256(root / receipt_path),
    }


def _augment(
    projection: Mapping[str, Any],
    *,
    selected: Mapping[str, Any],
    worker: Mapping[str, Any],
) -> dict[str, Any]:
    output = dict(projection)
    output.update(
        {
            "selection_group": str(selected["selection_group"]),
            "program_family_id": str(selected["program_family_id"]),
            "program_id": str(selected["program_id"]),
            "source_completion_ordinal": int(selected["source_completion_ordinal"]),
            "train_matched_positive": bool(selected["train_matched_positive"]),
            "train_left_incremental_net_mean": float(
                selected["train_left_incremental_net_mean"]
            ),
            "train_right_incremental_net_mean": float(
                selected["train_right_incremental_net_mean"]
            ),
            "train_left_incremental_net_lcb": float(
                selected["train_left_incremental_net_lcb"]
            ),
            "train_right_incremental_net_lcb": float(
                selected["train_right_incremental_net_lcb"]
            ),
        }
    )
    if worker.get("error"):
        output.update(
            {
                "fresh_search_reward": float("nan"),
                "fresh_matched_positive": False,
                "fresh_mechanism_realization_status": None,
                "fresh_active_axis_count": None,
            }
        )
        return output
    evaluation = dict(worker["evaluation"])
    realization = dict(evaluation.get("mechanism_realization_provenance") or {})
    output.update(
        {
            "fresh_search_reward": float(_search_ordering_reward(evaluation)),
            "fresh_matched_positive": bool(evaluation["matched_positive"]),
            "fresh_mechanism_realization_status": realization.get("status"),
            "fresh_active_axis_count": realization.get("active_axis_count"),
        }
    )
    output.update(
        {
            f"fresh_{key}": value
            for key, value in _evaluation_audit_fields(evaluation).items()
        }
    )
    return output


def _deoverlap(frame: pd.DataFrame) -> pd.DataFrame:
    return (
        frame.sort_values(
            ["train_search_reward", "candidate_id"],
            ascending=[False, True],
            kind="mergesort",
        )
        .drop_duplicates("behavior_family_id", keep="first")
        .sort_values("completion_ordinal", kind="mergesort")
    )


def _metrics(frame: pd.DataFrame) -> dict[str, Any]:
    evaluated = frame.loc[frame["strict_evaluated"].eq(True)].copy()
    if evaluated.empty:
        return {
            "source_count": int(len(frame)),
            "strict_evaluated_count": 0,
            "candidate_local_failure_count": int(len(frame)),
            "fresh_matched_positive_count": 0,
            "fresh_matched_positive_rate": 0.0,
            "both_axis_gross_positive_count": 0,
            "both_axis_net_positive_count": 0,
            "both_axis_net_lcb_positive_count": 0,
            "cost_killed_count": 0,
            "fresh_search_reward_positive_count": 0,
            "train_fresh_reward_spearman": None,
        }
    left = evaluated["fresh_left_incremental_net_mean"]
    right = evaluated["fresh_right_incremental_net_mean"]
    left_gross = evaluated["fresh_left_incremental_gross_mean"]
    right_gross = evaluated["fresh_right_incremental_gross_mean"]
    left_lcb = evaluated["fresh_left_incremental_net_lcb"]
    right_lcb = evaluated["fresh_right_incremental_net_lcb"]
    train_rank = evaluated["train_search_reward"].rank()
    fresh_rank = evaluated["fresh_search_reward"].rank()
    corr = train_rank.corr(fresh_rank) if len(evaluated) > 1 else float("nan")
    return {
        "source_count": int(len(frame)),
        "strict_evaluated_count": int(len(evaluated)),
        "candidate_local_failure_count": int(len(frame) - len(evaluated)),
        "fresh_matched_positive_count": int(evaluated["fresh_matched_positive"].sum()),
        "fresh_matched_positive_rate": float(evaluated["fresh_matched_positive"].mean()),
        "both_axis_gross_positive_count": int(
            (left_gross.gt(0.0) & right_gross.gt(0.0)).sum()
        ),
        "both_axis_net_positive_count": int((left.gt(0.0) & right.gt(0.0)).sum()),
        "both_axis_net_lcb_positive_count": int(
            (left_lcb.gt(0.0) & right_lcb.gt(0.0)).sum()
        ),
        "cost_killed_count": int(
            ((left_gross.gt(0.0) & right_gross.gt(0.0)) & ~(left.gt(0.0) & right.gt(0.0))).sum()
        ),
        "fresh_search_reward_positive_count": int(
            evaluated["fresh_search_reward"].gt(0.0).sum()
        ),
        "fresh_search_reward_mean": float(evaluated["fresh_search_reward"].mean()),
        "fresh_search_reward_median": float(evaluated["fresh_search_reward"].median()),
        "train_fresh_reward_spearman": (
            float(corr) if math.isfinite(float(corr)) else None
        ),
    }


def build_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    frame = pd.DataFrame(rows)
    raw_groups = {
        str(group): _metrics(local)
        for group, local in frame.groupby("selection_group", sort=True)
    }
    deoverlapped = _deoverlap(frame)
    deoverlap_groups = {
        str(group): _metrics(local)
        for group, local in deoverlapped.groupby("selection_group", sort=True)
    }
    positives = frame.loc[
        frame["selection_group"].eq("discovery_matched_positive")
    ]
    positives_deoverlapped = deoverlapped.loc[
        deoverlapped["selection_group"].eq("discovery_matched_positive")
    ]
    family_raw = {
        str(family): _metrics(local)
        for family, local in positives.groupby("program_family_id", sort=True)
    }
    family_deoverlapped = {
        str(family): _metrics(local)
        for family, local in positives_deoverlapped.groupby(
            "program_family_id", sort=True
        )
    }
    p4 = family_deoverlapped.get("P4_MULTISCALE_STATE_X_TRANSITION_ROUTING", {})
    control_matched_rate = max(
        float(deoverlap_groups[group]["fresh_matched_positive_rate"])
        for group in (
            "evolution_near_miss_control",
            "random_near_miss_control",
        )
    )
    if (
        int(p4.get("fresh_matched_positive_count", 0)) > 0
        and float(p4.get("fresh_matched_positive_rate", 0.0))
        > control_matched_rate
    ):
        result = "P4_POCKET_FRESH_MATCHED_REPLICATION_OBSERVED"
    elif int(p4.get("both_axis_net_positive_count", 0)) > 0:
        result = "P4_POCKET_DIRECTIONAL_SURVIVAL_ONLY"
    else:
        result = "P4_POCKET_NOT_REPLICATED"
    return {
        "schema_version": 1,
        "status": "P4_POCKET_VALIDATION_COMPLETE",
        "raw_candidate_count": int(len(frame)),
        "behavior_family_deoverlapped_count": int(len(deoverlapped)),
        "all_raw": _metrics(frame),
        "all_behavior_family_deoverlapped": _metrics(deoverlapped),
        "selection_group_raw": raw_groups,
        "selection_group_behavior_family_deoverlapped": deoverlap_groups,
        "discovery_program_family_raw": family_raw,
        "discovery_program_family_behavior_family_deoverlapped": (
            family_deoverlapped
        ),
        "research_result": result,
        "interpretation_boundary": (
            "DEVELOPMENT_FRESH_ONLY_NOT_OOS_PROMOTION_OR_AUTOMATIC_EXPANSION"
        ),
    }


def _report(summary: Mapping[str, Any], source_sha: str) -> str:
    groups = dict(summary["selection_group_behavior_family_deoverlapped"])
    p4 = dict(summary["discovery_program_family_behavior_family_deoverlapped"])[
        "P4_MULTISCALE_STATE_X_TRANSITION_ROUTING"
    ]
    p1 = dict(summary["discovery_program_family_behavior_family_deoverlapped"])[
        "P1_POSITION_STATE_CHANGE_TO_RESPONSE"
    ]
    return f"""# Crypto P4 Mechanism-Pocket Fresh Development Gate V1

- Status: `{summary['status']}`
- Research result: `{summary['research_result']}`
- Producer source: `{source_sha}`
- Interval: `2026-08-01` to `2026-08-10` (July 18-31 is feature warmup only).
- Contract: 40 frozen Evolution matched positives plus 20 Evolution and 20 Random near-miss controls; Binance USD-M delayed-open 4h target; unchanged mapping, dual-axis evaluator, reward, and 5 bps cost.
- Boundary: development-fresh evidence only; no generation, optimizer/archive feedback, OOS, promotion, or automatic expansion.

## Behavior-family-deoverlapped readout

| Slice | Source | Strict | Matched+ | Gross++ | Net++ | LCB++ | Cost-killed | Train/fresh Spearman |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| P4 discovery | {p4['source_count']} | {p4['strict_evaluated_count']} | {p4['fresh_matched_positive_count']} | {p4['both_axis_gross_positive_count']} | {p4['both_axis_net_positive_count']} | {p4['both_axis_net_lcb_positive_count']} | {p4['cost_killed_count']} | {p4['train_fresh_reward_spearman']} |
| P1 discovery | {p1['source_count']} | {p1['strict_evaluated_count']} | {p1['fresh_matched_positive_count']} | {p1['both_axis_gross_positive_count']} | {p1['both_axis_net_positive_count']} | {p1['both_axis_net_lcb_positive_count']} | {p1['cost_killed_count']} | {p1['train_fresh_reward_spearman']} |
| Evolution near-miss | {groups['evolution_near_miss_control']['source_count']} | {groups['evolution_near_miss_control']['strict_evaluated_count']} | {groups['evolution_near_miss_control']['fresh_matched_positive_count']} | {groups['evolution_near_miss_control']['both_axis_gross_positive_count']} | {groups['evolution_near_miss_control']['both_axis_net_positive_count']} | {groups['evolution_near_miss_control']['both_axis_net_lcb_positive_count']} | {groups['evolution_near_miss_control']['cost_killed_count']} | {groups['evolution_near_miss_control']['train_fresh_reward_spearman']} |
| Random near-miss | {groups['random_near_miss_control']['source_count']} | {groups['random_near_miss_control']['strict_evaluated_count']} | {groups['random_near_miss_control']['fresh_matched_positive_count']} | {groups['random_near_miss_control']['both_axis_gross_positive_count']} | {groups['random_near_miss_control']['both_axis_net_positive_count']} | {groups['random_near_miss_control']['both_axis_net_lcb_positive_count']} | {groups['random_near_miss_control']['cost_killed_count']} | {groups['random_near_miss_control']['train_fresh_reward_spearman']} |

Raw-candidate count is `{summary['raw_candidate_count']}`; behavior-family-deoverlapped count is `{summary['behavior_family_deoverlapped_count']}`. No candidate or family is promoted by this report.
"""


def run_gate(
    repo_root: Path,
    *,
    runtime_date: str = DEFAULT_RUNTIME_DATE,
    receipt_path: str = RECEIPT_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    receipt = load_receipt(root, require_authorized=True, receipt_path=receipt_path)
    source_sha = _validate_execution_source(root, receipt)
    selection, selected = load_selection(root)
    runtime_root = root / "runtime" / f"{RUNTIME_PREFIX}_{runtime_date}"
    if (runtime_root / "run_manifest.json").exists():
        raise RuntimeError("P4_POCKET_GATE_ALREADY_TERMINAL")
    manifest_path = runtime_root / "aligned_carrier_manifest.json"
    carrier_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    saved_carrier = str(carrier_manifest.pop("manifest_sha256", ""))
    if (
        canonical_sha256(carrier_manifest) != saved_carrier
        or carrier_manifest.get("status") != "P4_POCKET_CARRIER_READY"
        or int(carrier_manifest.get("field_count", -1)) != 115
    ):
        raise RuntimeError("P4_POCKET_CARRIER_MANIFEST_CHANGED")
    contract_rows = list(carrier_manifest["contracts"])
    carrier = dict(receipt["carrier"])
    cache_root = root / str(carrier["extended_aligned_cache"])
    target_root = root / str(carrier["target_cache"])
    target_metadata = json.loads((target_root / "metadata.json").read_text(encoding="utf-8"))
    if (
        str(carrier_manifest["target_cache"]["identity_sha256"])
        != str(target_metadata["identity_sha256"])
    ):
        raise RuntimeError("P4_POCKET_TARGET_IDENTITY_CHANGED")
    economic = _economic_context(
        root,
        receipt,
        target_identity_sha256=str(target_metadata["identity_sha256"]),
        receipt_path=receipt_path,
    )
    frozen = {
        "schema_version": 1,
        "status": "FROZEN_BEFORE_FRESH_CANDIDATE_EVALUATION",
        "producer_source_sha": source_sha,
        "run_receipt_sha256": file_sha256(root / receipt_path),
        "selection_receipt_sha256": selection["receipt_sha256"],
        "selection_sha256": EXPECTED_SELECTION_SHA256,
        "candidate_count": 80,
        "development_fresh_interval": dict(receipt["development_fresh_interval"]),
        "carrier_manifest_sha256": saved_carrier,
        "contracts_sha256": canonical_sha256(contract_rows),
        "compute": dict(receipt["compute"]),
        "decision_contract": dict(receipt["decision_contract"]),
        "boundaries": dict(receipt["boundaries"]),
        "candidate_generation": False,
        "optimizer_feedback": False,
        "archive_write": False,
        "oos": False,
        "promotion": False,
    }
    frozen["frozen_contract_sha256"] = canonical_sha256(frozen)
    write_json(runtime_root / "frozen_contract.json", frozen)
    started = time.perf_counter()
    active_workers = int(receipt["compute"]["workers_default"])
    memory_fallback_used = False

    def status(name: str, **extra: Any) -> None:
        write_json(
            runtime_root / "producer_status.json",
            {
                "schema_version": 1,
                "status": name,
                "producer_pid": os.getpid(),
                "producer_source_sha": source_sha,
                "heartbeat_utc": pd.Timestamp.now(tz="UTC").isoformat(),
                "source_candidate_count": 80,
                "workers": active_workers,
                "memory_fallback_used": memory_fallback_used,
                "active_wall_seconds": time.perf_counter() - started,
                "candidate_generation_performed": False,
                "optimizer_feedback_written": False,
                "archive_written": False,
                "oos_read_count": 0,
                **extra,
            },
        )

    interval = dict(receipt["development_fresh_interval"])

    def executor(workers: int) -> concurrent.futures.ProcessPoolExecutor:
        return concurrent.futures.ProcessPoolExecutor(
            max_workers=workers,
            initializer=_v24_worker_initialize,
            initargs=(
                str(cache_root),
                str(target_root),
                contract_rows,
                economic,
                str(interval["evaluation_start"]),
                str(interval["evaluation_end_exclusive"]),
                str(interval["role"]),
            ),
        )

    payloads = [
        {
            "candidate": row["candidate"],
            "frozen_train_orientation": float(row["train_orientation"]),
        }
        for row in selected
    ]
    status("P4_POCKET_GATE_RUNNING", completed_candidate_count=0)
    with executor(active_workers) as pool:
        workers = list(pool.map(_v24_worker_evaluate, payloads, chunksize=1))
    memory_indexes = [
        index for index, row in enumerate(workers) if bool(row.get("memory_error"))
    ]
    if memory_indexes:
        memory_fallback_used = True
        active_workers = int(receipt["compute"]["workers_fallback"])
        with executor(active_workers) as pool:
            retried = list(
                pool.map(
                    _v24_worker_evaluate,
                    [payloads[index] for index in memory_indexes],
                    chunksize=1,
                )
            )
        for index, worker in zip(memory_indexes, retried):
            workers[index] = worker
    if any(bool(row.get("memory_error")) for row in workers):
        status("ENGINE_BUDGET_EXHAUSTED_MEMORY")
        raise RuntimeError("P4_POCKET_MEMORY_FALLBACK_EXHAUSTED")

    checkpoint_root = runtime_root / "checkpoints"
    temporary = checkpoint_root / f"checkpoint_000.tmp-{os.getpid()}"
    final_checkpoint = checkpoint_root / "checkpoint_000"
    temporary.mkdir(parents=True)
    projections = _v24_write_batch_projections(
        temporary,
        base_ordinal=0,
        selected_rows=selected,
        worker_rows=workers,
        economic_receipt_sha256=str(economic["receipt_sha256"]),
        persist_candidate_local_failures=True,
    )
    rows = [
        _augment(projection, selected=selected[index], worker=workers[index])
        for index, projection in enumerate(projections)
    ]
    pd.DataFrame(rows).to_parquet(temporary / "candidate_ledger.parquet", index=False)
    checkpoint_manifest = {
        "schema_version": 1,
        "checkpoint": "checkpoint_000",
        "producer_source_sha": source_sha,
        "frozen_contract_sha256": frozen["frozen_contract_sha256"],
        "selection_receipt_sha256": selection["receipt_sha256"],
        "completed_candidate_count": 80,
        "strict_evaluated_count": sum(bool(row["strict_evaluated"]) for row in rows),
        "candidate_local_failure_count": sum(
            not bool(row["strict_evaluated"]) for row in rows
        ),
        "workers": active_workers,
        "memory_fallback_used": memory_fallback_used,
        "files": _v24_checkpoint_files(temporary),
    }
    checkpoint_manifest["manifest_sha256"] = canonical_sha256(checkpoint_manifest)
    write_json(temporary / "manifest.json", checkpoint_manifest)
    os.replace(temporary, final_checkpoint)
    ledger_path = runtime_root / "candidate_ledger.parquet"
    shutil.copy2(final_checkpoint / "candidate_ledger.parquet", ledger_path)
    summary = build_summary(rows)
    write_json(runtime_root / "validation_summary.json", summary)
    decision = {
        **summary,
        "producer_source_sha": source_sha,
        "selection_receipt_sha256": selection["receipt_sha256"],
        "frozen_contract_sha256": frozen["frozen_contract_sha256"],
        "candidate_or_family_qualified": False,
        "promotion_authorized": False,
        "oos": False,
        "automatic_expansion": False,
    }
    write_json(runtime_root / "final_decision.json", decision)
    report_path = root / "reports" / f"CRYPTO_P4_MECHANISM_POCKET_VALIDATION_V1_{runtime_date}.md"
    report_path.parent.mkdir(exist_ok=True)
    report_path.write_text(_report(summary, source_sha), encoding="utf-8")
    elapsed = time.perf_counter() - started
    process_cpu_seconds = float(sum(float(row["process_cpu_seconds"]) for row in workers))
    result_paths = (
        ledger_path,
        runtime_root / "validation_summary.json",
        runtime_root / "final_decision.json",
        final_checkpoint / "manifest.json",
        report_path,
    )
    manifest = {
        "schema_version": 1,
        "status": "P4_POCKET_VALIDATION_COMPLETE",
        "research_result": summary["research_result"],
        "producer_source_sha": source_sha,
        "runtime": str(runtime_root.relative_to(root).as_posix()),
        "report": str(report_path.relative_to(root).as_posix()),
        "run_receipt_sha256": file_sha256(root / receipt_path),
        "selection_receipt_sha256": selection["receipt_sha256"],
        "frozen_contract_sha256": frozen["frozen_contract_sha256"],
        "carrier_manifest_sha256": saved_carrier,
        "candidate_count": 80,
        "strict_evaluated_count": summary["all_raw"]["strict_evaluated_count"],
        "candidate_local_failure_count": summary["all_raw"][
            "candidate_local_failure_count"
        ],
        "active_wall_seconds": elapsed,
        "process_cpu_seconds": process_cpu_seconds,
        "pair_evaluated_per_hour": (
            summary["all_raw"]["strict_evaluated_count"] * 3600.0 / elapsed
            if elapsed > 0
            else 0.0
        ),
        "workers": active_workers,
        "memory_fallback_used": memory_fallback_used,
        "checkpoint_count": 1,
        "candidate_generation_performed": False,
        "optimizer_feedback_written": False,
        "policy_memory_written": False,
        "archive_written": False,
        "oos_read_count": 0,
        "promotion_authorized": False,
        "files": [
            {
                "path": str(path.relative_to(root).as_posix()),
                "bytes": path.stat().st_size,
                "sha256": file_sha256(path),
            }
            for path in result_paths
        ],
    }
    manifest["bundle_sha256"] = canonical_sha256(manifest)
    write_json(runtime_root / "run_manifest.json", manifest)
    status(
        "P4_POCKET_VALIDATION_COMPLETE",
        completed_candidate_count=80,
        strict_evaluated_count=summary["all_raw"]["strict_evaluated_count"],
        checkpoint="checkpoint_000",
        pair_evaluated_per_hour=manifest["pair_evaluated_per_hour"],
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
    _, selected = load_selection(root)
    runtime_root = root / "runtime" / f"{RUNTIME_PREFIX}_{runtime_date}"
    errors: list[str] = []
    manifest_path = runtime_root / "run_manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        saved_bundle = str(manifest.pop("bundle_sha256", ""))
        if canonical_sha256(manifest) != saved_bundle:
            errors.append("run_manifest_hash")
        if manifest.get("status") != "P4_POCKET_VALIDATION_COMPLETE":
            errors.append("run_status")
        for item in manifest.get("files") or ():
            path = root / str(item["path"])
            if (
                not path.is_file()
                or path.stat().st_size != int(item["bytes"])
                or file_sha256(path) != str(item["sha256"])
            ):
                errors.append("artifact_hash:" + str(item["path"]))
        ledger = pd.read_parquet(runtime_root / "candidate_ledger.parquet")
        expected_ids = {str(row["candidate_id"]) for row in selected}
        if len(ledger) != 80 or set(ledger["candidate_id"].astype(str)) != expected_ids:
            errors.append("candidate_identity")
        if sorted(ledger["completion_ordinal"].astype(int)) != list(range(1, 81)):
            errors.append("completion_ordinal")
        summary = build_summary(ledger.to_dict("records"))
        stored_summary = json.loads(
            (runtime_root / "validation_summary.json").read_text(encoding="utf-8")
        )
        if canonical_sha256(summary) != canonical_sha256(stored_summary):
            errors.append("summary_recompute")
        if (
            int(summary["raw_candidate_count"]) != 80
            or int(summary["behavior_family_deoverlapped_count"]) != 76
        ):
            errors.append("behavior_deoverlap_count")
        forbidden_true = (
            "candidate_generation_performed",
            "optimizer_feedback_written",
            "policy_memory_written",
            "archive_written",
            "promotion_authorized",
        )
        if any(manifest.get(key) is not False for key in forbidden_true):
            errors.append("forbidden_runtime_write")
        if int(manifest.get("oos_read_count", -1)) != 0:
            errors.append("oos_read_count")
        if file_sha256(root / receipt_path) != str(manifest["run_receipt_sha256"]):
            errors.append("run_receipt_hash")
        if receipt.get("run_authorized") is not True:
            errors.append("authorization")
    except Exception as exc:  # independent checker must report, not mask
        errors.append(f"checker_exception:{type(exc).__name__}:{exc}")
    result = {
        "schema_version": 1,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "runtime": str(runtime_root.relative_to(root).as_posix()),
        "checked_utc": pd.Timestamp.now(tz="UTC").isoformat(),
    }
    write_json(runtime_root / "independent_checker.json", result)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("prepare-carrier", "run", "check"))
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--runtime-date", default=DEFAULT_RUNTIME_DATE)
    parser.add_argument("--receipt-path", default=RECEIPT_PATH)
    parser.add_argument("--new-oi-source-root", type=Path)
    parser.add_argument("--previous-extended-cache", type=Path)
    parser.add_argument("--top100-tar", type=Path)
    parser.add_argument("--ranks101-200-tar", type=Path)
    args = parser.parse_args(argv)
    if args.command == "prepare-carrier":
        required = {
            "new_oi_source_root": args.new_oi_source_root,
            "previous_extended_cache": args.previous_extended_cache,
            "top100_tar": args.top100_tar,
            "ranks101_200_tar": args.ranks101_200_tar,
        }
        missing = [name for name, value in required.items() if value is None]
        if missing:
            parser.error("missing required paths: " + ",".join(missing))
        result = prepare_carrier(
            args.repo_root,
            new_oi_source_root=Path(args.new_oi_source_root),
            previous_extended_cache=Path(args.previous_extended_cache),
            top100_tar=Path(args.top100_tar),
            ranks101_200_tar=Path(args.ranks101_200_tar),
            runtime_date=args.runtime_date,
            receipt_path=args.receipt_path,
        )
    elif args.command == "run":
        result = run_gate(
            args.repo_root,
            runtime_date=args.runtime_date,
            receipt_path=args.receipt_path,
        )
    else:
        result = check_gate(
            args.repo_root,
            runtime_date=args.runtime_date,
            receipt_path=args.receipt_path,
        )
    print(json.dumps(result, sort_keys=True, default=str))
    return 0 if result.get("status") != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
