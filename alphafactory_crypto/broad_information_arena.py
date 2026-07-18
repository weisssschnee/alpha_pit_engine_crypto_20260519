"""Broad Core Pack information qualification and fixed matched Arena.

This module evaluates one frozen 39-field Broad surface against the current
10-field runtime surface.  It uses train-fitted discretization, block-matched
nulls, a residual-information proxy, and two fixed model families.  It does
not perform hyperparameter search, read sealed roles, or promote candidates.
"""

from __future__ import annotations

import hashlib
import json
import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge

from alphafactory_crypto.broad_search.pair18m import _series_metrics
from alphafactory_crypto.broad_search.panel18m import RawPanelStore
from alphafactory_crypto.field_information import apply_bins, discrete_entropy, discrete_mi, quantile_edges
from alphafactory_crypto.instrument_capability.mapping import (
    CROSS_SECTIONAL_ZERO_NET,
    DEFAULT_MAPPING_CONTRACTS,
    map_portfolio,
    mapping_contract_sha256,
)


CONTROL_SURFACE = "CURRENT_10"
FULL_SURFACE = "BROAD_CORE_PACK_39"
RIDGE_MODEL = "RIDGE"
MLP_MODEL = "FIXED_MLP"
DIRECT_DELTA_MAPPING = "DIRECT_DELTA_SIGNAL_ZERO_NET"
HORIZON_MEAN_DELTA_MAPPING = "HORIZON_4H_CAUSAL_MEAN_DELTA_ZERO_NET"


def payload_sha256(value: Any) -> str:
    raw = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest().upper()


def array_sha256(values: np.ndarray) -> str:
    array = np.ascontiguousarray(np.nan_to_num(values, nan=9.87654321e20), dtype="<f8")
    digest = hashlib.sha256()
    digest.update(str(array.shape).encode("ascii"))
    digest.update(array.tobytes(order="C"))
    return digest.hexdigest().upper()


@dataclass(slots=True)
class BroadArenaData:
    store: RawPanelStore
    fields: tuple[str, ...]
    control_fields: tuple[str, ...]
    values: np.ndarray
    target: np.ndarray
    eligibility: np.ndarray
    timestamps: np.ndarray
    slices: dict[str, slice]


def _slice(store: RawPanelStore, spec: Mapping[str, str]) -> slice:
    return store.block_slice(spec["start"], spec["end_exclusive"])


def load_broad_arena_data(repo_root: Path, config: Mapping[str, Any]) -> BroadArenaData:
    pack = json.loads((repo_root / config["inputs"]["resolved_core_pack"]).read_text())
    fields = tuple(
        row["field_id"]
        for row in pack["tokens"]
        if row["context_id"] == "BROAD_PANEL_BASELINE"
    )
    control_config = json.loads(
        (repo_root / config["inputs"]["field_information_config"]).read_text()
    )
    control_fields = tuple(
        control_config["contexts"]["BROAD_PANEL_BASELINE"]["known_fields"]
    )
    expected = int(config["frozen_budget"]["full_fields"])
    if len(fields) != expected or len(set(fields)) != expected:
        raise ValueError("frozen Broad Core Pack field identity changed")
    if not set(control_fields).issubset(fields):
        raise ValueError("current runtime control is not a subset of the Broad Core Pack")
    store = RawPanelStore.open(repo_root / config["inputs"]["broad_cache"])
    slices = {name: _slice(store, spec) for name, spec in config["splits"].items()}
    end = max(block.stop for block in slices.values())
    values = np.empty((store.shape[0], len(fields), end), dtype=np.float32)
    for index, field in enumerate(fields):
        values[:, index, :] = np.asarray(store.field(field)[:, :end], dtype=np.float32)
    target = np.asarray(store.target_return(int(config["target_horizon_hours"]))[:, :end], dtype=np.float32)
    eligibility = np.asarray(store.base_eligible()[:, :end], dtype=bool)
    timestamps = np.asarray(store.timestamp_ns[:end], dtype=np.int64)
    if timestamps[-1] >= pd.Timestamp(config["boundaries"]["latest_timestamp_exclusive"]).value:
        raise ValueError("Broad Arena crossed the development boundary")
    return BroadArenaData(
        store=store,
        fields=fields,
        control_fields=control_fields,
        values=values,
        target=target,
        eligibility=eligibility,
        timestamps=timestamps,
        slices=slices,
    )


