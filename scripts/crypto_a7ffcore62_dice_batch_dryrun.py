from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
SSM = REPO / "runtime" / "a7ssm_search_space_memory_map"
CORE61 = REPO / "runtime" / "a7ffcore61_integrated_repair_plan"
CORE60C = REPO / "runtime" / "a7ffcore60c_materialization_repair_audit"

RUNTIME = REPO / "runtime" / "a7ffcore62_dice_batch_dryrun"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE62_DICE_BATCH_DRYRUN_20260605.md"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 60) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    try:
        return view.to_markdown(index=False)
    except ImportError:
        return "```csv\n" + view.to_csv(index=False) + "```"


def diversified_take(df: pd.DataFrame, limit: int, group_cols: list[str]) -> pd.DataFrame:
    if df.empty:
        return df
    work = df.copy()
    work["_rank"] = range(len(work))
    selected = []
    seen = set()
    for _, row in work.iterrows():
        key = tuple(row.get(c) for c in group_cols)
        if key in seen:
            continue
        selected.append(row)
        seen.add(key)
        if len(selected) >= limit:
            break
    if len(selected) < limit:
        used_ids = {r.get("blueprint_id") for r in selected}
        for _, row in work.iterrows():
            if row.get("blueprint_id") in used_ids:
                continue
            selected.append(row)
            used_ids.add(row.get("blueprint_id"))
            if len(selected) >= limit:
                break
    return pd.DataFrame(selected).drop(columns=["_rank"], errors="ignore")


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    ssm = read_json(SSM / "a7ssm_manifest.json")
    selector_map = read_csv(SSM / "a7ssm_selector_eligibility_map.csv")
    pair_map = read_csv(SSM / "a7ssm_interaction_permission_matrix.csv")
    core61_preview = read_csv(CORE61 / "core61_repair_candidate_queue_preview.csv")
    material_pairs = read_csv(CORE60C / "core60c_materialization_by_semantic_pair.csv")

    if selector_map.empty or core61_preview.empty:
        raise SystemExit("CORE62 requires A7SSM selector map and CORE61 repair preview")

    selector_map["control_ratio"] = pd.to_numeric(selector_map["control_ratio"], errors="coerce")
    selector_map["cost10"] = pd.to_numeric(selector_map["cost10"], errors="coerce")
    selector_map["premay_positive_split_count"] = pd.to_numeric(selector_map["premay_positive_split_count"], errors="coerce")
    selector_map["selector_eligible"] = selector_map.get("selector_eligible", False).fillna(False).astype(bool)

    # Dice arm B: non-L7 target near-miss, not exact clean enough for search, but useful for repair dryrun.
    near_miss = selector_map[
        selector_map["core61_reason"].astype(str).str.startswith("near_miss")
        & selector_map["search_permission"].ne("blocked_until_materialized")
        & selector_map["label_family"].ne("L7_ranked_future_return")
        & selector_map["control_ratio"].lt(1.0)
        & selector_map["cost10"].gt(0)
    ].copy()
    near_miss = near_miss.sort_values(
        ["premay_positive_split_count", "control_ratio", "cost10"],
        ascending=[False, True, False],
    )
    dice_b = diversified_take(near_miss, 48, ["semantic_pair", "motif", "label_family"])
    dice_b["dice_arm"] = "CORE62B_target_near_miss_repair"

    # Dice arm C: materialization repair tasks for zero-activity semantic pairs.
    zero_pairs = material_pairs[pd.to_numeric(material_pairs.get("activity_ok_rows"), errors="coerce").fillna(0).eq(0)].copy()
    zero_pairs["dice_arm"] = "CORE62C_materialization_repair"
    zero_pairs["repair_task"] = zero_pairs["semantic_pair"].map(
        lambda x: "audit_field_coverage_and_transform_activity_for_" + str(x).replace("|", "_x_")
    )
    dice_c = zero_pairs[[
        "dice_arm", "semantic_pair", "queue_rows", "activity_ok_rows", "inactive_rows",
        "median_finite_share", "median_nonzero_share", "repair_task",
    ]].copy()

    dice_queue = pd.concat([dice_b, dice_c], ignore_index=True, sort=False)
    dice_queue.to_csv(RUNTIME / "core62_dice_batch_queue.csv", index=False)

    dice_summary = dice_queue.groupby(["dice_arm", "semantic_pair"], dropna=False).agg(
        rows=("dice_arm", "size"),
        unique_blueprints=("blueprint_id", "nunique"),
    ).reset_index().sort_values(["dice_arm", "rows"], ascending=[True, False])
    dice_summary.to_csv(RUNTIME / "core62_dice_batch_summary.csv", index=False)

    selector_caps = {
        "selected_l7_share_max": 0.40,
        "selected_non_l7_min": 12,
        "selected_semantic_pair_min": 4,
        "top_semantic_pair_share_max": 0.35,
        "control_ratio_max": 1.0,
        "cost10_min": 0.0,
    }
    write_json(RUNTIME / "core62_selector_caps.json", selector_caps)

    b_rows = int(len(dice_b))
    b_semantics = int(dice_b["semantic_pair"].nunique()) if b_rows else 0
    c_rows = int(len(dice_c))
    blockers = []
    if b_rows < 24:
        blockers.append("core62b_dice_rows_lt_24")
    if b_semantics < 4:
        blockers.append("core62b_semantic_pair_count_lt_4")
    if c_rows == 0:
        blockers.append("core62c_no_materialization_tasks")

    decision = "PASS_CORE62_DICE_BATCH_READY_FOR_PARALLEL_DRYRUN" if not blockers else "HOLD_CORE62_DICE_BATCH_TOO_NARROW"
    manifest = {
        "stage": "A7FF-CORE62",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "source_a7ssm_decision": ssm.get("decision"),
        "dice_batch_rows": int(len(dice_queue)),
        "core62b_target_near_miss_rows": b_rows,
        "core62b_semantic_pair_count": b_semantics,
        "core62c_materialization_task_rows": c_rows,
        "executes_search": False,
        "executes_replay": False,
        "authorizes_parallel_dryrun": decision.startswith("PASS"),
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
    }
    write_json(RUNTIME / "core62_decision_record.json", manifest)
    write_json(RUNTIME / "core62_manifest.json", manifest)

    REPORT.write_text("\n".join([
        "# CRYPTO A7FF-CORE62 DICE BATCH DRYRUN",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE62 throws the next controlled dice batch from the A7SSM map. It builds dryrun queues only; no search, replay, promotion, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Dice Summary",
        "",
        md_table(dice_summary, 60),
        "",
        "## Selector Caps",
        "",
        "```json",
        json.dumps(selector_caps, indent=2, sort_keys=True),
        "```",
        "",
        "## Dice Queue Preview",
        "",
        md_table(dice_queue, 80),
        "",
    ]), encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
