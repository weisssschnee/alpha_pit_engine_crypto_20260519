from __future__ import annotations

import hashlib
import unittest

import numpy as np

from alphafactory_crypto.instrument_capability.evidence_mapping import (
    mapping_synthetic_behavior_payload,
)
from alphafactory_crypto.instrument_capability.mapping import (
    CROSS_SECTIONAL_ZERO_NET,
    DEFAULT_MAPPING_CONTRACTS,
    SPARSE_EVENT_OR_CARRY,
    TIME_SERIES_DIRECTIONAL_STATEFUL,
    MappingContract,
    map_portfolio,
    mapping_contract_sha256,
    portfolio_series,
    turnover_decomposition,
)
from alphafactory_crypto.instrument_capability.primitives import (
    CANONICAL_PRIMITIVES,
    evaluate_primitive,
    primitive_contract_payload,
)


class CanonicalPrimitiveTests(unittest.TestCase):
    def test_contract_has_exact_requested_primitive_authority(self) -> None:
        expected = {
            "Delta", "Slope", "Acceleration", "Persistence", "Duration", "StateAge",
            "TimeSince", "LastHit", "FirstHit", "Transition", "PathShape",
            "EventWindow", "MultiScaleRelation",
        }
        self.assertEqual(set(CANONICAL_PRIMITIVES), expected)
        required = {
            "primitive_id", "canonical_semantics", "canonical_implementation", "input_domain",
            "output_domain", "window_semantics", "warm_up_rule", "missing_value_rule",
            "activation_semantics", "event_state_assumptions", "expected_invariants",
            "deprecated_aliases",
        }
        for row in primitive_contract_payload()["contracts"]:
            self.assertTrue(required.issubset(row))

    def test_delta_slope_and_acceleration_invariants(self) -> None:
        time = np.arange(20, dtype=float)
        linear = (3.0 * time + 7.0)[None, :]
        constant = np.ones((1, 20), dtype=float) * 4.0
        quadratic = (time * time)[None, :]
        delta = evaluate_primitive("Delta", linear, window=4)
        slope = evaluate_primitive("Slope", linear, window=5)
        acceleration = evaluate_primitive("Acceleration", quadratic, window=3)
        self.assertTrue(np.isnan(delta[0, :4]).all())
        np.testing.assert_allclose(delta[0, 4:], 12.0)
        np.testing.assert_allclose(slope[0, 4:], 3.0)
        np.testing.assert_allclose(evaluate_primitive("Slope", constant, window=5)[0, 4:], 0.0)
        np.testing.assert_allclose(acceleration[0, 6:], 18.0)
        np.testing.assert_allclose(evaluate_primitive("Acceleration", linear, window=3)[0, 6:], 0.0)

    def test_state_age_time_since_last_hit_and_duration_do_not_collapse(self) -> None:
        values = np.array([[-1, -1, 1, 1, 1, -1, -1, 1]], dtype=float)
        duration = evaluate_primitive("Duration", values)[0]
        state_age = evaluate_primitive("StateAge", values)[0]
        time_since = evaluate_primitive("TimeSince", values)[0]
        last_hit = evaluate_primitive("LastHit", values)[0]
        first_hit = evaluate_primitive("FirstHit", values)[0]
        transition = evaluate_primitive("Transition", values)[0]
        np.testing.assert_allclose(duration, [0, 0, 1, 2, 3, 0, 0, 1])
        np.testing.assert_allclose(state_age, [0, 1, 0, 1, 2, 0, 1, 0])
        np.testing.assert_allclose(time_since, [np.nan, np.nan, 0, 1, 2, 3, 4, 0], equal_nan=True)
        np.testing.assert_allclose(last_hit, [np.nan, np.nan, 2, 2, 2, 2, 2, 7], equal_nan=True)
        np.testing.assert_allclose(first_hit, [0, 0, 1, 0, 0, 0, 0, 0])
        np.testing.assert_allclose(transition, [0, 0, 1, 0, 0, -1, 0, 1])
        identities = {
            hashlib.sha256(np.nan_to_num(value, nan=-999).tobytes() + np.isfinite(value).tobytes()).hexdigest()
            for value in (duration, state_age, time_since, last_hit)
        }
        self.assertEqual(len(identities), 4)

    def test_missing_segment_resets_stateful_primitives(self) -> None:
        values = np.array([[-1, 1, 1, np.nan, 1, 1, -1]], dtype=float)
        np.testing.assert_allclose(
            evaluate_primitive("Duration", values)[0],
            [0, 1, 2, np.nan, 1, 2, 0],
            equal_nan=True,
        )
        np.testing.assert_allclose(
            evaluate_primitive("StateAge", values)[0],
            [0, 0, 1, np.nan, 0, 1, 0],
            equal_nan=True,
        )
        np.testing.assert_allclose(
            evaluate_primitive("FirstHit", values)[0],
            [0, 1, 0, np.nan, 1, 0, 0],
            equal_nan=True,
        )

    def test_event_window_counts_events_not_occupancy(self) -> None:
        values = np.array([[-1, -1, 1, 1, 1, -1, -1, 1]], dtype=float)
        actual = evaluate_primitive("EventWindow", values, window=4)[0]
        np.testing.assert_allclose(actual, [np.nan, np.nan, np.nan, 1, 1, 1, 0, 1], equal_nan=True)

    def test_path_shape_is_not_multiscale_alias(self) -> None:
        values = np.array([[0, 0, 0, 4, 4, -3, -3, 1, 0, 2]], dtype=float)
        path = evaluate_primitive("PathShape", values, window=6)
        multi = evaluate_primitive("MultiScaleRelation", values, window=3, long_window=6)
        common = np.isfinite(path) & np.isfinite(multi)
        self.assertTrue(common.any())
        self.assertFalse(np.allclose(path[common], multi[common]))


