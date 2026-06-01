from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore37x_route_arbitration"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE37X_ROUTE_ARBITRATION_20260602.md"
CORE30E = REPO / "runtime" / "a7ffcore30e_bounded_numeric_probe" / "a7ffcore30e_manifest.json"
CORE32E = REPO / "runtime" / "a7ffcore32e_replay_preflight_execution" / "a7ffcore32e_manifest.json"
CORE33E = REPO / "runtime" / "a7ffcore33e_bounded_replay_execution" / "a7ffcore33e_manifest.json"
CORE34E = REPO / "runtime" / "a7ffcore34e_orientation_control_repair_execution" / "a7ffcore34e_manifest.json"
CORE36E = REPO / "runtime" / "a7ffcore36e_replay_objective_reset_execution" / "a7ffcore36e_manifest.json"
CORE36ER = REPO / "runtime" / "a7ffcore36er_replay_objective_forensic" / "a7ffcore36er_manifest.json"
CORE36ER_FAMILY = REPO / "runtime" / "a7ffcore36er_replay_objective_forensic" / "a7ffcore36er_family_diagnosis.csv"


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
    core34e = read_json(CORE34E)
    core36e = read_json(CORE36E)
    source = read_json(CORE36ER)
    if source.get("decision") != "PASS_A7FFCORE36ER_REPLAY_OBJECTIVE_FORENSIC_COMPLETE_READY_FOR_CORE37X":
        raise SystemExit(f"CORE36ER not ready for CORE37X: {source.get('decision')}")

    family = pd.read_csv(CORE36ER_FAMILY)
    evidence = pd.DataFrame(
        [
            {
                "evidence_id": "E0_numeric_response",
                "stage": "CORE30E",
                "decision": core30e.get("decision"),
                "positive": "113 clean numeric clues across 3 independent families",
                "negative": "numeric response did not translate to bounded replay survivors",
            },
            {
                "evidence_id": "E1_replay_preflight",
                "stage": "CORE32E",
                "decision": core32e.get("decision"),
                "positive": "21 replay-preflight candidates across 3 families",
                "negative": "preflight evidence remained weaker than executable spread replay",
            },
            {
                "evidence_id": "E2_bounded_replay",
                "stage": "CORE33E",
                "decision": core33e.get("decision"),
                "positive": "bounded replay executed over existing candidates",
                "negative": "survivor_count=0",
            },
            {
                "evidence_id": "E3_orientation_control_repair",
                "stage": "CORE34E",
                "decision": core34e.get("decision"),
                "positive": "train-only orientation/control repair executed",
                "negative": "survivor_count=0 after repair",
            },
            {
                "evidence_id": "E4_replay_objective_reset",
                "stage": "CORE36E/36ER",
                "decision": core36e.get("decision"),
                "positive": "executable-spread-first rescoring isolated 3 train-pass F1a candidates",
                "negative": "selected_count=0; F1a OOS split unstable; F1b/F2a train objective/control fail",
            },
        ]
    )
    route_scorecard = pd.DataFrame(
        [
            {
                "route": "R0_same_queue_rerun",
                "status": "REJECT",
                "reason": "CORE34E and CORE36E already exhausted orientation/control and executable-objective rescoring",
                "authorizes_next": False,
            },
            {
                "route": "R1_large_formula_search",
                "status": "REJECT",
                "reason": "large search would amplify numeric-positive/replay-negative structures without executable translation",
                "authorizes_next": False,
            },
            {
                "route": "R2_more_independent_family_generation",
                "status": "HOLD",
                "reason": "independent data families show numeric response, but replay objective/label book still fails",
                "authorizes_next": False,
            },
            {
                "route": "R3_portfolio_label_objective_contract",
                "status": "AUTHORIZE_CONTRACT_ONLY",
                "reason": "failure is in label/book/executable spread translation, so next step must define executable portfolio-label objective before generation",
                "authorizes_next": True,
            },
        ]
    )
    frozen_paths = pd.DataFrame(
        [
            {"path": "CORE33/34/36 same candidate queue", "status": "FROZEN", "reason": "zero selected executable survivors"},
            {"path": "same direct numeric-response objective", "status": "FROZEN", "reason": "numeric response does not survive bounded replay"},
            {"path": "search before executable objective", "status": "BLOCKED", "reason": "selector target would reward non-executable clues"},
            {"path": "alpha proof / shadow / paper / live", "status": "BLOCKED", "reason": "no replay survivor or proof object"},
        ]
    )
    authorized_next = pd.DataFrame(
        [
            {
                "task": "A7FF-CORE38 executable portfolio-label objective contract",
                "status": "AUTHORIZED_CONTRACT_ONLY",
                "scope": "define labels/book proxies/cost/control gates for executable translation; no generation or replay",
            }
        ]
    )
    decision = "PASS_A7FFCORE37X_ROUTE_ARBITRATION_READY_FOR_CORE38_CONTRACT"
    manifest = {
        "stage": "A7FF-CORE37X",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE36ER",
        "source_decision": source.get("decision"),
        "decision": decision,
        "dominant_failure": source.get("dominant_failure"),
        "selected_route": "R3_portfolio_label_objective_contract",
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core38_contract": True,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE38 executable portfolio-label objective contract",
    }
    evidence.to_csv(RUNTIME / "a7ffcore37x_evidence_matrix.csv", index=False)
    family.to_csv(RUNTIME / "a7ffcore37x_family_diagnosis_snapshot.csv", index=False)
    route_scorecard.to_csv(RUNTIME / "a7ffcore37x_route_scorecard.csv", index=False)
    frozen_paths.to_csv(RUNTIME / "a7ffcore37x_frozen_paths.csv", index=False)
    authorized_next.to_csv(RUNTIME / "a7ffcore37x_authorized_next.csv", index=False)
    write_json(RUNTIME / "a7ffcore37x_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE37X ROUTE ARBITRATION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE37X arbitrates the route after CORE36E/36ER froze the replay-objective reset failure. It does not run replay, generation, search, alpha proof, shadow, paper, or live.",
        "",
        "## Selected Route",
        "",
        "`R3_portfolio_label_objective_contract`",
        "",
        "The current independent-family chain has numeric response and preflight evidence, but it does not translate into executable spread survivors. The next allowed work is a contract for executable portfolio-label objectives, not more formula generation.",
        "",
        "## Evidence Matrix",
        "",
        md_table(evidence),
        "",
        "## Route Scorecard",
        "",
        md_table(route_scorecard),
        "",
        "## Frozen Paths",
        "",
        md_table(frozen_paths),
        "",
        "## Authorized Next",
        "",
        md_table(authorized_next),
        "",
        "## Family Diagnosis Snapshot",
        "",
        md_table(family),
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
