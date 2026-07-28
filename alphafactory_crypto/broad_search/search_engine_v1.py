"""Bounded Broad-39 Search Engine V1 rolling Arena.

This module is deliberately an orchestration layer over the existing fixed
Skeleton/CandidateSpec genome, typed compiler, matched control, and pair
evaluator.  It does not introduce another AST, compiler, evaluator, scheduler,
database, or checkpoint service.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import math
import os
import random
import shutil
import subprocess
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

import numpy as np
import pandas as pd
import psutil

from alphafactory_crypto.data_admission_v1 import (
    AGGTRADES_SYSTEM_CANARY_FIELDS,
    build_aggtrades_system_canary_cache,
)
from alphafactory_crypto.instrument_canary.release import sha256_file

from .audit import FIELD_CONTRACTS as LEGACY_AGGTRADES_FIELD_CONTRACTS
from .audit import freeze_search_behavior_contract
from .compositional18m import (
    BETAS,
    HORIZONS,
    NORMALIZERS,
    WINDOWS,
    CandidateSpec,
    Skeleton,
    _effective_generation_gene_names,
    _legal_normalizers,
    _legal_windows,
    _mutable_gene_domains,
    candidate_from_genes,
    field_role_coverage,
    field_role_surface,
    generate_candidate,
    generate_effective_candidate,
    skeleton_registry,
)
from .expression import FieldContract, TypedExpressionRegistry
from .pair18m import (
    FIXED_COST_BPS,
    evaluate_pair,
    feedback_contract_payload,
    pair_contract_payload,
)
from .panel18m import RawPanelStore, infer_family
from .runner18m import (
    ADAPTIVE_END,
    ADAPTIVE_START,
    LanePolicy,
    _compiler_binding,
    _contracts_from_payload,
    _contracts_payload,
    _current_field_surface_binding,
    _directory_bundle,
    _environment_fingerprint,
    load_search_surface_carrier,
    _source_tree_clean_for_run,
)


EPOCH_ID = "CRYPTO_SEARCH_ENGINE_V1_20260721"
DEFAULT_RUNTIME_DATE = "20260721"
BASE_SHA = "bbb0e696bc5f560f733dd4e9bfe263f11e4bb840"
AGGTRADES_CANARY_EPOCH_ID = "CRYPTO_AGGTRADES_SYSTEM_CANARY_V1_20260727"
AGGTRADES_CANARY_DEFAULT_RUNTIME_DATE = "20260727"
AGGTRADES_CANARY_CONFIG = "config/crypto_aggtrades_system_canary_v1.json"
V11_EPOCH_ID = "CRYPTO_SEARCH_ENGINE_V1_1_BEHAVIOR_NICHED_20260727"
V11_DEFAULT_RUNTIME_DATE = "20260727"
V11_CONFIG = "config/crypto_search_engine_v1_1.json"
V12_EPOCH_ID = "CRYPTO_SEARCH_ENGINE_V1_2_COLLISION_CONTROLLED_20260727"
V12_DEFAULT_RUNTIME_DATE = "20260727"
V12_CONFIG = "config/crypto_search_engine_v1_2.json"
CARRIER_GATE_CONFIG = "config/crypto_search_carrier_gate_v1.json"
CARRIER_GATE_EPOCH_ID = "CRYPTO_SEARCH_CARRIER_GATE_V1_20260728"
CARRIER_GATE_DEFAULT_RUNTIME_DATE = "20260728"
CARRIER_GATE_ARMS = (
    "canonical_typed_random",
    "hierarchical_typed_cem_v2",
    "typed_evolution_v2",
)
CARRIER_GATE_CHECKPOINT_SIZE = 128
CARRIER_GATE_CHECKPOINT_COUNT = 2
CARRIER_GATE_STRICT_TARGET = 256
CARRIER_GATE_RAW_ATTEMPT_LIMIT = 20_000
CARRIER_GATE_WALL_TIME_LIMIT_SECONDS = 2 * 60 * 60
CARRIER_GATE_CHECKPOINT_ALLOCATION = {
    "canonical_typed_random": 32,
    "hierarchical_typed_cem_v2": 48,
    "typed_evolution_v2": 48,
}
CARRIER_GATE_IDS = (
    "AGGTRADES_TOP200_DELIVERED",
    "CORE3_MICROSTRUCTURE_PILOT",
    "OI_MARK_RANKS51_200_DELIVERED",
)
CONTINUATION_CONFIG = "config/crypto_18m_current_field_four_policy_continuation_v1.json"
CONTINUATION_RUNTIME = "runtime/crypto_18m_current_field_four_policy_continuation_20260719"
SEEDS = (20260716, 20260717, 20260718, 20260719)
FIRST_CHECKPOINT_ARMS = (
    "canonical_typed_random",
    "cem_distribution_v1",
    "evolutionary_typed_v1",
    "hierarchical_typed_cem_v2",
    "typed_evolution_v2",
)
ROLLING_ARMS = (
    "canonical_typed_random",
    "hierarchical_typed_cem_v2",
    "typed_evolution_v2",
)
CHECKPOINT_SIZE = 2_000
CHECKPOINT_COUNT = 10
STRICT_TARGET = CHECKPOINT_SIZE * CHECKPOINT_COUNT
RAW_ATTEMPT_LIMIT = 100_000
MAX_SINGLE_PROPOSAL_RAW_ATTEMPTS = 4_225
WALL_TIME_LIMIT_SECONDS = 18 * 60 * 60
DEFAULT_WORKERS = 10
FALLBACK_WORKERS = 8
MEMORY_GATE_BYTES = 12 * 1024**3
AGGTRADES_CANARY_ARMS = (
    "canonical_typed_random",
    "hierarchical_typed_cem_v2",
    "typed_evolution_v2",
)
AGGTRADES_CANARY_CHECKPOINT_SIZE = 1_000
AGGTRADES_CANARY_CHECKPOINT_COUNT = 2
AGGTRADES_CANARY_STRICT_TARGET = (
    AGGTRADES_CANARY_CHECKPOINT_SIZE * AGGTRADES_CANARY_CHECKPOINT_COUNT
)
AGGTRADES_CANARY_RAW_ATTEMPT_LIMIT = 20_000
AGGTRADES_CANARY_WALL_TIME_LIMIT_SECONDS = 4 * 60 * 60
AGGTRADES_CANARY_CHECKPOINT_ALLOCATION = {
    "canonical_typed_random": 200,
    "hierarchical_typed_cem_v2": 400,
    "typed_evolution_v2": 400,
}
V11_ARMS = (
    "canonical_typed_random",
    "behavior_niched_cem_v2_1",
    "behavior_niched_evolution_v2_1",
)
V11_CHECKPOINT_SIZE = 1_500
V11_CHECKPOINT_COUNT = 2
V11_STRICT_TARGET = V11_CHECKPOINT_SIZE * V11_CHECKPOINT_COUNT
V11_RAW_ATTEMPT_LIMIT = 20_000
V11_WALL_TIME_LIMIT_SECONDS = 4 * 60 * 60
V11_CHECKPOINT_ALLOCATION = {
    "canonical_typed_random": 500,
    "behavior_niched_cem_v2_1": 500,
    "behavior_niched_evolution_v2_1": 500,
}
V12_ARMS = (
    "canonical_typed_random",
    "collision_controlled_evolution_v2_2",
)
V12_CHECKPOINT_SIZE = 1_000
V12_CHECKPOINT_COUNT = 2
V12_STRICT_TARGET = V12_CHECKPOINT_SIZE * V12_CHECKPOINT_COUNT
V12_RAW_ATTEMPT_LIMIT = 15_000
V12_WALL_TIME_LIMIT_SECONDS = 4 * 60 * 60
V12_CHECKPOINT_ALLOCATION = {
    "canonical_typed_random": 500,
    "collision_controlled_evolution_v2_2": 500,
}
V12_BALANCED_BATCH_SIZE = len(V12_ARMS) * len(SEEDS)
QUALIFICATION_TOLERANCE = 1.0e-12
QUALIFICATION_DUPLICATE_RATE_MAXIMUM = 0.20
GENE_ORDER = (
    "left_field",
    "right_field",
    "left_window",
    "right_window",
    "beta",
    "left_normalizer",
    "right_normalizer",
    "horizon_hours",
)
EVOLUTION_OPERATIONS = (
    "EFFECTIVE_GENE_MUTATION_1_TO_3",
    "COMPATIBLE_SKELETON_VARIANT_MUTATION",
    "ONE_POINT_HOMOLOGOUS_GENE_BUNDLE_CROSSOVER",
)
V2_PARAMETERS: Mapping[str, Mapping[str, Any]] = {
    "hierarchical_typed_cem_v2": {
        "elite_fraction": 0.20,
        "smoothing": 0.35,
        "minimum_probability": 0.002,
        "entropy_floor_ratio": 0.60,
        "minimum_observation_count": 8,
        "count_pseudocount": 0.50,
        "duplicate_resample_limit": 64,
    },
    "typed_evolution_v2": {
        "warmup": 32,
        "tournament_size": 4,
        "population_limit": 256,
        "mechanism_cell_limit": 64,
        "gene_mutation_probability": 0.55,
        "skeleton_variant_mutation_probability": 0.25,
        "homologous_crossover_probability": 0.20,
        "minimum_mutated_genes": 1,
        "maximum_mutated_genes": 3,
        "duplicate_resample_limit": 64,
    },
}
V21_PARAMETERS: Mapping[str, Mapping[str, Any]] = {
    "behavior_niched_cem_v2_1": {
        **V2_PARAMETERS["hierarchical_typed_cem_v2"],
        "behavior_family_champion_elites": True,
        "mechanism_stratified_elites": True,
        "skeleton_stratified_elites": True,
    },
    "behavior_niched_evolution_v2_1": {
        **V2_PARAMETERS["typed_evolution_v2"],
        "skeleton_cell_limit": 32,
        "prefer_cross_skeleton_crossover": True,
        "operator_productivity_adaptation": True,
        "operator_productivity_floor": 0.15,
        "operator_productivity_prior_successes": 1,
        "operator_productivity_prior_trials": 2,
    },
}
V22_PARAMETERS: Mapping[str, Mapping[str, Any]] = {
    "collision_controlled_evolution_v2_2": {
        **V21_PARAMETERS["behavior_niched_evolution_v2_1"],
        "campaign_local_transition_collision_control": True,
        "transition_block_after_collisions": 1,
    },
}
V1_PARAMETERS: Mapping[str, Mapping[str, Any]] = {
    "canonical_typed_random": {"duplicate_resample_limit": 64},
    "cem_distribution_v1": {
        "generation_size": 16,
        "elite_fraction": 0.25,
        "smoothing": 0.50,
        "minimum_probability": 0.005,
        "duplicate_resample_limit": 64,
    },
    "evolutionary_typed_v1": {
        "warmup": 16,
        "exploration_probability": 0.25,
        "tournament_size": 4,
        "duplicate_resample_limit": 64,
    },
}


def _payload_sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            default=str,
        ).encode("utf-8")
    ).hexdigest().upper()


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".tmp-{os.getpid()}")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True, default=str)
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    os.replace(temporary, path)


def _write_parquet(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".tmp-{os.getpid()}")
    pd.DataFrame(list(rows)).to_parquet(temporary, index=False)
    os.replace(temporary, path)


def _git_sha(repo_root: Path) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=repo_root, text=True
    ).strip().lower()


def _git_blob_sha(repo_root: Path, path: str) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", f"HEAD:{path}"], cwd=repo_root, text=True
    ).strip().lower()


def _json_rng_state(state: tuple[Any, ...]) -> Any:
    return [_json_rng_state(value) if isinstance(value, tuple) else value for value in state]


def _tuple_rng_state(state: Any) -> Any:
    return tuple(_tuple_rng_state(value) for value in state) if isinstance(state, list) else state


def _skeleton_by_id(skeleton_id: str) -> Skeleton:
    return next(item for item in skeleton_registry() if item.skeleton_id == skeleton_id)


def _family_fields(
    roles: Mapping[str, Sequence[str]], role: str
) -> dict[str, tuple[str, ...]]:
    output: dict[str, list[str]] = defaultdict(list)
    for field_id in roles[role]:
        output[infer_family(str(field_id))].append(str(field_id))
    return {key: tuple(sorted(values)) for key, values in sorted(output.items())}


def _candidate_rebuild_verified(
    registry: TypedExpressionRegistry,
    candidate: CandidateSpec,
    roles: Mapping[str, Sequence[str]],
) -> bool:
    try:
        rebuilt = candidate_from_genes(
            registry,
            skeleton=_skeleton_by_id(candidate.skeleton_id),
            genes=candidate.generation_genes,
            roles=roles,
        )
        return bool(
            rebuilt.candidate_id == candidate.candidate_id
            and rebuilt.expression.expression_id == candidate.expression.expression_id
            and rebuilt.control.expression_id == candidate.control.expression_id
        )
    except (KeyError, TypeError, ValueError):
        return False


def _broad39_registry_contracts(
    repo_root: Path,
) -> tuple[tuple[FieldContract, ...], dict[str, Any], dict[str, Any]]:
    continuation_path = repo_root / CONTINUATION_CONFIG
    continuation = _read_json(continuation_path)
    field_binding, field_ids = _current_field_surface_binding(repo_root, continuation)
    if field_ids is None or len(field_ids) != 39:
        raise PermissionError("Broad registry authority no longer resolves 39 fields")
    prior_runtime = repo_root / CONTINUATION_RUNTIME
    prior_manifest = _read_json(prior_runtime / "CRYPTO_ARTIFACT_MANIFEST.json")
    registry_path = prior_runtime / "CRYPTO_18M_COMPOSITIONAL_FIELD_REGISTRY.json"
    registry_record = next(
        row
        for row in prior_manifest["artifacts"]
        if row["path"].endswith("CRYPTO_18M_COMPOSITIONAL_FIELD_REGISTRY.json")
    )
    if sha256_file(registry_path) != registry_record["sha256"]:
        raise ValueError("committed Broad field registry identity changed")
    registry_payload = _read_json(registry_path)
    rows = registry_payload["fields"]
    if registry_payload.get("field_count") != 39 or {
        str(row["field_id"]) for row in rows
    } != set(field_ids):
        raise ValueError("committed Broad field registry no longer matches its surface")
    by_id = {str(row["field_id"]): row for row in rows}
    contracts = tuple(
        FieldContract(
            field_id,
            str(by_id[field_id]["value_type"]),
            str(by_id[field_id]["unit"]),
            1,
            "CURRENT_CORE_PACK_ADAPTIVE_ONLY_QUALIFICATION",
        )
        for field_id in sorted(field_ids)
    )
    identity = {
        "field_surface": field_binding,
        "field_registry": {
            "path": registry_path.relative_to(repo_root).as_posix(),
            "sha256": registry_record["sha256"],
            "logical_sha256": registry_payload["registry_sha256"],
        },
        "continuation_config": {
            "path": CONTINUATION_CONFIG,
            "sha256": sha256_file(continuation_path),
        },
    }
    return contracts, identity, continuation


def _aggtrades_canary_contracts() -> tuple[FieldContract, ...]:
    contracts = tuple(
        FieldContract(
            "agg_trade_count" if item.field_id == "trade_count" else item.field_id,
            item.value_type,
            item.unit,
            1,
            "AGGTRADES_FIXED_COHORT_SYSTEM_CANARY_HOUR_CLOSE",
        )
        for item in LEGACY_AGGTRADES_FIELD_CONTRACTS
    )
    if {item.field_id for item in contracts} != set(AGGTRADES_SYSTEM_CANARY_FIELDS):
        raise AssertionError("aggTrades canary FieldContract surface drifted")
    return contracts


def _load_bound_inputs(
    repo_root: Path,
) -> tuple[
    RawPanelStore,
    tuple[FieldContract, ...],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    continuation_path = repo_root / CONTINUATION_CONFIG
    continuation = _read_json(continuation_path)
    field_binding, field_ids = _current_field_surface_binding(repo_root, continuation)
    if field_ids is None or len(field_ids) != 39:
        raise PermissionError("Search Engine V1 requires the frozen Broad 39 surface")
    if continuation["field_surface"].get("excluded_contexts") != [
        "CORE3_MICROSTRUCTURE_PILOT"
    ]:
        raise PermissionError("Core3 exclusion changed")

    cache_root = repo_root / str(continuation["cache_root"])
    cache_metadata = _read_json(cache_root / "metadata.json")
    panel_context = cache_metadata.get("panel_context_contract", {})
    if int(cache_metadata.get("schema_version", 0)) < 2 or panel_context.get(
        "authority"
    ) != "POST_JOIN_ASSET_BY_TIME_RECOMPUTE":
        raise ValueError("raw cache lacks the post-join panel context authority")
    if set(panel_context.get("fields", [])) != {
        "active_universe_size",
        "age_percentile_active_universe",
        "history_length_hours",
    }:
        raise ValueError("raw cache panel context field contract changed")
    reuse = continuation["cache_reuse"]
    if cache_metadata.get("identity_sha256") != reuse["expected_identity_sha256"]:
        raise ValueError("pinned raw-cache identity changed")
    if cache_metadata.get("source_sha") != reuse["expected_producer_source_sha"]:
        raise ValueError("pinned raw-cache producer changed")
    directory_bundle = _directory_bundle(cache_root)
    if directory_bundle != {
        "file_count": int(reuse["directory_bundle"]["file_count"]),
        "bytes": int(reuse["directory_bundle"]["bytes"]),
        "bundle_sha256": str(reuse["directory_bundle"]["bundle_sha256"]).upper(),
    }:
        raise ValueError("pinned raw-cache content bundle changed")
    for record in reuse["evidence_inputs"].values():
        path = repo_root / str(record["path"])
        if not path.is_file() or sha256_file(path) != str(record["sha256"]).upper():
            raise ValueError("pinned raw-cache evidence input changed")

    prior_runtime = repo_root / CONTINUATION_RUNTIME
    prior_manifest = _read_json(prior_runtime / "CRYPTO_ARTIFACT_MANIFEST.json")
    registry_path = prior_runtime / "CRYPTO_18M_COMPOSITIONAL_FIELD_REGISTRY.json"
    registry_record = next(
        row
        for row in prior_manifest["artifacts"]
        if row["path"].endswith("CRYPTO_18M_COMPOSITIONAL_FIELD_REGISTRY.json")
    )
    if sha256_file(registry_path) != registry_record["sha256"]:
        raise ValueError("committed Broad field registry identity changed")
    registry_payload = _read_json(registry_path)
    rows = registry_payload["fields"]
    if registry_payload.get("field_count") != 39 or {
        str(row["field_id"]) for row in rows
    } != set(field_ids):
        raise ValueError("committed Broad field registry does not match the frozen surface")
    by_id = {str(row["field_id"]): row for row in rows}
    contracts = tuple(
        FieldContract(
            field_id,
            str(by_id[field_id]["value_type"]),
            str(by_id[field_id]["unit"]),
            1,
            "CURRENT_CORE_PACK_ADAPTIVE_ONLY_QUALIFICATION",
        )
        for field_id in sorted(field_ids)
    )
    coverage = field_role_coverage(contracts)
    if not coverage["all_fields_reachable"]:
        raise ValueError("Broad 39 contains a generator-unreachable field")

    store = RawPanelStore.open(cache_root)
    adaptive = store.block_slice(ADAPTIVE_START, ADAPTIVE_END)
    behavior_contract = freeze_search_behavior_contract(
        np.asarray(store.field("active_universe_size")[:, adaptive], dtype=float),
        np.asarray(store.observed()[:, adaptive], dtype=bool),
    )
    identities = {
        "continuation_config": {
            "path": CONTINUATION_CONFIG,
            "sha256": sha256_file(continuation_path),
        },
        "field_surface": field_binding,
        "field_registry": {
            "path": registry_path.relative_to(repo_root).as_posix(),
            "sha256": registry_record["sha256"],
            "logical_sha256": registry_payload["registry_sha256"],
        },
        "raw_cache": {
            "root": cache_root.relative_to(repo_root).as_posix(),
            "identity_sha256": cache_metadata["identity_sha256"],
            "directory_bundle": directory_bundle,
            "panel_context_contract": panel_context,
        },
        "prior_continuation_manifest_bundle_sha256": prior_manifest["bundle_sha256"],
    }
    return store, contracts, behavior_contract, identities, continuation


def _resolve_config_path(repo_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else repo_root / path


def _validate_aggtrades_canary_config(config: Mapping[str, Any]) -> None:
    search = config["search"]
    if config.get("authorization") != (
        "ONE_FRESH_STATE_2000_AGGTRADES_SYSTEM_CANARY"
    ):
        raise ValueError("aggTrades canary authorization changed")
    if int(search["strict_evaluated_target"]) != AGGTRADES_CANARY_STRICT_TARGET:
        raise ValueError("aggTrades canary strict target changed")
    if int(search["checkpoint_size"]) != AGGTRADES_CANARY_CHECKPOINT_SIZE or int(
        search["checkpoint_count"]
    ) != AGGTRADES_CANARY_CHECKPOINT_COUNT:
        raise ValueError("aggTrades canary checkpoint contract changed")
    if {
        str(key): int(value)
        for key, value in search["arms_per_checkpoint"].items()
    } != AGGTRADES_CANARY_CHECKPOINT_ALLOCATION:
        raise ValueError("aggTrades canary arm allocation changed")
    if tuple(int(value) for value in search["seeds"]) != SEEDS:
        raise ValueError("aggTrades canary seed set changed")
    if (
        int(search["workers_default"]) != DEFAULT_WORKERS
        or int(search["workers_memory_fallback"]) != FALLBACK_WORKERS
        or search.get("workers_12_forbidden") is not True
    ):
        raise ValueError("aggTrades canary worker contract changed")
    boundaries = config["boundaries"]
    if (
        boundaries.get("fixed_retrospective_cohort") is not True
        or boundaries.get("system_behavior_only") is not True
        or any(
            bool(boundaries.get(key))
            for key in (
                "alpha_claim",
                "oos",
                "challenge",
                "recent",
                "may_stress",
                "forward",
                "promotion",
                "latent_priority",
                "relational_training",
                "cross_sprint_adaptive_memory",
                "future_arm_qualification",
            )
        )
    ):
        raise ValueError("aggTrades canary research boundary changed")


def _validate_v11_config(config: Mapping[str, Any]) -> None:
    search = config["search"]
    if config.get("authorization") != (
        "ONE_FRESH_STATE_3000_SPENT_DEVELOPMENT_SEARCH_ENGINE_V1_1"
    ):
        raise ValueError("Search Engine V1.1 authorization changed")
    if int(search["strict_evaluated_target"]) != V11_STRICT_TARGET:
        raise ValueError("Search Engine V1.1 strict target changed")
    if (
        int(search["checkpoint_size"]) != V11_CHECKPOINT_SIZE
        or int(search["checkpoint_count"]) != V11_CHECKPOINT_COUNT
    ):
        raise ValueError("Search Engine V1.1 checkpoint contract changed")
    if {
        str(key): int(value)
        for key, value in search["arms_per_checkpoint"].items()
    } != V11_CHECKPOINT_ALLOCATION:
        raise ValueError("Search Engine V1.1 arm allocation changed")
    if tuple(int(value) for value in search["seeds"]) != SEEDS:
        raise ValueError("Search Engine V1.1 seed set changed")
    if (
        int(search["raw_generation_attempt_limit"]) != V11_RAW_ATTEMPT_LIMIT
        or int(search["wall_time_limit_seconds"])
        != V11_WALL_TIME_LIMIT_SECONDS
        or int(search["workers_default"]) != DEFAULT_WORKERS
        or int(search["workers_memory_fallback"]) != FALLBACK_WORKERS
        or search.get("workers_12_forbidden") is not True
        or search.get("fresh_policy_and_archive_state") is not True
        or search.get("every_candidate_requires_aggtrades_input") is not True
    ):
        raise ValueError("Search Engine V1.1 execution contract changed")
    boundaries = config["boundaries"]
    if (
        boundaries.get("fixed_retrospective_cohort") is not True
        or boundaries.get("system_behavior_only") is not True
        or any(
            bool(boundaries.get(key))
            for key in (
                "alpha_claim",
                "oos",
                "challenge",
                "recent",
                "may_stress",
                "forward",
                "promotion",
                "latent_priority",
                "relational_training",
                "cross_sprint_adaptive_memory",
                "future_arm_qualification",
            )
        )
    ):
        raise ValueError("Search Engine V1.1 research boundary changed")


def _validate_v12_config(config: Mapping[str, Any]) -> None:
    search = config["search"]
    if config.get("authorization") != (
        "ONE_FRESH_STATE_2000_SPENT_DEVELOPMENT_SEARCH_ENGINE_V1_2"
    ):
        raise ValueError("Search Engine V1.2 authorization changed")
    if (
        int(search["strict_evaluated_target"]) != V12_STRICT_TARGET
        or int(search["checkpoint_size"]) != V12_CHECKPOINT_SIZE
        or int(search["checkpoint_count"]) != V12_CHECKPOINT_COUNT
    ):
        raise ValueError("Search Engine V1.2 checkpoint contract changed")
    if {
        str(key): int(value)
        for key, value in search["arms_per_checkpoint"].items()
    } != V12_CHECKPOINT_ALLOCATION:
        raise ValueError("Search Engine V1.2 arm allocation changed")
    if tuple(int(value) for value in search["seeds"]) != SEEDS:
        raise ValueError("Search Engine V1.2 seed set changed")
    if (
        int(search["raw_generation_attempt_limit"]) != V12_RAW_ATTEMPT_LIMIT
        or int(search["wall_time_limit_seconds"])
        != V12_WALL_TIME_LIMIT_SECONDS
        or int(search["workers_default"]) != DEFAULT_WORKERS
        or int(search["workers_memory_fallback"]) != FALLBACK_WORKERS
        or search.get("workers_12_forbidden") is not True
        or int(search["balanced_micro_batch_size"])
        != V12_BALANCED_BATCH_SIZE
        or search.get("one_inflight_candidate_per_seed_lane") is not True
        or search.get("rotating_seed_lane_submission_order") is not True
        or search.get("fresh_policy_and_archive_state") is not True
        or search.get("every_candidate_requires_aggtrades_input") is not True
    ):
        raise ValueError("Search Engine V1.2 execution contract changed")
    gate = config["frozen_engineering_gate"]
    if (
        any(
            gate.get(key) is not True
            for key in (
                "strict_per_raw_attempt_above_random",
                "balanced_valid_exact_unique_per_cpu_hour_not_below_random",
                "new_behavior_families_per_cpu_hour_not_below_random",
                "mean_pair_reward_not_below_random",
                "top_decile_pair_reward_not_below_random",
            )
        )
        or not math.isclose(
            float(gate["behavior_duplicate_rate_maximum"]),
            0.03,
            rel_tol=0.0,
            abs_tol=1.0e-12,
        )
    ):
        raise ValueError("Search Engine V1.2 engineering gate changed")
    boundaries = config["boundaries"]
    if (
        boundaries.get("fixed_retrospective_cohort") is not True
        or boundaries.get("system_behavior_only") is not True
        or any(
            bool(boundaries.get(key))
            for key in (
                "alpha_claim",
                "oos",
                "challenge",
                "recent",
                "may_stress",
                "forward",
                "promotion",
                "latent_priority",
                "relational_training",
                "cross_sprint_adaptive_memory",
                "future_arm_qualification",
            )
        )
    ):
        raise ValueError("Search Engine V1.2 research boundary changed")


def build_aggtrades_canary_cache_from_config(
    repo_root: Path, *, source_sha: str
) -> dict[str, Any]:
    config_path = repo_root / AGGTRADES_CANARY_CONFIG
    config = _read_json(config_path)
    _validate_aggtrades_canary_config(config)
    broad_contracts, _, continuation = _broad39_registry_contracts(repo_root)
    inputs = config["inputs"]
    cache = config["cache"]
    metadata = build_aggtrades_system_canary_cache(
        source_cache_root=repo_root / str(continuation["cache_root"]),
        top100_tar=_resolve_config_path(repo_root, str(inputs["top100_tar"])),
        ranks101_200_tar=_resolve_config_path(
            repo_root, str(inputs["ranks101_200_tar"])
        ),
        output_cache_root=repo_root / str(cache["root"]),
        broad_field_ids=[item.field_id for item in broad_contracts],
        start=str(config["window"]["start"]),
        end_exclusive=str(config["window"]["end_exclusive"]),
        producer_source_sha=source_sha,
        verify_tar_sha256=bool(inputs["verify_full_tar_sha256"]),
    )
    expected_hashes = {
        str(_resolve_config_path(repo_root, str(inputs["top100_tar"]))): str(
            inputs["top100_tar_sha256"]
        ).lower(),
        str(
            _resolve_config_path(repo_root, str(inputs["ranks101_200_tar"]))
        ): str(inputs["ranks101_200_tar_sha256"]).lower(),
    }
    source_manifest = _read_json(
        repo_root / str(cache["root"]) / "source_file_manifest.json"
    )
    observed_hashes = {
        str(row["path"]): str(row["declared_sha256"]).lower()
        for row in source_manifest["tars"]
    }
    if observed_hashes != expected_hashes:
        raise ValueError("built canary cache TAR identities differ from frozen config")
    return metadata


def _load_aggtrades_canary_inputs(
    repo_root: Path,
) -> tuple[
    RawPanelStore,
    tuple[FieldContract, ...],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    config_path = repo_root / AGGTRADES_CANARY_CONFIG
    config = _read_json(config_path)
    _validate_aggtrades_canary_config(config)
    broad_contracts, broad_identity, _ = _broad39_registry_contracts(repo_root)
    contracts = tuple((*broad_contracts, *_aggtrades_canary_contracts()))
    if len({item.field_id for item in contracts}) != len(contracts):
        raise ValueError("aggTrades canary field surface has duplicate identities")
    coverage = field_role_coverage(contracts)
    if not coverage["all_fields_reachable"]:
        raise ValueError("aggTrades canary contains a generator-unreachable field")
    cache_root = repo_root / str(config["cache"]["root"])
    metadata = _read_json(cache_root / "metadata.json")
    if metadata.get("cache_role") != (
        "AGGTRADES_FIXED_COHORT_SYSTEM_CANARY_RAW_PANEL_STORE"
    ):
        raise ValueError("aggTrades system canary cache role changed")
    if metadata.get("fixed_retrospective_cohort") is not True:
        raise ValueError("aggTrades canary must disclose its retrospective cohort")
    panel_context = metadata.get("panel_context_contract", {})
    if panel_context.get("authority") != "POST_JOIN_ASSET_BY_TIME_RECOMPUTE":
        raise ValueError("aggTrades canary cache lacks post-join context authority")
    expected_fields = {item.field_id for item in contracts}
    if not expected_fields.issubset(set(metadata.get("field_ids", []))):
        raise ValueError("aggTrades canary cache lacks a frozen searchable field")
    source_manifest = _read_json(cache_root / "source_file_manifest.json")
    expected_tar_hashes = {
        str(
            _resolve_config_path(
                repo_root, str(config["inputs"]["top100_tar"])
            ).resolve()
        ): str(config["inputs"]["top100_tar_sha256"]).lower(),
        str(
            _resolve_config_path(
                repo_root, str(config["inputs"]["ranks101_200_tar"])
            ).resolve()
        ): str(config["inputs"]["ranks101_200_tar_sha256"]).lower(),
    }
    observed_tar_hashes = {
        str(Path(str(row["path"])).resolve()): str(row["declared_sha256"]).lower()
        for row in source_manifest["tars"]
    }
    if observed_tar_hashes != expected_tar_hashes:
        raise ValueError("aggTrades canary cache input identity changed")
    store = RawPanelStore.open(cache_root)
    block = store.block_slice(
        str(config["window"]["start"]), str(config["window"]["end_exclusive"])
    )
    if block.start != 0 or block.stop != store.shape[1]:
        raise ValueError("aggTrades canary cache contains data outside its frozen window")
    behavior_contract = freeze_search_behavior_contract(
        np.asarray(store.field("active_universe_size")[:, block], dtype=float),
        np.asarray(store.observed()[:, block], dtype=bool),
    )
    directory_bundle = _directory_bundle(cache_root)
    identities = {
        **broad_identity,
        "canary_config": {
            "path": AGGTRADES_CANARY_CONFIG,
            "sha256": sha256_file(config_path),
        },
        "aggtrades_field_surface": {
            "field_count": len(AGGTRADES_SYSTEM_CANARY_FIELDS),
            "field_ids": list(AGGTRADES_SYSTEM_CANARY_FIELDS),
            "logical_sha256": _payload_sha(
                [
                    {
                        "field_id": item.field_id,
                        "value_type": item.value_type,
                        "unit": item.unit,
                        "observable_lag_hours": item.observable_lag_hours,
                        "pit_authority": item.pit_authority,
                    }
                    for item in _aggtrades_canary_contracts()
                ]
            ),
        },
        "raw_cache": {
            "root": cache_root.relative_to(repo_root).as_posix(),
            "identity_sha256": metadata["identity_sha256"],
            "directory_bundle": directory_bundle,
            "panel_context_contract": panel_context,
            "source_manifest_sha256": sha256_file(
                cache_root / "source_file_manifest.json"
            ),
        },
    }
    return store, contracts, behavior_contract, identities, config


def _load_v11_inputs(
    repo_root: Path,
) -> tuple[
    RawPanelStore,
    tuple[FieldContract, ...],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    store, contracts, behavior_contract, identities, canary_config = (
        _load_aggtrades_canary_inputs(repo_root)
    )
    config_path = repo_root / V11_CONFIG
    config = _read_json(config_path)
    _validate_v11_config(config)
    for key in ("window", "inputs", "cache"):
        if config.get(key) != canary_config.get(key):
            raise ValueError(
                f"Search Engine V1.1 {key} must reuse the exact canary input carrier"
            )
    identities = {
        **identities,
        "source_canary_config": identities["canary_config"],
        "v11_config": {
            "path": V11_CONFIG,
            "sha256": sha256_file(config_path),
        },
    }
    identities.pop("canary_config", None)
    return store, contracts, behavior_contract, identities, config


def _load_v12_inputs(
    repo_root: Path,
) -> tuple[
    RawPanelStore,
    tuple[FieldContract, ...],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    store, contracts, behavior_contract, identities, canary_config = (
        _load_aggtrades_canary_inputs(repo_root)
    )
    config_path = repo_root / V12_CONFIG
    config = _read_json(config_path)
    _validate_v12_config(config)
    for key in ("inputs", "cache"):
        if config.get(key) != canary_config.get(key):
            raise ValueError(
                f"Search Engine V1.2 {key} must reuse the exact canary input carrier"
            )
    if {
        key: config["window"].get(key) for key in ("start", "end_exclusive")
    } != {
        key: canary_config["window"].get(key)
        for key in ("start", "end_exclusive")
    }:
        raise ValueError(
            "Search Engine V1.2 window must reuse the exact canary input carrier"
        )
    identities = {
        **identities,
        "source_canary_config": identities["canary_config"],
        "v12_config": {
            "path": V12_CONFIG,
            "sha256": sha256_file(config_path),
        },
    }
    identities.pop("canary_config", None)
    return store, contracts, behavior_contract, identities, config


def _load_carrier_gate_inputs(
    repo_root: Path, carrier_id: str
) -> tuple[
    RawPanelStore,
    tuple[FieldContract, ...],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    if carrier_id not in CARRIER_GATE_IDS:
        raise ValueError(f"unsupported carrier gate identity: {carrier_id}")
    config_path = repo_root / CARRIER_GATE_CONFIG
    config = _read_json(config_path)
    if tuple(config["carriers"]) != CARRIER_GATE_IDS:
        raise ValueError("carrier gate identities changed")
    manifest_path = repo_root / str(config["source_carrier_manifest"])
    store, contracts, loader_evidence = load_search_surface_carrier(
        repo_root,
        carrier_manifest_path=manifest_path,
        surface_id=carrier_id,
    )
    surface = field_role_surface(contracts)
    if not surface["compatible_skeleton_ids"] or not surface["all_fields_reachable"]:
        raise ValueError("carrier gate has an unreachable field or no compatible skeleton")
    base = np.asarray(store.base_eligible(), dtype=bool)
    counts = base.sum(axis=0, dtype=np.int64).astype(float)
    regime = np.broadcast_to(counts, base.shape).copy()
    regime[~base] = np.nan
    behavior_contract = freeze_search_behavior_contract(
        regime,
        base,
        pit_regime_source="__BASE_ELIGIBLE_COUNT__",
    )
    metadata = _read_json(
        repo_root
        / str(
            _read_json(manifest_path)["carriers"][carrier_id]["cache_root"]
        )
        / "metadata.json"
    )
    identities = {
        "carrier_gate_config": {
            "path": CARRIER_GATE_CONFIG,
            "sha256": sha256_file(config_path),
        },
        "source_carrier_manifest": {
            "path": str(config["source_carrier_manifest"]),
            "sha256": sha256_file(manifest_path),
        },
        "carrier": {
            "carrier_id": carrier_id,
            "cache_identity_sha256": metadata["identity_sha256"],
            "contracts_sha256": _payload_sha(_contracts_payload(contracts)),
            "loader_evidence": loader_evidence,
        },
        "raw_cache": {
            "root": str(
                _read_json(manifest_path)["carriers"][carrier_id]["cache_root"]
            ),
            "identity_sha256": metadata["identity_sha256"],
        },
    }
    local_config = {
        **config,
        "carrier_id": carrier_id,
        "window": {
            "start": metadata["start_utc"],
            "end_exclusive": metadata["end_exclusive_utc"],
        },
        "cache": identities["raw_cache"],
    }
    return store, contracts, behavior_contract, identities, local_config


def _frozen_contract(
    *,
    source_sha: str,
    compiler_binding: Mapping[str, Any],
    behavior_contract: Mapping[str, Any],
    input_identities: Mapping[str, Any],
    environment: Mapping[str, Any],
) -> dict[str, Any]:
    payload = {
        "schema_version": 2,
        "epoch_id": EPOCH_ID,
        "source_sha": source_sha,
        "base_sha": BASE_SHA,
        "objective": "Compare rolling proposal productivity on the spent-development Broad 39 surface",
        "authorization": "ONE_20000_STRICT_BROAD39_DEVELOPMENT_ARENA",
        "surface": {
            "context_id": "BROAD_PANEL_BASELINE",
            "fields": 39,
            "core3_fields": 0,
            "joint_120_channel_panel": False,
        },
        "input_identities": dict(input_identities),
        "compiler_identity": dict(compiler_binding),
        "evaluator_contract": pair_contract_payload(),
        "behavior_descriptor": dict(behavior_contract),
        "environment": dict(environment),
        "seeds": list(SEEDS),
        "arm_contract": {
            "checkpoint_000": {arm: 400 for arm in FIRST_CHECKPOINT_ARMS},
            "rolling_default": {
                "canonical_typed_random": 0.20,
                "hierarchical_typed_cem_v2": 0.40,
                "typed_evolution_v2": 0.40,
            },
            "diagnostic_floor": 0.10,
            "typed_random_minimum": 0.20,
            "same_seed_set_for_every_arm": True,
            "reward_comparison": "same first N by deterministic candidate completion ordinal",
        },
        "v1_controls": {
            "fresh_state": True,
            "old_candidate_import": False,
            "old_reward_import": False,
            "old_distribution_import": False,
            "old_population_import": False,
            "old_policy_state_import": False,
            "exit_after_checkpoint_000": True,
            "parameters": dict(V1_PARAMETERS),
        },
        "v2_parameters": dict(V2_PARAMETERS),
        "cem": {
            "sample_order": [
                "mechanism_family",
                "skeleton_variant",
                "typed_roles",
                "field_families",
                "field_tokens",
                "windows_and_normalizers",
                "horizon",
            ],
            "operator_sampling": False,
            "interaction_sampling": False,
            "fallback": [
                "exact_condition",
                "typed_role_plus_field_family",
                "skeleton_variant",
                "mechanism_family",
                "global_legal_domain_filtered_by_typed_role",
            ],
        },
        "elite_authority": {
            "admission_hard_gates": [
                "compile_valid",
                "exact_unique",
                "matched_control_valid",
                "strict_cost_evaluated",
            ],
            "only_ordering_authority": "pair_reward",
            "equal_reward_tie_break": [
                "arm_seed_policy_local_behavior_family_count",
                "candidate_id",
            ],
            "diagnostic_only": [
                "turnover",
                "gross_positive_cost_sign_killed",
                "cost_threshold_violated",
                "turnover_threshold_violated",
                "failure_layer",
                "behavior_novelty_except_equal_reward",
            ],
        },
        "evolution": {
            "genome": "existing CandidateSpec generation_genes",
            "mutation": "1_to_3_effective_genes",
            "operator_replacement": "compatible_skeleton_variant_mutation",
            "crossover": "one_point_effective_homologous_gene_bundle_typed_role_compatible",
            "mechanism_cell_limit": int(
                V2_PARAMETERS["typed_evolution_v2"]["mechanism_cell_limit"]
            ),
            "free_string_mutation": False,
            "new_ast": False,
        },
        "representation_contract": {
            "field_family_normalizer_whitelist": True,
            "typed_role_window_whitelist": True,
            "sample_effective_genes_only": True,
        },
        "qualification_gate": {
            "engineering_execution_separate_from_search_strategy": True,
            "reward_mean_and_top_decile_must_not_be_worse": True,
            "productivity_must_clearly_improve": True,
            "cross_seed_required": True,
            "consecutive_checkpoints_required": 2,
            "frozen_tolerance": QUALIFICATION_TOLERANCE,
            "behavior_duplicate_rate_maximum": QUALIFICATION_DUPLICATE_RATE_MAXIMUM,
        },
        "budget": {
            "strict_evaluated_target": STRICT_TARGET,
            "raw_generation_attempts_maximum": RAW_ATTEMPT_LIMIT,
            "fail_closed_attempt_reservation_per_proposal": MAX_SINGLE_PROPOSAL_RAW_ATTEMPTS,
            "wall_time_seconds_maximum": WALL_TIME_LIMIT_SECONDS,
            "checkpoint_size": CHECKPOINT_SIZE,
            "checkpoint_count": CHECKPOINT_COUNT,
            "workers_default": DEFAULT_WORKERS,
            "workers_memory_fallback": FALLBACK_WORKERS,
            "workers_12_forbidden": True,
        },
        "cpu_hour_definition": "sum process CPU seconds for proposal, compile, archive, and pair evaluation; excludes queue and human wait",
        "memory": "CAMPAIGN_LOCAL_PER_RUN_MEMORY",
        "latent_status": "LATENT_SEARCH_PRIORITY_MODEL_DEFERRED_TO_V1_1",
        "relational_status": "STAGE1_CLOSED_READ_ONLY_BRIDGES_ONLY",
        "boundaries": {
            "sealed_reads": 0,
            "report_only_feedback": False,
            "challenge": False,
            "recent": False,
            "may_stress": False,
            "forward": False,
            "promotion": False,
            "cross_sprint_adaptive_memory": False,
        },
    }
    return {**payload, "frozen_contract_sha256": _payload_sha(payload)}


def _aggtrades_canary_frozen_contract(
    *,
    source_sha: str,
    compiler_binding: Mapping[str, Any],
    behavior_contract: Mapping[str, Any],
    input_identities: Mapping[str, Any],
    environment: Mapping[str, Any],
    config: Mapping[str, Any],
) -> dict[str, Any]:
    payload = {
        "schema_version": 1,
        "epoch_id": AGGTRADES_CANARY_EPOCH_ID,
        "experiment_id": str(config["experiment_id"]),
        "source_sha": source_sha,
        "objective": (
            "Exercise Search Engine V1 proposal productivity, behavior discovery, "
            "and exact checkpoint restoration on a newly materialized aggTrades "
            "field family"
        ),
        "authorization": "ONE_FRESH_STATE_2000_AGGTRADES_SYSTEM_CANARY",
        "evidence_role": "DEVELOPMENT_DIAGNOSTIC_FIXED_RETROSPECTIVE_COHORT",
        "input_identities": dict(input_identities),
        "compiler_identity": dict(compiler_binding),
        "evaluator_contract": pair_contract_payload(),
        "behavior_descriptor": dict(behavior_contract),
        "environment": dict(environment),
        "window": dict(config["window"]),
        "surface": {
            "broad_context_fields": 39,
            "aggtrades_fields": len(AGGTRADES_SYSTEM_CANARY_FIELDS),
            "aggtrades_field_ids": list(AGGTRADES_SYSTEM_CANARY_FIELDS),
            "every_candidate_requires_aggtrades_input": True,
            "fixed_retrospective_cohort": True,
            "missing_value_fill": None,
        },
        "seeds": list(SEEDS),
        "arms": {
            "active": list(AGGTRADES_CANARY_ARMS),
            "checkpoint_allocation": dict(AGGTRADES_CANARY_CHECKPOINT_ALLOCATION),
            "same_seed_set_for_every_arm": True,
            "reward_comparison": (
                "same first N by deterministic arm completion ordinal"
            ),
        },
        "fresh_state": {
            "old_candidate_import": False,
            "old_reward_import": False,
            "old_distribution_import": False,
            "old_population_import": False,
            "old_policy_state_import": False,
            "old_archive_import": False,
        },
        "policies": {
            "canonical_typed_random": dict(
                V1_PARAMETERS["canonical_typed_random"]
            ),
            "hierarchical_typed_cem_v2": dict(
                V2_PARAMETERS["hierarchical_typed_cem_v2"]
            ),
            "typed_evolution_v2": dict(
                V2_PARAMETERS["typed_evolution_v2"]
            ),
        },
        "elite_authority": {
            "only_ordering_authority": "pair_reward",
            "equal_reward_tie_break": [
                "arm_seed_policy_local_behavior_family_count",
                "candidate_id",
            ],
            "diagnostic_only": [
                "turnover",
                "cost_killed",
                "failure_layer",
                "behavior_novelty_except_equal_reward",
            ],
        },
        "budget": {
            "strict_evaluated_target": AGGTRADES_CANARY_STRICT_TARGET,
            "raw_generation_attempts_maximum": AGGTRADES_CANARY_RAW_ATTEMPT_LIMIT,
            "fail_closed_attempt_reservation_per_proposal": (
                MAX_SINGLE_PROPOSAL_RAW_ATTEMPTS
            ),
            "wall_time_seconds_maximum": (
                AGGTRADES_CANARY_WALL_TIME_LIMIT_SECONDS
            ),
            "checkpoint_size": AGGTRADES_CANARY_CHECKPOINT_SIZE,
            "checkpoint_count": AGGTRADES_CANARY_CHECKPOINT_COUNT,
            "workers_default": DEFAULT_WORKERS,
            "workers_memory_fallback": FALLBACK_WORKERS,
            "workers_12_forbidden": True,
        },
        "decision_authority": {
            "system_behavior_only": True,
            "alpha_discovery_claim": False,
            "future_arm_qualification": False,
            "data_admission_promotion": False,
        },
        "cpu_hour_definition": (
            "sum process CPU seconds for proposal, compile, archive, and pair "
            "evaluation; excludes queue and human wait"
        ),
        "memory": "CAMPAIGN_LOCAL_PER_RUN_MEMORY",
        "boundaries": {
            "sealed_reads": 0,
            "challenge": False,
            "recent": False,
            "may_stress": False,
            "forward": False,
            "promotion": False,
            "cross_sprint_adaptive_memory": False,
            "latent_priority": False,
            "relational_training": False,
        },
    }
    return {**payload, "frozen_contract_sha256": _payload_sha(payload)}


def _v11_frozen_contract(
    *,
    source_sha: str,
    compiler_binding: Mapping[str, Any],
    behavior_contract: Mapping[str, Any],
    input_identities: Mapping[str, Any],
    environment: Mapping[str, Any],
    config: Mapping[str, Any],
) -> dict[str, Any]:
    payload = {
        "schema_version": 1,
        "epoch_id": V11_EPOCH_ID,
        "experiment_id": str(config["experiment_id"]),
        "source_sha": source_sha,
        "objective": (
            "Compare behavior-niched CEM and Evolution against equal-count "
            "typed random on the fixed spent-development aggTrades carrier"
        ),
        "authorization": (
            "ONE_FRESH_STATE_3000_SPENT_DEVELOPMENT_SEARCH_ENGINE_V1_1"
        ),
        "evidence_role": "SYSTEM_SEARCH_CAPABILITY_ONLY_SPENT_DEVELOPMENT",
        "input_identities": dict(input_identities),
        "compiler_identity": dict(compiler_binding),
        "evaluator_contract": pair_contract_payload(),
        "behavior_descriptor": dict(behavior_contract),
        "environment": dict(environment),
        "window": dict(config["window"]),
        "surface": {
            "broad_context_fields": 39,
            "aggtrades_fields": len(AGGTRADES_SYSTEM_CANARY_FIELDS),
            "aggtrades_field_ids": list(AGGTRADES_SYSTEM_CANARY_FIELDS),
            "every_candidate_requires_aggtrades_input": True,
            "fixed_retrospective_cohort": True,
            "missing_value_fill": None,
            "input_carrier_reused_without_rebuild": True,
        },
        "seeds": list(SEEDS),
        "arms": {
            "active": list(V11_ARMS),
            "checkpoint_allocation": dict(V11_CHECKPOINT_ALLOCATION),
            "same_seed_set_for_every_arm": True,
            "reward_comparison": (
                "same first N by deterministic arm completion ordinal"
            ),
        },
        "fresh_state": {
            "old_candidate_import": False,
            "old_reward_import": False,
            "old_distribution_import": False,
            "old_population_import": False,
            "old_policy_state_import": False,
            "old_archive_import": False,
        },
        "policies": {
            "canonical_typed_random": dict(
                V1_PARAMETERS["canonical_typed_random"]
            ),
            **{
                key: dict(value)
                for key, value in V21_PARAMETERS.items()
            },
        },
        "search_capability_delta": {
            "cem": {
                "family_champion_elite_admission": True,
                "mechanism_stratified_elite_frontier": True,
                "skeleton_stratified_elite_frontier": True,
                "only_ordering_authority": "pair_reward",
            },
            "evolution": {
                "one_population_champion_per_behavior_family": True,
                "bounded_skeleton_cells": True,
                "cross_skeleton_crossover_preferred_when_compatible": True,
                "checkpoint_operator_family_productivity_update": True,
                "operator_probability_floor": float(
                    V21_PARAMETERS["behavior_niched_evolution_v2_1"][
                        "operator_productivity_floor"
                    ]
                ),
                "parent_tournament_authority": "pair_reward",
            },
            "new_ast": False,
            "new_compiler": False,
            "new_evaluator": False,
            "new_scheduler": False,
        },
        "elite_authority": {
            "only_ordering_authority": "pair_reward",
            "niche_admission": [
                "behavior_family_champion",
                "mechanism_family_frontier",
                "skeleton_variant_frontier",
            ],
            "equal_reward_tie_break": [
                "arm_seed_policy_local_behavior_family_count",
                "candidate_id",
            ],
            "diagnostic_only": [
                "turnover",
                "cost_killed",
                "failure_layer",
            ],
        },
        "budget": {
            "strict_evaluated_target": V11_STRICT_TARGET,
            "raw_generation_attempts_maximum": V11_RAW_ATTEMPT_LIMIT,
            "fail_closed_attempt_reservation_per_proposal": (
                MAX_SINGLE_PROPOSAL_RAW_ATTEMPTS
            ),
            "wall_time_seconds_maximum": V11_WALL_TIME_LIMIT_SECONDS,
            "checkpoint_size": V11_CHECKPOINT_SIZE,
            "checkpoint_count": V11_CHECKPOINT_COUNT,
            "workers_default": DEFAULT_WORKERS,
            "workers_memory_fallback": FALLBACK_WORKERS,
            "workers_12_forbidden": True,
        },
        "decision_authority": {
            "system_behavior_only": True,
            "alpha_discovery_claim": False,
            "future_arm_qualification": False,
            "data_admission_promotion": False,
        },
        "cpu_hour_definition": (
            "sum process CPU seconds for proposal, compile, archive, and pair "
            "evaluation; excludes queue and human wait"
        ),
        "memory": "CAMPAIGN_LOCAL_PER_RUN_MEMORY",
        "boundaries": {
            "sealed_reads": 0,
            "challenge": False,
            "recent": False,
            "may_stress": False,
            "forward": False,
            "promotion": False,
            "cross_sprint_adaptive_memory": False,
            "latent_priority": False,
            "relational_training": False,
        },
    }
    return {**payload, "frozen_contract_sha256": _payload_sha(payload)}


def _v12_frozen_contract(
    *,
    source_sha: str,
    compiler_binding: Mapping[str, Any],
    behavior_contract: Mapping[str, Any],
    input_identities: Mapping[str, Any],
    environment: Mapping[str, Any],
    config: Mapping[str, Any],
) -> dict[str, Any]:
    payload = {
        "schema_version": 1,
        "epoch_id": V12_EPOCH_ID,
        "experiment_id": str(config["experiment_id"]),
        "source_sha": source_sha,
        "objective": str(config["objective"]),
        "authorization": str(config["authorization"]),
        "evidence_role": "SYSTEM_SEARCH_CAPABILITY_ONLY_SPENT_DEVELOPMENT",
        "input_identities": dict(input_identities),
        "compiler_identity": dict(compiler_binding),
        "evaluator_contract": pair_contract_payload(),
        "behavior_descriptor": dict(behavior_contract),
        "environment": dict(environment),
        "window": dict(config["window"]),
        "surface": {
            "broad_context_fields": 39,
            "aggtrades_fields": len(AGGTRADES_SYSTEM_CANARY_FIELDS),
            "aggtrades_field_ids": list(AGGTRADES_SYSTEM_CANARY_FIELDS),
            "every_candidate_requires_aggtrades_input": True,
            "fixed_retrospective_cohort": True,
            "input_carrier_reused_without_rebuild": True,
        },
        "seeds": list(SEEDS),
        "arms": {
            "active": list(V12_ARMS),
            "checkpoint_allocation": dict(V12_CHECKPOINT_ALLOCATION),
            "same_seed_set_for_every_arm": True,
            "reward_comparison": (
                "same first N by deterministic arm completion ordinal"
            ),
        },
        "fresh_state": {
            "old_candidate_import": False,
            "old_reward_import": False,
            "old_distribution_import": False,
            "old_population_import": False,
            "old_policy_state_import": False,
            "old_archive_import": False,
            "old_transition_collision_memory_import": False,
        },
        "policies": {
            "canonical_typed_random": dict(
                V1_PARAMETERS["canonical_typed_random"]
            ),
            "collision_controlled_evolution_v2_2": dict(
                V22_PARAMETERS["collision_controlled_evolution_v2_2"]
            ),
        },
        "search_capability_delta": {
            "existing_lane_scheduler_balanced": True,
            "balanced_micro_batch_size": V12_BALANCED_BATCH_SIZE,
            "one_inflight_candidate_per_seed_lane": True,
            "rotating_seed_lane_submission_order": True,
            "matched_batch_cpu_authority": True,
            "campaign_local_transition_collision_control": True,
            "transition_key": [
                "parent_behavior_family_id",
                "source_skeleton_id",
                "target_skeleton_id",
                "remapped_genome_sha256",
            ],
            "block_after_collisions": int(
                V22_PARAMETERS["collision_controlled_evolution_v2_2"][
                    "transition_block_after_collisions"
                ]
            ),
            "new_ast": False,
            "new_compiler": False,
            "new_evaluator": False,
            "new_scheduler_system": False,
        },
        "budget": {
            "strict_evaluated_target": V12_STRICT_TARGET,
            "raw_generation_attempts_maximum": V12_RAW_ATTEMPT_LIMIT,
            "fail_closed_attempt_reservation_per_proposal": (
                MAX_SINGLE_PROPOSAL_RAW_ATTEMPTS
            ),
            "wall_time_seconds_maximum": V12_WALL_TIME_LIMIT_SECONDS,
            "checkpoint_size": V12_CHECKPOINT_SIZE,
            "checkpoint_count": V12_CHECKPOINT_COUNT,
            "workers_default": DEFAULT_WORKERS,
            "workers_memory_fallback": FALLBACK_WORKERS,
            "workers_12_forbidden": True,
        },
        "frozen_engineering_gate": dict(config["frozen_engineering_gate"]),
        "decision_authority": {
            "system_behavior_only": True,
            "alpha_discovery_claim": False,
            "future_arm_qualification": False,
            "data_admission_promotion": False,
        },
        "cpu_hour_definition": (
            "sum process CPU seconds for proposal, compile, archive, and pair "
            "evaluation inside full balanced matched micro-batches; excludes "
            "queue and human wait"
        ),
        "memory": "CAMPAIGN_LOCAL_PER_RUN_MEMORY",
        "boundaries": {
            "sealed_reads": 0,
            "challenge": False,
            "recent": False,
            "may_stress": False,
            "forward": False,
            "promotion": False,
            "cross_sprint_adaptive_memory": False,
            "latent_priority": False,
            "relational_training": False,
        },
    }
    return {**payload, "frozen_contract_sha256": _payload_sha(payload)}


def _carrier_gate_frozen_contract(
    *,
    source_sha: str,
    compiler_binding: Mapping[str, Any],
    behavior_contract: Mapping[str, Any],
    input_identities: Mapping[str, Any],
    environment: Mapping[str, Any],
    config: Mapping[str, Any],
    contracts: Sequence[FieldContract],
) -> dict[str, Any]:
    surface = field_role_surface(contracts)
    payload = {
        "schema_version": 1,
        "epoch_id": CARRIER_GATE_EPOCH_ID,
        "experiment_id": str(config["experiment_id"]),
        "source_sha": source_sha,
        "authorization": str(config["authorization"]),
        "carrier_id": str(config["carrier_id"]),
        "input_identities": dict(input_identities),
        "compiler_identity": dict(compiler_binding),
        "evaluator_contract": pair_contract_payload(),
        "behavior_descriptor": dict(behavior_contract),
        "environment": dict(environment),
        "window": dict(config["window"]),
        "surface": {
            "field_count": len(contracts),
            "field_ids": [item.field_id for item in contracts],
            "compatible_skeleton_ids": surface["compatible_skeleton_ids"],
            "contexts_merged": False,
        },
        "seeds": list(SEEDS),
        "arms": {
            "active": list(CARRIER_GATE_ARMS),
            "checkpoint_allocation": dict(CARRIER_GATE_CHECKPOINT_ALLOCATION),
            "same_seed_set_for_every_arm": True,
        },
        "fresh_state": {
            "old_candidate_import": False,
            "old_reward_import": False,
            "old_distribution_import": False,
            "old_population_import": False,
            "old_policy_state_import": False,
            "old_archive_import": False,
            "old_transition_memory_import": False,
        },
        "authority_repairs": dict(config["authority_repairs"]),
        "budget": {
            "strict_evaluated_target": CARRIER_GATE_STRICT_TARGET,
            "checkpoint_size": CARRIER_GATE_CHECKPOINT_SIZE,
            "checkpoint_count": CARRIER_GATE_CHECKPOINT_COUNT,
            "raw_generation_attempts_maximum": CARRIER_GATE_RAW_ATTEMPT_LIMIT,
            "wall_time_seconds_maximum": CARRIER_GATE_WALL_TIME_LIMIT_SECONDS,
            "workers_default": DEFAULT_WORKERS,
            "workers_memory_fallback": FALLBACK_WORKERS,
            "workers_12_forbidden": True,
        },
        "memory": "CAMPAIGN_LOCAL_PER_RUN_MEMORY_ARM_AND_SEED_LOCAL",
        "boundaries": {**dict(config["boundaries"]), "sealed_reads": 0},
    }
    return {**payload, "frozen_contract_sha256": _payload_sha(payload)}


@dataclass(slots=True)
class BehaviorArchive:
    rows: list[dict[str, Any]] = field(default_factory=list)
    champion_by_family: dict[str, int] = field(default_factory=dict)
    family_counts: Counter[str] = field(default_factory=Counter)
    duplicate_replacements: int = 0
    transition_productivity: dict[str, dict[str, int]] = field(default_factory=dict)
    blocked_transition_keys: set[str] = field(default_factory=set)
    blocked_transition_skips: int = 0

    def observe(
        self,
        *,
        candidate: CandidateSpec,
        evaluation: Mapping[str, Any],
        arm: str,
        seed: int,
        completion_ordinal: int,
        checkpoint_index: int,
    ) -> tuple[dict[str, Any], bool]:
        behavior = dict(evaluation.get("behavior") or {})
        family_id = str(behavior.get("behavior_family_id", ""))
        if not family_id:
            raise ValueError("strict candidate lacks a behavior family identity")
        new_family = family_id not in self.champion_by_family
        row = {
            "exact_expression_id": candidate.candidate_id,
            "canonical_expression_id": candidate.expression.expression_id,
            "behavior_family_id": family_id,
            "arm": arm,
            "seed": int(seed),
            "completion_ordinal": int(completion_ordinal),
            "checkpoint_index": int(checkpoint_index),
            "pair_reward": float(evaluation["pair_reward"]),
            "matched_positive": bool(evaluation["matched_positive"]),
            "gross_mean_annotation": evaluation["incremental"].get("gross_mean"),
            "net_mean_annotation": evaluation["incremental"].get("net_mean"),
            "cost_mean_annotation": evaluation["incremental"].get("cost_mean"),
            "is_family_champion": False,
            **behavior,
        }
        new_index = len(self.rows)
        self.rows.append(row)
        self.family_counts[family_id] += 1
        old_index = self.champion_by_family.get(family_id)
        replace = old_index is None
        if old_index is not None:
            old = self.rows[old_index]
            replace = (
                float(row["pair_reward"]) > float(old["pair_reward"])
                or (
                    float(row["pair_reward"]) == float(old["pair_reward"])
                    and str(row["exact_expression_id"])
                    < str(old["exact_expression_id"])
                )
            )
        if replace:
            if old_index is not None:
                self.rows[old_index]["is_family_champion"] = False
                self.duplicate_replacements += 1
            self.rows[new_index]["is_family_champion"] = True
            self.champion_by_family[family_id] = new_index
        return self.rows[new_index], new_family

    def summary_rows(self) -> list[dict[str, Any]]:
        output = []
        for family_id, index in sorted(self.champion_by_family.items()):
            champion = self.rows[index]
            output.append(
                {
                    "behavior_family_id": family_id,
                    "members": int(self.family_counts[family_id]),
                    "champion_exact_expression_id": champion["exact_expression_id"],
                    "champion_arm": champion["arm"],
                    "champion_pair_reward": champion["pair_reward"],
                    "champion_matched_positive": champion["matched_positive"],
                }
            )
        return output

    def observe_transition(
        self,
        *,
        transition_key: str,
        new_family: bool,
        block_after_collisions: int,
    ) -> None:
        if not transition_key:
            raise ValueError("campaign transition observation lacks a key")
        stats = self.transition_productivity.setdefault(
            str(transition_key),
            {"trials": 0, "new_families": 0, "collisions": 0},
        )
        stats["trials"] += 1
        stats["new_families"] += int(bool(new_family))
        stats["collisions"] += int(not new_family)
        if int(stats["collisions"]) >= int(block_after_collisions):
            self.blocked_transition_keys.add(str(transition_key))

    def transition_state(self) -> dict[str, Any]:
        return {
            "transition_productivity": {
                key: dict(stats)
                for key, stats in sorted(self.transition_productivity.items())
            },
            "blocked_transition_keys": sorted(self.blocked_transition_keys),
            "blocked_transition_skips": int(self.blocked_transition_skips),
        }

    def restore_transition_state(self, state: Mapping[str, Any]) -> None:
        self.transition_productivity = {
            str(key): {
                "trials": int(stats.get("trials", 0)),
                "new_families": int(stats.get("new_families", 0)),
                "collisions": int(stats.get("collisions", 0)),
            }
            for key, stats in state.get("transition_productivity", {}).items()
        }
        self.blocked_transition_keys = set(
            str(value) for value in state.get("blocked_transition_keys", ())
        )
        self.blocked_transition_skips = int(
            state.get("blocked_transition_skips", 0)
        )

    def state_hash(self) -> str:
        payload = {
            "families": self.summary_rows(),
            "rows": len(self.rows),
            "duplicate_replacements": self.duplicate_replacements,
        }
        if (
            self.transition_productivity
            or self.blocked_transition_keys
            or self.blocked_transition_skips
        ):
            payload["transition_state"] = self.transition_state()
        return _payload_sha(payload)

    @classmethod
    def from_rows(cls, rows: Sequence[Mapping[str, Any]]) -> "BehaviorArchive":
        archive = cls(rows=[dict(row) for row in rows])
        for index, row in enumerate(archive.rows):
            family_id = str(row["behavior_family_id"])
            archive.family_counts[family_id] += 1
            if bool(row["is_family_champion"]):
                if family_id in archive.champion_by_family:
                    raise ValueError("behavior archive has multiple family champions")
                archive.champion_by_family[family_id] = index
        if len(archive.champion_by_family) != len(archive.family_counts):
            raise ValueError("behavior archive family lacks a champion")
        return archive


@dataclass(slots=True)
class HierarchicalTypedCEMV2:
    seed: int
    registry: TypedExpressionRegistry
    parameters: Mapping[str, Any] = field(
        default_factory=lambda: dict(V2_PARAMETERS["hierarchical_typed_cem_v2"])
    )
    rng: random.Random = field(init=False)
    roles: dict[str, list[str]] = field(init=False)
    compatible_skeleton_ids: tuple[str, ...] = field(init=False)
    seen: set[str] = field(default_factory=set)
    tables: dict[str, dict[str, dict[str, Any]]] = field(
        default_factory=lambda: defaultdict(dict)
    )
    update_count: int = 0
    step: int = 0
    last_elite_family_count: int = 0
    last_elite_mechanism_count: int = 0
    last_elite_skeleton_count: int = 0

    def __post_init__(self) -> None:
        self.parameters = dict(self.parameters)
        self.rng = random.Random(int(self.seed))
        surface = field_role_surface(tuple(self.registry.fields.values()))
        self.roles = {
            str(key): [str(value) for value in values]
            for key, values in surface["roles"].items()
        }
        self.compatible_skeleton_ids = tuple(surface["compatible_skeleton_ids"])
        if not self.compatible_skeleton_ids:
            raise ValueError("CEM V2 carrier has no compatible skeleton")
        if not 0.0 < float(self.parameters["smoothing"]) <= 1.0:
            raise ValueError("CEM V2 smoothing is invalid")
        if int(self.parameters["minimum_observation_count"]) < 1:
            raise ValueError("CEM V2 minimum observation count is invalid")
        if not 0.0 <= float(self.parameters["entropy_floor_ratio"]) <= 1.0:
            raise ValueError("CEM V2 entropy floor is invalid")

    @staticmethod
    def _entropy(probabilities: Sequence[float]) -> float:
        return float(
            -sum(value * math.log(value) for value in probabilities if value > 0.0)
        )

    def _regularized(
        self, values: Sequence[Any], weights: Mapping[str, float]
    ) -> dict[str, float]:
        ordered = tuple(sorted(values, key=lambda value: str(value)))
        if not ordered:
            raise ValueError("CEM V2 received an empty legal domain")
        if len(ordered) == 1:
            return {str(ordered[0]): 1.0}
        floor = float(self.parameters["minimum_probability"])
        if floor * len(ordered) >= 1.0:
            raise ValueError("CEM V2 minimum probability exceeds the legal support")
        raw = np.asarray(
            [max(0.0, float(weights.get(str(value), 0.0))) for value in ordered],
            dtype=float,
        )
        if not np.any(raw > 0.0):
            raw = np.ones(len(ordered), dtype=float)
        raw /= float(raw.sum())
        probabilities = floor + (1.0 - floor * len(ordered)) * raw
        entropy_floor = float(self.parameters["entropy_floor_ratio"]) * math.log(
            len(ordered)
        )
        uniform = np.full(len(ordered), 1.0 / len(ordered), dtype=float)
        if self._entropy(probabilities.tolist()) < entropy_floor:
            for index in range(1, 51):
                mixture = index / 50.0
                candidate = (1.0 - mixture) * probabilities + mixture * uniform
                if self._entropy(candidate.tolist()) >= entropy_floor:
                    probabilities = candidate
                    break
        return {
            str(value): float(probability)
            for value, probability in zip(ordered, probabilities.tolist())
        }

    def _table_weights(
        self, axis: str, context: str, legal_values: Sequence[Any]
    ) -> dict[str, float] | None:
        table = self.tables.get(axis, {}).get(context)
        if table is None or int(table.get("observations", 0)) < int(
            self.parameters["minimum_observation_count"]
        ):
            return None
        return self._regularized(legal_values, table.get("probabilities", {}))

    def _choice(
        self,
        axis: str,
        legal_values: Sequence[Any],
        contexts: Sequence[str],
        *,
        role_family_contexts: Mapping[Any, str] | None = None,
    ) -> Any:
        ordered = tuple(sorted(legal_values, key=lambda value: str(value)))
        probabilities: dict[str, float] | None = None
        if contexts:
            probabilities = self._table_weights(axis, contexts[0], ordered)
        if probabilities is None and role_family_contexts:
            counts: dict[str, float] = {}
            observations = 0
            for value in ordered:
                table = self.tables.get(axis, {}).get(
                    role_family_contexts.get(value, "")
                )
                if table is None:
                    continue
                count = int(table.get("observations", 0))
                if count:
                    counts[str(value)] = float(count)
                    observations += count
            if observations >= int(self.parameters["minimum_observation_count"]):
                probabilities = self._regularized(ordered, counts)
        if probabilities is None:
            for context in contexts[1:]:
                probabilities = self._table_weights(axis, context, ordered)
                if probabilities is not None:
                    break
        if probabilities is None:
            probabilities = self._regularized(
                ordered, {str(value): 1.0 for value in ordered}
            )
        return self.rng.choices(
            ordered,
            weights=[probabilities[str(value)] for value in ordered],
            k=1,
        )[0]

    def _sample_candidate(self) -> CandidateSpec:
        compatible = tuple(
            item
            for item in skeleton_registry()
            if item.skeleton_id in self.compatible_skeleton_ids
        )
        mechanisms = tuple(sorted({item.mechanism_family for item in compatible}))
        mechanism = str(self._choice("mechanism_family", mechanisms, ("G",)))
        skeleton_ids = tuple(
            item.skeleton_id
            for item in compatible
            if item.mechanism_family == mechanism
        )
        skeleton = _skeleton_by_id(
            str(
                self._choice(
                    "skeleton_variant",
                    skeleton_ids,
                    (f"E|{mechanism}", "G"),
                )
            )
        )
        left_role, right_role = skeleton.field_roles

        selected: dict[str, Any] = {}
        for side, role in (("left", left_role), ("right", right_role)):
            families = _family_fields(self.roles, role)
            family = str(
                self._choice(
                    "field_family",
                    tuple(families),
                    (
                        f"E|{role}|{skeleton.skeleton_id}",
                        f"S|{skeleton.skeleton_id}",
                        f"M|{mechanism}",
                        f"G|{role}",
                    ),
                    role_family_contexts={
                        value: f"RF|{role}|{value}" for value in families
                    },
                )
            )
            fields = list(families[family])
            if side == "right" and selected.get("left_field") in fields and len(fields) > 1:
                fields.remove(selected["left_field"])
            selected[f"{side}_field"] = str(
                self._choice(
                    "field_token",
                    fields,
                    (
                        f"E|{role}|{family}|{skeleton.skeleton_id}",
                        f"RF|{role}|{family}",
                        f"S|{skeleton.skeleton_id}",
                        f"M|{mechanism}",
                        f"G|{role}|{family}",
                    ),
                )
            )
            field_id = str(selected[f"{side}_field"])
            window_contexts = (
                f"E|{role}|{family}|{skeleton.skeleton_id}",
                f"RF|{role}|{family}",
                f"S|{skeleton.skeleton_id}",
                f"M|{mechanism}",
                "G",
            )
            selected[f"{side}_window"] = int(
                WINDOWS[0]
                if side == "right"
                and infer_family(field_id) == "listing_age_context"
                else self._choice(
                    "window",
                    _legal_windows(field_id, role),
                    window_contexts,
                )
            )
            operator = skeleton.to_dict()["operator_DAG"]
            right_normalizer_inactive = side == "right" and (
                skeleton.mechanism_family == "STATE_REGIME_MODULATION"
                or operator == "StateModulation"
            )
            selected[f"{side}_normalizer"] = str(
                "RollingZScore"
                if right_normalizer_inactive
                else self._choice(
                    "normalizer",
                    _legal_normalizers(field_id, role),
                    window_contexts,
                )
            )
        selected["beta"] = float(
            self._choice(
                "beta",
                BETAS,
                (f"S|{skeleton.skeleton_id}", f"M|{mechanism}", "G"),
            )
            if skeleton.to_dict()["operator_DAG"] == "Residual"
            else 0.5
        )
        selected["horizon_hours"] = int(
            self._choice(
                "horizon",
                HORIZONS,
                (
                    f"E|{mechanism}|{skeleton.skeleton_id}",
                    f"S|{skeleton.skeleton_id}",
                    f"M|{mechanism}",
                    "G",
                ),
            )
        )
        return candidate_from_genes(
            self.registry, skeleton=skeleton, genes=selected, roles=self.roles
        )

    def propose(self) -> tuple[CandidateSpec, dict[str, Any]]:
        before = self.state_hash()
        limit = int(self.parameters["duplicate_resample_limit"])
        candidate: CandidateSpec | None = None
        for duplicate_resamples in range(limit + 1):
            candidate = self._sample_candidate()
            if candidate.candidate_id not in self.seen:
                break
        assert candidate is not None
        if candidate.candidate_id in self.seen:
            raise _ProposalGenerationFailure(
                "CEM V2 duplicate resample limit exhausted",
                raw_attempts=limit + 1,
            )
        self.seen.add(candidate.candidate_id)
        self.step += 1
        return candidate, {
            "policy_state_hash_before": before,
            "operation": "HIERARCHICAL_TYPED_CEM_SAMPLE",
            "parent_ids": [],
            "receipt": None,
            "receipt_verified": None,
            "raw_attempts": duplicate_resamples + 1,
            "operator_diagnostic": candidate.operator_path,
            "interaction_diagnostic": candidate.skeleton_id,
        }

    def _accumulate(
        self,
        accumulator: dict[str, dict[str, Counter[str]]],
        axis: str,
        contexts: Iterable[str],
        value: Any,
    ) -> None:
        for context in contexts:
            accumulator[axis][str(context)][str(value)] += 1

    @staticmethod
    def _elite_sort_key(row: Mapping[str, Any]) -> tuple[Any, ...]:
        return (
            -float(row["pair_reward"]),
            int(row.get("policy_local_family_count_at_completion", 1)),
            str(row["candidate_id"]),
        )

    def _select_elites(
        self, rows: Sequence[Mapping[str, Any]]
    ) -> list[Mapping[str, Any]]:
        elite_count = max(
            1,
            int(math.ceil(len(rows) * float(self.parameters["elite_fraction"]))),
        )
        ordered = sorted(rows, key=self._elite_sort_key)
        if bool(self.parameters.get("behavior_family_champion_elites", False)):
            champions: list[Mapping[str, Any]] = []
            seen_families: set[str] = set()
            for row in ordered:
                family_id = str(
                    row.get("behavior_family_id") or row["candidate_id"]
                )
                if family_id in seen_families:
                    continue
                seen_families.add(family_id)
                champions.append(row)
        else:
            champions = ordered
        if bool(
            self.parameters.get("mechanism_stratified_elites", False)
            or self.parameters.get("skeleton_stratified_elites", False)
        ):
            candidate_by_id = {
                str(row["candidate_id"]): CandidateSpec.from_dict(
                    json.loads(str(row["candidate_spec_json"]))
                )
                for row in champions
            }
            selected: list[Mapping[str, Any]] = []
            selected_ids: set[str] = set()
            if bool(
                self.parameters.get("mechanism_stratified_elites", False)
            ):
                best_by_mechanism: dict[str, Mapping[str, Any]] = {}
                for row in champions:
                    candidate = candidate_by_id[str(row["candidate_id"])]
                    best_by_mechanism.setdefault(
                        candidate.mechanism_family, row
                    )
                selected.extend(
                    sorted(
                        best_by_mechanism.values(),
                        key=self._elite_sort_key,
                    )[:elite_count]
                )
                selected_ids.update(
                    str(row["candidate_id"]) for row in selected
                )
            best_by_skeleton: dict[str, Mapping[str, Any]] = {}
            if bool(
                self.parameters.get("skeleton_stratified_elites", False)
            ):
                for row in champions:
                    candidate = candidate_by_id[str(row["candidate_id"])]
                    best_by_skeleton.setdefault(candidate.skeleton_id, row)
                for row in sorted(
                    best_by_skeleton.values(), key=self._elite_sort_key
                ):
                    if len(selected) >= elite_count:
                        break
                    if str(row["candidate_id"]) in selected_ids:
                        continue
                    selected.append(row)
                    selected_ids.add(str(row["candidate_id"]))
            for row in champions:
                if len(selected) >= elite_count:
                    break
                if str(row["candidate_id"]) in selected_ids:
                    continue
                selected.append(row)
                selected_ids.add(str(row["candidate_id"]))
            elites = sorted(selected, key=self._elite_sort_key)
        else:
            elites = champions[:elite_count]
        self.last_elite_family_count = len(
            {
                str(row.get("behavior_family_id") or row["candidate_id"])
                for row in elites
            }
        )
        self.last_elite_mechanism_count = len(
            {
                CandidateSpec.from_dict(
                    json.loads(str(row["candidate_spec_json"]))
                ).mechanism_family
                for row in elites
            }
        )
        self.last_elite_skeleton_count = len(
            {
                CandidateSpec.from_dict(
                    json.loads(str(row["candidate_spec_json"]))
                ).skeleton_id
                for row in elites
            }
        )
        return elites

    def update(self, rows: Sequence[Mapping[str, Any]]) -> None:
        if not rows:
            return
        elites = self._select_elites(rows)
        accumulator: dict[str, dict[str, Counter[str]]] = defaultdict(
            lambda: defaultdict(Counter)
        )
        for row in elites:
            candidate = CandidateSpec.from_dict(json.loads(str(row["candidate_spec_json"])))
            skeleton = _skeleton_by_id(candidate.skeleton_id)
            mechanism = candidate.mechanism_family
            genes = candidate.generation_genes
            self._accumulate(accumulator, "mechanism_family", ("G",), mechanism)
            self._accumulate(
                accumulator,
                "skeleton_variant",
                (f"E|{mechanism}", "G"),
                skeleton.skeleton_id,
            )
            for side, role in zip(("left", "right"), skeleton.field_roles):
                field_id = str(genes[f"{side}_field"])
                family = infer_family(field_id)
                self._accumulate(
                    accumulator,
                    "field_family",
                    (
                        f"E|{role}|{skeleton.skeleton_id}",
                        f"RF|{role}|{family}",
                        f"S|{skeleton.skeleton_id}",
                        f"M|{mechanism}",
                        f"G|{role}",
                    ),
                    family,
                )
                common = (
                    f"E|{role}|{family}|{skeleton.skeleton_id}",
                    f"RF|{role}|{family}",
                    f"S|{skeleton.skeleton_id}",
                    f"M|{mechanism}",
                    f"G|{role}|{family}",
                )
                self._accumulate(accumulator, "field_token", common, field_id)
                effective = _effective_generation_gene_names(skeleton, genes)
                if f"{side}_window" in effective:
                    self._accumulate(
                        accumulator,
                        "window",
                        (*common[:-1], "G"),
                        genes[f"{side}_window"],
                    )
                if f"{side}_normalizer" in effective:
                    self._accumulate(
                        accumulator,
                        "normalizer",
                        (*common[:-1], "G"),
                        genes[f"{side}_normalizer"],
                    )
            if "beta" in _effective_generation_gene_names(skeleton, genes):
                self._accumulate(
                    accumulator,
                    "beta",
                    (f"S|{skeleton.skeleton_id}", f"M|{mechanism}", "G"),
                    genes["beta"],
                )
            self._accumulate(
                accumulator,
                "horizon",
                (
                    f"E|{mechanism}|{skeleton.skeleton_id}",
                    f"S|{skeleton.skeleton_id}",
                    f"M|{mechanism}",
                    "G",
                ),
                genes["horizon_hours"],
            )

        smoothing = float(self.parameters["smoothing"])
        pseudocount = float(self.parameters["count_pseudocount"])
        for axis, contexts in accumulator.items():
            for context, additions in contexts.items():
                table = self.tables[axis].setdefault(
                    context,
                    {"observations": 0, "counts": {}, "probabilities": {}},
                )
                # The probability table is the sole cross-checkpoint memory.
                # Keeping cumulative elite counts as well would replay old
                # observations a second time through the smoothing update.
                current_observations = Counter(
                    {str(key): int(value) for key, value in additions.items()}
                )
                diagnostic_counts = Counter(
                    {
                        str(key): int(value)
                        for key, value in table["counts"].items()
                    }
                )
                diagnostic_counts.update(current_observations)
                table["counts"] = dict(sorted(diagnostic_counts.items()))
                # Admission uses current-checkpoint observations. Historical
                # counts remain diagnostic and never feed the EMA again.
                table["observations"] = int(sum(current_observations.values()))
                prior = table.get("probabilities", {})
                values = tuple(sorted(set(prior) | set(additions)))
                current_total = int(sum(additions.values()))
                empirical = {
                    value: (additions[value] + pseudocount)
                    / (current_total + pseudocount * len(values))
                    for value in values
                }
                blended = {
                    value: (1.0 - smoothing)
                    * float(prior.get(value, 1.0 / len(values)))
                    + smoothing * float(empirical[value])
                    for value in values
                }
                table["probabilities"] = self._regularized(values, blended)
        self.update_count += 1

    def entropy_summary(self) -> dict[str, float]:
        output: dict[str, float] = {}
        for axis, contexts in sorted(self.tables.items()):
            entropies = [
                self._entropy(list(table.get("probabilities", {}).values()))
                for table in contexts.values()
                if table.get("probabilities")
            ]
            output[axis] = float(np.mean(entropies)) if entropies else 0.0
        return output

    def export_state(self) -> dict[str, Any]:
        return {
            "kind": "hierarchical_typed_cem_v2",
            "seed": int(self.seed),
            "parameters": dict(self.parameters),
            "rng_state": _json_rng_state(self.rng.getstate()),
            "seen": sorted(self.seen),
            "tables": {
                axis: {context: dict(table) for context, table in sorted(contexts.items())}
                for axis, contexts in sorted(self.tables.items())
            },
            "update_count": int(self.update_count),
            "step": int(self.step),
            "last_elite_family_count": int(self.last_elite_family_count),
            "last_elite_mechanism_count": int(
                self.last_elite_mechanism_count
            ),
            "last_elite_skeleton_count": int(self.last_elite_skeleton_count),
        }

    def state_hash(self) -> str:
        return _payload_sha(self.export_state())

    @classmethod
    def from_state(
        cls, registry: TypedExpressionRegistry, state: Mapping[str, Any]
    ) -> "HierarchicalTypedCEMV2":
        policy = cls(int(state["seed"]), registry, dict(state["parameters"]))
        policy.rng.setstate(_tuple_rng_state(state["rng_state"]))
        policy.seen = set(str(value) for value in state["seen"])
        policy.tables = defaultdict(
            dict,
            {
                str(axis): {
                    str(context): dict(table)
                    for context, table in contexts.items()
                }
                for axis, contexts in state["tables"].items()
            },
        )
        policy.update_count = int(state["update_count"])
        policy.step = int(state["step"])
        policy.last_elite_family_count = int(
            state.get("last_elite_family_count", 0)
        )
        policy.last_elite_mechanism_count = int(
            state.get("last_elite_mechanism_count", 0)
        )
        policy.last_elite_skeleton_count = int(
            state.get("last_elite_skeleton_count", 0)
        )
        return policy


@dataclass(slots=True)
class TypedEvolutionV2:
    seed: int
    registry: TypedExpressionRegistry
    parameters: Mapping[str, Any] = field(
        default_factory=lambda: dict(V2_PARAMETERS["typed_evolution_v2"])
    )
    rng: random.Random = field(init=False)
    roles: dict[str, list[str]] = field(init=False)
    compatible_skeleton_ids: tuple[str, ...] = field(init=False)
    seen: set[str] = field(default_factory=set)
    population: dict[str, dict[str, Any]] = field(default_factory=dict)
    family_counts: Counter[str] = field(default_factory=Counter)
    step: int = 0
    verified_mutations: int = 0
    verified_skeleton_mutations: int = 0
    verified_crossovers: int = 0
    duplicate_replacements: int = 0
    operation_probabilities: dict[str, float] = field(init=False)
    operator_productivity: dict[str, dict[str, int]] = field(
        default_factory=lambda: {
            operation: {"trials": 0, "new_families": 0}
            for operation in EVOLUTION_OPERATIONS
        }
    )
    operator_update_count: int = 0
    blocked_transition_skips: int = 0
    transition_productivity: dict[str, dict[str, int]] = field(default_factory=dict)
    blocked_transition_keys: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        self.parameters = dict(self.parameters)
        self.rng = random.Random(int(self.seed))
        surface = field_role_surface(tuple(self.registry.fields.values()))
        self.roles = {
            str(key): [str(value) for value in values]
            for key, values in surface["roles"].items()
        }
        self.compatible_skeleton_ids = tuple(surface["compatible_skeleton_ids"])
        if not self.compatible_skeleton_ids:
            raise ValueError("Evolution V2 carrier has no compatible skeleton")
        probabilities = sum(
            float(self.parameters[name])
            for name in (
                "gene_mutation_probability",
                "skeleton_variant_mutation_probability",
                "homologous_crossover_probability",
            )
        )
        if not math.isclose(probabilities, 1.0, rel_tol=0.0, abs_tol=1.0e-12):
            raise ValueError("Evolution V2 operation probabilities must sum to one")
        if int(self.parameters["population_limit"]) < int(
            self.parameters["tournament_size"]
        ):
            raise ValueError("Evolution V2 population is smaller than its tournament")
        if not 1 <= int(self.parameters["mechanism_cell_limit"]) <= int(
            self.parameters["population_limit"]
        ):
            raise ValueError("Evolution V2 mechanism cell limit is invalid")
        skeleton_cell_limit = int(
            self.parameters.get(
                "skeleton_cell_limit", self.parameters["population_limit"]
            )
        )
        if not 1 <= skeleton_cell_limit <= int(
            self.parameters["population_limit"]
        ):
            raise ValueError("Evolution V2 skeleton cell limit is invalid")
        floor = float(self.parameters.get("operator_productivity_floor", 0.0))
        if bool(self.parameters.get("operator_productivity_adaptation", False)):
            if not 0.0 <= floor < 1.0 / len(EVOLUTION_OPERATIONS):
                raise ValueError(
                    "Evolution V2 operator productivity floor is invalid"
                )
        if bool(
            self.parameters.get(
                "campaign_local_transition_collision_control", False
            )
        ) and int(self.parameters.get("transition_block_after_collisions", 0)) < 1:
            raise ValueError("Evolution V2 transition collision gate is invalid")
        self.operation_probabilities = {
            "EFFECTIVE_GENE_MUTATION_1_TO_3": float(
                self.parameters["gene_mutation_probability"]
            ),
            "COMPATIBLE_SKELETON_VARIANT_MUTATION": float(
                self.parameters["skeleton_variant_mutation_probability"]
            ),
            "ONE_POINT_HOMOLOGOUS_GENE_BUNDLE_CROSSOVER": float(
                self.parameters["homologous_crossover_probability"]
            ),
        }

    def _candidate(self, record: Mapping[str, Any]) -> CandidateSpec:
        return CandidateSpec.from_dict(record["candidate"])

    def _parent(
        self,
        *,
        eligible: Sequence[str] | None = None,
    ) -> CandidateSpec:
        ids = sorted(eligible or self.population)
        size = min(int(self.parameters["tournament_size"]), len(ids))
        if size == 0:
            raise RuntimeError("Evolution V2 has no eligible parent")
        participants = self.rng.sample(ids, size)
        parent_id = max(
            participants,
            key=lambda candidate_id: (
                float(self.population[candidate_id]["pair_reward"]),
                -int(
                    self.family_counts[
                        str(self.population[candidate_id]["behavior_family_id"])
                    ]
                ),
                candidate_id,
            ),
        )
        return self._candidate(self.population[parent_id])

    def _receipt(
        self,
        *,
        operation: str,
        parents: Sequence[CandidateSpec],
        child: CandidateSpec,
        details: Mapping[str, Any],
    ) -> dict[str, Any]:
        core = {
            "schema_version": "BROAD_TYPED_EVOLUTION_RECEIPT_V2",
            "operation": operation,
            "parent_ids": [parent.candidate_id for parent in parents],
            "child_id": child.candidate_id,
            "parent_skeleton_ids": [parent.skeleton_id for parent in parents],
            "child_skeleton_id": child.skeleton_id,
            "parent_genome_sha256": [
                _payload_sha(parent.generation_genes) for parent in parents
            ],
            "child_genome_sha256": _payload_sha(child.generation_genes),
            "parent_expression_sha256": [
                _payload_sha(parent.expression.canonical_dict()) for parent in parents
            ],
            "child_expression_sha256": _payload_sha(
                child.expression.canonical_dict()
            ),
            "child_control_expression_sha256": _payload_sha(
                child.control.canonical_dict()
            ),
            "child_raw_fields": list(child.raw_fields),
            **dict(details),
        }
        return {**core, "receipt_sha256": _payload_sha(core)}

    def update_operator_productivity(
        self, rows: Sequence[Mapping[str, Any]]
    ) -> None:
        if not bool(
            self.parameters.get("operator_productivity_adaptation", False)
        ):
            return
        checkpoint_productivity = {
            operation: Counter(trials=0, new_families=0)
            for operation in EVOLUTION_OPERATIONS
        }
        for row in rows:
            operation = str(row.get("operation", ""))
            if operation not in checkpoint_productivity:
                continue
            stats = checkpoint_productivity[operation]
            stats["trials"] += 1
            stats["new_families"] += int(
                bool(
                    row.get(
                        "new_policy_local_behavior_family_at_completion",
                        False,
                    )
                )
            )
        self.operator_productivity = checkpoint_productivity
        prior_successes = int(
            self.parameters["operator_productivity_prior_successes"]
        )
        prior_trials = int(
            self.parameters["operator_productivity_prior_trials"]
        )
        scores = {
            operation: (
                int(stats["new_families"]) + prior_successes
            )
            / (int(stats["trials"]) + prior_trials)
            for operation, stats in sorted(self.operator_productivity.items())
        }
        total = float(sum(scores.values()))
        floor = float(self.parameters["operator_productivity_floor"])
        remaining = 1.0 - floor * len(EVOLUTION_OPERATIONS)
        self.operation_probabilities = {
            operation: floor + remaining * float(scores[operation]) / total
            for operation in EVOLUTION_OPERATIONS
        }
        self.operator_update_count += 1

    def _mutate_genes(
        self, parent: CandidateSpec
    ) -> tuple[CandidateSpec, dict[str, Any]]:
        skeleton = _skeleton_by_id(parent.skeleton_id)
        maximum = int(self.parameters["maximum_mutated_genes"])
        minimum = int(self.parameters["minimum_mutated_genes"])
        compiled_attempts = 0
        for internal_attempt in range(
            1, int(self.parameters["duplicate_resample_limit"]) + 2
        ):
            genome = dict(parent.generation_genes)
            effective = sorted(_effective_generation_gene_names(skeleton, genome))
            target_count = self.rng.randint(minimum, min(maximum, len(effective)))
            selected = self.rng.sample(effective, target_count)
            for name in selected:
                domains = _mutable_gene_domains(
                    skeleton, genes=genome, roles=self.roles
                )
                if name not in domains:
                    break
                genome[name] = self.rng.choice(domains[name])
            else:
                child = candidate_from_genes(
                    self.registry,
                    skeleton=skeleton,
                    genes=genome,
                    roles=self.roles,
                )
                compiled_attempts += 1
                changed = sorted(
                    name
                    for name in GENE_ORDER
                    if child.generation_genes[name] != parent.generation_genes[name]
                )
                if minimum <= len(changed) <= maximum and child.candidate_id != parent.candidate_id:
                    return child, self._receipt(
                        operation="EFFECTIVE_GENE_MUTATION_1_TO_3",
                        parents=(parent,),
                        child=child,
                        details={
                            "changed_genes": changed,
                            "internal_generation_attempts": internal_attempt,
                            "compile_valid_attempts": compiled_attempts,
                        },
                    )
        raise _ProposalGenerationFailure(
            "Evolution V2 could not produce an effective 1-3 gene mutation",
            raw_attempts=int(self.parameters["duplicate_resample_limit"]) + 1,
            compile_valid_attempts=compiled_attempts,
        )

    @staticmethod
    def _skeleton_transition_key(
        *,
        parent_behavior_family_id: str,
        source_skeleton_id: str,
        target_skeleton_id: str,
        remapped_genome_sha256: str,
    ) -> str:
        return _payload_sha(
            {
                "operation": "COMPATIBLE_SKELETON_VARIANT_MUTATION",
                "parent_behavior_family_id": str(parent_behavior_family_id),
                "source_skeleton_id": str(source_skeleton_id),
                "target_skeleton_id": str(target_skeleton_id),
                "remapped_genome_sha256": str(remapped_genome_sha256),
            }
        )

    def _mutate_skeleton_with_transition(
        self,
        parent: CandidateSpec,
        *,
        parent_behavior_family_id: str,
        blocked_transition_keys: set[str] | None = None,
    ) -> tuple[CandidateSpec, dict[str, Any], str]:
        source = _skeleton_by_id(parent.skeleton_id)
        targets = [
            item
            for item in skeleton_registry()
            if item.skeleton_id in self.compatible_skeleton_ids
            and item.mechanism_family == source.mechanism_family
            and item.skeleton_id != source.skeleton_id
            and item.field_roles == source.field_roles
        ]
        self.rng.shuffle(targets)
        blocked = blocked_transition_keys or set()
        for internal_attempt, target in enumerate(targets, start=1):
            child = candidate_from_genes(
                self.registry,
                skeleton=target,
                genes=dict(parent.generation_genes),
                roles=self.roles,
            )
            transition_key = self._skeleton_transition_key(
                parent_behavior_family_id=parent_behavior_family_id,
                source_skeleton_id=source.skeleton_id,
                target_skeleton_id=target.skeleton_id,
                remapped_genome_sha256=_payload_sha(
                    child.generation_genes
                ),
            )
            if transition_key in blocked:
                self.blocked_transition_skips += 1
                continue
            if child.candidate_id != parent.candidate_id:
                return (
                    child,
                    self._receipt(
                        operation="COMPATIBLE_SKELETON_VARIANT_MUTATION",
                        parents=(parent,),
                        child=child,
                        details={
                            "source_variant": int(source.variant),
                            "target_variant": int(target.variant),
                            "deterministic_gene_remapping": dict(
                                child.generation_genes
                            ),
                            "internal_generation_attempts": internal_attempt,
                            "compile_valid_attempts": internal_attempt,
                        },
                    ),
                    transition_key,
                )
        raise _ProposalGenerationFailure(
            "Evolution V2 has no compatible skeleton variant mutation",
            raw_attempts=max(1, len(targets)),
            compile_valid_attempts=len(targets),
        )

    def _mutate_skeleton(
        self, parent: CandidateSpec
    ) -> tuple[CandidateSpec, dict[str, Any]]:
        child, receipt, _ = self._mutate_skeleton_with_transition(
            parent,
            parent_behavior_family_id="RECEIPT_ONLY_NO_COLLISION_MEMORY",
            blocked_transition_keys=set(),
        )
        return child, receipt

    def _crossover(
        self, first: CandidateSpec, second: CandidateSpec
    ) -> tuple[CandidateSpec, dict[str, Any]]:
        first_skeleton = _skeleton_by_id(first.skeleton_id)
        second_skeleton = _skeleton_by_id(second.skeleton_id)
        if first_skeleton.field_roles != second_skeleton.field_roles:
            raise ValueError("crossover parents have incompatible typed roles")
        gene_order = [
            name
            for name in GENE_ORDER
            if name
            in (
                _effective_generation_gene_names(
                    first_skeleton, first.generation_genes
                )
                & _effective_generation_gene_names(
                    second_skeleton, second.generation_genes
                )
            )
        ]
        points = list(range(1, len(gene_order)))
        self.rng.shuffle(points)
        compiled_attempts = 0
        for internal_attempt, point in enumerate(points, start=1):
            genome = dict(first.generation_genes)
            for index, name in enumerate(gene_order):
                if index >= point:
                    genome[name] = second.generation_genes[name]
            try:
                child = candidate_from_genes(
                    self.registry,
                    skeleton=first_skeleton,
                    genes=genome,
                    roles=self.roles,
                )
            except ValueError:
                continue
            compiled_attempts += 1
            if child.candidate_id in {first.candidate_id, second.candidate_id}:
                continue
            return child, self._receipt(
                operation="ONE_POINT_HOMOLOGOUS_GENE_BUNDLE_CROSSOVER",
                parents=(first, second),
                child=child,
                details={
                    "crossover_point": int(point),
                    "gene_order": gene_order,
                    "output_type": "NUMERIC_ASSET_TIME",
                    "internal_generation_attempts": internal_attempt,
                    "compile_valid_attempts": compiled_attempts,
                },
            )
        raise _ProposalGenerationFailure(
            "Evolution V2 could not produce a compatible crossover",
            raw_attempts=max(1, len(points)),
            compile_valid_attempts=compiled_attempts,
        )

    def verify_receipt(
        self,
        parents: Sequence[CandidateSpec],
        child: CandidateSpec,
        receipt: Mapping[str, Any],
    ) -> bool:
        try:
            core = {
                key: value for key, value in receipt.items() if key != "receipt_sha256"
            }
            if (
                receipt.get("schema_version")
                != "BROAD_TYPED_EVOLUTION_RECEIPT_V2"
                or receipt.get("parent_ids")
                != [parent.candidate_id for parent in parents]
                or receipt.get("child_id") != child.candidate_id
                or receipt.get("parent_skeleton_ids")
                != [parent.skeleton_id for parent in parents]
                or receipt.get("child_skeleton_id") != child.skeleton_id
                or receipt.get("parent_genome_sha256")
                != [_payload_sha(parent.generation_genes) for parent in parents]
                or receipt.get("child_genome_sha256")
                != _payload_sha(child.generation_genes)
                or receipt.get("parent_expression_sha256")
                != [
                    _payload_sha(parent.expression.canonical_dict())
                    for parent in parents
                ]
                or receipt.get("child_expression_sha256")
                != _payload_sha(child.expression.canonical_dict())
                or receipt.get("child_control_expression_sha256")
                != _payload_sha(child.control.canonical_dict())
                or receipt.get("child_raw_fields") != list(child.raw_fields)
                or receipt.get("receipt_sha256") != _payload_sha(core)
                or not _candidate_rebuild_verified(self.registry, child, self.roles)
            ):
                return False
            operation = str(receipt["operation"])
            if operation == "EFFECTIVE_GENE_MUTATION_1_TO_3":
                if len(parents) != 1 or child.skeleton_id != parents[0].skeleton_id:
                    return False
                changed = sorted(
                    name
                    for name in GENE_ORDER
                    if child.generation_genes[name]
                    != parents[0].generation_genes[name]
                )
                return changed == receipt.get("changed_genes") and 1 <= len(changed) <= 3
            if operation == "COMPATIBLE_SKELETON_VARIANT_MUTATION":
                if len(parents) != 1:
                    return False
                source = _skeleton_by_id(parents[0].skeleton_id)
                target = _skeleton_by_id(child.skeleton_id)
                rebuilt = candidate_from_genes(
                    self.registry,
                    skeleton=target,
                    genes=dict(parents[0].generation_genes),
                    roles=self.roles,
                )
                return bool(
                    source.mechanism_family == target.mechanism_family
                    and source.field_roles == target.field_roles
                    and source.skeleton_id != target.skeleton_id
                    and rebuilt.candidate_id == child.candidate_id
                    and receipt.get("deterministic_gene_remapping")
                    == child.generation_genes
                )
            if operation == "ONE_POINT_HOMOLOGOUS_GENE_BUNDLE_CROSSOVER":
                if len(parents) != 2:
                    return False
                if (
                    _skeleton_by_id(parents[0].skeleton_id).field_roles
                    != _skeleton_by_id(parents[1].skeleton_id).field_roles
                ):
                    return False
                first_skeleton = _skeleton_by_id(parents[0].skeleton_id)
                second_skeleton = _skeleton_by_id(parents[1].skeleton_id)
                gene_order = [
                    name
                    for name in GENE_ORDER
                    if name
                    in (
                        _effective_generation_gene_names(
                            first_skeleton, parents[0].generation_genes
                        )
                        & _effective_generation_gene_names(
                            second_skeleton, parents[1].generation_genes
                        )
                    )
                ]
                if receipt.get("gene_order") != gene_order:
                    return False
                point = int(receipt["crossover_point"])
                if not 1 <= point < len(gene_order):
                    return False
                genome = dict(parents[0].generation_genes)
                for index, name in enumerate(gene_order):
                    if index >= point:
                        genome[name] = parents[1].generation_genes[name]
                rebuilt = candidate_from_genes(
                    self.registry,
                    skeleton=first_skeleton,
                    genes=genome,
                    roles=self.roles,
                )
                return rebuilt.candidate_id == child.candidate_id
            return False
        except (KeyError, TypeError, ValueError, StopIteration):
            return False

    def propose(
        self, archive: BehaviorArchive | None = None
    ) -> tuple[CandidateSpec, dict[str, Any]]:
        del archive  # reporting archive is never an adaptive-policy input
        before = self.state_hash()
        limit = int(self.parameters["duplicate_resample_limit"])
        candidate: CandidateSpec | None = None
        receipt: dict[str, Any] | None = None
        parents: tuple[CandidateSpec, ...] = ()
        operation = "TYPED_RANDOM_WARMUP"
        transition_key: str | None = None
        compile_attempts = 0
        compile_valid_attempts = 0

        def run_child_operation(operation_factory: Callable[[], Any]) -> Any:
            try:
                return operation_factory()
            except _ProposalGenerationFailure as failure:
                raise _ProposalGenerationFailure(
                    str(failure),
                    raw_attempts=(
                        compile_attempts + failure.raw_attempts - 1
                    ),
                    compile_valid_attempts=(
                        compile_valid_attempts
                        + failure.compile_valid_attempts
                    ),
                ) from failure

        for duplicate_resamples in range(limit + 1):
            transition_key = None
            compile_attempts += 1
            if len(self.population) < int(self.parameters["warmup"]):
                skeletons = tuple(
                    item
                    for item in skeleton_registry()
                    if item.skeleton_id in self.compatible_skeleton_ids
                )
                skeleton = skeletons[(self.step + self.seed + duplicate_resamples) % len(skeletons)]
                candidate = generate_effective_candidate(
                    self.registry, skeleton=skeleton, rng=self.rng, roles=self.roles
                )
                receipt = None
                parents = ()
                operation = "TYPED_RANDOM_WARMUP"
                compile_valid_attempts += 1
            else:
                draw = self.rng.random()
                gene_probability = float(
                    self.operation_probabilities[
                        "EFFECTIVE_GENE_MUTATION_1_TO_3"
                    ]
                )
                skeleton_probability = float(
                    self.operation_probabilities[
                        "COMPATIBLE_SKELETON_VARIANT_MUTATION"
                    ]
                )
                first = self._parent()
                if draw < gene_probability:
                    candidate, receipt = run_child_operation(
                        lambda: self._mutate_genes(first)
                    )
                    parents = (first,)
                    operation = str(receipt["operation"])
                elif draw < gene_probability + skeleton_probability:
                    if bool(
                        self.parameters.get(
                            "campaign_local_transition_collision_control",
                            False,
                        )
                    ):
                        parent_family_id = str(
                            self.population[first.candidate_id][
                                "behavior_family_id"
                            ]
                        )
                        (
                            candidate,
                            receipt,
                            transition_key,
                        ) = run_child_operation(
                            lambda: self._mutate_skeleton_with_transition(
                                first,
                                parent_behavior_family_id=parent_family_id,
                                blocked_transition_keys=self.blocked_transition_keys,
                            )
                        )
                    else:
                        candidate, receipt = run_child_operation(
                            lambda: self._mutate_skeleton(first)
                        )
                    parents = (first,)
                    operation = str(receipt["operation"])
                else:
                    first_roles = _skeleton_by_id(first.skeleton_id).field_roles
                    compatible = [
                        candidate_id
                        for candidate_id, record in self.population.items()
                        if candidate_id != first.candidate_id
                        and _skeleton_by_id(
                            str(record["candidate"]["skeleton_id"])
                        ).field_roles
                        == first_roles
                    ]
                    if bool(
                        self.parameters.get(
                            "prefer_cross_skeleton_crossover", False
                        )
                    ):
                        cross_skeleton = [
                            candidate_id
                            for candidate_id in compatible
                            if str(
                                self.population[candidate_id]["candidate"][
                                    "skeleton_id"
                                ]
                            )
                            != first.skeleton_id
                        ]
                        if cross_skeleton:
                            compatible = cross_skeleton
                    if not compatible:
                        candidate, receipt = run_child_operation(
                            lambda: self._mutate_genes(first)
                        )
                        parents = (first,)
                    else:
                        second = self._parent(eligible=compatible)
                        candidate, receipt = run_child_operation(
                            lambda: self._crossover(first, second)
                        )
                        parents = (first, second)
                    operation = str(receipt["operation"])
                compile_attempts += int(
                    receipt.get("internal_generation_attempts", 1)
                ) - 1
                compile_valid_attempts += int(
                    receipt.get("compile_valid_attempts", 1)
                )
            if candidate.candidate_id not in self.seen:
                break
        assert candidate is not None
        if candidate.candidate_id in self.seen:
            raise _ProposalGenerationFailure(
                "Evolution V2 duplicate resample limit exhausted",
                raw_attempts=compile_attempts,
                compile_valid_attempts=compile_valid_attempts,
            )
        verified = (
            self.verify_receipt(parents, candidate, receipt)
            if receipt is not None
            else _candidate_rebuild_verified(self.registry, candidate, self.roles)
        )
        if not verified:
            raise RuntimeError("Evolution V2 receipt or expression verification failed")
        self.seen.add(candidate.candidate_id)
        self.step += 1
        return candidate, {
            "policy_state_hash_before": before,
            "operation": operation,
            "parent_ids": [parent.candidate_id for parent in parents],
            "receipt": receipt,
            "receipt_verified": bool(verified) if receipt is not None else None,
            "raw_attempts": compile_attempts,
            "compile_valid_attempts": compile_valid_attempts,
            "transition_key": transition_key,
        }

    def observe(
        self,
        candidate: CandidateSpec,
        archive_row: Mapping[str, Any],
    ) -> None:
        family_id = str(archive_row["behavior_family_id"])
        self.family_counts[family_id] += 1
        parent_ids = [str(value) for value in archive_row.get("parent_ids", [])]
        root_lineage_ids = sorted(
            {
                root_id
                for parent_id in parent_ids
                for root_id in self.population.get(parent_id, {}).get(
                    "root_lineage_ids", [parent_id]
                )
            }
            or {candidate.candidate_id}
        )
        candidate_record = {
            "candidate": candidate.to_dict(),
            "pair_reward": float(archive_row["pair_reward"]),
            "behavior_family_id": family_id,
            "mechanism_family": candidate.mechanism_family,
            "skeleton_id": candidate.skeleton_id,
            "root_lineage_ids": root_lineage_ids,
        }
        family_members = [
            candidate_id
            for candidate_id, record in self.population.items()
            if str(record["behavior_family_id"]) == family_id
        ]
        keep_new = True
        for candidate_id in family_members:
            old = self.population[candidate_id]
            if (
                float(old["pair_reward"]) > float(candidate_record["pair_reward"])
                or (
                    float(old["pair_reward"]) == float(candidate_record["pair_reward"])
                    and candidate_id < candidate.candidate_id
                )
            ):
                keep_new = False
            else:
                del self.population[candidate_id]
                self.duplicate_replacements += 1
        if keep_new:
            self.population[candidate.candidate_id] = candidate_record
        limit = int(self.parameters["population_limit"])
        if len(self.population) > limit or (
            "skeleton_cell_limit" in self.parameters and self.population
        ):
            ordered = sorted(
                self.population,
                key=lambda candidate_id: (
                    -float(self.population[candidate_id]["pair_reward"]),
                    candidate_id,
                ),
            )
            cell_limit = int(self.parameters["mechanism_cell_limit"])
            skeleton_cell_limit = int(
                self.parameters.get("skeleton_cell_limit", limit)
            )
            mechanism_counts: Counter[str] = Counter()
            skeleton_counts: Counter[str] = Counter()
            retained: list[str] = []
            for candidate_id in ordered:
                mechanism = str(
                    self.population[candidate_id]["mechanism_family"]
                )
                skeleton_id = str(
                    self.population[candidate_id].get(
                        "skeleton_id",
                        self.population[candidate_id]["candidate"]["skeleton_id"],
                    )
                )
                if (
                    mechanism_counts[mechanism] >= cell_limit
                    or skeleton_counts[skeleton_id] >= skeleton_cell_limit
                ):
                    continue
                retained.append(candidate_id)
                mechanism_counts[mechanism] += 1
                skeleton_counts[skeleton_id] += 1
                if len(retained) == limit:
                    break
            self.population = {
                candidate_id: self.population[candidate_id]
                for candidate_id in retained
            }
        operation = str(archive_row.get("operation", ""))
        if operation == "EFFECTIVE_GENE_MUTATION_1_TO_3":
            self.verified_mutations += 1
        elif operation == "COMPATIBLE_SKELETON_VARIANT_MUTATION":
            self.verified_skeleton_mutations += 1
        elif operation == "ONE_POINT_HOMOLOGOUS_GENE_BUNDLE_CROSSOVER":
            self.verified_crossovers += 1

    def observe_transition(
        self,
        *,
        transition_key: str,
        new_family: bool,
        block_after_collisions: int,
    ) -> None:
        if not transition_key:
            raise ValueError("policy-local transition observation lacks a key")
        stats = self.transition_productivity.setdefault(
            str(transition_key),
            {"trials": 0, "new_families": 0, "collisions": 0},
        )
        stats["trials"] += 1
        stats["new_families"] += int(bool(new_family))
        stats["collisions"] += int(not new_family)
        if int(stats["collisions"]) >= int(block_after_collisions):
            self.blocked_transition_keys.add(str(transition_key))

    def population_diagnostics(self) -> dict[str, Any]:
        mechanism_occupancy = Counter(
            str(record.get("mechanism_family", ""))
            for record in self.population.values()
        )
        skeleton_occupancy = Counter(
            str(
                record.get(
                    "skeleton_id", record["candidate"]["skeleton_id"]
                )
            )
            for record in self.population.values()
        )
        family_occupancy = Counter(
            str(record.get("behavior_family_id", ""))
            for record in self.population.values()
        )
        root_counts: Counter[str] = Counter()
        for record in self.population.values():
            roots = tuple(record.get("root_lineage_ids", ()))
            weight = 1.0 / max(1, len(roots))
            for root_id in roots:
                root_counts[str(root_id)] += weight
        total_root_weight = float(sum(root_counts.values()))
        probabilities = [
            float(count) / total_root_weight
            for count in root_counts.values()
            if total_root_weight > 0.0 and count > 0.0
        ]
        return {
            "effective_parent_count": len(self.population),
            "lineage_entropy": float(
                -sum(value * math.log(value) for value in probabilities)
            ),
            "top_root_lineage_share": (
                max(root_counts.values(), default=0.0)
                / max(total_root_weight, 1.0)
            ),
            "mechanism_occupancy": dict(sorted(mechanism_occupancy.items())),
            "skeleton_occupancy": dict(sorted(skeleton_occupancy.items())),
            "behavior_family_count": len(family_occupancy),
            "duplicate_family_slots": int(
                sum(max(0, count - 1) for count in family_occupancy.values())
            ),
            "operation_probabilities": dict(
                sorted(self.operation_probabilities.items())
            ),
            "operator_productivity": {
                operation: dict(stats)
                for operation, stats in sorted(
                    self.operator_productivity.items()
                )
            },
            "operator_update_count": int(self.operator_update_count),
            "blocked_transition_skips": int(self.blocked_transition_skips),
            "transition_productivity": {
                key: dict(value)
                for key, value in sorted(self.transition_productivity.items())
            },
            "blocked_transition_keys": sorted(self.blocked_transition_keys),
        }

    def export_state(self) -> dict[str, Any]:
        state = {
            "kind": "typed_evolution_v2",
            "seed": int(self.seed),
            "parameters": dict(self.parameters),
            "rng_state": _json_rng_state(self.rng.getstate()),
            "seen": sorted(self.seen),
            "population": {
                candidate_id: dict(record)
                for candidate_id, record in sorted(self.population.items())
            },
            "family_counts": dict(sorted(self.family_counts.items())),
            "step": int(self.step),
            "verified_mutations": int(self.verified_mutations),
            "verified_skeleton_mutations": int(self.verified_skeleton_mutations),
            "verified_crossovers": int(self.verified_crossovers),
            "duplicate_replacements": int(self.duplicate_replacements),
            "operation_probabilities": dict(
                sorted(self.operation_probabilities.items())
            ),
            "operator_productivity": {
                operation: dict(stats)
                for operation, stats in sorted(
                    self.operator_productivity.items()
                )
            },
            "operator_update_count": int(self.operator_update_count),
        }
        if bool(
            self.parameters.get(
                "campaign_local_transition_collision_control", False
            )
        ):
            state["blocked_transition_skips"] = int(
                self.blocked_transition_skips
            )
            state["transition_productivity"] = {
                key: dict(value)
                for key, value in sorted(self.transition_productivity.items())
            }
            state["blocked_transition_keys"] = sorted(
                self.blocked_transition_keys
            )
        return state

    def state_hash(self) -> str:
        return _payload_sha(self.export_state())

    @classmethod
    def from_state(
        cls, registry: TypedExpressionRegistry, state: Mapping[str, Any]
    ) -> "TypedEvolutionV2":
        policy = cls(int(state["seed"]), registry, dict(state["parameters"]))
        policy.rng.setstate(_tuple_rng_state(state["rng_state"]))
        policy.seen = set(str(value) for value in state["seen"])
        policy.population = {
            str(candidate_id): dict(record)
            for candidate_id, record in state["population"].items()
        }
        policy.family_counts = Counter(
            {
                str(family_id): int(count)
                for family_id, count in state.get("family_counts", {}).items()
            }
        )
        policy.step = int(state["step"])
        policy.verified_mutations = int(state["verified_mutations"])
        policy.verified_skeleton_mutations = int(
            state["verified_skeleton_mutations"]
        )
        policy.verified_crossovers = int(state["verified_crossovers"])
        policy.duplicate_replacements = int(state["duplicate_replacements"])
        policy.operation_probabilities = {
            str(operation): float(probability)
            for operation, probability in state.get(
                "operation_probabilities",
                policy.operation_probabilities,
            ).items()
        }
        policy.operator_productivity = {
            operation: {
                "trials": int(
                    state.get("operator_productivity", {})
                    .get(operation, {})
                    .get("trials", 0)
                ),
                "new_families": int(
                    state.get("operator_productivity", {})
                    .get(operation, {})
                    .get("new_families", 0)
                ),
            }
            for operation in EVOLUTION_OPERATIONS
        }
        policy.operator_update_count = int(
            state.get("operator_update_count", 0)
        )
        policy.blocked_transition_skips = int(
            state.get("blocked_transition_skips", 0)
        )
        policy.transition_productivity = {
            str(key): {
                "trials": int(value.get("trials", 0)),
                "new_families": int(value.get("new_families", 0)),
                "collisions": int(value.get("collisions", 0)),
            }
            for key, value in state.get("transition_productivity", {}).items()
        }
        policy.blocked_transition_keys = set(
            str(value) for value in state.get("blocked_transition_keys", ())
        )
        return policy


PolicyType = LanePolicy | HierarchicalTypedCEMV2 | TypedEvolutionV2


def _export_lane_policy(policy: LanePolicy) -> dict[str, Any]:
    return {
        "kind": "lane_policy_v1",
        "policy": policy.policy,
        "seed": int(policy.seed),
        "parameters": dict(policy.parameters),
        "rng_state": _json_rng_state(policy.rng.getstate()),
        "seen": sorted(policy.seen),
        "rewards": dict(sorted(policy.rewards.items())),
        "candidates": {
            candidate_id: candidate.to_dict()
            for candidate_id, candidate in sorted(policy.candidates.items())
        },
        "skeleton_visits": dict(sorted(policy.skeleton_visits.items())),
        "skeleton_rewards": {
            key: list(values) for key, values in sorted(policy.skeleton_rewards.items())
        },
        "proposal_order": list(policy.proposal_order),
        "cem_probabilities": {
            axis: dict(sorted(values.items()))
            for axis, values in sorted(policy.cem_probabilities.items())
        },
        "cem_update_count": int(policy.cem_update_count),
        "step": int(policy.step),
    }


def _restore_lane_policy(
    registry: TypedExpressionRegistry, state: Mapping[str, Any]
) -> LanePolicy:
    policy = LanePolicy(
        str(state["policy"]),
        int(state["seed"]),
        registry,
        dict(state["parameters"]),
    )
    policy.rng.setstate(_tuple_rng_state(state["rng_state"]))
    policy.seen = set(str(value) for value in state["seen"])
    policy.rewards = {
        str(key): float(value) for key, value in state["rewards"].items()
    }
    policy.candidates = {
        str(candidate_id): CandidateSpec.from_dict(payload)
        for candidate_id, payload in state["candidates"].items()
    }
    policy.skeleton_visits = Counter(
        {str(key): int(value) for key, value in state["skeleton_visits"].items()}
    )
    policy.skeleton_rewards = defaultdict(
        list,
        {
            str(key): [float(value) for value in values]
            for key, values in state["skeleton_rewards"].items()
        },
    )
    policy.proposal_order = [str(value) for value in state["proposal_order"]]
    policy.cem_probabilities = {
        str(axis): {str(key): float(value) for key, value in values.items()}
        for axis, values in state["cem_probabilities"].items()
    }
    policy.cem_update_count = int(state["cem_update_count"])
    policy.step = int(state["step"])
    return policy


def _export_policy(policy: PolicyType) -> dict[str, Any]:
    if isinstance(policy, LanePolicy):
        return _export_lane_policy(policy)
    return policy.export_state()


def _restore_policy(
    registry: TypedExpressionRegistry, state: Mapping[str, Any]
) -> PolicyType:
    kind = str(state["kind"])
    if kind == "lane_policy_v1":
        return _restore_lane_policy(registry, state)
    if kind == "hierarchical_typed_cem_v2":
        return HierarchicalTypedCEMV2.from_state(registry, state)
    if kind == "typed_evolution_v2":
        return TypedEvolutionV2.from_state(registry, state)
    raise ValueError(f"unsupported checkpoint policy kind: {kind}")


def _policy_key(arm: str, seed: int) -> str:
    return f"{arm}|{int(seed)}"


def _balanced_lane_choice(
    *,
    lane_order: Sequence[str],
    lane_completed: Mapping[str, int],
    proposals: Sequence[Mapping[str, Any]],
    target_by_lane: Mapping[str, int],
    scheduler_cursor: int,
) -> tuple[str | None, int]:
    """Choose the least-progressed unused lane with deterministic rotation."""
    pending = Counter(str(row["policy_key"]) for row in proposals)
    used = set(pending)
    eligible = [
        str(key)
        for key in lane_order
        if str(key) not in used
        and int(lane_completed.get(str(key), 0)) + int(pending[str(key)])
        < int(target_by_lane[str(key)])
    ]
    if not eligible:
        return None, int(scheduler_cursor)
    progress = {
        key: (
            int(lane_completed.get(key, 0)) + int(pending[key])
        )
        / max(1, int(target_by_lane[key]))
        for key in eligible
    }
    minimum = min(progress.values())
    tied = {
        key
        for key in eligible
        if math.isclose(progress[key], minimum, rel_tol=0.0, abs_tol=1.0e-15)
    }
    count = len(lane_order)
    start = int(scheduler_cursor) % max(1, count)
    rotated = [str(lane_order[(start + offset) % count]) for offset in range(count)]
    selected = next(key for key in rotated if key in tied)
    return selected, int(scheduler_cursor) + 1


def _initial_policies(
    registry: TypedExpressionRegistry,
    *,
    arms: Sequence[str] = FIRST_CHECKPOINT_ARMS,
    seeds: Sequence[int] = SEEDS,
) -> dict[str, PolicyType]:
    output: dict[str, PolicyType] = {}
    compatible_skeleton_ids = field_role_surface(
        tuple(registry.fields.values())
    )["compatible_skeleton_ids"]
    for seed in seeds:
        for arm in arms:
            key = _policy_key(arm, seed)
            if arm in V1_PARAMETERS:
                parameters = dict(V1_PARAMETERS[arm])
                if len(compatible_skeleton_ids) != len(skeleton_registry()):
                    parameters["compatible_skeleton_ids"] = list(
                        compatible_skeleton_ids
                    )
                output[key] = LanePolicy(
                    arm, seed, registry, parameters
                )
            elif arm == "hierarchical_typed_cem_v2":
                output[key] = HierarchicalTypedCEMV2(
                    seed,
                    registry,
                    dict(V2_PARAMETERS["hierarchical_typed_cem_v2"]),
                )
            elif arm == "typed_evolution_v2":
                output[key] = TypedEvolutionV2(
                    seed, registry, dict(V2_PARAMETERS["typed_evolution_v2"])
                )
            elif arm == "behavior_niched_cem_v2_1":
                output[key] = HierarchicalTypedCEMV2(
                    seed,
                    registry,
                    dict(V21_PARAMETERS["behavior_niched_cem_v2_1"]),
                )
            elif arm == "behavior_niched_evolution_v2_1":
                output[key] = TypedEvolutionV2(
                    seed,
                    registry,
                    dict(V21_PARAMETERS["behavior_niched_evolution_v2_1"]),
                )
            elif arm == "collision_controlled_evolution_v2_2":
                output[key] = TypedEvolutionV2(
                    seed,
                    registry,
                    dict(
                        V22_PARAMETERS[
                            "collision_controlled_evolution_v2_2"
                        ]
                    ),
                )
            else:
                raise ValueError(f"unsupported search policy arm: {arm}")
    return output


def _policy_propose(
    policy: PolicyType, archive: BehaviorArchive
) -> tuple[CandidateSpec, dict[str, Any]]:
    if isinstance(policy, TypedEvolutionV2):
        return policy.propose(archive)
    if isinstance(policy, HierarchicalTypedCEMV2):
        return policy.propose()
    candidate, metadata = policy.propose()
    receipt = metadata.get("mutation_receipt")
    operation = {
        "canonical_typed_random": "CANONICAL_TYPED_RANDOM_SAMPLE",
        "cem_distribution_v1": "FRESH_STATE_CEM_DISTRIBUTION_V1_SAMPLE",
        "evolutionary_typed_v1": (
            str(receipt.get("operator"))
            if isinstance(receipt, Mapping)
            else "FRESH_STATE_EVOLUTIONARY_TYPED_V1_WARMUP"
        ),
    }[policy.policy]
    return candidate, {
        "policy_state_hash_before": metadata["policy_state_hash_before"],
        "operation": operation,
        "parent_ids": [metadata["parent_id"]] if metadata.get("parent_id") else [],
        "receipt": receipt,
        "receipt_verified": metadata.get("mutation_receipt_verified"),
        "raw_attempts": int(metadata.get("duplicate_resamples", 0)) + 1,
        "policy_diagnostics": metadata.get("policy_diagnostics", {}),
    }


def _policy_reject(policy: PolicyType, candidate: CandidateSpec) -> None:
    if isinstance(policy, LanePolicy):
        policy.update(candidate, -11.0)


def _policy_observe(
    policy: PolicyType,
    *,
    candidate: CandidateSpec,
    reward: float,
    archive_row: Mapping[str, Any] | None,
) -> None:
    if isinstance(policy, LanePolicy):
        policy.update(candidate, float(reward))
    elif isinstance(policy, TypedEvolutionV2) and archive_row is not None:
        policy.observe(candidate, archive_row)


_WORKER_STORE: RawPanelStore | None = None
_WORKER_REGISTRY: TypedExpressionRegistry | None = None
_WORKER_BEHAVIOR_CONTRACT: Mapping[str, Any] | None = None
_WORKER_BLOCK_START = ADAPTIVE_START
_WORKER_BLOCK_END = ADAPTIVE_END
_WORKER_BLOCK_ROLE = "SPENT_DEVELOPMENT_BROAD39_SEARCH_ENGINE_V1"


def _worker_initialize(
    cache_root: str,
    contract_rows: Sequence[Mapping[str, Any]],
    behavior_contract: Mapping[str, Any],
    block_start: str = ADAPTIVE_START,
    block_end: str = ADAPTIVE_END,
    block_role: str = "SPENT_DEVELOPMENT_BROAD39_SEARCH_ENGINE_V1",
) -> None:
    global _WORKER_STORE, _WORKER_REGISTRY, _WORKER_BEHAVIOR_CONTRACT
    global _WORKER_BLOCK_START, _WORKER_BLOCK_END, _WORKER_BLOCK_ROLE
    _WORKER_STORE = RawPanelStore.open(Path(cache_root))
    _WORKER_REGISTRY = TypedExpressionRegistry(_contracts_from_payload(contract_rows))
    _WORKER_BEHAVIOR_CONTRACT = dict(behavior_contract)
    _WORKER_BLOCK_START = str(block_start)
    _WORKER_BLOCK_END = str(block_end)
    _WORKER_BLOCK_ROLE = str(block_role)


def _worker_evaluate(candidate_payload: Mapping[str, Any]) -> dict[str, Any]:
    if (
        _WORKER_STORE is None
        or _WORKER_REGISTRY is None
        or _WORKER_BEHAVIOR_CONTRACT is None
    ):
        raise RuntimeError("Search Engine V1 worker was not initialized")
    candidate = CandidateSpec.from_dict(candidate_payload)
    process = psutil.Process(os.getpid())
    cpu_started = time.process_time()
    wall_started = time.perf_counter()
    evaluation = None
    error = None
    memory_error = False
    try:
        evaluation = evaluate_pair(
            store=_WORKER_STORE,
            registry=_WORKER_REGISTRY,
            candidate=candidate,
            block_start=_WORKER_BLOCK_START,
            block_end=_WORKER_BLOCK_END,
            block_role=_WORKER_BLOCK_ROLE,
            behavior_contract=_WORKER_BEHAVIOR_CONTRACT,
        )
    except MemoryError as failure:
        error = type(failure).__name__ + ":" + str(failure)
        memory_error = True
    except (ValueError, FloatingPointError) as failure:
        error = type(failure).__name__ + ":" + str(failure)
    memory = process.memory_info()
    return {
        "candidate_id": candidate.candidate_id,
        "evaluation": evaluation,
        "error": error,
        "memory_error": memory_error,
        "process_cpu_seconds": time.process_time() - cpu_started,
        "wall_seconds": time.perf_counter() - wall_started,
        "worker_rss_bytes": int(memory.rss),
        "worker_private_bytes": int(getattr(memory, "private", memory.rss)),
    }


def _new_campaign_state(
    source_sha: str,
    frozen_hash: str,
    *,
    arms: Sequence[str] = FIRST_CHECKPOINT_ARMS,
    seeds: Sequence[int] = SEEDS,
) -> dict[str, Any]:
    arm_set = set(arms)
    return {
        "schema_version": 1,
        "source_sha": source_sha,
        "frozen_contract_sha256": frozen_hash,
        "next_checkpoint_index": 0,
        "scheduler_cursor": 0,
        "balanced_batch_index": 0,
        "generation_attempts": 0,
        "compile_valid": 0,
        "exact_unique": 0,
        "matched_control_valid": 0,
        "strict_evaluated": 0,
        "attempted_exact_ids": [],
        "policy_local_family_counts": {
            _policy_key(arm, seed): {}
            for arm in sorted(arm_set)
            for seed in seeds
        },
        "failure_counts": {},
        "wall_elapsed_seconds": 0.0,
        "workers": DEFAULT_WORKERS,
        "memory_fallback_used": False,
        "arm_states": {
            arm: "ACTIVE"
            for arm in sorted(arm_set)
            if arm not in V1_PARAMETERS
        },
        "arm_counters": {
            arm: {
                "generation_attempts": 0,
                "compile_valid": 0,
                "exact_unique": 0,
                "matched_control_valid": 0,
                "strict_evaluated": 0,
                "cpu_seconds": 0.0,
            }
            for arm in sorted(arm_set)
        },
    }


def _checkpoint_allocation(
    checkpoint_index: int, arm_states: Mapping[str, str]
) -> dict[str, int]:
    if checkpoint_index == 0:
        return {arm: 400 for arm in FIRST_CHECKPOINT_ARMS}
    allocation = {"canonical_typed_random": 400}
    diagnostics = [
        arm for arm in ROLLING_ARMS[1:] if arm_states.get(arm) == "DIAGNOSTIC"
    ]
    active = [arm for arm in ROLLING_ARMS[1:] if arm_states.get(arm) == "ACTIVE"]
    for arm in diagnostics:
        allocation[arm] = 200
    remaining = CHECKPOINT_SIZE - sum(allocation.values())
    if active:
        per_arm = (remaining // len(active)) // len(SEEDS) * len(SEEDS)
        for arm in active:
            allocation[arm] = per_arm
        allocation[active[0]] += CHECKPOINT_SIZE - sum(allocation.values())
    else:
        allocation["canonical_typed_random"] += remaining
    for arm in ROLLING_ARMS[1:]:
        if arm_states.get(arm) == "EXITED":
            allocation[arm] = 0
    if sum(allocation.values()) != CHECKPOINT_SIZE:
        raise AssertionError("checkpoint arm allocation does not sum to 2,000")
    if any(value % len(SEEDS) for value in allocation.values()):
        raise AssertionError("checkpoint arm allocation is not seed balanced")
    if allocation["canonical_typed_random"] < 400:
        raise AssertionError("typed random fell below its 20% floor")
    return allocation


def _reward_at_equal_count(
    rows: Sequence[Mapping[str, Any]], count: int
) -> tuple[float | None, float | None]:
    local = sorted(rows, key=lambda row: int(row["arm_completion_ordinal"]))[:count]
    rewards = [float(row["pair_reward"]) for row in local]
    if not rewards:
        return None, None
    top_count = max(1, int(math.ceil(0.10 * len(rewards))))
    return float(np.mean(rewards)), float(np.mean(sorted(rewards, reverse=True)[:top_count]))


def _metrics_rows(
    *,
    checkpoint_index: int,
    ledger: Sequence[Mapping[str, Any]],
    archive: BehaviorArchive,
    state: Mapping[str, Any],
    policies: Mapping[str, PolicyType],
    comparison_arms: Sequence[str] | None = None,
) -> list[dict[str, Any]]:
    cumulative_by_arm: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in ledger:
        cumulative_by_arm[str(row["arm"])].append(row)
    if comparison_arms is None:
        active_comparison_arms = (
            FIRST_CHECKPOINT_ARMS
            if checkpoint_index == 0
            else tuple(
                arm
                for arm in ROLLING_ARMS
                if cumulative_by_arm.get(arm)
                and state.get("arm_states", {}).get(arm, "ACTIVE") != "EXITED"
            )
        )
    else:
        active_comparison_arms = tuple(
            arm for arm in comparison_arms if cumulative_by_arm.get(arm)
        )
    matched_count = min(
        (len(cumulative_by_arm[arm]) for arm in active_comparison_arms), default=0
    )
    prior_families = {
        str(row["behavior_family_id"])
        for row in ledger
        if int(row["checkpoint_index"]) < checkpoint_index
    }
    output: list[dict[str, Any]] = []
    for arm in sorted(cumulative_by_arm):
        rows = cumulative_by_arm[arm]
        checkpoint_rows = [
            row for row in rows if int(row["checkpoint_index"]) == checkpoint_index
        ]
        families = Counter(str(row["behavior_family_id"]) for row in rows)
        checkpoint_families = {
            str(row["behavior_family_id"]) for row in checkpoint_rows
        }
        family_champions: dict[str, Mapping[str, Any]] = {}
        for row in rows:
            family_id = str(row["behavior_family_id"])
            current = family_champions.get(family_id)
            if current is None or (
                float(row["pair_reward"]) > float(current["pair_reward"])
                or (
                    float(row["pair_reward"]) == float(current["pair_reward"])
                    and str(row["candidate_id"]) < str(current["candidate_id"])
                )
            ):
                family_champions[family_id] = row
        counters = state["arm_counters"][arm]
        cpu_hours = float(counters["cpu_seconds"]) / 3600.0
        mean_reward, top_reward = _reward_at_equal_count(rows, matched_count)
        cem_entropies = [
            policy.entropy_summary()
            for key, policy in policies.items()
            if key.startswith(arm + "|")
            and isinstance(policy, HierarchicalTypedCEMV2)
        ]
        entropy_summary = {
            axis: float(np.mean([row.get(axis, 0.0) for row in cem_entropies]))
            for axis in sorted({key for row in cem_entropies for key in row})
        }
        evolution_diagnostics = [
            policy.population_diagnostics()
            for key, policy in policies.items()
            if key.startswith(arm + "|") and isinstance(policy, TypedEvolutionV2)
        ]
        collision_controlled = any(
            isinstance(policy, TypedEvolutionV2)
            and policy.parameters.get(
                "campaign_local_transition_collision_control"
            )
            is True
            for key, policy in policies.items()
            if key.startswith(arm + "|")
        )
        mechanism_occupancy: Counter[str] = Counter()
        skeleton_occupancy: Counter[str] = Counter()
        operator_productivity: dict[str, Counter[str]] = defaultdict(Counter)
        for diagnostic in evolution_diagnostics:
            mechanism_occupancy.update(diagnostic["mechanism_occupancy"])
            skeleton_occupancy.update(diagnostic["skeleton_occupancy"])
            for operation, stats in diagnostic[
                "operator_productivity"
            ].items():
                operator_productivity[operation].update(stats)
        transition_productivity = (
            archive.transition_productivity if collision_controlled else {}
        )
        blocked_transition_count = (
            len(archive.blocked_transition_keys) if collision_controlled else 0
        )
        blocked_transition_skips = (
            int(archive.blocked_transition_skips)
            if collision_controlled
            else 0
        )
        operation_probabilities = {
            operation: float(
                np.mean(
                    [
                        diagnostic["operation_probabilities"][operation]
                        for diagnostic in evolution_diagnostics
                    ]
                )
            )
            for operation in EVOLUTION_OPERATIONS
            if evolution_diagnostics
        }
        cem_policies = [
            policy
            for key, policy in policies.items()
            if key.startswith(arm + "|")
            and isinstance(policy, HierarchicalTypedCEMV2)
        ]
        output.append(
            {
                "checkpoint_index": int(checkpoint_index),
                "completed_count": int(len(ledger)),
                "arm": arm,
                "checkpoint_evaluated_count": len(checkpoint_rows),
                "cumulative_evaluated_count": len(rows),
                "generation_attempts": int(counters["generation_attempts"]),
                "compile_valid_rate": float(counters["compile_valid"])
                / max(1, int(counters["generation_attempts"])),
                "exact_unique_rate": float(counters["exact_unique"])
                / max(1, int(counters["compile_valid"])),
                "matched_control_valid_rate": float(
                    counters["matched_control_valid"]
                )
                / max(1, int(counters["exact_unique"])),
                "strict_evaluated_count": int(counters["strict_evaluated"]),
                "strict_per_raw_attempt": int(counters["strict_evaluated"])
                / max(1, int(counters["generation_attempts"])),
                "cpu_hours": cpu_hours,
                "valid_exact_unique_per_cpu_hour": int(counters["exact_unique"])
                / max(cpu_hours, 1.0e-12),
                "balanced_valid_exact_unique_per_cpu_hour": int(
                    counters["strict_evaluated"]
                )
                / max(cpu_hours, 1.0e-12),
                "positive_matched_discoveries_per_cpu_hour": sum(
                    bool(row["matched_positive"]) for row in rows
                )
                / max(cpu_hours, 1.0e-12),
                "new_behavior_families_per_cpu_hour": sum(
                    bool(
                        row.get(
                            "new_policy_local_behavior_family_at_completion",
                            row["new_behavior_family_at_completion"],
                        )
                    )
                    for row in rows
                )
                / max(cpu_hours, 1.0e-12),
                "new_behavior_families_per_1k_evaluations": 1000.0
                * sum(
                    bool(
                        row.get(
                            "new_policy_local_behavior_family_at_completion",
                            row["new_behavior_family_at_completion"],
                        )
                    )
                    for row in rows
                )
                / max(1, len(rows)),
                "matched_reward_comparison_count": int(matched_count),
                "mean_pair_reward_at_matched_count": mean_reward,
                "top_decile_pair_reward_at_matched_count": top_reward,
                "positive_matched_family_rate": sum(
                    bool(row["matched_positive"])
                    for row in family_champions.values()
                )
                / max(1, len(family_champions)),
                "cross_checkpoint_repeated_families": len(
                    checkpoint_families & prior_families
                ),
                "behavior_duplicate_rate": 1.0
                - len(families) / max(1, len(rows)),
                "cost_killed_rate": sum(bool(row["cost_killed"]) for row in rows)
                / max(1, len(rows)),
                "turnover_killed_rate": sum(
                    bool(row["turnover_killed"]) for row in rows
                )
                / max(1, len(rows)),
                "top_behavior_family_share": max(families.values(), default=0)
                / max(1, len(rows)),
                "cem_entropy_json": json.dumps(entropy_summary, sort_keys=True),
                "cem_elite_family_count": sum(
                    policy.last_elite_family_count
                    for policy in cem_policies
                ),
                "cem_elite_mechanism_count": sum(
                    policy.last_elite_mechanism_count
                    for policy in cem_policies
                ),
                "cem_elite_skeleton_count": sum(
                    policy.last_elite_skeleton_count
                    for policy in cem_policies
                ),
                "verified_gene_mutations": sum(
                    str(row["operation"]) == "EFFECTIVE_GENE_MUTATION_1_TO_3"
                    and bool(row["receipt_verified"])
                    for row in rows
                ),
                "verified_skeleton_mutations": sum(
                    str(row["operation"])
                    == "COMPATIBLE_SKELETON_VARIANT_MUTATION"
                    and bool(row["receipt_verified"])
                    for row in rows
                ),
                "verified_crossovers": sum(
                    str(row["operation"])
                    == "ONE_POINT_HOMOLOGOUS_GENE_BUNDLE_CROSSOVER"
                    and bool(row["receipt_verified"])
                    for row in rows
                ),
                "effective_parent_count": int(
                    sum(
                        int(row["effective_parent_count"])
                        for row in evolution_diagnostics
                    )
                ),
                "lineage_entropy": (
                    float(
                        np.mean(
                            [
                                float(row["lineage_entropy"])
                                for row in evolution_diagnostics
                            ]
                        )
                    )
                    if evolution_diagnostics
                    else 0.0
                ),
                "top_root_lineage_share": (
                    float(
                        np.mean(
                            [
                                float(row["top_root_lineage_share"])
                                for row in evolution_diagnostics
                            ]
                        )
                    )
                    if evolution_diagnostics
                    else 0.0
                ),
                "mechanism_occupancy_json": json.dumps(
                    dict(sorted(mechanism_occupancy.items())), sort_keys=True
                ),
                "skeleton_occupancy_json": json.dumps(
                    dict(sorted(skeleton_occupancy.items())), sort_keys=True
                ),
                "operator_probabilities_json": json.dumps(
                    operation_probabilities, sort_keys=True
                ),
                "operator_productivity_json": json.dumps(
                    {
                        operation: dict(sorted(stats.items()))
                        for operation, stats in sorted(
                            operator_productivity.items()
                        )
                    },
                    sort_keys=True,
                ),
                "operator_update_count": sum(
                    int(row["operator_update_count"])
                    for row in evolution_diagnostics
                ),
                "transition_productivity_json": json.dumps(
                    {
                        key: dict(sorted(stats.items()))
                        for key, stats in sorted(
                            transition_productivity.items()
                        )
                    },
                    sort_keys=True,
                ),
                "blocked_transition_count": int(
                    blocked_transition_count
                ),
                "blocked_transition_skips": int(
                    blocked_transition_skips
                ),
                "balanced_batch_count": len(
                    {
                        int(row["balanced_batch_index"])
                        for row in rows
                        if row.get("balanced_batch_index") is not None
                    }
                ),
                "arm_state_after_gate": state.get("arm_states", {}).get(
                    arm, "CONTROL_EXITED" if checkpoint_index > 0 else "CONTROL"
                ),
                "exit_gate_json": None,
            }
        )
    output.append(
        {
            "checkpoint_index": int(checkpoint_index),
            "completed_count": int(len(ledger)),
            "arm": "__campaign__",
            "checkpoint_evaluated_count": sum(
                int(row["checkpoint_evaluated_count"]) for row in output
            ),
            "cumulative_evaluated_count": len(ledger),
            "generation_attempts": int(state["generation_attempts"]),
            "compile_valid_rate": float(state["compile_valid"])
            / max(1, int(state["generation_attempts"])),
            "exact_unique_rate": float(state["exact_unique"])
            / max(1, int(state["compile_valid"])),
            "matched_control_valid_rate": float(state["matched_control_valid"])
            / max(1, int(state["exact_unique"])),
            "strict_evaluated_count": int(state["strict_evaluated"]),
            "strict_per_raw_attempt": int(state["strict_evaluated"])
            / max(1, int(state["generation_attempts"])),
            "cpu_hours": sum(
                float(value["cpu_seconds"])
                for value in state["arm_counters"].values()
            )
            / 3600.0,
            "valid_exact_unique_per_cpu_hour": int(state["exact_unique"])
            / max(
                1.0e-12,
                sum(
                    float(value["cpu_seconds"])
                    for value in state["arm_counters"].values()
                )
                / 3600.0,
            ),
            "balanced_valid_exact_unique_per_cpu_hour": int(
                state["strict_evaluated"]
            )
            / max(
                1.0e-12,
                sum(
                    float(value["cpu_seconds"])
                    for value in state["arm_counters"].values()
                )
                / 3600.0,
            ),
            "positive_matched_discoveries_per_cpu_hour": None,
            "new_behavior_families_per_cpu_hour": None,
            "new_behavior_families_per_1k_evaluations": 1000.0
            * len(archive.champion_by_family)
            / max(1, len(ledger)),
            "matched_reward_comparison_count": int(matched_count),
            "mean_pair_reward_at_matched_count": None,
            "top_decile_pair_reward_at_matched_count": None,
            "positive_matched_family_rate": sum(
                bool(row["champion_matched_positive"])
                for row in archive.summary_rows()
            )
            / max(1, len(archive.champion_by_family)),
            "cross_checkpoint_repeated_families": len(
                {
                    str(row["behavior_family_id"])
                    for row in ledger
                    if int(row["checkpoint_index"]) == checkpoint_index
                }
                & prior_families
            ),
            "behavior_duplicate_rate": 1.0
            - len(archive.champion_by_family) / max(1, len(ledger)),
            "cost_killed_rate": sum(bool(row["cost_killed"]) for row in ledger)
            / max(1, len(ledger)),
            "turnover_killed_rate": sum(
                bool(row["turnover_killed"]) for row in ledger
            )
            / max(1, len(ledger)),
            "top_behavior_family_share": max(
                archive.family_counts.values(), default=0
            )
            / max(1, len(ledger)),
            "cem_entropy_json": "{}",
            "cem_elite_family_count": 0,
            "cem_elite_mechanism_count": 0,
            "cem_elite_skeleton_count": 0,
            "verified_gene_mutations": sum(
                str(row["operation"]) == "EFFECTIVE_GENE_MUTATION_1_TO_3"
                and bool(row["receipt_verified"])
                for row in ledger
            ),
            "verified_skeleton_mutations": sum(
                str(row["operation"]) == "COMPATIBLE_SKELETON_VARIANT_MUTATION"
                and bool(row["receipt_verified"])
                for row in ledger
            ),
            "verified_crossovers": sum(
                str(row["operation"])
                == "ONE_POINT_HOMOLOGOUS_GENE_BUNDLE_CROSSOVER"
                and bool(row["receipt_verified"])
                for row in ledger
            ),
            "effective_parent_count": sum(
                len(policy.population)
                for policy in policies.values()
                if isinstance(policy, TypedEvolutionV2)
            ),
            "lineage_entropy": 0.0,
            "top_root_lineage_share": 0.0,
            "mechanism_occupancy_json": "{}",
            "skeleton_occupancy_json": "{}",
            "operator_probabilities_json": "{}",
            "operator_productivity_json": "{}",
            "operator_update_count": 0,
            "transition_productivity_json": "{}",
            "blocked_transition_count": 0,
            "blocked_transition_skips": 0,
            "balanced_batch_count": len(
                {
                    int(row["balanced_batch_index"])
                    for row in ledger
                    if row.get("balanced_batch_index") is not None
                }
            ),
            "arm_state_after_gate": "RUNNING",
            "exit_gate_json": None,
        }
    )
    return output


def _apply_exit_gate(
    *,
    checkpoint_index: int,
    checkpoint_metrics: list[dict[str, Any]],
    state: dict[str, Any],
) -> dict[str, Any]:
    if checkpoint_index < 1:
        return {}
    by_arm = {str(row["arm"]): row for row in checkpoint_metrics}
    random_metrics = by_arm["canonical_typed_random"]
    decisions: dict[str, Any] = {}
    for arm in ROLLING_ARMS[1:]:
        if arm not in by_arm or state["arm_states"].get(arm) == "EXITED":
            continue
        metrics = by_arm[arm]
        comparisons = {
            "valid_exact_unique_per_cpu_hour": float(
                metrics["valid_exact_unique_per_cpu_hour"]
            )
            > float(random_metrics["valid_exact_unique_per_cpu_hour"]),
            "new_behavior_families_per_1k_evaluations": float(
                metrics["new_behavior_families_per_1k_evaluations"]
            )
            > float(random_metrics["new_behavior_families_per_1k_evaluations"]),
            "mean_pair_reward": float(metrics["mean_pair_reward_at_matched_count"])
            > float(random_metrics["mean_pair_reward_at_matched_count"]),
            "top_decile_pair_reward": float(
                metrics["top_decile_pair_reward_at_matched_count"]
            )
            > float(random_metrics["top_decile_pair_reward_at_matched_count"]),
        }
        all_no_increment = not any(comparisons.values())
        before = str(state["arm_states"][arm])
        if all_no_increment and before == "ACTIVE":
            after = "DIAGNOSTIC"
        elif all_no_increment and before == "DIAGNOSTIC":
            after = "EXITED"
        elif not all_no_increment and before == "DIAGNOSTIC":
            after = "ACTIVE"
        else:
            after = before
        state["arm_states"][arm] = after
        decision = {
            "state_before": before,
            "state_after": after,
            "strictly_higher_than_random": comparisons,
            "all_four_no_increment": all_no_increment,
            "parameters_changed": False,
        }
        decisions[arm] = decision
        metrics["arm_state_after_gate"] = after
        metrics["exit_gate_json"] = json.dumps(decision, sort_keys=True)
    return decisions


def _write_top_level_artifacts(
    *,
    runtime_root: Path,
    ledger: Sequence[Mapping[str, Any]],
    archive: BehaviorArchive,
    metrics: Sequence[Mapping[str, Any]],
) -> None:
    _write_parquet(runtime_root / "candidate_ledger.parquet", ledger)
    _write_parquet(runtime_root / "behavior_archive.parquet", archive.rows)
    _write_json(
        runtime_root / "behavior_family_summary.json",
        {
            "schema_version": 1,
            "family_count": len(archive.champion_by_family),
            "candidate_count": len(archive.rows),
            "duplicate_replacements": archive.duplicate_replacements,
            "families": archive.summary_rows(),
            "archive_state_sha256": archive.state_hash(),
        },
    )
    _write_parquet(runtime_root / "arm_checkpoint_metrics.parquet", metrics)


def _checkpoint_state_payload(
    state: Mapping[str, Any], policies: Mapping[str, PolicyType], archive: BehaviorArchive
) -> dict[str, Any]:
    return {
        **dict(state),
        "attempted_exact_ids": sorted(set(state["attempted_exact_ids"])),
        "archive_duplicate_replacements": int(archive.duplicate_replacements),
        "archive_transition_state": archive.transition_state(),
        "policies": {
            key: _export_policy(policy) for key, policy in sorted(policies.items())
        },
    }


def _write_checkpoint(
    *,
    runtime_root: Path,
    label: str,
    checkpoint_index: int,
    registry: TypedExpressionRegistry,
    state: Mapping[str, Any],
    policies: Mapping[str, PolicyType],
    ledger: Sequence[Mapping[str, Any]],
    archive: BehaviorArchive,
    metrics: Sequence[Mapping[str, Any]],
    identities: Mapping[str, Any],
) -> Path:
    checkpoints = runtime_root / "checkpoints"
    checkpoints.mkdir(parents=True, exist_ok=True)
    target = checkpoints / label
    if target.exists():
        raise FileExistsError(f"checkpoint already exists: {target}")
    temporary = checkpoints / f".{label}.tmp-{os.getpid()}"
    if temporary.exists():
        shutil.rmtree(temporary)
    temporary.mkdir(parents=True)
    state_payload = _checkpoint_state_payload(state, policies, archive)
    _write_json(temporary / "state.json", state_payload)
    _write_parquet(temporary / "candidate_ledger.parquet", ledger)
    _write_parquet(temporary / "behavior_archive.parquet", archive.rows)
    _write_parquet(temporary / "arm_checkpoint_metrics.parquet", metrics)
    files = []
    for path in sorted(temporary.iterdir()):
        files.append(
            {
                "name": path.name,
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    policy_hash = _payload_sha(state_payload["policies"])
    manifest = {
        "schema_version": 1,
        "checkpoint": label,
        "checkpoint_index": int(checkpoint_index),
        "source_sha": state["source_sha"],
        "frozen_contract_sha256": state["frozen_contract_sha256"],
        "data_cache_identity": identities["raw_cache"],
        "compiler_identity": identities["compiler_identity"],
        "completed_ledger_row_count": len(ledger),
        "completed_identity_sha256": _payload_sha(
            [str(row["candidate_id"]) for row in ledger]
        ),
        "policy_state_sha256": policy_hash,
        "archive_state_sha256": archive.state_hash(),
        "state_sha256": _payload_sha(state_payload),
        "receipt_count": sum(bool(row.get("receipt_json")) for row in ledger),
        "files": files,
        "atomic_write": "TEMP_DIRECTORY_THEN_OS_REPLACE",
        "restore_verified": False,
    }
    _write_json(temporary / "manifest.json", manifest)
    try:
        _load_checkpoint(
            checkpoint_path=temporary,
            registry=registry,
            expected_source_sha=str(state["source_sha"]),
            expected_frozen_hash=str(state["frozen_contract_sha256"]),
            expected_identities=identities,
            require_restore_verified=False,
        )
        manifest["restore_verified"] = True
        _write_json(temporary / "manifest.json", manifest)
        os.replace(temporary, target)
    except Exception:
        if temporary.exists():
            shutil.rmtree(temporary)
        raise
    return target


def _load_checkpoint(
    *,
    checkpoint_path: Path,
    registry: TypedExpressionRegistry,
    expected_source_sha: str,
    expected_frozen_hash: str,
    expected_identities: Mapping[str, Any],
    require_restore_verified: bool = True,
) -> tuple[dict[str, Any], dict[str, PolicyType], list[dict[str, Any]], BehaviorArchive, list[dict[str, Any]]]:
    manifest_path = checkpoint_path / "manifest.json"
    manifest = _read_json(manifest_path)
    if require_restore_verified and manifest.get("restore_verified") is not True:
        raise ValueError("checkpoint was not restore-verified before publication")
    if manifest.get("source_sha") != expected_source_sha:
        raise ValueError("checkpoint source SHA changed")
    if manifest.get("frozen_contract_sha256") != expected_frozen_hash:
        raise ValueError("checkpoint frozen contract changed")
    if manifest.get("data_cache_identity") != expected_identities["raw_cache"]:
        raise ValueError("checkpoint data/cache identity changed")
    if manifest.get("compiler_identity") != expected_identities["compiler_identity"]:
        raise ValueError("checkpoint compiler identity changed")
    for record in manifest["files"]:
        path = checkpoint_path / str(record["name"])
        if (
            not path.is_file()
            or path.stat().st_size != int(record["bytes"])
            or sha256_file(path) != str(record["sha256"])
        ):
            raise ValueError(f"checkpoint file identity changed: {record['name']}")
    state_payload = _read_json(checkpoint_path / "state.json")
    if _payload_sha(state_payload) != manifest["state_sha256"]:
        raise ValueError("checkpoint state hash changed")
    policies = {
        str(key): _restore_policy(registry, payload)
        for key, payload in state_payload.pop("policies").items()
    }
    archive_duplicate_replacements = int(
        state_payload.pop("archive_duplicate_replacements", 0)
    )
    archive_transition_state = dict(
        state_payload.pop("archive_transition_state", {})
    )
    ledger = pd.read_parquet(checkpoint_path / "candidate_ledger.parquet").to_dict(
        "records"
    )
    archive = BehaviorArchive.from_rows(
        pd.read_parquet(checkpoint_path / "behavior_archive.parquet").to_dict(
            "records"
        )
    )
    archive.duplicate_replacements = archive_duplicate_replacements
    archive.restore_transition_state(archive_transition_state)
    metrics = pd.read_parquet(
        checkpoint_path / "arm_checkpoint_metrics.parquet"
    ).to_dict("records")
    if len(ledger) != int(manifest["completed_ledger_row_count"]):
        raise ValueError("checkpoint ledger row count changed")
    if _payload_sha([str(row["candidate_id"]) for row in ledger]) != manifest[
        "completed_identity_sha256"
    ]:
        raise ValueError("checkpoint completed identity sequence changed")
    if _payload_sha(
        {key: _export_policy(policy) for key, policy in sorted(policies.items())}
    ) != manifest["policy_state_sha256"]:
        raise ValueError("checkpoint policy state restore changed")
    if archive.state_hash() != manifest["archive_state_sha256"]:
        raise ValueError("checkpoint archive state restore changed")
    return state_payload, policies, ledger, archive, metrics


class _EngineBudgetExhausted(RuntimeError):
    pass


class _ProposalGenerationFailure(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        raw_attempts: int,
        compile_valid_attempts: int | None = None,
    ) -> None:
        super().__init__(message)
        self.raw_attempts = int(raw_attempts)
        self.compile_valid_attempts = int(
            raw_attempts
            if compile_valid_attempts is None
            else compile_valid_attempts
        )


def _increment_counter(
    state: dict[str, Any], arm: str, name: str, amount: int | float = 1
) -> None:
    state[name] = state.get(name, 0) + amount
    state["arm_counters"][arm][name] = (
        state["arm_counters"][arm].get(name, 0) + amount
    )


def _failure(state: dict[str, Any], arm: str, reason: str) -> None:
    failures = Counter(
        {str(key): int(value) for key, value in state.get("failure_counts", {}).items()}
    )
    failures[f"{arm}:{reason}"] += 1
    state["failure_counts"] = dict(sorted(failures.items()))


def _evaluation_audit_fields(evaluation: Mapping[str, Any]) -> dict[str, Any]:
    """Flatten the matched economic waterfall without changing reward authority."""

    scalar_fields = (
        "gross_mean",
        "net_mean",
        "net_lcb",
        "net_standard_error",
        "net_standard_error_method",
        "net_standard_error_lags",
        "monthly_block_mean",
        "monthly_block_standard_error",
        "monthly_block_lcb",
        "monthly_block_count",
        "turnover_mean",
        "cost_mean",
        "support",
    )
    output: dict[str, Any] = {}
    for section_name in ("primary", "control", "incremental"):
        section = evaluation[section_name]
        for field in scalar_fields:
            output[f"{section_name}_{field}"] = section.get(field)
        output[f"{section_name}_month_metrics_json"] = json.dumps(
            section.get("month_metrics", []),
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        )

    incremental = evaluation["incremental"]
    gross_mean = float(incremental.get("gross_mean", float("nan")))
    net_mean = float(incremental.get("net_mean", float("nan")))
    violations = {
        str(value) for value in evaluation["feedback"].get("violations", [])
    }
    cost_sign_flip = bool(
        math.isfinite(gross_mean)
        and math.isfinite(net_mean)
        and gross_mean > 0.0
        and net_mean <= 0.0
    )
    output.update(
        {
            "scalar_net_delta_diagnostic": evaluation.get(
                "scalar_net_delta_diagnostic"
            ),
            "gross_positive_cost_sign_killed": cost_sign_flip,
            "cost_killed": cost_sign_flip,
            "cost_threshold_violated": "COST_MEAN" in violations,
            "turnover_killed": "TURNOVER_MEAN" in violations,
            "turnover_threshold_violated": "TURNOVER_MEAN" in violations,
        }
    )
    return output


def _ledger_row(
    *,
    candidate: CandidateSpec,
    evaluation: Mapping[str, Any],
    proposal: Mapping[str, Any],
    archive_row: Mapping[str, Any],
    new_family: bool,
    state_hash_after: str,
    checkpoint_index: int,
    completion_ordinal: int,
    arm_completion_ordinal: int,
    worker: Mapping[str, Any],
) -> dict[str, Any]:
    feedback = evaluation["feedback"]
    violations = [str(value) for value in feedback.get("violations", [])]
    incremental = evaluation["incremental"]
    behavior = evaluation["behavior"]
    economic_audit = _evaluation_audit_fields(evaluation)
    return {
        "completion_ordinal": int(completion_ordinal),
        "arm_completion_ordinal": int(arm_completion_ordinal),
        "checkpoint_index": int(checkpoint_index),
        "checkpoint_completion_ordinal": int(proposal["checkpoint_completion_ordinal"]),
        "generation_attempt_ordinal": int(proposal["generation_attempt_ordinal"]),
        "candidate_id": candidate.candidate_id,
        "exact_expression_id": candidate.candidate_id,
        "canonical_expression_id": candidate.expression.expression_id,
        "behavior_family_id": behavior["behavior_family_id"],
        "primary_behavior_id": behavior.get("primary_behavior_id"),
        "control_behavior_id": behavior.get("control_behavior_id"),
        "incremental_behavior_id": behavior.get(
            "incremental_behavior_id", behavior["behavior_family_id"]
        ),
        "arm": str(proposal["arm"]),
        "seed": int(proposal["seed"]),
        "skeleton_id": candidate.skeleton_id,
        "mechanism_family": candidate.mechanism_family,
        "operator_path": candidate.operator_path,
        "horizon_hours": int(candidate.horizon_hours),
        "raw_fields_json": json.dumps(list(candidate.raw_fields)),
        "field_families_json": json.dumps(list(candidate.field_families)),
        "operation": str(proposal["operation"]),
        "transition_key": proposal.get("transition_key"),
        "balanced_batch_index": proposal.get("balanced_batch_index"),
        "balanced_batch_slot": proposal.get("balanced_batch_slot"),
        "balanced_batch_size": proposal.get("balanced_batch_size"),
        "parent_ids_json": json.dumps(list(proposal["parent_ids"])),
        "receipt_json": (
            json.dumps(proposal["receipt"], sort_keys=True)
            if proposal.get("receipt") is not None
            else None
        ),
        "receipt_verified": proposal.get("receipt_verified"),
        "expression_hash_verified": bool(proposal["expression_hash_verified"]),
        "policy_state_hash_before": str(proposal["policy_state_hash_before"]),
        "policy_state_hash_after": state_hash_after,
        "candidate_spec_json": json.dumps(candidate.to_dict(), sort_keys=True),
        "compile_valid": True,
        "exact_unique": True,
        "matched_control_valid": True,
        "strict_cost_evaluated": True,
        "new_behavior_family_at_completion": bool(new_family),
        "new_policy_local_behavior_family_at_completion": bool(
            proposal.get(
                "new_policy_local_behavior_family_at_completion", new_family
            )
        ),
        "policy_local_family_count_at_completion": int(
            proposal.get(
                "policy_local_family_count_at_completion",
                proposal["family_member_count_at_completion"],
            )
        ),
        "family_member_count_at_completion": int(
            proposal["family_member_count_at_completion"]
        ),
        "is_family_champion_at_completion": bool(
            archive_row["is_family_champion"]
        ),
        "pair_reward": float(evaluation["pair_reward"]),
        "matched_positive": bool(evaluation["matched_positive"]),
        "gross_mean": incremental.get("gross_mean"),
        "net_mean": incremental.get("net_mean"),
        "net_lcb": incremental.get("net_lcb"),
        "turnover_mean": incremental.get("turnover_mean"),
        "cost_mean": incremental.get("cost_mean"),
        "support": incremental.get("support"),
        "feedback_violations_json": json.dumps(violations),
        **economic_audit,
        "coordinate_data_binding_id": behavior["coordinate_data_binding_id"],
        "rank_descriptor_id": behavior["rank_descriptor_id"],
        "selected_asset_overlap_id": behavior["selected_asset_overlap_id"],
        "mapped_weight_descriptor_id": behavior["mapped_weight_descriptor_id"],
        "turnover_path_descriptor_id": behavior["turnover_path_descriptor_id"],
        "turnover_path_sha256": behavior.get("turnover_path_sha256"),
        "pit_regime_descriptor_id": behavior["pit_regime_descriptor_id"],
        "descriptor_contract_sha256": behavior["descriptor_contract_sha256"],
        "proposal_compile_cpu_seconds": float(proposal["proposal_cpu_seconds"]),
        "pair_process_cpu_seconds": float(worker["process_cpu_seconds"]),
        "pair_wall_seconds": float(worker["wall_seconds"]),
        "worker_rss_bytes": int(worker["worker_rss_bytes"]),
        "worker_private_bytes": int(worker["worker_private_bytes"]),
        "field_read_seconds": evaluation["timings"].get("field_read_seconds"),
        "dag_materialization_seconds": evaluation["timings"].get(
            "dag_materialization_seconds"
        ),
        "mapping_seconds": evaluation["timings"].get("mapping_seconds"),
        "standalone_evaluator_seconds": evaluation["timings"].get(
            "standalone_evaluator_seconds"
        ),
        "incremental_sleeve_seconds": evaluation["timings"].get(
            "incremental_sleeve_seconds"
        ),
        "behavior_descriptor_seconds": evaluation["timings"].get(
            "behavior_descriptor_seconds"
        ),
    }


def _report_text(decision: Mapping[str, Any]) -> str:
    answers = decision["success_questions"]
    qualified = ", ".join(decision["future_new_data_arena_qualified_arms"]) or "none"
    return f"""# Crypto Search Engine V1

