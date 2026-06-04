from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
EXTERNAL = Path("G:/AlphaFactory_CryptoData/research_runtime/a7ffcore59_numeric_repair_execution_20260604")
CORE59 = REPO / "runtime" / "a7ffcore59_numeric_repair_execution"

RUNTIME_B = REPO / "runtime" / "a7ffcore60b_target_adequacy_repair_audit"
RUNTIME_C = REPO / "runtime" / "a7ffcore60c_materialization_repair_audit"
RUNTIME_D = REPO / "runtime" / "a7ffcore60d_selector_portfolio_proxy_attribution"

REPORT_B = REPO / "reports" / "CRYPTO_A7FFCORE60B_TARGET_ADEQUACY_REPAIR_AUDIT_20260605.md"
REPORT_C = REPO / "reports" / "CRYPTO_A7FFCORE60C_MATERIALIZATION_REPAIR_AUDIT_20260605.md"
REPORT_D = REPO / "reports" / "CRYPTO_A7FFCORE60D_SELECTOR_PORTFOLIO_PROXY_ATTRIBUTION_20260605.md"


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


def classify_decision(decision: Any) -> str:
    text = str(decision)
    if "NUMERIC_CLUE" in text and "RANK_LABEL" not in text:
        return "non_l7_numeric_clue"
    if "RANK_LABEL_DIAGNOSTIC_CLUE" in text:
        return "rank_label_diagnostic_clue"
    if "PRE_MAY_UNSTABLE" in text:
        return "pre_may_unstable"
    if "CONTROL_DOMINATED" in text:
        return "control_dominated"
    if "ONE_BAR_LAG_FRAGILE" in text:
        return "one_bar_lag_fragile"
    if "COST" in text:
        return "cost_fragile"
    return "other"


def safe_bool_mean(series: pd.Series) -> float:
    if series.empty:
        return 0.0
    return float(series.fillna(False).astype(bool).mean())


