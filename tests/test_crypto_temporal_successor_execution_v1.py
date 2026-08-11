from __future__ import annotations

import concurrent.futures
import json
import shutil
from collections.abc import Callable
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

from alphafactory_crypto.broad_search import temporal_program_search_v1 as runner
from alphafactory_crypto.broad_search.temporal_successor_v1 import (
    AUTHORIZED_STATUS,
    EXECUTION_MODE,
    FRESH_RANDOM_IDENTITY,
    NOT_AUTHORIZED_STATUS,
    SuccessorPreflightError,
    authorization_content_sha,
    derive_fresh_random_lane_seeds,
    reconstruct_prefix_state_tables,
    receipt_bound_role_bindings,
    successor_allocation,
    successor_budget_state,
    successor_checkpoint_decision,
    validate_authorization_payload,
    verify_successor_carrier_cache,
)
from alphafactory_crypto.broad_search import temporal_successor_v1 as successor


def _authorization(**changes: object) -> dict[str, object]:
    authority_identity = {
        "target_contract_sha256": "1" * 64,
        "target_execution_sha256": "2" * 64,
        "optimizer_reward_and_matched_attribution_sha256": "3" * 64,
        "portfolio_mapping_and_cost_sha256": "4" * 64,
    }
    executor_identity = {"host": "test-host", "workspace_path_sha256": "5" * 64}
    payload: dict[str, object] = {
        "schema_version": 2,
        "authorization_id": "CRYPTO_TEMPORAL_30K_TO_50K_SUCCESSOR_V1_AUTHORIZATION",
        "execution_mode": EXECUTION_MODE,
        "status": AUTHORIZED_STATUS,
        "run_authorized": True,
        "consumed": False,
        "successor_receipt_sha256": "A" * 64,
        "reconstruction_report_sha256": "B" * 64,
        "reconstructed_policy_bundle_sha256": "C" * 64,
        "source_artifact_identity_sha256": "D" * 64,
        "source_evidence_prefix": 30_000,
        "invalid_suffix_start": 30_001,
        "authorized_implementation_sha": "e" * 40,
        "authorized_component_sha256": {"module.py": "F" * 64},
        "expected_branch": "experiment/test",
        "runtime_id": "crypto_temporal_program_30k_to_50k_successor_v1_test",
        "random_control": {
            "identity": FRESH_RANDOM_IDENTITY,
            "seed_derivation_authority": (
                "FIRST_UINT32_SHA256_CRYPTO_TEMPORAL_30K_TO_50K_SUCCESSOR_V1_PIPE_LANE_INDEX"
            ),
            "rng_implementation_identity": "python.random.Random|CPYTHON_MT19937_V1",
            "lane_seeds": list(derive_fresh_random_lane_seeds()),
        },
        "allocation": {
            FRESH_RANDOM_IDENTITY: 0.2,
            "temporal_program_evolution": 0.6,
            "temporal_program_cem": 0.2,
        },
        "checkpoint_contract": {
            "additional_strict_per_decision": 5_000,
            "maximum_additional_strict": 20_000,
            "maximum_cumulative_valid_strict": 50_000,
            "family_concentration_is_diagnostic_only": True,
            "pruned_adaptive_budget_reallocation": (
                "KEEP_RANDOM_20_PERCENT_AND_ASSIGN_ALL_ADAPTIVE_80_PERCENT_TO_SURVIVING_ADAPTIVE_ARMS_PROPORTIONAL_TO_3_TO_1_BASE_WEIGHTS"
            ),
        },
        "authority_identity": authority_identity,
        "receipt_bound_role_bindings": receipt_bound_role_bindings(
            authority_identity
        ),
        "market_input_preflight": {
            "carrier_manifest_path": successor.CARRIER_MANIFEST_PATH,
            "carrier_manifest_sha256": "6" * 64,
            "cache_root": ".cache/test-carrier",
            "cache_identity_sha256": "7" * 64,
            "directory_bundle": {
                "file_count": 1,
                "bytes": 1,
                "bundle_sha256": "8" * 64,
            },
        },
        "executor_identity": executor_identity,
        "run_authorization": {
            "authority": "CURRENT_USER_INSTRUCTION",
            "decision_id": "TEST_SUCCESSOR_AUTHORIZATION",
            "scope": "ONE_30K_TO_50K_TRAIN_ONLY_TEMPORAL_PROGRAM_DEVELOPMENT_SUCCESSOR",
        },
        "evidence_to_add": "synthetic successor evidence",
        "decision_to_change": "synthetic continuation decision",
        "boundaries": {
            "train_only": True,
            "validation": False,
            "oos": False,
            "holdout": False,
            "forward": False,
            "promotion": False,
            "automatic_expansion": False,
            "sealed_reads": 0,
        },
    }
    payload.update(changes)
    payload["authorization_sha256"] = authorization_content_sha(payload)
    return payload


def test_fresh_random_seed_authority_is_deterministic_and_not_historical_resume() -> None:
    first = derive_fresh_random_lane_seeds()
    assert first == derive_fresh_random_lane_seeds()
    assert len(first) == len(set(first)) == 4
    assert all(0 <= value < 2**32 for value in first)
    assert FRESH_RANDOM_IDENTITY == "FRESH_RANDOM_CONTROL_AFTER_30K"


