from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Mapping

import numpy as np
import pandas as pd


STATE_INPUTS: dict[str, tuple[str, ...]] = {
    "funding_event_age": ("funding_rate",),
    "funding_event_intensity": ("funding_rate",),
    "basis_dislocation": ("mark_trade_basis_bps",),
    "oi_expansion_contraction": ("open_interest_value_last",),
    "liquidation_cluster": ("liquidation_notional",),
    "mark_index_deviation": ("mark_index_basis_bps",),
    "taker_imbalance_state": ("kline_taker_buy_quote_share",),
    "depth_liquidity_state": (),
    "liquidity_state": ("trade_quote_volume",),
    "volatility_state": ("trade_close",),
    "session_time_of_day": (),
    "cross_asset_confirmation": ("trade_close",),
}

ALLOWED_INPUT_ROLES = {"primary", "interaction-only", "condition-only", "state-only", "benchmark-only"}
NO_FEEDBACK = "NONE_NO_REWARD_GENERATOR_MEMORY_PROMOTION"
STATE_INPUT_ALTERNATIVES: dict[str, tuple[tuple[str, ...], ...]] = {
    "depth_liquidity_state": (("depth_notional_10bps",), ("top_of_book_quote_notional_mean",)),
}


@dataclass(frozen=True)
class StateAvailability:
    state_id: str
    status: str
    required_fields: tuple[str, ...]
    missing_fields: tuple[str, ...]


@dataclass(frozen=True)
class MaterializationResult:
    frame: pd.DataFrame
    availability: tuple[StateAvailability, ...]
    lineage: Mapping[str, object]
    artifact_hash: str


def _stable_frame_hash(frame: pd.DataFrame) -> str:
    ordered = frame.sort_values(["symbol", "timestamp"], kind="mergesort").reset_index(drop=True)
    payload = pd.util.hash_pandas_object(ordered, index=False, categorize=True).to_numpy(dtype="<u8").tobytes()
    return hashlib.sha256(payload).hexdigest().upper()


def _rolling_z(series: pd.Series, window: int = 168) -> pd.Series:
    mean = series.rolling(window, min_periods=max(2, min(24, window))).mean()
    std = series.rolling(window, min_periods=max(2, min(24, window))).std(ddof=0).replace(0.0, np.nan)
    return (series - mean) / std


def _funding_age(series: pd.Series) -> pd.Series:
    event = series.notna() & series.ne(series.shift(1))
    pos = pd.Series(np.arange(len(series), dtype=float), index=series.index)
    return pos - pos.where(event).ffill()


def _assert_coordinates(frame: pd.DataFrame) -> pd.DataFrame:
    required = {"symbol", "timestamp", "observable_time", "maturity_time"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"missing coordinate columns: {sorted(missing)}")
    out = frame.copy()
    for column in ("timestamp", "observable_time", "maturity_time"):
        out[column] = pd.to_datetime(out[column], utc=True)
    if out.duplicated(["symbol", "timestamp"]).any():
        raise ValueError("duplicate materialization coordinates")
    if (out["observable_time"] < out["timestamp"]).any() or (out["maturity_time"] < out["timestamp"]).any():
        raise ValueError("PIT metadata precedes event time")
    return out.sort_values(["symbol", "timestamp"], kind="mergesort").reset_index(drop=True)


def materialize_states(
    frame: pd.DataFrame,
    field_roles: Mapping[str, str],
    *,
    source_release_hash: str,
    field_registry_hash: str,
    production_scope: str,
) -> MaterializationResult:
    ordered = _assert_coordinates(frame)
    available: list[StateAvailability] = []
    outputs = ordered[["symbol", "timestamp", "observable_time", "maturity_time"]].copy()
    for state_id, required in STATE_INPUTS.items():
        alternatives = STATE_INPUT_ALTERNATIVES.get(state_id, (required,))
        valid_alternative = next(
            (
                fields for fields in alternatives
                if all(field in ordered.columns and field_roles.get(field) in ALLOWED_INPUT_ROLES for field in fields)
            ),
            None,
        )
        missing = () if valid_alternative is not None else tuple(
            sorted({field for fields in alternatives for field in fields})
        )
        required_for_record = valid_alternative if valid_alternative is not None else tuple(
            field for fields in alternatives for field in fields
        )
        status = "MATERIALIZED" if not missing else "UNAVAILABLE_NO_APPROVED_SOURCE"
        available.append(StateAvailability(state_id, status, tuple(required_for_record), missing))
        if missing:
            outputs[state_id] = np.nan

    groups = ordered.groupby("symbol", sort=False, group_keys=False)
    if "funding_rate" in ordered:
        outputs["funding_event_age"] = groups["funding_rate"].transform(_funding_age)
        outputs["funding_event_intensity"] = groups["funding_rate"].transform(lambda s: _rolling_z(s.abs()))
    if "mark_trade_basis_bps" in ordered:
        outputs["basis_dislocation"] = groups["mark_trade_basis_bps"].transform(_rolling_z)
    if "open_interest_value_last" in ordered:
        outputs["oi_expansion_contraction"] = groups["open_interest_value_last"].pct_change(fill_method=None)
    if "mark_index_basis_bps" in ordered:
        outputs["mark_index_deviation"] = ordered["mark_index_basis_bps"]
    if "kline_taker_buy_quote_share" in ordered:
        outputs["taker_imbalance_state"] = 2.0 * ordered["kline_taker_buy_quote_share"] - 1.0
    if "trade_quote_volume" in ordered:
        outputs["liquidity_state"] = groups["trade_quote_volume"].transform(lambda s: _rolling_z(np.log1p(s.clip(lower=0))))
    depth_source = next(
        (field for field in ("depth_notional_10bps", "top_of_book_quote_notional_mean") if field in ordered), None
    )
    if depth_source:
        outputs["depth_liquidity_state"] = groups[depth_source].transform(
            lambda s: _rolling_z(np.log1p(s.clip(lower=0)))
        )
    if "trade_close" in ordered:
        returns = groups["trade_close"].pct_change(fill_method=None)
        outputs["volatility_state"] = returns.groupby(ordered["symbol"], sort=False).transform(
            lambda s: s.rolling(24, min_periods=12).std(ddof=0)
        )
        market = returns.groupby(ordered["timestamp"], sort=False).transform("median")
        outputs["cross_asset_confirmation"] = np.sign(returns) * np.sign(market)
    outputs["session_time_of_day"] = ordered["timestamp"].dt.hour.astype(float)

    value_columns = [name for name in STATE_INPUTS]
    outputs["missing_mask"] = outputs[value_columns].isna().apply(
        lambda row: "".join("1" if value else "0" for value in row), axis=1
    )
    outputs["feedback_permission"] = NO_FEEDBACK
    lineage = {
        "source_release_hash": source_release_hash,
        "field_registry_hash": field_registry_hash,
        "production_scope": production_scope,
        "observable_time_rule": "timestamp_plus_source_lag",
        "maturity_rule": "max(source_maturity,observable_time)",
        "missing_semantics": "preserve_nan_and_explicit_bitmask",
        "feedback_permission": NO_FEEDBACK,
        "sort_contract": "symbol_then_timestamp_mergesort",
    }
    artifact_hash = hashlib.sha256(
        (_stable_frame_hash(outputs) + json.dumps(lineage, sort_keys=True, separators=(",", ":"))).encode()
    ).hexdigest().upper()
    return MaterializationResult(outputs, tuple(available), lineage, artifact_hash)
