from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from crypto_a7_validation_utils import REPORT_DIR, RUNTIME_DIR, clean_float, stable_hash
from crypto_a7o2c_semantic_uniqueness_audit import write_json, write_markdown_table


DATE_TAG = "20260521"
OUT_DIR = RUNTIME_DIR / "a7p_cell_failure_map_redesign"
A7O_W1R_DIR = RUNTIME_DIR / "a7o_l1w1r"
CHECKPOINTS = [
    ("01", RUNTIME_DIR / "a7o_l1_pilot", "a7o_l1_pilot"),
    ("02", RUNTIME_DIR / "a7o_l1_checkpoint_02", "a7o_l1_checkpoint_02"),
    ("03", RUNTIME_DIR / "a7o_l1_checkpoint_03", "a7o_l1_checkpoint_03"),
    ("04", RUNTIME_DIR / "a7o_l1_checkpoint_04", "a7o_l1_checkpoint_04"),
    ("05", RUNTIME_DIR / "a7o_l1_checkpoint_05", "a7o_l1_checkpoint_05"),
    ("06", RUNTIME_DIR / "a7o_l1_checkpoint_06", "a7o_l1_checkpoint_06"),
]
NON_MAY_REASONS = [
    "raw_validation_nonpositive",
    "raw_recent_nonpositive",
    "cost20_recent_nonpositive",
    "lag1_recent_nonpositive",
    "residual_funding_recent_nonpositive",
]
MAY_STRESS_REASONS = [
    "may_stress_no_raw_activity",
    "may_stress_no_residual_activity",
    "may_stress_severe_fail",
    "may_stress_material_fail",
    "may_residual_funding_negative",
    "stress_gate_v3_raw_gross_below_min",
    "stress_gate_v3_residual_gross_below_min",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_checkpoint_id(value: Any) -> str:
    return str(value).zfill(2)


def split_reasons(value: Any) -> set[str]:
    if pd.isna(value):
        return set()
    return {part for part in str(value).split(";") if part}


def contains_liqvol(value: Any) -> bool:
    parts = set(str(value).split(";"))
    return "liquidity" in parts and "volatility" in parts


def load_strict_metadata() -> pd.DataFrame:
    frames = []
    for checkpoint_id, base, prefix in CHECKPOINTS:
        strict = pd.read_csv(base / f"{prefix}_strict_replay_selected.csv")
        strict.insert(0, "checkpoint_id", checkpoint_id)
        frames.append(strict)
    out = pd.concat(frames, ignore_index=True)
    out["checkpoint_id"] = out["checkpoint_id"].map(normalize_checkpoint_id)
    return out


def load_reclassification() -> pd.DataFrame:
    reclass = pd.read_csv(A7O_W1R_DIR / "a7o_l1w1r_strict_pool_stress_gate_v3_reclassification.csv")
    reclass["checkpoint_id"] = reclass["checkpoint_id"].map(normalize_checkpoint_id)
    return reclass


def merged_candidate_table() -> pd.DataFrame:
    metadata = load_strict_metadata()
    reclass = load_reclassification()
    meta_cols = [
        "checkpoint_id",
        "candidate_id",
        "cell_id",
        "hypothesis_family",
        "feature_family_set",
        "operator_motif",
        "temporal_horizon_class",
        "normalization_scope",
        "residualization_target",
        "turnover_class",
        "regime_fold_target",
        "source_fields",
        "source_field_families",
        "object_type",
        "signal_mode",
        "static_score",
        "may_used_for_generation",
        "may_used_for_static_score",
    ]
    merged = reclass.merge(metadata[[c for c in meta_cols if c in metadata.columns]], on=["checkpoint_id", "candidate_id", "cell_id"], how="left", suffixes=("", "__meta"))
    for col in ["object_type", "signal_mode", "source_field_families"]:
        meta_col = f"{col}__meta"
        if meta_col in merged.columns:
            merged[col] = merged[col].combine_first(merged[meta_col])
            merged = merged.drop(columns=[meta_col])
    merged["reason_set"] = merged["stress_gate_v3_reasons"].apply(split_reasons)
    for reason in NON_MAY_REASONS:
        merged[reason] = merged["reason_set"].apply(lambda reasons, r=reason: r in reasons)
    for reason in MAY_STRESS_REASONS:
        merged[reason] = merged["reason_set"].apply(lambda reasons, r=reason: r in reasons)
    merged["non_may_fail"] = merged[NON_MAY_REASONS].any(axis=1)
    merged["may_stress_veto"] = merged[[r for r in MAY_STRESS_REASONS if r in merged.columns]].any(axis=1)
    merged["normal_candidate"] = ~merged["object_type"].astype(str).eq("placebo")
    merged["negative_control"] = merged["object_type"].astype(str).eq("placebo")
    merged["negative_control_research_like"] = merged["stress_gate_v2_decision"].astype(str).eq("NEGATIVE_CONTROL_RESEARCH_LIKE_FAIL")
    merged["pre_may_pass_normal"] = merged["normal_candidate"] & ~merged["non_may_fail"]
    merged["post_may_candidate_v3"] = merged["stress_gate_v3_decision"].astype(str).eq("A7O_PILOT_RESEARCH_CANDIDATE_V3")
    merged["liquidity_volatility_flag"] = merged["source_field_families"].apply(contains_liqvol)
    return merged


def mode_value(series: pd.Series) -> str:
    if series.empty:
        return ""
    mode = series.astype(str).replace("nan", "").value_counts()
    return str(mode.index[0]) if len(mode) else ""


def cell_failure_map(candidates: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (checkpoint_id, cell_id), part in candidates.groupby(["checkpoint_id", "cell_id"], sort=True):
        normal = part[part["normal_candidate"]]
        controls = part[part["negative_control"]]
        strict_count = len(part)
        normal_count = len(normal)
        control_count = len(controls)
        pre_may_pass_count = int(normal["pre_may_pass_normal"].sum())
        post_may_count = int(normal["post_may_candidate_v3"].sum())
        control_like_count = int(controls["negative_control_research_like"].sum())
        row = {
            "checkpoint_id": checkpoint_id,
            "cell_id": cell_id,
            "strict_count": strict_count,
            "normal_count": normal_count,
            "control_count": control_count,
            "hypothesis_family": mode_value(part.get("hypothesis_family", pd.Series(dtype=str))),
            "feature_family_set": mode_value(part.get("feature_family_set", pd.Series(dtype=str))),
            "operator_motif": mode_value(part.get("operator_motif", pd.Series(dtype=str))),
            "temporal_horizon_class": mode_value(part.get("temporal_horizon_class", pd.Series(dtype=str))),
            "normalization_scope": mode_value(part.get("normalization_scope", pd.Series(dtype=str))),
            "residualization_target": mode_value(part.get("residualization_target", pd.Series(dtype=str))),
            "turnover_class": mode_value(part.get("turnover_class", pd.Series(dtype=str))),
            "regime_fold_target": mode_value(part.get("regime_fold_target", pd.Series(dtype=str))),
            "source_field_families": mode_value(part.get("source_field_families", pd.Series(dtype=str))),
            "pre_may_pass_normal_count": pre_may_pass_count,
            "pre_may_pass_normal_rate": clean_float(pre_may_pass_count / normal_count) if normal_count else None,
            "post_may_candidate_v3_count_stress_only": post_may_count,
            "post_may_candidate_v3_rate_stress_only": clean_float(post_may_count / normal_count) if normal_count else None,
            "negative_control_research_like_count": control_like_count,
            "raw_validation_fail_rate": clean_float(normal["raw_validation_nonpositive"].mean()) if normal_count else None,
            "raw_recent_fail_rate": clean_float(normal["raw_recent_nonpositive"].mean()) if normal_count else None,
            "cost20_recent_fail_rate": clean_float(normal["cost20_recent_nonpositive"].mean()) if normal_count else None,
            "lag1_recent_fail_rate": clean_float(normal["lag1_recent_nonpositive"].mean()) if normal_count else None,
            "residual_funding_recent_fail_rate": clean_float(normal["residual_funding_recent_nonpositive"].mean()) if normal_count else None,
            "may_stress_veto_rate_stress_only": clean_float(normal["may_stress_veto"].mean()) if normal_count else None,
            "liquidity_volatility_share": clean_float(part["liquidity_volatility_flag"].mean()) if strict_count else None,
            "policy_uses_may": False,
        }
        rows.append(row)
    out = pd.DataFrame(rows)
    return out


def recommendation_for_cell(row: pd.Series) -> tuple[str, str, bool]:
    if row["negative_control_research_like_count"] > 0:
        return "quarantine_control_contaminated_cell", "hard_blocker", False
    if row["pre_may_pass_normal_count"] == 0 or row["raw_recent_fail_rate"] >= 0.75 or row["raw_validation_fail_rate"] >= 0.75:
        return "drop_or_low_priority_raw_weak_cell", "low", False
    if row["cost20_recent_fail_rate"] >= 0.75 or row["lag1_recent_fail_rate"] >= 0.75:
        return "redesign_for_cost_lag_robustness", "medium", False
    if row["residual_funding_recent_fail_rate"] >= 0.75:
        return "redesign_for_residual_independence", "medium", False
    if row["liquidity_volatility_share"] >= 0.50:
        return "retain_only_under_liquidity_volatility_quarantine_cap", "medium", False
    if row["pre_may_pass_normal_rate"] >= 0.20 and row["cost20_recent_fail_rate"] <= 0.50 and row["lag1_recent_fail_rate"] <= 0.50:
        return "retain_control_clean_non_may_robust_cell", "high", True
    return "retain_for_targeted_mutation_diagnostic", "medium", False


def build_recommendations(cell_map: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in cell_map.iterrows():
        action, priority, w2_ready = recommendation_for_cell(row)
        rows.append(
            {
                "checkpoint_id": row["checkpoint_id"],
                "cell_id": row["cell_id"],
                "recommended_action": action,
                "priority": priority,
                "w2_registry_candidate": w2_ready,
                "primary_reason": ";".join(
                    [
                        reason
                        for reason, condition in [
                            ("negative_control_contamination", row["negative_control_research_like_count"] > 0),
                            ("raw_weak", row["pre_may_pass_normal_count"] == 0 or row["raw_recent_fail_rate"] >= 0.75 or row["raw_validation_fail_rate"] >= 0.75),
                            ("cost_lag_fragile", row["cost20_recent_fail_rate"] >= 0.75 or row["lag1_recent_fail_rate"] >= 0.75),
                            ("residual_fragile", row["residual_funding_recent_fail_rate"] >= 0.75),
                            ("liquidity_volatility_heavy", row["liquidity_volatility_share"] >= 0.50),
                            ("non_may_robust", w2_ready),
                        ]
                        if condition
                    ]
                ),
            }
        )
    rec = pd.DataFrame(rows)
    out = cell_map.merge(rec, on=["checkpoint_id", "cell_id"], how="left")
    out["policy_uses_may"] = False
    return out


def group_summary(recommendations: pd.DataFrame, group_col: str) -> pd.DataFrame:
    rows = []
    for key, part in recommendations.groupby(group_col, dropna=False, sort=True):
        rows.append(
            {
                group_col: key,
                "cell_count": int(len(part)),
                "w2_registry_candidates": int(part["w2_registry_candidate"].sum()),
                "quarantined_cells": int(part["recommended_action"].eq("quarantine_control_contaminated_cell").sum()),
                "raw_weak_cells": int(part["recommended_action"].eq("drop_or_low_priority_raw_weak_cell").sum()),
                "cost_lag_redesign_cells": int(part["recommended_action"].eq("redesign_for_cost_lag_robustness").sum()),
                "residual_redesign_cells": int(part["recommended_action"].eq("redesign_for_residual_independence").sum()),
                "mean_pre_may_pass_rate": clean_float(part["pre_may_pass_normal_rate"].mean()),
                "mean_cost20_fail_rate": clean_float(part["cost20_recent_fail_rate"].mean()),
                "mean_lag1_fail_rate": clean_float(part["lag1_recent_fail_rate"].mean()),
                "may_stress_veto_rate_stress_only": clean_float(part["may_stress_veto_rate_stress_only"].mean()),
                "policy_uses_may": False,
            }
        )
    return pd.DataFrame(rows).sort_values(["w2_registry_candidates", "cell_count"], ascending=[False, False])


def task_registry(decision: dict[str, Any]) -> pd.DataFrame:
    rows = [
        {
            "task_id": "A7P-2A",
            "task": "instrument_active_hour_count_in_fold_and_split_artifacts",
            "reason": "stress_gate_v3_active_hour_count_unavailable",
            "required_before": "W2",
            "executes_search": False,
            "may_policy": "stress_only",
        },
        {
            "task_id": "A7P-2B",
            "task": "implement_negative_control_dominance_gate",
            "reason": "wrong_lag_stale_24h_controls_passed_research_like_gate",
            "required_before": "W2",
            "executes_search": False,
            "may_policy": "not_used",
        },
        {
            "task_id": "A7P-2C",
            "task": "quarantine_control_contaminated_cells_C0208_C0223",
            "reason": "checkpoint_04_control_contamination",
            "required_before": "W2",
            "executes_search": False,
            "may_policy": "not_used",
        },
        {
            "task_id": "A7P-2D",
            "task": "build_control_clean_w2_cell_registry_from_non_may_failure_map",
            "reason": "W1R_HOLD_and_W2_not_authorized",
            "required_before": "W2",
            "executes_search": False,
            "may_policy": "may_not_rank_or_allocate",
        },
        {
            "task_id": "A7P-2E",
            "task": "dry_run_w2_cell_registry_coverage_audit",
            "reason": "verify_cell_mix_before_any_checkpoint_execution",
            "required_before": "W2",
            "executes_search": False,
            "may_policy": "not_used",
        },
        {
            "task_id": "A7P-3",
            "task": "only_after_A7P2_pass_run_small_protected_w2_pilot",
            "reason": "W2_currently_not_authorized",
            "required_before": "none",
            "executes_search": True,
            "may_policy": "stress_only",
        },
    ]
    for row in rows:
        row["current_authorization"] = "blocked" if row["task_id"] == "A7P-3" else "authorized"
        row["parent_decision"] = decision["decision"]
    return pd.DataFrame(rows)


def write_contract_report(decision: dict[str, Any], tasks: pd.DataFrame) -> Path:
    path = REPORT_DIR / f"CRYPTO_A7P0_SEARCH_CELL_FAILURE_MAP_REDESIGN_CONTRACT_{DATE_TAG}.md"
    report = [
        "# Crypto A7P-0 Search-Cell Failure-Map Redesign Contract",
        "",
        f"- generated_at: `{decision['generated_at']}`",
        "- objective: convert A7O-L1W1R HOLD into non-May cell redesign tasks",
        "- executes_new_search: `False`",
        "- executes_replay: `False`",
        "- authorizes_w2: `False`",
        "- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`",
        "",
        "## Policy",
        "",
        "- May remains stress-only: post-selection stress/veto/failure attribution.",
        "- May is forbidden for ranking, reward, threshold tuning, generation, allocation, mutation, and surrogate targets.",
        "- Cell redesign may use negative-control contamination, non-May raw/cost/lag/residual fragility, activity validity, and diversity.",
        "- Control-contaminated cells cannot contribute to W2 continuation evidence.",
        "",
        "## Task Registry",
        "",
        write_markdown_table(tasks, 20),
    ]
    path.write_text("\n".join(report), encoding="utf-8")
    return path


def write_audit_report(
    decision: dict[str, Any],
    cell_map: pd.DataFrame,
    recommendations: pd.DataFrame,
    hypothesis_summary: pd.DataFrame,
    feature_summary: pd.DataFrame,
    tasks: pd.DataFrame,
) -> Path:
    path = REPORT_DIR / f"CRYPTO_A7P1_CELL_FAILURE_MAP_REDESIGN_AUDIT_{DATE_TAG}.md"
    top_actions = recommendations["recommended_action"].value_counts().rename_axis("recommended_action").reset_index(name="cell_count")
    report = [
        "# Crypto A7P-1 Cell Failure-Map Redesign Audit",
        "",
        f"- generated_at: `{decision['generated_at']}`",
        f"- decision: `{decision['decision']}`",
        "- executes_new_search: `False`",
        "- executes_replay: `False`",
        "- authorizes_w2: `False`",
        "- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`",
        f"- blockers: `{decision['blockers']}`",
        "",
        "## Action Summary",
        "",
        write_markdown_table(top_actions, 20),
        "## Cell Recommendation Sample",
        "",
        write_markdown_table(
            recommendations[
                [
                    "checkpoint_id",
                    "cell_id",
                    "recommended_action",
                    "priority",
                    "w2_registry_candidate",
                    "pre_may_pass_normal_rate",
                    "cost20_recent_fail_rate",
                    "lag1_recent_fail_rate",
                    "residual_funding_recent_fail_rate",
                    "negative_control_research_like_count",
                    "policy_uses_may",
                ]
            ].sort_values(["priority", "pre_may_pass_normal_rate"], ascending=[True, False]),
            30,
        ),
        "## Hypothesis Family Summary",
        "",
        write_markdown_table(hypothesis_summary, 30),
        "## Feature Family Summary",
        "",
        write_markdown_table(feature_summary, 30),
        "## Next Tasks",
        "",
        write_markdown_table(tasks, 20),
        "## Boundary",
        "",
        "A7P-1 is a redesign audit. It does not authorize W2 execution or any alpha/shadow/paper/live promotion.",
    ]
    path.write_text("\n".join(report), encoding="utf-8")
    return path


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_now()
    candidates = merged_candidate_table()
    cell_map = cell_failure_map(candidates)
    recommendations = build_recommendations(cell_map)
    hypothesis_summary = group_summary(recommendations, "hypothesis_family")
    feature_summary = group_summary(recommendations, "feature_family_set")
    control_contaminated = recommendations[recommendations["recommended_action"].eq("quarantine_control_contaminated_cell")].copy()
    w2_registry = recommendations[recommendations["w2_registry_candidate"]].copy()
    blockers = [
        "W1R_HOLD",
        "negative_control_dominance_gate_missing_in_runner",
        "stress_gate_v3_active_hour_count_unavailable",
        "W2_cell_registry_not_built",
    ]
    decision = {
        "generated_at": now,
        "decision": "PASS_A7P1_FAILURE_MAP_READY_FOR_A7P2_REDESIGN_TASKS",
        "authorizes_w2": False,
        "authorizes_full_l1_without_checkpoint": False,
        "authorizes_l2_or_l3": False,
        "alpha_proof_status": "NOT_ALPHA_PROOF",
        "shadow_paper_live_status": "NOT_AUTHORIZED",
        "executes_new_search": False,
        "executes_replay": False,
        "blockers": blockers,
        "metrics": {
            "candidate_rows": int(len(candidates)),
            "cell_count": int(len(cell_map)),
            "control_contaminated_cells": int(len(control_contaminated)),
            "w2_registry_candidate_cells_non_may_only": int(len(w2_registry)),
            "policy_uses_may": False,
        },
        "may_policy": {
            "allowed": ["post_selection_stress_label", "post_selection_veto", "failure_attribution"],
            "forbidden": ["score", "ranking", "threshold", "generation", "allocation", "mutation", "surrogate_target"],
        },
    }
    tasks = task_registry(decision)
    paths = {
        "manifest": OUT_DIR / "a7p_manifest.json",
        "decision": OUT_DIR / "a7p_decision_record.json",
        "cell_failure_map": OUT_DIR / "a7p_cell_failure_map.csv",
        "cell_policy_recommendations": OUT_DIR / "a7p_cell_policy_recommendations.csv",
        "control_contaminated_cells": OUT_DIR / "a7p_control_contaminated_cells.csv",
        "w2_candidate_cell_registry_non_may_only": OUT_DIR / "a7p_w2_candidate_cell_registry_non_may_only.csv",
        "hypothesis_family_summary": OUT_DIR / "a7p_hypothesis_family_summary.csv",
        "feature_family_summary": OUT_DIR / "a7p_feature_family_summary.csv",
        "task_registry": OUT_DIR / "a7p_next_task_registry.csv",
    }
    cell_map.to_csv(paths["cell_failure_map"], index=False)
    recommendations.to_csv(paths["cell_policy_recommendations"], index=False)
    control_contaminated.to_csv(paths["control_contaminated_cells"], index=False)
    w2_registry.to_csv(paths["w2_candidate_cell_registry_non_may_only"], index=False)
    hypothesis_summary.to_csv(paths["hypothesis_family_summary"], index=False)
    feature_summary.to_csv(paths["feature_family_summary"], index=False)
    tasks.to_csv(paths["task_registry"], index=False)
    contract_report = write_contract_report(decision, tasks)
    audit_report = write_audit_report(decision, cell_map, recommendations, hypothesis_summary, feature_summary, tasks)
    decision["outputs"] = {k: str(v) for k, v in paths.items()}
    decision["outputs"]["contract_report"] = str(contract_report)
    decision["outputs"]["audit_report"] = str(audit_report)
    decision["stable_decision_hash"] = stable_hash({k: v for k, v in decision.items() if k != "stable_decision_hash"})
    write_json(paths["decision"], decision)
    manifest = {
        **decision,
        "source_inputs": {
            "w1r_reclassification": str(A7O_W1R_DIR / "a7o_l1w1r_strict_pool_stress_gate_v3_reclassification.csv"),
            "checkpoints": [checkpoint_id for checkpoint_id, _, _ in CHECKPOINTS],
        },
    }
    manifest["stable_manifest_hash"] = stable_hash({k: v for k, v in manifest.items() if k not in {"generated_at", "stable_manifest_hash"}})
    write_json(paths["manifest"], manifest)
    print(json.dumps(decision, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
