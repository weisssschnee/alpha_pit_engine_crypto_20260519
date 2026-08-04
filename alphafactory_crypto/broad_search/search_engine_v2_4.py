"""Behavior-family-first V2.4 selection and economic-path persistence.

This module is deliberately not a second search engine or evaluator.  It
contains the thin policy-selection and artifact projections needed by the next
fresh-data gate while delegating candidate economics to ``pair18m.evaluate_pair``.
No market run is authorized by the committed contract.
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
import tempfile
import time
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd
import psutil


V24_CONTRACT_PATH = "config/crypto_search_engine_v2_4_behavior_family.json"
V24_RUN_RECEIPT_PATH = "config/crypto_search_engine_v2_4_fresh_gate_receipt.json"
V24_RUNTIME_PREFIX = "crypto_search_engine_v2_4_fresh_gate"
V24_DEFAULT_RUNTIME_DATE = "20260803"
V24_REPAIR_RUN_RECEIPT_PATH = (
    "config/crypto_search_engine_v2_4_repair_replay_receipt.json"
)
V24_REPAIR_RUNTIME_PREFIX = "crypto_search_engine_v2_4_repair_replay"
V24_REPAIR_DEFAULT_RUNTIME_DATE = "20260804"
V24_SOURCE_LEDGER_PATH = (
    "runtime/crypto_search_mechanism_v2_3_20260802/candidate_ledger.parquet"
)
V24_SOURCE_ARM_MAPPING = {
    "expanded_mechanism_random_v2_3": "expanded_mechanism_random_v2_4",
    "mechanism_evolution_v2_3": "mechanism_evolution_v2_4",
}
V24_SELECTION_AUTHORITY = "TRAIN_SEARCH_REWARD_ONLY"
V24_FAMILY_KEY = (
    "arm",
    "seed",
    "horizon_hours",
    "behavior_family_id",
)
V24_CHAMPION_ORDER = (
    "search_reward_desc",
    "arm_completion_ordinal_asc",
    "candidate_id_asc",
)
V24_CANDIDATE_LOCAL_FAILURES = frozenset(
    {
        "CONTROL_EXACT_IDENTITY_EQUALS_PRIMARY",
        "CONTROL_BEHAVIOR_EQUALS_PRIMARY",
        "RIGHT_AXIS_CONTROL_BEHAVIOR_EQUALS_PRIMARY",
        "INTERACTION_LEFT_CONTROL_BEHAVIOR_EQUALS_AB",
        "MATCHED_CONTROL_SUPPORT_DIFFERS_PRIMARY",
        "RIGHT_AXIS_CONTROL_SUPPORT_DIFFERS_PRIMARY",
        "INTERACTION_LEFT_CONTROL_SUPPORT_DIFFERS_AB",
        "DYNAMIC_UNIVERSE_SUPPORT_COLLAPSE",
    }
)


def prepare_v24_train_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    source_arm_mapping: Mapping[str, str],
) -> list[dict[str, Any]]:
    """Relabel the two frozen V2.3 proposal arms without changing candidates."""

    mapping = {str(key): str(value) for key, value in source_arm_mapping.items()}
    if mapping != V24_SOURCE_ARM_MAPPING:
        raise RuntimeError("V24_SOURCE_ARM_MAPPING_CHANGED")
    observed = {str(row.get("arm") or "") for row in rows}
    if observed != set(mapping):
        raise RuntimeError("V24_SOURCE_ARM_SET_CHANGED")
    output: list[dict[str, Any]] = []
    candidate_ids: set[str] = set()
    for raw in rows:
        row = dict(raw)
        candidate_id = str(row.get("candidate_id") or "")
        if not candidate_id or candidate_id in candidate_ids:
            raise RuntimeError("V24_SOURCE_CANDIDATE_IDENTITY_CHANGED")
        candidate_ids.add(candidate_id)
        source_arm = str(row["arm"])
        row["source_arm"] = source_arm
        row["arm"] = mapping[source_arm]
        output.append(row)
    return output


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            default=str,
        ).encode("utf-8")
    ).hexdigest().upper()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def load_v24_run_receipt(
    repo_root: Path,
    *,
    require_authorized: bool = True,
) -> dict[str, Any]:
    """Load the separate one-run authority without changing source authority."""

    path = Path(repo_root) / V24_RUN_RECEIPT_PATH
    if not path.is_file():
        raise RuntimeError("V24_RUN_RECEIPT_MISSING")
    receipt = json.loads(path.read_text(encoding="utf-8-sig"))
    blockers: list[str] = []
    if receipt.get("schema_version") != 1:
        blockers.append("schema_version")
    if receipt.get("experiment_id") != (
        "crypto_search_engine_v2_4_fresh_family_gate"
    ):
        blockers.append("experiment_id")
    source = dict(receipt.get("source_train") or {})
    if source.get("candidate_ledger_path") != V24_SOURCE_LEDGER_PATH:
        blockers.append("source_train.candidate_ledger_path")
    ledger_path = Path(repo_root) / str(source.get("candidate_ledger_path") or "")
    if (
        not ledger_path.is_file()
        or _file_sha256(ledger_path)
        != str(source.get("candidate_ledger_sha256") or "")
        or int(source.get("candidate_ledger_row_count", -1)) != 16_000
    ):
        blockers.append("source_train.candidate_ledger")
    economic_path = Path(repo_root) / str(
        source.get("economic_receipt_path") or ""
    )
    if (
        not economic_path.is_file()
        or _file_sha256(economic_path)
        != str(source.get("economic_receipt_file_sha256") or "")
    ):
        blockers.append("source_train.economic_receipt")
    if dict(source.get("source_arm_mapping") or {}) != V24_SOURCE_ARM_MAPPING:
        blockers.append("source_train.source_arm_mapping")
    if any(
        source.get(field) is not False
        for field in (
            "candidate_generation_allowed",
            "adaptive_state_import_allowed",
            "validation_or_oos_feedback_selection_allowed",
        )
    ):
        blockers.append("source_train.write_boundaries")
    selection = dict(receipt.get("selection") or {})
    expected_selection = {
        "unit": "BEHAVIOR_FAMILY",
        "per_cell_count": 64,
        "cell_count": 8,
        "candidate_count_exact": 512,
        "checkpoint_size": 64,
        "checkpoint_count": 8,
        "arms": [
            "expanded_mechanism_random_v2_4",
            "mechanism_evolution_v2_4",
        ],
        "seeds": [359914106, 1141399971],
        "horizons_hours": [1, 4],
        "duplicate_family_backfill_allowed": False,
        "selection_frozen_before_fresh_data_read": True,
    }
    if selection != expected_selection:
        blockers.append("selection")
    expected_fresh = {
        "start": "2026-07-01T00:00:00Z",
        "end_exclusive": "2026-07-18T00:00:00Z",
        "role": "FRESH_DATA_VALIDATION_V2_4",
        "execution_venue": "BINANCE_USD_M",
        "baseline_cost_bps": 5.0,
        "cost_sensitivity_bps": [5.0, 10.0],
    }
    if dict(receipt.get("fresh_validation") or {}) != expected_fresh:
        blockers.append("fresh_validation")
    compute = dict(receipt.get("compute") or {})
    if compute != {
        "execution_host": "PC2",
        "workers_default": 10,
        "workers_memory_fallback": 8,
        "workers_12_forbidden": True,
        "fallback_only_after_memory_anomaly": True,
        "evaluation_wall_time_seconds_maximum": 14_400,
        "minimum_pair_evaluated_per_hour": 128.0,
        "local_heavy_compute_allowed": False,
    }:
        blockers.append("compute")
    carrier = dict(receipt.get("carrier") or {})
    if carrier != {
        "field_count": 115,
        "oi_mark_field_count": 71,
        "aggtrades_field_count": 44,
        "source_oi_cache": (
            ".cache/crypto_search_surface_integration_v1/"
            "oi_mark_ranks51_200"
        ),
        "aligned_cache": (
            ".cache/crypto_search_engine_v2_4/"
            "oi_mark_x_aggtrades_115_20260701_20260718"
        ),
        "target_cache": (
            ".cache/crypto_search_engine_v2_4/"
            "binance_open_target_20260701_20260718"
        ),
        "missing_value_fill": None,
        "dynamic_eligible_intersection": True,
        "target_execution_delay_hours": 2,
        "partition_tail_purge_hours": 6,
    }:
        blockers.append("carrier")
    acquisition = dict(receipt.get("data_acquisition") or {})
    if (
        acquisition.get("authorized") is not True
        or acquisition.get("source")
        != "BINANCE_VISION_USD_M_MONTHLY_AGGTRADES"
        or acquisition.get("month") != "2026-07"
        or int(acquisition.get("rank_min", -1)) != 1
        or int(acquisition.get("rank_max", -1)) != 200
        or int(acquisition.get("workers", -1)) != 2
        or acquisition.get("checksum_required") is not True
        or acquisition.get("compact_1m_required") is not True
        or acquisition.get("raw_zip_deleted_after_verified_parquet") is not True
    ):
        blockers.append("data_acquisition")
    components = dict(receipt.get("component_sources") or {})
    if set(components) != {
        "v24_adapter",
        "pair_evaluator",
        "target_store",
        "carrier_materializer",
    }:
        blockers.append("component_sources.keys")
    boundaries = dict(receipt.get("boundaries") or {})
    expected_boundary_keys = {
        "single_run",
        "restart",
        "seed_change",
        "parameter_tuning",
        "rescue_rerun",
        "candidate_generation",
        "optimizer_feedback",
        "policy_memory_write",
        "archive_write",
        "oos",
        "challenge",
        "recent",
        "may_stress",
        "forward",
        "promotion",
        "new_evaluator",
        "new_ast",
        "new_compiler",
        "new_graph_node",
    }
    if (
        set(boundaries) != expected_boundary_keys
        or boundaries.get("single_run") is not True
        or any(
            boundaries.get(key) is not False
            for key in expected_boundary_keys - {"single_run"}
        )
    ):
        blockers.append("boundaries")
    if require_authorized:
        if receipt.get("status") != "RUN_AUTHORIZED":
            blockers.append("status")
        if receipt.get("run_authorized") is not True:
            blockers.append("run_authorized")
    source_sha = str(receipt.get("source_implementation_sha") or "").lower()
    if len(source_sha) != 40:
        blockers.append("source_implementation_sha")
    else:
        try:
            subprocess.check_call(
                ["git", "cat-file", "-e", f"{source_sha}^{{commit}}"],
                cwd=repo_root,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError:
            blockers.append("source_implementation_commit")
        for name, binding in components.items():
            item = dict(binding)
            relative = str(item.get("path") or "")
            try:
                committed = _git_file_sha256(repo_root, source_sha, relative)
            except (OSError, subprocess.CalledProcessError):
                committed = ""
            if committed != str(item.get("sha256") or ""):
                blockers.append(f"component_sources.{name}")
    if blockers:
        raise RuntimeError("V24_RUN_RECEIPT_BLOCKED:" + ",".join(blockers))
    return receipt


def _git_file_sha256(repo_root: Path, revision: str, path: str) -> str:
    payload = subprocess.check_output(
        ["git", "show", f"{revision}:{path}"], cwd=repo_root
    )
    return hashlib.sha256(payload).hexdigest().upper()


def load_v24_repair_run_receipt(
    repo_root: Path,
    *,
    require_authorized: bool = True,
) -> dict[str, Any]:
    """Load the one-time, same-cohort candidate-local isolation replay."""

    path = Path(repo_root) / V24_REPAIR_RUN_RECEIPT_PATH
    if not path.is_file():
        raise RuntimeError("V24_REPAIR_RUN_RECEIPT_MISSING")
    receipt = json.loads(path.read_text(encoding="utf-8-sig"))
    blockers: list[str] = []
    if receipt.get("schema_version") != 1:
        blockers.append("schema_version")
    if receipt.get("receipt_id") != (
        "CRYPTO_SEARCH_ENGINE_V2_4_REPAIR_REPLAY_RECEIPT"
    ):
        blockers.append("receipt_id")
    if receipt.get("experiment_id") != (
        "crypto_search_engine_v2_4_repair_replay"
    ):
        blockers.append("experiment_id")
    status = str(receipt.get("status") or "")
    allowed_statuses = {
        "RUN_AUTHORIZED_ONE_TIME_REPAIR_REPLAY",
        "RUN_AUTHORIZATION_CONSUMED_REPAIR_REPLAY_COMPLETE",
        "RUN_AUTHORIZATION_CONSUMED_ENGINE_VALIDATION_BLOCKED",
        "RUN_AUTHORIZATION_CONSUMED_ENGINE_BUDGET_EXHAUSTED",
    }
    if status not in allowed_statuses:
        blockers.append("status")
    expected_authorized = status == "RUN_AUTHORIZED_ONE_TIME_REPAIR_REPLAY"
    if receipt.get("run_authorized") is not expected_authorized:
        blockers.append("run_authorized")
    if require_authorized and not expected_authorized:
        blockers.append("authorization_consumed")
    historical_receipt = load_v24_run_receipt(
        repo_root,
        require_authorized=False,
    )
    for shared in ("source_train", "carrier"):
        if dict(receipt.get(shared) or {}) != dict(
            historical_receipt.get(shared) or {}
        ):
            blockers.append(shared)
    source = dict(receipt.get("source_v24") or {})
    expected_source_paths = {
        "source_runtime": (
            "runtime/crypto_search_engine_v2_4_fresh_gate_20260803"
        ),
        "selection_receipt_path": (
            "runtime/crypto_search_engine_v2_4_fresh_gate_20260803/"
            "behavior_family_selection_receipt.json"
        ),
        "aligned_carrier_manifest_path": (
            "runtime/crypto_search_engine_v2_4_fresh_gate_20260803/"
            "aligned_carrier_manifest.json"
        ),
        "economic_context_path": (
            "runtime/crypto_search_engine_v2_4_fresh_gate_20260803/"
            "economic_context.json"
        ),
        "prior_final_decision_path": (
            "runtime/crypto_search_engine_v2_4_fresh_gate_20260803/"
            "final_decision.json"
        ),
    }
    for name, expected in expected_source_paths.items():
        if str(source.get(name) or "") != expected:
            blockers.append(f"source_v24.{name}")
    source_file_bindings = (
        ("selection_receipt_path", "selection_receipt_file_sha256"),
        (
            "aligned_carrier_manifest_path",
            "aligned_carrier_manifest_file_sha256",
        ),
        ("economic_context_path", "economic_context_file_sha256"),
        ("prior_final_decision_path", "prior_final_decision_file_sha256"),
    )
    for _path_name, name in source_file_bindings:
        if len(str(source.get(name) or "")) != 64:
            blockers.append(f"source_v24.{name}")
    for path_name, hash_name in source_file_bindings:
        source_path = Path(repo_root) / str(source.get(path_name) or "")
        if (
            not source_path.is_file()
            or _file_sha256(source_path) != str(source.get(hash_name) or "")
        ):
            blockers.append(f"source_v24.file:{path_name}")
    if (
        str(source.get("selection_receipt_sha256") or "")
        != "DDD90D0F15CC7F54BA723D3E9C14274BB83F8FD186065374770C8C3205D4CD48"
        or int(source.get("candidate_count", -1)) != 512
        or str(source.get("prior_terminal_status") or "")
        != "ENGINE_VALIDATION_BLOCKED"
        or int(source.get("prior_strict_evaluated_count", -1)) != 0
        or source.get("prior_reward_feedback_observed") is not False
    ):
        blockers.append("source_v24.identity")
    selection = dict(receipt.get("selection") or {})
    if selection != {
        "candidate_count_exact": 512,
        "checkpoint_size": 64,
        "checkpoint_count": 8,
        "arms": [
            "expanded_mechanism_random_v2_4",
            "mechanism_evolution_v2_4",
        ],
        "seeds": [359914106, 1141399971],
        "horizons_hours": [1, 4],
        "candidate_replacement_allowed": False,
        "candidate_backfill_allowed": False,
        "candidate_reordering_allowed": False,
    }:
        blockers.append("selection")
    if dict(receipt.get("fresh_validation") or {}) != {
        "start": "2026-07-01T00:00:00Z",
        "end_exclusive": "2026-07-18T00:00:00Z",
        "role": "FRESH_DATA_VALIDATION_V2_4",
        "execution_venue": "BINANCE_USD_M",
        "baseline_cost_bps": 5.0,
        "cost_sensitivity_bps": [5.0, 10.0],
    }:
        blockers.append("fresh_validation")
    if dict(receipt.get("compute") or {}) != {
        "execution_host": "PC2",
        "workers_default": 10,
        "workers_memory_fallback": 8,
        "workers_12_forbidden": True,
        "evaluation_wall_time_seconds_maximum": 14_400,
        "minimum_pair_evaluated_per_hour": 128.0,
        "local_heavy_compute_allowed": False,
    }:
        blockers.append("compute")
    repair = dict(receipt.get("repair") or {})
    if repair != {
        "static_constructibility_sweep_required": True,
        "static_constructibility_expected_count": 512,
        "candidate_local_failure_action": "PERSIST_NO_BACKFILL",
        "candidate_local_failure_reasons": sorted(
            V24_CANDIDATE_LOCAL_FAILURES
        ),
        "checkpoint_unit": "SOURCE_CANDIDATE_ORDINAL",
        "source_candidates_per_checkpoint": 64,
        "checkpoint_count": 8,
        "economic_paths_for_strict_evaluated_only": True,
        "arm_comparison": (
            "DETERMINISTIC_EQUAL_COUNT_WITHIN_SEED_HORIZON_BY_SOURCE_ORDINAL"
        ),
    }:
        blockers.append("repair")
    boundaries = dict(receipt.get("boundaries") or {})
    if boundaries != {
        "single_run": True,
        "restart": False,
        "seed_change": False,
        "parameter_tuning": False,
        "candidate_generation": False,
        "candidate_backfill": False,
        "optimizer_feedback": False,
        "policy_memory_write": False,
        "archive_write": False,
        "oos": False,
        "challenge": False,
        "recent": False,
        "may_stress": False,
        "forward": False,
        "promotion": False,
        "new_evaluator": False,
        "new_ast": False,
        "new_compiler": False,
        "new_graph_node": False,
    }:
        blockers.append("boundaries")
    components = dict(receipt.get("component_sources") or {})
    if set(components) != {
        "v24_adapter",
        "pair_evaluator",
        "mechanism_compiler",
        "target_store",
    }:
        blockers.append("component_sources.keys")
    source_sha = str(receipt.get("source_implementation_sha") or "").lower()
    if len(source_sha) != 40:
        blockers.append("source_implementation_sha")
    else:
        try:
            subprocess.check_call(
                ["git", "cat-file", "-e", f"{source_sha}^{{commit}}"],
                cwd=repo_root,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError:
            blockers.append("source_implementation_commit")
        for name, binding in components.items():
            item = dict(binding)
            relative = str(item.get("path") or "")
            try:
                committed = _git_file_sha256(repo_root, source_sha, relative)
            except (OSError, subprocess.CalledProcessError):
                committed = ""
            if committed != str(item.get("sha256") or ""):
                blockers.append(f"component_sources.{name}")
            current = Path(repo_root) / relative
            if require_authorized and (
                not current.is_file()
                or _file_sha256(current) != str(item.get("sha256") or "")
            ):
                blockers.append(f"component_sources.current.{name}")
    if require_authorized and receipt.get("run_outcome"):
        blockers.append("run_outcome_before_consumption")
    if blockers:
        raise RuntimeError(
            "V24_REPAIR_RUN_RECEIPT_BLOCKED:" + ",".join(blockers)
        )
    return receipt


def _candidate_spec_sha256(row: Mapping[str, Any]) -> str:
    raw = row.get("candidate_spec_json")
    if isinstance(raw, Mapping):
        payload = dict(raw)
    elif isinstance(raw, str) and raw:
        payload = json.loads(raw)
    else:
        raise ValueError("V24_CANDIDATE_SPEC_MISSING")
    if str(payload.get("candidate_id") or "") != str(row["candidate_id"]):
        raise ValueError("V24_CANDIDATE_SPEC_IDENTITY_CHANGED")
    return _canonical_sha256(payload)


def _verify_producer_source(
    repo_root: Path,
    contract: Mapping[str, Any],
    producer_source_sha: str,
) -> str:
    normalized = str(producer_source_sha).lower()
    if (
        len(normalized) != 40
        or any(value not in "0123456789abcdef" for value in normalized)
    ):
        raise ValueError("V24_GATE_PRODUCER_SOURCE_SHA_INVALID")
    try:
        subprocess.check_call(
            ["git", "cat-file", "-e", f"{normalized}^{{commit}}"],
            cwd=repo_root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        for binding in dict(contract["component_sources"]).values():
            item = dict(binding)
            if _git_file_sha256(
                repo_root,
                normalized,
                str(item["path"]),
            ) != str(item["sha256"]):
                raise RuntimeError("V24_GATE_PRODUCER_COMPONENT_HASH_CHANGED")
        if _git_file_sha256(
            repo_root,
            normalized,
            V24_CONTRACT_PATH,
        ) != _file_sha256(Path(repo_root) / V24_CONTRACT_PATH):
            raise RuntimeError("V24_GATE_PRODUCER_CONTRACT_HASH_CHANGED")
    except subprocess.CalledProcessError as exc:
        raise RuntimeError("V24_GATE_PRODUCER_SOURCE_NOT_COMMITTED") from exc
    return normalized


def _family_key(row: Mapping[str, Any]) -> tuple[str, int, int, str]:
    family_id = str(row.get("behavior_family_id") or "")
    if not family_id:
        raise ValueError("V24_BEHAVIOR_FAMILY_ID_MISSING")
    return (
        str(row["arm"]),
        int(row["seed"]),
        int(row["horizon_hours"]),
        family_id,
    )


def _champion_order(row: Mapping[str, Any]) -> tuple[float, int, str]:
    reward = float(row["search_reward"])
    if not math.isfinite(reward):
        raise ValueError("V24_TRAIN_SEARCH_REWARD_NON_FINITE")
    return (
        -reward,
        int(row["arm_completion_ordinal"]),
        str(row["candidate_id"]),
    )


def select_behavior_family_champions(
    rows: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Select one deterministic train-reward champion per arm/seed/horizon/family.

    No validation, OOS, economic outcome, novelty score, or expression count is
    allowed to influence the champion order.  Cells remain separate so one
    seed or horizon cannot donate a champion to another.
    """

    champions: dict[tuple[str, int, int, str], Mapping[str, Any]] = {}
    family_expression_counts: Counter[tuple[str, int, int, str]] = Counter()
    candidate_ids: set[str] = set()
    for row in rows:
        candidate_id = str(row.get("candidate_id") or "")
        if not candidate_id or candidate_id in candidate_ids:
            raise ValueError("V24_CANDIDATE_ID_MISSING_OR_DUPLICATED")
        candidate_ids.add(candidate_id)
        key = _family_key(row)
        family_expression_counts[key] += 1
        previous = champions.get(key)
        if previous is None or _champion_order(row) < _champion_order(previous):
            champions[key] = row

    selected = [
        dict(row)
        for _, row in sorted(
            champions.items(),
            key=lambda item: (
                item[0][0],
                item[0][1],
                item[0][2],
                _champion_order(item[1]),
                item[0][3],
            ),
        )
    ]
    proof_rows = [
        {
            "arm": key[0],
            "seed": key[1],
            "horizon_hours": key[2],
            "behavior_family_id": key[3],
            "expression_count": int(family_expression_counts[key]),
            "champion_candidate_id": str(champions[key]["candidate_id"]),
            "champion_search_reward": float(champions[key]["search_reward"]),
            "champion_arm_completion_ordinal": int(
                champions[key]["arm_completion_ordinal"]
            ),
        }
        for key in sorted(champions)
    ]
    selection_projection = [
        {
            "arm": str(row["arm"]),
            "seed": int(row["seed"]),
            "horizon_hours": int(row["horizon_hours"]),
            "behavior_family_id": str(row["behavior_family_id"]),
            "candidate_id": str(row["candidate_id"]),
            "search_reward": float(row["search_reward"]),
            "arm_completion_ordinal": int(row["arm_completion_ordinal"]),
        }
        for row in selected
    ]
    receipt = {
        "schema_version": 1,
        "selection_unit": "BEHAVIOR_FAMILY",
        "family_key": list(V24_FAMILY_KEY),
        "selection_authority": V24_SELECTION_AUTHORITY,
        "champion_order": list(V24_CHAMPION_ORDER),
        "input_expression_count": len(rows),
        "selected_behavior_family_count": len(selected),
        "duplicate_expression_count": len(rows) - len(selected),
        "family_proof": proof_rows,
        "selection_sha256": _canonical_sha256(selection_projection),
        "validation_or_oos_feedback_used": False,
    }
    return selected, receipt


