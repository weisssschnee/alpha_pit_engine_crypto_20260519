from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "runtime" / "a7al2v_replay_aware_selector_dryrun"
REPORT = REPO / "reports" / "CRYPTO_A7AL2V_REPLAY_AWARE_SELECTOR_DRYRUN_20260528.md"

A7AR7_POOL = REPO / "runtime" / "a7ar7_shared_candidate_pool" / "a7ar7_shared_candidate_pool.csv"
A7AR7_MANIFEST = REPO / "runtime" / "a7ar7_shared_candidate_pool" / "a7ar7_manifest.json"


PREMAY_FEATURES = [
    "q_label_t1_positive_premay_splits",
    "q_label_t2_positive_premay_splits",
    "q_one_bar_lag_positive_premay_splits",
    "q_timevarying_latent_positive_premay_splits",
    "q_net_10bps_positive_premay_splits",
    "q_control_ratio_premay_max_by_split",
    "q_recent_net_mean_spread_10bps",
    "q_recent_turnover",
    "q_recent_newey_west_tstat_lag24",
    "r_label_t1_positive_premay_splits",
    "r_label_t2_positive_premay_splits",
    "r_one_bar_lag_positive_premay_splits",
    "r_latent_positive_premay_splits",
    "r_net_10bps_positive_premay_splits",
    "r_control_ratio_premay_max",
    "r_top_symbol_abs_contribution_share",
    "r_top_month_abs_contribution_share",
    "r_top_latent_abs_contribution_share",
]

