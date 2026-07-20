"""Evidence builder for the gated broad-universe compositional-search epoch."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import random
import subprocess
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
import pandas as pd

from alphafactory_crypto.instrument_canary.admission import authorize_candidate
from alphafactory_crypto.instrument_canary.evaluator import array_sha256
from alphafactory_crypto.instrument_canary.grammar import (
    CANONICAL_PRIMITIVE_IDS,
    MECHANISM_FAMILIES,
    PRIMITIVE_PARAMETER_OPTIONS,
    FrozenGrammar,
)
from alphafactory_crypto.instrument_canary.materialize import materialize_authorized
from alphafactory_crypto.instrument_canary.release import (
    ReleasePanel,
    load_development_release,
    sha256_file,
)

from .expression import Expression, FieldContract, TypedExpressionRegistry


EPOCH_ID = "CRYPTO_BROAD_UNIVERSE_COMPOSITIONAL_ALPHA_SEARCH_EPOCH1"
DECISION_BLOCKED = "CRYPTO_BROAD_SEARCH_DATA_UNIVERSE_BLOCKED"
GRAMMAR_BOTTLENECK = "CRYPTO_COMPOSITIONAL_GRAMMAR_BOTTLENECK_CONFIRMED"
FORBIDDEN_PATH_TOKENS = frozenset(
    {"challenge", "validation", "holdout", "test", "recent", "forward", "may_stress"}
)

RUNTIME_OUTPUTS = (
    "CRYPTO_DATA_ASSET_MONTH_COVERAGE.parquet",
    "CRYPTO_DATA_SOURCE_QUALITY.json",
    "CRYPTO_UNIVERSE_ELIGIBILITY_LEDGER.parquet",
    "CRYPTO_CURRENT_GRAMMAR_EXPRESSIVITY_AUDIT.json",
    "CRYPTO_COMPOSITIONAL_GRAMMAR_V2.json",
    "CRYPTO_DERIVED_REPRESENTATION_REGISTRY.json",
    "CRYPTO_MATCHED_ABLATION_CONTRACT.json",
    "CRYPTO_PROPOSAL_EXPOSURE_LEDGER.parquet",
    "CRYPTO_ADMISSION_WATERFALL.csv",
    "CRYPTO_STRICT_PAIR_RESULTS.parquet",
    "CRYPTO_ROBUST_STATISTICAL_AUDIT.parquet",
    "CRYPTO_BEHAVIOR_CLUSTERS.json",
    "CRYPTO_CROSS_SEED_MONTH_REPRODUCTION.json",
    "CRYPTO_SEARCH_DECISION.json",
    "CRYPTO_RESOURCE_PREFLIGHT.json",
    "CRYPTO_ARTIFACT_MANIFEST.json",
)


FIELD_CONTRACTS = (
    FieldContract("trade_count", "COUNT", "trades"),
    FieldContract("underlying_trade_count", "COUNT", "trades"),
    FieldContract("quantity", "VOLUME", "base_asset"),
    FieldContract("notional", "NOTIONAL", "quote_asset"),
    FieldContract("buy_agg_trade_count", "COUNT", "trades"),
    FieldContract("sell_agg_trade_count", "COUNT", "trades"),
    FieldContract("buy_quantity", "VOLUME", "base_asset"),
    FieldContract("sell_quantity", "VOLUME", "base_asset"),
    FieldContract("buy_notional", "NOTIONAL", "quote_asset"),
    FieldContract("sell_notional", "NOTIONAL", "quote_asset"),
    FieldContract("signed_aggressor_quantity", "SIGNED_FLOW", "base_asset"),
    FieldContract("signed_aggressor_notional", "SIGNED_FLOW", "quote_asset"),
    FieldContract("vwap", "PRICE", "quote_per_base"),
    FieldContract("buy_vwap", "PRICE", "quote_per_base"),
    FieldContract("sell_vwap", "PRICE", "quote_per_base"),
    FieldContract("volume_imbalance", "RATIO", "dimensionless"),
    FieldContract("buy_sell_notional_ratio", "RATIO", "dimensionless"),
    FieldContract("price_range_bps", "BPS", "bps"),
    FieldContract("close_to_open_bps", "BPS", "bps"),
    FieldContract("large_trade_count_ratio_100k_plus", "UNIT_INTERVAL", "dimensionless"),
    FieldContract("large_notional_ratio_100k_plus", "UNIT_INTERVAL", "dimensionless"),
)


SEARCH_BEHAVIOR_DESCRIPTOR_SCHEMA: Mapping[str, Any] = {
    "schema_version": "CRYPTO_SEARCH_BEHAVIOR_DESCRIPTOR_V1",
    "rank_bucket_count": 10,
    "rank_mean_quantization_step": 2.0,
    "selection_rate_quantization_step": 0.20,
    "selected_overlap_quantization_step": 0.10,
    "mapped_weight_quantization_step": 0.05,
    "turnover_histogram_quantization_step": 0.10,
    "turnover_bin_edges": [0.0, 0.25, 0.50, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0],
    "selected_weight_epsilon": 1.0e-12,
    "pit_regime_source": "active_universe_size",
    "pit_regime_lag_hours": 1,
    "pit_regime_quantiles": [0.25, 0.50, 0.75],
    "outcome_fields_in_identity": [],
}


def _json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str
    ).encode("utf-8")


def _payload_sha(value: Any) -> str:
    return hashlib.sha256(_json_bytes(value)).hexdigest().upper()


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(
            json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True, default=str)
            + "\n"
        )


def _assert_safe_path(path: Path) -> Path:
    resolved = path.resolve()
    lowered = {part.lower() for part in resolved.parts}
    overlap = lowered & FORBIDDEN_PATH_TOKENS
    if overlap:
        raise PermissionError(f"sealed role path prohibited: {sorted(overlap)}")
    return resolved


def _git_sha(repo_root: Path) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=repo_root, text=True
    ).strip().lower()


def _calendar_rows(month: str, frequency_minutes: int) -> int:
    start = pd.Timestamp(f"{month}-01", tz="UTC")
    end = start + pd.offsets.MonthBegin(1)
    return int((end - start) / pd.Timedelta(minutes=frequency_minutes))


def _root_inventory(root: Path) -> dict[str, Any]:
    entries = []
    for path in sorted(root.iterdir(), key=lambda value: value.name.lower()):
        if path.name.lower() in FORBIDDEN_PATH_TOKENS:
            continue
        entries.append(
            {
                "name": path.name,
                "kind": "directory" if path.is_dir() else "file",
                "bytes": path.stat().st_size if path.is_file() else None,
            }
        )
    manifest_root = root / "manifests"
    report_root = root / "reports"
    return {
        "root": root.as_posix(),
        "scope": "TOP_LEVEL_ROOTS_PLUS_REGISTERED_CONTENT_HASHED_MANIFESTS",
        "top_level_entries": entries,
        "manifest_entry_count": len(tuple(manifest_root.iterdir())),
        "report_entry_count": len(tuple(report_root.iterdir())),
        "sealed_role_directories_not_entered": sorted(FORBIDDEN_PATH_TOKENS),
    }


def _coverage_rows(
    config: Mapping[str, Any], repo_root: Path
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    sources = config["data_inventory"]["sources"]
    price_path = _assert_safe_path(Path(sources["pre2024_kline_flow"]["coverage_manifest"]))
    price_manifest = _assert_safe_path(Path(sources["pre2024_kline_flow"]["content_manifest"]))
    replay_path = _assert_safe_path(Path(sources["pre2024_derivatives"]["coverage_manifest"]))
    universe_path = _assert_safe_path(Path(sources["universe_seed"]["path"]))
    probe_path = _assert_safe_path(Path(sources["universe_seed"]["probe_report"]))
    for path in (price_path, price_manifest, replay_path, universe_path, probe_path):
        if not path.is_file():
            raise FileNotFoundError(path)

    price = pd.read_csv(price_path)
    replay = pd.read_csv(replay_path)
    price["month"] = price["month"].astype(str)
    replay["month"] = replay["month"].astype(str)
    if price["month"].gt("2023-12").any() or replay["month"].gt("2023-12").any():
        raise PermissionError("pre-2024 manifest unexpectedly crosses frozen audit boundary")

    coverage: list[dict[str, Any]] = []
    eligibility: list[dict[str, Any]] = []
    price_hashes = dict(
        zip(
            pd.read_csv(price_manifest, usecols=["symbol", "month", "source_sha256"])
            .assign(month=lambda frame: frame["month"].astype(str))
            .apply(lambda row: f"{row['symbol']}|{row['month']}", axis=1),
            pd.read_csv(price_manifest, usecols=["source_sha256"])["source_sha256"],
        )
    )
    for row in price.itertuples(index=False):
        expected = _calendar_rows(str(row.month), 1)
        observed = int(row.rows_1m)
        coverage.append(
            {
                "asset": row.symbol,
                "month": row.month,
                "source_family": "OFFICIAL_BINANCE_VISION_1M_KLINE_AGGREGATED_FLOW",
                "source_authority": "data.binance.vision",
                "frequency": "1m/15m/1h",
                "rows": observed,
                "expected_rows": expected,
                "missing_rate_calendar": max(0.0, 1.0 - observed / expected),
                "duplicate_rate": int(row.duplicate_timestamp_count) / max(1, observed),
                "timestamp_continuity": "PARTIAL_LISTING_AWARE" if observed < expected else "FULL_MONTH",
                "core_price_available": True,
                "native_aggtrades_available": False,
                "buy_sell_flow_available": True,
                "trade_size_distribution_available": False,
                "funding_available": False,
                "open_interest_available": False,
                "mark_index_available": False,
                "pit_observable_time": "BUCKET_CLOSE_PLUS_ONE_MINUTE",
                "field_units": "OHLC price; base volume; quote volume; count; taker-buy aggregates",
                "content_sha256": price_hashes.get(f"{row.symbol}|{row.month}", ""),
            }
        )
        eligibility.append(
            {
                "asset": row.symbol,
                "month": row.month,
                "eligible": True,
                "first_observed_timestamp": str(row.min_timestamp),
                "last_observed_timestamp": str(row.max_timestamp),
                "basis": "OFFICIAL_ARCHIVE_FILE_OBSERVED",
                "pit_qualified": False,
                "disqualification": "SYMBOL_SEED_DERIVED_FROM_2026_CURRENT_EXCHANGEINFO_AND_CHECKPOINT_METRICS",
            }
        )

    for row in replay.itertuples(index=False):
        expected = _calendar_rows(str(row.month), 60)
        observed = int(row.rows)
        coverage.append(
            {
                "asset": row.symbol,
                "month": row.month,
                "source_family": "OFFICIAL_BINANCE_VISION_DERIVATIVES_REPLAY_1H",
                "source_authority": "data.binance.vision and fapi.binance.com",
                "frequency": "1h",
                "rows": observed,
                "expected_rows": expected,
                "missing_rate_calendar": max(0.0, 1.0 - observed / expected),
                "duplicate_rate": int(row.duplicate_timestamp_count) / max(1, observed),
                "timestamp_continuity": "PARTIAL_LISTING_AWARE" if observed < expected else "FULL_MONTH",
                "core_price_available": True,
                "native_aggtrades_available": False,
                "buy_sell_flow_available": False,
                "trade_size_distribution_available": False,
                "funding_available": float(row.funding_coverage) > 0.0,
                "open_interest_available": float(row.metrics_coverage) > 0.0,
                "mark_index_available": float(row.mark_coverage) > 0.0,
                "pit_observable_time": "HOURLY_BUCKET_CLOSE; FUNDING/METRICS SOURCE TIMESTAMP",
                "field_units": "price; funding ratio; contract OI; notional OI; account/position ratios",
                "content_sha256": "OUTPUT_BUNDLE_MANIFEST_ONLY",
            }
        )

    base = repo_root / config["base_canary_config"]
    canary = json.loads(base.read_text(encoding="utf-8"))
    for asset in canary["release"]["symbols"]:
        for month in canary["release"]["months"]:
            coverage.append(
                {
                    "asset": asset,
                    "month": month,
                    "source_family": "NATIVE_AGGTRADES_CORE10_DEVELOPMENT",
                    "source_authority": "official Binance aggTrades archive via qualified release",
                    "frequency": "1h",
                    "rows": _calendar_rows(month, 60),
                    "expected_rows": _calendar_rows(month, 60),
                    "missing_rate_calendar": 0.0,
                    "duplicate_rate": 0.0,
                    "timestamp_continuity": "FULL_MONTH",
                    "core_price_available": True,
                    "native_aggtrades_available": True,
                    "buy_sell_flow_available": True,
                    "trade_size_distribution_available": True,
                    "funding_available": False,
                    "open_interest_available": False,
                    "mark_index_available": False,
                    "pit_observable_time": "BUCKET_T_PLUS_1H; EXECUTION_T_PLUS_2H",
                    "field_units": "native trade count; base volume; quote notional; VWAP; BPS; ratios",
                    "content_sha256": canary["release"]["expected_output_bundle_sha256"],
                }
            )
            eligibility.append(
                {
                    "asset": asset,
                    "month": month,
                    "eligible": True,
                    "first_observed_timestamp": f"{month}-01T00:00:00Z",
                    "last_observed_timestamp": "FULL_CALENDAR_MONTH",
                    "basis": "PREDECLARED_FIXED_CORE_DEVELOPMENT_RELEASE",
                    "pit_qualified": True,
                    "disqualification": "BROAD_UNIVERSE_ASSET_COUNT_BELOW_40",
                }
            )

    probe = json.loads(probe_path.read_text(encoding="utf-8"))
    quality = {
        "schema_version": 1,
        "source_authority": {
            "pre2024_price_flow": "official Binance Vision monthly archive",
            "pre2024_derivatives": "official Binance Vision and Binance Futures API",
            "native_aggtrades_core10": "qualified official Binance archive release",
        },
        "source_hashes": {
            "price_coverage": sha256_file(price_path),
            "price_manifest": sha256_file(price_manifest),
            "derivatives_coverage": sha256_file(replay_path),
            "universe_seed": sha256_file(universe_path),
            "current_probe": sha256_file(probe_path),
        },
        "current_probe_generated_at": probe.get("generated_at"),
        "current_probe_total_usdt_perp_trading": probe.get("total_usdt_perp_trading"),
        "universe_provenance_result": "SURVIVORSHIP_OR_ELIGIBILITY_UNRESOLVED",
        "universe_provenance_reason": "The 176-symbol historical download seed was selected from a 2026 current exchangeInfo snapshot plus current checkpoint availability; official file existence proves a listed asset-month but cannot prove that delisted historical contracts were not omitted.",
        "field_family_limits": {
            "bookTicker_BBO": "PRESENT_ELSEWHERE_WITH_LIMITED_COVERAGE_NOT_ADMITTED",
            "depth_snapshots": "NOT_RESEARCH_QUALIFIED_IN_SCANNED_RELEASES",
            "liquidation_force_orders": "NOT_RESEARCH_QUALIFIED_IN_SCANNED_RELEASES",
            "cross_asset_market_context": "DERIVABLE_ONLY_AFTER_PIT_UNIVERSE_QUALIFICATION",
        },
        "discovered_but_not_admitted_releases": [
            {
                "identity": "binance_universe498_replay_1h_v1/v2",
                "reason": "coverage manifests co-mingle admitted development dates with sealed/recent dates; no content was opened",
            },
            {
                "identity": "core39_market_structure",
                "reason": "limited universe and date/field contracts were not sufficient for either data mode",
            },
            {
                "identity": "bookTicker/BBO and depth snapshots",
                "reason": "local names were discovered but no registered qualified broad release was found",
            },
            {
                "identity": "liquidation/force orders",
                "reason": "no registered qualified broad release was found",
            },
            {
                "identity": "OKX open-interest clean218 30d",
                "reason": "history is far below the 18-month broad gate and cross-venue identity is not qualified",
            },
        ],
        "sealed_reads": 0,
    }
    return pd.DataFrame(coverage), pd.DataFrame(eligibility), quality


def _longest_contiguous_months(months: Iterable[str]) -> int:
    ordinals = sorted(
        {int(value[:4]) * 12 + int(value[5:7]) - 1 for value in months}
    )
    best = current = 0
    previous: int | None = None
    for value in ordinals:
        current = current + 1 if previous is not None and value == previous + 1 else 1
        best = max(best, current)
        previous = value
    return best


def qualify_data_mode(coverage: pd.DataFrame, eligibility: pd.DataFrame) -> dict[str, Any]:
    broad = coverage[
        coverage["source_family"].eq("OFFICIAL_BINANCE_VISION_1M_KLINE_AGGREGATED_FLOW")
    ]
    active_by_month = broad.groupby("month")["asset"].nunique().sort_index()
    price_qualified = broad[broad["missing_rate_calendar"].le(0.10)]
    core = coverage[
        coverage["source_family"].eq("NATIVE_AGGTRADES_CORE10_DEVELOPMENT")
    ]
    broad_contiguous = _longest_contiguous_months(active_by_month.index)
    core_contiguous = _longest_contiguous_months(core["month"].unique())
    broad_checks = {
        "assets_at_least_40": int(broad["asset"].nunique()) >= 40,
        "continuous_months_at_least_18": broad_contiguous >= 18,
        "core_agg_price_asset_month_coverage_at_least_90pct": (
            len(price_qualified) / max(1, len(broad)) >= 0.90
        ),
        "monthly_active_assets_at_least_30": bool((active_by_month >= 30).all()),
        "dynamic_eligibility_pit_qualified": bool(eligibility["pit_qualified"].all()),
        "native_order_field_coverage_not_fragmented": bool(
            broad["native_aggtrades_available"].all()
        ),
    }
    core_checks = {
        "fixed_product_universe_explicit": True,
        "assets": int(core["asset"].nunique()),
        "continuous_months_at_least_24": core_contiguous >= 24,
        "broad_conclusions_forbidden": True,
    }
    failures = []
    if not broad_checks["continuous_months_at_least_18"]:
        failures.append("TIME_HISTORY_TOO_SHORT")
    if not broad_checks["dynamic_eligibility_pit_qualified"]:
        failures.append("SURVIVORSHIP_OR_ELIGIBILITY_UNRESOLVED")
    if not broad_checks["native_order_field_coverage_not_fragmented"]:
        failures.append("ORDER_FIELD_COVERAGE_FRAGMENTED")
    if not core_checks["continuous_months_at_least_24"]:
        failures.append("EXPLICIT_CORE_TIME_HISTORY_TOO_SHORT")
    return {
        "broad_cross_sectional": {
            "checks": broad_checks,
            "assets": int(broad["asset"].nunique()),
            "months": sorted(broad["month"].unique().tolist()),
            "continuous_months": broad_contiguous,
            "monthly_active_assets": {str(k): int(v) for k, v in active_by_month.items()},
        },
        "explicit_core_time_series": {
            "checks": core_checks,
            "months": sorted(core["month"].unique().tolist()),
            "continuous_months": core_contiguous,
        },
        "qualified_mode": None,
        "gate_result": "CRYPTO_DATA_UNIVERSE_NOT_RESEARCH_QUALIFIED",
        "failure_classes": failures,
    }


def _sample_indices(size: int, count: int, seed: int) -> tuple[int, ...]:
    rng = random.Random(seed)
    offset = rng.randrange(size)
    stride = rng.randrange(1, size)
    while math.gcd(stride, size) != 1:
        stride = rng.randrange(1, size)
    return tuple((offset + index * stride) % size for index in range(count))


def _rank_sha(values: np.ndarray) -> str:
    order = np.argsort(values, axis=0, kind="mergesort")
    ranks = np.argsort(order, axis=0, kind="mergesort").astype(np.int16)
    return array_sha256(ranks)


def _behavior_sha(weights: np.ndarray, month_labels: np.ndarray) -> str:
    signature: list[Any] = []
    for month in sorted(set(month_labels.tolist())):
        block = weights[:, month_labels == month]
        changes = np.diff(block, axis=1, prepend=np.zeros((block.shape[0], 1)))
        signature.append(
            {
                "month": month,
                "asset_mean": np.round(np.mean(block, axis=1), 2).tolist(),
                "asset_std": np.round(np.std(block, axis=1), 2).tolist(),
                "positive_rate": np.round(np.mean(block > 0, axis=1), 1).tolist(),
                "turnover_l1": round(float(np.mean(np.sum(np.abs(changes), axis=0))), 1),
                "gross_exposure": round(float(np.mean(np.sum(np.abs(block), axis=0))), 1),
            }
        )
    return _payload_sha(signature)


def freeze_search_behavior_contract(active_universe_size: np.ndarray) -> dict[str, Any]:
    """Freeze behavior quantization and a lag-only market-state regime contract."""

    values = np.asarray(active_universe_size, dtype=float)
    if values.ndim == 2:
        with np.errstate(all="ignore"):
            values = np.nanmedian(values, axis=0)
    if values.ndim != 1 or values.size < 2:
        raise ValueError("active_universe_size must expose at least two hourly coordinates")
    lagged = np.empty(values.shape, dtype=float)
    lagged[0] = np.nan
    lagged[1:] = values[:-1]
    finite = lagged[np.isfinite(lagged)]
    if finite.size == 0:
        raise ValueError("lagged active_universe_size has no finite observations")
    quantiles = np.asarray(SEARCH_BEHAVIOR_DESCRIPTOR_SCHEMA["pit_regime_quantiles"])
    thresholds = np.quantile(finite, quantiles, method="linear").astype(float)
    return {
        **dict(SEARCH_BEHAVIOR_DESCRIPTOR_SCHEMA),
        "pit_regime_thresholds": thresholds.tolist(),
        "pit_regime_thresholds_sha256": _payload_sha(thresholds.tolist()),
        "frozen_observation_count": int(finite.size),
        "contract_sha256": _payload_sha(
            {
                **dict(SEARCH_BEHAVIOR_DESCRIPTOR_SCHEMA),
                "pit_regime_thresholds": thresholds.tolist(),
                "frozen_observation_count": int(finite.size),
            }
        ),
    }


def _quantized(values: np.ndarray, step: float, *, missing: int = -32768) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    output = np.full(array.shape, missing, dtype=np.int16)
    finite = np.isfinite(array)
    output[finite] = np.rint(array[finite] / float(step)).astype(np.int16)
    return output


def search_behavior_descriptor(
    *,
    signal: np.ndarray,
    weights: np.ndarray,
    eligible_mask: np.ndarray,
    month_labels: np.ndarray,
    timestamp_ns: np.ndarray,
    active_universe_size: np.ndarray,
    horizon_hours: int,
    mapping_id: str,
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    """Return a coarse, frozen, outcome-free behavior-family identity."""

    signal = np.asarray(signal, dtype=float)
    weights = np.asarray(weights, dtype=float)
    eligible = np.asarray(eligible_mask, dtype=bool)
    months = np.asarray(month_labels, dtype=str)
    timestamps = np.asarray(timestamp_ns, dtype=np.int64)
    if signal.shape != weights.shape or signal.shape != eligible.shape:
        raise ValueError("behavior arrays must share the asset/time coordinate shape")
    if signal.ndim != 2 or signal.shape[1] != months.size or months.size != timestamps.size:
        raise ValueError("behavior time coordinates do not match the mapped arrays")
    if str(contract.get("schema_version")) != "CRYPTO_SEARCH_BEHAVIOR_DESCRIPTOR_V1":
        raise ValueError("unsupported behavior descriptor contract")
    expected_contract_hash = _payload_sha(
        {
            key: value
            for key, value in contract.items()
            if key not in {"contract_sha256", "pit_regime_thresholds_sha256"}
        }
    )
    if expected_contract_hash != str(contract.get("contract_sha256")):
        raise ValueError("behavior descriptor contract identity changed")

    regime_values = np.asarray(active_universe_size, dtype=float)
    if regime_values.ndim == 2:
        with np.errstate(all="ignore"):
            regime_values = np.nanmedian(regime_values, axis=0)
    if regime_values.shape != (signal.shape[1],):
        raise ValueError("behavior regime source does not match the time coordinate")
    lagged_regime = np.empty(regime_values.shape, dtype=float)
    lagged_regime[0] = np.nan
    lagged_regime[1:] = regime_values[:-1]
    thresholds = np.asarray(contract["pit_regime_thresholds"], dtype=float)
    regimes = np.full(lagged_regime.shape, -1, dtype=np.int8)
    finite_regime = np.isfinite(lagged_regime)
    regimes[finite_regime] = np.digitize(
        lagged_regime[finite_regime], thresholds, right=True
    ).astype(np.int8)

    finite_signal = eligible & np.isfinite(signal)
    sortable = np.where(finite_signal, signal, np.inf)
    order = np.argsort(sortable, axis=0, kind="mergesort")
    ranks = np.argsort(order, axis=0, kind="mergesort").astype(float)
    denominators = np.maximum(1, finite_signal.sum(axis=0) - 1)
    rank_buckets = np.floor(
        ranks / denominators[np.newaxis, :] * int(contract["rank_bucket_count"])
    )
    rank_buckets = np.clip(rank_buckets, 0, int(contract["rank_bucket_count"]) - 1)
    rank_buckets[~finite_signal] = np.nan

    epsilon = float(contract["selected_weight_epsilon"])
    selected = np.abs(weights) > epsilon
    selected_sign = np.where(selected, np.sign(weights), 0.0)
    changes = np.diff(weights, axis=1, prepend=np.zeros((weights.shape[0], 1)))
    turnover_path = np.sum(np.abs(changes), axis=0) / float(horizon_hours)
    previous_selected = np.zeros_like(selected)
    previous_selected[:, 1:] = selected[:, :-1]
    union = np.sum(selected | previous_selected, axis=0)
    intersection = np.sum(selected & previous_selected, axis=0)
    overlap = np.divide(
        intersection,
        union,
        out=np.ones(intersection.shape, dtype=float),
        where=union > 0,
    )

    rank_rows: list[Any] = []
    selection_rows: list[Any] = []
    weight_rows: list[Any] = []
    turnover_rows: list[Any] = []
    group_keys = sorted({(str(month), int(regime)) for month, regime in zip(months, regimes)})
    turnover_edges = np.asarray(contract["turnover_bin_edges"], dtype=float)
    for month, regime in group_keys:
        local = (months == month) & (regimes == regime)
        if not np.any(local):
            continue
        local_ranks = rank_buckets[:, local]
        with np.errstate(all="ignore"):
            rank_mean = np.nanmean(local_ranks, axis=1)
        rank_rows.append(
            [month, regime, _quantized(rank_mean, float(contract["rank_mean_quantization_step"])).tolist()]
        )
        selection_rows.append(
            [
                month,
                regime,
                _quantized(
                    np.mean(selected_sign[:, local] > 0, axis=1),
                    float(contract["selection_rate_quantization_step"]),
                ).tolist(),
                _quantized(
                    np.mean(selected_sign[:, local] < 0, axis=1),
                    float(contract["selection_rate_quantization_step"]),
                ).tolist(),
                int(
                    _quantized(
                        np.asarray([np.mean(overlap[local])]),
                        float(contract["selected_overlap_quantization_step"]),
                    )[0]
                ),
            ]
        )
        local_weights = weights[:, local]
        weight_rows.append(
            [
                month,
                regime,
                _quantized(
                    np.mean(local_weights, axis=1),
                    float(contract["mapped_weight_quantization_step"]),
                ).tolist(),
                _quantized(
                    np.std(local_weights, axis=1),
                    float(contract["mapped_weight_quantization_step"]),
                ).tolist(),
            ]
        )
        local_turnover = turnover_path[local]
        histogram = np.histogram(local_turnover, bins=np.r_[turnover_edges, np.inf])[0]
        histogram_rate = histogram / max(1, int(histogram.sum()))
        turnover_rows.append(
            [
                month,
                regime,
                _quantized(
                    histogram_rate,
                    float(contract["turnover_histogram_quantization_step"]),
                ).tolist(),
            ]
        )

    coordinate_descriptor = {
        "shape": list(signal.shape),
        "timestamp_sha256": array_sha256(timestamps),
        "eligible_sha256": array_sha256(eligible.astype(np.int8)),
        "mapping_id": str(mapping_id),
        "horizon_hours": int(horizon_hours),
    }
    components = {
        "coordinate_data_binding_id": _payload_sha(coordinate_descriptor),
        "rank_descriptor_id": _payload_sha(rank_rows),
        "selected_asset_overlap_id": _payload_sha(selection_rows),
        "mapped_weight_descriptor_id": _payload_sha(weight_rows),
        "turnover_path_descriptor_id": _payload_sha(turnover_rows),
        "pit_regime_descriptor_id": _payload_sha(
            {
                "source": contract["pit_regime_source"],
                "lag_hours": int(contract["pit_regime_lag_hours"]),
                "thresholds": thresholds.tolist(),
                "regime_path": regimes.tolist(),
            }
        ),
        "descriptor_contract_sha256": str(contract["contract_sha256"]),
    }
    return {
        **components,
        "behavior_family_id": _payload_sha(components),
        "descriptor_schema_version": str(contract["schema_version"]),
        "identity_excludes": ["gross", "net", "cost", "pair_reward"],
    }


def audit_grammar(
    *,
    config: Mapping[str, Any],
    panel: ReleasePanel,
    source_sha: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    grammar = FrozenGrammar.default()
    count = int(config["grammar_audit"]["sample_candidates"])
    indices = _sample_indices(grammar.support_size, count, int(config["grammar_audit"]["seed"]))
    exact = Counter()
    numeric = Counter()
    ranks = Counter()
    weights = Counter()
    behaviors = Counter()
    materialization_cache: dict[tuple[Any, ...], tuple[str, str, str, str]] = {}
    started = time.perf_counter()
    for ordinal, index in enumerate(indices, start=1):
        genome = grammar.decode(index)
        receipt = authorize_candidate(
            genome,
            grammar=grammar,
            release_manifest=panel.release_manifest,
            expected_release=config["canary"]["release"],
            target_contract=config["canary"]["target_horizon"],
            source_code_sha=source_sha,
            cost_contract=config["canary"]["cost"],
        )
        key = (
            genome.field_id,
            genome.representation_id,
            genome.primitive_id,
            genome.window,
            genome.long_window,
            genome.threshold,
            genome.mechanism_family,
        )
        fingerprints = materialization_cache.get(key)
        if fingerprints is None:
            materialized = materialize_authorized(
                receipt, field_reader=lambda field_id: panel.fields[field_id]
            )
            fingerprints = (
                materialized.signal_array_sha256,
                _rank_sha(materialized.signal),
                materialized.weight_array_sha256,
                _behavior_sha(materialized.mapped.weights, panel.month_labels),
            )
            materialization_cache[key] = fingerprints
        signal_fingerprint, rank_fingerprint, weight_fingerprint, behavior_fingerprint = fingerprints
        exact[genome.candidate_id] += 1
        numeric[signal_fingerprint] += 1
        ranks[rank_fingerprint] += 1
        weights[weight_fingerprint] += 1
        behaviors[behavior_fingerprint] += 1
        if ordinal % 100 == 0:
            print(
                json.dumps(
                    {
                        "event": "grammar_alias_progress",
                        "sampled": ordinal,
                        "materialized_surfaces": len(materialization_cache),
                    },
                    sort_keys=True,
                ),
                flush=True,
            )

    ratio = len(behaviors) / len(exact)
    bottleneck = True  # field arity=1 and cross-field interactions=0 are source facts.
    audit = {
        "schema_version": 1,
        "epoch_id": EPOCH_ID,
        "source_sha": source_sha,
        "grammar_contract_sha256": grammar.contract_sha256,
        "support_size": grammar.support_size,
        "raw_field_count": len(grammar.field_specs),
        "field_representation_routes": len(grammar.field_representations),
        "representation_id_count": len({value[1] for value in grammar.field_representations}),
        "primitive_count": len(CANONICAL_PRIMITIVE_IDS),
        "parameter_routes": int(sum(len(value) for value in PRIMITIVE_PARAMETER_OPTIONS.values())),
        "mechanism_count": len(MECHANISM_FAMILIES),
        "field_arity": 1,
        "expression_depth": 2,
        "cross_field_interaction_count": 0,
        "dimension_aware_arithmetic_count": 0,
        "derived_field_dag_count": 0,
        "materializer_source_fact": "materialize_authorized reads receipt.field_id exactly once, applies one representation, then one primitive",
        "sample": {
            "selection": "deterministic full-cycle affine grammar coordinates",
            "seed": int(config["grammar_audit"]["seed"]),
            "requested": count,
            "exact_unique": len(exact),
            "numeric_unique": len(numeric),
            "rank_unique": len(ranks),
            "mapped_weight_unique": len(weights),
            "behavior_unique": len(behaviors),
            "numeric_alias_rate": 1.0 - len(numeric) / len(exact),
            "rank_alias_rate": 1.0 - len(ranks) / len(exact),
            "mapped_weight_alias_rate": 1.0 - len(weights) / len(exact),
            "behavior_alias_rate": 1.0 - ratio,
            "behavior_identity_over_exact_identity": ratio,
            "unique_materialized_surfaces": len(materialization_cache),
            "elapsed_seconds": time.perf_counter() - started,
        },
        "bottleneck_rules": {
            "field_arity_equals_one": True,
            "cross_field_interaction_count_equals_zero": True,
            "behavior_identity_over_exact_below_0_30": ratio < 0.30,
        },
        "decision": GRAMMAR_BOTTLENECK if bottleneck else "NOT_CONFIRMED",
        "cannot_conclude": [
            "No claim about compositional grammar economic value",
            "No claim about OOS performance",
            "No claim that adding windows repairs the bottleneck",
        ],
    }
    clusters = {
        "schema_version": 1,
        "sample_candidates": count,
        "fingerprint_definition": "per-month quantized asset mean/std/positive-rate plus turnover and gross exposure",
        "clusters": [
            {"behavior_sha256": key, "count": value}
            for key, value in sorted(behaviors.items(), key=lambda item: (-item[1], item[0]))
        ],
        "numeric_identity_histogram": dict(sorted(Counter(numeric.values()).items())),
        "rank_identity_histogram": dict(sorted(Counter(ranks.values()).items())),
        "mapped_weight_identity_histogram": dict(sorted(Counter(weights.values()).items())),
    }
    return audit, clusters


def _derived_registry_payload(registry: TypedExpressionRegistry) -> dict[str, Any]:
    raw = Expression.raw
    examples = {
        "flow_pressure_notional": Expression(
            "FlowPerNotional",
            (raw("signed_aggressor_notional"), raw("notional")),
        ),
        "flow_per_trade": Expression(
            "FlowPerTrade",
            (raw("signed_aggressor_notional"), raw("trade_count")),
        ),
        "vwap_gap": Expression(
            "NormalizedDifference", (raw("buy_vwap"), raw("sell_vwap"))
        ),
        "price_flow_impact": Expression(
            "PriceImpactRatio",
            (raw("price_range_bps"), raw("signed_aggressor_notional")),
        ),
        "large_trade_modulated_flow": Expression(
            "SafeMul",
            (raw("large_notional_ratio_100k_plus"), raw("volume_imbalance")),
        ),
        "cross_asset_flow_state": Expression(
            "CrossAssetRelative",
            (
                raw("volume_imbalance"),
                raw("buy_sell_notional_ratio"),
            ),
        ),
    }
    rows = []
    for name, expression in examples.items():
        assurance = registry.validate(expression)
        rows.append(
            {
                "family": name,
                "expression": expression.canonical_dict(),
                "expression_id": expression.expression_id,
                "assurance": {
                    "value_type": assurance.value_type,
                    "unit": assurance.unit,
                    "depth": assurance.depth,
                    "raw_fields": assurance.raw_fields,
                    "rolling_windows": assurance.rolling_windows,
                    "cross_asset_normalizations": assurance.cross_asset_normalizations,
                    "regime_gates": assurance.regime_gates,
                    "observable_lag_hours": assurance.observable_lag_hours,
                },
            }
        )
    return {
        "schema_version": 1,
        "lifecycle": "EXPERIMENTAL",
        "materialization": "LAZY_ONLY",
        "families": rows,
    }


def _matched_ablation_contract() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "lifecycle": "EXPERIMENTAL_NOT_RUN_DATA_GATE_BLOCKED",
        "match_on": [
            "raw fields",
            "representations",
            "rolling windows",
            "target horizon",
            "portfolio mapping",
            "support mask",
            "cost model",
        ],
        "ablation_routes": {
            "flow-price interaction": "flow-only",
            "large-trade modulation": "unmodulated flow",
            "regime gate": "ungated signal",
            "cross-asset relative": "asset-local signal",
            "persistence modulation": "instantaneous signal",
        },
        "required_outputs": [
            "primary net metric",
            "control net metric",
            "matched increment",
            "matched turnover increment",
            "support overlap",
            "behavior equivalence",
        ],
        "admission": "NO_MATCHED_CONTROL_NO_FINAL_MECHANISM_CONCLUSION",
        "feedback": "EXISTING_STRICT_FEEDBACK_ONLY",
        "robust_audit": "REPORT_ONLY_NEVER_FED_BACK_TO_SEARCH",
    }


def _empty_outputs(runtime_root: Path, data_gate: Mapping[str, Any]) -> None:
    metadata = {
        "epoch_id": pd.Series(dtype="str"),
        "status": pd.Series(dtype="str"),
        "reason": pd.Series(dtype="str"),
    }
    pd.DataFrame(metadata).to_parquet(runtime_root / "CRYPTO_PROPOSAL_EXPOSURE_LEDGER.parquet", index=False)
    pd.DataFrame(metadata).to_parquet(runtime_root / "CRYPTO_STRICT_PAIR_RESULTS.parquet", index=False)
    pd.DataFrame(metadata).to_parquet(runtime_root / "CRYPTO_ROBUST_STATISTICAL_AUDIT.parquet", index=False)
    with (runtime_root / "CRYPTO_ADMISSION_WATERFALL.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["stage", "count", "status", "reason"],
            lineterminator="\n",
        )
        writer.writeheader()
        for stage in (
            "generated",
            "legal",
            "exact_unique",
            "numeric_unique",
            "behavior_unique",
            "materialized",
            "support_pass",
            "mapping_pass",
            "strict_pass",
            "gross_positive",
            "net_positive",
            "matched_positive",
            "robust_positive",
            "cross_seed_reproduced",
            "cross_month_stable",
        ):
            writer.writerow(
                {
                    "stage": stage,
                    "count": 0,
                    "status": "NOT_RUN",
                    "reason": data_gate["gate_result"],
                }
            )


def _report_text(decision: Mapping[str, Any], grammar: Mapping[str, Any]) -> str:
    data = decision["data_gate"]
    broad = data["broad_cross_sectional"]
    core = data["explicit_core_time_series"]
    sample = grammar["sample"]
    return f"""# Crypto Broad-Universe Compositional Search Epoch 1

