from __future__ import annotations

import argparse
import csv
import hashlib
import json
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[1]
RUN_ROOT = REPO / "runtime" / "mechanism_data_expansion0_20260712" / "bbo_full_year_acquisition"
CORE12 = ("ADAUSDT", "AVAXUSDT", "BCHUSDT", "BNBUSDT", "BTCUSDT", "DOGEUSDT", "ETHUSDT", "LINKUSDT", "LTCUSDT", "SOLUSDT", "SUIUSDT", "XRPUSDT")
MONTHS = tuple(f"2024-{month:02d}" for month in range(1, 13))
BASE = "https://data.binance.vision/data/futures/um/monthly/bookTicker"


def source_url(symbol: str, month: str) -> str:
    return f"{BASE}/{symbol}/{symbol}-bookTicker-{month}.zip"


def head(symbol: str, month: str, timeout: int = 30) -> dict[str, Any]:
    url = source_url(symbol, month)
    result: dict[str, Any] = {"symbol": symbol, "month": month, "url": url, "status": "UNAVAILABLE", "bytes": -1, "checksum_status": "UNAVAILABLE"}
    try:
        request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "crypto-mechanism-data-inventory/1.0"})
        with urllib.request.urlopen(request, timeout=timeout) as response:
            result.update({"status": f"HTTP_{response.status}", "bytes": int(response.headers.get("Content-Length", -1)),
                           "last_modified": response.headers.get("Last-Modified", ""), "etag": response.headers.get("ETag", "")})
        checksum = urllib.request.Request(url + ".CHECKSUM", method="HEAD", headers={"User-Agent": "crypto-mechanism-data-inventory/1.0"})
        with urllib.request.urlopen(checksum, timeout=timeout) as response:
            result["checksum_status"] = f"HTTP_{response.status}"
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}:{exc}"
    return result


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def run(workers: int) -> dict[str, Any]:
    RUN_ROOT.mkdir(parents=True, exist_ok=True)
    coordinates = [(symbol, month) for symbol in CORE12 for month in MONTHS]
    with ThreadPoolExecutor(max_workers=workers) as executor:
        rows = list(executor.map(lambda item: head(*item), coordinates))
    rows.sort(key=lambda row: (row["symbol"], row["month"]))
    table = RUN_ROOT / "bbo_source_capacity.csv"
    fieldnames = sorted({key for row in rows for key in row})
    with table.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader(); writer.writerows(rows)
    available = [row for row in rows if row["status"] == "HTTP_200" and row["checksum_status"] == "HTTP_200" and row["bytes"] > 0]
    total = sum(row["bytes"] for row in available)
    largest = max((row["bytes"] for row in available), default=0)
    smallest = min(available, key=lambda row: row["bytes"], default={})
    summary = {
        "status": "BBO_FULL_YEAR_SOURCE_CAPACITY_PLANNED",
        "source": "Binance Vision USD-M monthly bookTicker",
        "source_coordinates": len(rows), "available_coordinates": len(available),
        "source_availability_ratio": len(available) / len(rows),
        "compressed_bytes_total": total, "compressed_gib_total": total / (1024 ** 3),
        "largest_monthly_file_bytes": largest, "largest_monthly_file_gib": largest / (1024 ** 3),
        "smallest_coordinate": smallest,
        "processing_contract": "one symbol-month at a time: download, official checksum, aggregate BBO, delete raw zip",
        "peak_raw_disk_requirement_bytes": largest,
        "target": "Binance UM core12 full-2024 BBO >=95% symbol-month coverage",
        "depth_claim": False, "performance_queries": 0, "forward_read": False, "accepted_identity_used": False,
        "official_source_repository": "https://github.com/binance/binance-public-data",
        "license": "MIT for public-data helper repository; exchange data access terms remain source-governed",
        "verified_on": date.today().isoformat(),
    }
    summary_path = RUN_ROOT / "bbo_acquisition_capacity_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest = {
        "experiment_id": "20260712_bbo_full_year_source_capacity_001", "performance_queries": 0,
        "forward_read": False, "row_data_read": False, "outputs": [
            {"path": str(table.relative_to(REPO)).replace("\\", "/"), "sha256": sha256_file(table)},
            {"path": str(summary_path.relative_to(REPO)).replace("\\", "/"), "sha256": sha256_file(summary_path)},
        ],
    }
    (RUN_ROOT / "bbo_acquisition_plan_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=12)
    args = parser.parse_args()
    print(json.dumps(run(args.workers), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
