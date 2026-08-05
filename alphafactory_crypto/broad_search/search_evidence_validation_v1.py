"""One-shot no-feedback validation for the final Evidence V1.1 champions.

This adapter deliberately reuses the existing typed compiler, Binance target,
portfolio mapping, pair evaluator, and V2.4 process worker/path projection.  It
does not generate candidates or write optimizer/archive state.
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
    _evaluation_audit_fields,
    _search_ordering_reward,
)
from alphafactory_crypto.broad_search.search_engine_v2_4 import (
    _v24_checkpoint_files,
    _v24_worker_evaluate,
    _v24_worker_initialize,
    _v24_write_batch_projections,
    sweep_v24_static_constructibility,
)


RECEIPT_PATH = "config/crypto_search_evidence_v1_1_validation_receipt.json"
RUNTIME_PREFIX = "crypto_search_evidence_v1_1_validation"
DEFAULT_RUNTIME_DATE = "20260805"
EXPECTED_SELECTION_SHA256 = (
    "C3BD1C0D0940BEE2FAE41B51BD94D11B3684CD93B4E9AD84D125AEC0D5A746DE"
)


def _canonical_sha256(payload: Any) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest().upper()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while block := handle.read(8 * 1024 * 1024):
            digest.update(block)
    return digest.hexdigest().upper()


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".tmp-{os.getpid()}")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def load_validation_receipt(
    repo_root: Path,
    *,
    require_authorized: bool | None = None,
) -> dict[str, Any]:
    path = Path(repo_root) / RECEIPT_PATH
    receipt = json.loads(path.read_text(encoding="utf-8"))
    blockers: list[str] = []
    if int(receipt.get("schema_version", -1)) != 1:
        blockers.append("schema_version")
    if receipt.get("receipt_id") != "CRYPTO_SEARCH_EVIDENCE_V1_1_VALIDATION":
        blockers.append("receipt_id")
    if require_authorized is not None and bool(receipt.get("run_authorized")) is not bool(
        require_authorized
    ):
        blockers.append("run_authorized")
    source = dict(receipt.get("source_evidence") or {})
    selection = dict(receipt.get("selection") or {})
    validation = dict(receipt.get("validation") or {})
    compute = dict(receipt.get("compute") or {})
    boundaries = dict(receipt.get("boundaries") or {})
    if source.get("candidate_ledger_sha256") != (
        "6554BECC35E8586F63505DA4646F41482BEFB80FEE4618B2710C22A35A8D6718"
    ):
        blockers.append("candidate_ledger_sha256")
    if source.get("behavior_archive_sha256") != (
        "182D2ABB810B73C02622BBA51E41F231EFA0AED8A4D1E15B93D48499866C391F"
    ):
        blockers.append("behavior_archive_sha256")
    if selection.get("candidate_count_exact") != 49:
        blockers.append("candidate_count_exact")
    if selection.get("selection_sha256") != EXPECTED_SELECTION_SHA256:
        blockers.append("selection_sha256")
    if validation != {
        "start": "2025-11-01T00:00:00Z",
        "end_exclusive": "2026-01-01T00:00:00Z",
        "role": "DEVELOPMENT_VALIDATION_NO_FEEDBACK",
        "execution_venue": "BINANCE_USD_M",
        "cost_bps": 5.0,
    }:
        blockers.append("validation")
    if compute.get("workers_default") != 10 or compute.get("workers_fallback") != 8:
        blockers.append("workers")
    required_false = (
        "candidate_generation",
        "optimizer_feedback",
        "policy_memory_write",
        "archive_write",
        "backfill",
        "restart",
        "reseed",
        "parameter_tuning",
        "rescue_rerun",
        "holdout_read",
        "oos",
        "promotion",
    )
    if any(boundaries.get(key) is not False for key in required_false):
        blockers.append("boundaries")
    if blockers:
        raise RuntimeError("EVIDENCE_VALIDATION_RECEIPT_INVALID:" + ",".join(blockers))
    return receipt


def _selection_projection(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "candidate_id": str(row["candidate_id"]),
            "candidate_spec_sha256": str(row["candidate_spec_sha256"]),
            "behavior_family_id": str(row["behavior_family_id"]),
            "arm": str(row["arm"]),
            "seed": int(row["seed"]),
            "horizon_hours": int(row["horizon_hours"]),
            "search_reward": float(row["search_reward"]),
            "train_orientation": float(row["train_orientation"]),
        }
        for row in rows
    ]


def select_final_positive_champions(
    repo_root: Path,
    *,
    receipt: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Rebuild the exact final champion cohort from immutable train artifacts."""

    root = Path(repo_root)
    receipt = dict(receipt or load_validation_receipt(root))
    source = dict(receipt["source_evidence"])
    ledger_path = root / str(source["candidate_ledger_path"])
    archive_path = root / str(source["behavior_archive_path"])
    if (
        _file_sha256(ledger_path) != str(source["candidate_ledger_sha256"])
        or _file_sha256(archive_path) != str(source["behavior_archive_sha256"])
    ):
        raise RuntimeError("EVIDENCE_VALIDATION_SOURCE_ARTIFACT_CHANGED")
    ledger = pd.read_parquet(ledger_path)
    archive = pd.read_parquet(archive_path)
    if len(ledger) != int(source["candidate_ledger_row_count"]):
        raise RuntimeError("EVIDENCE_VALIDATION_SOURCE_LEDGER_COUNT_CHANGED")
    champions = archive.loc[
        archive["is_family_champion"].eq(True) & archive["search_reward"].gt(0.0),
        ["exact_expression_id", "behavior_family_id", "arm", "seed"],
    ]
    selected = ledger.merge(
        champions,
        on=["exact_expression_id", "behavior_family_id", "arm", "seed"],
        how="inner",
        validate="one_to_one",
    ).sort_values("candidate_id", kind="stable")
    rows = selected.to_dict("records")
    if (
        len(rows) != 49
        or selected["candidate_id"].nunique() != 49
        or selected["behavior_family_id"].nunique() != 49
        or not selected["search_reward"].gt(0.0).all()
    ):
        raise RuntimeError("EVIDENCE_VALIDATION_COHORT_CHANGED")
    prepared: list[dict[str, Any]] = []
    for row in rows:
        local = dict(row)
        local["candidate"] = json.loads(str(local["candidate_spec_json"]))
        local["source_arm"] = str(local["arm"])
        prepared.append(local)
    projection = _selection_projection(prepared)
    if _canonical_sha256(projection) != str(
        receipt["selection"]["selection_sha256"]
    ):
        raise RuntimeError("EVIDENCE_VALIDATION_SELECTION_CHANGED")
    return prepared


