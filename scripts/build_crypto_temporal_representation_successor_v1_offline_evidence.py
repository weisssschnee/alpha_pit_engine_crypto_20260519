from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from alphafactory_crypto.broad_search.compositional18m import (
    FieldContract,
    compile_mechanism_catalog,
)
from alphafactory_crypto.broad_search.expression import TypedExpressionRegistry
from alphafactory_crypto.broad_search.temporal_program_search_v1 import (
    CONFIG_PATH,
    _limits,
    _make_policy,
)
from alphafactory_crypto.broad_search.temporal_program_v1 import (
    compile_temporal_program_catalog,
)
from alphafactory_crypto.broad_search.temporal_realization_v2 import (
    configure_policy_realization_v2,
)
from alphafactory_crypto.broad_search.temporal_representation_successor_v1 import (
    ACTIVE_FAMILIES,
    build_compatibility_inventory,
    compatibility_inventory_payload,
    lossless_embedding_benchmark,
    offline_closure_benchmark,
)
from alphafactory_crypto.broad_search.temporal_representation_tournament_v1 import (
    BASELINE_PATH,
    EVOLUTION_PROBABILITIES,
    MECHANISM_CATALOG_PATH,
    OFFLINE_EVIDENCE_PATH,
)
from alphafactory_crypto.broad_search.temporal_targeted_deepening_v1 import (
    build_frozen_target_parent_pool,
)


def sha(value) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "utf-8"
        )
    ).hexdigest().upper()


def registry(repo_root: Path, config) -> TypedExpressionRegistry:
    rows = json.loads(
        (
            repo_root
            / "runtime/crypto_search_engine_v1_4_oi_flow_20260728/aligned_carrier_manifest.json"
        ).read_text(encoding="utf-8")
    )["contracts"]
    contracts = tuple(
        FieldContract(
            str(row["field_id"]),
            str(row["value_type"]),
            str(row["unit"]),
            int(row["observable_lag_hours"]),
            str(row["pit_authority"]),
        )
        for row in rows
    )
    return TypedExpressionRegistry(contracts, **_limits(config))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--descendant-bundle", type=Path, required=True)
    parser.add_argument("--pairs-per-basin", type=int, default=24)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    config = json.loads((root / CONFIG_PATH).read_text(encoding="utf-8"))
    config["policy_parameters"]["temporal_program_evolution"].update(
        EVOLUTION_PROBABILITIES
    )
    temporal = compile_temporal_program_catalog(config)
    mechanism = compile_mechanism_catalog(
        json.loads((root / MECHANISM_CATALOG_PATH).read_text(encoding="utf-8"))
    )
    inventory = build_compatibility_inventory(temporal, mechanism)
    local_registry = registry(root, config)
    baseline = json.loads((root / BASELINE_PATH).read_text(encoding="utf-8-sig"))
    pool = build_frozen_target_parent_pool(root, baseline)
    active = tuple(pair for pair in temporal if pair[1].family_id in set(ACTIVE_FAMILIES))
    policy = _make_policy(
        arm="temporal_program_evolution",
        seed=20260814,
        registry=local_registry,
        config=config,
        catalog=active,
    )
    configure_policy_realization_v2(policy, pool=pool, baseline=baseline)
    descendants = json.loads(args.descendant_bundle.read_text(encoding="utf-8"))
    inventory_result = compatibility_inventory_payload(
        inventory,
        total_temporal_programs=len(temporal),
        total_mechanisms=len(mechanism),
    )
    embedding = lossless_embedding_benchmark(
        registry=local_registry,
        temporal_catalog=temporal,
        scale_contract=config["time_scale_authority"],
        inventory=inventory,
    )
    closure = offline_closure_benchmark(
        policies={"offline": policy},
        pool=pool,
        registry=local_registry,
        scale_contract=config["time_scale_authority"],
        inventory=inventory,
        pairs_per_basin=args.pairs_per_basin,
        descendant_records=descendants["descendants"],
    )
    status = (
        "OFFLINE_CLOSURE_PASS_READY_FOR_TOURNAMENT"
        if embedding["pass"] and closure["expanded_legal_support"]
        else "SEARCH_REPRESENTATION_IMPLEMENTATION_INVALID"
    )
    core = {
        "schema_version": 1,
        "status": status,
        "compatibility_inventory": inventory_result,
        "lossless_embedding": embedding,
        "closure_benchmark": closure,
        "descendant_bundle_path": str(args.descendant_bundle.resolve()),
        "descendant_bundle_sha256": hashlib.sha256(
            args.descendant_bundle.read_bytes()
        ).hexdigest().upper(),
        "descendant_bundle_receipt_sha256": descendants["receipt_sha256"],
        "frozen_parent_pool_sha256": pool["target_parent_pool_sha256"],
        "market_arrays_read": 0,
        "candidate_evaluations": 0,
        "validation_reads": 0,
        "oos_reads": 0,
        "sealed_reads": 0,
    }
    output = {**core, "offline_evidence_sha256": sha(core)}
    path = root / OFFLINE_EVIDENCE_PATH
    path.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({"path": str(path), "status": status, "offline_evidence_sha256": output["offline_evidence_sha256"]}, sort_keys=True))
    return 0 if status != "SEARCH_REPRESENTATION_IMPLEMENTATION_INVALID" else 2


if __name__ == "__main__":
    raise SystemExit(main())
