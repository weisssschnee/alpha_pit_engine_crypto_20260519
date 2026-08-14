from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from alphafactory_crypto.broad_search import search_engine_v1 as engine
from alphafactory_crypto.broad_search.expression import FieldContract, TypedExpressionRegistry
from alphafactory_crypto.broad_search.temporal_program_search_v1 import (
    _later_policies,
    _realization_v2_effective_config,
)
from alphafactory_crypto.broad_search.temporal_program_v1 import compile_temporal_program_catalog
from alphafactory_crypto.broad_search.temporal_realization_v2 import (
    configure_policy_realization_v2,
    observe_realization_v2,
)
from alphafactory_crypto.broad_search.temporal_targeted_deepening_v1 import (
    ECONOMIC_FINGERPRINT_FIELDS,
)


def registry(repo_root: Path, config: dict) -> TypedExpressionRegistry:
    manifest = json.loads(
        (repo_root / "runtime/crypto_search_engine_v1_4_oi_flow_20260728/aligned_carrier_manifest.json").read_text(encoding="utf-8")
    )
    contracts = tuple(
        FieldContract(
            str(row["field_id"]), str(row["value_type"]), str(row["unit"]),
            int(row["observable_lag_hours"]), str(row["pit_authority"]),
        )
        for row in manifest["contracts"]
    )
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--count-per-lane", type=int, default=50)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    evidence = args.evidence_root.resolve()
    config = _realization_v2_effective_config(
        json.loads((root / "config/crypto_temporal_mechanism_program_v1.json").read_text(encoding="utf-8"))
    )
    catalog = compile_temporal_program_catalog(config)
    policies = _later_policies(
        registry=registry(root, config), config=config, catalog=catalog,
        active_families=(
            "P1_POSITION_STATE_CHANGE_TO_RESPONSE",
            "P4_MULTISCALE_STATE_X_TRANSITION_ROUTING",
        ),
    )
    pool = json.loads((evidence / "targeted_frozen_parent_pool.json").read_text(encoding="utf-8"))
    baseline = json.loads((evidence / "targeted_deepening_diagnostic_baseline.json").read_text(encoding="utf-8"))
    evolution = {
        key: value for key, value in policies.items()
        if key.startswith("temporal_program_evolution|")
    }
    for policy in evolution.values():
        configure_policy_realization_v2(policy, pool=pool, baseline=baseline)
    rows = []
    archive_fixture = None
    proposal_failures: Counter[str] = Counter()

    def propose_success(policy):
        while True:
            try:
                return policy.propose()
            except (ValueError, RuntimeError) as failure:
                proposal_failures[type(failure).__name__ + ":" + str(failure)] += 1
    for key, policy in sorted(evolution.items()):
        for _ in range(args.count_per_lane):
            candidate, metadata = propose_success(policy)
            receipt = metadata["receipt"]
            parent_records = [policy._targeted_parent_record(value) for value in metadata["parent_ids"]]
            if any(
                str(record["economic_similarity_cluster_id"])
                != str(receipt["targeted_economic_basin_id"])
                for record in parent_records
            ):
                raise RuntimeError("cross-basin parent contamination")
            rows.append(
                {
                    "policy_key": key,
                    "candidate_id": candidate.candidate_id,
                    "requested": receipt["requested_operation"],
                    "realized": receipt["realized_operation"],
                    "fallback": bool(receipt["crossover_fallback"]),
                    "fallback_reason": receipt.get("fallback_reason"),
                    "legal_splice_count": int(receipt.get("legal_splice_count") or 0),
                    "receipt_verified": bool(metadata["receipt_verified"]),
                    "parent_source_types": receipt["targeted_parent_source_types"],
                }
            )
            if archive_fixture is None:
                archive_fixture = (policy, candidate, receipt)
    key, policy = sorted(evolution.items())[0]
    restored = engine.MechanismEvolutionV2.from_state(policy.registry, policy.export_state())
    before = policy.state_hash()
    if restored.state_hash() != before:
        raise RuntimeError("checkpoint restore state hash changed")
    while True:
        try:
            candidate_a, metadata_a = policy.propose()
            break
        except (ValueError, RuntimeError):
            pass
    while True:
        try:
            candidate_b, metadata_b = restored.propose()
            break
        except (ValueError, RuntimeError):
            pass
    exact_replay = (
        candidate_a.candidate_id == candidate_b.candidate_id
        and metadata_a["receipt"] == metadata_b["receipt"]
        and policy.state_hash() == restored.state_hash()
    )
    assert archive_fixture is not None
    fixture_policy, fixture_candidate, fixture_receipt = archive_fixture
    archive_a = engine.MechanismEvolutionV2.from_state(
        fixture_policy.registry, fixture_policy.export_state()
    )
    archive_b = engine.MechanismEvolutionV2.from_state(
        fixture_policy.registry, fixture_policy.export_state()
    )
    parent_id = fixture_receipt["parent_ids"][0]
    parent = fixture_policy._targeted_parent_record(parent_id)
    baseline_row = fixture_policy.realization_v2_state["baseline_rows"][parent_id]
    archive_row = {
        "receipt": fixture_receipt,
        "realization_v2_economic_fingerprint": {
            field: baseline_row.get(field) for field in ECONOMIC_FINGERPRINT_FIELDS
        },
        "behavior_family_id": "OFFLINE_ARCHIVE_REPLAY",
        "policy_local_family_count_at_completion": 1,
        "search_reward": parent["search_reward"],
        "block_robust_ordering": parent["block_robust_ordering"],
        "mapped_weight_descriptor_id": baseline_row.get("mapped_weight_descriptor_id"),
        "turnover_path_descriptor_id": baseline_row.get("turnover_path_descriptor_id"),
        "selected_asset_overlap_id": baseline_row.get("selected_asset_overlap_id"),
    }
    observe_realization_v2(archive_a, fixture_candidate, archive_row)
    observe_realization_v2(archive_b, fixture_candidate, archive_row)
    archive_replay = archive_a.state_hash() == archive_b.state_hash()
    archive_admitted = int(
        archive_a.realization_v2_state["admission_counts"]["admitted"]
    )
    rejection_policy = engine.MechanismEvolutionV2.from_state(
        fixture_policy.registry, fixture_policy.export_state()
    )
    other_basin = next(
        value for value in rejection_policy.targeted_basin_order
        if value != fixture_receipt["targeted_economic_basin_id"]
    )
    rejected_row = dict(archive_row)
    rejected_row["receipt"] = {
        **fixture_receipt,
        "targeted_economic_basin_id": other_basin,
    }
    observe_realization_v2(rejection_policy, fixture_candidate, rejected_row)
    cross_basin_rejection = int(
        rejection_policy.realization_v2_state["admission_counts"]["cross_basin_rejected"]
    )
    requested = Counter(row["requested"] for row in rows)
    realized = Counter(row["realized"] for row in rows)
    crossover = [row for row in rows if row["requested"] == "crossover"]
    fallback = [row for row in crossover if row["fallback"]]
    output = {
        "schema_version": 1,
        "status": "PASS" if exact_replay and archive_replay and archive_admitted == 1 and cross_basin_rejection == 1 and all(row["receipt_verified"] for row in rows) else "FAIL",
        "proposal_only": True,
        "market_arrays_read": 0,
        "candidate_evaluations": 0,
        "validation_reads": 0,
        "oos_reads": 0,
        "sealed_reads": 0,
        "proposal_count": len(rows),
        "requested_operation_counts": dict(sorted(requested.items())),
        "realized_operation_counts": dict(sorted(realized.items())),
        "crossover_requested": len(crossover),
        "crossover_realized": sum(row["realized"] == "crossover" for row in crossover),
        "crossover_fallback": len(fallback),
        "crossover_fallback_rate": len(fallback) / max(1, len(crossover)),
        "fallback_reasons": dict(Counter(str(row["fallback_reason"]) for row in fallback)),
        "proposal_failures": dict(sorted(proposal_failures.items())),
        "legal_splice_count": [row["legal_splice_count"] for row in crossover if row["realized"] == "crossover"],
        "cross_basin_parent_contamination": 0,
        "all_parent_sources_legal": all(
            set(row["parent_source_types"]).issubset({"FROZEN_TRAIN_ONLY_BASELINE", "ADAPTIVE_STRICT_DESCENDANT"})
            for row in rows
        ),
        "receipt_replay": all(row["receipt_verified"] for row in rows),
        "checkpoint_exact_replay": exact_replay,
        "archive_state_hash_replay": archive_replay,
        "archive_admitted_descendants": archive_admitted,
        "cross_basin_archive_rejection": cross_basin_rejection,
        "frozen_parent_pool_sha256": pool["target_parent_pool_sha256"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(output, sort_keys=True))
    if output["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
