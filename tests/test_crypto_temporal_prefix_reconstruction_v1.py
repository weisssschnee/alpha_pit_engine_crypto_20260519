from __future__ import annotations

import gzip
import json
from pathlib import Path

import pandas as pd
import pytest

from alphafactory_crypto.broad_search.temporal_prefix_reconstruction_v1 import (
    _authority_identity_from_frozen,
    _file_sha,
    _json_sha,
    _reconstruct_evolution_learning_state,
    _source_artifact_identity,
    _suffix_adaptive_mutation_rows,
    check_successor_preflight,
    successor_receipt_payload,
)


def _ordering(value: float) -> dict[str, object]:
    return {
        "authority": "DEVELOPMENT_THREE_BLOCK_ROBUST_ORDERING_V1",
        "replicated_positive_block_count": int(value > 0.0),
        "worst_block_min_matched_net_mean": value,
        "median_block_joint_search_reward": value,
        "max_required_mean_one_way_turnover": 0.1,
        "min_required_support": 0.8,
    }


def test_evolution_learning_state_reconstructs_family_champions() -> None:
    rows = pd.DataFrame(
        [
            {
                "candidate_id": "candidate-a",
                "behavior_family_id": "family-1",
                "policy_local_family_count_at_completion": 1,
                "search_reward": 0.1,
                "candidate_spec_json": json.dumps({"candidate_id": "candidate-a"}),
                "block_robust_ordering_json": json.dumps(_ordering(0.1)),
                "operation": "MECHANISM_PARAMETER_GROUP_MUTATION_1_TO_3",
            },
            {
                "candidate_id": "candidate-b",
                "behavior_family_id": "family-1",
                "policy_local_family_count_at_completion": 2,
                "search_reward": 0.2,
                "candidate_spec_json": json.dumps({"candidate_id": "candidate-b"}),
                "block_robust_ordering_json": json.dumps(_ordering(0.2)),
                "operation": "COMPATIBLE_MECHANISM_SPEC_MUTATION",
            },
            {
                "candidate_id": "candidate-c",
                "behavior_family_id": "family-2",
                "policy_local_family_count_at_completion": 1,
                "search_reward": -0.1,
                "candidate_spec_json": json.dumps({"candidate_id": "candidate-c"}),
                "block_robust_ordering_json": json.dumps(_ordering(-0.1)),
                "operation": "ONE_POINT_TYPED_MECHANISM_CROSSOVER",
            },
        ]
    )
    state = _reconstruct_evolution_learning_state(
        rows,
        parameters={
            "selection_authority": "DEVELOPMENT_THREE_BLOCK_ROBUST_ORDERING_V1",
            "population_limit": 2,
        },
    )
    assert set(state["population"]) == {"candidate-b", "candidate-c"}
    assert state["verified_parameter_mutations"] == 1
    assert state["verified_mechanism_mutations"] == 1
    assert state["verified_crossovers"] == 1


def test_suffix_adaptive_mutation_detection_is_fail_closed() -> None:
    candidates = pd.DataFrame(
        [
            {"completion_ordinal": 30_001, "arm": "temporal_program_random"},
            {"completion_ordinal": 30_002, "arm": "temporal_program_evolution"},
        ]
    )
    rejected = pd.DataFrame(
        [
            {"checkpoint_index": 15, "policy_key": "temporal_program_cem|7"},
        ]
    )
    assert _suffix_adaptive_mutation_rows(candidates, rejected, 30_000) == {
        "candidate_rows": 1,
        "rejected_rows": 1,
    }


def test_successor_receipt_requires_passed_prefix_reconstruction() -> None:
    authority_identity = {
        "source_frozen_contract_sha256": "C" * 64,
        "source_producer_sha": "d" * 40,
        "economic_receipt_sha256": "E" * 64,
        "target_contract_sha256": "F" * 64,
        "target_execution_sha256": "1" * 64,
        "portfolio_mapping_and_cost_sha256": "2" * 64,
        "optimizer_reward_and_matched_attribution_sha256": "3" * 64,
        "market_contract_sha256": "4" * 64,
        "program_catalog_sha256": "5" * 64,
        "behavior_contract_sha256": "6" * 64,
    }
    with pytest.raises(RuntimeError, match="PREFIX_POLICY_STATE_RECONSTRUCTION_FAIL"):
        successor_receipt_payload(
            reconstruction={"status": "PREFIX_POLICY_STATE_RECONSTRUCTION_FAIL"},
            reconstructed_policy_bundle_sha256="A" * 64,
            source_artifact_identity_sha256="B" * 64,
        )

    payload = successor_receipt_payload(
        reconstruction={
            "status": "PREFIX_POLICY_STATE_RECONSTRUCTION_PASS",
            "valid_prefix_boundary": 30_000,
            "sealed_reads": 0,
            "candidate_reevaluations": 0,
            "authority_identity": authority_identity,
        },
        reconstructed_policy_bundle_sha256="A" * 64,
        source_artifact_identity_sha256="B" * 64,
    )
    assert payload["source_evidence_prefix"] == 30_000
    assert payload["development_adaptive_policy_changed_after_observing_30k"] is True
    assert payload["allocation"] == {
        "FRESH_RANDOM_CONTROL_AFTER_30K": 0.20,
        "temporal_program_evolution": 0.60,
        "temporal_program_cem": 0.20,
    }
    assert payload["run_authorized"] is False
    assert payload["boundaries"]["validation"] is False
    assert payload["boundaries"]["oos"] is False


