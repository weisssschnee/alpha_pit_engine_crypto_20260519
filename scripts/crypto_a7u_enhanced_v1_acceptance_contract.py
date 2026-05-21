from __future__ import annotations

import calendar
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports"
OUT_DIR = ROOT / "runtime" / "a7u_enhanced_v1_acceptance"
DATA_ROOT = Path(r"G:\AlphaFactory_CryptoData")
DATASET_ROOT = DATA_ROOT / "gold" / "microstructure" / "aggtrades_1h_flow_enhanced_v1"
MANIFEST_DIR = DATA_ROOT / "manifests"
DATE_TAG = "20260522"

EXPECTED_SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
EXPECTED_MONTHS = pd.period_range("2024-01", "2026-04", freq="M").astype(str).tolist()
EXPECTED_FILES = len(EXPECTED_SYMBOLS) * len(EXPECTED_MONTHS)

REQUIRED_COLUMNS = [
    "timestamp",
    "trade_count",
    "underlying_trade_count",
    "quantity",
    "notional",
    "buy_agg_trade_count",
    "sell_agg_trade_count",
    "buy_underlying_trade_count",
    "sell_underlying_trade_count",
    "buy_quantity",
    "sell_quantity",
    "buy_notional",
    "sell_notional",
    "signed_aggressor_quantity",
    "signed_aggressor_notional",
    "trade_count_le_100",
    "trade_count_100_1k",
    "trade_count_1k_10k",
    "trade_count_10k_100k",
    "trade_count_100k_1m",
    "trade_count_gt_1m",
    "notional_le_100",
    "notional_100_1k",
    "notional_1k_10k",
    "notional_10k_100k",
    "notional_100k_1m",
    "notional_gt_1m",
    "first_agg_trade_id",
    "last_agg_trade_id",
    "first_transact_time_ms",
    "last_transact_time_ms",
    "high_price",
    "low_price",
    "price_std",
    "max_trade_notional",
    "open_price",
    "close_price",
    "vwap",
    "buy_vwap",
    "sell_vwap",
    "avg_agg_trade_notional",
    "avg_underlying_trade_notional",
    "volume_imbalance",
    "buy_sell_notional_ratio",
    "price_range_bps",
    "close_to_open_bps",
    "large_trade_count_100k_plus",
    "large_notional_100k_plus",
    "large_trade_count_ratio_100k_plus",
    "large_notional_ratio_100k_plus",
    "symbol",
    "month",
    "source",
    "aggregation",
]

COUNT_BUCKETS = [
    "trade_count_le_100",
    "trade_count_100_1k",
    "trade_count_1k_10k",
    "trade_count_10k_100k",
    "trade_count_100k_1m",
    "trade_count_gt_1m",
]

NOTIONAL_BUCKETS = [
    "notional_le_100",
    "notional_100_1k",
    "notional_1k_10k",
    "notional_10k_100k",
    "notional_100k_1m",
    "notional_gt_1m",
]

NONNEGATIVE_FIELDS = [
    "trade_count",
    "underlying_trade_count",
    "quantity",
    "notional",
    "buy_agg_trade_count",
    "sell_agg_trade_count",
    "buy_underlying_trade_count",
    "sell_underlying_trade_count",
    "buy_quantity",
    "sell_quantity",
    "buy_notional",
    "sell_notional",
    "price_std",
    "max_trade_notional",
    "avg_agg_trade_notional",
    "avg_underlying_trade_notional",
    "price_range_bps",
    "large_trade_count_100k_plus",
    "large_notional_100k_plus",
    "large_trade_count_ratio_100k_plus",
    "large_notional_ratio_100k_plus",
] + COUNT_BUCKETS + NOTIONAL_BUCKETS


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    return df.head(max_rows).to_markdown(index=False)


def max_abs(values: pd.Series) -> float:
    if values.empty:
        return 0.0
    arr = values.to_numpy(dtype=float)
    if arr.size == 0 or np.all(np.isnan(arr)):
        return 0.0
    return float(np.nanmax(np.abs(arr)))


