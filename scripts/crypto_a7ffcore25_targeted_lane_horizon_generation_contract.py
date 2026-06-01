from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore25_targeted_lane_horizon_generation_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE25_TARGETED_LANE_HORIZON_GENERATION_CONTRACT_20260601.md"
CORE24R = REPO / "runtime" / "a7ffcore24r_lane_packet_forensic" / "a7ffcore24r_manifest.json"


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
    source = read_json(CORE24R)
    if source.get("decision") != "PASS_A7FFCORE24R_LANE_PACKET_FORENSIC_COMPLETE_READY_FOR_CORE25":
        raise SystemExit(f"CORE24R is not ready: {source.get('decision')}")

    target_policy = pd.DataFrame(
        [
            {
                "target": "S0_positioning_price_basis",
                "reason": "missing from H4+ repair packet",
                "horizons": "4h,8h,24h",
                "allowed_templates": "positioning x basis/price lower-turnover transforms; rank/tsrank/zscore/delta/spread",
                "blocked_templates": "H1-only rerun; same-bar promotion; open grammar",
                "min_packet_quota": 160,
            },
            {
                "target": "S1_liquidity_basis_positioning",
                "reason": "same-bar diagnostic exists but one-bar executable fails",
                "horizons": "4h,8h,24h",
                "allowed_templates": "liquidity x basis/positioning lag-resilient smoothing and low-turnover transforms",
                "blocked_templates": "basis-only wrapper; funding-only wrapper; same-bar-only promotion",
                "min_packet_quota": 160,
            },
            {
                "target": "S2_taker_flow_liquidity_oi",
                "reason": "existing H24 executable clue is calibration lane",
                "horizons": "24h",
                "allowed_templates": "calibration variants only",
                "blocked_templates": "single-lane expansion",
                "min_packet_quota": 40,
            },
            {
                "target": "S3_cross_family_bridge",
                "reason": "existing non-L5 executable bridge is calibration lane",
                "horizons": "8h,24h",
                "allowed_templates": "calibration variants only",
                "blocked_templates": "S3-only dominance",
                "min_packet_quota": 40,
            },
        ]
    )
    generation_budget = pd.DataFrame(
        [
            {"item": "generated_blueprints_max", "value": 4800},
            {"item": "materialization_preflight_max", "value": 960},
            {"item": "numeric_probe_max", "value": 480},
            {"item": "target_lane_min_count", "value": 2},
            {"item": "target_horizon_min_count", "value": 3},
        ]
    )
    gates = pd.DataFrame(
        [
            {"gate": "targeted_generation_only", "requirement": "all candidates must belong to CORE25 target lanes and H4+/H24 horizons"},
            {"gate": "s0_s1_presence", "requirement": "S0 and S1 must both be present in generated packet"},
            {"gate": "one_bar_executable_policy", "requirement": "same-bar-only candidates remain diagnostic; one-bar positive required for replay-clean"},
            {"gate": "lane_cap", "requirement": "no lane may exceed 45% of materialization preflight packet"},
            {"gate": "search_auth", "requirement": "no search, large search, alpha proof, shadow, paper, or live"},
        ]
    )
    execution_plan = pd.DataFrame(
        [
            {
                "stage": "A7FF-CORE25E",
                "action": "targeted lane/horizon blueprint generation and preflight packet construction",
                "input": "CORE25 contract + existing field/operator registry",
                "authorized": True,
            },
            {
                "stage": "A7FF-CORE26",
                "action": "targeted numeric probe contract",
                "input": "CORE25E pass only",
                "authorized": False,
            },
        ]
    )
    target_policy.to_csv(RUNTIME / "a7ffcore25_target_policy.csv", index=False)
    generation_budget.to_csv(RUNTIME / "a7ffcore25_generation_budget.csv", index=False)
    gates.to_csv(RUNTIME / "a7ffcore25_gate_policy.csv", index=False)
    execution_plan.to_csv(RUNTIME / "a7ffcore25_execution_plan.csv", index=False)

    manifest = {
        "stage": "A7FF-CORE25",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE24R",
        "source_decision": source.get("decision"),
        "decision": "PASS_A7FFCORE25_TARGETED_LANE_HORIZON_GENERATION_CONTRACT_READY_FOR_CORE25E",
        "dominant_failure": source.get("dominant_failure"),
        "authorizes_core25e": True,
        "authorizes_targeted_generation": True,
        "authorizes_open_formula_generation": False,
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE25E targeted lane/horizon generation preflight packet",
    }
    write_json(RUNTIME / "a7ffcore25_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE25 TARGETED LANE/HORIZON GENERATION CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "CORE25 authorizes a bounded targeted generation preflight to repair missing executable lane/horizon coverage. It is not open formula search and does not authorize replay execution, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Target Policy",
        "",
        md_table(target_policy),
        "",
        "## Generation Budget",
        "",
        md_table(generation_budget),
        "",
        "## Gates",
        "",
        md_table(gates),
        "",
        "## Execution Plan",
        "",
        md_table(execution_plan),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
