from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import socket
import time
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


FILE_EXTENSIONS = {".parquet", ".csv", ".json", ".jsonl", ".zip", ".gz", ".feather", ".arrow", ".tar", ".7z"}
SEALED_TOKENS = ("forward", "validation", "test", "recent", "stress", "oos", "may2026", "2026-05")
CORE12 = ("ADAUSDT", "AVAXUSDT", "BCHUSDT", "BNBUSDT", "BTCUSDT", "DOGEUSDT", "ETHUSDT", "LINKUSDT", "LTCUSDT", "SOLUSDT", "SUIUSDT", "XRPUSDT")
TIMESTAMP_COLUMNS = ("timestamp", "event_time", "open_time", "time", "datetime", "ts")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def infer_venue(text: str) -> str:
    lowered = text.lower()
    for token, venue in (("binance", "BINANCE"), ("okx", "OKX"), ("bybit", "BYBIT"), ("deribit", "DERIBIT"), ("coinbase", "COINBASE"), ("kraken", "KRAKEN")):
        if token in lowered:
            return venue
    return "UNKNOWN"


def infer_market(text: str) -> str:
    lowered = text.lower()
    if any(token in lowered for token in ("option", "deribit")):
        return "OPTIONS"
    if any(token in lowered for token in ("um", "perp", "future", "futures", "swap")):
        return "PERPETUAL_OR_FUTURES"
    if "spot" in lowered:
        return "SPOT"
    return "UNKNOWN"


def infer_family(text: str) -> str:
    lowered = text.lower().replace("_", "").replace("-", "")
    rules = (
        (("forceorder", "liquidation"), "LIQUIDATION_FORCE_ORDER"),
        (("bookticker", "bestbid", "bestask"), "BOOKTICKER_BBO"),
        (("depth", "orderbook", "bookdelta", "booksnapshot"), "ORDER_BOOK_DEPTH"),
        (("aggtrade",), "AGG_TRADES"),
        (("trade",), "TRADES"),
        (("option", "ivsurface", "impliedvol", "skew"), "OPTIONS"),
        (("openinterest", "open_interest"), "OPEN_INTEREST"),
        (("funding",), "FUNDING"),
        (("markprice", "mark_price"), "MARK_PRICE"),
        (("indexprice", "index_price"), "INDEX_PRICE"),
        (("premium", "basis"), "BASIS_PREMIUM"),
        (("taker",), "TAKER_FLOW"),
        (("kline", "candlestick", "ohlc"), "KLINES"),
    )
    for tokens, family in rules:
        if any(token.replace("_", "") in lowered for token in tokens):
            return family
    return "OTHER"


def infer_symbol(text: str) -> str:
    upper = text.upper()
    match = re.search(r"(?:SYMBOL[=\\/_-])([A-Z0-9]{3,16}(?:USDT|USD|USDC|BTC|ETH))", upper)
    if match:
        return match.group(1)
    matches = re.findall(r"(?<![A-Z0-9])([A-Z0-9]{2,12}(?:USDT|USDC|USD))(?![A-Z0-9])", upper)
    return matches[-1] if matches else "UNKNOWN"


def infer_month(text: str) -> str:
    patterns = (r"(20\d{2})[-_/]?(0[1-9]|1[0-2])(?:[-_/]?[0-3]\d)?", r"YEAR[=\\/_-](20\d{2}).*MONTH[=\\/_-](0?[1-9]|1[0-2])")
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return f"{match.group(1)}-{int(match.group(2)):02d}"
    return "UNKNOWN"


def infer_frequency(text: str) -> str:
    lowered = text.lower()
    for token in ("1s", "5s", "1m", "5m", "15m", "30m", "1h", "4h", "8h", "1d", "tick"):
        if re.search(rf"(?:^|[^a-z0-9]){re.escape(token)}(?:[^a-z0-9]|$)", lowered):
            return token.upper()
    return "EVENT" if any(token in lowered for token in ("trade", "bookticker", "depth", "forceorder")) else "UNKNOWN"


def is_sealed(path: Path) -> bool:
    lowered = str(path).lower()
    return any(token in lowered for token in SEALED_TOKENS)


def dataset_root(path: Path, root: Path) -> str:
    parent = path.parent
    partition = re.compile(r"^(symbol|year|month|date|day|run)=", re.IGNORECASE)
    while parent != root and (partition.match(parent.name) or infer_symbol(parent.name) != "UNKNOWN" or re.fullmatch(r"20\d{2}[-_]?(?:0[1-9]|1[0-2])?", parent.name)):
        parent = parent.parent
    return str(parent)


