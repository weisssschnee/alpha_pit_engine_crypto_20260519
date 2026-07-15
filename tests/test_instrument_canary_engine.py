from __future__ import annotations

import unittest
from dataclasses import dataclass

from alphafactory_crypto.instrument_canary.contracts import Proposal
from alphafactory_crypto.instrument_canary.engine import (
    CandidateObservation,
    LazySearchEngine,
    replay_policy_transcript,
)
from alphafactory_crypto.instrument_canary.grammar import FrozenGrammar


@dataclass(frozen=True)
class DummyReceipt:
    candidate_id: str
    cache_key: str

    def to_dict(self):
        return {"candidate_id": self.candidate_id, "cache_key": self.cache_key}


@dataclass(frozen=True)
class DummyFeedback:
    blocked: bool
    feasible: bool
    violations: tuple[str, ...]
    distance: float
    sort_key: tuple[float, ...]
    reason: str


def feedback_for(candidate_id: str) -> DummyFeedback:
    value = (int(candidate_id[-6:], 16) % 101 - 50) / 10.0
    return DummyFeedback(
        blocked=False,
        feasible=value >= 0.0,
        violations=() if value >= 0.0 else ("TEST",),
        distance=value,
        sort_key=(1.0, float(value >= 0.0), value),
        reason="PASS" if value >= 0.0 else "FAIL",
    )


class InstrumentCanaryEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.grammar = FrozenGrammar()

    def _authorizer(self, proposal: Proposal) -> DummyReceipt:
        return DummyReceipt(proposal.candidate_id, "cache:" + proposal.candidate_id)

    def test_only_visited_proposals_are_authorized_evaluated_and_updated(self) -> None:
        evaluated: list[str] = []

        def evaluate(receipt: DummyReceipt) -> CandidateObservation:
            evaluated.append(receipt.candidate_id)
            return CandidateObservation(
                feedback_for(receipt.candidate_id),
                {"materialized": True, "evaluated": True},
            )

        result = LazySearchEngine(
            self.grammar,
            authorizer=self._authorizer,
            first_visit_evaluator=evaluate,
            first_evaluation_hard_cap=8,
        ).run(
            algorithms=["canonical_typed_random"],
            seeds=[20260715],
            steps_per_lane=4,
        )
        self.assertEqual(result.proposals, 4)
        self.assertEqual(len(result.ledger), 4)
        self.assertEqual(len(evaluated), result.first_evaluations)
        self.assertEqual(len(result.authorization_receipts), result.cache_size)
        self.assertTrue(all(row["feedback_exposed"] for row in result.ledger))
        self.assertLess(result.proposals, self.grammar.support_size)

    def test_global_cache_prevents_duplicate_first_evaluation_but_not_feedback(self) -> None:
        evaluated: list[str] = []

        class RepeatingPolicy:
            def __init__(self, name, grammar, seed):
                self.policy_name = name
                self.genome = grammar.decode(0)
                self.seed = seed
                self.count = 0
                self.updated = 0

            def state_hash(self):
                return f"{self.policy_name}:{self.seed}:{self.count}:{self.updated}"

            def propose(self, state):
                proposal = Proposal(self.policy_name, self.count, self.genome)
                self.count += 1
                return proposal

            def update(self, proposal, feedback):
                self.updated += 1

        def evaluate(receipt: DummyReceipt) -> CandidateObservation:
            evaluated.append(receipt.candidate_id)
            return CandidateObservation(feedback_for(receipt.candidate_id), {})

        result = LazySearchEngine(
            self.grammar,
            authorizer=self._authorizer,
            first_visit_evaluator=evaluate,
            first_evaluation_hard_cap=16,
            policy_factory=RepeatingPolicy,
        ).run(algorithms=["a", "b"], seeds=[2, 1], steps_per_lane=2)

        self.assertEqual(result.proposals, 8)
        self.assertEqual(result.first_evaluations, 1)
        self.assertEqual(result.cache_hits, 7)
        self.assertEqual(len(evaluated), 1)
        self.assertEqual(sum(row["feedback_exposed"] for row in result.ledger), 8)
        self.assertEqual(
            [row["lane_id"] for row in result.ledger],
            [
                "a:seed=1",
                "a:seed=1",
                "b:seed=1",
                "b:seed=1",
                "a:seed=2",
                "a:seed=2",
                "b:seed=2",
                "b:seed=2",
            ],
        )

    def test_event_order_is_proposal_authorization_cache_evaluation_feedback_update(self) -> None:
        result = LazySearchEngine(
            self.grammar,
            authorizer=self._authorizer,
            first_visit_evaluator=lambda receipt: CandidateObservation(
                feedback_for(receipt.candidate_id), {}
            ),
            first_evaluation_hard_cap=2,
        ).run(
            algorithms=["canonical_typed_random"], seeds=[1], steps_per_lane=1
        )
        row = result.ledger[0]
        self.assertLess(row["proposal_sequence"], row["authorization_started_sequence"])
        self.assertLess(row["authorization_started_sequence"], row["authorized_sequence"])
        self.assertLess(row["authorized_sequence"], row["cache_lookup_sequence"])
        self.assertLess(row["cache_lookup_sequence"], row["evaluation_sequence"])
        self.assertLess(row["evaluation_sequence"], row["feedback_sequence"])
        self.assertLess(row["feedback_sequence"], row["policy_update_sequence"])

    def test_hard_cap_counts_preflight_and_fails_before_extra_evaluation(self) -> None:
        evaluated: list[str] = []

        def evaluate(receipt):
            evaluated.append(receipt.candidate_id)
            return CandidateObservation(feedback_for(receipt.candidate_id), {})

        engine = LazySearchEngine(
            self.grammar,
            authorizer=self._authorizer,
            first_visit_evaluator=evaluate,
            first_evaluation_hard_cap=2,
            already_consumed_first_evaluations=1,
        )
        with self.assertRaisesRegex(RuntimeError, "hard cap"):
            engine.run(
                algorithms=["canonical_typed_random"],
                seeds=[1],
                steps_per_lane=2,
            )
        self.assertEqual(len(evaluated), 1)

    def test_real_policy_transcript_replays_without_market_evaluation(self) -> None:
        result = LazySearchEngine(
            self.grammar,
            authorizer=self._authorizer,
            first_visit_evaluator=lambda receipt: CandidateObservation(
                feedback_for(receipt.candidate_id), {}
            ),
            first_evaluation_hard_cap=16,
        ).run(algorithms=["cem_like"], seeds=[20260715], steps_per_lane=12)
        replay = replay_policy_transcript(
            self.grammar,
            algorithm="cem_like",
            seed=20260715,
            ledger_rows=result.ledger,
        )
        self.assertEqual(replay["result"], "PASS")
        self.assertEqual(
            replay["final_policy_state_sha256"],
            result.lane_state_hashes["cem_like:seed=20260715"],
        )

    def test_receipt_identity_mismatch_fails_before_evaluation(self) -> None:
        called = False

        def evaluate(receipt):
            nonlocal called
            called = True
            return CandidateObservation(feedback_for(receipt.candidate_id), {})

        engine = LazySearchEngine(
            self.grammar,
            authorizer=lambda proposal: DummyReceipt("wrong", "cache:wrong"),
            first_visit_evaluator=evaluate,
            first_evaluation_hard_cap=1,
        )
        with self.assertRaisesRegex(ValueError, "identity mismatch"):
            engine.run(
                algorithms=["canonical_typed_random"], seeds=[1], steps_per_lane=1
            )
        self.assertFalse(called)

    def test_engine_is_single_use_so_hard_cap_cannot_reset_between_runs(self) -> None:
        engine = LazySearchEngine(
            self.grammar,
            authorizer=self._authorizer,
            first_visit_evaluator=lambda receipt: CandidateObservation(
                feedback_for(receipt.candidate_id), {}
            ),
            first_evaluation_hard_cap=2,
        )
        engine.run(
            algorithms=["canonical_typed_random"], seeds=[1], steps_per_lane=1
        )
        with self.assertRaisesRegex(RuntimeError, "single-use"):
            engine.run(
                algorithms=["canonical_typed_random"], seeds=[2], steps_per_lane=1
            )

    def test_evidence_cannot_overwrite_authoritative_ledger_columns(self) -> None:
        engine = LazySearchEngine(
            self.grammar,
            authorizer=self._authorizer,
            first_visit_evaluator=lambda receipt: CandidateObservation(
                feedback_for(receipt.candidate_id),
                {"candidate_id": "FORGED", "first_evaluation": False},
            ),
            first_evaluation_hard_cap=1,
        )
        with self.assertRaisesRegex(ValueError, "overwrite ledger authority"):
            engine.run(
                algorithms=["canonical_typed_random"], seeds=[1], steps_per_lane=1
            )


if __name__ == "__main__":
    unittest.main()
