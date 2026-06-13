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
        "A7V3S5_ACTIVITY_QUEUE",
        r"D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7v3s0_v3_native_large_search_c2_aggregate_20260613\a7ls17_activity_ok_queue.csv",
    )
)
DEFAULT_RULES = Path(
    os.environ.get(
        "A7V3S5_PREFILTER_RULES",
        r"D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7v3s5_prefiltered_queue_20260613\a7v3s4_search_space_prefilter_rules.json",
    )
)
DEFAULT_RUNTIME = Path(
    os.environ.get(
        "A7V3S5_RUNTIME",
        r"D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7v3s5_prefiltered_queue_20260613",
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


def pair_motif_key(frame: pd.DataFrame) -> pd.Series:
    return frame.get("semantic_pair", pd.Series("", index=frame.index)).fillna("").astype(str) + "\t" + frame.get(
        "motif", pd.Series("", index=frame.index)
    ).fillna("").astype(str)


def rule_keys(records: list[dict[str, Any]]) -> set[str]:
    return {str(r.get("semantic_pair", "")) + "\t" + str(r.get("motif", "")) for r in records}


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
    ranked = frame.copy()
    sort_cols = [col for col in ["finite_share", "nonzero_share", "std_value"] if col in ranked.columns]
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

    return pd.DataFrame(selected).head(target).copy()


def summary(frame: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=keys + ["count"])
    return frame.groupby(keys, dropna=False).size().reset_index(name="count").sort_values("count", ascending=False)


def main() -> None:
    activity_queue = Path(os.environ.get("A7V3S5_ACTIVITY_QUEUE", str(DEFAULT_ACTIVITY_QUEUE)))
    rules_path = Path(os.environ.get("A7V3S5_PREFILTER_RULES", str(DEFAULT_RULES)))
    runtime = Path(os.environ.get("A7V3S5_RUNTIME", str(DEFAULT_RUNTIME)))
    target = int(os.environ.get("A7V3S5_TARGET", "4096"))
    lane_cap = int(os.environ.get("A7V3S5_LANE_CAP", str(max(1, target // 3))))
    pair_cap = int(os.environ.get("A7V3S5_PAIR_CAP", "96"))
    motif_cap = int(os.environ.get("A7V3S5_MOTIF_CAP", "640"))
    skeleton_cap = int(os.environ.get("A7V3S5_SKELETON_CAP", "12"))

    runtime.mkdir(parents=True, exist_ok=True)
    rules = json.loads(rules_path.read_text(encoding="utf-8"))
    hard_block = rule_keys(rules.get("hard_block_pair_motif", []))
    deprioritize = rule_keys(rules.get("deprioritize_recent_only_pair_motif", []))
    redesign = rule_keys(rules.get("redesign_pair_motif_not_reward_as_is", []))

    queue = pd.read_csv(activity_queue, low_memory=False)
    queue = queue[(queue["eval_success"].astype(bool)) & (queue["activity_ok"].astype(bool))].copy()
    queue["_pair_motif_key"] = pair_motif_key(queue)
    queue["_structural_excluded"] = structural_mask(queue)
    queue["_hard_blocked_by_a7v3s4"] = queue["_pair_motif_key"].isin(hard_block)
    queue["_deprioritized_by_a7v3s4"] = queue["_pair_motif_key"].isin(deprioritize)
    queue["_redesign_only_by_a7v3s4"] = queue["_pair_motif_key"].isin(redesign)

    hard_reject_mask = queue["_structural_excluded"] | queue["_hard_blocked_by_a7v3s4"] | queue["_deprioritized_by_a7v3s4"]
    eligible = queue[~hard_reject_mask & ~queue["_redesign_only_by_a7v3s4"]].copy()
    redesign_hold = queue[queue["_redesign_only_by_a7v3s4"] & ~hard_reject_mask].copy()
    selected = bounded_select(eligible, target, lane_cap, pair_cap, motif_cap, skeleton_cap)

    selected.drop(columns=[c for c in selected.columns if c.startswith("_")], errors="ignore").to_csv(
        runtime / "a7v3s5_prefiltered_reward_prequeue.csv", index=False
    )
    redesign_hold.drop(columns=[c for c in redesign_hold.columns if c.startswith("_")], errors="ignore").to_csv(
        runtime / "a7v3s5_redesign_hold_queue.csv", index=False
    )

    reject_rows = pd.DataFrame(
        [
            {"reason": "structural_excluded", "count": int(queue["_structural_excluded"].sum())},
            {"reason": "hard_blocked_by_a7v3s4", "count": int(queue["_hard_blocked_by_a7v3s4"].sum())},
            {"reason": "deprioritized_recent_only_by_a7v3s4", "count": int(queue["_deprioritized_by_a7v3s4"].sum())},
            {"reason": "redesign_only_by_a7v3s4", "count": int(queue["_redesign_only_by_a7v3s4"].sum())},
        ]
    )
    reject_rows.to_csv(runtime / "a7v3s5_prefilter_reject_summary.csv", index=False)
    summary(selected, ["a7ls_lane"]).to_csv(runtime / "a7v3s5_selected_lane_summary.csv", index=False)
    summary(selected, ["semantic_pair"]).to_csv(runtime / "a7v3s5_selected_pair_summary.csv", index=False)
    summary(selected, ["motif"]).to_csv(runtime / "a7v3s5_selected_motif_summary.csv", index=False)
    summary(selected, ["semantic_pair", "motif"]).to_csv(runtime / "a7v3s5_selected_pair_motif_summary.csv", index=False)

    manifest = {
        "stage": "A7V3S5_PREFILTERED_REWARD_QUEUE",
        "generated_at": now_utc(),
        "decision": "PASS_A7V3S5_PREFILTERED_QUEUE_READY" if not selected.empty else "HOLD_A7V3S5_EMPTY_PREFILTERED_QUEUE",
        "activity_queue": str(activity_queue),
        "rules_path": str(rules_path),
        "runtime": str(runtime),
        "input_activity_ok_rows": int(queue.shape[0]),
        "structural_excluded_rows": int(queue["_structural_excluded"].sum()),
        "hard_blocked_rows": int(queue["_hard_blocked_by_a7v3s4"].sum()),
        "deprioritized_recent_only_rows": int(queue["_deprioritized_by_a7v3s4"].sum()),
        "redesign_hold_rows": int(redesign_hold.shape[0]),
        "eligible_rows": int(eligible.shape[0]),
        "target_rows": target,
        "selected_rows": int(selected.shape[0]),
        "selected_semantic_pair_count": int(selected["semantic_pair"].nunique()) if not selected.empty else 0,
        "selected_motif_count": int(selected["motif"].nunique()) if not selected.empty else 0,
        "selected_skeleton_count": int(selected["skeleton_key"].nunique()) if "skeleton_key" in selected else 0,
        "output_queue": str(runtime / "a7v3s5_prefiltered_reward_prequeue.csv"),
        "redesign_hold_queue": str(runtime / "a7v3s5_redesign_hold_queue.csv"),
        "authorizes_reward_smoke": True,
        "authorizes_full_reward_wave": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(runtime / "a7v3s5_manifest.json", manifest)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
