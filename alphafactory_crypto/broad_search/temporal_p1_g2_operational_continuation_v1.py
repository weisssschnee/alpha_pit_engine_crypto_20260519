"""Exact-checkpoint operational continuation for the P1 G2 12k durable prefix."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

import pandas as pd

from . import search_engine_v1 as engine
from .expression import TypedExpressionRegistry
from .temporal_p1_semantic_expansion_search_v1 import (
    BLOCK_ROBUST_V2_AUTHORITY,
    CHECKPOINT_SIZE,
    EXECUTION_MODE,
    ProposalSupplyExhausted,
    REQUIRED_EXECUTION_COMPONENT_PATHS as SCIENTIFIC_COMPONENT_PATHS,
    STRICT_CAP,
    authorization_content_sha,
    run as run_scientific_search,
)
from .temporal_program_search_v1 import (
    CONFIG_PATH,
    _contracts_from_manifest,
    _json_sha,
    _limits,
    _load_checkpoint,
    _write_checkpoint,
)
from .temporal_representation_successor_v1 import ACTIVE_FAMILIES
from .temporal_representation_tournament_v1 import (
    EXPECTED_AUTHORITY_IDENTITY,
    EXPECTED_LEDGER_SHA256,
    EXPECTED_MARKET_INPUT_IDENTITY,
    EXPECTED_PC2_EXECUTOR_IDENTITY,
    EXPECTED_POOL_SHA256,
    EXPECTED_PREAUTH_RECEIPT_SHA256,
    _load_frozen_inputs,
)
from .temporal_successor_v1 import verify_successor_market_inputs


CONTINUATION_ID = "P1_G2_OPERATIONAL_CONTINUATION_V1"
AUTHORIZATION_PATH = "config/crypto_p1_g2_operational_continuation_v1_authorization.json"
SOURCE_RECEIPT_PATH = "config/crypto_p1_g2_operational_continuation_v1_source_checkpoint.json"
RAW_ATTEMPT_CAP = 1_250_000
RAW_ATTEMPT_TERMINAL = "OPERATIONAL_PROPOSAL_SUPPLY_EXHAUSTED"
IMPORTED_STRICT = 12_000
IMPORTED_CHECKPOINT_LABEL = "checkpoint_import_012000"
NATIVE_CHECKPOINT_LABELS = (
    "checkpoint_006",
    "checkpoint_007",
    "checkpoint_008",
    "checkpoint_009",
)
CONTINUATION_COMPONENT_PATHS = tuple(
    dict.fromkeys(
        (*SCIENTIFIC_COMPONENT_PATHS,
         "alphafactory_crypto/broad_search/temporal_p1_g2_operational_continuation_v1.py",
         SOURCE_RECEIPT_PATH,
         "scripts/authorize_crypto_p1_g2_operational_continuation_v1.py",
         "scripts/verify_crypto_p1_g2_operational_continuation_source_v1.py",
         "scripts/run_crypto_p1_g2_operational_continuation_v1.py",
         "scripts/run_crypto_p1_g2_operational_continuation_v1_pc2.ps1")
    )
)


def _sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("utf-8")
    ).hexdigest().upper()


def _file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()


def _registry(root: Path) -> TypedExpressionRegistry:
    config = engine._read_json(root / CONFIG_PATH)
    return TypedExpressionRegistry(
        _contracts_from_manifest(root, config), **_limits(config)
    )


def _runtime_only_untracked(root: Path, runtime_ids: set[str]) -> bool:
    if _git(root, "diff", "--name-only") or _git(root, "diff", "--cached", "--name-only"):
        return False
    untracked = _git(root, "ls-files", "--others", "--exclude-standard").splitlines()
    allowed = tuple(f"runtime/{runtime_id}/" for runtime_id in runtime_ids)
    return all(path.replace("\\", "/").startswith(allowed) for path in untracked)


def _source_receipt(root: Path) -> dict[str, Any]:
    receipt = engine._read_json(root / SOURCE_RECEIPT_PATH)
    if (
        receipt.get("schema_version") != 1
        or receipt.get("status") != "FROZEN_DURABLE_PREFIX_SOURCE"
        or receipt.get("continuation_id") != CONTINUATION_ID
        or int(receipt.get("durable_strict", -1)) != IMPORTED_STRICT
        or int(receipt.get("durable_generation_attempts", -1)) != 479_114
        or receipt.get("source_runtime_immutable") is not True
        or dict(receipt.get("forbidden_reads") or {})
        != {"validation": 0, "oos": 0, "holdout": 0, "forward": 0,
            "promotion": 0, "sealed": 0}
    ):
        raise RuntimeError("FAIL_CLOSED:SOURCE_CHECKPOINT_RECEIPT")
    return receipt


def _manifest_file_sha(manifest: Mapping[str, Any], name: str) -> str:
    row = next((row for row in manifest["files"] if row["name"] == name), None)
    if row is None:
        raise RuntimeError("FAIL_CLOSED:SOURCE_CHECKPOINT_FILE_SET")
    return str(row["sha256"])


def verify_source_checkpoint(repo_root: Path) -> dict[str, Any]:
    root = repo_root.resolve()
    receipt = _source_receipt(root)
    checkpoint = root / str(receipt["source_checkpoint_relative_path"])
    runtime = root / str(receipt["source_runtime_relative_path"])
    manifest_path = checkpoint / "manifest.json"
    frozen_path = runtime / "frozen_contract.json"
    if not checkpoint.is_dir() or not manifest_path.is_file() or not frozen_path.is_file():
        raise RuntimeError("FAIL_CLOSED:SOURCE_CHECKPOINT_MISSING")
    if _file_sha(manifest_path) != receipt["source_checkpoint_manifest_file_sha256"]:
        raise RuntimeError("FAIL_CLOSED:SOURCE_CHECKPOINT_MANIFEST_SHA")
    if _file_sha(frozen_path) != receipt["source_frozen_contract_file_sha256"]:
        raise RuntimeError("FAIL_CLOSED:SOURCE_FROZEN_FILE_SHA")
    manifest = engine._read_json(manifest_path)
    frozen = engine._read_json(frozen_path)
    source_market = dict(frozen.get("market_preflight") or {})
    carrier_identity = dict(EXPECTED_MARKET_INPUT_IDENTITY["carrier"])
    target_identity = dict(EXPECTED_MARKET_INPUT_IDENTITY["target"])
    if (
        manifest.get("restore_verified") is not True
        or manifest.get("source_sha") != receipt["source_authorization_head"]
        or manifest.get("frozen_contract_sha256") != receipt["source_frozen_contract_sha256"]
        or manifest.get("state_sha256") != receipt["source_checkpoint_state_sha256"]
        or manifest.get("completed_identity_sha256") != receipt["source_completed_identity_sha256"]
        or manifest.get("policy_state_sha256") != receipt["source_policy_state_sha256"]
        or manifest.get("archive_state_sha256") != receipt["source_archive_state_sha256"]
        or int(manifest.get("completed_ledger_row_count", -1)) != IMPORTED_STRICT
        or _manifest_file_sha(manifest, "state.json") != receipt["source_checkpoint_state_file_sha256"]
        or _manifest_file_sha(manifest, "candidate_ledger.parquet")
        != receipt["source_candidate_ledger_file_sha256"]
        or frozen.get("frozen_contract_sha256") != receipt["source_frozen_contract_sha256"]
        or frozen.get("ledger_sha256") != EXPECTED_LEDGER_SHA256
        or frozen.get("parent_pool_sha256") != EXPECTED_POOL_SHA256
        or frozen.get("p1_g2_catalog_sha256") != receipt["p1_g2_catalog_sha256"]
        or frozen.get("block_robust_v2_authority") != BLOCK_ROBUST_V2_AUTHORITY
        or dict(source_market.get("directory_bundle") or {})
        != {
            "file_count": carrier_identity["files"],
            "bytes": carrier_identity["bytes"],
            "bundle_sha256": carrier_identity["bundle_sha256"],
        }
        or source_market.get("cache_identity_sha256") != carrier_identity["identity_sha256"]
        or dict(dict(source_market.get("target_cache") or {}).get("directory_bundle") or {})
        != {
            "file_count": target_identity["files"],
            "bytes": target_identity["bytes"],
            "bundle_sha256": target_identity["bundle_sha256"],
        }
        or dict(source_market.get("target_cache") or {}).get("target_cache_identity_sha256")
        != target_identity["identity_sha256"]
    ):
        raise RuntimeError("FAIL_CLOSED:SOURCE_CHECKPOINT_IDENTITY")
    state, policies, ledger, archive, pairs, metrics, rejected = _load_checkpoint(
        checkpoint,
        registry=_registry(root),
        expected_source=str(receipt["source_authorization_head"]),
        expected_frozen=str(receipt["source_frozen_contract_sha256"]),
        expected_identities=dict(frozen["input_identities"]),
    )
    frame = pd.DataFrame(ledger)
    lanes = dict(sorted(Counter(frame["semantic_lane"].astype(str)).items()))
    families = dict(sorted(Counter(frame["program_family_id"].astype(str)).items()))
    authorities = sorted({
        str(json.loads(value)["authority"])
        for value in frame["block_robust_ordering_json"].astype(str)
    })
    partitions = sorted(set(frame["evaluation_partition"].astype(str)))
    if (
        len(ledger) != IMPORTED_STRICT
        or int(state.get("generation_attempts", -1)) != 479_114
        or lanes != dict(receipt["semantic_lane_counts"])
        or families != dict(receipt["program_family_counts"])
        or int(frame["matched_positive"].astype(bool).sum()) != int(receipt["matched_positive"])
        or int(frame["replicated_candidate"].astype(bool).sum()) != int(receipt["replicated_candidate"])
        or authorities != list(receipt["block_authorities"])
        or partitions != list(receipt["evaluation_partitions"])
        or any(families.get(name, 0) for name in (
            "P2_RECENT_CROWDING_EVENT_TO_RESPONSE",
            "P3_FLOW_SHOCK_PERSISTENCE_TO_ABSORPTION",
        ))
        or pairs
        or _json_sha({key: engine._export_policy(value) for key, value in sorted(policies.items())})
        != receipt["source_policy_state_sha256"]
        or archive.state_hash() != receipt["source_archive_state_sha256"]
    ):
        raise RuntimeError("FAIL_CLOSED:SOURCE_CHECKPOINT_RESTORE")
    return {
        "schema_version": 1,
        "status": "SOURCE_CHECKPOINT_RESTORE_PASS",
        "source_runtime_id": receipt["source_runtime_id"],
        "checkpoint": receipt["source_checkpoint"],
        "checkpoint_manifest_file_sha256": receipt["source_checkpoint_manifest_file_sha256"],
        "strict": len(ledger),
        "generation_attempts": int(state["generation_attempts"]),
        "semantic_lane_counts": lanes,
        "program_family_counts": families,
        "matched_positive": int(frame["matched_positive"].astype(bool).sum()),
        "replicated_candidate": int(frame["replicated_candidate"].astype(bool).sum()),
        "policy_state_sha256": receipt["source_policy_state_sha256"],
        "archive_state_sha256": receipt["source_archive_state_sha256"],
        "metrics_rows": len(metrics),
        "rejected_rows": len(rejected),
        "market_arrays_read": 0,
        "candidate_evaluations": 0,
        "validation_reads": 0,
        "oos_reads": 0,
        "holdout_reads": 0,
        "forward_reads": 0,
        "promotion_reads": 0,
        "sealed_reads": 0,
    }


def validate_authorization(repo_root: Path) -> dict[str, Any]:
    root = repo_root.resolve()
    payload = engine._read_json(root / AUTHORIZATION_PATH)
    errors: list[str] = []
    if (
        payload.get("schema_version") != 1
        or payload.get("continuation_id") != CONTINUATION_ID
        or payload.get("status") != "RUN_AUTHORIZED_ONE_TIME_OPERATIONAL_CONTINUATION_12000_TO_20000"
        or payload.get("run_authorized") is not True
        or payload.get("consumed") is not False
        or payload.get("authorization_sha256") != authorization_content_sha(payload)
    ):
        errors.append("authorization_hash_or_status")
    if dict(payload.get("budget") or {}) != {
        "imported_strict": IMPORTED_STRICT,
        "strict_evaluated_maximum": STRICT_CAP,
        "remaining_strict_maximum": STRICT_CAP - IMPORTED_STRICT,
        "raw_generation_attempts_maximum_total": RAW_ATTEMPT_CAP,
        "checkpoint_size": CHECKPOINT_SIZE,
        "automatic_further_increase": False,
        "terminal_if_exhausted": RAW_ATTEMPT_TERMINAL,
    }:
        errors.append("budget")
    if (
        payload.get("continuation_from_existing_valid_checkpoint") is not True
        or int(payload.get("source_strict", -1)) != IMPORTED_STRICT
        or int(payload.get("source_generation_attempts", -1)) != 479_114
        or int(payload.get("target_strict", -1)) != STRICT_CAP
        or int(payload.get("raw_attempt_ceiling", -1)) != RAW_ATTEMPT_CAP
        or payload.get("scientific_contract_changed") is not False
        or payload.get("adaptive_state_reset") is not False
        or payload.get("fresh_restart") is not False
    ):
        errors.append("continuation_semantics")
    if tuple(payload.get("active_program_families") or ()) != tuple(ACTIVE_FAMILIES):
        errors.append("family_scope")
    if dict(payload.get("forbidden_reads") or {}) != {
        "validation": 0, "oos": 0, "holdout": 0, "forward": 0,
        "promotion": 0, "sealed": 0,
    }:
        errors.append("forbidden_reads")
    if dict(payload.get("scientific_contract_unchanged") or {}) != {
        "search_core": True,
        "economic_contract": True,
        "semantic_catalog": True,
        "dispatcher": True,
        "reward": True,
        "mapping": True,
        "cost": True,
        "evaluator": True,
    }:
        errors.append("scientific_contract")
    receipt = _source_receipt(root)
    if (
        payload.get("source_checkpoint_receipt_path") != SOURCE_RECEIPT_PATH
        or payload.get("source_checkpoint_receipt_file_sha256") != _file_sha(root / SOURCE_RECEIPT_PATH)
        or payload.get("source_checkpoint_manifest_file_sha256")
        != receipt["source_checkpoint_manifest_file_sha256"]
        or payload.get("source_frozen_contract_sha256")
        != receipt["source_frozen_contract_sha256"]
    ):
        errors.append("source_checkpoint_binding")
    if dict(payload.get("authority_identity") or {}) != EXPECTED_AUTHORITY_IDENTITY:
        errors.append("authority_identity")
    if dict(payload.get("market_input_identity") or {}) != EXPECTED_MARKET_INPUT_IDENTITY:
        errors.append("market_input_identity")
    if dict(payload.get("pc2_executor_identity") or {}) != EXPECTED_PC2_EXECUTOR_IDENTITY:
        errors.append("pc2_executor_identity")
    frozen_inputs = dict(payload.get("frozen_inputs") or {})
    if frozen_inputs != {
        "ledger_rows": 50_000,
        "ledger_sha256": EXPECTED_LEDGER_SHA256,
        "matched_positive": 302,
        "target_basins": 23,
        "frozen_parents": 228,
        "parent_pool_sha256": EXPECTED_POOL_SHA256,
        "preauthorization_receipt_sha256": EXPECTED_PREAUTH_RECEIPT_SHA256,
    }:
        errors.append("frozen_inputs")
    implementation = str(payload.get("implementation_source_sha") or "").lower()
    components = dict(payload.get("execution_component_blob_oids") or {})
    if set(components) != set(CONTINUATION_COMPONENT_PATHS):
        errors.append("execution_component_set")
    for relative, expected in components.items():
        try:
            committed = _git(root, "rev-parse", f"{implementation}:{relative}").lower()
            observed = _git(root, "hash-object", f"--path={relative}", relative).lower()
        except (OSError, subprocess.CalledProcessError):
            errors.append("execution_component_missing:" + relative)
            continue
        if committed != str(expected).lower() or observed != committed:
            errors.append("execution_component_drift:" + relative)
    if _git(root, "rev-parse", "HEAD^").lower() != implementation:
        errors.append("authorization_not_direct_successor")
    changed = set(_git(root, "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD").splitlines())
    if changed != {AUTHORIZATION_PATH}:
        errors.append("authorization_commit_not_pure")
    runtime_ids = {str(receipt["source_runtime_id"]), str(payload.get("runtime_id") or "")}
    if not _runtime_only_untracked(root, runtime_ids):
        errors.append("worktree")
    if errors:
        raise RuntimeError("FAIL_CLOSED_BEFORE_MARKET_READ:" + ",".join(sorted(errors)))
    return payload


def preflight(repo_root: Path, *, runtime_id: str) -> dict[str, Any]:
    root = repo_root.resolve()
    authorization = validate_authorization(root)
    if runtime_id != authorization.get("runtime_id"):
        raise RuntimeError("FAIL_CLOSED_BEFORE_MARKET_READ:runtime_id")
    source = verify_source_checkpoint(root)
    market = verify_successor_market_inputs(root)
    baseline, pool = _load_frozen_inputs(root)
    runtime = root / "runtime" / runtime_id
    if runtime.exists() and not (runtime / "launch_claim.json").is_file():
        raise RuntimeError("FAIL_CLOSED_BEFORE_MARKET_READ:nonempty_unclaimed_runtime")
    return {
        "schema_version": 1,
        "status": "OPERATIONAL_CONTINUATION_PREFLIGHT_PASS",
        "runtime_id": runtime_id,
        "authorization_sha256": authorization["authorization_sha256"],
        "source_checkpoint": source,
        "market_preflight_sha256": _sha(market),
        "ledger_rows": int(baseline["source_strict_count"]),
        "ledger_sha256": baseline["source_ledger_sha256"],
        "matched_positive": int(baseline["matched_positive_count"]),
        "target_basins": int(pool["target_basin_count"]),
        "frozen_parents": int(pool["frozen_parent_candidate_count"]),
        "parent_pool_sha256": pool["target_parent_pool_sha256"],
        "market_arrays_read": 0,
        "candidate_evaluations": 0,
        "validation_reads": 0,
        "oos_reads": 0,
        "holdout_reads": 0,
        "forward_reads": 0,
        "promotion_reads": 0,
        "sealed_reads": 0,
    }


def validate_migration_receipt(
    repo_root: Path, *, runtime_id: str, authorization: Mapping[str, Any] | None = None
) -> dict[str, Any]:
    root = repo_root.resolve()
    authority = dict(authorization or validate_authorization(root))
    if runtime_id != authority.get("runtime_id"):
        raise RuntimeError("FAIL_CLOSED:MIGRATION_RUNTIME_ID")
    runtime = root / "runtime" / runtime_id
    receipt_path = runtime / "migration_receipt.json"
    imported = runtime / "checkpoints" / IMPORTED_CHECKPOINT_LABEL
    receipt = engine._read_json(receipt_path)
    core = {key: value for key, value in receipt.items() if key != "migration_receipt_sha256"}
    if (
        receipt.get("status") != "EXACT_CHECKPOINT_MIGRATION_PASS"
        or receipt.get("migration_receipt_sha256") != _sha(core)
        or receipt.get("new_runtime_id") != runtime_id
        or receipt.get("new_authorization_sha256") != authority["authorization_sha256"]
        or receipt.get("old_checkpoint_manifest_file_sha256")
        != authority["source_checkpoint_manifest_file_sha256"]
        or receipt.get("imported_checkpoint") != IMPORTED_CHECKPOINT_LABEL
        or int(receipt.get("strict", -1)) != IMPORTED_STRICT
        or int(receipt.get("generation_attempts", -1)) != 479_114
        or not all(dict(receipt.get("equality") or {}).values())
        or receipt.get("source_runtime_unchanged") is not True
        or _file_sha(imported / "manifest.json")
        != receipt.get("imported_checkpoint_manifest_file_sha256")
    ):
        raise RuntimeError("FAIL_CLOSED:MIGRATION_RECEIPT")
    return receipt


def _frame_sha(rows: list[dict[str, Any]]) -> str:
    payload = pd.DataFrame(rows).to_json(
        orient="records", date_format="iso", double_precision=15
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest().upper()


def _migration_importer(
    root: Path, authorization: Mapping[str, Any]
):
    receipt = _source_receipt(root)
    source_checkpoint = root / str(receipt["source_checkpoint_relative_path"])

    def importer(
        *, runtime_root: Path, registry: TypedExpressionRegistry,
        identities: Mapping[str, Any], source_sha: str, frozen_hash: str,
    ) -> Path:
        source_frozen = engine._read_json(
            root / str(receipt["source_runtime_relative_path"]) / "frozen_contract.json"
        )
        source_state, source_policies, source_ledger, source_archive, source_pairs, source_metrics, source_rejected = _load_checkpoint(
            source_checkpoint,
            registry=registry,
            expected_source=str(receipt["source_authorization_head"]),
            expected_frozen=str(receipt["source_frozen_contract_sha256"]),
            expected_identities=dict(source_frozen["input_identities"]),
        )
        migrated_state = copy.deepcopy(source_state)
        migrated_state["source_sha"] = source_sha
        migrated_state["frozen_contract_sha256"] = frozen_hash
        target = runtime_root / "checkpoints" / IMPORTED_CHECKPOINT_LABEL
        if not target.exists():
            _write_checkpoint(
                runtime_root,
                checkpoint_index=IMPORTED_STRICT // CHECKPOINT_SIZE - 1,
                label=IMPORTED_CHECKPOINT_LABEL,
                state=migrated_state,
                policies=source_policies,
                ledger=source_ledger,
                archive=source_archive,
                pair_rows=source_pairs,
                metrics=source_metrics,
                rejected=source_rejected,
                identities=identities,
                discovery_diagnostic=engine._read_json(source_checkpoint / "discovery_diagnostics.json"),
            )
        imported_state, imported_policies, imported_ledger, imported_archive, imported_pairs, imported_metrics, imported_rejected = _load_checkpoint(
            target,
            registry=registry,
            expected_source=source_sha,
            expected_frozen=frozen_hash,
            expected_identities=identities,
        )
        source_policy_sha = _json_sha({
            key: engine._export_policy(value) for key, value in sorted(source_policies.items())
        })
        imported_policy_sha = _json_sha({
            key: engine._export_policy(value) for key, value in sorted(imported_policies.items())
        })
        source_policy_payloads = {
            key: engine._export_policy(value) for key, value in sorted(source_policies.items())
        }
        imported_policy_payloads = {
            key: engine._export_policy(value) for key, value in sorted(imported_policies.items())
        }
        source_policy_hashes = {
            key: _sha(value) for key, value in source_policy_payloads.items()
        }
        imported_policy_hashes = {
            key: _sha(value) for key, value in imported_policy_payloads.items()
        }
        source_rng_hashes = {
            key: _sha(value["rng_state"]) for key, value in source_policy_payloads.items()
        }
        imported_rng_hashes = {
            key: _sha(value["rng_state"]) for key, value in imported_policy_payloads.items()
        }
        source_dispatcher_hashes = {
            key: _sha(value["realization_v2_state"]["proposal_dispatcher_v1"])
            for key, value in source_policy_payloads.items()
        }
        imported_dispatcher_hashes = {
            key: _sha(value["realization_v2_state"]["proposal_dispatcher_v1"])
            for key, value in imported_policy_payloads.items()
        }
        source_realization_qd_hashes = {
            key: _sha(value["realization_v2_state"])
            for key, value in source_policy_payloads.items()
        }
        imported_realization_qd_hashes = {
            key: _sha(value["realization_v2_state"])
            for key, value in imported_policy_payloads.items()
        }
        new_frozen = engine._read_json(runtime_root / "frozen_contract.json")
        expected_state_sha = _sha(migrated_state)
        imported_state_sha = _sha(imported_state)
        source_ledger_sha = _frame_sha(source_ledger)
        imported_ledger_sha = _frame_sha(imported_ledger)
        equality = {
            "state_except_authority_metadata": expected_state_sha == imported_state_sha,
            "policy_and_rng_state": source_policy_sha == imported_policy_sha,
            "policy_state_by_lane": source_policy_hashes == imported_policy_hashes,
            "rng_state_by_lane": source_rng_hashes == imported_rng_hashes,
            "dispatcher_state_by_lane": source_dispatcher_hashes == imported_dispatcher_hashes,
            "realization_qd_state_by_lane": source_realization_qd_hashes == imported_realization_qd_hashes,
            "candidate_ledger_content_and_order": source_ledger_sha == imported_ledger_sha,
            "archive_state": source_archive.state_hash() == imported_archive.state_hash(),
            "paired_rows": _frame_sha(source_pairs) == _frame_sha(imported_pairs),
            "metrics_rows": _frame_sha(source_metrics) == _frame_sha(imported_metrics),
            "rejected_rows": _frame_sha(source_rejected) == _frame_sha(imported_rejected),
            "attempted_candidate_ids": source_state.get("attempted_exact_ids") == imported_state.get("attempted_exact_ids"),
            "generation_attempts": int(imported_state.get("generation_attempts", -1)) == 479_114,
            "dispatcher_qd_and_adaptive_state": source_policy_sha == imported_policy_sha,
            "strict_prefix": len(imported_ledger) == IMPORTED_STRICT,
            "p1_g2_catalog_identity": (
                source_frozen["p1_g2_catalog_sha256"] == new_frozen["p1_g2_catalog_sha256"]
            ),
            "p1_g1_program_catalog_identity": (
                source_frozen["program_catalog_sha256"] == new_frozen["program_catalog_sha256"]
            ),
            "market_and_economic_identities": (
                source_frozen["input_identities"] == new_frozen["input_identities"]
                and source_frozen["ledger_sha256"] == new_frozen["ledger_sha256"]
                and source_frozen["parent_pool_sha256"] == new_frozen["parent_pool_sha256"]
            ),
        }
        if not all(equality.values()):
            raise RuntimeError("FAIL_CLOSED:MIGRATION_STATE_MISMATCH")
        target_manifest_path = target / "manifest.json"
        core = {
            "schema_version": 1,
            "status": "EXACT_CHECKPOINT_MIGRATION_PASS",
            "continuation_id": CONTINUATION_ID,
            "old_runtime_id": receipt["source_runtime_id"],
            "old_checkpoint": receipt["source_checkpoint"],
            "old_checkpoint_manifest_file_sha256": receipt["source_checkpoint_manifest_file_sha256"],
            "old_source_head": receipt["source_authorization_head"],
            "old_frozen_contract_sha256": receipt["source_frozen_contract_sha256"],
            "source_frozen_development_ledger_sha256": receipt["ledger_sha256"],
            "source_candidate_ledger_rows": len(source_ledger),
            "source_candidate_ledger_file_sha256": receipt["source_candidate_ledger_file_sha256"],
            "new_implementation_sha": authorization["implementation_source_sha"],
            "new_authorization_head": source_sha,
            "new_authorization_sha256": authorization["authorization_sha256"],
            "new_runtime_id": authorization["runtime_id"],
            "imported_checkpoint": IMPORTED_CHECKPOINT_LABEL,
            "imported_checkpoint_manifest_file_sha256": _file_sha(target_manifest_path),
            "strict": len(imported_ledger),
            "generation_attempts": int(imported_state["generation_attempts"]),
            "source_logical_ledger_sha256": source_ledger_sha,
            "imported_logical_ledger_sha256": imported_ledger_sha,
            "source_policy_state_sha256": source_policy_sha,
            "imported_policy_state_sha256": imported_policy_sha,
            "source_policy_state_sha256_by_lane": source_policy_hashes,
            "imported_policy_state_sha256_by_lane": imported_policy_hashes,
            "source_rng_state_sha256_by_lane": source_rng_hashes,
            "imported_rng_state_sha256_by_lane": imported_rng_hashes,
            "source_dispatcher_state_sha256_by_lane": source_dispatcher_hashes,
            "imported_dispatcher_state_sha256_by_lane": imported_dispatcher_hashes,
            "source_realization_qd_state_sha256_by_lane": source_realization_qd_hashes,
            "imported_realization_qd_state_sha256_by_lane": imported_realization_qd_hashes,
            "source_archive_state_sha256": source_archive.state_hash(),
            "imported_archive_state_sha256": imported_archive.state_hash(),
            "source_state_after_authority_rebind_sha256": expected_state_sha,
            "imported_state_sha256": imported_state_sha,
            "equality": equality,
            "source_runtime_unchanged": (
                _file_sha(source_checkpoint / "manifest.json")
                == receipt["source_checkpoint_manifest_file_sha256"]
            ),
            "market_arrays_read": 0,
            "candidate_evaluations": 0,
            "validation_reads": 0,
            "oos_reads": 0,
            "holdout_reads": 0,
            "forward_reads": 0,
            "promotion_reads": 0,
            "sealed_reads": 0,
        }
        migration = {**core, "migration_receipt_sha256": _sha(core)}
        migration_path = runtime_root / "migration_receipt.json"
        if migration_path.is_file():
            if engine._read_json(migration_path) != migration:
                raise RuntimeError("FAIL_CLOSED:MIGRATION_RECEIPT_CHANGED")
        else:
            engine._write_json(migration_path, migration)
        return target

    return importer


def run(repo_root: Path, *, runtime_id: str) -> dict[str, Any]:
    root = repo_root.resolve()
    authorization = validate_authorization(root)
    if runtime_id != authorization.get("runtime_id"):
        raise RuntimeError("FAIL_CLOSED_BEFORE_MARKET_READ:runtime_id")
    source = verify_source_checkpoint(root)
    context = {
        "continuation_id": CONTINUATION_ID,
        "source_runtime_id": source["source_runtime_id"],
        "source_checkpoint": source["checkpoint"],
        "source_checkpoint_manifest_file_sha256": source["checkpoint_manifest_file_sha256"],
        "imported_strict": IMPORTED_STRICT,
        "imported_generation_attempts": int(source["generation_attempts"]),
        "raw_generation_attempts_maximum_total": RAW_ATTEMPT_CAP,
        "terminal_if_exhausted": RAW_ATTEMPT_TERMINAL,
        "automatic_further_increase": False,
    }
    try:
        return run_scientific_search(
            root,
            runtime_id=runtime_id,
            authorization_override=authorization,
            raw_attempt_cap=RAW_ATTEMPT_CAP,
            raw_attempt_terminal=RAW_ATTEMPT_TERMINAL,
            continuation_context=context,
            checkpoint_importer=_migration_importer(root, authorization),
        )
    except ProposalSupplyExhausted as failure:
        runtime = root / "runtime" / runtime_id
        checkpoints = sorted((runtime / "checkpoints").glob("checkpoint_[0-9][0-9][0-9]"))
        latest = checkpoints[-1] if checkpoints else runtime / "checkpoints" / IMPORTED_CHECKPOINT_LABEL
        manifest = engine._read_json(latest / "manifest.json")
        core = {
            "schema_version": 1,
            "status": RAW_ATTEMPT_TERMINAL,
            "runtime_id": runtime_id,
            "raw_generation_attempts_maximum_total": RAW_ATTEMPT_CAP,
            "observed_attempts_at_terminal": failure.attempts,
            "durable_checkpoint": latest.name,
            "durable_strict": int(manifest["completed_ledger_row_count"]),
            "durable_generation_attempts": int(engine._read_json(latest / "state.json")["generation_attempts"]),
            "automatic_further_increase": False,
            "research_invalid": False,
            "validation_reads": 0,
            "oos_reads": 0,
            "holdout_reads": 0,
            "forward_reads": 0,
            "promotion_reads": 0,
            "sealed_reads": 0,
            "automatic_next_run_started": False,
        }
        result = {**core, "operational_stop_sha256": _sha(core)}
        engine._write_json(runtime / "operational_stop.json", result)
        return result


__all__ = [
    "AUTHORIZATION_PATH", "CONTINUATION_COMPONENT_PATHS", "CONTINUATION_ID",
    "IMPORTED_CHECKPOINT_LABEL", "IMPORTED_STRICT", "NATIVE_CHECKPOINT_LABELS",
    "RAW_ATTEMPT_CAP", "RAW_ATTEMPT_TERMINAL", "SOURCE_RECEIPT_PATH",
    "preflight", "run", "validate_authorization", "validate_migration_receipt",
    "verify_source_checkpoint",
]
