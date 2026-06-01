from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore22r_lag_translation_forensic"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE22R_LAG_TRANSLATION_FORENSIC_20260601.md"
CORE22E = REPO / "runtime" / "a7ffcore22e_lag_aware_replay_translation_audit" / "a7ffcore22e_manifest.json"
MATRIX = REPO / "runtime" / "a7ffcore22e_lag_aware_replay_translation_audit" / "a7ffcore22e_lag_translation_matrix.csv"


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
    source = read_json(CORE22E)
    if source.get("decision") != "HOLD_A7FFCORE22E_LAG_TRANSLATION_INSUFFICIENT":
        raise SystemExit(f"CORE22E is not in forensic state: {source.get('decision')}")
    matrix = pd.read_csv(MATRIX)
    diagnosis = pd.DataFrame(
        [
            {
                "finding": "same_bar_diagnostic_excess",
                "evidence": f"same-bar diagnostic count {source.get('best_same_bar_diagnostic_count')} vs one-bar count {source.get('best_one_bar_clean_candidate_count')}",
                "interpretation": "current packet has strong timing fragility",
            },
            {
                "finding": "one_bar_lane_breadth_insufficient",
                "evidence": f"one-bar lane count {source.get('best_one_bar_clean_lane_count')} < 3",
                "interpretation": "executable evidence is not broad enough for search readiness",
            },
            {
                "finding": "large_search_not_justified",
                "evidence": "failure occurs after governance/materialization/preflight and before search",
                "interpretation": "expanding formula generation would amplify timing-fragile structures",
            },
        ]
    )
    recommended = pd.DataFrame(
        [
            {
                "action_id": "R0_freeze_core22_path",
                "action": "freeze current locked-packet replay path as timing-fragile",
                "reason": "same-bar diagnostic overwhelms one-bar executable supply",
            },
            {
                "action_id": "R1_core23_contract",
                "action": "write CORE23 executable-horizon redesign contract",
                "reason": "next work must target lower-turnover/horizon/execution framing, not bigger search",
            },
            {
                "action_id": "R2_no_search",
                "action": "continue blocking large search and formula expansion",
                "reason": "one-bar clean evidence is 4 candidates across 2 lanes",
            },
        ]
    )
    diagnosis.to_csv(RUNTIME / "a7ffcore22r_diagnosis.csv", index=False)
    recommended.to_csv(RUNTIME / "a7ffcore22r_recommended_actions.csv", index=False)
    matrix.to_csv(RUNTIME / "a7ffcore22r_lag_translation_matrix.csv", index=False)
    manifest = {
        "stage": "A7FF-CORE22R",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE22E",
        "source_decision": source.get("decision"),
        "decision": "PASS_A7FFCORE22R_LAG_TRANSLATION_FORENSIC_COMPLETE_READY_FOR_CORE23",
        "dominant_failure": "same_bar_diagnostic_dominates_one_bar_executable",
        "best_one_bar_clean_candidate_count": int(source.get("best_one_bar_clean_candidate_count", 0)),
        "best_one_bar_clean_lane_count": int(source.get("best_one_bar_clean_lane_count", 0)),
        "best_same_bar_diagnostic_count": int(source.get("best_same_bar_diagnostic_count", 0)),
        "authorizes_core23_contract": True,
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE23 executable-horizon redesign contract",
    }
    write_json(RUNTIME / "a7ffcore22r_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE22R LAG TRANSLATION FORENSIC",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "CORE22R freezes the lag translation failure. It does not execute replay, formula generation, search, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Diagnosis",
        "",
        md_table(diagnosis),
        "",
        "## Recommended Actions",
        "",
        md_table(recommended),
        "",
        "## Lag Matrix",
        "",
        md_table(matrix),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
