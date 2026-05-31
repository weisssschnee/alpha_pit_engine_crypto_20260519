from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore6_materialization_preflight_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE6_MATERIALIZATION_PREFLIGHT_CONTRACT_20260601.md"
A7FFCORE5 = REPO / "runtime" / "a7ffcore5_gate_native_generation_dryrun" / "a7ffcore5_manifest.json"
QUEUE = REPO / "runtime" / "a7ffcore5_gate_native_generation_dryrun" / "a7ffcore5_gate_native_candidate_queue.csv"


SHARD_SIZE = 256


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


def split_fields(series: pd.Series) -> set[str]:
    fields: set[str] = set()
    for value in series.fillna("").astype(str):
        fields.update(part for part in value.split(";") if part)
    return fields


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    core5 = read_json(A7FFCORE5)
    if core5.get("decision") != "PASS_A7FFCORE5_GATE_NATIVE_DRYRUN_READY_FOR_CORE6":
        raise SystemExit(f"A7FF-CORE5 is not ready: {core5.get('decision')}")

    queue = pd.read_csv(QUEUE)
    shard_rows: list[dict[str, Any]] = []
    for shard_id, start in enumerate(range(0, len(queue), SHARD_SIZE)):
        shard = queue.iloc[start : start + SHARD_SIZE]
        shard_rows.append(
            {
                "shard_id": f"S{shard_id:02d}",
                "start_index": int(start),
                "end_index_exclusive": int(start + len(shard)),
                "candidate_count": int(len(shard)),
                "semantic_bucket_count": int(shard["semantic_bucket"].nunique()),
                "motif_bucket_count": int(shard["motif_bucket"].nunique()),
                "raw_field_count": len(split_fields(shard["raw_inputs"])),
                "expected_output": f"runtime/a7ffcore6e_materialization_preflight/a7ffcore6e_S{shard_id:02d}_materialization.csv",
            }
        )
    shard_plan = pd.DataFrame(shard_rows)
    shard_plan.to_csv(RUNTIME / "a7ffcore6_shard_plan.csv", index=False)

    field_plan_rows = []
    for field in sorted(split_fields(queue["raw_inputs"])):
        subset = queue[queue["raw_inputs"].fillna("").astype(str).str.contains(field, regex=False)]
        field_plan_rows.append(
            {
                "raw_field": field,
                "candidate_count": int(len(subset)),
                "semantic_buckets": ";".join(sorted(subset["semantic_bucket"].dropna().astype(str).unique())),
                "required_in_panel": True,
                "missing_policy": "fail_closed_for_candidate",
            }
        )
    field_plan = pd.DataFrame(field_plan_rows)
    field_plan.to_csv(RUNTIME / "a7ffcore6_required_field_plan.csv", index=False)

    preflight_checks = pd.DataFrame(
        [
            {"check_id": "C00_input_queue_integrity", "rule": "candidate_id/root_subgraph_id unique, gate_allowed=true for all rows", "hard_gate": True},
            {"check_id": "C01_panel_field_presence", "rule": "all raw_inputs exist in experiment panel or candidate fails closed", "hard_gate": True},
            {"check_id": "C02_operator_support", "rule": "expression operators supported by FeatureAlgebra before evaluation", "hard_gate": True},
            {"check_id": "C03_materialization_finite", "rule": "finite ratio and active coverage emitted per candidate", "hard_gate": True},
            {"check_id": "C04_no_label_or_may", "rule": "no label, future, May stress, or pass/fail tokens in materialized expression", "hard_gate": True},
            {"check_id": "C05_no_return_scoring", "rule": "preflight does not compute labels, returns, IC, spread, replay, selector score, or promotion", "hard_gate": True},
            {"check_id": "C06_shard_manifest", "rule": "each shard writes manifest with failure counts and reject reasons", "hard_gate": True},
            {"check_id": "C07_role_preservation", "rule": "diagnostic roots remain diagnostic; ordinary alpha remains unauthorized", "hard_gate": True},
        ]
    )
    preflight_checks.to_csv(RUNTIME / "a7ffcore6_preflight_checks.csv", index=False)

    execution_contract = {
        "stage": "A7FF-CORE6E",
        "input_queue": str(QUEUE.relative_to(REPO)),
        "candidate_count": int(len(queue)),
        "shard_size": SHARD_SIZE,
        "shard_count": int(len(shard_plan)),
        "allowed_actions": [
            "load panel",
            "evaluate expressions for finite/activity/materialization only",
            "emit per-candidate finite/activity/missing/operator status",
            "emit shard manifests",
        ],
        "forbidden_actions": [
            "compute forward returns",
            "compute labels",
            "compute IC/spread/PnL",
            "run replay",
            "run selector",
            "run search",
            "promote candidates",
            "use May stress labels or pass/fail",
        ],
        "pass_conditions": {
            "eval_failure_rate_max": 0.02,
            "missing_field_rate_max": 0.01,
            "role_violation_count": 0,
            "label_or_may_token_count": 0,
            "ordinary_alpha_leak_count": 0,
        },
    }
    write_json(RUNTIME / "a7ffcore6e_execution_contract.json", execution_contract)

    blockers: list[str] = []
    if len(queue) < 1024:
        blockers.append("queue_too_small_for_preflight")
    if int(queue["gate_allowed"].sum()) != len(queue):
        blockers.append("queue_has_gate_failures")
    if int(queue["ordinary_alpha_allowed"].sum()) != 0:
        blockers.append("ordinary_alpha_leak_in_queue")
    if len(shard_plan) < 4:
        blockers.append("shard_plan_too_small")
    if len(field_plan) == 0:
        blockers.append("empty_required_field_plan")

    decision = "PASS_A7FFCORE6_MATERIALIZATION_PREFLIGHT_CONTRACT_READY_FOR_CORE6E" if not blockers else "HOLD_A7FFCORE6_MATERIALIZATION_PREFLIGHT_CONTRACT_FAIL"
    manifest = {
        "stage": "A7FF-CORE6",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "source_stage": "A7FF-CORE5",
        "source_decision": core5.get("decision"),
        "input_queue_rows": int(len(queue)),
        "shard_size": SHARD_SIZE,
        "shard_count": int(len(shard_plan)),
        "required_field_count": int(len(field_plan)),
        "preflight_check_count": int(len(preflight_checks)),
        "executes_materialization": False,
        "executes_numeric": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_core6e": not bool(blockers),
        "authorizes_numeric": False,
        "authorizes_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE6E gate-native materialization preflight execution" if not blockers else "A7FF-CORE6 contract repair",
    }
    write_json(RUNTIME / "a7ffcore6_manifest.json", manifest)

    report = f"""# CRYPTO A7FF-CORE6 MATERIALIZATION PREFLIGHT CONTRACT

Generated: {manifest["generated_at"]}

## Decision

`{manifest["decision"]}`

A7FF-CORE6 defines the materialization preflight contract for the CORE5 gate-native queue. It does not execute materialization, numeric response, replay, search, or promotion.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Shard Plan

{md_table(shard_plan, 40)}

## Required Field Plan

{md_table(field_plan, 80)}

## Preflight Checks

{md_table(preflight_checks, 40)}

## Execution Contract

```json
{json.dumps(execution_contract, indent=2, sort_keys=True)}
```

## Boundary

```text
materialization executed: false
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
