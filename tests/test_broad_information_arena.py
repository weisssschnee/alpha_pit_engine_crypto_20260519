from __future__ import annotations

import numpy as np

from alphafactory_crypto.broad_information_arena import (
    FixedMLP,
    apply_linear_return_calibration,
    causal_trailing_mean,
    deterministic_coordinates,
    fit_nonnegative_linear_return_calibration,
    model_matrix,
    paired_surface_diagnostics,
    purge_label_boundary,
    sticky_mapping_decision,
    turnover_aware_sticky_weights,
)


def test_deterministic_coordinates_are_time_major_and_capped() -> None:
    mask = np.asarray([[True, False, True], [True, True, False]])
    first = deterministic_coordinates(mask, 3)
    second = deterministic_coordinates(mask, 3)
    assert np.array_equal(first[0], second[0])
    assert np.array_equal(first[1], second[1])
    assert len(first[0]) == 3


def test_model_matrix_exposes_values_and_missing_masks() -> None:
    raw = np.asarray([[1.0, np.nan], [3.0, 5.0]], dtype=np.float32)
    matrix = model_matrix(raw, np.asarray([1.0, 1.0]), np.asarray([2.0, 2.0]))
    assert matrix.shape == (2, 4)
    assert matrix[0].tolist() == [0.0, 0.0, 1.0, 0.0]
    assert matrix[1].tolist() == [1.0, 2.0, 1.0, 1.0]


def test_fixed_mlp_learns_a_nonconstant_small_mapping() -> None:
    rng = np.random.default_rng(7)
    x = rng.normal(size=(256, 4)).astype(np.float32)
    y = (x[:, 0] - 0.5 * x[:, 1]).astype(np.float32)
    model = FixedMLP(4, [8], 7)
    result = model.fit(
        x,
        y,
        seed=7,
        epochs=5,
        batch_size=64,
        learning_rate=0.01,
        weight_decay=0.0,
        torch_threads=1,
    )
    prediction = model.predict(x)
    assert result["training_loss_decreased"] is True
    assert np.var(prediction) > 0.01


def test_pair_diagnostics_separate_prediction_difference_from_mapping_collapse() -> None:
    full_prediction = np.asarray([[1.0, 2.0], [2.0, 1.0]])
    control_prediction = np.asarray([[1.0, 1.0], [2.0, 2.0]])
    identical_weights = np.asarray([[0.5, -0.5], [-0.5, 0.5]])
    result = paired_surface_diagnostics(
        full_prediction,
        control_prediction,
        identical_weights,
        identical_weights,
        maximum_rank_samples=100,
    )
    assert result["comparison_degenerate"] is False
    assert result["portfolio_mapping_collapse"] is True


def test_causal_trailing_mean_uses_no_future_values() -> None:
    values = np.asarray([[1.0, 2.0, 3.0, 100.0]])
    result = causal_trailing_mean(values, 3)
    assert result[0, 0] == 1.0
    assert result[0, 1] == 1.5
    assert result[0, 2] == 2.0
    assert result[0, 3] == 35.0


def test_turnover_aware_sticky_mapping_uses_horizon_cohort_and_fixed_cost_gate() -> None:
    strong = np.asarray([0.01, 0.005, -0.005, -0.01])
    prediction = np.column_stack([strong, strong, strong, strong, np.asarray([4e-5, -4e-5, 3e-5, -3e-5])])
    weights, diagnostics = turnover_aware_sticky_weights(
        prediction,
        horizon=4,
        cost_bps=5.0,
        round_trip_multiplier=2.0,
    )
    assert np.allclose(weights.sum(axis=0), 0.0)
    assert np.any(np.abs(weights[:, 0]) > 0.0)
    assert np.array_equal(weights[:, 4], weights[:, 0])
    assert diagnostics["accepted_rebalances"] == 4
    assert diagnostics["rejected_rebalances"] == 1
    assert diagnostics["decision_counts"]["HOLD_NO_TRADE_BAND"] == 1


def test_label_boundary_purge_removes_execution_delay_plus_horizon_tail() -> None:
    assert purge_label_boundary(slice(10, 30), 6) == slice(10, 24)


def test_nonnegative_calibration_recovers_positive_scale_and_flags_direction_flip() -> None:
    prediction = np.asarray([[1.0, 2.0, 3.0], [4.0, 5.0, np.nan]])
    target = 0.25 + 2.0 * prediction
    positive = fit_nonnegative_linear_return_calibration(prediction, target)
    assert positive["fit_degenerate"] is False
    assert np.isclose(positive["slope"], 2.0)
    assert np.isclose(positive["intercept"], 0.25)

    negative = fit_nonnegative_linear_return_calibration(prediction, -prediction)
    assert negative["fit_degenerate"] is True
    assert negative["slope"] == 0.0
    assert negative["unconstrained_slope"] < 0.0


def test_zero_net_sticky_decision_is_invariant_to_calibration_intercept() -> None:
    prediction = np.asarray(
        [
            [0.003, 0.002, 0.001, 0.004, 0.003],
            [0.001, -0.001, 0.002, -0.002, 0.001],
            [-0.001, 0.001, -0.002, 0.002, -0.001],
            [-0.003, -0.002, -0.001, -0.004, -0.003],
        ]
    )
    with_intercept = apply_linear_return_calibration(
        prediction, slope=1.7, intercept=0.123
    )
    without_intercept = apply_linear_return_calibration(
        prediction, slope=1.7, intercept=0.0
    )
    first, _ = turnover_aware_sticky_weights(
        with_intercept, horizon=4, cost_bps=5.0, round_trip_multiplier=2.0
    )
    second, _ = turnover_aware_sticky_weights(
        without_intercept, horizon=4, cost_bps=5.0, round_trip_multiplier=2.0
    )
    assert np.allclose(first, second, rtol=0.0, atol=1e-12)


def test_sticky_gate_counts_degenerate_arm_as_failure() -> None:
    rows = []
    for split in ("selection", "stability"):
        for index in range(4):
            rows.append(
                {
                    "split": split,
                    "matched_surface_difference": {"net_mean": 1e-5},
                    "delta_sleeve_metrics": {"net_mean": 1e-5},
                    "full": {
                        "net_improvement_vs_reference": 1e-5,
                        "turnover_reduction_ratio": 0.1,
                    },
                    "control": {
                        "net_improvement_vs_reference": 1e-5,
                        "turnover_reduction_ratio": 0.1,
                    },
                    "gate_degenerate": index == 0,
                }
            )
    decision = sticky_mapping_decision(rows, minimum_positive_run_ratio=0.8)
    assert decision["gate_degenerate_pairs"] == 2
    assert decision["development_increment_observed"] is False
    assert all(row["matched_positive_ratio"] == 0.75 for row in decision["summary"])
