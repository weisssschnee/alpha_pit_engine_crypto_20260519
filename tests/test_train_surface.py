from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from alphafactory_crypto.train_surface import _apply_temporal_derivations, load_symbol_train


RUNTIME_FIELDS = [
    "account_position_divergence",
    "global_long_short_account_ratio_last",
    "mark_trade_basis_bps",
    "open_interest_value_last",
    "open_interest_value_mean",
    "top_global_account_divergence",
    "top_long_short_account_ratio_last",
    "top_long_short_position_ratio_last",
    "trade_close",
    "trade_quote_volume",
]


def test_oi_change_rebuild_is_trailing_and_segment_independent() -> None:
    frame = pd.DataFrame(
        {
            "timestamp": pd.date_range("2023-12-31 22:00:00", periods=5, freq="1h", tz="UTC"),
            "source_segment": ["PRE2024_COMPLETE_REPLAY"] * 2 + ["TOP498_V3_TRAIN_2024"] * 3,
            "open_interest_last": [100.0, 110.0, 121.0, 133.1, 146.41],
        }
    )
    rebuilt = _apply_temporal_derivations(frame, ["open_interest_last_change_1h"])
    assert pd.isna(rebuilt.loc[0, "open_interest_last_change_1h"])
    assert rebuilt.loc[1:, "open_interest_last_change_1h"].tolist() == pytest.approx([0.1] * 4)


def _base_frame(timestamps: list[str], *, old_names: bool) -> pd.DataFrame:
    frame = pd.DataFrame(
        {
            "symbol": ["BTCUSDT"] * len(timestamps),
            "timestamp": pd.to_datetime(timestamps),
            "feature_available_time": pd.to_datetime(timestamps) + pd.Timedelta(hours=1),
            "global_long_short_account_ratio_last": [1.0 + i * 0.1 for i in range(len(timestamps))],
            "top_long_short_account_ratio_last": [1.2 + i * 0.1 for i in range(len(timestamps))],
            "top_long_short_position_ratio_last": [1.4 + i * 0.1 for i in range(len(timestamps))],
            "open_interest_value_last": [100.0 + i for i in range(len(timestamps))],
            "open_interest_value_mean": [99.0 + i for i in range(len(timestamps))],
            "mark_close": [101.0 + i for i in range(len(timestamps))],
        }
    )
    if old_names:
        frame["close"] = [100.0 + i for i in range(len(timestamps))]
        frame["quote_volume"] = [1000.0 + i for i in range(len(timestamps))]
        frame["recommended_stress_execution_time"] = frame["feature_available_time"] + pd.Timedelta(hours=1)
    else:
        frame["trade_close"] = [100.0 + i for i in range(len(timestamps))]
        frame["trade_quote_volume"] = [1000.0 + i for i in range(len(timestamps))]
        frame["forward_trade_return_1h"] = 999.0
        frame["is_recent_patch"] = False
    return frame


def _config(root: Path) -> dict:
    return {
        "data_root": str(root),
        "train_start_utc": "2023-07-01T00:00:00Z",
        "train_end_exclusive_utc": "2025-01-01T00:00:00Z",
        "runtime_fields": RUNTIME_FIELDS,
        "sources": {
            "pre2024_complete": "pre",
            "pre2024_age": "age",
            "top498_v3": "top",
        },
    }


def test_loader_joins_train_segments_and_excludes_sealed_rows(tmp_path: Path) -> None:
    pre_dir = tmp_path / "pre" / "symbol=BTCUSDT" / "month=2023-12"
    top_dir = tmp_path / "top" / "symbol=BTCUSDT"
    pre_dir.mkdir(parents=True)
    top_dir.mkdir(parents=True)
    _base_frame(["2023-12-31 22:00:00", "2023-12-31 23:00:00"], old_names=True).to_parquet(
        pre_dir / "part.parquet", index=False
    )
    _base_frame(
        ["2024-01-01 00:00:00", "2024-01-01 01:00:00", "2025-01-01 00:00:00"],
        old_names=False,
    ).to_parquet(top_dir / "part.parquet", index=False)

    frame = load_symbol_train(_config(tmp_path), "BTCUSDT")

    assert frame.shape[0] == 4
    assert frame["timestamp"].max() == pd.Timestamp("2024-01-01 01:00:00", tz="UTC")
    assert "forward_trade_return_1h" not in frame
    assert "recommended_stress_execution_time" not in frame
    assert set(RUNTIME_FIELDS).issubset(frame.columns)
    assert frame["account_position_divergence"].iloc[0] == pytest.approx(0.2)
    assert frame["top_global_account_divergence"].iloc[0] == pytest.approx(0.2)


def test_loader_defaults_to_current_runtime_fields(tmp_path: Path) -> None:
    top_dir = tmp_path / "top" / "symbol=BTCUSDT"
    top_dir.mkdir(parents=True)
    _base_frame(["2024-01-01 00:00:00", "2024-01-01 01:00:00"], old_names=False).to_parquet(
        top_dir / "part.parquet", index=False
    )

    frame = load_symbol_train(_config(tmp_path), "BTCUSDT")

    assert frame.columns.tolist() == [
        "symbol",
        "timestamp",
        "feature_available_time",
        "source_segment",
        *RUNTIME_FIELDS,
    ]
