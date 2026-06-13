from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def main() -> None:
    queue_path = Path(
        os.environ.get(
            "A7V3S0_REWARD_PREQUEUE",
            r"D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7v3s0_reward_prequeue_20260613\a7v3s0_reward_prequeue.csv",
        )
    )
    runtime = Path(
        os.environ.get(
            "A7V3S0_REWARD_SHARD_RUNTIME",
            r"D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7v3s0_reward_sharded_720h_20260613",
        )
    )
    rows_per_shard = int(os.environ.get("A7V3S0_REWARD_ROWS_PER_SHARD", "16"))
    queue = pd.read_csv(queue_path, low_memory=False)
    runtime.mkdir(parents=True, exist_ok=True)
    shard_root = runtime / "queue_shards"
    shard_root.mkdir(parents=True, exist_ok=True)

    shard_rows = []
    for i, start in enumerate(range(0, len(queue), rows_per_shard)):
        end = min(start + rows_per_shard, len(queue))
        shard_id = f"a7v3s0_reward_s{i:03d}"
        path = shard_root / f"{shard_id}.csv"
        queue.iloc[start:end].to_csv(path, index=False)
        shard_rows.append({"shard_id": shard_id, "start_row": start, "end_row": end, "rows": end - start, "queue_path": str(path)})

    shard_plan = pd.DataFrame(shard_rows)
    shard_plan.to_csv(runtime / "a7v3s0_reward_shard_plan.csv", index=False)
    manifest = {
        "stage": "A7V3S0-REWARD-SHARD-QUEUE",
        "decision": "PASS_A7V3S0_REWARD_SHARD_QUEUE_READY",
        "generated_at": now_utc(),
        "input_queue": str(queue_path),
        "runtime": str(runtime),
        "queue_rows": int(len(queue)),
        "rows_per_shard": rows_per_shard,
        "shard_count": int(len(shard_plan)),
        "shard_plan": str(runtime / "a7v3s0_reward_shard_plan.csv"),
        "authorizes_reward_sharded_gate": True,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(runtime / "a7v3s0_reward_shard_manifest.json", manifest)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
