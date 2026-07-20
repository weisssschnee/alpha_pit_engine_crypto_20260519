"""Bounded execution-parity canary for the Broad policy evaluator.

This replays eight fixed spent-development pairs. It never proposes candidates,
writes policy feedback, reads report-only data, or changes evaluator semantics.
"""

from __future__ import annotations

import concurrent.futures
import ctypes
import gc
import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Any, Mapping, Sequence

import pandas as pd
import psutil

from alphafactory_crypto.instrument_canary.release import sha256_file

from .compositional18m import CandidateSpec
from .expression import TypedExpressionRegistry
from .pair18m import evaluate_pair
from .panel18m import RawPanelStore
from .runner18m import _contracts_from_payload, _directory_bundle


EPOCH_ID = "CRYPTO_POLICY_ACCELERATION_CANARY_V1"
RUNTIME_FILES = (
    "ACCELERATION_CONTRACT.json",
    "ACCELERATION_RESULTS.json",
    "RESOURCE_AUDIT.json",
)
MANIFEST_FILE = "manifest.json"
PACKAGE_NAMES = (
    "numpy", "pandas", "pyarrow", "numba", "bottleneck",
    "numexpr", "polars", "joblib", "scikit-learn",
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n")


def _payload_sha(value: Any) -> str:
    raw = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest().upper()


def validate_config(config: Mapping[str, Any]) -> None:
    if config.get("epoch_id") != EPOCH_ID or config.get("authorization") != "BOUNDED_EXECUTION_PARITY_ONLY":
        raise ValueError("unexpected acceleration canary identity")
    candidates = config.get("candidates", ())
    if len(candidates) != 8 or len({row["candidate_id"] for row in candidates}) != 8:
        raise ValueError("acceleration canary requires eight fixed unique candidates")
    memory = config.get("memory_policy", {})
    if (
        memory.get("baseline") != "PER_PAIR_FULL_TRIM"
        or memory.get("candidate") != "RSS_THRESHOLD_PLUS_LANE_BOUNDARY"
        or int(memory.get("rss_threshold_bytes", 0)) != 805_306_368
        or memory.get("trial_order") != ["baseline", "candidate", "candidate", "baseline"]
    ):
        raise ValueError("memory policy changed")
    block = config.get("adaptive_block", {})
    if block != {
        "start": "2023-07-01T00:00:00Z",
        "end_exclusive": "2024-07-01T00:00:00Z",
        "evaluation_role": "DEVELOPMENT_ADAPTIVE_FEEDBACK",
    }:
        raise ValueError("adaptive block changed")
    scheduler = config.get("scheduler", {})
    if (
        tuple(scheduler.get("worker_counts", ())) != (8, 10, 12)
        or int(scheduler.get("task_count", 0)) != 20
        or int(scheduler.get("pairs_per_task", 0)) != 4
        or scheduler.get("trial_orders") != [[8, 10, 12], [12, 10, 8]]
        or float(scheduler.get("near_best_ratio", 0.0)) != 0.95
    ):
        raise ValueError("scheduler canary budget changed")
    boundaries = config.get("boundaries", {})
    if boundaries.get("development_block_only") is not True:
        raise PermissionError("development-only block is required")
    forbidden = (
        "policy_feedback", "report_only_reads", "sealed_reads", "forward_reads",
        "candidate_promotion", "cross_sprint_adaptive_memory", "economic_claim",
    )
    if any(boundaries.get(name) is not False for name in forbidden):
        raise PermissionError("acceleration canary boundary opened")


def _full_trim() -> dict[str, Any]:
    collected = gc.collect()
    native_attempted = 0
    native_succeeded = 0
    native_error = 0
    if os.name == "nt":
        native_attempted = 1
        try:
            psapi = ctypes.WinDLL("psapi", use_last_error=True)
            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            psapi.EmptyWorkingSet.argtypes = [ctypes.c_void_p]
            psapi.EmptyWorkingSet.restype = ctypes.c_int
            kernel32.GetCurrentProcess.restype = ctypes.c_void_p
            ctypes.set_last_error(0)
            native_succeeded = int(bool(psapi.EmptyWorkingSet(kernel32.GetCurrentProcess())))
            if not native_succeeded:
                native_error = int(ctypes.get_last_error())
        except (AttributeError, OSError):
            native_error = int(ctypes.get_last_error()) if hasattr(ctypes, "get_last_error") else -1
    return {
        "gc_collected": int(collected),
        "native_attempted": native_attempted,
        "native_succeeded": native_succeeded,
        "native_failed": native_attempted - native_succeeded,
        "native_error": native_error,
    }


def _semantic_projection(evaluation: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in evaluation.items() if key != "timings"}


def _trim_decision(
    trim_mode: str, *, current_rss: int, rss_threshold_bytes: int, is_lane_boundary: bool
) -> tuple[bool, bool]:
    if trim_mode == "PER_PAIR_FULL_TRIM":
        return True, False
    if trim_mode == "RSS_THRESHOLD_PLUS_LANE_BOUNDARY":
        threshold_reached = current_rss >= rss_threshold_bytes
        return threshold_reached or is_lane_boundary, threshold_reached
    raise ValueError(f"unknown trim mode: {trim_mode}")


def _batch_worker(
    task_id: str,
    cache_root: str,
    contract_rows: Sequence[Mapping[str, Any]],
    candidate_rows: Sequence[Mapping[str, Any]],
    trim_mode: str,
    rss_threshold_bytes: int,
    adaptive_block: Mapping[str, str],
) -> dict[str, Any]:
    store = RawPanelStore.open(Path(cache_root))
    registry = TypedExpressionRegistry(_contracts_from_payload(contract_rows))
    process = psutil.Process(os.getpid())
    peak_rss = process.memory_info().rss
    peak_private = getattr(process.memory_info(), "private", peak_rss)
    trim_count = 0
    threshold_trim_count = 0
    collected_objects = 0
    native_trim_attempted = 0
    native_trim_succeeded = 0
    native_trim_failed = 0
    native_trim_errors: set[int] = set()
    rows: list[dict[str, Any]] = []
    started = time.perf_counter()
    for index, candidate_row in enumerate(candidate_rows):
        candidate = CandidateSpec.from_dict(candidate_row["candidate_spec"])
        pair_started = time.perf_counter()
        evaluation = evaluate_pair(
            store=store,
            registry=registry,
            candidate=candidate,
            block_start=str(adaptive_block["start"]),
            block_end=str(adaptive_block["end_exclusive"]),
            block_role=str(adaptive_block["evaluation_role"]),
        )
        semantic = _semantic_projection(evaluation)
        observed_delta = str(evaluation["incremental"]["weight_sha256"])
        rows.append(
            {
                "task_id": task_id,
                "candidate_id": candidate.candidate_id,
                "semantic_sha256": _payload_sha(semantic),
                "delta_weight_sha256": observed_delta,
                "expected_delta_weight_sha256": candidate_row["expected_delta_weight_sha256"],
                "source_semantic_sha256": candidate_row["source_semantic_sha256"],
                "expected_pair_reward": candidate_row["expected_pair_reward"],
                "pair_reward": float(evaluation["pair_reward"]),
                "pair_seconds": time.perf_counter() - pair_started,
            }
        )
        peak_rss = max(peak_rss, int(evaluation["timings"]["peak_rss_bytes"]))
        peak_private = max(
            peak_private, int(evaluation["timings"]["peak_private_bytes"])
        )
        del evaluation, semantic
        current_rss = process.memory_info().rss
        is_lane_boundary = index == len(candidate_rows) - 1
        should_trim, threshold_reached = _trim_decision(
            trim_mode,
            current_rss=current_rss,
            rss_threshold_bytes=rss_threshold_bytes,
            is_lane_boundary=is_lane_boundary,
        )
        if should_trim:
            trim = _full_trim()
            collected_objects += int(trim["gc_collected"])
            native_trim_attempted += int(trim["native_attempted"])
            native_trim_succeeded += int(trim["native_succeeded"])
            native_trim_failed += int(trim["native_failed"])
            if int(trim["native_error"]):
                native_trim_errors.add(int(trim["native_error"]))
            trim_count += 1
            threshold_trim_count += int(threshold_reached)
    return {
        "task_id": task_id,
        "rows": rows,
        "elapsed_seconds": time.perf_counter() - started,
        "peak_rss_bytes": peak_rss,
        "peak_private_bytes": peak_private,
        "final_rss_bytes": process.memory_info().rss,
        "trim_count": trim_count,
        "threshold_trim_count": threshold_trim_count,
        "lane_boundary_trim_count": int(bool(candidate_rows)),
        "collected_objects": collected_objects,
        "native_trim_attempted": native_trim_attempted,
        "native_trim_succeeded": native_trim_succeeded,
        "native_trim_failed": native_trim_failed,
        "native_trim_errors": sorted(native_trim_errors),
    }


def _run_tasks(
    *,
    cache_root: Path,
    contract_rows: Sequence[Mapping[str, Any]],
    tasks: Sequence[Mapping[str, Any]],
    trim_mode: str,
    threshold: int,
    max_workers: int,
    adaptive_block: Mapping[str, str],
) -> dict[str, Any]:
    started = time.perf_counter()
    outputs: list[dict[str, Any]] = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(
                _batch_worker,
                str(task["task_id"]),
                str(cache_root),
                list(contract_rows),
                list(task["candidates"]),
                trim_mode,
                threshold,
                dict(adaptive_block),
            )
            for task in tasks
        ]
        for future in concurrent.futures.as_completed(futures):
            outputs.append(future.result())
    outputs.sort(key=lambda row: str(row["task_id"]))
    wall = time.perf_counter() - started
    pair_count = sum(len(row["rows"]) for row in outputs)
    return {
        "max_workers": max_workers,
        "trim_mode": trim_mode,
        "task_count": len(tasks),
        "pair_count": pair_count,
        "wall_seconds": wall,
        "pairs_per_second": pair_count / wall,
        "maximum_worker_peak_rss_bytes": max(row["peak_rss_bytes"] for row in outputs),
        "maximum_worker_peak_private_bytes": max(row["peak_private_bytes"] for row in outputs),
        "sum_worker_seconds": sum(row["elapsed_seconds"] for row in outputs),
        "trim_count": sum(row["trim_count"] for row in outputs),
        "threshold_trim_count": sum(row["threshold_trim_count"] for row in outputs),
        "lane_boundary_trim_count": sum(row["lane_boundary_trim_count"] for row in outputs),
        "native_trim_attempted": sum(row["native_trim_attempted"] for row in outputs),
        "native_trim_succeeded": sum(row["native_trim_succeeded"] for row in outputs),
        "native_trim_failed": sum(row["native_trim_failed"] for row in outputs),
        "native_trim_errors": sorted(
            {error for row in outputs for error in row["native_trim_errors"]}
        ),
        "tasks": outputs,
    }


