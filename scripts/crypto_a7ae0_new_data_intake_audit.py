from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(r"G:\AlphaFactory_CryptoData")

CORE39_MARKET = DATA_ROOT / "gold" / "features" / "binance_core39_market_structure_1h_features_v1.parquet"
CORE39_ALL = DATA_ROOT / "gold" / "features" / "binance_core39_all_features_metrics_v3_market_structure_v1.parquet"
CORE3_AGG = DATA_ROOT / "gold" / "features" / "binance_core3_all_features_metrics_market_structure_aggtrades_v1.parquet"

CORE39_MARKET_REPORT = DATA_ROOT / "reports" / "core39_market_structure_download_build_core39_20260522.json"
CORE39_ALL_REPORT = DATA_ROOT / "reports" / "core39_all_features_metrics_v3_market_structure_v1_report_20260522.json"
CORE39_MARKET_QUALITY = DATA_ROOT / "alphafactory_crypto" / "runtime" / "market_structure_core39" / "core39_all_features_market_added_quality.csv"
CORE3_AGG_COVERAGE = DATA_ROOT / "alphafactory_crypto" / "runtime" / "aggtrades_core3" / "core3_aggtrades_coverage_in_all_features_v1.csv"
CORE3_AGG_CATALOG = DATA_ROOT / "alphafactory_crypto" / "runtime" / "aggtrades_core3" / "core3_aggtrades_field_catalog_v1.csv"
AGG_RAW_MANIFEST = DATA_ROOT / "manifests" / "aggtrades_raw_only_2024-01_2026-05_core12_rem9_20260522.csv"

OUT_DIR = ROOT / "runtime" / "a7ae0_new_data_intake_audit"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7AE0_NEW_DATA_INTAKE_AUDIT_20260522.md"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 60) -> str:
    if df.empty:
        return "`<empty>`"
    try:
        return df.head(max_rows).to_markdown(index=False)
    except Exception:
        return "```\n" + df.head(max_rows).to_string(index=False) + "\n```"


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def parquet_summary(path: Path, dataset_id: str) -> dict[str, Any]:
    if not path.exists():
        return {
            "dataset_id": dataset_id,
            "path": str(path),
            "exists": False,
        }
    schema = pq.read_schema(path)
    df = pd.read_parquet(path, columns=[c for c in ["symbol", "timestamp"] if c in schema.names], engine="pyarrow")
    out: dict[str, Any] = {
        "dataset_id": dataset_id,
        "path": str(path),
        "exists": True,
        "size_mb": round(path.stat().st_size / 1024 / 1024, 3),
        "rows": int(len(df)),
        "columns": int(len(schema.names)),
        "symbols": int(df["symbol"].nunique()) if "symbol" in df.columns else None,
        "timestamp_min": str(df["timestamp"].min()) if "timestamp" in df.columns else None,
        "timestamp_max": str(df["timestamp"].max()) if "timestamp" in df.columns else None,
        "duplicate_symbol_timestamp": int(df.duplicated(["symbol", "timestamp"]).sum()) if {"symbol", "timestamp"}.issubset(df.columns) else None,
        "sample_symbols": ";".join(sorted(df["symbol"].dropna().unique().tolist())[:80]) if "symbol" in df.columns else "",
    }
    names = schema.names
    out["agg_columns"] = int(sum(c.startswith("agg_") for c in names))
    out["market_structure_columns"] = int(
        sum(
            c.startswith(("mark_price_", "index_price_", "premium_index_"))
            or c
            in {
                "funding_rate",
                "funding_time",
                "funding_mark_price",
                "mark_index_basis",
                "mark_index_basis_bps",
                "premium_index_bps",
                "funding_x_basis",
                "premium_minus_funding_bps",
            }
            for c in names
        )
    )
    out["known_independent_metric_source_fields"] = int(
        sum(
            c
            in {
                "open_interest",
                "open_interest_value",
                "global_long_short_account_ratio",
                "top_long_short_account_ratio",
                "top_long_short_position_ratio",
                "taker_buy_sell_volume_ratio",
            }
            for c in names
        )
    )
    return out


