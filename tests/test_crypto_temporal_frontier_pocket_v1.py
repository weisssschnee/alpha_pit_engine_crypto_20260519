from __future__ import annotations

import json
import random
from pathlib import Path

from alphafactory_crypto.broad_search import search_engine_v1 as engine
from alphafactory_crypto.broad_search.compositional18m import compile_mechanism_catalog
from alphafactory_crypto.broad_search.expression import FieldContract, TypedExpressionRegistry
from alphafactory_crypto.broad_search.temporal_frontier_pocket_v1 import ANCHORS, local_genes, propose_local
from alphafactory_crypto.broad_search.temporal_hypothesis_frontier_v1 import P5, P6, compile_frontier_catalog, sample_frontier_candidate
from alphafactory_crypto.broad_search.temporal_program_search_v1 import CONFIG_PATH, _limits


ROOT = Path(__file__).resolve().parents[1]


def _registry() -> TypedExpressionRegistry:
    config = engine._read_json(ROOT / CONFIG_PATH)
    rows = engine._read_json(ROOT / "runtime/crypto_search_engine_v1_4_oi_flow_20260728/aligned_carrier_manifest.json")["contracts"]
    contracts = tuple(FieldContract(str(row["field_id"]), str(row["value_type"]), str(row["unit"]), int(row["observable_lag_hours"]), str(row["pit_authority"])) for row in rows)
    return TypedExpressionRegistry(contracts, **_limits(config))


def _anchors() -> tuple[TypedExpressionRegistry, dict[str, object]]:
    registry = _registry()
    basis = compile_mechanism_catalog(engine._read_json(ROOT / "config/crypto_typed_mechanism_catalog_v2_1.json"))
    source_gap = engine._read_json(ROOT / "config/crypto_temporal_hypothesis_frontier_v1_source_gap.json")
    catalog = compile_frontier_catalog(basis, source_gap)
    output = {}
    for family in (P5, P6):
        mechanism, program = next(row for row in catalog if row[1].program_id == ANCHORS[family]["program_id"])
        output[family] = sample_frontier_candidate(registry=registry, mechanism=mechanism, program=program, rng=random.Random(ANCHORS[family]["seed"]))
    return registry, output


def test_pocket_policy_preserves_core_semantics_and_family_scope() -> None:
    registry, anchors = _anchors()
    for family in (P5, P6):
        rng = random.Random(20260817)
        anchor = anchors[family]
        for _ in range(100):
            candidate = propose_local(registry, anchor, family, rng)
            assert candidate.mapping_id == anchor.mapping_id == "CROSS_SECTIONAL_ZERO_NET"
            assert candidate.skeleton_id == anchor.skeleton_id
            assert candidate.generation_genes["mechanism_spec"]["program_id"] == ANCHORS[family]["program_id"]
            assert candidate.generation_genes["mechanism_spec"]["template_id"] == family
            assert candidate.generation_genes["matched_control_schema"] == "DUAL_AXIS_A_B_AB"
            assert all(token not in json.dumps(candidate.to_dict()) for token in ("P1_", "P2_", "P3_"))


def test_pocket_local_gene_edits_are_bounded() -> None:
    _, anchors = _anchors()
    for family in (P5, P6):
        anchor = anchors[family]
        genes = local_genes(anchor, family, random.Random(7))
        unchanged = {"mechanism_id", "mechanism_spec", "matched_control_schema", "horizon_hours", "left_auxiliary_field", "right_auxiliary_field", "condition_field", "condition_auxiliary_field"}
        for key in unchanged:
            assert genes[key] == anchor.generation_genes[key]
        assert genes["temporal_transform"]["primitive_id"] == ("Persistence" if family == P5 else "Transition")
        assert genes["temporal_transform"]["axis"] == "left"
