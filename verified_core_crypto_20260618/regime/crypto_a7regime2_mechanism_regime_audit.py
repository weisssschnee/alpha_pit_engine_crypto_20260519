from __future__ import annotations

import argparse
import json
import math
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow.parquet as pq


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.crypto_a7al2l_fast_derived_replay_preflight import SPLIT_ORDER, split_for_timestamps  # noqa: E402


DATA_ROOT = Path(os.environ.get("ALPHAFACTORY_CRYPTO_DATA_ROOT", r"G:\AlphaFactory_CryptoData"))
BASE_DIR = Path(os.environ.get("A7AL_BASE_PANEL_ROOT", str(DATA_ROOT / "gold" / "features" / "binance_universe498_replay_1h_v2_20260527")))
RUNTIME = REPO / "runtime" / "a7regime2_mechanism_regime_audit_20260612"
REPORT = REPO / "reports" / "CRYPTO_A7REGIME2_MECHANISM_REGIME_AUDIT_20260612.md"
DATE = "20260612"
STAGE = "A7REGIME-2"

NEEDED_COLUMNS = [
    "symbol",
    "timestamp",
    "trade_close",
    "trade_quote_volume",
    "funding_interval_hours",
    "funding_rate",
    "open_interest_value_last",
    "mark_index_basis_bps",
    "mark_trade_basis_bps",
    "premium_close_bps",
    "top_long_short_account_ratio_last",
    "top_long_short_position_ratio_last",
    "global_long_short_account_ratio_last",
    "taker_buy_sell_volume_ratio_last",
    "kline_taker_buy_quote_share",
]


def nan_p90(values: pd.Series) -> float:
    x = pd.to_numeric(values, errors="coerce")
    return float(np.nanpercentile(x, 90)) if x.notna().sum() else np.nan


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 40) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    try:
        return view.to_markdown(index=False)
    except Exception:
        return "```text\n" + view.to_string(index=False) + "\n```"


def episode_count(mask: np.ndarray) -> int:
    if len(mask) == 0:
        return 0
    x = mask.astype(bool)
    starts = x & np.r_[True, ~x[:-1]]
    return int(starts.sum())


def safe_z(series: pd.Series, train_mask: np.ndarray) -> pd.Series:
    base = pd.to_numeric(series.loc[train_mask], errors="coerce")
    mu = float(base.mean(skipna=True))
    sd = float(base.std(skipna=True))
    if not np.isfinite(sd) or sd <= 1e-12:
        return pd.Series(np.nan, index=series.index)
    return (pd.to_numeric(series, errors="coerce") - mu) / sd


def q(series: pd.Series, train_mask: np.ndarray, quantile: float) -> float:
    return float(pd.to_numeric(series.loc[train_mask], errors="coerce").quantile(quantile))


def session_bucket(ts: pd.Timestamp) -> str:
    hour = int(ts.hour)
    if 0 <= hour <= 7:
        return "asia_utc_00_07"
    if 8 <= hour <= 13:
        return "europe_utc_08_13"
    if 14 <= hour <= 21:
        return "us_utc_14_21"
    return "late_utc_22_23"


