"""Evidence-qualified runner for the bounded 18M compositional development search."""

from __future__ import annotations

import concurrent.futures
import ctypes
import gc
import hashlib
import importlib.metadata
import json
import math
import os
import platform
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

from alphafactory_crypto.instrument_capability.mapping import (
    CROSS_SECTIONAL_ZERO_NET,
    DEFAULT_MAPPING_CONTRACTS,
    mapping_contract_sha256,
)
from alphafactory_crypto.instrument_canary.release import sha256_file

from .compositional18m import (
    BETAS,
    CandidateSpec,
    HORIZONS,
    MECHANISM_FAMILIES,
    NORMALIZERS,
    WINDOWS,
    _effective_generation_gene_names,
    audit_numeric_expressivity,
    candidate_from_genes,
    field_role_coverage,
    generate_candidate,
    generate_structural_pool,
    skeleton_payload,
    skeleton_registry,
    typed_mutate_candidate,
    verify_typed_mutation_receipt,
)
from .expression import FieldContract, TypedExpressionRegistry
from .pair18m import (
    FIXED_COST_BPS,
    evaluate_pair,
    feedback_contract_payload,
    pair_contract_payload,
    robust_monthly_audit,
)
from .panel18m import (
    RawPanelStore,
    build_raw_panel_cache,
    economic_role,
    field_equivalence_audit,
    infer_family,
    infer_type_unit,
    qualify_fields,
)


EPOCH_ID = "CRYPTO_18M_COMPOSITIONAL_BROAD_ALPHA_SEARCH_EPOCH1"
CURRENT_FIELD_CONTINUATION_EPOCH_ID = (
    "CRYPTO_18M_COMPOSITIONAL_CURRENT_FIELD_CONTINUATION_V1"
)
POLICIES = (
    "canonical_typed_random",
    "cem_diversity_v2",
    "uct_ucb_like",
    "evolutionary",
)
POLICY_UPGRADE_CANARY_POLICIES = (
    "canonical_typed_random",
    "cem_diversity_v2",
    "cem_distribution_v1",
    "evolutionary",
    "evolutionary_typed_v1",
)
SUPPORTED_POLICIES = tuple(dict.fromkeys(POLICIES + POLICY_UPGRADE_CANARY_POLICIES))
SEEDS = (20260716, 20260717, 20260718, 20260719)
ADAPTIVE_START = "2023-07-01T00:00:00Z"
ADAPTIVE_END = "2024-07-01T00:00:00Z"
REPORT_ONLY_START = "2024-07-01T00:00:00Z"
REPORT_ONLY_END = "2025-01-01T00:00:00Z"

COMPILER_BINDING_PATHS = (
    "alphafactory_crypto/broad_search/audit.py",
    "alphafactory_crypto/broad_search/expression.py",
    "alphafactory_crypto/broad_search/panel18m.py",
    "alphafactory_crypto/broad_search/compositional18m.py",
    "alphafactory_crypto/broad_search/pair18m.py",
    "alphafactory_crypto/broad_search/runner18m.py",
    "alphafactory_crypto/broad_search/search_engine_v1.py",
    "alphafactory_crypto/broad_search/policy_upgrade_canary.py",
)

RUNTIME_OUTPUTS = (
    "CRYPTO_18M_SEARCH_CONTRACT.json",
    "CRYPTO_18M_FIELD_ADMISSION_AUDIT.csv",
    "CRYPTO_18M_COMPOSITIONAL_FIELD_REGISTRY.json",
    "CRYPTO_FIELD_EQUIVALENCE_AUDIT.csv",
    "CRYPTO_DYNAMIC_ELIGIBILITY_LEDGER.parquet",
    "CRYPTO_COMPOSITIONAL_SKELETON_REGISTRY.json",
    "CRYPTO_GENERATOR_EXPRESSIVITY_AUDIT.json",
    "CRYPTO_MATCHED_ABLATION_PAIR_CONTRACT.json",
    "CRYPTO_PAIR_NATIVE_FEEDBACK_CONTRACT.json",
    "CRYPTO_PROPOSAL_EXPOSURE_LEDGER.parquet",
    "CRYPTO_ADMISSION_WATERFALL.csv",
    "CRYPTO_STRICT_PAIR_RESULTS.parquet",
    "CRYPTO_INCREMENTAL_SLEEVE_RESULTS.parquet",
    "CRYPTO_DEVELOPMENT_CHALLENGE_RESULTS.parquet",
    "CRYPTO_ROBUST_STATISTICAL_AUDIT.parquet",
    "CRYPTO_BEHAVIOR_CLUSTERS.json",
    "CRYPTO_CROSS_SEED_REPRODUCTION.json",
    "CRYPTO_POLICY_BEHAVIOR_AUDIT.json",
    "CRYPTO_RESOURCE_PREFLIGHT.json",
    "CRYPTO_SEARCH_DECISION.json",
    "CRYPTO_ARTIFACT_MANIFEST.json",
)


def _git_sha(repo_root: Path) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=repo_root, text=True
    ).strip().lower()


def _git_clean(repo_root: Path) -> bool:
    output = subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=repo_root, text=True
    )
    return not output.strip()


def _source_tree_clean_for_run(
    repo_root: Path, *, allowed_paths: Sequence[Path]
) -> bool:
    output = subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=repo_root,
        text=True,
    )
    allowed = [path.resolve() for path in allowed_paths]
    for line in output.splitlines():
        raw = line[3:].strip().strip('"').replace("/", os.sep)
        path = (repo_root / raw).resolve()
        if not any(path == root or root in path.parents for root in allowed):
            return False
    return True


def _payload_sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str
        ).encode("utf-8")
    ).hexdigest().upper()


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True, default=str) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _compiler_binding(repo_root: Path) -> dict[str, Any]:
    rows = [
        {
            "path": relative,
            "bytes": (repo_root / relative).stat().st_size,
            "sha256": sha256_file(repo_root / relative),
        }
        for relative in COMPILER_BINDING_PATHS
    ]
    return {
        "paths": rows,
        "bundle_sha256": _payload_sha(rows),
    }


def _environment_fingerprint() -> dict[str, Any]:
    packages = {}
    for name in ("numpy", "pandas", "pyarrow", "scipy", "psutil"):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = "NOT_INSTALLED"
    return {
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "packages": packages,
        "thread_caps": {
            name: os.environ.get(name)
            for name in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS")
        },
    }


def _current_field_surface_binding(
    repo_root: Path, config: Mapping[str, Any]
) -> tuple[dict[str, Any] | None, tuple[str, ...] | None]:
    """Bind a continuation to one context of the committed Core Pack.

    Contexts remain separate.  This continuation intentionally consumes only
    the Broad base-token view that the frozen 40-skeleton compiler can express.
    """

    surface = config.get("field_surface")
    if surface is None:
        return None, None
    contract_path = repo_root / str(surface["contract"])
    observed_file_sha = sha256_file(contract_path)
    if observed_file_sha != str(surface["contract_file_sha256"]).upper():
        raise ValueError("current field contract file identity changed")
    payload = _read_json(contract_path)
    if payload.get("identity_sha256") != str(
        surface["contract_identity_sha256"]
    ).upper():
        raise ValueError("current field contract logical identity changed")
    if payload.get("boundaries", {}).get("context_merge_allowed") is not False:
        raise PermissionError("current field contract does not forbid context pooling")

    context_id = str(surface["context_id"])
    tokens = [
        row for row in payload.get("tokens", []) if row.get("context_id") == context_id
    ]
    if len(tokens) != int(surface["expected_fields"]):
        raise ValueError("current field context count changed")
    if any(row.get("token_kind") != "BASE" for row in tokens):
        raise ValueError("Broad continuation accepts base tokens only")
    family_mismatches = [
        str(row["field_id"])
        for row in tokens
        if str(row.get("family")) != infer_family(str(row["field_id"]))
    ]
    if family_mismatches:
        raise ValueError(
            "current field contract family mismatch: " + ",".join(family_mismatches)
        )
    field_ids = tuple(str(row["field_id"]) for row in tokens)
    if len(field_ids) != len(set(field_ids)):
        raise ValueError("current field context contains duplicate fields")
    market_state = sum(
        str(row.get("family")) == "cross_asset_market_state" for row in tokens
    )
    asset_local = len(tokens) - market_state
    expected_views = surface["expected_views"]
    if (
        asset_local != int(expected_views["asset_local"])
        or market_state != int(expected_views["market_state"])
    ):
        raise ValueError("current Broad 38+1 view changed")

    provisional_contracts = tuple(
        FieldContract(
            field_id,
            "STATE",
            "dimensionless",
            1,
            "CURRENT_FIELD_SURFACE_BINDING",
        )
        for field_id in field_ids
    )
    coverage = field_role_coverage(provisional_contracts)
    if not coverage["all_fields_reachable"]:
        raise ValueError(
            "current field surface is not generator-reachable: "
            + ",".join(coverage["unreachable_fields"])
        )
    context_counts = Counter(str(row.get("context_id")) for row in payload["tokens"])
    binding = {
        "contract_path": contract_path.relative_to(repo_root).as_posix(),
        "contract_file_sha256": observed_file_sha,
        "contract_identity_sha256": payload["identity_sha256"],
        "selected_context_id": context_id,
        "selected_field_count": len(field_ids),
        "selected_field_ids": list(field_ids),
        "view_counts": {
            "asset_local": asset_local,
            "market_state": market_state,
        },
        "all_context_counts": dict(sorted(context_counts.items())),
        "context_pooling": False,
        "selection_role": "FROZEN_CURRENT_SURFACE_BEFORE_CONTINUATION",
        "excluded_contexts": list(surface.get("excluded_contexts", [])),
        "generator_role_coverage": coverage,
    }
    return binding, field_ids


