from __future__ import annotations

import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


REPO = Path(r"D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote")
PYTHON = Path(r"D:\Python311\python.exe")
if not PYTHON.exists():
    PYTHON = Path(r"D:\HermesWorker\workspace\.venv\Scripts\python.exe")

RUN_ROOT = Path(r"D:\HermesWorker\runtime\a7source10_seed_expansion_proxy_20260708")
AGG_RUNTIME = REPO / r"runtime\a7source10_seed_expansion_proxy_aggregate_20260708"
REWARD_RUN_ROOT = Path(r"D:\HermesWorker\runtime\a7source10_seed_expansion_reward_20260708")
REWARD_AGG_RUNTIME = REPO / r"runtime\a7source10_seed_expansion_reward_aggregate_20260708"
QUEUE = REPO / r"runtime\a7source10_seed_expansion_queue_20260708\a7source10_seed_expansion_proxy_queue.csv"
PROXY_REPORT = REPO / r"reports\CRYPTO_A7SOURCE10_SEED_EXPANSION_PROXY_AGGREGATE_20260708.md"
REWARD_REPORT = REPO / r"reports\CRYPTO_A7SOURCE10_SEED_EXPANSION_REWARD_AGGREGATE_20260708.md"

PROXY_ROWS_PER_SHARD = 64
REWARD_ROWS_PER_SHARD = 16
MAX_PARALLEL = int(os.environ.get("A7SOURCE10_MAX_PARALLEL", "8"))


def child_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    env = os.environ.copy()
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(REPO) if not existing else f"{REPO}{os.pathsep}{existing}"
    if extra:
        env.update(extra)
    return env


def ts() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def log(message: str) -> None:
    RUN_ROOT.mkdir(parents=True, exist_ok=True)
    with (RUN_ROOT / "a7source10_proxy_reward_flow_py.log").open("a", encoding="utf-8") as fh:
        fh.write(f"[{ts()}] {message}\n")


def run(args: list[str], *, env: dict[str, str] | None = None) -> None:
    log("RUN " + " ".join(args))
    result = subprocess.run(args, cwd=str(REPO), env=child_env(env), text=True, capture_output=True)
    if result.stdout:
        log("STDOUT " + result.stdout[-4000:])
    if result.stderr:
        log("STDERR " + result.stderr[-4000:])
    if result.returncode != 0:
        raise RuntimeError(f"command failed {result.returncode}: {' '.join(args)}")


def ensure_proxy_shards() -> list[dict[str, str]]:
    shard_dir = RUN_ROOT / "queue_shards"
    shard_dir.mkdir(parents=True, exist_ok=True)
    rows = pd.read_csv(QUEUE, low_memory=False)
    plan = []
    for start in range(0, len(rows), PROXY_ROWS_PER_SHARD):
        end = min(len(rows), start + PROXY_ROWS_PER_SHARD)
        sid = f"a7source10_proxy_s{start // PROXY_ROWS_PER_SHARD:03d}"
        path = shard_dir / f"{sid}.csv"
        if not path.exists():
            rows.iloc[start:end].to_csv(path, index=False)
        plan.append({"shard_id": sid, "queue_path": str(path), "rows": end - start})
    pd.DataFrame(plan).to_csv(RUN_ROOT / "a7source10_proxy_shard_plan.csv", index=False)
    return plan


def proxy_manifest(sid: str) -> Path:
    return RUN_ROOT / "shards" / sid / "proxy_runtime" / "a7v3s9_proxy_manifest.json"


def reward_manifest(sid: str) -> Path:
    return REWARD_RUN_ROOT / "shards" / sid / "reward_runtime" / "a7reward1_manifest.json"


def launch_batch(jobs: list[tuple[str, list[str], Path, Path]]) -> None:
    procs = []
    for sid, args, out_path, err_path in jobs:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        err_path.parent.mkdir(parents=True, exist_ok=True)
        log(f"START {sid}")
        out = out_path.open("w", encoding="utf-8")
        err = err_path.open("w", encoding="utf-8")
        proc = subprocess.Popen(args, cwd=str(REPO), env=child_env(), stdout=out, stderr=err)
        procs.append((sid, proc, out, err))
    for sid, proc, out, err in procs:
        code = proc.wait()
        out.close()
        err.close()
        log(f"END {sid} exit={code}")
        if code != 0:
            raise RuntimeError(f"shard failed {sid}: {code}")


