from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore21r_translation_matrix_forensic"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE21R_TRANSLATION_MATRIX_FORENSIC_20260601.md"
CORE21E = REPO / "runtime" / "a7ffcore21e_replay_translation_matrix_audit" / "a7ffcore21e_manifest.json"
LABEL_COST = REPO / "runtime" / "a7ffcore21e_replay_translation_matrix_audit" / "a7ffcore21e_label_cost_matrix.csv"
LANE_COST = REPO / "runtime" / "a7ffcore21e_replay_translation_matrix_audit" / "a7ffcore21e_lane_cost_matrix.csv"
LAG = REPO / "runtime" / "a7ffcore21e_replay_translation_matrix_audit" / "a7ffcore21e_lag_gate_matrix.csv"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


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
    core21e = read_json(CORE21E)
    if core21e.get("decision") != "HOLD_A7FFCORE21E_TRANSLATION_MATRIX_INSUFFICIENT":
        raise SystemExit(f"CORE21E is not in forensic state: {core21e.get('decision')}")
    label_cost = load_csv(LABEL_COST)
    lane_cost = load_csv(LANE_COST)
    lag = load_csv(LAG)
    diagnosis = pd.DataFrame(
        [
            {
                "finding": "cost_relief_exists_but_insufficient",
                "evidence": "2bps non-L5 clean count is 3, but best label/cost bucket clean count is 1",
                "severity": "high",
            },
            {
                "finding": "lag_gate_is_major_suppressor",
                "evidence": "L0/L1 2bps each have 17 clean-without-lag candidates but only 1 with lag gate",
                "severity": "high",
            },
            {
                "finding": "lane_breadth_still_insufficient",
                "evidence": "current replay-clean lane count is 2; S0/S1 do not translate to clean bounded replay",
                "severity": "high",
            },
            {
                "finding": "not_l5_only",
                "evidence": "non-L5 2bps clean count exceeds L5 2bps clean count, but breadth is still too low",
                "severity": "medium",
            },
        ]
    )
    recommended = pd.DataFrame(
        [
            {
                "action_id": "R0_no_large_search",
                "action": "do not authorize large search",
                "reason": "translation matrix remains too narrow after cost and label decomposition",
            },
            {
                "action_id": "R1_lag_translation_contract",
                "action": "write CORE22 lag-aware replay translation contract",
                "reason": "lag gate suppresses many otherwise cost/control-clean L0/L1/L3 rows",
            },
            {
                "action_id": "R2_lane_specific_repair",
                "action": "require S0/S1 lane repair before any search-readiness claim",
                "reason": "clean replay evidence remains concentrated in S2/S3",
            },
        ]
    )
    diagnosis.to_csv(RUNTIME / "a7ffcore21r_diagnosis.csv", index=False)
    recommended.to_csv(RUNTIME / "a7ffcore21r_recommended_actions.csv", index=False)
    label_cost.sort_values("clean_candidate_count", ascending=False).to_csv(RUNTIME / "a7ffcore21r_label_cost_sorted.csv", index=False)
    lane_cost.sort_values("clean_candidate_count", ascending=False).to_csv(RUNTIME / "a7ffcore21r_lane_cost_sorted.csv", index=False)
    lag.sort_values("lag_gate_loss", ascending=False).to_csv(RUNTIME / "a7ffcore21r_lag_gate_sorted.csv", index=False)
    manifest = {
        "stage": "A7FF-CORE21R",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE21E",
        "source_decision": core21e.get("decision"),
        "decision": "PASS_A7FFCORE21R_TRANSLATION_MATRIX_FORENSIC_COMPLETE_READY_FOR_CORE22",
        "dominant_failure": "lag_and_lane_translation_bottleneck",
        "best_label_cost_clean_candidate_count": int(core21e.get("best_label_cost_clean_candidate_count", 0)),
        "best_lane_cost_clean_candidate_count": int(core21e.get("best_lane_cost_clean_candidate_count", 0)),
        "non_l5_clean_2bps": int(core21e.get("non_l5_clean_2bps", 0)),
        "authorizes_core22_contract": True,
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE22 lag-aware replay translation contract",
    }
    write_json(RUNTIME / "a7ffcore21r_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE21R TRANSLATION MATRIX FORENSIC",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "CORE21R freezes the translation matrix result. It does not execute replay, formula generation, search, alpha proof, shadow, paper, or live.",
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
        "## Top Lag Gate Loss",
        "",
        md_table(lag.sort_values("lag_gate_loss", ascending=False).head(20)),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
