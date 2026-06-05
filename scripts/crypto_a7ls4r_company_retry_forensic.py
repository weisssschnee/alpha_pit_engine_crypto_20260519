from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
EXTERNAL = Path("G:/AlphaFactory_CryptoData/research_runtime/a7ls4r_company_retry_numeric")
ORIGINAL = REPO / "runtime" / "a7ls4_company_numeric_forensic"
RUNTIME = REPO / "runtime" / "a7ls4r_company_retry_forensic"
REPORT = REPO / "reports" / "CRYPTO_A7LS4R_COMPANY_RETRY_FORENSIC_20260605.md"


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
        return "```text\n" + view.to_string(index=False) + "\n```"


def collect_shard(shard_dir: Path, shard: str) -> dict[str, Any]:
    manifest = read_json(shard_dir / f"a7ls3hr_{shard}_manifest.json")
    responses = read_csv(shard_dir / f"a7ls3hr_{shard}_label_response_metrics.csv")
    portfolio = read_csv(shard_dir / f"a7ls3hr_{shard}_selected_portfolio_queue.csv")
    materialized = read_csv(shard_dir / f"a7ls3hr_{shard}_materialization_metrics.csv")
    return {
        "manifest": manifest,
        "responses": responses,
        "portfolio": portfolio,
        "materialized": materialized,
    }


def summarize(df: pd.DataFrame, cols: list[str], name: str = "rows") -> pd.DataFrame:
    if df.empty or any(col not in df.columns for col in cols):
        return pd.DataFrame(columns=cols + [name])
    return df.groupby(cols, dropna=False).size().reset_index(name=name).sort_values(name, ascending=False)


