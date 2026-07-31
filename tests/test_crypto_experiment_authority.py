from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from alphafactory_crypto.broad_search.experiment_authority import (
    DEFAULT_SEARCH_ECONOMIC_RECEIPT_PATH,
    REQUIRED_REAL_EXPERIMENT_ROLES,
    _file_sha256,
    _validate_search_economic_receipt,
    evaluate_search_validation_kill_line,
    require_real_experiment_authority,
    resolve_search_economic_receipt,
    resolve_real_experiment_authorities,
)
from alphafactory_crypto.broad_search.search_engine_v1 import (
    _require_bound_authority_preflight,
    _validate_receipt_target_store_binding,
    apply_search_validation_kill_line,
)
from alphafactory_crypto.instrument_canary.release import sha256_file


def test_component_source_hash_is_checkout_line_ending_stable(
    tmp_path: Path,
) -> None:
    lf = tmp_path / "source_lf.py"
    crlf = tmp_path / "source_crlf.py"
    lf.write_bytes(b"def value():\n    return 1\n")
    crlf.write_bytes(b"def value():\r\n    return 1\r\n")

    assert _file_sha256(lf) == _file_sha256(crlf)


def _write_current(
    repo_root: Path,
    *,
    inactive_roles: tuple[str, ...] = (),
    non_formal_roles: tuple[str, ...] = (),
) -> None:
    graph_root = repo_root / ".planning" / "graphs"
    graph_root.mkdir(parents=True)
    nodes = []
    bindings = []
    for role in REQUIRED_REAL_EXPERIMENT_ROLES:
        component = f"{role}_component"
        nodes.append(
            {
                "id": component,
                "lifecycle": "ACTIVE",
                "active_authority": role not in inactive_roles,
                "validation": {"result": "PASS"},
            }
        )
        bindings.append(
            {
                "semantic_role": role,
                "authoritative_component": component,
                "authority_class": (
                    "NON_FORMAL" if role in non_formal_roles else "FORMAL"
                ),
            }
        )
    (graph_root / "current.json").write_text(
        json.dumps({"nodes": nodes, "semantic_authorities": bindings}),
        encoding="utf-8",
    )


def test_active_non_formal_authority_is_visible_but_not_formal(tmp_path: Path) -> None:
    _write_current(tmp_path, non_formal_roles=("optimizer_reward",))

    result = require_real_experiment_authority(
        tmp_path,
        evidence_to_add="compare a frozen development mechanism",
        decision_to_change="keep or close that mechanism",
        economic_receipt_required=False,
    )

    assert result["result"] == "READY_WITH_NON_FORMAL_BOUNDARIES"
    assert result["formal_claims_authorized"] is False
    assert (
        result["authority_refs"]["optimizer_reward"]["status"]
        == "FOUND_BUT_UNQUALIFIED"
    )


def test_inactive_bound_component_fails_closed(tmp_path: Path) -> None:
    _write_current(tmp_path, inactive_roles=("target",))

    with pytest.raises(
        RuntimeError,
        match="REAL_EXPERIMENT_AUTHORITY_BLOCKED: target:INACTIVE_AUTHORITY",
    ):
        require_real_experiment_authority(
            tmp_path,
            evidence_to_add="compare a frozen development mechanism",
            decision_to_change="keep or close that mechanism",
            economic_receipt_required=False,
        )


def test_missing_information_intent_fails_closed(tmp_path: Path) -> None:
    _write_current(tmp_path)

    with pytest.raises(RuntimeError, match="evidence_to_add:MISSING"):
        require_real_experiment_authority(
            tmp_path,
            evidence_to_add="TBD",
            decision_to_change="keep or close that mechanism",
            economic_receipt_required=False,
        )


def test_historical_runner_preflight_is_verified_without_economic_receipt(
    tmp_path: Path,
) -> None:
    _write_current(tmp_path)
    preflight = require_real_experiment_authority(
        tmp_path,
        evidence_to_add="replay an existing spent engineering contract",
        decision_to_change="preserve its recorded historical result",
        economic_receipt_required=False,
    )

    assert preflight["economic_receipt"] is None
    tampered = {**preflight, "result": "FORGED"}
    with pytest.raises(
        RuntimeError,
        match="ECONOMIC_RECEIPT_PREFLIGHT_CHANGED",
    ):
        _require_bound_authority_preflight(
            tmp_path,
            tampered,
            economic_receipt_required=False,
        )


