from __future__ import annotations

import unittest

import numpy as np

from alphafactory_crypto.identity_registry import (
    activation_identity,
    canonical_identity,
    register_economic_hypothesis,
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


if __name__ == "__main__":
    unittest.main()
