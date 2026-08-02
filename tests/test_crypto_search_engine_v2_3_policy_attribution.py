from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import alphafactory_crypto.broad_search.search_engine_v1 as search_engine
from alphafactory_crypto.broad_search.experiment_authority import (
    resolve_search_economic_receipt,
)
from alphafactory_crypto.broad_search.search_engine_v1 import (
    MECHANISM_SEARCH_V22_SEEDS,
    MECHANISM_SEARCH_V23_ARMS,
    MECHANISM_SEARCH_V23_CAMPAIGN,
    MECHANISM_SEARCH_V23_EPOCH_ID,
    MECHANISM_SEARCH_V23_SEEDS,
    _economic_campaign_seeds,
    _load_mechanism_v23_contract,
    _mechanism_v23_expected_checkpoint_allocations,
    _v23_attribution_projection,
    _v23_daily_path,
    _v23_paired_block_effect,
    _v23_stratified_candidate_rows,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_v23_contract_is_two_fresh_seeds_and_unchanged_mechanism_basis() -> None:
    config, catalog, knowledge = _load_mechanism_v23_contract(REPO_ROOT)
    derived = tuple(
        int.from_bytes(
            hashlib.sha256(
                f"{MECHANISM_SEARCH_V23_EPOCH_ID}|seed|{ordinal}".encode()
            ).digest()[:4],
            "big",
        )
        for ordinal in range(2)
    )
    assert _economic_campaign_seeds(MECHANISM_SEARCH_V23_CAMPAIGN) == derived
    assert derived == MECHANISM_SEARCH_V23_SEEDS
    assert not set(derived) & set(MECHANISM_SEARCH_V22_SEEDS)
    assert len(catalog) == 786
    assert config["boundaries"]["new_grammar"] is False
    assert config["boundaries"]["new_evaluator"] is False
    assert config["boundaries"]["v22_state_import"] is False
    assert knowledge["usage_contract"]["sampling_probability_prior"] is False


def test_v23_train_and_conditional_continuation_allocations_are_exact() -> None:
    config, _, _ = _load_mechanism_v23_contract(REPO_ROOT)
    allocations = _mechanism_v23_expected_checkpoint_allocations(
        stages=config["stages"],
        seeds=MECHANISM_SEARCH_V23_SEEDS,
    )
    assert allocations == {
        **{
            checkpoint: {
                "expanded_mechanism_random_v2_3": 1000,
                "mechanism_evolution_v2_3": 1000,
            }
            for checkpoint in range(8)
        },
        8: {"mechanism_evolution_v2_3": 2000},
        9: {"mechanism_evolution_v2_3": 2000},
    }
    assert sum(sum(row.values()) for row in allocations.values()) == 20_000
    assert set(config["policy_parameters"]) == set(MECHANISM_SEARCH_V23_ARMS)


def test_v23_receipt_makes_random_comparator_only() -> None:
    receipt = resolve_search_economic_receipt(
        REPO_ROOT,
        "config/crypto_search_mechanism_v2_3_receipt.json",
    )
    assert receipt["result"] == "RUN_AUTHORIZED_CONDITIONAL_DEVELOPMENT"
    assert receipt["run_authorized"] is True
    assert receipt["validation_kill_line"][
        "random_control_survival_required"
    ] is False
    assert receipt["validation_kill_line"]["absolute_kill_line_applies_to"] == (
        "evolution_train_top"
    )
    assert receipt["formal_claims_authorized"] is False


def test_v23_search_surface_accepts_its_frozen_seed_derivation() -> None:
    receipt = resolve_search_economic_receipt(
        REPO_ROOT,
        "config/crypto_search_mechanism_v2_3_receipt.json",
    )
    train = receipt["evidence_partition"]["train"]
    identities = {
        "raw_cache": {
            "identity_sha256": receipt["search_campaign"][
                "carrier_cache_identity_sha256"
            ]
        },
        "aligned_carrier_manifest": {
            "path": receipt["search_campaign"]["carrier_manifest"]
        },
        "behavior_contract_window": {
            "start": train["start"],
            "end_exclusive": train["end_exclusive"],
            "validation_read": False,
            "holdout_read": False,
        },
    }
    assert search_engine._validate_economic_search_surface(
        receipt=receipt,
        identities=identities,
        contracts=tuple(range(115)),
        expected_campaign=MECHANISM_SEARCH_V23_CAMPAIGN,
        expected_seeds=MECHANISM_SEARCH_V23_SEEDS,
        expected_strict_target=search_engine.MECHANISM_SEARCH_V23_STRICT_TARGET,
        expected_checkpoint_size=(
            search_engine.MECHANISM_SEARCH_V23_CHECKPOINT_SIZE
        ),
        expected_checkpoint_count=(
            search_engine.MECHANISM_SEARCH_V23_CHECKPOINT_COUNT
        ),
    ) == "OI_MARK_RANKS51_200_X_AGGTRADES_TOP200_ALIGNED"


def test_v23_stratified_selection_is_reward_blind_deterministic_and_disjoint() -> None:
    rows = [
        {
            "candidate_id": f"candidate-{index:03d}",
            "arm_completion_ordinal": index,
            "search_reward": float(index),
        }
        for index in range(160)
    ]
    excluded = {"candidate-001", "candidate-017", "candidate-099"}
    first = _v23_stratified_candidate_rows(
        rows,
        excluded_ids=excluded,
        stratum_count=8,
    )
    reward_changed = [{**row, "search_reward": -row["search_reward"]} for row in rows]
    second = _v23_stratified_candidate_rows(
        reward_changed,
        excluded_ids=excluded,
        stratum_count=8,
    )
    first_ids = {key: [row["candidate_id"] for row in value] for key, value in first.items()}
    second_ids = {
        key: [row["candidate_id"] for row in value] for key, value in second.items()
    }
    assert first_ids == second_ids
    assert not excluded & {candidate for values in first_ids.values() for candidate in values}
    assert set(first_ids) == set(range(8))


def test_v23_daily_paths_and_paired_block_effect_are_deterministic() -> None:
    hourly = np.arange(48, dtype=float)
    assert np.array_equal(_v23_daily_path(hourly), np.asarray([11.5, 35.5]))
    left = np.linspace(-0.001, 0.001, 61)
    right = left + 0.0002
    kwargs = {
        "seed": MECHANISM_SEARCH_V23_SEEDS[0],
        "horizon": 1,
        "comparison": "proposal_distribution",
        "metric": "primary_net",
        "block_length": 7,
        "replications": 2048,
        "lower_quantile": 0.25,
    }
    passed = _v23_paired_block_effect(left, right, **kwargs)
    replay = _v23_paired_block_effect(left, right, **kwargs)
    failed = _v23_paired_block_effect(right, left, **kwargs)
    assert passed == replay
    assert passed["passed"] is True
    assert passed["bootstrap_lower_quantile"] > 0.0
    assert failed["passed"] is False


def test_v23_projection_requires_all_four_cells_per_component() -> None:
    relative = [
        {"comparison": comparison, "passed": True, "cell": cell}
        for comparison in (
            "proposal_distribution",
            "train_ranker",
            "total_policy",
        )
        for cell in range(4)
    ]
    absolute = [{"passed": True, "cell": cell} for cell in range(4)]
    components, absolute_pass, full = _v23_attribution_projection(relative, absolute)
    assert components == {
        "proposal_distribution": True,
        "train_ranker": True,
        "total_policy": True,
    }
    assert absolute_pass is True
    assert full is True
    components, absolute_pass, full = _v23_attribution_projection(relative[:-1], absolute)
    assert components["total_policy"] is False
    assert absolute_pass is True
    assert full is False


def test_v23_cli_and_path_artifact_are_registered() -> None:
    source = (
        REPO_ROOT / "alphafactory_crypto/broad_search/search_engine_v1.py"
    ).read_text(encoding="utf-8")
    config = json.loads(
        (REPO_ROOT / "config/crypto_search_engine_v2_3_policy_attribution.json").read_text(
            encoding="utf-8"
        )
    )
    assert '"run-mechanism-v2-3"' in source
    assert '"check-mechanism-v2-3"' in source
    assert "run_v23_policy_attribution_validation" in source
    assert config["validation"]["path_artifact"]["path"] == (
        "validation_cohort_paths.parquet"
    )


def test_v23_validation_orchestration_attributes_all_four_cohorts(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    receipt = resolve_search_economic_receipt(
        REPO_ROOT,
        "config/crypto_search_mechanism_v2_3_receipt.json",
    )

    class FakeCandidate:
        def __init__(self, payload: dict[str, object]) -> None:
            self.candidate_id = str(payload["candidate_id"])
            self.horizon_hours = int(payload["horizon_hours"])
            self.quality = float(payload["quality"])

    monkeypatch.setattr(
        search_engine.CandidateSpec,
        "from_dict",
        staticmethod(lambda payload: FakeCandidate(payload)),
    )
    monkeypatch.setattr(search_engine, "_policy_state_sha256", lambda _: "POLICY")

    class FakeArchive:
        def state_hash(self) -> str:
            return "ARCHIVE"

    ledger: list[dict[str, object]] = []
    for arm in MECHANISM_SEARCH_V23_ARMS:
        arm_ordinal = 0
        for seed in MECHANISM_SEARCH_V23_SEEDS:
            for horizon in (1, 4):
                for local_ordinal in range(2000):
                    is_evolution = arm == "mechanism_evolution_v2_3"
                    quality = (0.0007 if is_evolution else 0.0001) + (
                        0.0003 if local_ordinal < 96 else 0.0
                    )
                    candidate_id = (
                        f"{arm}-{seed}-{horizon}-{local_ordinal:04d}"
                    )
                    candidate_payload = {
                        "candidate_id": candidate_id,
                        "horizon_hours": horizon,
                        "quality": quality,
                    }
                    ledger.append(
                        {
                            "arm": arm,
                            "seed": seed,
                            "arm_completion_ordinal": arm_ordinal,
                            "candidate_id": candidate_id,
                            "candidate_spec_json": json.dumps(candidate_payload),
                            "search_reward": float(2000 - local_ordinal),
                            "search_reward_authority": search_engine.SEARCH_REWARD_AUTHORITY,
                            "economic_receipt_sha256": receipt["receipt_sha256"],
                            "train_orientation_fitted": True,
                            "evaluation_partition": "train",
                            "train_orientation": 1.0,
                            "search_reward_matched_limiting_component": "delta",
                        }
                    )
                    arm_ordinal += 1

    def evaluate(candidate: FakeCandidate, orientation: float) -> dict[str, object]:
        phase = np.linspace(0.0, 8.0 * np.pi, 24 * 61)
        primary = candidate.quality + 0.00015 * np.sin(phase)
        matched = candidate.quality * 0.6 + 0.00005 * np.cos(phase)
        control = candidate.quality * 0.1 + 0.00002 * np.sin(phase)
        return {
            "candidate_id": candidate.candidate_id,
            "evaluation_partition": "validation",
            "train_orientation_fitted": False,
            "train_orientation": orientation,
            "effective_block_end_exclusive": "2026-01-01T00:00:00Z",
            "_validation_paths": {
                "primary_net": primary,
                "matched_component_net": {"delta": matched},
                "control_net": {"control": control},
            },
        }

    holder: dict[str, object] = {}

    def fake_write_checkpoint(**kwargs: object) -> Path:
        holder.update(kwargs)
        path = Path(str(kwargs["runtime_root"])) / "checkpoints" / str(
            kwargs["label"]
        )
        path.mkdir(parents=True)
        return path

    def fake_load_checkpoint(**_: object) -> tuple[object, ...]:
        return (
            holder["state"],
            holder["policies"],
            holder["ledger"],
            holder["archive"],
            holder["metrics"],
        )

    monkeypatch.setattr(search_engine, "_write_checkpoint", fake_write_checkpoint)
    monkeypatch.setattr(search_engine, "_load_checkpoint", fake_load_checkpoint)
    runtime_root = tmp_path / "runtime"
    runtime_root.mkdir()
    result = search_engine.run_v23_policy_attribution_validation(
        repo_root=REPO_ROOT,
        runtime_root=runtime_root,
        store=object(),
        registry=object(),
        state={
            "source_sha": "a" * 40,
            "frozen_contract_sha256": "B" * 64,
            "next_checkpoint_index": 8,
            "arm_states": {arm: "ACTIVE" for arm in MECHANISM_SEARCH_V23_ARMS},
        },
        policies={},
        train_ledger=ledger,
        archive=FakeArchive(),
        train_metrics=[],
        identities={},
        economic_receipt=receipt,
        evaluation_runner=evaluate,
    )[-1]
    assert result["strict_candidate_cohort_evaluated_count"] == 1024
    assert result["proposal_distribution_qualified"] is True
    assert result["train_ranker_qualified"] is True
    assert result["full_evolution_policy_pass"] is True
    validation_rows = pd.read_parquet(
        runtime_root / "validation_candidate_ledger.parquet"
    )
    assert validation_rows.loc[
        validation_rows["validation_status"] == "EVALUATED", "candidate_id"
    ].nunique() == 1024
    assert (
        runtime_root / "validation_cohort_paths.parquet"
    ).is_file()
