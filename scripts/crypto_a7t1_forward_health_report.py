from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(r"G:\AlphaFactory_CryptoData")

CROSS_SNAPSHOT = DATA_ROOT / "silver" / "cross_exchange_forward_snapshot" / "cross_exchange_forward_snapshot_20260522_core12_probe2.parquet"
ORDERBOOK_ROOT = DATA_ROOT / "silver" / "binance_api" / "orderbook_forward_snapshot"
POSITIONING_MANIFEST_ROOT = DATA_ROOT / "manifests"

OUT_DIR = ROOT / "runtime" / "a7t1_forward_health_report"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7T1_FORWARD_HEALTH_REPORT_20260522.md"


def now_utc() -> pd.Timestamp:
    return pd.Timestamp(datetime.now(timezone.utc))


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def table(df: pd.DataFrame, max_rows: int = 100) -> str:
    if df.empty:
        return "`<empty>`"
    return df.head(max_rows).to_markdown(index=False)


def age_hours(ts: pd.Timestamp | None) -> float | None:
    if ts is None or pd.isna(ts):
        return None
    return float((now_utc() - ts).total_seconds() / 3600.0)


def cross_health() -> dict[str, Any]:
    if not CROSS_SNAPSHOT.exists():
        return {"source_id": "cross_exchange_forward_snapshot", "status": "HOLD_MISSING", "rows": 0}
    df = pd.read_parquet(CROSS_SNAPSHOT)
    latest = pd.to_datetime(df["observable_time"], errors="coerce", utc=True).max() if "observable_time" in df.columns else None
    return {
        "source_id": "cross_exchange_forward_snapshot",
        "status": "PASS_SAMPLE_READY",
        "rows": int(len(df)),
        "symbols": int(df["symbol"].nunique()) if "symbol" in df.columns else 0,
        "providers": ",".join(sorted(map(str, df["provider"].dropna().unique()))) if "provider" in df.columns else "",
        "latest_observable_time": str(latest) if latest is not None else "",
        "age_hours": age_hours(latest),
        "errors": 0,
        "notes": "forward snapshot sample only; not historical proof",
    }


def orderbook_health() -> dict[str, Any]:
    files = sorted(ORDERBOOK_ROOT.glob("run=*/part.parquet")) if ORDERBOOK_ROOT.exists() else []
    rows = 0
    symbols: set[str] = set()
    latest = None
    for path in files:
        try:
            df = pd.read_parquet(path)
        except Exception:
            continue
        rows += int(len(df))
        if "symbol" in df.columns:
            symbols.update(map(str, df["symbol"].dropna().unique()))
        if "observable_time" in df.columns:
            ts = pd.to_datetime(df["observable_time"], errors="coerce", utc=True).max()
            if pd.notna(ts) and (latest is None or ts > latest):
                latest = ts
    age = age_hours(latest)
    status = "PASS_SAMPLE_READY"
    notes = "forward snapshot sample only"
    if not files:
        status = "HOLD_MISSING"
        notes = "no orderbook forward snapshot files"
    elif age is not None and age > 6:
        status = "WARN_STALE_SAMPLE"
        notes = "sample is stale for live telemetry; collector should run on schedule"
    return {
        "source_id": "binance_orderbook_forward_snapshot",
        "status": status,
        "runs": int(len(files)),
        "rows": rows,
        "symbols": int(len(symbols)),
        "providers": "binance",
        "latest_observable_time": str(latest) if latest is not None else "",
        "age_hours": age,
        "errors": 0,
        "notes": notes,
    }