def test_committed_search_economic_receipt_reuses_existing_crypto_authorities() -> None:
    repo_root = Path(__file__).resolve().parents[1]

    result = resolve_search_economic_receipt(repo_root)

    assert result["result"] == "RUN_AUTHORIZED_CONDITIONAL_DEVELOPMENT"
    assert result["receipt_path"] == DEFAULT_SEARCH_ECONOMIC_RECEIPT_PATH
    assert result["market"] == {
        "asset_class": "CRYPTO",
        "calendar": "CONTINUOUS_UTC",
    }
    assert result["search_campaign"]["runner_campaign"] == (
        "crypto_search_economic_v1"
    )
    assert result["search_campaign"]["field_count"] == 115
    assert result["search_campaign"]["strict_evaluated_target"] == 20_000
    assert result["mechanism"]["registry_symbol"].endswith("skeleton_registry")
    assert result["mechanism"]["mapping_adapter_symbol"].endswith(
        "mapping_id_for_mechanism_family"
    )
    assert result["direction"]["authority_symbol"].endswith(
        "select_train_orientation"
    )
    assert result["portfolio"]["mapping_id"] == "CROSS_SECTIONAL_ZERO_NET"
    assert result["execution"]["venue"] == "BINANCE_USD_M"
    assert result["execution"]["price_field"] == "open_price"
    assert result["execution"]["execution_delay_hours"] == 2
    assert result["execution"]["partition_tail_purge_hours"] == 6
    assert result["execution"]["target_cache_path"].endswith(
        "binance_open_target_v1"
    )
    assert len(result["execution"]["target_cache_identity_sha256"]) == 64
    assert result["cost"] == {
        "model_id": "FULL_L1_FIXED_BPS",
        "cost_bps": 5.0,
        "initial_establishment_charged": True,
    }
    assert result["validation"]["optimizer_feedback_allowed"] is False
    assert result["validation_kill_line"]["runtime_symbol"].endswith(
        "apply_search_validation_kill_line"
    )
    assert result["validation_kill_line"]["evaluated_per_active_arm"] == 128
    assert result["validation_kill_line"]["orchestration_campaign"] == (
        "crypto_search_economic_v1"
    )
    assert (
        result["validation_kill_line"][
            "trigger_after_train_checkpoint_index"
        ]
        == 0
    )
    assert result["validation_kill_line"]["required_horizons_hours"] == [1, 4]
    assert (
        result["validation_kill_line"]["evaluated_per_arm_per_horizon"]
        == 64
    )
    assert result["validation_kill_line"]["candidate_selection"] == (
        "TOP_TRAIN_SEARCH_REWARD_PER_REQUIRED_HORIZON_"
        "THEN_COMPLETION_ORDINAL"
    )
    assert result["validation_kill_line"]["failed_arm_allocation"] == (
        "EXISTING_ARM_STATE_EXITED"
    )
    assert result["validation_kill_line"]["continuation_action"] == (
        "NEXT_CHECKPOINT_USES_EXISTING_ARM_STATE"
    )
    assert result["holdout"]["read_allowed"] is False
    assert result["run_authorized"] is True
    assert result["formal_claims_authorized"] is False
    assert len(result["receipt_sha256"]) == 64
    assert all(
        len(value) == 64 for value in result["component_sha256"].values()
    )


