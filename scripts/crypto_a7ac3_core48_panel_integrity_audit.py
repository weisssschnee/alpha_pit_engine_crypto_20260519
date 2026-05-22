from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(r"G:\AlphaFactory_CryptoData")

CORE12_PANEL = DATA_ROOT / "gold" / "panels" / "crypto_core12_1h_with_aggtrades_metrics_features_v1.parquet"
PRIMARY_PANEL = DATA_ROOT / "gold" / "panels" / "crypto_primary_core48_additions_1h_with_metrics_v1.parquet"
OUTPUT_PANEL = DATA_ROOT / "gold" / "panels" / "crypto_core48_1h_with_metrics_candidate_v1.parquet"

TRACK_REGISTRY = ROOT / "runtime" / "a7ac1_expanded_universe_backfill_contract" / "a7ac1_track_symbol_registry.csv"
OUT_DIR = ROOT / "runtime" / "a7ac3_core48_panel_integrity_audit"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7AC3_CORE48_PANEL_INTEGRITY_AUDIT_20260522.md"

COMMON_WINDOW_START = pd.Timestamp("2024-03-16 12:00:00", tz="UTC")
COMMON_WINDOW_END = pd.Timestamp("2026-04-30 23:00:00", tz="UTC")


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    return df.head(max_rows).to_markdown(index=False)


def sha256_file(path: Path) -> str:
    import hashlib

    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_registry() -> pd.DataFrame:
    registry = pd.read_csv(TRACK_REGISTRY)
    return registry[registry["included_in_primary_core48"].astype(str).str.lower().eq("true")].copy()


