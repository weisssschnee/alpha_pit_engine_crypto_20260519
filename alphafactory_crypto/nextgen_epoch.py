from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, replace
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
import pandas as pd

from alphafactory_crypto.b1s_canary import FrozenPanel, behaviour_cluster_identity, rank_weights
from alphafactory_crypto.identity_registry import activation_identity
from alphafactory_crypto.signal_behaviour import canonical_weight_hash


MAIN_LANES = (
    "typed_random_fresh",
    "typed_ast",
    "cem",
    "uct_mcts",
    "evolutionary",
    "surrogate",
    "llm_proposal_repair",
    "orthogonal_exile",
)
BBO_LANES = ("bbo_typed_temporal",)
ADAPTIVE_LANES = ("cem", "uct_mcts", "evolutionary", "surrogate")
DISABLED_TOKENS = ("liquidation", "force_order", "multi_level_depth", "depth_notional")
FORBIDDEN_ACCESS_TOKENS = ("validation", "test", "recent", "may_stress", "oos", "forward", "a7mem")
PRIMITIVES = (
    "Level", "Delta", "Slope", "Acceleration", "Surprise", "Persistence", "Duration",
    "StateAge", "TimeSince", "Transition", "FirstHit", "LastHit", "PathShape",
    "EventWindow", "MultiScaleRelation",
)
SECONDARY_PRIMITIVES = ("Identity", "Delta", "Persistence", "Transition", "PathShape")
INTERACTIONS = ("none", "difference", "product", "residual", "condition")
WINDOWS = (2, 4, 8, 12, 24, 48, 72, 168)
THRESHOLDS = (-1.0, -0.5, 0.0, 0.5, 1.0)


@dataclass(frozen=True)
class ProgramSpec:
    lane_id: str
    panel_id: str
    algorithm: str
    seed: int
    ordinal: int
    mechanism_id: str
    economic_hypothesis: str
    field_a: str
    field_b: str
    primitive: str
    secondary_primitive: str
    interaction: str
    window: int
    long_window: int
    threshold: float
    direction: int
    parent_identity: str
    lineage_namespace: str
    raw_template: str = ""
    repaired: bool = False
    policy_feedback_used: bool = False


@dataclass(frozen=True)
class SignalRecord:
    exact_identity: str
    activation_identity: str
    behaviour_cluster: str
    proxy_score: float
    legal: bool
    failure_reason: str


@dataclass(frozen=True)
class MultiObjectiveVector:
    coordinate_coverage: float
    observations: int
    ic_mean: float
    ic_lcb: float
    gross_mean: float
    net_mean: float
    net_lcb: float
    return_risk: float
    worst_horizon_net_mean: float
    time_block_positive_fraction: float
    time_block_stability: float
    turnover_mean: float
    cost_drag_mean: float
    max_weight_mean: float
    concentration_hhi_mean: float
    complexity: int
    behaviour_novelty: float
    benchmark_incremental_mean: float
    benchmark_incremental_lcb: float
    placebo_ic_abs: float
    wrong_lag_ic_abs: float
    hard_gate_pass: bool
    hard_gate_reasons: str
    lane_scalar: float


def stable_hash(prefix: str, payload: object, length: int = 24) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    return f"{prefix}:" + hashlib.sha256(raw).hexdigest()[:length]


def _choice(seed: int, ordinal: int, salt: str, values: Sequence[Any]) -> Any:
    if not values:
        raise ValueError(f"empty choice set for {salt}")
    digest = hashlib.sha256(f"{seed}|{ordinal}|{salt}".encode()).digest()
    return values[int.from_bytes(digest[:8], "big") % len(values)]


