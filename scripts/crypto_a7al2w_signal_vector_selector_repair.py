from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "runtime" / "a7al2w_signal_vector_selector_repair"
REPORT = REPO / "reports" / "CRYPTO_A7AL2W_SIGNAL_VECTOR_SELECTOR_REPAIR_20260528.md"

A7AL2V_MATRIX = REPO / "runtime" / "a7al2v_replay_aware_selector_dryrun" / "a7al2v_selector_matrix.csv"
A7AR8_REGISTRY = REPO / "runtime" / "a7ar8_signal_vector_cluster_registry" / "a7ar8_signal_cluster_registry.csv"
A7AR8_VECTORS = REPO / "runtime" / "a7ar8_signal_vector_cluster_registry" / "a7ar8_signal_vectors.csv"
A7AR8_MANIFEST = REPO / "runtime" / "a7ar8_signal_vector_cluster_registry" / "a7ar8_manifest.json"

TARGET_SELECTED = 8
STRICT_PAIRWISE_CORR_CAP = 0.90
MIN_SELECTED_FOR_DIAGNOSTIC = 2


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


def max_corr_to_selected(candidate_id: str, selected: list[str], id_to_idx: dict[str, int], corr: np.ndarray) -> float:
    if not selected or candidate_id not in id_to_idx:
        return 0.0
    idx = id_to_idx[candidate_id]
    values = [float(corr[idx, id_to_idx[sid]]) for sid in selected if sid in id_to_idx]
    return max(values) if values else 0.0


def greedy_repair_select(eligible: pd.DataFrame, id_to_idx: dict[str, int], corr: np.ndarray) -> pd.DataFrame:
    candidates = eligible.sort_values(["selector_score_no_may", "candidate_id"], ascending=[False, True]).copy()
    selected: list[str] = []
    selected_clusters: set[str] = set()
    reasons: dict[str, str] = {}
    max_corrs: dict[str, float] = {}

    for _, row in candidates.iterrows():
        cid = str(row["candidate_id"])
        cluster = str(row["signal_vector_cluster_id"])
        if cluster in selected_clusters:
            reasons[cid] = "skip_same_signal_vector_cluster"
            continue
        mcor = max_corr_to_selected(cid, selected, id_to_idx, corr)
        max_corrs[cid] = mcor
        if mcor >= STRICT_PAIRWISE_CORR_CAP:
            reasons[cid] = f"skip_selected_queue_corr_ge_{STRICT_PAIRWISE_CORR_CAP}"
            continue
        selected.append(cid)
        selected_clusters.add(cluster)
        reasons[cid] = "selected_strict_diversity"
        if len(selected) >= TARGET_SELECTED:
            break

    out = candidates.copy()
    out["selected_by_a7al2w"] = out["candidate_id"].astype(str).isin(selected)
    out["a7al2w_queue_reason"] = out["candidate_id"].astype(str).map(reasons).fillna("not_reached_or_lower_score")
    out["a7al2w_max_corr_to_selected_before_pick"] = out["candidate_id"].astype(str).map(max_corrs).fillna(np.nan)
    return out


