"""Pair-native standalone and incremental-sleeve evaluation for the 18M search."""

from __future__ import annotations

import hashlib
import math
import time
from typing import Any, Mapping, Sequence

import numpy as np
import psutil

from alphafactory_crypto.instrument_capability.mapping import (
    DEFAULT_MAPPING_CONTRACTS,
    map_portfolio,
    mapping_contract_sha256,
)

from .audit import search_behavior_descriptor
from .compositional18m import CandidateSpec
from .expression import TypedExpressionRegistry, materialize_expression
from .panel18m import RawPanelStore


ACTIVE_EPSILON = 1e-12
FIXED_COST_BPS = 5.0
PAIR_THRESHOLDS: Mapping[str, float] = {
    "net_lcb": 0.0,
    "worst_month": -0.001,
    "positive_month_fraction": 0.40,
    "turnover_mean": 1.20,
    "cost_mean": 0.0006,
    "concentration_mean": 0.40,
    "support": 0.80,
}
PAIR_SCALES: Mapping[str, float] = {
    "net_lcb": 0.0001,
    "worst_month": 0.0001,
    "positive_month_fraction": 0.10,
    "turnover_mean": 0.30,
    "cost_mean": 0.0001,
    "concentration_mean": 0.10,
    "support": 0.10,
}


def _array_sha(values: np.ndarray) -> str:
    array = np.nan_to_num(np.asarray(values, dtype="<f8"), nan=9.87654321e37)
    digest = hashlib.sha256()
    digest.update(str(array.shape).encode("ascii"))
    digest.update(array.tobytes(order="C"))
    return digest.hexdigest().upper()


def _mean_lcb(
    values: np.ndarray, *, dependency_lags: int = 0
) -> tuple[float, float, float, int]:
    series = np.asarray(values, dtype=float).reshape(-1)
    finite = np.isfinite(series)
    observations = int(finite.sum())
    if observations == 0:
        return float("nan"), float("nan"), float("nan"), 0
    clean = series[finite]
    mean = float(clean.mean())
    if observations < 2:
        return mean, float("nan"), float("nan"), observations
    centered = np.where(finite, series - mean, 0.0)
    maximum_lag = min(max(0, int(dependency_lags)), int(series.size) - 1)
    long_run_variance = float(np.dot(centered, centered) / observations)
    for lag in range(1, maximum_lag + 1):
        weight = 1.0 - lag / float(maximum_lag + 1)
        valid_pairs = finite[lag:] & finite[:-lag]
        covariance = (
            float(
                np.dot(
                    centered[lag:][valid_pairs],
                    centered[:-lag][valid_pairs],
                )
                / observations
            )
            if np.any(valid_pairs)
            else 0.0
        )
        long_run_variance += 2.0 * weight * covariance
    long_run_variance *= observations / float(observations - 1)
    se = math.sqrt(max(0.0, long_run_variance) / observations)
    return mean, se, mean - 1.96 * se, observations


def _turnover(weights: np.ndarray, horizon: int) -> tuple[np.ndarray, dict[str, float]]:
    if horizon not in (1, 4):
        raise ValueError("horizon is outside the frozen 1h/4h sleeve contract")
    scale = 1.0 / float(horizon)
    previous = np.zeros_like(weights)
    if weights.shape[1] > horizon:
        previous[:, horizon:] = weights[:, :-horizon]
    current_zero = np.abs(weights) <= ACTIVE_EPSILON
    previous_zero = np.abs(previous) <= ACTIVE_EPSILON
    flip = (~current_zero) & (~previous_zero) & (np.sign(weights) != np.sign(previous))
    entry = np.where((previous_zero & ~current_zero) | flip, np.abs(weights), 0.0).sum(axis=0)
    exit_ = np.where((~previous_zero & current_zero) | flip, np.abs(previous), 0.0).sum(axis=0)
    rebalance = np.where(
        ~previous_zero & ~current_zero & ~flip, np.abs(weights - previous), 0.0
    ).sum(axis=0)
    turnover = (entry + exit_ + rebalance) * scale
    terminal = 0.0
    for offset in range(min(horizon, weights.shape[1])):
        terminal_index = weights.shape[1] - 1 - ((weights.shape[1] - 1 - offset) % horizon)
        liquidation = float(np.abs(weights[:, terminal_index]).sum()) * scale
        turnover[terminal_index] += liquidation
        terminal += liquidation
    initial = float(np.abs(weights[:, : min(horizon, weights.shape[1])]).sum()) * scale
    return turnover, {
        "initial_establishment_l1": initial,
        "entry_l1": float(entry.sum()) * scale,
        "rebalance_l1": float(rebalance.sum()) * scale,
        "transition_exit_l1": float(exit_.sum()) * scale,
        "terminal_liquidation_l1": terminal,
        "total_turnover_l1": float(turnover.sum()),
    }