def load_hourly_market_state(symbol_cap: int = 0) -> tuple[pd.DataFrame, dict[str, Any]]:
    files = sorted(BASE_DIR.rglob("*.parquet"))
    if symbol_cap > 0:
        files = files[:symbol_cap]
    frames: list[pd.DataFrame] = []
    missing_cols: dict[str, int] = {}
    for idx, path in enumerate(files, start=1):
        try:
            schema_cols = pq.read_schema(path).names
            cols = [col for col in NEEDED_COLUMNS if col in schema_cols]
            for col in set(NEEDED_COLUMNS) - set(cols):
                missing_cols[col] = missing_cols.get(col, 0) + 1
            part = pd.read_parquet(path, columns=cols, engine="pyarrow")
        except Exception as exc:
            missing_cols[f"READ_ERROR:{path.name}:{exc!r}"] = missing_cols.get(f"READ_ERROR:{path.name}:{exc!r}", 0) + 1
            continue
        if part.empty or "timestamp" not in part.columns or "trade_close" not in part.columns:
            continue
        part["timestamp"] = pd.to_datetime(part["timestamp"], utc=True)
        part = part.sort_values("timestamp")
        close = pd.to_numeric(part["trade_close"], errors="coerce")
        part["log_close"] = np.log(close.where(close > 0))
        part["ret_1h"] = part["log_close"].diff()
        if "trade_quote_volume" in part.columns:
            part["log_quote_volume"] = np.log1p(pd.to_numeric(part["trade_quote_volume"], errors="coerce"))
        if "open_interest_value_last" in part.columns:
            oi = pd.to_numeric(part["open_interest_value_last"], errors="coerce")
            part["oi_value"] = oi.where(oi > 0)
        if "kline_taker_buy_quote_share" in part.columns:
            part["taker_share_abs_imbalance"] = (pd.to_numeric(part["kline_taker_buy_quote_share"], errors="coerce") - 0.5).abs()
        elif "taker_buy_sell_volume_ratio_last" in part.columns:
            ratio = pd.to_numeric(part["taker_buy_sell_volume_ratio_last"], errors="coerce")
            part["taker_share_abs_imbalance"] = np.log(ratio.where(ratio > 0)).abs()
        for col in ["mark_index_basis_bps", "mark_trade_basis_bps", "premium_close_bps"]:
            if col in part.columns:
                part[f"{col}_abs"] = pd.to_numeric(part[col], errors="coerce").abs()
        for col in [
            "top_long_short_account_ratio_last",
            "top_long_short_position_ratio_last",
            "global_long_short_account_ratio_last",
        ]:
            if col in part.columns:
                values = pd.to_numeric(part[col], errors="coerce")
                part[f"{col}_log_abs"] = np.log(values.where(values > 0)).abs()
        keep = [col for col in part.columns if col in {
            "timestamp",
            "symbol",
            "ret_1h",
            "log_quote_volume",
            "oi_value",
            "funding_rate",
            "funding_interval_hours",
            "mark_index_basis_bps",
            "mark_index_basis_bps_abs",
            "mark_trade_basis_bps_abs",
            "premium_close_bps_abs",
            "top_long_short_account_ratio_last_log_abs",
            "top_long_short_position_ratio_last_log_abs",
            "global_long_short_account_ratio_last_log_abs",
            "taker_share_abs_imbalance",
        }]
        frames.append(part[keep])

    if not frames:
        raise RuntimeError(f"no readable parquet files under {BASE_DIR}")
    df = pd.concat(frames, ignore_index=True)
    g = df.groupby("timestamp", sort=True)
    hourly = pd.DataFrame(
        {
            "active_symbols": g["symbol"].nunique(),
            "market_ret_1h": g["ret_1h"].median(),
            "neg_asset_share": g["ret_1h"].apply(lambda x: float(np.nanmean(pd.to_numeric(x, errors="coerce") < 0))),
            "cs_dispersion_1h": g["ret_1h"].apply(lambda x: float(np.nanpercentile(x, 90) - np.nanpercentile(x, 10)) if x.notna().sum() >= 20 else np.nan),
        }
    )
    optional_aggs = {
        "log_quote_volume": ["median", "mean"],
        "oi_value": ["sum", "median"],
        "funding_rate": ["median", nan_p90],
        "funding_interval_hours": ["median"],
        "mark_index_basis_bps": ["median"],
        "mark_index_basis_bps_abs": ["median", nan_p90],
        "mark_trade_basis_bps_abs": ["median"],
        "premium_close_bps_abs": ["median"],
        "top_long_short_account_ratio_last_log_abs": ["median"],
        "top_long_short_position_ratio_last_log_abs": ["median"],
        "global_long_short_account_ratio_last_log_abs": ["median"],
        "taker_share_abs_imbalance": ["median"],
    }
    for col, funcs in optional_aggs.items():
        if col not in df.columns:
            continue
        agg = g[col].agg(funcs)
        if isinstance(agg, pd.Series):
            hourly[col] = agg
        else:
            for sub_col in agg.columns:
                suffix = str(sub_col)
                if suffix in {"nan_p90", "<lambda_0>", "<lambda>"}:
                    suffix = "p90"
                name = f"{col}_{suffix}"
                hourly[name] = agg[sub_col]
    hourly = hourly.sort_index()
    hourly.index = pd.DatetimeIndex(hourly.index)
    hourly["split"] = split_for_timestamps(hourly.index)
    hourly["market_ret_24h"] = hourly["market_ret_1h"].rolling(24, min_periods=8).sum()
    hourly["market_ret_168h"] = hourly["market_ret_1h"].rolling(168, min_periods=42).sum()
    hourly["vol_24h"] = hourly["market_ret_1h"].rolling(24, min_periods=8).std()
    hourly["vol_168h"] = hourly["market_ret_1h"].rolling(168, min_periods=42).std()
    market_index = hourly["market_ret_1h"].fillna(0).cumsum()
    peak = market_index.rolling(24 * 30, min_periods=24).max()
    hourly["drawdown_30d_log"] = market_index - peak
    if "log_quote_volume_median" in hourly.columns:
        vol_mu = hourly["log_quote_volume_median"].rolling(168, min_periods=48).mean()
        vol_sd = hourly["log_quote_volume_median"].rolling(168, min_periods=48).std()
        hourly["volume_z_168h"] = (hourly["log_quote_volume_median"] - vol_mu) / (vol_sd + 1e-12)
    if "oi_value_sum" in hourly.columns:
        oi_log = np.log(hourly["oi_value_sum"].where(hourly["oi_value_sum"] > 0))
        hourly["oi_value_log_delta_24h"] = oi_log - oi_log.shift(24)
        hourly["oi_value_log_delta_168h"] = oi_log - oi_log.shift(168)
    meta = {
        "base_dir": str(BASE_DIR),
        "files_read": len(frames),
        "row_count": int(df.shape[0]),
        "min_timestamp": str(hourly.index.min()),
        "max_timestamp": str(hourly.index.max()),
        "missing_columns_file_counts": missing_cols,
    }
    return hourly, meta


