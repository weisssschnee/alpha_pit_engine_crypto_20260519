"""Train-only 2023H2 plus 2024 Crypto panel adapter and qualification.

The adapter deliberately exposes only rows before 2025-01-01.  It reconciles
the two physical schemas without changing the current field authorization.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping, Sequence

import numpy as np
import pandas as pd
import pyarrow.parquet as pq


PRE2024_ALIASES: dict[str, str] = {
    "open": "trade_open",
    "high": "trade_high",
    "low": "trade_low",
    "close": "trade_close",
    "volume": "trade_volume",
    "quote_volume": "trade_quote_volume",
    "ret_1h": "trade_return_1h",
    "forward_only_flag": "is_forward_only",
    "historical_backfill_allowed": "is_historical_backfill",
    "funding_time": "last_funding_time",
    "open_interest_change_1h": "open_interest_last_change_1h",
    "open_interest_change_4h": "open_interest_last_change_4h",
    "open_interest_change_24h": "open_interest_last_change_24h",
    "open_interest_zscore_168h": "open_interest_last_zscore_168h",
    "open_interest_value_change_1h": "open_interest_value_last_change_1h",
    "open_interest_value_change_4h": "open_interest_value_last_change_4h",
    "open_interest_value_change_24h": "open_interest_value_last_change_24h",
    "open_interest_value_zscore_168h": "open_interest_value_last_zscore_168h",
    "premium_index_bps": "premium_close_bps",
}

AGE_FIELDS = frozenset(
    {
        "active_universe_size",
        "age_bucket",
        "age_percentile_active_universe",
        "first_observed_timestamp",
        "history_length_hours",
        "listing_age_days",
        "listing_age_hours",
        "listing_age_source",
        "log1p_listing_age_days",
        "sqrt_listing_age_days",
    }
)

DERIVED_DEPENDENCIES: dict[str, tuple[str, ...]] = {
    "account_position_divergence": (
        "top_long_short_position_ratio_last",
        "top_long_short_account_ratio_last",
    ),
    "top_global_account_divergence": (
        "top_long_short_account_ratio_last",
        "global_long_short_account_ratio_last",
    ),
    "mark_trade_basis_bps": ("mark_close", "trade_close"),
    "open_interest_last_change_1h": ("open_interest_last",),
    "open_interest_last_change_4h": ("open_interest_last",),
    "open_interest_last_change_24h": ("open_interest_last",),
    "open_interest_value_last_change_1h": ("open_interest_value_last",),
    "open_interest_value_last_change_4h": ("open_interest_value_last",),
    "open_interest_value_last_change_24h": ("open_interest_value_last",),
}

FORBIDDEN_SOURCE_FEATURES = frozenset(
    {
        "forward_trade_return_1h",
        "recommended_stress_execution_time",
        "execution_time",
        "is_recent_patch",
    }
)

IDENTITY_COLUMNS = ("symbol", "timestamp", "feature_available_time", "source_segment")


def _bool(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes"}


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _payload_sha(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest().upper()


def _git_sha(repo_root: Path) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=repo_root, text=True
    ).strip().lower()


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True, default=str))
        handle.write("\n")


def _read_parquet_file(path: Path, columns: Iterable[str]) -> pd.DataFrame:
    parquet = pq.ParquetFile(path)
    available = set(parquet.schema_arrow.names)
    selected = [column for column in dict.fromkeys(columns) if column in available]
    if not selected:
        return pd.DataFrame()
    return parquet.read(columns=selected).to_pandas()


def _timestamp(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce", utc=True)


def _apply_derivations(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    if {"mark_close", "trade_close"}.issubset(out.columns):
        denominator = pd.to_numeric(out["trade_close"], errors="coerce").replace(0, np.nan)
        derived = (
            pd.to_numeric(out["mark_close"], errors="coerce") / denominator - 1.0
        ) * 10000.0
        if "mark_trade_basis_bps" in out.columns:
            out["mark_trade_basis_bps"] = pd.to_numeric(
                out["mark_trade_basis_bps"], errors="coerce"
            ).fillna(derived)
        else:
            out["mark_trade_basis_bps"] = derived
    if {
        "top_long_short_position_ratio_last",
        "top_long_short_account_ratio_last",
    }.issubset(out.columns):
        out["account_position_divergence"] = (
            pd.to_numeric(out["top_long_short_position_ratio_last"], errors="coerce")
            - pd.to_numeric(out["top_long_short_account_ratio_last"], errors="coerce")
        )
    if {
        "top_long_short_account_ratio_last",
        "global_long_short_account_ratio_last",
    }.issubset(out.columns):
        out["top_global_account_divergence"] = (
            pd.to_numeric(out["top_long_short_account_ratio_last"], errors="coerce")
            - pd.to_numeric(out["global_long_short_account_ratio_last"], errors="coerce")
        )
    return out


def _apply_temporal_derivations(
    frame: pd.DataFrame, requested: Sequence[str]
) -> pd.DataFrame:
    """Rebuild lagged OI changes identically across both physical segments."""

    out = frame.copy()
    timestamps = _timestamp(out["timestamp"])
    sources = {
        "open_interest_last": "open_interest_last_change_{}h",
        "open_interest_value_last": "open_interest_value_last_change_{}h",
    }
    requested_set = set(requested)
    for source, template in sources.items():
        if source not in out:
            continue
        values = pd.to_numeric(out[source], errors="coerce")
        for horizon in (1, 4, 24):
            target = template.format(horizon)
            if target not in requested_set:
                continue
            lagged = values.shift(horizon)
            lagged_time = timestamps.shift(horizon)
            contiguous = timestamps.sub(lagged_time).eq(pd.Timedelta(hours=horizon))
            denominator = lagged.replace(0.0, np.nan)
            out[target] = ((values / denominator) - 1.0).where(contiguous)
    return out


def _required_physical_fields(fields: Sequence[str]) -> set[str]:
    required = set(fields) | {"symbol", "timestamp", "feature_available_time"}
    for name in fields:
        required.update(DERIVED_DEPENDENCIES.get(name, ()))
    return required - set(DERIVED_DEPENDENCIES)


def _pre2024_raw_fields(normalized_fields: Iterable[str]) -> set[str]:
    reverse = {normalized: raw for raw, normalized in PRE2024_ALIASES.items()}
    return {reverse.get(field, field) for field in normalized_fields}


def _normalise_frame(
    frame: pd.DataFrame,
    *,
    source_segment: str,
    start: pd.Timestamp,
    end: pd.Timestamp,
) -> pd.DataFrame:
    if frame.empty:
        return frame
    out = frame.rename(columns=PRE2024_ALIASES).copy()
    if "timestamp" not in out.columns:
        raise ValueError(f"{source_segment} has no timestamp")
    out["timestamp"] = _timestamp(out["timestamp"])
    if "feature_available_time" in out.columns:
        out["feature_available_time"] = _timestamp(out["feature_available_time"])
    out = out.loc[out["timestamp"].ge(start) & out["timestamp"].lt(end)].copy()
    out["source_segment"] = source_segment
    out = _apply_derivations(out)
    out = out.drop(columns=[c for c in FORBIDDEN_SOURCE_FEATURES if c in out], errors="ignore")
    return out


def _source_roots(config: Mapping[str, Any]) -> dict[str, Path]:
    data_root = Path(config["data_root"])
    return {name: data_root / relative for name, relative in config["sources"].items()}


def load_symbol_train(
    config: Mapping[str, Any],
    symbol: str,
    *,
    fields: Sequence[str] | None = None,
) -> pd.DataFrame:
    """Load one symbol while returning train rows and current-authorized fields only."""

    requested = tuple(fields or config["runtime_fields"])
    physical = _required_physical_fields(requested)
    roots = _source_roots(config)
    start = pd.Timestamp(config["train_start_utc"])
    end = pd.Timestamp(config["train_end_exclusive_utc"])
    frames: list[pd.DataFrame] = []

    pre_parts = sorted((roots["pre2024_complete"] / f"symbol={symbol}").glob("month=*/part.parquet"))
    if pre_parts:
        raw_fields = _pre2024_raw_fields(physical)
        pre_frames = [_read_parquet_file(path, raw_fields) for path in pre_parts]
        pre = pd.concat([part for part in pre_frames if not part.empty], ignore_index=True, sort=False)
        wanted_age = set(requested) & AGE_FIELDS
        if wanted_age:
            age_parts = sorted((roots["pre2024_age"] / f"symbol={symbol}").glob("month=*/part.parquet"))
            age_frames = [
                _read_parquet_file(path, {"symbol", "timestamp"} | wanted_age)
                for path in age_parts
            ]
            age = pd.concat([part for part in age_frames if not part.empty], ignore_index=True, sort=False)
            if not age.empty:
                age["timestamp"] = _timestamp(age["timestamp"])
                pre["timestamp"] = _timestamp(pre["timestamp"])
                age = age.drop_duplicates(["symbol", "timestamp"])
                pre = pre.merge(age, on=["symbol", "timestamp"], how="left", validate="one_to_one")
        frames.append(
            _normalise_frame(
                pre,
                source_segment="PRE2024_COMPLETE_REPLAY",
                start=start,
                end=min(end, pd.Timestamp("2024-01-01T00:00:00Z")),
            )
        )

    top_path = roots["top498_v3"] / f"symbol={symbol}" / "part.parquet"
    if top_path.is_file():
        top = _read_parquet_file(top_path, physical | {"is_recent_patch"})
        frames.append(
            _normalise_frame(
                top,
                source_segment="TOP498_V3_TRAIN_2024",
                start=max(start, pd.Timestamp("2024-01-01T00:00:00Z")),
                end=end,
            )
        )

    usable = [frame for frame in frames if not frame.empty]
    if not usable:
        return pd.DataFrame(columns=[*IDENTITY_COLUMNS, *requested])
    out = pd.concat(usable, ignore_index=True, sort=False)
    out = out.sort_values(["symbol", "timestamp", "source_segment"])
    duplicate_count = int(out.duplicated(["symbol", "timestamp"]).sum())
    if duplicate_count:
        raise ValueError(f"duplicate train rows for {symbol}: {duplicate_count}")
    if out["timestamp"].lt(start).any() or out["timestamp"].ge(end).any():
        raise PermissionError("train loader returned a row outside the frozen train interval")
    forbidden = FORBIDDEN_SOURCE_FEATURES & set(out.columns)
    if forbidden:
        raise PermissionError(f"forbidden source features escaped loader: {sorted(forbidden)}")
    out = _apply_temporal_derivations(out, requested)
    columns = [column for column in (*IDENTITY_COLUMNS, *requested) if column in out]
    return out.loc[:, columns].reset_index(drop=True)


def iter_train_symbols(
    config: Mapping[str, Any], *, fields: Sequence[str] | None = None
) -> Iterator[tuple[str, pd.DataFrame]]:
    roots = _source_roots(config)
    symbols = {
        path.name.split("=", 1)[1]
        for root in (roots["pre2024_complete"], roots["top498_v3"])
        for path in root.glob("symbol=*")
        if path.is_dir()
    }
    for symbol in sorted(symbols):
        frame = load_symbol_train(config, symbol, fields=fields)
        if not frame.empty:
            yield symbol, frame


@dataclass
class RunningStats:
    total: int = 0
    valid: int = 0
    mean: float = 0.0
    m2: float = 0.0
    minimum: float | None = None
    maximum: float | None = None
    varying_assets: set[str] = field(default_factory=set)

    def update(self, values: pd.Series, symbol: str) -> None:
        numeric = pd.to_numeric(values, errors="coerce").replace([np.inf, -np.inf], np.nan)
        self.total += int(numeric.size)
        clean = numeric.dropna().astype(float).to_numpy()
        if not clean.size:
            return
        batch_n = int(clean.size)
        batch_mean = float(clean.mean())
        batch_m2 = float(np.square(clean - batch_mean).sum())
        if self.valid == 0:
            self.mean = batch_mean
            self.m2 = batch_m2
        else:
            delta = batch_mean - self.mean
            combined = self.valid + batch_n
            self.m2 += batch_m2 + delta * delta * self.valid * batch_n / combined
            self.mean += delta * batch_n / combined
        self.valid += batch_n
        current_min = float(clean.min())
        current_max = float(clean.max())
        self.minimum = current_min if self.minimum is None else min(self.minimum, current_min)
        self.maximum = current_max if self.maximum is None else max(self.maximum, current_max)
        if pd.Series(clean).nunique(dropna=True) > 1:
            self.varying_assets.add(symbol)

    def payload(self) -> dict[str, Any]:
        variance = self.m2 / max(1, self.valid - 1) if self.valid > 1 else 0.0
        return {
            "rows": self.total,
            "valid_rows": self.valid,
            "non_null_ratio": self.valid / max(1, self.total),
            "mean": self.mean if self.valid else None,
            "variance": variance,
            "minimum": self.minimum,
            "maximum": self.maximum,
            "assets_with_time_variation": len(self.varying_assets),
        }


def _schema_columns(files: Iterable[Path]) -> tuple[set[str], dict[str, int]]:
    columns: set[str] = set()
    variants: dict[str, int] = defaultdict(int)
    for path in files:
        schema = pq.ParquetFile(path).schema_arrow
        columns.update(schema.names)
        variants[str(schema)] += 1
    return columns, dict(variants)


def _normalised_pre_columns(complete: set[str], age: set[str]) -> set[str]:
    return {PRE2024_ALIASES.get(column, column) for column in complete | age}


def _registry_reconciliation(
    repo_root: Path,
    config: Mapping[str, Any],
    *,
    pre_columns: set[str],
    top_columns: set[str],
) -> pd.DataFrame:
    registry = config["registries"]
    inventory = pd.read_csv(repo_root / registry["inventory"], keep_default_na=False)
    ontology = pd.read_csv(repo_root / registry["ontology"], keep_default_na=False)
    approval = pd.read_csv(repo_root / registry["approval"], keep_default_na=False)
    runtime = pd.read_csv(repo_root / registry["current_runtime"], keep_default_na=False)
    ontology_map = ontology.set_index("field_name").to_dict("index")
    approval_map = approval.set_index("field").to_dict("index")
    runtime_map = runtime.set_index("field_name").to_dict("index")
    inventory_map = inventory.set_index("field_id").to_dict("index")
    identities = sorted(set(inventory["field_id"]) | pre_columns | top_columns | set(DERIVED_DEPENDENCIES))
    rows: list[dict[str, Any]] = []
    for name in identities:
        inv = inventory_map.get(name, {})
        run = runtime_map.get(name, {})
        app = approval_map.get(name, {})
        ont = ontology_map.get(name, {})
        dependencies = tuple(DERIVED_DEPENDENCIES.get(name, ()))
        common_physical = name in pre_columns and name in top_columns
        dependency_materializable = bool(dependencies) and all(
            dependency in pre_columns and dependency in top_columns
            for dependency in dependencies
        )
        materializable = common_physical or dependency_materializable
        current_runtime = name in runtime_map or _bool(inv.get("runtime_loaded", False))
        if current_runtime and materializable:
            activation = "CURRENT_RUNTIME_18M_ADMITTED"
        elif name in inventory_map:
            activation = "REGISTERED_NOT_CURRENT_RUNTIME"
        else:
            activation = "PHYSICAL_NOT_REGISTERED"
        rows.append(
            {
                "field_id": name,
                "pre2024_physical": name in pre_columns,
                "top498_2024_physical": name in top_columns,
                "common_physical": common_physical,
                "derived_dependencies": ";".join(dependencies),
                "dependency_materializable_18m": dependency_materializable,
                "materializable_18m": materializable,
                "inventory_registered": name in inventory_map,
                "registry_status": inv.get("registry_status", ""),
                "inventory_search_allowed": inv.get("search_allowed", ""),
                "ontology_registered": name in ontology_map,
                "ontology_allowed_for_search": ont.get("allowed_for_search", ""),
                "approval_registered": name in approval_map,
                "source_input_approval": app.get("source_input_approval", ""),
                "system_input_role": app.get("system_input_role", ""),
                "input_route": app.get("input_route", ""),
                "current_runtime": current_runtime,
                "runtime_dependencies": run.get("dependencies", ""),
                "activation_18m": activation,
            }
        )
    return pd.DataFrame(rows)


def _month_ord(value: str) -> int:
    return int(value[:4]) * 12 + int(value[5:7]) - 1


def _longest_contiguous_months(months: Iterable[str]) -> int:
    values = sorted({_month_ord(value) for value in months})
    best = current = 0
    previous: int | None = None
    for value in values:
        current = current + 1 if previous is not None and value == previous + 1 else 1
        best = max(best, current)
        previous = value
    return best


def _report_text(
    decision: Mapping[str, Any], reconciliation: pd.DataFrame, quality: pd.DataFrame
) -> str:
    coverage = decision["coverage"]
    supersession = decision["supersession"]
    current = reconciliation[reconciliation["current_runtime"]]
    return f"""# Crypto Train Surface 18M Qualification

