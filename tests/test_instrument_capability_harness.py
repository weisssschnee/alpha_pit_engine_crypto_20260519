from __future__ import annotations

import csv
import io
import subprocess
import unittest
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import numpy as np

from alphafactory_crypto.instrument_capability.evaluator import (
    CapabilityEvaluationError,
    evaluate_mapping_result,
)
from alphafactory_crypto.instrument_capability.feedback import (
    StrictMetrics,
    aligned_feedback,
    feedback_contract_payload,
)
from alphafactory_crypto.instrument_capability.harness import (
    FAMILY_IDS,
    MUTATION_GENE_FIELDS,
    PROPOSAL_GRAMMAR,
    PROPOSAL_GRAMMAR_ID,
    build_synthetic_case,
    build_structural_mutation_space,
    evaluate_proposal,
    proposal_mutation_genes,
    qualify_family,
    run_qualification,
    serialize_candidate,
)
from alphafactory_crypto.instrument_capability.legacy import (
    EXPECTED_CLOSURE_SHA,
    FIXED_RAW_PROPOSAL_COORDINATES,
    RAW_PROPOSALS_SOURCE,
    load_legacy_modules,
)
from alphafactory_crypto.instrument_capability.mapping import (
    DEFAULT_MAPPING_CONTRACTS,
    TIME_SERIES_DIRECTIONAL_STATEFUL,
    map_portfolio,
)
from alphafactory_crypto.instrument_capability.search import (
    B1S_LABELS_DEGENERATE,
    MutationOption,
    SUPPORTED_ALGORITHMS,
    run_search,
)


REPO = Path(__file__).resolve().parents[1]


class FeedbackAndEvaluatorTests(unittest.TestCase):
    def test_wrong_lag_is_blocked_before_nonfinite_metrics(self) -> None:
        metrics = StrictMetrics(*(float("nan") for _ in range(9)), finite=False)
        decision = aligned_feedback(
            metrics,
            legal=True,
            mapping_present=True,
            wrong_lag=True,
            primitive_alias_conflict=False,
        )
        self.assertTrue(decision.blocked)
        self.assertEqual(decision.violations, ("WRONG_LAG",))

    def test_feedback_contract_is_lexicographic_not_a_gross_scalar(self) -> None:
        contract = feedback_contract_payload()
        self.assertEqual(contract["method"], "LEXICOGRAPHIC_STRICT_FEASIBILITY_ORDERING")
        self.assertIsNone(contract["scalar_weights"])
        self.assertEqual(contract["legacy_zero_cost_gross_proxy_role"], "DIAGNOSTIC_ONLY_NOT_IN_ORDERING")

    def test_evaluator_rejects_raw_weights(self) -> None:
        with self.assertRaisesRegex(TypeError, "MappingResult only"):
            evaluate_mapping_result(np.zeros((2, 4)), np.zeros((2, 4)), np.zeros(4))  # type: ignore[arg-type]

    def test_evaluator_fails_closed_on_target_missing_under_position(self) -> None:
        signal = np.ones((2, 32), dtype=float)
        mapped = map_portfolio(signal, DEFAULT_MAPPING_CONTRACTS[TIME_SERIES_DIRECTIONAL_STATEFUL])
        target = np.ones_like(signal) * 0.001
        target[0, 5] = np.nan
        with self.assertRaisesRegex(CapabilityEvaluationError, "TARGET_MISSING_UNDER_NONZERO_WEIGHT"):
            evaluate_mapping_result(mapped, target, np.zeros(32))


