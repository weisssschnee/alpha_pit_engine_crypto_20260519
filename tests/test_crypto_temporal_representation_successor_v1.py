from __future__ import annotations

import json
import random
from pathlib import Path

from alphafactory_crypto.broad_search.compositional18m import compile_mechanism_catalog
from alphafactory_crypto.broad_search.temporal_program_v1 import (
    compile_temporal_program_catalog,
    sample_temporal_program_candidate,
)
from alphafactory_crypto.broad_search.temporal_representation_successor_v1 import (
    ACTIVE_FAMILIES,
    build_compatibility_inventory,
    compatibility_inventory_payload,
    lossless_embedding_benchmark,
    semantic_block_children,
)
from alphafactory_crypto.broad_search.temporal_representation_tournament_v1 import (
    ARMS,
    ARM_LANE_SEEDS,
    EVOLUTION_PROBABILITIES,
    STRICT_PER_ARM,
)
from test_crypto_temporal_program_v1 import CONFIG, REPO_ROOT, _registry


def _catalogs():
    temporal = compile_temporal_program_catalog(CONFIG)
    mechanism = compile_mechanism_catalog(
        json.loads(
            (REPO_ROOT / "config/crypto_typed_mechanism_catalog_v2_1.json").read_text(
                encoding="utf-8"
            )
        )
    )
    return temporal, mechanism


def _constructible_candidate(pair, seed: int):
    mechanism, program = pair
    for attempt in range(128):
        try:
            return sample_temporal_program_candidate(
                registry=_registry(),
                mechanism=mechanism,
                program=program,
                domains=None,
                scale_contract=CONFIG["time_scale_authority"],
                rng=random.Random(seed + attempt),
            )
        except ValueError:
            continue
    raise AssertionError("fixture program was not constructible")


def test_inventory_reuses_both_existing_catalogs_and_rejects_incompatible_donors() -> None:
    temporal, mechanism = _catalogs()
    inventory = build_compatibility_inventory(temporal, mechanism)
    payload = compatibility_inventory_payload(
        inventory,
        total_temporal_programs=len(temporal),
        total_mechanisms=len(mechanism),
    )
    assert len(temporal) == 464
    assert len(mechanism) == 786
    assert payload["compatible_mechanism_donor_count"] == 33
    assert payload["rejected_mechanism_donor_reasons"]
    assert payload["market_arrays_read"] == payload["candidate_evaluations"] == 0


def test_all_464_program_semantics_and_all_constructible_expressions_embed_losslessly() -> None:
    temporal, mechanism = _catalogs()
    inventory = build_compatibility_inventory(temporal, mechanism)
    result = lossless_embedding_benchmark(
        registry=_registry(),
        temporal_catalog=temporal,
        scale_contract=CONFIG["time_scale_authority"],
        inventory=inventory,
    )
    assert result["pass"] is True
    assert result["exact_semantic_identity_matches"] == 464
    assert result["exact_expression_identity_matches"] == result[
        "constructible_expression_programs_tested"
    ]
    assert result["validation_reads"] == result["oos_reads"] == result["sealed_reads"] == 0


def test_semantic_block_crossover_compiles_non_parent_p1_children() -> None:
    temporal, mechanism = _catalogs()
    inventory = build_compatibility_inventory(temporal, mechanism)
    p1 = [pair for pair in temporal if pair[1].family_id == ACTIVE_FAMILIES[0]]
    first_pair = p1[0]
    second_pair = next(
        pair
        for pair in p1[1:]
        if pair[1].left_role != first_pair[1].left_role
        and pair[1].outer_operator != first_pair[1].outer_operator
    )
    first = _constructible_candidate(first_pair, 11)
    second = _constructible_candidate(second_pair, 37)
    children, details = semantic_block_children(
        first,
        second,
        registry=_registry(),
        scale_contract=CONFIG["time_scale_authority"],
        inventory=inventory,
        seen=set(),
    )
    assert details["completion_failure_count"] == 0
    assert details["legal_child_count"] == len(children) > 0
    assert all(
        child.generation_genes["program_spec"]["family_id"] == ACTIVE_FAMILIES[0]
        for child, _ in children.values()
    )


def test_tournament_is_fixed_independent_evolution_only_10k_per_arm() -> None:
    assert len(ARMS) == 2
    assert STRICT_PER_ARM == 10_000
    assert EVOLUTION_PROBABILITIES == {
        "parameter_mutation_probability": 0.62,
        "mechanism_mutation_probability": 0.03,
        "crossover_probability": 0.35,
    }
    assert all(len(values) == len(set(values)) == 4 for values in ARM_LANE_SEEDS.values())
    assert not set(ARM_LANE_SEEDS[ARMS[0]]) & set(ARM_LANE_SEEDS[ARMS[1]])
