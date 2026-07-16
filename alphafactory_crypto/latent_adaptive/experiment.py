from __future__ import annotations

import hashlib
import gc
import json
import math
import os
import platform
import random
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
import pandas as pd
import psutil
import torch
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from torch import nn

from alphafactory_crypto.broad_search.pair18m import _series_metrics
from alphafactory_crypto.broad_search.panel18m import RawPanelStore
from alphafactory_crypto.instrument_capability.mapping import (
    CROSS_SECTIONAL_ZERO_NET,
    DEFAULT_MAPPING_CONTRACTS,
    map_portfolio,
    mapping_contract_sha256,
)


ARM_A = "A_KNOWN_ONLY"
ARM_B = "B_LATENT_ONLY"
ARM_C = "C_KNOWN_GENERIC"
ARM_D = "D_KNOWN_RESIDUAL"
ARM_E = "E_KNOWN_STRUCTURED_PROXY"
ARMS = (ARM_A, ARM_B, ARM_C, ARM_D, ARM_E)
RECORD_TYPES = frozenset(
    {
        "capability",
        "pilot",
        "prediction",
        "representation",
        "economic",
        "matched_control",
        "slot_ablation",
        "seed_diagnostic",
        "shortcut_audit",
    }
)


def payload_sha(value: Any) -> str:
    raw = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest().upper()


def array_sha(value: np.ndarray) -> str:
    array = np.ascontiguousarray(value)
    digest = hashlib.sha256()
    digest.update(str(array.dtype).encode("ascii"))
    digest.update(json.dumps(array.shape, separators=(",", ":")).encode("ascii"))
    digest.update(memoryview(array).cast("B"))
    return digest.hexdigest().upper()


def file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )


def write_metrics(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    normalized = []
    for row in rows:
        normalized.append(
            {
                key: (
                    json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
                    if isinstance(value, (dict, list, tuple))
                    else value
                )
                for key, value in row.items()
            }
        )
    pd.DataFrame(normalized).to_parquet(path, index=False)


def current_sha(repo_root: Path) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=repo_root, text=True
    ).strip()


