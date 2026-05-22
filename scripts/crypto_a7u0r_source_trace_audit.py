from __future__ import annotations

import calendar
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(r"G:\AlphaFactory_CryptoData")
MANIFEST_DIR = DATA_ROOT / "manifests"
REPORT_DIR = DATA_ROOT / "reports"
AGG_ROOT = DATA_ROOT / "gold" / "microstructure" / "aggtrades_1h_flow_enhanced_v1"
FEATURE_ROOT = DATA_ROOT / "gold" / "features" / "aggtrades_enhanced_features_v1"
PANEL_PATH = DATA_ROOT / "gold" / "panels" / "crypto_core12_1h_with_aggtrades_features_v1.parquet"

OUT_DIR = ROOT / "runtime" / "a7u0r_source_trace_audit"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7U0R_SOURCE_TRACE_AUDIT_20260522.md"

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
MONTHLY_MONTHS = pd.period_range("2024-01", "2026-04", freq="M").astype(str).tolist()
DAILY_MONTH = "2026-05"


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    return df.head(max_rows).to_markdown(index=False)


def clean_float(value: Any) -> float | None:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def expected_hours(month: str) -> int:
    year, mon = [int(x) for x in month.split("-")]
    return calendar.monthrange(year, mon)[1] * 24


def latest_file(pattern: str) -> Path | None:
    files = sorted(MANIFEST_DIR.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def latest_report(pattern: str) -> Path | None:
    files = sorted(REPORT_DIR.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def parse_partition(path: Path) -> tuple[str, str]:
    return path.parent.parent.name.split("=", 1)[1], path.parent.name.split("=", 1)[1]


def load_monthly_conversion_manifest() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for path in sorted(MANIFEST_DIR.glob("aggtrades_hourly_enhanced_v1_*.csv")):
        df = pd.read_csv(path)
        if {"symbol", "month", "out_path", "hourly_rows"}.issubset(df.columns):
            df["conversion_manifest"] = path.name
            frames.append(df)
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True)
    out["run_time_sort"] = pd.to_datetime(out.get("run_time"), utc=True, errors="coerce")
    out = out.sort_values(["symbol", "month", "run_time_sort", "conversion_manifest"])
    out = out.drop_duplicates(["symbol", "month"], keep="last")
    return out


def load_raw_monthly_manifest() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    patterns = [
        "aggtrades_raw_latest_roundrobin_*.csv",
        "aggtrades_raw_only_*.csv",
        "aggtrades_package_a_core3_*.csv",
    ]
    for pattern in patterns:
        for path in sorted(MANIFEST_DIR.glob(pattern)):
            df = pd.read_csv(path)
            month_col = "month" if "month" in df.columns else "date_range" if "date_range" in df.columns else None
            if month_col is None or "symbol" not in df.columns:
                continue
            cols = [c for c in ["source_url", "download_time", "symbol", month_col, "local_path", "file_size", "sha256", "official_checksum", "checksum_status", "status", "error"] if c in df.columns]
            part = df[cols].copy().rename(columns={month_col: "month"})
            part["raw_manifest"] = path.name
            frames.append(part)
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True)
    out["download_time_sort"] = pd.to_datetime(out.get("download_time"), utc=True, errors="coerce")
    status_rank = out["checksum_status"].eq("ok").astype(int) + out["status"].isin(["downloaded", "exists"]).astype(int)
    out["status_rank"] = status_rank
    out = out.sort_values(["symbol", "month", "status_rank", "download_time_sort", "raw_manifest"])
    out = out.drop_duplicates(["symbol", "month"], keep="last")
    return out


