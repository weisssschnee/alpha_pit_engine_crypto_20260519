"""Deterministic, non-market qualification for the internal search instrument.

This package is intentionally capability-only.  It does not load market data,
open evaluation roles, or run a performance search.
"""

from .feedback import FeedbackDecision, StrictMetrics, aligned_feedback
from .mapping import MappingContract, MappingResult, map_portfolio
from .primitives import CANONICAL_PRIMITIVES, PrimitiveContract, evaluate_primitive

__all__ = [
    "CANONICAL_PRIMITIVES",
    "FeedbackDecision",
    "MappingContract",
    "MappingResult",
    "PrimitiveContract",
    "StrictMetrics",
    "aligned_feedback",
    "evaluate_primitive",
    "map_portfolio",
]
