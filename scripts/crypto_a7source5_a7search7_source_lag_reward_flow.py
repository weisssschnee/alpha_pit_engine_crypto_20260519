from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


DEFAULT_REPO = Path(r"D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote")
DEFAULT_STRICT_PACK_RUNTIME = DEFAULT_REPO / "runtime" / "a7search7_strict_accepted_pack_20260706"
DEFAULT_VALIDATION_QUEUE = DEFAULT_STRICT_PACK_RUNTIME / "a7search7_validation_ablation_queue.csv"
DEFAULT_SOURCE_RUN_ROOT = Path(r"D:\HermesWorker\runtime\a7source5_a7search7_source_lag_retest_py_20260706")
DEFAULT_SOURCE_AGG_RUNTIME = DEFAULT_REPO / "runtime" / "a7source5_a7search7_source_lag_retest_py_aggregate_20260706"
DEFAULT_SOURCE_AGG_REPORT = DEFAULT_REPO / "reports" / "CRYPTO_A7SOURCE5_PY_A7SEARCH7_SOURCE_LAG_RETEST_AGGREGATE_20260706.md"
DEFAULT_REWARD_RUN_ROOT = Path(r"D:\HermesWorker\runtime\a7search7_strict_validation_reward_source5_py_20260706")
DEFAULT_REWARD_AGG_RUNTIME = DEFAULT_REPO / "runtime" / "a7search7_strict_validation_reward_source5_py_aggregate_20260706"
DEFAULT_REWARD_AGG_REPORT = DEFAULT_REPO / "reports" / "CRYPTO_A7SEARCH7_STRICT_VALIDATION_REWARD_SOURCE5_PY_AGGREGATE_20260706.md"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path, low_memory=False)


def log(path: Path, message: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"[{datetime.now().isoformat(timespec='seconds')}] {message}\n")


def acquire_lock(run_root: Path) -> bool:
    run_root.mkdir(parents=True, exist_ok=True)
    lock = run_root / "a7source5_py_flow.lock"
    try:
        fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(f"{os.getpid()} {datetime.now().isoformat()}\n")
        return True
    except FileExistsError:
        return False


def split_queue(queue_path: Path, shard_dir: Path, rows_per_shard: int) -> pd.DataFrame:
    queue = read_csv(queue_path)
    if queue.empty:
        raise RuntimeError(f"empty validation queue: {queue_path}")
    if "horizon_h" not in queue.columns:
        for alias in ["horizon", "label_horizon_h"]:
            if alias in queue.columns:
                queue["horizon_h"] = queue[alias]
                break
    if "horizon_h" not in queue.columns:
        raise RuntimeError(f"validation queue requires horizon_h or horizon alias; columns={list(queue.columns)}")
    shard_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    for idx, start in enumerate(range(0, len(queue), rows_per_shard)):
        shard_id = f"a7source5_s{idx:03d}"
        shard = queue.iloc[start : start + rows_per_shard].copy()
        path = shard_dir / f"{shard_id}.csv"
        shard.to_csv(path, index=False)
        rows.append({"shard_id": shard_id, "queue_path": str(path), "row_count": int(len(shard))})
    return pd.DataFrame(rows)


def run_parallel(plan: pd.DataFrame, max_parallel: int, make_command, manifest_for, log_path: Path, kind: str) -> pd.DataFrame:
    running: list[dict[str, Any]] = []
    status_rows: list[dict[str, Any]] = []
    remaining = plan.to_dict("records")
    while remaining or running:
        while remaining and len(running) < max_parallel:
            row = remaining.pop(0)
            shard_id = str(row["shard_id"])
            manifest = Path(manifest_for(shard_id))
            if manifest.exists():
                status_rows.append({"shard_id": shard_id, "status": "skip_existing", "exit_code": 0, "queue_path": row.get("queue_path", "")})
                continue
            cmd, out_path, err_path = make_command(row)
            Path(out_path).parent.mkdir(parents=True, exist_ok=True)
            out = open(out_path, "w", encoding="utf-8")
            err = open(err_path, "w", encoding="utf-8")
            proc = subprocess.Popen(cmd, cwd=str(DEFAULT_REPO), stdout=out, stderr=err)
            running.append({"row": row, "proc": proc, "out": out, "err": err, "started_at": now_utc()})
            log(log_path, f"START {kind} {shard_id} pid={proc.pid}")
        time.sleep(15)
        still: list[dict[str, Any]] = []
        for entry in running:
            proc: subprocess.Popen = entry["proc"]
            code = proc.poll()
            shard_id = str(entry["row"]["shard_id"])
            manifest = Path(manifest_for(shard_id))
            if code is None:
                still.append(entry)
                continue
            entry["out"].close()
            entry["err"].close()
            status = "done" if manifest.exists() and code == 0 else "failed"
            status_rows.append(
                {
                    "shard_id": shard_id,
                    "status": status,
                    "exit_code": int(code),
                    "started_at": entry["started_at"],
                    "ended_at": now_utc(),
                    "queue_path": entry["row"].get("queue_path", ""),
                    "manifest": str(manifest),
                }
            )
            log(log_path, f"{status.upper()} {kind} {shard_id} exit={code} manifest={manifest.exists()}")
        running = still
        status_frame = pd.DataFrame(status_rows)
        if not status_frame.empty:
            status_frame.to_csv(log_path.with_name(f"{kind}_status.csv"), index=False)
    return pd.DataFrame(status_rows)


