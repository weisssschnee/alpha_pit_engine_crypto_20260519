from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff11_selected_queue_triage"
REPORT = REPO / "reports" / "CRYPTO_A7FF11_SELECTED_QUEUE_TRIAGE_20260530.md"

A7FF10_AGG = REPO / "runtime" / "a7ff10_company_parallel_aggregate"
SELECTED_QUEUE = A7FF10_AGG / "a7ff10_selected_portfolio_queue_all_shards.csv"
SHARD_SUMMARY = A7FF10_AGG / "a7ff10_shard_summary.csv"
AGG_MANIFEST = A7FF10_AGG / "a7ff10_manifest.json"


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
    view = df.head(max_rows).copy()
    for col in view.select_dtypes(include=["object"]).columns:
        view[col] = view[col].astype(str).str.replace("|", r"\|", regex=False)
    try:
        return view.to_markdown(index=False)
    except ImportError:
        return "```text\n" + view.to_string(index=False) + "\n```"


def bool_series(s: pd.Series) -> pd.Series:
    if s.dtype == bool:
        return s.fillna(False)
    return s.astype(str).str.lower().isin(["true", "1", "yes"])


def concentration(df: pd.DataFrame, col: str) -> pd.DataFrame:
    if df.empty or col not in df.columns:
        return pd.DataFrame(columns=[col, "count", "share"])
    out = df[col].fillna("<missing>").value_counts().reset_index()
    out.columns = [col, "count"]
    out["share"] = out["count"] / len(df)
    return out


def role_bucket(row: pd.Series) -> str:
    if row["label_family"] == "L7_ranked_future_return":
        return "rank_label_diagnostic_only"
    if row["control_ratio_premay_max"] >= 1.0:
        return "reject_control_dominated"
    if not row["lag_ok"] or not row["robust_ok"]:
        return "reject_latency_or_robustness_fragile"
    if row["cost10_recent_oriented"] <= 0 or row["robust_min_tstat_floor"] <= 0:
        return "watchlist_cost_or_overlap_weak"
    if row["control_ratio_premay_max"] < 0.8:
        return "priority_non_l7_control_clean"
    return "watchlist_control_margin_weak"


