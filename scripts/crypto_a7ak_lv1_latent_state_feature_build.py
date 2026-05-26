from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(r"G:\AlphaFactory_CryptoData")

PANEL_ROOT = DATA_ROOT / "gold" / "features" / "binance_universe498_replay_1h_v1_20260525"
SYMBOL_CLASSIFICATION = DATA_ROOT / "gold" / "metadata" / "binance_universe498_replay_1h_v1_symbol_classification_20260526.csv"
A7AK_LV0_AUTH = ROOT / "runtime" / "a7ak_lv0_listing_age_latent_variable_contract" / "a7ak_lv0_authorization_matrix.json"

OUTPUT_PANEL = DATA_ROOT / "gold" / "features" / "binance_universe498_latent_state_features_v1_20260527.parquet"
DATA_METADATA_DIR = DATA_ROOT / "gold" / "metadata"

OUT_DIR = ROOT / "runtime" / "a7ak_lv1_latent_state_feature_build"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7AK_LV1_LATENT_STATE_FEATURE_BUILD_20260527.md"


SPLITS = [
    ("train_2024", pd.Timestamp("2024-01-01 00:00:00+00:00"), pd.Timestamp("2024-12-31 23:00:00+00:00"), True),
    ("validation_2025H1", pd.Timestamp("2025-01-01 00:00:00+00:00"), pd.Timestamp("2025-06-30 23:00:00+00:00"), True),
    ("recent_2025H2_2026Apr", pd.Timestamp("2025-07-01 00:00:00+00:00"), pd.Timestamp("2026-04-30 23:00:00+00:00"), True),
    ("may_2026_unavailable", pd.Timestamp("2026-05-01 00:00:00+00:00"), pd.Timestamp("2026-05-31 23:00:00+00:00"), False),
]

