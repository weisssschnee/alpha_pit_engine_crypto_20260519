from __future__ import annotations

import copy
import json
from pathlib import Path

import pandas as pd
import pytest

from alphafactory_crypto.broad_search.temporal_policy_validation_v1 import (
    ARMS,
    PROGRAM_FAMILIES,
    _economic_context_for_interval,
    build_decision,
    canonical_sha256,
    load_receipt,
    select_equal_count_cohort,
    selection_projection,
    sweep_temporal_program_constructibility,
    validate_split_contract,
)
from alphafactory_crypto.broad_search.temporal_program_search_v1 import (
    _checkpoint_allocation,
)


ROOT = Path(__file__).resolve().parents[1]


def test_split_is_balanced_after_purge_and_blocks_are_equal() -> None:
    receipt = load_receipt(ROOT)
    split = validate_split_contract(receipt)
    assert split == {
        "train_raw_hours": 1529,
        "validation_raw_hours": 1464,
        "train_effective_hours": 1523,
        "validation_effective_hours": 1458,
        "train_effective_share": 1523 / 2981,
        "validation_effective_share": 1458 / 2981,
        "validation_block_raw_hours": 488,
        "validation_block_effective_hours": 482,
        "maximum_feature_warmup_hours": 720,
        "warmup_rows_in_labels_or_metrics": False,
    }


def test_each_evaluation_interval_is_bound_to_its_frozen_receipt_block() -> None:
    receipt = load_receipt(ROOT)
    economic = {
        "validation": {
            "role": "DEVELOPMENT_VALIDATION_NO_FEEDBACK_NOT_OOS",
            "start": "2025-11-01T00:00:00Z",
            "end_exclusive": "2026-01-01T00:00:00Z",
        },
        "evidence_partition": {
            "validation": {
                "role": "DEVELOPMENT_VALIDATION_NO_FEEDBACK_NOT_OOS",
                "start": "2025-11-01T00:00:00Z",
                "end_exclusive": "2026-01-01T00:00:00Z",
            }
        },
    }
    for interval in receipt["split_contract"]["validation_blocks"]:
        bound = _economic_context_for_interval(
            economic,
            interval=interval,
            receipt=receipt,
        )
        assert bound["validation"]["start"] == interval["start"]
        assert bound["validation"]["end_exclusive"] == interval["end_exclusive"]
        assert bound["evidence_partition"]["validation"] == bound["validation"]
    with pytest.raises(
        RuntimeError,
        match="TEMPORAL_POLICY_VALIDATION_INTERVAL_NOT_RECEIPT_BOUND",
    ):
        _economic_context_for_interval(
            economic,
            interval={
                "label": "unregistered",
                "start": "2025-11-02T00:00:00Z",
                "end_exclusive": "2025-11-03T00:00:00Z",
            },
            receipt=receipt,
        )


def test_train_only_selection_is_exact_equal_count_and_hash_bound() -> None:
    receipt = load_receipt(ROOT)
    rows = select_equal_count_cohort(ROOT, receipt=receipt)
    frame = pd.DataFrame(selection_projection(rows))
    assert len(frame) == 360
    assert frame["candidate_id"].nunique() == 360
    assert frame["behavior_family_id"].nunique() == 360
    assert set(frame["arm"]) == set(ARMS)
    assert set(frame["program_family_id"]) == set(PROGRAM_FAMILIES)
    assert set(frame.groupby(["arm", "program_family_id", "lane_index"]).size()) == {15}
    assert canonical_sha256(selection_projection(rows)) == receipt["selection"][
        "selection_sha256"
    ]


def test_temporal_program_constructibility_uses_the_temporal_builder() -> None:
    receipt = load_receipt(ROOT)
    rows = select_equal_count_cohort(ROOT, receipt=receipt)[:2]
    manifest = json.loads(
        (ROOT / receipt["carrier"]["manifest_path"]).read_text(encoding="utf-8")
    )
    config = json.loads(
        (ROOT / "config" / "crypto_temporal_mechanism_program_v1.json").read_text(
            encoding="utf-8"
        )
    )
    limits = config["expression_limits"]
    result = sweep_temporal_program_constructibility(
        selected_rows=rows,
        contract_rows=manifest["contracts"],
        expression_registry_limits={
            "max_depth": limits["maximum_depth"],
            "max_raw_inputs": limits["maximum_raw_fields"],
            "max_rolling_windows": limits["maximum_rolling_windows"],
            "max_canonical_primitive_nodes": limits[
                "maximum_canonical_primitive_nodes"
            ],
            "max_cross_asset_normalizations": limits[
                "maximum_cross_asset_normalizations"
            ],
            "max_regime_gates": limits["maximum_regime_gates"],
        },
    )
    assert result["status"] == "PASS_TEMPORAL_PROGRAM_CONSTRUCTIBILITY_SWEEP"
    assert result["candidate_count"] == 2
    assert result["unique_candidate_count"] == 2
    assert result["market_read_performed"] is False


def _decision_frame(evolution_replicated: int, control_replicated: int) -> pd.DataFrame:
    rows = []
    for arm in ARMS:
        positive_count = (
            evolution_replicated if arm == "temporal_program_evolution" else control_replicated
        )
        for index in range(120):
            positive = index < positive_count
            rows.append(
                {
                    "arm": arm,
                    "candidate_id": f"{arm}-{index}",
                    "validation_status": "EVALUATED",
                    "strict_evaluated": True,
                    "validation_left_incremental_net_mean": 0.1 if positive else -0.1,
                    "validation_right_incremental_net_mean": 0.1 if positive else -0.1,
                    "validation_matched_positive": False,
                    "replicated_positive_block_count": 2 if positive else 0,
                    "program_family_id": PROGRAM_FAMILIES[index % 2],
                    "lane_index": index % 4,
                    "program_id": f"program-{index % 8}",
                    "block_1_strict_evaluated": True,
                    "block_2_strict_evaluated": True,
                    "block_3_strict_evaluated": True,
                    "block_1_validation_status": "EVALUATED",
                    "block_2_validation_status": "EVALUATED",
                    "block_3_validation_status": "EVALUATED",
                }
            )
    return pd.DataFrame(rows)


def test_decision_qualifies_only_a_broad_replication_advantage() -> None:
    receipt = load_receipt(ROOT)
    passed = build_decision(_decision_frame(24, 4), receipt)
    held = build_decision(_decision_frame(5, 4), receipt)
    assert passed["decision"] == "QUALIFY_20_20_60_FIXED_DEVELOPMENT_FLOW"
    assert passed["policy_validation_pass"] is True
    assert passed["alpha_qualification"] == "HOLD"
    assert held["decision"] == "HOLD_CURRENT_FIXED_FLOW"
    assert held["policy_validation_pass"] is False


def test_temporal_program_uses_configured_fixed_policy_weights() -> None:
    config = json.loads(
        (ROOT / "config" / "crypto_temporal_mechanism_program_v1.json").read_text(
            encoding="utf-8"
        )
    )
    qualified = copy.deepcopy(config)
    qualified["stage_allocations"][1]["allocation_per_10000"] = {
        "temporal_program_random": 2000,
        "temporal_program_cem": 2000,
        "temporal_program_evolution": 6000,
    }
    state = {
        "skip_stage0": True,
        "arm_states": {
            "temporal_program_cem": "ACTIVE",
            "temporal_program_evolution": "ACTIVE",
        },
    }
    assert _checkpoint_allocation(state, 5, qualified) == {
        "temporal_program_random": 400,
        "temporal_program_cem": 400,
        "temporal_program_evolution": 1200,
    }
