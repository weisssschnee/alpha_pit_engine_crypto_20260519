from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "runtime" / "a7al2x1_dry_rerank"
REPORT = REPO / "reports" / "CRYPTO_A7AL2X1_DRY_RERANK_20260529.md"

A7AL2X_MANIFEST = REPO / "runtime" / "a7al2x_objective_family_reset" / "a7al2x_manifest.json"
A7AL2X_ALLOWED = REPO / "runtime" / "a7al2x_objective_family_reset" / "a7al2x_allowed_objective_families.csv"
A7AR7_POOL = REPO / "runtime" / "a7ar7_shared_candidate_pool" / "a7ar7_shared_candidate_pool.csv"
A7AR8_REGISTRY = REPO / "runtime" / "a7ar8_signal_vector_cluster_registry" / "a7ar8_signal_cluster_registry.csv"
A7AR8_VECTORS = REPO / "runtime" / "a7ar8_signal_vector_cluster_registry" / "a7ar8_signal_vectors.csv"

TARGET_SELECTED = 8
PAIRWISE_CORR_CAP = 0.80

DIRECT_WEAK_PRIOR_PATTERNS = {
    "abs_level_gap",
    "level_spread",
    "rank_level_spread",
    "oi_rank_x_neg_price_rank",
}

F0_PATTERNS = {
    "oi_delta_x_price_delta",
    "oi_delta_x_price_level",
    "oi_delta_plus_neg_price_level",
    "delta_spread",
    "rank_delta_spread",
    "abs_delta_gap",
    "oi_abs_delta_x_price_abs",
    "oi_delta_rank_x_price_rank",
}


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


def require(path: Path) -> None:
    if not path.exists():
        raise SystemExit(f"Missing required artifact: {path}")


def to_num(series: pd.Series, default: float = 0.0) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(default)


def objective_family(row: pd.Series) -> tuple[str, str]:
    pattern = str(row.get("pattern_id", ""))
    fields = str(row.get("fields", "")).lower()
    families = str(row.get("field_families", "")).lower()
    text = f"{pattern}|{fields}|{families}"

    if pattern in DIRECT_WEAK_PRIOR_PATTERNS:
        return "DIRECT_OI_PRICE_WEAK_PRIOR", "direct OI x price is weak prior only"
    if pattern in F0_PATTERNS:
        return "F0_OI_delta_price_interaction", "OI/price delta interaction represented in existing pool"
    if "premium" in text or "basis" in text:
        return "F1_OI_basis_premium_interaction", "basis/premium interaction"
    if "funding" in text:
        return "F2_OI_funding_crowding_interaction", "funding crowding interaction"
    if "long_short" in text or "position" in text:
        return "F3_positioning_divergence", "positioning divergence"
    if "taker" in text:
        return "F4_OI_taker_flow_interaction", "taker flow interaction"
    if "regime" in text or "stress_proxy" in text or "breadth" in text:
        return "F5_OI_upper_regime_interaction", "upper regime interaction"
    if "latent" in text or "meme" in text or "liquidity_tier" in text:
        return "F6_OI_latent_state_interaction", "latent state interaction"
    return "UNMAPPED_OR_FORBIDDEN", "not in A7AL-2X allowed objective families"


def standardize(values: np.ndarray) -> np.ndarray:
    means = np.nanmean(values, axis=0)
    stds = np.nanstd(values, axis=0)
    stds[~np.isfinite(stds) | (stds == 0.0)] = 1.0
    z = (values - means) / stds
    z[~np.isfinite(z)] = 0.0
    return z


def corr_lookup(vectors: pd.DataFrame) -> tuple[dict[str, int], np.ndarray]:
    ids = vectors["candidate_id"].astype(str).tolist()
    values = vectors.drop(columns=["candidate_id"]).to_numpy(dtype=float)
    z = standardize(values)
    norms = np.linalg.norm(z, axis=1)
    norms[norms == 0.0] = 1.0
    zn = z / norms[:, None]
    corr = np.clip(zn @ zn.T, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)
    return {cid: idx for idx, cid in enumerate(ids)}, corr


def max_corr(candidate_id: str, selected: list[str], id_to_idx: dict[str, int], corr: np.ndarray) -> float:
    if not selected or candidate_id not in id_to_idx:
        return 0.0
    idx = id_to_idx[candidate_id]
    values = [float(corr[idx, id_to_idx[sid]]) for sid in selected if sid in id_to_idx]
    return max(values) if values else 0.0


