"""Fail-closed ingress for an external liquidation history release.

The supplier archive and a Binance WebSocket capture are independent sources.
This module qualifies the supplier release, quarantines contracts whose notional
requires an explicit multiplier, and compares overlapping event streams.  It
does not stitch sources or authorize research use.
"""

from __future__ import annotations

import hashlib
import json
import re
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
import pandas as pd
import pyarrow.dataset as pyarrow_dataset
import pyarrow.parquet as parquet


LINEAR_SYMBOL = re.compile(r"^[A-Z0-9]+(?:USDT|USDC)$")
SUPPORTED_EVENT_SUFFIXES = {".parquet", ".csv", ".json", ".jsonl", ".ndjson"}


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def classify_contract(symbol: str) -> str:
    normalized = str(symbol).upper()
    if LINEAR_SYMBOL.fullmatch(normalized):
        return "LINEAR_QUOTE_MARGIN"
    if "USD_" in normalized or normalized.endswith("_PERP"):
        return "INVERSE_OR_DELIVERY"
    return "UNKNOWN_CONTRACT_SEMANTICS"


def _dates(start: str, end: str) -> tuple[str, ...]:
    return tuple(
        pd.date_range(start, end, freq="D", tz="UTC").strftime("%Y-%m-%d").tolist()
    )


def _partition_paths(root: Path, layer: str, dates: Sequence[str]) -> tuple[Path, ...]:
    layer_root = root / Path(layer)
    expected = tuple(layer_root / f"date={date}" / "part-000.parquet" for date in dates)
    missing = [path.as_posix() for path in expected if not path.is_file()]
    actual = set(layer_root.glob("date=*/*.parquet")) if layer_root.is_dir() else set()
    extra = sorted(path.as_posix() for path in actual - set(expected))
    if missing or extra:
        raise ValueError(
            f"partition identity mismatch for {layer}: missing={missing[:5]} extra={extra[:5]}"
        )
    return expected


def _file_record(root: Path, layer: str, path: Path) -> dict[str, Any]:
    return {
        "layer": layer,
        "path": path.relative_to(root).as_posix(),
        "sha256": sha256_file(path),
        "size_bytes": path.stat().st_size,
        "rows": parquet.ParquetFile(path).metadata.num_rows,
    }


def _file_records(
    root: Path, silver: Sequence[Path], gold: Sequence[Path], workers: int
) -> list[dict[str, Any]]:
    jobs = [("silver_events", path) for path in silver] + [
        ("gold_hourly_sparse", path) for path in gold
    ]
    with ThreadPoolExecutor(max_workers=max(1, min(int(workers), 16))) as pool:
        records = list(pool.map(lambda job: _file_record(root, job[0], job[1]), jobs))
    return sorted(records, key=lambda row: (row["layer"], row["path"]))


def _schema_columns(path: Path) -> tuple[str, ...]:
    return tuple(parquet.ParquetFile(path).schema_arrow.names)


def _check_required_columns(
    paths: Sequence[Path], required: Sequence[str], layer: str
) -> tuple[tuple[str, ...], list[str]]:
    schema = _schema_columns(paths[0])
    failures: list[str] = []
    missing = sorted(set(required) - set(schema))
    if missing:
        failures.append(f"{layer}:MISSING_COLUMNS:{','.join(missing)}")
    for path in paths[1:]:
        if _schema_columns(path) != schema:
            failures.append(f"{layer}:SCHEMA_DRIFT:{path.name}")
            break
    return schema, failures


@dataclass(frozen=True)
class SupplierPreflight:
    evidence: dict[str, Any]
    partition_records: tuple[dict[str, Any], ...]