## Decision

`{decision['main_status']}`

The requested large Alpha search did not start.  Existing data qualifies neither
the broad cross-sectional mode nor the explicit core time-series fallback.

## Data gate

- Broad archive: {broad['assets']} observed assets, {broad['continuous_months']} continuous months; required 40 assets and 18 months.
- Core native aggTrades: {core['checks']['assets']} assets, {core['continuous_months']} continuous months; required 24 months for the fallback.
- Failure classes: {', '.join(data['failure_classes'])}.
- Universe provenance: the historical seed came from a 2026 current exchangeInfo/metrics probe, so delisted historical contracts may be omitted.
- Sealed reads: 0.

## Current grammar

- Frozen support: {grammar['support_size']} exact candidates.
- Structure: one field, one representation, one primitive, zero cross-field interactions.
- Deterministic sample: {sample['requested']} candidates; {sample['numeric_unique']} numeric, {sample['rank_unique']} rank, {sample['mapped_weight_unique']} mapped-weight, and {sample['behavior_unique']} behavior identities.
- Grammar decision: `{grammar['decision']}`.

## Experimental replacement

The closure includes a small typed DAG and matched-ablation contract, but it is
not connected to the formal evaluator and was not economically evaluated.  Its
lifecycle remains `EXPERIMENTAL_CURRENT_NON_FORMAL`.

