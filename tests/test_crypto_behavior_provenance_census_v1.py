from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd
import pytest

from alphafactory_crypto.broad_search.behavior_provenance_census import (
    build_behavior_provenance_census,
    load_behavior_provenance_census_contract,
    verify_authoritative_legacy_v24,
    write_behavior_provenance_census,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def _sha(payload: dict) -> str:
    return hashlib.sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
    ).hexdigest().upper()


def _comparison(
    *,
    first_equal_stage: str | None,
    primary_label: str = "primary",
    control_label: str = "left_control",
) -> dict:
    order = [
        "SIGNAL",
        "RANK",
        "SELECTION",
        "CAPPED_WEIGHT",
        "MAPPED_WEIGHT",
        "EXECUTABLE_WEIGHT",
    ]
    first = order.index(first_equal_stage) if first_equal_stage else len(order)
    payload = {
        "schema_version": "CRYPTO_CONTROL_DEGENERACY_PROVENANCE_V1",
        "primary_label": primary_label,
        "control_label": control_label,
        "mapping_id": "CROSS_SECTIONAL_ZERO_NET",
        "stage_order": order,
        "stages": {
            stage: {
                "primary_identity_sha256": ("A" if index < first else "C")
                * 64,
                "control_identity_sha256": ("B" if index < first else "C")
                * 64,
                "equal": index >= first,
            }
            for index, stage in enumerate(order)
        },
        "first_equal_stage": first_equal_stage,
        "final_weight_equal": first_equal_stage is not None,
        "primary_mapping_provenance_sha256": "D" * 64,
        "control_mapping_provenance_sha256": "E" * 64,
        "rank_comparison": {},
        "identity_excludes": ["target", "target_ic", "reward"],
    }
    payload["provenance_sha256"] = _sha(payload)
    return payload


def _bound(
    *,
    candidate_id: str,
    candidate_spec_sha256: str,
    comparison: dict | None = None,
    successful_pair: bool = False,
) -> tuple[str, str]:
    if successful_pair:
        inner = {
            "schema_version": "CRYPTO_PAIR_CONTROL_PROVENANCE_V1",
            "comparisons": {
                "primary_vs_left_control": _comparison(
                    first_equal_stage=None,
                ),
                "primary_vs_right_control": _comparison(
                    first_equal_stage=None,
                    control_label="right_control",
                ),
            },
            "identity_excludes": ["target", "target_ic", "reward"],
        }
        inner["provenance_sha256"] = _sha(inner)
        failure_reason = None
    else:
        inner = dict(comparison or _comparison(first_equal_stage="RANK"))
        failure_reason = "CONTROL_BEHAVIOR_EQUALS_PRIMARY"
        inner["failure_reason"] = failure_reason
        inner.pop("provenance_sha256", None)
        inner["provenance_sha256"] = _sha(inner)
    envelope = {
        "schema_version": "CRYPTO_V24_BOUND_CONTROL_PROVENANCE_V1",
        "candidate_id": candidate_id,
        "candidate_spec_sha256": candidate_spec_sha256,
        "failure_reason": failure_reason,
        "provenance": inner,
    }
    envelope["provenance_sha256"] = _sha(envelope)
    return (
        json.dumps(
            envelope,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ),
        envelope["provenance_sha256"],
    )


def _row(
    *,
    candidate_id: str,
    arm: str,
    provenance: tuple[str, str] | None,
    strict_evaluated: bool,
    matched_positive: bool,
) -> dict:
    return {
        "candidate_id": candidate_id,
        "candidate_spec_sha256": ("1" if candidate_id == "c1" else "2") * 64,
        "behavior_family_id": f"family-{candidate_id}",
        "arm": arm,
        "seed": 7,
        "skeleton_id": "skeleton-A",
        "mechanism_family": "FLOW_CONFIRMATION",
        "mapping_family": "CROSS_SECTIONAL_ZERO_NET",
        "horizon_hours": 4,
        "direction_authority": "TRAIN_FROZEN_SIGN_ORIENTATION",
        "typed_constructible": True,
        "behavior_unique": True,
        "behavior_unique_scope": "ARM_SEED_HORIZON_BEHAVIOR_FAMILY",
        "strict_evaluated": strict_evaluated,
        "matched_positive": matched_positive,
        "qualified_candidate": None,
        "process_cpu_seconds": 2.0,
        "validation_status": (
            "EVALUATED" if strict_evaluated else "CANDIDATE_LOCAL_FAILURE"
        ),
        "validation_failure_reason": (
            None
            if strict_evaluated
            else "CONTROL_BEHAVIOR_EQUALS_PRIMARY"
        ),
        "control_degeneracy_provenance_json": (
            provenance[0] if provenance else None
        ),
        "control_degeneracy_provenance_sha256": (
            provenance[1] if provenance else None
        ),
    }


