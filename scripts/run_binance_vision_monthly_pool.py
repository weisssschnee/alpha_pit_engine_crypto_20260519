#!/usr/bin/env python
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import time
import urllib.error
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_ROOT = Path(r"G:\AlphaFactory_CryptoData")
UA = "AlphaFactory-BinanceVisionMonthlyPool/0.1"


@dataclass(frozen=True)
class Job:
    data_type: str
    symbol: str
    interval: str
    month: str


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def month_range(start: str, end: str) -> list[str]:
    cur = datetime.strptime(start, "%Y-%m")
    last = datetime.strptime(end, "%Y-%m")
    out: list[str] = []
    while cur <= last:
        out.append(cur.strftime("%Y-%m"))
        year = cur.year + (cur.month // 12)
        month = 1 if cur.month == 12 else cur.month + 1
        cur = cur.replace(year=year, month=month)
    return out


def remote_filename(job: Job) -> str:
    return f"{job.symbol}-{job.interval}-{job.month}.zip"


def build_url(job: Job) -> str:
    base = "https://data.binance.vision/data/futures/um/monthly"
    return f"{base}/{job.data_type}/{job.symbol}/{job.interval}/{remote_filename(job)}"


def parse_checksum(text: str) -> str:
    match = re.search(r"\b([a-fA-F0-9]{64})\b", text)
    return match.group(1).lower() if match else ""


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def download_bytes(url: str, timeout: int, retries: int, backoff: float) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    last_exc: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return response.read()
        except urllib.error.HTTPError:
            raise
        except Exception as exc:  # noqa: BLE001 - retried and recorded by caller
            last_exc = exc
            if attempt < retries:
                time.sleep(backoff * attempt)
    assert last_exc is not None
    raise last_exc


def download_file_once(url: str, path: Path, timeout: int) -> tuple[int, str]:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    if tmp.exists():
        tmp.unlink()
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    if tmp.exists():
        tmp.unlink()
    h = hashlib.sha256()
    size = 0
    with urllib.request.urlopen(req, timeout=timeout) as response:
        with tmp.open("wb") as f:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                f.write(chunk)
                h.update(chunk)
                size += len(chunk)
    tmp.replace(path)
    return size, h.hexdigest()


def zip_integrity_ok(path: Path) -> bool:
    if not zipfile.is_zipfile(path):
        return False
    try:
        with zipfile.ZipFile(path) as zf:
            return zf.testzip() is None
    except zipfile.BadZipFile:
        return False


def remove_bad_download(path: Path) -> None:
    if path.exists():
        path.unlink()


def download_verified_file(
    url: str,
    path: Path,
    expected_sha256: str,
    timeout: int,
    retries: int,
    backoff: float,
) -> tuple[int, str, bool, str]:
    last_error = ""
    for attempt in range(1, retries + 1):
        try:
            size, digest = download_file_once(url, path, timeout=timeout)
            checksum_ok = digest == expected_sha256
            integrity_ok = zip_integrity_ok(path)
            if checksum_ok and integrity_ok:
                return size, digest, True, ""
            last_error = f"attempt={attempt} checksum_ok={checksum_ok} zip_integrity_ok={integrity_ok}"
            remove_bad_download(path)
        except urllib.error.HTTPError:
            remove_bad_download(path)
            raise
        except Exception as exc:  # noqa: BLE001 - retry and preserve final reason
            last_error = f"attempt={attempt} error={exc!r}"
            remove_bad_download(path)
        if attempt < retries:
            time.sleep(backoff * attempt)
    return 0, "", False, last_error


def raw_path(root: Path, job: Job) -> Path:
    return root / "raw" / "binance_vision" / "futures_um" / job.data_type / job.symbol / job.interval / remote_filename(job)


def checksum_path(root: Path, job: Job) -> Path:
    return root / "metadata" / "checksums" / "binance_vision_monthly" / "futures_um" / job.data_type / job.symbol / job.interval / f"{remote_filename(job)}.CHECKSUM"


def evaluate_job(root: Path, job: Job, timeout: int, retries: int, backoff: float, overwrite_bad: bool) -> dict[str, Any]:
    url = build_url(job)
    checksum_url = url + ".CHECKSUM"
    dst = raw_path(root, job)
    chk_path = checksum_path(root, job)
    row: dict[str, Any] = {
        "ts_utc": utc_now(),
        "market": "futures_um",
        "data_type": job.data_type,
        "interval": job.interval,
        "symbol": job.symbol,
        "month": job.month,
        "url": url,
        "checksum_url": checksum_url,
        "path": str(dst),
        "checksum_path": str(chk_path),
        "status": "",
        "bytes": 0,
        "sha256": "",
        "expected_sha256": "",
        "checksum_ok": False,
        "error": "",
    }
    try:
        chk_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            checksum_text = download_bytes(checksum_url, timeout=timeout, retries=retries, backoff=backoff).decode("utf-8", errors="replace")
            chk_path.write_text(checksum_text, encoding="utf-8")
        except urllib.error.HTTPError as exc:
            row["status"] = "not_available_404" if exc.code == 404 else "checksum_http_error"
            row["error"] = f"{exc.code} {exc.reason}"
            return row
        expected = parse_checksum(chk_path.read_text(encoding="utf-8", errors="replace"))
        row["expected_sha256"] = expected
        if not expected:
            row["status"] = "checksum_parse_error"
            row["error"] = "no 64-char sha256 in checksum file"
            return row

        if dst.exists() and dst.stat().st_size > 0:
            digest = sha256_file(dst)
            row["bytes"] = dst.stat().st_size
            row["sha256"] = digest
            checksum_ok = digest == expected
            integrity_ok = zip_integrity_ok(dst)
            row["checksum_ok"] = checksum_ok and integrity_ok
            if row["checksum_ok"]:
                row["status"] = "exists_checksum_ok"
                return row
            if not overwrite_bad:
                row["status"] = "exists_checksum_mismatch"
                row["error"] = f"existing file invalid; checksum_ok={checksum_ok} zip_integrity_ok={integrity_ok}; rerun with --overwrite-bad"
                return row
            bad = dst.with_suffix(dst.suffix + f".bad_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            dst.replace(bad)

        size, digest, ok, verify_error = download_verified_file(
            url,
            dst,
            expected_sha256=expected,
            timeout=timeout,
            retries=retries,
            backoff=backoff,
        )
        row["bytes"] = size
        row["sha256"] = digest
        row["checksum_ok"] = ok
        row["status"] = "downloaded_checksum_ok" if ok else "downloaded_checksum_mismatch_after_retries"
        if not ok:
            row["error"] = verify_error or "downloaded file checksum/integrity mismatch after retries"
        return row
    except urllib.error.HTTPError as exc:
        row["status"] = "not_available_404" if exc.code == 404 else "zip_http_error"
        row["error"] = f"{exc.code} {exc.reason}"
        return row
    except Exception as exc:  # noqa: BLE001 - manifest should record all failures
        row["status"] = "error"
        row["error"] = repr(exc)
        return row


def append_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists() and path.stat().st_size > 0
    with path.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not exists:
            writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(path)


def main() -> int:
    ap = argparse.ArgumentParser(description="Concurrent Binance Vision monthly futures downloader with .CHECKSUM audit.")
    ap.add_argument("--symbols", nargs="+", required=True)
    ap.add_argument("--data-types", nargs="+", required=True, choices=["klines", "markPriceKlines", "indexPriceKlines", "premiumIndexKlines"])
    ap.add_argument("--interval", default="1m")
    ap.add_argument("--start", required=True, help="YYYY-MM")
    ap.add_argument("--end", required=True, help="YYYY-MM")
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    ap.add_argument("--max-workers", type=int, default=24)
    ap.add_argument("--timeout", type=int, default=90)
    ap.add_argument("--retries", type=int, default=8)
    ap.add_argument("--backoff", type=float, default=1.0)
    ap.add_argument("--tag", default=datetime.now().strftime("%Y%m%d_%H%M%S"))
    ap.add_argument("--overwrite-bad", action="store_true")
    ap.add_argument("--flush-every", type=int, default=50)
    args = ap.parse_args()

    root = Path(args.root)
    report_dir = root / "reports"
    manifest_dir = root / "manifests"
    status_path = report_dir / f"binance_vision_monthly_pool_status_{args.tag}.json"
    manifest_path = manifest_dir / f"binance_vision_monthly_pool_manifest_{args.tag}.csv"
    months = month_range(args.start, args.end)
    jobs = [
        Job(data_type=data_type, symbol=symbol.upper(), interval=args.interval, month=month)
        for data_type in args.data_types
        for symbol in args.symbols
        for month in months
    ]

    fieldnames = [
        "ts_utc",
        "market",
        "data_type",
        "interval",
        "symbol",
        "month",
        "url",
        "checksum_url",
        "path",
        "checksum_path",
        "status",
        "bytes",
        "sha256",
        "expected_sha256",
        "checksum_ok",
        "error",
    ]
    rows_buffer: list[dict[str, Any]] = []
    counts: dict[str, int] = {}
    completed = 0
    started_at = utc_now()

    def snapshot(decision: str) -> dict[str, Any]:
        return {
            "decision": decision,
            "generated_at": utc_now(),
            "started_at": started_at,
            "tag": args.tag,
            "root": str(root),
            "symbols": [s.upper() for s in args.symbols],
            "data_types": args.data_types,
            "interval": args.interval,
            "range": {"start": args.start, "end": args.end, "months": len(months)},
            "max_workers": args.max_workers,
            "executes_download": True,
            "executes_search": False,
            "authorizes_alpha_proof": False,
            "manifest": str(manifest_path),
            "counts": {"completed": completed, "total": len(jobs), **counts},
        }

    write_json(status_path, snapshot("A7AC2C_BINANCE_VISION_MONTHLY_POOL_RUNNING"))

    with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        future_to_job = {
            executor.submit(evaluate_job, root, job, args.timeout, args.retries, args.backoff, args.overwrite_bad): job
            for job in jobs
        }
        for future in as_completed(future_to_job):
            row = future.result()
            rows_buffer.append(row)
            completed += 1
            status = str(row["status"])
            counts[status] = counts.get(status, 0) + 1
            if len(rows_buffer) >= args.flush_every:
                append_csv(manifest_path, rows_buffer, fieldnames)
                rows_buffer.clear()
                write_json(status_path, snapshot("A7AC2C_BINANCE_VISION_MONTHLY_POOL_RUNNING"))
    if rows_buffer:
        append_csv(manifest_path, rows_buffer, fieldnames)
        rows_buffer.clear()

    ok_statuses = {"exists_checksum_ok", "downloaded_checksum_ok", "not_available_404"}
    bad_count = sum(v for k, v in counts.items() if k not in ok_statuses)
    decision = (
        "PASS_A7AC2C_BINANCE_VISION_MONTHLY_POOL_COMPLETED"
        if bad_count == 0 and counts.get("not_available_404", 0) == 0
        else (
            "PASS_A7AC2C_BINANCE_VISION_MONTHLY_POOL_COMPLETED_WITH_LISTING_GAPS"
            if bad_count == 0
            else "HOLD_A7AC2C_BINANCE_VISION_MONTHLY_POOL_HAS_FAILURES"
        )
    )
    write_json(status_path, snapshot(decision))
    print("status=" + str(status_path), flush=True)
    print("manifest=" + str(manifest_path), flush=True)
    return 0 if bad_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
