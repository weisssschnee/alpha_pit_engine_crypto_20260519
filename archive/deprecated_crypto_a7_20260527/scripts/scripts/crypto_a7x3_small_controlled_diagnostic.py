from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

import crypto_a7v5_small_replay_smoke as a7v5
from crypto_a7v5_small_replay_smoke import (
    PRIMARY_COST_BPS,
    SEVERE_COST_BPS,
    ExprContext,
    evaluate_row,
    load_panel,
)

LEGACY_TOP_BOTTOM_BOOK = a7v5.top_bottom_book


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "runtime" / "a7x3_small_controlled_diagnostic"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7X3_SMALL_CONTROLLED_DIAGNOSTIC_20260522.md"

VALIDATION = "validation_2025H1"
RECENT = "recent_oos_2025H2_2026Apr"
MAY = "fresh_may_2026"

GENERATED_CAP = 5000
STRICT_REPLAY_CAP = 100
DEEP_AUDIT_CAP = 64


def fast_top_bottom_book(signal: np.ndarray, target: np.ndarray, orientation: float, cost_bps: float) -> dict[str, np.ndarray]:
    """Vectorized core3 top1/bottom1 book equivalent to A7V-5's loop implementation."""
    oriented = signal * orientation
    valid = np.isfinite(oriented) & np.isfinite(target)
    valid_rows = valid.sum(axis=1) >= 3
    pos = np.zeros_like(target, dtype=float)
    if np.any(valid_rows):
        high = np.where(valid, oriented, -np.inf)
        low = np.where(valid, oriented, np.inf)
        rows = np.where(valid_rows)[0]
        long_idx = np.argmax(high[valid_rows], axis=1)
        short_idx = np.argmin(low[valid_rows], axis=1)
        pos[rows, long_idx] = 0.5
        pos[rows, short_idx] = -0.5
    gross = np.nansum(pos * target, axis=1)
    prev = np.vstack([np.zeros((1, pos.shape[1])), pos[:-1, :]])
    turnover = np.nansum(np.abs(pos - prev), axis=1) / 2.0
    fee = turnover * (cost_bps / 10000.0)
    return {
        "net": gross - fee,
        "gross": gross,
        "turnover": turnover,
        "gross_exposure": np.nansum(np.abs(pos), axis=1),
    }


