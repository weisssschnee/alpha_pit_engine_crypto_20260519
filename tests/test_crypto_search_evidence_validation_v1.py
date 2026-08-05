from __future__ import annotations

from pathlib import Path

from alphafactory_crypto.broad_search.search_evidence_validation_v1 import (
    EXPECTED_SELECTION_SHA256,
    _build_summary,
    _canonical_sha256,
    _selection_projection,
    load_validation_receipt,
    select_final_positive_champions,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


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
                "matched_positive": ordinal == 0,
                "primary_net_mean": 0.1 if ordinal < 2 else -0.1,
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
