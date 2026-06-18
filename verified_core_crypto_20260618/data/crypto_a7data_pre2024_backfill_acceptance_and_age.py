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
SOURCE_ROOT = DATA_ROOT / "gold" / "features" / "binance_universe_pre2024_1h_backfill_gold_v1_20260612"
OUT_ROOT = DATA_ROOT / "gold" / "features" / "binance_universe_pre2024_1h_backfill_gold_age_v1_20260612"
SOURCE_COVERAGE = DATA_ROOT / "manifests" / "binance_universe_pre2024_1m_backfill_silver_v1_20260612_coverage.csv"
SOURCE_MANIFEST = DATA_ROOT / "manifests" / "binance_universe_pre2024_1m_backfill_silver_v1_20260612_manifest.csv"
RAW_MANIFEST = DATA_ROOT / "manifests" / "binance_vision_monthly_pool_manifest_universe_pre2024_1m_backfill_20260612_r2_merged.csv"
MAIN_PANEL_ROOT = DATA_ROOT / "gold" / "features" / "binance_universe498_replay_1h_v2_20260527"
RUNTIME = REPO / "runtime" / "a7data_pre2024_backfill_acceptance_age_20260612"
REPORT = REPO / "reports" / "CRYPTO_A7DATA_PRE2024_BACKFILL_ACCEPTANCE_AGE_20260612.md"

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


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path) if path.exists() and path.stat().st_size else pd.DataFrame()


def age_bucket(days: pd.Series) -> pd.Series:
    bins = [-np.inf, 30, 90, 180, 365, np.inf]
    labels = ["age_lt_30d", "age_30_90d", "age_90_180d", "age_180_365d", "age_ge_365d"]
    return pd.cut(days, bins=bins, labels=labels, right=False).astype(str)


def collect_first_seen() -> pd.DataFrame:
    coverage = read_csv(SOURCE_COVERAGE)
    if coverage.empty:
        raise RuntimeError(f"missing coverage: {SOURCE_COVERAGE}")
    coverage["min_timestamp"] = pd.to_datetime(coverage["min_timestamp"], utc=True)
    pre = coverage.groupby("symbol", as_index=False).agg(
        pre2024_first_observed_timestamp=("min_timestamp", "min"),
        pre2024_last_observed_timestamp=("max_timestamp", "max"),
        pre2024_rows_1h=("rows_1h", "sum"),
        pre2024_months=("month", "nunique"),
    )

    main_rows: list[dict[str, Any]] = []
    for path in MAIN_PANEL_ROOT.glob("symbol=*/part.parquet"):
        symbol = path.parent.name.split("=", 1)[-1]
        try:
            ts = pd.read_parquet(path, columns=["timestamp"], engine="pyarrow")["timestamp"]
        except Exception:
            continue
        ts = pd.to_datetime(ts, utc=True, errors="coerce")
        main_rows.append(
            {
                "symbol": symbol,
                "main_first_observed_timestamp": ts.min(),
                "main_last_observed_timestamp": ts.max(),
                "main_rows_1h": int(ts.notna().sum()),
            }
        )
    main = pd.DataFrame(main_rows)
    out = pre.merge(main, on="symbol", how="left")
    out["combined_first_observed_timestamp"] = out[["pre2024_first_observed_timestamp", "main_first_observed_timestamp"]].min(axis=1)
    out["listing_age_source"] = "observed_first_seen_lower_bound_pre2024_plus_main_panel"
    return out


