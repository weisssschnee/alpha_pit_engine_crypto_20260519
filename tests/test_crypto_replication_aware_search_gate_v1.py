from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from alphafactory_crypto.broad_search.expression import (
    FieldContract,
    TypedExpressionRegistry,
)
from alphafactory_crypto.broad_search.pair18m import (
    SEARCH_REWARD_AUTHORITY,
    _development_block_robust_ordering,
)
from alphafactory_crypto.broad_search.experiment_authority import (
    resolve_search_economic_receipt,
)
from alphafactory_crypto.broad_search.search_engine_v1 import (
    BLOCK_ROBUST_GATE_ARMS,
    BLOCK_ROBUST_GATE_CAMPAIGN,
    BLOCK_ROBUST_GATE_SEEDS,
    MechanismEvolutionV2,
    MechanismRandomV2,
    _block_robust_gate_summary,
    _economic_campaign_seeds,
    _initial_policies,
    _load_search_evidence_v1_contract,
    _search_evidence_v1_expected_checkpoint_allocations,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def _contracts() -> tuple[FieldContract, ...]:
    manifest = json.loads(
        (
            REPO_ROOT
            / "runtime/crypto_search_engine_v1_4_oi_flow_20260728/"
            "aligned_carrier_manifest.json"
        ).read_text(encoding="utf-8")
    )
    return tuple(
        FieldContract(
            str(row["field_id"]),
            str(row["value_type"]),
            str(row["unit"]),
            int(row["observable_lag_hours"]),
            str(row["pit_authority"]),
        )
        for row in manifest["contracts"]
    )


def _ordering(
    *,
    replicated: int,
    worst: float,
    median: float,
    turnover: float,
    support: float,
) -> dict[str, object]:
    return {
        "authority": "DEVELOPMENT_THREE_BLOCK_ROBUST_ORDERING_V1",
        "replicated_positive_block_count": replicated,
        "worst_block_min_matched_net_mean": worst,
        "median_block_joint_search_reward": median,
        "max_required_mean_one_way_turnover": turnover,
        "min_required_support": support,
    }


def test_gate_contract_is_equal_count_fresh_development_only() -> None:
    config, catalog, _ = _load_search_evidence_v1_contract(
        REPO_ROOT, campaign=BLOCK_ROBUST_GATE_CAMPAIGN
    )
    allocations = _search_evidence_v1_expected_checkpoint_allocations(
        stages=config["stages"],
        seeds=BLOCK_ROBUST_GATE_SEEDS,
        arms=BLOCK_ROBUST_GATE_ARMS,
        checkpoint_size=512,
        checkpoint_count=3,
    )

    assert _economic_campaign_seeds(BLOCK_ROBUST_GATE_CAMPAIGN) == (
        BLOCK_ROBUST_GATE_SEEDS
    )
    assert set(allocations) == {0, 1, 2}
    assert {
        arm: sum(allocation[arm] for allocation in allocations.values())
        for arm in BLOCK_ROBUST_GATE_ARMS
    } == {arm: 512 for arm in BLOCK_ROBUST_GATE_ARMS}
    assert all(item.condition_role is None for item in catalog)
    assert config["block_robust_contract"]["horizons_hours"] == [4]
    assert not any(config["fresh_state"].values())
    assert config["validation"] == {
        "authorized": False,
        "status": "NOT_AUTHORIZED",
        "holdout_read": False,
        "automatic_continuation": False,
    }


def test_gate_receipt_is_hash_bound_and_authorizes_no_validation() -> None:
    receipt = resolve_search_economic_receipt(
        REPO_ROOT,
        "config/crypto_search_replication_aware_gate_v1_receipt.json",
    )

    assert receipt["result"] == "RUN_AUTHORIZED_CONDITIONAL_DEVELOPMENT"
    assert receipt["run_authorized"] is True
    assert receipt["search_campaign"]["strict_evaluated_target"] == 1536
    assert receipt["search_campaign"]["seed_set"] == list(
        BLOCK_ROBUST_GATE_SEEDS
    )
    assert receipt["validation"]["role"] == "NOT_AUTHORIZED"
    assert receipt["holdout"]["read_allowed"] is False
    assert receipt["validation_kill_line"]["required_horizons_hours"] == [4]
    assert receipt["validation_kill_line"]["evaluated_per_active_arm"] == 0
    assert receipt["formal_claims_authorized"] is False


def test_gate_policies_emit_only_4h_binary_candidates() -> None:
    registry = TypedExpressionRegistry(_contracts())
    policies = _initial_policies(
        registry,
        arms=BLOCK_ROBUST_GATE_ARMS,
        seeds=(BLOCK_ROBUST_GATE_SEEDS[0],),
    )

    assert len(policies) == 3
    for policy in policies.values():
        candidate, _ = policy.propose()
        assert candidate.horizon_hours == 4
        mechanism = candidate.generation_genes["mechanism_spec"]
        assert mechanism["condition_role"] is None


def test_replication_selection_is_lexicographic_without_changing_current() -> None:
    registry = TypedExpressionRegistry(_contracts())
    config, catalog, _ = _load_search_evidence_v1_contract(
        REPO_ROOT, campaign=BLOCK_ROBUST_GATE_CAMPAIGN
    )
    current = MechanismEvolutionV2(
        BLOCK_ROBUST_GATE_SEEDS[0],
        registry,
        catalog,
        dict(config["policy_parameters"][BLOCK_ROBUST_GATE_ARMS[1]]),
    )
    robust = MechanismEvolutionV2(
        BLOCK_ROBUST_GATE_SEEDS[0],
        registry,
        catalog,
        dict(config["policy_parameters"][BLOCK_ROBUST_GATE_ARMS[2]]),
    )
    high_reward = {
        "search_reward": 10.0,
        "family_count": 1,
        "block_robust_ordering": _ordering(
            replicated=1,
            worst=1.0,
            median=1.0,
            turnover=0.1,
            support=100.0,
        ),
    }
    replicated = {
        "search_reward": -10.0,
        "family_count": 1,
        "block_robust_ordering": _ordering(
            replicated=2,
            worst=-1.0,
            median=-1.0,
            turnover=1.0,
            support=10.0,
        ),
    }

    assert current.parameters["selection_authority"] == SEARCH_REWARD_AUTHORITY
    assert current._selection_key(
        "high", high_reward, include_family_count=False
    ) < current._selection_key(
        "replicated", replicated, include_family_count=False
    )
    assert robust._selection_key(
        "replicated", replicated, include_family_count=False
    ) < robust._selection_key(
        "high", high_reward, include_family_count=False
    )


def test_replication_evolution_checkpoint_restores_exact_policy_state() -> None:
    registry = TypedExpressionRegistry(_contracts())
    config, catalog, _ = _load_search_evidence_v1_contract(
        REPO_ROOT, campaign=BLOCK_ROBUST_GATE_CAMPAIGN
    )
    policy = MechanismEvolutionV2(
        BLOCK_ROBUST_GATE_SEEDS[0],
        registry,
        catalog,
        dict(config["policy_parameters"][BLOCK_ROBUST_GATE_ARMS[2]]),
    )
    candidate, _ = policy.propose()
    policy.observe(
        candidate,
        {
            "behavior_family_id": "family",
            "search_reward": 1.0,
            "search_reward_authority": SEARCH_REWARD_AUTHORITY,
            "policy_local_family_count_at_completion": 1,
            "block_robust_ordering": _ordering(
                replicated=2,
                worst=0.001,
                median=0.5,
                turnover=0.2,
                support=100.0,
            ),
        },
    )
    restored = MechanismEvolutionV2.from_state(registry, policy.export_state())

    assert restored.state_hash() == policy.state_hash()
    expected, expected_metadata = policy.propose()
    replayed, replayed_metadata = restored.propose()
    assert replayed.candidate_id == expected.candidate_id
    assert replayed_metadata["operation"] == expected_metadata["operation"]
    assert restored.state_hash() == policy.state_hash()


def test_three_block_projection_is_deterministic_and_train_only() -> None:
    registry = TypedExpressionRegistry(_contracts())
    config, catalog, _ = _load_search_evidence_v1_contract(
        REPO_ROOT, campaign=BLOCK_ROBUST_GATE_CAMPAIGN
    )
    policy = MechanismRandomV2(
        BLOCK_ROBUST_GATE_SEEDS[0],
        registry,
        catalog,
        dict(config["policy_parameters"][BLOCK_ROBUST_GATE_ARMS[0]]),
    )
    candidate, _ = policy.propose()
    timestamps = pd.date_range(
        "2025-08-29T07:00:00Z",
        "2025-11-01T00:00:00Z",
        freq="h",
        inclusive="left",
    ).asi8
    hours = len(timestamps)
    primary = np.repeat(np.array([[0.5], [-0.5]]), hours, axis=1)
    left_delta = np.repeat(np.array([[0.2], [-0.2]]), hours, axis=1)
    right_delta = np.repeat(np.array([[0.3], [-0.3]]), hours, axis=1)
    target = np.repeat(np.array([[0.001], [-0.001]]), hours, axis=1)
    arguments = {
        "candidate": candidate,
        "primary_weight": primary,
        "left_delta_weight": left_delta,
        "right_delta_weight": right_delta,
        "target": target,
        "evaluation_mask": np.ones(hours, dtype=bool),
        "timestamp_ns": timestamps,
        "cost_bps": 5.0,
        "full_block_start": "2025-08-29T07:00:00Z",
        "full_block_end": "2025-11-01T00:00:00Z",
        "contract": config["block_robust_contract"],
        "economic_receipt": {
            "execution": {"partition_tail_purge_hours": 6}
        },
    }

    first = _development_block_robust_ordering(**arguments)
    second = _development_block_robust_ordering(**arguments)
    assert first == second
    assert first["evaluation_partition"] == "train"
    assert first["validation_read"] is False
    assert first["block_count"] == 3
    assert first["replicated_candidate"] is True
    assert all(row["initial_establishment_charged"] for row in first["blocks"])
    assert all(row["terminal_liquidation_charged"] for row in first["blocks"])
    assert len(first["ordering_sha256"]) == 64


def test_gate_requires_broad_replication_productivity_not_one_template() -> None:
    registry = TypedExpressionRegistry(_contracts())
    config, catalog, _ = _load_search_evidence_v1_contract(
        REPO_ROOT, campaign=BLOCK_ROBUST_GATE_CAMPAIGN
    )
    policy = MechanismRandomV2(
        BLOCK_ROBUST_GATE_SEEDS[0], registry, catalog, {"allowed_horizons": [4]}
    )
    by_template: dict[str, str] = {}
    while len(by_template) < 2:
        candidate, _ = policy.propose()
        template = str(
            candidate.generation_genes["mechanism_spec"]["template_id"]
        )
        by_template.setdefault(
            template,
            json.dumps(candidate.to_dict(), sort_keys=True, separators=(",", ":")),
        )
    templates = sorted(by_template)[:2]
    rows: list[dict[str, object]] = []
    replicated_by_arm = {
        BLOCK_ROBUST_GATE_ARMS[0]: 80,
        BLOCK_ROBUST_GATE_ARMS[1]: 100,
        BLOCK_ROBUST_GATE_ARMS[2]: 200,
    }
    for arm in BLOCK_ROBUST_GATE_ARMS:
        for index in range(512):
            template = templates[index % 2]
            replicated = index < replicated_by_arm[arm]
            rows.append(
                {
                    "arm": arm,
                    "candidate_id": f"{arm}:{index}",
                    "candidate_spec_json": by_template[template],
                    "behavior_family_id": f"{arm}:family:{index}",
                    "block_robust_ordering_json": "{}",
                    "replicated_candidate": replicated,
                    "all_three_blocks_positive": replicated and index % 3 == 0,
                }
            )
    state = {
        "arm_counters": {
            arm: {
                "generation_attempts": 600,
                "cpu_seconds": 100.0 if arm != BLOCK_ROBUST_GATE_ARMS[2] else 120.0,
            }
            for arm in BLOCK_ROBUST_GATE_ARMS
        }
    }

    summary, template_rows = _block_robust_gate_summary(
        ledger=pd.DataFrame(rows), state=state, config=config
    )
    assert summary["status"] == (
        "QUALIFIED_FOR_SEPARATELY_AUTHORIZED_SMALL_DEVELOPMENT_VALIDATION"
    )
    assert all(summary["gate_checks"].values())
    assert len(summary["supported_templates_with_positive_delta"]) == 2
    assert len(template_rows) == 6
    assert summary["automatic_continuation"] is False
