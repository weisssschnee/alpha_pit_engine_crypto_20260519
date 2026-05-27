from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(r"G:\AlphaFactory_CryptoData")

A7AC1_DIR = ROOT / "runtime" / "a7ac1_expanded_universe_backfill_contract"
TRACK_REGISTRY = A7AC1_DIR / "a7ac1_track_symbol_registry.csv"
SOURCE_REQUIREMENTS = A7AC1_DIR / "a7ac1_source_requirements.csv"
JOB_PLAN = A7AC1_DIR / "a7ac1_download_job_plan.csv"

PANELS_DIR = DATA_ROOT / "gold" / "panels"
FEATURES_DIR = DATA_ROOT / "gold" / "features"

KNOWN_GOLD_FILES = [
    PANELS_DIR / "crypto_core12_1h_v1.parquet",
    PANELS_DIR / "crypto_core12_1h_with_aggtrades_features_v1.parquet",
    PANELS_DIR / "crypto_core12_1h_with_aggtrades_metrics_features_v1.parquet",
    FEATURES_DIR / "binance_metrics_1h_features_v1.parquet",
    PANELS_DIR / "crypto_expanded_1h_v1.parquet",
    PANELS_DIR / "crypto_core48_1h_v1.parquet",
    PANELS_DIR / "crypto_liquid80_1h_v1.parquet",
]

OUT_DIR = ROOT / "runtime" / "a7ac2_preflight_current_coverage_gap_scan"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7AC2_PREFLIGHT_CURRENT_COVERAGE_GAP_SCAN_20260522.md"


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def table(df: pd.DataFrame, max_rows: int = 100) -> str:
    if df.empty:
        return "`<empty>`"
    return df.head(max_rows).to_markdown(index=False)


def parquet_symbol_inventory(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "path": str(path),
            "exists": False,
            "rows": 0,
            "columns": 0,
            "symbols": 0,
            "symbol_list": "",
            "timestamp_min": "",
            "timestamp_max": "",
            "read_error": "",
        }
    try:
        df = pd.read_parquet(path, columns=["symbol", "timestamp"])
        symbols = sorted(map(str, df["symbol"].dropna().unique()))
        return {
            "path": str(path),
            "exists": True,
            "rows": int(len(df)),
            "columns": int(len(pd.read_parquet(path, engine="pyarrow").columns)) if False else -1,
            "symbols": int(len(symbols)),
            "symbol_list": ",".join(symbols),
            "timestamp_min": str(df["timestamp"].min()),
            "timestamp_max": str(df["timestamp"].max()),
            "read_error": "",
        }
    except Exception as exc:  # noqa: BLE001 - audit should record, not crash
        return {
            "path": str(path),
            "exists": True,
            "rows": 0,
            "columns": 0,
            "symbols": 0,
            "symbol_list": "",
            "timestamp_min": "",
            "timestamp_max": "",
            "read_error": repr(exc),
        }


def build_gold_inventory() -> pd.DataFrame:
    rows = []
    for path in KNOWN_GOLD_FILES:
        row = parquet_symbol_inventory(path)
        row["dataset"] = path.stem
        rows.append(row)
    return pd.DataFrame(rows)


def build_symbol_gap_matrix(track_registry: pd.DataFrame, gold_inventory: pd.DataFrame) -> pd.DataFrame:
    present_by_dataset: dict[str, set[str]] = {}
    for _, r in gold_inventory.iterrows():
        present_by_dataset[r["dataset"]] = set(str(r.get("symbol_list", "")).split(",")) if r.get("symbol_list", "") else set()

    core12_panel_symbols = present_by_dataset.get("crypto_core12_1h_v1", set())
    agg_metrics_symbols = present_by_dataset.get("crypto_core12_1h_with_aggtrades_metrics_features_v1", set())
    metrics_symbols = present_by_dataset.get("binance_metrics_1h_features_v1", set())
    expanded_symbols = (
        present_by_dataset.get("crypto_expanded_1h_v1", set())
        | present_by_dataset.get("crypto_core48_1h_v1", set())
        | present_by_dataset.get("crypto_liquid80_1h_v1", set())
    )

    rows = []
    for _, r in track_registry.iterrows():
        symbol = str(r["symbol"])
        rows.append(
            {
                "symbol": symbol,
                "track": r["track"],
                "tier": r["tier"],
                "priority": r["priority"],
                "in_core12_base_panel": symbol in core12_panel_symbols,
                "in_core12_agg_metrics_panel": symbol in agg_metrics_symbols,
                "in_metrics_gold": symbol in metrics_symbols,
                "in_any_expanded_gold_panel": symbol in expanded_symbols,
                "p0_backfill_needed": bool(r["track"] != "baseline_core12_existing" and symbol not in expanded_symbols),
                "a7ac2_status": "READY_EXISTING_CORE12" if r["track"] == "baseline_core12_existing" else ("READY_EXPANDED_PANEL_PRESENT" if symbol in expanded_symbols else "MISSING_P0_EXPANDED_PANEL"),
            }
        )
    return pd.DataFrame(rows)


