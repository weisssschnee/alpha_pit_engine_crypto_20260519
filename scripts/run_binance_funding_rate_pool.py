#!/usr/bin/env python
from __future__ import annotations

import argparse
import csv
import json
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


DEFAULT_ROOT = Path(r"G:\AlphaFactory_CryptoData")
UA = "AlphaFactory-BinanceFundingRatePool/0.1"
ENDPOINT = "https://fapi.binance.com/fapi/v1/fundingRate"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def ms_utc(date_text: str) -> int:
    dt = datetime.fromisoformat(date_text).replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)


def get_json(url: str, timeout: int, retries: int, backoff: float) -> list[dict[str, Any]]:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    last_exc: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001 - retried and recorded by caller
            last_exc = exc
            if attempt < retries:
                time.sleep(backoff * attempt)
    assert last_exc is not None
    raise last_exc


def build_url(symbol: str, start_ms: int, end_ms: int, limit: int) -> str:
    query = urllib.parse.urlencode(
        {
            "symbol": symbol,
            "startTime": start_ms,
            "endTime": end_ms,
            "limit": limit,
        }
    )
    return f"{ENDPOINT}?{query}"


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(path)


def write_status(path: Path, payload: dict[str, Any]) -> None:
    write_json(path, payload)


def append_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists() and path.stat().st_size > 0
    with path.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not exists:
            writer.writeheader()
        writer.writerows(rows)


def fetch_symbol(root: Path, symbol: str, start_ms: int, end_ms: int, limit: int, tag: str, timeout: int, retries: int, backoff: float) -> dict[str, Any]:
    raw_dir = root / "raw" / "binance_api" / "funding_rate" / f"symbol={symbol}" / f"run={tag}"
    silver_dir = root / "silver" / "binance_api" / "funding_rate" / f"symbol={symbol}"
    rows: list[dict[str, Any]] = []
    pages: list[dict[str, Any]] = []
    cursor = start_ms
    page_id = 0
    status = "ok"
    error = ""
    try:
        while cursor <= end_ms:
            url = build_url(symbol, cursor, end_ms, limit)
            data = get_json(url, timeout=timeout, retries=retries, backoff=backoff)
            page_path = raw_dir / f"page_{page_id:04d}.json"
            write_json(
                page_path,
                {
                    "symbol": symbol,
                    "url": url,
                    "collector_time": utc_now(),
                    "source": "binance_fapi_fundingRate",
                    "rows": data,
                },
            )
            pages.append({"page": page_id, "url": url, "raw_path": str(page_path), "rows": len(data)})
            if not data:
                break
            rows.extend(data)
            last_ms = int(data[-1]["fundingTime"])
            next_cursor = last_ms + 1
            if next_cursor <= cursor:
                break
            cursor = next_cursor
            page_id += 1
            if len(data) < limit:
                break
    except Exception as exc:  # noqa: BLE001 - manifest should record the symbol failure
        status = "error"
        error = repr(exc)

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.copy()
        df["symbol"] = symbol
        df["fundingTime"] = pd.to_numeric(df["fundingTime"], errors="coerce").astype("Int64")
        df["fundingRate"] = pd.to_numeric(df["fundingRate"], errors="coerce")
        df["markPrice"] = pd.to_numeric(df.get("markPrice"), errors="coerce") if "markPrice" in df.columns else pd.NA
        df["event_time"] = pd.to_datetime(df["fundingTime"], unit="ms", utc=True)
        df["observable_time"] = df["event_time"]
        df["collector_time"] = pd.Timestamp.utcnow()
        df["source"] = "binance_fapi_fundingRate"
        df["historical_backfill_allowed"] = True
        df = df.drop_duplicates(["symbol", "fundingTime"]).sort_values(["symbol", "fundingTime"])
        silver_dir.mkdir(parents=True, exist_ok=True)
        silver_path = silver_dir / f"funding_rate_{tag}.parquet"
        df.to_parquet(silver_path, index=False, compression="zstd")
    else:
        silver_path = silver_dir / f"funding_rate_{tag}.parquet"

    return {
        "symbol": symbol,
        "status": status,
        "error": error,
        "rows": int(len(df)),
        "pages": len(pages),
        "timestamp_min": str(df["event_time"].min()) if not df.empty else "",
        "timestamp_max": str(df["event_time"].max()) if not df.empty else "",
        "silver_path": str(silver_path) if not df.empty else "",
        "raw_dir": str(raw_dir),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Concurrent Binance USD-M funding rate history downloader.")
    ap.add_argument("--symbols", nargs="+", required=True)
    ap.add_argument("--start", default="2024-01-01")
    ap.add_argument("--end", default="2026-05-21")
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    ap.add_argument("--max-workers", type=int, default=8)
    ap.add_argument("--limit", type=int, default=1000)
    ap.add_argument("--timeout", type=int, default=60)
    ap.add_argument("--retries", type=int, default=8)
    ap.add_argument("--backoff", type=float, default=1.0)
    ap.add_argument("--tag", default=datetime.now().strftime("%Y%m%d_%H%M%S"))
    args = ap.parse_args()

    root = Path(args.root)
    report_dir = root / "reports"
    manifest_dir = root / "manifests"
    status_path = report_dir / f"binance_funding_rate_pool_status_{args.tag}.json"
    manifest_path = manifest_dir / f"binance_funding_rate_pool_manifest_{args.tag}.csv"
    start_ms = ms_utc(args.start)
    end_ms = ms_utc(args.end) + 86_399_999
    symbols = [s.upper() for s in args.symbols]
    started_at = utc_now()
    rows: list[dict[str, Any]] = []

    def snapshot(decision: str) -> dict[str, Any]:
        counts: dict[str, int] = {}
        for row in rows:
            counts[row["status"]] = counts.get(row["status"], 0) + 1
        return {
            "decision": decision,
            "generated_at": utc_now(),
            "started_at": started_at,
            "tag": args.tag,
            "root": str(root),
            "symbols": symbols,
            "range": {"start": args.start, "end": args.end},
            "max_workers": args.max_workers,
            "executes_download": True,
            "executes_search": False,
            "authorizes_alpha_proof": False,
            "manifest": str(manifest_path),
            "counts": {"completed": len(rows), "total": len(symbols), **counts},
        }

    write_status(status_path, snapshot("A7AC2D_BINANCE_FUNDING_RATE_POOL_RUNNING"))
    with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        futures = {
            executor.submit(fetch_symbol, root, symbol, start_ms, end_ms, args.limit, args.tag, args.timeout, args.retries, args.backoff): symbol
            for symbol in symbols
        }
        for future in as_completed(futures):
            row = future.result()
            rows.append(row)
            append_csv(
                manifest_path,
                [row],
                ["symbol", "status", "error", "rows", "pages", "timestamp_min", "timestamp_max", "silver_path", "raw_dir"],
            )
            write_status(status_path, snapshot("A7AC2D_BINANCE_FUNDING_RATE_POOL_RUNNING"))

    failed = [r for r in rows if r["status"] != "ok"]
    decision = "PASS_A7AC2D_BINANCE_FUNDING_RATE_POOL_COMPLETED" if not failed else "HOLD_A7AC2D_BINANCE_FUNDING_RATE_POOL_FAILED"
    write_status(status_path, snapshot(decision))
    print("status=" + str(status_path), flush=True)
    print("manifest=" + str(manifest_path), flush=True)
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