def preflight_supplier_release(config: Mapping[str, Any]) -> SupplierPreflight:
    release = config["release"]
    root = Path(release["root"]).resolve()
    if not root.is_dir():
        raise FileNotFoundError(root)
    summary_path = root / "summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    dates = _dates(release["start_date"], release["end_date"])
    silver = _partition_paths(root, release["silver_layer"], dates)
    gold = _partition_paths(root, release["gold_layer"], dates)
    failures: list[str] = []
    warnings: list[str] = []

    silver_schema, schema_failures = _check_required_columns(
        silver, config["schemas"]["silver_required"], "silver"
    )
    failures.extend(schema_failures)
    gold_schema, schema_failures = _check_required_columns(
        gold, config["schemas"]["gold_required"], "gold"
    )
    failures.extend(schema_failures)

    records = _file_records(root, silver, gold, config["hash_workers"])
    silver_rows = sum(row["rows"] for row in records if row["layer"] == "silver_events")
    gold_rows = sum(row["rows"] for row in records if row["layer"] == "gold_hourly_sparse")

    gold_columns = [
        "symbol",
        "timestamp",
        "liquidation_event_count",
        "liquidation_buy_count",
        "liquidation_sell_count",
        "liquidation_total_notional",
        "liquidation_event_notional_max",
        "feature_available_time",
        "execution_time_min",
        "first_observable_time",
        "last_observable_time",
        "exact_duplicate_rows_dropped",
    ]
    gold_frame = pyarrow_dataset.dataset(
        [str(path) for path in gold], format="parquet"
    ).to_table(columns=gold_columns).to_pandas()
    for column in (
        "timestamp",
        "feature_available_time",
        "execution_time_min",
        "first_observable_time",
        "last_observable_time",
    ):
        gold_frame[column] = pd.to_datetime(gold_frame[column], utc=True, errors="coerce")

    if gold_frame[gold_columns].isna().any().any():
        failures.append("GOLD_REQUIRED_VALUE_MISSING")
    if gold_frame.duplicated(["symbol", "timestamp"]).any():
        failures.append("GOLD_PRIMARY_KEY_DUPLICATE")
    if not gold_frame["liquidation_event_count"].eq(
        gold_frame["liquidation_buy_count"] + gold_frame["liquidation_sell_count"]
    ).all():
        failures.append("SIDE_COUNT_RECONCILIATION_FAILED")
    if (gold_frame["liquidation_total_notional"] < 0).any():
        failures.append("NEGATIVE_LIQUIDATION_NOTIONAL")
    if not gold_frame["feature_available_time"].eq(
        gold_frame["timestamp"] + pd.Timedelta(hours=1)
    ).all():
        failures.append("FEATURE_AVAILABLE_TIME_DRIFT")
    if not gold_frame["execution_time_min"].eq(
        gold_frame["timestamp"] + pd.Timedelta(hours=2)
    ).all():
        failures.append("EXECUTION_DELAY_DRIFT")
    if (gold_frame["first_observable_time"] < gold_frame["timestamp"]).any() or (
        gold_frame["last_observable_time"] >= gold_frame["timestamp"] + pd.Timedelta(hours=1)
    ).any():
        failures.append("OBSERVABLE_TIME_OUTSIDE_SOURCE_BUCKET")

    expected = release["expected_summary"]
    observed_summary = {
        "daily_partition_count": len(dates),
        "silver_rows": int(silver_rows),
        "gold_rows": int(gold_rows),
        "symbol_count": int(gold_frame["symbol"].nunique()),
        "event_count": int(gold_frame["liquidation_event_count"].sum()),
        "parse_error_count": int(summary.get("parse_error_count", -1)),
        "unknown_side_count": int(summary.get("unknown_side_count", -1)),
        "source_date_mismatch_count": int(summary.get("source_date_mismatch_count", -1)),
    }
    for key, value in expected.items():
        if observed_summary.get(key) != value:
            failures.append(f"SUMMARY_MISMATCH:{key}")
    if summary.get("status") != "complete":
        failures.append("SOURCE_SUMMARY_NOT_COMPLETE")

    gold_frame["contract_class"] = gold_frame["symbol"].map(classify_contract)
    class_rows: list[dict[str, Any]] = []
    for contract_class, block in gold_frame.groupby("contract_class", sort=True):
        class_rows.append(
            {
                "contract_class": contract_class,
                "symbols": int(block["symbol"].nunique()),
                "hourly_rows": int(len(block)),
                "events": int(block["liquidation_event_count"].sum()),
                "raw_supplier_notional": float(block["liquidation_total_notional"].sum()),
                "maximum_raw_event_notional": float(
                    block["liquidation_event_notional_max"].max()
                ),
                "notional_comparable": contract_class == "LINEAR_QUOTE_MARGIN",
            }
        )
    quarantined = gold_frame.loc[
        gold_frame["contract_class"] != "LINEAR_QUOTE_MARGIN", "symbol"
    ].drop_duplicates()
    if len(quarantined):
        warnings.append("NONLINEAR_AND_UNKNOWN_NOTIONAL_QUARANTINED")

    silver_records = [row for row in records if row["layer"] == "silver_events"]
    gold_records = [row for row in records if row["layer"] == "gold_hourly_sparse"]
    evidence: dict[str, Any] = {
        "schema_version": 1,
        "release_id": release["release_id"],
        "status": "QUALIFIED_QUARANTINED" if not failures else "INGRESS_PREFLIGHT_FAILED",
        "research_admitted": False,
        "stitching_allowed": False,
        "stitching_status": "BLOCKED_PENDING_OVERLAP_QUALIFICATION",
        "release_root": root.as_posix(),
        "source_summary_sha256": sha256_file(summary_path),
        "silver_bundle_sha256": canonical_sha256(silver_records),
        "gold_bundle_sha256": canonical_sha256(gold_records),
        "partition_manifest_sha256": canonical_sha256(records),
        "partition_files": len(records),
        "date_range": {
            "start": release["start_date"],
            "end": release["end_date"],
            "partitions": len(dates),
        },
        "observed": {
            **observed_summary,
            "first_timestamp": gold_frame["timestamp"].min().isoformat(),
            "last_timestamp": gold_frame["timestamp"].max().isoformat(),
            "active_dates": int(gold_frame["timestamp"].dt.floor("D").nunique()),
            "minimum_active_symbols_per_day": int(
                gold_frame.groupby(gold_frame["timestamp"].dt.floor("D"))["symbol"]
                .nunique()
                .min()
            ),
            "median_active_symbols_per_day": float(
                gold_frame.groupby(gold_frame["timestamp"].dt.floor("D"))["symbol"]
                .nunique()
                .median()
            ),
            "raw_supplier_notional": float(gold_frame["liquidation_total_notional"].sum()),
            "exact_duplicate_rows_dropped": int(
                gold_frame["exact_duplicate_rows_dropped"].sum()
            ),
        },
        "schemas": {
            "silver_columns": list(silver_schema),
            "gold_columns": list(gold_schema),
        },
        "contract_classification": class_rows,
        "notional_comparable_rule": "symbol matches ^[A-Z0-9]+(?:USDT|USDC)$",
        "quarantined_notional_symbols": sorted(quarantined.astype(str).tolist()),
        "pit_contract": {
            "event_observable_time": "supplier received_time",
            "hourly_feature_available_time": "timestamp + 1h",
            "minimum_execution_time": "timestamp + 2h",
            "partial_current_hour": "PROHIBITED",
        },
        "failures": sorted(set(failures)),
        "warnings": sorted(set(warnings)),
        "boundaries": dict(config["boundaries"]),
    }
    evidence["release_identity_sha256"] = canonical_sha256(
        {
            "release_id": evidence["release_id"],
            "source_summary_sha256": evidence["source_summary_sha256"],
            "silver_bundle_sha256": evidence["silver_bundle_sha256"],
            "gold_bundle_sha256": evidence["gold_bundle_sha256"],
            "partition_manifest_sha256": evidence["partition_manifest_sha256"],
        }
    )
    return SupplierPreflight(evidence, tuple(records))


