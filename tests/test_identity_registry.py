from __future__ import annotations

import unittest

import numpy as np

from alphafactory_crypto.identity_registry import (
    activation_identity,
    activation_cluster_identity,
    canonical_identity,
    economic_hypothesis_assignment,
    pnl_regime_diagnostic_identity,
    register_economic_hypothesis,
    register_behaviour_identity,
    syntax_identity,
)


class IdentityRegistryTests(unittest.TestCase):
    def test_syntax_and_canonical_layers_are_distinct_apis(self) -> None:
        self.assertTrue(syntax_identity("Add(a,b)").startswith("syntax:"))
        self.assertTrue(canonical_identity("Add(a,b)").startswith("canonical:"))

    def test_activation_identity_requires_universe_and_time_shape(self) -> None:
        mask = np.array([[True, False], [False, True]])
        identity = activation_identity(mask, universe_ids=["BTC", "ETH"], timestamps_ns=np.array([1, 2]))
        self.assertTrue(identity.startswith("activation:"))
        with self.assertRaises(ValueError):
            activation_identity(mask, universe_ids=["BTC"], timestamps_ns=np.array([1, 2]))

    def test_economic_hypothesis_cannot_be_inferred_without_registered_id(self) -> None:
        with self.assertRaises(ValueError):
            register_economic_hypothesis("positioning_like", "semantic pair only")
        registered = register_economic_hypothesis("hypothesis:funding-crowding", "docs/hypotheses/funding.md")
        self.assertEqual(registered.status, "REGISTERED")

    def test_activation_cluster_uses_behavior_identity_not_expression(self) -> None:
        cluster = activation_cluster_identity("activation:abc")
        self.assertTrue(cluster.startswith("activation-cluster:"))
        with self.assertRaises(ValueError):
            activation_cluster_identity("")

    def test_behaviour_identity_requires_registered_observation_provenance(self) -> None:
        registered = register_behaviour_identity("behaviour:abc", "runtime/a7b0a_signal_behaviour_20260711")
        self.assertEqual(registered.layer, "behaviour")
        self.assertEqual(registered.status, "REGISTERED_OBSERVATION_ONLY")
        with self.assertRaises(ValueError):
            register_behaviour_identity("expression:abc", "test")

    def test_pnl_regime_diagnostic_requires_spent_roles_and_is_sign_only(self) -> None:
        metrics = {"validation": 1.0, "test": -0.1, "recent": 3.0, "stress": 0.0}
        roles = {name: "SPENT_HISTORICAL_EVALUATION" for name in metrics}
        first = pnl_regime_diagnostic_identity(metrics, roles)
        second = pnl_regime_diagnostic_identity({**metrics, "validation": 99.0}, roles)
        self.assertEqual(first.identity_id, second.identity_id)
        self.assertIn("validation:POS", first.provenance)
        with self.assertRaises(PermissionError):
            pnl_regime_diagnostic_identity(metrics, {**roles, "test": "SEALED_FORWARD"})

    def test_economic_hypothesis_assignment_uses_fields_not_performance(self) -> None:
        registered = economic_hypothesis_assignment(
            "hypothesis:oi-versus-crowding",
            expression="Sub(Delta(open_interest_value_mean,240),Mean(top_long_short_account_ratio_last,120))",
            required_fields=["open_interest_value_mean", "top_long_short_account_ratio_last"],
            required_operators=["Sub", "Delta"],
            mechanism="open-interest change relative to account crowding",
            provenance="config/crypto_b0p_economic_hypothesis_registry_v1.json",
        )
        self.assertEqual(registered.layer, "economic_hypothesis")
        with self.assertRaises(ValueError):
            economic_hypothesis_assignment(
                "hypothesis:missing-field",
                expression="Delta(open_interest_value_mean,240)",
                required_fields=["future_return"],
                required_operators=["Delta"],
                mechanism="invalid",
                provenance="test",
            )
        with self.assertRaises(ValueError):
            economic_hypothesis_assignment(
                "hypothesis:wrong-structure",
                expression="Delta(open_interest_value_mean,240)",
                required_fields=["open_interest_value_mean"],
                required_operators=["SafeDiv"],
                mechanism="invalid structure",
                provenance="test",
            )


if __name__ == "__main__":
    unittest.main()