def positioning_health() -> tuple[dict[str, Any], pd.DataFrame]:
    manifests = sorted(POSITIONING_MANIFEST_ROOT.glob("positioning_forward_5m_*_manifest.csv")) if POSITIONING_MANIFEST_ROOT.exists() else []
    if not manifests:
        return {"source_id": "binance_positioning_forward_5m", "status": "HOLD_MISSING", "rows": 0, "errors": 0}, pd.DataFrame()
    latest_path = manifests[-1]
    df = pd.read_csv(latest_path)
    errors = df[df["status"].ne("downloaded")].copy() if "status" in df.columns else pd.DataFrame()
    row_count = int(df["row_count"].sum()) if "row_count" in df.columns else 0
    latest_download = pd.to_datetime(df["download_time"], errors="coerce", utc=True).max() if "download_time" in df.columns else None
    status = "PASS_LATEST_MANIFEST_CLEAN" if errors.empty else "HOLD_LATEST_MANIFEST_ERRORS"
    return (
        {
            "source_id": "binance_positioning_forward_5m",
            "status": status,
            "manifest": str(latest_path),
            "manifest_rows": int(len(df)),
            "downloaded_rows": int((df["status"] == "downloaded").sum()) if "status" in df.columns else 0,
            "rows": row_count,
            "symbols": int(df["symbol"].nunique()) if "symbol" in df.columns else 0,
            "endpoints": ",".join(sorted(map(str, df["endpoint"].dropna().unique()))) if "endpoint" in df.columns else "",
            "latest_observable_time": str(latest_download) if latest_download is not None else "",
            "age_hours": age_hours(latest_download),
            "errors": int(len(errors)),
            "notes": "latest manifest must be clean before operational forward telemetry is considered healthy",
        },
        errors,
    )


def build_health() -> tuple[pd.DataFrame, pd.DataFrame]:
    pos, pos_errors = positioning_health()
    health = pd.DataFrame([cross_health(), orderbook_health(), pos]).fillna("")
    return health, pos_errors


def build_authorization(health: pd.DataFrame, errors: pd.DataFrame) -> dict[str, Any]:
    hard_holds = int(health["status"].astype(str).str.startswith("HOLD").sum()) if "status" in health.columns else 0
    warnings = int(health["status"].astype(str).str.startswith("WARN").sum()) if "status" in health.columns else 0
    decision = "PASS_A7T1_FORWARD_HEALTH_CLEAN"
    if hard_holds > 0:
        decision = "HOLD_A7T1_FORWARD_HEALTH_REPAIR_REQUIRED"
    elif warnings > 0:
        decision = "WARN_A7T1_FORWARD_HEALTH_STALE_SAMPLE"
    required_next = [
        "Run orderbook/cross-exchange collectors on fixed schedule if telemetry dashboard is needed",
        "Add collector_version and schema_hash to all forward manifests",
    ]
    if len(errors) > 0:
        required_next.insert(0, "Repair or rerun latest positioning forward manifest error before treating positioning forward collector as healthy")
    return {
        "decision": decision,
        "generated_at": utc_stamp(),
        "executes_download": False,
        "executes_search": False,
        "executes_replay": False,
        "source_count": int(len(health)),
        "hard_hold_count": hard_holds,
        "warning_count": warnings,
        "positioning_error_count": int(len(errors)),
        "authorizes_forward_telemetry_collection": decision.startswith("PASS") or decision.startswith("WARN"),
        "authorizes_historical_alpha_proof": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "required_next": required_next,
    }


def write_report(health: pd.DataFrame, errors: pd.DataFrame, auth: dict[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# CRYPTO A7T-1 Forward Health Report",
        "",
        f"Generated: {auth['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{auth['decision']}`",
        "",
        "A7T-1 is an operational health report. It does not download data, run replay, search formulas, or authorize alpha proof.",
        "",
        "## Source Health",
        "",
        table(health),
        "",
        "## Positioning Error Detail",
        "",
        table(errors, max_rows=60),
        "",
        "## Authorization",
        "",
        table(pd.DataFrame([auth])),
        "",
        "## Required Next Action",
        "",
        "1. Run orderbook/cross-exchange collectors on a fixed cadence if telemetry dashboard freshness is required.",
        "2. Add `collector_version` and `schema_hash` to future forward manifests.",
        "3. Keep this report as telemetry health only; no alpha proof, shadow, paper, or live.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    health, errors = build_health()
    auth = build_authorization(health, errors)
    manifest = {
        "decision": auth["decision"],
        "generated_at": auth["generated_at"],
        "source_count": auth["source_count"],
        "hard_hold_count": auth["hard_hold_count"],
        "warning_count": auth["warning_count"],
        "executes_download": False,
        "executes_search": False,
        "executes_replay": False,
        "authorizes_alpha_proof": False,
    }
    health.to_csv(OUT_DIR / "a7t1_forward_source_health.csv", index=False)
    errors.to_csv(OUT_DIR / "a7t1_positioning_error_detail.csv", index=False)
    write_json(OUT_DIR / "a7t1_authorization_matrix.json", auth)
    write_json(OUT_DIR / "a7t1_manifest.json", manifest)
    write_report(health, errors, auth)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