def set_determinism(seed: int, threads: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.set_num_threads(int(threads))
    torch.use_deterministic_algorithms(True)


def causal_rolling_mean(values: np.ndarray, window: int) -> np.ndarray:
    finite = np.isfinite(values)
    clean = np.where(finite, values, 0.0).astype(np.float64, copy=False)
    sums = np.cumsum(clean, axis=2)
    counts = np.cumsum(finite.astype(np.int32), axis=2)
    sums = np.concatenate([np.zeros((*sums.shape[:2], 1)), sums], axis=2)
    counts = np.concatenate([np.zeros((*counts.shape[:2], 1)), counts], axis=2)
    total = sums[:, :, window:] - sums[:, :, :-window]
    count = counts[:, :, window:] - counts[:, :, :-window]
    out = np.full(values.shape, np.nan, dtype=np.float32)
    with np.errstate(invalid="ignore", divide="ignore"):
        out[:, :, window - 1 :] = (total / np.maximum(count, 1)).astype(np.float32)
    return out


def shifted_delta(values: np.ndarray, lag: int) -> np.ndarray:
    out = np.full(values.shape, np.nan, dtype=np.float32)
    out[:, :, lag:] = values[:, :, lag:] - values[:, :, :-lag]
    return out


def robust_stats(values: np.ndarray, train_slice: slice) -> tuple[np.ndarray, np.ndarray]:
    train = values[:, :, train_slice]
    median = np.nanmedian(train, axis=(0, 2)).astype(np.float32)
    q25 = np.nanquantile(train, 0.25, axis=(0, 2)).astype(np.float32)
    q75 = np.nanquantile(train, 0.75, axis=(0, 2)).astype(np.float32)
    scale = np.maximum((q75 - q25) / 1.349, 1e-6).astype(np.float32)
    return median, scale


def standardize(values: np.ndarray, median: np.ndarray, scale: np.ndarray) -> np.ndarray:
    out = (values - median[None, :, None]) / scale[None, :, None]
    return np.clip(out, -8.0, 8.0).astype(np.float32)


def future_volatility(close: np.ndarray, horizon: int = 4, delay: int = 2) -> np.ndarray:
    hourly = np.full(close.shape, np.nan, dtype=np.float32)
    with np.errstate(divide="ignore", invalid="ignore"):
        hourly[:, 1:] = np.log(close[:, 1:] / close[:, :-1]).astype(np.float32)
    out = np.full(close.shape, np.nan, dtype=np.float32)
    for offset in range(delay + 1, delay + horizon + 1):
        shifted = np.full(close.shape, np.nan, dtype=np.float32)
        shifted[:, : close.shape[1] - offset] = hourly[:, offset:]
        if offset == delay + 1:
            stack = shifted[:, :, None]
        else:
            stack = np.concatenate([stack, shifted[:, :, None]], axis=2)
    out[:] = np.nanstd(stack, axis=2).astype(np.float32)
    return out


@dataclass
class PreparedData:
    store: RawPanelStore
    fields: tuple[str, ...]
    families: tuple[str, ...]
    field_family: tuple[str, ...]
    values: np.ndarray
    masks: np.ndarray
    target: np.ndarray
    target_scaled: np.ndarray
    target_scale: float
    volatility_scaled: np.ndarray
    volatility_scale: float
    eligibility: np.ndarray
    timestamps: np.ndarray
    slices: Mapping[str, slice]
    slot_indices: Mapping[str, tuple[int, ...]]
    capability: Mapping[str, Any]


def _slice(store: RawPanelStore, spec: Mapping[str, str]) -> slice:
    return store.block_slice(spec["start"], spec["end_exclusive"])


def prepare_data(
    repo_root: Path, config: Mapping[str, Any], runtime_root: Path
) -> PreparedData:
    cache = repo_root / config["source"]["panel_cache"]
    store = RawPanelStore.open(cache)
    registry = json.loads(
        (repo_root / config["source"]["field_registry"]).read_text(encoding="utf-8")
    )
    fields = tuple(item["field_id"] for item in registry["fields"])
    families = tuple(sorted(set(item["field_family"] for item in registry["fields"])))
    family_by_field = {
        item["field_id"]: item["field_family"] for item in registry["fields"]
    }
    field_family = tuple(family_by_field[field] for field in fields)
    slices = {
        name: _slice(store, spec)
        for name, spec in config["splits"].items()
        if name != "spent_report_only"
    }
    adaptive_end = slices["stability"].stop
    raw = np.stack(
        [np.asarray(store.field(field)[:, :adaptive_end], dtype=np.float32) for field in fields],
        axis=1,
    )
    masks = np.isfinite(raw)
    median, scale = robust_stats(raw, slices["train"])
    values = standardize(raw, median, scale)
    values = np.nan_to_num(values, nan=0.0)
    target = np.asarray(store.target_return(4)[:, :adaptive_end], dtype=np.float32)
    target_train = target[:, slices["train"]]
    target_scale = float(max(np.nanstd(target_train), 1e-6))
    target_scaled = target / target_scale
    close = np.asarray(store.field("trade_close")[:, :adaptive_end], dtype=np.float32)
    volatility = future_volatility(close)
    volatility_scale = float(max(np.nanstd(volatility[:, slices["train"]]), 1e-6))
    volatility_scaled = volatility / volatility_scale
    eligibility = np.asarray(store.base_eligible()[:, :adaptive_end], dtype=bool)
    timestamps = np.asarray(store.timestamp_ns[:adaptive_end], dtype=np.int64)
    slot_families = {
        "position_pressure": {
            "open_interest_level_change",
            "open_interest_value",
            "funding",
            "account_crowding",
            "position_crowding",
        },
        "liquidity_absorption": {
            "quote_volume_activity",
            "price_return",
            "price_level",
        },
        "extreme_state_proximity": {
            "price_return",
            "basis_premium",
            "funding",
            "listing_age_context",
        },
        "crowding_state": {
            "account_crowding",
            "position_crowding",
            "account_position_divergence",
            "cross_asset_market_state",
        },
    }
    slot_indices = {
        name: tuple(i for i, family in enumerate(field_family) if family in allowed)
        for name, allowed in slot_families.items()
    }
    split_counts: dict[str, Any] = {}
    sequence_length = int(config["model"]["sequence_length"])
    for name, block in slices.items():
        local_eligible = eligibility[:, block].copy()
        if block.start < sequence_length:
            local_eligible[:, : sequence_length - block.start] = False
        local_target = np.isfinite(target[:, block])
        split_counts[name] = {
            "timestamps": int(block.stop - block.start),
            "eligible_coordinates": int(local_eligible.sum()),
            "target_aligned_samples": int((local_eligible & local_target).sum()),
            "eligible_assets": int(np.any(local_eligible & local_target, axis=1).sum()),
        }
    field_rows = []
    train = slices["train"]
    for index, field in enumerate(fields):
        local = raw[:, index, train]
        field_rows.append(
            {
                "field_id": field,
                "field_family": field_family[index],
                "source_available": True,
                "PIT_qualified": True,
                "representation_materialized": True,
                "model_input_exposed": True,
                "nonmissing_ratio": float(np.isfinite(local).mean()),
                "variance": float(np.nanvar(local)),
                "eligible_asset_count": int(
                    np.any(np.isfinite(local) & eligibility[:, train], axis=1).sum()
                ),
                "effective_time_count": int(
                    np.any(np.isfinite(local) & eligibility[:, train], axis=0).sum()
                ),
            }
        )
    family_covered = len({row["field_family"] for row in field_rows if row["variance"] > 0})
    effective_fields = sum(
        row["nonmissing_ratio"] > 0.05 and row["variance"] > 0 for row in field_rows
    )
    gates = {
        "field_count": len(fields) >= int(config["data_adequacy"]["minimum_fields"]),
        "field_families": len(families)
        >= int(config["data_adequacy"]["minimum_field_families"]),
        "assets": split_counts["train"]["eligible_assets"]
        >= int(config["data_adequacy"]["minimum_assets"]),
        "train_timestamps": split_counts["train"]["timestamps"]
        >= int(config["data_adequacy"]["minimum_train_timestamps"]),
        "selection_timestamps": split_counts["selection"]["timestamps"]
        >= int(config["data_adequacy"]["minimum_selection_timestamps"]),
        "stability_timestamps": split_counts["stability"]["timestamps"]
        >= int(config["data_adequacy"]["minimum_stability_timestamps"]),
        "effective_sequences": split_counts["train"]["target_aligned_samples"]
        >= int(config["data_adequacy"]["minimum_effective_sequences"]),
        "family_coverage": family_covered / max(len(families), 1)
        >= float(config["data_adequacy"]["minimum_family_coverage_ratio"]),
        "model_input_exposure": effective_fields / max(len(fields), 1)
        >= float(config["data_adequacy"]["minimum_model_input_exposure_ratio"]),
        "structured_slots_nonempty": all(slot_indices.values()),
    }
    capability = {
        "schema_version": 1,
        "status": "DATA_ADEQUACY_PASS" if all(gates.values()) else "DATA_ADEQUACY_BLOCKED",
        "gates": gates,
        "panel_identity": store.metadata["identity_sha256"],
        "field_registry_sha256": registry["registry_sha256"],
        "fields": field_rows,
        "field_count": len(fields),
        "field_family_count": len(families),
        "effective_input_fields": effective_fields,
        "model_input_exposure_ratio": effective_fields / max(len(fields), 1),
        "family_coverage_ratio": family_covered / max(len(families), 1),
        "effective_input_dimensions": {
            "latent_values": len(fields),
            "latent_masks": len(fields),
            "known_deterministic": 4 * len(fields),
        },
        "slot_indices": {key: list(value) for key, value in slot_indices.items()},
        "split_counts": split_counts,
        "spent_report_only_reads": 0,
        "sealed_reads": 0,
    }
    write_json(runtime_root / "capability_gate.json", capability)
    del raw
    gc.collect()
    return PreparedData(
        store=store,
        fields=fields,
        families=families,
        field_family=field_family,
        values=values,
        masks=masks,
        target=target,
        target_scaled=target_scaled,
        target_scale=target_scale,
        volatility_scaled=volatility_scaled,
        volatility_scale=volatility_scale,
        eligibility=eligibility,
        timestamps=timestamps,
        slices=slices,
        slot_indices=slot_indices,
        capability=capability,
    )


def known_window(
    data: PreparedData, assets: np.ndarray | Sequence[int] | slice, left: int, right: int
) -> np.ndarray:
    context = max(0, left - 167)
    values = np.asarray(data.values[assets, :, context:right], dtype=np.float32)
    masks = np.asarray(data.masks[assets, :, context:right], dtype=bool)
    raw_like = np.where(masks, values, np.nan)
    mean24 = np.nan_to_num(causal_rolling_mean(raw_like, 24), nan=0.0)
    mean168 = np.nan_to_num(causal_rolling_mean(raw_like, 168), nan=0.0)
    delta24 = np.nan_to_num(shifted_delta(values, 24), nan=0.0)
    start = left - context
    return np.concatenate(
        [
            values[:, :, start:],
            mean24[:, :, start:],
            mean168[:, :, start:],
            delta24[:, :, start:],
        ],
        axis=1,
    ).astype(np.float32, copy=False)


class CausalBlock(nn.Module):
    def __init__(self, channels_in: int, channels_out: int, dilation: int, kernel: int, dropout: float):
        super().__init__()
        self.pad = (kernel - 1) * dilation
        self.conv = nn.Conv1d(channels_in, channels_out, kernel, dilation=dilation)
        self.norm = nn.GroupNorm(1, channels_out)
        self.dropout = nn.Dropout(dropout)
        self.skip = nn.Conv1d(channels_in, channels_out, 1) if channels_in != channels_out else nn.Identity()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        residual = self.skip(x)
        y = self.conv(nn.functional.pad(x, (self.pad, 0)))
        return torch.relu(self.norm(y) + residual)


class TCNEncoder(nn.Module):
    def __init__(self, inputs: int, channels: int, config: Mapping[str, Any]):
        super().__init__()
        layers: list[nn.Module] = []
        current = inputs
        for dilation in config["dilations"]:
            layers.append(
                CausalBlock(
                    current,
                    channels,
                    int(dilation),
                    int(config["kernel_size"]),
                    float(config["dropout"]),
                )
            )
            current = channels
        self.net = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class KnownEncoder(nn.Module):
    def __init__(self, inputs: int, hidden: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv1d(inputs, hidden, 1),
            nn.ReLU(),
            nn.Conv1d(hidden, 32, 1),
            nn.ReLU(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class LatentModel(nn.Module):
    def __init__(
        self,
        arm: str,
        field_count: int,
        known_count: int,
        config: Mapping[str, Any],
        slot_indices: Mapping[str, tuple[int, ...]],
    ):
        super().__init__()
        self.arm = arm
        self.field_count = field_count
        self.slot_indices = slot_indices
        self.known = KnownEncoder(known_count, int(config["known_hidden_channels"]))
        latent_inputs = field_count * 2
        if arm == ARM_E:
            self.slots = nn.ModuleDict()
            self.slot_reconstruction = nn.ModuleDict()
            for name, indices in slot_indices.items():
                inputs = len(indices) * 2
                self.slots[name] = TCNEncoder(
                    inputs, int(config["structured_slot_channels"]), config
                )
                self.slot_reconstruction[name] = nn.Conv1d(
                    int(config["structured_slot_channels"]), len(indices), 1
                )
            latent_width = int(config["structured_slot_channels"]) * len(slot_indices)
        else:
            self.latent = TCNEncoder(
                latent_inputs, int(config["latent_channels"]), config
            )
            self.reconstruction = nn.Conv1d(
                int(config["latent_channels"]), field_count, 1
            )
            latent_width = int(config["latent_channels"])
        head_inputs = {
            ARM_A: 32,
            ARM_B: latent_width,
            ARM_C: 32 + latent_width,
            ARM_D: latent_width,
            ARM_E: 32 + latent_width,
        }[arm]
        self.return_head = nn.Conv1d(head_inputs, 1, 1)
        self.vol_head = nn.Conv1d(head_inputs, 1, 1)

    def forward(
        self,
        values: torch.Tensor,
        masks: torch.Tensor,
        known: torch.Tensor,
        *,
        frozen_known_prediction: torch.Tensor | None = None,
        slot_drop: str | None = None,
    ) -> Mapping[str, torch.Tensor]:
        known_repr = self.known(known)
        reconstruction: torch.Tensor | None = None
        slot_repr: dict[str, torch.Tensor] = {}
        if self.arm == ARM_E:
            recon = torch.zeros(
                values.shape[0], self.field_count, values.shape[2], device=values.device
            )
            for name, indices in self.slot_indices.items():
                index = torch.as_tensor(indices, dtype=torch.long, device=values.device)
                local = torch.cat(
                    [values.index_select(1, index), masks.index_select(1, index)], dim=1
                )
                encoded = self.slots[name](local)
                if slot_drop == name:
                    encoded = torch.zeros_like(encoded)
                slot_repr[name] = encoded
                recon.index_copy_(1, index, self.slot_reconstruction[name](encoded))
            latent_repr = torch.cat(list(slot_repr.values()), dim=1)
            reconstruction = recon
        elif self.arm != ARM_A:
            latent_repr = self.latent(torch.cat([values, masks], dim=1))
            reconstruction = self.reconstruction(latent_repr)
        if self.arm == ARM_A:
            combined = known_repr
        elif self.arm == ARM_B:
            combined = latent_repr
        elif self.arm == ARM_D:
            combined = latent_repr
        else:
            combined = torch.cat([known_repr, latent_repr], dim=1)
        prediction = self.return_head(combined).squeeze(1)
        if self.arm == ARM_D:
            if frozen_known_prediction is None:
                raise ValueError("Residual arm requires frozen Known prediction")
            prediction = prediction + frozen_known_prediction
        return {
            "prediction": prediction,
            "volatility": self.vol_head(combined).squeeze(1),
            "reconstruction": reconstruction,
            "known_repr": known_repr,
            "latent_repr": latent_repr if self.arm != ARM_A else known_repr,
            **{f"slot_{name}": value for name, value in slot_repr.items()},
        }


def parameter_count(model: nn.Module) -> int:
    return sum(item.numel() for item in model.parameters() if item.requires_grad)


def segment_batch(
    data: PreparedData,
    block: slice,
    *,
    rng: np.random.Generator,
    batch_assets: int,
    segment_length: int,
) -> tuple[torch.Tensor, ...]:
    history = 168
    right_min = max(block.start + segment_length, history + segment_length)
    right = int(rng.integers(right_min, block.stop + 1))
    left = right - segment_length
    eligible_assets = np.flatnonzero(
        np.any(
            data.eligibility[:, left:right] & np.isfinite(data.target[:, left:right]),
            axis=1,
        )
    )
    if eligible_assets.size < batch_assets:
        raise ValueError("insufficient eligible assets for batch")
    assets = rng.choice(eligible_assets, size=batch_assets, replace=False)
    values = torch.from_numpy(data.values[assets, :, left:right].copy())
    masks = torch.from_numpy(data.masks[assets, :, left:right].copy()).float()
    known = torch.from_numpy(known_window(data, assets, left, right))
    target = torch.from_numpy(data.target_scaled[assets, left:right].copy())
    volatility = torch.from_numpy(data.volatility_scaled[assets, left:right].copy())
    eligible = torch.from_numpy(
        (
            data.eligibility[assets, left:right]
            & np.isfinite(data.target[assets, left:right])
            & np.isfinite(data.volatility_scaled[assets, left:right])
        ).copy()
    )
    return values, masks, known, target, volatility, eligible


def masked_inputs(
    values: torch.Tensor, masks: torch.Tensor, probability: float, generator: torch.Generator
) -> tuple[torch.Tensor, torch.Tensor]:
    draw = torch.rand(values.shape, generator=generator, device=values.device)
    masked = (draw < probability) & masks.bool()
    result = values.clone()
    result[masked] = 0.0
    return result, masked


def loss_for_batch(
    model: LatentModel,
    batch: tuple[torch.Tensor, ...],
    config: Mapping[str, Any],
    generator: torch.Generator,
    frozen_known: LatentModel | None,
) -> tuple[torch.Tensor, Mapping[str, float], Mapping[str, torch.Tensor]]:
    values, masks, known, target, volatility, eligible = batch
    corrupted, reconstruction_mask = masked_inputs(
        values,
        masks,
        float(config["model"]["masked_reconstruction_probability"]),
        generator,
    )
    frozen_prediction = None
    if frozen_known is not None:
        with torch.no_grad():
            frozen_prediction = frozen_known(values, masks, known)["prediction"]
    output = model(
        corrupted,
        masks,
        known,
        frozen_known_prediction=frozen_prediction,
    )
    valid = eligible & torch.isfinite(target)
    if not valid.any():
        raise ValueError("batch has no valid target")
    return_loss = nn.functional.smooth_l1_loss(output["prediction"][valid], target[valid])
    vol_valid = eligible & torch.isfinite(volatility)
    vol_loss = nn.functional.smooth_l1_loss(
        output["volatility"][vol_valid], volatility[vol_valid]
    )
    reconstruction = output["reconstruction"]
    if reconstruction is None or not reconstruction_mask.any():
        recon_loss = torch.zeros((), dtype=return_loss.dtype)
    else:
        recon_loss = nn.functional.smooth_l1_loss(
            reconstruction[reconstruction_mask], values[reconstruction_mask]
        )
    total = (
        float(config["model"]["return_loss_weight"]) * return_loss
        + float(config["model"]["volatility_loss_weight"]) * vol_loss
        + float(config["model"]["reconstruction_loss_weight"]) * recon_loss
    )
    return total, {
        "return_loss": float(return_loss.detach()),
        "volatility_loss": float(vol_loss.detach()),
        "reconstruction_loss": float(recon_loss.detach()),
        "total_loss": float(total.detach()),
    }, output


def evaluate_loss(
    model: LatentModel,
    data: PreparedData,
    block: slice,
    config: Mapping[str, Any],
    *,
    seed: int,
    frozen_known: LatentModel | None,
    batches: int = 4,
) -> float:
    model.eval()
    rng = np.random.default_rng(seed)
    generator = torch.Generator().manual_seed(seed)
    values: list[float] = []
    with torch.no_grad():
        for _ in range(batches):
            batch = segment_batch(
                data,
                block,
                rng=rng,
                batch_assets=int(config["training"]["batch_assets"]),
                segment_length=int(config["training"]["segment_length"]),
            )
            loss, _, _ = loss_for_batch(model, batch, config, generator, frozen_known)
            values.append(float(loss))
    model.train()
    return float(np.mean(values))


def load_model(
    arm: str,
    data: PreparedData,
    config: Mapping[str, Any],
    checkpoint: Path | None = None,
) -> LatentModel:
    model = LatentModel(
        arm,
        len(data.fields),
        4 * len(data.fields),
        config["model"],
        data.slot_indices,
    )
    if checkpoint is not None:
        model.load_state_dict(torch.load(checkpoint, map_location="cpu", weights_only=True))
    return model


def train_model(
    *,
    arm: str,
    seed: int,
    data: PreparedData,
    config: Mapping[str, Any],
    checkpoint: Path,
    steps: int,
    pilot: bool,
    known_checkpoint: Path | None = None,
) -> Mapping[str, Any]:
    set_determinism(seed, int(config["training"]["torch_threads"]))
    model = load_model(arm, data, config)
    frozen_known = (
        load_model(ARM_A, data, config, known_checkpoint) if known_checkpoint else None
    )
    if frozen_known is not None:
        frozen_known.eval()
        for parameter in frozen_known.parameters():
            parameter.requires_grad_(False)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=float(config["training"]["learning_rate"]),
        weight_decay=float(config["training"]["weight_decay"]),
    )
    rng = np.random.default_rng(seed)
    generator = torch.Generator().manual_seed(seed)
    started = time.perf_counter()
    process = psutil.Process()
    peak_rss = process.memory_info().rss
    history: list[Mapping[str, Any]] = []
    best = math.inf
    stale = 0
    interval = int(config["training"]["selection_check_interval"])
    for step in range(1, steps + 1):
        batch = segment_batch(
            data,
            data.slices["train"],
            rng=rng,
            batch_assets=int(config["training"]["batch_assets"]),
            segment_length=int(config["training"]["segment_length"]),
        )
        optimizer.zero_grad(set_to_none=True)
        loss, parts, output = loss_for_batch(
            model, batch, config, generator, frozen_known
        )
        if not torch.isfinite(loss):
            raise FloatingPointError("non-finite training loss")
        loss.backward()
        gradient_norm = float(
            nn.utils.clip_grad_norm_(
                model.parameters(), float(config["model"]["gradient_clip_norm"])
            )
        )
        if not math.isfinite(gradient_norm):
            raise FloatingPointError("non-finite gradient")
        optimizer.step()
        peak_rss = max(peak_rss, process.memory_info().rss)
        if step == 1 or step % interval == 0 or step == steps:
            selection_loss = evaluate_loss(
                model,
                data,
                data.slices["selection"],
                config,
                seed=seed + step,
                frozen_known=frozen_known,
                batches=2 if pilot else 4,
            )
            row = {
                "step": step,
                **parts,
                "selection_loss": selection_loss,
                "gradient_norm": gradient_norm,
                "prediction_variance": float(output["prediction"].detach().var()),
                "latent_variance": float(output["latent_repr"].detach().var()),
            }
            history.append(row)
            if selection_loss < best - 1e-7:
                best = selection_loss
                stale = 0
                checkpoint.parent.mkdir(parents=True, exist_ok=True)
                torch.save(model.state_dict(), checkpoint)
            else:
                stale += 1
            if not pilot and stale >= int(config["training"]["early_stop_patience_checks"]):
                break
    elapsed = time.perf_counter() - started
    if not checkpoint.exists():
        checkpoint.parent.mkdir(parents=True, exist_ok=True)
        torch.save(model.state_dict(), checkpoint)
    result = {
        "arm": arm,
        "seed": seed,
        "pilot": pilot,
        "requested_steps": steps,
        "completed_steps": history[-1]["step"],
        "elapsed_seconds": elapsed,
        "seconds_per_step": elapsed / max(history[-1]["step"], 1),
        "peak_rss_bytes": int(peak_rss),
        "parameter_count": parameter_count(model),
        "checkpoint": str(checkpoint),
        "checkpoint_sha256": file_sha(checkpoint),
        "history": history,
        "loss_finite": all(math.isfinite(float(row["total_loss"])) for row in history),
        "gradient_finite": all(math.isfinite(float(row["gradient_norm"])) for row in history),
        "prediction_noncollapsed": all(float(row["prediction_variance"]) > 1e-12 for row in history),
        "representation_noncollapsed": all(float(row["latent_variance"]) > 1e-12 for row in history),
    }
    result["status"] = (
        "PASS"
        if all(
            result[key]
            for key in (
                "loss_finite",
                "gradient_finite",
                "prediction_noncollapsed",
                "representation_noncollapsed",
            )
        )
        else "MODEL_FIT_DEGENERATE"
    )
    return result


def predict_block(
    model: LatentModel,
    data: PreparedData,
    block: slice,
    *,
    config: Mapping[str, Any],
    frozen_known: LatentModel | None = None,
    slot_drop: str | None = None,
) -> tuple[np.ndarray, Mapping[str, Any]]:
    model.eval()
    if frozen_known is not None:
        frozen_known.eval()
    history = int(config["model"]["sequence_length"])
    left = max(0, block.start - history)
    predictions = np.full(
        (data.values.shape[0], block.stop - block.start), np.nan, dtype=np.float32
    )
    latent_variances: list[float] = []
    known_latent_correlations: list[float] = []
    batch_assets = 16
    with torch.no_grad():
        for start in range(0, data.values.shape[0], batch_assets):
            stop = min(start + batch_assets, data.values.shape[0])
            values = torch.from_numpy(data.values[start:stop, :, left:block.stop].copy())
            masks = torch.from_numpy(
                data.masks[start:stop, :, left:block.stop].copy()
            ).float()
            known = torch.from_numpy(
                known_window(data, slice(start, stop), left, block.stop)
            )
            frozen_prediction = None
            if frozen_known is not None:
                frozen_prediction = frozen_known(values, masks, known)["prediction"]
            output = model(
                values,
                masks,
                known,
                frozen_known_prediction=frozen_prediction,
                slot_drop=slot_drop,
            )
            offset = block.start - left
            local = output["prediction"][:, offset:].numpy() * data.target_scale
            predictions[start:stop] = local.astype(np.float32)
            latent = output["latent_repr"][:, offset:].numpy()
            known_repr = output["known_repr"][:, offset:].numpy()
            latent_variances.append(float(np.var(latent)))
            common = min(latent.shape[1], known_repr.shape[1])
            x = latent[:, :common].reshape(-1)
            y = known_repr[:, :common].reshape(-1)
            if np.std(x) > 0 and np.std(y) > 0:
                known_latent_correlations.append(float(np.corrcoef(x, y)[0, 1]))
    predictions[
        ~(
            data.eligibility[:, block]
            & np.isfinite(data.target[:, block])
        )
    ] = np.nan
    return predictions, {
        "latent_variance": float(np.mean(latent_variances)),
        "known_latent_correlation": (
            float(np.mean(known_latent_correlations))
            if known_latent_correlations
            else None
        ),
        "prediction_variance": float(np.nanvar(predictions)),
        "prediction_unique_rounded_1e8": int(
            np.unique(np.round(predictions[np.isfinite(predictions)], 8)).size
        ),
    }


def economic_metrics(
    prediction: np.ndarray, data: PreparedData, block: slice
) -> tuple[Mapping[str, Any], np.ndarray]:
    mapped = map_portfolio(
        prediction,
        DEFAULT_MAPPING_CONTRACTS[CROSS_SECTIONAL_ZERO_NET],
    )
    weights = np.asarray(mapped.weights, dtype=float)
    timestamps = data.timestamps[block]
    months = np.asarray(
        [str(np.datetime64(int(value), "ns"))[:7] for value in timestamps], dtype=str
    )
    target = np.asarray(data.target[:, block], dtype=float)
    active = np.abs(weights) > 1e-12
    missing_target = np.any(active & ~np.isfinite(target), axis=0)
    evaluation_mask = (
        (data.eligibility[:, block].sum(axis=0) >= 3)
        & ~missing_target
        & np.any(np.isfinite(prediction), axis=0)
    )
    metrics = _series_metrics(
        weights=weights,
        target=target,
        months=months,
        evaluation_mask=evaluation_mask,
        horizon=4,
    )
    return metrics, weights


def paired_increment(
    candidate_weights: np.ndarray,
    baseline_weights: np.ndarray,
    data: PreparedData,
    block: slice,
) -> Mapping[str, Any]:
    delta = candidate_weights - baseline_weights
    timestamps = data.timestamps[block]
    months = np.asarray(
        [str(np.datetime64(int(value), "ns"))[:7] for value in timestamps], dtype=str
    )
    target = np.asarray(data.target[:, block], dtype=float)
    evaluation_mask = data.eligibility[:, block].sum(axis=0) >= 3
    return _series_metrics(
        weights=delta,
        target=target,
        months=months,
        evaluation_mask=evaluation_mask,
        horizon=4,
    )


def baseline_models(
    data: PreparedData, config: Mapping[str, Any]
) -> list[Mapping[str, Any]]:
    rng = np.random.default_rng(20260717)
    train = data.slices["train"]
    valid = data.eligibility[:, train] & np.isfinite(data.target[:, train])
    assets, times = np.where(valid)
    cap = min(100000, len(assets))
    chosen = rng.choice(len(assets), size=cap, replace=False)
    selected_assets = assets[chosen]
    selected_times = times[chosen]
    x = np.empty((cap, 4 * len(data.fields)), dtype=np.float32)
    for asset in np.unique(selected_assets):
        rows = np.flatnonzero(selected_assets == asset)
        local = known_window(data, [int(asset)], train.start, train.stop)[0]
        x[rows] = local[:, selected_times[rows]].T
    y = data.target[selected_assets, train.start + selected_times]
    results = []
    for name, model in (
        ("RIDGE", Ridge(alpha=10.0)),
        (
            "HIST_GRADIENT_BOOSTING",
            HistGradientBoostingRegressor(
                max_iter=100, max_leaf_nodes=31, learning_rate=0.05, random_state=20260717
            ),
        ),
    ):
        started = time.perf_counter()
        model.fit(x, y)
        results.append(
            {
                "record_type": "matched_control",
                "control": name,
                "train_samples": cap,
                "fit_seconds": time.perf_counter() - started,
                "feature_count": int(x.shape[1]),
                "train_score": float(model.score(x, y)),
            }
        )
    return results


def _monthly_not_single_driver(metrics: Mapping[str, Any]) -> bool:
    rows = [row for row in metrics["month_metrics"] if row["net_mean"] is not None]
    if len(rows) < 2:
        return False
    values = np.asarray([row["net_mean"] for row in rows], dtype=float)
    return bool(np.median(values) > 0.0 and np.sum(values > 0.0) >= math.ceil(len(values) / 2))


def adaptive_decision(
    economics: Sequence[Mapping[str, Any]],
    representations: Sequence[Mapping[str, Any]],
) -> Mapping[str, Any]:
    stability = [
        row for row in economics if row["record_type"] == "economic" and row["split"] == "stability"
    ]
    candidates: dict[str, list[Mapping[str, Any]]] = {ARM_D: [], ARM_E: []}
    for row in stability:
        if row["arm"] in candidates:
            candidates[row["arm"]].append(row)
    gates: dict[str, Any] = {}
    for arm, rows in candidates.items():
        increments = np.asarray([row["increment"]["net_mean"] for row in rows], dtype=float)
        gate = {
            "three_seed_rows": len(rows) == 3,
            "aggregate_increment_positive": bool(len(rows) == 3 and np.mean(increments) > 0),
            "two_of_three_positive": bool(np.sum(increments > 0) >= 2),
            "not_single_month_driven": bool(
                len(rows) == 3
                and sum(_monthly_not_single_driver(row["increment"]) for row in rows) >= 2
            ),
            "prediction_noncollapsed": all(row["model"]["prediction_variance"] > 1e-12 for row in rows),
            "not_turnover_only": bool(
                len(rows) == 3
                and np.mean([row["increment"]["gross_mean"] for row in rows]) > 0
            ),
        }
        gate["pass"] = all(gate.values())
        gates[arm] = gate
    winners = [arm for arm, gate in gates.items() if gate["pass"]]
    return {
        "schema_version": 1,
        "status": (
            "CRYPTO_LATENT_ADAPTIVE_SIGNAL_OBSERVED"
            if winners
            else "ADAPTIVE_NO_STABLE_LATENT_INCREMENT"
        ),
        "winning_arms": winners,
        "arm_gates": gates,
        "evidence_scope": "ADAPTIVE_DEVELOPMENT_ONLY",
        "spent_report_only_access": "NOT_PERFORMED",
        "spent_report_only_reads": 0,
        "sealed_reads": 0,
        "oos_grade": "NONE",
        "promotion_implication": "NONE",
    }


def build_contracts(
    repo_root: Path, config: Mapping[str, Any], runtime_root: Path
) -> None:
    source_paths = {
        name: repo_root / value
        for name, value in config["source"].items()
        if name != "panel_cache"
    }
    contract = {
        "schema_version": 1,
        "experiment_id": config["experiment_id"],
        "question_answered": "Whether fixed small TCN residual or structured proxy latent representations add stable 4h adaptive-development increment over a strong deterministic Known State baseline.",
        "question_not_answered": [
            "independent report-only qualification",
            "OOS validity",
            "causal market ecology",
            "promotion readiness",
        ],
        "evidence_scope": "ADAPTIVE_DEVELOPMENT_ONLY",
        "authorization": config["authorization"],
        "economic_contract": config["economic_contract"],
        "budget": config["budget"],
        "source_sha": current_sha(repo_root),
        "source_files": {
            name: {"path": str(path.relative_to(repo_root)), "sha256": file_sha(path)}
            for name, path in source_paths.items()
        },
        "spent_report_only_reads": 0,
        "sealed_reads": 0,
    }
    binding = {
        "schema_version": 1,
        "splits": config["splits"],
        "panel_cache": config["source"]["panel_cache"],
        "panel_metadata_sha256": file_sha(
            repo_root / config["source"]["panel_cache"] / "metadata.json"
        ),
        "spent_report_only_access": "NOT_AUTHORIZED",
        "sealed_reads": 0,
    }
    write_json(runtime_root / "experiment_contract.json", contract)
    write_json(runtime_root / "data_and_split_binding.json", binding)


def environment_payload(config: Mapping[str, Any]) -> Mapping[str, Any]:
    return {
        "machine": platform.node(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "python_executable": os.sys.executable,
        "torch": torch.__version__,
        "torch_cuda_available": torch.cuda.is_available(),
        "torch_cuda_version": torch.version.cuda,
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "cpu_count": psutil.cpu_count(logical=True),
        "ram_bytes": psutil.virtual_memory().total,
        "torch_threads": config["training"]["torch_threads"],
    }


def run_experiment(
    repo_root: Path,
    config_path: Path,
    *,
    stage: str = "all",
) -> Mapping[str, Any]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    runtime_root = repo_root / config["outputs"]["runtime_root"]
    report_root = repo_root / config["outputs"]["report_root"]
    artifact_root = repo_root / config["outputs"]["artifact_root"]
    runtime_root.mkdir(parents=True, exist_ok=True)
    report_root.mkdir(parents=True, exist_ok=True)
    artifact_root.mkdir(parents=True, exist_ok=True)
    build_contracts(repo_root, config, runtime_root)
    data = prepare_data(repo_root, config, runtime_root)
    budget = {
        "schema_version": 1,
        "environment": environment_payload(config),
        "training": config["training"],
        "model": config["model"],
        "budget": config["budget"],
        "status": "FROZEN_BEFORE_PILOT",
    }
    write_json(runtime_root / "model_pack.json", budget)
    if data.capability["status"] != "DATA_ADEQUACY_PASS":
        decision = {
            "status": "DATA_ADEQUACY_BLOCKED",
            "capability": data.capability,
            "spent_report_only_reads": 0,
            "sealed_reads": 0,
        }
        write_json(runtime_root / "decision.json", decision)
        return decision
    checkpoint_root = artifact_root / "checkpoints"
    metrics: list[Mapping[str, Any]] = []
    pilot_results: list[Mapping[str, Any]] = []
    pilot_known = checkpoint_root / "pilot" / f"{ARM_A}_{config['training']['pilot_seed']}.pt"
    for arm in ARMS:
        checkpoint = checkpoint_root / "pilot" / f"{arm}_{config['training']['pilot_seed']}.pt"
        result = train_model(
            arm=arm,
            seed=int(config["training"]["pilot_seed"]),
            data=data,
            config=config,
            checkpoint=checkpoint,
            steps=int(config["training"]["pilot_steps"]),
            pilot=True,
            known_checkpoint=pilot_known if arm == ARM_D else None,
        )
        pilot_results.append(result)
        metrics.append({"record_type": "pilot", **result})
    pilot_status = (
        "PASS"
        if all(row["status"] == "PASS" for row in pilot_results)
        else "MODEL_FIT_DEGENERATE"
    )
    projected_cpu_hours = (
        sum(row["seconds_per_step"] for row in pilot_results)
        / len(pilot_results)
        * int(config["training"]["formal_steps"])
        * int(config["budget"]["formal_neural_jobs"])
        / 3600.0
    )
    budget["pilot_results"] = pilot_results
    budget["projected_formal_cpu_wall_hours"] = projected_cpu_hours
    budget["status"] = (
        "PILOT_PASS_BUDGET_PASS"
        if pilot_status == "PASS"
        and projected_cpu_hours <= float(config["budget"]["max_total_cpu_hours"])
        else "MODEL_FIT_DEGENERATE"
        if pilot_status != "PASS"
        else "RESOURCE_BUDGET_BLOCKED"
    )
    write_json(runtime_root / "model_pack.json", budget)
    if stage == "stage0" or budget["status"] != "PILOT_PASS_BUDGET_PASS":
        decision = {
            "status": (
                "REPRESENTATION_CAPABILITY_INCOMPLETE"
                if budget["status"] == "RESOURCE_BUDGET_BLOCKED"
                else "MODEL_FIT_DEGENERATE"
                if pilot_status != "PASS"
                else "STAGE0_COMPLETED"
            ),
            "projected_formal_cpu_wall_hours": projected_cpu_hours,
            "spent_report_only_reads": 0,
            "sealed_reads": 0,
        }
        write_metrics(runtime_root / "metrics.parquet", metrics)
        write_json(runtime_root / "decision.json", decision)
        return decision
    formal_results: list[Mapping[str, Any]] = []
    checkpoints: dict[tuple[str, int], Path] = {}
    for arm in (ARM_A, ARM_B, ARM_C, ARM_E, ARM_D):
        for seed in config["training"]["seeds"]:
            seed = int(seed)
            checkpoint = checkpoint_root / "formal" / f"{arm}_{seed}.pt"
            known_checkpoint = checkpoints.get((ARM_A, seed)) if arm == ARM_D else None
            result = train_model(
                arm=arm,
                seed=seed,
                data=data,
                config=config,
                checkpoint=checkpoint,
                steps=int(config["training"]["formal_steps"]),
                pilot=False,
                known_checkpoint=known_checkpoint,
            )
            if result["status"] != "PASS":
                decision = {
                    "status": "MODEL_FIT_DEGENERATE",
                    "failed_run": result,
                    "spent_report_only_reads": 0,
                    "sealed_reads": 0,
                }
                write_json(runtime_root / "decision.json", decision)
                return decision
            checkpoints[(arm, seed)] = checkpoint
            formal_results.append(result)
            metrics.append({"record_type": "seed_diagnostic", **result})
    metrics.extend(baseline_models(data, config))
    economics: list[Mapping[str, Any]] = []
    representations: list[Mapping[str, Any]] = []
    prediction_cache: dict[tuple[str, int, str], tuple[np.ndarray, np.ndarray]] = {}
    for split in ("selection", "stability"):
        block = data.slices[split]
        for seed in config["training"]["seeds"]:
            seed = int(seed)
            baseline_weights = None
            for arm in ARMS:
                model = load_model(arm, data, config, checkpoints[(arm, seed)])
                frozen_known = (
                    load_model(ARM_A, data, config, checkpoints[(ARM_A, seed)])
                    if arm == ARM_D
                    else None
                )
                prediction, representation = predict_block(
                    model, data, block, config=config, frozen_known=frozen_known
                )
                model_metrics, weights = economic_metrics(prediction, data, block)
                if arm == ARM_A:
                    baseline_weights = weights
                increment = (
                    paired_increment(weights, baseline_weights, data, block)
                    if arm != ARM_A and baseline_weights is not None
                    else None
                )
                row = {
                    "record_type": "economic",
                    "split": split,
                    "arm": arm,
                    "seed": seed,
                    "model": model_metrics,
                    "increment": increment,
                    "prediction_sha256": array_sha(
                        np.nan_to_num(prediction, nan=9.87654321e20)
                    ),
                }
                economics.append(row)
                metrics.append(row)
                rep_row = {
                    "record_type": "representation",
                    "split": split,
                    "arm": arm,
                    "seed": seed,
                    **representation,
                }
                representations.append(rep_row)
                metrics.append(rep_row)
                prediction_cache[(arm, seed, split)] = (prediction, weights)
    for seed in config["training"]["seeds"]:
        seed = int(seed)
        model = load_model(ARM_E, data, config, checkpoints[(ARM_E, seed)])
        for slot in data.slot_indices:
            prediction, representation = predict_block(
                model,
                data,
                data.slices["stability"],
                config=config,
                slot_drop=slot,
            )
            model_metrics, weights = economic_metrics(
                prediction, data, data.slices["stability"]
            )
            full_weights = prediction_cache[(ARM_E, seed, "stability")][1]
            metrics.append(
                {
                    "record_type": "slot_ablation",
                    "seed": seed,
                    "slot": slot,
                    "method": "INFERENCE_ZERO_OUT",
                    "model": model_metrics,
                    "increment_vs_full": paired_increment(
                        weights, full_weights, data, data.slices["stability"]
                    ),
                    **representation,
                }
            )
    decision = adaptive_decision(economics, representations)
    write_json(runtime_root / "decision.json", decision)
    checkpoint_manifest = {
        "schema_version": 1,
        "checkpoints": [
            {
                "arm": arm,
                "seed": seed,
                "path": str(path.relative_to(repo_root)),
                "sha256": file_sha(path),
                "bytes": path.stat().st_size,
            }
            for (arm, seed), path in sorted(checkpoints.items())
        ],
    }
    write_json(runtime_root / "checkpoint_manifest.json", checkpoint_manifest)
    write_metrics(runtime_root / "metrics.parquet", metrics)
    report = [
        "# Crypto Explicit Latent Adaptive V1",
        "",
        f"Final status: `{decision['status']}`",
        "",
        "- Evidence scope: adaptive development only.",
        "- Spent report-only reads: 0.",
        "- Sealed reads: 0.",
        "- Formula search remains frozen.",
        "- Strict OOS and promotion remain unauthorized.",
        "",
        "## Capability",
        "",
        f"- Fields exposed: {data.capability['effective_input_fields']} / {data.capability['field_count']}",
        f"- Families: {data.capability['field_family_count']}",
        f"- Model-input exposure: {data.capability['model_input_exposure_ratio']:.4f}",
        f"- Projected CPU wall hours: {projected_cpu_hours:.3f}",
        "",
        "## Adaptive gate",
        "",
        "```json",
        json.dumps(decision["arm_gates"], indent=2, sort_keys=True),
        "```",
    ]
    (report_root / "REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    artifacts = []
    for path in sorted(runtime_root.glob("*")):
        if path.is_file():
            artifacts.append(
                {
                    "path": str(path.relative_to(repo_root)),
                    "sha256": file_sha(path),
                    "bytes": path.stat().st_size,
                }
            )
    report_path = report_root / "REPORT.md"
    artifacts.append(
        {
            "path": str(report_path.relative_to(repo_root)),
            "sha256": file_sha(report_path),
            "bytes": report_path.stat().st_size,
        }
    )
    manifest = {
        "schema_version": 1,
        "experiment_id": config["experiment_id"],
        "source_sha": current_sha(repo_root),
        "artifacts": artifacts,
        "artifact_root_hash": payload_sha(artifacts),
        "spent_report_only_reads": 0,
        "sealed_reads": 0,
    }
    write_json(runtime_root / "artifact_manifest.json", manifest)
    return decision


__all__ = [
    "ARMS",
    "LatentModel",
    "PreparedData",
    "array_sha",
    "causal_rolling_mean",
    "future_volatility",
    "payload_sha",
    "run_experiment",
    "shifted_delta",
]