def summarize_quality() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    market_quality = pd.read_csv(CORE39_MARKET_QUALITY) if CORE39_MARKET_QUALITY.exists() else pd.DataFrame()
    if not market_quality.empty:
        market_quality = market_quality.sort_values("missing_rate", ascending=False)
    agg_cov = pd.read_csv(CORE3_AGG_COVERAGE) if CORE3_AGG_COVERAGE.exists() else pd.DataFrame()
    agg_catalog = pd.read_csv(CORE3_AGG_CATALOG) if CORE3_AGG_CATALOG.exists() else pd.DataFrame()
    return market_quality, agg_cov, agg_catalog


def raw_agg_manifest_summary() -> pd.DataFrame:
    if not AGG_RAW_MANIFEST.exists():
        return pd.DataFrame(
            [
                {
                    "manifest": str(AGG_RAW_MANIFEST),
                    "status": "missing",
                    "symbol": "",
                    "rows": 0,
                }
            ]
        )
    df = pd.read_csv(AGG_RAW_MANIFEST)
    symbol_col = "symbol" if "symbol" in df.columns else None
    checksum_col = next((c for c in df.columns if "checksum" in c.lower() and ("ok" in c.lower() or "match" in c.lower())), None)
    rows = []
    if symbol_col:
        for symbol, part in df.groupby(symbol_col):
            rows.append(
                {
                    "manifest": str(AGG_RAW_MANIFEST),
                    "status": "partial_manifest_seen",
                    "symbol": symbol,
                    "rows": int(len(part)),
                    "checksum_ok_count": int(part[checksum_col].astype(str).str.lower().isin(["true", "ok", "1"]).sum()) if checksum_col else None,
                    "first_download_time": str(part["download_time"].min()) if "download_time" in part.columns else "",
                    "last_download_time": str(part["download_time"].max()) if "download_time" in part.columns else "",
                }
            )
    else:
        rows.append({"manifest": str(AGG_RAW_MANIFEST), "status": "partial_manifest_seen_no_symbol_col", "symbol": "", "rows": int(len(df))})
    return pd.DataFrame(rows)


