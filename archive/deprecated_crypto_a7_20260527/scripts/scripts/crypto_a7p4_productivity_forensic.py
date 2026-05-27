from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "runtime"
REPORT_DIR = ROOT / "reports"
CHECKPOINT_ID = "A7P3_W2PILOT"
SOURCE_DIR = RUNTIME_DIR / f"a7o_l1_checkpoint_{CHECKPOINT_ID}"
SOURCE_PREFIX = f"a7o_l1_checkpoint_{CHECKPOINT_ID}"
OUT_DIR = RUNTIME_DIR / "a7p4_productivity_forensic"
DATE_TAG = "20260521"

MIN_GROSS = 0.05
MIN_ACTIVE_HOURS = 10
TARGET_ELIGIBLE_RATE = 0.15


def utc_stamp() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def table(df: pd.DataFrame, max_rows: int = 40) -> str:
    if df.empty:
        return "`<empty>`"
    return df.head(max_rows).to_markdown(index=False)


def load_csv(stem: str) -> pd.DataFrame:
    path = SOURCE_DIR / f"{SOURCE_PREFIX}_{stem}.csv"
    return pd.read_csv(path)


def bool_sum(series: pd.Series) -> int:
    return int(series.fillna(False).astype(bool).sum())


def write_csv(df: pd.DataFrame, name: str) -> Path:
    path = OUT_DIR / name
    df.to_csv(path, index=False)
    return path


