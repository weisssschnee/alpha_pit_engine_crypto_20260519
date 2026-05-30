from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff27_replay_preflight"
REPORT = REPO / "reports" / "CRYPTO_A7FF27_REPLAY_PREFLIGHT_SUMMARY_20260530.md"
A7FF26 = REPO / "runtime" / "a7ff26_numeric_clue_forensic"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


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


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    probe_manifest = read_json(RUNTIME / "a7ff27_manifest.json")
    prior_manifest = read_json(A7FF26 / "a7ff26_manifest.json")
    responses = read_csv(RUNTIME / "a7ff27_label_response_metrics.csv")
    selected = read_csv(RUNTIME / "a7ff27_selected_portfolio_queue.csv")
    materialized = read_csv(RUNTIME / "a7ff27_materialization_metrics.csv")
    control_summary = read_csv(RUNTIME / "a7ff27_control_summary.csv")
    promotion = read_csv(A7FF26 / "a7ff26_promotion_candidate_queue.csv")

    if responses.empty or materialized.empty:
        raise SystemExit("missing A7FF-27 numeric outputs")

    responses = responses.copy()
    responses["is_numeric_clue"] = responses["decision"].astype(str).eq("A7FF27_NUMERIC_CLUE")
    responses["is_rank_diag"] = responses["decision"].astype(str).eq("A7FF27_RANK_LABEL_DIAGNOSTIC_CLUE")
    responses["is_non_l7"] = responses["label_family"].ne("L7_ranked_future_return")

    clue_summary = (
        responses.groupby(["blueprint_id", "semantic_pair", "motif"], dropna=False)
        .agg(
            response_rows=("decision", "count"),
            non_l7_numeric_clue_rows=("is_numeric_clue", "sum"),
            rank_label_diag_rows=("is_rank_diag", "sum"),
            label_family_count=("label_family", "nunique"),
            horizon_count=("label_horizon_h", "nunique"),
            control_ratio_min=("control_ratio_premay_max", "min"),
            control_ratio_median=("control_ratio_premay_max", "median"),
            robust_min_tstat_max=("robust_min_tstat_floor", "max"),
            cost10_recent_max=("cost10_recent_oriented", "max"),
        )
        .reset_index()
    )
    if not promotion.empty:
        clue_summary = clue_summary.merge(
            promotion[["blueprint_id", "score_no_may", "skeleton_key"]].drop_duplicates("blueprint_id"),
            on="blueprint_id",
            how="left",
        )
    else:
        clue_summary["score_no_may"] = pd.NA
        clue_summary["skeleton_key"] = pd.NA

    selected_ids = set(selected["blueprint_id"].astype(str)) if not selected.empty else set()
    clue_summary["selected_for_a7ff28_preflight"] = clue_summary["blueprint_id"].astype(str).isin(selected_ids)
    clue_summary = clue_summary.sort_values(["selected_for_a7ff28_preflight", "non_l7_numeric_clue_rows", "score_no_may"], ascending=[False, False, False])
    clue_summary.to_csv(RUNTIME / "a7ff27_candidate_replay_preflight_summary.csv", index=False)

    selected_out = selected.copy()
    if not selected_out.empty:
        selected_out = selected_out.sort_values("score_no_may", ascending=False)
    selected_out.to_csv(RUNTIME / "a7ff27_a7ff28_preflight_queue.csv", index=False)

    label_decision = (
        responses.groupby(["label_family", "decision"], dropna=False).size().reset_index(name="count").sort_values(["label_family", "count"], ascending=[True, False])
    )
    label_decision.to_csv(RUNTIME / "a7ff27_label_decision_summary.csv", index=False)

    family_selected = (
        selected_out.groupby(["semantic_pair", "motif"], dropna=False).size().reset_index(name="selected_count").sort_values("selected_count", ascending=False)
        if not selected_out.empty
        else pd.DataFrame(columns=["semantic_pair", "motif", "selected_count"])
    )
    family_selected.to_csv(RUNTIME / "a7ff27_selected_family_summary.csv", index=False)

    input_count = int(probe_manifest.get("input_blueprint_count", len(materialized)) or 0)
    activity_count = int(probe_manifest.get("materialized_activity_ok_count", int(materialized["activity_ok"].sum())) or 0)
    non_l7_clues = int(probe_manifest.get("non_l7_numeric_clue_rows", int(responses["is_numeric_clue"].sum())) or 0)
    selected_count = int(probe_manifest.get("selected_portfolio_queue_count", len(selected_out)) or 0)
    selected_semantic_count = int(selected_out["semantic_pair"].nunique()) if not selected_out.empty else 0
    selected_skeleton_count = int(selected_out["skeleton_key"].nunique()) if not selected_out.empty and "skeleton_key" in selected_out.columns else 0
    warnings: list[str] = []
    if int(probe_manifest.get("rank_label_diagnostic_clue_rows", 0) or 0) > non_l7_clues:
        warnings.append("rank_label_diagnostics_exceed_non_l7_clues")
    if selected_semantic_count < 3:
        warnings.append("selected_semantic_breadth_thin")
    if selected_skeleton_count < 4:
        warnings.append("selected_skeleton_breadth_thin")

    if activity_count == input_count and non_l7_clues >= 8 and selected_count >= 4:
        decision = "PASS_A7FF27_REPLAY_PREFLIGHT_READY_FOR_A7FF28_DEEP_REPLAY_CONTRACT_NO_SEARCH_AUTH"
    elif non_l7_clues > 0:
        decision = "PASS_A7FF27_REPLAY_PREFLIGHT_CLUES_FOUND_WITH_WARNINGS_NO_SEARCH_AUTH"
    else:
        decision = "HOLD_A7FF27_NO_REPLAY_PREFLIGHT_CLUES"

    manifest = {
        "stage": "A7FF-27",
        "generated_at": now_utc(),
        "decision": decision,
        "warnings": warnings,
        "prior_stage": prior_manifest.get("stage", "A7FF-26"),
        "prior_decision": prior_manifest.get("decision", ""),
        "input_candidate_count": input_count,
        "materialized_activity_ok_count": activity_count,
        "label_response_rows": int(len(responses)),
        "non_l7_numeric_clue_rows": non_l7_clues,
        "selected_preflight_count": selected_count,
        "selected_semantic_pair_count": selected_semantic_count,
        "selected_skeleton_count": selected_skeleton_count,
        "executes_generation": False,
        "executes_numeric_probe": True,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_a7ff28_deep_replay_contract": decision.startswith("PASS_") and selected_count >= 4,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff27_summary_manifest.json", manifest)
    write_json(RUNTIME / "a7ff27_summary_decision_record.json", manifest)

    lines = [
        "# CRYPTO A7FF-27 REPLAY PREFLIGHT SUMMARY",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-27 reruns the A7FF-26 promotion-ready numeric research clues through the numeric replay preflight evaluator. It is a preflight step only; it does not run search, alpha proof, shadow, paper, or live execution.",
        "",
        "## Experiment Record",
        "",
        "```text",
        "experiment_id: 20260530_a7ff27_replay_preflight",
        "objective: verify whether A7FF-26 promotion-ready numeric clues survive a fresh evaluator run",
        "input: runtime/a7ff26_numeric_clue_forensic/a7ff26_promotion_candidate_queue.csv",
        "parameters: 14 candidates, labels L0/L1/L3/L5/L7, horizons 1/4/8/24h, controls from A7FF numeric probe",
        "command: A7FF8_STAGE=A7FF-27 ... py scripts/crypto_a7ff8_expanded_numeric_probe.py",
        "decision: no search authorization",
        "```",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## A7FF-28 Preflight Queue",
        "",
        md_table(selected_out[["blueprint_id", "expression", "semantic_pair", "motif", "label_family", "label_horizon_h", "score_no_may"]] if not selected_out.empty else selected_out, 40),
        "",
        "## Candidate Summary",
        "",
        md_table(clue_summary, 40),
        "",
        "## Label Decision Summary",
        "",
        md_table(label_decision, 80),
        "",
        "## Selected Family Summary",
        "",
        md_table(family_selected, 40),
        "",
        "## Control Summary",
        "",
        md_table(control_summary, 40),
        "",
        "## Boundary",
        "",
        "```text",
        "No May/post-selection stress is used in scoring or authorization.",
        "L7 ranked-return rows remain diagnostic-only.",
        "A7FF-27 authorizes at most drafting/executing A7FF-28 deep replay contract/preflight for the selected queue.",
        "No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
