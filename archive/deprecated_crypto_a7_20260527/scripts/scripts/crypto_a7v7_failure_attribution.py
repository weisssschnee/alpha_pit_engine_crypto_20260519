from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from crypto_a7v5_small_replay_smoke import (
    A7V4_DIR,
    CORE3,
    OUT_DIR as A7V5_OUT_DIR,
    PRIMARY_COST_BPS,
    SEVERE_COST_BPS,
    ExprContext,
    apply_control,
    forward_open_return,
    load_panel,
    row_ic,
    split_mask,
)


ROOT = Path(__file__).resolve().parents[1]
A7V6_DIR = ROOT / "runtime" / "a7v6_candidate_control_dominance_forensic"
OUT_DIR = ROOT / "runtime" / "a7v7_failure_attribution"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7V7_FAILURE_ATTRIBUTION_20260522.md"

VALIDATION = "validation_2025H1"
RECENT = "recent_oos_2025H2_2026Apr"
MAY = "fresh_may_2026"


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


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


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    clues = pd.read_csv(A7V6_DIR / "a7v6_pre_may_dominance_clues.csv")
    selected = pd.read_csv(A7V5_OUT_DIR / "a7v5_selected_candidates.csv")
    controls = pd.read_csv(A7V4_DIR / "a7v4_replay_control_specs.csv")
    selected = selected[selected["candidate_id"].isin(set(clues["candidate_id"]))].copy()
    controls = controls[controls["base_candidate_id"].isin(set(clues["candidate_id"]))].copy()
    return clues, selected, controls


def top_bottom_book_detail(signal: np.ndarray, target: np.ndarray, orientation: float, cost_bps: float) -> dict[str, np.ndarray]:
    oriented = signal * orientation
    valid = np.isfinite(oriented) & np.isfinite(target)
    pos = np.zeros_like(target, dtype=float)
    for i in range(target.shape[0]):
        idx = np.where(valid[i])[0]
        if len(idx) < 3:
            continue
        order = idx[np.argsort(oriented[i, idx])]
        pos[i, order[0]] = -0.5
        pos[i, order[-1]] = 0.5
    gross_by_symbol = pos * target
    gross = np.nansum(gross_by_symbol, axis=1)
    prev = np.vstack([np.zeros((1, pos.shape[1])), pos[:-1, :]])
    turnover_by_symbol = np.abs(pos - prev) / 2.0
    turnover = np.nansum(turnover_by_symbol, axis=1)
    fee = turnover * (cost_bps / 10000.0)
    return {
        "pos": pos,
        "gross_by_symbol": gross_by_symbol,
        "gross": gross,
        "turnover_by_symbol": turnover_by_symbol,
        "turnover": turnover,
        "fee": fee,
        "net": gross - fee,
        "gross_exposure": np.nansum(np.abs(pos), axis=1),
    }


def evaluate_signal(index: pd.DatetimeIndex, matrices: dict[str, np.ndarray], ctx: ExprContext, row: pd.Series, control_mode: str = "original") -> tuple[np.ndarray, np.ndarray, float, dict[str, np.ndarray], dict[str, np.ndarray]]:
    expr = str(row["expression"])
    horizon = int(row["horizon"])
    agg_mask = matrices["agg_features_available"].astype(bool)
    base_signal = np.where(agg_mask, ctx.eval(expr), np.nan)
    target = forward_open_return(matrices["open"], horizon)
    train_mask = split_mask(index, "train_2024")
    base_train_ic = np.nanmean(row_ic(base_signal[train_mask], target[train_mask]))
    orientation = 1.0 if not np.isfinite(base_train_ic) or base_train_ic >= 0 else -1.0
    signal = base_signal
    if control_mode != "original":
        signal = apply_control(signal, control_mode, str(row.get("control_id", row.get("candidate_id", ""))))
        signal = np.where(agg_mask, signal, np.nan)
    return signal, target, orientation, top_bottom_book_detail(signal, target, orientation, PRIMARY_COST_BPS), top_bottom_book_detail(signal, target, orientation, SEVERE_COST_BPS)


