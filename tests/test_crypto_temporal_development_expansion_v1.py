from __future__ import annotations

import json

from alphafactory_crypto.broad_search.temporal_development_expansion_v1 import (
    DECISION_BOUNDARIES,
    FIXED_ALLOCATION_PER_10000,
    LANE_SEEDS,
    discovery_diagnostics,
    fixed_flow_decision,
)
from alphafactory_crypto.broad_search.temporal_program_search_v1 import (
    _checkpoint_allocation,
    _expansion_effective_config,
    _later_checkpoint_targets,
    _new_state,
)

from test_crypto_temporal_program_v1 import CONFIG


def test_fixed_flow_uses_fresh_seeds_and_exact_20_20_60_allocation() -> None:
    assert len(LANE_SEEDS) == len(set(LANE_SEEDS)) == 4
    effective = _expansion_effective_config(CONFIG)
    assert tuple(effective["seed_authority"]["seeds"]) == LANE_SEEDS
    state = _new_state("a" * 40, "B" * 64, effective)
    state["skip_stage0"] = True
    assert _checkpoint_allocation(state, 0, effective) == {
        "temporal_program_random": 400,
        "temporal_program_cem": 400,
        "temporal_program_evolution": 1_200,
    }
    targets = _later_checkpoint_targets(
        _checkpoint_allocation(state, 0, effective), effective
    )
    assert sum(targets.values()) == 2_000
    assert len(targets) == 12
    assert sum(
        value for key, value in targets.items() if key.startswith("temporal_program_evolution|")
    ) == 1_200


def test_fixed_flow_decisions_never_prune_or_stop_an_arm() -> None:
    for boundary in DECISION_BOUNDARIES:
        decision = fixed_flow_decision(boundary)
        assert decision["status"] == "CONTINUE_FIXED_FLOW_DIAGNOSTIC_ONLY"
        assert decision["allocation_per_10000"] == FIXED_ALLOCATION_PER_10000
        assert set(decision["arm_states_before"].values()) == {"ACTIVE"}
        assert decision["arm_states_after"] == decision["arm_states_before"]
        assert decision["family_concentration_is_diagnostic_only"] is True


def test_discovery_diagnostics_are_baseline_relative_and_have_no_policy_feedback() -> None:
    common = {
        "left_incremental_gross_mean": 0.0002,
        "right_incremental_gross_mean": 0.0003,
        "left_turnover_mean": 0.1,
        "right_turnover_mean": 0.1,
        "search_reward": 1.0,
        "replicated_candidate": True,
        "mapped_weight_descriptor_id": "mapped",
        "selected_asset_overlap_id": "assets",
        "turnover_path_descriptor_id": "turnover",
        "raw_fields_json": json.dumps(["oi", "flow"]),
        "operator_path": "Delta|Residual",
    }
    rows = [
        {
            **common,
            "candidate_id": "old",
            "completion_ordinal": 1,
            "behavior_family_id": "known-cluster",
            "program_id": "known-basin",
            "program_family_id": "P1_POSITION_STATE_CHANGE_TO_RESPONSE",
            "arm": "temporal_program_random",
            "operation": "TYPED_RANDOM",
            "parent_ids_json": "[]",
            "left_incremental_net_mean": 0.0001,
            "right_incremental_net_mean": 0.0001,
            "matched_positive": False,
        },
        {
            **common,
            "candidate_id": "child",
            "completion_ordinal": 2,
            "behavior_family_id": "new-cluster",
            "program_id": "new-basin",
            "program_family_id": "P4_MULTISCALE_STATE_X_TRANSITION_ROUTING",
            "arm": "temporal_program_evolution",
            "operation": "COMPATIBLE_MECHANISM_SPEC_MUTATION",
            "parent_ids_json": json.dumps(["old"]),
            "left_incremental_net_mean": 0.0002,
            "right_incremental_net_mean": 0.0002,
            "matched_positive": True,
        },
    ]
    result = discovery_diagnostics(
        rows,
        baseline={
            "economic_behavior_family_ids": ["known-cluster"],
            "positive_program_ids": ["known-basin"],
        },
        strict_boundary=2,
        process_cpu_seconds=3600.0,
    )
    assert result["new_economic_opportunity_cluster_count"] == 1
    assert result["new_matched_positive_economic_cluster_count"] == 1
    assert result["development_replication_2_of_3_count"] == 2
    assert result["policy_feedback_applied"] is False
    operation = next(
        row
        for row in result["evolution_operation_attribution"]
        if row["operation"] == "mechanism_mutation"
    )
    assert operation["new_economic_cluster_count"] == 1
    assert operation["cross_basin_transition_count"] == 1
