from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore47e_compiler_readiness_audit"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE47E_COMPILER_READINESS_AUDIT_20260602.md"
CORE47 = REPO / "runtime" / "a7ffcore47_control_null_aware_factor_compiler_contract" / "a7ffcore47_manifest.json"

INPUTS = {
    "field_ontology_v3": REPO / "runtime" / "a7ffr1_field_ontology_v3" / "a7ffr1_field_ontology_v3.csv",
    "operator_response": REPO / "runtime" / "a7ffr2_operator_probing_v2" / "a7ffr2_observed_operator_response.csv",
    "feature_pair_policy": REPO / "runtime" / "a7ffr3_feature_pair_policy_v2" / "a7ffr3_feature_pair_policy_v2.csv",
    "primitive_response_map": REPO / "runtime" / "a7aa1_primitive_response_map" / "a7aa1_primitive_response_map.csv",
    "field_enforcement_manifest": REPO / "runtime" / "a7aif2_field_enforcement_regression" / "a7aif2_manifest.json",
    "materialization_manifest": REPO / "runtime" / "a7aif3_materialization_evaluator_parity" / "a7aif3_manifest.json",
    "control_vector_quality": REPO / "runtime" / "a7ffcore43e_control_vector_rebuild_audit" / "a7ffcore43e_sample_quality_gate.csv",
    "orthogonal_replay_manifest": REPO / "runtime" / "a7ffcore45e_orthogonal_book_replay_execution" / "a7ffcore45e_manifest.json",
    "orthogonal_forensic_manifest": REPO / "runtime" / "a7ffcore45r_orthogonal_book_replay_forensic" / "a7ffcore45r_manifest.json",
}


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


