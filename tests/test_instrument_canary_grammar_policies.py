from __future__ import annotations

import hashlib
import json
import random
import unittest
from dataclasses import dataclass, replace

from alphafactory_crypto.instrument_canary import (
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
    SUPPORTED_POLICIES,
    WINDOWLESS_PRIMITIVES,
    CandidateGenome,
    FrozenGrammar,
    GrammarFilter,
    Proposal,
    SearchState,
    build_policy,
)


@dataclass(frozen=True)
class DummyFeedback:
    candidate_id: str
    blocked: bool
    feasible: bool
    distance: float
    sort_key: tuple[float, ...]


def deterministic_feedback(candidate_id: str) -> DummyFeedback:
    value = (int(candidate_id[-8:], 16) % 2001 - 1000) / 100.0
    feasible = value >= 0.0
    return DummyFeedback(
        candidate_id, False, feasible, value, (1.0, float(feasible), value)
    )


class CandidateGenomeTests(unittest.TestCase):
    def test_canonical_identity_contains_only_structural_genes(self) -> None:
        grammar = FrozenGrammar()
        genome = grammar.decode(17)
        payload = genome.canonical_dict()
        self.assertEqual(
            set(payload),
            {
                "schema_version",
                "field_id",
                "representation_id",
                "primitive_id",
                "window",
                "long_window",
                "threshold",
                "mechanism_family",
                "target_horizon_hours",
            },
        )
        self.assertNotIn("label", json.dumps(payload, sort_keys=True).lower())
        self.assertEqual(genome.candidate_id, genome.identity)
        self.assertEqual(genome.candidate_id, grammar.decode(17).candidate_id)
        other_horizon = 4 if genome.target_horizon_hours == 1 else 1
        self.assertNotEqual(
            genome.candidate_id,
            replace(genome, target_horizon_hours=other_horizon).candidate_id,
        )

    def test_invalid_numeric_parameters_fail_closed(self) -> None:
        base = FrozenGrammar().decode(0)
        with self.assertRaisesRegex(ValueError, "window"):
            replace(base, window=0)
        with self.assertRaisesRegex(ValueError, "target_horizon"):
            replace(base, target_horizon_hours=0)
        with self.assertRaisesRegex(ValueError, "finite"):
            replace(base, threshold=float("nan"))

    def test_proposal_validates_complete_mutation_receipt_binding(self) -> None:
        grammar = FrozenGrammar()
        parent = grammar.decode(0)
        child, receipt = grammar.mutate(parent, random.Random(7))
        valid = Proposal(
            "evolutionary",
            1,
            child,
            parent_id=parent.candidate_id,
            mutation_receipt=receipt,
        )
        self.assertEqual(valid.candidate_id, receipt.child_id)
        with self.assertRaisesRegex(ValueError, "cannot declare a parent"):
            Proposal("evolutionary", 1, child, parent_id=parent.candidate_id)
        with self.assertRaisesRegex(ValueError, "parent identity"):
            Proposal(
                "evolutionary",
                1,
                child,
                parent_id="wrong-parent",
                mutation_receipt=receipt,
            )
        with self.assertRaisesRegex(ValueError, "child identity"):
            Proposal(
                "evolutionary",
                1,
                child,
                parent_id=parent.candidate_id,
                mutation_receipt=replace(receipt, child_id="wrong-child"),
            )
        with self.assertRaisesRegex(ValueError, "child genome"):
            Proposal(
                "evolutionary",
                1,
                child,
                parent_id=parent.candidate_id,
                mutation_receipt=replace(
                    receipt, child_genome=parent.canonical_dict()
                ),
            )
        with self.assertRaisesRegex(ValueError, "changed genes"):
            Proposal(
                "evolutionary",
                1,
                child,
                parent_id=parent.candidate_id,
                mutation_receipt=replace(receipt, changed_genes=()),
            )