def pairwise_selected(selected: pd.DataFrame, id_to_idx: dict[str, int], corr: np.ndarray) -> pd.DataFrame:
    ids = selected["candidate_id"].astype(str).tolist()
    rows = []
    for i, left in enumerate(ids):
        for right in ids[i + 1 :]:
            if left not in id_to_idx or right not in id_to_idx:
                continue
            rows.append(
                {
                    "left_candidate_id": left,
                    "right_candidate_id": right,
                    "signal_vector_corr": float(corr[id_to_idx[left], id_to_idx[right]]),
                    "above_0p90": bool(corr[id_to_idx[left], id_to_idx[right]] >= 0.90),
                    "above_0p95": bool(corr[id_to_idx[left], id_to_idx[right]] >= 0.95),
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for path in [A7AL2V_MATRIX, A7AR8_REGISTRY, A7AR8_VECTORS, A7AR8_MANIFEST]:
        require(path)

    a7ar8_manifest = read_json(A7AR8_MANIFEST)
    if "selected_queue" not in "|".join(a7ar8_manifest.get("blockers", [])):
        raise SystemExit("A7AR-8 does not expose selected queue blocker context")

    selector = pd.read_csv(A7AL2V_MATRIX)
    registry = pd.read_csv(A7AR8_REGISTRY)
    vectors = pd.read_csv(A7AR8_VECTORS)
    id_to_idx, corr = corr_lookup(vectors)

    merged = selector.merge(
        registry[["candidate_id", "signal_vector_cluster_id", "max_corr_to_other_signal_vector"]],
        on="candidate_id",
        how="left",
        suffixes=("", "_registry"),
    )
    merged["selector_hard_reject_reason"] = merged["selector_hard_reject_reason"].fillna("")
    eligible = merged[merged["selector_hard_reject_reason"].eq("")].copy()
    repaired = greedy_repair_select(eligible, id_to_idx, corr)

    selected = repaired[repaired["selected_by_a7al2w"]].copy()
    selected_pairwise = pairwise_selected(selected, id_to_idx, corr)
    selected_cluster_count = int(selected["signal_vector_cluster_id"].nunique()) if not selected.empty else 0
    selected_top_cluster_share = (
        float(selected["signal_vector_cluster_id"].value_counts(normalize=True).iloc[0]) if not selected.empty else 0.0
    )
    selected_max_pairwise_corr = (
        float(selected_pairwise["signal_vector_corr"].max()) if not selected_pairwise.empty else 0.0
    )
    selected_stress_clean = int((~selected["is_may_stress_failed"].astype(str).str.lower().isin(["true", "1"])).sum())

    reject_reason_summary = (
        merged.assign(selector_hard_reject_reason=merged["selector_hard_reject_reason"].replace("", "eligible"))
        .groupby("selector_hard_reject_reason", as_index=False)
        .agg(candidate_count=("candidate_id", "count"))
        .sort_values("candidate_count", ascending=False)
    )
    repair_reason_summary = (
        repaired.groupby("a7al2w_queue_reason", as_index=False)
        .agg(candidate_count=("candidate_id", "count"))
        .sort_values("candidate_count", ascending=False)
    )
    stress_quarantine = (
        selected[selected["is_may_stress_failed"].astype(str).str.lower().isin(["true", "1"])]
        [["candidate_id", "signal_vector_cluster_id", "t_failure_labels", "t_may_min_spread", "t_may_sign_flip_rows", "t_may_control_dominated_rows"]]
        .copy()
    )
    stress_quarantine["quarantine_type"] = "post_selection_stress_veto_only"
    stress_quarantine["allowed_for_selector_score"] = False
    stress_quarantine["allowed_for_generation_weight_update"] = False

    queue_audit = pd.DataFrame(
        [
            {
                "eligible_before_repair": int(eligible.shape[0]),
                "selected_count": int(selected.shape[0]),
                "selected_signal_vector_clusters": selected_cluster_count,
                "selected_top_cluster_share": selected_top_cluster_share,
                "selected_max_pairwise_corr": selected_max_pairwise_corr,
                "selected_stress_clean_candidates": selected_stress_clean,
                "uses_may_for_selector": False,
            }
        ]
    )

    blockers = []
    if selected.empty:
        blockers.append("no_repaired_selection")
    if 0 < len(selected) < MIN_SELECTED_FOR_DIAGNOSTIC:
        blockers.append("too_few_low_corr_selected_candidates")
    if selected_max_pairwise_corr >= STRICT_PAIRWISE_CORR_CAP:
        blockers.append("selected_queue_corr_still_high")
    if len(selected) >= 4 and selected_top_cluster_share > 0.35:
        blockers.append("selected_queue_cluster_concentration")
    if selected_stress_clean == 0 and not selected.empty:
        blockers.append("selected_queue_may_stress_veto")

    decision = "PASS_A7AL2W_SELECTOR_DIVERSITY_REPAIR_READY_OBJECTIVE_HOLD"
    if "selected_queue_may_stress_veto" in blockers:
        decision = "HOLD_A7AL2W_SELECTOR_DIVERSITY_REPAIRED_BUT_STRESS_VETO"
    elif blockers:
        decision = "HOLD_A7AL2W_SELECTOR_DIVERSITY_REPAIR_INCOMPLETE"

    repaired.to_csv(OUT_DIR / "a7al2w_repaired_selector_candidates.csv", index=False)
    selected.to_csv(OUT_DIR / "a7al2w_repaired_selected_pool.csv", index=False)
    selected_pairwise.to_csv(OUT_DIR / "a7al2w_selected_queue_pairwise_corr.csv", index=False)
    reject_reason_summary.to_csv(OUT_DIR / "a7al2w_input_reject_reason_summary.csv", index=False)
    repair_reason_summary.to_csv(OUT_DIR / "a7al2w_repair_reason_summary.csv", index=False)
    stress_quarantine.to_csv(OUT_DIR / "a7al2w_post_selection_stress_quarantine.csv", index=False)
    queue_audit.to_csv(OUT_DIR / "a7al2w_queue_diversity_audit.csv", index=False)

    authorization = pd.DataFrame(
        [
            {"action": "same_objective_rerun", "status": "NOT_AUTHORIZED", "reason": "selector diversity repair still has zero stress-clean candidates"},
            {"action": "direct_oi_price_expansion", "status": "NOT_AUTHORIZED", "reason": "post-selection stress veto remains"},
            {"action": "large_formula_search", "status": "NOT_AUTHORIZED", "reason": "objective stress mismatch unresolved"},
            {"action": "a7al2x_objective_family_reset_contract", "status": "AUTHORIZED", "reason": "selector mechanics repaired enough to move to objective reset"},
            {"action": "alpha_proof_shadow_paper_live", "status": "NOT_AUTHORIZED", "reason": "no stress-clean candidate"},
        ]
    )
    authorization.to_csv(OUT_DIR / "a7al2w_authorization_matrix.csv", index=False)

    manifest = {
        "generated_at": utc_now(),
        "decision": decision,
        "input_selector_candidates": int(merged.shape[0]),
        "eligible_before_repair": int(eligible.shape[0]),
        "selected_count": int(selected.shape[0]),
        "selected_signal_vector_clusters": selected_cluster_count,
        "selected_top_cluster_share": selected_top_cluster_share,
        "selected_max_pairwise_corr": selected_max_pairwise_corr,
        "selected_stress_clean_candidates": selected_stress_clean,
        "blockers": blockers,
        "executes_search": False,
        "executes_replay": False,
        "executes_training": False,
        "uses_may_for_selector": False,
        "uses_may_for_generation": False,
        "uses_may_for_weight_update": False,
        "uses_may_for_veto_or_attribution": True,
        "authorizes_same_objective_rerun": False,
        "authorizes_direct_expansion": False,
        "authorizes_large_search": False,
        "authorizes_a7al2x_objective_family_reset_contract": True,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(OUT_DIR / "a7al2w_manifest.json", manifest)

    report = f"""# CRYPTO A7AL-2W Signal-Vector Selector Repair

Generated: {manifest["generated_at"]}

## Decision

```text
{manifest["decision"]}
```

This stage repairs selected-queue diversity using pre-May signal-vector clusters. It executes no generation, no replay, no training, and no proof.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Queue Diversity Audit

{md_table(queue_audit)}

## Repaired Selected Pool

{md_table(selected[["candidate_id", "selector_score_no_may", "signal_vector_cluster_id", "a7al2w_queue_reason", "is_may_stress_failed", "t_failure_labels"]], 40)}

## Pairwise Correlation

{md_table(selected_pairwise, 40)}

## Repair Reason Summary

{md_table(repair_reason_summary)}

## Post-Selection Stress Quarantine

{md_table(stress_quarantine, 40)}

## Authorization

{md_table(authorization)}

## Boundary

```text
Selector repair:
  uses pre-May replay-aware selector score
  uses pre-May signal-vector clusters
  enforces selected-queue diversity

May:
  not used for selector score
  not used for generation or weight update
  retained only as post-selection veto / attribution

Not authorized:
  same objective rerun
  direct OI x price expansion
  large formula search
  alpha proof
  shadow / paper / live
```
"""
    REPORT.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
