"""Canonical temporal primitive authority used by the capability harness.

The definitions here are deliberately small and explicit.  Historical Epoch
implementations remain immutable proposal sources; ambiguous historical names
are not imported as active canonical primitives.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Callable, Mapping

import numpy as np


@dataclass(frozen=True)
class PrimitiveContract:
    primitive_id: str
    canonical_semantics: str
    canonical_implementation: str
    input_domain: str
    output_domain: str
    window_semantics: str
    warm_up_rule: str
    missing_value_rule: str
    activation_semantics: str
    event_state_assumptions: str
    expected_invariants: tuple[str, ...]
    deprecated_aliases: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["expected_invariants"] = list(self.expected_invariants)
        payload["deprecated_aliases"] = list(self.deprecated_aliases)
        return payload


_IMPLEMENTATION = "alphafactory_crypto.instrument_capability.primitives.evaluate_primitive"
_NUMERIC = "finite numeric panel shaped [asset,time]"
_OUTPUT = "float panel shaped [asset,time]"


CANONICAL_PRIMITIVES: Mapping[str, PrimitiveContract] = {
    "Delta": PrimitiveContract(
        "Delta",
        "x[t] - x[t-window]",
        _IMPLEMENTATION,
        _NUMERIC,
        _OUTPUT,
        "window is a lag distance",
        "window coordinates",
        "NaN unless both endpoints are finite",
        "active where the lagged difference is finite and nonzero",
        "no event state",
        ("constant input is zero after warm-up", "linear input has constant delta"),
        ("b1s:delta", "nextgen:Delta"),
    ),
    "Slope": PrimitiveContract(
        "Slope",
        "ordinary-least-squares slope over the trailing window including t",
        _IMPLEMENTATION,
        _NUMERIC,
        _OUTPUT,
        "window is the full OLS sample length",
        "window-1 coordinates",
        "NaN unless the complete trailing window is finite",
        "active where a complete window has nonzero fitted slope",
        "no event state",
        ("linear input recovers its per-coordinate slope", "constant input is zero"),
        ("legacy_nextgen:endpoint_slope", "legacy_b1s:endpoint_slope"),
    ),
    "Acceleration": PrimitiveContract(
        "Acceleration",
        "(x[t]-x[t-window]) - (x[t-window]-x[t-2*window])",
        _IMPLEMENTATION,
        _NUMERIC,
        _OUTPUT,
        "window is the lag used by both first differences",
        "2*window coordinates",
        "NaN unless all three lag endpoints are finite",
        "active where the lag-window second difference is finite and nonzero",
        "no event state",
        ("linear input is zero after warm-up", "quadratic input has stable sign"),
        ("b1s:acceleration", "nextgen:Acceleration"),
    ),
    "Persistence": PrimitiveContract(
        "Persistence",
        "fraction of values strictly above threshold in the complete trailing window",
        _IMPLEMENTATION,
        _NUMERIC,
        "float panel in [0,1]",
        "window is the occupancy sample length",
        "window-1 coordinates",
        "NaN unless the complete trailing window is finite",
        "continuous occupancy fraction; not an event counter",
        "state is raw x > threshold, never an implicit rolling z-score",
        ("bounded in [0,1]", "all-active window equals one", "all-inactive window equals zero"),
        ("legacy_nextgen:zscore_state_persistence",),
    ),
    "Duration": PrimitiveContract(
        "Duration",
        "length of the current consecutive active run, including t; zero while inactive",
        _IMPLEMENTATION,
        _NUMERIC,
        "nonnegative float panel",
        "window is not used; threshold defines active state",
        "none after a finite coordinate",
        "NaN resets the run; output is NaN at the missing coordinate",
        "increments only while x > threshold and resets to zero otherwise",
        "raw threshold state",
        ("inactive is zero", "first active coordinate is one", "missing values reset the run"),
        ("legacy_nextgen:zscore_state_duration",),
    ),
    "StateAge": PrimitiveContract(
        "StateAge",
        "age of the current boolean state since its most recent transition; zero on transition",
        _IMPLEMENTATION,
        _NUMERIC,
        "nonnegative float panel",
        "window is not used; threshold defines boolean state",
        "none after a finite coordinate",
        "NaN resets state identity; output is NaN at the missing coordinate",
        "tracks both active and inactive state age",
        "raw threshold state; distinct from active-only Duration",
        ("zero on each state change", "increments while either state persists", "missing resets age"),
        ("legacy_nextgen:event_age_alias", "legacy_b1s:numeric_change_age"),
    ),
    "TimeSince": PrimitiveContract(
        "TimeSince",
        "elapsed coordinates since the latest rising threshold activation; zero at a hit",
        _IMPLEMENTATION,
        _NUMERIC,
        "nonnegative float panel with NaN before first hit",
        "window is not used",
        "NaN until the first rising activation in each finite segment",
        "NaN resets hit history",
        "increments after a rising activation until the next activation",
        "event is a false-to-true raw-threshold transition",
        ("zero at every rising event", "increments by one between hits", "never equals absolute hit index"),
        ("legacy_nextgen:event_age_alias", "legacy_b1s:numeric_change_age"),
    ),
    "LastHit": PrimitiveContract(
        "LastHit",
        "absolute time-coordinate index of the latest rising threshold activation",
        _IMPLEMENTATION,
        _NUMERIC,
        "float coordinate-index panel with NaN before first hit",
        "window is not used",
        "NaN until the first rising activation in each finite segment",
        "NaN resets hit history",
        "holds the last activation coordinate until the next activation",
        "event is a false-to-true raw-threshold transition",
        ("equals coordinate index at a hit", "is piecewise constant between hits", "is not event age"),
        ("legacy_nextgen:event_age_alias", "legacy_b1s:numeric_change_age"),
    ),
    "FirstHit": PrimitiveContract(
        "FirstHit",
        "one-shot pulse at the first rising threshold activation of each finite segment",
        _IMPLEMENTATION,
        _NUMERIC,
        "binary float panel",
        "window is not used",
        "none after a finite coordinate",
        "NaN resets the segment; output is NaN at the missing coordinate",
        "one at only the first activation, zero at later activations in the segment",
        "event is a false-to-true raw-threshold transition",
        ("at most one pulse per finite segment", "later transitions are not FirstHit"),
        ("legacy_nextgen:transition_alias",),
    ),
    "Transition": PrimitiveContract(
        "Transition",
        "signed boolean-state change: +1 rising, -1 falling, 0 unchanged",
        _IMPLEMENTATION,
        _NUMERIC,
        "float panel in {-1,0,1}",
        "window is not used",
        "none after a finite coordinate",
        "NaN resets state; first finite active state is a +1 activation",
        "reports every state transition, not only the first",
        "raw threshold state",
        ("rising is +1", "falling is -1", "unchanged state is zero"),
        ("legacy_temporal:rising_only_transition", "legacy_nextgen:rising_only_transition", "legacy_b1s:any_numeric_change"),
    ),
    "PathShape": PrimitiveContract(
        "PathShape",
        "mean(last third) - mean(first third) inside the complete trailing window",
        _IMPLEMENTATION,
        _NUMERIC,
        _OUTPUT,
        "window is split into non-overlapping first/last thirds and must be >=3",
        "window-1 coordinates",
        "NaN unless the complete trailing window is finite",
        "active where early and late path thirds differ",
        "path geometry; not a short-minus-long moving average",
        ("constant path is zero", "is distinct from MultiScaleRelation"),
        ("legacy_nextgen:multiscale_alias",),
    ),
    "EventWindow": PrimitiveContract(
        "EventWindow",
        "count of rising threshold activations in the trailing window",
        _IMPLEMENTATION,
        _NUMERIC,
        "nonnegative integer-valued float panel",
        "window is the event-count lookback including t",
        "window-1 coordinates inside each finite segment",
        "NaN resets event history; windows never cross a missing coordinate",
        "counts rising activations, not active-state occupancy or arbitrary value changes",
        "event is a false-to-true raw-threshold transition",
        ("singleton event count is one", "persistent active state does not create repeated events"),
        ("legacy_temporal:active_state_count", "legacy_b1s:any_numeric_change_rate"),
    ),
    "MultiScaleRelation": PrimitiveContract(
        "MultiScaleRelation",
        "trailing short-window mean minus trailing long-window mean",
        _IMPLEMENTATION,
        _NUMERIC,
        _OUTPUT,
        "short_window < long_window; both include t",
        "long_window-1 coordinates",
        "NaN unless both complete windows are finite",
        "active where short and long path levels differ",
        "multi-scale level relation; not PathShape",
        ("constant path is zero", "short window must be strictly smaller than long window"),
        ("b1s:multiscale", "nextgen:MultiScaleRelation"),
    ),
}


def _matrix(values: np.ndarray) -> np.ndarray:
    result = np.asarray(values, dtype=float)
    if result.ndim != 2:
        raise ValueError("primitive input must have shape [asset,time]")
    if result.shape[1] == 0:
        raise ValueError("primitive input requires at least one time coordinate")
    return result


def _shift(values: np.ndarray, lag: int) -> np.ndarray:
    result = np.full(values.shape, np.nan, dtype=float)
    if lag < values.shape[1]:
        result[:, lag:] = values[:, :-lag]
    return result


def _rolling_apply(values: np.ndarray, window: int, function: Callable[[np.ndarray], float]) -> np.ndarray:
    result = np.full(values.shape, np.nan, dtype=float)
    for row in range(values.shape[0]):
        for column in range(window - 1, values.shape[1]):
            segment = values[row, column - window + 1 : column + 1]
            if np.isfinite(segment).all():
                result[row, column] = float(function(segment))
    return result


def _state_events(values: np.ndarray, threshold: float) -> tuple[np.ndarray, np.ndarray]:
    finite = np.isfinite(values)
    state = np.where(finite, values > threshold, False)
    rising = np.zeros(values.shape, dtype=bool)
    for row in range(values.shape[0]):
        previous_known = False
        previous_state = False
        for column in range(values.shape[1]):
            if not finite[row, column]:
                previous_known = False
                previous_state = False
                continue
            current = bool(state[row, column])
            rising[row, column] = current and (not previous_known or not previous_state)
            previous_known = True
            previous_state = current
    return state, rising


def evaluate_primitive(
    primitive_id: str,
    values: np.ndarray,
    *,
    window: int = 4,
    long_window: int = 8,
    threshold: float = 0.0,
) -> np.ndarray:
    """Evaluate one canonical primitive with contract-defined missing semantics."""

    if primitive_id not in CANONICAL_PRIMITIVES:
        raise ValueError(f"unknown or deprecated primitive_id: {primitive_id}")
    if window <= 0 or long_window <= 0:
        raise ValueError("windows must be positive")
    source = _matrix(values)
    finite = np.isfinite(source)

    if primitive_id == "Delta":
        lagged = _shift(source, window)
        return np.where(finite & np.isfinite(lagged), source - lagged, np.nan)
    if primitive_id == "Slope":
        if window < 2:
            raise ValueError("Slope requires window >= 2")
        axis = np.arange(window, dtype=float)
        centered = axis - axis.mean()
        denominator = float(np.sum(centered * centered))
        return _rolling_apply(source, window, lambda segment: np.sum(centered * segment) / denominator)
    if primitive_id == "Acceleration":
        lagged = _shift(source, window)
        twice = _shift(source, 2 * window)
        valid = finite & np.isfinite(lagged) & np.isfinite(twice)
        return np.where(valid, source - 2.0 * lagged + twice, np.nan)
    if primitive_id == "Persistence":
        return _rolling_apply(source, window, lambda segment: np.mean(segment > threshold))
    if primitive_id == "PathShape":
        if window < 3:
            raise ValueError("PathShape requires window >= 3")
        third = max(1, window // 3)
        return _rolling_apply(source, window, lambda segment: np.mean(segment[-third:]) - np.mean(segment[:third]))
    if primitive_id == "MultiScaleRelation":
        if long_window <= window:
            raise ValueError("MultiScaleRelation requires long_window > window")
        short = _rolling_apply(source, window, np.mean)
        long = _rolling_apply(source, long_window, np.mean)
        return np.where(np.isfinite(short) & np.isfinite(long), short - long, np.nan)

    state, rising = _state_events(source, threshold)
    result = np.full(source.shape, np.nan, dtype=float)
    if primitive_id == "Duration":
        for row in range(source.shape[0]):
            run = 0
            for column in range(source.shape[1]):
                if not finite[row, column]:
                    run = 0
                    continue
                run = run + 1 if state[row, column] else 0
                result[row, column] = float(run)
        return result
    if primitive_id == "StateAge":
        for row in range(source.shape[0]):
            previous_known = False
            previous_state = False
            age = 0
            for column in range(source.shape[1]):
                if not finite[row, column]:
                    previous_known = False
                    age = 0
                    continue
                current = bool(state[row, column])
                age = age + 1 if previous_known and current == previous_state else 0
                result[row, column] = float(age)
                previous_known = True
                previous_state = current
        return result
    if primitive_id == "Transition":
        for row in range(source.shape[0]):
            previous_known = False
            previous_state = False
            for column in range(source.shape[1]):
                if not finite[row, column]:
                    previous_known = False
                    previous_state = False
                    continue
                current = bool(state[row, column])
                if not previous_known:
                    result[row, column] = 1.0 if current else 0.0
                else:
                    result[row, column] = float(int(current) - int(previous_state))
                previous_known = True
                previous_state = current
        return result
    if primitive_id == "FirstHit":
        for row in range(source.shape[0]):
            seen = False
            for column in range(source.shape[1]):
                if not finite[row, column]:
                    seen = False
                    continue
                result[row, column] = 1.0 if rising[row, column] and not seen else 0.0
                seen = seen or bool(rising[row, column])
        return result
    if primitive_id == "TimeSince":
        for row in range(source.shape[0]):
            age = np.nan
            for column in range(source.shape[1]):
                if not finite[row, column]:
                    age = np.nan
                    continue
                if rising[row, column]:
                    age = 0.0
                elif np.isfinite(age):
                    age += 1.0
                result[row, column] = age
        return result
    if primitive_id == "LastHit":
        for row in range(source.shape[0]):
            last = np.nan
            for column in range(source.shape[1]):
                if not finite[row, column]:
                    last = np.nan
                    continue
                if rising[row, column]:
                    last = float(column)
                result[row, column] = last
        return result
    if primitive_id == "EventWindow":
        for row in range(source.shape[0]):
            segment_start = 0
            for column in range(source.shape[1]):
                if not finite[row, column]:
                    segment_start = column + 1
                    continue
                start = max(segment_start, column - window + 1)
                if column - start + 1 == window:
                    result[row, column] = float(np.count_nonzero(rising[row, start : column + 1]))
        return result
    raise AssertionError(primitive_id)


def primitive_contract_payload() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "authority": _IMPLEMENTATION,
        "scope": "deterministic non-market capability qualification only",
        "active_primitive_ids": list(CANONICAL_PRIMITIVES),
        "contracts": [contract.to_dict() for contract in CANONICAL_PRIMITIVES.values()],
    }
