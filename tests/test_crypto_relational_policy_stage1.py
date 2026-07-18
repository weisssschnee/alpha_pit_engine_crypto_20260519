from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

import torch

from alphafactory_crypto.relational_policy import (
    RELATIONAL_ARM,
    SHIFTED_RELATIONAL_NULL_ARM,
    TEMPORAL_ONLY_ARM,
    RelationalAttributionModel,
    decide_stage1,
    identical_initialized_models,
    stage1_block_metrics,
)
from scripts.crypto_relational_policy_stage1 import compare_parity


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads(
    (REPO_ROOT / "config/crypto_relational_policy_stage1_v1.json").read_text(
        encoding="utf-8"
    )
)


def _inputs() -> dict[str, torch.Tensor]:
    generator = torch.Generator().manual_seed(20260718)
    batch, history, assets = 2, 12, 6
    eligibility = torch.ones(batch, history, assets, dtype=torch.bool)
    eligibility[0, :5, 4] = False
    eligibility[1, :, 5] = False
    shifted_eligibility = eligibility.roll(2, dims=1)
    return {
        "asset_values": torch.randn(batch, history, assets, 8, generator=generator),
        "market_values": torch.randn(batch, history, 2, generator=generator),
        "eligibility": eligibility,
        "shifted_peer_values": torch.randn(
            batch, history, assets, 8, generator=generator
        ),
        "shifted_peer_eligibility": shifted_eligibility,
    }


