"""Bounded real-data canary structural grammar and lazy policy protocol.

Data access, evaluator execution, cache ownership, and evidence persistence are
kept outside this package surface so a policy cannot inspect unvisited results.
"""

from .contracts import CandidateGenome, MutationReceipt, Proposal, SearchState
from .grammar import (
    CANONICAL_PRIMITIVE_IDS,
    CROSS_SECTIONAL_RELATIVE,
    DIRECTIONAL_STATEFUL,
    FROZEN_FIELD_SPECS,
    FROZEN_RELEASE_FIELDS,
    MECHANISM_FAMILIES,
    MECHANISM_MAPPING,
    MINIMUM_SUPPORT_SIZE,
    SPARSE_EVENT_CARRY,
    SPARSE_PRIMITIVES,
    TARGET_HORIZONS_HOURS,
    WINDOWLESS_PRIMITIVES,
    FrozenGrammar,
    GrammarFilter,
)
from .policies import (
    SUPPORTED_POLICIES,
    CEMLikePolicy,
    CanonicalTypedRandomPolicy,
    EvolutionaryPolicy,
    SearchPolicy,
    UCTUCBLikePolicy,
    build_policy,
)

__all__ = [
    "CANONICAL_PRIMITIVE_IDS",
    "CEMLikePolicy",
    "CROSS_SECTIONAL_RELATIVE",
    "CandidateGenome",
    "CanonicalTypedRandomPolicy",
    "DIRECTIONAL_STATEFUL",
    "EvolutionaryPolicy",
    "FROZEN_FIELD_SPECS",
    "FROZEN_RELEASE_FIELDS",
    "FrozenGrammar",
    "GrammarFilter",
    "MECHANISM_FAMILIES",
    "MECHANISM_MAPPING",
    "MINIMUM_SUPPORT_SIZE",
    "MutationReceipt",
    "Proposal",
    "SPARSE_EVENT_CARRY",
    "SPARSE_PRIMITIVES",
    "SUPPORTED_POLICIES",
    "SearchPolicy",
    "SearchState",
    "TARGET_HORIZONS_HOURS",
    "UCTUCBLikePolicy",
    "WINDOWLESS_PRIMITIVES",
    "build_policy",
]
