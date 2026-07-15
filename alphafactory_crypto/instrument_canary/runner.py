"""Reproducible evidence builder for the bounded real-data canary."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import random
import statistics
import subprocess
import threading
import time
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, replace
from itertools import combinations
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
import psutil

from alphafactory_crypto.instrument_capability.feedback import (
    FEASIBILITY_DIRECTIONS,
    FEASIBILITY_NORMALIZATION,
    FEASIBILITY_ORDER,
    FEASIBILITY_THRESHOLDS,
    StrictMetrics,
    aligned_feedback,
    feedback_contract_payload,
)
from alphafactory_crypto.instrument_capability.mapping import mapping_contract_payload
from alphafactory_crypto.instrument_capability.primitives import primitive_contract_payload

from .admission import (
    CandidateAuthorizationReceipt,
    authorize_candidate,
    real_data_feedback_contract_payload,
)
from .contracts import CandidateGenome
from .engine import CandidateObservation, LazySearchEngine, replay_policy_transcript
from .evaluator import (
    StrictEvaluation,
    array_sha256,
    evaluate_authorized_materialization,
)
from .grammar import FROZEN_RELEASE_FIELDS, MECHANISM_MAPPING, FrozenGrammar
from .materialize import MaterializedCandidate, materialize_authorized
from .policies import SUPPORTED_POLICIES
from .release import ReleasePanel, load_development_release, sha256_file


QUALIFIED = "CRYPTO_REAL_DATA_INSTRUMENT_CANARY_EXECUTION_QUALIFIED"
PARTIAL = "CRYPTO_REAL_DATA_INSTRUMENT_CANARY_PARTIALLY_QUALIFIED"
MISMATCH = "CRYPTO_REAL_DATA_INSTRUMENT_CANARY_MISMATCH_CONFIRMED"
BLOCKED = "CRYPTO_REAL_DATA_INSTRUMENT_CANARY_BLOCKED"

REQUIRED_OUTPUTS = (
    "CRYPTO_REAL_DATA_CANARY_CONTRACT.json",
    "CRYPTO_REAL_DATA_RELEASE_MANIFEST.json",
    "CRYPTO_LAZY_EVALUATION_LEDGER.csv",
    "CRYPTO_REAL_DATA_SEARCH_EXPOSURE.csv",
    "CRYPTO_ALGORITHM_VISIT_DISTRIBUTION.csv",
    "CRYPTO_FEEDBACK_STRICT_ALIGNMENT.csv",
    "CRYPTO_REAL_DATA_MAPPING_COST_ATTRIBUTION.csv",
    "CRYPTO_REAL_DATA_INSTRUMENT_CANARY_RESULT.json",
)
GRAPH_PROFILE_ID = "crypto-real-data-instrument-canary"
GRAPH_CONTRACT_IDS = frozenset(
    {
        "unique_active_primitive_semantics",
        "explicit_mapping_admission",
        "strict_feedback_admission",
        "sealed_evaluation_roles",
        "frozen_mutations",
        "explicit_boundary_authority",
        "bounded_existing_release_canary_authority",
        "lazy_first_visit_feedback_only",
        "approved_existing_release_only",
        "fail_closed_candidate_authorization",
        "fixed_full_l1_cost_evaluator",
        "canary_loads_approved_development_release",
        "canary_authorizes_first_visit_candidate",
        "canary_executes_canonical_primitive",
        "canary_applies_explicit_mapping",
        "canary_evaluates_mapped_turnover_cost",
        "canary_consumes_aligned_visited_feedback",
        "canary_enforces_sealed_boundaries",
    }
)
DOMAIN_CHECK_NAMES = frozenset(
    {
        "contract",
        "event_order",
        "ledger_contract",
        "policy_replay",
        "different_seed_regions",
        "first_evaluation_cap",
        "all_feedback_is_visited",
        "run_cache_exact",
        "strict_evaluator_every_first_visit",
        "numeric_alias_integrity",
        "sealed_reads_zero",
        "strict_feedback_alignment",
        "admission_decoy_rejection",
        "algorithm_behavior_qualification",
    }
)

SOURCE_AUTHORITY_PATHS = (
    "alphafactory_crypto/instrument_capability/feedback.py",
    "alphafactory_crypto/instrument_capability/mapping.py",
    "alphafactory_crypto/instrument_capability/primitives.py",
    "alphafactory_crypto/instrument_canary/__init__.py",
    "alphafactory_crypto/instrument_canary/admission.py",
    "alphafactory_crypto/instrument_canary/contracts.py",
    "alphafactory_crypto/instrument_canary/engine.py",
    "alphafactory_crypto/instrument_canary/evaluator.py",
    "alphafactory_crypto/instrument_canary/grammar.py",
    "alphafactory_crypto/instrument_canary/materialize.py",
    "alphafactory_crypto/instrument_canary/policies.py",
    "alphafactory_crypto/instrument_canary/release.py",
    "alphafactory_crypto/instrument_canary/runner.py",
    "config/crypto_real_data_instrument_canary_v1.json",
    "docs/adr/0003-bounded-real-data-lazy-search-instrument-canary.md",
    "scripts/crypto_real_data_instrument_canary.py",
    "profiles/crypto-real-data-instrument-canary.json",
)


def _json_ready(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_ready(item) for item in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        _json_ready(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def _payload_sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest().upper()


def _evidence_values_equal(left: Any, right: Any) -> bool:
    """Compare exact evidence while treating matching NaNs as the same value."""

    if isinstance(left, np.generic):
        left = left.item()
    if isinstance(right, np.generic):
        right = right.item()
    if isinstance(left, float) and isinstance(right, float):
        if math.isnan(left) or math.isnan(right):
            return math.isnan(left) and math.isnan(right)
        return left == right
    if isinstance(left, Mapping) and isinstance(right, Mapping):
        return set(left) == set(right) and all(
            _evidence_values_equal(left[key], right[key]) for key in left
        )
    if isinstance(left, (list, tuple)) and isinstance(right, (list, tuple)):
        return len(left) == len(right) and all(
            _evidence_values_equal(left_item, right_item)
            for left_item, right_item in zip(left, right)
        )
    return bool(left == right)


def _replayed_metric_matches(expected: Any, observed: float) -> bool:
    """Match a replayed metric without turning equal missing values into drift."""

    if expected is None or expected == "":
        return not math.isfinite(observed)
    expected_value = float(expected)
    if math.isnan(expected_value) or math.isnan(observed):
        return math.isnan(expected_value) and math.isnan(observed)
    if math.isinf(expected_value) or math.isinf(observed):
        return expected_value == observed
    return math.isclose(
        observed,
        expected_value,
        rel_tol=1e-12,
        abs_tol=1e-12,
    )


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            _json_ready(payload),
            indent=2,
            sort_keys=True,
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n",
        encoding="utf-8",
    )


def _csv_value(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (Mapping, list, tuple, set)):
        return json.dumps(_json_ready(value), sort_keys=True, separators=(",", ":"))
    if isinstance(value, float) and not math.isfinite(value):
        return ""
    return value


def _write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    columns: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for name in row:
            if name not in seen:
                seen.add(name)
                columns.append(name)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({name: _csv_value(row.get(name)) for name in columns})


def _git_sha(repo_root: Path) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=repo_root, text=True
    ).strip()


def _require_clean_source_tree(repo_root: Path) -> None:
    dirty = subprocess.check_output(
        [
            "git",
            "status",
            "--porcelain",
            "--untracked-files=all",
            "--",
            *SOURCE_AUTHORITY_PATHS,
        ],
        cwd=repo_root,
        text=True,
    )
    if dirty.strip():
        raise RuntimeError(
            "formal evidence requires every source-authority path to match HEAD"
        )


def _source_blob_rows(repo_root: Path, source_sha: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for relative in SOURCE_AUTHORITY_PATHS:
        path = repo_root / relative
        if not path.is_file():
            raise FileNotFoundError(f"missing source authority path: {relative}")
        committed = subprocess.check_output(
            ["git", "show", f"{source_sha}:{relative}"], cwd=repo_root
        )
        unchanged = subprocess.run(
            ["git", "diff", "--quiet", source_sha, "--", relative],
            cwd=repo_root,
            check=False,
        ).returncode == 0
        if not unchanged:
            raise RuntimeError(
                f"source authority path differs from bound commit: {relative}"
            )
        rows.append(
            {
                "path": relative,
                "bytes": len(committed),
                "sha256": hashlib.sha256(committed).hexdigest().upper(),
                "git_blob": subprocess.check_output(
                    ["git", "rev-parse", f"{source_sha}:{relative}"],
                    cwd=repo_root,
                    text=True,
                ).strip(),
            }
        )
    return rows


def _read_config(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_frozen_canary_contract(
    config: Mapping[str, Any], grammar: FrozenGrammar
) -> dict[str, Any]:
    errors: list[str] = []
    if config.get("authorization") != "BOUNDED_EXISTING_RELEASE_DEVELOPMENT_CANARY":
        errors.append("authorization scope changed")
    boundaries = config.get("boundaries", {})
    if boundaries.get("allowed_data_role") != "DEVELOPMENT_TRAIN_ONLY":
        errors.append("data role is not development-train-only")
    for name in (
        "new_data_integration",
        "candidate_promotion",
        "cross_sprint_adaptive_memory",
        "historical_runner_activation",
        "economic_alpha_claim",
    ):
        if boundaries.get(name) is not False:
            errors.append(f"boundary opened: {name}")
    sealed = set(boundaries.get("sealed_roles", ()))
    required_sealed = {
        "VALIDATION",
        "HOLDOUT",
        "TEST",
        "RECENT",
        "FORWARD",
        "CHALLENGE",
        "MAY_STRESS",
    }
    if not required_sealed.issubset(sealed):
        errors.append("sealed role list is incomplete")

    grammar_contract = config.get("grammar", {})
    if grammar.support_size != int(grammar_contract.get("exact_unique_legal_candidates", -1)):
        errors.append("grammar exact support drift")
    if grammar.contract_sha256 != grammar_contract.get("contract_sha256"):
        errors.append("grammar contract hash drift")
    if tuple(config["release"]["searchable_fields"]) != FROZEN_RELEASE_FIELDS:
        errors.append("release/grammar field authority split")
    if dict(config.get("mapping", {})) != dict(MECHANISM_MAPPING):
        errors.append("mechanism/mapping authority drift")

    target = config.get("target_horizon", {})
    required_target = {
        "horizons_hours": [1, 4],
        "feature_bucket_coordinate": "t",
        "feature_observable_time": "t+1h",
        "execution_time": "t+2h",
        "execution_delay_after_observable_hours": 1,
        "formula": "log(close[t+2h+horizon] / close[t+2h])",
        "all_metrics_role": "DEVELOPMENT_TRAIN_ONLY",
    }
    if any(target.get(name) != value for name, value in required_target.items()):
        errors.append("target/horizon/PIT contract drift")
    blocks = config.get("evaluation_blocks", {})
    expected_block_labels = [
        f"DEV_TRAIN_2024_{month:02d}" for month in range(1, 7)
    ]
    if (
        blocks.get("kind") != "FROZEN_UTC_CALENDAR_MONTHS"
        or blocks.get("labels") != expected_block_labels
        or blocks.get("feedback_role") is not True
        or blocks.get("selection_or_tuning_role") is not True
        or blocks.get("oos_role") is not False
    ):
        errors.append("development feedback block contract drift")
    cost = config.get("cost", {})
    required_cost = {
        "model_id": "FULL_L1_FIXED_5BPS_WITH_INITIAL_AND_TERMINAL",
        "cost_bps": 5.0,
        "initial_establishment_charged": True,
        "terminal_liquidation_charged": True,
    }
    if any(cost.get(name) != value for name, value in required_cost.items()):
        errors.append("turnover/cost contract drift")
    execution = config.get("execution", {})
    if (
        execution.get("model_id") != "EQUAL_CAPITAL_HORIZON_OFFSET_SLEEVES"
        or execution.get("horizon_1h_sleeves") != 1
        or execution.get("horizon_4h_sleeves") != 4
        or execution.get("overlapping_full_capital_hourly_rebalance") is not False
    ):
        errors.append("overlapping-sleeve execution contract drift")

    budget = config.get("budget", {})
    algorithms = tuple(budget.get("algorithms", ()))
    if algorithms != SUPPORTED_POLICIES:
        errors.append("algorithm registry/order drift")
    seeds = tuple(int(value) for value in budget.get("seeds", ()))
    if seeds != (20260715, 20260716):
        errors.append("seed contract drift")
    steps = int(budget.get("proposal_steps_per_seed_algorithm", 0))
    maximum = int(budget.get("maximum_proposal_steps_per_seed_algorithm", 0))
    formal = len(algorithms) * len(seeds) * steps
    if steps <= 0 or steps > maximum or maximum > 256:
        errors.append("lane budget exceeds frozen maximum")
    if formal != int(budget.get("formal_proposal_steps", -1)):
        errors.append("formal proposal budget arithmetic drift")
    preflight = int(budget.get("cost_preflight_evaluations", 0))
    superseded_preflight = int(
        budget.get("superseded_development_preflight_evaluations", 0)
    )
    if superseded_preflight != 32:
        errors.append("superseded preflight accounting drift")
    if formal + preflight + superseded_preflight > int(
        budget.get("total_first_evaluation_hard_cap", -1)
    ):
        errors.append("declared proposal+preflight budget exceeds first-evaluation cap")
    if (
        budget.get("fixed_lane_order") != "seed ascending then algorithm listed order"
        or budget.get("global_cache_scope") != "THIS_CANARY_RUN_ONLY"
    ):
        errors.append("lane order/cache scope drift")
    preflight_contract = config.get("cost_preflight", {})
    if (
        preflight_contract.get("time_start") != "2024-01-01T00:00:00Z"
        or preflight_contract.get("time_end") != "2024-01-14T23:00:00Z"
        or preflight_contract.get("selection_seed") != 20260715
        or preflight_contract.get("feedback_exposed") is not False
        or preflight_contract.get("policy_update_enabled") is not False
        or preflight_contract.get("persist_economic_metrics") is not False
        or "affine grammar stride" not in str(preflight_contract.get("candidate_selection", ""))
    ):
        errors.append("cost preflight contract drift")
    strict_sample = config.get("strict_audit_sample", {})
    expected_sample = {
        "top_feedback": 8,
        "deterministic_random": 8,
        "high_cost": 8,
        "high_concentration": 8,
        "low_feedback": 8,
        "random_seed": 20260731,
    }
    if strict_sample != expected_sample:
        errors.append("strict feedback audit sample drift")
    if config.get("behavior_qualification") != {
        "maximum_pairwise_visit_jaccard": 0.95,
        "evolutionary_bootstrap_visits_per_lane": 8,
        "expected_evolutionary_mutation_receipts_per_lane": 120,
    }:
        errors.append("algorithm behavior qualification drift")
    if config.get("resource_admission") != {
        "maximum_estimated_2048_seconds_p95": 3600.0,
        "maximum_sampled_peak_rss_delta_bytes": 2_147_483_648,
        "maximum_release_load_seconds": 120.0,
        "rss_sampling_interval_ms": 50,
    }:
        errors.append("resource admission drift")
    if errors:
        raise ValueError("; ".join(errors))
    return {
        "result": "PASS",
        "grammar_support_size": grammar.support_size,
        "grammar_contract_sha256": grammar.contract_sha256,
        "formal_proposals": formal,
        "preflight_evaluations": preflight,
        "superseded_preflight_evaluations": superseded_preflight,
        "first_evaluation_hard_cap": int(budget["total_first_evaluation_hard_cap"]),
    }


def _authorize(
    genome: Any,
    *,
    grammar: FrozenGrammar,
    panel: ReleasePanel,
    config: Mapping[str, Any],
    source_sha: str,
) -> CandidateAuthorizationReceipt:
    return authorize_candidate(
        genome,
        grammar=grammar,
        release_manifest=panel.release_manifest,
        expected_release=config["release"],
        target_contract=config["target_horizon"],
        source_code_sha=source_sha,
        cost_contract=config["cost"],
    )


def _affine_preflight_indices(
    support_size: int, *, seed: int, count: int
) -> tuple[int, ...]:
    if count <= 0 or count > support_size:
        raise ValueError("invalid preflight candidate count")
    rng = random.Random(int(seed))
    offset = rng.randrange(support_size)
    stride = rng.randrange(1, support_size)
    while math.gcd(stride, support_size) != 1:
        stride = rng.randrange(1, support_size)
    return tuple((offset + index * stride) % support_size for index in range(count))


@dataclass(frozen=True)
class CostPreflight:
    payload: Mapping[str, Any]
    rows: tuple[dict[str, Any], ...]


def run_cost_preflight(
    panel: ReleasePanel,
    *,
    grammar: FrozenGrammar,
    config: Mapping[str, Any],
    source_sha: str,
    release_load_seconds: float,
    release_load_rss_delta_bytes: int,
) -> CostPreflight:
    contract = config["cost_preflight"]
    count = int(config["budget"]["cost_preflight_evaluations"])
    indices = _affine_preflight_indices(
        grammar.support_size,
        seed=int(contract["selection_seed"]),
        count=count,
    )
    sample = panel.time_slice(contract["time_start"], contract["time_end"])
    process = psutil.Process(os.getpid())
    preflight_rss_baseline = process.memory_info().rss
    peak_rss = [preflight_rss_baseline]
    stop_sampling = threading.Event()

    rss_interval_ms = int(config["resource_admission"]["rss_sampling_interval_ms"])

    def sample_rss() -> None:
        while not stop_sampling.wait(rss_interval_ms / 1000.0):
            peak_rss[0] = max(peak_rss[0], process.memory_info().rss)

    sampler = threading.Thread(target=sample_rss, daemon=True)
    sampler.start()
    rows: list[dict[str, Any]] = []
    for ordinal, grammar_index in enumerate(indices):
        genome = grammar.decode(grammar_index)
        receipt = _authorize(
            genome,
            grammar=grammar,
            panel=panel,
            config=config,
            source_sha=source_sha,
        )
        rss_before = process.memory_info().rss
        started = time.perf_counter_ns()
        materialized = materialize_authorized(
            receipt, field_reader=lambda field_id: sample.fields[field_id]
        )
        materialized_at = time.perf_counter_ns()
        evaluation_status = "PASS"
        try:
            evaluate_authorized_materialization(
                receipt,
                materialized,
                sample,
                require_full_development_blocks=False,
            )
        except ValueError as error:
            if "no evaluable development coordinate" not in str(error):
                raise
            evaluation_status = "NO_EVALUABLE_SUPPORT"
        finished = time.perf_counter_ns()
        rss_after = process.memory_info().rss
        rows.append(
            {
                "preflight_ordinal": ordinal,
                "grammar_index": grammar_index,
                "candidate_id": genome.candidate_id,
                "field_id": genome.field_id,
                "representation_id": genome.representation_id,
                "primitive_id": genome.primitive_id,
                "mechanism_family": genome.mechanism_family,
                "mapping_id": receipt.mapping_id,
                "target_horizon_hours": genome.target_horizon_hours,
                "sample_coordinates": len(sample.timestamps),
                "materialize_and_map_ms": (materialized_at - started) / 1_000_000.0,
                "strict_evaluate_ms": (finished - materialized_at) / 1_000_000.0,
                "total_ms": (finished - started) / 1_000_000.0,
                "rss_before_bytes": rss_before,
                "rss_after_bytes": rss_after,
                "rss_delta_bytes": rss_after - rss_before,
                "evaluation_status": evaluation_status,
                "feedback_exposed": False,
                "policy_update_enabled": False,
                "economic_metrics_persisted": False,
            }
        )
        del materialized

    stop_sampling.set()
    sampler.join(timeout=1.0)
    peak_rss[0] = max(peak_rss[0], process.memory_info().rss)

    total_seconds = [row["total_ms"] / 1000.0 for row in rows]
    median = statistics.median(total_seconds)
    ordered = sorted(total_seconds)
    p95 = ordered[min(len(ordered) - 1, math.ceil(0.95 * len(ordered)) - 1)]
    scale = len(panel.timestamps) / len(sample.timestamps)
    hard_cap = int(config["budget"]["total_first_evaluation_hard_cap"])
    estimated_p95 = release_load_seconds + hard_cap * p95 * scale
    sampled_peak_delta = peak_rss[0] - preflight_rss_baseline
    resource_contract = config["resource_admission"]
    resource_checks = {
        "estimated_2048_p95": estimated_p95
        <= float(resource_contract["maximum_estimated_2048_seconds_p95"]),
        "sampled_peak_rss_delta": sampled_peak_delta
        <= int(resource_contract["maximum_sampled_peak_rss_delta_bytes"]),
        "release_load_rss_delta": max(0, release_load_rss_delta_bytes)
        <= int(resource_contract["maximum_sampled_peak_rss_delta_bytes"]),
        "release_load_seconds": release_load_seconds
        <= float(resource_contract["maximum_release_load_seconds"]),
    }
    payload = {
        "schema_version": 1,
        "result": "PASS" if all(resource_checks.values()) else "FAIL",
        "scope": "COST_ONLY_FEEDBACK_WITHHELD",
        "candidate_selection": contract["candidate_selection"],
        "selection_seed": int(contract["selection_seed"]),
        "candidate_count": count,
        "grammar_support_size": grammar.support_size,
        "full_universe_ranked_or_materialized": False,
        "sample_coordinates": len(sample.timestamps),
        "sample_time_start": contract["time_start"],
        "sample_time_end": contract["time_end"],
        "full_coordinates": len(panel.timestamps),
        "release_load_seconds": release_load_seconds,
        "release_load_rss_delta_bytes": release_load_rss_delta_bytes,
        "preflight_rss_baseline_bytes": preflight_rss_baseline,
        "preflight_peak_rss_bytes": peak_rss[0],
        "preflight_peak_rss_delta_bytes": sampled_peak_delta,
        "preflight_peak_rss_sampling_interval_ms": rss_interval_ms,
        "sample_candidate_median_seconds": median,
        "sample_candidate_p95_seconds": p95,
        "linear_coordinate_scale": scale,
        "estimated_2048_seconds_median": release_load_seconds + hard_cap * median * scale,
        "estimated_2048_seconds_p95": estimated_p95,
        "resource_admission": {
            "result": "PASS" if all(resource_checks.values()) else "FAIL",
            "checks": resource_checks,
            "contract": dict(resource_contract),
        },
        "feedback_exposed": False,
        "policy_updates": 0,
        "economic_metrics_persisted": False,
        "first_evaluations_charged_to_hard_cap": count,
        "superseded_development_preflight_evaluations": int(
            config["budget"]["superseded_development_preflight_evaluations"]
        ),
        "rows": rows,
    }
    return CostPreflight(payload=payload, rows=tuple(rows))


def _real_feedback_contract() -> dict[str, Any]:
    payload = real_data_feedback_contract_payload()
    payload["contract_sha256"] = _payload_sha256(payload)
    return payload


def _evaluation_evidence(
    receipt: CandidateAuthorizationReceipt,
    materialized: MaterializedCandidate,
    evaluation: StrictEvaluation | None,
    *,
    elapsed_ms: float,
    evaluation_error: str = "",
) -> dict[str, Any]:
    genome = receipt.genome
    base: dict[str, Any] = {
        "field_id": genome.field_id,
        "representation_id": genome.representation_id,
        "primitive_id": genome.primitive_id,
        "window": genome.window,
        "long_window": genome.long_window,
        "threshold": genome.threshold,
        "mechanism_family": genome.mechanism_family,
        "mapping_id": receipt.mapping_id,
        "mapping_contract_sha256": receipt.mapping_contract_sha256,
        "target_horizon_hours": receipt.target_horizon_hours,
        "release_view_sha256": receipt.release_view_sha256,
        "receipt_sha256": receipt.receipt_sha256,
        "field_array_sha256": materialized.field_array_sha256,
        "represented_array_sha256": materialized.represented_array_sha256,
        "signal_array_sha256": materialized.signal_array_sha256,
        "weight_array_sha256": materialized.weight_array_sha256,
        "feasible_array_sha256": materialized.feasible_array_sha256,
        "mapping_diagnostics_sha256": materialized.mapping_diagnostics_sha256,
        "mapping_execution_sha256": materialized.mapping_execution_sha256,
        "endpoint_clip_count": getattr(materialized, "endpoint_clip_count", 0),
        "first_visit_elapsed_ms": elapsed_ms,
        "evaluation_error": evaluation_error,
    }
    if evaluation is None:
        base.update(
            {
                "observations": 0,
                "strict_metrics_finite": False,
                "mapped_net_metric": None,
                "benchmark_increment": None,
                "worst_block_margin": None,
                "positive_block_fraction": None,
                "turnover": None,
                "cost": None,
                "concentration": None,
                "support": None,
                "gross_proxy": None,
            }
        )
        return base
    metrics = evaluation.metrics
    base.update(
        {
            "observations": evaluation.observations,
            "strict_metrics_finite": metrics.finite,
            "mapped_net_metric": metrics.mapped_net_metric,
            "benchmark_increment": metrics.benchmark_increment,
            "worst_block_margin": metrics.worst_block_margin,
            "positive_block_fraction": metrics.positive_block_fraction,
            "turnover": metrics.turnover,
            "cost": metrics.cost,
            "concentration": metrics.concentration,
            "support": metrics.support,
            "gross_proxy": metrics.gross_proxy,
            "gross_mean": evaluation.gross_mean,
            "net_mean": evaluation.net_mean,
            "net_standard_error": evaluation.net_standard_error,
            "net_lcb": evaluation.net_lcb,
            "increment_lcb": evaluation.increment_lcb,
            "execution_model_id": evaluation.execution_model_id,
            "overlapping_sleeves": evaluation.overlapping_sleeves,
            "initial_establishment_l1": evaluation.initial_establishment_l1,
            "subsequent_entry_l1": evaluation.subsequent_entry_l1,
            "rebalance_l1": evaluation.rebalance_l1,
            "transition_exit_l1": evaluation.transition_exit_l1,
            "terminal_liquidation_l1": evaluation.terminal_liquidation_l1,
            "total_turnover_l1": evaluation.total_turnover_l1,
            "total_cost": evaluation.total_cost,
            "block_metrics": list(evaluation.block_metrics),
            "cross_sectional_rank_ic_mean": evaluation.cross_sectional_rank_ic_mean,
            "cross_sectional_rank_ic_role": evaluation.cross_sectional_rank_ic_role,
            "lcb_warning": evaluation.lcb_warning,
        }
    )
    return base


def _first_visit_evaluator(
    receipt: CandidateAuthorizationReceipt, panel: ReleasePanel
) -> CandidateObservation:
    started = time.perf_counter_ns()
    materialized = materialize_authorized(
        receipt, field_reader=lambda field_id: panel.fields[field_id]
    )
    evaluation: StrictEvaluation | None
    error = ""
    try:
        evaluation = evaluate_authorized_materialization(receipt, materialized, panel)
        metrics = evaluation.metrics
    except ValueError as caught:
        if "no evaluable development coordinate" not in str(caught):
            raise
        error = "NO_EVALUABLE_DEVELOPMENT_COORDINATE"
        evaluation = None
        metrics = StrictMetrics(*(float("nan") for _ in range(9)), finite=False)
    decision = aligned_feedback(
        metrics,
        legal=True,
        mapping_present=True,
        wrong_lag=False,
        primitive_alias_conflict=False,
    )
    elapsed_ms = (time.perf_counter_ns() - started) / 1_000_000.0
    evidence = _evaluation_evidence(
        receipt,
        materialized,
        evaluation,
        elapsed_ms=elapsed_ms,
        evaluation_error=error,
    )
    return CandidateObservation(feedback=decision, evidence=evidence)


def _numeric_evaluation_key(
    receipt: CandidateAuthorizationReceipt, materialized: MaterializedCandidate
) -> str:
    """Identify every mapped input that can change the strict evaluator surface."""

    return _payload_sha256(
        {
            "release_view_sha256": receipt.release_view_sha256,
            "target_horizon_hours": receipt.target_horizon_hours,
            "mapping_contract_sha256": receipt.mapping_contract_sha256,
            "cost_contract_sha256": receipt.cost_contract_sha256,
            "oriented_weight_array_sha256": materialized.weight_array_sha256,
            "feasible_array_sha256": materialized.feasible_array_sha256,
            "mapping_diagnostics_sha256": materialized.mapping_diagnostics_sha256,
        }
    )


class RealDataFirstVisitEvaluator:
    """Materialize and strictly evaluate every exact-candidate first visit.

    Numerically identical mapped inputs are recorded as diagnostic aliases, but
    they never bypass strict evaluation.  Only the engine's exact-candidate
    cache is authorized to reuse a completed observation.
    """

    def __init__(self, panel: ReleasePanel, *, runtime_trace: Any | None = None) -> None:
        self.panel = panel
        self.runtime_trace = runtime_trace
        self._numeric_first_candidate: dict[str, str] = {}
        self.materializations = 0
        self.strict_evaluator_calls = 0
        self.numeric_alias_observations = 0

    def __call__(self, receipt: CandidateAuthorizationReceipt) -> CandidateObservation:
        started = time.perf_counter_ns()
        materialized = materialize_authorized(
            receipt,
            field_reader=lambda field_id: self.panel.fields[field_id],
            runtime_trace=self.runtime_trace,
        )
        self.materializations += 1
        negated_weight_sha = array_sha256(-materialized.mapped.weights)
        orientation_invariant_fingerprint = min(
            materialized.weight_array_sha256, negated_weight_sha
        )
        evaluation_key = _numeric_evaluation_key(receipt, materialized)
        group_first_candidate_id = self._numeric_first_candidate.get(evaluation_key)
        numeric_alias_detected = group_first_candidate_id is not None
        if group_first_candidate_id is None:
            group_first_candidate_id = receipt.candidate_id
            self._numeric_first_candidate[evaluation_key] = group_first_candidate_id
        else:
            self.numeric_alias_observations += 1

        evaluation: StrictEvaluation | None
        error = ""
        try:
            evaluation = evaluate_authorized_materialization(
                receipt, materialized, self.panel
            )
            metrics = evaluation.metrics
        except ValueError as caught:
            if "no evaluable development coordinate" not in str(caught):
                raise
            error = "NO_EVALUABLE_DEVELOPMENT_COORDINATE"
            evaluation = None
            metrics = StrictMetrics(
                *(float("nan") for _ in range(9)), finite=False
            )
        self.strict_evaluator_calls += 1
        if self.runtime_trace is not None:
            self.runtime_trace.observe_component(
                "real_data_mapping_cost_evaluator",
                implementation_path="alphafactory_crypto/instrument_canary/evaluator.py",
                function="evaluate_authorized_materialization",
                semantic_role="mapped_cost_evaluator",
                evidence_produced=True,
            )
            self.runtime_trace.observe_edge(
                "real_data_lazy_search_canary",
                "real_data_mapping_cost_evaluator",
                edge_type="RUNTIME_CALL",
                relationship="evaluates_mapped_turnover_cost",
                evidence={"candidate_id": receipt.candidate_id},
            )
        decision = aligned_feedback(
            metrics,
            legal=True,
            mapping_present=True,
            wrong_lag=False,
            primitive_alias_conflict=False,
        )
        if self.runtime_trace is not None:
            self.runtime_trace.observe_component(
                "adaptive_strict_feasibility_feedback",
                implementation_path="alphafactory_crypto/instrument_capability/feedback.py",
                function="aligned_feedback",
                semantic_role="adaptive_feedback_authority",
                evidence_produced=True,
            )
            self.runtime_trace.observe_edge(
                "real_data_lazy_search_canary",
                "adaptive_strict_feasibility_feedback",
                edge_type="RUNTIME_CALL",
                relationship="consumes_aligned_visited_feedback",
                evidence={"candidate_id": receipt.candidate_id},
            )
        elapsed_ms = (time.perf_counter_ns() - started) / 1_000_000.0
        evidence = _evaluation_evidence(
            receipt,
            materialized,
            evaluation,
            elapsed_ms=elapsed_ms,
            evaluation_error=error,
        )
        evidence.update(
            {
                "strict_evaluator_call_confirmed": True,
                "numeric_evaluation_key": evaluation_key,
                "orientation_invariant_weight_fingerprint": orientation_invariant_fingerprint,
                "numeric_alias_detected": numeric_alias_detected,
                "numeric_alias_cache_hit": False,
                "numeric_alias_group_first_candidate_id": group_first_candidate_id,
            }
        )
        return CandidateObservation(feedback=decision, evidence=evidence)

    @property
    def numeric_unique_inputs(self) -> int:
        return len(self._numeric_first_candidate)


def _strict_metrics_from_ledger(row: Mapping[str, Any]) -> StrictMetrics:
    values: list[float] = []
    for name in (*FEASIBILITY_ORDER, "gross_proxy"):
        value = row.get(name)
        values.append(float(value) if value is not None and value != "" else float("nan"))
    return StrictMetrics(*values, finite=bool(row.get("strict_metrics_finite", False)))


def _feedback_alignment(row: Mapping[str, Any]) -> tuple[bool, dict[str, Any]]:
    decision = aligned_feedback(
        _strict_metrics_from_ledger(row),
        legal=True,
        mapping_present=True,
        wrong_lag=False,
        primitive_alias_conflict=False,
    )
    expected_sort = tuple(row["feedback_sort_key"])
    actual_sort = tuple(decision.sort_key)
    numeric_sort_match = len(expected_sort) == len(actual_sort) and all(
        math.isclose(float(left), float(right), rel_tol=1e-12, abs_tol=1e-12)
        for left, right in zip(expected_sort, actual_sort)
    )
    passed = (
        bool(row["feedback_blocked"]) == decision.blocked
        and bool(row["feedback_feasible"]) == decision.feasible
        and tuple(row["feedback_violations"]) == decision.violations
        and math.isclose(
            float(row["feedback_distance"]),
            float(decision.distance),
            rel_tol=1e-12,
            abs_tol=1e-12,
        )
        and str(row["feedback_reason"]) == decision.reason
        and numeric_sort_match
    )
    return passed, {
        "recomputed_blocked": decision.blocked,
        "recomputed_feasible": decision.feasible,
        "recomputed_violations": list(decision.violations),
        "recomputed_distance": decision.distance,
        "recomputed_sort_key": list(decision.sort_key),
        "recomputed_reason": decision.reason,
    }


def _strict_feedback_audit(
    ledger: Sequence[Mapping[str, Any]],
    config: Mapping[str, Any],
    *,
    panel: ReleasePanel,
    grammar: FrozenGrammar,
    source_sha: str,
) -> dict[str, Any]:
    first_rows = [row for row in ledger if bool(row.get("first_evaluation"))]
    if not first_rows:
        return {"result": "FAIL", "reason": "NO_FIRST_EVALUATIONS", "sample_rows": []}
    alignment = [_feedback_alignment(row)[0] for row in ledger]
    sample_contract = config["strict_audit_sample"]
    sample_rows: list[dict[str, Any]] = []

    def add(category: str, rows: Iterable[Mapping[str, Any]]) -> None:
        for rank, row in enumerate(rows):
            passed, recomputed = _feedback_alignment(row)
            sample_rows.append(
                {
                    "sample_category": category,
                    "sample_rank": rank,
                    "candidate_id": row["candidate_id"],
                    "feedback_sort_key": row["feedback_sort_key"],
                    "feedback_feasible": row["feedback_feasible"],
                    "feedback_blocked": row["feedback_blocked"],
                    "cost": row.get("cost"),
                    "concentration": row.get("concentration"),
                    "alignment_pass": passed,
                    **recomputed,
                }
            )

    top_n = int(sample_contract["top_feedback"])
    low_n = int(sample_contract["low_feedback"])
    high_cost_n = int(sample_contract["high_cost"])
    high_concentration_n = int(sample_contract["high_concentration"])
    random_n = int(sample_contract["deterministic_random"])
    ranked = sorted(
        first_rows,
        key=lambda row: (tuple(row["feedback_sort_key"]), str(row["candidate_id"])),
        reverse=True,
    )
    add("TOP_FEEDBACK", ranked[:top_n])
    add("LOW_FEEDBACK", list(reversed(ranked[-low_n:])))
    add(
        "HIGH_COST",
        sorted(
            first_rows,
            key=lambda row: (
                float(row["cost"]) if row.get("cost") not in (None, "") else float("-inf"),
                str(row["candidate_id"]),
            ),
            reverse=True,
        )[:high_cost_n],
    )
    add(
        "HIGH_CONCENTRATION",
        sorted(
            first_rows,
            key=lambda row: (
                float(row["concentration"])
                if row.get("concentration") not in (None, "")
                else float("-inf"),
                str(row["candidate_id"]),
            ),
            reverse=True,
        )[:high_concentration_n],
    )
    rng = random.Random(int(sample_contract["random_seed"]))
    add("DETERMINISTIC_RANDOM", rng.sample(first_rows, min(random_n, len(first_rows))))

    # Independently rerun the selected strict surface without exposing the
    # result to any policy. Category overlap is evaluated once per candidate.
    independent: dict[str, dict[str, Any]] = {}
    first_by_id = {str(row["candidate_id"]): row for row in first_rows}
    for candidate_id in sorted({str(row["candidate_id"]) for row in sample_rows}):
        original = first_by_id[candidate_id]
        genome = CandidateGenome(
            field_id=str(original["field_id"]),
            representation_id=str(original["representation_id"]),
            primitive_id=str(original["primitive_id"]),
            window=(int(original["window"]) if original.get("window") is not None else None),
            long_window=(
                int(original["long_window"])
                if original.get("long_window") is not None
                else None
            ),
            threshold=(
                float(original["threshold"])
                if original.get("threshold") is not None
                else None
            ),
            mechanism_family=str(original["mechanism_family"]),
            target_horizon_hours=int(original["target_horizon_hours"]),
        )
        receipt = _authorize(
            genome,
            grammar=grammar,
            panel=panel,
            config=config,
            source_sha=source_sha,
        )
        materialized = materialize_authorized(
            receipt, field_reader=lambda field_id: panel.fields[field_id]
        )
        replay_error = ""
        try:
            evaluation = evaluate_authorized_materialization(
                receipt, materialized, panel
            )
            replay_metrics = evaluation.metrics
        except ValueError as caught:
            if "no evaluable development coordinate" not in str(caught):
                raise
            replay_error = "NO_EVALUABLE_DEVELOPMENT_COORDINATE"
            replay_metrics = StrictMetrics(
                *(float("nan") for _ in range(9)), finite=False
            )
        replay_decision = aligned_feedback(
            replay_metrics,
            legal=True,
            mapping_present=True,
            wrong_lag=False,
            primitive_alias_conflict=False,
        )
        metric_match = replay_metrics.finite == bool(
            original.get("strict_metrics_finite", False)
        )
        for name in (*FEASIBILITY_ORDER, "gross_proxy"):
            expected = original.get(name)
            observed = float(getattr(replay_metrics, name))
            metric_match = metric_match and _replayed_metric_matches(
                expected, observed
            )
        decision_match = (
            replay_decision.blocked == bool(original["feedback_blocked"])
            and replay_decision.feasible == bool(original["feedback_feasible"])
            and tuple(replay_decision.violations)
            == tuple(original["feedback_violations"])
            and tuple(replay_decision.sort_key)
            == tuple(original["feedback_sort_key"])
            and replay_decision.reason == str(original["feedback_reason"])
        )
        hashes_match = (
            materialized.signal_array_sha256 == original["signal_array_sha256"]
            and materialized.weight_array_sha256 == original["weight_array_sha256"]
            and materialized.feasible_array_sha256
            == original["feasible_array_sha256"]
            and materialized.mapping_diagnostics_sha256
            == original["mapping_diagnostics_sha256"]
            and materialized.mapping_execution_sha256
            == original["mapping_execution_sha256"]
        )
        expected_error = str(original.get("evaluation_error", ""))
        independent[candidate_id] = {
            "candidate_id": candidate_id,
            "metric_match": metric_match,
            "decision_match": decision_match,
            "signal_weight_hash_match": hashes_match,
            "evaluation_error_match": replay_error == expected_error,
            "feedback_exposed": False,
            "policy_update_enabled": False,
            "result": (
                "PASS"
                if metric_match
                and decision_match
                and hashes_match
                and replay_error == expected_error
                else "FAIL"
            ),
        }
    for row in sample_rows:
        row["independent_strict_replay_result"] = independent[
            str(row["candidate_id"])
        ]["result"]

    pairwise_inversions = 0
    for left_index, left in enumerate(sample_rows):
        for right in sample_rows[left_index + 1 :]:
            original_cmp = tuple(left["feedback_sort_key"]) < tuple(right["feedback_sort_key"])
            replay_cmp = tuple(left["recomputed_sort_key"]) < tuple(right["recomputed_sort_key"])
            if original_cmp != replay_cmp:
                pairwise_inversions += 1
    feasible_rank_keys = [tuple(row["feedback_sort_key"]) for row in first_rows if row["feedback_feasible"]]
    infeasible_rank_keys = [tuple(row["feedback_sort_key"]) for row in first_rows if not row["feedback_feasible"]]
    feasibility_monotonic = not feasible_rank_keys or not infeasible_rank_keys or min(feasible_rank_keys) > max(infeasible_rank_keys)
    top_k = ranked[:top_n]
    top_k_feasible = sum(bool(row["feedback_feasible"]) for row in top_k)
    result = (
        "PASS"
        if all(alignment)
        and all(row["alignment_pass"] for row in sample_rows)
        and all(row["result"] == "PASS" for row in independent.values())
        and pairwise_inversions == 0
        and feasibility_monotonic
        else "FAIL"
    )
    return {
        "schema_version": 1,
        "result": result,
        "full_ledger_rows_recomputed": len(alignment),
        "full_ledger_alignment_failures": len(alignment) - sum(alignment),
        "sample_contract": dict(sample_contract),
        "sample_rows": sample_rows,
        "independent_strict_replays": list(independent.values()),
        "independent_strict_replay_count": len(independent),
        "independent_replay_feedback_exposures": 0,
        "independent_replay_policy_updates": 0,
        "pairwise_comparisons": len(sample_rows) * (len(sample_rows) - 1) // 2,
        "pairwise_inversions": pairwise_inversions,
        "feasibility_monotonic": feasibility_monotonic,
        "top_k": len(top_k),
        "top_k_feasible": top_k_feasible,
        "top_k_blocked": sum(bool(row["feedback_blocked"]) for row in top_k),
    }


def _admission_decoy_audit(
    panel: ReleasePanel,
    *,
    grammar: FrozenGrammar,
    config: Mapping[str, Any],
    source_sha: str,
) -> dict[str, Any]:
    base = grammar.decode(0)
    cases: list[tuple[str, Any, dict[str, Any]]] = [
        ("INVALID_FIELD", replace(base, field_id="close_price"), {}),
        ("DEPRECATED_PRIMITIVE_ALIAS", replace(base, primitive_id="b1s:delta"), {}),
        (
            "WRONG_MAPPING",
            base,
            {"expected_mapping_id": "TIME_SERIES_DIRECTIONAL_STATEFUL"},
        ),
    ]
    wrong_target = dict(config["target_horizon"])
    wrong_target["execution_time"] = "t+1h"
    cases.append(("WRONG_LAG", base, {"target_contract": wrong_target}))
    rows: list[dict[str, Any]] = []
    for case_id, genome, overrides in cases:
        reads = 0

        def reader() -> None:
            nonlocal reads
            reads += 1

        rejected = False
        reason = ""
        arguments = {
            "grammar": grammar,
            "release_manifest": panel.release_manifest,
            "expected_release": config["release"],
            "target_contract": config["target_horizon"],
            "source_code_sha": source_sha,
            "cost_contract": config["cost"],
            "reader_callback": reader,
            **overrides,
        }
        try:
            authorize_candidate(genome, **arguments)
        except (ValueError, PermissionError) as error:
            rejected = True
            reason = str(error)
        rows.append(
            {
                "case_id": case_id,
                "rejected": rejected,
                "reader_calls": reads,
                "reason": reason,
                "result": "PASS" if rejected and reads == 0 else "FAIL",
            }
        )
    return {
        "schema_version": 1,
        "result": "PASS" if all(row["result"] == "PASS" for row in rows) else "FAIL",
        "cases": rows,
        "total_reader_calls": sum(row["reader_calls"] for row in rows),
    }


def _evolution_runtime_receipts_pass(ledger: Sequence[Mapping[str, Any]]) -> bool:
    lanes: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in ledger:
        if row["algorithm"] == "evolutionary":
            lanes[str(row["lane_id"])].append(row)
    if len(lanes) != 2:
        return False
    for rows in lanes.values():
        rows = sorted(rows, key=lambda row: int(row["step"]))
        visited: set[str] = set()
        receipt_count = 0
        for row in rows:
            raw = row.get("mutation_receipt")
            if raw:
                receipt = json.loads(str(raw))
                receipt_count += 1
                if (
                    receipt.get("parent_id") not in visited
                    or receipt.get("child_id") != row["candidate_id"]
                    or not receipt.get("changed_genes")
                ):
                    return False
            visited.add(str(row["candidate_id"]))
        if receipt_count != max(0, len(rows) - 8):
            return False
    return True


def _algorithm_behavior_audit(
    ledger: Sequence[Mapping[str, Any]],
    behavior_hashes: Mapping[str, str],
    config: Mapping[str, Any],
) -> dict[str, Any]:
    threshold = float(
        config["behavior_qualification"]["maximum_pairwise_visit_jaccard"]
    )
    comparisons: list[dict[str, Any]] = []
    for seed in config["budget"]["seeds"]:
        sets = {
            algorithm: {
                str(row["candidate_id"])
                for row in ledger
                if int(row["seed"]) == int(seed)
                and row["algorithm"] == algorithm
            }
            for algorithm in config["budget"]["algorithms"]
        }
        for left, right in combinations(config["budget"]["algorithms"], 2):
            union = sets[left] | sets[right]
            jaccard = len(sets[left] & sets[right]) / len(union) if union else 1.0
            comparisons.append(
                {
                    "seed": int(seed),
                    "left_algorithm": left,
                    "right_algorithm": right,
                    "left_unique_visits": len(sets[left]),
                    "right_unique_visits": len(sets[right]),
                    "intersection": len(sets[left] & sets[right]),
                    "union": len(union),
                    "jaccard": jaccard,
                    "pass": jaccard <= threshold,
                }
            )
    hashes_distinct = len(set(behavior_hashes.values())) == len(behavior_hashes)
    evolution_pass = _evolution_runtime_receipts_pass(ledger)
    passed = all(row["pass"] for row in comparisons) and hashes_distinct and evolution_pass
    return {
        "schema_version": 1,
        "result": "PASS" if passed else "FAIL",
        "behavior_hash_definition": "SHA256_OF_ORDERED_CANDIDATE_IDS_ONLY",
        "behavior_hashes": dict(behavior_hashes),
        "behavior_hashes_distinct": hashes_distinct,
        "maximum_pairwise_visit_jaccard": threshold,
        "pairwise_visit_comparisons": comparisons,
        "evolutionary_runtime_mutation_receipts": evolution_pass,
    }


def _parse_json_cell(value: str) -> Any:
    return json.loads(value) if value else []


def _read_ledger(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for raw in csv.DictReader(handle):
            row: dict[str, Any] = dict(raw)
            for name in (
                "step",
                "seed",
                "proposal_ordinal",
                "proposal_sequence",
                "authorization_started_sequence",
                "authorized_sequence",
                "cache_lookup_sequence",
                "first_evaluation_sequence",
                "feedback_sequence",
                "policy_update_sequence",
                "feedback_available_after_step",
            ):
                if row.get(name):
                    row[name] = int(row[name])
            for name in (
                "feedback_blocked",
                "feedback_feasible",
                "cache_hit",
                "first_visit",
                "first_evaluation",
                "evaluation_executed",
                "strict_evaluator_call_confirmed",
                "numeric_alias_detected",
                "numeric_alias_cache_hit",
            ):
                row[name] = str(row.get(name, "")).lower() == "true"
            row["structural_genome"] = _parse_json_cell(row["structural_genome"])
            row["feedback_distance"] = float(row["feedback_distance"])
            row["feedback_sort_key"] = _parse_json_cell(row["feedback_sort_key"])
            row["feedback_violations"] = _parse_json_cell(row["feedback_violations"])
            rows.append(row)
    return rows


def replay_all_lanes(
    grammar: FrozenGrammar, ledger: Sequence[Mapping[str, Any]]
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, int], list[Mapping[str, Any]]] = defaultdict(list)
    for row in ledger:
        grouped[(str(row["algorithm"]), int(row["seed"]))].append(row)
    return [
        replay_policy_transcript(
            grammar,
            algorithm=algorithm,
            seed=seed,
            ledger_rows=rows,
        )
        for (algorithm, seed), rows in sorted(grouped.items(), key=lambda item: (item[0][1], item[0][0]))
    ]


def _event_order_pass(row: Mapping[str, Any]) -> bool:
    ordered = [
        int(row["proposal_sequence"]),
        int(row["authorization_started_sequence"]),
        int(row["authorized_sequence"]),
        int(row["cache_lookup_sequence"]),
    ]
    evaluation = row.get("evaluation_sequence")
    if evaluation not in (None, ""):
        ordered.append(int(evaluation))
    ordered.extend((int(row["feedback_sequence"]), int(row["policy_update_sequence"])))
    return all(left < right for left, right in zip(ordered, ordered[1:]))


def _ledger_contract_pass(ledger: Sequence[Mapping[str, Any]]) -> bool:
    required = {
        "proposal_id",
        "structural_genome",
        "first_visit",
        "evaluation_executed",
        "strict_evaluator_call_confirmed",
        "feedback_available_after_step",
        "policy_state_hash_before",
        "policy_state_hash_after",
    }
    proposal_ids: set[str] = set()
    for row in ledger:
        if not required.issubset(row) or not str(row["proposal_id"]):
            return False
        proposal_ids.add(str(row["proposal_id"]))
        try:
            genome = CandidateGenome(**{
                key: value
                for key, value in dict(row["structural_genome"]).items()
                if key != "schema_version"
            })
        except (TypeError, ValueError):
            return False
        first = bool(row["first_evaluation"])
        if not (
            genome.candidate_id == row["candidate_id"]
            and bool(row["first_visit"]) == first
            and bool(row["evaluation_executed"]) == first
            and (not first or bool(row["strict_evaluator_call_confirmed"]))
            and (row.get("evaluation_sequence") not in (None, "")) == first
            and int(row["feedback_available_after_step"]) == int(row["step"])
            and row["policy_state_hash_before"]
            == row["policy_state_before_proposal"]
            and row["policy_state_hash_after"] == row["policy_state_after_update"]
        ):
            return False
    return len(proposal_ids) == len(ledger)


def _numeric_alias_integrity(
    ledger: Sequence[Mapping[str, Any]], result: Mapping[str, Any]
) -> bool:
    first_rows = [row for row in ledger if bool(row.get("first_evaluation"))]
    groups: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in first_rows:
        key = str(row.get("numeric_evaluation_key", ""))
        if not key:
            return False
        groups[key].append(row)
    comparable = (
        "weight_array_sha256",
        "feasible_array_sha256",
        "mapping_diagnostics_sha256",
        "mapping_id",
        "mapping_contract_sha256",
        "target_horizon_hours",
        "evaluation_error",
        "observations",
        "strict_metrics_finite",
        *FEASIBILITY_ORDER,
        "gross_proxy",
        "gross_mean",
        "net_mean",
        "net_standard_error",
        "net_lcb",
        "increment_lcb",
        "execution_model_id",
        "overlapping_sleeves",
        "total_turnover_l1",
        "total_cost",
        "block_metrics",
        "feedback_blocked",
        "feedback_feasible",
        "feedback_violations",
        "feedback_distance",
        "feedback_sort_key",
        "feedback_reason",
    )
    alias_observations = 0
    for rows in groups.values():
        first_candidate_id = str(rows[0]["candidate_id"])
        if bool(rows[0].get("numeric_alias_detected")):
            return False
        representative = rows[0]
        for index, row in enumerate(rows):
            if (
                not bool(row.get("evaluation_executed"))
                or not bool(row.get("strict_evaluator_call_confirmed"))
                or bool(row.get("numeric_alias_cache_hit"))
                or bool(row.get("numeric_alias_detected")) != (index > 0)
                or str(row.get("numeric_alias_group_first_candidate_id"))
                != first_candidate_id
                or any(
                    not _evidence_values_equal(
                        row.get(name), representative.get(name)
                    )
                    for name in comparable
                )
            ):
                return False
        alias_observations += len(rows) - 1
    search = result.get("search", {})
    return bool(
        len(first_rows) == int(search.get("first_evaluations", -1))
        and len(first_rows) == int(search.get("strict_evaluator_calls", -1))
        and len(groups) == int(search.get("numeric_unique_inputs", -1))
        and alias_observations
        == int(search.get("numeric_alias_observations", -1))
        and int(search.get("exact_numeric_alias_savings", -1)) == 0
        and len(groups) + alias_observations == len(first_rows)
    )


def _exposure_rows(ledger: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[Any, ...], Counter[str]] = defaultdict(Counter)
    for row in ledger:
        key = (
            row.get("field_id"),
            row.get("representation_id"),
            row.get("primitive_id"),
            row.get("mechanism_family"),
            row.get("mapping_id"),
            row.get("target_horizon_hours"),
        )
        groups[key]["proposals"] += 1
        groups[key]["first_evaluations"] += int(bool(row.get("first_evaluation")))
        groups[key]["cache_hits"] += int(bool(row.get("cache_hit")))
    return [
        {
            "field_id": key[0],
            "representation_id": key[1],
            "primitive_id": key[2],
            "mechanism_family": key[3],
            "mapping_id": key[4],
            "target_horizon_hours": key[5],
            **dict(counts),
        }
        for key, counts in sorted(groups.items(), key=lambda item: tuple(str(v) for v in item[0]))
    ]


def _visit_rows(ledger: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[Any, ...], Counter[str]] = defaultdict(Counter)
    for row in ledger:
        key = (
            row["seed"],
            row["algorithm"],
            row.get("mechanism_family"),
            row.get("primitive_id"),
        )
        groups[key]["visits"] += 1
        groups[key]["unique_candidates"] += 0
        groups[key]["first_evaluations"] += int(bool(row.get("first_evaluation")))
    unique: dict[tuple[Any, ...], set[str]] = defaultdict(set)
    for row in ledger:
        unique[(row["seed"], row["algorithm"], row.get("mechanism_family"), row.get("primitive_id"))].add(str(row["candidate_id"]))
    rows: list[dict[str, Any]] = []
    for key, counts in sorted(groups.items(), key=lambda item: tuple(str(v) for v in item[0])):
        rows.append(
            {
                "seed": key[0],
                "algorithm": key[1],
                "mechanism_family": key[2],
                "primitive_id": key[3],
                "visits": counts["visits"],
                "unique_candidates": len(unique[key]),
                "first_evaluations": counts["first_evaluations"],
            }
        )
    return rows


def _feedback_rows(ledger: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in ledger:
        passed, recomputed = _feedback_alignment(row)
        rows.append({
            "candidate_id": row["candidate_id"],
            "seed": row["seed"],
            "algorithm": row["algorithm"],
            "first_evaluation": row["first_evaluation"],
            "cache_hit": row["cache_hit"],
            "blocked": row["feedback_blocked"],
            "feasible": row["feedback_feasible"],
            "distance": row["feedback_distance"],
            "sort_key": row["feedback_sort_key"],
            "reason": row["feedback_reason"],
            "violations": row["feedback_violations"],
            **{name: row.get(name) for name in FEASIBILITY_ORDER},
            "gross_proxy_diagnostic_only": row.get("gross_proxy"),
            "alignment_rule": "EXACT_SAME_VISITED_CANDIDATE_STRICT_DECISION",
            "alignment_pass": passed,
            **recomputed,
        })
    return rows


def _cost_rows(ledger: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    names = (
        "candidate_id",
        "seed",
        "algorithm",
        "mapping_id",
        "target_horizon_hours",
        "execution_model_id",
        "overlapping_sleeves",
        "gross_mean",
        "net_mean",
        "net_lcb",
        "turnover",
        "cost",
        "initial_establishment_l1",
        "subsequent_entry_l1",
        "rebalance_l1",
        "transition_exit_l1",
        "terminal_liquidation_l1",
        "total_turnover_l1",
        "total_cost",
        "concentration",
        "support",
    )
    return [{name: row.get(name) for name in names} for row in ledger if row.get("first_evaluation")]


def _report_text(result: Mapping[str, Any]) -> str:
    return f"""# Crypto Real-Data Instrument Canary

