from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Iterable

import numpy as np


LAYERS = ("syntax", "canonical", "exact_signal", "activation", "pnl_regime", "economic_hypothesis")


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
