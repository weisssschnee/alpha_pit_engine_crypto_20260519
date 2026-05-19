from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from crypto_a2_6_tradable_replay import forward_funding_cost, funding_event_rate, next_open_return
from crypto_a2_strict_replay import MatrixContext
from crypto_a7_validation_utils import (
    COST_BPS,
    METHOD_FILE,
    PURGE_EMBARGO_BARS,
    REPORT_DIR,
    RUNTIME_DIR,
    SPLITS,
    CandidateSpec,
    clean_float,
    eval_expression,
    load_core4_context,
    load_core4_specs,
    split_mask,
    summarize_returns,
)
from crypto_a7b_funding_baseline_audit import compute_multiplier, residualize, scale_book
from crypto_a7c_fundingcore_narrow_audit import (
    fundingcore_specs,
    row_shuffle_signal,
    stable_shift_signal,
    time_shuffle_signal,
)
from crypto_a7h1_nonfunding_masked_loo_audit import raw_book_from_specs_masked


A7H2_DIR = RUNTIME_DIR / "a7h2_taker_imbalance_deep_audit"
SPEC = CandidateSpec(
    "a7h_flow_rank_taker_imbalance_h6",
    "a7h_flow_001",
    "Rank(taker_imbalance)",
    6,
    "flow_liquidity",
)
PRIMARY_COST_NAME = "stress_10bp"
PRIMARY_COST_BPS = COST_BPS[PRIMARY_COST_NAME]
SEVERE_COST_NAME = "severe_20bp"
SEVERE_COST_BPS = COST_BPS[SEVERE_COST_NAME]
RNG_SEED = 20260519


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def split_summary(frame: pd.DataFrame, value_col: str, label: str) -> pd.DataFrame:
    ts = pd.DatetimeIndex(pd.to_datetime(frame["timestamp"], utc=True))
    rows = []
    for split_name in SPLITS:
        mask = split_mask(ts, split_name)
        st = summarize_returns(frame.loc[mask, value_col].to_numpy(dtype=float))
        rows.append(
            {
                "series": label,
                "split": split_name,
                **st,
                "mean_turnover": clean_float(frame.loc[mask, "turnover"].mean()) if "turnover" in frame else None,
                "mean_gross_exposure": clean_float(frame.loc[mask, "gross_exposure"].mean()) if "gross_exposure" in frame else None,
            }
        )
    return pd.DataFrame(rows)


def timing_audit(symbols: list[str]) -> tuple[pd.DataFrame, dict[str, Any]]:
    method = json.loads(METHOD_FILE.read_text(encoding="utf-8"))
    panel = Path(method["data_inputs"]["gold_panels"]["1h"])
    cols = [
        "timestamp",
        "symbol",
        "open_time_ms",
        "close_time_ms",
        "taker_buy_base_asset_volume",
        "taker_buy_quote_asset_volume",
        "volume",
        "quote_asset_volume",
        "taker_imbalance",
    ]
    df = pd.read_parquet(panel, columns=cols)
    df = df[df["symbol"].isin(symbols)].sort_values(["symbol", "open_time_ms"]).reset_index(drop=True)
    df["feature_time_ms"] = df["close_time_ms"]
    df["execution_time_ms"] = df.groupby("symbol")["open_time_ms"].shift(-1)
    df["label_start_time_ms"] = df["execution_time_ms"]
    df["label_end_time_ms"] = df["label_start_time_ms"] + SPEC.horizon * 3600_000
    df["feature_before_execution"] = df["feature_time_ms"] < df["execution_time_ms"]
    df["execution_at_label_start"] = df["execution_time_ms"] == df["label_start_time_ms"]
    df["taker_fields_present"] = (
        df["taker_buy_base_asset_volume"].notna()
        & df["taker_buy_quote_asset_volume"].notna()
        & df["volume"].notna()
        & df["quote_asset_volume"].notna()
        & df["taker_imbalance"].notna()
    )
    samples = pd.concat(
        [
            df.head(80),
            df[df["feature_before_execution"] != True].head(80),
            df[df["taker_fields_present"] != True].head(80),
            df.tail(80),
        ],
        ignore_index=True,
    )
    summary = {
        "row_count": int(len(df)),
        "symbol_count": int(df["symbol"].nunique()),
        "feature_before_execution_violations": int((~df["feature_before_execution"].fillna(True)).sum()),
        "execution_label_start_violations": int((~df["execution_at_label_start"].fillna(True)).sum()),
        "taker_field_missing_rows": int((~df["taker_fields_present"].fillna(False)).sum()),
        "taker_imbalance_nan_rate": clean_float(df["taker_imbalance"].isna().mean()),
        "min_feature_to_execution_ms": clean_float((df["execution_time_ms"] - df["feature_time_ms"]).min()),
        "median_feature_to_execution_ms": clean_float((df["execution_time_ms"] - df["feature_time_ms"]).median()),
    }
    keep_cols = [
        "timestamp",
        "symbol",
        "open_time_ms",
        "close_time_ms",
        "feature_time_ms",
        "execution_time_ms",
        "label_start_time_ms",
        "label_end_time_ms",
        "feature_before_execution",
        "execution_at_label_start",
        "taker_fields_present",
        "taker_imbalance",
    ]
    return samples[keep_cols], summary