def expected_hours(month: str) -> int:
    year, mon = [int(x) for x in month.split("-")]
    return calendar.monthrange(year, mon)[1] * 24


def parse_partition(path: Path) -> tuple[str, str]:
    symbol = path.parent.parent.name.split("=", 1)[1]
    month = path.parent.name.split("=", 1)[1]
    return symbol, month


def audit_files() -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict[str, Any]] = []
    all_keys: list[pd.DataFrame] = []
    for path in sorted(DATASET_ROOT.rglob("part.parquet")):
        path_symbol, path_month = parse_partition(path)
        df = pd.read_parquet(path)
        ts = pd.to_datetime(df["timestamp"], utc=True)
        expected = pd.date_range(ts.min(), ts.max(), freq="1h")
        month_start = pd.Timestamp(f"{path_month}-01T00:00:00Z")
        month_end = month_start + pd.offsets.MonthEnd(0) + pd.Timedelta(hours=23)
        missing_cols = sorted(set(REQUIRED_COLUMNS).difference(df.columns))
        nonfinite = 0
        for col in df.select_dtypes(include=[np.number]).columns:
            nonfinite += int((~np.isfinite(df[col].to_numpy(dtype=float))).sum())
        negative_counts = {col: int((df[col] < 0).sum()) for col in NONNEGATIVE_FIELDS if col in df.columns}
        count_bucket_diff = max_abs(df["trade_count"] - df[COUNT_BUCKETS].sum(axis=1))
        notional_bucket_diff = max_abs(df["notional"] - df[NOTIONAL_BUCKETS].sum(axis=1))
        quantity_diff = max_abs(df["quantity"] - (df["buy_quantity"] + df["sell_quantity"]))
        notional_diff = max_abs(df["notional"] - (df["buy_notional"] + df["sell_notional"]))
        signed_qty_diff = max_abs(df["signed_aggressor_quantity"] - (df["buy_quantity"] - df["sell_quantity"]))
        signed_notional_diff = max_abs(df["signed_aggressor_notional"] - (df["buy_notional"] - df["sell_notional"]))
        imbalance_diff = max_abs(df["volume_imbalance"] - (df["signed_aggressor_notional"] / df["notional"].replace(0, np.nan)))
        price_range_diff = max_abs(df["price_range_bps"] - ((df["high_price"] - df["low_price"]) / df["vwap"].replace(0, np.nan) * 10000.0))
        close_to_open_diff = max_abs(df["close_to_open_bps"] - ((df["close_price"] - df["open_price"]) / df["open_price"].replace(0, np.nan) * 10000.0))
        large_count_diff = max_abs(df["large_trade_count_100k_plus"] - (df["trade_count_100k_1m"] + df["trade_count_gt_1m"]))
        large_notional_diff = max_abs(df["large_notional_100k_plus"] - (df["notional_100k_1m"] + df["notional_gt_1m"]))
        row = {
            "path": str(path),
            "symbol_partition": path_symbol,
            "month_partition": path_month,
            "rows": int(len(df)),
            "expected_hours": expected_hours(path_month),
            "timestamp_min": ts.min().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "timestamp_max": ts.max().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "month_start_expected": month_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "month_end_expected": month_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "missing_hour_count": int(len(expected.difference(ts))),
            "duplicate_timestamp_count": int(ts.duplicated().sum()),
            "missing_required_columns": ",".join(missing_cols),
            "symbol_column_matches_partition": bool((df["symbol"].astype(str) == path_symbol).all()),
            "month_column_matches_partition": bool((df["month"].astype(str) == path_month).all()),
            "timestamp_all_hour_floor": bool((ts.dt.minute.eq(0) & ts.dt.second.eq(0)).all()),
            "nonfinite_numeric_count": nonfinite,
            "negative_nonnegative_field_total": int(sum(negative_counts.values())),
            "trade_count_bucket_max_abs_diff": count_bucket_diff,
            "notional_bucket_max_abs_diff": notional_bucket_diff,
            "quantity_additivity_max_abs_diff": quantity_diff,
            "notional_additivity_max_abs_diff": notional_diff,
            "signed_quantity_max_abs_diff": signed_qty_diff,
            "signed_notional_max_abs_diff": signed_notional_diff,
            "volume_imbalance_notional_formula_max_abs_diff": imbalance_diff,
            "price_range_bps_formula_max_abs_diff": price_range_diff,
            "close_to_open_bps_formula_max_abs_diff": close_to_open_diff,
            "large_trade_count_formula_max_abs_diff": large_count_diff,
            "large_notional_formula_max_abs_diff": large_notional_diff,
            "vwap_within_low_high_all": bool(((df["vwap"] >= df["low_price"]) & (df["vwap"] <= df["high_price"])).all()),
            "open_close_within_low_high_all": bool(((df["open_price"] >= df["low_price"]) & (df["open_price"] <= df["high_price"]) & (df["close_price"] >= df["low_price"]) & (df["close_price"] <= df["high_price"])).all()),
            "first_last_trade_id_order_all": bool((df["first_agg_trade_id"] <= df["last_agg_trade_id"]).all()),
            "first_last_time_order_all": bool((df["first_transact_time_ms"] <= df["last_transact_time_ms"]).all()),
            "source_values": ",".join(sorted(df["source"].astype(str).unique())),
            "aggregation_values": ",".join(sorted(df["aggregation"].astype(str).unique())),
        }
        row["decision"] = (
            "PASS_A7U_FILE_ACCEPTANCE"
            if row["rows"] == row["expected_hours"]
            and row["timestamp_min"] == row["month_start_expected"]
            and row["timestamp_max"] == row["month_end_expected"]
            and row["missing_hour_count"] == 0
            and row["duplicate_timestamp_count"] == 0
            and not row["missing_required_columns"]
            and row["symbol_column_matches_partition"]
            and row["month_column_matches_partition"]
            and row["timestamp_all_hour_floor"]
            and row["nonfinite_numeric_count"] == 0
            and row["negative_nonnegative_field_total"] == 0
            and count_bucket_diff < 1e-9
            and notional_bucket_diff < 1e-2
            and quantity_diff < 1e-6
            and notional_diff < 1e-2
            and signed_qty_diff < 1e-6
            and signed_notional_diff < 1e-2
            and imbalance_diff < 1e-12
            and price_range_diff < 1e-8
            and close_to_open_diff < 1e-8
            and large_count_diff < 1e-9
            and large_notional_diff < 1e-2
            and row["vwap_within_low_high_all"]
            and row["open_close_within_low_high_all"]
            and row["first_last_trade_id_order_all"]
            and row["first_last_time_order_all"]
            else "HOLD_A7U_FILE_REVIEW"
        )
        rows.append(row)
        all_keys.append(pd.DataFrame({"symbol": path_symbol, "timestamp": ts, "path": str(path)}))
    file_df = pd.DataFrame(rows)
    key_df = pd.concat(all_keys, ignore_index=True) if all_keys else pd.DataFrame(columns=["symbol", "timestamp", "path"])
    duplicate_keys = key_df[key_df.duplicated(["symbol", "timestamp"], keep=False)].copy()
    return file_df, duplicate_keys


