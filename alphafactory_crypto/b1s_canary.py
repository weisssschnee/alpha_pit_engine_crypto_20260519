from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

import numpy as np
import pandas as pd

from alphafactory_crypto.identity_registry import activation_identity
from alphafactory_crypto.signal_behaviour import canonical_weight_hash


MAIN_LANES = (
    "static_cross_sectional", "temporal_program", "funding_event", "basis_oi_state",
    "volatility_session", "cross_asset_state", "orthogonal_exile", "competitor_reproduction",
    "adaptive_challenger",
)
BBO_LANES = ("bbo_temporal_event_micro",)
DISABLED_TOKENS = ("liquidation", "force_order", "multi_level_depth", "depth_notional")
FORBIDDEN_ACCESS_TOKENS = ("validation", "test", "recent", "stress", "oos", "forward", "a7mem")


@dataclass(frozen=True)
class CandidateSpec:
    proposal_id: str
    panel_id: str
    lane_id: str
    seed: int
    ordinal: int
    field_a: str
    field_b: str
    operator: str
    window: int
    coefficient: float
    economic_hypothesis: str
    family_id: str
    parent_identity: str
    expression: str
    canonical_program: str
    algorithm: str = "typed_ast"
    adaptive_query: bool = False


@dataclass(frozen=True)
class FrozenPanel:
    panel_id: str
    symbols: tuple[str, ...]
    timestamps: pd.DatetimeIndex
    fields: Mapping[str, np.ndarray]
    target_return: np.ndarray
    observable_time_rule: str
    maturity_rule: str
    comparison_domain: str

    def validate(self) -> None:
        shape = (len(self.symbols), len(self.timestamps))
        if self.target_return.shape != shape:
            raise ValueError("target return does not match panel coordinates")
        if self.timestamps.has_duplicates or not self.timestamps.is_monotonic_increasing:
            raise ValueError("panel timestamps must be sorted and unique")
        if any(np.asarray(value).shape != shape for value in self.fields.values()):
            raise ValueError("panel field does not match frozen coordinates")
        if self.observable_time_rule != "bucket_start_plus_1h" or self.maturity_rule != "bucket_close":
            raise PermissionError("B1S panels require completed-bucket +1h observability")


@dataclass(frozen=True)
class SignalEvidence:
    proposal_id: str
    exact_identity: str
    activation_identity: str
    proxy_score: float
    legal: bool
    failure_reason: str


def stable_id(prefix: str, payload: object, length: int = 24) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    return f"{prefix}:" + hashlib.sha256(raw).hexdigest()[:length]


def validate_contract(config: Mapping[str, Any]) -> None:
    budget = config["budget_per_lane"]
    if budget["proposals_per_seed"] != 256 or tuple(budget["fixed_seeds"]) != (1701, 1709):
        raise ValueError("B1S proposal budget or seeds drifted")
    if budget["proposal_total"] != 512 or budget["stratified_admissions"] != 64:
        raise ValueError("B1S proposal/admission budget drifted")
    if budget["development_strict_evaluations"] != 32:
        raise ValueError("B1S strict budget drifted")
    if tuple(config["main_lanes"]) != MAIN_LANES or tuple(config["bbo_lanes"]) != BBO_LANES:
        raise ValueError("B1S enabled lanes drifted")
    if config["global_top_k_control"]["main_strict_evaluation_budget"] != 32 * len(MAIN_LANES):
        raise ValueError("main global-top-K control budget is not equal")
    if config["global_top_k_control"]["bbo_strict_evaluation_budget"] != 32 * len(BBO_LANES):
        raise ValueError("BBO global-top-K control budget is not equal")
    if config["global_top_k_control"]["cross_panel_ranking_allowed"]:
        raise PermissionError("main and BBO panels cannot be ranked together")
    if config["adaptive_challenger"]["max_development_feedback_queries"] != 64:
        raise ValueError("adaptive query budget drifted")