def _flat_rows(run: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [row for task in run["tasks"] for row in task["rows"]]


def _semantic_map(run: Mapping[str, Any]) -> dict[str, str]:
    return {row["candidate_id"]: row["semantic_sha256"] for row in _flat_rows(run)}


def _source_parity(row: Mapping[str, Any]) -> bool:
    return bool(
        row["semantic_sha256"] == row["source_semantic_sha256"]
        and row["delta_weight_sha256"] == row["expected_delta_weight_sha256"]
        and float(row["pair_reward"]) == float(row["expected_pair_reward"])
    )


def _ledger_rows(
    run: Mapping[str, Any], *, phase: str, trial_id: str, worker_count: int
) -> list[dict[str, Any]]:
    ledger: list[dict[str, Any]] = []
    for row in _flat_rows(run):
        ledger.append(
            {
                "phase": phase,
                "trial_id": trial_id,
                "worker_count": worker_count,
                "task_id": row["task_id"],
                "candidate_id": row["candidate_id"],
                "semantic_sha256": row["semantic_sha256"],
                "source_semantic_sha256": row["source_semantic_sha256"],
                "delta_weight_sha256": row["delta_weight_sha256"],
                "expected_delta_weight_sha256": row["expected_delta_weight_sha256"],
                "pair_reward": row["pair_reward"],
                "expected_pair_reward": row["expected_pair_reward"],
                "source_parity": _source_parity(row),
                "pair_seconds": row["pair_seconds"],
            }
        )
    return ledger


def _resource_projection(run: Mapping[str, Any]) -> dict[str, Any]:
    projected = {key: value for key, value in run.items() if key != "tasks"}
    projected["task_metrics"] = [
        {key: value for key, value in task.items() if key != "rows"}
        for task in run["tasks"]
    ]
    return projected


def _select_worker_limit(stats: Sequence[Mapping[str, Any]], near_best_ratio: float) -> int | None:
    eligible = [row for row in stats if row.get("eligible") is True]
    if not eligible:
        return None
    best = max(float(row["pairs_per_second"]) for row in eligible)
    near_best = [
        int(row["worker_count"])
        for row in eligible
        if float(row["pairs_per_second"]) >= best * near_best_ratio
    ]
    return min(near_best)


def _aggregate_scheduler_trials(
    trials: Sequence[Mapping[str, Any]], worker_counts: Sequence[int]
) -> list[dict[str, Any]]:
    aggregates: list[dict[str, Any]] = []
    for worker_count in worker_counts:
        matching = [row for row in trials if int(row["worker_count"]) == int(worker_count)]
        aggregates.append(
            {
                "worker_count": int(worker_count),
                "trial_count": len(matching),
                "pair_count": sum(int(row["pair_count"]) for row in matching),
                "pairs_per_second": median(
                    float(row["pairs_per_second"]) for row in matching
                ),
                "minimum_pairs_per_second": min(
                    float(row["pairs_per_second"]) for row in matching
                ),
                "maximum_worker_peak_rss_bytes": max(
                    int(row["maximum_worker_peak_rss_bytes"]) for row in matching
                ),
                "estimated_aggregate_peak_rss_bytes": max(
                    int(row["estimated_aggregate_peak_rss_bytes"]) for row in matching
                ),
                "semantic_parity": "PASS"
                if all(row["semantic_parity"] == "PASS" for row in matching)
                else "FAIL",
                "native_trim_pass": all(row["native_trim_pass"] for row in matching),
                "eligible": all(row["eligible"] for row in matching),
            }
        )
    return aggregates


def _package_matrix() -> dict[str, str]:
    versions: dict[str, str] = {}
    for name in PACKAGE_NAMES:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = "NOT_INSTALLED"
    return versions


def _power_plan() -> str:
    if os.name != "nt":
        return "NOT_WINDOWS"
    completed = subprocess.run(
        ["powercfg", "/getactivescheme"], capture_output=True, text=True, check=False
    )
    return (completed.stdout or completed.stderr).strip()


def _background_python_snapshot() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    current_pid = os.getpid()
    for process in psutil.process_iter(
        ("pid", "name", "cmdline", "memory_info", "cpu_times")
    ):
        try:
            if process.pid == current_pid or "python" not in str(process.info["name"]).lower():
                continue
            cmdline = process.info.get("cmdline") or ()
            script = next(
                (Path(value).name for value in cmdline if str(value).lower().endswith(".py")),
                "UNKNOWN",
            )
            memory = process.info["memory_info"]
            cpu_times = process.info["cpu_times"]
            rows.append(
                {
                    "pid": process.pid,
                    "name": process.info["name"],
                    "script": script,
                    "rss_bytes": int(memory.rss),
                    "cpu_seconds": float(cpu_times.user + cpu_times.system),
                }
            )
        except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
            continue
    return sorted(rows, key=lambda row: int(row["pid"]))


def _git_commit_exists(repo_root: Path, sha: str) -> bool:
    return subprocess.run(
        ["git", "cat-file", "-e", f"{sha}^{{commit}}"], cwd=repo_root,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
    ).returncode == 0


def _load_candidates(repo_root: Path, config: Mapping[str, Any]) -> list[dict[str, Any]]:
    source = config["source_evidence"]
    frame = pd.read_parquet(
        repo_root / source["pair_path"],
        columns=(
            "candidate_id", "candidate_spec_json", "delta_weight_sha256",
            "pair_evaluation_status", "pair_reward", "evaluation_json",
        ),
    )
    loaded: list[dict[str, Any]] = []
    for expected in config["candidates"]:
        rows = frame[frame["candidate_id"] == expected["candidate_id"]]
        specs = sorted(set(rows["candidate_spec_json"].astype(str)))
        deltas = sorted(set(rows["delta_weight_sha256"].astype(str)))
        rewards = sorted(set(float(value) for value in rows["pair_reward"]))
        source_evaluations = [
            json.loads(value) for value in rows["evaluation_json"].astype(str)
        ]
        semantic_hashes = sorted(
            {_payload_sha(_semantic_projection(value)) for value in source_evaluations}
        )
        statuses = set(rows["pair_evaluation_status"].astype(str))
        if (
            len(specs) != 1
            or len(rewards) != 1
            or len(semantic_hashes) != 1
            or deltas != [expected["expected_delta_weight_sha256"]]
            or statuses != {"PASS"}
        ):
            raise ValueError(f"candidate source identity mismatch: {expected['candidate_id']}")
        block = config["adaptive_block"]
        if any(
            value.get("block_start") != block["start"]
            or value.get("block_end_exclusive") != block["end_exclusive"]
            or value.get("block_role") != block["evaluation_role"]
            for value in source_evaluations
        ):
            raise ValueError(f"candidate block identity mismatch: {expected['candidate_id']}")
        loaded.append(
            {
                "candidate_id": expected["candidate_id"],
                "candidate_spec": json.loads(specs[0]),
                "expected_delta_weight_sha256": expected["expected_delta_weight_sha256"],
                "expected_pair_reward": rewards[0],
                "source_semantic_sha256": semantic_hashes[0],
            }
        )
    return loaded


def _render_report(contract: Mapping[str, Any], results: Mapping[str, Any], resource: Mapping[str, Any]) -> str:
    selected = results["decision"]["selected_worker_limit"]
    parity = results["parity"]
    baseline_wall = float(parity["baseline_median_wall_seconds"])
    candidate_wall = float(parity["candidate_median_wall_seconds"])
    trim_speedup = baseline_wall / candidate_wall if candidate_wall else 0.0
    baseline_trims = sum(
        int(row["trim_count"]) for row in parity["trials"] if row["mode"] == "baseline"
    )
    candidate_trims = sum(
        int(row["trim_count"]) for row in parity["trials"] if row["mode"] == "candidate"
    )
    scheduler_lines = [
        f"- {row['worker_count']} workers: two-trial median "
        f"{row['pairs_per_second']:.4f} pairs/s, minimum {row['minimum_pairs_per_second']:.4f}, "
        f"peak worker RSS {row['maximum_worker_peak_rss_bytes']:,} B, "
        f"source parity `{row['semantic_parity']}`, native trim `{row['native_trim_pass']}`"
        for row in results["scheduler"]
    ]
    packages = resource["environment"]["packages"]
    package_line = ", ".join(f"{name}={value}" for name, value in packages.items())
    background_scripts = sorted(
        {
            row["script"]
            for side in ("before", "after")
            for row in resource["host_load"][side]["background_python"]
        }
    )
    background_line = ", ".join(background_scripts) if background_scripts else "NONE"
    return "\n".join(
        [
            "# Crypto Policy Acceleration Canary V1",
            "",
            f"Status: `{results['result']}`",
            "",
            "## Exact parity",
            "",
            f"Eight fixed spent-development pairs across ABBA trials: `{parity['result']}`. "
            f"Per-pair full trim used {baseline_trims} trims; threshold plus lane-boundary used {candidate_trims}.",
            f"Median wall time baseline/candidate: {baseline_wall:.3f}s / {candidate_wall:.3f}s "
            f"({trim_speedup:.3f}x).",
            "Candidate identity, frozen-source complete non-timing evaluation payload, reward, replay hashes, and delta-weight hash are exact.",
            "",
            "## Worker scheduling",
            "",
            *scheduler_lines,
            "",
            f"Selected next development-Arena launch limit: `{selected}` (smallest configuration within 95% of best two-order median throughput).",
            "This is a bounded 20-lane x 4-pair scheduler canary, not a permanent global or 128-pair-lane guarantee.",
            "",
            "## Runtime reality",
            "",
            f"- Python: `{resource['environment']['python_executable']}`",
            f"- Packages: {package_line}",
            f"- Background Python observed: `{background_line}`; throughput is qualified only for this recorded co-run state.",
            "- Hot path: NumPy/pandas evaluator over the pinned memmap; no Numba, Polars, Joblib, or successive halving is active.",
            "- Applied: RSS-threshold trim at 768 MiB plus mandatory lane-boundary trim; two-order bounded worker selection.",
            "- Not applied: evaluator approximation, JIT rewrite, cache-key relaxation, candidate reuse, or policy feedback.",
            "",
            "## Next launch contract",
            "",
            "- `use_fast_context`: false / not implemented",
            f"- `development_arena_worker_limit`: {selected}",
            "- `successive_halving`: false",
            "- cache: exact raw bundle, source, compiler, candidate, adaptive block, mapping, delay, and cost identities remain required",
            "",
            "This canary changes execution guidance only. It makes no economic, OOS, forward, challenge, candidate, or promotion claim. The producer implementation is temporary and may be evicted after evidence closure.",
            "",
        ]
    )


def run_canary(repo_root: Path, *, config_path: Path, source_sha: str) -> dict[str, Any]:
    config = _read_json(config_path)
    validate_config(config)
    source_ref = subprocess.check_output(
        ["git", "rev-parse", f"{source_sha}^{{commit}}"], cwd=repo_root, text=True
    ).strip()
    if source_ref != subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=repo_root, text=True
    ).strip():
        raise ValueError("source SHA must equal checked-out HEAD")
    worktree_changes = subprocess.check_output(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=repo_root,
        text=True,
    ).strip()
    if worktree_changes:
        raise ValueError("worktree must be fully clean")
    source = config["source_evidence"]
    for key in ("manifest", "contract", "pair"):
        path = repo_root / source[f"{key}_path"]
        if sha256_file(path) != source[f"{key}_sha256"]:
            raise ValueError(f"{key} source identity changed")
    original_manifest = _read_json(repo_root / source["manifest_path"])
    if original_manifest.get("bundle_sha256") != source["bundle_sha256"]:
        raise ValueError("original bundle identity changed")
    cache_root = repo_root / config["cache_root"]
    cache_before = _directory_bundle(cache_root)
    if cache_before != config["expected_cache_bundle"]:
        raise ValueError("raw cache bundle changed")
    producer_contract = _read_json(repo_root / source["contract_path"])
    producer_block = producer_contract.get("adaptive_block", {})
    if (
        producer_block.get("start") != config["adaptive_block"]["start"]
        or producer_block.get("end_exclusive")
        != config["adaptive_block"]["end_exclusive"]
    ):
        raise ValueError("producer adaptive block changed")
    candidates = _load_candidates(repo_root, config)
    contract_rows = producer_contract["field_contracts"]
    threshold = int(config["memory_policy"]["rss_threshold_bytes"])
    host_before = {
        "cpu_percent": psutil.cpu_percent(interval=0.5),
        "background_python": _background_python_snapshot(),
    }

    adaptive_block = config["adaptive_block"]
    execution_ledger: list[dict[str, Any]] = []
    parity_trials: list[dict[str, Any]] = []
    parity_resources: list[dict[str, Any]] = []
    for trial_index, label in enumerate(config["memory_policy"]["trial_order"], start=1):
        trial_id = f"parity-{trial_index:02d}-{label}"
        run = _run_tasks(
            cache_root=cache_root,
            contract_rows=contract_rows,
            tasks=({"task_id": trial_id, "candidates": candidates},),
            trim_mode=config["memory_policy"][label],
            threshold=threshold,
            max_workers=1,
            adaptive_block=adaptive_block,
        )
        rows = _ledger_rows(run, phase="memory_parity", trial_id=trial_id, worker_count=1)
        execution_ledger.extend(rows)
        source_pass = all(row["source_parity"] for row in rows)
        native_pass = os.name != "nt" or int(run["native_trim_failed"]) == 0
        parity_trials.append(
            {
                "trial_id": trial_id,
                "mode": label,
                "pair_count": len(rows),
                "wall_seconds": run["wall_seconds"],
                "pairs_per_second": run["pairs_per_second"],
                "trim_count": run["trim_count"],
                "threshold_trim_count": run["threshold_trim_count"],
                "native_trim_pass": native_pass,
                "source_parity": "PASS" if source_pass else "FAIL",
            }
        )
        parity_resources.append(
            {"trial_id": trial_id, "mode": label, **_resource_projection(run)}
        )
    parity_pass = all(
        row["source_parity"] == "PASS" and row["native_trim_pass"] is True
        for row in parity_trials
    )

    scheduler_trials: list[dict[str, Any]] = []
    scheduler_resources: list[dict[str, Any]] = []
    pairs_per_task = int(config["scheduler"]["pairs_per_task"])
    tasks = [
        {
            "task_id": f"scheduler-lane-{index:02d}",
            "candidates": [
                candidates[(index * pairs_per_task + offset) % len(candidates)]
                for offset in range(pairs_per_task)
            ],
        }
        for index in range(int(config["scheduler"]["task_count"]))
    ]
    max_worker_rss = int(config["scheduler"]["maximum_worker_peak_rss_bytes"])
    max_aggregate = int(config["scheduler"]["maximum_aggregate_peak_rss_bytes"])
    for round_index, order in enumerate(config["scheduler"]["trial_orders"], start=1):
        for order_index, worker_count in enumerate(order, start=1):
            worker_count = int(worker_count)
            trial_id = f"scheduler-r{round_index}-p{order_index}-w{worker_count}"
            run = _run_tasks(
                cache_root=cache_root,
                contract_rows=contract_rows,
                tasks=tasks,
                trim_mode=config["memory_policy"]["candidate"],
                threshold=threshold,
                max_workers=worker_count,
                adaptive_block=adaptive_block,
            )
            rows = _ledger_rows(
                run, phase="scheduler", trial_id=trial_id, worker_count=worker_count
            )
            execution_ledger.extend(rows)
            source_pass = all(row["source_parity"] for row in rows)
            aggregate = int(run["maximum_worker_peak_rss_bytes"]) * min(
                worker_count, len(tasks)
            )
            native_pass = os.name != "nt" or int(run["native_trim_failed"]) == 0
            eligible = bool(
                source_pass
                and native_pass
                and int(run["maximum_worker_peak_rss_bytes"]) <= max_worker_rss
                and aggregate <= max_aggregate
            )
            scheduler_trials.append(
                {
                    "trial_id": trial_id,
                    "round": round_index,
                    "order_position": order_index,
                    "worker_count": worker_count,
                    "task_count": len(tasks),
                    "pair_count": len(rows),
                    "wall_seconds": run["wall_seconds"],
                    "pairs_per_second": run["pairs_per_second"],
                    "maximum_worker_peak_rss_bytes": run["maximum_worker_peak_rss_bytes"],
                    "estimated_aggregate_peak_rss_bytes": aggregate,
                    "semantic_parity": "PASS" if source_pass else "FAIL",
                    "native_trim_pass": native_pass,
                    "eligible": eligible,
                }
            )
            scheduler_resources.append(
                {
                    "trial_id": trial_id,
                    "round": round_index,
                    "order_position": order_index,
                    **_resource_projection(run),
                }
            )
    scheduler_results = _aggregate_scheduler_trials(
        scheduler_trials, config["scheduler"]["worker_counts"]
    )
    selected = _select_worker_limit(
        scheduler_results, float(config["scheduler"]["near_best_ratio"])
    )
    cache_after = _directory_bundle(cache_root)
    result = "PASS" if parity_pass and selected is not None and cache_after == cache_before else "FAIL"
    runtime_root = repo_root / config["outputs"]["runtime_root"]
    report_path = repo_root / config["outputs"]["report"]
    contract = {
        "schema_version": 1,
        "epoch_id": EPOCH_ID,
        "producer_source_sha": source_ref,
        "config_path": config_path.relative_to(repo_root).as_posix(),
        "config_sha256": sha256_file(config_path),
        "frozen_config": config,
        "source_evidence": source,
        "raw_cache_before": cache_before,
        "candidate_ids": [row["candidate_id"] for row in candidates],
        "unique_pair_count": 8,
        "total_pair_executions": len(execution_ledger),
        "adaptive_block": adaptive_block,
        "memory_policy": config["memory_policy"],
        "scheduler": config["scheduler"],
        "boundaries": config["boundaries"],
    }
    results = {
        "schema_version": 1,
        "epoch_id": EPOCH_ID,
        "result": result,
        "parity": {
            "result": "PASS" if parity_pass else "FAIL",
            "candidate_count": len(candidates),
            "trial_count": len(parity_trials),
            "trials": parity_trials,
            "baseline_median_wall_seconds": median(
                row["wall_seconds"] for row in parity_trials if row["mode"] == "baseline"
            ),
            "candidate_median_wall_seconds": median(
                row["wall_seconds"] for row in parity_trials if row["mode"] == "candidate"
            ),
        },
        "scheduler": scheduler_results,
        "scheduler_trials": scheduler_trials,
        "execution_ledger": execution_ledger,
        "decision": {
            "selected_worker_limit": selected,
            "selection_rule": "SMALLEST_WITHIN_95_PERCENT_OF_BEST_ELIGIBLE_THROUGHPUT",
            "use_fast_context": False,
            "successive_halving": False,
        },
        "raw_cache_unchanged": cache_after == cache_before,
        "data_scope": {
            "store_root": config["cache_root"],
            "adaptive_block": adaptive_block,
            "alternate_input_paths_constructed": False,
            "enforcement": "PINNED_RAW_PANEL_STORE_AND_FROZEN_FIELD_CONTRACTS_ONLY",
        },
        "candidate_promotion": "FORBIDDEN",
    }
    swap = psutil.swap_memory()
    host_after = {
        "cpu_percent": psutil.cpu_percent(interval=0.5),
        "background_python": _background_python_snapshot(),
    }
    resource = {
        "schema_version": 1,
        "execution_host": platform.node(),
        "environment": {
            "python_executable": os.path.realpath(os.sys.executable),
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "logical_cpu_count": psutil.cpu_count(logical=True),
            "physical_cpu_count": psutil.cpu_count(logical=False),
            "packages": _package_matrix(),
            "power_plan": _power_plan(),
        },
        "memory": {
            "physical_total_bytes": psutil.virtual_memory().total,
            "physical_available_after_bytes": psutil.virtual_memory().available,
            "pagefile_total_bytes": swap.total,
            "pagefile_used_after_bytes": swap.used,
        },
        "host_load": {"before": host_before, "after": host_after},
        "parity_runs": parity_resources,
        "scheduler_runs": scheduler_resources,
        "raw_cache_after": cache_after,
    }
    _write_json(runtime_root / RUNTIME_FILES[0], contract)
    _write_json(runtime_root / RUNTIME_FILES[1], results)
    _write_json(runtime_root / RUNTIME_FILES[2], resource)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(_render_report(contract, results, resource))
    artifact_paths = [runtime_root / name for name in RUNTIME_FILES] + [report_path]
    artifacts = [
        {
            "path": path.relative_to(repo_root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in artifact_paths
    ]
    _write_json(
        runtime_root / MANIFEST_FILE,
        {
            "schema_version": 1,
            "epoch_id": EPOCH_ID,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "producer_source_sha": source_ref,
            "artifacts": artifacts,
            "bundle_sha256": _payload_sha(artifacts),
            "result": result,
        },
    )
    return check_canary(repo_root, config_path=config_path)


def check_canary(repo_root: Path, *, config_path: Path) -> dict[str, Any]:
    config = _read_json(config_path)
    validate_config(config)
    runtime_root = repo_root / config["outputs"]["runtime_root"]
    report_path = repo_root / config["outputs"]["report"]
    errors: list[str] = []
    try:
        manifest = _read_json(runtime_root / MANIFEST_FILE)
        contract = _read_json(runtime_root / RUNTIME_FILES[0])
        results = _read_json(runtime_root / RUNTIME_FILES[1])
        resource = _read_json(runtime_root / RUNTIME_FILES[2])
        expected_paths = [
            (runtime_root / name).relative_to(repo_root).as_posix() for name in RUNTIME_FILES
        ] + [report_path.relative_to(repo_root).as_posix()]
        if [row.get("path") for row in manifest.get("artifacts", ())] != expected_paths:
            errors.append("artifact_paths")
        artifacts = []
        for relative in expected_paths:
            path = repo_root / relative
            artifacts.append(
                {"path": relative, "bytes": path.stat().st_size, "sha256": sha256_file(path)}
            )
        if manifest.get("artifacts") != artifacts or manifest.get("bundle_sha256") != _payload_sha(artifacts):
            errors.append("artifact_identity")
        if contract.get("config_sha256") != sha256_file(config_path):
            errors.append("config_identity")
        if contract.get("frozen_config") != config:
            errors.append("frozen_config")
        if (
            manifest.get("producer_source_sha") != contract.get("producer_source_sha")
            or contract.get("raw_cache_before") != config.get("expected_cache_bundle")
            or contract.get("candidate_ids")
            != [row["candidate_id"] for row in config.get("candidates", ())]
        ):
            errors.append("contract_identity")
        if not _git_commit_exists(repo_root, str(contract.get("producer_source_sha"))):
            errors.append("producer_source_sha")
        for key in ("manifest", "contract", "pair"):
            source = config["source_evidence"]
            if sha256_file(repo_root / source[f"{key}_path"]) != source[f"{key}_sha256"]:
                errors.append(f"source_{key}")
        if _directory_bundle(repo_root / config["cache_root"]) != contract.get("raw_cache_before"):
            errors.append("raw_cache")
        source_candidates = _load_candidates(repo_root, config)
        source_by_id = {row["candidate_id"]: row for row in source_candidates}
        ledger = results.get("execution_ledger", ())
        expected_total = (
            len(config["memory_policy"]["trial_order"]) * len(source_candidates)
            + len(config["scheduler"]["trial_orders"])
            * len(config["scheduler"]["worker_counts"])
            * int(config["scheduler"]["task_count"])
            * int(config["scheduler"]["pairs_per_task"])
        )
        ledger_valid = len(ledger) == expected_total
        for row in ledger:
            expected = source_by_id.get(row.get("candidate_id"))
            if expected is None:
                ledger_valid = False
                continue
            exact = bool(
                row.get("semantic_sha256") == expected["source_semantic_sha256"]
                and row.get("source_semantic_sha256") == expected["source_semantic_sha256"]
                and row.get("delta_weight_sha256")
                == expected["expected_delta_weight_sha256"]
                and row.get("expected_delta_weight_sha256")
                == expected["expected_delta_weight_sha256"]
                and float(row.get("pair_reward")) == float(expected["expected_pair_reward"])
                and float(row.get("expected_pair_reward"))
                == float(expected["expected_pair_reward"])
            )
            if row.get("source_parity") is not exact or not exact:
                ledger_valid = False
        if (
            not ledger_valid
            or contract.get("total_pair_executions") != expected_total
            or contract.get("adaptive_block") != config["adaptive_block"]
        ):
            errors.append("execution_ledger")

        platform_is_windows = "windows" in str(
            resource.get("environment", {}).get("platform", "")
        ).lower()

        def native_resource_pass(run: Mapping[str, Any]) -> bool:
            if not platform_is_windows:
                return True
            return bool(
                int(run.get("native_trim_failed", -1)) == 0
                and int(run.get("native_trim_attempted", -1))
                == int(run.get("trim_count", -2))
                and int(run.get("native_trim_succeeded", -1))
                == int(run.get("native_trim_attempted", -2))
            )

        parity = results.get("parity", {})
        parity_trials = parity.get("trials", ())
        parity_resources = resource.get("parity_runs", ())
        expected_parity_ids = [
            f"parity-{index:02d}-{label}"
            for index, label in enumerate(config["memory_policy"]["trial_order"], start=1)
        ]
        parity_valid = bool(
            parity.get("result") == "PASS"
            and parity.get("candidate_count") == 8
            and parity.get("trial_count") == len(expected_parity_ids)
            and [row.get("trial_id") for row in parity_trials] == expected_parity_ids
            and [row.get("trial_id") for row in parity_resources] == expected_parity_ids
        )
        for trial, run in zip(parity_trials, parity_resources):
            trial_rows = [row for row in ledger if row.get("trial_id") == trial.get("trial_id")]
            parity_valid = bool(
                parity_valid
                and len(trial_rows) == 8
                and {row["candidate_id"] for row in trial_rows} == set(source_by_id)
                and all(row.get("source_parity") is True for row in trial_rows)
                and trial.get("pair_count") == 8
                and trial.get("source_parity") == "PASS"
                and trial.get("native_trim_pass") is True
                and run.get("pair_count") == 8
                and run.get("task_count") == 1
                and native_resource_pass(run)
            )
        if parity_trials:
            baseline_median = median(
                float(row["wall_seconds"])
                for row in parity_trials
                if row.get("mode") == "baseline"
            )
            candidate_median = median(
                float(row["wall_seconds"])
                for row in parity_trials
                if row.get("mode") == "candidate"
            )
            parity_valid = bool(
                parity_valid
                and float(parity.get("baseline_median_wall_seconds")) == baseline_median
                and float(parity.get("candidate_median_wall_seconds")) == candidate_median
            )
        if not parity_valid:
            errors.append("parity")

        scheduler_trials = results.get("scheduler_trials", ())
        scheduler_resources = resource.get("scheduler_runs", ())
        expected_scheduler_ids = []
        for round_index, order in enumerate(config["scheduler"]["trial_orders"], start=1):
            expected_scheduler_ids.extend(
                f"scheduler-r{round_index}-p{order_index}-w{int(worker_count)}"
                for order_index, worker_count in enumerate(order, start=1)
            )
        scheduler_trials_valid = bool(
            [row.get("trial_id") for row in scheduler_trials] == expected_scheduler_ids
            and [row.get("trial_id") for row in scheduler_resources] == expected_scheduler_ids
        )
        max_worker_rss = int(config["scheduler"]["maximum_worker_peak_rss_bytes"])
        max_aggregate = int(config["scheduler"]["maximum_aggregate_peak_rss_bytes"])
        expected_pairs_per_trial = int(config["scheduler"]["task_count"]) * int(
            config["scheduler"]["pairs_per_task"]
        )
        for trial, run in zip(scheduler_trials, scheduler_resources):
            trial_rows = [row for row in ledger if row.get("trial_id") == trial.get("trial_id")]
            task_counts = {
                task_id: sum(row.get("task_id") == task_id for row in trial_rows)
                for task_id in {row.get("task_id") for row in trial_rows}
            }
            candidate_counts = {
                candidate_id: sum(row.get("candidate_id") == candidate_id for row in trial_rows)
                for candidate_id in source_by_id
            }
            aggregate = int(trial.get("maximum_worker_peak_rss_bytes", 2**63)) * min(
                int(trial.get("worker_count", 0)), int(config["scheduler"]["task_count"])
            )
            eligible = bool(
                trial.get("semantic_parity") == "PASS"
                and trial.get("native_trim_pass") is True
                and int(trial.get("maximum_worker_peak_rss_bytes", 2**63)) <= max_worker_rss
                and aggregate <= max_aggregate
            )
            scheduler_trials_valid = bool(
                scheduler_trials_valid
                and len(trial_rows) == expected_pairs_per_trial
                and all(row.get("source_parity") is True for row in trial_rows)
                and len(task_counts) == int(config["scheduler"]["task_count"])
                and set(task_counts.values()) == {int(config["scheduler"]["pairs_per_task"])}
                and set(candidate_counts.values()) == {expected_pairs_per_trial // 8}
                and trial.get("task_count") == int(config["scheduler"]["task_count"])
                and trial.get("pair_count") == expected_pairs_per_trial
                and int(trial.get("estimated_aggregate_peak_rss_bytes", -1)) == aggregate
                and trial.get("eligible") is eligible
                and run.get("task_count") == int(config["scheduler"]["task_count"])
                and run.get("pair_count") == expected_pairs_per_trial
                and float(run.get("wall_seconds")) == float(trial.get("wall_seconds"))
                and float(run.get("pairs_per_second"))
                == float(trial.get("pairs_per_second"))
                and int(run.get("maximum_worker_peak_rss_bytes"))
                == int(trial.get("maximum_worker_peak_rss_bytes"))
                and native_resource_pass(run)
            )
        scheduler = results.get("scheduler", ())
        recomputed_scheduler = _aggregate_scheduler_trials(
            scheduler_trials, config["scheduler"]["worker_counts"]
        )
        selected = _select_worker_limit(scheduler, float(config["scheduler"]["near_best_ratio"]))
        if (
            not scheduler_trials_valid
            or scheduler != recomputed_scheduler
            or tuple(row.get("worker_count") for row in scheduler) != (8, 10, 12)
            or any(row.get("semantic_parity") != "PASS" for row in scheduler)
            or selected != results.get("decision", {}).get("selected_worker_limit")
        ):
            errors.append("scheduler")
        expected_scope = {
            "store_root": config["cache_root"],
            "adaptive_block": config["adaptive_block"],
            "alternate_input_paths_constructed": False,
            "enforcement": "PINNED_RAW_PANEL_STORE_AND_FROZEN_FIELD_CONTRACTS_ONLY",
        }
        if (
            results.get("raw_cache_unchanged") is not True
            or results.get("data_scope") != expected_scope
            or results.get("candidate_promotion") != "FORBIDDEN"
        ):
            errors.append("boundaries")
        if report_path.read_text(encoding="utf-8") != _render_report(contract, results, resource):
            errors.append("report")
        if results.get("result") != "PASS" or manifest.get("result") != "PASS":
            errors.append("canary_result")
    except (KeyError, OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(type(exc).__name__ + ":" + str(exc))
        results = {}
        manifest = {}
    return {
        "result": "PASS" if not errors else "FAIL",
        "errors": errors,
        "selected_worker_limit": results.get("decision", {}).get("selected_worker_limit"),
        "unique_pair_count": results.get("parity", {}).get("candidate_count"),
        "total_pair_executions": (
            results.get("execution_ledger") and len(results["execution_ledger"])
        ) if results else None,
        "bundle_sha256": manifest.get("bundle_sha256"),
    }


__all__ = [
    "EPOCH_ID", "check_canary", "run_canary", "validate_config",
    "_aggregate_scheduler_trials", "_select_worker_limit", "_semantic_projection",
    "_trim_decision",
]
