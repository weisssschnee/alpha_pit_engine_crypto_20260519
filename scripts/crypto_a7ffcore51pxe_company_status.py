from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--expected-shards", type=int, default=16)
    args = parser.parse_args()
    out = Path(args.out)
    rows = []
    for i in range(args.expected_shards):
        shard_id = f"core51px_shard_{i:02d}"
        manifest = read_json(out / f"{shard_id}_manifest.json")
        metrics_path = out / f"{shard_id}_metrics.csv"
        rows.append(
            {
                "shard_id": shard_id,
                "manifest_exists": bool(manifest),
                "metrics_exists": metrics_path.exists(),
                "decision": manifest.get("decision", "MISSING"),
                "metric_rows": manifest.get("metric_rows", 0),
                "eval_failure_count": manifest.get("eval_failure_count", None),
                "control_clean_positive_rows": manifest.get("control_clean_positive_rows", 0),
            }
        )
    df = pd.DataFrame(rows)
    print(df.to_string(index=False))
    print(
        json.dumps(
            {
                "expected_shards": args.expected_shards,
                "completed_shards": int(df["decision"].astype(str).str.startswith("PASS_").sum()),
                "missing_shards": int((~df["manifest_exists"]).sum()),
                "output_dir": str(out).replace("\\", "/"),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
