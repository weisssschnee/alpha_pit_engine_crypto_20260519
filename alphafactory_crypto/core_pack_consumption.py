"""Executable consumer qualification for the context-bound 120-token Core Pack.

The pack is two independent surfaces, not one 120-channel panel.  This module
resolves each token against its source registry, materializes only the selected
channels, and runs a fixed dense probe to prove tensor exposure, gradient
reachability, parameter updates, and prediction sensitivity.  It is not a
performance search or an economic evaluator.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

from alphafactory_crypto.broad_search.panel18m import RawPanelStore
from alphafactory_crypto.engines.feature_algebra import CryptoFeatureAlgebra
from alphafactory_crypto.field_information import FieldBatchProvider


BROAD_CONTEXT = "BROAD_PANEL_BASELINE"
CORE3_CONTEXT = "CORE3_MICROSTRUCTURE_PILOT"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def payload_sha256(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest().upper()


@dataclass(frozen=True, slots=True)
class ResolvedToken:
    ordinal: int
    token_id: str
    field_id: str
    token_kind: str
    context_id: str
    family: str
    expression: str
    base_dependencies: tuple[str, ...]
    feature_available_lag_bars: int
    alignment_shift_bars: int
    execution_semantics: str
    authority_ref: str

    def to_dict(self) -> dict[str, Any]:
        row = asdict(self)
        row["base_dependencies"] = list(self.base_dependencies)
        return row


def _bool(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes"}


def _expression(transform: str, dependency: str, window: int) -> tuple[str, str]:
    if transform == "TSMean":
        return f"Mean({dependency},{window})", "TRAILING_SAME_SYMBOL_MEAN"
    if transform == "Delta":
        return f"Delta({dependency},{window})", "TRAILING_SAME_SYMBOL_DIFFERENCE"
    if transform == "Decay":
        return f"Decay({dependency},{window})", "TRAILING_LINEAR_DECAY"
    if transform == "ZScore":
        return (
            f"ZScore(Mean({dependency},{window}))",
            "TRAILING_MEAN_THEN_TIMESTAMP_CROSS_SECTIONAL_ZSCORE",
        )
    raise ValueError(f"unsupported selected transform: {transform}")


def resolve_core_pack(
    pack: Mapping[str, Any],
    base_registry: pd.DataFrame,
    derived_registry: pd.DataFrame,
    *,
    expected_tokens: int = 120,
) -> list[ResolvedToken]:
    tokens = list(pack.get("tokens", []))
    if len(tokens) != expected_tokens:
        raise ValueError(f"Core Pack token count changed: {len(tokens)} != {expected_tokens}")
    if len({str(row["token_id"]) for row in tokens}) != len(tokens):
        raise ValueError("Core Pack token identities are not unique")
    base = base_registry.set_index("field_name", drop=False)
    derived = derived_registry.set_index("derived_feature_id", drop=False)
    resolved: list[ResolvedToken] = []
    selected_base_by_context = {
        context: {
            str(row["field_id"])
            for row in tokens
            if row["context_id"] == context and row["token_kind"] == "BASE"
        }
        for context in (BROAD_CONTEXT, CORE3_CONTEXT)
    }
    for ordinal, row in enumerate(tokens, start=1):
        context = str(row["context_id"])
        kind = str(row["token_kind"])
        field = str(row["field_id"])
        if context not in {BROAD_CONTEXT, CORE3_CONTEXT}:
            raise ValueError(f"unknown context: {context}")
        if context == BROAD_CONTEXT:
            if kind != "BASE":
                raise ValueError("broad Core Pack currently permits base tokens only")
            lag = 1
            expression = field
            dependencies = (field,)
            semantics = "RAW_PANEL_ALIGNED_BASE_FIELD"
            authority = "CRYPTO_18M_COMPOSITIONAL_FIELD_REGISTRY"
        elif kind == "BASE":
            if field not in base.index:
                raise KeyError(field)
            source = base.loc[field]
            lag = int(source["feature_available_lag_bars"])
            if lag < 1 or _bool(source["same_hour_execution_allowed"]):
                raise ValueError(f"unsafe base timing contract: {field}")
            expression = field
            dependencies = (field,)
            semantics = "CORE3_AGGTRADES_BASE_FIELD"
            authority = "aggtrades_base_feature_registry_94.csv"
        else:
            if kind != "DERIVED" or field not in derived.index:
                raise KeyError(field)
            source = derived.loc[field]
            transform = str(source["transform"])
            window = int(source["window_hours"])
            dependencies = tuple(
                part.strip() for part in str(source["base_fields"]).split(";") if part.strip()
            )
            if len(dependencies) != 1:
                raise ValueError(f"selected lazy token is not unary: {field}")
            if not set(dependencies).issubset(selected_base_by_context[CORE3_CONTEXT]):
                raise ValueError(f"derived dependency is not in the Core3 pack: {field}")
            if transform != str(row.get("transform")) or window != int(row.get("window_hours")):
                raise ValueError(f"manifest/registry semantic mismatch: {field}")
            if not _bool(source["requires_agg_features_available_mask"]):
                raise ValueError(f"derived token lost the agg availability mask: {field}")
            if _bool(source["zero_fill_allowed"]) or _bool(source["missing_as_signal_allowed"]):
                raise ValueError(f"unsafe missing-value contract: {field}")
            if _bool(source["same_hour_execution_allowed"]):
                raise ValueError(f"unsafe same-hour contract: {field}")
            lag = int(source["feature_available_lag_bars"])
            expression, semantics = _expression(transform, dependencies[0], window)
            authority = "aggtrades_derived_feature_specs_5211.csv+CryptoFeatureAlgebra"
        resolved.append(
            ResolvedToken(
                ordinal=ordinal,
                token_id=str(row["token_id"]),
                field_id=field,
                token_kind=kind,
                context_id=context,
                family=str(row["family"]),
                expression=expression,
                base_dependencies=dependencies,
                feature_available_lag_bars=lag,
                alignment_shift_bars=max(0, lag - 1),
                execution_semantics=semantics,
                authority_ref=authority,
            )
        )
    return resolved


def _channel_statistics(values: np.ndarray) -> list[dict[str, Any]]:
    rows = []
    for index in range(values.shape[1]):
        column = np.asarray(values[:, index], dtype=float)
        finite = np.isfinite(column)
        finite_values = column[finite]
        rows.append(
            {
                "finite_ratio": float(finite.mean()),
                "finite_rows": int(finite.sum()),
                "variance": float(np.var(finite_values)) if len(finite_values) else 0.0,
                "nonzero_ratio_of_finite": (
                    float((np.abs(finite_values) > 1e-12).mean()) if len(finite_values) else 0.0
                ),
                "minimum": float(np.min(finite_values)) if len(finite_values) else None,
                "maximum": float(np.max(finite_values)) if len(finite_values) else None,
            }
        )
    return rows


def materialize_broad_context(
    cache_root: Path,
    contracts: Sequence[ResolvedToken],
    context: Mapping[str, Any],
    *,
    probe_assets: int,
    probe_start: str,
) -> tuple[np.ndarray, np.ndarray, list[dict[str, Any]], dict[str, Any]]:
    selected = [row for row in contracts if row.context_id == BROAD_CONTEXT]
    store = RawPanelStore.open(cache_root)
    full_slice = store.block_slice(context["start"], context["end_exclusive"])
    full_eligible = np.asarray(store.base_eligible()[:, full_slice], dtype=bool)
    field_stats = []
    for row in selected:
        values = np.asarray(store.field(row.field_id)[:, full_slice], dtype=np.float32)
        stats = _channel_statistics(values[full_eligible].reshape(-1, 1))[0]
        field_stats.append({**row.to_dict(), **stats})

    probe_slice = store.block_slice(probe_start, context["end_exclusive"])
    eligible = np.asarray(store.base_eligible()[:, probe_slice], dtype=bool)
    order = np.argsort(-eligible.sum(axis=1), kind="stable")[: int(probe_assets)]
    provider = FieldBatchProvider.from_raw_panel(store)
    batch = provider.load(
        [f"FIELD:{row.field_id}" for row in selected], order, probe_slice
    ).values
    values = batch.transpose(0, 2, 1).reshape(-1, len(selected)).astype(np.float32)
    target = np.asarray(store.target_return(int(context["target_horizon_hours"]))[order, probe_slice])
    target = target.reshape(-1).astype(np.float32)
    timestamps = np.asarray(store.timestamp_ns[probe_slice], dtype=np.int64)
    if timestamps.max() >= pd.Timestamp(context["end_exclusive"]).value:
        raise ValueError("broad consumer crossed the development boundary")
    summary = {
        "assets_total": store.shape[0],
        "probe_assets": len(order),
        "probe_symbols": [store.symbols[index] for index in order],
        "timestamps_full": int(full_slice.stop - full_slice.start),
        "timestamps_probe": int(probe_slice.stop - probe_slice.start),
        "tensor_rows": int(len(values)),
        "tensor_channels": int(values.shape[1]),
        "actual_start": pd.Timestamp(int(store.timestamp_ns[full_slice.start]), tz="UTC").isoformat(),
        "actual_end": pd.Timestamp(int(store.timestamp_ns[full_slice.stop - 1]), tz="UTC").isoformat(),
    }
    return values, target, field_stats, summary


def materialize_core3_context(
    panel_path: Path,
    contracts: Sequence[ResolvedToken],
    context: Mapping[str, Any],
) -> tuple[np.ndarray, np.ndarray, list[dict[str, Any]], dict[str, Any]]:
    selected = [row for row in contracts if row.context_id == CORE3_CONTEXT]
    base_fields = sorted({dependency for row in selected for dependency in row.base_dependencies})
    columns = ["symbol", "timestamp", "close", "agg_features_available", *base_fields]
    frame = pd.read_parquet(panel_path, columns=list(dict.fromkeys(columns)))
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
    frame = frame.loc[
        frame["symbol"].isin(context["symbols"])
        & frame["timestamp"].ge(pd.Timestamp(context["start"]))
        & frame["timestamp"].lt(pd.Timestamp(context["end_exclusive"]))
    ].sort_values(["symbol", "timestamp"]).reset_index(drop=True)
    for field in base_fields:
        frame[field] = pd.to_numeric(frame[field], errors="coerce").where(
            frame["agg_features_available"].astype(bool)
        )
    groups = {symbol: block for symbol, block in frame.groupby("symbol", sort=False)}
    if set(groups) != set(context["symbols"]):
        raise ValueError("Core3 consumer symbols are incomplete")
    reference = groups[context["symbols"][0]]["timestamp"].to_numpy()
    for symbol in context["symbols"]:
        if not np.array_equal(groups[symbol]["timestamp"].to_numpy(), reference):
            raise ValueError(f"Core3 timestamp mismatch for {symbol}")
    if frame["timestamp"].max() >= pd.Timestamp(context["end_exclusive"]):
        raise ValueError("Core3 consumer crossed the development boundary")

    algebra = CryptoFeatureAlgebra(frame, set(base_fields))
    aligned = pd.DataFrame(index=algebra.frame.index)
    for row in selected:
        raw = algebra.evaluate(row.expression).values
        aligned[row.token_id] = raw.groupby(algebra.frame["symbol"], sort=False).shift(
            row.alignment_shift_bars
        )
    values = aligned.to_numpy(dtype=np.float32)
    close = pd.to_numeric(algebra.frame["close"], errors="coerce")
    grouped_close = close.groupby(algebra.frame["symbol"], sort=False)
    target = np.log(grouped_close.shift(-6) / grouped_close.shift(-2)).to_numpy(dtype=np.float32)
    stats = [
        {**row.to_dict(), **channel}
        for row, channel in zip(selected, _channel_statistics(values), strict=True)
    ]
    summary = {
        "symbols": list(context["symbols"]),
        "timestamps": int(len(reference)),
        "tensor_rows": int(len(values)),
        "tensor_channels": int(values.shape[1]),
        "actual_start": algebra.frame["timestamp"].min().isoformat(),
        "actual_end": algebra.frame["timestamp"].max().isoformat(),
        "derived_channels": sum(row.token_kind == "DERIVED" for row in selected),
        "maximum_alignment_shift_bars": max(row.alignment_shift_bars for row in selected),
    }
    return values, target, stats, summary


def dense_consumption_probe(
    values: np.ndarray,
    target: np.ndarray,
    *,
    seed: int,
    maximum_samples: int,
    epochs: int,
    hidden_width: int,
    learning_rate: float,
    ablation_samples: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    import torch

    x_raw = np.asarray(values, dtype=np.float32)
    y_raw = np.asarray(target, dtype=np.float32)
    eligible = np.flatnonzero(np.isfinite(y_raw) & np.isfinite(x_raw).any(axis=1))
    if len(eligible) < x_raw.shape[1] * 2:
        raise ValueError("insufficient rows for the dense consumption probe")
    if len(eligible) > maximum_samples:
        positions = np.linspace(0, len(eligible) - 1, maximum_samples, dtype=int)
        eligible = eligible[positions]
    selected = x_raw[eligible]
    target_selected = y_raw[eligible]
    target_mean = float(np.mean(target_selected))
    target_scale = float(np.std(target_selected))
    if not np.isfinite(target_scale) or target_scale <= 1e-12:
        raise ValueError("probe target has no usable variation")
    target_selected = (target_selected - target_mean) / target_scale
    means = np.nanmean(selected, axis=0)
    scales = np.nanstd(selected, axis=0)
    scales = np.where(np.isfinite(scales) & (scales > 1e-12), scales, 1.0)
    standardized = (selected - means) / scales
    masks = np.isfinite(standardized).astype(np.float32)
    standardized = np.nan_to_num(standardized, nan=0.0, posinf=0.0, neginf=0.0)
    model_input = np.concatenate([standardized, masks], axis=1).astype(np.float32)

    torch.manual_seed(int(seed))
    torch.set_num_threads(1)
    model = torch.nn.Sequential(
        torch.nn.Linear(model_input.shape[1], int(hidden_width)),
        torch.nn.Tanh(),
        torch.nn.Linear(int(hidden_width), 1),
    )
    optimizer = torch.optim.Adam(model.parameters(), lr=float(learning_rate))
    x = torch.from_numpy(model_input)
    y = torch.from_numpy(target_selected.reshape(-1, 1))
    initial_weight = model[0].weight.detach().clone()
    initial_loss = None
    for _ in range(int(epochs)):
        optimizer.zero_grad(set_to_none=True)
        prediction = model(x)
        loss = torch.mean((prediction - y) ** 2)
        if initial_loss is None:
            initial_loss = float(loss.detach())
        loss.backward()
        optimizer.step()
    final_loss = float(torch.mean((model(x) - y) ** 2).detach())

    x_gradient = x.detach().clone().requires_grad_(True)
    model(x_gradient).sum().backward()
    channel_count = values.shape[1]
    gradient = x_gradient.grad[:, :channel_count].abs().mean(dim=0).detach().cpu().numpy()
    weight_update = (
        model[0].weight[:, :channel_count] - initial_weight[:, :channel_count]
    ).abs().mean(dim=0).detach().cpu().numpy()
    probe_count = min(int(ablation_samples), len(x))
    probe_x = x[:probe_count].detach().clone()
    with torch.no_grad():
        baseline = model(probe_x)
        sensitivity = []
        for index in range(channel_count):
            ablated = probe_x.clone()
            ablated[:, index] = 0.0
            sensitivity.append(float((model(ablated) - baseline).abs().mean()))

    rows = [
        {
            "input_gradient_mean_abs": float(gradient[index]),
            "first_layer_weight_update_mean_abs": float(weight_update[index]),
            "ablation_prediction_change_mean_abs": float(sensitivity[index]),
        }
        for index in range(channel_count)
    ]
    summary = {
        "samples": int(len(x)),
        "value_channels": int(channel_count),
        "mask_channels": int(channel_count),
        "model_input_channels": int(model_input.shape[1]),
        "epochs": int(epochs),
        "hidden_width": int(hidden_width),
        "seed": int(seed),
        "target_normalization": "CONTEXT_SAMPLE_ZSCORE",
        "initial_training_loss": initial_loss,
        "final_training_loss": final_loss,
        "training_loss_decreased": bool(final_loss < float(initial_loss)),
        "gradient_reachable_channels": int((gradient > 1e-12).sum()),
        "updated_value_channels": int((weight_update > 1e-12).sum()),
        "ablation_sensitive_channels": int((np.asarray(sensitivity) > 1e-12).sum()),
        "claim_boundary": "CONSUMPTION_PLUMBING_ONLY_NOT_MODEL_QUALITY_OR_ECONOMIC_EVIDENCE",
    }
    return summary, rows


def qualify_consumption_rows(
    materialization_rows: Sequence[Mapping[str, Any]],
    probe_rows: Sequence[Mapping[str, Any]],
    *,
    minimum_finite_ratio: float,
) -> list[dict[str, Any]]:
    if len(materialization_rows) != len(probe_rows):
        raise ValueError("materialization/probe channel count mismatch")
    output = []
    for materialized, probed in zip(materialization_rows, probe_rows, strict=True):
        checks = {
            "materialized": int(materialized["finite_rows"]) > 0,
            "finite_adequacy": float(materialized["finite_ratio"]) >= minimum_finite_ratio,
            "value_variation": float(materialized["variance"]) > 0.0,
            "gradient_reachable": float(probed["input_gradient_mean_abs"]) > 1e-12,
            "parameter_updated": float(probed["first_layer_weight_update_mean_abs"]) > 1e-12,
            "prediction_sensitive": float(probed["ablation_prediction_change_mean_abs"]) > 1e-12,
        }
        output.append(
            {
                **dict(materialized),
                **dict(probed),
                **{f"check_{key}": value for key, value in checks.items()},
                "plumbing_pass": all(
                    checks[key]
                    for key in ("materialized", "finite_adequacy", "gradient_reachable")
                ),
                "nontrivial_utilization_pass": all(checks.values()),
                "consumption_pass": all(checks.values()),
            }
        )
    return output


__all__ = [
    "BROAD_CONTEXT",
    "CORE3_CONTEXT",
    "ResolvedToken",
    "dense_consumption_probe",
    "materialize_broad_context",
    "materialize_core3_context",
    "payload_sha256",
    "qualify_consumption_rows",
    "resolve_core_pack",
    "sha256_file",
]