def _series_metrics(
    *,
    weights: np.ndarray,
    target: np.ndarray,
    months: np.ndarray,
    evaluation_mask: np.ndarray,
    horizon: int,
) -> dict[str, Any]:
    turnover, attribution = _turnover(weights, horizon)
    gross = np.nansum(weights * target, axis=0) / float(horizon)
    cost = turnover * FIXED_COST_BPS / 10000.0
    net = gross - cost
    mask = np.asarray(evaluation_mask, dtype=bool) | (turnover > ACTIVE_EPSILON)
    dependency_lags = max(0, int(horizon) - 1)
    net_mean, net_se, net_lcb, observations = _mean_lcb(
        np.where(mask, net, np.nan),
        dependency_lags=dependency_lags,
    )
    gross_mean, _, _, _ = _mean_lcb(
        np.where(mask, gross, np.nan),
        dependency_lags=dependency_lags,
    )
    month_rows: list[dict[str, Any]] = []
    month_means: list[float] = []
    for month in tuple(dict.fromkeys(months.tolist())):
        local = mask & (months == month)
        values = net[local]
        value = float(values.mean()) if values.size else float("nan")
        month_rows.append(
            {
                "month": month,
                "observations": int(values.size),
                "gross_mean": float(gross[local].mean()) if values.size else None,
                "cost_mean": float(cost[local].mean()) if values.size else None,
                "net_mean": value if np.isfinite(value) else None,
                "turnover_mean": float(turnover[local].mean()) if values.size else None,
            }
        )
        month_means.append(value)
    finite_months = np.asarray(month_means, dtype=float)
    finite_months = finite_months[np.isfinite(finite_months)]
    (
        monthly_block_mean,
        monthly_block_se,
        monthly_block_lcb,
        monthly_block_count,
    ) = _mean_lcb(finite_months, dependency_lags=0)
    active = np.abs(weights) > ACTIVE_EPSILON
    concentration = (
        float(np.mean(np.max(np.abs(weights[:, mask]), axis=0))) if np.any(mask) else float("nan")
    )
    support = float(np.mean(evaluation_mask))
    return {
        "observations": observations,
        "net_mean": net_mean,
        "net_standard_error": net_se,
        "net_lcb": net_lcb,
        "net_standard_error_method": "NEWEY_WEST_BARTLETT",
        "net_standard_error_lags": dependency_lags,
        "monthly_block_mean": monthly_block_mean,
        "monthly_block_standard_error": monthly_block_se,
        "monthly_block_lcb": monthly_block_lcb,
        "monthly_block_count": monthly_block_count,
        "gross_mean": gross_mean,
        "turnover_mean": float(np.mean(turnover[mask])) if np.any(mask) else float("nan"),
        "cost_mean": float(np.mean(cost[mask])) if np.any(mask) else float("nan"),
        "concentration_mean": concentration,
        "support": support,
        "active_weight_fraction": float(np.mean(active)),
        "positive_month_fraction": float(np.mean(finite_months > 0.0)) if finite_months.size else float("nan"),
        "median_month": float(np.median(finite_months)) if finite_months.size else float("nan"),
        "worst_month": float(np.min(finite_months)) if finite_months.size else float("nan"),
        "month_metrics": month_rows,
        "weight_sha256": _array_sha(weights),
        "gross_series_sha256": _array_sha(gross),
        "net_series_sha256": _array_sha(net),
        **attribution,
    }


