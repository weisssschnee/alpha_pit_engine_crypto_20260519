from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
A7LS10 = REPO / "runtime" / "a7ls10_company_result_aggregate"
RUNTIME = REPO / "runtime" / "a7ls11_promotion_and_missing_field_repair"
REPORT = REPO / "reports" / "CRYPTO_A7LS11_PROMOTION_AND_MISSING_FIELD_REPAIR_20260606.md"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_csv(name: str) -> pd.DataFrame:
    path = A7LS10 / name
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def to_bool(s: pd.Series) -> pd.Series:
    return s.astype(str).str.lower().isin(["true", "1", "yes"])


def numeric(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = df.copy()
    for col in cols:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def table(df: pd.DataFrame) -> str:
    if df.empty:
        return "<none>"
    return df.to_markdown(index=False)


def build() -> dict:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    manifest10 = json.loads((A7LS10 / "a7ls10_aggregate_manifest.json").read_text(encoding="utf-8"))
    clues = read_csv("a7ls10_non_l7_numeric_clues.csv")
    shortlist = read_csv("a7ls10_non_l7_shortlist.csv")
    shard_summary = read_csv("a7ls10_shard_manifest_summary.csv")
    rank_diag = read_csv("a7ls10_rank_label_diagnostic_clues.csv")

    score_cols = [
        "control_ratio_premay_max",
        "deep_followup_score",
        "robust_median_tstat_floor",
        "robust_min_tstat_floor",
        "one_bar_lag_recent_oriented",
        "cost10_recent_oriented",
        "avg_n_obs_recent",
        "label_horizon_h",
    ]
    clues = numeric(clues, score_cols)
    shortlist = numeric(shortlist, score_cols)
    for df in (clues, shortlist):
        if "premay_all_positive" in df.columns:
            df["premay_all_positive_bool"] = to_bool(df["premay_all_positive"])
        if "lag_ok" in df.columns:
            df["lag_ok_bool"] = to_bool(df["lag_ok"])
        if "robust_ok" in df.columns:
            df["robust_ok_bool"] = to_bool(df["robust_ok"])
        if "deep_followup_score" not in df.columns:
            df["deep_followup_score"] = (
                (1.0 - pd.to_numeric(df.get("control_ratio_premay_max", 1.0), errors="coerce").fillna(1.0)).clip(lower=0)
                * 1000.0
                + pd.to_numeric(df.get("robust_median_tstat_floor", 0.0), errors="coerce").fillna(0.0).clip(lower=0)
                * 100.0
                + pd.to_numeric(df.get("one_bar_lag_recent_oriented", 0.0), errors="coerce").fillna(0.0).clip(lower=0)
                * 10.0
            )

    eligible = clues[
        (clues["label_family"].isin(
            [
                "L0_raw_forward_return",
                "L1_cross_sectional_relative_return",
                "L3_liquidity_tier_relative_return",
                "L5_vol_adjusted_return",
            ]
        ))
        & (clues["premay_all_positive_bool"])
        & (clues["lag_ok_bool"])
        & (clues["robust_ok_bool"])
        & (clues["control_ratio_premay_max"] < 0.80)
    ].copy()

    eligible["promotion_lane"] = "A7LS11_DEEP_AUDIT_CANDIDATE"
    elite_mask = (
        (eligible["control_ratio_premay_max"] < 0.65)
        & (eligible["robust_median_tstat_floor"].fillna(0) >= 1.0)
        & (eligible["avg_n_obs_recent"].fillna(0) >= 90)
    )
    eligible.loc[elite_mask, "promotion_lane"] = "A7LS11_PRIORITY_DEEP_AUDIT"

    eligible = eligible.sort_values(
        ["promotion_lane", "deep_followup_score", "control_ratio_premay_max"],
        ascending=[False, False, True],
        na_position="last",
    )

    # Queue policy: keep all eligible rows, but cap the immediate deep-audit queue by
    # semantic pair, family, and skeleton so the next run does not collapse into one motif.
    deep_rows = []
    pair_cap: dict[str, int] = {}
    family_cap: dict[str, int] = {}
    skeleton_cap: dict[str, int] = {}
    for row in eligible.to_dict("records"):
        pair = str(row.get("semantic_pair", ""))
        fam = str(row.get("next_wave_family", ""))
        skel = str(row.get("skeleton_key", ""))
        if pair_cap.get(pair, 0) >= 12:
            continue
        if family_cap.get(fam, 0) >= 32:
            continue
        if skeleton_cap.get(skel, 0) >= 4:
            continue
        deep_rows.append(row)
        pair_cap[pair] = pair_cap.get(pair, 0) + 1
        family_cap[fam] = family_cap.get(fam, 0) + 1
        skeleton_cap[skel] = skeleton_cap.get(skel, 0) + 1
        if len(deep_rows) >= 160:
            break
    deep_queue = pd.DataFrame(deep_rows)

    # A broader next-wave queue keeps larger scale while marking execution class.
    next_wave = eligible.copy()
    next_wave["execution_class"] = "deep_audit_backlog"
    if not deep_queue.empty:
        next_wave.loc[next_wave["blueprint_id"].isin(deep_queue["blueprint_id"]), "execution_class"] = "immediate_deep_audit"

    missing_rows = []
    missing_shards = shard_summary[shard_summary["missing_numeric_fields"].fillna("").astype(str).str.len() > 0]
    for _, row in missing_shards.iterrows():
        fields = [x.strip() for x in str(row["missing_numeric_fields"]).split(";") if x.strip()]
        for field in fields:
            if field == "quote_volume":
                repair_action = "alias_to_trade_quote_volume"
                replacement = "trade_quote_volume"
                status = "REPAIR_READY_ALIAS_EXISTS_IN_UNIVERSE498_V2"
            else:
                repair_action = "manual_contract_review_required"
                replacement = ""
                status = "HOLD_UNKNOWN_FIELD"
            missing_rows.append(
                {
                    "shard": row.get("shard", ""),
                    "missing_field": field,
                    "repair_action": repair_action,
                    "replacement_field": replacement,
                    "status": status,
                    "blocked_input_blueprint_count": row.get("input_blueprint_count", ""),
                    "blocked_reason": row.get("blockers", ""),
                }
            )
    missing_repair = pd.DataFrame(missing_rows)

    family_summary = (
        clues.groupby(["source_info_axis", "next_wave_family", "label_family"], dropna=False)
        .size()
        .reset_index(name="non_l7_clue_rows")
        .sort_values("non_l7_clue_rows", ascending=False)
    )
    eligible_summary = (
        eligible.groupby(["source_info_axis", "next_wave_family"], dropna=False)
        .agg(
            eligible_rows=("blueprint_id", "count"),
            median_control_ratio=("control_ratio_premay_max", "median"),
            max_deep_followup_score=("deep_followup_score", "max"),
            unique_skeletons=("skeleton_key", "nunique"),
            unique_semantic_pairs=("semantic_pair", "nunique"),
        )
        .reset_index()
        .sort_values(["eligible_rows", "max_deep_followup_score"], ascending=[False, False])
    )
    label_summary = clues.groupby("label_family").size().reset_index(name="non_l7_clue_rows")
    rank_label_summary = rank_diag.groupby("label_family").size().reset_index(name="rank_label_rows") if not rank_diag.empty else pd.DataFrame()

    blocked_next = pd.DataFrame(
        [
            {
                "blocked_task": "large_search",
                "reason": "A7LS10 is numeric clue aggregation, not replay or alpha proof",
            },
            {
                "blocked_task": "alpha_proof_shadow_paper_live",
                "reason": "no portfolio/deep replay authorization and no live-forward proof",
            },
            {
                "blocked_task": "reuse_quote_volume_without_alias",
                "reason": "quote_volume is not in universe498 v2; use trade_quote_volume alias or block",
            },
            {
                "blocked_task": "rank_label_only_promotion",
                "reason": "ranked label diagnostics remain separate from non-L7 promotion",
            },
        ]
    )

    outputs = {
        "a7ls11_all_eligible_non_l7_promotion_queue.csv": eligible,
        "a7ls11_immediate_deep_audit_queue.csv": deep_queue,
        "a7ls11_next_wave_family_summary.csv": family_summary,
        "a7ls11_eligible_family_summary.csv": eligible_summary,
        "a7ls11_missing_field_repair_plan.csv": missing_repair,
        "a7ls11_label_summary.csv": label_summary,
        "a7ls11_rank_label_diagnostic_summary.csv": rank_label_summary,
        "a7ls11_blocked_next_tasks.csv": blocked_next,
    }
    for name, df in outputs.items():
        df.to_csv(RUNTIME / name, index=False)

    manifest = {
        "stage": "A7LS-11",
        "decision": "PASS_A7LS11_PROMOTION_AND_FIELD_REPAIR_READY_NO_SEARCH_AUTH",
        "generated_at": now_iso(),
        "input_stage": manifest10.get("stage"),
        "input_decision": manifest10.get("decision"),
        "input_non_l7_numeric_clue_rows": int(len(clues)),
        "eligible_non_l7_promotion_rows": int(len(eligible)),
        "immediate_deep_audit_rows": int(len(deep_queue)),
        "eligible_source_info_axis_count": int(eligible["source_info_axis"].nunique()) if not eligible.empty else 0,
        "eligible_next_wave_family_count": int(eligible["next_wave_family"].nunique()) if not eligible.empty else 0,
        "missing_field_repair_rows": int(len(missing_repair)),
        "quote_volume_alias_repair_ready": bool(
            (missing_repair.get("status", pd.Series(dtype=str)) == "REPAIR_READY_ALIAS_EXISTS_IN_UNIVERSE498_V2").any()
        ),
        "uses_may": False,
        "executes_numeric_probe": False,
        "executes_search": False,
        "authorizes_a7ls12_deep_audit_contract": True,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "blockers": [],
    }
    (RUNTIME / "a7ls11_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "# CRYPTO A7LS-11 PROMOTION AND MISSING FIELD REPAIR",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "## Summary",
        "",
        f"- input_non_l7_numeric_clue_rows: {manifest['input_non_l7_numeric_clue_rows']}",
        f"- eligible_non_l7_promotion_rows: {manifest['eligible_non_l7_promotion_rows']}",
        f"- immediate_deep_audit_rows: {manifest['immediate_deep_audit_rows']}",
        f"- eligible_source_info_axis_count: {manifest['eligible_source_info_axis_count']}",
        f"- eligible_next_wave_family_count: {manifest['eligible_next_wave_family_count']}",
        f"- missing_field_repair_rows: {manifest['missing_field_repair_rows']}",
        f"- quote_volume_alias_repair_ready: {manifest['quote_volume_alias_repair_ready']}",
        "",
        "A7LS-11 does not run search, replay, or alpha proof. It converts the A7LS-10 company numeric output into a repairable deep-audit queue and fixes the known missing-field route.",
        "",
        "## Eligible Family Summary",
        "",
        table(eligible_summary.head(30)),
        "",
        "## Label Summary",
        "",
        table(label_summary),
        "",
        "## Missing Field Repair Plan",
        "",
        table(missing_repair),
        "",
        "## Blocked Next Tasks",
        "",
        table(blocked_next),
        "",
        "## Authorization",
        "",
        "- A7LS-12 deep-audit contract: authorized",
        "- new formula search / large search: not authorized",
        "- alpha proof / shadow / paper / live: not authorized",
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    print(json.dumps(build(), indent=2, sort_keys=True))
