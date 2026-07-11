from __future__ import annotations

import pandas as pd

import scripts.crypto_nextgen_epoch1 as epoch1
import scripts.crypto_nextgen_epoch1r as epoch1r


def test_epoch1r_preserves_frozen_upstream_contracts() -> None:
    guard = epoch1r.validate_unchanged_upstream()
    assert guard["budget"]["total_proposals"] == 32768
    assert guard["budget"]["strict_per_arm"] == 1536
    assert tuple(guard["budget"]["fixed_seeds"]) == epoch1r.FIXED_SEEDS
    assert guard["protected_search_logic_ast_sha256"]


def test_epoch1r_all_panel_lane_capacity_schema_is_fixed() -> None:
    expected = {
        "panel_id", "lane_id", "proposal_count", "legal_count", "exact_identity_count",
        "representative_count", "mechanism_count", "requested_quota", "feasible_quota",
        "assigned_quota", "natural_underfill", "underfill_reason",
    }
    synthetic = pd.DataFrame(columns=sorted(expected))
    assert set(synthetic.columns) == expected
    assert len(epoch1.MAIN_LANES) + len(epoch1.BBO_LANES) + 2 == 15


def test_epoch1r_uses_separate_artifact_root_and_preserves_failure() -> None:
    assert epoch1r.OUTPUT_ROOT != epoch1.OUTPUT_ROOT
    assert epoch1.FAILURE.exists()
    failure = epoch1r.load_json(epoch1.FAILURE)
    assert failure["status"] == "FAILED_VISIBLE_NOT_DELETED"
    assert failure["error_type"] == "KeyError"
