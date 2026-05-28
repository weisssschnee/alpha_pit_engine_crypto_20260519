from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "runtime" / "a7ar8_signal_vector_cluster_registry"
REPORT = REPO / "reports" / "CRYPTO_A7AR8_SIGNAL_VECTOR_CLUSTER_REGISTRY_20260528.md"

Q_METRICS = REPO / "runtime" / "company_a7al2q2r_full_20260528" / "runtime" / "a7al2q_local_oi_price_formula_search" / "a7al2q_fast_replay_metrics.csv"
A7AR7_POOL = REPO / "runtime" / "a7ar7_shared_candidate_pool" / "a7ar7_shared_candidate_pool.csv"
A7AL2V_MATRIX = REPO / "runtime" / "a7al2v_replay_aware_selector_dryrun" / "a7al2v_selector_matrix.csv"
A7AL2V_SELECTED = REPO / "runtime" / "a7al2v_replay_aware_selector_dryrun" / "a7al2v_selected_pool.csv"
A7AL2V_MANIFEST = REPO / "runtime" / "a7al2v_replay_aware_selector_dryrun" / "a7al2v_manifest.json"

PREMAY_EVAL_SPLITS = ["validation_2025H1", "test_2025H2", "recent_oos_2026JanApr"]
VECTOR_METRICS = [
    "mean_oriented_spread",
    "net_mean_spread_10bps",
    "positive_rate",
    "avg_one_way_turnover",
    "hourly_tstat_naive",
]
CLUSTER_CORR_THRESHOLD = 0.95


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


def build_signal_vectors(metrics: pd.DataFrame) -> pd.DataFrame:
    premay = metrics[metrics["split"].isin(PREMAY_EVAL_SPLITS)].copy()
    premay["vector_key"] = (
        premay["variant"].astype(str)
        + "__"
        + premay["entry_label"].astype(str)
        + "__"
        + premay["split"].astype(str)
    )
    frames = []
    for metric in VECTOR_METRICS:
        part = premay.pivot_table(index="candidate_id", columns="vector_key", values=metric, aggfunc="mean")
        part.columns = [f"{metric}__{col}" for col in part.columns]
        frames.append(part)
    vectors = pd.concat(frames, axis=1).sort_index()
    vectors = vectors.replace([np.inf, -np.inf], np.nan)
    # Fill sparse metric gaps by column median. If a whole column is missing,
    # fill with zero so the registry remains deterministic.
    for col in vectors.columns:
        median = vectors[col].median(skipna=True)
        fill = float(median) if pd.notna(median) and np.isfinite(float(median)) else 0.0
        vectors[col] = vectors[col].fillna(fill)
    return vectors.reset_index()


def standardize_matrix(vectors: pd.DataFrame) -> np.ndarray:
    values = vectors.drop(columns=["candidate_id"]).to_numpy(dtype=float)
    means = np.nanmean(values, axis=0)
    stds = np.nanstd(values, axis=0)
    stds[~np.isfinite(stds) | (stds == 0.0)] = 1.0
    z = (values - means) / stds
    z[~np.isfinite(z)] = 0.0
    return z


def corr_matrix(z: np.ndarray) -> np.ndarray:
    if z.shape[0] == 0:
        return np.empty((0, 0))
    norms = np.linalg.norm(z, axis=1)
    norms[norms == 0.0] = 1.0
    zn = z / norms[:, None]
    corr = zn @ zn.T
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)
    return corr


def greedy_clusters(candidate_ids: list[str], corr: np.ndarray) -> dict[str, str]:
    remaining = set(range(len(candidate_ids)))
    assignments: dict[str, str] = {}
    cluster_index = 0
    while remaining:
        seed = min(remaining)
        members = sorted(i for i in remaining if corr[seed, i] >= CLUSTER_CORR_THRESHOLD)
        cluster_id = f"svc_{cluster_index:03d}"
        for idx in members:
            assignments[candidate_ids[idx]] = cluster_id
        remaining -= set(members)
        cluster_index += 1
    return assignments


def max_corr_to_other(candidate_ids: list[str], corr: np.ndarray) -> dict[str, float]:
    out: dict[str, float] = {}
    for i, cid in enumerate(candidate_ids):
        if len(candidate_ids) <= 1:
            out[cid] = 0.0
            continue
        row = np.delete(corr[i], i)
        out[cid] = float(np.nanmax(row)) if len(row) else 0.0
    return out


def selected_pairwise_audit(selected_ids: list[str], candidate_ids: list[str], corr: np.ndarray) -> pd.DataFrame:
    id_to_idx = {cid: idx for idx, cid in enumerate(candidate_ids)}
    rows = []
    for i, left in enumerate(selected_ids):
        for right in selected_ids[i + 1 :]:
            if left not in id_to_idx or right not in id_to_idx:
                continue
            rows.append(
                {
                    "left_candidate_id": left,
                    "right_candidate_id": right,
                    "signal_vector_corr": float(corr[id_to_idx[left], id_to_idx[right]]),
                    "above_0p95": bool(corr[id_to_idx[left], id_to_idx[right]] >= 0.95),
                    "above_0p90": bool(corr[id_to_idx[left], id_to_idx[right]] >= 0.90),
                }
            )
    return pd.DataFrame(rows)