def deterministic_coordinates(mask: np.ndarray, maximum: int) -> tuple[np.ndarray, np.ndarray]:
    coordinates = np.argwhere(np.asarray(mask, dtype=bool).T)
    if not len(coordinates):
        raise ValueError("no eligible coordinates")
    if len(coordinates) > int(maximum):
        positions = np.linspace(0, len(coordinates) - 1, int(maximum), dtype=int)
        coordinates = coordinates[positions]
    return coordinates[:, 1], coordinates[:, 0]


def _raw_matrix(
    data: BroadArenaData,
    assets: np.ndarray,
    times: np.ndarray,
    field_indices: np.ndarray,
) -> np.ndarray:
    return data.values[assets[:, None], field_indices[None, :], times[:, None]]


def fit_normalization(
    data: BroadArenaData, assets: np.ndarray, times: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    raw = _raw_matrix(data, assets, times, np.arange(len(data.fields)))
    median = np.nanmedian(raw, axis=0)
    q25 = np.nanquantile(raw, 0.25, axis=0)
    q75 = np.nanquantile(raw, 0.75, axis=0)
    scale = (q75 - q25) / 1.349
    scale = np.where(np.isfinite(scale) & (scale > 1e-8), scale, 1.0)
    return median.astype(np.float32), scale.astype(np.float32)


def model_matrix(
    raw: np.ndarray, median: np.ndarray, scale: np.ndarray
) -> np.ndarray:
    finite = np.isfinite(raw)
    normalized = np.clip((raw - median) / scale, -8.0, 8.0)
    normalized = np.nan_to_num(normalized, nan=0.0, posinf=8.0, neginf=-8.0)
    return np.concatenate([normalized, finite.astype(np.float32)], axis=1).astype(np.float32)


class FixedMLP:
    def __init__(self, input_features: int, hidden: Sequence[int], seed: int):
        import torch

        torch.manual_seed(int(seed))
        layers: list[torch.nn.Module] = []
        current = int(input_features)
        for width in hidden:
            layers.extend([torch.nn.Linear(current, int(width)), torch.nn.GELU()])
            current = int(width)
        layers.append(torch.nn.Linear(current, 1))
        self.model = torch.nn.Sequential(*layers)

    def fit(
        self,
        x: np.ndarray,
        y: np.ndarray,
        *,
        seed: int,
        epochs: int,
        batch_size: int,
        learning_rate: float,
        weight_decay: float,
        torch_threads: int,
    ) -> dict[str, Any]:
        import torch

        torch.set_num_threads(int(torch_threads))
        generator = torch.Generator().manual_seed(int(seed))
        features = torch.from_numpy(np.asarray(x, dtype=np.float32))
        target = torch.from_numpy(np.asarray(y, dtype=np.float32).reshape(-1, 1))
        optimizer = torch.optim.AdamW(
            self.model.parameters(), lr=float(learning_rate), weight_decay=float(weight_decay)
        )
        initial_loss = None
        final_loss = None
        started = time.perf_counter()
        for _ in range(int(epochs)):
            order = torch.randperm(len(features), generator=generator)
            total = 0.0
            observations = 0
            for start in range(0, len(order), int(batch_size)):
                chosen = order[start : start + int(batch_size)]
                prediction = self.model(features[chosen])
                loss = torch.mean((prediction - target[chosen]) ** 2)
                optimizer.zero_grad(set_to_none=True)
                loss.backward()
                optimizer.step()
                total += float(loss.detach()) * len(chosen)
                observations += len(chosen)
            epoch_loss = total / max(observations, 1)
            if initial_loss is None:
                initial_loss = epoch_loss
            final_loss = epoch_loss
        return {
            "initial_training_loss": float(initial_loss),
            "final_training_loss": float(final_loss),
            "training_loss_decreased": bool(final_loss < initial_loss),
            "fit_seconds": float(time.perf_counter() - started),
            "parameter_count": int(sum(p.numel() for p in self.model.parameters())),
        }

    def predict(self, x: np.ndarray, batch_size: int = 32768) -> np.ndarray:
        import torch

        self.model.eval()
        output = []
        with torch.no_grad():
            for start in range(0, len(x), int(batch_size)):
                local = torch.from_numpy(np.asarray(x[start : start + batch_size], dtype=np.float32))
                output.append(self.model(local).squeeze(1).cpu().numpy())
        return np.concatenate(output).astype(np.float32)


def predict_split(
    model: Any,
    *,
    model_family: str,
    data: BroadArenaData,
    block: slice,
    field_indices: np.ndarray,
    median: np.ndarray,
    scale: np.ndarray,
    target_mean: float,
    target_scale: float,
    maximum_chunk: int = 100_000,
) -> np.ndarray:
    local_mask = data.eligibility[:, block] & np.isfinite(data.target[:, block])
    assets, local_times = deterministic_coordinates(local_mask, int(local_mask.sum()))
    absolute_times = local_times + int(block.start)
    prediction = np.full(local_mask.shape, np.nan, dtype=np.float32)
    for start in range(0, len(assets), int(maximum_chunk)):
        stop = min(start + int(maximum_chunk), len(assets))
        raw = _raw_matrix(
            data,
            assets[start:stop],
            absolute_times[start:stop],
            field_indices,
        )
        x = model_matrix(raw, median[field_indices], scale[field_indices])
        scaled = model.predict(x) if model_family == RIDGE_MODEL else model.predict(x)
        prediction[assets[start:stop], local_times[start:stop]] = (
            np.asarray(scaled, dtype=np.float32) * target_scale + target_mean
        )
    return prediction


def prediction_metrics(
    prediction: np.ndarray, target: np.ndarray, maximum_rank_samples: int
) -> dict[str, Any]:
    valid = np.isfinite(prediction) & np.isfinite(target)
    pred = prediction[valid].astype(float)
    truth = target[valid].astype(float)
    if len(pred) > int(maximum_rank_samples):
        chosen = np.linspace(0, len(pred) - 1, int(maximum_rank_samples), dtype=int)
        pred_rank, truth_rank = pred[chosen], truth[chosen]
    else:
        pred_rank, truth_rank = pred, truth
    pearson = float(np.corrcoef(pred, truth)[0, 1]) if np.std(pred) > 0 else 0.0
    spearman = float(pd.Series(pred_rank).corr(pd.Series(truth_rank), method="spearman"))
    return {
        "observations": int(len(pred)),
        "mse": float(np.mean((pred - truth) ** 2)),
        "pearson": pearson,
        "spearman": spearman,
        "prediction_variance": float(np.var(pred)),
        "prediction_unique_rounded_1e8": int(np.unique(np.round(pred, 8)).size),
        "prediction_sha256": array_sha256(prediction),
    }


def paired_surface_diagnostics(
    full_prediction: np.ndarray,
    control_prediction: np.ndarray,
    full_weights: np.ndarray,
    control_weights: np.ndarray,
    *,
    maximum_rank_samples: int,
) -> dict[str, Any]:
    common = np.isfinite(full_prediction) & np.isfinite(control_prediction)
    full = np.asarray(full_prediction[common], dtype=float)
    control = np.asarray(control_prediction[common], dtype=float)
    if len(full) > int(maximum_rank_samples):
        chosen = np.linspace(0, len(full) - 1, int(maximum_rank_samples), dtype=int)
        full_rank, control_rank = full[chosen], control[chosen]
    else:
        full_rank, control_rank = full, control
    value_correlation = (
        float(np.corrcoef(full, control)[0, 1])
        if len(full) > 1 and np.std(full) > 0 and np.std(control) > 0
        else 0.0
    )
    rank_correlation = float(
        pd.Series(full_rank).corr(pd.Series(control_rank), method="spearman")
    )
    weight_difference = np.asarray(full_weights, dtype=float) - np.asarray(
        control_weights, dtype=float
    )
    full_weight_flat = np.asarray(full_weights, dtype=float).reshape(-1)
    control_weight_flat = np.asarray(control_weights, dtype=float).reshape(-1)
    weight_correlation = (
        float(np.corrcoef(full_weight_flat, control_weight_flat)[0, 1])
        if np.std(full_weight_flat) > 0 and np.std(control_weight_flat) > 0
        else 0.0
    )
    prediction_exact_ratio = float(np.mean(full == control)) if len(full) else 1.0
    weight_exact_ratio = float(np.mean(weight_difference == 0.0))
    prediction_identical = bool(prediction_exact_ratio == 1.0)
    mapping_collapse = bool(weight_exact_ratio == 1.0)
    return {
        "common_prediction_coordinates": int(len(full)),
        "prediction_value_correlation": value_correlation,
        "prediction_rank_correlation": rank_correlation,
        "prediction_exact_equality_ratio": prediction_exact_ratio,
        "prediction_mean_abs_difference": float(np.mean(np.abs(full - control))),
        "prediction_identical": prediction_identical,
        "weight_value_correlation": weight_correlation,
        "weight_exact_equality_ratio": weight_exact_ratio,
        "weight_mean_abs_difference": float(np.mean(np.abs(weight_difference))),
        "portfolio_mapping_collapse": mapping_collapse,
        "comparison_degenerate": prediction_identical,
    }


def economic_metrics(
    prediction: np.ndarray, data: BroadArenaData, block: slice
) -> tuple[dict[str, Any], np.ndarray]:
    mapped = map_portfolio(prediction, DEFAULT_MAPPING_CONTRACTS[CROSS_SECTIONAL_ZERO_NET])
    weights = np.asarray(mapped.weights, dtype=float)
    target = np.asarray(data.target[:, block], dtype=float)
    active = np.abs(weights) > 1e-12
    missing_target = np.any(active & ~np.isfinite(target), axis=0)
    evaluation = (
        (data.eligibility[:, block].sum(axis=0) >= 3)
        & ~missing_target
        & np.any(np.isfinite(prediction), axis=0)
    )
    months = pd.to_datetime(data.timestamps[block], utc=True).strftime("%Y-%m").to_numpy()
    return (
        _series_metrics(
            weights=weights,
            target=target,
            months=months,
            evaluation_mask=evaluation,
            horizon=4,
        ),
        weights,
    )


def paired_increment(
    full_weights: np.ndarray, control_weights: np.ndarray, data: BroadArenaData, block: slice
) -> dict[str, Any]:
    months = pd.to_datetime(data.timestamps[block], utc=True).strftime("%Y-%m").to_numpy()
    return _series_metrics(
        weights=full_weights - control_weights,
        target=np.asarray(data.target[:, block], dtype=float),
        months=months,
        evaluation_mask=data.eligibility[:, block].sum(axis=0) >= 3,
        horizon=4,
    )


def causal_trailing_mean(values: np.ndarray, window: int) -> np.ndarray:
    source = np.asarray(values, dtype=float)
    finite = np.isfinite(source)
    sums = np.cumsum(np.where(finite, source, 0.0), axis=1)
    counts = np.cumsum(finite.astype(np.int32), axis=1)
    sums = np.concatenate([np.zeros((source.shape[0], 1)), sums], axis=1)
    counts = np.concatenate([np.zeros((source.shape[0], 1), dtype=np.int32), counts], axis=1)
    output = np.full(source.shape, np.nan, dtype=float)
    for stop in range(1, source.shape[1] + 1):
        start = max(0, stop - int(window))
        total = sums[:, stop] - sums[:, start]
        count = counts[:, stop] - counts[:, start]
        output[:, stop - 1] = np.divide(
            total,
            count,
            out=np.full(source.shape[0], np.nan, dtype=float),
            where=count > 0,
        )
    return output


def incremental_signal_mapping(
    full_prediction: np.ndarray,
    control_prediction: np.ndarray,
    data: BroadArenaData,
    block: slice,
    *,
    smoothing_window: int,
) -> tuple[dict[str, Any], np.ndarray, np.ndarray]:
    common = np.isfinite(full_prediction) & np.isfinite(control_prediction)
    signal = np.where(common, full_prediction - control_prediction, np.nan)
    if int(smoothing_window) > 1:
        signal = causal_trailing_mean(signal, int(smoothing_window))
        signal[~common] = np.nan
    mapped = map_portfolio(signal, DEFAULT_MAPPING_CONTRACTS[CROSS_SECTIONAL_ZERO_NET])
    weights = np.asarray(mapped.weights, dtype=float)
    target = np.asarray(data.target[:, block], dtype=float)
    active = np.abs(weights) > 1e-12
    missing_target = np.any(active & ~np.isfinite(target), axis=0)
    evaluation = (
        (data.eligibility[:, block].sum(axis=0) >= 3)
        & ~missing_target
        & np.any(np.isfinite(signal), axis=0)
    )
    months = pd.to_datetime(data.timestamps[block], utc=True).strftime("%Y-%m").to_numpy()
    metrics = _series_metrics(
        weights=weights,
        target=target,
        months=months,
        evaluation_mask=evaluation,
        horizon=4,
    )
    return metrics, weights, signal


def _split_information(
    value_bins: np.ndarray,
    target_bins: np.ndarray,
    residual_bins: np.ndarray,
    eligible: np.ndarray,
    timestamps: np.ndarray,
    null_shifts: Sequence[int],
    maximum_samples: int,
) -> dict[str, Any]:
    valid = eligible & (value_bins >= 0) & (target_bins >= 0) & (residual_bins >= 0)
    assets, times = deterministic_coordinates(valid, maximum_samples)
    x = value_bins[assets, times]
    y = target_bins[assets, times]
    r = residual_bins[assets, times]
    observed = discrete_mi(x, y)
    residual = discrete_mi(x, r)
    target_entropy = discrete_entropy(y)
    residual_entropy = discrete_entropy(r)
    null = [discrete_mi(x, np.roll(target_bins, int(shift), axis=1)[assets, times]) for shift in null_shifts]
    residual_null = [
        discrete_mi(x, np.roll(residual_bins, int(shift), axis=1)[assets, times])
        for shift in null_shifts
    ]
    null_q95 = float(np.quantile(null, 0.95))
    residual_null_q95 = float(np.quantile(residual_null, 0.95))
    months = pd.to_datetime(timestamps, utc=True).strftime("%Y-%m").to_numpy()
    month_passes = []
    residual_month_passes = []
    for month in tuple(dict.fromkeys(months.tolist())):
        local = months == month
        local_valid = valid[:, local]
        if local_valid.sum() < 100:
            continue
        ma, mt = deterministic_coordinates(local_valid, min(maximum_samples, int(local_valid.sum())))
        mx = value_bins[:, local][ma, mt]
        my = target_bins[:, local][ma, mt]
        mr = residual_bins[:, local][ma, mt]
        local_null = [
            discrete_mi(mx, np.roll(target_bins[:, local], int(shift), axis=1)[ma, mt])
            for shift in null_shifts
        ]
        local_residual_null = [
            discrete_mi(mx, np.roll(residual_bins[:, local], int(shift), axis=1)[ma, mt])
            for shift in null_shifts
        ]
        month_passes.append(discrete_mi(mx, my) > float(np.quantile(local_null, 0.95)))
        residual_month_passes.append(
            discrete_mi(mx, mr) > float(np.quantile(local_residual_null, 0.95))
        )
    return {
        "samples": int(len(x)),
        "normalized_value_entropy": discrete_entropy(x) / max(math.log(int(x.max()) + 1), 1.0),
        "target_entropy": target_entropy,
        "target_conditional_entropy": target_entropy - observed,
        "target_mutual_information": observed,
        "target_null_q95": null_q95,
        "target_mi_excess_q95": observed - null_q95,
        "residual_entropy": residual_entropy,
        "residual_conditional_entropy": residual_entropy - residual,
        "residual_mutual_information": residual,
        "residual_null_q95": residual_null_q95,
        "residual_mi_excess_q95": residual - residual_null_q95,
        "positive_month_ratio": float(np.mean(month_passes)) if month_passes else 0.0,
        "residual_positive_month_ratio": (
            float(np.mean(residual_month_passes)) if residual_month_passes else 0.0
        ),
    }


def information_evidence(
    data: BroadArenaData,
    *,
    baseline_ridge: Ridge,
    median: np.ndarray,
    scale: np.ndarray,
    target_mean: float,
    target_scale: float,
    config: Mapping[str, Any],
    prior_census: pd.DataFrame,
) -> pd.DataFrame:
    info = config["information"]
    train = data.slices["train"]
    train_mask = data.eligibility[:, train] & np.isfinite(data.target[:, train])
    train_assets, train_times = deterministic_coordinates(train_mask, int(info["maximum_samples"]))
    train_absolute = train_times + train.start
    target_edges = quantile_edges(
        data.target[train_assets, train_absolute], int(info["quantile_bins"])
    )
    control_indices = np.asarray([data.fields.index(field) for field in data.control_fields])
    train_control = model_matrix(
        _raw_matrix(data, train_assets, train_absolute, control_indices),
        median[control_indices],
        scale[control_indices],
    )
    train_residual = data.target[train_assets, train_absolute] - (
        baseline_ridge.predict(train_control) * target_scale + target_mean
    )
    residual_edges = quantile_edges(train_residual, int(info["quantile_bins"]))
    field_edges = {}
    for index, field in enumerate(data.fields):
        field_edges[field] = quantile_edges(
            data.values[train_assets, index, train_absolute], int(info["quantile_bins"])
        )
    prior = prior_census.set_index("field_id", drop=False)
    split_payload: dict[str, dict[str, Any]] = {}
    for split in ("selection", "stability"):
        block = data.slices[split]
        control_prediction = predict_split(
            baseline_ridge,
            model_family=RIDGE_MODEL,
            data=data,
            block=block,
            field_indices=control_indices,
            median=median,
            scale=scale,
            target_mean=target_mean,
            target_scale=target_scale,
        )
        local_target = data.target[:, block]
        target_bins = apply_bins(local_target, target_edges)
        residual_bins = apply_bins(local_target - control_prediction, residual_edges)
        split_payload[split] = {
            "block": block,
            "target_bins": target_bins,
            "residual_bins": residual_bins,
        }
    rows = []
    for index, field in enumerate(data.fields):
        row: dict[str, Any] = {
            "field_id": field,
            "surface_role": "CONTROL" if field in data.control_fields else "ADDED",
            "prior_max_redundancy_spearman": float(prior.loc[field, "max_redundancy_spearman"]),
            "prior_redundancy_cluster_id": str(prior.loc[field, "redundancy_cluster_id"]),
        }
        for split, payload in split_payload.items():
            block = payload["block"]
            metrics = _split_information(
                apply_bins(data.values[:, index, block], field_edges[field]),
                payload["target_bins"],
                payload["residual_bins"],
                data.eligibility[:, block],
                data.timestamps[block],
                info["within_block_null_shifts_hours"],
                int(info["maximum_samples"]),
            )
            row.update({f"{split}_{key}": value for key, value in metrics.items()})
        row["stable_target_information"] = bool(
            row["selection_target_mi_excess_q95"] > 0
            and row["stability_target_mi_excess_q95"] > 0
            and row["selection_positive_month_ratio"] >= float(info["minimum_positive_month_ratio"])
            and row["stability_positive_month_ratio"] >= float(info["minimum_positive_month_ratio"])
        )
        row["stable_residual_information"] = bool(
            row["selection_residual_mi_excess_q95"] > 0
            and row["stability_residual_mi_excess_q95"] > 0
            and row["selection_residual_positive_month_ratio"]
            >= float(info["minimum_positive_month_ratio"])
            and row["stability_residual_positive_month_ratio"]
            >= float(info["minimum_positive_month_ratio"])
        )
        rows.append(row)
    return pd.DataFrame(rows)


def data_adequacy(data: BroadArenaData, config: Mapping[str, Any]) -> dict[str, Any]:
    gate = config["data_adequacy"]
    split_rows = {}
    for name, block in data.slices.items():
        local = data.eligibility[:, block] & np.isfinite(data.target[:, block])
        split_rows[name] = {
            "timestamps": int(block.stop - block.start),
            "eligible_assets": int(np.any(local, axis=1).sum()),
            "target_samples": int(local.sum()),
            "months": int(pd.Series(pd.to_datetime(data.timestamps[block], utc=True).strftime("%Y-%m")).nunique()),
        }
    train = data.slices["train"]
    coverage = []
    variance = []
    for index in range(len(data.fields)):
        local = data.values[:, index, train]
        finite = np.isfinite(local) & data.eligibility[:, train]
        coverage.append(float(finite.sum() / max(data.eligibility[:, train].sum(), 1)))
        variance.append(float(np.nanvar(local[finite])) if finite.any() else 0.0)
    checks = {
        "development_dates": sum(row["timestamps"] for row in split_rows.values()) / 24
        >= int(gate["minimum_development_dates"]),
        "training_samples": split_rows["train"]["target_samples"]
        >= int(gate["minimum_training_samples"]),
        "cross_sectional_assets": split_rows["train"]["eligible_assets"]
        >= int(gate["minimum_assets"]),
        "fields": len(data.fields) == int(config["frozen_budget"]["full_fields"]),
        "field_non_null": min(coverage) >= float(gate["minimum_field_non_null_ratio"]),
        "field_variance": all(value > 0 for value in variance),
        "history_length": split_rows["train"]["timestamps"] >= int(gate["minimum_train_hours"]),
        "label_support": all(row["target_samples"] >= int(gate["minimum_block_label_samples"]) for row in split_rows.values()),
        "turnover_observations": (
            split_rows["selection"]["timestamps"] + split_rows["stability"]["timestamps"]
        )
        >= int(gate["minimum_turnover_observations"]),
        "independent_evaluation_blocks": (
            split_rows["selection"]["months"] + split_rows["stability"]["months"]
        )
        >= int(gate["minimum_independent_evaluation_months"]),
    }
    return {
        "status": "DATA_ADEQUACY_PASS" if all(checks.values()) else "DATA_ADEQUACY_UNDERPOWERED",
        "checks": checks,
        "split_support": split_rows,
        "field_non_null_minimum": min(coverage),
        "field_variance_positive": int(sum(value > 0 for value in variance)),
        "claim_scope": "BROAD_39_FIELD_FIXED_DEVELOPMENT_ARENA_ONLY",
    }


def arena_decision(
    information: pd.DataFrame,
    increments: Sequence[Mapping[str, Any]],
    config: Mapping[str, Any],
) -> dict[str, Any]:
    added = information.loc[information["surface_role"] == "ADDED"]
    info_ratio = float(added["stable_residual_information"].mean())
    info_pass = info_ratio >= float(config["information"]["minimum_stable_added_field_ratio"])
    rows = pd.DataFrame(
        [
            {
                "model_family": row["model_family"],
                "seed": row["seed"],
                "split": row["split"],
                "gross_mean": row["metrics"]["gross_mean"],
                "net_mean": row["metrics"]["net_mean"],
                "net_lcb": row["metrics"]["net_lcb"],
            }
            for row in increments
        ]
    )
    by_split = rows.groupby("split", sort=False).agg(
        gross_median=("gross_mean", "median"),
        net_median=("net_mean", "median"),
        positive_net_ratio=("net_mean", lambda values: float(np.mean(np.asarray(values) > 0))),
    )
    economic_pass = bool(
        all(by_split["gross_median"] > 0)
        and all(by_split["net_median"] > 0)
        and all(
            by_split["positive_net_ratio"]
            >= float(config["decision"]["minimum_positive_run_ratio"])
        )
    )
    degenerate_pairs = int(
        sum(
            bool(row.get("comparison", {}).get("comparison_degenerate"))
            or bool(row.get("comparison", {}).get("portfolio_mapping_collapse"))
            for row in increments
        )
    )
    cost_killed = bool(
        info_pass
        and all(by_split["gross_median"] > 0)
        and all(by_split["net_median"] < 0)
        and all(by_split["positive_net_ratio"] == 0)
    )
    status = (
        "BROAD_CORE_PACK_COMPARISON_DEGENERATE"
        if degenerate_pairs
        else "BROAD_CORE_PACK_DEVELOPMENT_INCREMENT_OBSERVED"
        if info_pass and economic_pass
        else "BROAD_CORE_PACK_INFORMATION_INCREMENT_COST_KILLED"
        if cost_killed
        else "BROAD_CORE_PACK_INFORMATION_INCREMENT_ONLY"
        if info_pass
        else "BROAD_CORE_PACK_INCREMENT_NOT_ESTABLISHED"
    )
    return {
        "status": status,
        "stable_added_residual_information_ratio": info_ratio,
        "information_gate_pass": info_pass,
        "economic_increment_gate_pass": economic_pass,
        "cost_killed_under_frozen_mapping": cost_killed,
        "degenerate_pairs": degenerate_pairs,
        "split_increment_summary": by_split.reset_index().to_dict("records"),
        "cannot_infer": [
            "formal_performance_search_authority",
            "OOS_qualification",
            "candidate_promotion",
            "future_or_recent_performance",
        ],
    }


def mapping_repair_decision(
    rows: Sequence[Mapping[str, Any]], minimum_positive_run_ratio: float
) -> dict[str, Any]:
    frame = pd.DataFrame(
        [
            {
                "variant": row["variant"],
                "split": row["split"],
                "gross_mean": row["metrics"]["gross_mean"],
                "net_mean": row["metrics"]["net_mean"],
            }
            for row in rows
        ]
    )
    summary = (
        frame.groupby(["variant", "split"], sort=False)
        .agg(
            gross_median=("gross_mean", "median"),
            net_median=("net_mean", "median"),
            positive_net_ratio=("net_mean", lambda values: float(np.mean(np.asarray(values) > 0))),
        )
        .reset_index()
    )
    passed = []
    for variant, block in summary.groupby("variant", sort=False):
        if (
            set(block["split"]) == {"selection", "stability"}
            and bool((block["gross_median"] > 0).all())
            and bool((block["net_median"] > 0).all())
            and bool((block["positive_net_ratio"] >= float(minimum_positive_run_ratio)).all())
        ):
            passed.append(str(variant))
    return {
        "status": (
            "PORTFOLIO_MAPPING_DEVELOPMENT_INCREMENT_OBSERVED"
            if passed
            else "PORTFOLIO_MAPPING_REPAIR_NOT_ESTABLISHED"
        ),
        "passed_variants": passed,
        "summary": summary.to_dict("records"),
    }


__all__ = [
    "CONTROL_SURFACE",
    "DIRECT_DELTA_MAPPING",
    "FULL_SURFACE",
    "HORIZON_MEAN_DELTA_MAPPING",
    "MLP_MODEL",
    "RIDGE_MODEL",
    "BroadArenaData",
    "FixedMLP",
    "arena_decision",
    "array_sha256",
    "causal_trailing_mean",
    "data_adequacy",
    "deterministic_coordinates",
    "economic_metrics",
    "fit_normalization",
    "information_evidence",
    "incremental_signal_mapping",
    "load_broad_arena_data",
    "model_matrix",
    "mapping_repair_decision",
    "paired_increment",
    "paired_surface_diagnostics",
    "payload_sha256",
    "predict_split",
    "prediction_metrics",
]
