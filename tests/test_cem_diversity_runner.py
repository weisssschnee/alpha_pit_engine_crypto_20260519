from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from alphafactory_crypto.instrument_canary.cem_diversity import CEMDiversityV2Policy
from alphafactory_crypto.instrument_canary.cem_diversity_runner import (
    INVALID,
    MIXED,
    NO_IMPROVEMENT,
    QUALIFIED,
    _cache_reuse_is_completed,
    _decision,
    _lane_summary,
    _recompute_runtime_core,
    _top_unique,
    feedback_sensitivity_replay,
    load_baseline_binding,
    validate_experiment_contract,
)
from alphafactory_crypto.instrument_canary.contracts import SearchState
from alphafactory_crypto.instrument_canary.engine import CandidateFeedback
from alphafactory_crypto.instrument_canary.grammar import FrozenGrammar


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "config" / "crypto_cem_diversity_ab_v1.json"


def _config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def _feedback(candidate_id: str, score: float) -> CandidateFeedback:
    return CandidateFeedback(
        candidate_id=candidate_id,
        blocked=False,
        feasible=False,
        violations=(),
        distance=score,
        sort_key=(1, 0, 0, score, score, score, score, score, score, score, score, score, score),
        reason="TEST",
    )


def _policy_ledger(seed: int, scores: list[float]) -> list[dict]:
    policy = CEMDiversityV2Policy(FrozenGrammar.default(), seed)
    rows: list[dict] = []
    for step, score in enumerate(scores):
        proposal = policy.propose(SearchState(step, len(scores) - step))
        feedback = _feedback(proposal.candidate_id, score)
        policy.update(proposal, feedback)
        rows.append(
            {
                "lane_id": f"cem_diversity_v2:seed={seed}",
                "algorithm": "cem_diversity_v2",
                "seed": seed,
                "step": step,
                "candidate_id": proposal.candidate_id,
                "feedback_blocked": feedback.blocked,
                "feedback_feasible": feedback.feasible,
                "feedback_violations": list(feedback.violations),
                "feedback_distance": feedback.distance,
                "feedback_sort_key": list(feedback.sort_key),
                "feedback_reason": feedback.reason,
                "policy_state_after_update": policy.state_hash(),
            }
        )
    return rows


def test_experiment_contract_reuses_exact_frozen_canary() -> None:
    result = validate_experiment_contract(REPO_ROOT, _config())
    assert result["result"] == "PASS"
    assert result["grammar_support_size"] == 9576
    assert result["base_canary_contract"]["formal_proposals"] == 1024


def test_baseline_is_loaded_from_immutable_closure_with_policy_local_counts() -> None:
    binding, lanes = load_baseline_binding(REPO_ROOT, _config(), source_sha="test-source")
    expected = _config()["baseline"].get(
        "checkout_artifact_sha256", _config()["baseline"].get("artifact_sha256")
    )
    assert binding["checkout_artifact_sha256"] == expected
    assert binding["status"] == "PENDING"
    assert binding["validation_result"] == "PASS"
    assert len({row["candidate_id"] for row in lanes[20260715]}) == 39
    assert len({row["candidate_id"] for row in lanes[20260716]}) == 66
    assert binding["pooled_unique_candidate_top16_median_feedback_distance"] == (
        _config()["comparison"]["baseline_unique_candidate_top16_median_feedback_distance"]
    )


def test_lane_summary_distinguishes_policy_repeats_from_global_cache_hits() -> None:
    _, lanes = load_baseline_binding(REPO_ROOT, _config(), source_sha="test-source")
    first = _lane_summary(lanes[20260715], variant="baseline")
    second = _lane_summary(lanes[20260716], variant="baseline")
    assert (first["unique_candidate_ids"], first["first_evaluations"]) == (39, 38)
    assert (first["within_lane_repeated_candidate_count"], first["exact_cache_hits"]) == (89, 90)
    assert (second["unique_candidate_ids"], second["first_evaluations"]) == (66, 58)
    assert (second["within_lane_repeated_candidate_count"], second["exact_cache_hits"]) == (62, 70)


