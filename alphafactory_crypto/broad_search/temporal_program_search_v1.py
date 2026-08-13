"""Sequential development search over explicit temporal mechanism programs.

The module is an experiment orchestrator.  Programs compile to the existing
Expression/CandidateSpec DAG and are evaluated by the existing pair evaluator.
It deliberately does not introduce another AST, compiler, mapping, reward, or
evaluator.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import math
import os
import shutil
import subprocess
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence, TypeVar

import numpy as np
import pandas as pd
import psutil

from . import search_engine_v1 as engine
from .compositional18m import CandidateSpec, MechanismSpec, mechanism_role_domains
from .experiment_authority import (
    require_real_experiment_authority,
    resolve_search_economic_receipt,
)
from .expression import FieldContract, TypedExpressionRegistry
from .pair18m import (
    ControlBehaviorDegeneracyError,
    EvaluationContractError,
    PAIRED_DIAGNOSTIC_BLOCK_ROLE,
    evaluate_pair,
    evaluation_failure_is_contract_error,
    validate_pair_evaluation_request,
)
from .temporal_activation_v1 import _paired_common_support, _process_evidence_closed
from .temporal_development_expansion_v1 import (
    ALL_PROGRAM_FAMILIES as EXPANSION_PROGRAM_FAMILIES,
    AUTHORIZATION_PATH as EXPANSION_AUTHORIZATION_PATH,
    AUTHORIZATION_SCOPE as EXPANSION_AUTHORIZATION_SCOPE,
    CAMPAIGN as EXPANSION_CAMPAIGN,
    DECISION_BOUNDARIES as EXPANSION_DECISION_BOUNDARIES,
    EXECUTION_MODE as EXPANSION_EXECUTION_MODE,
    ExpansionPreflightError,
    LANE_SEEDS as EXPANSION_LANE_SEEDS,
    SEED_CAMPAIGN as EXPANSION_SEED_CAMPAIGN,
    SEED_DERIVATION as EXPANSION_SEED_DERIVATION,
    discovery_diagnostics,
    fixed_flow_decision,
    load_diagnostic_baseline,
    validate_authorization as validate_expansion_authorization,
)
from .temporal_targeted_deepening_v1 import (
    ACTIVE_PROGRAM_FAMILIES as TARGETED_PROGRAM_FAMILIES,
    AUTHORIZATION_PATH as TARGETED_AUTHORIZATION_PATH,
    AUTHORIZED_STATUS as TARGETED_AUTHORIZED_STATUS,
    CAMPAIGN as TARGETED_CAMPAIGN,
    CONSUMED_STATUS as TARGETED_CONSUMED_STATUS,
    DECISION_BOUNDARIES as TARGETED_DECISION_BOUNDARIES,
    EVOLUTION_OPERATION_PROBABILITIES as TARGETED_EVOLUTION_PROBABILITIES,
    EXECUTION_MODE as TARGETED_EXECUTION_MODE,
    FIXED_ALLOCATION_PER_10000,
    LANE_SEEDS as TARGETED_LANE_SEEDS,
    SEED_CAMPAIGN as TARGETED_SEED_CAMPAIGN,
    SEED_DERIVATION as TARGETED_SEED_DERIVATION,
    build_frozen_target_parent_pool,
    final_next_decision as targeted_final_next_decision,
    load_diagnostic_baseline as load_targeted_diagnostic_baseline,
    targeted_checkpoint_decision,
    targeted_diagnostics,
    validate_authorization as validate_targeted_authorization,
)
from .temporal_program_v1 import (
    PROGRAM_BUILDER_ID,
    TemporalProgramSpec,
    compile_temporal_program_catalog,
    program_catalog_payload,
    static_counterpart,
)
from .temporal_successor_v1 import (
    AUTHORIZED_STATUS as SUCCESSOR_AUTHORIZED_STATUS,
    CONSUMED_STATUS as SUCCESSOR_CONSUMED_STATUS,
    EXECUTION_MODE as SUCCESSOR_EXECUTION_MODE,
    FRESH_RANDOM_IDENTITY,
    PREFIX_BOUNDARY as SUCCESSOR_PREFIX_BOUNDARY,
    SUCCESSOR_AUTHORIZATION_PATH,
    SUCCESSOR_CAMPAIGN,
    SuccessorPreflightError,
    authorization_content_sha,
    derive_fresh_random_lane_seeds,
    executor_workspace_identity,
    prepare_successor_execution,
    successor_allocation,
    successor_budget_state,
    successor_checkpoint_decision,
    successor_lane_targets,
)


CONFIG_PATH = "config/crypto_temporal_mechanism_program_v1.json"
RECEIPT_PATH = "config/crypto_temporal_mechanism_program_v1_receipt.json"
CAMPAIGN = "crypto_temporal_mechanism_program_v1"
BLOCK_ROLE = PAIRED_DIAGNOSTIC_BLOCK_ROLE
REPORT_PREFIX = "CRYPTO_TEMPORAL_MECHANISM_PROGRAM_SEARCH_V1"
ARMS = (
    "temporal_program_random",
    "temporal_program_cem",
    "temporal_program_evolution",
)
ADAPTIVE_BROAD_FAMILIES = (
    "P1_POSITION_STATE_CHANGE_TO_RESPONSE",
    "P4_MULTISCALE_STATE_X_TRANSITION_ROUTING",
)
ADAPTIVE_BROAD_SEEDS = (1118667271, 873488160, 3664147548, 193613803)
COMPONENT_PATHS = (
    "alphafactory_crypto/broad_search/expression.py",
    "alphafactory_crypto/broad_search/compositional18m.py",
    "alphafactory_crypto/broad_search/pair18m.py",
    "alphafactory_crypto/broad_search/search_engine_v1.py",
    "alphafactory_crypto/broad_search/temporal_activation_v1.py",
    "alphafactory_crypto/broad_search/temporal_program_v1.py",
    "alphafactory_crypto/broad_search/temporal_program_search_v1.py",
    "scripts/run_crypto_temporal_mechanism_program_v1_pc2.ps1",
    CONFIG_PATH,
)


class ProgramBudgetExhausted(RuntimeError):
    pass


class ProgramRunInvalid(RuntimeError):
    pass


_T = TypeVar("_T")


def _json_sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            default=str,
        ).encode("utf-8")
    ).hexdigest().upper()


def _sha256_file(path: Path) -> str:
    return engine.sha256_file(path)


def _sha256_committed_file(repo_root: Path, path: str) -> str:
    """Hash the exact committed blob, independent of checkout line endings."""
    object_id = subprocess.check_output(
        ["git", "rev-parse", f"HEAD:{path}"], cwd=repo_root, text=True
    ).strip()
    payload = subprocess.check_output(
        ["git", "cat-file", "blob", object_id], cwd=repo_root
    )
    return hashlib.sha256(payload).hexdigest().upper()


def _component_worktree_is_clean(repo_root: Path) -> bool:
    paths = list(COMPONENT_PATHS)
    return (
        subprocess.run(
            ["git", "diff", "--quiet", "--", *paths], cwd=repo_root, check=False
        ).returncode
        == 0
        and subprocess.run(
            ["git", "diff", "--cached", "--quiet", "--", *paths],
            cwd=repo_root,
            check=False,
        ).returncode
        == 0
    )


def _limits(config: Mapping[str, Any]) -> dict[str, int]:
    values = dict(config["expression_limits"])
    return {
        "max_depth": int(values["maximum_depth"]),
        "max_raw_inputs": int(values["maximum_raw_fields"]),
        "max_rolling_windows": int(values["maximum_rolling_windows"]),
        "max_canonical_primitive_nodes": int(
            values["maximum_canonical_primitive_nodes"]
        ),
        "max_cross_asset_normalizations": int(
            values["maximum_cross_asset_normalizations"]
        ),
        "max_regime_gates": int(values["maximum_regime_gates"]),
    }


def validate_config(config: Mapping[str, Any]) -> None:
    budget = dict(config.get("search_budget") or {})
    seed_campaign = dict(config.get("seed_authority") or {}).get("campaign")
    targeted = seed_campaign == TARGETED_SEED_CAMPAIGN
    if config.get("experiment_id") != (
        "CRYPTO_SEARCH_CORE_V4_TEMPORAL_MECHANISM_PROGRAM_V1_20260807"
    ):
        raise ValueError("temporal program experiment identity changed")
    if config.get("authorization") != (
        "ONE_FRESH_STATE_SEQUENTIAL_UP_TO_50000_STRICT_TEMPORAL_PROGRAM_DEVELOPMENT_CAMPAIGN"
    ):
        raise PermissionError("temporal program authorization changed")
    expected_budget = {
        "strict_evaluated_maximum": 30_000 if targeted else 50_000,
        "raw_generation_attempts_maximum": 150_000 if targeted else 250_000,
        "wall_time_seconds_maximum": 36_000 if targeted else 64_800,
        "checkpoint_size": 2_000,
        "checkpoint_count_maximum": 15 if targeted else 25,
        "workers_default": 10,
        "workers_memory_fallback": 8,
    }
    if any(int(budget.get(key, -1)) != value for key, value in expected_budget.items()):
        raise ValueError("temporal program budget changed")
    if (
        budget.get("release_boundaries_strict")
        != (
            [10_000, 20_000, 30_000]
            if targeted
            else [10_000, 20_000, 30_000, 40_000, 50_000]
        )
        or budget.get("workers_12_forbidden") is not True
        or budget.get("automatic_release_only_through_frozen_gate") is not True
        or budget.get("later_tranche_proposal_pregeneration") is not False
    ):
        raise ValueError("temporal program sequential release contract changed")
    runtime_safety = dict(config.get("runtime_safety") or {})
    expected_runtime_safety = {
        "system_error_fatal": True,
        "stage0_attempt_round_robin": True,
        "process_evidence_required": True,
        "zero_strict_returned_pair_maximum": 64,
    }
    if runtime_safety != expected_runtime_safety:
        raise ValueError("temporal program runtime safety contract changed")
    adaptive_gate_contract = dict(
        dict(config["continuation_gates"])["stages_20000_30000_40000"]
    )
    if (
        float(
            adaptive_gate_contract["maximum_top_program_family_positive_share"]
        )
        != 0.60
        or adaptive_gate_contract.get(
            "program_family_concentration_is_diagnostic_only"
        )
        is not True
    ):
        raise ValueError("program-family concentration diagnostic contract changed")
    seed_authority = dict(config["seed_authority"])
    seeds = tuple(int(value) for value in seed_authority["seeds"])
    campaign = seed_authority.get("campaign")
    if campaign is None:
        expected_seeds = (2594819233, 4246332867, 3389304867, 168281835)
    elif campaign == "CRYPTO_TEMPORAL_ADAPTIVE_BROAD_V1":
        expected_seeds = ADAPTIVE_BROAD_SEEDS
        if seed_authority.get("derivation") != (
            "FIRST_UINT32_SHA256_CRYPTO_TEMPORAL_ADAPTIVE_BROAD_V1_PIPE_LANE_INDEX"
        ):
            raise ValueError("temporal adaptive broad seed derivation changed")
    elif campaign == EXPANSION_SEED_CAMPAIGN:
        expected_seeds = EXPANSION_LANE_SEEDS
        if seed_authority.get("derivation") != EXPANSION_SEED_DERIVATION:
            raise ValueError("temporal development expansion seed derivation changed")
    elif campaign == TARGETED_SEED_CAMPAIGN:
        expected_seeds = TARGETED_LANE_SEEDS
        if seed_authority.get("derivation") != TARGETED_SEED_DERIVATION:
            raise ValueError("temporal targeted deepening seed derivation changed")
    else:
        raise ValueError("temporal program seed campaign changed")
    if seeds != expected_seeds:
        raise ValueError("temporal program seed authority changed")
    evolution = dict(config["policy_parameters"]["temporal_program_evolution"])
    probabilities = {
        key: float(evolution[key]) for key in TARGETED_EVOLUTION_PROBABILITIES
    }
    expected_probabilities = (
        TARGETED_EVOLUTION_PROBABILITIES
        if targeted
        else {
            "parameter_mutation_probability": 0.50,
            "mechanism_mutation_probability": 0.30,
            "crossover_probability": 0.20,
        }
    )
    if probabilities != expected_probabilities or not math.isclose(
        sum(probabilities.values()), 1.0, rel_tol=0.0, abs_tol=1.0e-15
    ):
        raise ValueError("temporal program evolution operation mix changed")
    catalog = compile_temporal_program_catalog(config)
    if len(catalog) != 464 or {program.family_id for _, program in catalog} != {
        "P1_POSITION_STATE_CHANGE_TO_RESPONSE",
        "P2_RECENT_CROWDING_EVENT_TO_RESPONSE",
        "P3_FLOW_SHOCK_PERSISTENCE_TO_ABSORPTION",
        "P4_MULTISCALE_STATE_X_TRANSITION_ROUTING",
    }:
        raise ValueError("temporal program catalog changed")
    market = dict(config["market_contract"])
    if (
        int(market["execution_delay_hours"]) != 2
        or int(market["horizon_hours"]) != 4
        or market["cost"] != "EXISTING_5_BPS_FULL_L1"
        or market["matched_controls"] != "DUAL_AXIS_A_B_AB"
    ):
        raise ValueError("temporal program market contract changed")
    boundaries = dict(config["boundaries"])
    if boundaries.get("development_only") is not True:
        raise ValueError("temporal program is not development-only")
    for key in (
        "validation",
        "oos",
        "holdout",
        "promotion",
        "target_change",
        "mapping_change",
        "cost_change",
        "reward_change",
        "new_evaluator",
        "second_ast",
        "second_compiler",
        "cross_sprint_adaptive_memory",
        "parameter_tuning",
        "rescue_rerun",
        "new_graph_node",
    ):
        if boundaries.get(key) is not False:
            raise ValueError(f"temporal program forbidden boundary changed: {key}")


def _receipt_content_sha(receipt: Mapping[str, Any]) -> str:
    return _json_sha(
        {key: value for key, value in receipt.items() if key != "receipt_sha256"}
    )


def _qualification_scope(receipt: Mapping[str, Any]) -> dict[str, Any]:
    """Resolve a one-run release cap without changing the program budget contract."""
    replacement = dict(receipt.get("replacement_authorization") or {})
    if replacement.get("adaptive_broad_fresh_state") is True:
        families = tuple(
            str(value)
            for value in replacement.get("prequalified_program_families", ())
        )
        seeds = tuple(int(value) for value in replacement.get("fresh_state_seeds", ()))
        if (
            families != ADAPTIVE_BROAD_FAMILIES
            or seeds != ADAPTIVE_BROAD_SEEDS
            or int(replacement.get("qualification_strict_cap", -1)) != 50_000
            or replacement.get("stage0_only") is not False
            or replacement.get("prior_runtime_state_import_allowed") is not False
            or replacement.get("old_candidate_import") is not False
            or replacement.get("old_distribution_import") is not False
            or replacement.get("old_population_import") is not False
            or replacement.get("old_archive_import") is not False
        ):
            raise RuntimeError("temporal adaptive broad qualification scope changed")
        return {
            "strict_cap": 50_000,
            "stage0_only": False,
            "skip_stage0": True,
            "adaptive_start_strict": 0,
            "active_program_families": list(ADAPTIVE_BROAD_FAMILIES),
            "scope": "FRESH_STATE_PREQUALIFIED_ADAPTIVE_BROAD_PROGRAM",
        }
    has_cap = "qualification_strict_cap" in replacement
    has_stage0_only = "stage0_only" in replacement
    if not has_cap and not has_stage0_only:
        return {
            "strict_cap": 50_000,
            "stage0_only": False,
            "skip_stage0": False,
            "adaptive_start_strict": 10_000,
            "active_program_families": [],
            "scope": "FULL_SEQUENTIAL_PROGRAM",
        }
    if not has_cap or not has_stage0_only:
        raise RuntimeError("temporal program qualification scope is incomplete")
    strict_cap = int(replacement["qualification_strict_cap"])
    stage0_only = replacement["stage0_only"]
    if strict_cap not in {2_000, 10_000} or stage0_only is not True:
        raise RuntimeError("temporal program qualification scope changed")
    return {
        "strict_cap": strict_cap,
        "stage0_only": True,
        "skip_stage0": False,
        "adaptive_start_strict": 10_000,
        "active_program_families": [],
        "scope": (
            "FRESH_STATE_CHECKPOINT_ONLY_THROUGHPUT_QUALIFICATION"
            if strict_cap == 2_000
            else "FRESH_STATE_STAGE0_QUALIFICATION_ONLY"
        ),
    }


def _effective_config(
    config: Mapping[str, Any], receipt: Mapping[str, Any]
) -> dict[str, Any]:
    """Apply only receipt-frozen per-run seeds; never import campaign state."""

    effective = json.loads(json.dumps(config))
    scope = _qualification_scope(receipt)
    if bool(scope.get("skip_stage0")):
        effective["seed_authority"] = {
            **dict(effective["seed_authority"]),
            "campaign": "CRYPTO_TEMPORAL_ADAPTIVE_BROAD_V1",
            "derivation": (
                "FIRST_UINT32_SHA256_CRYPTO_TEMPORAL_ADAPTIVE_BROAD_V1_PIPE_LANE_INDEX"
            ),
            "seeds": list(ADAPTIVE_BROAD_SEEDS),
            "old_campaign_seed_reuse": False,
        }
    validate_config(effective)
    return effective


def _successor_effective_config(config: Mapping[str, Any]) -> dict[str, Any]:
    """Use the frozen adaptive-broad lanes; Random has a separate fresh contract."""

    effective = json.loads(json.dumps(config))
    effective["seed_authority"] = {
        **dict(effective["seed_authority"]),
        "campaign": "CRYPTO_TEMPORAL_ADAPTIVE_BROAD_V1",
        "derivation": (
            "FIRST_UINT32_SHA256_CRYPTO_TEMPORAL_ADAPTIVE_BROAD_V1_PIPE_LANE_INDEX"
        ),
        "seeds": list(ADAPTIVE_BROAD_SEEDS),
        "old_campaign_seed_reuse": False,
    }
    validate_config(effective)
    return effective


def _expansion_effective_config(config: Mapping[str, Any]) -> dict[str, Any]:
    """Freeze a fresh four-lane seed campaign without changing search policy."""

    effective = json.loads(json.dumps(config))
    effective["seed_authority"] = {
        **dict(effective["seed_authority"]),
        "campaign": EXPANSION_SEED_CAMPAIGN,
        "derivation": EXPANSION_SEED_DERIVATION,
        "seeds": list(EXPANSION_LANE_SEEDS),
        "old_campaign_seed_reuse": False,
    }
    validate_config(effective)
    return effective


def _targeted_effective_config(config: Mapping[str, Any]) -> dict[str, Any]:
    """Freeze the bounded P1/P4 campaign and its evidence-backed operation mix."""

    effective = json.loads(json.dumps(config))
    effective["seed_authority"] = {
        **dict(effective["seed_authority"]),
        "campaign": TARGETED_SEED_CAMPAIGN,
        "derivation": TARGETED_SEED_DERIVATION,
        "seeds": list(TARGETED_LANE_SEEDS),
        "old_campaign_seed_reuse": False,
    }
    effective["search_budget"].update(
        {
            "strict_evaluated_maximum": 30_000,
            "raw_generation_attempts_maximum": 150_000,
            "wall_time_seconds_maximum": 36_000,
            "checkpoint_count_maximum": 15,
            "release_boundaries_strict": [10_000, 20_000, 30_000],
        }
    )
    effective["policy_parameters"]["temporal_program_evolution"].update(
        TARGETED_EVOLUTION_PROBABILITIES
    )
    validate_config(effective)
    return effective


def _checkpoint_qualification_terminal_reason(
    *,
    checkpoint_index: int,
    qualification_scope: Mapping[str, Any],
    observed_strict_per_hour: float,
    minimum_strict_per_hour: float,
) -> str | None:
    if observed_strict_per_hour < minimum_strict_per_hour:
        return "ENGINE_BUDGET_EXHAUSTED_THROUGHPUT_FLOOR"
    if (
        int(qualification_scope["strict_cap"]) == 2_000
        and checkpoint_index == 0
    ):
        return "CHECKPOINT_ONLY_QUALIFICATION_CAP_REACHED"
    return None


def _merge_checkpoint_terminal_reason(
    current_reason: str | None,
    qualification_reason: str | None,
) -> str | None:
    """Keep an already-issued market/gate stop authoritative."""
    return current_reason if current_reason is not None else qualification_reason


def _seal_terminal_decision(
    state: dict[str, Any],
    *,
    reason: str,
    strict_boundary: int,
) -> dict[str, Any]:
    """Persist the point after which market/search state is immutable."""

    if not reason:
        raise ValueError("terminal decision reason is empty")
    boundary = int(strict_boundary)
    payload = {
        "schema_version": 1,
        "status": "SEALED",
        "terminal_reason": str(reason),
        "valid_prefix_boundary": boundary,
        "invalid_suffix_start": boundary + 1,
    }
    existing = state.get("terminal_decision")
    if existing is not None and dict(existing) != payload:
        raise ProgramRunInvalid("TERMINAL_DECISION_IDENTITY_CHANGED")
    state["terminal_decision"] = payload
    return payload


def _assert_terminal_market_open(
    state: Mapping[str, Any],
    *,
    action: str,
) -> None:
    sealed = state.get("terminal_decision")
    if isinstance(sealed, Mapping) and sealed.get("status") == "SEALED":
        raise RuntimeError(
            "TERMINAL_DECISION_SEALED:"
            + str(sealed.get("terminal_reason"))
            + ":"
            + str(action)
        )


def _call_with_terminal_invariant(
    state: Mapping[str, Any],
    action: str,
    callback: Callable[..., _T],
    *args: Any,
    **kwargs: Any,
) -> _T:
    _assert_terminal_market_open(state, action=action)
    return callback(*args, **kwargs)


def _valid_prefix_fields(
    state: Mapping[str, Any],
    *,
    status: str,
    strict_count: int,
) -> dict[str, Any]:
    sealed = state.get("terminal_decision")
    if isinstance(sealed, Mapping) and sealed.get("status") == "SEALED":
        boundary = int(sealed["valid_prefix_boundary"])
        invalid_suffix_start = int(sealed["invalid_suffix_start"])
        terminal_invalid = bool(
            str(status) == "ENGINE_RUN_INVALID" or int(strict_count) > boundary
        )
        return {
            "valid_prefix_boundary": boundary,
            "invalid_suffix_start": invalid_suffix_start,
            "economic_prefix_valid": True,
            "orchestration_terminal_invalid": terminal_invalid,
        }
    return {
        "valid_prefix_boundary": None,
        "invalid_suffix_start": None,
        "economic_prefix_valid": False,
        "orchestration_terminal_invalid": str(status) == "ENGINE_RUN_INVALID",
    }


def validate_receipt(
    repo_root: Path,
    *,
    config: Mapping[str, Any],
    require_authorized: bool,
) -> dict[str, Any]:
    receipt = engine._read_json(repo_root / RECEIPT_PATH)
    if receipt.get("receipt_id") != "CRYPTO_TEMPORAL_MECHANISM_PROGRAM_V1_RECEIPT":
        raise RuntimeError("temporal program receipt identity changed")
    if receipt.get("receipt_sha256") != _receipt_content_sha(receipt):
        raise RuntimeError("temporal program receipt hash changed")
    if require_authorized and (
        receipt.get("status") != "RUN_AUTHORIZED_DEVELOPMENT_ONLY"
        or receipt.get("run_authorized") is not True
    ):
        raise RuntimeError("temporal program receipt is not authorized")
    if receipt.get("authorization") != config["authorization"]:
        raise RuntimeError("temporal program receipt authorization changed")
    expected_budget = {
        "strict_evaluated_maximum": 50_000,
        "raw_generation_attempts_maximum": 250_000,
        "wall_time_seconds_maximum": 64_800,
        "checkpoint_size": 2_000,
        "release_boundaries_strict": [10_000, 20_000, 30_000, 40_000, 50_000],
        "workers": [10, 8],
    }
    if dict(receipt.get("budget") or {}) != expected_budget:
        raise RuntimeError("temporal program receipt budget changed")
    expected_boundaries = {
        "automatic_next_run": False,
        "development_only": True,
        "holdout": False,
        "oos": False,
        "promotion": False,
        "rescue_rerun": False,
        "validation": False,
    }
    if dict(receipt.get("boundaries") or {}) != expected_boundaries:
        raise RuntimeError("temporal program receipt boundaries changed")
    expected_market = {
        "carrier": config["market_contract"]["carrier"],
        "cost_bps": 5,
        "horizon_hours": int(config["market_contract"]["horizon_hours"]),
        "matched_controls": config["market_contract"]["matched_controls"],
        "target": config["market_contract"]["target"],
    }
    if dict(receipt.get("market_authority") or {}) != expected_market:
        raise RuntimeError("temporal program receipt market authority changed")
    replacement = dict(receipt.get("replacement_authorization") or {})
    adaptive_broad = replacement.get("adaptive_broad_fresh_state") is True
    seed_contract_valid = (
        replacement.get("seed_contract_unchanged") is True
        if not adaptive_broad
        else replacement.get("seed_contract_unchanged") is False
        and replacement.get("fresh_seed_contract_new") is True
    )
    if replacement and (
        replacement.get("budget_contract_unchanged") is not True
        or replacement.get("market_contract_unchanged") is not True
        or not seed_contract_valid
        or replacement.get("rescue_rerun") is not False
        or int(replacement.get("prior_strict_evaluated", -1)) < 0
        or int(replacement.get("prior_generation_attempts", -1)) < 0
        or replacement.get("prior_runtime_state_import_allowed") is not False
        or len(str(replacement.get("replaces_receipt_sha256") or "")) != 64
    ):
        raise RuntimeError("temporal program replacement authority changed")
    scope = _qualification_scope(receipt)
    if adaptive_broad:
        selection = dict(receipt.get("selection_evidence") or {})
        expected_paths = {
            "runtime/crypto_temporal_mechanism_program_v1_20260810s0/final_decision.json",
            "runtime/crypto_temporal_mechanism_program_v1_20260810s0/continuation_decision_010000.json",
        }
        files = dict(selection.get("committed_file_sha256") or {})
        if (
            set(files) != expected_paths
            or selection.get("producer_source_sha")
            != "a051f557844d59d829be80c33b7517157828a482"
            or tuple(selection.get("continuing_families") or ())
            != ADAPTIVE_BROAD_FAMILIES
            or any(
                _sha256_committed_file(repo_root, path) != str(files[path])
                for path in expected_paths
            )
        ):
            raise RuntimeError("temporal adaptive broad selection evidence changed")
    branch = subprocess.check_output(
        ["git", "branch", "--show-current"], cwd=repo_root, text=True
    ).strip()
    if branch != receipt.get("expected_branch"):
        raise RuntimeError("temporal program receipt branch changed")
    implementation_sha = str(receipt.get("authorized_implementation_sha") or "")
    if not implementation_sha or subprocess.run(
        ["git", "merge-base", "--is-ancestor", implementation_sha, "HEAD"],
        cwd=repo_root,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode != 0:
        raise RuntimeError("temporal program authorized implementation is not an ancestor")
    if not _component_worktree_is_clean(repo_root):
        raise RuntimeError("temporal program component worktree changed")
    if receipt.get("config_sha256") != _sha256_committed_file(
        repo_root, CONFIG_PATH
    ):
        raise RuntimeError("temporal program receipt config changed")
    component_hashes = dict(receipt.get("component_sha256") or {})
    if set(component_hashes) != set(COMPONENT_PATHS) or any(
        _sha256_committed_file(repo_root, path) != str(component_hashes[path])
        for path in COMPONENT_PATHS
    ):
        raise RuntimeError("temporal program component bundle changed")
    catalog_sha = program_catalog_payload(
        compile_temporal_program_catalog(config)
    )["catalog_sha256"]
    if receipt.get("program_catalog_sha256") != catalog_sha:
        raise RuntimeError("temporal program receipt catalog changed")
    return receipt


def _contracts_from_manifest(repo_root: Path, config: Mapping[str, Any]) -> tuple[FieldContract, ...]:
    manifest = engine._read_json(
        repo_root / str(config["source_authorities"]["source_carrier_manifest"])
    )
    contracts = tuple(
        FieldContract(
            str(row["field_id"]),
            str(row["value_type"]),
            str(row["unit"]),
            int(row["observable_lag_hours"]),
            str(row["pit_authority"]),
        )
        for row in manifest["contracts"]
    )
    if len(contracts) != 115:
        raise RuntimeError("temporal program requires the existing 115-field carrier")
    return contracts


def _validate_active_source_smoke_receipt(
    repo_root: Path,
    config: Mapping[str, Any],
) -> dict[str, Any]:
    receipt = engine._read_json(repo_root / RECEIPT_PATH)
    if receipt.get("run_authorized") is True:
        return validate_receipt(
            repo_root,
            config=config,
            require_authorized=True,
        )
    return receipt


def source_smoke(repo_root: Path) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    config = engine._read_json(repo_root / CONFIG_PATH)
    validate_config(config)
    receipt = _validate_active_source_smoke_receipt(repo_root, config)
    config = _effective_config(config, receipt)
    economic = resolve_search_economic_receipt(
        repo_root, str(config["source_authorities"]["economic_receipt_template"])
    )
    train = dict(economic["evidence_partition"]["train"])
    paired_partition = validate_pair_evaluation_request(
        block_start=str(train["start"]),
        block_end=str(train["end_exclusive"]),
        block_role=BLOCK_ROLE,
        economic_receipt=economic,
        include_paired_diagnostic_paths=True,
    )
    contracts = _contracts_from_manifest(repo_root, config)
    registry = TypedExpressionRegistry(contracts, **_limits(config))
    domains = {**mechanism_role_domains(contracts), "__HORIZONS__": (4,)}
    catalog = compile_temporal_program_catalog(config)
    family_rows = []
    for family in sorted({program.family_id for _, program in catalog}):
        mechanism, program = next(
            pair for pair in catalog if pair[1].family_id == family
        )
        policy = engine.MechanismRandomV2(
            int(config["seed_authority"]["seeds"][0]),
            registry,
            (mechanism,),
            _policy_parameters(config, ((mechanism, program),)),
        )
        candidate, metadata = policy.propose()
        static = static_counterpart(registry, candidate, domains=domains)
        if not engine._candidate_rebuild_verified(registry, candidate, {}):
            raise RuntimeError("temporal program source replay failed")
        if not engine._candidate_rebuild_verified(registry, static, {}):
            raise RuntimeError("temporal static source replay failed")
        family_rows.append(
            {
                "family_id": family,
                "temporal_candidate_id": candidate.candidate_id,
                "static_candidate_id": static.candidate_id,
                "raw_fields": list(candidate.raw_fields),
                "depth": candidate.expression_depth,
                "rolling_windows": list(candidate.rolling_windows),
                "raw_attempts": int(metadata["raw_attempts"]),
            }
        )
    return {
        "status": "PASS",
        "market_arrays_read": 0,
        "candidate_evaluations": 0,
        "paired_context_admission": paired_partition,
        "family_count": len(family_rows),
        "catalog_count": len(catalog),
        "catalog_sha256": program_catalog_payload(catalog)["catalog_sha256"],
        "records": family_rows,
    }


def _policy_parameters(
    config: Mapping[str, Any],
    catalog: Sequence[tuple[MechanismSpec, TemporalProgramSpec]],
    *,
    arm: str = "temporal_program_random",
) -> dict[str, Any]:
    parameters = dict(config["policy_parameters"][arm])
    parameters.update(
        {
            "candidate_builder": PROGRAM_BUILDER_ID,
            "temporal_program_specs": [program.to_dict() for _, program in catalog],
            "time_scale_authority": dict(config["time_scale_authority"]),
            "allowed_horizons": [4],
            "balanced_template_sampling": True,
        }
    )
    return parameters


def _make_policy(
    *,
    arm: str,
    seed: int,
    registry: TypedExpressionRegistry,
    config: Mapping[str, Any],
    catalog: Sequence[tuple[MechanismSpec, TemporalProgramSpec]],
) -> Any:
    mechanisms = tuple(mechanism for mechanism, _ in catalog)
    parameters = _policy_parameters(config, catalog, arm=arm)
    if arm == "temporal_program_random":
        return engine.MechanismRandomV2(seed, registry, mechanisms, parameters)
    if arm == "temporal_program_cem":
        return engine.MechanismCEMV2(seed, registry, mechanisms, parameters)
    if arm == "temporal_program_evolution":
        return engine.MechanismEvolutionV2(seed, registry, mechanisms, parameters)
    raise ValueError(f"unknown temporal program arm: {arm}")


def _worker_program_pair(payload: Mapping[str, Any]) -> dict[str, Any]:
    pair_id = str(payload["paired_program_id"])
    engine._write_worker_process_evidence(
        evidence_root=engine._WORKER_PROCESS_EVIDENCE_ROOT,
        channel="task",
        stage="TASK_STARTED",
        candidate_id=pair_id,
    )
    started_cpu = time.process_time()
    started_wall = time.perf_counter()
    process = psutil.Process(os.getpid())
    try:
        if engine._WORKER_STORE is None or engine._WORKER_REGISTRY is None:
            raise RuntimeError("temporal program pair worker is not initialized")
        evaluations: dict[str, dict[str, Any]] = {}
        paths: dict[str, dict[str, Any]] = {}
        candidates = {
            name: CandidateSpec.from_dict(payload[name])
            for name in ("static", "temporal")
        }
        for name, candidate in candidates.items():
            evaluation = evaluate_pair(
                store=engine._WORKER_STORE,
                registry=engine._WORKER_REGISTRY,
                candidate=candidate,
                block_start=engine._WORKER_BLOCK_START,
                block_end=engine._WORKER_BLOCK_END,
                block_role=engine._WORKER_BLOCK_ROLE,
                behavior_contract=engine._WORKER_BEHAVIOR_CONTRACT,
                economic_receipt=engine._WORKER_ECONOMIC_RECEIPT,
                include_control_provenance=True,
                optimizer_block_contract=engine._WORKER_OPTIMIZER_BLOCK_CONTRACT,
                include_paired_diagnostic_paths=True,
            )
            paths[name] = dict(evaluation.pop("_paired_diagnostic_paths"))
            evaluations[name] = evaluation
        common = _paired_common_support(
            paths["static"],
            paths["temporal"],
            cost_bps=float(evaluations["static"]["cost_bps"]),
            horizon=4,
        )
        status = "PAIR_EVALUATED"
        error = None
    except ControlBehaviorDegeneracyError as failure:
        status = "PAIR_REJECTED"
        error = type(failure).__name__ + ":" + str(failure)
        evaluations = {}
        common = None
    except MemoryError as failure:
        status = "MEMORY_ERROR"
        error = type(failure).__name__ + ":" + str(failure)
        evaluations = {}
        common = None
    except EvaluationContractError as failure:
        status = "SYSTEM_ERROR"
        error = type(failure).__name__ + ":" + str(failure)
        evaluations = {}
        common = None
    except (ValueError, FloatingPointError) as failure:
        status = (
            "SYSTEM_ERROR"
            if evaluation_failure_is_contract_error(failure)
            else "PAIR_REJECTED"
        )
        error = type(failure).__name__ + ":" + str(failure)
        evaluations = {}
        common = None
    except BaseException as failure:
        engine._write_worker_process_evidence(
            evidence_root=engine._WORKER_PROCESS_EVIDENCE_ROOT,
            channel="task",
            stage="TASK_FAILED",
            candidate_id=pair_id,
            error=failure,
        )
        raise
    memory = process.memory_info()
    result = {
        "status": status,
        "paired_program_id": pair_id,
        "static": evaluations.get("static"),
        "temporal": evaluations.get("temporal"),
        "common_support": common,
        "error": error,
        "process_cpu_seconds": time.process_time() - started_cpu,
        "wall_seconds": time.perf_counter() - started_wall,
        "worker_rss_bytes": int(memory.rss),
        "worker_private_bytes": int(getattr(memory, "private", memory.rss)),
        "memory_error": status == "MEMORY_ERROR",
        "system_error": status == "SYSTEM_ERROR",
    }
    engine._write_worker_process_evidence(
        evidence_root=engine._WORKER_PROCESS_EVIDENCE_ROOT,
        channel="task",
        stage="TASK_COMPLETED",
        candidate_id=pair_id,
        outcome=status,
    )
    return result


def _rejected_worker_runtime_fields(result: Mapping[str, Any]) -> dict[str, Any]:
    """Preserve worker cost for rejected pairs without changing gate authority."""

    return {
        "pair_process_cpu_seconds": float(result["process_cpu_seconds"]),
        "pair_wall_seconds": float(result["wall_seconds"]),
        "worker_rss_bytes": int(result["worker_rss_bytes"]),
        "worker_private_bytes": int(result["worker_private_bytes"]),
    }


def _dual_net(evaluation: Mapping[str, Any]) -> bool:
    return bool(
        float(evaluation["left_incremental"]["net_mean"]) > 0.0
        and float(evaluation["right_incremental"]["net_mean"]) > 0.0
    )


def _worst_net(evaluation: Mapping[str, Any]) -> float:
    return min(
        float(evaluation["left_incremental"]["net_mean"]),
        float(evaluation["right_incremental"]["net_mean"]),
    )


def _pair_diagnostic(
    *,
    pair: Mapping[str, Any],
    static: Mapping[str, Any],
    temporal: Mapping[str, Any],
    common: Mapping[str, Any],
) -> dict[str, Any]:
    static_worst = _worst_net(static)
    temporal_worst = _worst_net(temporal)
    return {
        "paired_program_id": str(pair["paired_program_id"]),
        "program_family_id": str(pair["program_family_id"]),
        "program_id": str(pair["program_id"]),
        "seed": int(pair["seed"]),
        "static_candidate_id": str(pair["static"].candidate_id),
        "temporal_candidate_id": str(pair["temporal"].candidate_id),
        "static_worst_axis_net_mean": static_worst,
        "temporal_worst_axis_net_mean": temporal_worst,
        "paired_worst_axis_net_delta": temporal_worst - static_worst,
        "common_support_paired_worst_axis_net_delta": float(
            common["paired_worst_axis_net_delta"]
        ),
        "static_dual_axis_net_positive": _dual_net(static),
        "temporal_dual_axis_net_positive": _dual_net(temporal),
        "static_replicated_2_of_3": int(
            static["block_robust_ordering"]["replicated_positive_block_count"]
        )
        >= 2,
        "temporal_replicated_2_of_3": int(
            temporal["block_robust_ordering"]["replicated_positive_block_count"]
        )
        >= 2,
        "static_matched_positive": bool(static["matched_positive"]),
        "temporal_matched_positive": bool(temporal["matched_positive"]),
        "common_support_json": json.dumps(
            common, sort_keys=True, separators=(",", ":")
        ),
    }


def stage0_family_decisions(
    rows: Sequence[Mapping[str, Any]], config: Mapping[str, Any]
) -> dict[str, Any]:
    frame = pd.DataFrame(list(rows))
    expected = int(config["stage_allocations"][0]["program_family_pairs_each"])
    if len(frame) != expected * 4:
        return {
            "status": "INVALID_RUN_FAIL_CLOSED",
            "reason": "STAGE0_PAIR_COUNT_CHANGED",
            "continuing_families": [],
            "family_decisions": [],
        }
    gate = dict(config["continuation_gates"]["stage_10000"])
    family_rows: list[dict[str, Any]] = []
    for family, local in frame.groupby("program_family_id", sort=True):
        if len(local) != expected:
            return {
                "status": "INVALID_RUN_FAIL_CLOSED",
                "reason": "STAGE0_FAMILY_QUOTA_CHANGED",
                "continuing_families": [],
                "family_decisions": [],
            }
        deltas = local["paired_worst_axis_net_delta"].astype(float)
        static_net = local["static_dual_axis_net_positive"].astype(bool)
        temporal_net = local["temporal_dual_axis_net_positive"].astype(bool)
        static_replicated = local["static_replicated_2_of_3"].astype(bool)
        temporal_replicated = local["temporal_replicated_2_of_3"].astype(bool)
        positive_by_tuple = local.groupby("program_id")[
            "paired_worst_axis_net_delta"
        ].median()
        positive_tuples = set(
            positive_by_tuple[positive_by_tuple > 0.0].index.astype(str)
        )
        positive_rows = local[deltas > 0.0]
        top_share = (
            float(positive_rows["program_id"].value_counts().iloc[0])
            / float(len(positive_rows))
            if len(positive_rows)
            else 1.0
        )
        routes = {
            "paired_worst_axis_net_median_strictly_positive": float(deltas.median()) > 0.0,
            "program_win_fraction_minimum": float((deltas > 0.0).mean())
            >= float(gate["primary_routes"]["program_win_fraction_minimum"]),
            "dual_axis_net_positive_rate_absolute_improvement_minimum": float(
                temporal_net.mean() - static_net.mean()
            )
            >= float(
                gate["primary_routes"][
                    "dual_axis_net_positive_rate_absolute_improvement_minimum"
                ]
            ),
            "replicated_2_of_3_rate_absolute_improvement_minimum": float(
                temporal_replicated.mean() - static_replicated.mean()
            )
            >= float(
                gate["primary_routes"][
                    "replicated_2_of_3_rate_absolute_improvement_minimum"
                ]
            ),
            "matched_positive_count_above_static": int(
                local["temporal_matched_positive"].astype(bool).sum()
            )
            > int(local["static_matched_positive"].astype(bool).sum()),
        }
        breadth = {
            "minimum_positive_semantic_tuple_count": len(positive_tuples)
            >= int(gate["breadth_required_for_a_family"]["minimum_positive_semantic_tuple_count"]),
            "maximum_top_semantic_tuple_positive_delta_share": top_share
            <= float(
                gate["breadth_required_for_a_family"][
                    "maximum_top_semantic_tuple_positive_delta_share"
                ]
            ),
        }
        family_rows.append(
            {
                "program_family_id": str(family),
                "pair_count": len(local),
                "paired_delta_median": float(deltas.median()),
                "program_win_fraction": float((deltas > 0.0).mean()),
                "static_dual_net_rate": float(static_net.mean()),
                "temporal_dual_net_rate": float(temporal_net.mean()),
                "static_replicated_rate": float(static_replicated.mean()),
                "temporal_replicated_rate": float(temporal_replicated.mean()),
                "static_matched_positive_count": int(
                    local["static_matched_positive"].astype(bool).sum()
                ),
                "temporal_matched_positive_count": int(
                    local["temporal_matched_positive"].astype(bool).sum()
                ),
                "positive_semantic_tuple_count": len(positive_tuples),
                "top_positive_semantic_tuple_share": top_share,
                "primary_routes": routes,
                "breadth_checks": breadth,
                "continue": any(routes.values()) and all(breadth.values()),
            }
        )
    continuing = [
        row["program_family_id"] for row in family_rows if row["continue"]
    ]
    return {
        "status": "CONTINUE" if continuing else "STOP_TEMPORAL_PROGRAM_SPACE_NOT_SUPPORTED",
        "reason": "FROZEN_FAMILY_LOCAL_STAGE0_GATE",
        "continuing_families": continuing,
        "family_decisions": family_rows,
        "next_stage_proposals_generated": False,
    }


def _top_decile(values: Sequence[float]) -> float:
    finite = sorted(
        (float(value) for value in values if math.isfinite(float(value))),
        reverse=True,
    )
    count = max(1, int(math.ceil(0.1 * len(finite))))
    return float(np.mean(finite[:count])) if finite else float("nan")


def _arm_slice(frame: pd.DataFrame, arm: str, count: int) -> pd.DataFrame:
    local = frame.loc[frame["arm"].astype(str) == arm].sort_values(
        "arm_completion_ordinal", kind="stable"
    )
    return local.iloc[:count]


def adaptive_gate(
    ledger: Sequence[Mapping[str, Any]],
    *,
    state: Mapping[str, Any],
    strict_boundary: int,
    config: Mapping[str, Any],
    tranche_size: int = 10_000,
) -> dict[str, Any]:
    frame = pd.DataFrame(list(ledger))
    adaptive_start = int(state.get("adaptive_start_strict", 10_000))
    if int(tranche_size) <= 0:
        raise ValueError("adaptive gate tranche size must be positive")
    tranche_start = max(adaptive_start, int(strict_boundary) - int(tranche_size))
    frame = frame.loc[
        (frame["completion_ordinal"].astype(int) > tranche_start)
        & (frame["completion_ordinal"].astype(int) <= int(strict_boundary))
    ]
    active_families = set(
        str(value) for value in state.get("active_program_families", ())
    )
    random_mask = frame["arm"].astype(str) == ARMS[0]
    if active_families:
        random_mask &= frame["program_family_id"].astype(str).isin(active_families)
    random_frame = frame.loc[random_mask]
    random_count = len(random_frame)
    adaptive_contract = dict(
        dict(config["continuation_gates"])["stages_20000_30000_40000"]
    )
    family_concentration_threshold = float(
        adaptive_contract["maximum_top_program_family_positive_share"]
    )
    decisions: dict[str, Any] = {}
    updated_states = dict(state["arm_states"])
    for arm in ARMS[1:]:
        arm_count = int((frame["arm"].astype(str) == arm).sum())
        common = min(random_count, arm_count)
        if common <= 0:
            decisions[arm] = {"decision": "NO_OBSERVATIONS", "same_count": 0}
            continue
        random_rows = random_frame.sort_values(
            "arm_completion_ordinal", kind="stable"
        ).iloc[:common]
        arm_rows = _arm_slice(frame, arm, common)

        def metrics(local: pd.DataFrame) -> dict[str, Any]:
            families = int(local["behavior_family_id"].astype(str).nunique())
            positives = local[
                (local["left_incremental_net_mean"].astype(float) > 0.0)
                & (local["right_incremental_net_mean"].astype(float) > 0.0)
            ]
            replicated = int(local["replicated_candidate"].fillna(False).astype(bool).sum())
            family_positive = (
                positives.groupby("program_family_id").size()
                if len(positives)
                else pd.Series(dtype=int)
            )
            dominant_program_family = (
                str(family_positive.idxmax()) if len(family_positive) else None
            )
            dominant_program_family_positive_share = (
                float(family_positive.max() / family_positive.sum())
                if len(family_positive)
                else 0.0
            )
            if not len(family_positive):
                family_concentration_diagnostic = "NO_POSITIVE_PROGRAM_FAMILY"
            elif (
                dominant_program_family_positive_share
                > family_concentration_threshold
            ):
                family_concentration_diagnostic = "ABOVE_DIAGNOSTIC_THRESHOLD"
            else:
                family_concentration_diagnostic = "WITHIN_DIAGNOSTIC_THRESHOLD"
            return {
                "same_count": len(local),
                "mean_search_reward": float(local["search_reward"].astype(float).mean()),
                "top_decile_search_reward": _top_decile(local["search_reward"]),
                "dual_axis_net_positive_per_1k": float(len(positives) * 1000.0 / len(local)),
                "replicated_2_of_3_per_1k": float(replicated * 1000.0 / len(local)),
                "new_behavior_families_per_1k": float(families * 1000.0 / len(local)),
                "behavior_family_count": families,
                "strict_per_process_cpu_hour": float(
                    len(local)
                    * 3600.0
                    / max(1.0e-12, float(local["total_process_cpu_seconds"].sum()))
                ),
                "dominant_program_family": dominant_program_family,
                "dominant_program_family_positive_share": (
                    dominant_program_family_positive_share
                ),
                "family_concentration_diagnostic": (
                    family_concentration_diagnostic
                ),
            }

        control = metrics(random_rows)
        observed = metrics(arm_rows)
        quality = [
            observed[key] > control[key]
            for key in ("mean_search_reward", "top_decile_search_reward")
        ]
        productivity = [
            observed[key] > control[key]
            for key in (
                "dual_axis_net_positive_per_1k",
                "replicated_2_of_3_per_1k",
                "new_behavior_families_per_1k",
                "strict_per_process_cpu_hour",
            )
        ]
        behavior_breadth = bool(
            observed["behavior_family_count"]
            >= 0.8 * control["behavior_family_count"]
        )
        incremental = any(quality) and any(productivity) and behavior_breadth
        old = str(updated_states.get(arm, "ACTIVE"))
        if incremental:
            new = "ACTIVE"
        elif old == "DIAGNOSTIC":
            new = "EXITED"
        else:
            new = "DIAGNOSTIC"
        updated_states[arm] = new
        decisions[arm] = {
            "decision": new,
            "same_count": common,
            "quality_improvement": any(quality),
            "productivity_improvement": any(productivity),
            "behavior_breadth_pass": behavior_breadth,
            "family_concentration_diagnostic": observed[
                "family_concentration_diagnostic"
            ],
            "random": control,
            "observed": observed,
        }
    return {
        "status": "CONTINUE" if any(updated_states.get(arm) != "EXITED" for arm in ARMS[1:]) else "STOP_ALL_ADAPTIVE_ARMS_EXITED",
        "strict_boundary": int(strict_boundary),
        "arm_states_before": dict(state["arm_states"]),
        "arm_states_after": updated_states,
        "arm_decisions": decisions,
        "next_stage_proposals_generated": False,
    }


def _checkpoint_allocation(
    state: Mapping[str, Any],
    checkpoint_index: int,
    config: Mapping[str, Any] | None = None,
) -> dict[str, int]:
    if not bool(state.get("skip_stage0")) and checkpoint_index < 5:
        return {"paired_static": 1_000, "temporal_program_random": 1_000}
    states = dict(state["arm_states"])
    configured = {
        ARMS[0]: 2_000,
        ARMS[1]: 4_000,
        ARMS[2]: 4_000,
    }
    if config is not None:
        configured = {
            str(arm): int(count)
            for arm, count in dict(
                config["stage_allocations"][1]["allocation_per_10000"]
            ).items()
        }
    if set(configured) != set(ARMS) or sum(configured.values()) != 10_000:
        raise RuntimeError("temporal program fixed policy allocation invalid")
    allocation = {ARMS[0]: configured[ARMS[0]] // 5, ARMS[1]: 0, ARMS[2]: 0}
    diagnostic = [arm for arm in ARMS[1:] if states.get(arm) == "DIAGNOSTIC"]
    active = [arm for arm in ARMS[1:] if states.get(arm) == "ACTIVE"]
    for arm in diagnostic:
        allocation[arm] = 200
    remaining = 2_000 - sum(allocation.values())
    if active:
        active_weight = sum(configured[arm] for arm in active)
        assigned = 0
        for arm in active[:-1]:
            share = remaining * configured[arm] // active_weight
            allocation[arm] = share
            assigned += share
        allocation[active[-1]] = remaining - assigned
    else:
        allocation[ARMS[0]] += remaining
    return allocation


def _new_state(source_sha: str, frozen_hash: str, config: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "source_sha": source_sha,
        "frozen_contract_sha256": frozen_hash,
        "next_checkpoint_index": 0,
        "generation_attempts": 0,
        "compile_valid": 0,
        "exact_unique": 0,
        "strict_evaluated": 0,
        "attempted_exact_ids": [],
        "completed_pair_ids": [],
        "workers_initial": int(config["search_budget"]["workers_default"]),
        "workers": int(config["search_budget"]["workers_default"]),
        "memory_fallback_used": False,
        "wall_elapsed_seconds": 0.0,
        "arm_states": {ARMS[1]: "ACTIVE", ARMS[2]: "ACTIVE"},
        "active_program_families": [],
        "skip_stage0": False,
        "adaptive_start_strict": 10_000,
        "failure_counts": {},
        "stage0_lane_cursor": 0,
        "evaluation_batch_index": 0,
        "returned_pair_results": 0,
        "system_error_count": 0,
        "arm_counters": {
            arm: {
                "generation_attempts": 0,
                "compile_valid": 0,
                "exact_unique": 0,
                "strict_evaluated": 0,
                "process_cpu_seconds": 0.0,
            }
            for arm in ("paired_static", *ARMS)
        },
        "policy_local_family_counts": {},
    }


def _program_family_metric_rows(
    *,
    ledger: Sequence[Mapping[str, Any]],
    pair_rows: Sequence[Mapping[str, Any]],
    config: Mapping[str, Any],
    adaptive_start_strict: int = 10_000,
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    if len(pair_rows) == 5_000:
        decision = stage0_family_decisions(pair_rows, config)
        for row in decision.get("family_decisions", ()):
            flat = dict(row)
            flat["primary_routes_json"] = json.dumps(
                flat.pop("primary_routes"), sort_keys=True, separators=(",", ":")
            )
            flat["breadth_checks_json"] = json.dumps(
                flat.pop("breadth_checks"), sort_keys=True, separators=(",", ":")
            )
            output.append(
                {
                    "stage": "PROGRAM_SPACE_ACTIVATION",
                    "arm": "paired_static_vs_temporal_program_random",
                    **flat,
                }
            )
    if ledger:
        frame = pd.DataFrame(list(ledger))
        frame = frame.loc[
            (frame["completion_ordinal"].astype(int) > int(adaptive_start_strict))
            & (frame["representation"].astype(str) == "TEMPORAL_PROGRAM")
        ]
        for (arm, family), local in frame.groupby(
            ["arm", "program_family_id"], sort=True
        ):
            dual_net = (
                (local["left_incremental_net_mean"].astype(float) > 0.0)
                & (local["right_incremental_net_mean"].astype(float) > 0.0)
            )
            output.append(
                {
                    "stage": "FRESH_POLICY_SEARCH",
                    "arm": str(arm),
                    "program_family_id": str(family),
                    "strict_evaluated_count": len(local),
                    "behavior_family_count": int(
                        local["behavior_family_id"].astype(str).nunique()
                    ),
                    "dual_axis_net_positive_count": int(dual_net.sum()),
                    "replicated_2_of_3_count": int(
                        local["replicated_candidate"].fillna(False).astype(bool).sum()
                    ),
                    "matched_positive_count": int(
                        local["matched_positive"].astype(bool).sum()
                    ),
                    "mean_search_reward": float(
                        local["search_reward"].astype(float).mean()
                    ),
                    "top_decile_search_reward": _top_decile(local["search_reward"]),
                }
            )
    return output


def _write_runtime_views(
    runtime_root: Path,
    *,
    state: Mapping[str, Any],
    ledger: Sequence[Mapping[str, Any]],
    archive: engine.BehaviorArchive,
    pair_rows: Sequence[Mapping[str, Any]],
    metrics: Sequence[Mapping[str, Any]],
    rejected: Sequence[Mapping[str, Any]],
) -> None:
    engine._write_json(runtime_root / "work_state.json", dict(state))
    engine._write_parquet(runtime_root / "candidate_ledger.parquet", ledger)
    engine._write_parquet(runtime_root / "behavior_archive.parquet", archive.rows)
    engine._write_parquet(runtime_root / "paired_program_diagnostics.parquet", pair_rows)
    engine._write_parquet(runtime_root / "arm_checkpoint_metrics.parquet", metrics)
    frozen_config = engine._read_json(runtime_root / "frozen_contract.json")["config"]
    engine._write_parquet(
        runtime_root / "program_family_metrics.parquet",
        _program_family_metric_rows(
            ledger=ledger,
            pair_rows=pair_rows,
            config=frozen_config,
            adaptive_start_strict=int(state.get("adaptive_start_strict", 10_000)),
        ),
    )
    engine._write_parquet(runtime_root / "rejected_candidate_ledger.parquet", rejected)


def _write_checkpoint(
    runtime_root: Path,
    *,
    checkpoint_index: int,
    label: str | None = None,
    state: Mapping[str, Any],
    policies: Mapping[str, Any],
    ledger: Sequence[Mapping[str, Any]],
    archive: engine.BehaviorArchive,
    pair_rows: Sequence[Mapping[str, Any]],
    metrics: Sequence[Mapping[str, Any]],
    rejected: Sequence[Mapping[str, Any]],
    identities: Mapping[str, Any],
    discovery_diagnostic: Mapping[str, Any] | None = None,
) -> Path:
    root = runtime_root / "checkpoints"
    root.mkdir(parents=True, exist_ok=True)
    checkpoint_label = str(label or f"checkpoint_{checkpoint_index:03d}")
    target = root / checkpoint_label
    temporary = root / f".{checkpoint_label}.tmp-{os.getpid()}"
    if target.exists() or temporary.exists():
        raise FileExistsError("temporal program checkpoint already exists")
    temporary.mkdir(parents=True)
    state_payload = {
        **dict(state),
        "attempted_exact_ids": sorted(set(state["attempted_exact_ids"])),
        "completed_pair_ids": sorted(set(state["completed_pair_ids"])),
        "archive_duplicate_replacements": int(archive.duplicate_replacements),
        "policies": {
            key: engine._export_policy(policy) for key, policy in sorted(policies.items())
        },
    }
    engine._write_json(temporary / "state.json", state_payload)
    engine._write_parquet(temporary / "candidate_ledger.parquet", ledger)
    engine._write_parquet(temporary / "behavior_archive.parquet", archive.rows)
    engine._write_parquet(temporary / "paired_program_diagnostics.parquet", pair_rows)
    engine._write_parquet(temporary / "arm_checkpoint_metrics.parquet", metrics)
    engine._write_parquet(temporary / "rejected_candidate_ledger.parquet", rejected)
    if discovery_diagnostic is not None:
        engine._write_json(
            temporary / "discovery_diagnostics.json",
            dict(discovery_diagnostic),
        )
    files = [
        {
            "name": path.name,
            "bytes": path.stat().st_size,
            "sha256": _sha256_file(path),
        }
        for path in sorted(temporary.iterdir())
    ]
    manifest = {
        "schema_version": 1,
        "checkpoint": checkpoint_label,
        "checkpoint_index": int(checkpoint_index),
        "source_sha": state["source_sha"],
        "frozen_contract_sha256": state["frozen_contract_sha256"],
        "data_cache_identity": identities["raw_cache"],
        "compiler_identity": identities["compiler_identity"],
        "completed_ledger_row_count": len(ledger),
        "completed_pair_row_count": len(pair_rows),
        "completed_identity_sha256": _json_sha(
            [str(row["candidate_id"]) for row in ledger]
        ),
        "policy_state_sha256": _json_sha(state_payload["policies"]),
        "archive_state_sha256": archive.state_hash(),
        "state_sha256": _json_sha(state_payload),
        "receipt_count": sum(bool(row.get("receipt_json")) for row in ledger),
        "files": files,
        "atomic_write": "TEMP_DIRECTORY_THEN_OS_REPLACE",
        "restore_verified": False,
    }
    engine._write_json(temporary / "manifest.json", manifest)
    _load_checkpoint(
        temporary,
        registry=None,
        expected_source=str(state["source_sha"]),
        expected_frozen=str(state["frozen_contract_sha256"]),
        expected_identities=identities,
        verify_policy_restore=False,
    )
    manifest["restore_verified"] = True
    engine._write_json(temporary / "manifest.json", manifest)
    os.replace(temporary, target)
    return target


def _load_checkpoint(
    path: Path,
    *,
    registry: TypedExpressionRegistry | None,
    expected_source: str,
    expected_frozen: str,
    expected_identities: Mapping[str, Any],
    verify_policy_restore: bool = True,
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    list[dict[str, Any]],
    engine.BehaviorArchive,
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    manifest = engine._read_json(path / "manifest.json")
    if (
        manifest.get("source_sha") != expected_source
        or manifest.get("frozen_contract_sha256") != expected_frozen
        or manifest.get("data_cache_identity") != expected_identities["raw_cache"]
        or manifest.get("compiler_identity") != expected_identities["compiler_identity"]
    ):
        raise RuntimeError("temporal program checkpoint authority changed")
    for row in manifest["files"]:
        local = path / str(row["name"])
        if (
            not local.is_file()
            or local.stat().st_size != int(row["bytes"])
            or _sha256_file(local) != str(row["sha256"])
        ):
            raise RuntimeError("temporal program checkpoint file changed")
    state_payload = engine._read_json(path / "state.json")
    if _json_sha(state_payload) != manifest["state_sha256"]:
        raise RuntimeError("temporal program checkpoint state changed")
    policy_payloads = dict(state_payload.pop("policies"))
    duplicate_replacements = int(state_payload.pop("archive_duplicate_replacements"))
    if verify_policy_restore:
        if registry is None:
            raise ValueError("checkpoint policy restore requires registry")
        policies = {
            key: engine._restore_policy(registry, value)
            for key, value in policy_payloads.items()
        }
        if _json_sha(
            {key: engine._export_policy(value) for key, value in sorted(policies.items())}
        ) != manifest["policy_state_sha256"]:
            raise RuntimeError("temporal program policy restore changed")
    else:
        policies = policy_payloads
    ledger = pd.read_parquet(path / "candidate_ledger.parquet").to_dict("records")
    archive = engine.BehaviorArchive.from_rows(
        pd.read_parquet(path / "behavior_archive.parquet").to_dict("records")
    )
    archive.duplicate_replacements = duplicate_replacements
    pairs = pd.read_parquet(path / "paired_program_diagnostics.parquet").to_dict("records")
    metrics = pd.read_parquet(path / "arm_checkpoint_metrics.parquet").to_dict("records")
    rejected = pd.read_parquet(path / "rejected_candidate_ledger.parquet").to_dict("records")
    if (
        len(ledger) != int(manifest["completed_ledger_row_count"])
        or len(pairs) != int(manifest["completed_pair_row_count"])
        or _json_sha([str(row["candidate_id"]) for row in ledger])
        != manifest["completed_identity_sha256"]
        or archive.state_hash() != manifest["archive_state_sha256"]
    ):
        raise RuntimeError("temporal program checkpoint row identity changed")
    return state_payload, policies, ledger, archive, pairs, metrics, rejected


def _program_family(candidate: CandidateSpec) -> str:
    return str(candidate.generation_genes["program_spec"]["family_id"])


def _observe_candidate(
    *,
    candidate: CandidateSpec,
    evaluation: Mapping[str, Any],
    proposal: dict[str, Any],
    worker: Mapping[str, Any],
    archive: engine.BehaviorArchive,
    policy: Any | None,
    state: dict[str, Any],
    ledger: list[dict[str, Any]],
    checkpoint_index: int,
) -> None:
    _assert_terminal_market_open(state, action="candidate_observe_and_ledger_append")
    arm = str(proposal["arm"])
    completion = len(ledger) + 1
    local_counts = state["policy_local_family_counts"].setdefault(
        str(proposal["policy_key"]), {}
    )
    archive_row, new_family = archive.observe(
        candidate=candidate,
        evaluation=evaluation,
        arm=arm,
        seed=int(proposal["seed"]),
        completion_ordinal=completion,
        checkpoint_index=checkpoint_index,
    )
    family_id = str(archive_row["behavior_family_id"])
    local_counts[family_id] = int(local_counts.get(family_id, 0)) + 1
    proposal["new_policy_local_behavior_family_at_completion"] = local_counts[family_id] == 1
    proposal["policy_local_family_count_at_completion"] = local_counts[family_id]
    proposal["family_member_count_at_completion"] = int(archive.family_counts[family_id])
    policy_row = {
        **archive_row,
        "operation": proposal["operation"],
        "parent_ids": list(proposal["parent_ids"]),
        "policy_local_family_count_at_completion": local_counts[family_id],
        "block_robust_ordering": evaluation.get("block_robust_ordering"),
    }
    if policy is not None:
        engine._policy_observe(
            policy,
            candidate=candidate,
            reward=engine._search_ordering_reward(evaluation),
            archive_row=policy_row,
        )
    row = engine._ledger_row(
        candidate=candidate,
        evaluation=evaluation,
        proposal=proposal,
        archive_row=archive_row,
        new_family=new_family,
        state_hash_after=(
            str(proposal["policy_state_hash_after_proposal"])
            if policy is None or type(policy) is engine.MechanismRandomV2
            else policy.state_hash()
        ),
        checkpoint_index=checkpoint_index,
        completion_ordinal=completion,
        arm_completion_ordinal=int(state["arm_counters"][arm]["strict_evaluated"]) + 1,
        worker=worker,
        require_evidence_provenance=True,
    )
    row["program_family_id"] = _program_family(candidate)
    row["program_id"] = str(candidate.generation_genes["program_id"])
    row["representation"] = str(candidate.generation_genes["representation"])
    row["total_process_cpu_seconds"] = float(
        row["proposal_compile_cpu_seconds"] + row["pair_process_cpu_seconds"]
    )
    ledger.append(row)
    state["strict_evaluated"] = len(ledger)
    state["arm_counters"][arm]["strict_evaluated"] += 1
    state["arm_counters"][arm]["process_cpu_seconds"] += row[
        "total_process_cpu_seconds"
    ]


def _checkpoint_metrics(
    *,
    checkpoint_index: int,
    ledger: Sequence[Mapping[str, Any]],
    state: Mapping[str, Any],
) -> list[dict[str, Any]]:
    frame = pd.DataFrame(list(ledger))
    rows: list[dict[str, Any]] = []
    for arm in ("paired_static", *ARMS):
        local = frame.loc[frame["arm"].astype(str) == arm]
        if not len(local):
            continue
        counter = dict(state["arm_counters"][arm])
        rows.append(
            {
                "checkpoint_index": int(checkpoint_index),
                "cumulative_strict_count": len(frame),
                "arm": arm,
                "strict_evaluated_count": len(local),
                "generation_attempts": int(counter["generation_attempts"]),
                "exact_unique_rate": float(
                    counter["exact_unique"] / max(1, counter["generation_attempts"])
                ),
                "behavior_family_count": int(
                    local["behavior_family_id"].astype(str).nunique()
                ),
                "behavior_duplicate_rate": float(
                    1.0
                    - local["behavior_family_id"].astype(str).nunique() / len(local)
                ),
                "dual_axis_net_positive_count": int(
                    (
                        (local["left_incremental_net_mean"].astype(float) > 0.0)
                        & (local["right_incremental_net_mean"].astype(float) > 0.0)
                    ).sum()
                ),
                "matched_positive_count": int(local["matched_positive"].astype(bool).sum()),
                "replicated_2_of_3_count": int(
                    local["replicated_candidate"].fillna(False).astype(bool).sum()
                ),
                "mean_search_reward": float(local["search_reward"].astype(float).mean()),
                "top_decile_search_reward": _top_decile(local["search_reward"]),
                "process_cpu_seconds": float(counter["process_cpu_seconds"]),
                "strict_per_process_cpu_hour": float(
                    len(local) * 3600.0 / max(1.0e-12, counter["process_cpu_seconds"])
                ),
            }
        )
    return rows


def _later_policies(
    *,
    registry: TypedExpressionRegistry,
    config: Mapping[str, Any],
    catalog: Sequence[tuple[MechanismSpec, TemporalProgramSpec]],
    active_families: Sequence[str],
) -> dict[str, Any]:
    active = tuple(pair for pair in catalog if pair[1].family_id in set(active_families))
    inactive = tuple(pair for pair in catalog if pair[1].family_id not in set(active_families))
    seeds = tuple(int(value) for value in config["seed_authority"]["seeds"])
    output: dict[str, Any] = {}
    for seed in seeds:
        for arm in ARMS:
            output[f"{arm}|{seed}"] = _make_policy(
                arm=arm,
                seed=seed,
                registry=registry,
                config=config,
                catalog=active,
            )
        if inactive:
            output[f"temporal_program_random_diagnostic|{seed}"] = _make_policy(
                arm="temporal_program_random",
                seed=seed ^ 0xA5A5A5A5,
                registry=registry,
                config=config,
                catalog=inactive,
            )
    return output


def _restore_successor_policies(
    *,
    registry: TypedExpressionRegistry,
    config: Mapping[str, Any],
    catalog: Sequence[tuple[MechanismSpec, TemporalProgramSpec]],
    successor_context: Mapping[str, Any],
) -> dict[str, Any]:
    """Restore eight adaptive lanes and construct fresh Random control lanes."""

    policies = {
        key: engine._restore_policy(registry, value)
        for key, value in dict(
            successor_context["reconstructed_policy_bundle"]["policies"]
        ).items()
    }
    expected_adaptive = {
        f"{arm}|{seed}"
        for arm in ("temporal_program_cem", "temporal_program_evolution")
        for seed in ADAPTIVE_BROAD_SEEDS
    }
    if set(policies) != expected_adaptive:
        raise RuntimeError(
            "FAIL_CLOSED_BEFORE_MARKET_READ:successor_adaptive_policy_lane_identity"
        )
    active_catalog = tuple(
        pair
        for pair in catalog
        if pair[1].family_id in set(ADAPTIVE_BROAD_FAMILIES)
    )
    diagnostic_catalog = tuple(
        pair
        for pair in catalog
        if pair[1].family_id not in set(ADAPTIVE_BROAD_FAMILIES)
    )
    for seed in successor_context["fresh_random_lane_seeds"]:
        key = f"temporal_program_random|{int(seed)}"
        policies[key] = _make_policy(
            arm="temporal_program_random",
            seed=int(seed),
            registry=registry,
            config=config,
            catalog=active_catalog,
        )
        policies[f"temporal_program_random_diagnostic|{int(seed)}"] = _make_policy(
            arm="temporal_program_random",
            seed=int(seed) ^ 0xA5A5A5A5,
            registry=registry,
            config=config,
            catalog=diagnostic_catalog,
        )
    if len(policies) != 16:
        raise RuntimeError(
            "FAIL_CLOSED_BEFORE_MARKET_READ:successor_policy_lane_count"
        )
    return policies


def _stage0_policies(
    *,
    registry: TypedExpressionRegistry,
    config: Mapping[str, Any],
    catalog: Sequence[tuple[MechanismSpec, TemporalProgramSpec]],
) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for family in sorted({program.family_id for _, program in catalog}):
        local = tuple(pair for pair in catalog if pair[1].family_id == family)
        for seed in config["seed_authority"]["seeds"]:
            output[f"stage0|{family}|{int(seed)}"] = _make_policy(
                arm="temporal_program_random",
                seed=int(seed),
                registry=registry,
                config=config,
                catalog=local,
            )
    return output


def _stage0_lane_targets(config: Mapping[str, Any]) -> dict[str, int]:
    quota = int(config["stage_allocations"][0]["program_family_pairs_each"])
    seeds = tuple(int(value) for value in config["seed_authority"]["seeds"])
    quotient, remainder = divmod(quota, len(seeds))
    return {
        f"stage0|{family['family_id']}|{seed}": quotient + int(index < remainder)
        for family in config["program_families"]
        for index, seed in enumerate(seeds)
    }


def _stage0_checkpoint_lane_targets(
    config: Mapping[str, Any], checkpoint_index: int
) -> dict[str, int]:
    if not 0 <= int(checkpoint_index) < 5:
        raise ValueError("stage-0 checkpoint index is outside the frozen range")
    seeds = tuple(int(value) for value in config["seed_authority"]["seeds"])
    output: Counter[str] = Counter()
    start = int(checkpoint_index) * 250
    for family in config["program_families"]:
        family_id = str(family["family_id"])
        for family_ordinal in range(start, start + 250):
            output[f"stage0|{family_id}|{seeds[family_ordinal % len(seeds)]}"] += 1
    if sum(output.values()) != 1_000:
        raise AssertionError("stage-0 checkpoint pair allocation changed")
    return dict(output)


def _next_stage0_lane(
    *,
    ordered_lanes: Sequence[str],
    lane_targets: Mapping[str, int],
    lane_completed: Mapping[str, int],
    lane_pending: Mapping[str, int],
    cursor: int,
) -> tuple[str | None, int]:
    """Select one eligible lane and advance even when its proposal is rejected."""

    if not ordered_lanes:
        return None, 0
    next_cursor = int(cursor) % len(ordered_lanes)
    for _ in range(len(ordered_lanes)):
        key = str(ordered_lanes[next_cursor])
        next_cursor = (next_cursor + 1) % len(ordered_lanes)
        if int(lane_completed.get(key, 0)) + int(lane_pending.get(key, 0)) < int(
            lane_targets[key]
        ):
            return key, next_cursor
    return None, next_cursor


def _stage0_pair_task_capacity(workers: int) -> int:
    """Return concurrent pair tasks; each task already evaluates both representations."""

    if int(workers) <= 0:
        raise ValueError("stage-0 worker count must be positive")
    return int(workers)


def _later_checkpoint_targets(
    allocation: Mapping[str, int], config: Mapping[str, Any]
) -> dict[str, int]:
    seeds = tuple(int(value) for value in config["seed_authority"]["seeds"])
    output: dict[str, int] = {}
    for arm, count in allocation.items():
        quotient, remainder = divmod(int(count), len(seeds))
        for index, seed in enumerate(seeds):
            output[f"{arm}|{seed}"] = quotient + int(index < remainder)
    return output


def _random_policy_key_for_lane(
    policy_key: str,
    *,
    arm: str,
    seed_text: str,
    local_index: int,
    targeted_mode: bool,
    active_program_families: Sequence[str],
    catalog: Sequence[tuple[Any, Any]],
) -> str:
    if targeted_mode:
        return policy_key
    if (
        arm == ARMS[0]
        and active_program_families
        and any(
            pair[1].family_id not in set(active_program_families)
            for pair in catalog
        )
        and int(local_index) % 10 == 9
    ):
        return f"temporal_program_random_diagnostic|{seed_text}"
    return policy_key


def _write_status(
    runtime_root: Path,
    *,
    state: Mapping[str, Any],
    status: str,
    active_elapsed: float,
) -> None:
    strict_count = int(state["strict_evaluated"])
    engine._write_json(
        runtime_root / "producer_status.json",
        {
            "schema_version": 1,
            "status": status,
            "producer_pid": os.getpid(),
            "producer_source_sha": state["source_sha"],
            "heartbeat_utc": pd.Timestamp.now(tz="UTC").isoformat(),
            "checkpoint_index": int(state["next_checkpoint_index"]),
            "strict_evaluated": strict_count,
            "strict_maximum": int(state.get("authorized_strict_cap", 50_000)),
            "generation_attempts": int(state["generation_attempts"]),
            "active_wall_seconds": active_elapsed,
            "observed_strict_per_hour": strict_count * 3600.0 / max(active_elapsed, 1.0),
            "workers": int(state["workers"]),
            "worker_accounting": {
                "configured_worker_processes": int(state["workers"]),
                "configured_paired_task_capacity": _stage0_pair_task_capacity(
                    int(state["workers"])
                ),
                "strict_rows_per_successful_pair_task": 2,
                "configured_strict_row_capacity_per_paired_batch": 2
                * _stage0_pair_task_capacity(int(state["workers"])),
            },
            "active_program_families": list(state["active_program_families"]),
            "arm_states": dict(state["arm_states"]),
        },
    )


def _program_process_evidence_summary(runtime_root: Path) -> dict[str, int]:
    initializer_rows = [
        engine._read_json(path)
        for path in sorted(
            (runtime_root / "process_evidence").glob("*_initializer.json")
        )
    ]
    worker_pids = {
        int(row["worker_pid"])
        for row in initializer_rows
        if row.get("worker_pid") is not None
    }
    batch_rows = [
        engine._read_json(path)
        for path in sorted(
            (runtime_root / "process_evidence").glob("producer_batch_*.json")
        )
    ]
    submitted = [int(row.get("submitted_count", 0)) for row in batch_rows]
    return {
        "observed_worker_process_count": len(worker_pids),
        "observed_batch_count": len(batch_rows),
        "total_submitted_worker_task_count": sum(submitted),
        "maximum_submitted_worker_tasks_per_batch": max(submitted, default=0),
    }


def _program_process_evidence_errors(
    runtime_root: Path,
    *,
    expected_batch_count: int,
    configured_worker_processes: int | None = None,
) -> list[str]:
    errors: list[str] = []
    if expected_batch_count <= 0:
        return errors
    initializer_rows = [
        engine._read_json(path)
        for path in sorted(
            (runtime_root / "process_evidence").glob("*_initializer.json")
        )
    ]
    if not initializer_rows or any(
        row.get("stage") != "INITIALIZER_READY" for row in initializer_rows
    ):
        errors.append("worker_initializer_evidence_not_ready")
    if not _process_evidence_closed(runtime_root):
        errors.append("worker_process_evidence_not_closed")
    batch_paths = sorted(
        (runtime_root / "process_evidence").glob("producer_batch_*.json")
    )
    if len(batch_paths) != expected_batch_count:
        errors.append("producer_batch_evidence_count")
    submitted_counts: list[int] = []
    for index, path in enumerate(batch_paths):
        row = engine._read_json(path)
        submitted_counts.append(int(row.get("submitted_count", 0)))
        if (
            int(row.get("evaluation_batch_index", -1)) != index
            or row.get("stage") != "WORKER_RESULTS_RETURNED"
            or int(row.get("proposal_count", -1))
            != int(row.get("submitted_count", -2))
            or int(row.get("submitted_count", -1))
            != int(row.get("returned_count", -2))
        ):
            errors.append(f"producer_batch_evidence:{index}")
    if configured_worker_processes is not None:
        capacity = _stage0_pair_task_capacity(configured_worker_processes)
        maximum_submitted = max(submitted_counts, default=0)
        total_submitted = sum(submitted_counts)
        if maximum_submitted > capacity:
            errors.append("producer_batch_worker_capacity_exceeded")
        if total_submitted >= capacity and maximum_submitted < capacity:
            errors.append("producer_batch_worker_capacity_underfilled")
        observed_workers = len(
            {
                int(row["worker_pid"])
                for row in initializer_rows
                if row.get("worker_pid") is not None
            }
        )
        if observed_workers < maximum_submitted:
            errors.append("worker_initializer_count_below_submitted_capacity")
    return errors


def run(
    repo_root: Path,
    *,
    runtime_date: str,
    source_sha: str | None = None,
    execution_mode: str = "FRESH_SEQUENTIAL_PROGRAM",
    successor_artifact_root: Path | None = None,
    successor_policy_bundle: Path | None = None,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    base_config = engine._read_json(repo_root / CONFIG_PATH)
    validate_config(base_config)
    successor_mode = str(execution_mode) == SUCCESSOR_EXECUTION_MODE
    expansion_mode = str(execution_mode) == EXPANSION_EXECUTION_MODE
    targeted_mode = str(execution_mode) == TARGETED_EXECUTION_MODE
    fixed_development_mode = expansion_mode or targeted_mode
    targeted_diagnostic_baseline: dict[str, Any] | None = None
    targeted_parent_pool: dict[str, Any] | None = None
    if str(execution_mode) not in {
        "FRESH_SEQUENTIAL_PROGRAM",
        SUCCESSOR_EXECUTION_MODE,
        EXPANSION_EXECUTION_MODE,
        TARGETED_EXECUTION_MODE,
    }:
        raise ValueError("unknown temporal program execution mode")
    if successor_mode:
        if successor_artifact_root is None or successor_policy_bundle is None:
            raise RuntimeError(
                "FAIL_CLOSED_BEFORE_MARKET_READ:successor_source_paths_required"
            )
        config = _successor_effective_config(base_config)
        qualification_scope = {
            "strict_cap": 50_000,
            "stage0_only": False,
            "skip_stage0": True,
            "adaptive_start_strict": SUCCESSOR_PREFIX_BOUNDARY,
            "active_program_families": list(ADAPTIVE_BROAD_FAMILIES),
            "scope": SUCCESSOR_EXECUTION_MODE,
            "source_evidence_prefix": SUCCESSOR_PREFIX_BOUNDARY,
            "maximum_additional_strict": 20_000,
            "checkpoint_size": 5_000,
        }
        runtime_root = repo_root / f"runtime/{SUCCESSOR_CAMPAIGN}_{runtime_date}"
        successor_context = prepare_successor_execution(
            repo_root,
            artifact_root=successor_artifact_root,
            bundle_path=successor_policy_bundle,
            runtime_root=runtime_root,
        )
        receipt = dict(successor_context["authorization"])
        successor_authority_preflight = None
    elif expansion_mode:
        if successor_artifact_root is not None or successor_policy_bundle is not None:
            raise RuntimeError(
                "FAIL_CLOSED_BEFORE_MARKET_READ:expansion_successor_inputs_forbidden"
            )
        config = _expansion_effective_config(base_config)
        qualification_scope = {
            "strict_cap": 50_000,
            "stage0_only": False,
            "skip_stage0": True,
            "adaptive_start_strict": 0,
            "active_program_families": list(EXPANSION_PROGRAM_FAMILIES),
            "scope": EXPANSION_EXECUTION_MODE,
            "fixed_flow": True,
            "family_concentration_is_diagnostic_only": True,
        }
        runtime_root = repo_root / f"runtime/{EXPANSION_CAMPAIGN}_{runtime_date}"
        receipt = {}
        successor_context = None
        successor_authority_preflight = None
    elif targeted_mode:
        if successor_artifact_root is not None or successor_policy_bundle is not None:
            raise RuntimeError(
                "FAIL_CLOSED_BEFORE_MARKET_READ:targeted_successor_inputs_forbidden"
            )
        config = _targeted_effective_config(base_config)
        qualification_scope = {
            "strict_cap": 30_000,
            "stage0_only": False,
            "skip_stage0": True,
            "adaptive_start_strict": 0,
            "active_program_families": list(TARGETED_PROGRAM_FAMILIES),
            "scope": TARGETED_EXECUTION_MODE,
            "fixed_flow": True,
            "family_concentration_is_diagnostic_only": True,
            "saturation_boundary": 20_000,
        }
        runtime_root = repo_root / f"runtime/{TARGETED_CAMPAIGN}_{runtime_date}"
        receipt = {}
        successor_context = None
        successor_authority_preflight = None
    else:
        receipt = validate_receipt(
            repo_root, config=base_config, require_authorized=True
        )
        qualification_scope = _qualification_scope(receipt)
        config = _effective_config(base_config, receipt)
        runtime_root = repo_root / f"runtime/{CAMPAIGN}_{runtime_date}"
        successor_context = None
        successor_authority_preflight = None
    observed_sha = engine._git_sha(repo_root)
    source_sha = str(source_sha or observed_sha).lower()
    if source_sha != observed_sha:
        if successor_mode:
            raise SuccessorPreflightError(
                "FAIL_CLOSED_BEFORE_MARKET_READ:producer_sha_differs_from_checkout"
            )
        raise RuntimeError("temporal program producer SHA differs from checkout")
    if expansion_mode:
        receipt = validate_expansion_authorization(
            repo_root,
            expected_source_sha=source_sha,
        )
        if runtime_root.name != str(receipt.get("runtime_id") or ""):
            raise ExpansionPreflightError(
                "FAIL_CLOSED_BEFORE_MARKET_READ:runtime_identity_changed"
            )
    elif targeted_mode:
        receipt = validate_targeted_authorization(
            repo_root,
            expected_source_sha=source_sha,
        )
        if runtime_root.name != str(receipt.get("runtime_id") or ""):
            raise ExpansionPreflightError(
                "FAIL_CLOSED_BEFORE_MARKET_READ:targeted_runtime_identity_changed"
            )
        targeted_diagnostic_baseline = load_targeted_diagnostic_baseline(
            repo_root, receipt
        )
        targeted_parent_pool = build_frozen_target_parent_pool(
            repo_root, targeted_diagnostic_baseline
        )
    report_name = (
        "CRYPTO_TEMPORAL_30K_TO_50K_SUCCESSOR_V1"
        if successor_mode
        else (
            "CRYPTO_TEMPORAL_LARGE_DEVELOPMENT_EXPANSION_V1"
            if expansion_mode
            else (
                "CRYPTO_TEMPORAL_TARGETED_P1_P4_BASIN_DEEPENING_V1"
                if targeted_mode
                else REPORT_PREFIX
            )
        )
    )
    report_path = repo_root / f"reports/{report_name}_{runtime_date}.md"
    if not engine._source_tree_clean_for_run(
        repo_root, allowed_paths=(runtime_root, report_path)
    ):
        if successor_mode:
            raise SuccessorPreflightError(
                "FAIL_CLOSED_BEFORE_MARKET_READ:producer_tree_not_clean"
            )
        raise RuntimeError("temporal program producer tree is not clean")
    if runtime_root.is_dir():
        if successor_mode or fixed_development_mode:
            raise RuntimeError("FAIL_CLOSED_BEFORE_MARKET_READ:non_fresh_output_root")
        prior_checkpoints = sorted(
            (runtime_root / "checkpoints").glob("checkpoint_[0-9][0-9][0-9]")
        )
        if prior_checkpoints:
            prior_state_path = prior_checkpoints[-1] / "state.json"
            if prior_state_path.is_file():
                prior_state = engine._read_json(prior_state_path)
                _assert_terminal_market_open(
                    prior_state,
                    action="resume_before_market_or_worker_initialization",
                )
    if successor_mode:
        assert successor_context is not None
        run_authorization = dict(receipt.get("run_authorization") or {})
        successor_authority_preflight = require_real_experiment_authority(
            repo_root,
            evidence_to_add=str(receipt.get("evidence_to_add") or ""),
            decision_to_change=str(receipt.get("decision_to_change") or ""),
            economic_receipt_required=False,
            receipt_bound_non_formal_authorization={
                "decision_id": str(run_authorization.get("decision_id") or ""),
                "authority": str(run_authorization.get("authority") or ""),
                "scope": str(run_authorization.get("scope") or ""),
                "receipt_path": SUCCESSOR_AUTHORIZATION_PATH,
                "receipt_sha256": _json_sha(receipt),
                "run_authorized": True,
            },
        )
        runtime_root.mkdir(parents=True)
        engine._write_json(
            runtime_root / "successor_launch_claim.json",
            {
                "schema_version": 1,
                "status": "ONE_TIME_SUCCESSOR_LAUNCH_CLAIMED",
                "execution_mode": SUCCESSOR_EXECUTION_MODE,
                "authorization_sha256": successor_context[
                    "authorization_sha256"
                ],
                "producer_source_sha": source_sha,
                "runtime_id": runtime_root.name,
                "market_arrays_read_at_claim": 0,
                "candidate_evaluations_at_claim": 0,
                "sealed_reads": 0,
            },
        )
    elif targeted_mode:
        run_authorization = dict(receipt.get("run_authorization") or {})
        successor_authority_preflight = require_real_experiment_authority(
            repo_root,
            evidence_to_add=str(receipt.get("evidence_to_add") or ""),
            decision_to_change=str(receipt.get("decision_to_change") or ""),
            economic_receipt_required=False,
            receipt_bound_non_formal_authorization={
                "decision_id": str(run_authorization.get("decision_id") or ""),
                "authority": str(run_authorization.get("authority") or ""),
                "scope": str(run_authorization.get("scope") or ""),
                "receipt_path": TARGETED_AUTHORIZATION_PATH,
                "receipt_sha256": _json_sha(receipt),
                "run_authorized": True,
            },
        )
        runtime_root.mkdir(parents=True)
        engine._write_json(
            runtime_root / "targeted_deepening_launch_claim.json",
            {
                "schema_version": 1,
                "status": "ONE_TIME_TARGETED_DEEPENING_LAUNCH_CLAIMED",
                "execution_mode": TARGETED_EXECUTION_MODE,
                "authorization_sha256": receipt["authorization_sha256"],
                "producer_source_sha": source_sha,
                "runtime_id": runtime_root.name,
                "market_arrays_read_at_claim": 0,
                "candidate_evaluations_at_claim": 0,
                "sealed_reads": 0,
            },
        )
        assert targeted_parent_pool is not None
        engine._write_json(
            runtime_root / "targeted_frozen_parent_pool.json",
            targeted_parent_pool,
        )
    elif expansion_mode:
        run_authorization = dict(receipt.get("run_authorization") or {})
        successor_authority_preflight = require_real_experiment_authority(
            repo_root,
            evidence_to_add=str(receipt.get("evidence_to_add") or ""),
            decision_to_change=str(receipt.get("decision_to_change") or ""),
            economic_receipt_required=False,
            receipt_bound_non_formal_authorization={
                "decision_id": str(run_authorization.get("decision_id") or ""),
                "authority": str(run_authorization.get("authority") or ""),
                "scope": str(run_authorization.get("scope") or ""),
                "receipt_path": EXPANSION_AUTHORIZATION_PATH,
                "receipt_sha256": _json_sha(receipt),
                "run_authorized": True,
            },
        )
        runtime_root.mkdir(parents=True)
        engine._write_json(
            runtime_root / "development_expansion_launch_claim.json",
            {
                "schema_version": 1,
                "status": "ONE_TIME_DEVELOPMENT_EXPANSION_LAUNCH_CLAIMED",
                "execution_mode": EXPANSION_EXECUTION_MODE,
                "authorization_sha256": receipt["authorization_sha256"],
                "producer_source_sha": source_sha,
                "runtime_id": runtime_root.name,
                "market_arrays_read_at_claim": 0,
                "candidate_evaluations_at_claim": 0,
                "sealed_reads": 0,
            },
        )
    economic = resolve_search_economic_receipt(
        repo_root, str(config["source_authorities"]["economic_receipt_template"])
    )
    if successor_mode or fixed_development_mode:
        authority = dict(receipt["authority_identity"])
        economic_components = dict(economic.get("component_sha256") or {})
        observed_economic = {
            "economic_receipt_sha256": str(economic.get("receipt_sha256") or ""),
            "target_contract_sha256": str(
                economic_components.get("target_contract") or ""
            ),
            "target_execution_sha256": str(
                economic_components.get("target_execution") or ""
            ),
            "portfolio_mapping_and_cost_sha256": str(
                economic_components.get("portfolio_mapping_and_cost") or ""
            ),
            "optimizer_reward_and_matched_attribution_sha256": str(
                economic_components.get("optimizer_reward_and_matched_attribution")
                or ""
            ),
        }
        if any(
            observed_economic[key] != str(authority[key])
            for key in observed_economic
        ):
            raise (
                SuccessorPreflightError
                if successor_mode
                else ExpansionPreflightError
            )(
                "FAIL_CLOSED_BEFORE_MARKET_READ:current_economic_authority_changed"
            )
        premarket_catalog_sha = program_catalog_payload(
            compile_temporal_program_catalog(config)
        )["catalog_sha256"]
        if premarket_catalog_sha != str(authority["program_catalog_sha256"]):
            raise (
                SuccessorPreflightError
                if successor_mode
                else ExpansionPreflightError
            )(
                "FAIL_CLOSED_BEFORE_MARKET_READ:current_program_catalog_changed"
            )
    train = dict(economic["evidence_partition"]["train"])
    validate_pair_evaluation_request(
        block_start=str(train["start"]),
        block_end=str(train["end_exclusive"]),
        block_role=BLOCK_ROLE,
        economic_receipt=economic,
        include_paired_diagnostic_paths=True,
    )
    store, contracts, behavior, identities, _ = engine._load_v14_inputs(
        repo_root, behavior_window=train
    )
    if len(contracts) != 115:
        raise RuntimeError("temporal program carrier contract changed")
    registry = TypedExpressionRegistry(contracts, **_limits(config))
    catalog = compile_temporal_program_catalog(config)
    catalog_payload = program_catalog_payload(catalog)
    expansion_diagnostic_baseline = (
        load_diagnostic_baseline(repo_root, receipt) if expansion_mode else None
    )
    if targeted_mode and targeted_diagnostic_baseline is None:
        raise RuntimeError(
            "FAIL_CLOSED_BEFORE_MARKET_READ:targeted_baseline_not_frozen"
        )
    block_config = engine._read_json(
        repo_root / str(config["source_authorities"]["development_blocks_config"])
    )
    block_contract = dict(block_config["block_robust_contract"])
    compiler_identity = engine._compiler_binding(repo_root)
    identities = {**identities, "compiler_identity": compiler_identity}
    successor_preflight_evidence = None
    if successor_mode:
        assert successor_context is not None
        restored_evidence = dict(successor_context["restored_prefix"])
        restored_archive = restored_evidence.pop("archive")
        restored_evidence.pop("ledger")
        successor_preflight_evidence = {
            "status": successor_context["status"],
            "authorization_sha256": successor_context["authorization_sha256"],
            "successor_receipt_sha256": successor_context[
                "successor_receipt_sha256"
            ],
            "reconstructed_policy_bundle_sha256": receipt[
                "reconstructed_policy_bundle_sha256"
            ],
            "source_artifact_identity_sha256": receipt[
                "source_artifact_identity_sha256"
            ],
            "state_restoration_sha256": restored_evidence[
                "state_restoration_sha256"
            ],
            "prefix_archive_state_sha256": restored_archive.state_hash(),
            "prefix_ledger_count": SUCCESSOR_PREFIX_BOUNDARY,
            "attempted_exact_id_count": len(
                restored_evidence["attempted_exact_ids"]
            ),
            "policy_local_lane_count": len(
                restored_evidence["policy_local_family_counts"]
            ),
            "suffix_contribution": restored_evidence["suffix_contribution"],
            "fresh_random_lane_seeds": successor_context[
                "fresh_random_lane_seeds"
            ],
            "market_arrays_read": 0,
            "sealed_reads": 0,
        }
    frozen = {
        "schema_version": 1,
        "experiment_id": config["experiment_id"],
        "execution_mode": str(execution_mode),
        "source_sha": source_sha,
        "config": config,
        "receipt_sha256": (
            receipt["authorization_sha256"]
            if successor_mode or fixed_development_mode
            else receipt["receipt_sha256"]
        ),
        "qualification_scope": qualification_scope,
        "economic_receipt": economic,
        "input_identities": identities,
        "behavior_contract_sha256": _json_sha(behavior),
        "compiler_identity": compiler_identity,
        "program_catalog_sha256": catalog_payload["catalog_sha256"],
        "block_robust_contract": block_contract,
        "expression_registry_limits": _limits(config),
        "successor_preflight": successor_preflight_evidence,
        "successor_current_authority_preflight": successor_authority_preflight,
        "targeted_parent_pool_sha256": (
            str(targeted_parent_pool["target_parent_pool_sha256"])
            if targeted_mode and targeted_parent_pool is not None
            else None
        ),
        "targeted_parent_source_ledger_sha256": (
            str(targeted_parent_pool["source_ledger_sha256"])
            if targeted_mode and targeted_parent_pool is not None
            else None
        ),
        "sealed_reads": 0,
    }
    frozen_hash = _json_sha(frozen)
    frozen = {**frozen, "frozen_contract_sha256": frozen_hash}
    if runtime_root.exists():
        if successor_mode:
            claim = engine._read_json(runtime_root / "successor_launch_claim.json")
            if (
                claim.get("authorization_sha256")
                != receipt.get("authorization_sha256")
                or claim.get("producer_source_sha") != source_sha
                or (runtime_root / "frozen_contract.json").exists()
            ):
                raise RuntimeError(
                    "FAIL_CLOSED_BEFORE_MARKET_READ:successor_launch_claim_changed"
                )
        elif expansion_mode:
            claim = engine._read_json(
                runtime_root / "development_expansion_launch_claim.json"
            )
            if (
                claim.get("authorization_sha256")
                != receipt.get("authorization_sha256")
                or claim.get("producer_source_sha") != source_sha
                or (runtime_root / "frozen_contract.json").exists()
            ):
                raise RuntimeError(
                    "FAIL_CLOSED_BEFORE_MARKET_READ:development_expansion_launch_claim_changed"
                )
        elif targeted_mode:
            claim = engine._read_json(
                runtime_root / "targeted_deepening_launch_claim.json"
            )
            if (
                claim.get("authorization_sha256")
                != receipt.get("authorization_sha256")
                or claim.get("producer_source_sha") != source_sha
                or (runtime_root / "frozen_contract.json").exists()
            ):
                raise RuntimeError(
                    "FAIL_CLOSED_BEFORE_MARKET_READ:targeted_deepening_launch_claim_changed"
                )
        else:
            if engine._read_json(runtime_root / "frozen_contract.json") != frozen:
                raise RuntimeError("temporal program runtime contract changed")
            if (runtime_root / "final_decision.json").is_file():
                raise FileExistsError("temporal program campaign already completed")
    else:
        runtime_root.mkdir(parents=True)
    if successor_mode or fixed_development_mode or not (runtime_root / "frozen_contract.json").exists():
        engine._write_json(runtime_root / "frozen_contract.json", frozen)
        engine._write_json(runtime_root / "program_catalog.json", catalog_payload)
        engine._write_json(runtime_root / "search_authority_binding_receipt.json", receipt)
        engine._write_json(
            runtime_root / "embedded_preflight.json",
            (
                successor_preflight_evidence
                if successor_mode
                else (
                    successor_authority_preflight
                    if fixed_development_mode
                    else source_smoke(repo_root)
                )
            ),
        )
        if successor_mode:
            assert successor_context is not None
            engine._write_json(
                runtime_root / "successor_authorization_snapshot.json", receipt
            )
            engine._write_json(
                runtime_root / "prefix_state_restoration_receipt.json",
                successor_preflight_evidence,
            )
        elif expansion_mode:
            engine._write_json(
                runtime_root / "development_expansion_authorization_snapshot.json",
                receipt,
            )
            engine._write_json(
                runtime_root / "development_expansion_diagnostic_baseline.json",
                expansion_diagnostic_baseline,
            )
        elif targeted_mode:
            engine._write_json(
                runtime_root / "targeted_deepening_authorization_snapshot.json",
                receipt,
            )
            engine._write_json(
                runtime_root / "targeted_deepening_diagnostic_baseline.json",
                targeted_diagnostic_baseline,
            )

    if any(
        (runtime_root / "checkpoints" / label).is_dir()
        for label in ("checkpoint_budget_exhausted", "checkpoint_run_invalid")
    ):
        raise RuntimeError("terminal runtime cannot be resumed")
    checkpoints = sorted((runtime_root / "checkpoints").glob("checkpoint_[0-9][0-9][0-9]"))
    if checkpoints:
        if successor_mode or fixed_development_mode:
            raise RuntimeError("FAIL_CLOSED_BEFORE_MARKET_READ:one_run_resume_forbidden")
        state, policies, ledger, archive, pair_rows, metrics, rejected = _load_checkpoint(
            checkpoints[-1],
            registry=registry,
            expected_source=source_sha,
            expected_frozen=frozen_hash,
            expected_identities=identities,
        )
    else:
        if successor_mode:
            assert successor_context is not None
            restored = successor_context["restored_prefix"]
            state = _new_state(source_sha, frozen_hash, config)
            state.update(
                {
                    "next_checkpoint_index": 15,
                    "successor_next_checkpoint_index": 0,
                    "strict_evaluated": SUCCESSOR_PREFIX_BOUNDARY,
                    "source_evidence_prefix": SUCCESSOR_PREFIX_BOUNDARY,
                    "additional_strict_evaluated": 0,
                    "cumulative_valid_strict": SUCCESSOR_PREFIX_BOUNDARY,
                    "skip_stage0": True,
                    "adaptive_start_strict": SUCCESSOR_PREFIX_BOUNDARY,
                    "active_program_families": list(ADAPTIVE_BROAD_FAMILIES),
                    "attempted_exact_ids": list(restored["attempted_exact_ids"]),
                    "completed_pair_ids": list(restored["completed_pair_ids"]),
                    "policy_local_family_counts": dict(
                        restored["policy_local_family_counts"]
                    ),
                    "prefix_state_restoration_sha256": restored[
                        "state_restoration_sha256"
                    ],
                    "invalid_suffix_contribution": dict(
                        restored["suffix_contribution"]
                    ),
                    "execution_mode": SUCCESSOR_EXECUTION_MODE,
                }
            )
            ledger = list(restored["ledger"])
            archive = restored["archive"]
            pair_rows = []
            metrics = []
            rejected = []
            policies = _restore_successor_policies(
                registry=registry,
                config=config,
                catalog=catalog,
                successor_context=successor_context,
            )
        else:
            state = _new_state(source_sha, frozen_hash, config)
            state["skip_stage0"] = bool(qualification_scope.get("skip_stage0"))
            state["adaptive_start_strict"] = int(
                qualification_scope.get("adaptive_start_strict", 10_000)
            )
            state["active_program_families"] = list(
                qualification_scope.get("active_program_families", ())
            )
            policies = (
                _later_policies(
                    registry=registry,
                    config=config,
                    catalog=catalog,
                    active_families=state["active_program_families"],
                )
                if state["skip_stage0"]
                else _stage0_policies(registry=registry, config=config, catalog=catalog)
            )
            if targeted_mode:
                if targeted_parent_pool is None:
                    raise RuntimeError(
                        "FAIL_CLOSED_BEFORE_MARKET_READ:targeted_parent_pool_missing"
                    )
                for key, policy in policies.items():
                    if key.startswith("temporal_program_evolution|"):
                        if not isinstance(policy, engine.MechanismEvolutionV2):
                            raise RuntimeError(
                                "FAIL_CLOSED_BEFORE_MARKET_READ:targeted_evolution_policy_changed"
                            )
                        policy.configure_targeted_parent_pool(targeted_parent_pool)
            ledger = []
            archive = engine.BehaviorArchive()
            pair_rows = []
            metrics = []
            rejected = []
    state["authorized_strict_cap"] = int(qualification_scope["strict_cap"])
    for key, default in (
        ("workers_initial", int(config["search_budget"]["workers_default"])),
        ("stage0_lane_cursor", 0),
        ("evaluation_batch_index", 0),
        ("returned_pair_results", 0),
        ("system_error_count", 0),
        ("skip_stage0", bool(qualification_scope.get("skip_stage0"))),
        (
            "adaptive_start_strict",
            int(qualification_scope.get("adaptive_start_strict", 10_000)),
        ),
    ):
        state.setdefault(key, default)
    attempted = set(str(value) for value in state["attempted_exact_ids"])
    completed_pairs = set(str(value) for value in state["completed_pair_ids"])
    budget = dict(config["search_budget"])
    prior_elapsed = float(state["wall_elapsed_seconds"])
    started = time.perf_counter()

    def elapsed() -> float:
        return prior_elapsed + time.perf_counter() - started

    def enforce_budget(extra_attempts: int = 0) -> None:
        if int(state["generation_attempts"]) + extra_attempts > int(
            budget["raw_generation_attempts_maximum"]
        ):
            raise ProgramBudgetExhausted("RAW_GENERATION_ATTEMPT_LIMIT")
        if elapsed() >= float(budget["wall_time_seconds_maximum"]):
            raise ProgramBudgetExhausted("ACTIVE_WALL_TIME_LIMIT")

    def proposal_attempt_reservation(arm: str) -> int:
        policy_arm = (
            "temporal_program_random"
            if arm in {"paired_static", "temporal_program_random_diagnostic"}
            else str(arm)
        )
        return int(config["policy_parameters"][policy_arm]["duplicate_resample_limit"]) + 1

    cache_root = repo_root / str(identities["raw_cache"]["root"])

    def make_executor(workers: int) -> concurrent.futures.ProcessPoolExecutor:
        return concurrent.futures.ProcessPoolExecutor(
            max_workers=workers,
            initializer=engine._worker_initialize,
            initargs=(
                str(cache_root),
                engine._contracts_payload(contracts),
                behavior,
                str(train["start"]),
                str(train["end_exclusive"]),
                BLOCK_ROLE,
                economic,
                True,
                block_contract,
                str(runtime_root / "process_evidence"),
                _limits(config),
            ),
        )

    def persist_batch_stage(
        *,
        proposals: Sequence[Mapping[str, Any]],
        checkpoint_index: int,
        stage: str,
        submitted_count: int,
        returned_count: int,
    ) -> None:
        engine._write_proposal_batch_process_evidence(
            evidence_root=runtime_root / "process_evidence",
            stage=stage,
            source_sha=source_sha,
            frozen_contract_sha256=frozen_hash,
            checkpoint_index=checkpoint_index,
            batch_index=int(state["evaluation_batch_index"]),
            generation_attempts=int(state["generation_attempts"]),
            attempted_exact_id_count=len(attempted),
            proposals=proposals,
            submitted_count=submitted_count,
            returned_count=returned_count,
        )

    executor: concurrent.futures.ProcessPoolExecutor | None = None
    terminal_reason: str | None = None
    latest_discovery_diagnostic: dict[str, Any] | None = None
    try:
        executor = make_executor(int(state["workers"]))
        _write_status(runtime_root, state=state, status="RUNNING", active_elapsed=elapsed())
        checkpoint_count_cap = (
            19
            if successor_mode
            else int(qualification_scope["strict_cap"])
            // int(budget["checkpoint_size"])
        )
        for checkpoint_index in range(
            int(state["next_checkpoint_index"]), checkpoint_count_cap
        ):
            _assert_terminal_market_open(state, action="next_checkpoint")
            checkpoint_start = len(ledger)
            checkpoint_target = checkpoint_start + (
                5_000 if successor_mode else 2_000
            )
            if not bool(state.get("skip_stage0")) and checkpoint_index < 5:
                lane_targets = _stage0_checkpoint_lane_targets(
                    config, checkpoint_index
                )
                lane_completed = Counter(
                    str(row["policy_key"])
                    for row in ledger
                    if int(row["checkpoint_index"]) == checkpoint_index
                    and str(row["representation"]) == "TEMPORAL_PROGRAM"
                )
                ordered_lanes = sorted(lane_targets)
                pair_target = 1_000
                pair_completed_in_checkpoint = len(ledger[checkpoint_start:]) // 2
                while pair_completed_in_checkpoint < pair_target:
                    batch: list[dict[str, Any]] = []
                    lane_pending: Counter[str] = Counter()
                    while len(batch) < _stage0_pair_task_capacity(
                        int(state["workers"])
                    ):
                        key, next_cursor = _next_stage0_lane(
                            ordered_lanes=ordered_lanes,
                            lane_targets=lane_targets,
                            lane_completed=lane_completed,
                            lane_pending=lane_pending,
                            cursor=int(state["stage0_lane_cursor"]),
                        )
                        state["stage0_lane_cursor"] = next_cursor
                        if key is None:
                            break
                        enforce_budget(proposal_attempt_reservation(ARMS[0]))
                        policy = policies[key]
                        proposal_cpu = time.process_time()
                        try:
                            temporal, metadata = _call_with_terminal_invariant(
                                state,
                                "candidate_generation",
                                policy.propose,
                            )
                            static = static_counterpart(registry, temporal)
                        except (ValueError, RuntimeError) as failure:
                            failed_raw_attempts = int(
                                getattr(failure, "raw_attempts", 1)
                            )
                            state["generation_attempts"] += failed_raw_attempts
                            state["arm_counters"][ARMS[0]][
                                "generation_attempts"
                            ] += failed_raw_attempts
                            rejected.append(
                                {
                                    "checkpoint_index": checkpoint_index,
                                    "policy_key": key,
                                    "status": "PROPOSAL_REJECT",
                                    "raw_attempts": failed_raw_attempts,
                                    "error": type(failure).__name__ + ":" + str(failure),
                                }
                            )
                            continue
                        raw_attempts = int(metadata["raw_attempts"])
                        state["generation_attempts"] += raw_attempts
                        state["compile_valid"] += int(metadata.get("compile_valid_attempts", raw_attempts))
                        state["arm_counters"][ARMS[0]]["generation_attempts"] += raw_attempts
                        state["arm_counters"][ARMS[0]]["compile_valid"] += int(metadata.get("compile_valid_attempts", raw_attempts))
                        if (
                            temporal.candidate_id in attempted
                            or static.candidate_id in attempted
                            or not engine._candidate_rebuild_verified(registry, temporal, {})
                            or not engine._candidate_rebuild_verified(registry, static, {})
                        ):
                            attempted.update((temporal.candidate_id, static.candidate_id))
                            rejected.append(
                                {
                                    "checkpoint_index": checkpoint_index,
                                    "policy_key": key,
                                    "status": "EXACT_OR_REPLAY_REJECT",
                                    "raw_attempts": raw_attempts,
                                    "temporal_candidate_id": temporal.candidate_id,
                                    "static_candidate_id": static.candidate_id,
                                }
                            )
                            continue
                        attempted.update((temporal.candidate_id, static.candidate_id))
                        pair_id = _json_sha([static.candidate_id, temporal.candidate_id])
                        if pair_id in completed_pairs:
                            rejected.append(
                                {
                                    "checkpoint_index": checkpoint_index,
                                    "policy_key": key,
                                    "status": "COMPLETED_PAIR_DUPLICATE",
                                    "raw_attempts": raw_attempts,
                                    "paired_program_id": pair_id,
                                }
                            )
                            continue
                        _, family, seed_text = key.split("|", 2)
                        lane_pending[key] += 1
                        batch.append(
                            {
                                "policy_key": key,
                                "arm": ARMS[0],
                                "seed": int(seed_text),
                                "program_family_id": family,
                                "program_id": str(temporal.generation_genes["program_id"]),
                                "paired_program_id": pair_id,
                                "static": static,
                                "temporal": temporal,
                                "metadata": metadata,
                                "generation_attempt_ordinal": int(state["generation_attempts"]),
                                "proposal_cpu_seconds": time.process_time() - proposal_cpu,
                            }
                        )
                    if not batch:
                        continue
                    assert executor is not None
                    persist_batch_stage(
                        proposals=batch,
                        checkpoint_index=checkpoint_index,
                        stage="PROPOSAL_BATCH_READY_BEFORE_WORKER_SUBMIT",
                        submitted_count=0,
                        returned_count=0,
                    )
                    futures: dict[concurrent.futures.Future[dict[str, Any]], dict[str, Any]] = {}
                    try:
                        for item in batch:
                            futures[
                                _call_with_terminal_invariant(
                                    state,
                                    "worker_submission",
                                    executor.submit,
                                    _worker_program_pair,
                                    {
                                        "paired_program_id": item["paired_program_id"],
                                        "static": item["static"].to_dict(),
                                        "temporal": item["temporal"].to_dict(),
                                    },
                                )
                            ] = item
                    except BaseException:
                        persist_batch_stage(
                            proposals=batch,
                            checkpoint_index=checkpoint_index,
                            stage="WORKER_SUBMISSION_FAILED",
                            submitted_count=len(futures),
                            returned_count=0,
                        )
                        raise
                    persist_batch_stage(
                        proposals=batch,
                        checkpoint_index=checkpoint_index,
                        stage="WORKERS_SUBMITTED",
                        submitted_count=len(futures),
                        returned_count=0,
                    )
                    results = [(futures[future], future.result()) for future in concurrent.futures.as_completed(futures)]
                    persist_batch_stage(
                        proposals=batch,
                        checkpoint_index=checkpoint_index,
                        stage="WORKER_RESULTS_RETURNED",
                        submitted_count=len(futures),
                        returned_count=len(results),
                    )
                    state["evaluation_batch_index"] += 1
                    state["returned_pair_results"] += len(results)
                    system_failures = [
                        (item, result)
                        for item, result in results
                        if bool(result.get("system_error"))
                    ]
                    if system_failures:
                        state["system_error_count"] += len(system_failures)
                        for item, result in system_failures:
                            rejected.append(
                                {
                                    "checkpoint_index": checkpoint_index,
                                    "policy_key": item["policy_key"],
                                    "status": "SYSTEM_ERROR",
                                    "error": result["error"],
                                    "paired_program_id": item["paired_program_id"],
                                    **_rejected_worker_runtime_fields(result),
                                }
                            )
                        raise ProgramRunInvalid(
                            "WORKER_SYSTEM_ERROR:" + str(system_failures[0][1]["error"])
                        )
                    if any(result["memory_error"] for _, result in results):
                        if int(state["workers"]) == int(budget["workers_default"]):
                            executor.shutdown(wait=True)
                            state["workers"] = int(budget["workers_memory_fallback"])
                            state["memory_fallback_used"] = True
                            executor = make_executor(int(state["workers"]))
                            retry_items = [item for item, result in results if result["memory_error"]]
                            retry = {
                                _call_with_terminal_invariant(
                                    state,
                                    "worker_retry_submission",
                                    executor.submit,
                                    _worker_program_pair,
                                    {
                                        "paired_program_id": item["paired_program_id"],
                                        "static": item["static"].to_dict(),
                                        "temporal": item["temporal"].to_dict(),
                                    },
                                ): item
                                for item in retry_items
                            }
                            retry_by_id = {
                                item["paired_program_id"]: (item, future.result())
                                for future, item in retry.items()
                            }
                            results = [
                                retry_by_id.get(item["paired_program_id"], (item, result))
                                for item, result in results
                            ]
                        if any(result["memory_error"] for _, result in results):
                            raise ProgramBudgetExhausted("MEMORY_ERROR_AT_8_WORKERS")
                    for item, result in sorted(results, key=lambda value: value[0]["paired_program_id"]):
                        if result["status"] != "PAIR_EVALUATED":
                            rejected.append(
                                {
                                    "checkpoint_index": checkpoint_index,
                                    "policy_key": item["policy_key"],
                                    "status": result["status"],
                                    "error": result["error"],
                                    "paired_program_id": item["paired_program_id"],
                                    **_rejected_worker_runtime_fields(result),
                                }
                            )
                            continue
                        lane_completed[item["policy_key"]] += 1
                        completed_pairs.add(item["paired_program_id"])
                        common_worker = {
                            **result,
                            "process_cpu_seconds": float(result["process_cpu_seconds"]) / 2.0,
                        }
                        for representation, arm in (
                            ("static", "paired_static"),
                            ("temporal", ARMS[0]),
                        ):
                            candidate = item[representation]
                            metadata = item["metadata"]
                            proposal = {
                                "arm": arm,
                                "seed": item["seed"],
                                "policy_key": item["policy_key"],
                                "checkpoint_completion_ordinal": len(ledger) - checkpoint_start + 1,
                                "generation_attempt_ordinal": int(state["generation_attempts"]),
                                "operation": (
                                    "PAIRED_STATIC_COUNTERPART"
                                    if representation == "static"
                                    else metadata["operation"]
                                ),
                                "parent_ids": [],
                                "receipt": None,
                                "receipt_verified": None,
                                "expression_hash_verified": True,
                                "policy_state_hash_before": metadata["policy_state_hash_before"],
                                "policy_state_hash_after_proposal": metadata["policy_state_hash_after_proposal"],
                                "proposal_cpu_seconds": item["proposal_cpu_seconds"] / 2.0,
                            }
                            _observe_candidate(
                                candidate=candidate,
                                evaluation=result[representation],
                                proposal=proposal,
                                worker=common_worker,
                                archive=archive,
                                policy=None,
                                state=state,
                                ledger=ledger,
                                checkpoint_index=checkpoint_index,
                            )
                            state["arm_counters"][arm]["exact_unique"] += 1
                            if representation == "static":
                                state["arm_counters"][arm]["generation_attempts"] += 1
                                state["arm_counters"][arm]["compile_valid"] += 1
                        pair_rows.append(
                            _pair_diagnostic(
                                pair=item,
                                static=result["static"],
                                temporal=result["temporal"],
                                common=result["common_support"],
                            )
                        )
                        pair_completed_in_checkpoint += 1
                    if (
                        not ledger
                        and int(state["returned_pair_results"])
                        >= int(config["runtime_safety"]["zero_strict_returned_pair_maximum"])
                    ):
                        raise ProgramRunInvalid(
                            "ZERO_STRICT_LIVENESS_LIMIT_AFTER_RETURNED_PAIRS"
                        )
                    _write_status(runtime_root, state=state, status="RUNNING", active_elapsed=elapsed())
            else:
                allocation = (
                    successor_allocation(state["arm_states"])
                    if successor_mode
                    else _checkpoint_allocation(state, checkpoint_index, config)
                )
                targets = (
                    successor_lane_targets(
                        allocation,
                        fresh_random_seeds=successor_context[
                            "fresh_random_lane_seeds"
                        ],
                        adaptive_seeds=config["seed_authority"]["seeds"],
                    )
                    if successor_mode
                    else _later_checkpoint_targets(allocation, config)
                )
                completed_by_lane = Counter(
                    str(row["policy_key"])
                    for row in ledger
                    if int(row["checkpoint_index"]) == checkpoint_index
                )
                lane_order = sorted(targets)
                cursor = 0
                while len(ledger) < checkpoint_target:
                    enforce_budget()
                    proposals: list[dict[str, Any]] = []
                    scans = 0
                    while len(proposals) < int(state["workers"]):
                        if all(completed_by_lane[key] + sum(row["policy_key"] == key for row in proposals) >= target for key, target in targets.items()):
                            break
                        key = lane_order[cursor % len(lane_order)]
                        cursor += 1
                        if completed_by_lane[key] + sum(row["policy_key"] == key for row in proposals) >= targets[key]:
                            scans += 1
                            if scans > len(lane_order) * 2:
                                break
                            continue
                        scans = 0
                        policy_key = key
                        arm, seed_text = key.rsplit("|", 1)
                        local_index = completed_by_lane[key] + sum(
                            row["policy_key"] == key for row in proposals
                        )
                        actual_policy_key = _random_policy_key_for_lane(
                            policy_key,
                            arm=arm,
                            seed_text=seed_text,
                            local_index=local_index,
                            targeted_mode=targeted_mode,
                            active_program_families=state["active_program_families"],
                            catalog=catalog,
                        )
                        policy = policies[actual_policy_key]
                        enforce_budget(proposal_attempt_reservation(arm))
                        proposal_cpu = time.process_time()
                        try:
                            candidate, metadata = _call_with_terminal_invariant(
                                state,
                                "candidate_generation",
                                engine._policy_propose,
                                policy,
                                archive,
                            )
                        except (ValueError, RuntimeError) as failure:
                            failed_raw_attempts = int(
                                getattr(failure, "raw_attempts", 1)
                            )
                            state["generation_attempts"] += failed_raw_attempts
                            state["arm_counters"][arm][
                                "generation_attempts"
                            ] += failed_raw_attempts
                            rejected.append(
                                {
                                    "checkpoint_index": checkpoint_index,
                                    "policy_key": actual_policy_key,
                                    "status": "PROPOSAL_REJECT",
                                    "raw_attempts": failed_raw_attempts,
                                    "error": type(failure).__name__ + ":" + str(failure),
                                }
                            )
                            continue
                        raw_attempts = int(metadata["raw_attempts"])
                        state["generation_attempts"] += raw_attempts
                        state["compile_valid"] += int(metadata.get("compile_valid_attempts", raw_attempts))
                        state["arm_counters"][arm]["generation_attempts"] += raw_attempts
                        state["arm_counters"][arm]["compile_valid"] += int(metadata.get("compile_valid_attempts", raw_attempts))
                        if candidate.candidate_id in attempted or not engine._candidate_rebuild_verified(registry, candidate, {}):
                            attempted.add(candidate.candidate_id)
                            rejected.append(
                                {
                                    "checkpoint_index": checkpoint_index,
                                    "policy_key": actual_policy_key,
                                    "status": "EXACT_OR_REPLAY_REJECT",
                                    "raw_attempts": raw_attempts,
                                    "candidate_id": candidate.candidate_id,
                                }
                            )
                            continue
                        attempted.add(candidate.candidate_id)
                        proposals.append(
                            {
                                "policy_key": policy_key,
                                "actual_policy_key": actual_policy_key,
                                "arm": arm,
                                "seed": int(seed_text),
                                "candidate": candidate,
                                "metadata": metadata,
                                "generation_attempt_ordinal": int(state["generation_attempts"]),
                                "proposal_cpu_seconds": time.process_time() - proposal_cpu,
                            }
                        )
                    if not proposals:
                        continue
                    assert executor is not None
                    persist_batch_stage(
                        proposals=proposals,
                        checkpoint_index=checkpoint_index,
                        stage="PROPOSAL_BATCH_READY_BEFORE_WORKER_SUBMIT",
                        submitted_count=0,
                        returned_count=0,
                    )
                    futures: dict[concurrent.futures.Future[dict[str, Any]], dict[str, Any]] = {}
                    try:
                        for row in proposals:
                            futures[
                                _call_with_terminal_invariant(
                                    state,
                                    "worker_submission",
                                    executor.submit,
                                    engine._worker_evaluate,
                                    row["candidate"].to_dict(),
                                )
                            ] = row
                    except BaseException:
                        persist_batch_stage(
                            proposals=proposals,
                            checkpoint_index=checkpoint_index,
                            stage="WORKER_SUBMISSION_FAILED",
                            submitted_count=len(futures),
                            returned_count=0,
                        )
                        raise
                    persist_batch_stage(
                        proposals=proposals,
                        checkpoint_index=checkpoint_index,
                        stage="WORKERS_SUBMITTED",
                        submitted_count=len(futures),
                        returned_count=0,
                    )
                    results = [(futures[future], future.result()) for future in concurrent.futures.as_completed(futures)]
                    persist_batch_stage(
                        proposals=proposals,
                        checkpoint_index=checkpoint_index,
                        stage="WORKER_RESULTS_RETURNED",
                        submitted_count=len(futures),
                        returned_count=len(results),
                    )
                    state["evaluation_batch_index"] += 1
                    system_failures = [
                        (row, result)
                        for row, result in results
                        if bool(result.get("system_error"))
                    ]
                    if system_failures:
                        state["system_error_count"] += len(system_failures)
                        for row, result in system_failures:
                            rejected.append(
                                {
                                    "checkpoint_index": checkpoint_index,
                                    "policy_key": row["actual_policy_key"],
                                    "status": "SYSTEM_ERROR",
                                    "error": result["error"],
                                    "candidate_id": row["candidate"].candidate_id,
                                }
                            )
                        raise ProgramRunInvalid(
                            "WORKER_SYSTEM_ERROR:" + str(system_failures[0][1]["error"])
                        )
                    if any(result["memory_error"] for _, result in results):
                        if int(state["workers"]) == int(budget["workers_default"]):
                            executor.shutdown(wait=True)
                            state["workers"] = int(budget["workers_memory_fallback"])
                            state["memory_fallback_used"] = True
                            executor = make_executor(int(state["workers"]))
                            retry_rows = [row for row, result in results if result["memory_error"]]
                            retry = {
                                _call_with_terminal_invariant(
                                    state,
                                    "worker_retry_submission",
                                    executor.submit,
                                    engine._worker_evaluate,
                                    row["candidate"].to_dict(),
                                ): row
                                for row in retry_rows
                            }
                            retry_by_id = {
                                row["candidate"].candidate_id: (row, future.result())
                                for future, row in retry.items()
                            }
                            results = [
                                retry_by_id.get(row["candidate"].candidate_id, (row, result))
                                for row, result in results
                            ]
                        if any(result["memory_error"] for _, result in results):
                            raise ProgramBudgetExhausted("MEMORY_ERROR_AT_8_WORKERS")
                    for row, worker in sorted(results, key=lambda value: value[0]["candidate"].candidate_id):
                        if worker["evaluation"] is None:
                            rejected.append(
                                {
                                    "checkpoint_index": checkpoint_index,
                                    "policy_key": row["actual_policy_key"],
                                    "status": "PAIR_REJECTED",
                                    "error": worker["error"],
                                    "candidate_id": row["candidate"].candidate_id,
                                }
                            )
                            continue
                        metadata = row["metadata"]
                        proposal = {
                            "arm": row["arm"],
                            "seed": row["seed"],
                            "policy_key": row["policy_key"],
                            "checkpoint_completion_ordinal": len(ledger) - checkpoint_start + 1,
                            "generation_attempt_ordinal": int(state["generation_attempts"]),
                            "operation": metadata["operation"],
                            "parent_ids": metadata["parent_ids"],
                            "receipt": metadata.get("receipt"),
                            "receipt_verified": metadata.get("receipt_verified"),
                            "expression_hash_verified": True,
                            "policy_state_hash_before": metadata["policy_state_hash_before"],
                            "policy_state_hash_after_proposal": metadata.get("policy_state_hash_after_proposal", ""),
                            "proposal_cpu_seconds": row["proposal_cpu_seconds"],
                        }
                        _observe_candidate(
                            candidate=row["candidate"],
                            evaluation=worker["evaluation"],
                            proposal=proposal,
                            worker=worker,
                            archive=archive,
                            policy=policies[row["actual_policy_key"]],
                            state=state,
                            ledger=ledger,
                            checkpoint_index=checkpoint_index,
                        )
                        state["arm_counters"][row["arm"]]["exact_unique"] += 1
                        completed_by_lane[row["policy_key"]] += 1
                    _write_status(runtime_root, state=state, status="RUNNING", active_elapsed=elapsed())

            if len(ledger) != checkpoint_target:
                raise RuntimeError("temporal program checkpoint strict count changed")
            checkpoint_rows = [row for row in ledger if int(row["checkpoint_index"]) == checkpoint_index]
            for seed in config["seed_authority"]["seeds"]:
                key = f"{ARMS[1]}|{int(seed)}"
                if key in policies:
                    local = [row for row in checkpoint_rows if row["arm"] == ARMS[1] and int(row["seed"]) == int(seed)]
                    if local:
                        _call_with_terminal_invariant(
                            state,
                            "policy_update",
                            policies[key].update,
                            local,
                        )
            metrics.extend(
                _checkpoint_metrics(checkpoint_index=checkpoint_index, ledger=ledger, state=state)
            )
            state["next_checkpoint_index"] = checkpoint_index + 1
            state["attempted_exact_ids"] = sorted(attempted)
            state["completed_pair_ids"] = sorted(completed_pairs)
            state["wall_elapsed_seconds"] = elapsed()
            strict_boundary = len(ledger)
            if targeted_mode:
                latest_discovery_diagnostic = targeted_diagnostics(
                    ledger,
                    baseline=targeted_diagnostic_baseline or {},
                    strict_boundary=strict_boundary,
                )
                engine._write_json(
                    runtime_root / "basin_diagnostics_latest.json",
                    latest_discovery_diagnostic,
                )
                engine._write_json(
                    runtime_root
                    / f"basin_diagnostics_checkpoint_{checkpoint_index:03d}.json",
                    latest_discovery_diagnostic,
                )
                if strict_boundary in TARGETED_DECISION_BOUNDARIES:
                    engine._write_json(
                        runtime_root
                        / f"basin_diagnostics_boundary_{strict_boundary:06d}.json",
                        latest_discovery_diagnostic,
                    )
            if successor_mode:
                budget_state = successor_budget_state(strict_boundary)
                state.update(budget_state)
                base_decision = adaptive_gate(
                    ledger,
                    state=state,
                    strict_boundary=strict_boundary,
                    config=config,
                    tranche_size=5_000,
                )
                decision = successor_checkpoint_decision(base_decision)
                additional_boundary = int(
                    budget_state["additional_strict_evaluated"]
                )
                engine._write_json(
                    runtime_root
                    / f"successor_decision_additional_{additional_boundary:06d}.json",
                    decision,
                )
                state["arm_states"] = dict(decision["arm_states_after"])
                state["successor_next_checkpoint_index"] = (
                    int(state.get("successor_next_checkpoint_index", 0)) + 1
                )
                if decision["status"] == "STOP_ECONOMIC_FUTILITY":
                    terminal_reason = "STOP_ECONOMIC_FUTILITY"
                elif decision["status"] == "STOP_INVALID":
                    terminal_reason = "ENGINE_RUN_INVALID:SUCCESSOR_GATE_STOP_INVALID"
                elif bool(budget_state["mechanical_stop_required"]):
                    terminal_reason = "SUCCESSOR_ADDITIONAL_BUDGET_COMPLETE"
            elif targeted_mode:
                if strict_boundary in TARGETED_DECISION_BOUNDARIES:
                    checkpoint_10000 = (
                        engine._read_json(
                            runtime_root / "basin_diagnostics_boundary_010000.json"
                        )
                        if strict_boundary == 20_000
                        else None
                    )
                    decision = targeted_checkpoint_decision(
                        strict_boundary,
                        latest_discovery_diagnostic or {},
                        checkpoint_10000=checkpoint_10000,
                    )
                    engine._write_json(
                        runtime_root
                        / f"continuation_decision_{strict_boundary:06d}.json",
                        decision,
                    )
                    if (
                        decision["status"]
                        == "STOP_TARGETED_DEEPENING_SATURATED_AT_20000"
                    ):
                        terminal_reason = (
                            "TARGETED_DEEPENING_SATURATION_REACHED_20000"
                        )
                if strict_boundary == int(qualification_scope["strict_cap"]):
                    terminal_reason = "TARGETED_DEEPENING_STRICT_CAP_REACHED"
            elif expansion_mode:
                if strict_boundary in EXPANSION_DECISION_BOUNDARIES:
                    decision = fixed_flow_decision(strict_boundary)
                    engine._write_json(
                        runtime_root
                        / f"continuation_decision_{strict_boundary:06d}.json",
                        decision,
                    )
                if strict_boundary == int(qualification_scope["strict_cap"]):
                    terminal_reason = "FIXED_DEVELOPMENT_STRICT_CAP_REACHED"
            elif not bool(state.get("skip_stage0")) and checkpoint_index == 4:
                decision = stage0_family_decisions(pair_rows, config)
                engine._write_json(runtime_root / "continuation_decision_010000.json", decision)
                if decision["status"] != "CONTINUE":
                    terminal_reason = decision["status"]
                else:
                    state["active_program_families"] = list(decision["continuing_families"])
                    if bool(qualification_scope["stage0_only"]):
                        terminal_reason = "STAGE0_QUALIFICATION_CAP_REACHED"
                    else:
                        policies = _later_policies(
                            registry=registry,
                            config=config,
                            catalog=catalog,
                            active_families=state["active_program_families"],
                        )
            elif (
                strict_boundary > int(state.get("adaptive_start_strict", 10_000))
                and strict_boundary
                in {
                    int(state.get("adaptive_start_strict", 10_000)) + 10_000,
                    int(state.get("adaptive_start_strict", 10_000)) + 20_000,
                    int(state.get("adaptive_start_strict", 10_000)) + 30_000,
                    int(state.get("adaptive_start_strict", 10_000)) + 40_000,
                }
                and strict_boundary < int(qualification_scope["strict_cap"])
            ):
                boundary = strict_boundary
                decision = adaptive_gate(
                    ledger,
                    state=state,
                    strict_boundary=boundary,
                    config=config,
                )
                engine._write_json(runtime_root / f"continuation_decision_{boundary:06d}.json", decision)
                state["arm_states"] = dict(decision["arm_states_after"])
                if decision["status"] != "CONTINUE":
                    terminal_reason = decision["status"]
            if fixed_development_mode:
                observed_rate = len(ledger) * 3600.0 / max(elapsed(), 1.0)
                if checkpoint_index == 0 and observed_rate < float(
                    budget["minimum_strict_per_hour_after_first_checkpoint"]
                ):
                    terminal_reason = "ENGINE_BUDGET_EXHAUSTED:THROUGHPUT_FLOOR"
                if expansion_mode:
                    process_cpu_seconds = sum(
                        float(row.get("proposal_compile_cpu_seconds") or row.get("proposal_cpu_seconds") or 0.0)
                        + float(row.get("pair_process_cpu_seconds") or row.get("process_cpu_seconds") or 0.0)
                        for row in ledger
                    )
                    latest_discovery_diagnostic = discovery_diagnostics(
                        ledger,
                        baseline=expansion_diagnostic_baseline or {},
                        strict_boundary=strict_boundary,
                        process_cpu_seconds=process_cpu_seconds,
                    )
                    engine._write_json(
                        runtime_root / "cluster_diagnostics_latest.json",
                        latest_discovery_diagnostic,
                    )
                    engine._write_json(
                        runtime_root
                        / f"cluster_diagnostics_checkpoint_{checkpoint_index:03d}.json",
                        latest_discovery_diagnostic,
                    )
            if terminal_reason is not None:
                _seal_terminal_decision(
                    state,
                    reason=terminal_reason,
                    strict_boundary=strict_boundary,
                )
            _write_runtime_views(
                runtime_root,
                state=state,
                ledger=ledger,
                archive=archive,
                pair_rows=pair_rows,
                metrics=metrics,
                rejected=rejected,
            )
            _write_checkpoint(
                runtime_root,
                checkpoint_index=checkpoint_index,
                state=state,
                policies=policies,
                ledger=ledger,
                archive=archive,
                pair_rows=pair_rows,
                metrics=metrics,
                rejected=rejected,
                identities=identities,
                discovery_diagnostic=latest_discovery_diagnostic,
            )
            if not successor_mode and not fixed_development_mode:
                observed_rate = len(ledger) * 3600.0 / max(elapsed(), 1.0)
                qualification_terminal_reason = _checkpoint_qualification_terminal_reason(
                    checkpoint_index=checkpoint_index,
                    qualification_scope=qualification_scope,
                    observed_strict_per_hour=observed_rate,
                    minimum_strict_per_hour=float(
                        budget["minimum_strict_per_hour_after_first_checkpoint"]
                    ),
                )
                terminal_reason = _merge_checkpoint_terminal_reason(
                    terminal_reason,
                    qualification_terminal_reason,
                )
            _write_status(runtime_root, state=state, status="RUNNING", active_elapsed=elapsed())
            if terminal_reason:
                break
    except ProgramBudgetExhausted as failure:
        terminal_reason = "ENGINE_BUDGET_EXHAUSTED:" + str(failure)
    except ProgramRunInvalid as failure:
        terminal_reason = "ENGINE_RUN_INVALID:" + str(failure)
    except Exception as failure:
        terminal_reason = (
            "ENGINE_RUN_INVALID:UNEXPECTED_"
            + type(failure).__name__
            + ":"
            + str(failure)
        )
    finally:
        if executor is not None:
            executor.shutdown(wait=True, cancel_futures=False)

    process_evidence_errors = _program_process_evidence_errors(
        runtime_root,
        expected_batch_count=int(state["evaluation_batch_index"]),
        configured_worker_processes=int(state["workers_initial"]),
    )
    process_evidence_summary = _program_process_evidence_summary(runtime_root)
    if process_evidence_errors:
        terminal_reason = "ENGINE_RUN_INVALID:PROCESS_EVIDENCE:" + ",".join(
            process_evidence_errors
        )

    state["attempted_exact_ids"] = sorted(attempted)
    state["completed_pair_ids"] = sorted(completed_pairs)
    state["wall_elapsed_seconds"] = elapsed()
    _write_runtime_views(
        runtime_root,
        state=state,
        ledger=ledger,
        archive=archive,
        pair_rows=pair_rows,
        metrics=metrics,
        rejected=rejected,
    )
    budget_checkpoint_written = False
    run_invalid_checkpoint_written = False
    if (
        terminal_reason
        and terminal_reason.startswith("ENGINE_BUDGET_EXHAUSTED")
        and (int(state["generation_attempts"]) > 0 or len(ledger) > 0)
        and not (runtime_root / "checkpoints/checkpoint_budget_exhausted").exists()
    ):
        _write_checkpoint(
            runtime_root,
            checkpoint_index=int(state["next_checkpoint_index"]),
            label="checkpoint_budget_exhausted",
            state=state,
            policies=policies,
            ledger=ledger,
            archive=archive,
            pair_rows=pair_rows,
            metrics=metrics,
            rejected=rejected,
            identities=identities,
        )
        budget_checkpoint_written = True
    if (
        terminal_reason
        and terminal_reason.startswith("ENGINE_RUN_INVALID")
        and (int(state["generation_attempts"]) > 0 or int(state["evaluation_batch_index"]) > 0)
        and not (runtime_root / "checkpoints/checkpoint_run_invalid").exists()
    ):
        _write_checkpoint(
            runtime_root,
            checkpoint_index=int(state["next_checkpoint_index"]),
            label="checkpoint_run_invalid",
            state=state,
            policies=policies,
            ledger=ledger,
            archive=archive,
            pair_rows=pair_rows,
            metrics=metrics,
            rejected=rejected,
            identities=identities,
        )
        run_invalid_checkpoint_written = True
    strict_count = len(ledger)
    matched = [row for row in ledger if bool(row["matched_positive"])]
    matched_families = {str(row["behavior_family_id"]) for row in matched}
    contributing = {str(row["program_family_id"]) for row in matched}
    if terminal_reason and terminal_reason.startswith("ENGINE_BUDGET_EXHAUSTED"):
        status = "ENGINE_BUDGET_EXHAUSTED"
    elif terminal_reason and terminal_reason.startswith("ENGINE_RUN_INVALID"):
        status = "ENGINE_RUN_INVALID"
    elif successor_mode and terminal_reason == "STOP_INVALID":
        status = "ENGINE_RUN_INVALID"
    elif successor_mode and terminal_reason == "STOP_ECONOMIC_FUTILITY":
        status = "SUCCESSOR_STOPPED_ECONOMIC_FUTILITY"
    elif successor_mode and terminal_reason == "SUCCESSOR_ADDITIONAL_BUDGET_COMPLETE":
        status = "SUCCESSOR_DEVELOPMENT_BUDGET_COMPLETE"
    elif successor_mode:
        status = "SUCCESSOR_DEVELOPMENT_STOPPED"
    elif expansion_mode and terminal_reason == "FIXED_DEVELOPMENT_STRICT_CAP_REACHED":
        status = "DEVELOPMENT_EXPANSION_BUDGET_COMPLETE"
    elif targeted_mode and terminal_reason in {
        "TARGETED_DEEPENING_STRICT_CAP_REACHED",
        "TARGETED_DEEPENING_SATURATION_REACHED_20000",
    }:
        status = "TARGETED_DEEPENING_BUDGET_COMPLETE"
    elif terminal_reason == "CHECKPOINT_ONLY_QUALIFICATION_CAP_REACHED":
        status = "CHECKPOINT_ONLY_QUALIFICATION_COMPLETE"
    elif strict_count == 10_000 and not state["active_program_families"]:
        status = "TEMPORAL_PROGRAM_SPACE_NOT_SUPPORTED"
    elif len(matched_families) >= 2 and len(contributing) >= 2:
        status = "TEMPORAL_PROGRAM_SPACE_SUPPORTED_FOR_FUTURE_VALIDATION"
    elif state["active_program_families"]:
        status = "LOCAL_TEMPORAL_PROGRAM_LINE_IDENTIFIED"
    else:
        status = "TEMPORAL_PROGRAM_SPACE_NOT_SUPPORTED"
    final = {
        "schema_version": 1,
        "execution_mode": str(execution_mode),
        "status": status,
        "terminal_reason": terminal_reason,
        "qualification_scope": qualification_scope,
        "adaptive_stage_started": strict_count
        > int(state.get("adaptive_start_strict", 10_000)),
        "producer_source_sha": source_sha,
        "frozen_contract_sha256": frozen_hash,
        "strict_evaluated_count": strict_count,
        "generation_attempts": int(state["generation_attempts"]),
        "checkpoint_count": (
            int(state.get("successor_next_checkpoint_index", 0))
            if successor_mode
            else int(state["next_checkpoint_index"])
        )
        + int(budget_checkpoint_written)
        + int(run_invalid_checkpoint_written),
        "completed_full_checkpoint_count": (
            int(state.get("successor_next_checkpoint_index", 0))
            if successor_mode
            else int(state["next_checkpoint_index"])
        ),
        "budget_checkpoint_written": budget_checkpoint_written,
        "run_invalid_checkpoint_written": run_invalid_checkpoint_written,
        "process_evidence_errors": process_evidence_errors,
        "evaluation_batch_count": int(state["evaluation_batch_index"]),
        "system_error_count": int(state["system_error_count"]),
        "active_wall_seconds": elapsed(),
        "workers_final": int(state["workers"]),
        "worker_accounting": {
            "configured_worker_processes_initial": int(state["workers_initial"]),
            "configured_worker_processes_final": int(state["workers"]),
            "configured_paired_task_capacity_initial": _stage0_pair_task_capacity(
                int(state["workers_initial"])
            ),
            "configured_paired_task_capacity_final": _stage0_pair_task_capacity(
                int(state["workers"])
            ),
            "strict_rows_per_successful_pair_task": 2,
            **process_evidence_summary,
        },
        "memory_fallback_used": bool(state["memory_fallback_used"]),
        "behavior_family_count": len(archive.champion_by_family),
        "matched_positive_count": len(matched),
        "matched_positive_behavior_family_count": len(matched_families),
        "matched_positive_program_family_count": len(contributing),
        "active_program_families": list(state["active_program_families"]),
        "arm_states": dict(state["arm_states"]),
        "source_evidence_prefix": (
            SUCCESSOR_PREFIX_BOUNDARY if successor_mode else None
        ),
        "source_invalid_suffix_start": (
            SUCCESSOR_PREFIX_BOUNDARY + 1 if successor_mode else None
        ),
        "additional_strict_evaluated": (
            strict_count - SUCCESSOR_PREFIX_BOUNDARY if successor_mode else None
        ),
        "cumulative_valid_strict": strict_count if successor_mode else None,
        "invalid_source_suffix_contribution": (
            dict(state.get("invalid_suffix_contribution") or {})
            if successor_mode
            else None
        ),
        "successor_authorization_sha256": (
            receipt.get("authorization_sha256") if successor_mode else None
        ),
        "development_expansion_authorization_sha256": (
            receipt.get("authorization_sha256") if expansion_mode else None
        ),
        "development_expansion_diagnostics": (
            latest_discovery_diagnostic if expansion_mode else None
        ),
        "targeted_deepening_authorization_sha256": (
            receipt.get("authorization_sha256") if targeted_mode else None
        ),
        "targeted_deepening_diagnostics": (
            latest_discovery_diagnostic if targeted_mode else None
        ),
        "fresh_random_control_identity": (
            FRESH_RANDOM_IDENTITY if successor_mode else None
        ),
        "sealed_reads": 0,
        "validation": False,
        "oos": False,
        "promotion": False,
        "automatic_next_run_started": False,
        "parameters_changed": bool(targeted_mode),
        "seed_changed": bool(fixed_development_mode),
        "seed_tuned": False,
        "rescue_rerun_started": False,
        "research_conclusion_forbidden": status in {
            "ENGINE_RUN_INVALID",
            "CHECKPOINT_ONLY_QUALIFICATION_COMPLETE",
        },
        **_valid_prefix_fields(
            state,
            status=status,
            strict_count=strict_count,
        ),
    }
    engine._write_json(runtime_root / "final_decision.json", final)
    manifest_paths = [
        "frozen_contract.json",
        "embedded_preflight.json",
        "program_catalog.json",
        "search_authority_binding_receipt.json",
        "work_state.json",
        "candidate_ledger.parquet",
        "behavior_archive.parquet",
        "paired_program_diagnostics.parquet",
        "program_family_metrics.parquet",
        "arm_checkpoint_metrics.parquet",
        "rejected_candidate_ledger.parquet",
        "final_decision.json",
    ]
    if successor_mode:
        manifest_paths.extend(
            [
                "successor_launch_claim.json",
                "successor_authorization_snapshot.json",
                "prefix_state_restoration_receipt.json",
            ]
        )
    elif expansion_mode:
        manifest_paths.extend(
            [
                "development_expansion_launch_claim.json",
                "development_expansion_authorization_snapshot.json",
                "development_expansion_diagnostic_baseline.json",
                "cluster_diagnostics_latest.json",
            ]
        )
        manifest_paths.extend(
            path.relative_to(runtime_root).as_posix()
            for path in sorted(
                runtime_root.glob("cluster_diagnostics_checkpoint_*.json")
            )
        )
    elif targeted_mode:
        manifest_paths.extend(
            [
                "targeted_deepening_launch_claim.json",
                "targeted_frozen_parent_pool.json",
                "targeted_deepening_authorization_snapshot.json",
                "targeted_deepening_diagnostic_baseline.json",
                "basin_diagnostics_latest.json",
            ]
        )
        manifest_paths.extend(
            path.relative_to(runtime_root).as_posix()
            for path in sorted(
                runtime_root.glob("basin_diagnostics_checkpoint_*.json")
            )
        )
        manifest_paths.extend(
            path.relative_to(runtime_root).as_posix()
            for path in sorted(
                runtime_root.glob("basin_diagnostics_boundary_*.json")
            )
        )
    manifest_paths.extend(
        path.relative_to(runtime_root).as_posix()
        for path in sorted(runtime_root.glob("continuation_decision_*.json"))
    )
    manifest_paths.extend(
        path.relative_to(runtime_root).as_posix()
        for path in sorted(
            runtime_root.glob("successor_decision_additional_*.json")
        )
    )
    manifest_paths.extend(
        path.relative_to(runtime_root).as_posix()
        for path in sorted((runtime_root / "checkpoints").glob("*/manifest.json"))
    )
    run_manifest = {
        "schema_version": 1,
        "producer_source_sha": source_sha,
        "frozen_contract_sha256": frozen_hash,
        "files": [
            {
                "path": value,
                "bytes": (runtime_root / value).stat().st_size,
                "sha256": _sha256_file(runtime_root / value),
            }
            for value in manifest_paths
        ],
    }
    run_manifest["bundle_sha256"] = _json_sha(run_manifest["files"])
    engine._write_json(runtime_root / "run_manifest.json", run_manifest)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    if targeted_mode:
        diagnostics = latest_discovery_diagnostic or {}
        economic = dict(diagnostics.get("economic_cluster_summary") or {})
        thresholds = dict(economic.get("thresholds") or {})
        depth = dict(diagnostics.get("basin_realization_depth") or {})
        next_decision = targeted_final_next_decision(
            diagnostics,
            system_valid=(
                status == "TARGETED_DEEPENING_BUDGET_COMPLETE"
                and terminal_reason
                in {
                    "TARGETED_DEEPENING_STRICT_CAP_REACHED",
                    "TARGETED_DEEPENING_SATURATION_REACHED_20000",
                }
            ),
        )
        report_lines = [
            "# TARGETED_DEEPENING_VALIDITY",
            f"- status: `{status}`",
            f"- strict/raw attempts: `{strict_count}` / `{state['generation_attempts']}`",
            f"- terminal reason: `{terminal_reason}`",
            "- allocation: `Random/CEM/Evolution = 20/20/60`",
            "- active program families: `P1/P4`; P2/P3 paused for this run",
            "- Evolution operation mix: `parameter/mechanism/crossover = 60/10/30`",
            "- validation/OOS/sealed reads: `0/0/0`",
            "- independent checker: `PENDING`",
            "",
            "# REAL_ECONOMIC_CLUSTER_RESULT",
            f"- matched-positive rows / behavior families: `{diagnostics.get('matched_positive_rows', 0)}` / `{diagnostics.get('matched_positive_behavior_families', 0)}`",
            f"- similarity 0.95/0.90/0.85 clusters: `{dict(thresholds.get('0.95') or {}).get('economic_cluster_count', 0)}` / `{dict(thresholds.get('0.90') or {}).get('economic_cluster_count', 0)}` / `{dict(thresholds.get('0.85') or {}).get('economic_cluster_count', 0)}`",
            f"- effective rank: `{economic.get('economic_effective_rank', 0.0)}`",
            f"- PCA dimensions 50/80/90: `{economic.get('pca_dimensions_50', 0)}` / `{economic.get('pca_dimensions_80', 0)}` / `{economic.get('pca_dimensions_90', 0)}`",
            f"- 0.90 largest/top3 cluster share: `{dict(thresholds.get('0.90') or {}).get('largest_cluster_share', 0.0)}` / `{dict(thresholds.get('0.90') or {}).get('top3_cluster_share', 0.0)}`",
            "",
            "# BASIN_REALIZATION_DEPTH",
            f"- mapped-weight basins >=2 / >=3: `{depth.get('mapped_weight_realizations_ge_2', 0)}` / `{depth.get('mapped_weight_realizations_ge_3', 0)}`",
            f"- turnover/raw-field/asset-selection basins >=2: `{depth.get('turnover_realizations_ge_2', 0)}` / `{depth.get('raw_field_realizations_ge_2', 0)}` / `{depth.get('asset_selection_realizations_ge_2', 0)}`",
            f"- singleton basins: `{depth.get('singleton_basin_count', 0)}`",
            f"- high-quality basins deepened / new concrete realizations: `{depth.get('high_quality_basins_deepened', 0)}` / `{depth.get('new_high_quality_concrete_realizations', 0)}`",
            "- full PnL/weight vectors: `NOT_AVAILABLE`; no historical market reevaluation performed",
            "",
            "# P1_VS_P4",
            f"`{json.dumps(diagnostics.get('p1_vs_p4', {}), sort_keys=True)}`",
            "",
            "# EVOLUTION_OPERATION_RESULT",
            f"`{json.dumps(diagnostics.get('evolution_operation_attribution', []), sort_keys=True)}`",
            "",
            "# NEXT_DECISION",
            f"`{next_decision}`",
        ]
    elif expansion_mode:
        diagnostics = latest_discovery_diagnostic or {}
        if status in {"ENGINE_RUN_INVALID", "ENGINE_BUDGET_EXHAUSTED"}:
            next_decision = "SYSTEM_INVALID"
        elif int(diagnostics.get("new_matched_positive_economic_cluster_count", 0)) > 0 and int(
            diagnostics.get("new_major_basin_count", 0)
        ) > 0:
            next_decision = "CONTINUE_DEVELOPMENT_DISCOVERY"
        elif int(diagnostics.get("new_economic_opportunity_cluster_count", 0)) > 0:
            next_decision = "SEARCH_SATURATION_REVIEW"
        else:
            next_decision = "SEARCH_CORE_REVIEW_REQUIRED"
        report_lines = [
            "# SEARCH_EXPANSION_VALIDITY",
            f"- status: `{status}`",
            f"- strict/raw attempts: `{strict_count}` / `{state['generation_attempts']}`",
            f"- terminal reason: `{terminal_reason}`",
            "- allocation: `Random/CEM/Evolution = 20/20/60`",
            "- validation/OOS/sealed reads: `0/0/0`",
            "",
            "# ECONOMIC_DISCOVERY_RESULT",
            f"- new economic opportunity clusters: `{diagnostics.get('new_economic_opportunity_cluster_count', 0)}`",
            f"- clusters per 1k / CPU-hour: `{diagnostics.get('new_economic_opportunity_clusters_per_1000', 0.0)}` / `{diagnostics.get('new_economic_opportunity_clusters_per_cpu_hour', 0.0)}`",
            f"- dual-positive / development 2-of-3 / matched-positive clusters: `{diagnostics.get('dual_positive_count', 0)}` / `{diagnostics.get('development_replication_2_of_3_count', 0)}` / `{diagnostics.get('new_matched_positive_economic_cluster_count', 0)}`",
            "",
            "# BASIN_DEPTH_RESULT",
            f"- largest / top3 basin share: `{diagnostics.get('largest_basin_share', 0.0)}` / `{diagnostics.get('top3_basin_share', 0.0)}`",
            f"- effective economic dimension / new major basins: `{diagnostics.get('effective_economic_dimension', 0.0)}` / `{diagnostics.get('new_major_basin_count', 0)}`",
            "",
            "# EVOLUTION_LEARNING_RESULT",
            f"- operation attribution: `{json.dumps(diagnostics.get('evolution_operation_attribution', []), sort_keys=True)}`",
            "- policy feedback from diagnostics: `false`",
            "",
            "# NEXT_DECISION",
            f"`{next_decision}`",
        ]
    else:
        report_lines = [
            "# Crypto Temporal Mechanism Program Search V1",
            "",
            f"- Decision: `{status}`",
            f"- Execution mode: `{execution_mode}`",
            f"- Strict evaluated: `{strict_count:,}`",
            f"- Source prefix / additional strict: `{SUCCESSOR_PREFIX_BOUNDARY if successor_mode else 0:,}` / `{strict_count - SUCCESSOR_PREFIX_BOUNDARY if successor_mode else strict_count:,}`",
            f"- Raw generation attempts: `{state['generation_attempts']:,}`",
            f"- Behavior families: `{len(archive.champion_by_family):,}`",
            f"- Matched-positive candidates/families: `{len(matched)}` / `{len(matched_families)}`",
            f"- Contributing program families: `{sorted(contributing)}`",
            f"- Active program families: `{state['active_program_families']}`",
            f"- Adaptive arm states: `{state['arm_states']}`",
            f"- Terminal reason: `{terminal_reason}`",
            "",
            "This is development-only evidence. No validation, OOS, promotion, target, mapping, cost, reward, AST, compiler, or evaluator change was performed.",
        ]
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    _write_status(runtime_root, state=state, status=status, active_elapsed=elapsed())
    return final


def _successor_executor_identity_errors(
    repo_root: Path,
    authorization: Mapping[str, Any],
    *,
    artifact_relocated: bool,
) -> list[str]:
    if not artifact_relocated:
        return (
            []
            if dict(authorization.get("executor_identity") or {})
            == executor_workspace_identity(repo_root)
            else ["authorization_executor_identity"]
        )
    canonical_path = repo_root / SUCCESSOR_AUTHORIZATION_PATH
    if not canonical_path.is_file():
        return ["authorization_canonical_receipt_missing"]
    canonical = engine._read_json(canonical_path)
    if canonical.get("authorization_sha256") != authorization_content_sha(canonical):
        return ["authorization_canonical_receipt_sha256"]
    if dict(canonical.get("executor_identity") or {}) != dict(
        authorization.get("executor_identity") or {}
    ):
        return ["authorization_canonical_executor_identity"]
    if canonical.get("authorization_sha256") == authorization.get(
        "authorization_sha256"
    ):
        return []
    if not (
        canonical.get("status") == SUCCESSOR_CONSUMED_STATUS
        and canonical.get("run_authorized") is False
        and canonical.get("consumed") is True
    ):
        return ["authorization_canonical_receipt_binding"]
    mutable_keys = {
        "authorization_sha256",
        "consumed",
        "run_authorized",
        "run_outcome",
        "status",
    }
    canonical_immutable = {
        key: value for key, value in canonical.items() if key not in mutable_keys
    }
    runtime_immutable = {
        key: value for key, value in authorization.items() if key not in mutable_keys
    }
    if canonical_immutable != runtime_immutable:
        return ["authorization_canonical_consumed_lineage"]
    return []


def check_successor_runtime(
    repo_root: Path,
    *,
    runtime_date: str,
    artifact_relocated: bool = False,
) -> dict[str, Any]:
    """Independently verify one completed successor runtime without market reads."""

    repo_root = repo_root.resolve()
    runtime_root = repo_root / f"runtime/{SUCCESSOR_CAMPAIGN}_{runtime_date}"
    errors: list[str] = []
    required = (
        "successor_launch_claim.json",
        "frozen_contract.json",
        "embedded_preflight.json",
        "program_catalog.json",
        "search_authority_binding_receipt.json",
        "successor_authorization_snapshot.json",
        "prefix_state_restoration_receipt.json",
        "work_state.json",
        "candidate_ledger.parquet",
        "behavior_archive.parquet",
        "arm_checkpoint_metrics.parquet",
        "rejected_candidate_ledger.parquet",
        "final_decision.json",
        "run_manifest.json",
    )
    for value in required:
        if not (runtime_root / value).is_file():
            errors.append("missing:" + value)
    if errors:
        return {"status": "FAIL", "errors": errors, "sealed_reads": 0}
    frozen = engine._read_json(runtime_root / "frozen_contract.json")
    final = engine._read_json(runtime_root / "final_decision.json")
    state = engine._read_json(runtime_root / "work_state.json")
    authorization = engine._read_json(
        runtime_root / "successor_authorization_snapshot.json"
    )
    claim = engine._read_json(runtime_root / "successor_launch_claim.json")
    restoration = engine._read_json(
        runtime_root / "prefix_state_restoration_receipt.json"
    )
    ledger = pd.read_parquet(runtime_root / "candidate_ledger.parquet")
    if frozen.get("execution_mode") != SUCCESSOR_EXECUTION_MODE:
        errors.append("execution_mode")
    if authorization.get("authorization_sha256") != authorization_content_sha(
        authorization
    ):
        errors.append("authorization_sha256")
    if (
        authorization.get("status") != SUCCESSOR_AUTHORIZED_STATUS
        or authorization.get("run_authorized") is not True
        or authorization.get("consumed") is not False
    ):
        errors.append("authorization_snapshot_state")
    errors.extend(
        _successor_executor_identity_errors(
            repo_root,
            authorization,
            artifact_relocated=artifact_relocated,
        )
    )
    if final.get("successor_authorization_sha256") != authorization.get(
        "authorization_sha256"
    ):
        errors.append("authorization_final_binding")
    if (
        claim.get("status") != "ONE_TIME_SUCCESSOR_LAUNCH_CLAIMED"
        or claim.get("execution_mode") != SUCCESSOR_EXECUTION_MODE
        or claim.get("authorization_sha256")
        != authorization.get("authorization_sha256")
        or claim.get("producer_source_sha") != final.get("producer_source_sha")
        or claim.get("runtime_id") != runtime_root.name
        or int(claim.get("market_arrays_read_at_claim", -1)) != 0
        or int(claim.get("candidate_evaluations_at_claim", -1)) != 0
        or int(claim.get("sealed_reads", -1)) != 0
    ):
        errors.append("successor_launch_claim")
    if (
        int(final.get("source_evidence_prefix", -1)) != SUCCESSOR_PREFIX_BOUNDARY
        or int(final.get("source_invalid_suffix_start", -1))
        != SUCCESSOR_PREFIX_BOUNDARY + 1
        or int(final.get("additional_strict_evaluated", -1))
        != len(ledger) - SUCCESSOR_PREFIX_BOUNDARY
        or int(final.get("cumulative_valid_strict", -1)) != len(ledger)
    ):
        errors.append("successor_budget_accounting")
    try:
        successor_budget_state(len(ledger))
    except RuntimeError:
        errors.append("successor_budget_limit")
    if len(ledger) < SUCCESSOR_PREFIX_BOUNDARY or ledger[
        "completion_ordinal"
    ].astype(int).tolist() != list(range(1, len(ledger) + 1)):
        errors.append("completion_ordinal")
    expected_suffix_zero = {
        "candidate_rows": 0,
        "archive_rows": 0,
        "attempted_exact_ids": 0,
        "completed_pair_ids": 0,
        "policy_local_family_counts": 0,
    }
    if (
        dict(restoration.get("suffix_contribution") or {}) != expected_suffix_zero
        or dict(final.get("invalid_source_suffix_contribution") or {})
        != expected_suffix_zero
    ):
        errors.append("invalid_source_suffix_contribution")
    checkpoints = sorted(
        (runtime_root / "checkpoints").glob("checkpoint_0[1][5-8]/manifest.json")
    )
    for offset, path in enumerate(checkpoints):
        manifest = engine._read_json(path)
        expected_index = 15 + offset
        expected_count = SUCCESSOR_PREFIX_BOUNDARY + (offset + 1) * 5_000
        if (
            int(manifest.get("checkpoint_index", -1)) != expected_index
            or int(manifest.get("completed_ledger_row_count", -1)) != expected_count
            or manifest.get("restore_verified") is not True
        ):
            errors.append(f"successor_checkpoint:{expected_index}")
        for row in manifest.get("files", ()):
            local = path.parent / str(row["name"])
            if not local.is_file() or _sha256_file(local) != str(row["sha256"]):
                errors.append(f"successor_checkpoint_file:{expected_index}:{row['name']}")
    if len(checkpoints) != int(final.get("completed_full_checkpoint_count", -1)):
        errors.append("successor_checkpoint_count")
    decisions = sorted(runtime_root.glob("successor_decision_additional_*.json"))
    if len(decisions) != len(checkpoints):
        errors.append("successor_decision_count")
    allowed_actions = {
        "CONTINUE",
        "PRUNE_ARM_AND_CONTINUE",
        "STOP_ECONOMIC_FUTILITY",
        "STOP_INVALID",
    }
    for index, path in enumerate(decisions, start=1):
        decision = engine._read_json(path)
        if (
            decision.get("status") not in allowed_actions
            or int(path.stem.rsplit("_", 1)[-1]) != index * 5_000
            or decision.get("family_concentration_is_diagnostic_only") is not True
        ):
            errors.append("successor_decision:" + path.name)
    terminal = dict(state.get("terminal_decision") or {})
    if terminal.get("status") != "SEALED":
        errors.append("terminal_seal")
    if int(final.get("sealed_reads", -1)) != 0:
        errors.append("sealed_reads")
    manifest = engine._read_json(runtime_root / "run_manifest.json")
    for row in manifest.get("files", ()):
        local = runtime_root / str(row["path"])
        if not local.is_file() or _sha256_file(local) != str(row["sha256"]):
            errors.append("manifest:" + str(row["path"]))
    result = {
        "schema_version": 1,
        "status": "PASS" if not errors else "FAIL",
        "errors": sorted(set(errors)),
        "producer_source_sha": final.get("producer_source_sha"),
        "source_evidence_prefix": SUCCESSOR_PREFIX_BOUNDARY,
        "additional_strict_evaluated": len(ledger) - SUCCESSOR_PREFIX_BOUNDARY,
        "cumulative_valid_strict": len(ledger),
        "checkpoint_count": len(checkpoints),
        "market_arrays_read_by_checker": 0,
        "candidate_evaluations_by_checker": 0,
        "sealed_reads": 0,
        "executor_identity_verification": (
            "CANONICAL_AUTHORIZATION_LINEAGE_MATCHED_RUNTIME_SNAPSHOT"
            if artifact_relocated
            else "CHECKER_HOST_AND_WORKSPACE_MATCHED_RUNTIME_AUTHORIZATION"
        ),
    }
    engine._write_json(runtime_root / "independent_checker.json", result)
    return result


def check(
    repo_root: Path,
    *,
    runtime_date: str,
    require_consumed: bool = False,
    execution_mode: str = "FRESH_SEQUENTIAL_PROGRAM",
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    expansion_mode = str(execution_mode) == EXPANSION_EXECUTION_MODE
    targeted_mode = str(execution_mode) == TARGETED_EXECUTION_MODE
    fixed_development_mode = expansion_mode or targeted_mode
    runtime_root = repo_root / (
        f"runtime/{EXPANSION_CAMPAIGN}_{runtime_date}"
        if expansion_mode
        else (
            f"runtime/{TARGETED_CAMPAIGN}_{runtime_date}"
            if targeted_mode
            else f"runtime/{CAMPAIGN}_{runtime_date}"
        )
    )
    errors: list[str] = []
    validity_errors: list[str] = []
    required = (
        "frozen_contract.json",
        "embedded_preflight.json",
        "program_catalog.json",
        "candidate_ledger.parquet",
        "behavior_archive.parquet",
        "paired_program_diagnostics.parquet",
        "program_family_metrics.parquet",
        "arm_checkpoint_metrics.parquet",
        "final_decision.json",
        "run_manifest.json",
    )
    if expansion_mode:
        required += (
            "development_expansion_launch_claim.json",
            "development_expansion_authorization_snapshot.json",
            "development_expansion_diagnostic_baseline.json",
            "cluster_diagnostics_latest.json",
        )
    elif targeted_mode:
        required += (
            "targeted_deepening_launch_claim.json",
            "targeted_frozen_parent_pool.json",
            "targeted_deepening_authorization_snapshot.json",
            "targeted_deepening_diagnostic_baseline.json",
            "basin_diagnostics_latest.json",
        )
    for value in required:
        if not (runtime_root / value).is_file():
            errors.append(f"missing:{value}")
    if errors:
        return {"status": "FAIL", "errors": errors}
    frozen = engine._read_json(runtime_root / "frozen_contract.json")
    final = engine._read_json(runtime_root / "final_decision.json")
    config = dict(frozen["config"])
    qualification_scope = dict(frozen.get("qualification_scope") or {})
    try:
        validate_config(config)
    except (KeyError, ValueError, PermissionError) as failure:
        errors.append("config:" + str(failure))
    ledger = pd.read_parquet(runtime_root / "candidate_ledger.parquet")
    pairs = pd.read_parquet(runtime_root / "paired_program_diagnostics.parquet")
    rejected = pd.read_parquet(runtime_root / "rejected_candidate_ledger.parquet")
    if len(ledger) != int(final["strict_evaluated_count"]):
        errors.append("strict_count")
    if dict(final.get("qualification_scope") or {}) != qualification_scope:
        errors.append("qualification_scope")
    if bool(qualification_scope.get("stage0_only")):
        strict_cap = int(qualification_scope.get("strict_cap", -1))
        if strict_cap not in {2_000, 10_000}:
            errors.append("qualification_strict_cap")
        if len(ledger) > strict_cap:
            errors.append("qualification_strict_cap_exceeded")
        if final.get("adaptive_stage_started") is not False:
            errors.append("adaptive_stage_started")
        if any(
            int(path.stem.rsplit("_", 1)[-1]) > strict_cap
            for path in runtime_root.glob("continuation_decision_*.json")
        ):
            errors.append("qualification_adaptive_decision")
    if bool(qualification_scope.get("skip_stage0")):
        if len(pairs) != 0:
            errors.append("adaptive_bootstrap_stage0_pairs_present")
        if bool(final.get("adaptive_stage_started")) != bool(len(ledger) > 0):
            errors.append("adaptive_stage_started")
    elif len(ledger) >= 10_000:
        if len(pairs) != 5_000:
            errors.append("stage0_pair_count")
        else:
            observed = stage0_family_decisions(pairs.to_dict("records"), config)
            recorded_path = runtime_root / "continuation_decision_010000.json"
            if not recorded_path.is_file() or engine._read_json(recorded_path) != observed:
                errors.append("stage0_decision")
    checkpoints = sorted(
        (runtime_root / "checkpoints").glob("checkpoint_[0-9][0-9][0-9]/manifest.json")
    )
    budget_checkpoint = runtime_root / "checkpoints/checkpoint_budget_exhausted/manifest.json"
    invalid_checkpoint = runtime_root / "checkpoints/checkpoint_run_invalid/manifest.json"
    all_checkpoints = [
        *checkpoints,
        *([budget_checkpoint] if budget_checkpoint.is_file() else []),
        *([invalid_checkpoint] if invalid_checkpoint.is_file() else []),
    ]
    if len(all_checkpoints) != int(final["checkpoint_count"]):
        errors.append("checkpoint_count")
    for index, path in enumerate(checkpoints):
        manifest = engine._read_json(path)
        if (
            manifest.get("restore_verified") is not True
            or int(manifest["checkpoint_index"]) != index
            or int(manifest["completed_ledger_row_count"]) != (index + 1) * 2_000
        ):
            errors.append(f"checkpoint_manifest:{index}")
        for row in manifest["files"]:
            local = path.parent / str(row["name"])
            if not local.is_file() or _sha256_file(local) != str(row["sha256"]):
                errors.append(f"checkpoint_file:{index}:{row['name']}")
        if fixed_development_mode and not (
            path.parent / "discovery_diagnostics.json"
        ).is_file():
            errors.append(f"checkpoint_discovery_diagnostics:{index}")
    if budget_checkpoint.is_file():
        manifest = engine._read_json(budget_checkpoint)
        if (
            manifest.get("restore_verified") is not True
            or int(manifest["completed_ledger_row_count"]) != len(ledger)
            or final.get("status") != "ENGINE_BUDGET_EXHAUSTED"
        ):
            errors.append("budget_checkpoint_manifest")
        for row in manifest["files"]:
            local = budget_checkpoint.parent / str(row["name"])
            if not local.is_file() or _sha256_file(local) != str(row["sha256"]):
                errors.append(f"budget_checkpoint_file:{row['name']}")
    if invalid_checkpoint.is_file():
        manifest = engine._read_json(invalid_checkpoint)
        if (
            manifest.get("restore_verified") is not True
            or int(manifest["completed_ledger_row_count"]) != len(ledger)
            or final.get("status") != "ENGINE_RUN_INVALID"
        ):
            errors.append("run_invalid_checkpoint_manifest")
        for row in manifest["files"]:
            local = invalid_checkpoint.parent / str(row["name"])
            if not local.is_file() or _sha256_file(local) != str(row["sha256"]):
                errors.append(f"run_invalid_checkpoint_file:{row['name']}")
    worker_accounting = final.get("worker_accounting")
    errors.extend(
        _program_process_evidence_errors(
            runtime_root,
            expected_batch_count=int(final.get("evaluation_batch_count", 0)),
            configured_worker_processes=(
                int(worker_accounting["configured_worker_processes_initial"])
                if isinstance(worker_accounting, Mapping)
                and "configured_worker_processes_initial" in worker_accounting
                else None
            ),
        )
    )
    if isinstance(worker_accounting, Mapping):
        default_workers = int(config["search_budget"]["workers_default"])
        fallback_workers = int(config["search_budget"]["workers_memory_fallback"])
        initial_workers = int(
            worker_accounting.get("configured_worker_processes_initial", -1)
        )
        final_workers = int(
            worker_accounting.get("configured_worker_processes_final", -1)
        )
        if initial_workers != default_workers:
            errors.append("worker_accounting:configured_worker_processes_initial")
        if final_workers not in {default_workers, fallback_workers} or final_workers != int(
            final.get("workers_final", -1)
        ):
            errors.append("worker_accounting:configured_worker_processes_final")
        if initial_workers > 0 and int(
            worker_accounting.get("configured_paired_task_capacity_initial", -1)
        ) != _stage0_pair_task_capacity(initial_workers):
            errors.append("worker_accounting:configured_paired_task_capacity_initial")
        if final_workers > 0 and int(
            worker_accounting.get("configured_paired_task_capacity_final", -1)
        ) != _stage0_pair_task_capacity(final_workers):
            errors.append("worker_accounting:configured_paired_task_capacity_final")
        if int(worker_accounting.get("strict_rows_per_successful_pair_task", -1)) != 2:
            errors.append("worker_accounting:strict_rows_per_successful_pair_task")
        observed_worker_accounting = _program_process_evidence_summary(runtime_root)
        for key, value in observed_worker_accounting.items():
            if int(worker_accounting.get(key, -1)) != int(value):
                errors.append("worker_accounting:" + key)
    batch_raw_attempts = 0
    for path in sorted(
        (runtime_root / "process_evidence").glob("producer_batch_*.json")
    ):
        batch_raw_attempts += sum(
            int(row.get("raw_attempts", 0))
            for row in engine._read_json(path).get("proposals", ())
        )
    rejected_raw_attempts = (
        int(pd.to_numeric(rejected["raw_attempts"], errors="coerce").fillna(0).sum())
        if "raw_attempts" in rejected.columns
        else 0
    )
    if batch_raw_attempts + rejected_raw_attempts != int(
        final.get("generation_attempts", 0)
    ):
        errors.append("generation_attempt_reconciliation")
    if final.get("status") == "ENGINE_RUN_INVALID":
        validity_errors.append("engine_run_invalid")
        if not invalid_checkpoint.is_file():
            errors.append("missing:checkpoint_run_invalid")
    elif int(final.get("generation_attempts", 0)) > 0 and len(ledger) == 0:
        validity_errors.append("nonzero_attempts_zero_strict")
    if int(final.get("system_error_count", 0)) > 0 and final.get("status") != "ENGINE_RUN_INVALID":
        validity_errors.append("system_error_without_invalid_terminal")
    if final.get("economic_prefix_valid") is True:
        prefix_boundary = int(final.get("valid_prefix_boundary", -1))
        if (
            prefix_boundary <= 0
            or int(final.get("invalid_suffix_start", -1)) != prefix_boundary + 1
            or prefix_boundary > len(ledger)
        ):
            errors.append("valid_prefix_contract")
        expected_terminal_invalid = bool(
            final.get("status") == "ENGINE_RUN_INVALID" or len(ledger) > prefix_boundary
        )
        if bool(final.get("orchestration_terminal_invalid")) != expected_terminal_invalid:
            errors.append("orchestration_terminal_invalid")
    manifest = engine._read_json(runtime_root / "run_manifest.json")
    for row in manifest["files"]:
        local = runtime_root / str(row["path"])
        if not local.is_file() or _sha256_file(local) != str(row["sha256"]):
            errors.append("manifest:" + str(row["path"]))
    if expansion_mode:
        receipt = engine._read_json(
            runtime_root / "development_expansion_authorization_snapshot.json"
        )
        if receipt.get("authorization_sha256") != authorization_content_sha(receipt):
            errors.append("expansion_authorization_snapshot")
        if final.get("execution_mode") != EXPANSION_EXECUTION_MODE:
            errors.append("expansion_execution_mode")
        claim = engine._read_json(
            runtime_root / "development_expansion_launch_claim.json"
        )
        if (
            int(claim.get("market_arrays_read_at_claim", -1)) != 0
            or int(claim.get("candidate_evaluations_at_claim", -1)) != 0
            or int(claim.get("sealed_reads", -1)) != 0
        ):
            errors.append("expansion_launch_claim")
        expected_states = {arm: "ACTIVE" for arm in ARMS[1:]}
        if dict(final.get("arm_states") or {}) != expected_states:
            errors.append("expansion_arm_states")
        if len(pairs) != 0:
            errors.append("expansion_stage0_pairs")
        if len(ledger) == 50_000:
            if (
                final.get("status") != "DEVELOPMENT_EXPANSION_BUDGET_COMPLETE"
                or final.get("terminal_reason")
                != "FIXED_DEVELOPMENT_STRICT_CAP_REACHED"
                or len(checkpoints) != 25
            ):
                errors.append("expansion_mechanical_stop")
            observed_arm_counts = Counter(str(value) for value in ledger["arm"])
            if observed_arm_counts != Counter(
                {
                    "temporal_program_random": 10_000,
                    "temporal_program_cem": 10_000,
                    "temporal_program_evolution": 30_000,
                }
            ):
                errors.append("expansion_fixed_allocation")
        for boundary in EXPANSION_DECISION_BOUNDARIES:
            path = runtime_root / f"continuation_decision_{boundary:06d}.json"
            if len(ledger) >= boundary and (
                not path.is_file()
                or engine._read_json(path) != fixed_flow_decision(boundary)
            ):
                errors.append(f"expansion_fixed_decision:{boundary}")
        diagnostics = engine._read_json(
            runtime_root / "cluster_diagnostics_latest.json"
        )
        if (
            diagnostics.get("status") != "DIAGNOSTIC_ONLY_NOT_SEARCH_AUTHORITY"
            or diagnostics.get("policy_feedback_applied") is not False
            or int(diagnostics.get("sealed_reads", -1)) != 0
        ):
            errors.append("expansion_diagnostics_authority")
        if require_consumed:
            canonical = engine._read_json(repo_root / EXPANSION_AUTHORIZATION_PATH)
            if canonical.get("run_authorized") is not False:
                errors.append("receipt_not_consumed")
    elif targeted_mode:
        receipt = engine._read_json(
            runtime_root / "targeted_deepening_authorization_snapshot.json"
        )
        if receipt.get("authorization_sha256") != authorization_content_sha(receipt):
            errors.append("targeted_authorization_snapshot")
        if final.get("execution_mode") != TARGETED_EXECUTION_MODE:
            errors.append("targeted_execution_mode")
        claim = engine._read_json(runtime_root / "targeted_deepening_launch_claim.json")
        if (
            int(claim.get("market_arrays_read_at_claim", -1)) != 0
            or int(claim.get("candidate_evaluations_at_claim", -1)) != 0
            or int(claim.get("sealed_reads", -1)) != 0
        ):
            errors.append("targeted_launch_claim")
        expected_states = {arm: "ACTIVE" for arm in ARMS[1:]}
        if dict(final.get("arm_states") or {}) != expected_states:
            errors.append("targeted_arm_states")
        if len(pairs) != 0:
            errors.append("targeted_stage0_pairs")
        parent_pool = engine._read_json(
            runtime_root / "targeted_frozen_parent_pool.json"
        )
        parent_pool_core = {
            key: value
            for key, value in parent_pool.items()
            if key != "target_parent_pool_sha256"
        }
        parent_pool_sha = str(parent_pool.get("target_parent_pool_sha256") or "")
        if (
            parent_pool_sha != _json_sha(parent_pool_core)
            or parent_pool_sha != str(frozen.get("targeted_parent_pool_sha256") or "")
            or int(parent_pool.get("market_arrays_read", -1)) != 0
            or int(parent_pool.get("candidate_evaluations", -1)) != 0
            or int(parent_pool.get("validation_reads", -1)) != 0
            or int(parent_pool.get("oos_reads", -1)) != 0
            or int(parent_pool.get("sealed_reads", -1)) != 0
        ):
            errors.append("targeted_parent_pool_identity")
        parent_records = dict(parent_pool.get("parent_records") or {})
        parent_to_basin = {
            str(candidate_id): str(basin.get("economic_similarity_cluster_id") or "")
            for basin in parent_pool.get("target_basins", ())
            for candidate_id in basin.get("member_candidate_ids", ())
        }
        for row in ledger.loc[
            ledger["arm"].astype(str).eq("temporal_program_evolution")
        ].to_dict("records"):
            try:
                receipt_row = json.loads(str(row.get("receipt_json") or "{}"))
                basin_id = str(
                    receipt_row.get("targeted_economic_basin_id") or ""
                )
                parent_ids = [
                    str(value)
                    for value in json.loads(str(row.get("parent_ids_json") or "[]"))
                ]
                if (
                    receipt_row.get("targeted_parent_source")
                    != "FROZEN_TRAIN_ONLY_BASELINE"
                    or str(receipt_row.get("targeted_parent_pool_sha256") or "")
                    != parent_pool_sha
                    or not parent_ids
                    or any(parent_id not in parent_records for parent_id in parent_ids)
                    or any(parent_to_basin.get(parent_id) != basin_id for parent_id in parent_ids)
                ):
                    raise ValueError("targeted parent lineage changed")
                if (
                    str(row.get("operation") or "")
                    == "ONE_POINT_TYPED_MECHANISM_CROSSOVER"
                    and len(parent_ids) == 2
                ):
                    realization_ids = list(
                        receipt_row.get("targeted_parent_realization_ids") or ()
                    )
                    basin_realizations = {
                        str(parent_records[parent_id].get("concrete_realization_id") or "")
                        for parent_id, observed_basin in parent_to_basin.items()
                        if observed_basin == basin_id
                    }
                    if len(basin_realizations) > 1 and len(set(realization_ids)) != 2:
                        raise ValueError("targeted crossover realization collapsed")
            except (ValueError, TypeError, json.JSONDecodeError):
                errors.append(
                    "targeted_evolution_parent_lineage:"
                    + str(row.get("candidate_id") or "UNKNOWN")
                )
        observed_families = set(str(value) for value in ledger["program_family_id"])
        if observed_families - set(TARGETED_PROGRAM_FAMILIES):
            errors.append("targeted_program_family_scope")
        if len(ledger) in {20_000, 30_000}:
            expected_terminal = (
                "TARGETED_DEEPENING_SATURATION_REACHED_20000"
                if len(ledger) == 20_000
                else "TARGETED_DEEPENING_STRICT_CAP_REACHED"
            )
            if (
                final.get("status") != "TARGETED_DEEPENING_BUDGET_COMPLETE"
                or final.get("terminal_reason") != expected_terminal
                or len(checkpoints) != len(ledger) // 2_000
            ):
                errors.append("targeted_mechanical_stop")
            multiplier = len(ledger) // 10_000
            expected_arm_counts = Counter(
                {
                    arm: count * multiplier
                    for arm, count in FIXED_ALLOCATION_PER_10000.items()
                }
            )
            if Counter(str(value) for value in ledger["arm"]) != expected_arm_counts:
                errors.append("targeted_fixed_allocation")
        elif final.get("status") != "ENGINE_RUN_INVALID":
            errors.append("targeted_terminal_strict_count")
        checkpoint_10000 = None
        for boundary in TARGETED_DECISION_BOUNDARIES:
            if len(ledger) < boundary:
                continue
            diagnostic_path = (
                runtime_root / f"basin_diagnostics_boundary_{boundary:06d}.json"
            )
            decision_path = runtime_root / f"continuation_decision_{boundary:06d}.json"
            if not diagnostic_path.is_file() or not decision_path.is_file():
                errors.append(f"targeted_decision_missing:{boundary}")
                continue
            observed_diagnostic = engine._read_json(diagnostic_path)
            expected_decision = targeted_checkpoint_decision(
                boundary,
                observed_diagnostic,
                checkpoint_10000=checkpoint_10000,
            )
            if engine._read_json(decision_path) != expected_decision:
                errors.append(f"targeted_fixed_decision:{boundary}")
            if boundary == 10_000:
                checkpoint_10000 = observed_diagnostic
            if (
                boundary == 20_000
                and len(ledger) == 20_000
                and expected_decision.get("status")
                != "STOP_TARGETED_DEEPENING_SATURATED_AT_20000"
            ):
                errors.append("targeted_saturation_stop_not_satisfied")
        diagnostics = engine._read_json(runtime_root / "basin_diagnostics_latest.json")
        if (
            diagnostics.get("status")
            != "TARGETED_DIAGNOSTIC_ONLY_NOT_SEARCH_AUTHORITY"
            or int(diagnostics.get("strict_boundary", -1)) != len(ledger)
            or diagnostics.get("policy_feedback_applied") is not False
            or int(diagnostics.get("validation_reads", -1)) != 0
            or int(diagnostics.get("oos_reads", -1)) != 0
            or int(diagnostics.get("sealed_reads", -1)) != 0
        ):
            errors.append("targeted_diagnostics_authority")
        if require_consumed:
            canonical = engine._read_json(repo_root / TARGETED_AUTHORIZATION_PATH)
            if canonical.get("run_authorized") is not False:
                errors.append("receipt_not_consumed")
    else:
        receipt = validate_receipt(repo_root, config=config, require_authorized=False)
        if require_consumed and receipt.get("run_authorized") is not False:
            errors.append("receipt_not_consumed")
    result = {
        "schema_version": 1,
        "status": "PASS" if not errors and not validity_errors else "FAIL",
        "artifact_integrity_status": "PASS" if not errors else "FAIL",
        "run_validity_status": "PASS" if not validity_errors else "INVALID",
        "errors": sorted(set(errors)),
        "validity_errors": sorted(set(validity_errors)),
        "producer_source_sha": final["producer_source_sha"],
        "strict_evaluated_count": len(ledger),
        "checkpoint_count": len(all_checkpoints),
        "stage0_pair_count": len(pairs),
        "reconciled_generation_attempts": batch_raw_attempts
        + rejected_raw_attempts,
        "valid_prefix_boundary": final.get("valid_prefix_boundary"),
        "invalid_suffix_start": final.get("invalid_suffix_start"),
        "economic_prefix_valid": bool(final.get("economic_prefix_valid", False)),
        "orchestration_terminal_invalid": bool(
            final.get("orchestration_terminal_invalid", False)
        ),
        "sealed_reads": 0,
        "execution_mode": str(execution_mode),
    }
    engine._write_json(runtime_root / "independent_checker.json", result)
    if targeted_mode:
        report_path = repo_root / (
            "reports/CRYPTO_TEMPORAL_TARGETED_P1_P4_BASIN_DEEPENING_V1_"
            f"{runtime_date}.md"
        )
        if report_path.is_file():
            report_lines = report_path.read_text(encoding="utf-8").splitlines()
            report_lines = [
                (
                    f"- independent checker: `{result['status']}`"
                    if line.startswith("- independent checker:")
                    else line
                )
                for line in report_lines
            ]
            report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    return result


def consume_receipt(
    repo_root: Path,
    *,
    runtime_date: str,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    path = repo_root / RECEIPT_PATH
    receipt = engine._read_json(path)
    if receipt.get("run_authorized") is not True:
        raise RuntimeError("temporal program receipt is already consumed")
    final = engine._read_json(
        repo_root / f"runtime/{CAMPAIGN}_{runtime_date}/final_decision.json"
    )
    updated = {
        key: value
        for key, value in receipt.items()
        if key not in {"receipt_sha256", "run_outcome"}
    }
    updated.update(
        {
            "status": "RUN_AUTHORIZATION_CONSUMED",
            "run_authorized": False,
            "run_outcome": {
                "status": final["status"],
                "runtime": f"runtime/{CAMPAIGN}_{runtime_date}",
                "producer_source_sha": final["producer_source_sha"],
                "strict_evaluated_count": final["strict_evaluated_count"],
                "generation_attempts": final["generation_attempts"],
                "checkpoint_count": final["checkpoint_count"],
                "rescue_rerun_started": False,
            },
        }
    )
    updated["receipt_sha256"] = _receipt_content_sha(updated)
    engine._write_json(path, updated)
    return updated


def consume_development_expansion_authorization(
    repo_root: Path,
    *,
    runtime_date: str,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    path = repo_root / EXPANSION_AUTHORIZATION_PATH
    authorization = engine._read_json(path)
    if (
        authorization.get("run_authorized") is not True
        or authorization.get("consumed") is not False
    ):
        raise RuntimeError("development expansion authorization is not active")
    runtime_root = repo_root / f"runtime/{EXPANSION_CAMPAIGN}_{runtime_date}"
    checker = engine._read_json(runtime_root / "independent_checker.json")
    if checker.get("status") != "PASS":
        raise RuntimeError("development expansion independent checker did not pass")
    final = engine._read_json(runtime_root / "final_decision.json")
    updated = {
        key: value
        for key, value in authorization.items()
        if key not in {"authorization_sha256", "run_outcome"}
    }
    updated.update(
        {
            "status": "RUN_AUTHORIZATION_CONSUMED_50000_STRICT_DEVELOPMENT_EXPANSION",
            "run_authorized": False,
            "consumed": True,
            "run_outcome": {
                "status": final["status"],
                "runtime": f"runtime/{EXPANSION_CAMPAIGN}_{runtime_date}",
                "producer_source_sha": final["producer_source_sha"],
                "strict_evaluated_count": final["strict_evaluated_count"],
                "generation_attempts": final["generation_attempts"],
                "checkpoint_count": final["checkpoint_count"],
                "sealed_reads": 0,
                "automatic_next_run_started": False,
            },
        }
    )
    updated["authorization_sha256"] = authorization_content_sha(updated)
    temporary = path.with_name(path.name + ".consuming.tmp")
    engine._write_json(temporary, updated)
    os.replace(temporary, path)
    return updated


def consume_targeted_deepening_authorization(
    repo_root: Path,
    *,
    runtime_date: str,
    system_invalid_audit: Path | None = None,
    producer_status_evidence: Path | None = None,
    task_status_evidence: Path | None = None,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    path = repo_root / TARGETED_AUTHORIZATION_PATH
    authorization = engine._read_json(path)
    if (
        authorization.get("status") != TARGETED_AUTHORIZED_STATUS
        or authorization.get("run_authorized") is not True
        or authorization.get("consumed") is not False
    ):
        raise RuntimeError("targeted deepening authorization is not active")
    runtime_root = repo_root / f"runtime/{TARGETED_CAMPAIGN}_{runtime_date}"
    if runtime_root.name != str(authorization.get("runtime_id") or ""):
        raise RuntimeError("targeted deepening runtime identity changed")
    invalid_evidence = (
        system_invalid_audit,
        producer_status_evidence,
        task_status_evidence,
    )
    if any(value is not None for value in invalid_evidence) and not all(
        value is not None for value in invalid_evidence
    ):
        raise ValueError("system-invalid consumption requires all evidence paths")
    if system_invalid_audit is None:
        checker = engine._read_json(runtime_root / "independent_checker.json")
        if checker.get("status") != "PASS":
            raise RuntimeError("targeted deepening independent checker did not pass")
        final = engine._read_json(runtime_root / "final_decision.json")
        run_outcome = {
            "status": final["status"],
            "runtime": runtime_root.relative_to(repo_root).as_posix(),
            "producer_source_sha": final["producer_source_sha"],
            "strict_evaluated_count": final["strict_evaluated_count"],
            "generation_attempts": final["generation_attempts"],
            "checkpoint_count": final["checkpoint_count"],
            "sealed_reads": 0,
            "automatic_next_run_started": False,
        }
    else:
        def evidence_path(value: Path | None) -> Path:
            assert value is not None
            return value if value.is_absolute() else repo_root / value

        audit_path = evidence_path(system_invalid_audit)
        producer_path = evidence_path(producer_status_evidence)
        task_path = evidence_path(task_status_evidence)

        def read_external_evidence(path: Path) -> dict[str, Any]:
            return json.loads(path.read_text(encoding="utf-8-sig"))

        audit = read_external_evidence(audit_path)
        producer = read_external_evidence(producer_path)
        task = read_external_evidence(task_path)
        if (
            audit.get("status") != "FAIL"
            or audit.get("finding")
            != "TARGETED_PROGRAM_FAMILY_SCOPE_VIOLATION"
            or audit.get("next_decision") != "SYSTEM_INVALID"
            or audit.get("runtime_id") != runtime_root.name
            or int(audit.get("out_of_scope_strict_rows", 0)) <= 0
            or int(audit.get("strict_rows_audited", 0)) <= 0
            or audit.get("completion_ordinals_contiguous") is not True
            or int(audit.get("market_arrays_read_by_audit", -1)) != 0
            or int(audit.get("candidate_evaluations_by_audit", -1)) != 0
            or int(audit.get("validation_reads", -1)) != 0
            or int(audit.get("oos_reads", -1)) != 0
            or int(audit.get("sealed_reads", -1)) != 0
        ):
            raise RuntimeError("targeted system-invalid audit is not admissible")
        if (
            producer.get("producer_source_sha")
            != audit.get("producer_source_sha")
            or int(producer.get("strict_evaluated", 0))
            < int(audit["strict_rows_audited"])
            or int(producer.get("generation_attempts", 0)) <= 0
            or producer.get("status") != "RUNNING"
        ):
            raise RuntimeError("targeted invalid producer evidence changed")
        if (
            task.get("task_id") != audit.get("task_id")
            or task.get("state") != "FAILED"
            or int(task.get("exit_code", 0)) == 0
            or not task.get("ended_at")
        ):
            raise RuntimeError("targeted invalid task termination is not proven")
        run_outcome = {
            "status": "SYSTEM_INVALID",
            "terminal_reason": audit["finding"],
            "runtime": runtime_root.relative_to(repo_root).as_posix(),
            "producer_source_sha": producer["producer_source_sha"],
            "strict_evaluated_count": int(producer["strict_evaluated"]),
            "audited_strict_prefix": int(audit["strict_rows_audited"]),
            "generation_attempts": int(producer["generation_attempts"]),
            "checkpoint_count": int(producer["checkpoint_index"]),
            "checker": "INDEPENDENT_SCOPE_AUDIT_FAIL",
            "runtime_integrity": "INVALID_PARTIAL_NO_FINAL_MANIFEST",
            "task_id": task["task_id"],
            "task_state": task["state"],
            "audit_sha256": _sha256_file(audit_path),
            "system_invalid_audit": audit_path.relative_to(repo_root).as_posix(),
            "producer_status_evidence": producer_path.relative_to(
                repo_root
            ).as_posix(),
            "task_status_evidence": task_path.relative_to(repo_root).as_posix(),
            "validation_reads": 0,
            "oos_reads": 0,
            "sealed_reads": 0,
            "automatic_next_run_started": False,
        }
    updated = {
        key: value
        for key, value in authorization.items()
        if key not in {"authorization_sha256", "run_outcome"}
    }
    updated.update(
        {
            "status": TARGETED_CONSUMED_STATUS,
            "run_authorized": False,
            "consumed": True,
            "run_outcome": run_outcome,
        }
    )
    updated["authorization_sha256"] = authorization_content_sha(updated)
    temporary = path.with_name(path.name + ".consuming.tmp")
    engine._write_json(temporary, updated)
    os.replace(temporary, path)
    return updated


def consume_successor_authorization(
    repo_root: Path,
    *,
    runtime_date: str,
    artifact_relocated: bool = False,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    path = repo_root / SUCCESSOR_AUTHORIZATION_PATH
    authorization = engine._read_json(path)
    if (
        authorization.get("status") != SUCCESSOR_AUTHORIZED_STATUS
        or authorization.get("run_authorized") is not True
        or authorization.get("consumed") is not False
    ):
        raise RuntimeError("successor authorization is not active or already consumed")
    runtime_root = repo_root / f"runtime/{SUCCESSOR_CAMPAIGN}_{runtime_date}"
    if runtime_root.name != str(authorization.get("runtime_id") or ""):
        raise RuntimeError("successor authorization runtime identity changed")
    runtime_authorization = engine._read_json(
        runtime_root / "successor_authorization_snapshot.json"
    )
    identity_errors = _successor_executor_identity_errors(
        repo_root,
        runtime_authorization,
        artifact_relocated=artifact_relocated,
    )
    if identity_errors:
        raise RuntimeError("successor authorization executor identity changed")
    final = engine._read_json(runtime_root / "final_decision.json")
    checker = engine._read_json(runtime_root / "independent_checker.json")
    if checker.get("status") != "PASS":
        raise RuntimeError("successor independent checker did not pass")
    expected_identity_verification = (
        "CANONICAL_AUTHORIZATION_LINEAGE_MATCHED_RUNTIME_SNAPSHOT"
        if artifact_relocated
        else "CHECKER_HOST_AND_WORKSPACE_MATCHED_RUNTIME_AUTHORIZATION"
    )
    if checker.get("executor_identity_verification") != expected_identity_verification:
        raise RuntimeError("successor checker identity mode changed")
    updated = {
        key: value
        for key, value in authorization.items()
        if key not in {"authorization_sha256", "run_outcome"}
    }
    updated.update(
        {
            "status": SUCCESSOR_CONSUMED_STATUS,
            "run_authorized": False,
            "consumed": True,
            "run_outcome": {
                "status": final["status"],
                "runtime": runtime_root.relative_to(repo_root).as_posix(),
                "producer_source_sha": final["producer_source_sha"],
                "source_evidence_prefix": final["source_evidence_prefix"],
                "additional_strict_evaluated": final[
                    "additional_strict_evaluated"
                ],
                "cumulative_valid_strict": final["cumulative_valid_strict"],
                "second_launch_started": False,
                "rescue_rerun_started": False,
            },
        }
    )
    updated["authorization_sha256"] = authorization_content_sha(updated)
    temporary = path.with_name(path.name + ".consuming.tmp")
    engine._write_json(temporary, updated)
    os.replace(temporary, path)
    return updated


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    for name in (
        "run",
        "check",
        "check-successor",
        "consume-receipt",
        "consume-successor-authorization",
        "consume-development-expansion-authorization",
        "consume-targeted-deepening-authorization",
    ):
        command = sub.add_parser(name)
        command.add_argument("--repo-root", type=Path, required=True)
        command.add_argument("--runtime-date", required=True)
        if name == "run":
            command.add_argument("--source-sha")
            command.add_argument(
                "--execution-mode",
                choices=(
                    "FRESH_SEQUENTIAL_PROGRAM",
                    SUCCESSOR_EXECUTION_MODE,
                    EXPANSION_EXECUTION_MODE,
                    TARGETED_EXECUTION_MODE,
                ),
                default="FRESH_SEQUENTIAL_PROGRAM",
            )
            command.add_argument("--successor-artifact-root", type=Path)
            command.add_argument("--successor-policy-bundle", type=Path)
        if name == "check":
            command.add_argument("--require-consumed", action="store_true")
            command.add_argument(
                "--execution-mode",
                choices=(
                    "FRESH_SEQUENTIAL_PROGRAM",
                    EXPANSION_EXECUTION_MODE,
                    TARGETED_EXECUTION_MODE,
                ),
                default="FRESH_SEQUENTIAL_PROGRAM",
            )
        if name in {"check-successor", "consume-successor-authorization"}:
            command.add_argument("--artifact-relocated", action="store_true")
        if name == "consume-targeted-deepening-authorization":
            command.add_argument("--system-invalid-audit", type=Path)
            command.add_argument("--producer-status-evidence", type=Path)
            command.add_argument("--task-status-evidence", type=Path)
    smoke = sub.add_parser("source-smoke")
    smoke.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "run":
        result = run(
            args.repo_root,
            runtime_date=args.runtime_date,
            source_sha=args.source_sha,
            execution_mode=args.execution_mode,
            successor_artifact_root=args.successor_artifact_root,
            successor_policy_bundle=args.successor_policy_bundle,
        )
    elif args.command == "check":
        result = check(
            args.repo_root,
            runtime_date=args.runtime_date,
            require_consumed=bool(args.require_consumed),
            execution_mode=args.execution_mode,
        )
    elif args.command == "check-successor":
        result = check_successor_runtime(
            args.repo_root,
            runtime_date=args.runtime_date,
            artifact_relocated=bool(args.artifact_relocated),
        )
    elif args.command == "consume-receipt":
        result = consume_receipt(args.repo_root, runtime_date=args.runtime_date)
    elif args.command == "consume-successor-authorization":
        result = consume_successor_authorization(
            args.repo_root,
            runtime_date=args.runtime_date,
            artifact_relocated=bool(args.artifact_relocated),
        )
    elif args.command == "consume-development-expansion-authorization":
        result = consume_development_expansion_authorization(
            args.repo_root,
            runtime_date=args.runtime_date,
        )
    elif args.command == "consume-targeted-deepening-authorization":
        result = consume_targeted_deepening_authorization(
            args.repo_root,
            runtime_date=args.runtime_date,
            system_invalid_audit=args.system_invalid_audit,
            producer_status_evidence=args.producer_status_evidence,
            task_status_evidence=args.task_status_evidence,
        )
    else:
        result = source_smoke(args.repo_root)
    print(json.dumps(result, sort_keys=True, default=str))
    if args.command in {"check", "check-successor"} and result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()


__all__ = [
    "adaptive_gate",
    "check",
    "check_successor_runtime",
    "consume_receipt",
    "consume_targeted_deepening_authorization",
    "consume_successor_authorization",
    "run",
    "source_smoke",
    "stage0_family_decisions",
    "validate_config",
]
