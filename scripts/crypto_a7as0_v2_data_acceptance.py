from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow.parquet as pq


DATA_ROOT = Path(r"G:\AlphaFactory_CryptoData")
REPO = Path(__file__).resolve().parents[1]

BASE_DIR = DATA_ROOT / "gold" / "features" / "binance_universe498_replay_1h_v2_20260527"
BASE_REPORT = DATA_ROOT / "reports" / "binance_universe498_replay_1h_v2_20260527.json"
BASE_MANIFEST = DATA_ROOT / "manifests" / "binance_universe498_replay_1h_v2_20260527_manifest.csv"
BASE_COVERAGE = DATA_ROOT / "manifests" / "binance_universe498_replay_1h_v2_20260527_coverage.csv"

OVERLAY_DIR = DATA_ROOT / "gold" / "features" / "okx_binance_cross_exchange_unified_1h_30d_v2_20260527"
OVERLAY_REPORT = DATA_ROOT / "reports" / "okx_binance_cross_exchange_unified_1h_30d_v2_20260527.json"
OVERLAY_MANIFEST = DATA_ROOT / "manifests" / "okx_binance_cross_exchange_unified_1h_30d_v2_20260527_manifest.csv"
OVERLAY_COVERAGE = DATA_ROOT / "manifests" / "okx_binance_cross_exchange_unified_1h_30d_v2_20260527_coverage.csv"
OVERLAY_CONTRACT = DATA_ROOT / "gold" / "metadata" / "okx_binance_cross_exchange_unified_1h_30d_v2_field_contract_20260527.json"

OUT_DIR = REPO / "runtime" / "a7as0_v2_data_acceptance"
REPORT = REPO / "reports" / "CRYPTO_A7AS0_V2_DATA_ACCEPTANCE_20260527.md"


REQUIRED_BASE_COLUMNS = [
    "symbol",
    "timestamp",
    "trade_open",
    "trade_high",
    "trade_low",
    "trade_close",
    "trade_volume",
    "trade_quote_volume",
    "trade_count",
    "mark_close",
    "index_close",
    "premium_close",
    "premium_close_bps",
    "mark_index_basis_bps",
    "funding_rate",
    "open_interest_last",
    "open_interest_mean",
    "open_interest_value_last",
    "open_interest_value_mean",
    "global_long_short_account_ratio_last",
    "top_long_short_account_ratio_last",
    "top_long_short_position_ratio_last",
    "taker_buy_sell_volume_ratio_last",
]

REQUIRED_OVERLAY_COLUMN_PATTERNS = [
    "okx",
    "binance",
    "spread",
    "basis",
    "funding",
    "open_interest",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    try:
        return df.head(max_rows).to_markdown(index=False)
    except Exception:
        return "```\n" + df.head(max_rows).to_string(index=False) + "\n```"


def parquet_schema_columns(dataset_dir: Path) -> list[str]:
    first = next(dataset_dir.glob("symbol=*/part.parquet"), None)
    if first is None:
        return []
    return pq.read_schema(first).names


def sample_symbols(dataset_dir: Path, symbols: list[str], columns: list[str] | None = None) -> pd.DataFrame:
    parts = []
    for symbol in symbols:
        path = dataset_dir / f"symbol={symbol}" / "part.parquet"
        if path.exists():
            available = pq.read_schema(path).names
            read_cols = [c for c in columns if c in available] if columns else None
            df = pd.read_parquet(path, columns=read_cols)
            if "symbol" not in df.columns:
                df["symbol"] = symbol
            parts.append(df)
    if not parts:
        return pd.DataFrame()
    out = pd.concat(parts, ignore_index=True)
    if "timestamp" in out.columns:
        out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True)
    return out


def coverage_summary(path: Path, key_cols: list[str]) -> tuple[pd.DataFrame, dict[str, Any]]:
    cov = pd.read_csv(path)
    summary: dict[str, Any] = {"rows": int(len(cov))}
    for col in key_cols:
        if col in cov.columns:
            vals = pd.to_numeric(cov[col], errors="coerce")
            summary[f"{col}_min"] = float(vals.min())
            summary[f"{col}_median"] = float(vals.median())
            summary[f"{col}_p05"] = float(vals.quantile(0.05))
            summary[f"{col}_below_095"] = int((vals < 0.95).sum())
    return cov, summary


