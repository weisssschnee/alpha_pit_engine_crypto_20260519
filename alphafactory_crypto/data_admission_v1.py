"""Build a frozen, lagged crypto-universe admission ledger.

This module is deliberately narrower than the search engine.  It downloads the
small official Binance USD-M monthly 1d kline archives, verifies every source
checksum, constructs lifecycle-safe daily quote volume, and freezes a
point-in-time Top-N ledger.  It never evaluates candidates or starts a search.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import io
import json
import math
import os
import subprocess
import tarfile
import threading
import time
import xml.etree.ElementTree as ET
import zipfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import requests


CONTRACT_VERSION = "CRYPTO_NEW_DATA_ADMISSION_AND_PIT_UNIVERSE_V1"
SOURCE_BUCKET = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"
SOURCE_HTTP = "https://data.binance.vision"
SYMBOL_PREFIX = "data/futures/um/monthly/klines/"
EXCHANGE_INFO_URL = "https://fapi.binance.com/fapi/v1/exchangeInfo"

# These contracts disappeared from the current exchangeInfo response but are
# unambiguously legacy crypto contracts.  The list is frozen and is not learned
# from reward or search output.
LEGACY_COIN_ALLOWLIST = frozenset(
    {
        "1000BTTCUSDT",
        "AERGOUSDT",
        "AKROUSDT",
        "ANCUSDT",
        "ANTUSDT",
        "AUDIOUSDT",
        "BTSUSDT",
        "BTTUSDT",
        "BZRXUSDT",
        "COCOSUSDT",
        "DODOUSDT",
        "EOSUSDT",
        "FRONTUSDT",
        "GALUSDT",
        "HNTUSDT",
        "KEEPUSDT",
        "LENDUSDT",
        "LUNAUSDT",
        "MATICUSDT",
        "MBLUSDT",
        "NUUSDT",
        "RNDRUSDT",
        "SRMUSDT",
        "SXPUSDT",
        "TOMOUSDT",
        "YFIIUSDT",
    }
)

# Known composite/index contracts are outside the crypto-instrument surface.
LEGACY_NON_COIN_EXCLUSIONS = frozenset(
    {"BLUEBIRDUSDT", "DOTECOUSDT", "FOOTBALLUSDT"}
)

KLINE_COLUMNS = (
    "open_time",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "close_time",
    "quote_volume",
    "count",
    "taker_buy_volume",
    "taker_buy_quote_volume",
    "ignore",
)

AGGTRADES_SYSTEM_CANARY_FIELDS = (
    "agg_trade_count",
    "underlying_trade_count",
    "quantity",
    "notional",
    "buy_agg_trade_count",
    "sell_agg_trade_count",
    "buy_quantity",
    "sell_quantity",
    "buy_notional",
    "sell_notional",
    "signed_aggressor_quantity",
    "signed_aggressor_notional",
    "vwap",
    "buy_vwap",
    "sell_vwap",
    "volume_imbalance",
    "buy_sell_notional_ratio",
    "price_range_bps",
    "close_to_open_bps",
    "large_trade_count_ratio_100k_plus",
    "large_notional_ratio_100k_plus",
)

_AGGTRADES_CANARY_SOURCE_COLUMNS = (
    "timestamp",
    "agg_trade_count",
    "underlying_trade_count",
    "quantity",
    "notional",
    "buy_agg_trade_count",
    "sell_agg_trade_count",
    "buy_quantity",
    "sell_quantity",
    "buy_notional",
    "sell_notional",
    "signed_aggressor_quantity",
    "signed_aggressor_notional",
    "high_price",
    "low_price",
    "open_price",
    "close_price",
    "large_trade_count_100k_plus",
    "large_notional_100k_plus",
    "feature_available_time",
    "execution_time_min",
)

LIT_OLD_END = pd.Timestamp("2025-01-31T08:59:59Z")
LIT_NEW_START = pd.Timestamp("2025-12-23T17:30:00Z")
_REQUEST_LOCAL = threading.local()


def _payload_sha(value: Any) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest().upper()


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().lower()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().lower()


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, default=str)
        + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def _write_parquet(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    table = pa.Table.from_pandas(frame, preserve_index=False)
    pq.write_table(table, temporary, compression="zstd")
    os.replace(temporary, path)


def _month_strings(start: str, end: str) -> list[str]:
    months = pd.period_range(start=start, end=end, freq="M")
    return [str(month) for month in months]


def _request(
    url: str,
    *,
    timeout_seconds: int,
    retries: int,
    session: requests.Session | None = None,
) -> requests.Response:
    requester = session
    if requester is None:
        requester = getattr(_REQUEST_LOCAL, "session", None)
        if requester is None:
            requester = requests.Session()
            adapter = requests.adapters.HTTPAdapter(
                pool_connections=1,
                pool_maxsize=1,
                max_retries=0,
            )
            requester.mount("https://", adapter)
            _REQUEST_LOCAL.session = requester
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            response = requester.get(
                url,
                timeout=(min(15, timeout_seconds), timeout_seconds),
                verify=True,
            )
            if response.status_code == 200:
                return response
            if response.status_code == 404:
                return response
            response.raise_for_status()
        except (requests.RequestException, OSError) as exc:
            last_error = exc
        if attempt + 1 < retries:
            time.sleep(float(2**attempt))
    if "s3-ap-northeast-1.amazonaws.com" in url or "fapi.binance.com" in url:
        command = (
            "[Console]::OutputEncoding=[Text.UTF8Encoding]::new();"
            f"(Invoke-WebRequest -UseBasicParsing -Uri '{url}' "
            f"-TimeoutSec {int(timeout_seconds)}).Content"
        )
        completed = subprocess.run(
            ["powershell", "-NoProfile", "-Command", command],
            capture_output=True,
            check=False,
            timeout=timeout_seconds + 15,
        )
        if completed.returncode == 0 and completed.stdout:
            response = requests.Response()
            response.status_code = 200
            response.url = url
            response._content = completed.stdout.decode("utf-8-sig").encode("utf-8")
            response.encoding = "utf-8"
            return response
    if last_error is not None:
        raise RuntimeError(f"source request failed after {retries} attempts: {url}") from last_error
    raise RuntimeError(f"source request returned a non-success status: {url}")


def _parse_s3_xml(content: bytes) -> ET.Element:
    return ET.fromstring(content)


def _s3_texts(root: ET.Element, path: str) -> list[str]:
    namespace = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
    return [str(node.text) for node in root.findall(path, namespace)]


def fetch_source_snapshots(
    *,
    timeout_seconds: int,
    retries: int,
) -> tuple[list[str], dict[str, Any]]:
    symbol_url = f"{SOURCE_BUCKET}?delimiter=%2F&prefix={SYMBOL_PREFIX.replace('/', '%2F')}"
    symbol_response = _request(
        symbol_url, timeout_seconds=timeout_seconds, retries=retries
    )
    root = _parse_s3_xml(symbol_response.content)
    prefixes = _s3_texts(root, "s3:CommonPrefixes/s3:Prefix")
    symbols = sorted(
        {
            prefix.rstrip("/").split("/")[-1]
            for prefix in prefixes
            if prefix.rstrip("/").split("/")[-1].endswith("USDT")
            and "_" not in prefix.rstrip("/").split("/")[-1]
        }
    )
    exchange_response = _request(
        EXCHANGE_INFO_URL, timeout_seconds=timeout_seconds, retries=retries
    )
    exchange_info = exchange_response.json()
    if not isinstance(exchange_info.get("symbols"), list):
        raise ValueError("Binance exchangeInfo did not expose a symbols list")
    return symbols, exchange_info


def classify_symbols(
    official_symbols: Sequence[str],
    exchange_info: Mapping[str, Any],
) -> pd.DataFrame:
    rows_by_symbol = {
        str(row["symbol"]): row
        for row in exchange_info.get("symbols", [])
        if str(row.get("quoteAsset", "")) == "USDT"
        and "_" not in str(row.get("symbol", ""))
    }
    rows: list[dict[str, Any]] = []
    for symbol in sorted(set(official_symbols)):
        source = rows_by_symbol.get(symbol)
        if source is not None and str(source.get("underlyingType")) == "COIN":
            classification = "CRYPTO_COIN"
            admitted = True
            authority = "CURRENT_EXCHANGE_INFO"
        elif symbol in LEGACY_COIN_ALLOWLIST:
            classification = "LEGACY_CRYPTO_COIN"
            admitted = True
            authority = "FROZEN_LEGACY_ALLOWLIST"
        elif symbol in LEGACY_NON_COIN_EXCLUSIONS:
            classification = "LEGACY_NON_COIN_INDEX"
            admitted = False
            authority = "FROZEN_LEGACY_EXCLUSION"
        elif source is not None:
            classification = str(source.get("underlyingType") or "UNKNOWN")
            admitted = False
            authority = "CURRENT_EXCHANGE_INFO"
        else:
            classification = "UNRESOLVED"
            admitted = False
            authority = "FAIL_CLOSED_UNRESOLVED"
        rows.append(
            {
                "symbol": symbol,
                "classification": classification,
                "admitted_crypto_surface": admitted,
                "classification_authority": authority,
                "contract_type": None if source is None else source.get("contractType"),
                "exchange_status": None if source is None else source.get("status"),
                "onboard_date_ms": None if source is None else source.get("onboardDate"),
                "delivery_date_ms": None if source is None else source.get("deliveryDate"),
            }
        )
    return pd.DataFrame(rows)


def list_monthly_objects(
    symbol: str,
    *,
    months: frozenset[str],
    timeout_seconds: int,
    retries: int,
) -> list[dict[str, Any]]:
    prefix = f"{SYMBOL_PREFIX}{symbol}/1d/"
    url = f"{SOURCE_BUCKET}?prefix={prefix.replace('/', '%2F')}"
    response = _request(url, timeout_seconds=timeout_seconds, retries=retries)
    root = _parse_s3_xml(response.content)
    namespace = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
    output: list[dict[str, Any]] = []
    for node in root.findall("s3:Contents", namespace):
        key = str(node.findtext("s3:Key", namespaces=namespace))
        if not key.endswith(".zip"):
            continue
        stem = key.rsplit("/", 1)[-1]
        month = stem.removeprefix(f"{symbol}-1d-").removesuffix(".zip")
        if month not in months:
            continue
        output.append(
            {
                "symbol": symbol,
                "month": month,
                "key": key,
                "source_bytes": int(node.findtext("s3:Size", default="0", namespaces=namespace)),
                "source_etag": str(
                    node.findtext("s3:ETag", default="", namespaces=namespace)
                ).strip('"'),
                "source_last_modified": node.findtext(
                    "s3:LastModified", default=None, namespaces=namespace
                ),
            }
        )
    return sorted(output, key=lambda row: (row["symbol"], row["month"]))


def _parse_kline_zip(content: bytes, *, symbol: str, month: str) -> pd.DataFrame:
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        members = [name for name in archive.namelist() if name.endswith(".csv")]
        if len(members) != 1:
            raise ValueError(f"{symbol} {month} archive must contain exactly one CSV")
        raw = archive.read(members[0])
    frame = pd.read_csv(io.BytesIO(raw))
    if tuple(frame.columns) != KLINE_COLUMNS:
        frame = pd.read_csv(io.BytesIO(raw), header=None, names=KLINE_COLUMNS)
    required = {"open_time", "close_time", "quote_volume"}
    if not required.issubset(frame.columns):
        raise ValueError(f"{symbol} {month} kline schema is incomplete")
    frame = frame.loc[:, ["open_time", "close_time", "quote_volume"]].copy()
    frame["open_time"] = pd.to_numeric(frame["open_time"], errors="raise").astype("int64")
    frame["close_time"] = pd.to_numeric(frame["close_time"], errors="raise").astype("int64")
    frame["quote_volume"] = pd.to_numeric(
        frame["quote_volume"], errors="raise"
    ).astype(float)
    frame["date"] = pd.to_datetime(frame["open_time"], unit="ms", utc=True).dt.floor("D")
    if not frame["date"].dt.strftime("%Y-%m").eq(month).all():
        raise ValueError(f"{symbol} {month} contains rows outside its source month")
    if frame["date"].duplicated().any():
        raise ValueError(f"{symbol} {month} contains duplicate daily coordinates")
    if (frame["quote_volume"] < 0.0).any() or not np.isfinite(
        frame["quote_volume"]
    ).all():
        raise ValueError(f"{symbol} {month} has invalid quote volume")
    frame.insert(0, "symbol", symbol)
    return frame


def download_object(
    task: Mapping[str, Any],
    *,
    timeout_seconds: int,
    retries: int,
) -> tuple[dict[str, Any], pd.DataFrame | None]:
    key = str(task["key"])
    url = f"{SOURCE_HTTP}/{key}"
    checksum_url = url + ".CHECKSUM"
    try:
        response = _request(url, timeout_seconds=timeout_seconds, retries=retries)
        if response.status_code == 404:
            return (
                {
                    **dict(task),
                    "source_url": url,
                    "checksum_url": checksum_url,
                    "checksum_expected": None,
                    "checksum_actual": None,
                    "checksum_status": "NOT_FOUND",
                    "download_bytes": 0,
                    "daily_rows": 0,
                    "date_min": None,
                    "date_max": None,
                    "status": "NOT_FOUND",
                    "error": None,
                },
                None,
            )
        checksum_response = _request(
            checksum_url, timeout_seconds=timeout_seconds, retries=retries
        )
        if response.status_code != 200 or checksum_response.status_code != 200:
            raise ValueError("listed object or checksum returned 404")
        expected = checksum_response.text.strip().split()[0].lower()
        actual = _sha256(response.content)
        if expected != actual:
            raise ValueError("source checksum mismatch")
        frame = _parse_kline_zip(
            response.content,
            symbol=str(task["symbol"]),
            month=str(task["month"]),
        )
        manifest = {
            **dict(task),
            "source_url": url,
            "checksum_url": checksum_url,
            "checksum_expected": expected,
            "checksum_actual": actual,
            "checksum_status": "PASS",
            "download_bytes": len(response.content),
            "daily_rows": len(frame),
            "date_min": frame["date"].min(),
            "date_max": frame["date"].max(),
            "status": "PASS",
            "error": None,
        }
        return manifest, frame
    except Exception as exc:  # fail closed and preserve the exact failed object
        manifest = {
            **dict(task),
            "source_url": url,
            "checksum_url": checksum_url,
            "checksum_expected": None,
            "checksum_actual": None,
            "checksum_status": "FAIL",
            "download_bytes": 0,
            "daily_rows": 0,
            "date_min": None,
            "date_max": None,
            "status": "FAIL",
            "error": f"{type(exc).__name__}: {exc}",
        }
        return manifest, None


def assign_instrument_lifecycles(
    daily: pd.DataFrame,
    *,
    gap_days: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if daily.empty:
        raise ValueError("daily quote-volume input is empty")
    values = daily.sort_values(["symbol", "date"]).copy()
    output: list[pd.DataFrame] = []
    ledger: list[dict[str, Any]] = []
    for symbol, group in values.groupby("symbol", sort=True):
        local = group.sort_values("date").copy()
        gaps = local["date"].diff().dt.total_seconds().div(86400.0)
        lifecycle = gaps.gt(float(gap_days)).cumsum().astype(int) + 1
        local["lifecycle_ordinal"] = lifecycle
        local["identity_status"] = "INFERRED_GAP_BOUNDED"
        if symbol == "LITUSDT":
            old = local["date"].le(LIT_OLD_END.floor("D"))
            new = local["date"].ge(LIT_NEW_START.floor("D"))
            ambiguous = ~(old | new)
            local.loc[old, "lifecycle_ordinal"] = 1
            local.loc[old, "identity_status"] = "LITENTRY_CONTRACT_BOUND"
            local.loc[new, "lifecycle_ordinal"] = 2
            local.loc[new, "identity_status"] = "LIGHTER_PROTOCOL_CONTRACT_BOUND"
            local.loc[ambiguous, "lifecycle_ordinal"] = -1
            local.loc[ambiguous, "identity_status"] = "QUARANTINED_IDENTITY_GAP"
        lifecycle_count = int(local.loc[local["lifecycle_ordinal"].gt(0), "lifecycle_ordinal"].nunique())
        local["instrument_id"] = [
            (
                f"{symbol}::QUARANTINED"
                if ordinal < 0
                else symbol
                if lifecycle_count == 1
                else f"{symbol}::L{ordinal:02d}"
            )
            for ordinal in local["lifecycle_ordinal"]
        ]
        for instrument_id, segment in local.groupby("instrument_id", sort=True):
            ledger.append(
                {
                    "raw_symbol": symbol,
                    "instrument_id": instrument_id,
                    "lifecycle_ordinal": int(segment["lifecycle_ordinal"].iloc[0]),
                    "identity_status": str(segment["identity_status"].iloc[0]),
                    "date_min": segment["date"].min(),
                    "date_max": segment["date"].max(),
                    "observed_days": len(segment),
                    "admitted": not instrument_id.endswith("::QUARANTINED"),
                }
            )
        output.append(local)
    joined = pd.concat(output, ignore_index=True)
    return joined, pd.DataFrame(ledger).sort_values(
        ["raw_symbol", "lifecycle_ordinal"]
    )


def build_lagged_pit_universe(
    daily: pd.DataFrame,
    *,
    start_date: str,
    end_date: str,
    top_n: int,
    trailing_days: int,
    minimum_observed_days: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    values = daily.loc[
        daily["lifecycle_ordinal"].gt(0),
        ["instrument_id", "symbol", "date", "quote_volume"],
    ].copy()
    dates = pd.date_range(start_date, end_date, freq="D", tz="UTC")
    prehistory_start = dates.min() - pd.Timedelta(days=trailing_days)
    values = values.loc[
        values["date"].between(prehistory_start, dates.max(), inclusive="both")
    ]
    symbol_by_instrument = (
        values[["instrument_id", "symbol"]]
        .drop_duplicates()
        .set_index("instrument_id")["symbol"]
        .to_dict()
    )
    volume = values.pivot_table(
        index="date",
        columns="instrument_id",
        values="quote_volume",
        aggfunc="sum",
    ).reindex(pd.date_range(prehistory_start, dates.max(), freq="D", tz="UTC"))
    observed = volume.notna()
    lagged_volume = volume.rolling(
        trailing_days, min_periods=1
    ).sum().shift(1)
    lagged_days = observed.rolling(
        trailing_days, min_periods=1
    ).sum().shift(1)
    active_yesterday = observed.shift(1, fill_value=False)
    eligible = lagged_days.ge(minimum_observed_days) & active_yesterday

    rows: list[dict[str, Any]] = []
    summary: list[dict[str, Any]] = []
    for date in dates:
        scores = lagged_volume.loc[date]
        days = lagged_days.loc[date]
        mask = eligible.loc[date] & scores.notna()
        candidates = pd.DataFrame(
            {
                "instrument_id": scores.index[mask],
                "trailing_quote_volume": scores.loc[mask].astype(float).values,
                "observed_days": days.loc[mask].astype(int).values,
            }
        ).sort_values(
            ["trailing_quote_volume", "instrument_id"],
            ascending=[False, True],
            kind="mergesort",
        )
        selected = candidates.head(top_n).copy()
        selected["date"] = date
        selected["rank"] = np.arange(1, len(selected) + 1, dtype=np.int16)
        selected["raw_symbol"] = selected["instrument_id"].map(symbol_by_instrument)
        selected["feature_available_time"] = date
        rows.extend(selected.to_dict("records"))
        summary.append(
            {
                "date": date,
                "eligible_instruments": len(candidates),
                "selected_instruments": len(selected),
                "top_n_complete": len(selected) == top_n,
                "minimum_selected_trailing_quote_volume": (
                    None if selected.empty else float(selected["trailing_quote_volume"].min())
                ),
            }
        )
    universe = pd.DataFrame(rows).sort_values(["date", "rank"])
    return universe, pd.DataFrame(summary)


def build_daily_context(universe: pd.DataFrame, ledger: pd.DataFrame) -> pd.DataFrame:
    first_dates = ledger.set_index("instrument_id")["date_min"].to_dict()
    context = universe.copy()
    context["active_universe_size"] = context.groupby("date")[
        "instrument_id"
    ].transform("size").astype("int16")
    context["listing_age_hours"] = [
        int((date - first_dates[instrument]).total_seconds() // 3600)
        for date, instrument in zip(context["date"], context["instrument_id"])
    ]
    context["history_length_hours"] = (
        context.groupby("instrument_id").cumcount().add(1).mul(24).astype("int32")
    )
    context["age_percentile_active_universe"] = context.groupby("date")[
        "listing_age_hours"
    ].rank(method="average", pct=True)
    return context


def coverage_against_surfaces(
    universe: pd.DataFrame,
    *,
    surfaces: Mapping[str, set[str]],
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for date, group in universe.groupby("date", sort=True):
        selected = set(group["raw_symbol"])
        for surface_id, symbols in sorted(surfaces.items()):
            covered = selected & symbols
            rows.append(
                {
                    "date": date,
                    "surface_id": surface_id,
                    "selected_count": len(selected),
                    "covered_count": len(covered),
                    "coverage_rate": (
                        math.nan if not selected else len(covered) / len(selected)
                    ),
                    "missing_count": len(selected - symbols),
                }
            )
    return pd.DataFrame(rows)


def surface_missing_member_rows(
    universe: pd.DataFrame,
    *,
    surfaces: Mapping[str, set[str]],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    detailed: list[pd.DataFrame] = []
    for surface_id, symbols in sorted(surfaces.items()):
        missing = universe.loc[
            ~universe["raw_symbol"].isin(symbols),
            ["date", "rank", "instrument_id", "raw_symbol"],
        ].copy()
        missing.insert(0, "surface_id", surface_id)
        detailed.append(missing)
    rows = pd.concat(detailed, ignore_index=True).sort_values(
        ["surface_id", "date", "rank"]
    )
    summary = (
        rows.groupby(["surface_id", "raw_symbol"], sort=True)
        .agg(
            missing_days=("date", "nunique"),
            first_missing_date=("date", "min"),
            last_missing_date=("date", "max"),
            best_rank=("rank", "min"),
            median_rank=("rank", "median"),
            worst_rank=("rank", "max"),
        )
        .reset_index()
        .sort_values(
            ["surface_id", "missing_days", "best_rank", "raw_symbol"],
            ascending=[True, False, True, True],
        )
    )
    return rows, summary


def coverage_against_temporal_surfaces(
    universe: pd.DataFrame,
    *,
    surfaces: Mapping[str, set[tuple[str, pd.Timestamp]]],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    detailed: list[pd.DataFrame] = []
    coverage_rows: list[dict[str, Any]] = []
    for surface_id, coordinates in sorted(surfaces.items()):
        local = universe.loc[
            :, ["date", "rank", "instrument_id", "raw_symbol"]
        ].copy()
        local["available"] = [
            (symbol, pd.to_datetime(date, utc=True).floor("D")) in coordinates
            for symbol, date in zip(local["raw_symbol"], local["date"])
        ]
        for date, group in local.groupby("date", sort=True):
            covered = int(group["available"].sum())
            coverage_rows.append(
                {
                    "date": date,
                    "surface_id": surface_id,
                    "selected_count": len(group),
                    "covered_count": covered,
                    "coverage_rate": covered / len(group),
                    "missing_count": len(group) - covered,
                }
            )
        missing = local.loc[~local["available"]].drop(columns=["available"])
        missing.insert(0, "surface_id", surface_id)
        detailed.append(missing)
    rows = pd.concat(detailed, ignore_index=True).sort_values(
        ["surface_id", "date", "rank"]
    )
    summary = (
        rows.groupby(["surface_id", "raw_symbol"], sort=True)
        .agg(
            missing_days=("date", "nunique"),
            first_missing_date=("date", "min"),
            last_missing_date=("date", "max"),
            best_rank=("rank", "min"),
            median_rank=("rank", "median"),
            worst_rank=("rank", "max"),
        )
        .reset_index()
        .sort_values(
            ["surface_id", "missing_days", "best_rank", "raw_symbol"],
            ascending=[True, False, True, True],
        )
    )
    return pd.DataFrame(coverage_rows), rows, summary


def _aggtrade_symbol_dates_from_tar(path: Path) -> set[tuple[str, pd.Timestamp]]:
    output: set[tuple[str, pd.Timestamp]] = set()
    with tarfile.open(path, "r:") as archive:
        for member in archive.getmembers():
            if (
                not member.isfile()
                or "/object_manifest/" not in member.name
                or not member.name.endswith(".json")
            ):
                continue
            payload = json.load(archive.extractfile(member))
            if payload.get("status") != "complete":
                continue
            start = pd.to_datetime(payload["timestamp_min"], utc=True).floor("D")
            end = pd.to_datetime(payload["timestamp_max"], utc=True).floor("D")
            output.update(
                (str(payload["symbol"]), date)
                for date in pd.date_range(start, end, freq="D", tz="UTC")
            )
    return output


def _declared_tar_sha256(path: Path) -> str:
    sidecar = Path(str(path) + ".sha256")
    if not sidecar.is_file():
        raise FileNotFoundError(f"missing TAR SHA256 sidecar: {sidecar}")
    tokens = sidecar.read_text(encoding="utf-8").strip().split()
    if not tokens or len(tokens[0]) != 64:
        raise ValueError(f"invalid TAR SHA256 sidecar: {sidecar}")
    return tokens[0].lower()


def _aggtrade_coordinate(member_name: str) -> tuple[str, str] | None:
    normalized = member_name.replace("\\", "/")
    marker = "/compact_1m/symbol="
    if marker not in normalized or not normalized.endswith("/part.parquet"):
        return None
    remainder = normalized.split(marker, 1)[1]
    try:
        symbol, month_part = remainder.split("/month=", 1)
        month = month_part.split("/", 1)[0]
    except ValueError:
        return None
    if not symbol or len(month) != 7:
        return None
    return symbol, month


def _safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    left = pd.to_numeric(numerator, errors="coerce").astype(float)
    right = pd.to_numeric(denominator, errors="coerce").astype(float)
    return left.divide(right.where(right.abs().gt(0.0)))


def _aggregate_aggtrades_hourly(frame: pd.DataFrame) -> pd.DataFrame:
    missing = sorted(set(_AGGTRADES_CANARY_SOURCE_COLUMNS) - set(frame.columns))
    if missing:
        raise ValueError(f"aggTrades compact partition lacks columns: {missing}")
    local = frame.loc[:, list(_AGGTRADES_CANARY_SOURCE_COLUMNS)].copy()
    local["timestamp"] = pd.to_datetime(local["timestamp"], utc=True)
    local["feature_available_time"] = pd.to_datetime(
        local["feature_available_time"], utc=True
    )
    local["execution_time_min"] = pd.to_datetime(
        local["execution_time_min"], utc=True
    )
    if local["timestamp"].duplicated().any():
        raise ValueError("aggTrades compact partition has duplicate minute timestamps")
    local = local.sort_values("timestamp")
    local["hour"] = local["timestamp"].dt.floor("h")
    grouped = local.groupby("hour", sort=True, observed=True)
    sum_columns = [
        "agg_trade_count",
        "underlying_trade_count",
        "quantity",
        "notional",
        "buy_agg_trade_count",
        "sell_agg_trade_count",
        "buy_quantity",
        "sell_quantity",
        "buy_notional",
        "sell_notional",
        "signed_aggressor_quantity",
        "signed_aggressor_notional",
        "large_trade_count_100k_plus",
        "large_notional_100k_plus",
    ]
    output = grouped[sum_columns].sum(min_count=1)
    output["vwap"] = _safe_divide(output["notional"], output["quantity"])
    output["buy_vwap"] = _safe_divide(
        output["buy_notional"], output["buy_quantity"]
    )
    output["sell_vwap"] = _safe_divide(
        output["sell_notional"], output["sell_quantity"]
    )
    output["volume_imbalance"] = _safe_divide(
        output["buy_notional"] - output["sell_notional"],
        output["buy_notional"] + output["sell_notional"],
    )
    output["buy_sell_notional_ratio"] = _safe_divide(
        output["buy_notional"], output["sell_notional"]
    )
    first_open = grouped["open_price"].first()
    last_close = grouped["close_price"].last()
    low = grouped["low_price"].min()
    high = grouped["high_price"].max()
    output["price_range_bps"] = 10_000.0 * _safe_divide(high - low, low)
    output["close_to_open_bps"] = 10_000.0 * _safe_divide(
        last_close - first_open, first_open
    )
    output["large_trade_count_ratio_100k_plus"] = _safe_divide(
        output["large_trade_count_100k_plus"], output["agg_trade_count"]
    )
    output["large_notional_ratio_100k_plus"] = _safe_divide(
        output["large_notional_100k_plus"], output["notional"]
    )
    output["minute_rows"] = grouped.size()
    output["maximum_feature_available_time"] = grouped[
        "feature_available_time"
    ].max()
    output["maximum_execution_time_min"] = grouped["execution_time_min"].max()
    hour_end = output.index + pd.Timedelta(hours=1)
    decision_time = output.index + pd.Timedelta(hours=2)
    output["complete_and_pit_safe"] = (
        output["minute_rows"].eq(60)
        & output["maximum_feature_available_time"].le(hour_end)
        & output["maximum_execution_time_min"].le(decision_time)
        & np.isfinite(output[list(AGGTRADES_SYSTEM_CANARY_FIELDS)]).all(axis=1)
    )
    return output


def _open_canary_matrix(
    path: Path, shape: tuple[int, int], dtype: Any, fill: Any
) -> np.memmap:
    values = np.lib.format.open_memmap(path, mode="w+", dtype=dtype, shape=shape)
    values[...] = fill
    return values


def _rank_percentile_on_mask(
    values: np.ndarray, observed: np.ndarray
) -> np.ndarray:
    output = np.full(values.shape, np.nan, dtype=np.float32)
    for time_index in range(values.shape[1]):
        mask = observed[:, time_index] & np.isfinite(values[:, time_index])
        count = int(mask.sum())
        if count == 0:
            continue
        local = values[mask, time_index]
        order = np.argsort(local, kind="stable")
        ranks = np.empty(count, dtype=float)
        ranks[order] = (np.arange(count, dtype=float) + 0.5) / count
        output[mask, time_index] = ranks.astype(np.float32)
    return output


def build_aggtrades_system_canary_cache(
    *,
    source_cache_root: Path,
    top100_tar: Path,
    ranks101_200_tar: Path,
    output_cache_root: Path,
    broad_field_ids: Sequence[str],
    start: str,
    end_exclusive: str,
    producer_source_sha: str,
    verify_tar_sha256: bool = True,
) -> dict[str, Any]:
    """Build the smallest RawPanelStore bridge for a fixed-cohort system canary.

    The bridge keeps the existing target, mapping, compiler, evaluator, and
    matched-control path. It aggregates only the frozen development window,
    requires 60 minute rows per hour, recomputes panel context after the
    aggTrades join, and never fills a missing source coordinate with zero.
    """

    from alphafactory_crypto.broad_search.panel18m import RawPanelStore

    source_cache_root = source_cache_root.resolve()
    output_cache_root = output_cache_root.resolve()
    top100_tar = top100_tar.resolve()
    ranks101_200_tar = ranks101_200_tar.resolve()
    if output_cache_root.exists():
        metadata_path = output_cache_root / "metadata.json"
        if not metadata_path.is_file():
            raise FileExistsError(
                f"existing canary cache has no metadata: {output_cache_root}"
            )
        existing = json.loads(metadata_path.read_text(encoding="utf-8"))
        if existing.get("producer_source_sha") != producer_source_sha:
            raise ValueError(
                "existing canary cache was built by a different producer source"
            )
        return existing
    for path in (top100_tar, ranks101_200_tar):
        if not path.is_file():
            raise FileNotFoundError(path)
    source = RawPanelStore.open(source_cache_root)
    start_ts = pd.Timestamp(start)
    end_ts = pd.Timestamp(end_exclusive)
    start_ts = start_ts.tz_localize("UTC") if start_ts.tzinfo is None else start_ts.tz_convert("UTC")
    end_ts = end_ts.tz_localize("UTC") if end_ts.tzinfo is None else end_ts.tz_convert("UTC")
    if end_ts <= start_ts:
        raise ValueError("canary cache window is empty")
    block = source.block_slice(start_ts.isoformat(), end_ts.isoformat())
    source_time_indices = np.arange(source.shape[1])[block]
    timestamp_ns = np.asarray(source.timestamp_ns[block], dtype=np.int64)
    if len(timestamp_ns) == 0:
        raise ValueError("canary cache window is outside the source target cache")
    timestamps = pd.to_datetime(timestamp_ns, utc=True)
    expected = pd.date_range(start_ts, end_ts, freq="h", inclusive="left")
    if not timestamps.equals(expected):
        raise ValueError("source target cache is not a complete hourly canary window")
    months = set(pd.period_range(start_ts, end_ts - pd.Timedelta(hours=1), freq="M").astype(str))

    declared_hashes = {
        str(top100_tar): _declared_tar_sha256(top100_tar),
        str(ranks101_200_tar): _declared_tar_sha256(ranks101_200_tar),
    }
    observed_hashes: dict[str, str] = {}
    if verify_tar_sha256:
        for path in (top100_tar, ranks101_200_tar):
            observed_hashes[str(path)] = _sha256_file(path)
            if observed_hashes[str(path)] != declared_hashes[str(path)]:
                raise ValueError(f"TAR SHA256 mismatch: {path}")

    archives = [
        tarfile.open(top100_tar, "r:"),
        tarfile.open(ranks101_200_tar, "r:"),
    ]
    try:
        coordinates: dict[tuple[str, str], tuple[int, tarfile.TarInfo]] = {}
        for archive_index, archive in enumerate(archives):
            for member in archive.getmembers():
                coordinate = _aggtrade_coordinate(member.name)
                if coordinate is None or coordinate[1] not in months:
                    continue
                if coordinate in coordinates:
                    raise ValueError(f"duplicate aggTrades coordinate: {coordinate}")
                coordinates[coordinate] = (archive_index, member)
        source_symbol_index = {
            symbol: index for index, symbol in enumerate(source.symbols)
        }
        symbols = sorted(
            {
                symbol
                for symbol, _ in coordinates
                if symbol in source_symbol_index
            }
        )
        if len(symbols) < 50:
            raise ValueError("aggTrades canary has fewer than 50 source-bridge symbols")
        source_asset_indices = np.asarray(
            [source_symbol_index[symbol] for symbol in symbols], dtype=int
        )
        broad_fields = tuple(dict.fromkeys(str(value) for value in broad_field_ids))
        missing_broad = sorted(set(broad_fields) - set(source.metadata["field_ids"]))
        if missing_broad:
            raise ValueError(f"source cache lacks Broad fields: {missing_broad}")
        all_fields = tuple(
            dict.fromkeys((*broad_fields, *AGGTRADES_SYSTEM_CANARY_FIELDS))
        )
        output_cache_root.parent.mkdir(parents=True, exist_ok=True)
        temporary = output_cache_root.with_name(
            f".{output_cache_root.name}.tmp-{os.getpid()}"
        )
        if temporary.exists():
            raise FileExistsError(f"stale canary cache temporary path: {temporary}")
        temporary.mkdir(parents=True)
        (temporary / "fields").mkdir()
        shape = (len(symbols), len(timestamp_ns))
        np.save(temporary / "timestamp_ns.npy", timestamp_ns)
        observed_minutes = _open_canary_matrix(
            temporary / "aggtrades_complete_hour.npy", shape, np.bool_, False
        )
        field_matrices = {
            field_id: _open_canary_matrix(
                temporary / "fields" / f"{field_id}.npy",
                shape,
                np.float32,
                np.nan,
            )
            for field_id in all_fields
        }
        for field_id in broad_fields:
            source_values = np.asarray(
                source.field(field_id)[:, block], dtype=np.float32
            )
            field_matrices[field_id][...] = source_values[source_asset_indices]

        output_time_index = pd.Index(timestamps)
        symbol_output_index = {symbol: index for index, symbol in enumerate(symbols)}
        partition_count = 0
        partition_rows = 0
        for (symbol, month), (archive_index, member) in sorted(coordinates.items()):
            if symbol not in symbol_output_index:
                continue
            handle = archives[archive_index].extractfile(member)
            if handle is None:
                raise ValueError(f"cannot read aggTrades member: {member.name}")
            frame = pq.ParquetFile(handle).read(
                columns=list(_AGGTRADES_CANARY_SOURCE_COLUMNS)
            ).to_pandas()
            hourly = _aggregate_aggtrades_hourly(frame)
            common = hourly.index.intersection(output_time_index)
            if common.empty:
                continue
            positions = output_time_index.get_indexer(common)
            row = symbol_output_index[symbol]
            selected = hourly.loc[common]
            valid = selected["complete_and_pit_safe"].to_numpy(dtype=bool)
            observed_minutes[row, positions] = valid
            for field_id in AGGTRADES_SYSTEM_CANARY_FIELDS:
                values = selected[field_id].to_numpy(dtype=np.float32)
                field_matrices[field_id][row, positions] = np.where(
                    valid, values, np.nan
                )
            partition_count += 1
            partition_rows += len(frame)

        source_observed = np.asarray(source.observed()[:, block], dtype=bool)[
            source_asset_indices
        ]
        observed = source_observed & np.asarray(observed_minutes, dtype=bool)
        source_base = np.asarray(source.base_eligible()[:, block], dtype=bool)[
            source_asset_indices
        ]
        base_eligible = source_base & observed
        np.save(temporary / "observed.npy", observed)
        np.save(temporary / "base_eligible.npy", base_eligible)
        source_segment = np.asarray(
            np.load(
                source_cache_root / "source_segment.npy", mmap_mode="r"
            )[:, block],
            dtype=np.int8,
        )[source_asset_indices]
        np.save(
            temporary / "source_segment.npy",
            np.where(observed, source_segment, 0).astype(np.int8),
        )
        active_count = observed.sum(axis=0).astype(np.float32)
        active_matrix = np.where(observed, active_count[None, :], np.nan).astype(
            np.float32
        )
        listing_age = np.asarray(
            source.field("listing_age_hours")[:, block], dtype=float
        )[source_asset_indices]
        age_percentile = _rank_percentile_on_mask(listing_age, observed)
        history_length = np.where(
            observed, np.cumsum(observed, axis=1, dtype=np.int32), np.nan
        ).astype(np.float32)
        for field_id, values in {
            "active_universe_size": active_matrix,
            "age_percentile_active_universe": age_percentile,
            "history_length_hours": history_length,
        }.items():
            if field_id not in field_matrices:
                raise ValueError(f"Broad canary registry lacks context field: {field_id}")
            field_matrices[field_id][...] = values
        for field_id, matrix in field_matrices.items():
            if field_id not in {
                "active_universe_size",
                "age_percentile_active_universe",
                "history_length_hours",
            }:
                matrix[~observed] = np.nan
            matrix.flush()
        observed_minutes.flush()
        for horizon in source.metadata["target_horizons_hours"]:
            target = np.asarray(
                source.target_return(int(horizon))[:, block], dtype=np.float32
            )[source_asset_indices]
            target = np.where(base_eligible, target, np.nan).astype(np.float32)
            np.save(temporary / f"target_return_{int(horizon)}h.npy", target)

        source_manifest = {
            "schema_version": 1,
            "source_cache_root": str(source_cache_root),
            "source_cache_identity_sha256": source.metadata["identity_sha256"],
            "tars": [
                {
                    "path": str(path),
                    "bytes": path.stat().st_size,
                    "declared_sha256": declared_hashes[str(path)],
                    "observed_sha256": observed_hashes.get(str(path)),
                    "full_sha256_verified": bool(verify_tar_sha256),
                }
                for path in (top100_tar, ranks101_200_tar)
            ],
            "partition_count": partition_count,
            "partition_rows": partition_rows,
        }
        _write_json(temporary / "source_file_manifest.json", source_manifest)
        identity_payload = {
            "schema_version": 1,
            "cache_role": "AGGTRADES_FIXED_COHORT_SYSTEM_CANARY_RAW_PANEL_STORE",
            "producer_source_sha": producer_source_sha,
            "source_manifest": source_manifest,
            "start_utc": start_ts.isoformat(),
            "end_exclusive_utc": end_ts.isoformat(),
            "symbols": symbols,
            "field_ids": list(all_fields),
            "observed_coordinates": int(observed.sum()),
            "eligible_coordinates": int(base_eligible.sum()),
            "aggregation": {
                "minute_rows_per_hour": 60,
                "missing_fill": None,
                "feature_available_time_maximum": "hour_end",
                "execution_time_maximum": "hour_plus_2h",
            },
        }
        metadata = {
            "schema_version": 2,
            "surface_id": "CRYPTO_AGGTRADES_FIXED_COHORT_SYSTEM_CANARY_V1",
            "cache_role": identity_payload["cache_role"],
            "identity_sha256": _payload_sha(identity_payload),
            "producer_source_sha": producer_source_sha,
            "source_cache_identity_sha256": source.metadata["identity_sha256"],
            "assets": len(symbols),
            "timestamps": len(timestamp_ns),
            "symbol_ids": symbols,
            "field_ids": list(all_fields),
            "target_horizons_hours": list(
                source.metadata["target_horizons_hours"]
            ),
            "target_formula": source.metadata["target_formula"],
            "start_utc": start_ts.isoformat(),
            "end_exclusive_utc": end_ts.isoformat(),
            "observed_coordinates": int(observed.sum()),
            "eligible_coordinates": int(base_eligible.sum()),
            "panel_context_contract": {
                "authority": "POST_JOIN_ASSET_BY_TIME_RECOMPUTE",
                "fields": [
                    "active_universe_size",
                    "age_percentile_active_universe",
                    "history_length_hours",
                ],
            },
            "fixed_retrospective_cohort": True,
            "research_admission": "DEVELOPMENT_DIAGNOSTIC_ONLY",
            "sealed_rows": 0,
        }
        _write_json(temporary / "metadata.json", metadata)
        del matrix
        del field_matrices
        del observed_minutes
        gc.collect()
        os.replace(temporary, output_cache_root)
        return metadata
    finally:
        for archive in archives:
            archive.close()


def _oi_symbol_dates(root: Path) -> set[tuple[str, pd.Timestamp]]:
    output: set[tuple[str, pd.Timestamp]] = set()
    for path in sorted((root / "compact_1h").rglob("part.parquet")):
        table = pq.ParquetFile(path).read(columns=["base_asset", "timestamp"])
        frame = table.to_pandas()
        frame["date"] = pd.to_datetime(frame["timestamp"], utc=True).dt.floor("D")
        output.update(
            (f"{base}USDT", date)
            for base, date in frame[["base_asset", "date"]]
            .drop_duplicates()
            .itertuples(index=False, name=None)
        )
    return output


def _hourly_cache_symbol_dates(cache_root: Path) -> set[tuple[str, pd.Timestamp]]:
    symbols = json.loads((cache_root / "symbols.json").read_text(encoding="utf-8"))[
        "symbols"
    ]
    timestamp_ns = np.load(cache_root / "timestamp_ns.npy", mmap_mode="r")
    timestamps = pd.to_datetime(timestamp_ns, utc=True).floor("D")
    observed = np.load(cache_root / "observed.npy", mmap_mode="r")
    output: set[tuple[str, pd.Timestamp]] = set()
    for asset_index, symbol in enumerate(symbols):
        output.update(
            (str(symbol), date)
            for date in pd.unique(timestamps[np.asarray(observed[asset_index])])
        )
    return output


def build_hourly_schema2_intersection_cache(
    *,
    universe: pd.DataFrame,
    identity_ledger: pd.DataFrame,
    v3_root: Path,
    cache_root: Path,
) -> dict[str, Any]:
    """Rebuild schema-2 context on the observed current-498/PIT intersection.

    This cache is useful input authority, but it is not search-ready when a
    historical PIT member is absent from the current-498 source panel.
    """

    from alphafactory_crypto.broad_search.panel18m import (
        rebuild_panel_context_fields,
    )

    selected_dates = {
        symbol: set(group["date"].dt.floor("D"))
        for symbol, group in universe.groupby("raw_symbol", sort=True)
    }
    instrument_by_symbol_date = {
        symbol: group.set_index(group["date"].dt.floor("D"))["instrument_id"].to_dict()
        for symbol, group in universe.groupby("raw_symbol", sort=True)
    }
    admitted_ledger = identity_ledger.loc[identity_ledger["admitted"].astype(bool)]
    lifecycle_counts = admitted_ledger.groupby("raw_symbol")["instrument_id"].nunique()
    first_date_by_instrument = admitted_ledger.set_index("instrument_id")[
        "date_min"
    ].to_dict()
    files = sorted(v3_root.glob("symbol=*/part.parquet"))
    if not files:
        raise ValueError("current-498 source panel exposes no symbol parquet files")
    source_rows: list[dict[str, Any]] = []
    timestamp_min: pd.Timestamp | None = None
    timestamp_max: pd.Timestamp | None = None
    for path in files:
        parquet = pq.ParquetFile(path)
        table = parquet.read(columns=["timestamp"])
        timestamps = pd.to_datetime(table["timestamp"].to_pandas(), utc=True)
        if timestamps.empty:
            continue
        local_min = timestamps.min()
        local_max = timestamps.max()
        timestamp_min = local_min if timestamp_min is None else min(timestamp_min, local_min)
        timestamp_max = local_max if timestamp_max is None else max(timestamp_max, local_max)
        source_rows.append(
            {
                "path": str(path),
                "bytes": path.stat().st_size,
                "rows": parquet.metadata.num_rows,
                "timestamp_min": local_min,
                "timestamp_max": local_max,
                "sha256": _sha256(path.read_bytes()),
            }
        )
    if timestamp_min is None or timestamp_max is None:
        raise ValueError("current-498 source panel has no timestamps")
    membership_min = pd.to_datetime(universe["date"].min(), utc=True)
    membership_max = pd.to_datetime(universe["date"].max(), utc=True) + pd.Timedelta(
        hours=23
    )
    timestamp_min = max(timestamp_min, membership_min)
    timestamp_max = min(timestamp_max, membership_max)
    timestamps = pd.date_range(timestamp_min, timestamp_max, freq="h", tz="UTC")
    timestamp_ns = timestamps.astype("int64").to_numpy()
    symbols = [path.parent.name.split("=", 1)[1] for path in files]
    observed = np.zeros((len(symbols), len(timestamps)), dtype=bool)
    listing_age_hours = np.full(
        (len(symbols), len(timestamps)), np.nan, dtype=np.float32
    )
    for asset_index, path in enumerate(files):
        symbol = symbols[asset_index]
        admitted_dates = selected_dates.get(symbol)
        if not admitted_dates:
            continue
        table = pq.ParquetFile(path).read(
            columns=["timestamp", "listing_age_hours"]
        )
        local_timestamp = pd.to_datetime(table["timestamp"].to_pandas(), utc=True)
        local_age = pd.to_numeric(
            table["listing_age_hours"].to_pandas(), errors="coerce"
        ).to_numpy(dtype=np.float32)
        local_date = local_timestamp.dt.floor("D")
        if int(lifecycle_counts.get(symbol, 0)) > 1:
            local_instrument = local_date.map(instrument_by_symbol_date[symbol])
            replacement = np.asarray(
                [
                    (
                        np.nan
                        if pd.isna(instrument)
                        else (
                            timestamp
                            - pd.to_datetime(
                                first_date_by_instrument[str(instrument)], utc=True
                            )
                        ).total_seconds()
                        / 3600.0
                    )
                    for timestamp, instrument in zip(
                        local_timestamp, local_instrument
                    )
                ],
                dtype=np.float32,
            )
            replace = np.isfinite(replacement)
            local_age[replace] = replacement[replace]
        keep = (
            local_date.isin(admitted_dates)
            & local_timestamp.ge(timestamp_min)
            & local_timestamp.le(timestamp_max)
        )
        if not bool(keep.any()):
            continue
        local_ns = local_timestamp.loc[keep].astype("int64").to_numpy()
        indices = np.searchsorted(timestamp_ns, local_ns)
        if np.any(indices >= len(timestamp_ns)) or not np.array_equal(
            timestamp_ns[indices], local_ns
        ):
            raise ValueError(f"{symbol} has a non-hourly timestamp coordinate")
        if len(np.unique(indices)) != len(indices):
            raise ValueError(f"{symbol} has duplicate hourly timestamp coordinates")
        observed[asset_index, indices] = True
        listing_age_hours[asset_index, indices] = local_age[keep.to_numpy()]
    context = rebuild_panel_context_fields(
        observed=observed,
        listing_age_hours=listing_age_hours,
    )
    cache_root.mkdir(parents=True, exist_ok=True)
    np.save(cache_root / "timestamp_ns.npy", timestamp_ns)
    np.save(cache_root / "observed.npy", observed)
    np.save(cache_root / "listing_age_hours.npy", listing_age_hours)
    for field_id, values in context.items():
        np.save(cache_root / f"{field_id}.npy", values)
    _write_json(cache_root / "symbols.json", {"symbols": symbols})
    _write_parquet(cache_root / "source_file_manifest.parquet", pd.DataFrame(source_rows))
    active_counts = observed.sum(axis=0)
    selected_by_day = universe.groupby("date")["instrument_id"].nunique()
    hourly_selected = pd.Series(timestamps.floor("D")).map(selected_by_day).fillna(0)
    complete_hourly_support = active_counts == hourly_selected.to_numpy()
    identity = {
        "cache_schema_version": 2,
        "cache_role": "SCHEMA2_CONTEXT_CURRENT498_PIT_INTERSECTION",
        "search_cache": False,
        "search_reuse_authorized": bool(complete_hourly_support.all()),
        "post_join_context_authority": True,
        "timestamp_min": timestamps.min(),
        "timestamp_max": timestamps.max(),
        "hours": len(timestamps),
        "source_symbols": len(symbols),
        "observed_coordinates": int(observed.sum()),
        "active_universe_min": int(active_counts.min()),
        "active_universe_max": int(active_counts.max()),
        "hours_with_complete_historical_pit_support": int(
            complete_hourly_support.sum()
        ),
        "complete_historical_pit_support_rate": float(
            complete_hourly_support.mean()
        ),
        "source_file_identity_sha256": _payload_sha(source_rows),
        "universe_identity_sha256": _payload_sha(
            universe.astype(str).to_dict("records")
        ),
        "context_builder": (
            "alphafactory_crypto.broad_search.panel18m."
            "rebuild_panel_context_fields"
        ),
        "missing_historical_members_are_not_imputed": True,
        "array_sha256": {
            path.name: _sha256(path.read_bytes())
            for path in sorted(cache_root.glob("*.npy"))
        },
    }
    identity["cache_identity_sha256"] = _payload_sha(identity)
    _write_json(cache_root / "cache_identity.json", identity)
    return identity


def _symbol_dirs(root: Path) -> set[str]:
    return {
        child.name.split("=", 1)[1]
        for child in root.glob("symbol=*")
        if child.is_dir() and "=" in child.name
    }


def _symbols_from_aggtrade_tar(path: Path) -> set[str]:
    import re
    import tarfile

    expression = re.compile(r"/compact_1m/symbol=([^/]+)/month=")
    with tarfile.open(path, "r:") as archive:
        return {
            match.group(1)
            for member in archive.getmembers()
            if member.isfile()
            for match in [expression.search(member.name)]
            if match is not None
        }


def _symbols_from_oi_map(path: Path) -> set[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    output: set[str] = set()
    for venue in payload.get("venues", {}).values():
        for value in venue.values():
            symbol = value.get("symbol") if isinstance(value, dict) else value
            if isinstance(symbol, str) and symbol.endswith("USDT"):
                output.add(symbol.replace("-", ""))
    return output


def _symbols_from_oi_top50_tar(path: Path) -> set[str]:
    import tarfile

    with tarfile.open(path, "r:") as archive:
        member = next(
            item
            for item in archive.getmembers()
            if item.isfile() and item.name.endswith("/symbol_map.json")
        )
        payload = json.load(archive.extractfile(member))
    bybit = payload.get("venues", {}).get("bybit", {})
    output = {
        str(symbol)
        for symbol in bybit.values()
        if isinstance(symbol, str) and symbol.endswith("USDT")
    }
    for base in payload.get("top_bases", []):
        if base in bybit:
            continue
        output.add(f"{base}USDT")
    return output


@dataclass(frozen=True)
class RunConfig:
    output_root: Path
    runtime_root: Path
    start_month: str
    end_month: str
    membership_start: str
    membership_end: str
    top_n: int
    trailing_days: int
    minimum_observed_days: int
    lifecycle_gap_days: int
    workers: int
    timeout_seconds: int
    retries: int
    v3_root: Path
    agg_top100_tar: Path
    agg_101_200_tar: Path
    oi_51_200_symbol_map: Path
    oi_top50_tar: Path | None


def run(config: RunConfig) -> dict[str, Any]:
    started_at = datetime.now(UTC)
    wall_started = time.perf_counter()
    cpu_started = time.process_time()
    if config.workers not in {8, 10}:
        raise ValueError("workers must be 10, or 8 after a fail-closed memory gate")
    months = frozenset(_month_strings(config.start_month, config.end_month))
    frozen_contract = {
        "contract_version": CONTRACT_VERSION,
        "created_at": started_at.isoformat(),
        "objective": (
            "independently admit delivered data and build a lagged historical "
            "crypto Top-N membership/context authority without running search"
        ),
        "source": {
            "symbol_prefix": SYMBOL_PREFIX,
            "exchange_info_url": EXCHANGE_INFO_URL,
            "monthly_kline_interval": "1d",
            "source_checksum_required": True,
            "raw_zip_retention": "none_after_verified_compact_parse",
        },
        "universe": {
            "quote_asset": "USDT",
            "contract_surface": "crypto coin perpetual candidates",
            "membership_start": config.membership_start,
            "membership_end": config.membership_end,
            "top_n": config.top_n,
            "ranking_measure": "sum_quote_volume",
            "trailing_days": config.trailing_days,
            "minimum_observed_days": config.minimum_observed_days,
            "information_lag": "one completed UTC day",
            "active_evidence": "observed on previous completed UTC day",
            "tie_break": "instrument_id ascending",
            "lifecycle_gap_days": config.lifecycle_gap_days,
            "lit_identity_contract": {
                "old_end": LIT_OLD_END.isoformat(),
                "new_start": LIT_NEW_START.isoformat(),
                "intervening_dates": "quarantined",
            },
        },
        "schema2_context": {
            "grain": "daily authority ledger",
            "fields": [
                "active_universe_size",
                "listing_age_hours",
                "history_length_hours",
                "age_percentile_active_universe",
            ],
            "search_cache": False,
            "post_join_rebuild_still_required": True,
            "reward_adaptation": False,
        },
        "boundaries": {
            "search": False,
            "oos": False,
            "promotion": False,
            "challenge_recent_may_stress_forward": False,
            "latent": False,
            "relational_training": False,
        },
        "parameters_frozen_without_hpo": True,
        "workers": config.workers,
    }
    stable_contract = {
        key: value for key, value in frozen_contract.items() if key != "created_at"
    }
    frozen_contract["contract_sha256"] = _payload_sha(stable_contract)
    contract_path = config.runtime_root / "frozen_contract.json"
    if contract_path.exists():
        existing = json.loads(contract_path.read_text(encoding="utf-8"))
        existing_stable = {
            key: value
            for key, value in existing.items()
            if key not in {"created_at", "contract_sha256"}
        }
        if existing_stable != stable_contract:
            raise ValueError("existing runtime root is bound to a different frozen contract")
    _write_json(contract_path, frozen_contract)

    symbol_snapshot = (
        config.output_root / "source_snapshots" / "official_symbol_prefixes.json"
    )
    exchange_snapshot = config.output_root / "source_snapshots" / "exchange_info.json"
    if symbol_snapshot.exists() and exchange_snapshot.exists():
        official_symbols = json.loads(
            symbol_snapshot.read_text(encoding="utf-8")
        )["symbols"]
        exchange_info = json.loads(exchange_snapshot.read_text(encoding="utf-8"))
        snapshot_mode = "REUSED_ABORT_SAFE_SOURCE_SNAPSHOT"
    else:
        official_symbols, exchange_info = fetch_source_snapshots(
            timeout_seconds=config.timeout_seconds,
            retries=config.retries,
        )
        snapshot_mode = "FETCHED_CURRENT_SOURCE_SNAPSHOT"
    classification = classify_symbols(official_symbols, exchange_info)
    admitted_symbols = sorted(
        classification.loc[
            classification["admitted_crypto_surface"], "symbol"
        ].astype(str)
    )
    unresolved = classification.loc[
        classification["classification"].eq("UNRESOLVED"), "symbol"
    ].astype(str).tolist()
    _write_json(
        config.output_root / "source_snapshots" / "official_symbol_prefixes.json",
        {"symbols": official_symbols},
    )
    _write_json(
        config.output_root / "source_snapshots" / "exchange_info.json",
        exchange_info,
    )
    _write_parquet(config.output_root / "symbol_classification.parquet", classification)

    object_tasks = [
        {
            "symbol": symbol,
            "month": month,
            "key": f"{SYMBOL_PREFIX}{symbol}/1d/{symbol}-1d-{month}.zip",
            "source_bytes": None,
            "source_etag": None,
            "source_last_modified": None,
        }
        for symbol in admitted_symbols
        for month in sorted(months)
    ]
    with ThreadPoolExecutor(max_workers=config.workers) as executor:
        downloaded = list(
            executor.map(
                lambda task: download_object(
                    task,
                    timeout_seconds=config.timeout_seconds,
                    retries=config.retries,
                ),
                object_tasks,
            )
        )
    manifest = pd.DataFrame([result[0] for result in downloaded])
    frames = [result[1] for result in downloaded if result[1] is not None]
    failures = manifest.loc[manifest["status"].eq("FAIL")].copy()
    if not frames:
        raise RuntimeError("no official daily kline objects passed checksum and parse")
    daily_source = pd.concat(frames, ignore_index=True).sort_values(["symbol", "date"])
    duplicate_coordinates = int(daily_source.duplicated(["symbol", "date"]).sum())
    if duplicate_coordinates:
        raise ValueError("official daily kline inputs contain duplicate symbol-date rows")
    zero_volume_rows = int(daily_source["quote_volume"].le(0.0).sum())
    daily = daily_source.loc[daily_source["quote_volume"].gt(0.0)].copy()
    daily, identity_ledger = assign_instrument_lifecycles(
        daily,
        gap_days=config.lifecycle_gap_days,
    )
    universe, universe_summary = build_lagged_pit_universe(
        daily,
        start_date=config.membership_start,
        end_date=config.membership_end,
        top_n=config.top_n,
        trailing_days=config.trailing_days,
        minimum_observed_days=config.minimum_observed_days,
    )
    context = build_daily_context(universe, identity_ledger)

    oi_top50_raw_symbols: set[str] = set()
    if config.oi_top50_tar is not None:
        oi_top50_raw_symbols = _symbols_from_oi_top50_tar(config.oi_top50_tar)
    surfaces = {
        "CURRENT_498_HOURLY_PANEL": _symbol_dirs(config.v3_root),
        "AGGTRADES_FIXED_CURRENT_200": (
            _symbols_from_aggtrade_tar(config.agg_top100_tar)
            | _symbols_from_aggtrade_tar(config.agg_101_200_tar)
        ),
        "OI_MARK_FIXED_CURRENT_51_200": _symbols_from_oi_map(
            config.oi_51_200_symbol_map
        ),
    }
    if config.oi_top50_tar is not None:
        surfaces["OI_MARK_FIXED_CURRENT_1_200"] = (
            surfaces["OI_MARK_FIXED_CURRENT_51_200"]
            | oi_top50_raw_symbols
        )
    cohort_coverage = coverage_against_surfaces(universe, surfaces=surfaces)

    config.output_root.mkdir(parents=True, exist_ok=True)
    _write_parquet(config.output_root / "source_object_manifest.parquet", manifest)
    _write_parquet(config.output_root / "daily_quote_volume.parquet", daily)
    _write_parquet(
        config.output_root / "instrument_identity_ledger.parquet", identity_ledger
    )
    _write_parquet(config.output_root / "historical_pit_universe.parquet", universe)
    _write_parquet(
        config.output_root / "historical_pit_universe_daily_summary.parquet",
        universe_summary,
    )
    _write_parquet(
        config.output_root / "schema2_context_authority_daily.parquet", context
    )
    _write_parquet(
        config.output_root / "surface_cohort_overlap.parquet", cohort_coverage
    )
    hourly_context_identity = build_hourly_schema2_intersection_cache(
        universe=universe,
        identity_ledger=identity_ledger,
        v3_root=config.v3_root,
        cache_root=config.output_root
        / "schema2_context_cache_current498_pit_intersection",
    )
    temporal_surfaces = {
        "CURRENT_498_HOURLY_ACTUAL": _hourly_cache_symbol_dates(
            config.output_root
            / "schema2_context_cache_current498_pit_intersection"
        ),
        "AGGTRADES_DELIVERED_ACTUAL": (
            _aggtrade_symbol_dates_from_tar(config.agg_top100_tar)
            | _aggtrade_symbol_dates_from_tar(config.agg_101_200_tar)
        ),
        "OI_MARK_SCHEMAFIXED_51_200_ACTUAL": _oi_symbol_dates(
            config.oi_51_200_symbol_map.parent
        ),
    }
    coverage, missing_rows, backfill_requirements = (
        coverage_against_temporal_surfaces(
            universe,
            surfaces=temporal_surfaces,
        )
    )
    _write_parquet(config.output_root / "surface_coverage.parquet", coverage)
    _write_parquet(config.output_root / "surface_missing_members.parquet", missing_rows)
    _write_parquet(
        config.output_root / "surface_backfill_requirements.parquet",
        backfill_requirements,
    )

    input_identity = {
        "official_symbol_prefixes_sha256": _payload_sha(official_symbols),
        "exchange_info_sha256": _payload_sha(exchange_info),
        "source_object_manifest_sha256": _payload_sha(
            manifest.fillna("").astype(str).to_dict("records")
        ),
        "requested_symbol_months": len(manifest),
        "source_object_count": int(manifest["status"].eq("PASS").sum()),
        "source_not_found_count": int(manifest["status"].eq("NOT_FOUND").sum()),
        "source_download_bytes": int(manifest["download_bytes"].sum()),
        "source_failures": len(failures),
        "source_snapshot_mode": snapshot_mode,
        "source_daily_rows": len(daily_source),
        "active_positive_volume_daily_rows": len(daily),
        "zero_volume_inactive_rows_excluded": zero_volume_rows,
    }
    complete_days = int(universe_summary["top_n_complete"].sum())
    membership_days = len(universe_summary)
    coverage_summary = (
        coverage.groupby("surface_id")
        .agg(
            mean_coverage_rate=("coverage_rate", "mean"),
            minimum_coverage_rate=("coverage_rate", "min"),
            maximum_coverage_rate=("coverage_rate", "max"),
            missing_member_days=("missing_count", lambda values: int((values > 0).sum())),
        )
        .reset_index()
        .to_dict("records")
    )
    holds: list[str] = []
    if len(failures):
        holds.append("OFFICIAL_SOURCE_OBJECT_FAILURE")
    if unresolved:
        holds.append("UNRESOLVED_INSTRUMENT_CLASSIFICATION")
    if complete_days != membership_days:
        holds.append("HISTORICAL_TOP_N_INCOMPLETE")
    if any(float(row["minimum_coverage_rate"]) < 1.0 for row in coverage_summary):
        holds.append("DELIVERED_FEATURE_SURFACES_DO_NOT_COVER_HISTORICAL_PIT_UNIVERSE")
    if identity_ledger["instrument_id"].astype(str).str.endswith("::QUARANTINED").any():
        holds.append("QUARANTINED_TICKER_REUSE_COORDINATES")
    inferred_lifecycles = (
        identity_ledger.loc[
            identity_ledger["identity_status"].eq("INFERRED_GAP_BOUNDED")
        ]
        .groupby("raw_symbol")["instrument_id"]
        .nunique()
    )
    inferred_multi_lifecycle_symbols = sorted(
        inferred_lifecycles.loc[inferred_lifecycles.gt(1)].index.astype(str)
    )
    if inferred_multi_lifecycle_symbols:
        holds.append("INFERRED_MULTI_LIFECYCLE_IDENTITY_REVIEW")
    pit_blocking_holds = {
        "OFFICIAL_SOURCE_OBJECT_FAILURE",
        "UNRESOLVED_INSTRUMENT_CLASSIFICATION",
        "HISTORICAL_TOP_N_INCOMPLETE",
        "QUARANTINED_TICKER_REUSE_COORDINATES",
        "INFERRED_MULTI_LIFECYCLE_IDENTITY_REVIEW",
    }
    if pit_blocking_holds.intersection(holds):
        decision = "HOLD_PIT_UNIVERSE_AND_SEARCH_CACHE"
    elif holds:
        decision = "PASS_PIT_LEDGER_HOLD_SEARCH_CACHE"
    else:
        decision = "PASS_PIT_LEDGER_AND_SURFACE_COVERAGE"
    final_decision = {
        "decision": decision,
        "pit_ledger_status": (
            "PROVISIONAL_FAIL_CLOSED"
            if pit_blocking_holds.intersection(holds)
            else "QUALIFIED"
        ),
        "holds": holds,
        "contract_sha256": frozen_contract["contract_sha256"],
        "membership_days": membership_days,
        "complete_top_n_days": complete_days,
        "universe_rows": len(universe),
        "distinct_raw_symbols_selected": int(universe["raw_symbol"].nunique()),
        "distinct_instruments_selected": int(universe["instrument_id"].nunique()),
        "source": input_identity,
        "unresolved_symbols": unresolved,
        "inferred_multi_lifecycle_symbols": inferred_multi_lifecycle_symbols,
        "coverage": coverage_summary,
        "coverage_semantics": (
            "actual delivered symbol-date support; Top50 raw excluded because "
            "no materialized authorized consumer"
        ),
        "surface_missing_member_rows": len(missing_rows),
        "surface_backfill_requirement_rows": len(backfill_requirements),
        "zero_volume_semantics": (
            "quote_volume <= 0 is inactive and excluded before lifecycle/ranking"
        ),
        "search_started": False,
        "search_cache_authorized": False,
        "schema2_context_authority_built": True,
        "schema2_hourly_intersection_cache": hourly_context_identity,
        "oi_top50_raw_symbol_map_count": len(oi_top50_raw_symbols),
        "oi_top50_raw_search_consumer_status": (
            "NOT_MATERIALIZED_OR_AUTHORIZED"
            if config.oi_top50_tar is not None
            else "NOT_IN_RUN_INPUTS"
        ),
        "post_join_schema2_rebuild_required": True,
    }
    _write_json(config.runtime_root / "embedded_preflight.json", final_decision)
    _write_json(config.runtime_root / "final_decision.json", final_decision)

    outputs = [
        config.output_root / "symbol_classification.parquet",
        config.output_root / "source_object_manifest.parquet",
        config.output_root / "daily_quote_volume.parquet",
        config.output_root / "instrument_identity_ledger.parquet",
        config.output_root / "historical_pit_universe.parquet",
        config.output_root / "historical_pit_universe_daily_summary.parquet",
        config.output_root / "schema2_context_authority_daily.parquet",
        config.output_root / "surface_coverage.parquet",
        config.output_root / "surface_cohort_overlap.parquet",
        config.output_root / "surface_missing_members.parquet",
        config.output_root / "surface_backfill_requirements.parquet",
        config.output_root
        / "schema2_context_cache_current498_pit_intersection"
        / "cache_identity.json",
        config.output_root
        / "schema2_context_cache_current498_pit_intersection"
        / "source_file_manifest.parquet",
        config.runtime_root / "frozen_contract.json",
        config.runtime_root / "embedded_preflight.json",
        config.runtime_root / "final_decision.json",
    ]
    run_manifest = {
        "experiment_id": f"crypto_new_data_admission_v1_{started_at:%Y%m%d}",
        "contract_version": CONTRACT_VERSION,
        "contract_sha256": frozen_contract["contract_sha256"],
        "objective": frozen_contract["objective"],
        "started_at": started_at.isoformat(),
        "completed_at": datetime.now(UTC).isoformat(),
        "input_identity": input_identity,
        "parameters": frozen_contract["universe"],
        "exact_command": " ".join(os.sys.argv),
        "outputs": [
            {
                "path": str(path),
                "bytes": path.stat().st_size,
                "sha256": _sha256(path.read_bytes()),
            }
            for path in outputs
        ],
        "cost": {
            "wall_seconds": time.perf_counter() - wall_started,
            "total_process_cpu_seconds_including_threads": (
                time.process_time() - cpu_started
            ),
            "cpu_accounting": "single Python process; thread CPU is included once",
            "download_bytes": int(manifest["download_bytes"].sum()),
            "workers": config.workers,
        },
        "reproducibility": {
            "source_checksums_verified": len(failures) == 0,
            "deterministic_rank_tie_break": "instrument_id ascending",
            "reward_or_search_feedback": False,
        },
        "continuation": {
            "rerun": "repeat the exact command; source snapshots and object checksums bind identity",
            "future_search": "requires separate authorization after all holds are cleared",
        },
        "failure": {
            "failed_source_objects": failures[
                ["symbol", "month", "source_url", "error"]
            ].to_dict("records"),
            "holds": holds,
        },
        "final_decision": final_decision,
    }
    _write_json(config.runtime_root / "run_manifest.json", run_manifest)
    return run_manifest


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--start-month", default="2023-12")
    parser.add_argument("--end-month", default="2026-06")
    parser.add_argument("--membership-start", default="2024-01-01")
    parser.add_argument("--membership-end", default="2026-06-11")
    parser.add_argument("--top-n", type=int, default=200)
    parser.add_argument("--trailing-days", type=int, default=30)
    parser.add_argument("--minimum-observed-days", type=int, default=7)
    parser.add_argument("--lifecycle-gap-days", type=int, default=30)
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--timeout-seconds", type=int, default=60)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--v3-root", type=Path, required=True)
    parser.add_argument("--agg-top100-tar", type=Path, required=True)
    parser.add_argument("--agg-101-200-tar", type=Path, required=True)
    parser.add_argument("--oi-51-200-symbol-map", type=Path, required=True)
    parser.add_argument("--oi-top50-tar", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    config = RunConfig(
        output_root=args.output_root,
        runtime_root=args.runtime_root,
        start_month=args.start_month,
        end_month=args.end_month,
        membership_start=args.membership_start,
        membership_end=args.membership_end,
        top_n=args.top_n,
        trailing_days=args.trailing_days,
        minimum_observed_days=args.minimum_observed_days,
        lifecycle_gap_days=args.lifecycle_gap_days,
        workers=args.workers,
        timeout_seconds=args.timeout_seconds,
        retries=args.retries,
        v3_root=args.v3_root,
        agg_top100_tar=args.agg_top100_tar,
        agg_101_200_tar=args.agg_101_200_tar,
        oi_51_200_symbol_map=args.oi_51_200_symbol_map,
        oi_top50_tar=args.oi_top50_tar,
    )
    manifest = run(config)
    print(json.dumps(manifest["final_decision"], indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