def audit_manifests() -> pd.DataFrame:
    enhanced = sorted(MANIFEST_DIR.glob("aggtrades_hourly_enhanced_v1*.csv"))
    raw = sorted(MANIFEST_DIR.glob("aggtrades_raw_latest_roundrobin*.csv")) + sorted(MANIFEST_DIR.glob("aggtrades_raw_only_*.csv")) + sorted(MANIFEST_DIR.glob("aggtrades_package_a*.csv"))
    rows = []
    for label, paths in [("enhanced_hourly", enhanced), ("raw_roundrobin", raw)]:
        combined = []
        for path in paths:
            df = pd.read_csv(path)
            df["manifest_path"] = str(path)
            combined.append(df)
        if not combined:
            rows.append({"manifest_group": label, "file_count": 0, "row_count": 0, "unique_symbol_month": 0, "ok_or_written_count": 0, "checksum_ok_unique_symbol_month": 0, "missing_expected_symbol_month": EXPECTED_FILES, "error_count": 0})
            continue
        df_all = pd.concat(combined, ignore_index=True)
        status = df_all.get("status", pd.Series(dtype=str)).fillna("")
        ok_cols = []
        if "checksum_status" in df_all.columns:
            ok_cols.append(df_all["checksum_status"].fillna("").eq("ok"))
        ok_or_written = status.isin(["written", "downloaded", "exists"])
        if ok_cols:
            ok_or_written = ok_or_written & ok_cols[0]
        unique_symbol_month = int(df_all[["symbol", "month"]].drop_duplicates().shape[0]) if {"symbol", "month"}.issubset(df_all.columns) else 0
        checksum_ok_unique = 0
        if {"symbol", "month", "checksum_status"}.issubset(df_all.columns):
            checksum_ok_unique = int(df_all[df_all["checksum_status"].fillna("").eq("ok")][["symbol", "month"]].drop_duplicates().shape[0])
        rows.append(
            {
                "manifest_group": label,
                "file_count": len(paths),
                "row_count": int(len(df_all)),
                "unique_symbol_month": unique_symbol_month,
                "ok_or_written_count": int(ok_or_written.sum()),
                "checksum_ok_unique_symbol_month": checksum_ok_unique,
                "missing_expected_symbol_month": max(EXPECTED_FILES - checksum_ok_unique, 0) if label == "raw_roundrobin" else max(EXPECTED_FILES - unique_symbol_month, 0),
                "error_count": int(status.eq("error").sum()),
                "manifest_paths": ";".join(str(p) for p in paths),
            }
        )
    return pd.DataFrame(rows)