def load_daily_manifest() -> tuple[pd.DataFrame, Path | None]:
    path = latest_file("aggtrades_daily_current_month_enhanced_*_company.csv")
    if path is None:
        return pd.DataFrame(), None
    df = pd.read_csv(path)
    if df.empty:
        return df, path
    df["month"] = pd.to_datetime(df["date"], utc=True, errors="coerce").dt.strftime("%Y-%m")
    grouped = (
        df.groupby(["symbol", "month"])
        .agg(
            raw_daily_rows=("date", "count"),
            raw_daily_checksum_ok=("checksum_status", lambda s: int((s == "ok").sum())),
            raw_daily_status_downloaded=("status", lambda s: int(s.isin(["downloaded", "exists"]).sum())),
            raw_daily_file_size_sum=("file_size", lambda s: int(pd.to_numeric(s, errors="coerce").fillna(0).sum())),
            raw_daily_rows_sum=("rows", lambda s: int(pd.to_numeric(s, errors="coerce").fillna(0).sum())),
            raw_daily_error_count=("error", lambda s: int(s.fillna("").astype(str).ne("").sum())),
        )
        .reset_index()
    )
    grouped["raw_daily_manifest"] = path.name
    return grouped, path


def audit_partitions() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for path in sorted(AGG_ROOT.rglob("part.parquet")):
        symbol, month = parse_partition(path)
        try:
            df = pd.read_parquet(path, columns=["timestamp", "symbol", "month", "source", "aggregation"])
            ts = pd.to_datetime(df["timestamp"], utc=True)
            source_values = ";".join(sorted(df["source"].astype(str).unique())) if "source" in df else ""
            aggregation_values = ";".join(sorted(df["aggregation"].astype(str).unique())) if "aggregation" in df else ""
            rows.append(
                {
                    "symbol": symbol,
                    "month": month,
                    "agg_partition_path": str(path),
                    "agg_partition_exists": True,
                    "agg_partition_rows": int(len(df)),
                    "agg_timestamp_min": ts.min().strftime("%Y-%m-%dT%H:%M:%SZ") if len(ts) else "",
                    "agg_timestamp_max": ts.max().strftime("%Y-%m-%dT%H:%M:%SZ") if len(ts) else "",
                    "agg_duplicate_timestamp_count": int(ts.duplicated().sum()),
                    "agg_symbol_column_ok": bool((df["symbol"].astype(str) == symbol).all()) if "symbol" in df else False,
                    "agg_month_column_ok": bool((df["month"].astype(str) == month).all()) if "month" in df else False,
                    "agg_source_values": source_values,
                    "agg_aggregation_values": aggregation_values,
                }
            )
        except Exception as exc:  # noqa: BLE001
            rows.append(
                {
                    "symbol": symbol,
                    "month": month,
                    "agg_partition_path": str(path),
                    "agg_partition_exists": True,
                    "agg_partition_error": f"{type(exc).__name__}: {exc}",
                }
            )
    return pd.DataFrame(rows)


