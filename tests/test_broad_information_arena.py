from __future__ import annotations

import numpy as np

from alphafactory_crypto.broad_information_arena import (
    FixedMLP,
    causal_trailing_mean,
    deterministic_coordinates,
    model_matrix,
    paired_surface_diagnostics,
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