def build_trace(pool: pd.DataFrame, registry: pd.DataFrame) -> pd.DataFrame:
    merged = pool.merge(
        registry[["candidate_id", "signal_vector_cluster_id", "max_corr_to_other_signal_vector"]],
        on="candidate_id",
        how="left",
    )
    families = merged.apply(objective_family, axis=1, result_type="expand")
    merged["a7al2x_objective_family"] = families[0]
    merged["a7al2x_family_reason"] = families[1]

    q_control = to_num(merged.get("q_control_ratio_premay_max_by_split", pd.Series(index=merged.index)), default=9.0)
    r_control = to_num(merged.get("r_control_ratio_premay_max", pd.Series(index=merged.index)), default=np.nan)
    merged["x1_control_ratio"] = r_control.fillna(q_control)
    merged["x1_reject_reason"] = ""
    merged.loc[~merged["in_a7al2q_fast_replay"].astype(str).str.lower().isin(["true", "1"]), "x1_reject_reason"] = "not_fast_replay_scored"
    merged.loc[merged["a7al2x_objective_family"].eq("DIRECT_OI_PRICE_WEAK_PRIOR"), "x1_reject_reason"] = "direct_oi_price_weak_prior_not_standalone"
    merged.loc[merged["a7al2x_objective_family"].eq("UNMAPPED_OR_FORBIDDEN"), "x1_reject_reason"] = "objective_family_not_allowed"
    merged.loc[merged["x1_control_ratio"] >= 1.0, "x1_reject_reason"] = "matched_control_dominated"
    r_decision = merged.get("r_decision", pd.Series("", index=merged.index)).fillna("").astype(str)
    merged.loc[r_decision.str.contains("LATENT_FRAGILE", case=False, na=False), "x1_reject_reason"] = "timevarying_latent_fragile"
    merged.loc[r_decision.str.contains("CONTROL_DOMINATED", case=False, na=False), "x1_reject_reason"] = "forensic_control_dominated"

    label = to_num(merged.get("q_label_t1_positive_premay_splits", pd.Series(index=merged.index))) + to_num(
        merged.get("q_label_t2_positive_premay_splits", pd.Series(index=merged.index))
    )
    lag = to_num(merged.get("q_one_bar_lag_positive_premay_splits", pd.Series(index=merged.index)))
    latent = to_num(merged.get("q_timevarying_latent_positive_premay_splits", pd.Series(index=merged.index)))
    cost = to_num(merged.get("q_net_10bps_positive_premay_splits", pd.Series(index=merged.index)))
    spread = to_num(merged.get("q_recent_net_mean_spread_10bps", pd.Series(index=merged.index)))
    tstat = to_num(merged.get("q_recent_newey_west_tstat_lag24", pd.Series(index=merged.index)))
    control_penalty = merged["x1_control_ratio"].clip(0.0, 2.0)
    merged["x1_selector_score_no_may"] = (
        0.30 * label
        + 0.25 * lag
        + 0.25 * latent
        + 0.25 * cost
        + 200.0 * spread
        + 0.10 * tstat
        - 0.80 * control_penalty
    ).round(8)
    merged["x1_selector_uses_may"] = False
    return merged


def select_queue(trace: pd.DataFrame, id_to_idx: dict[str, int], corr: np.ndarray) -> pd.DataFrame:
    eligible = trace[trace["x1_reject_reason"].eq("")].copy()
    if eligible.empty:
        trace["selected_by_a7al2x1"] = False
        trace["x1_queue_reason"] = np.where(trace["x1_reject_reason"].eq(""), "eligible_not_selected", trace["x1_reject_reason"])
        return trace

    eligible = eligible.sort_values(["x1_selector_score_no_may", "candidate_id"], ascending=[False, True])
    selected: list[str] = []
    clusters: set[str] = set()
    reasons: dict[str, str] = {}
    for _, row in eligible.iterrows():
        cid = str(row["candidate_id"])
        cluster = str(row.get("signal_vector_cluster_id", ""))
        if cluster and cluster in clusters:
            reasons[cid] = "skip_same_signal_vector_cluster"
            continue
        if max_corr(cid, selected, id_to_idx, corr) > PAIRWISE_CORR_CAP:
            reasons[cid] = "skip_pairwise_corr_cap"
            continue
        selected.append(cid)
        if cluster:
            clusters.add(cluster)
        reasons[cid] = "selected"
        if len(selected) >= TARGET_SELECTED:
            break
    trace["selected_by_a7al2x1"] = trace["candidate_id"].astype(str).isin(selected)
    trace["x1_queue_reason"] = trace["candidate_id"].astype(str).map(reasons).fillna(
        np.where(trace["x1_reject_reason"].eq(""), "eligible_not_selected", trace["x1_reject_reason"])
    )
    return trace


