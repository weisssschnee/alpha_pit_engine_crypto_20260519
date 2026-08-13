from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

from alphafactory_crypto.broad_search.temporal_program_search_v1 import (
    _checkpoint_allocation,
    _later_checkpoint_targets,
    _new_state,
    _random_policy_key_for_lane,
    _targeted_effective_config,
    consume_targeted_deepening_authorization,
)
from alphafactory_crypto.broad_search import search_engine_v1 as engine_module
from alphafactory_crypto.broad_search.search_engine_v1 import (
    MechanismEvolutionV2,
    MechanismRandomV2,
)
from alphafactory_crypto.broad_search.temporal_targeted_deepening_v1 import (
    ACTIVE_PROGRAM_FAMILIES,
    ECONOMIC_FINGERPRINT_FIELDS,
    EVOLUTION_OPERATION_PROBABILITIES,
    LANE_SEEDS,
    build_diagnostic_baseline,
    build_frozen_target_parent_pool,
    final_next_decision,
    targeted_checkpoint_decision,
    targeted_diagnostics,
)
from alphafactory_crypto.broad_search.temporal_successor_v1 import (
    authorization_content_sha,
)

from test_crypto_temporal_program_v1 import (
    CONFIG,
    _catalog,
    _policy_parameters,
    _registry,
)


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


def _targeted_parent_candidates(count: int = 6):
    registry = _registry()
    catalog = _catalog()
    mechanisms = tuple(mechanism for mechanism, _ in catalog)
    parameters = _policy_parameters(catalog)
    random_policy = MechanismRandomV2(7101, registry, mechanisms, parameters)
    base = None
    for _ in range(200):
        candidate, _ = random_policy.propose()
        family = str(candidate.generation_genes["program_spec"]["family_id"])
        if family in ACTIVE_PROGRAM_FAMILIES:
            base = candidate
            break
    assert base is not None
    factory = MechanismEvolutionV2(7102, registry, mechanisms, {**parameters, "duplicate_resample_limit": 64})
    candidates = [base]
    while len(candidates) < count:
        child, _ = factory._mutate_parameters(base)
        if child.candidate_id not in {value.candidate_id for value in candidates}:
            candidates.append(child)
    return registry, catalog, parameters, candidates


def _synthetic_target_parent_pool(candidates) -> dict[str, object]:
    basin_members = {
        "ECO_090_001": candidates[:2],
        "ECO_090_002": candidates[2:],
    }
    parent_records = {}
    target_basins = []
    for basin_id, members in basin_members.items():
        family = str(members[0].generation_genes["program_spec"]["family_id"])
        ids = []
        for index, candidate in enumerate(members):
            candidate_id = candidate.candidate_id
            ids.append(candidate_id)
            parent_records[candidate_id] = {
                "candidate_id": candidate_id,
                "candidate": candidate.to_dict(),
                "behavior_family_id": f"behavior-{candidate_id}",
                "program_family_id": family,
                "family_count": 1,
                "search_reward": 1.0,
                "block_robust_ordering": None,
                "concrete_realization_id": f"realization-{basin_id}-{index}",
                "economic_similarity_cluster_id": basin_id,
            }
        target_basins.append(
            {
                "economic_similarity_cluster_id": basin_id,
                "program_family_id": family,
                "baseline_row_count": len(members),
                "member_candidate_ids": ids,
                "realization_depth": {},
                "realization_gaps": {"turnover_lt_2": True},
            }
        )
    core = {
        "schema_version": 1,
        "status": "FROZEN_TRAIN_ONLY_ECONOMIC_BASIN_PARENT_POOL",
        "source_ledger_path": "runtime/frozen.parquet",
        "source_ledger_sha256": "A" * 64,
        "source_ledger_row_count": len(candidates),
        "baseline_matched_positive_count": len(candidates),
        "clustering": {"canonical_similarity_threshold": 0.90},
        "target_rule": {},
        "target_basin_count": len(target_basins),
        "frozen_parent_candidate_count": len(parent_records),
        "target_basins": target_basins,
        "parent_records": {key: parent_records[key] for key in sorted(parent_records)},
        "market_arrays_read": 0,
        "candidate_evaluations": 0,
        "validation_reads": 0,
        "oos_reads": 0,
        "sealed_reads": 0,
    }
    return {**core, "target_parent_pool_sha256": engine_module._payload_sha(core)}


