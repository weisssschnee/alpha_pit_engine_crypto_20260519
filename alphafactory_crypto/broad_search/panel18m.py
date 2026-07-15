"""Train-only 18-month panel cache, dynamic eligibility, and field admission.

The cache contains raw observable inputs only.  It is disposable and excluded
from the evidence bundle; derived expressions remain candidate-local and lazy.
"""

from __future__ import annotations

import hashlib
import json
import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from scipy.stats import rankdata

from alphafactory_crypto.train_surface import FORBIDDEN_SOURCE_FEATURES, load_symbol_train

from .expression import FieldContract


IDENTITY_OR_METADATA = frozenset(
    {
        "symbol",
        "timestamp",
        "feature_available_time",
        "source_segment",
        "first_observed_timestamp",
        "last_funding_time",
        "listing_age_source",
        "age_bucket",
        "source_market_funding",
        "source_metrics",
        "is_forward_only",
        "is_historical_backfill",
    }
)

SPARSE_FIELDS = frozenset({"funding_rate"})

FAMILY_OVERRIDES: Mapping[str, str] = {
    "account_position_divergence": "account_position_divergence",
    "top_global_account_divergence": "account_position_divergence",
    "active_universe_size": "cross_asset_market_state",
    "age_percentile_active_universe": "listing_age_context",
    "history_length_hours": "listing_age_context",
    "listing_age_days": "listing_age_context",
    "listing_age_hours": "listing_age_context",
    "log1p_listing_age_days": "listing_age_context",
    "sqrt_listing_age_days": "listing_age_context",
    "funding_rate": "funding",
    "mark_index_basis_bps": "basis_premium",
    "mark_trade_basis_bps": "basis_premium",
    "premium_close": "basis_premium",
    "premium_close_bps": "basis_premium",
    "trade_return_1h": "price_return",
    "trade_quote_volume": "quote_volume_activity",
    "trade_volume": "quote_volume_activity",
    "trade_count": "quote_volume_activity",
    "taker_buy_quote_volume": "quote_volume_activity",
    "taker_buy_volume": "quote_volume_activity",
    "taker_buy_sell_volume_ratio_last": "quote_volume_activity",
    "taker_buy_sell_volume_ratio_mean": "quote_volume_activity",
}