def evaluate_placebos(index: pd.DatetimeIndex, matrices: dict[str, np.ndarray], ctx: MatrixContext) -> tuple[pd.DataFrame, pd.DataFrame]:
    base_frame, meta = eval_expression(
        index=index,
        matrices=matrices,
        ctx=ctx,
        expression=SPEC.expression,
        horizon=SPEC.horizon,
        cost_bps=0.0,
    )
    base_signal = ctx.eval(SPEC.expression)
    base_orientation = float(meta["orientation"])
    modes = {
        "original": (base_signal, base_orientation),
        "sign_flip": (base_signal, -base_orientation),
        "wrong_lag_stale_24h": (stable_shift_signal(base_signal, 24), base_orientation),
        "wrong_lag_future_24h_diagnostic": (stable_shift_signal(base_signal, -24), base_orientation),
        "row_shuffle": (row_shuffle_signal(base_signal, RNG_SEED + 31), base_orientation),
        "time_shuffle": (time_shuffle_signal(base_signal, RNG_SEED + 37), base_orientation),
    }
    rows = []
    meta_rows = []
    for mode, (signal, orientation) in modes.items():
        frame, pmeta = eval_expression(
            index=index,
            matrices=matrices,
            ctx=ctx,
            expression=SPEC.expression,
            horizon=SPEC.horizon,
            cost_bps=0.0,
            forced_signal=signal,
            forced_orientation=orientation,
        )
        frame = frame.rename(columns={"net_return": "pre_fee_return"})
        scaled = scale_book(frame, PRIMARY_COST_BPS)
        part = split_summary(scaled, "net_return", mode)
        rows.append(part)
        meta_rows.append(
            {
                "mode": mode,
                "base_orientation": base_orientation,
                "orientation": pmeta["orientation"],
                "forced_orientation": orientation,
            }
        )
    return pd.concat(rows, ignore_index=True), pd.DataFrame(meta_rows)


