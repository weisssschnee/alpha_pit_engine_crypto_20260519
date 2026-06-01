from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore48_null_first_seed_generation_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE48_NULL_FIRST_SEED_GENERATION_CONTRACT_20260602.md"
CORE47E = REPO / "runtime" / "a7ffcore47e_compiler_readiness_audit" / "a7ffcore47e_manifest.json"


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
    return view.to_markdown(index=False)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    source = read_json(CORE47E)
    if source.get("decision") != "PASS_A7FFCORE47E_COMPILER_READINESS_READY_FOR_CORE48_CONTRACT":
        raise SystemExit(f"CORE47E not ready for CORE48: {source.get('decision')}")

    input_sources = pd.DataFrame(
        [
            {
                "input_id": "I0_field_ontology_v3",
                "path": "runtime/a7ffr1_field_ontology_v3/a7ffr1_field_ontology_v3.csv",
                "role": "field semantic and compiler role source",
                "required": True,
            },
            {
                "input_id": "I1_operator_response",
                "path": "runtime/a7ffr2_operator_probing_v2/a7ffr2_observed_operator_response.csv",
                "role": "operator response/null pre-score source",
                "required": True,
            },
            {
                "input_id": "I2_pair_policy",
                "path": "runtime/a7ffr3_feature_pair_policy_v2/a7ffr3_feature_pair_policy_v2.csv",
                "role": "semantic-compatible pair source",
                "required": True,
            },
            {
                "input_id": "I3_primitive_response_map",
                "path": "runtime/a7aa1_primitive_response_map/a7aa1_primitive_response_map.csv",
                "role": "label/control response evidence source",
                "required": True,
            },
            {
                "input_id": "I4_core43e_vector_schema",
                "path": "runtime/a7ffcore43e_control_vector_rebuild_audit/a7ffcore43e_sample_quality_gate.csv",
                "role": "required full-universe null-vector feasibility source",
                "required": True,
            },
        ]
    )
    generation_lanes = pd.DataFrame(
        [
            {
                "lane_id": "N0_single_field_operator_seed",
                "description": "single field x operator seeds with non-L7 response and control/null margin evidence",
                "max_seed_count": 360,
                "requires_pair": False,
            },
            {
                "lane_id": "N1_role_compatible_pair_seed",
                "description": "semantic-compatible field pairs after both sides have response evidence",
                "max_seed_count": 360,
                "requires_pair": True,
            },
            {
                "lane_id": "N2_regime_conditioned_seed",
                "description": "ordinary-alpha seed conditioned by regime/neutralizer fields without promoting those fields as standalone alpha",
                "max_seed_count": 240,
                "requires_pair": True,
            },
            {
                "lane_id": "N3_control_repair_seed",
                "description": "near-miss response rows explicitly redesigned to improve original-vs-stale/sign/shuffle separation",
                "max_seed_count": 240,
                "requires_pair": False,
            },
        ]
    )
    hard_gates = pd.DataFrame(
        [
            {"gate": "field_contract_present", "requirement": "all fields must exist in ontology/enforcement ledger"},
            {"gate": "role_allowed", "requirement": "diagnostic/risk-defense fields cannot be standalone alpha seeds"},
            {"gate": "non_l7_response_required", "requirement": "seed must have non-L7 response evidence or be marked diagnostic-only"},
            {"gate": "control_margin_required", "requirement": "operator/field evidence must show original signal weaker controls are not dominant"},
            {"gate": "full_universe_vector_required", "requirement": "CORE48E must output original/stale/sign/time/symbol score vector fields"},
            {"gate": "family_cap", "requirement": "no semantic family may exceed 35 percent of selected seeds"},
            {"gate": "motif_cap", "requirement": "no operator/motif may exceed 25 percent of selected seeds"},
            {"gate": "no_known_stress_score", "requirement": "known stress/May-like labels are forbidden in generation score"},
        ]
    )
    output_schema = pd.DataFrame(
        [
            {"field": "seed_id", "required": True},
            {"field": "lane_id", "required": True},
            {"field": "field_primary", "required": True},
            {"field": "field_partner", "required": False},
            {"field": "semantic_type_primary", "required": True},
            {"field": "semantic_type_partner", "required": False},
            {"field": "operator", "required": True},
            {"field": "window_h", "required": True},
            {"field": "expression", "required": True},
            {"field": "compiler_role", "required": True},
            {"field": "non_l7_evidence", "required": True},
            {"field": "operator_null_margin", "required": True},
            {"field": "role_gate_status", "required": True},
            {"field": "family_cap_status", "required": True},
            {"field": "candidate_status", "required": True},
        ]
    )
    pass_gate = pd.DataFrame(
        [
            {"gate": "generated_seed_count", "threshold": ">= 400 bounded dry seeds"},
            {"gate": "eligible_seed_count", "threshold": ">= 120 null-first eligible seeds"},
            {"gate": "semantic_family_count", "threshold": ">= 5 eligible semantic families"},
            {"gate": "operator_count", "threshold": ">= 4 eligible operators"},
            {"gate": "role_violation_count", "threshold": "0"},
            {"gate": "missing_contract_count", "threshold": "0"},
            {"gate": "family_cap_violation_count", "threshold": "0"},
        ]
    )
    execution_plan = pd.DataFrame(
        [
            {
                "stage": "A7FF-CORE48E",
                "action": "bounded null-first dry seed generation using CORE48 gates",
                "executes_generation": True,
                "executes_replay": False,
                "executes_search": False,
                "max_seed_count": 1200,
            },
            {
                "stage": "A7FF-CORE49",
                "action": "if CORE48E passes, define full-universe null-vector preflight for eligible seeds",
                "executes_generation": False,
                "executes_replay": False,
                "executes_search": False,
                "max_seed_count": None,
            },
        ]
    )
    authorization = {
        "authorized": {
            "A7FF-CORE48E bounded null-first dry seed generation": True
        },
        "not_authorized": {
            "numeric_replay": True,
            "formula_search": True,
            "large_search": True,
            "alpha_proof": True,
            "shadow_paper_live": True,
            "promotion": True,
        },
    }
    decision = "PASS_A7FFCORE48_NULL_FIRST_SEED_GENERATION_CONTRACT_READY_FOR_CORE48E"
    manifest = {
        "stage": "A7FF-CORE48",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE47E",
        "source_decision": source.get("decision"),
        "decision": decision,
        "executes_generation": False,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core48e_dry_generation": True,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "max_core48e_seed_count": 1200,
        "next_allowed": "A7FF-CORE48E bounded null-first dry seed generation",
    }
    input_sources.to_csv(RUNTIME / "a7ffcore48_input_sources.csv", index=False)
    generation_lanes.to_csv(RUNTIME / "a7ffcore48_generation_lanes.csv", index=False)
    hard_gates.to_csv(RUNTIME / "a7ffcore48_hard_gates.csv", index=False)
    output_schema.to_csv(RUNTIME / "a7ffcore48_seed_output_schema.csv", index=False)
    pass_gate.to_csv(RUNTIME / "a7ffcore48_pass_gate.csv", index=False)
    execution_plan.to_csv(RUNTIME / "a7ffcore48_execution_plan.csv", index=False)
    write_json(RUNTIME / "a7ffcore48_authorization_matrix.json", authorization)
    write_json(RUNTIME / "a7ffcore48_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE48 NULL-FIRST SEED GENERATION CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE48 defines bounded null-first dry seed generation after CORE47E readiness. It authorizes only CORE48E dry generation, not numeric replay, formula search, large search, proof, shadow, paper, live, or promotion.",
        "",
        "## Input Sources",
        "",
        md_table(input_sources),
        "",
        "## Generation Lanes",
        "",
        md_table(generation_lanes),
        "",
        "## Hard Gates",
        "",
        md_table(hard_gates),
        "",
        "## Output Schema",
        "",
        md_table(output_schema),
        "",
        "## Pass Gate",
        "",
        md_table(pass_gate),
        "",
        "## Execution Plan",
        "",
        md_table(execution_plan),
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
