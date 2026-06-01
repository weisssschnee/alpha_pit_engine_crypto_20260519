from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore19ser_replay_repair_forensic"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE19SER_REPLAY_REPAIR_FORENSIC_20260601.md"
CORE19SE = REPO / "runtime" / "a7ffcore19se_bounded_replay_repair_execution" / "a7ffcore19se_manifest.json"
COST_SUMMARY = REPO / "runtime" / "a7ffcore19se_bounded_replay_repair_execution" / "a7ffcore19se_cost_tier_clean_summary.csv"
DIAGNOSIS = REPO / "runtime" / "a7ffcore19se_bounded_replay_repair_execution" / "a7ffcore19se_diagnosis.csv"


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
    se = read_json(CORE19SE)
    if se.get("decision") != "HOLD_A7FFCORE19SE_REPLAY_REPAIR_INSUFFICIENT":
        raise SystemExit(f"CORE19SE is not in forensic state: {se.get('decision')}")
    cost_summary = load_csv(COST_SUMMARY)
    diagnosis = load_csv(DIAGNOSIS)
    recommended = pd.DataFrame(
        [
            {
                "action_id": "R0_freeze_core19_path",
                "action": "freeze CORE19 locked-packet replay path as engineering pass / signal hold",
                "reason": "bounded replay and repair both fail breadth gates",
            },
            {
                "action_id": "R1_no_large_search",
                "action": "do not authorize large search or formula expansion from this packet",
                "reason": "replay-clean supply is too narrow and lane-limited",
            },
            {
                "action_id": "R2_next_reset_contract",
                "action": "write CORE21 objective/label replay translation reset contract",
                "reason": "failure is replay translation/cost-lane breadth, not materialization or governance",
            },
        ]
    )
    recommended.to_csv(RUNTIME / "a7ffcore19ser_recommended_actions.csv", index=False)
    cost_summary.to_csv(RUNTIME / "a7ffcore19ser_cost_summary.csv", index=False)
    diagnosis.to_csv(RUNTIME / "a7ffcore19ser_diagnosis.csv", index=False)
    manifest = {
        "stage": "A7FF-CORE19SER",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE19SE",
        "source_decision": se.get("decision"),
        "decision": "PASS_A7FFCORE19SER_REPLAY_REPAIR_FORENSIC_COMPLETE_READY_FOR_CORE21",
        "dominant_failure": "replay_clean_supply_too_narrow_after_cost_repair",
        "best_clean_candidate_count": int(se.get("best_clean_candidate_count", 0)),
        "best_clean_seed_lane_count": int(se.get("best_clean_seed_lane_count", 0)),
        "authorizes_core21_contract": True,
        "authorizes_core20": False,
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE21 objective/label replay translation reset contract",
    }
    write_json(RUNTIME / "a7ffcore19ser_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE19SER REPLAY REPAIR FORENSIC",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "CORE19SER freezes the bounded replay repair result. It does not execute replay, formula generation, search, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Cost Summary",
        "",
        md_table(cost_summary),
        "",
        "## Diagnosis",
        "",
        md_table(diagnosis),
        "",
        "## Recommended Actions",
        "",
        md_table(recommended),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
