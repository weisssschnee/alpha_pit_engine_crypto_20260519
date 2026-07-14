"""Mapping-aware strict metrics for the deterministic capability harness.

This evaluator deliberately accepts :class:`MappingResult`, not a raw weight
matrix.  Portfolio semantics must therefore be explicit before a candidate can
receive strict-feasibility evidence.

The reported 95% lower confidence bounds use an ordinary deterministic
standard error.  They do *not* correct for serial correlation or any other
form of temporal dependence.
"""

from __future__ import annotations

import math
from typing import Any, Mapping

import numpy as np

from .feedback import StrictMetrics
from .mapping import (
    CROSS_SECTIONAL_ZERO_NET,
    SPARSE_EVENT_OR_CARRY,
    TIME_SERIES_DIRECTIONAL_STATEFUL,
    MappingResult,
    portfolio_series,
)


FIXED_COST_BPS = 5.0
FIXED_BLOCK_COUNT = 4
FROZEN_WORST_BLOCK_FLOOR = -0.001
_ACTIVE_EPSILON = 1e-12

SUPPORT_PROFILES: Mapping[str, Mapping[str, Any]] = {
    CROSS_SECTIONAL_ZERO_NET: {
        "minimum_active_assets": 3,
        "cross_sectional_rank_ic": "DIAGNOSTIC_ONLY",
    },
    TIME_SERIES_DIRECTIONAL_STATEFUL: {
        "minimum_active_assets": 1,
        "cross_sectional_rank_ic": "NOT_REQUIRED",
    },
    SPARSE_EVENT_OR_CARRY: {
        "minimum_active_assets": 1,
        "cross_sectional_rank_ic": "NOT_REQUIRED",
    },
}


class CapabilityEvaluationError(ValueError):
    """A fail-closed capability-evaluator contract violation."""


def _matrix(values: np.ndarray, name: str) -> np.ndarray:
    result = np.asarray(values, dtype=float)
    if result.ndim != 2 or result.shape[1] == 0:
        raise CapabilityEvaluationError(
            f"{name} must have shape [asset,time] with nonempty time"
        )
    return result


def _vector(values: np.ndarray, size: int, name: str) -> np.ndarray:
    result = np.asarray(values, dtype=float)
    if result.ndim != 1 or result.shape[0] != size:
        raise CapabilityEvaluationError(f"{name} must have shape [time]")
    return result


def _ordinary_mean_lcb(values: np.ndarray) -> tuple[float, float, float, int]:
    clean = np.asarray(values, dtype=float)
    clean = clean[np.isfinite(clean)]
    observations = int(clean.size)
    if observations == 0:
        return float("nan"), float("nan"), float("nan"), 0
    mean = float(clean.mean())
    if observations < 2:
        return mean, float("nan"), float("nan"), observations
    standard_error = float(clean.std(ddof=1) / math.sqrt(observations))
    return mean, standard_error, mean - 1.96 * standard_error, observations


