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

PANEL_PATH = DATA_ROOT / "gold" / "features" / "binance_core12_all_features_metrics_market_structure_aggtrades_v1_20260524.parquet"
HANDOFF_REPORT = DATA_ROOT / "reports" / "CRYPTO_CORE12_AGGTRADES_FINAL_HANDOFF_20260524.md"
MERGE_REPORT = DATA_ROOT / "reports" / "crypto_core12_1h_with_aggtrades_features_v1_20260524_091100.json"
AGG_FEATURE_REPORT = DATA_ROOT / "reports" / "aggtrades_enhanced_features_v1_20260524_090935.json"
AGG_FEATURE_ROOT = DATA_ROOT / "gold" / "features" / "aggtrades_enhanced_features_v1"
HOURLY_ROOT = DATA_ROOT / "gold" / "microstructure" / "aggtrades_1h_flow_enhanced_v1"
CHECKSUM_ROOT = DATA_ROOT / "metadata" / "checksums" / "binance_vision_aggtrades_package_a_raw" / "futures" / "um" / "monthly" / "aggTrades"

OUT_DIR = ROOT / "runtime" / "a7ah0_core12_aggtrades_final_handoff_audit"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7AH0_CORE12_AGGTRADES_FINAL_HANDOFF_AUDIT_20260524.md"

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

EXPECTED_PANEL_ROWS = 815_818
EXPECTED_PANEL_COLUMNS = 654
EXPECTED_AGG_FEATURE_ROWS_REPORT = 245_088
EXPECTED_AGG_SYMBOL_MONTH_REPORT = 336

REQUIRED_MERGED_AGG_FIELDS = [
    "agg_features_available",
    "agg_feature_schema",
    "agg_trade_count",
    "agg_underlying_trade_count",
    "agg_notional",
    "agg_buy_notional",
    "agg_sell_notional",
    "agg_signed_aggressor_notional",
    "agg_volume_imbalance",
    "agg_buy_sell_notional_ratio",
    "agg_large_notional_ratio_100k_plus",
]

DERIVED_AGG_FIELDS_NOT_REQUIRED_IN_FINAL_PANEL = [
    "agg_flow_imbalance_notional_24h",
    "agg_signed_flow_z_24h",
    "agg_notional_accel_4h_vs_24h",
    "agg_flow_accel_4h_vs_24h",
    "agg_cross_symbol_notional_share",
    "agg_cross_symbol_signed_flow_share",
    "agg_cross_symbol_large_notional_share",
]

A7U0R_TRACE = ROOT / "runtime" / "a7u0r_source_trace_audit" / "a7u0r_symbol_month_source_trace.csv"

NON_NEGATIVE_FIELDS = [
    "agg_trade_count",
    "agg_underlying_trade_count",
    "agg_quantity",
    "agg_notional",
    "agg_buy_notional",
    "agg_sell_notional",
    "agg_large_notional_100k_plus",
    "agg_large_notional_ratio_100k_plus",
    "agg_cross_symbol_notional_share",
    "agg_cross_symbol_large_notional_share",
]

BOUNDED_FIELDS = {
    "agg_volume_imbalance": (-1.0, 1.0),
    "agg_flow_imbalance_notional": (-1.0, 1.0),
    "agg_flow_imbalance_notional_24h": (-1.0, 1.0),
    "agg_buy_notional_share": (0.0, 1.0),
    "agg_sell_notional_share": (0.0, 1.0),
    "agg_large_notional_ratio_100k_plus": (0.0, 1.0),
    "agg_large_notional_share_4h": (0.0, 1.0),
    "agg_large_notional_share_24h": (0.0, 1.0),
    "agg_cross_symbol_notional_share": (0.0, 1.0),
    "agg_cross_symbol_large_notional_share": (0.0, 1.0),
}


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


def month_range(start: str = "2024-01", end: str = "2026-04") -> list[str]:
    return [ts.strftime("%Y-%m") for ts in pd.period_range(start=start, end=end, freq="M").to_timestamp()]


def schema_summary() -> tuple[pq.Schema, pq.FileMetaData, pd.DataFrame]:
    schema = pq.read_schema(PANEL_PATH)
    meta = pq.ParquetFile(PANEL_PATH).metadata
    rows = []
    for name, typ in zip(schema.names, schema.types):
        rows.append({"column": name, "type": str(typ), "is_agg_field": name.startswith("agg_")})
    return schema, meta, pd.DataFrame(rows)


