from __future__ import annotations

import json
import unittest
from pathlib import Path

import numpy as np
import torch

from alphafactory_crypto.instrument_canary.evaluator import evaluate_real_mapping
from alphafactory_crypto.relational_policy import (
    DynamicUniverseBatch,
    RelationalCostAwarePolicy,
    direct_net_utility_loss,
    resolve_field_views,
)
from alphafactory_crypto.instrument_capability.mapping import (
    DIRECT_ZERO_NET_COST_AWARE,
    validate_direct_weights,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads(
    (REPO_ROOT / "config/crypto_relational_policy_vertical_slice_v1.json").read_text(
        encoding="utf-8"
    )
)


class RelationalPolicyVerticalSliceTests(unittest.TestCase):
    def test_context_bound_field_views_are_exhaustive_without_fake_merged_panel(self) -> None:
        views = resolve_field_views(REPO_ROOT, CONFIG)
        self.assertEqual(
            {name: len(tokens) for name, tokens in views.items()},
            {
                "BROAD_ASSET_LOCAL": 38,
                "BROAD_MARKET_STATE": 1,
                "CORE3_ASSET_LOCAL_BASE": 31,
                "CORE3_CROSS_SYMBOL_BASE": 5,
                "CORE3_TEMPORAL_DERIVED": 45,
            },
        )
        broad = set(views["BROAD_ASSET_LOCAL"]) | set(views["BROAD_MARKET_STATE"])
        core3 = (
            set(views["CORE3_ASSET_LOCAL_BASE"])
            | set(views["CORE3_CROSS_SYMBOL_BASE"])
            | set(views["CORE3_TEMPORAL_DERIVED"])
        )
        self.assertEqual(len(broad), 39)
        self.assertEqual(len(core3), 81)
        self.assertFalse(broad & core3)

    def test_one_step_relational_direct_weight_path_is_equivariant_and_cost_closed(self) -> None:
        torch.manual_seed(20260718)
        batch_size, history, assets = 4, 12, 8
        eligibility = torch.ones(batch_size, history, assets, dtype=torch.bool)
        eligibility[:, : history // 2, 0] = False
        eligibility[1, -1, 3] = False
        previous_weights = torch.zeros(batch_size, assets, requires_grad=True)
        with torch.no_grad():
            previous_weights[:, 0] = 0.10
            previous_weights[:, 1] = -0.10
        batch = DynamicUniverseBatch(
            asset_values=torch.randn(batch_size, history, assets, 6),
            market_values=torch.randn(batch_size, history, 2),
            eligibility=eligibility,
            previous_weights=previous_weights,
            target_returns=torch.randn(batch_size, assets) * 0.001,
        )
        batch.validate()
        model = RelationalCostAwarePolicy(
            asset_features=6,
            market_features=2,
            hidden_size=8,
            attention_heads=2,
            temporal_kernel=3,
            gross_cap=1.0,
            position_cap=0.2,
        )
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        weights, scores = model(
            batch.asset_values,
            batch.market_values,
            batch.eligibility,
            batch.previous_weights,
        )
        loss = direct_net_utility_loss(
            weights, batch.previous_weights, batch.target_returns, cost_bps=5.0
        )
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        gradient_l1 = sum(
            float(parameter.grad.abs().sum())
            for parameter in model.parameters()
            if parameter.grad is not None
        )
        self.assertGreater(gradient_l1, 0.0)
        self.assertIsNotNone(batch.previous_weights.grad)
        self.assertGreater(float(batch.previous_weights.grad.abs().sum()), 0.0)
        optimizer.step()

        model.eval()
        with torch.no_grad():
            reference_weights, reference_scores = model(
                batch.asset_values,
                batch.market_values,
                batch.eligibility,
                batch.previous_weights,
            )
            permutation = torch.tensor([3, 0, 7, 1, 6, 4, 2, 5])
            permuted_weights, permuted_scores = model(
                batch.asset_values[:, :, permutation],
                batch.market_values,
                batch.eligibility[:, :, permutation],
                batch.previous_weights[:, permutation],
            )
        torch.testing.assert_close(
            permuted_weights, reference_weights[:, permutation], atol=2e-6, rtol=2e-6
        )
        torch.testing.assert_close(
            permuted_scores, reference_scores[:, permutation], atol=2e-6, rtol=2e-6
        )

        mapped = validate_direct_weights(
            reference_weights.numpy().T,
            batch.eligibility[:, -1].numpy().T,
        )
        self.assertEqual(mapped.portfolio_mapping_id, DIRECT_ZERO_NET_COST_AWARE)
        self.assertLessEqual(float(np.max(np.abs(mapped.weights))), 0.2 + 1e-6)
        self.assertLessEqual(float(np.max(np.abs(mapped.weights).sum(axis=0))), 1.0 + 1e-6)
        self.assertLessEqual(float(np.max(np.abs(mapped.weights.sum(axis=0)))), 1e-6)
        self.assertEqual(float(mapped.weights[3, 1]), 0.0)

        evaluation = evaluate_real_mapping(
            mapped,
            reference_scores.numpy().T,
            batch.target_returns.numpy().T,
            np.array(["2024-01"] * batch_size),
            target_horizon_hours=1,
            expected_mapping_id=DIRECT_ZERO_NET_COST_AWARE,
        )
        expected_turnover = float(np.abs(mapped.weights[:, 0]).sum())
        expected_turnover += float(np.abs(np.diff(mapped.weights, axis=1)).sum())
        expected_turnover += float(np.abs(mapped.weights[:, -1]).sum())
        self.assertAlmostEqual(evaluation.total_turnover_l1, expected_turnover, places=6)
        self.assertAlmostEqual(evaluation.total_cost, expected_turnover * 5.0 / 10_000.0)

        invalid_eligibility = batch.eligibility[:, -1].numpy().T.copy()
        active_asset, active_time = np.argwhere(np.abs(mapped.weights) > 1e-8)[0]
        invalid_eligibility[active_asset, active_time] = False
        with self.assertRaisesRegex(ValueError, "ineligible asset"):
            validate_direct_weights(mapped.weights, invalid_eligibility)


if __name__ == "__main__":
    unittest.main()
