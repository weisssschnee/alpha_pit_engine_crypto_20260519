from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff53_numeric_response_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FF53_NUMERIC_RESPONSE_CONTRACT_20260531.md"
A7FF52E = REPO / "runtime" / "a7ff52e_materialization_preflight"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.copy()
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

    m52e = read_json(A7FF52E / "a7ff52e_manifest.json")
    summary = read_csv(A7FF52E / "a7ff52e_summary.csv")
    if m52e.get("decision") != "PASS_A7FF52E_MATERIALIZATION_PREFLIGHT_READY_FOR_NUMERIC_CONTRACT":
        raise SystemExit(f"A7FF-52E is not ready for numeric contract: {m52e.get('decision')}")

    low_activity = set(m52e.get("low_activity_families", []))
    family_policy_rows: list[dict[str, Any]] = []
    for row in summary.to_dict(orient="records"):
        family = str(row.get("semantic_pair", ""))
        median_std = float(row.get("median_std", 0.0) or 0.0)
        policy = "primary_numeric_candidate"
        caveat = ""
        if family in low_activity:
            policy = "diagnostic_only_low_activity"
            caveat = "activity_ok_rows=0 in A7FF-52E; exclude from primary response gates"
        elif median_std > 1_000_000:
            policy = "primary_with_scale_guard"
            caveat = "large numeric scale; require winsor/scale audit before clue promotion"
        family_policy_rows.append(
            {
                "semantic_pair": family,
                "rows_in_materialization_sample": int(row.get("rows", 0)),
                "eval_success_rows": int(row.get("eval_success_rows", 0)),
                "activity_ok_rows": int(row.get("activity_ok_rows", 0)),
                "median_finite_share": float(row.get("median_finite_share", 0.0) or 0.0),
                "median_nonzero_share": float(row.get("median_nonzero_share", 0.0) or 0.0),
                "median_std": median_std,
                "numeric_policy": policy,
                "caveat": caveat,
            }
        )
    family_policy = pd.DataFrame(family_policy_rows)
    family_policy.to_csv(RUNTIME / "a7ff53_family_numeric_policy.csv", index=False)

    label_plan = pd.DataFrame(
        [
            {
                "label_family": "L0_raw_forward_return",
                "role": "primary",
                "horizons": "1h,4h,8h,24h",
                "pass_use": "can support clue only if control-clean and split-stable",
            },
            {
                "label_family": "L1_cross_sectional_relative_return",
                "role": "primary",
                "horizons": "1h,4h,8h,24h",
                "pass_use": "required to prevent pure ranked-label artifacts",
            },
            {
                "label_family": "L3_liquidity_tier_relative_return",
                "role": "primary",
                "horizons": "1h,4h,8h,24h",
                "pass_use": "tests liquidity-tier robustness",
            },
            {
                "label_family": "L5_vol_adjusted_return",
                "role": "secondary",
                "horizons": "4h,8h,24h",
                "pass_use": "supports risk-normalized clue evidence but cannot stand alone",
            },
            {
                "label_family": "L7_ranked_future_return",
                "role": "diagnostic_only",
                "horizons": "1h,4h,8h,24h",
                "pass_use": "never sufficient for promotion without non-L7 evidence",
            },
        ]
    )
    label_plan.to_csv(RUNTIME / "a7ff53_label_plan.csv", index=False)

    control_plan = pd.DataFrame(
        [
            {"control": "wrong_lag_future", "hard_gate": "control_ratio < 0.80 for clue promotion"},
            {"control": "wrong_lag_stale", "hard_gate": "control_ratio < 0.80 for clue promotion"},
            {"control": "row_shuffle", "hard_gate": "must be weaker than original signal"},
            {"control": "time_shuffle", "hard_gate": "must be weaker than original signal"},
            {"control": "symbol_shuffle", "hard_gate": "must be weaker than original signal"},
            {"control": "sign_flip", "hard_gate": "cannot produce symmetric pass"},
            {"control": "same_family_placebo", "hard_gate": "must not dominate original family"},
        ]
    )
    control_plan.to_csv(RUNTIME / "a7ff53_control_plan.csv", index=False)

    primary_families = family_policy.loc[family_policy["numeric_policy"] != "diagnostic_only_low_activity", "semantic_pair"].tolist()
    contract = {
        "stage": "A7FF-53",
        "name": "numeric response contract after A7FF-52E materialization preflight",
        "decision": "PASS_A7FF53_NUMERIC_RESPONSE_CONTRACT_READY_NO_EXECUTION_AUTH",
        "source_stage": "A7FF-52E",
        "input_metrics": "runtime/a7ff52e_materialization_preflight/a7ff52e_materialization_metrics.csv",
        "input_summary": "runtime/a7ff52e_materialization_preflight/a7ff52e_summary.csv",
        "execution_budget_if_later_approved": {
            "input_materialized_rows": int(m52e.get("sample_rows", 1200)),
            "primary_semantic_families": primary_families,
            "diagnostic_only_low_activity_families": sorted(low_activity),
            "labels": label_plan["label_family"].tolist(),
            "horizons": ["1h", "4h", "8h", "24h"],
            "max_reports": 1,
            "max_runtime_tables": 6,
            "max_scripts": 1,
        },
        "hard_gates_for_future_execution": {
            "materialization_eval_failure_count": 0,
            "missing_field_count": 0,
            "primary_family_count": ">= 6",
            "non_l7_primary_label_clue_rows": "> 0",
            "l7_only_evidence": "diagnostic_only_not_promotable",
            "control_ratio_for_clue": "< 0.80",
            "wrong_lag_dominance": 0,
            "low_activity_family_primary_rows": 0,
            "uses_may_in_score": False,
        },
        "hard_stop_before": ["formula search", "large search", "alpha proof", "shadow/paper/live"],
        "authorizes_numeric_response_execution": False,
        "authorizes_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff53_execution_contract.json", contract)

    manifest = {
        "stage": "A7FF-53",
        "generated_at": now_utc(),
        "decision": "PASS_A7FF53_NUMERIC_RESPONSE_CONTRACT_READY_NO_EXECUTION_AUTH",
        "source_a7ff52e_decision": m52e.get("decision"),
        "source_activity_ok_rate": m52e.get("activity_ok_rate"),
        "source_families_retained": m52e.get("families_retained"),
        "primary_family_count": len(primary_families),
        "diagnostic_only_low_activity_families": sorted(low_activity),
        "scale_guard_families": family_policy.loc[family_policy["numeric_policy"] == "primary_with_scale_guard", "semantic_pair"].tolist(),
        "blockers": [],
        "warnings": ["contract_only_no_numeric_response_execution"],
        "executes_generation": False,
        "executes_materialization": False,
        "executes_numeric_probe": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_numeric_response_execution": False,
        "authorizes_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff53_manifest.json", manifest)

    report = f"""# CRYPTO A7FF-53 NUMERIC RESPONSE CONTRACT

Generated: {manifest["generated_at"]}

## Decision

`{manifest["decision"]}`

A7FF-53 converts the A7FF-52E materialization pass into a numeric-response execution contract. It does not run labels, controls, replay, search, or alpha proof.

## Source Summary

```json
{json.dumps({k: m52e.get(k) for k in ["decision", "sample_rows", "eval_failure_count", "activity_ok_rate", "families_retained", "low_activity_families"]}, indent=2, sort_keys=True)}
```

## Family Numeric Policy

{md_table(family_policy)}

## Label Plan

{md_table(label_plan)}

## Control Plan

{md_table(control_plan)}

## Contract

```json
{json.dumps(contract, indent=2, sort_keys=True)}
```

## Boundary

```text
numeric response executed: false
replay executed: false
search executed: false
May used in scoring: false
alpha proof / shadow / paper / live: false
```
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
