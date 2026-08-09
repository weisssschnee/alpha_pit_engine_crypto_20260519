"""Explicit portfolio mappings and full-L1 turnover/cost attribution."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass, field
from typing import Any, Mapping

import numpy as np
import pandas as pd


CROSS_SECTIONAL_ZERO_NET = "CROSS_SECTIONAL_ZERO_NET"
TIME_SERIES_DIRECTIONAL_STATEFUL = "TIME_SERIES_DIRECTIONAL_STATEFUL"
SPARSE_EVENT_OR_CARRY = "SPARSE_EVENT_OR_CARRY"
DIRECT_ZERO_NET_COST_AWARE = "DIRECT_ZERO_NET_COST_AWARE"


@dataclass(frozen=True)
class MappingContract:
    portfolio_mapping_id: str
    parameters: Mapping[str, Any]
    rebalance_cadence: str
    hold_semantics: str
    cost_model: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MappingResult:
    portfolio_mapping_id: str
    contract_sha256: str
    weights: np.ndarray
    feasible: np.ndarray
    transition_reasons: tuple[tuple[str, ...], ...]
    diagnostics: Mapping[str, Any]
    behavior_provenance: Mapping[str, Any] = field(default_factory=dict)


DEFAULT_MAPPING_CONTRACTS: Mapping[str, MappingContract] = {
    CROSS_SECTIONAL_ZERO_NET: MappingContract(
        portfolio_mapping_id=CROSS_SECTIONAL_ZERO_NET,
        parameters={
            "rank_method": "average",
            "demean": True,
            "gross_target": 1.0,
            "position_cap": 0.20,
            "clip_renormalize_order": "rank_then_demean_then_sidewise_capped_allocation;never_post_cap_renormalize",
            "minimum_asset_count": 3,
            "singleton_behavior": "NO_TRADE_INFEASIBLE",
            "missing_handling": "exclude_nonfinite_assets_per_coordinate",
        },
        rebalance_cadence="every synthetic coordinate",
        hold_semantics="stateless cross-sectional rerank",
        cost_model={"id": "FULL_L1_FIXED_BPS", "cost_bps": 5.0, "initial_establishment_charged": True},
    ),
    TIME_SERIES_DIRECTIONAL_STATEFUL: MappingContract(
        portfolio_mapping_id=TIME_SERIES_DIRECTIONAL_STATEFUL,
        parameters={
            "entry_threshold": 0.60,
            "exit_threshold": 0.20,
            "maximum_position": 0.25,
            "gross_cap": 1.0,
            "rebalance_interval": 1,
            "missing_handling": "hold_existing_state_no_new_entry",
            "demean": False,
        },
        rebalance_cadence="explicit interval; default every synthetic coordinate",
        hold_semantics="hysteresis; retain entry position until exit, reversal, or gross-cap scaling",
        cost_model={"id": "FULL_L1_FIXED_BPS", "cost_bps": 5.0, "initial_establishment_charged": True},
    ),
    SPARSE_EVENT_OR_CARRY: MappingContract(
        portfolio_mapping_id=SPARSE_EVENT_OR_CARRY,
        parameters={
            "event_threshold": 0.75,
            "fixed_holding_period": 4,
            "settlement_interval": 1,
            "maximum_position": 0.25,
            "gross_cap": 1.0,
            "singleton_behavior": "PRESERVE_SINGLETON_EVENT",
            "missing_handling": "hold_existing_position_no_new_entry",
            "explicit_no_trade_state": True,
        },
        rebalance_cadence="event/settlement aligned",
        hold_semantics="fixed hold from eligible event, then explicit exit",
        cost_model={"id": "FULL_L1_FIXED_BPS", "cost_bps": 5.0, "initial_establishment_charged": True},
    ),
    DIRECT_ZERO_NET_COST_AWARE: MappingContract(
        portfolio_mapping_id=DIRECT_ZERO_NET_COST_AWARE,
        parameters={
            "source": "MODEL_DIRECT_WEIGHTS",
            "gross_cap": 1.0,
            "position_cap": 0.20,
            "zero_net_tolerance": 1e-6,
            "minimum_asset_count": 3,
            "ineligible_weight_tolerance": 1e-8,
            "missing_handling": "ineligible_assets_must_have_zero_weight",
        },
        rebalance_cadence="model decision coordinate",
        hold_semantics="previous portfolio is an explicit model input; output is the next feasible portfolio",
        cost_model={"id": "FULL_L1_FIXED_BPS", "cost_bps": 5.0, "initial_establishment_charged": True},
    ),
}


def mapping_contract_sha256(contract: MappingContract) -> str:
    encoded = json.dumps(contract.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest().upper()


def _matrix(values: np.ndarray, name: str) -> np.ndarray:
    result = np.asarray(values, dtype=float)
    if result.ndim != 2 or result.shape[1] == 0:
        raise ValueError(f"{name} must have shape [asset,time] with nonempty time")
    return result


def _array_identity(
    values: np.ndarray,
    *,
    finite: np.ndarray | None = None,
) -> str:
    """Hash a numeric stage with an explicit finite mask and stable zeros."""

    array = np.asarray(values, dtype="<f8")
    finite_mask = np.isfinite(array) if finite is None else np.asarray(finite, dtype=bool)
    if finite_mask.shape != array.shape:
        raise ValueError("finite mask shape mismatch")
    canonical = np.where(finite_mask, array, 0.0).astype("<f8", copy=False)
    canonical[canonical == 0.0] = 0.0
    digest = hashlib.sha256()
    digest.update(str(array.shape).encode("ascii"))
    digest.update(finite_mask.astype(np.uint8).tobytes(order="C"))
    digest.update(canonical.tobytes(order="C"))
    return digest.hexdigest().upper()


def _rank_entropy_mean(values: np.ndarray) -> float:
    """Mean normalized entropy of average-rank states across coordinates."""

    array = _matrix(values, "rank entropy values")
    entropies: list[float] = []
    for column in range(array.shape[1]):
        local = array[:, column]
        local = local[np.isfinite(local)]
        if local.size <= 1:
            entropies.append(0.0)
            continue
        _, counts = np.unique(local, return_counts=True)
        probabilities = counts.astype(float) / float(local.size)
        entropy = -float(np.sum(probabilities * np.log(probabilities)))
        entropies.append(entropy / math.log(float(local.size)))
    return float(np.mean(entropies)) if entropies else 0.0


def _stage_numeric_record(values: np.ndarray) -> dict[str, Any]:
    array = np.asarray(values, dtype=float)
    finite = np.isfinite(array)
    return {
        "identity_sha256": _array_identity(array, finite=finite),
        "shape": [int(value) for value in array.shape],
        "finite_count": int(finite.sum()),
        "non_null_rate": float(finite.mean()) if finite.size else 0.0,
    }


def _stage_record(
    values: np.ndarray,
    *,
    semantic: str,
    numeric_record: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    array = np.asarray(values, dtype=float)
    finite = np.isfinite(array)
    record: dict[str, Any] = {
        "semantic": str(semantic),
        **dict(numeric_record or _stage_numeric_record(array)),
    }
    if semantic in {
        "mapping_input_signal",
        "raw_expression_signal_before_train_orientation",
        "mapping_input_after_frozen_train_orientation",
    }:
        clean = array[finite]
        with np.errstate(all="ignore"):
            dispersions = np.nanstd(array, axis=0)
        finite_dispersions = dispersions[np.isfinite(dispersions)]
        record["distribution_summary"] = {
            "mean": float(np.mean(clean)) if clean.size else None,
            "standard_deviation": float(np.std(clean)) if clean.size else None,
            "minimum": float(np.min(clean)) if clean.size else None,
            "maximum": float(np.max(clean)) if clean.size else None,
            "cross_sectional_dispersion_mean": (
                float(np.mean(finite_dispersions))
                if finite_dispersions.size
                else None
            ),
            "rank_entropy_mean": _rank_entropy_mean(array),
        }
    return record


def _mapping_behavior_provenance(
    *,
    mapping_id: str,
    stage_order: list[str],
    stage_values: Mapping[str, tuple[np.ndarray, str]],
    unavailable_stages: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    numeric_records: dict[
        tuple[int, tuple[int, ...], tuple[int, ...] | None, str], dict[str, Any]
    ] = {}
    stages: dict[str, dict[str, Any]] = {}
    for name, (values, semantic) in stage_values.items():
        array = np.asarray(values, dtype=float)
        key = (
            id(values),
            tuple(int(value) for value in array.shape),
            (
                tuple(int(value) for value in array.strides)
                if array.strides is not None
                else None
            ),
            str(array.dtype),
        )
        numeric = numeric_records.get(key)
        if numeric is None:
            numeric = _stage_numeric_record(array)
            numeric_records[key] = numeric
        stages[name] = _stage_record(
            array,
            semantic=semantic,
            numeric_record=numeric,
        )
    payload: dict[str, Any] = {
        "schema_version": "CRYPTO_MAPPING_BEHAVIOR_PROVENANCE_V1",
        "mapping_id": str(mapping_id),
        "stage_order": list(stage_order),
        "stages": stages,
        "unavailable_stages": dict(unavailable_stages or {}),
        "identity_excludes": [
            "target",
            "target_ic",
            "gross",
            "net",
            "turnover",
            "cost",
            "reward",
        ],
    }
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    payload["provenance_sha256"] = hashlib.sha256(encoded).hexdigest().upper()
    return payload


def _signal_provenance_stages(
    mapping_signal: np.ndarray,
    source_signal: np.ndarray | None,
) -> tuple[list[str], dict[str, tuple[np.ndarray, str]]]:
    if source_signal is None:
        return ["SIGNAL"], {
            "SIGNAL": (mapping_signal, "mapping_input_signal"),
        }
    source = _matrix(source_signal, "source_signal_for_provenance")
    if source.shape != mapping_signal.shape:
        raise ValueError("source signal provenance shape mismatch")
    return ["SIGNAL", "ORIENTED_SIGNAL"], {
        "SIGNAL": (source, "raw_expression_signal_before_train_orientation"),
        "ORIENTED_SIGNAL": (
            mapping_signal,
            "mapping_input_after_frozen_train_orientation",
        ),
    }


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


def _capped_allocation(scores: np.ndarray, target: float, cap: float) -> np.ndarray:
    """Allocate a nonnegative target proportionally without ever breaking cap."""

    allocation = np.zeros(scores.shape, dtype=float)
    active = scores > 0
    remaining = float(target)
    while remaining > 1e-14 and np.any(active):
        indices = np.flatnonzero(active)
        scale = scores[indices].sum()
        proposal = remaining * (scores[indices] / scale)
        capacity = cap - allocation[indices]
        saturated = proposal >= capacity - 1e-14
        if not np.any(saturated):
            allocation[indices] += proposal
            remaining = 0.0
            break
        saturated_indices = indices[saturated]
        allocation[saturated_indices] = cap
        active[saturated_indices] = False
        remaining = target - float(allocation.sum())
    if remaining > 1e-10:
        raise ValueError("capped allocation target is infeasible")
    return allocation


def _capped_allocation_columns(
    scores: np.ndarray, targets: np.ndarray, cap: float
) -> np.ndarray:
    """Column-vectorized equivalent of ``_capped_allocation``."""

    allocation = np.zeros_like(scores, dtype=float)
    active = scores > 0.0
    remaining = np.asarray(targets, dtype=float).copy()
    for _ in range(scores.shape[0]):
        pending = remaining > 1e-14
        if not np.any(pending):
            break
        scale = np.sum(np.where(active, scores, 0.0), axis=0)
        proposal = np.divide(
            remaining[None, :] * scores,
            scale[None, :],
            out=np.zeros_like(scores, dtype=float),
            where=active & (scale[None, :] > 0.0),
        )
        capacity = cap - allocation
        saturated = active & (proposal >= capacity - 1e-14)
        has_saturation = saturated.any(axis=0) & pending
        unsaturated_columns = pending & ~has_saturation
        if np.any(unsaturated_columns):
            allocation[:, unsaturated_columns] += proposal[:, unsaturated_columns]
            remaining[unsaturated_columns] = 0.0
            active[:, unsaturated_columns] = False
        if np.any(has_saturation):
            allocation[saturated] = cap
            active[saturated] = False
            remaining[has_saturation] = (
                targets[has_saturation]
                - allocation[:, has_saturation].sum(axis=0)
            )
    if np.any(remaining > 1e-10):
        raise ValueError("capped allocation target is infeasible")
    return allocation


def _cross_sectional(
    signal: np.ndarray,
    contract: MappingContract,
    *,
    include_behavior_provenance: bool = False,
    source_signal_for_provenance: np.ndarray | None = None,
) -> MappingResult:
    parameters = contract.parameters
    gross_target = float(parameters["gross_target"])
    cap = float(parameters["position_cap"])
    minimum = int(parameters["minimum_asset_count"])
    if gross_target <= 0 or cap <= 0 or cap > 1:
        raise ValueError("invalid cross-sectional gross/cap parameters")
    finite = np.isfinite(signal)
    finite_count = finite.sum(axis=0)
    ranks = pd.DataFrame(signal).rank(
        axis=0, method="average", na_option="keep"
    ).to_numpy(dtype=float)
    rank_mean = np.divide(
        np.nansum(ranks, axis=0),
        finite_count,
        out=np.zeros(signal.shape[1], dtype=float),
        where=finite_count > 0,
    )
    centered = ranks - rank_mean
    positive = centered > 0.0
    negative = centered < 0.0
    requested_side = gross_target / 2.0
    side_targets = np.minimum.reduce(
        (
            np.full(signal.shape[1], requested_side, dtype=float),
            cap * positive.sum(axis=0),
            cap * negative.sum(axis=0),
        )
    )
    positive_allocation = _capped_allocation_columns(
        np.where(positive, centered, 0.0), side_targets, cap
    )
    negative_allocation = _capped_allocation_columns(
        np.where(negative, -centered, 0.0), side_targets, cap
    )
    capped_weights = np.where(
        finite,
        positive_allocation - negative_allocation,
        0.0,
    )
    weights = capped_weights.copy()
    feasible = (
        (finite_count >= minimum)
        & positive.any(axis=0)
        & negative.any(axis=0)
    )
    weights[:, ~feasible] = 0.0
    reasons: list[tuple[str, ...]] = []
    achieved_gross: list[float] = []
    for column in range(signal.shape[1]):
        if finite_count[column] < minimum:
            reasons.append(("MINIMUM_ASSET_COUNT_NOT_MET",))
            achieved_gross.append(0.0)
        elif not positive[:, column].any() or not negative[:, column].any():
            reasons.append(("NO_CROSS_SECTIONAL_DISPERSION",))
            achieved_gross.append(0.0)
        else:
            reasons.append(
                ("GROSS_REDUCED_FOR_CAP_FEASIBILITY",)
                if side_targets[column] < requested_side - 1e-12
                else ("MAPPED",)
            )
            achieved_gross.append(
                float(np.abs(weights[finite[:, column], column]).sum())
            )
    diagnostics = {
        "requested_gross": gross_target,
        "achieved_gross": achieved_gross,
        "position_cap": cap,
        "max_final_abs_weight": float(np.max(np.abs(weights))) if weights.size else 0.0,
        "max_abs_net_exposure": float(np.max(np.abs(weights.sum(axis=0)))) if weights.size else 0.0,
        "gross_reduced_coordinates": int(sum("GROSS_REDUCED_FOR_CAP_FEASIBILITY" in item for item in reasons)),
    }
    provenance = (
        _mapping_behavior_provenance(
            mapping_id=contract.portfolio_mapping_id,
            stage_order=[
                *_signal_provenance_stages(
                    signal,
                    source_signal_for_provenance,
                )[0],
                "RANK",
                "NORMALIZED_SCORE",
                "SELECTION",
                "CAPPED_WEIGHT",
                "MAPPED_WEIGHT",
                "EXECUTABLE_WEIGHT",
            ],
            stage_values={
                **_signal_provenance_stages(
                    signal,
                    source_signal_for_provenance,
                )[1],
                "RANK": (ranks, "cross_sectional_average_rank"),
                "NORMALIZED_SCORE": (
                    centered,
                    "demeaned_cross_sectional_rank_score",
                ),
                "SELECTION": (
                    np.where(finite, np.sign(weights), 0.0),
                    "final_long_short_membership",
                ),
                "CAPPED_WEIGHT": (
                    capped_weights,
                    "sidewise_capped_weight_before_feasibility_suppression",
                ),
                "MAPPED_WEIGHT": (weights, "portfolio_mapping_output"),
                "EXECUTABLE_WEIGHT": (
                    weights,
                    "evaluator_input_weight_no_post_mapping_transform",
                ),
            },
            unavailable_stages={
                "RAW_WEIGHT": (
                    "not materialized by CROSS_SECTIONAL_ZERO_NET; the authority "
                    "allocates sidewise under the cap directly"
                ),
            },
        )
        if include_behavior_provenance
        else {}
    )
    return MappingResult(
        contract.portfolio_mapping_id,
        mapping_contract_sha256(contract),
        weights,
        feasible,
        tuple(reasons),
        diagnostics,
        provenance,
    )


def _directional(
    signal: np.ndarray,
    contract: MappingContract,
    *,
    include_behavior_provenance: bool = False,
    source_signal_for_provenance: np.ndarray | None = None,
) -> MappingResult:
    p = contract.parameters
    entry = float(p["entry_threshold"])
    exit_threshold = float(p["exit_threshold"])
    maximum = float(p["maximum_position"])
    gross_cap = float(p["gross_cap"])
    interval = int(p["rebalance_interval"])
    if not (0 <= exit_threshold < entry and 0 < maximum <= gross_cap and interval >= 1):
        raise ValueError("invalid directional mapping parameters")
    weights = np.zeros(signal.shape, dtype=float)
    raw_weights = np.zeros(signal.shape, dtype=float)
    current = np.zeros(signal.shape[0], dtype=float)
    reasons: list[tuple[str, ...]] = []
    for column in range(signal.shape[1]):
        coordinate_reasons: list[str] = []
        if column % interval == 0:
            values = signal[:, column]
            finite = np.isfinite(values)
            confidence = np.abs(values)
            direction = np.sign(values)
            was_zero = current == 0.0
            reason_codes = np.full(current.shape, "", dtype=object)

            missing_held = ~finite & ~was_zero
            entries = finite & was_zero & (confidence >= entry)
            existing = finite & ~was_zero
            exits = existing & (confidence <= exit_threshold)
            reversals = (
                existing
                & ~exits
                & (direction != np.sign(current))
            )
            strong_reversals = reversals & (confidence >= entry)
            weak_reversals = reversals & ~strong_reversals
            holds = existing & ~exits & ~reversals

            current[entries] = direction[entries] * np.minimum(
                maximum,
                confidence[entries],
            )
            current[exits | weak_reversals] = 0.0
            current[strong_reversals] = direction[strong_reversals] * np.minimum(
                maximum,
                confidence[strong_reversals],
            )

            reason_codes[missing_held] = "MISSING_SIGNAL_HELD"
            reason_codes[entries] = "ENTRY"
            reason_codes[exits] = "EXIT_THRESHOLD"
            reason_codes[strong_reversals] = "REVERSAL"
            reason_codes[weak_reversals] = "EXIT_ON_WEAK_REVERSAL"
            reason_codes[holds] = "HOLD"
            coordinate_reasons.extend(
                str(code) for code in reason_codes.tolist() if code
            )
        else:
            coordinate_reasons.append("CADENCE_HOLD")
        gross = float(np.abs(current).sum())
        raw_weights[:, column] = current
        if gross > gross_cap:
            current *= gross_cap / gross
            coordinate_reasons.append("GROSS_CAP_SCALED")
        weights[:, column] = current
        reasons.append(tuple(coordinate_reasons or ["NO_TRADE"]))
    diagnostics = {
        "entry_threshold": entry,
        "exit_threshold": exit_threshold,
        "maximum_position": maximum,
        "gross_cap": gross_cap,
        "max_final_abs_weight": float(np.max(np.abs(weights))) if weights.size else 0.0,
        "max_gross": float(np.max(np.abs(weights).sum(axis=0))) if weights.size else 0.0,
        "common_mode_preserved": bool(np.any(np.abs(weights.sum(axis=0)) > 1e-12)),
        "state_out": {"positions": current.tolist()},
    }
    provenance = (
        _mapping_behavior_provenance(
            mapping_id=contract.portfolio_mapping_id,
            stage_order=[
                *_signal_provenance_stages(
                    signal,
                    source_signal_for_provenance,
                )[0],
                "SELECTION",
                "RAW_WEIGHT",
                "CAPPED_WEIGHT",
                "MAPPED_WEIGHT",
                "EXECUTABLE_WEIGHT",
            ],
            stage_values={
                **_signal_provenance_stages(
                    signal,
                    source_signal_for_provenance,
                )[1],
                "SELECTION": (
                    np.sign(weights),
                    "stateful_active_direction_membership",
                ),
                "RAW_WEIGHT": (
                    raw_weights,
                    "stateful_position_before_gross_cap_scaling",
                ),
                "CAPPED_WEIGHT": (
                    weights,
                    "stateful_position_after_gross_cap_scaling",
                ),
                "MAPPED_WEIGHT": (weights, "stateful_portfolio_mapping_output"),
                "EXECUTABLE_WEIGHT": (
                    weights,
                    "evaluator_input_weight_no_post_mapping_transform",
                ),
            },
            unavailable_stages={
                "RANK": "TIME_SERIES_DIRECTIONAL_STATEFUL does not rank assets",
                "NORMALIZED_WEIGHT": "no distinct normalization stage exists",
            },
        )
        if include_behavior_provenance
        else {}
    )
    return MappingResult(
        contract.portfolio_mapping_id,
        mapping_contract_sha256(contract),
        weights,
        np.ones(signal.shape[1], dtype=bool),
        tuple(reasons),
        diagnostics,
        provenance,
    )


def _sparse(
    signal: np.ndarray,
    contract: MappingContract,
    *,
    include_behavior_provenance: bool = False,
    source_signal_for_provenance: np.ndarray | None = None,
) -> MappingResult:
    p = contract.parameters
    threshold = float(p["event_threshold"])
    hold_period = int(p["fixed_holding_period"])
    settlement = int(p["settlement_interval"])
    maximum = float(p["maximum_position"])
    gross_cap = float(p["gross_cap"])
    if threshold <= 0 or hold_period <= 0 or settlement <= 0 or maximum <= 0 or gross_cap <= 0:
        raise ValueError("invalid sparse mapping parameters")
    weights = np.zeros(signal.shape, dtype=float)
    raw_weights = np.zeros(signal.shape, dtype=float)
    current = np.zeros(signal.shape[0], dtype=float)
    remaining = np.zeros(signal.shape[0], dtype=int)
    reasons: list[tuple[str, ...]] = []
    opportunity_mask: list[bool] = []
    entry_mask: list[bool] = []
    for column in range(signal.shape[1]):
        coordinate_reasons: list[str] = []
        values = signal[:, column]
        finite = np.isfinite(values)
        opportunity_mask.append(
            bool(
                column % settlement == 0
                and np.any(finite & (np.abs(values) >= threshold))
            )
        )
        first_reason_codes = np.full(current.shape, "", dtype=object)
        second_reason_codes = np.full(current.shape, "", dtype=object)
        active_holds = remaining > 0
        remaining[active_holds] -= 1
        hold_exits = active_holds & (remaining == 0)
        current[hold_exits] = 0.0
        first_reason_codes[hold_exits] = "EXPLICIT_HOLD_EXIT"

        entries = (
            (remaining == 0)
            & (column % settlement == 0)
            & finite
            & (np.abs(values) >= threshold)
        )
        current[entries] = np.sign(values[entries]) * np.minimum(
            maximum,
            np.abs(values[entries]),
        )
        remaining[entries] = hold_period
        second_reason_codes[entries] = "EVENT_ENTRY"
        missing_held = ~entries & ~finite & (current != 0.0)
        second_reason_codes[missing_held] = "MISSING_SIGNAL_HELD"
        coordinate_reasons.extend(
            str(code)
            for pair in zip(
                first_reason_codes.tolist(),
                second_reason_codes.tolist(),
            )
            for code in pair
            if code
        )
        gross = float(np.abs(current).sum())
        raw_weights[:, column] = current
        if gross > gross_cap:
            current *= gross_cap / gross
            coordinate_reasons.append("GROSS_CAP_SCALED")
        weights[:, column] = current
        entry_mask.append("EVENT_ENTRY" in coordinate_reasons)
        reasons.append(tuple(coordinate_reasons or ["EXPLICIT_NO_TRADE_OR_HOLD"]))
    active_assets = (np.abs(weights) > 1e-12).sum(axis=0)
    diagnostics = {
        "event_threshold": threshold,
        "fixed_holding_period": hold_period,
        "maximum_position": maximum,
        "gross_cap": gross_cap,
        "max_final_abs_weight": float(np.max(np.abs(weights))) if weights.size else 0.0,
        "singleton_active_coordinates": int(np.count_nonzero(active_assets == 1)),
        "singleton_preserved": bool(np.any(active_assets == 1)),
        "event_opportunity_mask": opportunity_mask,
        "event_entry_mask": entry_mask,
        "event_opportunity_count": int(sum(opportunity_mask)),
        "event_entry_count": int(sum(entry_mask)),
        "state_out": {
            "positions": current.tolist(),
            "remaining_holding_period": remaining.astype(int).tolist(),
        },
    }
    provenance = (
        _mapping_behavior_provenance(
            mapping_id=contract.portfolio_mapping_id,
            stage_order=[
                *_signal_provenance_stages(
                    signal,
                    source_signal_for_provenance,
                )[0],
                "SELECTION",
                "RAW_WEIGHT",
                "CAPPED_WEIGHT",
                "MAPPED_WEIGHT",
                "EXECUTABLE_WEIGHT",
            ],
            stage_values={
                **_signal_provenance_stages(
                    signal,
                    source_signal_for_provenance,
                )[1],
                "SELECTION": (
                    np.sign(weights),
                    "event_active_direction_membership",
                ),
                "RAW_WEIGHT": (
                    raw_weights,
                    "event_hold_position_before_gross_cap_scaling",
                ),
                "CAPPED_WEIGHT": (
                    weights,
                    "event_hold_position_after_gross_cap_scaling",
                ),
                "MAPPED_WEIGHT": (weights, "event_hold_portfolio_mapping_output"),
                "EXECUTABLE_WEIGHT": (
                    weights,
                    "evaluator_input_weight_no_post_mapping_transform",
                ),
            },
            unavailable_stages={
                "RANK": "SPARSE_EVENT_OR_CARRY does not rank assets",
                "NORMALIZED_WEIGHT": "no distinct normalization stage exists",
            },
        )
        if include_behavior_provenance
        else {}
    )
    return MappingResult(
        contract.portfolio_mapping_id,
        mapping_contract_sha256(contract),
        weights,
        np.ones(signal.shape[1], dtype=bool),
        tuple(reasons),
        diagnostics,
        provenance,
    )


def map_portfolio(
    signal: np.ndarray,
    contract: MappingContract,
    *,
    include_behavior_provenance: bool = False,
    source_signal_for_provenance: np.ndarray | None = None,
) -> MappingResult:
    source = _matrix(signal, "signal")
    if contract.portfolio_mapping_id == CROSS_SECTIONAL_ZERO_NET:
        return _cross_sectional(
            source,
            contract,
            include_behavior_provenance=include_behavior_provenance,
            source_signal_for_provenance=source_signal_for_provenance,
        )
    if contract.portfolio_mapping_id == TIME_SERIES_DIRECTIONAL_STATEFUL:
        return _directional(
            source,
            contract,
            include_behavior_provenance=include_behavior_provenance,
            source_signal_for_provenance=source_signal_for_provenance,
        )
    if contract.portfolio_mapping_id == SPARSE_EVENT_OR_CARRY:
        return _sparse(
            source,
            contract,
            include_behavior_provenance=include_behavior_provenance,
            source_signal_for_provenance=source_signal_for_provenance,
        )
    if contract.portfolio_mapping_id == DIRECT_ZERO_NET_COST_AWARE:
        raise ValueError(
            "direct-weight contract requires validate_direct_weights; it is not a signal mapping"
        )
    raise ValueError(f"unknown portfolio_mapping_id: {contract.portfolio_mapping_id}")


def validate_direct_weights(
    weights: np.ndarray,
    eligible: np.ndarray,
    contract: MappingContract | None = None,
) -> MappingResult:
    """Validate model-produced weights without relabeling them as a rank mapping."""

    selected = contract or DEFAULT_MAPPING_CONTRACTS[DIRECT_ZERO_NET_COST_AWARE]
    if selected.portfolio_mapping_id != DIRECT_ZERO_NET_COST_AWARE:
        raise ValueError("direct weights require the canonical direct-weight contract")
    values = _matrix(weights, "weights")
    mask = np.asarray(eligible, dtype=bool)
    if mask.shape != values.shape:
        raise ValueError("eligible must have the same [asset,time] shape as weights")
    if not np.isfinite(values).all():
        raise ValueError("direct weights must be finite")
    parameters = selected.parameters
    gross_cap = float(parameters["gross_cap"])
    position_cap = float(parameters["position_cap"])
    zero_net_tolerance = float(parameters["zero_net_tolerance"])
    ineligible_tolerance = float(parameters["ineligible_weight_tolerance"])
    minimum_assets = int(parameters["minimum_asset_count"])
    if np.any(np.abs(values[~mask]) > ineligible_tolerance):
        raise ValueError("direct weights allocate to an ineligible asset")
    gross = np.abs(values).sum(axis=0)
    net = values.sum(axis=0)
    maximum = np.abs(values).max(axis=0)
    active = (np.abs(values) > ineligible_tolerance).sum(axis=0)
    eligible_count = mask.sum(axis=0)
    violations = {
        "gross cap": gross > gross_cap + zero_net_tolerance,
        "position cap": maximum > position_cap + zero_net_tolerance,
        "zero net": np.abs(net) > zero_net_tolerance,
        "minimum active assets": (gross > ineligible_tolerance)
        & (active < minimum_assets),
    }
    failed = [name for name, coordinates in violations.items() if np.any(coordinates)]
    if failed:
        raise ValueError("direct weight contract violation: " + ", ".join(failed))
    feasible = (gross > ineligible_tolerance) & (active >= minimum_assets)
    reasons = tuple(
        ("DIRECT_WEIGHTS_VALIDATED",) if valid else ("EXPLICIT_NO_TRADE",)
        for valid in feasible
    )
    diagnostics = {
        "source": "MODEL_DIRECT_WEIGHTS",
        "gross_cap": gross_cap,
        "position_cap": position_cap,
        "maximum_gross": float(gross.max()) if gross.size else 0.0,
        "maximum_abs_weight": float(maximum.max()) if maximum.size else 0.0,
        "maximum_abs_net_exposure": float(np.abs(net).max()) if net.size else 0.0,
        "minimum_eligible_assets": int(eligible_count.min()) if eligible_count.size else 0,
    }
    return MappingResult(
        selected.portfolio_mapping_id,
        mapping_contract_sha256(selected),
        values,
        feasible,
        reasons,
        diagnostics,
    )


def portfolio_series(weights: np.ndarray, target_return: np.ndarray, cost_bps: float = 5.0) -> dict[str, np.ndarray]:
    mapped = _matrix(weights, "weights")
    target = _matrix(target_return, "target_return")
    if mapped.shape != target.shape:
        raise ValueError("weights and target_return shape mismatch")
    valid = np.isfinite(target)
    gross = np.sum(np.where(valid, mapped * target, 0.0), axis=0)
    previous = np.zeros(mapped.shape, dtype=float)
    if mapped.shape[1] > 1:
        previous[:, 1:] = mapped[:, :-1]
    turnover = np.sum(np.abs(mapped - previous), axis=0)
    cost = turnover * float(cost_bps) / 10_000.0
    return {"gross": gross, "turnover": turnover, "cost": cost, "net": gross - cost}


def _direct_signal_reference(signal: np.ndarray, maximum_position: float = 0.20, gross_cap: float = 1.0) -> np.ndarray:
    reference = np.where(np.isfinite(signal), np.clip(signal, -maximum_position, maximum_position), 0.0)
    gross = np.abs(reference).sum(axis=0, keepdims=True)
    scale = np.minimum(1.0, np.divide(gross_cap, gross, out=np.ones_like(gross), where=gross > 0))
    return reference * scale


def turnover_decomposition(signal: np.ndarray, weights: np.ndarray, cost_bps: float = 5.0) -> dict[str, Any]:
    raw = _matrix(signal, "signal")
    mapped = _matrix(weights, "weights")
    if raw.shape != mapped.shape:
        raise ValueError("signal and weights shape mismatch")
    previous = np.zeros(mapped.shape, dtype=float)
    if mapped.shape[1] > 1:
        previous[:, 1:] = mapped[:, :-1]
    current_zero = np.abs(mapped) <= 1e-12
    previous_zero = np.abs(previous) <= 1e-12
    sign_flip = (~current_zero) & (~previous_zero) & (np.sign(mapped) != np.sign(previous))
    entry = np.where((previous_zero & ~current_zero) | sign_flip, np.abs(mapped), 0.0).sum(axis=0)
    exit_ = np.where((~previous_zero & current_zero) | sign_flip, np.abs(previous), 0.0).sum(axis=0)
    rebalance = np.where((~previous_zero & ~current_zero & ~sign_flip), np.abs(mapped - previous), 0.0).sum(axis=0)
    mapped_turnover = entry + exit_ + rebalance
    raw_previous = np.full(raw.shape, np.nan, dtype=float)
    if raw.shape[1] > 1:
        raw_previous[:, 1:] = raw[:, :-1]
    raw_movement = np.nansum(np.abs(raw - raw_previous), axis=0)
    direct = _direct_signal_reference(raw)
    direct_previous = np.zeros(direct.shape, dtype=float)
    if direct.shape[1] > 1:
        direct_previous[:, 1:] = direct[:, :-1]
    direct_turnover = np.abs(direct - direct_previous).sum(axis=0)
    excess = mapped_turnover - direct_turnover
    return {
        "raw_signal_movement_l1_native_units": raw_movement.tolist(),
        "entry_portfolio_establishment_l1": entry.tolist(),
        "rebalance_turnover_l1": rebalance.tolist(),
        "exit_turnover_l1": exit_.tolist(),
        "mapped_full_l1_turnover": mapped_turnover.tolist(),
        "direct_clipped_signal_counterfactual_turnover": direct_turnover.tolist(),
        "mapping_excess_vs_direct_counterfactual_l1": excess.tolist(),
        "fixed_cost_bps": float(cost_bps),
        "fixed_cost": (mapped_turnover * float(cost_bps) / 10_000.0).tolist(),
        "unmodeled": ["spread", "slippage", "impact", "fill_probability", "capacity"],
        "causal_warning": "raw movement and weight turnover use different units; excess is a declared direct-signal counterfactual, not historical causal attribution",
    }


def mapping_contract_payload() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "cost_formula": {
            "gross": "sum_i(weight[i,t] * target_return[i,t])",
            "turnover": "sum_i(abs(weight[i,t] - weight[i,t-1]))",
            "cost": "turnover * cost_bps / 10000",
            "net": "gross - cost",
            "turnover_convention": "full_L1_no_divide_by_two; initial establishment from zero is charged",
        },
        "contracts": [
            {
                **contract.to_dict(),
                "contract_sha256": mapping_contract_sha256(contract),
            }
            for contract in DEFAULT_MAPPING_CONTRACTS.values()
        ],
    }
