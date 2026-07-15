"""Frozen train-only strict evaluator for the real-data instrument canary."""

from __future__ import annotations

import hashlib
import math
from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

from alphafactory_crypto.instrument_capability.feedback import StrictMetrics
from alphafactory_crypto.instrument_capability.mapping import (
    CROSS_SECTIONAL_ZERO_NET,
    DEFAULT_MAPPING_CONTRACTS,
    SPARSE_EVENT_OR_CARRY,
    MappingResult,
    map_portfolio,
    mapping_contract_sha256,
)


FIXED_COST_BPS = 5.0
FROZEN_WORST_BLOCK_FLOOR = -0.001
ACTIVE_EPSILON = 1e-12
FROZEN_DEVELOPMENT_MONTHS = (
    "2024-01",
    "2024-02",
    "2024-03",
    "2024-04",
    "2024-05",
    "2024-06",
)


def array_sha256(values: np.ndarray) -> str:
    array = np.asarray(values, dtype=np.float64)
    normalized = np.where(np.isnan(array), np.nan, array).astype("<f8", copy=False)
    digest = hashlib.sha256()
    digest.update(str(normalized.shape).encode("ascii"))
    digest.update(normalized.tobytes(order="C"))
    return digest.hexdigest().upper()


@dataclass(frozen=True)
class StrictEvaluation:
    metrics: StrictMetrics
    mapping_id: str
    observations: int
    target_horizon_hours: int
    net_mean: float
    net_standard_error: float
    net_lcb: float
    gross_mean: float
    benchmark_id: str
    benchmark_net_mean: float
    increment_lcb: float
    block_metrics: tuple[dict[str, Any], ...]
    turnover_mean: float
    cost_mean: float
    concentration_mean: float
    support: float
    execution_model_id: str
    overlapping_sleeves: int
    initial_establishment_l1: float
    subsequent_entry_l1: float
    rebalance_l1: float
    transition_exit_l1: float
    terminal_liquidation_l1: float
    total_turnover_l1: float
    total_cost: float
    signal_sha256: str
    weight_sha256: str
    target_sha256: str
    cross_sectional_rank_ic_mean: float | None
    lcb_warning: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["metrics"] = asdict(self.metrics)
        payload["block_metrics"] = list(self.block_metrics)
        return payload


def _mean_lcb(values: np.ndarray) -> tuple[float, float, float, int]:
    clean = np.asarray(values, dtype=float)
    clean = clean[np.isfinite(clean)]
    if clean.size == 0:
        return float("nan"), float("nan"), float("nan"), 0
    mean = float(clean.mean())
    if clean.size < 2:
        return mean, float("nan"), float("nan"), int(clean.size)
    se = float(clean.std(ddof=1) / math.sqrt(clean.size))
    return mean, se, mean - 1.96 * se, int(clean.size)


def _turnover_parts(
    weights: np.ndarray, *, overlapping_sleeves: int
) -> dict[str, np.ndarray | float]:
    """Full-L1 turnover for equal-capital, horizon-offset execution sleeves.

    A horizon-h signal is interpreted as h independent sleeves.  Sleeve s is
    rebalanced only at coordinates t where t mod h == s and receives 1/h of
    capital.  This prevents overlapping h-hour targets from being paired with
    an impossible full-capital hourly rebalance.
    """

    if overlapping_sleeves <= 0:
        raise ValueError("overlapping_sleeves must be positive")
    scale = 1.0 / float(overlapping_sleeves)
    previous = np.zeros_like(weights)
    if weights.shape[1] > overlapping_sleeves:
        previous[:, overlapping_sleeves:] = weights[:, :-overlapping_sleeves]
    current_zero = np.abs(weights) <= ACTIVE_EPSILON
    previous_zero = np.abs(previous) <= ACTIVE_EPSILON
    sign_flip = (~current_zero) & (~previous_zero) & (np.sign(weights) != np.sign(previous))
    entry = np.where((previous_zero & ~current_zero) | sign_flip, np.abs(weights), 0.0).sum(axis=0)
    transition_exit = np.where(
        (~previous_zero & current_zero) | sign_flip, np.abs(previous), 0.0
    ).sum(axis=0)
    rebalance = np.where(
        ~previous_zero & ~current_zero & ~sign_flip,
        np.abs(weights - previous),
        0.0,
    ).sum(axis=0)
    turnover = (entry + transition_exit + rebalance) * scale
    initial_coordinates = min(overlapping_sleeves, weights.shape[1])
    initial = (
        float(np.abs(weights[:, :initial_coordinates]).sum()) * scale
        if initial_coordinates
        else 0.0
    )
    entry_total = float(entry.sum()) * scale
    terminal = 0.0
    if turnover.size:
        for offset in range(min(overlapping_sleeves, weights.shape[1])):
            terminal_index = weights.shape[1] - 1 - (
                (weights.shape[1] - 1 - offset) % overlapping_sleeves
            )
            liquidation = float(np.abs(weights[:, terminal_index]).sum()) * scale
            turnover[terminal_index] += liquidation
            terminal += liquidation
    return {
        "turnover": turnover,
        "initial": initial,
        "subsequent_entry": entry_total - initial,
        "rebalance": float(rebalance.sum()) * scale,
        "transition_exit": float(transition_exit.sum()) * scale,
        "terminal": terminal,
    }