def test_successor_carrier_cache_preflight_is_content_bound_and_market_free(
    tmp_path: Path,
) -> None:
    cache_root = tmp_path / ".cache" / "test-carrier"
    fields_root = cache_root / "fields"
    fields_root.mkdir(parents=True)
    identity = "A" * 64
    (cache_root / "metadata.json").write_text(
        json.dumps({"identity_sha256": identity, "field_ids": ["field_a"]}) + "\n",
        encoding="utf-8",
    )
    for name in (
        "timestamp_ns.npy",
        "observed.npy",
        "base_eligible.npy",
        "source_segment.npy",
        "target_return_1h.npy",
        "target_return_4h.npy",
    ):
        (cache_root / name).write_bytes(name.encode("ascii"))
    (fields_root / "field_a.npy").write_bytes(b"field-a")
    bundle = successor.carrier_directory_bundle(cache_root)
    manifest_path = tmp_path / "aligned_carrier_manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "cache_root": ".cache/test-carrier",
                "cache_identity_sha256": identity,
                "directory_bundle": bundle,
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = verify_successor_carrier_cache(
        tmp_path, manifest_path=manifest_path
    )
    assert result["directory_bundle"] == bundle
    assert result["market_arrays_read"] == 0
    assert result["sealed_reads"] == 0

    (fields_root / "field_a.npy").write_bytes(b"tampered")
    with pytest.raises(
        SuccessorPreflightError, match="carrier_cache_directory_bundle"
    ):
        verify_successor_carrier_cache(tmp_path, manifest_path=manifest_path)


