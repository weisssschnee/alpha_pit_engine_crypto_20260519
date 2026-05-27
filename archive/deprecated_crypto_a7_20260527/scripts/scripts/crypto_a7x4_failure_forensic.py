from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
A7X3_DIR = ROOT / "runtime" / "a7x3_small_controlled_diagnostic"
OUT_DIR = ROOT / "runtime" / "a7x4_failure_forensic"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7X4_FAILURE_FORENSIC_20260522.md"

VALIDATION = "validation_2025H1"
RECENT = "recent_oos_2025H2_2026Apr"
MAY = "fresh_may_2026"


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    return df.head(max_rows).to_markdown(index=False)


def clean_float(value: Any) -> float | None:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if np.isfinite(out) else None


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    labels = pd.read_csv(A7X3_DIR / "a7x3_candidate_labels.csv")
    wide = pd.read_csv(A7X3_DIR / "a7x3_wide_metrics.csv")
    parity = pd.read_csv(A7X3_DIR / "a7x3_fast_book_parity_audit.csv")
    authorization = json.loads((A7X3_DIR / "a7x3_authorization_matrix.json").read_text(encoding="utf-8"))
    return labels, wide, parity, authorization


def label_summary(labels: pd.DataFrame) -> pd.DataFrame:
    return (
        labels.groupby(["production_family", "a7x3_label"], dropna=False)
        .agg(
            rows=("candidate_id", "count"),
            median_validation_net10=("validation_net10", "median"),
            median_recent_net10=("recent_net10", "median"),
            median_recent_net20=("recent_net20", "median"),
            median_may_net10=("may_net10", "median"),
        )
        .reset_index()
        .sort_values(["production_family", "a7x3_label"])
    )


def control_contamination_detail(labels: pd.DataFrame, wide: pd.DataFrame) -> pd.DataFrame:
    contaminated = labels[labels["a7x3_label"].eq("A7X3_HOLD_CONTROL_CONTAMINATED")].copy()
    controls = wide[wide["object_type"].eq("control")].copy()
    val_col = f"net_sum_10bps__{VALIDATION}"
    recent_col = f"net_sum_10bps__{RECENT}"
    may_col = f"net_sum_10bps__{MAY}"
    control_rows = controls[
        pd.to_numeric(controls[val_col], errors="coerce").gt(0)
        & pd.to_numeric(controls[recent_col], errors="coerce").gt(0)
    ].copy()
    detail = control_rows.merge(
        contaminated[
            [
                "candidate_id",
                "production_family",
                "expression",
                "horizon",
                "validation_net10",
                "recent_net10",
                "recent_net20",
                "may_net10",
                "derived_feature_id",
                "source_fields",
                "transform",
            ]
        ],
        left_on="base_candidate_id",
        right_on="candidate_id",
        how="inner",
        suffixes=("_control", "_candidate"),
    )
    if detail.empty:
        return detail
    keep = [
        "candidate_id_candidate",
        "production_family_candidate",
        "expression_candidate",
        "horizon_candidate",
        "control_mode",
        "candidate_id_control",
        "validation_net10",
        "recent_net10",
        "recent_net20",
        "may_net10",
        val_col,
        recent_col,
        may_col,
        "derived_feature_id",
        "source_fields",
        "transform",
    ]
    detail = detail[keep].rename(
        columns={
            "candidate_id_candidate": "candidate_id",
            "production_family_candidate": "production_family",
            "expression_candidate": "expression",
            "horizon_candidate": "horizon",
            "candidate_id_control": "control_id",
            val_col: "control_validation_net10",
            recent_col: "control_recent_net10",
            may_col: "control_may_net10",
        }
    )
    return detail.sort_values(["production_family", "candidate_id", "control_mode"])


def near_miss_records(labels: pd.DataFrame, wide: pd.DataFrame) -> pd.DataFrame:
    near = labels[labels["a7x3_label"].eq("A7X3_NEAR_MISS_MAY_STRESS_FAIL")].copy()
    controls = wide[wide["object_type"].eq("control")].copy()
    val_col = f"net_sum_10bps__{VALIDATION}"
    recent_col = f"net_sum_10bps__{RECENT}"
    may_col = f"net_sum_10bps__{MAY}"
    summaries = []
    for _, row in near.iterrows():
        matched = controls[controls["base_candidate_id"].eq(row["candidate_id"])].copy()
        summaries.append(
            {
                "candidate_id": row["candidate_id"],
                "production_family": row["production_family"],
                "expression": row["expression"],
                "horizon": row["horizon"],
                "validation_net10": row["validation_net10"],
                "recent_net10": row["recent_net10"],
                "recent_net20": row["recent_net20"],
                "may_net10": row["may_net10"],
                "max_control_validation_net10": row["max_control_validation_net10"],
                "max_control_recent_net10": row["max_control_recent_net10"],
                "best_control_may_net10": clean_float(pd.to_numeric(matched[may_col], errors="coerce").max()) if not matched.empty else None,
                "control_val_recent_positive_count": row["control_val_recent_positive_count"],
                "dominates_controls": row["dominates_controls"],
                "failure_interpretation": "pre_may_control_clean_cost20_survivor_but_may_negative",
                "promotion_status": "NOT_PROMOTABLE",
            }
        )
    return pd.DataFrame(summaries)


