from __future__ import annotations

import hashlib
from collections.abc import Iterable, Mapping, Sequence

import numpy as np
import pandas as pd

from alphafactory_crypto.engines.signal_identity import canonicalize_weight_orientation


ALLOWED_OBSERVATION_COLUMNS = frozenset(
    {
        "timestamp",
        "open_interest_value_last",
        "open_interest_value_mean",
        "top_long_short_account_ratio_last",
        "top_long_short_position_ratio_last",
        "global_long_short_account_ratio_last",
        "mark_trade_basis_bps",
    }
)
FORBIDDEN_COLUMN_TOKENS = (
    "return",
    "label",
    "reward",
    "sortino",
    "sharpe",
    "pnl",
    "profit",
    "future",
    "forward",
)


def validate_observation_columns(columns: Iterable[str]) -> tuple[str, ...]:
    normalized = tuple(str(column) for column in columns)
    forbidden = sorted(
        column
        for column in normalized
        if any(token in column.lower() for token in FORBIDDEN_COLUMN_TOKENS)
    )
    unknown = sorted(set(normalized).difference(ALLOWED_OBSERVATION_COLUMNS))
    if forbidden or unknown:
        raise PermissionError(
            f"B0A observation columns fail closed; forbidden={forbidden}; unknown={unknown}"
        )
    return normalized


def canonical_coordinate_order(
    symbols: Sequence[str], timestamps_ns: np.ndarray, values: np.ndarray
) -> tuple[tuple[str, ...], np.ndarray, np.ndarray]:
    symbol_values = np.asarray([str(symbol) for symbol in symbols], dtype=str)
    timestamp_values = np.asarray(timestamps_ns, dtype=np.int64)
    array = np.asarray(values)
    if array.shape[-2:] != (len(symbol_values), len(timestamp_values)):
        raise ValueError("values must end with symbol x timestamp coordinates")
    if len(set(symbol_values.tolist())) != len(symbol_values):
        raise ValueError("duplicate symbol coordinate")
    if len(np.unique(timestamp_values)) != len(timestamp_values):
        raise ValueError("duplicate timestamp coordinate")
    symbol_order = np.argsort(symbol_values, kind="stable")
    timestamp_order = np.argsort(timestamp_values, kind="stable")
    ordered = np.take(np.take(array, symbol_order, axis=-2), timestamp_order, axis=-1)
    return (
        tuple(symbol_values[symbol_order].tolist()),
        timestamp_values[timestamp_order],
        ordered,
    )


def canonical_weight_hash(weights: np.ndarray) -> str:
    canonical = np.ascontiguousarray(
        canonicalize_weight_orientation(np.asarray(weights, dtype=np.float64)), dtype="<f8"
    )
    payload = "x".join(str(value) for value in canonical.shape).encode("ascii") + b"|" + canonical.tobytes(order="C")
    return hashlib.sha256(payload).hexdigest()


def deterministic_weight_sketch(weights: np.ndarray, *, size: int = 4096) -> np.ndarray:
    if size <= 0:
        raise ValueError("sketch size must be positive")
    flat = canonicalize_weight_orientation(np.asarray(weights, dtype=np.float64)).ravel(order="C")
    if flat.size == 0:
        return np.zeros(size, dtype=np.float32)
    indices = np.linspace(0, flat.size - 1, min(size, flat.size), dtype=np.int64)
    sample = flat[indices].astype(np.float32, copy=False)
    if sample.size < size:
        sample = np.pad(sample, (0, size - sample.size))
    return np.ascontiguousarray(sample, dtype="<f4")


def rank_pct(signal: np.ndarray) -> np.ndarray:
    values = np.asarray(signal, dtype=np.float64)
    return pd.DataFrame(values).rank(axis=0, pct=True, method="average").to_numpy(dtype=np.float64)


def signal_to_rank_weights(
    signal: np.ndarray, *, gross: float = 1.0, max_abs_weight: float = 0.03
) -> tuple[np.ndarray, np.ndarray]:
    ranks = rank_pct(signal)
    finite_counts = np.isfinite(ranks).sum(axis=0, keepdims=True)
    means = np.divide(
        np.nansum(ranks, axis=0, keepdims=True),
        finite_counts,
        out=np.zeros((1, ranks.shape[1]), dtype=np.float64),
        where=finite_counts > 0,
    )
    centered = ranks - means
    centered[~np.isfinite(centered)] = 0.0
    denom = np.sum(np.abs(centered), axis=0, keepdims=True)
    weights = np.divide(centered, denom, out=np.zeros_like(centered), where=denom > 1e-12) * gross
    weights = np.clip(weights, -max_abs_weight, max_abs_weight)
    gross_after_clip = np.sum(np.abs(weights), axis=0, keepdims=True)
    weights = np.divide(
        weights,
        gross_after_clip,
        out=np.zeros_like(weights),
        where=gross_after_clip > 1e-12,
    ) * gross
    return ranks, canonicalize_weight_orientation(weights)


def top_bottom_masks(
    ranks: np.ndarray, *, top_fraction: float = 0.2, bottom_fraction: float = 0.2
) -> tuple[np.ndarray, np.ndarray]:
    if not (0 < top_fraction <= 0.5 and 0 < bottom_fraction <= 0.5):
        raise ValueError("top and bottom fractions must be in (0, 0.5]")
    values = np.asarray(ranks, dtype=np.float64)
    return values >= (1.0 - top_fraction), values <= bottom_fraction


