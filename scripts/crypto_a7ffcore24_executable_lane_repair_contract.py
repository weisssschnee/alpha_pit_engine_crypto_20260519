from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore24_executable_lane_repair_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE24_EXECUTABLE_LANE_REPAIR_CONTRACT_20260601.md"
CORE23R = REPO / "runtime" / "a7ffcore23r_executable_horizon_forensic" / "a7ffcore23r_manifest.json"


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
    source = read_json(CORE23R)
    if source.get("decision") != "PASS_A7FFCORE23R_EXECUTABLE_HORIZON_FORENSIC_COMPLETE_READY_FOR_CORE24":
        raise SystemExit(f"CORE23R is not ready: {source.get('decision')}")

    lane_policy = pd.DataFrame(
        [
            {
                "lane": "S0_positioning_price_basis",
                "repair_target": "convert same-bar H4/H8 diagnostic supply into one-bar executable H4+/H24 candidates",
                "allowed_fields": "positioning, price/mark/index, basis/premium",
                "forbidden": "same-bar-only promotion; direct high-turnover 1h rerun",
            },
            {
                "lane": "S1_basis_premium_funding",
                "repair_target": "restore funding/basis lane under executable horizon and one-bar lag",
                "allowed_fields": "basis/premium, funding, low-turnover trend/vol context",
                "forbidden": "funding-only wrapper; basis-only wrapper",
            },
            {
                "lane": "S2_taker_flow_liquidity_oi",
                "repair_target": "retain existing H24 executable clue as calibration, not expansion seed",
                "allowed_fields": "taker ratio, OI, liquidity state",
                "forbidden": "single-lane promotion",
            },
            {
                "lane": "S3_cross_family_bridge",
                "repair_target": "retain non-L5 H24 executable bridge as calibration, not proof",
                "allowed_fields": "positioning, OI value, cross-family bridge",
                "forbidden": "S3-only selector dominance",
            },
        ]
    )
    execution_plan = pd.DataFrame(
        [
            {
                "stage": "A7FF-CORE24E",
                "action": "bounded executable lane repair packet construction",
                "input": "CORE17E locked packet + CORE23E/23R lane findings",
                "authorized": True,
            },
            {
                "stage": "A7FF-CORE25",
                "action": "lower-turnover bounded replay contract",
                "input": "CORE24E pass only",
                "authorized": False,
            },
        ]
    )
    gates = pd.DataFrame(
        [
            {"gate": "min_executable_candidate_count", "threshold": ">= 6", "scope": "one-bar H4+ / H24 diagnostic packet"},
            {"gate": "min_executable_lane_count", "threshold": ">= 3", "scope": "S0/S1/S2/S3 lanes"},
            {"gate": "min_non_l5_candidate_count", "threshold": ">= 3", "scope": "non-L7/non-L5 preferred; L5 cannot dominate"},
            {"gate": "same_bar_only_candidate_policy", "threshold": "diagnostic_only", "scope": "cannot enter replay-clean packet unless one-bar positive"},
            {"gate": "search_authorization", "threshold": "false", "scope": "CORE24 authorizes packet construction only"},
        ]
    )
    blocked = pd.DataFrame(
        [
            {"blocked_task": "large search", "reason": "blocked: executable lane supply is too narrow"},
            {"blocked_task": "formula generation/search", "reason": "blocked: CORE24 authorizes bounded lane repair packet construction only"},
            {"blocked_task": "alpha proof / shadow / paper / live", "reason": "not authorized"},
        ]
    )
    lane_policy.to_csv(RUNTIME / "a7ffcore24_lane_policy.csv", index=False)
    execution_plan.to_csv(RUNTIME / "a7ffcore24_execution_plan.csv", index=False)
    gates.to_csv(RUNTIME / "a7ffcore24_gate_policy.csv", index=False)
    blocked.to_csv(RUNTIME / "a7ffcore24_blocked_tasks.csv", index=False)

    manifest = {
        "stage": "A7FF-CORE24",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE23R",
        "source_decision": source.get("decision"),
        "decision": "PASS_A7FFCORE24_EXECUTABLE_LANE_REPAIR_CONTRACT_READY_FOR_CORE24E",
        "dominant_failure": source.get("dominant_failure"),
        "missing_executable_lanes": source.get("missing_executable_lanes", []),
        "authorizes_core24e": True,
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE24E bounded executable lane repair packet construction",
    }
    write_json(RUNTIME / "a7ffcore24_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE24 EXECUTABLE LANE REPAIR CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "CORE24 defines a bounded repair path for executable lane breadth. It does not execute formula generation, search, large search, alpha proof, shadow, paper, or live.",
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
        "## Gates",
        "",
        md_table(gates),
        "",
        "## Execution Plan",
        "",
        md_table(execution_plan),
        "",
        "## Blocked",
        "",
        md_table(blocked),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
