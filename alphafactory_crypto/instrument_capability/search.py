"""Deterministic proposal policies for the capability-only harness.

All policies consume the same precomputed aligned feedback.  They differ in
proposal behavior, not merely in labels, and they never inject a known planted
positive directly into the survivor slot.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
from collections import Counter
from dataclasses import dataclass
from types import MappingProxyType
from typing import Iterable, Mapping

from .feedback import FeedbackDecision, feedback_sort_key


SUPPORTED_ALGORITHMS = (
    "canonical_typed_random",
    "cem_like",
    "uct_ucb_like",
    "evolutionary",
)

# Historical B1S rotated these names over proposals but pooled feedback into a
# single preferred operator.  They are recorded as a degeneracy, not exposed as
# independent policies in this harness.
B1S_LABELS_DEGENERATE: Mapping[str, object] = MappingProxyType(
    {
        "labels": ("cem", "uct_mcts", "evolutionary"),
        "classification": "ALGORITHM_LABEL_DEGENERATE",
        "reason": "round_robin_labels_shared_one_operator_feedback_update",
    }
)

POLICY_BEHAVIOR: Mapping[str, str] = MappingProxyType(
    {
        "canonical_typed_random": "random_without_replacement_then_reshuffled_cycles",
        "cem_like": "full_coverage_then_elite_categorical_update",
        "uct_ucb_like": "one_visit_per_arm_then_ucb",
        "evolutionary": "full_coverage_then_aligned_parent_neighbor_mutation",
    }
)

CEM_ELITE_FRACTION = 0.25
CEM_ELITE_WEIGHT = 4
CEM_BASE_WEIGHT = 1
EVOLUTION_PARENT_FRACTION = 0.25
EVOLUTION_NEIGHBOR_OFFSETS = (-2, -1, 1, 2)
UCB_EXPLORATION = math.sqrt(2.0)


@dataclass(frozen=True, slots=True)
class SearchOutcome:
    proposal_order: tuple[str, ...]
    visit_counts: Mapping[str, int]
    survivor_id: str | None
    behavior_hash: str
    independent_behavior: bool

    def to_dict(self, variant_by_id: Mapping[str, str] | None = None) -> dict[str, object]:
        variants = variant_by_id or {}
        return {
            "proposal_order": list(self.proposal_order),
            "proposal_variants": [variants.get(candidate_id) for candidate_id in self.proposal_order],
            "visit_counts": dict(self.visit_counts),
            "survivor_id": self.survivor_id,
            "survivor_variant": variants.get(self.survivor_id) if self.survivor_id else None,
            "behavior_hash": self.behavior_hash,
            "independent_behavior": self.independent_behavior,
        }


def _candidate_universe(candidate_ids: Iterable[str]) -> tuple[str, ...]:
    candidates = tuple(str(candidate_id) for candidate_id in candidate_ids)
    if len(candidates) != len(set(candidates)):
        raise ValueError("candidate_ids must be unique")
    if any(not candidate_id for candidate_id in candidates):
        raise ValueError("candidate_ids cannot contain an empty identity")
    return candidates


def _validate_inputs(
    algorithm: str,
    candidates: tuple[str, ...],
    decisions_by_id: Mapping[str, FeedbackDecision],
    budget: int,
) -> None:
    if algorithm not in SUPPORTED_ALGORITHMS:
        raise ValueError(f"unsupported capability search algorithm: {algorithm}")
    if isinstance(budget, bool) or int(budget) != budget or budget < 0:
        raise ValueError("budget must be a non-negative integer")
    if budget and not candidates:
        raise ValueError("a positive budget requires at least one candidate")
    missing = [candidate_id for candidate_id in candidates if candidate_id not in decisions_by_id]
    if missing:
        raise KeyError(f"missing aligned feedback for candidates: {missing[:5]}")
    if algorithm != "canonical_typed_random" and budget < len(candidates):
        raise ValueError(f"{algorithm} requires budget >= candidate count for frozen initial coverage")


def _coverage_order(candidates: tuple[str, ...], seed: int) -> list[str]:
    order = list(candidates)
    random.Random(seed).shuffle(order)
    return order


def _canonical_typed_random(
    candidates: tuple[str, ...], seed: int, budget: int
) -> list[str]:
    rng = random.Random(seed)
    proposals: list[str] = []
    while len(proposals) < budget:
        cycle = list(candidates)
        rng.shuffle(cycle)
        proposals.extend(cycle[: budget - len(proposals)])
    return proposals


def _weighted_choice(
    rng: random.Random, candidates: tuple[str, ...], weights: Mapping[str, int]
) -> str:
    total = sum(weights[candidate_id] for candidate_id in candidates)
    draw = rng.randrange(total)
    cumulative = 0
    for candidate_id in candidates:
        cumulative += weights[candidate_id]
        if draw < cumulative:
            return candidate_id
    raise AssertionError("integer categorical draw escaped its support")


def _cem_like(
    candidates: tuple[str, ...],
    decisions: Mapping[str, FeedbackDecision],
    seed: int,
    budget: int,
) -> list[str]:
    coverage = _coverage_order(candidates, seed)
    proposals = list(coverage)
    elite_count = max(1, math.ceil(len(candidates) * CEM_ELITE_FRACTION))
    ranked = sorted(
        candidates,
        key=lambda candidate_id: feedback_sort_key(decisions[candidate_id], candidate_id),
        reverse=True,
    )
    elite = set(ranked[:elite_count])
    categorical_weights = {
        candidate_id: CEM_ELITE_WEIGHT if candidate_id in elite else CEM_BASE_WEIGHT
        for candidate_id in candidates
    }
    rng = random.Random(seed)
    # Consume the same shuffle as the initial coverage before adaptive draws.
    replay = list(candidates)
    rng.shuffle(replay)
    while len(proposals) < budget:
        proposals.append(_weighted_choice(rng, candidates, categorical_weights))
    return proposals


def _ordinal_rewards(
    candidates: tuple[str, ...], decisions: Mapping[str, FeedbackDecision]
) -> dict[str, float]:
    ordered = sorted(
        candidates,
        key=lambda candidate_id: feedback_sort_key(decisions[candidate_id], candidate_id),
    )
    if len(ordered) == 1:
        return {ordered[0]: 1.0}
    return {
        candidate_id: rank / (len(ordered) - 1)
        for rank, candidate_id in enumerate(ordered)
    }


def _seeded_priority(seed: int, candidate_id: str) -> int:
    digest = hashlib.sha256(f"{seed}|{candidate_id}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


def _uct_ucb_like(
    candidates: tuple[str, ...],
    decisions: Mapping[str, FeedbackDecision],
    seed: int,
    budget: int,
) -> list[str]:
    proposals = _coverage_order(candidates, seed)
    rewards = _ordinal_rewards(candidates, decisions)
    visits = Counter(proposals)
    value = {candidate_id: rewards[candidate_id] * visits[candidate_id] for candidate_id in candidates}
    while len(proposals) < budget:
        total = len(proposals)

        def ucb_key(candidate_id: str) -> tuple[float, int]:
            count = visits[candidate_id]
            mean = value[candidate_id] / count
            exploration = UCB_EXPLORATION * math.sqrt(math.log(total + 1.0) / count)
            return mean + exploration, _seeded_priority(seed, candidate_id)

        selected = max(candidates, key=ucb_key)
        proposals.append(selected)
        visits[selected] += 1
        value[selected] += rewards[selected]
    return proposals


def _evolutionary(
    candidates: tuple[str, ...],
    decisions: Mapping[str, FeedbackDecision],
    seed: int,
    budget: int,
) -> list[str]:
    proposals = _coverage_order(candidates, seed)
    ranked = sorted(
        candidates,
        key=lambda candidate_id: feedback_sort_key(decisions[candidate_id], candidate_id),
        reverse=True,
    )
    parent_count = max(1, math.ceil(len(candidates) * EVOLUTION_PARENT_FRACTION))
    parents = tuple(ranked[:parent_count])
    sequence_index = {candidate_id: index for index, candidate_id in enumerate(candidates)}
    offsets = tuple(offset for offset in EVOLUTION_NEIGHBOR_OFFSETS if offset % len(candidates))
    if not offsets:
        offsets = (0,)
    rng = random.Random(seed)
    replay = list(candidates)
    rng.shuffle(replay)
    while len(proposals) < budget:
        parent = parents[rng.randrange(len(parents))]
        offset = offsets[rng.randrange(len(offsets))]
        child_index = (sequence_index[parent] + offset) % len(candidates)
        proposals.append(candidates[child_index])
    return proposals


def _survivor(
    proposals: Iterable[str], decisions: Mapping[str, FeedbackDecision]
) -> str | None:
    visited = set(proposals)
    if not visited:
        return None
    return max(
        visited,
        key=lambda candidate_id: feedback_sort_key(decisions[candidate_id], candidate_id),
    )


def _behavior_hash(
    proposals: tuple[str, ...], visit_counts: Mapping[str, int], survivor_id: str | None
) -> str:
    # Algorithm label is deliberately excluded so label-only aliases hash equal.
    payload = {
        "proposal_order": proposals,
        "visit_counts": sorted(visit_counts.items()),
        "survivor_id": survivor_id,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def run_search(
    algorithm: str,
    candidate_ids: Iterable[str],
    decisions_by_id: Mapping[str, FeedbackDecision],
    seed: int,
    budget: int,
) -> SearchOutcome:
    """Run one fixed-budget capability policy over aligned candidate feedback."""

    algorithm = str(algorithm)
    candidates = _candidate_universe(candidate_ids)
    _validate_inputs(algorithm, candidates, decisions_by_id, budget)
    budget = int(budget)
    seed = int(seed)

    if not candidates:
        proposal_order: tuple[str, ...] = ()
        visit_counts: dict[str, int] = {}
        survivor_id = None
        return SearchOutcome(
            proposal_order=proposal_order,
            visit_counts=visit_counts,
            survivor_id=survivor_id,
            behavior_hash=_behavior_hash(proposal_order, visit_counts, survivor_id),
            independent_behavior=False,
        )

    if algorithm == "canonical_typed_random":
        proposals = _canonical_typed_random(candidates, seed, budget)
    elif algorithm == "cem_like":
        proposals = _cem_like(candidates, decisions_by_id, seed, budget)
    elif algorithm == "uct_ucb_like":
        proposals = _uct_ucb_like(candidates, decisions_by_id, seed, budget)
    else:
        proposals = _evolutionary(candidates, decisions_by_id, seed, budget)

    proposal_order = tuple(proposals)
    counts = Counter(proposal_order)
    visit_counts = {candidate_id: int(counts[candidate_id]) for candidate_id in candidates}
    survivor_id = _survivor(proposal_order, decisions_by_id)
    behavior_hash = _behavior_hash(proposal_order, visit_counts, survivor_id)
    adaptive_behavior_exercised = algorithm == "canonical_typed_random" or (
        len(candidates) > 1 and budget > len(candidates)
    )
    return SearchOutcome(
        proposal_order=proposal_order,
        visit_counts=visit_counts,
        survivor_id=survivor_id,
        behavior_hash=behavior_hash,
        independent_behavior=adaptive_behavior_exercised,
    )