- Status: `{decision['status']}`
- Producer source: `{decision['producer_source_sha']}`
- Surface: Broad 39 spent-development only; Core3 excluded; sealed reads `0`.
- Strict completed: `{decision['strict_evaluated_count']:,}` from `{decision['generation_attempts']:,}` raw attempts.
- Checkpoints: `{decision['checkpoint_count']}/10`, all atomic and restore-verified.
- Behavior families: `{decision['behavior_family_count']:,}`; duplicate rate `{decision['behavior_duplicate_rate']:.2%}`.

## Required answers

1. CEM V2 compute density: **{answers['cem_v2_compute_density']}**.
2. Evolution V2 repair and behavior discovery: **{answers['evolution_v2_repair_and_behavior_discovery']}**.
3. Behavior Archive duplicate reduction: **{answers['behavior_archive_duplicate_reduction']}**.
4. Continuous checkpoint/resume: **{answers['continuous_checkpoint_resume']}**.
5. Future new-data Arena qualification: **{qualified}**.

No Alpha, fresh economic, OOS, challenge, recent, May-stress, forward, relational,
latent-priority, promotion, or cross-sprint-memory conclusion is created by this run.
"""


def _final_decision(
    *,
    source_sha: str,
    state: Mapping[str, Any],
    ledger: Sequence[Mapping[str, Any]],
    archive: BehaviorArchive,
    metrics: Sequence[Mapping[str, Any]],
    runtime_root: Path,
) -> dict[str, Any]:
    final_rows = {
        str(row["arm"]): row
        for row in metrics
        if int(row["checkpoint_index"]) == CHECKPOINT_COUNT - 1
    }
    random_metrics = final_rows["canonical_typed_random"]
    cem = final_rows.get("hierarchical_typed_cem_v2")
    evolution = final_rows.get("typed_evolution_v2")
    cem_density = bool(
        cem
        and float(cem["valid_exact_unique_per_cpu_hour"])
        > float(random_metrics["valid_exact_unique_per_cpu_hour"])
    )
    evolution_behavior = bool(
        evolution
        and float(evolution["new_behavior_families_per_1k_evaluations"])
        > float(random_metrics["new_behavior_families_per_1k_evaluations"])
    )
    evolution_repairs = sum(
        str(row["arm"]) == "typed_evolution_v2"
        and str(row["operation"])
        in {
            "EFFECTIVE_GENE_MUTATION_1_TO_3",
            "COMPATIBLE_SKELETON_VARIANT_MUTATION",
            "ONE_POINT_HOMOLOGOUS_GENE_BUNDLE_CROSSOVER",
        }
        and bool(row["receipt_verified"])
        for row in ledger
    )
    archive_reduced = bool(
        archive.duplicate_replacements > 0
        and sum(
            policy_record
            for policy_record in (
                1
                for row in ledger
                if str(row["arm"]) == "typed_evolution_v2"
                and int(row["family_member_count_at_completion"]) > 1
            )
        )
        > 0
    )
    checkpoints = sorted((runtime_root / "checkpoints").glob("checkpoint_[0-9][0-9][0-9]"))
    restore_verified = len(checkpoints) == CHECKPOINT_COUNT and all(
        bool(_read_json(path / "manifest.json").get("restore_verified"))
        for path in checkpoints
    )
    def not_worse(value: Any, baseline: Any) -> bool:
        return float(value) >= float(baseline) - QUALIFICATION_TOLERANCE

    def clearly_better(value: Any, baseline: Any) -> bool:
        return float(value) > float(baseline) + QUALIFICATION_TOLERANCE

    metric_by_checkpoint_arm = {
        (int(row["checkpoint_index"]), str(row["arm"])): row
        for row in metrics
        if str(row["arm"]) != "__campaign__"
    }
    qualification_evidence: dict[str, Any] = {}
    qualified = ["canonical_typed_random"]
    for arm, arm_metrics in (
        ("hierarchical_typed_cem_v2", cem),
        ("typed_evolution_v2", evolution),
    ):
        if arm_metrics is None or state["arm_states"].get(arm) != "ACTIVE":
            continue
        checkpoint_gates: list[dict[str, Any]] = []
        for checkpoint_index in range(
            max(1, CHECKPOINT_COUNT - 2), CHECKPOINT_COUNT
        ):
            local = metric_by_checkpoint_arm.get((checkpoint_index, arm))
            random_local = metric_by_checkpoint_arm.get(
                (checkpoint_index, "canonical_typed_random")
            )
            if local is None or random_local is None:
                continue
            reward_not_worse = all(
                not_worse(local[name], random_local[name])
                for name in (
                    "mean_pair_reward_at_matched_count",
                    "top_decile_pair_reward_at_matched_count",
                )
            )
            productivity_better = any(
                clearly_better(local[name], random_local[name])
                for name in (
                    "valid_exact_unique_per_cpu_hour",
                    "new_behavior_families_per_1k_evaluations",
                )
            )
            checkpoint_gates.append(
                {
                    "checkpoint_index": checkpoint_index,
                    "reward_not_worse": reward_not_worse,
                    "productivity_better": productivity_better,
                    "pass": reward_not_worse and productivity_better,
                }
            )

        seed_gates: dict[str, Any] = {}
        for seed in SEEDS:
            arm_rows = [
                row
                for row in ledger
                if str(row["arm"]) == arm and int(row["seed"]) == seed
            ]
            random_rows = [
                row
                for row in ledger
                if str(row["arm"]) == "canonical_typed_random"
                and int(row["seed"]) == seed
            ]
            matched_count = min(len(arm_rows), len(random_rows))
            arm_mean, arm_top = _reward_at_equal_count(arm_rows, matched_count)
            random_mean, random_top = _reward_at_equal_count(
                random_rows, matched_count
            )
            seed_pass = bool(
                matched_count > 0
                and arm_mean is not None
                and arm_top is not None
                and random_mean is not None
                and random_top is not None
                and not_worse(arm_mean, random_mean)
                and not_worse(arm_top, random_top)
            )
            seed_gates[str(seed)] = {
                "matched_count": matched_count,
                "mean_pair_reward_not_worse": (
                    seed_pass
                    if arm_mean is None or random_mean is None
                    else not_worse(arm_mean, random_mean)
                ),
                "top_decile_pair_reward_not_worse": (
                    seed_pass
                    if arm_top is None or random_top is None
                    else not_worse(arm_top, random_top)
                ),
                "pass": seed_pass,
            }

        duplicate_gate = (
            float(arm_metrics["behavior_duplicate_rate"])
            <= QUALIFICATION_DUPLICATE_RATE_MAXIMUM + QUALIFICATION_TOLERANCE
        )
        consecutive_gate = (
            len(checkpoint_gates) == 2
            and all(bool(row["pass"]) for row in checkpoint_gates)
        )
        cross_seed_gate = len(seed_gates) == len(SEEDS) and all(
            bool(row["pass"]) for row in seed_gates.values()
        )
        arm_pass = duplicate_gate and consecutive_gate and cross_seed_gate
        qualification_evidence[arm] = {
            "engineering_execution_qualified": True,
            "search_strategy_qualified": arm_pass,
            "frozen_tolerance": QUALIFICATION_TOLERANCE,
            "behavior_duplicate_rate_maximum": QUALIFICATION_DUPLICATE_RATE_MAXIMUM,
            "behavior_duplicate_rate_pass": duplicate_gate,
            "checkpoint_gates": checkpoint_gates,
            "seed_gates": seed_gates,
        }
        if arm_pass:
            qualified.append(arm)
    duplicate_rate = 1.0 - len(archive.champion_by_family) / max(1, len(ledger))
    archive_qualified = bool(
        archive_reduced
        and restore_verified
        and duplicate_rate
        <= QUALIFICATION_DUPLICATE_RATE_MAXIMUM + QUALIFICATION_TOLERANCE
    )
    return {
        "schema_version": 1,
        "epoch_id": EPOCH_ID,
        "status": "PASS" if len(ledger) == STRICT_TARGET else "HOLD_RESEARCH",
        "producer_source_sha": source_sha,
        "strict_evaluated_count": len(ledger),
        "generation_attempts": int(state["generation_attempts"]),
        "raw_attempt_limit": RAW_ATTEMPT_LIMIT,
        "active_wall_seconds": float(state["wall_elapsed_seconds"]),
        "wall_time_limit_seconds": WALL_TIME_LIMIT_SECONDS,
        "checkpoint_count": len(checkpoints),
        "behavior_family_count": len(archive.champion_by_family),
        "behavior_duplicate_rate": duplicate_rate,
        "archive_duplicate_replacements": archive.duplicate_replacements,
        "arm_states": dict(state["arm_states"]),
        "engineering_execution_qualified_arms": list(ROLLING_ARMS),
        "search_strategy_qualification_evidence": qualification_evidence,
        "per_run_behavior_archive_engineering_qualified": archive_qualified,
        "future_new_data_arena_qualified_arms": qualified,
        "future_new_data_arena_qualified_components": [
            *qualified,
            *(["per_run_behavior_archive"] if archive_qualified else []),
        ],
        "success_questions": {
            "cem_v2_compute_density": (
                "YES" if cem_density else "NO_NOT_DEMONSTRATED"
            ),
            "evolution_v2_repair_and_behavior_discovery": (
                "YES"
                if evolution_repairs > 0 and evolution_behavior
                else "PARTIAL_REPAIRS_VERIFIED_DISCOVERY_INCREMENT_NOT_DEMONSTRATED"
                if evolution_repairs > 0
                else "NO_NOT_DEMONSTRATED"
            ),
            "behavior_archive_duplicate_reduction": (
                "YES" if archive_reduced else "NO_DUPLICATE_REDUCTION_NOT_DEMONSTRATED"
            ),
            "continuous_checkpoint_resume": (
                "YES_EXACT_RESTORE_VERIFIED"
                if restore_verified
                else "NO_RESTORE_PROOF_INCOMPLETE"
            ),
        },
        "latent_status": "LATENT_SEARCH_PRIORITY_MODEL_DEFERRED_TO_V1_1",
        "relational_status": "STAGE1_CLOSED",
        "sealed_reads": 0,
        "promotion": "FORBIDDEN",
        "next_arena_started": False,
        "cannot_conclude": [
            "new or fresh economic increment",
            "Alpha discovery",
            "OOS validity",
            "challenge, recent, May-stress, or forward evidence",
            "promotion readiness",
            "latent or relational search priority",
        ],
    }


def _aggtrades_canary_final_decision(
    *,
    source_sha: str,
    state: Mapping[str, Any],
    ledger: Sequence[Mapping[str, Any]],
    archive: BehaviorArchive,
    metrics: Sequence[Mapping[str, Any]],
    runtime_root: Path,
) -> dict[str, Any]:
    final_rows = {
        str(row["arm"]): row
        for row in metrics
        if int(row["checkpoint_index"]) == AGGTRADES_CANARY_CHECKPOINT_COUNT - 1
    }
    random_metrics = final_rows["canonical_typed_random"]
    comparisons: dict[str, Any] = {}
    for arm in ("hierarchical_typed_cem_v2", "typed_evolution_v2"):
        local = final_rows[arm]
        comparisons[arm] = {
            "matched_evaluated_count": int(
                local["matched_reward_comparison_count"]
            ),
            "valid_exact_unique_per_cpu_hour_delta": float(
                local["valid_exact_unique_per_cpu_hour"]
            )
            - float(random_metrics["valid_exact_unique_per_cpu_hour"]),
            "new_behavior_families_per_1k_delta": float(
                local["new_behavior_families_per_1k_evaluations"]
            )
            - float(random_metrics["new_behavior_families_per_1k_evaluations"]),
            "mean_pair_reward_delta": float(
                local["mean_pair_reward_at_matched_count"]
            )
            - float(random_metrics["mean_pair_reward_at_matched_count"]),
            "top_decile_pair_reward_delta": float(
                local["top_decile_pair_reward_at_matched_count"]
            )
            - float(random_metrics["top_decile_pair_reward_at_matched_count"]),
            "behavior_duplicate_rate_delta": float(
                local["behavior_duplicate_rate"]
            )
            - float(random_metrics["behavior_duplicate_rate"]),
        }
    checkpoints = sorted(
        (runtime_root / "checkpoints").glob("checkpoint_[0-9][0-9][0-9]")
    )
    restore_verified = (
        len(checkpoints) == AGGTRADES_CANARY_CHECKPOINT_COUNT
        and all(
            bool(_read_json(path / "manifest.json").get("restore_verified"))
            for path in checkpoints
        )
    )
    arm_counts = Counter(str(row["arm"]) for row in ledger)
    expected_arm_counts = {
        arm: count * AGGTRADES_CANARY_CHECKPOINT_COUNT
        for arm, count in AGGTRADES_CANARY_CHECKPOINT_ALLOCATION.items()
    }
    every_candidate_uses_aggtrades = all(
        bool(
            set(json.loads(str(row["raw_fields_json"])))
            & set(AGGTRADES_SYSTEM_CANARY_FIELDS)
        )
        for row in ledger
    )
    verified_operations = Counter(
        str(row["operation"])
        for row in ledger
        if str(row["arm"]) == "typed_evolution_v2"
        and bool(row.get("receipt_verified"))
    )
    engineering_pass = bool(
        len(ledger) == AGGTRADES_CANARY_STRICT_TARGET
        and dict(arm_counts) == expected_arm_counts
        and every_candidate_uses_aggtrades
        and restore_verified
    )
    return {
        "schema_version": 1,
        "epoch_id": AGGTRADES_CANARY_EPOCH_ID,
        "status": (
            "PASS_SYSTEM_CANARY_COMPLETED"
            if engineering_pass
            else "HOLD_SYSTEM_CANARY_INCOMPLETE"
        ),
        "research_decision": "HOLD_RESEARCH_FIXED_RETROSPECTIVE_COHORT",
        "producer_source_sha": source_sha,
        "strict_evaluated_count": len(ledger),
        "generation_attempts": int(state["generation_attempts"]),
        "raw_attempt_limit": AGGTRADES_CANARY_RAW_ATTEMPT_LIMIT,
        "active_wall_seconds": float(state["wall_elapsed_seconds"]),
        "wall_time_limit_seconds": AGGTRADES_CANARY_WALL_TIME_LIMIT_SECONDS,
        "checkpoint_count": len(checkpoints),
        "checkpoint_restore_verified": restore_verified,
        "arm_counts": dict(sorted(arm_counts.items())),
        "expected_arm_counts": expected_arm_counts,
        "every_candidate_uses_aggtrades": every_candidate_uses_aggtrades,
        "behavior_family_count": len(archive.champion_by_family),
        "behavior_duplicate_rate": 1.0
        - len(archive.champion_by_family) / max(1, len(ledger)),
        "archive_duplicate_replacements": archive.duplicate_replacements,
        "system_comparisons_vs_typed_random": comparisons,
        "verified_evolution_operations": dict(sorted(verified_operations.items())),
        "engineering_execution_qualified_arms": list(AGGTRADES_CANARY_ARMS),
        "future_new_data_arena_qualified_arms": [],
        "promotion": "FORBIDDEN",
        "sealed_reads": 0,
        "next_arena_started": False,
        "cannot_conclude": [
            "unbiased cross-sectional Alpha",
            "fresh economic increment",
            "OOS validity",
            "challenge, recent, May-stress, or forward evidence",
            "candidate or component promotion",
        ],
    }


def _aggtrades_canary_report_text(decision: Mapping[str, Any]) -> str:
    comparisons = decision["system_comparisons_vs_typed_random"]
    cem = comparisons["hierarchical_typed_cem_v2"]
    evolution = comparisons["typed_evolution_v2"]
    return f"""# Crypto aggTrades Search-System Canary V1

