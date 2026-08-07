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
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd
import psutil

from . import search_engine_v1 as engine
from .compositional18m import CandidateSpec, MechanismSpec, mechanism_role_domains
from .experiment_authority import resolve_search_economic_receipt
from .expression import FieldContract, TypedExpressionRegistry
from .pair18m import ControlBehaviorDegeneracyError, evaluate_pair
from .temporal_activation_v1 import _paired_common_support
from .temporal_program_v1 import (
    PROGRAM_BUILDER_ID,
    TemporalProgramSpec,
    compile_temporal_program_catalog,
    program_catalog_payload,
    static_counterpart,
)


CONFIG_PATH = "config/crypto_temporal_mechanism_program_v1.json"
RECEIPT_PATH = "config/crypto_temporal_mechanism_program_v1_receipt.json"
CAMPAIGN = "crypto_temporal_mechanism_program_v1"
BLOCK_ROLE = "DEVELOPMENT_ONLY_TEMPORAL_MECHANISM_PROGRAM_SEARCH"
REPORT_PREFIX = "CRYPTO_TEMPORAL_MECHANISM_PROGRAM_SEARCH_V1"
ARMS = (
    "temporal_program_random",
    "temporal_program_cem",
    "temporal_program_evolution",
)
COMPONENT_PATHS = (
    "alphafactory_crypto/broad_search/expression.py",
    "alphafactory_crypto/broad_search/compositional18m.py",
    "alphafactory_crypto/broad_search/search_engine_v1.py",
    "alphafactory_crypto/broad_search/temporal_program_v1.py",
    "alphafactory_crypto/broad_search/temporal_program_search_v1.py",
    "scripts/run_crypto_temporal_mechanism_program_v1_pc2.ps1",
    CONFIG_PATH,
)