def build_trace() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    expected = pd.MultiIndex.from_product([SYMBOLS, MONTHLY_MONTHS + [DAILY_MONTH]], names=["symbol", "month"]).to_frame(index=False)
    monthly_conv = load_monthly_conversion_manifest()
    raw_monthly = load_raw_monthly_manifest()
    daily_summary, _ = load_daily_manifest()
    partitions = audit_partitions()
    trace = expected.merge(monthly_conv, on=["symbol", "month"], how="left", suffixes=("", "_conversion"))
    raw_cols = [c for c in raw_monthly.columns if c not in {"symbol", "month"}]
    trace = trace.merge(raw_monthly[["symbol", "month"] + raw_cols], on=["symbol", "month"], how="left")
    daily_cols = [c for c in daily_summary.columns if c not in {"symbol", "month"}]
    trace = trace.merge(daily_summary[["symbol", "month"] + daily_cols], on=["symbol", "month"], how="left")
    part_cols = [c for c in partitions.columns if c not in {"symbol", "month"}]
    trace = trace.merge(partitions[["symbol", "month"] + part_cols], on=["symbol", "month"], how="left")

    trace["expected_hours"] = trace["month"].map(lambda m: 480 if m == DAILY_MONTH else expected_hours(m))
    trace["is_daily_current_month"] = trace["month"].eq(DAILY_MONTH)
    trace["conversion_written"] = trace.get("status", pd.Series(index=trace.index, dtype=str)).fillna("").eq("written")
    trace["agg_partition_exists"] = trace["agg_partition_exists"].fillna(False).astype(bool)
    trace["agg_rows_match_expected"] = pd.to_numeric(trace["agg_partition_rows"], errors="coerce").fillna(-1).astype(int).eq(trace["expected_hours"])
    monthly_checksum_ok = trace.get("checksum_status", pd.Series(index=trace.index, dtype=str)).fillna("").eq("ok")
    daily_checksum_ok = (
        pd.to_numeric(trace.get("raw_daily_checksum_ok", pd.Series(index=trace.index, dtype=float)), errors="coerce").fillna(0)
        .eq(pd.to_numeric(trace.get("raw_daily_rows", pd.Series(index=trace.index, dtype=float)), errors="coerce").fillna(-1))
        & pd.to_numeric(trace.get("raw_daily_rows", pd.Series(index=trace.index, dtype=float)), errors="coerce").fillna(0).gt(0)
    )
    trace["raw_checksum_ok"] = (monthly_checksum_ok & ~trace["is_daily_current_month"]) | (daily_checksum_ok & trace["is_daily_current_month"])
    trace["raw_trace_class"] = "missing_raw_checksum_manifest"
    trace.loc[trace["raw_checksum_ok"], "raw_trace_class"] = "raw_checksum_ok"
    trace.loc[
        ~trace["is_daily_current_month"]
        & trace.get("checksum_status", pd.Series(index=trace.index, dtype=str)).fillna("").ne("")
        & ~trace["raw_checksum_ok"],
        "raw_trace_class",
    ] = "raw_checksum_not_ok"
    trace.loc[
        trace["is_daily_current_month"]
        & trace.get("raw_daily_rows", pd.Series(index=trace.index, dtype=float)).notna()
        & ~trace["raw_checksum_ok"],
        "raw_trace_class",
    ] = "raw_daily_checksum_not_complete"
    trace["source_trace_ready"] = (
        trace["agg_partition_exists"]
        & trace["agg_rows_match_expected"]
        & trace["raw_checksum_ok"]
        & trace.get("agg_symbol_column_ok", pd.Series(index=trace.index, dtype=bool)).fillna(False).astype(bool)
        & trace.get("agg_month_column_ok", pd.Series(index=trace.index, dtype=bool)).fillna(False).astype(bool)
        & pd.to_numeric(trace.get("agg_duplicate_timestamp_count", pd.Series(index=trace.index, dtype=float)), errors="coerce").fillna(999).eq(0)
    )
    trace["source_trace_decision"] = trace["source_trace_ready"].map({True: "PASS_A7U0R_SOURCE_TRACE_ROW", False: "HOLD_A7U0R_SOURCE_TRACE_ROW"})

    status = (
        trace.groupby(["raw_trace_class", "source_trace_decision"])
        .size()
        .reset_index(name="rows")
        .sort_values(["raw_trace_class", "source_trace_decision"])
    )
    by_symbol = (
        trace.groupby("symbol")
        .agg(
            rows=("month", "count"),
            ready=("source_trace_ready", "sum"),
            raw_checksum_ok=("raw_checksum_ok", "sum"),
            partitions=("agg_partition_exists", "sum"),
            row_hours=("agg_partition_rows", "sum"),
        )
        .reset_index()
    )
    return trace, status, by_symbol