- Status: `{decision['status']}`
- Research decision: `{decision['research_decision']}`
- Producer source: `{decision['producer_source_sha']}`
- Strict completed: `{decision['strict_evaluated_count']:,}` from `{decision['generation_attempts']:,}` raw attempts.
- Checkpoints: `{decision['checkpoint_count']}/{AGGTRADES_CANARY_CHECKPOINT_COUNT}`, exact restore verified: `{decision['checkpoint_restore_verified']}`.
- Every candidate used at least one aggTrades field: `{decision['every_candidate_uses_aggtrades']}`.
- Behavior families: `{decision['behavior_family_count']:,}`; duplicate rate `{decision['behavior_duplicate_rate']:.2%}`.

## System comparison versus typed random

| Arm | valid exact-unique / CPU-hour delta | new families / 1k delta | mean pair reward delta | top-decile reward delta |
|---|---:|---:|---:|---:|
| Hierarchical Typed CEM V2 | {cem['valid_exact_unique_per_cpu_hour_delta']:.6f} | {cem['new_behavior_families_per_1k_delta']:.6f} | {cem['mean_pair_reward_delta']:.8f} | {cem['top_decile_pair_reward_delta']:.8f} |
| Typed Evolution V2 | {evolution['valid_exact_unique_per_cpu_hour_delta']:.6f} | {evolution['new_behavior_families_per_1k_delta']:.6f} | {evolution['mean_pair_reward_delta']:.8f} | {evolution['top_decile_pair_reward_delta']:.8f} |

