from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore0_typed_ast_governance"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE0_TYPED_AST_GOVERNANCE_20260601.md"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


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

    a7ff55e = read_json(REPO / "runtime" / "a7ff55r5e_sharded_numeric_summary" / "a7ff55r5e_manifest.json")
    a7ff55r2 = read_json(REPO / "runtime" / "a7ff55r2_atlas_field_family_generation_repair" / "a7ff55r2_manifest.json")
    old_index = read_csv(REPO / "runtime" / "a7ff_version_20260530" / "a7ff_v20260530_formula_index.csv")
    repaired_index = read_csv(REPO / "runtime" / "a7ff55r3_repaired_atlas_dry_generation" / "a7ff55r3_repaired_formula_index.csv")

    expression_node_schema = {
        "schema_version": "a7ff_core_ast_v0",
        "node_types": {
            "Field": {
                "required": ["field_name", "raw_source_family", "semantic_type", "field_role", "pit_policy", "latency_policy"],
                "allowed_roles": ["raw_source", "signal_seed", "regime", "neutralizer", "risk_exposure", "diagnostic", "label_only", "forbidden"],
            },
            "Transform": {
                "required": ["operator", "input_node_id", "lookback_hours", "fit_window", "pit_policy", "role_policy"],
                "operators": ["Delta", "Mean", "ZScore", "TSRank", "Decay", "Rank", "CSRank", "Abs", "Sign", "Clip"],
            },
            "Interaction": {
                "required": ["operator", "left_node_id", "right_node_id", "semantic_pair", "motif", "role_policy"],
                "operators": ["Mul", "Sub", "Add", "SafeDiv", "GatedSign", "SpreadRank", "SmoothMul"],
            },
            "Neutralization": {
                "required": ["input_node_id", "group_key", "neutralization_policy", "min_group_count"],
                "operators": ["CSRank", "WithinLatentRank", "WithinLiquidityTierRank", "Residualize"],
            },
            "Label": {
                "required": ["label_family", "horizon_hours", "entry_alignment", "usage"],
                "usage": "target_only_never_feature",
            },
            "FactorCandidate": {
                "required": [
                    "expression_node_id",
                    "orientation_source",
                    "label_family",
                    "horizon_hours",
                    "neutralization",
                    "control_policy",
                    "response_evidence_id",
                ],
                "promotion_boundary": "cannot become replay candidate without response/control/latency evidence",
            },
        },
        "global_invariants": [
            "label nodes cannot be referenced by Field/Transform/Interaction nodes",
            "diagnostic/risk/neutralizer nodes cannot become ordinary alpha without explicit response-backed promotion",
            "FormulaGen may only compose approved feature subgraphs",
            "FeatureFactory may only emit typed subgraphs, not standalone untyped columns",
            "selector reads factor_role and response_evidence, not only expression string",
        ],
    }
    write_json(RUNTIME / "a7ffcore0_expression_node_schema.json", expression_node_schema)

    layer_boundary = pd.DataFrame(
        [
            {
                "layer": "L0_raw_field",
                "owner": "data_contracts / feature registry",
                "artifact": "Field node",
                "may_generate": "raw field node only",
                "must_not_generate": "transforms, labels as feature, formula interactions",
            },
            {
                "layer": "L1_typed_derived_feature",
                "owner": "Field-to-Factor Compiler",
                "artifact": "Transform / Interaction subgraph",
                "may_generate": "typed subgraph with lineage/PIT/role",
                "must_not_generate": "alpha candidate or replay authorization",
            },
            {
                "layer": "L2_response_tested_feature",
                "owner": "response map / controls",
                "artifact": "feature subgraph + response evidence",
                "may_generate": "promotion evidence",
                "must_not_generate": "portfolio claim",
            },
            {
                "layer": "L3_factor_candidate",
                "owner": "selector preflight",
                "artifact": "FactorCandidate node",
                "may_generate": "candidate with label/horizon/orientation/control policy",
                "must_not_generate": "paper/shadow/live authorization",
            },
            {
                "layer": "L4_alpha_formula_candidate",
                "owner": "FormulaGen / Searcher",
                "artifact": "composition of approved factor candidates",
                "may_generate": "bounded formula hypotheses",
                "must_not_generate": "raw unapproved feature transforms",
            },
            {
                "layer": "L5_book_component",
                "owner": "replay / cluster / promotion",
                "artifact": "book component",
                "may_generate": "promotion candidate after replay/cluster/marginal evidence",
                "must_not_generate": "bypass proof gates",
            },
        ]
    )

    overlap_rows: list[dict[str, Any]] = []
    if not old_index.empty:
        old_semantics = set(old_index.get("semantic_pair", pd.Series(dtype=str)).dropna().astype(str))
        old_fields = set(old_index.get("primary_field", pd.Series(dtype=str)).dropna().astype(str)) | set(
            old_index.get("secondary_field", pd.Series(dtype=str)).dropna().astype(str)
        )
    else:
        old_semantics, old_fields = set(), set()
    if not repaired_index.empty:
        repaired_semantics = set(repaired_index.get("semantic_pair", pd.Series(dtype=str)).dropna().astype(str))
        repaired_fields = set(repaired_index.get("primary_field", pd.Series(dtype=str)).dropna().astype(str)) | set(
            repaired_index.get("secondary_field", pd.Series(dtype=str)).dropna().astype(str)
        )
    else:
        repaired_semantics, repaired_fields = set(), set()
    for semantic in sorted(old_semantics | repaired_semantics):
        overlap_rows.append(
            {
                "object_type": "semantic_pair",
                "object_id": semantic,
                "in_a7ff_v20260530": semantic in old_semantics,
                "in_repaired_a7ff55r3": semantic in repaired_semantics,
                "governance_note": "semantic pair must map to typed AST semantic_pair, not ad hoc string families",
            }
        )
    for field in sorted(old_fields | repaired_fields):
        if not field or field == "nan":
            continue
        if any(token in field for token in ["open_interest", "taker", "liquidity", "premium", "basis", "funding"]):
            overlap_rows.append(
                {
                    "object_type": "field",
                    "object_id": field,
                    "in_a7ff_v20260530": field in old_fields,
                    "in_repaired_a7ff55r3": field in repaired_fields,
                    "governance_note": "field role must be carried as Field node metadata before transform/formula use",
                }
            )
    overlap_audit = pd.DataFrame(overlap_rows)

    role_enforcement = pd.DataFrame(
        [
            {
                "role": "ordinary_alpha_seed",
                "feature_factory_allowed": "emit typed subgraph after response evidence",
                "formula_gen_allowed": "compose with approved factor candidates",
                "selector_allowed": "eligible for alpha queue if controls pass",
            },
            {
                "role": "exploratory_signal_seed",
                "feature_factory_allowed": "emit typed subgraph for numeric response",
                "formula_gen_allowed": "compose only in diagnostic/repair waves",
                "selector_allowed": "not alpha-eligible until response-backed promotion",
            },
            {
                "role": "regime_neutralizer_interaction_seed",
                "feature_factory_allowed": "emit as modifier/condition node",
                "formula_gen_allowed": "right-hand modifier only unless promoted",
                "selector_allowed": "cannot stand alone as alpha signal",
            },
            {
                "role": "risk_defense_only",
                "feature_factory_allowed": "emit defense/neutralization node",
                "formula_gen_allowed": "not allowed in ordinary alpha expression as signal",
                "selector_allowed": "reject for alpha replay",
            },
            {
                "role": "diagnostic_only",
                "feature_factory_allowed": "emit only with diagnostic route",
                "formula_gen_allowed": "diagnostic search only",
                "selector_allowed": "cannot enter ordinary alpha replay queue",
            },
            {
                "role": "label_only",
                "feature_factory_allowed": "target node only",
                "formula_gen_allowed": "forbidden as feature input",
                "selector_allowed": "forbidden as candidate field",
            },
        ]
    )

    migration_plan = pd.DataFrame(
        [
            {
                "step": "A7FF-CORE1",
                "task": "AST schema adapter",
                "success_criteria": "formula_index rows can round-trip expression string -> typed AST JSON -> expression string",
                "blocks": "no new formula generation until adapter exists for new stages",
            },
            {
                "step": "A7FF-CORE2",
                "task": "FeatureFactory subgraph registry",
                "success_criteria": "derived features are emitted as approved subgraphs with raw_inputs/lookback/PIT/role",
                "blocks": "manual untyped derived columns",
            },
            {
                "step": "A7FF-CORE3",
                "task": "FormulaGen approved-subgraph gate",
                "success_criteria": "FormulaGen can only compose approved AST subgraphs or explicitly diagnostic nodes",
                "blocks": "bypass of field-role enforcement",
            },
            {
                "step": "A7FF-CORE4",
                "task": "SearchMemory semantic dedup",
                "success_criteria": "dedup includes raw_inputs/operator_path/semantic_type/response_role, not string only",
                "blocks": "duplicate economic meaning under different names",
            },
            {
                "step": "A7FF-CORE5",
                "task": "selector role trace enforcement",
                "success_criteria": "selector trace records AST node roles and rejects role violations fail-closed",
                "blocks": "diagnostic/risk fields selected as ordinary alpha",
            },
        ]
    )

    current_breakpoint = {
        "source": "A7FF-55R5E",
        "decision": a7ff55e.get("decision"),
        "numeric_response_issue": {
            "sampled_input_blueprints": a7ff55e.get("sampled_input_blueprints"),
            "non_l7_numeric_clue_rows": a7ff55e.get("non_l7_numeric_clue_rows"),
            "selected_portfolio_queue_count": a7ff55e.get("selected_portfolio_queue_count"),
        },
        "governance_interpretation": (
            "R2/R3/R4 repaired coverage, but the system still lacks a unified typed subgraph boundary; "
            "field-family repair can create syntactic coverage without enough response-backed factor seeds."
        ),
    }
    write_json(RUNTIME / "a7ffcore0_current_breakpoint.json", current_breakpoint)

    layer_boundary.to_csv(RUNTIME / "a7ffcore0_layer_boundary.csv", index=False)
    overlap_audit.to_csv(RUNTIME / "a7ffcore0_generator_overlap_audit.csv", index=False)
    role_enforcement.to_csv(RUNTIME / "a7ffcore0_role_enforcement_matrix.csv", index=False)
    migration_plan.to_csv(RUNTIME / "a7ffcore0_migration_plan.csv", index=False)

    manifest = {
        "stage": "A7FF-CORE0",
        "generated_at": now_utc(),
        "decision": "PASS_A7FFCORE0_TYPED_AST_GOVERNANCE_READY_FOR_CORE1",
        "source_stage": "A7FF-55R5E",
        "source_decision": a7ff55e.get("decision"),
        "purpose": "governance layer to unify derived feature generation and formula generation under typed AST",
        "node_type_count": len(expression_node_schema["node_types"]),
        "layer_boundary_rows": int(len(layer_boundary)),
        "overlap_audit_rows": int(len(overlap_audit)),
        "role_enforcement_rows": int(len(role_enforcement)),
        "migration_steps": int(len(migration_plan)),
        "next_allowed": "A7FF-CORE1 AST schema adapter",
        "executes_generation": False,
        "executes_numeric": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_generation": False,
        "authorizes_numeric": False,
        "authorizes_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ffcore0_manifest.json", manifest)

    report = f"""# CRYPTO A7FF-CORE0 TYPED AST GOVERNANCE

Generated: {manifest["generated_at"]}

## Decision

`{manifest["decision"]}`

A7FF-CORE0 is a governance-only layer. It formalizes that derived feature generation and formula generation must use one typed expression / FeatureAlgebra AST. It does not execute generation, numeric evaluation, replay, or search.

## Current Breakpoint

```json
{json.dumps(current_breakpoint, indent=2, sort_keys=True)}
```

## Expression Node Schema

```json
{json.dumps(expression_node_schema, indent=2, sort_keys=True)}
```

## Layer Boundary

{md_table(layer_boundary, 20)}

## Role Enforcement Matrix

{md_table(role_enforcement, 20)}

## Generator Overlap Audit

{md_table(overlap_audit, 80)}

## Migration Plan

{md_table(migration_plan, 20)}

## Boundary

```text
generation executed: false
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
