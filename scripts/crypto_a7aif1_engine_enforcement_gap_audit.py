from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7aif1_engine_enforcement_gap_audit"
REPORT = REPO / "reports" / "CRYPTO_A7AIF1_ENGINE_ENFORCEMENT_GAP_AUDIT_20260529.md"

A7AIF0_MANIFEST = REPO / "runtime" / "a7aif0_field_contract_enforcement_ledger" / "a7aif0_manifest.json"
A7AIF0_LEDGER = REPO / "runtime" / "a7aif0_field_contract_enforcement_ledger" / "a7aif0_semantic_field_enforcement_ledger.csv"
MOTIF_PACK = REPO / "config" / "crypto_formula_gen_v2_motif_pack_v1.json"
FORMULA_GEN = REPO / "alphafactory_crypto" / "engines" / "formula_gen_v2_adapter.py"
FEATURE_ALGEBRA = REPO / "alphafactory_crypto" / "engines" / "feature_algebra.py"
A7AA2_POLICY = REPO / "runtime" / "a7aa2_feature_role_classification" / "a7aa2_selector_rewrite_seed_policy.json"
A7AH1_CONTRACT = REPO / "runtime" / "a7ah1_ordinary_alpha_objective_rewrite_contract" / "a7ah1_manifest.json"
A7AH1D_MANIFEST = REPO / "runtime" / "a7ah1d_ordinary_alpha_dry_rerank" / "a7ah1d_manifest.json"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def status_row(component: str, check: str, status: str, evidence: str, severity: str, required_action: str) -> dict[str, str]:
    return {
        "component": component,
        "check": check,
        "status": status,
        "severity": severity,
        "evidence": evidence,
        "required_action": required_action,
    }


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    f0_manifest = read_json(A7AIF0_MANIFEST)
    if not f0_manifest.get("authorizes_a7aif1_engine_enforcement_gap_audit"):
        raise SystemExit("A7AI-F0 does not authorize A7AI-F1")

    ledger = pd.read_csv(A7AIF0_LEDGER)
    motif_pack = read_json(MOTIF_PACK)
    formula_text = read_text(FORMULA_GEN)
    algebra_text = read_text(FEATURE_ALGEBRA)
    a7aa2_policy = read_json(A7AA2_POLICY)
    a7ah1_contract = read_json(A7AH1_CONTRACT)
    a7ah1d_manifest = read_json(A7AH1D_MANIFEST)

    rows: list[dict[str, str]] = []

    generator_has_field_registry = "field_registry" in formula_text and "field_families" in formula_text
    generator_has_unknown_field_check = (
        "unknown_field" in formula_text
        or "unknown field" in formula_text
        or "candidate_fields if field not in allowed_fields" in formula_text
    )
    generator_has_semantic_ledger = (
        "a7aif0" in formula_text.lower()
        or "semantic_role" in formula_text
        or "feature_role" in formula_text
        or "field_enforcement" in formula_text
    )
    generator_has_mode_filter = "ordinary_alpha_allowed" in formula_text or "diagnostic_allowed" in formula_text or "risk_defense_allowed" in formula_text
    rows.append(
        status_row(
            "FormulaGenV2Adapter",
            "loads motif field registry",
            "PASS" if generator_has_field_registry else "HOLD",
            "field_registry/field_families found" if generator_has_field_registry else "field registry not found",
            "info" if generator_has_field_registry else "hard_gap",
            "keep motif registry as syntax source",
        )
    )
    rows.append(
        status_row(
            "FormulaGenV2Adapter",
            "rejects unknown fields",
            "PASS" if generator_has_unknown_field_check else "HOLD",
            "unknown field validation found" if generator_has_unknown_field_check else "unknown field validation not found",
            "info" if generator_has_unknown_field_check else "hard_gap",
            "keep field existence validation",
        )
    )
    rows.append(
        status_row(
            "FormulaGenV2Adapter",
            "enforces semantic field ledger",
            "PASS" if generator_has_semantic_ledger else "HARD_GAP",
            "semantic ledger hooks found" if generator_has_semantic_ledger else "generator only sees config field families; no A7AI-F0 semantic ledger hook",
            "hard_gap" if not generator_has_semantic_ledger else "info",
            "add optional semantic ledger loader and per-mode field allowlist",
        )
    )
    rows.append(
        status_row(
            "FormulaGenV2Adapter",
            "supports mode-specific field roles",
            "PASS" if generator_has_mode_filter else "HARD_GAP",
            "mode-specific role filter found" if generator_has_mode_filter else "no ordinary/diagnostic/risk-defense field filter in generator",
            "hard_gap" if not generator_has_mode_filter else "info",
            "filter sampled fields by ordinary_alpha_allowed / diagnostic_allowed / risk_defense_allowed",
        )
    )

    evaluator_mentions_caller_timing = "timing is audited by" in algebra_text.lower()
    evaluator_has_allowed_fields = "allowed_fields" in algebra_text
    evaluator_has_semantic_ledger = (
        "semantic_role" in algebra_text
        or "field_contract" in algebra_text
        or "enforcement_ledger" in algebra_text
    )
    rows.append(
        status_row(
            "CryptoFeatureAlgebra",
            "evaluates only allowed fields",
            "PASS" if evaluator_has_allowed_fields else "HOLD",
            "allowed_fields present" if evaluator_has_allowed_fields else "allowed_fields not found",
            "info" if evaluator_has_allowed_fields else "hard_gap",
            "keep evaluator field existence guard",
        )
    )
    rows.append(
        status_row(
            "CryptoFeatureAlgebra",
            "local timing enforcement",
            "HARD_GAP" if evaluator_mentions_caller_timing and not evaluator_has_semantic_ledger else "PASS",
            (
                "optional field_contract hook found; caller timing delegation remains default when no contract is passed"
                if evaluator_has_semantic_ledger
                else "feature_algebra delegates timing to caller"
            ),
            "hard_gap" if evaluator_mentions_caller_timing and not evaluator_has_semantic_ledger else "info",
            "pass A7AI-F0 field_contract in enforced replay callers",
        )
    )

    motif_constraints = motif_pack.get("constraints") or {}
    constraints_clean = (
        motif_constraints.get("same_bar_execution_allowed") is False
        and motif_constraints.get("fixed_delay_stress_required") is False
        and motif_constraints.get("field_native_latency_audit_required") is True
    )
    rows.append(
        status_row(
            "MotifPack",
            "declares crypto timing policy",
            "PASS" if constraints_clean else "HOLD",
            json.dumps(motif_constraints, sort_keys=True),
            "info" if constraints_clean else "hard_gap",
            "preserve field-native latency policy; no fixed +2h stress gate",
        )
    )
    motif_fields = sorted({field for fields in (motif_pack.get("field_families") or {}).values() for field in fields})
    ledger_fields = set(ledger["field_name"].astype(str))
    missing_motif_fields = [field for field in motif_fields if field not in ledger_fields]
    rows.append(
        status_row(
            "MotifPack",
            "all motif fields exist in A7AI-F0 ledger",
            "PASS" if not missing_motif_fields else "HARD_GAP",
            "missing=" + ",".join(missing_motif_fields[:20]) if missing_motif_fields else "all motif fields covered",
            "hard_gap" if missing_motif_fields else "info",
            "do not sample missing-contract motif fields",
        )
    )

    allowed_seed_fields = a7aa2_policy.get("allowed_seed_fields", [])
    rows.append(
        status_row(
            "SelectorPolicy",
            "primitive-response seed policy exists",
            "PASS" if allowed_seed_fields else "HOLD",
            f"allowed_seed_fields={len(allowed_seed_fields)}",
            "info" if allowed_seed_fields else "hard_gap",
            "use seed role as selector target input, not as formula-search authorization",
        )
    )
    rows.append(
        status_row(
            "SelectorPolicy",
            "ordinary alpha dry rerank remains non-executing",
            "PASS" if a7ah1d_manifest and not a7ah1d_manifest.get("authorizes_formula_search_execution") else "HOLD",
            f"a7ah1d_decision={a7ah1d_manifest.get('decision', '')}; formula_search={a7ah1d_manifest.get('authorizes_formula_search_execution', '')}",
            "info" if a7ah1d_manifest and not a7ah1d_manifest.get("authorizes_formula_search_execution") else "hard_gap",
            "preserve no-search boundary until engine enforcement is patched",
        )
    )
    rows.append(
        status_row(
            "Authorization",
            "A7AH ordinary contract does not authorize large search",
            "PASS" if a7ah1_contract and not a7ah1_contract.get("authorizes_large_search", False) else "HOLD",
            f"a7ah1_decision={a7ah1_contract.get('decision', '')}",
            "info" if a7ah1_contract and not a7ah1_contract.get("authorizes_large_search", False) else "hard_gap",
            "keep A7AI as hardening gate, not search execution",
        )
    )

    gap_matrix = pd.DataFrame(rows)
    hard_gaps = gap_matrix[gap_matrix["severity"].eq("hard_gap") & gap_matrix["status"].isin(["HARD_GAP", "HOLD"])].copy()
    decision = (
        "PASS_A7AIF1_ENGINE_ENFORCEMENT_CONNECTED"
        if hard_gaps.empty
        else "HOLD_A7AIF1_ENGINE_ENFORCEMENT_GAPS_PRESENT"
    )
    patch_status = "implemented_or_present" if hard_gaps.empty else "required"
    patch_plan = pd.DataFrame(
        [
            {
                "patch_id": "A7AI-F2-1",
                "component": "FormulaGenV2Adapter",
                "action": "add semantic ledger loader and per-mode allowed field lists",
                "status": patch_status,
                "blocks_search": bool(not hard_gaps.empty),
            },
            {
                "patch_id": "A7AI-F2-2",
                "component": "FormulaGenV2Adapter",
                "action": "reject fields marked label_only, future_dependent, fixed_delay_required, same_bar_allowed, or missing contract",
                "status": patch_status,
                "blocks_search": bool(not hard_gaps.empty),
            },
            {
                "patch_id": "A7AI-F2-3",
                "component": "ReplayCaller",
                "action": "feed A7AI-F0 timing and role ledger into evaluator caller before numeric replay",
                "status": patch_status,
                "blocks_search": bool(not hard_gaps.empty),
            },
            {
                "patch_id": "A7AI-F2-4",
                "component": "Selector",
                "action": "consume selector_primary_allowed and selector_diagnostic_allowed instead of raw motif family membership",
                "status": "artifact_policy_present" if hard_gaps.empty else "required",
                "blocks_search": bool(not hard_gaps.empty),
            },
        ]
    )
    manifest = {
        "stage": "A7AI-F1",
        "generated_at": now_utc(),
        "decision": decision,
        "input_a7aif0_decision": f0_manifest.get("decision"),
        "executes_search": False,
        "executes_replay": False,
        "executes_training": False,
        "uses_may": False,
        "hard_gap_count": int(len(hard_gaps)),
        "hard_gaps": hard_gaps[["component", "check", "required_action"]].to_dict("records"),
        "authorizes_a7aif2_engine_patch_contract": not hard_gaps.empty,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    authorization = {
        "A7AI-F1": {"status": decision},
        "A7AI-F2_engine_patch_contract": {"authorized": not hard_gaps.empty},
        "formula_search": {"authorized": False},
        "large_search": {"authorized": False},
        "alpha_proof": {"authorized": False},
        "shadow_paper_live": {"authorized": False},
    }

    gap_matrix.to_csv(RUNTIME / "a7aif1_engine_enforcement_gap_matrix.csv", index=False)
    hard_gaps.to_csv(RUNTIME / "a7aif1_hard_gaps.csv", index=False)
    patch_plan.to_csv(RUNTIME / "a7aif1_required_patch_plan.csv", index=False)
    write_json(RUNTIME / "a7aif1_manifest.json", manifest)
    write_json(RUNTIME / "a7aif1_authorization_matrix.json", authorization)

    lines = [
        "# CRYPTO A7AI-F1 ENGINE ENFORCEMENT GAP AUDIT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7AI-F1 checks whether the generator, evaluator caller boundary, motif pack, and selector artifacts actually consume the A7AI-F0 semantic enforcement ledger. It does not execute replay or search.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Engine Enforcement Gap Matrix",
        "",
        md_table(gap_matrix, 120),
        "",
        "## Enforcement Patch Status",
        "",
        md_table(patch_plan, 80),
        "",
        "## Boundary",
        "",
        "```text",
        "No formula search is authorized.",
        (
            "A7AI-F2 patch contract is not needed because the enforcement hooks are connected."
            if hard_gaps.empty
            else "A7AI-F2 may patch enforcement plumbing, but not train, replay, or promote candidates."
        ),
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
