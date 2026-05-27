from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(r"G:\AlphaFactory_CryptoData")

GOLD_ROOT = DATA_ROOT / "gold" / "features" / "okx_binance_cross_exchange_1h_30d_v1_20260527"
MANIFEST_PATH = DATA_ROOT / "manifests" / "okx_binance_cross_exchange_1h_30d_v1_20260527_manifest.csv"
COVERAGE_PATH = DATA_ROOT / "manifests" / "okx_binance_cross_exchange_1h_30d_v1_20260527_coverage.csv"
FIELD_CONTRACT_PATH = DATA_ROOT / "gold" / "metadata" / "okx_binance_cross_exchange_1h_30d_v1_field_contract_20260527.json"
SOURCE_REPORT_PATH = DATA_ROOT / "reports" / "OKX_BINANCE_CROSS_EXCHANGE_1H_30D_V1_20260527.md"

OUT_DIR = ROOT / "runtime" / "a7ap0_cross_exchange_overlay_acceptance"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7AP0_OKX_BINANCE_CROSS_EXCHANGE_ACCEPTANCE_20260527.md"

NUMERIC_CHECK_COLUMNS = [
    "okx_mark_close",
    "okx_index_close",
    "okx_funding_rate",
    "okx_realized_rate",
    "binance_trade_close",
    "binance_mark_close",
    "binance_index_close",
    "binance_funding_rate",
    "mark_basis_bps_okx_minus_binance",
    "index_spread_bps_okx_minus_binance",
    "funding_spread_okx_minus_binance",
    "okx_internal_mark_index_basis_bps",
    "binance_internal_mark_index_basis_bps",
]

PRICE_SCALE_MISMATCH_BPS_THRESHOLD = 500.0


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    try:
        return df.head(max_rows).to_markdown(index=False)
    except Exception:
        return "```\n" + df.head(max_rows).to_string(index=False) + "\n```"


def parquet_files() -> list[Path]:
    return sorted(GOLD_ROOT.glob("symbol=*/part.parquet"))


def load_panel() -> pd.DataFrame:
    parts = []
    for path in parquet_files():
        df = pd.read_parquet(path, engine="pyarrow")
        parts.append(df)
    if not parts:
        return pd.DataFrame()
    panel = pd.concat(parts, ignore_index=True)
    panel["timestamp"] = pd.to_datetime(panel["timestamp"], utc=True)
    panel["feature_available_time"] = pd.to_datetime(panel["feature_available_time"], utc=True)
    panel["execution_time"] = pd.to_datetime(panel["execution_time"], utc=True)
    panel["recommended_stress_execution_time"] = pd.to_datetime(panel["recommended_stress_execution_time"], utc=True)
    return panel


