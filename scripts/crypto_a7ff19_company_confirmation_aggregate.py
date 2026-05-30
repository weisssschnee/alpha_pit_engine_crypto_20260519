from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff19_company_numeric_confirmation_aggregate"
REPORT = REPO / "reports" / "CRYPTO_A7FF19_COMPANY_NUMERIC_CONFIRMATION_AGGREGATE_20260530.md"
SHARD_ROOT = REPO / "runtime"
SHARD_COUNT = 2


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


def shard_dir(i: int) -> Path:
    return SHARD_ROOT / f"a7ff19_company_numeric_confirmation_shard_{i:02d}"


def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    shard_rows: list[dict[str, Any]] = []
    response_frames: list[pd.DataFrame] = []
    selected_frames: list[pd.DataFrame] = []
    decision_frames: list[pd.DataFrame] = []
    missing: list[str] = []

    for i in range(SHARD_COUNT):
        sid = f"{i:02d}"
        prefix = f"a7ff19s{sid}"
        root = shard_dir(i)
        manifest_path = root / f"{prefix}_manifest.json"
        manifest = read_json(manifest_path)
        if not manifest:
            missing.append(str(manifest_path))
            continue
        shard_rows.append(
            {
                "shard": sid,
                "stage": manifest.get("stage", ""),
                "decision": manifest.get("decision", ""),
                "input_blueprint_count": manifest.get("input_blueprint_count", 0),
                "queue_path": manifest.get("queue_path", ""),
                "queue_offset": manifest.get("queue_offset", 0),
                "queue_limit": manifest.get("queue_limit", 0),
                "materialized_activity_ok_count": manifest.get("materialized_activity_ok_count", 0),
                "label_response_rows": manifest.get("label_response_rows", 0),
                "non_l7_numeric_clue_rows": manifest.get("non_l7_numeric_clue_rows", 0),
                "rank_label_diagnostic_clue_rows": manifest.get("rank_label_diagnostic_clue_rows", 0),
                "portfolio_queue_count": manifest.get("portfolio_queue_count", 0),
                "selected_portfolio_queue_count": manifest.get("selected_portfolio_queue_count", 0),
                "uses_may": manifest.get("uses_may", False),
                "authorizes_search": manifest.get("authorizes_search", False),
            }
        )
        for target, frames in [
            (root / f"{prefix}_label_response_metrics.csv", response_frames),
            (root / f"{prefix}_selected_portfolio_queue.csv", selected_frames),
            (root / f"{prefix}_decision_counts.csv", decision_frames),
        ]:
            df = load_csv(target)
            if not df.empty:
                df.insert(0, "shard", sid)
                frames.append(df)

    shards = pd.DataFrame(shard_rows)
    responses = pd.concat(response_frames, ignore_index=True) if response_frames else pd.DataFrame()
    selected = pd.concat(selected_frames, ignore_index=True) if selected_frames else pd.DataFrame()
    decisions = pd.concat(decision_frames, ignore_index=True) if decision_frames else pd.DataFrame()

    clues = responses[responses.get("decision", pd.Series(dtype=str)).astype(str).str.contains("NUMERIC_CLUE", na=False)].copy() if not responses.empty else pd.DataFrame()
    non_l7 = clues[~clues.get("label_family", pd.Series(dtype=str)).eq("L7_ranked_future_return")].copy() if not clues.empty else pd.DataFrame()
    label_summary = (
        non_l7.groupby(["label_family", "label_horizon_h"], dropna=False)
        .agg(
            clue_rows=("blueprint_id", "count"),
            unique_blueprints=("blueprint_id", "nunique"),
            median_control_ratio=("control_ratio_premay_max", "median"),
            median_cost2=("cost2_recent_oriented", "median"),
            median_cost5=("cost5_recent_oriented", "median"),
            median_cost10=("cost10_recent_oriented", "median"),
        )
        .reset_index()
        .sort_values(["label_family", "label_horizon_h"])
        if not non_l7.empty
        else pd.DataFrame()
    )
    semantic_summary = (
        non_l7.groupby(["semantic_pair", "label_family", "label_horizon_h"], dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        if not non_l7.empty
        else pd.DataFrame(columns=["semantic_pair", "label_family", "label_horizon_h", "count"])
    )

    complete = len(shard_rows) == SHARD_COUNT and not missing
    total_non_l7 = int(shards["non_l7_numeric_clue_rows"].sum()) if not shards.empty else 0
    total_selected = int(shards["selected_portfolio_queue_count"].sum()) if not shards.empty else 0
    label_families = int(non_l7["label_family"].nunique()) if not non_l7.empty else 0
    decision = (
        "PASS_A7FF19_COMPANY_NUMERIC_CONFIRMATION_AGGREGATE_BUILT"
        if complete and total_non_l7 > 0 and total_selected > 0 and label_families >= 3
        else "HOLD_A7FF19_COMPANY_NUMERIC_CONFIRMATION_INCOMPLETE_OR_EMPTY"
    )
    manifest = {
        "stage": "A7FF-19-COMPANY-NUMERIC-CONFIRMATION-AGGREGATE",
        "generated_at": now_utc(),
        "decision": decision,
        "shard_count_expected": SHARD_COUNT,
        "shard_count_complete": len(shard_rows),
        "missing_manifests": missing,
        "total_input_blueprints": int(shards["input_blueprint_count"].sum()) if not shards.empty else 0,
        "total_materialized_activity_ok": int(shards["materialized_activity_ok_count"].sum()) if not shards.empty else 0,
        "total_label_response_rows": int(shards["label_response_rows"].sum()) if not shards.empty else 0,
        "total_non_l7_numeric_clue_rows": total_non_l7,
        "total_rank_label_diagnostic_clue_rows": int(shards["rank_label_diagnostic_clue_rows"].sum()) if not shards.empty else 0,
        "total_portfolio_queue_count": int(shards["portfolio_queue_count"].sum()) if not shards.empty else 0,
        "total_selected_portfolio_queue_count": total_selected,
        "non_l7_label_families": label_families,
        "uses_may": False,
        "executes_generation": False,
        "executes_search": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }

    shards.to_csv(RUNTIME / "a7ff19_shard_summary.csv", index=False)
    responses.to_csv(RUNTIME / "a7ff19_label_response_metrics_all_shards.csv", index=False)
    label_summary.to_csv(RUNTIME / "a7ff19_label_summary.csv", index=False)
    semantic_summary.to_csv(RUNTIME / "a7ff19_non_l7_clue_summary.csv", index=False)
    selected.to_csv(RUNTIME / "a7ff19_selected_portfolio_queue_all_shards.csv", index=False)
    decisions.to_csv(RUNTIME / "a7ff19_decision_counts_all_shards.csv", index=False)
    write_json(RUNTIME / "a7ff19_manifest.json", manifest)

    report = f"""# CRYPTO A7FF-19 COMPANY NUMERIC CONFIRMATION AGGREGATE

Generated: {manifest["generated_at"]}

## Decision

`{decision}`

A7FF-19 aggregates company-machine numeric confirmation shards over the A7FF-19 external-selector execution queue. It is bounded numeric confirmation, not formula generation, alpha search, alpha proof, shadow, paper, or live execution.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Shards

{md_table(shards)}

## Non-L7 Label Summary

{md_table(label_summary, 120)}

## Non-L7 Semantic / Label Summary

{md_table(semantic_summary, 120)}

## Boundary

```text
No May/post-selection stress is used in scoring or authorization.
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
```
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