def _read_event_file(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".parquet":
        return pd.read_parquet(path)
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix in {".jsonl", ".ndjson"}:
        return pd.read_json(path, lines=True)
    if suffix == ".json":
        return pd.read_json(path)
    raise ValueError(f"unsupported WebSocket event file: {path}")


def _first_column(frame: pd.DataFrame, candidates: Iterable[str]) -> str | None:
    return next((column for column in candidates if column in frame.columns), None)


def _utc_timestamp(values: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(values, errors="coerce")
    if numeric.notna().mean() > 0.95:
        median = float(numeric.dropna().abs().median())
        unit = "ns" if median >= 1e17 else "us" if median >= 1e14 else "ms" if median >= 1e11 else "s"
        return pd.to_datetime(numeric, unit=unit, utc=True, errors="coerce")
    return pd.to_datetime(values, utc=True, errors="coerce")


def normalize_events(frame: pd.DataFrame, mapping: Mapping[str, Sequence[str]]) -> pd.DataFrame:
    if "payload" in frame.columns and frame["payload"].map(
        lambda value: isinstance(value, Mapping)
    ).any():
        payload = pd.json_normalize(
            frame["payload"].map(
                lambda value: value if isinstance(value, Mapping) else {}
            )
        )
        for column in payload.columns:
            if column not in frame.columns:
                frame[column] = payload[column]
    if "o" in frame.columns and frame["o"].map(lambda value: isinstance(value, Mapping)).any():
        order = pd.json_normalize(frame["o"].map(lambda value: value if isinstance(value, Mapping) else {}))
        order.columns = [f"o.{column}" for column in order.columns]
        frame = pd.concat([frame.reset_index(drop=True), order.reset_index(drop=True)], axis=1)
    event_column = _first_column(frame, mapping["event_time"])
    symbol_column = _first_column(frame, mapping["symbol"])
    side_column = _first_column(frame, mapping["side"])
    notional_column = _first_column(frame, mapping["notional"])
    quantity_column = _first_column(frame, mapping["quantity"])
    price_column = _first_column(frame, mapping["price"])
    missing = [
        name
        for name, value in (("event_time", event_column), ("symbol", symbol_column))
        if value is None
    ]
    if notional_column is None and (quantity_column is None or price_column is None):
        missing.append("notional_or_quantity_price")
    if missing:
        raise ValueError(f"event schema cannot be normalized: {missing}")
    result = pd.DataFrame(
        {
            "event_time": _utc_timestamp(frame[event_column]),
            "symbol": frame[symbol_column].astype(str).str.upper(),
            "side": frame[side_column].astype(str).str.upper() if side_column else "UNKNOWN",
        }
    )
    if notional_column:
        result["notional"] = pd.to_numeric(frame[notional_column], errors="coerce")
    else:
        result["notional"] = pd.to_numeric(frame[quantity_column], errors="coerce") * pd.to_numeric(
            frame[price_column], errors="coerce"
        )
    result["contract_class"] = result["symbol"].map(classify_contract)
    return result.loc[
        result["event_time"].notna()
        & result["symbol"].ne("")
        & np.isfinite(result["notional"])
        & result["notional"].ge(0)
    ].reset_index(drop=True)


def load_ws_events(root: Path, mapping: Mapping[str, Sequence[str]]) -> tuple[pd.DataFrame, list[str]]:
    files = sorted(
        path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in SUPPORTED_EVENT_SUFFIXES
    )
    if not files:
        raise FileNotFoundError(f"no supported WebSocket event files under {root}")
    frames = [normalize_events(_read_event_file(path), mapping) for path in files]
    return pd.concat(frames, ignore_index=True), [path.as_posix() for path in files]


def _load_vendor_overlap_events(
    release_root: Path,
    start_date: str,
    end_date: str,
    mapping: Mapping[str, Sequence[str]],
) -> pd.DataFrame:
    paths = _partition_paths(
        release_root, "silver/events_daily", _dates(start_date, end_date)
    )
    columns = sorted({column for values in mapping.values() for column in values})
    frames = []
    for path in paths:
        available = set(_schema_columns(path))
        read_columns = [column for column in columns if column in available]
        frames.append(normalize_events(pd.read_parquet(path, columns=read_columns), mapping))
    return pd.concat(frames, ignore_index=True)


def _symmetric_coverage(left: float, right: float) -> float:
    high = max(float(left), float(right))
    return 1.0 if high == 0 else min(float(left), float(right)) / high


def qualify_overlap(
    config: Mapping[str, Any],
    preflight: Mapping[str, Any],
    ws_root: Path | None,
) -> tuple[dict[str, Any], pd.DataFrame]:
    if preflight["status"] != "QUALIFIED_QUARANTINED":
        return {
            "status": "STITCHING_BLOCKED_SUPPLIER_PREFLIGHT_FAILED",
            "comparison_pass": False,
            "stitching_allowed": False,
        }, pd.DataFrame()
    if ws_root is None or not ws_root.is_dir():
        return {
            "status": "STITCHING_BLOCKED_NO_WS_OVERLAP_INPUT",
            "comparison_pass": False,
            "stitching_allowed": False,
            "required_metrics": [
                "event_count_coverage",
                "notional_coverage",
                "large_liquidation_count_coverage",
            ],
        }, pd.DataFrame()

    overlap = config["overlap_gate"]
    ws, ws_files = load_ws_events(ws_root.resolve(), overlap["ws_mapping"])
    ws = ws.loc[ws["contract_class"] == "LINEAR_QUOTE_MARGIN"].copy()
    if ws.empty:
        return {
            "status": "STITCHING_BLOCKED_NO_COMPARABLE_WS_EVENTS",
            "comparison_pass": False,
            "stitching_allowed": False,
            "ws_files": ws_files,
        }, pd.DataFrame()
    release_start = pd.Timestamp(config["release"]["start_date"], tz="UTC")
    release_end = pd.Timestamp(config["release"]["end_date"], tz="UTC")
    start = max(release_start, ws["event_time"].min().floor("D"))
    end = min(release_end, ws["event_time"].max().floor("D"))
    if start > end:
        return {
            "status": "STITCHING_BLOCKED_NO_DATE_OVERLAP",
            "comparison_pass": False,
            "stitching_allowed": False,
            "ws_files": ws_files,
        }, pd.DataFrame()

    vendor = _load_vendor_overlap_events(
        Path(config["release"]["root"]).resolve(),
        start.strftime("%Y-%m-%d"),
        end.strftime("%Y-%m-%d"),
        overlap["vendor_mapping"],
    )
    vendor = vendor.loc[vendor["contract_class"] == "LINEAR_QUOTE_MARGIN"].copy()
    common_symbols = sorted(set(vendor["symbol"]) & set(ws["symbol"]))
    vendor = vendor.loc[vendor["symbol"].isin(common_symbols)].copy()
    ws = ws.loc[
        ws["symbol"].isin(common_symbols)
        & ws["event_time"].ge(start)
        & ws["event_time"].lt(end + pd.Timedelta(days=1))
    ].copy()
    vendor = vendor.loc[
        vendor["event_time"].ge(start)
        & vendor["event_time"].lt(end + pd.Timedelta(days=1))
    ].copy()
    vendor["date"] = vendor["event_time"].dt.floor("D")
    ws["date"] = ws["event_time"].dt.floor("D")

    def aggregate(frame: pd.DataFrame, prefix: str) -> pd.DataFrame:
        rows = frame.groupby(["date", "symbol"], sort=True).agg(
            **{
                f"{prefix}_events": ("notional", "size"),
                f"{prefix}_notional": ("notional", "sum"),
            }
        )
        for threshold in overlap["large_notional_thresholds"]:
            large = frame.loc[frame["notional"] >= float(threshold)].groupby(
                ["date", "symbol"], sort=True
            ).agg(count=("notional", "size"), notional=("notional", "sum"))
            rows[f"{prefix}_large_{int(threshold)}_events"] = large["count"]
            rows[f"{prefix}_large_{int(threshold)}_notional"] = large["notional"]
        return rows.fillna(0).reset_index()

    comparison = aggregate(vendor, "vendor").merge(
        aggregate(ws, "ws"), on=["date", "symbol"], how="outer"
    ).fillna(0)
    vendor_events = int(len(vendor))
    ws_events = int(len(ws))
    vendor_notional = float(vendor["notional"].sum())
    ws_notional = float(ws["notional"].sum())
    large_metrics = []
    for threshold in overlap["large_notional_thresholds"]:
        vendor_large = int((vendor["notional"] >= float(threshold)).sum())
        ws_large = int((ws["notional"] >= float(threshold)).sum())
        large_metrics.append(
            {
                "threshold": float(threshold),
                "vendor_events": vendor_large,
                "ws_events": ws_large,
                "count_ratio_vendor_to_ws": None if ws_large == 0 else vendor_large / ws_large,
                "count_coverage": _symmetric_coverage(vendor_large, ws_large),
                "support_pass": min(vendor_large, ws_large)
                >= int(overlap["minimum_large_events_per_threshold"]),
            }
        )

    overlap_days = int(comparison["date"].nunique())
    checks = {
        "minimum_overlap_days": overlap_days >= int(overlap["minimum_overlap_days"]),
        "minimum_common_symbols": len(common_symbols) >= int(overlap["minimum_common_symbols"]),
        "minimum_ws_events": ws_events >= int(overlap["minimum_ws_events"]),
        "event_count_coverage": _symmetric_coverage(vendor_events, ws_events)
        >= float(overlap["minimum_event_count_coverage"]),
        "notional_coverage": _symmetric_coverage(vendor_notional, ws_notional)
        >= float(overlap["minimum_notional_coverage"]),
        "large_liquidation_count_coverage": all(
            item["support_pass"]
            and item["count_coverage"] >= float(overlap["minimum_large_count_coverage"])
            for item in large_metrics
        ),
    }
    passed = all(checks.values())
    result = {
        "status": (
            "STITCHING_ELIGIBLE_PENDING_EXPLICIT_ACTIVATION"
            if passed
            else "STITCHING_BLOCKED_OVERLAP_MISMATCH_OR_UNDERPOWERED"
        ),
        "comparison_pass": passed,
        "stitching_allowed": False,
        "explicit_activation_required": True,
        "comparison_universe": "COMMON_LINEAR_USDT_USDC_CONTRACTS_ONLY",
        "overlap_start": start.isoformat(),
        "overlap_end": end.isoformat(),
        "overlap_days": overlap_days,
        "common_symbols": len(common_symbols),
        "vendor_events": vendor_events,
        "ws_events": ws_events,
        "event_count_ratio_vendor_to_ws": None if ws_events == 0 else vendor_events / ws_events,
        "event_count_coverage": _symmetric_coverage(vendor_events, ws_events),
        "vendor_notional": vendor_notional,
        "ws_notional": ws_notional,
        "notional_ratio_vendor_to_ws": None if ws_notional == 0 else vendor_notional / ws_notional,
        "notional_coverage": _symmetric_coverage(vendor_notional, ws_notional),
        "large_liquidation_metrics": large_metrics,
        "checks": checks,
        "ws_files": ws_files,
        "claim_boundary": "SOURCE_COMPATIBILITY_ONLY_NO_RESEARCH_OR_ECONOMIC_CLAIM",
    }
    result["comparison_identity_sha256"] = canonical_sha256(
        {key: value for key, value in result.items() if key not in {"ws_files"}}
    )
    return result, comparison
