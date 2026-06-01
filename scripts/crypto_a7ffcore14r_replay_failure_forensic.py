from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore14r_replay_failure_forensic"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE14R_REPLAY_FAILURE_FORENSIC_20260601.md"
CORE14E = REPO / "runtime" / "a7ffcore14e_bounded_replay" / "a7ffcore14e_manifest.json"
ROWS = REPO / "runtime" / "a7ffcore14e_bounded_replay" / "a7ffcore14e_replay_rows.csv"
CANDIDATES = REPO / "runtime" / "a7ffcore14e_bounded_replay" / "a7ffcore14e_candidate_summary.csv"
FAMILIES = REPO / "runtime" / "a7ffcore14e_bounded_replay" / "a7ffcore14e_family_summary.csv"


CONTROL_COLS = [
    "wrong_lag_future_spread",
    "wrong_lag_stale_spread",
    "time_shuffle_spread",
    "symbol_shuffle_spread",
    "same_family_placebo_spread",
]


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


def dominant_control(row: pd.Series) -> str:
    vals = {col: abs(pd.to_numeric(row.get(col), errors="coerce")) for col in CONTROL_COLS}
    vals = {k: v for k, v in vals.items() if np.isfinite(v)}
    if not vals:
        return "none"
    return max(vals, key=vals.get)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    core14e = read_json(CORE14E)
    if core14e.get("decision") != "HOLD_A7FFCORE14E_BOUNDED_REPLAY_INSUFFICIENT":
        raise SystemExit(f"A7FF-CORE14E is not in HOLD forensic state: {core14e.get('decision')}")

    rows = pd.read_csv(ROWS)
    candidates = pd.read_csv(CANDIDATES)
    families = pd.read_csv(FAMILIES)
    ok = rows[rows["status"].eq("ok")].copy()
    ok["dominant_control"] = ok.apply(dominant_control, axis=1)
    ok["positive"] = pd.to_numeric(ok["cost_adjusted_spread"], errors="coerce").gt(0)
    ok["control_clean"] = pd.to_numeric(ok["control_ratio"], errors="coerce").lt(1.0)
    ok["strict_gate_row"] = ok["split"].isin(["validation", "recent"]) & ok["cost_bps"].eq(5) & ok["positive"] & ok["control_clean"]

    split_gate = (
        ok[ok["cost_bps"].eq(5)]
        .groupby(["split", "semantic_bucket", "motif_bucket"], dropna=False)
        .agg(
            candidate_count=("candidate_id", "nunique"),
            positive_count=("positive", "sum"),
            control_clean_count=("control_clean", "sum"),
            strict_gate_rows=("strict_gate_row", "sum"),
            median_spread=("spread", "median"),
            median_cost_adjusted_spread=("cost_adjusted_spread", "median"),
            median_control_ratio=("control_ratio", "median"),
        )
        .reset_index()
        .sort_values(["strict_gate_rows", "candidate_count"], ascending=[False, False])
    )
    control_summary = (
        ok[ok["cost_bps"].eq(5)]
        .groupby(["dominant_control", "semantic_bucket", "motif_bucket"], dropna=False)
        .agg(
            row_count=("candidate_id", "size"),
            candidate_count=("candidate_id", "nunique"),
            median_control_ratio=("control_ratio", "median"),
            median_cost_adjusted_spread=("cost_adjusted_spread", "median"),
        )
        .reset_index()
        .sort_values(["row_count"], ascending=False)
    )
    sensitivity_rows: list[dict[str, Any]] = []
    for cost in [0, 2, 5, 10]:
        for threshold in [0.8, 1.0, 1.5, 2.0]:
            frame = ok[ok["split"].isin(["validation", "recent"]) & ok["cost_bps"].eq(cost)].copy()
            pass_frame = frame[
                pd.to_numeric(frame["cost_adjusted_spread"], errors="coerce").gt(0)
                & pd.to_numeric(frame["control_ratio"], errors="coerce").lt(threshold)
            ]
            split_counts = pass_frame.groupby("candidate_id")["split"].nunique()
            both = set(split_counts[split_counts >= 2].index.astype(str))
            either = set(split_counts[split_counts >= 1].index.astype(str))
            both_candidates = candidates[candidates["candidate_id"].astype(str).isin(both)]
            sensitivity_rows.append(
                {
                    "cost_bps": cost,
                    "control_ratio_threshold": threshold,
                    "either_validation_or_recent_candidates": len(either),
                    "both_validation_and_recent_candidates": len(both),
                    "both_semantic_count": int(both_candidates["semantic_bucket"].nunique()) if not both_candidates.empty else 0,
                    "both_motif_count": int(both_candidates["motif_bucket"].nunique()) if not both_candidates.empty else 0,
                }
            )
    sensitivity = pd.DataFrame(sensitivity_rows)
    near_miss = candidates[
        (~candidates["replay_clean"].astype(str).str.lower().eq("true"))
        & (pd.to_numeric(candidates["validation_recent_clean_splits"], errors="coerce").fillna(0) >= 1)
    ].copy()
    near_miss = near_miss.sort_values(["validation_recent_clean_splits", "max_tstat"], ascending=[False, False])

    dominant_blocker = "control_and_cost_collapse"
    if int(sensitivity.loc[(sensitivity["cost_bps"].eq(0)) & (sensitivity["control_ratio_threshold"].eq(1.0)), "both_validation_and_recent_candidates"].max()) <= 2:
        dominant_blocker = "split_instability_or_control_dominance_not_cost_only"
    if int(sensitivity["both_validation_and_recent_candidates"].max()) < 24:
        next_allowed = "A7FF-CORE14S replay-packet/objective repair contract"
        decision = "PASS_A7FFCORE14R_FAILURE_ATTRIBUTION_COMPLETE_READY_FOR_CORE14S"
    else:
        next_allowed = "A7FF-CORE14E policy repair rerun contract"
        decision = "PASS_A7FFCORE14R_FAILURE_ATTRIBUTION_COMPLETE_POLICY_REPAIR_POSSIBLE"

    split_gate.to_csv(RUNTIME / "a7ffcore14r_split_gate_summary.csv", index=False)
    control_summary.to_csv(RUNTIME / "a7ffcore14r_control_dominance_summary.csv", index=False)
    sensitivity.to_csv(RUNTIME / "a7ffcore14r_gate_sensitivity.csv", index=False)
    near_miss.to_csv(RUNTIME / "a7ffcore14r_near_miss_candidates.csv", index=False)
    families.to_csv(RUNTIME / "a7ffcore14r_source_family_summary.csv", index=False)
    candidates.to_csv(RUNTIME / "a7ffcore14r_source_candidate_summary.csv", index=False)

    manifest = {
        "stage": "A7FF-CORE14R",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE14E",
        "source_decision": core14e.get("decision"),
        "decision": decision,
        "dominant_blocker": dominant_blocker,
        "source_candidate_count": int(core14e.get("candidate_count", 0)),
        "source_replay_clean_candidate_count": int(core14e.get("replay_clean_candidate_count", 0)),
        "near_miss_candidate_count": int(near_miss["candidate_id"].nunique()) if not near_miss.empty else 0,
        "max_strict_candidates_under_sensitivity": int(sensitivity["both_validation_and_recent_candidates"].max()),
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core14s_contract": decision.endswith("CORE14S"),
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": next_allowed,
    }
    write_json(RUNTIME / "a7ffcore14r_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE14R REPLAY FAILURE FORENSIC",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-CORE14R diagnoses the CORE14E bounded replay collapse. It does not rerun replay, execute formula search, promote candidates, or authorize alpha proof.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Gate Sensitivity",
        "",
        md_table(sensitivity),
        "",
        "## Split Gate Summary",
        "",
        md_table(split_gate),
        "",
        "## Control Dominance Summary",
        "",
        md_table(control_summary),
        "",
        "## Near Miss Candidates",
        "",
        md_table(near_miss, max_rows=60),
        "",
        "## Boundary",
        "",
        "```text",
        "replay rerun: false",
        "formula search / large search: false",
        "promotion: false",
        "alpha proof / shadow / paper / live: false",
        "```",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
