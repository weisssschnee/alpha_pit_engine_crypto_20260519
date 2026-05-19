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
    PURGE_EMBARGO_BARS,
    REPORT_DIR,
    RUNTIME_DIR,
    SPLITS,
    CandidateSpec,
    clean_float,
    evaluate_core4_book,
    load_core4_context,
    load_core4_specs,
    monthly_pass_rate,
    orient_signal,
    position_matrix,
    split_mask,
    summarize_returns,
)
from crypto_a7b_funding_baseline_audit import (
    RISK_VARIANT,
    residualize,
    scale_book,
    summarize_object,
)
from crypto_a7c_fundingcore_narrow_audit import (
    RNG_SEED,
    fundingcore_specs,
    may_failure_attribution,
    raw_book_from_specs,
    row_shuffle_signal,
    stable_shift_signal,
    time_shuffle_signal,
)


ROOT = Path("G:/AlphaFactory_CryptoData")
WORKSPACE = ROOT / "alphafactory_crypto"
A7D_DIR = RUNTIME_DIR / "a7d_funding_time_semantics_audit"
PANEL_1H = ROOT / "gold" / "panels" / "crypto_core12_1h_v1.parquet"
GOLD_PANEL_BUILDER = ROOT / "scripts" / "build_crypto_gold_panel_v1.py"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True), encoding="utf-8")


def summarize_scaled(object_name: str, scaled: pd.DataFrame, cost_name: str) -> pd.DataFrame:
    rows = []
    ts = pd.DatetimeIndex(pd.to_datetime(scaled["timestamp"], utc=True))
    for split_name in SPLITS:
        mask = split_mask(ts, split_name)
        st = summarize_returns(scaled.loc[mask, "net_return"].to_numpy(dtype=float))
        mon = monthly_pass_rate(scaled.rename(columns={"net_return": "tmp"}), "tmp", split_name)
        rows.append(
            {
                "object": object_name,
                "risk_variant": RISK_VARIANT,
                "cost_tier": cost_name,
                "split": split_name,
                **st,
                **mon,
                "mean_gross_exposure": clean_float(scaled.loc[mask, "gross_exposure"].mean()),
                "mean_turnover": clean_float(scaled.loc[mask, "turnover"].mean()),
            }
        )
    return pd.DataFrame(rows)


def funding_field_contract(now: str, alignment_summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "contract_id": "crypto_funding_field_contract_v1",
        "created_at": now,
        "source_panel": str(PANEL_1H),
        "panel_builder": str(GOLD_PANEL_BUILDER),
        "join_rule": "pd.merge_asof(base.open_time_ms, funding.fundingTime_ms, direction='backward', allow_exact_matches=True)",
        "fields": [
            {
                "field_name": "latest_known_funding_rate",
                "raw_source": "Binance futures fundingRate REST CSV, silver fundingRate.parquet",
                "is_predicted_or_settled": "settled_or_exchange_reported_rate_at_fundingTime; not a next-funding prediction",
                "available_time": "fundingTime_ms, then backward-asof carried into later bars",
                "funding_payment_time": "fundingTime_ms",
                "forward_filled_rule": "asof by open_time_ms; value remains until next fundingTime_ms",
                "timezone": "UTC milliseconds",
                "symbol": "core12 USDT perpetual futures",
                "contract_type": "USDT-M perpetual",
                "sign_convention": "positive funding means longs pay shorts under standard perp convention",
                "allowed_as_signal": "allowed only when fundingTime_ms <= feature_available_time",
                "known_risk": "same-hour event with fundingTime_ms > open_time_ms by a few ms is only visible on the next hourly row in the current panel",
            },
            {
                "field_name": "funding_rate_persistence_3",
                "raw_source": "derived from latest_known_funding_rate sign over funding events before asof carry",
                "is_predicted_or_settled": "derived settled/known history",
                "available_time": "same as source funding events after derivation",
                "funding_payment_time": "not a payment field",
                "forward_filled_rule": "asof-carried derived value",
                "timezone": "UTC milliseconds",
                "symbol": "core12 USDT perpetual futures",
                "contract_type": "USDT-M perpetual",
                "sign_convention": "mean sign over recent funding events",
                "allowed_as_signal": "allowed only when source fundingTime_ms <= feature_available_time",
            },
            {
                "field_name": "next_funding_rate",
                "raw_source": "not present in current gold panel",
                "is_predicted_or_settled": "future settlement or exchange estimate depending source; forbidden unless separately contracted",
                "available_time": "not available",
                "funding_payment_time": "future funding event",
                "forward_filled_rule": "not applicable",
                "timezone": "UTC milliseconds",
                "symbol": "not applicable",
                "contract_type": "not applicable",
                "sign_convention": "not applicable",
                "allowed_as_signal": "forbidden in current A7D protocol",
            },
        ],
        "observed_alignment_summary": alignment_summary,
    }


