from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore15y_replay_stability_surface"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE15Y_REPLAY_STABILITY_SURFACE_20260601.md"
CORE15X = REPO / "runtime" / "a7ffcore15x_objective_surface_reset_contract" / "a7ffcore15x_manifest.json"
CORE13E_CLUES = REPO / "runtime" / "a7ffcore13e_numeric_response" / "a7ffcore13e_numeric_clues.csv"
CORE14E_ROWS = REPO / "runtime" / "a7ffcore14e_bounded_replay" / "a7ffcore14e_replay_rows.csv"
CORE14SEE_ROWS = REPO / "runtime" / "a7ffcore14see_sharded_bounded_replay" / "a7ffcore14see_replay_rows.csv"


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


def replay_surface(rows: pd.DataFrame, source: str) -> pd.DataFrame:
    rows = rows[rows["status"].eq("ok")].copy()
    rows["positive_cost5"] = rows["cost_bps"].eq(5) & pd.to_numeric(rows["cost_adjusted_spread"], errors="coerce").gt(0)
    rows["control_clean"] = pd.to_numeric(rows.get("control_ratio", rows.get("wrong_lag_control_ratio")), errors="coerce").lt(1.0)
    rows["strict_row"] = rows["positive_cost5"] & rows["control_clean"]
    split = (
        rows[rows["cost_bps"].eq(5)]
        .groupby(["candidate_id", "semantic_bucket", "motif_bucket", "split"], dropna=False)
        .agg(
            positive=("positive_cost5", "max"),
            control_clean=("control_clean", "max"),
            strict=("strict_row", "max"),
            median_cost_adjusted_spread=("cost_adjusted_spread", "median"),
            median_control_ratio=("control_ratio" if "control_ratio" in rows.columns else "wrong_lag_control_ratio", "median"),
            max_tstat=("tstat", "max"),
        )
        .reset_index()
    )
    pivot = split.pivot_table(
        index=["candidate_id", "semantic_bucket", "motif_bucket"],
        columns="split",
        values=["positive", "control_clean", "strict"],
        aggfunc="max",
        fill_value=False,
    )
    pivot.columns = [f"{a}_{b}" for a, b in pivot.columns]
    pivot = pivot.reset_index()
    agg = (
        split.groupby(["candidate_id", "semantic_bucket", "motif_bucket"], dropna=False)
        .agg(
            split_count=("split", "nunique"),
            strict_split_count=("strict", "sum"),
            positive_split_count=("positive", "sum"),
            control_clean_split_count=("control_clean", "sum"),
            median_cost_adjusted_spread=("median_cost_adjusted_spread", "median"),
            median_control_ratio=("median_control_ratio", "median"),
            max_tstat=("max_tstat", "max"),
        )
        .reset_index()
    )
    out = agg.merge(pivot, on=["candidate_id", "semantic_bucket", "motif_bucket"], how="left")
    out["source"] = source
    out["split_stable_proxy"] = (
        out["strict_split_count"].ge(2)
        | (out["positive_split_count"].ge(2) & out["control_clean_split_count"].ge(2) & pd.to_numeric(out["median_control_ratio"], errors="coerce").lt(1.25))
    )
    out["surface_score"] = (
        out["strict_split_count"] * 4.0
        + out["positive_split_count"] * 1.5
        + out["control_clean_split_count"] * 1.5
        + pd.to_numeric(out["max_tstat"], errors="coerce").fillna(0).clip(upper=5)
        - pd.to_numeric(out["median_control_ratio"], errors="coerce").fillna(10).clip(upper=10)
    )
    return out


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    core15x = read_json(CORE15X)
    if core15x.get("decision") != "PASS_A7FFCORE15X_OBJECTIVE_SURFACE_RESET_CONTRACT_READY_FOR_CORE15Y":
        raise SystemExit(f"A7FF-CORE15X is not ready: {core15x.get('decision')}")

    core14e_surface = replay_surface(pd.read_csv(CORE14E_ROWS), "core14e_original_packet")
    core14see_surface = replay_surface(pd.read_csv(CORE14SEE_ROWS), "core14see_repaired_packet")
    combined = pd.concat([core14e_surface, core14see_surface], ignore_index=True)
    clues = pd.read_csv(CORE13E_CLUES)
    clue_summary = (
        clues[clues["numeric_clue"].astype(bool)]
        .groupby(["candidate_id", "semantic_bucket", "motif_bucket"], dropna=False)
        .agg(
            numeric_clue_rows=("candidate_id", "size"),
            numeric_label_count=("label_id", "nunique"),
            numeric_horizon_count=("horizon", "nunique"),
            numeric_min_control_ratio=("control_ratio", "min"),
            numeric_best_original_score=("original_score", "max"),
        )
        .reset_index()
    )
    surface = combined.merge(clue_summary, on=["candidate_id", "semantic_bucket", "motif_bucket"], how="left")
    surface["numeric_clue_rows"] = surface["numeric_clue_rows"].fillna(0).astype(int)
    surface["objective_surface_candidate"] = (
        surface["split_stable_proxy"]
        & pd.to_numeric(surface["median_control_ratio"], errors="coerce").lt(1.25)
        & surface["numeric_clue_rows"].gt(0)
    )
    family = (
        surface.groupby(["source", "semantic_bucket", "motif_bucket"], dropna=False)
        .agg(
            candidate_count=("candidate_id", "nunique"),
            surface_candidate_count=("objective_surface_candidate", "sum"),
            median_surface_score=("surface_score", "median"),
            median_control_ratio=("median_control_ratio", "median"),
            median_cost_adjusted_spread=("median_cost_adjusted_spread", "median"),
        )
        .reset_index()
        .sort_values(["surface_candidate_count", "candidate_count"], ascending=[False, False])
    )
    candidates = surface[surface["objective_surface_candidate"]].copy().sort_values("surface_score", ascending=False)
    candidate_count = int(candidates["candidate_id"].nunique())
    semantic_count = int(candidates["semantic_bucket"].nunique()) if not candidates.empty else 0
    motif_count = int(candidates["motif_bucket"].nunique()) if not candidates.empty else 0
    top_family_share = 1.0
    if not candidates.empty:
        top_family_share = float(candidates.groupby(["semantic_bucket", "motif_bucket"])["candidate_id"].nunique().max() / max(candidate_count, 1))
    blockers = []
    if candidate_count < 32:
        blockers.append("surface_candidate_count_lt_32")
    if semantic_count < 5:
        blockers.append("semantic_bucket_count_lt_5")
    if motif_count < 4:
        blockers.append("motif_bucket_count_lt_4")
    if top_family_share > 0.35:
        blockers.append("top_family_share_gt_35pct")
    decision = (
        "PASS_A7FFCORE15Y_REPLAY_STABILITY_SURFACE_READY_FOR_CORE15Z"
        if not blockers
        else "HOLD_A7FFCORE15Y_REPLAY_STABILITY_SURFACE_INSUFFICIENT"
    )

    surface.to_csv(RUNTIME / "a7ffcore15y_candidate_surface_matrix.csv", index=False)
    candidates.to_csv(RUNTIME / "a7ffcore15y_surface_candidates.csv", index=False)
    family.to_csv(RUNTIME / "a7ffcore15y_family_scorecard.csv", index=False)
    manifest = {
        "stage": "A7FF-CORE15Y",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE15X",
        "source_decision": core15x.get("decision"),
        "decision": decision,
        "blockers": blockers,
        "surface_row_count": int(surface.shape[0]),
        "surface_candidate_count": candidate_count,
        "surface_semantic_bucket_count": semantic_count,
        "surface_motif_bucket_count": motif_count,
        "top_family_share": top_family_share,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core15z": decision.startswith("PASS_"),
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE15Z objective-surface seed policy" if decision.startswith("PASS_") else "A7FF-CORE15YR objective-surface failure repair",
    }
    write_json(RUNTIME / "a7ffcore15y_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE15Y REPLAY-STABILITY OBJECTIVE SURFACE",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-CORE15Y builds a replay-stability objective surface from existing numeric/replay/forensic rows. It does not execute replay, formula generation, search, promotion, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Family Scorecard",
        "",
        md_table(family),
        "",
        "## Surface Candidates",
        "",
        md_table(candidates, max_rows=80),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
