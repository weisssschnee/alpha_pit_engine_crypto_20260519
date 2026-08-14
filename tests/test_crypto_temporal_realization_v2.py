from __future__ import annotations

from alphafactory_crypto.broad_search.temporal_realization_v2 import (
    checkpoint_decision,
    constructive_crossover,
)
from alphafactory_crypto.broad_search.search_engine_v1 import MechanismEvolutionV2

from test_crypto_temporal_targeted_deepening_v1 import (
    _targeted_parent_candidates,
)


def test_constructive_crossover_enumerates_and_verifies_legal_splices() -> None:
    registry, catalog, parameters, candidates = _targeted_parent_candidates(8)
    policy = MechanismEvolutionV2(
        8123, registry, tuple(value[0] for value in catalog), parameters
    )
    first = candidates[0]
    compatible = [
        candidate
        for candidate in candidates[1:]
        if policy._compatible(policy._spec(first), policy._spec(candidate))
    ]
    assert compatible
    child, details = constructive_crossover(policy, first, compatible[0])
    assert details["enumerated_splice_count"] == (
        1 << len(policy._gene_groups(first))
    ) - 2
    if child is not None:
        receipt = policy._receipt(
            operation="ONE_POINT_TYPED_MECHANISM_CROSSOVER",
            parents=(first, compatible[0]),
            child=child,
            details=details,
        )
        assert policy.verify_receipt((first, compatible[0]), child, receipt)


def test_realization_v2_10k_gate_is_predeclared() -> None:
    rows = []
    for index in range(6_000):
        requested = "crossover" if index < 2_000 else "parameter_mutation"
        fallback = requested == "crossover" and index < 600
        rows.append(
            {
                "arm": "temporal_program_evolution",
                "program_family_id": (
                    "P1_POSITION_STATE_CHANGE_TO_RESPONSE"
                    if index % 2
                    else "P4_MULTISCALE_STATE_X_TRANSITION_ROUTING"
                ),
                "requested_operation": requested,
                "realized_operation": "parameter_mutation" if fallback else requested,
                "crossover_fallback": fallback,
                "matched_positive": index < 700,
            }
        )
    rows.extend(
        {
            "arm": "temporal_program_random",
            "program_family_id": "P4_MULTISCALE_STATE_X_TRANSITION_ROUTING",
        }
        for _ in range(4_000)
    )
    decision = checkpoint_decision(
        rows,
        strict_boundary=10_000,
        frozen_parent_pool_sha256="A08112ED1765A432D15D259A70F308C2DE5BA7B617D294BFB8349020EC61AA49",
    )
    assert decision["status"] == "CONTINUE_TO_20000"
    assert decision["crossover_gate"]["pass"] is True
    assert decision["search_quality_gate"]["pass"] is True
