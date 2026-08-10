"""Build a month-to-date compact carrier from official Binance daily files.

The adapter deliberately reuses the already-qualified compact aggregation
functions supplied by the existing PC2 data-delivery script.  Its source hash
is recorded in the acquisition status.  Raw ZIP files are deleted after
checksum verification and parquet write.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import importlib.util
import json
import os
import tarfile
import zipfile
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import requests


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(8 * 1024 * 1024):
            digest.update(block)
    return digest.hexdigest().upper()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".tmp-{os.getpid()}")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    os.replace(temporary, path)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def days(start: date, end_exclusive: date):
    current = start
    while current < end_exclusive:
        yield current
        current += timedelta(days=1)


def load_base_module(path: Path):
    spec = importlib.util.spec_from_file_location("qualified_aggtrades_compact", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("AGGTRADES_BASE_MODULE_IMPORT_FAILED")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for name in (
        "COLUMNS",
        "chunk_partial",
        "finalize",
        "download_zip",
        "request_bytes",
    ):
        if not hasattr(module, name):
            raise RuntimeError(f"AGGTRADES_BASE_MODULE_MISSING:{name}")
    return module


def process_symbol(
    *,
    module: Any,
    symbol: str,
    start: date,
    end_exclusive: date,
    root: Path,
    temp_root: Path,
) -> dict[str, Any]:
    month = start.strftime("%Y-%m")
    done_path = root / "done" / symbol / f"{month}.json"
    output_path = root / "compact_1m" / f"symbol={symbol}" / f"month={month}" / "part.parquet"
    manifest_path = root / "object_manifest" / f"symbol={symbol}" / f"month={month}.json"
    if done_path.exists() and manifest_path.exists():
        saved = json.loads(done_path.read_text(encoding="utf-8"))
        if saved.get("status") == "not_found" or output_path.exists():
            return {"status": "already_done", "symbol": symbol}
    session = requests.Session()
    session.headers.update({"User-Agent": "AlphaFactory-P4-DailyAggTrades/1.0"})
    partials: list[pd.DataFrame] = []
    objects: list[dict[str, Any]] = []
    raw_rows = 0
    missing_days: list[str] = []
    symbol_temp = temp_root / symbol
    symbol_temp.mkdir(parents=True, exist_ok=True)
    try:
        for day in days(start, end_exclusive):
            day_text = day.isoformat()
            stem = f"{symbol}-aggTrades-{day_text}.zip"
            url = f"https://data.binance.vision/data/futures/um/daily/aggTrades/{symbol}/{stem}"
            checksum_url = url + ".CHECKSUM"
            checksum_code, checksum_body = module.request_bytes(session, checksum_url)
            expected = (
                checksum_body.decode("utf-8", errors="ignore").strip().split()[0].lower()
                if checksum_code == 200
                else None
            )
            zip_path = symbol_temp / stem
            code = module.download_zip(session, url, zip_path)
            if code == 404:
                missing_days.append(day_text)
                objects.append(
                    {
                        "day": day_text,
                        "status": "not_found",
                        "source_url": url,
                    }
                )
                continue
            if code != 200:
                raise RuntimeError(f"download failed status={code} url={url}")
            actual = sha256_file(zip_path).lower()
            if expected and actual != expected:
                raise RuntimeError(f"checksum mismatch {symbol} {day_text}")
            day_rows = 0
            try:
                with zipfile.ZipFile(zip_path) as archive:
                    members = [name for name in archive.namelist() if name.lower().endswith(".csv")]
                    if len(members) != 1:
                        raise RuntimeError(f"unexpected zip members {members}")
                    with archive.open(members[0]) as handle:
                        for chunk in pd.read_csv(
                            handle,
                            names=module.COLUMNS,
                            header=None,
                            chunksize=750_000,
                            low_memory=False,
                        ):
                            day_rows += len(chunk)
                            partial = module.chunk_partial(chunk)
                            if not partial.empty:
                                partials.append(partial)
                raw_rows += day_rows
                objects.append(
                    {
                        "day": day_text,
                        "status": "complete",
                        "source_url": url,
                        "source_checksum_url": checksum_url,
                        "source_checksum_expected": expected,
                        "source_checksum_actual": actual,
                        "source_checksum_status": "ok" if expected else "unavailable",
                        "raw_rows": day_rows,
                    }
                )
            finally:
                zip_path.unlink(missing_ok=True)
        if not partials:
            payload = {
                "status": "not_found",
                "symbol": symbol,
                "month": month,
                "start": start.isoformat(),
                "end_exclusive": end_exclusive.isoformat(),
                "missing_days": missing_days,
                "objects": objects,
                "completed_at": utc_now(),
                "raw_retained": False,
            }
            atomic_json(manifest_path, payload)
            atomic_json(done_path, payload)
            return payload
        output = module.finalize(partials, symbol, month)
        output["source"] = "binance_vision_usdm_daily_aggTrades"
        output["aggregation"] = "1min_compact_enhanced_v1_daily_bridge"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = output_path.with_suffix(".parquet.tmp")
        output.to_parquet(temporary, index=False, compression="zstd", engine="pyarrow")
        os.replace(temporary, output_path)
        payload = {
            "status": "complete",
            "symbol": symbol,
            "month": month,
            "start": start.isoformat(),
            "end_exclusive": end_exclusive.isoformat(),
            "requested_days": (end_exclusive - start).days,
            "available_days": sum(row["status"] == "complete" for row in objects),
            "missing_days": missing_days,
            "objects": objects,
            "raw_rows": raw_rows,
            "minute_rows": len(output),
            "timestamp_min": str(output["timestamp"].min()),
            "timestamp_max": str(output["timestamp"].max()),
            "output_path": str(output_path),
            "output_sha256": sha256_file(output_path),
            "completed_at": utc_now(),
            "raw_retained": False,
        }
        atomic_json(manifest_path, payload)
        atomic_json(done_path, payload)
        return payload
    finally:
        for item in symbol_temp.glob("*.zip"):
            item.unlink(missing_ok=True)
        try:
            symbol_temp.rmdir()
        except OSError:
            pass


def package_rank_group(
    *,
    data_root: Path,
    combined_root: Path,
    ranking: list[tuple[int, str]],
    first_rank: int,
    last_rank: int,
    name: str,
    month: str,
) -> dict[str, Any]:
    tar_path = data_root / f"{name}.tar"
    if tar_path.exists():
        raise FileExistsError(f"archive already exists: {tar_path}")
    members: list[Path] = []
    for rank, symbol in ranking:
        if not first_rank <= rank <= last_rank:
            continue
        done = combined_root / "done" / symbol / f"{month}.json"
        if not done.is_file():
            raise RuntimeError(f"missing done marker: {symbol}")
        payload = json.loads(done.read_text(encoding="utf-8"))
        members.append(done)
        members.append(combined_root / "object_manifest" / f"symbol={symbol}" / f"{month}.json")
        if payload.get("status") == "complete":
            members.append(
                combined_root / "compact_1m" / f"symbol={symbol}" / f"month={month}" / "part.parquet"
            )
    with tarfile.open(tar_path, "w") as archive:
        for path in members:
            if not path.is_file():
                raise RuntimeError(f"missing archive member: {path}")
            archive.add(path, arcname=str(path.relative_to(data_root)).replace("\\", "/"))
    digest = sha256_file(tar_path)
    tar_path.with_suffix(tar_path.suffix + ".sha256").write_text(
        f"{digest.lower()}  {tar_path.name}\n", encoding="ascii"
    )
    return {
        "path": str(tar_path),
        "bytes": tar_path.stat().st_size,
        "sha256": digest,
        "member_count": len(members),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("base_module", type=Path)
    parser.add_argument("classification", type=Path)
    parser.add_argument("output_root", type=Path)
    parser.add_argument("--start", required=True)
    parser.add_argument("--end-exclusive", required=True)
    parser.add_argument("--workers", type=int, default=3)
    args = parser.parse_args()
    start = date.fromisoformat(args.start)
    end_exclusive = date.fromisoformat(args.end_exclusive)
    if end_exclusive <= start or start.strftime("%Y-%m") != (end_exclusive - timedelta(days=1)).strftime("%Y-%m"):
        raise ValueError("daily acquisition must be a positive single-month interval")
    module = load_base_module(args.base_module)
    classification = pd.read_csv(args.classification)
    classification["liquidity_rank"] = pd.to_numeric(
        classification["liquidity_rank"], errors="raise"
    ).astype(int)
    ranking = sorted(
        (
            int(row.liquidity_rank),
            str(row.symbol),
        )
        for row in classification.itertuples()
        if 1 <= int(row.liquidity_rank) <= 200
    )
    if len(ranking) != 200 or len({symbol for _, symbol in ranking}) != 200:
        raise RuntimeError("FROZEN_TOP200_CLASSIFICATION_CHANGED")
    data_root = args.output_root
    combined = data_root / "combined"
    temp_root = data_root / "temp"
    status_path = data_root / "status.json"
    status: dict[str, Any] = {
        "schema_version": 1,
        "status": "running",
        "started_at": utc_now(),
        "start": start.isoformat(),
        "end_exclusive": end_exclusive.isoformat(),
        "symbols": 200,
        "workers": max(1, args.workers),
        "base_module": str(args.base_module),
        "base_module_sha256": sha256_file(args.base_module),
        "classification_sha256": sha256_file(args.classification),
        "completed_symbols": 0,
        "failure_count": 0,
        "recent_failures": [],
        "raw_retention_policy": "delete_after_checksum_and_compact_write",
    }
    atomic_json(status_path, status)
    pending = [(rank, symbol) for rank, symbol in ranking]
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = {
            pool.submit(
                process_symbol,
                module=module,
                symbol=symbol,
                start=start,
                end_exclusive=end_exclusive,
                root=combined,
                temp_root=temp_root,
            ): (rank, symbol)
            for rank, symbol in pending
        }
        for future in concurrent.futures.as_completed(futures):
            rank, symbol = futures[future]
            try:
                future.result()
                status["completed_symbols"] += 1
            except Exception as exc:
                status["failure_count"] += 1
                status["recent_failures"] = (
                    status["recent_failures"]
                    + [{"rank": rank, "symbol": symbol, "error": str(exc)}]
                )[-30:]
            status["updated_at"] = utc_now()
            atomic_json(status_path, status)
    if status["failure_count"]:
        status["status"] = "retry_required"
    else:
        month = start.strftime("%Y-%m")
        status["archives"] = [
            package_rank_group(
                data_root=data_root,
                combined_root=combined,
                ranking=ranking,
                first_rank=1,
                last_rank=100,
                name=f"binance_aggtrades_top100_compact_1m_{month.replace('-', '')}",
                month=month,
            ),
            package_rank_group(
                data_root=data_root,
                combined_root=combined,
                ranking=ranking,
                first_rank=101,
                last_rank=200,
                name=f"binance_aggtrades_ranks101_200_compact_1m_{month.replace('-', '')}",
                month=month,
            ),
        ]
        status["status"] = "complete"
    status["completed_at"] = utc_now()
    atomic_json(status_path, status)
    print(json.dumps(status, sort_keys=True))
    return 0 if status["status"] == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
