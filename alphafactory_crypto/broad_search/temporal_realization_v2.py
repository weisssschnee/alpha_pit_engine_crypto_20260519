"""Train-only realization search helpers for targeted Temporal programs.

The module changes proposal construction and campaign-local parent selection only.
It reuses the frozen Temporal grammar, compiler, mapping, cost, reward, and evaluator.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from . import search_engine_v1 as engine
from .temporal_targeted_deepening_v1 import (
    ACTIVE_PROGRAM_FAMILIES,
    BASELINE_ROW_FIELDS,
    CANONICAL_SIMILARITY_THRESHOLD,
    ECONOMIC_FINGERPRINT_FIELDS,
    build_frozen_target_parent_pool,
    load_diagnostic_baseline,
)
from .temporal_development_expansion_v1 import (
    ExpansionPreflightError,
    authorization_content_sha,
    executor_workspace_identity,
    file_sha256,
)
from .temporal_successor_v1 import verify_successor_market_inputs


EXECUTION_MODE = "TEMPORAL_SEARCH_CORE_REALIZATION_V2"
CAMPAIGN = "crypto_temporal_search_core_realization_v2"
SEED_CAMPAIGN = "CRYPTO_TEMPORAL_SEARCH_CORE_REALIZATION_V2"
SEED_DERIVATION = "FIRST_UINT32_SHA256_CRYPTO_TEMPORAL_SEARCH_CORE_REALIZATION_V2_PIPE_LANE_INDEX"
AUTHORIZATION_PATH = "config/crypto_temporal_search_core_realization_v2_authorization.json"
AUDIT_PATH = "config/crypto_temporal_search_core_realization_v2_audit.json"
AUTHORIZED_STATUS = "RUN_AUTHORIZED_ONE_TIME_REALIZATION_V2_CANARY"
CONSUMED_STATUS = "RUN_AUTHORIZATION_CONSUMED_REALIZATION_V2_CANARY"
AUTHORIZATION_SCOPE = (
    "ONE_20000_STRICT_TRAIN_ONLY_TEMPORAL_SEARCH_CORE_REALIZATION_V2_CANARY"
)
STRICT_CAP = 20_000
CHECKPOINT_SIZE = 2_000
DECISION_BOUNDARY = 10_000
FIXED_ALLOCATION_PER_10000 = {
    "temporal_program_random": 2_000,
    "temporal_program_cem": 2_000,
    "temporal_program_evolution": 6_000,
}
EVOLUTION_OPERATION_PROBABILITIES = {
    "parameter_mutation_probability": 0.62,
    "mechanism_mutation_probability": 0.03,
    "crossover_probability": 0.35,
}
TURNOVER_REACHABILITY = "TURNOVER_OPERATOR_REACHABLE"
R3_FIRST_10000_CROSSOVER_REQUESTED = 1_260
R3_FIRST_10000_CROSSOVER_REALIZED = 572
R3_FIRST_10000_EVOLUTION_STRICT = 6_000
R3_FIRST_10000_EVOLUTION_MATCHED_POSITIVE = 1_220
ARCHIVE_ID = "BASIN_LOCAL_REALIZATION_ARCHIVE_V1"
ARCHIVE_TOP_K = 2
P1_BASIN_SELECTION_WEIGHT = 3
GENERIC_PARAMETER_MUTATION_PROBABILITY = 0.20
COMPONENT_PATHS = (
    "alphafactory_crypto/broad_search/expression.py",
    "alphafactory_crypto/broad_search/compositional18m.py",
    "alphafactory_crypto/broad_search/pair18m.py",
    "alphafactory_crypto/broad_search/search_engine_v1.py",
    "alphafactory_crypto/broad_search/experiment_authority.py",
    "alphafactory_crypto/broad_search/temporal_activation_v1.py",
    "alphafactory_crypto/broad_search/temporal_program_v1.py",
    "alphafactory_crypto/broad_search/temporal_development_expansion_v1.py",
    "alphafactory_crypto/broad_search/temporal_successor_v1.py",
    "alphafactory_crypto/broad_search/temporal_targeted_deepening_v1.py",
    "alphafactory_crypto/broad_search/temporal_realization_v2.py",
    "alphafactory_crypto/broad_search/temporal_program_search_v1.py",
    "scripts/run_crypto_temporal_mechanism_program_v1_pc2.ps1",
    "config/crypto_temporal_mechanism_program_v1.json",
)

DIMENSION_FIELDS = {
    "mapped_weight": "mapped_weight_descriptor_id",
    "turnover": "turnover_path_descriptor_id",
    "raw_field": "raw_fields_json",
    "asset_selection": "selected_asset_overlap_id",
}
MUTATION_GROUP_WEIGHTS = {
    "mapped_weight": {
        "left_field+left_auxiliary_field": 1.0,
        "right_field+right_auxiliary_field": 1.0,
        "left_normalizer+left_normalizer_window": 0.9,
        "left_window+left_long_window+left_threshold": 0.9,
    },
    "turnover": {
        "right_field+right_auxiliary_field": 8.0,
        "right_window+right_long_window+right_threshold": 1.5,
        "right_normalizer+right_normalizer_window": 1.5,
    },
    "raw_field": {
        "left_field+left_auxiliary_field": 4.0,
        "right_field+right_auxiliary_field": 4.0,
    },
    "asset_selection": {
        "left_field+left_auxiliary_field": 1.5,
        "right_field+right_auxiliary_field": 1.5,
        "left_window+left_long_window+left_threshold": 1.0,
    },
    "generic": {},
}


def derive_lane_seeds(lane_count: int = 4) -> tuple[int, ...]:
    seeds = tuple(
        int.from_bytes(
            hashlib.sha256(f"{SEED_CAMPAIGN}|{index}".encode("ascii")).digest()[:4],
            byteorder="big",
            signed=False,
        )
        for index in range(int(lane_count))
    )
    if len(seeds) != int(lane_count) or len(set(seeds)) != len(seeds):
        raise RuntimeError("realization V2 lane seed identity changed")
    return seeds


LANE_SEEDS = derive_lane_seeds()


def _sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("utf-8")
    ).hexdigest().upper()


def committed_blob_oid(repo_root: Path, source_sha: str, relative_path: str) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", f"{source_sha}:{relative_path}"],
        cwd=repo_root,
        text=True,
    ).strip().lower()


def normalized_worktree_blob_oid(repo_root: Path, relative_path: str) -> str:
    return subprocess.check_output(
        ["git", "hash-object", f"--path={relative_path}", relative_path],
        cwd=repo_root,
        text=True,
    ).strip().lower()


def validate_authorization(
    repo_root: Path, *, expected_source_sha: str | None = None
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    path = repo_root / AUTHORIZATION_PATH
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as failure:
        raise ExpansionPreflightError(
            "FAIL_CLOSED_BEFORE_MARKET_READ:realization_v2_authorization_unreadable"
        ) from failure
    errors: list[str] = []
    if (
        payload.get("schema_version") != 1
        or payload.get("execution_mode") != EXECUTION_MODE
        or payload.get("status") != AUTHORIZED_STATUS
        or payload.get("run_authorized") is not True
        or payload.get("consumed") is not False
        or payload.get("authorization_sha256") != authorization_content_sha(payload)
    ):
        errors.append("authorization_hash_or_status")
    if dict(payload.get("budget") or {}) != {
        "strict_evaluated_maximum": STRICT_CAP,
        "raw_generation_attempts_maximum": 100_000,
        "wall_time_seconds_maximum": 36_000,
        "checkpoint_size": CHECKPOINT_SIZE,
        "checkpoint_boundary": DECISION_BOUNDARY,
        "workers_default": 10,
        "workers_memory_fallback": 8,
    }:
        errors.append("budget")
    if dict(payload.get("allocation_per_10000") or {}) != FIXED_ALLOCATION_PER_10000:
        errors.append("allocation")
    if dict(payload.get("evolution_operation_probabilities") or {}) != EVOLUTION_OPERATION_PROBABILITIES:
        errors.append("operation_probabilities")
    if tuple(payload.get("lane_seeds") or ()) != LANE_SEEDS:
        errors.append("lane_seeds")
    if tuple(payload.get("active_program_families") or ()) != ACTIVE_PROGRAM_FAMILIES:
        errors.append("program_families")
    boundaries = dict(payload.get("boundaries") or {})
    if (
        boundaries.get("train_only") is not True
        or any(
            bool(boundaries.get(key))
            for key in (
                "validation",
                "oos",
                "holdout",
                "forward",
                "promotion",
                "automatic_expansion",
                "mapping_change",
                "cost_change",
                "evaluator_change",
                "reward_change",
                "target_change",
                "grammar_change",
            )
        )
        or int(boundaries.get("sealed_reads", -1)) != 0
    ):
        errors.append("boundaries")
    source_sha = str(expected_source_sha or "").lower()
    implementation_sha = str(payload.get("authorized_implementation_sha") or "").lower()
    if source_sha and (
        not implementation_sha
        or subprocess.run(
            ["git", "merge-base", "--is-ancestor", implementation_sha, source_sha],
            cwd=repo_root,
            check=False,
            capture_output=True,
        ).returncode
        != 0
    ):
        errors.append("implementation_ancestry")
    identities = dict(payload.get("execution_component_git_identities") or {})
    if set(identities) != set(COMPONENT_PATHS):
        errors.append("component_paths")
    elif implementation_sha:
        for component, expected in identities.items():
            try:
                observed = committed_blob_oid(
                    repo_root, implementation_sha, component
                )
            except (OSError, RuntimeError, subprocess.CalledProcessError):
                errors.append("component_identity:" + component)
                continue
            if observed != str(expected):
                errors.append("component_identity:" + component)
                continue
            if normalized_worktree_blob_oid(repo_root, component) != str(expected):
                errors.append("component_worktree_identity:" + component)
    audit_path = Path(str(payload.get("operator_audit_path") or ""))
    if not audit_path.is_absolute():
        audit_path = repo_root / audit_path
    try:
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        errors.append("operator_audit")
    else:
        if (
            file_sha256(audit_path) != str(payload.get("operator_audit_sha256") or "")
            or audit.get("status") != "PASS"
            or audit.get("turnover_reachability") != TURNOVER_REACHABILITY
            or any(int(audit.get(key, -1)) != 0 for key in ("validation_reads", "oos_reads", "sealed_reads"))
        ):
            errors.append("operator_audit")
    offline_path = Path(str(payload.get("offline_verification_path") or ""))
    if not offline_path.is_absolute():
        offline_path = repo_root / offline_path
    try:
        offline = json.loads(offline_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        errors.append("offline_verification")
    else:
        if (
            file_sha256(offline_path)
            != str(payload.get("offline_verification_sha256") or "")
            or offline.get("status") != "PASS"
            or offline.get("checkpoint_exact_replay") is not True
            or offline.get("receipt_replay") is not True
            or offline.get("archive_state_hash_replay") is not True
            or int(offline.get("cross_basin_parent_contamination", -1)) != 0
            or any(
                int(offline.get(key, -1)) != 0
                for key in (
                    "market_arrays_read",
                    "candidate_evaluations",
                    "validation_reads",
                    "oos_reads",
                    "sealed_reads",
                )
            )
        ):
            errors.append("offline_verification")
    baseline_path = Path(str(payload.get("diagnostic_baseline_path") or ""))
    if not baseline_path.is_absolute():
        baseline_path = repo_root / baseline_path
    if (
        not baseline_path.is_file()
        or file_sha256(baseline_path)
        != str(payload.get("diagnostic_baseline_sha256") or "")
    ):
        errors.append("diagnostic_baseline")
    else:
        try:
            baseline = load_diagnostic_baseline(repo_root, payload)
            pool = build_frozen_target_parent_pool(repo_root, baseline)
        except (OSError, RuntimeError, ValueError) as failure:
            errors.append("frozen_pool:" + type(failure).__name__)
        else:
            identity = dict(payload.get("frozen_parent_pool_identity") or {})
            if (
                int(pool.get("target_basin_count", -1)) != 23
                or int(pool.get("frozen_parent_candidate_count", -1)) != 228
                or str(pool.get("target_parent_pool_sha256") or "")
                != "A08112ED1765A432D15D259A70F308C2DE5BA7B617D294BFB8349020EC61AA49"
                or identity.get("target_parent_pool_sha256")
                != pool.get("target_parent_pool_sha256")
            ):
                errors.append("frozen_pool_identity")
    try:
        market = verify_successor_market_inputs(repo_root)
    except Exception as failure:
        errors.append("market_input_preflight:" + type(failure).__name__)
    else:
        if market != dict(payload.get("market_input_preflight") or {}):
            errors.append("market_input_preflight")
    executor = dict(payload.get("executor_identity") or {})
    if executor != executor_workspace_identity(repo_root):
        errors.append("executor_identity")
    if errors:
        raise ExpansionPreflightError(
            "FAIL_CLOSED_BEFORE_MARKET_READ:" + ",".join(sorted(set(errors)))
        )
    return payload


def load_authorized_inputs(
    repo_root: Path, authorization: Mapping[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    baseline = load_diagnostic_baseline(repo_root, authorization)
    return baseline, build_frozen_target_parent_pool(repo_root, baseline)


def _as_float(value: Any) -> float:
    result = float(value or 0.0)
    return result if np.isfinite(result) else 0.0


def _realization_id(row: Mapping[str, Any]) -> str:
    return _sha(
        [
            str(row.get(key) or "NOT_AVAILABLE")
            for key in (
                "mapped_weight_descriptor_id",
                "selected_asset_overlap_id",
                "turnover_path_descriptor_id",
                "raw_fields_json",
                "operator_path",
                "program_id",
            )
        ]
    )


def _cell_id(row: Mapping[str, Any]) -> str:
    return _sha(
        {
            "mapped_weight_descriptor_id": row.get("mapped_weight_descriptor_id"),
            "turnover_path_descriptor_id": row.get("turnover_path_descriptor_id"),
            "raw_fields_json": row.get("raw_fields_json"),
            "selected_asset_overlap_id": row.get("selected_asset_overlap_id"),
            "operator_path": row.get("operator_path"),
            "program_id": row.get("program_id"),
        }
    )


def economic_fingerprint_from_evaluation(evaluation: Mapping[str, Any]) -> dict[str, float]:
    row = dict(engine._evaluation_audit_fields(evaluation))
    feedback = dict(evaluation.get("search_reward_feedback") or {})
    ordering = dict(evaluation.get("block_robust_ordering") or {})
    row.update(
        {
            "search_reward": engine._search_ordering_reward(evaluation),
            "primary_search_reward": feedback.get("primary_search_reward"),
            "matched_min_search_reward": feedback.get("matched_min_search_reward"),
            "worst_block_min_matched_net_mean": ordering.get(
                "worst_block_min_matched_net_mean"
            ),
            "median_block_joint_search_reward": ordering.get(
                "median_block_joint_search_reward"
            ),
            "train_day_sortino": feedback.get("train_day_sortino"),
            "train_day_bootstrap_sortino_p25": feedback.get(
                "train_day_bootstrap_sortino_p25"
            ),
            "train_day_bootstrap_probability_gt_zero": feedback.get(
                "train_day_bootstrap_probability_gt_zero"
            ),
            "train_mean_one_way_turnover": feedback.get("mean_one_way_turnover"),
            "pair_reward": evaluation.get("pair_reward"),
            "scalar_net_delta_diagnostic": evaluation.get(
                "scalar_net_delta_diagnostic",
                row.get("scalar_net_delta_diagnostic"),
            ),
        }
    )
    return {field: _as_float(row.get(field)) for field in ECONOMIC_FINGERPRINT_FIELDS}


def _standardized_anchor_model(
    baseline_rows: Sequence[Mapping[str, Any]], pool: Mapping[str, Any]
) -> dict[str, Any]:
    rows = [dict(row) for row in baseline_rows]
    matrix = np.asarray(
        [[_as_float(row.get(field)) for field in ECONOMIC_FINGERPRINT_FIELDS] for row in rows],
        dtype=np.float64,
    )
    for index in range(matrix.shape[1]):
        column = matrix[:, index]
        finite = np.isfinite(column)
        column[~finite] = float(np.median(column[finite])) if finite.any() else 0.0
    mean = matrix.mean(axis=0)
    std = matrix.std(axis=0)
    std[std <= 1.0e-12] = 1.0
    standardized = (matrix - mean) / std
    standardized -= standardized.mean(axis=1, keepdims=True)
    standardized /= np.maximum(
        np.linalg.norm(standardized, axis=1, keepdims=True), 1.0e-12
    )
    row_index = {str(row["candidate_id"]): index for index, row in enumerate(rows)}
    anchors = {
        str(basin["economic_similarity_cluster_id"]): [
            standardized[row_index[str(candidate_id)]].tolist()
            for candidate_id in basin["member_candidate_ids"]
        ]
        for basin in pool["target_basins"]
    }
    return {
        "fields": list(ECONOMIC_FINGERPRINT_FIELDS),
        "mean": mean.tolist(),
        "std": std.tolist(),
        "anchors": anchors,
    }


def configure_policy_realization_v2(
    policy: engine.MechanismEvolutionV2,
    *,
    pool: Mapping[str, Any],
    baseline: Mapping[str, Any],
) -> None:
    if policy.targeted_parent_pool_payload is None:
        policy.configure_targeted_parent_pool(pool)
    if (
        str(pool.get("target_parent_pool_sha256") or "")
        != "A08112ED1765A432D15D259A70F308C2DE5BA7B617D294BFB8349020EC61AA49"
        or int(pool.get("target_basin_count", -1)) != 23
        or int(pool.get("frozen_parent_candidate_count", -1)) != 228
        or int(baseline.get("source_strict_count", -1)) != 50_000
        or int(baseline.get("matched_positive_count", -1)) != 302
        or str(baseline.get("source_ledger_sha256") or "")
        != "5171CD9655944CCED18D35CCB413C725E9542889260A135E8F95F4BE7B401B46"
    ):
        raise ValueError("realization V2 frozen source identity changed")
    baseline_by_id = {
        str(row["candidate_id"]): {
            key: row.get(key)
            for key in BASELINE_ROW_FIELDS
            if key in row
        }
        for row in baseline["matched_positive_rows"]
    }
    frozen_ids = set(pool["parent_records"])
    if not frozen_ids.issubset(baseline_by_id):
        raise ValueError("realization V2 baseline parent recovery changed")
    state = {
        "schema_version": 1,
        "archive_id": ARCHIVE_ID,
        "target_parent_pool_sha256": pool["target_parent_pool_sha256"],
        "source_ledger_sha256": baseline["source_ledger_sha256"],
        "similarity_threshold": CANONICAL_SIMILARITY_THRESHOLD,
        "turnover_reachability": TURNOVER_REACHABILITY,
        "top_k_per_adaptive_cell": ARCHIVE_TOP_K,
        "generic_parameter_mutation_probability": GENERIC_PARAMETER_MUTATION_PROBABILITY,
        "p1_basin_selection_weight": P1_BASIN_SELECTION_WEIGHT,
        "baseline_rows": {candidate_id: baseline_by_id[candidate_id] for candidate_id in sorted(frozen_ids)},
        "anchor_model": _standardized_anchor_model(
            baseline["matched_positive_rows"], pool
        ),
        "descendants": {},
        "admission_counts": {
            "admitted": 0,
            "cross_basin_rejected": 0,
            "new_basin_diagnostic": 0,
            "cell_capacity_rejected": 0,
        },
        "mutation_target_counts": {},
    }
    state["configuration_sha256"] = _sha(
        {key: value for key, value in state.items() if key != "configuration_sha256"}
    )
    policy.realization_v2_state = state


def restore_policy_realization_v2(
    policy: engine.MechanismEvolutionV2, state: Mapping[str, Any]
) -> None:
    value = json.loads(json.dumps(dict(state)))
    if (
        value.get("schema_version") != 1
        or value.get("archive_id") != ARCHIVE_ID
        or str(value.get("target_parent_pool_sha256") or "")
        != str(policy.targeted_parent_pool_payload["target_parent_pool_sha256"])
    ):
        raise ValueError("realization V2 checkpoint identity changed")
    policy.realization_v2_state = value


def _dynamic_record(
    policy: engine.MechanismEvolutionV2, candidate_id: str
) -> dict[str, Any] | None:
    state = policy.realization_v2_state
    if not state:
        return None
    descendant = dict(state["descendants"].get(candidate_id) or {})
    if descendant:
        return descendant
    baseline = dict(state["baseline_rows"].get(candidate_id) or {})
    if not baseline:
        return None
    return {
        **dict(policy.targeted_parent_pool_payload["parent_records"][candidate_id]),
        **baseline,
        "realization_cell_id": _cell_id(baseline),
        "parent_source": "FROZEN_TRAIN_ONLY_BASELINE",
    }


def targeted_parent_record(
    policy: engine.MechanismEvolutionV2, candidate_id: str
) -> dict[str, Any] | None:
    return _dynamic_record(policy, candidate_id)


def targeted_members(policy: engine.MechanismEvolutionV2, basin_id: str) -> tuple[str, ...]:
    if not policy.realization_v2_state:
        return tuple(policy.targeted_member_order[basin_id])
    frozen = list(policy.targeted_member_order[basin_id])
    descendants = [
        candidate_id
        for candidate_id, record in policy.realization_v2_state["descendants"].items()
        if str(record["economic_similarity_cluster_id"]) == basin_id
    ]
    return tuple(frozen + sorted(descendants))


def _quality_key(policy: engine.MechanismEvolutionV2, candidate_id: str) -> tuple[Any, ...]:
    record = _dynamic_record(policy, candidate_id)
    if record is None:
        raise KeyError(candidate_id)
    return policy._selection_key(candidate_id, record, include_family_count=False)


def next_targeted_basin(policy: engine.MechanismEvolutionV2) -> str:
    state = policy.realization_v2_state
    if not state:
        return policy.targeted_basin_order[
            policy.targeted_basin_cursor % len(policy.targeted_basin_order)
        ]
    p1 = {
        str(row["economic_similarity_cluster_id"])
        for row in policy.targeted_parent_pool_payload["target_basins"]
        if str(row["program_family_id"]) == ACTIVE_PROGRAM_FAMILIES[0]
    }
    schedule = list(policy.targeted_basin_order)
    for basin_id in sorted(p1):
        schedule.extend([basin_id] * (int(state["p1_basin_selection_weight"]) - 1))
    basin_id = schedule[policy.targeted_basin_cursor % len(schedule)]
    policy.targeted_basin_cursor += 1
    return basin_id


def next_targeted_parent(
    policy: engine.MechanismEvolutionV2, basin_id: str
) -> engine.CandidateSpec:
    members = list(targeted_members(policy, basin_id))
    cells = Counter(
        str(_dynamic_record(policy, candidate_id)["realization_cell_id"])
        for candidate_id in members
    )
    ordered = sorted(
        members,
        key=lambda candidate_id: (
            cells[str(_dynamic_record(policy, candidate_id)["realization_cell_id"])],
            _quality_key(policy, candidate_id),
        ),
    )
    cursor = int(policy.targeted_parent_cursors.get(basin_id, 0))
    candidate_id = ordered[cursor % len(ordered)]
    policy.targeted_parent_cursors[basin_id] = cursor + 1
    return policy._candidate(_dynamic_record(policy, candidate_id))


def mutation_target(policy: engine.MechanismEvolutionV2, basin_id: str) -> str:
    state = policy.realization_v2_state
    if not state or policy.rng.random() < float(
        state["generic_parameter_mutation_probability"]
    ):
        target = "generic"
    else:
        records = [
            _dynamic_record(policy, candidate_id)
            for candidate_id in targeted_members(policy, basin_id)
        ]
        counts = {
            dimension: len(
                {str(record.get(field) or "NOT_AVAILABLE") for record in records}
            )
            for dimension, field in DIMENSION_FIELDS.items()
        }
        targets = []
        if counts["mapped_weight"] < 3:
            targets.append("mapped_weight")
        if counts["raw_field"] < 2:
            targets.append("raw_field")
        if counts["asset_selection"] < 2:
            targets.append("asset_selection")
        if TURNOVER_REACHABILITY == "TURNOVER_OPERATOR_REACHABLE" and counts["turnover"] < 2:
            targets.append("turnover")
        target = policy.rng.choice(targets) if targets else "generic"
    counts = Counter(state.get("mutation_target_counts") or {}) if state else Counter()
    counts[target] += 1
    if state is not None:
        state["mutation_target_counts"] = dict(sorted(counts.items()))
    return target


def select_mutation_groups(
    policy: engine.MechanismEvolutionV2,
    groups: Sequence[tuple[str, ...]],
    count: int,
    target: str | None,
) -> list[tuple[str, ...]]:
    if not policy.realization_v2_state or not target or target == "generic":
        return policy.rng.sample(list(groups), count)
    weights = MUTATION_GROUP_WEIGHTS.get(target, {})
    available = list(groups)
    selected: list[tuple[str, ...]] = []
    for _ in range(count):
        values = [float(weights.get("+".join(group), 0.25)) for group in available]
        draw = policy.rng.random() * sum(values)
        cumulative = 0.0
        chosen = available[-1]
        for group, weight in zip(available, values, strict=True):
            cumulative += weight
            if draw <= cumulative:
                chosen = group
                break
        selected.append(chosen)
        available.remove(chosen)
    return selected


def constructive_crossover(
    policy: engine.MechanismEvolutionV2,
    first: engine.CandidateSpec,
    second: engine.CandidateSpec,
) -> tuple[engine.CandidateSpec | None, dict[str, Any]]:
    if not policy._compatible(policy._spec(first), policy._spec(second)):
        return None, {
            "enumerated_splice_count": 0,
            "legal_splice_count": 0,
            "duplicate_splice_count": 0,
            "parent_identical_count": 0,
            "build_invalid_count": 0,
            "selected_splice": None,
        }
    groups = list(policy._gene_groups(first))
    legal: dict[str, tuple[list[int], engine.CandidateSpec]] = {}
    duplicate = parent_identical = build_invalid = 0
    for mask in range(1, (1 << len(groups)) - 1):
        selected = [index for index in range(len(groups)) if mask & (1 << index)]
        genome = dict(first.generation_genes)
        for index in selected:
            for name in groups[index]:
                genome[name] = second.generation_genes[name]
        try:
            child = policy._build_candidate(genome)
        except ValueError:
            build_invalid += 1
            continue
        if child.candidate_id in {first.candidate_id, second.candidate_id}:
            parent_identical += 1
            continue
        if child.candidate_id in policy.seen or child.candidate_id in legal:
            duplicate += 1
            continue
        legal[child.candidate_id] = (selected, child)
    ordered = sorted(legal)
    details = {
        "constructive_crossover": True,
        "gene_groups": [list(group) for group in groups],
        "enumerated_splice_count": (1 << len(groups)) - 2,
        "legal_splice_count": len(ordered),
        "duplicate_splice_count": duplicate,
        "parent_identical_count": parent_identical,
        "build_invalid_count": build_invalid,
        "selected_splice": None,
        "output_type": "NUMERIC_ASSET_TIME",
        "internal_generation_attempts": 1,
        "compile_valid_attempts": len(ordered),
    }
    if not ordered:
        return None, details
    candidate_id = ordered[policy.rng.randrange(len(ordered))]
    selected, child = legal[candidate_id]
    details["selected_splice"] = selected
    return child, details


def _rehash_receipt(receipt: Mapping[str, Any], **updates: Any) -> dict[str, Any]:
    core = {key: value for key, value in receipt.items() if key != "receipt_sha256"}
    core.update(updates)
    return {**core, "receipt_sha256": engine._payload_sha(core)}


def propose_targeted_realization_v2(
    policy: engine.MechanismEvolutionV2,
) -> tuple[engine.CandidateSpec, dict[str, Any]]:
    before = policy.state_hash()
    limit = int(policy.parameters.get("duplicate_resample_limit", 64))
    for duplicate_attempt in range(1, limit + 2):
        basin_id = next_targeted_basin(policy)
        first = next_targeted_parent(policy, basin_id)
        draw = policy.rng.random()
        parameter_probability = float(policy.parameters["parameter_mutation_probability"])
        mechanism_probability = float(policy.parameters["mechanism_mutation_probability"])
        fallback_reason = None
        crossover_details: dict[str, Any] = {}
        if draw < parameter_probability:
            requested = "parameter_mutation"
            target = mutation_target(policy, basin_id)
            child, receipt = policy._mutate_parameters(first, target_dimension=target)
            parents = (first,)
        elif draw < parameter_probability + mechanism_probability:
            requested = "mechanism_mutation"
            child, receipt = policy._mutate_mechanism(first)
            parents = (first,)
        else:
            requested = "crossover"
            second = policy._targeted_crossover_parent(basin_id, first)
            if second is None:
                crossover_details = {
                    "enumerated_splice_count": 0,
                    "legal_splice_count": 0,
                    "duplicate_splice_count": 0,
                    "parent_identical_count": 0,
                    "build_invalid_count": 0,
                    "selected_splice": None,
                }
                fallback_reason = "NO_COMPATIBLE_SAME_BASIN_PARENT"
                target = mutation_target(policy, basin_id)
                child, receipt = policy._mutate_parameters(first, target_dimension=target)
                parents = (first,)
            else:
                child, crossover_details = constructive_crossover(policy, first, second)
                if child is None:
                    fallback_reason = "LEGAL_CHILD_SET_EMPTY"
                    target = mutation_target(policy, basin_id)
                    child, receipt = policy._mutate_parameters(first, target_dimension=target)
                    parents = (first,)
                else:
                    parents = (first, second)
                    receipt = policy._receipt(
                        operation=engine.MECHANISM_EVOLUTION_OPERATIONS[2],
                        parents=parents,
                        child=child,
                        details=crossover_details,
                    )
        realized = {
            engine.MECHANISM_EVOLUTION_OPERATIONS[0]: "parameter_mutation",
            engine.MECHANISM_EVOLUTION_OPERATIONS[1]: "mechanism_mutation",
            engine.MECHANISM_EVOLUTION_OPERATIONS[2]: "crossover",
        }[str(receipt["operation"])]
        receipt = _rehash_receipt(
            receipt,
            requested_operation=requested,
            realized_operation=realized,
            crossover_fallback=bool(fallback_reason),
            fallback_reason=fallback_reason,
            **crossover_details,
        )
        receipt = policy._bind_targeted_receipt(
            receipt, basin_id=basin_id, parents=parents
        )
        if child.candidate_id in policy.seen:
            continue
        if not policy.verify_receipt(parents, child, receipt):
            raise RuntimeError("realization V2 receipt verification failed")
        policy.seen.add(child.candidate_id)
        policy.step += 1
        return child, {
            "policy_state_hash_before": before,
            "operation": str(receipt["operation"]),
            "parent_ids": [parent.candidate_id for parent in parents],
            "receipt": receipt,
            "receipt_verified": True,
            "raw_attempts": duplicate_attempt
            + int(receipt.get("internal_generation_attempts", 1))
            - 1,
            "compile_valid_attempts": int(receipt.get("compile_valid_attempts", 1)),
            "targeted_economic_basin_id": basin_id,
            "targeted_parent_pool_sha256": str(
                policy.targeted_parent_pool_payload["target_parent_pool_sha256"]
            ),
        }
    raise engine._ProposalGenerationFailure(
        "realization V2 duplicate resample limit exhausted", raw_attempts=limit + 1
    )


def _assign_anchor(state: Mapping[str, Any], fingerprint: Mapping[str, Any]) -> tuple[str, float]:
    model = state["anchor_model"]
    vector = np.asarray([_as_float(fingerprint.get(field)) for field in model["fields"]])
    vector = (vector - np.asarray(model["mean"])) / np.asarray(model["std"])
    vector -= vector.mean()
    vector /= max(float(np.linalg.norm(vector)), 1.0e-12)
    scores = {
        basin_id: float(
            np.mean(np.asarray(member_vectors, dtype=np.float64) @ vector)
        )
        for basin_id, member_vectors in model["anchors"].items()
    }
    basin_id = max(scores, key=scores.get)
    return basin_id, scores[basin_id]


def observe_realization_v2(
    policy: engine.MechanismEvolutionV2,
    candidate: engine.CandidateSpec,
    archive_row: Mapping[str, Any],
) -> None:
    state = policy.realization_v2_state
    if not state:
        return
    receipt = dict(archive_row.get("receipt") or {})
    origin = str(receipt.get("targeted_economic_basin_id") or "")
    fingerprint = dict(archive_row.get("realization_v2_economic_fingerprint") or {})
    assigned, similarity = _assign_anchor(state, fingerprint)
    counts = Counter(state["admission_counts"])
    if similarity < float(state["similarity_threshold"]):
        counts["new_basin_diagnostic"] += 1
        state["admission_counts"] = dict(counts)
        return
    if assigned != origin:
        counts["cross_basin_rejected"] += 1
        state["admission_counts"] = dict(counts)
        return
    behavior = dict(archive_row)
    record = {
        "candidate": candidate.to_dict(),
        "candidate_id": candidate.candidate_id,
        "economic_similarity_cluster_id": origin,
        "economic_similarity_to_anchor": similarity,
        "program_family_id": str(candidate.generation_genes["program_spec"]["family_id"]),
        "behavior_family_id": str(behavior["behavior_family_id"]),
        "family_count": int(behavior.get("policy_local_family_count_at_completion", 1)),
        "search_reward": float(behavior["search_reward"]),
        "block_robust_ordering": dict(behavior.get("block_robust_ordering") or {}),
        "mapped_weight_descriptor_id": behavior.get("mapped_weight_descriptor_id"),
        "turnover_path_descriptor_id": behavior.get("turnover_path_descriptor_id"),
        "raw_fields_json": json.dumps(list(candidate.raw_fields)),
        "selected_asset_overlap_id": behavior.get("selected_asset_overlap_id"),
        "operator_path": candidate.operator_path,
        "program_id": str(candidate.generation_genes["program_id"]),
        "parent_source": "ADAPTIVE_STRICT_DESCENDANT",
    }
    record["concrete_realization_id"] = _realization_id(record)
    record["realization_cell_id"] = _cell_id(record)
    descendants = dict(state["descendants"])
    same_cell = [
        candidate_id
        for candidate_id, value in descendants.items()
        if value["economic_similarity_cluster_id"] == origin
        and value["realization_cell_id"] == record["realization_cell_id"]
    ]
    contenders = same_cell + [candidate.candidate_id]
    records = {**descendants, candidate.candidate_id: record}
    retained = sorted(
        contenders,
        key=lambda candidate_id: policy._selection_key(
            candidate_id, records[candidate_id], include_family_count=False
        ),
    )[: int(state["top_k_per_adaptive_cell"])]
    for candidate_id in same_cell:
        if candidate_id not in retained:
            descendants.pop(candidate_id, None)
    if candidate.candidate_id in retained:
        descendants[candidate.candidate_id] = record
        counts["admitted"] += 1
    else:
        counts["cell_capacity_rejected"] += 1
    state["descendants"] = descendants
    state["admission_counts"] = dict(counts)


def archive_diagnostics(policies: Mapping[str, Any]) -> dict[str, Any]:
    descendants: dict[str, Mapping[str, Any]] = {}
    counters: Counter[str] = Counter()
    mutation_targets: Counter[str] = Counter()
    for policy in policies.values():
        if not isinstance(policy, engine.MechanismEvolutionV2) or not policy.realization_v2_state:
            continue
        state = policy.realization_v2_state
        descendants.update(state["descendants"])
        counters.update(state["admission_counts"])
        mutation_targets.update(state.get("mutation_target_counts") or {})
    cells = {
        (str(record["economic_similarity_cluster_id"]), str(record["realization_cell_id"]))
        for record in descendants.values()
    }
    return {
        "schema_version": 1,
        "archive_id": ARCHIVE_ID,
        "anchored_basin_count": 23,
        "frozen_seed_parent_count": 228,
        "active_descendant_archive_size": len(descendants),
        "occupied_adaptive_realization_cells": len(cells),
        "cells_added": len(cells),
        "admission_counts": dict(sorted(counters.items())),
        "mutation_target_counts": dict(sorted(mutation_targets.items())),
        "validation_reads": 0,
        "oos_reads": 0,
        "sealed_reads": 0,
    }


def operation_diagnostics(ledger: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    evolution = [
        row
        for row in ledger
        if str(row.get("arm") or "") == "temporal_program_evolution"
    ]
    requested = Counter(str(row.get("requested_operation") or "") for row in evolution)
    realized = Counter(str(row.get("realized_operation") or "") for row in evolution)
    crossover = [row for row in evolution if row.get("requested_operation") == "crossover"]
    fallback = [row for row in crossover if bool(row.get("crossover_fallback"))]
    legal = [
        int(row.get("legal_splice_count") or 0)
        for row in crossover
        if row.get("realized_operation") == "crossover"
    ]
    matched = sum(bool(row.get("matched_positive")) for row in evolution)
    return {
        "schema_version": 1,
        "evolution_strict": len(evolution),
        "evolution_matched_positive": matched,
        "evolution_matched_positive_density": matched / max(1, len(evolution)),
        "requested_operation_counts": dict(sorted(requested.items())),
        "realized_operation_counts": dict(sorted(realized.items())),
        "crossover_requested": len(crossover),
        "crossover_realized": sum(
            row.get("realized_operation") == "crossover" for row in crossover
        ),
        "crossover_fallback": len(fallback),
        "crossover_fallback_rate": len(fallback) / max(1, len(crossover)),
        "crossover_fallback_reasons": dict(
            sorted(Counter(str(row.get("fallback_reason") or "") for row in fallback).items())
        ),
        "legal_splice_count_distribution": {
            "minimum": min(legal, default=0),
            "median": float(np.median(legal)) if legal else 0.0,
            "maximum": max(legal, default=0),
        },
    }


def checkpoint_decision(
    ledger: Sequence[Mapping[str, Any]],
    *,
    strict_boundary: int,
    frozen_parent_pool_sha256: str,
) -> dict[str, Any]:
    diagnostics = operation_diagnostics(ledger)
    families = Counter(str(row.get("program_family_id") or "") for row in ledger)
    invalidity = []
    if set(families) - set(ACTIVE_PROGRAM_FAMILIES):
        invalidity.append("P2_P3_OR_UNKNOWN_FAMILY_CONTAMINATION")
    if frozen_parent_pool_sha256 != (
        "A08112ED1765A432D15D259A70F308C2DE5BA7B617D294BFB8349020EC61AA49"
    ):
        invalidity.append("FROZEN_PARENT_POOL_IDENTITY_CHANGED")
    old_ratio = R3_FIRST_10000_CROSSOVER_REALIZED / R3_FIRST_10000_CROSSOVER_REQUESTED
    new_ratio = diagnostics["crossover_realized"] / max(
        1, diagnostics["crossover_requested"]
    )
    crossover_pass = bool(
        diagnostics["crossover_fallback_rate"] <= 0.35
        or new_ratio >= 2.0 * old_ratio
    )
    quality_floor = 0.5 * (
        R3_FIRST_10000_EVOLUTION_MATCHED_POSITIVE / R3_FIRST_10000_EVOLUTION_STRICT
    )
    quality_pass = diagnostics["evolution_matched_positive_density"] >= quality_floor
    if invalidity:
        status = "RESEARCH_INVALID"
    elif int(strict_boundary) == DECISION_BOUNDARY:
        status = (
            "CONTINUE_TO_20000"
            if crossover_pass and quality_pass
            else "STOP_REALIZATION_V2_GATE_NOT_MET_AT_10000"
        )
    elif int(strict_boundary) == STRICT_CAP:
        status = "REALIZATION_V2_20000_HARD_CAP_COMPLETE"
    else:
        status = "CHECKPOINT_ONLY"
    return {
        "schema_version": 1,
        "status": status,
        "strict_boundary": int(strict_boundary),
        "validity": {
            "research_invalidity": invalidity,
            "P1_strict": int(families.get(ACTIVE_PROGRAM_FAMILIES[0], 0)),
            "P4_strict": int(families.get(ACTIVE_PROGRAM_FAMILIES[1], 0)),
            "P2_strict": int(families.get("P2", 0)),
            "P3_strict": int(families.get("P3", 0)),
            "validation_reads": 0,
            "oos_reads": 0,
            "sealed_reads": 0,
        },
        "crossover_gate": {
            "r3_first_10000_requested": R3_FIRST_10000_CROSSOVER_REQUESTED,
            "r3_first_10000_realized": R3_FIRST_10000_CROSSOVER_REALIZED,
            "r3_first_10000_realized_ratio": old_ratio,
            "v2_realized_ratio": new_ratio,
            "fallback_rate_maximum": 0.35,
            "realized_ratio_multiplier_minimum": 2.0,
            "pass": crossover_pass,
        },
        "search_quality_gate": {
            "r3_first_10000_evolution_density": (
                R3_FIRST_10000_EVOLUTION_MATCHED_POSITIVE
                / R3_FIRST_10000_EVOLUTION_STRICT
            ),
            "minimum_density": quality_floor,
            "observed_density": diagnostics["evolution_matched_positive_density"],
            "pass": quality_pass,
        },
        "operation_diagnostics": diagnostics,
        "automatic_next_run_started": False,
    }


__all__ = [
    "ARCHIVE_ID",
    "AUTHORIZATION_SCOPE",
    "AUDIT_PATH",
    "AUTHORIZATION_PATH",
    "AUTHORIZED_STATUS",
    "CAMPAIGN",
    "CHECKPOINT_SIZE",
    "CONSUMED_STATUS",
    "DECISION_BOUNDARY",
    "EVOLUTION_OPERATION_PROBABILITIES",
    "EXECUTION_MODE",
    "FIXED_ALLOCATION_PER_10000",
    "LANE_SEEDS",
    "SEED_CAMPAIGN",
    "SEED_DERIVATION",
    "STRICT_CAP",
    "TURNOVER_REACHABILITY",
    "archive_diagnostics",
    "checkpoint_decision",
    "configure_policy_realization_v2",
    "constructive_crossover",
    "economic_fingerprint_from_evaluation",
    "mutation_target",
    "next_targeted_basin",
    "next_targeted_parent",
    "observe_realization_v2",
    "operation_diagnostics",
    "propose_targeted_realization_v2",
    "restore_policy_realization_v2",
    "select_mutation_groups",
    "targeted_members",
    "targeted_parent_record",
]
