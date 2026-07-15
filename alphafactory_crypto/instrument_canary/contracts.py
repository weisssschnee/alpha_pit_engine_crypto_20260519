"""Small immutable contracts shared by the real-data canary search layer.

The contracts in this module contain structural identities only.  They do not
carry materialized arrays, market metrics, planted roles, or evidence labels.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from typing import Any, Mapping


GENOME_SCHEMA_VERSION = 1


def _canonical_float(value: float | None) -> float | None:
    if value is None:
        return None
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("genome floating-point parameters must be finite")
    return 0.0 if result == 0.0 else result


def canonical_json_bytes(payload: Mapping[str, Any]) -> bytes:
    """Return the one canonical JSON encoding used by structural identities."""

    return json.dumps(
        dict(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


@dataclass(frozen=True, slots=True)
class CandidateGenome:
    """One legal structural candidate before data materialization.

    ``window`` and ``long_window`` use ``None`` as their only N/A value.  This
    prevents windowless primitives from acquiring fake identities through
    parameters that their canonical implementation ignores.
    """

    field_id: str
    representation_id: str
    primitive_id: str
    window: int | None
    long_window: int | None
    threshold: float | None
    mechanism_family: str
    target_horizon_hours: int

    def __post_init__(self) -> None:
        for name in (
            "field_id",
            "representation_id",
            "primitive_id",
            "mechanism_family",
        ):
            if not str(getattr(self, name)).strip():
                raise ValueError(f"{name} must be non-empty")
        for name in ("window", "long_window"):
            value = getattr(self, name)
            if value is not None and (
                isinstance(value, bool) or int(value) != value or int(value) <= 0
            ):
                raise ValueError(f"{name} must be a positive integer or None")
        if (
            isinstance(self.target_horizon_hours, bool)
            or int(self.target_horizon_hours) != self.target_horizon_hours
            or int(self.target_horizon_hours) <= 0
        ):
            raise ValueError("target_horizon_hours must be a positive integer")
        _canonical_float(self.threshold)

    def canonical_dict(self) -> dict[str, Any]:
        """Return the complete, label-free structural identity payload."""

        return {
            "schema_version": GENOME_SCHEMA_VERSION,
            "field_id": self.field_id,
            "representation_id": self.representation_id,
            "primitive_id": self.primitive_id,
            "window": self.window,
            "long_window": self.long_window,
            "threshold": _canonical_float(self.threshold),
            "mechanism_family": self.mechanism_family,
            "target_horizon_hours": int(self.target_horizon_hours),
        }

    def canonical_bytes(self) -> bytes:
        return canonical_json_bytes(self.canonical_dict())

    @property
    def candidate_id(self) -> str:
        return "crypto-candidate:" + hashlib.sha256(self.canonical_bytes()).hexdigest()

    @property
    def identity(self) -> str:
        """Alias retained for consumers that call the structural ID identity."""

        return self.candidate_id


@dataclass(frozen=True, slots=True)
class MutationReceipt:
    """Proof that an evolutionary child was generated from a concrete parent."""

    operator: str
    parent_id: str
    child_id: str
    changed_genes: tuple[str, ...]
    parent_genome: Mapping[str, Any]
    child_genome: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "operator": self.operator,
            "parent_id": self.parent_id,
            "child_id": self.child_id,
            "changed_genes": list(self.changed_genes),
            "parent_genome": dict(self.parent_genome),
            "child_genome": dict(self.child_genome),
        }


@dataclass(frozen=True, slots=True)
class Proposal:
    """One policy proposal.  It intentionally contains no feedback."""

    policy_name: str
    ordinal: int
    genome: CandidateGenome
    parent_id: str | None = None
    mutation_receipt: MutationReceipt | None = None

    def __post_init__(self) -> None:
        if not self.policy_name or self.ordinal < 0:
            raise ValueError("proposal requires a policy name and non-negative ordinal")
        if self.mutation_receipt is None:
            if self.parent_id is not None:
                raise ValueError("unmutated proposal cannot declare a parent_id")
            return
        receipt = self.mutation_receipt
        if self.parent_id is None or receipt.parent_id != self.parent_id:
            raise ValueError("mutation receipt parent identity mismatch")
        if receipt.child_id != self.genome.candidate_id:
            raise ValueError("mutation receipt child identity mismatch")
        if dict(receipt.child_genome) != self.genome.canonical_dict():
            raise ValueError("mutation receipt child genome mismatch")
        if not receipt.changed_genes or len(receipt.changed_genes) != len(
            set(receipt.changed_genes)
        ):
            raise ValueError("mutation receipt requires unique changed genes")

    @property
    def candidate_id(self) -> str:
        return self.genome.candidate_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "policy_name": self.policy_name,
            "ordinal": self.ordinal,
            "candidate_id": self.candidate_id,
            "genome": self.genome.canonical_dict(),
            "parent_id": self.parent_id,
            "mutation_receipt": (
                self.mutation_receipt.to_dict() if self.mutation_receipt else None
            ),
        }


@dataclass(frozen=True, slots=True)
class SearchState:
    """Minimal engine-to-policy state with no global cache or feedback surface."""

    step: int
    remaining_budget: int | None = None

    def __post_init__(self) -> None:
        if isinstance(self.step, bool) or int(self.step) != self.step or self.step < 0:
            raise ValueError("step must be a non-negative integer")
        if self.remaining_budget is not None and (
            isinstance(self.remaining_budget, bool)
            or int(self.remaining_budget) != self.remaining_budget
            or self.remaining_budget < 0
        ):
            raise ValueError("remaining_budget must be a non-negative integer or None")


__all__ = [
    "CandidateGenome",
    "GENOME_SCHEMA_VERSION",
    "MutationReceipt",
    "Proposal",
    "SearchState",
    "canonical_json_bytes",
]
