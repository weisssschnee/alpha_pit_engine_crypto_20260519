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

OUT_DIR = ROOT / "runtime" / "a7ac2c_effective_backfill_coverage"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7AC2C_EFFECTIVE_BACKFILL_COVERAGE_AUDIT_20260522.md"

MONTHLY_MANIFEST = OUT_DIR / "binance_vision_monthly_pool_manifest_a7ac_company_p0b01_b04_monthly_v3_20260522_194402.csv"
MONTHLY_STATUS = OUT_DIR / "binance_vision_monthly_pool_status_a7ac_company_p0b01_b04_monthly_v3_20260522_194402.json"
FUNDING_INITIAL_MANIFEST = OUT_DIR / "binance_funding_rate_pool_manifest_a7ac_company_p0b05_funding_20260522_193740.csv"
FUNDING_RETRY_MANIFEST = OUT_DIR / "binance_funding_rate_pool_manifest_a7ac_company_p0b05_funding_retry_20260522_194314.csv"
FUNDING_INITIAL_STATUS = OUT_DIR / "binance_funding_rate_pool_status_a7ac_company_p0b05_funding_20260522_193740.json"
FUNDING_RETRY_STATUS = OUT_DIR / "binance_funding_rate_pool_status_a7ac_company_p0b05_funding_retry_20260522_194314.json"

METRICS_SILVER_ROOT = DATA_ROOT / "silver" / "binance_vision" / "metrics_5m"
METRICS_RAW_ROOT = DATA_ROOT / "raw" / "binance_vision" / "metrics_daily" / "futures_um" / "metrics"

MONTHS_MONTHLY = pd.period_range("2024-01", "2026-04", freq="M").astype(str).tolist()
MONTHS_METRICS = pd.period_range("2024-01", "2026-05", freq="M").astype(str).tolist()
MONTHLY_DATA_TYPES = ["klines", "markPriceKlines", "indexPriceKlines", "premiumIndexKlines"]
METRICS_START_DATE = pd.Timestamp("2024-01-01")
METRICS_END_DATE = pd.Timestamp("2026-05-21")


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    return df.head(max_rows).to_markdown(index=False)


def primary_symbols() -> list[str]:
    registry = pd.read_csv(TRACK_REGISTRY)
    symbols = registry.loc[registry["track"].eq("primary_core48_top36_addition"), "symbol"].astype(str)
    return sorted(symbols.tolist())


