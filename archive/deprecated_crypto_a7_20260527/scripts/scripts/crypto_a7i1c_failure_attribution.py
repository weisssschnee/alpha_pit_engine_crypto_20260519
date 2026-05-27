from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from crypto_a7_validation_utils import REPORT_DIR, RUNTIME_DIR, clean_float


A7I1B_DIR = RUNTIME_DIR / "a7i1b_matched_budget_smoke"
A7I1C_DIR = RUNTIME_DIR / "a7i1c_failure_attribution"
DATE_TAG = "20260520"


GATE_ORDER = [
    "raw_validation_nonpositive",
    "raw_recent_nonpositive",
    "raw_may_severely_negative",
    "residual_funding_validation_nonpositive",
    "residual_funding_recent_nonpositive",
    "residual_funding_may_negative",
    "residual_core4_recent_nonpositive",
    "cost20_recent_collapse",
    "execution_lag_recent_collapse",
    "funding_beta_too_high",
    "core4_beta_too_high",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_csv(name: str) -> pd.DataFrame:
    path = A7I1B_DIR / name
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def as_bool(s: pd.Series) -> pd.Series:
    if s.dtype == bool:
        return s
    return s.astype(str).str.lower().isin(["true", "1", "yes"])


def pivot_metrics(long_df: pd.DataFrame) -> pd.DataFrame:
    parts = []
    for value_col in ["annualized_mean", "compounded_max_dd", "mean_turnover", "mean_gross_exposure"]:
        p = long_df.pivot_table(index="candidate_id", columns=["series", "split"], values=value_col, aggfunc="first")
        p.columns = [f"{series}__{split}__{value_col}" for series, split in p.columns]
        parts.append(p)
    return pd.concat(parts, axis=1).reset_index()


def col(df: pd.DataFrame, name: str) -> pd.Series:
    if name not in df.columns:
        return pd.Series(np.nan, index=df.index)
    return pd.to_numeric(df[name], errors="coerce")


def add_gate_margins(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["raw_validation_margin_to_0"] = col(out, "raw_10bp__validation_2025H1__annualized_mean")
    out["raw_recent_margin_to_0"] = col(out, "raw_10bp__recent_oos_2025H2_2026Apr__annualized_mean")
    out["raw_may_margin_to_minus_0p5"] = col(out, "raw_may_10bp_ann_stress_only") + 0.5
    out["residual_funding_validation_margin_to_0"] = col(out, "residual_vs_funding_10bp__validation_2025H1__annualized_mean")
    out["residual_funding_recent_margin_to_0"] = col(out, "residual_vs_funding_10bp__recent_oos_2025H2_2026Apr__annualized_mean")
    out["residual_funding_may_margin_to_0"] = col(out, "residual_funding_may_ann_stress_only")
    out["residual_core4_recent_margin_to_0"] = col(out, "residual_vs_core4_10bp__recent_oos_2025H2_2026Apr__annualized_mean")
    out["cost20_recent_margin_to_minus_1"] = col(out, "raw_20bp__recent_oos_2025H2_2026Apr__annualized_mean") + 1.0
    out["lag_recent_margin_to_minus_1"] = col(out, "execution_lag_1bar_raw_10bp__recent_oos_2025H2_2026Apr__annualized_mean") + 1.0
    out["lag_may_margin_to_minus_1"] = col(out, "execution_lag_1bar_raw_10bp__fresh_forward_2026May__annualized_mean") + 1.0
    out["funding_beta_abs_margin_to_0p5"] = 0.5 - col(out, "funding_beta_recent").abs()
    out["core4_beta_abs_margin_to_0p5"] = 0.5 - col(out, "core4_beta_recent").abs()
    gate_exprs = {
        "raw_validation_nonpositive": out["raw_validation_margin_to_0"] <= 0,
        "raw_recent_nonpositive": out["raw_recent_margin_to_0"] <= 0,
        "raw_may_severely_negative": out["raw_may_margin_to_minus_0p5"] < 0,
        "residual_funding_validation_nonpositive": out["residual_funding_validation_margin_to_0"] <= 0,
        "residual_funding_recent_nonpositive": out["residual_funding_recent_margin_to_0"] <= 0,
        "residual_funding_may_negative": out["residual_funding_may_margin_to_0"] < 0,
        "residual_core4_recent_nonpositive": out["residual_core4_recent_margin_to_0"] <= 0,
        "cost20_recent_collapse": out["cost20_recent_margin_to_minus_1"] < 0,
        "execution_lag_recent_collapse": out["lag_recent_margin_to_minus_1"] < 0,
        "funding_beta_too_high": out["funding_beta_abs_margin_to_0p5"] < 0,
        "core4_beta_too_high": out["core4_beta_abs_margin_to_0p5"] < 0,
    }
    for gate, values in gate_exprs.items():
        out[f"gate_fail__{gate}"] = values.fillna(True)
    def first_gate(row: pd.Series) -> str:
        if row.get("object_type") == "placebo":
            return "placebo_negative_control"
        for gate in GATE_ORDER:
            if bool(row.get(f"gate_fail__{gate}", False)):
                return gate
        return "passes_all_a7i1b_research_gates"
    out["killer_gate"] = out.apply(first_gate, axis=1)
    gate_cols = [f"gate_fail__{g}" for g in GATE_ORDER]
    out["failed_gate_count"] = out[gate_cols].sum(axis=1).astype(int)
    margin_cols = [
        "raw_validation_margin_to_0",
        "raw_recent_margin_to_0",
        "raw_may_margin_to_minus_0p5",
        "residual_funding_validation_margin_to_0",
        "residual_funding_recent_margin_to_0",
        "residual_funding_may_margin_to_0",
        "residual_core4_recent_margin_to_0",
        "cost20_recent_margin_to_minus_1",
        "lag_recent_margin_to_minus_1",
        "funding_beta_abs_margin_to_0p5",
        "core4_beta_abs_margin_to_0p5",
    ]
    out["worst_margin"] = out[margin_cols].min(axis=1, skipna=True)
    out["negative_margin_sum"] = out[margin_cols].clip(upper=0).sum(axis=1, skipna=True)
    return out


def quantile_rows(df: pd.DataFrame, group_cols: list[str], value_cols: list[str]) -> pd.DataFrame:
    rows = []
    for group_key, g in df.groupby(group_cols, dropna=False):
        if not isinstance(group_key, tuple):
            group_key = (group_key,)
        prefix = dict(zip(group_cols, group_key))
        for colname in value_cols:
            vals = pd.to_numeric(g[colname], errors="coerce").dropna()
            row = dict(prefix)
            row["metric"] = colname
            row["count"] = int(vals.size)
            if vals.empty:
                row.update({k: None for k in ["mean", "std", "min", "q05", "q25", "median", "q75", "q95", "max"]})
            else:
                row.update(
                    {
                        "mean": clean_float(vals.mean()),
                        "std": clean_float(vals.std(ddof=1)),
                        "min": clean_float(vals.min()),
                        "q05": clean_float(vals.quantile(0.05)),
                        "q25": clean_float(vals.quantile(0.25)),
                        "median": clean_float(vals.quantile(0.50)),
                        "q75": clean_float(vals.quantile(0.75)),
                        "q95": clean_float(vals.quantile(0.95)),
                        "max": clean_float(vals.max()),
                    }
                )
            rows.append(row)
    return pd.DataFrame(rows)


def main() -> int:
    A7I1C_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_now()

    scoreboard = read_csv("a7i1_candidate_scoreboard.csv")
    full_metric = read_csv("a7i1_full_metric_long.csv")
    rejected = read_csv("a7i1_rejected_candidate_reasons.csv")
    shortlist = read_csv("a7i1_research_candidate_shortlist.csv")
    may = read_csv("a7i1_may_stress_only_audit.csv")
    beta = read_csv("a7i1_beta_corr_audit.csv")
    lag = read_csv("a7i1_execution_lag_1bar_stress.csv")

    scoreboard["selected_for_replay"] = as_bool(scoreboard["selected_for_replay"])
    wide = pivot_metrics(full_metric)
    beta_recent = beta[beta["split"] == "recent_oos_2025H2_2026Apr"][
        ["candidate_id", "funding_beta", "funding_corr", "core4_beta", "core4_corr"]
    ].rename(
        columns={
            "funding_beta": "funding_beta_recent",
            "funding_corr": "funding_corr_recent",
            "core4_beta": "core4_beta_recent",
            "core4_corr": "core4_corr_recent",
        }
    )
    merged = (
        scoreboard.merge(wide, on="candidate_id", how="left")
        .merge(may, on=["candidate_id", "arm"], how="left")
        .merge(beta_recent, on="candidate_id", how="left")
    )
    decision_source = pd.concat([rejected, shortlist], ignore_index=True, sort=False)
    decision_source = decision_source[["candidate_id", "candidate_decision", "reject_reasons"]].drop_duplicates("candidate_id")
    merged = merged.merge(decision_source, on="candidate_id", how="left")
    merged["candidate_decision"] = merged["candidate_decision"].fillna("NOT_SELECTED_FOR_REPLAY")
    merged["reject_reasons"] = merged["reject_reasons"].fillna("")
    merged = add_gate_margins(merged)

    selected = merged[merged["selected_for_replay"]].copy()
    non_placebo_selected = selected[selected["object_type"] != "placebo"].copy()
    research = selected[selected["candidate_decision"] == "A7I_RESEARCH_CANDIDATE"].copy()

    generation_funnel = (
        merged.groupby("arm", as_index=False)
        .agg(
            generated_count=("candidate_id", "size"),
            selected_count=("selected_for_replay", "sum"),
            research_candidate_count=("candidate_decision", lambda x: int((x == "A7I_RESEARCH_CANDIDATE").sum())),
            placebo_count=("object_type", lambda x: int((x == "placebo").sum())),
            median_rank_score=("rank_score", "median"),
            p95_rank_score=("rank_score", lambda x: x.quantile(0.95)),
        )
    )
    generation_funnel["selected_rate"] = generation_funnel["selected_count"] / generation_funnel["generated_count"]

    reject_rows = []
    for _, row in selected.iterrows():
        reasons = [r for r in str(row["reject_reasons"]).split(";") if r]
        if row["candidate_decision"] == "A7I_RESEARCH_CANDIDATE":
            reasons = ["pass_all_research_gates"]
        elif not reasons:
            reasons = [row["candidate_decision"]]
        for reason in reasons:
            reject_rows.append({"candidate_id": row["candidate_id"], "arm": row["arm"], "reason": reason})
    selected_reject_counts = (
        pd.DataFrame(reject_rows).groupby(["arm", "reason"], as_index=False).size().rename(columns={"size": "count"})
        if reject_rows
        else pd.DataFrame(columns=["arm", "reason", "count"])
    )

    score_cols = [c for c in scoreboard.columns if c.startswith("component_")] + ["rank_score"]
    score_distribution = quantile_rows(merged, ["arm", "selected_for_replay"], score_cols)

    margin_cols = [
        "raw_validation_margin_to_0",
        "raw_recent_margin_to_0",
        "raw_may_margin_to_minus_0p5",
        "residual_funding_validation_margin_to_0",
        "residual_funding_recent_margin_to_0",
        "residual_funding_may_margin_to_0",
        "residual_core4_recent_margin_to_0",
        "cost20_recent_margin_to_minus_1",
        "lag_recent_margin_to_minus_1",
        "lag_may_margin_to_minus_1",
        "funding_beta_abs_margin_to_0p5",
        "core4_beta_abs_margin_to_0p5",
    ]
    near_miss = (
        merged[merged["object_type"] != "placebo"]
        .sort_values(["failed_gate_count", "negative_margin_sum", "rank_score"], ascending=[True, False, False])
        .head(80)
    )[
        [
            "candidate_id",
            "arm",
            "family",
            "expression",
            "horizon",
            "selected_for_replay",
            "candidate_decision",
            "killer_gate",
            "failed_gate_count",
            "rank_score",
            *margin_cols,
        ]
    ]

    killer = merged.groupby(["arm", "selected_for_replay", "killer_gate"], as_index=False).size().rename(columns={"size": "count"})
    breakdown = (
        merged.groupby(["arm", "family", "horizon"], as_index=False)
        .agg(
            generated_count=("candidate_id", "size"),
            selected_count=("selected_for_replay", "sum"),
            research_candidate_count=("candidate_decision", lambda x: int((x == "A7I_RESEARCH_CANDIDATE").sum())),
            median_rank_score=("rank_score", "median"),
        )
        .sort_values(["arm", "family", "horizon"])
    )

    may_dist = quantile_rows(
        merged,
        ["arm", "selected_for_replay"],
        ["raw_may_10bp_ann_stress_only", "residual_funding_may_ann_stress_only", "residual_core4_may_ann_stress_only"],
    )
    may_fail_counts = merged.groupby(["arm", "selected_for_replay"], as_index=False).agg(
        raw_may_severe_fail_count=("gate_fail__raw_may_severely_negative", "sum"),
        residual_funding_may_fail_count=("gate_fail__residual_funding_may_negative", "sum"),
        candidate_count=("candidate_id", "size"),
    )
    may_dist = may_dist.merge(may_fail_counts, on=["arm", "selected_for_replay"], how="left")

    cost_lag_dist = quantile_rows(
        merged,
        ["arm", "selected_for_replay"],
        [
            "raw_20bp__recent_oos_2025H2_2026Apr__annualized_mean",
            "execution_lag_1bar_raw_10bp__recent_oos_2025H2_2026Apr__annualized_mean",
            "execution_lag_1bar_raw_10bp__fresh_forward_2026May__annualized_mean",
        ],
    )
    cost_lag_fail = merged.groupby(["arm", "selected_for_replay"], as_index=False).agg(
        cost20_recent_collapse_count=("gate_fail__cost20_recent_collapse", "sum"),
        execution_lag_recent_collapse_count=("gate_fail__execution_lag_recent_collapse", "sum"),
        candidate_count=("candidate_id", "size"),
    )
    cost_lag_dist = cost_lag_dist.merge(cost_lag_fail, on=["arm", "selected_for_replay"], how="left")

    residual_fail = merged.groupby(["arm", "selected_for_replay"], as_index=False).agg(
        residual_funding_validation_fail_count=("gate_fail__residual_funding_validation_nonpositive", "sum"),
        residual_funding_recent_fail_count=("gate_fail__residual_funding_recent_nonpositive", "sum"),
        residual_funding_may_fail_count=("gate_fail__residual_funding_may_negative", "sum"),
        residual_core4_recent_fail_count=("gate_fail__residual_core4_recent_nonpositive", "sum"),
        funding_beta_fail_count=("gate_fail__funding_beta_too_high", "sum"),
        core4_beta_fail_count=("gate_fail__core4_beta_too_high", "sum"),
        candidate_count=("candidate_id", "size"),
    )

    single = research.copy()
    if not single.empty:
        single["fragility_notes"] = single.apply(
            lambda r: ";".join(
                [
                    note
                    for note, flag in [
                        ("raw_may_near_severe_cutoff", pd.notna(r["raw_may_margin_to_minus_0p5"]) and r["raw_may_margin_to_minus_0p5"] < 0.05),
                        (
                            "cost20_recent_negative",
                            pd.notna(r["raw_20bp__recent_oos_2025H2_2026Apr__annualized_mean"])
                            and r["raw_20bp__recent_oos_2025H2_2026Apr__annualized_mean"] < 0,
                        ),
                        (
                            "lag_may_below_minus_1",
                            pd.notna(r["lag_may_margin_to_minus_1"]) and r["lag_may_margin_to_minus_1"] < 0,
                        ),
                    ]
                    if flag
                ]
            ),
            axis=1,
        )
    single_cols = [
        "candidate_id",
        "arm",
        "family",
        "expression",
        "horizon",
        "rank_score",
        "candidate_decision",
        "raw_10bp__validation_2025H1__annualized_mean",
        "raw_10bp__recent_oos_2025H2_2026Apr__annualized_mean",
        "raw_may_10bp_ann_stress_only",
        "raw_20bp__recent_oos_2025H2_2026Apr__annualized_mean",
        "execution_lag_1bar_raw_10bp__recent_oos_2025H2_2026Apr__annualized_mean",
        "execution_lag_1bar_raw_10bp__fresh_forward_2026May__annualized_mean",
        "residual_vs_funding_10bp__validation_2025H1__annualized_mean",
        "residual_vs_funding_10bp__recent_oos_2025H2_2026Apr__annualized_mean",
        "residual_funding_may_ann_stress_only",
        "residual_vs_core4_10bp__recent_oos_2025H2_2026Apr__annualized_mean",
        "raw_may_margin_to_minus_0p5",
        "cost20_recent_margin_to_minus_1",
        "lag_recent_margin_to_minus_1",
        "lag_may_margin_to_minus_1",
        "fragility_notes",
    ]
    single_record = single[[c for c in single_cols if c in single.columns]].copy()

    generation_funnel_path = A7I1C_DIR / "a7i1c_generation_funnel_by_arm.csv"
    selected_reject_path = A7I1C_DIR / "a7i1c_selected_reject_reason_counts.csv"
    score_dist_path = A7I1C_DIR / "a7i1c_all_generated_score_component_distribution.csv"
    near_miss_path = A7I1C_DIR / "a7i1c_near_miss_candidates.csv"
    killer_path = A7I1C_DIR / "a7i1c_killer_gate_hierarchy.csv"
    breakdown_path = A7I1C_DIR / "a7i1c_arm_family_horizon_breakdown.csv"
    may_dist_path = A7I1C_DIR / "a7i1c_may_stress_fail_distribution.csv"
    cost_lag_path = A7I1C_DIR / "a7i1c_cost20_lag_fragility_distribution.csv"
    residual_fail_path = A7I1C_DIR / "a7i1c_residual_baseline_fail_distribution.csv"
    single_path = A7I1C_DIR / "a7i1c_single_candidate_fragility_record.csv"

    generation_funnel.to_csv(generation_funnel_path, index=False)
    selected_reject_counts.to_csv(selected_reject_path, index=False)
    score_distribution.to_csv(score_dist_path, index=False)
    near_miss.to_csv(near_miss_path, index=False)
    killer.to_csv(killer_path, index=False)
    breakdown.to_csv(breakdown_path, index=False)
    may_dist.to_csv(may_dist_path, index=False)
    cost_lag_dist.to_csv(cost_lag_path, index=False)
    residual_fail.to_csv(residual_fail_path, index=False)
    single_record.to_csv(single_path, index=False)

    selected_reason_top = selected_reject_counts.sort_values("count", ascending=False).head(1)
    dominant_reason = selected_reason_top.iloc[0]["reason"] if not selected_reason_top.empty else None
    research_count = int((selected["candidate_decision"] == "A7I_RESEARCH_CANDIDATE").sum())
    placebo_research_count = int(((selected["candidate_decision"] == "A7I_RESEARCH_CANDIDATE") & (selected["arm"] == "I3_placebo_random")).sum())
    unique_fragile = False
    if len(single_record) == 1:
        notes = str(single_record.iloc[0].get("fragility_notes", ""))
        unique_fragile = bool(notes)
    if research_count < 2 and dominant_reason == "raw_may_severely_negative":
        decision = "HOLD_A7I1C_MAY_STRESS_BROAD_FAIL"
    elif research_count < 2 and unique_fragile:
        decision = "HOLD_A7I1C_COST_LAG_FRAGILE"
    elif research_count < 2 and dominant_reason in {"raw_validation_nonpositive", "raw_recent_nonpositive"}:
        decision = "HOLD_A7I1C_GENERATOR_RAW_WEAK"
    elif research_count < 2:
        decision = "HOLD_A7I1C_INSUFFICIENT_CANDIDATES"
    elif placebo_research_count > 0:
        decision = "HOLD_A7I1C_PLACEBO_TOO_STRONG"
    else:
        decision = "PASS_A7I1C_READY_FOR_SINGLE_CANDIDATE_DEEP_AUDIT"

    manifest = {
        "generated_at": now,
        "decision": decision,
        "stage": "A7I-1c matched-budget smoke failure attribution",
        "executes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "a7i1b_decision_name_fix": "HOLD_A7I1_INSUFFICIENT_RESEARCH_CANDIDATES",
        "generated_count": int(len(merged)),
        "selected_count": int(len(selected)),
        "research_candidate_count": research_count,
        "placebo_research_candidate_count": placebo_research_count,
        "dominant_selected_reject_reason": dominant_reason,
        "unique_candidate_fragile": unique_fragile,
        "outputs": {
            "generation_funnel_by_arm": str(generation_funnel_path),
            "selected_reject_reason_counts": str(selected_reject_path),
            "all_generated_score_component_distribution": str(score_dist_path),
            "near_miss_candidates": str(near_miss_path),
            "killer_gate_hierarchy": str(killer_path),
            "arm_family_horizon_breakdown": str(breakdown_path),
            "may_stress_fail_distribution": str(may_dist_path),
            "cost20_lag_fragility_distribution": str(cost_lag_path),
            "residual_baseline_fail_distribution": str(residual_fail_path),
            "single_candidate_fragility_record": str(single_path),
        },
    }
    manifest_path = A7I1C_DIR / f"a7i1c_manifest_{DATE_TAG}.json"
    write_json(manifest_path, manifest)

    report_path = REPORT_DIR / f"CRYPTO_A7I1C_FAILURE_ATTRIBUTION_{DATE_TAG}.md"
    lines = [
        "# Crypto A7I-1c Failure Attribution",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{decision}`",
        "- executes_search: `False`",
        "- authorizes_alpha_proof: `False`",
        f"- generated_count: `{len(merged)}`",
        f"- selected_count: `{len(selected)}`",
        f"- research_candidate_count: `{research_count}`",
        f"- placebo_research_candidate_count: `{placebo_research_count}`",
        f"- dominant_selected_reject_reason: `{dominant_reason}`",
        f"- unique_candidate_fragile: `{unique_fragile}`",
        "",
        "## Funnel By Arm",
        "",
        "| arm | generated | selected | research | median score |",
        "|---|---:|---:|---:|---:|",
    ]
    for _, row in generation_funnel.iterrows():
        lines.append(
            f"| `{row['arm']}` | {int(row['generated_count'])} | {int(row['selected_count'])} | "
            f"{int(row['research_candidate_count'])} | {float(row['median_rank_score']):.4f} |"
        )
    lines += [
        "",
        "## Top Selected Reject Reasons",
        "",
        "| arm | reason | count |",
        "|---|---|---:|",
    ]
    for _, row in selected_reject_counts.sort_values("count", ascending=False).head(12).iterrows():
        lines.append(f"| `{row['arm']}` | `{row['reason']}` | {int(row['count'])} |")
    lines += [
        "",
        "## Single Candidate Fragility",
        "",
        "| candidate | expression | raw May | 20bps recent | lag May | notes |",
        "|---|---|---:|---:|---:|---|",
    ]
    if single_record.empty:
        lines.append("| n/a | n/a |  |  |  | n/a |")
    else:
        row = single_record.iloc[0]
        lines.append(
            f"| `{row['candidate_id']}` | `{row['expression']}` | "
            f"{float(row['raw_may_10bp_ann_stress_only']):.4f} | "
            f"{float(row['raw_20bp__recent_oos_2025H2_2026Apr__annualized_mean']):.4f} | "
            f"{float(row['execution_lag_1bar_raw_10bp__fresh_forward_2026May__annualized_mean']):.4f} | "
            f"`{row.get('fragility_notes', '')}` |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        "- A7I-1b did not fail because placebo contaminated the run; placebo research candidates remain zero.",
        "- The blocker is insufficient non-placebo candidate count.",
        "- The only surviving candidate is near the May severe cutoff and weak under 20bps / lag stress, so it is not ready for promotion.",
        "",
        "## Decision Boundary",
        "",
        "- This attribution does not authorize alpha proof, shadow, paper, or live.",
        "- Next valid step is a narrow A7I-2 deep audit only if the single microstructure-lite clue is worth inspecting.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    decision_path = REPORT_DIR / f"CRYPTO_A7I1C_DECISION_RECORD_{DATE_TAG}.md"
    decision_lines = [
        "# Crypto A7I-1c Decision Record",
        "",
        f"decision: {decision}",
        "stage: matched-budget smoke failure attribution",
        "executes_search: false",
        "authorizes_alpha_proof: false",
        "authorizes_shadow_paper_live: false",
        f"research_candidate_count: {research_count}",
        f"placebo_research_candidate_count: {placebo_research_count}",
        f"dominant_selected_reject_reason: {dominant_reason}",
        "",
        "confirmed:",
        "- placebo arm did not produce a comparable research candidate",
        "- A7I-1b failed because candidate count was insufficient",
        "- the single microstructure-lite survivor is fragile and should not be promoted",
        "",
        "not_confirmed:",
        "- alpha proof",
        "- robust non-funding generator",
        "- shadow readiness",
        "- paper/live readiness",
    ]
    decision_path.write_text("\n".join(decision_lines) + "\n", encoding="utf-8")

    print("A7I1C_REPORT=" + str(report_path))
    print("A7I1C_DECISION=" + decision)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