class PlantedHarnessTests(unittest.TestCase):
    def test_all_seven_families_pass_one_seed_and_reject_required_decoys(self) -> None:
        for family_id in FAMILY_IDS:
            with self.subTest(family_id=family_id):
                row = qualify_family(family_id, 20260715)
                self.assertTrue(row["qualified"])
                self.assertTrue(all(row["qualification_checks"].values()))
                self.assertEqual(row["candidates"]["wrong_lag"]["entered_strict"], False)
                self.assertEqual(row["candidates"]["primitive_alias"]["entered_strict"], False)
                self.assertTrue(row["candidates"]["positive"]["feedback"]["feasible"])
                self.assertTrue(row["qualification_checks"]["proposal_generated_from_frozen_grammar"])
                self.assertEqual(row["mapping_preservation_receipt"]["result"], "PASS")

    def test_relabelling_does_not_bypass_lag_or_primitive_receipts(self) -> None:
        case = build_synthetic_case("CROSS_SECTIONAL_RELATIVE_ALPHA", 20260715)
        for role_id, expected_violation, receipt_name in (
            ("WRONG_LAG", "WRONG_LAG", "lag_receipt"),
            ("PRIMITIVE_ALIAS", "PRIMITIVE_ALIAS_CONFLICT", "primitive_receipt"),
        ):
            with self.subTest(role_id=role_id):
                proposal = next(item for item in case.proposals if item.role_id == role_id)
                tampered_label = replace(proposal, evidence_label="positive")
                evidence = evaluate_proposal(case, tampered_label)
                serialized = serialize_candidate(evidence)
                self.assertTrue(evidence.feedback.blocked)
                self.assertFalse(evidence.entered_strict)
                self.assertIn(expected_violation, evidence.feedback.violations)
                self.assertEqual(serialized["admission_receipt"][receipt_name]["result"], "FAIL")
                self.assertEqual(serialized["proposal_receipt"]["evidence_label"], "positive")
                self.assertTrue(serialized["proposal_receipt"]["identity_excludes_evidence_label"])

        positive = next(item for item in case.proposals if item.role_id == "CANONICAL_PLANTED")
        role_relabelled = replace(
            positive,
            role_id="MATCHED_NULL",
            evidence_label="opaque-report-label",
        )
        role_evidence = evaluate_proposal(case, role_relabelled)
        self.assertEqual(role_evidence.candidate_id, positive.grammar_identity)
        self.assertTrue(role_evidence.admission_receipt["grammar"]["identity_valid"])
        self.assertFalse(role_evidence.admission_receipt["grammar"]["member"])
        self.assertTrue(role_evidence.proposal_receipt["identity_excludes_role_id"])

    def test_proposal_grammar_is_frozen_and_search_sees_only_grammar_identity(self) -> None:
        with self.assertRaises(FrozenInstanceError):
            PROPOSAL_GRAMMAR[0].evidence_label = "changed"  # type: ignore[misc]
        row = qualify_family("MARKET_DIRECTIONAL_ALPHA", 20260715)
        identities = set(row["proposal_grammar"]["proposal_identities"])
        self.assertEqual(row["proposal_grammar"]["grammar_id"], PROPOSAL_GRAMMAR_ID)
        self.assertTrue(all(identity.startswith("proposal-grammar:") for identity in identities))
        for search in row["searches"].values():
            self.assertLessEqual(set(search["proposal_order"]), identities)
            self.assertIn(search["survivor_id"], search["proposal_order"])

    def test_mapping_preservation_uses_family_specific_semantics(self) -> None:
        expected = {
            "CROSS_SECTIONAL_RELATIVE_ALPHA": "CROSS_SECTIONAL_ORDER_AND_ZERO_NET_PRESERVED",
            "MARKET_DIRECTIONAL_ALPHA": "COMMON_MODE_DIRECTION_PRESERVED",
            "PERSISTENT_LOW_TURNOVER_ALPHA": "PERSISTENT_STATE_AND_LOW_TURNOVER_PRESERVED",
            "SPARSE_EVENT_ALPHA": "SPARSE_EVENT_ENTRY_HOLD_EXIT_PRESERVED",
            "STATEFUL_HOLD_ALPHA": "STATEFUL_ENTRY_HOLD_EXIT_PRESERVED",
            "FUNDING_CARRY_ALPHA": "SETTLEMENT_CARRY_ENTRY_HOLD_EXIT_PRESERVED",
            "REGIME_CONDITIONED_ALPHA": "REGIME_DIRECTION_AND_REVERSAL_PRESERVED",
        }
        for family_id, check_id in expected.items():
            with self.subTest(family_id=family_id):
                receipt = qualify_family(family_id, 20260715)["mapping_preservation_receipt"]
                self.assertEqual(receipt["check_id"], check_id)
                self.assertTrue(all(receipt["invariants"].values()))

    def test_cross_seed_reproduces_canonical_family_and_behavior(self) -> None:
        payload = run_qualification()
        self.assertEqual(payload["qualification"], "QUALIFIED")
        self.assertTrue(payload["all_runs_qualified"])
        self.assertTrue(payload["cross_seed_qualified"])
        for row in payload["cross_seed_reproduction"].values():
            self.assertTrue(row["exact_reproduction"])
            self.assertTrue(row["canonical_mechanism_reproduction"])
            self.assertTrue(row["behavior_reproduction"])

    def test_qualification_requires_two_distinct_fixed_seeds(self) -> None:
        for seeds in ((123,), (123, 123)):
            with self.subTest(seeds=seeds):
                payload = run_qualification(seeds)
                self.assertEqual(payload["qualification"], "PARTIALLY_QUALIFIED")
                self.assertFalse(payload["minimum_distinct_seed_count_met"])
                self.assertFalse(payload["cross_seed_qualified"])

    def test_evolutionary_uses_label_blind_structural_parent_child_mutation(self) -> None:
        case = build_synthetic_case("CROSS_SECTIONAL_RELATIVE_ALPHA", 20260715)
        relabelled = tuple(
            replace(proposal, evidence_label=f"opaque-{index}")
            for index, proposal in enumerate(case.proposals)
        )
        self.assertEqual(
            build_structural_mutation_space(case.proposals),
            build_structural_mutation_space(relabelled),
        )
        self.assertEqual(
            build_structural_mutation_space(case.proposals),
            build_structural_mutation_space(tuple(reversed(case.proposals))),
        )
        row = qualify_family("CROSS_SECTIONAL_RELATIVE_ALPHA", 20260715)
        contract = row["proposal_grammar"]["evolutionary_mutation_contract"]
        receipts = row["searches"]["evolutionary"]["mutation_receipts"]
        identities = set(row["proposal_grammar"]["proposal_identities"])
        proposals_by_id = {
            proposal.grammar_identity: proposal for proposal in case.proposals
        }
        self.assertEqual(
            contract["selection_basis"],
            "MINIMUM_POSITIVE_STRUCTURAL_GENE_DISTANCE",
        )
        self.assertFalse(contract["evidence_label_visible_to_mutation"])
        self.assertFalse(contract["role_id_visible_to_mutation"])
        self.assertEqual(len(receipts), 27 - len(PROPOSAL_GRAMMAR))
        self.assertEqual(
            [receipt["child_id"] for receipt in receipts],
            row["searches"]["evolutionary"]["proposal_order"][len(PROPOSAL_GRAMMAR) :],
        )
        for receipt in receipts:
            self.assertIn(receipt["parent_id"], identities)
            self.assertIn(receipt["child_id"], identities)
            self.assertNotEqual(receipt["parent_id"], receipt["child_id"])
            self.assertTrue(receipt["changed_genes"])
            self.assertLessEqual(set(receipt["changed_genes"]), set(MUTATION_GENE_FIELDS))
            self.assertNotIn("evidence_label", receipt["changed_genes"])
            self.assertNotIn("role_id", receipt["changed_genes"])
            parent_genes = proposal_mutation_genes(
                proposals_by_id[receipt["parent_id"]]
            )
            child_genes = proposal_mutation_genes(
                proposals_by_id[receipt["child_id"]]
            )
            expected_changed = [
                field
                for field in MUTATION_GENE_FIELDS
                if parent_genes[field] != child_genes[field]
            ]
            self.assertEqual(receipt["changed_genes"], expected_changed)

    def test_evolutionary_rejects_mutation_children_outside_frozen_grammar(self) -> None:
        case = build_synthetic_case("CROSS_SECTIONAL_RELATIVE_ALPHA", 20260715)
        evaluated = [evaluate_proposal(case, proposal) for proposal in case.proposals]
        candidate_ids = tuple(proposal.grammar_identity for proposal in case.proposals)
        decisions = {row.candidate_id: row.feedback for row in evaluated}
        bad_space = {
            candidate_id: (MutationOption("not-a-grammar-member", ("signal_recipe",)),)
            for candidate_id in candidate_ids
        }
        with self.assertRaisesRegex(ValueError, "candidate universe"):
            run_search(
                "evolutionary",
                candidate_ids,
                decisions,
                seed=20260715,
                budget=27,
                mutation_space=bad_space,
            )

    def test_search_policies_have_distinct_observed_behavior(self) -> None:
        row = qualify_family("CROSS_SECTIONAL_RELATIVE_ALPHA", 20260715)
        hashes = {algorithm: result["behavior_hash"] for algorithm, result in row["searches"].items()}
        self.assertEqual(set(hashes), set(SUPPORTED_ALGORITHMS))
        self.assertEqual(len(set(hashes.values())), len(SUPPORTED_ALGORITHMS))
        self.assertTrue(all(result["independent_behavior"] for result in row["searches"].values()))
        self.assertNotIn("typed_ast", SUPPORTED_ALGORITHMS)

    def test_b1s_algorithm_names_remain_classified_degenerate(self) -> None:
        self.assertEqual(B1S_LABELS_DEGENERATE["classification"], "ALGORITHM_LABEL_DEGENERATE")
        self.assertEqual(tuple(B1S_LABELS_DEGENERATE["labels"]), ("cem", "uct_mcts", "evolutionary"))

    def test_qualification_is_deterministic_for_fixed_seed(self) -> None:
        first = qualify_family("SPARSE_EVENT_ALPHA", 20260715)
        second = qualify_family("SPARSE_EVENT_ALPHA", 20260715)
        self.assertEqual(first, second)

    def test_same_case_exposes_explicit_mapping_contract(self) -> None:
        case = build_synthetic_case("MARKET_DIRECTIONAL_ALPHA", 20260715)
        self.assertEqual(case.positive_mapping.portfolio_mapping_id, TIME_SERIES_DIRECTIONAL_STATEFUL)
        self.assertTrue(case.positive_mapping.contract_sha256)


