from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


DEFAULT_ACTIVITY_QUEUE = Path(
    os.environ.get(
        "A7V3S3_ACTIVITY_QUEUE",
        r"D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7v3s0_v3_native_large_search_c2_aggregate_20260613\a7ls17_activity_ok_queue.csv",
    )
)
DEFAULT_RUNTIME = Path(
    os.environ.get(
        "A7V3S3_PREQUEUE_RUNTIME",
        r"D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7v3s3_strict_reward_prequeue_20260613",
    )
)

STRUCTURAL_FIELD_RE = re.compile(
    r"\b(?:listing_age_days|sqrt_listing_age_days|log1p_listing_age_days|age_percentile_active_universe|active_universe_size)\b"
)
STRUCTURAL_SEMANTICS = {"age", "universe_state"}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def bounded_select(
    frame: pd.DataFrame,
    target: int,
    lane_cap: int,
    pair_cap: int,
    motif_cap: int,
    skeleton_cap: int,
) -> pd.DataFrame:
    if frame.empty:
        return frame.copy()
    sort_cols = [col for col in ["finite_share", "nonzero_share", "std_value"] if col in frame.columns]
    ranked = frame.copy()
    for col in sort_cols:
        ranked[col] = pd.to_numeric(ranked[col], errors="coerce")
    ranked = ranked.sort_values(sort_cols + ["blueprint_id"], ascending=[False] * len(sort_cols) + [True])

    lane_counts: dict[str, int] = {}
    pair_counts: dict[str, int] = {}
    motif_counts: dict[str, int] = {}
    skeleton_counts: dict[str, int] = {}
    selected: list[pd.Series] = []

    for _, row in ranked.iterrows():
        lane = str(row.get("a7ls_lane", ""))
        pair = str(row.get("semantic_pair", ""))
        motif = str(row.get("motif", ""))
        skeleton = str(row.get("skeleton_key", ""))
        if lane_counts.get(lane, 0) >= lane_cap:
            continue
        if pair_counts.get(pair, 0) >= pair_cap:
            continue
        if motif_counts.get(motif, 0) >= motif_cap:
            continue
        if skeleton_counts.get(skeleton, 0) >= skeleton_cap:
            continue
        selected.append(row)
        lane_counts[lane] = lane_counts.get(lane, 0) + 1
        pair_counts[pair] = pair_counts.get(pair, 0) + 1
        motif_counts[motif] = motif_counts.get(motif, 0) + 1
        skeleton_counts[skeleton] = skeleton_counts.get(skeleton, 0) + 1
        if len(selected) >= target:
            break

    out = pd.DataFrame(selected)
    if out.shape[0] < target:
        existing = set(out.get("blueprint_id", pd.Series(dtype=str)).astype(str))
        filler = ranked[~ranked["blueprint_id"].astype(str).isin(existing)].head(target - out.shape[0])
        out = pd.concat([out, filler], ignore_index=True)
    return out.head(target).copy()


def structural_mask(frame: pd.DataFrame) -> pd.Series:
    expression = frame.get("expression", pd.Series("", index=frame.index)).fillna("").astype(str)
    formula = frame.get("formula", pd.Series("", index=frame.index)).fillna("").astype(str)
    semantic_pair = frame.get("semantic_pair", pd.Series("", index=frame.index)).fillna("").astype(str)
    primary = frame.get("primary_field", pd.Series("", index=frame.index)).fillna("").astype(str)
    secondary = frame.get("secondary_field", pd.Series("", index=frame.index)).fillna("").astype(str)
    has_structural_text = (
        expression.str.contains(STRUCTURAL_FIELD_RE)
        | formula.str.contains(STRUCTURAL_FIELD_RE)
        | primary.str.contains(STRUCTURAL_FIELD_RE)
        | secondary.str.contains(STRUCTURAL_FIELD_RE)
    )
    has_structural_semantic = semantic_pair.apply(
        lambda value: bool(set(str(value).split("|")) & STRUCTURAL_SEMANTICS)
    )
    return has_structural_text | has_structural_semantic


