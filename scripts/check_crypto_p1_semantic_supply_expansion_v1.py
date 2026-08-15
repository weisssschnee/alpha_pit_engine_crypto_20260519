from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from alphafactory_crypto.broad_search import search_engine_v1 as engine
from alphafactory_crypto.broad_search.compositional18m import CandidateSpec, mechanism_role_domains
from alphafactory_crypto.broad_search.expression import FieldContract, TypedExpressionRegistry
from alphafactory_crypto.broad_search.temporal_p1_semantic_expansion_search_v1 import (
    BLOCK_ROBUST_V2_AUTHORITY,
    G2_CATALOG_PATH,
    LANE_TARGETS,
    RAW_ATTEMPT_CAP,
    SOURCE_GAP_PATH,
    STRICT_CAP,
    validate_authorization,
)
from alphafactory_crypto.broad_search.temporal_p1_semantic_expansion_v1 import (
    CONTROL_SCHEMA,
    G2_GENE_KEYS,
    compile_p1_generation2_catalog,
    p1_generation2_candidate_from_genes,
    p1_generation2_catalog_payload,
)
from alphafactory_crypto.broad_search.temporal_program_search_v1 import CONFIG_PATH
from alphafactory_crypto.broad_search.temporal_program_v1 import (
    PROGRAM_GENE_KEYS,
    TemporalProgramSpec,
    compile_temporal_program_catalog,
)


def _sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest().upper()


def _file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _registry(root: Path, config: dict[str, Any]) -> TypedExpressionRegistry:
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
    )


