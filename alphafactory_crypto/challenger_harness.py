from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


STRATEGY_BENCHMARKS = (
    "simple_funding", "simple_basis", "simple_oi", "momentum", "reversal", "volatility",
    "liquidity", "session_time_of_day", "funding_core", "bz_compatible",
)
ALGORITHM_CHALLENGERS = (
    "cem", "typed_ast", "uct_mcts", "evolutionary_search", "surrogate", "llm_proposal",
    "external_competitor_reproduction",
)


@dataclass(frozen=True)
class HarnessSpec:
    harness_id: str
    harness_kind: str
    proposal_budget: int
    strict_eval_budget: int
    archive_namespace: str
    policy_frozen: bool
    candidate_contract: str
    data_access_contract: str
    execution_authorized: bool = False
    feedback_permission: str = "REPORT_ONLY_NO_MEMORY"


def validate_harness(specs: Iterable[HarnessSpec]) -> tuple[HarnessSpec, ...]:
    values = tuple(specs)
    strategy = {item.harness_id for item in values if item.harness_kind == "strategy_benchmark"}
    algorithms = {item.harness_id for item in values if item.harness_kind == "algorithm_challenger"}
    if strategy != set(STRATEGY_BENCHMARKS) or algorithms != set(ALGORITHM_CHALLENGERS):
        raise ValueError("benchmark/challenger harness registry is incomplete")
    archives: set[str] = set()
    for item in values:
        if item.proposal_budget <= 0 or item.strict_eval_budget < 0:
            raise ValueError("invalid harness budgets")
        if not item.policy_frozen or item.execution_authorized:
            raise PermissionError("NEXTGEN-DARK harness policies are frozen and execution is unauthorized")
        if item.feedback_permission != "REPORT_ONLY_NO_MEMORY":
            raise PermissionError("harness feedback cannot enter positive memory")
        if item.archive_namespace in archives:
            raise ValueError("harness archives must be independent")
        archives.add(item.archive_namespace)
        if "DEVELOPMENT_ONLY" not in item.data_access_contract:
            raise PermissionError("harness data access must be development-only")
    return tuple(sorted(values, key=lambda item: (item.harness_kind, item.harness_id)))

