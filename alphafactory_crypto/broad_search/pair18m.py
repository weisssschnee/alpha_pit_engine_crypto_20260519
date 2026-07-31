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

from .audit import search_behavior_descriptor, turnover_path
from .compositional18m import CandidateSpec
from .expression import Expression, TypedExpressionRegistry, materialize_expression
from .panel18m import RawPanelStore


ACTIVE_EPSILON = 1e-12
FIXED_COST_BPS = 5.0
SEARCH_REWARD_AUTHORITY = "CRYPTO_TRAIN_JOINT_PRIMARY_MATCHED_SORTINO_V2"
SEARCH_REWARD_COMPONENT_AUTHORITY = "CRYPTO_TRAIN_PORTFOLIO_SORTINO_COMPONENT_V2"
SEARCH_REWARD_UNCERTAINTY_CONTRACT = (
    "CRYPTO_ORDERED_DAY_STATIONARY_BOOTSTRAP_V1"
)
SEARCH_REWARD_BOOTSTRAP_DRAWS = 600
SEARCH_REWARD_BOOTSTRAP_SUPPORT_MINIMUM = 0.60
SEARCH_REWARD_WEIGHTS: Mapping[str, float] = {
    # Preserve the V1 effective 0.55 + duplicated 0.25 day-Sortino weight
    # without retaining a false second-horizon claim.
    "train_day_sortino": 0.80,
    "train_day_bootstrap_sortino_p25": 0.20,
}
SEARCH_REWARD_TURNOVER_PENALTY_START = 0.55
SEARCH_REWARD_TURNOVER_PENALTY_WEIGHT = 0.75
# Private compatibility name for the qualification evaluator.  It is an alias,
# not a second implementation; audit.turnover_path remains the sole authority.
_turnover = turnover_path
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


def _sortino(values: np.ndarray) -> float:
    clean = np.asarray(values, dtype=float).reshape(-1)
    clean = clean[np.isfinite(clean)]
    if clean.size == 0:
        return float("nan")
    downside = np.minimum(clean, 0.0)
    downside_scale = float(np.sqrt(np.mean(downside * downside)))
    if downside_scale <= 1.0e-18:
        return float("nan")
    return float(np.mean(clean) / downside_scale)


def _daily_net_returns(
    net: np.ndarray,
    mask: np.ndarray,
    timestamp_ns: np.ndarray | None,
) -> np.ndarray:
    values = np.asarray(net, dtype=float).reshape(-1)
    active = np.asarray(mask, dtype=bool).reshape(-1) & np.isfinite(values)
    if timestamp_ns is None:
        return values[active]
    timestamps = np.asarray(timestamp_ns, dtype=np.int64).reshape(-1)
    if timestamps.shape != values.shape:
        raise ValueError("timestamp_ns does not match the evaluated return path")
    day_labels = timestamps.astype("datetime64[ns]").astype("datetime64[D]")
    daily: list[float] = []
    for day in np.unique(day_labels[active]):
        local = active & (day_labels == day)
        if np.any(local):
            daily.append(float(np.sum(values[local])))
    return np.asarray(daily, dtype=float)


