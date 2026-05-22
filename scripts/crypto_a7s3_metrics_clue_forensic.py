from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

import crypto_a7s2m_metrics_registry_diagnostic as a7s2m


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "runtime" / "a7s3_metrics_clue_forensic"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7S3_METRICS_CLUE_FORENSIC_20260522.md"
A7S2M_DIR = ROOT / "runtime" / "a7s2m_metrics_registry_diagnostic"

PRIMARY_EXPR = "Neg(ZScore(global_long_short_account_ratio_zscore_168h))"
PRIMARY_FAMILY = "F2_crowding_positioning"


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


def split_masks(index: pd.DatetimeIndex) -> dict[str, np.ndarray]:
    return {name: a7s2m.split_mask(index, name) for name in a7s2m.SPLITS}


def position_book(signal: np.ndarray, target: np.ndarray, orientation: float, cost_bps: float, k: int = 3) -> dict[str, np.ndarray]:
    oriented = signal * orientation
    valid = np.isfinite(oriented) & np.isfinite(target)
    valid_rows = valid.sum(axis=1) >= (2 * k)
    pos = np.zeros_like(target, dtype=float)
    if np.any(valid_rows):
        high = np.where(valid, oriented, -np.inf)
        low = np.where(valid, oriented, np.inf)
        rows = np.where(valid_rows)[0]
        long_idx = np.argpartition(high[valid_rows], -k, axis=1)[:, -k:]
        short_idx = np.argpartition(low[valid_rows], k - 1, axis=1)[:, :k]
        weight = 0.5 / k
        for r_pos, r in enumerate(rows):
            pos[r, long_idx[r_pos]] = weight
            pos[r, short_idx[r_pos]] = -weight
    gross_by_symbol = pos * target
    gross = np.nansum(gross_by_symbol, axis=1)
    prev = np.vstack([np.zeros((1, pos.shape[1])), pos[:-1, :]])
    turnover_by_symbol = np.abs(pos - prev) / 2.0
    turnover = np.nansum(turnover_by_symbol, axis=1)
    fee_by_symbol = turnover_by_symbol * (cost_bps / 10000.0)
    fee = np.nansum(fee_by_symbol, axis=1)
    return {
        "pos": pos,
        "gross_by_symbol": gross_by_symbol,
        "fee_by_symbol": fee_by_symbol,
        "net_by_symbol": gross_by_symbol - fee_by_symbol,
        "gross": gross,
        "fee": fee,
        "net": gross - fee,
        "turnover": turnover,
        "gross_exposure": np.nansum(np.abs(pos), axis=1),
    }


def evaluate_expr(index: pd.DatetimeIndex, symbols: list[str], matrices: dict[str, np.ndarray], ctx: a7s2m.ExprContext, expression: str, horizon: int) -> dict[str, Any]:
    signal = np.where(matrices["metrics_features_available"].astype(bool), ctx.eval(expression), np.nan)
    target = a7s2m.forward_open_return(matrices["open"], horizon)
    train = a7s2m.split_mask(index, "train_2024")
    base_train_ic = np.nanmean(a7s2m.row_ic(signal[train], target[train]))
    orientation = 1.0 if not np.isfinite(base_train_ic) or base_train_ic >= 0 else -1.0
    book10 = position_book(signal, target, orientation, a7s2m.PRIMARY_COST_BPS)
    book20 = position_book(signal, target, orientation, a7s2m.SEVERE_COST_BPS)
    lag1_signal = a7s2m.apply_control(signal, "lag1_stress", expression + str(horizon))
    lag2_signal = a7s2m.apply_control(lag1_signal, "lag1_stress", expression + str(horizon) + "_lag2")
    lag3_signal = a7s2m.apply_control(lag2_signal, "lag1_stress", expression + str(horizon) + "_lag3")
    lag1 = position_book(lag1_signal, target, orientation, a7s2m.PRIMARY_COST_BPS)
    lag2 = position_book(lag2_signal, target, orientation, a7s2m.PRIMARY_COST_BPS)
    lag3 = position_book(lag3_signal, target, orientation, a7s2m.PRIMARY_COST_BPS)
    return {
        "expression": expression,
        "horizon": horizon,
        "signal": signal,
        "target": target,
        "orientation": orientation,
        "base_train_ic": clean_float(base_train_ic),
        "book10": book10,
        "book20": book20,
        "lag1": lag1,
        "lag2": lag2,
        "lag3": lag3,
    }