## Decision

`{decision['decision']}`

The train surface is now 2023-07-01 through 2024-12-31 only.  No 2025+
row is returned, no formal search was run, and no economic claim is made.

## Corrected train facts

- rows: {coverage['rows']:,}
- unique hourly timestamps: {coverage['unique_timestamps']:,}
- assets observed: {coverage['assets']}
- assets with any 2024 rows: {coverage['assets_any_2024']}
- assets present in every 2024 month: {coverage['assets_present_all_2024_months']}
- assets with all 8,784 hours in 2024: {coverage['assets_full_8784h_2024']}
- assets spanning both 2023H2 and 2024: {coverage['assets_spanning_pre2024_and_2024']}
- monthly active asset range: {coverage['monthly_active_assets_min']} to {coverage['monthly_active_assets_max']}
- continuous months: {coverage['continuous_months']}
- current Git runtime fields materializable: {int(current['materializable_18m'].sum())}/{len(current)}
- source content bundle SHA256: `{decision['source_content_bundle_sha256']}`

## Git field reconciliation

- inventory identities checked: {decision['field_reconciliation']['inventory_identities']:,}
- physical normalized fields common to both periods: {decision['field_reconciliation']['common_physical_fields']}
- common physical fields registered in the inventory: {decision['field_reconciliation']['common_registered_fields']}
- current runtime fields admitted: {decision['field_reconciliation']['current_runtime_admitted']}
- physical fields are not automatically search-authorized; the current 10-field runtime contract remains the activation boundary.

