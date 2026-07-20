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
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
import pandas as pd
import psutil

from alphafactory_crypto.instrument_canary.release import sha256_file

from .audit import freeze_search_behavior_contract
from .compositional18m import (
    BETAS,
    HORIZONS,
    NORMALIZERS,
    WINDOWS,
    CandidateSpec,
    Skeleton,
    _effective_generation_gene_names,
    _mutable_gene_domains,
    candidate_from_genes,
    field_role_coverage,
    generate_candidate,
    skeleton_registry,
)
from .expression import FieldContract, TypedExpressionRegistry
from .pair18m import FIXED_COST_BPS, evaluate_pair, feedback_contract_payload
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
    _source_tree_clean_for_run,
)


EPOCH_ID = "CRYPTO_SEARCH_ENGINE_V1_20260721"
DEFAULT_RUNTIME_DATE = "20260721"
BASE_SHA = "bbb0e696bc5f560f733dd4e9bfe263f11e4bb840"
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
        "gene_mutation_probability": 0.55,
        "skeleton_variant_mutation_probability": 0.25,
        "homologous_crossover_probability": 0.20,
        "minimum_mutated_genes": 1,
        "maximum_mutated_genes": 3,
        "duplicate_resample_limit": 64,
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
        np.asarray(store.field("active_universe_size")[:, adaptive], dtype=float)
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
        },
        "prior_continuation_manifest_bundle_sha256": prior_manifest["bundle_sha256"],
    }
    return store, contracts, behavior_contract, identities, continuation


