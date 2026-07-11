from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Iterable

import numpy as np


LAYERS = ("syntax", "canonical", "exact_signal", "activation", "behaviour", "pnl_regime", "economic_hypothesis")
SPENT_DIAGNOSTIC_BLOCKS = ("validation", "test", "recent", "stress")


def _id(prefix: str, payload: bytes) -> str:
    return f"{prefix}:" + hashlib.sha256(payload).hexdigest()[:24]


def syntax_identity(expression: str) -> str:
    normalized = str(expression).replace("\r\n", "\n").strip()
    return _id("syntax", normalized.encode("utf-8"))


def canonical_identity(canonical_expression: str) -> str:
    return _id("canonical", str(canonical_expression).strip().encode("utf-8"))


def exact_signal_identity(fingerprint: str) -> str:
    value = str(fingerprint).strip()
    if not value:
        raise ValueError("exact signal fingerprint is required")
    return _id("exact-signal", value.encode("utf-8"))


def activation_identity(mask: np.ndarray, *, universe_ids: Iterable[str], timestamps_ns: np.ndarray) -> str:
    universe = tuple(str(value) for value in universe_ids)
    timestamps = np.asarray(timestamps_ns, dtype=np.int64)
    active = np.asarray(mask, dtype=bool)
    if active.shape != (len(universe), len(timestamps)):
        raise ValueError("activation mask shape must match universe x timestamps")
    payload = "|".join(universe).encode("utf-8") + timestamps.tobytes() + np.packbits(active, axis=None).tobytes()
    return _id("activation", payload)


def activation_cluster_identity(activation_id: str) -> str:
    value = str(activation_id).strip()
    if not value.startswith("activation:"):
        raise ValueError("activation cluster requires an activation behavior identity")
    return _id("activation-cluster", value.encode("utf-8"))


def register_behaviour_identity(identity_id: str, provenance: str) -> "RegisteredIdentity":
    if not str(identity_id).startswith("behaviour:") or not provenance:
        raise ValueError("behaviour identity requires behaviour:* id and provenance")
    return RegisteredIdentity("behaviour", identity_id, "REGISTERED_OBSERVATION_ONLY", provenance)


@dataclass(frozen=True)
class RegisteredIdentity:
    layer: str
    identity_id: str
    status: str
    provenance: str


def register_pnl_regime_identity(identity_id: str, provenance: str) -> RegisteredIdentity:
    if not identity_id or not provenance:
        raise ValueError("PnL/regime identity requires explicit id and provenance")
    return RegisteredIdentity("pnl_regime", identity_id, "REGISTERED", provenance)


def register_economic_hypothesis(hypothesis_id: str, provenance: str) -> RegisteredIdentity:
    if not hypothesis_id.startswith("hypothesis:") or not provenance:
        raise ValueError("economic hypothesis requires hypothesis:* id and provenance")
    return RegisteredIdentity("economic_hypothesis", hypothesis_id, "REGISTERED", provenance)


def pnl_regime_diagnostic_identity(
    metrics: dict[str, float], block_roles: dict[str, str]
) -> RegisteredIdentity:
    missing = sorted(set(SPENT_DIAGNOSTIC_BLOCKS).difference(metrics))
    if missing:
        raise ValueError(f"missing PnL/regime diagnostic blocks: {missing}")
    invalid_roles = sorted(
        block for block in SPENT_DIAGNOSTIC_BLOCKS if block_roles.get(block) != "SPENT_HISTORICAL_EVALUATION"
    )
    if invalid_roles:
        raise PermissionError(f"PnL/regime identity requires spent historical blocks: {invalid_roles}")
    parts = []
    for block in SPENT_DIAGNOSTIC_BLOCKS:
        value = float(metrics[block])
        if not np.isfinite(value):
            bucket = "MISSING"
        elif value > 0:
            bucket = "POS"
        elif value < 0:
            bucket = "NEG"
        else:
            bucket = "ZERO"
        parts.append(f"{block}:{bucket}")
    pattern = "|".join(parts)
    return RegisteredIdentity(
        "pnl_regime",
        _id("pnl-regime", f"spent-split-sign-v1|{pattern}".encode("utf-8")),
        "REGISTERED_DIAGNOSTIC_ONLY",
        f"SPENT_HISTORICAL_EVALUATION;sign-buckets-only;{pattern}",
    )


def economic_hypothesis_assignment(
    hypothesis_id: str,
    *,
    expression: str,
    required_fields: Iterable[str],
    required_operators: Iterable[str] = (),
    mechanism: str,
    provenance: str,
) -> RegisteredIdentity:
    missing = sorted(field for field in required_fields if str(field) not in str(expression))
    if missing:
        raise ValueError(f"economic hypothesis fields absent from expression: {missing}")
    missing_operators = sorted(
        operator for operator in required_operators if f"{str(operator)}(" not in str(expression)
    )
    if missing_operators:
        raise ValueError(f"economic hypothesis operators absent from expression: {missing_operators}")
    performance_terms = {"reward", "sortino", "sharpe", "profit", "pareto", "leaderboard"}
    semantic_text = f"{hypothesis_id} {mechanism}".lower()
    if any(term in semantic_text for term in performance_terms):
        raise ValueError("economic hypothesis cannot be named from performance evidence")
    registered = register_economic_hypothesis(hypothesis_id, provenance)
    return RegisteredIdentity(
        registered.layer,
        registered.identity_id,
        registered.status,
        f"{provenance};fields={','.join(sorted(required_fields))};operators={','.join(sorted(required_operators))};mechanism={mechanism}",
    )
