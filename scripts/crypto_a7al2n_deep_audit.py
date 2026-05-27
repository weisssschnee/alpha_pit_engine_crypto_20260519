from __future__ import annotations

import importlib.util
import json
import math
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


FAST_SCRIPT = REPO / "scripts" / "crypto_a7al2l_fast_derived_replay_preflight.py"
A7AL2M_CLUES = REPO / "runtime" / "a7al2m_derived_clue_forensic" / "a7al2m_clue_shortlist.csv"
A7AL2L_DECISIONS = REPO / "runtime" / "a7al2l_fast_derived_replay_preflight" / "a7al2l_fast_candidate_decisions.csv"
A7AL2K_SELECTED = REPO / "runtime" / "a7al2k_derived_generator_smoke" / "a7al2k_selected_candidates.csv"
TAXONOMY = REPO / "runtime" / "a7ak_lv3r_contract_meme_taxonomy_audit" / "a7ak_lv3r_contract_meme_taxonomy.csv"
LV1_SYMBOL_STATE = REPO / "runtime" / "a7ak_lv1_latent_state_feature_build" / "a7ak_lv1_symbol_state_coverage.csv"

OUT_DIR = REPO / "runtime" / "a7al2n_derived_deep_audit"
REPORT = REPO / "reports" / "CRYPTO_A7AL2N_DERIVED_DEEP_AUDIT_20260527.md"

DEEP_LABEL = "A7AL2M_DEEP_AUDIT_CANDIDATE"
MIN_ACTIVE_SYMBOLS = 30
PRE_MAY_SPLITS = ["validation_2025H1", "test_2025H2", "recent_oos_2026JanApr"]
AUDIT_SPLITS = PRE_MAY_SPLITS + ["known_may2026_stress"]