Status: `{result['status']}`

This is an execution-instrument qualification on the approved 2024 development-train-only release. It is not Alpha, OOS proof, candidate promotion, or authorization to open any sealed role.

## Frozen execution

- Grammar support: {result['grammar']['support_size']:,} structural candidates.
- Formal proposals: {result['search']['proposals']:,} across four algorithms and two seeds.
- First evaluations: {result['search']['first_evaluations']:,}; cache hits: {result['search']['cache_hits']:,}.
- Exact-candidate cache hits and numeric aliases are separate: {result['search']['cache_hits']:,} exact-candidate cache hits skipped evaluation; {result['search']['numeric_alias_observations']:,} distinct-candidate numeric aliases were each strictly re-evaluated and saved 0 strict calls.
- Strict evaluator calls: {result['search']['strict_evaluator_calls']:,}, exactly one per first evaluation.
- Cost preflight first evaluations: {result['search']['preflight_first_evaluations']:,}.
- Target: feature bucket t, observable t+1h, execute t+2h; horizons 1h and 4h.
- 4h execution: four equal-capital offset sleeves, each rebalanced every four hours.
- Cost: full-L1 fixed 5 bps with initial establishment and terminal liquidation.

## Qualification

- Event order: {result['checks']['event_order']}.
- Policy transcript replay: {result['checks']['policy_replay']}.
- Unvisited candidates with metrics or feedback: {result['search']['unvisited_metrics_or_feedback']}.
- Sealed-role reads: {result['boundaries']['sealed_reads']}.
- Development-only feasible strict-feedback visits: {result['economic_observation']['feasible_visits']} (instrument diagnostic only).

