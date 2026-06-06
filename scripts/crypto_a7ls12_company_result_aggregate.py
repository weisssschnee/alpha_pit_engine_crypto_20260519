from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
EXTERNAL = Path("G:/AlphaFactory_CryptoData/research_runtime/a7ls12_company_deep_audit")
RUNTIME = REPO / "runtime" / "a7ls12_company_result_aggregate"
REPORT = REPO / "reports" / "CRYPTO_A7LS12_COMPANY_RESULT_AGGREGATE_20260606.md"
CONTRACT = REPO / "runtime" / "a7ls12_deep_audit_packet" / "a7ls12_manifest.json"
QUEUE = REPO / "runtime" / "a7ls12_deep_audit_packet" / "a7ls12_deep_audit_queue.csv"


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


def collect_csv(shard_dir: Path, pattern: str) -> pd.DataFrame:
    frames = []
    for path in sorted(shard_dir.glob(pattern)):
        frame = read_csv(path)
        if frame.empty:
            continue
        frame["source_file"] = str(path)
        frames.append(frame)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def summarize(df: pd.DataFrame, cols: list[str], name: str = "rows") -> pd.DataFrame:
    if df.empty or any(col not in df.columns for col in cols):
        return pd.DataFrame(columns=cols + [name])
    return df.groupby(cols, dropna=False).size().reset_index(name=name).sort_values(name, ascending=False)


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


def blocker_family(decision: Any) -> str:
    text = str(decision)
    if text.endswith("_NUMERIC_CLUE"):
        return "numeric_clue"
    if "RANK_LABEL_DIAGNOSTIC_CLUE" in text:
        return "rank_label_diagnostic_clue"
    if "CONTROL_DOMINATED" in text:
        return "control_dominated"
    if "PRE_MAY_UNSTABLE" in text:
        return "pre_may_unstable"
    if "ONE_BAR_LAG" in text:
        return "lag_fragile"
    if "NONOVERLAP" in text:
        return "nonoverlap_weak"
    if "COST" in text:
        return "cost_fragile"
    if "MISSING" in text:
        return "missing_fields"
    return "other"


def enrich_with_queue(responses: pd.DataFrame, queue: pd.DataFrame) -> pd.DataFrame:
    if responses.empty or queue.empty or "blueprint_id" not in responses.columns:
        return responses
    keep = [
        "blueprint_id",
        "a7ls12_rank",
        "promotion_lane",
        "next_wave_family",
        "a7ls_arm",
        "source_seed_id",
        "source_info_axis",
        "source_stability_tier",
        "source_info_axis_score",
        "skeleton_key",
        "production_key",
        "semantic_pair",
        "a7ls12_deep_shard",
    ]
    available = [col for col in keep if col in queue.columns]
    if "blueprint_id" not in available:
        return responses
    dedup = queue[available].drop_duplicates("blueprint_id")
    return responses.merge(dedup, on="blueprint_id", how="left", suffixes=("", "_queue"))


def numeric_col(df: pd.DataFrame, col: str) -> pd.Series:
    if col not in df.columns:
        return pd.Series([pd.NA] * len(df), index=df.index, dtype="float64")
    return pd.to_numeric(df[col], errors="coerce")


