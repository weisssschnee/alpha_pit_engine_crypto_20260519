"""Small cross-asset, cost-aware direct-weight vertical slice.

This module deliberately stops at one development-only capability path.  It
does not merge the Broad and Core3 contexts, implement a search controller, or
claim economic evidence from its smoke run.
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
import torch
from torch import nn
from torch.nn import functional as F

from alphafactory_crypto.broad_search.panel18m import RawPanelStore
from alphafactory_crypto.broad_information_arena import array_sha256, prediction_metrics
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

TEMPORAL_ONLY_ARM = "TEMPORAL_ONLY"
RELATIONAL_ARM = "RELATIONAL"
SHIFTED_RELATIONAL_NULL_ARM = "SHIFTED_RELATIONAL_NULL"
STAGE1_ARMS = (
    TEMPORAL_ONLY_ARM,
    RELATIONAL_ARM,
    SHIFTED_RELATIONAL_NULL_ARM,
)


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


class RelationalAttributionModel(nn.Module):
    """One score-only model used by all three Stage-1 attribution arms.

    The temporal path is asset-local and consumes the full causal window.  A
    runs the shared attention module on one asset at a time, B attends only to
    other current eligible assets, and N uses the current query/residual with
    stale peer keys/values.  The three arms therefore have identical parameter
    keys and counts; only the admitted information path changes.
    """

    def __init__(
        self,
        *,
        asset_features: int,
        market_features: int,
        hidden_size: int,
        attention_heads: int,
        temporal_kernel: int,
    ) -> None:
        super().__init__()
        if hidden_size % attention_heads:
            raise ValueError("hidden_size must be divisible by attention_heads")
        if temporal_kernel < 1:
            raise ValueError("temporal_kernel must be positive")
        self.temporal_kernel = int(temporal_kernel)
        self.temporal = nn.Conv1d(
            int(asset_features + market_features + 1),
            int(hidden_size),
            kernel_size=self.temporal_kernel,
        )
        self.state = nn.Linear(int(hidden_size), int(hidden_size))
        self.attention = nn.MultiheadAttention(
            int(hidden_size), int(attention_heads), dropout=0.0, batch_first=True
        )
        self.normalization = nn.LayerNorm(int(hidden_size))
        self.forecast = nn.Linear(int(hidden_size), 1)

    def _encode(
        self,
        asset_values: torch.Tensor,
        market_values: torch.Tensor,
        eligibility: torch.Tensor,
    ) -> torch.Tensor:
        if asset_values.ndim != 4:
            raise ValueError("asset_values must have shape [batch,history,asset,feature]")
        batch, history, assets, _ = asset_values.shape
        if market_values.ndim != 3 or market_values.shape[:2] != (batch, history):
            raise ValueError("market_values must have shape [batch,history,feature]")
        if eligibility.shape != (batch, history, assets):
            raise ValueError("eligibility must have shape [batch,history,asset]")
        market = market_values[:, :, None, :].expand(-1, -1, assets, -1)
        historical = eligibility.unsqueeze(-1).to(dtype=asset_values.dtype)
        temporal_input = torch.cat(
            (asset_values * historical, market, historical), dim=-1
        )
        temporal_input = temporal_input.permute(0, 2, 3, 1).reshape(
            batch * assets, temporal_input.shape[-1], history
        )
        encoded = F.gelu(
            self.temporal(F.pad(temporal_input, (self.temporal_kernel - 1, 0)))
        )
        mask = eligibility.permute(0, 2, 1).reshape(batch * assets, 1, history)
        mask = mask.to(dtype=encoded.dtype)
        pooled = (encoded * mask).sum(dim=2) / mask.sum(dim=2).clamp_min(1.0)
        # The last causal convolution preserves local recency while the masked
        # mean makes every point in the 168-hour window reachable.
        state = F.gelu(self.state(encoded[:, :, -1] + pooled))
        return state.reshape(batch, assets, -1)

    def forward(
        self,
        *,
        arm: str,
        asset_values: torch.Tensor,
        market_values: torch.Tensor,
        eligibility: torch.Tensor,
        shifted_peer_values: torch.Tensor,
        shifted_peer_eligibility: torch.Tensor,
    ) -> torch.Tensor:
        if arm not in STAGE1_ARMS:
            raise ValueError(f"unknown Stage-1 arm: {arm}")
        current = self._encode(asset_values, market_values, eligibility)
        current_eligible = eligibility[:, -1]
        if torch.any(current_eligible.sum(dim=1) < 3):
            raise ValueError("every decision coordinate needs at least three eligible assets")
        batch, assets, hidden = current.shape
        if arm == TEMPORAL_ONLY_ARM:
            self_only = current.reshape(batch * assets, 1, hidden)
            attended, _ = self.attention(
                self_only, self_only, self_only, need_weights=False
            )
            attended = attended.reshape(batch, assets, hidden)
        else:
            if arm == RELATIONAL_ARM:
                peer = current
            else:
                if shifted_peer_values.shape != asset_values.shape:
                    raise ValueError("shifted peer values must preserve current input shape")
                if shifted_peer_eligibility.shape != eligibility.shape:
                    raise ValueError("shifted peer eligibility must preserve current mask shape")
                # The shared market path intentionally remains current.  Only
                # peer asset K/V is stale, so N controls relational synchrony
                # without removing the current common market context.
                peer = self._encode(
                    shifted_peer_values, market_values, shifted_peer_eligibility
                )
            exclude_self = torch.eye(assets, device=current.device, dtype=torch.bool)
            attended, _ = self.attention(
                current,
                peer,
                peer,
                attn_mask=exclude_self,
                key_padding_mask=~current_eligible,
                need_weights=False,
            )
        representation = self.normalization(current + attended)
        score = self.forecast(representation).squeeze(-1)
        return torch.where(current_eligible, score, torch.zeros_like(score))


def identical_initialized_models(
    *,
    arms: tuple[str, ...],
    seed: int,
    asset_features: int,
    market_features: int,
    hidden_size: int,
    attention_heads: int,
    temporal_kernel: int,
) -> dict[str, RelationalAttributionModel]:
    """Construct capacity-identical arm models with exactly matched weights."""

    if tuple(arms) != STAGE1_ARMS:
        raise ValueError("Stage-1 arm identity or order changed")
    models: dict[str, RelationalAttributionModel] = {}
    for arm in arms:
        torch.manual_seed(int(seed))
        models[arm] = RelationalAttributionModel(
            asset_features=int(asset_features),
            market_features=int(market_features),
            hidden_size=int(hidden_size),
            attention_heads=int(attention_heads),
            temporal_kernel=int(temporal_kernel),
        )
    return models


def decide_stage1(
    pair_rows: list[Mapping[str, Any]],
    config: Mapping[str, Any],
    *,
    relational_nondegenerate: bool,
    b_a_outputs_differ: bool,
) -> dict[str, Any]:
    """Apply the pre-registered 4/6 block gate without dropping bad seeds."""

    seeds = tuple(int(value) for value in config["training"]["seeds"])
    blocks = tuple(
        str(row["block_id"]) for row in config["splits"]["attribution_blocks"]
    )
    pairs = ("B_MINUS_A", "B_MINUS_N")
    floor = float(config["decision"]["primary_mse_delta_floor"])
    minimum = int(config["decision"]["minimum_winning_blocks"])
    indexed = {
        (str(row["pair"]), int(row["seed"]), str(row["block_id"])): float(
            row["primary_delta"]
        )
        for row in pair_rows
        if row.get("row_type") == "PAIR_DELTA"
    }
    complete = all(
        (pair, seed, block) in indexed
        for pair in pairs
        for seed in seeds
        for block in blocks
    )
    block_summary: dict[str, list[dict[str, Any]]] = {}
    seed_summary: dict[str, list[dict[str, Any]]] = {}
    for pair in pairs:
        block_rows: list[dict[str, Any]] = []
        for block in blocks:
            values = [
                indexed[(pair, seed, block)]
                for seed in seeds
                if (pair, seed, block) in indexed
            ]
            mean = float(np.mean(values)) if len(values) == len(seeds) else None
            block_rows.append(
                {
                    "block_id": block,
                    "mean_primary_delta": mean,
                    "win": bool(mean is not None and mean > floor),
                }
            )
        block_summary[pair] = block_rows
        local_seed_rows: list[dict[str, Any]] = []
        for seed in seeds:
            values = [
                indexed[(pair, seed, block)]
                for block in blocks
                if (pair, seed, block) in indexed
            ]
            local_seed_rows.append(
                {
                    "seed": seed,
                    "blocks_present": len(values),
                    "winning_blocks": int(sum(value > floor for value in values)),
                    "mean_primary_delta": float(np.mean(values)) if values else None,
                }
            )
        seed_summary[pair] = local_seed_rows
    aggregate_pass = {
        pair: int(sum(row["win"] for row in block_summary[pair])) >= minimum
        for pair in pairs
    }
    require_seed_wins = bool(
        config["decision"].get("require_each_seed_minimum_winning_blocks", False)
    )
    require_seed_direction = bool(
        config["decision"].get("require_each_seed_positive_mean_delta", True)
    )
    seed_consistent = complete and all(
        (not require_seed_wins or row["winning_blocks"] >= minimum)
        and (
            not require_seed_direction
            or (
                row["mean_primary_delta"] is not None
                and row["mean_primary_delta"] > floor
            )
        )
        for pair in pairs
        for row in seed_summary[pair]
    )
    if not relational_nondegenerate or not b_a_outputs_differ:
        status = "RELATIONAL_REPRESENTATION_COMPARISON_DEGENERATE"
    elif not complete:
        status = "RELATIONAL_INCREMENT_UNSTABLE"
    elif not aggregate_pass["B_MINUS_A"]:
        status = "RELATIONAL_REPRESENTATION_INCREMENT_NOT_ESTABLISHED"
    elif not aggregate_pass["B_MINUS_N"]:
        status = "APPARENT_GAIN_NOT_ATTRIBUTABLE_TO_SYNCHRONIZED_CROSS_ASSET_RELATION"
    elif not seed_consistent:
        status = "RELATIONAL_INCREMENT_UNSTABLE"
    else:
        status = str(config["decision"]["pass_status"])
    return {
        "status": status,
        "complete_fixed_denominator": complete,
        "primary_mse_delta_floor": floor,
        "minimum_winning_blocks": minimum,
        "aggregate_pass": aggregate_pass,
        "seed_consistent": seed_consistent,
        "block_summary": block_summary,
        "seed_summary": seed_summary,
        "relational_nondegenerate": bool(relational_nondegenerate),
        "b_a_outputs_differ": bool(b_a_outputs_differ),
        "stage2_execution_authorized": False,
    }


@dataclass(frozen=True, slots=True)
class Stage1Scaler:
    asset_median: np.ndarray
    asset_scale: np.ndarray
    market_median: np.ndarray
    market_scale: np.ndarray
    identity_sha256: str


@dataclass(slots=True)
class Stage1Context:
    store: RawPanelStore
    asset_fields: tuple[str, ...]
    market_fields: tuple[str, ...]
    selected_asset_indices: np.ndarray
    field_arrays: tuple[np.ndarray, ...]
    market_series: np.ndarray
    eligibility: np.ndarray
    target: np.ndarray
    timestamps: np.ndarray
    scaler: Stage1Scaler
    schedules: dict[str, np.ndarray]
    schedule_identity_sha256: str

    @property
    def selected_symbols(self) -> tuple[str, ...]:
        return tuple(self.store.symbols[index] for index in self.selected_asset_indices)


@dataclass(frozen=True, slots=True)
class Stage1Batch:
    asset_values: torch.Tensor
    market_values: torch.Tensor
    eligibility: torch.Tensor
    shifted_peer_values: torch.Tensor
    shifted_peer_eligibility: torch.Tensor
    target_returns: torch.Tensor
    target_valid: torch.Tensor
    decision_indices: np.ndarray
    donor_current_membership_mismatch: float

    def model_inputs(self) -> dict[str, torch.Tensor]:
        return {
            "asset_values": self.asset_values,
            "market_values": self.market_values,
            "eligibility": self.eligibility,
            "shifted_peer_values": self.shifted_peer_values,
            "shifted_peer_eligibility": self.shifted_peer_eligibility,
        }


def _robust_center_scale(
    values: np.ndarray, *, axis: int
) -> tuple[np.ndarray, np.ndarray]:
    with np.errstate(invalid="ignore"):
        median = np.nanmedian(values, axis=axis)
        q25 = np.nanquantile(values, 0.25, axis=axis)
        q75 = np.nanquantile(values, 0.75, axis=axis)
    scale = (q75 - q25) / 1.349
    median = np.where(np.isfinite(median), median, 0.0)
    scale = np.where(np.isfinite(scale) & (scale > 1e-8), scale, 1.0)
    return median.astype(np.float32), scale.astype(np.float32)


def _purged_slice(
    store: RawPanelStore, spec: Mapping[str, str], purge_hours: int
) -> slice:
    block = store.block_slice(str(spec["start"]), str(spec["end_exclusive"]))
    if block.stop - block.start <= int(purge_hours):
        raise ValueError("attribution block is shorter than its label purge")
    return slice(int(block.start), int(block.stop) - int(purge_hours))


def _schedule_payload(
    schedules: Mapping[str, np.ndarray], timestamps: np.ndarray
) -> dict[str, Any]:
    return {
        name: {
            "coordinates": [int(value) for value in coordinates],
            "timestamps": [
                pd.Timestamp(int(timestamps[value]), tz="UTC").isoformat()
                for value in coordinates
            ],
        }
        for name, coordinates in schedules.items()
    }


def load_stage1_context(
    repo_root: Path, config: Mapping[str, Any]
) -> Stage1Context:
    """Load the frozen Broad view without cross-asset preprocessing leakage."""

    boundaries = config["boundaries"]
    for name in (
        "sealed_reads_allowed",
        "formal_performance_search",
        "hyperparameter_search",
        "candidate_promotion",
        "stage2_execution",
        "cross_sprint_adaptive_memory",
        "economic_claim",
        "oos_claim",
    ):
        if bool(boundaries[name]):
            raise PermissionError(f"forbidden Stage-1 boundary enabled: {name}")
    stage0 = json.loads(
        (repo_root / str(config["inputs"]["stage0_config"])).read_text(
            encoding="utf-8"
        )
    )
    views = resolve_field_views(repo_root, stage0)
    asset_fields = views["BROAD_ASSET_LOCAL"]
    market_fields = views["BROAD_MARKET_STATE"]
    if str(stage0["inputs"]["resolved_core_pack"]) != str(
        config["inputs"]["resolved_core_pack"]
    ):
        raise ValueError("Stage-0 and Stage-1 resolved token authorities differ")
    resolved = json.loads(
        (repo_root / str(config["inputs"]["resolved_core_pack"])).read_text(
            encoding="utf-8"
        )
    )
    broad_rows = [
        row
        for row in resolved["tokens"]
        if row["context_id"] == "BROAD_PANEL_BASELINE" and row["token_kind"] == "BASE"
    ]
    expected_asset_fields = tuple(
        str(row["field_id"])
        for row in broad_rows
        if row["family"] != "cross_asset_market_state"
    )
    expected_market_fields = tuple(
        str(row["field_id"])
        for row in broad_rows
        if row["family"] == "cross_asset_market_state"
    )
    if asset_fields != expected_asset_fields or market_fields != expected_market_fields:
        raise ValueError("Stage-1 consumed fields diverge from the resolved 120-token contract")
    contract = config["data_contract"]
    if len(asset_fields) != int(contract["asset_local_fields"]) or len(
        market_fields
    ) != int(contract["market_state_fields"]):
        raise ValueError("Stage-1 Broad 38+1 field contract changed")
    if (
        int(contract["role_tail_purge_hours"])
        != int(contract["execution_delay_hours"])
        + int(contract["target_horizon_hours"])
    ):
        raise ValueError("role-tail purge must equal execution delay plus target horizon")
    if int(contract["peer_shift_hours"]) <= int(contract["history_hours"]) - 1:
        raise ValueError("stale peer window overlaps the current temporal window")
    store = RawPanelStore.open(repo_root / str(config["inputs"]["broad_cache"]))
    timestamps = np.asarray(store.timestamp_ns, dtype=np.int64)
    boundary_index = int(
        np.searchsorted(
            timestamps,
            pd.Timestamp(boundaries["latest_timestamp_exclusive"]).value,
            side="left",
        )
    )
    purge = int(contract["role_tail_purge_hours"])
    fit_slice = _purged_slice(store, config["splits"]["model_fit"], purge)
    eligibility = store.base_eligible()
    fit_coverage = np.asarray(eligibility[:, fit_slice].sum(axis=1), dtype=np.int64)
    stable_symbols = np.asarray(store.symbols, dtype=str)
    order = np.lexsort((stable_symbols, -fit_coverage))
    asset_count = int(contract["asset_universe_size"])
    if asset_count < 3 or len(order) < asset_count:
        raise ValueError("frozen Stage-1 asset universe is unavailable")
    selected = np.asarray(order[:asset_count], dtype=np.int64)
    if np.count_nonzero(fit_coverage[selected]) < asset_count:
        raise ValueError("Stage-1 asset universe includes no-history assets")
    field_arrays = tuple(store.field(field) for field in asset_fields)
    market_arrays = tuple(store.field(field) for field in market_fields)

    asset_median = np.empty((asset_count, len(asset_fields)), dtype=np.float32)
    asset_scale = np.empty_like(asset_median)
    for index, values in enumerate(field_arrays):
        median, scale = _robust_center_scale(
            np.asarray(values[selected, fit_slice], dtype=np.float32), axis=1
        )
        asset_median[:, index] = median
        asset_scale[:, index] = scale
    market_series = np.stack(
        [
            np.nanmedian(
                np.asarray(values[:, :boundary_index], dtype=np.float32), axis=0
            )
            for values in market_arrays
        ],
        axis=-1,
    ).astype(np.float32)
    market_median, market_scale = _robust_center_scale(
        market_series[fit_slice], axis=0
    )
    scaler_identity = _payload_sha256(
        {
            "asset_median": array_sha256(asset_median),
            "asset_scale": array_sha256(asset_scale),
            "market_median": array_sha256(market_median),
            "market_scale": array_sha256(market_scale),
            "fit_start": int(fit_slice.start),
            "fit_stop": int(fit_slice.stop),
            "selected_symbols": [store.symbols[index] for index in selected],
        }
    )
    scaler = Stage1Scaler(
        asset_median=asset_median,
        asset_scale=asset_scale,
        market_median=market_median,
        market_scale=market_scale,
        identity_sha256=scaler_identity,
    )
    history = int(contract["history_hours"])
    shift = int(contract["peer_shift_hours"])
    stride = int(contract["coordinate_stride_hours"])
    fit_first = int(fit_slice.start) + history + shift - 1
    schedules: dict[str, np.ndarray] = {
        "MODEL_FIT": np.arange(fit_first, int(fit_slice.stop), stride, dtype=np.int64)
    }
    for block in config["splits"]["attribution_blocks"]:
        local = _purged_slice(store, block, purge)
        coordinates = np.arange(int(local.start), int(local.stop), stride, dtype=np.int64)
        if len(coordinates) == 0 or int(coordinates[0]) - shift - history + 1 < 0:
            raise ValueError(f"block lacks causal shifted-peer history: {block['block_id']}")
        schedules[str(block["block_id"])] = coordinates
    expected = int(config["training"]["expected_training_coordinates"])
    if len(schedules["MODEL_FIT"]) != expected:
        raise ValueError(
            f"training coordinate contract changed: {len(schedules['MODEL_FIT'])} != {expected}"
        )
    if max(int(values[-1]) for values in schedules.values()) >= boundary_index:
        raise PermissionError("Stage-1 schedule crosses its development boundary")
    schedule_identity = _payload_sha256(_schedule_payload(schedules, timestamps))
    return Stage1Context(
        store=store,
        asset_fields=asset_fields,
        market_fields=market_fields,
        selected_asset_indices=selected,
        field_arrays=field_arrays,
        market_series=market_series,
        eligibility=eligibility,
        target=store.target_return(int(contract["target_horizon_hours"])),
        timestamps=timestamps,
        scaler=scaler,
        schedules=schedules,
        schedule_identity_sha256=schedule_identity,
    )


def _normalize_stage1_asset_window(
    raw: np.ndarray, scaler: Stage1Scaler
) -> np.ndarray:
    finite = np.isfinite(raw)
    normalized = np.clip(
        (raw - scaler.asset_median[None, :, :])
        / scaler.asset_scale[None, :, :],
        -8.0,
        8.0,
    )
    normalized = np.nan_to_num(normalized, nan=0.0, posinf=8.0, neginf=-8.0)
    return np.concatenate((normalized, finite.astype(np.float32)), axis=-1).astype(
        np.float32
    )


def _normalize_stage1_market_window(
    raw: np.ndarray, scaler: Stage1Scaler
) -> np.ndarray:
    finite = np.isfinite(raw)
    normalized = np.clip(
        (raw - scaler.market_median[None, :]) / scaler.market_scale[None, :],
        -8.0,
        8.0,
    )
    normalized = np.nan_to_num(normalized, nan=0.0, posinf=8.0, neginf=-8.0)
    return np.concatenate((normalized, finite.astype(np.float32)), axis=-1).astype(
        np.float32
    )


def materialize_stage1_batch(
    context: Stage1Context,
    config: Mapping[str, Any],
    decision_indices: Sequence[int],
) -> Stage1Batch:
    contract = config["data_contract"]
    history = int(contract["history_hours"])
    shift = int(contract["peer_shift_hours"])
    selected = context.selected_asset_indices
    current_values: list[np.ndarray] = []
    shifted_values: list[np.ndarray] = []
    markets: list[np.ndarray] = []
    current_eligibility: list[np.ndarray] = []
    shifted_eligibility: list[np.ndarray] = []
    targets: list[np.ndarray] = []
    target_valid: list[np.ndarray] = []
    mismatch: list[float] = []
    indices = np.asarray(decision_indices, dtype=np.int64)
    if indices.ndim != 1 or not len(indices):
        raise ValueError("at least one Stage-1 decision coordinate is required")
    for decision in indices:
        decision = int(decision)
        current_start = decision - history + 1
        donor_end = decision - shift
        donor_start = donor_end - history + 1
        if donor_start < 0 or donor_end >= current_start:
            raise PermissionError("shifted peer window is not strictly causal/disjoint")
        current_slice = slice(current_start, decision + 1)
        donor_slice = slice(donor_start, donor_end + 1)
        raw_current = np.stack(
            [
                np.asarray(values[selected, current_slice], dtype=np.float32).T
                for values in context.field_arrays
            ],
            axis=-1,
        )
        raw_donor = np.stack(
            [
                np.asarray(values[selected, donor_slice], dtype=np.float32).T
                for values in context.field_arrays
            ],
            axis=-1,
        )
        current_values.append(_normalize_stage1_asset_window(raw_current, context.scaler))
        shifted_values.append(_normalize_stage1_asset_window(raw_donor, context.scaler))
        markets.append(
            _normalize_stage1_market_window(
                np.asarray(context.market_series[current_slice], dtype=np.float32),
                context.scaler,
            )
        )
        current_history = np.asarray(
            context.eligibility[selected, current_slice], dtype=bool
        ).T
        donor_history = np.asarray(
            context.eligibility[selected, donor_slice], dtype=bool
        ).T
        current_eligibility.append(current_history)
        shifted_eligibility.append(donor_history)
        raw_target = np.asarray(context.target[selected, decision], dtype=np.float32)
        valid = current_history[-1] & np.isfinite(raw_target)
        targets.append(np.where(valid, raw_target, 0.0).astype(np.float32))
        target_valid.append(valid)
        donor_current = np.asarray(
            context.eligibility[selected, donor_end], dtype=bool
        )
        mismatch.append(float(np.mean(current_history[-1] != donor_current)))
    batch = Stage1Batch(
        asset_values=torch.from_numpy(np.stack(current_values)),
        market_values=torch.from_numpy(np.stack(markets)),
        eligibility=torch.from_numpy(np.stack(current_eligibility)),
        shifted_peer_values=torch.from_numpy(np.stack(shifted_values)),
        shifted_peer_eligibility=torch.from_numpy(np.stack(shifted_eligibility)),
        target_returns=torch.from_numpy(np.stack(targets)),
        target_valid=torch.from_numpy(np.stack(target_valid)),
        decision_indices=indices,
        donor_current_membership_mismatch=float(np.mean(mismatch)),
    )
    if torch.any(batch.eligibility[:, -1].sum(dim=1) < 3):
        raise ValueError("Stage-1 batch has an inadequate current cross-section")
    return batch


def _prefix_array_sha256(values: np.ndarray, stop: int) -> str:
    digest = hashlib.sha256()
    digest.update(str((int(values.shape[0]), int(stop))).encode("ascii"))
    digest.update(str(values.dtype).encode("ascii"))
    if values.ndim == 1:
        digest.update(np.ascontiguousarray(values[:stop]).tobytes(order="C"))
    else:
        for start in range(0, int(values.shape[0]), 16):
            chunk = np.ascontiguousarray(values[start : start + 16, :stop])
            digest.update(chunk.tobytes(order="C"))
    return digest.hexdigest().upper()


def stage1_data_identity(
    context: Stage1Context, config: Mapping[str, Any]
) -> dict[str, Any]:
    """Hash only the admitted through-June data prefix, never later cache rows."""

    stop = int(
        np.searchsorted(
            context.timestamps,
            pd.Timestamp(config["boundaries"]["latest_timestamp_exclusive"]).value,
            side="left",
        )
    )
    array_hashes = {
        field: _prefix_array_sha256(values, stop)
        for field, values in zip(context.asset_fields, context.field_arrays)
    }
    for field in context.market_fields:
        array_hashes[field] = _prefix_array_sha256(context.store.field(field), stop)
    array_hashes.update(
        {
            "timestamp_ns": hashlib.sha256(
                np.ascontiguousarray(context.timestamps[:stop]).tobytes(order="C")
            ).hexdigest().upper(),
            "base_eligible": _prefix_array_sha256(context.eligibility, stop),
            "target_return_4h": _prefix_array_sha256(context.target, stop),
        }
    )
    logical = {
        "surface_id": context.store.metadata["surface_id"],
        "start_utc": context.store.metadata["start_utc"],
        "end_exclusive_utc": config["boundaries"]["latest_timestamp_exclusive"],
        "symbols": list(context.store.symbols),
        "asset_fields": list(context.asset_fields),
        "market_fields": list(context.market_fields),
        "array_sha256": array_hashes,
    }
    return {
        "metadata_identity_sha256": context.store.metadata.get("identity_sha256"),
        "metadata_source_sha": context.store.metadata.get("source_sha"),
        "logical_content_identity_sha256": _payload_sha256(logical),
        "logical_payload": logical,
    }


def torch_state_sha256(model: nn.Module) -> str:
    digest = hashlib.sha256()
    for name, value in sorted(model.state_dict().items()):
        array = np.ascontiguousarray(value.detach().cpu().numpy())
        digest.update(name.encode("utf-8"))
        digest.update(str(array.shape).encode("ascii"))
        digest.update(str(array.dtype).encode("ascii"))
        digest.update(array.tobytes(order="C"))
    return digest.hexdigest().upper()


def stage1_block_metrics(
    prediction: np.ndarray,
    target: np.ndarray,
    valid: np.ndarray,
    *,
    maximum_rank_samples: int,
) -> dict[str, Any]:
    pred = np.where(valid, np.asarray(prediction, dtype=np.float32), np.nan)
    truth = np.where(valid, np.asarray(target, dtype=np.float32), np.nan)
    metrics = prediction_metrics(
        pred.T, truth.T, maximum_rank_samples=int(maximum_rank_samples)
    )
    rank_ic: list[float] = []
    effective: list[int] = []
    cross_sectional_variance: list[float] = []
    for index in range(pred.shape[0]):
        local = np.isfinite(pred[index]) & np.isfinite(truth[index])
        effective.append(int(local.sum()))
        if local.sum() < 3:
            continue
        left = pred[index, local].astype(float)
        right = truth[index, local].astype(float)
        cross_sectional_variance.append(float(np.var(left)))
        left_order = np.argsort(left, kind="stable")
        right_order = np.argsort(right, kind="stable")
        left_rank = np.empty_like(left_order, dtype=float)
        right_rank = np.empty_like(right_order, dtype=float)
        left_rank[left_order] = np.arange(len(left_order), dtype=float)
        right_rank[right_order] = np.arange(len(right_order), dtype=float)
        if np.std(left_rank) > 0.0 and np.std(right_rank) > 0.0:
            rank_ic.append(float(np.corrcoef(left_rank, right_rank)[0, 1]))
    temporal_variance = [
        float(np.var(pred[local, asset]))
        for asset in range(pred.shape[1])
        if (local := np.isfinite(pred[:, asset])).sum() >= 2
    ]
    metrics.update(
        {
            "cross_sectional_rank_ic_mean": (
                float(np.mean(rank_ic)) if rank_ic else None
            ),
            "cross_sectional_rank_ic_dates": len(rank_ic),
            "median_effective_assets": float(np.median(effective)),
            "minimum_effective_assets": int(min(effective)),
            "target_coverage": float(np.mean(valid)),
            "mean_cross_sectional_prediction_variance": (
                float(np.mean(cross_sectional_variance))
                if cross_sectional_variance
                else 0.0
            ),
            "mean_temporal_prediction_variance": (
                float(np.mean(temporal_variance)) if temporal_variance else 0.0
            ),
            "finite_metrics": bool(
                math.isfinite(float(metrics["mse"]))
                and math.isfinite(float(metrics["prediction_variance"]))
            ),
        }
    )
    return metrics


def stage1_pair_metrics(
    left: np.ndarray, right: np.ndarray, valid: np.ndarray
) -> dict[str, Any]:
    common = np.asarray(valid, dtype=bool) & np.isfinite(left) & np.isfinite(right)
    left_values = np.asarray(left, dtype=float)[common]
    right_values = np.asarray(right, dtype=float)[common]
    if not len(left_values):
        return {
            "observations": 0,
            "value_correlation": None,
            "mean_absolute_difference": None,
            "exact_equality_ratio": None,
        }
    correlation = (
        float(np.corrcoef(left_values, right_values)[0, 1])
        if np.std(left_values) > 0.0 and np.std(right_values) > 0.0
        else 0.0
    )
    return {
        "observations": int(len(left_values)),
        "value_correlation": correlation,
        "mean_absolute_difference": float(
            np.mean(np.abs(left_values - right_values))
        ),
        "exact_equality_ratio": float(np.mean(left_values == right_values)),
    }


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
    probe_decision_eligibility = base_eligible[
        probe_indices[:, None], decision_times[None, :]
    ].T
    probe_transitions = int(
        np.count_nonzero(np.diff(probe_decision_eligibility.astype(np.int8), axis=0))
    )
    if bool(smoke.get("require_dynamic_membership_transition", False)) and not probe_transitions:
        raise ValueError("predeclared probe lacks a dynamic-universe membership transition")

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
        "probe_eligibility_transitions": probe_transitions,
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
    turnover_identity_closed = bool(
        np.isclose(float(training_turnover.sum()), evaluation.total_turnover_l1)
    )
    cost_identity_closed = bool(
        np.isclose(float(training_cost.sum()), evaluation.total_cost)
    )
    if not turnover_identity_closed or not cost_identity_closed:
        raise AssertionError("training and strict-evaluator cost paths diverged")
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
        "probe_eligibility_transitions": metadata[
            "probe_eligibility_transitions"
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
        "training_evaluator_turnover_identity_closed": turnover_identity_closed,
        "training_evaluator_cost_identity_closed": cost_identity_closed,
        "wall_seconds": elapsed,
        "boundaries": dict(config["boundaries"]),
    }
