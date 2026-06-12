from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(os.environ.get("ALPHAFACTORY_CRYPTO_DATA_ROOT", r"G:\AlphaFactory_CryptoData"))
MAIN_ROOT = DATA_ROOT / "gold" / "features" / "binance_universe498_replay_1h_v2_20260527"
PATCH_ROOT = DATA_ROOT / "gold" / "features" / "binance_universe498_recent_patch_1h_v1_20260612"
PRE2024_FIRST_SEEN = REPO / "runtime" / "a7data_pre2024_backfill_acceptance_age_20260612" / "a7data_pre2024_first_seen_map.csv"
OUT_ROOT = DATA_ROOT / "gold" / "features" / "binance_universe498_replay_1h_v3_patch_age_20260613"
RUNTIME = REPO / "runtime" / "a7data_recent_patch_merged_panel_20260613"
REPORT = REPO / "reports" / "CRYPTO_A7DATA_RECENT_PATCH_MERGED_PANEL_20260613.md"

AGE_COLUMNS = [
    "listing_age_hours",
    "listing_age_days",
    "log1p_listing_age_days",
    "sqrt_listing_age_days",
    "age_percentile_active_universe",
    "active_universe_size",
    "history_length_hours",
    "first_observed_timestamp",
    "listing_age_source",
    "age_bucket",
]

PATCH_RENAMES = {
    "open": "trade_open",
    "high": "trade_high",
    "low": "trade_low",
    "close": "trade_close",
    "volume": "trade_volume",
    "quote_volume": "trade_quote_volume",
    "return_1h": "trade_return_1h",
    "premium_bps": "premium_close_bps",
}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 40) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    try:
        return view.to_markdown(index=False)
    except Exception:
        return "```text\n" + view.to_string(index=False) + "\n```"


def age_bucket(days: pd.Series) -> pd.Series:
    bins = [-np.inf, 30, 90, 180, 365, np.inf]
    labels = ["age_lt_30d", "age_30_90d", "age_90_180d", "age_180_365d", "age_ge_365d"]
    return pd.cut(days, bins=bins, labels=labels, right=False).astype(str)


def read_panel_part(path: Path, source: str) -> pd.DataFrame:
    df = pd.read_parquet(path, engine="pyarrow")
    if df.empty:
        return df
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True).dt.tz_localize(None)
    if "symbol" not in df.columns:
        df["symbol"] = path.parent.name.split("=", 1)[-1]
    df["a7_source_panel"] = source
    return df


def normalize_patch(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={k: v for k, v in PATCH_RENAMES.items() if k in df.columns})
    if "kline_taker_buy_quote_share" not in df.columns and {"taker_buy_quote_volume", "trade_quote_volume"}.issubset(df.columns):
        denom = pd.to_numeric(df["trade_quote_volume"], errors="coerce").replace(0, np.nan)
        df["kline_taker_buy_quote_share"] = pd.to_numeric(df["taker_buy_quote_volume"], errors="coerce") / denom
    if "mark_trade_basis_bps" not in df.columns and {"mark_close", "trade_close"}.issubset(df.columns):
        denom = pd.to_numeric(df["trade_close"], errors="coerce").replace(0, np.nan)
        df["mark_trade_basis_bps"] = (pd.to_numeric(df["mark_close"], errors="coerce") / denom - 1.0) * 10000.0
    if "source_trade_klines" not in df.columns:
        df["source_trade_klines"] = True
    if "source_metrics" not in df.columns:
        df["source_metrics"] = df.get("open_interest_last", pd.Series(np.nan, index=df.index)).notna()
    if "source_market_funding" not in df.columns:
        df["source_market_funding"] = df.get("funding_rate", pd.Series(np.nan, index=df.index)).notna()
    if "is_historical_backfill" not in df.columns:
        df["is_historical_backfill"] = True
    if "is_forward_only" not in df.columns:
        df["is_forward_only"] = False
    if "funding_interval_hours" not in df.columns:
        df["funding_interval_hours"] = 8.0
    return df