def main() -> int:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    contract = read_json(CONTRACT)
    expected = int(contract.get("deep_audit_shard_count", 0))
    queue = read_csv(QUEUE)
    manifest_rows: list[dict[str, Any]] = []
    missing_rows: list[dict[str, Any]] = []
    response_frames: list[pd.DataFrame] = []
    material_frames: list[pd.DataFrame] = []
    portfolio_frames: list[pd.DataFrame] = []

    for i in range(expected):
        shard = f"s{i:03d}"
        prefix = f"a7ls12_s{i:03d}"
        shard_dir = EXTERNAL / f"shard_{i:03d}"
        manifest_path = shard_dir / f"{prefix}_manifest.json"
        if not manifest_path.exists():
            missing_rows.append({"shard": shard, "shard_dir": str(shard_dir), "reason": "missing_manifest"})
            continue
        manifest = read_json(manifest_path)
        manifest_rows.append(
            {
                "shard": shard,
                "manifest_path": str(manifest_path),
                "decision": manifest.get("decision", ""),
                "blockers": ";".join(map(str, manifest.get("blockers", []))),
                "missing_numeric_fields": ";".join(map(str, manifest.get("missing_numeric_fields", []))),
                "input_blueprint_count": manifest.get("input_blueprint_count", 0),
                "hours_per_split": manifest.get("hours_per_split", ""),
                "materialized_activity_ok_count": manifest.get("materialized_activity_ok_count", 0),
                "label_response_rows": manifest.get("label_response_rows", 0),
                "non_l7_numeric_clue_rows": manifest.get("non_l7_numeric_clue_rows", 0),
                "rank_label_diagnostic_clue_rows": manifest.get("rank_label_diagnostic_clue_rows", 0),
                "portfolio_queue_count": manifest.get("portfolio_queue_count", 0),
                "selected_portfolio_queue_count": manifest.get("selected_portfolio_queue_count", 0),
                "generated_at": manifest.get("generated_at", ""),
            }
        )
        responses = collect_csv(shard_dir, "*label_response_metrics.csv")
        if not responses.empty:
            responses["shard"] = shard
            response_frames.append(responses)
        material = collect_csv(shard_dir, "*materialization_metrics.csv")
        if not material.empty:
            material["shard"] = shard
            material_frames.append(material)
        portfolio = collect_csv(shard_dir, "*selected_portfolio_queue.csv")
        if not portfolio.empty:
            portfolio["shard"] = shard
            portfolio_frames.append(portfolio)

    manifests = pd.DataFrame(manifest_rows)
    missing = pd.DataFrame(missing_rows)
    responses = pd.concat(response_frames, ignore_index=True) if response_frames else pd.DataFrame()
    responses = enrich_with_queue(responses, queue)
    material = pd.concat(material_frames, ignore_index=True) if material_frames else pd.DataFrame()
    portfolio = pd.concat(portfolio_frames, ignore_index=True) if portfolio_frames else pd.DataFrame()

    if not responses.empty:
        responses["blocker_family"] = responses["decision"].map(blocker_family)
    non_l7 = (
        responses[
            responses["decision"].astype(str).str.endswith("_NUMERIC_CLUE")
            & responses["label_family"].astype(str).ne("L7_ranked_future_return")
        ].copy()
        if not responses.empty
        else pd.DataFrame()
    )
    rank_label = (
        responses[responses["decision"].astype(str).str.contains("RANK_LABEL_DIAGNOSTIC_CLUE", na=False)].copy()
        if not responses.empty
        else pd.DataFrame()
    )

    shortlist = non_l7.copy()
    if not shortlist.empty:
        control = numeric_col(shortlist, "control_ratio_premay_max")
        robust = numeric_col(shortlist, "robust_min_tstat_floor")
        lag = numeric_col(shortlist, "one_bar_lag_recent_oriented")
        cost = numeric_col(shortlist, "cost10_recent_oriented")
        shortlist["deep_audit_score"] = (
            (1.0 - control.clip(upper=1.0)).fillna(0.0) * 100.0
            + robust.clip(lower=0).fillna(0.0) * 5.0
            + lag.clip(lower=0).fillna(0.0) * 1000.0
            + cost.clip(lower=0).fillna(0.0) * 1000.0
        )
        shortlist = shortlist.sort_values(["deep_audit_score", "blueprint_id"], ascending=[False, True]).head(120)

    outputs = {
        "a7ls12_shard_manifest_summary.csv": manifests,
        "a7ls12_missing_shards.csv": missing,
        "a7ls12_combined_responses.csv": responses,
        "a7ls12_combined_materialization.csv": material,
        "a7ls12_selected_portfolio_queue.csv": portfolio,
        "a7ls12_non_l7_numeric_clues.csv": non_l7,
        "a7ls12_rank_label_diagnostic_clues.csv": rank_label,
        "a7ls12_non_l7_shortlist.csv": shortlist,
        "a7ls12_non_l7_by_label.csv": summarize(non_l7, ["label_family"]),
        "a7ls12_non_l7_by_semantic_pair.csv": summarize(non_l7, ["semantic_pair"]),
        "a7ls12_non_l7_by_next_wave_family.csv": summarize(non_l7, ["next_wave_family"]),
        "a7ls12_non_l7_by_source_info_axis.csv": summarize(non_l7, ["source_info_axis"]),
        "a7ls12_non_l7_by_pair_label.csv": summarize(non_l7, ["semantic_pair", "label_family"]),
        "a7ls12_non_l7_by_shard.csv": summarize(non_l7, ["shard"]),
        "a7ls12_response_by_blocker_family.csv": summarize(responses, ["blocker_family"]),
        "a7ls12_response_by_family_blocker.csv": summarize(responses, ["next_wave_family", "blocker_family"]),
        "a7ls12_response_by_pair_blocker.csv": summarize(responses, ["semantic_pair", "blocker_family"]),
    }
    for name, frame in outputs.items():
        frame.to_csv(RUNTIME / name, index=False)

    completed = int(len(manifests))
    pass_shards = int(manifests["decision"].astype(str).str.startswith("PASS_").sum()) if not manifests.empty else 0
    response_rows = int(len(responses))
    material_ok = int(pd.to_numeric(manifests.get("materialized_activity_ok_count", pd.Series(dtype=float)), errors="coerce").fillna(0).sum())
    non_l7_rows = int(len(non_l7))
    rank_rows = int(len(rank_label))
    shortlist_rows = int(len(shortlist))
    family_count = int(non_l7["next_wave_family"].nunique(dropna=True)) if not non_l7.empty and "next_wave_family" in non_l7.columns else 0
    axis_count = int(non_l7["source_info_axis"].nunique(dropna=True)) if not non_l7.empty and "source_info_axis" in non_l7.columns else 0
    label_count = int(non_l7["label_family"].nunique(dropna=True)) if not non_l7.empty and "label_family" in non_l7.columns else 0

    pair_summary = outputs["a7ls12_non_l7_by_semantic_pair.csv"]
    family_summary = outputs["a7ls12_non_l7_by_next_wave_family.csv"]
    axis_summary = outputs["a7ls12_non_l7_by_source_info_axis.csv"]
    top_pair_share = float(pair_summary["rows"].max()) / float(non_l7_rows) if non_l7_rows and not pair_summary.empty else 0.0
    top_family_share = float(family_summary["rows"].max()) / float(non_l7_rows) if non_l7_rows and not family_summary.empty else 0.0
    top_axis_share = float(axis_summary["rows"].max()) / float(non_l7_rows) if non_l7_rows and not axis_summary.empty else 0.0

    blockers: list[str] = []
    if completed != expected:
        blockers.append("missing_company_shard_results")
    if non_l7_rows == 0:
        blockers.append("no_non_l7_numeric_clues")
    if top_pair_share > 0.75:
        blockers.append("non_l7_semantic_pair_concentration_high")
    if top_family_share > 0.75:
        blockers.append("non_l7_next_family_concentration_high")
    if top_axis_share > 0.75:
        blockers.append("non_l7_source_axis_concentration_high")

    decision = (
        "PASS_A7LS12_DEEP_AUDIT_AGGREGATED_CLUES_FOUND_NO_SEARCH_AUTH"
        if completed == expected and non_l7_rows > 0
        else "HOLD_A7LS12_DEEP_AUDIT_NO_USABLE_NON_L7_CLUES"
    )

    manifest = {
        "stage": "A7LS-12-AGG",
        "decision": decision,
        "generated_at": now_utc(),
        "expected_shards": expected,
        "completed_shards": completed,
        "pass_shards": pass_shards,
        "response_rows": response_rows,
        "materialized_activity_ok_total": material_ok,
        "non_l7_numeric_clue_rows": non_l7_rows,
        "rank_label_diagnostic_rows": rank_rows,
        "shortlist_rows": shortlist_rows,
        "non_l7_next_wave_family_count": family_count,
        "non_l7_source_info_axis_count": axis_count,
        "non_l7_label_family_count": label_count,
        "top_non_l7_semantic_pair_share": top_pair_share,
        "top_non_l7_next_family_share": top_family_share,
        "top_non_l7_source_axis_share": top_axis_share,
        "hours_per_split": contract.get("hours_per_split", 0),
        "uses_may": False,
        "executes_search": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "blockers": blockers,
    }
    write_json(RUNTIME / "a7ls12_aggregate_manifest.json", manifest)

    report = [
        "# CRYPTO A7LS-12 COMPANY RESULT AGGREGATE",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "## Summary",
        "",
        f"- expected_shards: {expected}",
        f"- completed_shards: {completed}",
        f"- pass_shards: {pass_shards}",
        f"- hours_per_split: {manifest['hours_per_split']}",
        f"- response_rows: {response_rows}",
        f"- materialized_activity_ok_total: {material_ok}",
        f"- non_l7_numeric_clue_rows: {non_l7_rows}",
        f"- rank_label_diagnostic_rows: {rank_rows}",
        f"- shortlist_rows: {shortlist_rows}",
        f"- non_l7_next_wave_family_count: {family_count}",
        f"- non_l7_source_info_axis_count: {axis_count}",
        f"- non_l7_label_family_count: {label_count}",
        f"- top_non_l7_semantic_pair_share: {top_pair_share:.3f}",
        f"- top_non_l7_next_family_share: {top_family_share:.3f}",
        f"- top_non_l7_source_axis_share: {top_axis_share:.3f}",
        f"- blockers: {', '.join(blockers) if blockers else '<none>'}",
        "",
        "A7LS-12 is a full-timestamp deep audit of A7LS-11 promoted non-L7 clues. It does not authorize search, alpha proof, shadow, paper, or live.",
        "",
        "## Shard Summary",
        "",
        md_table(manifests),
        "",
        "## Non-L7 By Label",
        "",
        md_table(outputs["a7ls12_non_l7_by_label.csv"]),
        "",
        "## Non-L7 By Source Info Axis",
        "",
        md_table(axis_summary),
        "",
        "## Non-L7 By Next Wave Family",
        "",
        md_table(family_summary),
        "",
        "## Response By Blocker Family",
        "",
        md_table(outputs["a7ls12_response_by_blocker_family.csv"]),
        "",
        "## Authorization",
        "",
        "- A7LS-13 consolidation / replay packet contract: allowed if non-L7 clues remain after review",
        "- new formula search / large search: not authorized",
        "- alpha proof / shadow / paper / live: not authorized",
        "",
    ]
    REPORT.write_text("\n".join(report), encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