def audit_base() -> tuple[dict[str, Any], pd.DataFrame]:
    report = read_json(BASE_REPORT)
    columns = parquet_schema_columns(BASE_DIR)
    missing = [c for c in REQUIRED_BASE_COLUMNS if c not in columns]
    cov, cov_summary = coverage_summary(
        BASE_COVERAGE,
        [
            "metrics_coverage",
            "market_funding_coverage",
            "open_interest_last_coverage",
            "open_interest_value_last_coverage",
        ],
    )
    sample = sample_symbols(
        BASE_DIR,
        ["BTCUSDT", "ETHUSDT", "SOLUSDT", "1000PEPEUSDT", "0GUSDT"],
        REQUIRED_BASE_COLUMNS,
    )
    sample_checks: list[dict[str, Any]] = []
    if not sample.empty:
        for symbol, g in sample.groupby("symbol"):
            dup = int(g.duplicated(["symbol", "timestamp"]).sum())
            inf = int(np.isinf(g.select_dtypes(include=[np.number]).to_numpy()).sum())
            sample_checks.append(
                {
                    "symbol": symbol,
                    "rows": int(len(g)),
                    "min_timestamp": str(g["timestamp"].min()),
                    "max_timestamp": str(g["timestamp"].max()),
                    "duplicate_symbol_timestamp": dup,
                    "inf_numeric_cells": inf,
                    "trade_close_na": int(g["trade_close"].isna().sum()) if "trade_close" in g else None,
                    "open_interest_last_na": int(g["open_interest_last"].isna().sum()) if "open_interest_last" in g else None,
                }
            )
    manifest = pd.read_csv(BASE_MANIFEST)
    component_status_cols = [c for c in manifest.columns if c.lower() in {"status", "decision", "state"}]
    return (
        {
            "dataset": report.get("dataset"),
            "path": str(BASE_DIR),
            "report_decision": report.get("decision"),
            "symbols_reported": report.get("symbols"),
            "rows_reported": report.get("rows"),
            "min_timestamp": report.get("min_timestamp"),
            "max_timestamp": report.get("max_timestamp"),
            "duplicate_timestamp_count": report.get("duplicate_timestamp_count"),
            "inf_cell_count": report.get("inf_cell_count"),
            "gap_hours_gt_1": report.get("gap_hours_gt_1"),
            "schema_columns": len(columns),
            "missing_required_columns": missing,
            "manifest_rows": int(len(manifest)),
            "manifest_status_columns": component_status_cols,
            **cov_summary,
        },
        pd.DataFrame(sample_checks),
    )