def field_quality(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in NUMERIC_CHECK_COLUMNS:
        if col not in panel.columns:
            rows.append({"field_name": col, "exists": False})
            continue
        s = pd.to_numeric(panel[col], errors="coerce")
        rows.append(
            {
                "field_name": col,
                "exists": True,
                "non_null_rate": float(s.notna().mean()),
                "nan_count": int(s.isna().sum()),
                "inf_count": int(np.isinf(s.dropna()).sum()),
                "min": float(s.min()) if s.notna().any() else np.nan,
                "max": float(s.max()) if s.notna().any() else np.nan,
                "mean": float(s.mean()) if s.notna().any() else np.nan,
            }
        )
    return pd.DataFrame(rows)


def symbol_quality(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for symbol, g in panel.groupby("symbol", observed=True):
        g = g.sort_values("timestamp")
        expected_hours = int(((g["timestamp"].max() - g["timestamp"].min()).total_seconds() / 3600) + 1) if len(g) else 0
        rows.append(
            {
                "symbol": symbol,
                "rows": int(len(g)),
                "timestamp_min": g["timestamp"].min(),
                "timestamp_max": g["timestamp"].max(),
                "expected_hours_between_min_max": expected_hours,
                "missing_hour_count_between_min_max": int(max(expected_hours - len(g), 0)),
                "duplicate_timestamp_count": int(g["timestamp"].duplicated().sum()),
                "okx_mark_non_null_rate": float(g["okx_mark_close"].notna().mean()) if "okx_mark_close" in g else np.nan,
                "okx_index_non_null_rate": float(g["okx_index_close"].notna().mean()) if "okx_index_close" in g else np.nan,
                "okx_funding_non_null_rate": float(g["okx_funding_rate"].notna().mean()) if "okx_funding_rate" in g else np.nan,
                "binance_funding_non_null_rate": float(g["binance_funding_rate"].notna().mean()) if "binance_funding_rate" in g else np.nan,
            }
        )
    return pd.DataFrame(rows).sort_values(["rows", "symbol"], ascending=[False, True])


def timing_audit(panel: pd.DataFrame) -> pd.DataFrame:
    checks = [
        ("feature_available_time_eq_timestamp_plus_1h", panel["feature_available_time"] == panel["timestamp"] + pd.Timedelta(hours=1)),
        ("execution_time_eq_feature_available_time", panel["execution_time"] == panel["feature_available_time"]),
        ("stress_execution_time_eq_timestamp_plus_2h", panel["recommended_stress_execution_time"] == panel["timestamp"] + pd.Timedelta(hours=2)),
        ("historical_backfill_true", panel["is_historical_backfill"].astype(bool)),
        ("forward_only_false", ~panel["is_forward_only"].astype(bool)),
    ]
    return pd.DataFrame(
        [
            {
                "check": name,
                "pass_rate": float(mask.mean()) if len(mask) else np.nan,
                "fail_count": int((~mask).sum()) if len(mask) else 0,
            }
            for name, mask in checks
        ]
    )


def price_scale_audit(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for symbol, g in panel.groupby("symbol", observed=True):
        mark_extreme = pd.to_numeric(g["mark_basis_bps_okx_minus_binance"], errors="coerce").abs() > PRICE_SCALE_MISMATCH_BPS_THRESHOLD
        index_extreme = pd.to_numeric(g["index_spread_bps_okx_minus_binance"], errors="coerce").abs() > PRICE_SCALE_MISMATCH_BPS_THRESHOLD
        rows.append(
            {
                "symbol": symbol,
                "rows": int(len(g)),
                "mark_extreme_rows": int(mark_extreme.sum()),
                "index_extreme_rows": int(index_extreme.sum()),
                "mark_extreme_share": float(mark_extreme.mean()),
                "index_extreme_share": float(index_extreme.mean()),
                "mark_basis_min": float(g["mark_basis_bps_okx_minus_binance"].min()),
                "mark_basis_max": float(g["mark_basis_bps_okx_minus_binance"].max()),
                "index_spread_min": float(g["index_spread_bps_okx_minus_binance"].min()),
                "index_spread_max": float(g["index_spread_bps_okx_minus_binance"].max()),
                "price_scale_status": "quarantine_price_scale_mismatch" if bool((mark_extreme | index_extreme).any()) else "clean",
            }
        )
    return pd.DataFrame(rows).sort_values(["price_scale_status", "mark_extreme_share", "index_extreme_share"], ascending=[False, False, False])


def contract_audit(field_contract: dict[str, Any]) -> pd.DataFrame:
    source = field_contract.get("source_contract", {})
    rows = [
        {"item": "dataset", "value": field_contract.get("dataset", "")},
        {"item": "decision", "value": field_contract.get("decision", "")},
        {"item": "okx_source", "value": source.get("okx", "")},
        {"item": "binance_source", "value": source.get("binance", "")},
        {"item": "join_rule", "value": source.get("join", "")},
        {"item": "feature_available_time", "value": source.get("feature_available_time", "")},
        {"item": "recommended_stress_execution_time", "value": source.get("recommended_stress_execution_time", "")},
        {"item": "not_authorized", "value": ";".join(source.get("not_authorized", []))},
    ]
    return pd.DataFrame(rows)


def build_report(
    summary: dict[str, Any],
    field_q: pd.DataFrame,
    symbol_q: pd.DataFrame,
    timing: pd.DataFrame,
    price_scale: pd.DataFrame,
    contract: pd.DataFrame,
    manifest_summary: pd.DataFrame,
    coverage_summary: pd.DataFrame,
) -> None:
    report = f"""# CRYPTO A7AP-0 OKX/Binance Cross-Exchange Overlay Acceptance

Generated: {summary["generated_at"]}

## Decision

```text
{summary["decision"]}
```

This audit validates the OKX/Binance recent 30d cross-exchange overlay as a short overlap diagnostic dataset. It does not authorize historical alpha proof.

## Summary

```json
{json.dumps(summary, indent=2, sort_keys=True)}
```

## Field Quality

{md_table(field_q, max_rows=80)}

## Timing Audit

{md_table(timing)}

## Price Scale / Contract Unit Audit

{md_table(price_scale[price_scale["price_scale_status"] != "clean"], max_rows=80)}

## Symbol Quality Sample

{md_table(symbol_q.head(40), max_rows=40)}

## Manifest Summary

{md_table(manifest_summary)}

## Coverage Summary

{md_table(coverage_summary)}

## Contract Audit

{md_table(contract)}

## Boundary

```text
AUTHORIZED:
  A7AP-1 small diagnostic field-family smoke on overlap rows only

NOT AUTHORIZED:
  historical alpha proof
  broad search
  shadow / paper / live

PRIMARY CAVEAT:
  OKX 30d recent data only overlaps the accepted Binance panel from 2026-04-26 17:00 UTC to 2026-04-30 23:00 UTC.
```
"""
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = pd.read_csv(MANIFEST_PATH)
    coverage = pd.read_csv(COVERAGE_PATH)
    contract = read_json(FIELD_CONTRACT_PATH)
    panel = load_panel()

    blockers: list[str] = []
    warnings: list[str] = []
    if panel.empty:
        blockers.append("empty_cross_exchange_panel")
    if int(panel.duplicated(["symbol", "timestamp"]).sum()):
        blockers.append("duplicate_symbol_timestamp_rows")
    numeric_inf = 0
    for col in NUMERIC_CHECK_COLUMNS:
        if col in panel.columns:
            numeric_inf += int(np.isinf(pd.to_numeric(panel[col], errors="coerce").dropna()).sum())
    if numeric_inf:
        blockers.append("inf_numeric_cells")
    if not bool((panel["feature_available_time"] == panel["timestamp"] + pd.Timedelta(hours=1)).all()):
        blockers.append("feature_time_alignment_fail")
    if not bool((panel["recommended_stress_execution_time"] == panel["timestamp"] + pd.Timedelta(hours=2)).all()):
        blockers.append("stress_execution_alignment_fail")
    overlap_hours = int(panel["timestamp"].nunique()) if not panel.empty else 0
    if overlap_hours < 100:
        warnings.append("short_overlap_window_under_100_unique_hours")
    else:
        warnings.append("short_overlap_window_diagnostic_only")
    if float(panel["okx_funding_rate"].notna().mean()) < 0.95:
        warnings.append("okx_funding_hourly_non_null_rate_below_95pct_due_event_asof")
    if float(panel["binance_funding_rate"].notna().mean()) < 0.50:
        warnings.append("binance_funding_sparse_in_overlap")

    field_q = field_quality(panel)
    symbol_q = symbol_quality(panel)
    timing = timing_audit(panel)
    price_scale = price_scale_audit(panel)
    contract_df = contract_audit(contract)
    manifest_summary = manifest.groupby("status", dropna=False).size().reset_index(name="symbols")
    coverage_summary = coverage.groupby("decision", dropna=False).size().reset_index(name="symbols")
    price_scale_quarantine_symbols = price_scale.loc[price_scale["price_scale_status"] != "clean", "symbol"].tolist()
    if price_scale_quarantine_symbols:
        warnings.append("price_scale_mismatch_symbols_quarantined")

    summary = {
        "generated_at": utc_now(),
        "decision": "PASS_A7AP0_CROSS_EXCHANGE_OVERLAY_ACCEPTED_WITH_PRICE_SCALE_QUARANTINE",
        "gold_root": str(GOLD_ROOT),
        "manifest": str(MANIFEST_PATH),
        "coverage": str(COVERAGE_PATH),
        "field_contract": str(FIELD_CONTRACT_PATH),
        "source_report": str(SOURCE_REPORT_PATH),
        "symbols": int(panel["symbol"].nunique()) if not panel.empty else 0,
        "rows": int(len(panel)),
        "timestamp_min": str(panel["timestamp"].min()) if not panel.empty else "",
        "timestamp_max": str(panel["timestamp"].max()) if not panel.empty else "",
        "unique_hours": overlap_hours,
        "duplicate_symbol_timestamp_rows": int(panel.duplicated(["symbol", "timestamp"]).sum()) if not panel.empty else 0,
        "numeric_inf_cells": int(numeric_inf),
        "okx_mark_non_null_rate": float(panel["okx_mark_close"].notna().mean()) if not panel.empty else 0.0,
        "okx_index_non_null_rate": float(panel["okx_index_close"].notna().mean()) if not panel.empty else 0.0,
        "okx_funding_non_null_rate": float(panel["okx_funding_rate"].notna().mean()) if not panel.empty else 0.0,
        "binance_funding_non_null_rate": float(panel["binance_funding_rate"].notna().mean()) if not panel.empty else 0.0,
        "price_scale_quarantine_symbols": price_scale_quarantine_symbols,
        "price_scale_quarantine_symbol_count": int(len(price_scale_quarantine_symbols)),
        "clean_symbols_after_price_scale_quarantine": int(panel["symbol"].nunique() - len(price_scale_quarantine_symbols)) if not panel.empty else 0,
        "executes_acceptance_audit": True,
        "executes_search": False,
        "executes_replay": False,
        "authorizes_a7ap1_small_diagnostic_smoke": True,
        "authorizes_broad_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "blockers": blockers,
        "warnings": warnings,
    }
    if blockers:
        summary["decision"] = "HOLD_A7AP0_CROSS_EXCHANGE_OVERLAY_ACCEPTANCE_BLOCKED"
        summary["authorizes_a7ap1_small_diagnostic_smoke"] = False

    write_json(OUT_DIR / "a7ap0_manifest.json", summary)
    field_q.to_csv(OUT_DIR / "a7ap0_field_quality.csv", index=False)
    symbol_q.to_csv(OUT_DIR / "a7ap0_symbol_quality.csv", index=False)
    timing.to_csv(OUT_DIR / "a7ap0_timing_audit.csv", index=False)
    price_scale.to_csv(OUT_DIR / "a7ap0_price_scale_audit.csv", index=False)
    contract_df.to_csv(OUT_DIR / "a7ap0_field_contract_audit.csv", index=False)
    manifest_summary.to_csv(OUT_DIR / "a7ap0_manifest_summary.csv", index=False)
    coverage_summary.to_csv(OUT_DIR / "a7ap0_coverage_summary.csv", index=False)

    build_report(summary, field_q, symbol_q, timing, price_scale, contract_df, manifest_summary, coverage_summary)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