def test_search_economic_receipt_fails_closed_on_target_drift(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    source = repo_root / DEFAULT_SEARCH_ECONOMIC_RECEIPT_PATH
    receipt = json.loads(source.read_text(encoding="utf-8"))
    receipt["execution"]["price_field"] = "close_price"
    changed = tmp_path / "changed_receipt.json"
    changed.write_text(json.dumps(receipt), encoding="utf-8")

    with pytest.raises(
        RuntimeError,
        match="SEARCH_ECONOMIC_RECEIPT_BLOCKED: execution.price_field",
    ):
        _validate_search_economic_receipt(
            repo_root,
            receipt,
            receipt_path_label=str(changed),
        )


def test_search_economic_receipt_authority_remains_conditional() -> None:
    repo_root = Path(__file__).resolve().parents[1]

    receipt = resolve_search_economic_receipt(repo_root)
    preflight = require_real_experiment_authority(
        repo_root,
        evidence_to_add=(
            "fresh conditional development search productivity and matched "
            "reward evidence on the frozen 115-field carrier"
        ),
        decision_to_change=(
            "qualify or reject search arms for a future new-data arena "
            "without promotion"
        ),
    )

    assert receipt["run_authorized"] is True
    assert receipt["formal_claims_authorized"] is False
    assert receipt["cost"]["cost_bps"] == 5.0
    assert preflight["result"] == "READY_WITH_NON_FORMAL_BOUNDARIES"
    assert preflight["formal_claims_authorized"] is False
    assert {
        preflight["authority_refs"][role]["status"]
        for role in (
            "target",
            "optimizer_reward",
            "execution_price",
            "cost",
            "validation_role",
        )
    } == {"BOUND_NON_FORMAL_EXPERIMENT"}


def test_validation_kill_line_is_pure_and_fail_closed() -> None:
    passed = evaluate_search_validation_kill_line(
        {
            "validation_net_mean": 0.001,
            "validation_nonoverlap_floor_sortino": 0.2,
            "validation_matched_increment": 0.0001,
            "validation_control_not_dominant": True,
        }
    )
    assert passed["result"] == "PASS_CONTINUE_FROZEN_ARM"
    assert passed["passed"] is True
    failed = evaluate_search_validation_kill_line(
        {
            "validation_net_mean": 0.001,
            "validation_nonoverlap_floor_sortino": -0.2,
            "validation_matched_increment": 0.0001,
            "validation_control_not_dominant": True,
        }
    )
    assert failed == {
        "result": "FAIL_STOP_ARM_AND_WRITE_CHECKPOINT",
        "passed": False,
        "conditions": {
            "validation_net_mean_positive": True,
            "validation_nonoverlap_floor_sortino_positive": False,
            "validation_matched_increment_positive": True,
            "validation_control_not_dominant": True,
        },
        "optimizer_feedback_written": False,
        "policy_memory_written": False,
        "candidate_generation_performed": False,
        "holdout_read": False,
    }


def test_validation_kill_line_stops_arm_and_writes_atomic_checkpoint(
    tmp_path: Path,
) -> None:
    result = apply_search_validation_kill_line(
        runtime_root=tmp_path,
        arm_id="CEM_V2",
        metrics={
            "validation_net_mean": -0.001,
            "validation_nonoverlap_floor_sortino": 0.2,
            "validation_matched_increment": 0.0001,
            "validation_control_not_dominant": True,
        },
        matched_evaluated_counts={"random": 128, "cem_v2": 128},
        economic_receipt={
            "receipt_sha256": "A" * 64,
            "validation": {
                "role": "FRESH_DEVELOPMENT_VALIDATION_KILL_LINE",
                "optimizer_feedback_allowed": False,
                "policy_memory_write_allowed": False,
                "candidate_generation_allowed": False,
            },
            "validation_kill_line": {
                "minimum_evaluated_per_active_arm": 128,
            },
        },
    )
    checkpoint = (
        tmp_path / "checkpoints" / "validation_kill_cem_v2.json"
    )
    assert result["arm_stopped"] is True
    assert checkpoint.is_file()
    persisted = json.loads(checkpoint.read_text(encoding="utf-8"))
    assert persisted["result"] == "FAIL_STOP_ARM_AND_WRITE_CHECKPOINT"
    assert persisted["holdout_read"] is False


def test_target_override_is_bound_to_exact_source_cache_identity(
    tmp_path: Path,
) -> None:
    source_root = tmp_path / "source"
    source_root.mkdir()
    timestamp_path = source_root / "timestamp_ns.npy"
    np.save(timestamp_path, np.arange(4, dtype=np.int64))

    class _Source:
        cache_root = source_root
        shape = (2, 4)
        metadata = {"identity_sha256": "SOURCE-ID"}

    target_root = tmp_path / "target"
    target_root.mkdir()
    (target_root / "metadata.json").write_text(
        json.dumps(
            {
                "source_cache_identity_sha256": "SOURCE-ID",
                "shape": [2, 4],
                "timestamp_sha256": sha256_file(timestamp_path),
                "identity_sha256": "TARGET-ID",
            }
        ),
        encoding="utf-8",
    )
    result = _validate_receipt_target_store_binding(
        _Source(),
        target_root,
        {"target_cache_identity_sha256": "TARGET-ID"},
    )
    assert result["source_cache_identity_sha256"] == "SOURCE-ID"
    (target_root / "metadata.json").write_text(
        json.dumps(
            {
                **result,
                "source_cache_identity_sha256": "OTHER-SOURCE",
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(
        RuntimeError,
        match="ECONOMIC_RECEIPT_TARGET_SOURCE_IDENTITY_CHANGED",
    ):
        _validate_receipt_target_store_binding(
            _Source(),
            target_root,
            {"target_cache_identity_sha256": "TARGET-ID"},
        )


def test_committed_current_blocks_inactive_search_economic_roles() -> None:
    repo_root = Path(__file__).resolve().parents[1]

    resolution = resolve_real_experiment_authorities(repo_root)

    assert set(resolution["blockers"]) == {
        "target:INACTIVE_AUTHORITY",
        "optimizer_reward:INACTIVE_AUTHORITY",
        "execution_price:INACTIVE_AUTHORITY",
        "cost:INACTIVE_AUTHORITY",
        "validation_role:INACTIVE_AUTHORITY",
    }
    current = json.loads(
        (repo_root / ".planning" / "graphs" / "current.json").read_text(
            encoding="utf-8-sig"
        )
    )
    semantic_roles = {
        str(binding.get("semantic_role"))
        for binding in current.get("semantic_authorities", [])
    }
    assert "adaptive_feedback_authority" not in semantic_roles
    assert "capability_strict_feedback_authority" in semantic_roles