This fixed-retrospective-cohort canary evaluates search-system behavior only.
It creates no Alpha, OOS, challenge, recent, May-stress, forward, promotion,
data-admission, latent-priority, or relational-training authority.
"""


def _v11_final_decision(
    *,
    source_sha: str,
    state: Mapping[str, Any],
    ledger: Sequence[Mapping[str, Any]],
    archive: BehaviorArchive,
    metrics: Sequence[Mapping[str, Any]],
    runtime_root: Path,
) -> dict[str, Any]:
    final_rows = {
        str(row["arm"]): row
        for row in metrics
        if int(row["checkpoint_index"]) == V11_CHECKPOINT_COUNT - 1
    }
    random_metrics = final_rows["canonical_typed_random"]
    comparisons: dict[str, Any] = {}
    for arm in V11_ARMS[1:]:
        local = final_rows[arm]
        comparisons[arm] = {
            "matched_evaluated_count": int(
                local["matched_reward_comparison_count"]
            ),
            "valid_exact_unique_per_cpu_hour": float(
                local["valid_exact_unique_per_cpu_hour"]
            ),
            "valid_exact_unique_per_cpu_hour_delta": float(
                local["valid_exact_unique_per_cpu_hour"]
            )
            - float(random_metrics["valid_exact_unique_per_cpu_hour"]),
            "new_behavior_families_per_1k_evaluations": float(
                local["new_behavior_families_per_1k_evaluations"]
            ),
            "new_behavior_families_per_1k_delta": float(
                local["new_behavior_families_per_1k_evaluations"]
            )
            - float(random_metrics["new_behavior_families_per_1k_evaluations"]),
            "mean_pair_reward_at_matched_count": float(
                local["mean_pair_reward_at_matched_count"]
            ),
            "mean_pair_reward_delta": float(
                local["mean_pair_reward_at_matched_count"]
            )
            - float(random_metrics["mean_pair_reward_at_matched_count"]),
            "top_decile_pair_reward_at_matched_count": float(
                local["top_decile_pair_reward_at_matched_count"]
            ),
            "top_decile_pair_reward_delta": float(
                local["top_decile_pair_reward_at_matched_count"]
            )
            - float(random_metrics["top_decile_pair_reward_at_matched_count"]),
            "behavior_duplicate_rate": float(
                local["behavior_duplicate_rate"]
            ),
            "behavior_duplicate_rate_delta": float(
                local["behavior_duplicate_rate"]
            )
            - float(random_metrics["behavior_duplicate_rate"]),
        }
    checkpoints = sorted(
        (runtime_root / "checkpoints").glob("checkpoint_[0-9][0-9][0-9]")
    )
    restore_verified = (
        len(checkpoints) == V11_CHECKPOINT_COUNT
        and all(
            bool(_read_json(path / "manifest.json").get("restore_verified"))
            for path in checkpoints
        )
    )
    arm_counts = Counter(str(row["arm"]) for row in ledger)
    expected_arm_counts = {
        arm: count * V11_CHECKPOINT_COUNT
        for arm, count in V11_CHECKPOINT_ALLOCATION.items()
    }
    every_candidate_uses_aggtrades = all(
        bool(
            set(json.loads(str(row["raw_fields_json"])))
            & set(AGGTRADES_SYSTEM_CANARY_FIELDS)
        )
        for row in ledger
    )
    verified_operations = Counter(
        str(row["operation"])
        for row in ledger
        if str(row["arm"]) == "behavior_niched_evolution_v2_1"
        and bool(row.get("receipt_verified"))
    )
    positive_by_arm = {
        arm: sum(
            bool(row["matched_positive"])
            for row in ledger
            if str(row["arm"]) == arm
        )
        for arm in V11_ARMS
    }
    cem = comparisons["behavior_niched_cem_v2_1"]
    evolution = comparisons["behavior_niched_evolution_v2_1"]
    cem_pass = bool(
        cem["valid_exact_unique_per_cpu_hour_delta"] >= 0.0
        and (
            cem["new_behavior_families_per_1k_delta"] > 0.0
            or cem["mean_pair_reward_delta"] > 0.0
            or cem["top_decile_pair_reward_delta"] > 0.0
        )
    )
    evolution_pass = bool(
        evolution["new_behavior_families_per_1k_delta"] >= 0.0
        and evolution["mean_pair_reward_delta"] >= 0.0
        and evolution["top_decile_pair_reward_delta"] >= 0.0
        and evolution["behavior_duplicate_rate"] < 0.065
    )
    evolution_metrics = final_rows["behavior_niched_evolution_v2_1"]
    within_budget = bool(
        int(state["generation_attempts"]) <= V11_RAW_ATTEMPT_LIMIT
        and float(state["wall_elapsed_seconds"])
        <= V11_WALL_TIME_LIMIT_SECONDS
    )
    engineering_pass = bool(
        len(ledger) == V11_STRICT_TARGET
        and dict(arm_counts) == expected_arm_counts
        and every_candidate_uses_aggtrades
        and restore_verified
        and int(evolution_metrics["operator_update_count"]) > 0
        and within_budget
    )
    return {
        "schema_version": 1,
        "epoch_id": V11_EPOCH_ID,
        "status": (
            "PASS_SEARCH_ENGINE_V1_1_COMPLETED"
            if engineering_pass
            else "ENGINE_BUDGET_EXHAUSTED"
            if not within_budget
            else "HOLD_SEARCH_ENGINE_V1_1_INCOMPLETE"
        ),
        "research_decision": "HOLD_RESEARCH_SPENT_FIXED_RETROSPECTIVE_COHORT",
        "producer_source_sha": source_sha,
        "strict_evaluated_count": len(ledger),
        "generation_attempts": int(state["generation_attempts"]),
        "raw_attempt_limit": V11_RAW_ATTEMPT_LIMIT,
        "active_wall_seconds": float(state["wall_elapsed_seconds"]),
        "wall_time_limit_seconds": V11_WALL_TIME_LIMIT_SECONDS,
        "checkpoint_count": len(checkpoints),
        "checkpoint_restore_verified": restore_verified,
        "arm_counts": dict(sorted(arm_counts.items())),
        "expected_arm_counts": expected_arm_counts,
        "every_candidate_uses_aggtrades": every_candidate_uses_aggtrades,
        "behavior_family_count": len(archive.champion_by_family),
        "behavior_duplicate_rate": 1.0
        - len(archive.champion_by_family) / max(1, len(ledger)),
        "archive_duplicate_replacements": archive.duplicate_replacements,
        "system_comparisons_vs_typed_random": comparisons,
        "positive_matched_discoveries_by_arm": positive_by_arm,
        "verified_evolution_operations": dict(
            sorted(verified_operations.items())
        ),
        "final_evolution_operator_probabilities": json.loads(
            str(evolution_metrics["operator_probabilities_json"])
        ),
        "final_evolution_operator_productivity": json.loads(
            str(evolution_metrics["operator_productivity_json"])
        ),
        "search_iteration_decision": {
            "behavior_niched_cem_v2_1": (
                "RETAIN_ENGINEERING_SEARCH_INCREMENT"
                if cem_pass
                else "REJECT_INCREMENT_NOT_DEMONSTRATED"
            ),
            "behavior_niched_evolution_v2_1": (
                "RETAIN_ENGINEERING_SEARCH_INCREMENT"
                if evolution_pass
                else "REJECT_INCREMENT_NOT_DEMONSTRATED"
            ),
        },
        "engineering_execution_qualified_arms": list(V11_ARMS),
        "future_new_data_arena_qualified_arms": [],
        "promotion": "FORBIDDEN",
        "sealed_reads": 0,
        "next_arena_started": False,
        "cannot_conclude": [
            "unbiased cross-sectional Alpha",
            "fresh economic increment",
            "OOS validity",
            "challenge, recent, May-stress, or forward evidence",
            "candidate, arm, or component promotion",
        ],
    }


def _v12_final_decision(
    *,
    source_sha: str,
    state: Mapping[str, Any],
    ledger: Sequence[Mapping[str, Any]],
    archive: BehaviorArchive,
    metrics: Sequence[Mapping[str, Any]],
    runtime_root: Path,
) -> dict[str, Any]:
    final_rows = {
        str(row["arm"]): row
        for row in metrics
        if int(row["checkpoint_index"]) == V12_CHECKPOINT_COUNT - 1
    }
    random_metrics = final_rows["canonical_typed_random"]
    evolution_metrics = final_rows["collision_controlled_evolution_v2_2"]
    comparison = {
        "matched_evaluated_count": int(
            evolution_metrics["matched_reward_comparison_count"]
        ),
        "strict_per_raw_attempt": float(
            evolution_metrics["strict_per_raw_attempt"]
        ),
        "strict_per_raw_attempt_delta": float(
            evolution_metrics["strict_per_raw_attempt"]
        )
        - float(random_metrics["strict_per_raw_attempt"]),
        "balanced_valid_exact_unique_per_cpu_hour": float(
            evolution_metrics[
                "balanced_valid_exact_unique_per_cpu_hour"
            ]
        ),
        "balanced_valid_exact_unique_per_cpu_hour_delta": float(
            evolution_metrics[
                "balanced_valid_exact_unique_per_cpu_hour"
            ]
        )
        - float(
            random_metrics[
                "balanced_valid_exact_unique_per_cpu_hour"
            ]
        ),
        "new_behavior_families_per_cpu_hour": float(
            evolution_metrics["new_behavior_families_per_cpu_hour"]
        ),
        "new_behavior_families_per_cpu_hour_delta": float(
            evolution_metrics["new_behavior_families_per_cpu_hour"]
        )
        - float(random_metrics["new_behavior_families_per_cpu_hour"]),
        "new_behavior_families_per_1k_evaluations": float(
            evolution_metrics["new_behavior_families_per_1k_evaluations"]
        ),
        "new_behavior_families_per_1k_delta": float(
            evolution_metrics["new_behavior_families_per_1k_evaluations"]
        )
        - float(random_metrics["new_behavior_families_per_1k_evaluations"]),
        "mean_pair_reward_at_matched_count": float(
            evolution_metrics["mean_pair_reward_at_matched_count"]
        ),
        "mean_pair_reward_delta": float(
            evolution_metrics["mean_pair_reward_at_matched_count"]
        )
        - float(random_metrics["mean_pair_reward_at_matched_count"]),
        "top_decile_pair_reward_at_matched_count": float(
            evolution_metrics["top_decile_pair_reward_at_matched_count"]
        ),
        "top_decile_pair_reward_delta": float(
            evolution_metrics["top_decile_pair_reward_at_matched_count"]
        )
        - float(random_metrics["top_decile_pair_reward_at_matched_count"]),
        "behavior_duplicate_rate": float(
            evolution_metrics["behavior_duplicate_rate"]
        ),
        "behavior_duplicate_rate_delta": float(
            evolution_metrics["behavior_duplicate_rate"]
        )
        - float(random_metrics["behavior_duplicate_rate"]),
    }
    engineering_gate = {
        "strict_per_raw_attempt_above_random": (
            comparison["strict_per_raw_attempt_delta"] > 0.0
        ),
        "balanced_valid_exact_unique_per_cpu_hour_not_below_random": (
            comparison[
                "balanced_valid_exact_unique_per_cpu_hour_delta"
            ]
            >= 0.0
        ),
        "new_behavior_families_per_cpu_hour_not_below_random": (
            comparison["new_behavior_families_per_cpu_hour_delta"] >= 0.0
        ),
        "behavior_duplicate_rate_at_or_below_3pct": (
            comparison["behavior_duplicate_rate"] <= 0.03
        ),
        "mean_pair_reward_not_below_random": (
            comparison["mean_pair_reward_delta"] >= 0.0
        ),
        "top_decile_pair_reward_not_below_random": (
            comparison["top_decile_pair_reward_delta"] >= 0.0
        ),
    }
    increment_pass = all(engineering_gate.values())
    checkpoints = sorted(
        (runtime_root / "checkpoints").glob("checkpoint_[0-9][0-9][0-9]")
    )
    restore_verified = (
        len(checkpoints) == V12_CHECKPOINT_COUNT
        and all(
            bool(_read_json(path / "manifest.json").get("restore_verified"))
            for path in checkpoints
        )
    )
    arm_counts = Counter(str(row["arm"]) for row in ledger)
    expected_arm_counts = {
        arm: count * V12_CHECKPOINT_COUNT
        for arm, count in V12_CHECKPOINT_ALLOCATION.items()
    }
    batches: dict[int, list[Mapping[str, Any]]] = defaultdict(list)
    for row in ledger:
        if row.get("balanced_batch_index") is not None:
            batches[int(row["balanced_batch_index"])].append(row)
    balanced_batch_integrity = bool(
        len(batches) == V12_STRICT_TARGET // V12_BALANCED_BATCH_SIZE
        and all(
            len(rows) == V12_BALANCED_BATCH_SIZE
            and Counter(str(row["arm"]) for row in rows)
            == {
                "canonical_typed_random": len(SEEDS),
                "collision_controlled_evolution_v2_2": len(SEEDS),
            }
            and len(
                {
                    (str(row["arm"]), int(row["seed"]))
                    for row in rows
                }
            )
            == V12_BALANCED_BATCH_SIZE
            and sorted(int(row["balanced_batch_slot"]) for row in rows)
            == list(range(V12_BALANCED_BATCH_SIZE))
            for rows in batches.values()
        )
    )
    expected_lanes = {
        (arm, seed) for arm in V12_ARMS for seed in SEEDS
    }
    lanes_by_slot: dict[int, set[tuple[str, int]]] = defaultdict(set)
    for rows in batches.values():
        for row in rows:
            lanes_by_slot[int(row["balanced_batch_slot"])].add(
                (str(row["arm"]), int(row["seed"]))
            )
    rotating_submission_integrity = bool(
        balanced_batch_integrity
        and set(lanes_by_slot) == set(range(V12_BALANCED_BATCH_SIZE))
        and all(lanes == expected_lanes for lanes in lanes_by_slot.values())
    )
    every_candidate_uses_aggtrades = all(
        bool(
            set(json.loads(str(row["raw_fields_json"])))
            & set(AGGTRADES_SYSTEM_CANARY_FIELDS)
        )
        for row in ledger
    )
    verified_operations = Counter(
        str(row["operation"])
        for row in ledger
        if str(row["arm"]) == "collision_controlled_evolution_v2_2"
        and bool(row.get("receipt_verified"))
    )
    positive_by_arm = {
        arm: sum(
            bool(row["matched_positive"])
            for row in ledger
            if str(row["arm"]) == arm
        )
        for arm in V12_ARMS
    }
    within_budget = bool(
        int(state["generation_attempts"]) <= V12_RAW_ATTEMPT_LIMIT
        and float(state["wall_elapsed_seconds"])
        <= V12_WALL_TIME_LIMIT_SECONDS
    )
    engineering_pass = bool(
        len(ledger) == V12_STRICT_TARGET
        and dict(arm_counts) == expected_arm_counts
        and every_candidate_uses_aggtrades
        and balanced_batch_integrity
        and rotating_submission_integrity
        and restore_verified
        and int(evolution_metrics["operator_update_count"]) > 0
        and within_budget
    )
    return {
        "schema_version": 1,
        "epoch_id": V12_EPOCH_ID,
        "status": (
            "PASS_SEARCH_ENGINE_V1_2_COMPLETED"
            if engineering_pass
            else "ENGINE_BUDGET_EXHAUSTED"
            if not within_budget
            else "HOLD_SEARCH_ENGINE_V1_2_INCOMPLETE"
        ),
        "research_decision": "HOLD_RESEARCH_SPENT_FIXED_RETROSPECTIVE_COHORT",
        "producer_source_sha": source_sha,
        "strict_evaluated_count": len(ledger),
        "generation_attempts": int(state["generation_attempts"]),
        "raw_attempt_limit": V12_RAW_ATTEMPT_LIMIT,
        "active_wall_seconds": float(state["wall_elapsed_seconds"]),
        "wall_time_limit_seconds": V12_WALL_TIME_LIMIT_SECONDS,
        "checkpoint_count": len(checkpoints),
        "checkpoint_restore_verified": restore_verified,
        "arm_counts": dict(sorted(arm_counts.items())),
        "expected_arm_counts": expected_arm_counts,
        "balanced_batch_count": len(batches),
        "balanced_batch_integrity": balanced_batch_integrity,
        "rotating_submission_integrity": rotating_submission_integrity,
        "every_candidate_uses_aggtrades": every_candidate_uses_aggtrades,
        "behavior_family_count": len(archive.champion_by_family),
        "behavior_duplicate_rate": 1.0
        - len(archive.champion_by_family) / max(1, len(ledger)),
        "archive_duplicate_replacements": archive.duplicate_replacements,
        "system_comparison_vs_typed_random": comparison,
        "frozen_engineering_gate": engineering_gate,
        "verified_evolution_operations": dict(
            sorted(verified_operations.items())
        ),
        "final_evolution_operator_probabilities": json.loads(
            str(evolution_metrics["operator_probabilities_json"])
        ),
        "final_evolution_operator_productivity": json.loads(
            str(evolution_metrics["operator_productivity_json"])
        ),
        "transition_productivity": json.loads(
            str(evolution_metrics["transition_productivity_json"])
        ),
        "blocked_transition_count": int(
            evolution_metrics["blocked_transition_count"]
        ),
        "blocked_transition_skips": int(
            evolution_metrics["blocked_transition_skips"]
        ),
        "positive_matched_discoveries_by_arm": positive_by_arm,
        "search_iteration_decision": {
            "collision_controlled_evolution_v2_2": (
                "RETAIN_ENGINEERING_SEARCH_INCREMENT"
                if increment_pass
                else "REJECT_INCREMENT_NOT_DEMONSTRATED"
            )
        },
        "engineering_execution_qualified_arms": list(V12_ARMS),
        "future_new_data_arena_qualified_arms": [],
        "promotion": "FORBIDDEN",
        "sealed_reads": 0,
        "next_arena_started": False,
        "cannot_conclude": [
            "unbiased cross-sectional Alpha",
            "fresh economic increment",
            "OOS validity",
            "challenge, recent, May-stress, or forward evidence",
            "candidate, arm, or component promotion",
        ],
    }


def _v11_report_text(decision: Mapping[str, Any]) -> str:
    comparisons = decision["system_comparisons_vs_typed_random"]
    cem = comparisons["behavior_niched_cem_v2_1"]
    evolution = comparisons["behavior_niched_evolution_v2_1"]
    return f"""# Crypto Search Engine V1.1 Behavior-Niched Arena