def normalize_panel(df: pd.DataFrame, registry: pd.DataFrame, source_panel: str) -> pd.DataFrame:
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    if "open_time_ms" not in df.columns:
        df["open_time_ms"] = (df["timestamp"].astype("int64") // 1_000_000).astype("int64")
    if "interval" not in df.columns:
        df["interval"] = "1h"
    if "bar_interval" not in df.columns:
        df["bar_interval"] = "1h"
    if "feature_available_time" not in df.columns:
        df["feature_available_time"] = df["timestamp"] + pd.Timedelta(hours=1)
    else:
        df["feature_available_time"] = pd.to_datetime(df["feature_available_time"], utc=True, errors="coerce")
    if "execution_time_min" not in df.columns:
        df["execution_time_min"] = df["timestamp"] + pd.Timedelta(hours=1)
    else:
        df["execution_time_min"] = pd.to_datetime(df["execution_time_min"], utc=True, errors="coerce")
    if "metrics_features_available" not in df.columns:
        df["metrics_features_available"] = df.get("open_interest", pd.Series(index=df.index, dtype=float)).notna()
    if "metrics_vendor_warning_caveat" not in df.columns:
        df["metrics_vendor_warning_caveat"] = False
    if "agg_features_available" not in df.columns:
        df["agg_features_available"] = False
    df["panel_source"] = source_panel
    df = df.merge(registry[["symbol", "track", "tier", "priority"]], on="symbol", how="left")
    return df


def build_symbol_coverage(panel: pd.DataFrame, registry: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, rr in registry.iterrows():
        symbol = rr["symbol"]
        part = panel[panel["symbol"].eq(symbol)].sort_values("timestamp")
        if part.empty:
            rows.append(
                {
                    "symbol": symbol,
                    "track": rr["track"],
                    "tier": rr["tier"],
                    "rows": 0,
                    "timestamp_min": "",
                    "timestamp_max": "",
                    "common_window_rows": 0,
                    "common_window_missing_hours": "",
                    "duplicate_keys": 0,
                    "gap_count": "",
                    "listing_policy": "missing_panel_rows",
                    "ready_for_common_window": False,
                }
            )
            continue
        common = part[part["core48_common_window_eligible"]]
        expected_common_hours = int(((COMMON_WINDOW_END - COMMON_WINDOW_START) / pd.Timedelta(hours=1)) + 1)
        common_missing = expected_common_hours - int(len(common))
        diffs = part["timestamp"].diff().dropna()
        rows.append(
            {
                "symbol": symbol,
                "track": rr["track"],
                "tier": rr["tier"],
                "rows": int(len(part)),
                "timestamp_min": str(part["timestamp"].min()),
                "timestamp_max": str(part["timestamp"].max()),
                "common_window_rows": int(len(common)),
                "common_window_missing_hours": int(common_missing),
                "duplicate_keys": int(part.duplicated(["timestamp"]).sum()),
                "gap_count": int((diffs != pd.Timedelta(hours=1)).sum()),
                "listing_policy": "starts_at_listing_gap_boundary" if symbol == "BOMEUSDT" else "continuous_from_2024_01",
                "ready_for_common_window": int(common_missing) == 0 and int(part.duplicated(["timestamp"]).sum()) == 0,
            }
        )
    return pd.DataFrame(rows)


def build_field_coverage(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    key_cols = {"symbol", "timestamp", "track", "tier", "priority", "panel_source"}
    for col in panel.columns:
        if col in key_cols:
            continue
        s = panel[col]
        rows.append(
            {
                "field": col,
                "dtype": str(s.dtype),
                "non_null_rate_all": float(s.notna().mean()),
                "non_null_rate_common_window": float(panel.loc[panel["core48_common_window_eligible"], col].notna().mean()),
                "core12_non_null_rate": float(panel.loc[panel["track"].eq("baseline_core12_existing"), col].notna().mean()),
                "primary_addition_non_null_rate": float(panel.loc[panel["track"].eq("primary_core48_top36_addition"), col].notna().mean()),
            }
        )
    return pd.DataFrame(rows).sort_values(["non_null_rate_common_window", "field"], ascending=[True, True])


def build_schema_alignment(core12: pd.DataFrame, primary: pd.DataFrame) -> pd.DataFrame:
    all_cols = sorted(set(core12.columns) | set(primary.columns))
    rows = []
    for col in all_cols:
        rows.append(
            {
                "field": col,
                "in_core12": col in core12.columns,
                "in_primary_additions": col in primary.columns,
                "core12_dtype": str(core12[col].dtype) if col in core12.columns else "",
                "primary_dtype": str(primary[col].dtype) if col in primary.columns else "",
            }
        )
    return pd.DataFrame(rows)


def write_report(manifest: dict[str, Any], symbol_coverage: pd.DataFrame, field_coverage: pd.DataFrame, schema: pd.DataFrame) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    missing_common = symbol_coverage[~symbol_coverage["ready_for_common_window"]]
    primary_only_missing = schema[(~schema["in_core12"]) | (~schema["in_primary_additions"])]
    lines = [
        "# CRYPTO A7AC-3 Core48 Panel Integrity Audit",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "This is a data-line panel integrity and listing/survivorship audit. It does not authorize replay, formula search, large search, alpha proof, shadow, paper, or live trading.",
        "",
        "## Core48 Candidate Panel",
        "",
        "```text",
        f"output: {manifest['output_panel']}",
        f"rows: {manifest['rows']}",
        f"symbols: {manifest['symbols']}",
        f"columns: {manifest['columns']}",
        f"timestamp_min: {manifest['timestamp_min']}",
        f"timestamp_max: {manifest['timestamp_max']}",
        f"common_window: {manifest['common_window_start']} .. {manifest['common_window_end']}",
        f"common_window_rows: {manifest['common_window_rows']}",
        f"duplicate_key_count: {manifest['duplicate_key_count']}",
        "```",
        "",
        "## Listing / Survivorship Policy",
        "",
        "- `BOMEUSDT` starts at its available Binance Vision source boundary; 2024-01/02 source 404s remain explicit listing/source gaps.",
        "- Core48 historical replay must use the `core48_common_window_eligible` flag unless a test explicitly supports changing universe membership.",
        "- Rows after 2026-04-30 are not part of the current core48 common monthly-source historical window.",
        "",
        "## Symbol Coverage",
        "",
        table(symbol_coverage, max_rows=60),
        "",
        "## Symbols Not Ready For Common Window",
        "",
        table(missing_common, max_rows=60),
        "",
        "## Schema Mismatches",
        "",
        table(primary_only_missing, max_rows=80),
        "",
        "## Lowest Field Coverage In Common Window",
        "",
        table(field_coverage.head(40), max_rows=40),
        "",
        "## Authorization",
        "",
        "```text",
        f"authorizes_controlled_replay_prep: {str(manifest['authorizes_controlled_replay_prep']).lower()}",
        "authorizes_formula_search: false",
        "authorizes_large_search: false",
        "authorizes_alpha_proof: false",
        "authorizes_shadow_paper_live: false",
        "```",
        "",
        "## Next",
        "",
        "1. Define A7AD controlled replay prep using `core48_common_window_eligible` and explicit feature-family availability masks.",
        "2. Do not treat aggTrades fields as available for all 48 symbols; they remain core3/core12 specific depending on source coverage.",
        "3. Do not use tail rows outside the common window for fixed-split historical proof.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    registry = load_registry()
    core12 = pd.read_parquet(CORE12_PANEL)
    primary = pd.read_parquet(PRIMARY_PANEL)
    schema = build_schema_alignment(core12, primary)
    core12 = normalize_panel(core12, registry, "core12_aggtrades_metrics")
    primary = normalize_panel(primary, registry, "primary_additions_metrics")

    all_cols = sorted(set(core12.columns) | set(primary.columns))
    panel = pd.concat([core12.reindex(columns=all_cols), primary.reindex(columns=all_cols)], ignore_index=True)
    panel["timestamp"] = pd.to_datetime(panel["timestamp"], utc=True)
    panel["core48_member"] = panel["symbol"].isin(set(registry["symbol"]))
    panel["core48_common_window_eligible"] = panel["timestamp"].between(COMMON_WINDOW_START, COMMON_WINDOW_END, inclusive="both")
    panel = panel.sort_values(["timestamp", "symbol"]).reset_index(drop=True)
    panel = panel.replace([np.inf, -np.inf], np.nan)

    OUTPUT_PANEL.parent.mkdir(parents=True, exist_ok=True)
    panel.to_parquet(OUTPUT_PANEL, index=False, compression="zstd")

    symbol_coverage = build_symbol_coverage(panel, registry)
    field_coverage = build_field_coverage(panel)
    duplicate_key_count = int(panel.duplicated(["timestamp", "symbol"]).sum())
    all_symbols_ready = bool(symbol_coverage["ready_for_common_window"].all())
    blockers = []
    if duplicate_key_count:
        blockers.append("duplicate_timestamp_symbol_keys")
    if not all_symbols_ready:
        blockers.append("common_window_symbol_coverage_incomplete")
    decision = "PASS_A7AC3_CORE48_PANEL_READY_FOR_CONTROLLED_REPLAY_PREP" if not blockers else "HOLD_A7AC3_CORE48_PANEL_INTEGRITY_BLOCKERS"
    manifest = {
        "decision": decision,
        "generated_at": utc_now(),
        "blockers": blockers,
        "core12_panel": str(CORE12_PANEL),
        "primary_panel": str(PRIMARY_PANEL),
        "output_panel": str(OUTPUT_PANEL),
        "output_sha256": sha256_file(OUTPUT_PANEL),
        "rows": int(len(panel)),
        "symbols": int(panel["symbol"].nunique()),
        "columns": int(len(panel.columns)),
        "timestamp_min": str(panel["timestamp"].min()),
        "timestamp_max": str(panel["timestamp"].max()),
        "common_window_start": str(COMMON_WINDOW_START),
        "common_window_end": str(COMMON_WINDOW_END),
        "common_window_rows": int(panel["core48_common_window_eligible"].sum()),
        "duplicate_key_count": duplicate_key_count,
        "symbols_ready_for_common_window": int(symbol_coverage["ready_for_common_window"].sum()),
        "total_core48_symbols": int(len(registry)),
        "executes_search": False,
        "executes_replay": False,
        "authorizes_controlled_replay_prep": not blockers,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }

    symbol_coverage.to_csv(OUT_DIR / "a7ac3_symbol_coverage.csv", index=False)
    field_coverage.to_csv(OUT_DIR / "a7ac3_field_coverage.csv", index=False)
    schema.to_csv(OUT_DIR / "a7ac3_schema_alignment.csv", index=False)
    write_json(OUT_DIR / "a7ac3_manifest.json", manifest)
    write_report(manifest, symbol_coverage, field_coverage, schema)


if __name__ == "__main__":
    main()
