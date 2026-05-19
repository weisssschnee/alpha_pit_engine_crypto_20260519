from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from crypto_a7_validation_utils import REPORT_DIR, RUNTIME_DIR, clean_float


A7I1B_DIR = RUNTIME_DIR / "a7i1b_matched_budget_smoke"
A7J1_DIR = RUNTIME_DIR / "a7j1_redesigned_runner_preflight"
A7J2_DIR = RUNTIME_DIR / "a7j2_same_budget_redesigned_smoke"
DATE_TAG = "20260520"
REPLAY_PER_ARM = 64
ARMS = ["I0_basis_premium", "I1_flow_liquidity", "I2_microstructure_lite", "I3_placebo_random"]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def safe(value: Any, default: float = 0.0) -> float:
    out = clean_float(value)
    return default if out is None else out


def clip(value: Any, cap: float = 2.0) -> float:
    return float(np.clip(safe(value), -cap, cap))


def pivot_metrics(long_df: pd.DataFrame) -> pd.DataFrame:
    parts = []
    for value_col in ["n", "annualized_mean", "compounded_max_dd", "mean_turnover", "mean_gross_exposure"]:
        p = long_df.pivot_table(index="candidate_id", columns=["series", "split"], values=value_col, aggfunc="first")
        p.columns = [f"{series}__{split}__{value_col}" for series, split in p.columns]
        parts.append(p)
    return pd.concat(parts, axis=1).reset_index()