def mode_value(series: pd.Series) -> str:
    values = series.dropna().astype(str)
    if values.empty:
        return ""
    return values.value_counts().index[0]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for path in [Q_METRICS, A7AR7_POOL, A7AL2V_MATRIX, A7AL2V_SELECTED, A7AL2V_MANIFEST]:
        require(path)

    a7al2v_manifest = read_json(A7AL2V_MANIFEST)
    metrics = pd.read_csv(Q_METRICS)
    pool = pd.read_csv(A7AR7_POOL)
    selector = pd.read_csv(A7AL2V_MATRIX)
    selected = pd.read_csv(A7AL2V_SELECTED)

    vectors = build_signal_vectors(metrics)
    candidate_ids = vectors["candidate_id"].astype(str).tolist()
    z = standardize_matrix(vectors)
    corr = corr_matrix(z)
    cluster_assignments = greedy_clusters(candidate_ids, corr)
    max_corr = max_corr_to_other(candidate_ids, corr)

    registry = vectors[["candidate_id"]].copy()
    registry["signal_vector_cluster_id"] = registry["candidate_id"].map(cluster_assignments)
    registry["max_corr_to_other_signal_vector"] = registry["candidate_id"].map(max_corr)
    registry = registry.merge(
        pool[
            [
                "candidate_id",
                "expression",
                "field_families",
                "skeleton_key",
                "production_key",
                "q_decision",
                "r_decision",
                "s_a7al2s_tier",
                "is_may_stress_failed",
            ]
        ],
        on="candidate_id",
        how="left",
    )
    registry = registry.merge(
        selector[["candidate_id", "selector_score_no_may", "selected_by_a7al2v"]],
        on="candidate_id",
        how="left",
    )
    registry["selected_by_a7al2v"] = registry["selected_by_a7al2v"].astype(str).str.lower().isin(["true", "1"])
    registry["uses_may_for_cluster"] = False

    cluster_summary = (
        registry.groupby("signal_vector_cluster_id", as_index=False)
        .agg(
            candidate_count=("candidate_id", "count"),
            selected_count=("selected_by_a7al2v", "sum"),
            forensic_pass_count=("r_decision", lambda x: int((x == "A7AL2R_LOCAL_FORENSIC_PASS").sum())),
            may_stress_failed_count=("is_may_stress_failed", lambda x: int(x.astype(str).str.lower().isin(["true", "1"]).sum())),
            top_field_family=("field_families", mode_value),
            top_skeleton_key=("skeleton_key", mode_value),
            top_production_key=("production_key", mode_value),
        )
        .sort_values(["selected_count", "candidate_count"], ascending=[False, False])
    )

    selected_ids = selected["candidate_id"].astype(str).tolist()
    selected_pairwise = selected_pairwise_audit(selected_ids, candidate_ids, corr)
    selected_registry = registry[registry["candidate_id"].isin(selected_ids)].copy()
    selected_cluster_count = int(selected_registry["signal_vector_cluster_id"].nunique())
    selected_count = int(selected_registry.shape[0])
    selected_top_cluster_share = (
        float(selected_registry["signal_vector_cluster_id"].value_counts(normalize=True).iloc[0])
        if selected_count
        else 0.0
    )
    selected_max_pairwise_corr = (
        float(selected_pairwise["signal_vector_corr"].max()) if not selected_pairwise.empty else 0.0
    )
    selected_same_cluster_pairs = int(
        selected_pairwise.merge(
            selected_registry[["candidate_id", "signal_vector_cluster_id"]].rename(
                columns={"candidate_id": "left_candidate_id", "signal_vector_cluster_id": "left_cluster"}
            ),
            on="left_candidate_id",
            how="left",
        )
        .merge(
            selected_registry[["candidate_id", "signal_vector_cluster_id"]].rename(
                columns={"candidate_id": "right_candidate_id", "signal_vector_cluster_id": "right_cluster"}
            ),
            on="right_candidate_id",
            how="left",
        )
        .query("left_cluster == right_cluster")
        .shape[0]
        if not selected_pairwise.empty
        else 0
    )

    selected_queue_audit = pd.DataFrame(
        [
            {
                "selected_count": selected_count,
                "selected_signal_vector_clusters": selected_cluster_count,
                "selected_top_cluster_share": selected_top_cluster_share,
                "selected_max_pairwise_corr": selected_max_pairwise_corr,
                "selected_same_cluster_pairs": selected_same_cluster_pairs,
                "selected_stress_clean_candidates": a7al2v_manifest.get("selected_stress_clean_candidates", 0),
                "uses_may_for_cluster": False,
            }
        ]
    )

    authorization = pd.DataFrame(
        [
            {"action": "a7al2w_objective_repair", "status": "AUTHORIZED", "reason": "selected queue is stress-vetoed; repair objective before any expansion"},
            {"action": "same_objective_rerun", "status": "NOT_AUTHORIZED", "reason": "A7AL-2V selected queue has zero stress-clean candidates"},
            {"action": "direct_oi_price_expansion", "status": "NOT_AUTHORIZED", "reason": "signal-vector registry does not repair May stress veto"},
            {"action": "large_formula_search", "status": "NOT_AUTHORIZED", "reason": "registry is diagnostic; no stress-clean selected pool"},
            {"action": "alpha_proof_shadow_paper_live", "status": "NOT_AUTHORIZED", "reason": "no candidate-level proof"},
        ]
    )

    blockers = []
    if selected_count == 0:
        blockers.append("no_selected_queue")
    if selected_cluster_count < min(selected_count, 2) and selected_count > 1:
        blockers.append("selected_queue_signal_cluster_concentrated")
    if selected_max_pairwise_corr >= 0.95 and selected_count > 1:
        blockers.append("selected_queue_pairwise_corr_high")
    if int(a7al2v_manifest.get("selected_stress_clean_candidates", 0) or 0) == 0 and selected_count > 0:
        blockers.append("selected_queue_may_stress_veto")

    decision = "PASS_A7AR8_SIGNAL_VECTOR_REGISTRY_READY_EXECUTION_HOLD"
    if "selected_queue_may_stress_veto" in blockers:
        decision = "HOLD_A7AR8_SELECTED_QUEUE_STRESS_VETO_NO_EXPANSION"
    elif blockers:
        decision = "HOLD_A7AR8_SELECTED_QUEUE_DIVERSITY_WEAK"

    vectors.to_csv(OUT_DIR / "a7ar8_signal_vectors.csv", index=False)
    registry.to_csv(OUT_DIR / "a7ar8_signal_cluster_registry.csv", index=False)
    cluster_summary.to_csv(OUT_DIR / "a7ar8_signal_cluster_summary.csv", index=False)
    selected_registry.to_csv(OUT_DIR / "a7ar8_selected_queue_registry.csv", index=False)
    selected_pairwise.to_csv(OUT_DIR / "a7ar8_selected_queue_pairwise_corr.csv", index=False)
    selected_queue_audit.to_csv(OUT_DIR / "a7ar8_selected_queue_diversity_audit.csv", index=False)
    authorization.to_csv(OUT_DIR / "a7ar8_authorization_matrix.csv", index=False)

    manifest = {
        "generated_at": utc_now(),
        "decision": decision,
        "candidate_vectors": int(vectors.shape[0]),
        "vector_feature_count": int(vectors.shape[1] - 1),
        "signal_vector_clusters": int(registry["signal_vector_cluster_id"].nunique()),
        "cluster_corr_threshold": CLUSTER_CORR_THRESHOLD,
        "selected_count": selected_count,
        "selected_signal_vector_clusters": selected_cluster_count,
        "selected_top_cluster_share": selected_top_cluster_share,
        "selected_max_pairwise_corr": selected_max_pairwise_corr,
        "selected_same_cluster_pairs": selected_same_cluster_pairs,
        "selected_stress_clean_candidates": int(a7al2v_manifest.get("selected_stress_clean_candidates", 0) or 0),
        "blockers": blockers,
        "executes_search": False,
        "executes_replay": False,
        "executes_training": False,
        "uses_may_for_cluster": False,
        "uses_may_for_selection": False,
        "uses_may_for_veto_or_attribution": True,
        "authorizes_same_objective_rerun": False,
        "authorizes_direct_expansion": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(OUT_DIR / "a7ar8_manifest.json", manifest)

    report = f"""# CRYPTO A7AR-8 Signal-Vector Cluster Registry

Generated: {manifest["generated_at"]}

## Decision

```text
{manifest["decision"]}
```

This stage builds a pre-May replay-behavior cluster registry. It executes no generation, no replay, no training, and no proof.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Selected Queue Diversity Audit

{md_table(selected_queue_audit)}

## Selected Queue Registry

{md_table(selected_registry[["candidate_id", "signal_vector_cluster_id", "max_corr_to_other_signal_vector", "selector_score_no_may", "r_decision", "s_a7al2s_tier", "is_may_stress_failed"]], 40)}

## Cluster Summary

{md_table(cluster_summary, 40)}

## Authorization

{md_table(authorization)}

## Boundary

```text
Cluster features:
  pre-May replay metrics only
  validation/test/recent splits only
  original and one-bar-lag variants
  label_t_to_t24 / label_t1_to_t25 / label_t2_to_t26 entries

May:
  not used for cluster construction
  not used for selector score
  retained only as post-selection veto / attribution

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
