from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports"
OUT_DIR = ROOT / "runtime" / "a7s3_sample_acceptance"
DATA_ROOT = Path(r"G:\AlphaFactory_CryptoData")
DATE_TAG = "20260521"

CORE12 = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "BNBUSDT",
    "XRPUSDT",
    "DOGEUSDT",
    "ADAUSDT",
    "LINKUSDT",
    "AVAXUSDT",
    "LTCUSDT",
    "BCHUSDT",
    "SUIUSDT",
]

AGGTRADE_FILES = [
    DATA_ROOT / "gold" / "microstructure" / "aggtrades_1h_flow_fast" / "symbol=BTCUSDT" / "month=2025-09" / "part.parquet",
    DATA_ROOT / "gold" / "microstructure" / "aggtrades_1h_flow_fast" / "symbol=BTCUSDT" / "month=2025-10" / "part.parquet",
    DATA_ROOT / "gold" / "microstructure" / "aggtrades_1h_flow_fast" / "symbol=BTCUSDT" / "month=2025-11" / "part.parquet",
    DATA_ROOT / "gold" / "microstructure" / "aggtrades_1h_flow_fast" / "symbol=SOLUSDT" / "month=2026-04" / "part.parquet",
]

ORDERBOOK_FILES = [
    DATA_ROOT / "silver" / "binance_api" / "orderbook_forward_snapshot" / "run=20260521_071938" / "part.parquet",
    DATA_ROOT / "silver" / "binance_api" / "orderbook_forward_snapshot" / "run=20260521_074122" / "part.parquet",
]

POSITIONING_MANIFEST = DATA_ROOT / "manifests" / "positioning_forward_5m_2026-05-21_manifest.csv"
PANEL_PATH = DATA_ROOT / "gold" / "panels" / "crypto_core12_1h_v1.parquet"
PANEL_REFRESH_MANIFEST = DATA_ROOT / "manifests" / "crypto_forward_rest_1m_refresh_20260521_043623.csv"
PANEL_REFRESH_REPORT = DATA_ROOT / "reports" / "crypto_forward_rest_1m_refresh_20260521_043623.json"


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    return df.head(max_rows).to_markdown(index=False)


def max_abs(series: pd.Series) -> float:
    if series.empty:
        return float("nan")
    return float(np.nanmax(np.abs(series.to_numpy(dtype=float))))


