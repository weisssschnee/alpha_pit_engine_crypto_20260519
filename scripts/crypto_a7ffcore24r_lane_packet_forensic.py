from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore24r_lane_packet_forensic"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE24R_LANE_PACKET_FORENSIC_20260601.md"
CORE24E = REPO / "runtime" / "a7ffcore24e_executable_lane_repair_packet" / "a7ffcore24e_manifest.json"
ROLE_SUMMARY = REPO / "runtime" / "a7ffcore24e_executable_lane_repair_packet" / "a7ffcore24e_role_summary.csv"
LANE_SUMMARY = REPO / "runtime" / "a7ffcore24e_executable_lane_repair_packet" / "a7ffcore24e_lane_summary.csv"
HORIZON_COVERAGE = REPO / "runtime" / "a7ffcore24e_executable_lane_repair_packet" / "a7ffcore24e_source_lane_horizon_coverage.csv"


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
    source = read_json(CORE24E)
    if source.get("decision") != "HOLD_A7FFCORE24E_SOURCE_PACKET_LANE_COVERAGE_INSUFFICIENT":
        raise SystemExit(f"CORE24E is not in expected HOLD state: {source.get('decision')}")

    role_summary = pd.read_csv(ROLE_SUMMARY)
    lane_summary = pd.read_csv(LANE_SUMMARY)
    horizon_coverage = pd.read_csv(HORIZON_COVERAGE)

    diagnosis = pd.DataFrame(
        [
            {
                "finding": "repair_packet_exists",
                "value": source.get("repair_packet_candidate_count", 0),
                "interpretation": "packet can preserve diagnostic seeds, but cannot become executable evidence",
            },
            {
                "finding": "s0_absent_from_h4_plus_packet",
                "value": "S0_positioning_price_basis" in source.get("missing_packet_lanes", []),
                "interpretation": "S0 source candidates are H1-only and cannot be repaired without new bounded lane/horizon generation",
            },
            {
                "finding": "s1_same_bar_only",
                "value": "S1_liquidity_basis_positioning" in source.get("missing_executable_lanes", []),
                "interpretation": "S1 enters packet as diagnostic but fails one-bar executable gate",
            },
            {
                "finding": "dominant_failure",
                "value": "source_packet_missing_executable_lane_horizon_coverage",
                "interpretation": "old locked packet cannot supply enough executable lane breadth",
            },
        ]
    )
    recommended = pd.DataFrame(
        [
            {
                "next_stage": "A7FF-CORE25",
                "action": "targeted executable-lane horizon generation contract",
                "rationale": "bounded generation is required for S0 H4+/H24 and S1 one-bar conversion; old packet cannot repair this internally",
                "authorized": True,
            },
            {
                "next_stage": "A7FF large search",
                "action": "blocked",
                "rationale": "needed generation is lane/horizon-targeted, not open grammar or large search",
                "authorized": False,
            },
        ]
    )
    target_lanes = pd.DataFrame(
        [
            {
                "target_lane": "S0_positioning_price_basis",
                "needed_horizons": "4h/8h/24h",
                "reason": "current source packet has S0 only at H1",
                "generation_scope": "bounded lane-native transformations only",
            },
            {
                "target_lane": "S1_liquidity_basis_positioning",
                "needed_horizons": "4h/8h/24h",
                "reason": "same-bar diagnostic exists, one-bar executable conversion fails",
                "generation_scope": "lower-turnover smoothing / lag-resilient variants only",
            },
        ]
    )

    diagnosis.to_csv(RUNTIME / "a7ffcore24r_diagnosis.csv", index=False)
    recommended.to_csv(RUNTIME / "a7ffcore24r_recommended_actions.csv", index=False)
    target_lanes.to_csv(RUNTIME / "a7ffcore24r_target_lanes.csv", index=False)

    manifest = {
        "stage": "A7FF-CORE24R",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE24E",
        "source_decision": source.get("decision"),
        "decision": "PASS_A7FFCORE24R_LANE_PACKET_FORENSIC_COMPLETE_READY_FOR_CORE25",
        "dominant_failure": "source_packet_missing_executable_lane_horizon_coverage",
        "repair_packet_candidate_count": source.get("repair_packet_candidate_count", 0),
        "repair_packet_lane_count": source.get("repair_packet_lane_count", 0),
        "executable_clean_candidate_count": source.get("executable_clean_candidate_count", 0),
        "executable_clean_lane_count": source.get("executable_clean_lane_count", 0),
        "missing_packet_lanes": source.get("missing_packet_lanes", []),
        "missing_executable_lanes": source.get("missing_executable_lanes", []),
        "authorizes_core25_contract": True,
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE25 targeted executable-lane horizon generation contract",
    }
    write_json(RUNTIME / "a7ffcore24r_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE24R LANE PACKET FORENSIC",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "CORE24R shows the old locked packet cannot internally repair executable lane breadth. It authorizes only a targeted lane/horizon generation contract, not search execution or promotion.",
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
        "## Target Lanes",
        "",
        md_table(target_lanes),
        "",
        "## Role Summary From CORE24E",
        "",
        md_table(role_summary),
        "",
        "## Lane Summary From CORE24E",
        "",
        md_table(lane_summary),
        "",
        "## Source Horizon Coverage",
        "",
        md_table(horizon_coverage),
        "",
        "## Recommended Actions",
        "",
        md_table(recommended),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
