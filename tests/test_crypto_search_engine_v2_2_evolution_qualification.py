from __future__ import annotations

import json
from pathlib import Path

import pytest

from alphafactory_crypto.broad_search.experiment_authority import (
    resolve_search_economic_receipt,
)
from alphafactory_crypto.broad_search.search_engine_v1 import (
    MECHANISM_SEARCH_V22_ARMS,
    MECHANISM_SEARCH_V22_CAMPAIGN,
    MECHANISM_SEARCH_V22_SEEDS,
    _economic_campaign_seeds,
    _load_mechanism_v22_contract,
    _mechanism_v22_checkpoint_allocation,
    _mechanism_v22_expected_checkpoint_allocations,
    _mechanism_v22_train_gate,
    _mechanism_v22_validation_allows_expansion,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def _gate_rows(
    *,
    random_positive: int,
    evolution_positive: int,
    random_base: float = -0.30,
    evolution_base: float = -0.10,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for arm, base, positive_count in (
        ("expanded_mechanism_random_v2_2", random_base, random_positive),
        ("mechanism_evolution_v2_2", evolution_base, evolution_positive),
    ):
        for index in range(4_000):
            rows.append(
                {
                    "arm": arm,
                    "arm_completion_ordinal": index + 1,
                    "candidate_id": f"{arm}:{index:04d}",
                    "behavior_family_id": f"{arm}:family:{index:04d}",
                    "search_reward": 0.10 if index < positive_count else base,
                }
            )
    return rows


def test_v22_reuses_v21_catalog_with_new_disjoint_frozen_seeds() -> None:
    config, catalog, knowledge = _load_mechanism_v22_contract(REPO_ROOT)
    assert len(catalog) == 786
    assert config["catalog_path"] == "config/crypto_typed_mechanism_catalog_v2_1.json"
    assert config["search"]["strict_evaluated_target"] == 20_000
    assert config["search"]["required_pairs_per_hour"] == pytest.approx(
        20_000 / 18.0
    )
    assert knowledge["usage_contract"]["sampling_probability_prior"] is False
    assert _economic_campaign_seeds(MECHANISM_SEARCH_V22_CAMPAIGN) == (
        MECHANISM_SEARCH_V22_SEEDS
    )
    assert len(set(MECHANISM_SEARCH_V22_SEEDS)) == 4


def test_v22_stage_allocations_are_exact_and_seed_balanced() -> None:
    config, _, _ = _load_mechanism_v22_contract(REPO_ROOT)
    expected = {
        **{
            checkpoint: {
                "expanded_mechanism_random_v2_2": 1_000,
                "mechanism_evolution_v2_2": 1_000,
            }
            for checkpoint in range(4)
        },
        **{
            checkpoint: {
                "expanded_mechanism_random_v2_2": 400,
                "mechanism_evolution_v2_2": 1_600,
            }
            for checkpoint in range(4, 10)
        },
    }
    compiled = _mechanism_v22_expected_checkpoint_allocations(
        stages=json.loads(json.dumps(config["stages"])),
        seeds=MECHANISM_SEARCH_V22_SEEDS,
    )
    assert compiled == expected
    for checkpoint, nonzero in expected.items():
        allocation = _mechanism_v22_checkpoint_allocation(
            checkpoint,
            repo_root=REPO_ROOT,
            seeds=MECHANISM_SEARCH_V22_SEEDS,
        )
        assert set(allocation) == set(MECHANISM_SEARCH_V22_ARMS)
        assert {arm: count for arm, count in allocation.items() if count} == nonzero


def test_v22_train_gate_qualifies_evolution_not_the_random_control() -> None:
    gate = _mechanism_v22_train_gate(
        repo_root=REPO_ROOT,
        ledger=_gate_rows(random_positive=0, evolution_positive=80),
    )
    assert gate["status"] == "PASS"
    assert gate["validation_authorized_by_gate"] is True
    assert gate["evolution"]["positive_search_reward_count"] == 80
    assert "random_absolute_positive_floor" not in gate["checks"]
    assert all(gate["checks"].values())


@pytest.mark.parametrize("positive_count", [0, 39])
def test_v22_train_gate_fails_evolution_absolute_floor(positive_count: int) -> None:
    gate = _mechanism_v22_train_gate(
        repo_root=REPO_ROOT,
        ledger=_gate_rows(
            random_positive=0,
            evolution_positive=positive_count,
        ),
    )
    assert gate["status"] == "TRAIN_GATE_NEGATIVE"
    assert gate["validation_authorized_by_gate"] is False


def test_v22_validation_requires_both_random_control_and_evolution() -> None:
    passed = {
        "status": "VALIDATION_STAGE_COMPLETE",
        "arm_decisions": {
            "expanded_mechanism_random_v2_2": {"passed": True},
            "mechanism_evolution_v2_2": {"passed": True},
        },
    }
    assert _mechanism_v22_validation_allows_expansion(passed) is True
    for failed_arm in MECHANISM_SEARCH_V22_ARMS:
        failed = json.loads(json.dumps(passed))
        failed["arm_decisions"][failed_arm]["passed"] = False
        assert _mechanism_v22_validation_allows_expansion(failed) is False


def test_v22_receipt_is_narrow_fresh_state_authority() -> None:
    receipt = resolve_search_economic_receipt(
        REPO_ROOT,
        "config/crypto_search_mechanism_v2_2_receipt.json",
    )
    assert receipt["result"] == "RUN_AUTHORIZED_CONDITIONAL_DEVELOPMENT"
    assert receipt["run_authorized"] is True
    assert receipt["search_campaign"]["seed_set"] == list(
        MECHANISM_SEARCH_V22_SEEDS
    )
    assert receipt["validation_kill_line"]["control_arm_id"] == (
        "expanded_mechanism_random_v2_2"
    )
    assert receipt["validation_kill_line"][
        "random_control_survival_required"
    ] is True
    raw = json.loads(
        (
            REPO_ROOT / "config/crypto_search_mechanism_v2_2_receipt.json"
        ).read_text(encoding="utf-8")
    )
    assert all(value is False for value in raw["fresh_state"].values())
    assert raw["boundaries"]["sealed_reads"] == 0
    assert receipt["formal_claims_authorized"] is False