def check(root: Path, runtime_id: str) -> dict[str, Any]:
    authorization = validate_authorization(root)
    runtime = root / "runtime" / runtime_id
    errors = []
    if runtime_id != authorization["runtime_id"]:
        errors.append("runtime_id")
    complete = engine._read_json(runtime / "run_complete.json")
    analysis = engine._read_json(runtime / "final_analysis.json")
    complete_core = {key: value for key, value in complete.items() if key != "run_result_sha256"}
    analysis_core = {key: value for key, value in analysis.items() if key != "analysis_sha256"}
    if complete.get("run_result_sha256") != _sha(complete_core):
        errors.append("run_result_hash")
    if analysis.get("analysis_sha256") != _sha(analysis_core):
        errors.append("analysis_hash")
    frame = pd.read_parquet(runtime / "candidate_ledger.parquet")
    if len(frame) != STRICT_CAP or int(complete.get("strict", -1)) != STRICT_CAP:
        errors.append("strict_cap")
    if int(complete.get("attempts", RAW_ATTEMPT_CAP + 1)) > RAW_ATTEMPT_CAP:
        errors.append("attempt_cap")
    lanes = Counter(frame["semantic_lane"].astype(str))
    if set(lanes) != set(LANE_TARGETS) or lanes["P1_G2"] <= STRICT_CAP // 2 or min(lanes["P1_G1"], lanes["P4"]) < STRICT_CAP // 10:
        errors.append("lane_allocation")
    families = Counter(frame["program_family_id"].astype(str))
    if any(families.get(name, 0) for name in ("P2_RECENT_CROWDING_EVENT_TO_RESPONSE", "P3_FLOW_SHOCK_PERSISTENCE_TO_ABSORPTION")):
        errors.append("p2_p3_contamination")
    if set(frame["evaluation_partition"].astype(str)) != {"train"}:
        errors.append("partition")
    if not frame["matched_control_valid"].astype(bool).all() or not frame["strict_evaluated"].astype(bool).all():
        errors.append("strict_or_control")

    config = engine._read_json(root / CONFIG_PATH)
    parents = compile_temporal_program_catalog(config)
    source_gap = engine._read_json(root / SOURCE_GAP_PATH)
    g2 = compile_p1_generation2_catalog(parents, source_gap)
    g2_payload = p1_generation2_catalog_payload(g2, parents)
    frozen_catalog = engine._read_json(root / G2_CATALOG_PATH)
    if g2_payload["catalog_sha256"] != frozen_catalog["catalog_sha256"]:
        errors.append("catalog_hash")
    if (
        len(g2) != 171
        or sum(program.family_id.startswith("P1_") for _, program in parents) != 180
    ):
        errors.append("semantic_supply_count")
    legal_g2 = {program.program_id for _, program in g2}
    legal_g1 = {program.program_id for _, program in parents}
    registry = _registry(root, config)
    replayed = set()
    for row in frame.to_dict("records"):
        ordering = json.loads(str(row["block_robust_ordering_json"]))
        ordering_core = {
            key: value for key, value in ordering.items() if key != "ordering_sha256"
        }
        if (
            ordering.get("authority") != BLOCK_ROBUST_V2_AUTHORITY
            or ordering.get("ordering_sha256") != _sha(ordering_core)
            or int(ordering.get("block_count", -1)) != 3
            or len(ordering.get("required_matched_components") or ())
            not in {2, 3}
        ):
            errors.append("block_robust_v2_ordering")
            break
        payload = json.loads(str(row["candidate_spec_json"]))
        if engine._payload_sha(payload) != str(row["candidate_spec_sha256"]):
            errors.append("candidate_spec_hash")
            break
        candidate = CandidateSpec.from_dict(payload)
        genes = dict(candidate.generation_genes)
        lane = str(row["semantic_lane"])
        if lane == "P1_G2":
            if (
                set(genes) != set(G2_GENE_KEYS)
                or str(genes["program_id"]) not in legal_g2
                or int(genes["semantic_generation"]) != 2
                or str(genes["matched_control_schema"]) != CONTROL_SCHEMA
                or candidate.control.operator != "SupportMatchedPayload"
            ):
                errors.append("unapproved_g2_semantic")
                break
            if str(genes["program_id"]) not in replayed:
                rebuilt = p1_generation2_candidate_from_genes(registry, genes=genes)
                if rebuilt.to_dict() != candidate.to_dict():
                    errors.append("g2_replay")
                    break
                replayed.add(str(genes["program_id"]))
        else:
            if set(genes) != set(PROGRAM_GENE_KEYS) or str(genes["program_id"]) not in legal_g1:
                errors.append("legacy_semantic_drift")
                break
            TemporalProgramSpec.from_dict(dict(genes["program_spec"]))
            expected_family = "P1_POSITION_STATE_CHANGE_TO_RESPONSE" if lane == "P1_G1" else "P4_MULTISCALE_STATE_X_TRANSITION_ROUTING"
            if str(genes["program_spec"]["family_id"]) != expected_family:
                errors.append("legacy_lane_scope")
                break
    checkpoints = sorted((runtime / "checkpoints").glob("checkpoint_[0-9][0-9][0-9]"))
    if len(checkpoints) != STRICT_CAP // 2_000:
        errors.append("checkpoint_count")
    else:
        manifest = engine._read_json(checkpoints[-1] / "manifest.json")
        if manifest.get("restore_verified") is not True or int(manifest.get("completed_ledger_row_count", -1)) != STRICT_CAP:
            errors.append("checkpoint_restore")
    for payload in (complete, analysis, engine._read_json(runtime / "frozen_contract.json")):
        if any(int(payload.get(name, 0)) for name in ("validation_reads", "oos_reads", "holdout_reads", "forward_reads", "promotion_reads", "sealed_reads")):
            errors.append("forbidden_reads")
            break
    decision = str(analysis.get("next_decision"))
    if decision not in {
        "P1_SEMANTIC_EXPANSION_PASS", "P1_SEMANTIC_EXPANSION_PARTIAL",
        "P1_HYPOTHESIS_FAMILY_WEAK", "BLOCK_ROBUST_V2_INVALID",
        "GLOBAL_SEARCH_CORE_REGRESSION", "RESEARCH_INVALID",
    }:
        errors.append("decision")
    core = {
        "schema_version": 1,
        "status": "PASS" if not errors else "FAIL",
        "runtime_id": runtime_id,
        "authorization_sha256": authorization["authorization_sha256"],
        "candidate_ledger_rows": len(frame),
        "candidate_ledger_bytes": (runtime / "candidate_ledger.parquet").stat().st_size,
        "candidate_ledger_sha256": _file_sha(runtime / "candidate_ledger.parquet"),
        "semantic_lane_counts": dict(sorted(lanes.items())),
        "p1_g2_programs_observed": len(replayed),
        "p1_g2_catalog_sha256": g2_payload["catalog_sha256"],
        "p2_strict": 0,
        "p3_strict": 0,
        "checkpoint_count": len(checkpoints),
        "next_decision": decision,
        "errors": sorted(set(errors)),
        "market_arrays_read": 0,
        "validation_reads": 0,
        "oos_reads": 0,
        "holdout_reads": 0,
        "forward_reads": 0,
        "promotion_reads": 0,
        "sealed_reads": 0,
        "automatic_next_run_started": False,
    }
    return {**core, "checker_sha256": _sha(core)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--runtime-id", required=True)
    args = parser.parse_args()
    result = check(args.repo_root.resolve(), args.runtime_id)
    engine._write_json(args.repo_root.resolve() / "runtime" / args.runtime_id / "canonical_checker.json", result)
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