def symbol_contribution(
    *,
    index: pd.DatetimeIndex,
    symbols: list[str],
    matrices: dict[str, np.ndarray],
    ctx: MatrixContext,
    cost_bps: float,
) -> pd.DataFrame:
    signal = ctx.eval(SPEC.expression)
    gross_target = next_open_return(matrices["open"], SPEC.horizon)
    funding_cost = forward_funding_cost(funding_event_rate(matrices), SPEC.horizon)
    target = gross_target - funding_cost
    _, meta = eval_expression(
        index=index,
        matrices=matrices,
        ctx=ctx,
        expression=SPEC.expression,
        horizon=SPEC.horizon,
        cost_bps=0.0,
    )
    raw = raw_book_from_specs_masked(index=index, matrices=matrices, ctx=ctx, specs=[SPEC])
    multiplier = compute_multiplier(raw).to_numpy(dtype=float)[:, None]
    frame, _ = eval_expression(
        index=index,
        matrices=matrices,
        ctx=ctx,
        expression=SPEC.expression,
        horizon=SPEC.horizon,
        cost_bps=0.0,
    )
    # Reuse eval_expression position path by reconstructing positions through
    # the public helper's output assumptions is not exposed; compute directly.
    from crypto_a7_validation_utils import position_matrix

    pos = position_matrix(signal, target, float(meta["orientation"]))
    prev = np.vstack([np.zeros((1, pos.shape[1])), pos[:-1, :]])
    turnover = np.abs(pos - prev) / 2.0
    gross = pos * gross_target
    funding_drag = pos * funding_cost
    fee = turnover * (cost_bps / 10000.0)
    net = multiplier * (gross - funding_drag - fee)
    gross_scaled = multiplier * gross
    funding_scaled = multiplier * funding_drag
    fee_scaled = multiplier * fee
    turnover_scaled = multiplier * turnover
    rows = []
    ts = pd.DatetimeIndex(index)
    for split_name in SPLITS:
        mask = split_mask(ts, split_name)
        for j, symbol in enumerate(symbols):
            vals = net[mask, j]
            rows.append(
                {
                    "candidate_id": SPEC.candidate_id,
                    "symbol": symbol,
                    "split": split_name,
                    "net_sum": clean_float(np.nansum(vals)),
                    "net_mean": clean_float(np.nanmean(vals)),
                    "annualized_mean": clean_float(np.nanmean(vals) * 365 * 24),
                    "gross_sum": clean_float(np.nansum(gross_scaled[mask, j])),
                    "funding_drag_sum": clean_float(np.nansum(funding_scaled[mask, j])),
                    "fee_drag_sum": clean_float(np.nansum(fee_scaled[mask, j])),
                    "turnover_sum": clean_float(np.nansum(turnover_scaled[mask, j])),
                    "active_position_count": int(np.isfinite(vals).sum()),
                    "positive_hour_rate": clean_float(np.nanmean(vals > 0)),
                }
            )
    return pd.DataFrame(rows)


def month_leave_one_out(residual_frame: pd.DataFrame) -> pd.DataFrame:
    df = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(residual_frame["timestamp"], utc=True),
            "net_return": residual_frame["net_return"].to_numpy(dtype=float),
        }
    )
    df = df[np.isfinite(df["net_return"])].copy()
    df["month"] = df["timestamp"].dt.strftime("%Y-%m")
    rows = []
    months = sorted(df["month"].unique().tolist())
    for held_out in months:
        part = df[df["month"] != held_out]
        st = summarize_returns(part["net_return"].to_numpy(dtype=float))
        rows.append({"held_out_month": held_out, **st})
    return pd.DataFrame(rows)