def add_score_components(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    # Ranking terms intentionally exclude all May/fresh_forward columns.
    out["component_raw_validation"] = out["raw_10bp__validation_2025H1__annualized_mean"].map(clip)
    out["component_raw_recent"] = out["raw_10bp__recent_oos_2025H2_2026Apr__annualized_mean"].map(clip)
    out["component_residual_funding_validation"] = out[
        "residual_vs_funding_10bp__validation_2025H1__annualized_mean"
    ].map(clip)
    out["component_residual_funding_recent"] = out[
        "residual_vs_funding_10bp__recent_oos_2025H2_2026Apr__annualized_mean"
    ].map(clip)
    out["component_residual_core4_recent"] = out[
        "residual_vs_core4_10bp__recent_oos_2025H2_2026Apr__annualized_mean"
    ].map(clip)
    out["component_cost20_validation"] = out["raw_20bp__validation_2025H1__annualized_mean"].map(clip)
    out["component_cost20_recent"] = out["raw_20bp__recent_oos_2025H2_2026Apr__annualized_mean"].map(clip)
    out["component_lag1_validation"] = out[
        "execution_lag_1bar_raw_10bp__validation_2025H1__annualized_mean"
    ].map(clip)
    out["component_lag1_recent"] = out[
        "execution_lag_1bar_raw_10bp__recent_oos_2025H2_2026Apr__annualized_mean"
    ].map(clip)
    out["component_drawdown_penalty"] = out[
        "raw_10bp__recent_oos_2025H2_2026Apr__compounded_max_dd"
    ].fillna(0.0).clip(lower=-2.0, upper=0.0)
    out["component_turnover_penalty"] = -out[
        "raw_10bp__recent_oos_2025H2_2026Apr__mean_turnover"
    ].fillna(0.0).clip(lower=0.0, upper=2.0)
    out["component_funding_beta_penalty"] = -out["funding_beta_recent"].fillna(0.0).abs().clip(upper=1.0)
    out["component_core4_beta_penalty"] = -out["core4_beta_recent"].fillna(0.0).abs().clip(upper=1.0)
    out["a7j_rank_score"] = (
        0.7 * out["component_raw_validation"]
        + 0.9 * out["component_raw_recent"]
        + 0.9 * out["component_residual_funding_validation"]
        + 1.1 * out["component_residual_funding_recent"]
        + 0.8 * out["component_residual_core4_recent"]
        + 0.8 * out["component_cost20_validation"]
        + 1.2 * out["component_cost20_recent"]
        + 0.8 * out["component_lag1_validation"]
        + 1.2 * out["component_lag1_recent"]
        + 0.7 * out["component_drawdown_penalty"]
        + 0.5 * out["component_turnover_penalty"]
        + 0.7 * out["component_funding_beta_penalty"]
        + 0.7 * out["component_core4_beta_penalty"]
    )
    return out


def evaluate_candidate(row: pd.Series) -> tuple[str, list[str]]:
    if row["object_type"] == "placebo":
        return "NEGATIVE_CONTROL", ["placebo_arm"]
    reasons = []
    activity_checks = [
        ("raw_10bp__validation_2025H1__n", 250, "raw_validation_insufficient_n"),
        ("raw_10bp__recent_oos_2025H2_2026Apr__n", 250, "raw_recent_insufficient_n"),
        ("raw_10bp__fresh_forward_2026May__n", 24, "raw_may_insufficient_n"),
    ]
    for col, threshold, reason in activity_checks:
        if safe(row.get(col), default=0.0) < threshold:
            reasons.append(reason)
    exposure_checks = [
        ("raw_10bp__validation_2025H1__mean_gross_exposure", 0.10, "raw_validation_insufficient_gross_exposure"),
        ("raw_10bp__recent_oos_2025H2_2026Apr__mean_gross_exposure", 0.10, "raw_recent_insufficient_gross_exposure"),
    ]
    for col, threshold, reason in exposure_checks:
        if safe(row.get(col), default=0.0) < threshold:
            reasons.append(reason)
    checks = [
        ("raw_10bp__validation_2025H1__annualized_mean", 0.0, "raw_validation_nonpositive"),
        ("raw_10bp__recent_oos_2025H2_2026Apr__annualized_mean", 0.0, "raw_recent_nonpositive"),
        ("residual_vs_funding_10bp__validation_2025H1__annualized_mean", 0.0, "residual_funding_validation_nonpositive"),
        ("residual_vs_funding_10bp__recent_oos_2025H2_2026Apr__annualized_mean", 0.0, "residual_funding_recent_nonpositive"),
        ("residual_vs_core4_10bp__recent_oos_2025H2_2026Apr__annualized_mean", 0.0, "residual_core4_recent_nonpositive"),
        ("raw_20bp__recent_oos_2025H2_2026Apr__annualized_mean", 0.0, "cost20_recent_negative"),
        ("execution_lag_1bar_raw_10bp__recent_oos_2025H2_2026Apr__annualized_mean", 0.0, "lag1_recent_negative"),
    ]
    for col, threshold, reason in checks:
        if safe(row.get(col), default=-999.0) < threshold:
            reasons.append(reason)
    if abs(safe(row.get("funding_beta_recent"), 0.0)) >= 0.5:
        reasons.append("funding_beta_too_high")
    if abs(safe(row.get("core4_beta_recent"), 0.0)) >= 0.5:
        reasons.append("core4_beta_too_high")

    # May is stress-only: it is not in rank score, but it can veto a candidate label.
    raw_may = safe(row.get("raw_10bp__fresh_forward_2026May__annualized_mean"), default=-999.0)
    residual_may = safe(row.get("residual_vs_funding_10bp__fresh_forward_2026May__annualized_mean"), default=-999.0)
    if raw_may < -0.5:
        reasons.append("may_stress_severe_fail")
    elif raw_may < -0.25:
        reasons.append("may_stress_material_fail")
    if residual_may < 0:
        reasons.append("may_residual_funding_negative")

    if not reasons:
        return "A7J_RESEARCH_CANDIDATE", []
    if any(r in reasons for r in ["cost20_recent_negative", "lag1_recent_negative", "may_stress_severe_fail", "may_stress_material_fail"]):
        return "A7J_CLUE_ONLY", reasons
    return "REJECT_A7J_GATE_FAIL", reasons


def duplicate_audit(shortlist: pd.DataFrame) -> pd.DataFrame:
    rows = []
    total = max(1, len(shortlist))
    for family, count in Counter(shortlist["family"].tolist()).items():
        rows.append(
            {
                "bucket_type": "family",
                "bucket": family,
                "selected_count": count,
                "selected_share": count / total,
                "cap": 0.25 if total >= 4 else 1.0,
                "cap_pass": (count / total) <= (0.25 if total >= 4 else 1.0),
            }
        )
    for expr_hash, count in Counter(shortlist["expr_hash"].tolist()).items():
        rows.append(
            {
                "bucket_type": "formula_fingerprint",
                "bucket": expr_hash,
                "selected_count": count,
                "selected_share": count / total,
                "cap": 1 / total,
                "cap_pass": count == 1,
            }
        )
    return pd.DataFrame(rows)


def main() -> int:
    A7J2_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_now()

    preflight = json.loads((A7J1_DIR / f"crypto_a7j1_manifest_{DATE_TAG}.json").read_text(encoding="utf-8"))
    if not preflight.get("authorizes_a7j2"):
        raise RuntimeError("A7J-1 did not authorize A7J-2")

    scoreboard = pd.read_csv(A7I1B_DIR / "a7i1_candidate_scoreboard.csv")
    full_metric = pd.read_csv(A7I1B_DIR / "a7i1_full_metric_long.csv")
    beta = pd.read_csv(A7I1B_DIR / "a7i1_beta_corr_audit.csv")
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
    merged = scoreboard.drop(columns=["selected_for_replay"], errors="ignore").merge(wide, on="candidate_id", how="left")
    merged = merged.merge(beta_recent, on="candidate_id", how="left")
    ranked = add_score_components(merged)
    ranked["a7j_selected_for_replay"] = False
    for arm in ARMS:
        idx = ranked[ranked["arm"] == arm].sort_values(["a7j_rank_score", "candidate_id"], ascending=[False, True]).head(REPLAY_PER_ARM).index
        ranked.loc[idx, "a7j_selected_for_replay"] = True
    selected = ranked[ranked["a7j_selected_for_replay"]].copy()

    decisions = []
    for _, row in selected.iterrows():
        decision, reasons = evaluate_candidate(row)
        decisions.append({"candidate_id": row["candidate_id"], "candidate_decision": decision, "reject_reasons": ";".join(reasons)})
    decision_df = pd.DataFrame(decisions)
    selected_eval = selected.merge(decision_df, on="candidate_id", how="left")
    shortlist = selected_eval[selected_eval["candidate_decision"] == "A7J_RESEARCH_CANDIDATE"].copy()
    rejected = selected_eval[selected_eval["candidate_decision"] != "A7J_RESEARCH_CANDIDATE"].copy()
    placebo_research = shortlist[shortlist["arm"] == "I3_placebo_random"]
    non_placebo = shortlist[shortlist["arm"] != "I3_placebo_random"]
    non_flow = non_placebo[non_placebo["family"] != "flow_liquidity"]
    duplicate = duplicate_audit(shortlist)
    duplicate_cap_pass = bool(duplicate["cap_pass"].all()) if not duplicate.empty else True

    may_label = selected_eval[
        [
            "candidate_id",
            "arm",
            "candidate_decision",
            "raw_10bp__fresh_forward_2026May__annualized_mean",
            "residual_vs_funding_10bp__fresh_forward_2026May__annualized_mean",
            "reject_reasons",
        ]
    ].copy()
    may_label["may_used_for_ranking"] = False
    may_label["may_used_for_selection"] = False

    scoreboard_path = A7J2_DIR / "a7j2_candidate_scoreboard.csv"
    selected_path = A7J2_DIR / "a7j2_selected_candidates.csv"
    shortlist_path = A7J2_DIR / "a7j2_research_candidate_shortlist.csv"
    rejected_path = A7J2_DIR / "a7j2_rejected_candidate_reasons.csv"
    may_path = A7J2_DIR / "a7j2_may_stress_label_audit.csv"
    duplicate_path = A7J2_DIR / "a7j2_duplicate_family_audit.csv"
    score_component_path = A7J2_DIR / "a7j2_reward_score_components.csv"

    ranked.to_csv(scoreboard_path, index=False)
    selected_eval.to_csv(selected_path, index=False)
    shortlist.to_csv(shortlist_path, index=False)
    rejected.to_csv(rejected_path, index=False)
    may_label.to_csv(may_path, index=False)
    duplicate.to_csv(duplicate_path, index=False)
    component_cols = ["candidate_id", "arm", "family", "object_type", "a7j_rank_score"] + [c for c in ranked.columns if c.startswith("component_")]
    ranked[component_cols].to_csv(score_component_path, index=False)

    blockers = []
    if len(non_placebo) < 2:
        blockers.append("fewer_than_2_non_placebo_research_candidates")
    if len(placebo_research) > 0:
        blockers.append("placebo_research_candidate_nonzero")
    if len(non_flow) < 1:
        blockers.append("no_non_flow_non_taker_research_candidate")
    if not duplicate_cap_pass:
        blockers.append("duplicate_family_or_formula_cap_fail")
    if any(may_label["may_used_for_ranking"]) or any(may_label["may_used_for_selection"]):
        blockers.append("may_used_for_ranking_or_selection")

    decision = "PASS_A7J2_METHOD_SMOKE" if not blockers else (
        "HOLD_A7J2_INSUFFICIENT_RESEARCH_CANDIDATES" if "fewer_than_2_non_placebo_research_candidates" in blockers else "HOLD_A7J2_METHOD_SMOKE_BLOCKED"
    )

    arm_summary = (
        selected_eval.groupby("arm", as_index=False)
        .agg(
            generated_count=("candidate_id", lambda x: int((ranked["arm"] == x.name).sum()) if False else len(x)),
            selected_count=("candidate_id", "size"),
            research_candidate_count=("candidate_decision", lambda x: int((x == "A7J_RESEARCH_CANDIDATE").sum())),
            clue_only_count=("candidate_decision", lambda x: int((x == "A7J_CLUE_ONLY").sum())),
        )
    )
    # Correct generated counts explicitly.
    arm_summary["generated_count"] = arm_summary["arm"].map(ranked.groupby("arm").size().to_dict())

    comparison = pd.DataFrame(
        [
            {"metric": "non_placebo_research_candidate_count", "value": int(len(non_placebo))},
            {"metric": "placebo_research_candidate_count", "value": int(len(placebo_research))},
            {"metric": "non_flow_research_candidate_count", "value": int(len(non_flow))},
            {"metric": "duplicate_cap_pass", "value": bool(duplicate_cap_pass)},
        ]
    )
    arm_summary_path = A7J2_DIR / "a7j2_arm_summary.csv"
    comparison_path = A7J2_DIR / "a7j2_pass_fail_comparison.csv"
    arm_summary.to_csv(arm_summary_path, index=False)
    comparison.to_csv(comparison_path, index=False)

    manifest = {
        "generated_at": now,
        "decision": decision,
        "alpha_proof_status": "NOT_ALPHA_PROOF",
        "executes_new_generation": False,
        "candidate_pool_source": "A7I1B frozen 1000-candidate pool",
        "same_budget": {"arms": 4, "generated_per_arm": 250, "selected_per_arm": 64},
        "blockers": blockers,
        "research_candidate_count": int(len(non_placebo)),
        "placebo_research_candidate_count": int(len(placebo_research)),
        "non_flow_research_candidate_count": int(len(non_flow)),
        "may_boundary": {"may_used_for_ranking": False, "may_used_for_selection": False, "may_stress_only": True},
        "outputs": {
            "candidate_scoreboard": str(scoreboard_path),
            "selected_candidates": str(selected_path),
            "research_candidate_shortlist": str(shortlist_path),
            "rejected_candidate_reasons": str(rejected_path),
            "may_stress_label_audit": str(may_path),
            "duplicate_family_audit": str(duplicate_path),
            "reward_score_components": str(score_component_path),
            "arm_summary": str(arm_summary_path),
            "pass_fail_comparison": str(comparison_path),
        },
    }
    manifest_path = A7J2_DIR / f"crypto_a7j2_manifest_{DATE_TAG}.json"
    write_json(manifest_path, manifest)

    report_path = REPORT_DIR / f"CRYPTO_A7J2_SAME_BUDGET_REDESIGNED_SMOKE_{DATE_TAG}.md"
    lines = [
        "# Crypto A7J-2 Same-Budget Redesigned Generator Smoke",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{decision}`",
        "- evidence_level: `method_smoke_not_alpha_proof`",
        "- candidate_pool_source: `A7I1B frozen 1000-candidate pool`",
        "- generated_per_arm: `250`",
        "- selected_per_arm: `64`",
        "- may_used_for_ranking: `False`",
        "- may_used_for_selection: `False`",
        "- authorizes_alpha_proof: `False`",
        f"- blockers: `{blockers}`",
        "",
        "## Arm Summary",
        "",
        "| arm | generated | selected | research | clue_only |",
        "|---|---:|---:|---:|---:|",
    ]
    for _, row in arm_summary.iterrows():
        lines.append(
            f"| `{row['arm']}` | {int(row['generated_count'])} | {int(row['selected_count'])} | "
            f"{int(row['research_candidate_count'])} | {int(row['clue_only_count'])} |"
        )
    lines += [
        "",
        "## Research Candidate Shortlist",
        "",
    ]
    if shortlist.empty:
        lines.append("- none")
    else:
        lines += ["| candidate | arm | family | expression | raw recent | cost20 recent | lag recent | May stress |", "|---|---|---|---|---:|---:|---:|---:|"]
        for _, row in shortlist.iterrows():
            lines.append(
                f"| `{row['candidate_id']}` | `{row['arm']}` | `{row['family']}` | `{row['expression']}` | "
                f"{safe(row['raw_10bp__recent_oos_2025H2_2026Apr__annualized_mean']):.4f} | "
                f"{safe(row['raw_20bp__recent_oos_2025H2_2026Apr__annualized_mean']):.4f} | "
                f"{safe(row['execution_lag_1bar_raw_10bp__recent_oos_2025H2_2026Apr__annualized_mean']):.4f} | "
                f"{safe(row['raw_10bp__fresh_forward_2026May__annualized_mean']):.4f} |"
            )
    lines += [
        "",
        "## Boundary",
        "",
        "- A7J-2 uses the redesigned reward on the frozen A7I candidate pool; no budget expansion.",
        "- May is stress-only and did not enter score or selection.",
        "- PASS would only be method smoke, not alpha proof. Current decision remains bounded by blockers above.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    decision_path = REPORT_DIR / f"CRYPTO_A7J2_DECISION_RECORD_{DATE_TAG}.md"
    decision_path.write_text(
        "\n".join(
            [
                "# Crypto A7J-2 Decision Record",
                "",
                f"- decision: `{decision}`",
                "- alpha_proof_status: `NOT_ALPHA_PROOF`",
                f"- blockers: `{blockers}`",
                f"- research_candidate_count: `{int(len(non_placebo))}`",
                f"- placebo_research_candidate_count: `{int(len(placebo_research))}`",
                "",
                "A7J-2 reranked the frozen A7I candidate pool with the redesigned reward. It does not authorize shadow, paper, live, or production.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print("A7J2_REPORT=" + str(report_path))
    print("A7J2_DECISION_RECORD=" + str(decision_path))
    print("A7J2_MANIFEST=" + str(manifest_path))
    print("DECISION=" + decision)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