- Status: `{decision['status']}`
- Research decision: `{decision['research_decision']}`
- Producer source: `{decision['producer_source_sha']}`
- Strict completed: `{decision['strict_evaluated_count']:,}` from `{decision['generation_attempts']:,}` raw attempts.
- Checkpoints: `{decision['checkpoint_count']}/{V11_CHECKPOINT_COUNT}`, exact restore verified: `{decision['checkpoint_restore_verified']}`.
- Behavior families: `{decision['behavior_family_count']:,}`; duplicate rate `{decision['behavior_duplicate_rate']:.2%}`.
- Positive matched discoveries by arm: `{json.dumps(decision['positive_matched_discoveries_by_arm'], sort_keys=True)}`.

## Equal-count system comparison versus typed random

| Arm | valid unique / CPU-hour delta | new families / 1k | delta | mean reward delta | top-decile delta | duplicate rate |
|---|---:|---:|---:|---:|---:|---:|
| Behavior-Niched CEM V2.1 | {cem['valid_exact_unique_per_cpu_hour_delta']:.6f} | {cem['new_behavior_families_per_1k_evaluations']:.3f} | {cem['new_behavior_families_per_1k_delta']:.3f} | {cem['mean_pair_reward_delta']:.8f} | {cem['top_decile_pair_reward_delta']:.8f} | {cem['behavior_duplicate_rate']:.2%} |
| Behavior-Niched Evolution V2.1 | {evolution['valid_exact_unique_per_cpu_hour_delta']:.6f} | {evolution['new_behavior_families_per_1k_evaluations']:.3f} | {evolution['new_behavior_families_per_1k_delta']:.3f} | {evolution['mean_pair_reward_delta']:.8f} | {evolution['top_decile_pair_reward_delta']:.8f} | {evolution['behavior_duplicate_rate']:.2%} |