def build_states(hourly: pd.DataFrame) -> pd.DataFrame:
    out = hourly.copy()
    train = out["split"].eq("train_2024").to_numpy()
    out["session"] = [session_bucket(ts) for ts in out.index]
    out["is_weekend"] = out.index.weekday >= 5
    out["funding_boundary_8h_proxy"] = out.index.hour.isin([0, 8, 16])
    out["pre_funding_1h_proxy"] = out.index.hour.isin([23, 7, 15])
    out["post_funding_1h_proxy"] = out.index.hour.isin([1, 9, 17])
    out["us_equity_open_proxy"] = out.index.hour.isin([13, 14, 15])
    out["us_equity_close_proxy"] = out.index.hour.isin([20, 21])
    out["weekly_boundary_utc"] = (out.index.weekday == 0) & (out.index.hour <= 2)
    out["monthly_boundary_utc"] = (out.index.day <= 2) & (out.index.hour <= 2)

    out["market_crash_like"] = (
        (out["market_ret_24h"] <= q(out["market_ret_24h"], train, 0.05))
        & (out["neg_asset_share"] >= q(out["neg_asset_share"], train, 0.80))
    )
    out["extreme_vol_168h_p95"] = out["vol_168h"] >= q(out["vol_168h"], train, 0.95)
    out["extreme_drawdown_30d_p05"] = out["drawdown_30d_log"] <= q(out["drawdown_30d_log"], train, 0.05)
    if "volume_z_168h" in out.columns:
        out["liquidity_shock_low_volume"] = out["volume_z_168h"] <= q(out["volume_z_168h"], train, 0.10)
        out["volume_burst"] = out["volume_z_168h"] >= q(out["volume_z_168h"], train, 0.90)
    if "funding_rate_p90" in out.columns:
        out["funding_abs_extreme_p90"] = out["funding_rate_p90"] >= q(out["funding_rate_p90"], train, 0.90)
    if "funding_rate_median" in out.columns:
        out["funding_positive_extreme"] = out["funding_rate_median"] >= q(out["funding_rate_median"], train, 0.90)
        out["funding_negative_extreme"] = out["funding_rate_median"] <= q(out["funding_rate_median"], train, 0.10)
    basis_cols = [c for c in ["mark_index_basis_bps_abs_p90", "mark_index_basis_bps_abs_median", "premium_close_bps_abs_median"] if c in out.columns]
    if basis_cols:
        basis_proxy = out[basis_cols].mean(axis=1, skipna=True)
        out["basis_dislocation_p90"] = basis_proxy >= q(basis_proxy, train, 0.90)
        out["basis_dislocation_p95"] = basis_proxy >= q(basis_proxy, train, 0.95)
    if "oi_value_log_delta_24h" in out.columns:
        out["oi_expansion_24h_p90"] = out["oi_value_log_delta_24h"] >= q(out["oi_value_log_delta_24h"], train, 0.90)
        out["oi_contraction_24h_p10"] = out["oi_value_log_delta_24h"] <= q(out["oi_value_log_delta_24h"], train, 0.10)
    pos_cols = [c for c in [
        "top_long_short_account_ratio_last_log_abs_median",
        "top_long_short_position_ratio_last_log_abs_median",
        "global_long_short_account_ratio_last_log_abs_median",
    ] if c in out.columns]
    if pos_cols:
        pos_proxy = out[pos_cols].mean(axis=1, skipna=True)
        out["positioning_crowding_p90"] = pos_proxy >= q(pos_proxy, train, 0.90)
    if "taker_share_abs_imbalance_median" in out.columns:
        out["taker_flow_imbalance_p90"] = out["taker_share_abs_imbalance_median"] >= q(out["taker_share_abs_imbalance_median"], train, 0.90)

    if {"market_crash_like", "oi_expansion_24h_p90", "funding_positive_extreme"}.issubset(out.columns):
        out["crowded_long_unwind_proxy"] = out["market_crash_like"] & out["oi_expansion_24h_p90"] & out["funding_positive_extreme"]
    if {"market_crash_like", "oi_contraction_24h_p10"}.issubset(out.columns):
        out["forced_deleveraging_proxy"] = out["market_crash_like"] & out["oi_contraction_24h_p10"]
    if {"basis_dislocation_p90", "funding_abs_extreme_p90"}.issubset(out.columns):
        out["derivative_dislocation_proxy"] = out["basis_dislocation_p90"] & out["funding_abs_extreme_p90"]
    if {"basis_dislocation_p90", "taker_flow_imbalance_p90"}.issubset(out.columns):
        out["perp_pressure_proxy"] = out["basis_dislocation_p90"] & out["taker_flow_imbalance_p90"]
    return out


