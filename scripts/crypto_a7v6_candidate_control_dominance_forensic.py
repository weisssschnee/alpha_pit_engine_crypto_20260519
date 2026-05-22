from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
A7V5_DIR = ROOT / "runtime" / "a7v5_small_replay_smoke"
OUT_DIR = ROOT / "runtime" / "a7v6_candidate_control_dominance_forensic"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7V6_CANDIDATE_CONTROL_DOMINANCE_FORENSIC_20260522.md"

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
    return out if math.isfinite(out) else None


def bool_int(value: bool) -> int:
    return int(bool(value))


def metric_col(metric: str, split: str) -> str:
    return f"{metric}__{split}"


def load_wide_metrics() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    metrics = pd.read_csv(A7V5_DIR / "a7v5_smoke_split_metrics.csv")
    labels = pd.read_csv(A7V5_DIR / "a7v5_smoke_candidate_labels.csv")
    selected = pd.read_csv(A7V5_DIR / "a7v5_selected_candidates.csv")
    controls = pd.read_csv(A7V5_DIR / "a7v5_selected_controls.csv")
    idx = [
        "candidate_id",
        "base_candidate_id",
        "object_type",
        "control_mode",
        "production_family",
        "expression",
        "horizon",
    ]
    values = [
        "active_hours",
        "gross_exposure_mean",
        "mean_ic",
        "net_sum_10bps",
        "net_sum_20bps",
        "turnover_mean",
    ]
    wide = metrics.pivot_table(index=idx, columns="split", values=values, aggfunc="first")
    wide.columns = [f"{a}__{b}" for a, b in wide.columns]
    wide = wide.reset_index()
    label_cols = [
        "candidate_id",
        "fresh_may_status",
        "smoke_label",
        "validation_positive",
        "recent_positive",
        "control_non_promotable",
    ]
    wide = wide.merge(labels[label_cols], on="candidate_id", how="left")
    return metrics, wide, selected, controls


def best_control(controls: pd.DataFrame, metric: str, split: str) -> tuple[str, str, float | None]:
    col = metric_col(metric, split)
    if controls.empty or col not in controls:
        return "", "", None
    valid = controls[np.isfinite(pd.to_numeric(controls[col], errors="coerce"))].copy()
    if valid.empty:
        return "", "", None
    row = valid.loc[pd.to_numeric(valid[col], errors="coerce").idxmax()]
    return str(row["candidate_id"]), str(row["control_mode"]), clean_float(row[col])