def main() -> int:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    retry_shards = ["s007", "s013", "s014"]
    manifest_rows: list[dict[str, Any]] = []
    response_frames: list[pd.DataFrame] = []
    portfolio_frames: list[pd.DataFrame] = []
    material_frames: list[pd.DataFrame] = []

    for shard in retry_shards:
        shard_dir = EXTERNAL / f"shard_{int(shard[1:]):03d}"
        payload = collect_shard(shard_dir, shard)
        manifest = payload["manifest"]
        manifest_rows.append(
            {
                "shard": shard,
                "decision_before": "HOLD_A7LS3HR_MISSING_FIELDS",
                "decision_after": manifest.get("decision", ""),
                "blockers_after": ";".join(map(str, manifest.get("blockers", []))),
                "missing_numeric_fields_after": ";".join(map(str, manifest.get("missing_numeric_fields", []))),
                "materialized_activity_ok_count": manifest.get("materialized_activity_ok_count", ""),
                "label_response_rows": manifest.get("label_response_rows", ""),
                "non_l7_numeric_clue_rows": manifest.get("non_l7_numeric_clue_rows", ""),
                "rank_label_diagnostic_clue_rows": manifest.get("rank_label_diagnostic_clue_rows", ""),
                "portfolio_queue_count": manifest.get("portfolio_queue_count", ""),
                "selected_portfolio_queue_count": manifest.get("selected_portfolio_queue_count", ""),
                "generated_at": manifest.get("generated_at", ""),
            }
        )
        responses = payload["responses"]
        if not responses.empty:
            responses["shard"] = shard
            response_frames.append(responses)
        portfolio = payload["portfolio"]
        if not portfolio.empty:
            portfolio["shard"] = shard
            portfolio_frames.append(portfolio)
        materialized = payload["materialized"]
        if not materialized.empty:
            materialized["shard"] = shard
            material_frames.append(materialized)

    manifest_df = pd.DataFrame(manifest_rows)
    responses = pd.concat(response_frames, ignore_index=True) if response_frames else pd.DataFrame()
    portfolio = pd.concat(portfolio_frames, ignore_index=True) if portfolio_frames else pd.DataFrame()
    materialized = pd.concat(material_frames, ignore_index=True) if material_frames else pd.DataFrame()

    non_l7 = responses[
        responses.get("decision", pd.Series(dtype=str)).astype(str).str.endswith("_NUMERIC_CLUE")
        & responses.get("label_family", pd.Series(dtype=str)).ne("L7_ranked_future_return")
    ].copy() if not responses.empty else pd.DataFrame()

    rank_label = responses[
        responses.get("decision", pd.Series(dtype=str)).astype(str).str.contains("RANK_LABEL_DIAGNOSTIC_CLUE", na=False)
    ].copy() if not responses.empty else pd.DataFrame()

    manifest_df.to_csv(RUNTIME / "a7ls4r_retry_shard_manifest_summary.csv", index=False)
    responses.to_csv(RUNTIME / "a7ls4r_retry_combined_responses.csv", index=False)
    portfolio.to_csv(RUNTIME / "a7ls4r_retry_combined_portfolio.csv", index=False)
    materialized.to_csv(RUNTIME / "a7ls4r_retry_combined_materialization.csv", index=False)
    non_l7.to_csv(RUNTIME / "a7ls4r_retry_non_l7_numeric_clues.csv", index=False)
    rank_label.to_csv(RUNTIME / "a7ls4r_retry_rank_label_diagnostic_clues.csv", index=False)

    by_label = summarize(non_l7, ["label_family"])
    by_pair = summarize(non_l7, ["semantic_pair"])
    by_pair_label = summarize(non_l7, ["semantic_pair", "label_family"])
    by_shard = summarize(non_l7, ["shard"])
    by_label.to_csv(RUNTIME / "a7ls4r_retry_non_l7_by_label.csv", index=False)
    by_pair.to_csv(RUNTIME / "a7ls4r_retry_non_l7_by_semantic_pair.csv", index=False)
    by_pair_label.to_csv(RUNTIME / "a7ls4r_retry_non_l7_by_pair_label.csv", index=False)
    by_shard.to_csv(RUNTIME / "a7ls4r_retry_non_l7_by_shard.csv", index=False)

    missing_resolved = int(
        manifest_df["missing_numeric_fields_after"].fillna("").astype(str).eq("").sum()
    )
    pass_retry_shards = int(manifest_df["decision_after"].astype(str).str.startswith("PASS_").sum())
    non_l7_rows = int(len(non_l7))
    rank_rows = int(len(rank_label))
    materialized_ok = int(pd.to_numeric(manifest_df["materialized_activity_ok_count"], errors="coerce").fillna(0).sum())

    blockers: list[str] = []
    if missing_resolved != len(retry_shards):
        blockers.append("retry_missing_fields_remain")
    if non_l7_rows == 0:
        blockers.append("retry_no_non_l7_numeric_clues")
    if not by_pair.empty and float(by_pair["rows"].max()) / max(1, non_l7_rows) > 0.60:
        blockers.append("retry_clue_family_concentration")

    decision = (
        "PASS_A7LS4R_RETRY_MISSING_FIELDS_RESOLVED_WITH_NON_L7_CLUES"
        if missing_resolved == len(retry_shards) and non_l7_rows > 0
        else "HOLD_A7LS4R_RETRY_NO_USABLE_NEW_EVIDENCE"
    )
    manifest = {
        "stage": "A7LS-4R",
        "generated_at": now_utc(),
        "decision": decision,
        "external": str(EXTERNAL),
        "retry_shards": retry_shards,
        "retry_shard_count": len(retry_shards),
        "missing_resolved_shards": missing_resolved,
        "pass_retry_shards": pass_retry_shards,
        "retry_response_rows": int(len(responses)),
        "retry_materialized_activity_ok_count": materialized_ok,
        "retry_non_l7_numeric_clue_rows": non_l7_rows,
        "retry_rank_label_diagnostic_rows": rank_rows,
        "blockers": blockers,
        "executes_generation": False,
        "executes_numeric_probe": False,
        "executes_search": False,
        "authorizes_a7ls5_followup_contract": decision.startswith("PASS"),
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "source_note": "Retry result for the three A7LS-3HR missing-field shards after syncing current evaluator dependencies to company machine.",
    }
    write_json(RUNTIME / "a7ls4r_manifest.json", manifest)

    original = read_json(ORIGINAL / "a7ls4_manifest.json")
    report = [
        "# CRYPTO A7LS-4R COMPANY RETRY FORENSIC",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "## Summary",
        "",
        f"- retry_shards: {', '.join(retry_shards)}",
        f"- missing_resolved_shards: {missing_resolved} / {len(retry_shards)}",
        f"- pass_retry_shards: {pass_retry_shards}",
        f"- retry_response_rows: {len(responses)}",
        f"- retry_materialized_activity_ok_count: {materialized_ok}",
        f"- retry_non_l7_numeric_clue_rows: {non_l7_rows}",
        f"- retry_rank_label_diagnostic_rows: {rank_rows}",
        f"- original_a7ls4_non_l7_clue_rows: {original.get('non_l7_clue_rows', '')}",
        f"- original_a7ls4_shortlist_rows: {original.get('shortlist_rows', '')}",
        "",
        "## Retry Shards",
        "",
        md_table(manifest_df),
        "",
        "## Non-L7 Clues By Label",
        "",
        md_table(by_label),
        "",
        "## Non-L7 Clues By Semantic Pair",
        "",
        md_table(by_pair),
        "",
        "## Non-L7 Clues By Pair And Label",
        "",
        md_table(by_pair_label),
        "",
        "## New Non-L7 Clues",
        "",
        md_table(
            non_l7[
                [
                    c
                    for c in [
                        "shard",
                        "blueprint_id",
                        "expression",
                        "semantic_pair",
                        "motif",
                        "label_family",
                        "label_horizon_h",
                        "control_ratio_premay_max",
                        "robust_min_tstat_floor",
                        "cost10_recent_oriented",
                        "one_bar_lag_recent_oriented",
                        "decision",
                    ]
                    if c in non_l7.columns
                ]
            ],
            40,
        ),
        "",
        "## Authorization",
        "",
        "- Retry forensic only.",
        "- This does not authorize search, alpha proof, shadow, paper, or live.",
        "- If passed, it only authorizes drafting A7LS-5 follow-up / repair contract.",
    ]
    REPORT.write_text("\n".join(report), encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