def timestamp_alignment_audit() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    cols = [
        "timestamp",
        "symbol",
        "open_time_ms",
        "close_time_ms",
        "fundingTime_ms",
        "funding_datetime_utc",
        "latest_known_funding_rate",
    ]
    df = pd.read_parquet(PANEL_1H, columns=cols).sort_values(["symbol", "open_time_ms"]).reset_index(drop=True)
    df["next_open_time_ms"] = df.groupby("symbol")["open_time_ms"].shift(-1)
    df["feature_time_ms"] = df["close_time_ms"]
    df["execution_time_ms"] = df["next_open_time_ms"]
    df["label_start_time_ms"] = df["execution_time_ms"]
    df["label_end_time_h6_ms"] = df["execution_time_ms"] + 6 * 3600_000
    df["label_end_time_h12_ms"] = df["execution_time_ms"] + 12 * 3600_000
    df["funding_field_time_ms"] = df["fundingTime_ms"]
    df["funding_payment_time_ms"] = df["fundingTime_ms"]
    df["feature_before_execution"] = df["feature_time_ms"] < df["execution_time_ms"]
    df["execution_at_label_start"] = df["execution_time_ms"] == df["label_start_time_ms"]
    df["funding_before_feature"] = df["funding_field_time_ms"] <= df["feature_time_ms"]
    df["funding_before_open"] = df["funding_field_time_ms"] <= df["open_time_ms"]
    df["open_minus_funding_ms"] = df["open_time_ms"] - df["fundingTime_ms"]
    df["current_event_exact"] = df["open_minus_funding_ms"].abs() < 1.0
    df["event_visible_within_1h_after_payment"] = (df["open_minus_funding_ms"] >= 0) & (df["open_minus_funding_ms"] <= 3600_000)
    df["prev_fundingTime_ms"] = df.groupby("symbol")["fundingTime_ms"].shift(1)
    df["current_event_by_observable_change"] = (
        df["fundingTime_ms"].notna()
        & df["prev_fundingTime_ms"].notna()
        & (df["fundingTime_ms"] != df["prev_fundingTime_ms"])
    )
    unique_events = df[["symbol", "fundingTime_ms"]].dropna().drop_duplicates()
    first_events = df.dropna(subset=["fundingTime_ms"]).groupby("symbol", as_index=False).head(1)[["symbol", "fundingTime_ms"]]
    expected_change_events = unique_events.merge(
        first_events.assign(_first_event=True),
        on=["symbol", "fundingTime_ms"],
        how="left",
    )
    expected_change_events = expected_change_events[expected_change_events["_first_event"].isna()][["symbol", "fundingTime_ms"]]
    exact_events = df.loc[df["current_event_exact"], ["symbol", "fundingTime_ms"]].dropna().drop_duplicates()
    within_1h_events = df.loc[df["event_visible_within_1h_after_payment"], ["symbol", "fundingTime_ms"]].dropna().drop_duplicates()
    observable_change_events = df.loc[df["current_event_by_observable_change"], ["symbol", "fundingTime_ms"]].dropna().drop_duplicates()
    summary = {
        "row_count": int(len(df)),
        "symbol_count": int(df["symbol"].nunique()),
        "min_timestamp": pd.to_datetime(df["timestamp"], utc=True).min().isoformat(),
        "max_timestamp": pd.to_datetime(df["timestamp"], utc=True).max().isoformat(),
        "feature_before_execution_violations": int((~df["feature_before_execution"].fillna(True)).sum()),
        "funding_before_feature_violations": int((~df["funding_before_feature"].fillna(True)).sum()),
        "funding_before_open_violations": int((~df["funding_before_open"].fillna(True)).sum()),
        "unique_symbol_funding_events_in_panel": int(len(unique_events)),
        "exact_event_detected_unique": int(len(exact_events)),
        "within_1h_event_detected_unique": int(len(within_1h_events)),
        "observable_change_expected_unique": int(len(expected_change_events)),
        "observable_change_detected_unique": int(len(observable_change_events)),
        "exact_event_detection_rate": clean_float(len(exact_events) / len(unique_events)) if len(unique_events) else None,
        "within_1h_event_detection_rate": clean_float(len(within_1h_events) / len(unique_events)) if len(unique_events) else None,
        "observable_change_event_detection_rate": (
            clean_float(len(observable_change_events) / len(expected_change_events)) if len(expected_change_events) else None
        ),
    }
    sample_cols = [
        "symbol",
        "timestamp",
        "feature_time_ms",
        "execution_time_ms",
        "label_start_time_ms",
        "label_end_time_h6_ms",
        "label_end_time_h12_ms",
        "funding_field_time_ms",
        "funding_payment_time_ms",
        "open_minus_funding_ms",
        "feature_before_execution",
        "funding_before_feature",
        "current_event_exact",
        "current_event_by_observable_change",
    ]
    samples = pd.concat(
        [
            df.head(120),
            df[df["open_minus_funding_ms"].between(1, 3600_000, inclusive="both")].head(120),
            df[df["open_minus_funding_ms"] > 3600_000].head(120),
            df.tail(120),
        ],
        ignore_index=True,
    )[sample_cols].drop_duplicates()
    diff_counts = (
        df["open_minus_funding_ms"]
        .dropna()
        .round()
        .astype("int64")
        .value_counts()
        .sort_index()
        .rename_axis("open_minus_funding_ms")
        .reset_index(name="row_count")
    )
    return samples, diff_counts, summary


