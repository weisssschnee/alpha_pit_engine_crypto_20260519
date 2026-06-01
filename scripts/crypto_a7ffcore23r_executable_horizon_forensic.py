from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore23r_executable_horizon_forensic"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE23R_EXECUTABLE_HORIZON_FORENSIC_20260601.md"
CORE23E = REPO / "runtime" / "a7ffcore23e_executable_horizon_diagnostic_audit" / "a7ffcore23e_manifest.json"
MATRIX = REPO / "runtime" / "a7ffcore23e_executable_horizon_diagnostic_audit" / "a7ffcore23e_executable_horizon_matrix.csv"
CLEAN = REPO / "runtime" / "a7ffcore23e_executable_horizon_diagnostic_audit" / "a7ffcore23e_best_executable_clean_candidates.csv"


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
    source = read_json(CORE23E)
    if source.get("decision") != "HOLD_A7FFCORE23E_EXECUTABLE_HORIZON_SUPPLY_INSUFFICIENT":
        raise SystemExit(f"CORE23E is not in expected HOLD state: {source.get('decision')}")

    matrix = pd.read_csv(MATRIX)
    clean = pd.read_csv(CLEAN) if CLEAN.exists() else pd.DataFrame()
    primary = matrix[matrix["policy"].eq("one_bar_executable_h4_plus")].copy()
    same_bar = matrix[matrix["policy"].eq("same_bar_diagnostic_h4_plus")].copy()

    best_primary = primary.sort_values(["clean_candidate_count", "clean_lane_count"], ascending=[False, False]).head(1)
    best_same = same_bar.sort_values(["clean_candidate_count", "clean_lane_count"], ascending=[False, False]).head(1)
    primary_count = int(best_primary["clean_candidate_count"].iloc[0]) if not best_primary.empty else 0
    primary_lanes = int(best_primary["clean_lane_count"].iloc[0]) if not best_primary.empty else 0
    same_count = int(best_same["clean_candidate_count"].iloc[0]) if not best_same.empty else 0
    same_lanes = int(best_same["clean_lane_count"].iloc[0]) if not best_same.empty else 0

    lane_presence = (
        clean.groupby("seed_lane", dropna=False)
        .agg(clean_candidate_count=("candidate_id", "nunique"), label_family_count=("label_family", "nunique"))
        .reset_index()
        if not clean.empty
        else pd.DataFrame(columns=["seed_lane", "clean_candidate_count", "label_family_count"])
    )
    present_lanes = set(lane_presence["seed_lane"].astype(str))
    expected_lanes = {
        "S0_positioning_price_basis",
        "S1_basis_premium_funding",
        "S2_taker_flow_liquidity_oi",
        "S3_cross_family_bridge",
    }
    missing_lanes = sorted(expected_lanes - present_lanes)
    label_presence = (
        clean.groupby("label_family", dropna=False)
        .agg(clean_candidate_count=("candidate_id", "nunique"), lane_count=("seed_lane", "nunique"))
        .reset_index()
        if not clean.empty
        else pd.DataFrame(columns=["label_family", "clean_candidate_count", "lane_count"])
    )
    field_usage = (
        pd.concat(
            [
                clean[["left_field"]].rename(columns={"left_field": "field"}),
                clean[["right_field"]].rename(columns={"right_field": "field"}),
            ],
            ignore_index=True,
        )
        .groupby("field", dropna=False)
        .size()
        .reset_index(name="usage_count")
        .sort_values("usage_count", ascending=False)
        if not clean.empty
        else pd.DataFrame(columns=["field", "usage_count"])
    )

    diagnosis = pd.DataFrame(
        [
            {
                "finding": "executable_supply_exists",
                "value": primary_count,
                "interpretation": "there is H4+ one-bar executable evidence, but not enough breadth",
            },
            {
                "finding": "lane_breadth_deficit",
                "value": primary_lanes,
                "interpretation": "only two seed lanes survive; missing lanes must be repaired before any search",
            },
            {
                "finding": "same_bar_excess_supply",
                "value": same_count - primary_count,
                "interpretation": "same-bar H4+ diagnostics still exceed executable one-bar evidence",
            },
            {
                "finding": "missing_executable_lanes",
                "value": ",".join(missing_lanes),
                "interpretation": "lane repair target set",
            },
            {
                "finding": "dominant_failure",
                "value": "executable_lane_supply_too_narrow",
                "interpretation": "the bottleneck is not label translation anymore; it is executable breadth",
            },
        ]
    )
    recommended = pd.DataFrame(
        [
            {
                "next_stage": "A7FF-CORE24",
                "action": "lower-turnover executable lane repair contract",
                "rationale": "repair missing S0/S1 executable lanes and H4/H8 one-bar conversion without open formula search",
                "authorized": True,
            },
            {
                "next_stage": "A7FF search / large search",
                "action": "blocked",
                "rationale": "current executable clean supply is 4 candidates / 2 lanes only",
                "authorized": False,
            },
        ]
    )

    diagnosis.to_csv(RUNTIME / "a7ffcore23r_diagnosis.csv", index=False)
    lane_presence.to_csv(RUNTIME / "a7ffcore23r_lane_presence.csv", index=False)
    label_presence.to_csv(RUNTIME / "a7ffcore23r_label_presence.csv", index=False)
    field_usage.to_csv(RUNTIME / "a7ffcore23r_field_usage.csv", index=False)
    recommended.to_csv(RUNTIME / "a7ffcore23r_recommended_actions.csv", index=False)

    manifest = {
        "stage": "A7FF-CORE23R",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE23E",
        "source_decision": source.get("decision"),
        "decision": "PASS_A7FFCORE23R_EXECUTABLE_HORIZON_FORENSIC_COMPLETE_READY_FOR_CORE24",
        "dominant_failure": "executable_lane_supply_too_narrow",
        "best_executable_h4_plus_clean_candidate_count": primary_count,
        "best_executable_h4_plus_clean_lane_count": primary_lanes,
        "best_same_bar_h4_plus_candidate_count": same_count,
        "best_same_bar_h4_plus_lane_count": same_lanes,
        "missing_executable_lanes": missing_lanes,
        "authorizes_core24_contract": True,
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE24 lower-turnover executable lane repair contract",
    }
    write_json(RUNTIME / "a7ffcore23r_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE23R EXECUTABLE-HORIZON FORENSIC",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "CORE23R freezes the CORE23E hold and identifies the next bottleneck. It does not authorize formula generation, search, large search, alpha proof, shadow, paper, or live.",
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
        "## Lane Presence",
        "",
        md_table(lane_presence),
        "",
        "## Label Presence",
        "",
        md_table(label_presence),
        "",
        "## Field Usage",
        "",
        md_table(field_usage),
        "",
        "## Recommended Actions",
        "",
        md_table(recommended),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
