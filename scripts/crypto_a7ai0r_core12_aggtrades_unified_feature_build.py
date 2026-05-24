from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(r"G:\AlphaFactory_CryptoData")
INPUT_PANEL = DATA_ROOT / "gold" / "features" / "binance_core12_all_features_metrics_market_structure_aggtrades_v1_20260524.parquet"
OUTPUT_PANEL = DATA_ROOT / "gold" / "features" / "binance_core12_aggtrades_unified_features_v1_20260524.parquet"
A7AI0_AUTH = ROOT / "runtime" / "a7ai0_core12_aggtrades_experiment_contract" / "a7ai0_authorization_matrix.json"

OUT_DIR = ROOT / "runtime" / "a7ai0r_core12_aggtrades_unified_feature_build"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7AI0R_CORE12_AGGTRADES_UNIFIED_FEATURE_BUILD_20260524.md"

CORE12 = [
    "ADAUSDT",
    "AVAXUSDT",
    "BCHUSDT",
    "BNBUSDT",
    "BTCUSDT",
    "DOGEUSDT",
    "ETHUSDT",
    "LINKUSDT",
    "LTCUSDT",
    "SOLUSDT",
    "SUIUSDT",
    "XRPUSDT",
]

BASE_COLUMNS = [
    "symbol",
    "timestamp",
    "ret_1",
    "ret_24",
    "funding_rate_bps",
    "open_interest_change_24h",
    "mark_index_basis_change_24h",
    "premium_index_change_24h",
    "top_long_short_position_ratio_zscore_168h",
]

RAW_AGG_COLUMNS = [
    "agg_features_available",
    "agg_trade_count",
    "agg_underlying_trade_count",
    "agg_quantity",
    "agg_notional",
    "agg_buy_notional",
    "agg_sell_notional",
    "agg_signed_aggressor_quantity",
    "agg_signed_aggressor_notional",
    "agg_high_price",
    "agg_low_price",
    "agg_price_std",
    "agg_max_trade_notional",
    "agg_open_price",
    "agg_close_price",
    "agg_vwap",
    "agg_buy_vwap",
    "agg_sell_vwap",
    "agg_avg_agg_trade_notional",
    "agg_avg_underlying_trade_notional",
    "agg_volume_imbalance",
    "agg_buy_sell_notional_ratio",
    "agg_price_range_bps",
    "agg_close_to_open_bps",
    "agg_large_trade_count_100k_plus",
    "agg_large_notional_100k_plus",
    "agg_large_trade_count_ratio_100k_plus",
    "agg_large_notional_ratio_100k_plus",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 100) -> str:
    if df.empty:
        return "`<empty>`"
    try:
        return df.head(max_rows).to_markdown(index=False)
    except Exception:
        return "```\n" + df.head(max_rows).to_string(index=False) + "\n```"


def safe_div(num: pd.Series, den: pd.Series) -> pd.Series:
    out = num.astype(float) / den.astype(float).replace(0, np.nan)
    return out.replace([np.inf, -np.inf], np.nan)


def rolling_sum(g: pd.core.groupby.generic.SeriesGroupBy, window: int) -> pd.Series:
    return g.rolling(window, min_periods=max(2, min(window, 4))).sum().reset_index(level=0, drop=True)


def rolling_max(g: pd.core.groupby.generic.SeriesGroupBy, window: int) -> pd.Series:
    return g.rolling(window, min_periods=max(2, min(window, 4))).max().reset_index(level=0, drop=True)


def rolling_mean(g: pd.core.groupby.generic.SeriesGroupBy, window: int) -> pd.Series:
    return g.rolling(window, min_periods=max(2, min(window, 8))).mean().reset_index(level=0, drop=True)


def rolling_std(g: pd.core.groupby.generic.SeriesGroupBy, window: int) -> pd.Series:
    return g.rolling(window, min_periods=max(2, min(window, 8))).std(ddof=0).reset_index(level=0, drop=True)


