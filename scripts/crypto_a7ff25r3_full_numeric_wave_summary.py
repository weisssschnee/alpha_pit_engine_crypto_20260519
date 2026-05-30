from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff25r3_full_numeric_wave"
REPORT = REPO / "reports" / "CRYPTO_A7FF25R3_FULL_COMPANY_NUMERIC_WAVE_20260530.md"


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


def norm_decision(decision: str) -> str:
    text = str(decision)
    text = re.sub(r"A7FF25R3S\d{2}_", "A7FF25R3_", text)
    return text


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    shard_rows: list[dict[str, Any]] = []
    decision_frames: list[pd.DataFrame] = []
    family_frames: list[pd.DataFrame] = []
    control_frames: list[pd.DataFrame] = []
    selected_frames: list[pd.DataFrame] = []
    material_frames: list[pd.DataFrame] = []

    for shard_idx in range(12):
        shard = f"{shard_idx:02d}"
        shard_dir = RUNTIME / f"shard_{shard}"
        manifest = read_json(shard_dir / f"a7ff25r3s{shard}_manifest.json")
        exit_path = shard_dir / f"a7ff25r3s{shard}_exit_code.txt"
        exit_code = exit_path.read_text(encoding="utf-8").strip() if exit_path.exists() else ""
        row = {
            "shard": shard,
            "manifest_exists": bool(manifest),
            "exit_code": exit_code,
            "decision": manifest.get("decision", "MISSING_MANIFEST"),
            "normalized_decision": norm_decision(manifest.get("decision", "MISSING_MANIFEST")),
            "input_blueprint_count": int(manifest.get("input_blueprint_count", 0) or 0),
            "materialized_activity_ok_count": int(manifest.get("materialized_activity_ok_count", 0) or 0),
            "label_response_rows": int(manifest.get("label_response_rows", 0) or 0),
            "non_l7_numeric_clue_rows": int(manifest.get("non_l7_numeric_clue_rows", 0) or 0),
            "rank_label_diagnostic_clue_rows": int(manifest.get("rank_label_diagnostic_clue_rows", 0) or 0),
            "portfolio_queue_count": int(manifest.get("portfolio_queue_count", 0) or 0),
            "selected_portfolio_queue_count": int(manifest.get("selected_portfolio_queue_count", 0) or 0),
            "uses_may": bool(manifest.get("uses_may", False)),
        }
        shard_rows.append(row)

        decision = read_csv(shard_dir / f"a7ff25r3s{shard}_decision_counts.csv")
        if not decision.empty:
            decision["shard"] = shard
            decision["normalized_decision"] = decision["decision"].map(norm_decision)
            decision_frames.append(decision)

        family = read_csv(shard_dir / f"a7ff25r3s{shard}_family_decision_summary.csv")
        if not family.empty:
            family["shard"] = shard
            family["normalized_decision"] = family["decision"].map(norm_decision)
            family_frames.append(family)

        control = read_csv(shard_dir / f"a7ff25r3s{shard}_control_summary.csv")
        if not control.empty:
            control["shard"] = shard
            control_frames.append(control)

        selected = read_csv(shard_dir / f"a7ff25r3s{shard}_selected_portfolio_queue.csv")
        if not selected.empty:
            selected["shard"] = shard
            selected_frames.append(selected)

        material = read_csv(shard_dir / f"a7ff25r3s{shard}_materialization_metrics.csv")
        if not material.empty:
            material["shard"] = shard
            material_frames.append(material)

    shard_df = pd.DataFrame(shard_rows)
    shard_df.to_csv(RUNTIME / "a7ff25r3_shard_summary.csv", index=False)

    decision_merged = (
        pd.concat(decision_frames, ignore_index=True)
        .groupby(["normalized_decision", "label_family"], dropna=False)["count"]
        .sum()
        .reset_index()
        .sort_values(["normalized_decision", "label_family"])
        if decision_frames
        else pd.DataFrame(columns=["normalized_decision", "label_family", "count"])
    )
    decision_merged.to_csv(RUNTIME / "a7ff25r3_decision_counts_merged.csv", index=False)

    family_merged = (
        pd.concat(family_frames, ignore_index=True)
        .groupby(["semantic_pair", "normalized_decision"], dropna=False)["count"]
        .sum()
        .reset_index()
        .sort_values(["semantic_pair", "normalized_decision"])
        if family_frames
        else pd.DataFrame(columns=["semantic_pair", "normalized_decision", "count"])
    )
    family_merged.to_csv(RUNTIME / "a7ff25r3_family_decision_summary_merged.csv", index=False)

    control_merged = (
        pd.concat(control_frames, ignore_index=True)
        .groupby("control", dropna=False)
        .agg(median_ratio=("median_ratio", "median"), max_ratio=("max_ratio", "max"), rows=("rows", "sum"))
        .reset_index()
        .sort_values("control")
        if control_frames
        else pd.DataFrame(columns=["control", "median_ratio", "max_ratio", "rows"])
    )
    control_merged.to_csv(RUNTIME / "a7ff25r3_control_summary_merged.csv", index=False)

    selected_merged = pd.concat(selected_frames, ignore_index=True) if selected_frames else pd.DataFrame()
    selected_merged.to_csv(RUNTIME / "a7ff25r3_selected_portfolio_queue_merged.csv", index=False)

    material_merged = pd.concat(material_frames, ignore_index=True) if material_frames else pd.DataFrame()
    material_dropoff = (
        material_merged.groupby("shard", dropna=False)
        .agg(
            rows=("blueprint_id", "count"),
            eval_success=("eval_success", "sum"),
            activity_ok=("activity_ok", "sum"),
            finite_share_median=("finite_share", "median"),
            nonzero_share_median=("nonzero_share", "median"),
        )
        .reset_index()
        if not material_merged.empty
        else pd.DataFrame(columns=["shard", "rows", "eval_success", "activity_ok", "finite_share_median", "nonzero_share_median"])
    )
    material_dropoff.to_csv(RUNTIME / "a7ff25r3_materialization_dropoff_audit.csv", index=False)

    selected_family = (
        selected_merged.groupby(["semantic_pair", "motif"], dropna=False)
        .size()
        .reset_index(name="selected_count")
        .sort_values("selected_count", ascending=False)
        if not selected_merged.empty and {"semantic_pair", "motif"}.issubset(selected_merged.columns)
        else pd.DataFrame(columns=["semantic_pair", "motif", "selected_count"])
    )
    selected_family.to_csv(RUNTIME / "a7ff25r3_selected_family_summary.csv", index=False)

    total_input = int(shard_df["input_blueprint_count"].sum())
    total_activity = int(shard_df["materialized_activity_ok_count"].sum())
    total_non_l7 = int(shard_df["non_l7_numeric_clue_rows"].sum())
    total_rank = int(shard_df["rank_label_diagnostic_clue_rows"].sum())
    total_selected = int(shard_df["selected_portfolio_queue_count"].sum())
    completed_shards = int((shard_df["manifest_exists"] & shard_df["exit_code"].eq("0")).sum())
    no_activity_shards = shard_df[shard_df["materialized_activity_ok_count"].eq(0)]["shard"].tolist()
    top_selected_share = (
        float(selected_family["selected_count"].max() / selected_family["selected_count"].sum())
        if not selected_family.empty and selected_family["selected_count"].sum() > 0
        else 0.0
    )
    top_semantic = str(selected_family.iloc[0]["semantic_pair"]) if not selected_family.empty else ""

    warnings: list[str] = []
    if no_activity_shards:
        warnings.append("no_activity_shards_present")
    if top_selected_share > 0.35:
        warnings.append("selected_queue_family_concentration")
    if total_rank > total_non_l7:
        warnings.append("rank_label_diagnostic_rows_exceed_non_l7")

    if completed_shards < 12:
        decision = "HOLD_A7FF25R3_INCOMPLETE_SHARDS"
    elif total_non_l7 <= 0 or total_selected <= 0:
        decision = "HOLD_A7FF25R3_NO_USABLE_NUMERIC_CLUES"
    elif warnings:
        decision = "PASS_A7FF25R3_FULL_NUMERIC_WAVE_COMPLETED_WITH_WARNINGS_NO_SEARCH_AUTH"
    else:
        decision = "PASS_A7FF25R3_FULL_NUMERIC_WAVE_COMPLETED_NO_SEARCH_AUTH"

    manifest = {
        "stage": "A7FF-25R3",
        "generated_at": now_utc(),
        "decision": decision,
        "warnings": warnings,
        "completed_shards": completed_shards,
        "shard_count": 12,
        "input_blueprint_count": total_input,
        "materialized_activity_ok_count": total_activity,
        "label_response_rows": int(shard_df["label_response_rows"].sum()),
        "non_l7_numeric_clue_rows": total_non_l7,
        "rank_label_diagnostic_clue_rows": total_rank,
        "portfolio_queue_count": int(shard_df["portfolio_queue_count"].sum()),
        "selected_portfolio_queue_count": total_selected,
        "no_activity_shards": no_activity_shards,
        "selected_top_semantic_pair": top_semantic,
        "selected_top_semantic_pair_share": top_selected_share,
        "executes_generation": False,
        "executes_numeric_probe": True,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff25r3_manifest.json", manifest)
    write_json(RUNTIME / "a7ff25r3_decision_record.json", manifest)

    lines = [
        "# CRYPTO A7FF-25R3 FULL COMPANY NUMERIC WAVE",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-25R3 aggregates the 12 company-machine numeric shards from the A7FF-24R company wave queue. It is numeric response probing only: no generation, replay, search, alpha proof, shadow, paper, or live execution is authorized.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Shard Summary",
        "",
        md_table(shard_df, 40),
        "",
        "## Decision Counts",
        "",
        md_table(decision_merged, 80),
        "",
        "## Selected Family Summary",
        "",
        md_table(selected_family, 80),
        "",
        "## Control Summary",
        "",
        md_table(control_merged, 80),
        "",
        "## Materialization Dropoff",
        "",
        md_table(material_dropoff, 40),
        "",
        "## Boundary",
        "",
        "```text",
        "No May/post-selection stress is used in scoring or authorization.",
        "L7 ranked-return rows are diagnostic-only.",
        "This stage does not authorize A7FF formula search, large search, alpha proof, shadow, paper, or live execution.",
        "No-activity shards must be handled before treating the company queue as uniformly healthy.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
