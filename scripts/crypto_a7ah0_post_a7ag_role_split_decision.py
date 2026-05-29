from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ah0_post_a7ag_role_split_decision"
REPORT = REPO / "reports" / "CRYPTO_A7AH0_POST_A7AG_ROLE_SPLIT_DECISION_20260529.md"

A7AG5_MANIFEST = REPO / "runtime" / "a7ag5_clue_forensic_audit" / "a7ag5_manifest.json"
A7AG4_ROLE_SUMMARY = REPO / "runtime" / "a7ag4_clue_forensic_contract" / "a7ag4_role_summary.csv"
A7AG5_TRANSLATION_SUMMARY = REPO / "runtime" / "a7ag5_clue_forensic_audit" / "a7ag5_label_translation_summary.csv"
A7AG5_CONCENTRATION_SUMMARY = REPO / "runtime" / "a7ag5_clue_forensic_audit" / "a7ag5_concentration_summary.csv"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
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

    a7ag5 = read_json(A7AG5_MANIFEST)
    if a7ag5.get("decision") != "HOLD_A7AG5_NO_ORDINARY_LABEL_TRANSLATION":
        raise SystemExit("A7AG-5 is not in the expected HOLD state for A7AH-0 arbitration")

    role_summary = pd.read_csv(A7AG4_ROLE_SUMMARY)
    translation_summary = pd.read_csv(A7AG5_TRANSLATION_SUMMARY)
    concentration_summary = pd.read_csv(A7AG5_CONCENTRATION_SUMMARY)

    ordinary_translation = int(a7ag5.get("ordinary_label_translation_clue_count", 0))
    downside_count = int(a7ag5.get("input_clue_count", 0)) - int(role_summary.loc[
        role_summary["clue_role"].isin(["basis_premium_vol_adjusted_diagnostic", "neutralized_vol_adjusted_diagnostic"]),
        "clue_count",
    ].sum())
    concentration_blockers = int(a7ag5.get("concentration_blocker_count", 0))

    branch_rows = [
        {
            "branch_id": "B0_ordinary_alpha",
            "status": "HOLD",
            "evidence": "A7AG5 ordinary_label_translation_clue_count=0",
            "authorized_next": "A7AH1_ordinary_alpha_objective_rewrite_contract_only",
            "not_authorized": "formula_search_execution|large_search|alpha_proof|shadow_paper_live",
        },
        {
            "branch_id": "B1_vol_adjusted_diagnostic",
            "status": "DIAGNOSTIC_ONLY",
            "evidence": "A7AG4 has L5 vol-adjusted diagnostic clues but A7AG5 shows no L0/L1 translation",
            "authorized_next": "A7AH1_may_reuse_as_objective_input_no; diagnostic evidence only",
            "not_authorized": "ordinary_alpha_promotion|formula_search_execution|alpha_proof",
        },
        {
            "branch_id": "B2_downside_risk_defense",
            "status": "FORENSIC_ALLOWED",
            "evidence": f"A7AG4 downside risk-defense clues={downside_count}; A7AG5 concentration_blockers={concentration_blockers}",
            "authorized_next": "A7AH2_downside_risk_defense_forensic_contract_only",
            "not_authorized": "ordinary_alpha_promotion|live_risk_overlay|alpha_proof",
        },
    ]
    branch_df = pd.DataFrame(branch_rows)

    evidence_rows = [
        {"metric": "a7ag5_decision", "value": a7ag5.get("decision")},
        {"metric": "a7ag3_to_a7ag5_clues", "value": a7ag5.get("input_clue_count")},
        {"metric": "ordinary_label_translation_clue_count", "value": ordinary_translation},
        {"metric": "cost20_original_survivor_count", "value": a7ag5.get("cost20_original_survivor_count")},
        {"metric": "concentration_blocker_count", "value": concentration_blockers},
        {"metric": "formula_generation_overconservative", "value": "false; A7AG3 evaluated 96/96 and found 24 pilot clues"},
        {"metric": "ordinary_alpha_status", "value": "HOLD"},
        {"metric": "risk_defense_status", "value": "forensic_only"},
    ]
    evidence_df = pd.DataFrame(evidence_rows)

    ordinary_contract = {
        "stage": "A7AH-1",
        "name": "ordinary alpha objective rewrite contract",
        "purpose": "rewrite ordinary alpha objective after A7AG5 showed no L0/L1 translation",
        "must_not_use": [
            "L5_vol_adjusted_return_as_primary_alpha_label",
            "L6_downside_avoidance_as_primary_alpha_label",
            "May",
            "formula_search_execution",
        ],
        "allowed_contract_work": [
            "define L0/L1-first selector objective",
            "require ordinary label response before formula expansion",
            "keep vol-adjusted/downside fields as diagnostics or controls only",
            "define bounded A7AH1 dry rerank on existing A7AG queue",
        ],
    }
    risk_contract = {
        "stage": "A7AH-2",
        "name": "downside risk-defense forensic contract",
        "purpose": "audit whether L6 downside clues represent a coherent risk-defense state, not ordinary alpha",
        "must_audit": [
            "cost_ladder_5_10_20bps",
            "crash_state_conditioning",
            "top_loss_hour_attribution",
            "symbol_month_latent_concentration",
            "negative_controls_by_downside_label",
            "tradeability_as_risk_overlay_only",
        ],
        "not_authorized": [
            "ordinary_alpha_promotion",
            "live_risk_overlay",
            "alpha_proof",
        ],
    }

    decision = "PASS_A7AH0_POST_A7AG_ROLE_SPLIT_READY_FOR_A7AH1_A7AH2_CONTRACTS"
    manifest = {
        "stage": "A7AH-0",
        "generated_at": now_utc(),
        "decision": decision,
        "input_a7ag5_decision": a7ag5.get("decision"),
        "executes_role_split_decision": True,
        "executes_formula_generation": False,
        "executes_search": False,
        "executes_replay": False,
        "executes_training": False,
        "authorizes_a7ah1_ordinary_alpha_objective_rewrite_contract": True,
        "authorizes_a7ah2_downside_risk_defense_forensic_contract": True,
        "authorizes_formula_search_execution": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "uses_may": False,
        "ordinary_label_translation_clue_count": ordinary_translation,
        "concentration_blocker_count": concentration_blockers,
    }

    branch_df.to_csv(RUNTIME / "a7ah0_branch_decision_matrix.csv", index=False)
    evidence_df.to_csv(RUNTIME / "a7ah0_evidence_summary.csv", index=False)
    translation_summary.to_csv(RUNTIME / "a7ah0_input_label_translation_summary.csv", index=False)
    concentration_summary.to_csv(RUNTIME / "a7ah0_input_concentration_summary.csv", index=False)
    write_json(RUNTIME / "a7ah0_manifest.json", manifest)
    write_json(RUNTIME / "a7ah0_ordinary_alpha_objective_rewrite_next_contract.json", ordinary_contract)
    write_json(RUNTIME / "a7ah0_downside_risk_defense_next_contract.json", risk_contract)
    write_json(
        RUNTIME / "a7ah0_authorization_matrix.json",
        {
            "A7AH-0": {"status": decision},
            "A7AH-1_ordinary_alpha_objective_rewrite_contract": {"authorized": True},
            "A7AH-2_downside_risk_defense_forensic_contract": {"authorized": True},
            "formula_search_execution": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof_shadow_paper_live": {"authorized": False},
        },
    )

    lines = [
        "# CRYPTO A7AH-0 POST-A7AG ROLE SPLIT DECISION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7AH-0 freezes the A7AG result and splits ordinary alpha work from downside/risk-defense diagnostics. It does not generate formulas, replay, search, train, or authorize proof.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Evidence Summary",
        "",
        md_table(evidence_df),
        "",
        "## Branch Decision Matrix",
        "",
        md_table(branch_df),
        "",
        "## A7AH-1 Ordinary Alpha Contract Stub",
        "",
        "```json",
        json.dumps(ordinary_contract, indent=2, sort_keys=True),
        "```",
        "",
        "## A7AH-2 Risk Defense Contract Stub",
        "",
        "```json",
        json.dumps(risk_contract, indent=2, sort_keys=True),
        "```",
        "",
        "## Boundary",
        "",
        "```text",
        "A7AG did not fail because formulas were over-constrained: 96/96 evaluated and 24 pilot clues were found.",
        "A7AG failed ordinary alpha promotion because no clue translated to L0/L1 ordinary labels.",
        "Downside/risk-defense clues are separated from ordinary alpha evidence.",
        "No formula search, large search, alpha proof, shadow, paper, or live is authorized.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
