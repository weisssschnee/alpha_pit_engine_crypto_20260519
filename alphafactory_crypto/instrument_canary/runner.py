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
import time
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, replace
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
from .engine import CandidateObservation, LazySearchEngine, replay_policy_transcript
from .evaluator import StrictEvaluation, evaluate_authorized_materialization
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
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=repo_root,
        text=True,
    )
    if dirty.strip():
        raise RuntimeError(
            "formal evidence requires a clean committed source tree; commit source/config/tests first"
        )


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
    if formal + preflight > int(budget.get("total_first_evaluation_hard_cap", -1)):
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
    if errors:
        raise ValueError("; ".join(errors))
    return {
        "result": "PASS",
        "grammar_support_size": grammar.support_size,
        "grammar_contract_sha256": grammar.contract_sha256,
        "formal_proposals": formal,
        "preflight_evaluations": preflight,
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

    total_seconds = [row["total_ms"] / 1000.0 for row in rows]
    median = statistics.median(total_seconds)
    ordered = sorted(total_seconds)
    p95 = ordered[min(len(ordered) - 1, math.ceil(0.95 * len(ordered)) - 1)]
    scale = len(panel.timestamps) / len(sample.timestamps)
    hard_cap = int(config["budget"]["total_first_evaluation_hard_cap"])
    payload = {
        "schema_version": 1,
        "result": "PASS",
        "scope": "COST_ONLY_FEEDBACK_WITHHELD",
        "candidate_selection": contract["candidate_selection"],
        "selection_seed": int(contract["selection_seed"]),
        "candidate_count": count,
        "grammar_support_size": grammar.support_size,
        "full_universe_ranked_or_materialized": False,
        "sample_coordinates": len(sample.timestamps),
        "full_coordinates": len(panel.timestamps),
        "release_load_seconds": release_load_seconds,
        "release_load_rss_delta_bytes": release_load_rss_delta_bytes,
        "sample_candidate_median_seconds": median,
        "sample_candidate_p95_seconds": p95,
        "linear_coordinate_scale": scale,
        "estimated_2048_seconds_median": release_load_seconds + hard_cap * median * scale,
        "estimated_2048_seconds_p95": release_load_seconds + hard_cap * p95 * scale,
        "feedback_exposed": False,
        "policy_updates": 0,
        "economic_metrics_persisted": False,
        "first_evaluations_charged_to_hard_cap": count,
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
    ledger: Sequence[Mapping[str, Any]], config: Mapping[str, Any]
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
            ):
                if row.get(name):
                    row[name] = int(row[name])
            for name in ("feedback_blocked", "feedback_feasible", "cache_hit", "first_evaluation"):
                row[name] = str(row.get(name, "")).lower() == "true"
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


def build_evidence(
    repo_root: Path,
    *,
    config_path: Path,
    source_sha: str | None = None,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    _require_clean_source_tree(repo_root)
    config = _read_config(config_path)
    source_sha = (source_sha or _git_sha(repo_root)).lower()
    if source_sha != _git_sha(repo_root).lower():
        raise ValueError("source SHA must equal current HEAD")
    grammar = FrozenGrammar.default()
    contract_check = validate_frozen_canary_contract(config, grammar)

    process = psutil.Process(os.getpid())
    load_rss_before = process.memory_info().rss
    load_started = time.perf_counter()
    panel = load_development_release(config)
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

    engine = LazySearchEngine(
        grammar,
        authorizer=lambda proposal: _authorize(
            proposal.genome,
            grammar=grammar,
            panel=panel,
            config=config,
            source_sha=source_sha,
        ),
        first_visit_evaluator=lambda receipt: _first_visit_evaluator(receipt, panel),
        first_evaluation_hard_cap=int(config["budget"]["total_first_evaluation_hard_cap"]),
        already_consumed_first_evaluations=int(config["budget"]["cost_preflight_evaluations"]),
    )
    search = engine.run(
        algorithms=config["budget"]["algorithms"],
        seeds=config["budget"]["seeds"],
        steps_per_lane=int(config["budget"]["proposal_steps_per_seed_algorithm"]),
    )
    ledger = list(search.ledger)
    replays = replay_all_lanes(grammar, ledger)
    strict_audit = _strict_feedback_audit(ledger, config)
    decoy_audit = _admission_decoy_audit(
        panel,
        grammar=grammar,
        config=config,
        source_sha=source_sha,
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
    cross_algorithm_regions = all(
        len(
            {
                frozenset(
                    str(row["candidate_id"])
                    for row in ledger
                    if int(row["seed"]) == int(seed) and row["algorithm"] == algorithm
                )
                for algorithm in config["budget"]["algorithms"]
            }
        )
        == len(config["budget"]["algorithms"])
        for seed in config["budget"]["seeds"]
    )
    event_order = all(_event_order_pass(row) for row in ledger)
    replay_pass = len(replays) == 8 and all(row["result"] == "PASS" for row in replays)
    unique_visited = {str(row["candidate_id"]) for row in ledger}
    total_first = search.first_evaluations + int(config["budget"]["cost_preflight_evaluations"])
    checks = {
        "contract": contract_check["result"],
        "event_order": "PASS" if event_order else "FAIL",
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
        "sealed_reads_zero": "PASS" if panel.sealed_reads == 0 else "FAIL",
        "strict_feedback_alignment": strict_audit["result"],
        "admission_decoy_rejection": decoy_audit["result"],
        "cross_algorithm_visit_regions": "PASS" if cross_algorithm_regions else "FAIL",
        "evolutionary_runtime_mutation_receipts": (
            "PASS" if _evolution_runtime_receipts_pass(ledger) else "FAIL"
        ),
        "algorithm_behavior_hashes_distinct": (
            "PASS"
            if len(set(search.behavior_hashes.values())) == len(search.behavior_hashes)
            else "FAIL"
        ),
    }
    all_pass = all(value == "PASS" for value in checks.values())
    status = QUALIFIED if all_pass else MISMATCH
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
            "preflight_first_evaluations": int(config["budget"]["cost_preflight_evaluations"]),
            "total_first_evaluations": total_first,
            "hard_cap": int(config["budget"]["total_first_evaluation_hard_cap"]),
            "unvisited_structural_candidates": grammar.support_size - len(unique_visited),
            "unvisited_metrics_or_feedback": 0,
            "behavior_hashes": dict(search.behavior_hashes),
            "lane_state_hashes": dict(search.lane_state_hashes),
            "policy_replays": replays,
        },
        "checks": checks,
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
    manifest = {
        "schema_version": 1,
        "source_code_sha": source_sha,
        "artifacts": artifact_rows,
        "bundle_sha256": _payload_sha256(artifact_rows),
    }
    _write_json(runtime_root / "CRYPTO_CANARY_ARTIFACT_MANIFEST.json", manifest)
    return result


def check_evidence(repo_root: Path, *, config_path: Path) -> dict[str, Any]:
    config = _read_config(config_path)
    runtime_root = repo_root / config["outputs"]["runtime_root"]
    manifest_path = runtime_root / "CRYPTO_CANARY_ARTIFACT_MANIFEST.json"
    manifest = _read_config(manifest_path)
    errors: list[str] = []
    observed_rows: list[dict[str, Any]] = []
    for record in manifest.get("artifacts", []):
        path = repo_root / record["path"]
        if not path.is_file():
            errors.append(f"missing:{record['path']}")
            continue
        observed = sha256_file(path)
        observed_rows.append(
            {"path": record["path"], "bytes": path.stat().st_size, "sha256": observed}
        )
        if observed != record["sha256"] or path.stat().st_size != int(record["bytes"]):
            errors.append(f"hash_or_size:{record['path']}")
    if _payload_sha256(observed_rows) != manifest.get("bundle_sha256"):
        errors.append("bundle_sha256")
    for name in REQUIRED_OUTPUTS:
        if not (runtime_root / name).is_file():
            errors.append(f"required_output:{name}")
    result = _read_config(runtime_root / REQUIRED_OUTPUTS[7])
    if result.get("status") != QUALIFIED:
        errors.append("domain_status")
    ledger = _read_ledger(runtime_root / REQUIRED_OUTPUTS[2])
    replays = replay_all_lanes(FrozenGrammar.default(), ledger)
    if len(replays) != 8 or any(row["result"] != "PASS" for row in replays):
        errors.append("policy_replay")
    return {
        "result": "PASS" if not errors else "FAIL",
        "errors": errors,
        "artifact_count": len(observed_rows),
        "bundle_sha256": manifest.get("bundle_sha256"),
        "policy_replays": replays,
    }


__all__ = [
    "BLOCKED",
    "MISMATCH",
    "PARTIAL",
    "QUALIFIED",
    "REQUIRED_OUTPUTS",
    "build_evidence",
    "check_evidence",
    "replay_all_lanes",
    "run_cost_preflight",
    "validate_frozen_canary_contract",
]