def build_target_audit(label: pd.DataFrame) -> dict[str, Any]:
    RUNTIME_B.mkdir(parents=True, exist_ok=True)
    df = label.copy()
    df["decision_class"] = df["decision"].map(classify_decision)
    df["is_non_l7"] = (df["decision_class"] == "non_l7_numeric_clue") & (df["label_family"] != "L7_ranked_future_return")
    df["is_rank_label"] = df["decision_class"] == "rank_label_diagnostic_clue"
    df["is_premay_unstable"] = df["decision_class"] == "pre_may_unstable"
    df["is_control_dominated"] = df["decision_class"] == "control_dominated"
    df["cost10_positive"] = pd.to_numeric(df.get("cost10_recent_oriented"), errors="coerce") > 0

    target_summary = df.groupby(["label_family", "label_horizon_h"], dropna=False).agg(
        rows=("blueprint_id", "size"),
        unique_blueprints=("blueprint_id", "nunique"),
        premay_unstable_rows=("is_premay_unstable", "sum"),
        control_dominated_rows=("is_control_dominated", "sum"),
        rank_label_rows=("is_rank_label", "sum"),
        non_l7_rows=("is_non_l7", "sum"),
        median_control_ratio=("control_ratio_premay_max", "median"),
        median_cost10=("cost10_recent_oriented", "median"),
        cost10_positive_rate=("cost10_positive", "mean"),
        premay_all_positive_rate=("premay_all_positive", lambda s: safe_bool_mean(s)),
        robust_ok_rate=("robust_ok", lambda s: safe_bool_mean(s)),
        lag_ok_rate=("lag_ok", lambda s: safe_bool_mean(s)),
    ).reset_index()
    target_summary["premay_unstable_rate"] = target_summary["premay_unstable_rows"] / target_summary["rows"].replace(0, pd.NA)
    target_summary["control_dominated_rate"] = target_summary["control_dominated_rows"] / target_summary["rows"].replace(0, pd.NA)
    target_summary["non_l7_rate"] = target_summary["non_l7_rows"] / target_summary["rows"].replace(0, pd.NA)
    target_summary = target_summary.sort_values(["non_l7_rows", "rank_label_rows", "rows"], ascending=False)

    label_family_summary = df.groupby("label_family", dropna=False).agg(
        rows=("blueprint_id", "size"),
        unique_blueprints=("blueprint_id", "nunique"),
        premay_unstable_rows=("is_premay_unstable", "sum"),
        control_dominated_rows=("is_control_dominated", "sum"),
        rank_label_rows=("is_rank_label", "sum"),
        non_l7_rows=("is_non_l7", "sum"),
        median_control_ratio=("control_ratio_premay_max", "median"),
        median_cost10=("cost10_recent_oriented", "median"),
        cost10_positive_rate=("cost10_positive", "mean"),
    ).reset_index()
    label_family_summary["non_l7_share"] = label_family_summary["non_l7_rows"] / max(1, int(df["is_non_l7"].sum()))
    label_family_summary = label_family_summary.sort_values(["non_l7_rows", "rank_label_rows"], ascending=False)

    target_decision_matrix = df.groupby(["label_family", "label_horizon_h", "decision_class"], dropna=False).size().reset_index(name="rows")
    target_decision_matrix = target_decision_matrix.sort_values("rows", ascending=False)

    rank_vs_non_l7 = df.groupby(["semantic_pair", "label_family"], dropna=False).agg(
        rank_label_rows=("is_rank_label", "sum"),
        non_l7_rows=("is_non_l7", "sum"),
        rows=("blueprint_id", "size"),
        median_control_ratio=("control_ratio_premay_max", "median"),
        median_cost10=("cost10_recent_oriented", "median"),
    ).reset_index()
    rank_vs_non_l7["rank_to_non_l7_gap"] = rank_vs_non_l7["rank_label_rows"] - rank_vs_non_l7["non_l7_rows"]
    rank_vs_non_l7 = rank_vs_non_l7.sort_values("rank_to_non_l7_gap", ascending=False)

    for name, out in [
        ("core60b_target_summary.csv", target_summary),
        ("core60b_label_family_summary.csv", label_family_summary),
        ("core60b_target_decision_matrix.csv", target_decision_matrix),
        ("core60b_rank_vs_non_l7_target_gap.csv", rank_vs_non_l7),
    ]:
        out.to_csv(RUNTIME_B / name, index=False)

    non_l7_rows = int(df["is_non_l7"].sum())
    non_l7_target_count = int(df.loc[df["is_non_l7"], ["label_family", "label_horizon_h"]].drop_duplicates().shape[0])
    premay_unstable_rate = float(df["is_premay_unstable"].mean()) if len(df) else 0.0
    control_dominated_rate = float(df["is_control_dominated"].mean()) if len(df) else 0.0
    l7_rank_rows = int(df.loc[df["label_family"] == "L7_ranked_future_return", "is_rank_label"].sum())

    blockers: list[str] = []
    if non_l7_target_count < 4:
        blockers.append("non_l7_target_count_lt_4")
    if premay_unstable_rate > 0.6:
        blockers.append("premay_unstable_rate_gt_0_6")
    if control_dominated_rate > 0.25:
        blockers.append("control_dominated_rate_gt_0_25")
    if l7_rank_rows > 100 and non_l7_rows < 12:
        blockers.append("rank_label_gap_large")

    if "premay_unstable_rate_gt_0_6" in blockers or "rank_label_gap_large" in blockers:
        decision = "HOLD_CORE60B_TARGET_ADEQUACY_REPAIR_REQUIRED"
    elif blockers:
        decision = "HOLD_CORE60B_TARGET_GATE_OR_CONTROL_FRAGILE"
    else:
        decision = "PASS_CORE60B_TARGET_ADEQUACY_ACCEPTABLE"

    record = {
        "stage": "A7FF-CORE60B",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "label_response_rows": int(len(df)),
        "non_l7_rows": non_l7_rows,
        "non_l7_target_count": non_l7_target_count,
        "l7_rank_label_rows": l7_rank_rows,
        "premay_unstable_rate": premay_unstable_rate,
        "control_dominated_rate": control_dominated_rate,
        "executes_search": False,
        "executes_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
    }
    write_json(RUNTIME_B / "core60b_decision_record.json", record)

    REPORT_B.write_text("\n".join([
        "# CRYPTO A7FF-CORE60B TARGET ADEQUACY REPAIR AUDIT",
        "",
        f"Generated: {record['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE60B audits target gate behavior from CORE59 outputs. It does not relax gates, search, replay, or promote candidates.",
        "",
        "## Decision Record",
        "",
        "```json",
        json.dumps(record, indent=2, sort_keys=True),
        "```",
        "",
        "## Label Family Summary",
        "",
        md_table(label_family_summary, 20),
        "",
        "## Target Summary",
        "",
        md_table(target_summary, 40),
        "",
        "## Target Decision Matrix",
        "",
        md_table(target_decision_matrix, 40),
        "",
        "## Rank vs Non-L7 Target Gap",
        "",
        md_table(rank_vs_non_l7, 40),
        "",
    ]), encoding="utf-8")
    return record


