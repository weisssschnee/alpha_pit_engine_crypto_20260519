from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from alphafactory_crypto.broad_search.compositional18m import CandidateSpec
from alphafactory_crypto.broad_search.pair18m import PAIR_THRESHOLDS
from alphafactory_crypto.broad_search.replay_v14_binance_target import (
    _build_target_arrays,
    _waterfall_rows,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def _metrics(value: float = 0.001) -> dict[str, object]:
    return {
        "observations": 10,
        "net_mean": value,
        "net_standard_error": 0.0001,
        "net_lcb": value - 0.0002,
        "net_standard_error_method": "NEWEY_WEST_BARTLETT",
        "net_standard_error_lags": 0,
        "monthly_block_mean": value,
        "monthly_block_standard_error": 0.0001,
        "monthly_block_lcb": value - 0.0002,
        "monthly_block_count": 2,
        "gross_mean": value + 0.0001,
        "gross_standard_error": 0.0001,
        "gross_lcb": value - 0.0001,
        "gross_observations": 10,
        "turnover_mean": 0.1,
        "cost_mean": 0.00005,
        "concentration_mean": 0.1,
        "support": 0.9,
        "active_weight_fraction": 0.2,
        "positive_month_fraction": 1.0,
        "median_month": value,
        "worst_month": value,
        "month_metrics": [
            {
                "month": "2025-09",
                "observations": 5,
                "gross_mean": value,
                "cost_mean": 0.00005,
                "net_mean": value - 0.00005,
                "turnover_mean": 0.1,
            },
            {
                "month": "2025-10",
                "observations": 5,
                "gross_mean": -value,
                "cost_mean": 0.00005,
                "net_mean": -value - 0.00005,
                "turnover_mean": 0.1,
            },
        ],
        "weight_sha256": "A",
        "turnover_path_sha256": "B",
        "gross_series_sha256": "C",
        "net_series_sha256": "D",
    }


def _source_candidate() -> tuple[dict[str, object], CandidateSpec]:
    ledger = REPO_ROOT / (
        "runtime/crypto_search_engine_v1_4_oi_flow_20260728/"
        "candidate_ledger.parquet"
    )
    import pandas as pd

    row = (
        pd.read_parquet(ledger)
        .loc[lambda value: value["stage"].eq("STAGE_B")]
        .sort_values("stage_completion_ordinal")
        .iloc[0]
        .to_dict()
    )
    return row, CandidateSpec.from_dict(
        json.loads(str(row["candidate_spec_json"]))
    )


def test_binance_open_target_keeps_two_hour_execution_delay() -> None:
    price = np.asarray([[1.0, 2.0, 4.0, 8.0, 16.0, 32.0]])
    target = _build_target_arrays(
        price, horizons=(1, 2), execution_delay=2
    )
    np.testing.assert_allclose(
        target[1][0, :3], np.log(np.asarray([2.0, 2.0, 2.0]))
    )
    np.testing.assert_allclose(
        target[2][0, :2], np.log(np.asarray([4.0, 4.0]))
    )
    assert np.isnan(target[1][0, 3:]).all()
    assert np.isnan(target[2][0, 2:]).all()


def test_replay_config_freezes_exact_candidate_only_boundary() -> None:
    config = json.loads(
        (
            REPO_ROOT
            / "config/crypto_search_engine_v1_4_binance_target_replay.json"
        ).read_text(encoding="utf-8")
    )
    assert config["strict_count"] == 1200
    assert config["checkpoint_size"] == 300
    assert config["target"]["venue"] == "BINANCE_USD_M"
    assert config["target"]["price_field"] == "open_price"
    assert (
        config["target"]["formula"]
        == "log(open_price[t+2+h] / open_price[t+2])"
    )
    assert config["evaluation"]["cost_bps"] == 5.0
    assert config["budget"]["new_candidate_generation"] == 0
    assert config["boundaries"]["adaptive_search"] is False
    assert config["boundaries"]["turnover_optimization"] is False
    assert set(PAIR_THRESHOLDS) == {
        "net_lcb",
        "worst_month",
        "positive_month_fraction",
        "turnover_mean",
        "cost_mean",
        "concentration_mean",
        "support",
    }


def test_full_waterfall_persists_binary_a_b_ab_and_deltas() -> None:
    source, candidate = _source_candidate()
    metric = _metrics()
    evaluation = {
        "hierarchical_three_axis": False,
        "control": metric,
        "right_control": metric,
        "primary": metric,
        "left_incremental": metric,
        "right_incremental": metric,
    }
    summary, monthly = _waterfall_rows(
        source_row=source,
        candidate=candidate,
        evaluation=evaluation,
    )
    assert [row["sleeve"] for row in summary] == [
        "A",
        "B",
        "AB",
        "AB_MINUS_A",
        "AB_MINUS_B",
    ]
    assert len(monthly) == 10
    assert all(row["gross_positive_month_fraction"] == 0.5 for row in summary)
