"""Fail-closed 30k-to-50k successor support for the canonical temporal runner.

This module is deliberately artifact-only.  It verifies the frozen 30k prefix,
rebuilds cross-candidate state from ``completion_ordinal <= 30000``, and binds a
single external authorization.  It never loads market arrays and never evaluates
a candidate.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import math
import platform
import subprocess
from pathlib import Path
from typing import Any, Mapping, Sequence

import pandas as pd

from . import search_engine_v1 as engine
from .runner18m import _directory_bundle as carrier_directory_bundle
from .temporal_prefix_reconstruction_v1 import (
    PREFIX_BOUNDARY,
    _file_sha,
    _json_sha,
    check_successor_preflight,
)


EXECUTION_MODE = "30K_TO_50K_SUCCESSOR"
FRESH_RANDOM_IDENTITY = "FRESH_RANDOM_CONTROL_AFTER_30K"
NOT_AUTHORIZED_STATUS = "IMPLEMENTED_NOT_AUTHORIZED"
AUTHORIZED_STATUS = "RUN_AUTHORIZED_ONE_TIME_30K_TO_50K_DEVELOPMENT_SUCCESSOR"
CONSUMED_STATUS = "RUN_AUTHORIZATION_CONSUMED_30K_TO_50K_DEVELOPMENT_SUCCESSOR"
SUCCESSOR_CAMPAIGN = "crypto_temporal_program_30k_to_50k_successor_v1"
SUCCESSOR_RECEIPT_PATH = (
    "config/crypto_temporal_program_30k_to_50k_successor_v1_receipt.json"
)
SUCCESSOR_AUTHORIZATION_PATH = (
    "config/crypto_temporal_program_30k_to_50k_successor_v1_authorization.json"
)
RECONSTRUCTION_REPORT_PATH = (
    "runtime/crypto_temporal_30k_prefix_reconstruction_v1_20260811/"
    "prefix_policy_state_reconstruction_030000.json"
)
CARRIER_MANIFEST_PATH = (
    "runtime/crypto_search_engine_v1_4_oi_flow_20260728/"
    "aligned_carrier_manifest.json"
)
TEMPORAL_PROGRAM_CONFIG_PATH = "config/crypto_temporal_mechanism_program_v1.json"
ECONOMIC_RECEIPT_PATH = "config/crypto_search_replication_aware_gate_v1_r3_receipt.json"
PREMARKET_FAILURE_PATH = (
    "config/crypto_temporal_program_30k_to_50k_successor_v1_"
    "pre_market_failure.json"
)
CHECKPOINT_SIZE = 5_000
MAXIMUM_ADDITIONAL_STRICT = 20_000
MAXIMUM_CUMULATIVE_STRICT = 50_000
INVALID_SUFFIX_START = PREFIX_BOUNDARY + 1
RANDOM_SEED_DERIVATION_AUTHORITY = (
    "FIRST_UINT32_SHA256_CRYPTO_TEMPORAL_30K_TO_50K_SUCCESSOR_V1_PIPE_LANE_INDEX"
)
RANDOM_RNG_IMPLEMENTATION_IDENTITY = "python.random.Random|CPYTHON_MT19937_V1"
SUCCESSOR_AUTHORIZATION_SCOPE = (
    "ONE_30K_TO_50K_TRAIN_ONLY_TEMPORAL_PROGRAM_DEVELOPMENT_SUCCESSOR"
)
ADAPTIVE_ARMS = ("temporal_program_cem", "temporal_program_evolution")
BASE_ADAPTIVE_WEIGHTS = {
    "temporal_program_evolution": 3,
    "temporal_program_cem": 1,
}
SUCCESSOR_COMPONENT_PATHS = (
    "alphafactory_crypto/broad_search/expression.py",
    "alphafactory_crypto/broad_search/compositional18m.py",
    "alphafactory_crypto/broad_search/pair18m.py",
    "alphafactory_crypto/broad_search/search_engine_v1.py",
    "alphafactory_crypto/broad_search/experiment_authority.py",
    "alphafactory_crypto/broad_search/temporal_activation_v1.py",
    "alphafactory_crypto/broad_search/temporal_program_v1.py",
    "alphafactory_crypto/broad_search/temporal_prefix_reconstruction_v1.py",
    "alphafactory_crypto/broad_search/temporal_successor_v1.py",
    "alphafactory_crypto/broad_search/temporal_program_search_v1.py",
    "scripts/check_crypto_temporal_30k_successor_v1.py",
    "scripts/check_crypto_temporal_successor_execution_v1.py",
    TEMPORAL_PROGRAM_CONFIG_PATH,
    ECONOMIC_RECEIPT_PATH,
    CARRIER_MANIFEST_PATH,
    PREMARKET_FAILURE_PATH,
    SUCCESSOR_RECEIPT_PATH,
)


class SuccessorPreflightError(RuntimeError):
    """An authorization or source defect detected before market access."""


def _fail(*errors: str) -> None:
    values = sorted(set(str(value) for value in errors if value))
    raise SuccessorPreflightError(
        "FAIL_CLOSED_BEFORE_MARKET_READ:" + ",".join(values or ("unknown",))
    )


def authorization_content_sha(payload: Mapping[str, Any]) -> str:
    return _json_sha(
        {key: value for key, value in payload.items() if key != "authorization_sha256"}
    )


def executor_workspace_identity(repo_root: Path) -> dict[str, str]:
    resolved = str(repo_root.resolve()).replace("\\", "/").casefold()
    return {
        "host": platform.node().strip().casefold(),
        "workspace_path_sha256": hashlib.sha256(
            resolved.encode("utf-8")
        ).hexdigest().upper(),
    }


def _committed_file_sha(repo_root: Path, relative_path: str) -> str:
    object_id = subprocess.check_output(
        ["git", "rev-parse", f"HEAD:{relative_path}"], cwd=repo_root, text=True
    ).strip()
    payload = subprocess.check_output(
        ["git", "cat-file", "blob", object_id], cwd=repo_root
    )
    return hashlib.sha256(payload).hexdigest().upper()


def _complete_directory_bundle(root: Path) -> dict[str, Any]:
    rows = [
        {
            "path": str(path.relative_to(root)).replace("\\", "/"),
            "bytes": int(path.stat().st_size),
            "sha256": _file_sha(path),
        }
        for path in sorted(path for path in root.rglob("*") if path.is_file())
    ]
    return {
        "file_count": len(rows),
        "bytes": sum(int(row["bytes"]) for row in rows),
        "bundle_sha256": _json_sha(rows),
    }


def verify_successor_carrier_cache(
    repo_root: Path,
    *,
    manifest_path: Path | None = None,
) -> dict[str, Any]:
    """Verify the manifest-bound 115-field cache without loading market arrays."""

    repo_root = repo_root.resolve()
    default_manifest = manifest_path is None
    manifest_path = (
        manifest_path.resolve()
        if manifest_path is not None
        else (repo_root / CARRIER_MANIFEST_PATH).resolve()
    )
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        raw_cache_root = Path(str(manifest["cache_root"]))
        cache_root = (
            raw_cache_root
            if raw_cache_root.is_absolute()
            else repo_root / raw_cache_root
        ).resolve()
        metadata_path = cache_root / "metadata.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        observed_bundle = carrier_directory_bundle(cache_root)
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as failure:
        _fail("carrier_cache_unavailable:" + type(failure).__name__)
    expected_bundle = dict(manifest.get("directory_bundle") or {})
    errors: list[str] = []
    if str(metadata.get("identity_sha256") or "") != str(
        manifest.get("cache_identity_sha256") or ""
    ):
        errors.append("carrier_cache_identity")
    if observed_bundle != expected_bundle:
        errors.append("carrier_cache_directory_bundle")
    if errors:
        _fail(*errors)
    return {
        "carrier_manifest_path": CARRIER_MANIFEST_PATH,
        "carrier_manifest_sha256": (
            _committed_file_sha(repo_root, CARRIER_MANIFEST_PATH)
            if default_manifest
            else _file_sha(manifest_path)
        ),
        "cache_root": str(manifest["cache_root"]),
        "cache_identity_sha256": str(manifest["cache_identity_sha256"]),
        "directory_bundle": observed_bundle,
        "market_arrays_read": 0,
        "sealed_reads": 0,
    }


def verify_successor_target_cache(
    repo_root: Path,
    *,
    economic_receipt_path: Path | None = None,
) -> dict[str, Any]:
    """Verify the independently stored Binance target cache without np.load."""

    repo_root = repo_root.resolve()
    default_economic_receipt = economic_receipt_path is None
    try:
        if economic_receipt_path is None:
            config = json.loads(
                (repo_root / TEMPORAL_PROGRAM_CONFIG_PATH).read_text(
                    encoding="utf-8"
                )
            )
            configured_receipt = str(
                dict(config.get("source_authorities") or {}).get(
                    "economic_receipt_template"
                )
                or ""
            )
            if configured_receipt != ECONOMIC_RECEIPT_PATH:
                _fail("economic_receipt_path_changed")
            economic_receipt_path = repo_root / configured_receipt
        else:
            economic_receipt_path = economic_receipt_path.resolve()
        receipt = json.loads(economic_receipt_path.read_text(encoding="utf-8"))
        execution = dict(receipt.get("execution") or {})
        raw_target_root = Path(str(execution["target_cache_path"]))
        target_root = (
            raw_target_root
            if raw_target_root.is_absolute()
            else repo_root / raw_target_root
        ).resolve()
        target_metadata = json.loads(
            (target_root / "metadata.json").read_text(encoding="utf-8")
        )
        target_bundle = _complete_directory_bundle(target_root)

        carrier_manifest = json.loads(
            (repo_root / CARRIER_MANIFEST_PATH).read_text(encoding="utf-8")
        )
        raw_carrier_root = Path(str(carrier_manifest["cache_root"]))
        carrier_root = (
            raw_carrier_root
            if raw_carrier_root.is_absolute()
            else repo_root / raw_carrier_root
        ).resolve()
        carrier_metadata = json.loads(
            (carrier_root / "metadata.json").read_text(encoding="utf-8")
        )
    except SuccessorPreflightError:
        raise
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as failure:
        _fail("target_cache_unavailable:" + type(failure).__name__)

    errors: list[str] = []
    if str(target_metadata.get("identity_sha256") or "") != str(
        execution.get("target_cache_identity_sha256") or ""
    ):
        errors.append("target_cache_identity")
    if str(target_metadata.get("source_cache_identity_sha256") or "") != str(
        carrier_metadata.get("identity_sha256") or ""
    ):
        errors.append("target_cache_source_identity")
    carrier_shape = carrier_metadata.get("shape") or (
        carrier_metadata.get("assets"),
        carrier_metadata.get("timestamps"),
    )
    if tuple(int(value) for value in target_metadata.get("shape") or ()) != tuple(
        int(value) for value in carrier_shape
    ):
        errors.append("target_cache_source_shape")
    timestamp_path = carrier_root / "timestamp_ns.npy"
    if (
        not timestamp_path.is_file()
        or str(target_metadata.get("timestamp_sha256") or "")
        != _file_sha(timestamp_path)
    ):
        errors.append("target_cache_timestamp")
    for field in (
        "venue",
        "source",
        "price_field",
        "formula",
        "execution_delay_hours",
        "horizons_hours",
        "positive_price_required",
        "missing_value_fill",
    ):
        if target_metadata.get(field) != execution.get(field):
            errors.append("target_cache_execution:" + field)
    target_files = dict(target_metadata.get("target_files") or {})
    if set(target_files) != {
        str(int(value)) for value in execution.get("horizons_hours") or ()
    }:
        errors.append("target_cache_horizon_files")
    for target_file in target_files.values():
        target_file = dict(target_file or {})
        path = target_root / str(target_file.get("path") or "")
        if (
            not path.is_file()
            or int(path.stat().st_size) != int(target_file.get("bytes", -1))
            or _file_sha(path) != str(target_file.get("sha256") or "")
        ):
            errors.append("target_cache_file")
    if errors:
        _fail(*errors)
    return {
        "economic_receipt_path": (
            str(economic_receipt_path.relative_to(repo_root)).replace("\\", "/")
            if economic_receipt_path.is_relative_to(repo_root)
            else str(economic_receipt_path)
        ),
        "economic_receipt_sha256": (
            _committed_file_sha(repo_root, ECONOMIC_RECEIPT_PATH)
            if default_economic_receipt
            else _file_sha(economic_receipt_path)
        ),
        "target_cache_path": str(execution["target_cache_path"]),
        "target_cache_identity_sha256": str(target_metadata["identity_sha256"]),
        "directory_bundle": target_bundle,
    }


def verify_successor_market_inputs(repo_root: Path) -> dict[str, Any]:
    """Bind every market-side cache needed by the successor before its claim."""

    carrier = verify_successor_carrier_cache(repo_root)
    return {
        **{
            key: value
            for key, value in carrier.items()
            if key not in {"market_arrays_read", "sealed_reads"}
        },
        "target_cache": verify_successor_target_cache(repo_root),
        "market_arrays_read": 0,
        "sealed_reads": 0,
    }


def receipt_bound_role_bindings(
    authority_identity: Mapping[str, Any],
) -> dict[str, dict[str, str]]:
    authority = dict(authority_identity)
    return {
        "target": {
            "component": "real_policy_upgrade_canary",
            "component_sha256": str(authority["target_contract_sha256"]),
        },
        "optimizer_reward": {
            "component": "real_policy_upgrade_canary",
            "component_sha256": str(
                authority["optimizer_reward_and_matched_attribution_sha256"]
            ),
        },
        "execution_price": {
            "component": "real_policy_upgrade_canary",
            "component_sha256": str(authority["target_execution_sha256"]),
        },
        "cost": {
            "component": "real_data_mapping_cost_evaluator",
            "component_sha256": str(
                authority["portfolio_mapping_and_cost_sha256"]
            ),
        },
    }


def derive_fresh_random_lane_seeds(lane_count: int = 4) -> tuple[int, ...]:
    seeds = tuple(
        int.from_bytes(
            hashlib.sha256(
                f"CRYPTO_TEMPORAL_30K_TO_50K_SUCCESSOR_V1|{index}".encode(
                    "ascii"
                )
            ).digest()[:4],
            byteorder="big",
            signed=False,
        )
        for index in range(int(lane_count))
    )
    if len(seeds) != int(lane_count) or len(set(seeds)) != len(seeds):
        raise RuntimeError("fresh Random seed derivation is not unique")
    return seeds


def validate_authorization_payload(
    authorization: Mapping[str, Any],
    *,
    expected_successor_receipt_sha256: str,
    expected_reconstruction_report_sha256: str,
    expected_bundle_sha256: str,
    expected_source_identity_sha256: str,
    expected_authority_identity: Mapping[str, Any],
    expected_executor_identity: Mapping[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    if authorization.get("schema_version") != 2:
        errors.append("schema_version")
    if authorization.get("authorization_sha256") != authorization_content_sha(
        authorization
    ):
        errors.append("authorization_sha256")
    if authorization.get("authorization_id") != (
        "CRYPTO_TEMPORAL_30K_TO_50K_SUCCESSOR_V1_AUTHORIZATION"
    ) or authorization.get("execution_mode") != EXECUTION_MODE:
        errors.append("authorization_identity")
    if (
        authorization.get("status") != AUTHORIZED_STATUS
        or authorization.get("run_authorized") is not True
    ):
        errors.append("authorization_not_active")
    if authorization.get("consumed") is not False:
        errors.append("authorization_consumed")
    expected_hashes = {
        "successor_receipt_sha256": expected_successor_receipt_sha256,
        "reconstruction_report_sha256": expected_reconstruction_report_sha256,
        "reconstructed_policy_bundle_sha256": expected_bundle_sha256,
        "source_artifact_identity_sha256": expected_source_identity_sha256,
    }
    for key, expected in expected_hashes.items():
        if str(authorization.get(key) or "") != str(expected):
            errors.append(key)
    if dict(authorization.get("authority_identity") or {}) != dict(
        expected_authority_identity
    ):
        errors.append("authority_identity")
    if (
        int(authorization.get("source_evidence_prefix", -1)) != PREFIX_BOUNDARY
        or int(authorization.get("invalid_suffix_start", -1))
        != INVALID_SUFFIX_START
    ):
        errors.append("valid_prefix_boundary")
    implementation_sha = str(authorization.get("authorized_implementation_sha") or "")
    if len(implementation_sha) != 40:
        errors.append("authorized_implementation_sha")
    if not dict(authorization.get("authorized_component_sha256") or {}):
        errors.append("authorized_component_sha256")
    if not str(authorization.get("runtime_id") or ""):
        errors.append("runtime_id")
    run_authorization = dict(authorization.get("run_authorization") or {})
    if (
        run_authorization.get("authority") != "CURRENT_USER_INSTRUCTION"
        or run_authorization.get("scope") != SUCCESSOR_AUTHORIZATION_SCOPE
        or not str(run_authorization.get("decision_id") or "")
    ):
        errors.append("run_authorization")
    if dict(authorization.get("executor_identity") or {}) != dict(
        expected_executor_identity
    ):
        errors.append("executor_identity")
    if dict(authorization.get("receipt_bound_role_bindings") or {}) != (
        receipt_bound_role_bindings(expected_authority_identity)
    ):
        errors.append("receipt_bound_role_bindings")
    market_input = dict(authorization.get("market_input_preflight") or {})
    market_bundle = dict(market_input.get("directory_bundle") or {})
    target_input = dict(market_input.get("target_cache") or {})
    target_bundle = dict(target_input.get("directory_bundle") or {})
    if (
        market_input.get("carrier_manifest_path") != CARRIER_MANIFEST_PATH
        or len(str(market_input.get("carrier_manifest_sha256") or "")) != 64
        or len(str(market_input.get("cache_identity_sha256") or "")) != 64
        or not str(market_input.get("cache_root") or "")
        or len(str(market_bundle.get("bundle_sha256") or "")) != 64
        or int(market_bundle.get("file_count", -1)) <= 0
        or int(market_bundle.get("bytes", -1)) <= 0
        or target_input.get("economic_receipt_path") != ECONOMIC_RECEIPT_PATH
        or len(str(target_input.get("economic_receipt_sha256") or "")) != 64
        or not str(target_input.get("target_cache_path") or "")
        or len(str(target_input.get("target_cache_identity_sha256") or "")) != 64
        or len(str(target_bundle.get("bundle_sha256") or "")) != 64
        or int(target_bundle.get("file_count", -1)) <= 0
        or int(target_bundle.get("bytes", -1)) <= 0
    ):
        errors.append("market_input_preflight")
    replacement = dict(authorization.get("replacement_authorization") or {})
    if replacement and (
        replacement.get("authority") != "CURRENT_USER_INSTRUCTION"
        or replacement.get("reason") != "PRE_MARKET_DEPLOYMENT_PORTABILITY_REPAIR"
        or int(replacement.get("replacement_index", -1)) != 1
        or len(str(replacement.get("replaces_authorization_sha256") or "")) != 64
        or len(str(replacement.get("failed_launch_claim_sha256") or "")) != 64
        or not str(replacement.get("failed_task_id") or "")
        or not str(replacement.get("failed_runtime_id") or "")
        or int(replacement.get("market_arrays_read", -1)) != 0
        or int(replacement.get("candidate_evaluations", -1)) != 0
        or int(replacement.get("sealed_reads", -1)) != 0
        or replacement.get("old_runtime_resume_allowed") is not False
        or replacement.get("economic_contract_unchanged") is not True
        or replacement.get("search_contract_unchanged") is not True
    ):
        errors.append("replacement_authorization")
    if not str(authorization.get("evidence_to_add") or "").strip():
        errors.append("evidence_to_add")
    if not str(authorization.get("decision_to_change") or "").strip():
        errors.append("decision_to_change")
    random_control = dict(authorization.get("random_control") or {})
    if (
        random_control.get("identity") != FRESH_RANDOM_IDENTITY
        or random_control.get("seed_derivation_authority")
        != RANDOM_SEED_DERIVATION_AUTHORITY
        or random_control.get("rng_implementation_identity")
        != RANDOM_RNG_IMPLEMENTATION_IDENTITY
        or tuple(int(value) for value in random_control.get("lane_seeds", ()))
        != derive_fresh_random_lane_seeds()
    ):
        errors.append("fresh_random_seed_authority")
    expected_allocation = {
        FRESH_RANDOM_IDENTITY: 0.2,
        "temporal_program_evolution": 0.6,
        "temporal_program_cem": 0.2,
    }
    if dict(authorization.get("allocation") or {}) != expected_allocation:
        errors.append("allocation")
    checkpoint = dict(authorization.get("checkpoint_contract") or {})
    if (
        int(checkpoint.get("additional_strict_per_decision", -1))
        != CHECKPOINT_SIZE
        or int(checkpoint.get("maximum_additional_strict", -1))
        != MAXIMUM_ADDITIONAL_STRICT
        or int(checkpoint.get("maximum_cumulative_valid_strict", -1))
        != MAXIMUM_CUMULATIVE_STRICT
        or checkpoint.get("family_concentration_is_diagnostic_only") is not True
        or checkpoint.get("pruned_adaptive_budget_reallocation")
        != (
            "KEEP_RANDOM_20_PERCENT_AND_ASSIGN_ALL_ADAPTIVE_80_PERCENT_TO_"
            "SURVIVING_ADAPTIVE_ARMS_PROPORTIONAL_TO_3_TO_1_BASE_WEIGHTS"
        )
    ):
        errors.append("checkpoint_contract")
    boundaries = dict(authorization.get("boundaries") or {})
    expected_boundaries = {
        "train_only": True,
        "validation": False,
        "oos": False,
        "holdout": False,
        "forward": False,
        "promotion": False,
        "automatic_expansion": False,
        "sealed_reads": 0,
    }
    if boundaries != expected_boundaries:
        errors.append("sealed_boundaries")
    if errors:
        _fail(*errors)
    return dict(authorization)


def _prefix_archive(rows: Sequence[Mapping[str, Any]]) -> engine.BehaviorArchive:
    materialized = [dict(row) for row in rows]
    champions: dict[str, int] = {}
    replacements = 0
    for row in materialized:
        row["is_family_champion"] = False
    for index, row in enumerate(materialized):
        family_id = str(row["behavior_family_id"])
        old_index = champions.get(family_id)
        replace = old_index is None
        if old_index is not None:
            old = materialized[old_index]
            current_reward = float(row["search_reward"])
            old_reward = float(old["search_reward"])
            replace = current_reward > old_reward or (
                current_reward == old_reward
                and str(row["exact_expression_id"])
                < str(old["exact_expression_id"])
            )
        if replace:
            if old_index is not None:
                materialized[old_index]["is_family_champion"] = False
                replacements += 1
            row["is_family_champion"] = True
            champions[family_id] = index
    archive = engine.BehaviorArchive.from_rows(materialized)
    archive.duplicate_replacements = replacements
    return archive


def reconstruct_prefix_state_tables(
    *,
    candidates: pd.DataFrame,
    archive_rows: pd.DataFrame,
    rejected: pd.DataFrame,
    source_attempted_exact_ids: set[str],
    source_completed_pair_ids: set[str],
    prefix_boundary: int = PREFIX_BOUNDARY,
    checkpoint_size: int = 2_000,
) -> dict[str, Any]:
    boundary = int(prefix_boundary)
    ordered = candidates.loc[
        candidates["completion_ordinal"].astype(int) <= boundary
    ].sort_values("completion_ordinal", kind="stable")
    ordinals = ordered["completion_ordinal"].astype(int).tolist()
    if ordinals != list(range(1, boundary + 1)):
        _fail("prefix_completion_ordinals")
    archive_prefix = archive_rows.loc[
        archive_rows["completion_ordinal"].astype(int) <= boundary
    ].sort_values("completion_ordinal", kind="stable")
    if len(archive_prefix) != boundary:
        _fail("prefix_archive_row_count")
    if archive_prefix["exact_expression_id"].astype(str).tolist() != ordered[
        "candidate_id"
    ].astype(str).tolist():
        _fail("prefix_archive_candidate_identity")
    archive = _prefix_archive(archive_prefix.to_dict("records"))

    policy_counts: dict[str, dict[str, int]] = {}
    for row in ordered.to_dict("records"):
        key = f"{row['arm']}|{int(row['seed'])}"
        family_id = str(row["behavior_family_id"])
        local = policy_counts.setdefault(key, {})
        local[family_id] = int(local.get(family_id, 0)) + 1
        if int(row["policy_local_family_count_at_completion"]) != local[family_id]:
            _fail("policy_local_family_count")

    prefix_checkpoint_count = int(math.ceil(boundary / int(checkpoint_size)))
    rejected_prefix = rejected.loc[
        rejected["checkpoint_index"].astype(int) < prefix_checkpoint_count
    ]
    evaluated_ids = set(ordered["candidate_id"].astype(str))
    rejected_ids = {
        str(value)
        for value in rejected_prefix.get("candidate_id", pd.Series(dtype=object))
        if value is not None and not pd.isna(value) and str(value)
    }
    attempted = evaluated_ids | rejected_ids
    if not attempted.issubset(set(str(value) for value in source_attempted_exact_ids)):
        _fail("attempted_exact_identity_not_in_source")
    if source_completed_pair_ids:
        # This source skipped Stage 0; no pair identity can be assigned safely to
        # a completion boundary without a pair ledger.
        _fail("completed_pair_identity_boundary_unavailable")
    return {
        "ledger": ordered.to_dict("records"),
        "archive": archive,
        "attempted_exact_ids": sorted(attempted),
        "completed_pair_ids": [],
        "policy_local_family_counts": policy_counts,
        "rejected_prefix_identity_count": len(rejected_ids),
        "lineage_row_count": int(
            ordered.get("parent_ids_json", pd.Series(dtype=object)).notna().sum()
        ),
        "operation_counts": {
            str(key): int(value)
            for key, value in ordered["operation"].astype(str).value_counts().items()
        },
        "suffix_contribution": {
            "candidate_rows": 0,
            "archive_rows": 0,
            "attempted_exact_ids": 0,
            "completed_pair_ids": 0,
            "policy_local_family_counts": 0,
        },
    }


def _require_zero_suffix_contribution(restored: Mapping[str, Any]) -> None:
    expected = {
        "candidate_rows": 0,
        "archive_rows": 0,
        "attempted_exact_ids": 0,
        "completed_pair_ids": 0,
        "policy_local_family_counts": 0,
    }
    if dict(restored.get("suffix_contribution") or {}) != expected:
        _fail("invalid_suffix_state_injection")


def reconstruct_valid_prefix_state(artifact_root: Path) -> dict[str, Any]:
    artifact_root = artifact_root.resolve()
    checkpoint = artifact_root / "checkpoints/checkpoint_017/state.json"
    state = json.loads(checkpoint.read_text(encoding="utf-8"))
    candidates = pd.read_parquet(artifact_root / "candidate_ledger.parquet")
    archive_rows = pd.read_parquet(artifact_root / "behavior_archive.parquet")
    rejected = pd.read_parquet(artifact_root / "rejected_candidate_ledger.parquet")
    restored = reconstruct_prefix_state_tables(
        candidates=candidates,
        archive_rows=archive_rows,
        rejected=rejected,
        source_attempted_exact_ids=set(
            str(value) for value in state.get("attempted_exact_ids", ())
        ),
        source_completed_pair_ids=set(
            str(value) for value in state.get("completed_pair_ids", ())
        ),
    )
    restored["source_checkpoint_state_sha256"] = _file_sha(checkpoint)
    restored["source_candidate_ledger_sha256"] = _file_sha(
        artifact_root / "candidate_ledger.parquet"
    )
    restored["source_behavior_archive_sha256"] = _file_sha(
        artifact_root / "behavior_archive.parquet"
    )
    restored["source_rejected_ledger_sha256"] = _file_sha(
        artifact_root / "rejected_candidate_ledger.parquet"
    )
    restored["state_restoration_sha256"] = _json_sha(
        {
            "attempted_exact_ids": restored["attempted_exact_ids"],
            "completed_pair_ids": restored["completed_pair_ids"],
            "policy_local_family_counts": restored["policy_local_family_counts"],
            "archive_state_sha256": restored["archive"].state_hash(),
            "lineage_row_count": restored["lineage_row_count"],
            "operation_counts": restored["operation_counts"],
            "suffix_contribution": restored["suffix_contribution"],
        }
    )
    return restored


def successor_allocation(arm_states: Mapping[str, Any]) -> dict[str, int]:
    survivors = [
        arm
        for arm in ("temporal_program_evolution", "temporal_program_cem")
        if str(arm_states.get(arm)) != "EXITED"
    ]
    if not survivors:
        raise RuntimeError("no adaptive arm remains for successor allocation")
    allocation = {
        "temporal_program_random": 1_000,
        "temporal_program_evolution": 0,
        "temporal_program_cem": 0,
    }
    adaptive_budget = CHECKPOINT_SIZE - allocation["temporal_program_random"]
    total_weight = sum(BASE_ADAPTIVE_WEIGHTS[arm] for arm in survivors)
    assigned = 0
    for arm in survivors[:-1]:
        value = adaptive_budget * BASE_ADAPTIVE_WEIGHTS[arm] // total_weight
        allocation[arm] = value
        assigned += value
    allocation[survivors[-1]] = adaptive_budget - assigned
    if sum(allocation.values()) != CHECKPOINT_SIZE:
        raise AssertionError("successor allocation underfilled")
    return allocation


def successor_lane_targets(
    allocation: Mapping[str, int],
    *,
    fresh_random_seeds: Sequence[int],
    adaptive_seeds: Sequence[int],
) -> dict[str, int]:
    output: dict[str, int] = {}
    for arm, count in allocation.items():
        seeds = (
            tuple(int(value) for value in fresh_random_seeds)
            if arm == "temporal_program_random"
            else tuple(int(value) for value in adaptive_seeds)
        )
        quotient, remainder = divmod(int(count), len(seeds))
        for index, seed in enumerate(seeds):
            output[f"{arm}|{seed}"] = quotient + int(index < remainder)
    if sum(output.values()) != CHECKPOINT_SIZE:
        raise AssertionError("successor lane allocation underfilled")
    return output


def successor_budget_state(cumulative_valid_strict: int) -> dict[str, Any]:
    cumulative = int(cumulative_valid_strict)
    additional = cumulative - PREFIX_BOUNDARY
    if additional < 0 or additional > MAXIMUM_ADDITIONAL_STRICT:
        raise RuntimeError("successor strict budget exceeded")
    return {
        "source_evidence_prefix": PREFIX_BOUNDARY,
        "additional_strict_evaluated": additional,
        "cumulative_valid_strict": cumulative,
        "additional_budget_remaining": MAXIMUM_ADDITIONAL_STRICT - additional,
        "mechanical_stop_required": additional == MAXIMUM_ADDITIONAL_STRICT,
    }


def successor_checkpoint_decision(base_decision: Mapping[str, Any]) -> dict[str, Any]:
    before = dict(base_decision.get("arm_states_before") or {})
    after = dict(base_decision.get("arm_states_after") or {})
    if set(after) != set(ADAPTIVE_ARMS):
        return {
            **dict(base_decision),
            "status": "STOP_INVALID",
            "successor_action": "STOP_INVALID",
        }
    newly_pruned = sorted(
        arm
        for arm in ADAPTIVE_ARMS
        if str(before.get(arm)) != "EXITED" and str(after.get(arm)) == "EXITED"
    )
    survivors = [arm for arm in ADAPTIVE_ARMS if str(after.get(arm)) != "EXITED"]
    if not survivors:
        action = "STOP_ECONOMIC_FUTILITY"
    elif newly_pruned:
        action = "PRUNE_ARM_AND_CONTINUE"
    else:
        action = "CONTINUE"
    return {
        **dict(base_decision),
        "status": action,
        "successor_action": action,
        "newly_pruned_arms": newly_pruned,
        "next_allocation": (
            successor_allocation(after) if survivors else None
        ),
        "family_concentration_is_diagnostic_only": True,
    }


def _git_blob_sha(repo_root: Path, revision: str, path: str) -> str:
    object_id = subprocess.check_output(
        ["git", "rev-parse", f"{revision}:{path}"], cwd=repo_root, text=True
    ).strip()
    payload = subprocess.check_output(
        ["git", "cat-file", "blob", object_id], cwd=repo_root
    )
    return hashlib.sha256(payload).hexdigest().upper()


def _verify_implementation_binding(
    repo_root: Path, authorization: Mapping[str, Any]
) -> list[str]:
    errors: list[str] = []
    implementation_sha = str(authorization["authorized_implementation_sha"])
    if subprocess.run(
        ["git", "merge-base", "--is-ancestor", implementation_sha, "HEAD"],
        cwd=repo_root,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode != 0:
        errors.append("implementation_sha_not_ancestor")
    expected = dict(authorization.get("authorized_component_sha256") or {})
    if set(expected) != set(SUCCESSOR_COMPONENT_PATHS):
        errors.append("implementation_component_path_set")
        return errors
    for path in SUCCESSOR_COMPONENT_PATHS:
        try:
            implementation_hash = _git_blob_sha(repo_root, implementation_sha, path)
            checkout_hash = _git_blob_sha(repo_root, "HEAD", path)
        except subprocess.CalledProcessError:
            errors.append("implementation_component_missing:" + path)
            continue
        if implementation_hash != str(expected[path]) or checkout_hash != str(
            expected[path]
        ):
            errors.append("implementation_component_hash:" + path)
    if subprocess.run(
        ["git", "diff", "--quiet", "--", *SUCCESSOR_COMPONENT_PATHS],
        cwd=repo_root,
        check=False,
    ).returncode != 0 or subprocess.run(
        ["git", "diff", "--cached", "--quiet", "--", *SUCCESSOR_COMPONENT_PATHS],
        cwd=repo_root,
        check=False,
    ).returncode != 0:
        errors.append("implementation_component_worktree_dirty")
    return errors


def prepare_successor_execution(
    repo_root: Path,
    *,
    artifact_root: Path,
    bundle_path: Path,
    runtime_root: Path,
) -> dict[str, Any]:
    """Verify authorization and rebuild the valid-prefix state before market read."""

    repo_root = repo_root.resolve()
    artifact_root = artifact_root.resolve()
    bundle_path = bundle_path.resolve()
    runtime_root = runtime_root.resolve()
    try:
        receipt = json.loads(
            (repo_root / SUCCESSOR_RECEIPT_PATH).read_text(encoding="utf-8")
        )
        reconstruction = json.loads(
            (repo_root / RECONSTRUCTION_REPORT_PATH).read_text(encoding="utf-8")
        )
        authorization = json.loads(
            (repo_root / SUCCESSOR_AUTHORIZATION_PATH).read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError) as failure:
        _fail("authorization_artifact_read:" + type(failure).__name__)
    successor_check = check_successor_preflight(
        reconstruction=reconstruction,
        receipt=receipt,
        bundle_path=bundle_path,
        artifact_root=artifact_root,
    )
    if successor_check.get("status") != "PASS":
        _fail(*(str(value) for value in successor_check.get("errors", ())))
    authorization = validate_authorization_payload(
        authorization,
        expected_successor_receipt_sha256=str(receipt["receipt_sha256"]),
        expected_reconstruction_report_sha256=_committed_file_sha(
            repo_root, RECONSTRUCTION_REPORT_PATH
        ),
        expected_bundle_sha256=_file_sha(bundle_path),
        expected_source_identity_sha256=str(
            reconstruction["source_artifact_identity_sha256"]
        ),
        expected_authority_identity=dict(reconstruction["authority_identity"]),
        expected_executor_identity=executor_workspace_identity(repo_root),
    )
    observed_market_input = verify_successor_market_inputs(repo_root)
    expected_market_input = dict(authorization.get("market_input_preflight") or {})
    if {
        key: value
        for key, value in observed_market_input.items()
        if key not in {"market_arrays_read", "sealed_reads"}
    } != expected_market_input:
        _fail("market_input_preflight_binding")
    errors = _verify_implementation_binding(repo_root, authorization)
    branch = subprocess.check_output(
        ["git", "branch", "--show-current"], cwd=repo_root, text=True
    ).strip()
    if branch != str(authorization["expected_branch"]):
        errors.append("expected_branch")
    if runtime_root.name != str(authorization["runtime_id"]):
        errors.append("runtime_id")
    if runtime_root.exists():
        errors.append("non_fresh_output_root")
    source_hashes = dict(authorization.get("source_artifact_sha256") or {})
    expected_source_paths = {
        "candidate_ledger.parquet": artifact_root / "candidate_ledger.parquet",
        "behavior_archive.parquet": artifact_root / "behavior_archive.parquet",
        "rejected_candidate_ledger.parquet": (
            artifact_root / "rejected_candidate_ledger.parquet"
        ),
        "checkpoint_017_state.json": (
            artifact_root / "checkpoints/checkpoint_017/state.json"
        ),
    }
    if set(source_hashes) != set(expected_source_paths):
        errors.append("source_artifact_hash_set")
    else:
        for name, path in expected_source_paths.items():
            if not path.is_file() or _file_sha(path) != str(source_hashes[name]):
                errors.append("source_artifact_hash:" + name)
    if errors:
        _fail(*errors)
    restored = reconstruct_valid_prefix_state(artifact_root)
    _require_zero_suffix_contribution(restored)
    try:
        with gzip.open(bundle_path, "rt", encoding="utf-8") as handle:
            bundle = json.load(handle)
    except (OSError, json.JSONDecodeError) as failure:
        _fail("reconstructed_policy_bundle:" + type(failure).__name__)
    expected_policy_keys = {
        f"{arm}|{seed}"
        for arm in ADAPTIVE_ARMS
        for seed in (1118667271, 873488160, 3664147548, 193613803)
    }
    if (
        bundle.get("status") != "PREFIX_POLICY_STATE_RECONSTRUCTION_PASS"
        or set(dict(bundle.get("policies") or {})) != expected_policy_keys
        or int(bundle.get("source_evidence_prefix", -1)) != PREFIX_BOUNDARY
        or bundle.get("random_state_scope") != FRESH_RANDOM_IDENTITY
    ):
        _fail("reconstructed_policy_bundle_state")
    return {
        "status": "SUCCESSOR_PREFLIGHT_PASS",
        "market_arrays_read": 0,
        "sealed_reads": 0,
        "authorization": authorization,
        "authorization_sha256": authorization["authorization_sha256"],
        "successor_receipt": receipt,
        "successor_receipt_sha256": receipt["receipt_sha256"],
        "reconstruction": reconstruction,
        "reconstructed_policy_bundle": bundle,
        "restored_prefix": restored,
        "fresh_random_lane_seeds": list(derive_fresh_random_lane_seeds()),
        "market_input_preflight": observed_market_input,
    }


def check_successor_implementation(
    repo_root: Path,
    *,
    artifact_root: Path,
    bundle_path: Path,
) -> dict[str, Any]:
    """Independently verify READY/NOT_AUTHORIZED without enabling a run."""

    repo_root = repo_root.resolve()
    artifact_root = artifact_root.resolve()
    bundle_path = bundle_path.resolve()
    errors: list[str] = []
    try:
        receipt = json.loads(
            (repo_root / SUCCESSOR_RECEIPT_PATH).read_text(encoding="utf-8")
        )
        reconstruction = json.loads(
            (repo_root / RECONSTRUCTION_REPORT_PATH).read_text(encoding="utf-8")
        )
        authorization = json.loads(
            (repo_root / SUCCESSOR_AUTHORIZATION_PATH).read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError) as failure:
        return {
            "status": "FAIL",
            "errors": ["artifact_read:" + type(failure).__name__],
            "market_arrays_read": 0,
            "sealed_reads": 0,
        }
    preflight = check_successor_preflight(
        reconstruction=reconstruction,
        receipt=receipt,
        bundle_path=bundle_path,
        artifact_root=artifact_root,
    )
    errors.extend(str(value) for value in preflight.get("errors", ()))
    if authorization.get("authorization_sha256") != authorization_content_sha(
        authorization
    ):
        errors.append("authorization_sha256")
    if (
        authorization.get("status") != NOT_AUTHORIZED_STATUS
        or authorization.get("run_authorized") is not False
        or authorization.get("consumed") is not False
        or authorization.get("authorized_implementation_sha") is not None
        or dict(authorization.get("authorized_component_sha256") or {})
        or authorization.get("runtime_id") is not None
        or authorization.get("run_authorization") is not None
        or authorization.get("executor_identity") is not None
    ):
        errors.append("implementation_only_authorization_state")
    if (
        authorization.get("successor_receipt_sha256")
        != receipt.get("receipt_sha256")
        or authorization.get("reconstruction_report_sha256")
        != _committed_file_sha(repo_root, RECONSTRUCTION_REPORT_PATH)
        or authorization.get("reconstructed_policy_bundle_sha256")
        != _file_sha(bundle_path)
        or authorization.get("source_artifact_identity_sha256")
        != reconstruction.get("source_artifact_identity_sha256")
        or dict(authorization.get("authority_identity") or {})
        != dict(reconstruction.get("authority_identity") or {})
    ):
        errors.append("authorization_frozen_binding")
    random_control = dict(authorization.get("random_control") or {})
    if (
        random_control.get("identity") != FRESH_RANDOM_IDENTITY
        or random_control.get("seed_derivation_authority")
        != RANDOM_SEED_DERIVATION_AUTHORITY
        or random_control.get("rng_implementation_identity")
        != RANDOM_RNG_IMPLEMENTATION_IDENTITY
        or tuple(int(value) for value in random_control.get("lane_seeds", ()))
        != derive_fresh_random_lane_seeds()
    ):
        errors.append("fresh_random_contract")
    if authorization.get("schema_version") != 2:
        errors.append("schema_version")
    if dict(authorization.get("receipt_bound_role_bindings") or {}) != (
        receipt_bound_role_bindings(reconstruction["authority_identity"])
    ):
        errors.append("receipt_bound_role_bindings")
    if not str(authorization.get("evidence_to_add") or "").strip():
        errors.append("evidence_to_add")
    if not str(authorization.get("decision_to_change") or "").strip():
        errors.append("decision_to_change")
    source_hashes = dict(authorization.get("source_artifact_sha256") or {})
    source_paths = {
        "candidate_ledger.parquet": artifact_root / "candidate_ledger.parquet",
        "behavior_archive.parquet": artifact_root / "behavior_archive.parquet",
        "rejected_candidate_ledger.parquet": (
            artifact_root / "rejected_candidate_ledger.parquet"
        ),
        "checkpoint_017_state.json": (
            artifact_root / "checkpoints/checkpoint_017/state.json"
        ),
    }
    if set(source_hashes) != set(source_paths):
        errors.append("source_artifact_hash_set")
    else:
        for name, path in source_paths.items():
            if not path.is_file() or _file_sha(path) != str(source_hashes[name]):
                errors.append("source_artifact_hash:" + name)
    for path in SUCCESSOR_COMPONENT_PATHS:
        if not (repo_root / path).is_file():
            errors.append("missing_component:" + path)
    return {
        "schema_version": 1,
        "status": "PASS" if not errors else "FAIL",
        "errors": sorted(set(errors)),
        "prefix_reconstruction": reconstruction.get("status"),
        "successor_implementation": "READY" if not errors else "INVALID",
        "successor_authorization": "NOT_AUTHORIZED",
        "market_continuation": "NOT_RUN",
        "validation_oos_promotion": "FORBIDDEN",
        "authorization_sha256": authorization.get("authorization_sha256"),
        "market_arrays_read": 0,
        "candidate_evaluations": 0,
        "sealed_reads": 0,
    }


__all__ = [
    "AUTHORIZED_STATUS",
    "CONSUMED_STATUS",
    "EXECUTION_MODE",
    "FRESH_RANDOM_IDENTITY",
    "NOT_AUTHORIZED_STATUS",
    "SUCCESSOR_AUTHORIZATION_PATH",
    "SUCCESSOR_CAMPAIGN",
    "SUCCESSOR_COMPONENT_PATHS",
    "SuccessorPreflightError",
    "authorization_content_sha",
    "check_successor_implementation",
    "derive_fresh_random_lane_seeds",
    "executor_workspace_identity",
    "prepare_successor_execution",
    "reconstruct_prefix_state_tables",
    "reconstruct_valid_prefix_state",
    "receipt_bound_role_bindings",
    "SUCCESSOR_AUTHORIZATION_SCOPE",
    "successor_allocation",
    "successor_budget_state",
    "successor_checkpoint_decision",
    "successor_lane_targets",
    "validate_authorization_payload",
    "verify_successor_carrier_cache",
    "verify_successor_market_inputs",
    "verify_successor_target_cache",
]