## System decision

- CEM V2.1: `{decision['search_iteration_decision']['behavior_niched_cem_v2_1']}`
- Evolution V2.1: `{decision['search_iteration_decision']['behavior_niched_evolution_v2_1']}`
- Future new-data Arena arms: `[]`

This fixed, spent-development Arena evaluates search capability only. It
creates no Alpha, OOS, challenge, recent, May-stress, forward, promotion,
data-admission, latent-priority, relational-training, or future-Arena
    qualification authority.
"""


def _v12_report_text(decision: Mapping[str, Any]) -> str:
    comparison = decision["system_comparison_vs_typed_random"]
    gate = decision["frozen_engineering_gate"]
    return f"""# Crypto Search Engine V1.2

- Status: `{decision['status']}`
- Research decision: `{decision['research_decision']}`
- Producer source: `{decision['producer_source_sha']}`
- Strict completed: `{decision['strict_evaluated_count']:,}` from `{decision['generation_attempts']:,}` raw attempts.
- Checkpoints: `{decision['checkpoint_count']}/{V12_CHECKPOINT_COUNT}`, exact restore verified: `{decision['checkpoint_restore_verified']}`.
- Balanced batches: `{decision['balanced_batch_count']}`, integrity: `{decision['balanced_batch_integrity']}`, rotating submission: `{decision['rotating_submission_integrity']}`.
- Behavior families: `{decision['behavior_family_count']:,}`; global duplicate rate `{decision['behavior_duplicate_rate']:.2%}`.

## Evolution V2.2 versus typed random

| Metric | Delta / result |
|---|---:|
| strict per raw attempt | {comparison['strict_per_raw_attempt_delta']:+.8f} |
| balanced valid unique / CPU-hour | {comparison['balanced_valid_exact_unique_per_cpu_hour_delta']:+.6f} |
| new families / CPU-hour | {comparison['new_behavior_families_per_cpu_hour_delta']:+.6f} |
| new families / 1k | {comparison['new_behavior_families_per_1k_evaluations']:.3f} |
| mean pair reward | {comparison['mean_pair_reward_delta']:+.8f} |
| top-decile pair reward | {comparison['top_decile_pair_reward_delta']:+.8f} |
| behavior duplicate rate | {comparison['behavior_duplicate_rate']:.2%} |

## Collision control

- Blocked transitions: `{decision['blocked_transition_count']}`
- Pre-evaluation blocked-transition skips: `{decision['blocked_transition_skips']}`
- Frozen gates passed: `{sum(bool(value) for value in gate.values())}/{len(gate)}`
- Search decision: `{decision['search_iteration_decision']['collision_controlled_evolution_v2_2']}`
- Future new-data Arena arms: `[]`

This fixed, spent-development engineering Arena creates no Alpha, OOS,
challenge, recent, May-stress, forward, promotion, data-admission,
latent-priority, relational-training, or future-Arena qualification authority.
"""


def _final_manifest(
    *,
    repo_root: Path,
    runtime_root: Path,
    report_path: Path,
    source_sha: str,
    frozen_hash: str,
    identities: Mapping[str, Any],
    state: Mapping[str, Any],
    epoch_id: str = EPOCH_ID,
    base_sha: str = BASE_SHA,
    continuation: str = (
        "python -m alphafactory_crypto.broad_search.search_engine_v1 "
        "check --runtime-date 20260721"
    ),
) -> dict[str, Any]:
    paths = [
        runtime_root / "frozen_contract.json",
        runtime_root / "embedded_preflight.json",
        runtime_root / "candidate_ledger.parquet",
        runtime_root / "behavior_archive.parquet",
        runtime_root / "behavior_family_summary.json",
        runtime_root / "arm_checkpoint_metrics.parquet",
        runtime_root / "final_decision.json",
        report_path,
    ]
    for checkpoint in sorted((runtime_root / "checkpoints").glob("checkpoint_*")):
        paths.extend(sorted(checkpoint.iterdir()))
    artifacts = [
        {
            "path": path.relative_to(repo_root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in sorted(paths)
    ]
    return {
        "schema_version": 1,
        "epoch_id": epoch_id,
        "status": "COMPLETED",
        "producer_source_sha": source_sha,
        "base_sha": base_sha,
        "frozen_contract_sha256": frozen_hash,
        "data_cache_identity": identities["raw_cache"],
        "compiler_identity": identities["compiler_identity"],
        "strict_evaluated_count": int(state["strict_evaluated"]),
        "generation_attempts": int(state["generation_attempts"]),
        "active_wall_seconds": float(state["wall_elapsed_seconds"]),
        "workers_final": int(state["workers"]),
        "memory_fallback_used": bool(state["memory_fallback_used"]),
        "sealed_reads": 0,
        "artifacts": artifacts,
        "artifact_bundle_sha256": _payload_sha(artifacts),
        "reproducible": True,
        "continuation": continuation,
    }


def _carrier_gate_final_decision(
    *,
    source_sha: str,
    carrier_id: str,
    state: Mapping[str, Any],
    ledger: Sequence[Mapping[str, Any]],
    archive: BehaviorArchive,
    metrics: Sequence[Mapping[str, Any]],
    runtime_root: Path,
) -> dict[str, Any]:
    final_metrics = {
        str(row["arm"]): dict(row)
        for row in metrics
        if int(row["checkpoint_index"]) == CARRIER_GATE_CHECKPOINT_COUNT - 1
    }
    random_metrics = final_metrics["canonical_typed_random"]
    comparisons = {}
    for arm in CARRIER_GATE_ARMS[1:]:
        local = final_metrics[arm]
        comparisons[arm] = {
            "mean_pair_reward_delta": float(
                local["mean_pair_reward_at_matched_count"]
            )
            - float(random_metrics["mean_pair_reward_at_matched_count"]),
            "top_decile_pair_reward_delta": float(
                local["top_decile_pair_reward_at_matched_count"]
            )
            - float(random_metrics["top_decile_pair_reward_at_matched_count"]),
            "new_behavior_families_per_1k_delta": float(
                local["new_behavior_families_per_1k_evaluations"]
            )
            - float(random_metrics["new_behavior_families_per_1k_evaluations"]),
        }
    checkpoints = sorted(
        (runtime_root / "checkpoints").glob("checkpoint_[0-9][0-9][0-9]")
    )
    return {
        "schema_version": 1,
        "status": "PASS_CARRIER_GATE_COMPLETED",
        "producer_source_sha": source_sha,
        "carrier_id": carrier_id,
        "strict_evaluated_count": len(ledger),
        "generation_attempts": int(state["generation_attempts"]),
        "active_wall_seconds": float(state["wall_elapsed_seconds"]),
        "checkpoint_count": len(checkpoints),
        "checkpoint_restore_verified": (
            len(checkpoints) == CARRIER_GATE_CHECKPOINT_COUNT
            and all(
                _read_json(path / "manifest.json").get("restore_verified") is True
                for path in checkpoints
            )
        ),
        "behavior_family_count": len(archive.champion_by_family),
        "arm_comparisons": comparisons,
        "research_decision": "HOLD_DEVELOPMENT_FIXED_RETROSPECTIVE_CARRIER",
        "future_arena_qualification": False,
        "alpha_claim": False,
        "oos": False,
        "promotion": False,
        "sealed_reads": 0,
    }


def _carrier_gate_report_text(decision: Mapping[str, Any]) -> str:
    return f"""# Crypto Search Carrier Gate V1

