"""Development-only reader for the already-qualified native aggTrades release.

The adapter intentionally names every allowed symbol-month coordinate.  It never
walks the parent release root, so the physically adjacent challenge directory is
outside the reachable input surface.
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

import numpy as np
import pandas as pd


FORBIDDEN_ROLE_TOKENS = (
    "challenge",
    "validation",
    "holdout",
    "recent",
    "forward",
    "may_stress",
    "test",
)


def _readonly_array(values: np.ndarray) -> np.ndarray:
    result = np.array(values, copy=True)
    result.setflags(write=False)
    return result


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


def _safe_development_root(path: Path) -> Path:
    resolved = path.resolve()
    if resolved.name.lower() != "development":
        raise PermissionError("release_root must be the physical development directory")
    lowered_parts = {part.lower() for part in resolved.parts}
    if any(token in lowered_parts for token in FORBIDDEN_ROLE_TOKENS):
        raise PermissionError(f"prohibited role token in development root: {resolved}")
    return resolved


def _safe_coordinate(root: Path, symbol: str, month: str) -> Path:
    path = (root / f"symbol={symbol}" / f"month={month}" / "part.parquet").resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:  # pragma: no cover - defensive path traversal guard.
        raise PermissionError(f"coordinate escaped development root: {path}") from exc
    lowered = path.as_posix().lower()
    if any(f"/{token}/" in lowered for token in FORBIDDEN_ROLE_TOKENS):
        raise PermissionError(f"prohibited role path: {path}")
    return path


@dataclass(frozen=True)
class ReleasePanel:
    release_id: str
    development_view_id: str
    assets: tuple[str, ...]
    timestamps: pd.DatetimeIndex
    fields: Mapping[str, np.ndarray]
    close_price: np.ndarray
    month_labels: np.ndarray
    observable_times: pd.DatetimeIndex
    release_manifest: Mapping[str, Any]
    sealed_reads: int = 0

    def __post_init__(self) -> None:
        frozen_fields = {
            str(name): _readonly_array(values) for name, values in self.fields.items()
        }
        object.__setattr__(self, "fields", MappingProxyType(frozen_fields))
        object.__setattr__(self, "close_price", _readonly_array(self.close_price))
        object.__setattr__(self, "month_labels", _readonly_array(self.month_labels))
        object.__setattr__(
            self,
            "release_manifest",
            MappingProxyType(deepcopy(dict(self.release_manifest))),
        )

    def target_return(self, horizon_hours: int) -> np.ndarray:
        """Return the frozen PIT-safe target for a signal bucket at coordinate t.

        A completed hour t is observable at t+1h.  The canary waits a further
        complete hour and enters at t+2h, then measures the configured horizon.
        """

        if horizon_hours not in (1, 4):
            raise ValueError(f"unsupported target horizon: {horizon_hours}")
        execution_offset = 2
        result = np.full(self.close_price.shape, np.nan, dtype=float)
        usable = self.close_price.shape[1] - execution_offset - horizon_hours
        if usable <= 0:
            return result
        start = self.close_price[:, execution_offset : execution_offset + usable]
        stop = self.close_price[
            :, execution_offset + horizon_hours : execution_offset + horizon_hours + usable
        ]
        valid = np.isfinite(start) & np.isfinite(stop) & (start > 0.0) & (stop > 0.0)
        values = np.full(start.shape, np.nan, dtype=float)
        values[valid] = np.log(stop[valid] / start[valid])
        result[:, :usable] = values
        return result

    def time_slice(self, start: str, end: str) -> "ReleasePanel":
        start_ts = pd.Timestamp(start)
        end_ts = pd.Timestamp(end)
        if start_ts.tzinfo is None:
            start_ts = start_ts.tz_localize("UTC")
        else:
            start_ts = start_ts.tz_convert("UTC")
        if end_ts.tzinfo is None:
            end_ts = end_ts.tz_localize("UTC")
        else:
            end_ts = end_ts.tz_convert("UTC")
        mask = (self.timestamps >= start_ts) & (self.timestamps <= end_ts)
        if not np.any(mask):
            raise ValueError("requested development time slice is empty")
        return ReleasePanel(
            release_id=self.release_id,
            development_view_id=self.development_view_id,
            assets=self.assets,
            timestamps=self.timestamps[mask],
            fields={name: values[:, mask] for name, values in self.fields.items()},
            close_price=self.close_price[:, mask],
            month_labels=self.month_labels[mask],
            observable_times=self.observable_times[mask],
            release_manifest=self.release_manifest,
            sealed_reads=self.sealed_reads,
        )


def _calendar_hours(month: str) -> int:
    start = pd.Timestamp(f"{month}-01", tz="UTC")
    stop = start + pd.offsets.MonthBegin(1)
    return int((stop - start) / pd.Timedelta(hours=1))


def load_development_release(config: Mapping[str, Any]) -> ReleasePanel:
    from .grammar import FROZEN_RELEASE_FIELDS

    release = config["release"]
    if config["boundaries"]["allowed_data_role"] != "DEVELOPMENT_TRAIN_ONLY":
        raise PermissionError("canary configuration is not development-train-only")

    release_root = _safe_development_root(Path(release["release_root"]))
    source_root = Path(release["source_root"]).resolve()
    if not release_root.is_dir() or not source_root.is_dir():
        raise FileNotFoundError("registered development release or source root is missing")

    assets = tuple(str(value) for value in release["symbols"])
    months = tuple(str(value) for value in release["months"])
    searchable = tuple(str(value) for value in release["searchable_fields"])
    if searchable != FROZEN_RELEASE_FIELDS:
        raise ValueError("release searchable fields diverged from frozen grammar authority")
    if len(set(assets)) != len(assets) or len(set(months)) != len(months):
        raise ValueError("duplicate release coordinate identity")
    if any("2026" in month for month in months):
        raise PermissionError("2026 access is prohibited")

    output_columns = [
        "timestamp",
        "symbol",
        "month",
        *searchable,
        "observable_time",
        "maturity",
        "source_lag_seconds",
        "missing_any",
    ]
    source_columns = ["timestamp", "close_price"]
    frames: list[pd.DataFrame] = []
    source_records: list[dict[str, str]] = []
    output_records: list[dict[str, str]] = []
    file_records: list[dict[str, Any]] = []

    for symbol in assets:
        for month in months:
            output_path = _safe_coordinate(release_root, symbol, month)
            source_path = _safe_coordinate(source_root, symbol, month)
            if not output_path.is_file() or not source_path.is_file():
                raise FileNotFoundError(f"missing registered coordinate: {symbol} {month}")
            output_sha = sha256_file(output_path)
            source_sha = sha256_file(source_path)
            output_records.append({"symbol": symbol, "month": month, "sha256": output_sha})
            source_records.append({"symbol": symbol, "month": month, "sha256": source_sha})

            feature = pd.read_parquet(output_path, columns=output_columns)
            target_source = pd.read_parquet(source_path, columns=source_columns)
            feature["timestamp"] = pd.to_datetime(feature["timestamp"], utc=True)
            feature["observable_time"] = pd.to_datetime(feature["observable_time"], utc=True)
            feature["maturity"] = pd.to_datetime(feature["maturity"], utc=True)
            target_source["timestamp"] = pd.to_datetime(target_source["timestamp"], utc=True)
            if len(feature) != _calendar_hours(month) or len(target_source) != len(feature):
                raise ValueError(f"incomplete hourly coordinate: {symbol} {month}")
            if feature["timestamp"].duplicated().any() or target_source["timestamp"].duplicated().any():
                raise ValueError(f"duplicate timestamp: {symbol} {month}")
            if not feature["symbol"].eq(symbol).all() or not feature["month"].eq(month).all():
                raise ValueError(f"coordinate identity mismatch: {symbol} {month}")
            if feature["missing_any"].astype(bool).any():
                raise ValueError(f"missing_any is true: {symbol} {month}")
            expected_observable = feature["timestamp"] + pd.Timedelta(hours=1)
            if not feature["observable_time"].equals(expected_observable):
                raise ValueError(f"observable_time drift: {symbol} {month}")
            if not feature["maturity"].equals(expected_observable):
                raise ValueError(f"maturity drift: {symbol} {month}")
            if not pd.to_numeric(feature["source_lag_seconds"], errors="coerce").eq(0).all():
                raise ValueError(f"source lag drift: {symbol} {month}")
            merged = feature.merge(target_source, on="timestamp", how="left", validate="one_to_one")
            if merged["close_price"].isna().any() or (merged["close_price"] <= 0).any():
                raise ValueError(f"target-only close source is incomplete: {symbol} {month}")
            frames.append(merged)
            file_records.append(
                {
                    "symbol": symbol,
                    "month": month,
                    "role": "DEVELOPMENT_TRAIN_ONLY",
                    "output_path": output_path.as_posix(),
                    "output_sha256": output_sha,
                    "source_path": source_path.as_posix(),
                    "source_sha256": source_sha,
                    "rows": int(len(merged)),
                    "searchable_fields_read": list(searchable),
                    "target_only_fields_read": ["close_price"],
                }
            )

    source_bundle = canonical_sha256(source_records)
    output_bundle = canonical_sha256(output_records)
    if source_bundle != release["expected_source_bundle_sha256"]:
        raise ValueError(
            "development source bundle hash mismatch: "
            f"{source_bundle} != {release['expected_source_bundle_sha256']}"
        )
    if output_bundle != release["expected_output_bundle_sha256"]:
        raise ValueError(
            "development output bundle hash mismatch: "
            f"{output_bundle} != {release['expected_output_bundle_sha256']}"
        )

    combined = pd.concat(frames, ignore_index=True).sort_values(
        ["symbol", "timestamp"], kind="mergesort"
    )
    if len(combined) != int(release["expected_hourly_rows"]):
        raise ValueError("development hourly row count drift")
    timestamps = pd.DatetimeIndex(sorted(combined["timestamp"].unique()))
    if len(timestamps) != int(release["expected_timestamps"]):
        raise ValueError("development timestamp count drift")

    field_rows: dict[str, list[np.ndarray]] = {}
    close_rows: list[np.ndarray] = []
    observable_reference: pd.DatetimeIndex | None = None
    for symbol in assets:
        block = combined[combined["symbol"].eq(symbol)].sort_values("timestamp", kind="mergesort")
        block = block.set_index("timestamp").reindex(timestamps)
        if block["symbol"].isna().any():
            raise ValueError(f"fixed asset-time axis is incomplete: {symbol}")
        for field in searchable:
            field_rows.setdefault(field, [])
            field_rows[field].append(
                pd.to_numeric(block[field], errors="coerce").to_numpy(float)
            )
        close_rows.append(pd.to_numeric(block["close_price"], errors="coerce").to_numpy(float))
        observed = pd.DatetimeIndex(block["observable_time"])
        if observable_reference is None:
            observable_reference = observed
        elif not observable_reference.equals(observed):
            raise ValueError("observable-time axis differs by asset")
    field_matrices = {name: np.vstack(rows) for name, rows in field_rows.items()}
    if any(not np.isfinite(values).all() for values in field_matrices.values()):
        raise ValueError("searchable release field contains non-finite values")
    close = np.vstack(close_rows)
    if not np.isfinite(close).all():
        raise ValueError("target-only close panel contains non-finite values")
    month_labels = timestamps.strftime("%Y-%m").to_numpy(dtype=str)

    manifest: dict[str, Any] = {
        "schema_version": 1,
        "release_id": release["parent_release_id"],
        "development_view_id": release["development_view_id"],
        "data_role": "DEVELOPMENT_TRAIN_ONLY",
        "parent_release_content_sha256": release["parent_release_content_sha256"],
        "source_bundle_sha256": source_bundle,
        "output_bundle_sha256": output_bundle,
        "development_view_sha256": canonical_sha256(
            {
                "release_id": release["parent_release_id"],
                "assets": list(assets),
                "months": list(months),
                "source_bundle_sha256": source_bundle,
                "output_bundle_sha256": output_bundle,
                "searchable_fields": list(searchable),
                "target_only_fields": ["close_price"],
            }
        ),
        "release_root": release_root.as_posix(),
        "source_root": source_root.as_posix(),
        "assets": list(assets),
        "months": list(months),
        "first_timestamp": timestamps.min().isoformat(),
        "last_timestamp": timestamps.max().isoformat(),
        "hourly_rows": int(len(combined)),
        "timestamps": int(len(timestamps)),
        "coordinate_files": int(len(file_records)),
        "searchable_fields": list(searchable),
        "target_only_fields": ["close_price"],
        "pit_contract": {
            "observable_time": "timestamp + 1h",
            "maturity": "timestamp + 1h",
            "source_lag_seconds": 0,
            "partial_current_hour": "PROHIBITED",
            "no_fill": True,
        },
        "target_horizon_contract": dict(config["target_horizon"]),
        "file_records": file_records,
        "sealed_reads": 0,
        "challenge_path_enumerated": False,
        "old_qualification_bundle_status": "SUPERSEDED_NOT_SELF_CONSISTENT",
        "superseded_qualification_index_mismatches": list(
            release["superseded_qualification_index_mismatches"]
        ),
    }
    manifest["manifest_sha256"] = canonical_sha256(manifest)
    return ReleasePanel(
        release_id=str(release["parent_release_id"]),
        development_view_id=str(release["development_view_id"]),
        assets=assets,
        timestamps=timestamps,
        fields=field_matrices,
        close_price=close,
        month_labels=month_labels,
        observable_times=(
            observable_reference
            if observable_reference is not None
            else pd.DatetimeIndex([])
        ),
        release_manifest=manifest,
        sealed_reads=0,
    )
