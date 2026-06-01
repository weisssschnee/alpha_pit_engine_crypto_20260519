from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore19s_bounded_replay_repair_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE19S_BOUNDED_REPLAY_REPAIR_CONTRACT_20260601.md"
CORE19R = REPO / "runtime" / "a7ffcore19r_bounded_replay_forensic" / "a7ffcore19r_manifest.json"
FAILURE = REPO / "runtime" / "a7ffcore19r_bounded_replay_forensic" / "a7ffcore19r_failure_summary.csv"
CLEAN = REPO / "runtime" / "a7ffcore19r_bounded_replay_forensic" / "a7ffcore19r_clean_clue_summary.csv"


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
    core19r = read_json(CORE19R)
    if core19r.get("decision") != "PASS_A7FFCORE19R_BOUNDED_REPLAY_FORENSIC_COMPLETE_READY_FOR_CORE19S":
        raise SystemExit(f"CORE19R is not ready for CORE19S: {core19r.get('decision')}")
    failure = load_csv(FAILURE)
    clean = load_csv(CLEAN)
    repair_policy = pd.DataFrame(
        [
            {
                "repair_lane": "L0_cost_tier_attribution",
                "action": "re-evaluate clean supply at 2bps/5bps/10bps/20bps without changing candidate orientation",
                "allowed": True,
                "forbidden": "using cost tier to claim alpha proof",
            },
            {
                "repair_lane": "L1_lag_attribution",
                "action": "separate same-bar, one-bar-lag, and stale-lag failure counts",
                "allowed": True,
                "forbidden": "promoting same-bar-only candidates",
            },
            {
                "repair_lane": "L2_label_translation",
                "action": "audit L0/L1/L3/L5 and horizon-24 translation by lane",
                "allowed": True,
                "forbidden": "L5-only pass as search-ready evidence",
            },
            {
                "repair_lane": "L3_lane_specific_replay_packet",
                "action": "construct a diagnostic repair packet preserving S2/S3 clean clues and testing S0/S1 failure reasons",
                "allowed": True,
                "forbidden": "adding new formula generation or changing the locked packet source",
            },
        ]
    )
    execution_plan = pd.DataFrame(
        [
            {
                "stage": "A7FF-CORE19SE",
                "action": "bounded replay repair execution",
                "input": "CORE19E replay rows + CORE17E locked packet",
                "output": "cost/lag/label/lane attribution and repaired replay decision",
                "authorized": True,
            },
            {
                "stage": "A7FF-CORE20",
                "action": "replay-clean consolidation / search-readiness contract",
                "input": "CORE19SE pass only",
                "output": "contract only",
                "authorized": False,
            },
        ]
    )
    blocked = pd.DataFrame(
        [
            {"blocked_task": "CORE20", "reason": "blocked until CORE19SE repair execution passes"},
            {"blocked_task": "formula generation/search", "reason": "blocked: CORE19S authorizes replay repair only"},
            {"blocked_task": "large search", "reason": "blocked until replay-clean supply and selector readiness pass"},
            {"blocked_task": "alpha proof / shadow / paper / live", "reason": "not authorized"},
        ]
    )
    repair_policy.to_csv(RUNTIME / "a7ffcore19s_repair_policy.csv", index=False)
    execution_plan.to_csv(RUNTIME / "a7ffcore19s_execution_plan.csv", index=False)
    blocked.to_csv(RUNTIME / "a7ffcore19s_blocked_tasks.csv", index=False)
    failure.to_csv(RUNTIME / "a7ffcore19s_source_failure_summary.csv", index=False)
    clean.to_csv(RUNTIME / "a7ffcore19s_source_clean_clue_summary.csv", index=False)
    manifest = {
        "stage": "A7FF-CORE19S",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE19R",
        "source_decision": core19r.get("decision"),
        "decision": "PASS_A7FFCORE19S_BOUNDED_REPLAY_REPAIR_CONTRACT_READY_FOR_CORE19SE",
        "source_replay_clean_candidate_count": int(core19r.get("replay_clean_candidate_count", 0)),
        "source_replay_clean_seed_lane_count": int(core19r.get("replay_clean_seed_lane_count", 0)),
        "authorizes_core19se": True,
        "authorizes_core20": False,
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE19SE bounded replay repair execution",
    }
    write_json(RUNTIME / "a7ffcore19s_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE19S BOUNDED REPLAY REPAIR CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "CORE19S defines replay repair only. It does not execute formula generation, search, large search, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Repair Policy",
        "",
        md_table(repair_policy),
        "",
        "## Execution Plan",
        "",
        md_table(execution_plan),
        "",
        "## Source Failure Summary",
        "",
        md_table(failure),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