## Runtime field quality

{quality[['field_id', 'non_null_ratio', 'variance', 'assets_with_time_variation', 'gate_pass']].to_markdown(index=False)}

## Supersession scope

- superseded: {', '.join(supersession['superseded_findings'])}
- remains unresolved: {', '.join(supersession['remaining_findings'])}
- the 96-asset A7EFF2 numeric cache is classified as a cache scope, not the physical 2024 panel limit.

## Boundaries

- observed-archive/current-seed universe only; omitted delisted contracts remain possible.
- native aggTrades order-field history is still only the smaller historical release.
- validation, test, recent, May stress, challenge, and forward remain sealed.
- no candidate promotion and no cross-sprint adaptive memory.
"""


def build_qualification(
    repo_root: Path, *, config_path: Path, hash_source_files: bool = True
) -> dict[str, Any]:
    config = _read_json(config_path)
    if config["boundaries"]["sealed_reads_allowed"]:
        raise ValueError("sealed reads must remain disabled")
    if pd.Timestamp(config["train_end_exclusive_utc"]) > pd.Timestamp("2025-01-01T00:00:00Z"):
        raise PermissionError("train contract crosses the sealed boundary")
    roots = _source_roots(config)
    pre_files = sorted(roots["pre2024_complete"].glob("symbol=*/month=*/part.parquet"))
    age_files = sorted(roots["pre2024_age"].glob("symbol=*/month=*/part.parquet"))
    top_files_all = sorted(roots["top498_v3"].glob("symbol=*/part.parquet"))
    if not pre_files or not age_files or not top_files_all:
        raise FileNotFoundError("one or more train source releases are absent")

    pre_raw_columns, pre_variants = _schema_columns(pre_files)
    age_raw_columns, age_variants = _schema_columns(age_files)
    top_raw_columns, top_variants = _schema_columns(top_files_all)
    pre_columns = _normalised_pre_columns(pre_raw_columns, age_raw_columns)
    top_columns = set(top_raw_columns)
    reconciliation = _registry_reconciliation(
        repo_root, config, pre_columns=pre_columns, top_columns=top_columns
    )

    runtime_root = repo_root / config["outputs"]["runtime_root"]
    runtime_root.mkdir(parents=True, exist_ok=True)
    reconciliation_path = runtime_root / "CRYPTO_TRAIN_FIELD_RECONCILIATION.csv"
    reconciliation.to_csv(reconciliation_path, index=False, lineterminator="\n")

    runtime_fields = tuple(config["runtime_fields"])
    stats = {name: RunningStats() for name in runtime_fields}
    label_stats = {f"label_return_{h}h": RunningStats() for h in config["target_horizons_hours"]}
    month_assets: dict[str, set[str]] = defaultdict(set)
    month_rows: dict[str, int] = defaultdict(int)
    timestamp_union: set[pd.Timestamp] = set()
    assets: set[str] = set()
    total_rows = 0
    duplicates = 0
    availability_lags: list[float] = []
    segment_rows: dict[str, int] = defaultdict(int)
    symbol_2024_rows: dict[str, int] = defaultdict(int)
    for symbol, frame in iter_train_symbols(config, fields=runtime_fields):
        assets.add(symbol)
        total_rows += int(frame.shape[0])
        for segment, count in frame["source_segment"].value_counts().items():
            segment_rows[str(segment)] += int(count)
        duplicates += int(frame.duplicated(["symbol", "timestamp"]).sum())
        timestamp_union.update(frame["timestamp"].tolist())
        month_values = frame["timestamp"].dt.strftime("%Y-%m")
        symbol_2024_rows[symbol] += int(month_values.str.startswith("2024-").sum())
        for month, count in month_values.value_counts().items():
            month_assets[str(month)].add(symbol)
            month_rows[str(month)] += int(count)
        if "feature_available_time" in frame:
            lag = (
                _timestamp(frame["feature_available_time"]) - _timestamp(frame["timestamp"])
            ).dt.total_seconds() / 3600.0
            availability_lags.extend(lag.dropna().astype(float).tolist())
        for name in runtime_fields:
            stats[name].update(frame.get(name, pd.Series(np.nan, index=frame.index)), symbol)
        close = pd.to_numeric(frame["trade_close"], errors="coerce")
        timestamps = _timestamp(frame["timestamp"])
        for horizon in config["target_horizons_hours"]:
            future_close = close.shift(-horizon)
            future_time = timestamps.shift(-horizon)
            continuous = future_time.sub(timestamps).eq(pd.Timedelta(hours=horizon))
            label = (future_close / close - 1.0).where(continuous)
            label_stats[f"label_return_{horizon}h"].update(label, symbol)

    quality_rows = []
    threshold = float(config["data_adequacy"]["minimum_runtime_field_non_null_ratio"])
    for name, accumulator in stats.items():
        payload = accumulator.payload()
        payload.update(
            field_id=name,
            gate_pass=payload["non_null_ratio"] >= threshold
            and float(payload["variance"] or 0.0) > 0.0,
        )
        quality_rows.append(payload)
    quality = pd.DataFrame(quality_rows)[
        [
            "field_id",
            "rows",
            "valid_rows",
            "non_null_ratio",
            "mean",
            "variance",
            "minimum",
            "maximum",
            "assets_with_time_variation",
            "gate_pass",
        ]
    ]
    quality_path = runtime_root / "CRYPTO_TRAIN_RUNTIME_FIELD_QUALITY.csv"
    quality.to_csv(quality_path, index=False, lineterminator="\n")

    label_quality = pd.DataFrame(
        [dict(field_id=name, **accumulator.payload()) for name, accumulator in label_stats.items()]
    )
    label_quality_path = runtime_root / "CRYPTO_TRAIN_LABEL_SUPPORT.csv"
    label_quality.to_csv(label_quality_path, index=False, lineterminator="\n")

    coverage = pd.DataFrame(
        [
            {
                "month": month,
                "rows": month_rows[month],
                "active_assets": len(month_assets[month]),
                "role": "TRAIN",
            }
            for month in sorted(month_rows)
        ]
    )
    coverage_path = runtime_root / "CRYPTO_TRAIN_MONTH_COVERAGE.csv"
    coverage.to_csv(coverage_path, index=False, lineterminator="\n")

    source_rows: list[dict[str, Any]] = []
    source_manifest_path = runtime_root / "CRYPTO_TRAIN_SOURCE_CONTENT_MANIFEST.csv"
    cached_hashes: dict[tuple[str, str, int], str] = {}
    if hash_source_files and source_manifest_path.is_file():
        cached = pd.read_csv(source_manifest_path, keep_default_na=False)
        for row in cached.to_dict("records"):
            cached_hashes[(str(row["source"]), str(row["path"]), int(row["bytes"]))] = str(
                row["sha256"]
            )
    relevant_top_files: list[Path] = []
    for path in top_files_all:
        parquet = pq.ParquetFile(path)
        index = parquet.schema_arrow.names.index("timestamp")
        stats_meta = parquet.metadata.row_group(0).column(index).statistics
        if stats_meta and pd.Timestamp(stats_meta.min, tz="UTC") < pd.Timestamp("2025-01-01T00:00:00Z"):
            relevant_top_files.append(path)
    source_groups = (
        ("PRE2024_COMPLETE_REPLAY", pre_files),
        ("PRE2024_AGE", age_files),
        ("TOP498_V3_TRAIN_SOURCE", relevant_top_files),
    )
    data_root = Path(config["data_root"])
    for source_name, files in source_groups:
        for path in files:
            parquet = pq.ParquetFile(path)
            names = parquet.schema_arrow.names
            timestamp_min = timestamp_max = ""
            if "timestamp" in names:
                index = names.index("timestamp")
                metadata = parquet.metadata.row_group(0).column(index).statistics
                if metadata and metadata.has_min_max:
                    timestamp_min = str(metadata.min)
                    timestamp_max = str(metadata.max)
            source_rows.append(
                {
                    "source": source_name,
                    "path": path.relative_to(data_root).as_posix(),
                    "bytes": path.stat().st_size,
                    "rows": parquet.metadata.num_rows,
                    "timestamp_min": timestamp_min,
                    "timestamp_max": timestamp_max,
                    "sha256": (
                        cached_hashes.get(
                            (source_name, path.relative_to(data_root).as_posix(), path.stat().st_size)
                        )
                        or _sha256_file(path)
                    )
                    if hash_source_files
                    else "NOT_COMPUTED",
                }
            )
    source_manifest = pd.DataFrame(source_rows)
    source_manifest.to_csv(source_manifest_path, index=False, lineterminator="\n")
    source_bundle_sha = _payload_sha(source_rows)

    months = sorted(month_rows)
    gate = config["data_adequacy"]
    label_minimum = int(gate["minimum_label_observations"])
    checks = {
        "continuous_months": _longest_contiguous_months(months)
        >= int(gate["minimum_continuous_months"]),
        "assets": len(assets) >= int(gate["minimum_assets"]),
        "monthly_active_assets": min(map(len, month_assets.values()))
        >= int(gate["minimum_monthly_active_assets"]),
        "runtime_fields": bool(quality["gate_pass"].all()),
        "label_support": bool((label_quality["valid_rows"] >= label_minimum).all()),
        "independent_month_blocks": len(months)
        >= int(gate["minimum_independent_month_blocks"]),
        "duplicate_rows_zero": duplicates == 0,
        "availability_not_before_timestamp": min(availability_lags, default=0.0) >= 0.0,
        "sealed_rows_returned_zero": max(timestamp_union) < pd.Timestamp("2025-01-01T00:00:00Z"),
    }
    decision_code = (
        "PASS_CRYPTO_TRAIN_SURFACE_18M_DEVELOPMENT_READY_WITH_SCOPE_LIMITS"
        if all(checks.values())
        else "HOLD_CRYPTO_TRAIN_SURFACE_18M_DATA_QUALITY_GAP"
    )
    common = reconciliation[reconciliation["common_physical"]]
    current = reconciliation[reconciliation["current_runtime"]]
    months_2024 = [month for month in months if month.startswith("2024-")]
    months_pre2024 = [month for month in months if month.startswith("2023-")]
    assets_2024 = set().union(*(month_assets[month] for month in months_2024))
    assets_pre2024 = set().union(*(month_assets[month] for month in months_pre2024))
    assets_present_all_2024_months = set.intersection(
        *(month_assets[month] for month in months_2024)
    )
    assets_full_8784h_2024 = {
        symbol for symbol, rows in symbol_2024_rows.items() if rows == 8784
    }
    assets_present_all_18m = set.intersection(*(month_assets[month] for month in months))
    decision = {
        "schema_version": 1,
        "surface_id": config["surface_id"],
        "producer_source_sha": _git_sha(repo_root),
        "decision": decision_code,
        "coverage": {
            "start_utc": config["train_start_utc"],
            "end_exclusive_utc": config["train_end_exclusive_utc"],
            "rows": total_rows,
            "unique_timestamps": len(timestamp_union),
            "assets": len(assets),
            "continuous_months": _longest_contiguous_months(months),
            "monthly_active_assets_min": min(map(len, month_assets.values())),
            "monthly_active_assets_max": max(map(len, month_assets.values())),
            "duplicates": duplicates,
            "segment_rows": dict(sorted(segment_rows.items())),
            "assets_any_2024": len(assets_2024),
            "assets_present_all_2024_months": len(assets_present_all_2024_months),
            "assets_full_8784h_2024": len(assets_full_8784h_2024),
            "assets_spanning_pre2024_and_2024": len(assets_pre2024 & assets_2024),
            "assets_present_all_18_months": len(assets_present_all_18m),
        },
        "field_reconciliation": {
            "inventory_identities": int(reconciliation["inventory_registered"].sum()),
            "common_physical_fields": int(common.shape[0]),
            "common_registered_fields": int(common["inventory_registered"].sum()),
            "current_runtime_fields": int(current.shape[0]),
            "current_runtime_admitted": int(current["materializable_18m"].sum()),
        },
        "data_adequacy_checks": checks,
        "source_content_bundle_sha256": source_bundle_sha,
        "source_schema_variants": {
            "pre2024_complete": len(pre_variants),
            "pre2024_age": len(age_variants),
            "top498_v3": len(top_variants),
        },
        "source_timing": {
            "feature_available_lag_hours_min": min(availability_lags, default=None),
            "feature_available_lag_hours_max": max(availability_lags, default=None),
        },
        "supersession": {
            "superseded_findings": [
                "TIME_HISTORY_TOO_SHORT_FOR_OBSERVED_ARCHIVE_KLINE_DERIVATIVES_TRAIN_SURFACE",
                "A7EFF2_96_ASSETS_AS_PHYSICAL_PANEL_LIMIT",
            ],
            "remaining_findings": [
                "SURVIVORSHIP_OR_ELIGIBILITY_UNRESOLVED",
                "ORDER_FIELD_COVERAGE_FRAGMENTED",
                "EXPLICIT_CORE_AGGTRADES_TIME_HISTORY_TOO_SHORT",
                "COMPOSITIONAL_GRAMMAR_BOTTLENECK_NO_NEW_ECONOMIC_TEST",
            ],
        },
        "authorization": {
            "train_loader": True,
            "large_search": False,
            "formal_performance_search": False,
            "sealed_evaluation": False,
            "candidate_promotion": False,
            "economic_claim": False,
        },
    }
    decision_path = runtime_root / "CRYPTO_TRAIN_DATA_ADEQUACY.json"
    _write_json(decision_path, decision)

    report_path = repo_root / config["outputs"]["report"]
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        _report_text(decision, reconciliation, quality), encoding="utf-8", newline="\n"
    )

    artifact_paths = [
        config_path,
        repo_root / "alphafactory_crypto" / "train_surface.py",
        repo_root / "scripts" / "crypto_train_surface_18m.py",
        reconciliation_path,
        quality_path,
        label_quality_path,
        coverage_path,
        source_manifest_path,
        decision_path,
        report_path,
    ]
    artifacts = [
        {
            "path": path.relative_to(repo_root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": _sha256_file(path),
        }
        for path in sorted(artifact_paths)
    ]
    artifact_manifest = {
        "schema_version": 1,
        "producer_source_sha": _git_sha(repo_root),
        "data_role": "TRAIN_ONLY",
        "sealed_rows_returned": 0,
        "source_content_bundle_sha256": source_bundle_sha,
        "artifacts": artifacts,
        "bundle_sha256": _payload_sha(artifacts),
    }
    manifest_path = runtime_root / "CRYPTO_TRAIN_ARTIFACT_MANIFEST.json"
    _write_json(manifest_path, artifact_manifest)
    return {
        "result": "PASS" if all(checks.values()) else "FAIL",
        "decision": decision_code,
        "rows": total_rows,
        "assets": len(assets),
        "months": len(months),
        "runtime_fields_admitted": int(current["materializable_18m"].sum()),
        "source_content_bundle_sha256": source_bundle_sha,
        "artifact_bundle_sha256": artifact_manifest["bundle_sha256"],
        "sealed_rows_returned": 0,
    }


def check_qualification(repo_root: Path, *, config_path: Path) -> dict[str, Any]:
    config = _read_json(config_path)
    runtime_root = repo_root / config["outputs"]["runtime_root"]
    manifest_path = runtime_root / "CRYPTO_TRAIN_ARTIFACT_MANIFEST.json"
    if not manifest_path.is_file():
        return {"result": "FAIL", "errors": ["missing artifact manifest"]}
    manifest = _read_json(manifest_path)
    errors: list[str] = []
    for record in manifest.get("artifacts", []):
        path = (repo_root / record["path"]).resolve()
        try:
            path.relative_to(repo_root.resolve())
        except ValueError:
            errors.append(f"path_escape:{record['path']}")
            continue
        if not path.is_file():
            errors.append(f"missing:{record['path']}")
        elif path.stat().st_size != record["bytes"] or _sha256_file(path) != record["sha256"]:
            errors.append(f"identity:{record['path']}")
    if _payload_sha(manifest.get("artifacts", [])) != manifest.get("bundle_sha256"):
        errors.append("bundle_sha256")
    decision_path = runtime_root / "CRYPTO_TRAIN_DATA_ADEQUACY.json"
    if decision_path.is_file():
        decision = _read_json(decision_path)
        if not all(decision.get("data_adequacy_checks", {}).values()):
            errors.append("data_adequacy")
        if decision.get("authorization", {}).get("large_search"):
            errors.append("large_search_boundary")
    else:
        errors.append("missing_data_adequacy")
    return {
        "result": "PASS" if not errors else "FAIL",
        "errors": errors,
        "artifact_bundle_sha256": manifest.get("bundle_sha256"),
        "source_content_bundle_sha256": manifest.get("source_content_bundle_sha256"),
        "producer_source_sha": manifest.get("producer_source_sha"),
    }


__all__ = [
    "AGE_FIELDS",
    "DERIVED_DEPENDENCIES",
    "FORBIDDEN_SOURCE_FEATURES",
    "PRE2024_ALIASES",
    "build_qualification",
    "check_qualification",
    "iter_train_symbols",
    "load_symbol_train",
]
