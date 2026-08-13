from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from alphafactory_crypto.broad_search.temporal_program_search_v1 import (
    _checkpoint_allocation,
    _later_checkpoint_targets,
    _new_state,
    _random_policy_key_for_lane,
    _targeted_effective_config,
    consume_targeted_deepening_authorization,
)
from alphafactory_crypto.broad_search.temporal_targeted_deepening_v1 import (
    ACTIVE_PROGRAM_FAMILIES,
    ECONOMIC_FINGERPRINT_FIELDS,
    EVOLUTION_OPERATION_PROBABILITIES,
    LANE_SEEDS,
    build_diagnostic_baseline,
    final_next_decision,
    targeted_checkpoint_decision,
    targeted_diagnostics,
)
from alphafactory_crypto.broad_search.temporal_successor_v1 import (
    authorization_content_sha,
)

from test_crypto_temporal_program_v1 import CONFIG


def _row(
    candidate_id: str,
    *,
    family: str,
    ordinal: int,
    scale: float,
    mapped: str,
    operation: str = "TYPED_RANDOM",
) -> dict[str, object]:
    row: dict[str, object] = {
        field: scale * (index + 1) + ((index % 3) - 1) * 0.01
        for index, field in enumerate(ECONOMIC_FINGERPRINT_FIELDS)
    }
    row.update(
        {
            "candidate_id": candidate_id,
            "completion_ordinal": ordinal,
            "behavior_family_id": f"behavior-{candidate_id}",
            "program_family_id": family,
            "program_id": f"program-{family}",
            "arm": (
                "temporal_program_evolution"
                if operation != "TYPED_RANDOM"
                else "temporal_program_random"
            ),
            "seed": ordinal,
            "operation": operation,
            "mapped_weight_descriptor_id": mapped,
            "selected_asset_overlap_id": f"assets-{mapped}",
            "turnover_path_descriptor_id": f"turnover-{mapped}",
            "raw_fields_json": json.dumps(["oi", mapped]),
            "operator_path": f"Delta|{mapped}",
            "parent_ids_json": "[]",
            "left_incremental_net_mean": 0.001,
            "right_incremental_net_mean": 0.001,
            "matched_positive": True,
            "replicated_candidate": True,
        }
    )
    return row


def test_targeted_config_freezes_p1_p4_and_20_20_60_allocation() -> None:
    assert len(LANE_SEEDS) == len(set(LANE_SEEDS)) == 4
    effective = _targeted_effective_config(CONFIG)
    assert tuple(effective["seed_authority"]["seeds"]) == LANE_SEEDS
    assert effective["search_budget"]["strict_evaluated_maximum"] == 30_000
    assert {
        key: effective["policy_parameters"]["temporal_program_evolution"][key]
        for key in EVOLUTION_OPERATION_PROBABILITIES
    } == EVOLUTION_OPERATION_PROBABILITIES
    state = _new_state("a" * 40, "B" * 64, effective)
    state.update(
        {
            "skip_stage0": True,
            "active_program_families": list(ACTIVE_PROGRAM_FAMILIES),
        }
    )
    allocation = _checkpoint_allocation(state, 0, effective)
    assert allocation == {
        "temporal_program_random": 400,
        "temporal_program_cem": 400,
        "temporal_program_evolution": 1_200,
    }
    targets = _later_checkpoint_targets(allocation, effective)
    assert sum(targets.values()) == 2_000
    assert state["active_program_families"] == list(ACTIVE_PROGRAM_FAMILIES)


def test_targeted_random_lane_never_uses_out_of_scope_diagnostic_policy() -> None:
    catalog = [(None, SimpleNamespace(family_id="P2_PAUSED"))]
    policy_key = "temporal_program_random|71"
    assert (
        _random_policy_key_for_lane(
            policy_key,
            arm="temporal_program_random",
            seed_text="71",
            local_index=9,
            targeted_mode=True,
            active_program_families=ACTIVE_PROGRAM_FAMILIES,
            catalog=catalog,
        )
        == policy_key
    )
    assert _random_policy_key_for_lane(
        policy_key,
        arm="temporal_program_random",
        seed_text="71",
        local_index=9,
        targeted_mode=False,
        active_program_families=ACTIVE_PROGRAM_FAMILIES,
        catalog=catalog,
    ) == "temporal_program_random_diagnostic|71"


def test_targeted_diagnostics_separate_economic_basin_and_realization() -> None:
    baseline_rows = [
        _row(
            f"baseline-{index}",
            family=ACTIVE_PROGRAM_FAMILIES[index % 2],
            ordinal=index + 1,
            scale=1.0 + index * 0.001,
            mapped=f"mapped-{index % 2}",
        )
        for index in range(6)
    ]
    baseline = build_diagnostic_baseline(
        baseline_rows,
        source_ledger_path="runtime/source/candidate_ledger.parquet",
        source_ledger_sha256="A" * 64,
        source_strict_count=50_000,
    )
    current = [
        _row(
            "current-p1",
            family=ACTIVE_PROGRAM_FAMILIES[0],
            ordinal=1,
            scale=1.002,
            mapped="mapped-new-p1",
            operation="ONE_POINT_TYPED_MECHANISM_CROSSOVER",
        ),
        _row(
            "current-p4",
            family=ACTIVE_PROGRAM_FAMILIES[1],
            ordinal=2,
            scale=-0.7,
            mapped="mapped-new-p4",
            operation="MECHANISM_PARAMETER_GROUP_MUTATION_1_TO_3",
        ),
    ]
    result = targeted_diagnostics(current, baseline=baseline, strict_boundary=2)
    assert result["status"] == "TARGETED_DIAGNOSTIC_ONLY_NOT_SEARCH_AUTHORITY"
    assert result["policy_feedback_applied"] is False
    assert result["matched_positive_rows"] == 2
    assert set(result["p1_vs_p4"]) == set(ACTIVE_PROGRAM_FAMILIES)
    assert result["economic_cluster_summary"]["fingerprint_field_count"] == 53
    assert result["basin_realization_depth"]["economic_basin_count"] >= 1
    assert result["validation_reads"] == result["oos_reads"] == result["sealed_reads"] == 0


