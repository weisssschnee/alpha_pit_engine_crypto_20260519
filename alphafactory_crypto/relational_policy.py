"""Small cross-asset, cost-aware direct-weight vertical slice.

This module deliberately stops at one development-only capability path.  It
does not merge the Broad and Core3 contexts, implement a search controller, or
claim economic evidence from its smoke run.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pandas as pd
import torch
from torch import nn
from torch.nn import functional as F

from alphafactory_crypto.broad_search.panel18m import RawPanelStore
from alphafactory_crypto.instrument_canary.evaluator import evaluate_real_mapping
from alphafactory_crypto.instrument_capability.mapping import (
    DIRECT_ZERO_NET_COST_AWARE,
    validate_direct_weights,
)


EXPECTED_FIELD_VIEW_COUNTS = {
    "BROAD_ASSET_LOCAL": 38,
    "BROAD_MARKET_STATE": 1,
    "CORE3_ASSET_LOCAL_BASE": 31,
    "CORE3_CROSS_SYMBOL_BASE": 5,
    "CORE3_TEMPORAL_DERIVED": 45,
}


def _payload_sha256(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest().upper()


def resolve_field_views(
    repo_root: Path, config: Mapping[str, Any]
) -> dict[str, tuple[str, ...]]:
    """Project the committed 120-token contract into five context-local views."""

    contract_path = repo_root / str(config["inputs"]["resolved_core_pack"])
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    tokens = list(contract["tokens"])
    views: dict[str, tuple[str, ...]] = {}
    matched_token_ids: list[str] = []
    for name, selector in config["field_views"].items():
        families = set(selector.get("families", []))
        excluded = set(selector.get("exclude_families", []))
        rows = [
            row
            for row in tokens
            if row["context_id"] == selector["context_id"]
            and row["token_kind"] == selector["token_kind"]
            and (not families or row["family"] in families)
            and row["family"] not in excluded
        ]
        views[name] = tuple(str(row["field_id"]) for row in rows)
        matched_token_ids.extend(str(row["token_id"]) for row in rows)
    actual_counts = {name: len(rows) for name, rows in views.items()}
    if actual_counts != EXPECTED_FIELD_VIEW_COUNTS:
        raise ValueError(f"field view contract changed: {actual_counts}")
    if len(matched_token_ids) != len(set(matched_token_ids)):
        raise ValueError("field views overlap")
    contract_token_ids = {str(row["token_id"]) for row in tokens}
    if set(matched_token_ids) != contract_token_ids:
        raise ValueError("field views do not exactly cover the 120-token contract")
    return views


@dataclass(frozen=True, slots=True)
class DynamicUniverseBatch:
    asset_values: torch.Tensor
    market_values: torch.Tensor
    eligibility: torch.Tensor
    previous_weights: torch.Tensor
    target_returns: torch.Tensor

    def validate(self) -> None:
        if self.asset_values.ndim != 4:
            raise ValueError("asset_values must have shape [batch,history,asset,feature]")
        batch, history, assets, _ = self.asset_values.shape
        if self.market_values.ndim != 3 or self.market_values.shape[:2] != (
            batch,
            history,
        ):
            raise ValueError("market_values must have shape [batch,history,feature]")
        if self.eligibility.shape != (batch, history, assets):
            raise ValueError("eligibility must have shape [batch,history,asset]")
        if self.previous_weights.shape != (batch, assets):
            raise ValueError("previous_weights must have shape [batch,asset]")
        if self.target_returns.shape != (batch, assets):
            raise ValueError("target_returns must have shape [batch,asset]")
        for name, values in (
            ("asset_values", self.asset_values),
            ("market_values", self.market_values),
            ("previous_weights", self.previous_weights),
            ("target_returns", self.target_returns),
        ):
            if not torch.isfinite(values).all():
                raise ValueError(f"{name} must be finite")
        if torch.any(self.eligibility[:, -1].sum(dim=1) < 3):
            raise ValueError("every decision coordinate needs at least three eligible assets")


class RelationalCostAwarePolicy(nn.Module):
    """Causal temporal encoder plus permutation-equivariant asset attention."""

    def __init__(
        self,
        *,
        asset_features: int,
        market_features: int,
        hidden_size: int,
        attention_heads: int,
        temporal_kernel: int,
        gross_cap: float = 1.0,
        position_cap: float = 0.20,
    ) -> None:
        super().__init__()
        if hidden_size % attention_heads:
            raise ValueError("hidden_size must be divisible by attention_heads")
        if temporal_kernel < 1 or gross_cap <= 0 or position_cap <= 0:
            raise ValueError("invalid policy dimensions or portfolio caps")
        self.temporal_kernel = int(temporal_kernel)
        self.gross_cap = float(gross_cap)
        self.position_cap = float(position_cap)
        self.temporal = nn.Conv1d(
            int(asset_features + market_features + 1),
            int(hidden_size),
            kernel_size=self.temporal_kernel,
        )
        self.state = nn.Linear(int(hidden_size + 1), int(hidden_size))
        self.attention = nn.MultiheadAttention(
            int(hidden_size), int(attention_heads), dropout=0.0, batch_first=True
        )
        self.normalization = nn.LayerNorm(int(hidden_size))
        self.action = nn.Linear(int(hidden_size + 1), 1)

    def _project(self, scores: torch.Tensor, eligible: torch.Tensor) -> torch.Tensor:
        available = eligible.to(dtype=scores.dtype)
        count = available.sum(dim=1, keepdim=True).clamp_min(1.0)
        centered = (scores - (scores * available).sum(dim=1, keepdim=True) / count) * available
        gross = centered.abs().sum(dim=1, keepdim=True)
        normalized = centered / gross.clamp_min(1e-8) * self.gross_cap
        maximum = normalized.abs().amax(dim=1, keepdim=True)
        cap_scale = torch.clamp(self.position_cap / maximum.clamp_min(1e-8), max=1.0)
        valid = (eligible.sum(dim=1, keepdim=True) >= 3) & (gross > 1e-8)
        return torch.where(valid, normalized * cap_scale, torch.zeros_like(normalized))

    def forward(
        self,
        asset_values: torch.Tensor,
        market_values: torch.Tensor,
        eligibility: torch.Tensor,
        previous_weights: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        batch, history, assets, _ = asset_values.shape
        market = market_values[:, :, None, :].expand(-1, -1, assets, -1)
        historical_eligibility = eligibility.unsqueeze(-1).to(dtype=asset_values.dtype)
        temporal_input = torch.cat(
            (asset_values * historical_eligibility, market, historical_eligibility), dim=-1
        )
        temporal_input = temporal_input.permute(0, 2, 3, 1).reshape(
            batch * assets, temporal_input.shape[-1], history
        )
        encoded = self.temporal(F.pad(temporal_input, (self.temporal_kernel - 1, 0)))
        encoded = F.gelu(encoded[:, :, -1]).reshape(batch, assets, -1)
        state = F.gelu(self.state(torch.cat((encoded, previous_weights.unsqueeze(-1)), dim=-1)))
        current_eligible = eligibility[:, -1]
        attended, _ = self.attention(
            state, state, state, key_padding_mask=~current_eligible, need_weights=False
        )
        representation = self.normalization(state + attended)
        scores = self.action(
            torch.cat((representation, previous_weights.unsqueeze(-1)), dim=-1)
        ).squeeze(-1)
        scores = torch.where(current_eligible, scores, torch.zeros_like(scores))
        return self._project(scores, current_eligible), scores


def direct_net_utility_loss(
    weights: torch.Tensor,
    previous_weights: torch.Tensor,
    target_returns: torch.Tensor,
    *,
    cost_bps: float,
    target_horizon_hours: int = 1,
    terminal_liquidation: bool = True,
) -> torch.Tensor:
    gross, _, cost = _direct_utility_paths(
        weights,
        previous_weights,
        target_returns,
        cost_bps=cost_bps,
        target_horizon_hours=target_horizon_hours,
        terminal_liquidation=terminal_liquidation,
    )
    return -(gross - cost).mean()


def _direct_utility_paths(
    weights: torch.Tensor,
    previous_weights: torch.Tensor,
    target_returns: torch.Tensor,
    *,
    cost_bps: float,
    target_horizon_hours: int,
    terminal_liquidation: bool,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    if weights.shape != previous_weights.shape or weights.shape != target_returns.shape:
        raise ValueError("weights, previous_weights and target_returns must share shape")
    horizon = int(target_horizon_hours)
    if horizon not in (1, 4):
        raise ValueError("target horizon is outside the frozen sleeve contract")
    scale = 1.0 / float(horizon)
    gross = (weights * target_returns).sum(dim=1) * scale
    turnover = (weights - previous_weights).abs().sum(dim=1) * scale
    if terminal_liquidation and weights.shape[0]:
        terminal = torch.zeros_like(turnover)
        for offset in range(min(horizon, weights.shape[0])):
            index = weights.shape[0] - 1 - (
                (weights.shape[0] - 1 - offset) % horizon
            )
            terminal[index] = terminal[index] + weights[index].abs().sum() * scale
        turnover = turnover + terminal
    cost = turnover * float(cost_bps) / 10_000.0
    return gross, turnover, cost


def _rollout_policy(
    model: RelationalCostAwarePolicy,
    batch: DynamicUniverseBatch,
    *,
    target_horizon_hours: int,
    detach_state: bool,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Roll each horizon-offset sleeve with its own previous portfolio."""

    weights: list[torch.Tensor] = []
    scores: list[torch.Tensor] = []
    previous: list[torch.Tensor] = []
    horizon = int(target_horizon_hours)
    for index in range(batch.asset_values.shape[0]):
        if index < horizon:
            state = batch.previous_weights[index]
        else:
            state = weights[index - horizon]
            if detach_state:
                state = state.detach()
        local_weights, local_scores = model(
            batch.asset_values[index : index + 1],
            batch.market_values[index : index + 1],
            batch.eligibility[index : index + 1],
            state.unsqueeze(0),
        )
        previous.append(state)
        weights.append(local_weights.squeeze(0))
        scores.append(local_scores.squeeze(0))
    return torch.stack(weights), torch.stack(scores), torch.stack(previous)