def strict_pair_feedback(metrics: Mapping[str, Any]) -> dict[str, Any]:
    values = {name: float(metrics[name]) for name in PAIR_THRESHOLDS}
    finite = all(math.isfinite(value) for value in values.values())
    if not finite:
        return {
            "blocked": True,
            "matched_positive": False,
            "distance": -11.0,
            "violations": ["NON_FINITE_STRICT_METRICS"],
        }
    margins = {
        "net_lcb": (values["net_lcb"] - PAIR_THRESHOLDS["net_lcb"]) / PAIR_SCALES["net_lcb"],
        "worst_month": (values["worst_month"] - PAIR_THRESHOLDS["worst_month"]) / PAIR_SCALES["worst_month"],
        "positive_month_fraction": (values["positive_month_fraction"] - PAIR_THRESHOLDS["positive_month_fraction"]) / PAIR_SCALES["positive_month_fraction"],
        "turnover_mean": (PAIR_THRESHOLDS["turnover_mean"] - values["turnover_mean"]) / PAIR_SCALES["turnover_mean"],
        "cost_mean": (PAIR_THRESHOLDS["cost_mean"] - values["cost_mean"]) / PAIR_SCALES["cost_mean"],
        "concentration_mean": (PAIR_THRESHOLDS["concentration_mean"] - values["concentration_mean"]) / PAIR_SCALES["concentration_mean"],
        "support": (values["support"] - PAIR_THRESHOLDS["support"]) / PAIR_SCALES["support"],
    }
    clipped = {name: max(-10.0, min(10.0, value)) for name, value in margins.items()}
    violations = [name.upper() for name, value in clipped.items() if value < 0.0]
    return {
        "blocked": False,
        "matched_positive": not violations,
        "distance": min(clipped.values()),
        "violations": violations,
        "normalized_margins": clipped,
    }