def build_field_contract() -> pd.DataFrame:
    specs: list[tuple[str, str, str, str, str, str]] = [
        ("timestamp", "datetime_utc", "hour_bucket_start", "bucket start for raw aggTrades", "available_after_hour_close", "join_key"),
        ("trade_count", "count", "agg_trade_count", "number of aggregate trade rows", "available_after_hour_close", "feature"),
        ("underlying_trade_count", "count", "underlying_trade_count", "sum(last_trade_id - first_trade_id + 1)", "available_after_hour_close", "feature"),
        ("quantity", "base_asset", "total_quantity", "sum raw quantity", "available_after_hour_close", "feature"),
        ("notional", "quote_asset", "total_notional", "sum price * quantity", "available_after_hour_close", "feature"),
        ("buy_agg_trade_count", "count", "aggressor_buy_count", "is_buyer_maker=false", "available_after_hour_close", "feature"),
        ("sell_agg_trade_count", "count", "aggressor_sell_count", "is_buyer_maker=true", "available_after_hour_close", "feature"),
        ("buy_underlying_trade_count", "count", "aggressor_buy_underlying_count", "underlying count by buy aggressor side", "available_after_hour_close", "feature"),
        ("sell_underlying_trade_count", "count", "aggressor_sell_underlying_count", "underlying count by sell aggressor side", "available_after_hour_close", "feature"),
        ("buy_quantity", "base_asset", "aggressor_buy_quantity", "quantity where buyer is taker", "available_after_hour_close", "feature"),
        ("sell_quantity", "base_asset", "aggressor_sell_quantity", "quantity where seller is taker", "available_after_hour_close", "feature"),
        ("buy_notional", "quote_asset", "aggressor_buy_notional", "notional where buyer is taker", "available_after_hour_close", "feature"),
        ("sell_notional", "quote_asset", "aggressor_sell_notional", "notional where seller is taker", "available_after_hour_close", "feature"),
        ("signed_aggressor_quantity", "base_asset", "signed_flow_quantity", "buy_quantity - sell_quantity", "available_after_hour_close", "feature"),
        ("signed_aggressor_notional", "quote_asset", "signed_flow_notional", "buy_notional - sell_notional", "available_after_hour_close", "feature"),
        ("volume_imbalance", "ratio", "notional_weighted_flow_imbalance", "signed_aggressor_notional / notional", "available_after_hour_close", "feature"),
        ("buy_sell_notional_ratio", "ratio", "buy_sell_ratio", "buy_notional / sell_notional", "available_after_hour_close", "feature"),
        ("high_price", "price", "hour_high", "max trade price in hour", "available_after_hour_close", "feature"),
        ("low_price", "price", "hour_low", "min trade price in hour", "available_after_hour_close", "feature"),
        ("open_price", "price", "hour_open", "first trade price in hour", "available_after_hour_close", "feature"),
        ("close_price", "price", "hour_close", "last trade price in hour", "available_after_hour_close", "feature"),
        ("vwap", "price", "hour_vwap", "notional / quantity", "available_after_hour_close", "feature"),
        ("buy_vwap", "price", "buy_vwap", "buy_notional / buy_quantity", "available_after_hour_close", "feature"),
        ("sell_vwap", "price", "sell_vwap", "sell_notional / sell_quantity", "available_after_hour_close", "feature"),
        ("price_range_bps", "bps", "range_bps", "(high_price - low_price) / vwap * 10000", "available_after_hour_close", "feature"),
        ("close_to_open_bps", "bps", "intrahour_return_bps", "(close_price - open_price) / open_price * 10000", "available_after_hour_close", "feature"),
        ("large_trade_count_100k_plus", "count", "large_trade_count", "trade_count_100k_1m + trade_count_gt_1m", "available_after_hour_close", "feature"),
        ("large_notional_100k_plus", "quote_asset", "large_trade_notional", "notional_100k_1m + notional_gt_1m", "available_after_hour_close", "feature"),
        ("large_trade_count_ratio_100k_plus", "ratio", "large_trade_count_ratio", "large_trade_count_100k_plus / trade_count", "available_after_hour_close", "feature"),
        ("large_notional_ratio_100k_plus", "ratio", "large_trade_notional_ratio", "large_notional_100k_plus / notional", "available_after_hour_close", "feature"),
        ("first_transact_time_ms", "epoch_ms", "first_raw_trade_time", "first raw aggTrade transact_time in hour", "available_after_hour_close", "lineage"),
        ("last_transact_time_ms", "epoch_ms", "last_raw_trade_time", "last raw aggTrade transact_time in hour", "available_after_hour_close", "lineage"),
        ("first_agg_trade_id", "id", "first_agg_trade_id", "first aggregate trade id in hour", "available_after_hour_close", "lineage"),
        ("last_agg_trade_id", "id", "last_agg_trade_id", "last aggregate trade id in hour", "available_after_hour_close", "lineage"),
        ("symbol", "string", "symbol", "partition and join key", "n/a", "join_key"),
        ("month", "string", "month_partition", "partition month", "n/a", "lineage"),
        ("source", "string", "source", "source marker", "n/a", "lineage"),
        ("aggregation", "string", "aggregation", "aggregation marker", "n/a", "lineage"),
    ]
    for col in COUNT_BUCKETS:
        specs.append((col, "count", "trade_count_bucket", "aggregate trade count bucket by trade notional", "available_after_hour_close", "feature"))
    for col in NOTIONAL_BUCKETS:
        specs.append((col, "quote_asset", "notional_bucket", "notional bucket by trade notional", "available_after_hour_close", "feature"))
    for col in ["price_std", "max_trade_notional", "avg_agg_trade_notional", "avg_underlying_trade_notional"]:
        specs.append((col, "price_or_quote_asset", "distribution_summary", "hourly distribution summary", "available_after_hour_close", "feature"))
    return pd.DataFrame(specs, columns=["field_name", "unit", "semantic_group", "definition", "feature_available_time_rule", "role"]).drop_duplicates("field_name")