def _average_ranks(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(len(values), dtype=float)
    start = 0
    while start < len(values):
        end = start + 1
        while end < len(values) and values[order[end]] == values[order[start]]:
            end += 1
        ranks[order[start:end]] = 0.5 * (start + 1 + end)
        start = end
    return ranks


def _cross_sectional_rank_ic(
    weights: np.ndarray,
    target: np.ndarray,
    support_mask: np.ndarray,
    minimum_active_assets: int,
) -> dict[str, Any]:
    values: list[float] = []
    for column in np.flatnonzero(support_mask):
        active = (np.abs(weights[:, column]) > _ACTIVE_EPSILON) & np.isfinite(
            target[:, column]
        )
        if int(active.sum()) < minimum_active_assets:
            continue
        weight_rank = _average_ranks(weights[active, column])
        target_rank = _average_ranks(target[active, column])
        weight_centered = weight_rank - weight_rank.mean()
        target_centered = target_rank - target_rank.mean()
        denominator = float(
            np.sqrt(
                np.sum(np.square(weight_centered))
                * np.sum(np.square(target_centered))
            )
        )
        if denominator > 1e-15:
            values.append(
                float(np.sum(weight_centered * target_centered) / denominator)
            )
    return {
        "requirement": "DIAGNOSTIC_ONLY",
        "observations": len(values),
        "mean": float(np.mean(values)) if values else None,
        "values": values,
    }


def _fixed_block_metrics(
    net: np.ndarray,
    evaluation_mask: np.ndarray,
) -> tuple[list[dict[str, Any]], float, float]:
    block_rows: list[dict[str, Any]] = []
    block_means: list[float] = []
    for block_id, indices in enumerate(
        np.array_split(np.arange(net.shape[0]), FIXED_BLOCK_COUNT)
    ):
        selected = indices[evaluation_mask[indices]]
        values = net[selected]
        values = values[np.isfinite(values)]
        mean = float(values.mean()) if values.size else float("nan")
        block_means.append(mean)
        block_rows.append(
            {
                "block_id": block_id,
                "coordinate_start": int(indices[0]) if indices.size else None,
                "coordinate_stop_exclusive": int(indices[-1] + 1)
                if indices.size
                else None,
                "observations": int(values.size),
                "net_mean": mean if np.isfinite(mean) else None,
            }
        )
    finite_blocks = np.asarray(block_means, dtype=float)
    if not np.isfinite(finite_blocks).all():
        return block_rows, float("nan"), float("nan")
    return (
        block_rows,
        float(finite_blocks.min()),
        float(np.mean(finite_blocks > 0.0)),
    )


def evaluate_mapping_result(
    mapped: MappingResult,
    target_return: np.ndarray,
    benchmark_net: np.ndarray,
) -> tuple[StrictMetrics, dict[str, Any]]:
    """Evaluate one explicit mapping with the frozen capability cost contract.

    ``benchmark_net`` must already use the same time coordinate.  The function
    returns the compact feedback vector plus a JSON-serializable evidence
    dictionary.  Missing targets under nonzero positions are rejected rather
    than silently converted to zero return.
    """

    if not isinstance(mapped, MappingResult):
        raise TypeError(
            "capability evaluator accepts MappingResult only; raw weights are forbidden"
        )
    mapping_id = str(mapped.portfolio_mapping_id)
    if mapping_id not in SUPPORT_PROFILES:
        raise CapabilityEvaluationError(
            f"unsupported portfolio_mapping_id: {mapping_id}"
        )

    weights = _matrix(mapped.weights, "mapped.weights")
    if not np.isfinite(weights).all():
        raise CapabilityEvaluationError("mapped weights must be finite")
    target = _matrix(target_return, "target_return")
    if target.shape != weights.shape:
        raise CapabilityEvaluationError("weights and target_return shape mismatch")
    periods = weights.shape[1]
    feasible = np.asarray(mapped.feasible, dtype=bool)
    if feasible.ndim != 1 or feasible.shape[0] != periods:
        raise CapabilityEvaluationError("mapped.feasible must have shape [time]")
    benchmark = _vector(benchmark_net, periods, "benchmark_net")

    active = np.abs(weights) > _ACTIVE_EPSILON
    missing_under_position = active & ~np.isfinite(target)
    if np.any(missing_under_position):
        coordinates = np.argwhere(missing_under_position)
        preview = coordinates[:8].tolist()
        raise CapabilityEvaluationError(
            "TARGET_MISSING_UNDER_NONZERO_WEIGHT; "
            f"count={len(coordinates)} preview_asset_time={preview}"
        )

    profile = SUPPORT_PROFILES[mapping_id]
    minimum_active_assets = int(profile["minimum_active_assets"])
    active_count = active.sum(axis=0)
    support_mask = feasible & (active_count >= minimum_active_assets)

    path = portfolio_series(weights, target, FIXED_COST_BPS)
    gross = np.asarray(path["gross"], dtype=float)
    turnover = np.asarray(path["turnover"], dtype=float)
    cost = np.asarray(path["cost"], dtype=float)
    net = np.asarray(path["net"], dtype=float)

    # An explicit liquidation can occur on a coordinate that no longer meets
    # active-asset support.  Keep that cost in the economic path instead of
    # dropping it merely because the ending position is flat.
    evaluation_mask = support_mask | (turnover > _ACTIVE_EPSILON)
    if np.any(~np.isfinite(benchmark[evaluation_mask])):
        raise CapabilityEvaluationError(
            "benchmark_net must be finite on every evaluated coordinate"
        )

    net_mean, net_se, net_lcb, observations = _ordinary_mean_lcb(
        net[evaluation_mask]
    )
    increment = net - benchmark
    increment_mean, increment_se, increment_lcb, increment_observations = (
        _ordinary_mean_lcb(increment[evaluation_mask])
    )
    block_rows, worst_block, positive_block_fraction = _fixed_block_metrics(
        net, evaluation_mask
    )
    worst_block_margin = worst_block - FROZEN_WORST_BLOCK_FLOOR

    turnover_mean = (
        float(np.mean(turnover[evaluation_mask]))
        if np.any(evaluation_mask)
        else float("nan")
    )
    cost_mean = (
        float(np.mean(cost[evaluation_mask]))
        if np.any(evaluation_mask)
        else float("nan")
    )
    concentration = (
        float(np.mean(np.max(np.abs(weights[:, support_mask]), axis=0)))
        if np.any(support_mask)
        else float("nan")
    )
    if mapping_id == SPARSE_EVENT_OR_CARRY:
        opportunity = np.asarray(
            mapped.diagnostics.get("event_opportunity_mask", []), dtype=bool
        )
        entries = np.asarray(mapped.diagnostics.get("event_entry_mask", []), dtype=bool)
        if opportunity.shape != (periods,) or entries.shape != (periods,):
            raise CapabilityEvaluationError(
                "sparse MappingResult requires event opportunity/entry masks"
            )
        support = (
            float(np.count_nonzero(entries & opportunity) / np.count_nonzero(opportunity))
            if np.any(opportunity)
            else float("nan")
        )
        support_definition = "mapped_event_entries / eligible_event_opportunities"
    else:
        support = float(np.mean(support_mask))
        support_definition = "fraction_of_coordinates_meeting_mapping_active_asset_support"
    gross_mean, gross_se, _, gross_observations = _ordinary_mean_lcb(
        gross[evaluation_mask]
    )
    gross_std = (
        float(np.std(gross[evaluation_mask], ddof=0))
        if int(np.count_nonzero(evaluation_mask))
        else float("nan")
    )
    gross_proxy = (
        gross_mean / gross_std * math.sqrt(gross_observations)
        if gross_observations >= 2 and gross_std > 1e-15
        else float("nan")
    )

    strict_values = (
        net_lcb,
        increment_lcb,
        worst_block_margin,
        positive_block_fraction,
        turnover_mean,
        cost_mean,
        concentration,
        support,
    )
    finite = bool(
        observations >= 2
        and increment_observations >= 2
        and np.isfinite(strict_values).all()
    )
    metrics = StrictMetrics(
        mapped_net_metric=float(net_lcb),
        benchmark_increment=float(increment_lcb),
        worst_block_margin=float(worst_block_margin),
        positive_block_fraction=float(positive_block_fraction),
        turnover=float(turnover_mean),
        cost=float(cost_mean),
        concentration=float(concentration),
        support=float(support),
        gross_proxy=float(gross_proxy),
        finite=finite,
    )

    if profile["cross_sectional_rank_ic"] == "DIAGNOSTIC_ONLY":
        rank_ic: dict[str, Any] = _cross_sectional_rank_ic(
            weights, target, support_mask, minimum_active_assets
        )
    else:
        rank_ic = {
            "requirement": "NOT_REQUIRED",
            "observations": 0,
            "mean": None,
            "values": [],
        }

    details: dict[str, Any] = {
        "portfolio_mapping_id": mapping_id,
        "support_profile": {
            "minimum_active_assets": minimum_active_assets,
            "cross_sectional_rank_ic": profile["cross_sectional_rank_ic"],
        },
        "cost_model": {
            "id": "FULL_L1_FIXED_BPS",
            "cost_bps": FIXED_COST_BPS,
            "turnover_formula": "sum_i(abs(weight[i,t] - weight[i,t-1]))",
            "initial_establishment_charged": True,
        },
        "confidence_bound": {
            "method": "ordinary_standard_error",
            "quantile_multiplier": 1.96,
            "temporal_dependence_correction": False,
            "warning": "deterministic ordinary SE only; not a temporal-dependence correction",
        },
        "observations": observations,
        "evaluation_coordinates": int(np.count_nonzero(evaluation_mask)),
        "supported_coordinates": int(np.count_nonzero(support_mask)),
        "total_coordinates": periods,
        "active_asset_count": active_count.astype(int).tolist(),
        "support_mask": support_mask.tolist(),
        "evaluation_mask": evaluation_mask.tolist(),
        "mapped_net": {
            "mean": net_mean if np.isfinite(net_mean) else None,
            "standard_error": net_se if np.isfinite(net_se) else None,
            "lcb_95": net_lcb if np.isfinite(net_lcb) else None,
        },
        "benchmark_increment": {
            "mean": increment_mean if np.isfinite(increment_mean) else None,
            "standard_error": increment_se
            if np.isfinite(increment_se)
            else None,
            "lcb_95": increment_lcb if np.isfinite(increment_lcb) else None,
        },
        "fixed_blocks": {
            "count": FIXED_BLOCK_COUNT,
            "worst_floor": FROZEN_WORST_BLOCK_FLOOR,
            "worst_mean": worst_block if np.isfinite(worst_block) else None,
            "worst_margin": worst_block_margin
            if np.isfinite(worst_block_margin)
            else None,
            "positive_fraction": positive_block_fraction
            if np.isfinite(positive_block_fraction)
            else None,
            "blocks": block_rows,
        },
        "turnover_mean": turnover_mean if np.isfinite(turnover_mean) else None,
        "cost_mean": cost_mean if np.isfinite(cost_mean) else None,
        "concentration_mean_max_abs_weight": concentration
        if np.isfinite(concentration)
        else None,
        "support": support if np.isfinite(support) else None,
        "support_definition": support_definition,
        "gross": {
            "mean": gross_mean if np.isfinite(gross_mean) else None,
            "standard_error": gross_se if np.isfinite(gross_se) else None,
            "legacy_zero_cost_risk_ratio": gross_proxy
            if np.isfinite(gross_proxy)
            else None,
            "diagnostic_only": True,
        },
        "cross_sectional_rank_ic": rank_ic,
        "strict_metrics_finite": finite,
    }
    return metrics, details


__all__ = [
    "CapabilityEvaluationError",
    "FIXED_BLOCK_COUNT",
    "FIXED_COST_BPS",
    "FROZEN_WORST_BLOCK_FLOOR",
    "SUPPORT_PROFILES",
    "evaluate_mapping_result",
]
