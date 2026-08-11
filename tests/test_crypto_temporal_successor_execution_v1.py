from __future__ import annotations

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
)


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
