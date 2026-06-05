from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
EXTERNAL = Path("G:/AlphaFactory_CryptoData/research_runtime/a7ls6_company_deep_numeric")
RUNTIME = REPO / "runtime" / "a7ls6_company_result_aggregate"
REPORT = REPO / "reports" / "CRYPTO_A7LS6_COMPANY_RESULT_AGGREGATE_20260605.md"
A7LS6 = REPO / "runtime" / "a7ls6_deep_followup_queue_contract" / "a7ls6_manifest.json"


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


def main() -> int:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    contract = read_json(A7LS6)
    expected = int(contract.get("company_shard_count", 0))
    manifest_rows: list[dict[str, Any]] = []
    missing_rows: list[dict[str, Any]] = []
    response_frames: list[pd.DataFrame] = []
    material_frames: list[pd.DataFrame] = []
    portfolio_frames: list[pd.DataFrame] = []

    for i in range(expected):
        shard = f"s{i:03d}"
        prefix = f"a7ls6_s{i:03d}"
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
        for col in ["control_ratio_premay_max", "robust_min_tstat_floor", "cost10_recent_oriented", "one_bar_lag_recent_oriented"]:
            shortlist[col] = pd.to_numeric(shortlist.get(col), errors="coerce")
        shortlist["deep_followup_score"] = (
            (1.0 - shortlist["control_ratio_premay_max"].clip(upper=1.0)).fillna(0.0) * 100.0
            + shortlist["robust_min_tstat_floor"].clip(lower=0).fillna(0.0)
            + shortlist["one_bar_lag_recent_oriented"].clip(lower=0).fillna(0.0) * 1000.0
            + shortlist["cost10_recent_oriented"].clip(lower=0).fillna(0.0) * 1000.0
        )
        shortlist = shortlist.sort_values(["deep_followup_score", "blueprint_id"], ascending=[False, True]).head(96)

    outputs = {
        "a7ls6_shard_manifest_summary.csv": manifests,
        "a7ls6_missing_shards.csv": missing,
        "a7ls6_combined_responses.csv": responses,
        "a7ls6_combined_materialization.csv": material,
        "a7ls6_selected_portfolio_queue.csv": portfolio,
        "a7ls6_non_l7_numeric_clues.csv": non_l7,
        "a7ls6_rank_label_diagnostic_clues.csv": rank_label,
        "a7ls6_non_l7_shortlist.csv": shortlist,
        "a7ls6_non_l7_by_label.csv": summarize(non_l7, ["label_family"]),
        "a7ls6_non_l7_by_semantic_pair.csv": summarize(non_l7, ["semantic_pair"]),
        "a7ls6_non_l7_by_pair_label.csv": summarize(non_l7, ["semantic_pair", "label_family"]),
        "a7ls6_non_l7_by_shard.csv": summarize(non_l7, ["shard"]),
        "a7ls6_response_by_blocker_family.csv": summarize(responses, ["blocker_family"]),
        "a7ls6_response_by_pair_blocker.csv": summarize(responses, ["semantic_pair", "blocker_family"]),
    }
    for name, frame in outputs.items():
        frame.to_csv(RUNTIME / name, index=False)

    completed = int(len(manifests))
    pass_shards = int(manifests["decision"].astype(str).str.startswith("PASS_").sum()) if not manifests.empty else 0
    response_rows = int(len(responses))
    material_ok = int(pd.to_numeric(manifests.get("materialized_activity_ok_count", pd.Series(dtype=float)), errors="coerce").fillna(0).sum())
    non_l7_rows = int(len(non_l7))
    rank_rows = int(len(rank_label))
    pair_summary = outputs["a7ls6_non_l7_by_semantic_pair.csv"]
    top_pair_share = float(pair_summary["rows"].max()) / float(non_l7_rows) if non_l7_rows and not pair_summary.empty else 0.0
    nonbasis_rows = int(non_l7_rows - int(pair_summary.loc[pair_summary["semantic_pair"].eq("basis_premium_like"), "rows"].sum())) if not pair_summary.empty else 0

    blockers: list[str] = []
    if completed != expected:
        blockers.append("missing_company_shard_results")
    if non_l7_rows == 0:
        blockers.append("no_non_l7_numeric_clues")
    if top_pair_share > 0.75:
        blockers.append("non_l7_family_concentration_high")
    if nonbasis_rows == 0:
        blockers.append("no_nonbasis_non_l7_clues")

    decision = (
        "PASS_A7LS6_DEEP_NUMERIC_AGGREGATED_CLUES_FOUND_NO_SEARCH_AUTH"
        if completed == expected and non_l7_rows > 0
        else "HOLD_A7LS6_DEEP_NUMERIC_NO_USABLE_CLUES"
    )
    manifest = {
        "stage": "A7LS-6-AGG",
        "generated_at": now_utc(),
        "decision": decision,
        "external": str(EXTERNAL),
        "expected_shards": expected,
        "completed_shards": completed,
        "pass_shards": pass_shards,
        "response_rows": response_rows,
        "materialized_activity_ok_total": material_ok,
        "non_l7_numeric_clue_rows": non_l7_rows,
        "rank_label_diagnostic_rows": rank_rows,
        "shortlist_rows": int(len(shortlist)),
        "top_non_l7_semantic_pair_share": top_pair_share,
        "nonbasis_non_l7_clue_rows": nonbasis_rows,
        "blockers": blockers,
        "hours_per_split": 2160,
        "executes_numeric_probe": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ls6_aggregate_manifest.json", manifest)

    lines = [
        "# CRYPTO A7LS-6 COMPANY DEEP RESULT AGGREGATE",
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
        f"- shortlist_rows: {len(shortlist)}",
        f"- top_non_l7_semantic_pair_share: {top_pair_share:.3f}",
        f"- nonbasis_non_l7_clue_rows: {nonbasis_rows}",
        f"- blockers: {', '.join(blockers) if blockers else '<none>'}",
        "",
        "## Shard Summary",
        "",
        md_table(manifests, 40),
        "",
        "## Non-L7 By Label",
        "",
        md_table(outputs["a7ls6_non_l7_by_label.csv"]),
        "",
        "## Non-L7 By Semantic Pair",
        "",
        md_table(outputs["a7ls6_non_l7_by_semantic_pair.csv"]),
        "",
        "## Response Blockers",
        "",
        md_table(outputs["a7ls6_response_by_blocker_family.csv"]),
        "",
        "## Shortlist",
        "",
        md_table(shortlist[["blueprint_id", "expression", "semantic_pair", "motif", "label_family", "label_horizon_h", "control_ratio_premay_max", "cost10_recent_oriented", "deep_followup_score"]], 40)
        if not shortlist.empty
        else "`<empty>`",
        "",
        "## Authorization",
        "",
        "- This aggregate does not authorize formula search, large search, alpha proof, shadow, paper, or live.",
        "- May is not used.",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