def parquet_footer(path: Path) -> dict[str, Any]:
    try:
        import pyarrow.parquet as pq
        parquet = pq.ParquetFile(path)
        metadata = parquet.metadata
        schema = list(parquet.schema_arrow.names)
        minimum = maximum = ""
        timestamp_column = next((column for column in TIMESTAMP_COLUMNS if column in schema), "")
        if timestamp_column:
            column_index = schema.index(timestamp_column)
            values_min, values_max = [], []
            for group_index in range(metadata.num_row_groups):
                statistics = metadata.row_group(group_index).column(column_index).statistics
                if statistics and statistics.has_min_max:
                    values_min.append(statistics.min)
                    values_max.append(statistics.max)
            if values_min:
                minimum, maximum = str(min(values_min)), str(max(values_max))
        return {"row_count": metadata.num_rows, "fields": "|".join(schema), "timestamp_column": timestamp_column, "start": minimum, "end": maximum, "footer_status": "READ_OK"}
    except Exception as exc:
        return {"row_count": -1, "fields": "", "timestamp_column": "", "start": "", "end": "", "footer_status": f"FAILED:{type(exc).__name__}"}


def header_fields(path: Path) -> str:
    try:
        with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
            return "|".join(next(csv.reader(handle)))
    except Exception:
        return ""


def inventory_file(path: Path, root: Path, machine: str, inspect_metadata: bool = True) -> dict[str, Any]:
    text = str(path)
    sealed = is_sealed(path)
    stat = path.stat() if inspect_metadata and not sealed else None
    detail = {"row_count": -1, "fields": "", "timestamp_column": "", "start": "", "end": "", "footer_status": "NOT_APPLICABLE"}
    if not inspect_metadata and not sealed:
        detail["footer_status"] = "NOT_SAMPLED_DATASET_METADATA_CAP"
    elif path.suffix.lower() == ".parquet" and not sealed:
        detail = parquet_footer(path)
    elif path.suffix.lower() == ".csv" and not sealed:
        detail["fields"] = header_fields(path)
        detail["footer_status"] = "HEADER_ONLY"
    elif path.suffix.lower() == ".zip" and not sealed:
        try:
            with zipfile.ZipFile(path) as archive:
                names = archive.namelist()
            detail["fields"] = f"ARCHIVE_MEMBERS={len(names)};SAMPLE={'|'.join(names[:5])}"
            detail["footer_status"] = "ARCHIVE_DIRECTORY_ONLY"
        except Exception as exc:
            detail["footer_status"] = f"FAILED:{type(exc).__name__}"
    month = infer_month(text)
    inferred_start = f"{month}-01" if month != "UNKNOWN" else ""
    return {
        "machine": machine, "scan_root": str(root), "path": text, "dataset_root": dataset_root(path, root),
        "source": "LOCAL_OR_MOUNTED_HISTORICAL_FILE", "venue": infer_venue(text), "market_type": infer_market(text),
        "data_family": infer_family(text), "symbol": infer_symbol(text), "month": month,
        "start": detail["start"] or inferred_start, "end": detail["end"], "frequency": infer_frequency(text),
        "row_count": detail["row_count"], "fields": detail["fields"], "timestamp_column": detail["timestamp_column"],
        "event_time": detail["timestamp_column"] or "UNVERIFIED", "source_observed_time": "UNVERIFIED_REQUIRES_SOURCE_CONTRACT",
        "publication_delay": "UNVERIFIED", "coverage": "FILE_PRESENT_NOT_COVERAGE_QUALIFIED", "file_format": path.suffix.lower().lstrip("."),
        "size_bytes": stat.st_size if stat else -1,
        "modified_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat() if stat else "",
        "file_stat_status": "READ_METADATA_SAMPLE" if stat else "NOT_SAMPLED",
        "provenance": str(root), "licensing_access": "INTERNAL_ACCESS_PRESENT_LICENSE_REVIEW_REQUIRED",
        "contains_future_revisions": "UNKNOWN", "physical_split_possible": True,
        "data_role": "SEALED_METADATA_ONLY" if sealed else "INVENTORY_ONLY_NO_PERFORMANCE",
        "sealed_path": sealed, "row_data_read": False, "footer_status": "BLOCKED_SEALED_PATH" if sealed else detail["footer_status"],
    }


