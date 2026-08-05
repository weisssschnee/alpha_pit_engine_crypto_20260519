from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

import alphafactory_crypto.broad_search.search_evidence_validation_v1 as validation_module
from alphafactory_crypto.broad_search.search_evidence_validation_v1 import (
    CONSENSUS_MAIN_CANDIDATE_IDS_SHA256,
    CONSENSUS_OTHER_CANDIDATE_IDS_SHA256,
    EXPECTED_SELECTION_SHA256,
    _aggregate_consensus_group,
    _align_target_to_economic_path_identity,
    _apply_checkpoint_projection_boundary,
    _build_summary,
    _canonical_sha256,
    _file_sha256,
    _line_sha256,
    _restore_consensus_checkpoint_paths,
    _selection_projection,
    finalize_consensus_checkpoint,
    load_consensus_receipt,
    load_validation_receipt,
    select_consensus_cohort,
    select_final_positive_champions,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
REPLACEMENT_RECEIPT = (
    "config/crypto_search_evidence_v1_1_validation_replacement_receipt.json"
)


def test_receipt_freezes_one_no_feedback_development_validation() -> None:
    receipt = load_validation_receipt(REPO_ROOT)
    assert receipt["run_authorized"] is False
    assert receipt["status"] == (
        "RUN_AUTHORIZATION_CONSUMED_ENGINE_RUNTIME_WRAPPER_FAILED"
    )
    assert receipt["selection"]["candidate_count_exact"] == 49
    assert receipt["selection"]["selection_sha256"] == EXPECTED_SELECTION_SHA256
    assert receipt["selection"]["backfill_allowed"] is False
    assert receipt["validation"] == {
        "start": "2025-11-01T00:00:00Z",
        "end_exclusive": "2026-01-01T00:00:00Z",
        "role": "DEVELOPMENT_VALIDATION_NO_FEEDBACK",
        "execution_venue": "BINANCE_USD_M",
        "cost_bps": 5.0,
    }
    assert receipt["compute"]["workers_default"] == 10
    assert receipt["compute"]["workers_fallback"] == 8
    assert receipt["boundaries"]["holdout_read"] is False
    assert receipt["boundaries"]["oos"] is False
    assert receipt["boundaries"]["promotion"] is False
    assert receipt["outcome"]["status"] == (
        "ENGINE_RUNTIME_WRAPPER_FAILED_NO_CHECKPOINT"
    )
    assert receipt["outcome"]["auditable_completed_candidate_count"] == 0
    assert receipt["outcome"]["restart_started"] is False


def test_exact_final_champion_selection_is_immutable_and_complete() -> None:
    rows = select_final_positive_champions(REPO_ROOT)
    assert len(rows) == 49
    assert len({row["candidate_id"] for row in rows}) == 49
    assert len({row["behavior_family_id"] for row in rows}) == 49
    assert all(float(row["search_reward"]) > 0.0 for row in rows)
    assert sum(str(row["arm"]) == "mechanism_evolution_v2_3" for row in rows) == 44
    assert sum(int(row["horizon_hours"]) == 4 for row in rows) == 43
    assert sum(int(row["declared_axis_count"]) == 2 for row in rows) == 36
    assert _canonical_sha256(_selection_projection(rows)) == EXPECTED_SELECTION_SHA256


def test_replacement_receipt_keeps_same_cohort_and_repairs_only_launcher() -> None:
    receipt = load_validation_receipt(
        REPO_ROOT,
        require_authorized=False,
        receipt_path=REPLACEMENT_RECEIPT,
    )
    rows = select_final_positive_champions(REPO_ROOT, receipt=receipt)
    assert receipt["receipt_id"] == (
        "CRYPTO_SEARCH_EVIDENCE_V1_1_VALIDATION_REPLACEMENT"
    )
    assert receipt["replacement_for"]["auditable_completed_candidate_count"] == 0
    assert receipt["selection"]["selection_sha256"] == EXPECTED_SELECTION_SHA256
    assert _canonical_sha256(_selection_projection(rows)) == EXPECTED_SELECTION_SHA256
    assert receipt["launcher"]["native_stderr_warning_terminal"] is False
    assert receipt["launcher"]["python_exit_code_terminal"] is True
    assert receipt["status"] == "RUN_AUTHORIZATION_CONSUMED_VALIDATION_COMPLETE"
    assert receipt["outcome"]["strict_evaluated_count"] == 49
    assert receipt["outcome"]["both_axis_net_lcb_positive_count"] == 0
    assert receipt["outcome"]["validation_behavior_family_identity_observed"] is False
    launcher = (
        REPO_ROOT / "scripts/crypto_search_evidence_validation_v1_pc2_launcher.ps1"
    ).read_text(encoding="utf-8")
    assert "Start-Process" in launcher
    assert "RedirectStandardError" in launcher
    assert "$process.ExitCode" in launcher
    assert "*>>" not in launcher


def test_summary_keeps_all_candidates_and_predeclared_primary_slice_separate() -> None:
    rows = []
    for ordinal in range(4):
        rows.append(
            {
                "strict_evaluated": ordinal != 3,
                "primary_analysis_slice": ordinal < 2,
                "arm": "evolution" if ordinal < 3 else "random",
                "horizon_hours": 4 if ordinal < 2 else 1,
                "validation_search_reward": 1.0 if ordinal == 0 else -1.0,
                "matched_positive": False,
                "validation_matched_positive": ordinal == 0,
                "primary_net_mean": -0.1,
                "validation_primary_net_mean": 0.1 if ordinal < 2 else -0.1,
                "validation_left_incremental_net_mean": 0.1,
                "validation_right_incremental_net_mean": 0.1 if ordinal == 0 else -0.1,
                "validation_left_incremental_net_lcb": 0.01,
                "validation_right_incremental_net_lcb": 0.01 if ordinal == 0 else -0.01,
                "train_search_reward": float(4 - ordinal),
            }
        )
    summary = _build_summary(rows)
    assert summary["all_49"]["source_count"] == 4
    assert summary["all_49"]["strict_evaluated_count"] == 3
    assert summary["all_49"]["candidate_local_failure_count"] == 1
    assert summary["all_49"]["matched_positive_count"] == 1
    assert summary["primary_4h_two_axis"]["source_count"] == 2
    assert summary["primary_4h_two_axis"]["both_axis_net_lcb_positive_count"] == 1
    assert summary["interpretation_boundary"].endswith("OOS_OR_PROMOTION")


def test_consensus_receipt_freezes_exact_cohorts_and_development_boundary() -> None:
    receipt = load_consensus_receipt(REPO_ROOT, require_authorized=False)
    assert receipt["run_authorized"] is False
    assert receipt["status"] == "OFFLINE_CHECKPOINT_PROJECTION_COMPLETE"
    assert receipt["source_implementation_sha"] == (
        "d3dd61844cd05ca01aba857d57a5abd29c2a5840"
    )
    assert receipt["development_fresh_interval"] == {
        "start": "2026-07-18T00:00:00Z",
        "end_exclusive": "2026-08-01T00:00:00Z",
        "hours": 336,
        "role": "SECOND_STAGE_DEVELOPMENT_FRESH_NO_FEEDBACK",
    }
    main_ids = receipt["cohort"]["main_candidate_ids"]
    other_ids = receipt["cohort"]["other_candidate_ids"]
    assert _line_sha256(main_ids) == CONSENSUS_MAIN_CANDIDATE_IDS_SHA256
    assert _line_sha256(other_ids) == CONSENSUS_OTHER_CANDIDATE_IDS_SHA256
    assert receipt["aggregation"]["leave_one_out_target_used"] is False
    assert receipt["boundaries"]["oos"] is False
    assert receipt["boundaries"]["promotion"] is False
    assert receipt["boundaries"]["second_run"] is False
    assert receipt["previous_outcome"]["status"] == (
        "ACQUISITION_FAILED_NO_CANDIDATE_GATE"
    )
    assert receipt["previous_outcome"]["successful_day_coordinates"] == 38
    assert receipt["previous_outcome"]["failed_day_coordinates"] == 4
    assert receipt["repair_authorization"]["redownload_successful_coordinates"] is False
    assert receipt["repair_authorization"]["candidate_gate_previously_started"] is False
    assert receipt["repair_authorization"]["candidate_gate_runs_authorized"] == 1
    assert receipt["repair_authorization"]["oos"] is False
    offline = receipt["offline_checkpoint_finalization_outcome"]
    assert offline["status"] == "FAMILY_CONSENSUS_CHECKPOINT_PROJECTION_COMPLETE"
    assert offline["market_read_count"] == 0
    assert offline["candidate_evaluation_count"] == 0
    assert offline["main_interpretation"] == "FAMILY_CONSENSUS_DID_NOT_TRANSFER"
    assert offline["interpretation_robust_to_projection_bound"] is True
    assert offline["independent_checker"] == "PASS"
    assert offline["oos"] is False
    assert offline["promotion"] is False
    assert receipt["outcome"]["status"] == (
        "FAMILY_CONSENSUS_AGGREGATION_FAILED_TARGET_SHAPE"
    )
    assert receipt["outcome"]["successful_day_coordinates"] == 42
    assert receipt["outcome"]["pre_repair_files_changed"] == 0
    assert receipt["outcome"]["strict_evaluated_count"] == 35
    assert receipt["outcome"]["aggregation_failure"] == (
        "FAMILY_CONSENSUS_TARGET_SHAPE_CHANGED"
    )
    assert receipt["outcome"]["consensus_result"] == "NOT_OBSERVED"
    assert receipt["outcome"]["second_candidate_gate_started"] is False


def test_consensus_cohort_is_exact_23_plus_12_without_validation_reselection() -> None:
    grouped = select_consensus_cohort(REPO_ROOT)
    assert len(grouped["main"]) == 23
    assert len(grouped["other"]) == 12
    assert _line_sha256(
        [row["candidate_id"] for row in grouped["main"]]
    ) == CONSENSUS_MAIN_CANDIDATE_IDS_SHA256
    assert _line_sha256(
        [row["candidate_id"] for row in grouped["other"]]
    ) == CONSENSUS_OTHER_CANDIDATE_IDS_SHA256
    assert all(int(row["horizon_hours"]) == 4 for rows in grouped.values() for row in rows)
    assert all(int(row["declared_axis_count"]) == 2 for rows in grouped.values() for row in rows)
    assert all(
        row["mechanism_family"] == "MECHANISM_V2_FLOW_INTENSITY_CONVICTION"
        and row["mapping_family"] == "TIME_SERIES_DIRECTIONAL_STATEFUL"
        for row in grouped["main"]
    )


def test_consensus_recomputes_from_equal_weight_paths_and_target_free_influence() -> None:
    hours = 48
    timestamp_ns = (
        np.datetime64("2026-07-18T00:00:00", "ns").astype(np.int64)
        + np.arange(hours, dtype=np.int64) * 3_600_000_000_000
    )
    target = np.tile(np.asarray([[0.002], [-0.002], [0.0]]), (1, hours))
    rows = [
        {"candidate_id": "A"},
        {"candidate_id": "B"},
    ]
    workers = []
    primary_weights = []
    for candidate_id, scale in (("A", 0.5), ("B", 0.3)):
        primary = np.tile(np.asarray([[scale], [-scale], [0.0]]), (1, hours))
        left = primary * 0.5
        right = primary * 0.25
        mask = np.ones(hours, dtype=bool)
        if candidate_id == "B":
            mask[0] = False
        sleeves = {
            "primary": {"weights": primary, "mask": np.ones(hours, dtype=bool)},
            "control_left": {"weights": left, "mask": np.ones(hours, dtype=bool)},
            "control_right": {"weights": right, "mask": mask},
        }
        workers.append(
            {
                "candidate_id": candidate_id,
                "error": None,
                "evaluation": {
                    "_economic_paths": {
                        "asset_ids": ["BTCUSDT", "ETHUSDT", "SOLUSDT"],
                        "timestamp_ns": timestamp_ns,
                        "cost_bps": 5.0,
                        "horizon_hours": 4,
                        "sleeves": sleeves,
                    }
                },
            }
        )
        primary_weights.append(primary)
    result = _aggregate_consensus_group(
        group="main", rows=rows, workers=workers, target=target
    )
    assert result["summary"]["member_count"] == 2
    assert result["summary"]["coefficient"] == 0.5
    assert result["summary"]["common_support_hours"] == 47
    assert all(row["target_used"] is False for row in result["influence_rows"])
    primary_asset_rows = [
        row
        for row in result["asset_rows"]
        if row["sleeve"] == "primary" and row["timestamp_ns"] == timestamp_ns[1]
    ]
    observed = {row["asset_id"]: row["weight"] for row in primary_asset_rows}
    expected = np.mean(np.stack(primary_weights, axis=0), axis=0)
    assert observed["BTCUSDT"] == expected[0, 1]
    assert observed["ETHUSDT"] == expected[1, 1]
    assert {row["sleeve"] for row in result["metric_rows"]} == {
        "primary",
        "control_left",
        "control_right",
        "primary_minus_left_control",
        "primary_minus_right_control",
    }


def test_consensus_target_alignment_uses_economic_path_timestamps() -> None:
    class TargetStore:
        symbols = ("BTCUSDT", "ETHUSDT")
        timestamp_ns = np.arange(54, dtype=np.int64) * 3_600_000_000_000

        @staticmethod
        def target_return(horizon_hours: int) -> np.ndarray:
            assert horizon_hours == 4
            return np.vstack(
                (
                    np.arange(54, dtype=float),
                    -np.arange(54, dtype=float),
                )
            )

    paths = {
        "asset_ids": ["BTCUSDT", "ETHUSDT"],
        "timestamp_ns": TargetStore.timestamp_ns[:48],
        "horizon_hours": 4,
    }
    target = _align_target_to_economic_path_identity(TargetStore(), paths)
    assert target.shape == (2, 48)
    np.testing.assert_array_equal(target, TargetStore.target_return(4)[:, :48])


def test_consensus_checkpoint_restore_rebuilds_target_without_market_read(
    tmp_path: Path,
) -> None:
    checkpoint = tmp_path / "checkpoint_000"
    timestamps = (
        np.datetime64("2026-07-18T00:00:00", "ns").astype(np.int64)
        + np.arange(48, dtype=np.int64) * 3_600_000_000_000
    )
    target = np.tile(np.asarray([[0.002], [-0.002]]), (1, timestamps.size))
    rows = []
    for ordinal, (candidate_id, scale, group) in enumerate(
        (("A" * 64, 0.5, "main"), ("B" * 64, 0.3, "other")), start=1
    ):
        rows.append(
            {
                "completion_ordinal": ordinal,
                "candidate_id": candidate_id,
                "consensus_group": group,
                "horizon_hours": 4,
                "economic_receipt_sha256": "E" * 64,
            }
        )
        local = checkpoint / "paths" / f"{ordinal - 1:04d}_{candidate_id[:16]}"
        local.mkdir(parents=True)
        hourly_rows = []
        position_rows = []
        for sleeve, multiplier in (
            ("primary", 1.0),
            ("control_left", 0.5),
            ("control_right", 0.25),
        ):
            weights = np.tile(
                np.asarray([[scale * multiplier], [-scale * multiplier]]),
                (1, timestamps.size),
            )
            if ordinal == 1 and sleeve == "primary":
                weights[0, 0] = 5.0e-16
            gross = np.nansum(weights * target, axis=0) / 4.0
            for time_index, timestamp in enumerate(timestamps):
                hourly_rows.append(
                    {
                        "candidate_id": candidate_id,
                        "horizon_hours": 4,
                        "execution_venue": "BINANCE_USD_M",
                        "economic_receipt_sha256": "E" * 64,
                        "evaluation_partition": "validation",
                        "sleeve": sleeve,
                        "timestamp_ns": int(timestamp),
                        "objective_mask": True,
                        "gross": float(gross[time_index]),
                    }
                )
                for asset_index, asset_id in enumerate(("BTCUSDT", "ETHUSDT")):
                    position = {
                            "candidate_id": candidate_id,
                            "horizon_hours": 4,
                            "execution_venue": "BINANCE_USD_M",
                            "economic_receipt_sha256": "E" * 64,
                            "evaluation_partition": "validation",
                            "sleeve": sleeve,
                            "timestamp_ns": int(timestamp),
                            "asset_id": asset_id,
                            "weight": float(weights[asset_index, time_index]),
                            "asset_gross_contribution": float(
                                weights[asset_index, time_index]
                                * target[asset_index, time_index]
                                / 4.0
                            ),
                        }
                    if (
                        abs(position["weight"]) > 1.0e-12
                        or abs(position["asset_gross_contribution"]) > 1.0e-18
                    ):
                        position_rows.append(position)
        pd.DataFrame(hourly_rows).to_parquet(
            local / "economic_hourly_sleeves.parquet", index=False
        )
        pd.DataFrame(position_rows).to_parquet(
            local / "economic_asset_positions.parquet", index=False
        )

    workers, restored_target, restoration = _restore_consensus_checkpoint_paths(
        checkpoint, rows, asset_capacity_upper_bound=150
    )
    assert restoration["market_read_count"] == 0
    assert restoration["timestamp_count"] == 48
    assert restoration["active_asset_count"] == 2
    assert restoration["asset_capacity_upper_bound"] == 150
    assert restoration["bit_exact_original_executable_weights"] is False
    assert restoration["max_incremental_net_mean_abs_error_bound"] == (
        4.0 * 150 * 1.0e-12 * 5.0 / 10_000.0 + 2.0 * 150 * 1.0e-18
    )
    restored_primary = workers[0]["evaluation"]["_economic_paths"]["sleeves"][
        "primary"
    ]["weights"]
    assert restored_primary[0, 0] == 0.0
    assert 5.0e-16 <= restoration["max_sleeve_weight_l1_error_bound"]
    assert 2.5e-19 <= restoration["max_sleeve_gross_path_abs_error_bound"]
    np.testing.assert_allclose(restored_target, target, rtol=0.0, atol=1.0e-15)
    result = _aggregate_consensus_group(
        group="all", rows=rows, workers=workers, target=restored_target
    )
    assert result["summary"]["member_count"] == 2
    assert result["summary"]["common_support_hours"] == 48


def test_checkpoint_projection_labels_only_bound_robust_negative_result() -> None:
    restoration = {"max_incremental_net_mean_abs_error_bound": 3.1e-13}
    decision = {
        "status": "FAMILY_CONSENSUS_GATE_COMPLETE",
        "main_consensus": {
            "left_incremental_net_mean": -1.0e-4,
            "right_incremental_net_mean": -2.0e-4,
        },
        "main_interpretation": "FAMILY_CONSENSUS_DID_NOT_TRANSFER",
    }
    bounded = _apply_checkpoint_projection_boundary(decision, restoration)
    assert bounded["status"] == "FAMILY_CONSENSUS_CHECKPOINT_PROJECTION_COMPLETE"
    assert bounded["interpretation_robust_to_projection_bound"] is True
    assert bounded["checkpoint_projection_boundary"][
        "net_lcb_is_point_estimate_only"
    ] is True

    decision["main_consensus"]["left_incremental_net_mean"] = -1.0e-14
    indeterminate = _apply_checkpoint_projection_boundary(decision, restoration)
    assert indeterminate["interpretation_robust_to_projection_bound"] is False
    assert indeterminate["main_interpretation"] == "CHECKPOINT_PROJECTION_INDETERMINATE"


def test_offline_finalizer_is_atomic_and_does_not_call_market_or_evaluator(
    tmp_path: Path, monkeypatch
) -> None:
    root = tmp_path / "repo"
    runtime = root / "runtime" / "crypto_search_family_consensus_dev_v1_20260805"
    checkpoint = runtime / "checkpoints" / "checkpoint_000"
    config = root / "config"
    checkpoint.mkdir(parents=True)
    config.mkdir(parents=True)
    receipt_path = config / "crypto_search_family_consensus_dev_v1_receipt.json"
    receipt_path.write_text('{"schema_version":1}\n', encoding="utf-8")

    candidate_ids = [f"{index:064X}" for index in range(35)]
    ledger = pd.DataFrame(
        {
            "completion_ordinal": np.arange(1, 36),
            "candidate_id": candidate_ids,
            "consensus_group": ["main"] * 23 + ["other"] * 12,
        }
    )
    checkpoint_ledger = checkpoint / "candidate_ledger.parquet"
    ledger.to_parquet(checkpoint_ledger, index=False)
    shutil.copy2(checkpoint_ledger, runtime / "candidate_ledger.parquet")
    carrier = {"manifest_sha256": "CARRIER"}
    (runtime / "aligned_carrier_manifest.json").write_text(
        json.dumps(carrier), encoding="utf-8"
    )
    manifest = {
        "files": [],
        "completed_candidate_count": 35,
        "strict_evaluated_count": 35,
        "candidate_local_failure_count": 0,
        "producer_source_sha": "PRODUCER",
        "selection_receipt_sha256": "SELECTION",
        "frozen_contract_sha256": "CONTRACT",
        "workers": 10,
        "memory_fallback_used": False,
    }
    manifest["manifest_sha256"] = _canonical_sha256(manifest)
    manifest_path = checkpoint / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True
    )
    subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "source"], cwd=root, check=True)
    source_sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True
    ).strip()

    authorization = {
        "authorized": True,
        "scope": "PERSISTED_CHECKPOINT_PATH_AGGREGATION_ONLY",
        "market_read_count": 0,
        "candidate_evaluation_count": 0,
        "candidate_generation": False,
        "optimizer_feedback": False,
        "archive_write": False,
        "oos": False,
        "promotion": False,
        "source_implementation_sha": source_sha,
        "source_component_sha256": _file_sha256(Path(validation_module.__file__)),
        "allowed_execution_head_changed_paths": [
            "config/crypto_search_family_consensus_dev_v1_receipt.json"
        ],
        "checkpoint_manifest_file_sha256": _file_sha256(manifest_path),
        "checkpoint_manifest_sha256": manifest["manifest_sha256"],
        "candidate_ledger_sha256": _file_sha256(checkpoint_ledger),
    }
    receipt = {
        "schema_version": 1,
        "offline_checkpoint_finalization": authorization,
    }
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    subprocess.run(["git", "add", str(receipt_path)], cwd=root, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "authorize"], cwd=root, check=True
    )

    grouped = {
        "main": [{"candidate_id": value} for value in candidate_ids[:23]],
        "other": [{"candidate_id": value} for value in candidate_ids[23:]],
    }
    restoration = {
        "market_read_count": 0,
        "candidate_count": 35,
        "timestamp_count": 330,
        "target_sha256": "TARGET",
        "max_incremental_net_mean_abs_error_bound": 1.0e-12,
    }
    summary = {
        "member_count": 23,
        "common_support_hours": 30,
        "left_incremental_net_mean": -1.0e-4,
        "right_incremental_net_mean": -2.0e-4,
        "left_incremental_net_lcb": -3.0e-4,
        "right_incremental_net_lcb": -4.0e-4,
        "both_axis_net_mean_positive": False,
        "both_axis_net_lcb_positive": False,
        "dual_axis_matched_positive": False,
    }
    decision = {
        "status": "FAMILY_CONSENSUS_GATE_COMPLETE",
        "producer_source_sha": "PRODUCER",
        "main_consensus": summary,
        "other_consensus_descriptive": {**summary, "member_count": 12},
        "main_interpretation": "FAMILY_CONSENSUS_DID_NOT_TRANSFER",
    }
    tables = {
        "consensus_metrics.parquet": [{"value": 1}],
        "consensus_hourly_paths.parquet": [{"value": 1}],
        "consensus_asset_weights.parquet": [{"value": 1}],
        "candidate_influence.parquet": [{"value": 1}],
        "consensus_concentration.parquet": [{"value": 1}],
    }
    sentinel_calls: list[str] = []

    def forbidden(*args, **kwargs):
        sentinel_calls.append("forbidden")
        raise AssertionError("market/evaluator path called")

    monkeypatch.setattr(validation_module, "load_consensus_receipt", lambda *a, **k: receipt)
    monkeypatch.setattr(validation_module, "select_consensus_cohort", lambda *a, **k: grouped)
    monkeypatch.setattr(validation_module, "_v24_checkpoint_files", lambda *a: [])
    monkeypatch.setattr(
        validation_module,
        "_checkpoint_asset_capacity_authority",
        lambda *a: {"asset_capacity_upper_bound": 150, "market_payload_read": False},
    )
    monkeypatch.setattr(
        validation_module,
        "_restore_consensus_checkpoint_paths",
        lambda *a, **k: ([], np.empty((0, 0)), restoration),
    )
    monkeypatch.setattr(
        validation_module,
        "_build_consensus_aggregation_result",
        lambda **kwargs: (decision, tables),
    )
    monkeypatch.setattr(validation_module, "_v24_worker_evaluate", forbidden)
    monkeypatch.setattr(validation_module, "_v24_worker_initialize", forbidden)
    monkeypatch.setattr(
        validation_module, "_align_target_to_economic_path_identity", forbidden
    )

    result = finalize_consensus_checkpoint(
        root, finalizer_source_sha=source_sha
    )
    terminal = runtime / "offline_finalization_v1"
    assert result["status"] == "FAMILY_CONSENSUS_CHECKPOINT_PROJECTION_COMPLETE"
    assert sentinel_calls == []
    assert terminal.is_dir()
    assert (terminal / "run_manifest.json").is_file()
    assert (terminal / "final_decision.json").is_file()
    assert not (runtime / "final_decision.json").exists()
    assert not list(runtime.glob("offline_finalization_v1.tmp-*"))
