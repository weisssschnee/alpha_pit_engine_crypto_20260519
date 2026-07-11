from __future__ import annotations

import unittest
import hashlib
import json
import struct
from pathlib import Path

import numpy as np

from alphafactory_crypto.signal_behaviour import (
    behaviour_pair_metrics,
    canonical_coordinate_order,
    canonical_weight_hash,
    cluster_behaviours,
    deterministic_weight_sketch,
    validate_observation_columns,
)


class SignalBehaviourTests(unittest.TestCase):
    def test_weight_hash_canonicalizes_global_inverse_zero_and_nan(self) -> None:
        values = np.array([[np.nan, -0.0, 0.25], [0.0, 0.0, -0.25]], dtype=np.float64)
        inverted = -values
        self.assertEqual(canonical_weight_hash(values), canonical_weight_hash(inverted))
        self.assertEqual(
            canonical_weight_hash(values),
            canonical_weight_hash(np.nan_to_num(values, nan=0.0)),
        )

    def test_coordinate_order_is_independent_of_batch_and_shard_order(self) -> None:
        symbols = ["ETHUSDT", "BTCUSDT"]
        timestamps = np.array([3, 1, 2], dtype=np.int64)
        values = np.array([[30.0, 10.0, 20.0], [3.0, 1.0, 2.0]])
        ordered_symbols, ordered_timestamps, ordered_values = canonical_coordinate_order(
            symbols, timestamps, values
        )
        self.assertEqual(ordered_symbols, ("BTCUSDT", "ETHUSDT"))
        np.testing.assert_array_equal(ordered_timestamps, np.array([1, 2, 3]))
        np.testing.assert_array_equal(ordered_values, np.array([[1.0, 2.0, 3.0], [10.0, 20.0, 30.0]]))
        self.assertEqual(
            canonical_weight_hash(ordered_values),
            canonical_weight_hash(
                canonical_coordinate_order(
                    list(reversed(symbols)), timestamps[::-1], values[::-1, ::-1]
                )[2]
            ),
        )

    def test_pair_metrics_are_multi_dimensional(self) -> None:
        left = np.array([[0.5, 0.5, 0.0], [-0.5, -0.5, 0.0]])
        right = left.copy()
        profile = np.array([1.0, 0.5])
        metrics = behaviour_pair_metrics(
            left,
            right,
            left != 0,
            right != 0,
            left > 0,
            right > 0,
            left < 0,
            right < 0,
            persistence_left=profile,
            persistence_right=profile,
            stability_left=profile,
            stability_right=profile,
        )
        self.assertEqual(
            set(metrics),
            {
                "activation_jaccard",
                "sign_agreement",
                "rank_correlation",
                "top_bottom_overlap",
                "holding_weight_distance",
                "persistence_difference",
                "symbol_month_stability_difference",
            },
        )
        self.assertAlmostEqual(metrics["activation_jaccard"], 1.0)
        self.assertAlmostEqual(metrics["sign_agreement"], 1.0)

    def test_clustering_requires_all_contract_dimensions(self) -> None:
        thresholds = {
            "activation_jaccard_min": 0.95,
            "sign_agreement_min": 0.95,
            "rank_correlation_min": 0.95,
            "top_bottom_overlap_min": 0.90,
            "holding_weight_distance_max": 0.10,
            "persistence_difference_max": 0.10,
            "symbol_month_stability_difference_max": 0.10,
        }
        good = {
            "left": "a",
            "right": "b",
            "activation_jaccard": 1.0,
            "sign_agreement": 1.0,
            "rank_correlation": 1.0,
            "top_bottom_overlap": 1.0,
            "holding_weight_distance": 0.0,
            "persistence_difference": 0.0,
            "symbol_month_stability_difference": 0.0,
        }
        bad = {**good, "left": "b", "right": "c", "persistence_difference": 0.2}
        clusters = cluster_behaviours(["a", "b", "c"], [good, bad], thresholds)
        self.assertEqual(clusters["a"], clusters["b"])
        self.assertNotEqual(clusters["b"], clusters["c"])

    def test_sketch_is_deterministic(self) -> None:
        values = np.arange(100, dtype=np.float64).reshape(10, 10)
        np.testing.assert_array_equal(
            deterministic_weight_sketch(values, size=17),
            deterministic_weight_sketch(values.copy(), size=17),
        )

    def test_observation_column_guard_fails_closed(self) -> None:
        validate_observation_columns(["timestamp", "open_interest_value_last"])
        with self.assertRaises(PermissionError):
            validate_observation_columns(["timestamp", "forward_return_24h"])
        with self.assertRaises(PermissionError):
            validate_observation_columns(["timestamp", "reward"])

    def test_committed_b0a_artifact_is_reproducible_and_no_feedback(self) -> None:
        repo = Path(__file__).resolve().parents[1]
        root = repo / "runtime" / "a7b0a_signal_behaviour_20260711"
        manifest = json.loads((root / "b0a_run_manifest.json").read_text(encoding="utf-8"))
        artifact_hash = hashlib.sha256((root / "signal_behaviour_sketch.bin").read_bytes()).hexdigest().upper()
        self.assertEqual(manifest["decision"], "FROZEN_SIGNAL_BEHAVIOUR_QUALIFIED")
        self.assertEqual(manifest["artifact_sha256"], artifact_hash)
        self.assertEqual(manifest["repeat_artifact_sha256"], artifact_hash)
        self.assertTrue(manifest["reproducible"])
        artifact = (root / "signal_behaviour_sketch.bin").read_bytes()
        self.assertTrue(artifact.startswith(b"B0ASB1\n"))
        header_length = struct.unpack("<Q", artifact[7:15])[0]
        header = json.loads(artifact[15 : 15 + header_length])
        self.assertIn("positive_packbits", header["arrays_per_signal"])
        self.assertIn("negative_packbits", header["arrays_per_signal"])
        for flag in [
            "search_started",
            "candidate_modified",
            "generator_field_added",
            "state_event_reward_connected",
            "cem_ucb_mcts_updated",
            "a7mem_updated",
            "candidate_selection_performed",
            "forward_performance_read",
            "return_label_read",
            "reward_read",
            "spent_oos_reoptimized",
            "b1_lane_integration",
        ]:
            self.assertFalse(manifest[flag], flag)


if __name__ == "__main__":
    unittest.main()
