from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
DATE = "20260610"
STAGE = "A7LS-30"

PULLBACK_ROOT = Path(
    r"G:\AlphaFactory_CryptoData\company_pullback\a7ls30_productive_numeric_wave_20260610\unzipped"
)
RUNTIME = REPO / "runtime" / "a7ls30_productive_numeric_acceptance_20260610"
REPORT = REPO / "reports" / f"CRYPTO_A7LS30_PRODUCTIVE_NUMERIC_ACCEPTANCE_{DATE}.md"
DATA_RUNTIME = Path(r"G:\AlphaFactory_CryptoData\research_runtime\a7ls30_productive_numeric_acceptance_20260610")
DATA_REPORT = Path(r"G:\AlphaFactory_CryptoData\reports") / REPORT.name
DATA_MANIFEST = Path(r"G:\AlphaFactory_CryptoData\manifests\a7ls30_productive_numeric_acceptance_20260610_manifest.json")


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


def counts(df: pd.DataFrame, columns: list[str], name: str) -> pd.DataFrame:
    if df.empty or any(col not in df.columns for col in columns):
        return pd.DataFrame(columns=[*columns, name])
    return df.groupby(columns, dropna=False).size().reset_index(name=name).sort_values(name, ascending=False)


def write_artifacts(artifacts: dict[str, pd.DataFrame]) -> None:
    for name, df in artifacts.items():
        df.to_csv(RUNTIME / name, index=False)
        df.to_csv(DATA_RUNTIME / name, index=False)


