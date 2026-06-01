from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore23e_executable_horizon_diagnostic_audit"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE23E_EXECUTABLE_HORIZON_DIAGNOSTIC_AUDIT_20260601.md"
CORE23 = REPO / "runtime" / "a7ffcore23_executable_horizon_redesign_contract" / "a7ffcore23_manifest.json"
ROWS = REPO / "runtime" / "a7ffcore19e_bounded_replay_execution" / "a7ffcore19e_replay_rows.csv"

PREMAY = ["validation_2025H1", "test_2025H2", "recent_oos_2026JanApr"]


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


def horizon_bucket(h: int) -> str:
    if h <= 1:
        return "H1_high_turnover"
    if h <= 8:
        return "H4_H8_medium_turnover"
    return "H24_low_turnover"


def clean_candidates(data: pd.DataFrame, spread_col: str, cost: int, min_horizon: int) -> pd.DataFrame:
    x = data[
        data["split"].isin(PREMAY)
        & data["cost_bps"].eq(cost)
        & pd.to_numeric(data["label_horizon_h"], errors="coerce").ge(min_horizon)
    ].copy()
    x["test_spread"] = pd.to_numeric(x[spread_col], errors="coerce")
    x["control_ratio"] = pd.to_numeric(x["control_ratio_premay_max"], errors="coerce")
    ok = x[x["test_spread"].gt(0) & x["control_ratio"].lt(1.0)]
    split_counts = ok.groupby("candidate_id")["split"].nunique()
    clean_ids = set(split_counts[split_counts >= len(PREMAY)].index.astype(str))
    return x[x["candidate_id"].astype(str).isin(clean_ids)].copy()