def test_neutral_policy_only_replay_starts_at_update_zero_and_diverges_after_warmup() -> None:
    scores = [float(value) for value in range(24)]
    lanes = {
        20260715: _policy_ledger(20260715, scores),
        20260716: _policy_ledger(20260716, scores),
    }
    result = feedback_sensitivity_replay(FrozenGrammar.default(), lanes, _config())
    assert result["result"] == "PASS"
    assert result["neutral_feedback"]["applied_from_update_ordinal"] == 0
    assert all(row["first_warmup_proposals_equal"] for row in result["lanes"])
    assert all(row["post_warmup_transcript_diverged"] for row in result["lanes"])
    assert all(row["evaluator_calls"] == 0 for row in result["lanes"])


def test_cache_hit_requires_an_earlier_completed_exact_observation() -> None:
    first = {
        "step": 0, "cache_key": "same", "cache_hit": False, "evaluation_executed": True
    }
    hit = {
        "step": 1, "cache_key": "same", "cache_hit": True, "evaluation_executed": False
    }
    assert _cache_reuse_is_completed([first, hit])
    assert not _cache_reuse_is_completed([hit])
    assert not _cache_reuse_is_completed([first, {**hit, "evaluation_executed": True}])


def _summaries(unique15: int, unique16: int, repeats15: int, repeats16: int):
    baseline = {
        20260715: {"within_lane_repeated_candidate_count": 89},
        20260716: {"within_lane_repeated_candidate_count": 62},
    }
    challenger = {
        20260715: {"first_evaluations": unique15, "within_lane_repeated_candidate_count": repeats15},
        20260716: {"first_evaluations": unique16, "within_lane_repeated_candidate_count": repeats16},
    }
    return baseline, challenger


def test_decision_precedence_is_invalid_then_qualified_mixed_no_improvement() -> None:
    config = _config()
    baseline, challenger = _summaries(100, 100, 28, 28)
    good_integrity = {"runtime": True}
    assert _decision(
        config, baseline, challenger, integrity_checks={"runtime": False},
        sensitivity_pass=True, top16_median=0.0,
    )[0] == INVALID
    assert _decision(
        config, baseline, challenger, integrity_checks=good_integrity,
        sensitivity_pass=True, top16_median=0.0,
    )[0] == QUALIFIED
    baseline, challenger = _summaries(60, 70, 40, 40)
    assert _decision(
        config, baseline, challenger, integrity_checks=good_integrity,
        sensitivity_pass=True, top16_median=-2.0,
    )[0] == MIXED
    baseline, challenger = _summaries(40, 60, 88, 61)
    assert _decision(
        config, baseline, challenger, integrity_checks=good_integrity,
        sensitivity_pass=False, top16_median=0.0,
    )[0] == NO_IMPROVEMENT


@pytest.mark.parametrize(
    ("section", "name", "value"),
    [
        ("challenger", "branch_draws_per_proposal", 2),
        ("challenger", "feedback_warmup_steps", 9),
        ("challenger", "global_hard_cap", 4096),
        ("comparison", "feedback_distance_noninferiority_floor", -99.0),
        ("outputs", "runtime_root", "runtime/relaxed"),
    ],
)
def test_contract_rejects_preregistered_field_tampering(
    section: str, name: str, value: object
) -> None:
    config = deepcopy(_config())
    config[section][name] = value
    with pytest.raises(ValueError, match="drift"):
        validate_experiment_contract(REPO_ROOT, config)


