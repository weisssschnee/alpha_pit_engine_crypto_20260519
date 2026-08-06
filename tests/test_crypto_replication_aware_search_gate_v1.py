from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from alphafactory_crypto.broad_search.expression import (
    FieldContract,
    TypedExpressionRegistry,
)
from alphafactory_crypto.broad_search.pair18m import (
    SEARCH_REWARD_AUTHORITY,
    _development_block_robust_ordering,
)
from alphafactory_crypto.broad_search.experiment_authority import (
    resolve_search_economic_receipt,
)
from alphafactory_crypto.broad_search.search_engine_v1 import (
    BLOCK_ROBUST_GATE_ARMS,
    BLOCK_ROBUST_GATE_CAMPAIGN,
    BLOCK_ROBUST_GATE_SEEDS,
    MechanismEvolutionV2,
    MechanismRandomV2,
    _block_robust_gate_summary,
    _economic_campaign_seeds,
    _initial_policies,
    _load_search_evidence_v1_contract,
    _process_evidence_root_for_campaign,
    _search_evidence_v1_expected_checkpoint_allocations,
    _write_proposal_batch_process_evidence,
    _write_worker_process_evidence,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def _contracts() -> tuple[FieldContract, ...]:
    manifest = json.loads(
        (
            REPO_ROOT
            / "runtime/crypto_search_engine_v1_4_oi_flow_20260728/"
            "aligned_carrier_manifest.json"
        ).read_text(encoding="utf-8")
    )
    return tuple(
        FieldContract(
            str(row["field_id"]),
            str(row["value_type"]),
            str(row["unit"]),
            int(row["observable_lag_hours"]),
            str(row["pit_authority"]),
        )
        for row in manifest["contracts"]
    )


def _ordering(
    *,
    replicated: int,
    worst: float,
    median: float,
    turnover: float,
    support: float,
) -> dict[str, object]:
    return {
        "authority": "DEVELOPMENT_THREE_BLOCK_ROBUST_ORDERING_V1",
        "replicated_positive_block_count": replicated,
        "worst_block_min_matched_net_mean": worst,
        "median_block_joint_search_reward": median,
        "max_required_mean_one_way_turnover": turnover,
        "min_required_support": support,
    }


def test_gate_contract_is_equal_count_fresh_development_only() -> None:
    config, catalog, _ = _load_search_evidence_v1_contract(
        REPO_ROOT, campaign=BLOCK_ROBUST_GATE_CAMPAIGN
    )
    allocations = _search_evidence_v1_expected_checkpoint_allocations(
        stages=config["stages"],
        seeds=BLOCK_ROBUST_GATE_SEEDS,
        arms=BLOCK_ROBUST_GATE_ARMS,
        checkpoint_size=512,
        checkpoint_count=3,
    )

    assert _economic_campaign_seeds(BLOCK_ROBUST_GATE_CAMPAIGN) == (
        BLOCK_ROBUST_GATE_SEEDS
    )
    assert set(allocations) == {0, 1, 2}
    assert {
        arm: sum(allocation[arm] for allocation in allocations.values())
        for arm in BLOCK_ROBUST_GATE_ARMS
    } == {arm: 512 for arm in BLOCK_ROBUST_GATE_ARMS}
    assert all(item.condition_role is None for item in catalog)
    assert config["block_robust_contract"]["horizons_hours"] == [4]
    assert not any(config["fresh_state"].values())
    assert config["validation"] == {
        "authorized": False,
        "status": "NOT_AUTHORIZED",
        "holdout_read": False,
        "automatic_continuation": False,
    }


def test_proposal_batch_process_evidence_persists_pre_submit_identity(
    tmp_path: Path,
) -> None:
    registry = TypedExpressionRegistry(_contracts())
    config, catalog, _ = _load_search_evidence_v1_contract(
        REPO_ROOT, campaign=BLOCK_ROBUST_GATE_CAMPAIGN
    )
    policy = MechanismRandomV2(
        BLOCK_ROBUST_GATE_SEEDS[0],
        registry,
        catalog,
        dict(config["policy_parameters"][BLOCK_ROBUST_GATE_ARMS[0]]),
    )
    candidate, metadata = policy.propose()
    proposal = {
        **metadata,
        "candidate": candidate,
        "arm": BLOCK_ROBUST_GATE_ARMS[0],
        "seed": BLOCK_ROBUST_GATE_SEEDS[0],
        "policy_key": (
            f"{BLOCK_ROBUST_GATE_ARMS[0]}|{BLOCK_ROBUST_GATE_SEEDS[0]}"
        ),
        "generation_attempt_ordinal": 7,
    }

    payload = _write_proposal_batch_process_evidence(
        evidence_root=tmp_path,
        stage="PROPOSAL_BATCH_READY_BEFORE_WORKER_SUBMIT",
        source_sha="a" * 40,
        frozen_contract_sha256="B" * 64,
        checkpoint_index=0,
        batch_index=0,
        generation_attempts=7,
        attempted_exact_id_count=1,
        proposals=[proposal],
        submitted_count=0,
        returned_count=0,
    )

    observed = json.loads(
        (tmp_path / "producer_batch_000000.json").read_text(encoding="utf-8")
    )
    assert observed == payload
    assert observed["stage"] == "PROPOSAL_BATCH_READY_BEFORE_WORKER_SUBMIT"
    assert observed["generation_attempts"] == 7
    assert observed["proposal_count"] == 1
    assert observed["submitted_count"] == 0
    assert observed["proposals"][0]["candidate_id"] == candidate.candidate_id
    assert observed["proposals"][0]["candidate_spec_sha256"] == hashlib.sha256(
        json.dumps(
            candidate.to_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            default=str,
        ).encode("utf-8")
    ).hexdigest().upper()
    assert len(observed["evidence_sha256"]) == 64


def test_worker_process_evidence_is_stage_specific_and_atomic(tmp_path: Path) -> None:
    initializer = _write_worker_process_evidence(
        evidence_root=tmp_path,
        channel="initializer",
        stage="INITIALIZER_READY",
    )
    task = _write_worker_process_evidence(
        evidence_root=tmp_path,
        channel="task",
        stage="TASK_COMPLETED",
        candidate_id="candidate-1",
        outcome="PAIR_EVALUATED",
    )

    assert initializer is not None
    assert task is not None
    assert initializer.name.endswith("_initializer.json")
    assert task.name.endswith("_task.json")
    assert not list(tmp_path.glob("*.tmp-*"))
    observed = json.loads(task.read_text(encoding="utf-8"))
    assert observed["stage"] == "TASK_COMPLETED"
    assert observed["candidate_id"] == "candidate-1"
    assert observed["outcome"] == "PAIR_EVALUATED"
    assert len(observed["evidence_sha256"]) == 64


def test_process_evidence_is_replication_gate_local_and_fail_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert _process_evidence_root_for_campaign(
        tmp_path, BLOCK_ROBUST_GATE_CAMPAIGN
    ) == (tmp_path / "process_evidence")
    assert _process_evidence_root_for_campaign(tmp_path, "legacy") is None

    def fail_write(_path: Path, _value: object) -> None:
        raise OSError("diagnostic disk unavailable")

    monkeypatch.setattr(
        "alphafactory_crypto.broad_search.search_engine_v1._write_json",
        fail_write,
    )
    with pytest.raises(OSError, match="diagnostic disk unavailable"):
        _write_worker_process_evidence(
            evidence_root=tmp_path,
            channel="initializer",
            stage="INITIALIZER_STARTED",
        )


def test_original_gate_receipt_retains_consumed_invalid_run() -> None:
    receipt = resolve_search_economic_receipt(
        REPO_ROOT,
        "config/crypto_search_replication_aware_gate_v1_receipt.json",
    )

    assert receipt["result"] == (
        "RUN_AUTHORIZATION_CONSUMED_ENGINE_VERIFICATION_FAILED"
    )
    assert receipt["run_authorized"] is False
    assert receipt["run_outcome"] == {
        "status": "ENGINE_VERIFICATION_FAILED",
        "reason": "PRODUCER_PARENT_EXITED_BEFORE_FIRST_ATTEMPT",
        "runtime": "runtime/crypto_search_replication_aware_gate_v1_20260806",
        "producer_source_sha": "ee36ea46a617b8786661b402992ef3fb0fbaaf5a",
        "generation_attempts": 0,
        "strict_evaluated_count": 0,
        "checkpoint": None,
        "artifact_bundle_sha256": (
            "D0E544EB1396CA5C43E77ED82B4277FA"
            "EF05164650846CB7735CB3D4F65EBCFD"
        ),
        "checker_result": "FAIL",
        "checker_exit_code": 1,
        "checker_missing_artifact_count": 13,
        "effective_task_id": "job_20260806_044440_a5b83e",
        "sealed_reads": 0,
        "rescue_rerun_started": False,
    }
    assert receipt["search_campaign"]["strict_evaluated_target"] == 1536
    assert receipt["search_campaign"]["seed_set"] == list(
        BLOCK_ROBUST_GATE_SEEDS
    )
    assert receipt["validation"]["role"] == "NOT_AUTHORIZED"
    assert receipt["holdout"]["read_allowed"] is False
    assert receipt["validation_kill_line"]["required_horizons_hours"] == [4]


def test_replacement_receipt_retains_consumed_launcher_failure() -> None:
    receipt = resolve_search_economic_receipt(
        REPO_ROOT,
        "config/crypto_search_replication_aware_gate_v1_replacement_receipt.json",
    )

    assert receipt["result"] == (
        "RUN_AUTHORIZATION_CONSUMED_ENGINE_VERIFICATION_FAILED"
    )
    assert receipt["run_authorized"] is False
    assert receipt["search_campaign"]["runner_campaign"] == (
        BLOCK_ROBUST_GATE_CAMPAIGN
    )
    assert receipt["search_campaign"]["runtime_date"] == "20260806r1"
    assert receipt["search_campaign"]["strict_evaluated_target"] == 1536
    assert receipt["search_campaign"]["seed_set"] == list(BLOCK_ROBUST_GATE_SEEDS)
    assert receipt["run_outcome"] == {
        "status": "ENGINE_VERIFICATION_FAILED",
        "reason": "NATIVE_STDERR_TERMINATED_BEFORE_WORKER_SUBMIT",
        "runtime": "runtime/crypto_search_replication_aware_gate_v1_20260806r1",
        "producer_source_sha": "a0c60ec55c4e71da08f575dfcbf2ec76cecd7596",
        "generation_attempts": 8,
        "submitted_count": 0,
        "returned_count": 0,
        "strict_evaluated_count": 0,
        "market_evaluations": 0,
        "checkpoint": None,
        "artifact_bundle_sha256": (
            "C8B3ADD62EEBC1C01A9A7E0D20057148"
            "5BED83FF582B57AD798CE2E5568720EC"
        ),
        "checker_result": "FAIL",
        "checker_exit_code": 1,
        "checker_missing_artifact_count": 13,
        "effective_task_id": "job_20260806_125929_7681d5",
        "launcher_failure": (
            "WINDOWS_POWERSHELL_NATIVE_COMMAND_ERROR_FROM_NUMPY_RUNTIME_WARNING"
        ),
        "orphan_worker_terminated": True,
        "sealed_reads": 0,
        "rescue_rerun_started": False,
    }
    assert receipt["validation"]["role"] == "NOT_AUTHORIZED"
    assert receipt["holdout"]["read_allowed"] is False
    assert receipt["validation_kill_line"]["evaluated_per_active_arm"] == 0
    assert receipt["formal_claims_authorized"] is False


def test_r2_receipt_is_single_use_authorized_and_contract_identical() -> None:
    receipt = resolve_search_economic_receipt(
        REPO_ROOT,
        "config/crypto_search_replication_aware_gate_v1_r2_receipt.json",
    )

    assert receipt["result"] == "RUN_AUTHORIZED_CONDITIONAL_DEVELOPMENT"
    assert receipt["run_authorized"] is True
    assert receipt["search_campaign"]["runner_campaign"] == (
        BLOCK_ROBUST_GATE_CAMPAIGN
    )
    assert receipt["search_campaign"]["runtime_date"] == "20260806r2"
    assert receipt["search_campaign"]["strict_evaluated_target"] == 1536
    assert receipt["search_campaign"]["seed_set"] == list(
        BLOCK_ROBUST_GATE_SEEDS
    )
    assert receipt["validation"]["role"] == "NOT_AUTHORIZED"
    assert receipt["holdout"]["read_allowed"] is False
    assert receipt["validation_kill_line"]["required_horizons_hours"] == [4]


def test_pc2_launcher_treats_native_stderr_as_diagnostic() -> None:
    launcher = (
        REPO_ROOT
        / "scripts/crypto_replication_aware_gate_v1_pc2_launcher.ps1"
    ).read_text(encoding="utf-8")

    assert "Start-Process" in launcher
    assert "RedirectStandardOutput" in launcher
    assert "RedirectStandardError" in launcher
    assert "native-stderr-smoke" in launcher
    assert "NATIVE_STDERR_SMOKE_PASS" in launcher
    assert "& $Python @Arguments" not in launcher


def test_replacement_invalid_run_manifest_binds_pre_submit_evidence() -> None:
    runtime = (
        REPO_ROOT
        / "runtime/crypto_search_replication_aware_gate_v1_20260806r1"
    )
    manifest = json.loads(
        (runtime / "invalid_run_artifact_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    rows = sorted(manifest["artifacts"], key=lambda row: str(row["path"]))
    assert manifest["status"] == (
        "RUN_INVALID_NATIVE_STDERR_TERMINATED_BEFORE_WORKER_SUBMIT"
    )
    assert manifest["artifact_count"] == len(rows) == 16
    for row in rows:
        payload = (runtime / str(row["path"])).read_bytes()
        assert len(payload) == int(row["bytes"])
        assert hashlib.sha256(payload).hexdigest().upper() == row["sha256"]
    bundle_payload = "\n".join(
        f"{row['path']}|{row['bytes']}|{row['sha256']}" for row in rows
    ).encode("utf-8")
    assert hashlib.sha256(bundle_payload).hexdigest().upper() == (
        manifest["artifact_bundle_sha256"]
    )
    producer = json.loads((runtime / "producer_status.json").read_text())
    assert producer["generation_attempts"] == 8
    assert producer["last_batch"]["submitted_count"] == 0
    assert producer["last_batch"]["returned_count"] == 0
    assert producer["strict_evaluated"] == 0


def test_invalid_run_artifact_manifest_binds_zero_attempt_evidence() -> None:
    runtime = REPO_ROOT / "runtime/crypto_search_replication_aware_gate_v1_20260806"
    manifest = json.loads(
        (runtime / "invalid_run_artifact_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    rows = sorted(manifest["artifacts"], key=lambda row: str(row["path"]))
    assert manifest["status"] == (
        "RUN_INVALID_PRODUCER_PARENT_EXITED_BEFORE_ATTEMPTS"
    )
    assert manifest["artifact_count"] == len(rows) == 10
    for row in rows:
        payload = (runtime / str(row["path"])).read_bytes()
        assert len(payload) == int(row["bytes"])
        assert hashlib.sha256(payload).hexdigest().upper() == row["sha256"]
    bundle_payload = "\n".join(
        f"{row['path']}|{row['bytes']}|{row['sha256']}" for row in rows
    ).encode("utf-8")
    assert hashlib.sha256(bundle_payload).hexdigest().upper() == (
        manifest["artifact_bundle_sha256"]
    )
    producer = json.loads((runtime / "producer_status.json").read_text())
    assert producer["generation_attempts"] == 0
    assert producer["strict_evaluated"] == 0


def test_gate_policies_emit_only_4h_binary_candidates() -> None:
    registry = TypedExpressionRegistry(_contracts())
    policies = _initial_policies(
        registry,
        arms=BLOCK_ROBUST_GATE_ARMS,
        seeds=(BLOCK_ROBUST_GATE_SEEDS[0],),
    )

    assert len(policies) == 3
    for policy in policies.values():
        candidate, _ = policy.propose()
        assert candidate.horizon_hours == 4
        mechanism = candidate.generation_genes["mechanism_spec"]
        assert mechanism["condition_role"] is None


def test_replication_selection_is_lexicographic_without_changing_current() -> None:
    registry = TypedExpressionRegistry(_contracts())
    config, catalog, _ = _load_search_evidence_v1_contract(
        REPO_ROOT, campaign=BLOCK_ROBUST_GATE_CAMPAIGN
    )
    current = MechanismEvolutionV2(
        BLOCK_ROBUST_GATE_SEEDS[0],
        registry,
        catalog,
        dict(config["policy_parameters"][BLOCK_ROBUST_GATE_ARMS[1]]),
    )
    robust = MechanismEvolutionV2(
        BLOCK_ROBUST_GATE_SEEDS[0],
        registry,
        catalog,
        dict(config["policy_parameters"][BLOCK_ROBUST_GATE_ARMS[2]]),
    )
    high_reward = {
        "search_reward": 10.0,
        "family_count": 1,
        "block_robust_ordering": _ordering(
            replicated=1,
            worst=1.0,
            median=1.0,
            turnover=0.1,
            support=100.0,
        ),
    }
    replicated = {
        "search_reward": -10.0,
        "family_count": 1,
        "block_robust_ordering": _ordering(
            replicated=2,
            worst=-1.0,
            median=-1.0,
            turnover=1.0,
            support=10.0,
        ),
    }

    assert current.parameters["selection_authority"] == SEARCH_REWARD_AUTHORITY
    assert current._selection_key(
        "high", high_reward, include_family_count=False
    ) < current._selection_key(
        "replicated", replicated, include_family_count=False
    )
    assert robust._selection_key(
        "replicated", replicated, include_family_count=False
    ) < robust._selection_key(
        "high", high_reward, include_family_count=False
    )


def test_replication_evolution_checkpoint_restores_exact_policy_state() -> None:
    registry = TypedExpressionRegistry(_contracts())
    config, catalog, _ = _load_search_evidence_v1_contract(
        REPO_ROOT, campaign=BLOCK_ROBUST_GATE_CAMPAIGN
    )
    policy = MechanismEvolutionV2(
        BLOCK_ROBUST_GATE_SEEDS[0],
        registry,
        catalog,
        dict(config["policy_parameters"][BLOCK_ROBUST_GATE_ARMS[2]]),
    )
    candidate, _ = policy.propose()
    policy.observe(
        candidate,
        {
            "behavior_family_id": "family",
            "search_reward": 1.0,
            "search_reward_authority": SEARCH_REWARD_AUTHORITY,
            "policy_local_family_count_at_completion": 1,
            "block_robust_ordering": _ordering(
                replicated=2,
                worst=0.001,
                median=0.5,
                turnover=0.2,
                support=100.0,
            ),
        },
    )
    restored = MechanismEvolutionV2.from_state(registry, policy.export_state())

    assert restored.state_hash() == policy.state_hash()
    expected, expected_metadata = policy.propose()
    replayed, replayed_metadata = restored.propose()
    assert replayed.candidate_id == expected.candidate_id
    assert replayed_metadata["operation"] == expected_metadata["operation"]
    assert restored.state_hash() == policy.state_hash()


def test_three_block_projection_is_deterministic_and_train_only() -> None:
    registry = TypedExpressionRegistry(_contracts())
    config, catalog, _ = _load_search_evidence_v1_contract(
        REPO_ROOT, campaign=BLOCK_ROBUST_GATE_CAMPAIGN
    )
    policy = MechanismRandomV2(
        BLOCK_ROBUST_GATE_SEEDS[0],
        registry,
        catalog,
        dict(config["policy_parameters"][BLOCK_ROBUST_GATE_ARMS[0]]),
    )
    candidate, _ = policy.propose()
    timestamps = pd.date_range(
        "2025-08-29T07:00:00Z",
        "2025-11-01T00:00:00Z",
        freq="h",
        inclusive="left",
    ).asi8
    hours = len(timestamps)
    primary = np.repeat(np.array([[0.5], [-0.5]]), hours, axis=1)
    left_delta = np.repeat(np.array([[0.2], [-0.2]]), hours, axis=1)
    right_delta = np.repeat(np.array([[0.3], [-0.3]]), hours, axis=1)
    target = np.repeat(np.array([[0.001], [-0.001]]), hours, axis=1)
    arguments = {
        "candidate": candidate,
        "primary_weight": primary,
        "left_delta_weight": left_delta,
        "right_delta_weight": right_delta,
        "target": target,
        "evaluation_mask": np.ones(hours, dtype=bool),
        "timestamp_ns": timestamps,
        "cost_bps": 5.0,
        "full_block_start": "2025-08-29T07:00:00Z",
        "full_block_end": "2025-11-01T00:00:00Z",
        "contract": config["block_robust_contract"],
        "economic_receipt": {
            "execution": {"partition_tail_purge_hours": 6}
        },
    }

    first = _development_block_robust_ordering(**arguments)
    second = _development_block_robust_ordering(**arguments)
    assert first == second
    assert first["evaluation_partition"] == "train"
    assert first["validation_read"] is False
    assert first["block_count"] == 3
    assert first["replicated_candidate"] is True
    assert all(row["initial_establishment_charged"] for row in first["blocks"])
    assert all(row["terminal_liquidation_charged"] for row in first["blocks"])
    assert len(first["ordering_sha256"]) == 64


def test_gate_requires_broad_replication_productivity_not_one_template() -> None:
    registry = TypedExpressionRegistry(_contracts())
    config, catalog, _ = _load_search_evidence_v1_contract(
        REPO_ROOT, campaign=BLOCK_ROBUST_GATE_CAMPAIGN
    )
    policy = MechanismRandomV2(
        BLOCK_ROBUST_GATE_SEEDS[0], registry, catalog, {"allowed_horizons": [4]}
    )
    by_template: dict[str, str] = {}
    while len(by_template) < 2:
        candidate, _ = policy.propose()
        template = str(
            candidate.generation_genes["mechanism_spec"]["template_id"]
        )
        by_template.setdefault(
            template,
            json.dumps(candidate.to_dict(), sort_keys=True, separators=(",", ":")),
        )
    templates = sorted(by_template)[:2]
    rows: list[dict[str, object]] = []
    replicated_by_arm = {
        BLOCK_ROBUST_GATE_ARMS[0]: 80,
        BLOCK_ROBUST_GATE_ARMS[1]: 100,
        BLOCK_ROBUST_GATE_ARMS[2]: 200,
    }
    for arm in BLOCK_ROBUST_GATE_ARMS:
        for index in range(512):
            template = templates[index % 2]
            replicated = index < replicated_by_arm[arm]
            rows.append(
                {
                    "arm": arm,
                    "candidate_id": f"{arm}:{index}",
                    "candidate_spec_json": by_template[template],
                    "behavior_family_id": f"{arm}:family:{index}",
                    "block_robust_ordering_json": "{}",
                    "replicated_candidate": replicated,
                    "all_three_blocks_positive": replicated and index % 3 == 0,
                }
            )
    state = {
        "arm_counters": {
            arm: {
                "generation_attempts": 600,
                "cpu_seconds": 100.0 if arm != BLOCK_ROBUST_GATE_ARMS[2] else 120.0,
            }
            for arm in BLOCK_ROBUST_GATE_ARMS
        }
    }

    summary, template_rows = _block_robust_gate_summary(
        ledger=pd.DataFrame(rows), state=state, config=config
    )
    assert summary["status"] == (
        "QUALIFIED_FOR_SEPARATELY_AUTHORIZED_SMALL_DEVELOPMENT_VALIDATION"
    )
    assert all(summary["gate_checks"].values())
    assert len(summary["supported_templates_with_positive_delta"]) == 2
    assert len(template_rows) == 6
    assert summary["automatic_continuation"] is False