class ExplicitMappingTests(unittest.TestCase):
    def test_synthetic_evidence_checks_final_caps_for_all_mappings(self) -> None:
        payload = mapping_synthetic_behavior_payload()
        self.assertTrue(payload["all_checks_pass"])
        self.assertTrue(
            payload["checks"]["final_position_cap_holds_all_mappings"]
        )
        cap_case = payload["cases"]["position_cap"]
        self.assertTrue(cap_case["all_mappings_pass"])
        self.assertEqual(
            set(cap_case["mappings"]),
            {
                CROSS_SECTIONAL_ZERO_NET,
                TIME_SERIES_DIRECTIONAL_STATEFUL,
                SPARSE_EVENT_OR_CARRY,
            },
        )
        for mapping_id, evidence in cap_case["mappings"].items():
            with self.subTest(mapping_id=mapping_id):
                self.assertTrue(evidence["position_cap_holds"])
                self.assertTrue(evidence["gross_cap_holds"])
                self.assertLessEqual(
                    evidence["final_max_abs_weight"],
                    evidence["declared_position_cap"] + 1e-12,
                )
                self.assertLessEqual(
                    evidence["final_max_gross"],
                    evidence["declared_gross_cap"] + 1e-12,
                )

    def test_cross_sectional_cap_is_true_on_final_weights(self) -> None:
        signal = np.array([[-2.0], [-1.0], [0.0], [1.0], [2.0]])
        result = map_portfolio(signal, DEFAULT_MAPPING_CONTRACTS[CROSS_SECTIONAL_ZERO_NET])
        self.assertTrue(result.feasible[0])
        self.assertLessEqual(float(np.max(np.abs(result.weights))), 0.20 + 1e-12)
        self.assertAlmostEqual(float(np.abs(result.weights).sum()), 0.80)
        self.assertAlmostEqual(float(result.weights.sum()), 0.0)
        self.assertIn("GROSS_REDUCED_FOR_CAP_FEASIBILITY", result.transition_reasons[0])

    def test_cap_property_with_ties_and_missing_values(self) -> None:
        rng = np.random.default_rng(20260715)
        signal = np.round(rng.normal(size=(17, 40)), 1)
        signal[0, ::5] = np.nan
        result = map_portfolio(signal, DEFAULT_MAPPING_CONTRACTS[CROSS_SECTIONAL_ZERO_NET])
        self.assertLessEqual(float(np.max(np.abs(result.weights))), 0.20 + 1e-12)
        self.assertLessEqual(float(np.max(np.abs(result.weights.sum(axis=0)))), 1e-12)

    def test_cross_sectional_deletes_but_directional_preserves_common_mode(self) -> None:
        base = np.tile(np.array([[-1.0], [0.0], [1.0], [2.0]]), (1, 8))
        shifted = base + 20.0
        left_result = map_portfolio(
            base,
            DEFAULT_MAPPING_CONTRACTS[CROSS_SECTIONAL_ZERO_NET],
            include_behavior_provenance=True,
        )
        right_result = map_portfolio(
            shifted,
            DEFAULT_MAPPING_CONTRACTS[CROSS_SECTIONAL_ZERO_NET],
            include_behavior_provenance=True,
        )
        left = left_result.weights
        right = right_result.weights
        np.testing.assert_allclose(left, right)
        self.assertNotEqual(
            left_result.behavior_provenance["stages"]["SIGNAL"]["identity_sha256"],
            right_result.behavior_provenance["stages"]["SIGNAL"]["identity_sha256"],
        )
        self.assertEqual(
            left_result.behavior_provenance["stages"]["RANK"]["identity_sha256"],
            right_result.behavior_provenance["stages"]["RANK"]["identity_sha256"],
        )
        self.assertEqual(
            left_result.behavior_provenance["stage_order"],
            [
                "SIGNAL",
                "RANK",
                "NORMALIZED_SCORE",
                "SELECTION",
                "CAPPED_WEIGHT",
                "MAPPED_WEIGHT",
                "EXECUTABLE_WEIGHT",
            ],
        )
        self.assertNotIn("target", left_result.behavior_provenance)
        self.assertNotIn("reward", left_result.behavior_provenance)
        directional_signal = np.ones((4, 8), dtype=float) * 0.9
        directional = map_portfolio(
            directional_signal, DEFAULT_MAPPING_CONTRACTS[TIME_SERIES_DIRECTIONAL_STATEFUL]
        )
        self.assertGreater(float(np.max(directional.weights.sum(axis=0))), 0.0)

    def test_directional_hysteresis_holds_then_exits(self) -> None:
        signal = np.array([[0.0, 0.8, 0.4, 0.1]], dtype=float)
        result = map_portfolio(signal, DEFAULT_MAPPING_CONTRACTS[TIME_SERIES_DIRECTIONAL_STATEFUL])
        np.testing.assert_allclose(result.weights[0], [0.0, 0.25, 0.25, 0.0])

    def test_sparse_singleton_event_is_preserved_and_exits(self) -> None:
        signal = np.zeros((3, 8), dtype=float)
        signal[1, 2] = 1.0
        result = map_portfolio(signal, DEFAULT_MAPPING_CONTRACTS[SPARSE_EVENT_OR_CARRY])
        np.testing.assert_allclose(result.weights[1], [0, 0, 0.25, 0.25, 0.25, 0.25, 0, 0])
        self.assertTrue(result.diagnostics["singleton_preserved"])

    def test_behavior_provenance_is_an_opt_in_projection_with_mapping_parity(self) -> None:
        cases = {
            CROSS_SECTIONAL_ZERO_NET: np.asarray(
                [[-2.0, -1.0], [-1.0, 0.0], [1.0, 2.0], [2.0, 3.0]]
            ),
            TIME_SERIES_DIRECTIONAL_STATEFUL: np.asarray(
                [[0.0, 0.8, 0.4, 0.1], [0.0, -0.9, -0.3, 0.0]]
            ),
            SPARSE_EVENT_OR_CARRY: np.asarray(
                [[0.0, 0.8, 0.0, 0.0], [0.0, 0.0, -0.9, 0.0]]
            ),
        }
        for mapping_id, signal in cases.items():
            with self.subTest(mapping_id=mapping_id):
                contract = DEFAULT_MAPPING_CONTRACTS[mapping_id]
                baseline = map_portfolio(signal, contract)
                traced = map_portfolio(
                    signal,
                    contract,
                    include_behavior_provenance=True,
                )
                np.testing.assert_array_equal(baseline.weights, traced.weights)
                np.testing.assert_array_equal(baseline.feasible, traced.feasible)
                self.assertEqual(
                    baseline.transition_reasons,
                    traced.transition_reasons,
                )
                self.assertEqual(baseline.diagnostics, traced.diagnostics)
                self.assertEqual(baseline.behavior_provenance, {})
                self.assertEqual(
                    traced.behavior_provenance["mapping_id"],
                    mapping_id,
                )

    def test_behavior_provenance_separates_raw_and_train_oriented_signal(self) -> None:
        raw = np.asarray(
            [[-2.0, -1.0], [-1.0, 0.0], [1.0, 2.0], [2.0, 3.0]]
        )
        oriented = -raw
        traced = map_portfolio(
            oriented,
            DEFAULT_MAPPING_CONTRACTS[CROSS_SECTIONAL_ZERO_NET],
            include_behavior_provenance=True,
            source_signal_for_provenance=raw,
        )

        assert traced.behavior_provenance["stage_order"][:2] == [
            "SIGNAL",
            "ORIENTED_SIGNAL",
        ]
        assert (
            traced.behavior_provenance["stages"]["SIGNAL"]["identity_sha256"]
            != traced.behavior_provenance["stages"]["ORIENTED_SIGNAL"][
                "identity_sha256"
            ]
        )
        assert (
            traced.behavior_provenance["stages"]["SIGNAL"]["semantic"]
            == "raw_expression_signal_before_train_orientation"
        )

    def test_turnover_decomposition_and_full_l1_cost(self) -> None:
        signal = np.array([[1.0, -1.0]], dtype=float)
        weights = np.array([[0.2, -0.2]], dtype=float)
        decomposition = turnover_decomposition(signal, weights, cost_bps=5.0)
        np.testing.assert_allclose(decomposition["entry_portfolio_establishment_l1"], [0.2, 0.2])
        np.testing.assert_allclose(decomposition["exit_turnover_l1"], [0.0, 0.2])
        np.testing.assert_allclose(decomposition["rebalance_turnover_l1"], [0.0, 0.0])
        np.testing.assert_allclose(decomposition["mapped_full_l1_turnover"], [0.2, 0.4])
        series = portfolio_series(weights, np.zeros_like(weights), cost_bps=5.0)
        np.testing.assert_allclose(series["cost"], [0.0001, 0.0002])
        np.testing.assert_allclose(series["net"], -series["cost"])

    def test_mapping_identity_changes_with_contract(self) -> None:
        original = DEFAULT_MAPPING_CONTRACTS[CROSS_SECTIONAL_ZERO_NET]
        changed = MappingContract(
            original.portfolio_mapping_id,
            {**original.parameters, "position_cap": 0.19},
            original.rebalance_cadence,
            original.hold_semantics,
            original.cost_model,
        )
        self.assertNotEqual(mapping_contract_sha256(original), mapping_contract_sha256(changed))

    def test_unknown_mapping_is_rejected(self) -> None:
        contract = MappingContract("UNKNOWN", {}, "none", "none", {"cost_bps": 5.0})
        with self.assertRaisesRegex(ValueError, "unknown portfolio_mapping_id"):
            map_portfolio(np.ones((2, 2)), contract)


if __name__ == "__main__":
    unittest.main()