def test_saturation_and_final_decisions_are_predeclared() -> None:
    base_depth = {
        "mapped_weight_realizations_ge_2": 5,
        "mapped_weight_realizations_ge_3": 2,
        "turnover_realizations_ge_2": 3,
        "raw_field_realizations_ge_2": 5,
        "asset_selection_realizations_ge_2": 5,
        "high_quality_basins_deepened": 10,
        "new_high_quality_concrete_realizations": 12,
    }
    diagnostic_10k = {
        "economic_cluster_summary": {
            "thresholds": {"0.90": {"new_economic_cluster_count": 3}}
        },
        "basin_realization_depth": dict(base_depth),
    }
    diagnostic_20k = {
        "economic_cluster_summary": {
            "thresholds": {"0.90": {"new_economic_cluster_count": 3}}
        },
        "basin_realization_depth": dict(base_depth),
    }
    assert targeted_checkpoint_decision(
        20_000, diagnostic_20k, checkpoint_10000=diagnostic_10k
    )["status"] == "STOP_TARGETED_DEEPENING_SATURATED_AT_20000"
    diagnostic_20k["basin_realization_depth"] = {
        **base_depth,
        "mapped_weight_realizations_ge_2": 6,
    }
    assert targeted_checkpoint_decision(
        20_000, diagnostic_20k, checkpoint_10000=diagnostic_10k
    )["status"] == "CONTINUE_TO_FROZEN_30000_CAP"

    sufficient = {
        "baseline_basin_realization_depth": {
            key: 0 for key in base_depth
        },
        "basin_realization_depth": dict(base_depth),
    }
    assert (
        final_next_decision(sufficient, system_valid=True)
        == "TARGETED_DEEPENING_SUFFICIENT_WAIT_FOR_FORWARD"
    )
    assert final_next_decision({}, system_valid=False) == "SYSTEM_INVALID"


def test_system_invalid_attempt_consumes_one_time_authorization(
    tmp_path: Path,
) -> None:
    runtime_id = (
        "crypto_temporal_targeted_p1_p4_basin_deepening_v1_20260813r1"
    )
    authorization_path = (
        tmp_path
        / "config/crypto_temporal_targeted_p1_p4_basin_deepening_v1_authorization.json"
    )
    authorization_path.parent.mkdir(parents=True)
    authorization = {
        "status": "RUN_AUTHORIZED_ONE_TIME_TARGETED_P1_P4_DEEPENING",
        "run_authorized": True,
        "consumed": False,
        "runtime_id": runtime_id,
    }
    authorization["authorization_sha256"] = authorization_content_sha(
        authorization
    )
    authorization_path.write_text(json.dumps(authorization), encoding="utf-8")

    evidence = tmp_path / "reports/evidence"
    evidence.mkdir(parents=True)
    audit_path = evidence / "audit.json"
    producer_path = evidence / "producer.json"
    task_path = evidence / "task.json"
    audit_path.write_text(
        json.dumps(
            {
                "status": "FAIL",
                "finding": "TARGETED_PROGRAM_FAMILY_SCOPE_VIOLATION",
                "next_decision": "SYSTEM_INVALID",
                "runtime_id": runtime_id,
                "task_id": "job-invalid",
                "producer_source_sha": "a" * 40,
                "out_of_scope_strict_rows": 201,
                "strict_rows_audited": 10_000,
                "completion_ordinals_contiguous": True,
                "market_arrays_read_by_audit": 0,
                "candidate_evaluations_by_audit": 0,
                "validation_reads": 0,
                "oos_reads": 0,
                "sealed_reads": 0,
            }
        ),
        encoding="utf-8",
    )
    producer_path.write_text(
        json.dumps(
            {
                "status": "RUNNING",
                "producer_source_sha": "a" * 40,
                "strict_evaluated": 13_691,
                "generation_attempts": 23_671,
                "checkpoint_index": 6,
            }
        ),
        encoding="utf-8",
    )
    task_path.write_text(
        json.dumps(
            {
                "task_id": "job-invalid",
                "state": "FAILED",
                "exit_code": 1,
                "ended_at": "2026-08-13T15:36:54",
            }
        ),
        encoding="utf-8",
    )

    result = consume_targeted_deepening_authorization(
        tmp_path,
        runtime_date="20260813r1",
        system_invalid_audit=audit_path,
        producer_status_evidence=producer_path,
        task_status_evidence=task_path,
    )
    assert result["run_authorized"] is False
    assert result["consumed"] is True
    assert result["run_outcome"]["status"] == "SYSTEM_INVALID"
    assert result["run_outcome"]["audited_strict_prefix"] == 10_000
    assert result["run_outcome"]["automatic_next_run_started"] is False
