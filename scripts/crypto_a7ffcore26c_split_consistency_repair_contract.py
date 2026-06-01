from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore26c_split_consistency_repair_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE26C_SPLIT_CONSISTENCY_REPAIR_CONTRACT_20260602.md"
CORE26R = REPO / "runtime" / "a7ffcore26r_targeted_numeric_probe_forensic" / "a7ffcore26r_manifest.json"
LANE_FORENSIC = REPO / "runtime" / "a7ffcore26r_targeted_numeric_probe_forensic" / "a7ffcore26r_lane_forensic.csv"
NEAR_MISS = REPO / "runtime" / "a7ffcore26r_targeted_numeric_probe_forensic" / "a7ffcore26r_near_miss_candidates.csv"


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
    source = read_json(CORE26R)
    if source.get("decision") != "PASS_A7FFCORE26R_TARGETED_NUMERIC_FORENSIC_COMPLETE_READY_FOR_CORE26C":
        raise SystemExit(f"CORE26R is not ready: {source.get('decision')}")
    lane = pd.read_csv(LANE_FORENSIC)
    near = pd.read_csv(NEAR_MISS) if NEAR_MISS.exists() else pd.DataFrame()

    lane_policy = pd.DataFrame(
        [
            {
                "lane": "S0_positioning_price_basis",
                "status": "near_miss_primary",
                "evidence": "3 two-split near misses, 14 spread-positive candidates, high control median",
                "allowed_repair": "control-resistant variants and split-stability filters around existing S0 field pairs",
            },
            {
                "lane": "S3_cross_family_bridge",
                "status": "near_miss_primary",
                "evidence": "4 two-split near misses, positive median spread, high control median",
                "allowed_repair": "control-resistant bridge variants; cap S3 dominance",
            },
            {
                "lane": "S1_liquidity_basis_positioning",
                "status": "secondary_weak",
                "evidence": "spread-positive candidates exist but zero two-split near miss",
                "allowed_repair": "diagnostic only unless control/spread improves",
            },
            {
                "lane": "S2_taker_flow_liquidity_oi",
                "status": "blocked_weak",
                "evidence": "zero spread-positive three-split and high control",
                "allowed_repair": "no expansion in CORE26C",
            },
        ]
    )
    repair_budget = pd.DataFrame(
        [
            {"item": "generated_blueprints_max", "value": 2400},
            {"item": "numeric_probe_max", "value": 360},
            {"item": "focus_lanes", "value": "S0,S3 primary; S1 diagnostic cap; S2 blocked"},
            {"item": "required_output", "value": ">=6 three-split clean candidates and >=3 lanes before replay contract"},
        ]
    )
    blocked = pd.DataFrame(
        [
            {"blocked_task": "CORE27 bounded replay contract", "reason": "no three-split executable candidates"},
            {"blocked_task": "open formula generation / large search", "reason": "near misses are lane-specific and control-dominated"},
            {"blocked_task": "alpha proof / shadow / paper / live", "reason": "not authorized"},
        ]
    )
    execution_plan = pd.DataFrame(
        [
            {
                "stage": "A7FF-CORE26CE",
                "action": "split-consistency repair generation and numeric probe",
                "input": "CORE26R near-miss candidates + lane policy",
                "authorized": True,
            },
            {
                "stage": "A7FF-CORE27",
                "action": "bounded replay contract",
                "input": "CORE26CE pass only",
                "authorized": False,
            },
        ]
    )
    lane_policy.to_csv(RUNTIME / "a7ffcore26c_lane_policy.csv", index=False)
    repair_budget.to_csv(RUNTIME / "a7ffcore26c_repair_budget.csv", index=False)
    blocked.to_csv(RUNTIME / "a7ffcore26c_blocked_tasks.csv", index=False)
    execution_plan.to_csv(RUNTIME / "a7ffcore26c_execution_plan.csv", index=False)
    near.head(50).to_csv(RUNTIME / "a7ffcore26c_near_miss_seed_snapshot.csv", index=False)

    manifest = {
        "stage": "A7FF-CORE26C",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE26R",
        "source_decision": source.get("decision"),
        "decision": "PASS_A7FFCORE26C_SPLIT_CONSISTENCY_REPAIR_CONTRACT_READY_FOR_CORE26CE",
        "dominant_failure": source.get("dominant_failure"),
        "near_miss_count": source.get("two_split_near_miss_count", 0),
        "near_miss_lane_count": source.get("near_miss_lane_count", 0),
        "authorizes_core26ce": True,
        "authorizes_formula_generation": False,
        "authorizes_open_formula_generation": False,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE26CE split-consistency repair numeric probe",
    }
    write_json(RUNTIME / "a7ffcore26c_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE26C SPLIT-CONSISTENCY REPAIR CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "CORE26C authorizes a bounded repair of split consistency and control dominance after targeted numeric probe failure. It does not authorize open formula generation, search, large search, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Lane Policy",
        "",
        md_table(lane_policy),
        "",
        "## Repair Budget",
        "",
        md_table(repair_budget),
        "",
        "## Existing Lane Forensic",
        "",
        md_table(lane),
        "",
        "## Blocked",
        "",
        md_table(blocked),
        "",
        "## Execution Plan",
        "",
        md_table(execution_plan),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
