from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from alphafactory_crypto.frontier_arena import (
    build_alpha158_features,
    build_dmn_features,
    cross_sectional_unit_gross,
    evaluate_weights,
    topk_dropout_weights,
    validate_external_data_contract,
    validate_frontier_config,
)


REPO = Path(__file__).resolve().parents[1]
CONFIG = REPO / "config/crypto_external_frontier_assimilation_v1.json"


def synthetic_daily(days: int = 90) -> pd.DataFrame:
    dates = pd.date_range("2024-01-01", periods=days, freq="D", tz="UTC")
    rows = []
    for symbol_ordinal, symbol in enumerate(("A", "B", "C", "D")):
        for ordinal, date in enumerate(dates):
            close = 100.0 + symbol_ordinal * 3.0 + ordinal * (0.1 + symbol_ordinal * 0.01) + np.sin(ordinal / 5)
            rows.append({
                "date": date,
                "symbol": symbol,
                "data_role": "DEVELOPMENT" if ordinal < 60 else "CHALLENGE",
                "month": date.strftime("%Y-%m"),
                "open": close * 0.999,
                "high": close * 1.01,
                "low": close * 0.99,
                "close": close,
                "vwap": close * 1.0002,
                "volume": 1000.0 + ordinal + symbol_ordinal,
                "notional": close * (1000.0 + ordinal),
                "trade_count": 100 + ordinal,
                "signed_flow": (-1) ** ordinal * 10.0,
                "flow_imbalance": (-1) ** ordinal * 0.01,
                "observable_time": date + pd.Timedelta(days=1),
                "maturity": date + pd.Timedelta(days=1),
                "source_lag_seconds": 0,
                "hour_coverage": 24,
            })
    frame = pd.DataFrame(rows).sort_values(["symbol", "date"], kind="mergesort").reset_index(drop=True)
    group = frame.groupby("symbol", sort=False)
    frame["return_1d"] = group.close.pct_change(fill_method=None)
    frame["label"] = group.close.shift(-2) / group.close.shift(-1) - 1.0
    frame["label_observable_time"] = frame.date + pd.Timedelta(days=3)
    return frame


def test_frontier_config_freezes_two_reproductions_and_all_prohibitions() -> None:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    validate_frontier_config(config)
    assert config["fixed_budget"]["external_reproductions"] == 2
    assert config["fixed_budget"]["model_fits"] == 8
    assert len(config["frontier_map"]) >= 4
    assert all(config["prohibitions"].values())


def test_alpha158_feature_contract_is_exact_and_order_invariant() -> None:
    frame = synthetic_daily()
    first, names = build_alpha158_features(frame, [5, 10, 20, 30, 60])
    shuffled = frame.sample(frac=1.0, random_state=7).reset_index(drop=True)
    second, second_names = build_alpha158_features(shuffled, [5, 10, 20, 30, 60])
    assert len(names) == len(set(names)) == 158
    assert names == second_names
    keys = ["symbol", "date"]
    pd.testing.assert_frame_equal(
        first.sort_values(keys)[keys + names].reset_index(drop=True),
        second.sort_values(keys)[keys + names].reset_index(drop=True),
    )


def test_qlib_label_has_one_full_day_execution_delay() -> None:
    frame = synthetic_daily(10)
    block = frame[frame.symbol.eq("A")].reset_index(drop=True)
    expected = block.loc[2, "close"] / block.loc[1, "close"] - 1.0
    assert block.loc[0, "label"] == pytest.approx(expected)
    assert block.loc[0, "observable_time"] == block.loc[0, "date"] + pd.Timedelta(days=1)
    assert block.loc[0, "label_observable_time"] > block.loc[0, "observable_time"]


def test_dmn_features_use_only_past_observations() -> None:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))["dmn_reproduction"]
    frame = synthetic_daily()
    base, names = build_dmn_features(frame, config)
    changed = frame.copy()
    changed.loc[(changed.symbol == "A") & (changed.date == changed.date.max()), "close"] *= 10
    modified, _ = build_dmn_features(changed, config)
    earlier = (base.symbol == "A") & (base.date < base.date.max())
    pd.testing.assert_frame_equal(base.loc[earlier, names], modified.loc[earlier, names])


def test_common_weights_are_one_exact_system_vote_and_unit_gross() -> None:
    frame = synthetic_daily(10)
    values = pd.Series(np.arange(len(frame), dtype=float), index=frame.index)
    weights = cross_sectional_unit_gross(values, frame)
    gross = weights.abs().groupby(frame.date).sum()
    assert np.allclose(gross, 1.0)


def test_topk_dropout_is_deterministic_and_does_not_duplicate_assets() -> None:
    frame = synthetic_daily(10)
    score = frame.groupby("symbol", sort=False).close.pct_change(fill_method=None).fillna(0.0)
    first = topk_dropout_weights(score, frame, topk=2, n_drop=1)
    second = topk_dropout_weights(score, frame, topk=2, n_drop=1)
    assert first.equals(second)
    selected = first.gt(0).groupby(frame.date).sum()
    assert (selected <= 2).all()


def test_evaluator_charges_actual_weight_turnover() -> None:
    frame = synthetic_daily(20)
    weights = cross_sectional_unit_gross(frame.close, frame)
    record, path = evaluate_weights(frame, weights, "DEVELOPMENT", 5.0, "X", 0.1, 1.0)
    assert record["failure_mode"] == "NONE"
    assert record["turnover_mean"] >= 0
    assert (path.net_return <= path.gross_return + 1e-15).all()


def test_external_data_contract_blocks_missing_observable_time() -> None:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    contract = next(item for item in config["external_data_contracts"] if item["family"] == "multi_level_l2")
    incomplete = validate_external_data_contract(contract, ["venue", "symbol", "event_time", "side", "level", "price", "quantity"])
    assert incomplete["ready"] is False
    assert incomplete["missing_columns"] == ["observed_time"]
    complete = validate_external_data_contract(contract, contract["required_schema"])
    assert complete["ready"] is True


def test_runner_source_contains_no_forward_or_promotion_loader() -> None:
    source = (REPO / "scripts/crypto_external_frontier_assimilation.py").read_text(encoding="utf-8")
    for forbidden in ("forward_performance", "promote_candidate(", "A7MEM", "May_stress"):
        assert forbidden not in source
