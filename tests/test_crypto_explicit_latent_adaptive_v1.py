from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import torch

from alphafactory_crypto.latent_adaptive.experiment import (
    ARM_A,
    ARM_B,
    ARM_D,
    ARM_E,
    LatentModel,
    adaptive_decision,
    causal_rolling_mean,
    future_volatility,
    known_window,
    shifted_delta,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads(
    (ROOT / "config" / "crypto_explicit_latent_adaptive_v1.json").read_text()
)


def test_contract_keeps_report_only_and_sealed_roles_closed() -> None:
    assert CONFIG["authorization"]["spent_report_only_access"] is False
    assert CONFIG["authorization"]["sealed_reads"] is False
    assert CONFIG["authorization"]["formula_search"] is False
    assert CONFIG["authorization"]["strict_oos"] is False
    assert CONFIG["authorization"]["promotion"] is False
    assert (
        CONFIG["splits"]["spent_report_only"]["status"]
        == "HISTORICALLY_CONSUMED_NOT_AUTHORIZED"
    )


def test_economic_contract_is_single_frozen_4h_path() -> None:
    contract = CONFIG["economic_contract"]
    assert contract["target"] == "log(close[t+6] / close[t+2])"
    assert contract["horizon_hours"] == 4
    assert contract["mapping_id"] == "CROSS_SECTIONAL_ZERO_NET"
    assert contract["cost_bps"] == 5.0


def test_adaptive_splits_are_ordered_and_stop_before_report_only() -> None:
    splits = CONFIG["splits"]
    assert splits["train"]["end_exclusive"] == splits["selection"]["start"]
    assert splits["selection"]["end_exclusive"] == splits["stability"]["start"]
    assert (
        splits["stability"]["end_exclusive"]
        == splits["spent_report_only"]["start"]
    )


def test_causal_rolling_and_delta_do_not_use_future() -> None:
    values = np.arange(12, dtype=np.float32).reshape(1, 1, 12)
    mean = causal_rolling_mean(values, 3)
    delta = shifted_delta(values, 3)
    assert np.isnan(mean[0, 0, 1])
    assert mean[0, 0, 2] == 1.0
    assert mean[0, 0, 5] == 4.0
    assert np.isnan(delta[0, 0, 2])
    assert delta[0, 0, 3] == 3.0


def test_lazy_known_window_matches_eager_materialization() -> None:
    rng = np.random.default_rng(20260717)
    values = rng.normal(size=(3, 4, 420)).astype(np.float32)
    masks = rng.random(values.shape) > 0.1
    values = np.where(masks, values, 0.0).astype(np.float32)
    raw_like = np.where(masks, values, np.nan)
    eager = np.concatenate(
        [
            values,
            np.nan_to_num(causal_rolling_mean(raw_like, 24), nan=0.0),
            np.nan_to_num(causal_rolling_mean(raw_like, 168), nan=0.0),
            np.nan_to_num(shifted_delta(values, 24), nan=0.0),
        ],
        axis=1,
    )
    data = SimpleNamespace(values=values, masks=masks)
    actual = known_window(data, [0, 2], 200, 360)
    np.testing.assert_allclose(actual, eager[[0, 2], :, 200:360], atol=1e-6)


def test_future_volatility_uses_only_post_execution_returns() -> None:
    close = np.exp(np.arange(20, dtype=np.float32) / 100.0).reshape(1, -1)
    result = future_volatility(close, horizon=4, delay=2)
    assert np.isfinite(result[0, 0])
    changed = close.copy()
    changed[0, 1] *= 2.0
    changed_result = future_volatility(changed, horizon=4, delay=2)
    assert changed_result[0, 0] == result[0, 0]


def test_models_have_reachable_outputs_without_asset_identity() -> None:
    model_config = CONFIG["model"]
    slots = {
        "position_pressure": (0, 1),
        "liquidity_absorption": (2, 3),
        "extreme_state_proximity": (0, 2),
        "crowding_state": (1, 3),
    }
    values = torch.randn(2, 4, 192)
    masks = torch.ones_like(values)
    known = torch.randn(2, 16, 192)
    for arm in (ARM_A, ARM_B, ARM_E):
        model = LatentModel(arm, 4, 16, model_config, slots)
        output = model(values, masks, known)
        assert output["prediction"].shape == (2, 192)
        assert torch.isfinite(output["prediction"]).all()
        output["prediction"].mean().backward()
        assert any(
            parameter.grad is not None
            for parameter in model.parameters()
            if parameter.requires_grad
        )
    known_model = LatentModel(ARM_A, 4, 16, model_config, slots)
    known_prediction = known_model(values, masks, known)["prediction"].detach()
    residual = LatentModel(ARM_D, 4, 16, model_config, slots)
    output = residual(
        values, masks, known, frozen_known_prediction=known_prediction
    )
    assert output["prediction"].shape == known_prediction.shape


def test_budget_is_hard_capped_and_pilots_are_short() -> None:
    assert CONFIG["budget"]["hard_job_cap"] == 25
    assert CONFIG["budget"]["formal_neural_jobs"] == 15
    assert CONFIG["training"]["pilot_steps"] <= (
        CONFIG["training"]["formal_steps"] * 0.1
    )


def test_cli_supports_non_retraining_formal_stage() -> None:
    script = (
        ROOT / "scripts" / "crypto_explicit_latent_adaptive_v1.py"
    ).read_text(encoding="utf-8")
    assert 'choices=("stage0", "formal", "all")' in script


def test_adaptive_decision_reads_prediction_variance_from_representation() -> None:
    economics = []
    representations = []
    for arm in (ARM_D, ARM_E):
        for seed in CONFIG["training"]["seeds"]:
            increment = {
                "net_mean": 0.01,
                "gross_mean": 0.02,
                "month_metrics": [
                    {"net_mean": 0.01},
                    {"net_mean": 0.02},
                ],
            }
            economics.append(
                {
                    "record_type": "economic",
                    "split": "stability",
                    "arm": arm,
                    "seed": seed,
                    "model": {},
                    "increment": increment,
                }
            )
            representations.append(
                {
                    "record_type": "representation",
                    "split": "stability",
                    "arm": arm,
                    "seed": seed,
                    "prediction_variance": 0.1,
                }
            )
    decision = adaptive_decision(economics, representations)
    assert set(decision["winning_arms"]) == {ARM_D, ARM_E}