a7v5.top_bottom_book = fast_top_bottom_book


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def stable_id(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    return df.head(max_rows).to_markdown(index=False)


def clean_float(value: Any) -> float | None:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def candidate_row(family: str, expr: str, horizon: int, source_fields: list[str], motif: str) -> dict[str, Any]:
    cid = f"a7x3_{family}_{horizon}_{stable_id(expr + str(horizon))}"
    return {
        "candidate_id": cid,
        "generator": "crypto_a7x3_small_controlled_diagnostic",
        "production_family": family,
        "derived_feature_id": motif,
        "expression": expr,
        "horizon": horizon,
        "source_fields": ";".join(sorted(set(source_fields))),
        "source_field_families": "aggtrades_reset_interaction",
        "transform": motif,
        "window_hours": "",
        "availability_mask": "agg_features_available",
        "cross_symbol_scope": "core3_only",
        "feature_available_lag_bars": 1,
        "feature_timestamp_rule": "agg hour bucket t observable only after hour close; all rolling inputs past-only",
        "execution_rule": "next-bar or later; May stress post-selection only",
        "requires_residual_baselines": "FundingCore;Core4",
        "required_negative_controls": "row_shuffle;time_shuffle;wrong_lag;sign_flip;matched_family_controls",
        "paired_ablation_plan": "standalone_agg;market_state_only;interaction;matched_controls",
        "decision": "A7X3_GENERATED_CANDIDATE",
        "reject_reasons": "",
    }


def generate_candidates() -> pd.DataFrame:
    agg_flow = [
        "agg_flow_imbalance_notional",
        "agg_signed_flow_z_24h",
        "agg_flow_accel_4h_vs_24h",
        "agg_buy_notional_share",
        "agg_vwap_close_bps",
        "agg_large_notional_share_4h",
        "agg_cross_symbol_signed_flow_share",
        "agg_flow_minus_btcusdt_4h",
        "agg_flow_minus_ethusdt_4h",
    ]
    slow_liquidity = [
        "agg_notional_sum_24h",
        "agg_trade_count_sum_4h",
        "agg_avg_trade_notional_24h",
        "agg_large_notional_sum_24h",
    ]
    market_states = ["mark_index_ratio", "premium_index", "realized_vol_12", "realized_vol_24", "ret_6", "ret_12"]
    rows: list[dict[str, Any]] = []

    for field in agg_flow + slow_liquidity:
        for window in [12, 24, 48]:
            for horizon in [24, 48]:
                rows.append(candidate_row("F0_slow_aggtrades_horizon", f"Decay({field},{window})", horizon, [field], "slow_decay"))
                rows.append(candidate_row("F0_slow_aggtrades_horizon", f"TSMean({field},{window})", horizon, [field], "slow_tsmean"))
        for horizon in [24, 48]:
            rows.append(candidate_row("F0_slow_aggtrades_horizon", f"HorizonSpread({field},12,48)", horizon, [field], "horizon_spread"))

    for field in agg_flow:
        for state in ["mark_index_ratio", "premium_index"]:
            for window in [12, 24, 48]:
                expr = f"Mul(ZScore(Decay({field},{window})),Rank({state}))"
                rows.append(candidate_row("F1_aggtrades_basis_interaction", expr, 24, [field, state], "agg_x_basis"))

    for field in agg_flow + slow_liquidity:
        for window in [12, 24]:
            for vol_expr in ["SafeDiv(realized_vol_12,realized_vol_24)", "Sub(realized_vol_12,realized_vol_24)"]:
                expr = f"Mul(ZScore(TSMean({field},{window})),Rank({vol_expr}))"
                rows.append(candidate_row("F2_aggtrades_vol_compression_interaction", expr, 24, [field, "realized_vol_12", "realized_vol_24"], "agg_x_vol_compression"))

    for field in ["agg_cross_symbol_signed_flow_share", "agg_cross_symbol_notional_share", "agg_flow_minus_btcusdt_4h", "agg_flow_minus_ethusdt_4h"]:
        for state in ["Sub(ret_6,ret_12)", "HorizonSpread(ret_6,12,48)", "mark_index_ratio"]:
            expr = f"Mul(CrossSymbolRank({field}),ZScore({state}))"
            rows.append(candidate_row("F3_aggtrades_cross_symbol_dispersion", expr, 24, [field, "ret_6", "ret_12", "mark_index_ratio"], "agg_x_cross_symbol_dispersion"))

    for field in agg_flow:
        for rel in ["RelativeToBTC", "RelativeToETH"]:
            for state in ["ret_12", "premium_index"]:
                expr = f"Mul(ZScore({rel}({field})),Rank({state}))"
                rows.append(candidate_row("F4_symbol_tier_neutralized_aggtrades", expr, 24, [field, state], "symbol_tier_neutralized"))

    out = pd.DataFrame(rows).drop_duplicates("candidate_id").head(GENERATED_CAP).copy()
    return out


def choose_strict_replay(generated: pd.DataFrame) -> pd.DataFrame:
    selected = []
    quota = max(1, STRICT_REPLAY_CAP // 5)
    for family in [
        "F0_slow_aggtrades_horizon",
        "F1_aggtrades_basis_interaction",
        "F2_aggtrades_vol_compression_interaction",
        "F3_aggtrades_cross_symbol_dispersion",
        "F4_symbol_tier_neutralized_aggtrades",
    ]:
        part = generated[generated["production_family"].eq(family)].sort_values(["transform", "expression", "horizon", "candidate_id"])
        selected.append(part.head(quota))
    out = pd.concat(selected, ignore_index=True).head(STRICT_REPLAY_CAP)
    return out


def build_controls(selected: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for _, row in selected.iterrows():
        for mode in ["row_shuffle", "time_shuffle", "wrong_lag", "sign_flip"]:
            control_id = f"{row['candidate_id']}__ctrl_{mode}_{stable_id(str(row['candidate_id']) + mode)}"
            rec = row.to_dict()
            rec.update(
                {
                    "control_id": control_id,
                    "base_candidate_id": row["candidate_id"],
                    "control_mode": mode,
                    "control_class": "a7x3_replay_negative_control",
                    "promotable": False,
                    "allowed_in_a7x3_replay": True,
                }
            )
            rec.pop("candidate_id", None)
            rows.append(rec)
    return pd.DataFrame(rows)


def book_parity_audit(index: pd.DatetimeIndex, matrices: dict[str, np.ndarray], ctx: ExprContext, selected: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    agg_mask = matrices["agg_features_available"].astype(bool)
    train_mask = a7v5.split_mask(index, "train_2024")
    for _, row in selected.head(12).iterrows():
        expr = str(row["expression"])
        horizon = int(row["horizon"])
        signal = np.where(agg_mask, ctx.eval(expr), np.nan)
        target = a7v5.forward_open_return(matrices["open"], horizon)
        base_train_ic = np.nanmean(a7v5.row_ic(signal[train_mask], target[train_mask]))
        orientation = 1.0 if not np.isfinite(base_train_ic) or base_train_ic >= 0 else -1.0
        legacy = LEGACY_TOP_BOTTOM_BOOK(signal, target, orientation, PRIMARY_COST_BPS)
        fast = fast_top_bottom_book(signal, target, orientation, PRIMARY_COST_BPS)
        rows.append(
            {
                "candidate_id": row["candidate_id"],
                "expression": expr,
                "horizon": horizon,
                "max_abs_net_diff": clean_float(np.nanmax(np.abs(legacy["net"] - fast["net"]))),
                "max_abs_turnover_diff": clean_float(np.nanmax(np.abs(legacy["turnover"] - fast["turnover"]))),
                "max_abs_gross_exposure_diff": clean_float(np.nanmax(np.abs(legacy["gross_exposure"] - fast["gross_exposure"]))),
            }
        )
    out = pd.DataFrame(rows)
    if not out.empty:
        diff_cols = ["max_abs_net_diff", "max_abs_turnover_diff", "max_abs_gross_exposure_diff"]
        out["parity_pass"] = out[diff_cols].fillna(0).le(1e-12).all(axis=1)
    return out


def run_replay(selected: pd.DataFrame, controls: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    index, symbols, matrices = load_panel(selected)
    ctx = ExprContext(matrices, symbols)
    parity = book_parity_audit(index, matrices, ctx, selected)
    metric_rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for _, row in selected.iterrows():
        try:
            rows, _ = evaluate_row(index, matrices, ctx, row, "candidate", "original")
            metric_rows.extend(rows)
        except Exception as exc:  # noqa: BLE001
            failures.append({"candidate_id": row["candidate_id"], "object_type": "candidate", "control_mode": "original", "eval_error": f"{type(exc).__name__}: {exc}"})
    for _, row in controls.iterrows():
        try:
            rows, _ = evaluate_row(index, matrices, ctx, row, "control", str(row["control_mode"]))
            metric_rows.extend(rows)
        except Exception as exc:  # noqa: BLE001
            failures.append({"candidate_id": row["control_id"], "object_type": "control", "control_mode": row["control_mode"], "eval_error": f"{type(exc).__name__}: {exc}"})
    return pd.DataFrame(metric_rows), pd.DataFrame(failures), parity


def wide_metrics(metrics: pd.DataFrame) -> pd.DataFrame:
    idx = ["candidate_id", "base_candidate_id", "object_type", "control_mode", "production_family", "expression", "horizon"]
    values = ["active_hours", "mean_ic", "net_sum_10bps", "net_sum_20bps", "turnover_mean", "gross_exposure_mean"]
    wide = metrics.pivot_table(index=idx, columns="split", values=values, aggfunc="first")
    wide.columns = [f"{a}__{b}" for a, b in wide.columns]
    return wide.reset_index()


def label_candidates(wide: pd.DataFrame, selected: pd.DataFrame) -> pd.DataFrame:
    candidates = wide[wide["object_type"].eq("candidate")].copy()
    controls = wide[wide["object_type"].eq("control")].copy()
    rows: list[dict[str, Any]] = []
    for _, cand in candidates.iterrows():
        cid = str(cand["candidate_id"])
        matched = controls[controls["base_candidate_id"].eq(cid)]
        max_val = pd.to_numeric(matched[f"net_sum_10bps__{VALIDATION}"], errors="coerce").max() if not matched.empty else np.nan
        max_recent = pd.to_numeric(matched[f"net_sum_10bps__{RECENT}"], errors="coerce").max() if not matched.empty else np.nan
        val = float(cand.get(f"net_sum_10bps__{VALIDATION}", np.nan))
        recent = float(cand.get(f"net_sum_10bps__{RECENT}", np.nan))
        recent20 = float(cand.get(f"net_sum_20bps__{RECENT}", np.nan))
        may = float(cand.get(f"net_sum_10bps__{MAY}", np.nan))
        control_val_recent_positive = int(
            (
                (pd.to_numeric(matched[f"net_sum_10bps__{VALIDATION}"], errors="coerce") > 0)
                & (pd.to_numeric(matched[f"net_sum_10bps__{RECENT}"], errors="coerce") > 0)
            ).sum()
        )
        dominates_controls = bool(val > max_val and recent > max_recent)
        if control_val_recent_positive:
            label = "A7X3_HOLD_CONTROL_CONTAMINATED"
        elif not (val > 0 and recent > 0):
            label = "A7X3_HOLD_RAW_VAL_RECENT_FAIL"
        elif not dominates_controls:
            label = "A7X3_HOLD_DOES_NOT_DOMINATE_CONTROLS"
        elif not recent20 > 0:
            label = "A7X3_HOLD_COST20_FAIL"
        elif not may > 0:
            label = "A7X3_NEAR_MISS_MAY_STRESS_FAIL"
        else:
            label = "A7X_RESEARCH_CLUE"
        rows.append(
            {
                "candidate_id": cid,
                "production_family": cand["production_family"],
                "expression": cand["expression"],
                "horizon": cand["horizon"],
                "validation_net10": clean_float(val),
                "recent_net10": clean_float(recent),
                "recent_net20": clean_float(recent20),
                "may_net10": clean_float(may),
                "max_control_validation_net10": clean_float(max_val),
                "max_control_recent_net10": clean_float(max_recent),
                "dominates_controls": int(dominates_controls),
                "control_val_recent_positive_count": control_val_recent_positive,
                "a7x3_label": label,
            }
        )
    labels = pd.DataFrame(rows)
    lineage_cols = ["candidate_id", "derived_feature_id", "source_fields", "transform", "paired_ablation_plan"]
    labels = labels.merge(selected[[c for c in lineage_cols if c in selected.columns]], on="candidate_id", how="left")
    return labels


def select_deep_audit(labels: pd.DataFrame) -> pd.DataFrame:
    label_order = {
        "A7X_RESEARCH_CLUE": 0,
        "A7X3_NEAR_MISS_MAY_STRESS_FAIL": 1,
        "A7X3_HOLD_COST20_FAIL": 2,
        "A7X3_HOLD_DOES_NOT_DOMINATE_CONTROLS": 3,
        "A7X3_HOLD_CONTROL_CONTAMINATED": 4,
        "A7X3_HOLD_RAW_VAL_RECENT_FAIL": 5,
    }
    labels = labels.copy()
    labels["label_order"] = labels["a7x3_label"].map(label_order).fillna(99)
    selected = []
    quota = max(1, DEEP_AUDIT_CAP // max(1, labels["production_family"].nunique()))
    for family in sorted(labels["production_family"].unique()):
        part = labels[labels["production_family"].eq(family)].sort_values(["label_order", "recent_net10", "validation_net10"], ascending=[True, False, False])
        selected.append(part.head(quota))
    return pd.concat(selected, ignore_index=True).head(DEEP_AUDIT_CAP)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    return df.head(max_rows).to_markdown(index=False)


def write_report(now: str, generated: pd.DataFrame, selected: pd.DataFrame, controls: pd.DataFrame, labels: pd.DataFrame, deep: pd.DataFrame, failures: pd.DataFrame, authorization: dict[str, Any]) -> None:
    label_summary = labels.groupby(["production_family", "a7x3_label"]).size().reset_index(name="rows")
    lines = [
        "# Crypto A7X-3 Small Controlled Diagnostic",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{authorization['decision']}`",
        "- executes_search: `small_structural_generation`",
        "- executes_replay: `small_controlled_diagnostic`",
        "- alpha proof / expanded replay / full search / shadow / paper / live: `NOT_AUTHORIZED`",
        "",
        "## Scope",
        "",
        "A7X-3 tests the A7X reset contract with a capped diagnostic. It does not replay old A7V-5 positives and does not expand the failed activity/liquidity self-reproduction family.",
        "",
        "May is used only as a post-selection stress label. It is not used for generation, ranking, thresholds, orientation, or allocation.",
        "",
        "## Funnel",
        "",
        f"- generated: `{len(generated)}` / cap `{GENERATED_CAP}`",
        f"- strict replay candidates: `{len(selected)}` / cap `{STRICT_REPLAY_CAP}`",
        f"- controls: `{len(controls)}`",
        f"- deep audit selected: `{len(deep)}` / cap `{DEEP_AUDIT_CAP}`",
        "",
        "## Label Summary",
        "",
        table(label_summary, max_rows=80),
        "",
        "## Deep Audit Pool",
        "",
        table(deep.sort_values(["a7x3_label", "recent_net10"], ascending=[True, False]), max_rows=80),
        "",
        "## Eval Failures",
        "",
        table(failures, max_rows=40),
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
        "",
        "## Required Next",
        "",
        "- If research clues exist, run A7X-4 forensic before any larger replay.",
        "- If no research clues exist, use near-miss distribution to revise the reset contract; do not increase budget by default.",
        "- Keep A7V failed family in weak-prior registry.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_stamp()
    generated = generate_candidates()
    selected = choose_strict_replay(generated)
    controls = build_controls(selected)
    metrics, failures, parity = run_replay(selected, controls)
    wide = wide_metrics(metrics)
    labels = label_candidates(wide, selected)
    deep = select_deep_audit(labels)
    research_clues = int(labels["a7x3_label"].eq("A7X_RESEARCH_CLUE").sum())
    control_contaminated = int(labels["a7x3_label"].eq("A7X3_HOLD_CONTROL_CONTAMINATED").sum())
    blockers: list[str] = []
    if not failures.empty:
        blockers.append("eval_failures_present")
    if not parity.empty and not bool(parity["parity_pass"].all()):
        blockers.append("fast_book_parity_fail")
    if research_clues == 0:
        blockers.append("no_a7x_research_clue")
    if control_contaminated > 0:
        blockers.append("control_contamination_present")
    decision = "PASS_A7X3_RESEARCH_CLUE_POOL_FOR_FORENSIC" if not blockers else "HOLD_A7X3_NO_CLEAN_RESEARCH_CLUE"
    authorization = {
        "generated_at": now,
        "decision": decision,
        "blockers": blockers,
        "generated_count": int(len(generated)),
        "strict_replay_candidate_count": int(len(selected)),
        "control_count": int(len(controls)),
        "metric_rows": int(len(metrics)),
        "deep_audit_count": int(len(deep)),
        "research_clue_count": research_clues,
        "control_contaminated_candidate_count": control_contaminated,
        "fast_book_parity_pass": bool(parity.empty or parity["parity_pass"].all()),
        "executes_search": "small_structural_generation",
        "executes_replay": "small_controlled_diagnostic",
        "may_policy": "stress_only_not_generation_ranking_threshold_or_allocation",
        "authorizes_a7x4_forensic": research_clues > 0 and failures.empty,
        "authorizes_expanded_replay": False,
        "authorizes_full_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "required_next": [
            "A7X-4 forensic if research clues exist; otherwise revise reset objective",
            "Do not expand budget from A7X-3 alone",
            "Keep May stress-only policy",
        ],
    }
    generated.to_csv(OUT_DIR / "a7x3_generated_candidates.csv", index=False)
    selected.to_csv(OUT_DIR / "a7x3_selected_strict_replay_candidates.csv", index=False)
    controls.to_csv(OUT_DIR / "a7x3_replay_controls.csv", index=False)
    metrics.to_csv(OUT_DIR / "a7x3_split_metrics.csv", index=False)
    parity.to_csv(OUT_DIR / "a7x3_fast_book_parity_audit.csv", index=False)
    wide.to_csv(OUT_DIR / "a7x3_wide_metrics.csv", index=False)
    labels.to_csv(OUT_DIR / "a7x3_candidate_labels.csv", index=False)
    deep.to_csv(OUT_DIR / "a7x3_deep_audit_pool.csv", index=False)
    failures.to_csv(OUT_DIR / "a7x3_eval_failures.csv", index=False)
    write_json(OUT_DIR / "a7x3_authorization_matrix.json", authorization)
    write_json(OUT_DIR / "a7x3_manifest.json", {"generated_at": now, "decision": decision, "output_dir": str(OUT_DIR), "report": str(REPORT_PATH)})
    write_report(now, generated, selected, controls, labels, deep, failures, authorization)
    print(json.dumps({"decision": decision, "research_clues": research_clues, "generated": len(generated), "selected": len(selected), "controls": len(controls)}, indent=2))


if __name__ == "__main__":
    main()