- Carrier: `{decision['carrier_id']}`
- Strict evaluated: `{decision['strict_evaluated_count']}`
- Checkpoints: `{decision['checkpoint_count']}`, exact restore: `{decision['checkpoint_restore_verified']}`
- Research decision: `{decision['research_decision']}`
- Authority: dual-axis matched controls, incremental behavior identity, arm/seed-local adaptive memory, single-EMA CEM update.
- Boundaries: development-only; no OOS, promotion, sealed reads, or Alpha claim.
"""


def run_engine(
    repo_root: Path,
    *,
    runtime_date: str = DEFAULT_RUNTIME_DATE,
    source_sha: str | None = None,
    campaign: str = "legacy",
    carrier_id: str | None = None,
) -> dict[str, Any]:
    if campaign not in {
        "legacy",
        "aggtrades_system_canary",
        "search_engine_v1_1",
        "search_engine_v1_2",
        "carrier_gate_v1",
    }:
        raise ValueError(f"unsupported Search Engine V1 campaign: {campaign}")
    is_canary = campaign == "aggtrades_system_canary"
    is_v11 = campaign == "search_engine_v1_1"
    is_v12 = campaign == "search_engine_v1_2"
    is_carrier_gate = campaign == "carrier_gate_v1"
    is_system_campaign = is_canary or is_v11 or is_v12 or is_carrier_gate
    if is_carrier_gate:
        if runtime_date != CARRIER_GATE_DEFAULT_RUNTIME_DATE:
            raise ValueError("carrier gate runtime date changed")
        if carrier_id not in CARRIER_GATE_IDS:
            raise ValueError("carrier gate requires one frozen carrier id")
        carrier_slug = str(carrier_id).lower()
        runtime_root = repo_root / (
            f"runtime/crypto_search_carrier_gate_v1_r3_{carrier_slug}_{runtime_date}"
        )
        report_path = repo_root / (
            f"reports/CRYPTO_SEARCH_CARRIER_GATE_V1_R3_{carrier_slug.upper()}_{runtime_date}.md"
        )
        strict_target = CARRIER_GATE_STRICT_TARGET
        checkpoint_count = CARRIER_GATE_CHECKPOINT_COUNT
        checkpoint_size = CARRIER_GATE_CHECKPOINT_SIZE
        raw_attempt_limit = CARRIER_GATE_RAW_ATTEMPT_LIMIT
        wall_time_limit = CARRIER_GATE_WALL_TIME_LIMIT_SECONDS
        campaign_arms = CARRIER_GATE_ARMS
        block_role = f"FRESH_STATE_CARRIER_LOCAL_DEVELOPMENT_GATE:{carrier_id}"
    elif is_v12:
        if runtime_date != V12_DEFAULT_RUNTIME_DATE:
            raise ValueError(
                "Search Engine V1.2 is authorized only for runtime date "
                f"{V12_DEFAULT_RUNTIME_DATE}"
            )
        runtime_root = (
            repo_root / f"runtime/crypto_search_engine_v1_2_{runtime_date}"
        )
        report_path = (
            repo_root / f"reports/CRYPTO_SEARCH_ENGINE_V1_2_{runtime_date}.md"
        )
        strict_target = V12_STRICT_TARGET
        checkpoint_count = V12_CHECKPOINT_COUNT
        checkpoint_size = V12_CHECKPOINT_SIZE
        raw_attempt_limit = V12_RAW_ATTEMPT_LIMIT
        wall_time_limit = V12_WALL_TIME_LIMIT_SECONDS
        campaign_arms = V12_ARMS
        block_role = "SPENT_DEVELOPMENT_SEARCH_ENGINE_V1_2_SYSTEM_ONLY"
    elif is_v11:
        if runtime_date != V11_DEFAULT_RUNTIME_DATE:
            raise ValueError(
                "Search Engine V1.1 is authorized only for runtime date "
                f"{V11_DEFAULT_RUNTIME_DATE}"
            )
        runtime_root = (
            repo_root / f"runtime/crypto_search_engine_v1_1_{runtime_date}"
        )
        report_path = (
            repo_root / f"reports/CRYPTO_SEARCH_ENGINE_V1_1_{runtime_date}.md"
        )
        strict_target = V11_STRICT_TARGET
        checkpoint_count = V11_CHECKPOINT_COUNT
        checkpoint_size = V11_CHECKPOINT_SIZE
        raw_attempt_limit = V11_RAW_ATTEMPT_LIMIT
        wall_time_limit = V11_WALL_TIME_LIMIT_SECONDS
        campaign_arms = V11_ARMS
        block_role = "SPENT_DEVELOPMENT_SEARCH_ENGINE_V1_1_SYSTEM_ONLY"
    elif is_canary:
        runtime_root = (
            repo_root
            / f"runtime/crypto_aggtrades_system_canary_v1_{runtime_date}"
        )
        report_path = (
            repo_root
            / f"reports/CRYPTO_AGGTRADES_SYSTEM_CANARY_V1_{runtime_date}.md"
        )
        strict_target = AGGTRADES_CANARY_STRICT_TARGET
        checkpoint_count = AGGTRADES_CANARY_CHECKPOINT_COUNT
        checkpoint_size = AGGTRADES_CANARY_CHECKPOINT_SIZE
        raw_attempt_limit = AGGTRADES_CANARY_RAW_ATTEMPT_LIMIT
        wall_time_limit = AGGTRADES_CANARY_WALL_TIME_LIMIT_SECONDS
        campaign_arms = AGGTRADES_CANARY_ARMS
        block_role = "DEVELOPMENT_DIAGNOSTIC_FIXED_COHORT_AGGTRADES_SYSTEM_CANARY"
    else:
        runtime_root = repo_root / f"runtime/crypto_search_engine_v1_{runtime_date}"
        report_path = repo_root / f"reports/CRYPTO_SEARCH_ENGINE_V1_{runtime_date}.md"
        strict_target = STRICT_TARGET
        checkpoint_count = CHECKPOINT_COUNT
        checkpoint_size = CHECKPOINT_SIZE
        raw_attempt_limit = RAW_ATTEMPT_LIMIT
        wall_time_limit = WALL_TIME_LIMIT_SECONDS
        campaign_arms = FIRST_CHECKPOINT_ARMS
        block_role = "SPENT_DEVELOPMENT_BROAD39_SEARCH_ENGINE_V1"
    observed_source = _git_sha(repo_root)
    source_sha = (source_sha or observed_source).lower()
    if source_sha != observed_source:
        raise ValueError("run must bind the checked-out producer source SHA")
    if not _source_tree_clean_for_run(
        repo_root, allowed_paths=(runtime_root, report_path)
    ):
        raise RuntimeError(
            "Search Engine V1 requires a clean producer tree; only its runtime/report may exist"
        )
    if is_carrier_gate:
        store, contracts, behavior_contract, input_identities, continuation = (
            _load_carrier_gate_inputs(repo_root, str(carrier_id))
        )
        block_start = str(continuation["window"]["start"])
        block_end = str(continuation["window"]["end_exclusive"])
    elif is_v12:
        store, contracts, behavior_contract, input_identities, continuation = (
            _load_v12_inputs(repo_root)
        )
        block_start = str(continuation["window"]["start"])
        block_end = str(continuation["window"]["end_exclusive"])
    elif is_v11:
        store, contracts, behavior_contract, input_identities, continuation = (
            _load_v11_inputs(repo_root)
        )
        block_start = str(continuation["window"]["start"])
        block_end = str(continuation["window"]["end_exclusive"])
    elif is_canary:
        store, contracts, behavior_contract, input_identities, continuation = (
            _load_aggtrades_canary_inputs(repo_root)
        )
        block_start = str(continuation["window"]["start"])
        block_end = str(continuation["window"]["end_exclusive"])
    else:
        store, contracts, behavior_contract, input_identities, continuation = (
            _load_bound_inputs(repo_root)
        )
        block_start = ADAPTIVE_START
        block_end = ADAPTIVE_END
    registry = TypedExpressionRegistry(contracts)
    compiler_binding = _compiler_binding(repo_root)
    environment = _environment_fingerprint()
    if is_carrier_gate:
        frozen = _carrier_gate_frozen_contract(
            source_sha=source_sha,
            compiler_binding=compiler_binding,
            behavior_contract=behavior_contract,
            input_identities=input_identities,
            environment=environment,
            config=continuation,
            contracts=contracts,
        )
    elif is_v12:
        frozen = _v12_frozen_contract(
            source_sha=source_sha,
            compiler_binding=compiler_binding,
            behavior_contract=behavior_contract,
            input_identities=input_identities,
            environment=environment,
            config=continuation,
        )
    elif is_v11:
        frozen = _v11_frozen_contract(
            source_sha=source_sha,
            compiler_binding=compiler_binding,
            behavior_contract=behavior_contract,
            input_identities=input_identities,
            environment=environment,
            config=continuation,
        )
    elif is_canary:
        frozen = _aggtrades_canary_frozen_contract(
            source_sha=source_sha,
            compiler_binding=compiler_binding,
            behavior_contract=behavior_contract,
            input_identities=input_identities,
            environment=environment,
            config=continuation,
        )
    else:
        frozen = _frozen_contract(
            source_sha=source_sha,
            compiler_binding=compiler_binding,
            behavior_contract=behavior_contract,
            input_identities=input_identities,
            environment=environment,
        )
    frozen_hash = str(frozen["frozen_contract_sha256"])
    identities = {
        **input_identities,
        "compiler_identity": compiler_binding,
    }
    cache_root = (
        repo_root / str(continuation["cache"]["root"])
        if is_system_campaign or is_carrier_gate
        else repo_root / str(continuation["cache_root"])
    )

    existing_checkpoints: list[Path] = []
    if runtime_root.exists():
        frozen_path = runtime_root / "frozen_contract.json"
        if not frozen_path.is_file() or _read_json(frozen_path) != frozen:
            raise ValueError("existing runtime has a different frozen contract")
        if (runtime_root / "final_decision.json").is_file():
            raise FileExistsError("Search Engine V1 campaign already completed")
        existing_checkpoints = sorted(
            (runtime_root / "checkpoints").glob("checkpoint_[0-9][0-9][0-9]")
        )
    else:
        runtime_root.mkdir(parents=True)
        _write_json(runtime_root / "frozen_contract.json", frozen)
        _write_json(
            runtime_root / "embedded_preflight.json",
            {
                "schema_version": 1,
                "status": f"READY_FIRST_STRICT_BATCH_COUNTS_TOWARD_{strict_target}",
                "workers_requested": DEFAULT_WORKERS,
                "workers_12_forbidden": True,
                "memory_gate_bytes": MEMORY_GATE_BYTES,
                "available_memory_bytes": int(psutil.virtual_memory().available),
                "strict_candidates_consumed_outside_campaign": 0,
            },
        )

    if existing_checkpoints:
        state, policies, ledger, archive, metrics = _load_checkpoint(
            checkpoint_path=existing_checkpoints[-1],
            registry=registry,
            expected_source_sha=source_sha,
            expected_frozen_hash=frozen_hash,
            expected_identities=identities,
        )
    else:
        state = _new_campaign_state(
            source_sha, frozen_hash, arms=campaign_arms, seeds=SEEDS
        )
        policies = _initial_policies(
            registry, arms=campaign_arms, seeds=SEEDS
        )
        ledger: list[dict[str, Any]] = []
        archive = BehaviorArchive()
        metrics: list[dict[str, Any]] = []

    attempted_ids = set(str(value) for value in state["attempted_exact_ids"])
    active_started = time.perf_counter()
    prior_active_seconds = float(state["wall_elapsed_seconds"])
    preflight_done = _read_json(runtime_root / "embedded_preflight.json").get(
        "status"
    ) not in {
        f"READY_FIRST_STRICT_BATCH_COUNTS_TOWARD_{strict_target}"
    }

    def active_elapsed() -> float:
        return prior_active_seconds + (time.perf_counter() - active_started)

    def enforce_budget(reserve_attempts: int = 0) -> None:
        state["wall_elapsed_seconds"] = active_elapsed()
        if (
            int(state["generation_attempts"]) + int(reserve_attempts)
            > raw_attempt_limit
        ):
            raise _EngineBudgetExhausted("RAW_GENERATION_ATTEMPT_LIMIT")
        if float(state["wall_elapsed_seconds"]) >= wall_time_limit:
            raise _EngineBudgetExhausted("ACTIVE_WALL_TIME_LIMIT")

    executor: concurrent.futures.ProcessPoolExecutor | None = None

    def start_executor(workers: int) -> concurrent.futures.ProcessPoolExecutor:
        return concurrent.futures.ProcessPoolExecutor(
            max_workers=workers,
            initializer=_worker_initialize,
            initargs=(
                str(cache_root),
                _contracts_payload(contracts),
                behavior_contract,
                block_start,
                block_end,
                block_role,
            ),
        )

    def stop_executor() -> None:
        nonlocal executor
        if executor is not None:
            executor.shutdown(wait=True, cancel_futures=False)
            executor = None

    try:
        executor = start_executor(int(state["workers"]))
        for checkpoint_index in range(
            int(state["next_checkpoint_index"]), checkpoint_count
        ):
            allocation = (
                dict(CARRIER_GATE_CHECKPOINT_ALLOCATION)
                if is_carrier_gate
                else dict(V12_CHECKPOINT_ALLOCATION)
                if is_v12
                else dict(V11_CHECKPOINT_ALLOCATION)
                if is_v11
                else dict(AGGTRADES_CANARY_CHECKPOINT_ALLOCATION)
                if is_canary
                else _checkpoint_allocation(
                    checkpoint_index, state["arm_states"]
                )
            )
            checkpoint_existing = Counter(
                str(row["arm"])
                for row in ledger
                if int(row["checkpoint_index"]) == checkpoint_index
            )
            target_by_lane = {
                _policy_key(arm, seed): allocation[arm] // len(SEEDS)
                for arm in allocation
                if allocation[arm] > 0
                for seed in SEEDS
            }
            lane_completed = Counter(
                _policy_key(str(row["arm"]), int(row["seed"]))
                for row in ledger
                if int(row["checkpoint_index"]) == checkpoint_index
            )
            arm_completion = Counter(str(row["arm"]) for row in ledger)
            lane_order = sorted(target_by_lane)
            checkpoint_start_count = len(ledger)
            checkpoint_target_count = checkpoint_start_count + (
                checkpoint_size - sum(checkpoint_existing.values())
            )
            while len(ledger) < checkpoint_target_count:
                enforce_budget()
                proposals: list[dict[str, Any]] = []
                scans_without_slot = 0
                batch_target_size = (
                    min(int(state["workers"]), len(lane_order))
                    if is_v12
                    else int(state["workers"])
                )
                balanced_batch_index = int(state["balanced_batch_index"])
                while len(proposals) < batch_target_size:
                    enforce_budget()
                    if all(
                        lane_completed[key]
                        + sum(proposal["policy_key"] == key for proposal in proposals)
                        >= target
                        for key, target in target_by_lane.items()
                    ):
                        break
                    if is_v12:
                        policy_key, next_cursor = _balanced_lane_choice(
                            lane_order=lane_order,
                            lane_completed=lane_completed,
                            proposals=proposals,
                            target_by_lane=target_by_lane,
                            scheduler_cursor=int(state["scheduler_cursor"]),
                        )
                        state["scheduler_cursor"] = next_cursor
                        if policy_key is None:
                            break
                    else:
                        policy_key = lane_order[
                            int(state["scheduler_cursor"]) % len(lane_order)
                        ]
                        state["scheduler_cursor"] = (
                            int(state["scheduler_cursor"]) + 1
                        )
                    if any(
                        proposal["policy_key"] == policy_key
                        for proposal in proposals
                    ):
                        scans_without_slot += 1
                        if scans_without_slot > len(lane_order) * 2:
                            break
                        continue
                    if (
                        lane_completed[policy_key]
                        + sum(
                            proposal["policy_key"] == policy_key
                            for proposal in proposals
                        )
                        >= target_by_lane[policy_key]
                    ):
                        scans_without_slot += 1
                        if scans_without_slot > len(lane_order) * 2:
                            break
                        continue
                    scans_without_slot = 0
                    arm, seed_text = policy_key.rsplit("|", 1)
                    seed = int(seed_text)
                    policy = policies[policy_key]
                    enforce_budget(MAX_SINGLE_PROPOSAL_RAW_ATTEMPTS)
                    proposal_cpu_started = time.process_time()
                    try:
                        candidate, metadata = _policy_propose(policy, archive)
                    except (RuntimeError, ValueError) as failure:
                        proposal_cpu = time.process_time() - proposal_cpu_started
                        failed_raw_attempts = int(
                            getattr(failure, "raw_attempts", 1)
                        )
                        failed_compile_valid_attempts = int(
                            getattr(failure, "compile_valid_attempts", 0)
                        )
                        _increment_counter(
                            state,
                            arm,
                            "generation_attempts",
                            failed_raw_attempts,
                        )
                        _increment_counter(
                            state,
                            arm,
                            "compile_valid",
                            failed_compile_valid_attempts,
                        )
                        state["arm_counters"][arm]["cpu_seconds"] += proposal_cpu
                        _failure(
                            state,
                            arm,
                            "PROPOSAL_" + type(failure).__name__,
                        )
                        continue
                    raw_attempts = int(metadata["raw_attempts"])
                    compile_valid_attempts = int(
                        metadata.get("compile_valid_attempts", raw_attempts)
                    )
                    _increment_counter(
                        state, arm, "generation_attempts", raw_attempts
                    )
                    _increment_counter(
                        state, arm, "compile_valid", compile_valid_attempts
                    )
                    expression_verified = _candidate_rebuild_verified(
                        registry,
                        candidate,
                        field_role_surface(contracts)["roles"],
                    )
                    if not expression_verified:
                        attempted_ids.add(candidate.candidate_id)
                        _policy_reject(policy, candidate)
                        _failure(state, arm, "EXPRESSION_HASH_REPLAY")
                        state["arm_counters"][arm]["cpu_seconds"] += (
                            time.process_time() - proposal_cpu_started
                        )
                        continue
                    if candidate.candidate_id in attempted_ids:
                        _policy_reject(policy, candidate)
                        _failure(state, arm, "GLOBAL_EXACT_DUPLICATE")
                        state["arm_counters"][arm]["cpu_seconds"] += (
                            time.process_time() - proposal_cpu_started
                        )
                        continue
                    attempted_ids.add(candidate.candidate_id)
                    if is_system_campaign and not is_carrier_gate and not (
                        set(candidate.raw_fields)
                        & set(AGGTRADES_SYSTEM_CANARY_FIELDS)
                    ):
                        _policy_reject(policy, candidate)
                        _failure(state, arm, "AGGTRADES_INPUT_REQUIRED")
                        state["arm_counters"][arm]["cpu_seconds"] += (
                            time.process_time() - proposal_cpu_started
                        )
                        continue
                    _increment_counter(state, arm, "exact_unique", 1)
                    proposal_cpu = time.process_time() - proposal_cpu_started
                    state["arm_counters"][arm]["cpu_seconds"] += proposal_cpu
                    proposals.append(
                        {
                            **metadata,
                            "policy_key": policy_key,
                            "arm": arm,
                            "seed": seed,
                            "candidate": candidate,
                            "expression_hash_verified": expression_verified,
                            "proposal_cpu_seconds": proposal_cpu,
                            "generation_attempt_ordinal": int(
                                state["generation_attempts"]
                            ),
                            "checkpoint_completion_ordinal": len(ledger)
                            - checkpoint_start_count
                            + len(proposals)
                            + 1,
                            "balanced_batch_index": (
                                balanced_batch_index if is_v12 else None
                            ),
                            "balanced_batch_slot": (
                                len(proposals) if is_v12 else None
                            ),
                            "balanced_batch_size": (
                                batch_target_size if is_v12 else None
                            ),
                        }
                    )
                if not proposals:
                    continue
                if is_v12 and len(proposals) != V12_BALANCED_BATCH_SIZE:
                    raise _EngineBudgetExhausted(
                        "V12_BALANCED_BATCH_UNDERFILLED"
                    )
                if is_v12:
                    state["scheduler_cursor"] = (
                        int(state["scheduler_cursor"]) + 1
                    )
                assert executor is not None
                future_rows = [
                    (
                        proposal,
                        executor.submit(
                            _worker_evaluate, proposal["candidate"].to_dict()
                        ),
                    )
                    for proposal in proposals
                ]
                worker_results = [
                    (proposal, future.result()) for proposal, future in future_rows
                ]
                memory_failure = False
                batch_peak_rss = 0
                for proposal, worker in worker_results:
                    arm = str(proposal["arm"])
                    policy = policies[str(proposal["policy_key"])]
                    candidate = proposal["candidate"]
                    state["arm_counters"][arm]["cpu_seconds"] += float(
                        worker["process_cpu_seconds"]
                    )
                    completion_cpu_started = time.process_time()
                    batch_peak_rss = max(
                        batch_peak_rss, int(worker["worker_rss_bytes"])
                    )
                    evaluation = worker["evaluation"]
                    if evaluation is None:
                        _policy_reject(policy, candidate)
                        reason = str(worker["error"] or "PAIR_EVALUATION_FAILED")
                        _failure(state, arm, reason.split(":", 1)[0])
                        memory_failure = memory_failure or bool(
                            worker["memory_error"]
                        )
                        state["arm_counters"][arm]["cpu_seconds"] += (
                            time.process_time() - completion_cpu_started
                        )
                        continue
                    completion_ordinal = len(ledger) + 1
                    arm_completion[arm] += 1
                    archive_row, new_family = archive.observe(
                        candidate=candidate,
                        evaluation=evaluation,
                        arm=arm,
                        seed=int(proposal["seed"]),
                        completion_ordinal=completion_ordinal,
                        checkpoint_index=checkpoint_index,
                    )
                    proposal["family_member_count_at_completion"] = int(
                        archive.family_counts[
                            str(archive_row["behavior_family_id"])
                        ]
                    )
                    policy_family_counts = state.setdefault(
                        "policy_local_family_counts", {}
                    ).setdefault(str(proposal["policy_key"]), {})
                    local_family_id = str(archive_row["behavior_family_id"])
                    local_family_count = int(
                        policy_family_counts.get(local_family_id, 0)
                    ) + 1
                    policy_family_counts[local_family_id] = local_family_count
                    proposal[
                        "new_policy_local_behavior_family_at_completion"
                    ] = local_family_count == 1
                    proposal[
                        "policy_local_family_count_at_completion"
                    ] = local_family_count
                    policy_archive_row = {
                        **archive_row,
                        "operation": proposal["operation"],
                        "parent_ids": list(proposal["parent_ids"]),
                        "transition_key": proposal.get("transition_key"),
                        "new_policy_local_behavior_family_at_completion": bool(
                            proposal[
                                "new_policy_local_behavior_family_at_completion"
                            ]
                        ),
                    }
                    if (
                        isinstance(policy, TypedEvolutionV2)
                        and policy.parameters.get(
                            "campaign_local_transition_collision_control"
                        )
                        is True
                        and str(proposal["operation"])
                        == "COMPATIBLE_SKELETON_VARIANT_MUTATION"
                    ):
                        policy.observe_transition(
                            transition_key=str(
                                proposal.get("transition_key") or ""
                            ),
                            new_family=bool(
                                proposal[
                                    "new_policy_local_behavior_family_at_completion"
                                ]
                            ),
                            block_after_collisions=int(
                                policy.parameters[
                                    "transition_block_after_collisions"
                                ]
                            ),
                        )
                    _policy_observe(
                        policy,
                        candidate=candidate,
                        reward=float(evaluation["pair_reward"]),
                        archive_row=policy_archive_row,
                    )
                    _increment_counter(state, arm, "matched_control_valid", 1)
                    _increment_counter(state, arm, "strict_evaluated", 1)
                    lane_completed[str(proposal["policy_key"])] += 1
                    ledger_row = _ledger_row(
                        candidate=candidate,
                        evaluation=evaluation,
                        proposal=proposal,
                        archive_row=archive_row,
                        new_family=new_family,
                        state_hash_after=policy.state_hash(),
                        checkpoint_index=checkpoint_index,
                        completion_ordinal=completion_ordinal,
                        arm_completion_ordinal=arm_completion[arm],
                        worker=worker,
                    )
                    completion_cpu = time.process_time() - completion_cpu_started
                    state["arm_counters"][arm]["cpu_seconds"] += completion_cpu
                    ledger_row["archive_completion_cpu_seconds"] = completion_cpu
                    ledger.append(ledger_row)
                if not preflight_done:
                    available_memory = int(psutil.virtual_memory().available)
                    projected = (
                        batch_peak_rss * DEFAULT_WORKERS
                        + int(psutil.Process(os.getpid()).memory_info().rss)
                    )
                    fallback = bool(
                        memory_failure
                        or projected > MEMORY_GATE_BYTES
                        or available_memory < MEMORY_GATE_BYTES
                    )
                    preflight = {
                        "schema_version": 1,
                        "status": "PASS_10_WORKERS"
                        if not fallback
                        else "MEMORY_FAIL_CLOSED_FALLBACK_8",
                        "workers_requested": DEFAULT_WORKERS,
                        "workers_selected": FALLBACK_WORKERS
                        if fallback
                        else DEFAULT_WORKERS,
                        "workers_12_forbidden": True,
                        "strict_candidates_consumed_outside_campaign": 0,
                        "first_batch_candidates": len(proposals),
                        "first_batch_strict_completed": sum(
                            worker["evaluation"] is not None
                            for _, worker in worker_results
                        ),
                        "peak_worker_rss_bytes": batch_peak_rss,
                        "projected_10_worker_plus_parent_rss_bytes": projected,
                        "available_memory_bytes": available_memory,
                        "memory_gate_bytes": MEMORY_GATE_BYTES,
                    }
                    _write_json(runtime_root / "embedded_preflight.json", preflight)
                    preflight_done = True
                    if fallback:
                        stop_executor()
                        state["workers"] = FALLBACK_WORKERS
                        state["memory_fallback_used"] = True
                        executor = start_executor(FALLBACK_WORKERS)
                elif memory_failure:
                    if int(state["workers"]) == DEFAULT_WORKERS:
                        stop_executor()
                        state["workers"] = FALLBACK_WORKERS
                        state["memory_fallback_used"] = True
                        executor = start_executor(FALLBACK_WORKERS)
                    else:
                        raise _EngineBudgetExhausted(
                            "MEMORY_ERROR_RECURRED_AT_8_WORKERS"
                        )
                if is_v12:
                    state["balanced_batch_index"] = balanced_batch_index + 1
                state["attempted_exact_ids"] = sorted(attempted_ids)
                state["wall_elapsed_seconds"] = active_elapsed()
                if (
                    int(state["generation_attempts"]) > raw_attempt_limit
                    or float(state["wall_elapsed_seconds"]) > wall_time_limit
                ):
                    raise _EngineBudgetExhausted(
                        "RAW_OR_WALL_BUDGET_EXCEEDED_AFTER_WORKER_BATCH"
                    )
                if len(ledger) % 100 == 0:
                    print(
                        json.dumps(
                            {
                                "event": "search_engine_v1_progress",
                                "checkpoint_index": checkpoint_index,
                                "strict_evaluated": len(ledger),
                                "generation_attempts": state[
                                    "generation_attempts"
                                ],
                                "behavior_families": len(
                                    archive.champion_by_family
                                ),
                                "workers": state["workers"],
                            },
                            sort_keys=True,
                        ),
                        flush=True,
                    )

            checkpoint_rows = [
                row
                for row in ledger
                if int(row["checkpoint_index"]) == checkpoint_index
            ]
            cem_arms = tuple(
                arm
                for arm in campaign_arms
                if arm
                in {
                    "hierarchical_typed_cem_v2",
                    "behavior_niched_cem_v2_1",
                }
            )
            evolution_adaptation_arms = tuple(
                arm
                for arm in campaign_arms
                if arm
                in {
                    "behavior_niched_evolution_v2_1",
                    "collision_controlled_evolution_v2_2",
                }
            )
            for seed in SEEDS:
                for arm in cem_arms:
                    policy = policies[_policy_key(arm, seed)]
                    assert isinstance(policy, HierarchicalTypedCEMV2)
                    policy.update(
                        [
                            row
                            for row in checkpoint_rows
                            if row["arm"] == arm
                            and int(row["seed"]) == seed
                        ]
                    )
                for arm in evolution_adaptation_arms:
                    policy = policies[_policy_key(arm, seed)]
                    assert isinstance(policy, TypedEvolutionV2)
                    policy.update_operator_productivity(
                        [
                            row
                            for row in checkpoint_rows
                            if row["arm"] == arm
                            and int(row["seed"]) == seed
                        ]
                    )
            state["next_checkpoint_index"] = checkpoint_index + 1
            state["wall_elapsed_seconds"] = active_elapsed()
            checkpoint_metrics = _metrics_rows(
                checkpoint_index=checkpoint_index,
                ledger=ledger,
                archive=archive,
                state=state,
                policies=policies,
                comparison_arms=(
                    CARRIER_GATE_ARMS
                    if is_carrier_gate
                    else V12_ARMS
                    if is_v12
                    else V11_ARMS
                    if is_v11
                    else AGGTRADES_CANARY_ARMS
                    if is_canary
                    else None
                ),
            )
            gates = (
                {}
                if is_system_campaign
                else _apply_exit_gate(
                    checkpoint_index=checkpoint_index,
                    checkpoint_metrics=checkpoint_metrics,
                    state=state,
                )
            )
            metrics.extend(checkpoint_metrics)
            _write_top_level_artifacts(
                runtime_root=runtime_root,
                ledger=ledger,
                archive=archive,
                metrics=metrics,
            )
            checkpoint_path = _write_checkpoint(
                runtime_root=runtime_root,
                label=f"checkpoint_{checkpoint_index:03d}",
                checkpoint_index=checkpoint_index,
                registry=registry,
                state=state,
                policies=policies,
                ledger=ledger,
                archive=archive,
                metrics=metrics,
                identities=identities,
            )
            state, policies, ledger, archive, metrics = _load_checkpoint(
                checkpoint_path=checkpoint_path,
                registry=registry,
                expected_source_sha=source_sha,
                expected_frozen_hash=frozen_hash,
                expected_identities=identities,
            )
            attempted_ids = set(str(value) for value in state["attempted_exact_ids"])
            print(
                json.dumps(
                    {
                        "event": "search_engine_v1_checkpoint_complete",
                        "checkpoint": checkpoint_path.name,
                        "strict_evaluated": len(ledger),
                        "behavior_families": len(archive.champion_by_family),
                        "arm_states": state["arm_states"],
                        "exit_gates": gates,
                        "restore_verified": True,
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
        stop_executor()
    except _EngineBudgetExhausted as failure:
        stop_executor()
        state["attempted_exact_ids"] = sorted(attempted_ids)
        state["wall_elapsed_seconds"] = active_elapsed()
        _write_top_level_artifacts(
            runtime_root=runtime_root,
            ledger=ledger,
            archive=archive,
            metrics=metrics,
        )
        partial = _write_checkpoint(
            runtime_root=runtime_root,
            label="checkpoint_budget_exhausted",
            checkpoint_index=int(state["next_checkpoint_index"]),
            registry=registry,
            state=state,
            policies=policies,
            ledger=ledger,
            archive=archive,
            metrics=metrics,
            identities=identities,
        )
        decision = {
            "schema_version": 1,
            "status": "ENGINE_BUDGET_EXHAUSTED",
            "reason": str(failure),
            "strict_evaluated_count": len(ledger),
            "generation_attempts": int(state["generation_attempts"]),
            "active_wall_seconds": float(state["wall_elapsed_seconds"]),
            "checkpoint": partial.name,
            "parameters_changed": False,
            "seed_changed": False,
            "rescue_rerun_started": False,
            "sealed_reads": 0,
        }
        _write_json(runtime_root / "final_decision.json", decision)
        return {"result": "ENGINE_BUDGET_EXHAUSTED", **decision}
    finally:
        stop_executor()

    if len(ledger) != strict_target:
        raise AssertionError(
            f"Search Engine V1 ended without exactly {strict_target:,} strict candidates"
        )
    state["wall_elapsed_seconds"] = active_elapsed()
    decision = (
        _carrier_gate_final_decision(
            source_sha=source_sha,
            carrier_id=str(carrier_id),
            state=state,
            ledger=ledger,
            archive=archive,
            metrics=metrics,
            runtime_root=runtime_root,
        )
        if is_carrier_gate
        else _v12_final_decision(
            source_sha=source_sha,
            state=state,
            ledger=ledger,
            archive=archive,
            metrics=metrics,
            runtime_root=runtime_root,
        )
        if is_v12
        else _v11_final_decision(
            source_sha=source_sha,
            state=state,
            ledger=ledger,
            archive=archive,
            metrics=metrics,
            runtime_root=runtime_root,
        )
        if is_v11
        else _aggtrades_canary_final_decision(
            source_sha=source_sha,
            state=state,
            ledger=ledger,
            archive=archive,
            metrics=metrics,
            runtime_root=runtime_root,
        )
        if is_canary
        else _final_decision(
            source_sha=source_sha,
            state=state,
            ledger=ledger,
            archive=archive,
            metrics=metrics,
            runtime_root=runtime_root,
        )
    )
    _write_json(runtime_root / "final_decision.json", decision)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        (
            _carrier_gate_report_text(decision)
            if is_carrier_gate
            else _v12_report_text(decision)
            if is_v12
            else _v11_report_text(decision)
            if is_v11
            else _aggtrades_canary_report_text(decision)
            if is_canary
            else _report_text(decision)
        ),
        encoding="utf-8",
        newline="\n",
    )
    manifest = _final_manifest(
        repo_root=repo_root,
        runtime_root=runtime_root,
        report_path=report_path,
        source_sha=source_sha,
        frozen_hash=frozen_hash,
        identities=identities,
        state=state,
        epoch_id=(
            CARRIER_GATE_EPOCH_ID
            if is_carrier_gate
            else V12_EPOCH_ID
            if is_v12
            else V11_EPOCH_ID
            if is_v11
            else AGGTRADES_CANARY_EPOCH_ID
            if is_canary
            else EPOCH_ID
        ),
        base_sha=(source_sha if is_system_campaign else BASE_SHA),
        continuation=(
            "python -m alphafactory_crypto.broad_search.search_engine_v1 "
            f"check-carrier-gate --carrier-id {carrier_id} --runtime-date {runtime_date}"
            if is_carrier_gate
            else "python -m alphafactory_crypto.broad_search.search_engine_v1 "
            f"check-v12 --runtime-date {runtime_date}"
            if is_v12
            else "python -m alphafactory_crypto.broad_search.search_engine_v1 "
            f"check-v11 --runtime-date {runtime_date}"
            if is_v11
            else "python -m alphafactory_crypto.broad_search.search_engine_v1 "
            f"check-canary --runtime-date {runtime_date}"
            if is_canary
            else "python -m alphafactory_crypto.broad_search.search_engine_v1 "
            f"check --runtime-date {runtime_date}"
        ),
    )
    _write_json(runtime_root / "run_manifest.json", manifest)
    run_result = (
        "PASS"
        if is_carrier_gate
        or (not is_v11 and not is_v12)
        or decision["status"]
        in {
            "PASS_SEARCH_ENGINE_V1_1_COMPLETED",
            "PASS_SEARCH_ENGINE_V1_2_COMPLETED",
        }
        else "ENGINE_BUDGET_EXHAUSTED"
        if decision["status"] == "ENGINE_BUDGET_EXHAUSTED"
        else "FAIL"
    )
    return {
        "result": run_result,
        "status": decision["status"],
        "producer_source_sha": source_sha,
        "strict_evaluated_count": len(ledger),
        "generation_attempts": int(state["generation_attempts"]),
        "checkpoint_count": checkpoint_count,
        "behavior_family_count": len(archive.champion_by_family),
        "artifact_bundle_sha256": manifest["artifact_bundle_sha256"],
        "sealed_reads": 0,
    }


def check_engine(
    repo_root: Path, *, runtime_date: str = DEFAULT_RUNTIME_DATE
) -> dict[str, Any]:
    runtime_root = repo_root / f"runtime/crypto_search_engine_v1_{runtime_date}"
    report_path = repo_root / f"reports/CRYPTO_SEARCH_ENGINE_V1_{runtime_date}.md"
    errors: list[str] = []
    required = (
        "frozen_contract.json",
        "embedded_preflight.json",
        "candidate_ledger.parquet",
        "behavior_archive.parquet",
        "behavior_family_summary.json",
        "arm_checkpoint_metrics.parquet",
        "final_decision.json",
        "run_manifest.json",
    )
    for name in required:
        if not (runtime_root / name).is_file():
            errors.append(f"missing:{name}")
    if not report_path.is_file():
        errors.append("missing:report")
    if errors:
        return {"result": "FAIL", "errors": errors}

    frozen = _read_json(runtime_root / "frozen_contract.json")
    decision = _read_json(runtime_root / "final_decision.json")
    manifest = _read_json(runtime_root / "run_manifest.json")
    preflight = _read_json(runtime_root / "embedded_preflight.json")
    ledger = pd.read_parquet(runtime_root / "candidate_ledger.parquet")
    archive = pd.read_parquet(runtime_root / "behavior_archive.parquet")
    metrics = pd.read_parquet(runtime_root / "arm_checkpoint_metrics.parquet")
    family_summary = _read_json(runtime_root / "behavior_family_summary.json")

    frozen_without_hash = {
        key: value for key, value in frozen.items() if key != "frozen_contract_sha256"
    }
    if _payload_sha(frozen_without_hash) != frozen.get("frozen_contract_sha256"):
        errors.append("frozen_contract_sha256")
    if frozen.get("surface") != {
        "context_id": "BROAD_PANEL_BASELINE",
        "fields": 39,
        "core3_fields": 0,
        "joint_120_channel_panel": False,
    }:
        errors.append("broad39_surface")
    boundaries = frozen.get("boundaries", {})
    if (
        boundaries.get("sealed_reads") != 0
        or any(
            bool(boundaries.get(key))
            for key in (
                "report_only_feedback",
                "challenge",
                "recent",
                "may_stress",
                "forward",
                "promotion",
                "cross_sprint_adaptive_memory",
            )
        )
    ):
        errors.append("sealed_boundary")
    if frozen.get("behavior_descriptor", {}).get("outcome_fields_in_identity") != []:
        errors.append("behavior_outcome_identity")
    post_audit_holds: list[str] = []
    if frozen.get("behavior_descriptor", {}).get(
        "pit_regime_source_validation"
    ) != "CROSS_SECTION_CONSTANT_AND_EQUAL_TO_FINITE_ASSET_SUPPORT":
        post_audit_holds.append("LEGACY_UNVALIDATED_ACTIVE_UNIVERSE_REGIME")
    if frozen.get("evaluator_contract", {}).get("lcb_contract", {}).get(
        "authority"
    ) != "NEWEY_WEST_BARTLETT":
        post_audit_holds.append("LEGACY_IID_LCB_ON_OVERLAPPING_HORIZON")
    if "primary_month_metrics_json" not in ledger.columns:
        post_audit_holds.append("LEGACY_MATCHED_WATERFALL_NOT_PERSISTED")
    if preflight.get("strict_candidates_consumed_outside_campaign") != 0:
        errors.append("preflight_external_budget")
    if preflight.get("workers_selected") not in {DEFAULT_WORKERS, FALLBACK_WORKERS}:
        errors.append("worker_selection")

    if len(ledger) != STRICT_TARGET:
        errors.append("strict_count")
    if ledger["candidate_id"].nunique() != STRICT_TARGET:
        errors.append("exact_unique")
    for column in (
        "compile_valid",
        "exact_unique",
        "matched_control_valid",
        "strict_cost_evaluated",
        "expression_hash_verified",
    ):
        if column not in ledger or not bool(ledger[column].fillna(False).all()):
            errors.append(f"ledger_gate:{column}")
    receipt_rows = ledger[ledger["receipt_json"].notna()]
    if receipt_rows.empty or not bool(receipt_rows["receipt_verified"].eq(True).all()):
        errors.append("receipt_verification")
    for operation in (
        "EFFECTIVE_GENE_MUTATION_1_TO_3",
        "COMPATIBLE_SKELETON_VARIANT_MUTATION",
        "ONE_POINT_HOMOLOGOUS_GENE_BUNDLE_CROSSOVER",
    ):
        if not bool((ledger["operation"] == operation).any()):
            errors.append(f"operation_not_executed:{operation}")
    if ledger["behavior_family_id"].isna().any():
        errors.append("behavior_identity")
    if len(archive) != STRICT_TARGET:
        errors.append("archive_row_count")
    champions = archive[archive["is_family_champion"].fillna(False)]
    if champions["behavior_family_id"].nunique() != archive[
        "behavior_family_id"
    ].nunique():
        errors.append("archive_family_champion")
    if family_summary.get("family_count") != int(
        archive["behavior_family_id"].nunique()
    ):
        errors.append("family_summary_count")

    checkpoints = sorted(
        (runtime_root / "checkpoints").glob("checkpoint_[0-9][0-9][0-9]")
    )
    if len(checkpoints) != CHECKPOINT_COUNT:
        errors.append("checkpoint_count")
    for index, checkpoint in enumerate(checkpoints):
        checkpoint_manifest = _read_json(checkpoint / "manifest.json")
        if int(checkpoint_manifest.get("completed_ledger_row_count", -1)) != (
            index + 1
        ) * CHECKPOINT_SIZE:
            errors.append(f"checkpoint_rows:{index}")
        if checkpoint_manifest.get("source_sha") != manifest.get(
            "producer_source_sha"
        ):
            errors.append(f"checkpoint_source:{index}")
        if checkpoint_manifest.get("frozen_contract_sha256") != frozen.get(
            "frozen_contract_sha256"
        ):
            errors.append(f"checkpoint_contract:{index}")
        if checkpoint_manifest.get("restore_verified") is not True:
            errors.append(f"checkpoint_restore:{index}")
        for record in checkpoint_manifest.get("files", []):
            path = checkpoint / str(record["name"])
            if (
                not path.is_file()
                or path.stat().st_size != int(record["bytes"])
                or sha256_file(path) != str(record["sha256"])
            ):
                errors.append(f"checkpoint_file:{index}:{record['name']}")

    initial = ledger[ledger["checkpoint_index"] == 0].groupby("arm").size().to_dict()
    if initial != {arm: 400 for arm in FIRST_CHECKPOINT_ARMS}:
        errors.append("checkpoint_000_arm_contract")
    if bool(
        ledger[
            (ledger["checkpoint_index"] > 0)
            & ledger["arm"].isin(
                ["cem_distribution_v1", "evolutionary_typed_v1"]
            )
        ].shape[0]
    ):
        errors.append("v1_control_did_not_exit")
    if set(metrics["checkpoint_index"].astype(int).unique()) != set(
        range(CHECKPOINT_COUNT)
    ):
        errors.append("checkpoint_metrics")
    if int(decision.get("generation_attempts", RAW_ATTEMPT_LIMIT + 1)) > RAW_ATTEMPT_LIMIT:
        errors.append("raw_attempt_budget")
    if float(decision.get("active_wall_seconds", WALL_TIME_LIMIT_SECONDS + 1)) > WALL_TIME_LIMIT_SECONDS:
        errors.append("wall_time_budget")
    if decision.get("status") != "PASS" or decision.get("sealed_reads") != 0:
        errors.append("final_decision")
    if decision.get("next_arena_started") is not False:
        errors.append("next_arena_boundary")
    if decision.get("success_questions", {}).get("continuous_checkpoint_resume") != "YES_EXACT_RESTORE_VERIFIED":
        errors.append("resume_answer")

    if manifest.get("strict_evaluated_count") != STRICT_TARGET:
        errors.append("manifest_strict_count")
    if manifest.get("frozen_contract_sha256") != frozen.get(
        "frozen_contract_sha256"
    ):
        errors.append("manifest_contract")
    if manifest.get("sealed_reads") != 0:
        errors.append("manifest_sealed_reads")
    if _payload_sha(manifest.get("artifacts", [])) != manifest.get(
        "artifact_bundle_sha256"
    ):
        errors.append("manifest_bundle")
    for record in manifest.get("artifacts", []):
        path = repo_root / str(record["path"])
        if (
            not path.is_file()
            or path.stat().st_size != int(record["bytes"])
            or sha256_file(path) != str(record["sha256"])
        ):
            errors.append(f"manifest_artifact:{record['path']}")
    try:
        subprocess.check_call(
            [
                "git",
                "cat-file",
                "-e",
                f"{manifest['producer_source_sha']}^{{commit}}",
            ],
            cwd=repo_root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        errors.append("producer_source_commit")
    engineering_result = "PASS" if not errors else "FAIL"
    return {
        "result": engineering_result,
        "errors": errors,
        "engineering_integrity": engineering_result,
        "component_qualification": (
            "HOLD_POST_AUDIT_REMEDIATION_REQUIRED"
            if post_audit_holds
            else "HOLD_SEPARATE_FRESH_STATE_REQUALIFICATION_REQUIRED"
        ),
        "post_audit_holds": post_audit_holds,
        "future_new_data_arena_qualified_arms": [],
        "historical_diagnostic_qualification_only": decision.get(
            "future_new_data_arena_qualified_arms", []
        ),
        "producer_source_sha": manifest.get("producer_source_sha"),
        "strict_evaluated_count": len(ledger),
        "generation_attempts": decision.get("generation_attempts"),
        "checkpoint_count": len(checkpoints),
        "behavior_family_count": int(archive["behavior_family_id"].nunique()),
        "artifact_bundle_sha256": manifest.get("artifact_bundle_sha256"),
        "sealed_reads": decision.get("sealed_reads"),
    }


def check_aggtrades_canary(
    repo_root: Path,
    *,
    runtime_date: str = AGGTRADES_CANARY_DEFAULT_RUNTIME_DATE,
) -> dict[str, Any]:
    runtime_root = (
        repo_root / f"runtime/crypto_aggtrades_system_canary_v1_{runtime_date}"
    )
    report_path = (
        repo_root / f"reports/CRYPTO_AGGTRADES_SYSTEM_CANARY_V1_{runtime_date}.md"
    )
    errors: list[str] = []
    required = (
        "frozen_contract.json",
        "embedded_preflight.json",
        "candidate_ledger.parquet",
        "behavior_archive.parquet",
        "behavior_family_summary.json",
        "arm_checkpoint_metrics.parquet",
        "final_decision.json",
        "run_manifest.json",
    )
    for name in required:
        if not (runtime_root / name).is_file():
            errors.append(f"missing:{name}")
    if not report_path.is_file():
        errors.append("missing:report")
    if errors:
        return {"result": "FAIL", "errors": errors}
    frozen = _read_json(runtime_root / "frozen_contract.json")
    decision = _read_json(runtime_root / "final_decision.json")
    manifest = _read_json(runtime_root / "run_manifest.json")
    preflight = _read_json(runtime_root / "embedded_preflight.json")
    ledger = pd.read_parquet(runtime_root / "candidate_ledger.parquet")
    archive = pd.read_parquet(runtime_root / "behavior_archive.parquet")
    metrics = pd.read_parquet(runtime_root / "arm_checkpoint_metrics.parquet")
    family_summary = _read_json(runtime_root / "behavior_family_summary.json")
    frozen_without_hash = {
        key: value
        for key, value in frozen.items()
        if key != "frozen_contract_sha256"
    }
    if _payload_sha(frozen_without_hash) != frozen.get("frozen_contract_sha256"):
        errors.append("frozen_contract_sha256")
    if frozen.get("authorization") != (
        "ONE_FRESH_STATE_2000_AGGTRADES_SYSTEM_CANARY"
    ):
        errors.append("authorization")
    if frozen.get("surface", {}).get(
        "every_candidate_requires_aggtrades_input"
    ) is not True:
        errors.append("aggtrades_candidate_gate")
    boundaries = frozen.get("boundaries", {})
    if boundaries.get("sealed_reads") != 0 or any(
        bool(boundaries.get(key))
        for key in (
            "challenge",
            "recent",
            "may_stress",
            "forward",
            "promotion",
            "cross_sprint_adaptive_memory",
            "latent_priority",
            "relational_training",
        )
    ):
        errors.append("sealed_boundary")
    if preflight.get("workers_selected") not in {
        DEFAULT_WORKERS,
        FALLBACK_WORKERS,
    }:
        errors.append("worker_selection")
    if preflight.get("strict_candidates_consumed_outside_campaign") != 0:
        errors.append("preflight_external_budget")
    if len(ledger) != AGGTRADES_CANARY_STRICT_TARGET:
        errors.append("strict_count")
    if ledger["candidate_id"].nunique() != AGGTRADES_CANARY_STRICT_TARGET:
        errors.append("exact_unique")
    for column in (
        "compile_valid",
        "exact_unique",
        "matched_control_valid",
        "strict_cost_evaluated",
        "expression_hash_verified",
    ):
        if column not in ledger or not bool(ledger[column].fillna(False).all()):
            errors.append(f"ledger_gate:{column}")
    if not all(
        bool(
            set(json.loads(str(value)))
            & set(AGGTRADES_SYSTEM_CANARY_FIELDS)
        )
        for value in ledger["raw_fields_json"]
    ):
        errors.append("candidate_without_aggtrades")
    arm_counts = ledger.groupby("arm").size().to_dict()
    expected_arm_counts = {
        arm: count * AGGTRADES_CANARY_CHECKPOINT_COUNT
        for arm, count in AGGTRADES_CANARY_CHECKPOINT_ALLOCATION.items()
    }
    if arm_counts != expected_arm_counts:
        errors.append("arm_counts")
    for checkpoint_index in range(AGGTRADES_CANARY_CHECKPOINT_COUNT):
        local = (
            ledger[ledger["checkpoint_index"].astype(int).eq(checkpoint_index)]
            .groupby("arm")
            .size()
            .to_dict()
        )
        if local != AGGTRADES_CANARY_CHECKPOINT_ALLOCATION:
            errors.append(f"checkpoint_arm_counts:{checkpoint_index}")
    receipt_rows = ledger[ledger["receipt_json"].notna()]
    if receipt_rows.empty or not bool(
        receipt_rows["receipt_verified"].eq(True).all()
    ):
        errors.append("receipt_verification")
    for operation in (
        "EFFECTIVE_GENE_MUTATION_1_TO_3",
        "COMPATIBLE_SKELETON_VARIANT_MUTATION",
        "ONE_POINT_HOMOLOGOUS_GENE_BUNDLE_CROSSOVER",
    ):
        if not bool(ledger["operation"].eq(operation).any()):
            errors.append(f"operation_not_executed:{operation}")
    if len(archive) != AGGTRADES_CANARY_STRICT_TARGET:
        errors.append("archive_row_count")
    champions = archive[archive["is_family_champion"].fillna(False)]
    if champions["behavior_family_id"].nunique() != archive[
        "behavior_family_id"
    ].nunique():
        errors.append("archive_family_champion")
    if family_summary.get("family_count") != int(
        archive["behavior_family_id"].nunique()
    ):
        errors.append("family_summary_count")
    checkpoints = sorted(
        (runtime_root / "checkpoints").glob("checkpoint_[0-9][0-9][0-9]")
    )
    if len(checkpoints) != AGGTRADES_CANARY_CHECKPOINT_COUNT:
        errors.append("checkpoint_count")
    for index, checkpoint in enumerate(checkpoints):
        checkpoint_manifest = _read_json(checkpoint / "manifest.json")
        if int(checkpoint_manifest.get("completed_ledger_row_count", -1)) != (
            index + 1
        ) * AGGTRADES_CANARY_CHECKPOINT_SIZE:
            errors.append(f"checkpoint_rows:{index}")
        if checkpoint_manifest.get("restore_verified") is not True:
            errors.append(f"checkpoint_restore:{index}")
        for record in checkpoint_manifest.get("files", []):
            path = checkpoint / str(record["name"])
            if (
                not path.is_file()
                or path.stat().st_size != int(record["bytes"])
                or sha256_file(path) != str(record["sha256"])
            ):
                errors.append(f"checkpoint_file:{index}:{record['name']}")
    if set(metrics["checkpoint_index"].astype(int).unique()) != set(
        range(AGGTRADES_CANARY_CHECKPOINT_COUNT)
    ):
        errors.append("checkpoint_metrics")
    if int(
        decision.get(
            "generation_attempts", AGGTRADES_CANARY_RAW_ATTEMPT_LIMIT + 1
        )
    ) > AGGTRADES_CANARY_RAW_ATTEMPT_LIMIT:
        errors.append("raw_attempt_budget")
    if float(
        decision.get(
            "active_wall_seconds",
            AGGTRADES_CANARY_WALL_TIME_LIMIT_SECONDS + 1,
        )
    ) > AGGTRADES_CANARY_WALL_TIME_LIMIT_SECONDS:
        errors.append("wall_time_budget")
    if decision.get("status") != "PASS_SYSTEM_CANARY_COMPLETED":
        errors.append("final_decision")
    if decision.get("research_decision") != (
        "HOLD_RESEARCH_FIXED_RETROSPECTIVE_COHORT"
    ):
        errors.append("research_boundary")
    if decision.get("future_new_data_arena_qualified_arms") != []:
        errors.append("future_arm_qualification")
    if decision.get("sealed_reads") != 0:
        errors.append("sealed_reads")
    if manifest.get("strict_evaluated_count") != AGGTRADES_CANARY_STRICT_TARGET:
        errors.append("manifest_strict_count")
    if manifest.get("frozen_contract_sha256") != frozen.get(
        "frozen_contract_sha256"
    ):
        errors.append("manifest_contract")
    if _payload_sha(manifest.get("artifacts", [])) != manifest.get(
        "artifact_bundle_sha256"
    ):
        errors.append("manifest_bundle")
    for record in manifest.get("artifacts", []):
        path = repo_root / str(record["path"])
        if (
            not path.is_file()
            or path.stat().st_size != int(record["bytes"])
            or sha256_file(path) != str(record["sha256"])
        ):
            errors.append(f"manifest_artifact:{record['path']}")
    try:
        subprocess.check_call(
            [
                "git",
                "cat-file",
                "-e",
                f"{manifest['producer_source_sha']}^{{commit}}",
            ],
            cwd=repo_root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        errors.append("producer_source_commit")
    result = "PASS" if not errors else "FAIL"
    return {
        "result": result,
        "errors": errors,
        "engineering_integrity": result,
        "research_decision": decision.get("research_decision"),
        "producer_source_sha": manifest.get("producer_source_sha"),
        "strict_evaluated_count": len(ledger),
        "generation_attempts": decision.get("generation_attempts"),
        "checkpoint_count": len(checkpoints),
        "behavior_family_count": int(archive["behavior_family_id"].nunique()),
        "artifact_bundle_sha256": manifest.get("artifact_bundle_sha256"),
        "future_new_data_arena_qualified_arms": [],
        "sealed_reads": decision.get("sealed_reads"),
    }


def check_v11(
    repo_root: Path,
    *,
    runtime_date: str = V11_DEFAULT_RUNTIME_DATE,
) -> dict[str, Any]:
    runtime_root = repo_root / f"runtime/crypto_search_engine_v1_1_{runtime_date}"
    report_path = repo_root / f"reports/CRYPTO_SEARCH_ENGINE_V1_1_{runtime_date}.md"
    errors: list[str] = []
    required = (
        "frozen_contract.json",
        "embedded_preflight.json",
        "candidate_ledger.parquet",
        "behavior_archive.parquet",
        "behavior_family_summary.json",
        "arm_checkpoint_metrics.parquet",
        "final_decision.json",
        "run_manifest.json",
    )
    for name in required:
        if not (runtime_root / name).is_file():
            errors.append(f"missing:{name}")
    if not report_path.is_file():
        errors.append("missing:report")
    if errors:
        return {"result": "FAIL", "errors": errors}
    frozen = _read_json(runtime_root / "frozen_contract.json")
    decision = _read_json(runtime_root / "final_decision.json")
    manifest = _read_json(runtime_root / "run_manifest.json")
    preflight = _read_json(runtime_root / "embedded_preflight.json")
    ledger = pd.read_parquet(runtime_root / "candidate_ledger.parquet")
    archive = pd.read_parquet(runtime_root / "behavior_archive.parquet")
    metrics = pd.read_parquet(runtime_root / "arm_checkpoint_metrics.parquet")
    family_summary = _read_json(runtime_root / "behavior_family_summary.json")
    frozen_without_hash = {
        key: value
        for key, value in frozen.items()
        if key != "frozen_contract_sha256"
    }
    if _payload_sha(frozen_without_hash) != frozen.get("frozen_contract_sha256"):
        errors.append("frozen_contract_sha256")
    if frozen.get("authorization") != (
        "ONE_FRESH_STATE_3000_SPENT_DEVELOPMENT_SEARCH_ENGINE_V1_1"
    ):
        errors.append("authorization")
    if frozen.get("surface", {}).get(
        "every_candidate_requires_aggtrades_input"
    ) is not True:
        errors.append("aggtrades_candidate_gate")
    fresh_state = frozen.get("fresh_state", {})
    if any(bool(value) for value in fresh_state.values()):
        errors.append("fresh_state_import")
    boundaries = frozen.get("boundaries", {})
    if boundaries.get("sealed_reads") != 0 or any(
        bool(boundaries.get(key))
        for key in (
            "challenge",
            "recent",
            "may_stress",
            "forward",
            "promotion",
            "cross_sprint_adaptive_memory",
            "latent_priority",
            "relational_training",
        )
    ):
        errors.append("sealed_boundary")
    if preflight.get("workers_selected") not in {
        DEFAULT_WORKERS,
        FALLBACK_WORKERS,
    }:
        errors.append("worker_selection")
    if preflight.get("strict_candidates_consumed_outside_campaign") != 0:
        errors.append("preflight_external_budget")
    if len(ledger) != V11_STRICT_TARGET:
        errors.append("strict_count")
    if ledger["candidate_id"].nunique() != V11_STRICT_TARGET:
        errors.append("exact_unique")
    for column in (
        "compile_valid",
        "exact_unique",
        "matched_control_valid",
        "strict_cost_evaluated",
        "expression_hash_verified",
    ):
        if column not in ledger or not bool(ledger[column].fillna(False).all()):
            errors.append(f"ledger_gate:{column}")
    if not all(
        bool(
            set(json.loads(str(value)))
            & set(AGGTRADES_SYSTEM_CANARY_FIELDS)
        )
        for value in ledger["raw_fields_json"]
    ):
        errors.append("candidate_without_aggtrades")
    arm_counts = ledger.groupby("arm").size().to_dict()
    expected_arm_counts = {
        arm: count * V11_CHECKPOINT_COUNT
        for arm, count in V11_CHECKPOINT_ALLOCATION.items()
    }
    if arm_counts != expected_arm_counts:
        errors.append("arm_counts")
    expected_lane_count = next(iter(V11_CHECKPOINT_ALLOCATION.values())) // len(
        SEEDS
    )
    for checkpoint_index in range(V11_CHECKPOINT_COUNT):
        local = (
            ledger[ledger["checkpoint_index"].astype(int).eq(checkpoint_index)]
            .groupby("arm")
            .size()
            .to_dict()
        )
        if local != V11_CHECKPOINT_ALLOCATION:
            errors.append(f"checkpoint_arm_counts:{checkpoint_index}")
        lane_counts = (
            ledger[
                ledger["checkpoint_index"].astype(int).eq(checkpoint_index)
            ]
            .groupby(["arm", "seed"])
            .size()
            .to_dict()
        )
        expected_lanes = {
            (arm, seed): expected_lane_count
            for arm in V11_ARMS
            for seed in SEEDS
        }
        if lane_counts != expected_lanes:
            errors.append(f"checkpoint_arm_seed_counts:{checkpoint_index}")
    broad_contracts, _, _ = _broad39_registry_contracts(repo_root)
    replay_registry = TypedExpressionRegistry(
        tuple((*broad_contracts, *_aggtrades_canary_contracts()))
    )
    replay_policy = TypedEvolutionV2(
        0,
        replay_registry,
        V21_PARAMETERS["behavior_niched_evolution_v2_1"],
    )
    candidates_by_id = {
        str(row["candidate_id"]): CandidateSpec.from_dict(
            json.loads(str(row["candidate_spec_json"]))
        )
        for row in ledger.to_dict("records")
    }
    receipt_rows = ledger[ledger["receipt_json"].notna()]
    if receipt_rows.empty or not bool(
        receipt_rows["receipt_verified"].eq(True).all()
    ):
        errors.append("receipt_verification")
    for row in receipt_rows.to_dict("records"):
        try:
            child = candidates_by_id[str(row["candidate_id"])]
            parent_ids = json.loads(str(row["parent_ids_json"]))
            parents = tuple(
                candidates_by_id[str(parent_id)] for parent_id in parent_ids
            )
            receipt = json.loads(str(row["receipt_json"]))
            if not replay_policy.verify_receipt(parents, child, receipt):
                errors.append(f"receipt_replay:{row['candidate_id']}")
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            errors.append(f"receipt_replay:{row['candidate_id']}")
    for operation in EVOLUTION_OPERATIONS:
        if not bool(ledger["operation"].eq(operation).any()):
            errors.append(f"operation_not_executed:{operation}")
    if len(archive) != V11_STRICT_TARGET:
        errors.append("archive_row_count")
    champions = archive[archive["is_family_champion"].fillna(False)]
    if champions["behavior_family_id"].nunique() != archive[
        "behavior_family_id"
    ].nunique():
        errors.append("archive_family_champion")
    if family_summary.get("family_count") != int(
        archive["behavior_family_id"].nunique()
    ):
        errors.append("family_summary_count")
    checkpoints = sorted(
        (runtime_root / "checkpoints").glob("checkpoint_[0-9][0-9][0-9]")
    )
    if len(checkpoints) != V11_CHECKPOINT_COUNT:
        errors.append("checkpoint_count")
    checkpoint_policy_frontier_verified = True
    for index, checkpoint in enumerate(checkpoints):
        checkpoint_manifest = _read_json(checkpoint / "manifest.json")
        if int(checkpoint_manifest.get("completed_ledger_row_count", -1)) != (
            index + 1
        ) * V11_CHECKPOINT_SIZE:
            errors.append(f"checkpoint_rows:{index}")
        if checkpoint_manifest.get("restore_verified") is not True:
            errors.append(f"checkpoint_restore:{index}")
        for record in checkpoint_manifest.get("files", []):
            path = checkpoint / str(record["name"])
            if (
                not path.is_file()
                or path.stat().st_size != int(record["bytes"])
                or sha256_file(path) != str(record["sha256"])
            ):
                errors.append(f"checkpoint_file:{index}:{record['name']}")
        try:
            _, restored_policies, _, _, _ = _load_checkpoint(
                checkpoint_path=checkpoint,
                registry=replay_registry,
                expected_source_sha=str(frozen["source_sha"]),
                expected_frozen_hash=str(
                    frozen["frozen_contract_sha256"]
                ),
                expected_identities={
                    **dict(frozen["input_identities"]),
                    "compiler_identity": dict(frozen["compiler_identity"]),
                },
            )
            cem_policies = [
                policy
                for key, policy in restored_policies.items()
                if key.startswith("behavior_niched_cem_v2_1|")
                and isinstance(policy, HierarchicalTypedCEMV2)
            ]
            checkpoint_policy_frontier_verified = bool(
                checkpoint_policy_frontier_verified
                and len(cem_policies) == len(SEEDS)
                and all(
                    policy.parameters.get(
                        "mechanism_stratified_elites"
                    )
                    is True
                    and policy.parameters.get(
                        "skeleton_stratified_elites"
                    )
                    is True
                    and policy.last_elite_mechanism_count > 0
                    and policy.last_elite_skeleton_count > 0
                    for policy in cem_policies
                )
            )
        except (KeyError, TypeError, ValueError):
            errors.append(f"checkpoint_state_replay:{index}")
            checkpoint_policy_frontier_verified = False
    if not checkpoint_policy_frontier_verified:
        errors.append("cem_checkpoint_frontier_state")
    if set(metrics["checkpoint_index"].astype(int).unique()) != set(
        range(V11_CHECKPOINT_COUNT)
    ):
        errors.append("checkpoint_metrics")
    final_evolution = metrics[
        metrics["checkpoint_index"].astype(int).eq(V11_CHECKPOINT_COUNT - 1)
        & metrics["arm"].eq("behavior_niched_evolution_v2_1")
    ]
    final_cem = metrics[
        metrics["checkpoint_index"].astype(int).eq(V11_CHECKPOINT_COUNT - 1)
        & metrics["arm"].eq("behavior_niched_cem_v2_1")
    ]
    if (
        len(final_evolution) != 1
        or int(final_evolution.iloc[0]["operator_update_count"]) <= 0
        or json.loads(
            str(final_evolution.iloc[0]["operator_probabilities_json"])
        )
        == {}
    ):
        errors.append("operator_productivity_update")
    if (
        len(final_cem) != 1
        or int(final_cem.iloc[0]["cem_elite_family_count"]) <= 0
        or int(final_cem.iloc[0]["cem_elite_mechanism_count"]) <= 0
        or int(final_cem.iloc[0]["cem_elite_skeleton_count"]) <= 0
    ):
        errors.append("cem_behavior_niche_update")
    if int(
        decision.get("generation_attempts", V11_RAW_ATTEMPT_LIMIT + 1)
    ) > V11_RAW_ATTEMPT_LIMIT:
        errors.append("raw_attempt_budget")
    if float(
        decision.get(
            "active_wall_seconds", V11_WALL_TIME_LIMIT_SECONDS + 1
        )
    ) > V11_WALL_TIME_LIMIT_SECONDS:
        errors.append("wall_time_budget")
    if decision.get("status") != "PASS_SEARCH_ENGINE_V1_1_COMPLETED":
        errors.append("final_decision")
    if decision.get("research_decision") != (
        "HOLD_RESEARCH_SPENT_FIXED_RETROSPECTIVE_COHORT"
    ):
        errors.append("research_boundary")
    if decision.get("future_new_data_arena_qualified_arms") != []:
        errors.append("future_arm_qualification")
    if decision.get("sealed_reads") != 0:
        errors.append("sealed_reads")
    if manifest.get("strict_evaluated_count") != V11_STRICT_TARGET:
        errors.append("manifest_strict_count")
    if manifest.get("frozen_contract_sha256") != frozen.get(
        "frozen_contract_sha256"
    ):
        errors.append("manifest_contract")
    if _payload_sha(manifest.get("artifacts", [])) != manifest.get(
        "artifact_bundle_sha256"
    ):
        errors.append("manifest_bundle")
    for record in manifest.get("artifacts", []):
        path = repo_root / str(record["path"])
        if (
            not path.is_file()
            or path.stat().st_size != int(record["bytes"])
            or sha256_file(path) != str(record["sha256"])
        ):
            errors.append(f"manifest_artifact:{record['path']}")
    try:
        subprocess.check_call(
            [
                "git",
                "cat-file",
                "-e",
                f"{manifest['producer_source_sha']}^{{commit}}",
            ],
            cwd=repo_root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        errors.append("producer_source_commit")
    result = "PASS" if not errors else "FAIL"
    return {
        "result": result,
        "errors": errors,
        "engineering_integrity": result,
        "research_decision": decision.get("research_decision"),
        "producer_source_sha": manifest.get("producer_source_sha"),
        "strict_evaluated_count": len(ledger),
        "generation_attempts": decision.get("generation_attempts"),
        "checkpoint_count": len(checkpoints),
        "behavior_family_count": int(archive["behavior_family_id"].nunique()),
        "artifact_bundle_sha256": manifest.get("artifact_bundle_sha256"),
        "search_iteration_decision": decision.get(
            "search_iteration_decision", {}
        ),
        "future_new_data_arena_qualified_arms": [],
        "sealed_reads": decision.get("sealed_reads"),
    }


def check_v12(
    repo_root: Path,
    *,
    runtime_date: str = V12_DEFAULT_RUNTIME_DATE,
) -> dict[str, Any]:
    runtime_root = repo_root / f"runtime/crypto_search_engine_v1_2_{runtime_date}"
    report_path = repo_root / f"reports/CRYPTO_SEARCH_ENGINE_V1_2_{runtime_date}.md"
    errors: list[str] = []
    required = (
        "frozen_contract.json",
        "embedded_preflight.json",
        "candidate_ledger.parquet",
        "behavior_archive.parquet",
        "behavior_family_summary.json",
        "arm_checkpoint_metrics.parquet",
        "final_decision.json",
        "run_manifest.json",
    )
    for name in required:
        if not (runtime_root / name).is_file():
            errors.append(f"missing:{name}")
    if not report_path.is_file():
        errors.append("missing:report")
    if errors:
        return {"result": "FAIL", "errors": errors}
    frozen = _read_json(runtime_root / "frozen_contract.json")
    decision = _read_json(runtime_root / "final_decision.json")
    manifest = _read_json(runtime_root / "run_manifest.json")
    preflight = _read_json(runtime_root / "embedded_preflight.json")
    ledger = pd.read_parquet(runtime_root / "candidate_ledger.parquet")
    archive = pd.read_parquet(runtime_root / "behavior_archive.parquet")
    metrics = pd.read_parquet(runtime_root / "arm_checkpoint_metrics.parquet")
    family_summary = _read_json(runtime_root / "behavior_family_summary.json")
    frozen_without_hash = {
        key: value
        for key, value in frozen.items()
        if key != "frozen_contract_sha256"
    }
    if _payload_sha(frozen_without_hash) != frozen.get("frozen_contract_sha256"):
        errors.append("frozen_contract_sha256")
    if frozen.get("authorization") != (
        "ONE_FRESH_STATE_2000_SPENT_DEVELOPMENT_SEARCH_ENGINE_V1_2"
    ):
        errors.append("authorization")
    if frozen.get("surface", {}).get(
        "every_candidate_requires_aggtrades_input"
    ) is not True:
        errors.append("aggtrades_candidate_gate")
    fresh_state = frozen.get("fresh_state", {})
    if any(bool(value) for value in fresh_state.values()):
        errors.append("fresh_state_import")
    capability_delta = frozen.get("search_capability_delta", {})
    if (
        capability_delta.get("existing_lane_scheduler_balanced") is not True
        or int(capability_delta.get("balanced_micro_batch_size", -1))
        != V12_BALANCED_BATCH_SIZE
        or capability_delta.get("rotating_seed_lane_submission_order")
        is not True
        or capability_delta.get(
            "campaign_local_transition_collision_control"
        )
        is not True
        or capability_delta.get("new_scheduler_system") is not False
    ):
        errors.append("v12_capability_contract")
    boundaries = frozen.get("boundaries", {})
    if boundaries.get("sealed_reads") != 0 or any(
        bool(boundaries.get(key))
        for key in (
            "challenge",
            "recent",
            "may_stress",
            "forward",
            "promotion",
            "cross_sprint_adaptive_memory",
            "latent_priority",
            "relational_training",
        )
    ):
        errors.append("sealed_boundary")
    if preflight.get("workers_selected") not in {
        DEFAULT_WORKERS,
        FALLBACK_WORKERS,
    }:
        errors.append("worker_selection")
    if preflight.get("strict_candidates_consumed_outside_campaign") != 0:
        errors.append("preflight_external_budget")
    if len(ledger) != V12_STRICT_TARGET:
        errors.append("strict_count")
    if ledger["candidate_id"].nunique() != V12_STRICT_TARGET:
        errors.append("exact_unique")
    for column in (
        "compile_valid",
        "exact_unique",
        "matched_control_valid",
        "strict_cost_evaluated",
        "expression_hash_verified",
    ):
        if column not in ledger or not bool(ledger[column].fillna(False).all()):
            errors.append(f"ledger_gate:{column}")
    if not all(
        bool(set(json.loads(str(value))) & set(AGGTRADES_SYSTEM_CANARY_FIELDS))
        for value in ledger["raw_fields_json"]
    ):
        errors.append("candidate_without_aggtrades")
    expected_arm_counts = {
        arm: count * V12_CHECKPOINT_COUNT
        for arm, count in V12_CHECKPOINT_ALLOCATION.items()
    }
    if ledger.groupby("arm").size().to_dict() != expected_arm_counts:
        errors.append("arm_counts")
    expected_lane_count = next(
        iter(V12_CHECKPOINT_ALLOCATION.values())
    ) // len(SEEDS)
    for checkpoint_index in range(V12_CHECKPOINT_COUNT):
        local = ledger[
            ledger["checkpoint_index"].astype(int).eq(checkpoint_index)
        ]
        if local.groupby("arm").size().to_dict() != V12_CHECKPOINT_ALLOCATION:
            errors.append(f"checkpoint_arm_counts:{checkpoint_index}")
        expected_lanes = {
            (arm, seed): expected_lane_count
            for arm in V12_ARMS
            for seed in SEEDS
        }
        if local.groupby(["arm", "seed"]).size().to_dict() != expected_lanes:
            errors.append(f"checkpoint_arm_seed_counts:{checkpoint_index}")
    if any(
        column not in ledger
        for column in (
            "balanced_batch_index",
            "balanced_batch_slot",
            "balanced_batch_size",
        )
    ):
        errors.append("balanced_batch_columns")
    else:
        batches = list(ledger.groupby("balanced_batch_index", dropna=False))
        lanes_by_slot: dict[int, set[tuple[str, int]]] = defaultdict(set)
        if len(batches) != V12_STRICT_TARGET // V12_BALANCED_BATCH_SIZE:
            errors.append("balanced_batch_count")
        for batch_id, rows in batches:
            if pd.isna(batch_id):
                errors.append("balanced_batch_null")
                continue
            if (
                len(rows) != V12_BALANCED_BATCH_SIZE
                or not rows["balanced_batch_size"]
                .astype(int)
                .eq(V12_BALANCED_BATCH_SIZE)
                .all()
                or sorted(rows["balanced_batch_slot"].astype(int).tolist())
                != list(range(V12_BALANCED_BATCH_SIZE))
                or rows.groupby("arm").size().to_dict()
                != {
                    "canonical_typed_random": len(SEEDS),
                    "collision_controlled_evolution_v2_2": len(SEEDS),
                }
                or len(rows[["arm", "seed"]].drop_duplicates())
                != V12_BALANCED_BATCH_SIZE
            ):
                errors.append(f"balanced_batch:{int(batch_id)}")
            for row in rows.to_dict("records"):
                lanes_by_slot[int(row["balanced_batch_slot"])].add(
                    (str(row["arm"]), int(row["seed"]))
                )
        expected_rotating_lanes = {
            (arm, seed) for arm in V12_ARMS for seed in SEEDS
        }
        if (
            set(lanes_by_slot) != set(range(V12_BALANCED_BATCH_SIZE))
            or any(
                lanes != expected_rotating_lanes
                for lanes in lanes_by_slot.values()
            )
        ):
            errors.append("rotating_submission_order")
    broad_contracts, _, _ = _broad39_registry_contracts(repo_root)
    replay_registry = TypedExpressionRegistry(
        tuple((*broad_contracts, *_aggtrades_canary_contracts()))
    )
    replay_policy = TypedEvolutionV2(
        0,
        replay_registry,
        V22_PARAMETERS["collision_controlled_evolution_v2_2"],
    )
    candidates_by_id = {
        str(row["candidate_id"]): CandidateSpec.from_dict(
            json.loads(str(row["candidate_spec_json"]))
        )
        for row in ledger.to_dict("records")
    }
    receipt_rows = ledger[ledger["receipt_json"].notna()]
    if receipt_rows.empty or not bool(
        receipt_rows["receipt_verified"].eq(True).all()
    ):
        errors.append("receipt_verification")
    for row in receipt_rows.to_dict("records"):
        try:
            child = candidates_by_id[str(row["candidate_id"])]
            parents = tuple(
                candidates_by_id[str(parent_id)]
                for parent_id in json.loads(str(row["parent_ids_json"]))
            )
            receipt = json.loads(str(row["receipt_json"]))
            if not replay_policy.verify_receipt(parents, child, receipt):
                errors.append(f"receipt_replay:{row['candidate_id']}")
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            errors.append(f"receipt_replay:{row['candidate_id']}")
    for operation in EVOLUTION_OPERATIONS:
        if not bool(ledger["operation"].eq(operation).any()):
            errors.append(f"operation_not_executed:{operation}")
    skeleton_rows = ledger[
        ledger["operation"].eq("COMPATIBLE_SKELETON_VARIANT_MUTATION")
    ]
    if skeleton_rows.empty or not bool(
        skeleton_rows["transition_key"].notna().all()
    ):
        errors.append("transition_key")
    ledger_by_id = {
        str(row["candidate_id"]): row for row in ledger.to_dict("records")
    }
    for row in skeleton_rows.to_dict("records"):
        try:
            parent_ids = json.loads(str(row["parent_ids_json"]))
            if len(parent_ids) != 1:
                raise ValueError("skeleton mutation requires one parent")
            parent_row = ledger_by_id[str(parent_ids[0])]
            parent = candidates_by_id[str(parent_ids[0])]
            child = candidates_by_id[str(row["candidate_id"])]
            expected_transition_key = TypedEvolutionV2._skeleton_transition_key(
                parent_behavior_family_id=str(
                    parent_row["behavior_family_id"]
                ),
                source_skeleton_id=parent.skeleton_id,
                target_skeleton_id=child.skeleton_id,
                remapped_genome_sha256=_payload_sha(
                    child.generation_genes
                ),
            )
            if str(row["transition_key"]) != expected_transition_key:
                errors.append(f"transition_key_replay:{row['candidate_id']}")
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            errors.append(f"transition_key_replay:{row['candidate_id']}")
    if len(archive) != V12_STRICT_TARGET:
        errors.append("archive_row_count")
    champions = archive[archive["is_family_champion"].fillna(False)]
    if champions["behavior_family_id"].nunique() != archive[
        "behavior_family_id"
    ].nunique():
        errors.append("archive_family_champion")
    if family_summary.get("family_count") != int(
        archive["behavior_family_id"].nunique()
    ):
        errors.append("family_summary_count")
    checkpoints = sorted(
        (runtime_root / "checkpoints").glob("checkpoint_[0-9][0-9][0-9]")
    )
    if len(checkpoints) != V12_CHECKPOINT_COUNT:
        errors.append("checkpoint_count")
    for index, checkpoint in enumerate(checkpoints):
        checkpoint_manifest = _read_json(checkpoint / "manifest.json")
        if int(checkpoint_manifest.get("completed_ledger_row_count", -1)) != (
            index + 1
        ) * V12_CHECKPOINT_SIZE:
            errors.append(f"checkpoint_rows:{index}")
        if checkpoint_manifest.get("restore_verified") is not True:
            errors.append(f"checkpoint_restore:{index}")
        for record in checkpoint_manifest.get("files", []):
            path = checkpoint / str(record["name"])
            if (
                not path.is_file()
                or path.stat().st_size != int(record["bytes"])
                or sha256_file(path) != str(record["sha256"])
            ):
                errors.append(f"checkpoint_file:{index}:{record['name']}")
        try:
            _, restored_policies, _, _, _ = _load_checkpoint(
                checkpoint_path=checkpoint,
                registry=replay_registry,
                expected_source_sha=str(frozen["source_sha"]),
                expected_frozen_hash=str(
                    frozen["frozen_contract_sha256"]
                ),
                expected_identities={
                    **dict(frozen["input_identities"]),
                    "compiler_identity": dict(frozen["compiler_identity"]),
                },
            )
            evolution_policies = [
                policy
                for key, policy in restored_policies.items()
                if key.startswith("collision_controlled_evolution_v2_2|")
                and isinstance(policy, TypedEvolutionV2)
            ]
            if len(evolution_policies) != len(SEEDS) or not all(
                policy.parameters.get(
                    "campaign_local_transition_collision_control"
                )
                is True
                for policy in evolution_policies
            ):
                errors.append(f"checkpoint_transition_state:{index}")
        except (KeyError, TypeError, ValueError):
            errors.append(f"checkpoint_state_replay:{index}")
    if set(metrics["checkpoint_index"].astype(int).unique()) != set(
        range(V12_CHECKPOINT_COUNT)
    ):
        errors.append("checkpoint_metrics")
    final_evolution = metrics[
        metrics["checkpoint_index"].astype(int).eq(V12_CHECKPOINT_COUNT - 1)
        & metrics["arm"].eq("collision_controlled_evolution_v2_2")
    ]
    if (
        len(final_evolution) != 1
        or int(final_evolution.iloc[0]["operator_update_count"]) <= 0
        or json.loads(
            str(final_evolution.iloc[0]["operator_probabilities_json"])
        )
        == {}
        or json.loads(
            str(final_evolution.iloc[0]["transition_productivity_json"])
        )
        == {}
    ):
        errors.append("v12_policy_update")
    if int(
        decision.get("generation_attempts", V12_RAW_ATTEMPT_LIMIT + 1)
    ) > V12_RAW_ATTEMPT_LIMIT:
        errors.append("raw_attempt_budget")
    if float(
        decision.get(
            "active_wall_seconds", V12_WALL_TIME_LIMIT_SECONDS + 1
        )
    ) > V12_WALL_TIME_LIMIT_SECONDS:
        errors.append("wall_time_budget")
    if decision.get("status") != "PASS_SEARCH_ENGINE_V1_2_COMPLETED":
        errors.append("final_decision")
    if decision.get("balanced_batch_integrity") is not True:
        errors.append("final_balanced_batch_integrity")
    if decision.get("rotating_submission_integrity") is not True:
        errors.append("final_rotating_submission_integrity")
    if decision.get("research_decision") != (
        "HOLD_RESEARCH_SPENT_FIXED_RETROSPECTIVE_COHORT"
    ):
        errors.append("research_boundary")
    if decision.get("future_new_data_arena_qualified_arms") != []:
        errors.append("future_arm_qualification")
    if decision.get("sealed_reads") != 0:
        errors.append("sealed_reads")
    if manifest.get("strict_evaluated_count") != V12_STRICT_TARGET:
        errors.append("manifest_strict_count")
    if manifest.get("frozen_contract_sha256") != frozen.get(
        "frozen_contract_sha256"
    ):
        errors.append("manifest_contract")
    if _payload_sha(manifest.get("artifacts", [])) != manifest.get(
        "artifact_bundle_sha256"
    ):
        errors.append("manifest_bundle")
    for record in manifest.get("artifacts", []):
        path = repo_root / str(record["path"])
        if (
            not path.is_file()
            or path.stat().st_size != int(record["bytes"])
            or sha256_file(path) != str(record["sha256"])
        ):
            errors.append(f"manifest_artifact:{record['path']}")
    try:
        subprocess.check_call(
            [
                "git",
                "cat-file",
                "-e",
                f"{manifest['producer_source_sha']}^{{commit}}",
            ],
            cwd=repo_root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        errors.append("producer_source_commit")
    result = "PASS" if not errors else "FAIL"
    return {
        "result": result,
        "errors": errors,
        "engineering_integrity": result,
        "research_decision": decision.get("research_decision"),
        "producer_source_sha": manifest.get("producer_source_sha"),
        "strict_evaluated_count": len(ledger),
        "generation_attempts": decision.get("generation_attempts"),
        "checkpoint_count": len(checkpoints),
        "balanced_batch_count": decision.get("balanced_batch_count"),
        "behavior_family_count": int(archive["behavior_family_id"].nunique()),
        "artifact_bundle_sha256": manifest.get("artifact_bundle_sha256"),
        "search_iteration_decision": decision.get(
            "search_iteration_decision", {}
        ),
        "future_new_data_arena_qualified_arms": [],
        "sealed_reads": decision.get("sealed_reads"),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        choices=(
            "run",
            "check",
            "build-canary-cache",
            "run-canary",
            "check-canary",
            "run-v11",
            "check-v11",
            "run-v12",
            "check-v12",
            "run-carrier-gate",
        ),
    )
    parser.add_argument("--runtime-date")
    parser.add_argument("--source-sha")
    parser.add_argument("--carrier-id", choices=CARRIER_GATE_IDS)
    args = parser.parse_args(argv)
    repo_root = Path(__file__).resolve().parents[2]
    if args.command == "run":
        result = run_engine(
            repo_root,
            runtime_date=str(args.runtime_date or DEFAULT_RUNTIME_DATE),
            source_sha=args.source_sha,
        )
    elif args.command == "check":
        result = check_engine(
            repo_root,
            runtime_date=str(args.runtime_date or DEFAULT_RUNTIME_DATE),
        )
    elif args.command == "run-carrier-gate":
        result = run_engine(
            repo_root,
            runtime_date=str(
                args.runtime_date or CARRIER_GATE_DEFAULT_RUNTIME_DATE
            ),
            source_sha=args.source_sha,
            campaign="carrier_gate_v1",
            carrier_id=args.carrier_id,
        )
    elif args.command == "build-canary-cache":
        source_sha = str(args.source_sha or _git_sha(repo_root)).lower()
        metadata = build_aggtrades_canary_cache_from_config(
            repo_root, source_sha=source_sha
        )
        result = {
            "result": "PASS",
            "cache_identity_sha256": metadata["identity_sha256"],
            "assets": metadata["assets"],
            "timestamps": metadata["timestamps"],
            "observed_coordinates": metadata["observed_coordinates"],
        }
    elif args.command == "run-canary":
        result = run_engine(
            repo_root,
            runtime_date=str(
                args.runtime_date or AGGTRADES_CANARY_DEFAULT_RUNTIME_DATE
            ),
            source_sha=args.source_sha,
            campaign="aggtrades_system_canary",
        )
    elif args.command == "check-canary":
        result = check_aggtrades_canary(
            repo_root,
            runtime_date=str(
                args.runtime_date or AGGTRADES_CANARY_DEFAULT_RUNTIME_DATE
            ),
        )
    elif args.command == "run-v11":
        result = run_engine(
            repo_root,
            runtime_date=str(args.runtime_date or V11_DEFAULT_RUNTIME_DATE),
            source_sha=args.source_sha,
            campaign="search_engine_v1_1",
        )
    elif args.command == "check-v11":
        result = check_v11(
            repo_root,
            runtime_date=str(args.runtime_date or V11_DEFAULT_RUNTIME_DATE),
        )
    elif args.command == "run-v12":
        result = run_engine(
            repo_root,
            runtime_date=str(args.runtime_date or V12_DEFAULT_RUNTIME_DATE),
            source_sha=args.source_sha,
            campaign="search_engine_v1_2",
        )
    else:
        result = check_v12(
            repo_root,
            runtime_date=str(args.runtime_date or V12_DEFAULT_RUNTIME_DATE),
        )
    print(json.dumps(result, indent=2, sort_keys=True), flush=True)
    return 0 if result.get("result") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "BehaviorArchive",
    "HierarchicalTypedCEMV2",
    "TypedEvolutionV2",
    "V11_ARMS",
    "V21_PARAMETERS",
    "V12_ARMS",
    "V22_PARAMETERS",
    "build_aggtrades_canary_cache_from_config",
    "check_aggtrades_canary",
    "check_v11",
    "check_v12",
    "check_engine",
    "run_engine",
]