def build_dominance_table(wide: pd.DataFrame, selected: pd.DataFrame) -> pd.DataFrame:
    candidates = wide[wide["object_type"].eq("candidate")].copy()
    controls = wide[wide["object_type"].eq("control")].copy()
    lineage_cols = [
        "candidate_id",
        "derived_feature_id",
        "source_fields",
        "source_field_families",
        "transform",
        "window_hours",
        "availability_mask",
        "feature_available_lag_bars",
        "paired_ablation_plan",
    ]
    lineage = selected[[c for c in lineage_cols if c in selected.columns]].copy()
    rows: list[dict[str, Any]] = []
    for _, cand in candidates.iterrows():
        cid = str(cand["candidate_id"])
        matched = controls[controls["base_candidate_id"].eq(cid)].copy()
        rec: dict[str, Any] = {
            "candidate_id": cid,
            "production_family": str(cand["production_family"]),
            "expression": str(cand["expression"]),
            "horizon": int(cand["horizon"]),
            "smoke_label": str(cand.get("smoke_label", "")),
            "fresh_may_status": str(cand.get("fresh_may_status", "")),
        }
        for split in [VALIDATION, RECENT, MAY]:
            for metric in ["net_sum_10bps", "net_sum_20bps", "mean_ic", "active_hours", "turnover_mean", "gross_exposure_mean"]:
                rec[f"candidate_{metric}__{split}"] = clean_float(cand.get(metric_col(metric, split)))
            for metric in ["net_sum_10bps", "mean_ic"]:
                control_id, control_mode, value = best_control(matched, metric, split)
                cand_value = clean_float(cand.get(metric_col(metric, split)))
                rec[f"max_control_{metric}__{split}"] = value
                rec[f"max_control_{metric}_id__{split}"] = control_id
                rec[f"max_control_{metric}_mode__{split}"] = control_mode
                rec[f"margin_vs_max_control_{metric}__{split}"] = clean_float((cand_value or 0.0) - (value or 0.0)) if cand_value is not None and value is not None else None
        val_col = metric_col("net_sum_10bps", VALIDATION)
        recent_col = metric_col("net_sum_10bps", RECENT)
        val_ic_col = metric_col("mean_ic", VALIDATION)
        recent_ic_col = metric_col("mean_ic", RECENT)
        val20_col = metric_col("net_sum_20bps", VALIDATION)
        recent20_col = metric_col("net_sum_20bps", RECENT)
        may_col = metric_col("net_sum_10bps", MAY)
        control_val_recent_positive = matched[
            (pd.to_numeric(matched[val_col], errors="coerce") > 0)
            & (pd.to_numeric(matched[recent_col], errors="coerce") > 0)
        ]
        control_recent20_positive = matched[pd.to_numeric(matched[recent20_col], errors="coerce") > 0]
        max_val_control = pd.to_numeric(matched[val_col], errors="coerce").max() if not matched.empty else np.nan
        max_recent_control = pd.to_numeric(matched[recent_col], errors="coerce").max() if not matched.empty else np.nan
        max_val_ic_control = pd.to_numeric(matched[val_ic_col], errors="coerce").max() if not matched.empty else np.nan
        max_recent_ic_control = pd.to_numeric(matched[recent_ic_col], errors="coerce").max() if not matched.empty else np.nan
        cand_val = clean_float(cand.get(val_col)) or 0.0
        cand_recent = clean_float(cand.get(recent_col)) or 0.0
        cand_val_ic = clean_float(cand.get(val_ic_col)) or 0.0
        cand_recent_ic = clean_float(cand.get(recent_ic_col)) or 0.0
        rec["matched_control_count"] = int(len(matched))
        rec["control_val_recent_positive_count"] = int(len(control_val_recent_positive))
        rec["control_recent20_positive_count"] = int(len(control_recent20_positive))
        rec["dominates_controls_val_recent_net10"] = bool_int(cand_val > max_val_control and cand_recent > max_recent_control)
        rec["dominates_controls_val_recent_ic"] = bool_int(cand_val_ic > max_val_ic_control and cand_recent_ic > max_recent_ic_control)
        rec["cost20_survives_validation_recent"] = bool_int(
            (clean_float(cand.get(val20_col)) or 0.0) > 0
            and (clean_float(cand.get(recent20_col)) or 0.0) > 0
        )
        rec["may_stress_positive"] = bool_int((clean_float(cand.get(may_col)) or 0.0) > 0)
        rec["is_a7v5_smoke_positive"] = bool_int(rec["smoke_label"] == "A7V5_SIGNAL_SMOKE_POSITIVE_NOT_PROOF")
        rec["pre_may_control_clean_cost20_dominance"] = bool_int(
            rec["is_a7v5_smoke_positive"]
            and rec["dominates_controls_val_recent_net10"]
            and rec["cost20_survives_validation_recent"]
            and rec["control_val_recent_positive_count"] == 0
        )
        if not rec["is_a7v5_smoke_positive"]:
            label = "A7V6_NOT_A7V5_POSITIVE"
        elif rec["control_val_recent_positive_count"] > 0:
            label = "A7V6_HOLD_CONTROL_CONTAMINATED"
        elif not rec["dominates_controls_val_recent_net10"]:
            label = "A7V6_HOLD_DOES_NOT_DOMINATE_CONTROLS"
        elif not rec["cost20_survives_validation_recent"]:
            label = "A7V6_HOLD_COST20_FRAGILE"
        elif not rec["may_stress_positive"]:
            label = "A7V6_PRE_MAY_DOMINANCE_CLUE_MAY_FAIL"
        else:
            label = "A7V6_DOMINANCE_CANDIDATE_NEEDS_DEEP_REPLAY"
        rec["a7v6_label"] = label
        rows.append(rec)
    out = pd.DataFrame(rows)
    out = out.merge(lineage, on="candidate_id", how="left")
    return out


