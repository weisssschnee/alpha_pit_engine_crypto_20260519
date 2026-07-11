from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Iterable


LANE_IDS = (
    "static_cross_sectional", "temporal_program", "event_conditioned", "state_transition",
    "orthogonal_exile", "competitor_reproduction", "mcts_evolutionary_challenger",
)


@dataclass(frozen=True)
class CandidateContract:
    contract_id: str
    requires_exact_identity: bool = True
    requires_economic_hypothesis: bool = True
    requires_lineage: bool = True
    performance_fields_allowed: bool = False
    feedback_permission: str = "NONE_NEXTGEN_DARK"


@dataclass(frozen=True)
class LaneSpec:
    lane_id: str
    root_distribution: str
    proposal_quota: int
    admission_quota: int
    archive_namespace: str
    lineage_namespace: str
    seed: int
    candidate_contract: CandidateContract
    memory_policy: str = "NO_MEMORY"
    elite_sharing: bool = False
    historical_winner_sharing: bool = False
    new_economic_hypothesis_first_class: bool = False


def validate_lanes(lanes: Iterable[LaneSpec]) -> tuple[LaneSpec, ...]:
    values = tuple(lanes)
    ids = [lane.lane_id for lane in values]
    if tuple(sorted(ids)) != tuple(sorted(LANE_IDS)) or len(set(ids)) != len(LANE_IDS):
        raise ValueError("all seven isolated lanes must be registered exactly once")
    namespaces: set[str] = set()
    seeds: set[int] = set()
    for lane in values:
        if lane.proposal_quota <= 0 or lane.admission_quota <= 0 or lane.admission_quota > lane.proposal_quota:
            raise ValueError("invalid per-lane quotas")
        if lane.memory_policy != "NO_MEMORY" or lane.elite_sharing or lane.historical_winner_sharing:
            raise PermissionError("NEXTGEN-DARK lanes cannot share memory, elites, or historical winners")
        if lane.candidate_contract.performance_fields_allowed or lane.candidate_contract.feedback_permission != "NONE_NEXTGEN_DARK":
            raise PermissionError("NEXTGEN-DARK candidate contract cannot carry performance feedback")
        if lane.archive_namespace in namespaces or lane.lineage_namespace in namespaces:
            raise ValueError("archive and lineage namespaces must be globally isolated")
        namespaces.update((lane.archive_namespace, lane.lineage_namespace))
        if lane.seed in seeds:
            raise ValueError("lane seeds must be independent")
        seeds.add(lane.seed)
    exile = next(lane for lane in values if lane.lane_id == "orthogonal_exile")
    if not exile.new_economic_hypothesis_first_class or exile.memory_policy != "NO_MEMORY":
        raise ValueError("orthogonal/exile, no-memory and new-hypothesis must be first-class")
    return tuple(sorted(values, key=lambda item: item.lane_id))


def lane_registry_hash(lanes: Iterable[LaneSpec]) -> str:
    payload = [asdict(item) for item in validate_lanes(lanes)]
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()

