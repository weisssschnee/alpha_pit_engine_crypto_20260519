"""Receipt-scoped support for one fixed-flow Temporal Program development expansion.

This module is intentionally diagnostic-only.  It validates the one-run
authorization and summarizes the existing candidate ledger; it never proposes,
scores, selects, or updates a candidate.
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np


EXECUTION_MODE = "LARGE_DEVELOPMENT_EXPANSION_V1"
CAMPAIGN = "crypto_temporal_large_development_expansion_v1"
AUTHORIZATION_PATH = (
    "config/crypto_temporal_large_development_expansion_v1_authorization.json"
)
AUTHORIZATION_SCOPE = (
    "ONE_50000_STRICT_TRAIN_ONLY_TEMPORAL_PROGRAM_FIXED_FLOW_EXPANSION"
)
AUTHORIZED_STATUS = "RUN_AUTHORIZED_ONE_TIME_50000_STRICT_DEVELOPMENT_EXPANSION"
CONSUMED_STATUS = "RUN_AUTHORIZATION_CONSUMED_50000_STRICT_DEVELOPMENT_EXPANSION"
SEED_CAMPAIGN = "CRYPTO_TEMPORAL_LARGE_DEVELOPMENT_EXPANSION_V1"
SEED_DERIVATION = (
    "FIRST_UINT32_SHA256_CRYPTO_TEMPORAL_LARGE_DEVELOPMENT_EXPANSION_V1_PIPE_LANE_INDEX"
)
ALL_PROGRAM_FAMILIES = (
    "P1_POSITION_STATE_CHANGE_TO_RESPONSE",
    "P2_RECENT_CROWDING_EVENT_TO_RESPONSE",
    "P3_FLOW_SHOCK_PERSISTENCE_TO_ABSORPTION",
    "P4_MULTISCALE_STATE_X_TRANSITION_ROUTING",
)
FIXED_ALLOCATION_PER_10000 = {
    "temporal_program_random": 2_000,
    "temporal_program_cem": 2_000,
    "temporal_program_evolution": 6_000,
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
    "alphafactory_crypto/broad_search/temporal_program_search_v1.py",
    "scripts/run_crypto_temporal_mechanism_program_v1_pc2.ps1",
    "config/crypto_temporal_mechanism_program_v1.json",
)
CHECKPOINT_SIZE = 2_000
STRICT_CAP = 50_000
RAW_ATTEMPT_CAP = 250_000
WALL_SECONDS_CAP = 64_800
DECISION_BOUNDARIES = (10_000, 20_000, 30_000, 40_000)
EVOLUTION_OPERATIONS = {
    "MECHANISM_PARAMETER_GROUP_MUTATION_1_TO_3": "parameter_mutation",
    "COMPATIBLE_MECHANISM_SPEC_MUTATION": "mechanism_mutation",
    "ONE_POINT_TYPED_MECHANISM_CROSSOVER": "crossover",
    "MECHANISM_EVOLUTION_TYPED_RANDOM_WARMUP": "random_warmup",
}


class ExpansionPreflightError(RuntimeError):
    """A one-run authorization defect detected before market access."""


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


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def authorization_content_sha(payload: Mapping[str, Any]) -> str:
    return _json_sha(
        {key: value for key, value in payload.items() if key != "authorization_sha256"}
    )


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
        raise RuntimeError("development expansion lane seeds are not unique")
    return seeds


LANE_SEEDS = derive_lane_seeds()


def executor_workspace_identity(repo_root: Path) -> dict[str, str]:
    resolved = str(repo_root.resolve()).replace("\\", "/").casefold()
    return {
        "host": platform.node().strip().casefold(),
        "workspace_path_sha256": hashlib.sha256(
            resolved.encode("utf-8")
        ).hexdigest().upper(),
    }


def committed_file_sha(repo_root: Path, relative_path: str) -> str:
    object_id = subprocess.check_output(
        ["git", "rev-parse", f"HEAD:{relative_path}"],
        cwd=repo_root,
        text=True,
    ).strip()
    payload = subprocess.check_output(
        ["git", "cat-file", "blob", object_id], cwd=repo_root
    )
    return hashlib.sha256(payload).hexdigest().upper()


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
            "FAIL_CLOSED_BEFORE_MARKET_READ:authorization_unreadable"
        ) from failure
    errors: list[str] = []
    run_authorization = dict(payload.get("run_authorization") or {})
    budget = dict(payload.get("budget") or {})
    boundaries = dict(payload.get("boundaries") or {})
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
        "decision_id": "AUTHORIZE_LARGE_TEMPORAL_DEVELOPMENT_DISCOVERY_20260812",
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
    if tuple(payload.get("lane_seeds") or ()) != LANE_SEEDS:
        errors.append("lane_seeds")
    if tuple(payload.get("active_program_families") or ()) != ALL_PROGRAM_FAMILIES:
        errors.append("program_families")
    if (
        boundaries.get("train_only") is not True
        or boundaries.get("validation") is not False
        or boundaries.get("oos") is not False
        or boundaries.get("holdout") is not False
        or boundaries.get("forward") is not False
        or boundaries.get("promotion") is not False
        or boundaries.get("automatic_expansion") is not False
        or int(boundaries.get("sealed_reads", -1)) != 0
        or boundaries.get("family_concentration_can_stop") is not False
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
    if dict(payload.get("executor_identity") or {}) != executor_workspace_identity(repo_root):
        errors.append("executor_identity")
    branch = subprocess.check_output(
        ["git", "branch", "--show-current"], cwd=repo_root, text=True
    ).strip()
    if branch != str(payload.get("expected_branch") or ""):
        errors.append("expected_branch")
    component_hashes = dict(payload.get("authorized_component_sha256") or {})
    if set(component_hashes) != set(COMPONENT_PATHS) or any(
        committed_file_sha(repo_root, path) != str(component_hashes.get(path) or "")
        for path in COMPONENT_PATHS
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
    payload = json.loads(path.read_text(encoding="utf-8"))
    if file_sha256(path) != str(authorization["diagnostic_baseline_sha256"]):
        raise ExpansionPreflightError(
            "FAIL_CLOSED_BEFORE_MARKET_READ:diagnostic_baseline_changed"
        )
    return payload


def fixed_flow_decision(strict_boundary: int) -> dict[str, Any]:
    if int(strict_boundary) not in DECISION_BOUNDARIES:
        raise ValueError("fixed-flow diagnostic boundary changed")
    return {
        "schema_version": 1,
        "status": "CONTINUE_FIXED_FLOW_DIAGNOSTIC_ONLY",
        "strict_boundary": int(strict_boundary),
        "allocation_per_10000": dict(FIXED_ALLOCATION_PER_10000),
        "arm_states_before": {arm: "ACTIVE" for arm in FIXED_ALLOCATION_PER_10000},
        "arm_states_after": {arm: "ACTIVE" for arm in FIXED_ALLOCATION_PER_10000},
        "family_concentration_is_diagnostic_only": True,
        "next_stage_proposals_generated": False,
    }


def _as_bool(row: Mapping[str, Any], key: str) -> bool:
    value = row.get(key)
    return bool(value) and str(value).lower() not in {"false", "0", "nan", "none"}


def _dual_positive(row: Mapping[str, Any]) -> bool:
    return (
        float(row.get("left_incremental_net_mean") or 0.0) > 0.0
        and float(row.get("right_incremental_net_mean") or 0.0) > 0.0
    )


def _unique_count(rows: Sequence[Mapping[str, Any]], key: str) -> int:
    return len({str(row.get(key) or "") for row in rows if str(row.get(key) or "")})


def _effective_rank(rows: Sequence[Mapping[str, Any]]) -> float:
    fields = (
        "left_incremental_gross_mean",
        "right_incremental_gross_mean",
        "left_incremental_net_mean",
        "right_incremental_net_mean",
        "left_incremental_turnover_mean",
        "right_incremental_turnover_mean",
        "search_reward",
    )
    if len(rows) < 2:
        return float(len(rows))
    matrix = np.asarray(
        [[float(row.get(field) or 0.0) for field in fields] for row in rows],
        dtype=np.float64,
    )
    scale = matrix.std(axis=0)
    matrix = (matrix - matrix.mean(axis=0)) / np.where(scale > 1e-12, scale, 1.0)
    values = np.linalg.svd(matrix, compute_uv=False) ** 2
    denominator = float(np.square(values).sum())
    return float(values.sum() ** 2 / denominator) if denominator > 0.0 else 0.0


def discovery_diagnostics(
    rows: Sequence[Mapping[str, Any]],
    *,
    baseline: Mapping[str, Any],
    strict_boundary: int,
    process_cpu_seconds: float,
) -> dict[str, Any]:
    """Summarize discovery without feeding any value back to search policy."""

    current = [row for row in rows if int(row.get("completion_ordinal") or 0) <= int(strict_boundary)]
    baseline_clusters = {str(value) for value in baseline.get("economic_behavior_family_ids", ())}
    baseline_basins = {str(value) for value in baseline.get("positive_program_ids", ())}
    dual = [row for row in current if _dual_positive(row)]
    cluster_representatives: dict[str, Mapping[str, Any]] = {}
    for row in dual:
        cluster_representatives.setdefault(str(row.get("behavior_family_id") or ""), row)
    new_clusters = {
        cluster: row
        for cluster, row in cluster_representatives.items()
        if cluster and cluster not in baseline_clusters
    }
    matched_clusters = {
        str(row.get("behavior_family_id") or "")
        for row in current
        if _as_bool(row, "matched_positive")
    }
    new_matched_clusters = matched_clusters - baseline_clusters
    basin_clusters: dict[str, set[str]] = defaultdict(set)
    basin_rows: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for cluster, row in new_clusters.items():
        basin_clusters[str(row.get("program_id") or "")].add(cluster)
    for row in dual:
        basin_rows[str(row.get("program_id") or "")].append(row)
    basin_counts = sorted((len(values) for values in basin_clusters.values()), reverse=True)
    cluster_count = len(new_clusters)
    largest_share = basin_counts[0] / cluster_count if cluster_count else 0.0
    top3_share = sum(basin_counts[:3]) / cluster_count if cluster_count else 0.0
    per_1000 = 1000.0 / max(int(strict_boundary), 1)
    cpu_hours = max(float(process_cpu_seconds) / 3600.0, 1e-12)
    basin_payload = []
    for basin, local in sorted(basin_rows.items()):
        parent_ids = []
        for row in local:
            try:
                parent_ids.extend(json.loads(str(row.get("parent_ids_json") or "[]")))
            except json.JSONDecodeError:
                pass
        basin_payload.append(
            {
                "program_id": basin,
                "new_basin": basin not in baseline_basins,
                "useful_candidate_count": len(local),
                "unique_behavior_count": _unique_count(local, "behavior_family_id"),
                "unique_mapped_weight_count": _unique_count(local, "mapped_weight_descriptor_id"),
                "unique_selected_asset_count": _unique_count(local, "selected_asset_overlap_id"),
                "unique_turnover_path_count": _unique_count(local, "turnover_path_descriptor_id"),
                "unique_raw_field_set_count": _unique_count(local, "raw_fields_json"),
                "unique_operator_path_count": _unique_count(local, "operator_path"),
                "unique_lineage_parent_count": len({str(value) for value in parent_ids}),
                "economic_profile_effective_rank": _effective_rank(local),
            }
        )
    evolution = [row for row in current if str(row.get("arm") or "") == "temporal_program_evolution"]
    by_id = {str(row.get("candidate_id") or ""): row for row in current}
    operation_rows = []
    for operation, category in EVOLUTION_OPERATIONS.items():
        local = [row for row in evolution if str(row.get("operation") or "") == operation]
        new_local = [row for row in local if _dual_positive(row) and str(row.get("behavior_family_id") or "") not in baseline_clusters]
        same_basin = 0
        cross_basin = 0
        depths: list[int] = []
        for row in local:
            try:
                parents = [str(value) for value in json.loads(str(row.get("parent_ids_json") or "[]"))]
            except json.JSONDecodeError:
                parents = []
            depths.append(len(parents))
            parent_basins = {
                str(by_id[parent].get("program_id") or "")
                for parent in parents
                if parent in by_id
            }
            if not parent_basins:
                continue
            if str(row.get("program_id") or "") in parent_basins:
                same_basin += 1
            else:
                cross_basin += 1
        operation_rows.append(
            {
                "operation": category,
                "proposal_count": len(local),
                "new_economic_cluster_count": _unique_count(new_local, "behavior_family_id"),
                "good_basin_deepening_count": sum(
                    _dual_positive(row) and str(row.get("program_id") or "") in baseline_basins
                    for row in local
                ),
                "dual_positive_count": sum(_dual_positive(row) for row in local),
                "matched_positive_count": sum(_as_bool(row, "matched_positive") for row in local),
                "mean_parent_count": float(np.mean(depths)) if depths else 0.0,
                "same_basin_transition_count": same_basin,
                "cross_basin_transition_count": cross_basin,
            }
        )
    return {
        "schema_version": 1,
        "status": "DIAGNOSTIC_ONLY_NOT_SEARCH_AUTHORITY",
        "strict_boundary": int(strict_boundary),
        "new_economic_opportunity_cluster_count": cluster_count,
        "new_economic_opportunity_clusters_per_1000": cluster_count * per_1000,
        "new_economic_opportunity_clusters_per_cpu_hour": cluster_count / cpu_hours,
        "dual_positive_count": len(dual),
        "dual_positive_per_1000": len(dual) * per_1000,
        "development_replication_2_of_3_count": sum(_as_bool(row, "replicated_candidate") for row in current),
        "development_replication_2_of_3_per_1000": sum(_as_bool(row, "replicated_candidate") for row in current) * per_1000,
        "new_matched_positive_economic_cluster_count": len(new_matched_clusters),
        "new_matched_positive_economic_clusters_per_1000": len(new_matched_clusters) * per_1000,
        "largest_basin_share": largest_share,
        "top3_basin_share": top3_share,
        "effective_economic_dimension": _effective_rank(list(new_clusters.values())),
        "new_major_basin_count": sum(
            row["new_basin"] and int(row["unique_behavior_count"]) >= 10
            for row in basin_payload
        ),
        "basins": basin_payload,
        "evolution_operation_attribution": operation_rows,
        "policy_feedback_applied": False,
        "sealed_reads": 0,
    }


__all__ = [
    "ALL_PROGRAM_FAMILIES",
    "AUTHORIZATION_PATH",
    "AUTHORIZATION_SCOPE",
    "AUTHORIZED_STATUS",
    "CAMPAIGN",
    "CHECKPOINT_SIZE",
    "COMPONENT_PATHS",
    "CONSUMED_STATUS",
    "DECISION_BOUNDARIES",
    "EXECUTION_MODE",
    "FIXED_ALLOCATION_PER_10000",
    "LANE_SEEDS",
    "SEED_CAMPAIGN",
    "SEED_DERIVATION",
    "STRICT_CAP",
    "WALL_SECONDS_CAP",
    "authorization_content_sha",
    "discovery_diagnostics",
    "executor_workspace_identity",
    "file_sha256",
    "fixed_flow_decision",
    "load_diagnostic_baseline",
    "validate_authorization",
]