def main() -> None:
    activity_queue = Path(os.environ.get("A7V3S3_ACTIVITY_QUEUE", str(DEFAULT_ACTIVITY_QUEUE)))
    runtime = Path(os.environ.get("A7V3S3_PREQUEUE_RUNTIME", str(DEFAULT_RUNTIME)))
    target = int(os.environ.get("A7V3S3_PREQUEUE_TARGET", "4096"))
    lane_cap = int(os.environ.get("A7V3S3_PREQUEUE_LANE_CAP", str(max(1, target // 3))))
    pair_cap = int(os.environ.get("A7V3S3_PREQUEUE_PAIR_CAP", "96"))
    motif_cap = int(os.environ.get("A7V3S3_PREQUEUE_MOTIF_CAP", "640"))
    skeleton_cap = int(os.environ.get("A7V3S3_PREQUEUE_SKELETON_CAP", "12"))

    runtime.mkdir(parents=True, exist_ok=True)
    queue = pd.read_csv(activity_queue, low_memory=False)
    queue = queue[(queue["eval_success"].astype(bool)) & (queue["activity_ok"].astype(bool))].copy()
    structural = structural_mask(queue)
    strict_pool = queue[~structural].copy()
    selected = bounded_select(strict_pool, target, lane_cap, pair_cap, motif_cap, skeleton_cap)
    selected.to_csv(runtime / "a7v3s3_strict_reward_prequeue.csv", index=False)

    lane_summary = selected.groupby("a7ls_lane", dropna=False).size().reset_index(name="count").sort_values("count", ascending=False)
    pair_summary = (
        selected.groupby(["a7ls_lane", "semantic_pair"], dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    motif_summary = selected.groupby("motif", dropna=False).size().reset_index(name="count").sort_values("count", ascending=False)
    skeleton_summary = selected.groupby("skeleton_key", dropna=False).size().reset_index(name="count").sort_values("count", ascending=False)
    lane_summary.to_csv(runtime / "a7v3s3_strict_prequeue_lane_summary.csv", index=False)
    pair_summary.to_csv(runtime / "a7v3s3_strict_prequeue_pair_summary.csv", index=False)
    motif_summary.to_csv(runtime / "a7v3s3_strict_prequeue_motif_summary.csv", index=False)
    skeleton_summary.to_csv(runtime / "a7v3s3_strict_prequeue_skeleton_summary.csv", index=False)

    manifest = {
        "stage": "A7V3S3-STRICT-REWARD-PREQUEUE",
        "generated_at": now_utc(),
        "decision": "PASS_A7V3S3_STRICT_REWARD_PREQUEUE_READY",
        "activity_queue": str(activity_queue),
        "runtime": str(runtime),
        "input_activity_ok_rows": int(queue.shape[0]),
        "structural_excluded_rows": int(structural.sum()),
        "strict_pool_rows": int(strict_pool.shape[0]),
        "target_rows": target,
        "selected_rows": int(selected.shape[0]),
        "lane_count": int(selected["a7ls_lane"].nunique()) if not selected.empty else 0,
        "semantic_pair_count": int(selected["semantic_pair"].nunique()) if not selected.empty else 0,
        "motif_count": int(selected["motif"].nunique()) if not selected.empty else 0,
        "skeleton_count": int(selected["skeleton_key"].nunique()) if not selected.empty and "skeleton_key" in selected else 0,
        "lane_cap": lane_cap,
        "pair_cap": pair_cap,
        "motif_cap": motif_cap,
        "skeleton_cap": skeleton_cap,
        "output_queue": str(runtime / "a7v3s3_strict_reward_prequeue.csv"),
        "authorizes_strict_reward_gate": True,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(runtime / "a7v3s3_strict_reward_prequeue_manifest.json", manifest)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
