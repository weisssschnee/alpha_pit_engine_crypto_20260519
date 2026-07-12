from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

import scripts.crypto_native_aggtrades_benchmark as benchmark


def frame() -> pd.DataFrame:
    timestamps = pd.date_range("2024-01-01", periods=48, freq="h", tz="UTC")
    rows = []
    for symbol, offset in (("A", 0.0), ("B", 1.0), ("C", 2.0)):
        for ordinal, timestamp in enumerate(timestamps):
            rows.append({"timestamp": timestamp, "symbol": symbol, "month": "2024-01", "data_role": "DEVELOPMENT",
                         "volume_imbalance": ordinal + offset, "signed_aggressor_notional": ordinal + offset,
                         "large_notional_ratio_100k_plus": (ordinal % 5) / 5, "close_to_open_bps": offset - ordinal / 100,
                         "close_price": 100 + ordinal + offset})
    return pd.DataFrame(rows).sort_values(["symbol", "timestamp"], kind="mergesort").reset_index(drop=True)


def test_transforms_and_variants_are_deterministic() -> None:
    data = frame()
    spec = {"operator": "ZSCORE_24H", "field": "volume_imbalance"}
    base = benchmark.transform(data, spec)
    first = benchmark.variant_values(base, data, "SHUFFLED_WITHIN_SYMBOL_MONTH", 7)
    second = benchmark.variant_values(base, data, "SHUFFLED_WITHIN_SYMBOL_MONTH", 7)
    assert first.equals(second)
    assert benchmark.variant_values(base, data, "SIGN_FLIP", 7).equals(-base)


def test_future_label_uses_exact_time_and_execution_delay() -> None:
    data = frame()
    label = benchmark.future_label(data, horizon=1, delay=1)
    block = data[data.symbol.eq("A")]
    first = block.index[0]
    expected = np.log(block.iloc[2].close_price / block.iloc[1].close_price)
    assert label.loc[first] == expected
    assert label.loc[block.index[-1]] != label.loc[block.index[-1]]


def test_cross_sectional_weights_have_unit_gross_exposure() -> None:
    data = frame()
    weights = benchmark.cross_sectional_weights(data.volume_imbalance, data)
    gross = weights.abs().groupby(data.timestamp).sum()
    assert np.allclose(gross, 1.0)


def test_fixed_budget_is_predeclared() -> None:
    config = json.loads(benchmark.CONFIG.read_text(encoding="utf-8"))
    expected = len(config["benchmarks"]) * len(config["variants"]) * len(config["horizons_hours"]) * len(config["roles"]) + len(config["horizons_hours"]) * len(config["roles"])
    assert expected == 164 == config["fixed_evaluation_count"]
    assert config["online_adjustment"] is False
    assert config["complex_search_participation"] is False


def test_code_contains_no_search_or_forward_loader() -> None:
    source = Path(benchmark.__file__).read_text(encoding="utf-8")
    for forbidden in ("CEM", "MCTS", "surrogate", "validation", "recent", "May stress", "forward_performance"):
        assert forbidden not in source
