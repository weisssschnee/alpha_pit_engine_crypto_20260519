from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore24e_executable_lane_repair_packet"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE24E_EXECUTABLE_LANE_REPAIR_PACKET_20260601.md"
CORE24 = REPO / "runtime" / "a7ffcore24_executable_lane_repair_contract" / "a7ffcore24_manifest.json"
ROWS = REPO / "runtime" / "a7ffcore19e_bounded_replay_execution" / "a7ffcore19e_replay_rows.csv"

PREMAY = ["validation_2025H1", "test_2025H2", "recent_oos_2026JanApr"]
EXPECTED_LANES = {
    "S0_positioning_price_basis",
    "S1_liquidity_basis_positioning",
    "S2_taker_flow_liquidity_oi",
    "S3_cross_family_bridge",
}


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


def candidate_status(x: pd.DataFrame, spread_col: str) -> pd.DataFrame:
    y = x.copy()
    y["test_spread"] = pd.to_numeric(y[spread_col], errors="coerce")
    y["control_ratio"] = pd.to_numeric(y["control_ratio_premay_max"], errors="coerce")
    y["ok"] = y["test_spread"].gt(0) & y["control_ratio"].lt(1.0)
    return (
        y.groupby(
            [
                "candidate_id",
                "blueprint_id",
                "seed_lane",
                "second_pass_family",
                "left_field",
                "left_transform",
                "operator",
                "right_field",
                "right_transform",
                "label_family",
                "label_horizon_h",
            ],
            dropna=False,
        )
        .agg(ok_splits=("ok", "sum"), min_test_spread=("test_spread", "min"), mean_test_spread=("test_spread", "mean"), control_ratio=("control_ratio", "max"))
        .reset_index()
    )


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    core24 = read_json(CORE24)
    if core24.get("decision") != "PASS_A7FFCORE24_EXECUTABLE_LANE_REPAIR_CONTRACT_READY_FOR_CORE24E":
        raise SystemExit(f"CORE24 is not ready: {core24.get('decision')}")

    rows = pd.read_csv(ROWS)
    rows = rows[rows["split"].isin(PREMAY) & rows["cost_bps"].eq(2) & rows["label_horizon_h"].ge(4)].copy()
    rows["one_bar_costed_spread"] = pd.to_numeric(rows["one_bar_lag_spread"], errors="coerce") - (2.0 * 2 / 10000.0)
    one_bar = candidate_status(rows, "one_bar_costed_spread")
    same_bar = candidate_status(rows, "cost_adjusted_spread")

    one_bar_clean_ids = set(one_bar.loc[one_bar["ok_splits"].ge(len(PREMAY)), "candidate_id"].astype(str))
    same_bar_clean_ids = set(same_bar.loc[same_bar["ok_splits"].ge(len(PREMAY)), "candidate_id"].astype(str))
    near_miss_ids = set(one_bar.loc[one_bar["ok_splits"].eq(2), "candidate_id"].astype(str))

    all_ids = sorted(one_bar_clean_ids | same_bar_clean_ids | near_miss_ids)
    packet = one_bar[one_bar["candidate_id"].astype(str).isin(all_ids)].copy()
    packet["packet_role"] = "excluded"
    packet.loc[packet["candidate_id"].astype(str).isin(one_bar_clean_ids), "packet_role"] = "executable_clean"
    packet.loc[
        packet["candidate_id"].astype(str).isin(same_bar_clean_ids - one_bar_clean_ids),
        "packet_role",
    ] = "same_bar_repair_seed"
    packet.loc[
        packet["candidate_id"].astype(str).isin(near_miss_ids - one_bar_clean_ids - same_bar_clean_ids),
        "packet_role",
    ] = "one_bar_near_miss_seed"
    packet = packet[packet["packet_role"].ne("excluded")].copy()

    role_summary = (
        packet.groupby("packet_role", dropna=False)
        .agg(candidate_count=("candidate_id", "nunique"), lane_count=("seed_lane", "nunique"), label_family_count=("label_family", "nunique"))
        .reset_index()
    )
    lane_summary = (
        packet.groupby(["packet_role", "seed_lane"], dropna=False)
        .agg(candidate_count=("candidate_id", "nunique"), label_family_count=("label_family", "nunique"))
        .reset_index()
    )
    horizon_coverage = (
        pd.read_csv(ROWS)
        .groupby("seed_lane", dropna=False)
        .agg(candidate_count=("candidate_id", "nunique"), horizons=("label_horizon_h", lambda s: ",".join(map(str, sorted(set(s))))))
        .reset_index()
    )
    executable = packet[packet["packet_role"].eq("executable_clean")]
    executable_count = int(executable["candidate_id"].nunique())
    executable_lanes = set(executable["seed_lane"].astype(str))
    packet_lanes = set(packet["seed_lane"].astype(str))
    missing_executable_lanes = sorted(EXPECTED_LANES - executable_lanes)
    missing_packet_lanes = sorted(EXPECTED_LANES - packet_lanes)

    blockers: list[str] = []
    if executable_count < 6:
        blockers.append("executable_clean_count_lt_6")
    if len(executable_lanes) < 3:
        blockers.append("executable_clean_lane_count_lt_3")
    if missing_packet_lanes:
        blockers.append("repair_packet_missing_lanes")

    decision = "PASS_A7FFCORE24E_EXECUTABLE_REPAIR_PACKET_READY_FOR_CORE25" if not blockers else "HOLD_A7FFCORE24E_SOURCE_PACKET_LANE_COVERAGE_INSUFFICIENT"
    diagnosis = pd.DataFrame(
        [
            {"finding": "repair_packet_count", "value": int(packet["candidate_id"].nunique()), "interpretation": "includes executable clean and diagnostic repair seeds"},
            {"finding": "executable_clean_count", "value": executable_count, "interpretation": "true one-bar executable clean supply"},
            {"finding": "executable_clean_lanes", "value": len(executable_lanes), "interpretation": "true executable lane breadth"},
            {"finding": "missing_executable_lanes", "value": ",".join(missing_executable_lanes), "interpretation": "lanes not yet executable"},
            {"finding": "missing_packet_lanes", "value": ",".join(missing_packet_lanes), "interpretation": "lanes absent even as repair packet seeds"},
        ]
    )

    packet.to_csv(RUNTIME / "a7ffcore24e_repair_packet.csv", index=False)
    role_summary.to_csv(RUNTIME / "a7ffcore24e_role_summary.csv", index=False)
    lane_summary.to_csv(RUNTIME / "a7ffcore24e_lane_summary.csv", index=False)
    horizon_coverage.to_csv(RUNTIME / "a7ffcore24e_source_lane_horizon_coverage.csv", index=False)
    diagnosis.to_csv(RUNTIME / "a7ffcore24e_diagnosis.csv", index=False)

    manifest = {
        "stage": "A7FF-CORE24E",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE24",
        "source_decision": core24.get("decision"),
        "decision": decision,
        "blockers": blockers,
        "repair_packet_candidate_count": int(packet["candidate_id"].nunique()),
        "repair_packet_lane_count": int(len(packet_lanes)),
        "executable_clean_candidate_count": executable_count,
        "executable_clean_lane_count": int(len(executable_lanes)),
        "missing_executable_lanes": missing_executable_lanes,
        "missing_packet_lanes": missing_packet_lanes,
        "authorizes_core25_contract": decision.startswith("PASS_"),
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE25 lower-turnover bounded replay contract" if decision.startswith("PASS_") else "A7FF-CORE24R lane packet coverage forensic",
    }
    write_json(RUNTIME / "a7ffcore24e_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE24E EXECUTABLE LANE REPAIR PACKET",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE24E builds a bounded repair packet from existing rows. Same-bar repair seeds remain diagnostic-only. This stage does not authorize formula generation, search, alpha proof, shadow, paper, or live.",
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
        "## Role Summary",
        "",
        md_table(role_summary),
        "",
        "## Lane Summary",
        "",
        md_table(lane_summary),
        "",
        "## Source Lane Horizon Coverage",
        "",
        md_table(horizon_coverage),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