LANE_RECIPES: dict[str, dict[str, tuple[str, ...]]] = {
    "static_cross_sectional": {
        "fields": ("funding", "basis", "oi", "liquidity", "taker", "volatility", "positioning"),
        "operators": ("blend", "difference", "ratio", "cross_product"),
        "hypotheses": ("carry", "basis_dislocation", "positioning", "liquidity"),
    },
    "temporal_program": {
        "fields": ("funding", "basis", "oi", "liquidity", "taker", "volatility"),
        "operators": ("delta", "slope", "acceleration", "persistence", "multiscale"),
        "hypotheses": ("temporal_change", "persistence", "acceleration"),
    },
    "funding_event": {
        "fields": ("funding", "funding_abs", "funding_change"),
        "operators": ("event_age", "event_window", "persistence", "delta", "transition"),
        "hypotheses": ("funding_carry", "funding_extreme", "funding_transition"),
    },
    "basis_oi_state": {
        "fields": ("basis", "basis_abs", "oi", "oi_change"),
        "operators": ("blend", "difference", "delta", "zscore", "multiscale"),
        "hypotheses": ("basis_dislocation", "oi_expansion", "basis_oi_interaction"),
    },
    "volatility_session": {
        "fields": ("volatility", "liquidity", "session_sin", "session_cos", "taker"),
        "operators": ("blend", "cross_product", "delta", "zscore", "persistence"),
        "hypotheses": ("volatility_state", "session_effect", "liquidity_regime"),
    },
    "cross_asset_state": {
        "fields": ("asset_return", "market_return", "relative_market_return", "cross_confirmation"),
        "operators": ("blend", "difference", "delta", "persistence", "multiscale"),
        "hypotheses": ("cross_asset_confirmation", "relative_strength", "market_decoupling"),
    },
    "orthogonal_exile": {
        "fields": ("oi", "liquidity", "taker", "volatility", "positioning", "relative_market_return"),
        "operators": ("orthogonal", "difference", "ratio", "delta", "multiscale"),
        "hypotheses": ("new_economic_hypothesis", "orthogonal_flow", "exile_regime"),
    },
    "competitor_reproduction": {
        "fields": ("asset_return", "funding", "basis", "oi_change", "volatility", "liquidity", "session_sin"),
        "operators": ("momentum", "reversal", "zscore", "persistence", "blend"),
        "hypotheses": ("competitor_momentum", "competitor_reversal", "competitor_carry", "competitor_liquidity"),
    },
    "adaptive_challenger": {
        "fields": ("funding", "basis", "oi", "liquidity", "taker", "volatility", "relative_market_return"),
        "operators": ("delta", "slope", "multiscale", "blend", "orthogonal"),
        "hypotheses": ("adaptive_cem", "adaptive_mcts", "adaptive_evolutionary"),
    },
    "bbo_temporal_event_micro": {
        "fields": ("spread", "bid_qty", "ask_qty", "quote_imbalance", "top_of_book_liquidity"),
        "operators": ("delta", "slope", "acceleration", "persistence", "event_window", "multiscale", "blend"),
        "hypotheses": ("bbo_spread", "bbo_quantity", "bbo_imbalance", "bbo_liquidity"),
    },
}