def load_validation_columns(schema_names: set[str]) -> pd.DataFrame:
    cols = ["symbol", "timestamp"] + [c for c in REQUIRED_MERGED_AGG_FIELDS + NON_NEGATIVE_FIELDS + list(BOUNDED_FIELDS) if c in schema_names]
    cols = sorted(set(cols))
    df = pd.read_parquet(PANEL_PATH, columns=cols, engine="pyarrow")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    return df


def key_audit(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    symbols = sorted(df["symbol"].dropna().unique().tolist())
    ts_min = df["timestamp"].min()
    ts_max = df["timestamp"].max()
    full_hours = pd.date_range(ts_min, ts_max, freq="h", tz="UTC")
    rows = []
    missing_rows = []
    for symbol, part in df.groupby("symbol", observed=True):
        timestamps = pd.DatetimeIndex(part["timestamp"].dropna().sort_values().unique())
        missing = full_hours.difference(timestamps)
        rows.append(
            {
                "symbol": symbol,
                "rows": int(len(part)),
                "timestamp_min": str(part["timestamp"].min()),
                "timestamp_max": str(part["timestamp"].max()),
                "duplicate_keys": int(part.duplicated(["symbol", "timestamp"]).sum()),
                "missing_hours_vs_panel_range": int(len(missing)),
            }
        )
        for ts in missing[:20]:
            missing_rows.append({"symbol": symbol, "missing_timestamp": str(ts)})
    return pd.DataFrame(rows), pd.DataFrame(missing_rows)


def agg_coverage(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    flag = pd.to_numeric(df.get("agg_features_available", pd.Series(index=df.index, data=np.nan)), errors="coerce").fillna(0.0)
    df2 = df.copy()
    df2["_agg_available"] = flag > 0
    for symbol, part in df2.groupby("symbol", observed=True):
        available = part["_agg_available"]
        first = part.loc[available, "timestamp"].min() if available.any() else pd.NaT
        last = part.loc[available, "timestamp"].max() if available.any() else pd.NaT
        rows.append(
            {
                "symbol": symbol,
                "is_core12": symbol in CORE12,
                "rows": int(len(part)),
                "agg_available_rows": int(available.sum()),
                "agg_coverage": float(available.mean()),
                "agg_first_timestamp": str(first) if pd.notna(first) else "",
                "agg_last_timestamp": str(last) if pd.notna(last) else "",
                "may_2026_agg_rows": int((available & part["timestamp"].between(pd.Timestamp("2026-05-01", tz="UTC"), pd.Timestamp("2026-05-31 23:00", tz="UTC"))).sum()),
            }
        )
    return pd.DataFrame(rows).sort_values(["is_core12", "symbol"], ascending=[False, True])


def monthly_coverage(df: pd.DataFrame) -> pd.DataFrame:
    flag = pd.to_numeric(df.get("agg_features_available", pd.Series(index=df.index, data=np.nan)), errors="coerce").fillna(0.0).gt(0)
    part = df[df["symbol"].isin(CORE12)].copy()
    part["_agg_available"] = flag.loc[part.index].values
    part["month"] = part["timestamp"].dt.strftime("%Y-%m")
    rows = []
    for (symbol, month), g in part.groupby(["symbol", "month"], observed=True):
        rows.append(
            {
                "symbol": symbol,
                "month": month,
                "rows": int(len(g)),
                "agg_available_rows": int(g["_agg_available"].sum()),
                "agg_coverage": float(g["_agg_available"].mean()),
            }
        )
    return pd.DataFrame(rows).sort_values(["symbol", "month"])


def agg_partition_audit() -> pd.DataFrame:
    expected_months = set(month_range())
    rows = []
    for symbol in CORE12:
        root = AGG_FEATURE_ROOT / f"symbol={symbol}"
        months = []
        if root.exists():
            for child in root.glob("month=*"):
                if child.is_dir() and (child / "part.parquet").exists():
                    months.append(child.name.split("=", 1)[1])
        month_set = set(months)
        rows.append(
            {
                "symbol": symbol,
                "partition_months": len(month_set),
                "has_all_2024_01_to_2026_04": expected_months.issubset(month_set),
                "extra_months": ";".join(sorted(month_set - expected_months)),
                "missing_months": ";".join(sorted(expected_months - month_set)),
            }
        )
    return pd.DataFrame(rows)


def hourly_partition_audit() -> pd.DataFrame:
    expected_months = set(month_range())
    rows = []
    for symbol in CORE12:
        root = HOURLY_ROOT / f"symbol={symbol}"
        months = []
        if root.exists():
            for child in root.glob("month=*"):
                if child.is_dir() and (child / "part.parquet").exists():
                    months.append(child.name.split("=", 1)[1])
        month_set = set(months)
        rows.append(
            {
                "symbol": symbol,
                "hourly_months": len(month_set),
                "has_all_2024_01_to_2026_04": expected_months.issubset(month_set),
                "extra_months": ";".join(sorted(month_set - expected_months)),
                "missing_months": ";".join(sorted(expected_months - month_set)),
            }
        )
    return pd.DataFrame(rows)


def checksum_count_audit() -> pd.DataFrame:
    expected_months = set(month_range())
    rows = []
    for symbol in CORE12:
        root = CHECKSUM_ROOT / symbol
        months = set()
        if root.exists():
            for path in root.glob("*.CHECKSUM"):
                # Example: ADAUSDT-aggTrades-2024-01.zip.CHECKSUM
                stem = path.name.replace(".zip.CHECKSUM", "")
                month = stem.split("-")[-2] + "-" + stem.split("-")[-1] if "-" in stem else ""
                if len(month) == 7:
                    months.add(month)
        rows.append(
            {
                "symbol": symbol,
                "checksum_files_2024_01_2026_04": len(months & expected_months),
                "has_all_2024_01_to_2026_04": expected_months.issubset(months),
                "extra_months": ";".join(sorted(months - expected_months)),
                "missing_months": ";".join(sorted(expected_months - months)),
            }
        )
    return pd.DataFrame(rows)


def source_trace_audit(checksum_counts: pd.DataFrame) -> pd.DataFrame:
    rows = []
    core3_trace = pd.DataFrame()
    if A7U0R_TRACE.exists():
        core3_trace = pd.read_csv(A7U0R_TRACE)
    for symbol in CORE12:
        if symbol in {"BTCUSDT", "ETHUSDT", "SOLUSDT"} and not core3_trace.empty:
            part = core3_trace[core3_trace["symbol"].eq(symbol)]
            ready_col = "status" if "status" in part.columns else None
            ready = int((part[ready_col].astype(str).str.contains("ready|ok|checksum", case=False, regex=True)).sum()) if ready_col else len(part)
            rows.append(
                {
                    "symbol": symbol,
                    "source_trace_method": "A7U0R_source_trace_audit",
                    "trace_rows": int(len(part)),
                    "ready_rows": ready,
                    "expected_rows": 29,
                    "source_trace_complete": int(len(part)) >= 29,
                    "note": "core3 source trace closed by A7U-0R; checksum files may live outside package_a path",
                }
            )
        else:
            ck = checksum_counts[checksum_counts["symbol"].eq(symbol)]
            count = int(ck["checksum_files_2024_01_2026_04"].iloc[0]) if not ck.empty else 0
            rows.append(
                {
                    "symbol": symbol,
                    "source_trace_method": "package_a_checksum_files",
                    "trace_rows": count,
                    "ready_rows": count,
                    "expected_rows": 28,
                    "source_trace_complete": count >= 28,
                    "note": "rem9 monthly 2024-01..2026-04 checksum files present",
                }
            )
    return pd.DataFrame(rows)


def numeric_quality(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    num_cols = [c for c in df.columns if c not in {"symbol", "timestamp", "agg_feature_schema"}]
    rows = []
    bound_rows = []
    for col in num_cols:
        s = pd.to_numeric(df[col], errors="coerce")
        finite = np.isfinite(s.to_numpy(dtype=float, na_value=np.nan))
        rows.append(
            {
                "field_name": col,
                "non_null_rate": float(s.notna().mean()),
                "nan_count": int(s.isna().sum()),
                "inf_count": int(np.isinf(s.to_numpy(dtype=float, na_value=np.nan)).sum()),
                "negative_count": int((s < 0).sum()) if col in NON_NEGATIVE_FIELDS else None,
                "min": float(s.min()) if s.notna().any() and math.isfinite(float(s.min())) else None,
                "max": float(s.max()) if s.notna().any() and math.isfinite(float(s.max())) else None,
            }
        )
        if col in BOUNDED_FIELDS:
            lo, hi = BOUNDED_FIELDS[col]
            violations = int(((s < lo) | (s > hi)).sum())
            bound_rows.append({"field_name": col, "lower": lo, "upper": hi, "violation_count": violations})
    return pd.DataFrame(rows), pd.DataFrame(bound_rows)


def report_consistency(meta: pq.FileMetaData, schema: pq.Schema, merge_report: dict[str, Any], agg_report: dict[str, Any]) -> pd.DataFrame:
    rows = []

    def add(metric: str, observed: Any, expected: Any, source: str) -> None:
        rows.append(
            {
                "metric": metric,
                "observed": observed,
                "expected_or_reported": expected,
                "source": source,
                "matches": str(observed) == str(expected),
            }
        )

    add("final_panel_rows", meta.num_rows, EXPECTED_PANEL_ROWS, "handoff_expected")
    add("final_panel_columns", len(schema.names), EXPECTED_PANEL_COLUMNS, "handoff_expected")
    add("merge_report_output_rows", meta.num_rows, merge_report.get("output_rows"), "merge_json")
    add("merge_report_output_columns", len(schema.names), merge_report.get("output_columns"), "merge_json")
    add("agg_feature_report_rows", agg_report.get("rows"), EXPECTED_AGG_FEATURE_ROWS_REPORT, "agg_feature_json_vs_handoff")
    add("agg_feature_report_symbol_month_count", agg_report.get("symbol_month_count"), EXPECTED_AGG_SYMBOL_MONTH_REPORT, "agg_feature_json_vs_handoff")
    add("merge_report_input_agg_rows", merge_report.get("agg_rows"), agg_report.get("rows"), "merge_json_vs_agg_feature_json")
    add("merge_report_input_agg_symbol_month_count", merge_report.get("agg_symbol_month_count"), agg_report.get("symbol_month_count"), "merge_json_vs_agg_feature_json")
    return pd.DataFrame(rows)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    now = utc_now()

    merge_report = read_json(MERGE_REPORT)
    agg_report = read_json(AGG_FEATURE_REPORT)
    schema, meta, schema_df = schema_summary()
    schema_names = set(schema.names)
    df = load_validation_columns(schema_names)

    key_by_symbol, missing_sample = key_audit(df)
    coverage = agg_coverage(df)
    monthly = monthly_coverage(df)
    agg_parts = agg_partition_audit()
    hourly_parts = hourly_partition_audit()
    checksum_counts = checksum_count_audit()
    source_trace = source_trace_audit(checksum_counts)
    numeric, bounds = numeric_quality(df)
    consistency = report_consistency(meta, schema, merge_report, agg_report)

    core12_cov = coverage[coverage["is_core12"]]
    non_core12_cov = coverage[~coverage["is_core12"]]
    blockers: list[str] = []
    warnings: list[str] = []
    if not PANEL_PATH.exists():
        blockers.append("final_panel_missing")
    if meta.num_rows != EXPECTED_PANEL_ROWS:
        blockers.append("final_panel_row_count_mismatch")
    if len(schema.names) != EXPECTED_PANEL_COLUMNS:
        blockers.append("final_panel_column_count_mismatch")
    if int(key_by_symbol["duplicate_keys"].sum()) > 0:
        blockers.append("duplicate_symbol_timestamp_keys")
    missing_required = [field for field in REQUIRED_MERGED_AGG_FIELDS if field not in schema_names]
    if missing_required:
        blockers.append("required_agg_fields_missing")
    missing_derived = [field for field in DERIVED_AGG_FIELDS_NOT_REQUIRED_IN_FINAL_PANEL if field not in schema_names]
    if missing_derived:
        warnings.append("derived_agg_feature_fields_not_merged_into_final_panel_use_feature_root_or_rebuild_if_needed")
    if int(bounds["violation_count"].sum()) > 0:
        blockers.append("bounded_field_range_violation")
    neg_bad = numeric[(numeric["negative_count"].fillna(0) > 0)]
    if not neg_bad.empty:
        blockers.append("non_negative_field_has_negative_values")
    if int(non_core12_cov["agg_available_rows"].sum()) > 0:
        blockers.append("non_core12_has_agg_features")
    if bool((core12_cov["agg_coverage"] < 0.95).any()):
        blockers.append("core12_agg_coverage_below_95pct")
    if not bool(agg_parts["has_all_2024_01_to_2026_04"].all()):
        blockers.append("agg_feature_partition_missing_expected_month")
    if not bool(hourly_parts["has_all_2024_01_to_2026_04"].all()):
        blockers.append("hourly_enhanced_partition_missing_expected_month")
    if not bool(source_trace["source_trace_complete"].all()):
        blockers.append("source_trace_incomplete_for_some_core12_symbols")
    if bool((coverage[coverage["is_core12"]]["may_2026_agg_rows"] > 0).any()):
        warnings.append("some_core12_symbols_have_2026_05_agg_rows; handoff says monthly May unavailable so treat May agg as forward/current-month caveat")
    if not bool(consistency["matches"].all()):
        warnings.append("handoff_report_and_build_json_have_non_blocking_metric_discrepancies")
    if int(key_by_symbol["missing_hours_vs_panel_range"].sum()) > 0:
        warnings.append("panel_has_symbol_timestamp_gaps_relative_to_global_panel_range")

    decision = "PASS_A7AH0_CORE12_AGGTRADES_FINAL_HANDOFF_ACCEPTED" if not blockers else "HOLD_A7AH0_CORE12_AGGTRADES_FINAL_HANDOFF_BLOCKED"
    auth = {
        "decision": decision,
        "blockers": blockers,
        "warnings": warnings,
        "authorizes_a7ai0_core12_aggtrades_experiment_contract": decision.startswith("PASS_"),
        "authorizes_direct_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "may_policy": "2026-05 aggTrades monthly history is not claimed; any May agg coverage is caveated and cannot be ranking/tuning proof",
    }
    manifest = {
        "generated_at": now,
        "decision": decision,
        "panel_path": str(PANEL_PATH),
        "handoff_report": str(HANDOFF_REPORT),
        "panel_file_size_bytes": PANEL_PATH.stat().st_size if PANEL_PATH.exists() else None,
        "panel_rows": meta.num_rows,
        "panel_columns": len(schema.names),
        "symbols": int(df["symbol"].nunique()),
        "timestamp_min": str(df["timestamp"].min()),
        "timestamp_max": str(df["timestamp"].max()),
        "duplicate_keys": int(df.duplicated(["symbol", "timestamp"]).sum()),
        "core12_min_agg_coverage": float(core12_cov["agg_coverage"].min()),
        "core12_max_agg_coverage": float(core12_cov["agg_coverage"].max()),
        "non_core12_agg_rows": int(non_core12_cov["agg_available_rows"].sum()),
        "executes_replay": False,
        "executes_search": False,
        "report": str(REPORT_PATH),
        "output_dir": str(OUT_DIR),
    }

    schema_df.to_csv(OUT_DIR / "a7ah0_schema_audit.csv", index=False)
    key_by_symbol.to_csv(OUT_DIR / "a7ah0_key_coverage_by_symbol.csv", index=False)
    missing_sample.to_csv(OUT_DIR / "a7ah0_missing_timestamp_sample.csv", index=False)
    coverage.to_csv(OUT_DIR / "a7ah0_agg_coverage_by_symbol.csv", index=False)
    monthly.to_csv(OUT_DIR / "a7ah0_agg_monthly_coverage.csv", index=False)
    agg_parts.to_csv(OUT_DIR / "a7ah0_agg_feature_partition_audit.csv", index=False)
    hourly_parts.to_csv(OUT_DIR / "a7ah0_hourly_enhanced_partition_audit.csv", index=False)
    checksum_counts.to_csv(OUT_DIR / "a7ah0_checksum_count_audit.csv", index=False)
    source_trace.to_csv(OUT_DIR / "a7ah0_source_trace_closure_audit.csv", index=False)
    numeric.to_csv(OUT_DIR / "a7ah0_numeric_quality.csv", index=False)
    bounds.to_csv(OUT_DIR / "a7ah0_bounded_field_audit.csv", index=False)
    consistency.to_csv(OUT_DIR / "a7ah0_report_consistency_audit.csv", index=False)
    write_json(OUT_DIR / "a7ah0_authorization_matrix.json", auth)
    write_json(OUT_DIR / "a7ah0_manifest.json", manifest)

    report = f"""# CRYPTO A7AH-0 Core12 aggTrades Final Handoff Audit

Generated: {now}

## Decision

```text
{decision}
```

This stage validates the final core12 aggTrades handoff data. It does not run replay and does not run search.

## Summary

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Authorization

```json
{json.dumps(auth, indent=2, sort_keys=True)}
```

## Report Consistency Audit

{md_table(consistency)}

## Key Coverage By Symbol

{md_table(key_by_symbol)}

## aggTrades Coverage By Symbol

{md_table(coverage)}

## agg Feature Partition Audit

{md_table(agg_parts)}

## Hourly Enhanced Partition Audit

{md_table(hourly_parts)}

## Checksum Count Audit

{md_table(checksum_counts)}

## Source Trace Closure Audit

{md_table(source_trace)}

## Bounded Field Audit

{md_table(bounds)}

## Numeric Quality Sample

{md_table(numeric.sort_values(["inf_count", "negative_count", "nan_count"], ascending=False).head(40))}

## Boundary

- This is a data-line acceptance audit, not alpha evidence.
- The final parquet is a core39-sized panel with aggTrades fields populated for core12 only.
- 2026-05 monthly aggTrades history is not claimed by this handoff.
- Any experiment must use selected fields and an explicit time-availability contract.
- No direct formula search, large search, alpha proof, shadow, paper, or live is authorized.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
