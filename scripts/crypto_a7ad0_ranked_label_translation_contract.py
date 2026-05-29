from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ad0_ranked_label_translation_contract"
REPORT = REPO / "reports" / "CRYPTO_A7AD0_RANKED_LABEL_TRANSLATION_CONTRACT_20260529.md"

A7AC3_MANIFEST = REPO / "runtime" / "a7ac3_label_diversification_diagnostic" / "a7ac3_manifest.json"
A7AC3_DECISIONS = REPO / "runtime" / "a7ac3_label_diversification_diagnostic" / "a7ac3_label_neutralization_decisions.csv"


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

    a7ac3 = read_json(A7AC3_MANIFEST)
    if a7ac3.get("decision") != "HOLD_A7AC3_PARTIAL_LABEL_DIVERSIFICATION":
        raise SystemExit("A7AD-0 expects A7AC-3 partial label diversification HOLD")
    decisions = pd.read_csv(A7AC3_DECISIONS)
    source_summary = (
        decisions.groupby(["label_family", "neutralization_mode"], as_index=False)
        .agg(
            rows=("candidate_id", "count"),
            pass_rows=("decision", lambda x: int((x != "HOLD_A7AC3_LABEL_OR_NEUTRALIZATION_BLOCKED").sum())),
            candidates=("candidate_id", "nunique"),
        )
        .sort_values(["pass_rows", "rows"], ascending=[False, False])
    )
    translation_tests = pd.DataFrame(
        [
            {
                "test": "matched_label_translation",
                "definition": "for every L7 pass row, compare same candidate/horizon/neutralization under L0 and L1",
                "required": True,
            },
            {
                "test": "raw_relative_pnl_proxy",
                "definition": "L0/L1 validation, test, recent oriented spreads must all be positive",
                "required": True,
            },
            {
                "test": "control_dominance_after_translation",
                "definition": "translated L0/L1 row must have control_ratio < 1.0; >=0.80 remains warning",
                "required": True,
            },
            {
                "test": "neutralization_translation",
                "definition": "translation must hold under at least one non-global neutralization mode",
                "required": True,
            },
            {
                "test": "ranked_label_artifact_detection",
                "definition": "if L7 survives but L0/L1 do not, freeze as ranked-label diagnostic clue",
                "required": True,
            },
        ]
    )
    pass_gates = pd.DataFrame(
        [
            {"gate": "minimum_translated_candidates", "rule": ">= 2 candidates translate from L7 to L0/L1"},
            {"gate": "minimum_translated_modes", "rule": ">= 1 non-global neutralization mode has translated candidates"},
            {"gate": "control_clean_translation", "rule": "translated rows must have control_ratio < 1.0"},
            {"gate": "warning_disclosure", "rule": "0.80 <= control_ratio < 1.0 remains diagnostic-only"},
            {"gate": "no_search_authorization", "rule": "A7AD cannot authorize formula search, large search, alpha proof, shadow, paper, or live"},
        ]
    )
    experiment_record = {
        "date": "2026-05-29",
        "experiment_id": "20260529_a7ad0_ranked_label_translation_contract",
        "objective": "Define audit for whether L7 ranked-return clues translate into raw/relative PnL proxy.",
        "status": "completed",
        "mode": "light_contract",
        "inputs": {
            "a7ac3_manifest": str(A7AC3_MANIFEST),
            "a7ac3_decisions": str(A7AC3_DECISIONS),
        },
        "parameters": {
            "source_label": "L7_ranked_future_return",
            "translation_labels": ["L0_raw_forward_return", "L1_cross_sectional_relative_return"],
            "May_usage": "not used",
        },
        "outputs": {"runtime": str(RUNTIME), "report": str(REPORT)},
        "decision": "contract_only",
        "next_action": "A7AD-1 ranked-label translation audit",
    }
    decision = "PASS_A7AD0_RANKED_LABEL_TRANSLATION_CONTRACT_READY_FOR_A7AD1"
    manifest = {
        "stage": "A7AD-0",
        "generated_at": now_utc(),
        "decision": decision,
        "executes_contract_only": True,
        "executes_replay": False,
        "executes_search": False,
        "executes_training": False,
        "uses_may": False,
        "input_a7ac3_decision": a7ac3.get("decision"),
        "source_decision_rows": int(len(decisions)),
        "source_candidate_count": int(decisions["candidate_id"].nunique()),
        "authorizes_a7ad1_ranked_label_translation_audit": True,
        "authorizes_formula_search_execution": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }

    source_summary.to_csv(RUNTIME / "a7ad0_source_label_summary.csv", index=False)
    translation_tests.to_csv(RUNTIME / "a7ad0_translation_tests.csv", index=False)
    pass_gates.to_csv(RUNTIME / "a7ad0_pass_gates.csv", index=False)
    write_json(RUNTIME / "a7ad0_experiment_record.json", experiment_record)
    write_json(RUNTIME / "a7ad0_manifest.json", manifest)
    write_json(
        RUNTIME / "a7ad0_authorization_matrix.json",
        {
            "A7AD-0": {"status": decision},
            "A7AD-1_ranked_label_translation_audit": {"authorized": True},
            "formula_search_execution": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof": {"authorized": False},
            "shadow_paper_live": {"authorized": False},
        },
    )

    lines = [
        "# CRYPTO A7AD-0 RANKED LABEL TRANSLATION CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7AD-0 defines an audit for whether A7AC ranked-return clues translate into raw or cross-sectional relative PnL proxy. It does not execute replay, train, search, or authorize alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Source Label Summary",
        "",
        md_table(source_summary),
        "",
        "## Translation Tests",
        "",
        md_table(translation_tests),
        "",
        "## Pass Gates",
        "",
        md_table(pass_gates),
        "",
        "## Experiment Record",
        "",
        "```json",
        json.dumps(experiment_record, indent=2, sort_keys=True),
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