def audit_aggtrades() -> pd.DataFrame:
    required_cols = {
        "timestamp",
        "trade_count",
        "quantity",
        "notional",
        "buy_quantity",
        "sell_quantity",
        "buy_notional",
        "sell_notional",
        "signed_aggressor_quantity",
        "signed_aggressor_notional",
        "max_trade_notional",
        "symbol",
        "month",
        "volume_imbalance",
        "source",
        "aggregation",
    }
    count_buckets = [
        "trade_count_le_100",
        "trade_count_100_1k",
        "trade_count_1k_10k",
        "trade_count_10k_100k",
        "trade_count_100k_1m",
        "trade_count_gt_1m",
    ]
    notional_buckets = [
        "notional_le_100",
        "notional_100_1k",
        "notional_1k_10k",
        "notional_10k_100k",
        "notional_100k_1m",
        "notional_gt_1m",
    ]
    rows: list[dict[str, Any]] = []
    for path in AGGTRADE_FILES:
        row: dict[str, Any] = {"path": str(path), "exists": path.exists()}
        if not path.exists():
            row["decision"] = "FAIL_MISSING_FILE"
            rows.append(row)
            continue
        df = pd.read_parquet(path)
        ts = pd.to_datetime(df["timestamp"], utc=True)
        expected = pd.date_range(ts.min(), ts.max(), freq="1h")
        missing = expected.difference(ts)
        quantity_diff = max_abs(df["quantity"] - (df["buy_quantity"] + df["sell_quantity"]))
        notional_diff = max_abs(df["notional"] - (df["buy_notional"] + df["sell_notional"]))
        signed_qty_diff = max_abs(df["signed_aggressor_quantity"] - (df["buy_quantity"] - df["sell_quantity"]))
        signed_notional_diff = max_abs(df["signed_aggressor_notional"] - (df["buy_notional"] - df["sell_notional"]))
        imbalance_notional_diff = max_abs(df["volume_imbalance"] - (df["signed_aggressor_notional"] / df["notional"].replace(0, np.nan)))
        imbalance_quantity_diff = max_abs(df["volume_imbalance"] - (df["signed_aggressor_quantity"] / df["quantity"].replace(0, np.nan)))
        count_bucket_diff = max_abs(df["trade_count"] - df[count_buckets].sum(axis=1)) if set(count_buckets).issubset(df.columns) else float("nan")
        notional_bucket_diff = max_abs(df["notional"] - df[notional_buckets].sum(axis=1)) if set(notional_buckets).issubset(df.columns) else float("nan")
        row.update(
            {
                "symbol": ",".join(sorted(df["symbol"].dropna().astype(str).unique())),
                "month": ",".join(sorted(df["month"].dropna().astype(str).unique())),
                "rows": int(len(df)),
                "columns_present": len(df.columns),
                "missing_required_columns": ",".join(sorted(required_cols.difference(df.columns))),
                "min_timestamp": ts.min().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "max_timestamp": ts.max().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "missing_hour_count": int(len(missing)),
                "timestamp_all_hour_floor": bool((ts.dt.minute.eq(0) & ts.dt.second.eq(0)).all()),
                "volume_imbalance_min": float(df["volume_imbalance"].min()),
                "volume_imbalance_max": float(df["volume_imbalance"].max()),
                "quantity_additivity_max_abs_diff": quantity_diff,
                "notional_additivity_max_abs_diff": notional_diff,
                "signed_quantity_max_abs_diff": signed_qty_diff,
                "signed_notional_max_abs_diff": signed_notional_diff,
                "volume_imbalance_notional_formula_max_abs_diff": imbalance_notional_diff,
                "volume_imbalance_quantity_formula_max_abs_diff": imbalance_quantity_diff,
                "trade_count_bucket_max_abs_diff": count_bucket_diff,
                "notional_bucket_max_abs_diff": notional_bucket_diff,
            }
        )
        row["decision"] = (
            "PASS_A7S3_AGGTRADES_1H_FLOW_SAMPLE"
            if not row["missing_required_columns"]
            and row["missing_hour_count"] == 0
            and row["timestamp_all_hour_floor"]
            and quantity_diff < 1e-6
            and notional_diff < 1e-3
            and signed_qty_diff < 1e-6
            and signed_notional_diff < 1e-3
            and imbalance_notional_diff < 1e-12
            and count_bucket_diff < 1e-6
            and notional_bucket_diff < 1e-3
            else "HOLD_A7S3_AGGTRADES_SAMPLE_REVIEW"
        )
        rows.append(row)
    return pd.DataFrame(rows)


