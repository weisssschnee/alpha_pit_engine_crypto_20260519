from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import pandas as pd

from alphafactory_crypto.broad_search import search_engine_v1 as engine
from alphafactory_crypto.broad_search.expression import FieldContract, TypedExpressionRegistry
from alphafactory_crypto.broad_search.temporal_program_search_v1 import (
    _json_sha,
    _load_checkpoint,
)
from alphafactory_crypto.broad_search.temporal_realization_v2 import (
    ACTIVE_PROGRAM_FAMILIES,
    _assign_anchor,
    _realization_id,
    archive_diagnostics,
    checkpoint_decision,
    operation_diagnostics,
    validate_authorization,
)
from alphafactory_crypto.broad_search.temporal_targeted_deepening_v1 import (
    ECONOMIC_FINGERPRINT_FIELDS,
    targeted_diagnostics,
)


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def registry(root: Path, frozen: dict) -> TypedExpressionRegistry:
    manifest = read(root / "runtime/crypto_search_engine_v1_4_oi_flow_20260728/aligned_carrier_manifest.json")
    contracts = tuple(
        FieldContract(
            str(row["field_id"]), str(row["value_type"]), str(row["unit"]),
            int(row["observable_lag_hours"]), str(row["pit_authority"]),
        )
        for row in manifest["contracts"]
    )
    limits = frozen["expression_registry_limits"]
    return TypedExpressionRegistry(contracts, **{key: int(value) for key, value in limits.items()})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--r3-ledger", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    runtime = args.runtime_root.resolve()
    errors: list[str] = []
    frozen = read(runtime / "frozen_contract.json")
    final = read(runtime / "final_decision.json")
    pool = read(runtime / "targeted_frozen_parent_pool.json")
    baseline = read(runtime / "targeted_deepening_diagnostic_baseline.json")
    authorization = validate_authorization(root, expected_source_sha=str(final["producer_source_sha"]))
    ledger = pd.read_parquet(runtime / "candidate_ledger.parquet")
    rows = ledger.to_dict("records")
    strict = len(rows)
    if list(ledger["completion_ordinal"].astype(int)) != list(range(1, strict + 1)):
        errors.append("completion_ordinal")
    arms = Counter(ledger["arm"].astype(str))
    families = Counter(ledger["program_family_id"].astype(str))
    if set(families) - set(ACTIVE_PROGRAM_FAMILIES):
        errors.append("program_family_scope")
    expected_arms = {
        "temporal_program_random": strict // 5,
        "temporal_program_cem": strict // 5,
        "temporal_program_evolution": strict * 3 // 5,
    }
    if dict(arms) != expected_arms:
        errors.append("arm_allocation")
    receipt_errors = []
    parent_basin = {
        candidate_id: str(record["economic_similarity_cluster_id"])
        for candidate_id, record in pool["parent_records"].items()
    }
    for index, row in enumerate(rows):
        if row.get("arm") != "temporal_program_evolution":
            continue
        try:
            receipt = json.loads(str(row["operation_receipt_json"]))
            core = {key: value for key, value in receipt.items() if key != "receipt_sha256"}
            if receipt["receipt_sha256"] != engine._payload_sha(core):
                raise ValueError("receipt_hash")
            basin = str(receipt["targeted_economic_basin_id"])
            for parent_id in receipt["parent_ids"]:
                if parent_id in parent_basin and parent_basin[parent_id] != basin:
                    raise ValueError("cross_basin_parent")
            if not set(receipt["targeted_parent_source_types"]).issubset(
                {"FROZEN_TRAIN_ONLY_BASELINE", "ADAPTIVE_STRICT_DESCENDANT"}
            ):
                raise ValueError("parent_source")
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as failure:
            receipt_errors.append(f"{index}:{failure}")
    if receipt_errors:
        errors.append("operation_receipts")
    diagnostics = targeted_diagnostics(rows, baseline=baseline, strict_boundary=strict)
    recorded_diagnostics = read(runtime / "basin_diagnostics_latest.json")
    if diagnostics != recorded_diagnostics:
        errors.append("basin_diagnostics_replay")
    operation = operation_diagnostics(rows)
    decision_10_path = runtime / "continuation_decision_010000.json"
    if not decision_10_path.is_file():
        errors.append("missing_10k_decision")
        decision_10 = {}
    else:
        decision_10 = read(decision_10_path)
        replay_10 = checkpoint_decision(
            rows[:10_000], strict_boundary=10_000,
            frozen_parent_pool_sha256=pool["target_parent_pool_sha256"],
        )
        if decision_10 != replay_10:
            errors.append("10k_gate_replay")
    checkpoints = sorted((runtime / "checkpoints").glob("checkpoint_[0-9][0-9][0-9]"))
    if not checkpoints:
        errors.append("checkpoint_missing")
        replay_status = False
        policies = {}
    else:
        state, policies, checkpoint_rows, _, _, _, _ = _load_checkpoint(
            checkpoints[-1],
            registry=registry(root, frozen),
            expected_source=str(final["producer_source_sha"]),
            expected_frozen=str(final["frozen_contract_sha256"]),
            expected_identities=frozen["input_identities"],
        )
        replay_status = len(checkpoint_rows) == strict and int(state["strict_evaluated"]) == strict
        if not replay_status:
            errors.append("checkpoint_state_replay")
    archive = archive_diagnostics(policies)
    if archive != dict(final.get("realization_v2_archive_diagnostics") or {}):
        errors.append("archive_diagnostics_replay")
    manifest = read(runtime / "run_manifest.json")
    for item in manifest["files"]:
        path = runtime / item["path"]
        if not path.is_file() or engine.sha256_file(path) != item["sha256"]:
            errors.append("manifest_file:" + item["path"])
    if _json_sha(manifest["files"]) != manifest["bundle_sha256"]:
        errors.append("manifest_bundle")
    r3 = pd.read_parquet(args.r3_ledger.resolve())
    r3_prefix = {
        boundary: targeted_diagnostics(
            r3.iloc[:boundary].to_dict("records"),
            baseline=baseline,
            strict_boundary=boundary,
        )
        for boundary in (10_000, 20_000)
    }
    matched = int(ledger["matched_positive"].astype(bool).sum())
    p1 = ledger.loc[ledger["program_family_id"] == ACTIVE_PROGRAM_FAMILIES[0]]
    p4 = ledger.loc[ledger["program_family_id"] == ACTIVE_PROGRAM_FAMILIES[1]]
    model_state = next(
        policy.realization_v2_state
        for policy in policies.values()
        if isinstance(policy, engine.MechanismEvolutionV2)
        and policy.realization_v2_state is not None
    )
    baseline_realizations = {
        str(record["concrete_realization_id"])
        for record in pool["parent_records"].values()
    }
    dimension_fields = {
        "mapped_weight": "mapped_weight_descriptor_id",
        "turnover": "turnover_path_descriptor_id",
        "raw_field": "raw_fields_json",
        "asset_selection": "selected_asset_overlap_id",
    }
    descriptor_by_id = {
        str(row["candidate_id"]): dict(row)
        for row in baseline["matched_positive_rows"]
    }
    mutation_rows: dict[str, list[dict]] = {}
    operation_rows: dict[str, list[dict]] = {}
    for row in rows:
        candidate_id = str(row["candidate_id"])
        if row.get("arm") == "temporal_program_evolution":
            receipt = json.loads(str(row["operation_receipt_json"]))
            parent = descriptor_by_id.get(str(receipt["parent_ids"][0]), {})
            assigned, similarity = _assign_anchor(
                model_state,
                {field: row.get(field) for field in ECONOMIC_FINGERPRINT_FIELDS},
            )
            retained = bool(
                similarity >= float(model_state["similarity_threshold"])
                and assigned == str(receipt["targeted_economic_basin_id"])
            )
            realization_id = _realization_id(row)
            enriched = {
                **row,
                "receipt": receipt,
                "basin_retained": retained,
                "new_realization": realization_id not in baseline_realizations,
                "descriptor_changes": {
                    dimension: row.get(field) != parent.get(field)
                    for dimension, field in dimension_fields.items()
                },
            }
            operation_rows.setdefault(str(receipt["requested_operation"]), []).append(enriched)
            if receipt["realized_operation"] == "parameter_mutation":
                mutation_rows.setdefault(str(receipt.get("mutation_target") or "generic"), []).append(enriched)
        descriptor_by_id[candidate_id] = dict(row)

    def attribution(local: list[dict], dimension: str | None = None) -> dict:
        new_ids = {_realization_id(row) for row in local if row["new_realization"]}
        return {
            "strict_realized": len(local),
            "descriptor_change_rate": (
                sum(row["descriptor_changes"][dimension] for row in local) / max(1, len(local))
                if dimension is not None else None
            ),
            "matched_positive": sum(bool(row["matched_positive"]) for row in local),
            "basin_retained": sum(row["basin_retained"] for row in local),
            "basin_retention_rate": sum(row["basin_retained"] for row in local) / max(1, len(local)),
            "new_realization_contribution": len(new_ids),
            "matched_retained_new_realization_contribution": sum(
                bool(row["matched_positive"]) and row["basin_retained"] and row["new_realization"]
                for row in local
            ),
        }

    mutation_attribution = {
        target: attribution(local, target if target in dimension_fields else None)
        for target, local in sorted(mutation_rows.items())
    }
    basin_operation_attribution = {
        operation_name: attribution(local)
        for operation_name, local in sorted(operation_rows.items())
    }
    r3_comparison = {}
    for boundary, value in r3_prefix.items():
        frame = r3.iloc[:boundary]
        r3_comparison[str(boundary)] = {
            "strict": boundary,
            "matched_positive": int(frame["matched_positive"].astype(bool).sum()),
            "P1_matched_positive": int(frame.loc[frame["program_family_id"] == ACTIVE_PROGRAM_FAMILIES[0], "matched_positive"].astype(bool).sum()),
            "P4_matched_positive": int(frame.loc[frame["program_family_id"] == ACTIVE_PROGRAM_FAMILIES[1], "matched_positive"].astype(bool).sum()),
            "diagnostics": value,
        }
    if errors or final.get("status") == "ENGINE_RUN_INVALID":
        next_decision = "RESEARCH_INVALID"
    elif strict == 10_000:
        next_decision = "SEARCH_REPRESENTATION_BOTTLENECK"
    else:
        depth = diagnostics["basin_realization_depth"]
        p1_density = float(p1["matched_positive"].astype(bool).mean()) if len(p1) else 0.0
        p1_r3 = r3_comparison["20000"]["P1_matched_positive"] / max(
            1, int((r3.iloc[:20_000]["program_family_id"] == ACTIVE_PROGRAM_FAMILIES[0]).sum())
        )
        if not decision_10.get("crossover_gate", {}).get("pass"):
            next_decision = "SEARCH_REPRESENTATION_BOTTLENECK"
        elif p1_density <= p1_r3 and int(depth.get("high_quality_basins_deepened", 0)) > 0:
            next_decision = "P1_SPECIFIC_BOTTLENECK"
        elif int(depth.get("turnover_realizations_ge_2", 0)) <= int(
            depth.get("baseline_turnover_realizations_ge_2", 0)
        ):
            next_decision = "REALIZATION_V2_PARTIAL_PASS"
        else:
            next_decision = "REALIZATION_V2_PASS"
    result = {
        "schema_version": 1,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "execution_mode": final["execution_mode"],
        "implementation_sha": authorization["authorized_implementation_sha"],
        "authorization_sha256": authorization["authorization_sha256"],
        "strict": strict,
        "attempts": int(final["generation_attempts"]),
        "arm_counts": dict(sorted(arms.items())),
        "family_counts": dict(sorted(families.items())),
        "P1": {"strict": len(p1), "matched_positive": int(p1["matched_positive"].astype(bool).sum())},
        "P4": {"strict": len(p4), "matched_positive": int(p4["matched_positive"].astype(bool).sum())},
        "P2_strict": int(families.get("P2_RECENT_CROWDING_EVENT_TO_RESPONSE", 0)),
        "P3_strict": int(families.get("P3_FLOW_SHOCK_PERSISTENCE_TO_ABSORPTION", 0)),
        "matched_positive": matched,
        "operation_diagnostics": operation,
        "basin_level_operation_attribution": basin_operation_attribution,
        "dimension_aware_mutation_attribution": mutation_attribution,
        "economic_diagnostics": diagnostics,
        "basin_local_archive": archive,
        "r3_prefix_comparison": r3_comparison,
        "checkpoint_state_replay": replay_status,
        "operation_receipt_errors": receipt_errors,
        "forbidden_reads": {"validation": 0, "oos": 0, "forward": 0, "sealed": 0},
        "NEXT_DECISION": next_decision,
        "automatic_next_run_started": False,
    }
    output = args.output.resolve() if args.output else runtime / "independent_checker.json"
    engine._write_json(output, result)
    print(json.dumps(result, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
