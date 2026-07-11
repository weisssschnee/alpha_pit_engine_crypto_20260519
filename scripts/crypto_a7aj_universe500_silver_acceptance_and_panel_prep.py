from __future__ import annotations

import json
import math
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from alphafactory_crypto.funding_events import funding_event_flags_from_last_time


DATA_ROOT = Path(r"G:\AlphaFactory_CryptoData")
INCOMING_ROOT = DATA_ROOT / "incoming_company" / "crypto_universe500_silver_20260525"
EXTRACTED_ROOT = INCOMING_ROOT / "extracted"

METRICS_ROOT = EXTRACTED_ROOT / "silver" / "binance_vision" / "metrics_1h_universe500_v1"
MARKET_ROOT = EXTRACTED_ROOT / "silver" / "binance_vision" / "monthly_market_funding_1h_top300_v1"
MANIFEST_ROOT = EXTRACTED_ROOT / "manifests"
REPORT_IN_ROOT = EXTRACTED_ROOT / "reports"

METRICS_MANIFEST = MANIFEST_ROOT / "metrics_1h_universe500_v1_20260525_aggregate_v1.csv"
MARKET_MANIFEST = MANIFEST_ROOT / "monthly_market_funding_1h_top300_v1_20260525_aggregate_v1.csv"
METRICS_REPORT_IN = REPORT_IN_ROOT / "metrics_1h_universe500_v1_20260525_aggregate_v1.json"
MARKET_REPORT_IN = REPORT_IN_ROOT / "monthly_market_funding_1h_top300_v1_20260525_aggregate_v1.json"

CORE12_AGG_PANEL = DATA_ROOT / "gold" / "features" / "binance_core12_aggtrades_unified_features_v1_20260524.parquet"
OUTPUT_PANEL_ROOT = DATA_ROOT / "gold" / "features" / "binance_universe300_market_metrics_agg_overlay_1h_v1_20260525"

OUT_DIR = ROOT / "runtime" / "a7aj_universe500_silver_acceptance_panel_prep"
REPORT_ACCEPTANCE = ROOT / "reports" / "CRYPTO_A7AJ0_UNIVERSE500_SILVER_ACCEPTANCE_20260525.md"
REPORT_PANEL = ROOT / "reports" / "CRYPTO_A7AJ1_UNIVERSE300_SEARCH_PANEL_PREP_20260525.md"

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

SPLITS = [
    ("train_2024", "2024-01-01 00:00:00+00:00", "2024-12-31 23:00:00+00:00", True),
    ("validation_2025H1", "2025-01-01 00:00:00+00:00", "2025-06-30 23:00:00+00:00", True),
    ("recent_2025H2_2026Apr", "2025-07-01 00:00:00+00:00", "2026-04-30 23:00:00+00:00", True),
    ("may_2026_stress_only", "2026-05-01 00:00:00+00:00", "2026-05-31 23:00:00+00:00", False),
]

