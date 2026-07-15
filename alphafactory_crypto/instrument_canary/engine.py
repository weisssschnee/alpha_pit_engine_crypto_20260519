"""Event-ordered lazy search engine for the bounded real-data canary.

The engine knows nothing about market arrays.  It accepts a fail-closed
authorizer and a first-visit evaluator, keeps the run-local cache private, and
exposes feedback to a policy only after that policy has proposed the candidate.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Callable, Mapping, Sequence

from .contracts import Proposal, SearchState, canonical_json_bytes
from .grammar import FrozenGrammar
from .policies import SearchPolicy, build_policy


Authorizer = Callable[[Proposal], Any]
FirstVisitEvaluator = Callable[[Any], "CandidateObservation"]
PolicyFactory = Callable[[str, FrozenGrammar, int], SearchPolicy]


def _value(value: Any, name: str, default: Any = None) -> Any:
    if isinstance(value, Mapping):
        return value.get(name, default)
    return getattr(value, name, default)


def _receipt_dict(receipt: Any) -> dict[str, Any]:
    if hasattr(receipt, "to_dict"):
        payload = receipt.to_dict()
    elif isinstance(receipt, Mapping):
        payload = dict(receipt)
    else:
        raise TypeError("authorization receipt must expose to_dict or Mapping")
    if not isinstance(payload, Mapping):
        raise TypeError("authorization receipt serialization must be a mapping")
    return dict(payload)


def _feedback_payload(feedback: Any) -> dict[str, Any]:
    sort_key = _value(feedback, "sort_key")
    if not isinstance(sort_key, Sequence) or isinstance(sort_key, (str, bytes)):
        raise TypeError("feedback must expose a sequence sort_key")
    return {
        "blocked": bool(_value(feedback, "blocked")),
        "feasible": bool(_value(feedback, "feasible")),
        "violations": list(_value(feedback, "violations", ())),
        "distance": float(_value(feedback, "distance")),
        "sort_key": list(sort_key),
        "reason": str(_value(feedback, "reason", "")),
    }


@dataclass(frozen=True, slots=True)
class CandidateObservation:
    """Evaluation result cached under one fully qualified authorization key."""

    feedback: Any
    evidence: Mapping[str, Any]

    def __post_init__(self) -> None:
        _feedback_payload(self.feedback)
        if not isinstance(self.evidence, Mapping):
            raise TypeError("candidate evidence must be a mapping")


@dataclass(frozen=True, slots=True)
class CandidateFeedback:
    """Proposal-bound strict feedback; economic arrays never reach a policy."""

    candidate_id: str
    blocked: bool
    feasible: bool
    violations: tuple[str, ...]
    distance: float
    sort_key: tuple[int | float, ...]
    reason: str

    @classmethod
    def bind(cls, candidate_id: str, feedback: Any) -> "CandidateFeedback":
        existing = _value(feedback, "candidate_id")
        if existing is not None and str(existing) != str(candidate_id):
            raise ValueError("feedback candidate identity mismatch")
        payload = _feedback_payload(feedback)
        return cls(
            candidate_id=str(candidate_id),
            blocked=bool(payload["blocked"]),
            feasible=bool(payload["feasible"]),
            violations=tuple(str(value) for value in payload.get("violations", ())),
            distance=float(payload["distance"]),
            sort_key=tuple(payload["sort_key"]),
            reason=str(payload.get("reason", "")),
        )

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "CandidateFeedback":
        return cls(
            candidate_id=str(payload["candidate_id"]),
            blocked=bool(payload["blocked"]),
            feasible=bool(payload["feasible"]),
            violations=tuple(str(value) for value in payload.get("violations", ())),
            distance=float(payload["distance"]),
            sort_key=tuple(payload["sort_key"]),
            reason=str(payload.get("reason", "")),
        )


@dataclass(frozen=True, slots=True)
class LazySearchResult:
    ledger: tuple[dict[str, Any], ...]
    events: tuple[dict[str, Any], ...]
    authorization_receipts: tuple[dict[str, Any], ...]
    proposals: int
    first_evaluations: int
    cache_hits: int
    cache_size: int
    behavior_hashes: Mapping[str, str]
    lane_state_hashes: Mapping[str, str]


@dataclass(frozen=True, slots=True)
class _CacheEntry:
    observation: CandidateObservation
    first_evaluation_sequence: int
    first_lane_id: str


class LazySearchEngine:
    """Run fixed lanes against a private global first-visit cache."""

    def __init__(
        self,
        grammar: FrozenGrammar,
        *,
        authorizer: Authorizer,
        first_visit_evaluator: FirstVisitEvaluator,
        first_evaluation_hard_cap: int,
        already_consumed_first_evaluations: int = 0,
        policy_factory: PolicyFactory = build_policy,
    ) -> None:
        if not isinstance(grammar, FrozenGrammar):
            raise TypeError("LazySearchEngine requires FrozenGrammar")
        if first_evaluation_hard_cap <= 0:
            raise ValueError("first-evaluation hard cap must be positive")
        if not 0 <= already_consumed_first_evaluations <= first_evaluation_hard_cap:
            raise ValueError("already-consumed first evaluations exceed hard cap")
        self.grammar = grammar
        self._authorizer = authorizer
        self._first_visit_evaluator = first_visit_evaluator
        self._hard_cap = int(first_evaluation_hard_cap)
        self._already_consumed = int(already_consumed_first_evaluations)
        self._policy_factory = policy_factory
        self._cache: dict[str, _CacheEntry] = {}
        self._events: list[dict[str, Any]] = []
        self._event_sequence = 0
        self._run_started = False

    def _event(self, event_type: str, **payload: Any) -> int:
        self._event_sequence += 1
        self._events.append(
            {"sequence": self._event_sequence, "event_type": event_type, **payload}
        )
        return self._event_sequence

    def run(
        self,
        *,
        algorithms: Sequence[str],
        seeds: Sequence[int],
        steps_per_lane: int,
    ) -> LazySearchResult:
        if self._run_started:
            raise RuntimeError("LazySearchEngine is single-use; create a new bounded run")
        self._run_started = True
        if steps_per_lane <= 0:
            raise ValueError("steps_per_lane must be positive")
        if not algorithms or not seeds:
            raise ValueError("at least one algorithm and seed are required")

        ledger: list[dict[str, Any]] = []
        receipts_by_cache_key: dict[str, dict[str, Any]] = {}
        behavior_hashes: dict[str, str] = {}
        lane_state_hashes: dict[str, str] = {}
        first_evaluations = 0
        cache_hits = 0

        # The order is part of the frozen contract: seed ascending, then the
        # caller-provided algorithm order.
        for seed in sorted(int(value) for value in seeds):
            for algorithm in algorithms:
                lane_id = f"{algorithm}:seed={seed}"
                policy = self._policy_factory(str(algorithm), self.grammar, seed)
                lane_candidate_ids: list[str] = []
                for step in range(steps_per_lane):
                    state_before = policy.state_hash()
                    proposal_sequence = self._event(
                        "PROPOSAL_CREATED",
                        lane_id=lane_id,
                        step=step,
                    )
                    proposal = policy.propose(
                        SearchState(step=step, remaining_budget=steps_per_lane - step)
                    )
                    lane_candidate_ids.append(proposal.candidate_id)
                    proposed_state = policy.state_hash()
                    authorization_sequence = self._event(
                        "CANDIDATE_AUTHORIZATION_STARTED",
                        lane_id=lane_id,
                        step=step,
                        candidate_id=proposal.candidate_id,
                    )
                    receipt = self._authorizer(proposal)
                    receipt_payload = _receipt_dict(receipt)
                    receipt_candidate_id = str(
                        _value(receipt, "candidate_id", receipt_payload.get("candidate_id", ""))
                    )
                    if receipt_candidate_id != proposal.candidate_id:
                        raise ValueError("authorization receipt candidate identity mismatch")
                    cache_key = str(
                        _value(receipt, "cache_key", receipt_payload.get("cache_key", ""))
                    )
                    if not cache_key:
                        raise ValueError("authorization receipt lacks cache_key")
                    receipts_by_cache_key.setdefault(cache_key, receipt_payload)
                    authorized_sequence = self._event(
                        "CANDIDATE_AUTHORIZED",
                        lane_id=lane_id,
                        step=step,
                        candidate_id=proposal.candidate_id,
                        cache_key=cache_key,
                    )

                    lookup_sequence = self._event(
                        "RUN_CACHE_LOOKUP",
                        lane_id=lane_id,
                        step=step,
                        candidate_id=proposal.candidate_id,
                        cache_key=cache_key,
                    )
                    cache_hit = cache_key in self._cache
                    evaluation_sequence: int | None = None
                    if cache_hit:
                        cache_hits += 1
                        entry = self._cache[cache_key]
                        observation = entry.observation
                        self._event(
                            "RUN_CACHE_HIT",
                            lane_id=lane_id,
                            step=step,
                            candidate_id=proposal.candidate_id,
                            cache_key=cache_key,
                            first_evaluation_sequence=entry.first_evaluation_sequence,
                        )
                    else:
                        total_if_evaluated = (
                            self._already_consumed + first_evaluations + 1
                        )
                        if total_if_evaluated > self._hard_cap:
                            raise RuntimeError("first-evaluation hard cap would be exceeded")
                        evaluation_started = self._event(
                            "FIRST_VISIT_EVALUATION_STARTED",
                            lane_id=lane_id,
                            step=step,
                            candidate_id=proposal.candidate_id,
                            cache_key=cache_key,
                        )
                        observation = self._first_visit_evaluator(receipt)
                        if not isinstance(observation, CandidateObservation):
                            raise TypeError(
                                "first-visit evaluator must return CandidateObservation"
                            )
                        evaluation_sequence = self._event(
                            "FIRST_VISIT_EVALUATION_COMPLETED",
                            lane_id=lane_id,
                            step=step,
                            candidate_id=proposal.candidate_id,
                            cache_key=cache_key,
                            started_sequence=evaluation_started,
                        )
                        self._cache[cache_key] = _CacheEntry(
                            observation=observation,
                            first_evaluation_sequence=evaluation_sequence,
                            first_lane_id=lane_id,
                        )
                        first_evaluations += 1

                    bound_feedback = CandidateFeedback.bind(
                        proposal.candidate_id, observation.feedback
                    )
                    feedback_payload = _feedback_payload(bound_feedback)
                    feedback_sequence = self._event(
                        "VISITED_FEEDBACK_EXPOSED",
                        lane_id=lane_id,
                        step=step,
                        candidate_id=proposal.candidate_id,
                        cache_hit=cache_hit,
                    )
                    policy.update(proposal, bound_feedback)
                    update_sequence = self._event(
                        "POLICY_UPDATED",
                        lane_id=lane_id,
                        step=step,
                        candidate_id=proposal.candidate_id,
                    )
                    state_after = policy.state_hash()
                    cache_entry = self._cache[cache_key]
                    core_row = {
                            "lane_id": lane_id,
                            "seed": seed,
                            "algorithm": str(algorithm),
                            "step": step,
                            "proposal_ordinal": proposal.ordinal,
                            "candidate_id": proposal.candidate_id,
                            "cache_key": cache_key,
                            "cache_hit": cache_hit,
                            "first_evaluation": not cache_hit,
                            "first_evaluation_lane_id": cache_entry.first_lane_id,
                            "proposal_sequence": proposal_sequence,
                            "authorization_started_sequence": authorization_sequence,
                            "authorized_sequence": authorized_sequence,
                            "cache_lookup_sequence": lookup_sequence,
                            "evaluation_sequence": evaluation_sequence,
                            "first_evaluation_sequence": cache_entry.first_evaluation_sequence,
                            "feedback_sequence": feedback_sequence,
                            "policy_update_sequence": update_sequence,
                            "feedback_exposed": True,
                            "policy_state_before_proposal": state_before,
                            "policy_state_after_proposal": proposed_state,
                            "policy_state_after_update": state_after,
                            "parent_id": proposal.parent_id,
                            "mutation_receipt": (
                                json.dumps(
                                    proposal.mutation_receipt.to_dict(),
                                    sort_keys=True,
                                    separators=(",", ":"),
                                )
                                if proposal.mutation_receipt is not None
                                else ""
                            ),
                            **{f"feedback_{key}": value for key, value in feedback_payload.items()},
                        }
                    evidence_payload = dict(observation.evidence)
                    collisions = set(core_row).intersection(evidence_payload)
                    if collisions:
                        raise ValueError(
                            "candidate evidence attempted to overwrite ledger authority: "
                            + ",".join(sorted(collisions))
                        )
                    ledger.append({**core_row, **evidence_payload})

                transcript_sha = hashlib.sha256(
                    canonical_json_bytes(
                        {
                            "lane_id": lane_id,
                            "candidate_ids": lane_candidate_ids,
                            "policy_state_hash": policy.state_hash(),
                        }
                    )
                ).hexdigest().upper()
                behavior_hashes[lane_id] = transcript_sha
                lane_state_hashes[lane_id] = policy.state_hash()

        return LazySearchResult(
            ledger=tuple(ledger),
            events=tuple(self._events),
            authorization_receipts=tuple(receipts_by_cache_key.values()),
            proposals=len(ledger),
            first_evaluations=first_evaluations,
            cache_hits=cache_hits,
            cache_size=len(self._cache),
            behavior_hashes=behavior_hashes,
            lane_state_hashes=lane_state_hashes,
        )


def replay_policy_transcript(
    grammar: FrozenGrammar,
    *,
    algorithm: str,
    seed: int,
    ledger_rows: Sequence[Mapping[str, Any]],
    policy_factory: PolicyFactory = build_policy,
) -> dict[str, Any]:
    """Replay one lane without market data and verify proposal/update identity."""

    rows = sorted(ledger_rows, key=lambda row: int(row["step"]))
    policy = policy_factory(algorithm, grammar, int(seed))
    candidate_ids: list[str] = []
    for expected_step, row in enumerate(rows):
        if int(row["step"]) != expected_step:
            raise ValueError("transcript steps are not contiguous from zero")
        proposal = policy.propose(
            SearchState(expected_step, len(rows) - expected_step)
        )
        if proposal.candidate_id != row["candidate_id"]:
            raise ValueError("policy replay candidate identity mismatch")
        feedback = CandidateFeedback.from_payload(
            {
                "candidate_id": row["candidate_id"],
                "blocked": row["feedback_blocked"],
                "feasible": row["feedback_feasible"],
                "violations": row.get("feedback_violations", ()),
                "distance": row["feedback_distance"],
                "sort_key": row["feedback_sort_key"],
                "reason": row.get("feedback_reason", ""),
            }
        )
        policy.update(proposal, feedback)
        if policy.state_hash() != row["policy_state_after_update"]:
            raise ValueError("policy replay state hash mismatch")
        candidate_ids.append(proposal.candidate_id)
    return {
        "lane_id": f"{algorithm}:seed={int(seed)}",
        "proposals": len(rows),
        "candidate_ids_sha256": hashlib.sha256(
            "\n".join(candidate_ids).encode("utf-8")
        ).hexdigest().upper(),
        "final_policy_state_sha256": policy.state_hash(),
        "result": "PASS",
    }


__all__ = [
    "CandidateObservation",
    "CandidateFeedback",
    "LazySearchEngine",
    "LazySearchResult",
    "replay_policy_transcript",
]
