from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff26_numeric_clue_forensic"
REPORT = REPO / "reports" / "CRYPTO_A7FF26_NUMERIC_CLUE_FORENSIC_20260530.md"
A7FF25R3 = REPO / "runtime" / "a7ff25r3_full_numeric_wave"

CONTROL_PROMOTE_MAX = 0.80
ROBUST_MIN_TSTAT_MIN = 1.50
MIN_COST10_ORIENTED = 0.0
MIN_LAG_RECENT = 0.0


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    try:
        return view.to_markdown(index=False)
    except ImportError:
        return "```text\n" + view.to_string(index=False) + "\n```"


def bool_col(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series
    return series.astype(str).str.lower().isin(["true", "1", "yes"])


def triage_row(row: pd.Series) -> str:
    label = str(row.get("label_family", ""))
    if label == "L7_ranked_future_return":
        return "rank_label_diagnostic_only"
    if float(row.get("control_ratio_premay_max", 999.0)) >= 1.0:
        return "control_dominated_block"
    if float(row.get("control_ratio_premay_max", 999.0)) >= CONTROL_PROMOTE_MAX:
        return "watchlist_control_margin_thin"
    if float(row.get("robust_min_tstat_floor", -999.0)) < ROBUST_MIN_TSTAT_MIN:
        return "watchlist_robustness_thin"
    if float(row.get("cost10_recent_oriented", -999.0)) <= MIN_COST10_ORIENTED:
        return "watchlist_cost10_fragile"
    if float(row.get("one_bar_lag_recent_oriented", -999.0)) <= MIN_LAG_RECENT:
        return "watchlist_lag_fragile"
    if not bool(row.get("premay_all_positive", False)):
        return "watchlist_split_incomplete"
    return "promotion_ready_numeric_research_clue"


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    prior = read_json(A7FF25R3 / "a7ff25r3_manifest.json")
    selected = read_csv(A7FF25R3 / "a7ff25r3_selected_portfolio_queue_merged.csv")
    if selected.empty:
        raise SystemExit("missing A7FF-25R3 selected queue")

    selected = selected.copy()
    if "premay_all_positive" in selected.columns:
        selected["premay_all_positive"] = bool_col(selected["premay_all_positive"])
    selected["triage_status"] = selected.apply(triage_row, axis=1)
    selected["is_non_l7"] = selected["label_family"].ne("L7_ranked_future_return")
    selected["promotion_ready"] = selected["triage_status"].eq("promotion_ready_numeric_research_clue")

    triage_cols = [
        "shard",
        "blueprint_id",
        "expression",
        "semantic_pair",
        "motif",
        "skeleton_key",
        "label_family",
        "label_horizon_h",
        "decision",
        "triage_status",
        "control_ratio_premay_max",
        "one_bar_lag_recent_oriented",
        "robust_min_tstat_floor",
        "cost10_recent_oriented",
        "score_no_may",
        "finite_share",
        "nonzero_share",
    ]
    selected[triage_cols].to_csv(RUNTIME / "a7ff26_selected_candidate_triage.csv", index=False)

    promotion = selected[selected["promotion_ready"]].sort_values("score_no_may", ascending=False)
    promotion[triage_cols].to_csv(RUNTIME / "a7ff26_promotion_candidate_queue.csv", index=False)

    rank_diag = selected[selected["triage_status"].eq("rank_label_diagnostic_only")].sort_values("score_no_may", ascending=False)
    rank_diag[triage_cols].to_csv(RUNTIME / "a7ff26_rank_label_diagnostic_queue.csv", index=False)

    watch = selected[selected["triage_status"].str.startswith("watchlist_")].sort_values("score_no_may", ascending=False)
    watch[triage_cols].to_csv(RUNTIME / "a7ff26_watchlist_queue.csv", index=False)

    family_label = (
        selected.groupby(["triage_status", "semantic_pair", "motif", "label_family"], dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values(["triage_status", "count"], ascending=[True, False])
    )
    family_label.to_csv(RUNTIME / "a7ff26_family_label_summary.csv", index=False)

    control_summary = (
        selected.groupby(["triage_status"], dropna=False)
        .agg(
            rows=("blueprint_id", "count"),
            control_ratio_median=("control_ratio_premay_max", "median"),
            control_ratio_max=("control_ratio_premay_max", "max"),
            robust_min_tstat_median=("robust_min_tstat_floor", "median"),
            cost10_median=("cost10_recent_oriented", "median"),
            score_median=("score_no_may", "median"),
        )
        .reset_index()
        .sort_values("rows", ascending=False)
    )
    control_summary.to_csv(RUNTIME / "a7ff26_control_risk_summary.csv", index=False)

    label_summary = (
        selected.groupby(["label_family", "triage_status"], dropna=False).size().reset_index(name="count").sort_values(["label_family", "count"], ascending=[True, False])
    )
    label_summary.to_csv(RUNTIME / "a7ff26_label_triage_summary.csv", index=False)

    promotion_family_count = int(promotion["semantic_pair"].nunique()) if not promotion.empty else 0
    promotion_skeleton_count = int(promotion["skeleton_key"].nunique()) if not promotion.empty and "skeleton_key" in promotion.columns else 0
    promotion_count = int(len(promotion))
    selected_count = int(len(selected))
    l7_count = int((selected["label_family"] == "L7_ranked_future_return").sum())
    non_l7_count = selected_count - l7_count
    warnings: list[str] = []
    if l7_count > non_l7_count:
        warnings.append("rank_label_diagnostic_selected_majority")
    if promotion_family_count < 3:
        warnings.append("promotion_family_breadth_thin")
    if promotion_skeleton_count < 4:
        warnings.append("promotion_skeleton_breadth_thin")

    if promotion_count >= 8 and promotion_family_count >= 3:
        decision = "PASS_A7FF26_NUMERIC_RESEARCH_CLUES_READY_FOR_REPLAY_PREFLIGHT_NO_SEARCH_AUTH"
    elif promotion_count > 0:
        decision = "PASS_A7FF26_NUMERIC_RESEARCH_CLUES_FOUND_WITH_BREADTH_WARNINGS_NO_SEARCH_AUTH"
    else:
        decision = "HOLD_A7FF26_NO_PROMOTION_READY_NUMERIC_CLUES"

    manifest = {
        "stage": "A7FF-26",
        "generated_at": now_utc(),
        "decision": decision,
        "warnings": warnings,
        "prior_stage": prior.get("stage", "A7FF-25R3"),
        "prior_decision": prior.get("decision", ""),
        "selected_input_count": selected_count,
        "non_l7_selected_count": non_l7_count,
        "rank_label_diagnostic_count": l7_count,
        "promotion_ready_count": promotion_count,
        "promotion_semantic_pair_count": promotion_family_count,
        "promotion_skeleton_count": promotion_skeleton_count,
        "promotion_thresholds": {
            "control_ratio_premay_max_lt": CONTROL_PROMOTE_MAX,
            "robust_min_tstat_floor_gte": ROBUST_MIN_TSTAT_MIN,
            "cost10_recent_oriented_gt": MIN_COST10_ORIENTED,
            "one_bar_lag_recent_oriented_gt": MIN_LAG_RECENT,
            "premay_all_positive": True,
            "label_family_not": "L7_ranked_future_return",
        },
        "executes_generation": False,
        "executes_numeric_probe": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_replay_preflight": decision.startswith("PASS_") and promotion_count > 0,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff26_manifest.json", manifest)
    write_json(RUNTIME / "a7ff26_decision_record.json", manifest)

    lines = [
        "# CRYPTO A7FF-26 NUMERIC CLUE FORENSIC",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-26 triages the A7FF-25R3 selected numeric queue. It does not generate, replay, search, or prove alpha. It may authorize a replay-preflight stage for promotion-ready numeric research clues.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Promotion Candidate Queue",
        "",
        md_table(promotion[triage_cols], 40),
        "",
        "## Control Risk Summary",
        "",
        md_table(control_summary, 40),
        "",
        "## Label Triage Summary",
        "",
        md_table(label_summary, 40),
        "",
        "## Family Label Summary",
        "",
        md_table(family_label, 80),
        "",
        "## Boundary",
        "",
        "```text",
        "No May/post-selection stress is used in scoring or authorization.",
        "L7 ranked-return rows are diagnostic-only.",
        "This stage authorizes at most A7FF-27 replay preflight on promotion-ready numeric research clues.",
        "No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
