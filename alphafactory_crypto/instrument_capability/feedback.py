"""Frozen capability-only feedback aligned to strict feasibility.

This module deliberately does not learn weights from historical returns.  The
rules below are fixed engineering contracts for synthetic capability tests.
The legacy zero-cost gross proxy is retained only as a comparison diagnostic;
it never participates in the aligned ordering.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from types import MappingProxyType
from typing import Iterable, Mapping


# Thresholds are predeclared capability-test conventions.  ``cost`` is mean
# mapped cost drag; 0.0006 is 1.20 units of turnover at the frozen 5 bps rate.
FEASIBILITY_THRESHOLDS: Mapping[str, float] = MappingProxyType(
    {
        "mapped_net_metric": 0.0,
        "benchmark_increment": 0.0,
        "worst_block_margin": 0.0,
        "positive_block_fraction": 0.40,
        "turnover": 1.20,
        "cost": 0.0006,
        "concentration": 0.25,
        "support": 0.80,
    }
)

# Positive direction means larger is better; negative means smaller is better.
FEASIBILITY_DIRECTIONS: Mapping[str, int] = MappingProxyType(
    {
        "mapped_net_metric": 1,
        "benchmark_increment": 1,
        "worst_block_margin": 1,
        "positive_block_fraction": 1,
        "turnover": -1,
        "cost": -1,
        "concentration": -1,
        "support": 1,
    }
)

# Scales only make heterogeneous margins dimensionless.  They are fixed before
# any capability result and must not be adapted to observed returns.
FEASIBILITY_NORMALIZATION: Mapping[str, float] = MappingProxyType(
    {
        "mapped_net_metric": 0.0001,
        "benchmark_increment": 0.0001,
        "worst_block_margin": 0.0001,
        "positive_block_fraction": 0.10,
        "turnover": 0.30,
        "cost": 0.0001,
        "concentration": 0.05,
        "support": 0.10,
    }
)

FEASIBILITY_ORDER = tuple(FEASIBILITY_THRESHOLDS)
MISSING_VALUE_RULE = "HARD_BLOCK_BEFORE_STRICT_ORDERING"
NORMALIZED_MARGIN_CLIP = 10.0
BLOCKED_DISTANCE = -(NORMALIZED_MARGIN_CLIP + 1.0)
OLD_PROXY_MIN_OBSERVATIONS = 24
OLD_PROXY_DISPERSION_EPSILON = 1e-15


@dataclass(frozen=True, slots=True)
class StrictMetrics:
    """Small common bridge between explicit mapping and strict feasibility."""

    mapped_net_metric: float
    benchmark_increment: float
    worst_block_margin: float
    positive_block_fraction: float
    turnover: float
    cost: float
    concentration: float
    support: float
    gross_proxy: float
    finite: bool


@dataclass(frozen=True, slots=True)
class FeedbackDecision:
    """Result of hard admission checks followed by strict-feasibility order."""

    blocked: bool
    feasible: bool
    violations: tuple[str, ...]
    distance: float
    sort_key: tuple[int | float, ...]
    reason: str


def old_zero_cost_gross_proxy(gross_returns: Iterable[float]) -> float:
    """Reproduce the legacy zero-cost gross risk ratio for diagnostics only."""

    values = [float(value) for value in gross_returns if math.isfinite(float(value))]
    if len(values) < OLD_PROXY_MIN_OBSERVATIONS:
        return float("-inf")
    mean = math.fsum(values) / len(values)
    variance = math.fsum((value - mean) ** 2 for value in values) / len(values)
    dispersion = math.sqrt(max(0.0, variance))
    if dispersion <= OLD_PROXY_DISPERSION_EPSILON:
        return float("-inf")
    return mean / dispersion * math.sqrt(len(values))


def _normalized_margin(name: str, value: float) -> float:
    threshold = FEASIBILITY_THRESHOLDS[name]
    direction = FEASIBILITY_DIRECTIONS[name]
    scale = FEASIBILITY_NORMALIZATION[name]
    raw_margin = direction * (value - threshold) / scale
    return max(-NORMALIZED_MARGIN_CLIP, min(NORMALIZED_MARGIN_CLIP, raw_margin))


def _decision_sort_key(
    *, blocked: bool, feasible: bool, margins: Mapping[str, float]
) -> tuple[int | float, ...]:
    if blocked:
        return (0, 0, 0, BLOCKED_DISTANCE, *(BLOCKED_DISTANCE for _ in FEASIBILITY_ORDER))
    passed = sum(margin >= 0.0 for margin in margins.values())
    distance = min(margins.values())
    # Higher tuple values are always better.  Gross proxy is intentionally absent.
    return (
        1,
        int(feasible),
        passed,
        distance,
        *(margins[name] for name in FEASIBILITY_ORDER),
    )


def _blocked_decision(violations: tuple[str, ...]) -> FeedbackDecision:
    return FeedbackDecision(
        blocked=True,
        feasible=False,
        violations=violations,
        distance=BLOCKED_DISTANCE,
        sort_key=_decision_sort_key(blocked=True, feasible=False, margins={}),
        reason="HARD_BLOCK:" + "|".join(violations),
    )


def aligned_feedback(
    metrics: StrictMetrics,
    *,
    legal: bool,
    mapping_present: bool,
    wrong_lag: bool,
    primitive_alias_conflict: bool,
) -> FeedbackDecision:
    """Apply hard blocks first, then frozen lexicographic feasibility ordering."""

    hard_violations: list[str] = []
    if not legal:
        hard_violations.append("ILLEGAL_PROPOSAL")
    if not mapping_present:
        hard_violations.append("MAPPING_MISSING")
    if wrong_lag:
        hard_violations.append("WRONG_LAG")
    if primitive_alias_conflict:
        hard_violations.append("PRIMITIVE_ALIAS_CONFLICT")

    # Contract violations return before strict metric values are inspected.
    if hard_violations:
        return _blocked_decision(tuple(hard_violations))

    strict_values = {name: float(getattr(metrics, name)) for name in FEASIBILITY_ORDER}
    if not metrics.finite or any(not math.isfinite(value) for value in strict_values.values()):
        return _blocked_decision(("NON_FINITE_STRICT_METRICS",))

    margins = {name: _normalized_margin(name, value) for name, value in strict_values.items()}
    violations = tuple(name.upper() for name in FEASIBILITY_ORDER if margins[name] < 0.0)
    feasible = not violations
    distance = min(margins.values())
    reason = "STRICT_FEASIBILITY_PASS" if feasible else "STRICT_FEASIBILITY_FAIL:" + "|".join(violations)
    return FeedbackDecision(
        blocked=False,
        feasible=feasible,
        violations=violations,
        distance=distance,
        sort_key=_decision_sort_key(blocked=False, feasible=feasible, margins=margins),
        reason=reason,
    )


def feedback_sort_key(
    decision: FeedbackDecision, canonical_identity: str = ""
) -> tuple[int | float | str, ...]:
    """Return a stable higher-is-better key with an explicit final tie-break."""

    return (*decision.sort_key, str(canonical_identity))


def feedback_contract_payload() -> dict[str, object]:
    """Return the frozen, predeclared feedback contract for evidence output."""

    return {
        "schema_version": 1,
        "method": "LEXICOGRAPHIC_STRICT_FEASIBILITY_ORDERING",
        "hard_blocks_before_strict": [
            "ILLEGAL_PROPOSAL",
            "MAPPING_MISSING",
            "WRONG_LAG",
            "PRIMITIVE_ALIAS_CONFLICT",
            "NON_FINITE_STRICT_METRICS",
        ],
        "axis_order": list(FEASIBILITY_ORDER),
        "thresholds": dict(FEASIBILITY_THRESHOLDS),
        "directions": dict(FEASIBILITY_DIRECTIONS),
        "normalization": dict(FEASIBILITY_NORMALIZATION),
        "normalized_margin_clip": NORMALIZED_MARGIN_CLIP,
        "missing_handling": MISSING_VALUE_RULE,
        "scalar_weights": None,
        "legacy_zero_cost_gross_proxy_role": "DIAGNOSTIC_ONLY_NOT_IN_ORDERING",
        "strict_only_axes": ["complete IC surface", "placebo", "complete Pareto coordinates", "expensive controls"],
        "scope": "deterministic synthetic capability; not economic performance evidence",
    }