def split_summary(index: pd.DatetimeIndex, name: str, result: dict[str, Any]) -> dict[str, Any]:
    mask = a7s2m.split_mask(index, name)
    net10 = result["book10"]["net"][mask]
    net20 = result["book20"]["net"][mask]
    return {
        "split": name,
        "expression": result["expression"],
        "horizon": result["horizon"],
        "orientation": result["orientation"],
        "base_train_ic": result["base_train_ic"],
        "active_hours": int(np.sum(np.isfinite(net10) & (result["book10"]["gross_exposure"][mask] > 0))),
        "net10": clean_float(np.nansum(net10)),
        "net20": clean_float(np.nansum(net20)),
        "lag1_net10": clean_float(np.nansum(result["lag1"]["net"][mask])),
        "lag2_net10": clean_float(np.nansum(result["lag2"]["net"][mask])),
        "lag3_net10": clean_float(np.nansum(result["lag3"]["net"][mask])),
        "turnover_mean": clean_float(np.nanmean(result["book10"]["turnover"][mask])),
        "gross_exposure_mean": clean_float(np.nanmean(result["book10"]["gross_exposure"][mask])),
    }


def symbol_contribution(index: pd.DatetimeIndex, symbols: list[str], result: dict[str, Any]) -> pd.DataFrame:
    rows = []
    for split in a7s2m.SPLITS:
        mask = a7s2m.split_mask(index, split)
        net_by_symbol = np.nansum(result["book10"]["net_by_symbol"][mask], axis=0)
        gross_by_symbol = np.nansum(result["book10"]["gross_by_symbol"][mask], axis=0)
        fee_by_symbol = np.nansum(result["book10"]["fee_by_symbol"][mask], axis=0)
        active_by_symbol = np.sum(np.abs(result["book10"]["pos"][mask]) > 0, axis=0)
        for i, symbol in enumerate(symbols):
            rows.append(
                {
                    "expression": result["expression"],
                    "horizon": result["horizon"],
                    "split": split,
                    "symbol": symbol,
                    "net10": clean_float(net_by_symbol[i]),
                    "gross": clean_float(gross_by_symbol[i]),
                    "fee": clean_float(fee_by_symbol[i]),
                    "active_hours": int(active_by_symbol[i]),
                }
            )
    return pd.DataFrame(rows)


def month_contribution(index: pd.DatetimeIndex, result: dict[str, Any]) -> pd.DataFrame:
    df = pd.DataFrame(
        {
            "timestamp": index,
            "net10": result["book10"]["net"],
            "gross_exposure": result["book10"]["gross_exposure"],
        }
    )
    df["month"] = df["timestamp"].dt.strftime("%Y-%m")
    out = (
        df.groupby("month")
        .agg(net10=("net10", "sum"), active_hours=("gross_exposure", lambda x: int(np.sum(np.asarray(x) > 0))))
        .reset_index()
    )
    out.insert(0, "horizon", result["horizon"])
    out.insert(0, "expression", result["expression"])
    return out


def top_hours(index: pd.DatetimeIndex, result: dict[str, Any], n: int = 20) -> pd.DataFrame:
    df = pd.DataFrame(
        {
            "timestamp": index,
            "net10": result["book10"]["net"],
            "gross": result["book10"]["gross"],
            "fee": result["book10"]["fee"],
            "gross_exposure": result["book10"]["gross_exposure"],
        }
    )
    df = df[df["gross_exposure"].gt(0)].copy()
    loss = df.nsmallest(n, "net10").assign(hour_type="top_loss")
    gain = df.nlargest(n, "net10").assign(hour_type="top_gain")
    out = pd.concat([loss, gain], ignore_index=True)
    out.insert(0, "horizon", result["horizon"])
    out.insert(0, "expression", result["expression"])
    return out


def control_detail(index: pd.DatetimeIndex, result: dict[str, Any]) -> pd.DataFrame:
    rows = []
    signal = result["signal"]
    target = result["target"]
    for mode in ["sign_flip", "wrong_lag", "row_shuffle", "time_shuffle"]:
        ctrl = a7s2m.apply_control(signal, mode, result["expression"] + str(result["horizon"]) + mode)
        ctrl = np.where(np.isfinite(signal), ctrl, np.nan)
        book = position_book(ctrl, target, result["orientation"], a7s2m.PRIMARY_COST_BPS)
        for split in a7s2m.SPLITS:
            mask = a7s2m.split_mask(index, split)
            rows.append(
                {
                    "expression": result["expression"],
                    "horizon": result["horizon"],
                    "control_mode": mode,
                    "split": split,
                    "net10": clean_float(np.nansum(book["net"][mask])),
                    "active_hours": int(np.sum(np.isfinite(book["net"][mask]) & (book["gross_exposure"][mask] > 0))),
                }
            )
    return pd.DataFrame(rows)