def test_contract_rejects_baseline_and_neutral_feedback_tampering() -> None:
    baseline = deepcopy(_config())
    baseline["baseline"]["matched_policy_local"]["20260716"]["unique_candidates"] = 67
    with pytest.raises(ValueError, match="baseline authority drift"):
        validate_experiment_contract(REPO_ROOT, baseline)
    neutral = deepcopy(_config())
    neutral["challenger"]["neutral_feedback"]["applied_from_update_ordinal"] = 8
    with pytest.raises(ValueError, match="neutral feedback contract drift"):
        validate_experiment_contract(REPO_ROOT, neutral)


def test_pooled_top16_globally_deduplicates_cross_seed_candidate_identity() -> None:
    rows = [
        {"candidate_id": "shared", "feedback_sort_key": [2.0], "feedback_distance": 2.0},
        {"candidate_id": "shared", "feedback_sort_key": [2.0], "feedback_distance": 2.0},
        {"candidate_id": "other", "feedback_sort_key": [1.0], "feedback_distance": 1.0},
    ]
    top = _top_unique(rows, 16)
    assert [row["candidate_id"] for row in top] == ["shared", "other"]


def test_runtime_recomputation_fails_closed_on_strict_call_tamper(monkeypatch) -> None:
    rows = {
        seed: [
            {
                "seed": seed,
                "algorithm": "cem_diversity_v2",
                "lane_id": f"cem_diversity_v2:seed={seed}",
                "step": ordinal,
                "proposal_ordinal": ordinal,
                "candidate_id": f"{seed}-{ordinal}",
                "feedback_distance": 0.0,
            }
            for ordinal in range(128)
        ]
        for seed in (20260715, 20260716)
    }
    runs = {
        seed: {
            "seed": seed,
            "ledger": lane,
            "policy_diagnostics": [
                {
                    "ordinal": ordinal,
                    "candidate_id": row["candidate_id"],
                }
                for ordinal, row in enumerate(lane)
            ],
            "strict_evaluator_calls": 128,
            "first_evaluations": 128,
            "fresh_cache": True,
            "events": [
                {"event_type": "VISITED_FEEDBACK_EXPOSED"}
                for _ in range(128)
            ],
            "numeric_unique_inputs": 128,
            "numeric_alias_observations": 0,
            "behavior_hash": "hash",
        }
        for seed, lane in rows.items()
    }
    monkeypatch.setattr(
        "alphafactory_crypto.instrument_canary.cem_diversity_runner.feedback_sensitivity_replay",
        lambda *_args, **_kwargs: {
            "result": "PASS",
            "lanes": [
                {"seed": seed, "real_replay_result": "PASS", "real_transcript_sha256": "hash"}
                for seed in rows
            ],
        },
    )
    monkeypatch.setattr(
        "alphafactory_crypto.instrument_canary.cem_diversity_runner._lane_summary",
        lambda lane, variant, **_kwargs: {
            "variant": variant,
            "seed": int(lane[0]["seed"]),
            "first_evaluations": 100,
            "within_lane_repeated_candidate_count": 20,
        },
    )
    for name in (
        "_cache_reuse_is_completed", "_ledger_contract_pass",
        "_numeric_alias_integrity",
    ):
        monkeypatch.setattr(
            f"alphafactory_crypto.instrument_canary.cem_diversity_runner.{name}",
            lambda *_args, **_kwargs: True,
        )
    monkeypatch.setattr(
        "alphafactory_crypto.instrument_canary.cem_diversity_runner._feedback_alignment",
        lambda *_args, **_kwargs: (True, {}),
    )
    monkeypatch.setattr(
        "alphafactory_crypto.instrument_canary.cem_diversity_runner._top_unique",
        lambda *_args, **_kwargs: [{"feedback_distance": 0.0}],
    )
    monkeypatch.setattr(
        "alphafactory_crypto.instrument_canary.cem_diversity_runner._distribution_metrics",
        lambda *_args, **_kwargs: {
            "mechanism_family": {"counts": {}}, "primitive": {"counts": {}}
        },
    )
    monkeypatch.setattr(
        "alphafactory_crypto.instrument_canary.cem_diversity_runner._cross_seed_metrics",
        lambda *_args, **_kwargs: {},
    )
    baseline = {
        seed: [{"seed": seed, "candidate_id": f"base-{seed}", "feedback_distance": 0.0}]
        for seed in rows
    }
    tests = {"result": "PASS", "passed": 1, "new_tests": 1}
    good = _recompute_runtime_core(
        _config(), baseline_lanes=baseline, runs=runs, sealed_reads=0, test_evidence=tests
    )
    assert good["integrity_checks"]["exact_lane_shape"] is True
    assert good["integrity_checks"]["strict_evaluator_every_first_visit"] is True
    tampered = deepcopy(runs)
    tampered[20260716]["strict_evaluator_calls"] = 127
    bad = _recompute_runtime_core(
        _config(), baseline_lanes=baseline, runs=tampered, sealed_reads=0, test_evidence=tests
    )
    assert bad["integrity_checks"]["strict_evaluator_every_first_visit"] is False
    assert bad["status"] == INVALID