class ProgramBudgetExhausted(RuntimeError):
    pass


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
    if config.get("experiment_id") != (
        "CRYPTO_SEARCH_CORE_V4_TEMPORAL_MECHANISM_PROGRAM_V1_20260807"
    ):
        raise ValueError("temporal program experiment identity changed")
    if config.get("authorization") != (
        "ONE_FRESH_STATE_SEQUENTIAL_UP_TO_50000_STRICT_TEMPORAL_PROGRAM_DEVELOPMENT_CAMPAIGN"
    ):
        raise PermissionError("temporal program authorization changed")
    expected_budget = {
        "strict_evaluated_maximum": 50_000,
        "raw_generation_attempts_maximum": 250_000,
        "wall_time_seconds_maximum": 64_800,
        "checkpoint_size": 2_000,
        "checkpoint_count_maximum": 25,
        "workers_default": 10,
        "workers_memory_fallback": 8,
    }
    if any(int(budget.get(key, -1)) != value for key, value in expected_budget.items()):
        raise ValueError("temporal program budget changed")
    if (
        budget.get("release_boundaries_strict")
        != [10_000, 20_000, 30_000, 40_000, 50_000]
        or budget.get("workers_12_forbidden") is not True
        or budget.get("automatic_release_only_through_frozen_gate") is not True
        or budget.get("later_tranche_proposal_pregeneration") is not False
    ):
        raise ValueError("temporal program sequential release contract changed")
    seeds = tuple(int(value) for value in config["seed_authority"]["seeds"])
    if seeds != (2594819233, 4246332867, 3389304867, 168281835):
        raise ValueError("temporal program seed authority changed")
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
    if receipt.get("config_sha256") != _sha256_file(repo_root / CONFIG_PATH):
        raise RuntimeError("temporal program receipt config changed")
    component_hashes = dict(receipt.get("component_sha256") or {})
    if set(component_hashes) != set(COMPONENT_PATHS) or any(
        _sha256_file(repo_root / path) != str(component_hashes[path])
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


def source_smoke(repo_root: Path) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    config = engine._read_json(repo_root / CONFIG_PATH)
    validate_config(config)
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
    except (ValueError, FloatingPointError) as failure:
        status = "PAIR_REJECTED"
        error = type(failure).__name__ + ":" + str(failure)
        evaluations = {}
        common = None
    memory = process.memory_info()
    return {
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
) -> dict[str, Any]:
    frame = pd.DataFrame(list(ledger))
    tranche_start = max(10_000, int(strict_boundary) - 10_000)
    frame = frame.loc[
        (frame["completion_ordinal"].astype(int) > tranche_start)
        & (frame["completion_ordinal"].astype(int) <= int(strict_boundary))
    ]
    random_count = int((frame["arm"].astype(str) == ARMS[0]).sum())
    decisions: dict[str, Any] = {}
    updated_states = dict(state["arm_states"])
    for arm in ARMS[1:]:
        arm_count = int((frame["arm"].astype(str) == arm).sum())
        common = min(random_count, arm_count)
        if common <= 0:
            decisions[arm] = {"decision": "NO_OBSERVATIONS", "same_count": 0}
            continue
        random_rows = _arm_slice(frame, ARMS[0], common)
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
                "top_program_family_positive_share": (
                    float(family_positive.max() / family_positive.sum())
                    if len(family_positive)
                    else 0.0
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
        breadth = bool(
            observed["behavior_family_count"]
            >= 0.8 * control["behavior_family_count"]
            and observed["top_program_family_positive_share"] <= 0.6
        )
        incremental = any(quality) and any(productivity) and breadth
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
            "breadth_pass": breadth,
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


def _checkpoint_allocation(state: Mapping[str, Any], checkpoint_index: int) -> dict[str, int]:
    if checkpoint_index < 5:
        return {"paired_static": 1_000, "temporal_program_random": 1_000}
    states = dict(state["arm_states"])
    allocation = {ARMS[0]: 400, ARMS[1]: 0, ARMS[2]: 0}
    diagnostic = [arm for arm in ARMS[1:] if states.get(arm) == "DIAGNOSTIC"]
    active = [arm for arm in ARMS[1:] if states.get(arm) == "ACTIVE"]
    for arm in diagnostic:
        allocation[arm] = 200
    remaining = 2_000 - sum(allocation.values())
    if active:
        share = remaining // len(active)
        for arm in active:
            allocation[arm] = share
        allocation[active[0]] += 2_000 - sum(allocation.values())
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
        "workers": int(config["search_budget"]["workers_default"]),
        "memory_fallback_used": False,
        "wall_elapsed_seconds": 0.0,
        "arm_states": {ARMS[1]: "ACTIVE", ARMS[2]: "ACTIVE"},
        "active_program_families": [],
        "failure_counts": {},
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
            (frame["completion_ordinal"].astype(int) > 10_000)
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
            "strict_maximum": 50_000,
            "generation_attempts": int(state["generation_attempts"]),
            "active_wall_seconds": active_elapsed,
            "observed_strict_per_hour": strict_count * 3600.0 / max(active_elapsed, 1.0),
            "workers": int(state["workers"]),
            "active_program_families": list(state["active_program_families"]),
            "arm_states": dict(state["arm_states"]),
        },
    )