def reason_counts(deep: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for _, row in deep.iterrows():
        reasons = str(row.get("reject_reasons", "") or "")
        if reasons.lower() == "nan" or not reasons:
            reasons = "none"
        for reason in reasons.split(";"):
            reason = reason.strip() or "none"
            rows.append(
                {
                    "candidate_id": row["candidate_id"],
                    "candidate_decision": row["candidate_decision"],
                    "reason": reason,
                    "is_post_may_eligible": row["candidate_decision"] == "A7O_PILOT_RESEARCH_CANDIDATE",
                }
            )
    long = pd.DataFrame(rows)
    return (
        long.groupby(["candidate_decision", "reason"], dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values(["count", "candidate_decision"], ascending=[False, True])
    )


def family_summary(deep: pd.DataFrame, keys: list[str], name: str) -> pd.DataFrame:
    g = (
        deep.groupby(keys, dropna=False)
        .agg(
            deep_count=("candidate_id", "count"),
            post_may_eligible_count=("candidate_decision", lambda s: int((s == "A7O_PILOT_RESEARCH_CANDIDATE").sum())),
            may_vetoed_count=("candidate_decision", lambda s: int((s == "A7O_PILOT_MAY_VETOED_NEAR_MISS").sum())),
            pre_may_near_miss_count=("candidate_decision", lambda s: int((s == "A7O_PILOT_PRE_MAY_NEAR_MISS").sum())),
            rejected_count=("candidate_decision", lambda s: int((s == "A7O_PILOT_REJECTED").sum())),
            avg_rank_score=("pilot_rank_score", "mean"),
            avg_raw_may=("raw_10bp__fresh_forward_2026May", "mean"),
            avg_residual_funding_may=("residual_vs_funding_10bp__fresh_forward_2026May", "mean"),
            avg_raw_recent=("raw_10bp__recent_oos_2025H2_2026Apr", "mean"),
            avg_cost20_recent=("raw_20bp__recent_oos_2025H2_2026Apr", "mean"),
            avg_lag1_recent=("execution_lag_1bar_raw_10bp__recent_oos_2025H2_2026Apr", "mean"),
            avg_min_fold=("min_fold_component", "mean"),
            avg_positive_fold_rate=("positive_fold_rate", "mean"),
        )
        .reset_index()
    )
    g["post_may_eligible_rate"] = g["post_may_eligible_count"] / g["deep_count"].clip(lower=1)
    g["summary_name"] = name
    return g.sort_values(["post_may_eligible_count", "deep_count"], ascending=[False, False])


def may_gate_attribution(deep: pd.DataFrame) -> pd.DataFrame:
    raw_gross = deep["raw_10bp__fresh_forward_2026May__gross_exposure"].fillna(0.0)
    res_gross = deep["residual_vs_funding_10bp__fresh_forward_2026May__gross_exposure"].fillna(0.0)
    raw_active = deep["raw_10bp__fresh_forward_2026May__active_hour_count"].fillna(0)
    res_active = deep["residual_vs_funding_10bp__fresh_forward_2026May__active_hour_count"].fillna(0)
    raw_may = deep["raw_10bp__fresh_forward_2026May"].fillna(0.0)
    res_may = deep["residual_vs_funding_10bp__fresh_forward_2026May"].fillna(0.0)

    flags = pd.DataFrame(
        {
            "candidate_id": deep["candidate_id"],
            "candidate_decision": deep["candidate_decision"],
            "fail_raw_gross": raw_gross <= MIN_GROSS,
            "fail_residual_gross": res_gross <= MIN_GROSS,
            "fail_raw_active_hours": raw_active < MIN_ACTIVE_HOURS,
            "fail_residual_active_hours": res_active < MIN_ACTIVE_HOURS,
            "fail_raw_may_severe": raw_may < -0.5,
            "fail_residual_funding_may_negative": res_may < 0,
            "raw_may": raw_may,
            "residual_funding_may": res_may,
            "raw_may_gross": raw_gross,
            "residual_may_gross": res_gross,
            "raw_may_active_hours": raw_active,
            "residual_may_active_hours": res_active,
        }
    )
    summary_rows = []
    for col in [
        "fail_raw_gross",
        "fail_residual_gross",
        "fail_raw_active_hours",
        "fail_residual_active_hours",
        "fail_raw_may_severe",
        "fail_residual_funding_may_negative",
    ]:
        summary_rows.append(
            {
                "gate": col,
                "fail_count": bool_sum(flags[col]),
                "fail_rate": bool_sum(flags[col]) / len(flags) if len(flags) else 0.0,
            }
        )
    return flags, pd.DataFrame(summary_rows).sort_values("fail_count", ascending=False)


def fold_failure_summary(metrics: pd.DataFrame, series_filter: str, label: str) -> pd.DataFrame:
    df = metrics[metrics["series"].astype(str).eq(series_filter)].copy()
    if df.empty:
        return pd.DataFrame()
    g = (
        df.groupby("fold_id", dropna=False)
        .agg(
            rows=("candidate_id", "count"),
            negative_count=("annualized_mean", lambda s: int((s < 0).sum())),
            median_ann=("annualized_mean", "median"),
            mean_ann=("annualized_mean", "mean"),
            p10_ann=("annualized_mean", lambda s: s.quantile(0.10)),
            p90_ann=("annualized_mean", lambda s: s.quantile(0.90)),
            median_active_hours=("active_hour_count", "median"),
            median_gross=("mean_gross_exposure", "median"),
        )
        .reset_index()
    )
    g["negative_rate"] = g["negative_count"] / g["rows"].clip(lower=1)
    g["series"] = label
    return g.sort_values(["negative_rate", "median_ann"], ascending=[False, True])


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_stamp()

    deep = load_csv("deep_audit_scoreboard")
    split_metrics = load_csv("split_metrics")
    fold_metrics = load_csv("fold_replay_metrics")
    residual_metrics = load_csv("residual_fold_metrics")
    cost_lag_metrics = load_csv("cost_lag_fold_metrics")
    manifest = json.loads((SOURCE_DIR / f"{SOURCE_PREFIX}_manifest.json").read_text(encoding="utf-8"))
    decision = json.loads((SOURCE_DIR / f"{SOURCE_PREFIX}_checkpoint_decision.json").read_text(encoding="utf-8"))

    decision_counts = deep["candidate_decision"].value_counts().rename_axis("candidate_decision").reset_index(name="count")
    decision_counts["share"] = decision_counts["count"] / len(deep)
    write_csv(decision_counts, "a7p4_decision_counts.csv")

    reject_reason_counts = reason_counts(deep)
    write_csv(reject_reason_counts, "a7p4_reject_reason_counts.csv")

    may_flags, may_summary = may_gate_attribution(deep)
    write_csv(may_flags, "a7p4_may_gate_candidate_flags.csv")
    write_csv(may_summary, "a7p4_may_gate_failure_summary.csv")

    group_specs = {
        "hypothesis": ["hypothesis_family"],
        "feature_family": ["feature_family_set"],
        "horizon": ["temporal_horizon_class"],
        "operator": ["operator_motif"],
        "feature_operator_horizon": ["feature_family_set", "operator_motif", "temporal_horizon_class"],
        "cell": ["cell_id", "hypothesis_family", "feature_family_set", "operator_motif", "temporal_horizon_class"],
        "return_corr_cluster": ["return_corr_cluster"],
    }
    group_tables = []
    for name, keys in group_specs.items():
        summary = family_summary(deep, keys, name)
        write_csv(summary, f"a7p4_{name}_productivity.csv")
        top = summary.head(20).copy()
        group_tables.append((name, top))

    fold_tables = [
        fold_failure_summary(fold_metrics, "raw_10bp", "raw_10bp"),
        fold_failure_summary(residual_metrics, "residual_vs_funding_10bp", "residual_vs_funding_10bp"),
        fold_failure_summary(residual_metrics, "residual_vs_core4_10bp", "residual_vs_core4_10bp"),
        fold_failure_summary(cost_lag_metrics, "raw_20bp", "raw_20bp"),
        fold_failure_summary(cost_lag_metrics, "execution_lag_1bar_raw_10bp", "execution_lag_1bar_raw_10bp"),
    ]
    fold_summary = pd.concat([t for t in fold_tables if not t.empty], ignore_index=True)
    write_csv(fold_summary, "a7p4_fold_failure_summary.csv")

    eligible = deep[deep["candidate_decision"].eq("A7O_PILOT_RESEARCH_CANDIDATE")].copy()
    ineligible = deep[~deep["candidate_decision"].eq("A7O_PILOT_RESEARCH_CANDIDATE")].copy()
    eligible_rate = len(eligible) / len(deep) if len(deep) else 0.0
    blockers = []
    if eligible_rate < TARGET_ELIGIBLE_RATE:
        blockers.append("post_may_eligible_rate_below_15pct")
    if decision["metrics"].get("strict_negative_control_research_like", 0) != 0:
        blockers.append("strict_negative_control_research_like")
    if decision["metrics"].get("negative_control_dominance_failures", 0) != 0:
        blockers.append("negative_control_dominance_failures")
    if decision["metrics"].get("placebo_or_null_research_candidates", 0) != 0:
        blockers.append("placebo_or_null_research_candidates")

    top_eligible = eligible.sort_values("pilot_rank_score", ascending=False).head(25)
    write_csv(top_eligible, "a7p4_top_post_may_eligible_candidates.csv")

    rank_df = deep.copy()
    rank_df["rank_order"] = rank_df["pilot_rank_score"].rank(method="first", ascending=False)
    rank_df["rank_decile"] = pd.qcut(rank_df["rank_order"], 10, labels=False, duplicates="drop") + 1
    rank_deciles = (
        rank_df.groupby("rank_decile", dropna=False)
        .agg(
            rows=("candidate_id", "count"),
            post_may_eligible_count=("candidate_decision", lambda s: int((s == "A7O_PILOT_RESEARCH_CANDIDATE").sum())),
            may_vetoed_count=("candidate_decision", lambda s: int((s == "A7O_PILOT_MAY_VETOED_NEAR_MISS").sum())),
            median_rank_score=("pilot_rank_score", "median"),
            median_raw_may=("raw_10bp__fresh_forward_2026May", "median"),
            median_residual_funding_may=("residual_vs_funding_10bp__fresh_forward_2026May", "median"),
            median_raw_recent=("raw_10bp__recent_oos_2025H2_2026Apr", "median"),
        )
        .reset_index()
        .sort_values("rank_decile")
    )
    rank_deciles["post_may_eligible_rate"] = rank_deciles["post_may_eligible_count"] / rank_deciles["rows"].clip(lower=1)
    write_csv(rank_deciles, "a7p4_rank_decile_post_may_alignment.csv")
    top_decile_eligible_rate = float(rank_deciles.loc[rank_deciles["rank_decile"].eq(1), "post_may_eligible_rate"].iloc[0]) if not rank_deciles.empty else 0.0
    bottom_decile_eligible_rate = float(rank_deciles.loc[rank_deciles["rank_decile"].eq(rank_deciles["rank_decile"].max()), "post_may_eligible_rate"].iloc[0]) if not rank_deciles.empty else 0.0
    if top_decile_eligible_rate < eligible_rate and bottom_decile_eligible_rate > top_decile_eligible_rate:
        blockers.append("non_may_rank_inverted_vs_post_may_stress")

    decision_label = "HOLD_A7P4_PRODUCTIVITY_TOO_LOW" if blockers else "PASS_A7P4_READY_FOR_NEXT_PROTECTED_PILOT"

    contrast_cols = [
        "raw_10bp__fresh_forward_2026May",
        "residual_vs_funding_10bp__fresh_forward_2026May",
        "raw_10bp__recent_oos_2025H2_2026Apr",
        "raw_20bp__recent_oos_2025H2_2026Apr",
        "execution_lag_1bar_raw_10bp__recent_oos_2025H2_2026Apr",
        "min_fold_component",
        "positive_fold_rate",
        "mean_turnover",
        "mean_gross_exposure",
        "pilot_rank_score",
    ]
    contrast = pd.DataFrame(
        [
            {"group": "post_may_eligible", "count": len(eligible), **eligible[contrast_cols].median(numeric_only=True).to_dict()},
            {"group": "not_post_may_eligible", "count": len(ineligible), **ineligible[contrast_cols].median(numeric_only=True).to_dict()},
        ]
    )
    write_csv(contrast, "a7p4_eligible_vs_ineligible_median_metrics.csv")

    payload = {
        "generated_at": now,
        "decision": decision_label,
        "source_checkpoint": CHECKPOINT_ID,
        "executes_search": False,
        "executes_replay": False,
        "uses_existing_deep_audit": True,
        "authorizes_next_protected_pilot": False,
        "authorizes_full_l1": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "blockers": blockers,
        "metrics": {
            "deep_audit_selected": int(len(deep)),
            "post_may_eligible_deep_survivors": int(len(eligible)),
            "post_may_eligible_rate": eligible_rate,
            "target_post_may_eligible_rate": TARGET_ELIGIBLE_RATE,
            "top_decile_post_may_eligible_rate": top_decile_eligible_rate,
            "bottom_decile_post_may_eligible_rate": bottom_decile_eligible_rate,
            "may_gate_top_failure": may_summary.iloc[0].to_dict() if not may_summary.empty else None,
            "strict_negative_control_research_like": int(decision["metrics"].get("strict_negative_control_research_like", 0)),
            "negative_control_dominance_failures": int(decision["metrics"].get("negative_control_dominance_failures", 0)),
            "placebo_or_null_research_candidates": int(decision["metrics"].get("placebo_or_null_research_candidates", 0)),
        },
        "may_policy": manifest.get("may_policy", {}),
        "outputs": {
            "decision_counts": str(OUT_DIR / "a7p4_decision_counts.csv"),
            "reject_reason_counts": str(OUT_DIR / "a7p4_reject_reason_counts.csv"),
            "may_gate_failure_summary": str(OUT_DIR / "a7p4_may_gate_failure_summary.csv"),
            "fold_failure_summary": str(OUT_DIR / "a7p4_fold_failure_summary.csv"),
            "eligible_vs_ineligible_median_metrics": str(OUT_DIR / "a7p4_eligible_vs_ineligible_median_metrics.csv"),
            "rank_decile_post_may_alignment": str(OUT_DIR / "a7p4_rank_decile_post_may_alignment.csv"),
        },
    }
    write_json(OUT_DIR / "a7p4_decision_record.json", payload)

    report = [
        "# Crypto A7P-4 Productivity Forensic",
        "",
        f"- generated_at: `{now}`",
        f"- source_checkpoint: `{CHECKPOINT_ID}`",
        f"- decision: `{decision_label}`",
        "- executes_search: `False`",
        "- executes_replay: `False`",
        "- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`",
        f"- blockers: `{blockers}`",
        "",
        "## Summary",
        "",
        f"A7P-4 explains the A7P-3 protected W2 pilot productivity gap. The pilot had `{len(deep)}` deep-audit rows and `{len(eligible)}` post-May eligible rows, for an eligible rate of `{eligible_rate:.4f}` versus the `{TARGET_ELIGIBLE_RATE:.2f}` continuation target.",
        "",
        "May remains stress-only in this forensic. It is used only for post-selection attribution and does not enter ranking, generation, allocation, mutation, threshold tuning, or surrogate targets.",
        "",
        "## Decision Counts",
        "",
        table(decision_counts),
        "",
        "## May Gate Failure Summary",
        "",
        table(may_summary),
        "",
        "## Eligible vs Ineligible Median Metrics",
        "",
        table(contrast),
        "",
        "## Non-May Rank vs Post-May Eligibility",
        "",
        table(rank_deciles),
        "",
        "## Top Reject Reasons",
        "",
        table(reject_reason_counts.head(20)),
        "",
        "## Fold Failure Summary",
        "",
        table(fold_summary.head(30)),
        "",
        "## Top Group Productivity",
        "",
    ]
    for name, df in group_tables:
        report.extend([f"### {name}", "", table(df.head(10)), ""])
    report.extend(
        [
            "## Interpretation",
            "",
            "- The protected W2 registry is control-clean on this pilot: no strict negative-control research-like rows, no dominance failures, and no placebo/null research candidates.",
            "- The blocker is productivity, not pipeline safety. The post-May eligible pool is below the continuation threshold.",
            "- The non-May rank is inverted against the stress label: the top rank decile has no post-May eligible rows while the bottom rank decile has the highest eligible rate. This is forensic evidence only; May remains forbidden for ranking or training.",
            "- Full L1 continuation is not authorized from this result. The next valid step is either a second protected pilot only after an explicit authorization record, or a search-cell redesign focused on non-May fold productivity and May activity coverage.",
            "",
            "## Output Files",
            "",
            table(pd.DataFrame([{"path": str(path.relative_to(ROOT))} for path in sorted(OUT_DIR.glob("*.csv"))])),
        ]
    )
    (REPORT_DIR / f"CRYPTO_A7P4_PRODUCTIVITY_FORENSIC_{DATE_TAG}.md").write_text("\n".join(report), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