def baseline_rows(index: pd.DatetimeIndex, symbols: list[str], matrices: dict[str, np.ndarray], ctx: a7s2m.ExprContext) -> pd.DataFrame:
    expressions = [
        "ZScore(global_long_short_account_ratio_zscore_168h)",
        "Neg(ZScore(global_long_short_account_ratio_zscore_168h))",
        "Rank(global_long_short_account_ratio_zscore_168h)",
        "Neg(ZScore(global_long_short_account_ratio_change_24h))",
        "Neg(ZScore(top_long_short_account_ratio_zscore_168h))",
        "Neg(ZScore(top_long_short_position_ratio_zscore_168h))",
        "Neg(ZScore(open_interest_zscore_168h))",
    ]
    rows = []
    for expr in expressions:
        for horizon in [24, 48]:
            res = evaluate_expr(index, symbols, matrices, ctx, expr, horizon)
            for split in a7s2m.SPLITS:
                rows.append(split_summary(index, split, res))
    return pd.DataFrame(rows)


def concentration_summary(symbols_df: pd.DataFrame, months_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for horizon in sorted(symbols_df["horizon"].unique()):
        s = symbols_df[(symbols_df["horizon"].eq(horizon)) & (symbols_df["split"].eq("recent_oos_2025H2_2026Apr"))].copy()
        total_abs = s["net10"].abs().sum()
        top_share = float(s["net10"].abs().max() / total_abs) if total_abs > 0 else np.nan
        positive_symbols = int((s["net10"] > 0).sum())
        m = months_df[months_df["horizon"].eq(horizon)].copy()
        m["split_bucket"] = np.where(m["month"].between("2025-07", "2026-04"), "recent", "other")
        recent_m = m[m["split_bucket"].eq("recent")]
        total_month_abs = recent_m["net10"].abs().sum()
        top_month_share = float(recent_m["net10"].abs().max() / total_month_abs) if total_month_abs > 0 else np.nan
        rows.append(
            {
                "horizon": int(horizon),
                "recent_positive_symbols": positive_symbols,
                "recent_top_symbol_abs_share": clean_float(top_share),
                "recent_top_month_abs_share": clean_float(top_month_share),
                "recent_months_positive": int((recent_m["net10"] > 0).sum()),
                "recent_months_total": int(len(recent_m)),
            }
        )
    return pd.DataFrame(rows)


def write_report(now: str, split_df: pd.DataFrame, symbol_df: pd.DataFrame, month_df: pd.DataFrame, controls_df: pd.DataFrame, baselines_df: pd.DataFrame, concentration: pd.DataFrame, auth: dict[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Crypto A7S-3 Metrics Clue Forensic",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{auth['decision']}`",
        "- executes_search: `False`",
        "- executes_replay: `forensic_on_a7s2m_clues_only`",
        "- alpha proof / expanded replay / full search / shadow / paper / live: `NOT_AUTHORIZED`",
        "",
        "## Scope",
        "",
        "A7S-3 audits the two A7S-2M clean clues. They share the same formula and differ only by horizon, so the first question is independence and concentration, not promotion.",
        "",
        "May remains post-selection stress-only and is not used for ranking or threshold tuning.",
        "",
        "## Split Metrics",
        "",
        table(split_df, max_rows=40),
        "",
        "## Control Detail",
        "",
        table(controls_df, max_rows=80),
        "",
        "## Baseline Comparison",
        "",
        table(baselines_df, max_rows=80),
        "",
        "## Concentration Summary",
        "",
        table(concentration, max_rows=20),
        "",
        "## Recent Symbol Contribution",
        "",
        table(symbol_df[symbol_df["split"].eq("recent_oos_2025H2_2026Apr")].sort_values(["horizon", "net10"], ascending=[True, False]), max_rows=40),
        "",
        "## May Symbol Contribution",
        "",
        table(symbol_df[symbol_df["split"].eq("fresh_may_2026")].sort_values(["horizon", "net10"], ascending=[True, False]), max_rows=40),
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(auth, indent=2, sort_keys=True),
        "```",
        "",
        "## Required Next",
        "",
        "- Treat the clue as one crowding motif, not two independent candidates.",
        "- If continued, run a small A7S-4 crowding-only robustness audit with symbol/month LOO and stricter controls.",
        "- Do not run expanded search or alpha proof from A7S-3 alone.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_stamp()
    labels = pd.read_csv(A7S2M_DIR / "a7s2m_candidate_labels.csv")
    clues = labels[labels["a7s2m_label"].eq("A7S2M_RESEARCH_CLUE_FOR_FORENSIC")].copy()
    selected = pd.read_csv(A7S2M_DIR / "a7s2m_selected_candidates.csv")
    clue_selected = selected[selected["candidate_id"].isin(set(clues["candidate_id"]))].copy()
    if clue_selected.empty:
        raise RuntimeError("No A7S2M clues available for forensic")

    index, symbols, matrices, _ = a7s2m.load_panel(clue_selected)
    ctx = a7s2m.ExprContext(matrices)
    results = [evaluate_expr(index, symbols, matrices, ctx, str(row["expression"]), int(row["horizon"])) for _, row in clue_selected.iterrows()]

    split_df = pd.DataFrame([split_summary(index, split, res) for res in results for split in a7s2m.SPLITS])
    symbol_df = pd.concat([symbol_contribution(index, symbols, res) for res in results], ignore_index=True)
    month_df = pd.concat([month_contribution(index, res) for res in results], ignore_index=True)
    top_hours_df = pd.concat([top_hours(index, res) for res in results], ignore_index=True)
    controls_df = pd.concat([control_detail(index, res) for res in results], ignore_index=True)
    baselines_df = baseline_rows(index, symbols, matrices, ctx)
    concentration = concentration_summary(symbol_df, month_df)

    clue_expr_count = int(clue_selected["expression"].nunique())
    clue_family_count = int(clue_selected["production_family"].nunique())
    recent_control_positive = int(
        (
            controls_df[controls_df["split"].eq("recent_oos_2025H2_2026Apr")]
            .groupby(["horizon", "control_mode"])["net10"]
            .first()
            .gt(0)
            .sum()
        )
    )
    may_control_positive = int(
        (
            controls_df[controls_df["split"].eq("fresh_may_2026")]
            .groupby(["horizon", "control_mode"])["net10"]
            .first()
            .gt(0)
            .sum()
        )
    )
    concentration_block = bool(
        (concentration["recent_top_symbol_abs_share"].fillna(0) > 0.50).any()
        or (concentration["recent_top_month_abs_share"].fillna(0) > 0.40).any()
    )
    blockers = []
    warnings = []
    if clue_expr_count == 1:
        warnings.append("single_formula_two_horizons_not_independent")
    if clue_family_count == 1:
        warnings.append("single_family_crowding_motif")
    if recent_control_positive > 0:
        blockers.append("control_positive_in_recent_for_clue")
    if concentration_block:
        warnings.append("symbol_or_month_concentration_risk")
    if may_control_positive > 0:
        warnings.append("may_control_positive_stress_only")

    decision = "PASS_A7S3_CROWDING_CLUE_FORENSIC_COMPLETE_HOLD_PROMOTION"
    if blockers:
        decision = "HOLD_A7S3_CONTROL_BLOCKER"

    auth = {
        "generated_at": now,
        "decision": decision,
        "blockers": blockers,
        "warnings": warnings,
        "clue_count": int(len(clue_selected)),
        "unique_formula_count": clue_expr_count,
        "unique_family_count": clue_family_count,
        "recent_control_positive_count": recent_control_positive,
        "may_control_positive_count": may_control_positive,
        "executes_search": False,
        "executes_replay": "forensic_on_a7s2m_clues_only",
        "may_policy": "stress_only_not_ranking_threshold_or_selection",
        "authorizes_a7s4_small_robustness": not blockers,
        "authorizes_expanded_replay": False,
        "authorizes_full_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "required_next": [
            "Treat A7S2M clues as one global-long-short crowding motif",
            "A7S-4 small robustness only if continuing: symbol/month LOO and stronger matched controls",
            "No expanded search or proof promotion",
        ],
    }

    split_df.to_csv(OUT_DIR / "a7s3_clue_split_metrics.csv", index=False)
    symbol_df.to_csv(OUT_DIR / "a7s3_symbol_contribution.csv", index=False)
    month_df.to_csv(OUT_DIR / "a7s3_month_contribution.csv", index=False)
    top_hours_df.to_csv(OUT_DIR / "a7s3_top_hours.csv", index=False)
    controls_df.to_csv(OUT_DIR / "a7s3_control_detail.csv", index=False)
    baselines_df.to_csv(OUT_DIR / "a7s3_baseline_comparison.csv", index=False)
    concentration.to_csv(OUT_DIR / "a7s3_concentration_summary.csv", index=False)
    clue_selected.to_csv(OUT_DIR / "a7s3_clue_registry.csv", index=False)
    write_json(OUT_DIR / "a7s3_authorization_matrix.json", auth)
    write_json(OUT_DIR / "a7s3_manifest.json", {"generated_at": now, "decision": decision, "output_dir": str(OUT_DIR), "report": str(REPORT_PATH)})
    write_report(now, split_df, symbol_df, month_df, controls_df, baselines_df, concentration, auth)
    print(json.dumps({"decision": decision, "blockers": blockers, "warnings": warnings, "clues": len(clue_selected)}, indent=2))


if __name__ == "__main__":
    main()
