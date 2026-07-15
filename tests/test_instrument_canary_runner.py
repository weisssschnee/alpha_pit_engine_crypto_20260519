from __future__ import annotations

import json
import unittest
from pathlib import Path
from types import SimpleNamespace

from alphafactory_crypto.instrument_canary.admission import (
    _sha256,
    real_data_feedback_contract_payload,
)
from alphafactory_crypto.instrument_canary.grammar import FrozenGrammar
from alphafactory_crypto.instrument_canary.runner import (
    GRAPH_CONTRACT_IDS,
    SOURCE_AUTHORITY_PATHS,
    _affine_preflight_indices,
    _numeric_alias_integrity,
    _numeric_evaluation_key,
    _real_feedback_contract,
    _replayed_metric_matches,
    validate_frozen_canary_contract,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class CanaryRunnerContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = json.loads(
            (REPO_ROOT / "config" / "crypto_real_data_instrument_canary_v1.json").read_text(
                encoding="utf-8"
            )
        )
        self.grammar = FrozenGrammar.default()

    def test_committed_config_matches_exact_frozen_grammar_and_budget(self) -> None:
        result = validate_frozen_canary_contract(self.config, self.grammar)
        self.assertEqual(result["result"], "PASS")
        self.assertEqual(result["grammar_support_size"], 9576)
        self.assertEqual(result["formal_proposals"], 1024)
        self.assertLessEqual(
            result["formal_proposals"] + result["preflight_evaluations"],
            result["first_evaluation_hard_cap"],
        )

    def test_preflight_is_a_direct_affine_visit_not_universe_ranking(self) -> None:
        first = _affine_preflight_indices(9576, seed=20260715, count=32)
        second = _affine_preflight_indices(9576, seed=20260715, count=32)
        self.assertEqual(first, second)
        self.assertEqual(len(first), 32)
        self.assertEqual(len(set(first)), 32)
        self.assertTrue(all(0 <= index < 9576 for index in first))

    def test_real_feedback_capsule_is_exact_and_explicitly_not_oos_or_alpha(self) -> None:
        payload = real_data_feedback_contract_payload()
        output = _real_feedback_contract()
        self.assertEqual(
            output["contract_sha256"], _sha256(payload)
        )
        self.assertEqual(output["scope"], "REAL_EXISTING_RELEASE_DEVELOPMENT_TRAIN_ONLY_CANARY")
        self.assertFalse(output["oos_role"])
        self.assertFalse(output["economic_alpha_claim"])

    def test_opening_any_hard_boundary_invalidates_contract(self) -> None:
        self.config["boundaries"]["candidate_promotion"] = True
        with self.assertRaisesRegex(ValueError, "boundary opened"):
            validate_frozen_canary_contract(self.config, self.grammar)

    def test_mapping_execution_and_strict_sample_drift_fail_closed(self) -> None:
        cases = (
            ("mapping", lambda config: config["mapping"].__setitem__("CROSS_SECTIONAL_RELATIVE", "BOGUS")),
            ("execution", lambda config: config["execution"].__setitem__("horizon_4h_sleeves", 1)),
            ("sample", lambda config: config["strict_audit_sample"].__setitem__("top_feedback", 9)),
        )
        for label, mutate in cases:
            with self.subTest(label=label):
                config = json.loads(json.dumps(self.config))
                mutate(config)
                with self.assertRaises(ValueError):
                    validate_frozen_canary_contract(config, self.grammar)

    def test_numeric_cache_identity_binds_sparse_support_and_diagnostics(self) -> None:
        receipt = SimpleNamespace(
            release_view_sha256="release",
            target_horizon_hours=1,
            mapping_contract_sha256="mapping",
            cost_contract_sha256="cost",
        )
        base = {
            "weight_array_sha256": "weights",
            "feasible_array_sha256": "feasible-a",
            "mapping_diagnostics_sha256": "diagnostics-a",
        }
        first = _numeric_evaluation_key(receipt, SimpleNamespace(**base))
        changed_feasible = _numeric_evaluation_key(
            receipt,
            SimpleNamespace(**{**base, "feasible_array_sha256": "feasible-b"}),
        )
        changed_diagnostics = _numeric_evaluation_key(
            receipt,
            SimpleNamespace(
                **{**base, "mapping_diagnostics_sha256": "diagnostics-b"}
            ),
        )
        self.assertNotEqual(first, changed_feasible)
        self.assertNotEqual(first, changed_diagnostics)

    def test_numeric_alias_integrity_treats_matching_nan_evidence_as_equal(self) -> None:
        representative = {
            "candidate_id": "representative",
            "first_evaluation": True,
            "numeric_evaluation_key": "numeric-key",
            "numeric_alias_cache_hit": False,
            "numeric_representative_candidate_id": "representative",
            "worst_block_margin": float("nan"),
            "positive_block_fraction": float("nan"),
        }
        alias = {
            **representative,
            "candidate_id": "alias",
            "numeric_alias_cache_hit": True,
        }
        self.assertTrue(
            _numeric_alias_integrity(
                [representative, alias],
                {
                    "search": {
                        "first_evaluations": 2,
                        "numeric_representative_evaluations": 1,
                        "exact_numeric_alias_savings": 1,
                    }
                },
            )
        )

    def test_independent_replay_matches_same_nonfinite_metric(self) -> None:
        self.assertTrue(_replayed_metric_matches(float("nan"), float("nan")))
        self.assertTrue(_replayed_metric_matches(None, float("nan")))
        self.assertTrue(_replayed_metric_matches(float("inf"), float("inf")))
        self.assertFalse(_replayed_metric_matches(float("nan"), 0.0))
        self.assertFalse(_replayed_metric_matches(float("inf"), float("-inf")))

    def test_graph_profile_and_source_authority_are_explicit_and_nonempty(self) -> None:
        profile = json.loads(
            (REPO_ROOT / "profiles" / "crypto-real-data-instrument-canary.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(profile["id"], "crypto-real-data-instrument-canary")
        self.assertEqual(len(profile["required_components"]), 8)
        self.assertEqual(len(profile["required_edges"]), 7)
        self.assertEqual(len(GRAPH_CONTRACT_IDS), 18)
        self.assertIn(
            "alphafactory_crypto/instrument_capability/feedback.py",
            SOURCE_AUTHORITY_PATHS,
        )


if __name__ == "__main__":
    unittest.main()
