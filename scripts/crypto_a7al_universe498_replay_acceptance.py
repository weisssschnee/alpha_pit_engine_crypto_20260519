from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(r"G:\AlphaFactory_CryptoData")

PANEL_ROOT = DATA_ROOT / "gold" / "features" / "binance_universe498_replay_1h_v1_20260525"
SOURCE_REPORT = DATA_ROOT / "reports" / "BINANCE_UNIVERSE498_REPLAY_1H_V1_20260525.json"
SOURCE_MANIFEST = DATA_ROOT / "manifests" / "binance_universe498_replay_1h_v1_20260525_manifest.csv"
SOURCE_COVERAGE = DATA_ROOT / "manifests" / "binance_universe498_replay_1h_v1_20260525_coverage.csv"

OUT_DIR = ROOT / "runtime" / "a7al_universe498_replay_acceptance"
REPORT_ACCEPTANCE = ROOT / "reports" / "CRYPTO_A7AL0_UNIVERSE498_REPLAY_ACCEPTANCE_20260526.md"
REPORT_CONTRACT = ROOT / "reports" / "CRYPTO_A7AM0_UNIVERSE498_FEATURE_SYMBOL_CONTRACT_20260526.md"
DATA_METADATA_DIR = DATA_ROOT / "gold" / "metadata"

CORE12 = {
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
}

MAJORS = {"BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"}

SPLITS = [
    ("train_2024", pd.Timestamp("2024-01-01 00:00:00+00:00"), pd.Timestamp("2024-12-31 23:00:00+00:00"), True),
    ("validation_2025H1", pd.Timestamp("2025-01-01 00:00:00+00:00"), pd.Timestamp("2025-06-30 23:00:00+00:00"), True),
    ("recent_2025H2_2026Apr", pd.Timestamp("2025-07-01 00:00:00+00:00"), pd.Timestamp("2026-04-30 23:00:00+00:00"), True),
    ("may_2026_stress_unavailable", pd.Timestamp("2026-05-01 00:00:00+00:00"), pd.Timestamp("2026-05-31 23:00:00+00:00"), False),
]