def variant_matrices(matrices: dict[str, np.ndarray], variant: str) -> dict[str, np.ndarray]:
    out = {k: v.copy() for k, v in matrices.items()}
    funding_cols = ["latest_known_funding_rate", "funding_rate_persistence_3", "cs_z_latest_known_funding_rate", "cs_rank_latest_known_funding_rate"]
    for col in funding_cols:
        if col not in out:
            continue
        base = out[col]
        if variant == "F1_last_settled_stale_8h":
            out[col] = stable_shift_signal(base, 8)
        elif variant == "F2_latest_known_observable":
            out[col] = base.copy()
        elif variant == "F3_delayed_1_funding_event_16h":
            out[col] = stable_shift_signal(base, 16)
        elif variant == "F4_future_next_funding_forbidden_8h":
            out[col] = stable_shift_signal(base, -8)
        elif variant == "F5_time_shuffled_funding":
            out[col] = time_shuffle_signal(base, RNG_SEED + 11)
        elif variant == "F6_symbol_shuffled_funding":
            out[col] = row_shuffle_signal(base, RNG_SEED + 17)
        elif variant == "F7_wrong_lag_future_24h":
            out[col] = stable_shift_signal(base, -24)
        else:
            raise ValueError(f"unknown funding variant: {variant}")
    return out


def cash_book(index: pd.DatetimeIndex) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "timestamp": index,
            "gross_return": 0.0,
            "funding_drag": 0.0,
            "turnover": 0.0,
            "fee_drag": 0.0,
            "pre_fee_return": 0.0,
            "gross_exposure": 0.0,
            "net_exposure": 0.0,
        }
    )


def funding_lag_ladder(index: pd.DatetimeIndex, matrices: dict[str, np.ndarray], specs: list[CandidateSpec]) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    rows = []
    raw_books: dict[str, pd.DataFrame] = {"F0_no_funding_cash": cash_book(index)}
    variants = [
        "F1_last_settled_stale_8h",
        "F2_latest_known_observable",
        "F3_delayed_1_funding_event_16h",
        "F4_future_next_funding_forbidden_8h",
        "F5_time_shuffled_funding",
        "F6_symbol_shuffled_funding",
        "F7_wrong_lag_future_24h",
    ]
    for name in variants:
        vm = variant_matrices(matrices, name)
        raw, _ = raw_book_from_specs(index, vm, MatrixContext(vm), specs)
        raw_books[name] = raw
    for name, raw in raw_books.items():
        for cost_name, cost_bps in COST_BPS.items():
            scaled = scale_book(raw, cost_bps)
            part = summarize_object(name, scaled, cost_name)
            rows.append(part)
    return pd.concat(rows, ignore_index=True), raw_books