def build_control_summary(wide: pd.DataFrame) -> pd.DataFrame:
    controls = wide[wide["object_type"].eq("control")].copy()
    controls["val_recent_positive"] = (
        (pd.to_numeric(controls[metric_col("net_sum_10bps", VALIDATION)], errors="coerce") > 0)
        & (pd.to_numeric(controls[metric_col("net_sum_10bps", RECENT)], errors="coerce") > 0)
    )
    controls["recent20_positive"] = pd.to_numeric(controls[metric_col("net_sum_20bps", RECENT)], errors="coerce") > 0
    controls["may_positive"] = pd.to_numeric(controls[metric_col("net_sum_10bps", MAY)], errors="coerce") > 0
    return (
        controls.groupby(["control_mode", "production_family"])
        .agg(
            rows=("candidate_id", "count"),
            val_recent_positive=("val_recent_positive", "sum"),
            recent20_positive=("recent20_positive", "sum"),
            may_positive=("may_positive", "sum"),
            mean_validation_net10=(metric_col("net_sum_10bps", VALIDATION), "mean"),
            mean_recent_net10=(metric_col("net_sum_10bps", RECENT), "mean"),
            mean_may_net10=(metric_col("net_sum_10bps", MAY), "mean"),
        )
        .reset_index()
    )


def build_family_summary(dominance: pd.DataFrame) -> pd.DataFrame:
    return (
        dominance.groupby(["production_family", "a7v6_label"])
        .agg(rows=("candidate_id", "count"))
        .reset_index()
        .sort_values(["production_family", "a7v6_label"])
    )


