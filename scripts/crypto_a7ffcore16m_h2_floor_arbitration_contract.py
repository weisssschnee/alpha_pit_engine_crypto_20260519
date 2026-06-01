from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore16m_h2_floor_arbitration_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE16M_H2_FLOOR_ARBITRATION_CONTRACT_20260601.md"
CORE16KR = REPO / "runtime" / "a7ffcore16kr_h2_repair_forensic" / "a7ffcore16kr_manifest.json"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    kr = read_json(CORE16KR)
    if kr.get("decision") != "PASS_A7FFCORE16KR_H2_REPAIR_FORENSIC_COMPLETE_READY_FOR_CORE16M":
        raise SystemExit(f"CORE16KR is not ready: {kr.get('decision')}")

    policy = pd.DataFrame(
        [
            {
                "policy_id": "P0_retain_h2_floor",
                "decision": "retain",
                "reason": "H2/I4 under-supply was the explicit blocker; waiving the floor would make the balanced queue governance meaningless",
            },
            {
                "policy_id": "P1_no_nearmiss_promotion",
                "decision": "retain",
                "reason": "near-miss rows remain forensic evidence only; they cannot be used as strict alpha seeds",
            },
            {
                "policy_id": "P2_authorize_broader_h2_wave",
                "decision": "authorize_core16me",
                "reason": "CORE16KE found 2 of 3 required strict rows; the remaining gap is localized and worth one broader checkpointed H2 wave",
            },
        ]
    )
    allowed = pd.DataFrame(
        [
            {
                "stage": "A7FF-CORE16ME",
                "allowed_action": "broader checkpointed H2/I4 strict-floor repair execution",
                "scope": "H2_I4_near_miss_repair only; expand transform grid around taker_flow x liquidity/OI pairs",
            },
            {
                "stage": "A7PM-0/3",
                "allowed_action": "registry refresh after CORE16M/ME",
                "scope": "governance only",
            },
        ]
    )
    blocked = pd.DataFrame(
        [
            {"blocked_task": "A7FF-CORE16L", "reason": "strict pre-seed queue still below size/H2 floor"},
            {"blocked_task": "A7FF-CORE17", "reason": "objective seed policy blocked until strict queue lock passes"},
            {"blocked_task": "formula generation/search", "reason": "CORE16M authorizes H2 repair execution only"},
            {"blocked_task": "alpha proof / shadow / paper / live", "reason": "not authorized"},
        ]
    )
    operator_policy = pd.DataFrame(
        [
            {
                "family": "H2_I4_near_miss_repair",
                "left_families": "taker_flow",
                "right_families": "liquidity|open_interest",
                "operators": "Mul|SafeDiv|Sub",
                "left_transforms": "delta_1h|delta_2h|delta_4h|delta_8h|delta_24h|zscore_72h|zscore_168h|shock_24h|tsrank_72h",
                "right_transforms": "level|delta_1h|delta_2h|delta_4h|delta_8h|delta_24h|zscore_72h|zscore_168h|shock_24h|tsrank_72h",
                "required_added_strict_h2": int(kr.get("h2_rows_needed", 1)),
            }
        ]
    )
    policy.to_csv(RUNTIME / "a7ffcore16m_floor_policy.csv", index=False)
    allowed.to_csv(RUNTIME / "a7ffcore16m_allowed_next.csv", index=False)
    blocked.to_csv(RUNTIME / "a7ffcore16m_blocked_tasks.csv", index=False)
    operator_policy.to_csv(RUNTIME / "a7ffcore16m_core16me_operator_policy.csv", index=False)

    manifest = {
        "stage": "A7FF-CORE16M",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE16KR",
        "source_decision": kr.get("decision"),
        "decision": "PASS_A7FFCORE16M_H2_FLOOR_RETAINED_READY_FOR_CORE16ME",
        "h2_rows_needed": int(kr.get("h2_rows_needed", 1)),
        "queue_rows_needed": int(kr.get("queue_rows_needed", 1)),
        "floor_policy": "retain_h2_floor_no_nearmiss_promotion",
        "authorizes_core16me": True,
        "authorizes_core16l": False,
        "authorizes_core17": False,
        "authorizes_replay": False,
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE16ME broader checkpointed H2/I4 strict-floor repair execution",
    }
    write_json(RUNTIME / "a7ffcore16m_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE16M H2 FLOOR ARBITRATION CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "CORE16M is a contract and arbitration record. It does not execute replay, search, formula generation, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Floor Policy",
        "",
        md_table(policy),
        "",
        "## CORE16ME Operator Policy",
        "",
        md_table(operator_policy),
        "",
        "## Blocked",
        "",
        md_table(blocked),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