def _bool(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes"}


def _payload_sha(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest().upper()


def infer_family(field_id: str) -> str:
    if field_id in FAMILY_OVERRIDES:
        return FAMILY_OVERRIDES[field_id]
    if field_id.startswith("open_interest_value"):
        return "open_interest_value"
    if field_id.startswith("open_interest"):
        return "open_interest_level_change"
    if field_id.startswith("top_long_short_account") or field_id.startswith(
        "global_long_short_account"
    ):
        return "account_crowding"
    if field_id.startswith("top_long_short_position"):
        return "position_crowding"
    if field_id.startswith(("trade_", "mark_", "index_")) and field_id.endswith(
        ("open", "high", "low", "close")
    ):
        return "price_level"
    if field_id.startswith("premium_"):
        return "basis_premium"
    return "other"


def infer_type_unit(field_id: str) -> tuple[str, str]:
    family = infer_family(field_id)
    if family == "price_level":
        return "PRICE", "quote_per_base"
    if family == "price_return":
        return "RETURN", "dimensionless"
    if family == "quote_volume_activity":
        if "ratio" in field_id:
            return "RATIO", "dimensionless"
        if "count" in field_id:
            return "COUNT", "trades"
        if "quote" in field_id:
            return "NOTIONAL", "quote_asset"
        return "VOLUME", "base_asset"
    if family == "open_interest_value":
        return (
            ("RETURN", "dimensionless")
            if "change" in field_id or "zscore" in field_id
            else ("NOTIONAL", "quote_asset")
        )
    if family == "open_interest_level_change":
        return (
            ("RETURN", "dimensionless")
            if "change" in field_id or "zscore" in field_id
            else ("VOLUME", "contracts")
        )
    if family in {
        "funding",
        "account_crowding",
        "position_crowding",
        "account_position_divergence",
    }:
        return "RATIO", "dimensionless"
    if family == "basis_premium":
        return ("BPS", "bps") if "bps" in field_id or "basis" in field_id else ("RATIO", "dimensionless")
    if family == "listing_age_context":
        if "percentile" in field_id:
            return "UNIT_INTERVAL", "dimensionless"
        return "AGE", "hours" if "hours" in field_id else "days"
    if family == "cross_asset_market_state":
        return "STATE", "assets"
    return "RATIO", "dimensionless"


def economic_role(field_id: str) -> str:
    family = infer_family(field_id)
    return {
        "price_level": "price reference used only through normalized relations",
        "price_return": "observable price response",
        "quote_volume_activity": "trading activity and participation",
        "open_interest_value": "notional open-interest level or change",
        "open_interest_level_change": "contract open-interest level or change",
        "funding": "funding state",
        "basis_premium": "mark/index/trade dislocation state",
        "account_crowding": "account-side crowding state",
        "position_crowding": "position-side crowding state",
        "account_position_divergence": "crowding divergence",
        "listing_age_context": "point-in-time maturity context",
        "cross_asset_market_state": "observable active-universe context",
    }.get(family, "registered observable interaction input")


def candidate_fields(
    repo_root: Path, train_config: Mapping[str, Any]
) -> tuple[list[str], dict[str, dict[str, Any]]]:
    reconciliation = pd.read_csv(
        repo_root / train_config["registries"]["inventory"], keep_default_na=False
    )
    inventory = reconciliation.set_index("field_id").to_dict("index")
    ontology = pd.read_csv(
        repo_root / train_config["registries"]["ontology"], keep_default_na=False
    ).set_index("field_name").to_dict("index")
    approval = pd.read_csv(
        repo_root / train_config["registries"]["approval"], keep_default_na=False
    ).set_index("field").to_dict("index")
    field_reconciliation = pd.read_csv(
        repo_root
        / train_config["outputs"]["runtime_root"]
        / "CRYPTO_TRAIN_FIELD_RECONCILIATION.csv",
        keep_default_na=False,
    )
    fields: list[str] = []
    rows: dict[str, dict[str, Any]] = {}
    for row in field_reconciliation.to_dict("records"):
        field_id = str(row["field_id"])
        if field_id in IDENTITY_OR_METADATA or field_id in FORBIDDEN_SOURCE_FEATURES:
            continue
        if not _bool(row.get("materializable_18m")):
            continue
        if not (_bool(row.get("inventory_registered")) or field_id in train_config["runtime_fields"]):
            # Physical-only lag/change columns are admitted to the audit, never
            # automatically to search.  The field audit decides their status.
            if "change_" not in field_id and field_id not in {
                "active_universe_size",
                "hours_since_funding",
            }:
                continue
        fields.append(field_id)
        rows[field_id] = {
            **inventory.get(field_id, {}),
            **ontology.get(field_id, {}),
            **approval.get(field_id, {}),
            **row,
        }
    return sorted(set(fields)), rows


@dataclass(slots=True)
class _Stats:
    rows: int = 0
    valid: int = 0
    total: float = 0.0
    square: float = 0.0
    minimum: float = math.inf
    maximum: float = -math.inf
    varying_assets: int = 0
    pre_rows: int = 0
    pre_valid: int = 0
    top_rows: int = 0
    top_valid: int = 0

    def update(self, values: np.ndarray, *, source: np.ndarray) -> None:
        finite = np.isfinite(values)
        clean = values[finite].astype(np.float64, copy=False)
        self.rows += int(values.size)
        self.valid += int(clean.size)
        if clean.size:
            self.total += float(clean.sum())
            self.square += float(np.square(clean).sum())
            self.minimum = min(self.minimum, float(clean.min()))
            self.maximum = max(self.maximum, float(clean.max()))
            if clean.size >= 2 and float(np.nanmax(clean) - np.nanmin(clean)) > 1e-12:
                self.varying_assets += 1
        pre = source == 1
        top = source == 2
        self.pre_rows += int(pre.sum())
        self.pre_valid += int((finite & pre).sum())
        self.top_rows += int(top.sum())
        self.top_valid += int((finite & top).sum())

    def payload(self) -> dict[str, Any]:
        mean = self.total / self.valid if self.valid else None
        variance = (
            max(0.0, self.square / self.valid - float(mean) ** 2)
            if self.valid and mean is not None
            else None
        )
        return {
            "rows": self.rows,
            "valid_rows": self.valid,
            "non_null_ratio": self.valid / self.rows if self.rows else 0.0,
            "pre2024_non_null_ratio": self.pre_valid / self.pre_rows if self.pre_rows else 0.0,
            "top2024_non_null_ratio": self.top_valid / self.top_rows if self.top_rows else 0.0,
            "mean": mean,
            "variance": variance,
            "minimum": self.minimum if self.valid else None,
            "maximum": self.maximum if self.valid else None,
            "assets_with_time_variation": self.varying_assets,
        }


@dataclass(frozen=True, slots=True)
class RawPanelStore:
    cache_root: Path
    metadata: Mapping[str, Any]

    @classmethod
    def open(cls, cache_root: Path) -> "RawPanelStore":
        metadata = json.loads((cache_root / "metadata.json").read_text(encoding="utf-8"))
        return cls(cache_root, metadata)

    @property
    def shape(self) -> tuple[int, int]:
        return int(self.metadata["assets"]), int(self.metadata["timestamps"])

    @property
    def symbols(self) -> tuple[str, ...]:
        return tuple(self.metadata["symbol_ids"])

    @property
    def timestamp_ns(self) -> np.ndarray:
        return np.load(self.cache_root / "timestamp_ns.npy", mmap_mode="r")

    def field(self, field_id: str) -> np.ndarray:
        if field_id not in self.metadata["field_ids"]:
            raise KeyError(field_id)
        return np.load(self.cache_root / "fields" / f"{field_id}.npy", mmap_mode="r")

    def base_eligible(self) -> np.ndarray:
        return np.load(self.cache_root / "base_eligible.npy", mmap_mode="r")

    def observed(self) -> np.ndarray:
        return np.load(self.cache_root / "observed.npy", mmap_mode="r")

    def target_return(self, horizon_hours: int) -> np.ndarray:
        return np.load(
            self.cache_root / f"target_return_{int(horizon_hours)}h.npy", mmap_mode="r"
        )

    def block_slice(self, start: str, end: str) -> slice:
        timestamps = self.timestamp_ns
        left = int(np.searchsorted(timestamps, pd.Timestamp(start).value, side="left"))
        right = int(np.searchsorted(timestamps, pd.Timestamp(end).value, side="left"))
        return slice(left, right)


def _open_matrix(path: Path, shape: tuple[int, int], dtype: Any, fill: Any) -> np.memmap:
    path.parent.mkdir(parents=True, exist_ok=True)
    values = np.lib.format.open_memmap(path, mode="w+", dtype=dtype, shape=shape)
    values[:] = fill
    return values


def _write_eligibility_rows(
    writer: pq.ParquetWriter,
    *,
    symbol: str,
    timestamps: pd.Series,
    eligible: np.ndarray,
    required: np.ndarray,
    history: np.ndarray,
    sources: Sequence[str],
    warmup_hours: int,
) -> None:
    reason = np.where(
        ~required,
        "REQUIRED_EXECUTION_INPUT_UNAVAILABLE",
        np.where(
            history < warmup_hours,
            f"MINIMUM_HISTORY_{int(warmup_hours)}H_NOT_MET",
            "ELIGIBLE",
        ),
    )
    table = pa.Table.from_pydict(
        {
            "timestamp": pa.array(timestamps, type=pa.timestamp("ns", tz="UTC")),
            "symbol": [symbol] * len(timestamps),
            "eligible": eligible.astype(bool),
            "ineligibility_reason": reason.tolist(),
            "history_hours": history.astype(np.int32),
            "required_fields_available": required.astype(bool),
            "source_segment": list(sources),
        }
    )
    writer.write_table(table)


def build_raw_panel_cache(
    repo_root: Path,
    *,
    train_config: Mapping[str, Any],
    cache_root: Path,
    eligibility_path: Path,
    source_sha: str,
    warmup_hours: int = 168,
) -> tuple[RawPanelStore, pd.DataFrame, dict[str, dict[str, Any]], dict[str, Any]]:
    """Build a disposable raw memmap cache and the committed eligibility ledger."""

    started = time.perf_counter()
    fields, registry_rows = candidate_fields(repo_root, train_config)
    roots = [Path(train_config["data_root"]) / path for path in train_config["sources"].values()]
    symbols = sorted(
        {
            path.name.split("=", 1)[1]
            for root in roots
            for path in root.glob("symbol=*")
            if path.is_dir()
        }
    )
    start = pd.Timestamp(train_config["train_start_utc"])
    end = pd.Timestamp(train_config["train_end_exclusive_utc"])
    timestamps = pd.date_range(start, end, inclusive="left", freq="1h")
    shape = (len(symbols), len(timestamps))
    cache_root.mkdir(parents=True, exist_ok=True)
    (cache_root / "fields").mkdir(parents=True, exist_ok=True)
    timestamp_ns = _open_matrix(cache_root / "timestamp_ns.npy", (len(timestamps),), np.int64, 0)
    timestamp_ns[:] = timestamps.asi8
    observed = _open_matrix(cache_root / "observed.npy", shape, np.bool_, False)
    eligible_matrix = _open_matrix(cache_root / "base_eligible.npy", shape, np.bool_, False)
    source_matrix = _open_matrix(cache_root / "source_segment.npy", shape, np.int8, 0)
    matrices = {
        field: _open_matrix(cache_root / "fields" / f"{field}.npy", shape, np.float32, np.nan)
        for field in fields
    }
    stats = {field: _Stats() for field in fields}
    read_bytes = 0
    writer: pq.ParquetWriter | None = None
    eligibility_path.parent.mkdir(parents=True, exist_ok=True)
    if eligibility_path.exists():
        eligibility_path.unlink()
    for asset_index, symbol in enumerate(symbols):
        frame = load_symbol_train(train_config, symbol, fields=fields)
        if frame.empty:
            continue
        index = ((frame["timestamp"] - start) / pd.Timedelta(hours=1)).astype(int).to_numpy()
        if (index < 0).any() or (index >= shape[1]).any():
            raise PermissionError("train loader escaped the frozen 18-month coordinates")
        if len(np.unique(index)) != len(index):
            raise ValueError(f"duplicate panel coordinates for {symbol}")
        observed[asset_index, index] = True
        source_codes = np.where(
            frame["source_segment"].eq("PRE2024_COMPLETE_REPLAY").to_numpy(), 1, 2
        ).astype(np.int8)
        source_matrix[asset_index, index] = source_codes
        close = pd.to_numeric(frame.get("trade_close"), errors="coerce").to_numpy(dtype=float)
        available = pd.to_datetime(frame["feature_available_time"], utc=True, errors="coerce")
        lag = (available - frame["timestamp"]).dt.total_seconds().to_numpy(dtype=float) / 3600.0
        required = np.isfinite(close) & np.isfinite(lag) & (lag >= 0.0)
        history = np.zeros(len(index), dtype=np.int32)
        run = 0
        previous = -2
        for local, coordinate in enumerate(index):
            run = run + 1 if coordinate == previous + 1 else 1
            history[local] = run
            previous = int(coordinate)
        eligible = required & (history >= int(warmup_hours))
        eligible_matrix[asset_index, index] = eligible
        for field in fields:
            values = pd.to_numeric(
                frame.get(field, pd.Series(np.nan, index=frame.index)), errors="coerce"
            ).to_numpy(dtype=float)
            matrices[field][asset_index, index] = values.astype(np.float32)
            stats[field].update(values, source=source_codes)
        _write_eligibility_rows(
            writer
            if writer is not None
            else (writer := pq.ParquetWriter(eligibility_path, _eligibility_schema())),
            symbol=symbol,
            timestamps=frame["timestamp"],
            eligible=eligible,
            required=required,
            history=history,
            sources=frame["source_segment"].astype(str).tolist(),
            warmup_hours=int(warmup_hours),
        )
        read_bytes += int(frame.memory_usage(index=True, deep=True).sum())
    if writer is None:
        raise FileNotFoundError("18-month loader returned no observed symbols")
    writer.close()

    close_matrix = matrices["trade_close"]
    for horizon in (1, 4):
        target = _open_matrix(
            cache_root / f"target_return_{horizon}h.npy", shape, np.float32, np.nan
        )
        execution_delay = 2
        offset = execution_delay + horizon
        start_price = np.asarray(close_matrix[:, execution_delay : shape[1] - horizon], dtype=float)
        end_price = np.asarray(close_matrix[:, offset:], dtype=float)
        with np.errstate(divide="ignore", invalid="ignore"):
            target[:, : shape[1] - offset] = np.log(end_price / start_price).astype(np.float32)
        target.flush()

    for matrix in (*matrices.values(), observed, eligible_matrix, source_matrix, timestamp_ns):
        matrix.flush()
    quality = pd.DataFrame(
        [dict(field_id=field, **stats[field].payload()) for field in fields]
    )
    metadata = {
        "schema_version": 1,
        "source_sha": source_sha,
        "surface_id": train_config["surface_id"],
        "start_utc": train_config["train_start_utc"],
        "end_exclusive_utc": train_config["train_end_exclusive_utc"],
        "assets": shape[0],
        "timestamps": shape[1],
        "symbol_ids": symbols,
        "field_ids": fields,
        "warmup_hours": int(warmup_hours),
        "target_formula": "log(close[t+2+h] / close[t+2])",
        "target_horizons_hours": [1, 4],
        "sealed_rows": 0,
        "build_seconds": time.perf_counter() - started,
        "bytes_read_in_memory": read_bytes,
    }
    metadata["identity_sha256"] = _payload_sha(metadata)
    (cache_root / "metadata.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return RawPanelStore.open(cache_root), quality, registry_rows, metadata


def _eligibility_schema() -> pa.Schema:
    return pa.schema(
        [
            ("timestamp", pa.timestamp("ns", tz="UTC")),
            ("symbol", pa.string()),
            ("eligible", pa.bool_()),
            ("ineligibility_reason", pa.string()),
            ("history_hours", pa.int32()),
            ("required_fields_available", pa.bool_()),
            ("source_segment", pa.string()),
        ]
    )


def field_equivalence_audit(
    store: RawPanelStore,
    fields: Sequence[str],
    *,
    sample_size: int = 5000,
    seed: int = 20260716,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    total = store.shape[0] * store.shape[1]
    coordinates = np.sort(rng.choice(total, size=min(sample_size, total), replace=False))
    sampled = {
        field: np.asarray(store.field(field)).reshape(-1)[coordinates].astype(float)
        for field in fields
    }
    rows: list[dict[str, Any]] = []
    for left_index, left_name in enumerate(fields):
        for right_name in fields[left_index + 1 :]:
            left = sampled[left_name]
            right = sampled[right_name]
            finite = np.isfinite(left) & np.isfinite(right)
            overlap = int(finite.sum())
            exact = affine = rank_equivalent = False
            affine_error = rank_correlation = None
            if overlap >= 100:
                x = left[finite]
                y = right[finite]
                scale = max(1.0, float(np.nanmax(np.abs(x))), float(np.nanmax(np.abs(y))))
                exact = bool(np.max(np.abs(x - y)) <= 1e-10 * scale)
                if np.std(x) > 1e-12 and np.std(y) > 1e-12:
                    slope, intercept = np.polyfit(x, y, 1)
                    residual = y - (slope * x + intercept)
                    affine_error = float(np.std(residual) / max(np.std(y), 1e-12))
                    affine = abs(float(slope)) > 1e-12 and affine_error <= 1e-8
                    rank_correlation = float(np.corrcoef(rankdata(x), rankdata(y))[0, 1])
                    rank_equivalent = abs(rank_correlation) >= 0.99999
            rows.append(
                {
                    "left_field": left_name,
                    "right_field": right_name,
                    "overlap": overlap,
                    "exact_equivalent": exact,
                    "affine_equivalent": affine,
                    "affine_relative_error": affine_error,
                    "rank_equivalent": rank_equivalent,
                    "rank_correlation": rank_correlation,
                }
            )
    return pd.DataFrame(rows)


def qualify_fields(
    *,
    quality: pd.DataFrame,
    registry_rows: Mapping[str, Mapping[str, Any]],
    equivalence: pd.DataFrame,
    current_runtime_fields: Iterable[str],
) -> tuple[pd.DataFrame, dict[str, Any], tuple[FieldContract, ...]]:
    current = set(current_runtime_fields)
    rows: list[dict[str, Any]] = []
    for record in quality.to_dict("records"):
        field_id = str(record["field_id"])
        registry = registry_rows.get(field_id, {})
        family = infer_family(field_id)
        value_type, unit = infer_type_unit(field_id)
        sparse = field_id in SPARSE_FIELDS
        lineage_ok = not any(token in field_id.lower() for token in ("forward", "label", "recent", "stress", "execution"))
        if registry:
            lineage_ok = lineage_ok and not _bool(registry.get("uses_future")) and not _bool(
                registry.get("uses_label")
            )
        segment_ok = (
            float(record["pre2024_non_null_ratio"]) > 0.0
            and float(record["top2024_non_null_ratio"]) > 0.0
        )
        coverage_ok = (
            float(record["non_null_ratio"]) >= 0.95
            and int(record["assets_with_time_variation"]) >= 80
        ) or (
            sparse
            and int(record["assets_with_time_variation"]) >= 30
            and int(record["valid_rows"]) >= 1000
        )
        family_ok = family != "other"
        status = "ADMITTED" if lineage_ok and segment_ok and coverage_ok and family_ok else "REJECTED"
        reasons = []
        if not lineage_ok:
            reasons.append("FORBIDDEN_LINEAGE")
        if not segment_ok:
            reasons.append("TWO_SEGMENT_MATERIALIZATION_FAILED")
        if not coverage_ok:
            reasons.append("NON_NULL_OR_TIME_VARIATION_GATE")
        if not family_ok:
            reasons.append("NO_ECONOMIC_ROLE")
        rows.append(
            {
                **record,
                "field_family": family,
                "value_type": value_type,
                "unit": unit,
                "sparse_semantics": sparse,
                "observable_lag_hours": 1,
                "lineage_ok": lineage_ok,
                "economic_role": economic_role(field_id),
                "current_runtime_baseline": field_id in current,
                "admission_status": status,
                "rejection_reason": ";".join(reasons),
            }
        )
    audit = pd.DataFrame(rows)
    admitted = set(audit.loc[audit["admission_status"].eq("ADMITTED"), "field_id"])
    priority = {
        field: (0 if field in current else 1, field) for field in admitted
    }
    for record in equivalence.to_dict("records"):
        left = str(record["left_field"])
        right = str(record["right_field"])
        if left not in admitted or right not in admitted:
            continue
        if not (
            _bool(record["exact_equivalent"])
            or _bool(record["affine_equivalent"])
            or _bool(record["rank_equivalent"])
        ):
            continue
        keep, reject = sorted((left, right), key=lambda field: priority[field])
        admitted.discard(reject)
        mask = audit["field_id"].eq(reject)
        audit.loc[mask, "admission_status"] = "REJECTED"
        audit.loc[mask, "rejection_reason"] = f"EQUIVALENT_TO:{keep}"
    admitted_rows = audit[audit["field_id"].isin(admitted)].sort_values("field_id")
    contracts = tuple(
        FieldContract(
            str(row.field_id),
            str(row.value_type),
            str(row.unit),
            int(row.observable_lag_hours),
            "18M_TRAIN_FIELD_ADMISSION_AUDIT",
        )
        for row in admitted_rows.itertuples(index=False)
    )
    registry = {
        "schema_version": 1,
        "status": (
            "ADMITTED" if len(contracts) >= 16 else "CRYPTO_18M_FIELD_AUTHORIZATION_BOTTLENECK"
        ),
        "field_count": len(contracts),
        "field_families": sorted(set(admitted_rows["field_family"])),
        "fields": [
            {
                "field_id": row.field_id,
                "field_family": row.field_family,
                "value_type": row.value_type,
                "unit": row.unit,
                "observable_lag_hours": int(row.observable_lag_hours),
                "economic_role": row.economic_role,
                "current_runtime_baseline": bool(row.current_runtime_baseline),
                "non_null_ratio": float(row.non_null_ratio),
                "assets_with_time_variation": int(row.assets_with_time_variation),
            }
            for row in admitted_rows.itertuples(index=False)
        ],
    }
    registry["registry_sha256"] = _payload_sha(registry["fields"])
    return audit, registry, contracts


__all__ = [
    "RawPanelStore",
    "build_raw_panel_cache",
    "candidate_fields",
    "field_equivalence_audit",
    "infer_family",
    "infer_type_unit",
    "qualify_fields",
]
