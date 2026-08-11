"""Artifact-only reconstruction of the valid 30k temporal policy prefix.

This module never loads market arrays and never evaluates a candidate.  It
replays only persisted optimizer learning facts, then compares those facts to
the adaptive policy snapshots stored in checkpoint 017.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping

import pandas as pd

from . import search_engine_v1 as engine


PREFIX_BOUNDARY = 30_000
ADAPTIVE_ARMS = ("temporal_program_cem", "temporal_program_evolution")
ALLOWED_SUFFIX_ARMS = (
    "temporal_program_random",
    "temporal_program_random_diagnostic",
)
AUTHORITY_IDENTITY_KEYS = (
    "source_frozen_contract_sha256",
    "source_producer_sha",
    "economic_receipt_sha256",
    "target_contract_sha256",
    "target_execution_sha256",
    "portfolio_mapping_and_cost_sha256",
    "optimizer_reward_and_matched_attribution_sha256",
    "market_contract_sha256",
    "program_catalog_sha256",
    "behavior_contract_sha256",
)


def _json_sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()


def _file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _authority_identity_from_frozen(
    frozen: Mapping[str, Any],
) -> dict[str, str]:
    economic = dict(frozen["economic_receipt"])
    components = dict(economic["component_sha256"])
    market_contract = dict(dict(frozen["config"])["market_contract"])
    return {
        "source_frozen_contract_sha256": _json_sha(frozen),
        "source_producer_sha": str(frozen["source_sha"]),
        "economic_receipt_sha256": str(economic["receipt_sha256"]),
        "target_contract_sha256": str(components["target_contract"]),
        "target_execution_sha256": str(components["target_execution"]),
        "portfolio_mapping_and_cost_sha256": str(
            components["portfolio_mapping_and_cost"]
        ),
        "optimizer_reward_and_matched_attribution_sha256": str(
            components["optimizer_reward_and_matched_attribution"]
        ),
        "market_contract_sha256": _json_sha(market_contract),
        "program_catalog_sha256": str(frozen["program_catalog_sha256"]),
        "behavior_contract_sha256": str(frozen["behavior_contract_sha256"]),
    }


def _source_artifact_identity(
    *,
    checkpoint: str,
    source_sha: str,
    input_hashes: Mapping[str, str],
    prefix_boundary: int,
) -> str:
    return _json_sha(
        {
            "checkpoint": checkpoint,
            "source_sha": source_sha,
            "input_hashes": dict(input_hashes),
            "prefix_boundary": int(prefix_boundary),
        }
    )


def _parse_json_cell(value: Any) -> Any:
    return json.loads(value) if isinstance(value, str) else value


def _evolution_selection_key(
    parameters: Mapping[str, Any],
    candidate_id: str,
    record: Mapping[str, Any],
) -> tuple[Any, ...]:
    if parameters.get("selection_authority") != (
        "DEVELOPMENT_THREE_BLOCK_ROBUST_ORDERING_V1"
    ):
        base: tuple[Any, ...] = (-float(record["search_reward"]),)
    else:
        ordering = dict(record.get("block_robust_ordering") or {})
        if ordering.get("authority") != (
            "DEVELOPMENT_THREE_BLOCK_ROBUST_ORDERING_V1"
        ):
            raise ValueError("block-robust Evolution observation is unbound")
        base = (
            -int(ordering["replicated_positive_block_count"]),
            -float(ordering["worst_block_min_matched_net_mean"]),
            -float(ordering["median_block_joint_search_reward"]),
            float(ordering["max_required_mean_one_way_turnover"]),
            -float(ordering["min_required_support"]),
        )
    return (*base, str(candidate_id))


def _reconstruct_evolution_learning_state(
    rows: pd.DataFrame,
    *,
    parameters: Mapping[str, Any],
) -> dict[str, Any]:
    population: dict[str, dict[str, Any]] = {}
    operation_counts: Counter[str] = Counter()
    for row in rows.itertuples(index=False):
        candidate_id = str(row.candidate_id)
        family_id = str(row.behavior_family_id)
        record = {
            "candidate": _parse_json_cell(row.candidate_spec_json),
            "search_reward": float(row.search_reward),
            "block_robust_ordering": _parse_json_cell(
                row.block_robust_ordering_json
            ),
            "behavior_family_id": family_id,
            "family_count": int(row.policy_local_family_count_at_completion),
        }
        keep_new = True
        for old_id in [
            key
            for key, value in population.items()
            if str(value["behavior_family_id"]) == family_id
        ]:
            if _evolution_selection_key(
                parameters, old_id, population[old_id]
            ) < _evolution_selection_key(parameters, candidate_id, record):
                keep_new = False
                break
            del population[old_id]
        if not keep_new:
            continue
        population[candidate_id] = record
        operation_counts[str(row.operation)] += 1
        limit = int(parameters.get("population_limit", 256))
        if len(population) > limit:
            retained = sorted(
                population,
                key=lambda value: _evolution_selection_key(
                    parameters, value, population[value]
                ),
            )[:limit]
            population = {key: population[key] for key in retained}
    return {
        "population": population,
        "verified_parameter_mutations": int(
            operation_counts[engine.MECHANISM_EVOLUTION_OPERATIONS[0]]
        ),
        "verified_mechanism_mutations": int(
            operation_counts[engine.MECHANISM_EVOLUTION_OPERATIONS[1]]
        ),
        "verified_crossovers": int(
            operation_counts[engine.MECHANISM_EVOLUTION_OPERATIONS[2]]
        ),
    }


def _reconstruct_cem_learning_state(
    rows: pd.DataFrame,
    *,
    expected_policy: Mapping[str, Any],
) -> dict[str, Any]:
    catalog = tuple(
        engine.MechanismSpec.from_dict(value) for value in expected_policy["catalog"]
    )
    templates = sorted({value.template_id for value in catalog})
    template_probabilities = {
        value: 1.0 / len(templates) for value in templates
    }
    mechanism_probabilities: dict[str, dict[str, float]] = {}
    for template in templates:
        mechanism_ids = sorted(
            value.mechanism_id
            for value in catalog
            if value.template_id == template
        )
        mechanism_probabilities[template] = {
            value: 1.0 / len(mechanism_ids) for value in mechanism_ids
        }
    parameters = dict(expected_policy["parameters"])
    update_count = 0
    for checkpoint_index in sorted(rows["checkpoint_index"].astype(int).unique()):
        local = rows.loc[rows["checkpoint_index"].astype(int) == checkpoint_index]
        if not len(local):
            continue
        champions: dict[str, Mapping[str, Any]] = {}
        for row in local.itertuples(index=False):
            family_id = str(row.behavior_family_id)
            candidate = {
                "candidate_id": str(row.candidate_id),
                "search_reward": float(row.search_reward),
                "candidate_spec_json": row.candidate_spec_json,
            }
            previous = champions.get(family_id)
            if previous is None or (
                -candidate["search_reward"], candidate["candidate_id"]
            ) < (-previous["search_reward"], previous["candidate_id"]):
                champions[family_id] = candidate
        ordered = sorted(
            champions.values(),
            key=lambda value: (-value["search_reward"], value["candidate_id"]),
        )
        elite_count = max(
            1,
            int(
                math.ceil(
                    float(parameters.get("elite_fraction", 0.20)) * len(ordered)
                )
            ),
        )
        template_counts: Counter[str] = Counter()
        mechanism_counts: dict[str, Counter[str]] = defaultdict(Counter)
        for candidate in ordered[:elite_count]:
            payload = _parse_json_cell(candidate["candidate_spec_json"])
            spec = engine.MechanismSpec.from_dict(
                payload["generation_genes"]["mechanism_spec"]
            )
            template_counts[spec.template_id] += 1
            mechanism_counts[spec.template_id][spec.mechanism_id] += 1
        common = {
            "smoothing": float(parameters.get("smoothing", 0.35)),
            "minimum_probability": float(
                parameters.get("minimum_probability", 0.002)
            ),
            "entropy_floor_ratio": float(
                parameters.get("entropy_floor_ratio", 0.60)
            ),
            "pseudocount": float(parameters.get("count_pseudocount", 0.50)),
        }
        template_probabilities = engine._regularized_mechanism_probabilities(
            previous=template_probabilities,
            counts=template_counts,
            **common,
        )
        for template, previous in sorted(mechanism_probabilities.items()):
            mechanism_probabilities[template] = (
                engine._regularized_mechanism_probabilities(
                    previous=previous,
                    counts=mechanism_counts.get(template, {}),
                    **common,
                )
            )
        update_count += 1
    return {
        "template_probabilities": template_probabilities,
        "mechanism_probabilities": mechanism_probabilities,
        "update_count": update_count,
    }


def _suffix_adaptive_mutation_rows(
    candidates: pd.DataFrame,
    rejected: pd.DataFrame,
    prefix_boundary: int,
) -> dict[str, int]:
    candidate_suffix = candidates.loc[
        candidates["completion_ordinal"].astype(int) > int(prefix_boundary)
    ]
    adaptive_candidates = candidate_suffix.loc[
        candidate_suffix["arm"].astype(str).isin(ADAPTIVE_ARMS)
    ]
    suffix_checkpoint = int(prefix_boundary) // 2_000
    rejected_suffix = rejected.loc[
        rejected["checkpoint_index"].astype(int) >= suffix_checkpoint
    ]
    rejected_arms = rejected_suffix["policy_key"].astype(str).str.split("|").str[0]
    adaptive_rejected = rejected_suffix.loc[rejected_arms.isin(ADAPTIVE_ARMS)]
    return {
        "candidate_rows": len(adaptive_candidates),
        "rejected_rows": len(adaptive_rejected),
    }


def reconstruct_prefix_policy_state(
    artifact_root: Path,
    *,
    output_root: Path,
    prefix_boundary: int = PREFIX_BOUNDARY,
) -> dict[str, Any]:
    artifact_root = artifact_root.resolve()
    output_root = output_root.resolve()
    checkpoint_root = artifact_root / "checkpoints/checkpoint_017"
    manifest_path = checkpoint_root / "manifest.json"
    state_path = checkpoint_root / "state.json"
    candidate_path = artifact_root / "candidate_ledger.parquet"
    rejected_path = artifact_root / "rejected_candidate_ledger.parquet"
    frozen_path = artifact_root / "frozen_contract.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected_hashes = {
        str(row["name"]): str(row["sha256"])
        for row in manifest.get("files", ())
    }
    input_hashes = {
        "manifest.json": _file_sha(manifest_path),
        "state.json": _file_sha(state_path),
        "candidate_ledger.parquet": _file_sha(candidate_path),
        "rejected_candidate_ledger.parquet": _file_sha(rejected_path),
        "frozen_contract.json": _file_sha(frozen_path),
    }
    integrity_errors = [
        name
        for name in (
            "state.json",
            "candidate_ledger.parquet",
            "rejected_candidate_ledger.parquet",
        )
        if input_hashes[name] != expected_hashes.get(name)
    ]
    state = json.loads(state_path.read_text(encoding="utf-8"))
    frozen = json.loads(frozen_path.read_text(encoding="utf-8"))
    if str(frozen.get("source_sha")) != str(manifest.get("source_sha")):
        integrity_errors.append("frozen_contract_source_sha")
    if int(frozen.get("sealed_reads", -1)) != 0:
        integrity_errors.append("frozen_contract_sealed_reads")
    if _json_sha(state) != str(manifest["state_sha256"]):
        integrity_errors.append("state_sha256")
    if _json_sha(state["policies"]) != str(manifest["policy_state_sha256"]):
        integrity_errors.append("policy_state_sha256")

    columns = [
        "completion_ordinal",
        "checkpoint_index",
        "arm",
        "seed",
        "operation",
        "candidate_id",
        "behavior_family_id",
        "policy_local_family_count_at_completion",
        "search_reward",
        "candidate_spec_json",
        "block_robust_ordering_json",
    ]
    candidate_ledger = pd.read_parquet(candidate_path, columns=columns)
    rejected_ledger = pd.read_parquet(rejected_path)
    if len(candidate_ledger) != int(manifest["completed_ledger_row_count"]):
        integrity_errors.append("completed_ledger_row_count")
    prefix = candidate_ledger.loc[
        candidate_ledger["completion_ordinal"].astype(int) <= int(prefix_boundary)
    ].sort_values("completion_ordinal", kind="stable")
    prefix_counts = {
        str(key): int(value)
        for key, value in prefix.groupby("arm").size().sort_index().items()
    }
    if prefix_counts != {
        "temporal_program_cem": 5_000,
        "temporal_program_evolution": 12_000,
        "temporal_program_random": 13_000,
    }:
        integrity_errors.append("prefix_arm_counts")
    suffix_adaptive = _suffix_adaptive_mutation_rows(
        candidate_ledger, rejected_ledger, prefix_boundary
    )
    if any(suffix_adaptive.values()):
        integrity_errors.append("adaptive_policy_mutation_after_prefix")

    comparisons: dict[str, Any] = {}
    all_match = not integrity_errors
    adaptive_policy_bundle: dict[str, Any] = {}
    for policy_key, expected in sorted(state["policies"].items()):
        arm, seed_text = policy_key.rsplit("|", 1)
        if arm not in ADAPTIVE_ARMS:
            continue
        local = prefix.loc[
            (prefix["arm"].astype(str) == arm)
            & (prefix["seed"].astype(int) == int(seed_text))
        ]
        if arm == "temporal_program_evolution":
            reconstructed = _reconstruct_evolution_learning_state(
                local,
                parameters=dict(expected["parameters"]),
            )
            expected_learning = {
                key: expected[key]
                for key in (
                    "population",
                    "verified_parameter_mutations",
                    "verified_mechanism_mutations",
                    "verified_crossovers",
                )
            }
        else:
            reconstructed = _reconstruct_cem_learning_state(
                local,
                expected_policy=expected,
            )
            expected_learning = {
                key: expected[key]
                for key in (
                    "template_probabilities",
                    "mechanism_probabilities",
                    "update_count",
                )
            }
        matched = reconstructed == expected_learning
        comparisons[policy_key] = {
            "prefix_strict_rows": len(local),
            "learning_state_match": matched,
            "reconstructed_learning_state_sha256": _json_sha(reconstructed),
            "checkpoint_learning_state_sha256": _json_sha(expected_learning),
        }
        all_match = all_match and matched
        adaptive_policy_bundle[policy_key] = expected

    status = (
        "PREFIX_POLICY_STATE_RECONSTRUCTION_PASS"
        if all_match
        else "PREFIX_POLICY_STATE_RECONSTRUCTION_FAIL"
    )
    source_identity = _source_artifact_identity(
        checkpoint=str(manifest.get("checkpoint")),
        source_sha=str(manifest.get("source_sha")),
        input_hashes=input_hashes,
        prefix_boundary=int(prefix_boundary),
    )
    authority_identity = _authority_identity_from_frozen(frozen)
    output_root.mkdir(parents=True, exist_ok=True)
    bundle_payload = {
        "schema_version": 1,
        "status": status,
        "source_evidence_prefix": int(prefix_boundary),
        "source_artifact_identity_sha256": source_identity,
        "authority_identity": authority_identity,
        "policy_state_scope": "ADAPTIVE_CEM_AND_EVOLUTION_ONLY",
        "random_state_scope": "FRESH_RANDOM_CONTROL_AFTER_30K",
        "policies": adaptive_policy_bundle if all_match else {},
    }
    bundle_bytes = json.dumps(
        bundle_payload, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    bundle_path = output_root / "reconstructed_adaptive_policy_state_030000.json.gz"
    with bundle_path.open("wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as compressed:
            compressed.write(bundle_bytes)
    report = {
        "schema_version": 1,
        "status": status,
        "source_checkpoint": str(manifest.get("checkpoint")),
        "source_checkpoint_index": int(manifest.get("checkpoint_index", -1)),
        "source_producer_sha": str(manifest.get("source_sha")),
        "source_artifact_identity_sha256": source_identity,
        "authority_identity": authority_identity,
        "input_hashes": input_hashes,
        "integrity_errors": sorted(set(integrity_errors)),
        "valid_prefix_boundary": int(prefix_boundary),
        "invalid_suffix_start": int(prefix_boundary) + 1,
        "economic_prefix_valid": all_match,
        "orchestration_terminal_invalid": True,
        "prefix_arm_counts": prefix_counts,
        "suffix_adaptive_mutation_rows": suffix_adaptive,
        "policy_comparisons": comparisons,
        "checkpoint017_full_policy_state_sha256_verified": not any(
            value in integrity_errors
            for value in ("state_sha256", "policy_state_sha256")
        ),
        "reconstructed_policy_bundle": str(bundle_path),
        "reconstructed_policy_bundle_sha256": _file_sha(bundle_path),
        "policy_state_comparison_scope": (
            "CHECKPOINT017_FULL_HASH_VERIFIED_AND_PREFIX_LEARNING_SUBSTATE_EXACT"
        ),
        "fresh_random_control_identity": "FRESH_RANDOM_CONTROL_AFTER_30K",
        "market_arrays_read": 0,
        "candidate_reevaluations": 0,
        "sealed_reads": 0,
    }
    report_path = output_root / "prefix_policy_state_reconstruction_030000.json"
    report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return report


def successor_receipt_payload(
    *,
    reconstruction: Mapping[str, Any],
    reconstructed_policy_bundle_sha256: str,
    source_artifact_identity_sha256: str,
) -> dict[str, Any]:
    if reconstruction.get("status") != "PREFIX_POLICY_STATE_RECONSTRUCTION_PASS":
        raise RuntimeError("PREFIX_POLICY_STATE_RECONSTRUCTION_FAIL")
    if (
        int(reconstruction.get("valid_prefix_boundary", -1)) != PREFIX_BOUNDARY
        or int(reconstruction.get("sealed_reads", -1)) != 0
        or int(reconstruction.get("candidate_reevaluations", -1)) != 0
    ):
        raise RuntimeError("prefix reconstruction evidence contract changed")
    authority_identity = dict(reconstruction.get("authority_identity") or {})
    if set(authority_identity) != set(AUTHORITY_IDENTITY_KEYS):
        raise RuntimeError("prefix authority identity is incomplete")
    payload = {
        "schema_version": 1,
        "receipt_id": "CRYPTO_TEMPORAL_PROGRAM_30K_TO_50K_SUCCESSOR_V1",
        "status": "IMPLEMENTED_NOT_AUTHORIZED",
        "run_authorized": False,
        "source_evidence_prefix": PREFIX_BOUNDARY,
        "development_adaptive_policy_changed_after_observing_30k": True,
        "maximum_additional_strict": 20_000,
        "checkpoint_size": 5_000,
        "allocation": {
            "FRESH_RANDOM_CONTROL_AFTER_30K": 0.20,
            "temporal_program_evolution": 0.60,
            "temporal_program_cem": 0.20,
        },
        "allowed_checkpoint_decisions": [
            "CONTINUE",
            "PRUNE_ARM_AND_CONTINUE",
            "STOP_ECONOMIC_FUTILITY",
            "STOP_INVALID",
        ],
        "family_concentration_is_diagnostic_only": True,
        "reconstructed_policy_bundle_sha256": (
            reconstructed_policy_bundle_sha256
        ),
        "source_artifact_identity_sha256": source_artifact_identity_sha256,
        "authority_identity": authority_identity,
        "random_control_identity": "FRESH_RANDOM_CONTROL_AFTER_30K",
        "boundaries": {
            "train_only": True,
            "validation": False,
            "oos": False,
            "holdout": False,
            "forward": False,
            "promotion": False,
            "automatic_expansion": False,
            "market_run_started": False,
        },
        "unchanged_authorities": {
            "target": True,
            "execution": True,
            "portfolio_mapping": True,
            "cost": True,
            "evaluator": True,
            "grammar": True,
            "temporal_program_semantics": True,
        },
        "forbidden_additions": [
            "MCTS",
            "RL",
            "NOVELTY_QD",
            "NEW_OPTIMIZER",
            "NEW_GRAMMAR",
        ],
        "sealed_reads": 0,
    }
    return {**payload, "receipt_sha256": _json_sha(payload)}


def check_successor_preflight(
    *,
    reconstruction: Mapping[str, Any],
    receipt: Mapping[str, Any],
    bundle_path: Path,
    artifact_root: Path,
) -> dict[str, Any]:
    errors: list[str] = []
    artifact_root = artifact_root.resolve()
    if reconstruction.get("status") != "PREFIX_POLICY_STATE_RECONSTRUCTION_PASS":
        errors.append("prefix_reconstruction")
    if (
        int(reconstruction.get("valid_prefix_boundary", -1)) != PREFIX_BOUNDARY
        or int(reconstruction.get("invalid_suffix_start", -1)) != PREFIX_BOUNDARY + 1
        or reconstruction.get("economic_prefix_valid") is not True
        or reconstruction.get("orchestration_terminal_invalid") is not True
        or int(reconstruction.get("market_arrays_read", -1)) != 0
        or int(reconstruction.get("candidate_reevaluations", -1)) != 0
        or int(reconstruction.get("sealed_reads", -1)) != 0
    ):
        errors.append("prefix_identity")
    input_paths = {
        "manifest.json": artifact_root / "checkpoints/checkpoint_017/manifest.json",
        "state.json": artifact_root / "checkpoints/checkpoint_017/state.json",
        "candidate_ledger.parquet": artifact_root / "candidate_ledger.parquet",
        "rejected_candidate_ledger.parquet": (
            artifact_root / "rejected_candidate_ledger.parquet"
        ),
        "frozen_contract.json": artifact_root / "frozen_contract.json",
    }
    observed_input_hashes: dict[str, str] = {}
    for name, path in input_paths.items():
        if not path.is_file():
            errors.append("missing_source_artifact:" + name)
            continue
        observed_input_hashes[name] = _file_sha(path)
    if observed_input_hashes != dict(reconstruction.get("input_hashes") or {}):
        errors.append("source_artifact_input_hashes")
    frozen: dict[str, Any] = {}
    if input_paths["frozen_contract.json"].is_file():
        frozen = json.loads(
            input_paths["frozen_contract.json"].read_text(encoding="utf-8")
        )
    observed_authority_identity = (
        _authority_identity_from_frozen(frozen) if frozen else {}
    )
    if observed_authority_identity != dict(
        reconstruction.get("authority_identity") or {}
    ):
        errors.append("reconstruction_authority_identity")
    if observed_authority_identity != dict(receipt.get("authority_identity") or {}):
        errors.append("receipt_authority_identity")
    observed_source_identity = _source_artifact_identity(
        checkpoint=str(reconstruction.get("source_checkpoint")),
        source_sha=str(reconstruction.get("source_producer_sha")),
        input_hashes=observed_input_hashes,
        prefix_boundary=PREFIX_BOUNDARY,
    )
    if observed_source_identity != reconstruction.get(
        "source_artifact_identity_sha256"
    ):
        errors.append("source_artifact_identity_sha256")
    if receipt.get("receipt_sha256") != _json_sha(
        {key: value for key, value in receipt.items() if key != "receipt_sha256"}
    ):
        errors.append("receipt_sha256")
    if (
        receipt.get("status") != "IMPLEMENTED_NOT_AUTHORIZED"
        or receipt.get("run_authorized") is not False
    ):
        errors.append("implementation_only_authorization")
    expected_allocation = {
        "FRESH_RANDOM_CONTROL_AFTER_30K": 0.20,
        "temporal_program_evolution": 0.60,
        "temporal_program_cem": 0.20,
    }
    if dict(receipt.get("allocation") or {}) != expected_allocation:
        errors.append("allocation")
    if (
        int(receipt.get("source_evidence_prefix", -1)) != PREFIX_BOUNDARY
        or receipt.get(
            "development_adaptive_policy_changed_after_observing_30k"
        )
        is not True
        or int(receipt.get("maximum_additional_strict", -1)) != 20_000
        or int(receipt.get("checkpoint_size", -1)) != 5_000
        or receipt.get("family_concentration_is_diagnostic_only") is not True
        or receipt.get("random_control_identity")
        != "FRESH_RANDOM_CONTROL_AFTER_30K"
    ):
        errors.append("successor_search_contract")
    if receipt.get("allowed_checkpoint_decisions") != [
        "CONTINUE",
        "PRUNE_ARM_AND_CONTINUE",
        "STOP_ECONOMIC_FUTILITY",
        "STOP_INVALID",
    ]:
        errors.append("checkpoint_decisions")
    boundaries = dict(receipt.get("boundaries") or {})
    expected_boundaries = {
        "train_only": True,
        "validation": False,
        "oos": False,
        "holdout": False,
        "forward": False,
        "promotion": False,
        "automatic_expansion": False,
        "market_run_started": False,
    }
    if boundaries != expected_boundaries:
        errors.append("boundaries")
    unchanged = dict(receipt.get("unchanged_authorities") or {})
    if set(unchanged) != {
        "target",
        "execution",
        "portfolio_mapping",
        "cost",
        "evaluator",
        "grammar",
        "temporal_program_semantics",
    } or not all(value is True for value in unchanged.values()):
        errors.append("unchanged_authorities")
    if _file_sha(bundle_path) != receipt.get("reconstructed_policy_bundle_sha256"):
        errors.append("reconstructed_policy_bundle_sha256")
    if receipt.get("source_artifact_identity_sha256") != reconstruction.get(
        "source_artifact_identity_sha256"
    ):
        errors.append("source_artifact_identity_sha256")
    if int(receipt.get("sealed_reads", -1)) != 0:
        errors.append("sealed_reads")
    try:
        with gzip.open(bundle_path, "rt", encoding="utf-8") as handle:
            bundle = json.load(handle)
    except (OSError, json.JSONDecodeError):
        bundle = {}
        errors.append("reconstructed_policy_bundle")
    if bundle and (
        bundle.get("status") != "PREFIX_POLICY_STATE_RECONSTRUCTION_PASS"
        or int(bundle.get("source_evidence_prefix", -1)) != PREFIX_BOUNDARY
        or bundle.get("source_artifact_identity_sha256")
        != reconstruction.get("source_artifact_identity_sha256")
        or bundle.get("random_state_scope") != "FRESH_RANDOM_CONTROL_AFTER_30K"
    ):
        errors.append("reconstructed_policy_bundle_identity")
    return {
        "schema_version": 1,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "source_evidence_prefix": receipt.get("source_evidence_prefix"),
        "fresh_random_control_identity": receipt.get("random_control_identity"),
        "target_mapping_cost_evaluator_unchanged": (
            "unchanged_authorities" not in errors
            and "receipt_authority_identity" not in errors
        ),
        "market_run_started": False,
        "sealed_reads": 0,
    }
