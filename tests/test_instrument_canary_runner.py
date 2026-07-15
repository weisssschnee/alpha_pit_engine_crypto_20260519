from __future__ import annotations

import json
import unittest
from pathlib import Path

from alphafactory_crypto.instrument_canary.admission import (
    _sha256,
    real_data_feedback_contract_payload,
)
from alphafactory_crypto.instrument_canary.grammar import FrozenGrammar
from alphafactory_crypto.instrument_canary.runner import (
    _affine_preflight_indices,
    _real_feedback_contract,
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


if __name__ == "__main__":
    unittest.main()