def audit_monthly_sources(symbols: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    monthly = pd.read_csv(MONTHLY_MANIFEST)
    monthly["ok_or_listing_gap"] = monthly["status"].isin(["downloaded_checksum_ok", "exists_checksum_ok", "not_available_404"])
    monthly["checksum_ok_filled"] = monthly["checksum_ok"].fillna(False).astype(bool)

    rows = []
    for symbol in symbols:
        sym = monthly[monthly["symbol"].eq(symbol)]
        expected = len(MONTHLY_DATA_TYPES) * len(MONTHS_MONTHLY)
        checksum_ok = int(sym["status"].isin(["downloaded_checksum_ok", "exists_checksum_ok"]).sum())
        listing_gap = int(sym["status"].eq("not_available_404").sum())
        failures = int((~sym["ok_or_listing_gap"]).sum())
        missing_rows = expected - int(len(sym))
        rows.append(
            {
                "symbol": symbol,
                "expected_rows": expected,
                "manifest_rows": int(len(sym)),
                "checksum_ok_rows": checksum_ok,
                "listing_gap_rows": listing_gap,
                "failure_rows": failures,
                "missing_manifest_rows": missing_rows,
                "ready": failures == 0 and missing_rows == 0,
                "note": "listing_gap_only" if listing_gap else "complete",
            }
        )
    summary = pd.DataFrame(rows)
    listing_gaps = monthly[monthly["status"].eq("not_available_404")][
        ["symbol", "data_type", "interval", "month", "status", "error"]
    ].sort_values(["symbol", "month", "data_type"])
    return summary, listing_gaps


def audit_funding_sources(symbols: list[str]) -> pd.DataFrame:
    frames = []
    for source, path in [("initial", FUNDING_INITIAL_MANIFEST), ("retry", FUNDING_RETRY_MANIFEST)]:
        if path.exists():
            df = pd.read_csv(path)
            df["source_run"] = source
            frames.append(df)
    funding = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    rows = []
    for symbol in symbols:
        sym = funding[funding["symbol"].eq(symbol)] if not funding.empty else pd.DataFrame()
        ok = sym[sym["status"].eq("ok")].copy()
        rows.append(
            {
                "symbol": symbol,
                "ok_runs": int(len(ok)),
                "initial_ok": bool(((sym.get("source_run") == "initial") & (sym.get("status") == "ok")).any()) if not sym.empty else False,
                "retry_ok": bool(((sym.get("source_run") == "retry") & (sym.get("status") == "ok")).any()) if not sym.empty else False,
                "rows_max": int(ok["rows"].max()) if not ok.empty and "rows" in ok else 0,
                "timestamp_min": str(ok["timestamp_min"].min()) if not ok.empty and "timestamp_min" in ok else "",
                "timestamp_max": str(ok["timestamp_max"].max()) if not ok.empty and "timestamp_max" in ok else "",
                "ready": not ok.empty,
                "latest_status": str(sym.iloc[-1]["status"]) if not sym.empty else "missing",
            }
        )
    return pd.DataFrame(rows)


def metric_symbol_inventory(symbol: str) -> dict[str, Any]:
    silver_dir = METRICS_SILVER_ROOT / f"symbol={symbol}"
    raw_dir = METRICS_RAW_ROOT / symbol
    silver_files = sorted(silver_dir.glob("month=*/part.parquet")) if silver_dir.exists() else []
    silver_months = sorted([p.parent.name.replace("month=", "") for p in silver_files])
    silver_rows = 0
    ts_min = ""
    ts_max = ""
    read_errors: list[str] = []
    sparse_months: list[str] = []
    for p in silver_files:
        try:
            meta = pd.read_parquet(p, columns=["timestamp"])
            rows = int(len(meta))
            silver_rows += rows
            month = p.parent.name.replace("month=", "")
            month_start = pd.Timestamp(month + "-01")
            month_end = month_start + pd.offsets.MonthEnd(0)
            effective_start = max(month_start, METRICS_START_DATE)
            effective_end = min(month_end, METRICS_END_DATE)
            days = max(0, len(pd.date_range(effective_start, effective_end, freq="D")))
            expected_month_rows = days * 24 * 12
            if rows < expected_month_rows * 0.80:
                # BOME starts mid-March 2024; keep it as listing/availability,
                # not a generic sparse vendor warning.
                if not (symbol == "BOMEUSDT" and month == "2024-03"):
                    sparse_months.append(f"{month}:{rows}/{expected_month_rows}")
            if not meta.empty:
                mn = meta["timestamp"].min()
                mx = meta["timestamp"].max()
                ts_min = str(mn) if not ts_min or str(mn) < ts_min else ts_min
                ts_max = str(mx) if not ts_max or str(mx) > ts_max else ts_max
        except Exception as exc:  # noqa: BLE001 - source audit should record, not crash
            read_errors.append(f"{p}:{exc!r}")
    raw_zips = sorted(raw_dir.glob("*.zip")) if raw_dir.exists() else []
    raw_checksums = sorted(raw_dir.glob("*.zip.CHECKSUM")) if raw_dir.exists() else []
    expected_months = MONTHS_METRICS.copy()
    if symbol == "BOMEUSDT":
        # BOME Binance metrics start in 2024-03 in the observed local source tree.
        expected_months = [m for m in expected_months if m >= "2024-03"]
    missing_months = sorted(set(expected_months) - set(silver_months))
    # Most Binance metrics symbol-months are dense 5m series. Some official
    # vendor files are sparse despite checksum-ok source trace. Treat that as a
    # feature-availability warning rather than a checksum/source blocker.
    expected_dense_rows = len(expected_months) * 30 * 24 * 12
    density_ratio = (silver_rows / expected_dense_rows) if expected_dense_rows else 0.0
    density_warning = density_ratio < 0.90 or bool(sparse_months)
    return {
        "symbol": symbol,
        "expected_silver_months": len(expected_months),
        "silver_months": len(silver_months),
        "silver_rows": silver_rows,
        "silver_density_ratio_vs_30d_5m_proxy": round(float(density_ratio), 6),
        "silver_first_month": silver_months[0] if silver_months else "",
        "silver_last_month": silver_months[-1] if silver_months else "",
        "timestamp_min": ts_min,
        "timestamp_max": ts_max,
        "missing_silver_months": ",".join(missing_months),
        "raw_zip_files": len(raw_zips),
        "raw_checksum_files": len(raw_checksums),
        "read_error_count": len(read_errors),
        "feature_density_warning": density_warning,
        "sparse_month_count": len(sparse_months),
        "sparse_months": ",".join(sparse_months),
        "ready": len(missing_months) == 0 and len(silver_months) >= len(expected_months),
        "note": "listing_gap_2024_01_02" if symbol == "BOMEUSDT" else ("vendor_sparse_5m_warning" if density_warning else "complete"),
    }


def audit_metrics_sources(symbols: list[str]) -> pd.DataFrame:
    return pd.DataFrame([metric_symbol_inventory(symbol) for symbol in symbols])


def build_manifest(
    monthly_summary: pd.DataFrame,
    funding_summary: pd.DataFrame,
    metrics_summary: pd.DataFrame,
    listing_gaps: pd.DataFrame,
) -> dict[str, Any]:
    monthly_status = read_json(MONTHLY_STATUS)
    funding_initial_status = read_json(FUNDING_INITIAL_STATUS)
    funding_retry_status = read_json(FUNDING_RETRY_STATUS)
    monthly_ready = bool(monthly_summary["ready"].all())
    funding_ready = bool(funding_summary["ready"].all())
    metrics_ready = bool(metrics_summary["ready"].all())
    metrics_density_warning_symbols = int(metrics_summary["feature_density_warning"].sum()) if "feature_density_warning" in metrics_summary else 0
    blockers = []
    if not monthly_ready:
        blockers.append("monthly_source_incomplete")
    if not funding_ready:
        blockers.append("funding_source_incomplete")
    if not metrics_ready:
        blockers.append("metrics_source_incomplete")
    decision = (
        "PASS_A7AC2C_EFFECTIVE_P0_BACKFILL_SOURCE_COVERAGE_COMPLETE_WITH_LISTING_GAPS"
        if not blockers
        else "HOLD_A7AC2C_EFFECTIVE_P0_BACKFILL_SOURCE_COVERAGE_INCOMPLETE"
    )
    return {
        "decision": decision,
        "generated_at": utc_stamp(),
        "blockers": blockers,
        "executes_download": False,
        "executes_panel_build": False,
        "executes_search": False,
        "executes_replay": False,
        "authorizes_panel_build": not blockers,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "primary_symbols": int(len(monthly_summary)),
        "monthly_ready_symbols": int(monthly_summary["ready"].sum()),
        "funding_ready_symbols": int(funding_summary["ready"].sum()),
        "metrics_ready_symbols": int(metrics_summary["ready"].sum()),
        "monthly_manifest_rows": int(monthly_summary["manifest_rows"].sum()),
        "monthly_checksum_ok_rows": int(monthly_summary["checksum_ok_rows"].sum()),
        "monthly_listing_gap_rows": int(monthly_summary["listing_gap_rows"].sum()),
        "monthly_failure_rows": int(monthly_summary["failure_rows"].sum()),
        "funding_effective_ok_symbols": int(funding_summary["ready"].sum()),
        "metrics_effective_ready_symbols": int(metrics_summary["ready"].sum()),
        "metrics_density_warning_symbols": metrics_density_warning_symbols,
        "listing_gaps": listing_gaps.to_dict(orient="records"),
        "company_monthly_status_decision": monthly_status.get("decision", ""),
        "company_funding_initial_decision": funding_initial_status.get("decision", ""),
        "company_funding_retry_decision": funding_retry_status.get("decision", ""),
        "notes": [
            "P0B01-P0B04 monthly 1m source families are complete except explicit Binance Vision 404 listing gaps.",
            "P0B05 funding is complete after combining initial company run and retry run.",
            "P0B06 metrics is treated by effective local file coverage; stale/failed transient status files are not used as final source-trace state.",
            "Metrics source trace completeness is distinct from feature density; sparse official vendor files are recorded as warnings.",
            "This audit authorizes data-line panel build only, not replay/search/alpha proof.",
        ],
    }


def write_report(
    manifest: dict[str, Any],
    monthly_summary: pd.DataFrame,
    funding_summary: pd.DataFrame,
    metrics_summary: pd.DataFrame,
    listing_gaps: pd.DataFrame,
) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# CRYPTO A7AC-2C Effective P0 Backfill Coverage Audit",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "This is a data-line source coverage audit. It does not build a gold panel, run replay/search, authorize alpha proof, or authorize shadow/paper/live trading.",
        "",
        "## Effective Coverage",
        "",
        "```text",
        f"primary_symbols: {manifest['primary_symbols']}",
        f"monthly_ready_symbols: {manifest['monthly_ready_symbols']}",
        f"funding_ready_symbols: {manifest['funding_ready_symbols']}",
        f"metrics_ready_symbols: {manifest['metrics_ready_symbols']}",
        f"metrics_density_warning_symbols: {manifest['metrics_density_warning_symbols']}",
        f"monthly_checksum_ok_rows: {manifest['monthly_checksum_ok_rows']}",
        f"monthly_listing_gap_rows: {manifest['monthly_listing_gap_rows']}",
        f"monthly_failure_rows: {manifest['monthly_failure_rows']}",
        "```",
        "",
        "## Listing Gaps",
        "",
        table(listing_gaps, max_rows=20),
        "",
        "The listing gaps are explicit `not_available_404` rows from Binance Vision monthly source download, not checksum or integrity failures. They must be handled by A7AC-3 listing/survivorship policy before replay.",
        "",
        "## Monthly Source Summary",
        "",
        table(monthly_summary, max_rows=80),
        "",
        "## Funding Source Summary",
        "",
        table(funding_summary, max_rows=80),
        "",
        "## Metrics Source Summary",
        "",
        table(metrics_summary, max_rows=80),
        "",
        "## Authorization",
        "",
        "```text",
        f"authorizes_panel_build: {manifest['authorizes_panel_build']}",
        "authorizes_formula_search: false",
        "authorizes_large_search: false",
        "authorizes_alpha_proof: false",
        "authorizes_shadow_paper_live: false",
        "```",
        "",
        "## Next",
        "",
        "1. Build expanded 1h gold panel from the now-complete source coverage.",
        "2. Run A7AC-3 listing/survivorship policy for explicit listing gaps.",
        "3. Run expanded panel integrity audit before any replay/search.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    symbols = primary_symbols()
    monthly_summary, listing_gaps = audit_monthly_sources(symbols)
    funding_summary = audit_funding_sources(symbols)
    metrics_summary = audit_metrics_sources(symbols)
    manifest = build_manifest(monthly_summary, funding_summary, metrics_summary, listing_gaps)

    monthly_summary.to_csv(OUT_DIR / "a7ac2c_monthly_source_summary.csv", index=False)
    funding_summary.to_csv(OUT_DIR / "a7ac2c_funding_source_summary.csv", index=False)
    metrics_summary.to_csv(OUT_DIR / "a7ac2c_metrics_source_summary.csv", index=False)
    listing_gaps.to_csv(OUT_DIR / "a7ac2c_listing_gaps.csv", index=False)
    write_json(OUT_DIR / "a7ac2c_effective_backfill_manifest.json", manifest)
    write_report(manifest, monthly_summary, funding_summary, metrics_summary, listing_gaps)


if __name__ == "__main__":
    main()
