from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

import scripts.crypto_native_aggtrades_release as release


def sample_frame() -> pd.DataFrame:
    fields = [
        "trade_count", "underlying_trade_count", "quantity", "notional", "buy_agg_trade_count",
        "sell_agg_trade_count", "buy_quantity", "sell_quantity", "buy_notional", "sell_notional",
        "signed_aggressor_quantity", "signed_aggressor_notional", "vwap", "buy_vwap", "sell_vwap",
        "volume_imbalance", "buy_sell_notional_ratio", "price_range_bps", "close_to_open_bps",
        "large_trade_count_ratio_100k_plus", "large_notional_ratio_100k_plus",
    ]
    rows = []
    for hour in (1, 0):
        row = {"timestamp": pd.Timestamp("2024-01-01", tz="UTC") + pd.Timedelta(hours=hour), "symbol": "BTCUSDT", "month": "2024-01"}
        row.update({field: 1.0 for field in fields})
        rows.append(row)
    return pd.DataFrame(rows)


def test_release_frame_is_sorted_and_observable_only_after_bucket_close() -> None:
    config = release.json.loads(release.CONFIG.read_text(encoding="utf-8"))
    result = release.release_frame(sample_frame(), config["fields"], config["prohibited_columns"])
    assert result.timestamp.is_monotonic_increasing
    assert (result.observable_time == result.timestamp + pd.Timedelta(hours=1)).all()
    assert result.maturity.equals(result.observable_time)
    assert not result.missing_any.any()


def test_performance_columns_fail_closed() -> None:
    frame = sample_frame()
    frame["forward_return_1h"] = 0.1
    config = release.json.loads(release.CONFIG.read_text(encoding="utf-8"))
    with pytest.raises(PermissionError):
        release.release_frame(frame, config["fields"], config["prohibited_columns"])


def test_physical_roles_are_frozen_before_performance() -> None:
    config = release.json.loads(release.CONFIG.read_text(encoding="utf-8"))
    assert release.data_role("2024-01", config) == "DEVELOPMENT"
    assert release.data_role("2024-07", config) == "CHALLENGE"
    assert release.data_role("2024-11", config) == "QUARANTINED_OUT_OF_RELEASE"
    contract = config["mechanism_horizon_contract"]
    assert contract["freeze_before_performance"] is True
    assert contract["horizons"] == ["1h", "4h"]
    assert contract["performance_values_materialized_in_release"] is False


def test_hash_mapping_is_order_invariant() -> None:
    first = {"b": "2", "a": "1"}
    second = {"a": "1", "b": "2"}
    assert release.hash_mapping(first) == release.hash_mapping(second)


def test_safe_reset_rejects_authority_root(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        release.safe_reset(tmp_path, tmp_path)


def test_release_code_does_not_call_evaluator() -> None:
    source = Path(release.__file__).read_text(encoding="utf-8")
    for forbidden in ("multiobjective_evaluate(", "development_feedback(", "load_main_panel(", "strict_evaluations.csv"):
        assert forbidden not in source