def _directory_bundle(root: Path) -> dict[str, Any]:
    metadata = _read_json(root / "metadata.json")
    required_root = {
        "metadata.json",
        "timestamp_ns.npy",
        "observed.npy",
        "base_eligible.npy",
        "source_segment.npy",
        "target_return_1h.npy",
        "target_return_4h.npy",
    }
    paths = [root / name for name in sorted(required_root)] + [
        root / "fields" / f"{field_id}.npy"
        for field_id in sorted(metadata["field_ids"])
    ]
    missing = [path for path in paths if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"raw cache file missing: {missing[0]}")
    rows = [
        {
            "path": path.relative_to(root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in paths
    ]
    return {
        "file_count": len(rows),
        "bytes": sum(int(row["bytes"]) for row in rows),
        "bundle_sha256": _payload_sha(rows),
    }


def load_search_surface_carrier(
    repo_root: Path,
    *,
    carrier_manifest_path: Path,
    surface_id: str,
) -> tuple[RawPanelStore, tuple[FieldContract, ...], dict[str, Any]]:
    """Load one independently bound search carrier through the normal runner."""

    manifest = _read_json(carrier_manifest_path)
    if manifest.get("schema_version") != 1:
        raise ValueError("unsupported search carrier manifest")
    try:
        carrier = manifest["carriers"][surface_id]
    except KeyError as exc:
        raise KeyError(f"unknown search carrier: {surface_id}") from exc
    raw_root = Path(str(carrier["cache_root"]))
    cache_root = raw_root if raw_root.is_absolute() else repo_root / raw_root
    if not cache_root.is_dir():
        raise FileNotFoundError(f"search carrier is unavailable: {cache_root}")
    metadata = _read_json(cache_root / "metadata.json")
    if metadata.get("identity_sha256") != carrier["cache_identity_sha256"]:
        raise ValueError("search carrier metadata identity changed")
    if _directory_bundle(cache_root) != carrier["directory_bundle"]:
        raise ValueError("search carrier content bundle changed")
    contract_rows = list(carrier["contracts"])
    if _payload_sha(contract_rows) != carrier["contracts_sha256"]:
        raise ValueError("search carrier contract identity changed")
    contracts = tuple(
        FieldContract(
            field_id=str(row["field_id"]),
            value_type=str(row["value_type"]),
            unit=str(row["unit"]),
            observable_lag_hours=int(row["observable_lag_hours"]),
            pit_authority=str(row["pit_authority"]),
        )
        for row in contract_rows
    )
    field_ids = [item.field_id for item in contracts]
    if len(field_ids) != len(set(field_ids)):
        raise ValueError("search carrier contract fields are not unique")
    if not set(field_ids).issubset(set(metadata.get("field_ids", []))):
        raise ValueError("search carrier cache lacks a contracted field")
    minimum_assets = int(manifest["minimum_assets_per_timestamp"])
    store = RawPanelStore.open(
        cache_root,
        minimum_assets_per_timestamp=minimum_assets,
    )
    evidence = {
        "surface_id": surface_id,
        "cache_root": str(cache_root),
        "cache_identity_sha256": metadata["identity_sha256"],
        "contracts_sha256": carrier["contracts_sha256"],
        "field_count": len(contracts),
        "minimum_assets_per_timestamp": minimum_assets,
    }
    return store, contracts, evidence


def _load_pinned_cache_inputs(
    repo_root: Path,
    *,
    cache_root: Path,
    runtime_root: Path,
    cache_reuse: Mapping[str, Any],
) -> tuple[RawPanelStore, dict[str, Any]]:
    """Open the prior content-bound raw cache without rebuilding its data plane."""

    if cache_reuse.get("mode") != "PINNED_EXISTING_RAW_CACHE":
        raise ValueError("unsupported cache reuse mode")
    if not cache_root.is_dir():
        raise FileNotFoundError(f"pinned raw cache is unavailable: {cache_root}")
    metadata = _read_json(cache_root / "metadata.json")
    if metadata.get("identity_sha256") != str(
        cache_reuse["expected_identity_sha256"]
    ).upper():
        raise ValueError("pinned raw cache metadata identity changed")
    if metadata.get("source_sha") != str(
        cache_reuse["expected_producer_source_sha"]
    ).lower():
        raise ValueError("pinned raw cache producer changed")
    observed_bundle = _directory_bundle(cache_root)
    expected_bundle = cache_reuse["directory_bundle"]
    if observed_bundle != {
        "file_count": int(expected_bundle["file_count"]),
        "bytes": int(expected_bundle["bytes"]),
        "bundle_sha256": str(expected_bundle["bundle_sha256"]).upper(),
    }:
        raise ValueError("pinned raw cache content bundle changed")

    inputs = cache_reuse["evidence_inputs"]
    resolved: dict[str, Path] = {}
    for name, record in inputs.items():
        path = repo_root / str(record["path"])
        if not path.is_file() or sha256_file(path) != str(record["sha256"]).upper():
            raise ValueError(f"pinned cache evidence input changed: {name}")
        resolved[name] = path

    eligibility_target = runtime_root / RUNTIME_OUTPUTS[4]
    eligibility_target.parent.mkdir(parents=True, exist_ok=True)
    if resolved["eligibility_ledger"].resolve() != eligibility_target.resolve():
        shutil.copyfile(resolved["eligibility_ledger"], eligibility_target)
    cache_metadata = {
        **metadata,
        "reuse_validation": {
            "mode": cache_reuse["mode"],
            "directory_bundle": observed_bundle,
            "evidence_input_sha256": {
                name: str(record["sha256"]).upper()
                for name, record in sorted(inputs.items())
            },
        },
    }
    return RawPanelStore.open(cache_root), cache_metadata


def _adaptive_surface_qualification(
    store: RawPanelStore,
    *,
    field_ids: Sequence[str],
    current_runtime_fields: Iterable[str],
) -> tuple[pd.DataFrame, dict[str, Any], tuple[FieldContract, ...], pd.DataFrame]:
    """Qualify the frozen surface using adaptive dates only.

    The current Core Pack chooses the fields before this run.  This gate may
    abort for missing/constant inputs, but it never selects fields using the
    report-only block and never removes fields because of equivalence.
    """

    requested = tuple(field_ids)
    if len(requested) != len(set(requested)):
        raise ValueError("adaptive field surface contains duplicates")
    missing = sorted(set(requested) - set(store.metadata["field_ids"]))
    if missing:
        raise ValueError("adaptive field surface is absent from cache: " + ",".join(missing))
    time_slice = store.block_slice(ADAPTIVE_START, ADAPTIVE_END)
    timestamps = np.asarray(store.timestamp_ns[time_slice], dtype=np.int64)
    observed = np.asarray(store.observed()[:, time_slice], dtype=bool)
    pre_columns = timestamps < pd.Timestamp("2024-01-01T00:00:00Z").value
    top_columns = ~pre_columns
    current = set(current_runtime_fields)
    rows: list[dict[str, Any]] = []
    for field_id in requested:
        values = np.asarray(store.field(field_id)[:, time_slice], dtype=float)
        finite = np.isfinite(values) & observed
        clean = values[finite]
        asset_maximum = np.max(np.where(finite, values, -np.inf), axis=1)
        asset_minimum = np.min(np.where(finite, values, np.inf), axis=1)
        varying_assets = int(
            np.sum(
                np.isfinite(asset_maximum)
                & np.isfinite(asset_minimum)
                & ((asset_maximum - asset_minimum) > 1e-12)
            )
        )
        scope_rows = int(observed.sum())
        valid_rows = int(finite.sum())
        pre_scope = int(observed[:, pre_columns].sum())
        top_scope = int(observed[:, top_columns].sum())
        pre_valid = int(finite[:, pre_columns].sum())
        top_valid = int(finite[:, top_columns].sum())
        non_null_ratio = valid_rows / max(1, scope_rows)
        pre_non_null_ratio = pre_valid / max(1, pre_scope)
        top_non_null_ratio = top_valid / max(1, top_scope)
        coverage_ok = non_null_ratio >= 0.95 and varying_assets >= 80
        segment_ok = pre_non_null_ratio > 0.0 and top_non_null_ratio > 0.0
        family = infer_family(field_id)
        family_ok = family != "other"
        status = "ADMITTED" if coverage_ok and segment_ok and family_ok else "REJECTED"
        reasons = []
        if not segment_ok:
            reasons.append("ADAPTIVE_TWO_SEGMENT_MATERIALIZATION_FAILED")
        if not coverage_ok:
            reasons.append("ADAPTIVE_NON_NULL_OR_TIME_VARIATION_GATE")
        if not family_ok:
            reasons.append("NO_ECONOMIC_ROLE")
        value_type, unit = infer_type_unit(field_id)
        rows.append(
            {
                "field_id": field_id,
                "rows": scope_rows,
                "valid_rows": valid_rows,
                "non_null_ratio": non_null_ratio,
                "pre2024_non_null_ratio": pre_non_null_ratio,
                "top2024_non_null_ratio": top_non_null_ratio,
                "mean": float(np.mean(clean)) if clean.size else None,
                "variance": float(np.var(clean)) if clean.size else None,
                "minimum": float(np.min(clean)) if clean.size else None,
                "maximum": float(np.max(clean)) if clean.size else None,
                "assets_with_time_variation": varying_assets,
                "field_family": family,
                "value_type": value_type,
                "unit": unit,
                "sparse_semantics": False,
                "observable_lag_hours": 1,
                "lineage_ok": True,
                "economic_role": economic_role(field_id),
                "current_runtime_baseline": field_id in current,
                "admission_status": status,
                "rejection_reason": ";".join(reasons),
                "qualification_block": "DEVELOPMENT_ADAPTIVE_ONLY",
                "report_only_rows_read_for_admission": 0,
                "field_selection_role": "FROZEN_CURRENT_SURFACE_FAIL_CLOSED_ONLY",
            }
        )
    audit = pd.DataFrame(rows)
    admitted_rows = audit[audit["admission_status"].eq("ADMITTED")]
    contracts = tuple(
        FieldContract(
            str(row.field_id),
            str(row.value_type),
            str(row.unit),
            int(row.observable_lag_hours),
            "CURRENT_CORE_PACK_ADAPTIVE_ONLY_QUALIFICATION",
        )
        for row in admitted_rows.itertuples(index=False)
    )
    registry_rows = [
        {
            "field_id": row.field_id,
            "field_family": row.field_family,
            "value_type": row.value_type,
            "unit": row.unit,
            "observable_lag_hours": int(row.observable_lag_hours),
            "economic_role": row.economic_role,
            "current_runtime_baseline": bool(row.current_runtime_baseline),
            "non_null_ratio": float(row.non_null_ratio),
            "assets_with_time_variation": int(row.assets_with_time_variation),
        }
        for row in admitted_rows.itertuples(index=False)
    ]
    registry = {
        "schema_version": 1,
        "status": "ADMITTED_ADAPTIVE_ONLY" if len(contracts) == len(requested) else "DATA_ADEQUACY_UNDERPOWERED",
        "field_count": len(contracts),
        "field_families": sorted({str(row["field_family"]) for row in registry_rows}),
        "fields": registry_rows,
        "qualification_block": {
            "start": ADAPTIVE_START,
            "end_exclusive": ADAPTIVE_END,
            "report_only_rows_read_for_admission": 0,
        },
    }
    registry["registry_sha256"] = _payload_sha(registry_rows)
    equivalence = field_equivalence_audit(
        store,
        requested,
        block_start=ADAPTIVE_START,
        block_end=ADAPTIVE_END,
    )
    return audit, registry, contracts, equivalence


def _contracts_payload(contracts: Sequence[FieldContract]) -> list[dict[str, Any]]:
    return [
        {
            "field_id": item.field_id,
            "value_type": item.value_type,
            "unit": item.unit,
            "observable_lag_hours": item.observable_lag_hours,
            "pit_authority": item.pit_authority,
        }
        for item in contracts
    ]


def _contracts_from_payload(rows: Sequence[Mapping[str, Any]]) -> tuple[FieldContract, ...]:
    return tuple(
        FieldContract(
            str(row["field_id"]),
            str(row["value_type"]),
            str(row["unit"]),
            int(row["observable_lag_hours"]),
            str(row["pit_authority"]),
        )
        for row in rows
    )


def _trim_working_set() -> None:
    gc.collect()
    if os.name == "nt":
        try:
            ctypes.windll.psapi.EmptyWorkingSet(ctypes.windll.kernel32.GetCurrentProcess())
        except (AttributeError, OSError):
            pass


WORKING_SET_TRIM_RSS_THRESHOLD_BYTES = 805_306_368


def _working_set_trim_due(*, current_rss: int, lane_index: int, lane_count: int) -> bool:
    return bool(
        current_rss >= WORKING_SET_TRIM_RSS_THRESHOLD_BYTES
        or lane_index == lane_count - 1
    )


@dataclass(slots=True)
class LanePolicy:
    policy: str
    seed: int
    registry: TypedExpressionRegistry
    parameters: Mapping[str, Any] = field(default_factory=dict)
    rng: random.Random = field(init=False)
    seen: set[str] = field(default_factory=set)
    rewards: dict[str, float] = field(default_factory=dict)
    candidates: dict[str, CandidateSpec] = field(default_factory=dict)
    skeleton_visits: Counter[str] = field(default_factory=Counter)
    skeleton_rewards: dict[str, list[float]] = field(default_factory=lambda: defaultdict(list))
    proposal_order: list[str] = field(default_factory=list)
    cem_probabilities: dict[str, dict[str, float]] = field(default_factory=dict)
    cem_update_count: int = 0
    step: int = 0

    def __post_init__(self) -> None:
        if self.policy not in SUPPORTED_POLICIES:
            raise ValueError(self.policy)
        self.parameters = dict(self.parameters)
        self.rng = random.Random(self.seed)
        if self.policy == "cem_distribution_v1":
            self._validate_cem_parameters()
            self.cem_probabilities = {
                axis: {str(value): 1.0 / len(values) for value in values}
                for axis, values in self._cem_domains().items()
            }
        if self.policy == "evolutionary_typed_v1":
            self._validate_evolution_parameters()

    def _cem_parameter(self, name: str, default: Any) -> Any:
        return self.parameters.get(name, default)

    def _validate_cem_parameters(self) -> None:
        generation_size = int(self._cem_parameter("generation_size", 16))
        elite_fraction = float(self._cem_parameter("elite_fraction", 0.25))
        smoothing = float(self._cem_parameter("smoothing", 0.5))
        minimum_probability = float(
            self._cem_parameter("minimum_probability", 0.005)
        )
        if generation_size < 4:
            raise ValueError("CEM generation_size must be at least four")
        if not 0.0 < elite_fraction <= 0.5:
            raise ValueError("CEM elite_fraction must be in (0, 0.5]")
        if not 0.0 < smoothing <= 1.0:
            raise ValueError("CEM smoothing must be in (0, 1]")
        if not 0.0 <= minimum_probability < 1.0 / len(skeleton_registry()):
            raise ValueError("CEM minimum_probability is incompatible with support")

    def _validate_evolution_parameters(self) -> None:
        if int(self.parameters.get("warmup", 16)) < 4:
            raise ValueError("typed evolution warmup must be at least four")
        probability = float(self.parameters.get("exploration_probability", 0.25))
        if not 0.0 <= probability <= 1.0:
            raise ValueError("typed evolution exploration probability is invalid")
        if int(self.parameters.get("tournament_size", 4)) < 2:
            raise ValueError("typed evolution tournament must include two candidates")

    @staticmethod
    def _cem_domains() -> dict[str, tuple[Any, ...]]:
        return {
            "skeleton_id": tuple(item.skeleton_id for item in skeleton_registry()),
            "left_window": WINDOWS,
            "right_window": WINDOWS,
            "beta": BETAS,
            "left_normalizer": NORMALIZERS,
            "right_normalizer": NORMALIZERS,
            "horizon_hours": HORIZONS,
        }

    def distribution_hash(self) -> str:
        return _payload_sha(self.cem_probabilities)

    def _distribution_entropy(self) -> dict[str, float]:
        return {
            axis: float(-sum(value * math.log(value) for value in probabilities.values()))
            for axis, probabilities in self.cem_probabilities.items()
        }

    def _refresh_cem_distribution(self) -> None:
        generation_size = int(self._cem_parameter("generation_size", 16))
        if self.step == 0 or self.step % generation_size:
            return
        generation_ids = self.proposal_order[-generation_size:]
        if len(generation_ids) != generation_size or any(
            candidate_id not in self.rewards for candidate_id in generation_ids
        ):
            raise RuntimeError("CEM generation cannot update before complete feedback")
        elite_count = max(
            1,
            int(math.ceil(generation_size * float(self._cem_parameter("elite_fraction", 0.25)))),
        )
        elite_ids = sorted(
            generation_ids,
            key=lambda candidate_id: (self.rewards[candidate_id], candidate_id),
            reverse=True,
        )[:elite_count]
        smoothing = float(self._cem_parameter("smoothing", 0.5))
        floor = float(self._cem_parameter("minimum_probability", 0.005))
        domains = self._cem_domains()
        for axis, values in domains.items():
            counts = Counter()
            applicable = 0
            for candidate_id in elite_ids:
                candidate = self.candidates[candidate_id]
                skeleton = next(
                    item
                    for item in skeleton_registry()
                    if item.skeleton_id == candidate.skeleton_id
                )
                if (
                    axis != "skeleton_id"
                    and axis
                    not in _effective_generation_gene_names(
                        skeleton, candidate.generation_genes
                    )
                ):
                    continue
                value = (
                    candidate.skeleton_id
                    if axis == "skeleton_id"
                    else candidate.generation_genes[axis]
                )
                counts[str(value)] += 1
                applicable += 1
            if not applicable:
                continue
            blended = {
                str(value): (
                    (1.0 - smoothing) * self.cem_probabilities[axis][str(value)]
                    + smoothing * counts[str(value)] / applicable
                )
                for value in values
            }
            total = sum(blended.values())
            remaining = 1.0 - floor * len(values)
            self.cem_probabilities[axis] = {
                key: floor + remaining * value / total
                for key, value in blended.items()
            }
        self.cem_update_count += 1

    def _cem_choice(self, axis: str) -> Any:
        values = self._cem_domains()[axis]
        weights = [self.cem_probabilities[axis][str(value)] for value in values]
        return self.rng.choices(values, weights=weights, k=1)[0]

    def _propose_cem_candidate(self) -> CandidateSpec:
        skeleton_id = str(self._cem_choice("skeleton_id"))
        skeleton = next(
            item for item in skeleton_registry() if item.skeleton_id == skeleton_id
        )
        roles = field_role_coverage(tuple(self.registry.fields.values()))["roles"]
        left_field = self.rng.choice(roles[skeleton.field_roles[0]])
        right_options = roles[skeleton.field_roles[1]]
        distinct = [field_id for field_id in right_options if field_id != left_field]
        genes = {
            "left_field": left_field,
            "right_field": self.rng.choice(distinct or right_options),
            "left_window": self._cem_choice("left_window"),
            "right_window": self._cem_choice("right_window"),
            "beta": self._cem_choice("beta"),
            "left_normalizer": self._cem_choice("left_normalizer"),
            "right_normalizer": self._cem_choice("right_normalizer"),
            "horizon_hours": self._cem_choice("horizon_hours"),
        }
        return candidate_from_genes(
            self.registry, skeleton=skeleton, genes=genes, roles=roles
        )

    def _typed_evolution_parent(self) -> CandidateSpec:
        size = min(int(self.parameters.get("tournament_size", 4)), len(self.rewards))
        participant_ids = self.rng.sample(sorted(self.rewards), size)
        parent_id = max(
            participant_ids,
            key=lambda candidate_id: (self.rewards[candidate_id], candidate_id),
        )
        return self.candidates[parent_id]

    def state_hash(self) -> str:
        return _payload_sha(
            {
                "policy": self.policy,
                "seed": self.seed,
                "step": self.step,
                "seen": sorted(self.seen),
                "rewards": sorted(self.rewards.items()),
                "registry": _contracts_payload(tuple(self.registry.fields.values())),
                "parameters": dict(self.parameters),
                "proposal_order": list(self.proposal_order),
                "skeleton_visits": sorted(self.skeleton_visits.items()),
                "skeleton_rewards": {
                    key: list(values) for key, values in sorted(self.skeleton_rewards.items())
                },
                "cem_probabilities": self.cem_probabilities,
                "cem_update_count": self.cem_update_count,
                "rng": repr(self.rng.getstate()),
            }
        )

    def _mean_reward(self, skeleton_id: str) -> float:
        values = self.skeleton_rewards.get(skeleton_id, [])
        return float(np.mean(values)) if values else -11.0

    def _choose_skeleton(self) -> tuple[Any, str | None]:
        skeletons = skeleton_registry()
        parent_id: str | None = None
        if self.policy == "canonical_typed_random":
            return skeletons[(self.step + self.seed) % len(skeletons)], None
        if self.policy == "cem_diversity_v2":
            explore = self.step < 8 or self.rng.random() < 0.20
            if explore:
                return skeletons[(self.step + self.seed) % len(skeletons)], None
            scores = np.asarray([max(-10.0, self._mean_reward(item.skeleton_id)) for item in skeletons])
            weights = np.exp(scores - np.max(scores)) + 1e-6
            selected = self.rng.choices(skeletons, weights=weights.tolist(), k=1)[0]
            return selected, None
        if self.policy == "uct_ucb_like":
            unvisited = [item for item in skeletons if self.skeleton_visits[item.skeleton_id] == 0]
            if unvisited:
                return unvisited[0], None
            total = max(1, sum(self.skeleton_visits.values()))
            selected = max(
                skeletons,
                key=lambda item: self._mean_reward(item.skeleton_id)
                + math.sqrt(2.0 * math.log(total) / self.skeleton_visits[item.skeleton_id]),
            )
            return selected, None
        if self.step < 8 or not self.rewards:
            return skeletons[(self.step + self.seed) % len(skeletons)], None
        elites = sorted(self.rewards, key=lambda key: (self.rewards[key], key), reverse=True)[:8]
        parent_id = self.rng.choice(elites)
        parent = self.candidates[parent_id]
        selected = next(item for item in skeletons if item.skeleton_id == parent.skeleton_id)
        return selected, parent_id

    def propose(self) -> tuple[CandidateSpec, dict[str, Any]]:
        if self.policy == "evolutionary_typed_v1":
            return self._propose_typed_evolution()
        if self.policy == "cem_distribution_v1":
            self._refresh_cem_distribution()
        before = self.state_hash()
        if self.policy == "cem_distribution_v1":
            skeleton = None
            parent_id = None
        else:
            skeleton, parent_id = self._choose_skeleton()
        candidate: CandidateSpec | None = None
        duplicate_resamples = 0
        limit = int(self.parameters.get("duplicate_resample_limit", 16))
        for duplicate_resamples in range(limit + 1):
            candidate = (
                self._propose_cem_candidate()
                if self.policy == "cem_distribution_v1"
                else generate_candidate(self.registry, skeleton=skeleton, rng=self.rng)
            )
            if candidate.candidate_id not in self.seen:
                break
        assert candidate is not None
        if candidate.candidate_id in self.seen:
            raise RuntimeError("duplicate resample limit exhausted")
        changed: list[str] = []
        if parent_id is not None:
            parent = self.candidates[parent_id]
            for name in ("raw_fields", "rolling_windows", "horizon_hours", "operator_path"):
                if getattr(parent, name) != getattr(candidate, name):
                    changed.append(name)
        self.seen.add(candidate.candidate_id)
        self.candidates[candidate.candidate_id] = candidate
        self.proposal_order.append(candidate.candidate_id)
        self.skeleton_visits[candidate.skeleton_id] += 1
        metadata = {
            "proposal_step": self.step,
            "policy_state_hash_before": before,
            "parent_id": parent_id,
            "mutation_receipt": {
                "parent_id": parent_id,
                "child_id": candidate.candidate_id,
                "changed_genes": changed,
            }
            if parent_id is not None
            else None,
            "mutation_receipt_verified": None,
            "duplicate_resamples": duplicate_resamples,
            "first_visit": True,
            "cache_hit": False,
            "cumulative_skeleton_exposure": self.skeleton_visits[candidate.skeleton_id],
            "policy_diagnostics": {
                "cem_update_count": self.cem_update_count,
                "distribution_hash": self.distribution_hash()
                if self.policy == "cem_distribution_v1"
                else None,
                "distribution_entropy": self._distribution_entropy()
                if self.policy == "cem_distribution_v1"
                else None,
            },
        }
        self.step += 1
        return candidate, metadata

    def _propose_typed_evolution(self) -> tuple[CandidateSpec, dict[str, Any]]:
        before = self.state_hash()
        warmup = int(self.parameters.get("warmup", 16))
        exploration_probability = float(
            self.parameters.get("exploration_probability", 0.25)
        )
        explore = (
            self.step < warmup
            or not self.rewards
            or self.rng.random() < exploration_probability
        )
        limit = int(self.parameters.get("duplicate_resample_limit", 16))
        candidate: CandidateSpec | None = None
        parent_id: str | None = None
        receipt: dict[str, Any] | None = None
        verified: bool | None = None
        duplicate_resamples = 0
        skeletons = skeleton_registry()
        for duplicate_resamples in range(limit + 1):
            if explore:
                skeleton = skeletons[(self.step + self.seed + duplicate_resamples) % len(skeletons)]
                candidate = generate_candidate(
                    self.registry, skeleton=skeleton, rng=self.rng
                )
                parent_id = None
                receipt = None
                verified = None
            else:
                parent = self._typed_evolution_parent()
                parent_id = parent.candidate_id
                candidate, receipt = typed_mutate_candidate(
                    self.registry, parent=parent, rng=self.rng
                )
                verified = verify_typed_mutation_receipt(
                    self.registry, parent, candidate, receipt
                )
                if not verified:
                    raise RuntimeError("typed mutation receipt verification failed")
            if candidate.candidate_id not in self.seen:
                break
        assert candidate is not None
        if candidate.candidate_id in self.seen:
            raise RuntimeError("duplicate resample limit exhausted")
        self.seen.add(candidate.candidate_id)
        self.candidates[candidate.candidate_id] = candidate
        self.proposal_order.append(candidate.candidate_id)
        self.skeleton_visits[candidate.skeleton_id] += 1
        metadata = {
            "proposal_step": self.step,
            "policy_state_hash_before": before,
            "parent_id": parent_id,
            "mutation_receipt": receipt,
            "mutation_receipt_verified": verified,
            "duplicate_resamples": duplicate_resamples,
            "first_visit": True,
            "cache_hit": False,
            "cumulative_skeleton_exposure": self.skeleton_visits[candidate.skeleton_id],
            "policy_diagnostics": {
                "typed_mutation": receipt is not None,
                "receipt_sha256": receipt.get("receipt_sha256") if receipt else None,
            },
        }
        self.step += 1
        return candidate, metadata

    def update(self, candidate: CandidateSpec, reward: float) -> None:
        if candidate.candidate_id not in self.seen:
            raise PermissionError("unvisited candidate cannot receive feedback")
        if candidate.candidate_id in self.rewards:
            raise PermissionError("candidate feedback is immutable")
        value = float(reward)
        if not math.isfinite(value):
            value = -11.0
        self.rewards[candidate.candidate_id] = value
        self.skeleton_rewards[candidate.skeleton_id].append(value)


def _flat_pair_row(
    *,
    candidate: CandidateSpec,
    evaluation: Mapping[str, Any] | None,
    policy: str,
    seed: int,
    metadata: Mapping[str, Any],
    error: str | None,
) -> dict[str, Any]:
    if evaluation is None:
        reward = -11.0
        matched = False
        incremental: Mapping[str, Any] = {}
        timings: Mapping[str, Any] = {}
    else:
        reward = float(evaluation["pair_reward"])
        matched = bool(evaluation["matched_positive"])
        incremental = evaluation["incremental"]
        timings = evaluation["timings"]
    return {
        "candidate_id": candidate.candidate_id,
        "skeleton_id": candidate.skeleton_id,
        "mechanism_family": candidate.mechanism_family,
        "policy": policy,
        "seed": int(seed),
        "proposal_step": int(metadata["proposal_step"]),
        "parent_id": metadata.get("parent_id"),
        "mutation_receipt_json": json.dumps(metadata.get("mutation_receipt"), sort_keys=True),
        "mutation_receipt_verified": metadata.get("mutation_receipt_verified"),
        "policy_diagnostics_json": json.dumps(
            metadata.get("policy_diagnostics", {}), sort_keys=True
        ),
        "policy_state_hash_before": metadata["policy_state_hash_before"],
        "first_visit": bool(metadata["first_visit"]),
        "cache_hit": bool(metadata["cache_hit"]),
        "duplicate_resamples": int(metadata["duplicate_resamples"]),
        "cumulative_skeleton_exposure": int(metadata["cumulative_skeleton_exposure"]),
        "pair_evaluation_status": "PASS" if evaluation is not None else "FAIL",
        "failure_reason": error,
        "pair_reward": reward,
        "matched_positive": matched,
        "net_mean": incremental.get("net_mean"),
        "net_lcb": incremental.get("net_lcb"),
        "gross_mean": incremental.get("gross_mean"),
        "turnover_mean": incremental.get("turnover_mean"),
        "cost_mean": incremental.get("cost_mean"),
        "support": incremental.get("support"),
        "positive_month_fraction": incremental.get("positive_month_fraction"),
        "median_month": incremental.get("median_month"),
        "worst_month": incremental.get("worst_month"),
        "delta_weight_sha256": incremental.get("weight_sha256"),
        "candidate_spec_json": json.dumps(candidate.to_dict(), sort_keys=True),
        "evaluation_json": json.dumps(evaluation, sort_keys=True, default=str) if evaluation is not None else None,
        "field_read_seconds": timings.get("field_read_seconds"),
        "dag_materialization_seconds": timings.get("dag_materialization_seconds"),
        "mapping_seconds": timings.get("mapping_seconds"),
        "standalone_evaluator_seconds": timings.get("standalone_evaluator_seconds"),
        "incremental_sleeve_seconds": timings.get("incremental_sleeve_seconds"),
        "pair_peak_rss_bytes": timings.get("peak_rss_bytes"),
        "pair_peak_private_bytes": timings.get("peak_private_bytes"),
    }


def _run_lane_worker(
    cache_root: str,
    contract_rows: Sequence[Mapping[str, Any]],
    policy_name: str,
    seed: int,
    count: int,
    prior_rows: Sequence[Mapping[str, Any]] | None = None,
    policy_parameters: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    store = RawPanelStore.open(Path(cache_root))
    registry = TypedExpressionRegistry(_contracts_from_payload(contract_rows))
    policy = LanePolicy(
        policy_name, int(seed), registry, dict(policy_parameters or {})
    )
    replay_pass = True
    for prior in prior_rows or ():
        candidate, _ = policy.propose()
        if candidate.candidate_id != prior["candidate_id"]:
            replay_pass = False
            raise AssertionError("deterministic policy replay changed candidate identity")
        policy.update(candidate, float(prior["pair_reward"]))
    rows: list[dict[str, Any]] = []
    process = psutil.Process(os.getpid())
    peak_rss = process.memory_info().rss
    peak_private = getattr(process.memory_info(), "private", peak_rss)
    started = time.perf_counter()
    lane_count = int(count)
    for lane_index in range(lane_count):
        candidate, metadata = policy.propose()
        evaluation = None
        error = None
        try:
            evaluation = evaluate_pair(
                store=store,
                registry=registry,
                candidate=candidate,
                block_start=ADAPTIVE_START,
                block_end=ADAPTIVE_END,
                block_role="DEVELOPMENT_ADAPTIVE_FEEDBACK",
            )
        except (ValueError, FloatingPointError, MemoryError) as failure:
            error = type(failure).__name__ + ":" + str(failure)
        row = _flat_pair_row(
            candidate=candidate,
            evaluation=evaluation,
            policy=policy_name,
            seed=seed,
            metadata=metadata,
            error=error,
        )
        policy.update(candidate, float(row["pair_reward"]))
        row["policy_state_hash_after"] = policy.state_hash()
        rows.append(row)
        peak_rss = max(
            peak_rss,
            int(row.get("pair_peak_rss_bytes") or 0),
        )
        peak_private = max(
            peak_private,
            int(row.get("pair_peak_private_bytes") or 0),
        )
        del evaluation
        if _working_set_trim_due(
            current_rss=process.memory_info().rss,
            lane_index=lane_index,
            lane_count=lane_count,
        ):
            _trim_working_set()
    return {
        "policy": policy_name,
        "seed": seed,
        "rows": rows,
        "elapsed_seconds": time.perf_counter() - started,
        "peak_rss_bytes": peak_rss,
        "peak_private_bytes": peak_private,
        "deterministic_replay_pass": replay_pass,
    }


def _challenge_worker(
    cache_root: str,
    contract_rows: Sequence[Mapping[str, Any]],
    rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    store = RawPanelStore.open(Path(cache_root))
    registry = TypedExpressionRegistry(_contracts_from_payload(contract_rows))
    output: list[dict[str, Any]] = []
    for row in rows:
        candidate = CandidateSpec.from_dict(json.loads(str(row["candidate_spec_json"])))
        evaluation = None
        error = None
        try:
            evaluation = evaluate_pair(
                store=store,
                registry=registry,
                candidate=candidate,
                block_start=REPORT_ONLY_START,
                block_end=REPORT_ONLY_END,
                block_role="DEVELOPMENT_REPORT_ONLY_NO_FEEDBACK",
            )
        except (ValueError, FloatingPointError, MemoryError) as failure:
            error = type(failure).__name__ + ":" + str(failure)
        output.append(
            {
                "candidate_id": candidate.candidate_id,
                "skeleton_id": candidate.skeleton_id,
                "mechanism_family": candidate.mechanism_family,
                "policy": row["policy"],
                "seed": int(row["seed"]),
                "pair_evaluation_status": "PASS" if evaluation is not None else "FAIL",
                "failure_reason": error,
                "pair_reward": float(evaluation["pair_reward"]) if evaluation else -11.0,
                "matched_positive": bool(evaluation["matched_positive"]) if evaluation else False,
                "net_mean": evaluation["incremental"]["net_mean"] if evaluation else None,
                "net_lcb": evaluation["incremental"]["net_lcb"] if evaluation else None,
                "positive_month_fraction": evaluation["incremental"]["positive_month_fraction"] if evaluation else None,
                "median_month": evaluation["incremental"]["median_month"] if evaluation else None,
                "worst_month": evaluation["incremental"]["worst_month"] if evaluation else None,
                "delta_weight_sha256": evaluation["incremental"]["weight_sha256"] if evaluation else None,
                "evaluation_json": json.dumps(evaluation, sort_keys=True, default=str) if evaluation else None,
                "policy_feedback_written": False,
            }
        )
        del evaluation
        _trim_working_set()
    return output


def _parallel_lanes(
    *,
    cache_root: Path,
    contracts: Sequence[FieldContract],
    lanes: Sequence[tuple[str, int]],
    count_per_lane: int,
    max_workers: int,
    prior: Mapping[tuple[str, int], Sequence[Mapping[str, Any]]] | None = None,
    policy_parameters: Mapping[str, Mapping[str, Any]] | None = None,
    policy_order: Sequence[str] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    contract_rows = _contracts_payload(contracts)
    rows: list[dict[str, Any]] = []
    resources: list[dict[str, Any]] = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                _run_lane_worker,
                str(cache_root),
                contract_rows,
                policy,
                seed,
                count_per_lane,
                list((prior or {}).get((policy, seed), ())),
                dict((policy_parameters or {}).get(policy, {})),
            ): (policy, seed)
            for policy, seed in lanes
        }
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            rows.extend(result["rows"])
            resources.append({key: value for key, value in result.items() if key != "rows"})
            print(
                json.dumps(
                    {
                        "event": "strict_lane_complete",
                        "policy": result["policy"],
                        "seed": result["seed"],
                        "pairs": len(result["rows"]),
                        "seconds": result["elapsed_seconds"],
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
    order = tuple(policy_order or POLICIES)
    rows.sort(
        key=lambda row: (
            int(row["seed"]),
            order.index(str(row["policy"])),
            int(row["proposal_step"]),
        )
    )
    return rows, resources


def _parallel_challenge(
    *,
    cache_root: Path,
    contracts: Sequence[FieldContract],
    rows: Sequence[Mapping[str, Any]],
    max_workers: int,
    chunk_size: int = 32,
) -> list[dict[str, Any]]:
    contracts_payload = _contracts_payload(contracts)
    chunks = [rows[index : index + chunk_size] for index in range(0, len(rows), chunk_size)]
    output: list[dict[str, Any]] = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(_challenge_worker, str(cache_root), contracts_payload, chunk)
            for chunk in chunks
        ]
        for index, future in enumerate(concurrent.futures.as_completed(futures), start=1):
            output.extend(future.result())
            if index % 8 == 0 or index == len(futures):
                print(
                    json.dumps(
                        {
                            "event": "report_only_challenge_progress",
                            "chunks_complete": index,
                            "chunks_total": len(futures),
                        },
                        sort_keys=True,
                    ),
                    flush=True,
                )
    output.sort(key=lambda row: (int(row["seed"]), POLICIES.index(str(row["policy"])), str(row["candidate_id"])))
    return output


def _cluster_key(row: Mapping[str, Any]) -> str:
    candidate = CandidateSpec.from_dict(json.loads(str(row["candidate_spec_json"])))
    return _payload_sha(
        {
            "mechanism_family": candidate.mechanism_family,
            "skeleton_id": candidate.skeleton_id,
            "field_families": sorted(candidate.field_families),
            "operator_path": candidate.operator_path,
        }
    )


def _cluster_evidence(
    adaptive: Sequence[Mapping[str, Any]], challenge: Sequence[Mapping[str, Any]]
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    challenge_map = {str(row["candidate_id"]): row for row in challenge}
    groups: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in adaptive:
        enriched = dict(row)
        enriched["cluster_id"] = _cluster_key(row)
        groups[enriched["cluster_id"]].append(enriched)
    cluster_rows: list[dict[str, Any]] = []
    reproduced: list[dict[str, Any]] = []
    for cluster_id, rows in groups.items():
        adaptive_positive = [row for row in rows if bool(row["matched_positive"])]
        challenge_positive = [
            row
            for row in rows
            if bool(challenge_map.get(str(row["candidate_id"]), {}).get("matched_positive", False))
        ]
        seeds = sorted({int(row["seed"]) for row in challenge_positive})
        item = {
            "cluster_id": cluster_id,
            "mechanism_family": rows[0]["mechanism_family"],
            "skeleton_id": rows[0]["skeleton_id"],
            "candidates": len(rows),
            "adaptive_matched_positive": len(adaptive_positive),
            "challenge_matched_positive": len(challenge_positive),
            "challenge_positive_seeds": seeds,
            "cross_seed_reproduced": len(seeds) >= 2,
        }
        cluster_rows.append(item)
        if item["cross_seed_reproduced"]:
            reproduced.append(item)
    family_rows = []
    for family in MECHANISM_FAMILIES:
        local = [row for row in adaptive if row["mechanism_family"] == family]
        challenge_local = [challenge_map.get(str(row["candidate_id"]), {}) for row in local]
        family_rows.append(
            {
                "mechanism_family": family,
                "strict_pairs": len(local),
                "adaptive_matched_positive": sum(bool(row["matched_positive"]) for row in local),
                "challenge_matched_positive": sum(bool(row.get("matched_positive")) for row in challenge_local),
                "challenge_positive_yield": sum(bool(row.get("matched_positive")) for row in challenge_local) / max(1, len(local)),
            }
        )
    clusters = {"schema_version": 1, "clusters": sorted(cluster_rows, key=lambda row: row["cluster_id"]), "family_yield": family_rows}
    reproduction = {"schema_version": 1, "cross_seed_reproduced_clusters": len(reproduced), "clusters": reproduced}
    counts = {
        "adaptive_positive_clusters": sum(row["adaptive_matched_positive"] > 0 for row in cluster_rows),
        "challenge_positive_clusters": sum(row["challenge_matched_positive"] > 0 for row in cluster_rows),
        "cross_seed_reproduced_clusters": len(reproduced),
        "reproduced_families": len({row["mechanism_family"] for row in reproduced}),
        "maximum_family_challenge_yield": max((row["challenge_positive_yield"] for row in family_rows), default=0.0),
    }
    return clusters, reproduction, counts


def _policy_audit(
    rows: Sequence[Mapping[str, Any]], *, minimum_positive_seed_count: int = 2
) -> dict[str, Any]:
    summaries = []
    by_lane: dict[tuple[str, int], list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        by_lane[(str(row["policy"]), int(row["seed"]))].append(row)
    for (policy, seed), local in sorted(by_lane.items()):
        rewards = [float(row["pair_reward"]) for row in local]
        top_count = max(1, int(math.ceil(0.10 * len(rewards)))) if rewards else 0
        top_decile = sorted(rewards, reverse=True)[:top_count]
        candidate_rewards = {
            str(row["candidate_id"]): float(row["pair_reward"]) for row in local
        }
        parent_uplifts = [
            float(row["pair_reward"]) - candidate_rewards[str(row["parent_id"])]
            for row in local
            if row.get("parent_id")
            and str(row["parent_id"]) in candidate_rewards
        ]
        field_ids: set[str] = set()
        for row in local:
            if row.get("candidate_spec_json"):
                field_ids.update(
                    CandidateSpec.from_dict(
                        json.loads(str(row["candidate_spec_json"]))
                    ).raw_fields
                )
        summaries.append(
            {
                "policy": policy,
                "seed": seed,
                "pairs": len(local),
                "unique_candidates": len({row["candidate_id"] for row in local}),
                "unique_candidate_rate": len({row["candidate_id"] for row in local})
                / max(1, len(local)),
                "mean_pair_reward": float(np.mean(rewards)) if rewards else None,
                "top_decile_mean_pair_reward": (
                    float(np.mean(top_decile)) if top_decile else None
                ),
                "matched_positive": sum(bool(row["matched_positive"]) for row in local),
                "matched_positive_yield": sum(
                    bool(row["matched_positive"]) for row in local
                )
                / max(1, len(local)),
                "skeleton_coverage": len({str(row["skeleton_id"]) for row in local}),
                "mechanism_family_coverage": len(
                    {str(row["mechanism_family"]) for row in local}
                ),
                "field_coverage": len(field_ids),
                "mutation_receipts": sum(str(row["mutation_receipt_json"]) != "null" for row in local),
                "parent_child_comparisons": len(parent_uplifts),
                "mean_parent_child_reward_uplift": (
                    float(np.mean(parent_uplifts)) if parent_uplifts else None
                ),
                "positive_parent_child_uplift_rate": (
                    sum(value > 0.0 for value in parent_uplifts)
                    / len(parent_uplifts)
                    if parent_uplifts
                    else None
                ),
                "cache_hits": sum(bool(row["cache_hit"]) for row in local),
            }
        )
    random_by_seed = {
        row["seed"]: row["mean_pair_reward"]
        for row in summaries
        if row["policy"] == "canonical_typed_random"
    }
    stable_improvement: dict[str, bool] = {}
    productivity_vs_random: dict[str, list[dict[str, Any]]] = {}
    for policy in POLICIES[1:]:
        margins = [
            row["mean_pair_reward"] - random_by_seed.get(row["seed"], float("nan"))
            for row in summaries
            if row["policy"] == policy
        ]
        stable_improvement[policy] = len(margins) >= 2 and sum(value > 0 for value in margins) >= 2
        comparisons: list[dict[str, Any]] = []
        for row in summaries:
            if row["policy"] != policy:
                continue
            baseline = next(
                (
                    item
                    for item in summaries
                    if item["policy"] == "canonical_typed_random"
                    and item["seed"] == row["seed"]
                ),
                None,
            )
            if baseline is None:
                continue
            comparisons.append(
                {
                    "seed": row["seed"],
                    "mean_pair_reward_margin": row["mean_pair_reward"]
                    - baseline["mean_pair_reward"],
                    "top_decile_reward_margin": row["top_decile_mean_pair_reward"]
                    - baseline["top_decile_mean_pair_reward"],
                    "matched_positive_yield_margin": row["matched_positive_yield"]
                    - baseline["matched_positive_yield"],
                    "unique_candidate_rate_margin": row["unique_candidate_rate"]
                    - baseline["unique_candidate_rate"],
                }
            )
        productivity_vs_random[policy] = comparisons
    cem_passes = sum(
        row["mean_pair_reward_margin"] > 0.0
        and row["top_decile_reward_margin"] > 0.0
        for row in productivity_vs_random.get("cem_diversity_v2", [])
    )
    evolutionary_joint_passes = sum(
        row["mean_pair_reward_margin"] > 0.0
        and row["top_decile_reward_margin"] > 0.0
        for row in productivity_vs_random.get("evolutionary", [])
    )
    evolutionary_parent_passes = sum(
        row["policy"] == "evolutionary"
        and row["mean_parent_child_reward_uplift"] is not None
        and row["mean_parent_child_reward_uplift"] > 0.0
        for row in summaries
    )
    return {
        "schema_version": 1,
        "lanes": summaries,
        "adaptive_policy_quality_improvement_vs_typed_random": stable_improvement,
        "policy_productivity_vs_typed_random": productivity_vs_random,
        "post_search_upgrade_qualification": {
            "minimum_positive_seed_count": minimum_positive_seed_count,
            "cem_diversity_v2": {
                "joint_mean_and_top_decile_positive_seeds": cem_passes,
                "decision": (
                    "ELIGIBLE_FOR_DISTRIBUTION_SEARCH_UPGRADE"
                    if cem_passes >= minimum_positive_seed_count
                    else "RETAIN_LITE_INSUFFICIENT_PRODUCTIVITY"
                ),
            },
            "evolutionary": {
                "joint_mean_and_top_decile_positive_seeds": evolutionary_joint_passes,
                "mean_parent_child_uplift_positive_seeds": evolutionary_parent_passes,
                "parent_child_inference_role": "UNMATCHED_DIAGNOSTIC_NOT_DECISION_AUTHORITY",
                "decision": (
                    "ELIGIBLE_FOR_TYPED_MUTATION_UPGRADE"
                    if evolutionary_joint_passes >= minimum_positive_seed_count
                    else "RETAIN_LITE_INSUFFICIENT_PRODUCTIVITY"
                ),
            },
            "role": "REPORT_ONLY_FUTURE_COMPILER_DECISION",
            "current_run_feedback": False,
        },
        "any_cross_seed_stable_policy_improvement": any(stable_improvement.values()),
        "unvisited_candidate_feedback": 0,
        "cross_policy_private_state_reads": 0,
        "deterministic_replay_required": True,
    }


def _robust_rows(
    adaptive: Sequence[Mapping[str, Any]], challenge: Sequence[Mapping[str, Any]]
) -> list[dict[str, Any]]:
    challenge_map = {str(row["candidate_id"]): row for row in challenge}
    rows: list[dict[str, Any]] = []
    for ordinal, adaptive_row in enumerate(adaptive):
        evaluation = json.loads(str(adaptive_row["evaluation_json"])) if adaptive_row.get("evaluation_json") else None
        challenge_row = challenge_map.get(str(adaptive_row["candidate_id"]))
        challenge_evaluation = (
            json.loads(str(challenge_row["evaluation_json"]))
            if challenge_row and challenge_row.get("evaluation_json")
            else None
        )
        adaptive_months = (
            [row["net_mean"] for row in evaluation["incremental"]["month_metrics"]]
            if evaluation
            else []
        )
        challenge_months = (
            [row["net_mean"] for row in challenge_evaluation["incremental"]["month_metrics"]]
            if challenge_evaluation
            else []
        )
        audit = robust_monthly_audit(
            [*adaptive_months, *challenge_months], seed=20260716 + ordinal
        )
        rows.append(
            {
                "candidate_id": adaptive_row["candidate_id"],
                "mechanism_family": adaptive_row["mechanism_family"],
                "policy": adaptive_row["policy"],
                "seed": int(adaptive_row["seed"]),
                "adaptive_net_mean": adaptive_row.get("net_mean"),
                "challenge_net_mean": challenge_row.get("net_mean") if challenge_row else None,
                "adaptive_challenge_sign_agreement": bool(
                    challenge_row
                    and adaptive_row.get("net_mean") is not None
                    and challenge_row.get("net_mean") is not None
                    and np.sign(float(adaptive_row["net_mean"])) == np.sign(float(challenge_row["net_mean"]))
                ),
                **audit,
            }
        )
    return rows


def _waterfall(
    structural: Mapping[str, Any],
    expressivity: Mapping[str, Any],
    adaptive: Sequence[Mapping[str, Any]],
    challenge: Sequence[Mapping[str, Any]],
    robust: Sequence[Mapping[str, Any]],
    reproduction: Mapping[str, Any],
) -> pd.DataFrame:
    pass_rows = [row for row in adaptive if row["pair_evaluation_status"] == "PASS"]
    challenge_pass = [row for row in challenge if row["pair_evaluation_status"] == "PASS"]
    stages = [
        ("proposal_attempts", structural["proposal_attempts"]),
        ("grammar_legal", structural["grammar_legal"]),
        ("PIT_unit_pass", structural["grammar_legal"]),
        ("exact_unique", structural["exact_unique"]),
        ("numeric_unique", expressivity["numeric_unique"]),
        ("behavior_unique", expressivity["behavior_unique"]),
        ("control_valid", expressivity["matched_control_valid"]),
        ("materialization_pass", len(pass_rows)),
        ("dynamic_support_pass", sum(float(row.get("support") or 0.0) >= 0.80 for row in pass_rows)),
        ("standalone_evaluation_pass", len(pass_rows) * 2),
        ("incremental_sleeve_pass", len(pass_rows)),
        ("adaptive_matched_positive", sum(bool(row["matched_positive"]) for row in pass_rows)),
        ("challenge_evaluation_pass", len(challenge_pass)),
        ("challenge_matched_positive", sum(bool(row["matched_positive"]) for row in challenge_pass)),
        ("robust_positive", sum(bool(row["robust_positive"]) for row in robust)),
        ("cross_seed_reproduced", int(reproduction["cross_seed_reproduced_clusters"])),
    ]
    return pd.DataFrame([{"stage": stage, "count": int(count)} for stage, count in stages])


def _failure_attribution(
    *,
    field_count: int,
    expressivity: Mapping[str, Any],
    adaptive: Sequence[Mapping[str, Any]],
    challenge: Sequence[Mapping[str, Any]],
    resource: Mapping[str, Any],
) -> tuple[str, list[str], dict[str, int]]:
    failures = Counter(
        str(row["failure_reason"]).split(":", 1)[-1]
        for row in adaptive
        if row["pair_evaluation_status"] != "PASS"
    )
    if field_count < 16:
        return "FIELD_AUTHORIZATION_NARROW", [], dict(failures)
    if expressivity["status"] != "PASS":
        mapping = {
            "COMPOSITIONAL_GENERATOR_TEMPLATE_COLLAPSE": "GENERATOR_TEMPLATE_COLLAPSE",
            "SEMANTIC_ALIAS_COLLAPSE": "SEMANTIC_ALIAS_COLLAPSE",
            "MATCHED_CONTROL_CONSTRUCTION_BOTTLENECK": "MATCHED_CONTROL_FAILURE",
            "FIELD_COMBINATION_UNDERCOVERAGE": "GENERATOR_TEMPLATE_COLLAPSE",
        }
        return mapping.get(str(expressivity["status"]), "GENERATOR_TEMPLATE_COLLAPSE"), [], dict(failures)
    if not bool(resource.get("stage_a_authorized")):
        return "COMPUTE_OR_IO_BOTTLENECK", [], dict(failures)
    if failures:
        primary = failures.most_common(1)[0][0]
        mapping = {
            "DYNAMIC_UNIVERSE_SUPPORT_COLLAPSE": "DYNAMIC_UNIVERSE_SUPPORT_COLLAPSE",
            "CONTROL_BEHAVIOR_EQUALS_PRIMARY": "MATCHED_CONTROL_FAILURE",
            "CONTROL_EXACT_IDENTITY_EQUALS_PRIMARY": "MATCHED_CONTROL_FAILURE",
        }
        token = mapping.get(primary, "DAG_MATERIALIZATION_FAILURE")
    else:
        passed = [row for row in adaptive if row["pair_evaluation_status"] == "PASS"]
        gross_positive = sum(float(row.get("gross_mean") or 0.0) > 0.0 for row in passed)
        matched = sum(bool(row["matched_positive"]) for row in passed)
        challenge_matched = sum(bool(row["matched_positive"]) for row in challenge)
        if matched and not challenge_matched:
            token = "ADAPTIVE_ONLY_OVERFIT"
        elif not gross_positive:
            token = "NO_GROSS_EDGE"
        elif not matched:
            turnover_dominated = sum(
                float(row.get("gross_mean") or 0.0) > 0.0
                and float(row.get("net_mean") or 0.0) <= 0.0
                for row in passed
            )
            token = "TURNOVER_COST_DOMINATED" if turnover_dominated > len(passed) / 2 else "CONTROL_NOT_BEATEN"
        else:
            token = "CHALLENGE_INSTABILITY"
    secondary = [key for key, _ in failures.most_common(3) if key != token]
    return token, secondary, dict(failures)


def _main_status(
    *,
    field_count: int,
    expressivity: Mapping[str, Any],
    resource: Mapping[str, Any],
    counts: Mapping[str, int],
    robust_positive_clusters: int,
    primary_bottleneck: str,
) -> str:
    if field_count < 16:
        return "CRYPTO_18M_FIELD_AUTHORIZATION_BOTTLENECK"
    if expressivity["status"] != "PASS":
        return "CRYPTO_18M_COMPOSITIONAL_GENERATOR_BOTTLENECK"
    if not resource.get("stage_a_authorized"):
        return "CRYPTO_18M_COMPUTE_OR_IO_BOTTLENECK"
    if counts["cross_seed_reproduced_clusters"] >= 3 and counts["reproduced_families"] >= 2 and robust_positive_clusters >= 3:
        return "CRYPTO_18M_COMPOSITIONAL_SEARCH_REPRODUCIBLE_MECHANISMS_FOUND"
    if counts["challenge_positive_clusters"] > 0:
        return "CRYPTO_18M_COMPOSITIONAL_SEARCH_LOCALIZED_MECHANISMS_ONLY"
    if primary_bottleneck == "ADAPTIVE_ONLY_OVERFIT":
        return "CRYPTO_18M_COMPOSITIONAL_SEARCH_ADAPTIVE_OVERFIT"
    if primary_bottleneck in {
        "MATCHED_CONTROL_FAILURE",
        "DAG_MATERIALIZATION_FAILURE",
    }:
        return "CRYPTO_18M_MATCHED_CONTROL_BOTTLENECK"
    if primary_bottleneck in {
        "DYNAMIC_UNIVERSE_SUPPORT_COLLAPSE",
        "MAPPING_DEGENERACY",
        "TURNOVER_COST_DOMINATED",
    }:
        return "CRYPTO_18M_SUPPORT_OR_COST_BOTTLENECK"
    return "CRYPTO_18M_COMPOSITIONAL_SEARCH_NO_EDGE_UNDER_CURRENT_AUTHORIZED_FIELDS"


def _report_text(decision: Mapping[str, Any]) -> str:
    return f"""# Crypto 18M Compositional Broad Search

## Decision

`{decision['main_status']}`

This is development-only evidence on the observed official archive/current-seed
surface.  The six-month report-only block is not formal validation, challenge,
forward, recent, or OOS evidence and never fed the search policy.

## Frozen execution

- source SHA: `{decision['source_sha']}`
- base closure: `{decision['base_closure_sha']}`
- admitted fields: {decision['admitted_field_count']} across {decision['field_family_count']} families
- proposal attempts: {decision['proposal_attempts']:,}
- strict adaptive pairs: {decision['strict_pairs']:,}
- report-only pair evaluations: {decision['report_only_pairs']:,}
- standalone evaluator calls: {decision['standalone_evaluator_calls']:,}
- incremental sleeve calls: {decision['incremental_sleeve_calls']:,}
- sealed reads: {decision['sealed_reads']}

## Evidence

- adaptive matched-positive clusters: {decision['adaptive_matched_positive_clusters']}
- report-only matched-positive clusters: {decision['challenge_matched_positive_clusters']}
- robust-positive candidates: {decision['robust_positive_candidates']}
- cross-seed reproduced clusters: {decision['cross_seed_reproduced_clusters']}
- primary bottleneck: `{decision['primary_bottleneck']}`

## Claim boundary

No formal OOS, full delisted-contract coverage, promotion, execution
recommendation, native aggTrades microstructure, or live-trading conclusion is
authorized.  Candidate promotion and all 2025+ reads remain forbidden.
"""


def _failure_report_text(decision: Mapping[str, Any]) -> str:
    rows = "\n".join(
        f"| {key} | {value} |" for key, value in sorted(decision["failure_counts"].items())
    ) or "| NONE | 0 |"
    return f"""# Crypto 18M Search Failure Attribution

Primary bottleneck: `{decision['primary_bottleneck']}`.

Secondary bottlenecks: {', '.join(decision['secondary_bottlenecks']) or 'none'}.

| Failure | Count |
|---|---:|
{rows}

The classification is layer-specific.  It must not be generalized to
`DATA_UNDERPOWERED` or `NO_ALPHA` outside the authorized field registry,
typed DAG, mapping, cost, and observed-archive scope.
"""


def _validate_config(config: Mapping[str, Any]) -> None:
    epoch_id = str(config.get("epoch_id"))
    if epoch_id not in {EPOCH_ID, CURRENT_FIELD_CONTINUATION_EPOCH_ID}:
        raise ValueError("unsupported 18M search epoch")
    if config["base_closure_sha"].lower() != "a115913ae333696482059b497472864871cebc9f":
        raise ValueError("base data authority changed")
    boundaries = config["boundaries"]
    for key in (
        "sealed_reads_allowed",
        "formal_performance_search",
        "candidate_promotion",
        "cross_sprint_adaptive_memory",
    ):
        if bool(boundaries[key]):
            raise PermissionError(f"forbidden boundary enabled: {key}")
    budget = config["budget"]
    if int(budget["proposal_attempts"]) < 500000:
        raise ValueError("structural budget is below 500,000")
    if int(budget["stage_a_pairs"]) != 4096 or int(budget["hard_cap_pairs"]) != 8192:
        raise ValueError("strict pair budget changed")
    if tuple(int(value) for value in budget["seeds"]) != SEEDS:
        raise ValueError("seed contract changed")
    if tuple(budget["policies"]) != POLICIES:
        raise ValueError("policy contract changed")
    if epoch_id == CURRENT_FIELD_CONTINUATION_EPOCH_ID:
        exact_budget = {
            "proposal_attempts": 500000,
            "minimum_legal_exact_unique": 100000,
            "minimum_behavior_diverse": 25000,
            "cost_preflight_pairs": 64,
            "stage_a_pairs": 4096,
            "maximum_stage_b_pairs": 4096,
            "hard_cap_pairs": 8192,
            "hard_cap_standalone_evaluations": 16384,
            "hard_cap_incremental_sleeve_evaluations": 8192,
        }
        if any(int(budget.get(key, -1)) != value for key, value in exact_budget.items()):
            raise ValueError("continuation frozen budget changed")
        if int(config["expressivity"].get("numeric_audit_candidates", -1)) != 50000:
            raise ValueError("continuation numeric audit budget changed")
        if config["budget"].get("cem_diversity_v2") != {
            "exploration_probability": 0.20,
            "duplicate_resample_limit": 16,
        }:
            raise ValueError("continuation CEM-lite contract changed")
        if int(config["resources"].get("max_workers", 0)) != 8:
            raise ValueError("continuation PC2 worker budget changed")
        if config.get("expected_environment") != {
            "python_version": "3.11.9",
            "packages": {
                "numpy": "2.1.3",
                "pandas": "2.2.3",
                "pyarrow": "19.0.1",
                "scipy": "1.17.1",
                "psutil": "7.0.0",
            },
        }:
            raise ValueError("continuation environment binding changed")
        if config.get("authorization") != "BOUNDED_DEVELOPMENT_ONLY_CURRENT_FIELD_CONTINUATION":
            raise ValueError("current-field continuation authorization changed")
        if config.get("fresh_policy_state") is not True:
            raise ValueError("continuation must start from fresh policy state")
        surface = config.get("field_surface", {})
        if (
            surface.get("context_id") != "BROAD_PANEL_BASELINE"
            or int(surface.get("expected_fields", 0)) != 39
            or surface.get("excluded_contexts") != ["CORE3_MICROSTRUCTURE_PILOT"]
        ):
            raise ValueError("current Broad field-surface contract changed")
        if budget.get("stage_b_activation") != "FROZEN_FULL_BUDGET":
            raise ValueError("continuation Stage B must be frozen before execution")
        cache_reuse = config.get("cache_reuse", {})
        if (
            cache_reuse.get("mode") != "PINNED_EXISTING_RAW_CACHE"
            or cache_reuse.get("expected_identity_sha256")
            != "CBD66860C54314A8376A5EA126E4FE5A9760FB766D250AD1F966DC1007EE99F0"
            or cache_reuse.get("directory_bundle", {}).get("bundle_sha256")
            != "D120C0444B2A5828CBE0C7B538DEF81A1D2E50689C941F4B1A96D2AE60D93FED"
        ):
            raise ValueError("continuation raw-cache binding changed")
        productivity = config.get("post_search_policy_productivity_gate", {})
        if (
            productivity.get("role")
            != "REPORT_ONLY_FUTURE_COMPILER_DECISION"
            or productivity.get("no_effect_on_current_run") is not True
            or int(productivity.get("minimum_positive_seed_count", 0)) != 2
        ):
            raise ValueError("post-search policy productivity gate changed")


def build_evidence(
    repo_root: Path, *, config_path: Path, source_sha: str | None = None
) -> dict[str, Any]:
    config = _read_json(config_path)
    _validate_config(config)
    for name, value in config.get("resources", {}).get("thread_caps", {}).items():
        os.environ[str(name)] = str(value)
    execution_environment = _environment_fingerprint()
    expected_environment = config.get("expected_environment")
    if expected_environment and (
        execution_environment["python_version"]
        != expected_environment["python_version"]
        or execution_environment["packages"] != expected_environment["packages"]
    ):
        raise RuntimeError("execution environment does not match the frozen binding")
    source_sha = (source_sha or _git_sha(repo_root)).lower()
    if source_sha != _git_sha(repo_root):
        raise ValueError("runtime must bind the checked-out source implementation SHA")
    runtime_root = repo_root / config["outputs"]["runtime_root"]
    cache_root = repo_root / config["cache_root"]
    report_path = repo_root / config["outputs"]["report"]
    failure_path = repo_root / config["outputs"]["failure_report"]
    if not _source_tree_clean_for_run(
        repo_root, allowed_paths=(runtime_root, report_path, failure_path)
    ):
        raise RuntimeError("source execution requires a clean implementation tree; only its own generated evidence may exist")
    epoch_id = str(config["epoch_id"])
    field_surface_binding, field_surface_ids = _current_field_surface_binding(
        repo_root, config
    )
    compiler_binding = _compiler_binding(repo_root)
    runtime_root.mkdir(parents=True, exist_ok=True)
    train_config_path = repo_root / config["train_surface_config"]
    train_config = _read_json(train_config_path)
    train_decision = _read_json(
        repo_root
        / train_config["outputs"]["runtime_root"]
        / "CRYPTO_TRAIN_DATA_ADEQUACY.json"
    )
    if train_decision["decision"] != "PASS_CRYPTO_TRAIN_SURFACE_18M_DEVELOPMENT_READY_WITH_SCOPE_LIMITS":
        raise PermissionError("18M train authority is not qualified")

    search_contract = {
        "schema_version": 1,
        "epoch_id": epoch_id,
        "authorization": config["authorization"],
        "base_closure_sha": config["base_closure_sha"],
        "source_sha": source_sha,
        "fresh_policy_state": bool(config.get("fresh_policy_state", True)),
        "compiler_binding": compiler_binding,
        "field_surface_binding": field_surface_binding,
        "cache_input_binding": config.get("cache_reuse"),
        "post_search_policy_productivity_gate": config.get(
            "post_search_policy_productivity_gate"
        ),
        "execution_environment": execution_environment,
        "train_surface_id": train_config["surface_id"],
        "train_content_bundle_sha256": train_decision["source_content_bundle_sha256"],
        "adaptive_block": {"start": ADAPTIVE_START, "end_exclusive": ADAPTIVE_END, "feedback": True},
        "development_report_only_block": {"start": REPORT_ONLY_START, "end_exclusive": REPORT_ONLY_END, "feedback": False},
        "target": "log(close[t+2+h] / close[t+2])",
        "horizons_hours": [1, 4],
        "dynamic_eligibility": "observed at t, required inputs available at t, at least 168 completed consecutive hours; no future survival selection",
        "boundaries": config["boundaries"],
        "budget": config["budget"],
    }
    _write_json(runtime_root / RUNTIME_OUTPUTS[0], search_contract)

    if config.get("cache_reuse"):
        store, cache_metadata = _load_pinned_cache_inputs(
            repo_root,
            cache_root=cache_root,
            runtime_root=runtime_root,
            cache_reuse=config["cache_reuse"],
        )
        if field_surface_ids is None:
            raise ValueError("pinned cache reuse requires a frozen field surface")
        field_audit, field_registry, contracts, equivalence = (
            _adaptive_surface_qualification(
                store,
                field_ids=field_surface_ids,
                current_runtime_fields=train_config["runtime_fields"],
            )
        )
    else:
        store, quality, registry_rows, cache_metadata = build_raw_panel_cache(
            repo_root,
            train_config=train_config,
            cache_root=cache_root,
            eligibility_path=runtime_root / RUNTIME_OUTPUTS[4],
            source_sha=source_sha,
            warmup_hours=int(
                config["dynamic_eligibility"]["minimum_history_hours"]
            ),
        )
        equivalence = field_equivalence_audit(store, quality["field_id"].tolist())
        field_audit, field_registry, contracts = qualify_fields(
            quality=quality,
            registry_rows=registry_rows,
            equivalence=equivalence,
            current_runtime_fields=train_config["runtime_fields"],
        )
    if field_surface_ids is not None:
        surface_set = set(field_surface_ids)
        admitted_by_id = {item.field_id: item for item in contracts}
        missing = sorted(surface_set - set(admitted_by_id))
        if missing:
            raise ValueError(
                "current field surface failed data admission: " + ",".join(missing)
            )
        contracts = tuple(
            admitted_by_id[field_id] for field_id in sorted(surface_set)
        )
        coverage = field_role_coverage(contracts)
        if not coverage["all_fields_reachable"]:
            raise ValueError(
                "admitted current fields are not generator-reachable: "
                + ",".join(coverage["unreachable_fields"])
            )
        field_audit = field_audit.copy()
        field_audit["continuation_surface_member"] = field_audit["field_id"].isin(
            surface_set
        )
        excluded = field_audit["admission_status"].eq("ADMITTED") & ~field_audit[
            "continuation_surface_member"
        ]
        field_audit.loc[excluded, "admission_status"] = (
            "EXCLUDED_NOT_CURRENT_FIELD_SURFACE"
        )
        field_audit.loc[excluded, "rejection_reason"] = (
            "NOT_IN_CURRENT_FIELD_SURFACE"
        )
        selected_registry_rows = [
            row for row in field_registry["fields"] if row["field_id"] in surface_set
        ]
        field_registry = {
            **field_registry,
            "status": "ADMITTED_CURRENT_FIELD_SURFACE",
            "field_count": len(selected_registry_rows),
            "field_families": sorted(
                {str(row["field_family"]) for row in selected_registry_rows}
            ),
            "fields": selected_registry_rows,
            "registry_sha256": _payload_sha(selected_registry_rows),
            "source_contract_identity_sha256": field_surface_binding[
                "contract_identity_sha256"
            ],
            "generator_role_coverage": coverage,
        }
        search_contract["field_surface_binding"] = {
            **field_surface_binding,
            "admitted_registry_sha256": field_registry["registry_sha256"],
            "admitted_fields": [item.field_id for item in contracts],
        }
        _write_json(runtime_root / RUNTIME_OUTPUTS[0], search_contract)
    field_audit.to_csv(runtime_root / RUNTIME_OUTPUTS[1], index=False, lineterminator="\n")
    _write_json(runtime_root / RUNTIME_OUTPUTS[2], field_registry)
    equivalence.to_csv(runtime_root / RUNTIME_OUTPUTS[3], index=False, lineterminator="\n")
    skeletons = skeleton_payload()
    _write_json(runtime_root / RUNTIME_OUTPUTS[5], skeletons)
    _write_json(runtime_root / RUNTIME_OUTPUTS[7], pair_contract_payload())
    _write_json(runtime_root / RUNTIME_OUTPUTS[8], feedback_contract_payload())

    registry = TypedExpressionRegistry(contracts)
    structural_candidates, structural = generate_structural_pool(
        registry,
        attempts=int(config["budget"]["proposal_attempts"]),
        seed=int(config["budget"]["seeds"][0]),
        retain=int(config["expressivity"]["numeric_audit_candidates"]),
    )
    expressivity = audit_numeric_expressivity(
        store=store,
        registry=registry,
        candidates=structural_candidates,
        structural=structural,
        maximum_candidates=int(config["expressivity"]["numeric_audit_candidates"]),
        checkpoint_path=runtime_root / ".expressivity_checkpoint.json",
    )
    _write_json(runtime_root / RUNTIME_OUTPUTS[6], expressivity)

    max_workers = int(config["resources"]["max_workers"])
    preflight_lanes = [
        ("canonical_typed_random", SEEDS[0]),
        ("canonical_typed_random", SEEDS[1]),
        ("cem_diversity_v2", SEEDS[0]),
        ("cem_diversity_v2", SEEDS[1]),
    ]
    preflight_started = time.perf_counter()
    preflight_rows, preflight_resources = _parallel_lanes(
        cache_root=cache_root,
        contracts=contracts,
        lanes=preflight_lanes,
        count_per_lane=16,
        max_workers=max_workers,
    )
    preflight_seconds = time.perf_counter() - preflight_started
    preflight_pass = sum(row["pair_evaluation_status"] == "PASS" for row in preflight_rows)
    estimated_stage_a_seconds = preflight_seconds * int(config["budget"]["stage_a_pairs"]) / 64.0
    peak_rss = max((int(row["peak_rss_bytes"]) for row in preflight_resources), default=0)
    available_memory = int(psutil.virtual_memory().available)
    minimum_free_memory = int(
        config["resources"].get("minimum_free_memory_before_stage_a_bytes", 0)
    )
    stage_a_authorized = (
        len(contracts) >= 16
        and len(field_registry["field_families"]) >= 5
        and expressivity["status"] == "PASS"
        and preflight_pass == 64
        and estimated_stage_a_seconds <= float(config["resources"]["maximum_estimated_stage_a_seconds"])
        and peak_rss <= int(config["resources"]["maximum_worker_peak_rss_bytes"])
        and available_memory >= minimum_free_memory
    )
    resource = {
        "schema_version": 1,
        "execution_environment": execution_environment,
        "cache_build": cache_metadata,
        "preflight_pairs": 64,
        "preflight_pass": preflight_pass,
        "preflight_seconds": preflight_seconds,
        "pair_seconds": [sum(float(row.get(name) or 0.0) for name in ("field_read_seconds", "dag_materialization_seconds", "mapping_seconds", "standalone_evaluator_seconds", "incremental_sleeve_seconds")) for row in preflight_rows],
        "worker_resources": preflight_resources,
        "peak_worker_rss_bytes": peak_rss,
        "available_memory_before_stage_a_bytes": available_memory,
        "estimated_stage_a_seconds": estimated_stage_a_seconds,
        "estimated_stage_a_plus_report_only_seconds": estimated_stage_a_seconds * 2.0,
        "max_workers": max_workers,
        "stage_a_authorized": stage_a_authorized,
        "stage_a_authorization_requirements": {
            "fields_at_least_16": len(contracts) >= 16,
            "field_families_at_least_5": len(field_registry["field_families"]) >= 5,
            "generator_expressivity_pass": expressivity["status"] == "PASS",
            "preflight_64_of_64": preflight_pass == 64,
            "time_budget": estimated_stage_a_seconds <= float(config["resources"]["maximum_estimated_stage_a_seconds"]),
            "rss_budget": peak_rss <= int(config["resources"]["maximum_worker_peak_rss_bytes"]),
            "free_memory_budget": available_memory >= minimum_free_memory,
        },
    }
    _write_json(runtime_root / RUNTIME_OUTPUTS[18], resource)

    adaptive_rows: list[dict[str, Any]] = []
    challenge_rows: list[dict[str, Any]] = []
    lane_resources: list[dict[str, Any]] = []
    if stage_a_authorized:
        lanes = [(policy, seed) for seed in SEEDS for policy in POLICIES]
        per_lane = int(config["budget"]["stage_a_pairs"]) // len(lanes)
        stage_a, stage_a_resources = _parallel_lanes(
            cache_root=cache_root,
            contracts=contracts,
            lanes=lanes,
            count_per_lane=per_lane,
            max_workers=max_workers,
        )
        adaptive_rows.extend(stage_a)
        lane_resources.extend(stage_a_resources)
        fixed_full_stage_b = (
            config["budget"].get("stage_b_activation")
            == "FROZEN_FULL_BUDGET"
        )
        if fixed_full_stage_b:
            # The continuation freezes its entire adaptive budget before any
            # report-only metric exists.  No report-only result can affect
            # scheduling, policy state, or survivor exposure.
            continue_stage_b = True
        else:
            stage_a_challenge = _parallel_challenge(
                cache_root=cache_root,
                contracts=contracts,
                rows=stage_a,
                max_workers=max_workers,
            )
            challenge_rows.extend(stage_a_challenge)
            _, _, counts_a = _cluster_evidence(stage_a, stage_a_challenge)
            policy_a = _policy_audit(stage_a)
            continue_stage_b = (
                counts_a["adaptive_positive_clusters"] >= 10
                or counts_a["challenge_positive_clusters"] >= 5
                or counts_a["maximum_family_challenge_yield"] > 0.005
                or bool(policy_a["any_cross_seed_stable_policy_improvement"])
            )
        if continue_stage_b:
            prior: dict[tuple[str, int], list[Mapping[str, Any]]] = defaultdict(list)
            for row in stage_a:
                prior[(str(row["policy"]), int(row["seed"]))].append(row)
            stage_b, stage_b_resources = _parallel_lanes(
                cache_root=cache_root,
                contracts=contracts,
                lanes=lanes,
                count_per_lane=int(config["budget"]["maximum_stage_b_pairs"]) // len(lanes),
                max_workers=max_workers,
                prior=prior,
            )
            adaptive_rows.extend(stage_b)
            lane_resources.extend(stage_b_resources)
            if not fixed_full_stage_b:
                challenge_rows.extend(
                    _parallel_challenge(
                        cache_root=cache_root,
                        contracts=contracts,
                        rows=stage_b,
                        max_workers=max_workers,
                    )
                )
        if fixed_full_stage_b:
            challenge_rows.extend(
                _parallel_challenge(
                    cache_root=cache_root,
                    contracts=contracts,
                    rows=adaptive_rows,
                    max_workers=max_workers,
                )
            )
    if len(adaptive_rows) > int(config["budget"]["hard_cap_pairs"]):
        raise AssertionError("strict hard cap exceeded")
    if 2 * len(adaptive_rows) > int(
        config["budget"]["hard_cap_standalone_evaluations"]
    ):
        raise AssertionError("adaptive standalone evaluator hard cap exceeded")
    if len(adaptive_rows) > int(
        config["budget"]["hard_cap_incremental_sleeve_evaluations"]
    ):
        raise AssertionError("adaptive incremental sleeve hard cap exceeded")

    policy_audit = _policy_audit(
        adaptive_rows,
        minimum_positive_seed_count=int(
            config.get("post_search_policy_productivity_gate", {}).get(
                "minimum_positive_seed_count", 2
            )
        ),
    )
    field_exposure: Counter[str] = Counter()
    for row in adaptive_rows:
        if row.get("candidate_spec_json"):
            field_exposure.update(
                CandidateSpec.from_dict(
                    json.loads(str(row["candidate_spec_json"]))
                ).raw_fields
            )
    expected_fields = {item.field_id for item in contracts}
    missing_field_exposure = sorted(expected_fields - set(field_exposure))
    policy_audit["current_field_exposure"] = {
        "expected_field_count": len(expected_fields),
        "exposed_field_count": len(expected_fields & set(field_exposure)),
        "missing_fields": missing_field_exposure,
        "proposal_counts": {
            field_id: int(field_exposure.get(field_id, 0))
            for field_id in sorted(expected_fields)
        },
        "scope": "DEVELOPMENT_ADAPTIVE_PAIRS",
    }
    if (
        epoch_id == CURRENT_FIELD_CONTINUATION_EPOCH_ID
        and adaptive_rows
        and missing_field_exposure
    ):
        raise AssertionError(
            "current field surface lacks adaptive proposal exposure: "
            + ",".join(missing_field_exposure)
        )
    policy_audit["lane_resources"] = lane_resources
    policy_audit["development_report_only_feedback_writes"] = sum(
        bool(row["policy_feedback_written"]) for row in challenge_rows
    )
    _write_json(runtime_root / RUNTIME_OUTPUTS[17], policy_audit)
    clusters, reproduction, counts = _cluster_evidence(adaptive_rows, challenge_rows)
    _write_json(runtime_root / RUNTIME_OUTPUTS[15], clusters)
    _write_json(runtime_root / RUNTIME_OUTPUTS[16], reproduction)
    robust = _robust_rows(adaptive_rows, challenge_rows)
    robust_positive_candidates = sum(bool(row["robust_positive"]) for row in robust)
    robust_positive_clusters = len(
        {
            _cluster_key(row)
            for row, audit in zip(adaptive_rows, robust)
            if bool(audit["robust_positive"])
        }
    )

    exposure = pd.DataFrame(
        [
            {
                key: row[key]
                for key in (
                    "candidate_id",
                    "skeleton_id",
                    "mechanism_family",
                    "policy",
                    "seed",
                    "proposal_step",
                    "parent_id",
                    "mutation_receipt_json",
                    "policy_state_hash_before",
                    "policy_state_hash_after",
                    "first_visit",
                    "cache_hit",
                    "cumulative_skeleton_exposure",
                    "pair_reward",
                )
            }
            for row in adaptive_rows
        ]
    )
    exposure.to_parquet(runtime_root / RUNTIME_OUTPUTS[9], index=False)
    strict = pd.DataFrame(adaptive_rows)
    strict.to_parquet(runtime_root / RUNTIME_OUTPUTS[11], index=False)
    incremental_columns = [
        "candidate_id",
        "skeleton_id",
        "mechanism_family",
        "policy",
        "seed",
        "pair_reward",
        "matched_positive",
        "net_mean",
        "net_lcb",
        "gross_mean",
        "turnover_mean",
        "cost_mean",
        "support",
        "positive_month_fraction",
        "median_month",
        "worst_month",
        "delta_weight_sha256",
    ]
    pd.DataFrame(adaptive_rows, columns=incremental_columns).to_parquet(
        runtime_root / RUNTIME_OUTPUTS[12], index=False
    )
    pd.DataFrame(challenge_rows).to_parquet(runtime_root / RUNTIME_OUTPUTS[13], index=False)
    pd.DataFrame(robust).to_parquet(runtime_root / RUNTIME_OUTPUTS[14], index=False)
    waterfall = _waterfall(structural, expressivity, adaptive_rows, challenge_rows, robust, reproduction)
    waterfall.to_csv(runtime_root / RUNTIME_OUTPUTS[10], index=False, lineterminator="\n")

    primary, secondary, failure_counts = _failure_attribution(
        field_count=len(contracts),
        expressivity=expressivity,
        adaptive=adaptive_rows,
        challenge=challenge_rows,
        resource=resource,
    )
    if config.get("cache_reuse"):
        post_run_cache_bundle = _directory_bundle(cache_root)
        pre_run_cache_bundle = cache_metadata["reuse_validation"]["directory_bundle"]
        if post_run_cache_bundle != pre_run_cache_bundle:
            raise RuntimeError("pinned raw cache changed during the continuation")
        resource["cache_build"]["reuse_validation"][
            "post_run_directory_bundle"
        ] = post_run_cache_bundle
        resource["cache_build"]["reuse_validation"]["post_run_unchanged"] = True
        _write_json(runtime_root / RUNTIME_OUTPUTS[18], resource)
    status = _main_status(
        field_count=len(contracts),
        expressivity=expressivity,
        resource=resource,
        counts=counts,
        robust_positive_clusters=robust_positive_clusters,
        primary_bottleneck=primary,
    )
    decision = {
        "schema_version": 1,
        "epoch_id": epoch_id,
        "main_status": status,
        "source_sha": source_sha,
        "base_closure_sha": config["base_closure_sha"],
        "train_surface_id": train_config["surface_id"],
        "train_content_bundle_sha256": train_decision["source_content_bundle_sha256"],
        "admitted_field_count": len(contracts),
        "field_family_count": len(field_registry["field_families"]),
        "proposal_attempts": int(structural["proposal_attempts"]),
        "legal_exact_unique": int(structural["exact_unique"]),
        "numeric_unique": int(expressivity["numeric_unique"]),
        "behavior_unique": int(expressivity["behavior_unique"]),
        "strict_pairs": len(adaptive_rows),
        "stage_a_pairs": min(len(adaptive_rows), int(config["budget"]["stage_a_pairs"])),
        "stage_b_pairs": max(0, len(adaptive_rows) - int(config["budget"]["stage_a_pairs"])),
        "report_only_pairs": len(challenge_rows),
        "adaptive_standalone_evaluator_calls": 2 * len(adaptive_rows),
        "adaptive_incremental_sleeve_calls": len(adaptive_rows),
        "report_only_standalone_evaluator_calls": 2 * len(challenge_rows),
        "report_only_incremental_sleeve_calls": len(challenge_rows),
        "standalone_evaluator_calls": 2 * (len(adaptive_rows) + len(challenge_rows)),
        "incremental_sleeve_calls": len(adaptive_rows) + len(challenge_rows),
        "adaptive_matched_positive_clusters": counts["adaptive_positive_clusters"],
        "challenge_matched_positive_clusters": counts["challenge_positive_clusters"],
        "robust_positive_candidates": robust_positive_candidates,
        "robust_positive_clusters": robust_positive_clusters,
        "cross_seed_reproduced_clusters": counts["cross_seed_reproduced_clusters"],
        "reproduced_families": counts["reproduced_families"],
        "primary_bottleneck": primary,
        "secondary_bottlenecks": secondary,
        "failure_counts": failure_counts,
        "sealed_reads": 0,
        "formal_performance_search": "FORBIDDEN",
        "candidate_promotion": "FORBIDDEN",
        "forward": "SEALED",
        "accepted_tag_movement": "FORBIDDEN",
        "claim_scope": "observed-official-archive current-seeded 18M development surface only",
        "field_surface_binding": search_contract.get("field_surface_binding"),
        "compiler_bundle_sha256": compiler_binding["bundle_sha256"],
        "stage_b_activation": config["budget"].get(
            "stage_b_activation", "LEGACY_REPORT_VISIBLE_CONDITIONAL"
        ),
        "cannot_conclude": [
            "formal OOS validity",
            "full historical delisted-contract coverage",
            "live execution or promotion readiness",
            "native aggTrades microstructure validity",
            "all-Crypto-market generality",
        ],
    }
    _write_json(runtime_root / RUNTIME_OUTPUTS[19], decision)
    report_path = repo_root / config["outputs"]["report"]
    failure_path = repo_root / config["outputs"]["failure_report"]
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_report_text(decision), encoding="utf-8", newline="\n")
    failure_path.write_text(_failure_report_text(decision), encoding="utf-8", newline="\n")

    artifact_paths = [
        runtime_root / name
        for name in RUNTIME_OUTPUTS
        if name != "CRYPTO_ARTIFACT_MANIFEST.json"
    ] + [
        report_path,
        failure_path,
        config_path,
        train_config_path,
        repo_root / "alphafactory_crypto" / "broad_search" / "expression.py",
        repo_root / "alphafactory_crypto" / "broad_search" / "panel18m.py",
        repo_root / "alphafactory_crypto" / "broad_search" / "compositional18m.py",
        repo_root / "alphafactory_crypto" / "broad_search" / "pair18m.py",
        repo_root / "alphafactory_crypto" / "broad_search" / "runner18m.py",
        repo_root / "scripts" / "crypto_18m_compositional_broad_search.py",
        repo_root / "tests" / "test_broad_search_expression.py",
        repo_root / "tests" / "test_crypto_18m_compositional_search.py",
    ]
    if field_surface_binding is not None:
        artifact_paths.append(repo_root / field_surface_binding["contract_path"])
    artifact_rows = [
        {
            "path": path.relative_to(repo_root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in sorted(set(artifact_paths))
    ]
    manifest = {
        "schema_version": 1,
        "epoch_id": epoch_id,
        "producer_source_sha": source_sha,
        "base_closure_sha": config["base_closure_sha"],
        "bindings": {
            "train_surface_id": train_config["surface_id"],
            "train_content_bundle_sha256": train_decision["source_content_bundle_sha256"],
            "field_registry_hash": field_registry["registry_sha256"],
            "field_surface": search_contract.get("field_surface_binding"),
            "compiler": compiler_binding,
            "DAG_grammar_hash": _payload_sha(registry.contract_payload()),
            "skeleton_registry_hash": skeletons["skeleton_registry_sha256"],
            "mapping_hash": mapping_contract_sha256(DEFAULT_MAPPING_CONTRACTS[CROSS_SECTIONAL_ZERO_NET]),
            "cost_hash": _payload_sha({"cost_bps": FIXED_COST_BPS, "turnover": "FULL_L1"}),
            "pair_feedback_hash": _payload_sha(feedback_contract_payload()),
            "adaptive_report_only_split_hash": _payload_sha(
                {"adaptive": [ADAPTIVE_START, ADAPTIVE_END], "report_only": [REPORT_ONLY_START, REPORT_ONLY_END]}
            ),
            "seeds": list(SEEDS),
            "budget": config["budget"],
            "fresh_policy_state": bool(config.get("fresh_policy_state", True)),
            "cache_input": config.get("cache_reuse"),
            "post_search_policy_productivity_gate": config.get(
                "post_search_policy_productivity_gate"
            ),
            "execution_environment": execution_environment,
        },
        "sealed_reads": 0,
        "artifacts": artifact_rows,
    }
    manifest["bundle_sha256"] = _payload_sha(artifact_rows)
    _write_json(runtime_root / RUNTIME_OUTPUTS[20], manifest)
    return {
        "result": "PASS",
        "main_status": status,
        "source_sha": source_sha,
        "strict_pairs": len(adaptive_rows),
        "report_only_pairs": len(challenge_rows),
        "sealed_reads": 0,
        "bundle_sha256": manifest["bundle_sha256"],
    }


def check_evidence(repo_root: Path, *, config_path: Path) -> dict[str, Any]:
    config = _read_json(config_path)
    _validate_config(config)
    runtime_root = repo_root / config["outputs"]["runtime_root"]
    manifest_path = runtime_root / "CRYPTO_ARTIFACT_MANIFEST.json"
    errors: list[str] = []
    if not manifest_path.is_file():
        return {"result": "FAIL", "errors": ["missing artifact manifest"]}
    manifest = _read_json(manifest_path)
    for record in manifest.get("artifacts", []):
        path = (repo_root / record["path"]).resolve()
        try:
            path.relative_to(repo_root.resolve())
        except ValueError:
            errors.append(f"path_escape:{record['path']}")
            continue
        if not path.is_file():
            errors.append(f"missing:{record['path']}")
        elif path.stat().st_size != int(record["bytes"]) or sha256_file(path) != record["sha256"]:
            errors.append(f"identity:{record['path']}")
    if _payload_sha(manifest.get("artifacts", [])) != manifest.get("bundle_sha256"):
        errors.append("bundle_sha256")
    decision = _read_json(runtime_root / "CRYPTO_SEARCH_DECISION.json")
    resource = _read_json(runtime_root / "CRYPTO_RESOURCE_PREFLIGHT.json")
    field_registry = _read_json(runtime_root / "CRYPTO_18M_COMPOSITIONAL_FIELD_REGISTRY.json")
    expressivity = _read_json(runtime_root / "CRYPTO_GENERATOR_EXPRESSIVITY_AUDIT.json")
    policy = _read_json(runtime_root / "CRYPTO_POLICY_BEHAVIOR_AUDIT.json")
    if decision.get("sealed_reads") != 0 or manifest.get("sealed_reads") != 0:
        errors.append("sealed_reads")
    if decision.get("formal_performance_search") != "FORBIDDEN" or decision.get("candidate_promotion") != "FORBIDDEN":
        errors.append("boundary_status")
    if field_registry.get("field_count", 0) >= 16 and expressivity.get("status") == "PASS" and resource.get("stage_a_authorized"):
        if int(decision.get("stage_a_pairs", 0)) != 4096:
            errors.append("stage_a_pair_count")
    if int(decision.get("strict_pairs", 0)) > 8192:
        errors.append("hard_cap")
    if policy.get("development_report_only_feedback_writes") != 0:
        errors.append("report_only_feedback")
    if config["epoch_id"] == CURRENT_FIELD_CONTINUATION_EPOCH_ID:
        if manifest.get("epoch_id") != CURRENT_FIELD_CONTINUATION_EPOCH_ID or decision.get(
            "epoch_id"
        ) != CURRENT_FIELD_CONTINUATION_EPOCH_ID:
            errors.append("continuation_epoch")
        exact_decision = {
            "admitted_field_count": 39,
            "proposal_attempts": 500000,
            "stage_a_pairs": 4096,
            "stage_b_pairs": 4096,
            "strict_pairs": 8192,
            "report_only_pairs": 8192,
            "adaptive_standalone_evaluator_calls": 16384,
            "adaptive_incremental_sleeve_calls": 8192,
        }
        for key, expected in exact_decision.items():
            if int(decision.get(key, -1)) != expected:
                errors.append(f"continuation_exact:{key}")
        if int(expressivity.get("numeric_audit_candidates", -1)) != 50000:
            errors.append("continuation_numeric_audit")
        if resource.get("preflight_pairs") != 64 or resource.get("preflight_pass") != 64:
            errors.append("continuation_preflight")
        if resource.get("max_workers") != 8 or resource.get("stage_a_authorized") is not True:
            errors.append("continuation_resource_authorization")
        if field_registry.get("field_count") != 39:
            errors.append("continuation_field_count")
        if policy.get("current_field_exposure", {}).get("missing_fields") != []:
            errors.append("continuation_field_exposure")
        if decision.get("stage_b_activation") != "FROZEN_FULL_BUDGET":
            errors.append("continuation_stage_b_activation")
        surface = manifest.get("bindings", {}).get("field_surface", {})
        if (
            surface.get("contract_identity_sha256")
            != config["field_surface"]["contract_identity_sha256"]
            or surface.get("selected_field_count") != 39
        ):
            errors.append("continuation_field_surface_binding")
        environment = manifest.get("bindings", {}).get("execution_environment", {})
        if (
            environment.get("python_version")
            != config["expected_environment"]["python_version"]
            or environment.get("packages")
            != config["expected_environment"]["packages"]
        ):
            errors.append("continuation_environment_binding")
        field_audit = pd.read_csv(runtime_root / RUNTIME_OUTPUTS[1])
        if (
            set(field_audit.get("qualification_block", []))
            != {"DEVELOPMENT_ADAPTIVE_ONLY"}
            or int(field_audit.get("report_only_rows_read_for_admission", pd.Series([1])).sum())
            != 0
        ):
            errors.append("continuation_adaptive_only_field_qualification")
        equivalence = pd.read_csv(runtime_root / RUNTIME_OUTPUTS[3])
        if set(equivalence.get("qualification_block", [])) != {
            "DEVELOPMENT_ADAPTIVE_ONLY"
        }:
            errors.append("continuation_adaptive_only_equivalence")
    try:
        subprocess.check_call(
            ["git", "cat-file", "-e", f"{manifest['producer_source_sha']}^{{commit}}"],
            cwd=repo_root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        errors.append("producer_source_sha")
    return {
        "result": "PASS" if not errors else "FAIL",
        "errors": errors,
        "main_status": decision.get("main_status"),
        "producer_source_sha": manifest.get("producer_source_sha"),
        "bundle_sha256": manifest.get("bundle_sha256"),
        "strict_pairs": decision.get("strict_pairs"),
        "sealed_reads": decision.get("sealed_reads"),
    }


__all__ = [
    "ADAPTIVE_END",
    "ADAPTIVE_START",
    "CURRENT_FIELD_CONTINUATION_EPOCH_ID",
    "EPOCH_ID",
    "POLICIES",
    "REPORT_ONLY_END",
    "REPORT_ONLY_START",
    "RUNTIME_OUTPUTS",
    "SEEDS",
    "LanePolicy",
    "build_evidence",
    "check_evidence",
]
