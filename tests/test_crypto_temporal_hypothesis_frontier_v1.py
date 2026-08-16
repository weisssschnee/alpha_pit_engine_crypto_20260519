from __future__ import annotations

import json
import random
from pathlib import Path

from alphafactory_crypto.broad_search import search_engine_v1 as engine
from alphafactory_crypto.broad_search.compositional18m import compile_mechanism_catalog
from alphafactory_crypto.broad_search.expression import FieldContract, TypedExpressionRegistry
from alphafactory_crypto.broad_search.temporal_hypothesis_frontier_v1 import P5, P6, compile_frontier_catalog, frontier_catalog_payload, rebuild_frontier_candidate, sample_frontier_candidate
from alphafactory_crypto.broad_search.temporal_program_search_v1 import CONFIG_PATH, _limits, _program_family


ROOT = Path(__file__).resolve().parents[1]


def _registry() -> TypedExpressionRegistry:
    config = engine._read_json(ROOT / CONFIG_PATH)
    rows = engine._read_json(ROOT / "runtime/crypto_search_engine_v1_4_oi_flow_20260728/aligned_carrier_manifest.json")["contracts"]
    return TypedExpressionRegistry(tuple(FieldContract(str(row["field_id"]), str(row["value_type"]), str(row["unit"]), int(row["observable_lag_hours"]), str(row["pit_authority"])) for row in rows), **_limits(config))


def test_frontier_catalog_is_deterministic_bounded_and_exactly_rebuildable() -> None:
    basis = compile_mechanism_catalog(engine._read_json(ROOT / "config/crypto_typed_mechanism_catalog_v2_1.json"))
    source_gap = engine._read_json(ROOT / "config/crypto_temporal_hypothesis_frontier_v1_source_gap.json")
    first = compile_frontier_catalog(basis, source_gap); second = compile_frontier_catalog(basis, source_gap)
    assert [program.program_id for _, program in first] == [program.program_id for _, program in second]
    payload = frontier_catalog_payload(first, source_gap["source_gap_sha256"])
    assert payload == engine._read_json(ROOT / "config/crypto_temporal_hypothesis_frontier_v1_catalog.json")
    assert payload["family_counts"] == {P5: 49, P6: 62}
    registry = _registry(); rng = random.Random(20260817)
    for mechanism, program in first:
        candidate = sample_frontier_candidate(registry=registry, mechanism=mechanism, program=program, rng=rng)
        rebuilt = rebuild_frontier_candidate(registry, candidate)
        assert rebuilt.candidate_id == candidate.candidate_id
        assert _program_family(candidate) == program.family_id
        assert candidate.generation_genes["matched_control_schema"] in {"DUAL_AXIS_A_B_AB", "HIERARCHICAL_A_B_AB_ABC"}


def test_frontier_catalog_has_no_p1_p2_p3_or_new_mapping_authority() -> None:
    payload = engine._read_json(ROOT / "config/crypto_temporal_hypothesis_frontier_v1_catalog.json")
    rows = payload["semantic_rows"]
    assert {row["program_spec"]["family_id"] for row in rows} == {P5, P6}
    assert {row["program_spec"]["mapping_class"] for row in rows} <= {"CROSS_SECTIONAL_RELATIVE", "SPARSE_EVENT_CARRY"}
    assert all("P1_" not in json.dumps(row) and "P2_" not in json.dumps(row) and "P3_" not in json.dumps(row) for row in rows)