def _aggregate_sleeve_positions(weights: np.ndarray, sleeves: int) -> np.ndarray:
    """Return the concurrent equal-capital portfolio implied by sleeve entries."""

    aggregate = np.zeros_like(weights)
    live = np.zeros((sleeves, weights.shape[0]), dtype=float)
    scale = 1.0 / float(sleeves)
    for column in range(weights.shape[1]):
        live[column % sleeves] = weights[:, column]
        aggregate[:, column] = live.sum(axis=0) * scale
    return aggregate


def _average_ranks(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(len(values), dtype=float)
    start = 0
    while start < len(values):
        stop = start + 1
        while stop < len(values) and values[order[stop]] == values[order[start]]:
            stop += 1
        ranks[order[start:stop]] = 0.5 * (start + 1 + stop)
        start = stop
    return ranks


def _rank_ic(weights: np.ndarray, target: np.ndarray) -> float | None:
    values: list[float] = []
    for column in range(weights.shape[1]):
        active = (np.abs(weights[:, column]) > ACTIVE_EPSILON) & np.isfinite(target[:, column])
        if int(active.sum()) < 3:
            continue
        a = _average_ranks(weights[active, column])
        b = _average_ranks(target[active, column])
        a -= a.mean()
        b -= b.mean()
        denominator = float(np.sqrt(np.square(a).sum() * np.square(b).sum()))
        if denominator > 1e-15:
            values.append(float(np.sum(a * b) / denominator))
    return float(np.mean(values)) if values else None


def evaluate_real_mapping(
    mapped: MappingResult,
    signal: np.ndarray,
    target_return: np.ndarray,
    month_labels: np.ndarray,
    *,
    target_horizon_hours: int,
    expected_mapping_id: str | None = None,
    expected_months: tuple[str, ...] | None = None,
) -> StrictEvaluation:
    if not isinstance(mapped, MappingResult):
        raise TypeError("strict evaluator accepts MappingResult only")
    if mapped.portfolio_mapping_id not in DEFAULT_MAPPING_CONTRACTS:
        raise ValueError("mapping result is outside canonical mapping authority")
    if expected_mapping_id is not None and mapped.portfolio_mapping_id != expected_mapping_id:
        raise ValueError("mapping result does not match authorized mechanism family")
    canonical_mapping_hash = mapping_contract_sha256(
        DEFAULT_MAPPING_CONTRACTS[mapped.portfolio_mapping_id]
    )
    if mapped.contract_sha256 != canonical_mapping_hash:
        raise ValueError("mapping result contract hash is not canonical")
    weights = np.asarray(mapped.weights, dtype=float)
    signal_array = np.asarray(signal, dtype=float)
    target = np.asarray(target_return, dtype=float)
    months = np.asarray(month_labels, dtype=str)
    if weights.ndim != 2 or weights.shape != signal_array.shape or weights.shape != target.shape:
        raise ValueError("signal, mapping and target shapes must match")
    if months.shape != (weights.shape[1],):
        raise ValueError("month labels must match the time axis")
    observed_month_order = tuple(dict.fromkeys(months.tolist()))
    if tuple(sorted(observed_month_order)) != observed_month_order:
        raise ValueError("development month labels are not chronological/contiguous")
    if expected_months is not None and observed_month_order != tuple(expected_months):
        raise ValueError("development evaluation blocks are incomplete or changed")
    if not np.isfinite(weights).all():
        raise ValueError("mapped weights must be finite")
    valid_time = np.isfinite(target).all(axis=0)
    if not np.any(valid_time):
        raise ValueError("target has no complete development coordinate")
    last_valid = int(np.flatnonzero(valid_time)[-1]) + 1
    if not valid_time[:last_valid].all() or valid_time[last_valid:].any():
        raise ValueError("target validity must be one contiguous development prefix")
    weights = weights[:, :last_valid]
    signal_array = signal_array[:, :last_valid]
    target = target[:, :last_valid]
    months = months[:last_valid]
    feasible = np.asarray(mapped.feasible, dtype=bool)[:last_valid]

    active_count = (np.abs(weights) > ACTIVE_EPSILON).sum(axis=0)
    minimum_assets = 3 if mapped.portfolio_mapping_id == CROSS_SECTIONAL_ZERO_NET else 1
    support_mask = feasible & (active_count >= minimum_assets)
    sleeves = int(target_horizon_hours)
    if sleeves not in (1, 4):
        raise ValueError("target horizon is outside the frozen sleeve contract")
    turnover_parts = _turnover_parts(weights, overlapping_sleeves=sleeves)
    turnover = np.asarray(turnover_parts["turnover"], dtype=float)
    # Each interleaved sleeve owns 1/h of capital.  Its h-hour target is booked
    # once at the sleeve entry coordinate; across coordinates this is a
    # non-overlapping capital-accounting representation.
    gross = np.sum(weights * target, axis=0) / float(sleeves)
    cost = turnover * FIXED_COST_BPS / 10_000.0
    net = gross - cost
    evaluation_mask = support_mask | (turnover > ACTIVE_EPSILON)
    if not np.any(evaluation_mask):
        raise ValueError("mapping produced no evaluable development coordinate")

    net_mean, net_se, net_lcb, observations = _mean_lcb(net[evaluation_mask])
    gross_mean, _, _, gross_observations = _mean_lcb(gross[evaluation_mask])
    # The predeclared common benchmark is explicit no-trade on the identical
    # development coordinates.  It is an execution reference, not an alpha hurdle.
    benchmark_net = np.zeros_like(net)
    _, _, increment_lcb, _ = _mean_lcb((net - benchmark_net)[evaluation_mask])

    block_rows: list[dict[str, Any]] = []
    block_means: list[float] = []
    for month in sorted(set(months.tolist())):
        mask = evaluation_mask & (months == month)
        values = net[mask]
        mean = float(values.mean()) if values.size else float("nan")
        block_rows.append(
            {
                "block_id": f"DEV_TRAIN_{month.replace('-', '_')}",
                "month": month,
                "observations": int(values.size),
                "net_mean": mean if np.isfinite(mean) else None,
            }
        )
        block_means.append(mean)
    finite_blocks = np.asarray(block_means, dtype=float)
    if not np.isfinite(finite_blocks).all():
        worst_block_margin = float("nan")
        positive_block_fraction = float("nan")
    else:
        worst_block_margin = float(finite_blocks.min() - FROZEN_WORST_BLOCK_FLOOR)
        positive_block_fraction = float(np.mean(finite_blocks > 0.0))

    concurrent_weights = _aggregate_sleeve_positions(weights, sleeves)
    concentration = float(np.mean(np.max(np.abs(concurrent_weights[:, support_mask]), axis=0))) if np.any(support_mask) else float("nan")
    if mapped.portfolio_mapping_id == SPARSE_EVENT_OR_CARRY:
        opportunity = np.asarray(mapped.diagnostics.get("event_opportunity_mask", []), dtype=bool)[:last_valid]
        entries = np.asarray(mapped.diagnostics.get("event_entry_mask", []), dtype=bool)[:last_valid]
        if opportunity.shape != (last_valid,) or entries.shape != (last_valid,):
            raise ValueError("sparse mapping lacks event opportunity/entry diagnostics")
        support = float(np.count_nonzero(entries & opportunity) / np.count_nonzero(opportunity)) if np.any(opportunity) else float("nan")
    else:
        support = float(np.mean(support_mask))
    turnover_mean = float(np.mean(turnover[evaluation_mask]))
    cost_mean = float(np.mean(cost[evaluation_mask]))
    gross_std = float(np.std(gross[evaluation_mask], ddof=0))
    gross_proxy = (
        gross_mean / gross_std * math.sqrt(gross_observations)
        if gross_observations >= 2 and gross_std > 1e-15
        else float("nan")
    )
    attributed_turnover = math.fsum(
        (
            float(turnover_parts["initial"]),
            float(turnover_parts["subsequent_entry"]),
            float(turnover_parts["rebalance"]),
            float(turnover_parts["transition_exit"]),
            float(turnover_parts["terminal"]),
        )
    )
    if not math.isclose(
        attributed_turnover,
        float(turnover.sum()),
        rel_tol=1e-12,
        abs_tol=1e-12,
    ):
        raise AssertionError("turnover attribution does not close to full L1 total")
    strict_values = (
        net_lcb,
        increment_lcb,
        worst_block_margin,
        positive_block_fraction,
        turnover_mean,
        cost_mean,
        concentration,
        support,
        gross_proxy,
    )
    metrics = StrictMetrics(*strict_values, finite=bool(all(np.isfinite(v) for v in strict_values)))
    return StrictEvaluation(
        metrics=metrics,
        mapping_id=mapped.portfolio_mapping_id,
        observations=observations,
        target_horizon_hours=int(target_horizon_hours),
        net_mean=net_mean,
        net_standard_error=net_se,
        net_lcb=net_lcb,
        gross_mean=gross_mean,
        benchmark_id="NO_TRADE_SAME_DEVELOPMENT_COORDINATES",
        benchmark_net_mean=0.0,
        increment_lcb=increment_lcb,
        block_metrics=tuple(block_rows),
        turnover_mean=turnover_mean,
        cost_mean=cost_mean,
        concentration_mean=concentration,
        support=support,
        execution_model_id="EQUAL_CAPITAL_HORIZON_OFFSET_SLEEVES",
        overlapping_sleeves=sleeves,
        initial_establishment_l1=float(turnover_parts["initial"]),
        subsequent_entry_l1=float(turnover_parts["subsequent_entry"]),
        rebalance_l1=float(turnover_parts["rebalance"]),
        transition_exit_l1=float(turnover_parts["transition_exit"]),
        terminal_liquidation_l1=float(turnover_parts["terminal"]),
        total_turnover_l1=float(turnover.sum()),
        total_cost=float(cost.sum()),
        signal_sha256=array_sha256(signal_array),
        weight_sha256=array_sha256(weights),
        target_sha256=array_sha256(target),
        cross_sectional_rank_ic_mean=(
            _rank_ic(weights, target)
            if mapped.portfolio_mapping_id == CROSS_SECTIONAL_ZERO_NET
            else None
        ),
        lcb_warning="ordinary standard error; no serial-correlation or multiple-testing correction",
    )


def evaluate_authorized_materialization(
    receipt: Any,
    materialized: Any,
    panel: Any,
    *,
    require_full_development_blocks: bool = True,
) -> StrictEvaluation:
    """Bind authorization, canonical mapping and release-generated target.

    The public canary path uses this wrapper rather than accepting an arbitrary
    target matrix.  Cost preflight may use a declared development subset, but
    formal adaptive feedback requires all six frozen train-only month blocks.
    """

    materialized_receipt = getattr(materialized, "receipt")
    if (
        getattr(materialized_receipt, "receipt_sha256", None)
        != getattr(receipt, "receipt_sha256", None)
        or getattr(materialized_receipt, "candidate_id", None)
        != getattr(receipt, "candidate_id", None)
        or getattr(materialized_receipt, "cache_key", None)
        != getattr(receipt, "cache_key", None)
    ):
        raise ValueError("materialization/authorization candidate identity mismatch")
    receipt.verify_integrity()
    mapping_id = str(getattr(receipt, "mapping_id"))
    horizon = int(getattr(receipt, "target_horizon_hours"))
    release_view_sha = str(getattr(receipt, "release_view_sha256"))
    manifest = panel.release_manifest
    if release_view_sha != str(manifest["development_view_sha256"]):
        raise ValueError("authorization receipt/release panel identity mismatch")
    mapped = getattr(materialized, "mapped")
    signal = np.asarray(getattr(materialized, "signal"), dtype=float)
    if array_sha256(signal) != str(getattr(materialized, "signal_array_sha256")):
        raise ValueError("materialized signal hash mismatch")
    if array_sha256(mapped.weights) != str(getattr(materialized, "weight_array_sha256")):
        raise ValueError("materialized weight hash mismatch")
    canonical_mapped = map_portfolio(signal, DEFAULT_MAPPING_CONTRACTS[mapping_id])
    if not np.array_equal(
        np.asarray(mapped.weights), np.asarray(canonical_mapped.weights), equal_nan=True
    ):
        raise ValueError("materialized weights differ from canonical mapping replay")
    if not np.array_equal(
        np.asarray(mapped.feasible, dtype=bool),
        np.asarray(canonical_mapped.feasible, dtype=bool),
    ):
        raise ValueError("materialized feasibility differs from canonical mapping replay")
    if mapping_id == SPARSE_EVENT_OR_CARRY:
        for name in ("event_opportunity_mask", "event_entry_mask"):
            if list(mapped.diagnostics.get(name, ())) != list(
                canonical_mapped.diagnostics.get(name, ())
            ):
                raise ValueError(
                    "materialized sparse diagnostics differ from canonical mapping replay"
                )
    mapped = canonical_mapped
    target = panel.target_return(horizon)
    months = tuple(FROZEN_DEVELOPMENT_MONTHS) if require_full_development_blocks else None
    return evaluate_real_mapping(
        mapped,
        signal,
        target,
        panel.month_labels,
        target_horizon_hours=horizon,
        expected_mapping_id=mapping_id,
        expected_months=months,
    )
