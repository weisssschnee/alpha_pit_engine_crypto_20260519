from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore16_primitive_replay_stability_atlas"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE16_PRIMITIVE_REPLAY_STABILITY_ATLAS_20260601.md"
CORE15YR = REPO / "runtime" / "a7ffcore15yr_surface_failure_repair" / "a7ffcore15yr_manifest.json"
A7AA1 = REPO / "runtime" / "a7aa1_primitive_response_map" / "a7aa1_primitive_response_map.csv"
A7AA2 = REPO / "runtime" / "a7aa2_feature_role_classification" / "a7aa2_feature_role_ledger.csv"
CORE15Y_SURFACE = REPO / "runtime" / "a7ffcore15y_replay_stability_surface" / "a7ffcore15y_candidate_surface_matrix.csv"


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
    core15yr = read_json(CORE15YR)
    if core15yr.get("decision") != "PASS_A7FFCORE15YR_SURFACE_FAILURE_REPAIR_READY_FOR_CORE16_ATLAS":
        raise SystemExit(f"A7FF-CORE15YR is not ready: {core15yr.get('decision')}")

    aa1 = pd.read_csv(A7AA1)
    roles = pd.read_csv(A7AA2)
    surface = pd.read_csv(CORE15Y_SURFACE)

    aa1["control_ratio_premay_max"] = pd.to_numeric(aa1["control_ratio_premay_max"], errors="coerce")
    aa1["lag_ok_bool"] = aa1["lag_ok"].astype(str).str.lower().eq("true")
    aa1["premay_all_positive_bool"] = aa1["premay_all_positive"].astype(str).str.lower().eq("true")
    aa1["strict_primitive"] = aa1["decision"].eq("A7AA1_PRIMITIVE_RESPONSE_CANDIDATE")
    aa1["relaxed_primitive"] = aa1["premay_all_positive_bool"] & aa1["control_ratio_premay_max"].lt(1.0)
    aa1["non_l7"] = ~aa1["label_family"].astype(str).eq("L7_ranked_future_return")
    aa1["atlas_candidate"] = aa1["relaxed_primitive"] & aa1["lag_ok_bool"] & aa1["non_l7"]

    atlas = aa1[aa1["atlas_candidate"]].copy()
    atlas["objective_id"] = (
        "core16_"
        + atlas["field_family"].astype(str)
        + "_"
        + atlas["field_name"].astype(str)
        + "_"
        + atlas["transform"].astype(str)
        + "_"
        + atlas["label_family"].astype(str)
        + "_h"
        + atlas["label_horizon_h"].astype(str)
    )
    family = (
        aa1.groupby(["field_family", "label_family"], dropna=False)
        .agg(
            rows=("field_name", "size"),
            strict_primitive_count=("strict_primitive", "sum"),
            relaxed_primitive_count=("relaxed_primitive", "sum"),
            atlas_candidate_count=("atlas_candidate", "sum"),
            median_control_ratio=("control_ratio_premay_max", "median"),
        )
        .reset_index()
        .sort_values(["atlas_candidate_count", "relaxed_primitive_count"], ascending=[False, False])
    )
    role_summary = (
        roles.groupby(["field_family", "final_role"], dropna=False)
        .agg(field_count=("field_name", "nunique"))
        .reset_index()
        if {"field_family", "final_role", "field_name"}.issubset(roles.columns)
        else pd.DataFrame()
    )
    surface_family = (
        surface.groupby(["semantic_bucket", "motif_bucket"], dropna=False)
        .agg(
            surface_rows=("candidate_id", "nunique"),
            surface_candidates=("objective_surface_candidate", "sum"),
            median_surface_score=("surface_score", "median"),
            median_control_ratio=("median_control_ratio", "median"),
        )
        .reset_index()
        .sort_values(["surface_candidates", "surface_rows"], ascending=[False, False])
    )
    candidate_count = int(atlas["objective_id"].nunique())
    family_count = int(atlas["field_family"].nunique()) if not atlas.empty else 0
    transform_count = int(atlas["transform"].nunique()) if not atlas.empty else 0
    top_family_share = 1.0
    if not atlas.empty:
        top_family_share = float(atlas["field_family"].value_counts(normalize=True).max())
    blockers = []
    if candidate_count < 64:
        blockers.append("atlas_candidate_count_lt_64")
    if family_count < 6:
        blockers.append("field_family_count_lt_6")
    if transform_count < 5:
        blockers.append("transform_count_lt_5")
    if top_family_share > 0.30:
        blockers.append("top_family_share_gt_30pct")
    decision = (
        "PASS_A7FFCORE16_PRIMITIVE_REPLAY_STABILITY_ATLAS_READY_FOR_CORE17"
        if not blockers
        else "HOLD_A7FFCORE16_PRIMITIVE_ATLAS_INSUFFICIENT"
    )

    atlas.to_csv(RUNTIME / "a7ffcore16_candidate_objective_atlas.csv", index=False)
    family.to_csv(RUNTIME / "a7ffcore16_field_type_by_label_horizon_stability.csv", index=False)
    role_summary.to_csv(RUNTIME / "a7ffcore16_role_summary.csv", index=False)
    surface_family.to_csv(RUNTIME / "a7ffcore16_replay_surface_family_map.csv", index=False)
    manifest = {
        "stage": "A7FF-CORE16",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE15YR",
        "source_decision": core15yr.get("decision"),
        "decision": decision,
        "blockers": blockers,
        "atlas_candidate_count": candidate_count,
        "field_family_count": family_count,
        "transform_count": transform_count,
        "top_family_share": top_family_share,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core17": decision.startswith("PASS_"),
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE17 objective atlas seed policy" if decision.startswith("PASS_") else "A7FF-CORE16R primitive atlas supply repair",
    }
    write_json(RUNTIME / "a7ffcore16_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE16 PRIMITIVE REPLAY-STABILITY ATLAS",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-CORE16 rebuilds an objective atlas from primitive response and replay-stability evidence. It does not execute replay, formula generation, search, promotion, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Field Type By Label/Horizon Stability",
        "",
        md_table(family),
        "",
        "## Candidate Objective Atlas",
        "",
        md_table(atlas, max_rows=80),
        "",
        "## Replay Surface Family Map",
        "",
        md_table(surface_family),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