def build_join_contract() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "rule_id": "join_key",
                "rule": "Join to crypto 1h panel on symbol and timestamp.",
                "status": "required",
            },
            {
                "rule_id": "feature_available_time",
                "rule": "For timestamp t as hour bucket start, all aggTrades features are available only after t + 1h.",
                "status": "required",
            },
            {
                "rule_id": "execution_lag",
                "rule": "Primary experiments should use at least next-bar execution after feature availability; same-hour close execution is forbidden.",
                "status": "required",
            },
            {
                "rule_id": "raw_access",
                "rule": "Experiment code must read enhanced_v1 gold parquet, not raw zip.",
                "status": "required",
            },
            {
                "rule_id": "fast_version",
                "rule": "fast version is fallback only; enhanced_v1 is the main microstructure feature source after acceptance.",
                "status": "required",
            },
            {
                "rule_id": "coverage",
                "rule": "Current accepted dataset is core3 BTCUSDT/ETHUSDT/SOLUSDT for 2024-01 through 2026-04; do not treat it as core12.",
                "status": "required",
            },
        ]
    )


def write_report(
    now: str,
    file_audit: pd.DataFrame,
    dup_keys: pd.DataFrame,
    manifest_audit: pd.DataFrame,
    field_contract: pd.DataFrame,
    join_contract: pd.DataFrame,
    authorization: dict[str, Any],
) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    summary = {
        "files": int(len(file_audit)),
        "file_pass_count": int(file_audit["decision"].eq("PASS_A7U_FILE_ACCEPTANCE").sum()),
        "duplicate_symbol_timestamp_keys": int(len(dup_keys)),
        "symbols": sorted(file_audit["symbol_partition"].unique().tolist()),
        "months_min": str(file_audit["month_partition"].min()) if not file_audit.empty else "",
        "months_max": str(file_audit["month_partition"].max()) if not file_audit.empty else "",
    }
    lines = [
        "# Crypto A7U Enhanced v1 Data Acceptance and Feature Contract",
        "",
        f"- generated_at: `{now}`",
        "- dataset: `G:\\AlphaFactory_CryptoData\\gold\\microstructure\\aggtrades_1h_flow_enhanced_v1`",
        f"- decision: `{authorization['decision']}`",
        "- executes_search: `False`",
        "- executes_replay: `False`",
        "- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`",
        "",
        "## Summary",
        "",
        "```json",
        json.dumps(summary, indent=2, sort_keys=True),
        "```",
        "",
        "## Acceptance Decision",
        "",
        "The enhanced_v1 sample passes data acceptance for feature-contract experiments. It is stronger than OHLCV and should replace the fast version as the main microstructure source for experimental joins. It is not a final alpha panel because it is core3-only and still needs a gold panel fusion contract before model/reward use.",
        "",
        "## Manifest Traceability",
        "",
        table(manifest_audit),
        "",
        "## File Audit Sample",
        "",
        table(file_audit),
        "",
        "## Duplicate Symbol/Timestamp Keys",
        "",
        table(dup_keys.head(20)),
        "",
        "## Feature Contract",
        "",
        table(field_contract, max_rows=120),
        "",
        "## Join and Timing Contract",
        "",
        table(join_contract),
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
    ]
    (REPORT_DIR / f"CRYPTO_A7U_ENHANCED_V1_ACCEPTANCE_CONTRACT_{DATE_TAG}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    now = utc_stamp()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    file_audit, duplicate_keys = audit_files()
    manifest_audit = audit_manifests()
    field_contract = build_field_contract()
    join_contract = build_join_contract()

    all_files_pass = len(file_audit) == EXPECTED_FILES and file_audit["decision"].eq("PASS_A7U_FILE_ACCEPTANCE").all()
    duplicate_pass = duplicate_keys.empty
    manifests_no_errors = not manifest_audit.empty and (manifest_audit["error_count"].fillna(0).astype(int) == 0).all()
    raw_trace_complete = False
    raw_rows = manifest_audit[manifest_audit["manifest_group"].eq("raw_roundrobin")]
    if not raw_rows.empty:
        raw_trace_complete = int(raw_rows.iloc[0].get("checksum_ok_unique_symbol_month", 0)) >= EXPECTED_FILES

    if all_files_pass and duplicate_pass and manifests_no_errors and raw_trace_complete:
        decision = "PASS_A7U_ENHANCED_V1_ACCEPTED_FOR_FEATURE_CONTRACT_EXPERIMENTS"
    elif all_files_pass and duplicate_pass and manifests_no_errors:
        decision = "PASS_A7U_ENHANCED_V1_FEATURE_ACCEPTED_WITH_TRACEABILITY_WARNING"
    else:
        decision = "HOLD_A7U_ENHANCED_V1_ACCEPTANCE_REVIEW"
    authorization = {
        "generated_at": now,
        "decision": decision,
        "executes_search": False,
        "executes_replay": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "authorizes_experiment_line_feature_join": decision.startswith("PASS"),
        "authorizes_full_alpha_panel": False,
        "authorizes_core12_claim": False,
        "authorizes_raw_zip_direct_experiment_access": False,
        "primary_dataset": str(DATASET_ROOT),
        "coverage": {
            "symbols": EXPECTED_SYMBOLS,
            "months": f"{EXPECTED_MONTHS[0]}..{EXPECTED_MONTHS[-1]}",
            "file_count": EXPECTED_FILES,
        },
        "required_next": [
            "A7U-0R consolidated raw checksum trace manifest for all 84 symbol-month files",
            "A7U-1 join enhanced_v1 to crypto 1h panel with feature_available_time",
            "A7U-2 rolling/cross-symbol feature derivation contract",
            "A7U-3 small feature smoke against existing negative controls",
        ],
    }

    file_audit.to_csv(OUT_DIR / "a7u_file_acceptance_audit.csv", index=False)
    duplicate_keys.to_csv(OUT_DIR / "a7u_duplicate_symbol_timestamp_keys.csv", index=False)
    manifest_audit.to_csv(OUT_DIR / "a7u_manifest_traceability_audit.csv", index=False)
    field_contract.to_csv(OUT_DIR / "a7u_feature_contract.csv", index=False)
    join_contract.to_csv(OUT_DIR / "a7u_join_timing_contract.csv", index=False)
    write_json(OUT_DIR / "a7u_authorization_matrix.json", authorization)
    write_json(
        OUT_DIR / "a7u_manifest.json",
        {
            "generated_at": now,
            "script": str(Path(__file__).relative_to(ROOT)),
            "outputs": [
                str((OUT_DIR / "a7u_file_acceptance_audit.csv").relative_to(ROOT)),
                str((OUT_DIR / "a7u_duplicate_symbol_timestamp_keys.csv").relative_to(ROOT)),
                str((OUT_DIR / "a7u_manifest_traceability_audit.csv").relative_to(ROOT)),
                str((OUT_DIR / "a7u_feature_contract.csv").relative_to(ROOT)),
                str((OUT_DIR / "a7u_join_timing_contract.csv").relative_to(ROOT)),
                str((OUT_DIR / "a7u_authorization_matrix.json").relative_to(ROOT)),
                f"reports/CRYPTO_A7U_ENHANCED_V1_ACCEPTANCE_CONTRACT_{DATE_TAG}.md",
            ],
            "decision": decision,
        },
    )
    write_report(now, file_audit, duplicate_keys, manifest_audit, field_contract, join_contract, authorization)


if __name__ == "__main__":
    main()
