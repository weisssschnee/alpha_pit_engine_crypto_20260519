"""Generative, feedback-local policies for the real-data canary grammar.

No policy accepts a candidate universe or a feedback map.  ``propose`` creates
one structural genome; ``update`` is the only path by which that policy can
observe feedback for the proposal it just visited.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Sequence

from .contracts import CandidateGenome, Proposal, SearchState, canonical_json_bytes
from .grammar import (
    MECHANISM_FAMILIES,
    FrozenGrammar,
    GrammarCell,
)


SUPPORTED_POLICIES = (
    "canonical_typed_random",
    "cem_like",
    "uct_ucb_like",
    "evolutionary",
)

CEM_MIN_OBSERVATIONS = 8
CEM_ELITE_FRACTION = 0.25
CEM_ELITE_WEIGHT = 4.0
UCT_EXPLORATION = math.sqrt(2.0)
EVOLUTION_BOOTSTRAP_VISITS = 8
EVOLUTION_PARENT_FRACTION = 0.25


@dataclass(frozen=True, slots=True)
class _Observation:
    candidate_id: str
    genome: CandidateGenome
    rank_key: tuple[float, ...]
    scalar: float


def _value(feedback: Any, name: str, default: Any = None) -> Any:
    if isinstance(feedback, Mapping):
        return feedback.get(name, default)
    return getattr(feedback, name, default)


def _finite_float(value: Any, default: float = 0.0) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    return result if math.isfinite(result) else default


def _feedback_rank_key(feedback: Any) -> tuple[float, ...]:
    if isinstance(feedback, (int, float)) and not isinstance(feedback, bool):
        return (_finite_float(feedback),)
    raw = _value(feedback, "sort_key")
    if isinstance(raw, Sequence) and not isinstance(raw, (str, bytes)):
        converted = tuple(_finite_float(value) for value in raw)
        if converted:
            return converted
    return (_feedback_scalar(feedback),)


def _feedback_scalar(feedback: Any) -> float:
    if isinstance(feedback, (int, float)) and not isinstance(feedback, bool):
        return _finite_float(feedback)
    distance = _finite_float(_value(feedback, "distance"), 0.0)
    if bool(_value(feedback, "blocked", False)):
        return -20.0 + distance
    if bool(_value(feedback, "feasible", False)):
        return 20.0 + distance
    return distance


def _weighted_choice(
    rng: random.Random, values: Sequence[Any], weights: Sequence[float]
) -> Any:
    if not values or len(values) != len(weights):
        raise ValueError("categorical values/weights must be non-empty and aligned")
    total = math.fsum(weights)
    if not math.isfinite(total) or total <= 0.0 or any(weight <= 0 for weight in weights):
        raise ValueError("categorical weights must be finite and positive")
    draw = rng.random() * total
    cumulative = 0.0
    for value, weight in zip(values, weights):
        cumulative += weight
        if draw < cumulative:
            return value
    return values[-1]


def _rng_hash(rng: random.Random) -> str:
    return hashlib.sha256(repr(rng.getstate()).encode("utf-8")).hexdigest()


class SearchPolicy(ABC):
    """Base protocol that exposes feedback only through proposal-local update."""

    policy_name: str

    def __init__(self, grammar: FrozenGrammar, seed: int) -> None:
        if not isinstance(grammar, FrozenGrammar):
            raise TypeError("policy requires FrozenGrammar")
        self.grammar = grammar
        self.seed = int(seed)
        self._rng = random.Random(self.seed)
        self._proposal_count = 0
        self._pending: dict[int, Proposal] = {}
        self._updated_ordinals: set[int] = set()
        self._observations: list[_Observation] = []

    def _proposal(
        self,
        genome: CandidateGenome,
        *,
        parent_id: str | None = None,
        mutation_receipt: Any = None,
    ) -> Proposal:
        self.grammar.validate(genome)
        ordinal = self._proposal_count
        self._proposal_count += 1
        proposal = Proposal(
            policy_name=self.policy_name,
            ordinal=ordinal,
            genome=genome,
            parent_id=parent_id,
            mutation_receipt=mutation_receipt,
        )
        self._pending[ordinal] = proposal
        return proposal

    def _check_state(self, state: SearchState) -> None:
        if not isinstance(state, SearchState):
            raise TypeError("propose requires SearchState")
        if state.remaining_budget == 0:
            raise ValueError("cannot propose with zero remaining budget")
        if state.step != self._proposal_count:
            raise ValueError(
                "SearchState.step must equal this policy's next proposal ordinal"
            )
        if self._pending:
            raise RuntimeError(
                "policy is single-flight: consume pending proposal feedback before propose"
            )

    @abstractmethod
    def propose(self, state: SearchState) -> Proposal:
        """Generate one structural proposal without reading global feedback."""

    def update(self, proposal: Proposal, feedback: Any) -> None:
        """Expose feedback for exactly one proposal previously emitted by this policy."""

        if not isinstance(proposal, Proposal) or proposal.policy_name != self.policy_name:
            raise ValueError("feedback proposal belongs to a different policy")
        if proposal.ordinal in self._updated_ordinals:
            raise ValueError("proposal feedback was already consumed")
        expected = self._pending.get(proposal.ordinal)
        if expected != proposal:
            raise ValueError("feedback requires an exact pending proposal")
        feedback_candidate_id = _value(feedback, "candidate_id")
        if str(feedback_candidate_id or "") != proposal.candidate_id:
            raise ValueError("feedback candidate identity mismatch")
        observation = _Observation(
            candidate_id=proposal.candidate_id,
            genome=proposal.genome,
            rank_key=_feedback_rank_key(feedback),
            scalar=_feedback_scalar(feedback),
        )
        self._observations.append(observation)
        self._updated_ordinals.add(proposal.ordinal)
        self._after_update(proposal, observation)
        self._pending.pop(proposal.ordinal)

    def _after_update(self, proposal: Proposal, observation: _Observation) -> None:
        del proposal, observation

    @property
    def visited_feedback(self) -> Mapping[str, float]:
        """Read-only candidate scores for proposals that reached ``update`` only."""

        return MappingProxyType(
            {observation.candidate_id: observation.scalar for observation in self._observations}
        )

    @property
    def observation_count(self) -> int:
        return len(self._observations)

    @property
    def proposal_count(self) -> int:
        return self._proposal_count

    def _base_state_payload(self) -> dict[str, Any]:
        return {
            "policy_name": self.policy_name,
            "seed": self.seed,
            "grammar_contract_sha256": self.grammar.contract_sha256,
            "grammar_support_size": self.grammar.support_size,
            "proposal_count": self._proposal_count,
            "proposals": [
                {
                    "ordinal": ordinal,
                    "candidate_id": proposal.candidate_id,
                    "updated": ordinal in self._updated_ordinals,
                }
                for ordinal, proposal in sorted(self._pending.items())
            ],
            "updated_ordinals": sorted(self._updated_ordinals),
            "observations": [
                {
                    "candidate_id": observation.candidate_id,
                    "rank_key": list(observation.rank_key),
                    "scalar": observation.scalar,
                }
                for observation in self._observations
            ],
            "rng_state_sha256": _rng_hash(self._rng),
        }

    def _specific_state_payload(self) -> Mapping[str, Any]:
        return {}

    def state_hash(self) -> str:
        payload = self._base_state_payload()
        payload["policy_state"] = dict(self._specific_state_payload())
        return hashlib.sha256(canonical_json_bytes(payload)).hexdigest().upper()


class CanonicalTypedRandomPolicy(SearchPolicy):
    """A full-cycle affine permutation over grammar indices, generated lazily."""

    policy_name = "canonical_typed_random"

    def __init__(self, grammar: FrozenGrammar, seed: int) -> None:
        super().__init__(grammar, seed)
        support = grammar.support_size
        self._offset = self._rng.randrange(support)
        stride = self._rng.randrange(1, support)
        while math.gcd(stride, support) != 1:
            stride = self._rng.randrange(1, support)
        self._stride = stride
        self._cursor = 0

    def propose(self, state: SearchState) -> Proposal:
        self._check_state(state)
        if self._cursor >= self.grammar.support_size:
            raise RuntimeError("typed-random permutation exhausted grammar support")
        index = (self._offset + self._cursor * self._stride) % self.grammar.support_size
        self._cursor += 1
        return self._proposal(self.grammar.decode(index))

    def _specific_state_payload(self) -> Mapping[str, Any]:
        return {"offset": self._offset, "stride": self._stride, "cursor": self._cursor}


class CEMLikePolicy(SearchPolicy):
    """Categorical structural sampler learned only from visited elite feedback."""

    policy_name = "cem_like"

    def _elite(self) -> tuple[_Observation, ...]:
        if len(self._observations) < CEM_MIN_OBSERVATIONS:
            return ()
        count = max(1, math.ceil(len(self._observations) * CEM_ELITE_FRACTION))
        ranked = sorted(
            self._observations,
            key=lambda row: (row.rank_key, row.candidate_id),
            reverse=True,
        )
        return tuple(ranked[:count])

    @staticmethod
    def _counts(elite: Iterable[_Observation], attribute: str) -> dict[Any, int]:
        counts: dict[Any, int] = {}
        for observation in elite:
            value = getattr(observation.genome, attribute)
            counts[value] = counts.get(value, 0) + 1
        return counts

    @staticmethod
    def _weights(values: Sequence[Any], counts: Mapping[Any, int]) -> list[float]:
        return [1.0 + CEM_ELITE_WEIGHT * counts.get(value, 0) for value in values]

    def propose(self, state: SearchState) -> Proposal:
        self._check_state(state)
        elite = self._elite()
        family_counts = self._counts(elite, "mechanism_family")
        mechanism = _weighted_choice(
            self._rng,
            MECHANISM_FAMILIES,
            self._weights(MECHANISM_FAMILIES, family_counts),
        )

        field_family_counts: dict[str, int] = {}
        for observation in elite:
            field_family = self.grammar.field_family_for(observation.genome.field_id)
            field_family_counts[field_family] = field_family_counts.get(field_family, 0) + 1
        field_counts = self._counts(elite, "field_id")
        representation_counts = self._counts(elite, "representation_id")
        field_representations = self.grammar.field_representations
        field_weights = [
            (
                1.0
                + CEM_ELITE_WEIGHT
                * field_family_counts.get(self.grammar.field_family_for(field_id), 0)
            )
            * (1.0 + CEM_ELITE_WEIGHT * field_counts.get(field_id, 0))
            * (
                1.0
                + CEM_ELITE_WEIGHT
                * representation_counts.get(representation_id, 0)
            )
            for field_id, representation_id in field_representations
        ]
        field_id, representation_id = _weighted_choice(
            self._rng, field_representations, field_weights
        )

        cells = self.grammar.cells_for_mechanism(mechanism)
        primitive_counts = self._counts(elite, "primitive_id")
        cell = _weighted_choice(
            self._rng,
            cells,
            self._weights(
                [item.primitive_id for item in cells], primitive_counts
            ),
        )
        window_counts = self._counts(elite, "window")
        long_window_counts = self._counts(elite, "long_window")
        threshold_counts = self._counts(elite, "threshold")
        parameter_weights = [
            (1.0 + CEM_ELITE_WEIGHT * window_counts.get(parameters[0], 0))
            * (1.0 + CEM_ELITE_WEIGHT * long_window_counts.get(parameters[1], 0))
            * (1.0 + CEM_ELITE_WEIGHT * threshold_counts.get(parameters[2], 0))
            for parameters in cell.parameter_options
        ]
        window, long_window, threshold = _weighted_choice(
            self._rng, cell.parameter_options, parameter_weights
        )
        horizons = self.grammar.target_horizons_hours
        horizon_counts = self._counts(elite, "target_horizon_hours")
        horizon = _weighted_choice(
            self._rng, horizons, self._weights(horizons, horizon_counts)
        )
        return self._proposal(
            CandidateGenome(
                field_id,
                representation_id,
                cell.primitive_id,
                window,
                long_window,
                threshold,
                mechanism,
                horizon,
            )
        )

    def _specific_state_payload(self) -> Mapping[str, Any]:
        elite = self._elite()
        return {
            "minimum_observations": CEM_MIN_OBSERVATIONS,
            "elite_fraction": CEM_ELITE_FRACTION,
            "elite_candidate_ids": [row.candidate_id for row in elite],
        }


def _choice_token(value: Any) -> str:
    if isinstance(value, GrammarCell):
        value = {"primitive_id": value.primitive_id}
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


class UCTUCBLikePolicy(SearchPolicy):
    """UCT over expandable structural decisions rather than candidate IDs."""

    policy_name = "uct_ucb_like"

    def __init__(self, grammar: FrozenGrammar, seed: int) -> None:
        super().__init__(grammar, seed)
        self._stats: dict[tuple[str, ...], tuple[int, float]] = {}
        self._pending_paths: dict[int, tuple[tuple[str, ...], ...]] = {}

    def _select(
        self,
        depth: str,
        prefix: tuple[str, ...],
        choices: Sequence[Any],
    ) -> tuple[Any, tuple[str, ...]]:
        keys = [(depth, *prefix, _choice_token(choice)) for choice in choices]
        unvisited = [
            index
            for index, key in enumerate(keys)
            if self._stats.get(key, (0, 0.0))[0] == 0
        ]
        if unvisited:
            selected_index = unvisited[self._rng.randrange(len(unvisited))]
        else:
            total = sum(self._stats[key][0] for key in keys)

            def ucb(index: int) -> tuple[float, str]:
                count, value = self._stats[keys[index]]
                mean = value / count
                exploration = UCT_EXPLORATION * math.sqrt(math.log(total + 1.0) / count)
                priority = hashlib.sha256(
                    f"{self.seed}|{keys[index]}".encode("utf-8")
                ).hexdigest()
                return mean + exploration, priority

            selected_index = max(range(len(choices)), key=ucb)
        return choices[selected_index], keys[selected_index]

    def propose(self, state: SearchState) -> Proposal:
        self._check_state(state)
        path: list[tuple[str, ...]] = []
        prefix: tuple[str, ...] = ()

        mechanism, key = self._select("mechanism", prefix, MECHANISM_FAMILIES)
        path.append(key)
        prefix += (_choice_token(mechanism),)

        field_family, key = self._select(
            "field_family", prefix, self.grammar.field_families
        )
        path.append(key)
        prefix += (_choice_token(field_family),)

        field_representation, key = self._select(
            "field_representation",
            prefix,
            self.grammar.field_representations_for_family(field_family),
        )
        path.append(key)
        prefix += (_choice_token(field_representation),)

        cells = self.grammar.cells_for_mechanism(mechanism)
        cell, key = self._select("primitive", prefix, cells)
        path.append(key)
        prefix += (_choice_token(cell),)

        parameters, key = self._select("parameters", prefix, cell.parameter_options)
        path.append(key)
        prefix += (_choice_token(parameters),)

        horizon, key = self._select(
            "target_horizon", prefix, self.grammar.target_horizons_hours
        )
        path.append(key)

        field_id, representation_id = field_representation
        window, long_window, threshold = parameters
        proposal = self._proposal(
            CandidateGenome(
                field_id,
                representation_id,
                cell.primitive_id,
                window,
                long_window,
                threshold,
                mechanism,
                horizon,
            )
        )
        self._pending_paths[proposal.ordinal] = tuple(path)
        return proposal

    def _after_update(self, proposal: Proposal, observation: _Observation) -> None:
        path = self._pending_paths.pop(proposal.ordinal, None)
        if path is None:
            raise ValueError("UCT feedback has no recorded structural path")
        for key in path:
            count, value = self._stats.get(key, (0, 0.0))
            self._stats[key] = (count + 1, value + observation.scalar)

    def _specific_state_payload(self) -> Mapping[str, Any]:
        return {
            "tree_statistics": [
                {"path": list(key), "count": count, "value_sum": value}
                for key, (count, value) in sorted(self._stats.items())
            ],
            "pending_paths": [
                {
                    "ordinal": ordinal,
                    "path": [list(key) for key in path],
                }
                for ordinal, path in sorted(self._pending_paths.items())
            ],
        }


class EvolutionaryPolicy(SearchPolicy):
    """Visited-parent selection followed by a real grammar mutation."""

    policy_name = "evolutionary"

    def __init__(self, grammar: FrozenGrammar, seed: int) -> None:
        super().__init__(grammar, seed)
        self._mutation_history: list[dict[str, Any]] = []

    def propose(self, state: SearchState) -> Proposal:
        self._check_state(state)
        if len(self._observations) < EVOLUTION_BOOTSTRAP_VISITS:
            return self._proposal(self.grammar.sample(self._rng))
        ranked = sorted(
            self._observations,
            key=lambda row: (row.rank_key, row.candidate_id),
            reverse=True,
        )
        parent_count = max(1, math.ceil(len(ranked) * EVOLUTION_PARENT_FRACTION))
        parents = ranked[:parent_count]
        parent = parents[self._rng.randrange(len(parents))]
        child, receipt = self.grammar.mutate(parent.genome, self._rng)
        proposal = self._proposal(
            child,
            parent_id=parent.candidate_id,
            mutation_receipt=receipt,
        )
        self._mutation_history.append(receipt.to_dict())
        return proposal

    def _specific_state_payload(self) -> Mapping[str, Any]:
        return {
            "bootstrap_visits": EVOLUTION_BOOTSTRAP_VISITS,
            "parent_fraction": EVOLUTION_PARENT_FRACTION,
            "mutation_receipts": list(self._mutation_history),
        }


def build_policy(name: str, grammar: FrozenGrammar, seed: int) -> SearchPolicy:
    factories = {
        "canonical_typed_random": CanonicalTypedRandomPolicy,
        "cem_like": CEMLikePolicy,
        "uct_ucb_like": UCTUCBLikePolicy,
        "evolutionary": EvolutionaryPolicy,
    }
    try:
        factory = factories[str(name)]
    except KeyError as error:
        raise ValueError(f"unknown canary policy: {name}") from error
    return factory(grammar, seed)


__all__ = [
    "CEMLikePolicy",
    "CanonicalTypedRandomPolicy",
    "EvolutionaryPolicy",
    "SUPPORTED_POLICIES",
    "SearchPolicy",
    "UCTUCBLikePolicy",
    "build_policy",
]