def load_json(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def panel_lineage_summary() -> pd.DataFrame:
    agg_report_path = latest_report("aggtrades_enhanced_features_v1_*.json")
    panel_report_path = latest_report("crypto_core12_1h_with_aggtrades_features_v1_*.json")
    rows = []
    for name, path in [
        ("aggtrades_enhanced_features_v1", agg_report_path),
        ("crypto_core12_1h_with_aggtrades_features_v1", panel_report_path),
    ]:
        payload = load_json(path)
        rows.append(
            {
                "artifact": name,
                "report_path": str(path) if path else "",
                "generated_at": payload.get("generated_at", ""),
                "input_root_or_panel": payload.get("input_root", payload.get("input_panel", "")),
                "input_agg_root": payload.get("input_agg_root", ""),
                "output": payload.get("output", payload.get("output_root", "")),
                "rows": payload.get("rows", payload.get("output_rows", "")),
                "columns": len(payload.get("columns", [])) if isinstance(payload.get("columns"), list) else payload.get("output_columns", ""),
                "agg_rows": payload.get("agg_rows", ""),
                "agg_symbol_month_count": payload.get("agg_symbol_month_count", payload.get("symbol_month_count", "")),
            }
        )
    return pd.DataFrame(rows)


def write_report(now: str, trace: pd.DataFrame, status: pd.DataFrame, by_symbol: pd.DataFrame, lineage: pd.DataFrame, authorization: dict[str, Any]) -> None:
    missing = trace[~trace["source_trace_ready"]].copy()
    cols = [
        "symbol",
        "month",
        "raw_trace_class",
        "checksum_status",
        "raw_manifest",
        "raw_daily_manifest",
        "conversion_manifest",
        "agg_partition_exists",
        "agg_partition_rows",
        "expected_hours",
        "source_trace_decision",
    ]
    if authorization["blockers"]:
        interpretation = [
            "- Enhanced hourly partitions exist for the expected core3 symbol-month rows, including the current partial May daily extension.",
            "- Daily May rows have checksum status from the daily download manifest.",
            "- Several historical monthly rows lack complete raw checksum manifest coverage or have non-ok checksum status in the available local manifest set. These rows can be used for controlled experiments only under the existing panel acceptance boundary, not for final raw-level proof claims.",
            "- The unified panel can remain the A7V experiment input, but final panel claims require resolving the raw checksum trace gaps listed above.",
        ]
        required_next = [
            "- Ask data line to provide or regenerate raw checksum manifests for the HOLD rows, especially early 2024 ETH/SOL and any monthly checksum mismatch rows.",
            "- Do not use A7V/A7U to claim final raw-level panel proof until all source-trace rows pass.",
            "- Continue controlled experiments only with explicit `source_trace_incomplete` caveat.",
        ]
    else:
        interpretation = [
            "- All 87 core3 symbol-month source trace rows have raw checksum status `ok` and matching enhanced hourly partitions.",
            "- Enhanced hourly partitions exist for the expected core3 symbol-month rows, including the current partial May daily extension.",
            "- The `source_trace_incomplete` caveat is removed for A7V controlled experiments.",
            "- This closes raw-level source trace for the enhanced aggTrades panel; it does not validate alpha, strategy robustness, or production readiness.",
        ]
        required_next = [
            "- A7V/A7U may reference the enhanced aggTrades panel without the previous `source_trace_incomplete` caveat.",
            "- Continue to keep alpha proof / shadow / paper / live blocked by A7V-6/A7V-7 signal failures.",
            "- Any future aggTrades panel refresh must rerun A7U-0R before final panel claims.",
        ]

    lines = [
        "# Crypto A7U-0R Source Trace Audit",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{authorization['decision']}`",
        "- executes_search: `False`",
        "- executes_replay: `False`",
        "- alpha proof / panel final claim / shadow / paper / live: `NOT_AUTHORIZED`",
        "",
        "## Scope",
        "",
        "A7U-0R consolidates the source lineage for the enhanced aggTrades panel used by A7V. It audits raw checksum manifests, hourly enhanced partitions, enhanced feature panel lineage, and unified panel join reports.",
        "",
        "This audit does not validate alpha. It only determines whether the panel can be referenced with complete source/checksum traceability.",
        "",
        "## Trace Summary",
        "",
        table(status, max_rows=40),
        "",
        "## By Symbol",
        "",
        table(by_symbol, max_rows=20),
        "",
        "## Panel Lineage",
        "",
        table(lineage, max_rows=20),
        "",
        "## Rows Not Ready For Final Raw-Level Claim",
        "",
        table(missing[[c for c in cols if c in missing.columns]], max_rows=120),
        "",
        "## Interpretation",
        "",
        *interpretation,
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
        "",
        "## Required Next",
        "",
        *required_next,
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_stamp()
    trace, status, by_symbol = build_trace()
    lineage = panel_lineage_summary()
    total_rows = int(len(trace))
    ready_rows = int(trace["source_trace_ready"].sum())
    hold_rows = total_rows - ready_rows
    raw_checksum_ok_rows = int(trace["raw_checksum_ok"].sum())
    partition_rows = int(trace["agg_partition_exists"].sum())
    blockers: list[str] = []
    if hold_rows:
        blockers.append("source_trace_rows_not_ready")
    if raw_checksum_ok_rows < total_rows:
        blockers.append("raw_checksum_manifest_coverage_incomplete")
    if partition_rows < total_rows:
        blockers.append("agg_enhanced_partitions_missing")
    decision = "HOLD_A7U0R_SOURCE_TRACE_INCOMPLETE" if blockers else "PASS_A7U0R_SOURCE_TRACE_COMPLETE"
    required_next = (
        [
            "Resolve source trace HOLD rows before final raw-level panel claims",
            "Keep A7V experiment claims caveated as controlled experiments, not final panel proof",
            "Request missing or corrected raw checksum manifests from data line",
        ]
        if blockers
        else [
            "A7V/A7U may reference the enhanced aggTrades panel without source_trace_incomplete caveat",
            "Alpha proof, expanded replay, shadow, paper, and live remain blocked by A7V-6/A7V-7 signal failures",
            "Rerun A7U-0R after any future aggTrades panel refresh",
        ]
    )
    authorization = {
        "generated_at": now,
        "decision": decision,
        "blockers": blockers,
        "executes_search": False,
        "executes_replay": False,
        "expected_trace_rows": total_rows,
        "source_trace_ready_rows": ready_rows,
        "source_trace_hold_rows": hold_rows,
        "raw_checksum_ok_rows": raw_checksum_ok_rows,
        "agg_partition_rows": partition_rows,
        "authorizes_controlled_experiments_with_caveat": bool(blockers),
        "authorizes_controlled_experiments_without_source_trace_caveat": not bool(blockers),
        "authorizes_final_panel_raw_level_claim": False if blockers else True,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "required_next": required_next,
    }
    trace.to_csv(OUT_DIR / "a7u0r_symbol_month_source_trace.csv", index=False)
    status.to_csv(OUT_DIR / "a7u0r_trace_status_summary.csv", index=False)
    by_symbol.to_csv(OUT_DIR / "a7u0r_trace_by_symbol.csv", index=False)
    lineage.to_csv(OUT_DIR / "a7u0r_panel_lineage_summary.csv", index=False)
    trace[~trace["source_trace_ready"]].to_csv(OUT_DIR / "a7u0r_source_trace_hold_rows.csv", index=False)
    write_json(OUT_DIR / "a7u0r_authorization_matrix.json", authorization)
    write_json(
        OUT_DIR / "a7u0r_manifest.json",
        {
            "generated_at": now,
            "decision": decision,
            "output_dir": str(OUT_DIR),
            "report": str(REPORT_PATH),
            "panel_path": str(PANEL_PATH),
        },
    )
    write_report(now, trace, status, by_symbol, lineage, authorization)
    print(json.dumps({"decision": decision, "blockers": blockers, "ready": ready_rows, "hold": hold_rows, "total": total_rows}, indent=2))


if __name__ == "__main__":
    main()