def aggregate_family(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[(row["machine"], row["venue"], row["market_type"], row["data_family"], row["dataset_root"])].append(row)
    output = []
    for key, group in sorted(groups.items()):
        months = sorted({row["month"] for row in group if row["month"] != "UNKNOWN"})
        symbols = sorted({row["symbol"] for row in group if row["symbol"] != "UNKNOWN"})
        fields = sorted({field for row in group for field in row["fields"].split("|") if field and not field.startswith("ARCHIVE_")})
        output.append({
            "machine": key[0], "venue": key[1], "market_type": key[2], "data_family": key[3], "dataset_root": key[4],
            "files": len(group), "known_size_bytes": sum(max(0, int(row["size_bytes"])) for row in group),
            "size_known_files": sum(int(row["size_bytes"]) >= 0 for row in group),
            "known_rows_in_metadata_samples": sum(max(0, int(row["row_count"])) for row in group),
            "symbols": "|".join(symbols), "symbol_count": len(symbols),
            "months": "|".join(months), "month_count": len(months), "start": min((row["start"] for row in group if row["start"]), default=""),
            "end": max((row["end"] for row in group if row["end"]), default=""), "fields": "|".join(fields),
            "sealed_files": sum(bool(row["sealed_path"]) for row in group), "row_data_read": False,
            "qualification": "DISCOVERED_REQUIRES_OBSERVABLE_TIME_AND_COVERAGE_QUALIFICATION",
        })
    return output


def availability(families: list[dict[str, Any]]) -> dict[str, Any]:
    present = defaultdict(list)
    for row in families:
        if row["files"] and row["sealed_files"] < row["files"]:
            present[row["data_family"]].append(row)
    venues = {row["venue"] for row in families if row["venue"] != "UNKNOWN" and row["files"]}
    def status(*names: str) -> str:
        return "DISCOVERED_REQUIRES_QUALIFICATION" if any(present[name] for name in names) else "UNAVAILABLE_NO_VERIFIED_HISTORICAL_SOURCE"
    return {
        "cross_venue_price_discovery": "DISCOVERED_REQUIRES_QUALIFICATION" if len(venues) >= 2 else "UNAVAILABLE_NO_VERIFIED_HISTORICAL_SOURCE",
        "native_bbo": status("BOOKTICKER_BBO"),
        "multi_level_depth": status("ORDER_BOOK_DEPTH"),
        "forced_flow_liquidation": status("LIQUIDATION_FORCE_ORDER"),
        "options_expectation_state": status("OPTIONS"),
        "trade_flow": status("AGG_TRADES", "TRADES", "TAKER_FLOW"),
        "observed_venues": sorted(venues),
        "proxy_substitution_allowed": False,
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("\n", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def iter_data_files(root: Path) -> Iterable[Path]:
    """Yield the complete supported-file inventory in deterministic order."""
    for directory, child_directories, files in os.walk(root):
        child_directories.sort(key=str.casefold)
        for name in sorted(files, key=str.casefold):
            path = Path(directory) / name
            if path.suffix.lower() in FILE_EXTENSIONS:
                yield path


def run(roots: list[Path], output: Path, metadata_samples_per_dataset: int = 3) -> None:
    started = time.perf_counter(); output.mkdir(parents=True, exist_ok=True)
    machine = socket.gethostname(); rows = []
    sampled: dict[tuple[str, str], int] = defaultdict(int)
    metadata_files_inspected = 0
    for root in roots:
        if not root.exists():
            continue
        for path in iter_data_files(root):
            try:
                key = (str(root), dataset_root(path, root))
                inspect_metadata = sampled[key] < metadata_samples_per_dataset
                rows.append(inventory_file(path, root, machine, inspect_metadata=inspect_metadata))
                if inspect_metadata and not is_sealed(path):
                    sampled[key] += 1
                    metadata_files_inspected += 1
            except (OSError, PermissionError):
                continue
    families = aggregate_family(rows)
    ledger_map: dict[tuple[str, str, str, str, str], dict[str, Any]] = {}
    for row in rows:
        if row["symbol"] == "UNKNOWN" or row["month"] == "UNKNOWN":
            continue
        key = (row["machine"], row["venue"], row["data_family"], row["symbol"], row["month"])
        item = ledger_map.setdefault(key, {"machine": key[0], "venue": key[1], "data_family": key[2], "symbol": key[3], "month": key[4], "files": 0, "known_size_bytes": 0, "size_known_files": 0, "known_rows_in_metadata_samples": 0, "sealed_files": 0})
        item["files"] += 1
        item["known_size_bytes"] += max(0, int(row["size_bytes"]))
        item["size_known_files"] += int(row["size_bytes"]) >= 0
        item["known_rows_in_metadata_samples"] += max(0, int(row["row_count"]))
        item["sealed_files"] += bool(row["sealed_path"])
    write_csv(output / "file_inventory.csv", rows)
    write_csv(output / "data_family_inventory.csv", families)
    write_csv(output / "symbol_month_ledger.csv", list(ledger_map.values()))
    availability_payload = availability(families)
    (output / "mechanism_source_availability.json").write_text(json.dumps(availability_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    artifacts = [output / name for name in ("file_inventory.csv", "data_family_inventory.csv", "symbol_month_ledger.csv", "mechanism_source_availability.json")]
    manifest = {
        "experiment_id": "20260712_mechanism_data_inventory_001", "machine": machine,
        "roots": [str(root) for root in roots], "files": len(rows), "families": len(families),
        "row_data_read": False, "sealed_paths_footer_read": False, "performance_queries": 0,
        "metadata_samples_per_dataset": metadata_samples_per_dataset,
        "metadata_files_inspected": metadata_files_inspected,
        "scan_seconds": time.perf_counter() - started,
        "outputs": [{"path": str(path), "sha256": sha256_file(path)} for path in artifacts],
        "reproducible": True,
    }
    (output / "inventory_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "INVENTORY_COMPLETED", "machine": machine, "files": len(rows), "families": len(families), "seconds": manifest["scan_seconds"], "availability": availability_payload}, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", action="append", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--metadata-samples-per-dataset", type=int, default=3)
    args = parser.parse_args()
    if args.metadata_samples_per_dataset < 0:
        parser.error("--metadata-samples-per-dataset must be non-negative")
    run([Path(value) for value in args.root], Path(args.output), args.metadata_samples_per_dataset)


if __name__ == "__main__":
    main()
