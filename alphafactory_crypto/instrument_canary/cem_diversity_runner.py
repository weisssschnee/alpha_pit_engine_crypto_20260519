"""Bounded development-only CEM diversity A/B evidence runner.

The historical CEM baseline is read from its immutable closure commit.  Each
challenger seed runs in a separate :class:`LazySearchEngine`, so the exact
cache is fresh and lane-local.  Counterfactual feedback replays are policy-only
and never call the evaluator.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import re
import statistics
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

from .cem_diversity import (
    CEMDiversityV2Policy,
    EXPLORATION_PROBABILITY,
    MAX_DUPLICATE_RESAMPLES,
)
from .contracts import SearchState
from .engine import CandidateFeedback, LazySearchEngine, replay_policy_transcript
from .grammar import FrozenGrammar
from .release import load_development_release, sha256_file
from .runner import (
    GRAPH_CONTRACT_IDS,
    SOURCE_AUTHORITY_PATHS,
    RealDataFirstVisitEvaluator,
    _authorize,
    _csv_value,
    _feedback_alignment,
    _ledger_contract_pass,
    _numeric_alias_integrity,
    _payload_sha256,
    _write_csv,
    _write_json,
    validate_frozen_canary_contract,
)


QUALIFIED = "CRYPTO_CEM_DIVERSITY_REPAIR_QUALIFIED"
MIXED = "CRYPTO_CEM_DIVERSITY_REPAIR_MIXED"
NO_IMPROVEMENT = "CRYPTO_CEM_DIVERSITY_REPAIR_NO_IMPROVEMENT"
INVALID = "CRYPTO_CEM_DIVERSITY_REPAIR_INVALID"
VALID_STATUSES = {QUALIFIED, MIXED, NO_IMPROVEMENT, INVALID}
PRODUCER = "alphafactory_crypto.instrument_canary.cem_diversity_runner"
DATA_ROLE = "DEVELOPMENT_TRAIN_ONLY"
LIFECYCLE = "EXPERIMENTAL"

RUNTIME_OUTPUTS = (
    "CRYPTO_CEM_DIVERSITY_AB_CONTRACT.json",
    "CRYPTO_CEM_DIVERSITY_AB_RESULT.json",
    "CRYPTO_CEM_DIVERSITY_LANE_METRICS.csv",
    "CRYPTO_CEM_DIVERSITY_DISTRIBUTION_METRICS.json",
    "CRYPTO_CEM_FEEDBACK_SENSITIVITY.json",
    "CRYPTO_CEM_BASELINE_BINDING.json",
    "CRYPTO_CEM_DIVERSITY_RUNTIME_EVENT_LOG.json",
    "CRYPTO_CEM_DIVERSITY_ARTIFACT_MANIFEST.json",
)

EXPERIMENT_SOURCE_PATHS = tuple(
    dict.fromkeys(
        (*SOURCE_AUTHORITY_PATHS,
         "alphafactory_crypto/instrument_canary/cem_diversity.py",
         "alphafactory_crypto/instrument_canary/cem_diversity_runner.py",
         "config/crypto_cem_diversity_ab_v1.json",
         "docs/adr/0004-cem-diversity-ab-experiment.md",
         "profiles/crypto-cem-diversity-ab.json",
         "scripts/crypto_cem_diversity_ab.py",
         ".graphifyignore",
         "scripts/maintain_crypto_navigation_graph.ps1",
         "tests/test_cem_diversity_policy.py",
         "tests/test_cem_diversity_runner.py")
    )
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _git_sha(repo_root: Path) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=repo_root, text=True
    ).strip().lower()


def _git_show(repo_root: Path, commit: str, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=repo_root)


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest().upper()


def _windows_checkout_bytes(blob: bytes) -> bytes:
    """Reconstruct the byte form hashed by the Windows-produced manifest."""

    return blob.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")


def _metadata(source_sha: str, status: str) -> dict[str, Any]:
    return {
        "producer": PRODUCER,
        "source_code_sha": source_sha,
        "data_role": DATA_ROLE,
        "lifecycle": LIFECYCLE,
        "status": status,
    }


def _parse_ledger(text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw in csv.DictReader(io.StringIO(text)):
        row: dict[str, Any] = dict(raw)
        for name in (
            "step", "seed", "proposal_ordinal", "proposal_sequence",
            "authorization_started_sequence", "authorized_sequence",
            "cache_lookup_sequence", "first_evaluation_sequence",
            "feedback_sequence", "policy_update_sequence",
            "feedback_available_after_step",
        ):
            if row.get(name):
                row[name] = int(row[name])
        for name in (
            "feedback_blocked", "feedback_feasible", "cache_hit", "first_visit",
            "first_evaluation", "evaluation_executed",
            "strict_evaluator_call_confirmed", "numeric_alias_detected",
            "numeric_alias_cache_hit",
        ):
            row[name] = str(row.get(name, "")).lower() == "true"
        for name in ("structural_genome", "feedback_sort_key", "feedback_violations"):
            row[name] = json.loads(row[name]) if row.get(name) else []
        row["feedback_distance"] = float(row["feedback_distance"])
        rows.append(row)
    return rows


def _unique_rows(rows: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    seen: set[str] = set()
    result: list[Mapping[str, Any]] = []
    for row in rows:
        candidate_id = str(row["candidate_id"])
        if candidate_id not in seen:
            seen.add(candidate_id)
            result.append(row)
    return result


def _rank_key(row: Mapping[str, Any]) -> tuple[float, ...]:
    return tuple(float(value) for value in row["feedback_sort_key"])


def _top_unique(rows: Sequence[Mapping[str, Any]], count: int) -> list[Mapping[str, Any]]:
    return _top_ranked(_unique_rows(rows), count)


def _top_ranked(rows: Sequence[Mapping[str, Any]], count: int) -> list[Mapping[str, Any]]:
    return sorted(
        rows,
        key=lambda row: (_rank_key(row), str(row["candidate_id"])),
        reverse=True,
    )[:count]


def _lane_summary(
    rows: Sequence[Mapping[str, Any]],
    *,
    variant: str,
    strict_calls: int | None = None,
    diagnostics: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    proposals = len(rows)
    unique = len({str(row["candidate_id"]) for row in rows})
    first = sum(bool(row.get("first_evaluation")) for row in rows)
    hits = sum(bool(row.get("cache_hit")) for row in rows)
    repeated = proposals - unique
    top8 = _top_unique(rows, 8)
    local_first = _unique_rows(rows)
    return {
        "variant": variant,
        "seed": int(rows[0]["seed"]),
        "lane_id": str(rows[0]["lane_id"]),
        "proposals": proposals,
        "unique_candidate_ids": unique,
        "policy_local_first_visits": unique,
        "first_evaluations": first,
        "exact_cache_hits": hits,
        "first_evaluation_rate": first / proposals,
        "policy_local_unique_rate": unique / proposals,
        "within_lane_repeated_candidate_count": repeated,
        "within_lane_duplicate_rate": repeated / proposals,
        "duplicate_resample_attempts": sum(
            int(row.get("duplicate_resample_attempts", 0)) for row in diagnostics
        ),
        "duplicate_resample_exhaustion_count": sum(
            bool(row.get("duplicate_resample_exhausted")) for row in diagnostics
        ),
        "numeric_aliases": sum(
            bool(row.get("first_evaluation")) and bool(row.get("numeric_alias_detected"))
            for row in rows
        ),
        "strict_evaluator_calls": first if strict_calls is None else int(strict_calls),
        "best_strict_feedback_sort_key": list(_rank_key(top8[0])) if top8 else [],
        "top_8_feedback_sort_keys": [list(_rank_key(row)) for row in top8],
        "all_policy_local_first_visit_median_feedback_distance": statistics.median(
            float(row["feedback_distance"]) for row in local_first
        ),
        "blocked_rate": sum(bool(row["feedback_blocked"]) for row in rows) / proposals,
        "feasible_visit_count": sum(bool(row["feedback_feasible"]) for row in rows),
    }


def _distribution(values: Iterable[str]) -> dict[str, Any]:
    counts = Counter(values)
    total = sum(counts.values())
    probabilities = [count / total for count in counts.values()] if total else []
    entropy = -sum(value * math.log(value) for value in probabilities if value > 0)
    return {
        "counts": dict(sorted(counts.items())),
        "entropy": entropy,
        "effective_support_size": math.exp(entropy),
        "top_share": max(probabilities, default=0.0),
    }


def _distribution_metrics(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    def token(row: Mapping[str, Any], *names: str) -> str:
        return "|".join(str(row.get(name)) for name in names)
    return {
        "mechanism_family": _distribution(token(row, "mechanism_family") for row in rows),
        "primitive": _distribution(token(row, "primitive_id") for row in rows),
        "field_representation": _distribution(
            token(row, "field_id", "representation_id") for row in rows
        ),
        "parameter_tuple": _distribution(
            token(row, "window", "long_window", "threshold") for row in rows
        ),
        "target_horizon": _distribution(token(row, "target_horizon_hours") for row in rows),
        "unique_grammar_cells": len({str(row["candidate_id"]) for row in rows}),
        "top_exact_candidate_share": max(
            Counter(str(row["candidate_id"]) for row in rows).values(), default=0
        ) / max(1, len(rows)),
    }


def _js_divergence(left: Mapping[str, int], right: Mapping[str, int]) -> float:
    keys = set(left) | set(right)
    left_total, right_total = sum(left.values()), sum(right.values())
    result = 0.0
    for key in keys:
        p = left.get(key, 0) / left_total if left_total else 0.0
        q = right.get(key, 0) / right_total if right_total else 0.0
        midpoint = (p + q) / 2.0
        if p:
            result += 0.5 * p * math.log(p / midpoint)
        if q:
            result += 0.5 * q * math.log(q / midpoint)
    return result


def validate_experiment_contract(
    repo_root: Path, config: Mapping[str, Any]
) -> dict[str, Any]:
    if (
        config.get("schema_version") != 1
        or config.get("experiment_id") != "CRYPTO_CEM_DIVERSITY_AB_20260715"
        or config.get("authorization")
        != "BOUNDED_EXISTING_RELEASE_DEVELOPMENT_CEM_DIVERSITY_AB"
    ):
        raise ValueError("experiment identity drift")
    grammar = FrozenGrammar.default()
    expected_base_ref = {
        "path": "config/crypto_real_data_instrument_canary_v1.json",
        "sha256": "12C931FC0488E3A12DB5350F43FD31F236F1442F579326DD475793EA199B4724",
    }
    base_ref = config["base_canary_config"]
    if base_ref != expected_base_ref:
        raise ValueError("base canary authority drift")
    base_path = repo_root / str(base_ref["path"])
    if sha256_file(base_path) != str(base_ref["sha256"]):
        raise ValueError("base canary config hash drift")
    base_config = _read_json(base_path)
    base_check = validate_frozen_canary_contract(base_config, grammar)
    baseline = config.get("baseline", {})
    expected_baseline_identity = {
        "closure_sha": "abef0622382d5691274164faff1643404b170640",
        "source_authority_sha": "e943f14aba1d0c0287f61746567a4ed26d702035",
        "result_path": "runtime/crypto_real_data_instrument_canary_20260715/CRYPTO_REAL_DATA_INSTRUMENT_CANARY_RESULT.json",
        "ledger_path": "runtime/crypto_real_data_instrument_canary_20260715/CRYPTO_LAZY_EVALUATION_LEDGER.csv",
        "algorithm_behavior_path": "runtime/crypto_real_data_instrument_canary_20260715/CRYPTO_ALGORITHM_BEHAVIOR_AUDIT.json",
        "checkout_artifact_sha256": {
            "result": "6D4AA17739CA4D8E70D90C5819AA9EF5FC01EC465224662638F4844688C805B5",
            "ledger": "2ADE0131B17D457A781BCC4E2AAF02F00FE8F6B754729DD020F728C621737C3C",
            "algorithm_behavior": "E50933FD1B569404DDAB07A8F6EA0C57EBE72528DB71EE68D6CE41440947B05B",
        },
        "closure_blob_sha256": {
            "result": "977227CE4A9C1E7D5BBE34BB49CF35F902AC3F70CBB04957FBC32668EBD32EB5",
            "ledger": "0E84A2255CEDCE114DF45DC781FD275F3CEEDA74C7A6A074D42D8323576DE16E",
            "algorithm_behavior": "BBBA43E1BB523EB408F019F4CAB336A2769120B0C07862FE3C925A545B197758",
        },
        "cem_lane_behavior_sha256": {
            "20260715": "10911CDE3A7E55DB1B1798EC3A3E0903DB36942B03140960CF01F8CFB8DFDA1F",
            "20260716": "05E528043ED89EE5530BB66D0947D9FCE1B1DCAC0FE4A1135E39C4AD034EBE55",
        },
        "lanes": ["cem_like:seed=20260715", "cem_like:seed=20260716"],
        "observed_global_cache": {
            "20260715": {"proposals": 128, "first_evaluations": 38, "exact_cache_hits": 90},
            "20260716": {"proposals": 128, "first_evaluations": 58, "exact_cache_hits": 70},
        },
        "matched_policy_local": {
            "20260715": {"proposals": 128, "unique_candidates": 39, "within_lane_repeats": 89},
            "20260716": {"proposals": 128, "unique_candidates": 66, "within_lane_repeats": 62},
            "pooled_unique_candidates": 105,
            "pooled_proposals": 256,
        },
    }
    if baseline != expected_baseline_identity:
        raise ValueError("baseline authority drift")
    challenger = config["challenger"]
    if (
        challenger.get("policy_name") != "cem_diversity_v2"
        or challenger.get("seeds") != [20260715, 20260716]
        or challenger.get("proposals_per_seed") != 128
        or challenger.get("fresh_run_cache_per_seed") is not True
        or challenger.get("exploration_probability") != EXPLORATION_PROBABILITY
        or challenger.get("duplicate_resample_limit") != MAX_DUPLICATE_RESAMPLES
        or challenger.get("maximum_total_proposals") != 256
        or challenger.get("maximum_strict_evaluator_calls") != 256
        or challenger.get("feedback_warmup_steps") != 8
        or challenger.get("branch_draws_per_proposal") != 1
        or challenger.get("exploration_method")
        != "UNIFORM_GRAMMAR_INDEX_WITHOUT_UNIVERSE_MATERIALIZATION"
        or challenger.get("prior_conservative_physical_strict_calls") != 1728
        or challenger.get("maximum_post_experiment_conservative_calls") != 1984
        or challenger.get("global_hard_cap") != 2048
    ):
        raise ValueError("challenger contract drift")
    expected_neutral = {
        "applied_from_update_ordinal": 0,
        "blocked": False,
        "feasible": False,
        "violations": ["FIXED_NEUTRAL_POLICY_REPLAY_ONLY"],
        "distance": 0.0,
        "sort_key": [1, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "reason": "FIXED_NEUTRAL_POLICY_REPLAY_ONLY",
    }
    if challenger.get("neutral_feedback") != expected_neutral:
        raise ValueError("neutral feedback contract drift")
    comparison = config.get("comparison", {})
    expected_comparison = {
        "primary_coverage_metric": "POLICY_LOCAL_UNIQUE_PROPOSAL_RATE",
        "observed_global_cache_first_evaluations_role": "PROVENANCE_ONLY_NOT_PRIMARY_AB_EFFECT",
        "qualified_requires_observed_and_matched_thresholds": True,
        "entropy_log_base": "NATURAL",
        "effective_support_formula": "exp(shannon_entropy)",
        "distribution_divergence": "JENSEN_SHANNON_NATURAL_LOG_NO_SMOOTHING",
        "top_feedback_selection": "POOLED_GLOBAL_UNIQUE_CANDIDATES_SORTED_BY_FROZEN_FEEDBACK_SORT_KEY_DESCENDING",
        "top_feedback_count": 16,
        "baseline_unique_candidate_top16_median_feedback_distance": -0.9098252298484152,
        "feedback_distance_noninferiority_floor": -1.0008077528332566,
        "feedback_distance_noninferiority_formula": "baseline_median - 0.10 * abs(baseline_median)",
    }
    if comparison != expected_comparison:
        raise ValueError("comparison contract drift")
    expected_thresholds = {
        "per_seed_first_evaluation_rate_improvement_points": 0.15,
        "pooled_first_evaluation_rate_improvement_points": 0.2,
        "per_seed_duplicate_rate_relative_reduction": 0.3,
        "top16_feedback_distance_max_relative_degradation": 0.1,
        "matched_minimum_unique_candidates": {
            "20260715": 59, "20260716": 86, "pooled": 157,
        },
        "maximum_within_lane_repeats": {"20260715": 62, "20260716": 43},
        "decision_precedence": [INVALID, QUALIFIED, MIXED, NO_IMPROVEMENT],
    }
    if config.get("qualification_thresholds") != expected_thresholds:
        raise ValueError("qualification threshold drift")
    if config.get("outputs") != {
        "runtime_root": "runtime/crypto_cem_diversity_ab_20260715",
        "report": "reports/CRYPTO_CEM_DIVERSITY_AB_REPORT.md",
    }:
        raise ValueError("output contract drift")
    boundaries = config["boundaries"]
    if boundaries.get("allowed_data_role") != DATA_ROLE or any(
        boundaries.get(name) is not False
        for name in (
            "new_data_integration", "formal_performance_search",
            "candidate_promotion", "cross_sprint_adaptive_memory",
            "baseline_overwrite", "economic_alpha_claim",
        )
    ):
        raise ValueError("experiment boundary drift")
    expected_sealed = {
        "VALIDATION", "HOLDOUT", "TEST", "RECENT", "FORWARD",
        "CHALLENGE", "MAY_STRESS",
    }
    if not expected_sealed.issubset(set(boundaries.get("sealed_roles", ()))):
        raise ValueError("sealed role contract incomplete")
    return {
        "result": "PASS",
        "base_canary_contract": base_check,
        "grammar_support_size": grammar.support_size,
        "grammar_contract_sha256": grammar.contract_sha256,
        "base_config": base_config,
    }


def load_baseline_binding(
    repo_root: Path, config: Mapping[str, Any], *, source_sha: str
) -> tuple[dict[str, Any], dict[int, list[dict[str, Any]]]]:
    baseline = config["baseline"]
    closure = str(baseline["closure_sha"])
    payloads = {
        "result": _git_show(repo_root, closure, str(baseline["result_path"])),
        "ledger": _git_show(repo_root, closure, str(baseline["ledger_path"])),
        "algorithm_behavior": _git_show(
            repo_root, closure, str(baseline["algorithm_behavior_path"])
        ),
    }
    # Git stores the text blobs with LF, while the accepted Windows run wrote
    # and hashed CRLF bytes.  Bind both identities and compare the declared
    # artifact hash to the reconstructed checkout bytes.
    observed_hashes = {
        name: _sha256_bytes(_windows_checkout_bytes(value))
        for name, value in payloads.items()
    }
    git_blob_content_hashes = {
        name: _sha256_bytes(value) for name, value in payloads.items()
    }
    checkout_expected = dict(
        baseline.get("checkout_artifact_sha256", baseline.get("artifact_sha256", {}))
    )
    if observed_hashes != checkout_expected:
        raise ValueError("baseline artifact hash mismatch")
    blob_expected = baseline.get("closure_blob_sha256")
    if blob_expected is not None and git_blob_content_hashes != dict(blob_expected):
        raise ValueError("baseline closure blob hash mismatch")
    result = json.loads(payloads["result"])
    if (
        str(result.get("source_code_sha", "")) != str(baseline["source_authority_sha"])
        or result.get("status") != "CRYPTO_REAL_DATA_INSTRUMENT_CANARY_EXECUTION_QUALIFIED"
    ):
        raise ValueError("baseline source/status mismatch")
    ledger = _parse_ledger(payloads["ledger"].decode("utf-8"))
    lanes: dict[int, list[dict[str, Any]]] = {}
    summaries: dict[str, Any] = {}
    for seed in baseline["matched_policy_local"]:
        if seed in {"pooled_unique_candidates", "pooled_proposals"}:
            continue
        seed_int = int(seed)
        rows = [
            row for row in ledger
            if row["algorithm"] == "cem_like" and int(row["seed"]) == seed_int
        ]
        lanes[seed_int] = rows
        summary = _lane_summary(rows, variant="baseline_cem_like")
        expected = baseline["matched_policy_local"][seed]
        if (
            summary["proposals"] != int(expected["proposals"])
            or summary["unique_candidate_ids"] != int(expected["unique_candidates"])
            or summary["within_lane_repeated_candidate_count"]
            != int(expected["within_lane_repeats"])
        ):
            raise ValueError("baseline policy-local metric mismatch")
        observed = baseline["observed_global_cache"][seed]
        if (
            summary["first_evaluations"] != int(observed["first_evaluations"])
            or summary["exact_cache_hits"] != int(observed["exact_cache_hits"])
        ):
            raise ValueError("baseline global-cache metric mismatch")
        behavior = result["search"]["behavior_hashes"][f"cem_like:seed={seed}"]
        if behavior != baseline["cem_lane_behavior_sha256"][seed]:
            raise ValueError("baseline lane transcript hash mismatch")
        summaries[seed] = summary
    pooled_top = _top_unique([*lanes[20260715], *lanes[20260716]], 16)
    pooled_median = statistics.median(
        float(row["feedback_distance"]) for row in pooled_top
    )
    expected_median = float(
        config["comparison"]["baseline_unique_candidate_top16_median_feedback_distance"]
    )
    if not math.isclose(pooled_median, expected_median, rel_tol=1e-14, abs_tol=1e-14):
        raise ValueError("baseline top16 feedback qualification drift")
    binding = {
        "schema_version": 1,
        **_metadata(source_sha, "PENDING"),
        "validation_result": "PASS",
        "baseline_closure_sha": closure,
        "baseline_source_authority_sha": baseline["source_authority_sha"],
        "checkout_artifact_sha256": observed_hashes,
        "closure_blob_sha256": git_blob_content_hashes,
        "cem_lane_behavior_sha256": dict(baseline["cem_lane_behavior_sha256"]),
        "observed_global_cache": dict(baseline["observed_global_cache"]),
        "matched_policy_local": dict(baseline["matched_policy_local"]),
        "lane_metrics": summaries,
        "pooled_unique_candidate_top16_median_feedback_distance": pooled_median,
        "role": "IMMUTABLE_BASELINE_PROVENANCE_NO_RERUN",
    }
    return binding, lanes


def _policy_factory(store: dict[int, CEMDiversityV2Policy]) -> Callable[..., CEMDiversityV2Policy]:
    def factory(name: str, grammar: FrozenGrammar, seed: int) -> CEMDiversityV2Policy:
        if name != "cem_diversity_v2":
            raise ValueError("challenger runner accepts cem_diversity_v2 only")
        policy = CEMDiversityV2Policy(grammar, seed)
        store[int(seed)] = policy
        return policy
    return factory


def feedback_sensitivity_replay(
    grammar: FrozenGrammar,
    lanes: Mapping[int, Sequence[Mapping[str, Any]]],
    config: Mapping[str, Any],
) -> dict[str, Any]:
    outputs: list[dict[str, Any]] = []
    neutral = config["challenger"]["neutral_feedback"]
    warmup = int(config["challenger"]["feedback_warmup_steps"])
    for seed, raw_rows in sorted(lanes.items()):
        rows = sorted(raw_rows, key=lambda row: int(row["step"]))
        replay = replay_policy_transcript(
            grammar,
            algorithm="cem_diversity_v2",
            seed=seed,
            ledger_rows=rows,
            policy_factory=lambda _name, g, s: CEMDiversityV2Policy(g, s),
        )
        policy = CEMDiversityV2Policy(grammar, seed)
        neutral_ids: list[str] = []
        for step in range(len(rows)):
            proposal = policy.propose(SearchState(step, len(rows) - step))
            neutral_ids.append(proposal.candidate_id)
            feedback = CandidateFeedback(
                candidate_id=proposal.candidate_id,
                blocked=bool(neutral["blocked"]),
                feasible=bool(neutral["feasible"]),
                violations=tuple(str(value) for value in neutral["violations"]),
                distance=float(neutral["distance"]),
                sort_key=tuple(neutral["sort_key"]),
                reason=str(neutral["reason"]),
            )
            policy.update(proposal, feedback)
        real_ids = [str(row["candidate_id"]) for row in rows]
        differences = [index for index, pair in enumerate(zip(real_ids, neutral_ids)) if pair[0] != pair[1]]
        first_difference = differences[0] if differences else None
        lane_pass = bool(
            replay["result"] == "PASS"
            and real_ids[:warmup] == neutral_ids[:warmup]
            and any(index >= warmup for index in differences)
            and replay["final_policy_state_sha256"] != policy.state_hash()
        )
        outputs.append(
            {
                "seed": seed,
                "real_replay_result": replay["result"],
                "first_warmup_proposals_equal": real_ids[:warmup] == neutral_ids[:warmup],
                "post_warmup_transcript_diverged": any(index >= warmup for index in differences),
                "first_difference_proposal_ordinal": first_difference,
                "real_transcript_sha256": _payload_sha256({"candidate_ids": real_ids}),
                "neutral_transcript_sha256": _payload_sha256({"candidate_ids": neutral_ids}),
                "real_final_policy_state_sha256": replay["final_policy_state_sha256"],
                "neutral_final_policy_state_sha256": policy.state_hash(),
                "evaluator_calls": 0,
                "result": "PASS" if lane_pass else "FAIL",
            }
        )
    return {
        "schema_version": 1,
        "scope": "POLICY_ONLY_COUNTERFACTUAL_NO_MARKET_DATA",
        "neutral_feedback": dict(neutral),
        "lanes": outputs,
        "result": "PASS" if len(outputs) == 2 and all(row["result"] == "PASS" for row in outputs) else "FAIL",
    }


def _cache_reuse_is_completed(rows: Sequence[Mapping[str, Any]]) -> bool:
    completed: set[str] = set()
    for row in sorted(rows, key=lambda value: int(value["step"])):
        key = str(row["cache_key"])
        if bool(row["cache_hit"]):
            if key not in completed or bool(row["evaluation_executed"]):
                return False
        else:
            if key in completed or not bool(row["evaluation_executed"]):
                return False
            completed.add(key)
    return True


def _run_challenger(
    panel: Any,
    *,
    grammar: FrozenGrammar,
    base_config: Mapping[str, Any],
    experiment_config: Mapping[str, Any],
    source_sha: str,
    runtime_trace: Any | None,
) -> tuple[dict[int, dict[str, Any]], int]:
    runs: dict[int, dict[str, Any]] = {}
    total_strict_calls = 0
    steps = int(experiment_config["challenger"]["proposals_per_seed"])
    for seed in experiment_config["challenger"]["seeds"]:
        policies: dict[int, CEMDiversityV2Policy] = {}
        evaluator = RealDataFirstVisitEvaluator(panel, runtime_trace=runtime_trace)

        def authorize(proposal: Any) -> Any:
            receipt = _authorize(
                proposal.genome,
                grammar=grammar,
                panel=panel,
                config=base_config,
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
            authorizer=authorize,
            first_visit_evaluator=evaluator,
            first_evaluation_hard_cap=steps,
            policy_factory=_policy_factory(policies),
        )
        search = engine.run(
            algorithms=["cem_diversity_v2"], seeds=[int(seed)], steps_per_lane=steps
        )
        policy = policies[int(seed)]
        rows = list(search.ledger)
        diagnostics = [dict(row) for row in policy.proposal_diagnostics]
        if len(rows) != len(diagnostics):
            raise RuntimeError("challenger diagnostics/ledger length mismatch")
        runs[int(seed)] = {
            "seed": int(seed),
            "fresh_cache": True,
            "ledger": rows,
            "events": list(search.events),
            "authorization_receipts": list(search.authorization_receipts),
            "policy_diagnostics": diagnostics,
            "behavior_hash": search.behavior_hashes[f"cem_diversity_v2:seed={seed}"],
            "final_policy_state_sha256": search.lane_state_hashes[
                f"cem_diversity_v2:seed={seed}"
            ],
            "first_evaluations": search.first_evaluations,
            "cache_hits": search.cache_hits,
            "strict_evaluator_calls": evaluator.strict_evaluator_calls,
            "numeric_unique_inputs": evaluator.numeric_unique_inputs,
            "numeric_alias_observations": evaluator.numeric_alias_observations,
        }
        total_strict_calls += evaluator.strict_evaluator_calls
    return runs, total_strict_calls


def _cross_seed_metrics(rows_by_seed: Mapping[int, Sequence[Mapping[str, Any]]]) -> dict[str, Any]:
    left, right = (rows_by_seed[20260715], rows_by_seed[20260716])
    left_ids = {str(row["candidate_id"]) for row in left}
    right_ids = {str(row["candidate_id"]) for row in right}
    union = left_ids | right_ids
    left_distributions = _distribution_metrics(left)
    right_distributions = _distribution_metrics(right)
    left_rate = len(left_ids) / len(left)
    right_rate = len(right_ids) / len(right)
    return {
        "candidate_set_jaccard": len(left_ids & right_ids) / len(union) if union else 1.0,
        "mechanism_distribution_divergence": _js_divergence(
            left_distributions["mechanism_family"]["counts"],
            right_distributions["mechanism_family"]["counts"],
        ),
        "primitive_distribution_divergence": _js_divergence(
            left_distributions["primitive"]["counts"],
            right_distributions["primitive"]["counts"],
        ),
        "first_evaluation_rate_stability_absolute_difference": abs(left_rate - right_rate),
    }


def _decision(
    config: Mapping[str, Any],
    baseline_summaries: Mapping[int, Mapping[str, Any]],
    challenger_summaries: Mapping[int, Mapping[str, Any]],
    *,
    integrity_checks: Mapping[str, bool],
    sensitivity_pass: bool,
    top16_median: float,
) -> tuple[str, dict[str, bool]]:
    thresholds = config["qualification_thresholds"]
    minimums = thresholds["matched_minimum_unique_candidates"]
    maximum_repeats = thresholds["maximum_within_lane_repeats"]
    effect: dict[str, bool] = {}
    for seed in (20260715, 20260716):
        key = str(seed)
        challenger = challenger_summaries[seed]
        baseline = baseline_summaries[seed]
        effect[f"matched_first_evaluation_rate_seed_{seed}"] = (
            int(challenger["first_evaluations"]) >= int(minimums[key])
        )
        observed = config["baseline"]["observed_global_cache"][key]
        observed_minimum = math.ceil(
            (int(observed["first_evaluations"]) / int(observed["proposals"])
             + float(thresholds["per_seed_first_evaluation_rate_improvement_points"]))
            * int(observed["proposals"])
        )
        effect[f"observed_provenance_rate_seed_{seed}"] = (
            int(challenger["first_evaluations"]) >= observed_minimum
        )
        effect[f"duplicate_reduction_seed_{seed}"] = (
            int(challenger["within_lane_repeated_candidate_count"])
            <= int(maximum_repeats[key])
            and int(challenger["within_lane_repeated_candidate_count"])
            < int(baseline["within_lane_repeated_candidate_count"])
        )
    pooled_first = sum(int(row["first_evaluations"]) for row in challenger_summaries.values())
    effect["matched_pooled_first_evaluation_rate"] = pooled_first >= int(minimums["pooled"])
    observed_pooled_minimum = math.ceil(
        ((38 + 58) / 256 + float(thresholds["pooled_first_evaluation_rate_improvement_points"]))
        * 256
    )
    effect["observed_provenance_pooled_rate"] = pooled_first >= observed_pooled_minimum
    effect["feedback_sensitivity"] = sensitivity_pass
    effect["top16_feedback_noninferiority"] = top16_median >= float(
        config["comparison"]["feedback_distance_noninferiority_floor"]
    )
    if not all(integrity_checks.values()):
        return INVALID, effect
    qualification_names = [
        name for name in effect
        if name.startswith("matched_")
        or name.startswith("observed_")
        or name.startswith("duplicate_")
        or name in {"feedback_sensitivity", "top16_feedback_noninferiority"}
    ]
    if all(effect[name] for name in qualification_names):
        return QUALIFIED, effect
    duplicate_pass = all(
        effect[f"duplicate_reduction_seed_{seed}"] for seed in (20260715, 20260716)
    )
    coverage_any = any(
        effect[f"matched_first_evaluation_rate_seed_{seed}"]
        for seed in (20260715, 20260716)
    )
    if duplicate_pass and sensitivity_pass and (
        coverage_any or not effect["top16_feedback_noninferiority"]
    ):
        return MIXED, effect
    return NO_IMPROVEMENT, effect


def _run_tests(repo_root: Path) -> dict[str, Any]:
    collect = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "--collect-only",
            "-q",
            "tests/test_cem_diversity_policy.py",
            "tests/test_cem_diversity_runner.py",
        ],
        cwd=repo_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=repo_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    match = re.search(r"(\d+) passed", completed.stdout)
    collected = re.search(r"(\d+) tests? collected", collect.stdout)
    return {
        "result": (
            "PASS"
            if completed.returncode == 0 and collect.returncode == 0 and match and collected
            else "FAIL"
        ),
        "new_tests": int(collected.group(1)) if collected else 0,
        "passed": int(match.group(1)) if match else 0,
        "returncode": completed.returncode,
        "output_tail": completed.stdout[-2000:],
    }


def _recompute_runtime_core(
    config: Mapping[str, Any],
    *,
    baseline_lanes: Mapping[int, Sequence[Mapping[str, Any]]],
    runs: Mapping[int, Mapping[str, Any]],
    sealed_reads: int,
    test_evidence: Mapping[str, Any],
) -> dict[str, Any]:
    grammar = FrozenGrammar.default()
    challenger_lanes = {
        int(seed): list(run["ledger"]) for seed, run in runs.items()
    }
    sensitivity = feedback_sensitivity_replay(grammar, challenger_lanes, config)
    baseline_summaries = {
        seed: _lane_summary(rows, variant="baseline_cem_like")
        for seed, rows in baseline_lanes.items()
    }
    challenger_summaries = {
        seed: _lane_summary(
            run["ledger"],
            variant="challenger_cem_diversity_v2",
            strict_calls=int(run["strict_evaluator_calls"]),
            diagnostics=run["policy_diagnostics"],
        )
        for seed, run in runs.items()
    }
    strict_calls = sum(int(run["strict_evaluator_calls"]) for run in runs.values())
    expected_seeds = {int(seed) for seed in config["challenger"]["seeds"]}
    expected_steps = int(config["challenger"]["proposals_per_seed"])
    exact_lane_shape = set(runs) == expected_seeds and len(runs) == len(expected_seeds)
    if exact_lane_shape:
        for seed, run in runs.items():
            ledger = list(run.get("ledger", ()))
            diagnostics = list(run.get("policy_diagnostics", ()))
            lane_id = f"cem_diversity_v2:seed={seed}"
            exact_lane_shape = bool(
                int(run.get("seed", -1)) == seed
                and len(ledger) == expected_steps
                and len(diagnostics) == expected_steps
                and all(
                    int(row.get("seed", -1)) == seed
                    and row.get("algorithm") == "cem_diversity_v2"
                    and row.get("lane_id") == lane_id
                    and int(row.get("step", -1)) == ordinal
                    and int(row.get("proposal_ordinal", -1)) == ordinal
                    and diagnostics[ordinal].get("candidate_id") == row.get("candidate_id")
                    and int(diagnostics[ordinal].get("ordinal", -1)) == ordinal
                    for ordinal, row in enumerate(ledger)
                )
            )
            if not exact_lane_shape:
                break
    integrity: dict[str, bool] = {
        "frozen_contract": True,
        "exact_lane_shape": exact_lane_shape,
        "fresh_cache_per_seed": len(runs) == 2 and all(
            bool(run["fresh_cache"]) for run in runs.values()
        ),
        "proposal_budget": sum(len(run["ledger"]) for run in runs.values()) == 256,
        "strict_evaluator_budget": strict_calls <= 256,
        "strict_evaluator_every_first_visit": strict_calls
        == sum(int(run["first_evaluations"]) for run in runs.values()),
        "exact_cache_reuses_completed_observation": all(
            _cache_reuse_is_completed(run["ledger"]) for run in runs.values()
        ),
        "ledger_contract": all(
            _ledger_contract_pass(run["ledger"]) for run in runs.values()
        ),
        "strict_feedback_alignment": all(
            _feedback_alignment(row)[0]
            for run in runs.values() for row in run["ledger"]
        ),
        "numeric_aliases_strictly_re_evaluated": all(
            _numeric_alias_integrity(
                run["ledger"],
                {"search": {
                    "first_evaluations": run["first_evaluations"],
                    "strict_evaluator_calls": run["strict_evaluator_calls"],
                    "numeric_unique_inputs": run["numeric_unique_inputs"],
                    "numeric_alias_observations": run["numeric_alias_observations"],
                    "exact_numeric_alias_savings": 0,
                }},
            )
            for run in runs.values()
        ),
        "real_transcript_replay": all(
            lane["real_replay_result"] == "PASS"
            and lane["real_transcript_sha256"]
            == runs[int(lane["seed"])]["behavior_hash"]
            for lane in sensitivity["lanes"]
        ),
        "unvisited_metrics_or_feedback_zero": all(
            len([
                event for event in run["events"]
                if event["event_type"] == "VISITED_FEEDBACK_EXPOSED"
            ]) == len(run["ledger"])
            for run in runs.values()
        ),
        "sealed_reads_zero": int(sealed_reads) == 0,
        "tests": (
            test_evidence.get("result") == "PASS"
            and int(test_evidence.get("passed", 0)) > 0
            and int(test_evidence.get("new_tests", 0)) > 0
        ),
        "conservative_physical_call_cap": (
            int(config["challenger"]["prior_conservative_physical_strict_calls"])
            + strict_calls
            <= int(config["challenger"]["maximum_post_experiment_conservative_calls"])
            <= int(config["challenger"]["global_hard_cap"])
        ),
    }
    pooled_top = _top_unique(
        [*challenger_lanes[20260715], *challenger_lanes[20260716]],
        int(config["comparison"]["top_feedback_count"]),
    )
    pooled_median = statistics.median(
        float(row["feedback_distance"]) for row in pooled_top
    )
    status, effect = _decision(
        config,
        baseline_summaries,
        challenger_summaries,
        integrity_checks=integrity,
        sensitivity_pass=sensitivity["result"] == "PASS",
        top16_median=pooled_median,
    )
    distributions = {
        "lanes": {
            f"baseline:{seed}": _distribution_metrics(rows)
            for seed, rows in baseline_lanes.items()
        } | {
            f"challenger:{seed}": _distribution_metrics(rows)
            for seed, rows in challenger_lanes.items()
        },
        "cross_seed": {
            "baseline": _cross_seed_metrics(baseline_lanes),
            "challenger": _cross_seed_metrics(challenger_lanes),
        },
    }
    return {
        "status": status,
        "sensitivity": sensitivity,
        "baseline_summaries": baseline_summaries,
        "challenger_summaries": challenger_summaries,
        "strict_evaluator_calls": strict_calls,
        "integrity_checks": integrity,
        "effect_checks": effect,
        "pooled_top16_median_feedback_distance": pooled_median,
        "distributions": distributions,
    }


def _experiment_source_blobs(repo_root: Path, source_sha: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for relative in EXPERIMENT_SOURCE_PATHS:
        committed = _git_show(repo_root, source_sha, relative)
        if subprocess.run(
            ["git", "diff", "--quiet", source_sha, "--", relative],
            cwd=repo_root,
            check=False,
        ).returncode != 0:
            raise RuntimeError(f"source authority differs from bound SHA: {relative}")
        rows.append(
            {
                "path": relative,
                "bytes": len(committed),
                "sha256": _sha256_bytes(committed),
                "git_blob": subprocess.check_output(
                    ["git", "rev-parse", f"{source_sha}:{relative}"],
                    cwd=repo_root,
                    text=True,
                ).strip(),
            }
        )
    return rows


def _report_text(result: Mapping[str, Any]) -> str:
    lane_lines = []
    for row in result["lane_metrics"]:
        lane_lines.append(
            f"| {row['variant']} | {row['seed']} | {row['proposals']} | "
            f"{row['unique_candidate_ids']} | {row['first_evaluations']} | "
            f"{row['exact_cache_hits']} | {row['within_lane_repeated_candidate_count']} |"
        )
    return "\n".join(
        [
            "# Crypto CEM Diversity A/B",
            "",
            f"Status: `{result['status']}`",
            "",
            "This is a development-only search-instrument A/B. It is not Alpha, OOS proof, promotion, or authorization to expand search.",
            "",
            "| Variant | Seed | Proposals | Unique | First evals | Cache hits | Within-lane repeats |",
            "|---|---:|---:|---:|---:|---:|---:|",
            *lane_lines,
            "",
            f"- Strict evaluator calls: {result['strict_evaluator_calls']}.",
            f"- Sealed reads: {result['sealed_reads']}.",
            f"- Feedback sensitivity: {result['feedback_sensitivity_result']}.",
            f"- Unique-candidate pooled top-16 median feedback distance: {result['pooled_top16_median_feedback_distance']}.",
            f"- Tests: {result['test_evidence']['new_tests']} new; {result['test_evidence']['passed']} total passed.",
            "",
            "The 38/58 historical first-evaluation counts remain provenance-only because the old run shared a cache with other lanes. The primary matched baseline is 39/66 policy-local unique candidates.",
            "",
        ]
    )


def _manifest_payload(
    repo_root: Path,
    *,
    runtime_root: Path,
    report_path: Path,
    source_sha: str,
    status: str,
    source_blobs: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    manifest_path = runtime_root / RUNTIME_OUTPUTS[-1]
    paths = sorted(
        [path for path in runtime_root.iterdir() if path.is_file() and path != manifest_path]
        + [report_path]
    )
    artifacts = [
        {
            "path": path.relative_to(repo_root).as_posix(),
            "bytes": path.stat().st_size,
            "content_sha256": sha256_file(path),
            "producer": PRODUCER,
            "source_code_sha": source_sha,
            "data_role": DATA_ROLE,
            "lifecycle": LIFECYCLE,
            "status": status,
        }
        for path in paths
    ]
    return {
        "schema_version": 1,
        **_metadata(source_sha, status),
        "artifacts": artifacts,
        "source_blobs": list(source_blobs),
        "bundle_sha256": _payload_sha256(artifacts),
        "manifest_self_excluded": True,
    }


def build_evidence(
    repo_root: Path,
    *,
    config_path: Path,
    source_sha: str | None = None,
    runtime_trace: Any | None = None,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    config = _read_json(config_path)
    contract_check = validate_experiment_contract(repo_root, config)
    source_sha = (source_sha or _git_sha(repo_root)).lower()
    if source_sha != _git_sha(repo_root):
        raise ValueError("source SHA must equal HEAD")
    source_blobs = _experiment_source_blobs(repo_root, source_sha)
    runtime_root = repo_root / config["outputs"]["runtime_root"]
    report_path = repo_root / config["outputs"]["report"]
    if runtime_root.exists() and any(runtime_root.iterdir()):
        raise RuntimeError("runtime output root is not empty")
    if report_path.exists():
        raise RuntimeError("report already exists")
    baseline_binding, baseline_lanes = load_baseline_binding(
        repo_root, config, source_sha=source_sha
    )
    test_evidence = _run_tests(repo_root)
    if test_evidence["result"] != "PASS":
        raise RuntimeError("test suite failed before market-data execution")
    grammar = FrozenGrammar.default()
    base_config = contract_check["base_config"]
    panel = load_development_release(base_config)
    if runtime_trace is not None:
        runtime_trace.observe_component(
            "cem_diversity_ab_experiment",
            implementation_path="alphafactory_crypto/instrument_canary/cem_diversity_runner.py",
            function="build_evidence",
            semantic_role="experimental_non_formal_cem_ab",
            evidence_produced=True,
        )
        runtime_trace.observe_component(
            "real_data_lazy_search_canary",
            implementation_path="alphafactory_crypto/instrument_canary/engine.py",
            function="LazySearchEngine.run",
            semantic_role="bounded_real_data_lazy_search",
            evidence_produced=True,
        )
        runtime_trace.observe_edge(
            "cem_diversity_ab_experiment",
            "real_data_lazy_search_canary",
            edge_type="RUNTIME_CALL",
            relationship="EXPERIMENTAL_CURRENT_NON_FORMAL",
        )
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
        runtime_trace.observe_component(
            "sealed_research_boundaries",
            implementation_path="alphafactory_crypto/instrument_canary/cem_diversity_runner.py",
            function="validate_experiment_contract",
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
    runs, strict_calls = _run_challenger(
        panel,
        grammar=grammar,
        base_config=base_config,
        experiment_config=config,
        source_sha=source_sha,
        runtime_trace=runtime_trace,
    )
    recomputed = _recompute_runtime_core(
        config,
        baseline_lanes=baseline_lanes,
        runs=runs,
        sealed_reads=panel.sealed_reads,
        test_evidence=test_evidence,
    )
    sensitivity = recomputed["sensitivity"]
    baseline_summaries = recomputed["baseline_summaries"]
    challenger_summaries = recomputed["challenger_summaries"]
    integrity = recomputed["integrity_checks"]
    effect_checks = recomputed["effect_checks"]
    pooled_top_median = recomputed["pooled_top16_median_feedback_distance"]
    strict_calls = recomputed["strict_evaluator_calls"]
    status = recomputed["status"]
    baseline_binding.update(_metadata(source_sha, status))
    lane_rows = [
        *[baseline_summaries[seed] for seed in sorted(baseline_summaries)],
        *[challenger_summaries[seed] for seed in sorted(challenger_summaries)],
    ]
    for row in lane_rows:
        row.update(_metadata(source_sha, status))
    distributions = {
        "schema_version": 1,
        **_metadata(source_sha, status),
        **recomputed["distributions"],
    }
    sensitivity = {**_metadata(source_sha, status), **sensitivity}
    contract_payload = {
        "schema_version": 1,
        **_metadata(source_sha, status),
        "experiment_config": config,
        "experiment_config_sha256": _payload_sha256(config),
        "base_canary_contract": contract_check["base_canary_contract"],
        "grammar_contract_sha256": grammar.contract_sha256,
        "source_blobs": source_blobs,
    }
    result = {
        "schema_version": 1,
        **_metadata(source_sha, status),
        "experiment_id": config["experiment_id"],
        "status": status,
        "conclusion_scope": "SEARCH_INSTRUMENT_DIVERSITY_ONLY_NOT_ECONOMIC_ALPHA",
        "lane_metrics": lane_rows,
        "strict_evaluator_calls": strict_calls,
        "sealed_reads": panel.sealed_reads,
        "feedback_sensitivity_result": sensitivity["result"],
        "pooled_top16_median_feedback_distance": pooled_top_median,
        "integrity_checks": {name: "PASS" if value else "FAIL" for name, value in integrity.items()},
        "effect_checks": {name: "PASS" if value else "FAIL" for name, value in effect_checks.items()},
        "test_evidence": test_evidence,
        "boundaries": {
            "allowed_role": DATA_ROLE,
            "sealed_roles": config["boundaries"]["sealed_roles"],
            "promotion": False,
            "formal_search": False,
            "cross_sprint_memory": False,
        },
    }
    event_log = {
        "schema_version": 1,
        **_metadata(source_sha, status),
        "fresh_engine_per_seed": True,
        "sealed_reads": panel.sealed_reads,
        "runs": [runs[seed] for seed in sorted(runs)],
    }
    runtime_root.mkdir(parents=True, exist_ok=True)
    _write_json(runtime_root / RUNTIME_OUTPUTS[0], contract_payload)
    _write_json(runtime_root / RUNTIME_OUTPUTS[1], result)
    _write_csv(runtime_root / RUNTIME_OUTPUTS[2], lane_rows)
    _write_json(runtime_root / RUNTIME_OUTPUTS[3], distributions)
    _write_json(runtime_root / RUNTIME_OUTPUTS[4], sensitivity)
    _write_json(runtime_root / RUNTIME_OUTPUTS[5], baseline_binding)
    _write_json(runtime_root / RUNTIME_OUTPUTS[6], event_log)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_report_text(result), encoding="utf-8")
    manifest = _manifest_payload(
        repo_root,
        runtime_root=runtime_root,
        report_path=report_path,
        source_sha=source_sha,
        status=status,
        source_blobs=source_blobs,
    )
    _write_json(runtime_root / RUNTIME_OUTPUTS[7], manifest)
    if runtime_trace is not None:
        config_ref = config_path.relative_to(repo_root).as_posix()
        base_config_ref = str(config["base_canary_config"]["path"])
        contract_ref = (runtime_root / RUNTIME_OUTPUTS[0]).relative_to(repo_root).as_posix()
        boundary_contracts = {
            "sealed_evaluation_roles",
            "frozen_mutations",
            "explicit_boundary_authority",
            "canary_enforces_sealed_boundaries",
        }
        release_contracts = {
            "approved_existing_release_only",
            "bounded_existing_release_canary_authority",
            "canary_loads_approved_development_release",
        }
        for contract_id in sorted(GRAPH_CONTRACT_IDS):
            binding_path = (
                config_ref
                if contract_id in boundary_contracts
                else base_config_ref
                if contract_id in release_contracts
                else contract_ref
            )
            runtime_trace.bind_contract(
                contract_id, contract_id=contract_id, path=binding_path
            )
        runtime_trace.bind_contract(
            "cem_diversity_development_only",
            contract_id="cem_diversity_development_only",
            path=config_ref,
        )
        runtime_trace.bind_contract(
            "cem_diversity_non_formal_relation",
            contract_id="cem_diversity_non_formal_relation",
            path=contract_ref,
        )
        for path in sorted(runtime_root.iterdir()):
            runtime_trace.record_artifact(
                path.relative_to(repo_root).as_posix(),
                producer_component="cem_diversity_ab_experiment",
            )
        runtime_trace.record_artifact(
            report_path.relative_to(repo_root).as_posix(),
            producer_component="cem_diversity_ab_experiment",
        )
    return result


def check_evidence(repo_root: Path, *, config_path: Path) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    config = _read_json(config_path)
    errors: list[str] = []
    contract_check: dict[str, Any] = {}
    try:
        contract_check = validate_experiment_contract(repo_root, config)
    except (OSError, KeyError, TypeError, ValueError) as error:
        errors.append(f"contract:{error}")
    runtime_root = repo_root / config["outputs"]["runtime_root"]
    manifest_path = runtime_root / RUNTIME_OUTPUTS[-1]
    result_path = runtime_root / RUNTIME_OUTPUTS[1]
    event_path = runtime_root / RUNTIME_OUTPUTS[6]
    try:
        manifest = _read_json(manifest_path)
        result = _read_json(result_path)
        event_log = _read_json(event_path)
        sensitivity = _read_json(runtime_root / RUNTIME_OUTPUTS[4])
        distribution_artifact = _read_json(runtime_root / RUNTIME_OUTPUTS[3])
    except (OSError, json.JSONDecodeError, KeyError) as error:
        return {"result": "FAIL", "errors": [f"header:{error}"]}
    source_sha = str(manifest.get("source_code_sha", "")).lower()
    if result.get("status") not in VALID_STATUSES or result.get("bundle_sha256") is not None:
        errors.append("result_status_or_forbidden_bundle_hash")
    expected_identity = {
        "producer": PRODUCER,
        "source_code_sha": source_sha,
        "data_role": DATA_ROLE,
        "lifecycle": LIFECYCLE,
        "status": result.get("status"),
    }
    for name in (
        RUNTIME_OUTPUTS[0],
        RUNTIME_OUTPUTS[1],
        RUNTIME_OUTPUTS[3],
        RUNTIME_OUTPUTS[4],
        RUNTIME_OUTPUTS[5],
        RUNTIME_OUTPUTS[6],
        RUNTIME_OUTPUTS[7],
    ):
        try:
            payload = _read_json(runtime_root / name)
        except (OSError, json.JSONDecodeError):
            errors.append(f"artifact_payload:{name}")
            continue
        if any(payload.get(key) != value for key, value in expected_identity.items()):
            errors.append(f"artifact_payload_identity:{name}")
    try:
        subprocess.check_call(
            ["git", "merge-base", "--is-ancestor", source_sha, "HEAD"],
            cwd=repo_root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        source_blobs = _experiment_source_blobs(repo_root, source_sha)
        if source_blobs != manifest.get("source_blobs"):
            errors.append("source_blobs")
    except (OSError, RuntimeError, subprocess.CalledProcessError):
        errors.append("source_authority")
    observed_records: list[dict[str, Any]] = []
    for record in manifest.get("artifacts", []):
        if any(
            record.get(name) != expected
            for name, expected in expected_identity.items()
        ):
            errors.append(f"artifact_identity:{record.get('path')}")
        path = (repo_root / str(record.get("path", ""))).resolve()
        try:
            path.relative_to(repo_root)
        except ValueError:
            errors.append("artifact_outside_repo")
            continue
        if not path.is_file():
            errors.append(f"missing:{record.get('path')}")
            continue
        observed = dict(record)
        if (
            path.stat().st_size != int(record.get("bytes", -1))
            or sha256_file(path) != record.get("content_sha256")
        ):
            errors.append(f"hash:{record.get('path')}")
        observed_records.append(observed)
    expected_paths = sorted(
        [
            (runtime_root / name).relative_to(repo_root).as_posix()
            for name in RUNTIME_OUTPUTS[:-1]
        ]
        + [(repo_root / config["outputs"]["report"]).relative_to(repo_root).as_posix()]
    )
    if sorted(record["path"] for record in observed_records) != expected_paths:
        errors.append("artifact_set")
    if _payload_sha256(observed_records) != manifest.get("bundle_sha256"):
        errors.append("bundle_sha256")
    if manifest.get("manifest_self_excluded") is not True:
        errors.append("manifest_self_exclusion")
    baseline_lanes: dict[int, list[dict[str, Any]]] = {}
    try:
        binding, baseline_lanes = load_baseline_binding(
            repo_root, config, source_sha=source_sha
        )
        binding.update(_metadata(source_sha, str(result.get("status"))))
        if binding != _read_json(runtime_root / RUNTIME_OUTPUTS[5]):
            errors.append("baseline_binding")
    except (OSError, KeyError, TypeError, ValueError, subprocess.CalledProcessError):
        errors.append("baseline_binding_verification")
    try:
        raw_runs = list(event_log["runs"])
        raw_seeds = [int(run["seed"]) for run in raw_runs]
        if (
            len(raw_runs) != 2
            or len(set(raw_seeds)) != len(raw_seeds)
            or set(raw_seeds) != {20260715, 20260716}
        ):
            raise ValueError("event log run identities do not match the frozen lanes")
        runs = {int(run["seed"]): dict(run) for run in raw_runs}
        observed_tests = _run_tests(repo_root)
        if any(
            observed_tests.get(name) != result.get("test_evidence", {}).get(name)
            for name in ("result", "new_tests", "passed")
        ):
            errors.append("test_evidence")
        recomputed = _recompute_runtime_core(
            config,
            baseline_lanes=baseline_lanes,
            runs=runs,
            sealed_reads=int(event_log["sealed_reads"]),
            test_evidence=observed_tests,
        )
        replay = recomputed["sensitivity"]
        persisted_core = {
            key: sensitivity[key]
            for key in ("schema_version", "scope", "neutral_feedback", "lanes", "result")
        }
        if replay != persisted_core:
            errors.append("feedback_sensitivity_replay")
        expected_lane_rows = [
            *[
                recomputed["baseline_summaries"][seed]
                for seed in sorted(recomputed["baseline_summaries"])
            ],
            *[
                recomputed["challenger_summaries"][seed]
                for seed in sorted(recomputed["challenger_summaries"])
            ],
        ]
        for row in expected_lane_rows:
            row.update(_metadata(source_sha, recomputed["status"]))
        lane_path = runtime_root / RUNTIME_OUTPUTS[2]
        with lane_path.open(newline="", encoding="utf-8") as handle:
            persisted_lane_rows = list(csv.DictReader(handle))
        columns: list[str] = []
        for row in expected_lane_rows:
            for name in row:
                if name not in columns:
                    columns.append(name)
        expected_csv_rows = [
            {
                name: str(_csv_value(row.get(name)))
                for name in columns
            }
            for row in expected_lane_rows
        ]
        if persisted_lane_rows != expected_csv_rows:
            errors.append("lane_metrics_semantic_recomputation")
        expected_result_core = {
            "schema_version": 1,
            "experiment_id": config["experiment_id"],
            "status": recomputed["status"],
            "conclusion_scope": "SEARCH_INSTRUMENT_DIVERSITY_ONLY_NOT_ECONOMIC_ALPHA",
            "lane_metrics": expected_lane_rows,
            "strict_evaluator_calls": recomputed["strict_evaluator_calls"],
            "sealed_reads": int(event_log["sealed_reads"]),
            "feedback_sensitivity_result": replay["result"],
            "pooled_top16_median_feedback_distance": recomputed[
                "pooled_top16_median_feedback_distance"
            ],
            "integrity_checks": {
                name: "PASS" if value else "FAIL"
                for name, value in recomputed["integrity_checks"].items()
            },
            "effect_checks": {
                name: "PASS" if value else "FAIL"
                for name, value in recomputed["effect_checks"].items()
            },
            "boundaries": {
                "allowed_role": DATA_ROLE,
                "sealed_roles": config["boundaries"]["sealed_roles"],
                "promotion": False,
                "formal_search": False,
                "cross_sprint_memory": False,
            },
        }
        if any(result.get(name) != value for name, value in expected_result_core.items()):
            errors.append("result_semantic_recomputation")
        persisted_distribution_core = {
            "lanes": distribution_artifact.get("lanes"),
            "cross_seed": distribution_artifact.get("cross_seed"),
        }
        if persisted_distribution_core != recomputed["distributions"]:
            errors.append("distribution_semantic_recomputation")
        if (
            event_log.get("fresh_engine_per_seed") is not True
            or int(event_log.get("sealed_reads", -1)) != int(result.get("sealed_reads", -2))
        ):
            errors.append("runtime_event_contract")
        contract_artifact = _read_json(runtime_root / RUNTIME_OUTPUTS[0])
        if (
            contract_artifact.get("schema_version") != 1
            or contract_artifact.get("experiment_config") != config
            or contract_artifact.get("experiment_config_sha256")
            != _payload_sha256(config)
            or contract_artifact.get("base_canary_contract")
            != contract_check.get("base_canary_contract")
            or contract_artifact.get("grammar_contract_sha256")
            != FrozenGrammar.default().contract_sha256
            or contract_artifact.get("source_blobs") != source_blobs
        ):
            errors.append("contract_semantic_recomputation")
        report_path = repo_root / config["outputs"]["report"]
        if report_path.read_text(encoding="utf-8") != _report_text(result):
            errors.append("report_semantic_recomputation")
    except Exception as error:  # fail closed on any malformed persisted runtime payload
        errors.append(f"runtime_replay:{type(error).__name__}")
    return {
        "result": "PASS" if not errors else "FAIL",
        "errors": errors,
        "status": result.get("status"),
        "artifact_count": len(observed_records),
        "bundle_sha256": manifest.get("bundle_sha256"),
    }


__all__ = [
    "INVALID",
    "MIXED",
    "NO_IMPROVEMENT",
    "QUALIFIED",
    "RUNTIME_OUTPUTS",
    "build_evidence",
    "check_evidence",
    "feedback_sensitivity_replay",
    "load_baseline_binding",
    "validate_experiment_contract",
]
