from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore26r_targeted_numeric_probe_forensic"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE26R_TARGETED_NUMERIC_PROBE_FORENSIC_20260602.md"
CORE26E = REPO / "runtime" / "a7ffcore26e_targeted_numeric_probe_execution" / "a7ffcore26e_manifest.json"
ROWS = REPO / "runtime" / "a7ffcore26e_targeted_numeric_probe_execution" / "a7ffcore26e_numeric_rows.csv"

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
    source = read_json(CORE26E)
    if source.get("decision") != "HOLD_A7FFCORE26E_TARGETED_NUMERIC_PROBE_INSUFFICIENT":
        raise SystemExit(f"CORE26E is not in expected HOLD state: {source.get('decision')}")
    rows = pd.read_csv(ROWS)
    eval_rows = rows[rows["split"].isin(PREMAY) & rows["cost_bps"].eq(2)].copy()
    eval_rows["pass_spread"] = eval_rows["one_bar_costed_spread"].gt(0)
    eval_rows["pass_control"] = eval_rows["control_ratio"].lt(1.0)
    eval_rows["pass_both"] = eval_rows["pass_spread"] & eval_rows["pass_control"]

    cand = (
        eval_rows.groupby(["candidate_id", "seed_lane", "label_family", "label_horizon_h"], dropna=False)
        .agg(
            pass_both_splits=("pass_both", "sum"),
            pass_spread_splits=("pass_spread", "sum"),
            pass_control_splits=("pass_control", "sum"),
            min_spread=("one_bar_costed_spread", "min"),
            mean_spread=("one_bar_costed_spread", "mean"),
            max_control_ratio=("control_ratio", "max"),
            min_sample_rows=("sample_rows", "min"),
        )
        .reset_index()
    )
    near = cand[cand["pass_both_splits"].ge(2)].sort_values(["pass_both_splits", "mean_spread"], ascending=[False, False])
    lane = (
        cand.groupby("seed_lane", dropna=False)
        .agg(
            candidates=("candidate_id", "nunique"),
            pass_3_split=("pass_both_splits", lambda s: int((s >= 3).sum())),
            pass_2_split=("pass_both_splits", lambda s: int((s >= 2).sum())),
            pass_spread_3_split=("pass_spread_splits", lambda s: int((s >= 3).sum())),
            median_control=("max_control_ratio", "median"),
            median_spread=("mean_spread", "median"),
        )
        .reset_index()
    )
    label = (
        cand.groupby("label_family", dropna=False)
        .agg(
            candidates=("candidate_id", "nunique"),
            pass_3_split=("pass_both_splits", lambda s: int((s >= 3).sum())),
            pass_2_split=("pass_both_splits", lambda s: int((s >= 2).sum())),
            median_control=("max_control_ratio", "median"),
            median_spread=("mean_spread", "median"),
        )
        .reset_index()
    )
    blockers = []
    if int((cand["pass_both_splits"] >= 3).sum()) == 0:
        blockers.append("no_three_split_executable_candidates")
    if int((cand["pass_both_splits"] >= 2).sum()) < 6:
        blockers.append("near_miss_two_split_supply_lt_6")
    if int(lane.loc[lane["pass_2_split"].gt(0), "seed_lane"].nunique()) < 3:
        blockers.append("near_miss_lane_count_lt_3")
    if int((cand["min_sample_rows"] <= 0).sum()) > 0:
        blockers.append("sample_rows_zero_present")

    dominant_failure = "split_consistency_failure_after_targeted_generation"
    if "sample_rows_zero_present" in blockers:
        dominant_failure = "coverage_and_split_consistency_failure_after_targeted_generation"
    diagnosis = pd.DataFrame(
        [
            {"finding": "three_split_clean_count", "value": int((cand["pass_both_splits"] >= 3).sum()), "interpretation": "strict executable clean supply"},
            {"finding": "two_split_near_miss_count", "value": int((cand["pass_both_splits"] >= 2).sum()), "interpretation": "near-miss supply if one split fails"},
            {"finding": "lane_with_two_split_near_miss", "value": int(lane.loc[lane["pass_2_split"].gt(0), "seed_lane"].nunique()), "interpretation": "near-miss lane breadth"},
            {"finding": "zero_sample_candidate_count", "value": int((cand["min_sample_rows"] <= 0).sum()), "interpretation": "coverage/materialization holes in sampled probe"},
            {"finding": "dominant_failure", "value": dominant_failure, "interpretation": "why CORE26E cannot advance"},
        ]
    )
    recommended = pd.DataFrame(
        [
            {
                "next_stage": "A7FF-CORE26C",
                "action": "coverage-aware numeric probe repair contract",
                "rationale": "CORE26E produced eval-success but zero strict clean; repair must separate coverage holes from genuine split instability",
                "authorized": True,
            },
            {
                "next_stage": "A7FF-CORE27 replay contract",
                "action": "blocked",
                "rationale": "no three-split executable candidates",
                "authorized": False,
            },
        ]
    )

    cand.to_csv(RUNTIME / "a7ffcore26r_candidate_split_forensic.csv", index=False)
    near.to_csv(RUNTIME / "a7ffcore26r_near_miss_candidates.csv", index=False)
    lane.to_csv(RUNTIME / "a7ffcore26r_lane_forensic.csv", index=False)
    label.to_csv(RUNTIME / "a7ffcore26r_label_forensic.csv", index=False)
    diagnosis.to_csv(RUNTIME / "a7ffcore26r_diagnosis.csv", index=False)
    recommended.to_csv(RUNTIME / "a7ffcore26r_recommended_actions.csv", index=False)

    manifest = {
        "stage": "A7FF-CORE26R",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE26E",
        "source_decision": source.get("decision"),
        "decision": "PASS_A7FFCORE26R_TARGETED_NUMERIC_FORENSIC_COMPLETE_READY_FOR_CORE26C",
        "dominant_failure": dominant_failure,
        "blockers": blockers,
        "three_split_clean_count": int((cand["pass_both_splits"] >= 3).sum()),
        "two_split_near_miss_count": int((cand["pass_both_splits"] >= 2).sum()),
        "near_miss_lane_count": int(lane.loc[lane["pass_2_split"].gt(0), "seed_lane"].nunique()),
        "zero_sample_candidate_count": int((cand["min_sample_rows"] <= 0).sum()),
        "authorizes_core26c_contract": True,
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE26C coverage-aware numeric probe repair contract",
    }
    write_json(RUNTIME / "a7ffcore26r_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE26R TARGETED NUMERIC PROBE FORENSIC",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "CORE26R freezes the targeted numeric probe hold. It does not authorize replay, search, large search, alpha proof, shadow, paper, or live.",
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
        "## Lane Forensic",
        "",
        md_table(lane),
        "",
        "## Label Forensic",
        "",
        md_table(label),
        "",
        "## Top Near Miss Candidates",
        "",
        md_table(near.head(30)),
        "",
        "## Recommended Actions",
        "",
        md_table(recommended),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
