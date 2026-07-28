"""Exact V1.4 Stage-B replay against a Binance executable-price target.

This module does not generate candidates or introduce another evaluator.  It
reconstructs the 1,200 persisted CandidateSpec objects in completion order,
overrides only RawPanelStore.target_return, and delegates every evaluation to
pair18m.evaluate_pair.
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
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd
import psutil

from alphafactory_crypto.instrument_canary.release import sha256_file

from .compositional18m import CandidateSpec
from .expression import FieldContract, TypedExpressionRegistry
from .pair18m import (
    FIXED_COST_BPS,
    evaluate_pair,
    pair_contract_payload,
    strict_pair_feedback,
)
from .panel18m import RawPanelStore
from .runner18m import (
    _compiler_binding,
    _contracts_from_payload,
    _contracts_payload,
    _source_tree_clean_for_run,
)
from .search_engine_v1 import _load_v14_inputs


CONFIG_PATH = "config/crypto_search_engine_v1_4_binance_target_replay.json"
DEFAULT_RUNTIME_DATE = "20260729"
SOURCE_RUNTIME_DATE = "20260728"
TARGET_CACHE_PATH = (
    ".cache/crypto_search_engine_v1_4/binance_open_target_v1"
)
RUNTIME_PREFIX = "runtime/crypto_search_engine_v1_4_binance_target_replay_"
REPORT_PREFIX = "reports/CRYPTO_SEARCH_ENGINE_V1_4_BINANCE_TARGET_REPLAY_"
DEFAULT_WORKERS = 10
FALLBACK_WORKERS = 8
MEMORY_GATE_BYTES = 12 * 1024**3


def _payload_sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            default=str,
        ).encode("utf-8")
    ).hexdigest().upper()


def _git_sha(repo_root: Path) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=repo_root, text=True
    ).strip().lower()


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".tmp-{os.getpid()}")
    temporary.write_text(
        json.dumps(
            value,
            indent=2,
            sort_keys=True,
            ensure_ascii=True,
            default=str,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    os.replace(temporary, path)


def _write_parquet(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".tmp-{os.getpid()}")
    pd.DataFrame(list(rows)).to_parquet(temporary, index=False)
    os.replace(temporary, path)


def _directory_bundle(root: Path) -> dict[str, Any]:
    rows = [
        {
            "path": path.relative_to(root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in sorted(value for value in root.rglob("*") if value.is_file())
    ]
    return {
        "root": str(root),
        "file_count": len(rows),
        "bytes": sum(int(row["bytes"]) for row in rows),
        "bundle_sha256": _payload_sha(rows),
        "files": rows,
    }


def _build_target_arrays(
    price: np.ndarray,
    *,
    horizons: Sequence[int],
    execution_delay: int,
) -> dict[int, np.ndarray]:
    values = np.asarray(price, dtype=float)
    if values.ndim != 2:
        raise ValueError("Binance execution price must be asset-by-time")
    output: dict[int, np.ndarray] = {}
    for raw_horizon in horizons:
        horizon = int(raw_horizon)
        if horizon < 1:
            raise ValueError("target horizon must be positive")
        offset = execution_delay + horizon
        target = np.full(values.shape, np.nan, dtype=np.float32)
        entry = values[:, execution_delay : values.shape[1] - horizon]
        exit_price = values[:, offset:]
        legal = (
            np.isfinite(entry)
            & np.isfinite(exit_price)
            & (entry > 0.0)
            & (exit_price > 0.0)
        )
        local = np.full(entry.shape, np.nan, dtype=np.float32)
        with np.errstate(divide="ignore", invalid="ignore"):
            local[legal] = np.log(exit_price[legal] / entry[legal]).astype(
                np.float32
            )
        target[:, : values.shape[1] - offset] = local
        output[horizon] = target
    return output


def build_binance_target_cache(
    repo_root: Path,
    *,
    source_store: RawPanelStore,
    config: Mapping[str, Any],
) -> dict[str, Any]:
    target_config = dict(config["target"])
    if str(target_config["price_field"]) != "open_price":
        raise ValueError("Binance replay target field changed")
    if float(config["evaluation"]["cost_bps"]) != FIXED_COST_BPS:
        raise ValueError("Binance replay must isolate target from cost changes")
    price_path = source_store.cache_root / "fields" / "open_price.npy"
    identity_payload = {
        "schema_version": 1,
        "source_cache_identity_sha256": source_store.metadata[
            "identity_sha256"
        ],
        "price_field": "open_price",
        "price_file_sha256": sha256_file(price_path),
        "venue": target_config["venue"],
        "source": target_config["source"],
        "formula": target_config["formula"],
        "execution_delay_hours": int(
            target_config["execution_delay_hours"]
        ),
        "horizons_hours": [
            int(value) for value in target_config["horizons_hours"]
        ],
        "positive_price_required": True,
        "missing_value_fill": None,
        "shape": list(source_store.shape),
        "timestamp_sha256": sha256_file(
            source_store.cache_root / "timestamp_ns.npy"
        ),
    }
    identity = _payload_sha(identity_payload)
    cache_root = repo_root / TARGET_CACHE_PATH
    if cache_root.exists():
        metadata = _read_json(cache_root / "metadata.json")
        if metadata.get("identity_sha256") != identity:
            raise ValueError("existing Binance target cache identity changed")
        for horizon in identity_payload["horizons_hours"]:
            record = metadata["target_files"][str(horizon)]
            path = cache_root / str(record["path"])
            if (
                not path.is_file()
                or path.stat().st_size != int(record["bytes"])
                or sha256_file(path) != record["sha256"]
            ):
                raise ValueError("existing Binance target cache file changed")
        return metadata
    cache_root.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(
        tempfile.mkdtemp(
            prefix=f".{cache_root.name}.tmp-",
            dir=str(cache_root.parent),
        )
    )
    try:
        arrays = _build_target_arrays(
            source_store.field("open_price"),
            horizons=identity_payload["horizons_hours"],
            execution_delay=identity_payload["execution_delay_hours"],
        )
        target_files: dict[str, Any] = {}
        for horizon, values in sorted(arrays.items()):
            path = temporary / f"target_return_{horizon}h.npy"
            np.save(path, values)
            target_files[str(horizon)] = {
                "path": path.name,
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
                "finite_count": int(np.isfinite(values).sum()),
            }
        metadata = {
            **identity_payload,
            "identity_sha256": identity,
            "cache_role": "TARGET_OVERRIDE_ONLY_NOT_A_SECOND_PANEL_STORE",
            "target_files": target_files,
        }
        _write_json(temporary / "metadata.json", metadata)
        os.replace(temporary, cache_root)
    except BaseException:
        if temporary.exists():
            shutil.rmtree(temporary)
        raise
    return metadata


@dataclass(frozen=True, slots=True)
class BinanceTargetStore:
    """Delegate all carrier authority except target_return to RawPanelStore."""

    source: RawPanelStore
    target_root: Path

    @property
    def shape(self) -> tuple[int, int]:
        return self.source.shape

    @property
    def symbols(self) -> tuple[str, ...]:
        return self.source.symbols

    @property
    def timestamp_ns(self) -> np.ndarray:
        return self.source.timestamp_ns

    @property
    def metadata(self) -> Mapping[str, Any]:
        return self.source.metadata

    def field(self, field_id: str) -> np.ndarray:
        return self.source.field(field_id)

    def base_eligible(self) -> np.ndarray:
        return self.source.base_eligible()

    def observed(self) -> np.ndarray:
        return self.source.observed()

    def field_available(
        self, field_id: str, time_slice: slice | None = None
    ) -> np.ndarray:
        return self.source.field_available(field_id, time_slice)

    def candidate_support(
        self,
        field_ids: Sequence[str],
        time_slice: slice | None = None,
    ) -> np.ndarray:
        return self.source.candidate_support(field_ids, time_slice)

    def block_slice(self, start: str, end: str) -> slice:
        return self.source.block_slice(start, end)

    def target_return(self, horizon_hours: int) -> np.ndarray:
        return np.load(
            self.target_root / f"target_return_{int(horizon_hours)}h.npy",
            mmap_mode="r",
        )


_WORKER_STORE: BinanceTargetStore | None = None
_WORKER_REGISTRY: TypedExpressionRegistry | None = None
_WORKER_BEHAVIOR_CONTRACT: Mapping[str, Any] | None = None
_WORKER_BLOCK_START = ""
_WORKER_BLOCK_END = ""


def _worker_initialize(
    source_cache_root: str,
    target_cache_root: str,
    contract_rows: Sequence[Mapping[str, Any]],
    behavior_contract: Mapping[str, Any],
    block_start: str,
    block_end: str,
) -> None:
    global _WORKER_STORE, _WORKER_REGISTRY, _WORKER_BEHAVIOR_CONTRACT
    global _WORKER_BLOCK_START, _WORKER_BLOCK_END
    _WORKER_STORE = BinanceTargetStore(
        RawPanelStore.open(Path(source_cache_root)),
        Path(target_cache_root),
    )
    _WORKER_REGISTRY = TypedExpressionRegistry(
        _contracts_from_payload(contract_rows)
    )
    _WORKER_BEHAVIOR_CONTRACT = dict(behavior_contract)
    _WORKER_BLOCK_START = str(block_start)
    _WORKER_BLOCK_END = str(block_end)


def _worker_evaluate(candidate_payload: Mapping[str, Any]) -> dict[str, Any]:
    if (
        _WORKER_STORE is None
        or _WORKER_REGISTRY is None
        or _WORKER_BEHAVIOR_CONTRACT is None
    ):
        raise RuntimeError("Binance target replay worker was not initialized")
    candidate = CandidateSpec.from_dict(candidate_payload)
    process = psutil.Process(os.getpid())
    cpu_started = time.process_time()
    wall_started = time.perf_counter()
    try:
        evaluation = evaluate_pair(
            store=_WORKER_STORE,
            registry=_WORKER_REGISTRY,
            candidate=candidate,
            block_start=_WORKER_BLOCK_START,
            block_end=_WORKER_BLOCK_END,
            block_role="SPENT_DEVELOPMENT_V14_BINANCE_TARGET_EXACT_REPLAY",
            behavior_contract=_WORKER_BEHAVIOR_CONTRACT,
        )
        error = None
        memory_error = False
    except MemoryError as failure:
        evaluation = None
        error = f"{type(failure).__name__}:{failure}"
        memory_error = True
    except (ValueError, FloatingPointError) as failure:
        evaluation = None
        error = f"{type(failure).__name__}:{failure}"
        memory_error = False
    memory = process.memory_info()
    return {
        "candidate_id": candidate.candidate_id,
        "evaluation": evaluation,
        "error": error,
        "memory_error": memory_error,
        "process_cpu_seconds": time.process_time() - cpu_started,
        "wall_seconds": time.perf_counter() - wall_started,
        "worker_rss_bytes": int(memory.rss),
        "worker_private_bytes": int(getattr(memory, "private", memory.rss)),
    }


def _sleeves(
    evaluation: Mapping[str, Any],
) -> tuple[tuple[str, Mapping[str, Any], str], ...]:
    if bool(evaluation["hierarchical_three_axis"]):
        return (
            ("A", evaluation["interaction_left_control"], "STANDALONE"),
            ("B", evaluation["right_control"], "STANDALONE"),
            ("AB", evaluation["control"], "STANDALONE"),
            ("ABC", evaluation["primary"], "STANDALONE"),
            (
                "AB_MINUS_A",
                evaluation["interaction_left_incremental"],
                "INCREMENTAL",
            ),
            (
                "AB_MINUS_B",
                evaluation["interaction_right_incremental"],
                "INCREMENTAL",
            ),
            (
                "ABC_MINUS_AB",
                evaluation["conditional_incremental"],
                "INCREMENTAL",
            ),
        )
    return (
        ("A", evaluation["control"], "STANDALONE"),
        ("B", evaluation["right_control"], "STANDALONE"),
        ("AB", evaluation["primary"], "STANDALONE"),
        ("AB_MINUS_A", evaluation["left_incremental"], "INCREMENTAL"),
        ("AB_MINUS_B", evaluation["right_incremental"], "INCREMENTAL"),
    )


def _monthly_gross_positive_fraction(metrics: Mapping[str, Any]) -> float:
    values = [
        float(row["gross_mean"])
        for row in metrics["month_metrics"]
        if row.get("gross_mean") is not None
        and math.isfinite(float(row["gross_mean"]))
    ]
    return (
        float(np.mean(np.asarray(values, dtype=float) > 0.0))
        if values
        else float("nan")
    )


def _waterfall_rows(
    *,
    source_row: Mapping[str, Any],
    candidate: CandidateSpec,
    evaluation: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    summary: list[dict[str, Any]] = []
    monthly: list[dict[str, Any]] = []
    for sleeve, metrics, role in _sleeves(evaluation):
        feedback = strict_pair_feedback(metrics)
        base = {
            "stage_completion_ordinal": int(
                source_row["stage_completion_ordinal"]
            ),
            "candidate_id": candidate.candidate_id,
            "mechanism_family": candidate.mechanism_family,
            "semantic_tuple": source_row.get("semantic_tuple"),
            "hierarchical_three_axis": bool(
                evaluation["hierarchical_three_axis"]
            ),
            "horizon_hours": int(candidate.horizon_hours),
            "sleeve": sleeve,
            "sleeve_role": role,
        }
        row = {
            **base,
            **{
                key: value
                for key, value in metrics.items()
                if key != "month_metrics"
            },
            "gross_positive_month_fraction": (
                _monthly_gross_positive_fraction(metrics)
            ),
            "strict_distance": float(feedback["distance"]),
            "strict_matched_positive": bool(
                feedback["matched_positive"]
            ),
            "strict_violations_json": json.dumps(
                feedback["violations"], sort_keys=True
            ),
        }
        summary.append(row)
        for month_row in metrics["month_metrics"]:
            monthly.append(
                {
                    **base,
                    **dict(month_row),
                    "gross_positive": (
                        bool(float(month_row["gross_mean"]) > 0.0)
                        if month_row.get("gross_mean") is not None
                        else None
                    ),
                    "net_positive": (
                        bool(float(month_row["net_mean"]) > 0.0)
                        if month_row.get("net_mean") is not None
                        else None
                    ),
                }
            )
    return summary, monthly


def _final_increment(
    evaluation: Mapping[str, Any],
) -> tuple[str, Mapping[str, Any]]:
    if bool(evaluation["hierarchical_three_axis"]):
        return "ABC_MINUS_AB", evaluation["conditional_incremental"]
    return "AB_MINUS_A", evaluation["left_incremental"]


def _replay_row(
    *,
    source_row: Mapping[str, Any],
    candidate: CandidateSpec,
    evaluation: Mapping[str, Any],
    worker: Mapping[str, Any],
) -> dict[str, Any]:
    sleeve, final = _final_increment(evaluation)
    monthly_fraction = _monthly_gross_positive_fraction(final)
    old_net = float(source_row["net_mean"])
    old_cost = float(source_row["cost_mean"])
    return {
        "stage_completion_ordinal": int(
            source_row["stage_completion_ordinal"]
        ),
        "source_completion_ordinal": int(source_row["completion_ordinal"]),
        "candidate_id": candidate.candidate_id,
        "candidate_spec_sha256": _payload_sha(candidate.to_dict()),
        "exact_candidate_identity_preserved": (
            candidate.candidate_id == str(source_row["candidate_id"])
        ),
        "arm": source_row["arm"],
        "seed": int(source_row["seed"]),
        "mechanism_family": candidate.mechanism_family,
        "semantic_tuple": source_row.get("semantic_tuple"),
        "hierarchical_three_axis": bool(
            evaluation["hierarchical_three_axis"]
        ),
        "horizon_hours": int(candidate.horizon_hours),
        "final_increment_sleeve": sleeve,
        "old_pair_reward": float(source_row["pair_reward"]),
        "new_pair_reward": float(evaluation["pair_reward"]),
        "old_matched_positive": bool(source_row["matched_positive"]),
        "new_matched_positive": bool(evaluation["matched_positive"]),
        "old_final_net_mean": old_net,
        "old_final_cost_mean": old_cost,
        "old_final_gross_mean": old_net + old_cost,
        "new_final_gross_mean": float(final["gross_mean"]),
        "new_final_gross_standard_error": float(
            final["gross_standard_error"]
        ),
        "new_final_gross_lcb": float(final["gross_lcb"]),
        "new_final_net_mean": float(final["net_mean"]),
        "new_final_net_lcb": float(final["net_lcb"]),
        "new_final_turnover_mean": float(final["turnover_mean"]),
        "new_final_cost_mean": float(final["cost_mean"]),
        "new_final_positive_month_fraction": float(
            final["positive_month_fraction"]
        ),
        "new_final_gross_positive_month_fraction": monthly_fraction,
        "new_final_worst_month": float(final["worst_month"]),
        "new_final_support": float(final["support"]),
        "left_delta_weight_sha256": evaluation[
            "left_delta_weight_sha256"
        ],
        "right_delta_weight_sha256": evaluation[
            "right_delta_weight_sha256"
        ],
        "interaction_left_delta_weight_sha256": evaluation.get(
            "interaction_left_delta_weight_sha256"
        ),
        "process_cpu_seconds": float(worker["process_cpu_seconds"]),
        "wall_seconds": float(worker["wall_seconds"]),
        "worker_rss_bytes": int(worker["worker_rss_bytes"]),
    }


def _load_source_candidates(
    repo_root: Path,
    config: Mapping[str, Any],
    registry: TypedExpressionRegistry,
) -> tuple[pd.DataFrame, list[CandidateSpec], dict[str, Any]]:
    ledger_path = repo_root / str(config["source_ledger"])
    source = pd.read_parquet(ledger_path)
    selected = (
        source.loc[source["stage"].eq(str(config["source_stage"]))]
        .sort_values("stage_completion_ordinal", kind="stable")
        .reset_index(drop=True)
    )
    expected = int(config["strict_count"])
    if len(selected) != expected:
        raise ValueError("source Stage-B candidate count changed")
    if selected["candidate_id"].nunique() != expected:
        raise ValueError("source Stage-B candidate identities are not unique")
    if selected["stage_completion_ordinal"].tolist() != list(
        range(1, expected + 1)
    ):
        raise ValueError("source Stage-B completion order changed")
    candidates: list[CandidateSpec] = []
    for row in selected.to_dict("records"):
        candidate = CandidateSpec.from_dict(
            json.loads(str(row["candidate_spec_json"]))
        )
        if candidate.candidate_id != str(row["candidate_id"]):
            raise ValueError("source CandidateSpec identity changed")
        assurance = registry.validate(candidate.expression)
        control_assurance = registry.validate(candidate.control)
        if (
            set(assurance.raw_fields) != set(candidate.raw_fields)
            or set(control_assurance.raw_fields) != set(
                candidate.raw_fields
            )
        ):
            raise ValueError("source CandidateSpec compiler contract changed")
        candidates.append(candidate)
    preflight = {
        "status": "PASS",
        "source_ledger": str(config["source_ledger"]),
        "source_ledger_sha256": sha256_file(ledger_path),
        "source_ledger_rows": len(source),
        "selected_stage": str(config["source_stage"]),
        "selected_candidate_count": len(selected),
        "selected_candidate_identity_sha256": _payload_sha(
            selected["candidate_id"].tolist()
        ),
        "selected_candidate_spec_sha256": _payload_sha(
            [
                json.loads(str(value))
                for value in selected["candidate_spec_json"]
            ]
        ),
        "candidate_generation_count": 0,
        "exact_order_preserved": True,
        "compiler_valid_count": len(candidates),
        "sealed_reads": 0,
    }
    return selected, candidates, preflight


def _write_checkpoint(
    *,
    runtime_root: Path,
    checkpoint_index: int,
    source_sha: str,
    frozen_hash: str,
    source_candidate_hash: str,
    target_identity: str,
    replay_rows: Sequence[Mapping[str, Any]],
    waterfall_rows: Sequence[Mapping[str, Any]],
    monthly_rows: Sequence[Mapping[str, Any]],
) -> None:
    root = runtime_root / "checkpoints"
    root.mkdir(parents=True, exist_ok=True)
    target = root / f"checkpoint_{checkpoint_index:03d}"
    if target.exists():
        raise FileExistsError(target)
    temporary = root / f".checkpoint_{checkpoint_index:03d}.tmp-{os.getpid()}"
    if temporary.exists():
        shutil.rmtree(temporary)
    temporary.mkdir(parents=True)
    completed_ids = [str(row["candidate_id"]) for row in replay_rows]
    state = {
        "schema_version": 1,
        "source_sha": source_sha,
        "frozen_contract_sha256": frozen_hash,
        "source_candidate_identity_sha256": source_candidate_hash,
        "target_identity_sha256": target_identity,
        "completed_candidate_count": len(replay_rows),
        "completed_candidate_ids": completed_ids,
        "next_stage_completion_ordinal": len(replay_rows) + 1,
        "candidate_generation_count": 0,
        "policy_state": None,
        "rng_state": None,
    }
    _write_json(temporary / "state.json", state)
    _write_parquet(temporary / "candidate_replay_ledger.parquet", replay_rows)
    _write_parquet(temporary / "full_waterfall.parquet", waterfall_rows)
    _write_parquet(temporary / "monthly_waterfall.parquet", monthly_rows)
    files = [
        {
            "name": path.name,
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in sorted(temporary.iterdir())
    ]
    manifest = {
        "schema_version": 1,
        "checkpoint_index": checkpoint_index,
        "source_sha": source_sha,
        "frozen_contract_sha256": frozen_hash,
        "source_candidate_identity_sha256": source_candidate_hash,
        "target_identity_sha256": target_identity,
        "completed_candidate_count": len(replay_rows),
        "completed_identity_sha256": _payload_sha(completed_ids),
        "state_sha256": _payload_sha(state),
        "files": files,
        "atomic_write": "TEMP_DIRECTORY_THEN_OS_REPLACE",
        "restore_verified": False,
    }
    _write_json(temporary / "manifest.json", manifest)
    restored_state = _read_json(temporary / "state.json")
    restored_rows = pd.read_parquet(
        temporary / "candidate_replay_ledger.parquet"
    )
    if (
        _payload_sha(restored_state) != manifest["state_sha256"]
        or len(restored_rows) != len(replay_rows)
        or _payload_sha(restored_rows["candidate_id"].tolist())
        != manifest["completed_identity_sha256"]
    ):
        shutil.rmtree(temporary)
        raise ValueError("Binance target checkpoint restore failed")
    manifest["restore_verified"] = True
    _write_json(temporary / "manifest.json", manifest)
    os.replace(temporary, target)


def _restore_latest_checkpoint(
    *,
    runtime_root: Path,
    source_sha: str,
    frozen_hash: str,
    source_candidate_hash: str,
    target_identity: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    checkpoints = sorted(
        path
        for path in (runtime_root / "checkpoints").glob("checkpoint_*")
        if path.is_dir()
    )
    if not checkpoints:
        return [], [], []
    path = checkpoints[-1]
    manifest = _read_json(path / "manifest.json")
    expected = {
        "source_sha": source_sha,
        "frozen_contract_sha256": frozen_hash,
        "source_candidate_identity_sha256": source_candidate_hash,
        "target_identity_sha256": target_identity,
    }
    if manifest.get("restore_verified") is not True or any(
        manifest.get(key) != value for key, value in expected.items()
    ):
        raise ValueError("Binance target checkpoint authority changed")
    for record in manifest["files"]:
        local = path / str(record["name"])
        if (
            not local.is_file()
            or local.stat().st_size != int(record["bytes"])
            or sha256_file(local) != record["sha256"]
        ):
            raise ValueError("Binance target checkpoint file changed")
    state = _read_json(path / "state.json")
    replay = pd.read_parquet(
        path / "candidate_replay_ledger.parquet"
    ).to_dict("records")
    waterfall = pd.read_parquet(
        path / "full_waterfall.parquet"
    ).to_dict("records")
    monthly = pd.read_parquet(
        path / "monthly_waterfall.parquet"
    ).to_dict("records")
    if (
        _payload_sha(state) != manifest["state_sha256"]
        or len(replay) != int(manifest["completed_candidate_count"])
        or _payload_sha([str(row["candidate_id"]) for row in replay])
        != manifest["completed_identity_sha256"]
    ):
        raise ValueError("Binance target checkpoint content changed")
    return replay, waterfall, monthly


def _safe_correlation(left: pd.Series, right: pd.Series) -> float | None:
    values = pd.concat([left, right], axis=1).dropna()
    if len(values) < 2:
        return None
    correlation = float(values.iloc[:, 0].corr(values.iloc[:, 1]))
    return correlation if math.isfinite(correlation) else None


def _finalize_metrics(
    replay_rows: Sequence[Mapping[str, Any]],
    config: Mapping[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    frame = pd.DataFrame(list(replay_rows))
    threshold = float(
        config["gross_persistence_gate"][
            "final_increment_monthly_gross_positive_fraction_minimum"
        ]
    )
    gross_lcb_positive = frame["new_final_gross_lcb"].gt(0.0)
    monthly_consistent = (
        frame["new_final_gross_mean"].gt(0.0)
        & frame["new_final_gross_positive_month_fraction"].ge(threshold)
    )
    qualified = gross_lcb_positive & monthly_consistent
    qualified_frame = frame.loc[qualified]
    groups = qualified_frame["semantic_tuple"].fillna(
        "BINARY_BASELINE"
    )
    gate = {
        "final_increment_gross_lcb_positive_count": int(
            gross_lcb_positive.sum()
        ),
        "final_increment_monthly_consistent_count": int(
            monthly_consistent.sum()
        ),
        "joint_gross_persistent_count": int(qualified.sum()),
        "qualified_horizons": sorted(
            int(value)
            for value in qualified_frame["horizon_hours"].unique()
        ),
        "qualified_semantic_groups": sorted(
            str(value) for value in groups.unique()
        ),
    }
    contract = config["gross_persistence_gate"]
    gates = {
        "gross_lcb_positive_minimum": (
            gate["final_increment_gross_lcb_positive_count"]
            >= int(contract["final_increment_gross_lcb_positive_minimum"])
        ),
        "monthly_consistent_minimum": (
            gate["final_increment_monthly_consistent_count"]
            >= int(contract["monthly_consistent_candidate_minimum"])
        ),
        "horizon_breadth": (
            len(gate["qualified_horizons"])
            >= int(contract["minimum_horizons_represented"])
        ),
        "semantic_breadth": (
            len(gate["qualified_semantic_groups"])
            >= int(contract["minimum_semantic_groups_represented"])
        ),
    }
    metrics = {
        "strict_replayed_count": len(frame),
        "exact_candidate_count": int(frame["candidate_id"].nunique()),
        "candidate_generation_count": 0,
        "old_gross_positive_count": int(
            frame["old_final_gross_mean"].gt(0.0).sum()
        ),
        "new_gross_positive_count": int(
            frame["new_final_gross_mean"].gt(0.0).sum()
        ),
        "new_net_positive_count": int(
            frame["new_final_net_mean"].gt(0.0).sum()
        ),
        "new_gross_lcb_positive_count": int(
            gross_lcb_positive.sum()
        ),
        "new_matched_positive_count": int(
            frame["new_matched_positive"].sum()
        ),
        "old_mean_pair_reward": float(frame["old_pair_reward"].mean()),
        "new_mean_pair_reward": float(frame["new_pair_reward"].mean()),
        "old_new_gross_correlation": _safe_correlation(
            frame["old_final_gross_mean"],
            frame["new_final_gross_mean"],
        ),
        "old_new_reward_correlation": _safe_correlation(
            frame["old_pair_reward"],
            frame["new_pair_reward"],
        ),
        "process_cpu_seconds": float(frame["process_cpu_seconds"].sum()),
        "worker_wall_seconds": float(frame["wall_seconds"].sum()),
        "gross_persistence": gate,
        "gross_persistence_gates": gates,
        "gross_persistence_status": (
            "PASS_GROSS_PERSISTS_DIAGNOSTIC"
            if all(gates.values())
            else "HOLD_GROSS_NOT_PERSISTENT"
        ),
    }
    comparisons = [
        {
            "group": "ALL",
            "horizon_hours": None,
            "semantic_group": "ALL",
            "count": len(frame),
            "old_gross_positive_rate": float(
                frame["old_final_gross_mean"].gt(0.0).mean()
            ),
            "new_gross_positive_rate": float(
                frame["new_final_gross_mean"].gt(0.0).mean()
            ),
            "new_gross_lcb_positive_rate": float(
                gross_lcb_positive.mean()
            ),
            "new_net_positive_rate": float(
                frame["new_final_net_mean"].gt(0.0).mean()
            ),
            "old_mean_pair_reward": float(frame["old_pair_reward"].mean()),
            "new_mean_pair_reward": float(frame["new_pair_reward"].mean()),
        }
    ]
    for (horizon, semantic), local in frame.assign(
        semantic_group=frame["semantic_tuple"].fillna("BINARY_BASELINE")
    ).groupby(["horizon_hours", "semantic_group"], sort=True):
        comparisons.append(
            {
                "group": "HORIZON_X_SEMANTIC",
                "horizon_hours": int(horizon),
                "semantic_group": str(semantic),
                "count": len(local),
                "old_gross_positive_rate": float(
                    local["old_final_gross_mean"].gt(0.0).mean()
                ),
                "new_gross_positive_rate": float(
                    local["new_final_gross_mean"].gt(0.0).mean()
                ),
                "new_gross_lcb_positive_rate": float(
                    local["new_final_gross_lcb"].gt(0.0).mean()
                ),
                "new_net_positive_rate": float(
                    local["new_final_net_mean"].gt(0.0).mean()
                ),
                "old_mean_pair_reward": float(
                    local["old_pair_reward"].mean()
                ),
                "new_mean_pair_reward": float(
                    local["new_pair_reward"].mean()
                ),
            }
        )
    return metrics, comparisons


def _report(
    *,
    source_sha: str,
    target_metadata: Mapping[str, Any],
    metrics: Mapping[str, Any],
    decision: Mapping[str, Any],
) -> str:
    gate = metrics["gross_persistence"]
    return "\n".join(
        [
            "# Crypto Search Engine V1.4 Binance Target Exact Replay",
            "",
            f"- Producer source: `{source_sha}`.",
            "- Replay: exact existing V1.4 Stage-B `1,200` CandidateSpec objects in original completion order; new candidates `0`.",
            "- Target: Binance USD-M aggTrades hourly `open_price`, `log(open[t+2+h] / open[t+2])`, horizons `1h/4h`.",
            f"- Target identity: `{target_metadata['identity_sha256']}`.",
            "- Evaluator/mapping/cost: existing pair evaluator, existing mappings, unchanged `5 bps` full-L1 cost.",
            f"- Old/new gross-positive final increments: `{metrics['old_gross_positive_count']}/{metrics['new_gross_positive_count']}`.",
            f"- New net-positive / gross-HAC-LCB-positive / matched-positive: `{metrics['new_net_positive_count']}/{metrics['new_gross_lcb_positive_count']}/{metrics['new_matched_positive_count']}`.",
            f"- Old/new mean pair reward: `{metrics['old_mean_pair_reward']:.6f}` / `{metrics['new_mean_pair_reward']:.6f}`.",
            f"- Joint gross-persistent candidates: `{gate['joint_gross_persistent_count']}`; horizons `{gate['qualified_horizons']}`; semantic groups `{len(gate['qualified_semantic_groups'])}`.",
            f"- Gross persistence gate: `{metrics['gross_persistence_status']}`.",
            f"- Decision: `{decision['next_action']}`.",
            "",
            "## Evidence boundary",
            "",
            "- Complete A/B/AB/ABC and incremental sleeve metrics plus monthly waterfalls are persisted.",
            "- This is spent-development exact replay, not OOS, promotion, challenge, recent, May-stress, forward, or fresh Alpha evidence.",
            "- No CEM, Evolution, operator expansion, turnover optimization, or rescue rerun was started.",
            "",
            "## Bias audit",
            "",
            f"- Decision: `{decision['bias_audit_decision']}`.",
            "- Target venue now matches the Binance USD-M order-flow source; missing target prices remain missing.",
            "- Candidate selection, order, mapping, horizon, eligibility and cost are frozen; only target_return is overridden.",
            "- Gross HAC LCB is diagnostic and does not replace strict pair_reward or grant research qualification.",
            "",
        ]
    )


def run_replay(
    repo_root: Path,
    *,
    runtime_date: str = DEFAULT_RUNTIME_DATE,
    source_sha: str | None = None,
) -> dict[str, Any]:
    config_path = repo_root / CONFIG_PATH
    config = _read_json(config_path)
    runtime_root = repo_root / f"{RUNTIME_PREFIX}{runtime_date}"
    report_path = repo_root / f"{REPORT_PREFIX}{runtime_date}.md"
    actual_sha = _git_sha(repo_root)
    producer_sha = str(source_sha or actual_sha).lower()
    if producer_sha != actual_sha:
        raise ValueError("producer source must equal current HEAD")
    if runtime_root.exists() and (runtime_root / "run_manifest.json").exists():
        raise FileExistsError("completed replay runtime already exists")
    runtime_root.mkdir(parents=True, exist_ok=True)
    if not _source_tree_clean_for_run(
        repo_root, allowed_paths=(runtime_root, report_path)
    ):
        raise ValueError("source tree must be clean before replay")
    (
        source_store,
        contracts,
        behavior_contract,
        v14_identities,
        v14_config,
    ) = _load_v14_inputs(repo_root)
    registry = TypedExpressionRegistry(contracts)
    source_frame, candidates, preflight = _load_source_candidates(
        repo_root, config, registry
    )
    target_metadata = build_binance_target_cache(
        repo_root, source_store=source_store, config=config
    )
    window = v14_config["qualified_continuous_window"]
    block = source_store.block_slice(
        str(window["start"]), str(window["end_exclusive"])
    )
    target_support = {}
    target_store = BinanceTargetStore(
        source_store, repo_root / TARGET_CACHE_PATH
    )
    for horizon in config["target"]["horizons_hours"]:
        target_support[str(horizon)] = int(
            np.isfinite(target_store.target_return(int(horizon))[:, block]).sum()
        )
    preflight = {
        **preflight,
        "producer_source_sha": producer_sha,
        "source_cache_identity_sha256": source_store.metadata[
            "identity_sha256"
        ],
        "target_identity_sha256": target_metadata["identity_sha256"],
        "target_finite_on_qualified_window": target_support,
        "qualified_window": dict(window),
        "cost_bps": FIXED_COST_BPS,
        "workers_requested": DEFAULT_WORKERS,
        "workers_12_forbidden": True,
    }
    frozen_payload = {
        "schema_version": 1,
        "producer_source_sha": producer_sha,
        "experiment_id": config["experiment_id"],
        "authorization": config["authorization"],
        "config_path": CONFIG_PATH,
        "config_sha256": sha256_file(config_path),
        "source_ledger_sha256": preflight["source_ledger_sha256"],
        "source_candidate_identity_sha256": preflight[
            "selected_candidate_identity_sha256"
        ],
        "source_candidate_spec_sha256": preflight[
            "selected_candidate_spec_sha256"
        ],
        "source_cache_identity_sha256": source_store.metadata[
            "identity_sha256"
        ],
        "target_contract": dict(config["target"]),
        "target_identity_sha256": target_metadata["identity_sha256"],
        "target_cache_role": target_metadata["cache_role"],
        "qualified_window": dict(window),
        "compiler_identity": _compiler_binding(repo_root),
        "evaluator_contract": pair_contract_payload(),
        "evaluation": dict(config["evaluation"]),
        "gross_persistence_gate": dict(
            config["gross_persistence_gate"]
        ),
        "budget": dict(config["budget"]),
        "boundaries": dict(config["boundaries"]),
        "v14_input_identities": v14_identities,
        "candidate_generation_count": 0,
    }
    frozen = {
        **frozen_payload,
        "frozen_contract_sha256": _payload_sha(frozen_payload),
    }
    _write_json(runtime_root / "frozen_contract.json", frozen)
    _write_json(runtime_root / "target_contract.json", target_metadata)
    _write_json(runtime_root / "embedded_preflight.json", preflight)
    replay_rows, waterfall_rows, monthly_rows = _restore_latest_checkpoint(
        runtime_root=runtime_root,
        source_sha=producer_sha,
        frozen_hash=frozen["frozen_contract_sha256"],
        source_candidate_hash=preflight[
            "selected_candidate_identity_sha256"
        ],
        target_identity=target_metadata["identity_sha256"],
    )
    completed = len(replay_rows)
    if [row["candidate_id"] for row in replay_rows] != source_frame[
        "candidate_id"
    ].iloc[:completed].tolist():
        raise ValueError("restored replay order changed")
    workers = DEFAULT_WORKERS
    memory_fallback = False
    deadline = time.perf_counter() + int(
        config["budget"]["wall_time_seconds_maximum"]
    )
    executor = concurrent.futures.ProcessPoolExecutor(
        max_workers=workers,
        initializer=_worker_initialize,
        initargs=(
            str(source_store.cache_root),
            str(repo_root / TARGET_CACHE_PATH),
            _contracts_payload(contracts),
            behavior_contract,
            str(window["start"]),
            str(window["end_exclusive"]),
        ),
    )
    checkpoint_size = int(config["checkpoint_size"])
    source_records = source_frame.to_dict("records")
    try:
        while completed < len(candidates):
            if time.perf_counter() >= deadline:
                raise RuntimeError("ENGINE_BUDGET_EXHAUSTED:WALL_TIME")
            remaining_checkpoint = checkpoint_size - (
                completed % checkpoint_size
            )
            count = min(
                workers,
                remaining_checkpoint,
                len(candidates) - completed,
            )
            batch_candidates = candidates[completed : completed + count]
            futures = [
                executor.submit(_worker_evaluate, candidate.to_dict())
                for candidate in batch_candidates
            ]
            results = [future.result() for future in futures]
            peak_rss = max(
                (int(row["worker_rss_bytes"]) for row in results),
                default=0,
            )
            if (
                not memory_fallback
                and workers == DEFAULT_WORKERS
                and (
                    any(bool(row["memory_error"]) for row in results)
                    or peak_rss * DEFAULT_WORKERS > MEMORY_GATE_BYTES
                )
            ):
                executor.shutdown(wait=True)
                workers = FALLBACK_WORKERS
                memory_fallback = True
                executor = concurrent.futures.ProcessPoolExecutor(
                    max_workers=workers,
                    initializer=_worker_initialize,
                    initargs=(
                        str(source_store.cache_root),
                        str(repo_root / TARGET_CACHE_PATH),
                        _contracts_payload(contracts),
                        behavior_contract,
                        str(window["start"]),
                        str(window["end_exclusive"]),
                    ),
                )
            for candidate, worker in zip(batch_candidates, results):
                source_row = source_records[completed]
                if worker["candidate_id"] != candidate.candidate_id:
                    raise ValueError("worker candidate identity changed")
                if worker["evaluation"] is None:
                    raise ValueError(
                        "exact replay evaluation failed: "
                        + str(worker["error"])
                    )
                evaluation = worker["evaluation"]
                replay_rows.append(
                    _replay_row(
                        source_row=source_row,
                        candidate=candidate,
                        evaluation=evaluation,
                        worker=worker,
                    )
                )
                summary, monthly = _waterfall_rows(
                    source_row=source_row,
                    candidate=candidate,
                    evaluation=evaluation,
                )
                waterfall_rows.extend(summary)
                monthly_rows.extend(monthly)
                completed += 1
            if completed % checkpoint_size == 0:
                _write_checkpoint(
                    runtime_root=runtime_root,
                    checkpoint_index=completed // checkpoint_size - 1,
                    source_sha=producer_sha,
                    frozen_hash=frozen["frozen_contract_sha256"],
                    source_candidate_hash=preflight[
                        "selected_candidate_identity_sha256"
                    ],
                    target_identity=target_metadata["identity_sha256"],
                    replay_rows=replay_rows,
                    waterfall_rows=waterfall_rows,
                    monthly_rows=monthly_rows,
                )
    finally:
        executor.shutdown(wait=True)
    if completed != int(config["strict_count"]):
        raise ValueError("exact replay did not complete its frozen count")
    _write_parquet(
        runtime_root / "candidate_replay_ledger.parquet", replay_rows
    )
    _write_parquet(runtime_root / "full_waterfall.parquet", waterfall_rows)
    _write_parquet(
        runtime_root / "monthly_waterfall.parquet", monthly_rows
    )
    metrics, comparison_rows = _finalize_metrics(replay_rows, config)
    _write_parquet(
        runtime_root / "old_new_comparison.parquet", comparison_rows
    )
    waterfall_frame = pd.DataFrame(waterfall_rows)
    constraint_rows = []
    for keys, local in waterfall_frame.groupby(
        ["hierarchical_three_axis", "horizon_hours", "sleeve"],
        sort=True,
    ):
        hierarchical, horizon, sleeve = keys
        violation_counts: dict[str, int] = {}
        for raw in local["strict_violations_json"]:
            for violation in json.loads(str(raw)):
                violation_counts[violation] = (
                    violation_counts.get(violation, 0) + 1
                )
        constraint_rows.append(
            {
                "hierarchical_three_axis": bool(hierarchical),
                "horizon_hours": int(horizon),
                "sleeve": str(sleeve),
                "count": len(local),
                "gross_positive_count": int(
                    local["gross_mean"].gt(0.0).sum()
                ),
                "gross_lcb_positive_count": int(
                    local["gross_lcb"].gt(0.0).sum()
                ),
                "net_positive_count": int(
                    local["net_mean"].gt(0.0).sum()
                ),
                "matched_positive_count": int(
                    local["strict_matched_positive"].sum()
                ),
                "mean_gross": float(local["gross_mean"].mean()),
                "mean_net": float(local["net_mean"].mean()),
                "mean_turnover": float(local["turnover_mean"].mean()),
                "violation_counts_json": json.dumps(
                    violation_counts, sort_keys=True
                ),
            }
        )
    _write_parquet(
        runtime_root / "constraint_bottleneck_matrix.parquet",
        constraint_rows,
    )
    decision = {
        "status": "PASS_EXACT_REPLAY_COMPLETED",
        "gross_persistence_status": metrics[
            "gross_persistence_status"
        ],
        "next_action": (
            "TURNOVER_REPAIR_THEN_BOUNDED_ADAPTIVE_SEARCH_IS_INFORMATION_BEARING"
            if metrics["gross_persistence_status"]
            == "PASS_GROSS_PERSISTS_DIAGNOSTIC"
            else "DO_NOT_OPTIMIZE_TURNOVER_OR_START_ADAPTIVE_SEARCH_ON_THIS_SYNTAX_SURFACE"
        ),
        "adaptive_search_started": False,
        "turnover_optimization_started": False,
        "new_candidate_generation_count": 0,
        "future_new_data_arena_qualified_arms": [],
        "research_qualification": "HOLD_SPENT_DEVELOPMENT_EXACT_REPLAY",
        "bias_audit_decision": "HOLD",
        "sealed_reads": 0,
        "oos": False,
        "promotion": False,
    }
    _write_json(runtime_root / "replay_metrics.json", metrics)
    _write_json(runtime_root / "final_decision.json", decision)
    report_path.write_text(
        _report(
            source_sha=producer_sha,
            target_metadata=target_metadata,
            metrics=metrics,
            decision=decision,
        ),
        encoding="utf-8",
        newline="\n",
    )
    artifacts = [
        {
            "path": path.relative_to(repo_root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in sorted(
            (
                *[
                    value
                    for value in runtime_root.rglob("*")
                    if value.is_file()
                    and value.name != "run_manifest.json"
                ],
                report_path,
            ),
            key=lambda value: str(value),
        )
    ]
    manifest_payload = {
        "schema_version": 1,
        "producer_source_sha": producer_sha,
        "frozen_contract_sha256": frozen[
            "frozen_contract_sha256"
        ],
        "source_candidate_identity_sha256": preflight[
            "selected_candidate_identity_sha256"
        ],
        "target_identity_sha256": target_metadata["identity_sha256"],
        "strict_replayed_count": len(replay_rows),
        "new_candidate_generation_count": 0,
        "checkpoint_count": len(
            list((runtime_root / "checkpoints").glob("checkpoint_*"))
        ),
        "workers_final": workers,
        "memory_fallback_used": memory_fallback,
        "artifacts": artifacts,
    }
    manifest = {
        **manifest_payload,
        "artifact_bundle_sha256": _payload_sha(artifacts),
        "run_identity_sha256": _payload_sha(manifest_payload),
    }
    _write_json(runtime_root / "run_manifest.json", manifest)
    return {
        "result": "PASS",
        "producer_source_sha": producer_sha,
        "strict_replayed_count": len(replay_rows),
        "target_identity_sha256": target_metadata["identity_sha256"],
        "gross_persistence_status": metrics[
            "gross_persistence_status"
        ],
        "next_action": decision["next_action"],
        "artifact_bundle_sha256": manifest[
            "artifact_bundle_sha256"
        ],
    }


def check_replay(
    repo_root: Path, *, runtime_date: str = DEFAULT_RUNTIME_DATE
) -> dict[str, Any]:
    config = _read_json(repo_root / CONFIG_PATH)
    runtime_root = repo_root / f"{RUNTIME_PREFIX}{runtime_date}"
    report_path = repo_root / f"{REPORT_PREFIX}{runtime_date}.md"
    required = (
        "frozen_contract.json",
        "target_contract.json",
        "embedded_preflight.json",
        "candidate_replay_ledger.parquet",
        "full_waterfall.parquet",
        "monthly_waterfall.parquet",
        "old_new_comparison.parquet",
        "constraint_bottleneck_matrix.parquet",
        "replay_metrics.json",
        "final_decision.json",
        "run_manifest.json",
    )
    missing = [
        value for value in required if not (runtime_root / value).is_file()
    ]
    if missing or not report_path.is_file():
        raise FileNotFoundError(f"missing replay artifacts: {missing}")
    frozen = _read_json(runtime_root / "frozen_contract.json")
    preflight = _read_json(runtime_root / "embedded_preflight.json")
    target = _read_json(runtime_root / "target_contract.json")
    manifest = _read_json(runtime_root / "run_manifest.json")
    decision = _read_json(runtime_root / "final_decision.json")
    replay = pd.read_parquet(
        runtime_root / "candidate_replay_ledger.parquet"
    )
    waterfall = pd.read_parquet(runtime_root / "full_waterfall.parquet")
    monthly = pd.read_parquet(runtime_root / "monthly_waterfall.parquet")
    expected = int(config["strict_count"])
    if (
        len(replay) != expected
        or replay["candidate_id"].nunique() != expected
        or not bool(replay["exact_candidate_identity_preserved"].all())
        or replay["stage_completion_ordinal"].tolist()
        != list(range(1, expected + 1))
    ):
        raise ValueError("replay candidate identity/count/order changed")
    source = (
        pd.read_parquet(repo_root / str(config["source_ledger"]))
        .loc[lambda value: value["stage"].eq(config["source_stage"])]
        .sort_values("stage_completion_ordinal", kind="stable")
    )
    if replay["candidate_id"].tolist() != source["candidate_id"].tolist():
        raise ValueError("replay candidates differ from source Stage B")
    if (
        preflight["candidate_generation_count"] != 0
        or decision["new_candidate_generation_count"] != 0
        or manifest["new_candidate_generation_count"] != 0
        or decision["adaptive_search_started"]
        or decision["turnover_optimization_started"]
    ):
        raise ValueError("replay crossed its authorization boundary")
    expected_sleeves = np.where(
        replay["hierarchical_three_axis"], 7, 5
    ).sum()
    if len(waterfall) != int(expected_sleeves):
        raise ValueError("full waterfall sleeve count changed")
    if monthly.empty or set(
        ["A", "B", "AB", "AB_MINUS_A", "AB_MINUS_B"]
    ) - set(waterfall["sleeve"]):
        raise ValueError("full waterfall coverage changed")
    if (
        frozen["producer_source_sha"] != manifest["producer_source_sha"]
        or frozen["target_identity_sha256"]
        != target["identity_sha256"]
        or manifest["strict_replayed_count"] != expected
        or manifest["checkpoint_count"] != math.ceil(
            expected / int(config["checkpoint_size"])
        )
    ):
        raise ValueError("replay manifest authority changed")
    checkpoints = sorted(
        (runtime_root / "checkpoints").glob("checkpoint_*")
    )
    if not checkpoints or any(
        _read_json(path / "manifest.json").get("restore_verified") is not True
        for path in checkpoints
    ):
        raise ValueError("replay checkpoint restore proof changed")
    for record in manifest["artifacts"]:
        path = repo_root / str(record["path"])
        if (
            not path.is_file()
            or path.stat().st_size != int(record["bytes"])
            or sha256_file(path) != record["sha256"]
        ):
            raise ValueError("replay artifact identity changed")
    if _payload_sha(manifest["artifacts"]) != manifest[
        "artifact_bundle_sha256"
    ]:
        raise ValueError("replay artifact bundle changed")
    return {
        "result": "PASS",
        "producer_source_sha": manifest["producer_source_sha"],
        "strict_replayed_count": len(replay),
        "waterfall_rows": len(waterfall),
        "monthly_waterfall_rows": len(monthly),
        "checkpoint_count": len(checkpoints),
        "target_identity_sha256": target["identity_sha256"],
        "gross_persistence_status": decision[
            "gross_persistence_status"
        ],
        "next_action": decision["next_action"],
        "artifact_bundle_sha256": manifest[
            "artifact_bundle_sha256"
        ],
        "sealed_reads": decision["sealed_reads"],
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("run", "check"))
    parser.add_argument("--runtime-date", default=DEFAULT_RUNTIME_DATE)
    parser.add_argument("--source-sha")
    args = parser.parse_args(argv)
    repo_root = Path(__file__).resolve().parents[2]
    if args.command == "run":
        result = run_replay(
            repo_root,
            runtime_date=str(args.runtime_date),
            source_sha=args.source_sha,
        )
    else:
        result = check_replay(
            repo_root, runtime_date=str(args.runtime_date)
        )
    print(json.dumps(result, indent=2, sort_keys=True), flush=True)
    return 0 if result.get("result") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "BinanceTargetStore",
    "_build_target_arrays",
    "_waterfall_rows",
    "build_binance_target_cache",
    "check_replay",
    "run_replay",
]
