from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from crypto_a7_validation_utils import REPORT_DIR, RUNTIME_DIR, clean_float, stable_hash
from crypto_a7o2c_semantic_uniqueness_audit import write_json, write_markdown_table
from crypto_a7o_l1_pilot_shard import (
    DEEP_AUDIT_PER_CELL,
    is_liquidity_volatility_family,
    pivot_split_metrics,
    robust_score,
)


DATE_TAG = "20260521"
OUT_DIR = RUNTIME_DIR / "a7o_l1w1r"
CHECKPOINTS = [
    ("01", RUNTIME_DIR / "a7o_l1_pilot", "a7o_l1_pilot"),
    ("02", RUNTIME_DIR / "a7o_l1_checkpoint_02", "a7o_l1_checkpoint_02"),
    ("03", RUNTIME_DIR / "a7o_l1_checkpoint_03", "a7o_l1_checkpoint_03"),
    ("04", RUNTIME_DIR / "a7o_l1_checkpoint_04", "a7o_l1_checkpoint_04"),
    ("05", RUNTIME_DIR / "a7o_l1_checkpoint_05", "a7o_l1_checkpoint_05"),
    ("06", RUNTIME_DIR / "a7o_l1_checkpoint_06", "a7o_l1_checkpoint_06"),
]
STRESS_GATE_V3_MIN_GROSS_EXPOSURE = 0.05
MAX_LIQUIDITY_VOLATILITY_DEEP_SHARE = 0.15


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_deep() -> pd.DataFrame:
    frames = []
    for checkpoint_id, base, prefix in CHECKPOINTS:
        path = base / f"{prefix}_deep_audit_scoreboard.csv"
        df = pd.read_csv(path)
        split_path = base / f"{prefix}_split_metrics.csv"
        if split_path.exists():
            df = enrich_with_split_gross_exposure(df, pd.read_csv(split_path))
        df.insert(0, "checkpoint_id", checkpoint_id)
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def enrich_with_split_gross_exposure(deep: pd.DataFrame, split_metrics: pd.DataFrame) -> pd.DataFrame:
    required = {"candidate_id", "series", "split", "mean_gross_exposure"}
    if not required.issubset(split_metrics.columns):
        return deep
    gross = split_metrics[["candidate_id", "series", "split", "mean_gross_exposure"]].copy()
    gross["metric_column"] = gross["series"].astype(str) + "__" + gross["split"].astype(str) + "__gross_exposure"
    pivot = gross.pivot_table(
        index="candidate_id",
        columns="metric_column",
        values="mean_gross_exposure",
        aggfunc="first",
    ).reset_index()
    merged = deep.merge(pivot, on="candidate_id", how="left", suffixes=("", "__split_metric"))
    split_cols = [c for c in pivot.columns if c != "candidate_id"]
    for col in split_cols:
        split_col = f"{col}__split_metric"
        if split_col in merged.columns:
            merged[col] = merged[col].combine_first(merged[split_col])
            merged = merged.drop(columns=[split_col])
    return merged


def positive(value: Any) -> bool:
    v = clean_float(value)
    return v is not None and v > 0


def nonnegative(value: Any) -> bool:
    v = clean_float(value)
    return v is not None and v >= 0