def next_action(row: pd.Series) -> str:
    bucket = row["triage_bucket"]
    if bucket == "priority_non_l7_control_clean":
        return "eligible_for_a7ff12_numeric_followup_not_search"
    if bucket.startswith("watchlist"):
        return "keep_for_attribution_or_broader_wave_only"
    if bucket == "rank_label_diagnostic_only":
        return "diagnostic_only_do_not_promote"
    return "reject_from_followup_queue"


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    manifest10 = read_json(AGG_MANIFEST)
    if not SELECTED_QUEUE.exists():
        raise SystemExit(f"missing selected queue: {SELECTED_QUEUE}")
    selected = pd.read_csv(SELECTED_QUEUE)
    shards = pd.read_csv(SHARD_SUMMARY) if SHARD_SUMMARY.exists() else pd.DataFrame()

    selected["lag_ok"] = bool_series(selected["lag_ok"])
    selected["robust_ok"] = bool_series(selected["robust_ok"])
    selected["premay_all_positive"] = bool_series(selected["premay_all_positive"])
    selected["triage_bucket"] = selected.apply(role_bucket, axis=1)
    selected["next_action"] = selected.apply(next_action, axis=1)
    selected["is_non_l7"] = selected["label_family"] != "L7_ranked_future_return"
    selected["is_priority_followup"] = selected["triage_bucket"].eq("priority_non_l7_control_clean")

    # This queue is already one row per blueprint in A7FF-10, but keep an explicit ledger.
    candidate_cols = [
        "shard",
        "blueprint_id",
        "expression",
        "semantic_pair",
        "motif",
        "label_family",
        "label_horizon_h",
        "triage_bucket",
        "next_action",
        "orientation_from_train",
        "premay_positive_split_count",
        "control_ratio_premay_max",
        "one_bar_lag_recent_oriented",
        "robust_min_tstat_floor",
        "cost10_recent_oriented",
        "score_no_may",
        "skeleton_key",
        "finite_share",
        "nonzero_share",
        "is_priority_followup",
    ]
    candidate_triage = selected[candidate_cols].sort_values(
        ["is_priority_followup", "score_no_may"], ascending=[False, False]
    )

    bucket_summary = (
        selected.groupby("triage_bucket", dropna=False)
        .agg(
            count=("blueprint_id", "count"),
            median_control_ratio=("control_ratio_premay_max", "median"),
            median_cost10=("cost10_recent_oriented", "median"),
            median_score_no_may=("score_no_may", "median"),
        )
        .reset_index()
        .sort_values("count", ascending=False)
    )
    label_summary = (
        selected.groupby(["label_family", "label_horizon_h"], dropna=False)
        .agg(
            count=("blueprint_id", "count"),
            priority_count=("is_priority_followup", "sum"),
            median_control_ratio=("control_ratio_premay_max", "median"),
            median_cost10=("cost10_recent_oriented", "median"),
        )
        .reset_index()
        .sort_values(["priority_count", "count"], ascending=False)
    )
    semantic_summary = (
        selected.groupby(["semantic_pair", "motif"], dropna=False)
        .agg(
            count=("blueprint_id", "count"),
            priority_count=("is_priority_followup", "sum"),
            median_control_ratio=("control_ratio_premay_max", "median"),
            median_score_no_may=("score_no_may", "median"),
        )
        .reset_index()
        .sort_values(["priority_count", "count"], ascending=False)
    )
    skeleton_summary = concentration(selected, "skeleton_key")
    production_proxy_summary = concentration(selected, "semantic_pair")

    followup_queue = candidate_triage[candidate_triage["triage_bucket"].eq("priority_non_l7_control_clean")].copy()
    watchlist_queue = candidate_triage[candidate_triage["triage_bucket"].str.startswith("watchlist")].copy()

    selected_count = int(len(selected))
    priority_count = int(len(followup_queue))
    non_l7_count = int(selected["is_non_l7"].sum())
    rank_only_count = int(selected["label_family"].eq("L7_ranked_future_return").sum())
    top_semantic_share = float(production_proxy_summary["share"].max()) if not production_proxy_summary.empty else 0.0
    top_skeleton_share = float(skeleton_summary["share"].max()) if not skeleton_summary.empty else 0.0
    priority_label_families = int(followup_queue["label_family"].nunique()) if not followup_queue.empty else 0
    priority_semantic_pairs = int(followup_queue["semantic_pair"].nunique()) if not followup_queue.empty else 0

    label_concentration_warning = priority_label_families < 2 or (
        not followup_queue.empty and followup_queue["label_family"].value_counts(normalize=True).max() > 0.8
    )
    semantic_concentration_warning = top_semantic_share > 0.35
    decision = (
        "PASS_A7FF11_TRIAGE_READY_FOR_A7FF12_NUMERIC_WAVE_WITH_LABEL_DIVERSITY_WARNING"
        if priority_count >= 8 and label_concentration_warning
        else "PASS_A7FF11_TRIAGE_READY_FOR_A7FF12_NUMERIC_WAVE"
        if priority_count >= 8
        else "HOLD_A7FF11_INSUFFICIENT_PRIORITY_FOLLOWUP_QUEUE"
    )

    manifest = {
        "stage": "A7FF-11-SELECTED-QUEUE-TRIAGE",
        "generated_at": now_utc(),
        "decision": decision,
        "source_stage": manifest10.get("stage", "A7FF-10-COMPANY-PARALLEL-AGGREGATE"),
        "source_decision": manifest10.get("decision", ""),
        "input_selected_rows": selected_count,
        "unique_blueprints": int(selected["blueprint_id"].nunique()),
        "non_l7_selected_rows": non_l7_count,
        "rank_label_diagnostic_rows": rank_only_count,
        "priority_followup_count": priority_count,
        "watchlist_count": int(len(watchlist_queue)),
        "priority_label_families": priority_label_families,
        "priority_semantic_pairs": priority_semantic_pairs,
        "top_semantic_pair_share": top_semantic_share,
        "top_skeleton_share": top_skeleton_share,
        "warnings": [
            w
            for w, active in [
                ("priority_queue_label_concentrated", bool(label_concentration_warning)),
                ("selected_queue_semantic_pair_at_or_above_35pct", bool(semantic_concentration_warning)),
            ]
            if active
        ],
        "executes_generation": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_a7ff12_numeric_wave_contract": priority_count >= 8,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }

    candidate_triage.to_csv(RUNTIME / "a7ff11_candidate_triage.csv", index=False)
    bucket_summary.to_csv(RUNTIME / "a7ff11_triage_bucket_summary.csv", index=False)
    label_summary.to_csv(RUNTIME / "a7ff11_label_horizon_summary.csv", index=False)
    semantic_summary.to_csv(RUNTIME / "a7ff11_semantic_motif_summary.csv", index=False)
    skeleton_summary.to_csv(RUNTIME / "a7ff11_skeleton_concentration.csv", index=False)
    production_proxy_summary.to_csv(RUNTIME / "a7ff11_semantic_concentration.csv", index=False)
    followup_queue.to_csv(RUNTIME / "a7ff11_priority_followup_queue.csv", index=False)
    watchlist_queue.to_csv(RUNTIME / "a7ff11_watchlist_queue.csv", index=False)
    shards.to_csv(RUNTIME / "a7ff11_source_shard_summary.csv", index=False)
    write_json(RUNTIME / "a7ff11_manifest.json", manifest)

    experiment_record = {
        "date": manifest["generated_at"],
        "experiment_id": "20260530_a7ff11_selected_queue_triage",
        "objective": "Triage A7FF-10 company-machine selected queue before any larger numeric wave.",
        "status": "completed",
        "mode": "research_governance",
        "inputs": {
            "selected_queue": str(SELECTED_QUEUE.relative_to(REPO)),
            "source_manifest": str(AGG_MANIFEST.relative_to(REPO)),
        },
        "parameters": {
            "priority_control_ratio_max": 0.8,
            "requires_non_l7": True,
            "requires_cost10_positive": True,
            "requires_robust_min_tstat_positive": True,
            "requires_lag_ok": True,
            "requires_premay_all_positive": True,
        },
        "outputs": {
            "manifest": str((RUNTIME / "a7ff11_manifest.json").relative_to(REPO)),
            "priority_followup_queue": str((RUNTIME / "a7ff11_priority_followup_queue.csv").relative_to(REPO)),
            "candidate_triage": str((RUNTIME / "a7ff11_candidate_triage.csv").relative_to(REPO)),
        },
        "decision": decision,
        "next_action": "Draft or execute A7FF-12 numeric wave only after preserving non-L7 label diversity and fixing company runner reliability.",
    }
    write_json(RUNTIME / "a7ff11_experiment_record.json", experiment_record)

    lines = [
        "# CRYPTO A7FF-11 SELECTED QUEUE TRIAGE",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-11 triages the 40 selected A7FF-10 numeric-probe rows. It does not generate formulas, execute replay, run search, or authorize alpha proof.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Triage Buckets",
        "",
        md_table(bucket_summary),
        "",
        "## Label / Horizon",
        "",
        md_table(label_summary, 80),
        "",
        "## Semantic / Motif",
        "",
        md_table(semantic_summary, 80),
        "",
        "## Priority Follow-Up Queue",
        "",
        md_table(followup_queue, 60),
        "",
        "## Operational Interpretation",
        "",
        "```text",
        "The A7FF-10 selected queue has enough non-L7, control-clean numeric clues to justify a larger numeric wave.",
        "However, the priority queue is concentrated in L5_vol_adjusted_return and basis/premium-related semantic pairs.",
        "A7FF-12 must expand numeric probing with explicit label-family and semantic-pair diversity; this still is not formula search.",
        "```",
        "",
        "## Boundary",
        "",
        "```text",
        "May is not used.",
        "No formula generation, replay execution, search execution, alpha proof, shadow, paper, or live execution is authorized.",
        "A7FF-11 only authorizes drafting/running a broader numeric wave under the same non-search boundary.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
