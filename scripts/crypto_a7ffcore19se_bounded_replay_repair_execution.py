from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore19se_bounded_replay_repair_execution"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE19SE_BOUNDED_REPLAY_REPAIR_EXECUTION_20260601.md"
CORE19S = REPO / "runtime" / "a7ffcore19s_bounded_replay_repair_contract" / "a7ffcore19s_manifest.json"
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


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    core19s = read_json(CORE19S)
    if core19s.get("decision") != "PASS_A7FFCORE19S_BOUNDED_REPLAY_REPAIR_CONTRACT_READY_FOR_CORE19SE":
        raise SystemExit(f"CORE19S is not ready: {core19s.get('decision')}")
    rows = pd.read_csv(ROWS)
    candidates = pd.read_csv(CANDIDATES)

    cost_rows = []
    clean_ids_by_cost: dict[int, set[str]] = {}
    for cost in sorted(rows["cost_bps"].unique()):
        eligible = rows[
            rows["split"].isin(PREMAY)
            & rows["cost_bps"].eq(cost)
            & pd.to_numeric(rows["cost_adjusted_spread"], errors="coerce").gt(0)
            & pd.to_numeric(rows["control_ratio_premay_max"], errors="coerce").lt(1.0)
            & pd.to_numeric(rows["one_bar_lag_spread"], errors="coerce").gt(0)
        ].copy()
        counts = eligible.groupby("candidate_id")["split"].nunique()
        clean_ids = set(counts[counts >= len(PREMAY)].index.astype(str))
        clean_ids_by_cost[int(cost)] = clean_ids
        clean_frame = candidates[candidates["candidate_id"].astype(str).isin(clean_ids)].copy()
        cost_rows.append(
            {
                "cost_bps": int(cost),
                "clean_candidate_count": len(clean_ids),
                "clean_seed_lane_count": int(clean_frame["seed_lane"].nunique()) if not clean_frame.empty else 0,
                "clean_non_l5_share": float(clean_frame["label_family"].astype(str).ne("L5_vol_adjusted_return").mean()) if not clean_frame.empty else 0.0,
            }
        )
    cost_summary = pd.DataFrame(cost_rows)
    best_cost = cost_summary.sort_values(["clean_candidate_count", "clean_seed_lane_count"], ascending=[False, False]).head(1)
    clean2 = candidates[candidates["candidate_id"].astype(str).isin(clean_ids_by_cost.get(2, set()))].copy()
    lane_cost_summary = (
        rows[rows["split"].isin(PREMAY)]
        .groupby(["seed_lane", "cost_bps"], dropna=False)
        .agg(
            median_cost_adjusted_spread=("cost_adjusted_spread", "median"),
            median_control_ratio=("control_ratio_premay_max", "median"),
            median_one_bar_lag_spread=("one_bar_lag_spread", "median"),
            candidate_count=("candidate_id", "nunique"),
        )
        .reset_index()
        .sort_values(["cost_bps", "seed_lane"])
    )
    diagnosis = pd.DataFrame(
        [
            {
                "diagnosis": "cost_dominant_failure",
                "evidence": "2bps clean count improves over 5bps but remains below replay-clean breadth gate",
                "value": int(cost_summary[cost_summary["cost_bps"].eq(2)]["clean_candidate_count"].iloc[0]) if not cost_summary[cost_summary["cost_bps"].eq(2)].empty else 0,
            },
            {
                "diagnosis": "lane_breadth_insufficient",
                "evidence": "best-cost clean lane count remains below 3",
                "value": int(best_cost["clean_seed_lane_count"].iloc[0]) if not best_cost.empty else 0,
            },
            {
                "diagnosis": "clean_clues_diagnostic_only",
                "evidence": "clean rows exist but are too few for search-readiness",
                "value": int(best_cost["clean_candidate_count"].iloc[0]) if not best_cost.empty else 0,
            },
        ]
    )
    cost_summary.to_csv(RUNTIME / "a7ffcore19se_cost_tier_clean_summary.csv", index=False)
    lane_cost_summary.to_csv(RUNTIME / "a7ffcore19se_lane_cost_summary.csv", index=False)
    clean2.to_csv(RUNTIME / "a7ffcore19se_2bps_clean_diagnostic_clues.csv", index=False)
    diagnosis.to_csv(RUNTIME / "a7ffcore19se_diagnosis.csv", index=False)

    best_clean = int(best_cost["clean_candidate_count"].iloc[0]) if not best_cost.empty else 0
    best_lanes = int(best_cost["clean_seed_lane_count"].iloc[0]) if not best_cost.empty else 0
    pass_gate = best_clean >= 12 and best_lanes >= 3
    decision = "PASS_A7FFCORE19SE_REPLAY_REPAIR_READY_FOR_CORE20" if pass_gate else "HOLD_A7FFCORE19SE_REPLAY_REPAIR_INSUFFICIENT"
    manifest = {
        "stage": "A7FF-CORE19SE",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE19S",
        "source_decision": core19s.get("decision"),
        "decision": decision,
        "best_clean_candidate_count": best_clean,
        "best_clean_seed_lane_count": best_lanes,
        "clean_2bps_candidate_count": int(cost_summary[cost_summary["cost_bps"].eq(2)]["clean_candidate_count"].iloc[0]) if not cost_summary[cost_summary["cost_bps"].eq(2)].empty else 0,
        "clean_5bps_candidate_count": int(cost_summary[cost_summary["cost_bps"].eq(5)]["clean_candidate_count"].iloc[0]) if not cost_summary[cost_summary["cost_bps"].eq(5)].empty else 0,
        "authorizes_core20": pass_gate,
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay_repair": True,
        "executes_search": False,
        "next_allowed": "A7FF-CORE20 replay-clean consolidation / search-readiness contract" if pass_gate else "A7FF-CORE19SER replay repair forensic",
    }
    write_json(RUNTIME / "a7ffcore19se_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE19SE BOUNDED REPLAY REPAIR EXECUTION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE19SE performs cost/lag/label/lane replay repair attribution using existing CORE19E replay rows. It does not execute formula generation, search, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Cost Tier Clean Summary",
        "",
        md_table(cost_summary),
        "",
        "## Diagnosis",
        "",
        md_table(diagnosis),
        "",
        "## 2bps Diagnostic Clean Clues",
        "",
        md_table(clean2),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