def _normalize_with_missing(values: np.ndarray, axes: tuple[int, ...]) -> np.ndarray:
    finite = np.isfinite(values)
    median = np.nanmedian(values, axis=axes, keepdims=True)
    q25 = np.nanquantile(values, 0.25, axis=axes, keepdims=True)
    q75 = np.nanquantile(values, 0.75, axis=axes, keepdims=True)
    scale = (q75 - q25) / 1.349
    scale = np.where(np.isfinite(scale) & (scale > 1e-8), scale, 1.0)
    normalized = np.clip((values - median) / scale, -8.0, 8.0)
    normalized = np.nan_to_num(normalized, nan=0.0, posinf=8.0, neginf=-8.0)
    return np.concatenate((normalized, finite.astype(np.float32)), axis=-1).astype(np.float32)


def load_broad_smoke_batch(
    repo_root: Path, config: Mapping[str, Any]
) -> tuple[DynamicUniverseBatch, dict[str, Any]]:
    """Load a tiny, real, train-only Broad batch with one stable asset set."""

    views = resolve_field_views(repo_root, config)
    smoke = config["smoke"]
    store = RawPanelStore.open(repo_root / str(config["inputs"]["broad_cache"]))
    timestamps = np.asarray(store.timestamp_ns, dtype=np.int64)
    declared_end = pd.Timestamp(smoke["end_exclusive"])
    sealed_boundary = pd.Timestamp(config["boundaries"]["latest_timestamp_exclusive"])
    if declared_end > sealed_boundary:
        raise ValueError("smoke window crosses the declared development boundary")
    start = int(np.searchsorted(timestamps, pd.Timestamp(smoke["start"]).value, side="left"))
    stop = int(
        np.searchsorted(timestamps, declared_end.value, side="left")
    )
    history = int(smoke["history_hours"])
    decisions = int(smoke["decision_coordinates"])
    if start < history - 1 or start + decisions > stop:
        raise ValueError("smoke window does not satisfy history/development boundaries")
    decision_times = np.arange(start, start + decisions, dtype=int)
    horizon = int(smoke["target_horizon_hours"])
    target_end = pd.Timestamp(int(timestamps[decision_times[-1]]), tz="UTC") + pd.Timedelta(
        hours=horizon
    )
    if target_end >= declared_end or target_end >= sealed_boundary:
        raise ValueError("smoke target horizon crosses the development boundary")
    target_store = np.asarray(store.target_return(horizon), dtype=np.float32)
    base_eligible = np.asarray(store.base_eligible(), dtype=bool)
    # Universe membership and coverage ranking are frozen at the first
    # decision coordinate.  Later coordinates may invalidate the smoke, but
    # may not reach backward and influence which assets were selected.
    candidate = base_eligible[:, start]
    candidate_indices = np.flatnonzero(candidate)
    requested_assets = int(smoke["assets"])
    probe_symbols = tuple(str(value) for value in smoke.get("dynamic_membership_probe_symbols", []))
    symbol_to_index = {symbol: index for index, symbol in enumerate(store.symbols)}
    try:
        probe_indices = np.asarray([symbol_to_index[symbol] for symbol in probe_symbols], dtype=int)
    except KeyError as error:
        raise ValueError(f"unknown dynamic-membership probe symbol: {error.args[0]}") from error
    stable_assets = requested_assets - len(probe_indices)
    if stable_assets < 3 or candidate_indices.size < stable_assets:
        raise ValueError("not enough stable eligible assets for the real smoke batch")
    asset_fields = views["BROAD_ASSET_LOCAL"]
    market_fields = views["BROAD_MARKET_STATE"]
    history_start = start - history + 1
    coverage = np.zeros(candidate_indices.size, dtype=float)
    asset_arrays = {field: store.field(field) for field in asset_fields}
    for values in asset_arrays.values():
        coverage += np.isfinite(values[candidate_indices, history_start : start + 1]).mean(axis=1)
    ranked = candidate_indices[np.argsort(-coverage, kind="stable")]
    ranked = ranked[~np.isin(ranked, probe_indices)]
    selected = np.concatenate((ranked[:stable_assets], probe_indices))
    if not np.isfinite(target_store[selected[:, None], decision_times[None, :]]).all():
        raise ValueError("first-coordinate asset set lacks complete smoke targets")
    decision_eligibility = base_eligible[selected[:, None], decision_times[None, :]].T
    decision_transitions = int(
        np.count_nonzero(np.diff(decision_eligibility.astype(np.int8), axis=0))
    )
    if bool(smoke.get("require_dynamic_membership_transition", False)) and not decision_transitions:
        raise ValueError("real smoke lacks a dynamic-universe membership transition")

    asset_batches: list[np.ndarray] = []
    market_batches: list[np.ndarray] = []
    eligibility_batches: list[np.ndarray] = []
    for decision in decision_times:
        block = slice(decision - history + 1, decision + 1)
        raw_assets = np.stack(
            [np.asarray(asset_arrays[field][selected, block], dtype=np.float32).T for field in asset_fields],
            axis=-1,
        )
        asset_batches.append(_normalize_with_missing(raw_assets, (0, 1)))
        raw_market = np.stack(
            [
                np.nanmedian(np.asarray(store.field(field)[:, block], dtype=np.float32), axis=0)
                for field in market_fields
            ],
            axis=-1,
        )
        market_batches.append(_normalize_with_missing(raw_market, (0,)))
        eligibility_batches.append(base_eligible[selected, block].T)
    targets = target_store[selected[:, None], decision_times[None, :]].T
    batch = DynamicUniverseBatch(
        asset_values=torch.from_numpy(np.stack(asset_batches)),
        market_values=torch.from_numpy(np.stack(market_batches)),
        eligibility=torch.from_numpy(np.stack(eligibility_batches)),
        previous_weights=torch.zeros((decisions, requested_assets), dtype=torch.float32),
        target_returns=torch.from_numpy(np.asarray(targets, dtype=np.float32)),
    )
    batch.validate()
    metadata = {
        "asset_ids": [store.symbols[index] for index in selected],
        "decision_timestamps": [
            pd.Timestamp(int(timestamps[index]), tz="UTC").isoformat()
            for index in decision_times
        ],
        "field_view_counts": {name: len(fields) for name, fields in views.items()},
        "field_view_identity_sha256": _payload_sha256(views),
        "source_contract_identity_sha256": json.loads(
            (repo_root / str(config["inputs"]["resolved_core_pack"])).read_text(
                encoding="utf-8"
            )
        )["identity_sha256"],
        "historical_eligibility_transitions": int(
            np.count_nonzero(
                np.diff(np.stack(eligibility_batches).astype(np.int8), axis=1)
            )
        ),
        "historical_ineligible_cells": int(
            np.count_nonzero(~np.stack(eligibility_batches))
        ),
        "decision_eligibility_transitions": decision_transitions,
    }
    return batch, metadata