def build_materialization_audit(queue: pd.DataFrame, material: pd.DataFrame) -> dict[str, Any]:
    RUNTIME_C.mkdir(parents=True, exist_ok=True)
    df = material.copy()
    df["status"] = df.apply(
        lambda r: "eval_fail" if not bool(r.get("eval_success")) else ("activity_ok" if bool(r.get("activity_ok")) else "inactive_or_sparse"),
        axis=1,
    )
    merged = queue.merge(
        df[["blueprint_id", "eval_success", "finite_share", "nonzero_share", "activity_ok", "status", "std_value", "error"]],
        on="blueprint_id",
        how="left",
        suffixes=("", "_mat"),
    )
    merged["status"] = merged["status"].fillna("not_materialized")
    merged["is_activity_ok"] = merged["status"] == "activity_ok"
    merged["is_inactive"] = merged["status"] == "inactive_or_sparse"
    merged["is_eval_fail"] = merged["status"] == "eval_fail"

    by_semantic = merged.groupby("semantic_pair", dropna=False).agg(
        queue_rows=("blueprint_id", "size"),
        activity_ok_rows=("is_activity_ok", "sum"),
        inactive_rows=("is_inactive", "sum"),
        eval_fail_rows=("is_eval_fail", "sum"),
        median_finite_share=("finite_share", "median"),
        median_nonzero_share=("nonzero_share", "median"),
        median_std_value=("std_value", "median"),
    ).reset_index()
    by_semantic["activity_ok_rate"] = by_semantic["activity_ok_rows"] / by_semantic["queue_rows"].replace(0, pd.NA)
    by_semantic = by_semantic.sort_values(["activity_ok_rate", "queue_rows"], ascending=[True, False])

    by_motif = merged.groupby(["semantic_pair", "motif"], dropna=False).agg(
        queue_rows=("blueprint_id", "size"),
        activity_ok_rows=("is_activity_ok", "sum"),
        inactive_rows=("is_inactive", "sum"),
        eval_fail_rows=("is_eval_fail", "sum"),
        median_finite_share=("finite_share", "median"),
        median_nonzero_share=("nonzero_share", "median"),
        median_std_value=("std_value", "median"),
    ).reset_index()
    by_motif["activity_ok_rate"] = by_motif["activity_ok_rows"] / by_motif["queue_rows"].replace(0, pd.NA)
    by_motif = by_motif.sort_values(["activity_ok_rate", "queue_rows"], ascending=[True, False])

    by_field = pd.concat(
        [
            merged.rename(columns={"primary_field": "field"})[["field", "semantic_pair", "motif", "status", "blueprint_id", "finite_share", "nonzero_share"]],
            merged.rename(columns={"secondary_field": "field"})[["field", "semantic_pair", "motif", "status", "blueprint_id", "finite_share", "nonzero_share"]],
        ],
        ignore_index=True,
    )
    by_field = by_field[by_field["field"].notna()]
    by_field_summary = by_field.groupby("field", dropna=False).agg(
        usages=("blueprint_id", "size"),
        activity_ok_rows=("status", lambda s: int((s == "activity_ok").sum())),
        inactive_rows=("status", lambda s: int((s == "inactive_or_sparse").sum())),
        eval_fail_rows=("status", lambda s: int((s == "eval_fail").sum())),
        median_finite_share=("finite_share", "median"),
        median_nonzero_share=("nonzero_share", "median"),
    ).reset_index()
    by_field_summary["activity_ok_rate"] = by_field_summary["activity_ok_rows"] / by_field_summary["usages"].replace(0, pd.NA)
    by_field_summary = by_field_summary.sort_values(["activity_ok_rate", "usages"], ascending=[True, False])

    inactive_examples = merged[merged["status"] != "activity_ok"].sort_values(["semantic_pair", "motif"]).head(200)

    for name, out in [
        ("core60c_materialization_by_semantic_pair.csv", by_semantic),
        ("core60c_materialization_by_semantic_motif.csv", by_motif),
        ("core60c_materialization_by_field.csv", by_field_summary),
        ("core60c_inactive_or_failed_examples.csv", inactive_examples),
    ]:
        out.to_csv(RUNTIME_C / name, index=False)

    queue_rows = int(len(merged))
    activity_ok_rows = int(merged["is_activity_ok"].sum())
    inactive_rows = int(merged["is_inactive"].sum())
    eval_fail_rows = int(merged["is_eval_fail"].sum())
    zero_activity_semantics = int((by_semantic["activity_ok_rows"] == 0).sum()) if not by_semantic.empty else 0

    blockers: list[str] = []
    if activity_ok_rows / max(1, queue_rows) < 0.6:
        blockers.append("activity_ok_rate_lt_0_6")
    if zero_activity_semantics > 0:
        blockers.append("semantic_pairs_with_zero_activity_ok")
    if eval_fail_rows > 0:
        blockers.append("eval_fail_rows_gt_0")

    decision = "HOLD_CORE60C_MATERIALIZATION_REPAIR_REQUIRED" if blockers else "PASS_CORE60C_MATERIALIZATION_ACCEPTABLE"
    record = {
        "stage": "A7FF-CORE60C",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "queue_rows": queue_rows,
        "activity_ok_rows": activity_ok_rows,
        "inactive_or_sparse_rows": inactive_rows,
        "eval_fail_rows": eval_fail_rows,
        "activity_ok_rate": activity_ok_rows / max(1, queue_rows),
        "zero_activity_semantic_pair_count": zero_activity_semantics,
        "executes_search": False,
        "executes_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
    }
    write_json(RUNTIME_C / "core60c_decision_record.json", record)
    REPORT_C.write_text("\n".join([
        "# CRYPTO A7FF-CORE60C MATERIALIZATION REPAIR AUDIT",
        "",
        f"Generated: {record['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE60C audits materialization attrition from CORE59. It does not search, replay, or promote candidates.",
        "",
        "## Decision Record",
        "",
        "```json",
        json.dumps(record, indent=2, sort_keys=True),
        "```",
        "",
        "## Materialization By Semantic Pair",
        "",
        md_table(by_semantic, 30),
        "",
        "## Materialization By Semantic Pair / Motif",
        "",
        md_table(by_motif, 40),
        "",
        "## Materialization By Field",
        "",
        md_table(by_field_summary, 40),
        "",
        "## Inactive / Failed Examples",
        "",
        md_table(inactive_examples[["blueprint_id", "semantic_pair", "motif", "primary_field", "secondary_field", "status", "finite_share", "nonzero_share", "expression"]], 30),
        "",
    ]), encoding="utf-8")
    return record