def audit_overlay() -> tuple[dict[str, Any], pd.DataFrame, pd.DataFrame]:
    report = read_json(OVERLAY_REPORT)
    contract = read_json(OVERLAY_CONTRACT)
    columns = parquet_schema_columns(OVERLAY_DIR)
    pattern_hits = {
        pat: int(sum(pat.lower() in col.lower() for col in columns)) for pat in REQUIRED_OVERLAY_COLUMN_PATTERNS
    }
    cov, cov_summary = coverage_summary(
        OVERLAY_COVERAGE,
        ["price_funding_coverage", "oi_coverage", "crowding_taker_coverage"],
    )
    overlay_symbols = set(cov["symbol"].astype(str)) if "symbol" in cov.columns else set()
    base_cov = pd.read_csv(BASE_COVERAGE, usecols=["symbol"])
    base_symbols = set(base_cov["symbol"].astype(str))
    sample = sample_symbols(
        OVERLAY_DIR,
        ["BTCUSDT", "ETHUSDT", "SOLUSDT", "1000PEPEUSDT", "0GUSDT"],
        columns,
    )
    sample_checks: list[dict[str, Any]] = []
    if not sample.empty:
        for symbol, g in sample.groupby("symbol"):
            dup = int(g.duplicated(["symbol", "timestamp"]).sum())
            inf = int(np.isinf(g.select_dtypes(include=[np.number]).to_numpy()).sum())
            sample_checks.append(
                {
                    "symbol": symbol,
                    "rows": int(len(g)),
                    "min_timestamp": str(g["timestamp"].min()),
                    "max_timestamp": str(g["timestamp"].max()),
                    "duplicate_symbol_timestamp": dup,
                    "inf_numeric_cells": inf,
                }
            )
    timing_rows = []
    if isinstance(contract, dict):
        for field, meta in contract.items():
            if isinstance(meta, dict):
                timing_rows.append(
                    {
                        "field": field,
                        "source": meta.get("source") or meta.get("source_family"),
                        "pit": meta.get("pit") or meta.get("pit_safe") or meta.get("observable_time"),
                        "feature_available_time": meta.get("feature_available_time"),
                        "usage": meta.get("usage") or meta.get("allowed_usage"),
                    }
                )
    timing = pd.DataFrame(timing_rows)
    return (
        {
            "dataset": report.get("dataset"),
            "path": str(OVERLAY_DIR),
            "report_decision": report.get("decision"),
            "symbols_reported": report.get("symbols"),
            "rows_reported": report.get("rows"),
            "min_timestamp": report.get("min_timestamp"),
            "max_timestamp": report.get("max_timestamp"),
            "duplicate_timestamp_count": report.get("duplicate_timestamp_count"),
            "inf_cell_count": report.get("inf_cell_count"),
            "schema_columns": len(columns),
            "pattern_hits": pattern_hits,
            "overlay_symbols_in_base": int(len(overlay_symbols & base_symbols)),
            "overlay_symbols_not_in_base": int(len(overlay_symbols - base_symbols)),
            "base_symbols_without_overlay": int(len(base_symbols - overlay_symbols)),
            **cov_summary,
        },
        pd.DataFrame(sample_checks),
        timing,
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    base_summary, base_samples = audit_base()
    overlay_summary, overlay_samples, overlay_timing = audit_overlay()

    blockers: list[str] = []
    warnings: list[str] = []
    if base_summary["missing_required_columns"]:
        blockers.append("base_missing_required_columns")
    if base_summary.get("duplicate_timestamp_count", 0) != 0:
        blockers.append("base_duplicate_timestamps")
    if base_summary.get("inf_cell_count", 0) != 0:
        blockers.append("base_inf_cells")
    if base_summary.get("metrics_coverage_p05", 0) < 0.95:
        blockers.append("base_metrics_coverage_p05_below_95pct")
    if base_summary.get("market_funding_coverage_p05", 0) < 0.95:
        blockers.append("base_market_funding_coverage_p05_below_95pct")
    if base_summary.get("gap_hours_gt_1", 0) > 0:
        warnings.append("base_has_listing_or_patch_gaps_gt_1h_review_required")

    if overlay_summary.get("duplicate_timestamp_count", 0) != 0:
        blockers.append("overlay_duplicate_timestamps")
    if overlay_summary.get("inf_cell_count", 0) != 0:
        blockers.append("overlay_inf_cells")
    if overlay_summary.get("price_funding_coverage_p05", 0) < 0.90:
        blockers.append("overlay_price_funding_coverage_p05_below_90pct")
    if overlay_summary.get("overlay_symbols_not_in_base", 0) > 0:
        blockers.append("overlay_symbols_not_in_base")
    if overlay_summary.get("base_symbols_without_overlay", 0) > 0:
        warnings.append("overlay_is_30d_subset_not_full_universe")

    decision = "PASS_A7AS0_V2_DATA_ACCEPTANCE_READY_FOR_A7AL2G" if not blockers else "HOLD_A7AS0_V2_DATA_ACCEPTANCE"
    manifest = {
        "generated_at": utc_now(),
        "decision": decision,
        "base_summary": base_summary,
        "overlay_summary": overlay_summary,
        "blockers": blockers,
        "warnings": warnings,
        "authorizes_a7al2g_matched_control_gate": not blockers,
        "authorizes_formula_search_execution": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "usage_boundary": {
            "base_v2": "historical 1h replay base through 2026-05-26",
            "overlay_v2": "30d cross-exchange diagnostic overlay; not full-history proof input",
            "one_bar_lag_stress": "required for field-family smoke and matched-control replay",
        },
    }

    write_json(OUT_DIR / "a7as0_manifest.json", manifest)
    pd.DataFrame([base_summary]).to_csv(OUT_DIR / "a7as0_base_summary.csv", index=False)
    base_samples.to_csv(OUT_DIR / "a7as0_base_sample_audit.csv", index=False)
    pd.DataFrame([overlay_summary]).to_csv(OUT_DIR / "a7as0_overlay_summary.csv", index=False)
    overlay_samples.to_csv(OUT_DIR / "a7as0_overlay_sample_audit.csv", index=False)
    overlay_timing.to_csv(OUT_DIR / "a7as0_overlay_timing_contract_extract.csv", index=False)

    base_summary_table = pd.DataFrame([base_summary]).T.reset_index().rename(columns={"index": "metric", 0: "value"})
    overlay_summary_table = pd.DataFrame([overlay_summary]).T.reset_index().rename(columns={"index": "metric", 0: "value"})

    report = f"""# CRYPTO A7AS-0 V2 Data Acceptance

Generated: {manifest["generated_at"]}

## Decision

```text
{decision}
```

## Base Summary

{md_table(base_summary_table, 120)}

## Base Sample Audit

{md_table(base_samples, 80)}

## Overlay Summary

{md_table(overlay_summary_table, 120)}

## Overlay Sample Audit

{md_table(overlay_samples, 80)}

## Overlay Timing Contract Extract

{md_table(overlay_timing, 120)}

## Boundary

```text
Base v2 may replace v1 for replay/field-family smoke after this acceptance.
Overlay v2 is 30d diagnostic only; do not use it as full-history alpha proof input.
One-bar-lag stress remains required. Fixed +2h blanket stress remains prohibited.
No formula search, alpha proof, shadow, paper, or live is authorized by this acceptance.
```
"""
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