def test_frozen_target_parent_pool_builds_from_hash_bound_development_ledger(
    tmp_path: Path,
) -> None:
    _, _, _, candidates = _targeted_parent_candidates(6)
    baseline_rows = []
    source_rows = []
    for index, candidate in enumerate(candidates):
        family = str(candidate.generation_genes["program_spec"]["family_id"])
        row = _row(
            candidate.candidate_id,
            family=family,
            ordinal=index + 1,
            scale=1.0,
            mapped="mapped-shared",
        )
        baseline_rows.append(row)
        source_rows.append(
            {
                "candidate_id": candidate.candidate_id,
                "candidate_spec_json": json.dumps(candidate.to_dict(), sort_keys=True),
                "program_family_id": family,
                "behavior_family_id": row["behavior_family_id"],
                "block_robust_ordering_json": None,
                "search_reward": 1.0,
            }
        )
    source = tmp_path / "candidate_ledger.parquet"
    pd.DataFrame(source_rows).to_parquet(source, index=False)
    from alphafactory_crypto.broad_search.temporal_development_expansion_v1 import file_sha256

    baseline = {
        "source_ledger_path": str(source),
        "source_ledger_sha256": file_sha256(source),
        "source_strict_count": 6,
        "matched_positive_count": 6,
        "matched_positive_rows": baseline_rows,
    }
    pool = build_frozen_target_parent_pool(tmp_path, baseline)
    assert pool["target_basin_count"] == 1
    assert pool["frozen_parent_candidate_count"] == 6
    assert pool["baseline_matched_positive_count"] == 6
    assert pool["clustering"]["canonical_similarity_threshold"] == 0.90
    assert pool["market_arrays_read"] == pool["candidate_evaluations"] == 0
    assert pool["validation_reads"] == pool["oos_reads"] == pool["sealed_reads"] == 0
    bad = {**baseline, "source_ledger_sha256": "B" * 64}
    with pytest.raises(RuntimeError, match="FAIL_CLOSED_BEFORE_MARKET_READ"):
        build_frozen_target_parent_pool(tmp_path, bad)


def test_targeted_evolution_uses_only_frozen_basin_parents_and_restores_exactly() -> None:
    registry, catalog, parameters, candidates = _targeted_parent_candidates(6)
    pool = _synthetic_target_parent_pool(candidates)
    mechanisms = tuple(mechanism for mechanism, _ in catalog)
    policy = MechanismEvolutionV2(991, registry, mechanisms, {
        **parameters,
        "warmup": 32,
        "population_limit": 64,
        "tournament_size": 4,
        "parameter_mutation_probability": 0.60,
        "mechanism_mutation_probability": 0.10,
        "crossover_probability": 0.30,
    })
    policy.configure_targeted_parent_pool(pool)
    parent_to_basin = {
        candidate_id: basin["economic_similarity_cluster_id"]
        for basin in pool["target_basins"]
        for candidate_id in basin["member_candidate_ids"]
    }
    basin_counts = {key: 0 for key in policy.targeted_basin_order}
    for _ in range(8):
        _, metadata = policy.propose()
        receipt = metadata["receipt"]
        basin = receipt["targeted_economic_basin_id"]
        basin_counts[basin] += 1
        assert receipt["targeted_parent_pool_sha256"] == pool["target_parent_pool_sha256"]
        assert all(parent_to_basin[parent] == basin for parent in metadata["parent_ids"])
        if len(metadata["parent_ids"]) == 2:
            assert len(set(receipt["targeted_parent_realization_ids"])) == 2
    # 2-row and 4-row basins receive the same proposal count: scheduling is basin-balanced.
    assert max(basin_counts.values()) - min(basin_counts.values()) <= 1

    restored = MechanismEvolutionV2.from_state(registry, policy.export_state())
    assert restored.state_hash() == policy.state_hash()
    next_a, meta_a = policy.propose()
    next_b, meta_b = restored.propose()
    assert next_a.candidate_id == next_b.candidate_id
    assert meta_a["receipt"] == meta_b["receipt"]


def test_non_targeted_mechanism_evolution_still_uses_original_warmup() -> None:
    registry, catalog, parameters, _ = _targeted_parent_candidates(6)
    mechanisms = tuple(mechanism for mechanism, _ in catalog)
    policy = MechanismEvolutionV2(1234, registry, mechanisms, {**parameters, "warmup": 2})
    _, metadata = policy.propose()
    assert metadata["operation"] == "MECHANISM_EVOLUTION_TYPED_RANDOM_WARMUP"
    assert policy.targeted_parent_pool_payload is None