def component_position_decomposition(
    *,
    index: pd.DatetimeIndex,
    matrices: dict[str, np.ndarray],
    ctx: MatrixContext,
    spec: CandidateSpec,
    cost_bps: float,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    signal = ctx.eval(spec.expression)
    gross_target = next_open_return(matrices["open"], spec.horizon)
    event_rate = funding_event_rate(matrices)
    funding_cost = forward_funding_cost(event_rate, spec.horizon)
    target = gross_target - funding_cost
    orientation, train_ic_mean = orient_signal(index, signal, target)
    pos = position_matrix(signal, target, orientation)
    gross_by_symbol = pos * gross_target
    current_long_only_funding_by_symbol = np.where(pos > 0, pos * funding_cost, 0.0)
    full_signed_funding_pnl_by_symbol = -pos * funding_cost
    inverted_signed_funding_pnl_by_symbol = pos * funding_cost
    prev = np.vstack([np.zeros((1, pos.shape[1])), pos[:-1, :]])
    turnover_by_symbol = np.abs(pos - prev) / 2.0
    fee_by_symbol = turnover_by_symbol * (cost_bps / 10000.0)
    frame = pd.DataFrame(
        {
            "timestamp": index,
            "component_id": spec.cluster_id,
            "gross_price_pnl": np.nansum(gross_by_symbol, axis=1),
            "funding_current_long_only_drag": np.nansum(current_long_only_funding_by_symbol, axis=1),
            "funding_full_signed_pnl": np.nansum(full_signed_funding_pnl_by_symbol, axis=1),
            "funding_inverted_signed_pnl": np.nansum(inverted_signed_funding_pnl_by_symbol, axis=1),
            "fee_drag": np.nansum(fee_by_symbol, axis=1),
            "turnover": np.nansum(turnover_by_symbol, axis=1),
            "gross_exposure": np.nansum(np.abs(pos), axis=1),
        }
    )
    frame["net_current_long_only"] = frame["gross_price_pnl"] - frame["funding_current_long_only_drag"] - frame["fee_drag"]
    frame["net_full_signed"] = frame["gross_price_pnl"] + frame["funding_full_signed_pnl"] - frame["fee_drag"]
    frame["net_inverted_signed"] = frame["gross_price_pnl"] + frame["funding_inverted_signed_pnl"] - frame["fee_drag"]
    symbol_rows = []
    for j, symbol in enumerate(sorted(pd.read_parquet(PANEL_1H, columns=["symbol"])["symbol"].unique().tolist())):
        may = pd.DataFrame(
            {
                "timestamp": index,
                "symbol": symbol,
                "component_id": spec.cluster_id,
                "gross_price_pnl": gross_by_symbol[:, j],
                "funding_current_long_only_drag": current_long_only_funding_by_symbol[:, j],
                "funding_full_signed_pnl": full_signed_funding_pnl_by_symbol[:, j],
                "fee_drag": fee_by_symbol[:, j],
                "turnover": turnover_by_symbol[:, j],
            }
        )
        may = may[pd.to_datetime(may["timestamp"], utc=True) >= pd.Timestamp("2026-05-01T00:00:00Z")]
        symbol_rows.append(
            {
                "symbol": symbol,
                "component_id": spec.cluster_id,
                "may_gross_price_pnl_sum": clean_float(may["gross_price_pnl"].sum()),
                "may_funding_current_long_only_drag_sum": clean_float(may["funding_current_long_only_drag"].sum()),
                "may_funding_full_signed_pnl_sum": clean_float(may["funding_full_signed_pnl"].sum()),
                "may_fee_drag_sum": clean_float(may["fee_drag"].sum()),
                "may_turnover_sum": clean_float(may["turnover"].sum()),
                "may_net_current_long_only_sum": clean_float((may["gross_price_pnl"] - may["funding_current_long_only_drag"] - may["fee_drag"]).sum()),
                "may_net_full_signed_sum": clean_float((may["gross_price_pnl"] + may["funding_full_signed_pnl"] - may["fee_drag"]).sum()),
            }
        )
    meta = pd.DataFrame(
        [
            {
                "component_id": spec.cluster_id,
                "expression": spec.expression,
                "horizon": spec.horizon,
                "orientation": orientation,
                "train_ic_mean": train_ic_mean,
            }
        ]
    )
    return frame, pd.DataFrame(symbol_rows).merge(meta, on="component_id", how="left")


def payment_decomposition(index: pd.DatetimeIndex, matrices: dict[str, np.ndarray], ctx: MatrixContext, specs: list[CandidateSpec]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    frames = []
    may_symbol = []
    meta = []
    for spec in specs:
        frame, symbol_part = component_position_decomposition(index=index, matrices=matrices, ctx=ctx, spec=spec, cost_bps=COST_BPS["stress_10bp"])
        frames.append(frame)
        may_symbol.append(symbol_part)
    comp = pd.concat(frames, ignore_index=True)
    book = pd.DataFrame({"timestamp": index})
    for col in [
        "gross_price_pnl",
        "funding_current_long_only_drag",
        "funding_full_signed_pnl",
        "funding_inverted_signed_pnl",
        "fee_drag",
        "turnover",
        "gross_exposure",
        "net_current_long_only",
        "net_full_signed",
        "net_inverted_signed",
    ]:
        pivot = comp.pivot(index="timestamp", columns="component_id", values=col)
        book[col] = pivot.mean(axis=1, skipna=True).to_numpy(dtype=float)
    summary_rows = []
    for value_col in ["net_current_long_only", "net_full_signed", "net_inverted_signed", "gross_price_pnl", "funding_full_signed_pnl"]:
        for split_name in SPLITS:
            mask = split_mask(pd.DatetimeIndex(pd.to_datetime(book["timestamp"], utc=True)), split_name)
            st = summarize_returns(book.loc[mask, value_col].to_numpy(dtype=float))
            summary_rows.append({"object": value_col, "split": split_name, **st})
    return pd.DataFrame(summary_rows), book, pd.concat(may_symbol, ignore_index=True)


def residual_by_funding_version(index: pd.DatetimeIndex, matrices: dict[str, np.ndarray], core_specs: list[CandidateSpec], funding_specs: list[CandidateSpec]) -> pd.DataFrame:
    rows = []
    for name in ["F1_last_settled_stale_8h", "F2_latest_known_observable", "F4_future_next_funding_forbidden_8h"]:
        vm = variant_matrices(matrices, name)
        ctx = MatrixContext(vm)
        core_raw, _ = raw_book_from_specs(index, vm, ctx, core_specs)
        funding_raw, _ = raw_book_from_specs(index, vm, ctx, funding_specs)
        core_scaled = scale_book(core_raw, COST_BPS["stress_10bp"])
        funding_scaled = scale_book(funding_raw, COST_BPS["stress_10bp"])
        residual = residualize(core_scaled, funding_scaled)
        part = summarize_scaled(f"Core4_residual_vs_{name}", residual, "stress_10bp")
        rows.append(part)
    return pd.concat(rows, ignore_index=True)


def metric(df: pd.DataFrame, obj: str, split: str, col: str, cost: str = "stress_10bp") -> float | None:
    part = df[(df["object"] == obj) & (df["split"] == split)]
    if "cost_tier" in part.columns:
        part = part[part["cost_tier"] == cost]
    if part.empty or col not in part.columns:
        return None
    return clean_float(part.iloc[0][col])


def write_report(
    *,
    manifest: dict[str, Any],
    contract_path: Path,
    alignment_summary: dict[str, Any],
    ladder: pd.DataFrame,
    payment_summary: pd.DataFrame,
    residual: pd.DataFrame,
    may_symbol: pd.DataFrame,
    report_path: Path,
) -> None:
    ladder_display = ladder[
        (ladder["cost_tier"] == "stress_10bp")
        & (ladder["split"].isin(["validation_2025H1", "recent_oos_2025H2_2026Apr", "fresh_forward_2026May"]))
    ].copy()
    payment_display = payment_summary[payment_summary["split"].isin(["validation_2025H1", "recent_oos_2025H2_2026Apr", "fresh_forward_2026May"])].copy()
    residual_display = residual[residual["split"].isin(["validation_2025H1", "recent_oos_2025H2_2026Apr", "fresh_forward_2026May"])].copy()
    worst_may = may_symbol.sort_values("may_net_full_signed_sum").head(12)
    lines = [
        "# Crypto A7D Funding Time-Semantics Audit",
        "",
        f"- generated_at: `{manifest['generated_at']}`",
        f"- decision: `{manifest['decision']}`",
        f"- blockers: `{manifest['blockers']}`",
        f"- warnings: `{manifest['warnings']}`",
        f"- field_contract: `{contract_path}`",
        "",
        "## Field Contract Summary",
        "",
        "- `latest_known_funding_rate` is treated as a backward-asof settled/exchange-reported funding field, not a next funding prediction.",
        "- `next_funding_rate` is not present and remains forbidden for signal use.",
        "- Signal use is only allowed when `fundingTime_ms <= feature_available_time`.",
        "",
        "## Timestamp Alignment",
        "",
        f"- rows: `{alignment_summary['row_count']}`",
        f"- feature_before_execution violations: `{alignment_summary['feature_before_execution_violations']}`",
        f"- funding_before_feature violations: `{alignment_summary['funding_before_feature_violations']}`",
        f"- exact event detection rate: `{alignment_summary['exact_event_detection_rate']}`",
        f"- within 1h event visibility rate: `{alignment_summary['within_1h_event_detection_rate']}`",
        f"- observable change event detection rate: `{alignment_summary['observable_change_event_detection_rate']}`",
        "",
        "## Funding Lag Ladder",
        "",
        "| object | split | ann mean | compounded DD | month pass | mean turnover |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for _, row in ladder_display.iterrows():
        lines.append(
            f"| `{row['object']}` | `{row['split']}` | {row['annualized_mean']:.4f} | "
            f"{row['compounded_max_dd'] if pd.notna(row['compounded_max_dd']) else 0:.4f} | "
            f"{row['positive_month_rate'] if pd.notna(row['positive_month_rate']) else 0:.3f} | "
            f"{row['mean_turnover'] if pd.notna(row['mean_turnover']) else 0:.4f} |"
        )
    lines += [
        "",
        "## Funding Sign / Payment Decomposition",
        "",
        "| object | split | ann mean | compounded DD |",
        "|---|---|---:|---:|",
    ]
    for _, row in payment_display.iterrows():
        lines.append(
            f"| `{row['object']}` | `{row['split']}` | {row['annualized_mean']:.4f} | "
            f"{row['compounded_max_dd'] if pd.notna(row['compounded_max_dd']) else 0:.4f} |"
        )
    lines += [
        "",
        "## Core4 Residual By Funding Version",
        "",
        "| object | split | ann mean | compounded DD |",
        "|---|---|---:|---:|",
    ]
    for _, row in residual_display.iterrows():
        lines.append(
            f"| `{row['object']}` | `{row['split']}` | {row['annualized_mean']:.4f} | "
            f"{row['compounded_max_dd'] if pd.notna(row['compounded_max_dd']) else 0:.4f} |"
        )
    lines += [
        "",
        "## May 2026 Worst Symbol/Component Rows",
        "",
        "| symbol | component | net full signed | price pnl | funding pnl | fee | turnover |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for _, row in worst_may.iterrows():
        lines.append(
            f"| `{row['symbol']}` | `{row['component_id']}` | {row['may_net_full_signed_sum']:.4f} | "
            f"{row['may_gross_price_pnl_sum']:.4f} | {row['may_funding_full_signed_pnl_sum']:.4f} | "
            f"{row['may_fee_drag_sum']:.4f} | {row['may_turnover_sum']:.4f} |"
        )
    lines += [
        "",
        "## Bias Audit Decision",
        "",
        "- This is a linkage/data-semantics audit, not a new alpha search.",
        "- Promotion remains blocked if event detection or funding payment semantics are unresolved.",
        "- A clean result here would only allow further research; it would not imply paper/live readiness.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    A7D_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_now()
    index, symbols, matrices, ctx = load_core4_context()
    funding_specs = fundingcore_specs()
    core_specs = load_core4_specs()

    alignment_samples, event_diff_counts, alignment_summary = timestamp_alignment_audit()
    contract = funding_field_contract(now, alignment_summary)
    contract_path = REPORT_DIR / "CRYPTO_A7D_FUNDING_FIELD_CONTRACT_20260519.json"
    write_json(contract_path, contract)

    samples_path = A7D_DIR / "crypto_a7d_timestamp_alignment_samples_20260519.csv"
    event_counts_path = A7D_DIR / "crypto_a7d_funding_event_detection_counts_20260519.csv"
    alignment_samples.to_csv(samples_path, index=False)
    event_diff_counts.to_csv(event_counts_path, index=False)

    ladder, raw_books = funding_lag_ladder(index, matrices, funding_specs)
    ladder_path = A7D_DIR / "crypto_a7d_funding_lag_ladder_metrics_20260519.csv"
    ladder.to_csv(ladder_path, index=False)

    payment_summary, payment_hourly, may_symbol = payment_decomposition(index, matrices, ctx, funding_specs)
    payment_path = A7D_DIR / "crypto_a7d_funding_payment_decomposition_20260519.csv"
    payment_hourly_path = A7D_DIR / "crypto_a7d_funding_payment_hourly_summary_20260519.csv"
    may_path = A7D_DIR / "crypto_a7d_may_failure_attribution_20260519.csv"
    payment_summary.to_csv(payment_path, index=False)
    payment_hourly.to_csv(payment_hourly_path, index=False)
    may_symbol.to_csv(may_path, index=False)

    residual = residual_by_funding_version(index, matrices, core_specs, funding_specs)
    residual_path = A7D_DIR / "crypto_a7d_core4_residual_by_funding_version_20260519.csv"
    residual.to_csv(residual_path, index=False)

    f2_recent = metric(ladder, "F2_latest_known_observable", "recent_oos_2025H2_2026Apr", "annualized_mean")
    f4_recent = metric(ladder, "F4_future_next_funding_forbidden_8h", "recent_oos_2025H2_2026Apr", "annualized_mean")
    f5_recent = metric(ladder, "F5_time_shuffled_funding", "recent_oos_2025H2_2026Apr", "annualized_mean")
    f6_recent = metric(ladder, "F6_symbol_shuffled_funding", "recent_oos_2025H2_2026Apr", "annualized_mean")
    f7_recent = metric(ladder, "F7_wrong_lag_future_24h", "recent_oos_2025H2_2026Apr", "annualized_mean")
    f2_may = metric(ladder, "F2_latest_known_observable", "fresh_forward_2026May", "annualized_mean")
    net_current_recent = metric(payment_summary, "net_current_long_only", "recent_oos_2025H2_2026Apr", "annualized_mean", cost="")
    net_full_recent = metric(payment_summary, "net_full_signed", "recent_oos_2025H2_2026Apr", "annualized_mean", cost="")
    blockers = []
    warnings = []
    exact_rate = alignment_summary["exact_event_detection_rate"]
    observable_change_rate = alignment_summary["observable_change_event_detection_rate"]
    if alignment_summary["feature_before_execution_violations"] > 0 or alignment_summary["funding_before_feature_violations"] > 0:
        blockers.append("timestamp_alignment_violation")
    if observable_change_rate is None or observable_change_rate < 0.99:
        blockers.append("funding_event_detection_observable_change_misses_events")
    if exact_rate is not None and exact_rate < 0.95:
        warnings.append("exact_match_event_detection_misses_ms_offset_events")
    if net_current_recent is not None and net_full_recent is not None and abs(net_current_recent - net_full_recent) > 0.25:
        warnings.append("legacy_long_only_funding_model_materially_differs_from_full_signed_model")
    if f5_recent is not None and f2_recent is not None and f5_recent > max(0.0, 0.5 * f2_recent):
        blockers.append("time_shuffled_funding_too_strong")
    if f6_recent is not None and f2_recent is not None and f6_recent > max(0.0, 0.5 * f2_recent):
        blockers.append("symbol_shuffled_funding_too_strong")
    if f4_recent is not None and f2_recent is not None and f4_recent > 1.25 * f2_recent:
        warnings.append("future_forbidden_funding_variant_much_stronger_than_observable")
    if f7_recent is not None and f2_recent is not None and f7_recent > 1.25 * f2_recent:
        warnings.append("wrong_lag_future_24h_diagnostic_much_stronger_than_observable")
    if f2_may is not None and f2_may <= 0:
        warnings.append("observable_fundingcore_fresh_may_negative")

    decision = "PASS_A7D_FUNDING_SEMANTICS_FOR_RESEARCH" if not blockers else "HOLD_A7D_FUNDING_SEMANTICS_UNRESOLVED"
    manifest = {
        "generated_at": now,
        "decision": decision,
        "blockers": blockers,
        "warnings": warnings,
        "risk_variant": RISK_VARIANT,
        "cost_tier_primary": "stress_10bp",
        "purge_embargo_bars": PURGE_EMBARGO_BARS,
        "evaluator_funding_payment_model": "full_signed_long_pays_short_receives",
        "key_metrics": {
            "exact_event_detection_rate": exact_rate,
            "within_1h_event_detection_rate": alignment_summary["within_1h_event_detection_rate"],
            "observable_change_event_detection_rate": observable_change_rate,
            "f2_recent_annualized": f2_recent,
            "f4_future_recent_annualized": f4_recent,
            "f5_time_shuffle_recent_annualized": f5_recent,
            "f6_symbol_shuffle_recent_annualized": f6_recent,
            "f7_wrong_lag_future_24h_recent_annualized": f7_recent,
            "f2_fresh_may_annualized": f2_may,
            "net_current_long_only_recent_ann": net_current_recent,
            "net_full_signed_recent_ann": net_full_recent,
        },
        "outputs": {
            "field_contract": str(contract_path),
            "timestamp_alignment_samples": str(samples_path),
            "funding_event_detection_counts": str(event_counts_path),
            "funding_lag_ladder_metrics": str(ladder_path),
            "funding_payment_decomposition": str(payment_path),
            "funding_payment_hourly_summary": str(payment_hourly_path),
            "may_failure_attribution": str(may_path),
            "core4_residual_by_funding_version": str(residual_path),
        },
    }
    manifest_path = A7D_DIR / "crypto_a7d_manifest_20260519.json"
    write_json(manifest_path, manifest)

    report_path = REPORT_DIR / "CRYPTO_A7D_FUNDING_TIME_SEMANTICS_AUDIT_20260519.md"
    write_report(
        manifest=manifest,
        contract_path=contract_path,
        alignment_summary=alignment_summary,
        ladder=ladder,
        payment_summary=payment_summary,
        residual=residual,
        may_symbol=may_symbol,
        report_path=report_path,
    )

    decision_path = REPORT_DIR / "CRYPTO_A7D_DECISION_RECORD_20260519.md"
    decision_lines = [
        "# Crypto A7D Decision Record",
        "",
        f"- decision: `{decision}`",
        f"- generated_at: `{now}`",
        f"- blockers: `{blockers}`",
        f"- warnings: `{warnings}`",
        "",
        "## Conclusion",
        "",
        "A7D audits funding time semantics, event detection, payment sign handling, lag ladder behavior, and May 2026 failure attribution.",
        "",
        "Funding data semantics pass for further research when blockers are empty. This does not promote FundingCore or Core4 to alpha shadow proof.",
        "",
        "## Confirmed",
        "",
        "- `latest_known_funding_rate` is joined by backward asof from fundingTime.",
        "- `next_funding_rate` is not present in the current gold panel and remains forbidden.",
        "- A7D does not run new search or tune formulas.",
        "",
        "## Not Confirmed",
        "",
        "- alpha shadow proof",
        "- paper/live readiness",
        "- production execution",
        "- generator/reward maturity",
        "",
        "## Required Next Action",
        "",
        "With evaluator semantics repaired, continue with funding-regime/risk failure audit. Do not run generator bakeoff or shadow promotion while fresh May and drawdown risks remain unresolved.",
    ]
    decision_path.write_text("\n".join(decision_lines) + "\n", encoding="utf-8")

    print("A7D_REPORT=" + str(report_path))
    print("A7D_DECISION_RECORD=" + str(decision_path))
    print("A7D_CONTRACT=" + str(contract_path))
    print("A7D_MANIFEST=" + str(manifest_path))
    print("DECISION=" + decision)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