def evaluate_pair(
    *,
    store: RawPanelStore,
    registry: TypedExpressionRegistry,
    candidate: CandidateSpec,
    block_start: str,
    block_end: str,
    block_role: str,
    behavior_contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    timings: dict[str, float] = {}
    process = psutil.Process()
    rss_samples = [process.memory_info().rss]
    private_samples = [getattr(process.memory_info(), "private", rss_samples[0])]

    def sample_memory() -> None:
        memory = process.memory_info()
        rss_samples.append(int(memory.rss))
        private_samples.append(int(getattr(memory, "private", memory.rss)))

    block = store.block_slice(block_start, block_end)
    base = np.asarray(store.base_eligible()[:, block], dtype=bool)
    read_started = time.perf_counter()
    raw = {
        field: np.asarray(store.field(field)[:, block], dtype=float)
        for field in candidate.raw_fields
    }
    timings["field_read_seconds"] = time.perf_counter() - read_started
    sample_memory()
    support = base.copy()
    for values in raw.values():
        support &= np.isfinite(values)
    materialize_started = time.perf_counter()
    # Primary and ablation control deliberately share their unchanged DAG
    # subtrees.  Reusing those immutable arrays preserves exact semantics and
    # avoids recomputing the matched support/normalization path twice.
    candidate_cache: dict[str, np.ndarray] = {}
    primary_signal = materialize_expression(
        candidate.expression,
        registry=registry,
        field_reader=raw.__getitem__,
        eligible_mask=base,
        candidate_cache=candidate_cache,
    )
    control_signal = materialize_expression(
        candidate.control,
        registry=registry,
        field_reader=raw.__getitem__,
        eligible_mask=base,
        candidate_cache=candidate_cache,
    )
    primary_signal = np.where(support, primary_signal, np.nan)
    control_signal = np.where(support, control_signal, np.nan)
    timings["dag_materialization_seconds"] = time.perf_counter() - materialize_started
    sample_memory()
    mapping_started = time.perf_counter()
    mapping_contract = DEFAULT_MAPPING_CONTRACTS[candidate.mapping_id]
    primary_mapped = map_portfolio(primary_signal, mapping_contract)
    control_mapped = map_portfolio(control_signal, mapping_contract)
    timings["mapping_seconds"] = time.perf_counter() - mapping_started
    sample_memory()
    primary_weight = np.asarray(primary_mapped.weights, dtype=float)
    control_weight = np.asarray(control_mapped.weights, dtype=float)
    if candidate.expression.expression_id == candidate.control.expression_id:
        raise ValueError("CONTROL_EXACT_IDENTITY_EQUALS_PRIMARY")
    if np.array_equal(primary_weight, control_weight):
        raise ValueError("CONTROL_BEHAVIOR_EQUALS_PRIMARY")
    target = np.asarray(store.target_return(candidate.horizon_hours)[:, block], dtype=float)
    active_union = (np.abs(primary_weight) > ACTIVE_EPSILON) | (
        np.abs(control_weight) > ACTIVE_EPSILON
    )
    missing_active_target = np.any(active_union & ~np.isfinite(target), axis=0)
    raw_coordinate_support = support.sum(axis=0) >= 3
    evaluation_mask = raw_coordinate_support & ~missing_active_target
    if not np.any(evaluation_mask):
        raise ValueError("DYNAMIC_UNIVERSE_SUPPORT_COLLAPSE")
    timestamp_ns = store.timestamp_ns[block]
    months = np.asarray(
        [str(np.datetime64(int(value), "ns"))[:7] for value in timestamp_ns], dtype=str
    )
    standalone_started = time.perf_counter()
    primary = _series_metrics(
        weights=primary_weight,
        target=target,
        months=months,
        evaluation_mask=evaluation_mask,
        horizon=candidate.horizon_hours,
    )
    control = _series_metrics(
        weights=control_weight,
        target=target,
        months=months,
        evaluation_mask=evaluation_mask,
        horizon=candidate.horizon_hours,
    )
    timings["standalone_evaluator_seconds"] = time.perf_counter() - standalone_started
    sample_memory()
    incremental_started = time.perf_counter()
    delta_weight = primary_weight - control_weight
    incremental = _series_metrics(
        weights=delta_weight,
        target=target,
        months=months,
        evaluation_mask=evaluation_mask,
        horizon=candidate.horizon_hours,
    )
    feedback = strict_pair_feedback(incremental)
    timings["incremental_sleeve_seconds"] = time.perf_counter() - incremental_started
    sample_memory()
    behavior = None
    if behavior_contract is not None:
        behavior_started = time.perf_counter()
        regime_values = np.asarray(
            store.field(str(behavior_contract["pit_regime_source"]))[:, block],
            dtype=float,
        )
        behavior = search_behavior_descriptor(
            signal=primary_signal,
            weights=primary_weight,
            eligible_mask=support,
            month_labels=months,
            timestamp_ns=timestamp_ns,
            active_universe_size=regime_values,
            horizon_hours=candidate.horizon_hours,
            mapping_id=candidate.mapping_id,
            contract=behavior_contract,
        )
        timings["behavior_descriptor_seconds"] = (
            time.perf_counter() - behavior_started
        )
        sample_memory()
    timings["peak_rss_bytes"] = float(max(rss_samples))
    timings["peak_private_bytes"] = float(max(private_samples))
    support_overlap = 1.0
    return {
        "candidate_id": candidate.candidate_id,
        "skeleton_id": candidate.skeleton_id,
        "mechanism_family": candidate.mechanism_family,
        "horizon_hours": candidate.horizon_hours,
        "mapping_id": candidate.mapping_id,
        "mapping_hash": mapping_contract_sha256(mapping_contract),
        "block_role": block_role,
        "block_start": block_start,
        "block_end_exclusive": block_end,
        "raw_fields": list(candidate.raw_fields),
        "field_families": list(candidate.field_families),
        "operator_path": candidate.operator_path,
        "expression_id": candidate.expression.expression_id,
        "control_expression_id": candidate.control.expression_id,
        "support_overlap": support_overlap,
        "raw_support_coordinates": int(raw_coordinate_support.sum()),
        "missing_active_target_coordinates": int(missing_active_target.sum()),
        "primary": primary,
        "control": control,
        "incremental": incremental,
        "scalar_net_delta_diagnostic": float(primary["net_mean"] - control["net_mean"]),
        "pair_reward": float(feedback["distance"]),
        "matched_positive": bool(feedback["matched_positive"]),
        "feedback": feedback,
        "behavior": behavior,
        "primary_control_weight_equal": False,
        "delta_weight_sha256": incremental["weight_sha256"],
        "timings": timings,
    }


def pair_contract_payload() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "pair_authority": "PRIMARY_CONTROL_WITH_INCREMENTAL_DELTA_WEIGHT_SLEEVE",
        "lcb_contract": {
            "authority": "NEWEY_WEST_BARTLETT",
            "dependency_lags": "horizon_hours_minus_one",
            "confidence_multiplier": 1.96,
            "monthly_block_lcb": "DIAGNOSTIC_ONLY",
        },
        "match_on": [
            "raw inputs",
            "timestamps",
            "dynamic eligibility",
            "target horizon",
            "mapping family and position cap",
            "5 bps full-L1 cost model",
            "raw support",
        ],
        "control_rule": "remove exactly one registered core mechanism while SupportMatchedPayload retains the removed input in support",
        "support_overlap_required": 1.0,
        "control_exact_identity_forbidden": True,
        "control_behavior_identity_forbidden": True,
        "optional_behavior_identity": "FROZEN_OUTCOME_FREE_DESCRIPTOR_V1",
        "incremental_weight_formula": "primary_weight - control_weight",
        "incremental_turnover": "recomputed independently from delta weights",
        "standalone_scalar_delta_role": "DIAGNOSTIC_ONLY",
    }