def test_runtime_recomputation_rejects_truncated_lane_shape(monkeypatch) -> None:
    # Reuse the preceding test's fail-closed surface with the cheapest possible
    # malformed payload: neither lane reaches the frozen 128-proposal shape.
    monkeypatch.setattr(
        "alphafactory_crypto.instrument_canary.cem_diversity_runner.feedback_sensitivity_replay",
        lambda *_args, **_kwargs: {"result": "FAIL", "lanes": []},
    )
    monkeypatch.setattr(
        "alphafactory_crypto.instrument_canary.cem_diversity_runner._lane_summary",
        lambda lane, variant, **_kwargs: {
            "variant": variant,
            "seed": int(lane[0]["seed"]),
            "first_evaluations": 1,
            "within_lane_repeated_candidate_count": 0,
        },
    )
    monkeypatch.setattr(
        "alphafactory_crypto.instrument_canary.cem_diversity_runner._top_unique",
        lambda *_args, **_kwargs: [{"feedback_distance": 0.0}],
    )
    monkeypatch.setattr(
        "alphafactory_crypto.instrument_canary.cem_diversity_runner._distribution_metrics",
        lambda *_args, **_kwargs: {
            "mechanism_family": {"counts": {}}, "primitive": {"counts": {}}
        },
    )
    monkeypatch.setattr(
        "alphafactory_crypto.instrument_canary.cem_diversity_runner._cross_seed_metrics",
        lambda *_args, **_kwargs: {},
    )
    for name in (
        "_cache_reuse_is_completed",
        "_ledger_contract_pass",
        "_numeric_alias_integrity",
    ):
        monkeypatch.setattr(
            f"alphafactory_crypto.instrument_canary.cem_diversity_runner.{name}",
            lambda *_args, **_kwargs: True,
        )
    monkeypatch.setattr(
        "alphafactory_crypto.instrument_canary.cem_diversity_runner._feedback_alignment",
        lambda *_args, **_kwargs: (True, {}),
    )
    runs = {
        seed: {
            "seed": seed,
            "ledger": [{"seed": seed, "candidate_id": str(seed), "step": 0}],
            "policy_diagnostics": [],
            "strict_evaluator_calls": 0,
            "first_evaluations": 0,
            "fresh_cache": True,
            "events": [],
            "numeric_unique_inputs": 0,
            "numeric_alias_observations": 0,
            "behavior_hash": "",
        }
        for seed in (20260715, 20260716)
    }
    baseline = {
        seed: [{"seed": seed, "candidate_id": f"base-{seed}"}]
        for seed in runs
    }
    result = _recompute_runtime_core(
        _config(),
        baseline_lanes=baseline,
        runs=runs,
        sealed_reads=0,
        test_evidence={"result": "PASS", "new_tests": 1, "passed": 1},
    )
    assert result["integrity_checks"]["exact_lane_shape"] is False
    assert result["integrity_checks"]["proposal_budget"] is False
    assert result["status"] == INVALID
