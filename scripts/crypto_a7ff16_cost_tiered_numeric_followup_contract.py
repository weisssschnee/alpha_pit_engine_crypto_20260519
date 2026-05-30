from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff16_cost_tiered_numeric_followup_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FF16_COST_TIERED_NUMERIC_FOLLOWUP_CONTRACT_20260530.md"

A7FF15_MANIFEST = REPO / "runtime" / "a7ff15_cost_tiered_balanced_followup" / "a7ff15_manifest.json"
A7FF15_QUEUE = REPO / "runtime" / "a7ff15_cost_tiered_balanced_followup" / "a7ff15_cost_tiered_selected_queue.csv"

REMOTE_REPO = r"D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote"
REMOTE_PYTHON = r"D:\HermesWorker\venvs\phase3z33\Scripts\python.exe"
REMOTE_DATA_ROOT = r"D:\HermesWorker\GDrive\AlphaFactory_CryptoData"
REMOTE_BASE_PANEL = r"D:\HermesWorker\GDrive\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_20260527"


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


def join_unique(values: pd.Series) -> str:
    return ";".join(sorted({str(x) for x in values.dropna().tolist()}))


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    a7ff15 = read_json(A7FF15_MANIFEST)
    if not a7ff15.get("authorizes_a7ff16_cost_tiered_numeric_followup"):
        raise SystemExit("A7FF-15 does not authorize A7FF-16 cost-tiered numeric follow-up")
    selected = pd.read_csv(A7FF15_QUEUE)
    if selected.empty:
        raise SystemExit("empty A7FF-15 selected queue")

    best = (
        selected.sort_values(
            ["cost_tier_rank", "followup_score", "control_ratio_premay_max", "blueprint_id"],
            ascending=[False, False, True, True],
        )
        .drop_duplicates("blueprint_id", keep="first")
        .copy()
    )
    meta = (
        selected.groupby("blueprint_id", dropna=False)
        .agg(
            a7ff15_selected_rows=("blueprint_id", "count"),
            a7ff15_label_targets=("label_family", join_unique),
            a7ff15_horizon_targets=("label_horizon_h", lambda s: ";".join(map(str, sorted(set(s.dropna().astype(int).tolist()))))),
            a7ff15_best_cost_tier_rank=("cost_tier_rank", "max"),
            a7ff15_best_followup_score=("followup_score", "max"),
            a7ff15_any_strict_cost10=("cost_tier", lambda s: bool((s == "strict_cost10").any())),
            a7ff15_any_cost5_or_better=("cost_tier", lambda s: bool(s.isin(["strict_cost10", "cost5_followup"]).any())),
        )
        .reset_index()
    )
    execution_queue = best.merge(meta, on="blueprint_id", how="left")
    required_cols = [
        "blueprint_id",
        "expression",
        "semantic_pair",
        "motif",
        "skeleton_key",
        "a7ff15_selected_rows",
        "a7ff15_label_targets",
        "a7ff15_horizon_targets",
        "a7ff15_best_cost_tier_rank",
        "a7ff15_best_followup_score",
        "a7ff15_any_strict_cost10",
        "a7ff15_any_cost5_or_better",
    ]
    execution_queue = execution_queue[required_cols].sort_values(
        ["a7ff15_best_cost_tier_rank", "a7ff15_best_followup_score", "blueprint_id"],
        ascending=[False, False, True],
    )

    label_target_summary = (
        selected.groupby(["label_family", "cost_tier"], dropna=False)
        .agg(rows=("blueprint_id", "count"), unique_blueprints=("blueprint_id", "nunique"))
        .reset_index()
        .sort_values(["label_family", "cost_tier"])
    )
    exec_semantic_summary = (
        execution_queue.groupby("semantic_pair", dropna=False)
        .agg(execution_blueprints=("blueprint_id", "count"))
        .reset_index()
        .sort_values("execution_blueprints", ascending=False)
    )
    exec_motif_summary = (
        execution_queue.groupby("motif", dropna=False)
        .agg(execution_blueprints=("blueprint_id", "count"))
        .reset_index()
        .sort_values("execution_blueprints", ascending=False)
    )

    execution_count = int(len(execution_queue))
    top_semantic_share = float(execution_queue["semantic_pair"].value_counts(normalize=True).max()) if execution_count else 0.0
    top_motif_share = float(execution_queue["motif"].value_counts(normalize=True).max()) if execution_count else 0.0
    strict_blueprints = int(execution_queue["a7ff15_any_strict_cost10"].sum())
    cost5_blueprints = int(execution_queue["a7ff15_any_cost5_or_better"].sum())
    decision = (
        "PASS_A7FF16_COST_TIERED_NUMERIC_FOLLOWUP_CONTRACT_READY_FOR_COMPANY_EXECUTION"
        if execution_count >= 90
        and top_semantic_share <= 0.35
        and top_motif_share <= 0.35
        and strict_blueprints >= 30
        and cost5_blueprints >= 70
        else "HOLD_A7FF16_COST_TIERED_NUMERIC_FOLLOWUP_CONTRACT_INSUFFICIENT"
    )

    runner_config = {
        "remote_repo": REMOTE_REPO,
        "remote_python": REMOTE_PYTHON,
        "remote_data_root": REMOTE_DATA_ROOT,
        "remote_base_panel": REMOTE_BASE_PANEL,
        "queue_local_path": str((RUNTIME / "a7ff16_execution_queue.csv").relative_to(REPO)),
        "queue_remote_path": r"runtime\a7ff16_cost_tiered_numeric_followup_contract\a7ff16_execution_queue.csv",
        "recommended_shard_count": 2,
        "recommended_shard_size": 48,
        "recommended_max_parallel": 2,
        "stage_prefix": "A7FF-16S",
        "file_prefix": "a7ff16s",
        "runner_script": "scripts\\crypto_a7ff8_expanded_numeric_probe.py",
        "materialize_cap_per_shard": 48,
        "fast_numeric_cap_per_shard": 48,
        "portfolio_cap_per_shard": 128,
    }

    manifest = {
        "stage": "A7FF-16-COST-TIERED-NUMERIC-FOLLOWUP-CONTRACT",
        "generated_at": now_utc(),
        "decision": decision,
        "source_a7ff15_decision": a7ff15.get("decision", ""),
        "a7ff15_selected_rows": int(len(selected)),
        "execution_blueprints": execution_count,
        "strict_cost10_execution_blueprints": strict_blueprints,
        "cost5_or_better_execution_blueprints": cost5_blueprints,
        "top_semantic_share": top_semantic_share,
        "top_motif_share": top_motif_share,
        "uses_may": False,
        "executes_generation": False,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_company_numeric_execution": decision.startswith("PASS"),
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }

    execution_queue.to_csv(RUNTIME / "a7ff16_execution_queue.csv", index=False)
    label_target_summary.to_csv(RUNTIME / "a7ff16_label_target_summary.csv", index=False)
    exec_semantic_summary.to_csv(RUNTIME / "a7ff16_execution_semantic_summary.csv", index=False)
    exec_motif_summary.to_csv(RUNTIME / "a7ff16_execution_motif_summary.csv", index=False)
    write_json(RUNTIME / "a7ff16_company_runner_config.json", runner_config)
    write_json(RUNTIME / "a7ff16_manifest.json", manifest)

    report = f"""# CRYPTO A7FF-16 COST-TIERED NUMERIC FOLLOWUP CONTRACT

Generated: {manifest["generated_at"]}

## Decision

`{decision}`

A7FF-16 converts the A7FF-15 label-target queue into a unique-blueprint execution queue for company-machine numeric confirmation. It does not execute replay in this stage; it only authorizes a bounded company run through the existing A7FF-8 numeric runner.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Runner Config

```json
{json.dumps(runner_config, indent=2, sort_keys=True)}
```

## Label Target Summary

{md_table(label_target_summary, 80)}

## Execution Semantic Summary

{md_table(exec_semantic_summary, 40)}

## Execution Motif Summary

{md_table(exec_motif_summary, 40)}

## Execution Queue Preview

{md_table(execution_queue, 80)}

## Boundary

- Uses May: `false`
- Executes generation: `false`
- Executes replay in this stage: `false`
- Executes search: `false`
- Authorizes company numeric confirmation only if decision PASS: `{manifest["authorizes_company_numeric_execution"]}`
- Authorizes alpha proof / shadow / paper / live: `false`
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
