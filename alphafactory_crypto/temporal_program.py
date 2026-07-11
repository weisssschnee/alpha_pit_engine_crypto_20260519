from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Mapping

import numpy as np
import pandas as pd


PRIMITIVES = (
    "Delta", "Slope", "Acceleration", "Persistence", "Duration", "StateAge",
    "TimeSince", "Transition", "FirstHit", "LastHit", "PathShape",
    "EventWindow", "MultiScaleRelation",
)


@dataclass(frozen=True)
class TypedProgram:
    primitive: str
    source_identity: str
    parameters: Mapping[str, Any]
    input_type: str = "numeric"
    output_type: str = "numeric"
    observable_time_rule: str = "source_observable_time"
    maturity_rule: str = "source_maturity"
    pit_rule: str = "usable_time_lte_decision_time"


@dataclass(frozen=True)
class ObservationVector:
    values: pd.Series
    observable_time: pd.Series
    maturity_time: pd.Series

    def validate(self) -> None:
        if not isinstance(self.values.index, pd.DatetimeIndex) or not self.values.index.is_monotonic_increasing:
            raise ValueError("values require a sorted DatetimeIndex")
        if self.values.index.has_duplicates:
            raise ValueError("duplicate decision coordinates are forbidden")
        if not self.observable_time.index.equals(self.values.index) or not self.maturity_time.index.equals(self.values.index):
            raise ValueError("time metadata must share the value index")
        event = pd.Series(self.values.index, index=self.values.index)
        if (pd.to_datetime(self.observable_time, utc=True) < event).any():
            raise ValueError("observable_time cannot precede event_time")

    def pit_values(self) -> pd.Series:
        """Return the latest source record usable at each decision coordinate."""
        self.validate()
        usable = pd.concat(
            [pd.to_datetime(self.observable_time, utc=True), pd.to_datetime(self.maturity_time, utc=True)], axis=1
        ).max(axis=1)
        source = pd.DataFrame({"usable": usable, "event": self.values.index, "value": self.values.to_numpy()})
        source = source.sort_values(["usable", "event"], kind="mergesort")
        decisions = pd.DataFrame({"decision": self.values.index}).sort_values("decision")
        aligned = pd.merge_asof(
            decisions, source, left_on="decision", right_on="usable", direction="backward", allow_exact_matches=True
        )
        return pd.Series(aligned["value"].to_numpy(), index=self.values.index, dtype="float64")


def _canon_value(key: str, value: Any) -> Any:
    if key.endswith("_duration") or key in {"window", "short_window", "long_window", "max_age"}:
        ns = int(pd.Timedelta(value).value)
        if ns <= 0:
            raise ValueError(f"{key} must be positive")
        return {"duration_ns": ns}
    if isinstance(value, float):
        if not np.isfinite(value):
            raise ValueError("non-finite program parameters are forbidden")
        return 0.0 if value == 0.0 else float(value)
    if isinstance(value, (np.integer, int)):
        if int(value) <= 0 and key in {"periods", "short_periods", "long_periods"}:
            raise ValueError(f"{key} must be positive")
        return int(value)
    return value


def canonical_program(program: TypedProgram) -> dict[str, Any]:
    if program.primitive not in PRIMITIVES:
        raise ValueError(f"unknown typed primitive: {program.primitive}")
    params = {str(key): _canon_value(str(key), value) for key, value in sorted(program.parameters.items())}
    if program.primitive == "MultiScaleRelation":
        short = int(params.get("short_periods", 0))
        long = int(params.get("long_periods", 0))
        if short >= long:
            raise ValueError("short_periods must be less than long_periods")
    return {
        "primitive": program.primitive,
        "source_identity": program.source_identity,
        "parameters": params,
        "input_type": program.input_type,
        "output_type": program.output_type,
        "observable_time_rule": program.observable_time_rule,
        "maturity_rule": program.maturity_rule,
        "pit_rule": program.pit_rule,
    }


def program_identity(program: TypedProgram) -> str:
    payload = json.dumps(canonical_program(program), sort_keys=True, separators=(",", ":")).encode()
    return "typed-program:" + hashlib.sha256(payload).hexdigest()


def equivalent(left: TypedProgram, right: TypedProgram) -> bool:
    return program_identity(left) == program_identity(right)


def _periods(params: Mapping[str, Any], key: str = "periods", default: int = 1) -> int:
    value = int(params.get(key, default))
    if value <= 0:
        raise ValueError(f"{key} must be positive")
    return value


def _consecutive(values: pd.Series) -> pd.Series:
    truth = values.fillna(False).astype(bool)
    groups = (~truth).cumsum()
    return truth.groupby(groups).cumsum().astype(float)


def evaluate(program: TypedProgram, observations: ObservationVector) -> pd.Series:
    canonical_program(program)
    x = observations.pit_values()
    p = dict(program.parameters)
    op = program.primitive
    n = _periods(p)
    if op == "Delta":
        return x - x.shift(n)
    if op == "Slope":
        axis = np.arange(n, dtype=float)
        return x.rolling(n, min_periods=n).apply(lambda a: np.polyfit(axis, a, 1)[0], raw=True)
    if op == "Acceleration":
        return x.diff(n).diff(n)
    if op == "Persistence":
        threshold = float(p.get("threshold", 0.0))
        return (x > threshold).rolling(n, min_periods=n).mean()
    if op in {"Duration", "StateAge"}:
        return _consecutive(x > float(p.get("threshold", 0.0)))
    if op == "TimeSince":
        hit = x > float(p.get("threshold", 0.0))
        positions = pd.Series(np.arange(len(x), dtype=float), index=x.index)
        return positions - positions.where(hit).ffill()
    if op == "Transition":
        threshold = float(p.get("threshold", 0.0))
        state = x > threshold
        return (state & ~state.shift(1, fill_value=False)).astype(float)
    if op == "FirstHit":
        hit = x > float(p.get("threshold", 0.0))
        return (hit & ~hit.shift(1, fill_value=False)).astype(float)
    if op == "LastHit":
        hit = x > float(p.get("threshold", 0.0))
        positions = pd.Series(np.arange(len(x), dtype=float), index=x.index)
        return positions.where(hit).ffill()
    if op == "PathShape":
        return x.rolling(n, min_periods=n).apply(
            lambda a: float(np.nanmean(a[(2 * len(a)) // 3 :]) - np.nanmean(a[: max(1, len(a) // 3)])), raw=True
        )
    if op == "EventWindow":
        return (x > float(p.get("threshold", 0.0))).rolling(n, min_periods=1).sum()
    if op == "MultiScaleRelation":
        short = _periods(p, "short_periods")
        long = _periods(p, "long_periods")
        return x.rolling(short, min_periods=short).mean() - x.rolling(long, min_periods=long).mean()
    raise AssertionError(op)

