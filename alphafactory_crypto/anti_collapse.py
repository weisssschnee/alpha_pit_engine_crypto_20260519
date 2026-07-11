from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import asdict, dataclass
from typing import Iterable


@dataclass(frozen=True)
class CandidateEnvelope:
    candidate_id: str
    exact_identity: str
    behaviour_cluster: str
    economic_hypothesis: str
    parent_identity: str
    family_id: str
    lane_id: str
    proposal_ordinal: int
    is_fresh: bool
    lineage_namespace: str
    memory_source: str = "NONE"


@dataclass(frozen=True)
class AdmissionPolicy:
    total_quota: int
    behaviour_cluster_quota: int
    economic_hypothesis_quota: int
    parent_descendant_cap: int
    family_budget_cap: int
    fresh_budget_floor: int
    no_memory: bool = True
    top_cluster_exile: str | None = None
    global_top_k_baseline_enabled: bool = False


@dataclass(frozen=True)
class AdmissionResult:
    admitted: tuple[CandidateEnvelope, ...]
    rejected: tuple[tuple[str, str], ...]
    semantic_volume: dict[str, dict[str, int]]
    decision_hash: str


def _validate_policy(policy: AdmissionPolicy) -> None:
    integers = (
        policy.total_quota, policy.behaviour_cluster_quota, policy.economic_hypothesis_quota,
        policy.parent_descendant_cap, policy.family_budget_cap,
    )
    if any(value <= 0 for value in integers) or policy.fresh_budget_floor < 0:
        raise ValueError("invalid admission quota")
    if policy.fresh_budget_floor > policy.total_quota:
        raise ValueError("fresh floor exceeds total quota")
    if policy.global_top_k_baseline_enabled:
        raise PermissionError("global top-K is configuration-only and frozen in NEXTGEN-DARK")


def admit(candidates: Iterable[CandidateEnvelope], policy: AdmissionPolicy) -> AdmissionResult:
    _validate_policy(policy)
    ordered = sorted(candidates, key=lambda item: (item.proposal_ordinal, item.candidate_id))
    if policy.no_memory and any(item.memory_source != "NONE" for item in ordered):
        raise PermissionError("no-memory admission received a memory-derived candidate")
    admitted: list[CandidateEnvelope] = []
    rejected: list[tuple[str, str]] = []
    exact: set[str] = set()
    behaviour: Counter[str] = Counter()
    hypothesis: Counter[str] = Counter()
    parents: Counter[str] = Counter()
    families: Counter[str] = Counter()

    def consider(item: CandidateEnvelope) -> str | None:
        if item.exact_identity in exact:
            return "DUPLICATE_EXACT_IDENTITY_ONE_VOTE"
        if policy.top_cluster_exile and item.behaviour_cluster == policy.top_cluster_exile:
            return "TOP_CLUSTER_EXILE"
        if behaviour[item.behaviour_cluster] >= policy.behaviour_cluster_quota:
            return "BEHAVIOUR_CLUSTER_QUOTA"
        if hypothesis[item.economic_hypothesis] >= policy.economic_hypothesis_quota:
            return "ECONOMIC_HYPOTHESIS_QUOTA"
        if parents[item.parent_identity] >= policy.parent_descendant_cap:
            return "PARENT_DESCENDANT_CAP"
        if families[item.family_id] >= policy.family_budget_cap:
            return "FAMILY_BUDGET_CAP"
        return None

    fresh_first = [item for item in ordered if item.is_fresh]
    remaining = [item for item in ordered if not item.is_fresh]
    for item in fresh_first + remaining:
        if len(admitted) >= policy.total_quota:
            rejected.append((item.candidate_id, "TOTAL_QUOTA"))
            continue
        reason = consider(item)
        if reason:
            rejected.append((item.candidate_id, reason))
            continue
        admitted.append(item)
        exact.add(item.exact_identity)
        behaviour[item.behaviour_cluster] += 1
        hypothesis[item.economic_hypothesis] += 1
        parents[item.parent_identity] += 1
        families[item.family_id] += 1
    if len([item for item in admitted if item.is_fresh]) < min(policy.fresh_budget_floor, len(fresh_first)):
        raise ValueError("quota interaction makes fresh budget floor infeasible")
    semantic_volume = {
        "behaviour_cluster": dict(sorted(behaviour.items())),
        "economic_hypothesis": dict(sorted(hypothesis.items())),
        "family": dict(sorted(families.items())),
        "lane": dict(sorted(Counter(item.lane_id for item in admitted).items())),
    }
    payload = {
        "policy": asdict(policy), "admitted": [item.candidate_id for item in admitted], "rejected": rejected,
        "semantic_volume": semantic_volume,
    }
    decision_hash = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()
    return AdmissionResult(tuple(admitted), tuple(rejected), semantic_volume, decision_hash)