def row_zscore(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = df[["symbol", "timestamp"]].copy()
    for col in cols:
        values = df.pivot(index="timestamp", columns="symbol", values=col)
        mean = values.mean(axis=1)
        std = values.std(axis=1, ddof=0).replace(0, np.nan)
        z = values.sub(mean, axis=0).div(std, axis=0)
        long = z.stack().rename(f"{col}_cs_zscore").reset_index()
        out = out.merge(long, on=["timestamp", "symbol"], how="left")
    return out


def row_rank(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = df[["symbol", "timestamp"]].copy()
    for col in cols:
        values = df.pivot(index="timestamp", columns="symbol", values=col)
        rank = values.rank(axis=1, pct=True)
        long = rank.stack().rename(f"{col}_cs_rank").reset_index()
        out = out.merge(long, on=["timestamp", "symbol"], how="left")
    return out


def build_features(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = df[df["symbol"].isin(CORE12)].copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.sort_values(["symbol", "timestamp"]).reset_index(drop=True)
    for col in RAW_AGG_COLUMNS + BASE_COLUMNS:
        if col in df.columns and col not in {"symbol", "timestamp"}:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    g = df.groupby("symbol", observed=True)
    out = df[BASE_COLUMNS + RAW_AGG_COLUMNS].copy()

    out["agg_vwap_close_bps"] = (safe_div(df["agg_vwap"], df["agg_close_price"]) - 1.0) * 10000.0
    out["agg_buy_sell_vwap_spread_bps"] = (safe_div(df["agg_buy_vwap"], df["agg_sell_vwap"]) - 1.0) * 10000.0
    out["agg_avg_underlying_trades_per_agg"] = safe_div(df["agg_underlying_trade_count"], df["agg_trade_count"])
    out["agg_flow_imbalance_notional"] = safe_div(df["agg_signed_aggressor_notional"], df["agg_notional"]).clip(-1, 1)
    out["agg_buy_notional_share"] = safe_div(df["agg_buy_notional"], df["agg_notional"]).clip(0, 1)
    out["agg_sell_notional_share"] = safe_div(df["agg_sell_notional"], df["agg_notional"]).clip(0, 1)

    for window in [4, 24]:
        notional = rolling_sum(g["agg_notional"], window)
        signed = rolling_sum(g["agg_signed_aggressor_notional"], window)
        large = rolling_sum(g["agg_large_notional_100k_plus"], window)
        trades = rolling_sum(g["agg_trade_count"], window)
        out[f"agg_notional_sum_{window}h"] = notional
        out[f"agg_quantity_sum_{window}h"] = rolling_sum(g["agg_quantity"], window)
        out[f"agg_signed_notional_sum_{window}h"] = signed
        out[f"agg_flow_imbalance_notional_{window}h"] = safe_div(signed, notional).clip(-1, 1)
        out[f"agg_large_notional_sum_{window}h"] = large
        out[f"agg_large_notional_share_{window}h"] = safe_div(large, notional).clip(0, 1)
        out[f"agg_trade_count_sum_{window}h"] = trades
        out[f"agg_avg_trade_notional_{window}h"] = safe_div(notional, trades)
        out[f"agg_price_range_bps_max_{window}h"] = rolling_max(g["agg_price_range_bps"], window)
        out[f"agg_close_to_open_bps_sum_{window}h"] = rolling_sum(g["agg_close_to_open_bps"], window)

    mean_24 = rolling_mean(g["agg_signed_aggressor_notional"], 24)
    std_24 = rolling_std(g["agg_signed_aggressor_notional"], 24).replace(0, np.nan)
    out["agg_signed_flow_z_24h"] = (df["agg_signed_aggressor_notional"] - mean_24) / std_24
    median_24 = g["agg_notional"].rolling(24, min_periods=8).median().reset_index(level=0, drop=True)
    mad_24 = (df["agg_notional"] - median_24).abs().groupby(df["symbol"], observed=True).rolling(24, min_periods=8).median().reset_index(level=0, drop=True)
    out["agg_notional_shock_24h_mad"] = safe_div(df["agg_notional"] - median_24, mad_24.replace(0, np.nan))
    out["agg_notional_accel_4h_vs_24h"] = safe_div(out["agg_notional_sum_4h"], out["agg_notional_sum_24h"] / 6.0) - 1.0
    out["agg_flow_accel_4h_vs_24h"] = out["agg_flow_imbalance_notional_4h"] - out["agg_flow_imbalance_notional_24h"]

    by_time = out.groupby("timestamp", observed=True)
    out["agg_universe_notional"] = by_time["agg_notional"].transform("sum")
    out["agg_universe_signed_abs_notional"] = by_time["agg_signed_aggressor_notional"].transform(lambda s: s.abs().sum())
    out["agg_universe_large_notional"] = by_time["agg_large_notional_100k_plus"].transform("sum")
    out["agg_cross_symbol_notional_share"] = safe_div(out["agg_notional"], out["agg_universe_notional"]).clip(0, 1)
    out["agg_cross_symbol_signed_flow_share"] = safe_div(out["agg_signed_aggressor_notional"], out["agg_universe_signed_abs_notional"]).clip(-1, 1)
    out["agg_cross_symbol_large_notional_share"] = safe_div(out["agg_large_notional_100k_plus"], out["agg_universe_large_notional"]).clip(0, 1)

    piv = out.pivot(index="timestamp", columns="symbol", values="agg_flow_imbalance_notional_4h")
    for ref in ["BTCUSDT", "ETHUSDT"]:
        if ref in piv.columns:
            ref_series = piv[ref]
            aligned = out["timestamp"].map(ref_series)
            prefix = ref.lower()
            out[f"agg_{prefix}_flow_imbalance_4h"] = aligned
            out[f"agg_flow_minus_{prefix}_4h"] = out["agg_flow_imbalance_notional_4h"] - aligned

    cs_cols = [
        "agg_volume_imbalance",
        "agg_signed_flow_z_24h",
        "agg_large_notional_share_24h",
        "agg_notional_accel_4h_vs_24h",
        "agg_cross_symbol_notional_share",
    ]
    ranks = row_rank(out, cs_cols)
    zscores = row_zscore(out, cs_cols)
    out = out.merge(ranks.drop_duplicates(["symbol", "timestamp"]), on=["symbol", "timestamp"], how="left")
    out = out.merge(zscores.drop_duplicates(["symbol", "timestamp"]), on=["symbol", "timestamp"], how="left")

    for col in out.columns:
        if col not in {"symbol", "timestamp"}:
            out[col] = pd.to_numeric(out[col], errors="coerce").replace([np.inf, -np.inf], np.nan)

    catalog = []
    for col in out.columns:
        if col in {"symbol", "timestamp"}:
            source = "key"
        elif col in BASE_COLUMNS:
            source = "base_context"
        elif col in RAW_AGG_COLUMNS:
            source = "raw_aggtrades"
        elif "_cs_" in col:
            source = "cross_symbol_derived"
        elif any(tag in col for tag in ["_4h", "_24h", "z_24h", "shock_24h"]):
            source = "past_rolling_derived"
        else:
            source = "derived"
        catalog.append({"field_name": col, "source_class": source, "non_null_rate": float(out[col].notna().mean()) if col not in {"symbol", "timestamp"} else 1.0})
    return out, pd.DataFrame(catalog)


def quality(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    bounds = []
    bounded = {
        "agg_volume_imbalance": (-1, 1),
        "agg_flow_imbalance_notional": (-1, 1),
        "agg_flow_imbalance_notional_4h": (-1, 1),
        "agg_flow_imbalance_notional_24h": (-1, 1),
        "agg_buy_notional_share": (0, 1),
        "agg_sell_notional_share": (0, 1),
        "agg_large_notional_ratio_100k_plus": (0, 1),
        "agg_large_notional_share_4h": (0, 1),
        "agg_large_notional_share_24h": (0, 1),
        "agg_cross_symbol_notional_share": (0, 1),
        "agg_cross_symbol_signed_flow_share": (-1, 1),
        "agg_cross_symbol_large_notional_share": (0, 1),
    }
    for col in df.columns:
        if col in {"symbol", "timestamp"}:
            continue
        s = pd.to_numeric(df[col], errors="coerce")
        rows.append(
            {
                "field_name": col,
                "non_null_rate": float(s.notna().mean()),
                "nan_count": int(s.isna().sum()),
                "inf_count": int(np.isinf(s.to_numpy(dtype=float, na_value=np.nan)).sum()),
                "min": float(s.min()) if s.notna().any() and math.isfinite(float(s.min())) else None,
                "max": float(s.max()) if s.notna().any() and math.isfinite(float(s.max())) else None,
            }
        )
        if col in bounded:
            lo, hi = bounded[col]
            bounds.append({"field_name": col, "lower": lo, "upper": hi, "violation_count": int(((s < lo) | (s > hi)).sum())})
    return pd.DataFrame(rows), pd.DataFrame(bounds)


def split_coverage(df: pd.DataFrame) -> pd.DataFrame:
    splits = [
        ("train_2024", "2024-01-01", "2024-12-31 23:00"),
        ("validation_2025H1", "2025-01-01", "2025-06-30 23:00"),
        ("recent_2025H2_2026Apr", "2025-07-01", "2026-04-30 23:00"),
        ("may_2026_stress_caveated", "2026-05-01", "2026-05-20 23:00"),
    ]
    rows = []
    for name, start, end in splits:
        part = df[df["timestamp"].between(pd.Timestamp(start, tz="UTC"), pd.Timestamp(end, tz="UTC"), inclusive="both")]
        flag = pd.to_numeric(part["agg_features_available"], errors="coerce").fillna(0).gt(0)
        rows.append(
            {
                "split": name,
                "rows": int(len(part)),
                "symbols": int(part["symbol"].nunique()),
                "agg_available_rows": int(flag.sum()),
                "agg_available_symbols": int(part.loc[flag, "symbol"].nunique()),
                "agg_available_rate": float(flag.mean()) if len(part) else 0.0,
                "may_allowed_for_ranking": False if "may" in name else True,
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PANEL.parent.mkdir(parents=True, exist_ok=True)
    now = utc_now()
    auth_prev = json.loads(A7AI0_AUTH.read_text(encoding="utf-8"))
    if not auth_prev.get("authorizes_a7ai1_small_controlled_raw_agg_smoke"):
        raise RuntimeError("A7AI0 does not authorize unified feature build")

    schema = pq.read_schema(INPUT_PANEL)
    cols = [c for c in BASE_COLUMNS + RAW_AGG_COLUMNS if c in schema.names]
    df = pd.read_parquet(INPUT_PANEL, columns=sorted(set(cols)), engine="pyarrow")
    unified, catalog = build_features(df)
    unified.to_parquet(OUTPUT_PANEL, index=False, engine="pyarrow", compression="zstd")

    q, bounds = quality(unified)
    split = split_coverage(unified)
    blockers: list[str] = []
    warnings = [
        "May 2026 agg coverage remains core3 current-month caveated; not valid as full core12 May history",
        "This build creates experimental features from accepted raw agg fields; it is not alpha evidence",
    ]
    if int(unified.duplicated(["symbol", "timestamp"]).sum()) > 0:
        blockers.append("duplicate_symbol_timestamp")
    if int(bounds["violation_count"].sum()) > 0:
        blockers.append("bounded_feature_violation")
    if int(q["inf_count"].sum()) > 0:
        blockers.append("inf_values_present")
    non_may = split[~split["split"].str.contains("may")]
    if int(non_may["agg_available_symbols"].min()) < 12:
        blockers.append("non_may_core12_availability_incomplete")
    decision = "PASS_A7AI0R_CORE12_AGGTRADES_UNIFIED_FEATURES_READY" if not blockers else "HOLD_A7AI0R_CORE12_AGGTRADES_UNIFIED_FEATURES_BLOCKED"
    auth = {
        "decision": decision,
        "blockers": blockers,
        "warnings": warnings,
        "authorizes_a7ai1_small_controlled_unified_agg_smoke": decision.startswith("PASS_"),
        "authorizes_direct_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "may_policy": "May stress-only and core3-current-month caveated; do not rank/tune on May",
    }
    manifest = {
        "generated_at": now,
        "decision": decision,
        "input_panel": str(INPUT_PANEL),
        "output_panel": str(OUTPUT_PANEL),
        "rows": int(len(unified)),
        "columns": int(unified.shape[1]),
        "symbols": int(unified["symbol"].nunique()),
        "timestamp_min": str(unified["timestamp"].min()),
        "timestamp_max": str(unified["timestamp"].max()),
        "executes_replay": False,
        "executes_search": False,
        "report": str(REPORT_PATH),
        "output_dir": str(OUT_DIR),
    }

    catalog.to_csv(OUT_DIR / "a7ai0r_unified_feature_catalog.csv", index=False)
    q.to_csv(OUT_DIR / "a7ai0r_numeric_quality.csv", index=False)
    bounds.to_csv(OUT_DIR / "a7ai0r_bounded_feature_audit.csv", index=False)
    split.to_csv(OUT_DIR / "a7ai0r_split_coverage.csv", index=False)
    write_json(OUT_DIR / "a7ai0r_authorization_matrix.json", auth)
    write_json(OUT_DIR / "a7ai0r_manifest.json", manifest)

    report = f"""# CRYPTO A7AI-0R Core12 aggTrades Unified Feature Build

Generated: {now}

## Decision

```text
{decision}
```

This stage materializes a unified core12 aggTrades feature layer from the accepted raw enhanced agg fields. It does not run replay and does not run search.

## Summary

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Authorization

```json
{json.dumps(auth, indent=2, sort_keys=True)}
```

## Split Coverage

{md_table(split)}

## Feature Catalog Summary

{md_table(catalog.groupby("source_class", observed=True).size().reset_index(name="count"))}

## Bounded Feature Audit

{md_table(bounds)}

## Numeric Quality Worst Missing

{md_table(q.sort_values("non_null_rate").head(40))}

## Boundary

- Use this unified panel for A7AI-1 instead of recomputing rolling/cross-symbol agg fields inside the smoke runner.
- All rolling transforms are past/current-hour only and become available after the 1h bucket closes.
- May 2026 agg coverage is caveated and cannot enter ranking/tuning.
- No direct formula search, large search, alpha proof, shadow, paper, or live is authorized.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
