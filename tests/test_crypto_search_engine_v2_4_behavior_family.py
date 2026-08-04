from __future__ import annotations

import json
import hashlib
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from alphafactory_crypto.broad_search.search_engine_v2_4 import (
    V24_CANDIDATE_LOCAL_FAILURES,
    _v24_failure_reason,
    _v24_mark_equal_count_comparison,
    _v24_write_batch_projections,
    _v24_write_candidate_failure_projection,
    build_economic_path_artifacts,
    freeze_v24_gate_selection,
    load_v24_run_receipt,
    load_v24_contract,
    prepare_v24_train_rows,
    persist_v24_gate_bundle,
    select_behavior_family_cohort,
    select_behavior_family_champions,
    sweep_v24_static_constructibility,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_v24_one_time_receipt_binds_exact_budget_and_fresh_interval() -> None:
    receipt = load_v24_run_receipt(REPO_ROOT, require_authorized=False)
    assert receipt["experiment_id"] == "crypto_search_engine_v2_4_fresh_family_gate"
    assert receipt["selection"]["per_cell_count"] == 64
    assert receipt["selection"]["cell_count"] == 8
    assert receipt["selection"]["candidate_count_exact"] == 512
    assert receipt["fresh_validation"] == {
        "start": "2026-07-01T00:00:00Z",
        "end_exclusive": "2026-07-18T00:00:00Z",
        "role": "FRESH_DATA_VALIDATION_V2_4",
        "execution_venue": "BINANCE_USD_M",
        "baseline_cost_bps": 5.0,
        "cost_sensitivity_bps": [5.0, 10.0],
    }
    assert receipt["compute"]["workers_default"] == 10
    assert receipt["compute"]["workers_memory_fallback"] == 8
    assert receipt["compute"]["workers_12_forbidden"] is True
    assert receipt["compute"]["evaluation_wall_time_seconds_maximum"] == 14400
    assert receipt["compute"]["minimum_pair_evaluated_per_hour"] == 128.0


def test_v24_static_sweep_recompiles_all_frozen_candidates_without_market_read() -> None:
    runtime_root = (
        REPO_ROOT / "runtime" / "crypto_search_engine_v2_4_fresh_gate_20260803"
    )
    selection = json.loads(
        (runtime_root / "behavior_family_selection_receipt.json").read_text()
    )
    carrier = json.loads(
        (runtime_root / "aligned_carrier_manifest.json").read_text()
    )
    ledger = pd.read_parquet(
        REPO_ROOT
        / "runtime"
        / "crypto_search_mechanism_v2_3_20260802"
        / "candidate_ledger.parquet"
    ).set_index("candidate_id")
    selected_rows = []
    for frozen in selection["selected_candidates"]:
        row = ledger.loc[str(frozen["candidate_id"])]
        selected_rows.append(
            {
                **dict(frozen),
                "candidate": json.loads(str(row["candidate_spec_json"])),
            }
        )
    sweep = sweep_v24_static_constructibility(
        selected_rows=selected_rows,
        contract_rows=carrier["contracts"],
    )
    assert sweep["status"] == "PASS_V24_STATIC_CONSTRUCTIBILITY_SWEEP"
    assert sweep["market_read_performed"] is False
    assert sweep["candidate_count"] == sweep["unique_candidate_count"] == 512


def test_v24_candidate_local_failure_is_persisted_without_backfill() -> None:
    selected = {
        "candidate_id": "candidate-1",
        "candidate_spec_sha256": "A" * 64,
        "behavior_family_id": "family-1",
        "arm": "expanded_mechanism_random_v2_4",
        "source_arm": "expanded_mechanism_random_v2_3",
        "seed": 359914106,
        "horizon_hours": 1,
        "search_reward": 0.5,
        "train_orientation": 1.0,
    }
    worker = {
        "candidate_id": "candidate-1",
        "error": "ValueError:CONTROL_BEHAVIOR_EQUALS_PRIMARY",
        "process_cpu_seconds": 1.5,
        "wall_seconds": 2.0,
        "worker_rss_bytes": 10,
        "worker_private_bytes": 12,
    }
    row = _v24_write_candidate_failure_projection(
        ordinal=0,
        selected=selected,
        worker=worker,
        economic_receipt_sha256="E" * 64,
    )
    assert row["candidate_id"] == "candidate-1"
    assert row["validation_status"] == "CANDIDATE_LOCAL_FAILURE"
    assert row["validation_failure_reason"] in V24_CANDIDATE_LOCAL_FAILURES
    assert row["strict_evaluated"] is False
    assert row["comparison_included"] is False
    with pytest.raises(RuntimeError, match="V24_UNEXPECTED_CANDIDATE_FAILURE"):
        _v24_failure_reason(
            {"error": "ValueError:UNREGISTERED_CANDIDATE_FAILURE"}
        )


def test_v24_repair_batch_continues_after_candidate_local_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def success_projection(
        root: Path,
        *,
        ordinal: int,
        selected: dict,
        worker: dict,
        economic_receipt_sha256: str,
    ) -> dict:
        del root, worker, economic_receipt_sha256
        return {
            "completion_ordinal": ordinal + 1,
            "candidate_id": selected["candidate_id"],
            "strict_evaluated": True,
            "validation_status": "EVALUATED",
        }

    monkeypatch.setattr(
        "alphafactory_crypto.broad_search.search_engine_v2_4."
        "_v24_write_candidate_projection",
        success_projection,
    )
    base = {
        "candidate_spec_sha256": "A" * 64,
        "behavior_family_id": "family",
        "arm": "expanded_mechanism_random_v2_4",
        "source_arm": "expanded_mechanism_random_v2_3",
        "seed": 359914106,
        "horizon_hours": 1,
        "search_reward": 0.5,
        "train_orientation": 1.0,
    }
    selected = [
        {**base, "candidate_id": "candidate-failed"},
        {**base, "candidate_id": "candidate-evaluated"},
    ]
    workers = [
        {
            "candidate_id": "candidate-failed",
            "error": "ValueError:CONTROL_BEHAVIOR_EQUALS_PRIMARY",
            "process_cpu_seconds": 1.0,
            "wall_seconds": 1.0,
            "worker_rss_bytes": 10,
            "worker_private_bytes": 10,
        },
        {"candidate_id": "candidate-evaluated", "error": None},
    ]
    projected = _v24_write_batch_projections(
        tmp_path,
        base_ordinal=0,
        selected_rows=selected,
        worker_rows=workers,
        economic_receipt_sha256="E" * 64,
        persist_candidate_local_failures=True,
    )
    assert [row["candidate_id"] for row in projected] == [
        "candidate-failed",
        "candidate-evaluated",
    ]
    assert [row["strict_evaluated"] for row in projected] == [False, True]


def test_v24_equal_count_comparison_uses_source_ordinal_without_backfill() -> None:
    rows = []
    ordinal = 0
    for seed in (359914106, 1141399971):
        for horizon in (1, 4):
            for arm, count in (
                ("expanded_mechanism_random_v2_4", 3),
                ("mechanism_evolution_v2_4", 2),
            ):
                for local in range(count):
                    ordinal += 1
                    rows.append(
                        {
                            "completion_ordinal": ordinal,
                            "candidate_id": f"candidate-{ordinal}",
                            "arm": arm,
                            "seed": seed,
                            "horizon_hours": horizon,
                            "strict_evaluated": True,
                        }
                    )
    marked, counts = _v24_mark_equal_count_comparison(rows)
    assert counts == {
        "359914106:1": 2,
        "359914106:4": 2,
        "1141399971:1": 2,
        "1141399971:4": 2,
    }
    compared = [row for row in marked if row["comparison_included"]]
    assert len(compared) == 16
    assert all(
        sum(
            row["comparison_included"]
            for row in marked
            if row["arm"] == arm
            and row["seed"] == seed
            and row["horizon_hours"] == horizon
        )
        == 2
        for arm in (
            "expanded_mechanism_random_v2_4",
            "mechanism_evolution_v2_4",
        )
        for seed in (359914106, 1141399971)
        for horizon in (1, 4)
    )


def test_v24_one_time_receipt_is_consumed_by_exact_blocked_outcome() -> None:
    receipt = load_v24_run_receipt(REPO_ROOT, require_authorized=False)
    assert receipt["status"] == (
        "RUN_AUTHORIZATION_CONSUMED_ENGINE_VALIDATION_BLOCKED"
    )
    assert receipt["run_authorized"] is False
    assert receipt["outcome"] == {
        "status": "ENGINE_VALIDATION_BLOCKED",
        "producer_status": "V24_FRESH_GATE_FAILED_CANDIDATE_LOCAL",
        "producer_source_sha": "83a38d56fc2b362aed65ba246ea3fbd7993dfc4a",
        "runtime_path": "runtime/crypto_search_engine_v2_4_fresh_gate_20260803",
        "selection_receipt_sha256": (
            "DDD90D0F15CC7F54BA723D3E9C14274BB83F8FD186065374770C8C3205D4CD48"
        ),
        "selected_candidate_count": 512,
        "failure_candidate_id": (
            "949A5E2EDAE1E2117B9C9E49C9ABCA229F7E080A429285D3A57D0FFFBAF40D37"
        ),
        "failure_reason": "ValueError:CONTROL_BEHAVIOR_EQUALS_PRIMARY",
        "strict_evaluated_count": 0,
        "checkpoint_count": 0,
        "workers": 10,
        "memory_fallback_used": False,
        "carrier_qualification": "PASS",
        "carrier_field_count": 115,
        "carrier_identity_sha256": (
            "56C3F44FCF374ECB3A14927C32CA582F139FBA7C2A0F38CB083C151A47183CC8"
        ),
        "aligned_carrier_manifest_sha256": (
            "A709DF8F5E4ABE598DD88C89647CC27C76936FCD4F60A0961254719983D5429B"
        ),
        "arm_qualified": [],
        "candidate_generation_performed": False,
        "optimizer_feedback_written": False,
        "policy_memory_written": False,
        "archive_written": False,
        "sealed_read_count": 0,
        "oos": False,
        "promotion_authorized": False,
        "research_interpretation": (
            "VALIDATION_CONSTRUCTIBILITY_BLOCK_ONLY_NOT_ALPHA_OR_CARRIER_NEGATIVE"
        ),
    }
    with pytest.raises(RuntimeError, match="V24_RUN_RECEIPT_BLOCKED"):
        load_v24_run_receipt(REPO_ROOT, require_authorized=True)


def test_v24_terminal_artifacts_preserve_fail_closed_boundaries() -> None:
    runtime_root = (
        REPO_ROOT / "runtime" / "crypto_search_engine_v2_4_fresh_gate_20260803"
    )
    producer = json.loads((runtime_root / "producer_status.json").read_text())
    decision = json.loads((runtime_root / "final_decision.json").read_text())
    checker = json.loads(
        (runtime_root / "independent_terminal_check.local.json").read_text()
    )
    assert producer["status"] == "V24_FRESH_GATE_FAILED_CANDIDATE_LOCAL"
    assert decision["status"] == "ENGINE_VALIDATION_BLOCKED"
    assert checker["status"] == "PASS_V24_TERMINAL_BLOCKED_INDEPENDENT_CHECK"
    for artifact in (producer, decision, checker):
        completed = artifact.get(
            "strict_evaluated_count", artifact.get("completed_candidate_count")
        )
        assert completed == 0
    assert decision["checkpoint_count"] == checker["checkpoint_count"] == 0
    assert decision["arm_qualified"] == checker["arm_qualified"] == []
    assert decision["sealed_read_count"] == checker["sealed_read_count"] == 0
    assert decision["oos"] is checker["oos"] is False
    assert decision["promotion_authorized"] is False
    assert decision["next_search_started"] is False
    manifest = json.loads((runtime_root / "run_manifest.json").read_text())
    observed_files = []
    for row in manifest["files"]:
        payload = (runtime_root / row["path"]).read_bytes()
        assert len(payload) == row["bytes"]
        assert hashlib.sha256(payload).hexdigest().upper() == row["sha256"]
        observed_files.append(row)
    bundle_payload = json.dumps(
        observed_files,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    assert hashlib.sha256(bundle_payload).hexdigest().upper() == (
        manifest["artifact_bundle_sha256"]
    )


def test_v24_train_rows_map_only_frozen_v23_arms_without_changing_candidates() -> None:
    rows = [
        {
            "candidate_id": "random-1",
            "behavior_family_id": "family-r",
            "arm": "expanded_mechanism_random_v2_3",
            "seed": 11,
            "horizon_hours": 1,
            "search_reward": 1.0,
            "arm_completion_ordinal": 2,
            "candidate_spec_json": json.dumps({"candidate_id": "random-1"}),
            "train_orientation": 1.0,
        },
        {
            "candidate_id": "evolution-1",
            "behavior_family_id": "family-e",
            "arm": "mechanism_evolution_v2_3",
            "seed": 22,
            "horizon_hours": 4,
            "search_reward": 2.0,
            "arm_completion_ordinal": 3,
            "candidate_spec_json": json.dumps({"candidate_id": "evolution-1"}),
            "train_orientation": -1.0,
        },
    ]
    mapped = prepare_v24_train_rows(
        rows,
        source_arm_mapping={
            "expanded_mechanism_random_v2_3": "expanded_mechanism_random_v2_4",
            "mechanism_evolution_v2_3": "mechanism_evolution_v2_4",
        },
    )
    assert [row["candidate_id"] for row in mapped] == ["random-1", "evolution-1"]
    assert [row["arm"] for row in mapped] == [
        "expanded_mechanism_random_v2_4",
        "mechanism_evolution_v2_4",
    ]
    assert [row["source_arm"] for row in mapped] == [
        "expanded_mechanism_random_v2_3",
        "mechanism_evolution_v2_3",
    ]
    with pytest.raises(RuntimeError, match="SOURCE_ARM_SET_CHANGED"):
        prepare_v24_train_rows(
            [*rows, {**rows[0], "candidate_id": "other", "arm": "other"}],
            source_arm_mapping={
                "expanded_mechanism_random_v2_3": "expanded_mechanism_random_v2_4",
                "mechanism_evolution_v2_3": "mechanism_evolution_v2_4",
            },
        )


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
            "authority": "PAIR18M_EXISTING_MAPPING_COST_EVALUATOR_PATH_PROJECTION_V1",
            "candidate_id": "candidate-1",
            "candidate_spec_sha256": "C" * 64,
            "economic_receipt_sha256": "E" * 64,
            "evaluation_partition": "validation",
            "execution_venue": "BINANCE_USD_M",
            "asset_ids": ["BTCUSDT", "ETHUSDT"],
            "timestamp_ns": timestamps,
            "horizon_hours": 1,
            "cost_bps": 5.0,
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
        candidate_spec_sha256="C" * 64,
        economic_receipt_sha256="E" * 64,
        evaluation_partition="validation",
        execution_venue="BINANCE_USD_M",
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
                "candidate_spec_json": json.dumps(
                    {
                        "candidate_id": candidate_id,
                        "horizon_hours": 1,
                        "arm": arm,
                    },
                    sort_keys=True,
                ),
            }
        )
    producer_source_sha = load_v24_run_receipt(
        REPO_ROOT,
        require_authorized=False,
    )["source_implementation_sha"]
    selection_receipt_path = tmp_path / "selection_receipt.json"
    freeze_v24_gate_selection(
        repo_root=REPO_ROOT,
        receipt_path=selection_receipt_path,
        train_rows=train_rows,
        expected_cells=(
            ("expanded_mechanism_random_v2_4", 11, 1),
            ("mechanism_evolution_v2_4", 11, 1),
        ),
        per_cell_count=1,
        producer_source_sha=producer_source_sha,
        evaluation_start="2026-07-01T00:00:00Z",
        evaluation_end_exclusive="2026-07-02T00:00:00Z",
        economic_receipt_sha256="E" * 64,
        evaluation_partition="validation",
        execution_venue="BINANCE_USD_M",
    )
    evaluations = []
    for arm_index, arm in enumerate(
        ("expanded_mechanism_random_v2_4", "mechanism_evolution_v2_4")
    ):
        candidate_id = f"candidate-{arm_index}"
        candidate_spec_sha256 = hashlib.sha256(
            json.dumps(
                {
                    "candidate_id": candidate_id,
                    "horizon_hours": 1,
                    "arm": arm,
                },
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
            ).encode("utf-8")
        ).hexdigest().upper()
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
                    "authority": (
                        "PAIR18M_EXISTING_MAPPING_COST_EVALUATOR_"
                        "PATH_PROJECTION_V1"
                    ),
                    "candidate_id": candidate_id,
                    "candidate_spec_sha256": candidate_spec_sha256,
                    "economic_receipt_sha256": "E" * 64,
                    "evaluation_partition": "validation",
                    "execution_venue": "BINANCE_USD_M",
                    "asset_ids": ["BTCUSDT"],
                    "timestamp_ns": timestamps,
                    "raw_fields": ["volume_imbalance"],
                    "horizon_hours": 1,
                    "cost_bps": 5.0,
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
        selection_receipt_path=selection_receipt_path,
        evaluations=evaluations,
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