def running_download_processes() -> pd.DataFrame:
    try:
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'download_aggtrades_raw_only|core39|market_structure|aggtrades' } | Select-Object ProcessId,Name,CommandLine | ConvertTo-Json -Depth 3",
            ],
            capture_output=True,
            text=True,
            timeout=20,
        )
    except Exception as exc:
        return pd.DataFrame([{"process_id": None, "name": "process_scan_failed", "command_line": repr(exc)}])
    text = result.stdout.strip()
    if not text:
        return pd.DataFrame(columns=["process_id", "name", "command_line"])
    try:
        payload = json.loads(text)
    except Exception:
        return pd.DataFrame([{"process_id": None, "name": "process_scan_parse_failed", "command_line": text[:500]}])
    if isinstance(payload, dict):
        payload = [payload]
    rows = []
    for item in payload:
        rows.append(
            {
                "process_id": item.get("ProcessId"),
                "name": item.get("Name"),
                "command_line": item.get("CommandLine"),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    now = utc_now()

    summaries = pd.DataFrame(
        [
            parquet_summary(CORE39_MARKET, "core39_market_structure_1h"),
            parquet_summary(CORE39_ALL, "core39_all_features_metrics_v3_market_structure"),
            parquet_summary(CORE3_AGG, "core3_all_features_with_aggtrades"),
        ]
    )
    market_quality, agg_cov, agg_catalog = summarize_quality()
    raw_agg = raw_agg_manifest_summary()
    processes = running_download_processes()
    market_report = read_json(CORE39_MARKET_REPORT)
    all_report = read_json(CORE39_ALL_REPORT)

    independent_source_contract = pd.DataFrame(
        [
            {
                "source_family": "binance_metrics_history",
                "independent_source_fields": "open_interest;open_interest_value;global_long_short_account_ratio;top_long_short_account_ratio;top_long_short_position_ratio;taker_buy_sell_volume_ratio",
                "historical_backfill": True,
                "experiment_status": "usable_with_vendor_5m_warnings_and_field_selection",
            },
            {
                "source_family": "market_structure_rest_history",
                "independent_source_fields": "premiumIndexKlines;markPriceKlines;indexPriceKlines;fundingRate",
                "historical_backfill": True,
                "experiment_status": "usable_for_field_selection; funding fields must preserve asof semantics",
            },
            {
                "source_family": "aggtrades_order_flow_core3",
                "independent_source_fields": "aggTrades order-flow buckets, signed aggressor flow, large trade buckets",
                "historical_backfill": True,
                "experiment_status": "core3_only; do not project to core39/core48",
            },
            {
                "source_family": "aggtrades_raw_core12_rem9",
                "independent_source_fields": "raw aggTrades zip/checksum",
                "historical_backfill": False,
                "experiment_status": "in_progress_raw_only_not_experiment_ready",
            },
        ]
    )

    blockers: list[str] = []
    warnings: list[str] = []
    if not bool(summaries["exists"].all()):
        blockers.append("one_or_more_expected_new_datasets_missing")
    if int(summaries["duplicate_symbol_timestamp"].fillna(0).sum()) > 0:
        blockers.append("duplicate_symbol_timestamp_in_new_gold_dataset")
    if not raw_agg.empty and raw_agg["status"].astype(str).str.contains("partial", case=False).any():
        warnings.append("core12_rem9_aggtrades_raw_download_in_progress_not_ready")
    if not market_quality.empty and (market_quality["missing_rate"].astype(float) > 0.20).any():
        warnings.append("market_structure_has_high_missing_funding_related_fields_select_columns_before_replay")
    warnings.append("core39_all_features_is_wide_derived_table_do_not_feed_all_603_columns_blindly")
    warnings.append("core3_aggtrades_is_core3_only_not_core39_or_core48_wide")

    decision = "PASS_A7AE0_NEW_DATA_INTAKE_AUDIT_WITH_USAGE_LIMITS" if not blockers else "HOLD_A7AE0_NEW_DATA_INTAKE_BLOCKED"
    auth = {
        "decision": decision,
        "blockers": blockers,
        "warnings": warnings,
        "authorizes_field_selection_contract": decision.startswith("PASS_"),
        "authorizes_direct_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "recommended_next": "A7AE1 field-family selection contract for core39/core3 data, then small controlled replay only",
    }
    manifest = {
        "generated_at": now,
        "decision": decision,
        "blockers": blockers,
        "warnings": warnings,
        "datasets": summaries.to_dict(orient="records"),
        "market_report_decision": market_report.get("decision"),
        "all_features_report_decision": all_report.get("decision"),
        "executes_replay": False,
        "executes_search": False,
        "report": str(REPORT_PATH),
        "output_dir": str(OUT_DIR),
    }

    summaries.to_csv(OUT_DIR / "a7ae0_dataset_summary.csv", index=False)
    independent_source_contract.to_csv(OUT_DIR / "a7ae0_independent_source_contract.csv", index=False)
    market_quality.to_csv(OUT_DIR / "a7ae0_market_structure_quality.csv", index=False)
    agg_cov.to_csv(OUT_DIR / "a7ae0_core3_aggtrades_coverage.csv", index=False)
    agg_catalog.to_csv(OUT_DIR / "a7ae0_core3_aggtrades_field_catalog.csv", index=False)
    raw_agg.to_csv(OUT_DIR / "a7ae0_core12_rem9_aggtrades_raw_status.csv", index=False)
    processes.to_csv(OUT_DIR / "a7ae0_running_data_processes.csv", index=False)
    write_json(OUT_DIR / "a7ae0_authorization_matrix.json", auth)
    write_json(OUT_DIR / "a7ae0_manifest.json", manifest)

    report = f"""# CRYPTO A7AE-0 New Data Intake Audit

Generated: {now}

## Decision

```text
{decision}
```

This stage inspects new data only. It does not run replay and does not run search.

## Authorization

```json
{json.dumps(auth, indent=2, sort_keys=True)}
```

## Dataset Summary

{md_table(summaries)}

## Independent Source Contract

{md_table(independent_source_contract)}

## Market Structure Quality

{md_table(market_quality, 40)}

## Core3 aggTrades Coverage

{md_table(agg_cov)}

## Core12 Remaining aggTrades Raw Status

{md_table(raw_agg)}

## Running Data Processes

{md_table(processes, 20)}

## Usage Boundary

- `core39_all_features_metrics_v3_market_structure` is a wide research/search table, not a proof panel. It needs field-family selection and correlation pruning first.
- `core39_market_structure` adds PIT-relevant market structure fields from REST historical sources; funding fields must remain as-of/backward only.
- `core3_all_features_with_aggtrades` is strong but core3-only; it cannot be projected to core39/core48.
- `core12_rem9 aggTrades raw` is currently raw/in-progress and is not experiment-ready until checksum/source trace and hourly aggregation close.
- No alpha proof, shadow, paper, live, or large search is authorized by this audit.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