def _stationary_bootstrap_indices(
    observation_count: int,
    *,
    seed: int,
    draws: int,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Return deterministic ordered-day stationary-bootstrap indices.

    The restart probability is frozen from the observed day count.  This is a
    dependence-aware bootstrap, not MCMC and not a Bayesian posterior.
    """

    count = int(observation_count)
    requested_draws = int(draws)
    if count <= 0 or requested_draws <= 0:
        return np.empty((0, 0), dtype=np.int64), {
            "contract": SEARCH_REWARD_UNCERTAINTY_CONTRACT,
            "method": "STATIONARY_BOOTSTRAP",
            "seed": int(seed),
            "requested_draws": max(0, requested_draws),
            "observation_count": max(0, count),
            "expected_block_length": 0,
            "restart_probability": float("nan"),
        }
    expected_block_length = (
        1
        if count == 1
        else min(20, max(2, int(round(count ** (1.0 / 3.0)))))
    )
    restart_probability = 1.0 / float(expected_block_length)
    rng = np.random.default_rng(int(seed))
    indices = np.empty((requested_draws, count), dtype=np.int64)
    indices[:, 0] = rng.integers(0, count, size=requested_draws, dtype=np.int64)
    if count > 1:
        restart = rng.random((requested_draws, count - 1)) < restart_probability
        restart_at = rng.integers(
            0,
            count,
            size=(requested_draws, count - 1),
            dtype=np.int64,
        )
        for column in range(1, count):
            continued = (indices[:, column - 1] + 1) % count
            indices[:, column] = np.where(
                restart[:, column - 1],
                restart_at[:, column - 1],
                continued,
            )
    return indices, {
        "contract": SEARCH_REWARD_UNCERTAINTY_CONTRACT,
        "method": "STATIONARY_BOOTSTRAP",
        "seed": int(seed),
        "requested_draws": requested_draws,
        "observation_count": count,
        "expected_block_length": expected_block_length,
        "restart_probability": restart_probability,
    }


def _bootstrap_sortino(
    day_values: np.ndarray,
    *,
    seed: int,
    draws: int,
    shared_indices: np.ndarray | None = None,
    shared_metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    clean = np.asarray(day_values, dtype=float).reshape(-1)
    clean = clean[np.isfinite(clean)]
    if clean.size == 0 or int(draws) <= 0:
        return {
            "draws": 0,
            "requested_draws": max(0, int(draws)),
            "invalid_draws": max(0, int(draws)),
            "p25": float("nan"),
            "median": float("nan"),
            "probability_gt_zero": float("nan"),
            "monte_carlo_standard_error": float("nan"),
            "uncertainty_contract": SEARCH_REWARD_UNCERTAINTY_CONTRACT,
        }
    if shared_indices is None:
        indices, metadata = _stationary_bootstrap_indices(
            clean.size,
            seed=int(seed),
            draws=int(draws),
        )
    else:
        indices = np.asarray(shared_indices, dtype=np.int64)
        metadata = dict(shared_metadata or {})
        if indices.shape != (int(draws), clean.size):
            raise ValueError("shared stationary-bootstrap path shape changed")
        if np.any(indices < 0) or np.any(indices >= clean.size):
            raise ValueError("shared stationary-bootstrap path is out of bounds")
    samples = clean[indices]
    means = np.mean(samples, axis=1)
    downside = np.minimum(samples, 0.0)
    scales = np.sqrt(np.mean(downside * downside, axis=1))
    finite = np.isfinite(means) & np.isfinite(scales) & (scales > 1.0e-18)
    sortinos = means[finite] / scales[finite]
    mean_support = float(np.mean(means > 0.0)) if means.size else float("nan")
    monte_carlo_standard_error = (
        math.sqrt(mean_support * (1.0 - mean_support) / float(means.size))
        if means.size and math.isfinite(mean_support)
        else float("nan")
    )
    if sortinos.size == 0:
        return {
            "draws": 0,
            "requested_draws": int(indices.shape[0]),
            "invalid_draws": int(indices.shape[0]),
            "p25": float("nan"),
            "median": float("nan"),
            "probability_gt_zero": mean_support,
            "monte_carlo_standard_error": monte_carlo_standard_error,
            "uncertainty_contract": SEARCH_REWARD_UNCERTAINTY_CONTRACT,
            **metadata,
        }
    return {
        "draws": int(sortinos.size),
        "requested_draws": int(indices.shape[0]),
        "invalid_draws": int(indices.shape[0] - sortinos.size),
        "p05": float(np.quantile(sortinos, 0.05)),
        "p25": float(np.quantile(sortinos, 0.25)),
        "median": float(np.quantile(sortinos, 0.50)),
        "p75": float(np.quantile(sortinos, 0.75)),
        "p95": float(np.quantile(sortinos, 0.95)),
        "probability_gt_zero": mean_support,
        "monte_carlo_standard_error": monte_carlo_standard_error,
        "uncertainty_contract": SEARCH_REWARD_UNCERTAINTY_CONTRACT,
        **metadata,
    }


def _portfolio_search_reward(
    *,
    net: np.ndarray,
    turnover_l1: np.ndarray,
    mask: np.ndarray,
    timestamp_ns: np.ndarray,
    seed: int,
    shared_indices: np.ndarray | None = None,
    shared_metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return one crypto train-portfolio component of the joint objective."""

    daily = _daily_net_returns(net, mask, timestamp_ns)
    day_sortino = _sortino(daily)
    bootstrap = _bootstrap_sortino(
        daily,
        seed=int(seed),
        draws=SEARCH_REWARD_BOOTSTRAP_DRAWS,
        shared_indices=shared_indices,
        shared_metadata=shared_metadata,
    )
    bootstrap_p25 = float(bootstrap["p25"])
    active_turnover = np.asarray(turnover_l1, dtype=float)[np.asarray(mask, dtype=bool)]
    mean_full_l1_turnover = (
        float(np.mean(active_turnover)) if active_turnover.size else float("nan")
    )
    # For a dollar-neutral book, one-way turnover is exactly half the full-L1
    # weight change.  Phase3CM charges both long and short sleeves, which makes
    # 2 * one-way turnover * one-side cost identical to full-L1 * one-side cost.
    mean_one_way_turnover = 0.5 * mean_full_l1_turnover
    day_component = day_sortino if math.isfinite(day_sortino) else -2.0
    bootstrap_component = bootstrap_p25 if math.isfinite(bootstrap_p25) else -2.0
    turnover_penalty = (
        max(
            0.0,
            mean_one_way_turnover - SEARCH_REWARD_TURNOVER_PENALTY_START,
        )
        * SEARCH_REWARD_TURNOVER_PENALTY_WEIGHT
        if math.isfinite(mean_one_way_turnover)
        else 2.0
    )
    reward = (
        SEARCH_REWARD_WEIGHTS["train_day_sortino"] * day_component
        + SEARCH_REWARD_WEIGHTS["train_day_bootstrap_sortino_p25"]
        * bootstrap_component
        - turnover_penalty
    )
    blockers: list[str] = []
    if not math.isfinite(day_sortino) or day_sortino <= 0.0:
        blockers.append("NON_POSITIVE_TRAIN_DAY_SORTINO")
    if (
        not math.isfinite(float(bootstrap["probability_gt_zero"]))
        or float(bootstrap["probability_gt_zero"])
        < SEARCH_REWARD_BOOTSTRAP_SUPPORT_MINIMUM
    ):
        blockers.append("WEAK_TRAIN_DAY_STATIONARY_BOOTSTRAP")
    if not math.isfinite(reward) or reward <= 0.0:
        blockers.append("NON_POSITIVE_TRAIN_SEARCH_REWARD")
    return {
        "authority": SEARCH_REWARD_COMPONENT_AUTHORITY,
        "uncertainty_contract": SEARCH_REWARD_UNCERTAINTY_CONTRACT,
        "search_reward": float(reward),
        "train_day_sortino": day_sortino,
        "train_worst_horizon_day_sortino": None,
        "train_day_bootstrap_sortino_p25": bootstrap_p25,
        "train_day_bootstrap_sortino_median": float(bootstrap["median"]),
        "train_day_bootstrap_probability_gt_zero": float(
            bootstrap["probability_gt_zero"]
        ),
        "train_day_bootstrap_draws": int(bootstrap["draws"]),
        "train_day_bootstrap_requested_draws": int(
            bootstrap["requested_draws"]
        ),
        "train_day_bootstrap_invalid_draws": int(bootstrap["invalid_draws"]),
        "train_day_bootstrap_expected_block_length": int(
            bootstrap.get("expected_block_length", 0)
        ),
        "train_day_bootstrap_restart_probability": float(
            bootstrap.get("restart_probability", float("nan"))
        ),
        "train_day_bootstrap_monte_carlo_standard_error": float(
            bootstrap["monte_carlo_standard_error"]
        ),
        "train_day_count": int(daily.size),
        "mean_full_l1_turnover": mean_full_l1_turnover,
        "mean_one_way_turnover": mean_one_way_turnover,
        "turnover_penalty": float(turnover_penalty),
        "horizon_scope": "CANDIDATE_SELECTED_SINGLE_HORIZON",
        "worst_horizon_term_removed": True,
        "cross_horizon_instability_penalty": 0.0,
        "inherited_blocker_penalty": 0.0,
        "blockers": blockers,
    }


def _joint_portfolio_search_reward(
    *,
    components: Mapping[str, Mapping[str, np.ndarray]],
    timestamp_ns: np.ndarray,
    seed: int,
) -> dict[str, Any]:
    """Conservatively join primary quality with all required matched sleeves."""

    if "primary" not in components or len(components) < 2:
        raise ValueError("joint search reward requires primary and matched components")
    ordered_names = tuple(components)
    common_mask = np.zeros(np.asarray(timestamp_ns).shape, dtype=bool)
    for name in ordered_names:
        local = components[name]
        common_mask |= np.asarray(local["mask"], dtype=bool)
    day_count: int | None = None
    for name in ordered_names:
        local = components[name]
        daily = _daily_net_returns(
            np.asarray(local["net"], dtype=float),
            common_mask,
            np.asarray(timestamp_ns, dtype=np.int64),
        )
        if day_count is None:
            day_count = int(daily.size)
        elif int(daily.size) != day_count:
            raise ValueError("joint reward components lost shared ordered-day support")
    shared_indices, shared_metadata = _stationary_bootstrap_indices(
        int(day_count or 0),
        seed=int(seed),
        draws=SEARCH_REWARD_BOOTSTRAP_DRAWS,
    )
    objectives: dict[str, dict[str, Any]] = {}
    for name in ordered_names:
        local = components[name]
        objectives[name] = _portfolio_search_reward(
            net=np.asarray(local["net"], dtype=float),
            turnover_l1=np.asarray(local["turnover"], dtype=float),
            mask=common_mask,
            timestamp_ns=np.asarray(timestamp_ns, dtype=np.int64),
            seed=int(seed),
            shared_indices=shared_indices,
            shared_metadata=shared_metadata,
        )
    limiting_component = min(
        ordered_names,
        key=lambda name: (float(objectives[name]["search_reward"]), name),
    )
    matched_names = tuple(name for name in ordered_names if name != "primary")
    matched_limiting_component = min(
        matched_names,
        key=lambda name: (float(objectives[name]["search_reward"]), name),
    )
    blockers = [
        f"{name}:{blocker}"
        for name in ordered_names
        for blocker in objectives[name]["blockers"]
    ]
    primary = objectives["primary"]
    return {
        "authority": SEARCH_REWARD_AUTHORITY,
        "component_authority": SEARCH_REWARD_COMPONENT_AUTHORITY,
        "uncertainty_contract": SEARCH_REWARD_UNCERTAINTY_CONTRACT,
        "joint_rule": "MIN_PRIMARY_AND_ALL_REQUIRED_MATCHED_COMPONENTS",
        "search_reward": float(
            objectives[limiting_component]["search_reward"]
        ),
        "primary_search_reward": float(primary["search_reward"]),
        "matched_min_search_reward": float(
            objectives[matched_limiting_component]["search_reward"]
        ),
        "limiting_component": limiting_component,
        "matched_limiting_component": matched_limiting_component,
        "component_order": list(ordered_names),
        "component_objectives": objectives,
        "shared_stationary_bootstrap_path_sha256": _array_sha(shared_indices),
        "shared_ordered_day_count": int(day_count or 0),
        "train_day_sortino": primary["train_day_sortino"],
        "train_worst_horizon_day_sortino": None,
        "train_day_bootstrap_sortino_p25": primary[
            "train_day_bootstrap_sortino_p25"
        ],
        "train_day_bootstrap_sortino_median": primary[
            "train_day_bootstrap_sortino_median"
        ],
        "train_day_bootstrap_probability_gt_zero": primary[
            "train_day_bootstrap_probability_gt_zero"
        ],
        "train_day_bootstrap_draws": primary["train_day_bootstrap_draws"],
        "train_day_bootstrap_requested_draws": primary[
            "train_day_bootstrap_requested_draws"
        ],
        "train_day_bootstrap_invalid_draws": primary[
            "train_day_bootstrap_invalid_draws"
        ],
        "train_day_bootstrap_expected_block_length": primary[
            "train_day_bootstrap_expected_block_length"
        ],
        "train_day_bootstrap_restart_probability": primary[
            "train_day_bootstrap_restart_probability"
        ],
        "train_day_bootstrap_monte_carlo_standard_error": primary[
            "train_day_bootstrap_monte_carlo_standard_error"
        ],
        "train_day_count": primary["train_day_count"],
        "mean_full_l1_turnover": primary["mean_full_l1_turnover"],
        "mean_one_way_turnover": primary["mean_one_way_turnover"],
        "turnover_penalty": primary["turnover_penalty"],
        "horizon_scope": "CANDIDATE_SELECTED_SINGLE_HORIZON",
        "worst_horizon_term_removed": True,
        "cross_horizon_instability_penalty": 0.0,
        "inherited_blocker_penalty": 0.0,
        "feedback_eligible": not blockers,
        "blockers": blockers,
    }


def _series_metrics(
    *,
    weights: np.ndarray,
    target: np.ndarray,
    months: np.ndarray,
    evaluation_mask: np.ndarray,
    horizon: int,
    cost_bps: float = FIXED_COST_BPS,
    timestamp_ns: np.ndarray | None = None,
    search_reward_seed: int | None = None,
    include_internal_objective_paths: bool = False,
) -> dict[str, Any]:
    turnover, attribution = turnover_path(weights, horizon)
    gross = np.nansum(weights * target, axis=0) / float(horizon)
    cost = turnover * float(cost_bps) / 10000.0
    net = gross - cost
    mask = np.asarray(evaluation_mask, dtype=bool) | (turnover > ACTIVE_EPSILON)
    dependency_lags = max(0, int(horizon) - 1)
    net_mean, net_se, net_lcb, observations = _mean_lcb(
        np.where(mask, net, np.nan),
        dependency_lags=dependency_lags,
    )
    gross_mean, gross_se, gross_lcb, gross_observations = _mean_lcb(
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
    metrics = {
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
        "gross_standard_error": gross_se,
        "gross_lcb": gross_lcb,
        "gross_observations": gross_observations,
        "turnover_mean": float(np.mean(turnover[mask])) if np.any(mask) else float("nan"),
        "cost_mean": float(np.mean(cost[mask])) if np.any(mask) else float("nan"),
        "cost_bps": float(cost_bps),
        "concentration_mean": concentration,
        "support": support,
        "active_weight_fraction": float(np.mean(active)),
        "positive_month_fraction": float(np.mean(finite_months > 0.0)) if finite_months.size else float("nan"),
        "median_month": float(np.median(finite_months)) if finite_months.size else float("nan"),
        "worst_month": float(np.min(finite_months)) if finite_months.size else float("nan"),
        "month_metrics": month_rows,
        "weight_sha256": _array_sha(weights),
        "turnover_path_sha256": _array_sha(turnover),
        "gross_series_sha256": _array_sha(gross),
        "net_series_sha256": _array_sha(net),
        **attribution,
    }
    if search_reward_seed is not None:
        if timestamp_ns is None:
            raise ValueError("search reward requires explicit timestamps")
        metrics["portfolio_search_objective"] = _portfolio_search_reward(
            net=net,
            turnover_l1=turnover,
            mask=mask,
            timestamp_ns=np.asarray(timestamp_ns, dtype=np.int64),
            seed=int(search_reward_seed),
        )
    if include_internal_objective_paths:
        metrics["_objective_net_path"] = net
        metrics["_objective_turnover_path"] = turnover
        metrics["_objective_mask"] = mask
    return metrics


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
    economic_receipt: Mapping[str, Any] | None = None,
    frozen_train_orientation: float | None = None,
    include_validation_paths: bool = False,
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
    if hasattr(store, "candidate_support"):
        support = store.candidate_support(candidate.raw_fields, block)
    else:
        # Lightweight test/probe stores predate the explicit carrier method.
        # Preserve the exact candidate-local semantics without requiring them
        # to impersonate the full RawPanelStore API.
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
    if len(candidate.expression.inputs) != 2:
        raise ValueError("DUAL_AXIS_CONTROL_REQUIRES_BINARY_PRIMARY")
    hierarchical_conditional = candidate.mechanism_family.startswith(
        "CONDITIONAL_"
    )
    interaction_left_control_expression = None
    if hierarchical_conditional:
        interaction, condition = candidate.expression.inputs
        if (
            candidate.expression.operator != "StateModulation"
            or interaction.operator != "RatioInteraction"
            or len(interaction.inputs) != 2
        ):
            raise ValueError("HIERARCHICAL_CONDITIONAL_DAG_CHANGED")
        expected_ab_control = Expression(
            "SupportMatchedPayload", (interaction, condition)
        )
        if candidate.control.expression_id != expected_ab_control.expression_id:
            raise ValueError("HIERARCHICAL_AB_CONTROL_CHANGED")
        left_axis, right_axis = interaction.inputs
        interaction_left_control_expression = Expression(
            "SupportMatchedPayload",
            (
                left_axis,
                Expression("SupportMatchedPayload", (right_axis, condition)),
            ),
        )
        right_control_expression = Expression(
            "SupportMatchedPayload",
            (
                right_axis,
                Expression("SupportMatchedPayload", (left_axis, condition)),
            ),
        )
    else:
        right_control_expression = Expression(
            "SupportMatchedPayload",
            (candidate.expression.inputs[1], candidate.expression.inputs[0]),
        )
    right_control_assurance = registry.validate(right_control_expression)
    if set(right_control_assurance.raw_fields) != set(candidate.raw_fields):
        raise ValueError("RIGHT_AXIS_CONTROL_CHANGED_RAW_INPUT_CONTRACT")
    right_control_signal = materialize_expression(
        right_control_expression,
        registry=registry,
        field_reader=raw.__getitem__,
        eligible_mask=base,
        candidate_cache=candidate_cache,
    )
    interaction_left_control_signal = None
    if interaction_left_control_expression is not None:
        interaction_left_assurance = registry.validate(
            interaction_left_control_expression
        )
        if set(interaction_left_assurance.raw_fields) != set(
            candidate.raw_fields
        ):
            raise ValueError("INTERACTION_LEFT_CONTROL_CHANGED_RAW_INPUT_CONTRACT")
        interaction_left_control_signal = materialize_expression(
            interaction_left_control_expression,
            registry=registry,
            field_reader=raw.__getitem__,
            eligible_mask=base,
            candidate_cache=candidate_cache,
        )
    primary_signal = np.where(support, primary_signal, np.nan)
    control_signal = np.where(support, control_signal, np.nan)
    right_control_signal = np.where(support, right_control_signal, np.nan)
    if interaction_left_control_signal is not None:
        interaction_left_control_signal = np.where(
            support, interaction_left_control_signal, np.nan
        )
    timings["dag_materialization_seconds"] = time.perf_counter() - materialize_started
    sample_memory()
    target = np.asarray(
        store.target_return(candidate.horizon_hours)[:, block],
        dtype=float,
    )
    mapping_started = time.perf_counter()
    mapping_contract = DEFAULT_MAPPING_CONTRACTS[candidate.mapping_id]
    train_orientation = 1.0
    train_orientation_fitted = False
    evaluation_partition = "legacy"
    evaluation_cost_bps = FIXED_COST_BPS
    if economic_receipt is not None:
        receipt = dict(economic_receipt)
        train = dict(receipt.get("train") or {})
        validation = dict(receipt.get("validation") or {})
        portfolio = dict(receipt.get("portfolio") or {})
        direction = dict(receipt.get("direction") or {})
        cost_contract = dict(receipt.get("cost") or {})
        execution = dict(receipt.get("execution") or {})
        if direction.get("rule") != "TRAIN_FROZEN_SIGN_ORIENTATION":
            raise ValueError("ECONOMIC_RECEIPT_DIRECTION_RULE_CHANGED")
        if candidate.mapping_id != portfolio.get("mapping_id"):
            raise ValueError("ECONOMIC_RECEIPT_MAPPING_CHANGED")
        target_metadata = getattr(store, "target_metadata", None)
        if not isinstance(target_metadata, Mapping):
            raise ValueError("ECONOMIC_RECEIPT_TARGET_STORE_NOT_BOUND")
        for field in (
            "venue",
            "source",
            "price_field",
            "formula",
            "execution_delay_hours",
            "horizons_hours",
            "positive_price_required",
            "missing_value_fill",
            "target_cache_identity_sha256",
        ):
            observed = (
                target_metadata.get("identity_sha256")
                if field == "target_cache_identity_sha256"
                else target_metadata.get(field)
            )
            if observed != execution.get(field):
                raise ValueError(
                    f"ECONOMIC_RECEIPT_TARGET_CONTRACT_CHANGED:{field}"
                )
        is_train = (
            str(block_start) == str(train.get("start"))
            and str(block_end) == str(train.get("end_exclusive"))
        )
        is_validation = (
            str(block_start) == str(validation.get("start"))
            and str(block_end) == str(validation.get("end_exclusive"))
            and str(block_role) == str(validation.get("role"))
        )
        evaluation_cost_bps = float(cost_contract["cost_bps"])
        if is_train:
            if frozen_train_orientation is not None:
                raise ValueError(
                    "ECONOMIC_RECEIPT_TRAIN_MUST_FIT_ORIENTATION"
                )
            positive_mapped = map_portfolio(primary_signal, mapping_contract)
            negative_mapped = map_portfolio(-primary_signal, mapping_contract)
            positive_weight = np.asarray(positive_mapped.weights, dtype=float)
            negative_weight = np.asarray(negative_mapped.weights, dtype=float)
            positive_turnover, _ = turnover_path(
                positive_weight,
                candidate.horizon_hours,
            )
            negative_turnover, _ = turnover_path(
                negative_weight,
                candidate.horizon_hours,
            )
            positive_cost = positive_turnover * evaluation_cost_bps / 10_000.0
            negative_cost = negative_turnover * evaluation_cost_bps / 10_000.0
            active_union = (
                (np.abs(positive_weight) > ACTIVE_EPSILON)
                | (np.abs(negative_weight) > ACTIVE_EPSILON)
            )
            orientation_mask = (
                (support.sum(axis=0) >= 3)
                & ~np.any(active_union & ~np.isfinite(target), axis=0)
            )
            if not np.any(orientation_mask):
                raise ValueError(
                    "ECONOMIC_RECEIPT_ORIENTATION_SUPPORT_COLLAPSE"
                )
            from scripts.crypto_a7reward1_portfolio_reward_model import (
                select_train_orientation,
            )

            train_orientation = select_train_orientation(
                (
                    positive_weight,
                    positive_cost,
                    primary_signal,
                    positive_turnover,
                ),
                (
                    negative_weight,
                    negative_cost,
                    -primary_signal,
                    negative_turnover,
                ),
                target,
                orientation_mask,
            )
            train_orientation_fitted = True
            evaluation_partition = "train"
        elif is_validation:
            if any(
                validation.get(field) is not False
                for field in (
                    "optimizer_feedback_allowed",
                    "policy_memory_write_allowed",
                    "candidate_generation_allowed",
                )
            ):
                raise ValueError(
                    "ECONOMIC_RECEIPT_VALIDATION_WRITE_BOUNDARY_CHANGED"
                )
            allowed = {
                float(value)
                for value in direction.get("allowed_values", (-1.0, 1.0))
            }
            if (
                frozen_train_orientation is None
                or float(frozen_train_orientation) not in allowed
            ):
                raise ValueError(
                    "ECONOMIC_RECEIPT_VALIDATION_REQUIRES_FROZEN_ORIENTATION"
                )
            train_orientation = float(frozen_train_orientation)
            evaluation_partition = "validation"
        else:
            raise ValueError("ECONOMIC_RECEIPT_EVALUATION_BLOCK_CHANGED")
        primary_signal = primary_signal * train_orientation
        control_signal = control_signal * train_orientation
        right_control_signal = right_control_signal * train_orientation
        if interaction_left_control_signal is not None:
            interaction_left_control_signal = (
                interaction_left_control_signal * train_orientation
            )
    primary_mapped = map_portfolio(primary_signal, mapping_contract)
    control_mapped = map_portfolio(control_signal, mapping_contract)
    right_control_mapped = map_portfolio(right_control_signal, mapping_contract)
    interaction_left_control_mapped = (
        map_portfolio(interaction_left_control_signal, mapping_contract)
        if interaction_left_control_signal is not None
        else None
    )
    timings["mapping_seconds"] = time.perf_counter() - mapping_started
    sample_memory()
    primary_weight = np.asarray(primary_mapped.weights, dtype=float)
    control_weight = np.asarray(control_mapped.weights, dtype=float)
    right_control_weight = np.asarray(right_control_mapped.weights, dtype=float)
    interaction_left_control_weight = (
        np.asarray(interaction_left_control_mapped.weights, dtype=float)
        if interaction_left_control_mapped is not None
        else None
    )
    if candidate.expression.expression_id == candidate.control.expression_id:
        raise ValueError("CONTROL_EXACT_IDENTITY_EQUALS_PRIMARY")
    if np.array_equal(primary_weight, control_weight):
        raise ValueError("CONTROL_BEHAVIOR_EQUALS_PRIMARY")
    if np.array_equal(primary_weight, right_control_weight):
        raise ValueError("RIGHT_AXIS_CONTROL_BEHAVIOR_EQUALS_PRIMARY")
    if (
        interaction_left_control_weight is not None
        and np.array_equal(control_weight, interaction_left_control_weight)
    ):
        raise ValueError("INTERACTION_LEFT_CONTROL_BEHAVIOR_EQUALS_AB")
    active_union = (
        (np.abs(primary_weight) > ACTIVE_EPSILON)
        | (np.abs(control_weight) > ACTIVE_EPSILON)
        | (np.abs(right_control_weight) > ACTIVE_EPSILON)
    )
    if interaction_left_control_weight is not None:
        active_union |= np.abs(interaction_left_control_weight) > ACTIVE_EPSILON
    missing_active_target = np.any(active_union & ~np.isfinite(target), axis=0)
    raw_coordinate_support = support.sum(axis=0) >= 3
    evaluation_mask = raw_coordinate_support & ~missing_active_target
    if not np.any(evaluation_mask):
        raise ValueError("DYNAMIC_UNIVERSE_SUPPORT_COLLAPSE")
    timestamp_ns = store.timestamp_ns[block]
    months = np.asarray(
        [str(np.datetime64(int(value), "ns"))[:7] for value in timestamp_ns], dtype=str
    )
    search_reward_seed = int.from_bytes(
        hashlib.sha256(
            (
                f"{SEARCH_REWARD_AUTHORITY}|{candidate.candidate_id}|"
                f"{block_start}|{block_end}|{block_role}"
            ).encode("utf-8")
        ).digest()[:8],
        "little",
        signed=False,
    )
    standalone_started = time.perf_counter()
    primary = _series_metrics(
        weights=primary_weight,
        target=target,
        months=months,
        evaluation_mask=evaluation_mask,
        horizon=candidate.horizon_hours,
        cost_bps=evaluation_cost_bps,
        timestamp_ns=timestamp_ns,
        include_internal_objective_paths=True,
    )
    control = _series_metrics(
        weights=control_weight,
        target=target,
        months=months,
        evaluation_mask=evaluation_mask,
        horizon=candidate.horizon_hours,
        cost_bps=evaluation_cost_bps,
        include_internal_objective_paths=include_validation_paths,
    )
    right_control = _series_metrics(
        weights=right_control_weight,
        target=target,
        months=months,
        evaluation_mask=evaluation_mask,
        horizon=candidate.horizon_hours,
        cost_bps=evaluation_cost_bps,
        include_internal_objective_paths=include_validation_paths,
    )
    interaction_left_control = (
        _series_metrics(
            weights=interaction_left_control_weight,
            target=target,
            months=months,
            evaluation_mask=evaluation_mask,
            horizon=candidate.horizon_hours,
            cost_bps=evaluation_cost_bps,
            include_internal_objective_paths=include_validation_paths,
        )
        if interaction_left_control_weight is not None
        else None
    )
    timings["standalone_evaluator_seconds"] = time.perf_counter() - standalone_started
    sample_memory()
    incremental_started = time.perf_counter()
    left_delta_weight = primary_weight - control_weight
    right_delta_weight = (
        control_weight - right_control_weight
        if hierarchical_conditional
        else primary_weight - right_control_weight
    )
    left_incremental = _series_metrics(
        weights=left_delta_weight,
        target=target,
        months=months,
        evaluation_mask=evaluation_mask,
        horizon=candidate.horizon_hours,
        cost_bps=evaluation_cost_bps,
        include_internal_objective_paths=True,
    )
    right_incremental = _series_metrics(
        weights=right_delta_weight,
        target=target,
        months=months,
        evaluation_mask=evaluation_mask,
        horizon=candidate.horizon_hours,
        cost_bps=evaluation_cost_bps,
        include_internal_objective_paths=True,
    )
    left_feedback = strict_pair_feedback(left_incremental)
    right_feedback = strict_pair_feedback(right_incremental)
    interaction_left_incremental = None
    interaction_left_feedback = None
    if hierarchical_conditional:
        assert interaction_left_control_weight is not None
        interaction_left_incremental = _series_metrics(
            weights=control_weight - interaction_left_control_weight,
            target=target,
            months=months,
            evaluation_mask=evaluation_mask,
            horizon=candidate.horizon_hours,
            cost_bps=evaluation_cost_bps,
            include_internal_objective_paths=True,
        )
        interaction_left_feedback = strict_pair_feedback(
            interaction_left_incremental
        )
        authoritative = min(
            (
                interaction_left_feedback,
                right_feedback,
                left_feedback,
            ),
            key=lambda item: float(item["distance"]),
        )
        feedback = {
            **authoritative,
            "dual_axis": False,
            "hierarchical_three_axis": True,
            "interaction_left_axis": interaction_left_feedback,
            "interaction_right_axis": right_feedback,
            "conditional_axis": left_feedback,
            "left_axis": left_feedback,
            "right_axis": right_feedback,
            "interaction_matched_positive": bool(
                interaction_left_feedback["matched_positive"]
                and right_feedback["matched_positive"]
            ),
            "conditional_matched_positive": bool(
                left_feedback["matched_positive"]
            ),
            "matched_positive": bool(
                interaction_left_feedback["matched_positive"]
                and right_feedback["matched_positive"]
                and left_feedback["matched_positive"]
            ),
            "distance": float(
                min(
                    interaction_left_feedback["distance"],
                    right_feedback["distance"],
                    left_feedback["distance"],
                )
            ),
        }
    else:
        feedback = {
            **(
                left_feedback
                if float(left_feedback["distance"])
                <= float(right_feedback["distance"])
                else right_feedback
            ),
            "dual_axis": True,
            "left_axis": left_feedback,
            "right_axis": right_feedback,
            "matched_positive": bool(
                left_feedback["matched_positive"]
                and right_feedback["matched_positive"]
            ),
            "distance": float(
                min(left_feedback["distance"], right_feedback["distance"])
            ),
        }
    if include_validation_paths and evaluation_partition != "validation":
        raise ValueError("VALIDATION_PATHS_REQUIRE_VALIDATION_PARTITION")
    validation_paths: dict[str, Any] | None = None
    if include_validation_paths:
        validation_paths = {
            "primary_net": np.where(
                np.asarray(primary["_objective_mask"], dtype=bool),
                np.asarray(primary["_objective_net_path"], dtype=float),
                np.nan,
            ),
            "control_net": {},
            "matched_component_net": {},
        }
        control_sections = {
            "left": control,
            "right": right_control,
        }
        if interaction_left_control is not None:
            control_sections["interaction_left"] = interaction_left_control
        for name, section in control_sections.items():
            validation_paths["control_net"][name] = np.where(
                np.asarray(section.pop("_objective_mask"), dtype=bool),
                np.asarray(section.pop("_objective_net_path"), dtype=float),
                np.nan,
            )
            section.pop("_objective_turnover_path")

    objective_components: dict[str, dict[str, np.ndarray]] = {}
    component_metrics: list[tuple[str, dict[str, Any]]]
    if hierarchical_conditional:
        assert interaction_left_incremental is not None
        component_metrics = [
            ("primary", primary),
            ("interaction_ab_minus_a", interaction_left_incremental),
            ("interaction_ab_minus_b", right_incremental),
            ("conditional_abc_minus_ab", left_incremental),
        ]
    else:
        component_metrics = [
            ("primary", primary),
            ("primary_minus_left_control", left_incremental),
            ("primary_minus_right_control", right_incremental),
        ]
    for name, metrics in component_metrics:
        if validation_paths is not None and name != "primary":
            validation_paths["matched_component_net"][name] = np.where(
                np.asarray(metrics["_objective_mask"], dtype=bool),
                np.asarray(metrics["_objective_net_path"], dtype=float),
                np.nan,
            )
        objective_components[name] = {
            "net": np.asarray(metrics.pop("_objective_net_path"), dtype=float),
            "turnover": np.asarray(
                metrics.pop("_objective_turnover_path"), dtype=float
            ),
            "mask": np.asarray(metrics.pop("_objective_mask"), dtype=bool),
        }
    search_objective = _joint_portfolio_search_reward(
        components=objective_components,
        timestamp_ns=timestamp_ns,
        seed=search_reward_seed,
    )
    primary["portfolio_search_objective"] = search_objective
    timings["incremental_sleeve_seconds"] = time.perf_counter() - incremental_started
    sample_memory()
    behavior = None
    if behavior_contract is not None:
        behavior_started = time.perf_counter()
        regime_source = str(behavior_contract["pit_regime_source"])
        if regime_source == "__BASE_ELIGIBLE_COUNT__":
            counts = base.sum(axis=0, dtype=np.int64).astype(float)
            regime_values = np.broadcast_to(counts, base.shape).copy()
        else:
            regime_values = np.asarray(
                store.field(regime_source)[:, block],
                dtype=float,
            )
        descriptor_kwargs = {
            "eligible_mask": support,
            "month_labels": months,
            "timestamp_ns": timestamp_ns,
            "active_universe_size": regime_values,
            "horizon_hours": candidate.horizon_hours,
            "mapping_id": candidate.mapping_id,
            "contract": behavior_contract,
        }
        primary_behavior = search_behavior_descriptor(
            signal=primary_signal,
            weights=primary_weight,
            **descriptor_kwargs,
        )
        control_behavior = search_behavior_descriptor(
            signal=control_signal,
            weights=control_weight,
            **descriptor_kwargs,
        )
        right_control_behavior = search_behavior_descriptor(
            signal=right_control_signal,
            weights=right_control_weight,
            **descriptor_kwargs,
        )
        interaction_left_control_behavior = (
            search_behavior_descriptor(
                signal=interaction_left_control_signal,
                weights=interaction_left_control_weight,
                **descriptor_kwargs,
            )
            if interaction_left_control_signal is not None
            and interaction_left_control_weight is not None
            else None
        )
        left_incremental_behavior = search_behavior_descriptor(
            signal=primary_signal - control_signal,
            weights=left_delta_weight,
            **descriptor_kwargs,
        )
        right_incremental_behavior = search_behavior_descriptor(
            signal=(
                control_signal - right_control_signal
                if hierarchical_conditional
                else primary_signal - right_control_signal
            ),
            weights=right_delta_weight,
            **descriptor_kwargs,
        )
        behavior = {
            **left_incremental_behavior,
            "primary_behavior_id": primary_behavior["behavior_family_id"],
            "control_behavior_id": control_behavior["behavior_family_id"],
            "right_control_behavior_id": right_control_behavior[
                "behavior_family_id"
            ],
            "left_incremental_behavior_id": left_incremental_behavior[
                "behavior_family_id"
            ],
            "right_incremental_behavior_id": right_incremental_behavior[
                "behavior_family_id"
            ],
            "incremental_behavior_id": left_incremental_behavior[
                "behavior_family_id"
            ],
            "interaction_left_control_behavior_id": (
                interaction_left_control_behavior["behavior_family_id"]
                if interaction_left_control_behavior is not None
                else None
            ),
            "identity_authority": (
                "ABC_MINUS_AB_CONDITIONAL_DELTA_WEIGHT_V1"
                if hierarchical_conditional
                else "LEFT_AXIS_INCREMENTAL_DELTA_WEIGHT_V1"
            ),
        }
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
        "cost_bps": float(evaluation_cost_bps),
        "train_orientation": float(train_orientation),
        "train_orientation_fitted": bool(train_orientation_fitted),
        "evaluation_partition": evaluation_partition,
        "economic_receipt_sha256": (
            str(economic_receipt.get("receipt_sha256"))
            if economic_receipt is not None
            else None
        ),
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
        "left_control": control,
        "right_control": right_control,
        "incremental": left_incremental,
        "left_incremental": left_incremental,
        "right_incremental": right_incremental,
        "hierarchical_three_axis": hierarchical_conditional,
        "interaction_left_control": interaction_left_control,
        "interaction_right_control": (
            right_control if hierarchical_conditional else None
        ),
        "interaction_left_incremental": interaction_left_incremental,
        "interaction_right_incremental": (
            right_incremental if hierarchical_conditional else None
        ),
        "conditional_incremental": (
            left_incremental if hierarchical_conditional else None
        ),
        "scalar_net_delta_diagnostic": float(primary["net_mean"] - control["net_mean"]),
        "search_reward": float(search_objective["search_reward"]),
        "search_reward_authority": SEARCH_REWARD_AUTHORITY,
        "search_reward_feedback": search_objective,
        "pair_reward": float(feedback["distance"]),
        "matched_positive": bool(feedback["matched_positive"]),
        "feedback": feedback,
        "behavior": behavior,
        "primary_control_weight_equal": False,
        "delta_weight_sha256": left_incremental["weight_sha256"],
        "left_delta_weight_sha256": left_incremental["weight_sha256"],
        "right_delta_weight_sha256": right_incremental["weight_sha256"],
        "interaction_left_delta_weight_sha256": (
            interaction_left_incremental["weight_sha256"]
            if interaction_left_incremental is not None
            else None
        ),
        "timings": timings,
        **(
            {"_validation_paths": validation_paths}
            if validation_paths is not None
            else {}
        ),
    }


def pair_contract_payload() -> dict[str, Any]:
    return {
        "schema_version": 3,
        "pair_authority": "PRIMARY_WITH_LEFT_AND_RIGHT_AXIS_INCREMENTAL_DELTA_WEIGHT_SLEEVES",
        "market_semantics": {
            "asset_class": "CRYPTO",
            "calendar": "CONTINUOUS_UTC",
            "a_share_constraints_applied": False,
            "forbidden_cross_market_constraints": [
                "A_SHARE_T_PLUS_ONE",
                "A_SHARE_ST",
                "A_SHARE_PRICE_LIMIT",
                "A_SHARE_STAMP_DUTY",
                "A_SHARE_SUSPENSION_CALENDAR",
            ],
        },
        "search_objective": {
            "authority": SEARCH_REWARD_AUTHORITY,
            "component_authority": SEARCH_REWARD_COMPONENT_AUTHORITY,
            "portfolio": (
                "minimum of primary mapped portfolio and every required "
                "matched incremental delta-weight sleeve"
            ),
            "split": "train/development adaptive block only",
            "formula_weights": dict(SEARCH_REWARD_WEIGHTS),
            "uncertainty_contract": SEARCH_REWARD_UNCERTAINTY_CONTRACT,
            "stationary_bootstrap_draws": SEARCH_REWARD_BOOTSTRAP_DRAWS,
            "stationary_bootstrap_support_minimum": (
                SEARCH_REWARD_BOOTSTRAP_SUPPORT_MINIMUM
            ),
            "shared_resample_path": (
                "primary and matched components use one deterministic "
                "ordered-day stationary-bootstrap index path"
            ),
            "turnover_penalty_start_one_way": SEARCH_REWARD_TURNOVER_PENALTY_START,
            "turnover_penalty_weight": SEARCH_REWARD_TURNOVER_PENALTY_WEIGHT,
            "selected_horizon_scope": (
                "CandidateSpec freezes one horizon; the duplicate nominal "
                "worst-horizon term is removed rather than counted twice"
            ),
            "validation_role": (
                "not implemented by Search Engine V1; an explicit fresh "
                "validation split and kill-line are required before another "
                "adaptive market campaign"
            ),
            "holdout_role": (
                "not read by Search Engine V1 and must remain read-only"
            ),
        },
        "lcb_contract": {
            "authority": "NEWEY_WEST_BARTLETT",
            "dependency_lags": "horizon_hours_minus_one",
            "confidence_multiplier": 1.96,
            "gross_lcb_role": "DIAGNOSTIC_ONLY",
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
        "control_rule": "compare the primary independently with left-only and right-only SupportMatchedPayload controls; both retain identical raw support",
        "support_overlap_required": 1.0,
        "control_exact_identity_forbidden": True,
        "control_behavior_identity_forbidden": True,
        "optional_behavior_identity": "FROZEN_OUTCOME_FREE_DESCRIPTOR_V1",
        "incremental_weight_formula": "primary_weight - each_axis_control_weight",
        "pair_reward_role": (
            "matched attribution and execution diagnostic; never proposal-policy, "
            "elite, parent, archive-champion, or arm-exit ordering authority"
        ),
        "pair_reward": "minimum strict feasibility distance across left and right incremental sleeves",
        "hierarchical_three_axis_extension": {
            "dag": "ABC=StateModulation(AB,C); AB=RatioInteraction(A,B)",
            "shared_contract": "raw support, target, timestamps, eligibility, horizon, mapping, and cost are identical for A, B, AB, and ABC",
            "interaction_gate": "AB_minus_A and AB_minus_B must both pass",
            "conditional_gate": "ABC_minus_AB must pass",
            "pair_reward": "minimum strict feasibility distance across AB-A, AB-B, and ABC-AB",
            "behavior_identity": "ABC_minus_AB incremental delta weight",
        },
        "incremental_turnover": "recomputed independently from delta weights",
        "standalone_scalar_delta_role": "DIAGNOSTIC_ONLY",
    }


def feedback_contract_payload() -> dict[str, Any]:
    return {
        "schema_version": 3,
        "authoritative_search_feedback": SEARCH_REWARD_AUTHORITY,
        "matched_attribution_feedback": "incremental sleeve strict feasibility distance",
        "matched_attribution_is_search_ordering_authority": False,
        "matched_incremental_portfolio_quality_is_search_ordering_authority": True,
        "joint_ordering_rule": "minimum primary and all required matched component rewards",
        "uncertainty_contract": SEARCH_REWARD_UNCERTAINTY_CONTRACT,
        "thresholds": dict(PAIR_THRESHOLDS),
        "normalization_scales": dict(PAIR_SCALES),
        "feedback_block": "2023-07-01/2024-07-01 development adaptive block only",
        "report_only_block": "2024-07-01/2025-01-01 development report-only block",
        "report_only_block_is_formal_validation": False,
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