def load_fast_module() -> Any:
    spec = importlib.util.spec_from_file_location("a7al2l_fast", FAST_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {FAST_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


fast = load_fast_module()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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


def numeric(x: Any, default: float = np.nan) -> float:
    try:
        return float(x)
    except Exception:
        return default


def finite_tstat(x: np.ndarray) -> float:
    x = x[np.isfinite(x)]
    if len(x) < 3:
        return np.nan
    std = np.nanstd(x, ddof=1)
    if not np.isfinite(std) or std <= 0:
        return np.nan
    return float(np.nanmean(x) / std * math.sqrt(len(x)))


def portfolio_weights_and_spread(signal: np.ndarray, label: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    valid = np.isfinite(signal) & np.isfinite(label)
    valid_counts = valid.sum(axis=0)
    enough = valid_counts >= MIN_ACTIVE_SYMBOLS
    sig = np.where(valid, signal, np.nan)
    q10 = np.full(signal.shape[1], np.nan)
    q90 = np.full(signal.shape[1], np.nan)
    cols = np.where(enough)[0]
    if len(cols):
        with np.errstate(all="ignore"):
            q10[cols] = np.nanpercentile(sig[:, cols], 10, axis=0)
            q90[cols] = np.nanpercentile(sig[:, cols], 90, axis=0)
    top_mask = valid & enough.reshape(1, -1) & (signal >= q90.reshape(1, -1))
    bottom_mask = valid & enough.reshape(1, -1) & (signal <= q10.reshape(1, -1))
    top_count = top_mask.sum(axis=0)
    bottom_count = bottom_mask.sum(axis=0)
    ok = (top_count > 0) & (bottom_count > 0)
    weights = np.zeros(signal.shape, dtype=np.float64)
    if ok.any():
        top_cols = np.where(ok)[0]
        weights[:, top_cols] += top_mask[:, top_cols] / top_count[top_cols].reshape(1, -1)
        weights[:, top_cols] -= bottom_mask[:, top_cols] / bottom_count[top_cols].reshape(1, -1)
    spread = np.full(signal.shape[1], np.nan)
    spread[ok] = np.nansum(weights[:, ok] * label[:, ok], axis=0)
    return weights, spread, top_count.astype(float), bottom_count.astype(float)


def summarize_split(candidate_id: str, spread: np.ndarray, split: np.ndarray, top_count: np.ndarray, bottom_count: np.ndarray) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for split_name in fast.SPLIT_ORDER:
        mask = (split == split_name) & np.isfinite(spread)
        x = spread[mask]
        rows.append(
            {
                "candidate_id": candidate_id,
                "split": split_name,
                "n_dates": int(mask.sum()),
                "mean_oriented_spread_24h": float(np.nanmean(x)) if len(x) else np.nan,
                "spread_tstat": finite_tstat(x),
                "positive_spread_rate": float(np.nanmean(x > 0)) if len(x) else np.nan,
                "avg_top_count": float(np.nanmean(top_count[mask])) if mask.any() else np.nan,
                "avg_bottom_count": float(np.nanmean(bottom_count[mask])) if mask.any() else np.nan,
            }
        )
    return rows


def group_mask(split: np.ndarray, group: str) -> np.ndarray:
    if group == "pre_may_oos":
        return np.isin(split, PRE_MAY_SPLITS)
    if group == "audit_all":
        return np.isin(split, AUDIT_SPLITS)
    return split == group


def symbol_contrib_rows(
    candidate_id: str,
    symbols: list[str],
    weights: np.ndarray,
    label: np.ndarray,
    split: np.ndarray,
    groups: list[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    for group in groups:
        mask = group_mask(split, group)
        contrib = np.nansum(weights[:, mask] * label[:, mask], axis=1)
        exposure = np.nansum(np.abs(weights[:, mask]), axis=1)
        abs_contrib = np.abs(contrib)
        total_abs_contrib = float(abs_contrib.sum())
        total_exposure = float(exposure.sum())
        shares = abs_contrib / total_abs_contrib if total_abs_contrib > 0 else np.zeros_like(abs_contrib)
        exp_shares = exposure / total_exposure if total_exposure > 0 else np.zeros_like(exposure)
        order_abs = np.argsort(-shares)
        pos_order = np.argsort(-contrib)
        neg_order = np.argsort(contrib)
        for i, symbol in enumerate(symbols):
            rows.append(
                {
                    "candidate_id": candidate_id,
                    "group": group,
                    "symbol": symbol,
                    "contribution": float(contrib[i]),
                    "abs_contribution": float(abs_contrib[i]),
                    "abs_contribution_share": float(shares[i]) if len(shares) else 0.0,
                    "abs_exposure": float(exposure[i]),
                    "abs_exposure_share": float(exp_shares[i]) if len(exp_shares) else 0.0,
                }
            )
        summary_rows.append(
            {
                "candidate_id": candidate_id,
                "group": group,
                "top_symbol_abs_contribution_share": float(shares[order_abs[0]]) if len(order_abs) else np.nan,
                "top3_symbol_abs_contribution_share": float(shares[order_abs[:3]].sum()) if len(order_abs) else np.nan,
                "top_abs_symbol": symbols[int(order_abs[0])] if len(order_abs) else "",
                "top_positive_symbol": symbols[int(pos_order[0])] if len(pos_order) else "",
                "top_negative_symbol": symbols[int(neg_order[0])] if len(neg_order) else "",
                "total_abs_contribution": total_abs_contrib,
                "total_abs_exposure": total_exposure,
            }
        )
    return rows, summary_rows


def month_rows(candidate_id: str, timestamps: pd.DatetimeIndex, split: np.ndarray, spread: np.ndarray) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    frame = pd.DataFrame({"timestamp": timestamps, "split": split, "spread": spread})
    frame = frame[np.isfinite(frame["spread"]) & frame["split"].isin(AUDIT_SPLITS)].copy()
    if frame.empty:
        return [], {
            "candidate_id": candidate_id,
            "pre_may_top_month_abs_share": np.nan,
            "pre_may_positive_month_rate": np.nan,
            "pre_may_month_count": 0,
        }
    frame["month"] = frame["timestamp"].dt.tz_convert(None).dt.to_period("M").astype(str)
    grouped = frame.groupby(["split", "month"], as_index=False).agg(
        n_hours=("spread", "size"),
        mean_oriented_spread_24h=("spread", "mean"),
        sum_oriented_spread_24h=("spread", "sum"),
        positive_hour_rate=("spread", lambda x: float(np.mean(np.asarray(x) > 0))),
    )
    grouped.insert(0, "candidate_id", candidate_id)
    pre = grouped[grouped["split"].isin(PRE_MAY_SPLITS)]
    abs_sum = pre["sum_oriented_spread_24h"].abs()
    total_abs = float(abs_sum.sum())
    top_share = float(abs_sum.max() / total_abs) if total_abs > 0 else np.nan
    summary = {
        "candidate_id": candidate_id,
        "pre_may_top_month_abs_share": top_share,
        "pre_may_positive_month_rate": float((pre["sum_oriented_spread_24h"] > 0).mean()) if len(pre) else np.nan,
        "pre_may_month_count": int(len(pre)),
        "worst_month": str(pre.sort_values("sum_oriented_spread_24h").iloc[0]["month"]) if len(pre) else "",
        "best_month": str(pre.sort_values("sum_oriented_spread_24h", ascending=False).iloc[0]["month"]) if len(pre) else "",
    }
    return grouped.to_dict("records"), summary


def top_hour_rows(candidate_id: str, timestamps: pd.DatetimeIndex, split: np.ndarray, spread: np.ndarray) -> list[dict[str, Any]]:
    frame = pd.DataFrame({"timestamp": timestamps, "split": split, "oriented_spread_24h": spread})
    frame = frame[np.isfinite(frame["oriented_spread_24h"]) & frame["split"].isin(AUDIT_SPLITS)].copy()
    rows: list[dict[str, Any]] = []
    for label_name, part in [("worst", frame.nsmallest(10, "oriented_spread_24h")), ("best", frame.nlargest(10, "oriented_spread_24h"))]:
        for rank, (_, row) in enumerate(part.iterrows(), 1):
            rows.append(
                {
                    "candidate_id": candidate_id,
                    "tail": label_name,
                    "rank": rank,
                    "timestamp": row["timestamp"],
                    "split": row["split"],
                    "oriented_spread_24h": float(row["oriented_spread_24h"]),
                }
            )
    return rows


def beta_rows(candidate_id: str, timestamps: pd.DatetimeIndex, spread: np.ndarray, split: np.ndarray, label: np.ndarray, symbols: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    betas = {}
    for sym in ["BTCUSDT", "ETHUSDT"]:
        if sym in symbols:
            betas[sym] = label[symbols.index(sym)]
    for group in ["pre_may_oos", "known_may2026_stress"]:
        mask_group = group_mask(split, group)
        for sym, beta_ret in betas.items():
            mask = mask_group & np.isfinite(spread) & np.isfinite(beta_ret)
            x = spread[mask]
            y = beta_ret[mask]
            if len(x) < 3 or np.nanvar(y) <= 0:
                corr = np.nan
                beta = np.nan
            else:
                corr = float(np.corrcoef(x, y)[0, 1])
                beta = float(np.cov(x, y, ddof=1)[0, 1] / np.var(y, ddof=1))
            rows.append(
                {
                    "candidate_id": candidate_id,
                    "group": group,
                    "benchmark_symbol": sym,
                    "n_dates": int(mask.sum()),
                    "corr": corr,
                    "beta": beta,
                }
            )
    return rows


def group_exposure_rows(
    candidate_id: str,
    symbol_rows: pd.DataFrame,
    taxonomy: pd.DataFrame,
    state_cov: pd.DataFrame,
) -> list[dict[str, Any]]:
    frame = symbol_rows[symbol_rows["group"].eq("pre_may_oos")].merge(taxonomy, on="symbol", how="left")
    if not state_cov.empty:
        frame = frame.merge(
            state_cov[["symbol", "dominant_state_id", "dominant_state_share", "unseen_state_share"]],
            on="symbol",
            how="left",
        )
    rows: list[dict[str, Any]] = []
    dimensions = [
        "is_meme_token",
        "is_multiplier_contract",
        "meme_contract_group",
        "liquidity_tier",
        "search_stratification_group",
        "dominant_state_id",
    ]
    for dim in dimensions:
        if dim not in frame.columns:
            continue
        totals = frame.groupby(dim, dropna=False).agg(
            abs_exposure=("abs_exposure", "sum"),
            abs_contribution=("abs_contribution", "sum"),
            symbols=("symbol", "nunique"),
        )
        exp_total = float(totals["abs_exposure"].sum())
        contrib_total = float(totals["abs_contribution"].sum())
        for group_value, row in totals.reset_index().iterrows():
            rows.append(
                {
                    "candidate_id": candidate_id,
                    "dimension": dim,
                    "group_value": str(row[dim]),
                    "symbols": int(row["symbols"]),
                    "abs_exposure": float(row["abs_exposure"]),
                    "abs_exposure_share": float(row["abs_exposure"] / exp_total) if exp_total > 0 else np.nan,
                    "abs_contribution": float(row["abs_contribution"]),
                    "abs_contribution_share": float(row["abs_contribution"] / contrib_total) if contrib_total > 0 else np.nan,
                }
            )
    return rows


def concentration_value(group_rows: pd.DataFrame, dimension: str, group_value: str | bool) -> float:
    if group_rows.empty:
        return np.nan
    part = group_rows[group_rows["dimension"].eq(dimension)].copy()
    if part.empty:
        return np.nan
    key = str(group_value)
    matched = part[part["group_value"].astype(str).str.lower().eq(key.lower())]
    if matched.empty:
        return 0.0
    return float(matched["abs_contribution_share"].max())


def max_group_share(group_rows: pd.DataFrame, dimension: str) -> float:
    part = group_rows[group_rows["dimension"].eq(dimension)]
    return float(part["abs_contribution_share"].max()) if not part.empty else np.nan


def classify_deep_candidate(
    candidate_id: str,
    symbol_summary: pd.DataFrame,
    month_summary: pd.DataFrame,
    beta: pd.DataFrame,
    group_rows: pd.DataFrame,
    clue_row: pd.Series,
) -> tuple[str, list[str]]:
    reasons: list[str] = []
    sym = symbol_summary[(symbol_summary["candidate_id"].eq(candidate_id)) & (symbol_summary["group"].eq("pre_may_oos"))]
    if not sym.empty:
        top_symbol = numeric(sym.iloc[0]["top_symbol_abs_contribution_share"])
        top3_symbol = numeric(sym.iloc[0]["top3_symbol_abs_contribution_share"])
        if np.isfinite(top_symbol) and top_symbol > 0.30:
            reasons.append("symbol_concentrated")
        if np.isfinite(top3_symbol) and top3_symbol > 0.58:
            reasons.append("top3_symbol_concentrated")
    mon = month_summary[month_summary["candidate_id"].eq(candidate_id)]
    if not mon.empty:
        top_month = numeric(mon.iloc[0]["pre_may_top_month_abs_share"])
        pos_month_rate = numeric(mon.iloc[0]["pre_may_positive_month_rate"])
        if np.isfinite(top_month) and top_month > 0.45:
            reasons.append("month_concentrated")
        if np.isfinite(pos_month_rate) and pos_month_rate < 0.45:
            reasons.append("month_unstable")
    beta_part = beta[(beta["candidate_id"].eq(candidate_id)) & (beta["group"].eq("pre_may_oos"))]
    if not beta_part.empty and beta_part["corr"].abs().max(skipna=True) > 0.78:
        reasons.append("btc_eth_beta_explained")
    grp = group_rows[group_rows["candidate_id"].eq(candidate_id)]
    meme_share = concentration_value(grp, "is_meme_token", True)
    multiplier_share = concentration_value(grp, "is_multiplier_contract", True)
    top_strat_share = max_group_share(grp, "search_stratification_group")
    if np.isfinite(meme_share) and meme_share > 0.55:
        reasons.append("meme_dominated")
    if np.isfinite(multiplier_share) and multiplier_share > 0.55:
        reasons.append("multiplier_dominated")
    if np.isfinite(top_strat_share) and top_strat_share > 0.65:
        reasons.append("taxonomy_group_concentrated")
    if numeric(clue_row.get("control_dominance_ratio_premay_max")) >= 1.10:
        reasons.append("control_margin_thin")
    if bool(clue_row.get("may_same_sign_as_premay")) is False:
        reasons.append("may_stress_divergent")
    if numeric(clue_row.get("lag_recent_retention")) < 0.50:
        reasons.append("one_bar_lag_fragile")
    if not reasons:
        return "A7AL2N_DEEP_AUDIT_DIAGNOSTIC_PASS", reasons
    if "btc_eth_beta_explained" in reasons:
        return "HOLD_A7AL2N_BETA_EXPLAINED", reasons
    if "symbol_concentrated" in reasons or "top3_symbol_concentrated" in reasons:
        return "HOLD_A7AL2N_SYMBOL_CONCENTRATED", reasons
    if "month_concentrated" in reasons or "month_unstable" in reasons:
        return "HOLD_A7AL2N_MONTH_CONCENTRATED", reasons
    if "meme_dominated" in reasons or "multiplier_dominated" in reasons or "taxonomy_group_concentrated" in reasons:
        return "HOLD_A7AL2N_MEME_MULTIPLIER_DOMINATED", reasons
    if "control_margin_thin" in reasons:
        return "HOLD_A7AL2N_CONTROL_MARGIN_THIN", reasons
    if "may_stress_divergent" in reasons:
        return "HOLD_A7AL2N_STRESS_DIVERGENT", reasons
    if "one_bar_lag_fragile" in reasons:
        return "HOLD_A7AL2N_LAG_FRAGILE", reasons
    return "HOLD_A7AL2N_DEEP_AUDIT_WEAK", reasons


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    clues = pd.read_csv(A7AL2M_CLUES)
    deep = clues[clues["quality_label"].eq(DEEP_LABEL)].copy()
    selected = pd.read_csv(A7AL2K_SELECTED)
    decisions_l = pd.read_csv(A7AL2L_DECISIONS)
    deep = deep.merge(selected[["candidate_id", "expression", "expression_key", "skeleton_key", "production_key"]], on="candidate_id", how="left")
    deep = deep.merge(
        decisions_l[["candidate_id", "original_validation_spread", "original_test_spread", "original_recent_spread", "original_may_stress_spread"]],
        on="candidate_id",
        how="left",
        suffixes=("", "_a7al2l"),
    )

    fields = {"trade_close"}
    for text in deep["fields"].dropna().astype(str):
        fields.update(part for part in text.split("|") if part)
    symbols = fast.strict_symbols()
    loaded_symbols, timestamps, matrices = fast.load_panel_matrices(symbols, fields)
    split = fast.split_for_timestamps(timestamps)
    label = fast.label_matrix(matrices["trade_close"], timestamps, split)
    evaluator = fast.MatrixFormulaEvaluator(matrices, field_shift=0)

    taxonomy = pd.read_csv(TAXONOMY).drop_duplicates("symbol")
    state_cov = pd.read_csv(LV1_SYMBOL_STATE).drop_duplicates("symbol") if LV1_SYMBOL_STATE.exists() else pd.DataFrame()

    split_summary_rows: list[dict[str, Any]] = []
    symbol_rows_all: list[dict[str, Any]] = []
    symbol_summary_all: list[dict[str, Any]] = []
    month_rows_all: list[dict[str, Any]] = []
    month_summary_rows: list[dict[str, Any]] = []
    top_hour_rows_all: list[dict[str, Any]] = []
    beta_rows_all: list[dict[str, Any]] = []
    group_rows_all: list[dict[str, Any]] = []
    candidate_summary_rows: list[dict[str, Any]] = []
    eval_errors: list[dict[str, Any]] = []

    for idx, row in deep.iterrows():
        candidate_id = str(row["candidate_id"])
        expression = str(row["expression"])
        premay_spreads = [
            numeric(row.get("original_validation_spread")),
            numeric(row.get("original_test_spread")),
            numeric(row.get("original_recent_spread")),
        ]
        finite = [x for x in premay_spreads if np.isfinite(x)]
        orientation = 1.0 if not finite or np.nanmean(finite) >= 0 else -1.0
        print(f"[A7AL-2N] {candidate_id} orientation={orientation:+.0f}", flush=True)
        try:
            signal = evaluator.eval(expression)
            raw_weights, raw_spread, top_count, bottom_count = portfolio_weights_and_spread(signal, label)
            weights = raw_weights * orientation
            oriented_spread = raw_spread * orientation
            split_summary_rows.extend(summarize_split(candidate_id, oriented_spread, split, top_count, bottom_count))
            sym_rows, sym_summary = symbol_contrib_rows(
                candidate_id,
                loaded_symbols,
                weights,
                label,
                split,
                ["pre_may_oos", "known_may2026_stress", "audit_all"],
            )
            symbol_rows_all.extend(sym_rows)
            symbol_summary_all.extend(sym_summary)
            m_rows, m_summary = month_rows(candidate_id, timestamps, split, oriented_spread)
            month_rows_all.extend(m_rows)
            month_summary_rows.append(m_summary)
            top_hour_rows_all.extend(top_hour_rows(candidate_id, timestamps, split, oriented_spread))
            beta_rows_all.extend(beta_rows(candidate_id, timestamps, oriented_spread, split, label, loaded_symbols))
            sym_frame = pd.DataFrame(sym_rows)
            group_rows_all.extend(group_exposure_rows(candidate_id, sym_frame, taxonomy, state_cov))
            candidate_summary_rows.append(
                {
                    "candidate_id": candidate_id,
                    "cell": row.get("cell"),
                    "family": row.get("family"),
                    "field_families": row.get("field_families"),
                    "fields": row.get("fields"),
                    "expression": expression,
                    "orientation_from_premay": int(orientation),
                    "a7al2m_quality_label": row.get("quality_label"),
                    "control_dominance_ratio_premay_max": row.get("control_dominance_ratio_premay_max"),
                    "lag_recent_retention": row.get("lag_recent_retention"),
                    "may_same_sign_as_premay": row.get("may_same_sign_as_premay"),
                }
            )
        except Exception as exc:
            eval_errors.append({"candidate_id": candidate_id, "error": repr(exc)})

    split_summary = pd.DataFrame(split_summary_rows)
    symbol_contribution = pd.DataFrame(symbol_rows_all)
    symbol_summary = pd.DataFrame(symbol_summary_all)
    month_contribution = pd.DataFrame(month_rows_all)
    month_summary = pd.DataFrame(month_summary_rows)
    top_hours = pd.DataFrame(top_hour_rows_all)
    beta = pd.DataFrame(beta_rows_all)
    group_exposure = pd.DataFrame(group_rows_all)
    candidate_summary = pd.DataFrame(candidate_summary_rows)

    decision_rows: list[dict[str, Any]] = []
    for _, row in candidate_summary.iterrows():
        clue_row = clues[clues["candidate_id"].eq(row["candidate_id"])].iloc[0]
        label_decision, reasons = classify_deep_candidate(
            str(row["candidate_id"]),
            symbol_summary,
            month_summary,
            beta,
            group_exposure,
            clue_row,
        )
        decision_rows.append(
            {
                "candidate_id": row["candidate_id"],
                "deep_audit_label": label_decision,
                "reasons": "|".join(reasons),
            }
        )
    decisions = pd.DataFrame(decision_rows)
    if not candidate_summary.empty and not decisions.empty:
        candidate_summary = candidate_summary.merge(decisions, on="candidate_id", how="left")
        candidate_summary = candidate_summary.merge(
            split_summary.pivot_table(index="candidate_id", columns="split", values="mean_oriented_spread_24h", aggfunc="first")
            .add_prefix("oriented_spread__")
            .reset_index(),
            on="candidate_id",
            how="left",
        )
        candidate_summary = candidate_summary.merge(
            symbol_summary[symbol_summary["group"].eq("pre_may_oos")][
                ["candidate_id", "top_symbol_abs_contribution_share", "top3_symbol_abs_contribution_share", "top_abs_symbol", "top_positive_symbol", "top_negative_symbol"]
            ],
            on="candidate_id",
            how="left",
        )
        candidate_summary = candidate_summary.merge(month_summary, on="candidate_id", how="left")
        candidate_summary["warnings"] = ""
        train_col = "oriented_spread__train_2024"
        if train_col in candidate_summary.columns:
            train_warn = pd.to_numeric(candidate_summary[train_col], errors="coerce").le(0)
            candidate_summary.loc[train_warn, "warnings"] = "train_oriented_spread_nonpositive"

    decision_counts = decisions["deep_audit_label"].value_counts().rename_axis("deep_audit_label").reset_index(name="count") if not decisions.empty else pd.DataFrame()
    pass_count = int(decisions["deep_audit_label"].eq("A7AL2N_DEEP_AUDIT_DIAGNOSTIC_PASS").sum()) if not decisions.empty else 0
    warning_counts: dict[str, int] = {}
    if not candidate_summary.empty and "warnings" in candidate_summary.columns:
        for warning in candidate_summary["warnings"].dropna().astype(str):
            for part in [x for x in warning.split("|") if x]:
                warning_counts[part] = warning_counts.get(part, 0) + 1
    blockers = []
    if eval_errors:
        blockers.append("candidate_eval_errors")
    if pass_count == 0:
        blockers.append("no_deep_audit_diagnostic_pass")
    stage_decision = "PASS_A7AL2N_DEEP_AUDIT_DIAGNOSTIC_CANDIDATES_FOUND" if pass_count > 0 and not eval_errors else "HOLD_A7AL2N_NO_DEEP_AUDIT_PASS"

    manifest = {
        "generated_at": utc_now(),
        "decision": stage_decision,
        "input_clue_file": str(A7AL2M_CLUES),
        "deep_audit_candidates": int(len(deep)),
        "diagnostic_pass_count": pass_count,
        "candidate_eval_errors": len(eval_errors),
        "decision_counts": {str(r["deep_audit_label"]): int(r["count"]) for _, r in decision_counts.iterrows()} if not decision_counts.empty else {},
        "blockers": blockers,
        "warnings": warning_counts,
        "orientation_policy": "pre_may_validation_test_recent_mean_sign_only",
        "may_usage": "stress_label_only_not_used_for_orientation_or_selection",
        "latency_policy": "field_native_one_bar_lag_inherited_from_a7al2l_no_blanket_plus2h",
        "strict_symbols": len(loaded_symbols),
        "timestamps": int(len(timestamps)),
        "executes_formula_generation": False,
        "executes_deep_audit": True,
        "executes_alpha_proof": False,
        "authorizes_a7al2o_candidate_mini_replay": pass_count > 0 and not eval_errors,
        "authorizes_formula_search_execution": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }

    candidate_summary.to_csv(OUT_DIR / "a7al2n_deep_candidate_summary.csv", index=False)
    split_summary.to_csv(OUT_DIR / "a7al2n_split_summary.csv", index=False)
    symbol_contribution.to_csv(OUT_DIR / "a7al2n_symbol_contribution.csv", index=False)
    symbol_summary.to_csv(OUT_DIR / "a7al2n_symbol_concentration_summary.csv", index=False)
    month_contribution.to_csv(OUT_DIR / "a7al2n_month_contribution.csv", index=False)
    month_summary.to_csv(OUT_DIR / "a7al2n_month_concentration_summary.csv", index=False)
    top_hours.to_csv(OUT_DIR / "a7al2n_top_loss_gain_hours.csv", index=False)
    beta.to_csv(OUT_DIR / "a7al2n_beta_exposure.csv", index=False)
    group_exposure.to_csv(OUT_DIR / "a7al2n_meme_multiplier_exposure.csv", index=False)
    decisions.to_csv(OUT_DIR / "a7al2n_decision_record.csv", index=False)
    pd.DataFrame(eval_errors).to_csv(OUT_DIR / "a7al2n_eval_errors.csv", index=False)
    write_json(OUT_DIR / "a7al2n_manifest.json", manifest)

    display_cols = [
        "candidate_id",
        "cell",
        "family",
        "field_families",
        "orientation_from_premay",
        "deep_audit_label",
        "reasons",
        "warnings",
        "oriented_spread__validation_2025H1",
        "oriented_spread__test_2025H2",
        "oriented_spread__recent_oos_2026JanApr",
        "oriented_spread__known_may2026_stress",
        "top_symbol_abs_contribution_share",
        "top3_symbol_abs_contribution_share",
        "pre_may_top_month_abs_share",
    ]
    report = f"""# CRYPTO A7AL-2N Derived Deep Audit

Generated: {manifest["generated_at"]}

## Decision

```text
{stage_decision}
```

This audits the four A7AL-2M deep-audit derived clues for concentration, beta, taxonomy exposure, control-margin, and month/symbol dependence. It does not authorize alpha proof, large search, shadow, paper, or live.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Decision Counts

{md_table(decision_counts, 20)}

## Candidate Summary

{md_table(candidate_summary[[c for c in display_cols if c in candidate_summary.columns]], 20)}

## Split Summary

{md_table(split_summary, 40)}

## Beta Exposure

{md_table(beta, 40)}

## Boundary

```text
Allowed next step if diagnostic candidates pass:
  A7AL-2O candidate-specific mini replay / neutralization audit.

Not authorized:
  formula search execution
  alpha proof
  shadow / paper / live
```
"""
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