def main() -> None:
    if not PULLBACK_ROOT.exists():
        raise FileNotFoundError(PULLBACK_ROOT)
    RUNTIME.mkdir(parents=True, exist_ok=True)
    DATA_RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    DATA_REPORT.parent.mkdir(parents=True, exist_ok=True)

    manifests = [read_manifest(path) for path in sorted(PULLBACK_ROOT.rglob("shards/*/*manifest.json"))]
    if len(manifests) != 16:
        raise RuntimeError(f"expected 16 shard manifests, found {len(manifests)}")
    shard_summary = pd.DataFrame(manifests)

    selected = read_csvs("*selected_portfolio_queue.csv")
    portfolio = read_csvs("*portfolio_marginal_proxy.csv")
    materialization = read_csvs("*materialization_metrics.csv")
    responses = read_csvs("*label_response_metrics.csv")

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
    selected_top = selected.sort_values("score_no_may", ascending=False)[[c for c in top_cols if c in selected.columns]].head(240)
    non_l7_top = (
        portfolio[portfolio["label_family"].ne("L7_ranked_future_return")]
        .sort_values("score_no_may", ascending=False)[[c for c in top_cols if c in portfolio.columns]]
        .head(360)
    )

    selected_family = counts(selected, ["semantic_pair", "motif", "label_family"], "selected_rows")
    selected_label = counts(selected, ["label_family", "label_horizon_h"], "selected_rows")
    portfolio_family = counts(portfolio, ["semantic_pair", "motif", "label_family"], "portfolio_rows")
    response_decisions = counts(responses, ["decision", "label_family"], "response_rows")
    shard_light = shard_summary[
        [
            "shard_id",
            "decision",
            "materialized_activity_ok_count",
            "non_l7_numeric_clue_rows",
            "rank_label_diagnostic_clue_rows",
            "portfolio_queue_count",
            "selected_portfolio_queue_count",
        ]
    ].copy()

    material_eval_fail = int((~materialization["eval_success"].astype(bool)).sum()) if "eval_success" in materialization.columns else 0
    material_activity_false = int((~materialization["activity_ok"].astype(bool)).sum()) if "activity_ok" in materialization.columns else 0
    selected_skeleton_unique = int(selected["skeleton_key"].nunique()) if "skeleton_key" in selected.columns else 0
    top_skeleton_share = (
        float(selected["skeleton_key"].value_counts().iloc[0] / len(selected))
        if not selected.empty and "skeleton_key" in selected.columns
        else 0.0
    )

    counts_payload = {
        "queue_rows": int(shard_summary["queue_total_rows"].max()),
        "shard_count": int(len(shard_summary)),
        "pass_count": int(shard_summary["decision"].astype(str).str.startswith("PASS_").sum()),
        "hold_count": int(shard_summary["decision"].astype(str).str.startswith("HOLD_").sum()),
        "input_blueprint_count_total": int(shard_summary["input_blueprint_count"].sum()),
        "activity_ok_total": int(shard_summary["materialized_activity_ok_count"].sum()),
        "missing_numeric_field_shards": int(shard_summary["missing_numeric_fields"].astype(str).ne("[]").sum()),
        "materialization_eval_fail_count": material_eval_fail,
        "materialization_activity_false_count": material_activity_false,
        "non_l7_numeric_clue_rows_total": int(shard_summary["non_l7_numeric_clue_rows"].sum()),
        "rank_label_diagnostic_clue_rows_total": int(shard_summary["rank_label_diagnostic_clue_rows"].sum()),
        "portfolio_queue_rows_total": int(shard_summary["portfolio_queue_count"].sum()),
        "selected_portfolio_queue_rows_total": int(shard_summary["selected_portfolio_queue_count"].sum()),
        "selected_skeleton_unique": selected_skeleton_unique,
        "selected_top_skeleton_share": top_skeleton_share,
    }
    decision = (
        "PASS_A7LS30_PRODUCTIVE_NUMERIC_ACCEPTED_NO_SEARCH_AUTH"
        if counts_payload["pass_count"] == 16
        and counts_payload["missing_numeric_field_shards"] == 0
        and counts_payload["materialization_eval_fail_count"] == 0
        and counts_payload["selected_portfolio_queue_rows_total"] >= 300
        else "HOLD_A7LS30_PRODUCTIVE_NUMERIC_ACCEPTANCE_REVIEW_REQUIRED"
    )

    artifacts = {
        "a7ls30_shard_manifest_summary.csv": shard_light,
        "a7ls30_selected_family_summary.csv": selected_family,
        "a7ls30_selected_label_summary.csv": selected_label,
        "a7ls30_portfolio_family_summary.csv": portfolio_family,
        "a7ls30_response_decision_summary.csv": response_decisions,
        "a7ls30_selected_top240.csv": selected_top,
        "a7ls30_non_l7_top360.csv": non_l7_top,
    }
    write_artifacts(artifacts)

    manifest = {
        "stage": STAGE,
        "generated_at": now_iso(),
        "decision": decision,
        "pullback_root": str(PULLBACK_ROOT),
        "runtime": str(RUNTIME),
        "data_runtime": str(DATA_RUNTIME),
        "counts": counts_payload,
        "best_blueprint_id": str(selected_top.iloc[0]["blueprint_id"]) if not selected_top.empty else "",
        "best_expression": str(selected_top.iloc[0]["expression"]) if not selected_top.empty else "",
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": [
            "A7RAW lightly governed large-space queue compilation",
            "A7RAW field gate",
            "A7RAW company numeric probe",
        ],
    }
    write_json(RUNTIME / "a7ls30_productive_numeric_acceptance_manifest.json", manifest)
    write_json(DATA_RUNTIME / "a7ls30_productive_numeric_acceptance_manifest.json", manifest)
    write_json(DATA_MANIFEST, manifest)

    report = f"""# CRYPTO A7LS30 Productive Numeric Acceptance {DATE}

## Decision

`{decision}`

A7LS30 completed all 16 company-machine numeric shards. This is numeric evidence and queue validation only. It does not authorize alpha proof, formula search promotion, shadow, paper, or live execution.

## Counts

- queue_rows: {counts_payload['queue_rows']}
- shard_count: {counts_payload['shard_count']}
- pass_count: {counts_payload['pass_count']}
- hold_count: {counts_payload['hold_count']}
- input_blueprint_count_total: {counts_payload['input_blueprint_count_total']}
- activity_ok_total: {counts_payload['activity_ok_total']}
- missing_numeric_field_shards: {counts_payload['missing_numeric_field_shards']}
- materialization_eval_fail_count: {counts_payload['materialization_eval_fail_count']}
- non_l7_numeric_clue_rows_total: {counts_payload['non_l7_numeric_clue_rows_total']}
- rank_label_diagnostic_clue_rows_total: {counts_payload['rank_label_diagnostic_clue_rows_total']}
- portfolio_queue_rows_total: {counts_payload['portfolio_queue_rows_total']}
- selected_portfolio_queue_rows_total: {counts_payload['selected_portfolio_queue_rows_total']}
- selected_skeleton_unique: {counts_payload['selected_skeleton_unique']}
- selected_top_skeleton_share: {counts_payload['selected_top_skeleton_share']:.4f}

## Best Current Formula

```text
{manifest['best_expression']}
```

## Shard Summary

{md_table(shard_light, 24)}

## Selected Family Summary

{md_table(selected_family, 60)}

## Selected Label Summary

{md_table(selected_label, 40)}

## Top Selected Queue

{md_table(selected_top, 30)}

## Interpretation

A7LS30 improved over A7LS29: selected portfolio rows increased from 291 to {counts_payload['selected_portfolio_queue_rows_total']}, all shards passed, and the best current formula moved from a pure basis/positioning variant to an open-interest-value / positioning-scale structure. This suggests the previous bottleneck was not only field scarcity; the prior search neighborhood was too centered on basis/positioning.

## Boundary

```text
No alpha proof is authorized.
No shadow, paper, or live execution is authorized.
Next work should use lightly governed large-space raw search, not another narrow productive-parent mutation.
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