def test_v25_contract_is_observability_only() -> None:
    contract = load_behavior_provenance_census_contract(REPO_ROOT)
    assert contract["status"] == "SOURCE_ONLY_OBSERVABILITY_INFRASTRUCTURE"
    assert contract["historical_inference_allowed"] is False
    assert contract["market_read_allowed"] is False
    assert contract["candidate_replay_allowed"] is False
    assert contract["reward_or_policy_feedback_allowed"] is False
    assert contract["exclusive_counting_key"] == "first_equal_stage"
    assert contract["legacy_authority"]["candidate_ledger_row_count"] == 512
    assert contract["legacy_authority"]["expected_result"] == {
        "status": "NO_PROVENANCE_ROWS",
        "legacy_final_equal_count": 372,
        "first_equal_stage": None,
    }
    assert "control_degeneracy_provenance_json" in contract[
        "required_provenance_ledger_columns"
    ]
    assert set(contract["output_schemas"]) == {
        "candidate_behavior_provenance.parquet",
        "degeneracy_stage_counts.parquet",
        "search_policy_funnel.parquet",
    }


def test_v25_authoritative_legacy_closure_is_hash_bound_and_unknown() -> None:
    assert verify_authoritative_legacy_v24(REPO_ROOT) == {
        "status": "NO_PROVENANCE_ROWS",
        "legacy_final_equal_count": 372,
        "first_equal_stage": None,
    }


def test_v25_legacy_ledger_reports_unknown_not_fake_zero() -> None:
    legacy = pd.DataFrame(
        [
            {
                "candidate_id": "c1",
                "validation_failure_reason": "CONTROL_BEHAVIOR_EQUALS_PRIMARY",
            },
            {
                "candidate_id": "c2",
                "validation_failure_reason": (
                    "INTERACTION_LEFT_CONTROL_BEHAVIOR_EQUALS_AB"
                ),
            },
            {"candidate_id": "c3", "validation_failure_reason": None},
        ]
    )
    result = build_behavior_provenance_census(legacy)
    assert result["summary"] == {
        "status": "NO_PROVENANCE_ROWS",
        "legacy_final_equal_count": 2,
        "first_equal_stage": None,
    }
    assert result["candidate_provenance"].empty
    assert result["stage_counts"].empty
    assert result["funnel"].empty
    contract = load_behavior_provenance_census_contract(REPO_ROOT)
    assert list(result["candidate_provenance"].columns) == contract[
        "output_schemas"
    ]["candidate_behavior_provenance.parquet"]
    assert list(result["stage_counts"].columns) == contract[
        "output_schemas"
    ]["degeneracy_stage_counts.parquet"]
    assert list(result["funnel"].columns) == contract["output_schemas"][
        "search_policy_funnel.parquet"
    ]


def test_v25_counts_first_equal_stage_exclusively_and_slices_funnel() -> None:
    failure = _bound(
        candidate_id="c1",
        candidate_spec_sha256="1" * 64,
        comparison=_comparison(first_equal_stage="RANK"),
    )
    success = _bound(
        candidate_id="c2",
        candidate_spec_sha256="2" * 64,
        successful_pair=True,
    )
    ledger = pd.DataFrame(
        [
            _row(
                candidate_id="c1",
                arm="evolution",
                provenance=failure,
                strict_evaluated=False,
                matched_positive=False,
            ),
            _row(
                candidate_id="c2",
                arm="random",
                provenance=success,
                strict_evaluated=True,
                matched_positive=True,
            ),
        ]
    )
    result = build_behavior_provenance_census(ledger)
    summary = result["summary"]
    assert summary["status"] == "PASS_BEHAVIOR_PROVENANCE_CENSUS"
    assert summary["candidate_count"] == 2
    assert summary["provenance_candidate_count"] == 2

    overall = result["stage_counts"].loc[
        result["stage_counts"]["slice_dimension"] == "overall"
    ]
    assert dict(
        zip(overall["first_equal_stage"], overall["candidate_count"])
    ) == {"NON_DEGENERATE": 1, "RANK": 1}
    assert "SIGNAL" not in set(overall["first_equal_stage"])
    assert {
        "arm",
        "seed",
        "skeleton",
        "mechanism_family",
        "mapping_family",
        "horizon",
        "direction_authority",
    }.issubset(set(result["stage_counts"]["slice_dimension"]))

    evolution = result["funnel"].loc[
        (result["funnel"]["slice_dimension"] == "arm")
        & (result["funnel"]["slice_value"] == "evolution")
    ].iloc[0]
    assert evolution["proposal_count"] == 1
    assert evolution["typed_constructible_count"] == 1
    assert evolution["behavior_unique_count"] == 1
    assert evolution["control_non_degenerate_count"] == 0
    assert evolution["strict_evaluated_count"] == 0
    assert evolution["matched_positive_count"] == 0
    assert pd.isna(evolution["qualified_candidate_count"])

    stages = result["candidate_provenance"]
    rank = stages.loc[
        (stages["candidate_id"] == "c1") & (stages["stage"] == "RANK")
    ].iloc[0]
    assert rank["primary_fingerprint"] == "C" * 64
    assert rank["control_fingerprint"] == "C" * 64
    assert bool(rank["equal"]) is True
    for row in result["funnel"].to_dict("records"):
        chain = [
            row["proposal_count"],
            row["typed_constructible_count"],
            row["behavior_unique_count"],
            row["control_non_degenerate_count"],
            row["strict_evaluated_count"],
            row["matched_positive_count"],
        ]
        assert chain == sorted(chain, reverse=True)


