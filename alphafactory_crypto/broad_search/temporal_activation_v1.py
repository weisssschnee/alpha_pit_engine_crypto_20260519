"""Paired development gate for the existing canonical temporal primitives.

This module is deliberately an experiment adapter, not another search engine.
It reuses the current mechanism catalog, CandidateSpec compiler, pair evaluator,
mapping, cost, target, block-robust projection, and worker initialization.
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
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd
import psutil

from alphafactory_crypto.instrument_canary.grammar import (
    PRIMITIVE_PARAMETER_OPTIONS,
)

from .audit import turnover_path
from .compositional18m import (
    CandidateSpec,
    MechanismSpec,
    compile_mechanism_catalog,
    mechanism_role_domains,
    sample_mechanism_candidate,
    temporal_mechanism_candidate_from_genes,
)
from .experiment_authority import resolve_search_economic_receipt
from .expression import (
    CANONICAL_PRIMITIVE_OPERATOR,
    CanonicalTemporalPrimitiveAdapterV1,
    Expression,
    FieldContract,
    TypedExpressionRegistry,
)
from .pair18m import ControlBehaviorDegeneracyError, evaluate_pair
from . import search_engine_v1 as engine


CONFIG_PATH = "config/crypto_search_temporal_activation_v1.json"
BINDING_RECEIPT_PATH = "config/crypto_search_temporal_activation_v1_receipt.json"
ECONOMIC_RECEIPT_PATH = (
    "config/crypto_search_replication_aware_gate_v1_r3_receipt.json"
)
CATALOG_PATH = "config/crypto_typed_mechanism_catalog_v2_1.json"
BLOCK_CONFIG_PATH = "config/crypto_search_replication_aware_gate_v1.json"
CAMPAIGN = "crypto_search_temporal_activation_v1"
BLOCK_ROLE = "FRESH_DEVELOPMENT_TEMPORAL_PAIRED_ATTRIBUTION_ONLY"
ALLOWED_PRIMITIVES = (
    "Delta",
    "Acceleration",
    "Persistence",
    "Transition",
    "EventWindow",
    "MultiScaleRelation",
)
_ALLOCATION_CACHE: dict[
    tuple[str, tuple[str, ...]],
    tuple[
        tuple[
            str,
            str,
            MechanismSpec,
            str,
            tuple[int | None, int | None, float | None],
        ],
        ...,
    ],
] = {}
COMPONENT_PATHS = (
    "alphafactory_crypto/instrument_capability/primitives.py",
    "alphafactory_crypto/instrument_canary/grammar.py",
    "alphafactory_crypto/broad_search/expression.py",
    "alphafactory_crypto/broad_search/compositional18m.py",
    "alphafactory_crypto/broad_search/pair18m.py",
    "alphafactory_crypto/broad_search/temporal_activation_v1.py",
    "scripts/run_crypto_search_temporal_activation_v1_pc2.ps1",
    CONFIG_PATH,
    CATALOG_PATH,
    BLOCK_CONFIG_PATH,
)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest().upper()


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


def _seed(*parts: Any) -> int:
    return int.from_bytes(
        hashlib.sha256("|".join(map(str, parts)).encode("utf-8")).digest()[:8],
        "big",
        signed=False,
    )


def _operator_nodes(expression: Expression, operator: str) -> tuple[Expression, ...]:
    rows = (expression,) if expression.operator == operator else ()
    return rows + tuple(
        node
        for child in expression.inputs
        for node in _operator_nodes(child, operator)
    )


def _validate_config(config: Mapping[str, Any]) -> None:
    budget = dict(config.get("search_budget") or {})
    families = tuple(dict(value) for value in config.get("temporal_families") or ())
    authorities = dict(config.get("source_authorities") or {})
    if config.get("experiment_id") != (
        "CRYPTO_SEARCH_CORE_V3_CANONICAL_TEMPORAL_PRIMITIVE_ACTIVATION"
    ):
        raise ValueError("temporal experiment identity changed")
    if (
        int(budget.get("strict_evaluated_maximum", -1)) != 8_192
        or int(budget.get("pair_maximum", -1)) != 4_096
        or int(budget.get("strict_evaluated_per_tranche", -1)) != 2_048
        or int(budget.get("pair_per_tranche", -1)) != 1_024
        or int(budget.get("tranche_count_maximum", -1)) != 4
        or int(budget.get("checkpoint_count_maximum", -1)) != 4
        or int(budget.get("workers_default", -1)) != 10
        or int(budget.get("workers_memory_fallback", -1)) != 8
        or budget.get("workers_12_forbidden") is not True
        or budget.get("automatic_expansion") is not False
        or budget.get("sequential_gate_release_only") is not True
        or budget.get("later_tranche_proposal_pregeneration") is not False
    ):
        raise ValueError("temporal sequential maximum budget changed")
    if len(families) != 4 or any(
        int(value.get("pair_quota_per_tranche", -1)) != 256
        for value in families
    ):
        raise ValueError("temporal family quota changed")
    observed = {
        str(primitive)
        for family in families
        for primitive in family.get("primitive_ids") or ()
    }
    adapter = dict(config.get("temporal_adapter") or {})
    if observed != set(ALLOWED_PRIMITIVES) or tuple(
        adapter.get("allowed_primitive_ids") or ()
    ) != ALLOWED_PRIMITIVES:
        raise ValueError("temporal primitive scope changed")
    if int(config["market_contract"]["execution_delay_hours"]) != 2:
        raise ValueError("Binance delayed-open execution contract changed")
    if int(config["market_contract"]["horizon_hours"]) != 4:
        raise ValueError("temporal gate requires the frozen 4h horizon")
    if (
        authorities.get("economic_receipt_path") != ECONOMIC_RECEIPT_PATH
        or authorities.get("catalog_path") != CATALOG_PATH
        or config["market_contract"].get("development_blocks_config")
        != BLOCK_CONFIG_PATH
    ):
        raise ValueError("temporal source authority binding changed")
    boundaries = dict(config.get("boundaries") or {})
    forbidden = (
        "new_fields",
        "new_data_source",
        "target_change",
        "horizon_change",
        "mapping_change",
        "cost_change",
        "reward_change",
        "new_ast",
        "new_compiler",
        "new_evaluator",
        "evaluator_formula_change",
        "new_behavior_archive_identity",
        "optimizer_feedback",
        "archive_feedback",
        "validation",
        "oos",
        "holdout",
        "challenge",
        "recent",
        "may_stress",
        "forward",
        "promotion",
        "cross_sprint_adaptive_memory",
        "rescue_rerun",
        "parameter_tuning",
        "new_graph_node",
    )
    if boundaries.get("development_only") is not True or any(
        boundaries.get(key) is not False for key in forbidden
    ):
        raise ValueError("temporal research boundary changed")


def _validate_binding_receipt(
    repo_root: Path,
    *,
    config: Mapping[str, Any],
    require_authorized: bool,
) -> dict[str, Any]:
    path = repo_root / BINDING_RECEIPT_PATH
    receipt = engine._read_json(path)
    required = {
        "schema_version",
        "receipt_id",
        "status",
        "run_authorized",
        "authorization",
        "authorized_implementation_sha",
        "expected_branch",
        "component_sha256",
        "input_identities",
        "allowed_primitive_ids",
        "allowed_placements",
        "budget",
        "boundaries",
    }
    if set(receipt) - (required | {"run_outcome"}) or not required.issubset(receipt):
        raise RuntimeError("TEMPORAL_BINDING_RECEIPT_SCHEMA_CHANGED")
    if receipt["receipt_id"] != "CRYPTO_TEMPORAL_ACTIVATION_V1_RECEIPT":
        raise RuntimeError("TEMPORAL_BINDING_RECEIPT_ID_CHANGED")
    if require_authorized and (
        receipt["status"] != "RUN_AUTHORIZED_DEVELOPMENT_ONLY"
        or receipt["run_authorized"] is not True
    ):
        raise RuntimeError("TEMPORAL_BINDING_RECEIPT_ALREADY_CONSUMED")
    if tuple(receipt["allowed_primitive_ids"]) != ALLOWED_PRIMITIVES:
        raise RuntimeError("TEMPORAL_BINDING_PRIMITIVE_SCOPE_CHANGED")
    if tuple(receipt["allowed_placements"]) != (
        "PRE_NORMALIZER",
        "POST_NORMALIZER",
        "POST_TYPED_BUNDLE_PRE_OUTER",
    ):
        raise RuntimeError("TEMPORAL_BINDING_PLACEMENT_SCOPE_CHANGED")
    branch = subprocess.check_output(
        ["git", "branch", "--show-current"], cwd=repo_root, text=True
    ).strip()
    if branch != receipt["expected_branch"]:
        raise RuntimeError("TEMPORAL_BINDING_BRANCH_CHANGED")
    if subprocess.run(
        [
            "git",
            "merge-base",
            "--is-ancestor",
            str(receipt["authorized_implementation_sha"]),
            "HEAD",
        ],
        cwd=repo_root,
        check=False,
    ).returncode != 0:
        raise RuntimeError("TEMPORAL_BINDING_IMPLEMENTATION_SHA_NOT_ANCESTOR")
    if dict(receipt["budget"]) != dict(config["search_budget"]):
        raise RuntimeError("TEMPORAL_BINDING_BUDGET_CHANGED")
    expected_components = {
        value: _sha256_file(repo_root / value) for value in COMPONENT_PATHS
    }
    if dict(receipt["component_sha256"]) != expected_components:
        raise RuntimeError("TEMPORAL_BINDING_COMPONENT_HASH_CHANGED")
    inputs = dict(receipt["input_identities"])
    manifest_path = repo_root / str(
        config["source_authorities"]["source_carrier_manifest"]
    )
    if inputs != {
        "carrier_manifest_path": manifest_path.relative_to(repo_root).as_posix(),
        "carrier_manifest_sha256": _sha256_file(manifest_path),
        "economic_receipt_path": ECONOMIC_RECEIPT_PATH,
        "economic_receipt_sha256": _sha256_file(
            repo_root / ECONOMIC_RECEIPT_PATH
        ),
        "target_authority_path": str(
            config["source_authorities"]["target_authority_config"]
        ),
        "target_authority_sha256": _sha256_file(
            repo_root
            / str(config["source_authorities"]["target_authority_config"])
        ),
    }:
        raise RuntimeError("TEMPORAL_BINDING_INPUT_IDENTITY_CHANGED")
    return {**receipt, "receipt_sha256": _json_sha(receipt)}


def binding_receipt_payload(repo_root: Path) -> dict[str, Any]:
    """Build the one-time receipt body after implementation bytes are final."""

    config = engine._read_json(repo_root / CONFIG_PATH)
    _validate_config(config)
    manifest_path = repo_root / str(
        config["source_authorities"]["source_carrier_manifest"]
    )
    return {
        "schema_version": 1,
        "receipt_id": "CRYPTO_TEMPORAL_ACTIVATION_V1_RECEIPT",
        "status": "RUN_AUTHORIZED_DEVELOPMENT_ONLY",
        "run_authorized": True,
        "authorization": {
            "authority": "CURRENT_USER_INSTRUCTION",
            "scope": "SEQUENTIAL_MAX8192_STRICT_PAIRED_DEVELOPMENT_GATE",
            "adaptive_optimizer": False,
            "automatic_expansion": False,
            "sequential_gate_release_only": True,
            "later_tranche_proposal_pregeneration": False,
        },
        "component_sha256": {
            value: _sha256_file(repo_root / value) for value in COMPONENT_PATHS
        },
        "input_identities": {
            "carrier_manifest_path": manifest_path.relative_to(repo_root).as_posix(),
            "carrier_manifest_sha256": _sha256_file(manifest_path),
            "economic_receipt_path": ECONOMIC_RECEIPT_PATH,
            "economic_receipt_sha256": _sha256_file(
                repo_root / ECONOMIC_RECEIPT_PATH
            ),
            "target_authority_path": str(
                config["source_authorities"]["target_authority_config"]
            ),
            "target_authority_sha256": _sha256_file(
                repo_root
                / str(config["source_authorities"]["target_authority_config"])
            ),
        },
        "allowed_primitive_ids": list(ALLOWED_PRIMITIVES),
        "allowed_placements": [
            "PRE_NORMALIZER",
            "POST_NORMALIZER",
            "POST_TYPED_BUNDLE_PRE_OUTER",
        ],
        "authorized_implementation_sha": engine._git_sha(repo_root),
        "expected_branch": "experiment/crypto-search-evidence-v1-1-20260805",
        "budget": dict(config["search_budget"]),
        "boundaries": dict(config["boundaries"]),
    }


def _candidate_replay_verified(
    registry: TypedExpressionRegistry,
    candidate: CandidateSpec,
    domains: Mapping[str, Sequence[Any]],
) -> bool:
    restored = CandidateSpec.from_dict(candidate.to_dict())
    if "temporal_transform" in candidate.generation_genes:
        rebuilt = temporal_mechanism_candidate_from_genes(
            registry,
            genes=candidate.generation_genes,
            domains=domains,
        )
    else:
        rebuilt = engine.mechanism_candidate_from_genes(
            registry,
            genes=candidate.generation_genes,
            domains=domains,
        )
    return all(
        (
            restored.to_dict() == candidate.to_dict(),
            rebuilt.candidate_id == candidate.candidate_id,
            rebuilt.expression.expression_id == candidate.expression.expression_id,
            rebuilt.control.expression_id == candidate.control.expression_id,
        )
    )


def _pair_identity(
    *,
    family_id: str,
    slot: int,
    attempt: int,
    static: CandidateSpec,
    temporal: CandidateSpec,
) -> dict[str, Any]:
    transform = dict(temporal.generation_genes["temporal_transform"])
    shared = {
        "family_id": family_id,
        "slot": int(slot),
        "raw_fields": list(static.raw_fields),
        "mechanism_spec": static.generation_genes["mechanism_spec"],
        "left_window": static.generation_genes["left_window"],
        "right_window": static.generation_genes["right_window"],
        "left_normalizer": static.generation_genes["left_normalizer"],
        "right_normalizer": static.generation_genes["right_normalizer"],
        "beta": static.generation_genes["beta"],
        "mapping_id": static.mapping_id,
        "horizon_hours": static.horizon_hours,
        "matched_control_schema": static.generation_genes[
            "matched_control_schema"
        ],
    }
    shared_hash = _json_sha(shared)
    delta_hash = _json_sha(transform)
    pair_id = _json_sha(
        {
            "shared_base_identity_sha256": shared_hash,
            "temporal_delta_identity_sha256": delta_hash,
            "attempt": int(attempt),
        }
    )
    return {
        "paired_proposal_id": pair_id,
        "static_candidate_id": static.candidate_id,
        "temporal_candidate_id": temporal.candidate_id,
        "shared_base_identity_sha256": shared_hash,
        "temporal_delta_identity_sha256": delta_hash,
        "temporal_family_id": family_id,
        "allocation_slot": int(slot),
        "generation_attempt_within_slot": int(attempt),
        "primitive_id": transform["primitive_id"],
        "temporal_axis": transform["axis"],
        "temporal_window": transform["window"],
        "temporal_long_window": transform["long_window"],
        "temporal_threshold": transform["threshold"],
        "temporal_placement": transform["placement"],
        "outer_template": static.generation_genes["mechanism_spec"][
            "template_id"
        ],
        "temporal_role": (
            static.generation_genes["mechanism_spec"]["left_role"]
            if transform["axis"] == "left"
            else static.generation_genes["mechanism_spec"]["right_role"]
        ),
        "temporal_field_family": (
            static.generation_genes["mechanism_spec"]["left_role"]
            if transform["axis"] == "left"
            else static.generation_genes["mechanism_spec"]["right_role"]
        ),
        "raw_fields_json": json.dumps(list(static.raw_fields)),
        "static_candidate_spec_json": json.dumps(
            static.to_dict(), sort_keys=True, separators=(",", ":")
        ),
        "temporal_candidate_spec_json": json.dumps(
            temporal.to_dict(), sort_keys=True, separators=(",", ":")
        ),
    }


def _family_routes(
    *,
    family: Mapping[str, Any],
    specs: Sequence[MechanismSpec],
) -> dict[tuple[str, str], tuple[tuple[MechanismSpec, str], ...]]:
    roles = set(str(value) for value in family["eligible_temporal_roles"])
    templates = tuple(str(value) for value in family["eligible_outer_templates"])
    routes: dict[tuple[str, str], list[tuple[MechanismSpec, str]]] = defaultdict(list)
    for primitive in map(str, family["primitive_ids"]):
        for template in templates:
            for spec in specs:
                if spec.template_id != template:
                    continue
                for axis, role in (("left", spec.left_role), ("right", spec.right_role)):
                    if role not in roles:
                        continue
                    routes[(primitive, template)].append((spec, axis))
    missing = [
        (primitive, template)
        for primitive in map(str, family["primitive_ids"])
        for template in templates
        if not routes[(primitive, template)]
    ]
    if missing:
        raise ValueError(f"temporal family has an empty typed route: {missing}")
    return {
        key: tuple(sorted(values, key=lambda value: (value[0].mechanism_id, value[1])))
        for key, values in routes.items()
    }


def propose_pair(
    *,
    config: Mapping[str, Any],
    family: Mapping[str, Any],
    registry: TypedExpressionRegistry,
    specs: Sequence[MechanismSpec],
    domains: Mapping[str, Sequence[Any]],
    slot: int,
    attempt: int,
) -> dict[str, Any]:
    family_id = str(family["family_id"])
    primitive, template, spec, axis, parameters = _allocation_coordinate(
        family=family,
        specs=specs,
        slot=slot,
    )
    window, long_window, threshold = parameters
    local_rng = random.Random(
        _seed(
            config["paired_proposal_contract"]["rng_seed"],
            family_id,
            slot,
            attempt,
        )
    )
    static = sample_mechanism_candidate(
        registry=registry,
        spec=spec,
        domains=domains,
        rng=local_rng,
    )
    role = spec.left_role if axis == "left" else spec.right_role
    numeric = primitive in {"Delta", "Acceleration", "MultiScaleRelation"}
    placement = (
        "POST_TYPED_BUNDLE_PRE_OUTER"
        if role in {"BASIS_BUNDLE", "CROSS_VENUE_OI_BUNDLE"}
        else "PRE_NORMALIZER"
        if numeric
        else "POST_NORMALIZER"
    )
    temporal = temporal_mechanism_candidate_from_genes(
        registry,
        genes={
            **static.generation_genes,
            "temporal_transform": {
                "temporal_family_id": family_id,
                "primitive_id": primitive,
                "axis": axis,
                "window": window,
                "long_window": long_window,
                "threshold": threshold,
                "placement": placement,
            },
        },
        domains=domains,
    )
    if (
        static.raw_fields != temporal.raw_fields
        or static.mapping_id != temporal.mapping_id
        or static.horizon_hours != temporal.horizon_hours
        or static.generation_genes["mechanism_spec"]
        != temporal.generation_genes["mechanism_spec"]
    ):
        raise AssertionError("paired proposal changed a shared economic coordinate")
    expression_nodes = _operator_nodes(
        temporal.expression, CANONICAL_PRIMITIVE_OPERATOR
    )
    control_nodes = _operator_nodes(
        temporal.control, CANONICAL_PRIMITIVE_OPERATOR
    )
    if (
        len(expression_nodes) != 1
        or len(control_nodes) != 1
        or expression_nodes[0].parameters != control_nodes[0].parameters
    ):
        raise AssertionError("matched control did not preserve temporal transform")
    if not _candidate_replay_verified(registry, static, domains) or not (
        _candidate_replay_verified(registry, temporal, domains)
    ):
        raise AssertionError("paired candidate replay identity changed")
    identity = _pair_identity(
        family_id=family_id,
        slot=slot,
        attempt=attempt,
        static=static,
        temporal=temporal,
    )
    temporal_with_lineage = temporal_mechanism_candidate_from_genes(
        registry,
        genes={
            **temporal.generation_genes,
            "paired_lineage": {
                "paired_static_candidate_id": static.candidate_id,
                "paired_proposal_id": identity["paired_proposal_id"],
                "proposal_ordinal": int(slot),
            },
        },
        domains=domains,
    )
    if (
        temporal_with_lineage.candidate_id != temporal.candidate_id
        or temporal_with_lineage.expression.expression_id
        != temporal.expression.expression_id
    ):
        raise AssertionError("paired lineage changed temporal economic identity")
    temporal = temporal_with_lineage
    identity = _pair_identity(
        family_id=family_id,
        slot=slot,
        attempt=attempt,
        static=static,
        temporal=temporal,
    )
    return {**identity, "static": static, "temporal": temporal}


def _allocation_coordinate(
    *,
    family: Mapping[str, Any],
    specs: Sequence[MechanismSpec],
    slot: int,
) -> tuple[str, str, MechanismSpec, str, tuple[int | None, int | None, float | None]]:
    """Return the pre-frozen primitive/template/role/parameter allocation."""

    slot = int(slot)
    if not 0 <= slot < 1_024:
        raise ValueError("temporal family allocation slot is outside frozen maximum")
    cache_key = (
        _json_sha(dict(family)),
        tuple(value.mechanism_id for value in specs),
    )
    if cache_key not in _ALLOCATION_CACHE:
        primitives = tuple(str(value) for value in family["primitive_ids"])
        templates = tuple(str(value) for value in family["eligible_outer_templates"])
        roles = tuple(str(value) for value in family["eligible_temporal_roles"])
        routes = _family_routes(family=family, specs=specs)
        groups: dict[
            tuple[str, str, str], list[tuple[MechanismSpec, str]]
        ] = defaultdict(list)
        for primitive in primitives:
            for template in templates:
                for spec, axis in routes[(primitive, template)]:
                    role = spec.left_role if axis == "left" else spec.right_role
                    if role in roles:
                        groups[(primitive, template, role)].append((spec, axis))
        missing_roles = sorted(set(roles) - {key[2] for key in groups})
        if missing_roles:
            raise ValueError(
                "temporal family has no compatible route for roles: "
                + ",".join(missing_roles)
            )
        primitive_count: Counter[str] = Counter()
        template_count: Counter[str] = Counter()
        role_count: Counter[str] = Counter()
        group_count: Counter[tuple[str, str, str]] = Counter()
        schedule: list[
            tuple[
                str,
                str,
                MechanismSpec,
                str,
                tuple[int | None, int | None, float | None],
            ]
        ] = []
        for allocation_slot in range(1_024):
            if allocation_slot % 256 == 0:
                primitive_count = Counter()
                template_count = Counter()
                role_count = Counter()
                group_count = Counter()
            key = min(
                groups,
                key=lambda value: (
                    primitive_count[value[0]] * len(primitives),
                    template_count[value[1]] * len(templates),
                    role_count[value[2]] * len(roles),
                    group_count[value] * len(groups),
                    _seed(family["family_id"], allocation_slot, *value),
                ),
            )
            primitive, template, _ = key
            compatible = tuple(
                sorted(
                    groups[key], key=lambda value: (value[0].mechanism_id, value[1])
                )
            )
            spec, axis = compatible[group_count[key] % len(compatible)]
            parameters = tuple(PRIMITIVE_PARAMETER_OPTIONS[primitive])
            parameter = parameters[primitive_count[primitive] % len(parameters)]
            schedule.append((primitive, template, spec, axis, parameter))
            primitive_count[primitive] += 1
            template_count[template] += 1
            role_count[key[2]] += 1
            group_count[key] += 1
        _ALLOCATION_CACHE[cache_key] = tuple(schedule)
    return _ALLOCATION_CACHE[cache_key][slot]


def _common_sleeve_summary(
    static: Mapping[str, Any],
    temporal: Mapping[str, Any],
    *,
    cost_bps: float,
    horizon: int,
) -> dict[str, Any]:
    static_mask = np.asarray(static["mask"], dtype=bool)
    temporal_mask = np.asarray(temporal["mask"], dtype=bool)
    common = static_mask & temporal_mask

    def summary(sleeve: Mapping[str, Any]) -> dict[str, Any]:
        weights = np.nan_to_num(
            np.asarray(sleeve["weights"], dtype=float), nan=0.0
        )
        weights = np.where(common[np.newaxis, :], weights, 0.0)
        turnover, _ = turnover_path(weights, horizon)
        gross = np.where(
            common,
            np.nan_to_num(np.asarray(sleeve["gross"], dtype=float), nan=0.0),
            0.0,
        )
        cost = turnover * float(cost_bps) / 10_000.0
        net = gross - cost
        objective = common | (turnover > 1.0e-12)
        return {
            "support_coordinates": int(common.sum()),
            "objective_coordinates": int(objective.sum()),
            "support_rate": float(np.mean(common)),
            "gross_mean": float(np.mean(gross[objective])) if np.any(objective) else None,
            "cost_mean": float(np.mean(cost[objective])) if np.any(objective) else None,
            "net_mean": float(np.mean(net[objective])) if np.any(objective) else None,
            "turnover_mean": (
                float(np.mean(turnover[objective])) if np.any(objective) else None
            ),
        }

    return {"static": summary(static), "temporal": summary(temporal)}


def _paired_common_support(
    static_paths: Mapping[str, Any],
    temporal_paths: Mapping[str, Any],
    *,
    cost_bps: float,
    horizon: int,
) -> dict[str, Any]:
    rows = {}
    for axis, sleeve_name in (
        ("left", "primary_minus_left_control"),
        ("right", "primary_minus_right_control"),
    ):
        rows[axis] = _common_sleeve_summary(
            static_paths["sleeves"][sleeve_name],
            temporal_paths["sleeves"][sleeve_name],
            cost_bps=cost_bps,
            horizon=horizon,
        )
    static_worst = min(
        float(rows[axis]["static"]["net_mean"]) for axis in ("left", "right")
    )
    temporal_worst = min(
        float(rows[axis]["temporal"]["net_mean"]) for axis in ("left", "right")
    )
    return {
        "axis": rows,
        "static_worst_axis_net_mean": static_worst,
        "temporal_worst_axis_net_mean": temporal_worst,
        "paired_worst_axis_net_delta": temporal_worst - static_worst,
    }


def _worker_pair(payload: Mapping[str, Any]) -> dict[str, Any]:
    pair_id = str(payload["paired_proposal_id"])
    engine._write_worker_process_evidence(
        evidence_root=engine._WORKER_PROCESS_EVIDENCE_ROOT,
        channel="task",
        stage="TASK_STARTED",
        candidate_id=pair_id,
    )
    cpu_started = time.process_time()
    wall_started = time.perf_counter()
    process = psutil.Process(os.getpid())
    try:
        if engine._WORKER_STORE is None or engine._WORKER_REGISTRY is None:
            raise RuntimeError("temporal pair worker was not initialized")
        candidates = {
            "static": CandidateSpec.from_dict(payload["static"]),
            "temporal": CandidateSpec.from_dict(payload["temporal"]),
        }
        evaluations: dict[str, dict[str, Any]] = {}
        paths: dict[str, dict[str, Any]] = {}
        for name, candidate in candidates.items():
            evaluation = evaluate_pair(
                store=engine._WORKER_STORE,
                registry=engine._WORKER_REGISTRY,
                candidate=candidate,
                block_start=engine._WORKER_BLOCK_START,
                block_end=engine._WORKER_BLOCK_END,
                block_role=engine._WORKER_BLOCK_ROLE,
                behavior_contract=None,
                economic_receipt=engine._WORKER_ECONOMIC_RECEIPT,
                optimizer_block_contract=engine._WORKER_OPTIMIZER_BLOCK_CONTRACT,
                include_paired_diagnostic_paths=True,
            )
            paths[name] = dict(evaluation.pop("_paired_diagnostic_paths"))
            evaluations[name] = evaluation
        common = _paired_common_support(
            paths["static"],
            paths["temporal"],
            cost_bps=float(evaluations["static"]["cost_bps"]),
            horizon=int(candidates["static"].horizon_hours),
        )
        result = {
            "status": "PAIR_EVALUATED",
            "paired_proposal_id": pair_id,
            "static": evaluations["static"],
            "temporal": evaluations["temporal"],
            "common_support": common,
            "error": None,
        }
    except ControlBehaviorDegeneracyError as failure:
        result = {
            "status": "PAIR_REJECTED",
            "paired_proposal_id": pair_id,
            "static": None,
            "temporal": None,
            "common_support": None,
            "error": type(failure).__name__ + ":" + str(failure),
        }
    except MemoryError as failure:
        result = {
            "status": "MEMORY_ERROR",
            "paired_proposal_id": pair_id,
            "static": None,
            "temporal": None,
            "common_support": None,
            "error": type(failure).__name__ + ":" + str(failure),
        }
    except (ValueError, FloatingPointError) as failure:
        result = {
            "status": "PAIR_REJECTED",
            "paired_proposal_id": pair_id,
            "static": None,
            "temporal": None,
            "common_support": None,
            "error": type(failure).__name__ + ":" + str(failure),
        }
    memory = process.memory_info()
    result.update(
        {
            "process_cpu_seconds": time.process_time() - cpu_started,
            "wall_seconds": time.perf_counter() - wall_started,
            "worker_rss_bytes": int(memory.rss),
            "worker_private_bytes": int(getattr(memory, "private", memory.rss)),
        }
    )
    engine._write_worker_process_evidence(
        evidence_root=engine._WORKER_PROCESS_EVIDENCE_ROOT,
        channel="task",
        stage="TASK_COMPLETED",
        candidate_id=pair_id,
        outcome=str(result["status"]),
    )
    return result


def _source_smoke_worker(evidence_root: str) -> dict[str, Any]:
    root = Path(evidence_root)
    engine._write_worker_process_evidence(
        evidence_root=root,
        channel="task",
        stage="TASK_STARTED",
        candidate_id="NO_MARKET_TEMPORAL_SOURCE_SMOKE",
    )
    engine._write_worker_process_evidence(
        evidence_root=root,
        channel="task",
        stage="TASK_COMPLETED",
        candidate_id="NO_MARKET_TEMPORAL_SOURCE_SMOKE",
        outcome="PASS",
    )
    return {"status": "PASS", "pid": os.getpid()}


def source_smoke(repo_root: Path, *, evidence_root: Path) -> dict[str, Any]:
    """Compile all frozen temporal families without loading market arrays."""

    repo_root = repo_root.resolve()
    config = engine._read_json(repo_root / CONFIG_PATH)
    _validate_config(config)
    manifest = engine._read_json(
        repo_root
        / str(config["source_authorities"]["source_carrier_manifest"])
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
        raise RuntimeError("source smoke carrier contract count changed")
    registry = TypedExpressionRegistry(contracts)
    domains = {**mechanism_role_domains(contracts), "__HORIZONS__": (4,)}
    specs = tuple(
        value
        for value in compile_mechanism_catalog(
            engine._read_json(repo_root / CATALOG_PATH)
        )
        if value.generation == 1
        and value.matched_control_schema == "DUAL_AXIS_A_B_AB"
    )
    pairs = [
        propose_pair(
            config=config,
            family=family,
            registry=registry,
            specs=specs,
            domains=domains,
            slot=0,
            attempt=0,
        )
        for family in config["temporal_families"]
    ]
    for family in config["temporal_families"]:
        allocations = [
            _allocation_coordinate(family=family, specs=specs, slot=slot)
            for slot in range(256)
        ]
        observed_roles = {
            spec.left_role if axis == "left" else spec.right_role
            for _, _, spec, axis, _ in allocations
        }
        if observed_roles != set(family["eligible_temporal_roles"]):
            raise RuntimeError("source smoke found a silently omitted typed role")
    evidence_root = evidence_root.resolve()
    evidence_root.mkdir(parents=True, exist_ok=False)
    with concurrent.futures.ProcessPoolExecutor(max_workers=1) as executor:
        process_result = executor.submit(
            _source_smoke_worker, str(evidence_root)
        ).result()
    if not _process_evidence_closed(evidence_root.parent):
        # _process_evidence_closed expects a runtime/process_evidence layout.
        rows = [engine._read_json(path) for path in evidence_root.glob("*_task.json")]
        if not rows or any(row.get("stage") != "TASK_COMPLETED" for row in rows):
            raise RuntimeError("source smoke process evidence did not close")
    return {
        "status": "PASS",
        "market_arrays_read": 0,
        "receipt_consumed": False,
        "compiled_family_count": len(pairs),
        "unique_pair_count": len(
            {str(pair["paired_proposal_id"]) for pair in pairs}
        ),
        "worker": process_result,
    }


def _candidate_row(
    *,
    pair: Mapping[str, Any],
    candidate: CandidateSpec,
    evaluation: Mapping[str, Any],
    representation: str,
    completion_ordinal: int,
    worker: Mapping[str, Any],
) -> dict[str, Any]:
    block = dict(evaluation["block_robust_ordering"])
    row = {
        "completion_ordinal": int(completion_ordinal),
        "tranche_index": int(pair["tranche_index"]),
        "paired_proposal_id": pair["paired_proposal_id"],
        "representation": representation,
        "candidate_id": candidate.candidate_id,
        "canonical_expression_id": candidate.expression.expression_id,
        "control_expression_id": candidate.control.expression_id,
        "candidate_spec_sha256": _json_sha(candidate.to_dict()),
        "candidate_spec_json": json.dumps(
            candidate.to_dict(), sort_keys=True, separators=(",", ":")
        ),
        "temporal_enabled": representation == "temporal",
        "temporal_primitive_id": (
            pair["primitive_id"] if representation == "temporal" else None
        ),
        "temporal_axis": (
            pair["temporal_axis"] if representation == "temporal" else None
        ),
        "temporal_window": (
            pair["temporal_window"] if representation == "temporal" else None
        ),
        "temporal_long_window": (
            pair["temporal_long_window"] if representation == "temporal" else None
        ),
        "temporal_threshold": (
            pair["temporal_threshold"] if representation == "temporal" else None
        ),
        "temporal_placement": (
            pair["temporal_placement"] if representation == "temporal" else None
        ),
        "paired_static_candidate_id": pair["static_candidate_id"],
        "temporal_family_id": pair["temporal_family_id"],
        "primitive_id": pair["primitive_id"] if representation == "temporal" else None,
        "outer_template": pair["outer_template"],
        "temporal_role": pair["temporal_role"] if representation == "temporal" else None,
        "raw_fields_json": json.dumps(list(candidate.raw_fields)),
        "mapping_id": candidate.mapping_id,
        "horizon_hours": int(candidate.horizon_hours),
        "operator_path": candidate.operator_path,
        "rolling_windows_json": json.dumps(list(candidate.rolling_windows)),
        "expression_depth": int(candidate.expression_depth),
        "train_orientation": float(evaluation["train_orientation"]),
        "search_reward": float(evaluation["search_reward"]),
        "pair_reward": float(evaluation["pair_reward"]),
        "matched_positive": bool(evaluation["matched_positive"]),
        "replicated_positive_block_count": int(
            block["replicated_positive_block_count"]
        ),
        "all_three_blocks_positive": bool(block["all_three_blocks_positive"]),
        "worst_block_min_matched_net_mean": float(
            block["worst_block_min_matched_net_mean"]
        ),
        "block_robust_ordering_json": json.dumps(
            block, sort_keys=True, separators=(",", ":")
        ),
        "process_cpu_seconds": float(worker["process_cpu_seconds"]) / 2.0,
        "worker_rss_bytes": int(worker["worker_rss_bytes"]),
        "strict_evaluated": True,
    }
    row.update(engine._evaluation_audit_fields(evaluation))
    return row


def _pair_diagnostic_row(
    *,
    pair: Mapping[str, Any],
    static: Mapping[str, Any],
    temporal: Mapping[str, Any],
    common: Mapping[str, Any],
) -> dict[str, Any]:
    static_worst = min(
        float(static["left_incremental"]["net_mean"]),
        float(static["right_incremental"]["net_mean"]),
    )
    temporal_worst = min(
        float(temporal["left_incremental"]["net_mean"]),
        float(temporal["right_incremental"]["net_mean"]),
    )
    native_delta = temporal_worst - static_worst
    common_delta = float(common["paired_worst_axis_net_delta"])
    static_dual_gross = bool(
        float(static["left_incremental"]["gross_mean"]) > 0.0
        and float(static["right_incremental"]["gross_mean"]) > 0.0
    )
    temporal_dual_gross = bool(
        float(temporal["left_incremental"]["gross_mean"]) > 0.0
        and float(temporal["right_incremental"]["gross_mean"]) > 0.0
    )
    static_dual_net = bool(
        float(static["left_incremental"]["net_mean"]) > 0.0
        and float(static["right_incremental"]["net_mean"]) > 0.0
    )
    temporal_dual_net = bool(
        float(temporal["left_incremental"]["net_mean"]) > 0.0
        and float(temporal["right_incremental"]["net_mean"]) > 0.0
    )

    def joint_lcb_margin(evaluation: Mapping[str, Any]) -> float:
        left = float(evaluation["left_incremental"]["net_lcb"])
        right = float(evaluation["right_incremental"]["net_lcb"])
        return -math.sqrt(max(0.0, -left) ** 2 + max(0.0, -right) ** 2)

    return {
        key: value
        for key, value in pair.items()
        if not key.endswith("_candidate_spec_json")
    } | {
        "static_native_worst_axis_net_mean": static_worst,
        "temporal_native_worst_axis_net_mean": temporal_worst,
        "native_paired_worst_axis_net_delta": native_delta,
        "common_static_worst_axis_net_mean": float(
            common["static_worst_axis_net_mean"]
        ),
        "common_temporal_worst_axis_net_mean": float(
            common["temporal_worst_axis_net_mean"]
        ),
        "common_paired_worst_axis_net_delta": common_delta,
        "support_selection_effect": bool(
            native_delta != 0.0
            and common_delta != 0.0
            and math.copysign(1.0, native_delta) != math.copysign(1.0, common_delta)
        ),
        "static_dual_axis_gross_positive": static_dual_gross,
        "temporal_dual_axis_gross_positive": temporal_dual_gross,
        "static_dual_axis_net_positive": static_dual_net,
        "temporal_dual_axis_net_positive": temporal_dual_net,
        "static_cost_sign_killed": static_dual_gross and not static_dual_net,
        "temporal_cost_sign_killed": temporal_dual_gross and not temporal_dual_net,
        "static_replicated_positive_block_count": int(
            static["block_robust_ordering"]["replicated_positive_block_count"]
        ),
        "temporal_replicated_positive_block_count": int(
            temporal["block_robust_ordering"]["replicated_positive_block_count"]
        ),
        "static_all_three_blocks_positive": bool(
            static["block_robust_ordering"]["all_three_blocks_positive"]
        ),
        "temporal_all_three_blocks_positive": bool(
            temporal["block_robust_ordering"]["all_three_blocks_positive"]
        ),
        "static_worst_axis_net_lcb": min(
            float(static["left_incremental"]["net_lcb"]),
            float(static["right_incremental"]["net_lcb"]),
        ),
        "temporal_worst_axis_net_lcb": min(
            float(temporal["left_incremental"]["net_lcb"]),
            float(temporal["right_incremental"]["net_lcb"]),
        ),
        "static_joint_net_lcb_margin": joint_lcb_margin(static),
        "temporal_joint_net_lcb_margin": joint_lcb_margin(temporal),
        "static_worst_block_matched_net": float(
            static["block_robust_ordering"]["worst_block_min_matched_net_mean"]
        ),
        "temporal_worst_block_matched_net": float(
            temporal["block_robust_ordering"]["worst_block_min_matched_net_mean"]
        ),
        "static_matched_positive": bool(static["matched_positive"]),
        "temporal_matched_positive": bool(temporal["matched_positive"]),
        "common_support_json": json.dumps(
            common, sort_keys=True, separators=(",", ":")
        ),
    }


def _rate(values: Sequence[bool]) -> float:
    return float(sum(bool(value) for value in values) / max(1, len(values)))


def _representation_metrics(
    pairs: pd.DataFrame,
    *,
    prefix: str,
) -> dict[str, Any]:
    gross = pairs[f"{prefix}_dual_axis_gross_positive"].astype(bool)
    net = pairs[f"{prefix}_dual_axis_net_positive"].astype(bool)
    gross_count = int(gross.sum())
    net_count = int(net.sum())
    cost_killed = gross & ~net
    return {
        "dual_axis_gross_positive_count": gross_count,
        "dual_axis_gross_positive_rate": float(gross.mean()),
        "dual_axis_net_positive_count": net_count,
        "dual_axis_net_positive_rate": float(net.mean()),
        "cost_sign_killed_count": int(cost_killed.sum()),
        "cost_sign_kill_rate": (
            float(cost_killed.sum() / gross_count) if gross_count else 1.0
        ),
        "dual_axis_net_positive_per_gross_positive": (
            float(net_count / gross_count) if gross_count else 0.0
        ),
        "replicated_2_of_3_rate": _rate(
            pairs[f"{prefix}_replicated_positive_block_count"] >= 2
        ),
        "all_three_count": int(
            pairs[f"{prefix}_all_three_blocks_positive"].astype(bool).sum()
        ),
        "worst_block_matched_net_median": float(
            pairs[f"{prefix}_worst_block_matched_net"].median()
        ),
        "worst_axis_net_lcb_p90": float(
            pairs[f"{prefix}_worst_axis_net_lcb"].quantile(0.90)
        ),
        "joint_net_lcb_margin_p90": float(
            pairs[f"{prefix}_joint_net_lcb_margin"].quantile(0.90)
        ),
        "matched_positive_count": int(
            pairs[f"{prefix}_matched_positive"].astype(bool).sum()
        ),
    }


def _positive_share(pairs: pd.DataFrame, column: str) -> float:
    positive = pairs[pairs["native_paired_worst_axis_net_delta"] > 0.0]
    return (
        float(positive[column].value_counts().iloc[0]) / float(len(positive))
        if len(positive)
        else 1.0
    )


def classify_results(
    paired_rows: Sequence[Mapping[str, Any]],
    candidate_rows: Sequence[Mapping[str, Any]],
    *,
    expected_pairs: int | None = None,
) -> dict[str, Any]:
    pairs = pd.DataFrame(list(paired_rows))
    candidates = pd.DataFrame(list(candidate_rows))
    expected = len(pairs) if expected_pairs is None else int(expected_pairs)
    if expected <= 0 or len(pairs) != expected or len(candidates) != 2 * expected:
        return {
            "status": "INVALID_RUN_FAIL_CLOSED",
            "reason": "STRICT_OR_PAIR_COUNT_CHANGED",
            "gate_checks": {},
        }
    native_deltas = pairs["native_paired_worst_axis_net_delta"].to_numpy(float)
    common_deltas = pairs["common_paired_worst_axis_net_delta"].to_numpy(float)
    static = _representation_metrics(pairs, prefix="static")
    temporal = _representation_metrics(pairs, prefix="temporal")
    static_rate = float(static["dual_axis_net_positive_rate"])
    temporal_rate = float(temporal["dual_axis_net_positive_rate"])
    relative = (
        (temporal_rate - static_rate) / static_rate
        if static_rate > 0.0
        else float("inf") if temporal_rate > 0.0 else 0.0
    )
    template_medians = {
        str(key): float(value)
        for key, value in pairs.groupby("outer_template")[
            "native_paired_worst_axis_net_delta"
        ].median().items()
    }
    primitive_medians = {
        str(key): float(value)
        for key, value in pairs.groupby("primitive_id")[
            "native_paired_worst_axis_net_delta"
        ].median().items()
    }
    field_family_medians = {
        str(key): float(value)
        for key, value in pairs.groupby("temporal_field_family")[
            "native_paired_worst_axis_net_delta"
        ].median().items()
    }
    best_template = max(
        template_medians,
        key=lambda key: (template_medians[key], key),
    )
    leave_best = pairs[pairs["outer_template"] != best_template][
        "native_paired_worst_axis_net_delta"
    ]
    best_field_family = max(
        field_family_medians,
        key=lambda key: (field_family_medians[key], key),
    )
    leave_best_field_family = pairs[
        pairs["temporal_field_family"] != best_field_family
    ]["native_paired_worst_axis_net_delta"]
    top_template_share = _positive_share(pairs, "outer_template")
    top_primitive_share = _positive_share(pairs, "primitive_id")
    checks = {
        "paired_delta_median_strictly_positive": (
            float(np.median(native_deltas)) > 0.0
        ),
        "temporal_pair_win_fraction_minimum": (
            float(np.mean(native_deltas > 0.0)) >= 0.55
        ),
        "common_support_paired_delta_median_nonnegative": (
            float(np.median(common_deltas)) >= 0.0
        ),
        "native_dual_axis_net_positive_rate_improved": temporal_rate > static_rate,
        "native_dual_axis_net_positive_effect_size": (
            temporal_rate - static_rate >= 0.01 or relative >= 0.20
        ),
        "cost_sign_kill_rate_not_above_static": (
            temporal["cost_sign_kill_rate"] <= static["cost_sign_kill_rate"]
        ),
        "dual_axis_net_positive_per_gross_positive_above_static": (
            temporal["dual_axis_net_positive_per_gross_positive"]
            > static["dual_axis_net_positive_per_gross_positive"]
        ),
        "replicated_2_of_3_rate_strictly_above_static": (
            temporal["replicated_2_of_3_rate"] > static["replicated_2_of_3_rate"]
        ),
        "all_3_blocks_count_not_below_static": (
            temporal["all_three_count"] >= static["all_three_count"]
        ),
        "worst_block_matched_net_median_above_static": (
            temporal["worst_block_matched_net_median"]
            > static["worst_block_matched_net_median"]
        ),
        "worst_axis_lcb_p90_improved": (
            temporal["worst_axis_net_lcb_p90"] > static["worst_axis_net_lcb_p90"]
        ),
        "joint_net_lcb_margin_p90_improved": (
            temporal["joint_net_lcb_margin_p90"]
            > static["joint_net_lcb_margin_p90"]
        ),
        "minimum_positive_template_count": sum(
            value > 0.0 for value in template_medians.values()
        )
        >= 2,
        "minimum_positive_primitive_count": sum(
            value > 0.0 for value in primitive_medians.values()
        )
        >= 2,
        "leave_best_template_out_positive": float(leave_best.median()) > 0.0,
        "maximum_top_template_positive_delta_share": top_template_share <= 0.40,
    }
    broad = all(checks.values())
    final_breadth = {
        "minimum_positive_field_family_count": sum(
            value > 0.0 for value in field_family_medians.values()
        )
        >= 2,
        "leave_best_field_family_out_positive": (
            float(leave_best_field_family.median()) > 0.0
        ),
    }
    broadly_supported = broad and all(final_breadth.values())
    local = (
        not broadly_supported
        and (
            sum(value > 0.0 for value in template_medians.values()) >= 1
            or sum(value > 0.0 for value in primitive_medians.values()) >= 1
        )
        and float(np.median(native_deltas)) > 0.0
    )
    status = (
        "CANONICAL_TEMPORAL_PRIMITIVE_ACTIVATION_SUPPORTED"
        if broadly_supported
        else "LOCAL_TEMPORAL_MECHANISM_LINE_IDENTIFIED"
        if local
        else "CANONICAL_TEMPORAL_PRIMITIVE_ACTIVATION_NOT_SUPPORTED"
    )
    return {
        "status": status,
        "reason": "CUMULATIVE_PAIRED_DEVELOPMENT_EVIDENCE_CLASSIFIED",
        "gate_checks": checks,
        "final_breadth_checks": final_breadth,
        "broad_shift_gate_pass": broad,
        "metrics": {
            "pair_count": len(pairs),
            "native_paired_delta_median": float(np.median(native_deltas)),
            "native_temporal_win_fraction": float(np.mean(native_deltas > 0.0)),
            "common_support_paired_delta_median": float(np.median(common_deltas)),
            "common_support_temporal_win_fraction": float(
                np.mean(common_deltas > 0.0)
            ),
            "static": static,
            "temporal": temporal,
            "static_dual_axis_net_positive_rate": static_rate,
            "temporal_dual_axis_net_positive_rate": temporal_rate,
            "dual_axis_net_positive_absolute_delta": temporal_rate - static_rate,
            "dual_axis_net_positive_relative_delta": relative,
            "static_replicated_2_of_3_rate": static["replicated_2_of_3_rate"],
            "temporal_replicated_2_of_3_rate": temporal["replicated_2_of_3_rate"],
            "static_all_three_count": static["all_three_count"],
            "temporal_all_three_count": temporal["all_three_count"],
            "static_matched_positive_count": static["matched_positive_count"],
            "temporal_matched_positive_count": temporal["matched_positive_count"],
            "support_selection_effect_count": int(
                pairs["support_selection_effect"].sum()
            ),
            "top_template_positive_delta_share": top_template_share,
            "top_primitive_positive_delta_share": top_primitive_share,
            "best_template_removed": best_template,
            "leave_best_template_out_delta_median": float(leave_best.median()),
            "template_delta_medians": template_medians,
            "primitive_delta_medians": primitive_medians,
            "field_family_delta_medians": field_family_medians,
            "best_field_family_removed": best_field_family,
            "leave_best_field_family_out_delta_median": float(
                leave_best_field_family.median()
            ),
        },
        "alpha_claim": False,
        "validation": False,
        "oos": False,
        "temporal_evolution_authorized": False,
        "automatic_continuation": False,
    }


def _positive_groups(pairs: pd.DataFrame, column: str) -> set[str]:
    return {
        str(key)
        for key, value in pairs.groupby(column)[
            "native_paired_worst_axis_net_delta"
        ].median().items()
        if float(value) > 0.0
    }


def continuation_decision(
    paired_rows: Sequence[Mapping[str, Any]],
    candidate_rows: Sequence[Mapping[str, Any]],
    *,
    completed_tranche: int,
    prior_decisions: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    """Apply the frozen sequential-release rule without changing proposals."""

    completed_tranche = int(completed_tranche)
    expected_pairs = (completed_tranche + 1) * 1_024
    cumulative = classify_results(
        paired_rows,
        candidate_rows,
        expected_pairs=expected_pairs,
    )
    if cumulative["status"] == "INVALID_RUN_FAIL_CLOSED":
        return {
            "decision": "STOP_INVALID",
            "completed_tranche": completed_tranche,
            "strict_evaluated_count": expected_pairs * 2,
            "cumulative": cumulative,
            "next_tranche_proposals_generated": False,
        }
    if completed_tranche == 0:
        return {
            "decision": (
                "CONTINUE"
                if cumulative["broad_shift_gate_pass"] is True
                else "STOP_TEMPORAL_NOT_SUPPORTED"
            ),
            "completed_tranche": 0,
            "strict_evaluated_count": 2_048,
            "cumulative": cumulative,
            "next_tranche_proposals_generated": False,
        }

    pairs = pd.DataFrame(list(paired_rows))
    start = completed_tranche * 1_024
    current = pairs.iloc[start : start + 1_024]
    previous = pairs.iloc[:start]
    current_delta_nonnegative = bool(
        float(current["native_paired_worst_axis_net_delta"].median()) >= 0.0
    )
    new_matched_positive = int(current["temporal_matched_positive"].sum())
    new_all_three = int(current["temporal_all_three_blocks_positive"].sum())
    new_templates = sorted(
        _positive_groups(pairs, "outer_template")
        - _positive_groups(previous, "outer_template")
    )
    new_primitives = sorted(
        _positive_groups(pairs, "primitive_id")
        - _positive_groups(previous, "primitive_id")
    )
    previous_metrics = _representation_metrics(previous, prefix="temporal")
    cumulative_metrics = _representation_metrics(pairs, prefix="temporal")
    cost_improved = bool(
        cumulative_metrics["cost_sign_kill_rate"]
        < previous_metrics["cost_sign_kill_rate"]
    )
    net_rate_improved = bool(
        cumulative_metrics["dual_axis_net_positive_rate"]
        > previous_metrics["dual_axis_net_positive_rate"]
    )
    marginal = {
        "new_matched_positive_count": new_matched_positive,
        "new_all_three_count": new_all_three,
        "new_positive_templates": new_templates,
        "new_positive_primitives": new_primitives,
        "cumulative_cost_sign_kill_rate_improved": cost_improved,
        "cumulative_dual_axis_net_positive_rate_improved": net_rate_improved,
    }
    marginal_progress = any(
        (
            new_matched_positive > 0,
            new_all_three > 0,
            bool(new_templates),
            bool(new_primitives),
            cost_improved,
            net_rate_improved,
        )
    )
    no_boundary_progress = not any(
        (
            new_matched_positive > 0,
            new_all_three > 0,
            bool(new_templates),
            bool(new_primitives),
            cost_improved,
        )
    )
    prior_no_progress = bool(
        prior_decisions
        and prior_decisions[-1].get("no_boundary_progress") is True
    )
    concentration = {
        "top_template_positive_delta_share": _positive_share(
            pairs, "outer_template"
        ),
        "top_primitive_positive_delta_share": _positive_share(
            pairs, "primitive_id"
        ),
    }
    cumulative_broad = bool(
        cumulative["broad_shift_gate_pass"] is True
    )
    continuation_checks = {
        "cumulative_broad_shift_pass": cumulative_broad,
        "current_tranche_paired_delta_median_nonnegative": (
            current_delta_nonnegative
        ),
        "marginal_progress_present": marginal_progress,
        "top_template_positive_delta_share_at_most_0_35": (
            concentration["top_template_positive_delta_share"] <= 0.35
        ),
        "top_primitive_positive_delta_share_at_most_0_40": (
            concentration["top_primitive_positive_delta_share"] <= 0.40
        ),
        "not_two_consecutive_no_boundary_progress": not (
            no_boundary_progress and prior_no_progress
        ),
    }
    if completed_tranche == 3:
        action = "MAXIMUM_BUDGET_COMPLETE"
    elif not cumulative_broad:
        action = "STOP_TEMPORAL_NOT_SUPPORTED"
    elif no_boundary_progress and prior_no_progress:
        action = "EARLY_STOP_TEMPORAL_FUTILITY"
    elif all(continuation_checks.values()):
        action = "CONTINUE"
    else:
        action = "EARLY_STOP_TEMPORAL_FUTILITY"
    return {
        "decision": action,
        "completed_tranche": completed_tranche,
        "strict_evaluated_count": expected_pairs * 2,
        "cumulative": cumulative,
        "current_tranche_native_paired_delta_median": float(
            current["native_paired_worst_axis_net_delta"].median()
        ),
        "marginal_progress": marginal,
        "no_boundary_progress": no_boundary_progress,
        "continuation_checks": continuation_checks,
        "concentration": concentration,
        "next_tranche_proposals_generated": False,
    }


def _write_progress(
    runtime_root: Path,
    *,
    source_sha: str,
    frozen_hash: str,
    workers: int,
    attempts: Mapping[str, int],
    accepted: Mapping[str, int],
    pair_rows: Sequence[Mapping[str, Any]],
    diagnostic_rows: Sequence[Mapping[str, Any]],
    candidate_rows: Sequence[Mapping[str, Any]],
    rejected_rows: Sequence[Mapping[str, Any]],
    elapsed: float,
) -> None:
    engine._write_parquet(runtime_root / "paired_proposal_ledger.parquet", pair_rows)
    engine._write_parquet(
        runtime_root / "paired_economic_diagnostics.parquet", diagnostic_rows
    )
    engine._write_parquet(runtime_root / "candidate_ledger.parquet", candidate_rows)
    engine._write_parquet(runtime_root / "rejected_pair_ledger.parquet", rejected_rows)
    engine._write_json(
        runtime_root / "work_state.json",
        {
            "schema_version": 1,
            "source_sha": source_sha,
            "frozen_contract_sha256": frozen_hash,
            "workers": int(workers),
            "attempts_by_family": dict(attempts),
            "accepted_by_family": dict(accepted),
            "pair_row_count": len(pair_rows),
            "diagnostic_row_count": len(diagnostic_rows),
            "candidate_row_count": len(candidate_rows),
            "rejected_row_count": len(rejected_rows),
            "active_wall_seconds": float(elapsed),
        },
    )


def _load_progress(
    runtime_root: Path,
    *,
    source_sha: str,
    frozen_hash: str,
) -> tuple[
    dict[str, int],
    dict[str, int],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    float,
    int,
]:
    state_path = runtime_root / "work_state.json"
    if not state_path.is_file():
        return {}, {}, [], [], [], [], 0.0, 10
    state = engine._read_json(state_path)
    if (
        state.get("source_sha") != source_sha
        or state.get("frozen_contract_sha256") != frozen_hash
    ):
        raise RuntimeError("temporal work state identity changed")
    pairs = pd.read_parquet(runtime_root / "paired_proposal_ledger.parquet").to_dict("records")
    diagnostics = pd.read_parquet(
        runtime_root / "paired_economic_diagnostics.parquet"
    ).to_dict("records")
    candidates = pd.read_parquet(runtime_root / "candidate_ledger.parquet").to_dict("records")
    rejected_path = runtime_root / "rejected_pair_ledger.parquet"
    rejected = (
        pd.read_parquet(rejected_path).to_dict("records")
        if rejected_path.is_file()
        else []
    )
    if (
        len(pairs) != int(state["pair_row_count"])
        or len(diagnostics) != int(state["diagnostic_row_count"])
        or len(candidates) != int(state["candidate_row_count"])
    ):
        raise RuntimeError("temporal work state row count changed")
    return (
        {str(k): int(v) for k, v in state["attempts_by_family"].items()},
        {str(k): int(v) for k, v in state["accepted_by_family"].items()},
        pairs,
        diagnostics,
        candidates,
        rejected,
        float(state["active_wall_seconds"]),
        int(state["workers"]),
    )


def _process_evidence_closed(runtime_root: Path) -> bool:
    task_rows = [
        engine._read_json(path)
        for path in sorted((runtime_root / "process_evidence").glob("*_task.json"))
    ]
    return bool(task_rows) and all(row.get("stage") == "TASK_COMPLETED" for row in task_rows)


def _write_derived_views(
    runtime_root: Path,
    *,
    pair_rows: Sequence[Mapping[str, Any]],
    diagnostic_rows: Sequence[Mapping[str, Any]],
    candidate_rows: Sequence[Mapping[str, Any]],
) -> None:
    pairs = pd.DataFrame(list(pair_rows))
    diagnostics = pd.DataFrame(list(diagnostic_rows))
    candidates = pd.DataFrame(list(candidate_rows))
    exposure = (
        pairs.groupby(
            [
                "tranche_index",
                "temporal_family_id",
                "primitive_id",
                "outer_template",
                "temporal_role",
            ],
            dropna=False,
        )
        .size()
        .rename("pair_count")
        .reset_index()
    )
    waterfall_rows: list[dict[str, Any]] = []
    block_rows: list[dict[str, Any]] = []
    lcb_rows: list[dict[str, Any]] = []
    grouped_candidates = [
        (int(tranche_index), str(representation), group)
        for (tranche_index, representation), group in candidates.groupby(
            ["tranche_index", "representation"]
        )
    ]
    grouped_candidates.extend(
        (-1, str(representation), group)
        for representation, group in candidates.groupby("representation")
    )
    for tranche_index, representation, group in grouped_candidates:
        dual_gross = (
            group["left_incremental_gross_mean"].astype(float) > 0.0
        ) & (group["right_incremental_gross_mean"].astype(float) > 0.0)
        dual_net = (group["left_incremental_net_mean"].astype(float) > 0.0) & (
            group["right_incremental_net_mean"].astype(float) > 0.0
        )
        waterfall_rows.append(
            {
                "representation": representation,
                "tranche_index": tranche_index,
                "strict_count": len(group),
                "dual_axis_gross_positive_count": int(dual_gross.sum()),
                "cost_sign_killed_count": int((dual_gross & ~dual_net).sum()),
                "dual_axis_net_positive_count": int(dual_net.sum()),
                "matched_positive_count": int(group["matched_positive"].sum()),
            }
        )
        block_rows.append(
            {
                "representation": representation,
                "tranche_index": tranche_index,
                "replicated_2_of_3_count": int(
                    (group["replicated_positive_block_count"] >= 2).sum()
                ),
                "all_three_blocks_positive_count": int(
                    group["all_three_blocks_positive"].sum()
                ),
                "worst_block_matched_net_median": float(
                    group["worst_block_min_matched_net_mean"].median()
                ),
            }
        )
        worst_lcb = group["left_incremental_net_lcb"].combine(
            group["right_incremental_net_lcb"], min
        )
        for quantile in (0.1, 0.5, 0.9):
            lcb_rows.append(
                {
                    "representation": representation,
                    "tranche_index": tranche_index,
                    "quantile": quantile,
                    "worst_axis_net_lcb": float(worst_lcb.quantile(quantile)),
                }
            )
    engine._write_parquet(
        runtime_root / "template_primitive_exposure.parquet",
        exposure.to_dict("records"),
    )
    engine._write_parquet(
        runtime_root / "economic_waterfall.parquet", waterfall_rows
    )
    engine._write_parquet(
        runtime_root / "block_robustness.parquet", block_rows
    )
    engine._write_parquet(runtime_root / "lcb_distribution.parquet", lcb_rows)
    if len(diagnostics) != len(pairs):
        raise RuntimeError("paired diagnostics are not one-to-one")


def _checkpoint(
    runtime_root: Path,
    *,
    checkpoint_index: int,
    source_sha: str,
    frozen_hash: str,
    attempts: Mapping[str, int],
    accepted: Mapping[str, int],
    pair_rows: Sequence[Mapping[str, Any]],
    diagnostic_rows: Sequence[Mapping[str, Any]],
    candidate_rows: Sequence[Mapping[str, Any]],
    rejected_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    checkpoint_root = runtime_root / "checkpoints"
    final_path = checkpoint_root / f"checkpoint_{checkpoint_index:03d}"
    temporary = checkpoint_root / f"checkpoint_{checkpoint_index:03d}.tmp"
    if final_path.exists() or temporary.exists():
        raise RuntimeError("temporal checkpoint target already exists")
    temporary.mkdir(parents=True, exist_ok=False)
    files = (
        "work_state.json",
        "paired_proposal_ledger.parquet",
        "paired_economic_diagnostics.parquet",
        "candidate_ledger.parquet",
        "rejected_pair_ledger.parquet",
    )
    for value in files:
        shutil.copyfile(runtime_root / value, temporary / value)
    manifest = {
        "schema_version": 1,
        "checkpoint_index": int(checkpoint_index),
        "source_sha": source_sha,
        "frozen_contract_sha256": frozen_hash,
        "strict_evaluated_count": len(candidate_rows),
        "pair_count": len(pair_rows),
        "diagnostic_count": len(diagnostic_rows),
        "rejected_count": len(rejected_rows),
        "attempts_by_family": dict(attempts),
        "accepted_by_family": dict(accepted),
        "proposal_rng_state": {
            "kind": "STATELESS_SHA256_SEED_DERIVATION",
            "attempts_by_family": dict(attempts),
        },
        "files": [
            {
                "path": value,
                "sha256": _sha256_file(temporary / value),
                "bytes": (temporary / value).stat().st_size,
            }
            for value in files
        ],
    }
    manifest["checkpoint_state_sha256"] = _json_sha(manifest)
    engine._write_json(temporary / "manifest.json", manifest)
    os.replace(temporary, final_path)
    restored = engine._read_json(final_path / "manifest.json")
    if restored != manifest or any(
        _sha256_file(final_path / row["path"]) != row["sha256"]
        for row in restored["files"]
    ):
        raise RuntimeError("checkpoint restore verification failed")
    return restored


def run(
    repo_root: Path,
    *,
    runtime_date: str,
    source_sha: str | None = None,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    config = engine._read_json(repo_root / CONFIG_PATH)
    _validate_config(config)
    receipt = _validate_binding_receipt(
        repo_root, config=config, require_authorized=True
    )
    observed_sha = engine._git_sha(repo_root)
    source_sha = str(source_sha or observed_sha).lower()
    if source_sha != observed_sha:
        raise RuntimeError("temporal run source SHA differs from checkout")
    runtime_root = repo_root / f"runtime/{CAMPAIGN}_{runtime_date}"
    report_path = repo_root / (
        "reports/CRYPTO_SEARCH_CORE_V3_CANONICAL_TEMPORAL_PRIMITIVE_ACTIVATION_"
        f"{runtime_date}.md"
    )
    if not engine._source_tree_clean_for_run(
        repo_root, allowed_paths=(runtime_root, report_path)
    ):
        raise RuntimeError("temporal producer tree is not clean")
    economic = resolve_search_economic_receipt(repo_root, ECONOMIC_RECEIPT_PATH)
    train = dict(economic["evidence_partition"]["train"])
    store, contracts, behavior, identities, _ = engine._load_v14_inputs(
        repo_root, behavior_window=train
    )
    if len(contracts) != 115:
        raise RuntimeError("temporal gate requires the existing 115-field carrier")
    block_config = engine._read_json(repo_root / BLOCK_CONFIG_PATH)
    optimizer_block_contract = dict(block_config["block_robust_contract"])
    catalog = compile_mechanism_catalog(
        engine._read_json(repo_root / CATALOG_PATH)
    )
    specs = tuple(
        value
        for value in catalog
        if value.generation == 1
        and value.matched_control_schema == "DUAL_AXIS_A_B_AB"
    )
    registry = TypedExpressionRegistry(contracts)
    domains = {
        **mechanism_role_domains(contracts),
        "__HORIZONS__": (4,),
    }
    frozen = {
        "schema_version": 1,
        "experiment_id": config["experiment_id"],
        "source_sha": source_sha,
        "config": config,
        "binding_receipt_sha256": receipt["receipt_sha256"],
        "economic_receipt": economic,
        "input_identities": identities,
        "behavior_contract_sha256": _json_sha(behavior),
        "compiler_identity": engine._compiler_binding(repo_root),
        "block_robust_contract": optimizer_block_contract,
        "allowed_primitive_ids": list(ALLOWED_PRIMITIVES),
        "sealed_reads": 0,
    }
    frozen_hash = _json_sha(frozen)
    frozen = {**frozen, "frozen_contract_sha256": frozen_hash}
    if runtime_root.exists():
        if engine._read_json(runtime_root / "frozen_contract.json") != frozen:
            raise RuntimeError("existing temporal runtime contract changed")
        if engine._read_json(
            runtime_root / "search_authority_binding_receipt.json"
        ) != receipt:
            raise RuntimeError("existing temporal runtime receipt changed")
        if (runtime_root / "final_decision.json").is_file():
            raise FileExistsError("temporal experiment already completed")
    else:
        runtime_root.mkdir(parents=True)
        engine._write_json(runtime_root / "frozen_contract.json", frozen)
        engine._write_json(
            runtime_root / "search_authority_binding_receipt.json", receipt
        )
    (
        attempts,
        accepted,
        pair_rows,
        diagnostic_rows,
        candidate_rows,
        rejected_rows,
        prior_elapsed,
        workers,
    ) = _load_progress(
        runtime_root,
        source_sha=source_sha,
        frozen_hash=frozen_hash,
    )
    families = tuple(dict(value) for value in config["temporal_families"])
    for family in families:
        attempts.setdefault(str(family["family_id"]), 0)
        accepted.setdefault(str(family["family_id"]), 0)
    budget = dict(config["search_budget"])
    if workers not in {
        int(budget["workers_default"]),
        int(budget["workers_memory_fallback"]),
    }:
        raise RuntimeError("temporal worker count changed")
    active_started = time.perf_counter()

    def elapsed() -> float:
        return prior_elapsed + time.perf_counter() - active_started

    def start_executor(count: int) -> concurrent.futures.ProcessPoolExecutor:
        return concurrent.futures.ProcessPoolExecutor(
            max_workers=count,
            initializer=engine._worker_initialize,
            initargs=(
                str(repo_root / identities["raw_cache"]["root"]),
                engine._contracts_payload(contracts),
                behavior,
                str(train["start"]),
                str(train["end_exclusive"]),
                BLOCK_ROLE,
                economic,
                False,
                optimizer_block_contract,
                str(runtime_root / "process_evidence"),
            ),
        )

    executor: concurrent.futures.ProcessPoolExecutor | None = None
    batch_index = 0
    decision_rows: list[dict[str, Any]] = []
    completed_tranches = len(pair_rows) // int(budget["pair_per_tranche"])
    if len(pair_rows) % int(budget["pair_per_tranche"]):
        expected_previous = completed_tranches
    else:
        expected_previous = completed_tranches
    terminal_action: str | None = None
    for checkpoint_index in range(expected_previous):
        strict_count = (checkpoint_index + 1) * int(
            budget["strict_evaluated_per_tranche"]
        )
        decision_path = runtime_root / f"continuation_decision_{strict_count:06d}.json"
        checkpoint_path = (
            runtime_root / "checkpoints" / f"checkpoint_{checkpoint_index:03d}"
        )
        if not checkpoint_path.is_dir():
            if checkpoint_index != expected_previous - 1:
                raise RuntimeError("historical completed tranche is missing its checkpoint")
            if not _process_evidence_closed(runtime_root):
                raise RuntimeError("resume boundary process evidence did not close")
            temporary_checkpoint = checkpoint_path.with_name(
                checkpoint_path.name + ".tmp"
            )
            if temporary_checkpoint.exists():
                shutil.rmtree(temporary_checkpoint)
            _write_derived_views(
                runtime_root,
                pair_rows=pair_rows,
                diagnostic_rows=diagnostic_rows,
                candidate_rows=candidate_rows,
            )
            _checkpoint(
                runtime_root,
                checkpoint_index=checkpoint_index,
                source_sha=source_sha,
                frozen_hash=frozen_hash,
                attempts=attempts,
                accepted=accepted,
                pair_rows=pair_rows,
                diagnostic_rows=diagnostic_rows,
                candidate_rows=candidate_rows,
                rejected_rows=rejected_rows,
            )
        manifest = engine._read_json(checkpoint_path / "manifest.json")
        if any(
            _sha256_file(checkpoint_path / row["path"]) != row["sha256"]
            for row in manifest["files"]
        ):
            raise RuntimeError("completed tranche checkpoint restore changed")
        if not decision_path.is_file():
            if checkpoint_index != expected_previous - 1:
                raise RuntimeError("historical continuation decision is missing")
            decision = continuation_decision(
                diagnostic_rows[: (checkpoint_index + 1) * 1_024],
                candidate_rows[: (checkpoint_index + 1) * 2_048],
                completed_tranche=checkpoint_index,
                prior_decisions=decision_rows,
            )
            engine._write_json(decision_path, decision)
        decision = engine._read_json(decision_path)
        decision_rows.append(decision)
        if checkpoint_index < expected_previous - 1 and decision["decision"] != "CONTINUE":
            raise RuntimeError("later tranche exists after a frozen stop decision")
    if decision_rows and (
        decision_rows[-1]["decision"] != "CONTINUE" or completed_tranches == 4
    ):
        terminal_action = str(decision_rows[-1]["decision"])
    try:
        if terminal_action is None:
            executor = start_executor(workers)
        while (
            terminal_action is None
            and len(pair_rows) < int(budget["pair_maximum"])
        ):
            tranche_index = len(pair_rows) // int(budget["pair_per_tranche"])
            family_target = (tranche_index + 1) * 256
            if sum(attempts.values()) >= int(budget["raw_pair_attempts_maximum"]):
                raise RuntimeError("TEMPORAL_RAW_PAIR_ATTEMPT_LIMIT")
            if elapsed() >= float(budget["wall_time_seconds_maximum"]):
                raise RuntimeError("TEMPORAL_ACTIVE_WALL_LIMIT")
            batch: list[dict[str, Any]] = []
            reserved_candidate_ids = {
                str(row["candidate_id"]) for row in candidate_rows
            }
            reserved_pair_ids = {
                str(row["paired_proposal_id"]) for row in pair_rows
            }
            for family in families:
                family_id = str(family["family_id"])
                deficit = family_target - accepted[family_id]
                if deficit <= 0:
                    continue
                slots = min(deficit, max(1, math.ceil(workers / 4)))
                generated = 0
                while generated < slots:
                    if sum(attempts.values()) >= int(
                        budget["raw_pair_attempts_maximum"]
                    ):
                        raise RuntimeError("TEMPORAL_RAW_PAIR_ATTEMPT_LIMIT")
                    slot = accepted[family_id] + generated
                    attempt = attempts[family_id]
                    attempts[family_id] += 1
                    try:
                        pair = propose_pair(
                            config=config,
                            family=family,
                            registry=registry,
                            specs=specs,
                            domains=domains,
                            slot=slot,
                            attempt=attempt,
                        )
                    except (ValueError, AssertionError) as failure:
                        rejected_rows.append(
                            {
                                "temporal_family_id": family_id,
                                "allocation_slot": slot,
                                "generation_attempt_within_slot": attempt,
                                "status": "STATIC_COMPILE_REJECT",
                                "error": type(failure).__name__ + ":" + str(failure),
                            }
                        )
                        continue
                    pair["tranche_index"] = tranche_index
                    pair["within_tranche_family_slot"] = slot - tranche_index * 256
                    candidate_ids = {
                        str(pair["static"].candidate_id),
                        str(pair["temporal"].candidate_id),
                    }
                    if (
                        len(candidate_ids) != 2
                        or candidate_ids & reserved_candidate_ids
                        or str(pair["paired_proposal_id"]) in reserved_pair_ids
                    ):
                        rejected_rows.append(
                            {
                                "temporal_family_id": family_id,
                                "allocation_slot": slot,
                                "generation_attempt_within_slot": attempt,
                                "status": "EXACT_DUPLICATE_REJECT",
                                "error": "paired candidate or pair identity already completed",
                            }
                        )
                        continue
                    reserved_candidate_ids.update(candidate_ids)
                    reserved_pair_ids.add(str(pair["paired_proposal_id"]))
                    batch.append(pair)
                    generated += 1
            if not batch:
                continue
            if executor is None:
                raise RuntimeError("temporal executor was not initialized")
            futures = {
                executor.submit(
                    _worker_pair,
                    {
                        "paired_proposal_id": pair["paired_proposal_id"],
                        "static": pair["static"].to_dict(),
                        "temporal": pair["temporal"].to_dict(),
                    },
                ): pair
                for pair in batch
            }
            results = [
                (futures[future], future.result())
                for future in concurrent.futures.as_completed(futures)
            ]
            memory_failures = [
                value for _, value in results if value["status"] == "MEMORY_ERROR"
            ]
            if memory_failures and workers == int(budget["workers_default"]):
                executor.shutdown(wait=True, cancel_futures=False)
                workers = int(budget["workers_memory_fallback"])
                executor = start_executor(workers)
                retry_pairs = {
                    str(pair["paired_proposal_id"]): pair
                    for pair, result in results
                    if result["status"] == "MEMORY_ERROR"
                }
                retry_futures = {
                    executor.submit(
                        _worker_pair,
                        {
                            "paired_proposal_id": pair["paired_proposal_id"],
                            "static": pair["static"].to_dict(),
                            "temporal": pair["temporal"].to_dict(),
                        },
                    ): pair
                    for pair in retry_pairs.values()
                }
                retry_results = [
                    (retry_futures[future], future.result())
                    for future in concurrent.futures.as_completed(retry_futures)
                ]
                retry_by_id = {
                    str(pair["paired_proposal_id"]): (pair, result)
                    for pair, result in retry_results
                }
                results = [
                    retry_by_id.get(str(pair["paired_proposal_id"]), (pair, result))
                    for pair, result in results
                ]
                if any(result["status"] == "MEMORY_ERROR" for _, result in results):
                    raise MemoryError("temporal pair evaluation failed at 8 workers")
            elif memory_failures:
                raise MemoryError("temporal pair evaluation failed at 8 workers")
            for pair, result in sorted(
                results, key=lambda value: str(value[0]["paired_proposal_id"])
            ):
                family_id = str(pair["temporal_family_id"])
                if result["status"] != "PAIR_EVALUATED":
                    rejected_rows.append(
                        {
                            **{
                                key: value
                                for key, value in pair.items()
                                if key not in {"static", "temporal"}
                                and not key.endswith("_candidate_spec_json")
                            },
                            "status": result["status"],
                            "error": result["error"],
                        }
                    )
                    continue
                if accepted[family_id] >= family_target:
                    raise RuntimeError("temporal family quota overshot")
                accepted[family_id] += 1
                pair_row = {
                    key: value
                    for key, value in pair.items()
                    if key not in {"static", "temporal"}
                }
                pair_rows.append(pair_row)
                candidate_rows.append(
                    _candidate_row(
                        pair=pair,
                        candidate=pair["static"],
                        evaluation=result["static"],
                        representation="static",
                        completion_ordinal=len(candidate_rows),
                        worker=result,
                    )
                )
                candidate_rows.append(
                    _candidate_row(
                        pair=pair,
                        candidate=pair["temporal"],
                        evaluation=result["temporal"],
                        representation="temporal",
                        completion_ordinal=len(candidate_rows),
                        worker=result,
                    )
                )
                diagnostic_rows.append(
                    _pair_diagnostic_row(
                        pair=pair,
                        static=result["static"],
                        temporal=result["temporal"],
                        common=result["common_support"],
                    )
                )
            _write_progress(
                runtime_root,
                source_sha=source_sha,
                frozen_hash=frozen_hash,
                workers=workers,
                attempts=attempts,
                accepted=accepted,
                pair_rows=pair_rows,
                diagnostic_rows=diagnostic_rows,
                candidate_rows=candidate_rows,
                rejected_rows=rejected_rows,
                elapsed=elapsed(),
            )
            observed_rate = len(candidate_rows) * 3600.0 / max(elapsed(), 1.0)
            engine._write_json(
                runtime_root / "producer_status.json",
                {
                    "status": "RUNNING",
                    "producer_source_sha": source_sha,
                    "batch_index": batch_index,
                    "strict_evaluated": len(candidate_rows),
                    "strict_maximum": int(budget["strict_evaluated_maximum"]),
                    "current_tranche": tranche_index,
                    "accepted_by_family": accepted,
                    "raw_pair_attempts": sum(attempts.values()),
                    "active_wall_seconds": elapsed(),
                    "observed_candidates_per_hour": observed_rate,
                    "workers": workers,
                    "heartbeat_utc": pd.Timestamp.now(tz="UTC").isoformat(),
                },
            )
            batch_index += 1
            if len(pair_rows) == (tranche_index + 1) * int(
                budget["pair_per_tranche"]
            ):
                if not _process_evidence_closed(runtime_root):
                    raise RuntimeError("temporal process evidence did not close")
                _write_derived_views(
                    runtime_root,
                    pair_rows=pair_rows,
                    diagnostic_rows=diagnostic_rows,
                    candidate_rows=candidate_rows,
                )
                checkpoint = _checkpoint(
                    runtime_root,
                    checkpoint_index=tranche_index,
                    source_sha=source_sha,
                    frozen_hash=frozen_hash,
                    attempts=attempts,
                    accepted=accepted,
                    pair_rows=pair_rows,
                    diagnostic_rows=diagnostic_rows,
                    candidate_rows=candidate_rows,
                    rejected_rows=rejected_rows,
                )
                decision = continuation_decision(
                    diagnostic_rows,
                    candidate_rows,
                    completed_tranche=tranche_index,
                    prior_decisions=decision_rows,
                )
                decision["checkpoint_state_sha256"] = checkpoint[
                    "checkpoint_state_sha256"
                ]
                strict_count = (tranche_index + 1) * int(
                    budget["strict_evaluated_per_tranche"]
                )
                engine._write_json(
                    runtime_root / f"continuation_decision_{strict_count:06d}.json",
                    decision,
                )
                decision_rows.append(decision)
                if decision["decision"] != "CONTINUE" or tranche_index == 3:
                    terminal_action = str(decision["decision"])
    finally:
        if executor is not None:
            executor.shutdown(wait=True, cancel_futures=False)
    if not decision_rows:
        raise RuntimeError("temporal run ended without a tranche decision")
    decision = dict(decision_rows[-1]["cumulative"])
    if terminal_action == "STOP_INVALID":
        decision = {
            "status": "INVALID_RUN_FAIL_CLOSED",
            "reason": "TRANCHE_INTEGRITY_FAILED",
            "gate_checks": {},
        }
    elif terminal_action == "EARLY_STOP_TEMPORAL_FUTILITY":
        decision["status"] = "EARLY_STOP_TEMPORAL_FUTILITY"
        decision["reason"] = (
            "TWO_CONSECUTIVE_TRANCHES_WITHOUT_BOUNDARY_PROGRESS"
            if len(decision_rows) >= 2
            and decision_rows[-1].get("no_boundary_progress") is True
            and decision_rows[-2].get("no_boundary_progress") is True
            else "LATER_TRANCHE_MARGINAL_CONTINUATION_GATE_FAILED"
        )
    checkpoint_restore_verified = all(
        all(
            _sha256_file(path.parent / row["path"]) == row["sha256"]
            for row in engine._read_json(path)["files"]
        )
        for path in sorted((runtime_root / "checkpoints").glob("*/manifest.json"))
    )
    if not checkpoint_restore_verified:
        decision = {
            "status": "INVALID_RUN_FAIL_CLOSED",
            "reason": "CHECKPOINT_RESTORE_VERIFICATION_FAILED",
            "gate_checks": {},
        }
    final = {
        **decision,
        "sequential_stop_action": terminal_action,
        "producer_source_sha": source_sha,
        "frozen_contract_sha256": frozen_hash,
        "strict_evaluated_count": len(candidate_rows),
        "pair_count": len(pair_rows),
        "raw_pair_attempts": sum(attempts.values()),
        "active_wall_seconds": elapsed(),
        "workers_final": workers,
        "checkpoint_restore_verified": checkpoint_restore_verified,
        "completed_tranches": len(decision_rows),
        "continuation_decisions": [
            {
                "completed_tranche": row["completed_tranche"],
                "decision": row["decision"],
            }
            for row in decision_rows
        ],
        "sealed_reads": 0,
        "next_search_started": False,
        "temporal_evolution_authorized": False,
    }
    engine._write_json(runtime_root / "final_decision.json", final)
    manifest_files = [
        "frozen_contract.json",
        "search_authority_binding_receipt.json",
        "paired_proposal_ledger.parquet",
        "candidate_ledger.parquet",
        "paired_economic_diagnostics.parquet",
        "rejected_pair_ledger.parquet",
        "template_primitive_exposure.parquet",
        "economic_waterfall.parquet",
        "block_robustness.parquet",
        "lcb_distribution.parquet",
        "final_decision.json",
    ]
    manifest_files.extend(
        path.relative_to(runtime_root).as_posix()
        for path in sorted(runtime_root.glob("continuation_decision_*.json"))
    )
    manifest_files.extend(
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
                "sha256": _sha256_file(runtime_root / value),
                "bytes": (runtime_root / value).stat().st_size,
            }
            for value in manifest_files
        ],
    }
    run_manifest["bundle_sha256"] = _json_sha(run_manifest["files"])
    engine._write_json(runtime_root / "run_manifest.json", run_manifest)
    report_lines = [
        "# Crypto Search Core V3 Canonical Temporal Primitive Activation",
        "",
        f"Research decision: `{final['status']}`.",
        "",
        f"This development-only sequential paired gate completed {len(pair_rows):,} "
        f"static/temporal pairs across {len(decision_rows)} tranche(s) under identical fields, "
        "outer mechanisms, target, mapping, 4h horizon, dual controls, and 5 bps cost.",
        "",
        f"- Native paired delta median: `{final.get('metrics', {}).get('native_paired_delta_median')}`",
        f"- Common-support paired delta median: `{final.get('metrics', {}).get('common_support_paired_delta_median')}`",
        f"- Native temporal win fraction: `{final.get('metrics', {}).get('native_temporal_win_fraction')}`",
        f"- Static/temporal dual-axis net-positive rates: `{final.get('metrics', {}).get('static_dual_axis_net_positive_rate')}` / `{final.get('metrics', {}).get('temporal_dual_axis_net_positive_rate')}`",
        f"- Static/temporal 2-of-3 rates: `{final.get('metrics', {}).get('static_replicated_2_of_3_rate')}` / `{final.get('metrics', {}).get('temporal_replicated_2_of_3_rate')}`",
        f"- Static/temporal 3-of-3 counts: `{final.get('metrics', {}).get('static_all_three_count')}` / `{final.get('metrics', {}).get('temporal_all_three_count')}`",
        f"- Static/temporal matched-positive counts: `{final.get('metrics', {}).get('static_matched_positive_count')}` / `{final.get('metrics', {}).get('temporal_matched_positive_count')}`",
        f"- Static/temporal cost-sign-kill rates: `{final.get('metrics', {}).get('static', {}).get('cost_sign_kill_rate')}` / `{final.get('metrics', {}).get('temporal', {}).get('cost_sign_kill_rate')}`",
        f"- Positive template/primitive medians: `{final.get('metrics', {}).get('template_delta_medians')}` / `{final.get('metrics', {}).get('primitive_delta_medians')}`",
        f"- Field-family paired-delta medians: `{final.get('metrics', {}).get('field_family_delta_medians')}`",
        f"- Top template/primitive positive-delta shares: `{final.get('metrics', {}).get('top_template_positive_delta_share')}` / `{final.get('metrics', {}).get('top_primitive_positive_delta_share')}`",
        f"- Static/temporal worst-axis net-LCB p90: `{final.get('metrics', {}).get('static', {}).get('worst_axis_net_lcb_p90')}` / `{final.get('metrics', {}).get('temporal', {}).get('worst_axis_net_lcb_p90')}`",
        f"- Sequential stop action: `{terminal_action}`.",
        "",
        "## Sequential decisions",
        "",
        *[
            f"- Tranche {row['completed_tranche']}: `{row['decision']}`; "
            f"new-tranche native delta median="
            f"`{row.get('current_tranche_native_paired_delta_median')}`; "
            f"marginal={row.get('marginal_progress')}"
            for row in decision_rows
        ],
        "",
        "No validation, OOS, promotion, optimizer feedback, or non-gated budget expansion was performed.",
    ]
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    engine._write_json(
        runtime_root / "producer_status.json",
        {
            "status": "COMPLETE",
            "producer_source_sha": source_sha,
            "strict_evaluated": len(candidate_rows),
            "strict_maximum": int(budget["strict_evaluated_maximum"]),
            "completed_tranches": len(decision_rows),
            "active_wall_seconds": elapsed(),
            "workers": workers,
            "heartbeat_utc": pd.Timestamp.now(tz="UTC").isoformat(),
        },
    )
    return final


def check(
    repo_root: Path,
    *,
    runtime_date: str,
    require_consumed: bool = False,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    runtime_root = repo_root / f"runtime/{CAMPAIGN}_{runtime_date}"
    errors: list[str] = []
    required = (
        "frozen_contract.json",
        "search_authority_binding_receipt.json",
        "paired_proposal_ledger.parquet",
        "candidate_ledger.parquet",
        "paired_economic_diagnostics.parquet",
        "template_primitive_exposure.parquet",
        "economic_waterfall.parquet",
        "block_robustness.parquet",
        "lcb_distribution.parquet",
        "checkpoints/checkpoint_000/manifest.json",
        "final_decision.json",
        "run_manifest.json",
    )
    for value in required:
        if not (runtime_root / value).is_file():
            errors.append(f"missing:{value}")
    if errors:
        return {"status": "FAIL", "errors": errors}
    frozen = engine._read_json(runtime_root / "frozen_contract.json")
    final = engine._read_json(runtime_root / "final_decision.json")
    try:
        _validate_config(dict(frozen.get("config") or {}))
    except (KeyError, TypeError, ValueError):
        errors.append("frozen_research_boundary")
    pairs = pd.read_parquet(runtime_root / "paired_proposal_ledger.parquet")
    candidates = pd.read_parquet(runtime_root / "candidate_ledger.parquet")
    diagnostics = pd.read_parquet(
        runtime_root / "paired_economic_diagnostics.parquet"
    )
    pair_count = len(pairs)
    strict_count = len(candidates)
    completed_tranches = int(final.get("completed_tranches", -1))
    if pair_count not in {1_024, 2_048, 3_072, 4_096}:
        errors.append("pair_count")
    if strict_count != pair_count * 2:
        errors.append("strict_count")
    if len(diagnostics) != pair_count:
        errors.append("diagnostic_count")
    if candidates["candidate_id"].nunique() != strict_count:
        errors.append("candidate_exact_uniqueness")
    if pairs["paired_proposal_id"].nunique() != pair_count:
        errors.append("pair_uniqueness")
    if set(pairs["paired_proposal_id"]) != set(diagnostics["paired_proposal_id"]):
        errors.append("diagnostic_pair_join")
    candidate_pair_counts = candidates.groupby("paired_proposal_id")[
        "representation"
    ].agg(lambda values: tuple(sorted(values)))
    if any(value != ("static", "temporal") for value in candidate_pair_counts):
        errors.append("pair_representation_one_to_one")
    if set(candidates["representation"]) != {"static", "temporal"}:
        errors.append("representation_balance")
    expected_family = {
        "T1_POSITION_STATE_CHANGE": 256,
        "T2_FLOW_SHOCK_LIFECYCLE": 256,
        "T3_CROWDING_TRANSITION": 256,
        "T4_MULTI_SCALE_DISLOCATION": 256,
    }
    for _, tranche in pairs.groupby("tranche_index"):
        if dict(tranche["temporal_family_id"].value_counts()) != expected_family:
            errors.append("family_quota")
    if set(pairs["primitive_id"]) - set(ALLOWED_PRIMITIVES):
        errors.append("primitive_scope")
    if final.get("strict_evaluated_count") != strict_count:
        errors.append("final_strict_count")
    if completed_tranches != pair_count // 1_024:
        errors.append("completed_tranches")
    if final.get("checkpoint_restore_verified") is not True:
        errors.append("checkpoint_restore")
    if final.get("sealed_reads") != 0:
        errors.append("sealed_reads")
    if frozen.get("source_sha") != final.get("producer_source_sha"):
        errors.append("source_sha")
    if subprocess.check_output(
        ["git", "branch", "--show-current"], cwd=repo_root, text=True
    ).strip() != "experiment/crypto-search-evidence-v1-1-20260805":
        errors.append("branch")
    runtime_receipt = engine._read_json(
        runtime_root / "search_authority_binding_receipt.json"
    )
    if (
        runtime_receipt.get("budget") != frozen.get("config", {}).get("search_budget")
        or runtime_receipt.get("boundaries")
        != frozen.get("config", {}).get("boundaries")
    ):
        errors.append("runtime_receipt_scope")
    if _json_sha(runtime_receipt) != frozen.get("binding_receipt_sha256"):
        errors.append("runtime_receipt")
    source_sha = str(final.get("producer_source_sha") or "")
    for component, expected_hash in runtime_receipt["component_sha256"].items():
        try:
            committed = subprocess.check_output(
                ["git", "show", f"{source_sha}:{component}"], cwd=repo_root
            )
        except subprocess.CalledProcessError:
            errors.append(f"source_blob_missing:{component}")
            continue
        if hashlib.sha256(committed).hexdigest().upper() != expected_hash:
            errors.append(f"source_blob:{component}")
        if (repo_root / component).read_bytes() != committed:
            errors.append(f"working_blob:{component}")
    expression_source = (repo_root / "alphafactory_crypto/broad_search/expression.py").read_text(
        encoding="utf-8"
    )
    if expression_source.count("evaluate_primitive(") != 1:
        errors.append("adapter_authority_call")
    for row in pairs.to_dict("records"):
        static = CandidateSpec.from_dict(json.loads(row["static_candidate_spec_json"]))
        temporal = CandidateSpec.from_dict(json.loads(row["temporal_candidate_spec_json"]))
        temporal_nodes = _operator_nodes(temporal.expression, CANONICAL_PRIMITIVE_OPERATOR)
        control_nodes = _operator_nodes(temporal.control, CANONICAL_PRIMITIVE_OPERATOR)
        if len(temporal_nodes) != 1 or len(control_nodes) != 1:
            errors.append("primitive_node_count")
            break
        if temporal_nodes[0].parameters != control_nodes[0].parameters:
            errors.append("control_temporal_transform")
            break
        lineage = temporal.generation_genes.get("paired_lineage", {})
        if (
            lineage.get("paired_static_candidate_id") != static.candidate_id
            or lineage.get("paired_proposal_id") != row["paired_proposal_id"]
            or static.raw_fields != temporal.raw_fields
            or static.mapping_id != temporal.mapping_id
            or static.horizon_hours != temporal.horizon_hours
            or static.generation_genes["mechanism_spec"]
            != temporal.generation_genes["mechanism_spec"]
        ):
            errors.append("paired_identity_or_shared_contract")
            break
    decision_rows: list[dict[str, Any]] = []
    for checkpoint_index in range(completed_tranches):
        strict_at_checkpoint = (checkpoint_index + 1) * 2_048
        decision_path = runtime_root / (
            f"continuation_decision_{strict_at_checkpoint:06d}.json"
        )
        checkpoint_path = (
            runtime_root / "checkpoints" / f"checkpoint_{checkpoint_index:03d}"
        )
        if not decision_path.is_file() or not checkpoint_path.is_dir():
            errors.append("sequential_artifact_missing")
            continue
        actual = engine._read_json(decision_path)
        recomputed = continuation_decision(
            diagnostics.iloc[: (checkpoint_index + 1) * 1_024].to_dict("records"),
            candidates.iloc[: (checkpoint_index + 1) * 2_048].to_dict("records"),
            completed_tranche=checkpoint_index,
            prior_decisions=decision_rows,
        )
        for key in (
            "decision",
            "completed_tranche",
            "strict_evaluated_count",
            "cumulative",
            "marginal_progress",
            "no_boundary_progress",
            "continuation_checks",
            "concentration",
        ):
            if actual.get(key) != recomputed.get(key):
                errors.append(f"decision_recompute:{checkpoint_index}:{key}")
        if checkpoint_index < completed_tranches - 1 and actual.get("decision") != "CONTINUE":
            errors.append("proposal_after_stop")
        manifest_at_checkpoint = engine._read_json(checkpoint_path / "manifest.json")
        if any(
            _sha256_file(checkpoint_path / row["path"]) != row["sha256"]
            for row in manifest_at_checkpoint["files"]
        ):
            errors.append(f"checkpoint_snapshot:{checkpoint_index}")
        decision_rows.append(actual)
    observed = classify_results(
        diagnostics.to_dict("records"),
        candidates.to_dict("records"),
        expected_pairs=pair_count,
    )
    if final.get("status") not in {
        observed.get("status"),
        "EARLY_STOP_TEMPORAL_FUTILITY",
    } or observed.get("gate_checks") != final.get("gate_checks"):
        errors.append("final_decision_recompute")
    if not _process_evidence_closed(runtime_root):
        errors.append("process_evidence")
    local_receipt = engine._read_json(repo_root / BINDING_RECEIPT_PATH)
    if require_consumed and (
        local_receipt.get("run_authorized") is not False
        or local_receipt.get("status") != "CONSUMED"
        or local_receipt.get("run_outcome", {}).get("runtime_date") != runtime_date
    ):
        errors.append("receipt_not_consumed")
    manifest = engine._read_json(runtime_root / "run_manifest.json")
    for row in manifest["files"]:
        if _sha256_file(runtime_root / row["path"]) != row["sha256"]:
            errors.append(f"manifest:{row['path']}")
    result = {
        "schema_version": 1,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "producer_source_sha": final.get("producer_source_sha"),
        "research_decision": final.get("status"),
        "strict_evaluated_count": strict_count,
        "pair_count": pair_count,
        "completed_tranches": completed_tranches,
        "sealed_reads": final.get("sealed_reads"),
        "receipt_consumption_required": bool(require_consumed),
    }
    engine._write_json(runtime_root / "independent_checker.json", result)
    return result


def consume_binding_receipt(repo_root: Path, *, runtime_date: str) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    path = repo_root / BINDING_RECEIPT_PATH
    receipt = engine._read_json(path)
    if (
        receipt.get("status") != "RUN_AUTHORIZED_DEVELOPMENT_ONLY"
        or receipt.get("run_authorized") is not True
        or "run_outcome" in receipt
    ):
        raise RuntimeError("temporal binding receipt is not consumable")
    runtime_root = repo_root / f"runtime/{CAMPAIGN}_{runtime_date}"
    final = engine._read_json(runtime_root / "final_decision.json")
    manifest = engine._read_json(runtime_root / "run_manifest.json")
    consumed = {
        **receipt,
        "status": "CONSUMED",
        "run_authorized": False,
        "run_outcome": {
            "runtime_date": runtime_date,
            "producer_source_sha": final["producer_source_sha"],
            "research_decision": final["status"],
            "strict_evaluated_count": final["strict_evaluated_count"],
            "completed_tranches": final["completed_tranches"],
            "run_manifest_bundle_sha256": manifest["bundle_sha256"],
        },
    }
    engine._write_json(path, consumed)
    return {
        "status": "CONSUMED",
        "receipt_sha256": _json_sha(consumed),
        "research_decision": final["status"],
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        choices=("freeze-receipt", "source-smoke", "run", "check", "consume-receipt"),
    )
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--runtime-date", default="20260806")
    parser.add_argument("--source-sha")
    parser.add_argument("--require-consumed", action="store_true")
    parser.add_argument("--smoke-evidence-root", type=Path)
    args = parser.parse_args(argv)
    if args.command == "freeze-receipt":
        receipt_path = args.repo_root.resolve() / BINDING_RECEIPT_PATH
        if receipt_path.exists():
            raise FileExistsError("temporal binding receipt already exists")
        payload = binding_receipt_payload(args.repo_root.resolve())
        engine._write_json(
            args.repo_root.resolve() / BINDING_RECEIPT_PATH,
            payload,
        )
        result = {"status": "RECEIPT_FROZEN", "receipt_sha256": _json_sha(payload)}
    elif args.command == "source-smoke":
        if args.smoke_evidence_root is None:
            raise ValueError("source-smoke requires --smoke-evidence-root")
        result = source_smoke(
            args.repo_root, evidence_root=args.smoke_evidence_root
        )
    elif args.command == "run":
        result = run(
            args.repo_root,
            runtime_date=str(args.runtime_date),
            source_sha=args.source_sha,
        )
    elif args.command == "check":
        result = check(
            args.repo_root,
            runtime_date=str(args.runtime_date),
            require_consumed=bool(args.require_consumed),
        )
    else:
        result = consume_binding_receipt(
            args.repo_root, runtime_date=str(args.runtime_date)
        )
    print(json.dumps(result, indent=2, sort_keys=True), flush=True)
    return 0 if result.get("status") not in {"FAIL", "INVALID_RUN_FAIL_CLOSED"} else 1


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "binding_receipt_payload",
    "check",
    "classify_results",
    "consume_binding_receipt",
    "continuation_decision",
    "propose_pair",
    "run",
    "source_smoke",
]