def run_proxy_shards(plan: list[dict[str, str]]) -> None:
    pending = [row for row in plan if not proxy_manifest(row["shard_id"]).exists()]
    log(f"proxy pending={len(pending)} total={len(plan)} max_parallel={MAX_PARALLEL}")
    for start in range(0, len(pending), MAX_PARALLEL):
        jobs = []
        for row in pending[start : start + MAX_PARALLEL]:
            sid = row["shard_id"]
            root = RUN_ROOT / "shards" / sid
            runtime = root / "proxy_runtime"
            report = root / f"CRYPTO_{sid}_PROXY.md"
            args = [
                str(PYTHON),
                r"scripts\crypto_a7v3s9_prereward_oos_control_proxy.py",
                "--queue",
                row["queue_path"],
                "--runtime",
                str(runtime),
                "--report",
                str(report),
                "--candidate-cap",
                "0",
                "--select-target",
                "48",
                "--pair-cap",
                "16",
                "--motif-cap",
                "24",
                "--skeleton-cap",
                "2",
                "--checkpoint-every",
                "16",
            ]
            jobs.append((sid, args, root / "proxy.out.log", root / "proxy.err.log"))
        launch_batch(jobs)
        missing = [row["shard_id"] for row in pending[start : start + MAX_PARALLEL] if not proxy_manifest(row["shard_id"]).exists()]
        if missing:
            raise RuntimeError(f"missing proxy manifests after batch: {missing}")


def run_proxy_aggregate() -> Path:
    AGG_RUNTIME.mkdir(parents=True, exist_ok=True)
    run(
        [
            str(PYTHON),
            r"scripts\crypto_a7v3s9_proxy_aggregate.py",
            "--run-root",
            str(RUN_ROOT),
            "--runtime",
            str(AGG_RUNTIME),
            "--report",
            str(PROXY_REPORT),
            "--select-target",
            "384",
        ]
    )
    manifest_path = AGG_RUNTIME / "a7v3s9_proxy_aggregate_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    log(f"proxy aggregate selected={manifest.get('selected_rows')} errors={manifest.get('eval_error_rows')}")
    return AGG_RUNTIME / "a7v3s9_proxy_selected_for_reward.csv"


def ensure_reward_shards(selected_queue: Path) -> list[dict[str, str]]:
    REWARD_RUN_ROOT.mkdir(parents=True, exist_ok=True)
    env = {
        "A7V3S0_REWARD_PREQUEUE": str(selected_queue),
        "A7V3S0_REWARD_SHARD_RUNTIME": str(REWARD_RUN_ROOT),
        "A7V3S0_REWARD_ROWS_PER_SHARD": str(REWARD_ROWS_PER_SHARD),
    }
    run([str(PYTHON), r"scripts\crypto_a7v3s0_reward_shard_queue.py"], env=env)
    plan_path = REWARD_RUN_ROOT / "a7v3s0_reward_shard_plan.csv"
    return pd.read_csv(plan_path, low_memory=False).to_dict("records")


def run_reward_shards(plan: list[dict[str, str]]) -> None:
    pending = [row for row in plan if not reward_manifest(row["shard_id"]).exists()]
    log(f"reward pending={len(pending)} total={len(plan)} max_parallel={MAX_PARALLEL}")
    for start in range(0, len(pending), MAX_PARALLEL):
        jobs = []
        for row in pending[start : start + MAX_PARALLEL]:
            sid = row["shard_id"]
            root = REWARD_RUN_ROOT / "shards" / sid
            runtime = root / "reward_runtime"
            report = root / f"CRYPTO_{sid}_FULL_REWARD.md"
            args = [
                str(PYTHON),
                r"scripts\crypto_a7reward1_portfolio_reward_model.py",
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
                "--runtime",
                str(runtime),
                "--report",
                str(report),
            ]
            jobs.append((sid, args, root / "reward.out.log", root / "reward.err.log"))
        launch_batch(jobs)
        missing = [row["shard_id"] for row in pending[start : start + MAX_PARALLEL] if not reward_manifest(row["shard_id"]).exists()]
        if missing:
            raise RuntimeError(f"missing reward manifests after batch: {missing}")


def run_reward_aggregate() -> None:
    REWARD_AGG_RUNTIME.mkdir(parents=True, exist_ok=True)
    run(
        [
            str(PYTHON),
            r"scripts\crypto_a7v3s0_reward_sharded_aggregate.py",
            "--run-root",
            str(REWARD_RUN_ROOT),
            "--runtime",
            str(REWARD_AGG_RUNTIME),
            "--report",
            str(REWARD_REPORT),
        ]
    )
    log("reward aggregate complete")


def main() -> None:
    log("A7SOURCE10 python supervisor start source_commit=3fa2a35")
    plan = ensure_proxy_shards()
    run_proxy_shards(plan)
    selected_queue = run_proxy_aggregate()
    if not selected_queue.exists() or selected_queue.stat().st_size <= 2:
        log("no selected queue; stop before reward")
        return
    reward_plan = ensure_reward_shards(selected_queue)
    run_reward_shards(reward_plan)
    run_reward_aggregate()
    log("A7SOURCE10 python supervisor finished")


if __name__ == "__main__":
    main()
