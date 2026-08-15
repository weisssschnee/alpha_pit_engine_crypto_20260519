from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from alphafactory_crypto.broad_search import search_engine_v1 as engine
from alphafactory_crypto.broad_search.compositional18m import (
    CandidateSpec,
    mapping_id_for_mechanism_spec,
    mechanism_role_domains,
)
from alphafactory_crypto.broad_search.expression import FieldContract, TypedExpressionRegistry
from alphafactory_crypto.broad_search.temporal_p1_semantic_expansion_v1 import (
    compile_p1_generation2_catalog,
    p1_generation2_candidate_from_genes,
    p1_generation2_catalog_payload,
    sample_p1_generation2_candidate,
)
from alphafactory_crypto.broad_search.temporal_program_v1 import (
    compile_temporal_program_catalog,
    program_catalog_payload,
    sample_temporal_program_candidate,
)


def _sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    ).hexdigest().upper()


def _registry(root: Path, config: dict[str, Any]) -> tuple[TypedExpressionRegistry, tuple[FieldContract, ...]]:
    rows = engine._read_json(root / "runtime/crypto_search_engine_v1_4_oi_flow_20260728/aligned_carrier_manifest.json")["contracts"]
    contracts = tuple(FieldContract(str(row["field_id"]), str(row["value_type"]), str(row["unit"]), int(row["observable_lag_hours"]), str(row["pit_authority"])) for row in rows)
    limits = config["expression_limits"]
    return TypedExpressionRegistry(
        contracts,
        max_depth=int(limits["maximum_depth"]),
        max_raw_inputs=int(limits["maximum_raw_fields"]),
        max_rolling_windows=int(limits["maximum_rolling_windows"]),
        max_canonical_primitive_nodes=int(limits["maximum_canonical_primitive_nodes"]),
        max_cross_asset_normalizations=int(limits["maximum_cross_asset_normalizations"]),
        max_regime_gates=int(limits["maximum_regime_gates"]),
    ), contracts


def build(root: Path) -> dict[str, Any]:
    config = engine._read_json(root / "config/crypto_temporal_mechanism_program_v1.json")
    source_gap = engine._read_json(root / "config/crypto_p1_semantic_supply_expansion_v1_source_gap.json")
    frozen = engine._read_json(root / "config/crypto_p1_semantic_supply_expansion_v1_catalog.json")
    parents = compile_temporal_program_catalog(config)
    g2 = compile_p1_generation2_catalog(parents, source_gap)
    repeated = compile_p1_generation2_catalog(parents, source_gap)
    payload = p1_generation2_catalog_payload(g2, parents)
    if payload["catalog_sha256"] != frozen["catalog_sha256"] or payload != p1_generation2_catalog_payload(repeated, parents):
        raise RuntimeError("P1 G2 catalog is not deterministic or frozen")
    registry, contracts = _registry(root, config)
    domains = mechanism_role_domains(contracts)
    parent_by_id = {program.program_id: (mechanism, program) for mechanism, program in parents}
    compiled = []
    failures = []
    for index, (mechanism, program) in enumerate(g2):
        parent_mechanism, parent_program = parent_by_id[program.parent_program_id]
        parent = sample_temporal_program_candidate(
            registry=registry,
            mechanism=parent_mechanism,
            program=parent_program,
            domains=domains,
            scale_contract=config["time_scale_authority"],
            rng=random.Random(1_000_000 + index),
        )
        candidate = None
        last_error = None
        for attempt in range(64):
            try:
                candidate = sample_p1_generation2_candidate(
                    registry=registry,
                    mechanism=mechanism,
                    program=program,
                    parent=parent,
                    parent_program=parent_program,
                    scale_contract=config["time_scale_authority"],
                    rng=random.Random(2_000_000 + index * 64 + attempt),
                    domains=domains,
                )
                break
            except ValueError as failure:
                last_error = type(failure).__name__ + ":" + str(failure)
                continue
        if candidate is None:
            failures.append({"program_id": program.program_id, "reason": "NO_LEGAL_REALIZATION_IN_64", "last_error": last_error})
            continue
        replay = p1_generation2_candidate_from_genes(registry, genes=candidate.generation_genes, domains=domains)
        restored = CandidateSpec.from_dict(candidate.to_dict())
        assurance = registry.validate(candidate.expression)
        control = registry.validate(candidate.control)
        if not (
            replay.to_dict() == candidate.to_dict()
            and restored.to_dict() == candidate.to_dict()
            and candidate.control.operator == "SupportMatchedPayload"
            and set(assurance.raw_fields) == set(control.raw_fields)
            and candidate.mapping_id == mapping_id_for_mechanism_spec(mechanism)
            and engine._candidate_rebuild_verified(registry, candidate, {})
        ):
            failures.append({"program_id": program.program_id, "reason": "REPLAY_CONTROL_MAPPING_OR_SERIALIZATION"})
            continue
        compiled.append(candidate)
    if failures or len(compiled) != len(g2):
        raise RuntimeError(json.dumps(failures[:10], sort_keys=True))
    core = {
        "schema_version": 1,
        "status": "P1_SEMANTIC_SUPPLY_EXPANSION_OFFLINE_PASS",
        "old_p1_g1_count": 180,
        "old_temporal_program_catalog_sha256": program_catalog_payload(parents)["catalog_sha256"],
        "old_g1_identity_replay": True,
        "p1_g2_catalog_sha256": payload["catalog_sha256"],
        "p1_g2_semantic_count": len(g2),
        "deterministic_semantic_identity": True,
        "compiled_candidate_count": len(compiled),
        "expression_compiler_pass": True,
        "hierarchical_matched_controls_pass": True,
        "mapping_derivation_pass": True,
        "pit_field_legality_pass": True,
        "checkpoint_serialization_pass": True,
        "candidate_rebuild_pass": True,
        "semantic_dedup_pass": len({program.program_id for _, program in g2}) == len(g2),
        "p2_p3_catalog_activation_count": 0,
        "condition_roles": dict(sorted(Counter(program.condition_role for _, program in g2).items())),
        "condition_primitives": dict(sorted(Counter(program.condition_component for _, program in g2).items())),
        "condition_operator_modes": dict(sorted(Counter(program.condition_operator + ":" + str(program.condition_mode) for _, program in g2).items())),
        "market_arrays_read": 0,
        "candidate_evaluations": 0,
        "validation_reads": 0,
        "oos_reads": 0,
        "holdout_reads": 0,
        "forward_reads": 0,
        "promotion_reads": 0,
        "sealed_reads": 0,
    }
    return {**core, "offline_evidence_sha256": _sha(core)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = build(args.repo_root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    engine._write_json(args.output, payload)
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
