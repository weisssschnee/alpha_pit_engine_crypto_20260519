from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore14s_replay_packet_repair_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE14S_REPLAY_PACKET_REPAIR_CONTRACT_20260601.md"
CORE14R = REPO / "runtime" / "a7ffcore14r_replay_failure_forensic" / "a7ffcore14r_manifest.json"
SENSITIVITY = REPO / "runtime" / "a7ffcore14r_replay_failure_forensic" / "a7ffcore14r_gate_sensitivity.csv"
CONTROL = REPO / "runtime" / "a7ffcore14r_replay_failure_forensic" / "a7ffcore14r_control_dominance_summary.csv"
FAMILY = REPO / "runtime" / "a7ffcore14r_replay_failure_forensic" / "a7ffcore14r_source_family_summary.csv"


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
    core14r = read_json(CORE14R)
    if core14r.get("decision") != "PASS_A7FFCORE14R_FAILURE_ATTRIBUTION_COMPLETE_READY_FOR_CORE14S":
        raise SystemExit(f"A7FF-CORE14R is not ready: {core14r.get('decision')}")

    sensitivity = pd.read_csv(SENSITIVITY)
    control = pd.read_csv(CONTROL)
    family = pd.read_csv(FAMILY)

    repair_rules = pd.DataFrame(
        [
            {
                "rule_id": "R0_no_gate_relaxation_as_solution",
                "requirement": "do not proceed by merely relaxing CORE14E pass gates",
                "reason": "CORE14R max strict candidates under sensitivity is below 24; relaxed control thresholds do not create enough breadth",
            },
            {
                "rule_id": "R1_split_first_packet_score",
                "requirement": "CORE14SE packet score must prioritize candidates with validation and recent evidence separately",
                "reason": "CORE14E collapsed under validation+recent joint clean rule",
            },
            {
                "rule_id": "R2_control_margin_first",
                "requirement": "packet construction must rank by non-signflip max control margin before raw score",
                "reason": "dominant blocker is control_and_cost_collapse",
            },
            {
                "rule_id": "R3_cost_floor",
                "requirement": "candidate packet must estimate 5bps cost survival before replay execution",
                "reason": "many candidates have positive raw spread but negative cost-adjusted spread",
            },
            {
                "rule_id": "R4_family_rebalance",
                "requirement": "packet must cap any semantic/motif pair at 20 percent and include at least 6 semantic buckets and 5 motifs",
                "reason": "CORE14E clean pool collapsed to one semantic and one motif",
            },
            {
                "rule_id": "R5_no_same_packet_rerun",
                "requirement": "CORE14E packet cannot be rerun unchanged",
                "reason": "same packet already executed bounded replay and failed clean pool gates",
            },
        ]
    )
    next_contract = {
        "stage": "A7FF-CORE14SE",
        "action": "build repaired replay packet and execute bounded replay only if packet gates pass",
        "source_pool": "CORE13E numeric clues plus CORE14R failure attribution; not CORE14E clean pool only",
        "max_packet": 128,
        "min_packet": 96,
        "min_semantic_buckets": 6,
        "min_motif_buckets": 5,
        "max_semantic_motif_pair_share": 0.20,
        "required_controls": [
            "wrong_lag_future",
            "wrong_lag_stale",
            "time_shuffle",
            "symbol_shuffle",
            "same_family_placebo",
        ],
        "clean_rule": "validation and recent both positive at 5bps with max non-signflip control_ratio < 1.0",
        "forbidden": [
            "same CORE14 packet rerun",
            "gate relaxation as pass",
            "formula search",
            "large search",
            "alpha proof",
            "shadow/paper/live",
        ],
    }
    blocked = pd.DataFrame(
        [
            {"task": "A7FF-CORE15", "reason": "blocked until repaired packet replay produces enough clean breadth"},
            {"task": "A7FF large search", "reason": "blocked; CORE14E replay-clean pool has only two candidates"},
            {"task": "same packet rerun", "reason": "blocked; CORE14R attributes failure to control/cost/split collapse"},
            {"task": "alpha proof / shadow / paper / live", "reason": "not authorized"},
        ]
    )

    repair_rules.to_csv(RUNTIME / "a7ffcore14s_repair_rules.csv", index=False)
    sensitivity.to_csv(RUNTIME / "a7ffcore14s_source_gate_sensitivity.csv", index=False)
    control.to_csv(RUNTIME / "a7ffcore14s_source_control_dominance.csv", index=False)
    family.to_csv(RUNTIME / "a7ffcore14s_source_family_summary.csv", index=False)
    blocked.to_csv(RUNTIME / "a7ffcore14s_blocked_tasks.csv", index=False)
    write_json(RUNTIME / "a7ffcore14s_next_contract.json", next_contract)

    decision = "PASS_A7FFCORE14S_REPLAY_PACKET_REPAIR_CONTRACT_READY_FOR_CORE14SE"
    manifest = {
        "stage": "A7FF-CORE14S",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE14R",
        "source_decision": core14r.get("decision"),
        "decision": decision,
        "dominant_blocker": core14r.get("dominant_blocker"),
        "authorizes_core14se": True,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE14SE repaired packet construction / bounded replay execution",
    }
    write_json(RUNTIME / "a7ffcore14s_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE14S REPLAY PACKET REPAIR CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-CORE14S defines a repair contract after CORE14E replay failure. It does not execute replay, formula search, large search, promotion, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Repair Rules",
        "",
        md_table(repair_rules),
        "",
        "## Next Contract",
        "",
        "```json",
        json.dumps(next_contract, indent=2, sort_keys=True),
        "```",
        "",
        "## Source Gate Sensitivity",
        "",
        md_table(sensitivity),
        "",
        "## Source Control Dominance",
        "",
        md_table(control),
        "",
        "## Blocked Tasks",
        "",
        md_table(blocked),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
