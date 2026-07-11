from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Mapping

import pandas as pd


@dataclass(frozen=True)
class TemporalObservation:
    event_time: pd.Timestamp
    observable_time: pd.Timestamp
    maturity_time: pd.Timestamp

    @property
    def usable_time(self) -> pd.Timestamp:
        return max(self.observable_time, self.maturity_time)

    def validate(self) -> None:
        if self.observable_time < self.event_time:
            raise ValueError("observable_time cannot precede event_time")

    def assert_usable_at(self, decision_time: pd.Timestamp) -> None:
        self.validate()
        if decision_time < self.usable_time:
            raise PermissionError("temporal observation is not usable at decision time")


@dataclass(frozen=True)
class PrimitiveSpec:
    primitive_id: str
    source_identity: str
    parameters: Mapping[str, Any]
    event_identity_policy: str = "none"
    observable_policy: str = "source_contract"
    maturity_rule: str = "source_maturity"
    tolerance_ns: int = 0


def _duration_ns(value: Any) -> int:
    return int(pd.Timedelta(value).value)


def canonicalize_primitive(spec: PrimitiveSpec) -> dict[str, Any]:
    primitive = spec.primitive_id
    params = dict(spec.parameters)
    if primitive == "lag":
        periods_ns = _duration_ns(params.get("period", "0h"))
        if periods_ns < 0:
            raise ValueError("legal lag cannot look into the future")
        if periods_ns == 0:
            primitive = "identity"
            params = {}
        else:
            params = {"period_ns": periods_ns}
    elif primitive == "past_window":
        window_ns = _duration_ns(params["window"])
        if window_ns <= 0:
            raise ValueError("past window must be positive")
        params = {"closed": "left", "window_ns": window_ns}
    elif primitive in {"event_observed", "event_age", "matured_event_value", "identity"}:
        params = {str(key): params[key] for key in sorted(params)}
    else:
        raise ValueError(f"unknown temporal primitive: {primitive}")
    return {
        "primitive_id": primitive,
        "source_identity": spec.source_identity,
        "parameters": params,
        "event_identity_policy": spec.event_identity_policy,
        "observable_policy": spec.observable_policy,
        "maturity_rule": spec.maturity_rule,
        "tolerance_ns": int(spec.tolerance_ns),
    }


def primitive_equivalence_id(spec: PrimitiveSpec) -> str:
    canonical = canonicalize_primitive(spec)
    payload = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "temporal-equivalence:" + hashlib.sha256(payload).hexdigest()[:24]


def temporal_equivalent(left: PrimitiveSpec, right: PrimitiveSpec) -> bool:
    return primitive_equivalence_id(left) == primitive_equivalence_id(right)