def build_augmented_panel(first_seen: pd.DataFrame, out_root: Path) -> pd.DataFrame:
    out_root.mkdir(parents=True, exist_ok=True)
    first_map = {
        str(row["symbol"]): pd.Timestamp(row["combined_first_observed_timestamp"])
        for row in first_seen.to_dict("records")
        if pd.notna(row.get("combined_first_observed_timestamp"))
    }
    rows: list[dict[str, Any]] = []
    frames_for_rank: list[pd.DataFrame] = []
    for path in sorted(SOURCE_ROOT.glob("symbol=*/month=*/part.parquet")):
        try:
            df = pd.read_parquet(path, engine="pyarrow")
        except Exception as exc:
            rows.append({"source_path": str(path), "status": "read_error", "error": repr(exc)})
            continue
        if df.empty:
            rows.append({"source_path": str(path), "status": "empty", "error": ""})
            continue
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        symbol = str(df["symbol"].iloc[0])
        first_ts = first_map.get(symbol, df["timestamp"].min())
        age_hours = (df["timestamp"] - first_ts).dt.total_seconds() / 3600.0
        df["listing_age_hours"] = age_hours.clip(lower=0)
        df["listing_age_days"] = df["listing_age_hours"] / 24.0
        df["log1p_listing_age_days"] = np.log1p(df["listing_age_days"])
        df["sqrt_listing_age_days"] = np.sqrt(df["listing_age_days"].clip(lower=0))
        df["history_length_hours"] = np.arange(len(df), dtype=float) + 1.0
        df["first_observed_timestamp"] = first_ts
        df["listing_age_source"] = "observed_first_seen_lower_bound_pre2024_plus_main_panel"
        df["age_bucket"] = age_bucket(df["listing_age_days"])
        frames_for_rank.append(df)

    if not frames_for_rank:
        raise RuntimeError(f"no source parquet files under {SOURCE_ROOT}")
    full = pd.concat(frames_for_rank, ignore_index=True)
    full["active_universe_size"] = full.groupby("timestamp")["symbol"].transform("nunique")
    full["age_percentile_active_universe"] = full.groupby("timestamp")["listing_age_days"].rank(pct=True)
    full = full.sort_values(["symbol", "timestamp"]).reset_index(drop=True)

    for (symbol, month), part in full.groupby(["symbol", full["timestamp"].dt.strftime("%Y-%m")], sort=True):
        out_dir = out_root / f"symbol={symbol}" / f"month={month}"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "part.parquet"
        part.to_parquet(out_path, index=False)
        rows.append(
            {
                "symbol": symbol,
                "month": month,
                "status": "ok",
                "rows": int(part.shape[0]),
                "min_timestamp": str(part["timestamp"].min()),
                "max_timestamp": str(part["timestamp"].max()),
                "active_universe_size_min": int(part["active_universe_size"].min()),
                "active_universe_size_max": int(part["active_universe_size"].max()),
                "age_days_min": float(part["listing_age_days"].min()),
                "age_days_max": float(part["listing_age_days"].max()),
                "output_path": str(out_path),
            }
        )
    return pd.DataFrame(rows), full