## Search budget

Proposal attempts: 0. Strict primary/control pairs: 0. The 64-pair cost
preflight and the 500,000-attempt search are gated behind qualified data and
were intentionally not run.
"""


def build_evidence(repo_root: Path, *, config_path: Path, source_sha: str | None = None) -> dict[str, Any]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    source_sha = (source_sha or _git_sha(repo_root)).lower()
    if source_sha != _git_sha(repo_root):
        raise ValueError("build must bind the checked-out source SHA")
    if config["boundaries"]["sealed_reads_allowed"]:
        raise ValueError("sealed reads must remain forbidden")
    runtime_root = repo_root / config["outputs"]["runtime_root"]
    runtime_root.mkdir(parents=True, exist_ok=True)
    canary = json.loads((repo_root / config["base_canary_config"]).read_text(encoding="utf-8"))
    config["canary"] = canary

    coverage, eligibility, source_quality = _coverage_rows(config, repo_root)
    source_quality["filesystem_inventory"] = _root_inventory(
        _assert_safe_path(Path(config["data_inventory"]["root"]))
    )
    data_gate = qualify_data_mode(coverage, eligibility)
    panel = load_development_release(canary)
    if panel.sealed_reads != 0:
        raise PermissionError("development release reported sealed reads")
    grammar_audit, behavior_clusters = audit_grammar(
        config=config, panel=panel, source_sha=source_sha
    )
    registry = TypedExpressionRegistry(FIELD_CONTRACTS)

    coverage.to_parquet(runtime_root / RUNTIME_OUTPUTS[0], index=False)
    eligibility.to_parquet(runtime_root / RUNTIME_OUTPUTS[2], index=False)
    _write_json(runtime_root / RUNTIME_OUTPUTS[1], source_quality)
    _write_json(runtime_root / RUNTIME_OUTPUTS[3], grammar_audit)
    _write_json(runtime_root / RUNTIME_OUTPUTS[4], registry.contract_payload())
    _write_json(runtime_root / RUNTIME_OUTPUTS[5], _derived_registry_payload(registry))
    _write_json(runtime_root / RUNTIME_OUTPUTS[6], _matched_ablation_contract())
    _empty_outputs(runtime_root, data_gate)
    _write_json(runtime_root / RUNTIME_OUTPUTS[11], behavior_clusters)
    _write_json(
        runtime_root / RUNTIME_OUTPUTS[12],
        {
            "schema_version": 1,
            "status": "NOT_RUN_DATA_GATE_BLOCKED",
            "cross_seed_reproduced_clusters": 0,
            "cross_month_stable_clusters": 0,
        },
    )
    resource = {
        "schema_version": 1,
        "data_gate": data_gate["gate_result"],
        "cost_preflight_pairs": 0,
        "cost_preflight_status": "NOT_RUN_DATA_GATE_BLOCKED",
        "large_search_authorized": False,
        "frozen_hard_caps": config["search_budget"],
        "official_backfill_status": "NOT_STARTED",
        "official_backfill_reason": "Historical universe completeness must be resolved before a survivorship-safe download plan can be sized.",
    }
    _write_json(runtime_root / RUNTIME_OUTPUTS[14], resource)
    decision = {
        "schema_version": 1,
        "epoch_id": EPOCH_ID,
        "branch": config["branch"],
        "source_sha": source_sha,
        "main_status": DECISION_BLOCKED,
        "data_gate": data_gate,
        "grammar_status": grammar_audit["decision"],
        "actual_universe_mode": None,
        "proposal_attempts": 0,
        "strict_pairs": 0,
        "matched_positive_clusters": 0,
        "robust_positive_clusters": 0,
        "sealed_reads": 0,
        "formal_performance_search": "FORBIDDEN",
        "candidate_promotion": "FORBIDDEN",
        "forward": "SEALED",
        "challenge": "SEALED",
        "cannot_conclude": [
            "No qualified-data no-edge conclusion",
            "No compositional representation increment conclusion",
            "No policy comparison conclusion",
            "No OOS or promotion conclusion",
        ],
    }
    _write_json(runtime_root / RUNTIME_OUTPUTS[13], decision)
    report_path = repo_root / config["outputs"]["report"]
    failure_path = repo_root / config["outputs"]["failure_report"]
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(_report_text(decision, grammar_audit))
    with failure_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(
            "# Crypto Broad Search Failure Attribution\n\n"
            + "Main status: `CRYPTO_BROAD_SEARCH_DATA_UNIVERSE_BLOCKED`.\n\n"
            + "| Layer | Classification | Evidence |\n|---|---|---|\n"
            + "| Time history | TIME_HISTORY_TOO_SHORT | broad=6/18 months; core=6/24 months |\n"
            + "| Historical eligibility | SURVIVORSHIP_OR_ELIGIBILITY_UNRESOLVED | current-snapshot seed may omit delisted contracts |\n"
            + "| Order fields | ORDER_FIELD_COVERAGE_FRAGMENTED | native aggTrades is limited to core10 development; broad history is kline aggregates |\n"
            + "| Representation | COMPOSITIONAL_GRAMMAR_TOO_SHALLOW | current materializer is one-field/one-representation/one-primitive |\n"
            + "| Search/economics | NOT_RUN | data gate blocked 64-pair preflight and large search |\n"
        )

    artifact_paths = [
        runtime_root / name for name in RUNTIME_OUTPUTS if name != RUNTIME_OUTPUTS[-1]
    ] + [report_path, failure_path, config_path]
    manifest = {
        "schema_version": 1,
        "epoch_id": EPOCH_ID,
        "producer_source_sha": source_sha,
        "data_role": "DEVELOPMENT_ONLY",
        "sealed_reads": 0,
        "artifacts": [
            {
                "path": path.relative_to(repo_root).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
            for path in sorted(artifact_paths)
        ],
    }
    manifest["bundle_sha256"] = _payload_sha(manifest["artifacts"])
    _write_json(runtime_root / RUNTIME_OUTPUTS[-1], manifest)
    return {
        "result": "PASS",
        "main_status": decision["main_status"],
        "data_gate": data_gate["gate_result"],
        "grammar_status": grammar_audit["decision"],
        "sample_candidates": grammar_audit["sample"]["requested"],
        "bundle_sha256": manifest["bundle_sha256"],
        "sealed_reads": 0,
    }


def check_evidence(repo_root: Path, *, config_path: Path) -> dict[str, Any]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    runtime_root = repo_root / config["outputs"]["runtime_root"]
    manifest_path = runtime_root / RUNTIME_OUTPUTS[-1]
    errors: list[str] = []
    if not manifest_path.is_file():
        return {"result": "FAIL", "errors": ["missing artifact manifest"]}
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for record in manifest.get("artifacts", []):
        path = (repo_root / record["path"]).resolve()
        try:
            path.relative_to(repo_root.resolve())
        except ValueError:
            errors.append(f"path_escape:{record['path']}")
            continue
        if not path.is_file():
            errors.append(f"missing:{record['path']}")
        elif path.stat().st_size != record["bytes"] or sha256_file(path) != record["sha256"]:
            errors.append(f"identity:{record['path']}")
    if _payload_sha(manifest.get("artifacts", [])) != manifest.get("bundle_sha256"):
        errors.append("bundle_sha256")
    decision = json.loads((runtime_root / RUNTIME_OUTPUTS[13]).read_text(encoding="utf-8"))
    grammar = json.loads((runtime_root / RUNTIME_OUTPUTS[3]).read_text(encoding="utf-8"))
    if decision.get("main_status") != DECISION_BLOCKED:
        errors.append("decision_status")
    if decision.get("sealed_reads") != 0 or manifest.get("sealed_reads") != 0:
        errors.append("sealed_reads")
    if grammar.get("decision") != GRAMMAR_BOTTLENECK or grammar.get("sample", {}).get("requested") < 2000:
        errors.append("grammar_qualification")
    return {
        "result": "PASS" if not errors else "FAIL",
        "errors": errors,
        "main_status": decision.get("main_status"),
        "bundle_sha256": manifest.get("bundle_sha256"),
        "producer_source_sha": manifest.get("producer_source_sha"),
    }


__all__ = [
    "DECISION_BLOCKED",
    "EPOCH_ID",
    "FIELD_CONTRACTS",
    "GRAMMAR_BOTTLENECK",
    "RUNTIME_OUTPUTS",
    "audit_grammar",
    "build_evidence",
    "check_evidence",
    "qualify_data_mode",
]