NON_NEGATIVE_COLUMNS = [
    "trade_open",
    "trade_high",
    "trade_low",
    "trade_close",
    "trade_volume",
    "trade_quote_volume",
    "trade_count",
    "taker_buy_volume",
    "taker_buy_quote_volume",
    "metrics_n_5m",
    "open_interest_last",
    "open_interest_mean",
    "open_interest_value_last",
    "open_interest_value_mean",
    "mark_open",
    "mark_high",
    "mark_low",
    "mark_close",
    "mark_count",
    "index_open",
    "index_high",
    "index_low",
    "index_close",
    "index_count",
    "premium_count",
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


def read_symbol(symbol: str, columns: list[str] | None = None) -> pd.DataFrame:
    df = pd.read_parquet(symbol_path(symbol), engine="pyarrow", columns=columns)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    if "feature_available_time" in df.columns:
        df["feature_available_time"] = pd.to_datetime(df["feature_available_time"], utc=True)
    if "execution_time" in df.columns:
        df["execution_time"] = pd.to_datetime(df["execution_time"], utc=True)
    return df


def classify_symbol_format(symbol: str) -> tuple[str, str]:
    base = symbol.removesuffix("USDT")
    if re.match(r"^(1000|1000000|1M)", base):
        return "multiplier_contract", base
    return "plain_contract", base


def feature_family(field: str) -> tuple[str, bool, str]:
    if field in {"symbol", "timestamp"}:
        return "key", False, "identity"
    if field in {"trade_return_1h", "forward_trade_return_1h", "premium_close_bps"}:
        return "derived_replay_base", False, "derived from accepted source fields"
    if field.startswith("trade_") or field in {"taker_buy_volume", "taker_buy_quote_volume", "kline_taker_buy_quote_share"}:
        return "trade_ohlcv", True, "Binance futures trade kline 1h"
    if field.startswith("mark_") or field.startswith("index_") or field.startswith("premium_") or field in {"mark_index_basis_bps", "mark_trade_basis_bps"}:
        return "mark_index_premium", True, "Binance mark/index/premium 1h"
    if field.startswith("funding_"):
        return "funding", True, "Binance funding event observed in 1h"
    if field in {
        "metrics_n_5m",
        "open_interest_last",
        "open_interest_mean",
        "open_interest_value_last",
        "open_interest_value_mean",
        "top_long_short_account_ratio_last",
        "top_long_short_account_ratio_mean",
        "top_long_short_position_ratio_last",
        "top_long_short_position_ratio_mean",
        "global_long_short_account_ratio_last",
        "global_long_short_account_ratio_mean",
        "taker_buy_sell_volume_ratio_last",
        "taker_buy_sell_volume_ratio_mean",
    }:
        return "metrics_positioning", True, "Binance metrics 5m aggregated to 1h"
    if field in {
        "source_trade_klines",
        "source_metrics",
        "source_market_funding",
        "feature_available_time",
        "execution_time",
        "is_historical_backfill",
        "is_forward_only",
    }:
        return "metadata_timing", False, "pipeline metadata"
    return "other", False, "unclassified; review before generator use"


def audit_symbol(symbol: str, manifest_row: pd.Series, coverage_row: pd.Series) -> dict[str, Any]:
    path = symbol_path(symbol)
    row: dict[str, Any] = {
        "symbol": symbol,
        "path": str(path),
        "file_exists": path.exists(),
        "manifest_status": str(manifest_row.get("status", "")),
        "manifest_rows": int(manifest_row.get("rows", 0)),
        "coverage_metrics": float(coverage_row.get("metrics_coverage", np.nan)),
        "coverage_market_funding": float(coverage_row.get("market_funding_coverage", np.nan)),
    }
    if not path.exists():
        row["read_ok"] = False
        row["error"] = "missing_parquet"
        return row
    try:
        df = read_symbol(symbol)
        numeric = df.select_dtypes(include=[np.number])
        ts = df["timestamp"]
        expected = int(((ts.max() - ts.min()).total_seconds() // 3600) + 1) if len(ts) else 0
        gap_hours = max(0, expected - int(ts.nunique()))
        non_negative = [c for c in NON_NEGATIVE_COLUMNS if c in df.columns]
        negative_non_allowed = int((df[non_negative] < 0).sum().sum()) if non_negative else 0
        feature_lag_min_hours = float(((df["feature_available_time"] - df["timestamp"]).dt.total_seconds() / 3600).min())
        execution_lag_min_hours = float(((df["execution_time"] - df["timestamp"]).dt.total_seconds() / 3600).min())
        feature_to_exec_min_hours = float(((df["execution_time"] - df["feature_available_time"]).dt.total_seconds() / 3600).min())
        quote = pd.to_numeric(df["trade_quote_volume"], errors="coerce")
        row.update(
            {
                "read_ok": True,
                "error": "",
                "rows": int(len(df)),
                "row_count_match": int(len(df)) == int(manifest_row.get("rows", -1)),
                "timestamp_min": str(ts.min()),
                "timestamp_max": str(ts.max()),
                "duplicate_symbol_timestamp": int(df.duplicated(["symbol", "timestamp"]).sum()),
                "gap_hours": int(gap_hours),
                "inf_cell_count": int(np.isinf(numeric.to_numpy(dtype=float, copy=False)).sum()) if not numeric.empty else 0,
                "nan_cell_count": int(numeric.isna().sum().sum()) if not numeric.empty else 0,
                "negative_non_allowed_count": negative_non_allowed,
                "feature_lag_min_hours": feature_lag_min_hours,
                "execution_lag_min_hours": execution_lag_min_hours,
                "feature_to_execution_lag_min_hours": feature_to_exec_min_hours,
                "median_hourly_quote_volume": float(quote.median()),
                "mean_hourly_quote_volume": float(quote.mean()),
                "p10_hourly_quote_volume": float(quote.quantile(0.10)),
                "p90_hourly_quote_volume": float(quote.quantile(0.90)),
                "metrics_missing_rows": int(manifest_row.get("missing_metrics_rows", 0)),
                "market_funding_missing_rows": int(manifest_row.get("missing_market_funding_rows", 0)),
                "source_trade_klines_rate": float(df["source_trade_klines"].fillna(False).mean()),
                "source_metrics_rate": float(df["source_metrics"].fillna(False).mean()),
                "source_market_funding_rate": float(df["source_market_funding"].fillna(False).mean()),
            }
        )
        for split, start, end, _allowed in SPLITS:
            part = df[(df["timestamp"] >= start) & (df["timestamp"] <= end)]
            row[f"rows_{split}"] = int(len(part))
    except Exception as exc:  # pragma: no cover
        row["read_ok"] = False
        row["error"] = repr(exc)
    return row


def assign_liquidity_tiers(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out = out.sort_values("median_hourly_quote_volume", ascending=False).reset_index(drop=True)
    out["liquidity_rank"] = np.arange(1, len(out) + 1)
    out["liquidity_tier"] = pd.cut(
        out["liquidity_rank"],
        bins=[0, 20, 50, 100, 200, 500],
        labels=["top20", "top50", "top100", "top200", "tail"],
        include_lowest=True,
    ).astype(str)
    out["history_tier"] = np.select(
        [
            (out["rows_train_2024"] >= 8000) & (out["rows_validation_2025H1"] >= 4000) & (out["rows_recent_2025H2_2026Apr"] >= 7000),
            (out["rows_validation_2025H1"] >= 4000) & (out["rows_recent_2025H2_2026Apr"] >= 7000),
            out["rows_recent_2025H2_2026Apr"] >= 7000,
        ],
        ["full_2024_2026apr", "listed_by_2025H1", "recent_only"],
        default="short_history",
    )
    out["search_eligibility"] = np.select(
        [
            (out["history_tier"] == "full_2024_2026apr")
            & (out["coverage_metrics"] >= 0.995)
            & (out["coverage_market_funding"] >= 0.995)
            & (out["duplicate_symbol_timestamp"] == 0)
            & (out["inf_cell_count"] == 0)
            & (out["negative_non_allowed_count"] == 0),
            (out["coverage_metrics"] >= 0.99)
            & (out["coverage_market_funding"] >= 0.99)
            & (out["duplicate_symbol_timestamp"] == 0)
            & (out["inf_cell_count"] == 0),
        ],
        ["strict_full_history", "listing_aware"],
        default="hold_quality_or_short_history",
    )
    formatted = out["symbol"].map(classify_symbol_format)
    out["contract_format"] = [x[0] for x in formatted]
    out["base_asset"] = [x[1] for x in formatted]
    out["is_core12"] = out["symbol"].isin(CORE12)
    out["is_major"] = out["symbol"].isin(MAJORS)
    return out


def build_split_coverage(symbol_quality: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for split, _start, _end, allowed in SPLITS:
        rows.append(
            {
                "split": split,
                "rows": int(symbol_quality[f"rows_{split}"].sum()),
                "symbols_with_rows": int((symbol_quality[f"rows_{split}"] > 0).sum()),
                "strict_full_history_symbols": int(((symbol_quality["search_eligibility"] == "strict_full_history") & (symbol_quality[f"rows_{split}"] > 0)).sum()),
                "may_allowed_for_ranking": allowed,
            }
        )
    return pd.DataFrame(rows)


def build_reports(summary: dict[str, Any], dataset_summary: pd.DataFrame, symbol_quality: pd.DataFrame, feature_contract: pd.DataFrame, split_coverage: pd.DataFrame, symbol_classes: pd.DataFrame) -> None:
    tier_summary = symbol_classes.groupby(["search_eligibility", "liquidity_tier"], dropna=False).size().reset_index(name="symbols")
    source_summary = feature_contract.groupby("source_class", dropna=False).size().reset_index(name="fields")
    acceptance = f"""# CRYPTO A7AL-0 Universe498 Replay Acceptance

Generated: {summary["generated_at"]}

## Decision

```text
{summary["decision"]}
```

This audit validates the top498 1h replay base. It does not run replay and does not run search.

## Summary

```json
{json.dumps(summary, indent=2, sort_keys=True)}
```

## Dataset Summary

{md_table(dataset_summary)}

## Split Coverage

{md_table(split_coverage)}

## Search Eligibility x Liquidity Tier

{md_table(tier_summary, 50)}

## Worst Quality Rows

{md_table(symbol_quality.sort_values(["search_eligibility", "median_hourly_quote_volume"], ascending=[True, False])[[
    "symbol",
    "search_eligibility",
    "history_tier",
    "liquidity_tier",
    "rows",
    "coverage_metrics",
    "coverage_market_funding",
    "gap_hours",
    "median_hourly_quote_volume",
]], 40)}

## Timing Boundary

```text
timestamp = 1h bucket start UTC
feature_available_time = timestamp + 1h
panel execution_time = timestamp + 1h
recommended replay execution_time = timestamp + 1h / next 1h bar open; fixed delay stress prohibited
May 2026 rows are not present in this panel and cannot be used for ranking or stress here
```
"""
    REPORT_ACCEPTANCE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_ACCEPTANCE.write_text(acceptance, encoding="utf-8")

    contract = f"""# CRYPTO A7AM-0 Universe498 Feature And Symbol Contract

Generated: {summary["generated_at"]}

## Decision

```text
{summary["decision"]}
```

This contract separates feature families and symbol classes for the next controlled smoke. It does not authorize large search.

## Feature Families

{md_table(source_summary)}

## Symbol Classes

{md_table(tier_summary, 60)}

## Authorized Next Step

```text
AUTHORIZED:
  A7AK-min small controlled field-family smoke

NOT AUTHORIZED:
  large formula search
  alpha proof
  shadow / paper / live

UNIVERSE:
  primary = strict_full_history subset
  secondary = listing_aware diagnostic only
  May unavailable in this panel

FEATURE FAMILY BLOCKS:
  trade_ohlcv
  mark_index_premium
  funding
  metrics_positioning
  derived_replay_base
```

## Feature Contract Sample

{md_table(feature_contract, 80)}
"""
    REPORT_CONTRACT.parent.mkdir(parents=True, exist_ok=True)
    REPORT_CONTRACT.write_text(contract, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    source_report = read_json(SOURCE_REPORT)
    manifest = pd.read_csv(SOURCE_MANIFEST)
    coverage = pd.read_csv(SOURCE_COVERAGE)
    manifest_map = manifest.set_index("symbol")
    coverage_map = coverage.set_index("symbol")
    symbols = sorted(manifest["symbol"].astype(str).tolist())

    quality_rows = []
    for symbol in symbols:
        quality_rows.append(audit_symbol(symbol, manifest_map.loc[symbol], coverage_map.loc[symbol]))
    symbol_quality = assign_liquidity_tiers(pd.DataFrame(quality_rows))

    sample_symbol = "BTCUSDT" if "BTCUSDT" in symbols else symbols[0]
    sample_schema = pq.read_schema(symbol_path(sample_symbol))
    feature_contract = pd.DataFrame(
        [
            {
                "field_name": name,
                "source_class": feature_family(name)[0],
                "independent_source": feature_family(name)[1],
                "source_detail": feature_family(name)[2],
                "feature_available_rule": "timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited",
            }
            for name in sample_schema.names
        ]
    )

    split_coverage = build_split_coverage(symbol_quality)
    dataset_summary = pd.DataFrame(
        [
            {
                "dataset": "binance_universe498_replay_1h_v1",
                "symbols": int(len(symbols)),
                "rows_manifest": int(manifest["rows"].sum()),
                "rows_actual": int(symbol_quality["rows"].sum()),
                "duplicate_timestamp_count": int(symbol_quality["duplicate_symbol_timestamp"].sum()),
                "gap_hours": int(symbol_quality["gap_hours"].sum()),
                "inf_cell_count": int(symbol_quality["inf_cell_count"].sum()),
                "negative_non_allowed_count": int(symbol_quality["negative_non_allowed_count"].sum()),
                "strict_full_history_symbols": int((symbol_quality["search_eligibility"] == "strict_full_history").sum()),
                "listing_aware_symbols": int((symbol_quality["search_eligibility"] == "listing_aware").sum()),
            }
        ]
    )

    blockers: list[str] = []
    if int((symbol_quality["read_ok"] == False).sum()):
        blockers.append("symbol_read_error")
    if int(symbol_quality["duplicate_symbol_timestamp"].sum()):
        blockers.append("duplicate_symbol_timestamp")
    if int(symbol_quality["inf_cell_count"].sum()):
        blockers.append("inf_cells")
    if int(symbol_quality["negative_non_allowed_count"].sum()):
        blockers.append("negative_non_allowed_values")
    if int((feature_contract["source_class"] == "other").sum()):
        blockers.append("unclassified_feature_fields")

    summary: dict[str, Any] = {
        "generated_at": utc_now(),
        "decision": "PASS_A7AL_UNIVERSE498_REPLAY_BASE_ACCEPTED",
        "source_report": str(SOURCE_REPORT),
        "panel_root": str(PANEL_ROOT),
        "symbols": int(len(symbols)),
        "rows": int(symbol_quality["rows"].sum()),
        "columns": int(len(sample_schema.names)),
        "strict_full_history_symbols": int((symbol_quality["search_eligibility"] == "strict_full_history").sum()),
        "listing_aware_symbols": int((symbol_quality["search_eligibility"] == "listing_aware").sum()),
        "hold_symbols": int((symbol_quality["search_eligibility"] == "hold_quality_or_short_history").sum()),
        "duplicate_timestamp_count": int(symbol_quality["duplicate_symbol_timestamp"].sum()),
        "inf_cell_count": int(symbol_quality["inf_cell_count"].sum()),
        "negative_non_allowed_count": int(symbol_quality["negative_non_allowed_count"].sum()),
        "blockers": blockers,
        "executes_search": False,
        "executes_replay": False,
        "authorizes_a7ak_min_small_controlled_smoke": True,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "warnings": [
            "May 2026 rows are not present; May cannot be used from this panel",
            "Universe498 membership is current/listing-aware and is not by itself survivorship-safe proof",
            "Panel execution_time equals feature_available_time; experiments should use field-native latency audit and wrong-lag controls",
            "No aggTrades/book/liquidation/cross-exchange fields in this replay base",
        ],
        "source_report_rows": source_report.get("rows"),
        "source_report_symbols": source_report.get("symbols"),
    }
    if blockers:
        summary["decision"] = "HOLD_A7AL_UNIVERSE498_REPLAY_BASE_ACCEPTANCE_BLOCKED"
        summary["authorizes_a7ak_min_small_controlled_smoke"] = False

    search_config = {
        "stage": "A7AK-min",
        "input_panel_root": str(PANEL_ROOT),
        "symbol_classification": str(OUT_DIR / "a7am_symbol_classification.csv"),
        "feature_contract": str(OUT_DIR / "a7am_feature_contract.csv"),
        "primary_universe_rule": "search_eligibility == strict_full_history",
        "secondary_universe_rule": "listing_aware diagnostic only",
        "feature_families": sorted(feature_contract["source_class"].unique().tolist()),
        "blocked": [
            "large_search",
            "alpha_proof",
            "shadow_paper_live",
            "May ranking/tuning/selection",
            "using listing-aware universe as final proof universe without survivorship caveat",
        ],
        "timing_contract": {
            "timestamp": "1h bucket start UTC",
            "feature_available_time": "timestamp + 1h",
            "panel_execution_time": "timestamp + 1h",
            "recommended_stress_execution_time": "field_native_latency_audit",
        },
    }

    DATA_METADATA_DIR.mkdir(parents=True, exist_ok=True)
    data_feature_contract = DATA_METADATA_DIR / "binance_universe498_replay_1h_v1_feature_contract_20260526.csv"
    data_symbol_classification = DATA_METADATA_DIR / "binance_universe498_replay_1h_v1_symbol_classification_20260526.csv"
    data_search_config = DATA_METADATA_DIR / "binance_universe498_replay_1h_v1_a7ak_min_search_config_20260526.json"
    search_config["data_metadata_feature_contract"] = str(data_feature_contract)
    search_config["data_metadata_symbol_classification"] = str(data_symbol_classification)
    search_config["data_metadata_search_config"] = str(data_search_config)

    write_json(OUT_DIR / "a7al_summary.json", summary)
    write_json(OUT_DIR / "a7ak_min_search_chain_config.json", search_config)
    write_json(data_search_config, search_config)
    dataset_summary.to_csv(OUT_DIR / "a7al_dataset_summary.csv", index=False)
    symbol_quality.to_csv(OUT_DIR / "a7al_symbol_quality.csv", index=False)
    split_coverage.to_csv(OUT_DIR / "a7al_split_coverage.csv", index=False)
    feature_contract.to_csv(OUT_DIR / "a7am_feature_contract.csv", index=False)
    feature_contract.to_csv(data_feature_contract, index=False)
    symbol_classification = symbol_quality[
        [
            "symbol",
            "base_asset",
            "contract_format",
            "is_core12",
            "is_major",
            "liquidity_rank",
            "liquidity_tier",
            "history_tier",
            "search_eligibility",
            "median_hourly_quote_volume",
            "rows",
            "timestamp_min",
            "timestamp_max",
        ]
    ]
    symbol_classification.to_csv(OUT_DIR / "a7am_symbol_classification.csv", index=False)
    symbol_classification.to_csv(data_symbol_classification, index=False)

    build_reports(summary, dataset_summary, symbol_quality, feature_contract, split_coverage, symbol_quality)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