def failure_mode_matrix(labels: pd.DataFrame, contamination: pd.DataFrame, near: pd.DataFrame) -> pd.DataFrame:
    total = len(labels)
    rows = [
        {
            "failure_mode": "raw_validation_or_recent_fail",
            "count": int(labels["a7x3_label"].eq("A7X3_HOLD_RAW_VAL_RECENT_FAIL").sum()),
            "share": clean_float(labels["a7x3_label"].eq("A7X3_HOLD_RAW_VAL_RECENT_FAIL").mean()),
            "interpretation": "candidate cannot clear basic non-May raw evidence",
            "next_action": "do not tune May; lower priority for same-space expansion",
        },
        {
            "failure_mode": "control_contaminated",
            "count": int(labels["a7x3_label"].eq("A7X3_HOLD_CONTROL_CONTAMINATED").sum()),
            "share": clean_float(labels["a7x3_label"].eq("A7X3_HOLD_CONTROL_CONTAMINATED").mean()),
            "interpretation": "matched null/control can be positive in validation and recent",
            "next_action": "keep negative-control dominance as hard gate",
        },
        {
            "failure_mode": "may_stress_fail_after_non_may_pass",
            "count": int(labels["a7x3_label"].eq("A7X3_NEAR_MISS_MAY_STRESS_FAIL").sum()),
            "share": clean_float(labels["a7x3_label"].eq("A7X3_NEAR_MISS_MAY_STRESS_FAIL").mean()),
            "interpretation": "pre-May clean clue does not survive known adversarial stress",
            "next_action": "record as stress clue only; not candidate",
        },
        {
            "failure_mode": "clean_research_clue",
            "count": int(labels["a7x3_label"].eq("A7X_RESEARCH_CLUE").sum()),
            "share": clean_float(labels["a7x3_label"].eq("A7X_RESEARCH_CLUE").mean()) if total else None,
            "interpretation": "no current A7X family clears all gates",
            "next_action": "do not run A7X-4 candidate forensic; redesign objective or move to A7S",
        },
    ]
    out = pd.DataFrame(rows)
    out["total_candidates"] = total
    out["contaminating_control_rows"] = int(len(contamination))
    out["near_miss_rows"] = int(len(near))
    return out


def route_scorecard() -> pd.DataFrame:
    rows = [
        {
            "route": "A7X_same_family_expansion",
            "status": "REJECT",
            "rationale": "A7X-3 produced 0 clean research clues and 28 control-contaminated candidates",
            "authorized": False,
        },
        {
            "route": "A7X_objective_revision",
            "status": "LOW_PRIORITY_DIAGNOSTIC",
            "rationale": "near-miss motif is narrow and May-negative; useful only to refine weak-prior registry",
            "authorized": True,
        },
        {
            "route": "A7S_new_data_horizon_contract",
            "status": "PRIMARY_NEXT",
            "rationale": "data-line is clean but current aggTrades objective/family does not produce promotable signal evidence",
            "authorized": True,
        },
        {
            "route": "A7T_forward_locked_observation",
            "status": "PARALLEL_EVIDENCE_HYGIENE",
            "rationale": "May is already known stress; forward-only observation is needed for clean future evidence",
            "authorized": True,
        },
        {
            "route": "alpha_shadow_paper_live",
            "status": "BLOCKED",
            "rationale": "no alpha proof object; controls and May stress block promotion",
            "authorized": False,
        },
    ]
    return pd.DataFrame(rows)