class FrozenGrammarTests(unittest.TestCase):
    def setUp(self) -> None:
        self.grammar = FrozenGrammar()

    def test_release_field_and_representation_contract_is_exact(self) -> None:
        expected_fields = {
            "trade_count",
            "underlying_trade_count",
            "quantity",
            "notional",
            "buy_agg_trade_count",
            "sell_agg_trade_count",
            "buy_quantity",
            "sell_quantity",
            "buy_notional",
            "sell_notional",
            "signed_aggressor_quantity",
            "signed_aggressor_notional",
            "vwap",
            "buy_vwap",
            "sell_vwap",
            "volume_imbalance",
            "buy_sell_notional_ratio",
            "price_range_bps",
            "close_to_open_bps",
            "large_trade_count_ratio_100k_plus",
            "large_notional_ratio_100k_plus",
        }
        self.assertEqual(len(FROZEN_RELEASE_FIELDS), 21)
        self.assertEqual(set(FROZEN_RELEASE_FIELDS), expected_fields)
        self.assertEqual(tuple(spec.field_id for spec in FROZEN_FIELD_SPECS), FROZEN_RELEASE_FIELDS)
        for spec in FROZEN_FIELD_SPECS:
            with self.subTest(field_id=spec.field_id):
                self.assertTrue(spec.field_family)
                self.assertEqual(len(spec.representations), 2)
                identity, nonlinear = spec.representations
                self.assertEqual(identity.representation_id, "identity")
                self.assertFalse(identity.nonlinear)
                self.assertTrue(nonlinear.nonlinear)
                self.assertNotEqual(identity.formula, nonlinear.formula)
                self.assertEqual(identity.input_domain, spec.value_domain)
                self.assertEqual(nonlinear.input_domain, spec.value_domain)

    def test_support_size_is_exact_large_and_not_materialized(self) -> None:
        expected = sum(
            len(self.grammar.field_representations)
            * len(cell.parameter_options)
            * len(self.grammar.target_horizons_hours)
            for cell in self.grammar.cells
        )
        self.assertEqual(self.grammar.support_size, expected)
        self.assertGreaterEqual(self.grammar.support_size, MINIMUM_SUPPORT_SIZE)
        self.assertFalse(hasattr(self.grammar, "candidates"))
        self.assertFalse(hasattr(self.grammar, "all_candidates"))
        self.assertLess(len(self.grammar.cells), 64)

    def test_mixed_radix_encode_decode_is_bijective_without_a_candidate_list(self) -> None:
        observed_ids: set[str] = set()
        for index in range(self.grammar.support_size):
            genome = self.grammar.decode(index)
            self.assertEqual(self.grammar.encode(genome), index)
            observed_ids.add(genome.candidate_id)
        self.assertEqual(len(observed_ids), self.grammar.support_size)

    def test_filter_count_and_generation_are_lazy_and_exact(self) -> None:
        grammar_filter = GrammarFilter(
            field_ids=frozenset({"trade_count"}),
            primitive_ids=frozenset({"Delta"}),
            mechanism_families=frozenset({CROSS_SECTIONAL_RELATIVE}),
            target_horizons_hours=frozenset({1}),
        )
        expected = 2 * len(self.grammar.parameter_options("Delta"))
        self.assertEqual(self.grammar.filtered_support_size(grammar_filter), expected)
        stream = self.grammar.iter_filtered(grammar_filter)
        self.assertNotIsInstance(stream, (list, tuple))
        rows = list(stream)
        self.assertEqual(len(rows), expected)
        for row in rows:
            self.assertEqual(row.field_id, "trade_count")
            self.assertEqual(row.primitive_id, "Delta")
            self.assertEqual(row.mechanism_family, CROSS_SECTIONAL_RELATIVE)
            self.assertEqual(row.target_horizon_hours, 1)

    def test_windowless_and_multiscale_routes_have_no_parameter_aliases(self) -> None:
        for primitive_id in WINDOWLESS_PRIMITIVES:
            with self.subTest(primitive_id=primitive_id):
                options = self.grammar.parameter_options(primitive_id)
                self.assertEqual(options, ((None, None, 0.0),))
        for short, long, threshold in self.grammar.parameter_options("MultiScaleRelation"):
            self.assertIsNotNone(short)
            self.assertIsNotNone(long)
            self.assertLess(short, long)
            self.assertIsNone(threshold)

    def test_sparse_family_has_only_event_or_state_primitives_and_fixed_mapping(self) -> None:
        sparse_ids = {
            cell.primitive_id
            for cell in self.grammar.cells_for_mechanism(SPARSE_EVENT_CARRY)
        }
        self.assertEqual(sparse_ids, set(SPARSE_PRIMITIVES))
        self.assertLess(sparse_ids, set(CANONICAL_PRIMITIVE_IDS))
        for family in MECHANISM_FAMILIES:
            genome = self.grammar.decode_filtered(
                0, GrammarFilter(mechanism_families=frozenset({family}))
            )
            self.assertEqual(self.grammar.mapping_for(genome), MECHANISM_MAPPING[family])

        directional = self.grammar.decode_filtered(
            0,
            GrammarFilter(
                primitive_ids=frozenset({"Delta"}),
                mechanism_families=frozenset({DIRECTIONAL_STATEFUL}),
            ),
        )
        illegal = replace(directional, mechanism_family=SPARSE_EVENT_CARRY)
        self.assertFalse(self.grammar.is_legal(illegal))
        with self.assertRaisesRegex(ValueError, "event/state"):
            self.grammar.encode(illegal)

    def test_mutation_generates_a_legal_child_and_exact_receipt(self) -> None:
        rng = random.Random(20260715)
        parent = self.grammar.decode(1234)
        operators: set[str] = set()
        for _ in range(128):
            child, receipt = self.grammar.mutate(parent, rng)
            operators.add(receipt.operator)
            self.assertTrue(self.grammar.is_legal(child))
            self.assertNotEqual(child.candidate_id, parent.candidate_id)
            self.assertEqual(receipt.parent_id, parent.candidate_id)
            self.assertEqual(receipt.child_id, child.candidate_id)
            self.assertEqual(receipt.parent_genome, parent.canonical_dict())
            self.assertEqual(receipt.child_genome, child.canonical_dict())
            expected_changed = tuple(
                key
                for key in parent.canonical_dict()
                if key != "schema_version"
                and parent.canonical_dict()[key] != child.canonical_dict()[key]
            )
            self.assertEqual(receipt.changed_genes, expected_changed)
            parent = child
        self.assertGreaterEqual(len(operators), 3)


class GenerativePolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.grammar = FrozenGrammar()

    def _exercise(self, name: str, seed: int, count: int = 32):
        policy = build_policy(name, self.grammar, seed)
        proposals = []
        for step in range(count):
            proposal = policy.propose(SearchState(step, count - step))
            proposals.append(proposal)
            policy.update(proposal, deterministic_feedback(proposal.candidate_id))
        return policy, proposals

    def test_propose_has_no_feedback_until_update(self) -> None:
        for name in SUPPORTED_POLICIES:
            with self.subTest(name=name):
                policy = build_policy(name, self.grammar, 123)
                before = policy.state_hash()
                proposal = policy.propose(SearchState(0, 4))
                self.assertEqual(policy.observation_count, 0)
                self.assertEqual(dict(policy.visited_feedback), {})
                self.assertNotEqual(policy.state_hash(), before)
                with self.assertRaisesRegex(RuntimeError, "single-flight"):
                    policy.propose(SearchState(1, 3))
                policy.update(proposal, deterministic_feedback(proposal.candidate_id))
                self.assertEqual(policy.observation_count, 1)
                self.assertEqual(set(policy.visited_feedback), {proposal.candidate_id})

    def test_search_state_step_must_match_next_policy_ordinal(self) -> None:
        policy = build_policy("canonical_typed_random", self.grammar, 123)
        with self.assertRaisesRegex(ValueError, "next proposal ordinal"):
            policy.propose(SearchState(1, 4))
        proposal = policy.propose(SearchState(0, 4))
        policy.update(proposal, deterministic_feedback(proposal.candidate_id))
        with self.assertRaisesRegex(ValueError, "next proposal ordinal"):
            policy.propose(SearchState(0, 3))

    def test_policy_state_hash_binds_grammar_contract_and_support(self) -> None:
        default_policy = build_policy("cem_like", self.grammar, 123)
        alternate_grammar = FrozenGrammar(target_horizons_hours=(1, 4, 8))
        alternate_policy = build_policy("cem_like", alternate_grammar, 123)
        self.assertNotEqual(self.grammar.contract_sha256, alternate_grammar.contract_sha256)
        self.assertNotEqual(self.grammar.support_size, alternate_grammar.support_size)
        self.assertNotEqual(default_policy.state_hash(), alternate_policy.state_hash())

    def test_policy_rejects_feedback_for_unproposed_or_foreign_proposal(self) -> None:
        left = build_policy("cem_like", self.grammar, 1)
        right = build_policy("uct_ucb_like", self.grammar, 1)
        proposal = left.propose(SearchState(0, 2))
        with self.assertRaisesRegex(ValueError, "different policy"):
            right.update(proposal, deterministic_feedback(proposal.candidate_id))
        wrong_feedback = replace(
            deterministic_feedback(proposal.candidate_id), candidate_id="wrong-candidate"
        )
        with self.assertRaisesRegex(ValueError, "candidate identity mismatch"):
            left.update(proposal, wrong_feedback)
        left.update(proposal, deterministic_feedback(proposal.candidate_id))
        with self.assertRaisesRegex(ValueError, "already consumed"):
            left.update(proposal, deterministic_feedback(proposal.candidate_id))

    def test_typed_random_generates_unique_structural_indices_without_replacement(self) -> None:
        policy, proposals = self._exercise("canonical_typed_random", 20260715, 256)
        self.assertEqual(len({proposal.candidate_id for proposal in proposals}), 256)
        self.assertEqual(policy.observation_count, 256)
        self.assertLess(256, self.grammar.support_size)

    def test_all_policies_are_fixed_seed_reproducible_and_behavior_distinct(self) -> None:
        behavior_hashes: dict[str, str] = {}
        for name in SUPPORTED_POLICIES:
            with self.subTest(name=name):
                first, first_proposals = self._exercise(name, 20260715, 48)
                second, second_proposals = self._exercise(name, 20260715, 48)
                first_ids = [proposal.candidate_id for proposal in first_proposals]
                second_ids = [proposal.candidate_id for proposal in second_proposals]
                self.assertEqual(first_ids, second_ids)
                self.assertEqual(first.state_hash(), second.state_hash())
                behavior_hashes[name] = hashlib.sha256(
                    "\n".join(first_ids).encode("utf-8")
                ).hexdigest()
        self.assertEqual(len(set(behavior_hashes.values())), len(SUPPORTED_POLICIES))

    def test_different_seeds_reach_different_regions(self) -> None:
        for name in SUPPORTED_POLICIES:
            with self.subTest(name=name):
                _, first = self._exercise(name, 20260715, 32)
                _, second = self._exercise(name, 20260716, 32)
                self.assertNotEqual(
                    {proposal.candidate_id for proposal in first},
                    {proposal.candidate_id for proposal in second},
                )

    def test_evolutionary_children_are_generated_from_visited_parents(self) -> None:
        policy = build_policy("evolutionary", self.grammar, 20260715)
        visited: set[str] = set()
        mutation_count = 0
        for step in range(32):
            proposal = policy.propose(SearchState(step, 32 - step))
            if proposal.mutation_receipt is not None:
                mutation_count += 1
                receipt = proposal.mutation_receipt
                self.assertIn(receipt.parent_id, visited)
                self.assertEqual(receipt.child_id, proposal.candidate_id)
                self.assertEqual(receipt.child_genome, proposal.genome.canonical_dict())
                self.assertTrue(receipt.changed_genes)
                self.assertNotEqual(receipt.parent_id, receipt.child_id)
            policy.update(proposal, deterministic_feedback(proposal.candidate_id))
            visited.add(proposal.candidate_id)
        self.assertEqual(mutation_count, 32 - 8)

    def test_no_policy_requires_complete_coverage_before_feedback_update(self) -> None:
        for name in ("cem_like", "uct_ucb_like", "evolutionary"):
            with self.subTest(name=name):
                policy = build_policy(name, self.grammar, 9)
                proposal = policy.propose(SearchState(0, 2))
                policy.update(proposal, deterministic_feedback(proposal.candidate_id))
                self.assertEqual(policy.observation_count, 1)
                self.assertLess(policy.observation_count, self.grammar.support_size)


if __name__ == "__main__":
    unittest.main()
