from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff55r5_repaired_atlas_numeric_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FF55R5_REPAIRED_ATLAS_NUMERIC_CONTRACT_20260531.md"
A7FF55R4 = REPO / "runtime" / "a7ff55r4_repaired_atlas_coverage_audit" / "a7ff55r4_manifest.json"
QUEUE = REPO / "runtime" / "a7ff55r3_repaired_atlas_dry_generation" / "a7ff55r3_repaired_materialization_queue.csv"


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
    m55r4 = read_json(A7FF55R4)
    if m55r4.get("decision") != "PASS_A7FF55R4_REPAIRED_ATLAS_COVERAGE_READY_FOR_NUMERIC_CONTRACT":
        raise SystemExit(f"A7FF-55R4 is not ready: {m55r4.get('decision')}")
    queue = pd.read_csv(QUEUE)
    queue_summary = (
        queue.groupby(["semantic_pair", "motif"], dropna=False)
        .size()
        .reset_index(name="queue_rows")
        .sort_values("queue_rows", ascending=False)
    )
    shard_plan = (
        queue.groupby("company_shard", dropna=False)
        .agg(
            queue_rows=("blueprint_id", "count"),
            semantic_pairs=("semantic_pair", "nunique"),
            motifs=("motif", "nunique"),
        )
        .reset_index()
        .sort_values("company_shard")
    )
    label_plan = pd.DataFrame(
        [
            {
                "label_family": "L0_raw_forward_return",
                "role": "primary",
                "horizons": "1h,4h,8h,24h",
                "promotion_use": "raw return sanity; cannot pass alone if control dominated",
            },
            {
                "label_family": "L1_cross_sectional_relative_return",
                "role": "primary",
                "horizons": "1h,4h,8h,24h",
                "promotion_use": "primary cross-sectional economics; required representation",
            },
            {
                "label_family": "L3_liquidity_tier_relative_return",
                "role": "primary",
                "horizons": "1h,4h,8h,24h",
                "promotion_use": "liquidity-tier robustness; required representation",
            },
            {
                "label_family": "L5_vol_adjusted_return",
                "role": "blocked_this_wave",
                "horizons": "none",
                "promotion_use": "blocked to prevent previous L5 absorption",
            },
            {
                "label_family": "L7_ranked_future_return",
                "role": "blocked_this_wave",
                "horizons": "none",
                "promotion_use": "diagnostic only, not part of repaired primary wave",
            },
        ]
    )
    execution_env = {
        "A7FF8_STAGE": "A7FF-55R5E",
        "A7FF8_FILE_PREFIX": "a7ff55r5e",
        "A7FF8_RUNTIME": "runtime/a7ff55r5e_repaired_atlas_numeric_execution",
        "A7FF8_REPORT": "reports/CRYPTO_A7FF55R5E_REPAIRED_ATLAS_NUMERIC_EXECUTION_20260531.md",
        "A7FF8_QUEUE_PATH": "runtime/a7ff55r3_repaired_atlas_dry_generation/a7ff55r3_repaired_materialization_queue.csv",
        "A7FF8_AUTH_MANIFEST": "runtime/a7ff55r5_repaired_atlas_numeric_contract/a7ff55r5_manifest.json",
        "A7FF8_AUTH_DECISION": "PASS_A7FF55R5_REPAIRED_ATLAS_NUMERIC_CONTRACT_READY_FOR_EXECUTION",
        "A7FF8_PLAN_PATH": "runtime/a7ff55r5_repaired_atlas_numeric_contract/a7ff55r5_numeric_plan.json",
        "A7FF8_LABELS": "L0_raw_forward_return,L1_cross_sectional_relative_return,L3_liquidity_tier_relative_return",
        "A7FF8_WRITE_CONTROL_DETAIL": "0",
        "A7FF8_MATERIALIZE_CAP": "2400",
        "A7FF8_FAST_NUMERIC_CAP": "2400",
        "A7FF8_PORTFOLIO_CAP": "256",
        "A7FF8_QUEUE_LIMIT": "0",
        "A7FF8_QUEUE_OFFSET": "0",
    }
    numeric_plan = {
        "stage": "A7FF-55R5E",
        "queue_rows": int(len(queue)),
        "labels": [
            "L0_raw_forward_return",
            "L1_cross_sectional_relative_return",
            "L3_liquidity_tier_relative_return",
        ],
        "horizons": ["1h", "4h", "8h", "24h"],
        "expected_label_response_rows": int(len(queue) * 3 * 4),
        "runner": "scripts/crypto_a7ff8_expanded_numeric_probe.py",
        "execution_mode": "bounded_numeric_only_no_replay_no_search",
        "may_policy": "not used in scoring or authorization",
        "hard_gates": {
            "eval_failure_count": 0,
            "missing_field_count": 0,
            "non_l7_numeric_clue_rows": "> 0",
            "selected_portfolio_queue_count": ">= 24",
            "selected_semantic_pair_count": ">= 5",
            "selected_motif_count": ">= 5",
            "control_ratio_for_candidate": "< 0.80",
        },
    }
    queue_summary.to_csv(RUNTIME / "a7ff55r5_queue_summary.csv", index=False)
    shard_plan.to_csv(RUNTIME / "a7ff55r5_shard_plan.csv", index=False)
    label_plan.to_csv(RUNTIME / "a7ff55r5_label_plan.csv", index=False)
    write_json(RUNTIME / "a7ff55r5_execution_env.json", execution_env)
    write_json(RUNTIME / "a7ff55r5_numeric_plan.json", numeric_plan)
    manifest = {
        "stage": "A7FF-55R5",
        "generated_at": now_utc(),
        "decision": "PASS_A7FF55R5_REPAIRED_ATLAS_NUMERIC_CONTRACT_READY_FOR_EXECUTION",
        "source_stage": "A7FF-55R4",
        "source_decision": m55r4.get("decision"),
        "queue_rows": int(len(queue)),
        "semantic_pair_count": int(queue["semantic_pair"].nunique()),
        "motif_count": int(queue["motif"].nunique()),
        "expected_label_response_rows": numeric_plan["expected_label_response_rows"],
        "labels": numeric_plan["labels"],
        "executes_numeric": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_numeric_execution": True,
        "authorizes_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-55R5E repaired atlas numeric execution",
    }
    write_json(RUNTIME / "a7ff55r5_manifest.json", manifest)
    report = f"""# CRYPTO A7FF-55R5 REPAIRED ATLAS NUMERIC CONTRACT

Generated: {manifest["generated_at"]}

## Decision

`{manifest["decision"]}`

A7FF-55R5 defines the bounded primary-label numeric execution over the repaired 2400-row atlas queue. It does not execute numeric evaluation, replay, or search.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Label Plan

{md_table(label_plan, 20)}

## Queue Summary

{md_table(queue_summary, 80)}

## Shard Plan

{md_table(shard_plan, 40)}

## Execution Environment

```json
{json.dumps(execution_env, indent=2, sort_keys=True)}
```

## Boundary

```text
numeric execution: false
replay executed: false
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
