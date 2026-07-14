from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd


PROHIBITED_PERFORMANCE_TOKENS = (
    "forward",
    "fwd",
    "label",
    "reward",
    "target",
    "pnl",
    "return",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(payload).hexdigest().upper()


@dataclass(frozen=True)
class ReleaseEvidence:
    release_id: str
    content_sha256: str
    role: str
    months: tuple[str, ...]
    symbols: tuple[str, ...]
    coordinate_count: int
    source_bundle_sha256: str
    release_bundle_sha256: str
    qualification_bundle_sha256: str
    qualification_index_mismatches: tuple[str, ...]
    first_timestamp: str
    last_timestamp: str
    row_count_hourly: int
    row_count_daily: int
    no_fill: bool
    source_and_release_hashes_verified: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_qualification_artifacts(qualification_root: Path) -> tuple[str, tuple[str, ...]]:
    index_path = qualification_root / "release_artifact_index.csv"
    if not index_path.exists():
        raise FileNotFoundError(index_path)
    index = pd.read_csv(index_path)
    records: list[dict[str, Any]] = []
    mismatches: list[str] = []
    for row in index.sort_values("artifact", kind="mergesort").itertuples():
        artifact = qualification_root.parents[1] / Path(row.artifact).relative_to("runtime")
        if not artifact.exists():
            raise FileNotFoundError(artifact)
        observed = sha256_file(artifact)
        declared = str(row.sha256).upper()
        if observed != declared:
            mismatches.append(str(row.artifact))
        records.append(
            {
                "artifact": str(row.artifact),
                "declared_sha256": declared,
                "observed_sha256": observed,
                "role": row.role,
            }
        )
    return canonical_sha256(records), tuple(mismatches)


def _has_prohibited_performance_column(columns: Iterable[str]) -> list[str]:
    prohibited: list[str] = []
    for column in columns:
        normalized = str(column).lower()
        if any(token in normalized for token in PROHIBITED_PERFORMANCE_TOKENS):
            prohibited.append(str(column))
    return sorted(prohibited)


def validate_external_release_manifest(manifest: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    required_metadata = set(contract["required_metadata"])
    missing = sorted(required_metadata - set(manifest))
    failures: list[str] = []
    if missing:
        failures.append("MISSING_METADATA")
    if manifest.get("data_role") != "DEVELOPMENT":
        failures.append("ROLE_NOT_DEVELOPMENT")
    allowed = set(manifest.get("allowed_research_roles", []))
    if "DEVELOPMENT_ONLY_REPRODUCTION" not in allowed:
        failures.append("DEVELOPMENT_USE_NOT_ALLOWED")
    if not manifest.get("content_sha256"):
        failures.append("CONTENT_HASH_MISSING")
    schema = manifest.get("schema", [])
    if not isinstance(schema, list) or not schema:
        failures.append("SCHEMA_MISSING")
    prohibited = _has_prohibited_performance_column(schema)
    if prohibited:
        failures.append("PROHIBITED_PERFORMANCE_COLUMNS")
    for semantic in ("event_time_semantics", "observable_time_semantics", "maturity_semantics"):
        if not manifest.get(semantic):
            failures.append(f"{semantic.upper()}_MISSING")
    return {
        "release_id": manifest.get("release_id"),
        "ready": not failures,
        "missing_metadata": missing,
        "prohibited_columns": prohibited,
        "failures": failures,
        "checks_required": list(contract["required_checks"]),
    }


def preflight_external_release(manifest_path: Path, contract: dict[str, Any]) -> dict[str, Any]:
    manifest_path = manifest_path.resolve()
    manifest = _read_json(manifest_path)
    result = validate_external_release_manifest(manifest, contract)
    failures = list(result["failures"])
    file_records: list[dict[str, Any]] = []
    frames: list[pd.DataFrame] = []
    for entry in manifest.get("files", []):
        path = Path(entry["path"])
        if not path.is_absolute():
            path = (manifest_path.parent / path).resolve()
        lowered = path.as_posix().lower()
        if any(token in lowered for token in ("challenge", "forward", "recent", "may_stress", "/test/")):
            failures.append("PROHIBITED_ROLE_PATH")
            continue
        if not path.exists():
            failures.append("DATA_FILE_MISSING")
            continue
        observed_sha = sha256_file(path)
        if observed_sha != str(entry.get("sha256", "")).upper():
            failures.append("PER_FILE_HASH_MISMATCH")
        if path.suffix.lower() == ".parquet":
            frame = pd.read_parquet(path)
        elif path.suffix.lower() == ".csv":
            frame = pd.read_csv(path)
        else:
            failures.append("UNSUPPORTED_FILE_FORMAT")
            continue
        expected_schema = list(manifest.get("schema", []))
        if list(frame.columns) != expected_schema:
            failures.append("SCHEMA_MISMATCH")
        frames.append(frame)
        file_records.append(
            {
                "path": path.as_posix(),
                "sha256": observed_sha,
                "rows": len(frame),
                "size_bytes": path.stat().st_size,
            }
        )
    if not file_records:
        failures.append("NO_DATA_FILES")
    bundle_sha = canonical_sha256(
        [{"path": record["path"], "sha256": record["sha256"], "rows": record["rows"]} for record in file_records]
    )
    if bundle_sha != str(manifest.get("content_sha256", "")).upper():
        failures.append("CONTENT_HASH_MISMATCH")

    combined = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    primary_key = list(manifest.get("primary_key", []))
    if not primary_key or any(column not in combined.columns for column in primary_key):
        failures.append("PRIMARY_KEY_MISSING")
    elif combined.duplicated(primary_key).any():
        failures.append("DUPLICATE_PRIMARY_KEY")
    time_fields = manifest.get("time_fields", {})
    event_field = time_fields.get("event")
    observable_field = time_fields.get("observable")
    maturity_field = time_fields.get("maturity")
    if not all(field in combined.columns for field in (event_field, observable_field, maturity_field)):
        failures.append("TIME_FIELDS_MISSING")
    elif not combined.empty:
        event = pd.to_datetime(combined[event_field], utc=True, errors="coerce")
        observable = pd.to_datetime(combined[observable_field], utc=True, errors="coerce")
        maturity = pd.to_datetime(combined[maturity_field], utc=True, errors="coerce")
        if event.isna().any() or observable.isna().any() or maturity.isna().any():
            failures.append("TIME_PARSE_FAILURE")
        if (observable < event).any() or (maturity < observable).any():
            failures.append("POINT_IN_TIME_ORDER_VIOLATION")
    if _has_prohibited_performance_column(combined.columns):
        failures.append("PROHIBITED_PERFORMANCE_COLUMNS")

    coverage = float(manifest.get("coverage_ratio", 0.0))
    minimum_coverage = float(manifest.get("minimum_coverage_ratio", 0.95))
    if not 0 <= coverage <= 1 or coverage < minimum_coverage:
        failures.append("COVERAGE_BELOW_CONTRACT")
    coverage_entry = manifest.get("coverage_ledger", {})
    coverage_value = coverage_entry.get("path")
    coverage_path = Path(coverage_value) if coverage_value else None
    if coverage_path is not None and not coverage_path.is_absolute():
        coverage_path = (manifest_path.parent / coverage_path).resolve()
    if coverage_path is None or not coverage_path.is_file():
        failures.append("COVERAGE_LEDGER_MISSING")
    elif sha256_file(coverage_path) != str(coverage_entry.get("sha256", "")).upper():
        failures.append("COVERAGE_LEDGER_HASH_MISMATCH")
    if not manifest.get("consumer_ids"):
        failures.append("NO_REGISTERED_CONSUMER")

    observed_release_facts: dict[str, Any] = {
        "row_count": int(len(combined)),
        "unique_dates": 0,
        "history_days": 0,
        "minimum_cross_sectional_assets": 0,
        "feature_non_null_rate": 0.0,
        "positive_variance_feature_fraction": 0.0,
        "maximum_turnover_observations": 0,
    }
    if not combined.empty and event_field in combined.columns:
        observed_event = pd.to_datetime(combined[event_field], utc=True, errors="coerce")
        valid_event = observed_event.dropna()
        if not valid_event.empty:
            event_day = observed_event.dt.floor("D")
            unique_dates = int(event_day.nunique())
            observed_release_facts["unique_dates"] = unique_dates
            observed_release_facts["history_days"] = int(
                (valid_event.max().floor("D") - valid_event.min().floor("D")).days + 1
            )
            observed_release_facts["maximum_turnover_observations"] = max(unique_dates - 1, 0)
            asset_field = manifest.get("adequacy_asset_field")
            if not asset_field:
                preferred = [column for column in ("symbol", "asset", "instrument", "ticker") if column in combined]
                non_time_primary = [
                    column
                    for column in primary_key
                    if column not in {event_field, observable_field, maturity_field}
                ]
                asset_field = (preferred or non_time_primary or [None])[0]
            if asset_field in combined.columns:
                per_day_assets = combined.assign(__event_day=event_day).groupby("__event_day")[asset_field].nunique()
                if not per_day_assets.empty:
                    observed_release_facts["minimum_cross_sectional_assets"] = int(per_day_assets.min())

    excluded_fields = set(primary_key) | {event_field, observable_field, maturity_field}
    declared_features = [column for column in manifest.get("adequacy_feature_fields", []) if column in combined]
    numeric_features = declared_features or [
        column
        for column in combined.select_dtypes(include=[np.number]).columns
        if column not in excluded_fields
    ]
    if numeric_features:
        feature_frame = combined[numeric_features]
        observed_release_facts["feature_non_null_rate"] = float(feature_frame.notna().mean().min())
        observed_release_facts["positive_variance_feature_fraction"] = float(
            (feature_frame.nunique(dropna=True) > 1).mean()
        )

    unique_failures = sorted(set(failures))
    result.update(
        {
            "ready": not unique_failures,
            "failures": unique_failures,
            "manifest_path": str(manifest_path),
            "observed_content_sha256": bundle_sha,
            "file_count": len(file_records),
            "row_count": int(len(combined)),
            "per_file_checks": file_records,
            "coverage_ratio": coverage,
            "minimum_coverage_ratio": minimum_coverage,
            "observed_release_facts": observed_release_facts,
            "point_in_time_checked": not any(
                failure in unique_failures
                for failure in ("TIME_FIELDS_MISSING", "TIME_PARSE_FAILURE", "POINT_IN_TIME_ORDER_VIOLATION")
            ),
        }
    )
    return result


def load_development_daily_panel(
    repo: Path,
    config: dict[str, Any],
    *,
    symbols: Iterable[str] | None = None,
) -> tuple[pd.DataFrame, ReleaseEvidence]:
    boundaries = config["boundaries"]
    if boundaries["allowed_role"] != "DEVELOPMENT" or not boundaries["development_only"]:
        raise PermissionError("frontier v2 release loader is development-only")

    release_contract = config["release"]
    release_cfg = _read_json(repo / release_contract["release_config"])
    qualification_root = repo / release_contract["qualification_root"]
    release_manifest = _read_json(qualification_root / "release_manifest.json")
    if release_manifest["release_id"] != release_contract["release_id"]:
        raise ValueError("release id mismatch")
    if release_manifest["content_sha256"] != release_contract["content_sha256"]:
        raise ValueError("release content hash mismatch")
    if release_manifest["performance_values_read"] or release_manifest["forward_read"]:
        raise PermissionError("qualified release records prohibited performance access")

    qualification_bundle, qualification_mismatches = _validate_qualification_artifacts(qualification_root)
    coverage = pd.read_csv(qualification_root / "coverage_ledger.csv")
    reads = pd.read_csv(qualification_root / "read_ledger.csv")
    selected_symbols = tuple(symbols or release_contract["fixed_complete_universe"])
    selected_months = tuple(release_contract["development_months"])

    coordinates = coverage[
        coverage.data_role.eq("DEVELOPMENT")
        & coverage.status.eq("QUALIFIED")
        & coverage.symbol.isin(selected_symbols)
        & coverage.month.isin(selected_months)
    ].copy()
    expected = {(symbol, month) for symbol in selected_symbols for month in selected_months}
    observed = set(zip(coordinates.symbol, coordinates.month))
    missing = sorted(expected - observed)
    if missing:
        raise ValueError(f"fixed asset axis has missing qualified coordinates: {missing}")
    if len(coordinates) != len(expected):
        raise ValueError("duplicate qualified coordinates")

    read_rows = reads[
        reads.data_role.eq("DEVELOPMENT")
        & reads.symbol.isin(selected_symbols)
        & reads.month.isin(selected_months)
    ].copy()
    if len(read_rows) != len(expected):
        raise ValueError("read ledger does not cover the fixed development axis")
    coordinates = coordinates.merge(
        read_rows[["symbol", "month", "data_role", "output_path", "output_sha256", "rows_read", "missing_rows"]],
        on=["symbol", "month", "data_role"],
        how="left",
        validate="one_to_one",
    )
    if coordinates.output_path.isna().any():
        raise ValueError("qualified coordinate lacks physical release output")
    if coordinates.interpolated.astype(str).str.lower().eq("true").any():
        raise ValueError("interpolated coordinates are prohibited")
    if (coordinates.missing_rows.astype(int) != 0).any():
        raise ValueError("release coordinate contains missing rows")

    feature_columns = [
        "timestamp",
        "symbol",
        "month",
        "quantity",
        "notional",
        "signed_aggressor_notional",
        "volume_imbalance",
        "vwap",
        "trade_count",
        "missing_any",
        "observable_time",
        "maturity",
    ]
    source_columns = ["timestamp", "open_price", "high_price", "low_price", "close_price"]
    frames: list[pd.DataFrame] = []
    source_hashes: list[dict[str, str]] = []
    output_hashes: list[dict[str, str]] = []
    verify_hashes = bool(release_contract["verify_source_and_release_hashes"])
    for row in coordinates.sort_values(["symbol", "month"], kind="mergesort").itertuples():
        source_path = Path(row.source_path)
        output_path = Path(row.output_path)
        if not source_path.exists() or not output_path.exists():
            raise FileNotFoundError(f"missing release coordinate files: {row.symbol} {row.month}")
        if "challenge" in output_path.as_posix().lower() or row.data_role != "DEVELOPMENT":
            raise PermissionError("non-development path reached by development loader")
        source_sha = sha256_file(source_path) if verify_hashes else str(row.source_sha256).upper()
        output_sha = sha256_file(output_path) if verify_hashes else str(row.output_sha256).upper()
        if source_sha != str(row.source_sha256).upper():
            raise ValueError(f"source hash mismatch: {source_path}")
        if output_sha != str(row.output_sha256).upper():
            raise ValueError(f"release output hash mismatch: {output_path}")
        source_hashes.append({"symbol": row.symbol, "month": row.month, "sha256": source_sha})
        output_hashes.append({"symbol": row.symbol, "month": row.month, "sha256": output_sha})

        feature = pd.read_parquet(output_path, columns=feature_columns)
        source = pd.read_parquet(source_path, columns=source_columns)
        if _has_prohibited_performance_column(feature.columns):
            raise ValueError("qualified release contains prohibited performance columns")
        feature["timestamp"] = pd.to_datetime(feature.timestamp, utc=True)
        source["timestamp"] = pd.to_datetime(source.timestamp, utc=True)
        if feature.timestamp.duplicated().any() or source.timestamp.duplicated().any():
            raise ValueError(f"duplicate timestamp: {row.symbol} {row.month}")
        merged = feature.merge(source, on="timestamp", how="left", validate="one_to_one")
        if merged[source_columns[1:]].isna().any().any():
            raise ValueError(f"OHLC join missing: {row.symbol} {row.month}")
        merged["data_role"] = "DEVELOPMENT"
        frames.append(merged)

    hourly = pd.concat(frames, ignore_index=True)
    hourly = hourly.sort_values(["symbol", "timestamp"], kind="mergesort").reset_index(drop=True)
    if hourly.missing_any.astype(bool).any():
        raise ValueError("fixed development axis contains missing_any rows")
    if hourly.duplicated(["symbol", "timestamp"]).any():
        raise ValueError("duplicate primary key in qualified release")
    hourly["date"] = hourly.timestamp.dt.floor("D")
    required_hours = int(release_contract["required_hours_per_day"])
    hourly_counts = hourly.groupby(["symbol", "date"], sort=True).size()
    if not hourly_counts.eq(required_hours).all():
        invalid = hourly_counts[~hourly_counts.eq(required_hours)].head().to_dict()
        raise ValueError(f"incomplete UTC days in fixed axis: {invalid}")

    daily_rows: list[dict[str, Any]] = []
    for (symbol, date), block in hourly.groupby(["symbol", "date"], sort=True):
        block = block.sort_values("timestamp", kind="mergesort")
        quantity = float(block.quantity.sum())
        notional = float(block.notional.sum())
        signed_flow = float(block.signed_aggressor_notional.sum())
        daily_rows.append(
            {
                "date": date,
                "symbol": symbol,
                "data_role": "DEVELOPMENT",
                "month": date.strftime("%Y-%m"),
                "open": float(block.open_price.iloc[0]),
                "high": float(block.high_price.max()),
                "low": float(block.low_price.min()),
                "close": float(block.close_price.iloc[-1]),
                "vwap": notional / quantity if quantity > 0 else np.nan,
                "volume": quantity,
                "notional": notional,
                "trade_count": int(block.trade_count.sum()),
                "signed_flow": signed_flow,
                "flow_imbalance": signed_flow / notional if notional > 0 else np.nan,
                "observable_time": date + pd.Timedelta(days=1),
                "maturity": date + pd.Timedelta(days=1),
                "hour_coverage": len(block),
            }
        )
    daily = pd.DataFrame(daily_rows).sort_values(["date", "symbol"], kind="mergesort").reset_index(drop=True)
    if daily.isna().any().any():
        bad = daily.columns[daily.isna().any()].tolist()
        raise ValueError(f"fixed development daily panel contains NaN: {bad}")
    expected_daily = len(selected_symbols) * daily.date.nunique()
    if len(daily) != expected_daily or daily.symbol.nunique() != len(selected_symbols):
        raise ValueError("fixed daily asset axis drift")
    by_symbol = daily.sort_values(["symbol", "date"], kind="mergesort").groupby("symbol", sort=False)
    daily["return_1d"] = by_symbol.close.pct_change(fill_method=None)
    daily["label_1d_delayed"] = by_symbol.close.shift(-2) / by_symbol.close.shift(-1) - 1.0
    daily["label_observable_time"] = daily.date + pd.Timedelta(days=3)

    evidence = ReleaseEvidence(
        release_id=release_contract["release_id"],
        content_sha256=release_contract["content_sha256"],
        role="DEVELOPMENT",
        months=selected_months,
        symbols=selected_symbols,
        coordinate_count=len(coordinates),
        source_bundle_sha256=canonical_sha256(source_hashes),
        release_bundle_sha256=canonical_sha256(output_hashes),
        qualification_bundle_sha256=qualification_bundle,
        qualification_index_mismatches=qualification_mismatches,
        first_timestamp=str(hourly.timestamp.min()),
        last_timestamp=str(hourly.timestamp.max()),
        row_count_hourly=len(hourly),
        row_count_daily=len(daily),
        no_fill=True,
        source_and_release_hashes_verified=verify_hashes,
    )
    return daily, evidence
