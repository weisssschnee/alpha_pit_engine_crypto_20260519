from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from alphafactory_crypto.broad_search import search_engine_v1 as engine
from alphafactory_crypto.broad_search.compositional18m import compile_mechanism_catalog
from alphafactory_crypto.broad_search.expression import FieldContract, TypedExpressionRegistry
from alphafactory_crypto.broad_search.temporal_p1_semantic_expansion_v1 import (
    compile_p1_generation2_catalog,
    p1_generation2_catalog_payload,
)
from alphafactory_crypto.broad_search.temporal_p1_semantic_proposal_v1 import propose_p1_generation2_with_dispatcher
from alphafactory_crypto.broad_search.temporal_program_search_v1 import CONFIG_PATH, _limits, _make_policy
from alphafactory_crypto.broad_search.temporal_program_v1 import compile_temporal_program_catalog, program_catalog_payload
from alphafactory_crypto.broad_search.temporal_proposal_dispatch_v1 import configure_policy_dispatcher_v1, propose_with_dispatcher_v1
from alphafactory_crypto.broad_search.temporal_realization_v2 import configure_policy_realization_v2
from alphafactory_crypto.broad_search.temporal_representation_successor_v1 import ACTIVE_FAMILIES, build_compatibility_inventory
from alphafactory_crypto.broad_search.temporal_representation_tournament_v1 import _load_frozen_inputs
from alphafactory_crypto.broad_search.temporal_successor_v1 import verify_successor_market_inputs


def _sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest().upper()


def _git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()


def _registry(root: Path, config: dict[str, Any]) -> TypedExpressionRegistry:
    rows = engine._read_json(root / "runtime/crypto_search_engine_v1_4_oi_flow_20260728/aligned_carrier_manifest.json")["contracts"]
    contracts = tuple(FieldContract(str(row["field_id"]), str(row["value_type"]), str(row["unit"]), int(row["observable_lag_hours"]), str(row["pit_authority"])) for row in rows)
    return TypedExpressionRegistry(contracts, **_limits(config))


def verify(root: Path, proposal_count: int) -> dict[str, Any]:
    if _git(root, "rev-parse", "HEAD") != _git(root, "rev-parse", "@{upstream}") or _git(root, "status", "--porcelain=v1"):
        raise RuntimeError("offline verification requires clean tracking implementation")
    market = verify_successor_market_inputs(root)
    baseline, pool = _load_frozen_inputs(root)
    config = engine._read_json(root / CONFIG_PATH)
    source_gap = engine._read_json(root / "config/crypto_p1_semantic_supply_expansion_v1_source_gap.json")
    frozen_catalog = engine._read_json(root / "config/crypto_p1_semantic_supply_expansion_v1_catalog.json")
    prior = engine._read_json(root / "config/crypto_temporal_proposal_dispatch_v1_historical_prior.json")
    temporal = compile_temporal_program_catalog(config)
    active = tuple(row for row in temporal if row[1].family_id in set(ACTIVE_FAMILIES))
    g2 = compile_p1_generation2_catalog(temporal, source_gap)
    g2_payload = p1_generation2_catalog_payload(g2, temporal)
    if g2_payload["catalog_sha256"] != frozen_catalog["catalog_sha256"]:
        raise RuntimeError("offline G2 catalog identity changed")
    registry = _registry(root, config)
    mechanism = compile_mechanism_catalog(engine._read_json(root / "config/crypto_typed_mechanism_catalog_v2_1.json"))
    inventory = build_compatibility_inventory(temporal, mechanism)
    policy = _make_policy(arm="temporal_program_evolution", seed=20260816, registry=registry, config=config, catalog=active)
    configure_policy_realization_v2(policy, pool=pool, baseline=baseline)
    configure_policy_dispatcher_v1(policy, historical_prior=prior, p1_g2_source_gap=source_gap)
    candidates = []
    pool_sizes = []
    required_features = {
        "semantic_generation", "parent_p1_program_id", "condition_role",
        "condition_primitive", "condition_operator", "condition_mode",
        "payload_identity", "semantic_novelty", "program_id",
    }
    for _ in range(proposal_count):
        candidate, metadata = propose_p1_generation2_with_dispatcher(policy, catalog=g2, scale_contract=config["time_scale_authority"])
        features = dict(metadata["dispatch_receipt"]["candidate_features"])
        if not required_features.issubset(features) or not engine._candidate_rebuild_verified(registry, candidate, {}):
            raise RuntimeError("P1 G2 proposal replay or dispatcher feature extraction failed")
        candidates.append(candidate.candidate_id)
        pool_sizes.append(int(metadata["dispatch_receipt"]["legal_candidates_generated"]))
    lane_families = {}
    for lane, family in (("P1_G1", ACTIVE_FAMILIES[0]), ("P4", ACTIVE_FAMILIES[1])):
        candidate, _ = propose_with_dispatcher_v1(policy, scale_contract=config["time_scale_authority"], inventory=inventory, allowed_families=(family,))
        lane_families[lane] = str(candidate.generation_genes["program_spec"]["family_id"])
    restored = engine._restore_policy(registry, engine._export_policy(policy))
    if restored.state_hash() != policy.state_hash():
        raise RuntimeError("proposal-only policy checkpoint restore changed")
    core = {
        "schema_version": 1,
        "status": "P1_SEMANTIC_SUPPLY_EXPANSION_PREAUTHORIZATION_OFFLINE_PASS",
        "head": _git(root, "rev-parse", "HEAD").lower(),
        "program_catalog_sha256": program_catalog_payload(temporal)["catalog_sha256"],
        "p1_g1_count": 180,
        "p1_g2_count": len(g2),
        "p1_g2_catalog_sha256": g2_payload["catalog_sha256"],
        "proposal_only_requested": proposal_count,
        "proposal_only_unique": len(set(candidates)),
        "minimum_legal_pool_size": min(pool_sizes),
        "dispatcher_feature_extraction_pass": True,
        "candidate_rebuild_pass": True,
        "policy_checkpoint_restore_pass": True,
        "lane_family_scope": lane_families,
        "p2_p3_proposals": 0,
        "market_preflight_sha256": _sha(market),
        "ledger_rows": baseline["source_strict_count"],
        "ledger_sha256": baseline["source_ledger_sha256"],
        "matched_positive": baseline["matched_positive_count"],
        "target_basins": pool["target_basin_count"],
        "frozen_parents": pool["frozen_parent_candidate_count"],
        "parent_pool_sha256": pool["target_parent_pool_sha256"],
        "market_arrays_read": 0,
        "candidate_evaluations": 0,
        "validation_reads": 0,
        "oos_reads": 0,
        "holdout_reads": 0,
        "forward_reads": 0,
        "promotion_reads": 0,
        "sealed_reads": 0,
    }
    return {**core, "offline_preflight_sha256": _sha(core)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--proposal-count", type=int, default=64)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = verify(args.repo_root.resolve(), args.proposal_count)
    if args.output:
        engine._write_json(args.output, result)
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