def split_summary(index: pd.DatetimeIndex, signal: np.ndarray, target: np.ndarray, book10: dict[str, np.ndarray], book20: dict[str, np.ndarray]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for split in [VALIDATION, RECENT, MAY]:
        mask = split_mask(index, split)
        ic = row_ic(signal[mask], target[mask])
        net = book10["net"][mask]
        gross_exp = book10["gross_exposure"][mask]
        rows.append(
            {
                "split": split,
                "rows": int(mask.sum()),
                "active_hours": int(np.sum(np.isfinite(net) & (gross_exp > 0))),
                "mean_ic": clean_float(np.nanmean(ic)),
                "net_sum_10bps": clean_float(np.nansum(net)),
                "net_sum_20bps": clean_float(np.nansum(book20["net"][mask])),
                "net_mean_10bps": clean_float(np.nanmean(net)),
                "positive_hour_rate_10bps": clean_float(np.mean(net[np.isfinite(net)] > 0)) if np.isfinite(net).any() else None,
                "turnover_mean": clean_float(np.nanmean(book10["turnover"][mask])),
                "gross_exposure_mean": clean_float(np.nanmean(gross_exp)),
            }
        )
    return rows


def may_hourly_rows(index: pd.DatetimeIndex, symbols: list[str], row: pd.Series, book10: dict[str, np.ndarray]) -> list[dict[str, Any]]:
    mask = split_mask(index, MAY)
    timestamps = index[mask]
    pos = book10["pos"][mask]
    gross_by_symbol = book10["gross_by_symbol"][mask]
    out: list[dict[str, Any]] = []
    for i, ts in enumerate(timestamps):
        rec = {
            "candidate_id": str(row["candidate_id"]),
            "timestamp": ts.isoformat(),
            "net_10bps": clean_float(book10["net"][mask][i]),
            "gross": clean_float(book10["gross"][mask][i]),
            "fee": clean_float(book10["fee"][mask][i]),
            "turnover": clean_float(book10["turnover"][mask][i]),
            "gross_exposure": clean_float(book10["gross_exposure"][mask][i]),
        }
        for j, sym in enumerate(symbols):
            rec[f"position_{sym}"] = clean_float(pos[i, j])
            rec[f"gross_pnl_{sym}"] = clean_float(gross_by_symbol[i, j])
        out.append(rec)
    return out


def may_symbol_contribution(symbols: list[str], row: pd.Series, book10: dict[str, np.ndarray], index: pd.DatetimeIndex) -> list[dict[str, Any]]:
    mask = split_mask(index, MAY)
    pos = book10["pos"][mask]
    gross_by_symbol = book10["gross_by_symbol"][mask]
    rows: list[dict[str, Any]] = []
    for j, sym in enumerate(symbols):
        symbol_gross = gross_by_symbol[:, j]
        symbol_pos = pos[:, j]
        rows.append(
            {
                "candidate_id": str(row["candidate_id"]),
                "symbol": sym,
                "gross_pnl_sum_may": clean_float(np.nansum(symbol_gross)),
                "positive_hour_rate_may": clean_float(np.mean(symbol_gross[np.isfinite(symbol_gross)] > 0)) if np.isfinite(symbol_gross).any() else None,
                "long_hours": int(np.sum(symbol_pos > 0)),
                "short_hours": int(np.sum(symbol_pos < 0)),
                "flat_hours": int(np.sum(symbol_pos == 0)),
                "avg_position": clean_float(np.nanmean(symbol_pos)),
                "avg_abs_position": clean_float(np.nanmean(np.abs(symbol_pos))),
            }
        )
    return rows


def attribution_rows(index: pd.DatetimeIndex, row: pd.Series, book10: dict[str, np.ndarray]) -> dict[str, Any]:
    mask = split_mask(index, MAY)
    net = book10["net"][mask]
    gross = book10["gross"][mask]
    finite = np.isfinite(net)
    losses = net[finite & (net < 0)]
    sorted_losses = np.sort(losses)
    top10_loss_abs = float(np.sum(np.abs(sorted_losses[:10]))) if len(sorted_losses) else 0.0
    total_loss_abs = float(np.sum(np.abs(losses))) if len(losses) else 0.0
    worst_idx = int(np.nanargmin(net)) if finite.any() else -1
    return {
        "candidate_id": str(row["candidate_id"]),
        "production_family": str(row["production_family"]),
        "expression": str(row["expression"]),
        "source_fields": str(row.get("source_fields", "")),
        "source_field_families": str(row.get("source_field_families", "")),
        "may_net_sum_10bps": clean_float(np.nansum(net)),
        "may_gross_sum": clean_float(np.nansum(gross)),
        "may_fee_sum": clean_float(np.nansum(book10["fee"][mask])),
        "may_positive_hour_rate": clean_float(np.mean(net[finite] > 0)) if finite.any() else None,
        "may_loss_hour_count": int(np.sum(finite & (net < 0))),
        "may_active_hour_count": int(np.sum(finite & (book10["gross_exposure"][mask] > 0))),
        "may_worst_hour": index[mask][worst_idx].isoformat() if worst_idx >= 0 else "",
        "may_worst_hour_net": clean_float(net[worst_idx]) if worst_idx >= 0 else None,
        "may_top10_loss_share": clean_float(top10_loss_abs / total_loss_abs) if total_loss_abs > 0 else None,
        "may_total_loss_abs": clean_float(total_loss_abs),
    }


def control_contamination_detail(wide_controls: pd.DataFrame, clue_ids: set[str]) -> pd.DataFrame:
    ctrl = wide_controls[wide_controls["base_candidate_id"].isin(clue_ids)].copy()
    ctrl["val_recent_positive"] = (
        (pd.to_numeric(ctrl[f"net_sum_10bps__{VALIDATION}"], errors="coerce") > 0)
        & (pd.to_numeric(ctrl[f"net_sum_10bps__{RECENT}"], errors="coerce") > 0)
    )
    ctrl["recent20_positive"] = pd.to_numeric(ctrl[f"net_sum_20bps__{RECENT}"], errors="coerce") > 0
    return ctrl[
        [
            "candidate_id",
            "base_candidate_id",
            "control_mode",
            "production_family",
            f"net_sum_10bps__{VALIDATION}",
            f"net_sum_10bps__{RECENT}",
            f"net_sum_20bps__{RECENT}",
            f"net_sum_10bps__{MAY}",
            "val_recent_positive",
            "recent20_positive",
        ]
    ].sort_values(["base_candidate_id", "control_mode"])


def wide_metrics() -> pd.DataFrame:
    metrics = pd.read_csv(A7V5_OUT_DIR / "a7v5_smoke_split_metrics.csv")
    idx = ["candidate_id", "base_candidate_id", "object_type", "control_mode", "production_family", "expression", "horizon"]
    vals = ["net_sum_10bps", "net_sum_20bps", "mean_ic", "active_hours"]
    wide = metrics.pivot_table(index=idx, columns="split", values=vals, aggfunc="first")
    wide.columns = [f"{a}__{b}" for a, b in wide.columns]
    return wide.reset_index()


def build_factor_review(selected: pd.DataFrame, attr: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    attr_by_id = attr.set_index("candidate_id")
    for _, row in selected.iterrows():
        cid = str(row["candidate_id"])
        may_net = clean_float(attr_by_id.loc[cid, "may_net_sum_10bps"]) if cid in attr_by_id.index else None
        rows.append(
            {
                "factor_id": cid,
                "formula": str(row["expression"]),
                "provenance": "A7V-3 generated agg-aware dry-run; A7V-5 capped smoke; A7V-6 pre-May dominance clue",
                "operator_path": f"{row.get('source_fields', '')} -> {row.get('transform', '')} -> {row['expression']} -> core3 top1/bottom1 next-bar smoke book",
                "data_source": "crypto_core12_1h_with_aggtrades_features_v1.parquet; core3 rows with agg_features_available=true",
                "feature_family": str(row.get("source_field_families", "")),
                "nearest_known_factors": "activity/liquidity agg notional and trade-count bucket family",
                "overlap_assessment": "high overlap; 5 clues are all activity_liquidity and 4/5 are rolling decay bucket variants",
                "family_diversity_impact": "negative; accepting would concentrate keep list in one microstructure liquidity motif",
                "cluster_coverage": "not promoted; May failure and control contamination prevent cluster-credit assignment",
                "may_net_sum_10bps": may_net,
                "keep_list_decision": "HOLD_RESEARCH",
                "required_next_action": "Treat as failure-attribution input; do not promote or expand replay until May failure is explained",
            }
        )
    return pd.DataFrame(rows)


def write_report(now: str, attribution: pd.DataFrame, symbol_contrib: pd.DataFrame, control_detail: pd.DataFrame, factor_review: pd.DataFrame, authorization: dict[str, Any]) -> None:
    symbol_summary = (
        symbol_contrib.groupby("symbol")
        .agg(
            rows=("candidate_id", "count"),
            gross_pnl_sum_may=("gross_pnl_sum_may", "sum"),
            avg_abs_position=("avg_abs_position", "mean"),
            long_hours=("long_hours", "sum"),
            short_hours=("short_hours", "sum"),
        )
        .reset_index()
    )
    lines = [
        "# Crypto A7V-7 Failure Attribution",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{authorization['decision']}`",
        "- executes_search: `False`",
        "- executes_replay: `forensic_recompute_on_a7v6_clues_only`",
        "- alpha proof / expanded replay / full search / shadow / paper / live: `NOT_AUTHORIZED`",
        "",
        "## Scope",
        "",
        "A7V-7 recomputes hourly and symbol-level attribution for the five A7V-6 pre-May dominance clues. It is a failure-attribution audit, not a candidate promotion step.",
        "",
        "May is still stress-only. The audit uses May only to explain why the pre-May clues fail; it does not tune formulas, thresholds, or rankings.",
        "",
        "## Candidate Failure Attribution",
        "",
        table(attribution, max_rows=40),
        "",
        "## May Symbol Contribution Summary",
        "",
        table(symbol_summary, max_rows=20),
        "",
        "## Symbol Contribution By Candidate",
        "",
        table(symbol_contrib, max_rows=80),
        "",
        "## Matched Control Detail",
        "",
        table(control_detail, max_rows=80),
        "",
        "## Candidate Factor Review Matrix",
        "",
        table(factor_review, max_rows=40),
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
        "",
        "## Required Next",
        "",
        "- Do not expand A7V replay from these clues; they are activity-liquidity failure-attribution objects.",
        "- If continuing aggTrades research, redefine the objective around regime/horizon or new data contracts, not the current pre-May clue family.",
        "- Complete A7U-0R consolidated raw checksum/source trace before final panel claims.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_stamp()
    clues, selected, controls = load_inputs()
    index, symbols, matrices = load_panel(selected)
    ctx = ExprContext(matrices, symbols)
    hourly: list[dict[str, Any]] = []
    symbol_rows: list[dict[str, Any]] = []
    split_rows: list[dict[str, Any]] = []
    attribution: list[dict[str, Any]] = []
    for _, row in selected.iterrows():
        signal, target, orientation, book10, book20 = evaluate_signal(index, matrices, ctx, row)
        for rec in split_summary(index, signal, target, book10, book20):
            rec.update({"candidate_id": row["candidate_id"], "expression": row["expression"], "orientation": orientation})
            split_rows.append(rec)
        hourly.extend(may_hourly_rows(index, symbols, row, book10))
        symbol_rows.extend(may_symbol_contribution(symbols, row, book10, index))
        attribution.append(attribution_rows(index, row, book10))
    split_df = pd.DataFrame(split_rows)
    hourly_df = pd.DataFrame(hourly)
    symbol_df = pd.DataFrame(symbol_rows)
    attribution_df = pd.DataFrame(attribution)
    wide = wide_metrics()
    control_detail = control_contamination_detail(wide[wide["object_type"].eq("control")], set(selected["candidate_id"]))
    factor_review = build_factor_review(selected, attribution_df)

    post_may_positive = int((attribution_df["may_net_sum_10bps"] > 0).sum())
    avg_positive_hour_rate = clean_float(attribution_df["may_positive_hour_rate"].mean())
    top_family_share = float(selected["production_family"].value_counts(normalize=True).iloc[0]) if not selected.empty else 0.0
    max_symbol_loss_share = 0.0
    total_loss = float(np.abs(symbol_df.loc[symbol_df["gross_pnl_sum_may"] < 0, "gross_pnl_sum_may"]).sum())
    if total_loss > 0:
        max_symbol_loss_share = float(np.abs(symbol_df.groupby("symbol")["gross_pnl_sum_may"].sum().min()) / total_loss)
    blockers = [
        "all_pre_may_clues_fail_may_stress",
        "activity_liquidity_family_concentration",
        "matched_control_contamination_present_in_a7v6",
    ]
    if avg_positive_hour_rate is not None and avg_positive_hour_rate < 0.50:
        blockers.append("may_positive_hour_rate_below_half")
    decision = "HOLD_A7V7_ACTIVITY_LIQUIDITY_CLUES_FAIL_MAY_STRESS"
    authorization = {
        "generated_at": now,
        "decision": decision,
        "blockers": blockers,
        "executes_search": False,
        "executes_replay": "forensic_recompute_on_a7v6_clues_only",
        "candidate_count": int(len(selected)),
        "post_may_positive_candidates": post_may_positive,
        "avg_may_positive_hour_rate": avg_positive_hour_rate,
        "top_production_family_share": clean_float(top_family_share),
        "max_symbol_loss_share_proxy": clean_float(max_symbol_loss_share),
        "authorizes_expanded_replay": False,
        "authorizes_full_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "authorizes_may_robustness_claim": False,
        "authorizes_a7u0r_source_trace": True,
        "required_next": [
            "A7U-0R consolidated raw checksum/source trace",
            "Do not promote A7V clues; all fail May stress",
            "If continuing, redesign objective/data/horizon rather than expanding current A7V clue family",
        ],
    }
    split_df.to_csv(OUT_DIR / "a7v7_split_metrics_recomputed.csv", index=False)
    hourly_df.to_csv(OUT_DIR / "a7v7_may_hourly_pnl.csv", index=False)
    symbol_df.to_csv(OUT_DIR / "a7v7_may_symbol_contribution.csv", index=False)
    attribution_df.to_csv(OUT_DIR / "a7v7_candidate_failure_attribution.csv", index=False)
    control_detail.to_csv(OUT_DIR / "a7v7_matched_control_detail.csv", index=False)
    factor_review.to_csv(OUT_DIR / "a7v7_candidate_factor_review_matrix.csv", index=False)
    write_json(OUT_DIR / "a7v7_authorization_matrix.json", authorization)
    write_json(
        OUT_DIR / "a7v7_manifest.json",
        {
            "generated_at": now,
            "decision": decision,
            "input_a7v6_dir": str(A7V6_DIR),
            "output_dir": str(OUT_DIR),
            "report": str(REPORT_PATH),
        },
    )
    write_report(now, attribution_df, symbol_df, control_detail, factor_review, authorization)
    print(json.dumps({"decision": decision, "candidate_count": len(selected), "post_may_positive": post_may_positive, "avg_may_positive_hour_rate": avg_positive_hour_rate}, indent=2))


if __name__ == "__main__":
    main()
