from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore35_search_readiness_arbitration"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE35_SEARCH_READINESS_ARBITRATION_20260602.md"
CORE30E = REPO / "runtime" / "a7ffcore30e_bounded_numeric_probe" / "a7ffcore30e_manifest.json"
CORE32E = REPO / "runtime" / "a7ffcore32e_replay_preflight_execution" / "a7ffcore32e_manifest.json"
CORE33E = REPO / "runtime" / "a7ffcore33e_bounded_replay_execution" / "a7ffcore33e_manifest.json"
CORE34ER = REPO / "runtime" / "a7ffcore34er_repair_forensic" / "a7ffcore34er_manifest.json"
CORE34ER_FAMILY = REPO / "runtime" / "a7ffcore34er_repair_forensic" / "a7ffcore34er_family_failure_diagnostic.csv"


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
    core30e = read_json(CORE30E)
    core32e = read_json(CORE32E)
    core33e = read_json(CORE33E)
    core34er = read_json(CORE34ER)
    if core34er.get("decision") != "PASS_A7FFCORE34ER_REPAIR_FORENSIC_READY_FOR_CORE35_ARBITRATION":
        raise SystemExit(f"CORE34ER not ready for CORE35: {core34er.get('decision')}")
    family_failure = pd.read_csv(CORE34ER_FAMILY)
    evidence = pd.DataFrame(
        [
            {
                "stage": "CORE30E numeric probe",
                "decision": core30e.get("decision"),
                "positive_evidence": "113 clean numeric clues across 3 families",
                "negative_evidence": "numeric-only; no portfolio/replay proof",
            },
            {
                "stage": "CORE32E replay preflight",
                "decision": core32e.get("decision"),
                "positive_evidence": "21 preflight candidates across 3 families",
                "negative_evidence": "preflight only; no tradable replay",
            },
            {
                "stage": "CORE33E bounded replay",
                "decision": core33e.get("decision"),
                "positive_evidence": "bounded replay executed",
                "negative_evidence": "survivor_count=0",
            },
            {
                "stage": "CORE34E/34ER repair",
                "decision": core34er.get("decision"),
                "positive_evidence": "repair failure diagnosed",
                "negative_evidence": "train_control_fail_count=12; OOS positive still insufficient",
            },
        ]
    )
    authorization = pd.DataFrame(
        [
            {"task": "large_search", "status": "NOT_AUTHORIZED", "reason": "bounded replay and repair survivor_count=0"},
            {"task": "formula_search", "status": "NOT_AUTHORIZED", "reason": "numeric/preflight clues did not survive replay proxy"},
            {"task": "same_queue_rerun", "status": "NOT_AUTHORIZED", "reason": "CORE34E exhausted train-only orientation/control repair"},
            {"task": "alpha_proof", "status": "NOT_AUTHORIZED", "reason": "no replay survivor/proof object"},
            {"task": "shadow_paper_live", "status": "NOT_AUTHORIZED", "reason": "no alpha proof and no replay survivor"},
            {
                "task": "A7FF-CORE36 replay-objective/portfolio-proxy reset contract",
                "status": "AUTHORIZED_CONTRACT_ONLY",
                "reason": "failure moved from numeric feature response to replay/portfolio translation",
            },
        ]
    )
    next_contract = pd.DataFrame(
        [
            {
                "contract_item": "label_portfolio_alignment",
                "required_change": "separate IC-like numeric response from executable spread; define portfolio objective before generation",
            },
            {
                "contract_item": "train_only_orientation_policy",
                "required_change": "orientation can be used only if train control clean and OOS split coverage survives",
            },
            {
                "contract_item": "control_first_replay_queue",
                "required_change": "control ratio must gate replay candidates before score ranking",
            },
            {
                "contract_item": "family_specific_response_roles",
                "required_change": "F1a may be regime/hedge-like; F1b/F2a need stronger control dominance filter",
            },
        ]
    )
    decision = "HOLD_A7FFCORE35_SEARCH_NOT_READY_REPLAY_TRANSLATION_FAILURE"
    manifest = {
        "stage": "A7FF-CORE35",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE34ER",
        "source_decision": core34er.get("decision"),
        "decision": decision,
        "dominant_failure": "numeric_response_does_not_translate_to_bounded_replay_survivors",
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core36_contract": True,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE36 replay-objective/portfolio-proxy reset contract",
    }
    evidence.to_csv(RUNTIME / "a7ffcore35_evidence_matrix.csv", index=False)
    family_failure.to_csv(RUNTIME / "a7ffcore35_family_failure_snapshot.csv", index=False)
    authorization.to_csv(RUNTIME / "a7ffcore35_authorization_matrix.csv", index=False)
    next_contract.to_csv(RUNTIME / "a7ffcore35_next_contract_requirements.csv", index=False)
    write_json(RUNTIME / "a7ffcore35_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE35 SEARCH READINESS ARBITRATION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE35 arbitrates search readiness after independent-family numeric/preflight/replay repair. It does not execute replay, search, large search, alpha proof, shadow, paper, or live.",
        "",
        "## Evidence Matrix",
        "",
        md_table(evidence),
        "",
        "## Family Failure Snapshot",
        "",
        md_table(family_failure),
        "",
        "## Authorization Matrix",
        "",
        md_table(authorization),
        "",
        "## Next Contract Requirements",
        "",
        md_table(next_contract),
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