def build_batch_plan(job_plan: pd.DataFrame) -> pd.DataFrame:
    p0 = job_plan[job_plan["priority"].eq("P0")].copy()
    p0 = p0[p0["job_group"].eq("primary_core48_top36_addition")].copy()
    source_order = {
        "futures_trade_klines_1m": 1,
        "mark_price_klines_1m": 2,
        "index_price_klines_1m": 3,
        "premium_index_klines_1m": 4,
        "funding_rate": 5,
        "binance_metrics_daily": 6,
    }
    p0["source_order"] = p0["source_family"].map(source_order).fillna(99).astype(int)
    p0 = p0.sort_values(["source_order", "symbol"])
    p0["batch_id"] = ((range(len(p0))))
    p0["batch_id"] = p0["batch_id"].map(lambda i: f"P0B{int(i) // 36 + 1:02d}")
    p0["checkpoint_group"] = p0["batch_id"]
    p0["execution_note"] = "download/build source family for all primary additions, then run source trace audit"
    return p0.drop(columns=["source_order"])


def build_readiness(
    track_registry: pd.DataFrame,
    gap: pd.DataFrame,
    gold_inventory: pd.DataFrame,
    batch_plan: pd.DataFrame,
) -> dict[str, Any]:
    missing_primary = int(gap[gap["track"].eq("primary_core48_top36_addition")]["p0_backfill_needed"].sum())
    expanded_panel_exists = bool(gold_inventory[gold_inventory["dataset"].isin(["crypto_expanded_1h_v1", "crypto_core48_1h_v1", "crypto_liquid80_1h_v1"])]["exists"].any())
    return {
        "decision": "HOLD_A7AC2_PREFLIGHT_EXPANDED_PANEL_NOT_PRESENT",
        "generated_at": utc_stamp(),
        "executes_download": False,
        "executes_panel_build": False,
        "executes_search": False,
        "executes_replay": False,
        "core12_existing_symbols": int(track_registry["track"].eq("baseline_core12_existing").sum()),
        "primary_addition_symbols": int(track_registry["track"].eq("primary_core48_top36_addition").sum()),
        "secondary_pool_symbols": int(track_registry["track"].eq("secondary_liquid80_eligible_pool").sum()),
        "expanded_gold_panel_exists": expanded_panel_exists,
        "primary_additions_missing_p0_panel": missing_primary,
        "p0_batch_jobs": int(len(batch_plan)),
        "authorizes_data_line_execution": True,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "required_next": [
            "Execute P0B01-P0B06 backfill batches for primary_core48 additions",
            "Build crypto_expanded_1h_v1 or crypto_core48_1h_v1 gold panel",
            "Run A7AC-2 full source trace/panel integrity audit after expanded panel exists",
            "Run A7AC-3 listing/survivorship policy before any replay",
        ],
    }


def write_report(
    readiness: dict[str, Any],
    gold_inventory: pd.DataFrame,
    gap: pd.DataFrame,
    batch_plan: pd.DataFrame,
) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    missing = gap[gap["p0_backfill_needed"].eq(True)].copy()
    lines = [
        "# CRYPTO A7AC-2 Preflight Current Coverage Gap Scan",
        "",
        f"Generated: {readiness['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{readiness['decision']}`",
        "",
        "A7AC-2 preflight checks what already exists locally and converts the A7AC-1 contract into concrete P0 backfill batches. It does not download data, build panels, run replay, or authorize search.",
        "",
        "## Current Gold Inventory",
        "",
        table(gold_inventory, max_rows=20),
        "",
        "## Symbol Gap Summary",
        "",
        table(
            gap.groupby(["track", "a7ac2_status"], dropna=False)
            .agg(symbols=("symbol", "nunique"), p0_backfill_needed=("p0_backfill_needed", "sum"))
            .reset_index(),
            max_rows=20,
        ),
        "",
        "## Missing Primary Additions",
        "",
        table(missing[["symbol", "tier", "priority", "a7ac2_status"]], max_rows=80),
        "",
        "## P0 Backfill Batch Plan",
        "",
        table(
            batch_plan.groupby(["batch_id", "source_family"], dropna=False)
            .agg(jobs=("symbol", "size"), symbols=("symbol", lambda s: ",".join(sorted(set(map(str, s))))))
            .reset_index(),
            max_rows=20,
        ),
        "",
        "## Authorization",
        "",
        table(pd.DataFrame([readiness])),
        "",
        "## Required Next Action",
        "",
        "1. Data line runs P0B01-P0B06 for the 36 primary additions.",
        "2. Build an expanded 1h gold panel only after raw/source traces are closed.",
        "3. Re-run this A7AC-2 script; decision should move from HOLD to panel-integrity audit if expanded panel exists.",
        "4. Do not run formula search until A7AC-2 panel audit and A7AC-3 listing/survivorship policy pass.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    track_registry = pd.read_csv(TRACK_REGISTRY)
    job_plan = pd.read_csv(JOB_PLAN)
    gold_inventory = build_gold_inventory()
    gap = build_symbol_gap_matrix(track_registry, gold_inventory)
    batch_plan = build_batch_plan(job_plan)
    readiness = build_readiness(track_registry, gap, gold_inventory, batch_plan)
    manifest = {
        "decision": readiness["decision"],
        "generated_at": readiness["generated_at"],
        "executes_download": False,
        "executes_panel_build": False,
        "executes_search": False,
        "executes_replay": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
    }

    gold_inventory.to_csv(OUT_DIR / "a7ac2_current_gold_inventory.csv", index=False)
    gap.to_csv(OUT_DIR / "a7ac2_symbol_source_gap_matrix.csv", index=False)
    batch_plan.to_csv(OUT_DIR / "a7ac2_p0_backfill_batches.csv", index=False)
    write_json(OUT_DIR / "a7ac2_readiness.json", readiness)
    write_json(OUT_DIR / "a7ac2_manifest.json", manifest)
    write_report(readiness, gold_inventory, gap, batch_plan)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