def build_selector_audit(label: pd.DataFrame, selected: pd.DataFrame) -> dict[str, Any]:
    RUNTIME_D.mkdir(parents=True, exist_ok=True)
    df = label.copy()
    df["decision_class"] = df["decision"].map(classify_decision)
    df["is_rank_label"] = df["decision_class"] == "rank_label_diagnostic_clue"
    df["is_non_l7"] = (df["decision_class"] == "non_l7_numeric_clue") & (df["label_family"] != "L7_ranked_future_return")
    selected_ids = set(selected.get("blueprint_id", pd.Series(dtype=str)).astype(str))
    df["selected_blueprint"] = df["blueprint_id"].astype(str).isin(selected_ids)

    pool_vs_selected = df.groupby(["semantic_pair", "motif"], dropna=False).agg(
        label_rows=("blueprint_id", "size"),
        unique_blueprints=("blueprint_id", "nunique"),
        rank_label_rows=("is_rank_label", "sum"),
        non_l7_rows=("is_non_l7", "sum"),
        selected_blueprint_rows=("selected_blueprint", "sum"),
        median_control_ratio=("control_ratio_premay_max", "median"),
        median_cost10=("cost10_recent_oriented", "median"),
    ).reset_index()
    pool_vs_selected["selected_rate_vs_rank"] = pool_vs_selected["selected_blueprint_rows"] / pool_vs_selected["rank_label_rows"].replace(0, pd.NA)
    pool_vs_selected["non_l7_rate_vs_selected_rows"] = pool_vs_selected["non_l7_rows"] / pool_vs_selected["selected_blueprint_rows"].replace(0, pd.NA)
    pool_vs_selected = pool_vs_selected.sort_values(["selected_blueprint_rows", "rank_label_rows"], ascending=False)

    selected_copy = selected.copy()
    selected_copy["is_non_l7"] = (selected_copy["decision"].map(classify_decision) == "non_l7_numeric_clue") & (selected_copy["label_family"] != "L7_ranked_future_return")
    selected_copy["is_l7"] = selected_copy["label_family"] == "L7_ranked_future_return"
    selected_distribution = selected_copy.groupby(["semantic_pair", "label_family", "motif"], dropna=False).agg(
        rows=("blueprint_id", "size"),
        unique_blueprints=("blueprint_id", "nunique"),
        median_score_no_may=("score_no_may", "median"),
        median_control_ratio=("control_ratio_premay_max", "median"),
        median_cost10=("cost10_recent_oriented", "median"),
        non_l7_rows=("is_non_l7", "sum"),
    ).reset_index().sort_values("rows", ascending=False)

    l7_pressure = selected_copy.groupby("semantic_pair", dropna=False).agg(
        selected_rows=("blueprint_id", "size"),
        l7_rows=("is_l7", "sum"),
        non_l7_rows=("is_non_l7", "sum"),
        median_score_no_may=("score_no_may", "median"),
    ).reset_index()
    l7_pressure["l7_share"] = l7_pressure["l7_rows"] / l7_pressure["selected_rows"].replace(0, pd.NA)
    l7_pressure = l7_pressure.sort_values(["l7_share", "selected_rows"], ascending=False)

    for name, out in [
        ("core60d_pool_vs_selected_by_semantic_motif.csv", pool_vs_selected),
        ("core60d_selected_distribution.csv", selected_distribution),
        ("core60d_l7_pressure_by_semantic_pair.csv", l7_pressure),
        ("core60d_selected_queue_full.csv", selected_copy),
    ]:
        out.to_csv(RUNTIME_D / name, index=False)

    selected_rows = int(len(selected_copy))
    selected_non_l7 = int(selected_copy["is_non_l7"].sum()) if selected_rows else 0
    selected_l7_share = float(selected_copy["is_l7"].mean()) if selected_rows else 0.0
    selected_semantic_count = int(selected_copy["semantic_pair"].nunique()) if selected_rows else 0
    top_selected_share = float(selected_copy["semantic_pair"].value_counts(normalize=True).iloc[0]) if selected_rows else 0.0

    blockers: list[str] = []
    if selected_non_l7 < 12:
        blockers.append("selected_non_l7_lt_12")
    if selected_l7_share > 0.65:
        blockers.append("selected_l7_share_gt_0_65")
    if selected_semantic_count < 4:
        blockers.append("selected_semantic_count_lt_4")

    if "selected_l7_share_gt_0_65" in blockers:
        decision = "HOLD_CORE60D_SELECTOR_STILL_RANK_BIASED"
    elif blockers:
        decision = "HOLD_CORE60D_SELECTOR_PORTFOLIO_PROXY_NARROW"
    else:
        decision = "PASS_CORE60D_SELECTOR_ATTRIBUTION_ACCEPTABLE"

    record = {
        "stage": "A7FF-CORE60D",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "selected_rows": selected_rows,
        "selected_non_l7_rows": selected_non_l7,
        "selected_l7_share": selected_l7_share,
        "selected_semantic_pair_count": selected_semantic_count,
        "top_selected_semantic_share": top_selected_share,
        "executes_search": False,
        "executes_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
    }
    write_json(RUNTIME_D / "core60d_decision_record.json", record)
    REPORT_D.write_text("\n".join([
        "# CRYPTO A7FF-CORE60D SELECTOR / PORTFOLIO PROXY ATTRIBUTION",
        "",
        f"Generated: {record['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE60D audits selected queue attribution from CORE59. It does not search, replay, or promote candidates.",
        "",
        "## Decision Record",
        "",
        "```json",
        json.dumps(record, indent=2, sort_keys=True),
        "```",
        "",
        "## Selected Distribution",
        "",
        md_table(selected_distribution, 40),
        "",
        "## L7 Pressure By Semantic Pair",
        "",
        md_table(l7_pressure, 30),
        "",
        "## Pool vs Selected By Semantic / Motif",
        "",
        md_table(pool_vs_selected, 40),
        "",
    ]), encoding="utf-8")
    return record


def main() -> None:
    queue = collect("queue")
    material = collect("materialization_metrics")
    label = collect("label_response_metrics")
    selected = collect("selected_portfolio_queue")
    if queue.empty:
        queue = read_csv(CORE59 / "a7ffcore59_numeric_repair_queue.csv")
    if label.empty or material.empty:
        raise SystemExit("CORE59 detailed external artifacts are missing")

    records = {
        "CORE60B": build_target_audit(label),
        "CORE60C": build_materialization_audit(queue, material),
        "CORE60D": build_selector_audit(label, selected),
    }
    print(json.dumps(records, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