def validate_mechanism_registry(payload: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    if payload.get("registry_id") != "CRYPTO-NEXTGEN-MECHANISM-REGISTRY-V1":
        raise ValueError("unexpected mechanism registry")
    if not payload.get("development_only"):
        raise PermissionError("mechanism registry must be development-only")
    forbidden = {str(value).lower() for value in payload.get("forbidden_capabilities", [])}
    if not {"liquidation", "force_order", "multi_level_depth"}.issubset(forbidden):
        raise PermissionError("unapproved capabilities are not explicitly disabled")
    families = tuple(dict(item) for item in payload.get("mechanism_families", []))
    ids = [str(item.get("mechanism_id")) for item in families]
    if len(families) != 11 or len(ids) != len(set(ids)):
        raise ValueError("eleven unique mechanism families are required")
    required = {
        "mechanism_id", "economic_hypotheses", "observable_fields", "typed_states",
        "temporal_primitives", "legal_program_templates", "canonicalization",
        "semantic_volume_estimate", "expected_failure_modes",
    }
    for item in families:
        missing = required - set(item)
        if missing:
            raise ValueError(f"mechanism family missing fields: {sorted(missing)}")
        if int(item["semantic_volume_estimate"]) <= 0:
            raise ValueError("semantic volume must be positive")
        if not set(item["temporal_primitives"]).issubset(PRIMITIVES):
            raise ValueError(f"unknown primitive in {item['mechanism_id']}")
        joined = json.dumps(item).lower()
        if any(token in joined for token in DISABLED_TOKENS):
            raise PermissionError(f"disabled capability leaked into {item['mechanism_id']}")
    return families


def validate_epoch_contract(config: Mapping[str, Any], registry: Mapping[str, Any]) -> None:
    validate_mechanism_registry(registry)
    if tuple(config["lanes"]["main"]) != MAIN_LANES or tuple(config["lanes"]["bbo_micro"]) != BBO_LANES:
        raise ValueError("Epoch-0 lane registry drifted")
    proposal = config["budget_range"]["proposals"]
    strict = config["budget_range"]["stratified_strict_evaluations"]
    if proposal != [32768, 65536] or strict != [1024, 2048]:
        raise ValueError("Epoch-0 budget range drifted")
    if int(config["minimum_fixed_seeds"]) < 2:
        raise ValueError("at least two fixed seeds are required")
    if not config["contracts"]["one_exact_identity_one_vote"]:
        raise PermissionError("one exact identity, one vote must be enabled")
    if config["contracts"]["cross_lane_memory"] or config["contracts"]["cross_epoch_memory"]:
        raise PermissionError("cross-lane and cross-epoch memory are forbidden")
    if config["data_access"] != "TRAIN_DEVELOPMENT_ONLY":
        raise PermissionError("Epoch-0 data access must remain development-only")


def _family_map(registry: Mapping[str, Any], *, panel_id: str, lane_id: str) -> dict[str, dict[str, Any]]:
    families = {item["mechanism_id"]: dict(item) for item in validate_mechanism_registry(registry)}
    if panel_id == "bbo_micro":
        return {"liquidity_top_level": families["liquidity_top_level"]}
    families.pop("liquidity_top_level")
    if lane_id == "orthogonal_exile":
        allowed = {"taker_imbalance", "volatility_regime", "session_time", "cross_asset_confirmation", "temporal_state_path", "orthogonal_exile"}
        families = {key: value for key, value in families.items() if key in allowed}
    return families


def canonical_program(spec: ProgramSpec) -> dict[str, Any]:
    if spec.primitive not in PRIMITIVES or spec.secondary_primitive not in SECONDARY_PRIMITIVES:
        raise ValueError("unknown typed primitive")
    if spec.interaction not in INTERACTIONS:
        raise ValueError("unknown interaction")
    if spec.window <= 0 or spec.long_window <= spec.window:
        raise ValueError("long window must exceed short window")
    if spec.direction not in (-1, 1) or not np.isfinite(spec.threshold):
        raise ValueError("invalid direction or threshold")
    field_a, field_b = spec.field_a, spec.field_b
    if spec.interaction in {"product"} and field_b < field_a:
        field_a, field_b = field_b, field_a
    return {
        "mechanism_id": spec.mechanism_id,
        "economic_hypothesis": spec.economic_hypothesis,
        "field_a": field_a,
        "field_b": field_b,
        "primitive": spec.primitive,
        "secondary_primitive": spec.secondary_primitive,
        "interaction": spec.interaction,
        "window": int(spec.window),
        "long_window": int(spec.long_window),
        "threshold": 0.0 if float(spec.threshold) == 0.0 else float(spec.threshold),
        "direction": int(spec.direction),
        "observable_time_rule": "completed_bucket_plus_source_lag",
        "maturity_rule": "max(source_maturity,completed_past_window)",
        "pit_rule": "usable_time_lte_decision_time",
    }


def canonical_program_json(spec: ProgramSpec) -> str:
    return json.dumps(canonical_program(spec), sort_keys=True, separators=(",", ":"))


def program_identity(spec: ProgramSpec) -> str:
    return stable_hash("typed-program", canonical_program(spec), 64)


def candidate_identity(spec: ProgramSpec) -> str:
    return stable_hash("epoch-candidate", {
        "lane": spec.lane_id, "panel": spec.panel_id, "algorithm": spec.algorithm,
        "seed": spec.seed, "ordinal": spec.ordinal, "program": canonical_program(spec),
    })


def make_program(
    registry: Mapping[str, Any], *, lane_id: str, panel_id: str, algorithm: str,
    seed: int, ordinal: int, preference: Mapping[str, Sequence[Any]] | None = None,
    policy_feedback_used: bool = False,
) -> ProgramSpec:
    families = _family_map(registry, panel_id=panel_id, lane_id=lane_id)
    family_ids = sorted(families)
    preferred_families = tuple((preference or {}).get("mechanism_id", ()))
    mechanism_id = str(_choice(seed, ordinal, "mechanism", preferred_families or family_ids))
    family = families[mechanism_id]
    fields = tuple(str(value) for value in family["observable_fields"])
    primitives = tuple(str(value) for value in family["temporal_primitives"])
    hypotheses = tuple(str(value) for value in family["economic_hypotheses"])
    primitive = str(_choice(seed, ordinal, "primitive", tuple((preference or {}).get("primitive", ())) or primitives))
    interaction = str(_choice(seed, ordinal, "interaction", tuple((preference or {}).get("interaction", ())) or INTERACTIONS))
    field_a = str(_choice(seed, ordinal, "field_a", fields))
    field_b = str(_choice(seed, ordinal, "field_b", fields))
    window = int(_choice(seed, ordinal, "window", tuple((preference or {}).get("window", ())) or WINDOWS[:-1]))
    long_options = tuple(value for value in WINDOWS if value > window)
    long_window = int(_choice(seed, ordinal, "long_window", long_options or (window * 2,)))
    secondary = str(_choice(seed, ordinal, "secondary", SECONDARY_PRIMITIVES))
    threshold = float(_choice(seed, ordinal, "threshold", THRESHOLDS))
    direction = int(_choice(seed, ordinal, "direction", (-1, 1)))
    hypothesis = str(_choice(seed, ordinal, "hypothesis", hypotheses))
    raw_template = ""
    repaired = False
    if lane_id == "llm_proposal_repair":
        templates = tuple(str(value) for value in family["legal_program_templates"])
        raw_template = str(_choice(seed, ordinal, "llm_static_template", templates))
        # Codex-authored templates are frozen before performance. Repair removes neutral aliases
        # and makes invalid same-scale MultiScale programs legal without consulting reward.
        repaired = True
        if primitive == "MultiScaleRelation" and long_window <= window:
            long_window = window * 2
        if interaction == "difference" and field_a == field_b:
            interaction = "none"
    if lane_id == "orthogonal_exile":
        interaction = "residual"
        if field_b == field_a:
            field_b = "funding" if field_a != "funding" else "oi"
    parent = stable_hash("epoch-parent", {
        "lane": lane_id, "mechanism": mechanism_id, "field": field_a, "primitive": primitive,
    })
    return ProgramSpec(
        lane_id, panel_id, algorithm, seed, ordinal, mechanism_id, hypothesis, field_a, field_b,
        primitive, secondary, interaction, window, long_window, threshold, direction, parent,
        f"runtime_only/epoch0/{panel_id}/{lane_id}/seed_{seed}", raw_template, repaired,
        policy_feedback_used,
    )


def mutate_program(parent: ProgramSpec, registry: Mapping[str, Any], *, seed: int, ordinal: int) -> ProgramSpec:
    fresh = make_program(
        registry, lane_id=parent.lane_id, panel_id=parent.panel_id, algorithm=parent.algorithm,
        seed=seed, ordinal=ordinal, policy_feedback_used=False,
    )
    slot = int(_choice(seed, ordinal, "mutation_slot", tuple(range(8))))
    updates: dict[str, Any] = {"seed": seed, "ordinal": ordinal, "policy_feedback_used": False}
    keys = ("mechanism_id", "economic_hypothesis", "field_a", "field_b", "primitive", "interaction", "window", "threshold")
    key = keys[slot]
    updates[key] = getattr(fresh, key)
    if key == "mechanism_id":
        updates.update({
            "economic_hypothesis": fresh.economic_hypothesis, "field_a": fresh.field_a,
            "field_b": fresh.field_b, "primitive": fresh.primitive,
        })
    if key == "window":
        updates["long_window"] = fresh.long_window
    child = replace(parent, **updates)
    child = replace(child, parent_identity=program_identity(parent), lineage_namespace=f"runtime_only/epoch0/{parent.panel_id}/{parent.lane_id}/seed_{seed}")
    canonical_program(child)
    return child


def _shift(values: np.ndarray, periods: int) -> np.ndarray:
    out = np.full_like(values, np.nan, dtype=float)
    if 0 < periods < values.shape[1]:
        out[:, periods:] = values[:, :-periods]
    return out


def _rolling(values: np.ndarray, window: int, kind: str = "mean") -> np.ndarray:
    """NaN-aware O(N) rolling mean/std without constructing a DataFrame per program."""
    source = np.asarray(values, dtype=float)
    finite = np.isfinite(source)
    clean = np.where(finite, source, 0.0)
    count = np.cumsum(finite.astype(np.int32), axis=1)
    total = np.cumsum(clean, axis=1)
    square = np.cumsum(clean * clean, axis=1) if kind == "std" else None

    def windowed(cumulative: np.ndarray) -> np.ndarray:
        result = cumulative.copy()
        if window < cumulative.shape[1]:
            result[:, window:] = cumulative[:, window:] - cumulative[:, :-window]
        return result

    count_window = windowed(count)
    total_window = windowed(total)
    minimum = max(2, window // 2)
    mean = np.divide(total_window, count_window, out=np.full(source.shape, np.nan), where=count_window >= minimum)
    if kind == "mean":
        return mean
    if kind != "std" or square is None:
        raise ValueError(f"unsupported rolling kind: {kind}")
    square_window = windowed(square)
    variance = np.divide(square_window, count_window, out=np.full(source.shape, np.nan), where=count_window >= minimum) - mean * mean
    return np.sqrt(np.maximum(variance, 0.0))


def _zscore(values: np.ndarray, window: int) -> np.ndarray:
    mean, std = _rolling(values, window), _rolling(values, window, "std")
    return np.divide(values - mean, std, out=np.full_like(values, np.nan), where=std > 1e-12)


def _state(values: np.ndarray, threshold: float, window: int) -> np.ndarray:
    z = _zscore(values, max(8, window))
    return np.where(np.isfinite(z), z > threshold, False)


def _duration(state: np.ndarray) -> np.ndarray:
    result = np.zeros(state.shape, dtype=float)
    for row in range(state.shape[0]):
        run = 0.0
        for column, value in enumerate(state[row]):
            run = run + 1.0 if bool(value) else 0.0
            result[row, column] = run
    return result


def _event_age_from_state(state: np.ndarray) -> np.ndarray:
    transition = state & ~np.concatenate([np.zeros((state.shape[0], 1), dtype=bool), state[:, :-1]], axis=1)
    result = np.full(state.shape, np.nan, dtype=float)
    for row in range(state.shape[0]):
        age = np.nan
        for column in range(state.shape[1]):
            if transition[row, column]:
                age = 0.0
            elif np.isfinite(age):
                age += 1.0
            result[row, column] = age
    return result


def _residual(values: np.ndarray, reference: np.ndarray) -> np.ndarray:
    x, y = np.asarray(reference, dtype=float), np.asarray(values, dtype=float)
    valid = np.isfinite(x) & np.isfinite(y)
    count = valid.sum(axis=0, keepdims=True)
    x_clean, y_clean = np.where(valid, x, 0.0), np.where(valid, y, 0.0)
    x_mean = np.divide(x_clean.sum(axis=0, keepdims=True), count, out=np.zeros((1, x.shape[1])), where=count > 0)
    y_mean = np.divide(y_clean.sum(axis=0, keepdims=True), count, out=np.zeros((1, y.shape[1])), where=count > 0)
    xc, yc = np.where(valid, x - x_mean, 0.0), np.where(valid, y - y_mean, 0.0)
    variance = np.sum(xc * xc, axis=0, keepdims=True)
    beta = np.divide(np.sum(xc * yc, axis=0, keepdims=True), variance, out=np.zeros((1, x.shape[1])), where=(count >= 3) & (variance > 1e-15))
    return np.where(valid & (count >= 3) & (variance > 1e-15), y - beta * x, np.nan)


def _primitive(values: np.ndarray, primitive: str, window: int, long_window: int, threshold: float) -> np.ndarray:
    if primitive == "Level":
        return values.copy()
    if primitive == "Delta":
        return values - _shift(values, window)
    if primitive == "Slope":
        return (values - _shift(values, window)) / float(window)
    if primitive == "Acceleration":
        first = values - _shift(values, window)
        return first - _shift(first, window)
    if primitive == "Surprise":
        return _zscore(values, long_window)
    state = _state(values, threshold, window)
    if primitive == "Persistence":
        return _rolling(state.astype(float), window)
    if primitive == "Duration":
        return _duration(state)
    if primitive in {"StateAge", "TimeSince", "LastHit"}:
        return _event_age_from_state(state)
    transition = state & ~np.concatenate([np.zeros((state.shape[0], 1), dtype=bool), state[:, :-1]], axis=1)
    if primitive in {"Transition", "FirstHit"}:
        return transition.astype(float)
    if primitive == "PathShape":
        return _rolling(values, window) - _rolling(values, long_window)
    if primitive == "EventWindow":
        return _rolling(transition.astype(float), window)
    if primitive == "MultiScaleRelation":
        return _rolling(values, window) - _rolling(values, long_window)
    raise ValueError(f"unsupported primitive: {primitive}")


def materialize_program(spec: ProgramSpec, panel: FrozenPanel) -> np.ndarray:
    panel.validate()
    canonical = canonical_program_json(spec).lower()
    if any(token in canonical for token in DISABLED_TOKENS):
        raise PermissionError("disabled capability entered Epoch-0 program")
    if spec.field_a not in panel.fields or spec.field_b not in panel.fields:
        raise KeyError(f"field unavailable in {panel.panel_id}: {spec.field_a}/{spec.field_b}")
    a = np.asarray(panel.fields[spec.field_a], dtype=float)
    b = np.asarray(panel.fields[spec.field_b], dtype=float)
    result = _primitive(a, spec.primitive, spec.window, spec.long_window, spec.threshold)
    if spec.interaction == "difference":
        result = result - _primitive(b, "Level", spec.window, spec.long_window, spec.threshold)
    elif spec.interaction == "product":
        result = result * np.sign(b)
    elif spec.interaction == "residual":
        result = _residual(result, b)
    elif spec.interaction == "condition":
        condition = _state(b, spec.threshold, spec.window)
        result = np.where(condition, result, np.nan)
    if spec.secondary_primitive != "Identity":
        secondary = "Persistence" if spec.secondary_primitive == "Persistence" else spec.secondary_primitive
        result = _primitive(result, secondary, spec.window, spec.long_window, spec.threshold)
    return np.asarray(spec.direction * result, dtype=float)


def signal_record(spec: ProgramSpec, signal: np.ndarray, panel: FrozenPanel, proxy_mask: np.ndarray) -> tuple[SignalRecord, np.ndarray]:
    weights = rank_weights(signal)
    exact = "exact-signal:" + canonical_weight_hash(weights)[:24]
    active = np.abs(weights) > 1e-12
    activation = activation_identity(active, universe_ids=panel.symbols, timestamps_ns=panel.timestamps.asi8)
    behaviour = behaviour_cluster_identity(weights, panel.timestamps)
    target = np.asarray(panel.target_return, dtype=float)
    gross, _ = portfolio_series(weights[:, proxy_mask], target[:, proxy_mask], 0.0)
    finite = gross[np.isfinite(gross)]
    proxy = float(np.mean(finite) / np.std(finite) * math.sqrt(len(finite))) if len(finite) >= 24 and np.std(finite) > 1e-15 else float("-inf")
    legal = bool(np.any(active) and np.isfinite(proxy))
    return SignalRecord(exact, activation, behaviour, proxy, legal, "" if legal else "NON_FINITE_OR_ZERO_DISPERSION"), weights


def portfolio_series(weights: np.ndarray, target: np.ndarray, cost_bps: float) -> tuple[np.ndarray, np.ndarray]:
    valid = np.isfinite(target)
    gross = np.nansum(np.where(valid, weights * target, 0.0), axis=0)
    previous = np.zeros_like(weights)
    if weights.shape[1] > 1:
        previous[:, 1:] = weights[:, :-1]
    turnover = np.nansum(np.abs(weights - previous), axis=0)
    return gross - turnover * cost_bps / 10_000.0, turnover


def _cross_sectional_ic(weights: np.ndarray, target: np.ndarray) -> np.ndarray:
    x = pd.DataFrame(np.where(np.abs(weights) > 1e-12, weights, np.nan)).rank(axis=0).to_numpy(dtype=float)
    y = pd.DataFrame(target).rank(axis=0).to_numpy(dtype=float)
    valid = np.isfinite(x) & np.isfinite(y)
    n = valid.sum(axis=0, keepdims=True)
    xm = np.divide(np.nansum(x, axis=0, keepdims=True), n, out=np.zeros((1, x.shape[1])), where=n > 0)
    ym = np.divide(np.nansum(y, axis=0, keepdims=True), n, out=np.zeros((1, y.shape[1])), where=n > 0)
    xc, yc = np.where(valid, x - xm, 0.0), np.where(valid, y - ym, 0.0)
    denom = np.sqrt(np.sum(xc * xc, axis=0) * np.sum(yc * yc, axis=0))
    return np.divide(np.sum(xc * yc, axis=0), denom, out=np.full(x.shape[1], np.nan), where=denom > 1e-15)


def multiobjective_evaluate(
    weights: np.ndarray,
    panel: FrozenPanel,
    *,
    complexity: int,
    behaviour_novelty: float,
    benchmark_net: np.ndarray,
    cost_bps: float,
    minimum_assets: int,
) -> MultiObjectiveVector:
    target = np.asarray(panel.target_return, dtype=float)
    active = (np.abs(weights) > 1e-12).sum(axis=0)
    target_assets = np.isfinite(target).sum(axis=0)
    coordinate = (active >= minimum_assets) & (target_assets >= minimum_assets)
    gross, _ = portfolio_series(weights[:, coordinate], target[:, coordinate], 0.0)
    net, turnover = portfolio_series(weights[:, coordinate], target[:, coordinate], cost_bps)
    finite = np.isfinite(net)
    net, gross, turnover = net[finite], gross[finite], turnover[finite]
    observations = len(net)
    net_mean = float(np.mean(net)) if observations else float("nan")
    net_std = float(np.std(net)) if observations else float("nan")
    net_se = net_std / math.sqrt(observations) if observations and np.isfinite(net_std) else float("nan")
    net_lcb = net_mean - 1.96 * net_se if np.isfinite(net_se) else float("nan")
    return_risk = net_mean / net_std * math.sqrt(observations) if observations >= 2 and net_std > 1e-15 else float("nan")
    ic = _cross_sectional_ic(weights, target)
    ic_values = ic[coordinate & np.isfinite(ic)]
    ic_mean = float(np.mean(ic_values)) if len(ic_values) else float("nan")
    ic_std = float(np.std(ic_values)) if len(ic_values) else float("nan")
    ic_lcb = ic_mean - 1.96 * ic_std / math.sqrt(len(ic_values)) if len(ic_values) else float("nan")
    timestamps = panel.timestamps[coordinate][finite]
    blocks = pd.PeriodIndex(timestamps, freq="Q")
    block_means = pd.Series(net).groupby(blocks).mean().to_numpy(dtype=float)
    worst = float(np.min(block_means)) if len(block_means) else float("nan")
    positive_fraction = float(np.mean(block_means > 0)) if len(block_means) else 0.0
    stability = float(1.0 / (1.0 + np.std(block_means) * 10_000.0)) if len(block_means) else 0.0
    benchmark = np.asarray(benchmark_net, dtype=float)[coordinate][finite]
    incremental = net - benchmark
    incremental_mean = float(np.mean(incremental)) if len(incremental) else float("nan")
    incremental_std = float(np.std(incremental)) if len(incremental) else float("nan")
    incremental_lcb = incremental_mean - 1.96 * incremental_std / math.sqrt(len(incremental)) if len(incremental) else float("nan")
    placebo = np.roll(target, 1, axis=0)
    placebo_ic = _cross_sectional_ic(weights, placebo)
    placebo_values = placebo_ic[coordinate & np.isfinite(placebo_ic)]
    wrong_lag = np.full_like(target, np.nan)
    wrong_lag[:, :-1] = target[:, 1:]
    wrong_ic = _cross_sectional_ic(weights, wrong_lag)
    wrong_values = wrong_ic[coordinate & np.isfinite(wrong_ic)]
    max_weight = np.max(np.abs(weights[:, coordinate]), axis=0) if coordinate.any() else np.array([])
    hhi = np.sum(np.square(weights[:, coordinate]), axis=0) if coordinate.any() else np.array([])
    reasons = []
    coverage = float(coordinate.mean())
    if coverage < 0.80:
        reasons.append("COVERAGE")
    if observations < 100:
        reasons.append("OBSERVATIONS")
    if not np.isfinite(ic_lcb):
        reasons.append("IC_NON_FINITE")
    if float(np.mean(max_weight)) > 0.25 if len(max_weight) else True:
        reasons.append("CONCENTRATION")
    placebo_abs = abs(float(np.mean(placebo_values))) if len(placebo_values) else float("inf")
    wrong_abs = abs(float(np.mean(wrong_values))) if len(wrong_values) else float("inf")
    if placebo_abs > 0.10:
        reasons.append("PLACEBO")
    scalar = (
        np.nan_to_num(ic_lcb, nan=-1.0) * 4.0
        + np.nan_to_num(return_risk, nan=-20.0) / 10.0
        + np.nan_to_num(incremental_lcb, nan=-0.01) * 1000.0
        + positive_fraction
        + behaviour_novelty
        - float(np.mean(turnover)) * 0.05 if observations else -999.0
    )
    return MultiObjectiveVector(
        coverage, observations, ic_mean, ic_lcb, float(np.mean(gross)) if observations else float("nan"),
        net_mean, net_lcb, return_risk, worst, positive_fraction, stability,
        float(np.mean(turnover)) if observations else float("nan"),
        float(np.mean(gross - net)) if observations else float("nan"),
        float(np.mean(max_weight)) if len(max_weight) else float("nan"),
        float(np.mean(hhi)) if len(hhi) else float("nan"), complexity, behaviour_novelty,
        incremental_mean, incremental_lcb, placebo_abs, wrong_abs, not reasons, "|".join(reasons), float(scalar),
    )


def complexity(spec: ProgramSpec) -> int:
    return 1 + int(spec.secondary_primitive != "Identity") + int(spec.interaction != "none") + int(spec.interaction == "condition")


def pareto_front(rows: Iterable[Mapping[str, Any]]) -> list[str]:
    values = [row for row in rows if bool(row.get("hard_gate_pass"))]
    maximize = ("ic_lcb", "net_lcb", "worst_horizon_net_mean", "time_block_stability", "behaviour_novelty", "benchmark_incremental_lcb")
    minimize = ("turnover_mean", "concentration_hhi_mean", "complexity", "placebo_ic_abs")
    survivors: list[str] = []
    for left in values:
        dominated = False
        for right in values:
            if left is right:
                continue
            weak = all(float(right[key]) >= float(left[key]) for key in maximize) and all(float(right[key]) <= float(left[key]) for key in minimize)
            strict = any(float(right[key]) > float(left[key]) for key in maximize) or any(float(right[key]) < float(left[key]) for key in minimize)
            if weak and strict:
                dominated = True
                break
        if not dominated:
            survivors.append(str(left["proposal_id"]))
    return sorted(set(survivors))


def effective_count(values: Iterable[str]) -> float:
    counts = np.asarray(list(Counter(values).values()), dtype=float)
    return float(counts.sum() ** 2 / np.square(counts).sum()) if len(counts) else 0.0


class UCTProgramPolicy:
    """Lane-local multi-step program construction; state is never serialized."""

    def __init__(self, registry: Mapping[str, Any], *, panel_id: str, lane_id: str, seed: int, exploration: float = 1.2) -> None:
        self.registry = registry
        self.panel_id = panel_id
        self.lane_id = lane_id
        self.seed = seed
        self.exploration = exploration
        self.visits: Counter[tuple[str, ...]] = Counter()
        self.value: defaultdict[tuple[str, ...], float] = defaultdict(float)
        self.paths: dict[int, tuple[str, ...]] = {}

    def _select(self, prefix: tuple[str, ...], options: Sequence[Any], ordinal: int, salt: str) -> Any:
        ordered = sorted(str(value) for value in options)
        unvisited = [value for value in ordered if self.visits[prefix + (value,)] == 0]
        if unvisited:
            return _choice(self.seed, ordinal, salt, unvisited)
        parent_visits = max(1, self.visits[prefix])
        scored = []
        for value in ordered:
            key = prefix + (value,)
            mean = self.value[key] / self.visits[key]
            score = mean + self.exploration * math.sqrt(math.log(parent_visits + 1.0) / self.visits[key])
            scored.append((score, value))
        return max(scored, key=lambda item: (item[0], item[1]))[1]

    def propose(self, ordinal: int) -> ProgramSpec:
        families = _family_map(self.registry, panel_id=self.panel_id, lane_id=self.lane_id)
        mechanism = self._select((), tuple(families), ordinal, "uct_mechanism")
        family = families[mechanism]
        primitive = self._select((mechanism,), family["temporal_primitives"], ordinal, "uct_primitive")
        interaction = self._select((mechanism, primitive), INTERACTIONS, ordinal, "uct_interaction")
        window = int(self._select((mechanism, primitive, interaction), WINDOWS[:-1], ordinal, "uct_window"))
        preference = {"mechanism_id": (mechanism,), "primitive": (primitive,), "interaction": (interaction,), "window": (window,)}
        spec = make_program(
            self.registry, lane_id=self.lane_id, panel_id=self.panel_id, algorithm="uct_mcts",
            seed=self.seed, ordinal=ordinal, preference=preference, policy_feedback_used=True,
        )
        self.paths[ordinal] = (mechanism, primitive, interaction, str(window))
        return spec

    def update(self, ordinal: int, reward: float) -> None:
        path = self.paths[ordinal]
        bounded = float(np.clip(reward if np.isfinite(reward) else -10.0, -10.0, 10.0))
        self.visits[()] += 1
        for depth in range(1, len(path) + 1):
            key = path[:depth]
            self.visits[key] += 1
            self.value[key] += bounded

    def frozen_preference(self) -> dict[str, tuple[Any, ...]]:
        mechanisms = _family_map(self.registry, panel_id=self.panel_id, lane_id=self.lane_id)
        best_mechanism = max(mechanisms, key=lambda value: self.value[(value,)] / max(1, self.visits[(value,)]))
        family = mechanisms[best_mechanism]
        best_primitive = max(family["temporal_primitives"], key=lambda value: self.value[(best_mechanism, str(value))] / max(1, self.visits[(best_mechanism, str(value))]))
        return {"mechanism_id": (best_mechanism,), "primitive": (best_primitive,)}


def cem_preference(specs: Sequence[ProgramSpec], scores: Sequence[float]) -> dict[str, tuple[Any, ...]]:
    finite = [(spec, float(score)) for spec, score in zip(specs, scores) if np.isfinite(score)]
    if not finite:
        return {}
    finite.sort(key=lambda item: item[1], reverse=True)
    elite = [item[0] for item in finite[: max(8, len(finite) // 4)]]
    result: dict[str, tuple[Any, ...]] = {}
    for key in ("mechanism_id", "primitive", "interaction", "window"):
        counts = Counter(getattr(spec, key) for spec in elite)
        result[key] = tuple(value for value, _ in counts.most_common(max(1, min(3, len(counts)))))
    return result


def surrogate_rank(specs: Sequence[ProgramSpec], scores: Sequence[float], pool: Sequence[ProgramSpec], count: int) -> list[ProgramSpec]:
    categories = sorted({
        f"m={spec.mechanism_id}" for spec in list(specs) + list(pool)
    } | {
        f"p={spec.primitive}" for spec in list(specs) + list(pool)
    } | {
        f"i={spec.interaction}" for spec in list(specs) + list(pool)
    })
    index = {value: position for position, value in enumerate(categories)}

    def encode(spec: ProgramSpec) -> np.ndarray:
        row = np.zeros(len(categories) + 4, dtype=float)
        row[index[f"m={spec.mechanism_id}"]] = 1.0
        row[index[f"p={spec.primitive}"]] = 1.0
        row[index[f"i={spec.interaction}"]] = 1.0
        row[-4:] = (spec.window / 168.0, spec.long_window / 168.0, spec.threshold, spec.direction)
        return row

    finite = [(spec, float(score)) for spec, score in zip(specs, scores) if np.isfinite(score)]
    if len(finite) < 8:
        return list(pool[:count])
    x = np.vstack([encode(spec) for spec, _ in finite])
    y = np.asarray([score for _, score in finite], dtype=float)
    beta = np.linalg.solve(x.T @ x + np.eye(x.shape[1]) * 1e-3, x.T @ y)
    ranked = sorted(pool, key=lambda spec: (float(encode(spec) @ beta), program_identity(spec)), reverse=True)
    selected: list[ProgramSpec] = []
    seen: set[str] = set()
    for spec in ranked:
        identity = program_identity(spec)
        if identity not in seen:
            selected.append(spec)
            seen.add(identity)
        if len(selected) >= count:
            break
    return selected