def summarize_states(states: pd.DataFrame) -> pd.DataFrame:
    state_cols = [
        col for col in states.columns
        if states[col].dtype == bool or col in ["session"]
    ]
    rows: list[dict[str, Any]] = []
    for col in state_cols:
        if col == "session":
            values = sorted(states[col].dropna().unique().tolist())
            for value in values:
                mask = states[col].eq(value).to_numpy()
                rows.extend(summarize_mask(states, f"session={value}", mask))
        else:
            rows.extend(summarize_mask(states, col, states[col].fillna(False).to_numpy(dtype=bool)))
    return pd.DataFrame(rows)


def summarize_mask(states: pd.DataFrame, name: str, mask: np.ndarray) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    total_hours = int(mask.sum())
    total_episodes = episode_count(mask)
    may_mask = states["split"].eq("known_may2026_stress").to_numpy()
    train_mask = states["split"].eq("train_2024").to_numpy()
    train_rate = float(mask[train_mask].mean()) if train_mask.any() else np.nan
    may_rate = float(mask[may_mask].mean()) if may_mask.any() else np.nan
    enrichment = may_rate / train_rate if np.isfinite(train_rate) and train_rate > 0 else np.nan
    row_base = {
        "state": name,
        "total_hours": total_hours,
        "total_episodes": total_episodes,
        "train_rate": train_rate,
        "may_rate": may_rate,
        "may_vs_train_enrichment": enrichment,
        "future_label_next_24h_market_ret_when_on": float(states["market_ret_24h"].shift(-24).loc[mask].mean()) if mask.any() else np.nan,
        "decision": "candidate_mechanism_regime" if total_hours >= 240 and total_episodes >= 3 else "thin_attribution_only",
    }
    for split_name in SPLIT_ORDER:
        split_mask = states["split"].eq(split_name).to_numpy()
        row_base[f"{split_name}_hours"] = int((mask & split_mask).sum())
        row_base[f"{split_name}_episodes"] = episode_count(mask & split_mask)
    rows.append(row_base)
    return rows