def _frozen_contract(
    *,
    source_sha: str,
    compiler_binding: Mapping[str, Any],
    behavior_contract: Mapping[str, Any],
    input_identities: Mapping[str, Any],
    environment: Mapping[str, Any],
) -> dict[str, Any]:
    payload = {
        "schema_version": 1,
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
            "equal_reward_tie_break": ["new_behavior_family", "candidate_id"],
            "diagnostic_only": [
                "turnover",
                "cost_killed",
                "failure_layer",
                "behavior_novelty_except_equal_reward",
            ],
        },
        "evolution": {
            "genome": "existing CandidateSpec generation_genes",
            "mutation": "1_to_3_effective_genes",
            "operator_replacement": "compatible_skeleton_variant_mutation",
            "crossover": "one_point_homologous_gene_bundle_typed_role_compatible",
            "free_string_mutation": False,
            "new_ast": False,
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


@dataclass(slots=True)
class BehaviorArchive:
    rows: list[dict[str, Any]] = field(default_factory=list)
    champion_by_family: dict[str, int] = field(default_factory=dict)
    family_counts: Counter[str] = field(default_factory=Counter)
    duplicate_replacements: int = 0

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

    def state_hash(self) -> str:
        return _payload_sha(
            {
                "families": self.summary_rows(),
                "rows": len(self.rows),
                "duplicate_replacements": self.duplicate_replacements,
            }
        )

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
    seen: set[str] = field(default_factory=set)
    tables: dict[str, dict[str, dict[str, Any]]] = field(
        default_factory=lambda: defaultdict(dict)
    )
    update_count: int = 0
    step: int = 0

    def __post_init__(self) -> None:
        self.parameters = dict(self.parameters)
        self.rng = random.Random(int(self.seed))
        self.roles = {
            str(key): [str(value) for value in values]
            for key, values in field_role_coverage(
                tuple(self.registry.fields.values())
            )["roles"].items()
        }
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
        mechanisms = tuple(sorted({item.mechanism_family for item in skeleton_registry()}))
        mechanism = str(self._choice("mechanism_family", mechanisms, ("G",)))
        skeleton_ids = tuple(
            item.skeleton_id
            for item in skeleton_registry()
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
            selected[f"{side}_window"] = int(
                self._choice(
                    "window",
                    WINDOWS,
                    (
                        f"E|{role}|{family}|{skeleton.skeleton_id}",
                        f"RF|{role}|{family}",
                        f"S|{skeleton.skeleton_id}",
                        f"M|{mechanism}",
                        "G",
                    ),
                )
            )
            selected[f"{side}_normalizer"] = str(
                self._choice(
                    "normalizer",
                    NORMALIZERS,
                    (
                        f"E|{role}|{family}|{skeleton.skeleton_id}",
                        f"RF|{role}|{family}",
                        f"S|{skeleton.skeleton_id}",
                        f"M|{mechanism}",
                        "G",
                    ),
                )
            )
        selected["beta"] = float(
            self._choice(
                "beta",
                BETAS,
                (f"S|{skeleton.skeleton_id}", f"M|{mechanism}", "G"),
            )
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
            raise RuntimeError("CEM V2 duplicate resample limit exhausted")
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

    def update(self, rows: Sequence[Mapping[str, Any]]) -> None:
        if not rows:
            return
        elite_count = max(
            1,
            int(math.ceil(len(rows) * float(self.parameters["elite_fraction"]))),
        )
        elites = sorted(
            rows,
            key=lambda row: (
                -float(row["pair_reward"]),
                -int(bool(row["new_behavior_family_at_completion"])),
                str(row["candidate_id"]),
            ),
        )[:elite_count]
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
                self._accumulate(accumulator, "window", (*common[:-1], "G"), genes[f"{side}_window"])
                self._accumulate(
                    accumulator,
                    "normalizer",
                    (*common[:-1], "G"),
                    genes[f"{side}_normalizer"],
                )
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
                cumulative = Counter(
                    {str(key): int(value) for key, value in table["counts"].items()}
                )
                cumulative.update(additions)
                table["counts"] = dict(sorted(cumulative.items()))
                table["observations"] = int(sum(cumulative.values()))
                values = tuple(sorted(cumulative))
                empirical = {
                    value: (cumulative[value] + pseudocount)
                    / (sum(cumulative.values()) + pseudocount * len(values))
                    for value in values
                }
                prior = table.get("probabilities", {})
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
    seen: set[str] = field(default_factory=set)
    population: dict[str, dict[str, Any]] = field(default_factory=dict)
    step: int = 0
    verified_mutations: int = 0
    verified_skeleton_mutations: int = 0
    verified_crossovers: int = 0
    duplicate_replacements: int = 0

    def __post_init__(self) -> None:
        self.parameters = dict(self.parameters)
        self.rng = random.Random(int(self.seed))
        self.roles = {
            str(key): [str(value) for value in values]
            for key, values in field_role_coverage(
                tuple(self.registry.fields.values())
            )["roles"].items()
        }
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

    def _candidate(self, record: Mapping[str, Any]) -> CandidateSpec:
        return CandidateSpec.from_dict(record["candidate"])

    def _parent(
        self,
        archive: BehaviorArchive,
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
                    archive.family_counts[
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

    def _mutate_genes(
        self, parent: CandidateSpec
    ) -> tuple[CandidateSpec, dict[str, Any]]:
        skeleton = _skeleton_by_id(parent.skeleton_id)
        maximum = int(self.parameters["maximum_mutated_genes"])
        minimum = int(self.parameters["minimum_mutated_genes"])
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
                        },
                    )
        raise RuntimeError("Evolution V2 could not produce an effective 1-3 gene mutation")

    def _mutate_skeleton(
        self, parent: CandidateSpec
    ) -> tuple[CandidateSpec, dict[str, Any]]:
        source = _skeleton_by_id(parent.skeleton_id)
        targets = [
            item
            for item in skeleton_registry()
            if item.mechanism_family == source.mechanism_family
            and item.skeleton_id != source.skeleton_id
            and item.field_roles == source.field_roles
        ]
        self.rng.shuffle(targets)
        for internal_attempt, target in enumerate(targets, start=1):
            child = candidate_from_genes(
                self.registry,
                skeleton=target,
                genes=dict(parent.generation_genes),
                roles=self.roles,
            )
            if child.candidate_id != parent.candidate_id:
                return child, self._receipt(
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
                    },
                )
        raise RuntimeError("Evolution V2 has no compatible skeleton variant mutation")

    def _crossover(
        self, first: CandidateSpec, second: CandidateSpec
    ) -> tuple[CandidateSpec, dict[str, Any]]:
        first_skeleton = _skeleton_by_id(first.skeleton_id)
        second_skeleton = _skeleton_by_id(second.skeleton_id)
        if first_skeleton.field_roles != second_skeleton.field_roles:
            raise ValueError("crossover parents have incompatible typed roles")
        points = list(range(1, len(GENE_ORDER)))
        self.rng.shuffle(points)
        for internal_attempt, point in enumerate(points, start=1):
            genome = {
                name: (
                    first.generation_genes[name]
                    if index < point
                    else second.generation_genes[name]
                )
                for index, name in enumerate(GENE_ORDER)
            }
            try:
                child = candidate_from_genes(
                    self.registry,
                    skeleton=first_skeleton,
                    genes=genome,
                    roles=self.roles,
                )
            except ValueError:
                continue
            if child.candidate_id in {first.candidate_id, second.candidate_id}:
                continue
            return child, self._receipt(
                operation="ONE_POINT_HOMOLOGOUS_GENE_BUNDLE_CROSSOVER",
                parents=(first, second),
                child=child,
                details={
                    "crossover_point": int(point),
                    "gene_order": list(GENE_ORDER),
                    "output_type": "NUMERIC_ASSET_TIME",
                    "internal_generation_attempts": internal_attempt,
                },
            )
        raise RuntimeError("Evolution V2 could not produce a compatible crossover")

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
                point = int(receipt["crossover_point"])
                if not 1 <= point < len(GENE_ORDER):
                    return False
                if (
                    _skeleton_by_id(parents[0].skeleton_id).field_roles
                    != _skeleton_by_id(parents[1].skeleton_id).field_roles
                ):
                    return False
                genome = {
                    name: (
                        parents[0].generation_genes[name]
                        if index < point
                        else parents[1].generation_genes[name]
                    )
                    for index, name in enumerate(GENE_ORDER)
                }
                rebuilt = candidate_from_genes(
                    self.registry,
                    skeleton=_skeleton_by_id(parents[0].skeleton_id),
                    genes=genome,
                    roles=self.roles,
                )
                return rebuilt.candidate_id == child.candidate_id
            return False
        except (KeyError, TypeError, ValueError, StopIteration):
            return False

    def propose(
        self, archive: BehaviorArchive
    ) -> tuple[CandidateSpec, dict[str, Any]]:
        before = self.state_hash()
        limit = int(self.parameters["duplicate_resample_limit"])
        candidate: CandidateSpec | None = None
        receipt: dict[str, Any] | None = None
        parents: tuple[CandidateSpec, ...] = ()
        operation = "TYPED_RANDOM_WARMUP"
        compile_attempts = 0
        for duplicate_resamples in range(limit + 1):
            compile_attempts += 1
            if len(self.population) < int(self.parameters["warmup"]):
                skeletons = skeleton_registry()
                skeleton = skeletons[(self.step + self.seed + duplicate_resamples) % len(skeletons)]
                candidate = generate_candidate(
                    self.registry, skeleton=skeleton, rng=self.rng, roles=self.roles
                )
                receipt = None
                parents = ()
                operation = "TYPED_RANDOM_WARMUP"
            else:
                draw = self.rng.random()
                gene_probability = float(self.parameters["gene_mutation_probability"])
                skeleton_probability = float(
                    self.parameters["skeleton_variant_mutation_probability"]
                )
                first = self._parent(archive)
                if draw < gene_probability:
                    candidate, receipt = self._mutate_genes(first)
                    parents = (first,)
                    operation = str(receipt["operation"])
                elif draw < gene_probability + skeleton_probability:
                    candidate, receipt = self._mutate_skeleton(first)
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
                    if not compatible:
                        candidate, receipt = self._mutate_genes(first)
                        parents = (first,)
                    else:
                        second = self._parent(archive, eligible=compatible)
                        candidate, receipt = self._crossover(first, second)
                        parents = (first, second)
                    operation = str(receipt["operation"])
                compile_attempts += int(
                    receipt.get("internal_generation_attempts", 1)
                ) - 1
            if candidate.candidate_id not in self.seen:
                break
        assert candidate is not None
        if candidate.candidate_id in self.seen:
            raise RuntimeError("Evolution V2 duplicate resample limit exhausted")
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
        }

    def observe(
        self,
        candidate: CandidateSpec,
        archive_row: Mapping[str, Any],
    ) -> None:
        family_id = str(archive_row["behavior_family_id"])
        candidate_record = {
            "candidate": candidate.to_dict(),
            "pair_reward": float(archive_row["pair_reward"]),
            "behavior_family_id": family_id,
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
        if len(self.population) > limit:
            ordered = sorted(
                self.population,
                key=lambda candidate_id: (
                    -float(self.population[candidate_id]["pair_reward"]),
                    candidate_id,
                ),
            )
            self.population = {
                candidate_id: self.population[candidate_id]
                for candidate_id in ordered[:limit]
            }
        operation = str(archive_row.get("operation", ""))
        if operation == "EFFECTIVE_GENE_MUTATION_1_TO_3":
            self.verified_mutations += 1
        elif operation == "COMPATIBLE_SKELETON_VARIANT_MUTATION":
            self.verified_skeleton_mutations += 1
        elif operation == "ONE_POINT_HOMOLOGOUS_GENE_BUNDLE_CROSSOVER":
            self.verified_crossovers += 1

    def export_state(self) -> dict[str, Any]:
        return {
            "kind": "typed_evolution_v2",
            "seed": int(self.seed),
            "parameters": dict(self.parameters),
            "rng_state": _json_rng_state(self.rng.getstate()),
            "seen": sorted(self.seen),
            "population": {
                candidate_id: dict(record)
                for candidate_id, record in sorted(self.population.items())
            },
            "step": int(self.step),
            "verified_mutations": int(self.verified_mutations),
            "verified_skeleton_mutations": int(self.verified_skeleton_mutations),
            "verified_crossovers": int(self.verified_crossovers),
            "duplicate_replacements": int(self.duplicate_replacements),
        }

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
        policy.step = int(state["step"])
        policy.verified_mutations = int(state["verified_mutations"])
        policy.verified_skeleton_mutations = int(
            state["verified_skeleton_mutations"]
        )
        policy.verified_crossovers = int(state["verified_crossovers"])
        policy.duplicate_replacements = int(state["duplicate_replacements"])
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


def _initial_policies(registry: TypedExpressionRegistry) -> dict[str, PolicyType]:
    output: dict[str, PolicyType] = {}
    for seed in SEEDS:
        for arm in FIRST_CHECKPOINT_ARMS:
            key = _policy_key(arm, seed)
            if arm in V1_PARAMETERS:
                output[key] = LanePolicy(
                    arm, seed, registry, dict(V1_PARAMETERS[arm])
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


def _worker_initialize(
    cache_root: str,
    contract_rows: Sequence[Mapping[str, Any]],
    behavior_contract: Mapping[str, Any],
) -> None:
    global _WORKER_STORE, _WORKER_REGISTRY, _WORKER_BEHAVIOR_CONTRACT
    _WORKER_STORE = RawPanelStore.open(Path(cache_root))
    _WORKER_REGISTRY = TypedExpressionRegistry(_contracts_from_payload(contract_rows))
    _WORKER_BEHAVIOR_CONTRACT = dict(behavior_contract)


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
            block_start=ADAPTIVE_START,
            block_end=ADAPTIVE_END,
            block_role="SPENT_DEVELOPMENT_BROAD39_SEARCH_ENGINE_V1",
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


def _new_campaign_state(source_sha: str, frozen_hash: str) -> dict[str, Any]:
    arms = set(FIRST_CHECKPOINT_ARMS)
    return {
        "schema_version": 1,
        "source_sha": source_sha,
        "frozen_contract_sha256": frozen_hash,
        "next_checkpoint_index": 0,
        "scheduler_cursor": 0,
        "generation_attempts": 0,
        "compile_valid": 0,
        "exact_unique": 0,
        "matched_control_valid": 0,
        "strict_evaluated": 0,
        "attempted_exact_ids": [],
        "failure_counts": {},
        "wall_elapsed_seconds": 0.0,
        "workers": DEFAULT_WORKERS,
        "memory_fallback_used": False,
        "arm_states": {
            "hierarchical_typed_cem_v2": "ACTIVE",
            "typed_evolution_v2": "ACTIVE",
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
            for arm in sorted(arms)
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
) -> list[dict[str, Any]]:
    cumulative_by_arm: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in ledger:
        cumulative_by_arm[str(row["arm"])].append(row)
    comparison_arms = (
        FIRST_CHECKPOINT_ARMS
        if checkpoint_index == 0
        else tuple(
            arm
            for arm in ROLLING_ARMS
            if cumulative_by_arm.get(arm)
            and state.get("arm_states", {}).get(arm, "ACTIVE") != "EXITED"
        )
    )
    matched_count = min(
        (len(cumulative_by_arm[arm]) for arm in comparison_arms), default=0
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
                "cpu_hours": cpu_hours,
                "valid_exact_unique_per_cpu_hour": len(rows)
                / max(cpu_hours, 1.0e-12),
                "positive_matched_discoveries_per_cpu_hour": sum(
                    bool(row["matched_positive"]) for row in rows
                )
                / max(cpu_hours, 1.0e-12),
                "new_behavior_families_per_cpu_hour": sum(
                    bool(row["new_behavior_family_at_completion"]) for row in rows
                )
                / max(cpu_hours, 1.0e-12),
                "new_behavior_families_per_1k_evaluations": 1000.0
                * sum(bool(row["new_behavior_family_at_completion"]) for row in rows)
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
            "cpu_hours": sum(
                float(value["cpu_seconds"])
                for value in state["arm_counters"].values()
            )
            / 3600.0,
            "valid_exact_unique_per_cpu_hour": len(ledger)
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
        "policies": {
            key: _export_policy(policy) for key, policy in sorted(policies.items())
        },
    }


def _write_checkpoint(
    *,
    runtime_root: Path,
    label: str,
    checkpoint_index: int,
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
    os.replace(temporary, target)
    return target


def _load_checkpoint(
    *,
    checkpoint_path: Path,
    registry: TypedExpressionRegistry,
    expected_source_sha: str,
    expected_frozen_hash: str,
    expected_identities: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, PolicyType], list[dict[str, Any]], BehaviorArchive, list[dict[str, Any]]]:
    manifest_path = checkpoint_path / "manifest.json"
    manifest = _read_json(manifest_path)
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
    ledger = pd.read_parquet(checkpoint_path / "candidate_ledger.parquet").to_dict(
        "records"
    )
    archive = BehaviorArchive.from_rows(
        pd.read_parquet(checkpoint_path / "behavior_archive.parquet").to_dict(
            "records"
        )
    )
    archive.duplicate_replacements = archive_duplicate_replacements
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
    manifest["restore_verified"] = True
    _write_json(manifest_path, manifest)
    return state_payload, policies, ledger, archive, metrics


class _EngineBudgetExhausted(RuntimeError):
    pass


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
        "arm": str(proposal["arm"]),
        "seed": int(proposal["seed"]),
        "skeleton_id": candidate.skeleton_id,
        "mechanism_family": candidate.mechanism_family,
        "operator_path": candidate.operator_path,
        "horizon_hours": int(candidate.horizon_hours),
        "raw_fields_json": json.dumps(list(candidate.raw_fields)),
        "field_families_json": json.dumps(list(candidate.field_families)),
        "operation": str(proposal["operation"]),
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
        "cost_killed": "COST_MEAN" in violations,
        "turnover_killed": "TURNOVER_MEAN" in violations,
        "coordinate_data_binding_id": behavior["coordinate_data_binding_id"],
        "rank_descriptor_id": behavior["rank_descriptor_id"],
        "selected_asset_overlap_id": behavior["selected_asset_overlap_id"],
        "mapped_weight_descriptor_id": behavior["mapped_weight_descriptor_id"],
        "turnover_path_descriptor_id": behavior["turnover_path_descriptor_id"],
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
    qualified = ["canonical_typed_random"]
    for arm, arm_metrics in (
        ("hierarchical_typed_cem_v2", cem),
        ("typed_evolution_v2", evolution),
    ):
        if arm_metrics is None or state["arm_states"].get(arm) != "ACTIVE":
            continue
        if any(
            (
                float(arm_metrics[name]) > float(random_metrics[name])
                for name in (
                    "valid_exact_unique_per_cpu_hour",
                    "new_behavior_families_per_1k_evaluations",
                    "mean_pair_reward_at_matched_count",
                    "top_decile_pair_reward_at_matched_count",
                )
            )
        ):
            qualified.append(arm)
    if archive_reduced and restore_verified:
        qualified.append("per_run_behavior_archive")
    duplicate_rate = 1.0 - len(archive.champion_by_family) / max(1, len(ledger))
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
        "future_new_data_arena_qualified_arms": qualified,
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


def _final_manifest(
    *,
    repo_root: Path,
    runtime_root: Path,
    report_path: Path,
    source_sha: str,
    frozen_hash: str,
    identities: Mapping[str, Any],
    state: Mapping[str, Any],
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
        "epoch_id": EPOCH_ID,
        "status": "COMPLETED",
        "producer_source_sha": source_sha,
        "base_sha": BASE_SHA,
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
        "continuation": "python -m alphafactory_crypto.broad_search.search_engine_v1 check --runtime-date 20260721",
    }


def run_engine(
    repo_root: Path,
    *,
    runtime_date: str = DEFAULT_RUNTIME_DATE,
    source_sha: str | None = None,
) -> dict[str, Any]:
    runtime_root = repo_root / f"runtime/crypto_search_engine_v1_{runtime_date}"
    report_path = repo_root / f"reports/CRYPTO_SEARCH_ENGINE_V1_{runtime_date}.md"
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
    store, contracts, behavior_contract, input_identities, continuation = (
        _load_bound_inputs(repo_root)
    )
    registry = TypedExpressionRegistry(contracts)
    compiler_binding = _compiler_binding(repo_root)
    environment = _environment_fingerprint()
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
    cache_root = repo_root / str(continuation["cache_root"])

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
                "status": "READY_FIRST_STRICT_BATCH_COUNTS_TOWARD_20000",
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
        state = _new_campaign_state(source_sha, frozen_hash)
        policies = _initial_policies(registry)
        ledger: list[dict[str, Any]] = []
        archive = BehaviorArchive()
        metrics: list[dict[str, Any]] = []

    attempted_ids = set(str(value) for value in state["attempted_exact_ids"])
    active_started = time.perf_counter()
    prior_active_seconds = float(state["wall_elapsed_seconds"])
    preflight_done = _read_json(runtime_root / "embedded_preflight.json").get(
        "status"
    ) not in {"READY_FIRST_STRICT_BATCH_COUNTS_TOWARD_20000"}

    def active_elapsed() -> float:
        return prior_active_seconds + (time.perf_counter() - active_started)

    def enforce_budget(reserve_attempts: int = 0) -> None:
        state["wall_elapsed_seconds"] = active_elapsed()
        if (
            int(state["generation_attempts"]) + int(reserve_attempts)
            > RAW_ATTEMPT_LIMIT
        ):
            raise _EngineBudgetExhausted("RAW_GENERATION_ATTEMPT_LIMIT")
        if float(state["wall_elapsed_seconds"]) >= WALL_TIME_LIMIT_SECONDS:
            raise _EngineBudgetExhausted("ACTIVE_WALL_TIME_LIMIT")

    executor: concurrent.futures.ProcessPoolExecutor | None = None

    def start_executor(workers: int) -> concurrent.futures.ProcessPoolExecutor:
        return concurrent.futures.ProcessPoolExecutor(
            max_workers=workers,
            initializer=_worker_initialize,
            initargs=(str(cache_root), _contracts_payload(contracts), behavior_contract),
        )

    def stop_executor() -> None:
        nonlocal executor
        if executor is not None:
            executor.shutdown(wait=True, cancel_futures=False)
            executor = None

    try:
        executor = start_executor(int(state["workers"]))
        for checkpoint_index in range(
            int(state["next_checkpoint_index"]), CHECKPOINT_COUNT
        ):
            allocation = _checkpoint_allocation(
                checkpoint_index, state["arm_states"]
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
                CHECKPOINT_SIZE - sum(checkpoint_existing.values())
            )
            while len(ledger) < checkpoint_target_count:
                enforce_budget()
                proposals: list[dict[str, Any]] = []
                scans_without_slot = 0
                while len(proposals) < int(state["workers"]):
                    enforce_budget()
                    if all(
                        lane_completed[key]
                        + sum(proposal["policy_key"] == key for proposal in proposals)
                        >= target
                        for key, target in target_by_lane.items()
                    ):
                        break
                    policy_key = lane_order[
                        int(state["scheduler_cursor"]) % len(lane_order)
                    ]
                    state["scheduler_cursor"] = int(state["scheduler_cursor"]) + 1
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
                        _increment_counter(state, arm, "generation_attempts", 1)
                        state["arm_counters"][arm]["cpu_seconds"] += proposal_cpu
                        _failure(
                            state,
                            arm,
                            "PROPOSAL_" + type(failure).__name__,
                        )
                        continue
                    proposal_cpu = time.process_time() - proposal_cpu_started
                    raw_attempts = int(metadata["raw_attempts"])
                    _increment_counter(
                        state, arm, "generation_attempts", raw_attempts
                    )
                    _increment_counter(state, arm, "compile_valid", raw_attempts)
                    state["arm_counters"][arm]["cpu_seconds"] += proposal_cpu
                    expression_verified = _candidate_rebuild_verified(
                        registry,
                        candidate,
                        field_role_coverage(contracts)["roles"],
                    )
                    if not expression_verified:
                        attempted_ids.add(candidate.candidate_id)
                        _policy_reject(policy, candidate)
                        _failure(state, arm, "EXPRESSION_HASH_REPLAY")
                        continue
                    if candidate.candidate_id in attempted_ids:
                        _policy_reject(policy, candidate)
                        _failure(state, arm, "GLOBAL_EXACT_DUPLICATE")
                        continue
                    attempted_ids.add(candidate.candidate_id)
                    _increment_counter(state, arm, "exact_unique", 1)
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
                        }
                    )
                if not proposals:
                    continue
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
                    policy_archive_row = {
                        **archive_row,
                        "operation": proposal["operation"],
                    }
                    _policy_observe(
                        policy,
                        candidate=candidate,
                        reward=float(evaluation["pair_reward"]),
                        archive_row=policy_archive_row,
                    )
                    _increment_counter(state, arm, "matched_control_valid", 1)
                    _increment_counter(state, arm, "strict_evaluated", 1)
                    lane_completed[str(proposal["policy_key"])] += 1
                    ledger.append(
                        _ledger_row(
                            candidate=candidate,
                            evaluation=evaluation,
                            proposal=proposal,
                            archive_row=archive_row,
                            new_family=new_family,
                            state_hash_after=(
                                policy.state_hash()
                                if not isinstance(policy, LanePolicy)
                                else policy.state_hash()
                            ),
                            checkpoint_index=checkpoint_index,
                            completion_ordinal=completion_ordinal,
                            arm_completion_ordinal=arm_completion[arm],
                            worker=worker,
                        )
                    )
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
                state["attempted_exact_ids"] = sorted(attempted_ids)
                state["wall_elapsed_seconds"] = active_elapsed()
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
            for seed in SEEDS:
                policy = policies[
                    _policy_key("hierarchical_typed_cem_v2", seed)
                ]
                assert isinstance(policy, HierarchicalTypedCEMV2)
                policy.update(
                    [
                        row
                        for row in checkpoint_rows
                        if row["arm"] == "hierarchical_typed_cem_v2"
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
            )
            gates = _apply_exit_gate(
                checkpoint_index=checkpoint_index,
                checkpoint_metrics=checkpoint_metrics,
                state=state,
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

    if len(ledger) != STRICT_TARGET:
        raise AssertionError("Search Engine V1 ended without exactly 20,000 strict candidates")
    state["wall_elapsed_seconds"] = active_elapsed()
    decision = _final_decision(
        source_sha=source_sha,
        state=state,
        ledger=ledger,
        archive=archive,
        metrics=metrics,
        runtime_root=runtime_root,
    )
    _write_json(runtime_root / "final_decision.json", decision)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        _report_text(decision), encoding="utf-8", newline="\n"
    )
    manifest = _final_manifest(
        repo_root=repo_root,
        runtime_root=runtime_root,
        report_path=report_path,
        source_sha=source_sha,
        frozen_hash=frozen_hash,
        identities=identities,
        state=state,
    )
    _write_json(runtime_root / "run_manifest.json", manifest)
    return {
        "result": "PASS",
        "status": decision["status"],
        "producer_source_sha": source_sha,
        "strict_evaluated_count": len(ledger),
        "generation_attempts": int(state["generation_attempts"]),
        "checkpoint_count": CHECKPOINT_COUNT,
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
    if receipt_rows.empty or not bool(receipt_rows["receipt_verified"].fillna(False).all()):
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
    return {
        "result": "PASS" if not errors else "FAIL",
        "errors": errors,
        "producer_source_sha": manifest.get("producer_source_sha"),
        "strict_evaluated_count": len(ledger),
        "generation_attempts": decision.get("generation_attempts"),
        "checkpoint_count": len(checkpoints),
        "behavior_family_count": int(archive["behavior_family_id"].nunique()),
        "artifact_bundle_sha256": manifest.get("artifact_bundle_sha256"),
        "sealed_reads": decision.get("sealed_reads"),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("run", "check"))
    parser.add_argument("--runtime-date", default=DEFAULT_RUNTIME_DATE)
    parser.add_argument("--source-sha")
    args = parser.parse_args(argv)
    repo_root = Path(__file__).resolve().parents[2]
    if args.command == "run":
        result = run_engine(
            repo_root,
            runtime_date=str(args.runtime_date),
            source_sha=args.source_sha,
        )
    else:
        result = check_engine(repo_root, runtime_date=str(args.runtime_date))
    print(json.dumps(result, indent=2, sort_keys=True), flush=True)
    return 0 if result.get("result") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "BehaviorArchive",
    "HierarchicalTypedCEMV2",
    "TypedEvolutionV2",
    "check_engine",
    "run_engine",
]
