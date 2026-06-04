from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
CORE59 = REPO / "runtime" / "a7ffcore59_numeric_repair_execution"
EXTERNAL = Path("G:/AlphaFactory_CryptoData/research_runtime/a7ffcore59_numeric_repair_execution_20260604")

F_RUNTIME = REPO / "runtime" / "a7ffcore59f_non_l7_forensic"
G_RUNTIME = REPO / "runtime" / "a7ffcore59g_attrition_map"
F_REPORT = REPO / "reports" / "CRYPTO_A7FFCORE59F_NON_L7_CLUE_FORENSIC_20260604.md"
G_REPORT = REPO / "reports" / "CRYPTO_A7FFCORE59G_QUEUE_TARGET_ATTRITION_MAP_20260604.md"


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


def md_table(df: pd.DataFrame, max_rows: int = 40) -> str:
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


def collect(name: str, shard_count: int = 6) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for shard in range(shard_count):
        path = EXTERNAL / f"shard_{shard:02d}" / f"a7ffcore59_s{shard:02d}_{name}.csv"
        frame = read_csv(path)
        if not frame.empty:
            frame["core59_shard"] = f"s{shard:02d}"
            frames.append(frame)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def safe_group(df: pd.DataFrame, cols: list[str], name: str = "row_count") -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=cols + [name])
    existing = [c for c in cols if c in df.columns]
    if not existing:
        return pd.DataFrame({name: [len(df)]})
    return df.groupby(existing, dropna=False).size().reset_index(name=name).sort_values(name, ascending=False)