def run_vertical_slice_smoke(
    repo_root: Path, config: Mapping[str, Any]
) -> dict[str, Any]:
    started = time.perf_counter()
    if any(
        bool(config["boundaries"][name])
        for name in (
            "sealed_reads_allowed",
            "formal_performance_search",
            "hyperparameter_search",
            "candidate_promotion",
            "cross_sprint_adaptive_memory",
        )
    ):
        raise ValueError("vertical-slice smoke requires every sealed/search boundary to stay false")
    smoke = config["smoke"]
    torch.manual_seed(int(smoke["seed"]))
    torch.set_num_threads(min(4, max(1, torch.get_num_threads())))
    batch, metadata = load_broad_smoke_batch(repo_root, config)
    model = RelationalCostAwarePolicy(
        asset_features=int(batch.asset_values.shape[-1]),
        market_features=int(batch.market_values.shape[-1]),
        hidden_size=int(smoke["hidden_size"]),
        attention_heads=int(smoke["attention_heads"]),
        temporal_kernel=int(smoke["temporal_kernel"]),
        gross_cap=float(smoke["gross_cap"]),
        position_cap=float(smoke["position_cap"]),
    )
    optimizer = torch.optim.Adam(model.parameters(), lr=float(smoke["learning_rate"]))
    weights, _, previous_weights = _rollout_policy(
        model,
        batch,
        target_horizon_hours=int(smoke["target_horizon_hours"]),
        detach_state=True,
    )
    loss = direct_net_utility_loss(
        weights,
        previous_weights,
        batch.target_returns,
        cost_bps=float(smoke["cost_bps"]),
        target_horizon_hours=int(smoke["target_horizon_hours"]),
        terminal_liquidation=True,
    )
    optimizer.zero_grad(set_to_none=True)
    loss.backward()
    gradient_l1 = sum(
        float(parameter.grad.abs().sum())
        for parameter in model.parameters()
        if parameter.grad is not None
    )
    optimizer.step()
    model.eval()
    with torch.no_grad():
        weights, scores, previous_weights = _rollout_policy(
            model,
            batch,
            target_horizon_hours=int(smoke["target_horizon_hours"]),
            detach_state=False,
        )
        permutation = torch.arange(weights.shape[1] - 1, -1, -1)
        permuted_batch = DynamicUniverseBatch(
            asset_values=batch.asset_values[:, :, permutation],
            market_values=batch.market_values,
            eligibility=batch.eligibility[:, :, permutation],
            previous_weights=batch.previous_weights[:, permutation],
            target_returns=batch.target_returns[:, permutation],
        )
        permuted_weights, _, _ = _rollout_policy(
            model,
            permuted_batch,
            target_horizon_hours=int(smoke["target_horizon_hours"]),
            detach_state=False,
        )
    permutation_error = float(
        (permuted_weights - weights[:, permutation]).abs().max()
    )
    mapped = validate_direct_weights(
        weights.numpy().T, batch.eligibility[:, -1].numpy().T
    )
    months = np.asarray([value[:7] for value in metadata["decision_timestamps"]])
    evaluation = evaluate_real_mapping(
        mapped,
        scores.numpy().T,
        batch.target_returns.numpy().T,
        months,
        target_horizon_hours=int(smoke["target_horizon_hours"]),
        expected_mapping_id=DIRECT_ZERO_NET_COST_AWARE,
    )
    _, training_turnover, training_cost = _direct_utility_paths(
        weights,
        previous_weights,
        batch.target_returns,
        cost_bps=float(smoke["cost_bps"]),
        target_horizon_hours=int(smoke["target_horizon_hours"]),
        terminal_liquidation=True,
    )
    elapsed = float(time.perf_counter() - started)
    if elapsed > float(smoke["maximum_wall_seconds"]):
        raise RuntimeError(f"vertical-slice smoke exceeded wall budget: {elapsed:.3f}s")
    return {
        "status": "PASS",
        "scope": "DEVELOPMENT_ONLY_ARCHITECTURE_SMOKE_NOT_ECONOMIC_EVIDENCE",
        "capability_id": config["capability_id"],
        "field_views": metadata["field_view_counts"],
        "field_view_identity_sha256": metadata["field_view_identity_sha256"],
        "source_contract_identity_sha256": metadata["source_contract_identity_sha256"],
        "real_asset_count": len(metadata["asset_ids"]),
        "real_decision_coordinates": len(metadata["decision_timestamps"]),
        "historical_eligibility_transitions": metadata[
            "historical_eligibility_transitions"
        ],
        "historical_ineligible_cells": metadata["historical_ineligible_cells"],
        "decision_eligibility_transitions": metadata[
            "decision_eligibility_transitions"
        ],
        "nonzero_previous_weight_coordinates": int(
            torch.count_nonzero(previous_weights.abs().sum(dim=1) > 1e-8)
        ),
        "first_decision_timestamp": metadata["decision_timestamps"][0],
        "last_decision_timestamp": metadata["decision_timestamps"][-1],
        "gradient_l1": gradient_l1,
        "asset_permutation_max_error": permutation_error,
        "maximum_abs_weight": float(np.abs(mapped.weights).max()),
        "maximum_abs_net_exposure": float(np.abs(mapped.weights.sum(axis=0)).max()),
        "maximum_ineligible_current_weight": float(
            np.abs(mapped.weights[~batch.eligibility[:, -1].numpy().T]).max(initial=0.0)
        ),
        "strict_evaluator_mapping_id": evaluation.mapping_id,
        "strict_evaluator_total_turnover_l1": evaluation.total_turnover_l1,
        "strict_evaluator_total_cost": evaluation.total_cost,
        "training_evaluator_turnover_identity_closed": bool(
            np.isclose(float(training_turnover.sum()), evaluation.total_turnover_l1)
        ),
        "training_evaluator_cost_identity_closed": bool(
            np.isclose(float(training_cost.sum()), evaluation.total_cost)
        ),
        "wall_seconds": elapsed,
        "boundaries": dict(config["boundaries"]),
    }