## Scope

All six calendar blocks are development-train feedback blocks, not OOS blocks. Ordinary LCBs do not correct serial dependence or multiple testing. No validation, holdout, challenge, recent, forward, May stress, 2026 data, promotion, or cross-sprint memory was opened.
"""


def _artifact_manifest_payload(
    repo_root: Path,
    *,
    runtime_root: Path,
    report_path: Path,
    source_sha: str,
    source_blobs: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    artifact_paths = sorted(
        [path for path in runtime_root.iterdir() if path.is_file()]
        + [report_path]
    )
    artifact_rows = [
        {
            "path": path.relative_to(repo_root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in artifact_paths
        if path.name != "CRYPTO_CANARY_ARTIFACT_MANIFEST.json"
    ]
    return {
        "schema_version": 1,
        "source_code_sha": source_sha,
        "artifacts": artifact_rows,
        "source_blobs": list(source_blobs),
        "bundle_sha256": _payload_sha256(artifact_rows),
    }


def _persisted_receipt_valid(row: Mapping[str, Any], *, source_sha: str) -> bool:
    try:
        payload = dict(row)
        receipt_sha = str(payload.pop("receipt_sha256"))
        genome_payload = dict(payload["genome"])
        genome_payload.pop("schema_version", None)
        genome = CandidateGenome(**genome_payload)
        contracts = dict(payload["contracts"])
        release = dict(payload["release"])
        target = dict(payload["target"])
        expected_cache = _payload_sha256(
            {
                "candidate_id": payload["candidate_id"],
                "release_view_sha256": release["development_view_sha256"],
                "source_code_sha": payload["source_code_sha"],
                "contracts": {
                    "grammar": contracts["grammar_sha256"],
                    "representation": contracts["representation_sha256"],
                    "primitive": contracts["primitive_sha256"],
                    "mapping": contracts["mapping_sha256"],
                    "target": contracts["target_sha256"],
                    "pit_lag": contracts["pit_lag_sha256"],
                    "cost": contracts["cost_sha256"],
                    "feedback": contracts["feedback_sha256"],
                    "authorization": contracts["authorization_sha256"],
                },
            }
        )
        return bool(
            payload["candidate_id"] == genome.candidate_id
            and payload["source_code_sha"] == source_sha
            and receipt_sha == _payload_sha256(payload)
            and payload["cache_key"] == expected_cache
            and contracts["target_sha256"]
            == _payload_sha256(target["contract"])
            and contracts["pit_lag_sha256"]
            == _payload_sha256(payload["pit_lag_contract"])
            and contracts["cost_sha256"] == _payload_sha256(payload["cost_contract"])
            and contracts["feedback_sha256"]
            == _payload_sha256(payload["feedback_contract"])
        )
    except (KeyError, TypeError, ValueError):
        return False


def _domain_bundle_integrity_errors(
    repo_root: Path,
    *,
    runtime_root: Path,
    allowed_statuses: set[str],
    require_head_equal: bool,
) -> tuple[list[str], dict[str, Any]]:
    """Independently verify the domain bundle before Graph can change status."""

    errors: list[str] = []
    manifest_path = runtime_root / "CRYPTO_CANARY_ARTIFACT_MANIFEST.json"
    result_path = runtime_root / REQUIRED_OUTPUTS[7]
    contract_path = runtime_root / REQUIRED_OUTPUTS[0]
    try:
        manifest = _read_config(manifest_path)
        result = _read_config(result_path)
        contract = _read_config(contract_path)
    except (FileNotFoundError, json.JSONDecodeError, TypeError, ValueError):
        return ["domain_bundle_header"], {}
    source_sha = str(manifest.get("source_code_sha", "")).lower()
    if not source_sha:
        errors.append("source_sha_missing")
    elif require_head_equal and _git_sha(repo_root).lower() != source_sha:
        errors.append("source_sha_not_head")
    elif not require_head_equal:
        try:
            subprocess.check_call(
                ["git", "merge-base", "--is-ancestor", source_sha, "HEAD"],
                cwd=repo_root,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except (subprocess.CalledProcessError, OSError):
            errors.append("source_sha_not_ancestor")
    if not (
        source_sha
        == str(result.get("source_code_sha", "")).lower()
        == str(contract.get("source_code_sha", "")).lower()
    ):
        errors.append("source_sha_cross_artifact")
    if result.get("status") not in allowed_statuses:
        errors.append("domain_status")
    checks = result.get("checks", {})
    if set(checks) != DOMAIN_CHECK_NAMES or any(
        value != "PASS" for value in checks.values()
    ):
        errors.append("domain_checks")
    try:
        observed_source_blobs = _source_blob_rows(repo_root, source_sha)
    except (
        ValueError,
        RuntimeError,
        FileNotFoundError,
        subprocess.CalledProcessError,
    ):
        observed_source_blobs = []
        errors.append("source_blob_verification")
    if observed_source_blobs != manifest.get("source_blobs"):
        errors.append("source_blob_manifest")
    observed_rows: list[dict[str, Any]] = []
    expected_artifact_paths = sorted(
        [
            path.relative_to(repo_root).as_posix()
            for path in runtime_root.iterdir()
            if path.is_file()
            and path.name != "CRYPTO_CANARY_ARTIFACT_MANIFEST.json"
        ]
        + [str(contract.get("config", {}).get("outputs", {}).get("report", ""))]
    )
    declared_artifact_paths = [
        str(record.get("path", "")) for record in manifest.get("artifacts", [])
    ]
    if declared_artifact_paths != expected_artifact_paths:
        errors.append("artifact_set")
    for record in manifest.get("artifacts", []):
        path = (repo_root / str(record.get("path", ""))).resolve()
        try:
            path.relative_to(repo_root.resolve())
        except ValueError:
            errors.append(f"artifact_outside_repository:{record.get('path')}")
            continue
        if not path.is_file():
            errors.append(f"missing:{record.get('path')}")
            continue
        observed = {
            "path": str(record["path"]),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        observed_rows.append(observed)
        if observed != record:
            errors.append(f"hash_or_size:{record['path']}")
    if _payload_sha256(observed_rows) != manifest.get("bundle_sha256"):
        errors.append("bundle_sha256")
    for name in REQUIRED_OUTPUTS:
        if not (runtime_root / name).is_file():
            errors.append(f"required_output:{name}")
    ledger_path = runtime_root / REQUIRED_OUTPUTS[2]
    try:
        ledger = _read_ledger(ledger_path)
        replays = replay_all_lanes(FrozenGrammar.default(), ledger)
    except (OSError, ValueError, KeyError, json.JSONDecodeError):
        ledger = []
        replays = []
    if len(replays) != 8 or any(row.get("result") != "PASS" for row in replays):
        errors.append("policy_replay")
    if not ledger or not _ledger_contract_pass(ledger):
        errors.append("ledger_contract")
    if ledger and not _numeric_alias_integrity(ledger, result):
        errors.append("numeric_alias_integrity")
    receipts_path = runtime_root / "CRYPTO_CANDIDATE_AUTHORIZATION_RECEIPTS.jsonl"
    receipt_rows: list[dict[str, Any]] = []
    try:
        receipt_rows = [
            json.loads(line)
            for line in receipts_path.read_text(encoding="utf-8").splitlines()
            if line
        ]
    except (OSError, json.JSONDecodeError):
        errors.append("receipt_file")
    if receipt_rows:
        receipt_by_cache = {
            str(row.get("cache_key")): row for row in receipt_rows
        }
        first_cache_order = [
            str(row.get("cache_key"))
            for row in ledger
            if bool(row.get("first_evaluation"))
        ]
        if list(receipt_by_cache) != first_cache_order:
            errors.append("receipt_ledger_identity")
        for row in ledger:
            receipt = receipt_by_cache.get(str(row.get("cache_key")), {})
            if not (
                receipt.get("candidate_id") == row.get("candidate_id")
                and receipt.get("receipt_sha256") == row.get("receipt_sha256")
            ):
                errors.append("receipt_cache_identity")
                break
        if any(
            not _persisted_receipt_valid(row, source_sha=source_sha)
            for row in receipt_rows
        ):
            errors.append("receipt_identity")
    elif ledger:
        errors.append("receipt_rows_empty")
    return errors, {
        "source_sha": source_sha,
        "manifest": manifest,
        "result": result,
        "contract": contract,
        "artifact_count": len(observed_rows),
        "replays": replays,
    }


def _graph_assurance_errors(
    repo_root: Path,
    *,
    source_sha: str,
    trace_path: Path,
) -> list[str]:
    errors: list[str] = []
    repo_root = repo_root.resolve()
    trace_path = trace_path.resolve()
    try:
        trace_ref = trace_path.relative_to(repo_root).as_posix()
    except ValueError:
        return ["runtime_trace_outside_repository"]
    current_path = repo_root / ".planning" / "graphs" / "current.json"
    profile_path = repo_root / "profiles" / f"{GRAPH_PROFILE_ID}.json"
    if not current_path.is_file() or not trace_path.is_file() or not profile_path.is_file():
        return ["graph_assurance_files_missing"]
    current = _read_config(current_path)
    trace = _read_config(trace_path)
    profile = _read_config(profile_path)
    summary = current.get("summary", {})
    if not (
        current.get("status") == "PASS"
        and current.get("strict_mode") is True
        and current.get("strict_ready") is True
        and current.get("profile_id") == GRAPH_PROFILE_ID
        and current.get("repo_head") == source_sha
        and current.get("trace", {}).get("repo_sha") == source_sha
        and current.get("trace", {}).get("path") == trace_ref
        and summary.get("errors") == 0
        and summary.get("warnings") == 0
        and summary.get("runtime_nodes") == 8
        and summary.get("runtime_edges") == 7
        and summary.get("current_nodes") == 16
        and summary.get("current_edges") == 15
    ):
        errors.append("strict_current_summary")
    if not (
        trace.get("status") == "COMPLETED"
        and trace.get("repo_sha") == source_sha
        and trace.get("profile_id") == GRAPH_PROFILE_ID
        and not trace.get("errors")
    ):
        errors.append("runtime_trace_header")
    tracer_authority = trace.get("tracer_authority", {})
    tracer_path = Path(str(tracer_authority.get("runtime_trace_path", "")))
    skill_path = Path(str(tracer_authority.get("skill_path", "")))
    if not (
        tracer_path.is_file()
        and skill_path.is_file()
        and tracer_path.name == "runtime_trace.py"
        and tracer_path.parent.name == "scripts"
        and tracer_path.parent.parent == skill_path.parent
        and tracer_authority.get("runtime_trace_sha256") == sha256_file(tracer_path)
        and tracer_authority.get("skill_sha256") == sha256_file(skill_path)
    ):
        errors.append("runtime_tracer_authority")
    required_components = set(profile.get("required_components", ()))
    observed_components = {
        row.get("component_id") for row in trace.get("observed_components", ())
    }
    if observed_components != required_components:
        errors.append("runtime_trace_components")
    required_edges = {
        (row["source"], row["target"], row["relation"])
        for row in profile.get("required_edges", ())
    }
    observed_edges = {
        (row.get("source"), row.get("target"), row.get("relationship"))
        for row in trace.get("observed_edges", ())
    }
    if observed_edges != required_edges:
        errors.append("runtime_trace_edges")
    if any(not row.get("evidence") for row in trace.get("observed_edges", ())):
        errors.append("runtime_trace_edge_evidence")
    try:
        canary_config = _read_config(
            repo_root / "config" / "crypto_real_data_instrument_canary_v1.json"
        )
        runtime_root = repo_root / canary_config["outputs"]["runtime_root"]
        ledger_candidate_ids = {
            str(row["candidate_id"])
            for row in _read_ledger(runtime_root / REQUIRED_OUTPUTS[2])
        }
        release_manifest = _read_config(runtime_root / REQUIRED_OUTPUTS[1])
    except (OSError, KeyError, ValueError, json.JSONDecodeError):
        ledger_candidate_ids = set()
        release_manifest = {}
        errors.append("runtime_trace_evidence_inputs")
    candidate_relations = {
        "authorizes_first_visit_candidate",
        "executes_canonical_primitive",
        "applies_explicit_mapping",
        "evaluates_mapped_turnover_cost",
        "consumes_aligned_visited_feedback",
    }
    for row in trace.get("observed_edges", ()):
        relationship = row.get("relationship")
        evidence = row.get("evidence", {})
        if relationship in candidate_relations and str(
            evidence.get("candidate_id", "")
        ) not in ledger_candidate_ids:
            errors.append(f"runtime_edge_candidate:{relationship}")
        if relationship == "loads_approved_development_release" and evidence.get(
            "release_id"
        ) != release_manifest.get("release_id"):
            errors.append("runtime_edge_release")
        if relationship == "enforces_sealed_boundaries" and evidence.get(
            "contract_result"
        ) != "PASS":
            errors.append("runtime_edge_boundary")
    bindings = trace.get("contract_bindings", {})
    if set(bindings) != GRAPH_CONTRACT_IDS:
        errors.append("runtime_trace_contract_bindings")
    for contract_id, row in bindings.items():
        binding_path = repo_root / str(row.get("path", ""))
        if (
            row.get("contract_id") != contract_id
            or not binding_path.is_file()
            or row.get("sha256") != sha256_file(binding_path)
        ):
            errors.append(f"runtime_contract_binding:{contract_id}")
    for component in trace.get("observed_components", ()):
        implementation_path = repo_root / str(component.get("implementation_path", ""))
        if (
            not implementation_path.is_file()
            or component.get("implementation_sha256") != sha256_file(implementation_path)
            or not component.get("function")
        ):
            errors.append(f"runtime_component_identity:{component.get('component_id')}")
    approved_fields = {field.field_id for field in FrozenGrammar.default().field_specs}
    loaded_fields = trace.get("loaded_fields", ())
    if not loaded_fields or any(
        row.get("field_id") not in approved_fields
        or row.get("consumer_component") != "real_data_lazy_search_canary"
        for row in loaded_fields
    ):
        errors.append("runtime_loaded_fields")
    for artifact in trace.get("artifacts", ()):
        artifact_path = repo_root / str(artifact.get("path", ""))
        if (
            not artifact_path.is_file()
            or artifact.get("sha256") != sha256_file(artifact_path)
            or artifact.get("producer_component") != "real_data_lazy_search_canary"
        ):
            errors.append(f"runtime_artifact:{artifact.get('path')}")
    current_nodes = {row["id"]: row for row in current.get("nodes", ())}
    expected_lifecycle = {
        "real_data_lazy_search_canary": "EXPERIMENTAL",
        "approved_existing_development_release": "ACTIVE",
        "real_data_candidate_authorization": "EXPERIMENTAL",
        "canonical_primitive_authority": "ACTIVE",
        "explicit_portfolio_mapping": "ACTIVE",
        "real_data_mapping_cost_evaluator": "EXPERIMENTAL",
        "adaptive_strict_feasibility_feedback": "ACTIVE",
        "sealed_research_boundaries": "FORBIDDEN",
        "internal_search_instrument": "EXPERIMENTAL",
        "formal_performance_search": "FORBIDDEN",
        "new_data_integration": "FORBIDDEN",
    }
    for component_id, expected in expected_lifecycle.items():
        if current_nodes.get(component_id, {}).get("lifecycle") != expected:
            errors.append(f"lifecycle:{component_id}")
    for component_id in required_components:
        node = current_nodes.get(component_id, {})
        validation = node.get("validation", {})
        expected_level = (
            "RUNTIME_ENFORCED"
            if component_id
            in {
                "real_data_candidate_authorization",
                "real_data_mapping_cost_evaluator",
                "sealed_research_boundaries",
            }
            else "RUNTIME_VERIFIED"
        )
        if not (
            node.get("evidence") == "RUNTIME"
            and validation.get("result") == "PASS"
            and validation.get("level") == expected_level
            and validation.get("profile") == GRAPH_PROFILE_ID
            and validation.get("verified_at_sha") == source_sha
        ):
            errors.append(f"runtime_node:{component_id}")
    current_edges = {
        (row["source"], row["target"], row["relation"]): row
        for row in current.get("edges", ())
    }
    for key in required_edges:
        edge = current_edges.get(key, {})
        validation = edge.get("validation", {})
        expected_level = (
            "RUNTIME_ENFORCED"
            if key[2]
            in {
                "authorizes_first_visit_candidate",
                "evaluates_mapped_turnover_cost",
                "enforces_sealed_boundaries",
            }
            else "RUNTIME_VERIFIED"
        )
        if not (
            edge.get("evidence") == "RUNTIME"
            and edge.get("line_style") == "solid"
            and validation.get("result") == "PASS"
            and validation.get("level") == expected_level
            and validation.get("profile") == GRAPH_PROFILE_ID
        ):
            errors.append("runtime_edge:" + "|".join(key))
    if any(check.get("code") == "FORBIDDEN_RUNTIME_EDGE" for check in current.get("checks", ())):
        errors.append("forbidden_runtime_edge")
    return errors


def finalize_graph_qualification(
    repo_root: Path,
    *,
    config_path: Path,
    trace_path: Path,
) -> dict[str, Any]:
    config = _read_config(config_path)
    runtime_root = repo_root / config["outputs"]["runtime_root"]
    report_path = repo_root / config["outputs"]["report"]
    result_path = runtime_root / REQUIRED_OUTPUTS[7]
    result = _read_config(result_path)
    source_sha = str(result["source_code_sha"])
    if result.get("status") != PARTIAL:
        raise ValueError("domain result is not eligible for Graph qualification")
    domain_errors, _ = _domain_bundle_integrity_errors(
        repo_root,
        runtime_root=runtime_root,
        allowed_statuses={PARTIAL},
        require_head_equal=True,
    )
    if domain_errors:
        raise ValueError("domain bundle verification failed: " + ";".join(domain_errors))
    errors = _graph_assurance_errors(
        repo_root, source_sha=source_sha, trace_path=trace_path
    )
    if errors:
        raise ValueError("Graph assurance failed: " + ";".join(errors))
    current_path = repo_root / ".planning" / "graphs" / "current.json"
    current = _read_config(current_path)
    lifecycle_by_id = {
        row["id"]: row.get("lifecycle") for row in current.get("nodes", ())
    }
    lifecycle_promotions = sum(
        lifecycle_by_id.get(component_id) == "ACTIVE"
        for component_id in (
            "real_data_lazy_search_canary",
            "internal_search_instrument",
        )
    )
    sealed_boundaries_opened = sum(
        lifecycle_by_id.get(component_id) != "FORBIDDEN"
        for component_id in (
            "formal_performance_search",
            "new_data_integration",
            "sealed_research_boundaries",
        )
    )
    qualification = {
        "schema_version": 1,
        "result": "PASS",
        "profile_id": GRAPH_PROFILE_ID,
        "source_code_sha": source_sha,
        "trace_path": trace_path.relative_to(repo_root).as_posix(),
        "trace_sha256": sha256_file(trace_path),
        "current_path": current_path.relative_to(repo_root).as_posix(),
        "current_sha256": sha256_file(current_path),
        "runtime_nodes": 8,
        "runtime_edges": 7,
        "lifecycle_promotions": lifecycle_promotions,
        "sealed_boundaries_opened": sealed_boundaries_opened,
    }
    _write_json(
        runtime_root / "CRYPTO_GRAPH_STRICT_QUALIFICATION.json", qualification
    )
    result["status"] = QUALIFIED
    result["graph_assurance"] = {
        "runtime_trace": "PASS",
        "strict_current_profile": "PASS",
        "profile_id": GRAPH_PROFILE_ID,
        "qualification_ref": "runtime/crypto_real_data_instrument_canary_20260715/CRYPTO_GRAPH_STRICT_QUALIFICATION.json",
        "required_before_execution_qualified": True,
    }
    _write_json(result_path, result)
    report_path.write_text(_report_text(result), encoding="utf-8")
    prior_manifest = _read_config(
        runtime_root / "CRYPTO_CANARY_ARTIFACT_MANIFEST.json"
    )
    manifest = _artifact_manifest_payload(
        repo_root,
        runtime_root=runtime_root,
        report_path=report_path,
        source_sha=source_sha,
        source_blobs=prior_manifest["source_blobs"],
    )
    _write_json(runtime_root / "CRYPTO_CANARY_ARTIFACT_MANIFEST.json", manifest)
    return {
        "result": "PASS",
        "status": QUALIFIED,
        "graph_qualification": qualification,
        "bundle_sha256": manifest["bundle_sha256"],
    }


def build_evidence(
    repo_root: Path,
    *,
    config_path: Path,
    source_sha: str | None = None,
    runtime_trace: Any | None = None,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    _require_clean_source_tree(repo_root)
    config = _read_config(config_path)
    source_sha = (source_sha or _git_sha(repo_root)).lower()
    if source_sha != _git_sha(repo_root).lower():
        raise ValueError("source SHA must equal current HEAD")
    planned_runtime_root = repo_root / config["outputs"]["runtime_root"]
    planned_report_path = repo_root / config["outputs"]["report"]
    if planned_runtime_root.exists() and any(planned_runtime_root.iterdir()):
        raise RuntimeError("formal runtime root is not empty; refusing mixed-run evidence")
    if planned_report_path.exists():
        raise RuntimeError("formal report path already exists; refusing evidence overwrite")
    grammar = FrozenGrammar.default()
    contract_check = validate_frozen_canary_contract(config, grammar)
    source_blobs = _source_blob_rows(repo_root, source_sha)
    if runtime_trace is not None:
        runtime_trace.observe_component(
            "real_data_lazy_search_canary",
            implementation_path="alphafactory_crypto/instrument_canary/runner.py",
            function="build_evidence",
            semantic_role="bounded_real_data_lazy_search",
            evidence_produced=True,
        )
        runtime_trace.observe_component(
            "sealed_research_boundaries",
            implementation_path="alphafactory_crypto/instrument_canary/runner.py",
            function="validate_frozen_canary_contract",
            semantic_role="evaluation_access_boundary",
            evidence_produced=True,
        )
        runtime_trace.observe_edge(
            "real_data_lazy_search_canary",
            "sealed_research_boundaries",
            edge_type="RUNTIME_CALL",
            relationship="enforces_sealed_boundaries",
            evidence={"contract_result": contract_check["result"]},
        )

    process = psutil.Process(os.getpid())
    load_rss_before = process.memory_info().rss
    load_started = time.perf_counter()
    panel = load_development_release(config)
    if runtime_trace is not None:
        runtime_trace.observe_component(
            "approved_existing_development_release",
            implementation_path="alphafactory_crypto/instrument_canary/release.py",
            function="load_development_release",
            semantic_role="development_release_authority",
            evidence_produced=True,
        )
        runtime_trace.observe_edge(
            "real_data_lazy_search_canary",
            "approved_existing_development_release",
            edge_type="RUNTIME_CALL",
            relationship="loads_approved_development_release",
            evidence={"release_id": panel.release_id},
        )
    release_load_seconds = time.perf_counter() - load_started
    release_load_rss_delta = process.memory_info().rss - load_rss_before
    preflight = run_cost_preflight(
        panel,
        grammar=grammar,
        config=config,
        source_sha=source_sha,
        release_load_seconds=release_load_seconds,
        release_load_rss_delta_bytes=release_load_rss_delta,
    )
    if preflight.payload["resource_admission"]["result"] != "PASS":
        raise RuntimeError("cost preflight failed frozen resource admission")

    numeric_evaluator = RealDataFirstVisitEvaluator(
        panel, runtime_trace=runtime_trace
    )

    def authorize_first_visit(proposal: Any) -> CandidateAuthorizationReceipt:
        receipt = _authorize(
            proposal.genome,
            grammar=grammar,
            panel=panel,
            config=config,
            source_sha=source_sha,
        )
        if runtime_trace is not None:
            runtime_trace.observe_component(
                "real_data_candidate_authorization",
                implementation_path="alphafactory_crypto/instrument_canary/admission.py",
                function="authorize_candidate",
                semantic_role="candidate_admission",
                evidence_produced=True,
            )
            runtime_trace.observe_edge(
                "real_data_lazy_search_canary",
                "real_data_candidate_authorization",
                edge_type="RUNTIME_CALL",
                relationship="authorizes_first_visit_candidate",
                evidence={"candidate_id": receipt.candidate_id},
            )
        return receipt

    engine = LazySearchEngine(
        grammar,
        authorizer=authorize_first_visit,
        first_visit_evaluator=numeric_evaluator,
        first_evaluation_hard_cap=int(config["budget"]["total_first_evaluation_hard_cap"]),
        already_consumed_first_evaluations=(
            int(config["budget"]["cost_preflight_evaluations"])
            + int(
                config["budget"]["superseded_development_preflight_evaluations"]
            )
        ),
    )
    search = engine.run(
        algorithms=config["budget"]["algorithms"],
        seeds=config["budget"]["seeds"],
        steps_per_lane=int(config["budget"]["proposal_steps_per_seed_algorithm"]),
    )
    ledger = list(search.ledger)
    replays = replay_all_lanes(grammar, ledger)
    strict_audit = _strict_feedback_audit(
        ledger,
        config,
        panel=panel,
        grammar=grammar,
        source_sha=source_sha,
    )
    decoy_audit = _admission_decoy_audit(
        panel,
        grammar=grammar,
        config=config,
        source_sha=source_sha,
    )
    behavior_audit = _algorithm_behavior_audit(
        ledger, search.behavior_hashes, config
    )

    sets_by_algorithm_seed: dict[str, dict[int, set[str]]] = defaultdict(dict)
    for algorithm in config["budget"]["algorithms"]:
        for seed in config["budget"]["seeds"]:
            sets_by_algorithm_seed[algorithm][int(seed)] = {
                str(row["candidate_id"])
                for row in ledger
                if row["algorithm"] == algorithm and int(row["seed"]) == int(seed)
            }
    different_seed_regions = all(
        len({frozenset(values) for values in seed_sets.values()}) == len(seed_sets)
        for seed_sets in sets_by_algorithm_seed.values()
    )
    event_order = all(_event_order_pass(row) for row in ledger)
    replay_pass = len(replays) == 8 and all(row["result"] == "PASS" for row in replays)
    unique_visited = {str(row["candidate_id"]) for row in ledger}
    total_first = (
        search.first_evaluations
        + int(config["budget"]["cost_preflight_evaluations"])
        + int(config["budget"]["superseded_development_preflight_evaluations"])
    )
    checks = {
        "contract": contract_check["result"],
        "event_order": "PASS" if event_order else "FAIL",
        "ledger_contract": "PASS" if _ledger_contract_pass(ledger) else "FAIL",
        "policy_replay": "PASS" if replay_pass else "FAIL",
        "different_seed_regions": "PASS" if different_seed_regions else "FAIL",
        "first_evaluation_cap": (
            "PASS"
            if total_first <= int(config["budget"]["total_first_evaluation_hard_cap"])
            else "FAIL"
        ),
        "all_feedback_is_visited": (
            "PASS"
            if len([event for event in search.events if event["event_type"] == "VISITED_FEEDBACK_EXPOSED"])
            == len(ledger)
            == search.proposals
            else "FAIL"
        ),
        "run_cache_exact": "PASS" if search.cache_size == search.first_evaluations else "FAIL",
        "strict_evaluator_every_first_visit": (
            "PASS"
            if numeric_evaluator.strict_evaluator_calls == search.first_evaluations
            else "FAIL"
        ),
        "numeric_alias_integrity": (
            "PASS"
            if _numeric_alias_integrity(
                ledger,
                {
                    "search": {
                        "first_evaluations": search.first_evaluations,
                        "strict_evaluator_calls": numeric_evaluator.strict_evaluator_calls,
                        "numeric_unique_inputs": numeric_evaluator.numeric_unique_inputs,
                        "numeric_alias_observations": numeric_evaluator.numeric_alias_observations,
                        "exact_numeric_alias_savings": 0,
                    }
                },
            )
            else "FAIL"
        ),
        "sealed_reads_zero": "PASS" if panel.sealed_reads == 0 else "FAIL",
        "strict_feedback_alignment": strict_audit["result"],
        "admission_decoy_rejection": decoy_audit["result"],
        "algorithm_behavior_qualification": behavior_audit["result"],
    }
    all_pass = all(value == "PASS" for value in checks.values())
    status = PARTIAL if all_pass else MISMATCH
    result = {
        "schema_version": 1,
        "canary_id": config["canary_id"],
        "status": status,
        "source_code_sha": source_sha,
        "authorization": config["authorization"],
        "conclusion_scope": "EXECUTION_INSTRUMENT_ONLY_NOT_ECONOMIC_ALPHA",
        "grammar": {
            "support_size": grammar.support_size,
            "contract_sha256": grammar.contract_sha256,
            "full_universe_materialized": False,
        },
        "release": {
            "release_id": panel.release_id,
            "development_view_id": panel.development_view_id,
            "development_view_sha256": panel.release_manifest["development_view_sha256"],
            "assets": len(panel.assets),
            "timestamps": len(panel.timestamps),
            "months": list(panel.release_manifest["months"]),
        },
        "search": {
            "algorithms": list(config["budget"]["algorithms"]),
            "seeds": list(config["budget"]["seeds"]),
            "steps_per_lane": int(config["budget"]["proposal_steps_per_seed_algorithm"]),
            "proposals": search.proposals,
            "unique_visited_candidates": len(unique_visited),
            "first_evaluations": search.first_evaluations,
            "cache_hits": search.cache_hits,
            "cache_size": search.cache_size,
            "strict_evaluator_calls": numeric_evaluator.strict_evaluator_calls,
            "numeric_unique_inputs": numeric_evaluator.numeric_unique_inputs,
            "numeric_alias_observations": numeric_evaluator.numeric_alias_observations,
            "exact_numeric_alias_savings": 0,
            "preflight_first_evaluations": int(config["budget"]["cost_preflight_evaluations"]),
            "superseded_development_preflight_evaluations": int(
                config["budget"]["superseded_development_preflight_evaluations"]
            ),
            "total_first_evaluations": total_first,
            "hard_cap": int(config["budget"]["total_first_evaluation_hard_cap"]),
            "unvisited_structural_candidates": grammar.support_size - len(unique_visited),
            "unvisited_metrics_or_feedback": 0,
            "behavior_hashes": dict(search.behavior_hashes),
            "lane_state_hashes": dict(search.lane_state_hashes),
            "policy_replays": replays,
        },
        "checks": checks,
        "graph_assurance": {
            "runtime_trace": "PENDING",
            "strict_current_profile": "PENDING",
            "required_before_execution_qualified": True,
        },
        "boundaries": {
            "allowed_role": "DEVELOPMENT_TRAIN_ONLY",
            "sealed_roles": list(config["boundaries"]["sealed_roles"]),
            "sealed_reads": panel.sealed_reads,
            "challenge_path_enumerated": False,
            "promotion": False,
            "cross_sprint_memory": False,
            "new_data_integration": False,
        },
        "economic_observation": {
            "feasible_visits": sum(bool(row["feedback_feasible"]) for row in ledger),
            "blocked_visits": sum(bool(row["feedback_blocked"]) for row in ledger),
            "claim": "NONE; development-only adaptive instrument diagnostics",
            "ordinary_lcb_warning": "no serial-correlation or multiple-testing correction",
        },
        "cost_preflight": {key: value for key, value in preflight.payload.items() if key != "rows"},
    }

    runtime_root = repo_root / config["outputs"]["runtime_root"]
    report_path = repo_root / config["outputs"]["report"]
    runtime_root.mkdir(parents=True, exist_ok=True)
    contract_payload = {
        "schema_version": 1,
        "source_code_sha": source_sha,
        "config": config,
        "config_sha256": _payload_sha256(config),
        "grammar_contract_sha256": grammar.contract_sha256,
        "canonical_primitive_contract_sha256": _payload_sha256(primitive_contract_payload()),
        "canonical_mapping_contract_sha256": _payload_sha256(mapping_contract_payload()),
        "real_data_feedback_contract": _real_feedback_contract(),
        "contract_check": contract_check,
        "source_blobs": source_blobs,
    }
    _write_json(runtime_root / REQUIRED_OUTPUTS[0], contract_payload)
    _write_json(runtime_root / REQUIRED_OUTPUTS[1], dict(panel.release_manifest))
    _write_csv(runtime_root / REQUIRED_OUTPUTS[2], ledger)
    _write_csv(runtime_root / REQUIRED_OUTPUTS[3], _exposure_rows(ledger))
    _write_csv(runtime_root / REQUIRED_OUTPUTS[4], _visit_rows(ledger))
    _write_csv(runtime_root / REQUIRED_OUTPUTS[5], _feedback_rows(ledger))
    _write_csv(runtime_root / REQUIRED_OUTPUTS[6], _cost_rows(ledger))
    _write_json(runtime_root / REQUIRED_OUTPUTS[7], result)
    _write_json(runtime_root / "CRYPTO_REAL_DATA_COST_PREFLIGHT.json", preflight.payload)
    _write_json(runtime_root / "CRYPTO_REAL_DATA_RUNTIME_EVENT_LOG.json", list(search.events))
    _write_json(runtime_root / "CRYPTO_STRICT_FEEDBACK_AUDIT.json", strict_audit)
    _write_json(runtime_root / "CRYPTO_ADMISSION_DECOY_AUDIT.json", decoy_audit)
    _write_json(runtime_root / "CRYPTO_ALGORITHM_BEHAVIOR_AUDIT.json", behavior_audit)
    receipts_path = runtime_root / "CRYPTO_CANDIDATE_AUTHORIZATION_RECEIPTS.jsonl"
    receipts_path.write_text(
        "".join(
            json.dumps(_json_ready(receipt), sort_keys=True, separators=(",", ":")) + "\n"
            for receipt in search.authorization_receipts
        ),
        encoding="utf-8",
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_report_text(result), encoding="utf-8")

    manifest = _artifact_manifest_payload(
        repo_root,
        runtime_root=runtime_root,
        report_path=report_path,
        source_sha=source_sha,
        source_blobs=source_blobs,
    )
    _write_json(runtime_root / "CRYPTO_CANARY_ARTIFACT_MANIFEST.json", manifest)
    if runtime_trace is not None:
        config_ref = config_path.relative_to(repo_root).as_posix()
        release_ref = (runtime_root / REQUIRED_OUTPUTS[1]).relative_to(repo_root).as_posix()
        contract_ref = (runtime_root / REQUIRED_OUTPUTS[0]).relative_to(repo_root).as_posix()
        for contract_id in sorted(GRAPH_CONTRACT_IDS):
            if contract_id in {
                "sealed_evaluation_roles",
                "frozen_mutations",
                "explicit_boundary_authority",
                "canary_enforces_sealed_boundaries",
            }:
                binding_path = config_ref
            elif contract_id in {
                "approved_existing_release_only",
                "bounded_existing_release_canary_authority",
                "canary_loads_approved_development_release",
            }:
                binding_path = release_ref
            else:
                binding_path = contract_ref
            runtime_trace.bind_contract(
                contract_id, contract_id=contract_id, path=binding_path
            )
        mutable_after_graph = {
            REQUIRED_OUTPUTS[7],
            "CRYPTO_CANARY_ARTIFACT_MANIFEST.json",
        }
        for path in sorted(runtime_root.iterdir()):
            if path.is_file() and path.name not in mutable_after_graph:
                runtime_trace.record_artifact(
                    path.relative_to(repo_root).as_posix(),
                    producer_component="real_data_lazy_search_canary",
                )
    return result


def check_evidence(repo_root: Path, *, config_path: Path) -> dict[str, Any]:
    config = _read_config(config_path)
    runtime_root = repo_root / config["outputs"]["runtime_root"]
    errors, details = _domain_bundle_integrity_errors(
        repo_root,
        runtime_root=runtime_root,
        allowed_statuses={QUALIFIED},
        require_head_equal=False,
    )
    manifest = details.get("manifest", {})
    result = details.get("result", {})
    source_sha = str(details.get("source_sha", ""))
    trace_ref = result.get("graph_assurance", {}).get("qualification_ref")
    if not trace_ref:
        errors.append("graph_qualification_ref")
    else:
        try:
            qualification_path = (repo_root / trace_ref).resolve()
            qualification_path.relative_to(repo_root.resolve())
            qualification = _read_config(qualification_path)
            trace_path = (repo_root / qualification["trace_path"]).resolve()
            current_path = (repo_root / qualification["current_path"]).resolve()
            if not (
                qualification.get("result") == "PASS"
                and qualification.get("profile_id") == GRAPH_PROFILE_ID
                and qualification.get("source_code_sha") == source_sha
                and qualification.get("runtime_nodes") == 8
                and qualification.get("runtime_edges") == 7
                and qualification.get("lifecycle_promotions") == 0
                and qualification.get("sealed_boundaries_opened") == 0
                and qualification.get("trace_sha256") == sha256_file(trace_path)
                and qualification.get("current_sha256") == sha256_file(current_path)
                and current_path
                == (repo_root / ".planning" / "graphs" / "current.json").resolve()
            ):
                errors.append("graph_qualification_identity")
            errors.extend(
                _graph_assurance_errors(
                    repo_root, source_sha=source_sha, trace_path=trace_path
                )
            )
        except (OSError, KeyError, ValueError, json.JSONDecodeError):
            errors.append("graph_qualification_verification")
    return {
        "result": "PASS" if not errors else "FAIL",
        "errors": errors,
        "artifact_count": details.get("artifact_count", 0),
        "bundle_sha256": manifest.get("bundle_sha256"),
        "policy_replays": details.get("replays", []),
    }


__all__ = [
    "BLOCKED",
    "MISMATCH",
    "PARTIAL",
    "QUALIFIED",
    "REQUIRED_OUTPUTS",
    "build_evidence",
    "check_evidence",
    "finalize_graph_qualification",
    "replay_all_lanes",
    "run_cost_preflight",
    "validate_frozen_canary_contract",
]