def summarize_clean(data: pd.DataFrame, spread_col: str, cost: int, min_horizon: int, name: str) -> dict[str, Any]:
    clean = clean_candidates(data, spread_col, cost, min_horizon)
    candidates = clean.drop_duplicates("candidate_id")
    return {
        "policy": name,
        "cost_bps": int(cost),
        "min_horizon_h": int(min_horizon),
        "clean_candidate_count": int(candidates["candidate_id"].nunique()),
        "clean_lane_count": int(candidates["seed_lane"].nunique()) if not candidates.empty else 0,
        "clean_label_family_count": int(candidates["label_family"].nunique()) if not candidates.empty else 0,
        "non_l5_candidate_count": int(candidates["label_family"].astype(str).ne("L5_vol_adjusted_return").sum()) if not candidates.empty else 0,
        "non_l5_share": float(candidates["label_family"].astype(str).ne("L5_vol_adjusted_return").mean()) if not candidates.empty else 0.0,
        "horizon_buckets": ",".join(sorted(candidates["horizon_bucket"].astype(str).unique())) if not candidates.empty else "",
    }


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    core23 = read_json(CORE23)
    if core23.get("decision") != "PASS_A7FFCORE23_EXECUTABLE_HORIZON_REDESIGN_CONTRACT_READY_FOR_CORE23E":
        raise SystemExit(f"CORE23 is not ready: {core23.get('decision')}")

    rows = pd.read_csv(ROWS)
    rows["label_horizon_h"] = pd.to_numeric(rows["label_horizon_h"], errors="coerce").fillna(0).astype(int)
    rows["horizon_bucket"] = rows["label_horizon_h"].map(horizon_bucket)
    rows["one_bar_costed_spread"] = pd.to_numeric(rows["one_bar_lag_spread"], errors="coerce") - (
        2.0 * pd.to_numeric(rows["cost_bps"], errors="coerce") / 10000.0
    )

    policy_rows = []
    for cost in sorted(rows["cost_bps"].unique()):
        policy_rows.append(summarize_clean(rows, "one_bar_costed_spread", int(cost), 1, "one_bar_any_horizon"))
        policy_rows.append(summarize_clean(rows, "one_bar_costed_spread", int(cost), 4, "one_bar_executable_h4_plus"))
        policy_rows.append(summarize_clean(rows, "one_bar_costed_spread", int(cost), 24, "one_bar_low_turnover_h24"))
        policy_rows.append(summarize_clean(rows, "cost_adjusted_spread", int(cost), 4, "same_bar_diagnostic_h4_plus"))

    matrix = pd.DataFrame(policy_rows)
    primary = matrix[matrix["policy"].eq("one_bar_executable_h4_plus")].sort_values(
        ["clean_candidate_count", "clean_lane_count", "clean_label_family_count"],
        ascending=[False, False, False],
    )
    best = primary.head(1)
    best_count = int(best["clean_candidate_count"].iloc[0]) if not best.empty else 0
    best_lanes = int(best["clean_lane_count"].iloc[0]) if not best.empty else 0
    best_labels = int(best["clean_label_family_count"].iloc[0]) if not best.empty else 0
    best_non_l5 = int(best["non_l5_candidate_count"].iloc[0]) if not best.empty else 0
    best_cost = int(best["cost_bps"].iloc[0]) if not best.empty else 0

    clean_best = clean_candidates(rows, "one_bar_costed_spread", best_cost, 4) if best_cost else pd.DataFrame()
    clean_candidates_view = (
        clean_best.drop_duplicates("candidate_id")[
            [
                "candidate_id",
                "seed_lane",
                "second_pass_family",
                "label_family",
                "label_horizon_h",
                "left_field",
                "left_transform",
                "operator",
                "right_field",
                "right_transform",
                "control_ratio_premay_max",
            ]
        ].sort_values(["seed_lane", "label_family", "candidate_id"])
        if not clean_best.empty
        else pd.DataFrame()
    )

    by_lane = (
        clean_candidates_view.groupby("seed_lane", dropna=False)
        .agg(clean_candidate_count=("candidate_id", "nunique"), label_family_count=("label_family", "nunique"))
        .reset_index()
        if not clean_candidates_view.empty
        else pd.DataFrame(columns=["seed_lane", "clean_candidate_count", "label_family_count"])
    )
    by_label = (
        clean_candidates_view.groupby("label_family", dropna=False)
        .agg(clean_candidate_count=("candidate_id", "nunique"), lane_count=("seed_lane", "nunique"))
        .reset_index()
        if not clean_candidates_view.empty
        else pd.DataFrame(columns=["label_family", "clean_candidate_count", "lane_count"])
    )

    blockers: list[str] = []
    if best_count < 6:
        blockers.append("executable_h4_plus_clean_count_lt_6")
    if best_lanes < 3:
        blockers.append("executable_h4_plus_clean_lane_count_lt_3")
    if best_labels < 3:
        blockers.append("executable_h4_plus_label_family_count_lt_3")
    if best_non_l5 < 3:
        blockers.append("non_l5_executable_clean_count_lt_3")

    decision = "PASS_A7FFCORE23E_EXECUTABLE_HORIZON_DIAGNOSTIC_READY_FOR_CORE24" if not blockers else "HOLD_A7FFCORE23E_EXECUTABLE_HORIZON_SUPPLY_INSUFFICIENT"
    diagnosis = pd.DataFrame(
        [
            {"finding": "best_executable_h4_plus_clean_candidate_count", "value": best_count, "interpretation": "primary lower-turnover executable clean supply"},
            {"finding": "best_executable_h4_plus_clean_lane_count", "value": best_lanes, "interpretation": "lane breadth after one-bar executable cost gate"},
            {"finding": "best_executable_h4_plus_label_family_count", "value": best_labels, "interpretation": "label breadth after one-bar executable cost gate"},
            {"finding": "best_executable_h4_plus_non_l5_count", "value": best_non_l5, "interpretation": "non-L5 executable translation supply"},
            {"finding": "best_cost_bps", "value": best_cost, "interpretation": "best cost tier remains diagnostic unless breadth gates pass"},
        ]
    )

    matrix.to_csv(RUNTIME / "a7ffcore23e_executable_horizon_matrix.csv", index=False)
    clean_candidates_view.to_csv(RUNTIME / "a7ffcore23e_best_executable_clean_candidates.csv", index=False)
    by_lane.to_csv(RUNTIME / "a7ffcore23e_clean_by_lane.csv", index=False)
    by_label.to_csv(RUNTIME / "a7ffcore23e_clean_by_label.csv", index=False)
    diagnosis.to_csv(RUNTIME / "a7ffcore23e_diagnosis.csv", index=False)

    manifest = {
        "stage": "A7FF-CORE23E",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE23",
        "source_decision": core23.get("decision"),
        "decision": decision,
        "blockers": blockers,
        "best_cost_bps": best_cost,
        "best_executable_h4_plus_clean_candidate_count": best_count,
        "best_executable_h4_plus_clean_lane_count": best_lanes,
        "best_executable_h4_plus_label_family_count": best_labels,
        "best_executable_h4_plus_non_l5_count": best_non_l5,
        "authorizes_core24_contract": decision.startswith("PASS_"),
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE24 lower-turnover bounded replay contract" if decision.startswith("PASS_") else "A7FF-CORE23R executable-horizon forensic",
    }
    write_json(RUNTIME / "a7ffcore23e_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE23E EXECUTABLE-HORIZON DIAGNOSTIC AUDIT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE23E audits whether the locked packet translates into lower-turnover executable evidence. It reuses existing CORE19E replay rows and does not execute formula generation, search, alpha proof, shadow, paper, or live.",
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
        "## Executable Horizon Matrix",
        "",
        md_table(matrix),
        "",
        "## Best Executable Clean Candidates",
        "",
        md_table(clean_candidates_view, max_rows=40),
        "",
        "## Clean By Lane",
        "",
        md_table(by_lane),
        "",
        "## Clean By Label",
        "",
        md_table(by_label),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
