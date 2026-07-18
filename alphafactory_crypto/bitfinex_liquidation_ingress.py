"""Independent preflight for the Bitfinex historical liquidation archive.

This module verifies the downloaded files and the internally materialized
aggregates.  It deliberately does *not* qualify the archive as a Binance
``forceOrder`` reference, a CryptoHFT coverage control, or a research input.
Historical REST event timestamps are not publication receipts, and the current
archive does not contain a page/request ledger that proves empty tail periods
were actually queried.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd
import pyarrow.parquet as parquet


BITFINEX_UST_LINEAR = re.compile(r"^T[A-Z0-9]+F0:USTF0$")


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


def classify_symbol(symbol: str) -> str:
    value = str(symbol).upper()
    if "TEST" in value:
        return "TEST_SYMBOL_QUARANTINED"
    if BITFINEX_UST_LINEAR.fullmatch(value):
        return "USTF0_QUOTE_PROXY"
    if ":" in value:
        return "NON_UST_DERIVATIVE_QUOTE_QUARANTINED"
    return "LEGACY_OR_UNKNOWN_SYMBOL_QUARANTINED"


def _months(start: str, end: str) -> tuple[str, ...]:
    return tuple(pd.period_range(start, end, freq="M").astype(str).tolist())


def _raw_rows(path: Path) -> int:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, list):
        raise ValueError(f"raw payload must be a JSON list: {path}")
    return len(payload)


def _effective_count(counts: Sequence[int] | np.ndarray) -> float:
    values = np.asarray(counts, dtype=float)
    total = float(values.sum())
    if total <= 0:
        return 0.0
    shares = values / total
    return float(1.0 / np.square(shares).sum())


def _schema(path: Path) -> tuple[str, ...]:
    return tuple(parquet.ParquetFile(path).schema_arrow.names)


def _file_record(root: Path, path: Path, rows: int | None = None) -> dict[str, Any]:
    return {
        "path": path.relative_to(root).as_posix(),
        "size_bytes": int(path.stat().st_size),
        "sha256": sha256_file(path),
        "rows": rows,
    }


def _as_utc(frame: pd.DataFrame, columns: Sequence[str]) -> None:
    for column in columns:
        frame[column] = pd.to_datetime(frame[column], utc=True, errors="coerce")


def _compare_gold(
    silver: pd.DataFrame,
    gold: pd.DataFrame,
    resolution: str,
) -> list[str]:
    failures: list[str] = []
    required = {
        "venue",
        "symbol",
        "timestamp",
        "liquidation_count",
        "liquidation_notional",
        "max_liquidation_notional",
        "long_liquidation_notional",
        "short_liquidation_notional",
        "liquidation_imbalance",
        "feature_available_time",
        "execution_time_min",
    }
    if not required.issubset(gold.columns):
        return [f"GOLD_{resolution}_MISSING_COLUMNS"]
    _as_utc(gold, ("timestamp", "feature_available_time", "execution_time_min"))
    if gold[list(required)].isna().any().any():
        failures.append(f"GOLD_{resolution}_REQUIRED_VALUE_MISSING")
    if gold.duplicated(["venue", "symbol", "timestamp"]).any():
        failures.append(f"GOLD_{resolution}_PRIMARY_KEY_DUPLICATE")
    offset = pd.Timedelta(resolution)
    if not gold["feature_available_time"].eq(gold["timestamp"] + offset).all():
        failures.append(f"GOLD_{resolution}_FEATURE_AVAILABLE_TIME_DRIFT")
    if not gold["execution_time_min"].eq(
        gold["feature_available_time"] + pd.Timedelta(hours=1)
    ).all():
        failures.append(f"GOLD_{resolution}_EXECUTION_DELAY_DRIFT")

    work = silver.copy()
    work["timestamp"] = work["timestamp"].dt.floor(resolution)
    work["long_notional"] = work["notional"].where(work["side"].eq("LONG"), 0.0)
    work["short_notional"] = work["notional"].where(work["side"].eq("SHORT"), 0.0)
    expected = (
        work.groupby(["venue", "symbol", "timestamp"], sort=True)
        .agg(
            liquidation_count=("notional", "size"),
            liquidation_notional=("notional", "sum"),
            max_liquidation_notional=("notional", "max"),
            long_liquidation_notional=("long_notional", "sum"),
            short_liquidation_notional=("short_notional", "sum"),
        )
        .reset_index()
    )
    expected["liquidation_imbalance"] = np.where(
        expected["liquidation_notional"].gt(0),
        (
            expected["short_liquidation_notional"]
            - expected["long_liquidation_notional"]
        )
        / expected["liquidation_notional"],
        0.0,
    )
    columns = [
        "venue",
        "symbol",
        "timestamp",
        "liquidation_count",
        "liquidation_notional",
        "max_liquidation_notional",
        "long_liquidation_notional",
        "short_liquidation_notional",
        "liquidation_imbalance",
    ]
    observed = gold[columns].sort_values(columns[:3]).reset_index(drop=True)
    expected = expected[columns].sort_values(columns[:3]).reset_index(drop=True)
    if len(observed) != len(expected) or not observed[columns[:3]].equals(
        expected[columns[:3]]
    ):
        failures.append(f"GOLD_{resolution}_KEY_OR_ROW_MISMATCH")
        return failures
    if not observed["liquidation_count"].equals(expected["liquidation_count"]):
        failures.append(f"GOLD_{resolution}_COUNT_RECONCILIATION_FAILED")
    for column in columns[4:]:
        if not np.allclose(
            observed[column].to_numpy(dtype=float),
            expected[column].to_numpy(dtype=float),
            rtol=1e-10,
            atol=1e-8,
            equal_nan=False,
        ):
            failures.append(f"GOLD_{resolution}_{column.upper()}_RECONCILIATION_FAILED")
    return failures


@dataclass(frozen=True)
class BitfinexPreflight:
    evidence: dict[str, Any]
    file_records: tuple[dict[str, Any], ...]


def preflight_bitfinex_release(config: Mapping[str, Any]) -> BitfinexPreflight:
    release = config["release"]
    root = Path(release["root"]).resolve()
    if not root.is_dir():
        raise FileNotFoundError(root)

    expected_months = _months(release["start_date"], release["end_date"])
    failures: list[str] = []
    warnings: list[str] = []
    records: list[dict[str, Any]] = []
    status_path = root / "status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    records.append(_file_record(root, status_path))
    if status.get("status") != "complete":
        failures.append("DOWNLOAD_STATUS_NOT_COMPLETE")
    if int(status.get("completed_months", -1)) != len(expected_months):
        failures.append("DOWNLOAD_COMPLETED_MONTH_COUNT_MISMATCH")

    manifest_rows: list[dict[str, Any]] = []
    silver_frames: list[pd.DataFrame] = []
    gold_frames: dict[str, list[pd.DataFrame]] = {
        resolution: [] for resolution in config["gold_resolutions"]
    }
    silver_schema: tuple[str, ...] | None = None
    gold_schemas: dict[str, tuple[str, ...]] = {}

    for month in expected_months:
        manifest_path = root / "manifests" / f"{month}.json"
        raw_path = root / "raw" / f"bitfinex_liquidations_{month}.json.gz"
        silver_path = root / "silver" / f"month={month}" / "part.parquet"
        expected_paths = [manifest_path, raw_path, silver_path]
        expected_paths.extend(
            root / "gold" / resolution / f"month={month}" / "part.parquet"
            for resolution in config["gold_resolutions"]
        )
        missing = [path.as_posix() for path in expected_paths if not path.is_file()]
        if missing:
            failures.append(f"MISSING_MONTH_FILES:{month}")
            continue

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest_rows.append(manifest)
        if manifest.get("status") != "ok" or manifest.get("month") != month:
            failures.append(f"MONTH_MANIFEST_STATUS_OR_ID_MISMATCH:{month}")
        if manifest.get("source") != release["source"]:
            failures.append(f"MONTH_SOURCE_MISMATCH:{month}")
        raw_rows = _raw_rows(raw_path)
        raw_hash = sha256_file(raw_path)
        if raw_rows != int(manifest.get("raw_rows", -1)):
            failures.append(f"RAW_ROW_COUNT_MISMATCH:{month}")
        if raw_hash.lower() != str(manifest.get("raw_sha256", "")).lower():
            failures.append(f"RAW_SHA256_MISMATCH:{month}")
        records.append(_file_record(root, manifest_path))
        records.append(
            {
                "path": raw_path.relative_to(root).as_posix(),
                "size_bytes": int(raw_path.stat().st_size),
                "sha256": raw_hash.upper(),
                "rows": raw_rows,
            }
        )

        observed_silver_rows = parquet.ParquetFile(silver_path).metadata.num_rows
        if observed_silver_rows != int(manifest.get("silver_rows", -1)):
            failures.append(f"SILVER_ROW_COUNT_MISMATCH:{month}")
        schema = _schema(silver_path)
        if silver_schema is None:
            silver_schema = schema
        elif schema != silver_schema:
            failures.append(f"SILVER_SCHEMA_DRIFT:{month}")
        frame = pd.read_parquet(silver_path)
        frame["source_month"] = month
        silver_frames.append(frame)
        records.append(_file_record(root, silver_path, observed_silver_rows))

        for resolution in config["gold_resolutions"]:
            gold_path = root / "gold" / resolution / f"month={month}" / "part.parquet"
            observed_rows = parquet.ParquetFile(gold_path).metadata.num_rows
            if observed_rows != int(manifest.get("gold_rows", {}).get(resolution, -1)):
                failures.append(f"GOLD_ROW_COUNT_MISMATCH:{resolution}:{month}")
            schema = _schema(gold_path)
            if resolution not in gold_schemas:
                gold_schemas[resolution] = schema
            elif schema != gold_schemas[resolution]:
                failures.append(f"GOLD_SCHEMA_DRIFT:{resolution}:{month}")
            gold_frame = pd.read_parquet(gold_path)
            gold_frame["source_month"] = month
            gold_frames[resolution].append(gold_frame)
            records.append(_file_record(root, gold_path, observed_rows))

    if not silver_frames:
        raise ValueError("no readable silver partitions")
    silver = pd.concat(silver_frames, ignore_index=True)
    required = set(config["schemas"]["silver_required"])
    if not required.issubset(silver.columns):
        failures.append("SILVER_REQUIRED_COLUMNS_MISSING")
    _as_utc(silver, ("timestamp", "source_observable_time"))
    if silver[list(required)].isna().any().any():
        failures.append("SILVER_REQUIRED_VALUE_MISSING")
    if not silver["venue"].eq("bitfinex_derivatives").all():
        failures.append("SILVER_VENUE_DRIFT")
    if not silver["side"].isin(["LONG", "SHORT"]).all():
        failures.append("SILVER_SIDE_DRIFT")
    if not silver["is_match"].eq(1).all():
        failures.append("SILVER_NON_MATCH_ROW_PRESENT")
    if (
        silver["quantity"].le(0).any()
        or silver["price"].le(0).any()
        or silver["notional"].lt(0).any()
    ):
        failures.append("SILVER_NONPOSITIVE_QUANTITY_OR_PRICE")
    if not np.allclose(
        silver["notional"].to_numpy(dtype=float),
        (silver["quantity"] * silver["price"]).to_numpy(dtype=float),
        rtol=1e-10,
        atol=1e-10,
    ):
        failures.append("SILVER_NOTIONAL_RECONCILIATION_FAILED")
    if not silver["source_observable_time"].eq(silver["timestamp"]).all():
        failures.append("SOURCE_OBSERVABLE_TIME_RULE_DRIFT")
    duplicate_columns = [
        "timestamp",
        "symbol",
        "side",
        "quantity",
        "price",
        "position_id",
        "is_match",
        "is_market_sold",
    ]
    if silver.duplicated(duplicate_columns).any():
        failures.append("SILVER_EVENT_IDENTITY_DUPLICATE")

    start = pd.Timestamp(release["start_date"], tz="UTC")
    end_exclusive = pd.Timestamp(release["end_date"], tz="UTC") + pd.Timedelta(days=1)
    if silver["timestamp"].lt(start).any() or silver["timestamp"].ge(end_exclusive).any():
        failures.append("SILVER_TIMESTAMP_OUTSIDE_REQUESTED_INTERVAL")
    for resolution, frames in gold_frames.items():
        if frames:
            failures.extend(_compare_gold(silver, pd.concat(frames, ignore_index=True), resolution))

    silver["contract_class"] = silver["symbol"].map(classify_symbol)
    eligible = silver.loc[silver["contract_class"].eq("USTF0_QUOTE_PROXY")].copy()
    eligible["event_date"] = eligible["timestamp"].dt.floor("D")
    requested_days = int((end_exclusive - start).days)
    month_diagnostics: list[dict[str, Any]] = []
    for month, block in silver.groupby("source_month", sort=True):
        manifest = next(row for row in manifest_rows if row["month"] == month)
        requested_end = pd.Timestamp(manifest["end"], tz="UTC") + pd.Timedelta(days=1)
        last_event = block["timestamp"].max()
        month_diagnostics.append(
            {
                "month": month,
                "raw_rows": int(manifest["raw_rows"]),
                "silver_rows": int(len(block)),
                "active_dates": int(block["timestamp"].dt.floor("D").nunique()),
                "first_event": block["timestamp"].min().isoformat(),
                "last_event": last_event.isoformat(),
                "requested_end_exclusive": requested_end.isoformat(),
                "tail_without_events_days": float(
                    (requested_end - last_event).total_seconds() / 86400.0
                ),
                "page_boundary_like_raw_count": int(manifest["raw_rows"]) % 500
                in {0, 499},
            }
        )

    source_coverage_proof = release.get("source_interval_coverage_ledger")
    # V1 deliberately does not accept file presence as interval proof.  A future
    # ledger must define request bounds, pagination/cursors, terminal responses,
    # and its own content identity before this flag can become true.
    source_interval_verified = False
    if source_coverage_proof:
        warnings.append("SOURCE_INTERVAL_LEDGER_PRESENT_BUT_NOT_QUALIFIED_BY_V1")
    if not source_interval_verified:
        warnings.append("SOURCE_INTERVAL_COMPLETENESS_UNVERIFIED")
    if not bool(release.get("publication_time_available", False)):
        warnings.append("PUBLICATION_TIME_UNAVAILABLE_EVENT_TIME_ONLY")
    warnings.append("NON_UST_AND_LEGACY_NOTIONAL_QUARANTINED")

    event_counts_by_month = eligible.groupby("source_month").size()
    event_counts_by_symbol = eligible.groupby("symbol").size()
    event_counts_by_date = eligible.groupby("event_date").size()
    adequacy_config = config["event_data_adequacy"]
    adequacy_checks = {
        "source_interval_completeness": {
            "observed": source_interval_verified,
            "minimum": True,
            "pass": source_interval_verified,
        },
        "eligible_events": {
            "observed": int(len(eligible)),
            "minimum": int(adequacy_config["minimum_eligible_events"]),
            "pass": len(eligible) >= int(adequacy_config["minimum_eligible_events"]),
        },
        "active_event_dates": {
            "observed": int(eligible["event_date"].nunique()),
            "minimum": int(adequacy_config["minimum_active_event_dates"]),
            "pass": eligible["event_date"].nunique()
            >= int(adequacy_config["minimum_active_event_dates"]),
        },
        "eligible_symbols": {
            "observed": int(eligible["symbol"].nunique()),
            "minimum": int(adequacy_config["minimum_eligible_symbols"]),
            "pass": eligible["symbol"].nunique()
            >= int(adequacy_config["minimum_eligible_symbols"]),
        },
        "effective_independent_months": {
            "observed": _effective_count(event_counts_by_month.to_numpy()),
            "minimum": float(adequacy_config["minimum_effective_months"]),
            "pass": _effective_count(event_counts_by_month.to_numpy())
            >= float(adequacy_config["minimum_effective_months"]),
        },
        "effective_cross_sectional_symbols": {
            "observed": _effective_count(event_counts_by_symbol.to_numpy()),
            "minimum": float(adequacy_config["minimum_effective_symbols"]),
            "pass": _effective_count(event_counts_by_symbol.to_numpy())
            >= float(adequacy_config["minimum_effective_symbols"]),
        },
        "price_label_match_ratio": {
            "observed": None,
            "minimum": float(adequacy_config["minimum_price_label_match_ratio"]),
            "pass": False,
            "reason": "No price/label bridge is included in this ingress package.",
        },
        "turnover_observations": {
            "observed": None,
            "minimum": int(adequacy_config["minimum_turnover_observations"]),
            "pass": False,
            "reason": "No portfolio mapping is authorized by ingress preflight.",
        },
    }
    adequacy_pass = all(row["pass"] for row in adequacy_checks.values())
    internal_pass = not failures
    status_value = (
        "INGRESS_PREFLIGHT_FAILED"
        if not internal_pass
        else "FILE_INTEGRITY_QUALIFIED_SOURCE_COVERAGE_UNVERIFIED"
        if not source_interval_verified
        else "INGRESS_QUALIFIED_RESEARCH_QUARANTINED"
    )
    contract_rows = []
    for contract_class, block in silver.groupby("contract_class", sort=True):
        contract_rows.append(
            {
                "contract_class": contract_class,
                "rows": int(len(block)),
                "symbols": int(block["symbol"].nunique()),
                "raw_quantity_times_price": float(block["notional"].sum()),
                "common_usd_notional_comparable": False,
                "event_study_eligible_proxy": contract_class == "USTF0_QUOTE_PROXY",
            }
        )

    records = sorted(records, key=lambda row: row["path"])
    evidence: dict[str, Any] = {
        "schema_version": 1,
        "release_id": release["release_id"],
        "status": status_value,
        "internal_file_and_aggregation_checks_pass": internal_pass,
        "source_interval_completeness_verified": source_interval_verified,
        "publication_time_available": False,
        "research_admitted": False,
        "binance_reference_allowed": False,
        "cryptohft_coverage_validation_allowed": False,
        "automatic_stitching_allowed": False,
        "release_root": root.as_posix(),
        "file_count": len(records),
        "bundle_sha256": canonical_sha256(records),
        "requested_interval": {
            "start": release["start_date"],
            "end": release["end_date"],
            "calendar_days": requested_days,
            "months": len(expected_months),
        },
        "observed": {
            "raw_rows": int(sum(int(row["raw_rows"]) for row in manifest_rows)),
            "silver_rows": int(len(silver)),
            "first_event": silver["timestamp"].min().isoformat(),
            "last_event": silver["timestamp"].max().isoformat(),
            "active_event_dates": int(silver["timestamp"].dt.floor("D").nunique()),
            "active_date_ratio": float(
                silver["timestamp"].dt.floor("D").nunique() / requested_days
            ),
            "symbols": int(silver["symbol"].nunique()),
            "eligible_ustf0_rows": int(len(eligible)),
            "eligible_ustf0_symbols": int(eligible["symbol"].nunique()),
            "eligible_active_dates": int(eligible["event_date"].nunique()),
            "eligible_median_symbols_per_active_date": float(
                eligible.groupby("event_date")["symbol"].nunique().median()
            ),
            "eligible_effective_months": _effective_count(
                event_counts_by_month.to_numpy()
            ),
            "eligible_effective_symbols": _effective_count(
                event_counts_by_symbol.to_numpy()
            ),
            "eligible_effective_dates": _effective_count(
                event_counts_by_date.to_numpy()
            ),
            "eligible_top_symbol_event_share": float(
                event_counts_by_symbol.max() / event_counts_by_symbol.sum()
            ),
            "eligible_large_event_counts": {
                str(int(threshold)): int(eligible["notional"].ge(threshold).sum())
                for threshold in config["large_event_thresholds"]
            },
        },
        "month_diagnostics": month_diagnostics,
        "contract_classification": contract_rows,
        "data_adequacy": {
            "status": "PASS" if adequacy_pass else "DATA_ADEQUACY_UNDERPOWERED",
            "checks": adequacy_checks,
            "interpretation": (
                "Event rows are numerous, but interval completeness, label support, "
                "turnover observations, and concentration-adjusted independence must "
                "pass before a large event experiment."
            ),
        },
        "schemas": {
            "silver": list(silver_schema or ()),
            "gold": {key: list(value) for key, value in gold_schemas.items()},
        },
        "failures": sorted(set(failures)),
        "warnings": sorted(set(warnings)),
        "boundaries": dict(config["boundaries"]),
    }
    evidence["release_identity_sha256"] = canonical_sha256(
        {
            "release_id": evidence["release_id"],
            "bundle_sha256": evidence["bundle_sha256"],
            "requested_interval": evidence["requested_interval"],
            "source_interval_completeness_verified": source_interval_verified,
        }
    )
    return BitfinexPreflight(evidence, tuple(records))


__all__ = [
    "BitfinexPreflight",
    "canonical_sha256",
    "classify_symbol",
    "preflight_bitfinex_release",
    "sha256_file",
]
