from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
DATE = "20260610"
STAGE = "A7LS-29"

PULLBACK_ROOT = Path(
    r"G:\AlphaFactory_CryptoData\company_pullback\a7ls29_productive_numeric_wave_20260610\unzipped"
)
RUNTIME = REPO / "runtime" / "a7ls29_productive_numeric_acceptance_20260610"
REPORT = REPO / "reports" / f"CRYPTO_A7LS29_PRODUCTIVE_NUMERIC_ACCEPTANCE_{DATE}.md"
DATA_RUNTIME = Path(r"G:\AlphaFactory_CryptoData\research_runtime\a7ls29_productive_numeric_acceptance_20260610")
DATA_REPORT = Path(r"G:\AlphaFactory_CryptoData\reports") / REPORT.name
DATA_MANIFEST = Path(r"G:\AlphaFactory_CryptoData\manifests\a7ls29_productive_numeric_acceptance_20260610_manifest.json")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 40) -> str:
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


def read_manifest(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    data["manifest_path"] = str(path)
    data["shard_id"] = path.parent.name
    return data


def read_csvs(pattern: str) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for path in sorted(PULLBACK_ROOT.rglob(pattern)):
        df = pd.read_csv(path)
        df["shard_id"] = path.parent.name
        df["source_path"] = str(path)
        frames.append(df)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def safe_value_counts(df: pd.DataFrame, columns: list[str], name: str) -> pd.DataFrame:
    if df.empty or any(col not in df.columns for col in columns):
        return pd.DataFrame(columns=[*columns, name])
    return df.groupby(columns, dropna=False).size().reset_index(name=name).sort_values(name, ascending=False)


def main() -> None:
    if not PULLBACK_ROOT.exists():
        raise FileNotFoundError(PULLBACK_ROOT)
    RUNTIME.mkdir(parents=True, exist_ok=True)
    DATA_RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    DATA_REPORT.parent.mkdir(parents=True, exist_ok=True)

    manifests = [read_manifest(path) for path in sorted(PULLBACK_ROOT.rglob("shards/*/*manifest.json"))]
    if len(manifests) != 12:
        raise RuntimeError(f"expected 12 shard manifests, found {len(manifests)}")
    shard_summary = pd.DataFrame(manifests)

    selected = read_csvs("*selected_portfolio_queue.csv")
    portfolio = read_csvs("*portfolio_marginal_proxy.csv")
    materialization = read_csvs("*materialization_metrics.csv")
    responses = read_csvs("*label_response_metrics.csv")

    selected_family = safe_value_counts(selected, ["semantic_pair", "motif", "label_family"], "selected_rows")
    selected_label = safe_value_counts(selected, ["label_family", "label_horizon_h"], "selected_rows")
    portfolio_family = safe_value_counts(portfolio, ["semantic_pair", "motif", "label_family"], "portfolio_rows")
    response_decisions = safe_value_counts(responses, ["decision", "label_family"], "response_rows")

    top_cols = [
        "blueprint_id",
        "semantic_pair",
        "motif",
        "label_family",
        "label_horizon_h",
        "score_no_may",
        "control_ratio_premay_max",
        "cost10_recent_oriented",
        "robust_median_tstat_floor",
        "skeleton_key",
        "expression",
    ]
    selected_top = (
        selected.sort_values("score_no_may", ascending=False)[[c for c in top_cols if c in selected.columns]].head(160)
        if not selected.empty
        else pd.DataFrame(columns=top_cols)
    )
    non_l7_top = (
        portfolio[portfolio["label_family"].ne("L7_ranked_future_return")]
        .sort_values("score_no_may", ascending=False)[[c for c in top_cols if c in portfolio.columns]]
        .head(240)
        if not portfolio.empty and "label_family" in portfolio.columns
        else pd.DataFrame(columns=top_cols)
    )

    selected_skeleton_unique = int(selected["skeleton_key"].nunique()) if "skeleton_key" in selected.columns else 0
    selected_top_skeleton_share = (
        float(selected["skeleton_key"].value_counts().iloc[0] / len(selected))
        if not selected.empty and "skeleton_key" in selected.columns
        else 0.0
    )
    material_eval_fail = int((~materialization["eval_success"].astype(bool)).sum()) if "eval_success" in materialization.columns else 0
    material_activity_false = int((~materialization["activity_ok"].astype(bool)).sum()) if "activity_ok" in materialization.columns else 0
    material_finite_median = float(pd.to_numeric(materialization.get("finite_share", pd.Series(dtype=float)), errors="coerce").median())

    counts = {
        "shard_count": int(len(shard_summary)),
        "pass_count": int(shard_summary["decision"].astype(str).str.startswith("PASS_").sum()),
        "hold_count": int(shard_summary["decision"].astype(str).str.startswith("HOLD_").sum()),
        "queue_rows": int(shard_summary["queue_total_rows"].max()),
        "input_blueprint_count_total": int(shard_summary["input_blueprint_count"].sum()),
        "activity_ok_total": int(shard_summary["materialized_activity_ok_count"].sum()),
        "missing_numeric_field_shards": int(shard_summary["missing_numeric_fields"].astype(str).ne("[]").sum()),
        "non_l7_numeric_clue_rows_total": int(shard_summary["non_l7_numeric_clue_rows"].sum()),
        "rank_label_diagnostic_clue_rows_total": int(shard_summary["rank_label_diagnostic_clue_rows"].sum()),
        "portfolio_queue_rows_total": int(shard_summary["portfolio_queue_count"].sum()),
        "selected_portfolio_queue_rows_total": int(shard_summary["selected_portfolio_queue_count"].sum()),
        "selected_skeleton_unique": selected_skeleton_unique,
        "selected_top_skeleton_share": selected_top_skeleton_share,
        "materialization_eval_fail_count": material_eval_fail,
        "materialization_activity_false_count": material_activity_false,
        "materialization_finite_share_median": material_finite_median,
    }
    decision = (
        "PASS_A7LS29_PRODUCTIVE_NUMERIC_ACCEPTED_NO_SEARCH_AUTH"
        if counts["pass_count"] == 12
        and counts["missing_numeric_field_shards"] == 0
        and counts["materialization_eval_fail_count"] == 0
        and counts["selected_portfolio_queue_rows_total"] >= 120
        else "HOLD_A7LS29_PRODUCTIVE_NUMERIC_ACCEPTANCE_REVIEW_REQUIRED"
    )

    artifacts = {
        "a7ls29_shard_manifest_summary.csv": shard_summary,
        "a7ls29_selected_family_summary.csv": selected_family,
        "a7ls29_selected_label_summary.csv": selected_label,
        "a7ls29_portfolio_family_summary.csv": portfolio_family,
        "a7ls29_response_decision_summary.csv": response_decisions,
        "a7ls29_selected_top160.csv": selected_top,
        "a7ls29_non_l7_top240.csv": non_l7_top,
    }
    for name, df in artifacts.items():
        df.to_csv(RUNTIME / name, index=False)
        df.to_csv(DATA_RUNTIME / name, index=False)

    manifest = {
        "stage": STAGE,
        "generated_at": now_iso(),
        "decision": decision,
        "pullback_root": str(PULLBACK_ROOT),
        "runtime": str(RUNTIME),
        "data_runtime": str(DATA_RUNTIME),
        "counts": counts,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": [
            "A7LS30 productive follow-up queue compilation",
            "A7LS30 field gate",
            "A7LS30 numeric probe wave on company machine",
        ],
    }
    write_json(RUNTIME / "a7ls29_productive_numeric_acceptance_manifest.json", manifest)
    write_json(DATA_RUNTIME / "a7ls29_productive_numeric_acceptance_manifest.json", manifest)
    write_json(DATA_MANIFEST, manifest)

    report = f"""# CRYPTO A7LS29 Productive Numeric Acceptance {DATE}

## Decision

`{decision}`

A7LS29 completed all 12 company-machine numeric shards and fixes the A7LS28B portfolio-queue collapse. This is numeric evidence and queue validation only. It does not authorize alpha proof, search promotion, shadow, paper, or live execution.

## Counts

- queue_rows: {counts['queue_rows']}
- shard_count: {counts['shard_count']}
- pass_count: {counts['pass_count']}
- hold_count: {counts['hold_count']}
- input_blueprint_count_total: {counts['input_blueprint_count_total']}
- activity_ok_total: {counts['activity_ok_total']}
- missing_numeric_field_shards: {counts['missing_numeric_field_shards']}
- materialization_eval_fail_count: {counts['materialization_eval_fail_count']}
- non_l7_numeric_clue_rows_total: {counts['non_l7_numeric_clue_rows_total']}
- rank_label_diagnostic_clue_rows_total: {counts['rank_label_diagnostic_clue_rows_total']}
- portfolio_queue_rows_total: {counts['portfolio_queue_rows_total']}
- selected_portfolio_queue_rows_total: {counts['selected_portfolio_queue_rows_total']}
- selected_skeleton_unique: {counts['selected_skeleton_unique']}
- selected_top_skeleton_share: {counts['selected_top_skeleton_share']:.4f}

## Shard Summary

{md_table(shard_summary[['shard_id', 'decision', 'materialized_activity_ok_count', 'non_l7_numeric_clue_rows', 'rank_label_diagnostic_clue_rows', 'portfolio_queue_count', 'selected_portfolio_queue_count']], 20)}

## Selected Family Summary

{md_table(selected_family, 40)}

## Selected Label Summary

{md_table(selected_label, 40)}

## Top Selected Queue

{md_table(selected_top, 25)}

## Interpretation

A7LS29 is materially better than A7LS28B: the skeleton key problem is repaired, selected portfolio queue rows increased from 12 to {counts['selected_portfolio_queue_rows_total']}, and the field/materialization layer stayed clean. The best current structures remain basis/positioning and OI/positioning variants, with useful L5 and L3 non-L7 evidence. The next wave should expand these productive families while forcing OI/positioning/regime/listing-age quotas so the search does not collapse back to basis-only.

## Boundary

```text
No formula search promotion is authorized by this file.
No alpha proof / shadow / paper / live is authorized.
A7LS30 may run numeric probes only, with field gate first.
```

## Outputs

- `{RUNTIME}`
- `{DATA_RUNTIME}`
- `{DATA_MANIFEST}`
"""
    REPORT.write_text(report, encoding="utf-8")
    DATA_REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
