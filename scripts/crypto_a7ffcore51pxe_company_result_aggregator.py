from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, help="CORE51PXE external output directory")
    parser.add_argument("--expected-shards", type=int, default=16)
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    manifests = []
    for path in sorted(out.glob("core51px_shard_*_manifest.json")):
        payload = read_json(path)
        payload["manifest_path"] = str(path).replace("\\", "/")
        manifests.append(payload)
    manifest_df = pd.DataFrame(manifests)
    metrics_frames = [pd.read_csv(path) for path in sorted(out.glob("core51px_shard_*_metrics.csv"))]
    metrics = pd.concat(metrics_frames, ignore_index=True) if metrics_frames else pd.DataFrame()

    manifest_df.to_csv(out / "a7ffcore51pxe_shard_manifest_summary.csv", index=False)
    if not metrics.empty:
        metrics.to_csv(out / "a7ffcore51pxe_aggregate_metrics.csv", index=False)
        label_summary = (
            metrics.groupby("label_key", as_index=False)
            .agg(
                row_count=("seed_id", "count"),
                seed_count=("seed_id", "nunique"),
                control_clean_positive_count=("decision", lambda s: int((s == "control_clean_positive").sum())),
                median_control_ratio=("control_ratio", "median"),
                median_original_spread=("original_spread_mean", "median"),
            )
            .sort_values("label_key")
        )
        family_summary = (
            metrics.groupby(["semantic_pair", "operator"], as_index=False)
            .agg(
                row_count=("seed_id", "count"),
                seed_count=("seed_id", "nunique"),
                control_clean_positive_count=("decision", lambda s: int((s == "control_clean_positive").sum())),
                median_control_ratio=("control_ratio", "median"),
            )
            .sort_values(["control_clean_positive_count", "seed_count"], ascending=False)
        )
    else:
        label_summary = pd.DataFrame()
        family_summary = pd.DataFrame()
    label_summary.to_csv(out / "a7ffcore51pxe_label_summary.csv", index=False)
    family_summary.to_csv(out / "a7ffcore51pxe_family_operator_summary.csv", index=False)

    completed = int(manifest_df.get("decision", pd.Series(dtype=str)).astype(str).str.startswith("PASS_").sum()) if not manifest_df.empty else 0
    eval_failures = int(pd.to_numeric(manifest_df.get("eval_failure_count", pd.Series(dtype=int)), errors="coerce").fillna(0).sum()) if not manifest_df.empty else 0
    clean_rows = int(metrics["decision"].eq("control_clean_positive").sum()) if not metrics.empty and "decision" in metrics else 0
    clean_seeds = int(metrics.loc[metrics["decision"].eq("control_clean_positive"), "seed_id"].nunique()) if clean_rows else 0
    decision = (
        "PASS_A7FFCORE51PXE_COMPANY_SHARDED_REPLAY_AGGREGATED"
        if completed == args.expected_shards and eval_failures == 0 and not metrics.empty
        else "HOLD_A7FFCORE51PXE_COMPANY_SHARDED_REPLAY_INCOMPLETE"
    )
    aggregate_manifest = {
        "stage": "A7FF-CORE51PXE-AGGREGATE",
        "generated_at": now_utc(),
        "output_dir": str(out).replace("\\", "/"),
        "decision": decision,
        "expected_shards": int(args.expected_shards),
        "completed_shards": completed,
        "manifest_count": int(len(manifest_df)),
        "metric_rows": int(len(metrics)),
        "unique_seed_count": int(metrics["seed_id"].nunique()) if not metrics.empty and "seed_id" in metrics else 0,
        "eval_failure_count": eval_failures,
        "control_clean_positive_rows": clean_rows,
        "control_clean_positive_seed_count": clean_seeds,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    (out / "a7ffcore51pxe_aggregate_manifest.json").write_text(json.dumps(aggregate_manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(aggregate_manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
