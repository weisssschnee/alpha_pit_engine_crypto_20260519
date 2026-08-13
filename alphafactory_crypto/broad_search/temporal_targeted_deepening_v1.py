"""Receipt-scoped diagnostics for targeted P1/P4 Temporal basin deepening.

The search still uses the existing Temporal Program compiler, policies, mapping,
cost, reward, and evaluator.  This module only freezes the one-run authority and
measures economic-similarity clusters and concrete realizations from persisted
development rows.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import squareform

from .temporal_development_expansion_v1 import (
    ExpansionPreflightError,
    authorization_content_sha,
    committed_file_sha,
    executor_workspace_identity,
    file_sha256,
)


EXECUTION_MODE = "TARGETED_P1_P4_BASIN_DEEPENING_V1"
CAMPAIGN = "crypto_temporal_targeted_p1_p4_basin_deepening_v1"
AUTHORIZATION_PATH = (
    "config/crypto_temporal_targeted_p1_p4_basin_deepening_v1_authorization.json"
)
AUTHORIZATION_SCOPE = "ONE_30000_STRICT_TRAIN_ONLY_P1_P4_TARGETED_DEEPENING"
AUTHORIZED_STATUS = "RUN_AUTHORIZED_ONE_TIME_TARGETED_P1_P4_DEEPENING"
CONSUMED_STATUS = "RUN_AUTHORIZATION_CONSUMED_TARGETED_P1_P4_DEEPENING"
SEED_CAMPAIGN = "CRYPTO_TEMPORAL_TARGETED_P1_P4_BASIN_DEEPENING_V1"
SEED_DERIVATION = (
    "FIRST_UINT32_SHA256_CRYPTO_TEMPORAL_TARGETED_P1_P4_BASIN_DEEPENING_V1_PIPE_LANE_INDEX"
)
ACTIVE_PROGRAM_FAMILIES = (
    "P1_POSITION_STATE_CHANGE_TO_RESPONSE",
    "P4_MULTISCALE_STATE_X_TRANSITION_ROUTING",
)
FIXED_ALLOCATION_PER_10000 = {
    "temporal_program_random": 2_000,
    "temporal_program_cem": 2_000,
    "temporal_program_evolution": 6_000,
}
EVOLUTION_OPERATION_PROBABILITIES = {
    "parameter_mutation_probability": 0.60,
    "mechanism_mutation_probability": 0.10,
    "crossover_probability": 0.30,
}
COMPONENT_PATHS = (
    "alphafactory_crypto/broad_search/expression.py",
    "alphafactory_crypto/broad_search/compositional18m.py",
    "alphafactory_crypto/broad_search/pair18m.py",
    "alphafactory_crypto/broad_search/search_engine_v1.py",
    "alphafactory_crypto/broad_search/experiment_authority.py",
    "alphafactory_crypto/broad_search/temporal_activation_v1.py",
    "alphafactory_crypto/broad_search/temporal_program_v1.py",
    "alphafactory_crypto/broad_search/temporal_development_expansion_v1.py",
    "alphafactory_crypto/broad_search/temporal_targeted_deepening_v1.py",
    "alphafactory_crypto/broad_search/temporal_program_search_v1.py",
    "scripts/run_crypto_temporal_mechanism_program_v1_pc2.ps1",
    "config/crypto_temporal_mechanism_program_v1.json",
)
CHECKPOINT_SIZE = 2_000
STRICT_CAP = 30_000
RAW_ATTEMPT_CAP = 150_000
WALL_SECONDS_CAP = 36_000
DECISION_BOUNDARIES = (10_000, 20_000)
SATURATION_BOUNDARY = 20_000
ECONOMIC_SIMILARITY_THRESHOLDS = (0.95, 0.90, 0.85, 0.80)
CANONICAL_SIMILARITY_THRESHOLD = 0.90
BASELINE_HIGH_QUALITY_MINIMUM_ROWS = 5

_FINGERPRINT_PREFIXES = (
    "primary",
    "control",
    "left_control",
    "right_control",
    "incremental",
    "left_incremental",
    "right_incremental",
)
_FINGERPRINT_SUFFIXES = (
    "net_mean",
    "monthly_block_standard_error",
    "monthly_block_lcb",
    "turnover_mean",
    "cost_mean",
    "support",
)
ECONOMIC_FINGERPRINT_FIELDS = tuple(
    f"{prefix}_{suffix}"
    for prefix in _FINGERPRINT_PREFIXES
    for suffix in _FINGERPRINT_SUFFIXES
) + (
    "search_reward",
    "primary_search_reward",
    "matched_min_search_reward",
    "worst_block_min_matched_net_mean",
    "median_block_joint_search_reward",
    "train_day_sortino",
    "train_day_bootstrap_sortino_p25",
    "train_day_bootstrap_probability_gt_zero",
    "train_mean_one_way_turnover",
    "pair_reward",
    "scalar_net_delta_diagnostic",
)
BASELINE_ROW_FIELDS = (
    "candidate_id",
    "behavior_family_id",
    "program_family_id",
    "program_id",
    "arm",
    "seed",
    "operation",
    "mapped_weight_descriptor_id",
    "selected_asset_overlap_id",
    "turnover_path_descriptor_id",
    "raw_fields_json",
    "operator_path",
    "parent_ids_json",
    *ECONOMIC_FINGERPRINT_FIELDS,
)
EVOLUTION_OPERATIONS = {
    "MECHANISM_PARAMETER_GROUP_MUTATION_1_TO_3": "parameter_mutation",
    "COMPATIBLE_MECHANISM_SPEC_MUTATION": "mechanism_mutation",
    "ONE_POINT_TYPED_MECHANISM_CROSSOVER": "crossover",
    "MECHANISM_EVOLUTION_TYPED_RANDOM_WARMUP": "random_warmup",
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
        raise RuntimeError("targeted deepening lane seeds are not unique")
    return seeds


LANE_SEEDS = derive_lane_seeds()


def validate_authorization(
    repo_root: Path,
    *,
    expected_source_sha: str | None = None,
) -> dict[str, Any]:
    path = repo_root.resolve() / AUTHORIZATION_PATH
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as failure:
        raise ExpansionPreflightError(
            "FAIL_CLOSED_BEFORE_MARKET_READ:targeted_authorization_unreadable"
        ) from failure
    errors: list[str] = []
    budget = dict(payload.get("budget") or {})
    boundaries = dict(payload.get("boundaries") or {})
    run_authorization = dict(payload.get("run_authorization") or {})
    if (
        payload.get("schema_version") != 2
        or payload.get("execution_mode") != EXECUTION_MODE
        or payload.get("status") != AUTHORIZED_STATUS
        or payload.get("run_authorized") is not True
        or payload.get("consumed") is not False
        or payload.get("authorization_sha256") != authorization_content_sha(payload)
    ):
        errors.append("authorization_hash_or_status")
    if run_authorization != {
        "authority": "CURRENT_USER_INSTRUCTION",
        "decision_id": "AUTHORIZE_TARGETED_P1_P4_BASIN_DEEPENING_20260813",
        "scope": AUTHORIZATION_SCOPE,
    }:
        errors.append("authorization_scope")
    if budget != {
        "strict_evaluated_maximum": STRICT_CAP,
        "raw_generation_attempts_maximum": RAW_ATTEMPT_CAP,
        "wall_time_seconds_maximum": WALL_SECONDS_CAP,
        "checkpoint_size": CHECKPOINT_SIZE,
        "workers_default": 10,
        "workers_memory_fallback": 8,
    }:
        errors.append("budget")
    if dict(payload.get("allocation_per_10000") or {}) != FIXED_ALLOCATION_PER_10000:
        errors.append("allocation")
    if dict(payload.get("evolution_operation_probabilities") or {}) != (
        EVOLUTION_OPERATION_PROBABILITIES
    ):
        errors.append("evolution_operation_probabilities")
    if tuple(payload.get("lane_seeds") or ()) != LANE_SEEDS:
        errors.append("lane_seeds")
    if tuple(payload.get("active_program_families") or ()) != ACTIVE_PROGRAM_FAMILIES:
        errors.append("program_families")
    saturation = dict(payload.get("saturation_rule") or {})
    if (
        saturation.get("strict_boundary") != SATURATION_BOUNDARY
        or saturation.get("new_economic_clusters_since_10000_maximum") != 0
        or saturation.get("new_high_quality_deepened_basins_since_10000_maximum")
        != 0
        or saturation.get(
            "new_high_quality_concrete_realizations_since_10000_maximum"
        )
        != 0
        or saturation.get("realization_depth_increase_since_10000_maximum") != 0
    ):
        errors.append("saturation_rule")
    if (
        boundaries.get("train_only") is not True
        or boundaries.get("validation") is not False
        or boundaries.get("oos") is not False
        or boundaries.get("holdout") is not False
        or boundaries.get("forward") is not False
        or boundaries.get("promotion") is not False
        or boundaries.get("automatic_expansion") is not False
        or boundaries.get("family_concentration_can_stop") is not False
        or int(boundaries.get("sealed_reads", -1)) != 0
    ):
        errors.append("boundaries")
    baseline_path = Path(str(payload.get("diagnostic_baseline_path") or ""))
    if not baseline_path.is_absolute():
        baseline_path = repo_root.resolve() / baseline_path
    if (
        not baseline_path.is_file()
        or file_sha256(baseline_path)
        != str(payload.get("diagnostic_baseline_sha256") or "")
    ):
        errors.append("diagnostic_baseline")
    source_sha = str(expected_source_sha or "").lower()
    implementation_sha = str(payload.get("authorized_implementation_sha") or "").lower()
    if source_sha and (
        not implementation_sha
        or subprocess.run(
            ["git", "merge-base", "--is-ancestor", implementation_sha, source_sha],
            cwd=repo_root,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode
        != 0
    ):
        errors.append("authorized_implementation_sha")
    if dict(payload.get("executor_identity") or {}) != executor_workspace_identity(
        repo_root
    ):
        errors.append("executor_identity")
    branch = subprocess.check_output(
        ["git", "branch", "--show-current"], cwd=repo_root, text=True
    ).strip()
    if branch != str(payload.get("expected_branch") or ""):
        errors.append("expected_branch")
    component_hashes = dict(payload.get("authorized_component_sha256") or {})
    if set(component_hashes) != set(COMPONENT_PATHS) or any(
        committed_file_sha(repo_root, component) != str(component_hashes.get(component) or "")
        for component in COMPONENT_PATHS
    ):
        errors.append("authorized_component_sha256")
    if errors:
        raise ExpansionPreflightError(
            "FAIL_CLOSED_BEFORE_MARKET_READ:" + ",".join(sorted(set(errors)))
        )
    return payload


def load_diagnostic_baseline(
    repo_root: Path, authorization: Mapping[str, Any]
) -> dict[str, Any]:
    path = Path(str(authorization["diagnostic_baseline_path"]))
    if not path.is_absolute():
        path = repo_root.resolve() / path
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if file_sha256(path) != str(authorization["diagnostic_baseline_sha256"]):
        raise ExpansionPreflightError(
            "FAIL_CLOSED_BEFORE_MARKET_READ:targeted_diagnostic_baseline_changed"
        )
    return payload


def _as_bool(row: Mapping[str, Any], key: str) -> bool:
    value = row.get(key)
    return bool(value) and str(value).lower() not in {"false", "0", "nan", "none"}


def _dual_positive(row: Mapping[str, Any]) -> bool:
    return (
        float(row.get("left_incremental_net_mean") or 0.0) > 0.0
        and float(row.get("right_incremental_net_mean") or 0.0) > 0.0
    )


def _stable_row_id(row: Mapping[str, Any]) -> str:
    return f"{row.get('_origin', 'current')}|{row.get('candidate_id', '')}"


def _fingerprint_matrix(rows: Sequence[Mapping[str, Any]]) -> np.ndarray:
    if not rows:
        return np.empty((0, len(ECONOMIC_FINGERPRINT_FIELDS)), dtype=np.float64)
    matrix = np.asarray(
        [
            [float(row.get(field) or 0.0) for field in ECONOMIC_FINGERPRINT_FIELDS]
            for row in rows
        ],
        dtype=np.float64,
    )
    for column_index in range(matrix.shape[1]):
        column = matrix[:, column_index]
        finite = np.isfinite(column)
        replacement = float(np.median(column[finite])) if finite.any() else 0.0
        column[~finite] = replacement
        standard_deviation = float(column.std())
        matrix[:, column_index] = (
            column - float(column.mean())
        ) / (standard_deviation if standard_deviation > 1.0e-12 else 1.0)
    return matrix


def _dimension_summary(matrix: np.ndarray) -> dict[str, Any]:
    if matrix.shape[0] == 0:
        return {
            "economic_effective_rank": 0.0,
            "pca_dimensions_50": 0,
            "pca_dimensions_80": 0,
            "pca_dimensions_90": 0,
        }
    singular_values = np.linalg.svd(matrix, compute_uv=False)
    eigenvalues = np.square(singular_values)
    denominator = float(np.square(eigenvalues).sum())
    effective_rank = (
        float(eigenvalues.sum() ** 2 / denominator) if denominator > 0.0 else 0.0
    )
    total = float(eigenvalues.sum())
    cumulative = (
        np.cumsum(eigenvalues / total) if total > 0.0 else np.ones(len(eigenvalues))
    )

    def dimensions(fraction: float) -> int:
        return int(np.searchsorted(cumulative, fraction) + 1) if len(cumulative) else 0

    return {
        "economic_effective_rank": effective_rank,
        "pca_dimensions_50": dimensions(0.50),
        "pca_dimensions_80": dimensions(0.80),
        "pca_dimensions_90": dimensions(0.90),
    }


def _cluster_labels(matrix: np.ndarray, threshold: float) -> np.ndarray:
    if matrix.shape[0] <= 1:
        return np.ones(matrix.shape[0], dtype=np.int64)
    similarity = np.corrcoef(matrix)
    similarity = np.nan_to_num(similarity, nan=-1.0, posinf=1.0, neginf=-1.0)
    np.fill_diagonal(similarity, 1.0)
    distances = np.clip(1.0 - similarity, 0.0, 2.0)
    hierarchy = linkage(squareform(distances, checks=False), method="average")
    return fcluster(hierarchy, t=1.0 - float(threshold), criterion="distance")


def _realization_id(row: Mapping[str, Any]) -> str:
    values = [
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
    return hashlib.sha256(
        json.dumps(values, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest().upper()


def _cluster_payload(
    rows: Sequence[Mapping[str, Any]], labels: np.ndarray, threshold: float
) -> list[dict[str, Any]]:
    grouped: dict[int, list[Mapping[str, Any]]] = defaultdict(list)
    for label, row in zip(labels, rows, strict=True):
        grouped[int(label)].append(row)
    ordered = sorted(grouped.values(), key=lambda local: min(_stable_row_id(row) for row in local))
    output: list[dict[str, Any]] = []
    for index, local in enumerate(ordered, start=1):
        baseline_rows = [row for row in local if row.get("_origin") == "baseline"]
        current_rows = [row for row in local if row.get("_origin") == "current"]
        baseline_realizations = {_realization_id(row) for row in baseline_rows}
        current_realizations = {_realization_id(row) for row in current_rows}

        def unique(key: str) -> int:
            return len({str(row.get(key) or "NOT_AVAILABLE") for row in local})

        parent_ids: set[str] = set()
        for row in local:
            try:
                parent_ids.update(
                    str(value)
                    for value in json.loads(str(row.get("parent_ids_json") or "[]"))
                )
            except json.JSONDecodeError:
                continue
        output.append(
            {
                "economic_similarity_cluster_id": (
                    f"ECO_{int(round(float(threshold) * 100)):03d}_{index:03d}"
                ),
                "row_count": len(local),
                "baseline_row_count": len(baseline_rows),
                "current_row_count": len(current_rows),
                "behavior_family_count": unique("behavior_family_id"),
                "program_basin_count": unique("program_id"),
                "concrete_realization_count": len(
                    baseline_realizations | current_realizations
                ),
                "new_concrete_realization_count": len(
                    current_realizations - baseline_realizations
                ),
                "mapped_weight_realization_count": unique(
                    "mapped_weight_descriptor_id"
                ),
                "selected_asset_realization_count": unique(
                    "selected_asset_overlap_id"
                ),
                "turnover_realization_count": unique(
                    "turnover_path_descriptor_id"
                ),
                "raw_field_realization_count": unique("raw_fields_json"),
                "operator_realization_count": unique("operator_path"),
                "lineage_parent_count": len(parent_ids),
                "seed_count": unique("seed"),
                "program_family_ids": sorted(
                    {str(row.get("program_family_id") or "") for row in local}
                ),
                "program_ids": sorted(
                    {str(row.get("program_id") or "") for row in local}
                ),
                "is_new_economic_cluster": not baseline_rows and bool(current_rows),
                "baseline_high_quality": (
                    len(baseline_rows) >= BASELINE_HIGH_QUALITY_MINIMUM_ROWS
                ),
                "high_quality_basin_deepened": (
                    len(baseline_rows) >= BASELINE_HIGH_QUALITY_MINIMUM_ROWS
                    and bool(current_realizations - baseline_realizations)
                ),
                "full_pnl_vector": "NOT_AVAILABLE",
                "full_weight_vector": "NOT_AVAILABLE",
            }
        )
    return output


def _depth_summary(clusters: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    def at_least(key: str, count: int) -> int:
        return sum(int(row.get(key, 0)) >= count for row in clusters)

    return {
        "economic_basin_count": len(clusters),
        "mapped_weight_realizations_ge_2": at_least(
            "mapped_weight_realization_count", 2
        ),
        "mapped_weight_realizations_ge_3": at_least(
            "mapped_weight_realization_count", 3
        ),
        "turnover_realizations_ge_2": at_least("turnover_realization_count", 2),
        "raw_field_realizations_ge_2": at_least("raw_field_realization_count", 2),
        "asset_selection_realizations_ge_2": at_least(
            "selected_asset_realization_count", 2
        ),
        "singleton_basin_count": sum(int(row.get("row_count", 0)) == 1 for row in clusters),
        "high_quality_basins_deepened": sum(
            bool(row.get("high_quality_basin_deepened")) for row in clusters
        ),
        "new_high_quality_concrete_realizations": sum(
            int(row.get("new_concrete_realization_count", 0))
            for row in clusters
            if bool(row.get("baseline_high_quality"))
        ),
    }


def _cluster_summary(
    baseline_rows: Sequence[Mapping[str, Any]],
    current_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    rows = [
        {**dict(row), "_origin": "baseline"} for row in baseline_rows
    ] + [{**dict(row), "_origin": "current"} for row in current_rows]
    rows.sort(key=_stable_row_id)
    matrix = _fingerprint_matrix(rows)
    summary = {
        "fingerprint_field_count": len(ECONOMIC_FINGERPRINT_FIELDS),
        "fingerprint_fields": list(ECONOMIC_FINGERPRINT_FIELDS),
        "linkage": "AVERAGE",
        "similarity": "PEARSON_ROW_CORRELATION_AFTER_COLUMN_STANDARDIZATION",
        **_dimension_summary(matrix),
        "thresholds": {},
    }
    for threshold in ECONOMIC_SIMILARITY_THRESHOLDS:
        clusters = _cluster_payload(rows, _cluster_labels(matrix, threshold), threshold)
        sizes = sorted((int(row["row_count"]) for row in clusters), reverse=True)
        row_count = max(len(rows), 1)
        summary["thresholds"][f"{threshold:.2f}"] = {
            "economic_cluster_count": len(clusters),
            "new_economic_cluster_count": sum(
                bool(row["is_new_economic_cluster"]) for row in clusters
            ),
            "largest_cluster_share": sizes[0] / row_count if sizes else 0.0,
            "top3_cluster_share": sum(sizes[:3]) / row_count if sizes else 0.0,
            "clusters": clusters,
        }
    return summary


def build_diagnostic_baseline(
    rows: Sequence[Mapping[str, Any]],
    *,
    source_ledger_path: str,
    source_ledger_sha256: str,
    source_strict_count: int,
) -> dict[str, Any]:
    matched = [
        {key: row.get(key) for key in BASELINE_ROW_FIELDS}
        for row in rows
        if _as_bool(row, "matched_positive")
    ]
    matched.sort(key=lambda row: str(row.get("candidate_id") or ""))
    clusters = _cluster_summary(matched, [])
    canonical = clusters["thresholds"][f"{CANONICAL_SIMILARITY_THRESHOLD:.2f}"]
    return {
        "schema_version": 1,
        "status": "TARGETED_DEEPENING_DIAGNOSTIC_BASELINE_NO_POLICY_FEEDBACK",
        "source_ledger_path": source_ledger_path,
        "source_ledger_sha256": source_ledger_sha256,
        "source_strict_count": int(source_strict_count),
        "matched_positive_count": len(matched),
        "matched_positive_rows": matched,
        "economic_cluster_summary": clusters,
        "canonical_depth_summary": _depth_summary(canonical["clusters"]),
        "validation_rows": 0,
        "oos_rows": 0,
        "sealed_reads": 0,
    }


def targeted_diagnostics(
    rows: Sequence[Mapping[str, Any]],
    *,
    baseline: Mapping[str, Any],
    strict_boundary: int,
) -> dict[str, Any]:
    current = [
        row
        for row in rows
        if int(row.get("completion_ordinal") or 0) <= int(strict_boundary)
    ]
    matched_current = [row for row in current if _as_bool(row, "matched_positive")]
    baseline_rows = list(baseline.get("matched_positive_rows") or ())
    economic = _cluster_summary(baseline_rows, matched_current)
    canonical = economic["thresholds"][f"{CANONICAL_SIMILARITY_THRESHOLD:.2f}"]
    depth = _depth_summary(canonical["clusters"])
    baseline_depth = dict(baseline.get("canonical_depth_summary") or {})
    depth_increase = {
        key: int(depth.get(key, 0)) - int(baseline_depth.get(key, 0))
        for key in (
            "mapped_weight_realizations_ge_2",
            "mapped_weight_realizations_ge_3",
            "turnover_realizations_ge_2",
            "raw_field_realizations_ge_2",
            "asset_selection_realizations_ge_2",
        )
    }
    # Reconstruct exact threshold-local membership once for attribution.
    combined = [
        {**dict(row), "_origin": "baseline"} for row in baseline_rows
    ] + [{**dict(row), "_origin": "current"} for row in matched_current]
    combined.sort(key=_stable_row_id)
    labels = _cluster_labels(
        _fingerprint_matrix(combined), CANONICAL_SIMILARITY_THRESHOLD
    )
    groups: dict[int, list[Mapping[str, Any]]] = defaultdict(list)
    for label, row in zip(labels, combined, strict=True):
        groups[int(label)].append(row)
    ordered_groups = sorted(
        groups.values(), key=lambda local: min(_stable_row_id(row) for row in local)
    )
    candidate_to_cluster: dict[str, str] = {}
    exact_clusters: dict[str, dict[str, Any]] = {}
    for index, local in enumerate(ordered_groups, start=1):
        cluster_id = f"ECO_090_{index:03d}"
        exact_clusters[cluster_id] = next(
            row
            for row in canonical["clusters"]
            if row["economic_similarity_cluster_id"] == cluster_id
        )
        for row in local:
            if row.get("_origin") == "current":
                candidate_to_cluster[str(row.get("candidate_id") or "")] = cluster_id

    def family_result(family: str) -> dict[str, Any]:
        local = [row for row in current if str(row.get("program_family_id")) == family]
        matched = [row for row in local if _as_bool(row, "matched_positive")]
        cluster_ids = {
            candidate_to_cluster.get(str(row.get("candidate_id") or ""))
            for row in matched
        } - {None}
        relevant_clusters = [exact_clusters[value] for value in sorted(cluster_ids)]
        return {
            "proposal_count": len(local),
            "dual_positive_count": sum(_dual_positive(row) for row in local),
            "dual_positive_density": (
                sum(_dual_positive(row) for row in local) / len(local) if local else 0.0
            ),
            "replicated_count": sum(
                _as_bool(row, "replicated_candidate") for row in local
            ),
            "replication_density": (
                sum(_as_bool(row, "replicated_candidate") for row in local)
                / len(local)
                if local
                else 0.0
            ),
            "matched_positive_count": len(matched),
            "economic_cluster_count_0_90": len(cluster_ids),
            "concrete_realization_count": len(
                {_realization_id(row) for row in matched}
            ),
            "mapped_weight_realizations_ge_2": sum(
                int(row["mapped_weight_realization_count"]) >= 2
                for row in relevant_clusters
            ),
            "turnover_realizations_ge_2": sum(
                int(row["turnover_realization_count"]) >= 2
                for row in relevant_clusters
            ),
            "high_quality_basins_deepened": sum(
                bool(row["high_quality_basin_deepened"])
                for row in relevant_clusters
            ),
        }

    evolution = [
        row
        for row in current
        if str(row.get("arm") or "") == "temporal_program_evolution"
    ]
    operation_rows = []
    for raw_operation, operation in EVOLUTION_OPERATIONS.items():
        local = [
            row for row in evolution if str(row.get("operation") or "") == raw_operation
        ]
        matched = [row for row in local if _as_bool(row, "matched_positive")]
        cluster_ids = {
            candidate_to_cluster.get(str(row.get("candidate_id") or ""))
            for row in matched
        } - {None}
        relevant_clusters = [exact_clusters[value] for value in sorted(cluster_ids)]
        operation_rows.append(
            {
                "operation": operation,
                "proposal_count": len(local),
                "dual_positive_count": sum(_dual_positive(row) for row in local),
                "matched_positive_count": len(matched),
                "economic_cluster_count_0_90": len(cluster_ids),
                "new_economic_cluster_count_0_90": sum(
                    bool(row["is_new_economic_cluster"]) for row in relevant_clusters
                ),
                "high_quality_basins_deepened": sum(
                    bool(row["high_quality_basin_deepened"])
                    for row in relevant_clusters
                ),
                "new_high_quality_concrete_realizations": sum(
                    int(row["new_concrete_realization_count"])
                    for row in relevant_clusters
                    if bool(row["baseline_high_quality"])
                ),
            }
        )
    per_1000 = 1000.0 / max(int(strict_boundary), 1)
    return {
        "schema_version": 1,
        "status": "TARGETED_DIAGNOSTIC_ONLY_NOT_SEARCH_AUTHORITY",
        "strict_boundary": int(strict_boundary),
        "matched_positive_rows": len(matched_current),
        "matched_positive_behavior_families": len(
            {str(row.get("behavior_family_id") or "") for row in matched_current}
        ),
        "dual_positive_rows": sum(_dual_positive(row) for row in current),
        "replicated_rows": sum(
            _as_bool(row, "replicated_candidate") for row in current
        ),
        "economic_cluster_summary": economic,
        "new_economic_clusters_per_1000": (
            int(canonical["new_economic_cluster_count"]) * per_1000
        ),
        "existing_high_quality_basin_deepening_per_1000": (
            int(depth["high_quality_basins_deepened"]) * per_1000
        ),
        "new_high_quality_concrete_realizations_per_1000": (
            int(depth["new_high_quality_concrete_realizations"]) * per_1000
        ),
        "basin_realization_depth": depth,
        "baseline_basin_realization_depth": baseline_depth,
        "basin_realization_depth_increase": depth_increase,
        "p1_vs_p4": {
            family: family_result(family) for family in ACTIVE_PROGRAM_FAMILIES
        },
        "evolution_operation_attribution": operation_rows,
        "policy_feedback_applied": False,
        "validation_reads": 0,
        "oos_reads": 0,
        "sealed_reads": 0,
    }


def targeted_checkpoint_decision(
    strict_boundary: int,
    current: Mapping[str, Any],
    *,
    checkpoint_10000: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if int(strict_boundary) not in DECISION_BOUNDARIES:
        raise ValueError("targeted deepening diagnostic boundary changed")
    if int(strict_boundary) == 10_000:
        return {
            "schema_version": 1,
            "status": "CONTINUE_TO_PREDECLARED_SATURATION_CHECK",
            "strict_boundary": 10_000,
            "family_concentration_is_diagnostic_only": True,
            "next_stage_proposals_generated": False,
        }
    if checkpoint_10000 is None:
        raise ValueError("targeted 20k saturation check requires the 10k diagnostic")
    current_economic = dict(current["economic_cluster_summary"])["thresholds"]["0.90"]
    prior_economic = dict(checkpoint_10000["economic_cluster_summary"])["thresholds"]["0.90"]
    current_depth = dict(current["basin_realization_depth"])
    prior_depth = dict(checkpoint_10000["basin_realization_depth"])
    depth_keys = (
        "mapped_weight_realizations_ge_2",
        "mapped_weight_realizations_ge_3",
        "turnover_realizations_ge_2",
        "raw_field_realizations_ge_2",
        "asset_selection_realizations_ge_2",
    )
    observed = {
        "new_economic_clusters_since_10000": int(
            current_economic["new_economic_cluster_count"]
        )
        - int(prior_economic["new_economic_cluster_count"]),
        "new_high_quality_deepened_basins_since_10000": int(
            current_depth["high_quality_basins_deepened"]
        )
        - int(prior_depth["high_quality_basins_deepened"]),
        "new_high_quality_concrete_realizations_since_10000": int(
            current_depth["new_high_quality_concrete_realizations"]
        )
        - int(prior_depth["new_high_quality_concrete_realizations"]),
        "realization_depth_increase_since_10000": sum(
            max(0, int(current_depth[key]) - int(prior_depth[key]))
            for key in depth_keys
        ),
    }
    saturated = all(value <= 0 for value in observed.values())
    return {
        "schema_version": 1,
        "status": (
            "STOP_TARGETED_DEEPENING_SATURATED_AT_20000"
            if saturated
            else "CONTINUE_TO_FROZEN_30000_CAP"
        ),
        "strict_boundary": 20_000,
        "observed": observed,
        "family_concentration_is_diagnostic_only": True,
        "next_stage_proposals_generated": False,
    }


def final_next_decision(
    diagnostics: Mapping[str, Any], *, system_valid: bool
) -> str:
    if not system_valid:
        return "SYSTEM_INVALID"
    depth = dict(diagnostics.get("basin_realization_depth") or {})
    baseline = dict(diagnostics.get("baseline_basin_realization_depth") or {})
    mapped_2_increase = int(depth.get("mapped_weight_realizations_ge_2", 0)) - int(
        baseline.get("mapped_weight_realizations_ge_2", 0)
    )
    mapped_3_increase = int(depth.get("mapped_weight_realizations_ge_3", 0)) - int(
        baseline.get("mapped_weight_realizations_ge_3", 0)
    )
    turnover_increase = int(depth.get("turnover_realizations_ge_2", 0)) - int(
        baseline.get("turnover_realizations_ge_2", 0)
    )
    raw_increase = int(depth.get("raw_field_realizations_ge_2", 0)) - int(
        baseline.get("raw_field_realizations_ge_2", 0)
    )
    asset_increase = int(depth.get("asset_selection_realizations_ge_2", 0)) - int(
        baseline.get("asset_selection_realizations_ge_2", 0)
    )
    high_quality = int(depth.get("high_quality_basins_deepened", 0))
    if (
        high_quality >= 10
        and mapped_2_increase >= 5
        and mapped_3_increase >= 2
        and turnover_increase >= 2
        and raw_increase >= 5
        and asset_increase >= 5
    ):
        return "TARGETED_DEEPENING_SUFFICIENT_WAIT_FOR_FORWARD"
    if (
        high_quality == 0
        and mapped_2_increase <= 0
        and turnover_increase <= 0
        and raw_increase <= 0
        and asset_increase <= 0
    ):
        return "SEARCH_CORE_REALIZATION_BOTTLENECK"
    return "CONTINUE_TARGETED_DEEPENING"


__all__ = [
    "ACTIVE_PROGRAM_FAMILIES",
    "AUTHORIZATION_PATH",
    "AUTHORIZATION_SCOPE",
    "AUTHORIZED_STATUS",
    "BASELINE_ROW_FIELDS",
    "CAMPAIGN",
    "CHECKPOINT_SIZE",
    "COMPONENT_PATHS",
    "CONSUMED_STATUS",
    "DECISION_BOUNDARIES",
    "ECONOMIC_FINGERPRINT_FIELDS",
    "ECONOMIC_SIMILARITY_THRESHOLDS",
    "EVOLUTION_OPERATION_PROBABILITIES",
    "EXECUTION_MODE",
    "FIXED_ALLOCATION_PER_10000",
    "LANE_SEEDS",
    "RAW_ATTEMPT_CAP",
    "SATURATION_BOUNDARY",
    "SEED_CAMPAIGN",
    "SEED_DERIVATION",
    "STRICT_CAP",
    "WALL_SECONDS_CAP",
    "build_diagnostic_baseline",
    "final_next_decision",
    "load_diagnostic_baseline",
    "targeted_checkpoint_decision",
    "targeted_diagnostics",
    "validate_authorization",
]
