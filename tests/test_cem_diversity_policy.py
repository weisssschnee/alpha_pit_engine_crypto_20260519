from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import patch

import pytest

from alphafactory_crypto.instrument_canary.cem_diversity import (
    CEMDiversityV2Policy,
    EXPLORATION_PROBABILITY,
    MAX_DUPLICATE_RESAMPLES,
    cem_diversity_v2,
)
from alphafactory_crypto.instrument_canary.contracts import SearchState
from alphafactory_crypto.instrument_canary.grammar import FrozenGrammar
from alphafactory_crypto.instrument_canary.policies import CEMLikePolicy


REPO_ROOT = Path(__file__).resolve().parents[1]
FROZEN_BASELINE_POLICIES_SHA256 = (
    "3FAAC73945755E0BCFDA02A2855510F24FCD2EE6C5DA87CCEE3F9ED8D6A55C78"
)


@dataclass(frozen=True)
class Feedback:
    candidate_id: str
    sort_key: tuple[float, ...]
    distance: float
    blocked: bool = False
    feasible: bool = False


def _feedback(candidate_id: str, score: float) -> Feedback:
    return Feedback(candidate_id, (score,), score)


def _transcript(seed: int, scores: list[float]) -> tuple[list[str], tuple[dict, ...], str]:
    policy = CEMDiversityV2Policy(FrozenGrammar.default(), seed)
    candidate_ids: list[str] = []
    for step, score in enumerate(scores):
        proposal = policy.propose(SearchState(step, len(scores) - step))
        candidate_ids.append(proposal.candidate_id)
        policy.update(proposal, _feedback(proposal.candidate_id, score))
    diagnostics = tuple(dict(row) for row in policy.proposal_diagnostics)
    return candidate_ids, diagnostics, policy.state_hash()


def test_same_seed_and_feedback_are_fully_deterministic() -> None:
    scores = [float(value) for value in range(24)]
    first = _transcript(20260715, scores)
    second = _transcript(20260715, scores)

    assert first == second
    assert len(first[0]) == 24
    assert all(row["duplicate_resample_attempts"] <= 16 for row in first[1])


def test_feedback_changes_post_warmup_transcript_and_state() -> None:
    real_scores = [float(value) for value in range(16)]
    neutral_scores = [0.0] * 16

    real = _transcript(20260715, real_scores)
    neutral = _transcript(20260715, neutral_scores)

    assert real[0][:8] == neutral[0][:8]
    assert real[0][8:] != neutral[0][8:]
    assert real[2] != neutral[2]


def test_duplicate_resample_is_bounded_and_fail_safe() -> None:
    policy = CEMDiversityV2Policy(FrozenGrammar.default(), 7)
    first = policy.propose(SearchState(0, 2))
    policy.update(first, _feedback(first.candidate_id, 0.0))

    with (
        patch.object(policy, "_sample_exploration_genome", return_value=first.genome),
        patch.object(policy, "_sample_exploitation_genome", return_value=first.genome),
    ):
        repeated = policy.propose(SearchState(1, 1))

    diagnostic = dict(policy.proposal_diagnostics[-1])
    assert repeated.candidate_id == first.candidate_id
    assert diagnostic["duplicate_resample_attempts"] == MAX_DUPLICATE_RESAMPLES
    assert diagnostic["duplicate_resample_exhausted"] is True
    assert policy.proposal_count == 2


def test_local_seen_ids_drive_successful_deterministic_resample() -> None:
    policy = CEMDiversityV2Policy(FrozenGrammar.default(), 11)
    first = policy.propose(SearchState(0, 2))
    policy.update(first, _feedback(first.candidate_id, 0.0))
    alternative = policy.grammar.decode(
        (policy.grammar.encode(first.genome) + 1) % policy.grammar.support_size
    )
    draws = iter((first.genome, alternative))

    with (
        patch.object(policy._rng, "random", return_value=0.0),
        patch.object(policy, "_sample_exploration_genome", side_effect=lambda: next(draws)),
    ):
        second = policy.propose(SearchState(1, 1))

    diagnostic = dict(policy.proposal_diagnostics[-1])
    assert second.genome == alternative
    assert diagnostic["branch"] == "uniform_exploration"
    assert diagnostic["duplicate_resample_attempts"] == 1
    assert diagnostic["duplicate_resample_exhausted"] is False


def test_mixture_branch_is_drawn_once_per_proposal() -> None:
    policy = CEMDiversityV2Policy(FrozenGrammar.default(), 12)
    genome = policy.grammar.decode(0)

    with (
        patch.object(policy._rng, "random", return_value=0.19) as mixture_draw,
        patch.object(policy, "_sample_exploration_genome", return_value=genome),
    ):
        proposal = policy.propose(SearchState(0, 1))

    diagnostic = dict(policy.proposal_diagnostics[-1])
    assert proposal.genome == genome
    assert mixture_draw.call_count == 1
    assert diagnostic["exploration_draw"] == 0.19
    assert diagnostic["exploration_selected"] is True
    assert diagnostic["branch"] == "uniform_exploration"


def test_policy_surface_has_no_global_cache_or_candidate_universe() -> None:
    policy = cem_diversity_v2(FrozenGrammar.default(), 13)

    assert isinstance(policy, CEMLikePolicy)
    assert policy.policy_name == "cem_diversity_v2"
    assert EXPLORATION_PROBABILITY == 0.20
    for forbidden in ("global_cache", "engine_cache", "candidate_universe", "feedback_map"):
        assert not hasattr(policy, forbidden)
    with pytest.raises(TypeError):
        policy.propose(object())  # type: ignore[arg-type]


def test_frozen_baseline_policy_module_is_byte_identical() -> None:
    policies_path = REPO_ROOT / "alphafactory_crypto" / "instrument_canary" / "policies.py"

    assert hashlib.sha256(policies_path.read_bytes()).hexdigest().upper() == (
        FROZEN_BASELINE_POLICIES_SHA256
    )


def test_state_hash_binds_seen_ids_configuration_and_diagnostics() -> None:
    policy = CEMDiversityV2Policy(FrozenGrammar.default(), 17)
    before = policy.state_hash()
    proposal = policy.propose(SearchState(0, 1))
    after_proposal = policy.state_hash()
    policy.update(proposal, _feedback(proposal.candidate_id, 1.0))
    after_feedback = policy.state_hash()

    state = policy._specific_state_payload()
    assert before != after_proposal != after_feedback
    assert state["exploration_probability"] == 0.20
    assert state["maximum_duplicate_resamples"] == 16
    assert state["seen_candidate_ids"] == [proposal.candidate_id]
    assert state["proposal_diagnostics"][0]["candidate_id"] == proposal.candidate_id