def test_independent_preflight_fails_closed_on_authority_or_boundary_drift(
    tmp_path: Path,
) -> None:
    artifact_root = tmp_path / "source"
    checkpoint = artifact_root / "checkpoints/checkpoint_017"
    checkpoint.mkdir(parents=True)
    source_sha = "d" * 40
    frozen = {
        "source_sha": source_sha,
        "sealed_reads": 0,
        "behavior_contract_sha256": "A" * 64,
        "program_catalog_sha256": "B" * 64,
        "config": {"market_contract": {"target": "BINANCE", "cost": "5BPS"}},
        "economic_receipt": {
            "receipt_sha256": "C" * 64,
            "component_sha256": {
                "target_contract": "D" * 64,
                "target_execution": "E" * 64,
                "portfolio_mapping_and_cost": "F" * 64,
                "optimizer_reward_and_matched_attribution": "1" * 64,
            },
        },
    }
    source_files = {
        checkpoint / "manifest.json": b"manifest",
        checkpoint / "state.json": b"state",
        artifact_root / "candidate_ledger.parquet": b"candidate-ledger",
        artifact_root / "rejected_candidate_ledger.parquet": b"rejected-ledger",
    }
    for path, payload in source_files.items():
        path.write_bytes(payload)
    frozen_path = artifact_root / "frozen_contract.json"
    frozen_path.write_text(
        json.dumps(frozen, sort_keys=True) + "\n", encoding="utf-8"
    )
    input_hashes = {
        "manifest.json": _file_sha(checkpoint / "manifest.json"),
        "state.json": _file_sha(checkpoint / "state.json"),
        "candidate_ledger.parquet": _file_sha(
            artifact_root / "candidate_ledger.parquet"
        ),
        "rejected_candidate_ledger.parquet": _file_sha(
            artifact_root / "rejected_candidate_ledger.parquet"
        ),
        "frozen_contract.json": _file_sha(frozen_path),
    }
    source_identity = _source_artifact_identity(
        checkpoint="checkpoint_017",
        source_sha=source_sha,
        input_hashes=input_hashes,
        prefix_boundary=30_000,
    )
    reconstruction = {
        "status": "PREFIX_POLICY_STATE_RECONSTRUCTION_PASS",
        "source_checkpoint": "checkpoint_017",
        "source_producer_sha": source_sha,
        "source_artifact_identity_sha256": source_identity,
        "input_hashes": input_hashes,
        "authority_identity": _authority_identity_from_frozen(frozen),
        "valid_prefix_boundary": 30_000,
        "invalid_suffix_start": 30_001,
        "economic_prefix_valid": True,
        "orchestration_terminal_invalid": True,
        "market_arrays_read": 0,
        "candidate_reevaluations": 0,
        "sealed_reads": 0,
    }
    bundle_path = tmp_path / "bundle.json.gz"
    with bundle_path.open("wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as compressed:
            compressed.write(
                json.dumps(
                    {
                        "status": "PREFIX_POLICY_STATE_RECONSTRUCTION_PASS",
                        "source_evidence_prefix": 30_000,
                        "source_artifact_identity_sha256": source_identity,
                        "random_state_scope": "FRESH_RANDOM_CONTROL_AFTER_30K",
                    },
                    sort_keys=True,
                ).encode("utf-8")
            )
    receipt = successor_receipt_payload(
        reconstruction=reconstruction,
        reconstructed_policy_bundle_sha256=_file_sha(bundle_path),
        source_artifact_identity_sha256=source_identity,
    )
    passed = check_successor_preflight(
        reconstruction=reconstruction,
        receipt=receipt,
        bundle_path=bundle_path,
        artifact_root=artifact_root,
    )
    assert passed["status"] == "PASS"

    drifted = json.loads(json.dumps(receipt))
    drifted["unchanged_authorities"]["target"] = False
    drifted["receipt_sha256"] = _json_sha(
        {key: value for key, value in drifted.items() if key != "receipt_sha256"}
    )
    failed = check_successor_preflight(
        reconstruction=reconstruction,
        receipt=drifted,
        bundle_path=bundle_path,
        artifact_root=artifact_root,
    )
    assert failed["status"] == "FAIL"
    assert "unchanged_authorities" in failed["errors"]

    drifted = json.loads(json.dumps(receipt))
    drifted["source_evidence_prefix"] = 29_000
    drifted["development_adaptive_policy_changed_after_observing_30k"] = False
    drifted["receipt_sha256"] = _json_sha(
        {key: value for key, value in drifted.items() if key != "receipt_sha256"}
    )
    failed = check_successor_preflight(
        reconstruction=reconstruction,
        receipt=drifted,
        bundle_path=bundle_path,
        artifact_root=artifact_root,
    )
    assert failed["status"] == "FAIL"
    assert "successor_search_contract" in failed["errors"]