def acceptance_tables(first_seen: pd.DataFrame, manifest: pd.DataFrame, coverage: pd.DataFrame, raw: pd.DataFrame, full: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    symbol_summary = full.groupby("symbol", as_index=False).agg(
        rows_1h=("timestamp", "size"),
        min_timestamp=("timestamp", "min"),
        max_timestamp=("timestamp", "max"),
        age_days_min=("listing_age_days", "min"),
        age_days_max=("listing_age_days", "max"),
        active_universe_size_median=("active_universe_size", "median"),
    )
    symbol_summary = symbol_summary.merge(first_seen, on="symbol", how="left")

    age_bucket_summary = full.groupby("age_bucket", as_index=False).agg(
        rows=("timestamp", "size"),
        symbols=("symbol", "nunique"),
        min_timestamp=("timestamp", "min"),
        max_timestamp=("timestamp", "max"),
    ).sort_values("age_bucket")

    return symbol_summary, age_bucket_summary


def main() -> None:
    global SOURCE_ROOT
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", default=str(SOURCE_ROOT))
    parser.add_argument("--out-root", default=str(OUT_ROOT))
    parser.add_argument("--runtime", default=str(RUNTIME))
    parser.add_argument("--report", default=str(REPORT))
    args = parser.parse_args()

    SOURCE_ROOT = Path(args.source_root)
    out_root = Path(args.out_root)
    runtime = Path(args.runtime)
    report = Path(args.report)
    runtime.mkdir(parents=True, exist_ok=True)
    report.parent.mkdir(parents=True, exist_ok=True)

    source_manifest = read_csv(SOURCE_MANIFEST)
    source_coverage = read_csv(SOURCE_COVERAGE)
    raw_manifest = read_csv(RAW_MANIFEST)
    first_seen = collect_first_seen()
    output_manifest, full = build_augmented_panel(first_seen, out_root)
    symbol_summary, age_bucket_summary = acceptance_tables(first_seen, source_manifest, source_coverage, raw_manifest, full)

    first_seen.to_csv(runtime / "a7data_pre2024_first_seen_map.csv", index=False)
    output_manifest.to_csv(runtime / "a7data_pre2024_age_augmented_manifest.csv", index=False)
    symbol_summary.to_csv(runtime / "a7data_pre2024_symbol_acceptance_summary.csv", index=False)
    age_bucket_summary.to_csv(runtime / "a7data_pre2024_age_bucket_summary.csv", index=False)

    converted_files = int((source_manifest["status"].astype(str) == "ok").sum()) if not source_manifest.empty and "status" in source_manifest else 0
    if not raw_manifest.empty and "status" in raw_manifest:
        raw_status = raw_manifest["status"].astype(str)
        raw_404 = int(raw_status.str.contains("404", case=False, na=False).sum())
        raw_bad = raw_status.str.contains("error|fail", case=False, na=False)
        raw_ok = int((~raw_status.str.contains("404", case=False, na=False) & ~raw_bad).sum())
    else:
        raw_ok = 0
        raw_404 = 0
    duplicate_timestamps = int(source_coverage["duplicate_timestamp_count"].sum()) if not source_coverage.empty and "duplicate_timestamp_count" in source_coverage else -1
    decision = "PASS_A7DATA_PRE2024_BACKFILL_ACCEPTED_WITH_AGE_AUGMENTATION"
    if duplicate_timestamps != 0 or converted_files == 0:
        decision = "HOLD_A7DATA_PRE2024_BACKFILL_ACCEPTANCE_GAP"

    manifest = {
        "stage": "A7DATA-PRE2024",
        "generated_at": now_utc(),
        "decision": decision,
        "source_root": str(SOURCE_ROOT),
        "age_augmented_gold_root": str(out_root),
        "raw_ok_or_existing": raw_ok,
        "raw_404_listing_gaps": raw_404,
        "converted_files": converted_files,
        "output_files": int(output_manifest["status"].eq("ok").sum()) if not output_manifest.empty and "status" in output_manifest else 0,
        "symbols": int(full["symbol"].nunique()),
        "rows_1h": int(full.shape[0]),
        "min_timestamp": str(full["timestamp"].min()),
        "max_timestamp": str(full["timestamp"].max()),
        "duplicate_timestamp_count": duplicate_timestamps,
        "age_columns": AGE_COLUMNS,
        "listing_age_semantics": "observed first-seen lower bound, consistent with existing A7AK listing_age_days semantics; not exchange true listing date",
        "authorized_use": [
            "regime_bank",
            "stress_prototype",
            "age_bucket_attribution",
            "microstructure_1h_feature_source",
        ],
        "not_authorized_use": [
            "direct_merge_into_ordinary_alpha_search_panel",
            "alpha_proof",
            "shadow_paper_live",
        ],
        "outputs": {
            "first_seen_map": str((runtime / "a7data_pre2024_first_seen_map.csv").relative_to(REPO)),
            "age_augmented_manifest": str((runtime / "a7data_pre2024_age_augmented_manifest.csv").relative_to(REPO)),
            "symbol_acceptance_summary": str((runtime / "a7data_pre2024_symbol_acceptance_summary.csv").relative_to(REPO)),
            "age_bucket_summary": str((runtime / "a7data_pre2024_age_bucket_summary.csv").relative_to(REPO)),
            "report": str(report.relative_to(REPO)),
        },
    }
    write_json(runtime / "a7data_pre2024_manifest.json", manifest)

    report.write_text(
        "\n".join(
            [
                "# CRYPTO A7DATA Pre-2024 Backfill Acceptance And Age Augmentation 20260612",
                "",
                "## Decision",
                "",
                f"`{decision}`",
                "",
                "This accepts the 2023-07 to 2023-12 backfill as a regime/stress data bank and builds a listing-age augmented 1h gold layer. It does not authorize direct alpha search or alpha proof.",
                "",
                "## Delivered Data Acceptance",
                "",
                f"- raw_ok_or_existing: `{raw_ok}`",
                f"- raw_404_listing_gaps: `{raw_404}`",
                f"- converted_files: `{converted_files}`",
                f"- output_files: `{manifest['output_files']}`",
                f"- symbols: `{manifest['symbols']}`",
                f"- rows_1h: `{manifest['rows_1h']}`",
                f"- min_timestamp: `{manifest['min_timestamp']}`",
                f"- max_timestamp: `{manifest['max_timestamp']}`",
                f"- duplicate_timestamp_count: `{duplicate_timestamps}`",
                "",
                "## Age Augmentation",
                "",
                f"- age_augmented_gold_root: `{out_root}`",
                "- age fields: `listing_age_hours`, `listing_age_days`, `log1p_listing_age_days`, `sqrt_listing_age_days`, `age_percentile_active_universe`, `active_universe_size`, `history_length_hours`, `first_observed_timestamp`, `age_bucket`",
                "- listing age semantics: observed first-seen lower bound, not exchange true listing date. This mirrors the existing A7AK panel-age semantics and avoids pretending old coins truly listed in 2023-07.",
                "",
                "## Age Bucket Summary",
                "",
                md_table(age_bucket_summary, 20),
                "",
                "## Symbol Summary Sample",
                "",
                md_table(symbol_summary.sort_values('rows_1h', ascending=False).head(30), 30),
                "",
                "## Use Policy",
                "",
                "Allowed: regime bank, stress prototype, age-bucket attribution, and 1m-derived microstructure feature research.",
                "",
                "Not allowed yet: direct merge into ordinary-alpha search, alpha proof, shadow, paper, or live.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(decision)
    print(report)


if __name__ == "__main__":
    main()