def test_v25_partial_or_tampered_provenance_fails_closed() -> None:
    bound = _bound(
        candidate_id="c1",
        candidate_spec_sha256="1" * 64,
        comparison=_comparison(first_equal_stage="RANK"),
    )
    partial = pd.DataFrame(
        [
            _row(
                candidate_id="c1",
                arm="evolution",
                provenance=bound,
                strict_evaluated=False,
                matched_positive=False,
            ),
            _row(
                candidate_id="c2",
                arm="random",
                provenance=None,
                strict_evaluated=True,
                matched_positive=False,
            ),
        ]
    )
    with pytest.raises(ValueError, match="PARTIAL_PROVENANCE_ROWS"):
        build_behavior_provenance_census(partial)

    tampered = partial.iloc[[0]].copy()
    tampered.loc[:, "control_degeneracy_provenance_sha256"] = "F" * 64
    with pytest.raises(ValueError, match="BOUND_PROVENANCE_HASH_CHANGED"):
        build_behavior_provenance_census(tampered)

    wrong_mapping = partial.iloc[[0]].copy()
    wrong_mapping.loc[:, "mapping_family"] = "DIRECTIONAL_STATEFUL"
    with pytest.raises(ValueError, match="PROVENANCE_MAPPING_FAMILY_CHANGED"):
        build_behavior_provenance_census(wrong_mapping)

    inconsistent = partial.iloc[[0]].copy()
    inconsistent.loc[:, "strict_evaluated"] = True
    inconsistent.loc[:, "matched_positive"] = True
    inconsistent.loc[:, "validation_status"] = "EVALUATED"
    with pytest.raises(ValueError, match="PROVENANCE_LEDGER_STATE_INCONSISTENT"):
        build_behavior_provenance_census(inconsistent)


def test_v25_writer_persists_explicit_legacy_unknown_bundle(
    tmp_path: Path,
) -> None:
    contract = load_behavior_provenance_census_contract(REPO_ROOT)
    ledger_path = REPO_ROOT / contract["legacy_authority"]["candidate_ledger_path"]
    source_manifest = REPO_ROOT / contract["legacy_authority"]["source_manifest_path"]
    output = tmp_path / "census"
    result = write_behavior_provenance_census(
        REPO_ROOT,
        ledger_path=ledger_path,
        output_root=output,
        source_manifest_path=source_manifest,
    )
    assert result["summary"] == {
        "status": "NO_PROVENANCE_ROWS",
        "legacy_final_equal_count": 372,
        "first_equal_stage": None,
    }
    assert json.loads(
        (output / "census_summary.json").read_text(encoding="utf-8")
    ) == result["summary"]
    assert pd.read_parquet(
        output / "degeneracy_stage_counts.parquet"
    ).empty
    for name, columns in contract["output_schemas"].items():
        assert list(pd.read_parquet(output / name).columns) == columns
    manifest = json.loads(
        (output / "run_manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["market_read_performed"] is False
    assert manifest["candidate_replay_performed"] is False
    assert manifest["reward_or_policy_feedback_written"] is False
    assert "\\" not in manifest["input_authority"]["source_manifest_path"]
    with pytest.raises(FileExistsError):
        write_behavior_provenance_census(
            REPO_ROOT,
            ledger_path=ledger_path,
            output_root=output,
            source_manifest_path=source_manifest,
        )