def run(repo_root: Path, *, runtime_date: str, source_sha: str | None = None) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    config = engine._read_json(repo_root / CONFIG_PATH)
    validate_config(config)
    receipt = validate_receipt(repo_root, config=config, require_authorized=True)
    observed_sha = engine._git_sha(repo_root)
    source_sha = str(source_sha or observed_sha).lower()
    if source_sha != observed_sha:
        raise RuntimeError("temporal program producer SHA differs from checkout")
    runtime_root = repo_root / f"runtime/{CAMPAIGN}_{runtime_date}"
    report_path = repo_root / f"reports/{REPORT_PREFIX}_{runtime_date}.md"
    if not engine._source_tree_clean_for_run(
        repo_root, allowed_paths=(runtime_root, report_path)
    ):
        raise RuntimeError("temporal program producer tree is not clean")
    economic = resolve_search_economic_receipt(
        repo_root, str(config["source_authorities"]["economic_receipt_template"])
    )
    train = dict(economic["evidence_partition"]["train"])
    store, contracts, behavior, identities, _ = engine._load_v14_inputs(
        repo_root, behavior_window=train
    )
    if len(contracts) != 115:
        raise RuntimeError("temporal program carrier contract changed")
    registry = TypedExpressionRegistry(contracts, **_limits(config))
    catalog = compile_temporal_program_catalog(config)
    catalog_payload = program_catalog_payload(catalog)
    block_config = engine._read_json(
        repo_root / str(config["source_authorities"]["development_blocks_config"])
    )
    block_contract = dict(block_config["block_robust_contract"])
    compiler_identity = engine._compiler_binding(repo_root)
    identities = {**identities, "compiler_identity": compiler_identity}
    frozen = {
        "schema_version": 1,
        "experiment_id": config["experiment_id"],
        "source_sha": source_sha,
        "config": config,
        "receipt_sha256": receipt["receipt_sha256"],
        "economic_receipt": economic,
        "input_identities": identities,
        "behavior_contract_sha256": _json_sha(behavior),
        "compiler_identity": compiler_identity,
        "program_catalog_sha256": catalog_payload["catalog_sha256"],
        "block_robust_contract": block_contract,
        "expression_registry_limits": _limits(config),
        "sealed_reads": 0,
    }
    frozen_hash = _json_sha(frozen)
    frozen = {**frozen, "frozen_contract_sha256": frozen_hash}
    if runtime_root.exists():
        if engine._read_json(runtime_root / "frozen_contract.json") != frozen:
            raise RuntimeError("temporal program runtime contract changed")
        if (runtime_root / "final_decision.json").is_file():
            raise FileExistsError("temporal program campaign already completed")
    else:
        runtime_root.mkdir(parents=True)
        engine._write_json(runtime_root / "frozen_contract.json", frozen)
        engine._write_json(runtime_root / "program_catalog.json", catalog_payload)
        engine._write_json(runtime_root / "search_authority_binding_receipt.json", receipt)
        engine._write_json(runtime_root / "embedded_preflight.json", source_smoke(repo_root))

    if (runtime_root / "checkpoints/checkpoint_budget_exhausted").is_dir():
        raise RuntimeError("budget-exhausted runtime cannot be resumed")
    checkpoints = sorted((runtime_root / "checkpoints").glob("checkpoint_[0-9][0-9][0-9]"))
    if checkpoints:
        state, policies, ledger, archive, pair_rows, metrics, rejected = _load_checkpoint(
            checkpoints[-1],
            registry=registry,
            expected_source=source_sha,
            expected_frozen=frozen_hash,
            expected_identities=identities,
        )
    else:
        state = _new_state(source_sha, frozen_hash, config)
        policies = _stage0_policies(registry=registry, config=config, catalog=catalog)
        ledger: list[dict[str, Any]] = []
        archive = engine.BehaviorArchive()
        pair_rows: list[dict[str, Any]] = []
        metrics: list[dict[str, Any]] = []
        rejected: list[dict[str, Any]] = []
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
                None,
                _limits(config),
            ),
        )

    executor: concurrent.futures.ProcessPoolExecutor | None = None
    terminal_reason: str | None = None
    try:
        executor = make_executor(int(state["workers"]))
        _write_status(runtime_root, state=state, status="RUNNING", active_elapsed=elapsed())
        for checkpoint_index in range(int(state["next_checkpoint_index"]), 25):
            checkpoint_start = len(ledger)
            checkpoint_target = checkpoint_start + 2_000
            if checkpoint_index < 5:
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
                    enforce_budget()
                    batch: list[dict[str, Any]] = []
                    for key in ordered_lanes:
                        while (
                            lane_completed[key]
                            + sum(item["policy_key"] == key for item in batch)
                            < lane_targets[key]
                            and len(batch) < max(1, int(state["workers"]) // 2)
                        ):
                            policy = policies[key]
                            proposal_cpu = time.process_time()
                            try:
                                temporal, metadata = policy.propose()
                                static = static_counterpart(registry, temporal)
                            except (ValueError, RuntimeError) as failure:
                                state["generation_attempts"] += 1
                                rejected.append(
                                    {
                                        "checkpoint_index": checkpoint_index,
                                        "policy_key": key,
                                        "status": "PROPOSAL_REJECT",
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
                                        "temporal_candidate_id": temporal.candidate_id,
                                        "static_candidate_id": static.candidate_id,
                                    }
                                )
                                continue
                            attempted.update((temporal.candidate_id, static.candidate_id))
                            pair_id = _json_sha([static.candidate_id, temporal.candidate_id])
                            if pair_id in completed_pairs:
                                continue
                            _, family, seed_text = key.split("|", 2)
                            batch.append(
                                {
                                    "policy_key": key,
                                    "seed": int(seed_text),
                                    "program_family_id": family,
                                    "program_id": str(temporal.generation_genes["program_id"]),
                                    "paired_program_id": pair_id,
                                    "static": static,
                                    "temporal": temporal,
                                    "metadata": metadata,
                                    "proposal_cpu_seconds": time.process_time() - proposal_cpu,
                                }
                            )
                    if not batch:
                        continue
                    assert executor is not None
                    futures = {
                        executor.submit(
                            _worker_program_pair,
                            {
                                "paired_program_id": item["paired_program_id"],
                                "static": item["static"].to_dict(),
                                "temporal": item["temporal"].to_dict(),
                            },
                        ): item
                        for item in batch
                    }
                    results = [(futures[future], future.result()) for future in concurrent.futures.as_completed(futures)]
                    if any(result["memory_error"] for _, result in results):
                        if int(state["workers"]) == int(budget["workers_default"]):
                            executor.shutdown(wait=True)
                            state["workers"] = int(budget["workers_memory_fallback"])
                            state["memory_fallback_used"] = True
                            executor = make_executor(int(state["workers"]))
                            retry_items = [item for item, result in results if result["memory_error"]]
                            retry = {
                                executor.submit(
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
                    _write_status(runtime_root, state=state, status="RUNNING", active_elapsed=elapsed())
            else:
                allocation = _checkpoint_allocation(state, checkpoint_index)
                targets = _later_checkpoint_targets(allocation, config)
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
                        actual_policy_key = policy_key
                        if arm == ARMS[0] and state["active_program_families"] and any(
                            pair[1].family_id not in set(state["active_program_families"])
                            for pair in catalog
                        ):
                            local_index = completed_by_lane[key] + sum(row["policy_key"] == key for row in proposals)
                            if local_index % 10 == 9:
                                actual_policy_key = f"temporal_program_random_diagnostic|{seed_text}"
                        policy = policies[actual_policy_key]
                        proposal_cpu = time.process_time()
                        try:
                            candidate, metadata = engine._policy_propose(policy, archive)
                        except (ValueError, RuntimeError) as failure:
                            state["generation_attempts"] += int(getattr(failure, "raw_attempts", 1))
                            rejected.append(
                                {
                                    "checkpoint_index": checkpoint_index,
                                    "policy_key": actual_policy_key,
                                    "status": "PROPOSAL_REJECT",
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
                                "proposal_cpu_seconds": time.process_time() - proposal_cpu,
                            }
                        )
                    if not proposals:
                        continue
                    assert executor is not None
                    futures = {
                        executor.submit(engine._worker_evaluate, row["candidate"].to_dict()): row
                        for row in proposals
                    }
                    results = [(futures[future], future.result()) for future in concurrent.futures.as_completed(futures)]
                    if any(result["memory_error"] for _, result in results):
                        if int(state["workers"]) == int(budget["workers_default"]):
                            executor.shutdown(wait=True)
                            state["workers"] = int(budget["workers_memory_fallback"])
                            state["memory_fallback_used"] = True
                            executor = make_executor(int(state["workers"]))
                            retry_rows = [row for row, result in results if result["memory_error"]]
                            retry = {
                                executor.submit(engine._worker_evaluate, row["candidate"].to_dict()): row
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
                        policies[key].update(local)
            metrics.extend(
                _checkpoint_metrics(checkpoint_index=checkpoint_index, ledger=ledger, state=state)
            )
            state["next_checkpoint_index"] = checkpoint_index + 1
            state["attempted_exact_ids"] = sorted(attempted)
            state["completed_pair_ids"] = sorted(completed_pairs)
            state["wall_elapsed_seconds"] = elapsed()
            if checkpoint_index == 4:
                decision = stage0_family_decisions(pair_rows, config)
                engine._write_json(runtime_root / "continuation_decision_010000.json", decision)
                if decision["status"] != "CONTINUE":
                    terminal_reason = decision["status"]
                else:
                    state["active_program_families"] = list(decision["continuing_families"])
                    policies = _later_policies(
                        registry=registry,
                        config=config,
                        catalog=catalog,
                        active_families=state["active_program_families"],
                    )
            elif checkpoint_index in {9, 14, 19}:
                boundary = (checkpoint_index + 1) * 2_000
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
            )
            observed_rate = len(ledger) * 3600.0 / max(elapsed(), 1.0)
            if checkpoint_index >= 0 and observed_rate < float(budget["minimum_strict_per_hour_after_first_checkpoint"]):
                terminal_reason = "ENGINE_BUDGET_EXHAUSTED_THROUGHPUT_FLOOR"
            _write_status(runtime_root, state=state, status="RUNNING", active_elapsed=elapsed())
            if terminal_reason:
                break
    except ProgramBudgetExhausted as failure:
        terminal_reason = "ENGINE_BUDGET_EXHAUSTED:" + str(failure)
    finally:
        if executor is not None:
            executor.shutdown(wait=True, cancel_futures=False)

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
    if (
        terminal_reason
        and terminal_reason.startswith("ENGINE_BUDGET_EXHAUSTED")
        and len(ledger) > int(state["next_checkpoint_index"]) * 2_000
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
    strict_count = len(ledger)
    matched = [row for row in ledger if bool(row["matched_positive"])]
    matched_families = {str(row["behavior_family_id"]) for row in matched}
    contributing = {str(row["program_family_id"]) for row in matched}
    if terminal_reason and terminal_reason.startswith("ENGINE_BUDGET_EXHAUSTED"):
        status = "ENGINE_BUDGET_EXHAUSTED"
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
        "status": status,
        "terminal_reason": terminal_reason,
        "producer_source_sha": source_sha,
        "frozen_contract_sha256": frozen_hash,
        "strict_evaluated_count": strict_count,
        "generation_attempts": int(state["generation_attempts"]),
        "checkpoint_count": int(state["next_checkpoint_index"])
        + int(budget_checkpoint_written),
        "completed_full_checkpoint_count": int(state["next_checkpoint_index"]),
        "budget_checkpoint_written": budget_checkpoint_written,
        "active_wall_seconds": elapsed(),
        "workers_final": int(state["workers"]),
        "memory_fallback_used": bool(state["memory_fallback_used"]),
        "behavior_family_count": len(archive.champion_by_family),
        "matched_positive_count": len(matched),
        "matched_positive_behavior_family_count": len(matched_families),
        "matched_positive_program_family_count": len(contributing),
        "active_program_families": list(state["active_program_families"]),
        "arm_states": dict(state["arm_states"]),
        "sealed_reads": 0,
        "validation": False,
        "oos": False,
        "promotion": False,
        "automatic_next_run_started": False,
        "parameters_changed": False,
        "seed_changed": False,
        "rescue_rerun_started": False,
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
    manifest_paths.extend(
        path.relative_to(runtime_root).as_posix()
        for path in sorted(runtime_root.glob("continuation_decision_*.json"))
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
    report_path.write_text(
        "\n".join(
            [
                "# Crypto Temporal Mechanism Program Search V1",
                "",
                f"- Decision: `{status}`",
                f"- Strict evaluated: `{strict_count:,}`",
                f"- Raw generation attempts: `{state['generation_attempts']:,}`",
                f"- Behavior families: `{len(archive.champion_by_family):,}`",
                f"- Matched-positive candidates/families: `{len(matched)}` / `{len(matched_families)}`",
                f"- Contributing program families: `{sorted(contributing)}`",
                f"- Stage-0 continuing families: `{state['active_program_families']}`",
                f"- Adaptive arm states: `{state['arm_states']}`",
                f"- Terminal reason: `{terminal_reason}`",
                "",
                "This is development-only evidence. No validation, OOS, promotion, target, mapping, cost, reward, AST, compiler, or evaluator change was performed.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    _write_status(runtime_root, state=state, status="COMPLETE", active_elapsed=elapsed())
    return final


def check(repo_root: Path, *, runtime_date: str, require_consumed: bool = False) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    runtime_root = repo_root / f"runtime/{CAMPAIGN}_{runtime_date}"
    errors: list[str] = []
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
    for value in required:
        if not (runtime_root / value).is_file():
            errors.append(f"missing:{value}")
    if errors:
        return {"status": "FAIL", "errors": errors}
    frozen = engine._read_json(runtime_root / "frozen_contract.json")
    final = engine._read_json(runtime_root / "final_decision.json")
    config = dict(frozen["config"])
    try:
        validate_config(config)
    except (KeyError, ValueError, PermissionError) as failure:
        errors.append("config:" + str(failure))
    ledger = pd.read_parquet(runtime_root / "candidate_ledger.parquet")
    pairs = pd.read_parquet(runtime_root / "paired_program_diagnostics.parquet")
    if len(ledger) != int(final["strict_evaluated_count"]):
        errors.append("strict_count")
    if len(ledger) >= 10_000:
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
    all_checkpoints = [*checkpoints, *([budget_checkpoint] if budget_checkpoint.is_file() else [])]
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
    manifest = engine._read_json(runtime_root / "run_manifest.json")
    for row in manifest["files"]:
        local = runtime_root / str(row["path"])
        if not local.is_file() or _sha256_file(local) != str(row["sha256"]):
            errors.append("manifest:" + str(row["path"]))
    receipt = validate_receipt(repo_root, config=config, require_authorized=False)
    if require_consumed and receipt.get("run_authorized") is not False:
        errors.append("receipt_not_consumed")
    result = {
        "schema_version": 1,
        "status": "PASS" if not errors else "FAIL",
        "errors": sorted(set(errors)),
        "producer_source_sha": final["producer_source_sha"],
        "strict_evaluated_count": len(ledger),
        "checkpoint_count": len(all_checkpoints),
        "stage0_pair_count": len(pairs),
        "sealed_reads": 0,
    }
    if result["status"] == "PASS":
        engine._write_json(runtime_root / "independent_checker.json", result)
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


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("run", "check", "consume-receipt"):
        command = sub.add_parser(name)
        command.add_argument("--repo-root", type=Path, required=True)
        command.add_argument("--runtime-date", required=True)
        if name == "run":
            command.add_argument("--source-sha")
        if name == "check":
            command.add_argument("--require-consumed", action="store_true")
    smoke = sub.add_parser("source-smoke")
    smoke.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "run":
        result = run(args.repo_root, runtime_date=args.runtime_date, source_sha=args.source_sha)
    elif args.command == "check":
        result = check(
            args.repo_root,
            runtime_date=args.runtime_date,
            require_consumed=bool(args.require_consumed),
        )
    elif args.command == "consume-receipt":
        result = consume_receipt(args.repo_root, runtime_date=args.runtime_date)
    else:
        result = source_smoke(args.repo_root)
    print(json.dumps(result, sort_keys=True, default=str))
    if args.command == "check" and result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()


__all__ = [
    "adaptive_gate",
    "check",
    "consume_receipt",
    "run",
    "source_smoke",
    "stage0_family_decisions",
    "validate_config",
]
