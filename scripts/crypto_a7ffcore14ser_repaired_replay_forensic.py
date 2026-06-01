from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore14ser_repaired_replay_forensic"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE14SER_REPAIRED_REPLAY_FORENSIC_20260601.md"
CORE14SEE = REPO / "runtime" / "a7ffcore14see_sharded_bounded_replay" / "a7ffcore14see_manifest.json"
ROWS = REPO / "runtime" / "a7ffcore14see_sharded_bounded_replay" / "a7ffcore14see_replay_rows.csv"
CANDIDATES = REPO / "runtime" / "a7ffcore14see_sharded_bounded_replay" / "a7ffcore14see_candidate_summary.csv"
CLEAN = REPO / "runtime" / "a7ffcore14see_sharded_bounded_replay" / "a7ffcore14see_replay_clean_candidates.csv"


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
    core14see = read_json(CORE14SEE)
    if core14see.get("decision") != "HOLD_A7FFCORE14SEE_REPAIRED_BOUNDED_REPLAY_INSUFFICIENT_OR_INCOMPLETE":
        raise SystemExit(f"A7FF-CORE14SEE is not in forensic hold state: {core14see.get('decision')}")
    rows = pd.read_csv(ROWS)
    candidates = pd.read_csv(CANDIDATES)
    clean = pd.read_csv(CLEAN) if CLEAN.exists() else pd.DataFrame()

    cost5 = rows[rows["cost_bps"].eq(5)].copy()
    cost5["positive"] = pd.to_numeric(cost5["cost_adjusted_spread"], errors="coerce").gt(0)
    cost5["control_clean"] = pd.to_numeric(cost5["control_ratio"], errors="coerce").lt(1.0)
    split_summary = (
        cost5.groupby(["split", "semantic_bucket", "motif_bucket"], dropna=False)
        .agg(
            candidate_count=("candidate_id", "nunique"),
            positive_rows=("positive", "sum"),
            control_clean_rows=("control_clean", "sum"),
            median_cost_adjusted_spread=("cost_adjusted_spread", "median"),
            median_control_ratio=("control_ratio", "median"),
        )
        .reset_index()
        .sort_values(["positive_rows", "control_clean_rows"], ascending=[False, False])
    )
    family_summary = (
        candidates.groupby(["semantic_bucket", "motif_bucket"], dropna=False)
        .agg(
            candidate_count=("candidate_id", "nunique"),
            clean_candidate_count=("replay_clean", lambda s: int(s.astype(str).str.lower().eq("true").sum())),
            near_miss_count=("validation_recent_clean_splits", lambda s: int(pd.to_numeric(s, errors="coerce").fillna(0).ge(1).sum())),
            median_min_control_ratio=("min_control_ratio", "median"),
            median_cost_adjusted_spread=("median_cost_adjusted_spread", "median"),
            max_tstat=("max_tstat", "max"),
        )
        .reset_index()
        .sort_values(["clean_candidate_count", "near_miss_count", "candidate_count"], ascending=[False, False, False])
    )
    sensitivity_rows: list[dict[str, Any]] = []
    for cost in [0, 2, 5, 10]:
        for ratio in [0.8, 1.0, 1.5, 2.0, 3.0]:
            frame = rows[rows["split"].isin(["validation", "recent"]) & rows["cost_bps"].eq(cost)].copy()
            passed = frame[
                pd.to_numeric(frame["cost_adjusted_spread"], errors="coerce").gt(0)
                & pd.to_numeric(frame["control_ratio"], errors="coerce").lt(ratio)
            ]
            split_counts = passed.groupby("candidate_id")["split"].nunique()
            both = set(split_counts[split_counts >= 2].index.astype(str))
            both_frame = candidates[candidates["candidate_id"].astype(str).isin(both)]
            sensitivity_rows.append(
                {
                    "cost_bps": cost,
                    "control_ratio_threshold": ratio,
                    "both_validation_recent_candidates": len(both),
                    "semantic_count": int(both_frame["semantic_bucket"].nunique()) if not both_frame.empty else 0,
                    "motif_count": int(both_frame["motif_bucket"].nunique()) if not both_frame.empty else 0,
                }
            )
    sensitivity = pd.DataFrame(sensitivity_rows)

    clean_family_concentration = 1.0
    if not clean.empty and "semantic_bucket" in clean.columns:
        clean_family_concentration = float(clean["semantic_bucket"].value_counts(normalize=True).max())
    dominant_failure = "repaired_packet_replay_collapse"
    if int(core14see.get("replay_clean_candidate_count", 0)) <= 1:
        dominant_failure = "objective_surface_not_replay_stable"

    split_summary.to_csv(RUNTIME / "a7ffcore14ser_split_summary.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ffcore14ser_family_summary.csv", index=False)
    sensitivity.to_csv(RUNTIME / "a7ffcore14ser_gate_sensitivity.csv", index=False)
    candidates.to_csv(RUNTIME / "a7ffcore14ser_candidate_summary.csv", index=False)
    clean.to_csv(RUNTIME / "a7ffcore14ser_clean_candidates.csv", index=False)

    decision = "PASS_A7FFCORE14SER_REPAIRED_REPLAY_FORENSIC_COMPLETE_STOP_REPLAY_EXPANSION"
    manifest = {
        "stage": "A7FF-CORE14SER",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE14SEE",
        "source_decision": core14see.get("decision"),
        "decision": decision,
        "dominant_failure": dominant_failure,
        "completed_shard_count": int(core14see.get("completed_shard_count", 0)),
        "candidate_count": int(core14see.get("candidate_count", 0)),
        "clean_candidate_count": int(core14see.get("replay_clean_candidate_count", 0)),
        "clean_semantic_bucket_count": int(core14see.get("replay_clean_semantic_bucket_count", 0)),
        "clean_motif_bucket_count": int(core14see.get("replay_clean_motif_bucket_count", 0)),
        "clean_family_concentration": clean_family_concentration,
        "max_candidates_under_relaxed_sensitivity": int(sensitivity["both_validation_recent_candidates"].max()),
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core15_contract": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE15X objective-surface reset / replay-stability repair contract",
    }
    write_json(RUNTIME / "a7ffcore14ser_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE14SER REPAIRED REPLAY FORENSIC",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-CORE14SER freezes the repaired-packet bounded replay result. It does not authorize CORE15, formula search, large search, alpha proof, shadow, paper, or live.",
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
        "## Family Summary",
        "",
        md_table(family_summary),
        "",
        "## Split Summary",
        "",
        md_table(split_summary),
        "",
        "## Clean Candidates",
        "",
        md_table(clean),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