def test_successor_carrier_cache_missing_fails_before_launch_claim(
    tmp_path: Path,
) -> None:
    manifest_path = tmp_path / "aligned_carrier_manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "cache_root": ".cache/missing",
                "cache_identity_sha256": "A" * 64,
                "directory_bundle": {
                    "file_count": 1,
                    "bytes": 1,
                    "bundle_sha256": "B" * 64,
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    with pytest.raises(SuccessorPreflightError, match="carrier_cache_unavailable"):
        verify_successor_carrier_cache(tmp_path, manifest_path=manifest_path)


def test_authorization_payload_distinguishes_ready_from_one_time_authorized() -> None:
    ready = _authorization(
        status=NOT_AUTHORIZED_STATUS,
        run_authorized=False,
        authorized_implementation_sha=None,
        authorized_component_sha256={},
        runtime_id=None,
        executor_identity=None,
        run_authorization=None,
    )
    with pytest.raises(SuccessorPreflightError, match="FAIL_CLOSED_BEFORE_MARKET_READ"):
        validate_authorization_payload(
            ready,
            expected_successor_receipt_sha256="A" * 64,
            expected_reconstruction_report_sha256="B" * 64,
            expected_bundle_sha256="C" * 64,
            expected_source_identity_sha256="D" * 64,
            expected_authority_identity=dict(ready["authority_identity"]),
            expected_executor_identity={
                "host": "test-host",
                "workspace_path_sha256": "5" * 64,
            },
        )

    authorized = _authorization()
    validated = validate_authorization_payload(
        authorized,
        expected_successor_receipt_sha256="A" * 64,
        expected_reconstruction_report_sha256="B" * 64,
        expected_bundle_sha256="C" * 64,
        expected_source_identity_sha256="D" * 64,
        expected_authority_identity=dict(authorized["authority_identity"]),
        expected_executor_identity=dict(authorized["executor_identity"]),
    )
    assert validated["status"] == AUTHORIZED_STATUS

    tampered = dict(authorized)
    tampered["source_evidence_prefix"] = 30_001
    with pytest.raises(SuccessorPreflightError, match="authorization_sha256"):
        validate_authorization_payload(
            tampered,
            expected_successor_receipt_sha256="A" * 64,
            expected_reconstruction_report_sha256="B" * 64,
            expected_bundle_sha256="C" * 64,
            expected_source_identity_sha256="D" * 64,
            expected_authority_identity=dict(authorized["authority_identity"]),
            expected_executor_identity=dict(authorized["executor_identity"]),
        )


@pytest.mark.parametrize(
    ("mutation", "expected_error"),
    [
        (lambda payload: payload.update(schema_version=1), "schema_version"),
        (lambda payload: payload.update(consumed=True), "authorization_consumed"),
        (
            lambda payload: payload.update(successor_receipt_sha256="9" * 64),
            "successor_receipt_sha256",
        ),
        (
            lambda payload: payload.update(
                reconstructed_policy_bundle_sha256="9" * 64
            ),
            "reconstructed_policy_bundle_sha256",
        ),
        (
            lambda payload: payload.update(authorized_implementation_sha="0" * 39),
            "authorized_implementation_sha",
        ),
        (
            lambda payload: payload.update(
                executor_identity={
                    "host": "other-host",
                    "workspace_path_sha256": "5" * 64,
                }
            ),
            "executor_identity",
        ),
        (
            lambda payload: payload["run_authorization"].update(
                scope="UNREGISTERED_SCOPE"
            ),
            "run_authorization",
        ),
        (
            lambda payload: payload["authority_identity"].update(
                target_contract_sha256="9" * 64
            ),
            "authority_identity",
        ),
        (
            lambda payload: payload["authority_identity"].update(
                target_execution_sha256="9" * 64
            ),
            "authority_identity",
        ),
        (
            lambda payload: payload["authority_identity"].update(
                portfolio_mapping_and_cost_sha256="9" * 64
            ),
            "authority_identity",
        ),
        (
            lambda payload: payload["authority_identity"].update(
                optimizer_reward_and_matched_attribution_sha256="9" * 64
            ),
            "authority_identity",
        ),
        (
            lambda payload: payload["receipt_bound_role_bindings"][
                "execution_price"
            ].update(component_sha256="9" * 64),
            "receipt_bound_role_bindings",
        ),
        (
            lambda payload: payload["boundaries"].update(validation=True),
            "sealed_boundaries",
        ),
    ],
)
def test_authorization_payload_negative_matrix_fails_before_market_read(
    mutation: Callable[[dict[str, object]], object],
    expected_error: str,
) -> None:
    authorized = _authorization()
    mutation(authorized)
    authorized["authorization_sha256"] = authorization_content_sha(authorized)

    with pytest.raises(SuccessorPreflightError, match=expected_error):
        validate_authorization_payload(
            authorized,
            expected_successor_receipt_sha256="A" * 64,
            expected_reconstruction_report_sha256="B" * 64,
            expected_bundle_sha256="C" * 64,
            expected_source_identity_sha256="D" * 64,
            expected_authority_identity={
                "target_contract_sha256": "1" * 64,
                "target_execution_sha256": "2" * 64,
                "optimizer_reward_and_matched_attribution_sha256": "3" * 64,
                "portfolio_mapping_and_cost_sha256": "4" * 64,
            },
            expected_executor_identity={
                "host": "test-host",
                "workspace_path_sha256": "5" * 64,
            },
        )


def test_valid_prefix_state_restoration_excludes_suffix_and_rebuilds_archive() -> None:
    candidates = pd.DataFrame(
        [
            {
                "completion_ordinal": 1,
                "checkpoint_index": 0,
                "candidate_id": "candidate-a",
                "arm": "temporal_program_evolution",
                "seed": 7,
                "behavior_family_id": "family-1",
                "policy_local_family_count_at_completion": 1,
                "operation": "MUTATE",
                "parent_ids_json": "[]",
            },
            {
                "completion_ordinal": 2,
                "checkpoint_index": 0,
                "candidate_id": "candidate-b",
                "arm": "temporal_program_evolution",
                "seed": 7,
                "behavior_family_id": "family-1",
                "policy_local_family_count_at_completion": 2,
                "operation": "MUTATE",
                "parent_ids_json": '["candidate-a"]',
            },
            {
                "completion_ordinal": 3,
                "checkpoint_index": 1,
                "candidate_id": "suffix-candidate",
                "arm": "temporal_program_random",
                "seed": 9,
                "behavior_family_id": "family-2",
                "policy_local_family_count_at_completion": 1,
                "operation": "RANDOM",
                "parent_ids_json": "[]",
            },
        ]
    )
    archive_rows = pd.DataFrame(
        [
            {
                "completion_ordinal": 1,
                "exact_expression_id": "candidate-a",
                "behavior_family_id": "family-1",
                "search_reward": 0.1,
                "search_reward_authority": "CRYPTO_TRAIN_JOINT_PRIMARY_MATCHED_SORTINO_V2",
                "is_family_champion": False,
            },
            {
                "completion_ordinal": 2,
                "exact_expression_id": "candidate-b",
                "behavior_family_id": "family-1",
                "search_reward": 0.2,
                "search_reward_authority": "CRYPTO_TRAIN_JOINT_PRIMARY_MATCHED_SORTINO_V2",
                "is_family_champion": False,
            },
            {
                "completion_ordinal": 3,
                "exact_expression_id": "suffix-candidate",
                "behavior_family_id": "family-2",
                "search_reward": 1.0,
                "search_reward_authority": "CRYPTO_TRAIN_JOINT_PRIMARY_MATCHED_SORTINO_V2",
                "is_family_champion": True,
            },
        ]
    )
    rejected = pd.DataFrame(
        [
            {
                "checkpoint_index": 0,
                "policy_key": "temporal_program_evolution|7",
                "candidate_id": "prefix-reject",
                "status": "EXACT_OR_REPLAY_REJECT",
            },
            {
                "checkpoint_index": 1,
                "policy_key": "temporal_program_random|9",
                "candidate_id": "suffix-reject",
                "status": "EXACT_OR_REPLAY_REJECT",
            },
        ]
    )
    restored = reconstruct_prefix_state_tables(
        candidates=candidates,
        archive_rows=archive_rows,
        rejected=rejected,
        source_attempted_exact_ids={
            "candidate-a",
            "candidate-b",
            "prefix-reject",
            "suffix-candidate",
            "suffix-reject",
        },
        source_completed_pair_ids=set(),
        prefix_boundary=2,
        checkpoint_size=2,
    )
    assert [row["candidate_id"] for row in restored["ledger"]] == [
        "candidate-a",
        "candidate-b",
    ]
    assert set(restored["attempted_exact_ids"]) == {
        "candidate-a",
        "candidate-b",
        "prefix-reject",
    }
    assert restored["suffix_contribution"] == {
        "candidate_rows": 0,
        "archive_rows": 0,
        "attempted_exact_ids": 0,
        "completed_pair_ids": 0,
        "policy_local_family_counts": 0,
    }
    assert restored["archive"].champion_by_family == {"family-1": 1}
    assert restored["archive"].duplicate_replacements == 1
    assert restored["policy_local_family_counts"] == {
        "temporal_program_evolution|7": {"family-1": 2}
    }


def test_suffix_state_injection_is_rejected_by_physical_successor_preflight() -> None:
    with pytest.raises(
        SuccessorPreflightError, match="invalid_suffix_state_injection"
    ):
        successor._require_zero_suffix_contribution(
            {
                "suffix_contribution": {
                    "candidate_rows": 1,
                    "archive_rows": 0,
                    "attempted_exact_ids": 0,
                    "completed_pair_ids": 0,
                    "policy_local_family_counts": 0,
                }
            }
        )


def test_successor_allocation_and_budget_are_additional_not_fresh_campaign() -> None:
    assert successor_allocation(
        {
            "temporal_program_evolution": "ACTIVE",
            "temporal_program_cem": "ACTIVE",
        }
    ) == {
        "temporal_program_random": 1_000,
        "temporal_program_evolution": 3_000,
        "temporal_program_cem": 1_000,
    }
    assert successor_allocation(
        {
            "temporal_program_evolution": "ACTIVE",
            "temporal_program_cem": "EXITED",
        }
    ) == {
        "temporal_program_random": 1_000,
        "temporal_program_evolution": 4_000,
        "temporal_program_cem": 0,
    }
    with pytest.raises(RuntimeError, match="no adaptive arm remains"):
        successor_allocation(
            {
                "temporal_program_evolution": "EXITED",
                "temporal_program_cem": "EXITED",
            }
        )
    assert successor_budget_state(30_000) == {
        "source_evidence_prefix": 30_000,
        "additional_strict_evaluated": 0,
        "cumulative_valid_strict": 30_000,
        "additional_budget_remaining": 20_000,
        "mechanical_stop_required": False,
    }
    assert successor_budget_state(50_000)["mechanical_stop_required"] is True
    with pytest.raises(RuntimeError, match="successor strict budget exceeded"):
        successor_budget_state(50_001)


def test_successor_restores_all_adaptive_lanes_and_fresh_initializes_random(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    adaptive_states = {
        f"{arm}|{seed}": {"kind": "state", "key": f"{arm}|{seed}"}
        for arm in ("temporal_program_cem", "temporal_program_evolution")
        for seed in runner.ADAPTIVE_BROAD_SEEDS
    }
    restored: list[str] = []
    fresh: list[tuple[str, int, tuple[str, ...]]] = []
    monkeypatch.setattr(
        runner.engine,
        "_restore_policy",
        lambda registry, state: restored.append(str(state["key"])) or state["key"],
    )
    monkeypatch.setattr(
        runner,
        "_make_policy",
        lambda *, arm, seed, registry, config, catalog: fresh.append(
            (arm, seed, tuple(pair[1].family_id for pair in catalog))
        )
        or (arm, seed),
    )
    catalog = tuple(
        (object(), SimpleNamespace(family_id=family))
        for family in (
            "P1_POSITION_STATE_CHANGE_TO_RESPONSE",
            "P2_RECENT_CROWDING_EVENT_TO_RESPONSE",
            "P3_FLOW_SHOCK_PERSISTENCE_TO_ABSORPTION",
            "P4_MULTISCALE_STATE_X_TRANSITION_ROUTING",
        )
    )
    seeds = derive_fresh_random_lane_seeds()
    policies = runner._restore_successor_policies(
        registry=object(),
        config={},
        catalog=catalog,
        successor_context={
            "reconstructed_policy_bundle": {"policies": adaptive_states},
            "fresh_random_lane_seeds": seeds,
        },
    )
    assert set(restored) == set(adaptive_states)
    assert len(policies) == 16
    assert {key for key in policies if key.startswith("temporal_program_random|")} == {
        f"temporal_program_random|{seed}" for seed in seeds
    }
    assert not set(seeds) & set(runner.ADAPTIVE_BROAD_SEEDS)
    assert len(fresh) == 8


def test_successor_checkpoint_decision_prunes_only_on_economic_gate_state() -> None:
    decision = successor_checkpoint_decision(
        {
            "status": "CONTINUE",
            "arm_states_before": {
                "temporal_program_cem": "DIAGNOSTIC",
                "temporal_program_evolution": "ACTIVE",
            },
            "arm_states_after": {
                "temporal_program_cem": "EXITED",
                "temporal_program_evolution": "ACTIVE",
            },
            "arm_decisions": {
                "temporal_program_cem": {
                    "family_concentration_diagnostic": "ABOVE_DIAGNOSTIC_THRESHOLD"
                }
            },
        }
    )
    assert decision["status"] == "PRUNE_ARM_AND_CONTINUE"
    assert decision["next_allocation"] == {
        "temporal_program_random": 1_000,
        "temporal_program_evolution": 4_000,
        "temporal_program_cem": 0,
    }
    assert decision["family_concentration_is_diagnostic_only"] is True


def test_successor_four_tranche_schedule_reaches_only_the_20k_hard_stop() -> None:
    decisions = []
    for cumulative in (35_000, 40_000, 45_000, 50_000):
        budget = successor_budget_state(cumulative)
        decision = successor_checkpoint_decision(
            {
                "status": "CONTINUE",
                "arm_states_before": {
                    "temporal_program_cem": "ACTIVE",
                    "temporal_program_evolution": "ACTIVE",
                },
                "arm_states_after": {
                    "temporal_program_cem": "ACTIVE",
                    "temporal_program_evolution": "ACTIVE",
                },
                "arm_decisions": {},
            }
        )
        decisions.append(
            (
                budget["additional_strict_evaluated"],
                budget["cumulative_valid_strict"],
                budget["mechanical_stop_required"],
                decision["status"],
                decision["next_allocation"],
            )
        )

    assert [row[:4] for row in decisions] == [
        (5_000, 35_000, False, "CONTINUE"),
        (10_000, 40_000, False, "CONTINUE"),
        (15_000, 45_000, False, "CONTINUE"),
        (20_000, 50_000, True, "CONTINUE"),
    ]
    assert all(
        row[4]
        == {
            "temporal_program_random": 1_000,
            "temporal_program_evolution": 3_000,
            "temporal_program_cem": 1_000,
        }
        for row in decisions
    )


def test_canonical_successor_fails_before_any_market_authority_read(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    market_read = False

    def forbidden_market_read(*args: object, **kwargs: object) -> None:
        nonlocal market_read
        market_read = True
        raise AssertionError("market authority must not be read")

    monkeypatch.setattr(runner, "resolve_search_economic_receipt", forbidden_market_read)
    monkeypatch.setattr(
        runner,
        "prepare_successor_execution",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            SuccessorPreflightError("FAIL_CLOSED_BEFORE_MARKET_READ:authorization")
        ),
        raising=False,
    )
    with pytest.raises(SuccessorPreflightError, match="FAIL_CLOSED_BEFORE_MARKET_READ"):
        runner.run(
            Path(__file__).resolve().parents[1],
            runtime_date="20990101",
            execution_mode=EXECUTION_MODE,
            successor_artifact_root=tmp_path / "source",
            successor_policy_bundle=tmp_path / "bundle.json.gz",
        )
    assert market_read is False


def test_canonical_successor_calls_current_preflight_before_market_authority(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    runtime_date = "20990103_current_preflight"
    runtime_root = (
        repo_root / "runtime" / f"{runner.SUCCESSOR_CAMPAIGN}_{runtime_date}"
    )
    shutil.rmtree(runtime_root, ignore_errors=True)
    observed: list[str] = []
    authorization = _authorization(
        runtime_id=runtime_root.name,
        executor_identity={
            "host": "synthetic-host",
            "workspace_path_sha256": "5" * 64,
        },
    )

    monkeypatch.setattr(
        runner,
        "prepare_successor_execution",
        lambda *args, **kwargs: {
            "authorization": authorization,
            "authorization_sha256": authorization["authorization_sha256"],
        },
    )
    monkeypatch.setattr(
        runner.engine, "_source_tree_clean_for_run", lambda *args, **kwargs: True
    )

    def current_preflight(*args: object, **kwargs: object) -> dict[str, object]:
        observed.append("CURRENT")
        assert kwargs["evidence_to_add"] == authorization["evidence_to_add"]
        assert kwargs["decision_to_change"] == authorization["decision_to_change"]
        assert kwargs["receipt_bound_non_formal_authorization"] == {
            "decision_id": "TEST_SUCCESSOR_AUTHORIZATION",
            "authority": "CURRENT_USER_INSTRUCTION",
            "scope": (
                "ONE_30K_TO_50K_TRAIN_ONLY_TEMPORAL_PROGRAM_DEVELOPMENT_SUCCESSOR"
            ),
            "receipt_path": runner.SUCCESSOR_AUTHORIZATION_PATH,
            "receipt_sha256": runner._json_sha(authorization),
            "run_authorized": True,
        }
        return {"result": "READY_WITH_NON_FORMAL_BOUNDARIES"}

    def stop_at_market(*args: object, **kwargs: object) -> None:
        observed.append("MARKET")
        raise RuntimeError("synthetic stop at market authority")

    monkeypatch.setattr(runner, "require_real_experiment_authority", current_preflight)
    monkeypatch.setattr(runner, "resolve_search_economic_receipt", stop_at_market)
    try:
        with pytest.raises(RuntimeError, match="synthetic stop at market authority"):
            runner.run(
                repo_root,
                runtime_date=runtime_date,
                execution_mode=EXECUTION_MODE,
                successor_artifact_root=repo_root / "unused-source",
                successor_policy_bundle=repo_root / "unused-bundle.json.gz",
            )
        assert observed == ["CURRENT", "MARKET"]
        assert (runtime_root / "successor_launch_claim.json").is_file()
    finally:
        shutil.rmtree(runtime_root, ignore_errors=True)


def test_successor_launch_claim_blocks_second_launch_before_market_read(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    runtime_date = "20990102_launch_claim"
    runtime_root = (
        repo_root
        / "runtime"
        / f"{runner.SUCCESSOR_CAMPAIGN}_{runtime_date}"
    )
    shutil.rmtree(runtime_root, ignore_errors=True)
    market_reads = 0

    def stop_at_first_market_authority(*args: object, **kwargs: object) -> None:
        nonlocal market_reads
        market_reads += 1
        raise RuntimeError("test stop after launch claim")

    monkeypatch.setattr(
        runner,
        "prepare_successor_execution",
        lambda *args, **kwargs: {
            "authorization": {"authorization_sha256": "A" * 64},
            "authorization_sha256": "A" * 64,
        },
    )
    monkeypatch.setattr(
        runner.engine, "_source_tree_clean_for_run", lambda *args, **kwargs: True
    )
    monkeypatch.setattr(
        runner,
        "require_real_experiment_authority",
        lambda *args, **kwargs: {
            "result": "READY_WITH_NON_FORMAL_BOUNDARIES",
            "formal_claims_authorized": False,
        },
    )
    monkeypatch.setattr(
        runner, "resolve_search_economic_receipt", stop_at_first_market_authority
    )
    try:
        with pytest.raises(RuntimeError, match="test stop after launch claim"):
            runner.run(
                repo_root,
                runtime_date=runtime_date,
                execution_mode=EXECUTION_MODE,
                successor_artifact_root=repo_root / "unused-source",
                successor_policy_bundle=repo_root / "unused-bundle.json.gz",
            )
        claim = json.loads(
            (runtime_root / "successor_launch_claim.json").read_text(
                encoding="utf-8"
            )
        )
        assert claim["market_arrays_read_at_claim"] == 0
        assert market_reads == 1

        with pytest.raises(RuntimeError, match="non_fresh_output_root"):
            runner.run(
                repo_root,
                runtime_date=runtime_date,
                execution_mode=EXECUTION_MODE,
                successor_artifact_root=repo_root / "unused-source",
                successor_policy_bundle=repo_root / "unused-bundle.json.gz",
            )
        assert market_reads == 1
    finally:
        shutil.rmtree(runtime_root, ignore_errors=True)


@pytest.mark.parametrize(
    "changed_component",
    [
        "target_contract",
        "target_execution",
        "portfolio_mapping_and_cost",
        "optimizer_reward_and_matched_attribution",
    ],
)
def test_canonical_successor_economic_authority_drift_stops_before_market_arrays(
    monkeypatch: pytest.MonkeyPatch,
    changed_component: str,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    runtime_date = "20990105_" + changed_component
    runtime_root = repo_root / "runtime" / f"{runner.SUCCESSOR_CAMPAIGN}_{runtime_date}"
    shutil.rmtree(runtime_root, ignore_errors=True)
    market_arrays_read = False
    authority = {
        "economic_receipt_sha256": "7" * 64,
        "target_contract_sha256": "1" * 64,
        "target_execution_sha256": "2" * 64,
        "optimizer_reward_and_matched_attribution_sha256": "3" * 64,
        "portfolio_mapping_and_cost_sha256": "4" * 64,
        "program_catalog_sha256": "6" * 64,
    }
    authorization = _authorization(authority_identity=authority)
    authorization["receipt_bound_role_bindings"] = receipt_bound_role_bindings(
        authority
    )
    authorization["runtime_id"] = runtime_root.name
    authorization["authorization_sha256"] = authorization_content_sha(authorization)
    observed = {
        "target_contract": authority["target_contract_sha256"],
        "target_execution": authority["target_execution_sha256"],
        "portfolio_mapping_and_cost": authority[
            "portfolio_mapping_and_cost_sha256"
        ],
        "optimizer_reward_and_matched_attribution": authority[
            "optimizer_reward_and_matched_attribution_sha256"
        ],
    }
    observed[changed_component] = "9" * 64

    monkeypatch.setattr(
        runner,
        "prepare_successor_execution",
        lambda *args, **kwargs: {
            "authorization": authorization,
            "authorization_sha256": authorization["authorization_sha256"],
        },
    )
    monkeypatch.setattr(
        runner.engine, "_source_tree_clean_for_run", lambda *args, **kwargs: True
    )
    monkeypatch.setattr(
        runner,
        "require_real_experiment_authority",
        lambda *args, **kwargs: {"result": "READY_WITH_NON_FORMAL_BOUNDARIES"},
    )
    monkeypatch.setattr(
        runner,
        "resolve_search_economic_receipt",
        lambda *args, **kwargs: {
            "receipt_sha256": authority["economic_receipt_sha256"],
            "component_sha256": observed,
        },
    )

    def forbidden_market_arrays(*args: object, **kwargs: object) -> None:
        nonlocal market_arrays_read
        market_arrays_read = True
        raise AssertionError("market arrays must remain unread")

    monkeypatch.setattr(runner.engine, "_load_v14_inputs", forbidden_market_arrays)
    try:
        with pytest.raises(
            SuccessorPreflightError, match="current_economic_authority_changed"
        ):
            runner.run(
                repo_root,
                runtime_date=runtime_date,
                execution_mode=EXECUTION_MODE,
                successor_artifact_root=repo_root / "unused-source",
                successor_policy_bundle=repo_root / "unused-bundle.json.gz",
            )
        assert market_arrays_read is False
    finally:
        shutil.rmtree(runtime_root, ignore_errors=True)


def test_terminal_successor_runtime_cannot_resume_before_market_read(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    runtime_date = "20990106_terminal_resume"
    runtime_root = repo_root / "runtime" / f"{runner.SUCCESSOR_CAMPAIGN}_{runtime_date}"
    shutil.rmtree(runtime_root, ignore_errors=True)
    (runtime_root / "checkpoints" / "checkpoint_budget_exhausted").mkdir(
        parents=True
    )
    market_read = False

    def forbidden_market_read(*args: object, **kwargs: object) -> None:
        nonlocal market_read
        market_read = True
        raise AssertionError("terminal successor must not reach market authority")

    monkeypatch.setattr(
        runner,
        "prepare_successor_execution",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            SuccessorPreflightError("FAIL_CLOSED_BEFORE_MARKET_READ:non_fresh_output_root")
        ),
    )
    monkeypatch.setattr(runner, "resolve_search_economic_receipt", forbidden_market_read)
    try:
        with pytest.raises(SuccessorPreflightError, match="non_fresh_output_root"):
            runner.run(
                repo_root,
                runtime_date=runtime_date,
                execution_mode=EXECUTION_MODE,
                successor_artifact_root=repo_root / "unused-source",
                successor_policy_bundle=repo_root / "unused-bundle.json.gz",
            )
        assert market_read is False
    finally:
        shutil.rmtree(runtime_root, ignore_errors=True)


def test_canonical_run_executes_four_synthetic_successor_tranches_and_seals(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    runtime_date = "20990107_four_tranches"
    runtime_root = repo_root / "runtime" / f"{runner.SUCCESSOR_CAMPAIGN}_{runtime_date}"
    report_path = (
        repo_root
        / "reports"
        / f"CRYPTO_TEMPORAL_30K_TO_50K_SUCCESSOR_V1_{runtime_date}.md"
    )
    shutil.rmtree(runtime_root, ignore_errors=True)
    report_path.unlink(missing_ok=True)

    class Candidate:
        def __init__(self, candidate_id: str) -> None:
            self.candidate_id = candidate_id

        def to_dict(self) -> dict[str, str]:
            return {"candidate_id": self.candidate_id}

    class Policy:
        def update(self, rows: object) -> None:
            return None

        def state_hash(self) -> str:
            return "policy-state"

    class ImmediateExecutor:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def submit(self, function: object, *args: object, **kwargs: object):
            future: concurrent.futures.Future[dict[str, object]] = (
                concurrent.futures.Future()
            )
            future.set_result(
                {
                    "system_error": False,
                    "memory_error": False,
                    "evaluation": {"matched_positive": False},
                }
            )
            return future

        def shutdown(self, *args: object, **kwargs: object) -> None:
            return None

    authority = {
        "economic_receipt_sha256": "7" * 64,
        "target_contract_sha256": "1" * 64,
        "target_execution_sha256": "2" * 64,
        "optimizer_reward_and_matched_attribution_sha256": "3" * 64,
        "portfolio_mapping_and_cost_sha256": "4" * 64,
        "program_catalog_sha256": "6" * 64,
    }
    authorization = _authorization(authority_identity=authority)
    authorization["receipt_bound_role_bindings"] = receipt_bound_role_bindings(
        authority
    )
    authorization["runtime_id"] = runtime_root.name
    authorization["authorization_sha256"] = authorization_content_sha(authorization)
    prefix_ledger = [
        {
            "completion_ordinal": ordinal,
            "candidate_id": f"prefix-{ordinal}",
            "checkpoint_index": (ordinal - 1) // 2_000,
            "matched_positive": False,
            "behavior_family_id": "prefix-family",
            "program_family_id": "P4_MULTISCALE_STATE_X_TRANSITION_ROUTING",
        }
        for ordinal in range(1, 30_001)
    ]
    restored = {
        "ledger": prefix_ledger,
        "archive": runner.engine.BehaviorArchive(),
        "attempted_exact_ids": [],
        "completed_pair_ids": [],
        "policy_local_family_counts": {},
        "state_restoration_sha256": "8" * 64,
        "suffix_contribution": {
            "candidate_rows": 0,
            "archive_rows": 0,
            "attempted_exact_ids": 0,
            "completed_pair_ids": 0,
            "policy_local_family_counts": 0,
        },
    }
    successor_context = {
        "status": "SUCCESSOR_PREFLIGHT_PASS",
        "authorization": authorization,
        "authorization_sha256": authorization["authorization_sha256"],
        "successor_receipt_sha256": authorization["successor_receipt_sha256"],
        "reconstructed_policy_bundle": {"policies": {}},
        "restored_prefix": restored,
        "fresh_random_lane_seeds": list(derive_fresh_random_lane_seeds()),
    }
    economic = {
        "receipt_sha256": authority["economic_receipt_sha256"],
        "component_sha256": {
            "target_contract": authority["target_contract_sha256"],
            "target_execution": authority["target_execution_sha256"],
            "portfolio_mapping_and_cost": authority[
                "portfolio_mapping_and_cost_sha256"
            ],
            "optimizer_reward_and_matched_attribution": authority[
                "optimizer_reward_and_matched_attribution_sha256"
            ],
        },
        "evidence_partition": {
            "train": {"start": "2024-01-01", "end_exclusive": "2024-02-01"}
        },
    }
    proposed = 0

    def propose(*args: object, **kwargs: object):
        nonlocal proposed
        proposed += 1
        return Candidate(f"successor-{proposed:05d}"), {
            "raw_attempts": 1,
            "compile_valid_attempts": 1,
            "operation": "SYNTHETIC",
            "parent_ids": [],
            "receipt": None,
            "receipt_verified": True,
            "policy_state_hash_before": "before",
            "policy_state_hash_after_proposal": "after",
        }

    def observe(
        *,
        candidate: Candidate,
        proposal: dict[str, object],
        state: dict[str, object],
        ledger: list[dict[str, object]],
        checkpoint_index: int,
        **kwargs: object,
    ) -> None:
        arm = str(proposal["arm"])
        ledger.append(
            {
                "completion_ordinal": len(ledger) + 1,
                "candidate_id": candidate.candidate_id,
                "checkpoint_index": checkpoint_index,
                "policy_key": str(proposal["policy_key"]),
                "arm": arm,
                "seed": int(proposal["seed"]),
                "matched_positive": False,
                "behavior_family_id": candidate.candidate_id,
                "program_family_id": "P4_MULTISCALE_STATE_X_TRANSITION_ROUTING",
                "representation": "TEMPORAL_PROGRAM",
            }
        )
        state["strict_evaluated"] = len(ledger)
        state["arm_counters"][arm]["strict_evaluated"] += 1

    def write_views(
        root: Path,
        *,
        state: dict[str, object],
        **kwargs: object,
    ) -> None:
        root.mkdir(parents=True, exist_ok=True)
        runner.engine._write_json(root / "work_state.json", dict(state))
        for name in (
            "candidate_ledger.parquet",
            "behavior_archive.parquet",
            "paired_program_diagnostics.parquet",
            "program_family_metrics.parquet",
            "arm_checkpoint_metrics.parquet",
            "rejected_candidate_ledger.parquet",
        ):
            (root / name).write_bytes(b"synthetic")

    def write_checkpoint(
        root: Path,
        *,
        checkpoint_index: int,
        state: dict[str, object],
        ledger: list[dict[str, object]],
        label: str | None = None,
        **kwargs: object,
    ) -> Path:
        target = root / "checkpoints" / str(
            label or f"checkpoint_{checkpoint_index:03d}"
        )
        target.mkdir(parents=True)
        runner.engine._write_json(
            target / "manifest.json",
            {
                "schema_version": 1,
                "checkpoint_index": checkpoint_index,
                "completed_ledger_row_count": len(ledger),
                "restore_verified": True,
                "terminal_decision": state.get("terminal_decision"),
                "files": [],
            },
        )
        return target

    policy_keys = {
        f"{arm}|{seed}"
        for arm in ("temporal_program_cem", "temporal_program_evolution")
        for seed in runner.ADAPTIVE_BROAD_SEEDS
    }
    policy_keys.update(
        f"temporal_program_random|{seed}"
        for seed in derive_fresh_random_lane_seeds()
    )
    policy_keys.update(
        f"temporal_program_random_diagnostic|{seed}"
        for seed in derive_fresh_random_lane_seeds()
    )
    policies = {key: Policy() for key in policy_keys}

    monkeypatch.setattr(
        runner, "prepare_successor_execution", lambda *a, **k: successor_context
    )
    monkeypatch.setattr(
        runner.engine, "_source_tree_clean_for_run", lambda *a, **k: True
    )
    monkeypatch.setattr(
        runner,
        "require_real_experiment_authority",
        lambda *a, **k: {"result": "READY_WITH_NON_FORMAL_BOUNDARIES"},
    )
    monkeypatch.setattr(runner, "resolve_search_economic_receipt", lambda *a, **k: economic)
    monkeypatch.setattr(runner, "validate_pair_evaluation_request", lambda *a, **k: None)
    monkeypatch.setattr(
        runner.engine,
        "_load_v14_inputs",
        lambda *a, **k: (
            object(),
            [object() for _ in range(115)],
            {},
            {"raw_cache": {"root": "synthetic-cache"}},
            None,
        ),
    )
    monkeypatch.setattr(runner, "TypedExpressionRegistry", lambda *a, **k: object())
    monkeypatch.setattr(
        runner,
        "program_catalog_payload",
        lambda catalog: {"catalog_sha256": authority["program_catalog_sha256"]},
    )
    monkeypatch.setattr(
        runner.engine, "_compiler_binding", lambda root: {"identity": "synthetic"}
    )
    monkeypatch.setattr(runner.engine, "_contracts_payload", lambda contracts: [])
    monkeypatch.setattr(runner, "_restore_successor_policies", lambda **k: policies)
    monkeypatch.setattr(runner.engine, "_policy_propose", propose)
    monkeypatch.setattr(
        runner.engine, "_candidate_rebuild_verified", lambda *a, **k: True
    )
    monkeypatch.setattr(runner, "_observe_candidate", observe)
    monkeypatch.setattr(runner, "_checkpoint_metrics", lambda **k: [])
    monkeypatch.setattr(
        runner,
        "adaptive_gate",
        lambda *a, **k: {
            "status": "CONTINUE",
            "arm_states_before": {
                "temporal_program_cem": "ACTIVE",
                "temporal_program_evolution": "ACTIVE",
            },
            "arm_states_after": {
                "temporal_program_cem": "ACTIVE",
                "temporal_program_evolution": "ACTIVE",
            },
            "arm_decisions": {},
        },
    )
    monkeypatch.setattr(runner, "_write_runtime_views", write_views)
    monkeypatch.setattr(runner, "_write_checkpoint", write_checkpoint)
    monkeypatch.setattr(
        runner.engine, "_write_proposal_batch_process_evidence", lambda **k: None
    )
    monkeypatch.setattr(runner, "_program_process_evidence_errors", lambda *a, **k: [])
    monkeypatch.setattr(runner, "_program_process_evidence_summary", lambda *a, **k: {})
    monkeypatch.setattr(
        runner.concurrent.futures, "ProcessPoolExecutor", ImmediateExecutor
    )

    try:
        final = runner.run(
            repo_root,
            runtime_date=runtime_date,
            execution_mode=EXECUTION_MODE,
            successor_artifact_root=repo_root / "synthetic-source",
            successor_policy_bundle=repo_root / "synthetic-bundle.json.gz",
        )
        assert final["status"] == "SUCCESSOR_DEVELOPMENT_BUDGET_COMPLETE", final[
            "terminal_reason"
        ]
        assert final["additional_strict_evaluated"] == 20_000
        assert final["cumulative_valid_strict"] == 50_000
        assert final["completed_full_checkpoint_count"] == 4
        assert proposed == 20_000
        assert [
            path.name
            for path in sorted(runtime_root.glob("successor_decision_additional_*.json"))
        ] == [
            "successor_decision_additional_005000.json",
            "successor_decision_additional_010000.json",
            "successor_decision_additional_015000.json",
            "successor_decision_additional_020000.json",
        ]
        assert [
            path.parent.name
            for path in sorted((runtime_root / "checkpoints").glob("*/manifest.json"))
        ] == [
            "checkpoint_015",
            "checkpoint_016",
            "checkpoint_017",
            "checkpoint_018",
        ]
        state = json.loads((runtime_root / "work_state.json").read_text("utf-8"))
        terminal = state["terminal_decision"]
        assert terminal["status"] == "SEALED"
        assert terminal["terminal_reason"] == "SUCCESSOR_ADDITIONAL_BUDGET_COMPLETE"
        assert terminal["valid_prefix_boundary"] == 50_000
        assert terminal["invalid_suffix_start"] == 50_001
        with pytest.raises(RuntimeError, match="TERMINAL_DECISION_SEALED"):
            runner._call_with_terminal_invariant(
                state, "post_terminal_candidate_generation", lambda: None
            )
    finally:
        shutil.rmtree(runtime_root, ignore_errors=True)
        report_path.unlink(missing_ok=True)