def feedback_contract_payload() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "authoritative_feedback": "incremental sleeve strict feasibility distance",
        "thresholds": dict(PAIR_THRESHOLDS),
        "normalization_scales": dict(PAIR_SCALES),
        "feedback_block": "2023-07-01/2024-07-01 development adaptive block only",
        "report_only_block": "2024-07-01/2025-01-01 development report-only block",
        "report_only_metrics_visible_to_policy": False,
        "control_has_independent_vote": False,
        "control_has_adaptive_memory": False,
    }


def robust_monthly_audit(
    month_values: Sequence[float], *, seed: int, bootstrap_draws: int = 1000
) -> dict[str, Any]:
    values = np.asarray(month_values, dtype=float)
    values = values[np.isfinite(values)]
    if values.size < 3:
        return {
            "months": int(values.size),
            "hac_standard_error": None,
            "hac_lcb": None,
            "moving_block_bootstrap_p05": None,
            "moving_block_bootstrap_p50": None,
            "robust_positive": False,
        }
    centered = values - values.mean()
    lag = min(2, values.size - 1)
    variance = float(np.dot(centered, centered) / values.size)
    for offset in range(1, lag + 1):
        covariance = float(np.dot(centered[offset:], centered[:-offset]) / values.size)
        variance += 2.0 * (1.0 - offset / (lag + 1.0)) * covariance
    hac_se = math.sqrt(max(variance, 0.0) / values.size)
    hac_lcb = float(values.mean() - 1.96 * hac_se)
    rng = np.random.default_rng(seed)
    block_length = 2
    draws = np.empty(bootstrap_draws, dtype=float)
    starts = np.arange(values.size)
    for draw in range(bootstrap_draws):
        sampled: list[float] = []
        while len(sampled) < values.size:
            start = int(rng.choice(starts))
            sampled.extend(values[(start + step) % values.size] for step in range(block_length))
        draws[draw] = float(np.mean(sampled[: values.size]))
    p05, p50 = np.quantile(draws, [0.05, 0.50])
    return {
        "months": int(values.size),
        "hac_standard_error": hac_se,
        "hac_lcb": hac_lcb,
        "moving_block_bootstrap_p05": float(p05),
        "moving_block_bootstrap_p50": float(p50),
        "robust_positive": bool(hac_lcb > 0.0 and p05 > 0.0),
    }


__all__ = [
    "FIXED_COST_BPS",
    "PAIR_THRESHOLDS",
    "evaluate_pair",
    "feedback_contract_payload",
    "pair_contract_payload",
    "robust_monthly_audit",
    "strict_pair_feedback",
]