class RelationalPolicyStage1Tests(unittest.TestCase):
    def _model(self) -> RelationalAttributionModel:
        torch.manual_seed(20260718)
        model = RelationalAttributionModel(
            asset_features=8,
            market_features=2,
            hidden_size=8,
            attention_heads=2,
            temporal_kernel=3,
        )
        model.eval()
        return model

    def test_contract_is_small_fixed_and_development_only(self) -> None:
        self.assertEqual(CONFIG["training"]["arms"], [
            TEMPORAL_ONLY_ARM,
            RELATIONAL_ARM,
            SHIFTED_RELATIONAL_NULL_ARM,
        ])
        self.assertEqual(CONFIG["training"]["seeds"], [20260718, 20260719])
        self.assertEqual(len(CONFIG["splits"]["attribution_blocks"]), 6)
        self.assertEqual(CONFIG["training"]["epochs"], 1)
        self.assertEqual(CONFIG["training"]["expected_optimizer_steps_per_arm_seed"], 245)
        self.assertLessEqual(CONFIG["budget"]["maximum_pc2_machine_hours"], 3.0)
        self.assertTrue(
            all(
                not value
                for value in CONFIG["boundaries"].values()
                if isinstance(value, bool)
            )
        )
        self.assertEqual(CONFIG["lifecycle"]["expires"], "STAGE1_DECISION_CLOSURE")

    def test_temporal_only_has_no_cross_asset_path_and_consumes_early_history(self) -> None:
        model = self._model()
        inputs = _inputs()
        with torch.no_grad():
            base = model(arm=TEMPORAL_ONLY_ARM, **inputs)
            peer_changed = copy.deepcopy(inputs)
            peer_changed["asset_values"][:, :, 1] += 20.0
            changed = model(arm=TEMPORAL_ONLY_ARM, **peer_changed)
            early_changed = copy.deepcopy(inputs)
            early_changed["asset_values"][:, 0, 0] += 20.0
            early = model(arm=TEMPORAL_ONLY_ARM, **early_changed)
        torch.testing.assert_close(base[:, 0], changed[:, 0], atol=1e-7, rtol=1e-7)
        self.assertFalse(torch.allclose(base[:, 0], early[:, 0]))

    def test_relational_is_permutation_equivariant_and_masks_inactive_peers(self) -> None:
        model = self._model()
        inputs = _inputs()
        permutation = torch.tensor([3, 0, 5, 1, 4, 2])
        with torch.no_grad():
            base = model(arm=RELATIONAL_ARM, **inputs)
            permuted_inputs = {
                **inputs,
                "asset_values": inputs["asset_values"][:, :, permutation],
                "eligibility": inputs["eligibility"][:, :, permutation],
                "shifted_peer_values": inputs["shifted_peer_values"][:, :, permutation],
                "shifted_peer_eligibility": inputs["shifted_peer_eligibility"][:, :, permutation],
            }
            permuted = model(arm=RELATIONAL_ARM, **permuted_inputs)
            inactive_changed = copy.deepcopy(inputs)
            inactive_changed["asset_values"][1, :, 5] += 1000.0
            masked = model(arm=RELATIONAL_ARM, **inactive_changed)
        torch.testing.assert_close(permuted, base[:, permutation], atol=2e-6, rtol=2e-6)
        torch.testing.assert_close(base[1, :5], masked[1, :5], atol=1e-7, rtol=1e-7)
        self.assertEqual(float(base[1, 5]), 0.0)

    def test_shifted_null_keeps_current_self_but_breaks_synchronous_peer_path(self) -> None:
        model = self._model()
        inputs = _inputs()
        with torch.no_grad():
            base = model(arm=SHIFTED_RELATIONAL_NULL_ARM, **inputs)
            peer_changed = copy.deepcopy(inputs)
            peer_changed["asset_values"][:, :, 1] += 20.0
            no_sync_peer = model(arm=SHIFTED_RELATIONAL_NULL_ARM, **peer_changed)
            self_changed = copy.deepcopy(inputs)
            self_changed["asset_values"][:, :, 0] += 20.0
            current_self = model(arm=SHIFTED_RELATIONAL_NULL_ARM, **self_changed)
        torch.testing.assert_close(base[:, 0], no_sync_peer[:, 0], atol=1e-7, rtol=1e-7)
        self.assertFalse(torch.allclose(base[:, 0], current_self[:, 0]))

    def test_arms_have_identical_initial_state_and_parameter_count(self) -> None:
        models = identical_initialized_models(
            arms=(TEMPORAL_ONLY_ARM, RELATIONAL_ARM, SHIFTED_RELATIONAL_NULL_ARM),
            seed=20260718,
            asset_features=8,
            market_features=2,
            hidden_size=8,
            attention_heads=2,
            temporal_kernel=3,
        )
        counts = {
            arm: sum(parameter.numel() for parameter in model.parameters())
            for arm, model in models.items()
        }
        self.assertEqual(len(set(counts.values())), 1)
        reference = models[TEMPORAL_ONLY_ARM].state_dict()
        for model in models.values():
            for name, value in model.state_dict().items():
                torch.testing.assert_close(value, reference[name], atol=0.0, rtol=0.0)

    def test_four_of_six_gate_retains_each_seed_and_degenerate_failure(self) -> None:
        rows = []
        blocks = [row["block_id"] for row in CONFIG["splits"]["attribution_blocks"]]
        for seed in (20260718, 20260719):
            for index, block in enumerate(blocks):
                rows.extend(
                    [
                        {"row_type": "PAIR_DELTA", "pair": "B_MINUS_A", "seed": seed, "block_id": block, "primary_delta": 1e-6 if index < 4 else -1e-6},
                        {"row_type": "PAIR_DELTA", "pair": "B_MINUS_N", "seed": seed, "block_id": block, "primary_delta": 1e-6 if index < 4 else -1e-6},
                    ]
                )
        decision = decide_stage1(rows, CONFIG, relational_nondegenerate=True, b_a_outputs_differ=True)
        self.assertEqual(decision["status"], CONFIG["decision"]["pass_status"])

        # The contract votes on six seed-aggregated blocks, then requires each
        # seed's overall direction to be positive.  It does not require each
        # seed independently to win four blocks.
        mixed = []
        for seed in (20260718, 20260719):
            for index, block in enumerate(blocks):
                if seed == 20260718:
                    delta = 2e-6 if index < 3 else -1e-6
                else:
                    delta = -1e-6 if index == 5 else 2e-6
                for pair in ("B_MINUS_A", "B_MINUS_N"):
                    mixed.append(
                        {"row_type": "PAIR_DELTA", "pair": pair, "seed": seed, "block_id": block, "primary_delta": delta}
                    )
        mixed_decision = decide_stage1(
            mixed, CONFIG, relational_nondegenerate=True, b_a_outputs_differ=True
        )
        self.assertEqual(mixed_decision["status"], CONFIG["decision"]["pass_status"])
        missing_seed = [row for row in rows if row["seed"] == 20260718]
        failed = decide_stage1(missing_seed, CONFIG, relational_nondegenerate=True, b_a_outputs_differ=True)
        self.assertEqual(failed["status"], "RELATIONAL_INCREMENT_UNSTABLE")
        degenerate = decide_stage1(rows, CONFIG, relational_nondegenerate=False, b_a_outputs_differ=True)
        self.assertEqual(degenerate["status"], "RELATIONAL_REPRESENTATION_COMPARISON_DEGENERATE")

    def test_nondegeneracy_exposes_cross_sectional_and_temporal_collapse(self) -> None:
        target = torch.linspace(-0.02, 0.02, 24).reshape(4, 6).numpy()
        valid = torch.ones(4, 6, dtype=torch.bool).numpy()
        time_constant = torch.arange(6, dtype=torch.float32).repeat(4, 1).numpy()
        cross_constant = torch.arange(4, dtype=torch.float32)[:, None].repeat(1, 6).numpy()
        time_metrics = stage1_block_metrics(
            time_constant, target, valid, maximum_rank_samples=1000
        )
        cross_metrics = stage1_block_metrics(
            cross_constant, target, valid, maximum_rank_samples=1000
        )
        self.assertEqual(time_metrics["mean_temporal_prediction_variance"], 0.0)
        self.assertGreater(time_metrics["mean_cross_sectional_prediction_variance"], 0.0)
        self.assertEqual(cross_metrics["mean_cross_sectional_prediction_variance"], 0.0)
        self.assertGreater(cross_metrics["mean_temporal_prediction_variance"], 0.0)

    def test_pc2_parity_mismatch_fails_closed(self) -> None:
        side = {
            "source_sha": "a" * 40,
            "config_sha256": "C",
            "token_contract_identity_sha256": "T",
            "schedule_identity_sha256": "S",
            "scaler_identity_sha256": "R",
            "selected_asset_ids": ["BTCUSDT"],
            "decision_timestamp": CONFIG["parity"]["decision_timestamp"],
            "decision_coordinate": 1,
            "input_sha256": {"asset_values": "LEFT"},
            "parameter_counts": {"TEMPORAL_ONLY:20260718": 1},
            "initial_state_sha256": {"TEMPORAL_ONLY:20260718": "I"},
            "data_identity": {
                "logical_content_identity_sha256": "D",
                "metadata_identity_sha256": "M",
            },
            "runtime": {
                "python": "3.11.9",
                "packages": {"numpy": "2.1.3", "pandas": "2.2.3", "pyarrow": "19.0.1", "torch": "2.12.1"},
            },
            "outputs": {
                "TEMPORAL_ONLY:20260718": {"values": [0.0]}
            },
            "wall_seconds": 1.0,
        }
        remote = copy.deepcopy(side)
        remote["input_sha256"]["asset_values"] = "RIGHT"
        with tempfile.TemporaryDirectory() as directory:
            local_path = Path(directory) / "local.json"
            remote_path = Path(directory) / "remote.json"
            local_path.write_text(json.dumps(side), encoding="utf-8")
            remote_path.write_text(json.dumps(remote), encoding="utf-8")
            result = compare_parity(
                local_path,
                remote_path,
                REPO_ROOT / "config/crypto_relational_policy_stage1_v1.json",
            )
        self.assertEqual(result["status"], "STOP_BEFORE_TRAINING")
        self.assertIn("input_sha256", result["mismatches"])


if __name__ == "__main__":
    unittest.main()