def concat_csv(pattern: str, output: Path) -> pd.DataFrame:
    frames = []
    for path in sorted(Path().glob(pattern)):
        frame = read_csv(path)
        if frame.empty:
            continue
        frame.insert(0, "source_file", str(path))
        frames.append(frame)
    out = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    output.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output, index=False)
    return out


def concat_csv_files(paths: list[Path], output: Path) -> pd.DataFrame:
    frames = []
    for path in sorted(paths):
        frame = read_csv(path)
        if frame.empty:
            continue
        frame.insert(0, "source_file", str(path))
        frames.append(frame)
    out = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    output.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output, index=False)
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--repo", type=Path, default=DEFAULT_REPO)
    parser.add_argument("--validation-queue", type=Path, default=DEFAULT_VALIDATION_QUEUE)
    parser.add_argument("--source-run-root", type=Path, default=DEFAULT_SOURCE_RUN_ROOT)
    parser.add_argument("--source-aggregate-runtime", type=Path, default=DEFAULT_SOURCE_AGG_RUNTIME)
    parser.add_argument("--source-aggregate-report", type=Path, default=DEFAULT_SOURCE_AGG_REPORT)
    parser.add_argument("--reward-run-root", type=Path, default=DEFAULT_REWARD_RUN_ROOT)
    parser.add_argument("--reward-aggregate-runtime", type=Path, default=DEFAULT_REWARD_AGG_RUNTIME)
    parser.add_argument("--reward-aggregate-report", type=Path, default=DEFAULT_REWARD_AGG_REPORT)
    parser.add_argument("--rows-per-shard", type=int, default=16)
    parser.add_argument("--max-parallel", type=int, default=8)
    args = parser.parse_args()

    globals()["DEFAULT_REPO"] = args.repo
    log_path = args.source_run_root / "a7source5_py_flow.log"
    if not acquire_lock(args.source_run_root):
        log(args.source_run_root / "a7source5_py_duplicate_launch.log", "lock exists; duplicate launch exits")
        return

    log(log_path, "A7SOURCE5 Python source-lag -> strict reward flow start")
    log(log_path, f"validation_queue={args.validation_queue}")
    log(log_path, f"max_parallel={args.max_parallel} rows_per_shard={args.rows_per_shard}")

    source_plan = split_queue(args.validation_queue, args.source_run_root / "source_queue_shards", args.rows_per_shard)
    source_plan.to_csv(args.source_run_root / "a7source5_source_lag_shard_plan.csv", index=False)
    log(log_path, f"source_shard_count={len(source_plan)}")

    def source_manifest(shard_id: str) -> Path:
        return args.source_run_root / "shards" / shard_id / "runtime" / "a7source4_manifest.json"

    def source_command(row: dict[str, Any]):
        shard_id = str(row["shard_id"])
        shard_root = args.source_run_root / "shards" / shard_id
        runtime = shard_root / "runtime"
        report = shard_root / f"CRYPTO_{shard_id}_SOURCE_LAG_RETEST.md"
        cmd = [
            args.python,
            "scripts/crypto_a7source4_batch_source_lag_retest.py",
            "--input",
            str(row["queue_path"]),
            "--runtime",
            str(runtime),
            "--report",
            str(report),
            "--max-rows",
            "100000",
            "--cost-bps",
            "5",
        ]
        return cmd, shard_root / "source_lag.out.log", shard_root / "source_lag.err.log"

    source_status = run_parallel(source_plan, args.max_parallel, source_command, source_manifest, log_path, "source_lag")
    failed_source = source_status[source_status["status"].eq("failed")] if not source_status.empty else pd.DataFrame()
    if not failed_source.empty:
        raise RuntimeError(f"source-lag shard failures: {failed_source[['shard_id', 'exit_code']].to_dict('records')}")

    summary_paths = list(args.source_run_root.glob("shards/a7source5_s*/runtime/a7source4_source_lag_summary.csv"))
    metric_paths = list(args.source_run_root.glob("shards/a7source5_s*/runtime/a7source4_source_lag_metrics.csv"))
    error_paths = list(args.source_run_root.glob("shards/a7source5_s*/runtime/a7source4_eval_errors.csv"))
    source_summary = concat_csv_files(summary_paths, args.source_aggregate_runtime / "a7source5_source_lag_summary.csv")
    concat_csv_files(metric_paths, args.source_aggregate_runtime / "a7source5_source_lag_metrics.csv")
    source_errors = concat_csv_files(error_paths, args.source_aggregate_runtime / "a7source5_source_lag_eval_errors.csv")
    source_pass_count = int(source_summary.get("source_lag_gate", pd.Series(dtype=str)).astype(str).eq("PASS_SOURCE_LAG_1H_2H_DIAGNOSTIC").sum())
    source_manifest_payload = {
        "stage": "A7SOURCE5-PY-A7SEARCH7-SOURCE-LAG-AGGREGATE",
        "generated_at": now_utc(),
        "source_shards_expected": int(len(source_plan)),
        "source_manifest_count": int(len(summary_paths)),
        "source_lag_summary_rows": int(len(source_summary)),
        "source_lag_pass_count": source_pass_count,
        "source_eval_error_rows": int(len(source_errors)),
        "source_lag_summary": str(args.source_aggregate_runtime / "a7source5_source_lag_summary.csv"),
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(args.source_aggregate_runtime / "a7source5_manifest.json", source_manifest_payload)
    args.source_aggregate_report.parent.mkdir(parents=True, exist_ok=True)
    args.source_aggregate_report.write_text(
        "\n".join(
            [
                "# CRYPTO A7SOURCE5 Python A7SEARCH7 Source-Lag Retest Aggregate",
                "",
                "## Decision",
                "",
                "PASS_A7SOURCE5_SOURCE_LAG_SURVIVORS_FOUND" if source_pass_count > 0 else "HOLD_A7SOURCE5_SOURCE_LAG_NO_SURVIVORS",
                "",
                "## Counts",
                "",
                f"- source_shards_expected: {len(source_plan)}",
                f"- source_manifest_count: {len(summary_paths)}",
                f"- source_lag_summary_rows: {len(source_summary)}",
                f"- source_lag_pass_count: {source_pass_count}",
                f"- source_eval_error_rows: {len(source_errors)}",
                "",
                "This is a source-lag diagnostic and strict reward input, not alpha proof.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    log(log_path, f"source aggregate pass_count={source_pass_count} rows={len(source_summary)} errors={len(source_errors)}")

    env = os.environ.copy()
    env["A7V3S0_REWARD_PREQUEUE"] = str(args.validation_queue)
    env["A7V3S0_REWARD_SHARD_RUNTIME"] = str(args.reward_run_root)
    env["A7V3S0_REWARD_ROWS_PER_SHARD"] = str(args.rows_per_shard)
    subprocess.run([args.python, "scripts/crypto_a7v3s0_reward_shard_queue.py"], cwd=str(args.repo), env=env, check=True)
    reward_plan = read_csv(args.reward_run_root / "a7v3s0_reward_shard_plan.csv")
    log(log_path, f"reward_shard_count={len(reward_plan)}")

    def reward_manifest(shard_id: str) -> Path:
        return args.reward_run_root / "shards" / shard_id / "reward_runtime" / "a7reward1_manifest.json"

    def reward_command(row: dict[str, Any]):
        shard_id = str(row["shard_id"])
        shard_root = args.reward_run_root / "shards" / shard_id
        runtime = shard_root / "reward_runtime"
        report = shard_root / f"CRYPTO_{shard_id}_A7SEARCH7_STRICT_VALIDATION_REWARD_SOURCE5_PY.md"
        cmd = [
            args.python,
            "scripts/crypto_a7reward1_portfolio_reward_model.py",
            "--queue",
            str(row["queue_path"]),
            "--candidate-cap",
            "0",
            "--hours-per-split",
            "720",
            "--cost-bps",
            "5",
            "--checkpoint-every",
            "4",
            "--source-lag-summary",
            str(args.source_aggregate_runtime / "a7source5_source_lag_summary.csv"),
            "--runtime",
            str(runtime),
            "--report",
            str(report),
        ]
        return cmd, shard_root / "reward.out.log", shard_root / "reward.err.log"

    reward_status = run_parallel(reward_plan, args.max_parallel, reward_command, reward_manifest, log_path, "reward_source5")
    failed_reward = reward_status[reward_status["status"].eq("failed")] if not reward_status.empty else pd.DataFrame()
    if not failed_reward.empty:
        raise RuntimeError(f"reward shard failures: {failed_reward[['shard_id', 'exit_code']].to_dict('records')}")

    subprocess.run(
        [
            args.python,
            "scripts/crypto_a7v3s0_reward_sharded_aggregate.py",
            "--run-root",
            str(args.reward_run_root),
            "--runtime",
            str(args.reward_aggregate_runtime),
            "--report",
            str(args.reward_aggregate_report),
        ],
        cwd=str(args.repo),
        check=True,
    )
    log(log_path, "A7SOURCE5 Python source-lag -> strict reward flow finished")


if __name__ == "__main__":
    main()