FORBIDDEN_SELECTOR_FEATURE_PATTERNS = [
    "may_",
    "known_may2026",
    "stress",
    "eligible_for_expansion",
    "alpha_proof",
    "shadow_ready",
    "paper_ready",
    "live_ready",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if pd.api.types.is_object_dtype(view[col]) or pd.api.types.is_string_dtype(view[col]):
            view[col] = view[col].astype(str).str.replace("|", r"\|", regex=False)
    try:
        return view.to_markdown(index=False)
    except Exception:
        return "```\n" + view.to_string(index=False) + "\n```"


def to_num(series: pd.Series, default: float = 0.0) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(default)


def minmax(series: pd.Series) -> pd.Series:
    values = to_num(series)
    lo = values.min()
    hi = values.max()
    if not np.isfinite(lo) or not np.isfinite(hi) or hi <= lo:
        return pd.Series(0.0, index=series.index)
    return (values - lo) / (hi - lo)


def forbidden_feature_audit(feature_columns: list[str]) -> pd.DataFrame:
    rows = []
    for col in feature_columns:
        hit = [pat for pat in FORBIDDEN_SELECTOR_FEATURE_PATTERNS if pat in col.lower()]
        rows.append({"feature": col, "forbidden_pattern_hit": "|".join(hit), "allowed_for_selector_score": not hit})
    return pd.DataFrame(rows)


def build_selector_matrix(pool: pd.DataFrame) -> pd.DataFrame:
    scored = pool[pool["in_a7al2q_fast_replay"].astype(str).str.lower().isin(["true", "1"])].copy()
    if scored.empty:
        return scored

    q_control = to_num(scored["q_control_ratio_premay_max_by_split"], default=9.0)
    r_control = to_num(scored.get("r_control_ratio_premay_max", pd.Series(index=scored.index)), default=np.nan)
    control_ratio = r_control.fillna(q_control)

    label_t1 = to_num(scored["q_label_t1_positive_premay_splits"])
    label_t2 = to_num(scored["q_label_t2_positive_premay_splits"])
    lag = to_num(scored["q_one_bar_lag_positive_premay_splits"])
    latent = to_num(scored["q_timevarying_latent_positive_premay_splits"])
    net10 = to_num(scored["q_net_10bps_positive_premay_splits"])
    robust = to_num(scored["q_recent_newey_west_tstat_lag24"])
    spread = to_num(scored["q_recent_net_mean_spread_10bps"])
    turnover = to_num(scored["q_recent_turnover"])

    r_label_t1 = to_num(scored.get("r_label_t1_positive_premay_splits", pd.Series(index=scored.index)))
    r_label_t2 = to_num(scored.get("r_label_t2_positive_premay_splits", pd.Series(index=scored.index)))
    r_lag = to_num(scored.get("r_one_bar_lag_positive_premay_splits", pd.Series(index=scored.index)))
    r_latent = to_num(scored.get("r_latent_positive_premay_splits", pd.Series(index=scored.index)))
    r_net10 = to_num(scored.get("r_net_10bps_positive_premay_splits", pd.Series(index=scored.index)))

    replay_alignment_score = (label_t1 + label_t2 + r_label_t1 + r_label_t2) / 12.0
    latency_survival_score = (lag + r_lag) / 6.0
    neutral_survival_score = (latent + r_latent) / 6.0
    cost_survival_score = (net10 + r_net10) / 6.0
    robust_stat_score = minmax(robust)
    spread_score = minmax(spread)
    turnover_penalty = minmax(turnover)
    control_penalty = control_ratio.clip(0.0, 2.0) / 2.0

    symbol_conc = to_num(scored.get("r_top_symbol_abs_contribution_share", pd.Series(index=scored.index)))
    month_conc = to_num(scored.get("r_top_month_abs_contribution_share", pd.Series(index=scored.index)))
    latent_conc = to_num(scored.get("r_top_latent_abs_contribution_share", pd.Series(index=scored.index)))
    concentration_penalty = pd.concat([symbol_conc, month_conc, latent_conc], axis=1).max(axis=1).fillna(0.0)

    scored["selector_feature_replay_alignment_score"] = replay_alignment_score
    scored["selector_feature_latency_survival_score"] = latency_survival_score
    scored["selector_feature_neutral_survival_score"] = neutral_survival_score
    scored["selector_feature_cost_survival_score"] = cost_survival_score
    scored["selector_feature_robust_stat_score"] = robust_stat_score
    scored["selector_feature_spread_score"] = spread_score
    scored["selector_feature_control_penalty"] = control_penalty
    scored["selector_feature_turnover_penalty"] = turnover_penalty
    scored["selector_feature_concentration_penalty"] = concentration_penalty

    scored["selector_hard_reject_reason"] = ""
    r_decision = scored.get("r_decision", pd.Series("", index=scored.index)).fillna("").astype(str)
    scored.loc[r_decision.str.startswith("HOLD_"), "selector_hard_reject_reason"] = "replay_forensic_hold"
    scored.loc[control_ratio >= 1.0, "selector_hard_reject_reason"] = "premay_control_dominated"
    scored.loc[(label_t1 < 2) | (label_t2 < 2), "selector_hard_reject_reason"] = scored["selector_hard_reject_reason"].where(
        scored["selector_hard_reject_reason"] != "", "entry_alignment_weak"
    )
    scored.loc[lag < 2, "selector_hard_reject_reason"] = scored["selector_hard_reject_reason"].where(
        scored["selector_hard_reject_reason"] != "", "one_bar_lag_weak"
    )
    scored.loc[net10 < 2, "selector_hard_reject_reason"] = scored["selector_hard_reject_reason"].where(
        scored["selector_hard_reject_reason"] != "", "cost10_weak"
    )

    scored["selector_score_no_may"] = (
        1.20 * scored["selector_feature_replay_alignment_score"]
        + 0.90 * scored["selector_feature_latency_survival_score"]
        + 0.90 * scored["selector_feature_neutral_survival_score"]
        + 0.90 * scored["selector_feature_cost_survival_score"]
        + 0.65 * scored["selector_feature_robust_stat_score"]
        + 0.65 * scored["selector_feature_spread_score"]
        - 1.40 * scored["selector_feature_control_penalty"]
        - 0.35 * scored["selector_feature_turnover_penalty"]
        - 0.50 * scored["selector_feature_concentration_penalty"]
    ).round(8)
    scored["selector_score_uses_may"] = False
    return scored


def select_with_caps(scored: pd.DataFrame, budget: int = 32) -> pd.DataFrame:
    if scored.empty:
        return scored
    candidates = scored[scored["selector_hard_reject_reason"].eq("")].copy()
    if candidates.empty:
        scored["selected_by_a7al2v"] = False
        return scored
    candidates = candidates.sort_values(["selector_score_no_may", "candidate_id"], ascending=[False, True])
    selected: list[str] = []
    skeleton_counts: dict[str, int] = {}
    production_counts: dict[str, int] = {}
    family_counts: dict[str, int] = {}
    for _, row in candidates.iterrows():
        cid = str(row["candidate_id"])
        skeleton = str(row.get("skeleton_key", ""))
        production = str(row.get("production_key", ""))
        family = str(row.get("field_families", ""))
        if skeleton_counts.get(skeleton, 0) >= 4:
            continue
        if production_counts.get(production, 0) >= 3:
            continue
        if family_counts.get(family, 0) >= 8:
            continue
        selected.append(cid)
        skeleton_counts[skeleton] = skeleton_counts.get(skeleton, 0) + 1
        production_counts[production] = production_counts.get(production, 0) + 1
        family_counts[family] = family_counts.get(family, 0) + 1
        if len(selected) >= budget:
            break
    scored["selected_by_a7al2v"] = scored["candidate_id"].astype(str).isin(selected)
    return scored


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if not A7AR7_POOL.exists():
        raise SystemExit(f"Missing A7AR-7 pool: {A7AR7_POOL}")

    a7ar7_manifest = read_json(A7AR7_MANIFEST)
    if not a7ar7_manifest.get("authorizes_a7al2v_selector_dryrun"):
        raise SystemExit("A7AR-7 does not authorize A7AL-2V")

    pool = pd.read_csv(A7AR7_POOL)
    selector_matrix = build_selector_matrix(pool)
    selector_matrix = select_with_caps(selector_matrix, budget=32)

    selector_features = [
        col for col in selector_matrix.columns if col.startswith("selector_feature_") or col == "selector_score_no_may"
    ]
    forbidden_audit = forbidden_feature_audit(selector_features)
    selected = selector_matrix[selector_matrix.get("selected_by_a7al2v", False).astype(bool)].copy()
    post_selection = selected[
        [
            "candidate_id",
            "selector_score_no_may",
            "selector_score_uses_may",
            "q_decision",
            "r_decision",
            "s_a7al2s_tier",
            "t_failure_labels",
            "t_may_sign_flip_rows",
            "t_may_control_dominated_rows",
            "t_may_min_spread",
            "is_may_stress_failed",
        ]
    ].copy()
    post_selection["post_selection_stress_status"] = np.where(
        post_selection["is_may_stress_failed"].astype(str).str.lower().isin(["true", "1"]),
        "MAY_STRESS_VETO",
        np.where(post_selection["t_failure_labels"].isna(), "MAY_STRESS_NOT_AVAILABLE", "MAY_STRESS_NOT_FAILED"),
    )

    reject_summary = (
        selector_matrix.assign(
            selector_hard_reject_reason=selector_matrix["selector_hard_reject_reason"].replace("", "eligible")
        )
        .groupby("selector_hard_reject_reason", as_index=False)
        .agg(candidate_count=("candidate_id", "count"))
        .sort_values("candidate_count", ascending=False)
    )

    selected_count = int(selected.shape[0])
    selected_with_may = post_selection[post_selection["post_selection_stress_status"].ne("MAY_STRESS_NOT_AVAILABLE")]
    stress_clean_selected = int(post_selection["post_selection_stress_status"].eq("MAY_STRESS_NOT_FAILED").sum())
    forbidden_overlap_count = int((~forbidden_audit["allowed_for_selector_score"]).sum())
    blockers = []
    if forbidden_overlap_count:
        blockers.append("forbidden_selector_feature_overlap")
    if selected_count == 0:
        blockers.append("no_selector_candidates")
    if selected_count and stress_clean_selected == 0 and not selected_with_may.empty:
        blockers.append("selected_pool_may_stress_veto")

    decision = "PASS_A7AL2V_REPLAY_AWARE_SELECTOR_DRYRUN_COMPLETE_EXECUTION_HOLD"
    if forbidden_overlap_count:
        decision = "HOLD_A7AL2V_FORBIDDEN_SELECTOR_FEATURES"
    elif selected_count == 0:
        decision = "HOLD_A7AL2V_NO_REPLAY_AWARE_SELECTION"
    elif "selected_pool_may_stress_veto" in blockers:
        decision = "HOLD_A7AL2V_SELECTED_POOL_STRESS_VETO_NO_EXPANSION"

    selector_matrix.to_csv(OUT_DIR / "a7al2v_selector_matrix.csv", index=False)
    selected.to_csv(OUT_DIR / "a7al2v_selected_pool.csv", index=False)
    post_selection.to_csv(OUT_DIR / "a7al2v_post_selection_stress_veto_audit.csv", index=False)
    reject_summary.to_csv(OUT_DIR / "a7al2v_reject_reason_summary.csv", index=False)
    forbidden_audit.to_csv(OUT_DIR / "a7al2v_forbidden_feature_audit.csv", index=False)

    authorization = pd.DataFrame(
        [
            {"action": "a7ar8_signal_vector_registry", "status": "AUTHORIZED" if not forbidden_overlap_count else "NOT_AUTHORIZED", "reason": "needed before larger replay selection"},
            {"action": "a7al2w_selector_repair_iteration", "status": "AUTHORIZED" if blockers else "OPTIONAL", "reason": "dry-run shows remaining blocker state"},
            {"action": "a7al2q_same_objective_rerun", "status": "NOT_AUTHORIZED", "reason": "same objective already failed May stress attribution"},
            {"action": "direct_oi_price_expansion", "status": "NOT_AUTHORIZED", "reason": "stress veto/control dominance unresolved"},
            {"action": "large_formula_search", "status": "NOT_AUTHORIZED", "reason": "replay-aware selector dry-run is not a search pass"},
            {"action": "alpha_proof_shadow_paper_live", "status": "NOT_AUTHORIZED", "reason": "no stress-clean selected pool"},
        ]
    )
    authorization.to_csv(OUT_DIR / "a7al2v_authorization_matrix.csv", index=False)

    manifest = {
        "generated_at": utc_now(),
        "decision": decision,
        "input_pool_candidates": int(pool.shape[0]),
        "selector_scored_candidates": int(selector_matrix.shape[0]),
        "selected_candidates": selected_count,
        "selected_with_may_stress_evidence": int(selected_with_may.shape[0]),
        "selected_stress_clean_candidates": stress_clean_selected,
        "forbidden_selector_feature_overlap_count": forbidden_overlap_count,
        "blockers": blockers,
        "executes_search": False,
        "executes_replay": False,
        "executes_training": False,
        "uses_may_for_selector_score": False,
        "uses_may_for_ranking": False,
        "uses_may_for_generation": False,
        "uses_may_for_veto_or_attribution": True,
        "authorizes_same_objective_rerun": False,
        "authorizes_direct_expansion": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(OUT_DIR / "a7al2v_manifest.json", manifest)

    report = f"""# CRYPTO A7AL-2V Replay-Aware Selector Dry-Run

Generated: {manifest["generated_at"]}

## Decision

```text
{manifest["decision"]}
```

This stage scores the existing A7AR-7 shared pool using non-May replay-aware selector features. It executes no generation, no replay, no training, and no proof.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Reject Summary

{md_table(reject_summary)}

## Selected Pool Stress Veto Audit

{md_table(post_selection, 40)}

## Forbidden Feature Audit

{md_table(forbidden_audit)}

## Authorization

{md_table(authorization)}

## Boundary

```text
Selector score:
  non-May replay alignment
  non-May control dominance
  non-May cost/latency
  non-May neutralization
  non-May robust statistics

May:
  post-selection veto / attribution only
  not used in score, ranking, generation, mutation, lane allocation, or training target

Not authorized:
  same objective rerun
  direct OI x price expansion
  large search
  alpha proof
  shadow / paper / live
```
"""
    REPORT.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