def write_report(now: str, dominance: pd.DataFrame, control_summary: pd.DataFrame, family_summary: pd.DataFrame, authorization: dict[str, Any]) -> None:
    positive = dominance[dominance["is_a7v5_smoke_positive"].eq(1)].copy()
    pre_may = dominance[dominance["pre_may_control_clean_cost20_dominance"].eq(1)].copy()
    controls_contam = positive[positive["control_val_recent_positive_count"].gt(0)].copy()
    cols = [
        "candidate_id",
        "production_family",
        "expression",
        "a7v6_label",
        "candidate_net_sum_10bps__validation_2025H1",
        "candidate_net_sum_10bps__recent_oos_2025H2_2026Apr",
        "candidate_net_sum_20bps__recent_oos_2025H2_2026Apr",
        "candidate_net_sum_10bps__fresh_may_2026",
        "margin_vs_max_control_net_sum_10bps__validation_2025H1",
        "margin_vs_max_control_net_sum_10bps__recent_oos_2025H2_2026Apr",
        "control_val_recent_positive_count",
        "dominates_controls_val_recent_net10",
        "dominates_controls_val_recent_ic",
        "cost20_survives_validation_recent",
        "may_stress_positive",
    ]
    lines = [
        "# Crypto A7V-6 Candidate/Control Dominance Forensic",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{authorization['decision']}`",
        "- executes_search: `False`",
        "- executes_replay: `False`",
        "- alpha proof / full search / shadow / paper / live: `NOT_AUTHORIZED`",
        "",
        "## Scope",
        "",
        "A7V-6 reviews the A7V-5 capped smoke outputs. It does not generate candidates and does not rerun replay. The objective is to determine whether A7V-5 smoke-positive candidates dominate their matched row-shuffle, time-shuffle, wrong-lag, and sign-flip controls before any larger replay is considered.",
        "",
        "May remains a stress-only label. It is used here only to block robustness claims, not to rank, tune, or select formulas.",
        "",
        "## Decision Summary",
        "",
        f"- A7V-5 smoke positives: `{len(positive)}`",
        f"- pre-May control-clean + 20bps dominance clues: `{len(pre_may)}`",
        f"- post-May positive among A7V-5 positives: `{int(positive['may_stress_positive'].sum())}`",
        f"- A7V-5 positives with matched control validation+recent positive: `{len(controls_contam)}`",
        f"- candidates authorized for promotion: `0`",
        "",
        "## A7V-5 Positive Candidate Dominance",
        "",
        table(positive[cols].sort_values(["a7v6_label", "candidate_net_sum_10bps__recent_oos_2025H2_2026Apr"], ascending=[True, False]), max_rows=80),
        "",
        "## Pre-May Dominance Clues",
        "",
        table(pre_may[cols].sort_values("candidate_net_sum_10bps__recent_oos_2025H2_2026Apr", ascending=False), max_rows=40),
        "",
        "## Control Summary",
        "",
        table(control_summary, max_rows=80),
        "",
        "## Family Summary",
        "",
        table(family_summary, max_rows=80),
        "",
        "## Candidate Factor Review Notes",
        "",
        "- provenance: generated by A7V-3 agg-aware dry run, replay-smoked by A7V-5, reviewed here against matched controls.",
        "- data source: `crypto_core12_1h_with_aggtrades_features_v1.parquet`, restricted to core3 rows with `agg_features_available=true`.",
        "- operator path: aggTrades enhanced fields -> A7V-1 registered rolling/cross-symbol/interaction transforms -> A7V-3 formulas -> A7V-5 core3 top1/bottom1 smoke book.",
        "- keep-list decision: `HOLD_RESEARCH`; no factor is eligible for keep review or promotion from A7V-6.",
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
        "",
        "## Required Next",
        "",
        "- A7V-7 should focus on the 5 pre-May dominance clues as failure-attribution objects, not promotion objects.",
        "- Do not expand replay until May stress failure and matched-control contamination are explained.",
        "- A7U-0R consolidated raw checksum/source trace is still required before final panel claims.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_stamp()
    metrics, wide, selected, controls = load_wide_metrics()
    dominance = build_dominance_table(wide, selected)
    control_summary = build_control_summary(wide)
    family_summary = build_family_summary(dominance)
    positive = dominance[dominance["is_a7v5_smoke_positive"].eq(1)]
    pre_may = dominance[dominance["pre_may_control_clean_cost20_dominance"].eq(1)]
    post_may_positive = int(positive["may_stress_positive"].sum())
    contaminated_positive = int(positive["control_val_recent_positive_count"].gt(0).sum())
    blockers = []
    if len(positive) == 0:
        blockers.append("no_a7v5_smoke_positive_candidates")
    if post_may_positive == 0:
        blockers.append("no_a7v5_positive_survives_may_stress")
    if contaminated_positive > 0:
        blockers.append("matched_controls_positive_for_a7v5_positives")
    if len(pre_may) < 2:
        blockers.append("too_few_pre_may_control_clean_dominance_clues")
    pre_may_family_share = 0.0
    if not pre_may.empty:
        pre_may_family_share = float(pre_may["production_family"].value_counts(normalize=True).iloc[0])
    if pre_may_family_share > 0.70:
        blockers.append("pre_may_clues_family_concentrated")
    decision = "HOLD_A7V6_NO_POST_MAY_DOMINANT_CANDIDATE" if blockers else "PASS_A7V6_DOMINANCE_FORENSIC_READY_FOR_EXPANDED_REPLAY_REVIEW"
    authorization = {
        "generated_at": now,
        "decision": decision,
        "blockers": blockers,
        "executes_search": False,
        "executes_replay": False,
        "a7v5_metric_rows_read": int(len(metrics)),
        "a7v5_candidate_count": int(wide["object_type"].eq("candidate").sum()),
        "a7v5_control_count": int(wide["object_type"].eq("control").sum()),
        "a7v5_smoke_positive_count": int(len(positive)),
        "pre_may_control_clean_cost20_dominance_count": int(len(pre_may)),
        "post_may_positive_among_a7v5_positives": post_may_positive,
        "a7v5_positives_with_matched_positive_controls": contaminated_positive,
        "pre_may_top_family_share": clean_float(pre_may_family_share),
        "authorizes_full_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "authorizes_may_robustness_claim": False,
        "authorizes_expanded_replay": False,
        "authorizes_a7v7_failure_attribution": True,
        "required_next": [
            "A7V-7 failure attribution on the 5 pre-May dominance clues",
            "Do not promote A7V candidates; all A7V-5 positives fail May stress",
            "Explain matched-control contamination before any expanded replay",
            "A7U-0R consolidated raw checksum/source trace before final panel claims",
        ],
    }
    dominance.to_csv(OUT_DIR / "a7v6_candidate_control_dominance.csv", index=False)
    dominance[dominance["is_a7v5_smoke_positive"].eq(1)].to_csv(OUT_DIR / "a7v6_positive_candidate_dominance.csv", index=False)
    pre_may.to_csv(OUT_DIR / "a7v6_pre_may_dominance_clues.csv", index=False)
    control_summary.to_csv(OUT_DIR / "a7v6_control_mode_summary.csv", index=False)
    family_summary.to_csv(OUT_DIR / "a7v6_family_summary.csv", index=False)
    write_json(OUT_DIR / "a7v6_authorization_matrix.json", authorization)
    write_json(
        OUT_DIR / "a7v6_manifest.json",
        {
            "generated_at": now,
            "decision": decision,
            "input_dir": str(A7V5_DIR),
            "output_dir": str(OUT_DIR),
            "report": str(REPORT_PATH),
        },
    )
    write_report(now, dominance, control_summary, family_summary, authorization)
    print(json.dumps({"decision": decision, "blockers": blockers, "pre_may_clues": len(pre_may), "post_may_positive": post_may_positive}, indent=2))


if __name__ == "__main__":
    main()
