"""Experimental diversity-preserving CEM policy for the bounded canary A/B.

The baseline :mod:`policies` module is intentionally untouched.  This policy
inherits its proposal-local feedback contract from ``CEMLikePolicy`` and adds
only two pre-registered behaviours: a fixed uniform exploration mixture and a
bounded, policy-local duplicate resample.
"""

from __future__ import annotations

from types import MappingProxyType
from typing import Any, Mapping

from .contracts import CandidateGenome, Proposal, SearchState
from .grammar import FrozenGrammar, MECHANISM_FAMILIES
from .policies import CEM_ELITE_WEIGHT, CEMLikePolicy, _weighted_choice


EXPLORATION_PROBABILITY = 0.20
MAX_DUPLICATE_RESAMPLES = 16


class CEMDiversityV2Policy(CEMLikePolicy):
    """Visited-elite CEM with fixed exploration and bounded local deduping."""

    policy_name = "cem_diversity_v2"

    def __init__(self, grammar: FrozenGrammar, seed: int) -> None:
        super().__init__(grammar, seed)
        self._seen_candidate_ids: set[str] = set()
        self._proposal_diagnostics: list[dict[str, Any]] = []

    def _sample_exploration_genome(self) -> CandidateGenome:
        """Draw uniformly from the frozen structural support without traversal."""

        return self.grammar.decode(self._rng.randrange(self.grammar.support_size))

    def _sample_exploitation_genome(self) -> CandidateGenome:
        """Sample the unchanged baseline visited-elite categorical CEM model."""

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
            self._weights([item.primitive_id for item in cells], primitive_counts),
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
        return CandidateGenome(
            field_id,
            representation_id,
            cell.primitive_id,
            window,
            long_window,
            threshold,
            mechanism,
            horizon,
        )

    def propose(self, state: SearchState) -> Proposal:
        self._check_state(state)

        # The mixture branch is drawn exactly once per proposal.  Duplicate
        # resamples remain in that branch and therefore cannot change the
        # pre-registered 80/20 decision after seeing a duplicate identity.
        exploration_draw = self._rng.random()
        exploration = exploration_draw < EXPLORATION_PROBABILITY
        sampler = (
            self._sample_exploration_genome
            if exploration
            else self._sample_exploitation_genome
        )
        genome = sampler()
        duplicate_resample_attempts = 0
        while (
            genome.candidate_id in self._seen_candidate_ids
            and duplicate_resample_attempts < MAX_DUPLICATE_RESAMPLES
        ):
            duplicate_resample_attempts += 1
            genome = sampler()

        duplicate_resample_exhausted = genome.candidate_id in self._seen_candidate_ids
        proposal = self._proposal(genome)
        self._seen_candidate_ids.add(proposal.candidate_id)
        self._proposal_diagnostics.append(
            {
                "ordinal": proposal.ordinal,
                "candidate_id": proposal.candidate_id,
                "branch": "uniform_exploration" if exploration else "cem_exploitation",
                "exploration_draw": exploration_draw,
                "exploration_selected": exploration,
                "duplicate_resample_attempts": duplicate_resample_attempts,
                "duplicate_resample_exhausted": duplicate_resample_exhausted,
                "seen_candidate_count": len(self._seen_candidate_ids),
            }
        )
        return proposal

    @property
    def proposal_diagnostics(self) -> tuple[Mapping[str, Any], ...]:
        """Return immutable copies of per-proposal branch and dedupe receipts."""

        return tuple(MappingProxyType(dict(row)) for row in self._proposal_diagnostics)

    @property
    def seen_candidate_ids(self) -> frozenset[str]:
        """Expose this policy's own proposal identities, never engine cache state."""

        return frozenset(self._seen_candidate_ids)

    def _specific_state_payload(self) -> Mapping[str, Any]:
        baseline_state = dict(super()._specific_state_payload())
        baseline_state.update(
            {
                "exploration_probability": EXPLORATION_PROBABILITY,
                "maximum_duplicate_resamples": MAX_DUPLICATE_RESAMPLES,
                "seen_candidate_ids": sorted(self._seen_candidate_ids),
                "proposal_diagnostics": [
                    dict(row) for row in self._proposal_diagnostics
                ],
            }
        )
        return baseline_state


def cem_diversity_v2(grammar: FrozenGrammar, seed: int) -> CEMDiversityV2Policy:
    """Construct the independently registered experimental challenger policy."""

    return CEMDiversityV2Policy(grammar, seed)


__all__ = [
    "CEMDiversityV2Policy",
    "EXPLORATION_PROBABILITY",
    "MAX_DUPLICATE_RESAMPLES",
    "cem_diversity_v2",
]