class LegacyParityIdentityTests(unittest.TestCase):
    def test_closure_modules_load_at_exact_tag_without_checkout(self) -> None:
        modules = load_legacy_modules(REPO)
        self.assertEqual(modules.closure_sha, EXPECTED_CLOSURE_SHA)
        self.assertEqual(set(modules.source_sha256), {"temporal_program", "b1s_canary", "nextgen_epoch"})

    def test_fixed_coordinates_are_first_legal_rows_without_performance_selection(self) -> None:
        completed = subprocess.run(
            ["git", "show", f"{EXPECTED_CLOSURE_SHA}:{RAW_PROPOSALS_SOURCE}"],
            cwd=REPO,
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=True,
        )
        wanted = {row.primitive for row in FIXED_RAW_PROPOSAL_COORDINATES}
        eligible = [
            row
            for row in csv.DictReader(io.StringIO(completed.stdout))
            if row["panel_id"] == "main"
            and row["lane_id"] == "typed_random_fresh"
            and row["legal"] == "True"
            and row["primitive"] in wanted
        ]
        selected = {}
        for row in sorted(eligible, key=lambda item: (int(item["seed"]), int(item["ordinal"]), item["proposal_id"])):
            selected.setdefault(row["primitive"], row["proposal_id"])
        actual = {row.primitive: row.proposal_id for row in FIXED_RAW_PROPOSAL_COORDINATES}
        self.assertEqual(actual, selected)


if __name__ == "__main__":
    unittest.main()
