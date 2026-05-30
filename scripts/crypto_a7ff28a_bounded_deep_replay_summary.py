from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff28a_bounded_deep_replay"
REPORT = REPO / "reports" / "CRYPTO_A7FF28A_BOUNDED_DEEP_REPLAY_SUMMARY_20260530.md"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


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


def main() -> None:
    manifest = read_json(RUNTIME / "a7ff28a_manifest.json")
    responses = read_csv(RUNTIME / "a7ff28a_label_response_metrics.csv")
    selected = read_csv(RUNTIME / "a7ff28a_selected_portfolio_queue.csv")
    materialization = read_csv(RUNTIME / "a7ff28a_materialization_metrics.csv")
    decision_counts = read_csv(RUNTIME / "a7ff28a_decision_counts.csv")

    non_l7 = responses[
        responses["decision"].eq("A7FF28A_NUMERIC_CLUE")
        & responses["label_family"].ne("L7_ranked_future_return")
    ].copy()
    portfolio_scores = selected[
        ["blueprint_id", "score_no_may", "skeleton_key", "finite_share", "nonzero_share"]
    ].drop_duplicates("blueprint_id") if not selected.empty else pd.DataFrame()
    if not non_l7.empty and not portfolio_scores.empty:
        non_l7 = non_l7.merge(portfolio_scores, on="blueprint_id", how="left", suffixes=("", "_portfolio"))
    if not non_l7.empty:
        non_l7 = non_l7.sort_values(
            ["score_no_may", "control_ratio_premay_max", "label_family"],
            ascending=[False, True, True],
        )
    a7ff29_queue = non_l7.drop_duplicates("blueprint_id").copy()
    a7ff29_queue.insert(0, "a7ff29_queue_rank", range(1, len(a7ff29_queue) + 1))
    a7ff29_queue.to_csv(RUNTIME / "a7ff28a_a7ff29_candidate_forensic_queue.csv", index=False)

    selected_l7 = selected[selected["label_family"].eq("L7_ranked_future_return")].copy() if not selected.empty else pd.DataFrame()
    selected_l7.to_csv(RUNTIME / "a7ff28a_rank_label_diagnostic_selected.csv", index=False)

    family_summary = (
        a7ff29_queue.groupby(["semantic_pair", "motif", "label_family"], dropna=False)
        .agg(
            candidate_count=("blueprint_id", "count"),
            median_control_ratio=("control_ratio_premay_max", "median"),
            median_score_no_may=("score_no_may", "median"),
        )
        .reset_index()
        if not a7ff29_queue.empty
        else pd.DataFrame()
    )
    family_summary.to_csv(RUNTIME / "a7ff28a_a7ff29_queue_family_summary.csv", index=False)

    warnings: list[str] = []
    if not selected_l7.empty:
        warnings.append("selected_portfolio_queue_contains_rank_label_diagnostic_rows_excluded_from_a7ff29")
    semantic_pair_count = int(a7ff29_queue["semantic_pair"].nunique()) if not a7ff29_queue.empty else 0
    if semantic_pair_count < 3:
        warnings.append("a7ff29_queue_semantic_pair_count_lt_3")
    max_control = float(a7ff29_queue["control_ratio_premay_max"].max()) if not a7ff29_queue.empty else None
    if max_control is not None and max_control >= 1.0:
        warnings.append("a7ff29_queue_control_ratio_ge_1")

    decision = (
        "PASS_A7FF28A_BOUNDED_DEEP_REPLAY_READY_FOR_A7FF29_FORENSIC_NO_SEARCH_AUTH"
        if len(a7ff29_queue) >= 4 and semantic_pair_count >= 3 and (max_control is None or max_control < 1.0)
        else "HOLD_A7FF28A_A7FF29_QUEUE_TOO_NARROW"
    )
    summary = {
        "stage": "A7FF-28A-SUMMARY",
        "generated_at": now_utc(),
        "decision": decision,
        "prior_decision": manifest.get("decision", ""),
        "input_blueprint_count": manifest.get("input_blueprint_count"),
        "materialized_activity_ok_count": manifest.get("materialized_activity_ok_count"),
        "label_response_rows": manifest.get("label_response_rows"),
        "non_l7_numeric_clue_rows": manifest.get("non_l7_numeric_clue_rows"),
        "rank_label_diagnostic_clue_rows": manifest.get("rank_label_diagnostic_clue_rows"),
        "a7ff29_queue_count": int(len(a7ff29_queue)),
        "a7ff29_semantic_pair_count": semantic_pair_count,
        "a7ff29_max_control_ratio": max_control,
        "selected_rank_label_diagnostic_count": int(len(selected_l7)),
        "warnings": warnings,
        "executes_generation": False,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_a7ff29_candidate_forensic_contract": decision.startswith("PASS"),
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff28a_summary_manifest.json", summary)
    write_json(RUNTIME / "a7ff28a_summary_decision_record.json", summary)

    lines = [
        "# CRYPTO A7FF-28A BOUNDED DEEP REPLAY SUMMARY",
        "",
        f"Generated: {summary['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-28A reran the frozen A7FF-28 queue on 181 strict full-history symbols. This summary strips ranked-label diagnostic rows from the next queue and authorizes only A7FF-29 candidate forensic contract work.",
        "",
        "## Summary",
        "",
        "```json",
        json.dumps(summary, indent=2, sort_keys=True),
        "```",
        "",
        "## A7FF-29 Candidate Forensic Queue",
        "",
        md_table(a7ff29_queue[["a7ff29_queue_rank", "blueprint_id", "expression", "semantic_pair", "motif", "label_family", "label_horizon_h", "control_ratio_premay_max", "score_no_may"]] if not a7ff29_queue.empty else a7ff29_queue, 20),
        "",
        "## Excluded Ranked-Label Diagnostic Selected Rows",
        "",
        md_table(selected_l7[["blueprint_id", "expression", "label_family", "label_horizon_h", "score_no_may"]] if not selected_l7.empty else selected_l7, 20),
        "",
        "## Decision Counts",
        "",
        md_table(decision_counts, 40),
        "",
        "## Materialization",
        "",
        md_table(materialization, 20),
        "",
        "## Family Summary",
        "",
        md_table(family_summary, 20),
        "",
        "## Boundary",
        "",
        "```text",
        "A7FF-28A does not authorize formula generation, large search, alpha proof, shadow, paper, or live execution.",
        "A7FF-29 may only do candidate forensic/deep-audit contract work on the non-L7 queue.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