def safe_rows(path: Path) -> int:
    if not path.exists():
        return 0
    try:
        return int(pd.read_csv(path).shape[0])
    except Exception:
        return 0


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    source = read_json(CORE47)
    if source.get("decision") != "PASS_A7FFCORE47_CONTROL_NULL_AWARE_COMPILER_CONTRACT_READY_FOR_CORE47E":
        raise SystemExit(f"CORE47 not ready for CORE47E: {source.get('decision')}")

    ontology = pd.read_csv(INPUTS["field_ontology_v3"]) if INPUTS["field_ontology_v3"].exists() else pd.DataFrame()
    operator_response = pd.read_csv(INPUTS["operator_response"]) if INPUTS["operator_response"].exists() else pd.DataFrame()
    pair_policy = pd.read_csv(INPUTS["feature_pair_policy"]) if INPUTS["feature_pair_policy"].exists() else pd.DataFrame()
    response_map = pd.read_csv(INPUTS["primitive_response_map"]) if INPUTS["primitive_response_map"].exists() else pd.DataFrame()
    enforcement = read_json(INPUTS["field_enforcement_manifest"])
    materialization = read_json(INPUTS["materialization_manifest"])
    core45e = read_json(INPUTS["orthogonal_replay_manifest"])
    core45r = read_json(INPUTS["orthogonal_forensic_manifest"])
    control_quality = pd.read_csv(INPUTS["control_vector_quality"]) if INPUTS["control_vector_quality"].exists() else pd.DataFrame()

    input_inventory = pd.DataFrame(
        [
            {
                "artifact": name,
                "path": str(path.relative_to(REPO)).replace("\\", "/") if path.exists() else str(path),
                "exists": path.exists(),
                "rows": safe_rows(path) if path.suffix.lower() == ".csv" else None,
            }
            for name, path in INPUTS.items()
        ]
    )
    readiness = pd.DataFrame(
        [
            {
                "requirement": "field ontology with compiler roles",
                "evidence": "a7ffr1_field_ontology_v3",
                "status": "PASS"
                if not ontology.empty and {"semantic_type_v3", "compiler_role_v3", "allowed_roles_v3"}.issubset(ontology.columns)
                else "HOLD",
                "notes": f"rows={ontology.shape[0]}",
            },
            {
                "requirement": "operator probing evidence",
                "evidence": "a7ffr2_observed_operator_response",
                "status": "PASS"
                if not operator_response.empty and {"semantic_type_v3", "operator", "min_control_ratio"}.issubset(operator_response.columns)
                else "HOLD",
                "notes": f"rows={operator_response.shape[0]}",
            },
            {
                "requirement": "feature pair policy",
                "evidence": "a7ffr3_feature_pair_policy_v2",
                "status": "PASS" if not pair_policy.empty else "HOLD",
                "notes": f"rows={pair_policy.shape[0]}",
            },
            {
                "requirement": "primitive response map",
                "evidence": "a7aa1_primitive_response_map",
                "status": "PASS"
                if not response_map.empty and {"decision", "label_family", "control_ratio_premay_max"}.issubset(response_map.columns)
                else "HOLD",
                "notes": f"rows={response_map.shape[0]}",
            },
            {
                "requirement": "role enforcement connected",
                "evidence": "A7AI-F2",
                "status": "PASS" if enforcement.get("decision") == "PASS_A7AIF2_END_TO_END_ENFORCEMENT_CONNECTED" else "HOLD",
                "notes": f"role_violation_count={enforcement.get('role_violation_count')}",
            },
            {
                "requirement": "materialization/evaluator parity",
                "evidence": "A7AI-F3",
                "status": "PASS" if materialization.get("decision") == "PASS_A7AIF3_REPLAY_MATERIALIZATION_PARITY_READY" else "HOLD",
                "notes": f"fields={materialization.get('field_count')}; operators={materialization.get('operator_count')}",
            },
            {
                "requirement": "full-universe control vector feasibility",
                "evidence": "A7FF-CORE43E",
                "status": "PASS" if not control_quality.empty and control_quality["pass"].astype(str).str.lower().eq("true").all() else "HOLD",
                "notes": f"quality_rows={control_quality.shape[0]}",
            },
            {
                "requirement": "negative replay evidence available",
                "evidence": "A7FF-CORE45E/45R",
                "status": "PASS"
                if core45e.get("decision") == "HOLD_A7FFCORE45E_ORTHOGONAL_BOOK_REPLAY_INSUFFICIENT"
                and core45r.get("dominant_failure") == "orthogonal_book_replay_control_dominated_zero_survivors"
                else "HOLD",
                "notes": f"core45e={core45e.get('decision')}; failure={core45r.get('dominant_failure')}",
            },
        ]
    )
    generation_readiness = pd.DataFrame(
        [
            {
                "capability": "define_null_first_generation_contract",
                "status": "READY" if readiness["status"].eq("PASS").all() else "NOT_READY",
                "reason": "source artifacts are sufficient to define a bounded null-first generation contract",
            },
            {
                "capability": "execute_null_first_generation_now",
                "status": "NOT_READY",
                "reason": "compiler implementation and gate-native output schema are not built yet; CORE47E is audit-only",
            },
            {
                "capability": "execute_formula_search_now",
                "status": "NOT_AUTHORIZED",
                "reason": "CORE46/CORE47 explicitly block generation/search until null-first compiler contract and later gates exist",
            },
        ]
    )
    gap_matrix = pd.DataFrame(
        [
            {
                "gap_id": "G0_compiler_implementation_missing",
                "severity": "expected_next_contract_gap",
                "description": "no null-first compiler execution entrypoint exists yet",
                "blocks_core48_contract": False,
                "blocks_generation_execution": True,
            },
            {
                "gap_id": "G1_operator_null_margin_not_native",
                "severity": "implementation_gap",
                "description": "operator probing has response/control summaries but not native full-universe null vectors per operator",
                "blocks_core48_contract": False,
                "blocks_generation_execution": True,
            },
            {
                "gap_id": "G2_pair_policy_not_null_ranked",
                "severity": "implementation_gap",
                "description": "feature-pair policy exists but must be re-ranked by null-margin evidence before generation",
                "blocks_core48_contract": False,
                "blocks_generation_execution": True,
            },
        ]
    )
    decision = (
        "PASS_A7FFCORE47E_COMPILER_READINESS_READY_FOR_CORE48_CONTRACT"
        if readiness["status"].eq("PASS").all()
        else "HOLD_A7FFCORE47E_COMPILER_READINESS_GAPS"
    )
    authorization = {
        "authorized": {
            "A7FF-CORE48 bounded null-first factor seed generation contract": decision.startswith("PASS")
        },
        "not_authorized": {
            "null_first_generation_execution": True,
            "formula_search": True,
            "large_search": True,
            "current_candidate_expansion": True,
            "alpha_proof": True,
            "shadow_paper_live": True,
        },
    }
    manifest = {
        "stage": "A7FF-CORE47E",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE47",
        "source_decision": source.get("decision"),
        "decision": decision,
        "readiness_pass_count": int(readiness["status"].eq("PASS").sum()),
        "readiness_total_count": int(readiness.shape[0]),
        "executes_generation": False,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core48_contract": decision.startswith("PASS"),
        "authorizes_generation_execution": False,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE48 bounded null-first factor seed generation contract"
        if decision.startswith("PASS")
        else "A7FF-CORE47E repair / rerun only",
    }
    input_inventory.to_csv(RUNTIME / "a7ffcore47e_input_inventory.csv", index=False)
    readiness.to_csv(RUNTIME / "a7ffcore47e_readiness_matrix.csv", index=False)
    generation_readiness.to_csv(RUNTIME / "a7ffcore47e_generation_readiness.csv", index=False)
    gap_matrix.to_csv(RUNTIME / "a7ffcore47e_gap_matrix.csv", index=False)
    write_json(RUNTIME / "a7ffcore47e_authorization_matrix.json", authorization)
    write_json(RUNTIME / "a7ffcore47e_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE47E COMPILER READINESS AUDIT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE47E audits whether the existing evidence base can support a control-null-aware compiler contract. It does not execute generation, replay, search, proof, shadow, paper, or live.",
        "",
        "## Input Inventory",
        "",
        md_table(input_inventory),
        "",
        "## Readiness Matrix",
        "",
        md_table(readiness),
        "",
        "## Generation Readiness",
        "",
        md_table(generation_readiness),
        "",
        "## Gap Matrix",
        "",
        md_table(gap_matrix),
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