def load_first_seen(main_root: Path) -> dict[str, pd.Timestamp]:
    first_seen: dict[str, pd.Timestamp] = {}
    if PRE2024_FIRST_SEEN.exists():
        pre = pd.read_csv(PRE2024_FIRST_SEEN)
        if {"symbol", "combined_first_observed_timestamp"}.issubset(pre.columns):
            for row in pre[["symbol", "combined_first_observed_timestamp"]].dropna().to_dict("records"):
                first_seen[str(row["symbol"])] = pd.to_datetime(row["combined_first_observed_timestamp"], utc=True).tz_localize(None)
    for path in main_root.glob("symbol=*/part.parquet"):
        symbol = path.parent.name.split("=", 1)[-1]
        try:
            ts = pd.read_parquet(path, columns=["timestamp"], engine="pyarrow")["timestamp"]
        except Exception:
            continue
        ts = pd.to_datetime(ts, errors="coerce", utc=True).dt.tz_localize(None)
        min_ts = ts.min()
        if pd.notna(min_ts):
            cur = first_seen.get(symbol)
            first_seen[symbol] = min_ts if cur is None else min(cur, min_ts)
    return first_seen


def add_age_columns(df: pd.DataFrame, first_seen: dict[str, pd.Timestamp]) -> pd.DataFrame:
    df = df.sort_values(["symbol", "timestamp"]).reset_index(drop=True)
    fallback = df.groupby("symbol")["timestamp"].transform("min")
    first = df["symbol"].map(first_seen)
    first = pd.to_datetime(first).fillna(fallback)
    age_hours = (df["timestamp"] - first).dt.total_seconds() / 3600.0
    df["listing_age_hours"] = age_hours.clip(lower=0)
    df["listing_age_days"] = df["listing_age_hours"] / 24.0
    df["log1p_listing_age_days"] = np.log1p(df["listing_age_days"])
    df["sqrt_listing_age_days"] = np.sqrt(df["listing_age_days"].clip(lower=0))
    df["history_length_hours"] = df.groupby("symbol").cumcount().astype(float) + 1.0
    df["first_observed_timestamp"] = first
    df["listing_age_source"] = "observed_first_seen_lower_bound_pre2024_plus_main_plus_patch"
    df["age_bucket"] = age_bucket(df["listing_age_days"])
    df["active_universe_size"] = df.groupby("timestamp")["symbol"].transform("nunique")
    df["age_percentile_active_universe"] = df.groupby("timestamp")["listing_age_days"].rank(pct=True)
    return df


