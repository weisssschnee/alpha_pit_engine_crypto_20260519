from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7sel0_selector_counterfactual"
REPORT = REPO / "reports" / "CRYPTO_A7SEL0_SELECTOR_TARGET_COUNTERFACTUAL_20260529.md"

A7AA4 = REPO / "runtime" / "a7aa4_response_readiness_handoff" / "a7aa4_manifest.json"
POOL = REPO / "runtime" / "a7ar7_shared_candidate_pool" / "a7ar7_shared_candidate_pool.csv"
CLUSTERS = REPO / "runtime" / "a7ar8_signal_vector_cluster_registry" / "a7ar8_signal_cluster_registry.csv"
ROLE_RECLASS = REPO / "runtime" / "a7aif2_field_enforcement_regression" / "a7aif2_historical_candidate_role_reclassification.csv"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def num(series: pd.Series, default: float = np.nan) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(default)


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    aa4 = read_json(A7AA4)
    if not aa4.get("authorizes_a7sel0"):
        raise SystemExit("A7AA-4 does not authorize A7SEL-0")
    pool = pd.read_csv(POOL)
    clusters = pd.read_csv(CLUSTERS)
    roles = pd.read_csv(ROLE_RECLASS)
    frame = pool.merge(clusters[["candidate_id", "signal_vector_cluster_id", "max_corr_to_other_signal_vector"]], on="candidate_id", how="left")
    frame = frame.merge(roles[["candidate_id", "candidate_role", "field_roles", "role_violation"]], on="candidate_id", how="left")

    control = num(frame.get("r_control_ratio_premay_max", pd.Series(np.nan, index=frame.index)), 10.0)
    q_control = num(frame.get("q_control_ratio_premay_max_by_split", pd.Series(np.nan, index=frame.index)), 10.0)
    frame["control_ratio_for_selector"] = np.minimum(control, q_control)
    label_cols = [
        "q_label_t1_positive_premay_splits",
        "q_label_t2_positive_premay_splits",
        "r_label_t1_positive_premay_splits",
        "r_label_t2_positive_premay_splits",
    ]
    for col in label_cols:
        frame[col] = num(frame.get(col, pd.Series(0, index=frame.index)), 0.0)
    frame["non_l7_label_alignment_score"] = frame[label_cols].sum(axis=1)
    frame["lag_score"] = num(frame.get("r_one_bar_lag_positive_premay_splits", frame.get("q_one_bar_lag_positive_premay_splits", pd.Series(0, index=frame.index))), 0.0)
    frame["latent_score"] = num(frame.get("r_latent_positive_premay_splits", frame.get("q_timevarying_latent_positive_premay_splits", pd.Series(0, index=frame.index))), 0.0)
    frame["cost_score"] = num(frame.get("r_net_10bps_positive_premay_splits", frame.get("q_net_10bps_positive_premay_splits", pd.Series(0, index=frame.index))), 0.0)
    base_score = num(frame.get("q_selector_score_no_may", pd.Series(0, index=frame.index)), 0.0)
    frame["a7sel0_score_no_may"] = (
        base_score
        + frame["non_l7_label_alignment_score"]
        + frame["lag_score"]
        + frame["latent_score"]
        + frame["cost_score"]
        - frame["control_ratio_for_selector"].clip(0, 10)
    )
    frame["role_violation"] = frame["role_violation"].apply(truthy)
    frame["control_dominated"] = frame.get("is_control_dominated_premay", pd.Series(False, index=frame.index)).apply(truthy) | (frame["control_ratio_for_selector"] >= 1.0)
    frame["may_observed"] = frame.get("in_a7al2t_may_attribution", pd.Series(False, index=frame.index)).apply(truthy)
    frame["may_stress_failed"] = frame.get("is_may_stress_failed", pd.Series(False, index=frame.index)).apply(truthy)
    frame["stress_clean_observed"] = frame["may_observed"] & ~frame["may_stress_failed"]
    frame["eligible_for_counterfactual_queue"] = (
        ~frame["role_violation"]
        & ~frame["control_dominated"]
        & (frame["non_l7_label_alignment_score"] > 0)
    )

    queue = frame[frame["eligible_for_counterfactual_queue"]].sort_values("a7sel0_score_no_may", ascending=False).copy()
    selected_rows = []
    used_clusters: set[str] = set()
    for _, row in queue.iterrows():
        cluster = str(row.get("signal_vector_cluster_id", ""))
        if cluster in used_clusters:
            continue
        selected_rows.append(row)
        used_clusters.add(cluster)
        if len(selected_rows) >= 4:
            break
    selected = pd.DataFrame(selected_rows)
    diversity = pd.DataFrame(
        [
            {
                "selected_count": int(len(selected)),
                "selected_signal_vector_clusters": int(selected["signal_vector_cluster_id"].nunique()) if not selected.empty else 0,
                "selected_max_pairwise_corr_proxy": float(pd.to_numeric(selected["max_corr_to_other_signal_vector"], errors="coerce").max()) if not selected.empty else np.nan,
                "top_cluster_share": float(selected["signal_vector_cluster_id"].value_counts(normalize=True).max()) if not selected.empty else 0.0,
            }
        ]
    )
    control_audit = selected[["candidate_id", "control_ratio_for_selector", "control_dominated", "role_violation", "candidate_role"]].copy() if not selected.empty else pd.DataFrame()
    label_dist = selected[["candidate_id", "non_l7_label_alignment_score", *label_cols]].copy() if not selected.empty else pd.DataFrame()
    stress = pd.DataFrame(
        [
            {
                "selected_count": int(len(selected)),
                "selected_may_observed_count": int(selected["may_observed"].sum()) if not selected.empty else 0,
                "selected_stress_clean_candidates": int(selected["stress_clean_observed"].sum()) if not selected.empty else 0,
                "selected_may_stress_failed_count": int(selected["may_stress_failed"].sum()) if not selected.empty else 0,
            }
        ]
    )
    blockers = []
    if len(selected) < 4:
        blockers.append("selected_count_lt_4")
    if not selected.empty and selected["signal_vector_cluster_id"].nunique() < min(len(selected), 4):
        blockers.append("selected_cluster_count_low")
    if not selected.empty and bool(selected["control_dominated"].any()):
        blockers.append("control_dominated_selected")
    if not selected.empty and bool(selected["role_violation"].any()):
        blockers.append("role_violation_selected")
    if not selected.empty and int(selected["stress_clean_observed"].sum()) == 0:
        blockers.append("selected_stress_clean_candidates_zero")
    if not selected.empty and float(selected["non_l7_label_alignment_score"].sum()) <= 0:
        blockers.append("selected_non_l7_label_evidence_zero")
    decision = "PASS_A7SEL0_SELECTOR_TARGET_COUNTERFACTUAL_HAS_CLEAN_QUEUE" if not blockers else "HOLD_A7SEL0_SELECTOR_COUNTERFACTUAL_NOT_PROMOTABLE"
    manifest = {
        "stage": "A7SEL-0",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "executes_generation": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may_in_selector_score": False,
        "uses_may_for_post_selection_stress_summary": True,
        "input_candidate_count": int(len(frame)),
        "eligible_queue_count": int(len(queue)),
        "selected_count": int(len(selected)),
        "selected_stress_clean_candidates": int(selected["stress_clean_observed"].sum()) if not selected.empty else 0,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    frame.to_csv(RUNTIME / "a7sel0_selector_trace.csv", index=False)
    selected.to_csv(RUNTIME / "a7sel0_selected_queue.csv", index=False)
    diversity.to_csv(RUNTIME / "a7sel0_signal_vector_diversity.csv", index=False)
    control_audit.to_csv(RUNTIME / "a7sel0_control_dominance_audit.csv", index=False)
    label_dist.to_csv(RUNTIME / "a7sel0_label_family_distribution.csv", index=False)
    stress.to_csv(RUNTIME / "a7sel0_stress_veto_summary.csv", index=False)
    write_json(RUNTIME / "a7sel0_manifest.json", manifest)
    lines = [
        "# CRYPTO A7SEL-0 SELECTOR TARGET COUNTERFACTUAL",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7SEL-0 dry-reranks existing shared-pool candidates only. It does not generate formulas or run replay.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Selected Queue",
        "",
        md_table(selected[["candidate_id", "candidate_role", "signal_vector_cluster_id", "a7sel0_score_no_may", "control_ratio_for_selector", "non_l7_label_alignment_score", "stress_clean_observed"]] if not selected.empty else selected, 20),
        "",
        "## Stress Summary",
        "",
        md_table(stress, 20),
        "",
        "## Boundary",
        "",
        "```text",
        "No generation, replay, search, alpha proof, shadow, paper, or live execution is authorized.",
        "May is not used in selector score; it is only summarized after selection.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