def stress_gate_v2_reclassify(deep: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in deep.iterrows():
        pre_reasons = []
        if not positive(row.get("raw_10bp__validation_2025H1")):
            pre_reasons.append("raw_validation_nonpositive")
        if not positive(row.get("raw_10bp__recent_oos_2025H2_2026Apr")):
            pre_reasons.append("raw_recent_nonpositive")
        if not positive(row.get("raw_20bp__recent_oos_2025H2_2026Apr")):
            pre_reasons.append("cost20_recent_nonpositive")
        if not positive(row.get("execution_lag_1bar_raw_10bp__recent_oos_2025H2_2026Apr")):
            pre_reasons.append("lag1_recent_nonpositive")
        if not positive(row.get("residual_vs_funding_10bp__recent_oos_2025H2_2026Apr")):
            pre_reasons.append("residual_funding_recent_nonpositive")

        may_reasons = []
        if not positive(row.get("raw_10bp__fresh_forward_2026May__gross_exposure")):
            may_reasons.append("may_stress_no_raw_activity")
        if not positive(row.get("residual_vs_funding_10bp__fresh_forward_2026May__gross_exposure")):
            may_reasons.append("may_stress_no_residual_activity")
        may = clean_float(row.get("raw_10bp__fresh_forward_2026May"))
        may_resid = clean_float(row.get("residual_vs_funding_10bp__fresh_forward_2026May"))
        if may is None or may < -0.5:
            may_reasons.append("may_stress_severe_fail")
        elif may < -0.25:
            may_reasons.append("may_stress_material_fail")
        if may_resid is None or may_resid < 0:
            may_reasons.append("may_residual_funding_negative")

        is_control = str(row.get("object_type", "")) == "placebo"
        if is_control:
            label = "NEGATIVE_CONTROL_RESEARCH_LIKE_FAIL" if not pre_reasons and not may_reasons else "NEGATIVE_CONTROL"
        elif not pre_reasons and not may_reasons:
            label = "A7O_PILOT_RESEARCH_CANDIDATE"
        elif not pre_reasons and may_reasons:
            label = "A7O_PILOT_MAY_VETOED_NEAR_MISS"
        elif len(pre_reasons) <= 1:
            label = "A7O_PILOT_PRE_MAY_NEAR_MISS"
        else:
            label = "A7O_PILOT_REJECTED"
        rows.append(
            {
                "checkpoint_id": row["checkpoint_id"],
                "candidate_id": row["candidate_id"],
                "cell_id": row["cell_id"],
                "object_type": row.get("object_type"),
                "signal_mode": row.get("signal_mode"),
                "source_field_families": row.get("source_field_families"),
                "old_candidate_decision": row.get("candidate_decision"),
                "stress_gate_v2_decision": label,
                "stress_gate_v2_reasons": ";".join(pre_reasons + may_reasons),
                "raw_may": row.get("raw_10bp__fresh_forward_2026May"),
                "raw_may_gross": row.get("raw_10bp__fresh_forward_2026May__gross_exposure"),
                "residual_may": row.get("residual_vs_funding_10bp__fresh_forward_2026May"),
                "residual_may_gross": row.get("residual_vs_funding_10bp__fresh_forward_2026May__gross_exposure"),
            }
        )
    return pd.DataFrame(rows)


def control_forensic(deep: pd.DataFrame, reclass: pd.DataFrame) -> pd.DataFrame:
    controls = reclass[reclass["stress_gate_v2_decision"].eq("NEGATIVE_CONTROL_RESEARCH_LIKE_FAIL")].copy()
    if controls.empty:
        return controls
    cols = [
        "checkpoint_id",
        "candidate_id",
        "cell_id",
        "signal_mode",
        "expression",
        "hypothesis_family",
        "feature_family_set",
        "operator_motif",
        "temporal_horizon_class",
        "normalization_scope",
        "residualization_target",
        "source_field_families",
        "pilot_rank_score",
        "raw_10bp__validation_2025H1",
        "raw_10bp__recent_oos_2025H2_2026Apr",
        "raw_20bp__recent_oos_2025H2_2026Apr",
        "execution_lag_1bar_raw_10bp__recent_oos_2025H2_2026Apr",
        "residual_vs_funding_10bp__recent_oos_2025H2_2026Apr",
        "residual_vs_core4_10bp__recent_oos_2025H2_2026Apr",
        "raw_10bp__fresh_forward_2026May",
        "raw_10bp__fresh_forward_2026May__gross_exposure",
        "residual_vs_funding_10bp__fresh_forward_2026May",
        "residual_vs_funding_10bp__fresh_forward_2026May__gross_exposure",
        "return_corr_cluster",
    ]
    merged = controls[["checkpoint_id", "candidate_id", "stress_gate_v2_reasons"]].merge(
        deep[[c for c in cols if c in deep.columns]], on=["checkpoint_id", "candidate_id"], how="left"
    )
    return merged


def load_strict_scored() -> pd.DataFrame:
    frames = []
    for checkpoint_id, base, prefix in CHECKPOINTS:
        strict = pd.read_csv(base / f"{prefix}_strict_replay_selected.csv")
        fold = pd.read_csv(base / f"{prefix}_fold_replay_metrics.csv")
        residual = pd.read_csv(base / f"{prefix}_residual_fold_metrics.csv")
        cost_lag = pd.read_csv(base / f"{prefix}_cost_lag_fold_metrics.csv")
        split_metrics = pd.read_csv(base / f"{prefix}_split_metrics.csv")
        score = robust_score(fold, residual, cost_lag)
        split_pivot = pivot_split_metrics(split_metrics)
        scored = strict.merge(score, on="candidate_id", how="left").merge(split_pivot, on="candidate_id", how="left")
        scored.insert(0, "checkpoint_id", checkpoint_id)
        frames.append(scored)
    return pd.concat(frames, ignore_index=True)


def stress_gate_v3_reclassify(reclass: pd.DataFrame, contaminated_cells: pd.DataFrame) -> pd.DataFrame:
    contaminated = set(contaminated_cells["cell_id"].astype(str).tolist()) if not contaminated_cells.empty else set()
    out = reclass.copy()
    decisions = []
    reasons = []
    for _, row in out.iterrows():
        current = str(row["stress_gate_v2_decision"])
        row_reasons = [r for r in str(row.get("stress_gate_v2_reasons", "")).split(";") if r]
        is_control = str(row.get("object_type", "")) == "placebo"
        cell_id = str(row.get("cell_id", ""))
        raw_gross = clean_float(row.get("raw_may_gross"))
        resid_gross = clean_float(row.get("residual_may_gross"))
        if raw_gross is None or raw_gross <= STRESS_GATE_V3_MIN_GROSS_EXPOSURE:
            row_reasons.append("stress_gate_v3_raw_gross_below_min")
        if resid_gross is None or resid_gross <= STRESS_GATE_V3_MIN_GROSS_EXPOSURE:
            row_reasons.append("stress_gate_v3_residual_gross_below_min")
        if is_control and current == "NEGATIVE_CONTROL_RESEARCH_LIKE_FAIL":
            decisions.append("NEGATIVE_CONTROL_DOMINANCE_FAIL")
        elif cell_id in contaminated:
            row_reasons.append("control_contaminated_cell")
            decisions.append("A7O_PILOT_CONTROL_CONTAMINATED_CELL")
        elif current == "A7O_PILOT_RESEARCH_CANDIDATE" and not row_reasons:
            decisions.append("A7O_PILOT_RESEARCH_CANDIDATE_V3")
        elif current == "A7O_PILOT_RESEARCH_CANDIDATE":
            decisions.append("A7O_PILOT_V3_VETOED")
        else:
            decisions.append(current)
        reasons.append(";".join(dict.fromkeys(row_reasons)))
    out["stress_gate_v3_decision"] = decisions
    out["stress_gate_v3_reasons"] = reasons
    return out


def reselect_deep_from_strict(strict_scored: pd.DataFrame, contaminated_cells: pd.DataFrame) -> pd.DataFrame:
    contaminated = set(contaminated_cells["cell_id"].astype(str).tolist()) if not contaminated_cells.empty else set()
    candidates = strict_scored[~strict_scored["object_type"].astype(str).eq("placebo")].copy()
    candidates = candidates[~candidates["cell_id"].astype(str).isin(contaminated)].copy()
    candidates["liquidity_volatility_flag"] = candidates["source_field_families"].apply(is_liquidity_volatility_family)
    candidates["pilot_rank_score"] = pd.to_numeric(candidates["pilot_rank_score"], errors="coerce").fillna(-999.0)
    candidates["diversity_adjusted_rank_score"] = candidates["pilot_rank_score"] - 0.30 * candidates["liquidity_volatility_flag"].astype(float)
    target = len(CHECKPOINTS) * 64 * DEEP_AUDIT_PER_CELL
    liqvol_cap = int(target * MAX_LIQUIDITY_VOLATILITY_DEEP_SHARE)
    liqvol_count = 0
    selected_ids: set[str] = set()
    parts = []
    ranked_parts = []
    for cell_id, part in candidates.groupby("cell_id", sort=True):
        ranked = part.sort_values(["diversity_adjusted_rank_score", "pilot_rank_score", "candidate_id"], ascending=[False, False, True])
        ranked_parts.append(ranked)
        selected = []
        for _, row in ranked.iterrows():
            if len(selected) >= DEEP_AUDIT_PER_CELL:
                break
            if bool(row["liquidity_volatility_flag"]) and liqvol_count >= liqvol_cap:
                continue
            selected.append(row)
            selected_ids.add(str(row["candidate_id"]))
            if bool(row["liquidity_volatility_flag"]):
                liqvol_count += 1
        if selected:
            part_selected = pd.DataFrame(selected)
            part_selected["w1r_reselection_stage"] = "cell_quota"
            parts.append(part_selected)
    reselected = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()
    if len(reselected) < target and ranked_parts:
        ranked_all = pd.concat(ranked_parts, ignore_index=True)
        ranked_all = ranked_all[~ranked_all["candidate_id"].astype(str).isin(selected_ids)].copy()
        ranked_all = ranked_all.sort_values(["diversity_adjusted_rank_score", "pilot_rank_score", "candidate_id"], ascending=[False, False, True])
        backfill = []
        for _, row in ranked_all.iterrows():
            if len(reselected) + len(backfill) >= target:
                break
            if bool(row["liquidity_volatility_flag"]) and liqvol_count >= liqvol_cap:
                continue
            backfill.append(row)
            selected_ids.add(str(row["candidate_id"]))
            if bool(row["liquidity_volatility_flag"]):
                liqvol_count += 1
        if backfill:
            backfill_df = pd.DataFrame(backfill)
            backfill_df["w1r_reselection_stage"] = "global_backfill"
            reselected = pd.concat([reselected, backfill_df], ignore_index=True)
    if reselected.empty:
        return reselected
    reselected["w1r_deep_selection_policy"] = "strict_pool_reselect_excluding_control_contaminated_cells"
    reselected["w1r_liquidity_volatility_cap"] = liqvol_cap
    reselected["w1r_liquidity_volatility_count"] = liqvol_count
    return reselected


def checkpoint_summary_v2(reclass: pd.DataFrame, deep: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for checkpoint_id, part in reclass.groupby("checkpoint_id", sort=True):
        deep_part = deep[deep["checkpoint_id"].astype(str).eq(str(checkpoint_id))]
        controls = int(part["stress_gate_v2_decision"].eq("NEGATIVE_CONTROL_RESEARCH_LIKE_FAIL").sum())
        post_may = int(part[(part["stress_gate_v2_decision"].eq("A7O_PILOT_RESEARCH_CANDIDATE")) & (~part["object_type"].eq("placebo"))].shape[0])
        liqvol = deep_part["source_field_families"].astype(str).apply(lambda x: {"liquidity", "volatility"}.issubset(set(x.split(";"))))
        rows.append(
            {
                "checkpoint_id": checkpoint_id,
                "deep_audit_selected": int(len(part)),
                "post_may_eligible_deep_survivors_v2": post_may,
                "post_may_eligible_rate_v2": clean_float(post_may / len(part)) if len(part) else None,
                "negative_control_research_like_v2": controls,
                "liquidity_volatility_deep_share": clean_float(liqvol.mean()) if len(deep_part) else None,
                "single_return_corr_cluster_share": clean_float(deep_part["return_corr_cluster"].value_counts(normalize=True).iloc[0]) if len(deep_part) and "return_corr_cluster" in deep_part else None,
                "active_cells_with_valid_deep_audit": int(deep_part["cell_id"].nunique()) if len(deep_part) else 0,
                "decision_v2": "PASS_RECLASSIFIED_CHECKPOINT" if controls == 0 else "HOLD_NEGATIVE_CONTROL",
            }
        )
    return pd.DataFrame(rows)


def artifact_staleness_audit(reclass: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for checkpoint_id, base, prefix in CHECKPOINTS:
        old_path = base / f"{prefix}_checkpoint_decision.json"
        old = json.loads(old_path.read_text(encoding="utf-8"))
        old_post = int(old["metrics"]["post_may_eligible_deep_survivors"])
        new_post = int(
            reclass[
                reclass["checkpoint_id"].astype(str).eq(str(checkpoint_id))
                & reclass["stress_gate_v2_decision"].eq("A7O_PILOT_RESEARCH_CANDIDATE")
                & ~reclass["object_type"].eq("placebo")
            ].shape[0]
        )
        rows.append(
            {
                "checkpoint_id": checkpoint_id,
                "artifact": str(old_path),
                "stored_post_may_eligible": old_post,
                "stress_gate_v2_post_may_eligible": new_post,
                "stale": old_post != new_post,
            }
        )
    return pd.DataFrame(rows)


def write_report(
    summary: pd.DataFrame,
    stale: pd.DataFrame,
    controls: pd.DataFrame,
    strict_controls: pd.DataFrame,
    contaminated_cells: pd.DataFrame,
    reselected_concentration: pd.DataFrame,
    concentration: pd.DataFrame,
    decision: dict[str, Any],
) -> Path:
    path = REPORT_DIR / f"CRYPTO_A7O_L1W1R_POLICY_REPAIR_AND_RECLASSIFICATION_{DATE_TAG}.md"
    report = [
        "# Crypto A7O-L1W1R Policy Repair And Reclassification",
        "",
        f"- generated_at: `{decision['generated_at']}`",
        f"- decision: `{decision['decision']}`",
        "- executes_new_search: `False`",
        "- executes_replay: `False`",
        "- authorizes_w2: `False`",
        "- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`",
        f"- blockers: `{decision['blockers']}`",
        "",
        "## Checkpoint Summary V2",
        "",
        write_markdown_table(summary, 20),
        "## Artifact Staleness Audit",
        "",
        write_markdown_table(stale, 20),
        "## Negative-Control Forensic",
        "",
        write_markdown_table(controls, 20) if not controls.empty else "`No negative-control research-like candidates under stress_gate_v2.`",
        "## Strict-Pool Negative-Control Forensic",
        "",
        write_markdown_table(strict_controls, 20) if not strict_controls.empty else "`No strict-pool negative-control research-like candidates under stress_gate_v2.`",
        "## Control-Contaminated Cells",
        "",
        write_markdown_table(contaminated_cells, 20) if not contaminated_cells.empty else "`No control-contaminated cells.`",
        "## W1R Strict-Pool Reselection Counterfactual",
        "",
        write_markdown_table(reselected_concentration, 20),
        "## Wave V2 Concentration/Productivity",
        "",
        write_markdown_table(concentration, 20),
        "## Stress Gate V3 Limitation",
        "",
        "`active_hour_count` is not present in the existing checkpoint artifacts, so W1R does not claim a full active-hour v3 pass. This remains a blocker for W2 authorization.",
        "## Boundary",
        "",
        "A7O-L1W1R is a reclassification and forensic stage only. It does not authorize W2, full L1, alpha proof, shadow, paper, or live.",
    ]
    path.write_text("\n".join(report), encoding="utf-8")
    return path


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_now()
    deep = load_deep()
    reclass = stress_gate_v2_reclassify(deep)
    controls = control_forensic(deep, reclass)
    summary = checkpoint_summary_v2(reclass, deep)
    stale = artifact_staleness_audit(reclass)
    strict_scored = load_strict_scored()
    strict_reclass = stress_gate_v2_reclassify(strict_scored)
    strict_controls = control_forensic(strict_scored, strict_reclass)
    contaminated_cells = strict_controls[["checkpoint_id", "cell_id"]].drop_duplicates().copy() if not strict_controls.empty else pd.DataFrame(columns=["checkpoint_id", "cell_id"])
    reclass_v3 = stress_gate_v3_reclassify(reclass, contaminated_cells)
    strict_reclass_v3 = stress_gate_v3_reclassify(strict_reclass, contaminated_cells)
    reselected = reselect_deep_from_strict(strict_scored, contaminated_cells)
    if not reselected.empty:
        reselected_reclass_v2 = stress_gate_v2_reclassify(reselected)
        reselected_reclass_v3 = stress_gate_v3_reclassify(reselected_reclass_v2, contaminated_cells)
        reselected_post_may = reselected_reclass_v3[reselected_reclass_v3["stress_gate_v3_decision"].eq("A7O_PILOT_RESEARCH_CANDIDATE_V3")].copy()
        reselected_liqvol = reselected["source_field_families"].astype(str).apply(lambda x: {"liquidity", "volatility"}.issubset(set(x.split(";"))))
    else:
        reselected_reclass_v2 = pd.DataFrame()
        reselected_reclass_v3 = pd.DataFrame()
        reselected_post_may = pd.DataFrame()
        reselected_liqvol = pd.Series(dtype=bool)
    post_may = reclass[(reclass["stress_gate_v2_decision"].eq("A7O_PILOT_RESEARCH_CANDIDATE")) & (~reclass["object_type"].eq("placebo"))].copy()
    liqvol = deep["source_field_families"].astype(str).apply(lambda x: {"liquidity", "volatility"}.issubset(set(x.split(";"))))
    concentration_rows = [
        {"metric": "wave_liquidity_volatility_deep_share", "value": clean_float(liqvol.mean()), "threshold": 0.15, "operator": "<=", "pass": bool(liqvol.mean() <= 0.15)},
        {"metric": "wave_single_return_corr_cluster_share", "value": clean_float(deep["return_corr_cluster"].value_counts(normalize=True).iloc[0]), "threshold": 0.20, "operator": "<=", "pass": bool(deep["return_corr_cluster"].value_counts(normalize=True).iloc[0] <= 0.20)},
        {"metric": "wave_post_may_eligible_deep_survivors_v2", "value": int(len(post_may)), "threshold": 120, "operator": ">=", "pass": bool(len(post_may) >= 120)},
        {"metric": "wave_post_may_eligible_rate_v2", "value": clean_float(len(post_may) / len(deep)), "threshold": 0.15, "operator": ">=", "pass": bool(len(post_may) / len(deep) >= 0.15)},
        {"metric": "negative_control_research_like_v2", "value": int(len(controls)), "threshold": 0, "operator": "=", "pass": bool(len(controls) == 0)},
    ]
    concentration = pd.DataFrame(concentration_rows)
    reselected_concentration = pd.DataFrame(
        [
            {"metric": "reselected_deep_count", "value": int(len(reselected)), "threshold": int(len(CHECKPOINTS) * 64 * DEEP_AUDIT_PER_CELL), "operator": "=", "pass": bool(len(reselected) == len(CHECKPOINTS) * 64 * DEEP_AUDIT_PER_CELL)},
            {"metric": "reselected_liquidity_volatility_share", "value": clean_float(reselected_liqvol.mean()) if len(reselected_liqvol) else None, "threshold": 0.15, "operator": "<=", "pass": bool(len(reselected_liqvol) and reselected_liqvol.mean() <= 0.15)},
            {"metric": "reselected_post_may_eligible_deep_survivors_v3", "value": int(len(reselected_post_may)), "threshold": 120, "operator": ">=", "pass": bool(len(reselected_post_may) >= 120)},
            {"metric": "reselected_post_may_eligible_rate_v3", "value": clean_float(len(reselected_post_may) / len(reselected)) if len(reselected) else None, "threshold": 0.15, "operator": ">=", "pass": bool(len(reselected) and len(reselected_post_may) / len(reselected) >= 0.15)},
            {"metric": "strict_negative_control_research_like_v2", "value": int(len(strict_controls)), "threshold": 0, "operator": "=", "pass": bool(len(strict_controls) == 0)},
            {"metric": "control_contaminated_cells", "value": int(contaminated_cells["cell_id"].nunique()) if not contaminated_cells.empty else 0, "threshold": 0, "operator": "=", "pass": bool(contaminated_cells.empty)},
            {"metric": "stress_gate_v3_active_hour_count_available", "value": 0, "threshold": 1, "operator": "=", "pass": False},
        ]
    )
    blockers = []
    if len(controls) > 0:
        blockers.append("negative_control_research_like_v2")
    if len(strict_controls) > 0:
        blockers.append("strict_negative_control_research_like_v2")
    if not contaminated_cells.empty:
        blockers.append("control_contaminated_cells")
    if len(post_may) < 120:
        blockers.append("wave_post_may_eligible_deep_survivors_v2")
    if len(post_may) / len(deep) < 0.15:
        blockers.append("wave_post_may_eligible_rate_v2")
    if len(reselected_post_may) < 120:
        blockers.append("reselected_post_may_eligible_deep_survivors_v3")
    if len(reselected) == 0 or len(reselected_post_may) / len(reselected) < 0.15:
        blockers.append("reselected_post_may_eligible_rate_v3")
    blockers.append("stress_gate_v3_active_hour_count_unavailable")
    if not bool(concentration.loc[concentration["metric"].eq("wave_liquidity_volatility_deep_share"), "pass"].iloc[0]):
        blockers.append("wave_liquidity_volatility_deep_share")
    if not bool(concentration.loc[concentration["metric"].eq("wave_single_return_corr_cluster_share"), "pass"].iloc[0]):
        blockers.append("wave_single_return_corr_cluster_share")
    blockers = list(dict.fromkeys(blockers))
    decision = {
        "generated_at": now,
        "decision": "PASS_A7O_L1W1R_READY_FOR_W2" if not blockers else "HOLD_A7O_L1W1R",
        "authorizes_w2": False,
        "authorizes_full_l1_without_checkpoint": False,
        "authorizes_l2_or_l3": False,
        "alpha_proof_status": "NOT_ALPHA_PROOF",
        "shadow_paper_live_status": "NOT_AUTHORIZED",
        "blockers": blockers,
        "stress_gate_version": "v2_may_activity_required",
        "metrics": {
            "deep_audit_selected": int(len(deep)),
            "post_may_eligible_deep_survivors_v2": int(len(post_may)),
            "post_may_eligible_rate_v2": clean_float(len(post_may) / len(deep)),
            "negative_control_research_like_v2": int(len(controls)),
            "strict_pool_size": int(len(strict_scored)),
            "strict_negative_control_research_like_v2": int(len(strict_controls)),
            "control_contaminated_cells": int(contaminated_cells["cell_id"].nunique()) if not contaminated_cells.empty else 0,
            "reselected_deep_count": int(len(reselected)),
            "reselected_post_may_eligible_deep_survivors_v3": int(len(reselected_post_may)),
            "reselected_post_may_eligible_rate_v3": clean_float(len(reselected_post_may) / len(reselected)) if len(reselected) else None,
            "stale_checkpoint_artifacts": int(stale["stale"].sum()),
        },
    }
    paths = {
        "reclassification": OUT_DIR / "a7o_l1w1r_stress_gate_v2_reclassification.csv",
        "checkpoint_summary": OUT_DIR / "a7o_l1w1r_checkpoint_summary_v2.csv",
        "cumulative_summary": OUT_DIR / "a7o_l1w1r_cumulative_summary_v2.csv",
        "artifact_staleness": OUT_DIR / "a7o_l1w1r_artifact_staleness_audit.csv",
        "negative_control": OUT_DIR / "a7o_l1w1r_negative_control_forensic.csv",
        "control_contaminated_cells": OUT_DIR / "a7o_l1w1r_control_contaminated_cells.csv",
        "post_may_pool": OUT_DIR / "a7o_l1w1r_post_may_eligible_pool_v2.csv",
        "concentration": OUT_DIR / "a7o_l1w1r_concentration_audit_v2.csv",
        "strict_reclassification": OUT_DIR / "a7o_l1w1r_strict_pool_stress_gate_v2_reclassification.csv",
        "strict_negative_control": OUT_DIR / "a7o_l1w1r_strict_pool_negative_control_forensic.csv",
        "stress_gate_v3_reclassification": OUT_DIR / "a7o_l1w1r_stress_gate_v3_reclassification.csv",
        "strict_stress_gate_v3_reclassification": OUT_DIR / "a7o_l1w1r_strict_pool_stress_gate_v3_reclassification.csv",
        "reselected_deep": OUT_DIR / "a7o_l1w1r_reselected_deep_audit_scoreboard.csv",
        "reselected_reclassification": OUT_DIR / "a7o_l1w1r_reselected_stress_gate_v3_reclassification.csv",
        "reselected_post_may_pool": OUT_DIR / "a7o_l1w1r_reselected_post_may_eligible_pool_v3.csv",
        "reselected_concentration": OUT_DIR / "a7o_l1w1r_reselected_concentration_audit_v3.csv",
        "decision": OUT_DIR / "a7o_l1w1r_decision_record.json",
    }
    reclass.to_csv(paths["reclassification"], index=False)
    summary.to_csv(paths["checkpoint_summary"], index=False)
    summary.to_csv(paths["cumulative_summary"], index=False)
    stale.to_csv(paths["artifact_staleness"], index=False)
    controls.to_csv(paths["negative_control"], index=False)
    strict_reclass.to_csv(paths["strict_reclassification"], index=False)
    strict_controls.to_csv(paths["strict_negative_control"], index=False)
    reclass_v3.to_csv(paths["stress_gate_v3_reclassification"], index=False)
    strict_reclass_v3.to_csv(paths["strict_stress_gate_v3_reclassification"], index=False)
    contaminated_cells.to_csv(paths["control_contaminated_cells"], index=False)
    post_may.to_csv(paths["post_may_pool"], index=False)
    concentration.to_csv(paths["concentration"], index=False)
    reselected.to_csv(paths["reselected_deep"], index=False)
    reselected_reclass_v3.to_csv(paths["reselected_reclassification"], index=False)
    reselected_post_may.to_csv(paths["reselected_post_may_pool"], index=False)
    reselected_concentration.to_csv(paths["reselected_concentration"], index=False)
    report = write_report(summary, stale, controls, strict_controls, contaminated_cells, reselected_concentration, concentration, decision)
    decision["outputs"] = {k: str(v) for k, v in paths.items()}
    decision["outputs"]["report"] = str(report)
    decision["stable_decision_hash"] = stable_hash({k: v for k, v in decision.items() if k != "stable_decision_hash"})
    write_json(paths["decision"], decision)
    print(json.dumps(decision, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
