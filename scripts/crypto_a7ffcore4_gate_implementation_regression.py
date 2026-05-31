from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from crypto_a7ffcore_gate import FormulaGenSubgraphGate


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore4_gate_implementation_regression"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE4_GATE_IMPLEMENTATION_REGRESSION_20260601.md"
A7FFCORE3 = REPO / "runtime" / "a7ffcore3_formula_gen_subgraph_gate" / "a7ffcore3_manifest.json"
CORE3_AUDIT = REPO / "runtime" / "a7ffcore3_formula_gen_subgraph_gate" / "a7ffcore3_generation_script_bypass_audit.csv"
CORE2_REUSABLE = REPO / "runtime" / "a7ffcore2_feature_subgraph_registry" / "a7ffcore2_reusable_feature_subgraphs.csv"
CORE2_ROOTS = REPO / "runtime" / "a7ffcore2_feature_subgraph_registry" / "a7ffcore2_factor_candidate_roots.csv"


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


def classify_entrypoints(audit: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for row in audit.to_dict("records"):
        bypass = str(row.get("bypass_risk", ""))
        script_path = str(row.get("script_path", ""))
        if bypass == "high":
            route = "quarantined_legacy_generation"
            core4_status = "blocked_until_rewritten_against_subgraph_gate"
            allowed = False
        else:
            route = "contract_or_non_generation_reference"
            core4_status = "allowed_as_non_generation_reference"
            allowed = True
        rows.append(
            {
                "script_path": script_path,
                "bypass_risk": bypass,
                "entrypoint_route": route,
                "core4_status": core4_status,
                "allowed_as_generation_entrypoint": allowed,
                "requires_gate_native_rewrite": bypass == "high",
                "direct_expression_hit_count": int(row.get("direct_expression_hit_count", 0)),
                "core2_reference_hit_count": int(row.get("core2_reference_hit_count", 0)),
            }
        )
    return pd.DataFrame(rows)


def regression_cases(gate: FormulaGenSubgraphGate) -> pd.DataFrame:
    reusable = pd.read_csv(CORE2_REUSABLE)
    roots = pd.read_csv(CORE2_ROOTS)
    approved = reusable[
        reusable["formula_gen_gate"].eq("feature_factory_reusable_subgraph")
        & reusable["feature_factory_allowed"].astype(bool)
    ].head(50)
    root_sample = roots[roots["formula_gen_gate"].eq("diagnostic_or_repair_root_only")].head(20)

    cases: list[dict[str, Any]] = []
    for row in approved.to_dict("records"):
        cases.append(
            {
                "case_id": f"allow_reusable_id_{len(cases)}",
                "mode": "ordinary_alpha",
                "input_type": "subgraph_id",
                "expression": "",
                "subgraph_id": row["subgraph_id"],
                "expected_allowed": True,
            }
        )
        cases.append(
            {
                "case_id": f"allow_reusable_expr_{len(cases)}",
                "mode": "ordinary_alpha",
                "input_type": "expression",
                "expression": row["expression"],
                "subgraph_id": "",
                "expected_allowed": True,
            }
        )
    for row in root_sample.to_dict("records"):
        cases.append(
            {
                "case_id": f"reject_root_ordinary_{len(cases)}",
                "mode": "ordinary_alpha",
                "input_type": "subgraph_id",
                "expression": "",
                "subgraph_id": row["subgraph_id"],
                "expected_allowed": False,
            }
        )
        cases.append(
            {
                "case_id": f"allow_root_diagnostic_{len(cases)}",
                "mode": "diagnostic_repair",
                "input_type": "subgraph_id",
                "expression": "",
                "subgraph_id": row["subgraph_id"],
                "expected_allowed": True,
            }
        )
    bad_exprs = [
        "Mul(label_forward_return_1h,open_interest_last)",
        "Mul(unknown_field,trade_close)",
        "UnknownOp(open_interest_last)",
        "Sub(MayStressPass,open_interest_last)",
        "Mul(ZScore(Mean(open_interest_last,9999)),ZScore(Mean(trade_close,9999)))",
    ]
    for expr in bad_exprs:
        cases.append(
            {
                "case_id": f"reject_bypass_{len(cases)}",
                "mode": "ordinary_alpha",
                "input_type": "expression",
                "expression": expr,
                "subgraph_id": "",
                "expected_allowed": False,
            }
        )
    rows: list[dict[str, Any]] = []
    for case in cases:
        result = gate.validate(
            expression=case["expression"] or None,
            subgraph_id=case["subgraph_id"] or None,
            mode=case["mode"],
        )
        rows.append(
            {
                **case,
                "actual_allowed": bool(result["allowed"]),
                "result_reason": result["reason"],
                "resolved_subgraph_id": result.get("resolved_subgraph_id", ""),
                "pass": bool(result["allowed"]) == bool(case["expected_allowed"]),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    core3 = read_json(A7FFCORE3)
    if core3.get("decision") != "PASS_A7FFCORE3_FORMULAGEN_SUBGRAPH_GATE_READY_FOR_CORE4":
        raise SystemExit(f"A7FF-CORE3 is not ready: {core3.get('decision')}")

    audit = pd.read_csv(CORE3_AUDIT)
    entrypoints = classify_entrypoints(audit)
    gate = FormulaGenSubgraphGate()
    cases = regression_cases(gate)

    entrypoints.to_csv(RUNTIME / "a7ffcore4_entrypoint_policy.csv", index=False)
    cases.to_csv(RUNTIME / "a7ffcore4_gate_regression_cases.csv", index=False)

    route_summary = (
        entrypoints.groupby(["entrypoint_route", "core4_status"], dropna=False)
        .agg(
            scripts=("script_path", "count"),
            generation_entrypoints_allowed=("allowed_as_generation_entrypoint", "sum"),
            rewrite_required=("requires_gate_native_rewrite", "sum"),
        )
        .reset_index()
        .sort_values("scripts", ascending=False)
    )
    route_summary.to_csv(RUNTIME / "a7ffcore4_entrypoint_route_summary.csv", index=False)

    regression_summary = (
        cases.groupby(["mode", "input_type", "expected_allowed", "actual_allowed"], dropna=False)
        .size()
        .reset_index(name="cases")
        .sort_values("cases", ascending=False)
    )
    regression_summary.to_csv(RUNTIME / "a7ffcore4_regression_summary.csv", index=False)

    allowed_generation_entrypoints = int(entrypoints["allowed_as_generation_entrypoint"].sum())
    high_risk_unquarantined = int(
        (
            entrypoints["bypass_risk"].eq("high")
            & entrypoints["allowed_as_generation_entrypoint"].astype(bool)
        ).sum()
    )
    regression_failures = int((~cases["pass"].astype(bool)).sum())
    blockers: list[str] = []
    if high_risk_unquarantined:
        blockers.append("high_risk_generation_entrypoint_not_quarantined")
    if regression_failures:
        blockers.append("gate_regression_failures_present")

    decision = "PASS_A7FFCORE4_GATE_IMPLEMENTATION_REGRESSION_READY_FOR_CORE5" if not blockers else "HOLD_A7FFCORE4_GATE_IMPLEMENTATION_REGRESSION_FAIL"
    manifest = {
        "stage": "A7FF-CORE4",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "source_stage": "A7FF-CORE3",
        "source_decision": core3.get("decision"),
        "audited_generation_scripts": int(len(entrypoints)),
        "quarantined_legacy_generation_scripts": int(entrypoints["requires_gate_native_rewrite"].sum()),
        "allowed_generation_entrypoints": allowed_generation_entrypoints,
        "high_risk_unquarantined_entrypoints": high_risk_unquarantined,
        "gate_regression_case_count": int(len(cases)),
        "gate_regression_failures": regression_failures,
        "executes_generation": False,
        "executes_numeric": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_core5": not bool(blockers),
        "authorizes_generation": False,
        "authorizes_numeric": False,
        "authorizes_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE5 gate-native generation compatibility dryrun" if not blockers else "A7FF-CORE4 gate repair",
    }
    write_json(RUNTIME / "a7ffcore4_manifest.json", manifest)

    report = f"""# CRYPTO A7FF-CORE4 GATE IMPLEMENTATION REGRESSION

Generated: {manifest["generated_at"]}

## Decision

`{manifest["decision"]}`

A7FF-CORE4 adds a reusable FormulaGen subgraph gate implementation, quarantines legacy high-bypass generation scripts as non-active generation entrypoints, and runs allow/reject regression cases against CORE2 approved subgraphs. It does not execute formula generation, numeric evaluation, replay, or search.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Entrypoint Route Summary

{md_table(route_summary, 20)}

## Gate Regression Summary

{md_table(regression_summary, 40)}

## Quarantined Legacy Generation Scripts

{md_table(entrypoints[entrypoints["requires_gate_native_rewrite"].astype(bool)][["script_path", "bypass_risk", "core4_status", "direct_expression_hit_count", "core2_reference_hit_count"]], 80)}

## Boundary

```text
generation executed: false
numeric execution: false
replay executed: false
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```

## Next

`A7FF-CORE5 gate-native generation compatibility dryrun` may build a new generation entrypoint that emits only CORE4-gated subgraph references. Legacy generation scripts remain quarantined until rewritten or retired.
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
