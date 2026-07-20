from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from alphafactory_crypto.broad_search.acceleration_canary import (
    _aggregate_scheduler_trials,
    _select_worker_limit,
    _semantic_projection,
    _trim_decision,
    validate_config,
)


ROOT = Path(__file__).parents[1]


def _config() -> dict:
    return json.loads((ROOT / "config/crypto_policy_acceleration_canary_v1.json").read_text())


def test_contract_is_eight_fixed_pairs_and_closed_boundaries() -> None:
    config = _config()
    validate_config(config)
    assert len(config["candidates"]) == 8
    assert config["scheduler"]["worker_counts"] == [8, 10, 12]
    assert config["scheduler"]["task_count"] == 20
    assert config["scheduler"]["pairs_per_task"] == 4
    changed = deepcopy(config)
    changed["boundaries"]["policy_feedback"] = True
    with pytest.raises(PermissionError, match="boundary opened"):
        validate_config(changed)


def test_semantic_projection_ignores_only_timings() -> None:
    first = {"candidate_id": "A", "pair_reward": 1.0, "timings": {"seconds": 1.0}}
    second = {"candidate_id": "A", "pair_reward": 1.0, "timings": {"seconds": 9.0}}
    assert _semantic_projection(first) == _semantic_projection(second)
    second["pair_reward"] = 2.0
    assert _semantic_projection(first) != _semantic_projection(second)


def test_worker_limit_is_smallest_configuration_within_five_percent_of_best() -> None:
    stats = [
        {"worker_count": 8, "pairs_per_second": 0.80, "eligible": True},
        {"worker_count": 10, "pairs_per_second": 0.97, "eligible": True},
        {"worker_count": 12, "pairs_per_second": 1.00, "eligible": True},
    ]
    assert _select_worker_limit(stats, 0.95) == 10
    stats[1]["eligible"] = False
    assert _select_worker_limit(stats, 0.95) == 12


def test_trim_decision_matches_original_baseline_and_threshold_lane_boundary() -> None:
    assert _trim_decision(
        "PER_PAIR_FULL_TRIM",
        current_rss=1,
        rss_threshold_bytes=100,
        is_lane_boundary=False,
    ) == (True, False)
    assert _trim_decision(
        "RSS_THRESHOLD_PLUS_LANE_BOUNDARY",
        current_rss=99,
        rss_threshold_bytes=100,
        is_lane_boundary=False,
    ) == (False, False)
    assert _trim_decision(
        "RSS_THRESHOLD_PLUS_LANE_BOUNDARY",
        current_rss=99,
        rss_threshold_bytes=100,
        is_lane_boundary=True,
    ) == (True, False)
    assert _trim_decision(
        "RSS_THRESHOLD_PLUS_LANE_BOUNDARY",
        current_rss=100,
        rss_threshold_bytes=100,
        is_lane_boundary=True,
    ) == (True, True)


def test_scheduler_aggregation_uses_two_trial_median_and_all_trial_eligibility() -> None:
    trials = []
    for worker_count, rates in ((8, (0.8, 0.9)), (10, (1.0, 1.1)), (12, (1.2, 1.0))):
        for index, rate in enumerate(rates):
            trials.append(
                {
                    "worker_count": worker_count,
                    "pair_count": 80,
                    "pairs_per_second": rate,
                    "maximum_worker_peak_rss_bytes": 100 + index,
                    "estimated_aggregate_peak_rss_bytes": 1000 + index,
                    "semantic_parity": "PASS",
                    "native_trim_pass": True,
                    "eligible": not (worker_count == 12 and index == 1),
                }
            )
    aggregated = _aggregate_scheduler_trials(trials, [8, 10, 12])
    assert [row["pairs_per_second"] for row in aggregated] == pytest.approx(
        [0.85, 1.05, 1.1]
    )
    assert [row["eligible"] for row in aggregated] == [True, True, False]
