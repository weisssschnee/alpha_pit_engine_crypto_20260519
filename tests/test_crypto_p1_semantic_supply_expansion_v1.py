from __future__ import annotations

import json
import random
from collections import Counter
from pathlib import Path

from alphafactory_crypto.broad_search import search_engine_v1 as engine
from alphafactory_crypto.broad_search.compositional18m import (
    mapping_id_for_mechanism_spec,
    mechanism_role_domains,
)
from alphafactory_crypto.broad_search.expression import FieldContract, TypedExpressionRegistry
from alphafactory_crypto.broad_search.temporal_p1_semantic_expansion_v1 import (
    CONTROL_SCHEMA,
    REPRESENTATION,
    compile_p1_generation2_catalog,
    p1_generation2_candidate_from_genes,
    p1_generation2_catalog_payload,
    sample_p1_generation2_candidate,
)
from alphafactory_crypto.broad_search.temporal_p1_semantic_expansion_search_v1 import (
    _next_semantic_lane,
)
from alphafactory_crypto.broad_search.temporal_program_v1 import (
    compile_temporal_program_catalog,
    program_catalog_payload,
    sample_temporal_program_candidate,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "config/crypto_temporal_mechanism_program_v1.json").read_text(encoding="utf-8"))
SOURCE_GAP = json.loads((ROOT / "config/crypto_p1_semantic_supply_expansion_v1_source_gap.json").read_text(encoding="utf-8"))


def _contracts() -> tuple[FieldContract, ...]:
    rows = json.loads((ROOT / "runtime/crypto_search_engine_v1_4_oi_flow_20260728/aligned_carrier_manifest.json").read_text(encoding="utf-8"))["contracts"]
    return tuple(FieldContract(str(row["field_id"]), str(row["value_type"]), str(row["unit"]), int(row["observable_lag_hours"]), str(row["pit_authority"])) for row in rows)


def _registry() -> TypedExpressionRegistry:
    limits = CONFIG["expression_limits"]
    return TypedExpressionRegistry(
        _contracts(),
        max_depth=int(limits["maximum_depth"]),
        max_raw_inputs=int(limits["maximum_raw_fields"]),
        max_rolling_windows=int(limits["maximum_rolling_windows"]),
        max_canonical_primitive_nodes=int(limits["maximum_canonical_primitive_nodes"]),
        max_cross_asset_normalizations=int(limits["maximum_cross_asset_normalizations"]),
        max_regime_gates=int(limits["maximum_regime_gates"]),
    )


def test_g1_catalog_identity_is_unchanged_and_g2_is_bounded() -> None:
    parents = compile_temporal_program_catalog(CONFIG)
    before = program_catalog_payload(parents)
    g2 = compile_p1_generation2_catalog(parents, SOURCE_GAP)
    after = program_catalog_payload(compile_temporal_program_catalog(CONFIG))
    assert before == after
    assert len([program for _, program in parents if program.family_id.startswith("P1_")]) == 180
    assert len(g2) == 171
    assert len({program.program_id for _, program in g2}) == len(g2)
    assert {mechanism.generation for mechanism, _ in g2} == {2}
    assert {mechanism.matched_control_schema for mechanism, _ in g2} == {CONTROL_SCHEMA}
    assert Counter(program.condition_operator for _, program in g2) == {"ConditionGate": 92, "StateModulation": 79}
    assert p1_generation2_catalog_payload(g2, parents)["catalog_sha256"] == "60AEE0D3AF8EEABA43B89D39BE05AD1CC75DD076963D4FC6346CC5B95904E286"


def test_g2_candidate_compiles_replays_and_uses_existing_hierarchical_control() -> None:
    registry = _registry()
    domains = mechanism_role_domains(_contracts())
    parents = compile_temporal_program_catalog(CONFIG)
    g2 = compile_p1_generation2_catalog(parents, SOURCE_GAP)
    mechanism, program = g2[0]
    parent_mechanism, parent_program = next(row for row in parents if row[1].program_id == program.parent_program_id)
    parent = sample_temporal_program_candidate(
        registry=registry,
        mechanism=parent_mechanism,
        program=parent_program,
        domains=domains,
        scale_contract=CONFIG["time_scale_authority"],
        rng=random.Random(20260816),
    )
    candidate = sample_p1_generation2_candidate(
        registry=registry,
        mechanism=mechanism,
        program=program,
        parent=parent,
        parent_program=parent_program,
        scale_contract=CONFIG["time_scale_authority"],
        rng=random.Random(20260816),
        domains=domains,
    )
    replay = p1_generation2_candidate_from_genes(registry, genes=candidate.generation_genes, domains=domains)
    assert replay.to_dict() == candidate.to_dict()
    assert candidate.generation_genes["representation"] == REPRESENTATION
    assert candidate.generation_genes["semantic_generation"] == 2
    assert candidate.control.operator == "SupportMatchedPayload"
    assert candidate.control.inputs[0].expression_id == candidate.expression.inputs[0].expression_id
    assert set(candidate.raw_fields) == set(registry.validate(candidate.control).raw_fields)
    assert engine._candidate_rebuild_verified(registry, candidate, {})
    assert candidate.mapping_id == mapping_id_for_mechanism_spec(mechanism)


def test_source_gap_is_train_only_and_selected_parent_is_recoverable() -> None:
    assert SOURCE_GAP["selected_parent_count"] == 24
    assert SOURCE_GAP["observed_p1_program_count"] <= 180
    assert SOURCE_GAP["source_partitions"] == ["train"]
    assert all(SOURCE_GAP[name] == 0 for name in ("validation_reads", "oos_reads", "holdout_reads", "forward_reads", "promotion_reads", "sealed_reads"))
    catalog_ids = {program.program_id for _, program in compile_temporal_program_catalog(CONFIG)}
    assert {row["program_id"] for row in SOURCE_GAP["selected_parent_programs"]}.issubset(catalog_ids)


def test_productive_lane_scheduler_keeps_g2_as_clear_majority() -> None:
    rows = []
    for _ in range(20_000):
        lane = _next_semantic_lane(rows, [])
        rows.append({"semantic_lane": lane})
    assert Counter(row["semantic_lane"] for row in rows) == {
        "P1_G2": 14_000,
        "P1_G1": 3_000,
        "P4": 3_000,
    }