def generate_proposals(
    panel_id: str,
    lane_id: str,
    seed: int,
    count: int = 256,
    *,
    ordinal_offset: int = 0,
    preferred_operator: str | None = None,
    adaptive_query_count: int = 0,
) -> list[CandidateSpec]:
    if lane_id not in LANE_RECIPES:
        raise ValueError(f"unknown B1S lane: {lane_id}")
    recipe = LANE_RECIPES[lane_id]
    fields, operators, hypotheses = recipe["fields"], recipe["operators"], recipe["hypotheses"]
    windows = (2, 4, 8, 12, 24, 48, 72, 168)
    coefficients = (-2.0, -1.0, -0.5, 0.5, 1.0, 2.0)
    algorithms = ("cem", "uct_mcts", "evolutionary") if lane_id == "adaptive_challenger" else ("typed_ast",)
    proposals: list[CandidateSpec] = []
    for local in range(count):
        ordinal = ordinal_offset + local
        base = ordinal % 128
        field_a = fields[(base + seed) % len(fields)]
        field_b = fields[((base // len(fields)) * 3 + seed + 1) % len(fields)]
        operator = operators[(base // max(1, len(fields))) % len(operators)]
        if preferred_operator and ordinal >= adaptive_query_count:
            operator = preferred_operator
        window = windows[(base // max(1, len(fields) * len(operators))) % len(windows)]
        coefficient = coefficients[(base + seed // 7) % len(coefficients)]
        hypothesis = hypotheses[(base + len(operator)) % len(hypotheses)]
        algorithm = algorithms[ordinal % len(algorithms)]
        canonical_payload = {
            "panel": panel_id, "lane": lane_id, "field_a": field_a, "field_b": field_b,
            "operator": operator, "window": window, "coefficient": coefficient,
        }
        canonical = json.dumps(canonical_payload, sort_keys=True, separators=(",", ":"))
        alias = (ordinal // 128 + seed) % 4
        core = f"{operator}({field_a},{field_b},w={window},c={coefficient:g})"
        expression = (core, f"Scale({core},1)", f"Add({core},0)", f"SafeDiv({core},1)")[alias]
        proposal_payload = {"panel": panel_id, "lane": lane_id, "seed": seed, "ordinal": ordinal, "expression": expression}
        proposals.append(CandidateSpec(
            stable_id("proposal", proposal_payload), panel_id, lane_id, seed, ordinal,
            field_a, field_b, operator, window, coefficient, f"hypothesis:{hypothesis}",
            f"family:{lane_id}:{operator}", stable_id("parent", {"lane": lane_id, "a": field_a, "op": operator}),
            expression, canonical, algorithm, lane_id == "adaptive_challenger" and ordinal < adaptive_query_count,
        ))
    return proposals


def _shift(values: np.ndarray, periods: int) -> np.ndarray:
    out = np.full_like(values, np.nan, dtype=float)
    if periods > 0 and periods < values.shape[1]:
        out[:, periods:] = values[:, :-periods]
    return out


def _rolling_mean(values: np.ndarray, window: int) -> np.ndarray:
    frame = pd.DataFrame(values.T)
    return frame.rolling(window, min_periods=max(2, min(window, window // 2))).mean().to_numpy().T


def _rolling_std(values: np.ndarray, window: int) -> np.ndarray:
    frame = pd.DataFrame(values.T)
    return frame.rolling(window, min_periods=max(2, min(window, window // 2))).std(ddof=0).to_numpy().T


def _safe_z(values: np.ndarray, window: int) -> np.ndarray:
    mean, std = _rolling_mean(values, window), _rolling_std(values, window)
    return np.divide(values - mean, std, out=np.full_like(values, np.nan), where=std > 1e-12)


def _event_age(values: np.ndarray) -> np.ndarray:
    result = np.full_like(values, np.nan, dtype=float)
    for row in range(values.shape[0]):
        age = np.nan
        previous = np.nan
        for column in range(values.shape[1]):
            value = values[row, column]
            if not np.isfinite(value):
                continue
            if not np.isfinite(previous) or value != previous:
                age = 0.0
            elif np.isfinite(age):
                age += 1.0
            result[row, column] = age
            previous = value
    return result


def _cross_sectional_residual(values: np.ndarray, reference: np.ndarray) -> np.ndarray:
    out = np.full_like(values, np.nan, dtype=float)
    for column in range(values.shape[1]):
        x, y = reference[:, column], values[:, column]
        valid = np.isfinite(x) & np.isfinite(y)
        if valid.sum() < 3 or np.var(x[valid]) <= 1e-15:
            continue
        beta = np.cov(x[valid], y[valid], ddof=0)[0, 1] / np.var(x[valid])
        out[valid, column] = y[valid] - beta * x[valid]
    return out


def materialize(spec: CandidateSpec, panel: FrozenPanel) -> np.ndarray:
    panel.validate()
    if any(token in spec.canonical_program.lower() for token in DISABLED_TOKENS):
        raise PermissionError("disabled liquidation/depth capability entered B1S proposal")
    if spec.field_a not in panel.fields or spec.field_b not in panel.fields:
        raise KeyError(f"candidate field missing from {panel.panel_id}")
    a = np.asarray(panel.fields[spec.field_a], dtype=float)
    b = np.asarray(panel.fields[spec.field_b], dtype=float)
    w, c, op = spec.window, spec.coefficient, spec.operator
    if op in {"blend", "cross_product"}:
        result = a + c * b if op == "blend" else a * b
    elif op == "difference":
        result = a - c * b
    elif op == "ratio":
        result = np.divide(a, np.abs(b) + max(abs(c), 0.5), out=np.full_like(a, np.nan), where=np.isfinite(b))
    elif op in {"delta", "momentum"}:
        result = a - _shift(a, w)
    elif op == "reversal":
        result = -(a - _shift(a, w))
    elif op == "slope":
        result = (a - _shift(a, w)) / float(w)
    elif op == "acceleration":
        first = a - _shift(a, w)
        result = first - _shift(first, w)
    elif op in {"zscore", "persistence"}:
        result = _safe_z(a, w) if op == "zscore" else _rolling_mean((a > 0).astype(float), w)
    elif op == "multiscale":
        result = _rolling_mean(a, max(2, w // 4)) - _rolling_mean(a, w)
    elif op == "event_age":
        result = _event_age(a)
    elif op in {"event_window", "transition"}:
        changed = np.where(np.isfinite(a) & np.isfinite(_shift(a, 1)), a != _shift(a, 1), False).astype(float)
        result = _rolling_mean(changed, w) if op == "event_window" else changed
    elif op == "orthogonal":
        result = _cross_sectional_residual(a, panel.fields.get("funding", b))
    else:
        raise ValueError(f"unsupported B1S operator: {op}")
    return np.asarray(result, dtype=float)


def rank_weights(signal: np.ndarray, max_abs_weight: float = 0.20) -> np.ndarray:
    ranks = pd.DataFrame(signal).rank(axis=0, pct=True, method="average").to_numpy(dtype=float)
    finite = np.isfinite(ranks)
    count = finite.sum(axis=0, keepdims=True)
    mean = np.divide(np.nansum(ranks, axis=0, keepdims=True), count, out=np.zeros((1, ranks.shape[1])), where=count > 0)
    centered = np.where(finite, ranks - mean, 0.0)
    denom = np.abs(centered).sum(axis=0, keepdims=True)
    weights = np.divide(centered, denom, out=np.zeros_like(centered), where=denom > 1e-12)
    weights = np.clip(weights, -max_abs_weight, max_abs_weight)
    gross = np.abs(weights).sum(axis=0, keepdims=True)
    return np.divide(weights, gross, out=np.zeros_like(weights), where=gross > 1e-12)


def _portfolio_series(weights: np.ndarray, target: np.ndarray, cost_bps: float) -> tuple[np.ndarray, np.ndarray]:
    valid = np.isfinite(target)
    gross_return = np.nansum(np.where(valid, weights * target, 0.0), axis=0)
    previous = np.zeros_like(weights)
    if weights.shape[1] > 1:
        previous[:, 1:] = weights[:, :-1]
    turnover = np.nansum(np.abs(weights - previous), axis=0)
    return gross_return - turnover * cost_bps / 10_000.0, turnover


def proxy_score(weights: np.ndarray, target: np.ndarray, coordinate_mask: np.ndarray) -> float:
    returns, _ = _portfolio_series(weights[:, coordinate_mask], target[:, coordinate_mask], 0.0)
    values = returns[np.isfinite(returns)]
    if len(values) < 24 or np.std(values) <= 1e-15:
        return float("-inf")
    return float(np.mean(values) / np.std(values) * math.sqrt(len(values)))


def strict_evaluate(weights: np.ndarray, panel: FrozenPanel, *, cost_bps: float = 5.0, minimum_assets: int = 5) -> dict[str, float | int | bool]:
    target = np.asarray(panel.target_return, dtype=float)
    active_assets = (np.abs(weights) > 1e-12).sum(axis=0)
    target_assets = np.isfinite(target).sum(axis=0)
    coordinate = (active_assets >= minimum_assets) & (target_assets >= minimum_assets)
    net, turnover = _portfolio_series(weights[:, coordinate], target[:, coordinate], cost_bps)
    x_rank = pd.DataFrame(np.where(np.abs(weights) > 1e-12, weights, np.nan)).rank(axis=0).to_numpy(dtype=float)
    y_rank = pd.DataFrame(target).rank(axis=0).to_numpy(dtype=float)
    valid_rank = np.isfinite(x_rank) & np.isfinite(y_rank)
    rank_count = valid_rank.sum(axis=0, keepdims=True)
    x_mean = np.divide(np.nansum(x_rank, axis=0, keepdims=True), rank_count, out=np.zeros((1, x_rank.shape[1])), where=rank_count > 0)
    y_mean = np.divide(np.nansum(y_rank, axis=0, keepdims=True), rank_count, out=np.zeros((1, y_rank.shape[1])), where=rank_count > 0)
    x_center = np.where(valid_rank, x_rank - x_mean, 0.0)
    y_center = np.where(valid_rank, y_rank - y_mean, 0.0)
    numerator = np.sum(x_center * y_center, axis=0)
    denominator = np.sqrt(np.sum(np.square(x_center), axis=0) * np.sum(np.square(y_center), axis=0))
    ic = np.divide(numerator, denominator, out=np.full(x_rank.shape[1], np.nan), where=denominator > 1e-15)
    ic_values = ic[coordinate & (rank_count.ravel() >= minimum_assets)]
    finite_net = net[np.isfinite(net)]
    mean = float(np.mean(finite_net)) if len(finite_net) else float("nan")
    std = float(np.std(finite_net)) if len(finite_net) else float("nan")
    coverage = float(coordinate.mean())
    ic_mean = float(np.nanmean(ic_values)) if len(ic_values) else float("nan")
    score = mean / std * math.sqrt(len(finite_net)) if len(finite_net) >= 2 and std > 1e-15 else float("nan")
    survivor = bool(coverage >= 0.80 and len(finite_net) >= 100 and mean > 0 and ic_mean > 0)
    return {
        "coordinate_coverage": coverage, "observations": int(len(finite_net)), "net_mean": mean,
        "net_std": std, "development_score": score, "ic_mean": ic_mean,
        "turnover_mean": float(np.mean(turnover)) if len(turnover) else float("nan"),
        "development_survivor": survivor,
    }


def evidence(spec: CandidateSpec, signal: np.ndarray, panel: FrozenPanel, proxy_mask: np.ndarray) -> tuple[SignalEvidence, np.ndarray]:
    weights = rank_weights(signal)
    exact = "exact-signal:" + canonical_weight_hash(weights)[:24]
    active = np.abs(weights) > 1e-12
    activation = activation_identity(active, universe_ids=panel.symbols, timestamps_ns=panel.timestamps.asi8)
    score = proxy_score(weights, panel.target_return, proxy_mask)
    legal = bool(np.isfinite(weights).any() and np.isfinite(score))
    return SignalEvidence(spec.proposal_id, exact, activation, score, legal, "" if legal else "NON_FINITE_SIGNAL_OR_PROXY"), weights


def stratified_strict_selection(rows: Iterable[Mapping[str, Any]], quota: int) -> list[str]:
    ordered = sorted(rows, key=lambda row: (str(row["behaviour_potential"]), str(row["economic_hypothesis"]), int(row["ordinal"]), str(row["proposal_id"])))
    buckets: dict[tuple[str, str], list[Mapping[str, Any]]] = {}
    for row in ordered:
        buckets.setdefault((str(row["behaviour_potential"]), str(row["economic_hypothesis"])), []).append(row)
    selected: list[str] = []
    keys = sorted(buckets)
    while len(selected) < quota and any(buckets.values()):
        for key in keys:
            if buckets[key] and len(selected) < quota:
                selected.append(str(buckets[key].pop(0)["proposal_id"]))
    return selected


def global_top_k(rows: Iterable[Mapping[str, Any]], quota: int, *, panel_id: str) -> list[str]:
    values = [row for row in rows if str(row["panel_id"]) == panel_id and bool(row["legal"])]
    by_exact: dict[str, Mapping[str, Any]] = {}
    for row in values:
        exact = str(row["exact_identity"])
        incumbent = by_exact.get(exact)
        key = (float(row["proxy_score"]), -int(row["ordinal"]), str(row["proposal_id"]))
        if incumbent is None or key > (float(incumbent["proxy_score"]), -int(incumbent["ordinal"]), str(incumbent["proposal_id"])):
            by_exact[exact] = row
    ranked = sorted(by_exact.values(), key=lambda row: (-float(row["proxy_score"]), int(row["ordinal"]), str(row["proposal_id"])))
    return [str(row["proposal_id"]) for row in ranked[:quota]]


def assert_no_cross_panel_comparison(left_panel: str, right_panel: str) -> None:
    if left_panel != right_panel:
        raise PermissionError("main and BBO micro-CANARY results cannot be directly ranked")


def effective_cluster_count(cluster_ids: Iterable[str]) -> float:
    counts = pd.Series(list(cluster_ids)).value_counts().to_numpy(dtype=float)
    return float(counts.sum() ** 2 / np.square(counts).sum()) if len(counts) else 0.0


def behaviour_cluster_identity(weights: np.ndarray, timestamps: pd.DatetimeIndex) -> str:
    """Multi-aspect deterministic behaviour signature; no performance inputs."""
    values = np.asarray(weights, dtype=float)
    if values.shape[1] != len(timestamps):
        raise ValueError("behaviour coordinates do not match timestamps")
    sample_index = np.linspace(0, values.shape[1] - 1, min(512, values.shape[1]), dtype=int)
    sample = values[:, sample_index]
    active = np.abs(sample) > 1e-12
    positive = sample > 1e-12
    coverage = active.mean(axis=1)
    sign_balance = np.divide(positive.sum(axis=1), active.sum(axis=1), out=np.zeros(values.shape[0]), where=active.sum(axis=1) > 0)
    persistence = []
    for lag in (1, 24):
        if sample.shape[1] <= lag:
            persistence.append(0.0)
            continue
        left, right = sample[:, lag:].ravel(), sample[:, :-lag].ravel()
        valid = np.isfinite(left) & np.isfinite(right)
        persistence.append(float(np.corrcoef(left[valid], right[valid])[0, 1]) if valid.sum() >= 2 and np.std(left[valid]) > 1e-15 and np.std(right[valid]) > 1e-15 else 0.0)
    top_share = (sample > 0).mean(axis=1)
    bottom_share = (sample < 0).mean(axis=1)
    month = timestamps[sample_index].strftime("%Y-%m")
    monthly = []
    for key in sorted(set(month)):
        monthly.append(float(np.mean(active[:, month == key])))
    vector = np.concatenate([coverage, sign_balance, top_share, bottom_share, np.asarray(persistence), np.asarray(monthly)])
    quantized = np.nan_to_num(np.round(vector / 0.10) * 0.10, nan=-9.0, posinf=9.0, neginf=-9.0)
    return stable_id("behaviour-cluster", quantized.tolist())