def build(main_root: Path, patch_root: Path, out_root: Path, runtime: Path, report: Path) -> dict[str, Any]:
    runtime.mkdir(parents=True, exist_ok=True)
    out_root.mkdir(parents=True, exist_ok=True)
    report.parent.mkdir(parents=True, exist_ok=True)

    first_seen = load_first_seen(main_root)
    manifest_rows: list[dict[str, Any]] = []
    duplicate_rows: list[dict[str, Any]] = []
    coverage_rows: list[dict[str, Any]] = []
    schema_columns: set[str] = set()

    main_paths = {p.parent.name.split("=", 1)[-1]: p for p in main_root.glob("symbol=*/part.parquet")}
    patch_paths = {p.parent.name.split("=", 1)[-1]: p for p in patch_root.glob("symbol=*/part-000.parquet")}
    symbols = sorted(set(main_paths) | set(patch_paths))

    for symbol in symbols:
        frames: list[pd.DataFrame] = []
        if symbol in main_paths:
            frames.append(read_panel_part(main_paths[symbol], "main_v2"))
        if symbol in patch_paths:
            frames.append(normalize_patch(read_panel_part(patch_paths[symbol], "recent_patch_v1")))
        if not frames:
            continue
        df = pd.concat(frames, ignore_index=True, sort=False)
        before = int(df.shape[0])
        dup_mask = df.duplicated(["symbol", "timestamp"], keep=False)
        if dup_mask.any():
            dup = df.loc[dup_mask, ["symbol", "timestamp", "a7_source_panel"]].sort_values(["symbol", "timestamp", "a7_source_panel"])
            duplicate_rows.extend(dup.to_dict("records"))
        # Keep the recent patch at identical timestamps because it has the richer recent source payload.
        priority = df["a7_source_panel"].map({"main_v2": 0, "recent_patch_v1": 1}).fillna(0)
        df = df.assign(_source_priority=priority).sort_values(["symbol", "timestamp", "_source_priority"])
        df = df.drop_duplicates(["symbol", "timestamp"], keep="last").drop(columns=["_source_priority"])
        dropped = before - int(df.shape[0])
        df = add_age_columns(df, first_seen)
        schema_columns.update(df.columns)

        out_dir = out_root / f"symbol={symbol}"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "part.parquet"
        df.to_parquet(out_path, index=False)
        numeric = df.select_dtypes(include=[np.number])
        inf_cells = int(np.isinf(numeric.to_numpy()).sum()) if not numeric.empty else 0
        premium_gap = int(df.get("premium_close_bps", pd.Series(index=df.index, dtype=float)).isna().sum())
        funding_gap = int(df.get("funding_rate", pd.Series(index=df.index, dtype=float)).isna().sum())
        manifest_rows.append(
            {
                "symbol": symbol,
                "status": "ok",
                "rows": int(df.shape[0]),
                "main_rows": int(frames[0].shape[0]) if symbol in main_paths else 0,
                "patch_rows": int(frames[-1].shape[0]) if symbol in patch_paths else 0,
                "overlap_rows_dropped": int(dropped),
                "timestamp_min": str(df["timestamp"].min()),
                "timestamp_max": str(df["timestamp"].max()),
                "duplicate_after_merge": int(df.duplicated(["symbol", "timestamp"]).sum()),
                "inf_cells": inf_cells,
                "premium_close_bps_na": premium_gap,
                "funding_rate_na": funding_gap,
                "age_days_min": float(df["listing_age_days"].min()),
                "age_days_max": float(df["listing_age_days"].max()),
                "output_path": str(out_path),
            }
        )
        coverage_rows.append(
            {
                "symbol": symbol,
                "rows": int(df.shape[0]),
                "premium_close_bps_coverage": float(df.get("premium_close_bps", pd.Series(index=df.index, dtype=float)).notna().mean()),
                "mark_index_basis_bps_coverage": float(df.get("mark_index_basis_bps", pd.Series(index=df.index, dtype=float)).notna().mean()),
                "funding_rate_coverage": float(df.get("funding_rate", pd.Series(index=df.index, dtype=float)).notna().mean()),
                "open_interest_last_coverage": float(df.get("open_interest_last", pd.Series(index=df.index, dtype=float)).notna().mean()),
                "recent_patch_rows": int((df["a7_source_panel"] == "recent_patch_v1").sum()),
                "main_rows_kept": int((df["a7_source_panel"] == "main_v2").sum()),
            }
        )

    manifest_df = pd.DataFrame(manifest_rows)
    coverage_df = pd.DataFrame(coverage_rows)
    duplicate_df = pd.DataFrame(duplicate_rows)
    schema_df = pd.DataFrame({"column": sorted(schema_columns)})
    manifest_df.to_csv(runtime / "a7data_recent_patch_merged_manifest.csv", index=False)
    coverage_df.to_csv(runtime / "a7data_recent_patch_merged_coverage.csv", index=False)
    duplicate_df.to_csv(runtime / "a7data_recent_patch_overlap_rows.csv", index=False)
    schema_df.to_csv(runtime / "a7data_recent_patch_merged_schema.csv", index=False)

    decision = "PASS_A7DATA_RECENT_PATCH_MERGED_PANEL_READY_FOR_CONTROLLED_EXPERIMENT"
    if manifest_df.empty or int(manifest_df["duplicate_after_merge"].sum()) != 0:
        decision = "HOLD_A7DATA_RECENT_PATCH_MERGE_DUPLICATE_OR_EMPTY"

    payload = {
        "stage": "A7DATA-RECENT-PATCH-MERGE",
        "generated_at": now_utc(),
        "decision": decision,
        "main_root": str(main_root),
        "patch_root": str(patch_root),
        "out_root": str(out_root),
        "symbols": int(manifest_df["symbol"].nunique()) if not manifest_df.empty else 0,
        "rows": int(manifest_df["rows"].sum()) if not manifest_df.empty else 0,
        "timestamp_min": str(manifest_df["timestamp_min"].min()) if not manifest_df.empty else "",
        "timestamp_max": str(manifest_df["timestamp_max"].max()) if not manifest_df.empty else "",
        "overlap_rows_dropped": int(manifest_df["overlap_rows_dropped"].sum()) if not manifest_df.empty else 0,
        "duplicate_after_merge": int(manifest_df["duplicate_after_merge"].sum()) if not manifest_df.empty else 0,
        "inf_cells": int(manifest_df["inf_cells"].sum()) if not manifest_df.empty else 0,
        "mean_premium_close_bps_coverage": float(coverage_df["premium_close_bps_coverage"].mean()) if not coverage_df.empty else None,
        "mean_mark_index_basis_bps_coverage": float(coverage_df["mark_index_basis_bps_coverage"].mean()) if not coverage_df.empty else None,
        "mean_funding_rate_coverage": float(coverage_df["funding_rate_coverage"].mean()) if not coverage_df.empty else None,
        "mean_open_interest_last_coverage": float(coverage_df["open_interest_last_coverage"].mean()) if not coverage_df.empty else None,
        "age_semantics": "observed first-seen lower bound; not true exchange listing date",
        "authorized_use": ["controlled_experiment", "recent_regime_validation", "patch_aware_candidate_validation"],
        "not_authorized_use": ["alpha_proof", "shadow_paper_live", "search_without_field_gates"],
        "required_gates": [
            "field_contract_enforcement",
            "premium_coverage_gate",
            "funding_coverage_gate",
            "age_control_gate",
            "source_trace_checksum_before_final_proof",
        ],
        "outputs": {
            "manifest": str((runtime / "a7data_recent_patch_merged_manifest.csv").relative_to(REPO)),
            "coverage": str((runtime / "a7data_recent_patch_merged_coverage.csv").relative_to(REPO)),
            "overlap_rows": str((runtime / "a7data_recent_patch_overlap_rows.csv").relative_to(REPO)),
            "schema": str((runtime / "a7data_recent_patch_merged_schema.csv").relative_to(REPO)),
            "report": str(report.relative_to(REPO)),
        },
    }
    write_json(runtime / "a7data_recent_patch_merged_manifest.json", payload)

    report.write_text(
        "\n".join(
            [
                "# CRYPTO A7DATA Recent Patch Merged Panel 20260613",
                "",
                "## Decision",
                "",
                f"`{decision}`",
                "",
                "This builds a patch-aware controlled-experiment panel by replacing the overlapping main-panel boundary hour with the richer recent patch row and adding observed first-seen age controls. It does not authorize alpha proof.",
                "",
                "## Summary",
                "",
                f"- output root: `{out_root}`",
                f"- symbols: `{payload['symbols']}`",
                f"- rows: `{payload['rows']}`",
                f"- timestamp_min: `{payload['timestamp_min']}`",
                f"- timestamp_max: `{payload['timestamp_max']}`",
                f"- overlap_rows_dropped: `{payload['overlap_rows_dropped']}`",
                f"- duplicate_after_merge: `{payload['duplicate_after_merge']}`",
                f"- inf_cells: `{payload['inf_cells']}`",
                f"- mean_premium_close_bps_coverage: `{payload['mean_premium_close_bps_coverage']}`",
                f"- mean_mark_index_basis_bps_coverage: `{payload['mean_mark_index_basis_bps_coverage']}`",
                f"- mean_funding_rate_coverage: `{payload['mean_funding_rate_coverage']}`",
                f"- mean_open_interest_last_coverage: `{payload['mean_open_interest_last_coverage']}`",
                "",
                "## Merge Rules",
                "",
                "- `recent_patch_v1` replaces `main_v2` at identical `(symbol, timestamp)` rows.",
                "- Patch columns are normalized from `open/high/low/close/volume/quote_volume` to `trade_*` names.",
                "- `premium_bps` is normalized to `premium_close_bps`.",
                "- `kline_taker_buy_quote_share` is recomputed from taker buy quote volume divided by quote volume when available.",
                "- Age fields are observed first-seen lower bounds and must not be interpreted as true exchange listing dates.",
                "",
                "## Required Downstream Gates",
                "",
                "- Block formulas that use `premium_close_bps` without symbol/date coverage checks.",
                "- Block funding-spread assumptions that treat sparse funding events as dense hourly fields.",
                "- Keep field-role enforcement active; legacy `forward_trade_return_1h` is a label-like column and must not enter ordinary alpha features.",
                "- Final proof still requires official Binance Vision CHECKSUM/source trace audit.",
                "",
                "## Coverage Sample",
                "",
                md_table(coverage_df.sort_values("premium_close_bps_coverage").head(20)),
            ]
        ),
        encoding="utf-8",
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--main-root", default=str(MAIN_ROOT))
    parser.add_argument("--patch-root", default=str(PATCH_ROOT))
    parser.add_argument("--out-root", default=str(OUT_ROOT))
    parser.add_argument("--runtime", default=str(RUNTIME))
    parser.add_argument("--report", default=str(REPORT))
    args = parser.parse_args()
    payload = build(Path(args.main_root), Path(args.patch_root), Path(args.out_root), Path(args.runtime), Path(args.report))
    print(payload["decision"])
    print(payload["out_root"])
    print(payload["outputs"]["report"])


if __name__ == "__main__":
    main()
