from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
DEFAULT_RUNTIME = Path(
    os.environ.get(
        "A7LS17_RUNTIME",
        "G:/AlphaFactory_CryptoData/research_runtime/a7ls17_company_materialization_20260606_r3",
    )
)
LOCAL_RUNTIME = REPO / "runtime" / "a7ls17_company_materialization_aggregate"
LOCAL_REPORT = REPO / "reports" / "CRYPTO_A7LS17_COMPANY_MATERIALIZATION_AGGREGATE_20260606.md"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 40) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def collect(runtime: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    manifests = []
    metrics_frames = []
    for manifest_path in sorted((runtime / "shards").glob("a7ls17_s*/a7ls17_manifest.json")):
        manifest = read_json(manifest_path)
        manifest["manifest_path"] = str(manifest_path)
        manifests.append(manifest)
        metrics_path = manifest_path.parent / "a7ls17_materialization_metrics.csv"
        if metrics_path.exists():
            frame = pd.read_csv(metrics_path)
            frame["shard_id"] = manifest.get("shard_id", manifest_path.parent.name)
            metrics_frames.append(frame)
    manifest_df = pd.DataFrame(manifests)
    metrics = pd.concat(metrics_frames, ignore_index=True) if metrics_frames else pd.DataFrame()
    return manifest_df, metrics


def aggregate(runtime: Path, out_runtime: Path, report_path: Path) -> dict[str, Any]:
    out_runtime.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_df, metrics = collect(runtime)

    expected = int(os.environ.get("A7LS17_EXPECTED_SHARDS", "100"))
    expected_ids = {f"a7ls17_s{i:03d}" for i in range(expected)}
    seen_ids = set(manifest_df["shard_id"].astype(str).tolist()) if not manifest_df.empty else set()
    missing_ids = sorted(expected_ids - seen_ids)

    manifest_df.to_csv(out_runtime / "a7ls17_shard_manifest_summary.csv", index=False)
    if not metrics.empty:
        metrics[[
            "shard_id",
            "blueprint_id",
            "a7ls_lane",
            "semantic_pair",
            "motif",
            "candidate_role",
            "eval_success",
            "activity_ok",
            "finite_share",
            "nonzero_share",
            "std_value",
            "error",
        ]].to_csv(out_runtime / "a7ls17_materialization_metrics_compact.csv", index=False)

    if metrics.empty:
        lane_summary = pd.DataFrame()
        pair_summary = pd.DataFrame()
    else:
        lane_summary = (
            metrics.groupby("a7ls_lane", dropna=False)
            .agg(
                rows=("blueprint_id", "size"),
                eval_success=("eval_success", "sum"),
                activity_ok=("activity_ok", "sum"),
                semantic_pairs=("semantic_pair", "nunique"),
                motifs=("motif", "nunique"),
                finite_share_median=("finite_share", "median"),
                nonzero_share_median=("nonzero_share", "median"),
            )
            .reset_index()
        )
        lane_summary["eval_success_rate"] = lane_summary["eval_success"] / lane_summary["rows"].clip(lower=1)
        lane_summary["activity_ok_rate"] = lane_summary["activity_ok"] / lane_summary["rows"].clip(lower=1)
        pair_summary = (
            metrics.groupby(["a7ls_lane", "semantic_pair"], dropna=False)
            .agg(
                rows=("blueprint_id", "size"),
                eval_success=("eval_success", "sum"),
                activity_ok=("activity_ok", "sum"),
                motifs=("motif", "nunique"),
            )
            .reset_index()
            .sort_values(["activity_ok", "eval_success", "rows"], ascending=False)
        )
        pair_summary["activity_ok_rate"] = pair_summary["activity_ok"] / pair_summary["rows"].clip(lower=1)
    lane_summary.to_csv(out_runtime / "a7ls17_lane_materialization_summary.csv", index=False)
    pair_summary.to_csv(out_runtime / "a7ls17_semantic_pair_materialization_summary.csv", index=False)

    total_rows = int(metrics.shape[0])
    eval_success = int(metrics["eval_success"].sum()) if not metrics.empty else 0
    activity_ok = int(metrics["activity_ok"].sum()) if not metrics.empty else 0
    blockers = []
    if missing_ids:
        blockers.append("missing_shards")
    if total_rows <= 0:
        blockers.append("no_metrics")
    if metrics.empty or int((~metrics["eval_success"].astype(bool)).sum()) > 0:
        blockers.append("eval_failures_present")

    decision = "PASS_A7LS17_COMPANY_MATERIALIZATION_AGGREGATE_READY_FOR_A7LS18" if not blockers else "HOLD_A7LS17_COMPANY_MATERIALIZATION_INCOMPLETE"
    manifest = {
        "stage": "A7LS-17",
        "decision": decision,
        "generated_at": now_iso(),
        "runtime": str(runtime),
        "expected_shards": expected,
        "completed_shards": int(len(seen_ids)),
        "missing_shards": missing_ids,
        "total_rows": total_rows,
        "eval_success_count": eval_success,
        "eval_failure_count": int(total_rows - eval_success),
        "activity_ok_count": activity_ok,
        "activity_ok_rate": float(activity_ok / total_rows) if total_rows else 0.0,
        "lane_count": int(metrics["a7ls_lane"].nunique()) if not metrics.empty else 0,
        "semantic_pair_count": int(metrics["semantic_pair"].nunique()) if not metrics.empty else 0,
        "motif_count": int(metrics["motif"].nunique()) if not metrics.empty else 0,
        "authorizes_a7ls18_company_numeric": decision.startswith("PASS_"),
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "uses_may": False,
        "blockers": blockers,
    }
    write_json(out_runtime / "a7ls17_manifest.json", manifest)

    report = [
        "# CRYPTO A7LS-17 COMPANY MATERIALIZATION AGGREGATE",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "## Summary",
        "",
        f"- completed_shards: {manifest['completed_shards']} / {expected}",
        f"- total_rows: {total_rows:,}",
        f"- eval_success_count: {eval_success:,}",
        f"- eval_failure_count: {manifest['eval_failure_count']:,}",
        f"- activity_ok_count: {activity_ok:,}",
        f"- activity_ok_rate: {manifest['activity_ok_rate']:.4f}",
        f"- lane_count: {manifest['lane_count']}",
        f"- semantic_pair_count: {manifest['semantic_pair_count']}",
        f"- motif_count: {manifest['motif_count']}",
        "",
        "## Lane Summary",
        "",
        md_table(lane_summary),
        "",
        "## Top Semantic Pairs",
        "",
        md_table(pair_summary.head(30)),
        "",
        "## Authorization",
        "",
        "- A7LS18 company numeric wave: authorized only if decision is PASS",
        "- alpha proof / shadow / paper / live: not authorized",
    ]
    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")
    return manifest


if __name__ == "__main__":
    runtime = Path(os.environ.get("A7LS17_RUNTIME", str(DEFAULT_RUNTIME)))
    out_runtime = Path(os.environ.get("A7LS17_AGG_RUNTIME", str(LOCAL_RUNTIME)))
    report = Path(os.environ.get("A7LS17_AGG_REPORT", str(LOCAL_REPORT)))
    result = aggregate(runtime, out_runtime, report)
    print(json.dumps(result, indent=2, sort_keys=True))