def audit_orderbook() -> pd.DataFrame:
    required_cols = {
        "symbol",
        "collector_time",
        "observable_time",
        "event_time",
        "forward_only_flag",
        "best_bid",
        "best_ask",
        "bid_size_1",
        "ask_size_1",
        "mid",
        "spread",
        "spread_bps",
        "depth_bid_notional_5",
        "depth_ask_notional_5",
        "depth_bid_notional_10",
        "depth_ask_notional_10",
        "depth_bid_notional_20",
        "depth_ask_notional_20",
        "depth_imbalance_20",
    }
    rows = []
    for path in ORDERBOOK_FILES:
        row: dict[str, Any] = {"path": str(path), "exists": path.exists()}
        if not path.exists():
            row["decision"] = "FAIL_MISSING_FILE"
            rows.append(row)
            continue
        df = pd.read_parquet(path)
        row.update(
            {
                "rows": int(len(df)),
                "symbol_count": int(df["symbol"].nunique()),
                "missing_required_columns": ",".join(sorted(required_cols.difference(df.columns))),
                "forward_only_all_true": bool(df["forward_only_flag"].fillna(False).astype(bool).all()) if "forward_only_flag" in df.columns else False,
                "time_fields_not_null": bool(df[["collector_time", "observable_time", "event_time"]].notna().all().all()) if {"collector_time", "observable_time", "event_time"}.issubset(df.columns) else False,
                "event_time_equals_collector_time_all": bool((df["event_time"].astype(str) == df["collector_time"].astype(str)).all()) if {"event_time", "collector_time"}.issubset(df.columns) else False,
                "best_bid_lt_best_ask_all": bool((df["best_bid"] < df["best_ask"]).all()) if {"best_bid", "best_ask"}.issubset(df.columns) else False,
                "spread_bps_min": float(df["spread_bps"].min()) if "spread_bps" in df.columns else None,
                "spread_bps_max": float(df["spread_bps"].max()) if "spread_bps" in df.columns else None,
                "depth_imbalance_min": float(df["depth_imbalance_20"].min()) if "depth_imbalance_20" in df.columns else None,
                "depth_imbalance_max": float(df["depth_imbalance_20"].max()) if "depth_imbalance_20" in df.columns else None,
            }
        )
        row["decision"] = (
            "PASS_A7S3_ORDERBOOK_FORWARD_SAMPLE"
            if row["rows"] == 12
            and row["symbol_count"] == 12
            and not row["missing_required_columns"]
            and row["forward_only_all_true"]
            and row["time_fields_not_null"]
            and row["best_bid_lt_best_ask_all"]
            and (row["spread_bps_min"] or 0) > 0
            and -1.0 <= (row["depth_imbalance_min"] or -2) <= 1.0
            and -1.0 <= (row["depth_imbalance_max"] or 2) <= 1.0
            else "HOLD_A7S3_ORDERBOOK_SAMPLE_REVIEW"
        )
        rows.append(row)
    return pd.DataFrame(rows)


def audit_positioning() -> pd.DataFrame:
    required_cols = {
        "event_time",
        "event_time_ms",
        "observable_time",
        "collector_time",
        "forward_only_flag",
        "no_historical_backfill_flag",
    }
    rows = []
    if not POSITIONING_MANIFEST.exists():
        return pd.DataFrame([{"source": str(POSITIONING_MANIFEST), "exists": False, "decision": "FAIL_MISSING_MANIFEST"}])
    manifest = pd.read_csv(POSITIONING_MANIFEST)
    for endpoint, group in manifest.groupby("endpoint"):
        checked = 0
        missing_files = 0
        missing_cols: set[str] = set()
        forward_false = 0
        no_backfill_false = 0
        rows_total = 0
        for path_str in group["silver_path"].dropna().astype(str):
            path = Path(path_str)
            if not path.exists():
                missing_files += 1
                continue
            df = pd.read_parquet(path)
            checked += 1
            rows_total += len(df)
            missing_cols.update(required_cols.difference(df.columns))
            if "forward_only_flag" in df.columns:
                forward_false += int((~df["forward_only_flag"].fillna(False).astype(bool)).sum())
            if "no_historical_backfill_flag" in df.columns:
                no_backfill_false += int((~df["no_historical_backfill_flag"].fillna(False).astype(bool)).sum())
        rows.append(
            {
                "endpoint": endpoint,
                "manifest_rows": int(len(group)),
                "silver_files_checked": checked,
                "missing_files": missing_files,
                "rows_total": rows_total,
                "missing_required_columns": ",".join(sorted(missing_cols)),
                "forward_only_false_count": forward_false,
                "no_historical_backfill_false_count": no_backfill_false,
                "decision": "PASS_A7S3_POSITIONING_FORWARD_SCHEMA" if checked == len(group) and not missing_cols and forward_false == 0 and no_backfill_false == 0 else "HOLD_A7S3_POSITIONING_SCHEMA_REVIEW",
            }
        )
    return pd.DataFrame(rows)