def select_behavior_family_cohort(
    rows: Sequence[Mapping[str, Any]],
    *,
    per_cell_count: int,
    expected_cells: Sequence[tuple[str, int, int]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Return an equal-count top-family cohort for every arm/seed/horizon cell."""

    if int(per_cell_count) < 1:
        raise ValueError("V24_BEHAVIOR_FAMILY_COHORT_COUNT_INVALID")
    champions, champion_receipt = select_behavior_family_champions(rows)
    cells: dict[tuple[str, int, int], list[dict[str, Any]]] = {}
    for row in champions:
        key = (str(row["arm"]), int(row["seed"]), int(row["horizon_hours"]))
        cells.setdefault(key, []).append(row)
    normalized_expected = {
        (str(arm), int(seed), int(horizon))
        for arm, seed, horizon in expected_cells
    }
    if not normalized_expected or set(cells) != normalized_expected:
        missing = sorted(normalized_expected - set(cells))
        extra = sorted(set(cells) - normalized_expected)
        raise RuntimeError(
            "V24_BEHAVIOR_FAMILY_CELL_SET_CHANGED:"
            f"missing={missing};extra={extra}"
        )
    selected: list[dict[str, Any]] = []
    cell_proof: list[dict[str, Any]] = []
    for key in sorted(cells):
        ordered = sorted(cells[key], key=_champion_order)
        if len(ordered) < int(per_cell_count):
            raise RuntimeError(
                "V24_BEHAVIOR_FAMILY_COHORT_UNDERFILLED:"
                + "|".join((key[0], str(key[1]), str(key[2])))
            )
        local = ordered[: int(per_cell_count)]
        selected.extend(local)
        cell_proof.append(
            {
                "arm": key[0],
                "seed": key[1],
                "horizon_hours": key[2],
                "available_family_count": len(ordered),
                "selected_family_count": len(local),
                "selected_candidate_ids": [
                    str(row["candidate_id"]) for row in local
                ],
            }
        )
    projection = [
        {
            "arm": str(row["arm"]),
            "seed": int(row["seed"]),
            "horizon_hours": int(row["horizon_hours"]),
            "behavior_family_id": str(row["behavior_family_id"]),
            "candidate_id": str(row["candidate_id"]),
        }
        for row in selected
    ]
    return selected, {
        "schema_version": 1,
        "selection_unit": "BEHAVIOR_FAMILY",
        "per_arm_seed_horizon_count": int(per_cell_count),
        "cell_count": len(cells),
        "expected_cells": [
            {"arm": arm, "seed": seed, "horizon_hours": horizon}
            for arm, seed, horizon in sorted(normalized_expected)
        ],
        "selected_count": len(selected),
        "duplicate_family_backfill_used": False,
        "champion_selection_sha256": champion_receipt["selection_sha256"],
        "cell_proof": cell_proof,
        "cohort_sha256": _canonical_sha256(projection),
    }


def _finite_mean(values: np.ndarray) -> float:
    finite = np.asarray(values, dtype=float)
    finite = finite[np.isfinite(finite)]
    return float(np.mean(finite)) if finite.size else float("nan")


def build_economic_path_artifacts(
    evaluation: Mapping[str, Any],
    *,
    cohort: str,
    arm: str,
    seed: int,
    horizon_hours: int,
    candidate_spec_sha256: str,
    economic_receipt_sha256: str,
    evaluation_partition: str,
    execution_venue: str,
) -> dict[str, list[dict[str, Any]]]:
    """Project pair18m paths to exact hourly, daily, and sparse asset rows."""

    payload = evaluation.get("_economic_paths")
    if not isinstance(payload, Mapping) or int(payload.get("schema_version", -1)) != 1:
        raise ValueError("V24_ECONOMIC_PATHS_MISSING")
    if (
        str(payload.get("candidate_id") or "")
        != str(evaluation.get("candidate_id") or "")
        or str(payload.get("candidate_spec_sha256") or "")
        != str(candidate_spec_sha256)
        or int(payload.get("horizon_hours", -1)) != int(horizon_hours)
        or float(payload.get("cost_bps", float("nan"))) != 5.0
        or str(payload.get("authority") or "")
        != "PAIR18M_EXISTING_MAPPING_COST_EVALUATOR_PATH_PROJECTION_V1"
        or str(payload.get("economic_receipt_sha256") or "")
        != str(economic_receipt_sha256)
        or str(payload.get("evaluation_partition") or "")
        != str(evaluation_partition)
        or str(payload.get("execution_venue") or "") != str(execution_venue)
    ):
        raise ValueError("V24_ECONOMIC_PATH_IDENTITY_CHANGED")
    timestamps = np.asarray(payload["timestamp_ns"], dtype=np.int64)
    if timestamps.ndim != 1 or timestamps.size == 0:
        raise ValueError("V24_ECONOMIC_TIMESTAMPS_INVALID")
    asset_ids = tuple(str(value) for value in payload["asset_ids"])
    execution_venue = str(payload.get("execution_venue") or "")
    if not execution_venue or len(asset_ids) != len(set(asset_ids)):
        raise ValueError("V24_ECONOMIC_IDENTITY_INVALID")
    utc_hours = timestamps.astype("datetime64[ns]")
    utc_days = utc_hours.astype("datetime64[D]")
    unique_days = tuple(dict.fromkeys(utc_days.tolist()))
    candidate_id = str(evaluation["candidate_id"])
    common = {
        "candidate_id": candidate_id,
        "cohort": str(cohort),
        "arm": str(arm),
        "seed": int(seed),
        "horizon_hours": int(horizon_hours),
        "execution_venue": execution_venue,
        "economic_receipt_sha256": str(payload["economic_receipt_sha256"]),
        "evaluation_partition": str(payload["evaluation_partition"]),
        "raw_fields_json": json.dumps(
            list(payload.get("raw_fields") or ()),
            sort_keys=True,
            separators=(",", ":"),
        ),
    }
    hourly_rows: list[dict[str, Any]] = []
    daily_rows: list[dict[str, Any]] = []
    position_rows: list[dict[str, Any]] = []
    sleeves = dict(payload.get("sleeves") or {})
    if not sleeves:
        raise ValueError("V24_ECONOMIC_SLEEVES_MISSING")
    for sleeve_name, raw_sleeve in sorted(sleeves.items()):
        sleeve = dict(raw_sleeve)
        vectors = {
            name: np.asarray(sleeve[name], dtype=float)
            for name in ("gross", "cost", "turnover", "net")
        }
        mask = np.asarray(sleeve["mask"], dtype=bool)
        weights = np.asarray(sleeve["weights"], dtype=float)
        asset_gross = np.asarray(
            sleeve["asset_gross_contribution"], dtype=float
        )
        if (
            any(values.shape != timestamps.shape for values in vectors.values())
            or mask.shape != timestamps.shape
            or weights.shape != (len(asset_ids), timestamps.size)
            or asset_gross.shape != weights.shape
        ):
            raise ValueError("V24_ECONOMIC_PATH_SHAPE_CHANGED")
        finite = mask & np.isfinite(vectors["net"])
        if not np.allclose(
            vectors["gross"][finite] - vectors["cost"][finite],
            vectors["net"][finite],
            rtol=0.0,
            atol=1.0e-15,
        ):
            raise ValueError("V24_ECONOMIC_WATERFALL_NOT_ADDITIVE")
        for time_index, timestamp in enumerate(timestamps):
            objective = bool(mask[time_index])
            gross_value = float(vectors["gross"][time_index])
            turnover_value = float(vectors["turnover"][time_index])
            cost_5bps = turnover_value * 5.0 / 10_000.0
            cost_10bps = turnover_value * 10.0 / 10_000.0
            hourly_rows.append(
                {
                    **common,
                    "sleeve": str(sleeve_name),
                    "timestamp_ns": int(timestamp),
                    "utc_hour": str(utc_hours[time_index]),
                    "objective_mask": objective,
                    "gross": gross_value,
                    "cost": float(vectors["cost"][time_index]),
                    "turnover": turnover_value,
                    "net": float(vectors["net"][time_index]),
                    "cost_5bps": cost_5bps,
                    "net_5bps": gross_value - cost_5bps,
                    "cost_10bps": cost_10bps,
                    "net_10bps": gross_value - cost_10bps,
                }
            )
        for day_ordinal, day in enumerate(unique_days):
            local = (utc_days == day) & mask
            daily_gross = _finite_mean(vectors["gross"][local])
            daily_turnover = _finite_mean(vectors["turnover"][local])
            daily_cost_5bps = daily_turnover * 5.0 / 10_000.0
            daily_cost_10bps = daily_turnover * 10.0 / 10_000.0
            daily_rows.append(
                {
                    **common,
                    "sleeve": str(sleeve_name),
                    "day_ordinal": int(day_ordinal),
                    "utc_day": str(day),
                    "gross": daily_gross,
                    "cost": _finite_mean(vectors["cost"][local]),
                    "turnover": daily_turnover,
                    "net": _finite_mean(vectors["net"][local]),
                    "cost_5bps": daily_cost_5bps,
                    "net_5bps": daily_gross - daily_cost_5bps,
                    "cost_10bps": daily_cost_10bps,
                    "net_10bps": daily_gross - daily_cost_10bps,
                    "active_hour_count": int(local.sum()),
                }
            )
        active_coordinates = np.argwhere(
            mask[np.newaxis, :]
            & (
                (np.abs(weights) > 1.0e-12)
                | (np.abs(asset_gross) > 1.0e-18)
            )
        )
        for asset_index, time_index in active_coordinates:
            position_rows.append(
                {
                    **common,
                    "sleeve": str(sleeve_name),
                    "timestamp_ns": int(timestamps[time_index]),
                    "utc_hour": str(utc_hours[time_index]),
                    "asset_id": asset_ids[int(asset_index)],
                    "weight": float(weights[asset_index, time_index]),
                    "asset_gross_contribution": float(
                        asset_gross[asset_index, time_index]
                    ),
                }
            )
    return {
        "hourly_sleeves": hourly_rows,
        "daily_sleeves": daily_rows,
        "asset_positions": position_rows,
    }


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
            ensure_ascii=True,
            default=str,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


def freeze_v24_gate_selection(
    *,
    repo_root: Path,
    receipt_path: Path,
    train_rows: Sequence[Mapping[str, Any]],
    expected_cells: Sequence[tuple[str, int, int]],
    per_cell_count: int,
    producer_source_sha: str,
    evaluation_start: str,
    evaluation_end_exclusive: str,
    economic_receipt_sha256: str,
    evaluation_partition: str,
    execution_venue: str,
) -> dict[str, Any]:
    """Freeze family champions and the fresh interval before any data read."""

    contract = load_v24_contract(repo_root)
    normalized_source_sha = _verify_producer_source(
        repo_root,
        contract,
        producer_source_sha,
    )
    start = np.datetime64(str(evaluation_start).replace("Z", ""), "ns")
    end = np.datetime64(str(evaluation_end_exclusive).replace("Z", ""), "ns")
    prior_end = np.datetime64(
        str(contract["fresh_data_gate"]["prior_holdout_end_exclusive"]).replace(
            "Z", ""
        ),
        "ns",
    )
    if start < prior_end or end <= start:
        raise ValueError("V24_FRESH_DATA_INTERVAL_NOT_ADMITTED")
    if (
        len(str(economic_receipt_sha256)) != 64
        or any(
            value not in "0123456789abcdefABCDEF"
            for value in str(economic_receipt_sha256)
        )
        or str(evaluation_partition)
        != str(contract["fresh_data_gate"]["evaluation_partition"])
        or str(execution_venue)
        != str(contract["fresh_data_gate"]["execution_venue"])
    ):
        raise ValueError("V24_FRESH_DATA_ECONOMIC_IDENTITY_INVALID")
    selected, selection_receipt = select_behavior_family_cohort(
        train_rows,
        per_cell_count=per_cell_count,
        expected_cells=expected_cells,
    )
    required_arms = set(contract["gate_adapter"]["required_arms"])
    if {str(row["arm"]) for row in selected} != required_arms:
        raise RuntimeError("V24_GATE_REQUIRED_ARMS_CHANGED")
    selection_projection = [
        {
            "candidate_id": str(row["candidate_id"]),
            "candidate_spec_sha256": _candidate_spec_sha256(row),
            "behavior_family_id": str(row["behavior_family_id"]),
            "arm": str(row["arm"]),
            "seed": int(row["seed"]),
            "horizon_hours": int(row["horizon_hours"]),
            "search_reward": float(row["search_reward"]),
            "arm_completion_ordinal": int(row["arm_completion_ordinal"]),
        }
        for row in selected
    ]
    receipt = {
        "schema_version": 1,
        "status": "V24_SELECTION_FROZEN_BEFORE_DATA_READ",
        "producer_source_sha": normalized_source_sha,
        "contract_path": V24_CONTRACT_PATH,
        "contract_sha256": _file_sha256(Path(repo_root) / V24_CONTRACT_PATH),
        "evaluation_start": str(evaluation_start),
        "evaluation_end_exclusive": str(evaluation_end_exclusive),
        "fresh_data_admission": "AFTER_PRIOR_HOLDOUT_END",
        "economic_receipt_sha256": str(economic_receipt_sha256).upper(),
        "evaluation_partition": str(evaluation_partition),
        "execution_venue": str(execution_venue),
        "market_read_performed": False,
        "candidate_generation_performed": False,
        "adaptive_feedback_written": False,
        "selection_receipt": selection_receipt,
        "selected_candidates": selection_projection,
    }
    receipt["receipt_sha256"] = _canonical_sha256(receipt)
    if receipt_path.exists():
        raise FileExistsError(f"V24 selection receipt exists: {receipt_path}")
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = receipt_path.with_name(receipt_path.name + f".tmp-{os.getpid()}")
    if temporary.exists():
        raise FileExistsError(f"V24 selection temporary exists: {temporary}")
    _write_json(temporary, receipt)
    os.replace(temporary, receipt_path)
    return receipt


def _v24_expected_cells(
    receipt: Mapping[str, Any],
) -> tuple[tuple[str, int, int], ...]:
    selection = dict(receipt["selection"])
    cells = tuple(
        (str(arm), int(seed), int(horizon))
        for arm in selection["arms"]
        for seed in selection["seeds"]
        for horizon in selection["horizons_hours"]
    )
    if len(cells) != int(selection["cell_count"]):
        raise RuntimeError("V24_RECEIPT_CELL_COUNT_CHANGED")
    return cells


def freeze_v24_authorized_selection(
    repo_root: Path,
    *,
    runtime_date: str = V24_DEFAULT_RUNTIME_DATE,
    producer_source_sha: str | None = None,
) -> dict[str, Any]:
    """Freeze the exact 512 train-only family champions before a fresh read."""

    if str(runtime_date) != V24_DEFAULT_RUNTIME_DATE:
        raise ValueError("V24_RUNTIME_DATE_CHANGED")
    receipt = load_v24_run_receipt(repo_root, require_authorized=True)
    observed_source = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=repo_root, text=True
    ).strip().lower()
    source_sha = str(producer_source_sha or observed_source).lower()
    if source_sha != observed_source:
        raise RuntimeError("V24_PRODUCER_SOURCE_SHA_CHANGED")
    runtime_root = (
        Path(repo_root) / "runtime" / f"{V24_RUNTIME_PREFIX}_{runtime_date}"
    )
    output = runtime_root / "behavior_family_selection_receipt.json"
    if output.is_file():
        existing = json.loads(output.read_text(encoding="utf-8"))
        saved_hash = str(existing.pop("receipt_sha256", ""))
        if _canonical_sha256(existing) != saved_hash:
            raise RuntimeError("V24_EXISTING_SELECTION_RECEIPT_CHANGED")
        return {**existing, "receipt_sha256": saved_hash}
    source = dict(receipt["source_train"])
    frame = pd.read_parquet(Path(repo_root) / source["candidate_ledger_path"])
    if len(frame) != int(source["candidate_ledger_row_count"]):
        raise RuntimeError("V24_SOURCE_LEDGER_ROW_COUNT_CHANGED")
    rows = prepare_v24_train_rows(
        frame.to_dict("records"),
        source_arm_mapping=source["source_arm_mapping"],
    )
    fresh = dict(receipt["fresh_validation"])
    return freeze_v24_gate_selection(
        repo_root=Path(repo_root),
        receipt_path=output,
        train_rows=rows,
        expected_cells=_v24_expected_cells(receipt),
        per_cell_count=int(receipt["selection"]["per_cell_count"]),
        producer_source_sha=source_sha,
        evaluation_start=str(fresh["start"]),
        evaluation_end_exclusive=str(fresh["end_exclusive"]),
        economic_receipt_sha256=_file_sha256(
            Path(repo_root) / V24_RUN_RECEIPT_PATH
        ),
        evaluation_partition="validation",
        execution_venue=str(fresh["execution_venue"]),
    )


def _load_v24_selection(
    repo_root: Path,
    *,
    runtime_date: str,
) -> dict[str, Any]:
    path = (
        Path(repo_root)
        / "runtime"
        / f"{V24_RUNTIME_PREFIX}_{runtime_date}"
        / "behavior_family_selection_receipt.json"
    )
    if not path.is_file():
        raise RuntimeError("V24_SELECTION_MUST_BE_FROZEN_BEFORE_DATA_READ")
    receipt = json.loads(path.read_text(encoding="utf-8"))
    receipt_hash = str(receipt.pop("receipt_sha256", ""))
    if (
        receipt.get("status") != "V24_SELECTION_FROZEN_BEFORE_DATA_READ"
        or receipt.get("market_read_performed") is not False
        or receipt.get("candidate_generation_performed") is not False
        or _canonical_sha256(receipt) != receipt_hash
    ):
        raise RuntimeError("V24_SELECTION_RECEIPT_INVALID")
    return {**receipt, "receipt_sha256": receipt_hash}


def _build_v24_economic_context(
    repo_root: Path,
    *,
    receipt: Mapping[str, Any],
    target_metadata: Mapping[str, Any],
) -> dict[str, Any]:
    from alphafactory_crypto.broad_search.experiment_authority import (
        resolve_search_economic_receipt,
    )

    source = dict(receipt["source_train"])
    base = resolve_search_economic_receipt(
        Path(repo_root), str(source["economic_receipt_path"])
    )
    fresh = dict(receipt["fresh_validation"])
    validation = {
        "role": str(fresh["role"]),
        "start": str(fresh["start"]),
        "end_exclusive": str(fresh["end_exclusive"]),
        "optimizer_feedback_allowed": False,
        "policy_memory_write_allowed": False,
        "candidate_generation_allowed": False,
    }
    execution = {
        **dict(base["execution"]),
        "target_cache_path": str(receipt["carrier"]["target_cache"]),
        "target_cache_identity_sha256": str(target_metadata["identity_sha256"]),
    }
    partitions = {
        **{
            key: dict(value)
            for key, value in dict(base["evidence_partition"]).items()
        },
        "validation": validation,
    }
    return {
        **base,
        "run_authorized": True,
        "run_authorization": {
            "decision_id": str(receipt["decision_id"]),
            "authority": "CURRENT_USER_INSTRUCTION",
            "scope": "ONE_FROZEN_512_FAMILY_FRESH_DATA_VALIDATION_GATE",
            "parameter_tuning_allowed": False,
            "seed_change_allowed": False,
            "rescue_rerun_allowed": False,
        },
        "evidence_partition": partitions,
        "validation": validation,
        "execution": execution,
        "receipt_sha256": _file_sha256(
            Path(repo_root) / V24_RUN_RECEIPT_PATH
        ),
    }


def prepare_v24_fresh_carrier(
    repo_root: Path,
    *,
    top100_tar: Path,
    ranks101_200_tar: Path,
    runtime_date: str = V24_DEFAULT_RUNTIME_DATE,
    producer_source_sha: str | None = None,
) -> dict[str, Any]:
    """Reuse the admitted carrier materializer for the frozen July interval."""

    if str(runtime_date) != V24_DEFAULT_RUNTIME_DATE:
        raise ValueError("V24_RUNTIME_DATE_CHANGED")
    selection = _load_v24_selection(repo_root, runtime_date=runtime_date)
    receipt = load_v24_run_receipt(repo_root, require_authorized=True)
    observed_source = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=repo_root, text=True
    ).strip().lower()
    source_sha = str(producer_source_sha or observed_source).lower()
    if source_sha != observed_source or source_sha != str(
        selection["producer_source_sha"]
    ).lower():
        raise RuntimeError("V24_CARRIER_SOURCE_SHA_CHANGED")
    if not Path(top100_tar).is_file() or not Path(ranks101_200_tar).is_file():
        raise FileNotFoundError("V24_JULY_AGGTRADES_TAR_MISSING")
    from alphafactory_crypto.broad_search.replay_v14_binance_target import (
        build_binance_target_cache,
    )
    from alphafactory_crypto.broad_search.runner18m import RawPanelStore
    from alphafactory_crypto.broad_search.search_engine_v1 import (
        _contracts_payload,
        _directory_bundle,
        _load_v14_config,
        _v14_carrier_contracts,
        sha256_file,
    )
    from alphafactory_crypto.data_admission_v1 import (
        build_aggtrades_search_surface_cache,
    )

    v14_config, _ = _load_v14_config(Path(repo_root))
    oi_contracts, agg_contracts, _, _ = _v14_carrier_contracts(
        Path(repo_root), v14_config
    )
    carrier = dict(receipt["carrier"])
    source_oi_cache = Path(repo_root) / str(carrier["source_oi_cache"])
    aligned_cache = Path(repo_root) / str(carrier["aligned_cache"])
    metadata = build_aggtrades_search_surface_cache(
        source_cache_root=source_oi_cache,
        top100_tar=Path(top100_tar),
        ranks101_200_tar=Path(ranks101_200_tar),
        output_cache_root=aligned_cache,
        broad_field_ids=[item.field_id for item in oi_contracts],
        start=str(receipt["fresh_validation"]["start"]),
        end_exclusive=str(receipt["fresh_validation"]["end_exclusive"]),
        producer_source_sha=source_sha,
        verify_tar_sha256=True,
    )
    contracts = tuple((*oi_contracts, *agg_contracts))
    if len(contracts) != int(carrier["field_count"]):
        raise RuntimeError("V24_CARRIER_FIELD_COUNT_CHANGED")
    target_config = json.loads(
        (
            Path(repo_root)
            / "config/crypto_search_engine_v1_4_binance_target_replay.json"
        ).read_text(encoding="utf-8")
    )
    store = RawPanelStore.open(aligned_cache)
    target_root = Path(repo_root) / str(carrier["target_cache"])
    target_metadata = build_binance_target_cache(
        Path(repo_root),
        source_store=store,
        config=target_config,
        target_cache_root=target_root,
    )
    runtime_root = (
        Path(repo_root) / "runtime" / f"{V24_RUNTIME_PREFIX}_{runtime_date}"
    )
    contract_rows = _contracts_payload(contracts)
    manifest = {
        "schema_version": 1,
        "status": "V24_FRESH_ALIGNED_CARRIER_READY",
        "producer_source_sha": source_sha,
        "selection_receipt_sha256": selection["receipt_sha256"],
        "carrier_id": "OI_MARK_RANKS51_200_X_AGGTRADES_TOP200_ALIGNED_V24",
        "cache_root": str(carrier["aligned_cache"]),
        "cache_identity_sha256": metadata["identity_sha256"],
        "directory_bundle": _directory_bundle(aligned_cache),
        "contracts": contract_rows,
        "contracts_sha256": _canonical_sha256(contract_rows),
        "field_count": len(contracts),
        "field_origins": {
            "OI_MARK_RANKS51_200_DELIVERED": [
                item.field_id for item in oi_contracts
            ],
            "AGGTRADES_TOP200_DELIVERED": [
                item.field_id for item in agg_contracts
            ],
        },
        "fresh_interval": dict(receipt["fresh_validation"]),
        "top100_tar": {
            "path": str(Path(top100_tar)),
            "sha256": sha256_file(Path(top100_tar)),
        },
        "ranks101_200_tar": {
            "path": str(Path(ranks101_200_tar)),
            "sha256": sha256_file(Path(ranks101_200_tar)),
        },
        "target_cache": {
            "path": str(carrier["target_cache"]),
            "identity_sha256": target_metadata["identity_sha256"],
            "metadata_sha256": _file_sha256(target_root / "metadata.json"),
        },
        "market_read_performed_after_selection_freeze": True,
        "missing_value_fill": None,
        "candidate_generation_performed": False,
    }
    manifest["manifest_sha256"] = _canonical_sha256(manifest)
    _write_json(runtime_root / "aligned_carrier_manifest.json", manifest)
    economic = _build_v24_economic_context(
        Path(repo_root), receipt=receipt, target_metadata=target_metadata
    )
    _write_json(runtime_root / "economic_context.json", economic)
    return manifest


def persist_v24_gate_bundle(
    *,
    repo_root: Path,
    output_root: Path,
    selection_receipt_path: Path,
    evaluations: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Persist paths only for an already-frozen, fresh-data selection."""

    contract = load_v24_contract(repo_root)
    selection_receipt = json.loads(
        selection_receipt_path.read_text(encoding="utf-8")
    )
    receipt_hash = str(selection_receipt.pop("receipt_sha256", ""))
    if (
        selection_receipt.get("status")
        != "V24_SELECTION_FROZEN_BEFORE_DATA_READ"
        or _canonical_sha256(selection_receipt) != receipt_hash
        or selection_receipt.get("market_read_performed") is not False
        or selection_receipt.get("contract_sha256")
        != _file_sha256(Path(repo_root) / V24_CONTRACT_PATH)
    ):
        raise RuntimeError("V24_SELECTION_RECEIPT_INVALID")
    normalized_source_sha = _verify_producer_source(
        repo_root,
        contract,
        str(selection_receipt["producer_source_sha"]),
    )
    selected = [dict(row) for row in selection_receipt["selected_candidates"]]
    selected_ids = {str(row["candidate_id"]) for row in selected}
    evaluation_lookup: dict[str, Mapping[str, Any]] = {}
    for evaluation in evaluations:
        candidate_id = str(evaluation.get("candidate_id") or "")
        if not candidate_id or candidate_id in evaluation_lookup:
            raise ValueError("V24_GATE_EVALUATION_ID_MISSING_OR_DUPLICATED")
        evaluation_lookup[candidate_id] = evaluation
    if set(evaluation_lookup) != selected_ids:
        raise RuntimeError("V24_GATE_EVALUATION_ID_SET_CHANGED")
    start_ns = np.datetime64(
        str(selection_receipt["evaluation_start"]).replace("Z", ""), "ns"
    ).astype(np.int64)
    end_ns = np.datetime64(
        str(selection_receipt["evaluation_end_exclusive"]).replace("Z", ""),
        "ns",
    ).astype(np.int64)
    for evaluation in evaluations:
        paths = dict(evaluation.get("_economic_paths") or {})
        timestamps = np.asarray(paths.get("timestamp_ns"), dtype=np.int64)
        if (
            timestamps.ndim != 1
            or timestamps.size == 0
            or int(timestamps.min()) < int(start_ns)
            or int(timestamps.max()) >= int(end_ns)
        ):
            raise RuntimeError("V24_GATE_EVALUATION_OUTSIDE_FROZEN_INTERVAL")
    if output_root.exists():
        raise FileExistsError(f"V24 gate output already exists: {output_root}")
    temporary = output_root.with_name(
        output_root.name + f".tmp-{os.getpid()}"
    )
    if temporary.exists():
        raise FileExistsError(f"V24 temporary output already exists: {temporary}")
    temporary.mkdir(parents=True)
    try:
        selection_projection = selected
        hourly_rows: list[dict[str, Any]] = []
        daily_rows: list[dict[str, Any]] = []
        position_rows: list[dict[str, Any]] = []
        for row in selected:
            projection = build_economic_path_artifacts(
                evaluation_lookup[str(row["candidate_id"])],
                cohort="behavior_family_train_top",
                arm=str(row["arm"]),
                seed=int(row["seed"]),
                horizon_hours=int(row["horizon_hours"]),
                candidate_spec_sha256=str(row["candidate_spec_sha256"]),
                economic_receipt_sha256=str(
                    selection_receipt["economic_receipt_sha256"]
                ),
                evaluation_partition=str(
                    selection_receipt["evaluation_partition"]
                ),
                execution_venue=str(selection_receipt["execution_venue"]),
            )
            hourly_rows.extend(projection["hourly_sleeves"])
            daily_rows.extend(projection["daily_sleeves"])
            position_rows.extend(projection["asset_positions"])
        artifacts = {
            "behavior_family_selection.parquet": selection_projection,
            "economic_hourly_sleeves.parquet": hourly_rows,
            "economic_daily_sleeves.parquet": daily_rows,
            "economic_asset_positions.parquet": position_rows,
        }
        _write_json(
            temporary / "behavior_family_selection_receipt.json",
            {**selection_receipt, "receipt_sha256": receipt_hash},
        )
        for name, rows in artifacts.items():
            pd.DataFrame(rows).to_parquet(temporary / name, index=False)
        file_rows = [
            {
                "path": name,
                "rows": len(rows),
                "sha256": _file_sha256(temporary / name),
            }
            for name, rows in artifacts.items()
        ]
        file_rows.append(
            {
                "path": "behavior_family_selection_receipt.json",
                "rows": 1,
                "sha256": _file_sha256(
                    temporary / "behavior_family_selection_receipt.json"
                ),
            }
        )
        manifest = {
            "schema_version": 1,
            "status": "V24_GATE_BUNDLE_COMPLETE",
            "producer_source_sha": normalized_source_sha,
            "contract_path": V24_CONTRACT_PATH,
            "contract_sha256": _file_sha256(
                Path(repo_root) / V24_CONTRACT_PATH
            ),
            "selection_receipt_sha256": receipt_hash,
            "selection_sha256": selection_receipt["selection_receipt"][
                "cohort_sha256"
            ],
            "champion_selection_sha256": selection_receipt[
                "selection_receipt"
            ][
                "champion_selection_sha256"
            ],
            "selected_behavior_family_count": len(selected),
            "evaluation_count": len(evaluations),
            "absolute_zero_benchmark": 0.0,
            "cost_sensitivity_bps": [5.0, 10.0],
            "economic_receipt_sha256": str(
                selection_receipt["economic_receipt_sha256"]
            ),
            "evaluation_partition": str(
                selection_receipt["evaluation_partition"]
            ),
            "execution_venue": str(selection_receipt["execution_venue"]),
            "candidate_generation_during_gate": False,
            "adaptive_feedback_during_gate": False,
            "files": file_rows,
        }
        manifest["bundle_sha256"] = _canonical_sha256(manifest)
        _write_json(temporary / "manifest.json", manifest)
        os.replace(temporary, output_root)
        return manifest
    except BaseException:
        if temporary.exists():
            shutil.rmtree(temporary)
        raise


_V24_WORKER_STORE: Any | None = None
_V24_WORKER_REGISTRY: Any | None = None
_V24_WORKER_CONTEXT: Mapping[str, Any] | None = None
_V24_WORKER_START = ""
_V24_WORKER_END = ""
_V24_WORKER_ROLE = ""


def sweep_v24_static_constructibility(
    *,
    selected_rows: Sequence[Mapping[str, Any]],
    contract_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Recompile the frozen genome identities without reading market arrays."""

    from alphafactory_crypto.broad_search.compositional18m import (
        CandidateSpec,
        TypedExpressionRegistry,
        mechanism_candidate_from_genes,
    )
    from alphafactory_crypto.broad_search.runner18m import _contracts_from_payload

    registry = TypedExpressionRegistry(_contracts_from_payload(contract_rows))
    proofs: list[dict[str, Any]] = []
    seen: set[str] = set()
    for ordinal, raw in enumerate(selected_rows):
        selected = dict(raw)
        payload = dict(selected["candidate"])
        stored = CandidateSpec.from_dict(payload)
        rebuilt = mechanism_candidate_from_genes(
            registry,
            genes=stored.generation_genes,
        )
        candidate_id = str(selected["candidate_id"])
        if (
            candidate_id in seen
            or stored.candidate_id != candidate_id
            or rebuilt.to_dict() != stored.to_dict()
            or _canonical_sha256(payload)
            != str(selected["candidate_spec_sha256"])
            or stored.expression.expression_id == stored.control.expression_id
        ):
            raise RuntimeError(
                f"V24_STATIC_CONSTRUCTIBILITY_CHANGED:{ordinal}:{candidate_id}"
            )
        seen.add(candidate_id)
        proofs.append(
            {
                "source_ordinal": int(ordinal),
                "candidate_id": candidate_id,
                "candidate_spec_sha256": str(
                    selected["candidate_spec_sha256"]
                ),
                "expression_id": stored.expression.expression_id,
                "control_expression_id": stored.control.expression_id,
                "mechanism_id": str(
                    stored.generation_genes.get("mechanism_id") or ""
                ),
            }
        )
    return {
        "schema_version": 1,
        "status": "PASS_V24_STATIC_CONSTRUCTIBILITY_SWEEP",
        "market_read_performed": False,
        "candidate_count": len(proofs),
        "unique_candidate_count": len(seen),
        "proofs_sha256": _canonical_sha256(proofs),
    }


def _v24_worker_initialize(
    cache_root: str,
    target_root: str,
    contract_rows: Sequence[Mapping[str, Any]],
    economic_context: Mapping[str, Any],
    start: str,
    end_exclusive: str,
    role: str,
) -> None:
    global _V24_WORKER_STORE, _V24_WORKER_REGISTRY, _V24_WORKER_CONTEXT
    global _V24_WORKER_START, _V24_WORKER_END, _V24_WORKER_ROLE
    from alphafactory_crypto.broad_search.compositional18m import (
        TypedExpressionRegistry,
    )
    from alphafactory_crypto.broad_search.replay_v14_binance_target import (
        BinanceTargetStore,
    )
    from alphafactory_crypto.broad_search.runner18m import (
        RawPanelStore,
        _contracts_from_payload,
    )

    _V24_WORKER_STORE = BinanceTargetStore(
        RawPanelStore.open(Path(cache_root)), Path(target_root)
    )
    _V24_WORKER_REGISTRY = TypedExpressionRegistry(
        _contracts_from_payload(contract_rows)
    )
    _V24_WORKER_CONTEXT = dict(economic_context)
    _V24_WORKER_START = str(start)
    _V24_WORKER_END = str(end_exclusive)
    _V24_WORKER_ROLE = str(role)


def _v24_worker_evaluate(payload: Mapping[str, Any]) -> dict[str, Any]:
    if (
        _V24_WORKER_STORE is None
        or _V24_WORKER_REGISTRY is None
        or _V24_WORKER_CONTEXT is None
    ):
        raise RuntimeError("V24_WORKER_NOT_INITIALIZED")
    from alphafactory_crypto.broad_search.compositional18m import CandidateSpec
    from alphafactory_crypto.broad_search.pair18m import evaluate_pair

    candidate = CandidateSpec.from_dict(dict(payload["candidate"]))
    orientation = float(payload["frozen_train_orientation"])
    process = psutil.Process(os.getpid())
    cpu_started = time.process_time()
    wall_started = time.perf_counter()
    try:
        evaluation = evaluate_pair(
            store=_V24_WORKER_STORE,
            registry=_V24_WORKER_REGISTRY,
            candidate=candidate,
            block_start=_V24_WORKER_START,
            block_end=_V24_WORKER_END,
            block_role=_V24_WORKER_ROLE,
            behavior_contract=None,
            economic_receipt=_V24_WORKER_CONTEXT,
            frozen_train_orientation=orientation,
            include_economic_paths=True,
        )
        error = None
        memory_error = False
    except MemoryError as failure:
        evaluation = None
        error = f"{type(failure).__name__}:{failure}"
        memory_error = True
    except (ValueError, FloatingPointError) as failure:
        evaluation = None
        error = f"{type(failure).__name__}:{failure}"
        memory_error = False
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


def _v24_checkpoint_files(root: Path) -> list[dict[str, Any]]:
    return [
        {
            "path": path.relative_to(root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": _file_sha256(path),
        }
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.name != "manifest.json"
    ]


def _v24_failure_reason(worker: Mapping[str, Any]) -> str | None:
    error = str(worker.get("error") or "")
    if not error:
        return None
    prefix, separator, reason = error.partition(":")
    if prefix not in {"ValueError", "FloatingPointError"} or not separator:
        raise RuntimeError(f"V24_UNEXPECTED_WORKER_FAILURE:{error}")
    if reason not in V24_CANDIDATE_LOCAL_FAILURES:
        raise RuntimeError(f"V24_UNEXPECTED_CANDIDATE_FAILURE:{error}")
    return reason


def _v24_write_candidate_failure_projection(
    *,
    ordinal: int,
    selected: Mapping[str, Any],
    worker: Mapping[str, Any],
    economic_receipt_sha256: str,
) -> dict[str, Any]:
    candidate_id = str(selected["candidate_id"])
    if str(worker.get("candidate_id") or "") != candidate_id:
        raise RuntimeError("V24_WORKER_FAILURE_IDENTITY_CHANGED")
    reason = _v24_failure_reason(worker)
    if reason is None:
        raise RuntimeError("V24_WORKER_FAILURE_REASON_MISSING")
    return {
        "completion_ordinal": int(ordinal + 1),
        "candidate_id": candidate_id,
        "candidate_spec_sha256": str(selected["candidate_spec_sha256"]),
        "behavior_family_id": str(selected["behavior_family_id"]),
        "arm": str(selected["arm"]),
        "source_arm": str(selected["source_arm"]),
        "seed": int(selected["seed"]),
        "horizon_hours": int(selected["horizon_hours"]),
        "train_search_reward": float(selected["search_reward"]),
        "train_orientation": float(selected["train_orientation"]),
        "evaluation_partition": "validation",
        "validation_status": "CANDIDATE_LOCAL_FAILURE",
        "validation_failure_reason": reason,
        "strict_evaluated": False,
        "comparison_included": False,
        "pair_reward": float("nan"),
        "matched_positive": False,
        "primary_gross_mean": float("nan"),
        "primary_net_mean": float("nan"),
        "primary_turnover_mean": float("nan"),
        "primary_cost_mean": float("nan"),
        "primary_net_5bps_path_mean": float("nan"),
        "primary_net_10bps_path_mean": float("nan"),
        "matched_net_5bps_path_mean": float("nan"),
        "matched_net_10bps_path_mean": float("nan"),
        "economic_receipt_sha256": str(economic_receipt_sha256),
        "process_cpu_seconds": float(worker["process_cpu_seconds"]),
        "wall_seconds": float(worker["wall_seconds"]),
        "worker_rss_bytes": int(worker["worker_rss_bytes"]),
        "worker_private_bytes": int(worker["worker_private_bytes"]),
        "candidate_generation_performed": False,
        "optimizer_feedback_written": False,
        "policy_memory_written": False,
        "archive_written": False,
        "fresh_data_read": True,
    }


def _v24_write_batch_projections(
    root: Path,
    *,
    base_ordinal: int,
    selected_rows: Sequence[Mapping[str, Any]],
    worker_rows: Sequence[Mapping[str, Any]],
    economic_receipt_sha256: str,
    persist_candidate_local_failures: bool,
) -> list[dict[str, Any]]:
    if len(selected_rows) != len(worker_rows):
        raise RuntimeError("V24_WORKER_BATCH_COUNT_CHANGED")
    output: list[dict[str, Any]] = []
    for offset, (selected, worker) in enumerate(
        zip(selected_rows, worker_rows)
    ):
        if worker.get("error"):
            if not persist_candidate_local_failures:
                raise RuntimeError(
                    "V24_CANDIDATE_LOCAL_FAILURE:"
                    f"{worker['candidate_id']}:{worker['error']}"
                )
            output.append(
                _v24_write_candidate_failure_projection(
                    ordinal=base_ordinal + offset,
                    selected=selected,
                    worker=worker,
                    economic_receipt_sha256=economic_receipt_sha256,
                )
            )
        else:
            output.append(
                _v24_write_candidate_projection(
                    root,
                    ordinal=base_ordinal + offset,
                    selected=selected,
                    worker=worker,
                    economic_receipt_sha256=economic_receipt_sha256,
                )
            )
    return output


def _v24_write_candidate_projection(
    root: Path,
    *,
    ordinal: int,
    selected: Mapping[str, Any],
    worker: Mapping[str, Any],
    economic_receipt_sha256: str,
) -> dict[str, Any]:
    evaluation = dict(worker["evaluation"])
    candidate_id = str(selected["candidate_id"])
    if (
        str(worker["candidate_id"]) != candidate_id
        or str(evaluation.get("candidate_id") or "") != candidate_id
        or evaluation.get("evaluation_partition") != "validation"
        or evaluation.get("train_orientation_fitted") is not False
        or float(evaluation.get("train_orientation", float("nan")))
        != float(selected["train_orientation"])
    ):
        raise RuntimeError("V24_WORKER_EVALUATION_IDENTITY_CHANGED")
    projection = build_economic_path_artifacts(
        evaluation,
        cohort="behavior_family_train_top",
        arm=str(selected["arm"]),
        seed=int(selected["seed"]),
        horizon_hours=int(selected["horizon_hours"]),
        candidate_spec_sha256=str(selected["candidate_spec_sha256"]),
        economic_receipt_sha256=str(economic_receipt_sha256),
        evaluation_partition="validation",
        execution_venue="BINANCE_USD_M",
    )
    local = root / "paths" / f"{ordinal:04d}_{candidate_id[:16]}"
    local.mkdir(parents=True)
    names = {
        "hourly_sleeves": "economic_hourly_sleeves.parquet",
        "daily_sleeves": "economic_daily_sleeves.parquet",
        "asset_positions": "economic_asset_positions.parquet",
    }
    for key, name in names.items():
        pd.DataFrame(projection[key]).to_parquet(local / name, index=False)
    hourly = projection["hourly_sleeves"]
    primary = [
        row
        for row in hourly
        if row["sleeve"] == "primary" and bool(row["objective_mask"])
    ]
    incremental = [
        row
        for row in hourly
        if row["sleeve"] != "primary"
        and "control" not in str(row["sleeve"])
        and bool(row["objective_mask"])
    ]
    primary_net_5 = _finite_mean(
        np.asarray([row["net_5bps"] for row in primary], dtype=float)
    )
    primary_net_10 = _finite_mean(
        np.asarray([row["net_10bps"] for row in primary], dtype=float)
    )
    matched_net_5 = _finite_mean(
        np.asarray([row["net_5bps"] for row in incremental], dtype=float)
    )
    matched_net_10 = _finite_mean(
        np.asarray([row["net_10bps"] for row in incremental], dtype=float)
    )
    primary_metrics = dict(evaluation.get("primary") or {})
    return {
        "completion_ordinal": int(ordinal + 1),
        "candidate_id": candidate_id,
        "candidate_spec_sha256": str(selected["candidate_spec_sha256"]),
        "behavior_family_id": str(selected["behavior_family_id"]),
        "arm": str(selected["arm"]),
        "source_arm": str(selected["source_arm"]),
        "seed": int(selected["seed"]),
        "horizon_hours": int(selected["horizon_hours"]),
        "train_search_reward": float(selected["search_reward"]),
        "train_orientation": float(selected["train_orientation"]),
        "evaluation_partition": "validation",
        "validation_status": "EVALUATED",
        "validation_failure_reason": None,
        "strict_evaluated": True,
        "comparison_included": False,
        "pair_reward": float(evaluation["pair_reward"]),
        "matched_positive": bool(evaluation["matched_positive"]),
        "primary_gross_mean": float(primary_metrics.get("gross_mean", float("nan"))),
        "primary_net_mean": float(primary_metrics.get("net_mean", float("nan"))),
        "primary_turnover_mean": float(
            primary_metrics.get("turnover_mean", float("nan"))
        ),
        "primary_cost_mean": float(primary_metrics.get("cost_mean", float("nan"))),
        "primary_net_5bps_path_mean": primary_net_5,
        "primary_net_10bps_path_mean": primary_net_10,
        "matched_net_5bps_path_mean": matched_net_5,
        "matched_net_10bps_path_mean": matched_net_10,
        "economic_receipt_sha256": str(economic_receipt_sha256),
        "process_cpu_seconds": float(worker["process_cpu_seconds"]),
        "wall_seconds": float(worker["wall_seconds"]),
        "worker_rss_bytes": int(worker["worker_rss_bytes"]),
        "worker_private_bytes": int(worker["worker_private_bytes"]),
        "candidate_generation_performed": False,
        "optimizer_feedback_written": False,
        "policy_memory_written": False,
        "archive_written": False,
        "fresh_data_read": True,
    }


def _v24_mark_equal_count_comparison(
    rows: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Mark an equal source-ordinal prefix per arm, seed, and horizon."""

    output = [{**dict(row), "comparison_included": False} for row in rows]
    arms = (
        "expanded_mechanism_random_v2_4",
        "mechanism_evolution_v2_4",
    )
    equal_counts: dict[str, int] = {}
    for seed in (359914106, 1141399971):
        for horizon in (1, 4):
            by_arm: dict[str, list[int]] = {}
            for arm in arms:
                by_arm[arm] = sorted(
                    (
                        index
                        for index, row in enumerate(output)
                        if bool(row["strict_evaluated"])
                        and str(row["arm"]) == arm
                        and int(row["seed"]) == seed
                        and int(row["horizon_hours"]) == horizon
                    ),
                    key=lambda index: int(output[index]["completion_ordinal"]),
                )
            count = min(len(by_arm[arm]) for arm in arms)
            if count <= 0:
                equal_counts[f"{seed}:{horizon}"] = 0
                continue
            equal_counts[f"{seed}:{horizon}"] = int(count)
            for arm in arms:
                for index in by_arm[arm][:count]:
                    output[index]["comparison_included"] = True
    return output, equal_counts


def _v24_restore_checkpoints(
    runtime_root: Path,
    *,
    frozen_hash: str,
    selection_hash: str,
) -> list[dict[str, Any]]:
    root = runtime_root / "checkpoints"
    rows: list[dict[str, Any]] = []
    for expected_index, path in enumerate(
        sorted(item for item in root.glob("checkpoint_*") if item.is_dir())
    ):
        if path.name != f"checkpoint_{expected_index:03d}":
            raise RuntimeError("V24_CHECKPOINT_SEQUENCE_CHANGED")
        manifest = json.loads((path / "manifest.json").read_text(encoding="utf-8"))
        saved = str(manifest.pop("manifest_sha256", ""))
        if (
            _canonical_sha256(manifest) != saved
            or manifest.get("frozen_contract_sha256") != frozen_hash
            or manifest.get("selection_receipt_sha256") != selection_hash
            or manifest.get("files") != _v24_checkpoint_files(path)
        ):
            raise RuntimeError("V24_CHECKPOINT_RESTORE_FAILED")
        local = pd.read_parquet(path / "candidate_ledger.parquet").to_dict("records")
        if len(local) != 64:
            raise RuntimeError("V24_CHECKPOINT_ROW_COUNT_CHANGED")
        rows.extend(local)
    return rows


def _v24_concat_parquet(inputs: Sequence[Path], output: Path) -> None:
    import pyarrow.parquet as parquet

    temporary = output.with_name(output.name + f".tmp-{os.getpid()}")
    writer = None
    try:
        for path in inputs:
            table = parquet.read_table(path)
            if writer is None:
                writer = parquet.ParquetWriter(temporary, table.schema)
            writer.write_table(table)
        if writer is None:
            raise RuntimeError("V24_PARQUET_INPUTS_EMPTY")
        writer.close()
        writer = None
        os.replace(temporary, output)
    finally:
        if writer is not None:
            writer.close()
        if temporary.exists():
            temporary.unlink()


def run_v24_fresh_gate(
    repo_root: Path,
    *,
    runtime_date: str = V24_DEFAULT_RUNTIME_DATE,
    producer_source_sha: str | None = None,
    finalize_only: bool = False,
) -> dict[str, Any]:
    """Evaluate the one frozen 512-family cohort on fresh July data."""

    is_repair_replay = str(runtime_date) == V24_REPAIR_DEFAULT_RUNTIME_DATE
    if finalize_only and not is_repair_replay:
        raise ValueError("V24_FINALIZE_ONLY_REQUIRES_REPAIR_REPLAY")
    if str(runtime_date) not in {
        V24_DEFAULT_RUNTIME_DATE,
        V24_REPAIR_DEFAULT_RUNTIME_DATE,
    }:
        raise ValueError("V24_RUNTIME_DATE_CHANGED")
    if is_repair_replay:
        receipt = load_v24_repair_run_receipt(
            repo_root,
            require_authorized=not finalize_only,
        )
        if finalize_only and (
            receipt.get("status")
            != "RUN_AUTHORIZED_ONE_TIME_REPAIR_REPLAY"
            or receipt.get("run_authorized") is not True
        ):
            raise RuntimeError("V24_REPAIR_FINALIZATION_AUTHORITY_CHANGED")
        runtime_prefix = V24_REPAIR_RUNTIME_PREFIX
        run_receipt_path = V24_REPAIR_RUN_RECEIPT_PATH
    else:
        receipt = load_v24_run_receipt(repo_root, require_authorized=True)
        runtime_prefix = V24_RUNTIME_PREFIX
        run_receipt_path = V24_RUN_RECEIPT_PATH
    selection = _load_v24_selection(
        repo_root,
        runtime_date=V24_DEFAULT_RUNTIME_DATE,
    )
    observed_source = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=repo_root, text=True
    ).strip().lower()
    source_sha = str(producer_source_sha or observed_source).lower()
    if not finalize_only and (
        source_sha != observed_source
        or (
            not is_repair_replay
            and source_sha
            != str(selection["producer_source_sha"]).lower()
        )
    ):
        raise RuntimeError("V24_RUN_SOURCE_SHA_CHANGED")
    tracked = subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        cwd=repo_root,
        text=True,
    ).strip()
    if tracked:
        raise RuntimeError("V24_RUN_REQUIRES_CLEAN_TRACKED_TREE")
    source_runtime_root = (
        Path(repo_root)
        / "runtime"
        / f"{V24_RUNTIME_PREFIX}_{V24_DEFAULT_RUNTIME_DATE}"
    )
    runtime_root = Path(repo_root) / "runtime" / f"{runtime_prefix}_{runtime_date}"
    carrier_path = source_runtime_root / "aligned_carrier_manifest.json"
    economic_path = source_runtime_root / "economic_context.json"
    if not carrier_path.is_file() or not economic_path.is_file():
        raise RuntimeError("V24_FRESH_CARRIER_NOT_PREPARED")
    carrier = json.loads(carrier_path.read_text(encoding="utf-8"))
    carrier_hash = str(carrier.pop("manifest_sha256", ""))
    if _canonical_sha256(carrier) != carrier_hash:
        raise RuntimeError("V24_CARRIER_MANIFEST_CHANGED")
    economic = json.loads(economic_path.read_text(encoding="utf-8"))
    if str(economic.get("receipt_sha256") or "") != str(
        selection["economic_receipt_sha256"]
    ):
        raise RuntimeError("V24_ECONOMIC_RECEIPT_IDENTITY_CHANGED")
    source = dict(receipt["source_train"])
    train = pd.read_parquet(Path(repo_root) / source["candidate_ledger_path"])
    train_lookup = train.set_index("candidate_id").to_dict("index")
    selected_rows: list[dict[str, Any]] = []
    for frozen in selection["selected_candidates"]:
        candidate_id = str(frozen["candidate_id"])
        row = dict(train_lookup.get(candidate_id) or {})
        if not row:
            raise RuntimeError("V24_SELECTED_TRAIN_CANDIDATE_MISSING")
        candidate_payload = json.loads(str(row["candidate_spec_json"]))
        if (
            _canonical_sha256(candidate_payload)
            != str(frozen["candidate_spec_sha256"])
            or str(row["behavior_family_id"])
            != str(frozen["behavior_family_id"])
            or str(V24_SOURCE_ARM_MAPPING[str(row["arm"])])
            != str(frozen["arm"])
            or row.get("train_orientation_fitted") is not True
            or str(row.get("evaluation_partition") or "") != "train"
        ):
            raise RuntimeError("V24_SELECTED_TRAIN_BINDING_CHANGED")
        selected_rows.append(
            {
                **dict(frozen),
                "source_arm": str(row["arm"]),
                "train_orientation": float(row["train_orientation"]),
                "candidate": candidate_payload,
            }
        )
    if len(selected_rows) != int(receipt["selection"]["candidate_count_exact"]):
        raise RuntimeError("V24_SELECTED_COUNT_CHANGED")
    runtime_root.mkdir(parents=True, exist_ok=True)
    if is_repair_replay:
        sweep = sweep_v24_static_constructibility(
            selected_rows=selected_rows,
            contract_rows=carrier["contracts"],
        )
        if int(sweep["candidate_count"]) != 512:
            raise RuntimeError("V24_STATIC_CONSTRUCTIBILITY_COUNT_CHANGED")
        _write_json(runtime_root / "constructibility_sweep.json", sweep)
        for name in (
            "behavior_family_selection_receipt.json",
            "aligned_carrier_manifest.json",
            "economic_context.json",
        ):
            source_path = source_runtime_root / name
            target_path = runtime_root / name
            if target_path.is_file():
                if _file_sha256(target_path) != _file_sha256(source_path):
                    raise RuntimeError(f"V24_REPAIR_SOURCE_COPY_CHANGED:{name}")
            else:
                shutil.copyfile(source_path, target_path)
    frozen_payload = {
        "schema_version": 1,
        "experiment_id": str(receipt["experiment_id"]),
        "producer_source_sha": source_sha,
        "run_receipt_path": run_receipt_path,
        "run_receipt_file_sha256": _file_sha256(
            Path(repo_root) / run_receipt_path
        ),
        "source_contract_path": V24_CONTRACT_PATH,
        "source_contract_sha256": _file_sha256(
            Path(repo_root) / V24_CONTRACT_PATH
        ),
        "selection_receipt_sha256": selection["receipt_sha256"],
        "selection_cohort_sha256": selection["selection_receipt"][
            "cohort_sha256"
        ],
        "carrier_manifest_sha256": carrier_hash,
        "carrier_cache_identity_sha256": carrier["cache_identity_sha256"],
        "target_cache_identity_sha256": carrier["target_cache"][
            "identity_sha256"
        ],
        "fresh_validation": dict(receipt["fresh_validation"]),
        "candidate_count": len(selected_rows),
        "workers_initial": int(receipt["compute"]["workers_default"]),
        "workers_memory_fallback": int(
            receipt["compute"]["workers_memory_fallback"]
        ),
        "checkpoint_size": int(receipt["selection"]["checkpoint_size"]),
        "checkpoint_count": int(receipt["selection"]["checkpoint_count"]),
        "candidate_local_failure_action": (
            "PERSIST_NO_BACKFILL" if is_repair_replay else "FAIL_CAMPAIGN"
        ),
        "source_runtime": source_runtime_root.relative_to(repo_root).as_posix(),
        "candidate_generation_performed": False,
        "optimizer_feedback_written": False,
        "policy_memory_written": False,
        "archive_written": False,
        "promotion_authorized": False,
    }
    frozen_path = runtime_root / "frozen_contract.json"
    if finalize_only:
        if not frozen_path.is_file():
            raise RuntimeError("V24_REPAIR_FROZEN_CONTRACT_MISSING")
        frozen = json.loads(frozen_path.read_text(encoding="utf-8"))
        saved_frozen_hash = str(frozen.get("frozen_contract_sha256") or "")
        frozen_without_hash = dict(frozen)
        frozen_without_hash.pop("frozen_contract_sha256", None)
        if (
            _canonical_sha256(frozen_without_hash) != saved_frozen_hash
            or str(frozen.get("producer_source_sha") or "").lower()
            != source_sha
        ):
            raise RuntimeError("V24_REPAIR_FROZEN_CONTRACT_CHANGED")
    else:
        frozen = {
            **frozen_payload,
            "frozen_contract_sha256": _canonical_sha256(frozen_payload),
        }
        if frozen_path.is_file():
            if json.loads(frozen_path.read_text(encoding="utf-8")) != frozen:
                raise RuntimeError("V24_EXISTING_FROZEN_CONTRACT_CHANGED")
        else:
            _write_json(frozen_path, frozen)
    if (runtime_root / "final_decision.json").is_file():
        raise FileExistsError("V24_FRESH_GATE_ALREADY_TERMINAL")
    frozen_hash = str(frozen["frozen_contract_sha256"])
    restored = _v24_restore_checkpoints(
        runtime_root,
        frozen_hash=frozen_hash,
        selection_hash=str(selection["receipt_sha256"]),
    )
    prefix = [str(row["candidate_id"]) for row in selected_rows[: len(restored)]]
    if [str(row["candidate_id"]) for row in restored] != prefix:
        raise RuntimeError("V24_CHECKPOINT_SELECTION_PREFIX_CHANGED")
    completed_rows = list(restored)
    fresh = dict(receipt["fresh_validation"])
    cache_root = Path(repo_root) / str(receipt["carrier"]["aligned_cache"])
    target_root = Path(repo_root) / str(receipt["carrier"]["target_cache"])
    started = time.perf_counter()
    active_workers = int(receipt["compute"]["workers_default"])
    memory_fallback_used = False

    def write_status(status: str, checkpoint: str | None = None, **extra: Any) -> None:
        elapsed = time.perf_counter() - started
        _write_json(
            runtime_root / "producer_status.json",
            {
                "schema_version": 1,
                "status": status,
                "producer_pid": os.getpid(),
                "producer_source_sha": source_sha,
                "frozen_contract_sha256": frozen_hash,
                "heartbeat_utc": pd.Timestamp.now(tz="UTC").isoformat(),
                "completed_candidate_count": len(completed_rows),
                "strict_evaluated_count": sum(
                    bool(row.get("strict_evaluated")) for row in completed_rows
                ),
                "candidate_local_failure_count": sum(
                    str(row.get("validation_status"))
                    == "CANDIDATE_LOCAL_FAILURE"
                    for row in completed_rows
                ),
                "source_candidate_count": len(selected_rows),
                "checkpoint": checkpoint,
                "workers": active_workers,
                "memory_fallback_used": memory_fallback_used,
                "active_wall_seconds": elapsed,
                "pair_evaluated_per_hour": (
                    sum(
                        bool(row.get("strict_evaluated"))
                        for row in completed_rows
                    )
                    * 3600.0
                    / elapsed
                    if elapsed > 0
                    else 0.0
                ),
                "candidate_generation_performed": False,
                "optimizer_feedback_written": False,
                "policy_memory_written": False,
                "archive_written": False,
                **extra,
            },
        )

    def make_executor(workers: int) -> concurrent.futures.ProcessPoolExecutor:
        return concurrent.futures.ProcessPoolExecutor(
            max_workers=workers,
            initializer=_v24_worker_initialize,
            initargs=(
                str(cache_root),
                str(target_root),
                carrier["contracts"],
                economic,
                str(fresh["start"]),
                str(fresh["end_exclusive"]),
                str(fresh["role"]),
            ),
        )

    write_status("V24_FRESH_GATE_STARTING")
    executor = make_executor(active_workers)
    try:
        while len(completed_rows) < len(selected_rows):
            checkpoint_index = len(completed_rows) // 64
            batch = selected_rows[len(completed_rows) : len(completed_rows) + 64]
            futures = [
                executor.submit(
                    _v24_worker_evaluate,
                    {
                        "candidate": row["candidate"],
                        "frozen_train_orientation": row["train_orientation"],
                    },
                )
                for row in batch
            ]
            results = [future.result() for future in futures]
            if any(bool(row["memory_error"]) for row in results):
                if memory_fallback_used:
                    raise MemoryError("V24_MEMORY_FALLBACK_EXHAUSTED")
                executor.shutdown(wait=True, cancel_futures=False)
                active_workers = int(
                    receipt["compute"]["workers_memory_fallback"]
                )
                memory_fallback_used = True
                write_status("V24_MEMORY_FALLBACK_TO_8")
                executor = make_executor(active_workers)
                results = [
                    future.result()
                    for future in [
                        executor.submit(
                            _v24_worker_evaluate,
                            {
                                "candidate": row["candidate"],
                                "frozen_train_orientation": row["train_orientation"],
                            },
                        )
                        for row in batch
                    ]
                ]
                if any(bool(row["memory_error"]) for row in results):
                    raise MemoryError("V24_MEMORY_FALLBACK_EXHAUSTED")
            if not is_repair_replay:
                failure = next((row for row in results if row["error"]), None)
                if failure is not None:
                    write_status(
                        "V24_FRESH_GATE_FAILED_CANDIDATE_LOCAL",
                        failure_candidate_id=failure["candidate_id"],
                        failure_reason=failure["error"],
                    )
                    raise RuntimeError(
                        "V24_CANDIDATE_LOCAL_FAILURE:"
                        f"{failure['candidate_id']}:{failure['error']}"
                    )
            else:
                for worker in results:
                    _v24_failure_reason(worker)
            checkpoint_root = runtime_root / "checkpoints"
            checkpoint_root.mkdir(parents=True, exist_ok=True)
            target = checkpoint_root / f"checkpoint_{checkpoint_index:03d}"
            if target.exists():
                raise FileExistsError("V24_CHECKPOINT_ALREADY_EXISTS")
            temporary = checkpoint_root / (
                f".checkpoint_{checkpoint_index:03d}.tmp-{os.getpid()}"
            )
            if temporary.exists():
                shutil.rmtree(temporary)
            temporary.mkdir()
            local_rows: list[dict[str, Any]] = []
            try:
                base_ordinal = len(completed_rows)
                local_rows = _v24_write_batch_projections(
                    temporary,
                    base_ordinal=base_ordinal,
                    selected_rows=batch,
                    worker_rows=results,
                    economic_receipt_sha256=str(
                        selection["economic_receipt_sha256"]
                    ),
                    persist_candidate_local_failures=is_repair_replay,
                )
                pd.DataFrame(local_rows).to_parquet(
                    temporary / "candidate_ledger.parquet", index=False
                )
                manifest = {
                    "schema_version": 1,
                    "status": "V24_CHECKPOINT_COMPLETE",
                    "checkpoint_index": checkpoint_index,
                    "producer_source_sha": source_sha,
                    "frozen_contract_sha256": frozen_hash,
                    "selection_receipt_sha256": selection["receipt_sha256"],
                    "completed_candidate_count": len(completed_rows)
                    + len(local_rows),
                    "checkpoint_candidate_count": len(local_rows),
                    "strict_evaluated_count": sum(
                        bool(row.get("strict_evaluated"))
                        for row in (*completed_rows, *local_rows)
                    ),
                    "checkpoint_strict_evaluated_count": sum(
                        bool(row.get("strict_evaluated")) for row in local_rows
                    ),
                    "candidate_local_failure_count": sum(
                        str(row.get("validation_status"))
                        == "CANDIDATE_LOCAL_FAILURE"
                        for row in (*completed_rows, *local_rows)
                    ),
                    "workers": active_workers,
                    "memory_fallback_used": memory_fallback_used,
                    "files": _v24_checkpoint_files(temporary),
                }
                manifest["manifest_sha256"] = _canonical_sha256(manifest)
                _write_json(temporary / "manifest.json", manifest)
                os.replace(temporary, target)
            finally:
                if temporary.exists():
                    shutil.rmtree(temporary)
            completed_rows.extend(local_rows)
            label = f"checkpoint_{checkpoint_index:03d}"
            write_status("V24_FRESH_GATE_RUNNING", checkpoint=label)
            elapsed = time.perf_counter() - started
            if elapsed > int(
                receipt["compute"]["evaluation_wall_time_seconds_maximum"]
            ):
                write_status("ENGINE_BUDGET_EXHAUSTED", checkpoint=label)
                raise RuntimeError("ENGINE_BUDGET_EXHAUSTED")
            throughput = (
                sum(bool(row.get("strict_evaluated")) for row in completed_rows)
                * 3600.0
                / max(elapsed, 1.0e-9)
            )
            if throughput < float(
                receipt["compute"]["minimum_pair_evaluated_per_hour"]
            ):
                write_status("ENGINE_THROUGHPUT_FLOOR_FAILED", checkpoint=label)
                raise RuntimeError("ENGINE_THROUGHPUT_FLOOR_FAILED")
    except BaseException:
        if not (runtime_root / "producer_status.json").is_file():
            write_status("V24_FRESH_GATE_FAILED")
        raise
    finally:
        executor.shutdown(wait=True, cancel_futures=False)
    checkpoints = sorted((runtime_root / "checkpoints").glob("checkpoint_*"))
    if len(checkpoints) != 8 or len(completed_rows) != 512:
        raise RuntimeError("V24_TERMINAL_COUNT_CHANGED")
    pd.DataFrame(selection["selected_candidates"]).to_parquet(
        runtime_root / "behavior_family_selection.parquet", index=False
    )
    if is_repair_replay:
        completed_rows, equal_counts = _v24_mark_equal_count_comparison(
            completed_rows
        )
    else:
        completed_rows = [
            {**dict(row), "comparison_included": True} for row in completed_rows
        ]
        equal_counts = {
            f"{seed}:{horizon}": 64
            for seed in (359914106, 1141399971)
            for horizon in (1, 4)
        }
    evaluated_rows = [
        row for row in completed_rows if bool(row.get("strict_evaluated"))
    ]
    failure_rows = [
        row
        for row in completed_rows
        if str(row.get("validation_status")) == "CANDIDATE_LOCAL_FAILURE"
    ]
    comparison_rows = [
        row for row in completed_rows if bool(row.get("comparison_included"))
    ]
    pd.DataFrame(completed_rows).to_parquet(
        runtime_root / "candidate_ledger.parquet", index=False
    )
    path_names = {
        "economic_hourly_sleeves.parquet": "economic_hourly_sleeves.parquet",
        "economic_daily_sleeves.parquet": "economic_daily_sleeves.parquet",
        "economic_asset_positions.parquet": "economic_asset_positions.parquet",
    }
    for output_name, source_name in path_names.items():
        inputs = sorted(
            path
            for checkpoint in checkpoints
            for path in checkpoint.glob(f"paths/*/{source_name}")
        )
        if len(inputs) != len(evaluated_rows):
            raise RuntimeError("V24_ECONOMIC_PATH_SHARD_COUNT_CHANGED")
        _v24_concat_parquet(inputs, runtime_root / output_name)

    def summarize_arms(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
        summaries: dict[str, Any] = {}
        for arm, local in pd.DataFrame(rows).groupby("arm"):
            summaries[str(arm)] = {
                "candidate_count": int(len(local)),
                "behavior_family_count": int(
                    local["behavior_family_id"].nunique()
                ),
                "matched_positive_count": int(local["matched_positive"].sum()),
                "mean_pair_reward": float(local["pair_reward"].mean()),
                "primary_net_5bps_path_mean": float(
                    local["primary_net_5bps_path_mean"].mean()
                ),
                "primary_net_10bps_path_mean": float(
                    local["primary_net_10bps_path_mean"].mean()
                ),
                "matched_net_5bps_path_mean": float(
                    local["matched_net_5bps_path_mean"].mean()
                ),
                "matched_net_10bps_path_mean": float(
                    local["matched_net_10bps_path_mean"].mean()
                ),
            }
        return summaries

    arm_summaries = summarize_arms(comparison_rows)
    all_evaluated_arm_summaries = summarize_arms(evaluated_rows)
    random_arm = arm_summaries["expanded_mechanism_random_v2_4"]
    evolution_arm = arm_summaries["mechanism_evolution_v2_4"]
    decision = {
        "schema_version": 1,
        "status": (
            "PASS_V24_REPAIR_REPLAY_COMPLETE"
            if is_repair_replay
            else "PASS_V24_FRESH_BEHAVIOR_FAMILY_GATE_COMPLETE"
        ),
        "classification": "FRESH_DATA_VALIDATION_EVIDENCE_NO_PROMOTION",
        "producer_source_sha": source_sha,
        "finalizer_source_sha": observed_source,
        "selected_behavior_family_count": 512,
        "source_candidate_count": 512,
        "strict_evaluated_count": len(evaluated_rows),
        "candidate_local_failure_count": len(failure_rows),
        "candidate_local_failures": [
            {
                "completion_ordinal": int(row["completion_ordinal"]),
                "candidate_id": str(row["candidate_id"]),
                "arm": str(row["arm"]),
                "seed": int(row["seed"]),
                "horizon_hours": int(row["horizon_hours"]),
                "reason": str(row["validation_failure_reason"]),
            }
            for row in failure_rows
        ],
        "checkpoint_count": 8,
        "checkpoint_restore_verified": True,
        "workers_final": active_workers,
        "memory_fallback_used": memory_fallback_used,
        "active_wall_seconds": time.perf_counter() - started,
        "absolute_zero_benchmark": 0.0,
        "arm_summaries": arm_summaries,
        "all_evaluated_arm_summaries": all_evaluated_arm_summaries,
        "equal_comparison_count_by_seed_horizon": equal_counts,
        "evolution_minus_random": {
            key: float(evolution_arm[key]) - float(random_arm[key])
            for key in (
                "mean_pair_reward",
                "primary_net_5bps_path_mean",
                "primary_net_10bps_path_mean",
                "matched_net_5bps_path_mean",
                "matched_net_10bps_path_mean",
            )
        },
        "candidate_generation_performed": False,
        "optimizer_feedback_written": False,
        "policy_memory_written": False,
        "archive_written": False,
        "oos": False,
        "arm_qualified": [],
        "promotion_authorized": False,
        "next_search_started": False,
    }
    _write_json(runtime_root / "final_decision.json", decision)
    write_status(
        (
            "V24_REPAIR_REPLAY_COMPLETE"
            if is_repair_replay
            else "V24_FRESH_GATE_COMPLETE"
        ),
        checkpoint="checkpoint_007",
    )
    artifact_names = [
        "behavior_family_selection_receipt.json",
        "aligned_carrier_manifest.json",
        "economic_context.json",
        "frozen_contract.json",
        "producer_status.json",
        "behavior_family_selection.parquet",
        "candidate_ledger.parquet",
        *path_names,
        "final_decision.json",
    ]
    if is_repair_replay:
        artifact_names.append("constructibility_sweep.json")
    manifest = {
        "schema_version": 1,
        "experiment_id": str(receipt["experiment_id"]),
        "producer_source_sha": source_sha,
        "finalizer_source_sha": observed_source,
        "frozen_contract_sha256": frozen_hash,
        "selection_receipt_sha256": selection["receipt_sha256"],
        "source_candidate_count": 512,
        "strict_evaluated_count": len(evaluated_rows),
        "candidate_local_failure_count": len(failure_rows),
        "checkpoint_count": 8,
        "files": [
            {
                "path": name,
                "bytes": (runtime_root / name).stat().st_size,
                "sha256": _file_sha256(runtime_root / name),
            }
            for name in artifact_names
        ],
        "candidate_generation_performed": False,
        "optimizer_feedback_written": False,
        "policy_memory_written": False,
        "archive_written": False,
        "promotion_started": False,
    }
    manifest["artifact_bundle_sha256"] = _canonical_sha256(manifest["files"])
    _write_json(runtime_root / "run_manifest.json", manifest)
    report = (
        Path(repo_root)
        / "reports"
        / f"CRYPTO_SEARCH_ENGINE_V2_4_{runtime_date}.md"
    )
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(
        "\n".join(
            [
                f"# Crypto Search Engine V2.4 ({runtime_date})",
                "",
                "- Evidence: fresh-data validation only; no OOS or promotion.",
                (
                    "- Frozen behavior families: `512`; strict evaluated: "
                    f"`{len(evaluated_rows)}`; candidate-local failures: "
                    f"`{len(failure_rows)}`."
                ),
                f"- Checkpoints: `8`; workers final: `{active_workers}`.",
                (
                    "- Evolution minus random mean pair reward: "
                    f"`{decision['evolution_minus_random']['mean_pair_reward']:.12f}`."
                ),
                (
                    "- Evolution minus random primary net at 5 bps: "
                    f"`{decision['evolution_minus_random']['primary_net_5bps_path_mean']:.12f}`."
                ),
                (
                    "- Evolution minus random matched net at 5 bps: "
                    f"`{decision['evolution_minus_random']['matched_net_5bps_path_mean']:.12f}`."
                ),
                "",
                "Complete hourly, daily, and sparse asset-level economic paths are persisted.",
                "No candidate replacement/backfill, generation, optimizer/archive/policy write, tuning, reseed, OOS, or promotion occurred.",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    return {**decision, "artifact_bundle_sha256": manifest["artifact_bundle_sha256"]}


def check_v24_fresh_gate(
    repo_root: Path,
    *,
    runtime_date: str = V24_DEFAULT_RUNTIME_DATE,
) -> dict[str, Any]:
    is_repair_replay = str(runtime_date) == V24_REPAIR_DEFAULT_RUNTIME_DATE
    if str(runtime_date) not in {
        V24_DEFAULT_RUNTIME_DATE,
        V24_REPAIR_DEFAULT_RUNTIME_DATE,
    }:
        raise ValueError("V24_RUNTIME_DATE_CHANGED")
    if is_repair_replay:
        receipt = load_v24_repair_run_receipt(
            repo_root,
            require_authorized=False,
        )
        runtime_prefix = V24_REPAIR_RUNTIME_PREFIX
    else:
        receipt = load_v24_run_receipt(repo_root, require_authorized=False)
        runtime_prefix = V24_RUNTIME_PREFIX
    runtime_root = (
        Path(repo_root) / "runtime" / f"{runtime_prefix}_{runtime_date}"
    )
    manifest = json.loads(
        (runtime_root / "run_manifest.json").read_text(encoding="utf-8")
    )
    decision = json.loads(
        (runtime_root / "final_decision.json").read_text(encoding="utf-8")
    )
    errors: list[str] = []
    strict_evaluated = int(decision.get("strict_evaluated_count", -1))
    failure_count = int(decision.get("candidate_local_failure_count", -1))
    if (
        strict_evaluated <= 0
        or strict_evaluated + failure_count != 512
        or manifest.get("source_candidate_count", 512) != 512
        or manifest.get("strict_evaluated_count") != strict_evaluated
        or manifest.get("candidate_local_failure_count", 0) != failure_count
        or manifest.get("checkpoint_count") != 8
        or decision.get("checkpoint_restore_verified") is not True
    ):
        errors.append("terminal_count")
    ledger = pd.read_parquet(runtime_root / "candidate_ledger.parquet")
    selection = _load_v24_selection(
        repo_root,
        runtime_date=V24_DEFAULT_RUNTIME_DATE,
    )
    if (
        len(ledger) != 512
        or ledger["candidate_id"].duplicated().any()
        or ledger["behavior_family_id"].isna().any()
        or int(ledger["strict_evaluated"].sum()) != strict_evaluated
        or ledger["candidate_id"].astype(str).tolist()
        != [
            str(row["candidate_id"])
            for row in selection["selected_candidates"]
        ]
    ):
        errors.append("candidate_ledger")
    failed = ledger.loc[~ledger["strict_evaluated"].astype(bool)]
    if (
        len(failed) != failure_count
        or set(failed["validation_status"].astype(str))
        - {"CANDIDATE_LOCAL_FAILURE"}
        or set(failed["validation_failure_reason"].astype(str))
        - set(V24_CANDIDATE_LOCAL_FAILURES)
    ):
        errors.append("candidate_local_failures")
    compared = ledger.loc[ledger["comparison_included"].astype(bool)]
    comparison_counts = {
        (str(arm), int(seed), int(horizon)): int(len(local))
        for (arm, seed, horizon), local in compared.groupby(
            ["arm", "seed", "horizon_hours"]
        )
    }
    for seed in (359914106, 1141399971):
        for horizon in (1, 4):
            if comparison_counts.get(
                ("expanded_mechanism_random_v2_4", seed, horizon)
            ) != comparison_counts.get(
                ("mechanism_evolution_v2_4", seed, horizon)
            ):
                errors.append(f"equal_count:{seed}:{horizon}")
    for item in manifest.get("files") or ():
        path = runtime_root / str(item["path"])
        if (
            not path.is_file()
            or path.stat().st_size != int(item["bytes"])
            or _file_sha256(path) != str(item["sha256"])
        ):
            errors.append(f"file:{item['path']}")
    if any(
        bool(manifest.get(field))
        for field in (
            "candidate_generation_performed",
            "optimizer_feedback_written",
            "policy_memory_written",
            "archive_written",
            "promotion_started",
        )
    ):
        errors.append("write_boundary")
    checkpoints = sorted((runtime_root / "checkpoints").glob("checkpoint_*"))
    if len(checkpoints) != int(receipt["selection"]["checkpoint_count"]):
        errors.append("checkpoints")
    if errors:
        raise RuntimeError("V24_FRESH_GATE_CHECK_FAILED:" + ",".join(errors))
    return {
        "status": (
            "PASS_V24_REPAIR_REPLAY_INDEPENDENT_CHECK"
            if is_repair_replay
            else "PASS_V24_FRESH_GATE_INDEPENDENT_CHECK"
        ),
        "source_candidate_count": len(ledger),
        "strict_evaluated_count": strict_evaluated,
        "candidate_local_failure_count": failure_count,
        "behavior_family_count": int(ledger["behavior_family_id"].nunique()),
        "checkpoint_count": len(checkpoints),
        "artifact_bundle_sha256": manifest["artifact_bundle_sha256"],
        "promotion_authorized": False,
    }


def load_v24_contract(repo_root: Path) -> dict[str, Any]:
    path = Path(repo_root) / V24_CONTRACT_PATH
    contract = json.loads(path.read_text(encoding="utf-8"))
    blockers: list[str] = []
    if contract.get("schema_version") != 1:
        blockers.append("schema_version")
    if contract.get("status") != "SOURCE_IMPLEMENTED_RUN_NOT_AUTHORIZED":
        blockers.append("status")
    if contract.get("run_authorized") is not False:
        blockers.append("run_authorized")
    selection = dict(contract.get("selection") or {})
    expected_selection = {
        "unit": "BEHAVIOR_FAMILY",
        "family_key": list(V24_FAMILY_KEY),
        "champion_authority": V24_SELECTION_AUTHORITY,
        "champion_order": list(V24_CHAMPION_ORDER),
        "expression_count_weighting": False,
        "validation_feedback_allowed": False,
        "oos_feedback_allowed": False,
        "duplicate_family_backfill_allowed": False,
        "seed_horizon_pooling_allowed": False,
        "cohort_count_rule": "EQUAL_COUNT_PER_ARM_SEED_HORIZON",
        "underfilled_cell_action": (
            "FAIL_CLOSED_NO_DUPLICATE_FAMILY_BACKFILL"
        ),
    }
    if selection != expected_selection:
        blockers.append("selection")
    evolution = dict(contract.get("evolution") or {})
    expected_evolution = {
        "population_unit": "EXISTING_BEHAVIOR_FAMILY_REWARD_CHAMPION",
        "parent_order_primary": "TRAIN_SEARCH_REWARD",
        "behavior_novelty_role": "DETERMINISTIC_TIE_BREAK_ONLY",
        "existing_typed_mutation_receipts_reused": True,
        "existing_compiler_reused": True,
        "existing_ast_reused": True,
        "existing_evaluator_reused": True,
    }
    if evolution != expected_evolution:
        blockers.append("evolution")
    fresh = dict(contract.get("fresh_data_gate") or {})
    expected_fresh = {
        "prior_holdout_end_exclusive": "2026-07-01T00:00:00Z",
        "admission_rule": "START_AT_OR_AFTER_PRIOR_HOLDOUT_END",
        "candidate_generation_during_gate": False,
        "adaptive_feedback_during_gate": False,
        "policy_memory_write_during_gate": False,
        "selection_frozen_before_read": True,
        "absolute_zero_benchmark_required": True,
        "typed_random_comparator_required": True,
        "cost_sensitivity_bps": [5.0, 10.0],
        "run_requires_new_user_authorization": True,
        "evaluation_partition": "validation",
        "execution_venue": "BINANCE_USD_M",
    }
    if fresh != expected_fresh:
        blockers.append("fresh_data_gate")
    required_paths = dict(contract.get("economic_path_artifacts") or {})
    expected_paths = {
        "required": True,
        "baseline_cost_bps": 5.0,
        "hourly_sleeve_path_fields": [
            "objective_mask",
            "gross",
            "cost",
            "turnover",
            "net",
            "cost_5bps",
            "net_5bps",
            "cost_10bps",
            "net_10bps",
        ],
        "daily_sleeve_path_fields": ["gross", "cost", "turnover", "net"],
        "sparse_asset_path_fields": ["weight", "asset_gross_contribution"],
        "identity_fields": [
            "candidate_id",
            "cohort",
            "arm",
            "seed",
            "horizon_hours",
            "sleeve",
            "execution_venue",
            "economic_receipt_sha256",
            "evaluation_partition",
            "asset_id",
            "timestamp_ns",
        ],
        "pair_evaluator_authority": (
            "alphafactory_crypto.broad_search.pair18m.evaluate_pair"
        ),
        "projection_symbol": (
            "alphafactory_crypto.broad_search.search_engine_v2_4."
            "build_economic_path_artifacts"
        ),
        "new_evaluator": False,
    }
    if required_paths != expected_paths:
        blockers.append("economic_path_artifacts")
    gate_adapter = dict(contract.get("gate_adapter") or {})
    expected_gate_adapter = {
        "selection_freeze_symbol": (
            "alphafactory_crypto.broad_search.search_engine_v2_4."
            "freeze_v24_gate_selection"
        ),
        "persistence_symbol": (
            "alphafactory_crypto.broad_search.search_engine_v2_4."
            "persist_v24_gate_bundle"
        ),
        "required_arms": [
            "expanded_mechanism_random_v2_4",
            "mechanism_evolution_v2_4",
        ],
        "market_read_performed": False,
        "candidate_evaluation_performed": False,
        "atomic_directory_rename": True,
        "manifest_required": True,
    }
    if gate_adapter != expected_gate_adapter:
        blockers.append("gate_adapter")
    component_sources = dict(contract.get("component_sources") or {})
    if set(component_sources) != {"pair_evaluator", "v24_adapter"}:
        blockers.append("component_sources.keys")
    historical_source_sha = ""
    historical_receipt_path = Path(repo_root) / V24_RUN_RECEIPT_PATH
    if historical_receipt_path.is_file():
        historical_source_sha = str(
            json.loads(
                historical_receipt_path.read_text(encoding="utf-8-sig")
            ).get("source_implementation_sha")
            or ""
        ).lower()
    for name, binding in component_sources.items():
        item = dict(binding)
        relative = str(item.get("path") or "")
        try:
            committed = _git_file_sha256(
                repo_root,
                historical_source_sha,
                relative,
            )
        except (OSError, subprocess.CalledProcessError):
            committed = ""
        if committed != str(item.get("sha256") or ""):
            blockers.append(f"component_sources.{name}")
    boundaries = dict(contract.get("boundaries") or {})
    expected_boundaries = {
        "market_search": False,
        "sealed_read": False,
        "oos": False,
        "forward": False,
        "recent": False,
        "challenge": False,
        "promotion": False,
        "new_evaluator": False,
        "new_ast": False,
        "new_compiler": False,
        "cross_sprint_adaptive_memory": False,
    }
    if boundaries != expected_boundaries:
        blockers.append("boundaries")
    if blockers:
        raise RuntimeError("V24_SOURCE_CONTRACT_BLOCKED:" + ",".join(blockers))
    return contract


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=(
            "check-source",
            "check-authority",
            "freeze-selection",
            "prepare-carrier",
            "run",
            "check",
            "check-repair-authority",
            "run-repair",
            "finalize-repair",
            "check-repair",
        ),
    )
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--runtime-date", default=V24_DEFAULT_RUNTIME_DATE)
    parser.add_argument("--source-sha")
    parser.add_argument("--top100-tar", type=Path)
    parser.add_argument("--ranks101-200-tar", type=Path)
    arguments = parser.parse_args(argv)
    if arguments.command == "check-source":
        contract = load_v24_contract(arguments.repo_root)
        result = {
            "status": "PASS_V24_SOURCE_ONLY",
            "run_authorized": contract["run_authorized"],
            "contract_sha256": _canonical_sha256(contract),
        }
    elif arguments.command == "check-authority":
        receipt = load_v24_run_receipt(
            arguments.repo_root, require_authorized=True
        )
        result = {
            "status": "PASS_V24_ONE_TIME_RUN_AUTHORITY",
            "run_authorized": receipt["run_authorized"],
            "source_implementation_sha": receipt["source_implementation_sha"],
            "receipt_file_sha256": _file_sha256(
                arguments.repo_root / V24_RUN_RECEIPT_PATH
            ),
        }
    elif arguments.command == "check-repair-authority":
        receipt = load_v24_repair_run_receipt(
            arguments.repo_root,
            require_authorized=True,
        )
        result = {
            "status": "PASS_V24_REPAIR_ONE_TIME_RUN_AUTHORITY",
            "run_authorized": receipt["run_authorized"],
            "source_implementation_sha": receipt["source_implementation_sha"],
            "receipt_file_sha256": _file_sha256(
                arguments.repo_root / V24_REPAIR_RUN_RECEIPT_PATH
            ),
        }
    elif arguments.command == "freeze-selection":
        result = freeze_v24_authorized_selection(
            arguments.repo_root,
            runtime_date=str(arguments.runtime_date),
            producer_source_sha=arguments.source_sha,
        )
    elif arguments.command == "prepare-carrier":
        if arguments.top100_tar is None or arguments.ranks101_200_tar is None:
            parser.error("prepare-carrier requires both July aggTrades TAR paths")
        result = prepare_v24_fresh_carrier(
            arguments.repo_root,
            top100_tar=arguments.top100_tar,
            ranks101_200_tar=arguments.ranks101_200_tar,
            runtime_date=str(arguments.runtime_date),
            producer_source_sha=arguments.source_sha,
        )
    elif arguments.command == "run":
        result = run_v24_fresh_gate(
            arguments.repo_root,
            runtime_date=str(arguments.runtime_date),
            producer_source_sha=arguments.source_sha,
        )
    elif arguments.command == "run-repair":
        result = run_v24_fresh_gate(
            arguments.repo_root,
            runtime_date=V24_REPAIR_DEFAULT_RUNTIME_DATE,
            producer_source_sha=arguments.source_sha,
        )
    elif arguments.command == "finalize-repair":
        if not arguments.source_sha:
            parser.error("finalize-repair requires the evaluation source SHA")
        result = run_v24_fresh_gate(
            arguments.repo_root,
            runtime_date=V24_REPAIR_DEFAULT_RUNTIME_DATE,
            producer_source_sha=arguments.source_sha,
            finalize_only=True,
        )
    elif arguments.command == "check-repair":
        result = check_v24_fresh_gate(
            arguments.repo_root,
            runtime_date=V24_REPAIR_DEFAULT_RUNTIME_DATE,
        )
    else:
        result = check_v24_fresh_gate(
            arguments.repo_root, runtime_date=str(arguments.runtime_date)
        )
    print(
        json.dumps(result, sort_keys=True, default=str)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
