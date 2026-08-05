from __future__ import annotations

from pathlib import Path

import numpy as np

from alphafactory_crypto.broad_search.search_evidence_validation_v1 import (
    CONSENSUS_MAIN_CANDIDATE_IDS_SHA256,
    CONSENSUS_OTHER_CANDIDATE_IDS_SHA256,
    EXPECTED_SELECTION_SHA256,
    _aggregate_consensus_group,
    _build_summary,
    _canonical_sha256,
    _line_sha256,
    _selection_projection,
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
    assert receipt["status"] == (
        "RUN_AUTHORIZATION_CONSUMED_ACQUISITION_FAILED_NO_GATE"
    )
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
    assert receipt["outcome"]["status"] == "ACQUISITION_FAILED_NO_CANDIDATE_GATE"
    assert receipt["outcome"]["scheduled_day_coordinates"] == 42
    assert receipt["outcome"]["successful_day_coordinates"] == 38
    assert receipt["outcome"]["failed_day_coordinates"] == 4
    assert receipt["outcome"]["candidate_gate_started"] is False
    assert receipt["outcome"]["strict_evaluated_count"] == 0
    assert receipt["outcome"]["consensus_result"] == "NOT_OBSERVED"
    assert receipt["outcome"]["restart_started"] is False


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