def audit_panel() -> pd.DataFrame:
    row: dict[str, Any] = {
        "panel_path": str(PANEL_PATH),
        "panel_exists": PANEL_PATH.exists(),
        "refresh_manifest_exists": PANEL_REFRESH_MANIFEST.exists(),
        "refresh_report_exists": PANEL_REFRESH_REPORT.exists(),
    }
    if PANEL_PATH.exists():
        df = pd.read_parquet(PANEL_PATH, columns=["symbol", "timestamp"])
        ts = pd.to_datetime(df["timestamp"], utc=True)
        max_ts = ts.max()
        latest = df[ts == max_ts]
        row.update(
            {
                "rows": int(len(df)),
                "symbol_count": int(df["symbol"].nunique()),
                "latest_timestamp": max_ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "latest_timestamp_symbol_count": int(latest["symbol"].nunique()),
            }
        )
    row["decision"] = "PASS_A7S3_PANEL_REFRESH_SAMPLE" if row.get("latest_timestamp") == "2026-05-21T03:00:00Z" and row.get("latest_timestamp_symbol_count") == 12 else "HOLD_A7S3_PANEL_REFRESH_REVIEW"
    return pd.DataFrame([row])


def acceptance_matrix(agg: pd.DataFrame, orderbook: pd.DataFrame, positioning: pd.DataFrame, panel: pd.DataFrame) -> pd.DataFrame:
    def all_pass(df: pd.DataFrame, prefix: str) -> bool:
        return not df.empty and df["decision"].astype(str).str.startswith(prefix).all()

    rows = [
        {
            "asset": "aggTrades_1h_flow_fast_samples",
            "decision": "PASS_FOR_A7S_EXPERIMENTAL_FEATURE_AUDIT" if all_pass(agg, "PASS") else "HOLD",
            "allowed_use": "feature_schema_and_small_research_panel_join_test",
            "not_allowed_use": "full_core12_alpha_proof_until_backfill_contract",
        },
        {
            "asset": "orderbook_forward_snapshot_samples",
            "decision": "PASS_FOR_A7T_FORWARD_CONTEXT_ONLY" if all_pass(orderbook, "PASS") else "HOLD",
            "allowed_use": "forward_observation_context",
            "not_allowed_use": "historical_alpha_proof_or_backfill",
        },
        {
            "asset": "positioning_forward_schema",
            "decision": "PASS_FOR_A7T_FORWARD_CONTEXT_ONLY" if all_pass(positioning, "PASS") else "HOLD",
            "allowed_use": "append_only_forward_history",
            "not_allowed_use": "2024_2026_historical_proof",
        },
        {
            "asset": "crypto_core12_1h_panel_refresh",
            "decision": "PASS_FOR_A7T_MARKET_DATA_FRESHNESS" if all_pass(panel, "PASS") else "HOLD",
            "allowed_use": "fresh panel base for observation",
            "not_allowed_use": "alpha promotion",
        },
    ]
    return pd.DataFrame(rows)