def pairwise(selected: pd.DataFrame, id_to_idx: dict[str, int], corr: np.ndarray) -> pd.DataFrame:
    ids = selected["candidate_id"].astype(str).tolist()
    rows = []
    for i, left in enumerate(ids):
        for right in ids[i + 1 :]:
            if left not in id_to_idx or right not in id_to_idx:
                continue
            c = float(corr[id_to_idx[left], id_to_idx[right]])
            rows.append({"left_candidate_id": left, "right_candidate_id": right, "signal_vector_corr": c, "above_0p80": bool(c > 0.80)})
    return pd.DataFrame(rows)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for path in [A7AL2X_MANIFEST, A7AL2X_ALLOWED, A7AR7_POOL, A7AR8_REGISTRY, A7AR8_VECTORS]:
        require(path)

    x_manifest = read_json(A7AL2X_MANIFEST)
    if not x_manifest.get("authorizes_a7al2x1_dry_rerank"):
        raise SystemExit("A7AL-2X does not authorize A7AL-2X1")

    pool = pd.read_csv(A7AR7_POOL)
    registry = pd.read_csv(A7AR8_REGISTRY)
    vectors = pd.read_csv(A7AR8_VECTORS)
    id_to_idx, corr = corr_lookup(vectors)
    trace = build_trace(pool, registry)
    trace = select_queue(trace, id_to_idx, corr)
    selected = trace[trace["selected_by_a7al2x1"]].copy()
    pairwise_corr = pairwise(selected, id_to_idx, corr)

    family_counts = (
        trace[trace["in_a7al2q_fast_replay"].astype(str).str.lower().isin(["true", "1"])]
        .groupby(["a7al2x_objective_family", "x1_reject_reason"], dropna=False, as_index=False)
        .agg(candidate_count=("candidate_id", "count"))
        .sort_values("candidate_count", ascending=False)
    )
    reject_summary = (
        trace.groupby("x1_queue_reason", as_index=False)
        .agg(candidate_count=("candidate_id", "count"))
        .sort_values("candidate_count", ascending=False)
    )

    selected_count = int(selected.shape[0])
    selected_clusters = int(selected["signal_vector_cluster_id"].nunique()) if selected_count else 0
    selected_max_corr = float(pairwise_corr["signal_vector_corr"].max()) if not pairwise_corr.empty else 0.0
    selected_control_dominated = int((selected["x1_control_ratio"] >= 1.0).sum()) if selected_count else 0
    selected_latent_fragile = int(selected["r_decision"].fillna("").astype(str).str.contains("LATENT_FRAGILE", case=False).sum()) if selected_count else 0
    selected_with_stress = selected[selected["in_a7al2t_may_attribution"].astype(str).str.lower().isin(["true", "1"])]
    selected_stress_clean = int((~selected_with_stress["is_may_stress_failed"].astype(str).str.lower().isin(["true", "1"])).sum()) if not selected_with_stress.empty else 0

    diversity_audit = pd.DataFrame(
        [
            {
                "selected_count": selected_count,
                "selected_signal_vector_clusters": selected_clusters,
                "selected_max_pairwise_corr": selected_max_corr,
                "selected_control_dominated": selected_control_dominated,
                "selected_latent_fragile": selected_latent_fragile,
                "selected_with_stress_evidence": int(selected_with_stress.shape[0]),
                "selected_stress_clean_candidates": selected_stress_clean,
                "uses_may_for_selector": False,
            }
        ]
    )
    control_audit = selected[["candidate_id", "x1_control_ratio", "r_decision", "q_decision", "x1_queue_reason"]].copy() if selected_count else pd.DataFrame(columns=["candidate_id", "x1_control_ratio", "r_decision", "q_decision", "x1_queue_reason"])
    stress_summary = selected[["candidate_id", "a7al2x_objective_family", "in_a7al2t_may_attribution", "is_may_stress_failed", "t_failure_labels", "t_may_min_spread"]].copy() if selected_count else pd.DataFrame(columns=["candidate_id", "a7al2x_objective_family", "in_a7al2t_may_attribution", "is_may_stress_failed", "t_failure_labels", "t_may_min_spread"])

    blockers = []
    if selected_count < 4:
        blockers.append("selected_count_below_4")
    if selected_clusters < min(selected_count, 4):
        blockers.append("selected_signal_vector_clusters_below_requirement")
    if selected_max_corr > PAIRWISE_CORR_CAP:
        blockers.append("selected_pairwise_corr_above_0p80")
    if selected_control_dominated:
        blockers.append("selected_control_dominated")
    if selected_latent_fragile:
        blockers.append("selected_latent_fragile")
    if selected_stress_clean <= 0:
        blockers.append("selected_stress_clean_candidates_zero")

    if selected_count == 0:
        decision = "HOLD_A7AL2X1_NO_ELIGIBLE_ALLOWED_OBJECTIVE_FAMILY_IN_SHARED_POOL"
    elif selected_stress_clean <= 0:
        decision = "HOLD_A7AL2X1_NO_STRESS_CLEAN_SELECTED_CANDIDATES"
    elif blockers:
        decision = "HOLD_A7AL2X1_DRY_RERANK_GATES_FAIL"
    else:
        decision = "PASS_A7AL2X1_DRY_RERANK_FOUND_EXPANDABLE_EVIDENCE"

    authorization = {
        "decision": decision,
        "a7al2y_generation": "NOT_AUTHORIZED",
        "large_formula_search": "NOT_AUTHORIZED",
        "alpha_proof": "NOT_AUTHORIZED",
        "shadow_paper_live": "NOT_AUTHORIZED",
        "reason": "A7AL-2X1 is dry rerank only; generation requires stress-clean selected evidence, which is absent.",
    }

    trace.to_csv(OUT_DIR / "a7al2x1_selector_trace.csv", index=False)
    selected.to_csv(OUT_DIR / "a7al2x1_selected_queue.csv", index=False)
    diversity_audit.to_csv(OUT_DIR / "a7al2x1_signal_vector_diversity_audit.csv", index=False)
    control_audit.to_csv(OUT_DIR / "a7al2x1_control_dominance_audit.csv", index=False)
    stress_summary.to_csv(OUT_DIR / "a7al2x1_stress_veto_summary.csv", index=False)
    family_counts.to_csv(OUT_DIR / "a7al2x1_objective_family_funnel.csv", index=False)
    reject_summary.to_csv(OUT_DIR / "a7al2x1_reject_reason_summary.csv", index=False)
    pairwise_corr.to_csv(OUT_DIR / "a7al2x1_selected_pairwise_corr.csv", index=False)
    write_json(OUT_DIR / "a7al2x1_decision_record.json", authorization)

    manifest = {
        "generated_at": utc_now(),
        "decision": decision,
        "input_pool_candidates": int(pool.shape[0]),
        "fast_replay_candidates": int(trace["in_a7al2q_fast_replay"].astype(str).str.lower().isin(["true", "1"]).sum()),
        "eligible_allowed_family_candidates": int(trace["x1_reject_reason"].eq("").sum()),
        "selected_count": selected_count,
        "selected_signal_vector_clusters": selected_clusters,
        "selected_max_pairwise_corr": selected_max_corr,
        "selected_control_dominated": selected_control_dominated,
        "selected_latent_fragile": selected_latent_fragile,
        "selected_with_stress_evidence": int(selected_with_stress.shape[0]),
        "selected_stress_clean_candidates": selected_stress_clean,
        "blockers": blockers,
        "executes_search": False,
        "executes_replay": False,
        "executes_training": False,
        "uses_may_for_selector": False,
        "uses_may_for_generation": False,
        "uses_may_for_veto_or_attribution": True,
        "authorizes_a7al2y_generation": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(OUT_DIR / "a7al2x1_manifest.json", manifest)

    report = f"""# CRYPTO A7AL-2X1 Dry Rerank

Generated: {manifest["generated_at"]}

## Decision

```text
{manifest["decision"]}
```

This stage dry-reranks the existing A7AR-7 shared pool under the A7AL-2X objective-family reset contract. It executes no generation, no replay, no training, and no proof.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Objective Family Funnel

{md_table(family_counts, 80)}

## Selected Queue

{md_table(selected[["candidate_id", "a7al2x_objective_family", "x1_selector_score_no_may", "signal_vector_cluster_id", "x1_control_ratio", "r_decision", "is_may_stress_failed", "x1_queue_reason"]], 40) if selected_count else "`<empty>`"}

## Signal-Vector Diversity Audit

{md_table(diversity_audit)}

## Control Dominance Audit

{md_table(control_audit, 40)}

## Stress Veto Summary

{md_table(stress_summary, 40)}

## Authorization

```json
{json.dumps(authorization, indent=2, sort_keys=True)}
```

## Boundary

```text
No generation.
No replay.
No search.
No May in selector score.
May is post-selection veto / attribution only.
```
"""
    REPORT.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
