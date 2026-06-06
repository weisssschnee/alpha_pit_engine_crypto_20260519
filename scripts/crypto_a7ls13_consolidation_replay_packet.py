from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
A7LS12 = REPO / "runtime" / "a7ls12_company_result_aggregate"
RUNTIME = REPO / "runtime" / "a7ls13_consolidation_replay_packet"
REPORT = REPO / "reports" / "CRYPTO_A7LS13_CONSOLIDATION_REPLAY_PACKET_20260606.md"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "<none>"
    return df.head(max_rows).to_markdown(index=False)


def joined_unique(series: pd.Series) -> str:
    values = sorted({str(x) for x in series.dropna() if str(x) and str(x) != "nan"})
    return ";".join(values)


def build() -> dict:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    manifest12 = json.loads((A7LS12 / "a7ls12_aggregate_manifest.json").read_text(encoding="utf-8"))
    clues = pd.read_csv(A7LS12 / "a7ls12_non_l7_numeric_clues.csv")
    shortlist = pd.read_csv(A7LS12 / "a7ls12_non_l7_shortlist.csv")
    if clues.empty:
        raise RuntimeError("A7LS12 non-L7 clue table is empty")

    for df in (clues, shortlist):
        for col in [
            "control_ratio_premay_max",
            "robust_min_tstat_floor",
            "robust_median_tstat_floor",
            "one_bar_lag_recent_oriented",
            "cost10_recent_oriented",
            "deep_audit_score",
            "label_horizon_h",
        ]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

    group_cols = ["blueprint_id", "expression"]
    agg = (
        clues.groupby(group_cols, dropna=False)
        .agg(
            clue_rows=("blueprint_id", "count"),
            label_family_count=("label_family", "nunique"),
            label_families=("label_family", joined_unique),
            horizon_count=("label_horizon_h", "nunique"),
            horizons=("label_horizon_h", lambda s: ";".join(map(str, sorted(pd.to_numeric(s, errors="coerce").dropna().astype(int).unique())))),
            source_info_axis=("source_info_axis", "first"),
            next_wave_family=("next_wave_family", "first"),
            semantic_pair=("semantic_pair", "first"),
            motif=("motif", "first"),
            skeleton_key=("skeleton_key", "first"),
            production_key=("production_key", "first"),
            min_control_ratio=("control_ratio_premay_max", "min"),
            median_control_ratio=("control_ratio_premay_max", "median"),
            max_robust_min_tstat=("robust_min_tstat_floor", "max"),
            median_robust_min_tstat=("robust_min_tstat_floor", "median"),
            max_lag_recent=("one_bar_lag_recent_oriented", "max"),
            max_cost10_recent=("cost10_recent_oriented", "max"),
        )
        .reset_index()
    )
    # Merge best shortlist score where available.
    if "deep_audit_score" in shortlist.columns and not shortlist.empty:
        score = shortlist.groupby("blueprint_id", dropna=False)["deep_audit_score"].max().reset_index(name="shortlist_best_score")
        agg = agg.merge(score, on="blueprint_id", how="left")
    else:
        agg["shortlist_best_score"] = 0.0
    agg["shortlist_best_score"] = pd.to_numeric(agg["shortlist_best_score"], errors="coerce").fillna(0.0)
    agg["candidate_score"] = (
        agg["label_family_count"].fillna(0) * 100.0
        + agg["horizon_count"].fillna(0) * 20.0
        + (1.0 - agg["min_control_ratio"].clip(upper=1.0)).fillna(0.0) * 100.0
        + agg["max_robust_min_tstat"].clip(lower=0).fillna(0.0) * 10.0
        + agg["max_lag_recent"].clip(lower=0).fillna(0.0) * 100.0
        + agg["max_cost10_recent"].clip(lower=0).fillna(0.0) * 100.0
        + agg["shortlist_best_score"].clip(lower=0).fillna(0.0) * 0.1
    )
    agg["consolidation_status"] = "candidate_level_clue"
    agg.loc[(agg["label_family_count"] >= 2) & (agg["min_control_ratio"] < 0.8), "consolidation_status"] = "multi_label_control_clean"
    agg.loc[(agg["label_family_count"] >= 3) & (agg["min_control_ratio"] < 0.7), "consolidation_status"] = "priority_multi_label"

    agg = agg.sort_values(["candidate_score", "blueprint_id"], ascending=[False, True])

    selected_rows = []
    axis_cap: dict[str, int] = {}
    family_cap: dict[str, int] = {}
    skeleton_cap: dict[str, int] = {}
    label_bundle_cap: dict[str, int] = {}
    for row in agg.to_dict("records"):
        axis = str(row.get("source_info_axis", ""))
        family = str(row.get("next_wave_family", ""))
        skeleton = str(row.get("skeleton_key", ""))
        labels = str(row.get("label_families", ""))
        if axis_cap.get(axis, 0) >= 18:
            continue
        if family_cap.get(family, 0) >= 16:
            continue
        if skeleton_cap.get(skeleton, 0) >= 2:
            continue
        if label_bundle_cap.get(labels, 0) >= 10:
            continue
        selected_rows.append(row)
        axis_cap[axis] = axis_cap.get(axis, 0) + 1
        family_cap[family] = family_cap.get(family, 0) + 1
        skeleton_cap[skeleton] = skeleton_cap.get(skeleton, 0) + 1
        label_bundle_cap[labels] = label_bundle_cap.get(labels, 0) + 1
        if len(selected_rows) >= 48:
            break
    replay_packet = pd.DataFrame(selected_rows)
    replay_packet["a7ls13_packet_rank"] = range(1, len(replay_packet) + 1)
    replay_packet["a7ls13_packet_role"] = "consolidated_replay_candidate"

    axis_summary = replay_packet.groupby("source_info_axis").size().reset_index(name="packet_rows") if not replay_packet.empty else pd.DataFrame()
    family_summary = replay_packet.groupby("next_wave_family").size().reset_index(name="packet_rows") if not replay_packet.empty else pd.DataFrame()
    status_summary = agg.groupby("consolidation_status").size().reset_index(name="candidate_rows")
    label_bundle_summary = replay_packet.groupby("label_families").size().reset_index(name="packet_rows") if not replay_packet.empty else pd.DataFrame()

    blocked = pd.DataFrame(
        [
            {"blocked_task": "new_formula_generation", "reason": "A7LS13 consolidates existing A7LS12 clues only"},
            {"blocked_task": "large_search", "reason": "deep audit clues are not replay proof"},
            {"blocked_task": "alpha_proof_shadow_paper_live", "reason": "no live-forward or portfolio proof"},
        ]
    )

    outputs = {
        "a7ls13_candidate_consolidation.csv": agg,
        "a7ls13_replay_packet.csv": replay_packet,
        "a7ls13_packet_by_source_axis.csv": axis_summary,
        "a7ls13_packet_by_next_wave_family.csv": family_summary,
        "a7ls13_consolidation_status_summary.csv": status_summary,
        "a7ls13_packet_by_label_bundle.csv": label_bundle_summary,
        "a7ls13_blocked_next_tasks.csv": blocked,
    }
    for name, df in outputs.items():
        df.to_csv(RUNTIME / name, index=False)

    manifest = {
        "stage": "A7LS-13",
        "decision": "PASS_A7LS13_CONSOLIDATED_REPLAY_PACKET_READY_NO_SEARCH_AUTH",
        "generated_at": now_iso(),
        "input_decision": manifest12.get("decision"),
        "input_non_l7_clue_rows": int(len(clues)),
        "candidate_level_rows": int(len(agg)),
        "priority_multi_label_rows": int((agg["consolidation_status"] == "priority_multi_label").sum()),
        "multi_label_control_clean_rows": int((agg["consolidation_status"] == "multi_label_control_clean").sum()),
        "replay_packet_rows": int(len(replay_packet)),
        "packet_source_axis_count": int(replay_packet["source_info_axis"].nunique()) if not replay_packet.empty else 0,
        "packet_next_wave_family_count": int(replay_packet["next_wave_family"].nunique()) if not replay_packet.empty else 0,
        "packet_label_bundle_count": int(replay_packet["label_families"].nunique()) if not replay_packet.empty else 0,
        "uses_may": False,
        "executes_search": False,
        "authorizes_a7ls14_replay_contract": True,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "blockers": [],
    }
    (RUNTIME / "a7ls13_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    report = [
        "# CRYPTO A7LS-13 CONSOLIDATION REPLAY PACKET",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "## Summary",
        "",
        f"- input_non_l7_clue_rows: {manifest['input_non_l7_clue_rows']}",
        f"- candidate_level_rows: {manifest['candidate_level_rows']}",
        f"- priority_multi_label_rows: {manifest['priority_multi_label_rows']}",
        f"- multi_label_control_clean_rows: {manifest['multi_label_control_clean_rows']}",
        f"- replay_packet_rows: {manifest['replay_packet_rows']}",
        f"- packet_source_axis_count: {manifest['packet_source_axis_count']}",
        f"- packet_next_wave_family_count: {manifest['packet_next_wave_family_count']}",
        f"- packet_label_bundle_count: {manifest['packet_label_bundle_count']}",
        "",
        "A7LS-13 consolidates full-timestamp A7LS-12 non-L7 clue rows to candidate-level replay packets. It removes duplicate label/horizon rows from the same formula and applies axis/family/skeleton caps.",
        "",
        "## Consolidation Status",
        "",
        md_table(status_summary),
        "",
        "## Packet By Source Axis",
        "",
        md_table(axis_summary),
        "",
        "## Packet By Next Wave Family",
        "",
        md_table(family_summary),
        "",
        "## Packet By Label Bundle",
        "",
        md_table(label_bundle_summary),
        "",
        "## Top Replay Packet",
        "",
        md_table(replay_packet[["a7ls13_packet_rank", "blueprint_id", "source_info_axis", "next_wave_family", "label_families", "horizons", "min_control_ratio", "candidate_score"]], 40),
        "",
        "## Authorization",
        "",
        "- A7LS-14 replay contract: authorized",
        "- new generation / large search / alpha proof / shadow / paper / live: not authorized",
        "",
    ]
    REPORT.write_text("\n".join(report), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    print(json.dumps(build(), indent=2, sort_keys=True))