def aggregate_metrics(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    existing = [c for c in group_cols if c in df.columns]
    if df.empty or not existing:
        return pd.DataFrame(columns=existing)
    out = df.groupby(existing, dropna=False).agg(
        rows=("blueprint_id", "size"),
        unique_blueprints=("blueprint_id", "nunique"),
        median_control_ratio=("control_ratio_premay_max", "median"),
        max_control_ratio=("control_ratio_premay_max", "max"),
        min_cost5=("cost5_recent_oriented", "min"),
        min_cost10=("cost10_recent_oriented", "min"),
        median_recent_spread=("recent_oos_2026JanApr_mean_spread", "median"),
        robust_ok_rate=("robust_ok", "mean"),
        lag_ok_rate=("lag_ok", "mean"),
    ).reset_index()
    return out.sort_values(["rows"], ascending=False)


def build_forensic(label: pd.DataFrame, selected: pd.DataFrame, controls: pd.DataFrame) -> dict[str, Any]:
    F_RUNTIME.mkdir(parents=True, exist_ok=True)

    non_l7 = label[
        label.get("decision", pd.Series(dtype=str)).astype(str).str.contains("NUMERIC_CLUE", na=False)
        & (label.get("label_family", pd.Series(dtype=str)).astype(str) != "L7_ranked_future_return")
    ].copy()
    non_l7["control_margin"] = 1.0 - pd.to_numeric(non_l7.get("control_ratio_premay_max"), errors="coerce")
    non_l7["cost2_positive"] = pd.to_numeric(non_l7.get("cost2_recent_oriented"), errors="coerce") > 0
    non_l7["cost5_positive"] = pd.to_numeric(non_l7.get("cost5_recent_oriented"), errors="coerce") > 0
    non_l7["cost10_positive"] = pd.to_numeric(non_l7.get("cost10_recent_oriented"), errors="coerce") > 0

    clue_cols = [
        "core59_shard", "blueprint_id", "semantic_pair", "motif", "label_family", "label_horizon_h",
        "decision", "control_ratio_premay_max", "control_margin", "cost2_recent_oriented",
        "cost5_recent_oriented", "cost10_recent_oriented", "robust_median_tstat_floor",
        "one_bar_lag_recent_oriented", "premay_positive_split_count", "expression",
    ]
    clue_table = non_l7[[c for c in clue_cols if c in non_l7.columns]].sort_values(
        [c for c in ["semantic_pair", "label_family", "blueprint_id"] if c in non_l7.columns]
    )
    clue_table.to_csv(F_RUNTIME / "core59f_non_l7_clue_table.csv", index=False)

    label_breakdown = safe_group(non_l7, ["label_family", "label_horizon_h", "decision"])
    semantic_breakdown = safe_group(non_l7, ["semantic_pair", "motif"])
    control_margin = aggregate_metrics(non_l7, ["semantic_pair", "label_family", "label_horizon_h"])
    cost_net = non_l7.groupby(["semantic_pair", "label_family"], dropna=False).agg(
        rows=("blueprint_id", "size"),
        cost2_positive_rate=("cost2_positive", "mean"),
        cost5_positive_rate=("cost5_positive", "mean"),
        cost10_positive_rate=("cost10_positive", "mean"),
        min_cost10=("cost10_recent_oriented", "min"),
    ).reset_index() if not non_l7.empty else pd.DataFrame()

    selected_non_l7 = selected[
        selected.get("decision", pd.Series(dtype=str)).astype(str).str.contains("NUMERIC_CLUE", na=False)
        & (selected.get("label_family", pd.Series(dtype=str)).astype(str) != "L7_ranked_future_return")
    ].copy()
    selected_overlap = safe_group(selected_non_l7, ["semantic_pair", "label_family", "motif"], "selected_rows")

    state_concentration = pd.DataFrame(
        [
            {
                "audit_item": "symbol_state_concentration",
                "status": "UNAVAILABLE_IN_CORE59_NUMERIC_OUTPUT",
                "reason": "CORE59 shard outputs do not include symbol_id, latent_state_id, meme, liquidity_tier, or per-row state exposure columns.",
                "fallback_used": "semantic_pair/motif/skeleton concentration only",
            }
        ]
    )

    label_breakdown.to_csv(F_RUNTIME / "core59f_label_target_breakdown.csv", index=False)
    semantic_breakdown.to_csv(F_RUNTIME / "core59f_semantic_pair_breakdown.csv", index=False)
    control_margin.to_csv(F_RUNTIME / "core59f_control_margin_audit.csv", index=False)
    cost_net.to_csv(F_RUNTIME / "core59f_cost_net_audit.csv", index=False)
    state_concentration.to_csv(F_RUNTIME / "core59f_symbol_state_concentration.csv", index=False)
    selected_overlap.to_csv(F_RUNTIME / "core59f_selected_overlap.csv", index=False)

    clue_count = int(len(non_l7))
    semantic_count = int(non_l7["semantic_pair"].nunique()) if "semantic_pair" in non_l7.columns and not non_l7.empty else 0
    top_semantic_share = float(non_l7["semantic_pair"].value_counts(normalize=True).iloc[0]) if semantic_count else 0.0
    max_control = float(pd.to_numeric(non_l7.get("control_ratio_premay_max"), errors="coerce").max()) if clue_count else None
    min_cost10 = float(pd.to_numeric(non_l7.get("cost10_recent_oriented"), errors="coerce").min()) if clue_count else None
    all_cost10_positive = bool((pd.to_numeric(non_l7.get("cost10_recent_oriented"), errors="coerce") > 0).all()) if clue_count else False
    all_share_basis = bool(non_l7["semantic_pair"].astype(str).str.contains("basis_premium_like").all()) if clue_count else False

    if clue_count == 0:
        decision = "HOLD_CORE59F_NO_NON_L7_CLUES"
        blockers = ["no_non_l7_clues"]
    elif max_control is not None and max_control >= 0.8:
        decision = "HOLD_CORE59F_THIN_OR_CONTROL_FRAGILE"
        blockers = ["control_ratio_ge_0_8"]
    elif not all_cost10_positive:
        decision = "HOLD_CORE59F_THIN_OR_CONTROL_FRAGILE"
        blockers = ["cost10_not_all_positive"]
    elif semantic_count <= 2 and (top_semantic_share > 0.8 or all_share_basis):
        decision = "HOLD_CORE59F_SINGLE_STRUCTURE_RESIDUAL"
        blockers = ["semantic_width_low", "basis_premium_root_concentration"]
    else:
        decision = "PASS_CORE59F_NARROW_BUT_CLEAN"
        blockers = []

    record = {
        "stage": "A7FF-CORE59F",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "input_core59_decision": read_json(CORE59 / "a7ffcore59_manifest.json").get("decision"),
        "non_l7_clue_rows": clue_count,
        "non_l7_unique_blueprints": int(non_l7["blueprint_id"].nunique()) if "blueprint_id" in non_l7.columns else 0,
        "non_l7_semantic_pair_count": semantic_count,
        "top_semantic_pair_share": top_semantic_share,
        "max_control_ratio": max_control,
        "min_cost10_recent_oriented": min_cost10,
        "all_cost10_positive": all_cost10_positive,
        "symbol_state_concentration_auditable": False,
        "executes_search": False,
        "executes_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
    }
    write_json(F_RUNTIME / "core59f_decision_record.json", record)

    report = [
        "# CRYPTO A7FF-CORE59F NON-L7 CLUE FORENSIC",
        "",
        f"Generated: {record['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE59F audits the six non-L7 numeric clues from CORE59. It does not search, replay, or promote candidates.",
        "",
        "## Decision Record",
        "",
        "```json",
        json.dumps(record, indent=2, sort_keys=True),
        "```",
        "",
        "## Non-L7 Clue Table",
        "",
        md_table(clue_table, 20),
        "",
        "## Label / Target Breakdown",
        "",
        md_table(label_breakdown),
        "",
        "## Semantic Pair Breakdown",
        "",
        md_table(semantic_breakdown),
        "",
        "## Control Margin Audit",
        "",
        md_table(control_margin),
        "",
        "## Cost Net Audit",
        "",
        md_table(cost_net),
        "",
        "## State Concentration Caveat",
        "",
        md_table(state_concentration),
        "",
    ]
    F_REPORT.parent.mkdir(parents=True, exist_ok=True)
    F_REPORT.write_text("\n".join(report), encoding="utf-8")
    return record


def build_attrition(queue: pd.DataFrame, material: pd.DataFrame, label: pd.DataFrame, selected: pd.DataFrame) -> dict[str, Any]:
    G_RUNTIME.mkdir(parents=True, exist_ok=True)

    rank = label[label.get("label_family", pd.Series(dtype=str)).astype(str) == "L7_ranked_future_return"].copy()
    rank = rank[rank.get("decision", pd.Series(dtype=str)).astype(str).str.contains("RANK_LABEL_DIAGNOSTIC_CLUE", na=False)]
    non_l7 = label[
        label.get("decision", pd.Series(dtype=str)).astype(str).str.contains("NUMERIC_CLUE", na=False)
        & (label.get("label_family", pd.Series(dtype=str)).astype(str) != "L7_ranked_future_return")
    ].copy()

    def funnel(cols: list[str]) -> pd.DataFrame:
        keys = [c for c in cols if c in queue.columns or c in material.columns or c in label.columns or c in selected.columns]
        if not keys:
            return pd.DataFrame()
        q = safe_group(queue, keys, "queue_rows")
        m_all = safe_group(material, keys, "materialized_rows")
        m_ok = safe_group(material[material.get("activity_ok", False) == True], keys, "activity_ok_rows") if not material.empty else pd.DataFrame()
        l = safe_group(label, keys, "label_response_rows")
        r = safe_group(rank, keys, "rank_label_clue_rows")
        s = safe_group(selected, keys, "selected_rows")
        n = safe_group(non_l7, keys, "non_l7_rows")
        out = q
        for frame in [m_all, m_ok, l, r, s, n]:
            if frame.empty:
                continue
            out = out.merge(frame, on=[c for c in keys if c in frame.columns and c in out.columns], how="outer")
        for c in ["queue_rows", "materialized_rows", "activity_ok_rows", "label_response_rows", "rank_label_clue_rows", "selected_rows", "non_l7_rows"]:
            if c not in out.columns:
                out[c] = 0
            out[c] = out[c].fillna(0).astype(int)
        out["activity_ok_rate_vs_queue"] = out["activity_ok_rows"] / out["queue_rows"].replace(0, pd.NA)
        out["selected_rate_vs_rank_clue"] = out["selected_rows"] / out["rank_label_clue_rows"].replace(0, pd.NA)
        out["non_l7_rate_vs_selected"] = out["non_l7_rows"] / out["selected_rows"].replace(0, pd.NA)
        return out.sort_values(["queue_rows", "activity_ok_rows", "non_l7_rows"], ascending=False)

    by_family = funnel(["semantic_pair"])
    by_semantic = funnel(["semantic_pair"])
    by_motif = funnel(["motif"])
    by_target = safe_group(label, ["label_family", "label_horizon_h", "decision"], "label_response_rows")

    material_failure = material.copy()
    if not material_failure.empty:
        material_failure["materialization_status"] = material_failure.apply(
            lambda r: "eval_fail" if not bool(r.get("eval_success")) else ("activity_ok" if bool(r.get("activity_ok")) else "inactive_or_sparse"),
            axis=1,
        )
    material_failure_map = safe_group(material_failure, ["semantic_pair", "motif", "materialization_status"], "rows")

    selector_rejection = pd.concat(
        [
            rank.assign(selector_stage="rank_label_diagnostic_clue"),
            selected.assign(selector_stage="selected_portfolio_queue"),
            non_l7.assign(selector_stage="non_l7_numeric_clue"),
        ],
        ignore_index=True,
        sort=False,
    )
    selector_map = safe_group(selector_rejection, ["selector_stage", "semantic_pair", "motif", "label_family"], "rows")

    non_l7_loss = by_semantic.copy()
    if not non_l7_loss.empty:
        non_l7_loss["rank_to_non_l7_loss_rows"] = non_l7_loss["rank_label_clue_rows"] - non_l7_loss["non_l7_rows"]
        non_l7_loss["selected_to_non_l7_loss_rows"] = non_l7_loss["selected_rows"] - non_l7_loss["non_l7_rows"]
    non_l7_loss = non_l7_loss.sort_values(["rank_to_non_l7_loss_rows", "selected_to_non_l7_loss_rows"], ascending=False) if not non_l7_loss.empty else non_l7_loss

    outputs = {
        "core59g_funnel_by_family.csv": by_family,
        "core59g_funnel_by_semantic_pair.csv": by_semantic,
        "core59g_funnel_by_operator_motif.csv": by_motif,
        "core59g_funnel_by_target.csv": by_target,
        "core59g_materialization_failure_map.csv": material_failure_map,
        "core59g_selector_rejection_map.csv": selector_map,
        "core59g_non_l7_loss_map.csv": non_l7_loss,
    }
    for name, df in outputs.items():
        df.to_csv(G_RUNTIME / name, index=False)

    queue_rows = int(len(queue))
    activity_ok = int(material.get("activity_ok", pd.Series(dtype=bool)).fillna(False).astype(bool).sum()) if not material.empty else 0
    rank_rows = int(len(rank))
    selected_rows = int(len(selected))
    non_l7_rows = int(len(non_l7))
    non_l7_semantic = int(non_l7["semantic_pair"].nunique()) if "semantic_pair" in non_l7.columns and not non_l7.empty else 0
    top_queue_share = float(queue["semantic_pair"].value_counts(normalize=True).iloc[0]) if "semantic_pair" in queue.columns and not queue.empty else 0.0
    top_selected_share = float(selected["semantic_pair"].value_counts(normalize=True).iloc[0]) if "semantic_pair" in selected.columns and not selected.empty else 0.0
    top_non_l7_share = float(non_l7["semantic_pair"].value_counts(normalize=True).iloc[0]) if "semantic_pair" in non_l7.columns and not non_l7.empty else 0.0

    blockers: list[str] = []
    if non_l7_semantic < 4:
        blockers.append("queue_non_l7_semantic_width_lt_4")
    if top_non_l7_share > 0.8:
        blockers.append("non_l7_top_semantic_pair_share_gt_0_8")
    if top_selected_share > 0.5:
        blockers.append("selected_queue_semantic_concentration_gt_0_5")
    if activity_ok / queue_rows < 0.6:
        blockers.append("activity_ok_rate_lt_0_6")

    if "queue_non_l7_semantic_width_lt_4" in blockers:
        decision = "HOLD_CORE59G_QUEUE_COVERAGE_TOO_NARROW"
    elif "selected_queue_semantic_concentration_gt_0_5" in blockers:
        decision = "HOLD_CORE59G_SELECTOR_STILL_RANK_BIASED"
    elif "activity_ok_rate_lt_0_6" in blockers:
        decision = "HOLD_CORE59G_MATERIALIZATION_BOTTLENECK"
    else:
        decision = "PASS_CORE59G_ATTRITION_EXPLAINED"

    record = {
        "stage": "A7FF-CORE59G",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "queue_rows": queue_rows,
        "activity_ok_rows": activity_ok,
        "label_response_rows": int(len(label)),
        "rank_label_diagnostic_clue_rows": rank_rows,
        "selected_portfolio_queue_rows": selected_rows,
        "non_l7_numeric_clue_rows": non_l7_rows,
        "non_l7_semantic_pair_count": non_l7_semantic,
        "activity_ok_rate": activity_ok / queue_rows if queue_rows else None,
        "top_queue_semantic_share": top_queue_share,
        "top_selected_semantic_share": top_selected_share,
        "top_non_l7_semantic_share": top_non_l7_share,
        "executes_search": False,
        "executes_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
    }
    write_json(G_RUNTIME / "core59g_decision_record.json", record)

    report = [
        "# CRYPTO A7FF-CORE59G QUEUE TARGET ATTRITION MAP",
        "",
        f"Generated: {record['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE59G maps attrition from queue to materialization, rank-label diagnostics, selected queue, and non-L7 clues. It does not search, replay, or promote candidates.",
        "",
        "## Decision Record",
        "",
        "```json",
        json.dumps(record, indent=2, sort_keys=True),
        "```",
        "",
        "## Funnel By Semantic Pair",
        "",
        md_table(by_semantic, 30),
        "",
        "## Funnel By Motif",
        "",
        md_table(by_motif, 30),
        "",
        "## Funnel By Target",
        "",
        md_table(by_target, 40),
        "",
        "## Materialization Failure Map",
        "",
        md_table(material_failure_map, 40),
        "",
        "## Selector Rejection / Survival Map",
        "",
        md_table(selector_map, 40),
        "",
        "## Non-L7 Loss Map",
        "",
        md_table(non_l7_loss, 30),
        "",
    ]
    G_REPORT.parent.mkdir(parents=True, exist_ok=True)
    G_REPORT.write_text("\n".join(report), encoding="utf-8")
    return record


def main() -> None:
    label = collect("label_response_metrics")
    controls = collect("control_dominance_metrics")
    selected = collect("selected_portfolio_queue")
    material = collect("materialization_metrics")
    queue = collect("queue")

    if queue.empty:
        queue = read_csv(CORE59 / "a7ffcore59_numeric_repair_queue.csv")
    if label.empty:
        raise SystemExit("CORE59 label_response_metrics are empty; cannot run F/G")

    f_record = build_forensic(label, selected, controls)
    g_record = build_attrition(queue, material, label, selected)
    print(json.dumps({"CORE59F": f_record, "CORE59G": g_record}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