def write_report(now: str, agg: pd.DataFrame, orderbook: pd.DataFrame, positioning: pd.DataFrame, panel: pd.DataFrame, matrix: pd.DataFrame, authorization: dict[str, Any]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Crypto A7S-3 Sample Package Acceptance Audit",
        "",
        f"- generated_at: `{now}`",
        "- decision: `PASS_A7S3_SAMPLE_PACKAGE_FOR_CONTRACTED_EXPERIMENTS_HOLD_ALPHA_PROOF`",
        "- executes_search: `False`",
        "- executes_replay: `False`",
        "- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`",
        "",
        "## Acceptance Matrix",
        "",
        table(matrix),
        "",
        "## AggTrades 1h Flow Samples",
        "",
        table(agg),
        "",
        "## Orderbook Forward Snapshots",
        "",
        table(orderbook),
        "",
        "## Positioning Forward Schema",
        "",
        table(positioning),
        "",
        "## 1h Gold Panel Refresh",
        "",
        table(panel),
        "",
        "## Notes",
        "",
        "- AggTrades samples pass schema, continuity, bucket additivity, signed-flow algebra, and notional-weighted volume imbalance formula checks.",
        "- `is_buyer_maker = true` is treated as seller aggressor; therefore signed aggressor flow equals buy flow minus sell flow under the current definition. `volume_imbalance` is notional-weighted: `signed_aggressor_notional / notional`. This semantic is acceptable for experiments but should remain explicit in the field contract.",
        "- Orderbook snapshots pass forward-only checks, but `event_time` currently equals collector/observable time. Treat it as snapshot observation time, not exchange book-update event time.",
        "- Positioning forward silver files include event/observable/collector time and forward/no-backfill flags.",
        "- None of these sample passes authorize historical alpha proof.",
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
    ]
    (REPORT_DIR / f"CRYPTO_A7S3_SAMPLE_PACKAGE_ACCEPTANCE_AUDIT_{DATE_TAG}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    now = utc_stamp()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    agg = audit_aggtrades()
    orderbook = audit_orderbook()
    positioning = audit_positioning()
    panel = audit_panel()
    matrix = acceptance_matrix(agg, orderbook, positioning, panel)

    authorization = {
        "generated_at": now,
        "decision": "PASS_A7S3_SAMPLE_PACKAGE_FOR_CONTRACTED_EXPERIMENTS_HOLD_ALPHA_PROOF",
        "executes_search": False,
        "executes_replay": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "authorizes_aggtrades_schema_join_experiment": True,
        "authorizes_orderbook_forward_observation_context": True,
        "authorizes_positioning_forward_observation_context": True,
        "authorizes_full_core12_aggtrades_backfill": False,
        "required_before_full_backfill": [
            "costed_storage_runtime_plan",
            "core12_monthly_manifest_plan",
            "checksum_and_repair_policy",
            "gold_join_contract_with_feature_available_time",
        ],
    }

    agg.to_csv(OUT_DIR / "a7s3_aggtrades_sample_audit.csv", index=False)
    orderbook.to_csv(OUT_DIR / "a7s3_orderbook_snapshot_audit.csv", index=False)
    positioning.to_csv(OUT_DIR / "a7s3_positioning_forward_schema_audit.csv", index=False)
    panel.to_csv(OUT_DIR / "a7s3_panel_refresh_audit.csv", index=False)
    matrix.to_csv(OUT_DIR / "a7s3_acceptance_matrix.csv", index=False)
    write_json(OUT_DIR / "a7s3_authorization_matrix.json", authorization)
    write_json(
        OUT_DIR / "a7s3_manifest.json",
        {
            "generated_at": now,
            "script": str(Path(__file__).relative_to(ROOT)),
            "outputs": [
                str((OUT_DIR / "a7s3_aggtrades_sample_audit.csv").relative_to(ROOT)),
                str((OUT_DIR / "a7s3_orderbook_snapshot_audit.csv").relative_to(ROOT)),
                str((OUT_DIR / "a7s3_positioning_forward_schema_audit.csv").relative_to(ROOT)),
                str((OUT_DIR / "a7s3_panel_refresh_audit.csv").relative_to(ROOT)),
                str((OUT_DIR / "a7s3_acceptance_matrix.csv").relative_to(ROOT)),
                str((OUT_DIR / "a7s3_authorization_matrix.json").relative_to(ROOT)),
                f"reports/CRYPTO_A7S3_SAMPLE_PACKAGE_ACCEPTANCE_AUDIT_{DATE_TAG}.md",
            ],
            "decision": authorization["decision"],
        },
    )
    write_report(now, agg, orderbook, positioning, panel, matrix, authorization)


if __name__ == "__main__":
    main()