METRICS_RENAME = {
    "n_5m": "metrics_n_5m",
    "sum_open_interest_last": "metrics_open_interest_last",
    "sum_open_interest_mean": "metrics_open_interest_mean",
    "sum_open_interest_value_last": "metrics_open_interest_value_last",
    "sum_open_interest_value_mean": "metrics_open_interest_value_mean",
    "count_toptrader_long_short_ratio_last": "metrics_toptrader_account_long_short_ratio_last",
    "count_toptrader_long_short_ratio_mean": "metrics_toptrader_account_long_short_ratio_mean",
    "sum_toptrader_long_short_ratio_last": "metrics_toptrader_position_long_short_ratio_last",
    "sum_toptrader_long_short_ratio_mean": "metrics_toptrader_position_long_short_ratio_mean",
    "count_long_short_ratio_last": "metrics_global_account_long_short_ratio_last",
    "count_long_short_ratio_mean": "metrics_global_account_long_short_ratio_mean",
    "sum_taker_long_short_vol_ratio_last": "metrics_taker_buy_sell_volume_ratio_last",
    "sum_taker_long_short_vol_ratio_mean": "metrics_taker_buy_sell_volume_ratio_mean",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def symbol_path(root: Path, symbol: str) -> Path:
    return root / f"symbol={symbol}" / "part.csv.gz"


def read_symbol_csv(root: Path, symbol: str, parse_timestamp: bool = True) -> pd.DataFrame:
    path = symbol_path(root, symbol)
    df = pd.read_csv(path)
    if parse_timestamp and "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    return df


def load_manifest(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    for col in ["min_timestamp", "max_timestamp"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], utc=True)
    return df


def safe_div(num: pd.Series, den: pd.Series) -> pd.Series:
    return (num.astype(float) / den.astype(float).replace(0, np.nan)).replace([np.inf, -np.inf], np.nan)


def audit_symbol_file(root: Path, manifest_row: pd.Series, row_col: str) -> dict[str, Any]:
    symbol = str(manifest_row["symbol"])
    path = symbol_path(root, symbol)
    out: dict[str, Any] = {
        "symbol": symbol,
        "path": str(path),
        "file_exists": path.exists(),
        "manifest_status": str(manifest_row.get("status", "")),
        "manifest_rows": int(manifest_row[row_col]),
        "manifest_min_timestamp": str(manifest_row.get("min_timestamp", "")),
        "manifest_max_timestamp": str(manifest_row.get("max_timestamp", "")),
    }
    if not path.exists():
        out.update(
            {
                "read_ok": False,
                "error": "missing_local_file",
                "actual_rows": 0,
                "duplicate_timestamp_count": None,
                "gap_hours": None,
                "inf_cell_count": None,
                "negative_value_count": None,
            }
        )
        return out
    try:
        df = read_symbol_csv(root, symbol)
        numeric = df.select_dtypes(include=[np.number])
        ts = df["timestamp"]
        unique_ts = ts.drop_duplicates()
        expected = int(((ts.max() - ts.min()).total_seconds() // 3600) + 1) if len(ts) else 0
        gap_hours = max(0, expected - int(unique_ts.nunique()))
        negative_cols = [c for c in numeric.columns if not c.endswith("_rate") and "ratio" not in c and "premium" not in c]
        negative_value_count = int((numeric[negative_cols] < 0).sum().sum()) if negative_cols else 0
        out.update(
            {
                "read_ok": True,
                "error": "",
                "actual_rows": int(len(df)),
                "row_count_match": int(len(df)) == int(manifest_row[row_col]),
                "actual_min_timestamp": str(ts.min()),
                "actual_max_timestamp": str(ts.max()),
                "min_timestamp_match": ts.min() == manifest_row["min_timestamp"],
                "max_timestamp_match": ts.max() == manifest_row["max_timestamp"],
                "duplicate_timestamp_count": int(df.duplicated(["symbol", "timestamp"]).sum()),
                "monotonic_timestamp": bool(ts.is_monotonic_increasing),
                "gap_hours": int(gap_hours),
                "inf_cell_count": int(np.isinf(numeric.to_numpy(dtype=float, copy=False)).sum()) if not numeric.empty else 0,
                "nan_cell_count": int(numeric.isna().sum().sum()) if not numeric.empty else 0,
                "negative_value_count": negative_value_count,
            }
        )
    except Exception as exc:  # pragma: no cover - audit script
        out.update(
            {
                "read_ok": False,
                "error": repr(exc),
                "actual_rows": 0,
                "duplicate_timestamp_count": None,
                "gap_hours": None,
                "inf_cell_count": None,
                "negative_value_count": None,
            }
        )
    return out


def audit_dataset(root: Path, manifest: pd.DataFrame, row_col: str) -> pd.DataFrame:
    rows = [audit_symbol_file(root, row, row_col) for _, row in manifest.sort_values("symbol").iterrows()]
    return pd.DataFrame(rows)


def derive_market_features(market: pd.DataFrame) -> pd.DataFrame:
    market = market.copy()
    numeric_cols = [c for c in market.columns if c not in {"symbol", "timestamp"}]
    for col in numeric_cols:
        market[col] = pd.to_numeric(market[col], errors="coerce")
    market["mark_index_ratio"] = safe_div(market["mark_close"], market["index_close"]) - 1.0
    market["mark_index_basis_bps"] = market["mark_index_ratio"] * 10000.0
    market["premium_close_bps"] = market["premium_close"] * 10000.0
    market["funding_rate_bps"] = market["last_funding_rate"] * 10000.0
    market["funding_event_observed"] = funding_event_flags_from_last_time(market)
    market["market_counts_complete"] = (
        (market["mark_count"] >= 3600)
        & (market["index_count"] >= 3600)
        & (market["premium_count"] >= 720)
    )
    return market


def derive_metrics_features(metrics: pd.DataFrame) -> pd.DataFrame:
    metrics = metrics.rename(columns=METRICS_RENAME).copy()
    for col in metrics.columns:
        if col not in {"symbol", "timestamp"}:
            metrics[col] = pd.to_numeric(metrics[col], errors="coerce")
    metrics["metrics_5m_complete"] = metrics["metrics_n_5m"] >= 12
    return metrics


def load_agg_overlay() -> tuple[pd.DataFrame, list[str]]:
    if not CORE12_AGG_PANEL.exists():
        return pd.DataFrame(), []
    schema_cols = pd.read_parquet(CORE12_AGG_PANEL, engine="pyarrow", columns=["symbol", "timestamp"]).columns.tolist()
    _ = schema_cols  # keep a cheap existence check before loading selected columns
    all_cols = pd.read_parquet(CORE12_AGG_PANEL, engine="pyarrow", columns=None).columns.tolist()
    agg_cols = [c for c in all_cols if c == "agg_features_available" or c.startswith("agg_")]
    use_cols = ["symbol", "timestamp"] + agg_cols
    agg = pd.read_parquet(CORE12_AGG_PANEL, engine="pyarrow", columns=use_cols)
    agg["timestamp"] = pd.to_datetime(agg["timestamp"], utc=True)
    return agg, agg_cols


def build_search_panel(market_manifest: pd.DataFrame, metrics_symbols: set[str]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if OUTPUT_PANEL_ROOT.exists():
        resolved = OUTPUT_PANEL_ROOT.resolve()
        if DATA_ROOT.resolve() not in resolved.parents:
            raise RuntimeError(f"Refusing to overwrite unexpected path: {OUTPUT_PANEL_ROOT}")
        shutil.rmtree(OUTPUT_PANEL_ROOT)
    OUTPUT_PANEL_ROOT.mkdir(parents=True, exist_ok=True)

    agg_overlay, agg_cols = load_agg_overlay()
    agg_by_symbol = {s: g.copy() for s, g in agg_overlay.groupby("symbol")} if not agg_overlay.empty else {}

    manifest_rows: list[dict[str, Any]] = []
    split_rows: list[dict[str, Any]] = []
    quality_rows: list[dict[str, Any]] = []
    symbols = sorted(market_manifest["symbol"].astype(str).tolist())
    for symbol in symbols:
        market = derive_market_features(read_symbol_csv(MARKET_ROOT, symbol))
        if symbol in metrics_symbols and symbol_path(METRICS_ROOT, symbol).exists():
            metrics = derive_metrics_features(read_symbol_csv(METRICS_ROOT, symbol))
            panel = market.merge(metrics, on=["symbol", "timestamp"], how="left", validate="one_to_one")
        else:
            panel = market.copy()
            panel["metrics_5m_complete"] = False

        if symbol in agg_by_symbol:
            panel = panel.merge(agg_by_symbol[symbol], on=["symbol", "timestamp"], how="left", validate="one_to_one")
            panel["agg_overlay_available"] = panel["agg_features_available"].fillna(False).astype(bool)
        else:
            panel["agg_overlay_available"] = False

        panel["is_core12"] = symbol in CORE12
        panel["feature_available_time"] = panel["timestamp"] + pd.Timedelta(hours=1)
        panel["execution_time_min"] = panel["timestamp"] + pd.Timedelta(hours=2)
        panel["source_market_top300"] = True
        panel["source_metrics_universe500"] = symbol in metrics_symbols
        panel["source_core12_agg_overlay"] = symbol in CORE12

        for col in panel.columns:
            if col not in {"symbol", "timestamp", "feature_available_time", "execution_time_min"}:
                if panel[col].dtype == object:
                    continue
                if pd.api.types.is_numeric_dtype(panel[col]):
                    panel[col] = panel[col].replace([np.inf, -np.inf], np.nan)

        out_dir = OUTPUT_PANEL_ROOT / f"symbol={symbol}"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "part.parquet"
        panel.to_parquet(out_path, engine="pyarrow", index=False)

        numeric = panel.select_dtypes(include=[np.number])
        manifest_rows.append(
            {
                "symbol": symbol,
                "rows": int(len(panel)),
                "timestamp_min": str(panel["timestamp"].min()),
                "timestamp_max": str(panel["timestamp"].max()),
                "path": str(out_path),
                "metrics_join_rate": round(float(panel["metrics_5m_complete"].notna().mean()), 6),
                "metrics_complete_5m_rate": round(float(panel["metrics_5m_complete"].fillna(False).mean()), 6),
                "agg_overlay_available_rate": round(float(panel["agg_overlay_available"].fillna(False).mean()), 6),
                "duplicate_symbol_timestamp": int(panel.duplicated(["symbol", "timestamp"]).sum()),
                "inf_cell_count": int(np.isinf(numeric.to_numpy(dtype=float, copy=False)).sum()) if not numeric.empty else 0,
            }
        )
        for split, start, end, allowed in SPLITS:
            mask = (panel["timestamp"] >= pd.Timestamp(start)) & (panel["timestamp"] <= pd.Timestamp(end))
            part = panel.loc[mask]
            split_rows.append(
                {
                    "symbol": symbol,
                    "split": split,
                    "rows": int(len(part)),
                    "metrics_complete_5m_rate": round(float(part["metrics_5m_complete"].fillna(False).mean()), 6) if len(part) else np.nan,
                    "agg_overlay_available_rate": round(float(part["agg_overlay_available"].fillna(False).mean()), 6) if len(part) else np.nan,
                    "may_allowed_for_ranking": allowed,
                }
            )
        quality_rows.append(
            {
                "symbol": symbol,
                "missing_rate_mean": round(float(panel.isna().mean(numeric_only=False).mean()), 6),
                "market_counts_complete_rate": round(float(panel["market_counts_complete"].fillna(False).mean()), 6),
                "metrics_5m_complete_rate": round(float(panel["metrics_5m_complete"].fillna(False).mean()), 6),
                "agg_overlay_available_rate": round(float(panel["agg_overlay_available"].fillna(False).mean()), 6),
            }
        )

    return pd.DataFrame(manifest_rows), pd.DataFrame(split_rows), pd.DataFrame(quality_rows)


def feature_contract(columns: list[str], agg_cols: list[str]) -> pd.DataFrame:
    rows = []
    for col in columns:
        if col in {"symbol", "timestamp"}:
            source_class = "key"
            independent_source = False
            timing = "row identity"
        elif col.startswith("metrics_"):
            source_class = "binance_metrics"
            independent_source = True
            timing = "hourly aggregate from 5m metrics; usable after hour close with field-native latency audit"
        elif col.startswith(("mark_", "index_", "premium_", "funding_", "last_funding_", "market_")):
            source_class = "market_funding"
            independent_source = True
            timing = "hourly market/funding aggregate; usable after hour close with field-native latency audit"
        elif col in agg_cols or col.startswith("agg_"):
            source_class = "core12_aggtrades_overlay"
            independent_source = True
            timing = "core12 aggTrades hourly/derived; usable after hour close with field-native latency audit"
        elif col.endswith("_time") or col.startswith("source_") or col.startswith("is_"):
            source_class = "metadata"
            independent_source = False
            timing = "metadata"
        else:
            source_class = "derived"
            independent_source = False
            timing = "derived from accepted source fields"
        rows.append(
            {
                "field_name": col,
                "source_class": source_class,
                "independent_source": independent_source,
                "feature_available_rule": timing,
                "may_policy": "May stress-only; not ranking/tuning/selection",
            }
        )
    return pd.DataFrame(rows)


def make_universe_registry(market_audit: pd.DataFrame, metrics_audit: pd.DataFrame) -> pd.DataFrame:
    m = market_audit.copy()
    met = metrics_audit[["symbol", "read_ok", "gap_hours", "actual_rows", "actual_min_timestamp", "actual_max_timestamp"]].rename(
        columns={
            "read_ok": "metrics_read_ok",
            "gap_hours": "metrics_gap_hours",
            "actual_rows": "metrics_rows",
            "actual_min_timestamp": "metrics_min_timestamp",
            "actual_max_timestamp": "metrics_max_timestamp",
        }
    )
    reg = m.merge(met, on="symbol", how="left")
    reg["is_core12"] = reg["symbol"].isin(CORE12)
    reg["market_full_2024_2026apr"] = (
        (pd.to_datetime(reg["actual_min_timestamp"], utc=True) <= pd.Timestamp("2024-01-01 00:00:00+00:00"))
        & (pd.to_datetime(reg["actual_max_timestamp"], utc=True) >= pd.Timestamp("2026-04-30 23:00:00+00:00"))
        & (reg["gap_hours"] == 0)
        & (reg["read_ok"] == True)
    )
    reg["metrics_available"] = reg["metrics_read_ok"].fillna(False)
    reg["search_tier"] = np.select(
        [
            reg["market_full_2024_2026apr"] & reg["metrics_available"] & reg["is_core12"],
            reg["market_full_2024_2026apr"] & reg["metrics_available"],
            reg["metrics_available"],
        ],
        [
            "core12_full_history_with_agg_overlay",
            "top300_full_history_market_metrics",
            "listing_aware_market_metrics",
        ],
        default="hold_missing_metrics_or_market_gap",
    )
    return reg


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    metrics_manifest = load_manifest(METRICS_MANIFEST)
    market_manifest = load_manifest(MARKET_MANIFEST)

    metrics_audit = audit_dataset(METRICS_ROOT, metrics_manifest, "rows_1h")
    market_audit = audit_dataset(MARKET_ROOT, market_manifest, "rows")
    metrics_symbols = set(metrics_manifest.loc[metrics_manifest["status"].astype(str).str.lower() == "ok", "symbol"].astype(str))
    market_symbols = set(market_manifest.loc[market_manifest["status"].astype(str).str.lower() == "ok", "symbol"].astype(str))

    panel_manifest, split_coverage, panel_quality = build_search_panel(market_manifest, metrics_symbols)

    sample_symbol = "BTCUSDT" if "BTCUSDT" in market_symbols else sorted(market_symbols)[0]
    sample_panel = pd.read_parquet(OUTPUT_PANEL_ROOT / f"symbol={sample_symbol}" / "part.parquet", engine="pyarrow")
    agg_overlay, agg_cols = load_agg_overlay()
    contract = feature_contract(sample_panel.columns.tolist(), agg_cols)
    universe_registry = make_universe_registry(market_audit, metrics_audit)

    summary = {
        "generated_at": utc_now(),
        "decision": "PASS_A7AJ_UNIVERSE500_SILVER_ACCEPTED_AND_SEARCH_PANEL_PREPARED",
        "incoming_root": str(INCOMING_ROOT),
        "metrics_symbols": int(len(metrics_symbols)),
        "market_symbols": int(len(market_symbols)),
        "market_metrics_intersection_symbols": int(len(market_symbols & metrics_symbols)),
        "metrics_rows_manifest": int(metrics_manifest["rows_1h"].sum()),
        "market_rows_manifest": int(market_manifest["rows"].sum()),
        "output_panel_root": str(OUTPUT_PANEL_ROOT),
        "output_panel_symbols": int(panel_manifest["symbol"].nunique()),
        "output_panel_rows": int(panel_manifest["rows"].sum()),
        "output_panel_columns_sample": int(len(sample_panel.columns)),
        "executes_search": False,
        "executes_replay": False,
        "authorizes_a7ak_small_field_family_smoke": True,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "warnings": [
            "Incoming company package contains silver aggregates only; raw checksum trace remains on company machine",
            "Universe300 is current/top selection and is not by itself a survivorship-safe proof universe",
            "Output market/funding panel ends at 2026-04-30; May stress requires separate current/forward source and remains excluded from ranking",
            "May remains stress-only and must not be used for ranking, tuning, universe selection, or promotion",
        ],
    }

    blockers: list[str] = []
    if int((metrics_audit["file_exists"] == False).sum()) or int((market_audit["file_exists"] == False).sum()):
        blockers.append("missing_local_silver_file")
    if int((metrics_audit["read_ok"] == False).sum()) or int((market_audit["read_ok"] == False).sum()):
        blockers.append("silver_read_error")
    if int(metrics_audit["duplicate_timestamp_count"].fillna(0).sum()) or int(market_audit["duplicate_timestamp_count"].fillna(0).sum()):
        blockers.append("duplicate_symbol_timestamp")
    if int(panel_manifest["duplicate_symbol_timestamp"].sum()):
        blockers.append("output_duplicate_symbol_timestamp")
    if int(panel_manifest["inf_cell_count"].sum()):
        blockers.append("output_inf_cells")
    summary["blockers"] = blockers
    if blockers:
        summary["decision"] = "HOLD_A7AJ_UNIVERSE500_SILVER_ACCEPTANCE_BLOCKED"
        summary["authorizes_a7ak_small_field_family_smoke"] = False

    metrics_summary = pd.DataFrame(
        [
            {
                "dataset": "metrics_1h_universe500_v1",
                "manifest_symbols": int(len(metrics_manifest)),
                "ok_status": int((metrics_manifest["status"].astype(str).str.lower() == "ok").sum()),
                "audit_read_ok": int(metrics_audit["read_ok"].sum()),
                "rows_manifest": int(metrics_manifest["rows_1h"].sum()),
                "rows_actual": int(metrics_audit["actual_rows"].sum()),
                "duplicate_timestamp_count": int(metrics_audit["duplicate_timestamp_count"].fillna(0).sum()),
                "gap_hours": int(metrics_audit["gap_hours"].fillna(0).sum()),
                "inf_cell_count": int(metrics_audit["inf_cell_count"].fillna(0).sum()),
            },
            {
                "dataset": "monthly_market_funding_1h_top300_v1",
                "manifest_symbols": int(len(market_manifest)),
                "ok_status": int((market_manifest["status"].astype(str).str.lower() == "ok").sum()),
                "audit_read_ok": int(market_audit["read_ok"].sum()),
                "rows_manifest": int(market_manifest["rows"].sum()),
                "rows_actual": int(market_audit["actual_rows"].sum()),
                "duplicate_timestamp_count": int(market_audit["duplicate_timestamp_count"].fillna(0).sum()),
                "gap_hours": int(market_audit["gap_hours"].fillna(0).sum()),
                "inf_cell_count": int(market_audit["inf_cell_count"].fillna(0).sum()),
            },
        ]
    )

    outputs = {
        "summary": OUT_DIR / "a7aj_summary.json",
        "metrics_symbol_audit": OUT_DIR / "a7aj_metrics_symbol_audit.csv",
        "market_symbol_audit": OUT_DIR / "a7aj_market_symbol_audit.csv",
        "dataset_summary": OUT_DIR / "a7aj_dataset_summary.csv",
        "output_panel_manifest": OUT_DIR / "a7aj_output_panel_manifest.csv",
        "split_coverage": OUT_DIR / "a7aj_split_coverage.csv",
        "panel_quality": OUT_DIR / "a7aj_panel_quality.csv",
        "feature_contract": OUT_DIR / "a7aj_feature_contract.csv",
        "universe_registry": OUT_DIR / "a7aj_universe_registry.csv",
        "search_chain_config": OUT_DIR / "a7aj_search_chain_config.json",
    }
    write_json(outputs["summary"], summary)
    metrics_audit.to_csv(outputs["metrics_symbol_audit"], index=False)
    market_audit.to_csv(outputs["market_symbol_audit"], index=False)
    metrics_summary.to_csv(outputs["dataset_summary"], index=False)
    panel_manifest.to_csv(outputs["output_panel_manifest"], index=False)
    split_coverage.to_csv(outputs["split_coverage"], index=False)
    panel_quality.to_csv(outputs["panel_quality"], index=False)
    contract.to_csv(outputs["feature_contract"], index=False)
    universe_registry.to_csv(outputs["universe_registry"], index=False)

    search_config = {
        "stage": "A7AK",
        "input_panel_root": str(OUTPUT_PANEL_ROOT),
        "universe_registry": str(outputs["universe_registry"]),
        "allowed_next_step": "A7AK1 small controlled field-family smoke",
        "max_initial_symbols": "strict full-history subset from a7aj_universe_registry.csv",
        "feature_families": [
            "market_funding",
            "binance_metrics_open_interest_and_positioning",
            "core12_aggtrades_overlay",
            "cross_source_interactions_derived_in_runner",
        ],
        "blocked": [
            "large_search",
            "alpha_proof",
            "shadow_paper_live",
            "May ranking/tuning/selection",
            "using this top300 panel as May stress source; it has no May 2026 market/funding rows",
            "using current top300 membership as proof universe without survivorship caveat",
        ],
        "timing_contract": {
            "timestamp": "1h bucket start UTC",
            "feature_available_time": "timestamp + 1h",
            "minimum_execution_time": "timestamp + 1h / next 1h bar open",
            "fixed_delay_stress_required": False,
        },
        "source_trace_boundary": "local silver accepted; raw checksum trace remains on company machine",
        "may_boundary": "this panel ends at 2026-04-30; May stress must come from separate stress-only source",
    }
    write_json(outputs["search_chain_config"], search_config)

    acceptance_md = f"""# CRYPTO A7AJ-0 Universe500 Silver Acceptance

Generated: {summary["generated_at"]}

## Decision

```text
{summary["decision"]}
```

This audit validates the incoming company-machine silver aggregates on the local machine. It does not run replay and does not run search.

## Summary

```json
{json.dumps(summary, indent=2, sort_keys=True)}
```

## Dataset Summary

{md_table(metrics_summary)}

## Manifest Reports

```text
metrics_report: {METRICS_REPORT_IN}
market_report: {MARKET_REPORT_IN}
metrics_manifest: {METRICS_MANIFEST}
market_manifest: {MARKET_MANIFEST}
```

## Worst Metrics Gaps

{md_table(metrics_audit.sort_values(["gap_hours", "actual_rows"], ascending=[False, False])[["symbol", "actual_rows", "actual_min_timestamp", "actual_max_timestamp", "gap_hours", "duplicate_timestamp_count", "inf_cell_count"]], 30)}

## Worst Market Gaps

{md_table(market_audit.sort_values(["gap_hours", "actual_rows"], ascending=[False, False])[["symbol", "actual_rows", "actual_min_timestamp", "actual_max_timestamp", "gap_hours", "duplicate_timestamp_count", "inf_cell_count"]], 30)}

## Boundary

```text
raw data remains on company machine
local acceptance covers silver aggregates and company manifests only
May remains stress-only
no alpha proof, large search, shadow, paper, or live authorization
```
"""
    REPORT_ACCEPTANCE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_ACCEPTANCE.write_text(acceptance_md, encoding="utf-8")

    tier_summary = universe_registry["search_tier"].value_counts().rename_axis("search_tier").reset_index(name="symbols")
    split_summary = (
        split_coverage.groupby("split", as_index=False)
        .agg(
            rows=("rows", "sum"),
            symbols=("symbol", "nunique"),
            metrics_complete_5m_rate=("metrics_complete_5m_rate", "mean"),
            agg_overlay_available_rate=("agg_overlay_available_rate", "mean"),
            may_allowed_for_ranking=("may_allowed_for_ranking", "first"),
        )
        .sort_values("split")
    )
    panel_md = f"""# CRYPTO A7AJ-1 Universe300 Search Panel Prep

Generated: {summary["generated_at"]}

## Decision

```text
{summary["decision"]}
```

This stage materializes a partitioned top300 market+metrics panel and overlays the accepted core12 aggTrades unified features where available. It prepares the next controlled smoke path; it does not authorize direct formula search.

## Output Panel

```text
{OUTPUT_PANEL_ROOT}
```

## Panel Summary

```json
{json.dumps({k: summary[k] for k in ["output_panel_root", "output_panel_symbols", "output_panel_rows", "output_panel_columns_sample", "authorizes_a7ak_small_field_family_smoke", "authorizes_large_search", "authorizes_alpha_proof"]}, indent=2, sort_keys=True)}
```

## Universe Tiers

{md_table(tier_summary)}

## Split Coverage

{md_table(split_summary)}

## Feature Contract Summary

{md_table(contract["source_class"].value_counts().rename_axis("source_class").reset_index(name="fields"))}

## Search Chain Boundary

```text
AUTHORIZED:
  A7AK1 small controlled field-family smoke on strict full-history subset

NOT AUTHORIZED:
  direct large formula search
  alpha proof
  shadow / paper / live

TIMING:
  timestamp = 1h bucket start UTC
  feature_available_time = timestamp + 1h
  minimum execution_time = timestamp + 1h / next 1h bar open
  fixed delay stress = prohibited

MAY:
  this panel has no May 2026 market/funding rows
  May stress requires a separate current/forward source
  stress-only; not ranking, tuning, selection, universe selection, or promotion
```
"""
    REPORT_PANEL.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PANEL.write_text(panel_md, encoding="utf-8")

    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
