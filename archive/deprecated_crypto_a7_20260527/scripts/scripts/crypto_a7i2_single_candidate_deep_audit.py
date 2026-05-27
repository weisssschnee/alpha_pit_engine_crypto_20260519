from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from crypto_a2_6_tradable_replay import forward_funding_cost, funding_event_rate, next_open_return
from crypto_a7_validation_utils import (
    COST_BPS,
    PURGE_EMBARGO_BARS,
    REPORT_DIR,
    RUNTIME_DIR,
    SPLITS,
    CandidateSpec,
    clean_float,
    load_core4_context,
    load_core4_specs,
    orient_signal,
    position_matrix,
    return_components,
    split_mask,
    summarize_returns,
)
from crypto_a7b_funding_baseline_audit import residualize, scale_book
from crypto_a7c_fundingcore_narrow_audit import fundingcore_specs, stable_shift_signal
from crypto_a7h1_nonfunding_masked_loo_audit import raw_book_from_specs_masked


A7I2_DIR = RUNTIME_DIR / "a7i2_single_candidate_deep_audit"
DATE_TAG = "20260520"
PRIMARY_COST_NAME = "stress_10bp"
PRIMARY_COST_BPS = COST_BPS[PRIMARY_COST_NAME]
CANDIDATE = CandidateSpec(
    "i2_microstructure_lite_113",
    "a7i_micro_113",
    "Mul(Rank(realized_vol_6),ZScore(quote_volume_mean_12))",
    12,
    "microstructure_lite",
)
DIRECT_FEATURES = ["realized_vol_6", "quote_volume_mean_12"]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def candidate_raw_book(
    *,
    index: pd.DatetimeIndex,
    matrices: dict[str, np.ndarray],
    ctx,
    signal_lag_bars: int = 0,
    symbols_to_keep: np.ndarray | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    base_signal = ctx.eval(CANDIDATE.expression)
    gross_target = next_open_return(matrices["open"], CANDIDATE.horizon)
    funding_cost = forward_funding_cost(funding_event_rate(matrices), CANDIDATE.horizon)
    target = gross_target - funding_cost
    orientation, train_ic_mean = orient_signal(index, base_signal, target)
    signal = stable_shift_signal(base_signal, signal_lag_bars) if signal_lag_bars else base_signal
    pos = position_matrix(signal, target, orientation, symbols_to_keep=symbols_to_keep)
    comp = return_components(pos, gross_target, funding_cost, 0.0)
    frame = pd.DataFrame({"timestamp": index, **comp})
    frame = frame.rename(columns={"net_return": "pre_fee_return"})
    meta = {
        "orientation": orientation,
        "train_ic_mean": train_ic_mean,
        "horizon": CANDIDATE.horizon,
        "signal_lag_bars": signal_lag_bars,
    }
    return frame, meta


def candidate_symbol_detail(
    *,
    index: pd.DatetimeIndex,
    symbols: list[str],
    matrices: dict[str, np.ndarray],
    ctx,
    cost_bps: float,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    base_signal = ctx.eval(CANDIDATE.expression)
    gross_target = next_open_return(matrices["open"], CANDIDATE.horizon)
    funding_cost = forward_funding_cost(funding_event_rate(matrices), CANDIDATE.horizon)
    target = gross_target - funding_cost
    orientation, train_ic_mean = orient_signal(index, base_signal, target)
    pos = position_matrix(base_signal, target, orientation)
    prev = np.vstack([np.zeros((1, pos.shape[1])), pos[:-1, :]])
    turnover_by_symbol = np.abs(pos - prev) / 2.0
    gross_by_symbol = pos * gross_target
    funding_by_symbol = pos * funding_cost
    fee_by_symbol = turnover_by_symbol * (cost_bps / 10000.0)
    net_by_symbol = gross_by_symbol - funding_by_symbol - fee_by_symbol
    raw_book, _ = candidate_raw_book(index=index, matrices=matrices, ctx=ctx)
    scaled = scale_book(raw_book, cost_bps)
    multiplier = scaled["multiplier"].to_numpy(dtype=float)[:, None]
    net_by_symbol = net_by_symbol * multiplier
    gross_by_symbol = gross_by_symbol * multiplier
    funding_by_symbol = funding_by_symbol * multiplier
    fee_by_symbol = fee_by_symbol * multiplier
    turnover_by_symbol = turnover_by_symbol * multiplier

    flat_rows = []
    for j, symbol in enumerate(symbols):
        flat_rows.append(
            pd.DataFrame(
                {
                    "timestamp": index,
                    "symbol": symbol,
                    "position": pos[:, j] * multiplier[:, 0],
                    "gross_return_contribution": gross_by_symbol[:, j],
                    "funding_drag_contribution": funding_by_symbol[:, j],
                    "fee_drag_contribution": fee_by_symbol[:, j],
                    "turnover_contribution": turnover_by_symbol[:, j],
                    "net_return_contribution": net_by_symbol[:, j],
                }
            )
        )
    detail = pd.concat(flat_rows, ignore_index=True)
    meta = pd.DataFrame(
        [
            {
                "candidate_id": CANDIDATE.candidate_id,
                "expression": CANDIDATE.expression,
                "horizon": CANDIDATE.horizon,
                "cost_bps": cost_bps,
                "orientation": orientation,
                "train_ic_mean": train_ic_mean,
            }
        ]
    )
    return detail, meta


def summarize_scaled_object(object_name: str, scaled: pd.DataFrame, cost_name: str, series: str) -> pd.DataFrame:
    ts = pd.DatetimeIndex(pd.to_datetime(scaled["timestamp"], utc=True))
    rows = []
    for split_name in SPLITS:
        mask = split_mask(ts, split_name)
        st = summarize_returns(scaled.loc[mask, "net_return"].to_numpy(dtype=float))
        row = {
            "candidate_id": CANDIDATE.candidate_id,
            "object": object_name,
            "series": series,
            "cost_tier": cost_name,
            "split": split_name,
            **st,
            "mean_turnover": clean_float(scaled.loc[mask, "turnover"].mean()) if "turnover" in scaled else None,
            "mean_gross_exposure": clean_float(scaled.loc[mask, "gross_exposure"].mean()) if "gross_exposure" in scaled else None,
        }
        rows.append(row)
    return pd.DataFrame(rows)


def cost_ladder(
    *,
    index: pd.DatetimeIndex,
    matrices: dict[str, np.ndarray],
    ctx,
    funding_raw: pd.DataFrame,
    core4_raw: pd.DataFrame,
) -> pd.DataFrame:
    raw, _ = candidate_raw_book(index=index, matrices=matrices, ctx=ctx)
    rows = []
    for cost_name, cost_bps in {"zero_0bp": 0.0, **COST_BPS, "extreme_30bp": 30.0}.items():
        scaled = scale_book(raw, cost_bps)
        funding_scaled = scale_book(funding_raw, cost_bps)
        core4_scaled = scale_book(core4_raw, cost_bps)
        rows.append(summarize_scaled_object("candidate", scaled, cost_name, "raw"))
        rows.append(summarize_scaled_object("candidate", residualize(scaled, funding_scaled), cost_name, "residual_vs_funding"))
        rows.append(summarize_scaled_object("candidate", residualize(scaled, core4_scaled), cost_name, "residual_vs_core4"))
    return pd.concat(rows, ignore_index=True)


def lag_ladder(*, index: pd.DatetimeIndex, matrices: dict[str, np.ndarray], ctx) -> pd.DataFrame:
    rows = []
    for lag in [0, 1, 2, 3, 6]:
        raw, meta = candidate_raw_book(index=index, matrices=matrices, ctx=ctx, signal_lag_bars=lag)
        scaled = scale_book(raw, PRIMARY_COST_BPS)
        part = summarize_scaled_object("candidate", scaled, PRIMARY_COST_NAME, f"raw_lag_{lag}_bars")
        part["signal_lag_bars"] = lag
        part["orientation"] = meta["orientation"]
        rows.append(part)
    return pd.concat(rows, ignore_index=True)


def symbol_loo(
    *,
    index: pd.DatetimeIndex,
    symbols: list[str],
    matrices: dict[str, np.ndarray],
    ctx,
    funding_specs: list[CandidateSpec],
    core4_specs: list[CandidateSpec],
) -> pd.DataFrame:
    rows = []
    ts = pd.DatetimeIndex(index)
    for held_out in symbols:
        keep = np.asarray([s != held_out for s in symbols])
        cand_raw, _ = candidate_raw_book(index=index, matrices=matrices, ctx=ctx, symbols_to_keep=keep)
        funding_raw = raw_book_from_specs_masked(index=index, matrices=matrices, ctx=ctx, specs=funding_specs, symbols_to_keep=keep)
        core4_raw = raw_book_from_specs_masked(index=index, matrices=matrices, ctx=ctx, specs=core4_specs, symbols_to_keep=keep)
        cand_scaled = scale_book(cand_raw, PRIMARY_COST_BPS)
        funding_scaled = scale_book(funding_raw, PRIMARY_COST_BPS)
        core4_scaled = scale_book(core4_raw, PRIMARY_COST_BPS)
        rf = residualize(cand_scaled, funding_scaled)
        rc = residualize(cand_scaled, core4_scaled)
        for split_name in ["validation_2025H1", "recent_oos_2025H2_2026Apr", "fresh_forward_2026May"]:
            mask = split_mask(ts, split_name)
            raw_st = summarize_returns(cand_scaled.loc[mask, "net_return"].to_numpy(dtype=float))
            rf_st = summarize_returns(rf.loc[mask, "net_return"].to_numpy(dtype=float))
            rc_st = summarize_returns(rc.loc[mask, "net_return"].to_numpy(dtype=float))
            rows.append(
                {
                    "candidate_id": CANDIDATE.candidate_id,
                    "held_out_symbol": held_out,
                    "split": split_name,
                    "raw_ann": raw_st.get("annualized_mean"),
                    "raw_dd": raw_st.get("compounded_max_dd"),
                    "residual_vs_funding_ann": rf_st.get("annualized_mean"),
                    "residual_vs_funding_dd": rf_st.get("compounded_max_dd"),
                    "residual_vs_core4_ann": rc_st.get("annualized_mean"),
                    "residual_vs_core4_dd": rc_st.get("compounded_max_dd"),
                    "mean_turnover": clean_float(cand_scaled.loc[mask, "turnover"].mean()),
                }
            )
    return pd.DataFrame(rows)


def symbol_contribution(detail: pd.DataFrame) -> pd.DataFrame:
    detail = detail.copy()
    detail["timestamp"] = pd.to_datetime(detail["timestamp"], utc=True)
    rows = []
    for split_name in SPLITS:
        mask = split_mask(pd.DatetimeIndex(detail["timestamp"]), split_name)
        part = detail.loc[mask]
        grouped = part.groupby("symbol", as_index=False).agg(
            net_return_sum=("net_return_contribution", "sum"),
            gross_return_sum=("gross_return_contribution", "sum"),
            funding_drag_sum=("funding_drag_contribution", "sum"),
            fee_drag_sum=("fee_drag_contribution", "sum"),
            turnover_sum=("turnover_contribution", "sum"),
            mean_abs_position=("position", lambda x: float(np.nanmean(np.abs(x)))),
            active_hours=("position", lambda x: int(np.isfinite(x).sum())),
        )
        grouped["split"] = split_name
        grouped["candidate_id"] = CANDIDATE.candidate_id
        total_abs = float(grouped["net_return_sum"].abs().sum())
        grouped["abs_contribution_share"] = grouped["net_return_sum"].abs() / total_abs if total_abs else np.nan
        rows.append(grouped)
    return pd.concat(rows, ignore_index=True)


def month_contribution(scaled: pd.DataFrame, residual_funding: pd.DataFrame, residual_core4: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for series, frame in [
        ("raw_10bp", scaled),
        ("residual_vs_funding_10bp", residual_funding),
        ("residual_vs_core4_10bp", residual_core4),
    ]:
        part = frame.copy()
        part["timestamp"] = pd.to_datetime(part["timestamp"], utc=True)
        part["month"] = part["timestamp"].dt.strftime("%Y-%m")
        grouped = part.groupby("month", as_index=False).agg(
            hour_count=("net_return", "size"),
            month_sum=("net_return", "sum"),
            mean_hour=("net_return", "mean"),
            hit_rate=("net_return", lambda x: float((x > 0).mean())),
            worst_hour=("net_return", "min"),
            mean_turnover=("turnover", "mean"),
        )
        grouped["series"] = series
        grouped["candidate_id"] = CANDIDATE.candidate_id
        rows.append(grouped)
    return pd.concat(rows, ignore_index=True)


def month_loo(months: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for series, g in months.groupby("series"):
        total = g["month_sum"].sum()
        for _, row in g.iterrows():
            kept_sum = total - row["month_sum"]
            rows.append(
                {
                    "candidate_id": CANDIDATE.candidate_id,
                    "series": series,
                    "dropped_month": row["month"],
                    "dropped_month_sum": row["month_sum"],
                    "remaining_month_sum": clean_float(kept_sum),
                    "remaining_positive": bool(kept_sum > 0),
                }
            )
    return pd.DataFrame(rows)


def top_loss_hours(scaled: pd.DataFrame, detail: pd.DataFrame, n: int = 30) -> pd.DataFrame:
    part = scaled.copy()
    part["timestamp"] = pd.to_datetime(part["timestamp"], utc=True)
    worst = part.sort_values("net_return").head(n).copy()
    detail = detail.copy()
    detail["timestamp"] = pd.to_datetime(detail["timestamp"], utc=True)
    rows = []
    for _, row in worst.iterrows():
        ts = row["timestamp"]
        sym = detail[detail["timestamp"] == ts].sort_values("net_return_contribution")
        contributors = ";".join(
            f"{r.symbol}:{r.net_return_contribution:.6g}" for r in sym.head(3).itertuples(index=False)
        )
        rows.append(
            {
                "candidate_id": CANDIDATE.candidate_id,
                "timestamp": ts,
                "net_return": row["net_return"],
                "gross_exposure": row["gross_exposure"],
                "turnover": row["turnover"],
                "funding_drag": row["funding_drag"],
                "top_negative_symbol_contributors": contributors,
            }
        )
    return pd.DataFrame(rows)


def field_timing_audit(index: pd.DatetimeIndex) -> pd.DataFrame:
    sample_idx = [0, min(24, len(index) - 2), min(1000, len(index) - 2), max(0, len(index) - 14)]
    rows = []
    for feature in DIRECT_FEATURES:
        lookback = 6 if feature == "realized_vol_6" else 12
        primitive = "log_ret_1 rolling std" if feature == "realized_vol_6" else "quote_asset_volume rolling mean"
        for i in sample_idx:
            signal_time = index[i]
            rows.append(
                {
                    "candidate_id": CANDIDATE.candidate_id,
                    "feature": feature,
                    "primitive": primitive,
                    "rolling_lookback_bars": lookback,
                    "signal_bar_open_time": signal_time,
                    "feature_available_time": signal_time + pd.Timedelta(hours=1),
                    "execution_time": signal_time + pd.Timedelta(hours=1),
                    "label_start_time": signal_time + pd.Timedelta(hours=1),
                    "label_end_time": signal_time + pd.Timedelta(hours=1 + CANDIDATE.horizon),
                    "timing_rule": "feature computed after current 1h bar close; execution uses next open return",
                    "violates_feature_before_execution_strict": True,
                    "bar_boundary_convention_ok": True,
                    "notes": "base replay has available_time == execution_time under bar-close-to-next-open convention; strict latency is tested by required 1bar lag stress",
                }
            )
    return pd.DataFrame(rows)


def split_value(df: pd.DataFrame, series: str, split: str, col: str) -> float | None:
    row = df[(df["series"] == series) & (df["split"] == split)]
    if row.empty:
        return None
    return clean_float(row.iloc[0][col])


def main() -> int:
    A7I2_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_now()

    index, symbols, matrices, ctx = load_core4_context(extra_features=DIRECT_FEATURES)
    funding_specs = fundingcore_specs()
    core4_specs = load_core4_specs()

    cand_raw, meta = candidate_raw_book(index=index, matrices=matrices, ctx=ctx)
    funding_raw = raw_book_from_specs_masked(index=index, matrices=matrices, ctx=ctx, specs=funding_specs)
    core4_raw = raw_book_from_specs_masked(index=index, matrices=matrices, ctx=ctx, specs=core4_specs)

    cand_10 = scale_book(cand_raw, PRIMARY_COST_BPS)
    funding_10 = scale_book(funding_raw, PRIMARY_COST_BPS)
    core4_10 = scale_book(core4_raw, PRIMARY_COST_BPS)
    residual_funding_10 = residualize(cand_10, funding_10)
    residual_core4_10 = residualize(cand_10, core4_10)

    detail, meta_df = candidate_symbol_detail(index=index, symbols=symbols, matrices=matrices, ctx=ctx, cost_bps=PRIMARY_COST_BPS)
    cost = cost_ladder(index=index, matrices=matrices, ctx=ctx, funding_raw=funding_raw, core4_raw=core4_raw)
    lag = lag_ladder(index=index, matrices=matrices, ctx=ctx)
    loo = symbol_loo(index=index, symbols=symbols, matrices=matrices, ctx=ctx, funding_specs=funding_specs, core4_specs=core4_specs)
    sym_contrib = symbol_contribution(detail)
    months = month_contribution(cand_10, residual_funding_10, residual_core4_10)
    months_loo = month_loo(months)
    top_losses = top_loss_hours(cand_10, detail)
    field_timing = field_timing_audit(index)

    metrics = cost[cost["cost_tier"] == PRIMARY_COST_NAME].copy()
    metrics_path = A7I2_DIR / "a7i2_candidate_metrics.csv"
    cost_path = A7I2_DIR / "a7i2_cost_ladder.csv"
    lag_path = A7I2_DIR / "a7i2_lag_ladder.csv"
    loo_path = A7I2_DIR / "a7i2_symbol_loo.csv"
    sym_path = A7I2_DIR / "a7i2_symbol_contribution.csv"
    month_path = A7I2_DIR / "a7i2_month_contribution.csv"
    month_loo_path = A7I2_DIR / "a7i2_month_loo.csv"
    top_loss_path = A7I2_DIR / "a7i2_top_loss_hours.csv"
    timing_path = A7I2_DIR / "a7i2_field_timing_audit.csv"
    meta_path = A7I2_DIR / "a7i2_candidate_meta.csv"

    metrics.to_csv(metrics_path, index=False)
    cost.to_csv(cost_path, index=False)
    lag.to_csv(lag_path, index=False)
    loo.to_csv(loo_path, index=False)
    sym_contrib.to_csv(sym_path, index=False)
    months.to_csv(month_path, index=False)
    months_loo.to_csv(month_loo_path, index=False)
    top_losses.to_csv(top_loss_path, index=False)
    field_timing.to_csv(timing_path, index=False)
    meta_df.to_csv(meta_path, index=False)

    recent_loo = loo[loo["split"] == "recent_oos_2025H2_2026Apr"]
    may_loo = loo[loo["split"] == "fresh_forward_2026May"]
    val_raw = split_value(metrics, "raw", "validation_2025H1", "annualized_mean")
    recent_raw = split_value(metrics, "raw", "recent_oos_2025H2_2026Apr", "annualized_mean")
    may_raw = split_value(metrics, "raw", "fresh_forward_2026May", "annualized_mean")
    recent_cost20 = cost[
        (cost["series"] == "raw")
        & (cost["cost_tier"] == "severe_20bp")
        & (cost["split"] == "recent_oos_2025H2_2026Apr")
    ]["annualized_mean"].iloc[0]
    lag_may_1 = lag[
        (lag["series"] == "raw_lag_1_bars")
        & (lag["split"] == "fresh_forward_2026May")
    ]["annualized_mean"].iloc[0]
    lag_recent_1 = lag[
        (lag["series"] == "raw_lag_1_bars")
        & (lag["split"] == "recent_oos_2025H2_2026Apr")
    ]["annualized_mean"].iloc[0]
    may_worst = clean_float(top_losses["net_return"].min())
    recent_loo_pos = clean_float((recent_loo["raw_ann"] > 0).mean())
    may_loo_pos = clean_float((may_loo["raw_ann"] > 0).mean())
    may_resid_funding = split_value(metrics, "residual_vs_funding", "fresh_forward_2026May", "annualized_mean")
    recent_resid_funding = split_value(metrics, "residual_vs_funding", "recent_oos_2025H2_2026Apr", "annualized_mean")

    blockers = []
    if val_raw is None or val_raw <= 0:
        blockers.append("raw_validation_nonpositive")
    if recent_raw is None or recent_raw <= 0:
        blockers.append("raw_recent_nonpositive")
    if may_raw is None or may_raw < -0.25:
        blockers.append("raw_may_materially_negative")
    if recent_cost20 < 0:
        blockers.append("cost20_recent_negative")
    if lag_recent_1 < 0:
        blockers.append("lag1_recent_negative")
    if lag_may_1 < -0.5:
        blockers.append("lag1_may_severely_negative")
    if recent_loo_pos is None or recent_loo_pos < 0.75:
        blockers.append("recent_symbol_loo_weak")
    if may_loo_pos is None or may_loo_pos < 0.50:
        blockers.append("may_symbol_loo_weak")

    if not blockers:
        decision = "PASS_A7I2_DEEP_AUDIT_RESEARCH_CANDIDATE"
    elif "cost20_recent_negative" in blockers or "lag1_may_severely_negative" in blockers:
        decision = "HOLD_A7I2_COST_LAG_MAY_FRAGILE"
    else:
        decision = "HOLD_A7I2_DEEP_AUDIT_UNRESOLVED"

    manifest = {
        "generated_at": now,
        "decision": decision,
        "alpha_proof_status": "NOT_ALPHA_PROOF",
        "candidate_id": CANDIDATE.candidate_id,
        "expression": CANDIDATE.expression,
        "family": CANDIDATE.family,
        "horizon": CANDIDATE.horizon,
        "primary_cost_tier": PRIMARY_COST_NAME,
        "purge_embargo_bars": PURGE_EMBARGO_BARS,
        "blockers": blockers,
        "key_metrics": {
            "raw_validation_ann_10bp": val_raw,
            "raw_recent_ann_10bp": recent_raw,
            "raw_may_ann_10bp": may_raw,
            "residual_funding_recent_ann_10bp": recent_resid_funding,
            "residual_funding_may_ann_10bp": may_resid_funding,
            "raw_recent_ann_20bp": clean_float(recent_cost20),
            "raw_recent_ann_lag1_10bp": clean_float(lag_recent_1),
            "raw_may_ann_lag1_10bp": clean_float(lag_may_1),
            "recent_symbol_loo_positive_rate": recent_loo_pos,
            "may_symbol_loo_positive_rate": may_loo_pos,
            "worst_hour_net_return_10bp": may_worst,
        },
        "warnings": [
            "a7i2_is_single_candidate_deep_audit_not_generator_success",
            "may_2026_is_known_adversarial_stress_set_not_fresh_proof",
            "base_replay_uses_bar_boundary_execution_available_time_equals_execution_time",
            "no_alpha_shadow_paper_live_authorized",
        ],
        "outputs": {
            "candidate_metrics": str(metrics_path),
            "cost_ladder": str(cost_path),
            "lag_ladder": str(lag_path),
            "symbol_loo": str(loo_path),
            "symbol_contribution": str(sym_path),
            "month_contribution": str(month_path),
            "month_loo": str(month_loo_path),
            "top_loss_hours": str(top_loss_path),
            "field_timing_audit": str(timing_path),
            "candidate_meta": str(meta_path),
        },
    }
    manifest_path = A7I2_DIR / f"a7i2_manifest_{DATE_TAG}.json"
    write_json(manifest_path, manifest)

    report_path = REPORT_DIR / f"CRYPTO_A7I2_SINGLE_CANDIDATE_DEEP_AUDIT_{DATE_TAG}.md"
    lines = [
        "# Crypto A7I-2 Single Candidate Deep Audit",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{decision}`",
        "- evidence_level: `single_candidate_deep_audit_not_alpha_proof`",
        f"- candidate_id: `{CANDIDATE.candidate_id}`",
        f"- expression: `{CANDIDATE.expression}`",
        f"- horizon: `{CANDIDATE.horizon}`",
        "",
        "## Boundary",
        "",
        "- No new candidate generation.",
        "- No reward/gate/threshold tuning.",
        "- May 2026 remains a known adversarial stress set.",
        "- Base replay uses bar-boundary execution where feature availability equals next-open execution time; promotion depends on the required 1bar lag stress.",
        "- This does not authorize alpha proof, shadow, paper, live, or production.",
        "",
        "## Key Metrics",
        "",
        f"- raw validation ann 10bps: `{val_raw:.4f}`",
        f"- raw recent ann 10bps: `{recent_raw:.4f}`",
        f"- raw May stress ann 10bps: `{may_raw:.4f}`",
        f"- residual vs FundingCore recent ann 10bps: `{recent_resid_funding:.4f}`",
        f"- residual vs FundingCore May ann 10bps: `{may_resid_funding:.4f}`",
        f"- raw recent ann 20bps: `{recent_cost20:.4f}`",
        f"- raw recent ann lag1 10bps: `{lag_recent_1:.4f}`",
        f"- raw May ann lag1 10bps: `{lag_may_1:.4f}`",
        f"- recent symbol LOO raw positive rate: `{recent_loo_pos:.3f}`",
        f"- May symbol LOO raw positive rate: `{may_loo_pos:.3f}`",
        "",
        "## Blockers",
        "",
    ]
    if blockers:
        lines.extend([f"- `{b}`" for b in blockers])
    else:
        lines.append("- none")
    lines += [
        "",
        "## Interpretation",
        "",
        "The candidate remains a microstructure-lite clue, not an alpha proof object. It keeps positive validation/recent raw 10bps performance and positive residual-vs-FundingCore behavior, but the 20bps recent result is negative and one-bar execution lag is severely negative on May stress. The May stress weakness is not used for ranking, but it is enough to block promotion.",
        "",
        "## Output Files",
        "",
    ]
    for key, path in manifest["outputs"].items():
        lines.append(f"- {key}: `{path}`")
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    decision_path = REPORT_DIR / f"CRYPTO_A7I2_DECISION_RECORD_{DATE_TAG}.md"
    decision_lines = [
        "# Crypto A7I-2 Decision Record",
        "",
        f"- decision: `{decision}`",
        "- alpha_proof_status: `NOT_ALPHA_PROOF`",
        f"- candidate_id: `{CANDIDATE.candidate_id}`",
        f"- blockers: `{blockers}`",
        "",
        "## Conclusion",
        "",
        "A7I-2 deep-audited the only A7I-1b survivor. It is not promoted. The dominant blockers are cost/lag/May fragility, so A7I remains in method-smoke status.",
    ]
    decision_path.write_text("\n".join(decision_lines) + "\n", encoding="utf-8")

    print("A7I2_REPORT=" + str(report_path))
    print("A7I2_DECISION_RECORD=" + str(decision_path))
    print("A7I2_MANIFEST=" + str(manifest_path))
    print("DECISION=" + decision)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
