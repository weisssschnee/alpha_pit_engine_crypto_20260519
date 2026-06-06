from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
DEFAULT_EXTERNAL = Path(
    os.environ.get(
        "A7LS18_EXTERNAL",
        r"D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7ls18_company_numeric_20260606_r2",
    )
)
DEFAULT_REPORT = Path(
    os.environ.get(
        "A7LS18_REPORT",
        r"D:\HermesWorker\GDrive\AlphaFactory_CryptoData\reports\CRYPTO_A7LS18_COMPANY_NUMERIC_AGGREGATE_20260606.md",
    )
)
LOCAL_RUNTIME = REPO / "runtime" / "a7ls18_company_numeric_aggregate"
LOCAL_REPORT = REPO / "reports" / "CRYPTO_A7LS18_COMPANY_NUMERIC_AGGREGATE_20260606.md"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


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
        return "```csv\n" + view.to_csv(index=False) + "```"


def shard_dirs(external: Path) -> list[Path]:
    root = external / "shards"
    if not root.exists():
        return []
    return sorted(path for path in root.glob("a7ls18_s*") if path.is_dir())


def collect_shards(external: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rows: list[dict[str, Any]] = []
    decision_frames: list[pd.DataFrame] = []
    selected_frames: list[pd.DataFrame] = []
    family_frames: list[pd.DataFrame] = []

    for shard_dir in shard_dirs(external):
        shard_id = shard_dir.name
        manifest = read_json(shard_dir / f"{shard_id}_manifest.json")
        queue = read_csv(shard_dir / f"{shard_id}_queue.csv")
        rows.append(
            {
                "shard_id": shard_id,
                "has_manifest": bool(manifest),
                "decision": manifest.get("decision", "NO_MANIFEST"),
                "blockers": ";".join(manifest.get("blockers", [])) if manifest else "no_manifest",
                "input_blueprint_count": int(manifest.get("input_blueprint_count", 0) or 0),
                "materialized_activity_ok_count": int(manifest.get("materialized_activity_ok_count", 0) or 0),
                "label_response_rows": int(manifest.get("label_response_rows", 0) or 0),
                "non_l7_numeric_clue_rows": int(manifest.get("non_l7_numeric_clue_rows", 0) or 0),
                "rank_label_diagnostic_clue_rows": int(manifest.get("rank_label_diagnostic_clue_rows", 0) or 0),
                "selected_portfolio_queue_count": int(manifest.get("selected_portfolio_queue_count", 0) or 0),
                "queue_rows": int(len(queue)),
                "lane_count": int(queue["a7ls_lane"].nunique()) if not queue.empty and "a7ls_lane" in queue.columns else 0,
                "semantic_pair_count": int(queue["semantic_pair"].nunique()) if not queue.empty and "semantic_pair" in queue.columns else 0,
                "motif_count": int(queue["motif"].nunique()) if not queue.empty and "motif" in queue.columns else 0,
                "skeleton_count": int(queue["skeleton_key"].nunique()) if not queue.empty and "skeleton_key" in queue.columns else 0,
            }
        )
        decision = read_csv(shard_dir / f"{shard_id}_decision_counts.csv")
        if not decision.empty:
            decision["shard_id"] = shard_id
            decision_frames.append(decision)
        selected = read_csv(shard_dir / f"{shard_id}_selected_portfolio_queue.csv")
        if not selected.empty:
            selected["shard_id"] = shard_id
            selected_frames.append(selected)
        family = read_csv(shard_dir / f"{shard_id}_family_decision_summary.csv")
        if not family.empty:
            family["shard_id"] = shard_id
            family_frames.append(family)

    shard_summary = pd.DataFrame(rows)
    decision_counts = pd.concat(decision_frames, ignore_index=True) if decision_frames else pd.DataFrame()
    selected_queue = pd.concat(selected_frames, ignore_index=True) if selected_frames else pd.DataFrame()
    family_summary = pd.concat(family_frames, ignore_index=True) if family_frames else pd.DataFrame()
    return shard_summary, decision_counts, selected_queue, family_summary


def main() -> None:
    external = Path(os.environ.get("A7LS18_EXTERNAL", str(DEFAULT_EXTERNAL)))
    report_path = Path(os.environ.get("A7LS18_REPORT", str(DEFAULT_REPORT)))
    queue_manifest = read_json(external / "a7ls18_queue_manifest.json")
    shard_plan = read_csv(external / "a7ls18_shard_plan.csv")
    shard_summary, decision_counts, selected_queue, family_summary = collect_shards(external)

    discovered_shards = shard_dirs(external)
    expected_shards = int(queue_manifest.get("shard_count", len(shard_plan) or len(discovered_shards)) or 0)
    completed_shards = int(shard_summary["has_manifest"].sum()) if not shard_summary.empty else 0
    missing_shards: list[str] = []
    if not shard_plan.empty and "shard_id" in shard_plan.columns:
        present = set(shard_summary.loc[shard_summary["has_manifest"], "shard_id"].astype(str)) if not shard_summary.empty else set()
        missing_shards = sorted(set(shard_plan["shard_id"].astype(str)) - present)

    if not decision_counts.empty:
        decision_total = (
            decision_counts.groupby(["decision", "label_family"], dropna=False)["count"]
            .sum()
            .reset_index()
            .sort_values("count", ascending=False)
        )
    else:
        decision_total = pd.DataFrame(columns=["decision", "label_family", "count"])

    if not family_summary.empty:
        family_total = (
            family_summary.groupby(["semantic_pair", "decision"], dropna=False)["count"]
            .sum()
            .reset_index()
            .sort_values("count", ascending=False)
        )
    else:
        family_total = pd.DataFrame(columns=["semantic_pair", "decision", "count"])

    blockers: list[str] = []
    if expected_shards and completed_shards < expected_shards:
        blockers.append("incomplete_shards")
    if not shard_summary.empty and shard_summary["decision"].astype(str).str.contains("MISSING_FIELDS", na=False).any():
        blockers.append("missing_numeric_fields")
    total_non_l7 = int(shard_summary["non_l7_numeric_clue_rows"].sum()) if not shard_summary.empty else 0
    total_rank = int(shard_summary["rank_label_diagnostic_clue_rows"].sum()) if not shard_summary.empty else 0
    total_selected = int(shard_summary["selected_portfolio_queue_count"].sum()) if not shard_summary.empty else 0
    total_responses = int(shard_summary["label_response_rows"].sum()) if not shard_summary.empty else 0
    total_activity = int(shard_summary["materialized_activity_ok_count"].sum()) if not shard_summary.empty else 0
    if completed_shards == expected_shards and total_non_l7 <= 0 and total_rank <= 0:
        blockers.append("no_numeric_clues")

    if blockers:
        decision = "HOLD_A7LS18_COMPANY_NUMERIC_AGGREGATE_NEEDS_A7LS19"
    else:
        decision = "PASS_A7LS18_COMPANY_NUMERIC_CLUES_READY_FOR_A7LS19"

    manifest = {
        "stage": "A7LS-18",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "external": str(external),
        "expected_shards": expected_shards,
        "completed_shards": completed_shards,
        "missing_shards": missing_shards,
        "queue_rows": int(queue_manifest.get("queue_rows", int(shard_summary["queue_rows"].sum()) if not shard_summary.empty else 0) or 0),
        "label_response_rows": total_responses,
        "materialized_activity_ok_count": total_activity,
        "non_l7_numeric_clue_rows": total_non_l7,
        "rank_label_diagnostic_clue_rows": total_rank,
        "selected_portfolio_queue_count": total_selected,
        "uses_may": False,
        "executes_search": False,
        "authorizes_a7ls19_checkpoint_arbitration": True,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }

    out_dir = external / "aggregate"
    out_dir.mkdir(parents=True, exist_ok=True)
    shard_summary.to_csv(out_dir / "a7ls18_shard_summary.csv", index=False)
    decision_total.to_csv(out_dir / "a7ls18_decision_counts.csv", index=False)
    family_total.to_csv(out_dir / "a7ls18_family_decision_summary.csv", index=False)
    selected_queue.to_csv(out_dir / "a7ls18_selected_portfolio_queue.csv", index=False)
    write_json(out_dir / "a7ls18_manifest.json", manifest)

    report_lines = [
        "# CRYPTO A7LS18 COMPANY NUMERIC AGGREGATE",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Decision Counts",
        "",
        md_table(decision_total, 80),
        "",
        "## Family Decision Summary",
        "",
        md_table(family_total, 80),
        "",
        "## Shard Summary",
        "",
        md_table(shard_summary, 80),
        "",
        "## Boundary",
        "",
        "A7LS-18 aggregates numeric diagnostics only. It does not authorize alpha proof, shadow, paper, or live.",
        "",
    ]
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    if os.environ.get("A7LS18_WRITE_LOCAL_COPY", "0").lower() in {"1", "true", "yes"}:
        LOCAL_RUNTIME.mkdir(parents=True, exist_ok=True)
        shard_summary.to_csv(LOCAL_RUNTIME / "a7ls18_shard_summary.csv", index=False)
        decision_total.to_csv(LOCAL_RUNTIME / "a7ls18_decision_counts.csv", index=False)
        family_total.to_csv(LOCAL_RUNTIME / "a7ls18_family_decision_summary.csv", index=False)
        selected_queue.to_csv(LOCAL_RUNTIME / "a7ls18_selected_portfolio_queue.csv", index=False)
        write_json(LOCAL_RUNTIME / "a7ls18_manifest.json", manifest)
        LOCAL_REPORT.parent.mkdir(parents=True, exist_ok=True)
        LOCAL_REPORT.write_text("\n".join(report_lines), encoding="utf-8")

    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
