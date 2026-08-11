from __future__ import annotations

import json
import random
import subprocess
import hashlib
from collections import Counter
from pathlib import Path

import pytest

from alphafactory_crypto.broad_search import search_engine_v1 as engine_module
from alphafactory_crypto.broad_search import temporal_program_search_v1 as program_module
from alphafactory_crypto.broad_search.compositional18m import (
    CandidateSpec,
    mechanism_role_domains,
)
from alphafactory_crypto.broad_search.expression import (
    FieldContract,
    TypedExpressionRegistry,
)
from alphafactory_crypto.broad_search.search_engine_v1 import (
    BehaviorArchive,
    MECHANISM_EVOLUTION_OPERATIONS,
    MechanismCEMV2,
    MechanismEvolutionV2,
    MechanismRandomV2,
)
from alphafactory_crypto.broad_search.pair18m import (
    EvaluationContractError,
    PAIRED_DIAGNOSTIC_BLOCK_ROLE,
    evaluate_pair,
    evaluation_failure_is_contract_error,
    validate_pair_evaluation_request,
)
from alphafactory_crypto.broad_search.temporal_program_v1 import (
    PROGRAM_BUILDER_ID,
    compile_temporal_program_catalog,
    program_catalog_payload,
    sample_temporal_program_candidate,
    static_counterpart,
    temporal_program_candidate_from_genes,
)
from alphafactory_crypto.broad_search.temporal_program_search_v1 import (
    _assert_terminal_market_open,
    _call_with_terminal_invariant,
    _checkpoint_qualification_terminal_reason,
    _merge_checkpoint_terminal_reason,
    _checkpoint_allocation,
    _effective_config,
    _sha256_committed_file,
    _load_checkpoint,
    _new_state,
    _next_stage0_lane,
    _program_process_evidence_errors,
    _program_process_evidence_summary,
    _qualification_scope,
    _rejected_worker_runtime_fields,
    _stage0_pair_task_capacity,
    _stage0_checkpoint_lane_targets,
    _stage0_lane_targets,
    _seal_terminal_decision,
    _validate_active_source_smoke_receipt,
    _write_checkpoint,
    stage0_family_decisions,
    validate_config,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads(
    (REPO_ROOT / "config/crypto_temporal_mechanism_program_v1.json").read_text(
        encoding="utf-8"
    )
)


def test_stage0_qualification_scope_is_receipt_scoped_and_exact() -> None:
    assert _qualification_scope({}) == {
        "strict_cap": 50_000,
        "stage0_only": False,
        "skip_stage0": False,
        "adaptive_start_strict": 10_000,
        "active_program_families": [],
        "scope": "FULL_SEQUENTIAL_PROGRAM",
    }
    assert _qualification_scope(
        {
            "replacement_authorization": {
                "qualification_strict_cap": 2_000,
                "stage0_only": True,
            }
        }
    ) == {
        "strict_cap": 2_000,
        "stage0_only": True,
        "skip_stage0": False,
        "adaptive_start_strict": 10_000,
        "active_program_families": [],
        "scope": "FRESH_STATE_CHECKPOINT_ONLY_THROUGHPUT_QUALIFICATION",
    }
    assert _qualification_scope(
        {
            "replacement_authorization": {
                "qualification_strict_cap": 10_000,
                "stage0_only": True,
            }
        }
    ) == {
        "strict_cap": 10_000,
        "stage0_only": True,
        "skip_stage0": False,
        "adaptive_start_strict": 10_000,
        "active_program_families": [],
        "scope": "FRESH_STATE_STAGE0_QUALIFICATION_ONLY",
    }


def test_adaptive_broad_scope_is_fresh_state_and_skips_spent_stage0() -> None:
    replacement = {
        "adaptive_broad_fresh_state": True,
        "prequalified_program_families": [
            "P1_POSITION_STATE_CHANGE_TO_RESPONSE",
            "P4_MULTISCALE_STATE_X_TRANSITION_ROUTING",
        ],
        "fresh_state_seeds": [1118667271, 873488160, 3664147548, 193613803],
        "qualification_strict_cap": 50_000,
        "stage0_only": False,
        "prior_runtime_state_import_allowed": False,
        "old_candidate_import": False,
        "old_distribution_import": False,
        "old_population_import": False,
        "old_archive_import": False,
    }
    receipt = {"replacement_authorization": replacement}
    scope = _qualification_scope(receipt)
    assert scope == {
        "strict_cap": 50_000,
        "stage0_only": False,
        "skip_stage0": True,
        "adaptive_start_strict": 0,
        "active_program_families": [
            "P1_POSITION_STATE_CHANGE_TO_RESPONSE",
            "P4_MULTISCALE_STATE_X_TRANSITION_ROUTING",
        ],
        "scope": "FRESH_STATE_PREQUALIFIED_ADAPTIVE_BROAD_PROGRAM",
    }
    effective = _effective_config(CONFIG, receipt)
    assert effective["seed_authority"]["seeds"] == replacement["fresh_state_seeds"]
    state = _new_state("a" * 40, "B" * 64, effective)
    state["skip_stage0"] = True
    assert _checkpoint_allocation(state, 0) == {
        "temporal_program_random": 400,
        "temporal_program_cem": 800,
        "temporal_program_evolution": 800,
    }


@pytest.mark.parametrize(
    "replacement",
    (
        {"qualification_strict_cap": 10_000},
        {"stage0_only": True},
        {"qualification_strict_cap": 20_000, "stage0_only": True},
        {"qualification_strict_cap": 10_000, "stage0_only": False},
    ),
)
def test_stage0_qualification_scope_fails_closed_on_drift(
    replacement: dict[str, object],
) -> None:
    with pytest.raises(RuntimeError, match="qualification scope"):
        _qualification_scope({"replacement_authorization": replacement})


def test_stage0_qualification_scope_does_not_reclassify_prior_completed_work_as_rescue() -> None:
    receipt = {
        "replacement_authorization": {
            "prior_strict_evaluated": 2_000,
            "prior_runtime_state_import_allowed": False,
            "rescue_rerun": False,
            "qualification_strict_cap": 10_000,
            "stage0_only": True,
        }
    }
    assert _qualification_scope(receipt)["strict_cap"] == 10_000


def test_checkpoint_only_qualification_stops_after_first_checkpoint() -> None:
    scope = {
        "strict_cap": 2_000,
        "stage0_only": True,
        "scope": "FRESH_STATE_CHECKPOINT_ONLY_THROUGHPUT_QUALIFICATION",
    }
    assert _checkpoint_qualification_terminal_reason(
        checkpoint_index=0,
        qualification_scope=scope,
        observed_strict_per_hour=3_000.0,
        minimum_strict_per_hour=2_777.7778,
    ) == "CHECKPOINT_ONLY_QUALIFICATION_CAP_REACHED"
    assert _checkpoint_qualification_terminal_reason(
        checkpoint_index=0,
        qualification_scope=scope,
        observed_strict_per_hour=2_000.0,
        minimum_strict_per_hour=2_777.7778,
    ) == "ENGINE_BUDGET_EXHAUSTED_THROUGHPUT_FLOOR"


def test_checkpoint_qualification_cannot_overwrite_frozen_gate_stop() -> None:
    assert _merge_checkpoint_terminal_reason(
        "STOP_ALL_ADAPTIVE_ARMS_EXITED",
        None,
    ) == "STOP_ALL_ADAPTIVE_ARMS_EXITED"
    assert _merge_checkpoint_terminal_reason(
        None,
        "ENGINE_BUDGET_EXHAUSTED_THROUGHPUT_FLOOR",
    ) == "ENGINE_BUDGET_EXHAUSTED_THROUGHPUT_FLOOR"


def test_terminal_decision_is_a_mechanical_market_mutation_invariant() -> None:
    state = _new_state("a" * 40, "B" * 64, CONFIG)
    ledger: list[dict[str, object]] = []
    rejected: list[dict[str, object]] = []
    calls = Counter()

    sealed = _seal_terminal_decision(
        state,
        reason="STOP_ALL_ADAPTIVE_ARMS_EXITED",
        strict_boundary=30_000,
    )
    assert sealed == {
        "schema_version": 1,
        "status": "SEALED",
        "terminal_reason": "STOP_ALL_ADAPTIVE_ARMS_EXITED",
        "valid_prefix_boundary": 30_000,
        "invalid_suffix_start": 30_001,
    }

    def mutate(name: str) -> None:
        calls[name] += 1
        ledger.append({"name": name})
        rejected.append({"name": name})
        state["generation_attempts"] += 1

    for action in (
        "candidate_generation",
        "executor_submit",
        "ledger_append",
        "archive_mutation",
        "policy_observe",
    ):
        with pytest.raises(RuntimeError, match="TERMINAL_DECISION_SEALED"):
            _call_with_terminal_invariant(state, action, mutate, action)

    with pytest.raises(RuntimeError, match="TERMINAL_DECISION_SEALED"):
        _assert_terminal_market_open(state, action="resume_next_loop")

    assert calls == Counter()
    assert ledger == []
    assert rejected == []
    assert state["generation_attempts"] == 0


def test_sealed_checkpoint_resume_stops_before_market_workers_or_artifact_mutation(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "config/crypto_temporal_mechanism_program_v1.json"
    config_path.parent.mkdir(parents=True)
    config_path.write_text("{}\n", encoding="utf-8")
    runtime_root = (
        tmp_path / "runtime/crypto_temporal_mechanism_program_v1_resume-test"
    )
    checkpoint = runtime_root / "checkpoints/checkpoint_014"
    checkpoint.mkdir(parents=True)
    state = _new_state("a" * 40, "B" * 64, CONFIG)
    _seal_terminal_decision(
        state,
        reason="STOP_ALL_ADAPTIVE_ARMS_EXITED",
        strict_boundary=30_000,
    )
    (checkpoint / "state.json").write_text(
        json.dumps(state, sort_keys=True) + "\n", encoding="utf-8"
    )
    observed_artifacts = {
        runtime_root / "candidate_ledger.parquet": b"ledger-before",
        runtime_root / "behavior_archive.parquet": b"archive-before",
        runtime_root / "process_evidence/producer_batch_000001.json": (
            b"submission-before"
        ),
    }
    for path, payload in observed_artifacts.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    before = {
        path: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in observed_artifacts
    }
    calls = Counter()

    monkeypatch.setattr(program_module, "validate_config", lambda config: None)
    monkeypatch.setattr(
        program_module,
        "validate_receipt",
        lambda *args, **kwargs: {},
    )
    monkeypatch.setattr(engine_module, "_git_sha", lambda root: "a" * 40)
    monkeypatch.setattr(
        engine_module,
        "_source_tree_clean_for_run",
        lambda *args, **kwargs: True,
    )

    def market_read(*args, **kwargs):
        calls["market_read"] += 1
        raise AssertionError("sealed resume reached market loading")

    def executor(*args, **kwargs):
        calls["executor"] += 1
        raise AssertionError("sealed resume initialized an executor")

    monkeypatch.setattr(program_module, "resolve_search_economic_receipt", market_read)
    monkeypatch.setattr(
        program_module.concurrent.futures,
        "ProcessPoolExecutor",
        executor,
    )

    with pytest.raises(RuntimeError, match="TERMINAL_DECISION_SEALED"):
        program_module.run(tmp_path, runtime_date="resume-test", source_sha="a" * 40)

    assert calls == Counter()
    assert before == {
        path: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in observed_artifacts
    }


def test_source_smoke_validates_active_run_receipt(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    observed: dict[str, object] = {}

    monkeypatch.setattr(
        engine_module,
        "_read_json",
        lambda path: {"run_authorized": True},
    )

    def validate(repo_root, *, config, require_authorized):
        observed.update(
            {
                "repo_root": repo_root,
                "config": config,
                "require_authorized": require_authorized,
            }
        )
        return {"run_authorized": True}

    monkeypatch.setattr(program_module, "validate_receipt", validate)
    config = {"authorization": "test"}
    assert _validate_active_source_smoke_receipt(tmp_path, config) == {
        "run_authorized": True
    }
    assert observed == {
        "repo_root": tmp_path,
        "config": config,
        "require_authorized": True,
    }


def test_committed_component_hash_is_checkout_line_ending_independent(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.invalid"],
        cwd=repo,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Temporal Test"], cwd=repo, check=True
    )
    source = repo / "component.py"
    committed = b"first = 1\nsecond = 2\n"
    source.write_bytes(committed)
    subprocess.run(["git", "add", "component.py"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "fixture"], cwd=repo, check=True, capture_output=True)
    source.write_bytes(committed.replace(b"\n", b"\r\n"))

    assert hashlib.sha256(source.read_bytes()).hexdigest().upper() != hashlib.sha256(
        committed
    ).hexdigest().upper()
    assert _sha256_committed_file(repo, "component.py") == hashlib.sha256(
        committed
    ).hexdigest().upper()


def _contracts() -> tuple[FieldContract, ...]:
    rows = json.loads(
        (
            REPO_ROOT
            / "runtime/crypto_search_engine_v1_4_oi_flow_20260728/aligned_carrier_manifest.json"
        ).read_text(encoding="utf-8")
    )["contracts"]
    return tuple(
        FieldContract(
            str(row["field_id"]),
            str(row["value_type"]),
            str(row["unit"]),
            int(row["observable_lag_hours"]),
            str(row["pit_authority"]),
        )
        for row in rows
    )


def _registry() -> TypedExpressionRegistry:
    limits = CONFIG["expression_limits"]
    return TypedExpressionRegistry(
        _contracts(),
        max_depth=int(limits["maximum_depth"]),
        max_raw_inputs=int(limits["maximum_raw_fields"]),
        max_rolling_windows=int(limits["maximum_rolling_windows"]),
        max_canonical_primitive_nodes=int(
            limits["maximum_canonical_primitive_nodes"]
        ),
        max_cross_asset_normalizations=int(
            limits["maximum_cross_asset_normalizations"]
        ),
        max_regime_gates=int(limits["maximum_regime_gates"]),
    )


def _catalog():
    return compile_temporal_program_catalog(CONFIG)


def _policy_parameters(catalog):
    return {
        "candidate_builder": PROGRAM_BUILDER_ID,
        "temporal_program_specs": [program.to_dict() for _, program in catalog],
        "time_scale_authority": CONFIG["time_scale_authority"],
        "allowed_horizons": [4],
        "balanced_template_sampling": True,
        "duplicate_resample_limit": 128,
    }


def test_catalog_is_content_addressed_balanced_and_not_the_old_canary_box() -> None:
    catalog = _catalog()
    counts = Counter(program.family_id for _, program in catalog)
    assert len(catalog) == 464
    assert counts == {
        "P1_POSITION_STATE_CHANGE_TO_RESPONSE": 180,
        "P2_RECENT_CROWDING_EVENT_TO_RESPONSE": 96,
        "P3_FLOW_SHOCK_PERSISTENCE_TO_ABSORPTION": 8,
        "P4_MULTISCALE_STATE_X_TRANSITION_ROUTING": 180,
    }
    assert len({program.program_id for _, program in catalog}) == len(catalog)
    assert len({mechanism.mechanism_id for mechanism, _ in catalog}) == len(catalog)
    payload = program_catalog_payload(catalog)
    assert payload["builder_id"] == PROGRAM_BUILDER_ID
    assert len(payload["catalog_sha256"]) == 64
    assert max(CONFIG["time_scale_authority"]["POSITIONING_SLOW"]["long_hours"]) == 720


@pytest.mark.parametrize(
    "family_id",
    [
        "P1_POSITION_STATE_CHANGE_TO_RESPONSE",
        "P2_RECENT_CROWDING_EVENT_TO_RESPONSE",
        "P3_FLOW_SHOCK_PERSISTENCE_TO_ABSORPTION",
        "P4_MULTISCALE_STATE_X_TRANSITION_ROUTING",
    ],
)
def test_each_family_compiles_replays_and_has_a_distinct_static_pair(
    family_id: str,
) -> None:
    registry = _registry()
    domains = {**mechanism_role_domains(_contracts()), "__HORIZONS__": (4,)}
    mechanism, program = next(
        pair for pair in _catalog() if pair[1].family_id == family_id
    )
    candidate = sample_temporal_program_candidate(
        registry=registry,
        mechanism=mechanism,
        program=program,
        domains=domains,
        scale_contract=CONFIG["time_scale_authority"],
        rng=random.Random(20260807),
    )
    replay = temporal_program_candidate_from_genes(
        registry, genes=candidate.generation_genes, domains=domains
    )
    static = static_counterpart(registry, candidate, domains=domains)
    assert replay.to_dict() == candidate.to_dict()
    assert static.candidate_id != candidate.candidate_id
    assert static.raw_fields == candidate.raw_fields
    assert static.mapping_id == candidate.mapping_id
    assert static.horizon_hours == candidate.horizon_hours == 4
    assert len(candidate.expression.canonical_dict()) > 0


def test_program_nesting_requires_explicit_run_local_registry_limits() -> None:
    registry = _registry()
    mechanism, program = next(
        pair for pair in _catalog() if pair[1].family_id.startswith("P3_")
    )
    candidate = sample_temporal_program_candidate(
        registry=registry,
        mechanism=mechanism,
        program=program,
        domains=mechanism_role_domains(_contracts()),
        scale_contract=CONFIG["time_scale_authority"],
        rng=random.Random(13),
    )
    with pytest.raises(ValueError, match="canonical primitive"):
        TypedExpressionRegistry(_contracts()).validate(candidate.expression)
    registry.validate(candidate.expression)


def test_random_cem_and_evolution_replay_the_program_genome() -> None:
    registry = _registry()
    catalog = _catalog()
    mechanisms = tuple(mechanism for mechanism, _ in catalog)
    parameters = _policy_parameters(catalog)

    random_policy = MechanismRandomV2(17, registry, mechanisms, parameters)
    first, metadata = random_policy.propose()
    assert metadata["operation"] == "EXTENSIBLE_MECHANISM_TYPED_RANDOM"
    restored = MechanismRandomV2.from_state(registry, random_policy.export_state())
    assert restored.state_hash() == random_policy.state_hash()
    assert temporal_program_candidate_from_genes(
        registry, genes=first.generation_genes
    ).candidate_id == first.candidate_id

    cem = MechanismCEMV2(
        19,
        registry,
        mechanisms,
        {
            **parameters,
            "minimum_observation_count": 1,
            "elite_fraction": 0.5,
            "smoothing": 0.35,
            "minimum_probability": 0.002,
            "entropy_floor_ratio": 0.6,
            "count_pseudocount": 0.5,
        },
    )
    cem_candidate, _ = cem.propose()
    cem.update(
        [
            {
                "candidate_id": cem_candidate.candidate_id,
                "candidate_spec_json": json.dumps(cem_candidate.to_dict()),
                "search_reward": 1.0,
            }
        ]
    )
    assert cem.update_count == 1
    assert MechanismCEMV2.from_state(registry, cem.export_state()).state_hash() == cem.state_hash()

    evolution = MechanismEvolutionV2(
        23,
        registry,
        mechanisms,
        {
            **parameters,
            "warmup": 2,
            "population_limit": 16,
            "tournament_size": 2,
            "parameter_mutation_probability": 1.0,
            "mechanism_mutation_probability": 0.0,
            "crossover_probability": 0.0,
            "selection_authority": "CRYPTO_TRAIN_JOINT_PRIMARY_MATCHED_SORTINO_V2",
        },
    )
    for index in range(2):
        parent, _ = evolution.propose()
        evolution.observe(
            parent,
            {
                "behavior_family_id": f"family-{index}",
                "search_reward": float(index),
                "search_reward_authority": "CRYPTO_TRAIN_JOINT_PRIMARY_MATCHED_SORTINO_V2",
                "policy_local_family_count_at_completion": 1,
                "operation": "MECHANISM_EVOLUTION_TYPED_RANDOM_WARMUP",
            },
        )
    child, child_metadata = evolution.propose()
    assert child_metadata["operation"] in MECHANISM_EVOLUTION_OPERATIONS
    assert child_metadata["receipt_verified"] is True
    assert child.candidate_id not in {
        CandidateSpec.from_dict(row["candidate"]).candidate_id
        for row in evolution.population.values()
    }
    assert MechanismEvolutionV2.from_state(
        registry, evolution.export_state()
    ).state_hash() == evolution.state_hash()


def test_contract_is_sequential_development_only_and_not_an_all_family_veto() -> None:
    validate_config(CONFIG)
    budget = CONFIG["search_budget"]
    assert budget["strict_evaluated_maximum"] == 50_000
    assert budget["checkpoint_size"] == 2_000
    assert budget["release_boundaries_strict"] == [
        10_000,
        20_000,
        30_000,
        40_000,
        50_000,
    ]
    gate = CONFIG["continuation_gates"]["stage_10000"]
    assert gate["family_continues_when_any_primary_route_passes"] is True
    assert gate["minimum_continuing_family_count"] == 1
    assert all(value is False for value in CONFIG["boundaries"].values()) is False
    for key in ("validation", "oos", "holdout", "promotion", "rescue_rerun"):
        assert CONFIG["boundaries"][key] is False
    assert CONFIG["runtime_safety"] == {
        "system_error_fatal": True,
        "stage0_attempt_round_robin": True,
        "process_evidence_required": True,
        "zero_strict_returned_pair_maximum": 64,
    }


def test_pc2_runner_treats_native_exit_code_as_authority_not_stderr() -> None:
    runner = (
        REPO_ROOT / "scripts/run_crypto_temporal_mechanism_program_v1_pc2.ps1"
    ).read_text(encoding="utf-8")
    assert "function Invoke-PythonChecked" in runner
    assert '$ErrorActionPreference = "Continue"' in runner
    assert "2>&1 | ForEach-Object { Write-Output $_ }" in runner
    assert 'if ($nativeExitCode -ne 0)' in runner
    assert runner.count("Invoke-PythonChecked -Arguments") == 3
    assert "& $PythonExe -m alphafactory_crypto" not in runner


def test_stage0_checkpoint_allocation_is_exact_without_rounding_underfill() -> None:
    cumulative: Counter[str] = Counter()
    for checkpoint_index in range(5):
        local = _stage0_checkpoint_lane_targets(CONFIG, checkpoint_index)
        assert sum(local.values()) == 1_000
        assert {
            key.split("|", 2)[1]
            for key in local
        } == {
            row["family_id"] for row in CONFIG["program_families"]
        }
        cumulative.update(local)
    assert dict(cumulative) == _stage0_lane_targets(CONFIG)


def test_stage0_attempts_rotate_even_when_no_lane_completes() -> None:
    ordered = ["lane-a", "lane-b", "lane-c", "lane-d"]
    targets = {key: 10 for key in ordered}
    completed: Counter[str] = Counter()
    pending: Counter[str] = Counter()
    cursor = 0
    observed = []
    for _ in range(12):
        key, cursor = _next_stage0_lane(
            ordered_lanes=ordered,
            lane_targets=targets,
            lane_completed=completed,
            lane_pending=pending,
            cursor=cursor,
        )
        observed.append(key)
    assert observed == ordered * 3


def test_stage0_pair_tasks_use_every_configured_worker_process() -> None:
    assert _stage0_pair_task_capacity(10) == 10
    assert _stage0_pair_task_capacity(8) == 8
    with pytest.raises(ValueError, match="worker count must be positive"):
        _stage0_pair_task_capacity(0)


def test_stage0_full_pool_batching_preserves_deterministic_lane_sequence() -> None:
    targets = _stage0_checkpoint_lane_targets(CONFIG, 0)
    ordered = sorted(targets)

    def schedule(capacity: int) -> tuple[list[str], int]:
        completed: Counter[str] = Counter()
        cursor = 0
        output: list[str] = []
        batches = 0
        while sum(completed.values()) < sum(targets.values()):
            pending: Counter[str] = Counter()
            local: list[str] = []
            while len(local) < capacity:
                key, cursor = _next_stage0_lane(
                    ordered_lanes=ordered,
                    lane_targets=targets,
                    lane_completed=completed,
                    lane_pending=pending,
                    cursor=cursor,
                )
                if key is None:
                    break
                pending[key] += 1
                local.append(key)
            completed.update(pending)
            output.extend(local)
            batches += 1
        return output, batches

    old_sequence, old_batch_count = schedule(5)
    repaired_sequence, repaired_batch_count = schedule(10)
    assert repaired_sequence == old_sequence
    assert old_batch_count == 200
    assert repaired_batch_count == 100


def test_paired_authority_rejects_before_any_store_access() -> None:
    class StoreMustNotBeTouched:
        def __getattribute__(self, name):
            raise AssertionError(f"store touched before authority admission: {name}")

    receipt = {
        "train": {"start": "2025-01-01", "end_exclusive": "2025-02-01"},
        "validation": {"start": "2025-02-01", "end_exclusive": "2025-03-01"},
        "holdout": {"start": "2025-03-01", "end_exclusive": "2025-04-01"},
    }
    with pytest.raises(
        EvaluationContractError,
        match="PAIRED_DIAGNOSTIC_PATHS_REQUIRE_BOUND_DEVELOPMENT_TRAIN_ROLE",
    ):
        evaluate_pair(
            store=StoreMustNotBeTouched(),
            registry=None,
            candidate=None,
            block_start="2025-01-01",
            block_end="2025-02-01",
            block_role="WRONG_ROLE",
            economic_receipt=receipt,
            include_paired_diagnostic_paths=True,
        )
    assert evaluation_failure_is_contract_error(
        ValueError("ECONOMIC_RECEIPT_TARGET_CONTRACT_CHANGED:venue")
    )
    assert (
        validate_pair_evaluation_request(
            block_start="2025-01-01",
            block_end="2025-02-01",
            block_role=PAIRED_DIAGNOSTIC_BLOCK_ROLE,
            economic_receipt=receipt,
            include_paired_diagnostic_paths=True,
        )
        == "train"
    )


def test_worker_preserves_run_global_contract_failure_as_system_error(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    registry = _registry()
    mechanism, program = _catalog()[0]
    candidate = sample_temporal_program_candidate(
        registry=registry,
        mechanism=mechanism,
        program=program,
        domains=mechanism_role_domains(_contracts()),
        scale_contract=CONFIG["time_scale_authority"],
        rng=random.Random(31),
    )

    def fail_contract(**kwargs):
        raise EvaluationContractError("ECONOMIC_RECEIPT_TARGET_CONTRACT_CHANGED:venue")

    monkeypatch.setattr(program_module, "evaluate_pair", fail_contract)
    monkeypatch.setattr(engine_module, "_WORKER_STORE", object())
    monkeypatch.setattr(engine_module, "_WORKER_REGISTRY", registry)
    monkeypatch.setattr(engine_module, "_WORKER_PROCESS_EVIDENCE_ROOT", tmp_path)
    result = program_module._worker_program_pair(
        {
            "paired_program_id": "pair-system-error",
            "static": candidate.to_dict(),
            "temporal": candidate.to_dict(),
        }
    )
    assert result["status"] == "SYSTEM_ERROR"
    assert result["system_error"] is True
    task_rows = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in tmp_path.glob("*_task.json")
    ]
    assert task_rows and task_rows[0]["stage"] == "TASK_COMPLETED"
    assert task_rows[0]["outcome"] == "SYSTEM_ERROR"


def test_rejected_worker_runtime_fields_preserve_existing_worker_cost() -> None:
    assert _rejected_worker_runtime_fields(
        {
            "process_cpu_seconds": 1.25,
            "wall_seconds": 2.5,
            "worker_rss_bytes": 123,
            "worker_private_bytes": 456,
        }
    ) == {
        "pair_process_cpu_seconds": 1.25,
        "pair_wall_seconds": 2.5,
        "worker_rss_bytes": 123,
        "worker_private_bytes": 456,
    }


def test_empty_invalid_terminal_checkpoint_is_atomic_and_restorable(tmp_path: Path) -> None:
    state = _new_state("a" * 40, "B" * 64, CONFIG)
    state["generation_attempts"] = 5
    identities = {
        "raw_cache": {"root": "unused", "identity_sha256": "C" * 64},
        "compiler_identity": {"identity_sha256": "D" * 64},
    }
    target = _write_checkpoint(
        tmp_path,
        checkpoint_index=0,
        label="checkpoint_run_invalid",
        state=state,
        policies={},
        ledger=[],
        archive=BehaviorArchive(),
        pair_rows=[],
        metrics=[],
        rejected=[{"status": "SYSTEM_ERROR"}],
        identities=identities,
    )
    manifest = json.loads((target / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["restore_verified"] is True
    assert manifest["completed_ledger_row_count"] == 0
    restored = _load_checkpoint(
        target,
        registry=None,
        expected_source="a" * 40,
        expected_frozen="B" * 64,
        expected_identities=identities,
        verify_policy_restore=False,
    )
    assert restored[0]["generation_attempts"] == 5


def test_paired_batch_process_evidence_closes_and_carries_raw_attempts(
    tmp_path: Path,
) -> None:
    registry = _registry()
    mechanism, program = _catalog()[0]
    candidate = sample_temporal_program_candidate(
        registry=registry,
        mechanism=mechanism,
        program=program,
        domains=mechanism_role_domains(_contracts()),
        scale_contract=CONFIG["time_scale_authority"],
        rng=random.Random(37),
    )
    evidence_root = tmp_path / "process_evidence"
    engine_module._write_worker_process_evidence(
        evidence_root=evidence_root,
        channel="initializer",
        stage="INITIALIZER_READY",
    )
    engine_module._write_worker_process_evidence(
        evidence_root=evidence_root,
        channel="task",
        stage="TASK_COMPLETED",
        candidate_id="paired-id",
        outcome="PAIR_EVALUATED",
    )
    payload = engine_module._write_proposal_batch_process_evidence(
        evidence_root=evidence_root,
        stage="WORKER_RESULTS_RETURNED",
        source_sha="a" * 40,
        frozen_contract_sha256="B" * 64,
        checkpoint_index=0,
        batch_index=0,
        generation_attempts=7,
        attempted_exact_id_count=2,
        proposals=[
            {
                "paired_program_id": "paired-id",
                "static": candidate,
                "temporal": candidate,
                "arm": "temporal_program_random",
                "seed": 1,
                "policy_key": "lane",
                "metadata": {"operation": "TEST", "raw_attempts": 7},
                "generation_attempt_ordinal": 7,
            }
        ],
        submitted_count=1,
        returned_count=1,
    )
    assert payload["proposals"][0]["raw_attempts"] == 7
    assert _program_process_evidence_errors(
        tmp_path, expected_batch_count=1, configured_worker_processes=10
    ) == []
    assert _program_process_evidence_summary(tmp_path) == {
        "observed_worker_process_count": 1,
        "observed_batch_count": 1,
        "total_submitted_worker_task_count": 1,
        "maximum_submitted_worker_tasks_per_batch": 1,
    }


def test_process_evidence_rejects_systematic_half_pool_submission(
    tmp_path: Path,
) -> None:
    registry = _registry()
    mechanism, program = _catalog()[0]
    candidate = sample_temporal_program_candidate(
        registry=registry,
        mechanism=mechanism,
        program=program,
        domains=mechanism_role_domains(_contracts()),
        scale_contract=CONFIG["time_scale_authority"],
        rng=random.Random(41),
    )
    evidence_root = tmp_path / "process_evidence"
    engine_module._write_worker_process_evidence(
        evidence_root=evidence_root,
        channel="initializer",
        stage="INITIALIZER_READY",
    )
    engine_module._write_worker_process_evidence(
        evidence_root=evidence_root,
        channel="task",
        stage="TASK_COMPLETED",
        candidate_id="paired-id",
        outcome="PAIR_EVALUATED",
    )
    proposals = [
        {
            "paired_program_id": f"pair-{index}",
            "arm": "temporal_program_random",
            "seed": 1,
            "policy_key": "lane",
            "static": candidate,
            "temporal": candidate,
            "metadata": {"operation": "TEST", "raw_attempts": 1},
            "generation_attempt_ordinal": index + 1,
        }
        for index in range(5)
    ]
    for batch_index in range(2):
        engine_module._write_proposal_batch_process_evidence(
            evidence_root=evidence_root,
            stage="WORKER_RESULTS_RETURNED",
            source_sha="a" * 40,
            frozen_contract_sha256="B" * 64,
            checkpoint_index=0,
            batch_index=batch_index,
            generation_attempts=(batch_index + 1) * 5,
            attempted_exact_id_count=(batch_index + 1) * 10,
            proposals=proposals,
            submitted_count=5,
            returned_count=5,
        )
    errors = _program_process_evidence_errors(
        tmp_path, expected_batch_count=2, configured_worker_processes=10
    )
    assert "producer_batch_worker_capacity_underfilled" in errors


def test_stage0_continuation_is_family_local_or_plus_breadth_not_all_family_veto() -> None:
    rows = []
    for family_index, family in enumerate(CONFIG["program_families"]):
        family_id = family["family_id"]
        for index in range(1_250):
            positive = family_index == 0 and index % 2 == 0
            delta = 0.2 if positive else (-0.1 if family_index else -0.01)
            rows.append(
                {
                    "program_family_id": family_id,
                    "program_id": f"{family_id}|{index % 4}",
                    "paired_worst_axis_net_delta": delta,
                    "static_dual_axis_net_positive": False,
                    "temporal_dual_axis_net_positive": positive,
                    "static_replicated_2_of_3": False,
                    "temporal_replicated_2_of_3": positive,
                    "static_matched_positive": False,
                    "temporal_matched_positive": positive,
                }
            )
    decision = stage0_family_decisions(rows, CONFIG)
    assert decision["status"] == "CONTINUE"
    assert decision["continuing_families"] == [
        "P1_POSITION_STATE_CHANGE_TO_RESPONSE"
    ]


def test_adaptive_gate_excludes_inactive_family_random_diagnostics() -> None:
    rows = []
    ordinal = 0

    def add(arm: str, family: str, reward: float, positive: bool) -> None:
        nonlocal ordinal
        ordinal += 1
        rows.append(
            {
                "arm": arm,
                "completion_ordinal": ordinal,
                "arm_completion_ordinal": ordinal,
                "behavior_family_id": f"behavior-{ordinal}",
                "left_incremental_net_mean": 0.1 if positive else -0.1,
                "right_incremental_net_mean": 0.1 if positive else -0.1,
                "replicated_candidate": positive,
                "program_family_id": family,
                "search_reward": reward,
                "total_process_cpu_seconds": 1.0,
            }
        )

    for family in (
        "P1_POSITION_STATE_CHANGE_TO_RESPONSE",
        "P4_MULTISCALE_STATE_X_TRANSITION_ROUTING",
    ):
        add("temporal_program_random", family, 0.0, False)
        add("temporal_program_random", family, 0.0, False)
    add("temporal_program_random", "P2_RECENT_CROWDING_EVENT_TO_RESPONSE", 100.0, True)
    add("temporal_program_random", "P3_FLOW_SHOCK_PERSISTENCE_TO_ABSORPTION", 100.0, True)
    for family in (
        "P1_POSITION_STATE_CHANGE_TO_RESPONSE",
        "P4_MULTISCALE_STATE_X_TRANSITION_ROUTING",
    ):
        add("temporal_program_cem", family, 1.0, True)
        add("temporal_program_cem", family, 1.0, True)

    decision = program_module.adaptive_gate(
        rows,
        state={
            "adaptive_start_strict": 0,
            "active_program_families": [
                "P1_POSITION_STATE_CHANGE_TO_RESPONSE",
                "P4_MULTISCALE_STATE_X_TRANSITION_ROUTING",
            ],
            "arm_states": {
                "temporal_program_cem": "ACTIVE",
                "temporal_program_evolution": "ACTIVE",
            },
        },
        strict_boundary=len(rows),
        config=CONFIG,
    )
    cem = decision["arm_decisions"]["temporal_program_cem"]
    assert cem["decision"] == "ACTIVE"
    assert cem["same_count"] == 4
    assert cem["random"]["mean_search_reward"] == 0.0


def test_program_family_concentration_is_diagnostic_not_an_exit_gate() -> None:
    rows = []
    ordinal = 0

    def add(
        arm: str,
        *,
        positive: bool,
        family: str,
        reward: float,
        replicated: bool,
    ) -> None:
        nonlocal ordinal
        ordinal += 1
        rows.append(
            {
                "arm": arm,
                "completion_ordinal": ordinal,
                "arm_completion_ordinal": ordinal,
                "behavior_family_id": f"behavior-{arm}-{ordinal}",
                "left_incremental_net_mean": 0.1 if positive else -0.1,
                "right_incremental_net_mean": 0.1 if positive else -0.1,
                "replicated_candidate": replicated,
                "program_family_id": family,
                "search_reward": reward,
                "total_process_cpu_seconds": 1.0,
            }
        )

    for index in range(1_000):
        add(
            "temporal_program_random",
            positive=index < 100,
            family="P1_POSITION_STATE_CHANGE_TO_RESPONSE",
            reward=0.0,
            replicated=index < 50,
        )
        add(
            "temporal_program_evolution",
            positive=True,
            family=(
                "P4_MULTISCALE_STATE_X_TRANSITION_ROUTING"
                if index < 861
                else "P1_POSITION_STATE_CHANGE_TO_RESPONSE"
            ),
            reward=1.0,
            replicated=index < 700,
        )

    decision = program_module.adaptive_gate(
        rows,
        state={
            "adaptive_start_strict": 0,
            "active_program_families": [
                "P1_POSITION_STATE_CHANGE_TO_RESPONSE",
                "P4_MULTISCALE_STATE_X_TRANSITION_ROUTING",
            ],
            "arm_states": {
                "temporal_program_cem": "EXITED",
                "temporal_program_evolution": "ACTIVE",
            },
        },
        strict_boundary=len(rows),
        config=CONFIG,
    )
    evolution = decision["arm_decisions"]["temporal_program_evolution"]
    observed = evolution["observed"]
    assert evolution["decision"] == "ACTIVE"
    assert evolution["quality_improvement"] is True
    assert evolution["productivity_improvement"] is True
    assert evolution["behavior_breadth_pass"] is True
    assert observed["dominant_program_family"] == (
        "P4_MULTISCALE_STATE_X_TRANSITION_ROUTING"
    )
    assert observed["dominant_program_family_positive_share"] == pytest.approx(
        0.861
    )
    assert observed["family_concentration_diagnostic"] == (
        "ABOVE_DIAGNOSTIC_THRESHOLD"
    )
    assert decision["status"] == "CONTINUE"