def mechanism_overlap(states: pd.DataFrame, state_summary: pd.DataFrame) -> pd.DataFrame:
    names = state_summary["state"].tolist()
    bools: dict[str, np.ndarray] = {}
    for name in names:
        if name.startswith("session="):
            bools[name] = states["session"].eq(name.split("=", 1)[1]).to_numpy()
        elif name in states.columns:
            bools[name] = states[name].fillna(False).to_numpy(dtype=bool)
    rows = []
    selected = [
        name for name in names
        if any(token in name for token in ["funding", "basis", "oi_", "crowded", "forced", "derivative", "perp", "crash", "vol", "drawdown", "session="])
    ][:40]
    for left in selected:
        a = bools.get(left)
        if a is None or a.sum() == 0:
            continue
        for right in selected:
            if left >= right:
                continue
            b = bools.get(right)
            if b is None or b.sum() == 0:
                continue
            inter = int((a & b).sum())
            union = int((a | b).sum())
            if inter == 0:
                continue
            rows.append(
                {
                    "left": left,
                    "right": right,
                    "intersection_hours": inter,
                    "jaccard": inter / union if union else np.nan,
                    "left_covered_by_right": inter / int(a.sum()),
                    "right_covered_by_left": inter / int(b.sum()),
                }
            )
    return pd.DataFrame(rows).sort_values("jaccard", ascending=False) if rows else pd.DataFrame()


