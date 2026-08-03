from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import numpy as np
import pytest

from alphafactory_crypto.broad_search.search_engine_v2_4 import (
    build_economic_path_artifacts,
    load_v24_contract,
    persist_v24_gate_bundle,
    select_behavior_family_cohort,
    select_behavior_family_champions,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_behavior_family_champion_selection_gives_each_family_one_vote() -> None:
    rows = [
        {
            "candidate_id": "a-low",
            "behavior_family_id": "family-a",
            "arm": "mechanism_evolution_v2_4",
            "seed": 11,
            "horizon_hours": 1,
            "search_reward": 1.0,
            "arm_completion_ordinal": 1,
        },
        {
            "candidate_id": "a-high",
            "behavior_family_id": "family-a",
            "arm": "mechanism_evolution_v2_4",
            "seed": 11,
            "horizon_hours": 1,
            "search_reward": 3.0,
            "arm_completion_ordinal": 8,
        },
        {
            "candidate_id": "b-late",
            "behavior_family_id": "family-b",
            "arm": "mechanism_evolution_v2_4",
            "seed": 11,
            "horizon_hours": 1,
            "search_reward": 2.0,
            "arm_completion_ordinal": 7,
        },
        {
            "candidate_id": "b-early",
            "behavior_family_id": "family-b",
            "arm": "mechanism_evolution_v2_4",
            "seed": 11,
            "horizon_hours": 1,
            "search_reward": 2.0,
            "arm_completion_ordinal": 3,
        },
        {
            "candidate_id": "a-other-horizon",
            "behavior_family_id": "family-a",
            "arm": "mechanism_evolution_v2_4",
            "seed": 11,
            "horizon_hours": 4,
            "search_reward": 9.0,
            "arm_completion_ordinal": 2,
        },
    ]
    selected, receipt = select_behavior_family_champions(rows)
    assert [row["candidate_id"] for row in selected] == [
        "a-high",
        "b-early",
        "a-other-horizon",
    ]
    assert len({
        (row["arm"], row["seed"], row["horizon_hours"], row["behavior_family_id"])
        for row in selected
    }) == len(selected)
    assert receipt["input_expression_count"] == 5
    assert receipt["selected_behavior_family_count"] == 3
    assert receipt["duplicate_expression_count"] == 2
    assert receipt["selection_authority"] == "TRAIN_SEARCH_REWARD_ONLY"
    assert len(receipt["selection_sha256"]) == 64


def test_behavior_family_cohort_is_equal_count_and_never_duplicate_backfilled() -> None:
    rows = []
    for seed in (11, 22):
        for family in range(3):
            for duplicate in range(family + 1):
                rows.append(
                    {
                        "candidate_id": f"{seed}-{family}-{duplicate}",
                        "behavior_family_id": f"family-{family}",
                        "arm": "mechanism_evolution_v2_4",
                        "seed": seed,
                        "horizon_hours": 1,
                        "search_reward": float(family + duplicate / 10.0),
                        "arm_completion_ordinal": family * 10 + duplicate,
                    }
                )
    selected, receipt = select_behavior_family_cohort(
        rows,
        per_cell_count=2,
        expected_cells=(
            ("mechanism_evolution_v2_4", 11, 1),
            ("mechanism_evolution_v2_4", 22, 1),
        ),
    )
    assert len(selected) == 4
    assert Counter((row["seed"], row["horizon_hours"]) for row in selected) == {
        (11, 1): 2,
        (22, 1): 2,
    }
    assert receipt["duplicate_family_backfill_used"] is False
    assert all(row["selected_family_count"] == 2 for row in receipt["cell_proof"])
    with pytest.raises(RuntimeError, match="CELL_SET_CHANGED"):
        select_behavior_family_cohort(
            rows,
            per_cell_count=2,
            expected_cells=(
                ("mechanism_evolution_v2_4", 11, 1),
                ("mechanism_evolution_v2_4", 22, 1),
                ("mechanism_evolution_v2_4", 33, 1),
            ),
        )


def test_complete_economic_paths_project_to_daily_and_sparse_asset_tables() -> None:
    timestamps = (
        np.datetime64("2026-07-01T00:00:00", "ns").astype(np.int64)
        + np.arange(48, dtype=np.int64) * 3_600_000_000_000
    )
    weights = np.zeros((2, 48), dtype=float)
    weights[0, :24] = 0.5
    weights[1, 24:] = -0.5
    gross_by_asset = weights * 0.001
    gross = gross_by_asset.sum(axis=0)
    turnover = np.full(48, 0.2)
    cost = turnover * 5.0 / 10_000.0
    net = gross - cost
    evaluation = {
        "candidate_id": "candidate-1",
        "_economic_paths": {
            "schema_version": 1,
            "execution_venue": "BINANCE_USD_M",
            "asset_ids": ["BTCUSDT", "ETHUSDT"],
            "timestamp_ns": timestamps,
            "sleeves": {
                "primary": {
                    "weights": weights,
                    "asset_gross_contribution": gross_by_asset,
                    "gross": gross,
                    "cost": cost,
                    "turnover": turnover,
                    "net": net,
                    "mask": np.ones(48, dtype=bool),
                }
            },
        },
    }
    artifacts = build_economic_path_artifacts(
        evaluation,
        cohort="evolution_train_top",
        arm="mechanism_evolution_v2_4",
        seed=11,
        horizon_hours=1,
    )
    hourly = artifacts["hourly_sleeves"]
    daily = artifacts["daily_sleeves"]
    positions = artifacts["asset_positions"]
    assert len(hourly) == 48
    assert all("objective_mask" in row for row in hourly)
    assert all("net_10bps" in row for row in hourly)
    assert len(daily) == 2
    assert len(positions) == 48
    assert {row["execution_venue"] for row in daily + positions} == {
        "BINANCE_USD_M"
    }
    assert all(row["gross"] - row["cost"] == row["net"] for row in daily)
    assert {row["asset_id"] for row in positions} == {"BTCUSDT", "ETHUSDT"}


def test_v24_gate_adapter_atomically_persists_selection_and_complete_paths(
    tmp_path: Path,
) -> None:
    train_rows = []
    evaluations = []
    timestamps = (
        np.datetime64("2026-07-01T00:00:00", "ns").astype(np.int64)
        + np.arange(4, dtype=np.int64) * 3_600_000_000_000
    )
    for arm_index, arm in enumerate(
        ("expanded_mechanism_random_v2_4", "mechanism_evolution_v2_4")
    ):
        candidate_id = f"candidate-{arm_index}"
        train_rows.append(
            {
                "candidate_id": candidate_id,
                "behavior_family_id": f"family-{arm_index}",
                "arm": arm,
                "seed": 11,
                "horizon_hours": 1,
                "search_reward": float(arm_index),
                "arm_completion_ordinal": 1,
            }
        )
        weights = np.full((1, 4), 0.5, dtype=float)
        gross_by_asset = weights * 0.001
        gross = gross_by_asset.sum(axis=0)
        turnover = np.full(4, 0.2)
        cost = turnover * 5.0 / 10_000.0
        evaluations.append(
            {
                "candidate_id": candidate_id,
                "_economic_paths": {
                    "schema_version": 1,
                    "execution_venue": "BINANCE_USD_M",
                    "asset_ids": ["BTCUSDT"],
                    "timestamp_ns": timestamps,
                    "raw_fields": ["volume_imbalance"],
                    "sleeves": {
                        "primary": {
                            "weights": weights,
                            "asset_gross_contribution": gross_by_asset,
                            "gross": gross,
                            "cost": cost,
                            "turnover": turnover,
                            "net": gross - cost,
                            "mask": np.ones(4, dtype=bool),
                        }
                    },
                },
            }
        )
    output = tmp_path / "v24_bundle"
    manifest = persist_v24_gate_bundle(
        repo_root=REPO_ROOT,
        output_root=output,
        train_rows=train_rows,
        evaluations=evaluations,
        expected_cells=(
            ("expanded_mechanism_random_v2_4", 11, 1),
            ("mechanism_evolution_v2_4", 11, 1),
        ),
        per_cell_count=1,
        producer_source_sha="a" * 40,
    )
    assert manifest["status"] == "V24_GATE_BUNDLE_COMPLETE"
    assert manifest["selected_behavior_family_count"] == 2
    assert manifest["evaluation_count"] == 2
    assert (output / "manifest.json").is_file()
    assert (output / "behavior_family_selection_receipt.json").is_file()
    assert (output / "economic_hourly_sleeves.parquet").is_file()
    assert (output / "economic_asset_positions.parquet").is_file()
    assert not list(tmp_path.glob("v24_bundle.tmp-*"))


def test_v24_contract_is_source_only_and_requires_fresh_data() -> None:
    contract = load_v24_contract(REPO_ROOT)
    assert contract["status"] == "SOURCE_IMPLEMENTED_RUN_NOT_AUTHORIZED"
    assert contract["run_authorized"] is False
    assert contract["fresh_data_gate"]["prior_holdout_end_exclusive"] == (
        "2026-07-01T00:00:00Z"
    )
    assert contract["fresh_data_gate"]["candidate_generation_during_gate"] is False
    assert contract["selection"]["unit"] == "BEHAVIOR_FAMILY"
    assert contract["selection"]["champion_order"] == [
        "search_reward_desc",
        "arm_completion_ordinal_asc",
        "candidate_id_asc",
    ]
    assert contract["economic_path_artifacts"]["required"] is True
    assert contract["boundaries"] == {
        "market_search": False,
        "sealed_read": False,
        "oos": False,
        "forward": False,
        "recent": False,
        "challenge": False,
        "promotion": False,
        "new_evaluator": False,
        "new_ast": False,
        "new_compiler": False,
        "cross_sprint_adaptive_memory": False,
    }
