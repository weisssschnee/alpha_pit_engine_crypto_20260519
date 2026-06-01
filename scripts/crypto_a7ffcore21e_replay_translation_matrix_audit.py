from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore21e_replay_translation_matrix_audit"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE21E_REPLAY_TRANSLATION_MATRIX_AUDIT_20260601.md"
CORE21 = REPO / "runtime" / "a7ffcore21_replay_translation_reset_contract" / "a7ffcore21_manifest.json"
ROWS = REPO / "runtime" / "a7ffcore19e_bounded_replay_execution" / "a7ffcore19e_replay_rows.csv"
CANDIDATES = REPO / "runtime" / "a7ffcore19e_bounded_replay_execution" / "a7ffcore19e_candidate_summary.csv"

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


def clean_counts(rows: pd.DataFrame, group_cols: list[str], require_lag: bool = True) -> pd.DataFrame:
    data = rows[rows["split"].isin(PREMAY)].copy()
    data["spread_ok"] = pd.to_numeric(data["cost_adjusted_spread"], errors="coerce").gt(0)
    data["control_ok"] = pd.to_numeric(data["control_ratio_premay_max"], errors="coerce").lt(1.0)
    data["lag_ok"] = pd.to_numeric(data["one_bar_lag_spread"], errors="coerce").gt(0)
    ok = data[data["spread_ok"] & data["control_ok"] & (data["lag_ok"] if require_lag else True)].copy()
    split_counts = ok.groupby(group_cols + ["candidate_id"], dropna=False)["split"].nunique().reset_index(name="clean_split_count")
    clean = split_counts[split_counts["clean_split_count"] >= len(PREMAY)].copy()
    return (
        clean.groupby(group_cols, dropna=False)
        .agg(clean_candidate_count=("candidate_id", "nunique"))
        .reset_index()
    )


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    core21 = read_json(CORE21)
    if core21.get("decision") != "PASS_A7FFCORE21_REPLAY_TRANSLATION_RESET_CONTRACT_READY_FOR_CORE21E":
        raise SystemExit(f"CORE21 is not ready for CORE21E: {core21.get('decision')}")
    rows = pd.read_csv(ROWS)
    candidates = pd.read_csv(CANDIDATES)

    label_cost = clean_counts(rows, ["label_family", "cost_bps"], require_lag=True)
    label_cost_all = (
        rows[rows["split"].isin(PREMAY)]
        .groupby(["label_family", "cost_bps"], dropna=False)
        .agg(candidate_count=("candidate_id", "nunique"), median_cost_adjusted_spread=("cost_adjusted_spread", "median"), median_control_ratio=("control_ratio_premay_max", "median"), median_lag_spread=("one_bar_lag_spread", "median"))
        .reset_index()
    )
    label_cost = label_cost_all.merge(label_cost, on=["label_family", "cost_bps"], how="left")
    label_cost["clean_candidate_count"] = label_cost["clean_candidate_count"].fillna(0).astype(int)

    lane_cost = clean_counts(rows, ["seed_lane", "cost_bps"], require_lag=True)
    lane_cost_all = (
        rows[rows["split"].isin(PREMAY)]
        .groupby(["seed_lane", "cost_bps"], dropna=False)
        .agg(candidate_count=("candidate_id", "nunique"), median_cost_adjusted_spread=("cost_adjusted_spread", "median"), median_control_ratio=("control_ratio_premay_max", "median"), median_lag_spread=("one_bar_lag_spread", "median"))
        .reset_index()
    )
    lane_cost = lane_cost_all.merge(lane_cost, on=["seed_lane", "cost_bps"], how="left")
    lane_cost["clean_candidate_count"] = lane_cost["clean_candidate_count"].fillna(0).astype(int)

    label_horizon = clean_counts(rows[rows["cost_bps"].eq(2)], ["label_family", "label_horizon_h"], require_lag=True)
    label_horizon_all = (
        rows[rows["split"].isin(PREMAY) & rows["cost_bps"].eq(2)]
        .groupby(["label_family", "label_horizon_h"], dropna=False)
        .agg(candidate_count=("candidate_id", "nunique"), median_cost_adjusted_spread=("cost_adjusted_spread", "median"), median_control_ratio=("control_ratio_premay_max", "median"), median_lag_spread=("one_bar_lag_spread", "median"))
        .reset_index()
    )
    label_horizon = label_horizon_all.merge(label_horizon, on=["label_family", "label_horizon_h"], how="left")
    label_horizon["clean_candidate_count"] = label_horizon["clean_candidate_count"].fillna(0).astype(int)

    lag_relief = clean_counts(rows, ["label_family", "cost_bps"], require_lag=False).rename(columns={"clean_candidate_count": "clean_without_lag_gate"})
    lag_matrix = label_cost[["label_family", "cost_bps", "clean_candidate_count"]].merge(lag_relief, on=["label_family", "cost_bps"], how="left")
    lag_matrix["lag_gate_loss"] = lag_matrix["clean_without_lag_gate"].fillna(0).astype(int) - lag_matrix["clean_candidate_count"]

    best_label_cost = label_cost.sort_values(["clean_candidate_count", "candidate_count"], ascending=[False, False]).head(10)
    best_lane_cost = lane_cost.sort_values(["clean_candidate_count", "candidate_count"], ascending=[False, False]).head(10)
    best_total_clean = int(best_label_cost["clean_candidate_count"].max()) if not best_label_cost.empty else 0
    best_lane_clean = int(best_lane_cost["clean_candidate_count"].max()) if not best_lane_cost.empty else 0
    non_l5_clean_2bps = int(label_cost[label_cost["cost_bps"].eq(2) & label_cost["label_family"].astype(str).ne("L5_vol_adjusted_return")]["clean_candidate_count"].sum())
    l5_clean_2bps = int(label_cost[label_cost["cost_bps"].eq(2) & label_cost["label_family"].astype(str).eq("L5_vol_adjusted_return")]["clean_candidate_count"].sum())
    clean_candidate_ids = set(candidates[candidates["replay_clean"].astype(str).str.lower().eq("true")]["candidate_id"].astype(str))
    clean_lanes = int(candidates[candidates["candidate_id"].astype(str).isin(clean_candidate_ids)]["seed_lane"].nunique()) if clean_candidate_ids else 0

    blockers: list[str] = []
    if non_l5_clean_2bps < 3:
        blockers.append("non_l5_2bps_clean_lt_3")
    if best_total_clean < 6:
        blockers.append("best_label_cost_clean_lt_6")
    if clean_lanes < 3:
        blockers.append("current_replay_clean_lanes_lt_3")
    if l5_clean_2bps >= non_l5_clean_2bps and l5_clean_2bps > 0:
        blockers.append("l5_not_subordinate_to_non_l5")

    decision = "PASS_A7FFCORE21E_TRANSLATION_MATRIX_READY_FOR_CORE22" if not blockers else "HOLD_A7FFCORE21E_TRANSLATION_MATRIX_INSUFFICIENT"
    diagnosis = pd.DataFrame(
        [
            {"finding": "best_label_cost_clean", "value": best_total_clean, "interpretation": "max clean candidates by label/cost bucket"},
            {"finding": "best_lane_cost_clean", "value": best_lane_clean, "interpretation": "max clean candidates by lane/cost bucket"},
            {"finding": "non_l5_clean_2bps", "value": non_l5_clean_2bps, "interpretation": "non-L5 translation at lowest cost tier"},
            {"finding": "l5_clean_2bps", "value": l5_clean_2bps, "interpretation": "L5 diagnostic-only translation at lowest cost tier"},
            {"finding": "current_clean_lanes", "value": clean_lanes, "interpretation": "lane breadth under original CORE19E clean rule"},
        ]
    )

    label_cost.to_csv(RUNTIME / "a7ffcore21e_label_cost_matrix.csv", index=False)
    lane_cost.to_csv(RUNTIME / "a7ffcore21e_lane_cost_matrix.csv", index=False)
    label_horizon.to_csv(RUNTIME / "a7ffcore21e_label_horizon_matrix_2bps.csv", index=False)
    lag_matrix.to_csv(RUNTIME / "a7ffcore21e_lag_gate_matrix.csv", index=False)
    diagnosis.to_csv(RUNTIME / "a7ffcore21e_diagnosis.csv", index=False)

    manifest = {
        "stage": "A7FF-CORE21E",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE21",
        "source_decision": core21.get("decision"),
        "decision": decision,
        "blockers": blockers,
        "best_label_cost_clean_candidate_count": best_total_clean,
        "best_lane_cost_clean_candidate_count": best_lane_clean,
        "non_l5_clean_2bps": non_l5_clean_2bps,
        "l5_clean_2bps": l5_clean_2bps,
        "current_replay_clean_lanes": clean_lanes,
        "authorizes_core22_contract": decision.startswith("PASS_"),
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE22 bounded replay objective repair contract" if decision.startswith("PASS_") else "A7FF-CORE21R translation matrix forensic",
    }
    write_json(RUNTIME / "a7ffcore21e_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE21E REPLAY TRANSLATION MATRIX AUDIT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE21E audits label/cost/lag/lane translation using existing CORE19E replay rows. It does not execute formula generation, search, large search, alpha proof, shadow, paper, or live.",
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
        "## Best Label/Cost Buckets",
        "",
        md_table(best_label_cost),
        "",
        "## Best Lane/Cost Buckets",
        "",
        md_table(best_lane_cost),
        "",
        "## Lag Gate Matrix",
        "",
        md_table(lag_matrix.sort_values(["lag_gate_loss", "clean_without_lag_gate"], ascending=[False, False]).head(20)),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
