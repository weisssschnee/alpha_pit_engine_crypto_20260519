from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff13_wave_triage"
REPORT = REPO / "reports" / "CRYPTO_A7FF13_WAVE_TRIAGE_20260530.md"

A7FF12_AGG = REPO / "runtime" / "a7ff12_company_wave_aggregate"
MANIFEST12 = A7FF12_AGG / "a7ff12_manifest.json"
CLUE_SUMMARY = A7FF12_AGG / "a7ff12_non_l7_clue_summary.csv"
SELECTED_QUEUE = A7FF12_AGG / "a7ff12_selected_portfolio_queue_all_shards.csv"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    safe = df.head(max_rows).copy()
    for col in safe.select_dtypes(include=["object"]).columns:
        safe[col] = safe[col].astype(str).str.replace("|", r"\|", regex=False)
    try:
        return safe.to_markdown(index=False)
    except ImportError:
        return "```text\n" + safe.to_string(index=False) + "\n```"


def bool_series(s: pd.Series) -> pd.Series:
    if s.dtype == bool:
        return s.fillna(False)
    return s.astype(str).str.lower().isin(["true", "1", "yes"])


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    manifest12 = read_json(MANIFEST12)
    clues = pd.read_csv(CLUE_SUMMARY)
    selected = pd.read_csv(SELECTED_QUEUE)
    for col in ["lag_ok", "robust_ok", "premay_all_positive"]:
        selected[col] = bool_series(selected[col])

    selected["is_non_l7"] = selected["label_family"].ne("L7_ranked_future_return")
    selected["is_priority_clean"] = (
        selected["is_non_l7"]
        & selected["premay_all_positive"]
        & selected["lag_ok"]
        & selected["robust_ok"]
        & (selected["control_ratio_premay_max"] < 0.8)
        & (selected["cost10_recent_oriented"] > 0)
        & (selected["robust_min_tstat_floor"] > 0)
    )

    clue_label_summary = (
        clues.groupby(["label_family", "label_horizon_h"], dropna=False)["count"]
        .sum()
        .reset_index(name="clue_count")
        .sort_values("clue_count", ascending=False)
    )
    clue_semantic_summary = (
        clues.groupby("semantic_pair", dropna=False)["count"]
        .sum()
        .reset_index(name="clue_count")
        .sort_values("clue_count", ascending=False)
    )
    selected_label_summary = (
        selected.groupby(["label_family", "label_horizon_h"], dropna=False)
        .agg(
            selected_count=("blueprint_id", "count"),
            priority_clean_count=("is_priority_clean", "sum"),
            median_control_ratio=("control_ratio_premay_max", "median"),
            median_cost10=("cost10_recent_oriented", "median"),
        )
        .reset_index()
        .sort_values(["priority_clean_count", "selected_count"], ascending=False)
    )
    selected_semantic_summary = (
        selected.groupby("semantic_pair", dropna=False)
        .agg(
            selected_count=("blueprint_id", "count"),
            priority_clean_count=("is_priority_clean", "sum"),
            median_control_ratio=("control_ratio_premay_max", "median"),
        )
        .reset_index()
        .sort_values(["priority_clean_count", "selected_count"], ascending=False)
    )
    priority = selected[selected["is_priority_clean"]].copy().sort_values("score_no_may", ascending=False)

    raw_non_l7_label_families = int(clue_label_summary["label_family"].nunique())
    selected_priority_label_families = int(priority["label_family"].nunique()) if not priority.empty else 0
    priority_top_label_share = float(priority["label_family"].value_counts(normalize=True).max()) if not priority.empty else 0.0
    selected_top_label_share = float(selected["label_family"].value_counts(normalize=True).max()) if not selected.empty else 0.0

    decision = (
        "HOLD_A7FF13_SELECTOR_LABEL_CONCENTRATION_AFTER_NUMERIC_SCALEUP"
        if selected_priority_label_families <= 1 and raw_non_l7_label_families >= 4
        else "PASS_A7FF13_WAVE_TRIAGE_READY_FOR_SELECTOR_REPAIR"
    )
    manifest = {
        "stage": "A7FF-13-WAVE-TRIAGE",
        "generated_at": now_utc(),
        "decision": decision,
        "source_stage": manifest12.get("stage", ""),
        "source_decision": manifest12.get("decision", ""),
        "input_blueprints": manifest12.get("total_input_blueprints", 0),
        "raw_non_l7_numeric_clue_rows": manifest12.get("total_non_l7_numeric_clue_rows", 0),
        "raw_rank_label_diagnostic_clue_rows": manifest12.get("total_rank_label_diagnostic_clue_rows", 0),
        "selected_queue_count": int(len(selected)),
        "selected_priority_clean_count": int(priority["is_priority_clean"].sum()) if not priority.empty else 0,
        "raw_non_l7_label_families": raw_non_l7_label_families,
        "selected_priority_label_families": selected_priority_label_families,
        "selected_top_label_share": selected_top_label_share,
        "priority_top_label_share": priority_top_label_share,
        "uses_may": False,
        "authorizes_a7ff14_selector_repair_contract": True,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }

    clue_label_summary.to_csv(RUNTIME / "a7ff13_raw_clue_label_summary.csv", index=False)
    clue_semantic_summary.to_csv(RUNTIME / "a7ff13_raw_clue_semantic_summary.csv", index=False)
    selected_label_summary.to_csv(RUNTIME / "a7ff13_selected_label_summary.csv", index=False)
    selected_semantic_summary.to_csv(RUNTIME / "a7ff13_selected_semantic_summary.csv", index=False)
    priority.to_csv(RUNTIME / "a7ff13_priority_clean_selected_queue.csv", index=False)
    write_json(RUNTIME / "a7ff13_manifest.json", manifest)

    lines = [
        "# CRYPTO A7FF-13 WAVE TRIAGE",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-13 compares the A7FF-12 raw non-L7 clue surface against the selected portfolio queue. It does not run generation, replay, search, alpha proof, shadow, paper, or live execution.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Raw Clue Label Surface",
        "",
        md_table(clue_label_summary, 80),
        "",
        "## Selected Label Surface",
        "",
        md_table(selected_label_summary, 80),
        "",
        "## Selected Semantic Surface",
        "",
        md_table(selected_semantic_summary, 80),
        "",
        "## Interpretation",
        "",
        "```text",
        "A7FF-12 successfully expanded numeric evidence: L0/L1/L3/L5 raw non-L7 clue families are all present.",
        "The selected queue still concentrates the clean follow-up set in L5_vol_adjusted_return.",
        "The next step is selector repair with label-family balancing, not more unconstrained formula generation.",
        "```",
        "",
        "## Boundary",
        "",
        "```text",
        "No May is used.",
        "No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.",
        "A7FF-14 may only be a selector repair / dry rerank contract.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