def write_report(
    now: str,
    labels: pd.DataFrame,
    parity: pd.DataFrame,
    summary: pd.DataFrame,
    contamination: pd.DataFrame,
    near: pd.DataFrame,
    matrix: pd.DataFrame,
    routes: pd.DataFrame,
    authorization: dict[str, Any],
) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Crypto A7X-4 Failure Forensic",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{authorization['decision']}`",
        "- executes_search: `False`",
        "- executes_replay: `False`",
        "- alpha proof / expanded replay / full search / shadow / paper / live: `NOT_AUTHORIZED`",
        "",
        "## Scope",
        "",
        "A7X-4 reads A7X-3 artifacts only. It does not generate formulas, rerun replay, or reinterpret A7X-3 near-misses as candidates.",
        "",
        "May remains post-selection stress only. A7X-4 uses May only for failure attribution and authorization blocking.",
        "",
        "## Bias Audit",
        "",
        "- Factor/run: `A7X-3 aggTrades reset diagnostic`",
        "- Data source and universe: `core3 aggTrades-enhanced panel from source-traced A7U-0R data`",
        "- Frequency and horizon: `1h panel; candidate horizons 24h/48h in this small diagnostic`",
        "- Cost model: `10bps primary; 20bps severe from A7V-5 evaluator`",
        "- Discovery status: `post-A7V reset diagnostic, not promotion replay`",
        "- Look-ahead/date alignment: `inherits A7X contract; no new feature construction or replay in A7X-4`",
        "- Negative controls: `row_shuffle/time_shuffle/wrong_lag/sign_flip matched controls`",
        "- Decision: `HOLD_RESEARCH`",
        "",
        "## Fast Book Parity",
        "",
        table(parity, max_rows=20),
        "",
        "## Label Summary",
        "",
        table(summary, max_rows=80),
        "",
        "## Failure Mode Matrix",
        "",
        table(matrix, max_rows=20),
        "",
        "## Near-Miss Records",
        "",
        table(near, max_rows=20),
        "",
        "## Control Contamination Detail",
        "",
        table(contamination, max_rows=80),
        "",
        "## Route Scorecard",
        "",
        table(routes, max_rows=20),
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
        "",
        "## Required Next",
        "",
        "- Do not expand A7X-3 or replay old A7V positives.",
        "- Promote A7S-0 data/horizon contract as the primary next stage.",
        "- Keep A7X same-family work limited to objective/weak-prior diagnostics unless new evidence arrives.",
    ]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_stamp()
    labels, wide, parity, a7x3_auth = load_inputs()
    summary = label_summary(labels)
    contamination = control_contamination_detail(labels, wide)
    near = near_miss_records(labels, wide)
    matrix = failure_mode_matrix(labels, contamination, near)
    routes = route_scorecard()

    research_clues = int(labels["a7x3_label"].eq("A7X_RESEARCH_CLUE").sum())
    control_contaminated = int(labels["a7x3_label"].eq("A7X3_HOLD_CONTROL_CONTAMINATED").sum())
    parity_pass = bool(parity.empty or parity.get("parity_pass", pd.Series(dtype=bool)).astype(bool).all())
    blockers = []
    if not parity_pass:
        blockers.append("fast_book_parity_unresolved")
    if research_clues == 0:
        blockers.append("no_clean_research_clue")
    if control_contaminated > 0:
        blockers.append("control_contamination_present")

    decision = "PASS_A7X4_FAILURE_FORENSIC_COMPLETE_SIGNAL_LINE_HOLD"
    authorization = {
        "generated_at": now,
        "decision": decision,
        "blockers": blockers,
        "source_stage": "A7X-3",
        "a7x3_decision": a7x3_auth.get("decision"),
        "candidate_count": int(len(labels)),
        "research_clue_count": research_clues,
        "near_miss_may_stress_fail_count": int(labels["a7x3_label"].eq("A7X3_NEAR_MISS_MAY_STRESS_FAIL").sum()),
        "control_contaminated_candidate_count": control_contaminated,
        "raw_val_recent_fail_count": int(labels["a7x3_label"].eq("A7X3_HOLD_RAW_VAL_RECENT_FAIL").sum()),
        "fast_book_parity_pass": parity_pass,
        "executes_search": False,
        "executes_replay": False,
        "may_policy": "stress_only_failure_attribution_not_ranking_or_generation",
        "authorizes_a7x_same_family_expansion": False,
        "authorizes_a7x_candidate_forensic": False,
        "authorizes_a7s0_data_horizon_contract": True,
        "authorizes_a7t_forward_locked_observation_contract": True,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "required_next": [
            "A7S-0 data/horizon contract as primary next stage",
            "A7T-0 forward-locked observation contract in parallel",
            "Do not expand A7X-3 same-family diagnostic",
        ],
    }

    summary.to_csv(OUT_DIR / "a7x4_label_summary_by_family.csv", index=False)
    contamination.to_csv(OUT_DIR / "a7x4_control_contamination_detail.csv", index=False)
    near.to_csv(OUT_DIR / "a7x4_near_miss_records.csv", index=False)
    matrix.to_csv(OUT_DIR / "a7x4_failure_mode_matrix.csv", index=False)
    routes.to_csv(OUT_DIR / "a7x4_route_scorecard.csv", index=False)
    write_json(OUT_DIR / "a7x4_authorization_matrix.json", authorization)
    write_json(OUT_DIR / "a7x4_manifest.json", {"generated_at": now, "decision": decision, "output_dir": str(OUT_DIR), "report": str(REPORT_PATH)})
    write_report(now, labels, parity, summary, contamination, near, matrix, routes, authorization)
    print(json.dumps({"decision": decision, "blockers": blockers, "authorizes_a7s0": True}, indent=2))


if __name__ == "__main__":
    main()
