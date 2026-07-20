from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from alphafactory_crypto.broad_search.expression import (
    FieldContract,
    TypedExpressionRegistry,
)
from alphafactory_crypto.broad_search.policy_upgrade_canary import (
    CANARY_POLICIES,
    _policy_upgrade_audit,
    compile_replay_audit,
    validate_canary_config,
)


def _registry() -> TypedExpressionRegistry:
    return TypedExpressionRegistry(
        (
            FieldContract("open_interest_last_change_1h", "RETURN", "dimensionless"),
            FieldContract("open_interest_value_last", "NOTIONAL", "quote_asset"),
            FieldContract("trade_return_1h", "RETURN", "dimensionless"),
            FieldContract("trade_quote_volume", "NOTIONAL", "quote_asset"),
            FieldContract("mark_trade_basis_bps", "BPS", "bps"),
            FieldContract("top_long_short_account_ratio_last", "RATIO", "dimensionless"),
            FieldContract("global_long_short_account_ratio_last", "RATIO", "dimensionless"),
            FieldContract("top_long_short_position_ratio_last", "RATIO", "dimensionless"),
            FieldContract("account_position_divergence", "RATIO", "dimensionless"),
            FieldContract("listing_age_days", "AGE", "days"),
            FieldContract("active_universe_size", "STATE", "assets"),
        )
    )


def _config() -> dict:
    root = Path(__file__).parents[1]
    return json.loads(
        (root / "config" / "crypto_policy_upgrade_canary_v1.json").read_text()
    )


def test_canary_contract_is_exactly_five_by_four_by_128_and_sealed() -> None:
    config = _config()
    validate_canary_config(config)
    assert tuple(config["budget"]["policies"]) == CANARY_POLICIES
    assert len(config["budget"]["seeds"]) == 4
    assert config["budget"]["pairs_per_lane"] == 128
    assert config["budget"]["strict_pairs"] == 2560
    assert config["budget"]["report_only_pairs"] == 0
    assert config["boundaries"]["sealed_reads_allowed"] is False
    assert config["boundaries"]["report_only_reads_allowed"] is False
    assert config["boundaries"]["candidate_promotion"] is False
    changed = deepcopy(config)
    changed["budget"]["pairs_per_lane"] = 64
    with pytest.raises(ValueError, match="frozen canary budget"):
        validate_canary_config(changed)


def test_compile_replay_covers_all_upgraded_lanes_and_receipts() -> None:
    config = _config()
    config["budget"]["seeds"] = [20260720, 20260721]
    config["compile_replay"]["steps_per_lane"] = 20
    audit = compile_replay_audit(_registry(), config)
    assert audit["result"] == "PASS"
    assert audit["lane_count"] == 10
    assert audit["all_candidate_ids_replayed"] is True
    assert audit["all_state_hashes_replayed"] is True
    assert audit["all_mutation_receipts_verified"] is True
    assert audit["real_cem_update_count"] >= 2
    assert audit["typed_mutation_receipt_count"] >= 8


def test_policy_audit_requires_real_policy_to_beat_random_and_lite() -> None:
    config = _config()
    config["budget"].update(
        {"seeds": [1, 2], "pairs_per_lane": 2, "lane_count": 10, "strict_pairs": 20}
    )
    config["qualification"].update(
        {
            "minimum_positive_seed_count": 2,
            "minimum_unique_rate": 1.0,
            "minimum_skeleton_coverage": 1,
            "minimum_family_coverage": 1,
            "minimum_field_coverage": 1,
            "minimum_cem_updates_per_lane": 0,
            "minimum_verified_mutations_per_lane": 1,
        }
    )
    reward = {
        "canonical_typed_random": (0.0, 0.1),
        "cem_diversity_v2": (0.1, 0.2),
        "cem_distribution_v1": (0.3, 0.4),
        "evolutionary": (0.05, 0.15),
        "evolutionary_typed_v1": (0.25, 0.35),
    }
    rows = []
    for seed in (1, 2):
        for policy in CANARY_POLICIES:
            for step, value in enumerate(reward[policy]):
                rows.append(
                    {
                        "policy": policy,
                        "seed": seed,
                        "proposal_step": step,
                        "candidate_id": f"{policy}-{seed}-{step}",
                        "pair_evaluation_status": "PASS",
                        "pair_reward": value,
                        "skeleton_id": "skeleton",
                        "mechanism_family": "family",
                        "candidate_spec_json": json.dumps({"raw_fields": ["field"]}),
                        "mutation_receipt_verified": (
                            True if policy == "evolutionary_typed_v1" and step else None
                        ),
                        "policy_diagnostics_json": json.dumps(
                            {"cem_update_count": 0}
                        ),
                    }
                )
    audit = _policy_upgrade_audit(rows, config)
    assert audit["implementation_result"] == "PASS"
    for policy in ("cem_distribution_v1", "evolutionary_typed_v1"):
        decision = audit["upgrade_decisions"][policy]
        assert decision["positive_seed_count_vs_random_and_lite"] == 2
        assert decision["decision"] == "KEEP_FOR_FUTURE_NEW_DATA_ARENA"
    weaker = deepcopy(rows)
    for row in weaker:
        if row["policy"] == "cem_distribution_v1":
            row["pair_reward"] = -1.0
    failed = _policy_upgrade_audit(weaker, config)
    assert (
        failed["upgrade_decisions"]["cem_distribution_v1"]["decision"]
        == "EVICT_EXPERIMENTAL_UPGRADE"
    )