def priority_recommendations(summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in summary.iterrows():
        state = str(row["state"])
        enrich = float(row.get("may_vs_train_enrichment", np.nan))
        train_hours = int(row.get("train_2024_hours", 0))
        oos_episodes = sum(int(row.get(f"{s}_episodes", 0)) for s in SPLIT_ORDER if s != "train_2024")
        if any(token in state for token in ["funding", "basis", "oi_", "crowded", "forced", "derivative", "perp"]):
            family = "crypto_derivatives_mechanism"
        elif any(token in state for token in ["taker", "flow"]):
            family = "crypto_microstructure_proxy"
        elif any(token in state for token in ["session", "funding_boundary", "us_equity", "weekly", "monthly"]):
            family = "event_boundary"
        elif any(token in state for token in ["vol", "drawdown", "crash", "liquidity", "volume"]):
            family = "surface_stress"
        else:
            family = "general"
        if train_hours < 240:
            action = "high_interest_but_train_thin_attribution_first" if np.isfinite(enrich) and enrich >= 2.0 else "attribution_only_until_more_events"
        elif row["decision"] == "thin_attribution_only":
            action = "attribution_only_until_more_events"
        elif family == "event_boundary":
            action = "use_for_attribution_and_split_checks_not_alpha_signal"
        elif np.isfinite(enrich) and enrich >= 2.0:
            action = "promote_to_mechanism_regime_candidate"
        elif train_hours >= 500 and oos_episodes >= 3:
            action = "use_as_selector_regime_diversity_feature"
        else:
            action = "hold_for_more_data_or_lower_priority"
        rows.append(
            {
                "state": state,
                "family": family,
                "train_hours": train_hours,
                "oos_episodes": oos_episodes,
                "may_vs_train_enrichment": enrich,
                "recommended_action": action,
            }
        )
    return pd.DataFrame(rows).sort_values(["recommended_action", "may_vs_train_enrichment"], ascending=[True, False])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", default=str(RUNTIME))
    parser.add_argument("--report", default=str(REPORT))
    parser.add_argument("--symbol-cap", type=int, default=int(os.environ.get("A7REGIME2_SYMBOL_CAP", "0")))
    args = parser.parse_args()

    runtime = Path(args.runtime)
    report = Path(args.report)
    runtime.mkdir(parents=True, exist_ok=True)
    report.parent.mkdir(parents=True, exist_ok=True)

    hourly, meta = load_hourly_market_state(args.symbol_cap)
    states = build_states(hourly)
    summary = summarize_states(states)
    overlap = mechanism_overlap(states, summary)
    priority = priority_recommendations(summary)

    states.reset_index(names="timestamp").to_csv(runtime / "a7regime2_hourly_mechanism_state_panel.csv", index=False)
    summary.to_csv(runtime / "a7regime2_state_sufficiency_and_enrichment.csv", index=False)
    overlap.to_csv(runtime / "a7regime2_state_overlap_matrix.csv", index=False)
    priority.to_csv(runtime / "a7regime2_regime_priority_recommendations.csv", index=False)

    promote_count = int(priority["recommended_action"].eq("promote_to_mechanism_regime_candidate").sum()) if not priority.empty else 0
    usable_count = int(priority["recommended_action"].isin(["promote_to_mechanism_regime_candidate", "use_as_selector_regime_diversity_feature", "use_for_attribution_and_split_checks_not_alpha_signal"]).sum()) if not priority.empty else 0
    decision = "PASS_A7REGIME2_MECHANISM_REGIME_CANDIDATES_FOUND" if promote_count else "HOLD_A7REGIME2_NO_PROMOTABLE_MECHANISM_REGIME"
    manifest = {
        "stage": STAGE,
        "generated_at": now_utc(),
        "decision": decision,
        "base_dir": str(BASE_DIR),
        "symbol_cap": int(args.symbol_cap),
        "hour_count": int(states.shape[0]),
        "min_timestamp": str(states.index.min()),
        "max_timestamp": str(states.index.max()),
        "state_rows": int(summary.shape[0]),
        "promote_to_mechanism_regime_candidate": promote_count,
        "usable_or_attribution_state_count": usable_count,
        "load_meta": meta,
        "outputs": {
            "hourly_state_panel": str((runtime / "a7regime2_hourly_mechanism_state_panel.csv").relative_to(REPO)),
            "state_sufficiency_and_enrichment": str((runtime / "a7regime2_state_sufficiency_and_enrichment.csv").relative_to(REPO)),
            "state_overlap_matrix": str((runtime / "a7regime2_state_overlap_matrix.csv").relative_to(REPO)),
            "regime_priority_recommendations": str((runtime / "a7regime2_regime_priority_recommendations.csv").relative_to(REPO)),
            "report": str(report.relative_to(REPO)),
        },
    }
    write_json(runtime / "a7regime2_manifest.json", manifest)

    top_priority = priority.head(30)
    top_enriched = summary.sort_values("may_vs_train_enrichment", ascending=False).head(25)
    report.write_text(
        "\n".join(
            [
                "# CRYPTO A7REGIME2 Mechanism Regime Audit 20260612",
                "",
                "## Decision",
                "",
                f"`{decision}`",
                "",
                "This audit optimizes the regime research layer only. It does not authorize alpha proof, shadow, paper, live execution, or direct formula search.",
                "",
                "## What Was Tested",
                "",
                "The audit converts the current 1h top498 gold panel into a crypto-specific mechanism state panel. It adds funding-window proxies, UTC session boundaries, US session proxies, weekend/weekly/monthly boundaries, funding extremes, basis dislocation, OI expansion/contraction, positioning crowding, taker-flow imbalance, and composite derivative-stress proxies.",
                "",
                "## Scope",
                "",
                f"- base_dir: `{BASE_DIR}`",
                f"- rows_read: `{meta['row_count']}`",
                f"- hourly_state_rows: `{states.shape[0]}`",
                f"- min_timestamp: `{states.index.min()}`",
                f"- max_timestamp: `{states.index.max()}`",
                f"- files_read: `{meta['files_read']}`",
                "",
                "## Top Enriched States Versus Train",
                "",
                md_table(top_enriched, 25),
                "",
                "## Priority Recommendations",
                "",
                md_table(top_priority, 30),
                "",
                "## Interpretation",
                "",
                "The useful optimization is not to replace existing vol/liquidity regimes. It is to add a mechanism layer that distinguishes derivative dislocation, funding crowding, OI expansion/contraction, session boundaries, and event-window concentration. These states should first enter attribution, leave-one-event-out checks, and selector diversity controls. Only states with enough train/OOS events should become regime gates.",
                "",
                "## Risks",
                "",
                "- Funding-window proxies are based on UTC 8h conventions and must be upgraded to symbol-level actual funding intervals before hard gating.",
                "- There is no true liquidation feed in this panel; forced liquidation is only proxied through market crash + OI contraction.",
                "- Event boundaries can become calendar overfit if used as alpha signals. They should start as attribution/split controls.",
                "- The current audit uses 1h features. 1m data should be converted into 1h microstructure regime features before being added here.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(decision)
    print(report)


if __name__ == "__main__":
    main()