INPUT_COLUMNS = [
    "symbol",
    "timestamp",
    "trade_close",
    "trade_quote_volume",
    "trade_count",
    "trade_return_1h",
    "funding_rate",
    "mark_index_basis_bps",
    "premium_close_bps",
    "open_interest_last",
    "source_trade_klines",
    "source_metrics",
    "source_market_funding",
    "feature_available_time",
    "execution_time",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    try:
        return df.head(max_rows).to_markdown(index=False)
    except Exception:
        return "```\n" + df.head(max_rows).to_string(index=False) + "\n```"


def symbol_path(symbol: str) -> Path:
    return PANEL_ROOT / f"symbol={symbol}" / "part.parquet"


def split_name(timestamp: pd.Series) -> pd.Series:
    out = pd.Series("outside_contract", index=timestamp.index, dtype="object")
    for name, start, end, _allowed in SPLITS:
        out[(timestamp >= start) & (timestamp <= end)] = name
    return out


def stable_state_id(label: str) -> str:
    digest = hashlib.sha1(label.encode("utf-8")).hexdigest()[:10]
    return f"lv_{digest}"


def safe_log_diff(series: pd.Series, periods: int) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce")
    return np.log(s.where(s > 0)).diff(periods)


def build_symbol_features(symbol: str, static_row: pd.Series) -> pd.DataFrame:
    df = pd.read_parquet(symbol_path(symbol), columns=INPUT_COLUMNS, engine="pyarrow")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["feature_available_time"] = pd.to_datetime(df["feature_available_time"], utc=True)
    df["execution_time"] = pd.to_datetime(df["execution_time"], utc=True)
    df = df.sort_values("timestamp").reset_index(drop=True)

    first_ts = df["timestamp"].min()
    age_hours = (df["timestamp"] - first_ts).dt.total_seconds() / 3600.0
    df["listing_age_hours"] = age_hours
    df["listing_age_days"] = age_hours / 24.0
    df["log1p_listing_age_days"] = np.log1p(df["listing_age_days"])
    df["sqrt_listing_age_days"] = np.sqrt(df["listing_age_days"].clip(lower=0))

    dt_hours = df["timestamp"].diff().dt.total_seconds().div(3600.0).fillna(1.0)
    df["gap_hours_at_row"] = (dt_hours - 1.0).clip(lower=0)
    source_complete = (
        df["source_trade_klines"].fillna(False).astype(bool)
        & df["source_metrics"].fillna(False).astype(bool)
        & df["source_market_funding"].fillna(False).astype(bool)
    ).astype(float)
    df["rolling_coverage_168h"] = source_complete.rolling(168, min_periods=24).mean()
    df["gap_hours_recent_168h"] = df["gap_hours_at_row"].rolling(168, min_periods=24).sum()
    df["history_length_hours"] = np.arange(len(df), dtype=float) + 1.0

    df["median_quote_volume_168h"] = df["trade_quote_volume"].rolling(168, min_periods=24).median()
    df["log_quote_volume_168h"] = np.log1p(df["median_quote_volume_168h"].clip(lower=0))
    df["trade_count_168h"] = df["trade_count"].rolling(168, min_periods=24).mean()
    df["realized_vol_24h"] = df["trade_return_1h"].rolling(24, min_periods=12).std(ddof=0)
    df["realized_vol_72h"] = df["trade_return_1h"].rolling(72, min_periods=24).std(ddof=0)
    df["realized_vol_168h"] = df["trade_return_1h"].rolling(168, min_periods=48).std(ddof=0)
    df["volume_volatility_ratio_168h"] = df["log_quote_volume_168h"] / df["realized_vol_168h"].replace(0, np.nan)
    df["funding_rate_abs_168h"] = df["funding_rate"].abs().rolling(168, min_periods=24).mean()
    df["funding_rate_mean_168h"] = df["funding_rate"].rolling(168, min_periods=24).mean()
    df["basis_abs_168h"] = df["mark_index_basis_bps"].abs().rolling(168, min_periods=24).mean()
    df["premium_abs_168h"] = df["premium_close_bps"].abs().rolling(168, min_periods=24).mean()
    df["open_interest_change_24h"] = safe_log_diff(df["open_interest_last"], 24)
    df["trade_return_24h"] = safe_log_diff(df["trade_close"], 24)
    df["oi_x_price_move_24h"] = df["open_interest_change_24h"] * df["trade_return_24h"]

    df["split"] = split_name(df["timestamp"])
    df["first_observed_timestamp"] = first_ts
    df["search_eligibility"] = static_row["search_eligibility"]
    df["liquidity_tier_static"] = static_row["liquidity_tier"]
    df["history_tier_static"] = static_row["history_tier"]
    df["contract_format"] = static_row["contract_format"]
    df["is_core12"] = bool(static_row["is_core12"])
    df["is_major"] = bool(static_row["is_major"])
    return df


def active_cross_section_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["age_percentile_active_universe"] = df.groupby("timestamp")["listing_age_days"].rank(pct=True)
    df["liquidity_rank_active_universe"] = df.groupby("timestamp")["median_quote_volume_168h"].rank(pct=True)
    return df


def train_thresholds(df: pd.DataFrame) -> pd.DataFrame:
    train = df[df["split"] == "train_2024"]
    fields = [
        ("log_quote_volume_168h", [0.33, 0.66]),
        ("realized_vol_168h", [0.33, 0.66]),
        ("funding_rate_abs_168h", [0.50, 0.80]),
        ("basis_abs_168h", [0.50, 0.80]),
        ("rolling_coverage_168h", [0.90, 0.99]),
    ]
    rows = []
    for field, qs in fields:
        values = pd.to_numeric(train[field], errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
        for q in qs:
            rows.append(
                {
                    "field_name": field,
                    "quantile": q,
                    "threshold": float(values.quantile(q)) if len(values) else np.nan,
                    "fit_split": "train_2024",
                    "fit_rows": int(len(values)),
                }
            )
    return pd.DataFrame(rows)


def get_threshold(thresholds: pd.DataFrame, field: str, q: float) -> float:
    row = thresholds[(thresholds["field_name"] == field) & (thresholds["quantile"] == q)]
    if row.empty:
        return np.nan
    return float(row["threshold"].iloc[0])


def bucketize(df: pd.DataFrame, thresholds: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["age_bucket_dynamic"] = pd.cut(
        out["listing_age_days"],
        bins=[-np.inf, 30, 90, 180, 365, np.inf],
        labels=["age_lt30d", "age_30_90d", "age_90_180d", "age_180_365d", "age_ge365d"],
    ).astype("object")

    def tri_bucket(series: pd.Series, field: str, labels: tuple[str, str, str]) -> pd.Series:
        lo = get_threshold(thresholds, field, 0.33)
        hi = get_threshold(thresholds, field, 0.66)
        return pd.cut(series, bins=[-np.inf, lo, hi, np.inf], labels=list(labels)).astype("object")

    def med_hi_bucket(series: pd.Series, field: str, labels: tuple[str, str, str]) -> pd.Series:
        med = get_threshold(thresholds, field, 0.50)
        hi = get_threshold(thresholds, field, 0.80)
        return pd.cut(series, bins=[-np.inf, med, hi, np.inf], labels=list(labels)).astype("object")

    out["liquidity_state"] = tri_bucket(out["log_quote_volume_168h"], "log_quote_volume_168h", ("liq_low", "liq_mid", "liq_high"))
    out["volatility_state"] = tri_bucket(out["realized_vol_168h"], "realized_vol_168h", ("vol_low", "vol_mid", "vol_high"))
    out["funding_abs_state"] = med_hi_bucket(out["funding_rate_abs_168h"], "funding_rate_abs_168h", ("fund_low", "fund_mid", "fund_high"))
    out["basis_abs_state"] = med_hi_bucket(out["basis_abs_168h"], "basis_abs_168h", ("basis_low", "basis_mid", "basis_high"))
    cov90 = get_threshold(thresholds, "rolling_coverage_168h", 0.90)
    cov99 = get_threshold(thresholds, "rolling_coverage_168h", 0.99)
    if not np.isfinite(cov90) or not np.isfinite(cov99) or cov90 >= cov99:
        out["coverage_state"] = np.select(
            [out["rolling_coverage_168h"] >= 0.999, out["rolling_coverage_168h"] >= 0.95],
            ["cov_high", "cov_mid"],
            default="cov_low",
        )
    else:
        out["coverage_state"] = pd.cut(out["rolling_coverage_168h"], bins=[-np.inf, cov90, cov99, np.inf], labels=["cov_low", "cov_mid", "cov_high"]).astype("object")
    out["major_state"] = np.where(out["is_major"], "major", "nonmajor")

    for col in ["age_bucket_dynamic", "liquidity_state", "volatility_state", "funding_abs_state", "basis_abs_state", "coverage_state"]:
        out[col] = out[col].fillna(f"{col}_missing")

    out["raw_latent_state_label"] = (
        out["age_bucket_dynamic"].astype(str)
        + "|"
        + out["liquidity_state"].astype(str)
        + "|"
        + out["volatility_state"].astype(str)
        + "|"
        + out["funding_abs_state"].astype(str)
        + "|"
        + out["basis_abs_state"].astype(str)
        + "|"
        + out["coverage_state"].astype(str)
        + "|"
        + out["major_state"].astype(str)
    )
    state_ids = {label: stable_state_id(label) for label in sorted(out["raw_latent_state_label"].dropna().unique())}
    out["raw_latent_state_id"] = out["raw_latent_state_label"].map(state_ids)
    train_seen = set(out.loc[out["split"] == "train_2024", "raw_latent_state_id"].dropna().unique())
    out["state_seen_in_train"] = out["raw_latent_state_id"].isin(train_seen)

    out["age_x_liquidity"] = out["log1p_listing_age_days"] * out["liquidity_rank_active_universe"]
    out["age_x_volatility"] = out["log1p_listing_age_days"] * out["realized_vol_168h"]
    out["age_x_funding_abs"] = out["log1p_listing_age_days"] * out["funding_rate_abs_168h"]
    return out


def state_registry(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (state_id, label), g in df.groupby(["raw_latent_state_id", "raw_latent_state_label"], dropna=False):
        row: dict[str, Any] = {
            "raw_latent_state_id": state_id,
            "raw_latent_state_label": label,
            "rows": int(len(g)),
            "symbols": int(g["symbol"].nunique()),
            "state_seen_in_train": bool(g["state_seen_in_train"].any()),
        }
        for split, _start, _end, _allowed in SPLITS:
            p = g[g["split"] == split]
            row[f"rows_{split}"] = int(len(p))
            row[f"symbols_{split}"] = int(p["symbol"].nunique())
        rows.append(row)
    return pd.DataFrame(rows).sort_values(["rows_train_2024", "rows"], ascending=[False, False])


def symbol_state_coverage(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for symbol, g in df.groupby("symbol", sort=True):
        state_counts = g["raw_latent_state_id"].value_counts(dropna=False)
        rows.append(
            {
                "symbol": symbol,
                "rows": int(len(g)),
                "search_eligibility": g["search_eligibility"].iloc[0],
                "history_tier": g["history_tier_static"].iloc[0],
                "liquidity_tier": g["liquidity_tier_static"].iloc[0],
                "states": int(state_counts.size),
                "dominant_state_id": str(state_counts.index[0]) if len(state_counts) else "",
                "dominant_state_share": float(state_counts.iloc[0] / len(g)) if len(g) else np.nan,
                "age_lt30_rows": int((g["age_bucket_dynamic"] == "age_lt30d").sum()),
                "age_lt30_share": float((g["age_bucket_dynamic"] == "age_lt30d").mean()) if len(g) else np.nan,
                "unseen_state_rows": int((~g["state_seen_in_train"]).sum()),
                "unseen_state_share": float((~g["state_seen_in_train"]).mean()) if len(g) else np.nan,
            }
        )
    return pd.DataFrame(rows)


def age_quota_audit(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    bucket_order = ["age_lt30d", "age_30_90d", "age_90_180d", "age_180_365d", "age_ge365d"]
    for split, _start, _end, allowed in SPLITS:
        part = df[df["split"] == split]
        total = len(part)
        for bucket in bucket_order:
            p = part[part["age_bucket_dynamic"] == bucket]
            rows.append(
                {
                    "split": split,
                    "age_bucket": bucket,
                    "rows": int(len(p)),
                    "symbols": int(p["symbol"].nunique()),
                    "row_share": float(len(p) / total) if total else 0.0,
                    "may_allowed_for_ranking": allowed,
                    "fixed_quota_minimum": 0.10 if bucket == "age_lt30d" else np.nan,
                    "quota_available": bool(len(p) > 0) if bucket == "age_lt30d" else True,
                }
            )
    return pd.DataFrame(rows)


def feature_quality(df: pd.DataFrame, features: list[str]) -> pd.DataFrame:
    rows = []
    for col in features:
        values = pd.to_numeric(df[col], errors="coerce")
        rows.append(
            {
                "field_name": col,
                "non_null_rate": float(values.notna().mean()),
                "nan_count": int(values.isna().sum()),
                "inf_count": int(np.isinf(values.to_numpy(dtype=float, copy=False)).sum()),
                "min": float(values.min(skipna=True)) if values.notna().any() else np.nan,
                "max": float(values.max(skipna=True)) if values.notna().any() else np.nan,
            }
        )
    return pd.DataFrame(rows).sort_values("non_null_rate")


def split_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for split, _start, _end, allowed in SPLITS:
        p = df[df["split"] == split]
        rows.append(
            {
                "split": split,
                "rows": int(len(p)),
                "symbols": int(p["symbol"].nunique()),
                "raw_states": int(p["raw_latent_state_id"].nunique()),
                "rows_state_seen_in_train": int(p["state_seen_in_train"].sum()),
                "state_seen_in_train_rate": float(p["state_seen_in_train"].mean()) if len(p) else np.nan,
                "may_allowed_for_ranking": allowed,
            }
        )
    return pd.DataFrame(rows)


def build_report(summary: dict[str, Any], split_df: pd.DataFrame, state_df: pd.DataFrame, quota_df: pd.DataFrame, quality_df: pd.DataFrame, threshold_df: pd.DataFrame) -> None:
    report = f"""# CRYPTO A7AK-LV1 Latent State Feature Build

Generated: {summary["generated_at"]}

## Decision

```text
{summary["decision"]}
```

This stage builds observable listing-age latent-state features and train-only initial raw states. It does not compute response-based merges, run replay, or run search.

## Summary

```json
{json.dumps(summary, indent=2, sort_keys=True)}
```

## Split Summary

{md_table(split_df)}

## Train-Only Thresholds

{md_table(threshold_df)}

## Largest Raw States

{md_table(state_df.head(40))}

## Age Quota Audit

{md_table(quota_df)}

## Feature Quality Worst Missing

{md_table(quality_df.head(40))}

## Boundary

```text
AUTHORIZED NEXT:
  A7AK-LV2 train-only response vector and state merge audit

NOT AUTHORIZED:
  search
  replay promotion
  alpha proof
  shadow / paper / live

LEAKAGE RULE:
  thresholds/scalers are fit on train_2024 only
  May rows are unavailable in this panel
  validation/recent only receive frozen bucket mapping
```
"""
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    auth = read_json(A7AK_LV0_AUTH)
    symbols = pd.read_csv(SYMBOL_CLASSIFICATION)
    all_parts = []
    for _, row in symbols.iterrows():
        symbol = row["symbol"]
        if not symbol_path(symbol).exists():
            continue
        all_parts.append(build_symbol_features(symbol, row))
    panel = pd.concat(all_parts, ignore_index=True)
    panel = active_cross_section_features(panel)
    thresholds = train_thresholds(panel)
    panel = bucketize(panel, thresholds)

    output_cols = [
        "symbol",
        "timestamp",
        "split",
        "search_eligibility",
        "liquidity_tier_static",
        "history_tier_static",
        "contract_format",
        "is_core12",
        "is_major",
        "feature_available_time",
        "execution_time",
        "first_observed_timestamp",
        "listing_age_hours",
        "listing_age_days",
        "log1p_listing_age_days",
        "sqrt_listing_age_days",
        "age_percentile_active_universe",
        "history_length_hours",
        "rolling_coverage_168h",
        "gap_hours_recent_168h",
        "median_quote_volume_168h",
        "log_quote_volume_168h",
        "liquidity_rank_active_universe",
        "trade_count_168h",
        "realized_vol_24h",
        "realized_vol_72h",
        "realized_vol_168h",
        "volume_volatility_ratio_168h",
        "funding_rate_abs_168h",
        "funding_rate_mean_168h",
        "basis_abs_168h",
        "premium_abs_168h",
        "open_interest_change_24h",
        "trade_return_24h",
        "oi_x_price_move_24h",
        "age_x_liquidity",
        "age_x_volatility",
        "age_x_funding_abs",
        "age_bucket_dynamic",
        "liquidity_state",
        "volatility_state",
        "funding_abs_state",
        "basis_abs_state",
        "coverage_state",
        "major_state",
        "raw_latent_state_label",
        "raw_latent_state_id",
        "state_seen_in_train",
    ]
    panel_out = panel[output_cols].copy()
    for col in panel_out.columns:
        if pd.api.types.is_numeric_dtype(panel_out[col]):
            panel_out[col] = panel_out[col].replace([np.inf, -np.inf], np.nan)
    panel_out.to_parquet(OUTPUT_PANEL, engine="pyarrow", index=False)

    state_df = state_registry(panel_out)
    symbol_cov = symbol_state_coverage(panel_out)
    quota_df = age_quota_audit(panel_out)
    state_feature_cols = [
        "listing_age_days",
        "log1p_listing_age_days",
        "sqrt_listing_age_days",
        "age_percentile_active_universe",
        "rolling_coverage_168h",
        "gap_hours_recent_168h",
        "median_quote_volume_168h",
        "log_quote_volume_168h",
        "liquidity_rank_active_universe",
        "trade_count_168h",
        "realized_vol_24h",
        "realized_vol_72h",
        "realized_vol_168h",
        "volume_volatility_ratio_168h",
        "funding_rate_abs_168h",
        "funding_rate_mean_168h",
        "basis_abs_168h",
        "premium_abs_168h",
        "open_interest_change_24h",
        "trade_return_24h",
        "oi_x_price_move_24h",
        "age_x_liquidity",
        "age_x_volatility",
        "age_x_funding_abs",
    ]
    quality_df = feature_quality(panel_out, state_feature_cols)
    split_df = split_summary(panel_out)

    blockers = []
    if auth.get("requires_user_approval_before_execution") is not True:
        blockers.append("missing_lv0_approval_gate")
    if int(np.isinf(panel_out.select_dtypes(include=[np.number]).to_numpy(dtype=float, copy=False)).sum()):
        blockers.append("inf_in_state_feature_panel")
    if int((thresholds["fit_rows"] == 0).sum()):
        blockers.append("empty_train_threshold_fit")

    summary = {
        "generated_at": utc_now(),
        "decision": "PASS_A7AK_LV1_LATENT_STATE_FEATURES_READY",
        "input_panel_root": str(PANEL_ROOT),
        "input_symbol_classification": str(SYMBOL_CLASSIFICATION),
        "output_panel": str(OUTPUT_PANEL),
        "rows": int(len(panel_out)),
        "symbols": int(panel_out["symbol"].nunique()),
        "columns": int(len(panel_out.columns)),
        "raw_latent_states": int(panel_out["raw_latent_state_id"].nunique()),
        "train_seen_states": int(panel_out.loc[panel_out["state_seen_in_train"], "raw_latent_state_id"].nunique()),
        "unseen_state_rows": int((~panel_out["state_seen_in_train"]).sum()),
        "unseen_state_row_share": float((~panel_out["state_seen_in_train"]).mean()),
        "age_lt30_rows": int((panel_out["age_bucket_dynamic"] == "age_lt30d").sum()),
        "age_lt30_symbols": int(panel_out.loc[panel_out["age_bucket_dynamic"] == "age_lt30d", "symbol"].nunique()),
        "age_lt30_fixed_quota_minimum": 0.10,
        "executes_replay": False,
        "executes_search": False,
        "executes_state_construction": True,
        "authorizes_lv2_response_merge_audit": True,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "blockers": blockers,
        "warnings": [
            "LV1 uses interpretable train-only bucketized raw states, not response-merged states",
            "Short-history symbols can contribute to lifecycle state research but not primary proof",
            "May 2026 rows are unavailable in the input panel",
            "Raw latent states unseen in train are flagged and require LV2/LV3 handling before use",
        ],
    }
    if blockers:
        summary["decision"] = "HOLD_A7AK_LV1_LATENT_STATE_FEATURE_BUILD_BLOCKED"
        summary["authorizes_lv2_response_merge_audit"] = False

    write_json(OUT_DIR / "a7ak_lv1_manifest.json", summary)
    thresholds.to_csv(OUT_DIR / "a7ak_lv1_train_thresholds.csv", index=False)
    state_df.to_csv(OUT_DIR / "a7ak_lv1_raw_state_registry.csv", index=False)
    symbol_cov.to_csv(OUT_DIR / "a7ak_lv1_symbol_state_coverage.csv", index=False)
    quota_df.to_csv(OUT_DIR / "a7ak_lv1_age_quota_audit.csv", index=False)
    quality_df.to_csv(OUT_DIR / "a7ak_lv1_state_feature_quality.csv", index=False)
    split_df.to_csv(OUT_DIR / "a7ak_lv1_split_summary.csv", index=False)

    DATA_ROOT.joinpath("gold", "metadata").mkdir(parents=True, exist_ok=True)
    state_df.to_csv(DATA_ROOT / "gold" / "metadata" / "binance_universe498_latent_state_registry_v1_20260527.csv", index=False)
    thresholds.to_csv(DATA_ROOT / "gold" / "metadata" / "binance_universe498_latent_state_train_thresholds_v1_20260527.csv", index=False)

    build_report(summary, split_df, state_df, quota_df, quality_df, thresholds)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