def lag_persistence(weights: np.ndarray, lags: Sequence[int]) -> np.ndarray:
    values = np.asarray(weights, dtype=np.float64)
    result: list[float] = []
    for raw_lag in lags:
        lag = int(raw_lag)
        if lag <= 0 or lag >= values.shape[1]:
            result.append(float("nan"))
            continue
        left = values[:, lag:].ravel(order="C")
        right = values[:, :-lag].ravel(order="C")
        valid = np.isfinite(left) & np.isfinite(right)
        if valid.sum() < 2 or np.std(left[valid]) <= 1e-15 or np.std(right[valid]) <= 1e-15:
            result.append(float("nan"))
        else:
            result.append(float(np.corrcoef(left[valid], right[valid])[0, 1]))
    return np.asarray(result, dtype=np.float64)


def _jaccard(left: np.ndarray, right: np.ndarray) -> float:
    a = np.asarray(left, dtype=bool)
    b = np.asarray(right, dtype=bool)
    union = np.logical_or(a, b).sum()
    return float(np.logical_and(a, b).sum() / union) if union else 1.0


def _normalized_profile_distance(left: np.ndarray, right: np.ndarray) -> float:
    a = np.asarray(left, dtype=np.float64)
    b = np.asarray(right, dtype=np.float64)
    valid = np.isfinite(a) & np.isfinite(b)
    if not valid.any():
        return 0.0
    scale = max(float(np.mean(np.abs(a[valid]))), float(np.mean(np.abs(b[valid]))), 1e-12)
    return float(np.mean(np.abs(a[valid] - b[valid])) / scale)


def behaviour_pair_metrics(
    weights_left: np.ndarray,
    weights_right: np.ndarray,
    activation_left: np.ndarray,
    activation_right: np.ndarray,
    top_left: np.ndarray,
    top_right: np.ndarray,
    bottom_left: np.ndarray,
    bottom_right: np.ndarray,
    *,
    persistence_left: np.ndarray,
    persistence_right: np.ndarray,
    stability_left: np.ndarray,
    stability_right: np.ndarray,
) -> dict[str, float]:
    left = np.asarray(weights_left, dtype=np.float64)
    right = np.asarray(weights_right, dtype=np.float64)
    joint = np.asarray(activation_left, dtype=bool) & np.asarray(activation_right, dtype=bool)
    sign_agreement = float(np.mean(np.sign(left[joint]) == np.sign(right[joint]))) if joint.any() else 1.0
    if joint.sum() >= 2 and np.std(left[joint]) > 1e-15 and np.std(right[joint]) > 1e-15:
        rank_correlation = float(np.corrcoef(left[joint], right[joint])[0, 1])
    else:
        rank_correlation = 1.0 if np.array_equal(left[joint], right[joint]) else 0.0
    per_timestamp_distance = np.sum(np.abs(left - right), axis=0) / 2.0
    return {
        "activation_jaccard": _jaccard(activation_left, activation_right),
        "sign_agreement": sign_agreement,
        "rank_correlation": rank_correlation,
        "top_bottom_overlap": (_jaccard(top_left, top_right) + _jaccard(bottom_left, bottom_right)) / 2.0,
        "holding_weight_distance": float(np.mean(per_timestamp_distance)),
        "persistence_difference": _normalized_profile_distance(persistence_left, persistence_right),
        "symbol_month_stability_difference": _normalized_profile_distance(stability_left, stability_right),
    }


def pair_passes_contract(metrics: Mapping[str, float], thresholds: Mapping[str, float]) -> bool:
    return bool(
        metrics["activation_jaccard"] >= thresholds["activation_jaccard_min"]
        and metrics["sign_agreement"] >= thresholds["sign_agreement_min"]
        and metrics["rank_correlation"] >= thresholds["rank_correlation_min"]
        and metrics["top_bottom_overlap"] >= thresholds["top_bottom_overlap_min"]
        and metrics["holding_weight_distance"] <= thresholds["holding_weight_distance_max"]
        and metrics["persistence_difference"] <= thresholds["persistence_difference_max"]
        and metrics["symbol_month_stability_difference"]
        <= thresholds["symbol_month_stability_difference_max"]
    )


def cluster_behaviours(
    signal_ids: Sequence[str], pair_rows: Sequence[Mapping[str, object]], thresholds: Mapping[str, float]
) -> dict[str, str]:
    ordered = tuple(sorted(str(signal_id) for signal_id in signal_ids))
    parent = {signal_id: signal_id for signal_id in ordered}

    def find(value: str) -> str:
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = parent[value]
        return value

    def union(left: str, right: str) -> None:
        a, b = find(left), find(right)
        if a != b:
            parent[max(a, b)] = min(a, b)

    for row in pair_rows:
        left, right = str(row["left"]), str(row["right"])
        if left not in parent or right not in parent:
            raise ValueError("pair row references an unknown signal")
        if pair_passes_contract(row, thresholds):
            union(left, right)
    members: dict[str, list[str]] = {}
    for signal_id in ordered:
        members.setdefault(find(signal_id), []).append(signal_id)
    cluster_ids = {
        root: "behaviour-cluster:" + hashlib.sha256("|".join(group).encode("utf-8")).hexdigest()[:24]
        for root, group in members.items()
    }
    return {signal_id: cluster_ids[find(signal_id)] for signal_id in ordered}