def main() -> int:
    A7H2_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_now()
    index, symbols, matrices, ctx = load_core4_context(extra_features=["taker_imbalance"])

    timing_samples, timing_summary = timing_audit(symbols)
    timing_path = A7H2_DIR / "crypto_a7h2_taker_timing_samples_20260519.csv"
    timing_samples.to_csv(timing_path, index=False)

    candidate_raw = raw_book_from_specs_masked(index=index, matrices=matrices, ctx=ctx, specs=[SPEC])
    funding_raw = raw_book_from_specs_masked(index=index, matrices=matrices, ctx=ctx, specs=fundingcore_specs())
    core4_raw = raw_book_from_specs_masked(index=index, matrices=matrices, ctx=ctx, specs=load_core4_specs())
    candidate_scaled = scale_book(candidate_raw, PRIMARY_COST_BPS)
    candidate_scaled_20 = scale_book(candidate_raw, SEVERE_COST_BPS)
    funding_scaled = scale_book(funding_raw, PRIMARY_COST_BPS)
    core4_scaled = scale_book(core4_raw, PRIMARY_COST_BPS)
    residual_funding = residualize(candidate_scaled, funding_scaled)
    residual_core4 = residualize(candidate_scaled, core4_scaled)

    split_metrics = pd.concat(
        [
            split_summary(candidate_scaled, "net_return", "raw_10bp"),
            split_summary(candidate_scaled_20, "net_return", "raw_20bp"),
            split_summary(residual_funding, "net_return", "residual_vs_funding_10bp"),
            split_summary(residual_core4, "net_return", "residual_vs_core4_10bp"),
        ],
        ignore_index=True,
    )
    split_metrics.insert(0, "candidate_id", SPEC.candidate_id)

    placebo, placebo_meta = evaluate_placebos(index, matrices, ctx)
    placebo.insert(0, "candidate_id", SPEC.candidate_id)
    symbol_contrib = symbol_contribution(index=index, symbols=symbols, matrices=matrices, ctx=ctx, cost_bps=PRIMARY_COST_BPS)
    month_loo = month_leave_one_out(residual_funding)
    top_losses = candidate_scaled.sort_values("net_return").head(30).assign(candidate_id=SPEC.candidate_id)

    split_metrics_path = A7H2_DIR / "crypto_a7h2_split_metrics_20260519.csv"
    placebo_path = A7H2_DIR / "crypto_a7h2_placebo_wrong_lag_20260519.csv"
    placebo_meta_path = A7H2_DIR / "crypto_a7h2_placebo_meta_20260519.csv"
    symbol_path = A7H2_DIR / "crypto_a7h2_symbol_contribution_20260519.csv"
    month_loo_path = A7H2_DIR / "crypto_a7h2_month_leave_one_out_20260519.csv"
    top_loss_path = A7H2_DIR / "crypto_a7h2_top_loss_hours_20260519.csv"
    split_metrics.to_csv(split_metrics_path, index=False)
    placebo.to_csv(placebo_path, index=False)
    placebo_meta.to_csv(placebo_meta_path, index=False)
    symbol_contrib.to_csv(symbol_path, index=False)
    month_loo.to_csv(month_loo_path, index=False)
    top_losses.to_csv(top_loss_path, index=False)

    def metric(series: str, split: str, col: str) -> float | None:
        row = split_metrics[(split_metrics["series"] == series) & (split_metrics["split"] == split)]
        if row.empty:
            return None
        return clean_float(row.iloc[0][col])

    def placebo_metric(mode: str, split: str, col: str = "annualized_mean") -> float | None:
        row = placebo[(placebo["series"] == mode) & (placebo["split"] == split)]
        if row.empty:
            return None
        return clean_float(row.iloc[0][col])

    recent_res = metric("residual_vs_funding_10bp", "recent_oos_2025H2_2026Apr", "annualized_mean")
    may_res = metric("residual_vs_funding_10bp", "fresh_forward_2026May", "annualized_mean")
    val_res = metric("residual_vs_funding_10bp", "validation_2025H1", "annualized_mean")
    recent_dd = metric("residual_vs_funding_10bp", "recent_oos_2025H2_2026Apr", "compounded_max_dd")
    may_dd = metric("residual_vs_funding_10bp", "fresh_forward_2026May", "compounded_max_dd")
    raw_20_recent = metric("raw_20bp", "recent_oos_2025H2_2026Apr", "annualized_mean")
    raw_20_may = metric("raw_20bp", "fresh_forward_2026May", "annualized_mean")
    raw_10_recent = metric("raw_10bp", "recent_oos_2025H2_2026Apr", "annualized_mean")
    raw_10_may = metric("raw_10bp", "fresh_forward_2026May", "annualized_mean")
    sign_flip_recent = placebo_metric("sign_flip", "recent_oos_2025H2_2026Apr")
    row_shuffle_recent = placebo_metric("row_shuffle", "recent_oos_2025H2_2026Apr")
    time_shuffle_recent = placebo_metric("time_shuffle", "recent_oos_2025H2_2026Apr")
    future_recent = placebo_metric("wrong_lag_future_24h_diagnostic", "recent_oos_2025H2_2026Apr")
    month_loo_min = clean_float(month_loo["annualized_mean"].min())
    month_loo_positive_rate = clean_float((month_loo["annualized_mean"] > 0).mean())
    recent_symbols = symbol_contrib[symbol_contrib["split"] == "recent_oos_2025H2_2026Apr"]
    may_symbols = symbol_contrib[symbol_contrib["split"] == "fresh_forward_2026May"]
    recent_symbol_positive_rate = clean_float((recent_symbols["annualized_mean"] > 0).mean())
    may_symbol_positive_rate = clean_float((may_symbols["annualized_mean"] > 0).mean())

    blockers = []
    warnings = []
    if timing_summary["feature_before_execution_violations"] > 0:
        blockers.append("taker_timing_blocker")
    if timing_summary["taker_imbalance_nan_rate"] is not None and timing_summary["taker_imbalance_nan_rate"] > 0.001:
        blockers.append("taker_field_coverage_blocker")
    elif timing_summary["taker_field_missing_rows"] > 0:
        warnings.append("minor_taker_field_missing_rows")
    if val_res is None or val_res <= 0 or recent_res is None or recent_res <= 0 or may_res is None or may_res <= 0:
        blockers.append("residual_vs_funding_not_positive_across_validation_recent_may")
    if raw_10_recent is None or raw_10_may is None or raw_10_recent <= 0 or raw_10_may <= 0:
        blockers.append("standalone_raw_10bp_negative_recent_or_may")
    if recent_dd is not None and recent_dd < -0.35:
        warnings.append("recent_residual_drawdown_large")
    if may_dd is not None and may_dd < -0.12:
        warnings.append("may_residual_drawdown_large")
    if raw_20_recent is None or raw_20_recent <= 0:
        warnings.append("raw_20bp_recent_not_positive")
    if raw_20_may is None or raw_20_may <= 0:
        warnings.append("raw_20bp_may_not_positive")
    if sign_flip_recent is not None and sign_flip_recent > 0:
        blockers.append("sign_flip_recent_positive")
    if row_shuffle_recent is not None and recent_res is not None and row_shuffle_recent > max(0.0, 0.5 * recent_res):
        blockers.append("row_shuffle_recent_too_strong")
    if time_shuffle_recent is not None and recent_res is not None and time_shuffle_recent > max(0.0, 0.5 * recent_res):
        blockers.append("time_shuffle_recent_too_strong")
    if future_recent is not None and recent_res is not None and future_recent > 1.25 * recent_res:
        warnings.append("wrong_lag_future_flow_stronger_than_original")
    if month_loo_positive_rate is not None and month_loo_positive_rate < 0.70:
        warnings.append("month_leave_one_out_weak")
    if recent_symbol_positive_rate is not None and recent_symbol_positive_rate < 0.70:
        blockers.append("standalone_recent_symbol_contribution_weak")
    if may_symbol_positive_rate is not None and may_symbol_positive_rate < 0.50:
        blockers.append("standalone_may_symbol_contribution_weak")

    decision = "PASS_A7H2_TAKER_IMBALANCE_DEEP_AUDIT_CANDIDATE" if not blockers else "HOLD_A7H2_TAKER_IMBALANCE_UNRESOLVED"
    manifest = {
        "generated_at": now,
        "decision": decision,
        "alpha_proof_status": "NOT_ALPHA_PROOF",
        "blockers": blockers,
        "warnings": warnings,
        "candidate": {
            "candidate_id": SPEC.candidate_id,
            "expression": SPEC.expression,
            "horizon": SPEC.horizon,
        },
        "key_metrics": {
            "validation_residual_vs_funding_ann": val_res,
            "recent_residual_vs_funding_ann": recent_res,
            "fresh_may_residual_vs_funding_ann": may_res,
            "recent_residual_dd": recent_dd,
            "fresh_may_residual_dd": may_dd,
            "raw_20bp_recent_ann": raw_20_recent,
            "raw_20bp_may_ann": raw_20_may,
            "raw_10bp_recent_ann": raw_10_recent,
            "raw_10bp_may_ann": raw_10_may,
            "month_loo_positive_rate": month_loo_positive_rate,
            "month_loo_min_ann": month_loo_min,
            "recent_symbol_positive_rate": recent_symbol_positive_rate,
            "may_symbol_positive_rate": may_symbol_positive_rate,
            "sign_flip_recent_ann": sign_flip_recent,
            "row_shuffle_recent_ann": row_shuffle_recent,
            "time_shuffle_recent_ann": time_shuffle_recent,
            "wrong_lag_future_recent_ann": future_recent,
            **timing_summary,
        },
        "outputs": {
            "timing_samples": str(timing_path),
            "split_metrics": str(split_metrics_path),
            "placebo_wrong_lag": str(placebo_path),
            "placebo_meta": str(placebo_meta_path),
            "symbol_contribution": str(symbol_path),
            "month_leave_one_out": str(month_loo_path),
            "top_loss_hours": str(top_loss_path),
        },
    }
    manifest_path = A7H2_DIR / "crypto_a7h2_manifest_20260519.json"
    write_json(manifest_path, manifest)

    report_path = REPORT_DIR / "CRYPTO_A7H2_TAKER_IMBALANCE_DEEP_AUDIT_20260519.md"
    lines = [
        "# Crypto A7H-2 Taker Imbalance Deep Audit",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{decision}`",
        "- evidence_level: `deep_candidate_audit_only_not_alpha_proof`",
        f"- blockers: `{blockers}`",
        f"- warnings: `{warnings}`",
        "",
        "## Candidate",
        "",
        f"- candidate_id: `{SPEC.candidate_id}`",
        f"- expression: `{SPEC.expression}`",
        f"- horizon: `{SPEC.horizon}`",
        "",
        "## Timing Contract",
        "",
        f"- feature_before_execution_violations: `{timing_summary['feature_before_execution_violations']}`",
        f"- taker_field_missing_rows: `{timing_summary['taker_field_missing_rows']}`",
        f"- min_feature_to_execution_ms: `{timing_summary['min_feature_to_execution_ms']}`",
        "",
        "## Split Metrics",
        "",
        "| series | split | ann mean | DD | hit rate | turnover |",
        "|---|---|---:|---:|---:|---:|",
    ]
    show = split_metrics[
        split_metrics["series"].isin(["raw_10bp", "raw_20bp", "residual_vs_funding_10bp", "residual_vs_core4_10bp"])
    ]
    for _, row in show.iterrows():
        lines.append(
            f"| `{row['series']}` | `{row['split']}` | "
            f"{row['annualized_mean'] if pd.notna(row['annualized_mean']) else 0:.4f} | "
            f"{row['compounded_max_dd'] if pd.notna(row['compounded_max_dd']) else 0:.4f} | "
            f"{row['hit_rate'] if pd.notna(row['hit_rate']) else 0:.3f} | "
            f"{row['mean_turnover'] if pd.notna(row['mean_turnover']) else 0:.4f} |"
        )
    lines += [
        "",
        "## Placebo / Wrong-Lag",
        "",
        "| mode | split | ann mean | DD | hit rate |",
        "|---|---|---:|---:|---:|",
    ]
    for _, row in placebo.iterrows():
        if row["split"] not in ["validation_2025H1", "recent_oos_2025H2_2026Apr", "fresh_forward_2026May"]:
            continue
        lines.append(
            f"| `{row['series']}` | `{row['split']}` | "
            f"{row['annualized_mean'] if pd.notna(row['annualized_mean']) else 0:.4f} | "
            f"{row['compounded_max_dd'] if pd.notna(row['compounded_max_dd']) else 0:.4f} | "
            f"{row['hit_rate'] if pd.notna(row['hit_rate']) else 0:.3f} |"
        )
    lines += [
        "",
        "## Stability Summary",
        "",
        f"- month_loo_positive_rate: `{month_loo_positive_rate}`",
        f"- month_loo_min_ann: `{month_loo_min}`",
        f"- recent_symbol_positive_rate: `{recent_symbol_positive_rate}`",
        f"- may_symbol_positive_rate: `{may_symbol_positive_rate}`",
        "",
        "## Decision Boundary",
        "",
        "- PASS here means the single taker-imbalance candidate deserves a future locked-forward/replay design audit as an alpha candidate.",
        "- If raw standalone performance is broadly negative while only residual performance is positive, classify it as a hedge/overlay clue, not an alpha candidate.",
        "- It does not authorize generator bakeoff, alpha shadow proof, paper, live, or production claims.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    decision_path = REPORT_DIR / "CRYPTO_A7H2_DECISION_RECORD_20260519.md"
    decision_lines = [
        "# Crypto A7H-2 Decision Record",
        "",
        f"- decision: `{decision}`",
        "- alpha_proof_status: `NOT_ALPHA_PROOF`",
        f"- blockers: `{blockers}`",
        f"- warnings: `{warnings}`",
        "",
        "## Conclusion",
        "",
        "A7H-2 is a deep audit of the single non-funding taker-imbalance residual candidate. It remains below alpha shadow proof; residual-only strength should not be interpreted as standalone alpha.",
    ]
    decision_path.write_text("\n".join(decision_lines) + "\n", encoding="utf-8")

    print("A7H2_REPORT=" + str(report_path))
    print("A7H2_DECISION_RECORD=" + str(decision_path))
    print("A7H2_MANIFEST=" + str(manifest_path))
    print("DECISION=" + decision)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