def freeze_selection_before_validation_read(
    repo_root: Path,
    runtime_root: Path,
    *,
    producer_source_sha: str,
    receipt: Mapping[str, Any],
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    output = Path(runtime_root) / "behavior_family_selection_receipt.json"
    if output.exists():
        raise RuntimeError("EVIDENCE_VALIDATION_RUNTIME_ALREADY_EXISTS")
    payload = {
        "schema_version": 1,
        "status": "SELECTION_FROZEN_BEFORE_VALIDATION_READ",
        "producer_source_sha": str(producer_source_sha).lower(),
        "run_receipt_sha256": _file_sha256(Path(repo_root) / RECEIPT_PATH),
        "source_candidate_ledger_sha256": receipt["source_evidence"][
            "candidate_ledger_sha256"
        ],
        "source_behavior_archive_sha256": receipt["source_evidence"][
            "behavior_archive_sha256"
        ],
        "candidate_count": len(rows),
        "selection_sha256": _canonical_sha256(_selection_projection(rows)),
        "candidate_ids": [str(row["candidate_id"]) for row in rows],
        "market_read_performed": False,
        "candidate_generation_performed": False,
        "optimizer_feedback_used": False,
    }
    payload["receipt_sha256"] = _canonical_sha256(payload)
    _write_json(output, payload)
    return payload


def _build_economic_context(
    repo_root: Path,
    *,
    receipt: Mapping[str, Any],
    target_identity_sha256: str,
) -> dict[str, Any]:
    from alphafactory_crypto.broad_search.experiment_authority import (
        resolve_search_economic_receipt,
    )

    source = dict(receipt["source_evidence"])
    base = resolve_search_economic_receipt(
        Path(repo_root), str(source["economic_receipt_path"])
    )
    validation = {
        "role": str(receipt["validation"]["role"]),
        "start": str(receipt["validation"]["start"]),
        "end_exclusive": str(receipt["validation"]["end_exclusive"]),
        "optimizer_feedback_allowed": False,
        "policy_memory_write_allowed": False,
        "candidate_generation_allowed": False,
    }
    partitions = {
        **{key: dict(value) for key, value in dict(base["evidence_partition"]).items()},
        "validation": validation,
    }
    execution = {
        **dict(base["execution"]),
        "target_cache_path": str(receipt["carrier"]["target_cache"]),
        "target_cache_identity_sha256": str(target_identity_sha256),
    }
    return {
        **base,
        "run_authorized": True,
        "run_authorization": {
            "decision_id": str(receipt["decision_id"]),
            "authority": "CURRENT_USER_INSTRUCTION",
            "scope": "ONE_EXACT_49_CHAMPION_DEVELOPMENT_VALIDATION_NO_FEEDBACK",
            "parameter_tuning_allowed": False,
            "seed_change_allowed": False,
            "rescue_rerun_allowed": False,
        },
        "evidence_partition": partitions,
        "validation": validation,
        "execution": execution,
        "receipt_sha256": _file_sha256(Path(repo_root) / RECEIPT_PATH),
    }


def _augment_projection(
    projection: Mapping[str, Any],
    *,
    selected: Mapping[str, Any],
    worker: Mapping[str, Any],
) -> dict[str, Any]:
    output = dict(projection)
    output["train_declared_axis_count"] = int(selected["declared_axis_count"])
    output["primary_analysis_slice"] = bool(
        int(selected["horizon_hours"]) == 4
        and int(selected["declared_axis_count"]) == 2
    )
    if worker.get("error"):
        output.update(
            {
                "validation_search_reward": float("nan"),
                "validation_search_reward_feedback_json": None,
                "validation_behavior_family_id": None,
                "validation_declared_axis_count": None,
                "validation_active_axis_count": None,
                "validation_mechanism_realization_status": None,
            }
        )
        return output
    evaluation = dict(worker["evaluation"])
    feedback = dict(evaluation.get("search_reward_feedback") or {})
    behavior = dict(evaluation.get("behavior") or {})
    realization = dict(evaluation.get("mechanism_realization_provenance") or {})
    output.update(
        {
            "validation_search_reward": float(_search_ordering_reward(evaluation)),
            "validation_search_reward_feedback_json": json.dumps(
                feedback, sort_keys=True, separators=(",", ":"), default=str
            ),
            "validation_primary_search_reward": feedback.get("primary_search_reward"),
            "validation_matched_min_search_reward": feedback.get(
                "matched_min_search_reward"
            ),
            "validation_search_reward_limiting_component": feedback.get(
                "limiting_component"
            ),
            "validation_behavior_family_id": behavior.get("behavior_family_id"),
            "validation_declared_axis_count": realization.get("declared_axis_count"),
            "validation_active_axis_count": realization.get("active_axis_count"),
            "validation_mechanism_realization_status": realization.get("status"),
        }
    )
    output.update(
        {
            f"validation_{key}": value
            for key, value in _evaluation_audit_fields(evaluation).items()
        }
    )
    return output


def _slice_metrics(frame: pd.DataFrame) -> dict[str, Any]:
    evaluated = frame.loc[frame["strict_evaluated"].eq(True)].copy()
    if evaluated.empty:
        return {
            "source_count": int(len(frame)),
            "strict_evaluated_count": 0,
            "candidate_local_failure_count": int(len(frame)),
            "validation_search_reward_positive_count": 0,
            "matched_positive_count": 0,
            "primary_net_positive_count": 0,
            "both_axis_net_positive_count": 0,
            "both_axis_net_lcb_positive_count": 0,
            "train_validation_search_reward_spearman": None,
        }
    left_net = evaluated["validation_left_incremental_net_mean"]
    right_net = evaluated["validation_right_incremental_net_mean"]
    left_lcb = evaluated["validation_left_incremental_net_lcb"]
    right_lcb = evaluated["validation_right_incremental_net_lcb"]
    train_rank = evaluated["train_search_reward"].rank()
    validation_rank = evaluated["validation_search_reward"].rank()
    rank_corr = (
        train_rank.corr(validation_rank)
        if len(evaluated) > 1
        and train_rank.nunique() > 1
        and validation_rank.nunique() > 1
        else float("nan")
    )
    return {
        "source_count": int(len(frame)),
        "strict_evaluated_count": int(len(evaluated)),
        "candidate_local_failure_count": int(len(frame) - len(evaluated)),
        "validation_search_reward_positive_count": int(
            evaluated["validation_search_reward"].gt(0.0).sum()
        ),
        "matched_positive_count": int(evaluated["matched_positive"].sum()),
        "primary_net_positive_count": int(
            evaluated["primary_net_mean"].gt(0.0).sum()
        ),
        "both_axis_net_positive_count": int(
            (left_net.gt(0.0) & right_net.gt(0.0)).sum()
        ),
        "both_axis_net_lcb_positive_count": int(
            (left_lcb.gt(0.0) & right_lcb.gt(0.0)).sum()
        ),
        "train_validation_search_reward_spearman": (
            float(rank_corr) if math.isfinite(float(rank_corr)) else None
        ),
    }


def _build_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    frame = pd.DataFrame(rows)
    all_metrics = _slice_metrics(frame)
    primary = frame.loc[frame["primary_analysis_slice"].eq(True)]
    return {
        "schema_version": 1,
        "status": "VALIDATION_COMPLETE",
        "all_49": all_metrics,
        "primary_4h_two_axis": _slice_metrics(primary),
        "arm": {
            str(arm): _slice_metrics(local)
            for arm, local in frame.groupby("arm", sort=True)
        },
        "horizon": {
            str(int(horizon)): _slice_metrics(local)
            for horizon, local in frame.groupby("horizon_hours", sort=True)
        },
        "interpretation_boundary": (
            "DEVELOPMENT_VALIDATION_ONLY_NOT_GLOBALLY_UNTOUCHED_OOS_OR_PROMOTION"
        ),
    }


def _report(summary: Mapping[str, Any], source_sha: str) -> str:
    all_metrics = dict(summary["all_49"])
    primary = dict(summary["primary_4h_two_axis"])
    return f"""# Crypto Search Evidence V1.1 Champion Validation

- Status: `{summary['status']}`
- Producer source: `{source_sha}`
- Contract: exactly 49 final positive development behavior-family champions; no generation, feedback, backfill, tuning, reseed, OOS, or promotion.
- Partition: `2025-11-01` to `2026-01-01`, Binance USD-M delayed-open target, frozen direction/mapping/evaluator and 5 bps cost.
- Scope: development validation only; this block is not globally untouched confirmation.

## All 49 champions

- Strict evaluated: `{all_metrics['strict_evaluated_count']}/49`
- Candidate-local failures: `{all_metrics['candidate_local_failure_count']}`
- Positive validation search reward: `{all_metrics['validation_search_reward_positive_count']}`
- Matched positive: `{all_metrics['matched_positive_count']}`
- Both matched axes net positive: `{all_metrics['both_axis_net_positive_count']}`
- Both matched axes net-LCB positive: `{all_metrics['both_axis_net_lcb_positive_count']}`
- Train/validation reward rank correlation: `{all_metrics['train_validation_search_reward_spearman']}`

## Predeclared primary slice: 4h x two-axis

- Source: `{primary['source_count']}`
- Strict evaluated: `{primary['strict_evaluated_count']}`
- Positive validation search reward: `{primary['validation_search_reward_positive_count']}`
- Matched positive: `{primary['matched_positive_count']}`
- Both matched axes net positive: `{primary['both_axis_net_positive_count']}`
- Both matched axes net-LCB positive: `{primary['both_axis_net_lcb_positive_count']}`

No candidate is qualified or promoted by this report.
"""


def run_validation(
    repo_root: Path,
    *,
    runtime_date: str = DEFAULT_RUNTIME_DATE,
    producer_source_sha: str | None = None,
) -> dict[str, Any]:
    root = Path(repo_root)
    receipt = load_validation_receipt(root, require_authorized=True)
    observed_sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True
    ).strip().lower()
    source_sha = str(producer_source_sha or observed_sha).lower()
    if source_sha != observed_sha:
        raise RuntimeError("EVIDENCE_VALIDATION_SOURCE_SHA_CHANGED")
    runtime_root = root / "runtime" / f"{RUNTIME_PREFIX}_{runtime_date}"
    if runtime_root.exists():
        raise RuntimeError("EVIDENCE_VALIDATION_RUNTIME_ALREADY_EXISTS")
    runtime_root.mkdir(parents=True)
    selected = select_final_positive_champions(root, receipt=receipt)
    selection_receipt = freeze_selection_before_validation_read(
        root,
        runtime_root,
        producer_source_sha=source_sha,
        receipt=receipt,
        rows=selected,
    )
    carrier_manifest = json.loads(
        (root / str(receipt["carrier"]["manifest_path"])).read_text(encoding="utf-8")
    )
    contract_rows = list(carrier_manifest["contracts"])
    static = sweep_v24_static_constructibility(
        selected_rows=selected, contract_rows=contract_rows
    )
    _write_json(runtime_root / "static_constructibility.json", static)
    target_metadata = json.loads(
        (root / str(receipt["carrier"]["target_cache"]) / "metadata.json").read_text(
            encoding="utf-8"
        )
    )
    if (
        str(carrier_manifest["cache_identity_sha256"])
        != str(receipt["carrier"]["cache_identity_sha256"])
        or str(target_metadata["identity_sha256"])
        != str(receipt["carrier"]["target_identity_sha256"])
        or len(contract_rows) != 115
    ):
        raise RuntimeError("EVIDENCE_VALIDATION_CARRIER_OR_TARGET_CHANGED")
    economic = _build_economic_context(
        root,
        receipt=receipt,
        target_identity_sha256=str(target_metadata["identity_sha256"]),
    )
    frozen = {
        "schema_version": 1,
        "producer_source_sha": source_sha,
        "run_receipt_sha256": _file_sha256(root / RECEIPT_PATH),
        "selection_receipt_sha256": selection_receipt["receipt_sha256"],
        "selection_sha256": receipt["selection"]["selection_sha256"],
        "candidate_count": 49,
        "validation": dict(receipt["validation"]),
        "carrier_cache_identity_sha256": carrier_manifest["cache_identity_sha256"],
        "target_cache_identity_sha256": target_metadata["identity_sha256"],
        "contracts_sha256": _canonical_sha256(contract_rows),
        "workers_default": 10,
        "workers_fallback": 8,
        "candidate_generation": False,
        "optimizer_feedback": False,
        "archive_write": False,
        "holdout_read": False,
    }
    frozen["frozen_contract_sha256"] = _canonical_sha256(frozen)
    _write_json(runtime_root / "frozen_contract.json", frozen)
    started = time.perf_counter()
    active_workers = int(receipt["compute"]["workers_default"])
    memory_fallback_used = False

    def write_status(status: str, **extra: Any) -> None:
        _write_json(
            runtime_root / "producer_status.json",
            {
                "schema_version": 1,
                "status": status,
                "producer_pid": os.getpid(),
                "producer_source_sha": source_sha,
                "heartbeat_utc": pd.Timestamp.now(tz="UTC").isoformat(),
                "source_candidate_count": 49,
                "workers": active_workers,
                "memory_fallback_used": memory_fallback_used,
                "active_wall_seconds": time.perf_counter() - started,
                "candidate_generation_performed": False,
                "optimizer_feedback_written": False,
                "archive_written": False,
                "holdout_read_count": 0,
                **extra,
            },
        )

    cache_root = root / str(receipt["carrier"]["aligned_cache"])
    target_root = root / str(receipt["carrier"]["target_cache"])

    def make_executor(workers: int) -> concurrent.futures.ProcessPoolExecutor:
        return concurrent.futures.ProcessPoolExecutor(
            max_workers=workers,
            initializer=_v24_worker_initialize,
            initargs=(
                str(cache_root),
                str(target_root),
                contract_rows,
                economic,
                str(receipt["validation"]["start"]),
                str(receipt["validation"]["end_exclusive"]),
                str(receipt["validation"]["role"]),
            ),
        )

    write_status("VALIDATION_RUNNING", completed_candidate_count=0)
    payloads = [
        {
            "candidate": row["candidate"],
            "frozen_train_orientation": float(row["train_orientation"]),
        }
        for row in selected
    ]
    with make_executor(active_workers) as executor:
        workers = list(executor.map(_v24_worker_evaluate, payloads, chunksize=1))
    memory_indexes = [
        index for index, row in enumerate(workers) if bool(row.get("memory_error"))
    ]
    if memory_indexes:
        memory_fallback_used = True
        active_workers = int(receipt["compute"]["workers_fallback"])
        with make_executor(active_workers) as executor:
            retried = list(
                executor.map(
                    _v24_worker_evaluate,
                    [payloads[index] for index in memory_indexes],
                    chunksize=1,
                )
            )
        for index, row in zip(memory_indexes, retried):
            workers[index] = row
    if any(bool(row.get("memory_error")) for row in workers):
        write_status("ENGINE_BUDGET_EXHAUSTED_MEMORY")
        raise RuntimeError("EVIDENCE_VALIDATION_MEMORY_FALLBACK_EXHAUSTED")
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
        _augment_projection(item, selected=selected[index], worker=workers[index])
        for index, item in enumerate(projections)
    ]
    pd.DataFrame(rows).to_parquet(temporary / "candidate_ledger.parquet", index=False)
    checkpoint_manifest = {
        "schema_version": 1,
        "checkpoint": "checkpoint_000",
        "producer_source_sha": source_sha,
        "frozen_contract_sha256": frozen["frozen_contract_sha256"],
        "selection_receipt_sha256": selection_receipt["receipt_sha256"],
        "completed_candidate_count": 49,
        "strict_evaluated_count": sum(bool(row["strict_evaluated"]) for row in rows),
        "candidate_local_failure_count": sum(
            not bool(row["strict_evaluated"]) for row in rows
        ),
        "workers": active_workers,
        "memory_fallback_used": memory_fallback_used,
        "files": _v24_checkpoint_files(temporary),
    }
    checkpoint_manifest["manifest_sha256"] = _canonical_sha256(checkpoint_manifest)
    _write_json(temporary / "manifest.json", checkpoint_manifest)
    os.replace(temporary, final_checkpoint)
    ledger_path = runtime_root / "candidate_ledger.parquet"
    shutil.copy2(final_checkpoint / "candidate_ledger.parquet", ledger_path)
    summary = _build_summary(rows)
    _write_json(runtime_root / "validation_summary.json", summary)
    decision = {
        **summary,
        "producer_source_sha": source_sha,
        "selection_receipt_sha256": selection_receipt["receipt_sha256"],
        "frozen_contract_sha256": frozen["frozen_contract_sha256"],
        "arm_qualified": [],
        "promotion_authorized": False,
        "oos": False,
        "automatic_expansion": False,
    }
    _write_json(runtime_root / "final_decision.json", decision)
    reports = root / "reports"
    reports.mkdir(exist_ok=True)
    report_path = reports / f"CRYPTO_SEARCH_EVIDENCE_V1_1_VALIDATION_{runtime_date}.md"
    report_path.write_text(_report(summary, source_sha), encoding="utf-8")
    elapsed = time.perf_counter() - started
    manifest = {
        "schema_version": 1,
        "status": "VALIDATION_COMPLETE",
        "producer_source_sha": source_sha,
        "runtime": str(runtime_root.relative_to(root).as_posix()),
        "report": str(report_path.relative_to(root).as_posix()),
        "run_receipt_sha256": _file_sha256(root / RECEIPT_PATH),
        "selection_receipt_sha256": selection_receipt["receipt_sha256"],
        "frozen_contract_sha256": frozen["frozen_contract_sha256"],
        "candidate_count": 49,
        "strict_evaluated_count": summary["all_49"]["strict_evaluated_count"],
        "candidate_local_failure_count": summary["all_49"][
            "candidate_local_failure_count"
        ],
        "active_wall_seconds": elapsed,
        "pair_evaluated_per_hour": (
            summary["all_49"]["strict_evaluated_count"] * 3600.0 / elapsed
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
        "holdout_read_count": 0,
        "oos": False,
        "promotion_authorized": False,
        "files": [
            {
                "path": str(path.relative_to(root).as_posix()),
                "bytes": path.stat().st_size,
                "sha256": _file_sha256(path),
            }
            for path in (
                ledger_path,
                runtime_root / "validation_summary.json",
                runtime_root / "final_decision.json",
                final_checkpoint / "manifest.json",
                report_path,
            )
        ],
    }
    manifest["bundle_sha256"] = _canonical_sha256(manifest)
    _write_json(runtime_root / "run_manifest.json", manifest)
    write_status(
        "VALIDATION_COMPLETE",
        completed_candidate_count=49,
        strict_evaluated_count=summary["all_49"]["strict_evaluated_count"],
        checkpoint="checkpoint_000",
        pair_evaluated_per_hour=manifest["pair_evaluated_per_hour"],
    )
    return decision


def check_validation(
    repo_root: Path,
    *,
    runtime_date: str = DEFAULT_RUNTIME_DATE,
) -> dict[str, Any]:
    root = Path(repo_root)
    receipt = load_validation_receipt(root)
    runtime_root = root / "runtime" / f"{RUNTIME_PREFIX}_{runtime_date}"
    errors: list[str] = []
    try:
        selected = select_final_positive_champions(root, receipt=receipt)
        selection = json.loads(
            (runtime_root / "behavior_family_selection_receipt.json").read_text(
                encoding="utf-8"
            )
        )
        saved = str(selection.pop("receipt_sha256", ""))
        if _canonical_sha256(selection) != saved:
            errors.append("selection_receipt_hash")
        ledger = pd.read_parquet(runtime_root / "candidate_ledger.parquet")
        if len(ledger) != 49 or ledger["candidate_id"].nunique() != 49:
            errors.append("ledger_count")
        if set(ledger["candidate_id"].astype(str)) != {
            str(row["candidate_id"]) for row in selected
        }:
            errors.append("candidate_identity")
        if not ledger["completion_ordinal"].tolist() == list(range(1, 50)):
            errors.append("completion_ordinal")
        if ledger["candidate_generation_performed"].any():
            errors.append("candidate_generation")
        if ledger["optimizer_feedback_written"].any():
            errors.append("optimizer_feedback")
        if ledger["archive_written"].any():
            errors.append("archive_write")
        strict = ledger.loc[ledger["strict_evaluated"].eq(True)]
        if strict["validation_search_reward"].isna().any():
            errors.append("validation_reward_missing")
        checkpoint = runtime_root / "checkpoints" / "checkpoint_000"
        manifest = json.loads((checkpoint / "manifest.json").read_text(encoding="utf-8"))
        saved_manifest = str(manifest.pop("manifest_sha256", ""))
        if (
            _canonical_sha256(manifest) != saved_manifest
            or manifest["files"] != _v24_checkpoint_files(checkpoint)
        ):
            errors.append("checkpoint_restore")
        run_manifest = json.loads(
            (runtime_root / "run_manifest.json").read_text(encoding="utf-8")
        )
        saved_bundle = str(run_manifest.pop("bundle_sha256", ""))
        if _canonical_sha256(run_manifest) != saved_bundle:
            errors.append("run_manifest_hash")
        for item in run_manifest["files"]:
            path = root / str(item["path"])
            if (
                not path.is_file()
                or path.stat().st_size != int(item["bytes"])
                or _file_sha256(path) != str(item["sha256"])
            ):
                errors.append("run_manifest_file:" + str(item["path"]))
        if (
            run_manifest["candidate_generation_performed"]
            or run_manifest["optimizer_feedback_written"]
            or run_manifest["archive_written"]
            or int(run_manifest["holdout_read_count"]) != 0
            or run_manifest["oos"]
            or run_manifest["promotion_authorized"]
        ):
            errors.append("boundary")
    except Exception as exc:  # independent checker must report, not conceal
        errors.append(f"{type(exc).__name__}:{exc}")
    result = {
        "schema_version": 1,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "runtime": str(runtime_root.relative_to(root).as_posix()),
        "checked_utc": pd.Timestamp.now(tz="UTC").isoformat(),
    }
    _write_json(runtime_root / "independent_checker.json", result)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("run", "check", "select"))
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--runtime-date", default=DEFAULT_RUNTIME_DATE)
    parser.add_argument("--producer-source-sha")
    args = parser.parse_args(argv)
    if args.command == "select":
        rows = select_final_positive_champions(args.repo_root)
        print(json.dumps({"candidate_count": len(rows), "selection_sha256": _canonical_sha256(_selection_projection(rows))}, sort_keys=True))
        return 0
    if args.command == "run":
        result = run_validation(
            args.repo_root,
            runtime_date=args.runtime_date,
            producer_source_sha=args.producer_source_sha,
        )
    else:
        result = check_validation(args.repo_root, runtime_date=args.runtime_date)
    print(json.dumps(result, sort_keys=True, default=str))
    return 0 if result.get("status") != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
