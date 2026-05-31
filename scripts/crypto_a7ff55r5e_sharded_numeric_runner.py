from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
PYTHON = REPO.parent / "PythonProject" / ".venv" / "Scripts" / "python.exe"
if not PYTHON.exists():
    PYTHON = Path(sys.executable)


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_shard(index: int, offset: int, limit: int) -> dict[str, object]:
    tag = f"s{index:02d}"
    runtime = REPO / "runtime" / f"a7ff55r5e_repaired_atlas_numeric_{tag}"
    report = REPO / "reports" / f"CRYPTO_A7FF55R5E_REPAIRED_ATLAS_NUMERIC_{tag.upper()}_20260531.md"
    env = os.environ.copy()
    env.update(
        {
            "A7FF8_STAGE": "A7FF-55R5E",
            "A7FF8_FILE_PREFIX": f"a7ff55r5e_{tag}",
            "A7FF8_RUNTIME": str(runtime),
            "A7FF8_REPORT": str(report),
            "A7FF8_QUEUE_PATH": str(REPO / "runtime" / "a7ff55r3_repaired_atlas_dry_generation" / "a7ff55r3_repaired_materialization_queue.csv"),
            "A7FF8_AUTH_MANIFEST": str(REPO / "runtime" / "a7ff55r5_repaired_atlas_numeric_contract" / "a7ff55r5_manifest.json"),
            "A7FF8_AUTH_DECISION": "PASS_A7FF55R5_REPAIRED_ATLAS_NUMERIC_CONTRACT_READY_FOR_EXECUTION",
            "A7FF8_PLAN_PATH": str(REPO / "runtime" / "a7ff55r5_repaired_atlas_numeric_contract" / "a7ff55r5_numeric_plan.json"),
            "A7FF8_LABELS": "L0_raw_forward_return,L1_cross_sectional_relative_return,L3_liquidity_tier_relative_return",
            "A7FF8_WRITE_CONTROL_DETAIL": "0",
            "A7FF8_MATERIALIZE_CAP": str(limit),
            "A7FF8_FAST_NUMERIC_CAP": str(limit),
            "A7FF8_PORTFOLIO_CAP": "64",
            "A7FF8_QUEUE_OFFSET": str(offset),
            "A7FF8_QUEUE_LIMIT": str(limit),
        }
    )
    started = now_utc()
    proc = subprocess.run(
        [str(PYTHON), "scripts/crypto_a7ff8_expanded_numeric_probe.py"],
        cwd=str(REPO),
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=3600,
    )
    manifest_path = runtime / f"a7ff55r5e_{tag}_decision_record.json"
    manifest = {}
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    return {
        "shard": tag,
        "offset": offset,
        "limit": limit,
        "started_at": started,
        "finished_at": now_utc(),
        "returncode": proc.returncode,
        "stdout_tail": proc.stdout[-2000:],
        "stderr_tail": proc.stderr[-2000:],
        "manifest_path": str(manifest_path.relative_to(REPO)),
        "decision": manifest.get("decision", "missing_manifest"),
        "input_blueprint_count": manifest.get("input_blueprint_count"),
        "label_response_rows": manifest.get("label_response_rows"),
        "non_l7_numeric_clue_rows": manifest.get("non_l7_numeric_clue_rows"),
        "selected_portfolio_queue_count": manifest.get("selected_portfolio_queue_count"),
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--count", type=int, default=4)
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args()

    out_dir = REPO / "runtime" / "a7ff55r5e_sharded_numeric_runner"
    out_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for i in range(args.start, args.start + args.count):
        results.append(run_shard(i, i * args.limit, args.limit))
        (out_dir / "a7ff55r5e_shard_run_results.json").write_text(
            json.dumps(results, indent=2, sort_keys=True), encoding="utf-8"
        )
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
