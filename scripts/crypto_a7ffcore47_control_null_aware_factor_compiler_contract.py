from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore47_control_null_aware_factor_compiler_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE47_CONTROL_NULL_AWARE_FACTOR_COMPILER_CONTRACT_20260602.md"
CORE46 = REPO / "runtime" / "a7ffcore46_orthogonal_failure_route_arbitration" / "a7ffcore46_manifest.json"


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
    source = read_json(CORE46)
    if source.get("decision") != "PASS_A7FFCORE46_ROUTE_ARBITRATION_READY_FOR_CORE47_CONTRACT":
        raise SystemExit(f"CORE46 not ready for CORE47: {source.get('decision')}")

    compiler_principles = pd.DataFrame(
        [
            {
                "principle_id": "C0_null_first",
                "description": "feature-to-factor candidates must expose original-vs-null separability before replay or book selection",
                "hard_requirement": True,
            },
            {
                "principle_id": "C1_full_universe_vectors",
                "description": "candidate scoring must be evaluated on full timestamp-symbol score vectors, not selected top/bottom rows",
                "hard_requirement": True,
            },
            {
                "principle_id": "C2_role_typed_generation",
                "description": "signal, regime, neutralizer, and risk-defense fields must remain role-tagged through compilation",
                "hard_requirement": True,
            },
            {
                "principle_id": "C3_response_before_interaction",
                "description": "single-field/operator response and null-separation evidence must exist before pairwise interaction expansion",
                "hard_requirement": True,
            },
            {
                "principle_id": "C4_portfolio_marginal_later",
                "description": "book/replay reward can only be used after null-separation and role checks pass",
                "hard_requirement": True,
            },
        ]
    )
    score_contract = pd.DataFrame(
        [
            {
                "score_component": "original_response_score",
                "source": "feature x transform x label/horizon response",
                "allowed_stage": "probe",
                "may_use": True,
            },
            {
                "score_component": "stale_null_margin",
                "source": "original score vector versus stale score vector",
                "allowed_stage": "probe_and_gate",
                "may_use": True,
            },
            {
                "score_component": "sign_flip_asymmetry",
                "source": "original score behavior versus sign-flipped score behavior",
                "allowed_stage": "probe_and_gate",
                "may_use": True,
            },
            {
                "score_component": "shuffle_time_margin",
                "source": "original score vector versus time-shuffle null",
                "allowed_stage": "probe_and_gate",
                "may_use": True,
            },
            {
                "score_component": "shuffle_symbol_margin",
                "source": "original score vector versus symbol-shuffle null",
                "allowed_stage": "probe_and_gate",
                "may_use": True,
            },
            {
                "score_component": "role_violation_penalty",
                "source": "field ontology / role enforcement ledger",
                "allowed_stage": "hard_gate",
                "may_use": True,
            },
            {
                "score_component": "family_breadth_bonus",
                "source": "semantic family and motif diversity",
                "allowed_stage": "selection_after_gate",
                "may_use": True,
            },
            {
                "score_component": "may_or_known_stress_score",
                "source": "known stress label or May-like post-selection veto result",
                "allowed_stage": "forbidden_for_compiler_score",
                "may_use": False,
            },
        ]
    )
    generation_funnel = pd.DataFrame(
        [
            {
                "level": "L0_field_operator_probe",
                "action": "probe field_type x operator with null-vector margins before derived feature promotion",
                "max_output_role": "probe_result",
            },
            {
                "level": "L1_single_field_factor_seed",
                "action": "promote only fields/transforms with non-null separation and non-L7 response evidence",
                "max_output_role": "ordinary_alpha_seed_or_regime_only",
            },
            {
                "level": "L2_compatible_pair_probe",
                "action": "test semantic-compatible field pairs only after both sides have L1 evidence",
                "max_output_role": "interaction_probe",
            },
            {
                "level": "L3_state_conditioned_factor",
                "action": "allow regime/neutralizer fields only as conditioners unless response-backed as signal",
                "max_output_role": "factor_candidate",
            },
            {
                "level": "L4_replay_candidate_packet",
                "action": "build full-universe vectors and control-null residual score packet before book replay",
                "max_output_role": "replay_candidate",
            },
        ]
    )
    blocked_patterns = pd.DataFrame(
        [
            {"pattern": "selected_top_bottom_only_orthogonalization", "status": "FORBIDDEN"},
            {"pattern": "control_dominated_candidate_expansion", "status": "FORBIDDEN"},
            {"pattern": "same_family_rerun_after_zero_survivors", "status": "FORBIDDEN"},
            {"pattern": "diagnostic_or_risk_defense_field_as_alpha_without_promotion", "status": "FORBIDDEN"},
            {"pattern": "formula_shape_expansion_without_null_margin", "status": "FORBIDDEN"},
            {"pattern": "May_or_known_stress_in_compiler_score", "status": "FORBIDDEN"},
        ]
    )
    next_audit = pd.DataFrame(
        [
            {
                "stage": "A7FF-CORE47E",
                "action": "audit existing feature/operator/field-family artifacts for control-null-aware compiler readiness",
                "executes_generation": False,
                "executes_replay": False,
                "executes_search": False,
            },
            {
                "stage": "A7FF-CORE48",
                "action": "if CORE47E passes, define bounded null-first factor seed generation contract",
                "executes_generation": False,
                "executes_replay": False,
                "executes_search": False,
            },
        ]
    )
    authorization = {
        "authorized": {
            "A7FF-CORE47E control-null-aware compiler readiness audit": True
        },
        "not_authorized": {
            "new_generation": True,
            "formula_search": True,
            "large_search": True,
            "same_family_rerun": True,
            "current_candidate_expansion": True,
            "alpha_proof": True,
            "shadow_paper_live": True,
        },
    }
    decision = "PASS_A7FFCORE47_CONTROL_NULL_AWARE_COMPILER_CONTRACT_READY_FOR_CORE47E"
    manifest = {
        "stage": "A7FF-CORE47",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE46",
        "source_decision": source.get("decision"),
        "source_selected_route": source.get("selected_route"),
        "decision": decision,
        "executes_generation": False,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core47e_audit": True,
        "authorizes_new_generation": False,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE47E control-null-aware compiler readiness audit",
    }
    compiler_principles.to_csv(RUNTIME / "a7ffcore47_compiler_principles.csv", index=False)
    score_contract.to_csv(RUNTIME / "a7ffcore47_score_contract.csv", index=False)
    generation_funnel.to_csv(RUNTIME / "a7ffcore47_generation_funnel.csv", index=False)
    blocked_patterns.to_csv(RUNTIME / "a7ffcore47_blocked_patterns.csv", index=False)
    next_audit.to_csv(RUNTIME / "a7ffcore47_next_audit_plan.csv", index=False)
    write_json(RUNTIME / "a7ffcore47_authorization_matrix.json", authorization)
    write_json(RUNTIME / "a7ffcore47_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE47 CONTROL-NULL-AWARE FACTOR COMPILER CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE47 defines the next feature-to-factor compiler after CORE45R/CORE46 found zero orthogonal book survivors. It is contract-only and does not execute generation, replay, search, proof, shadow, paper, or live.",
        "",
        "## Compiler Principles",
        "",
        md_table(compiler_principles),
        "",
        "## Score Contract",
        "",
        md_table(score_contract),
        "",
        "## Generation Funnel",
        "",
        md_table(generation_funnel),
        "",
        "## Blocked Patterns",
        "",
        md_table(blocked_patterns),
        "",
        "## Next Audit Plan",
        "",
        md_table(next_audit),
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
