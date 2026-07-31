from __future__ import annotations

import json
import os
import random
from copy import deepcopy
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from alphafactory_crypto.broad_search.audit import (
    freeze_search_behavior_contract,
    search_behavior_descriptor,
)
from alphafactory_crypto.broad_search.compositional18m import (
    CONDITIONAL_SEMANTIC_TUPLES,
    CandidateSpec,
    MECHANISM_FAMILIES,
    MECHANISM_MAPPING_CLASS,
    candidate_from_genes,
    field_role_coverage,
    generate_candidate,
    mapping_id_for_mechanism_family,
    skeleton_registry,
    typed_mutate_candidate,
    verify_typed_mutation_receipt,
)
from alphafactory_crypto.instrument_canary.grammar import (
    CROSS_SECTIONAL_RELATIVE,
    MECHANISM_MAPPING,
)
from alphafactory_crypto.broad_search.expression import (
    Expression,
    FieldContract,
    TypedExpressionRegistry,
    ablate_expression,
    materialize_expression,
)
from alphafactory_crypto.broad_search.pair18m import (
    SEARCH_REWARD_AUTHORITY,
    _mean_lcb,
    _series_metrics,
    evaluate_pair,
    feedback_contract_payload,
)
from alphafactory_crypto.broad_search.panel18m import rebuild_panel_context_fields
from alphafactory_crypto.broad_search.runner18m import (
    LanePolicy,
    _current_field_surface_binding,
    _directory_bundle,
    _policy_audit,
    _validate_config,
    _working_set_trim_due,
)
from alphafactory_crypto.broad_search.search_engine_v1 import (
    BehaviorArchive,
    HierarchicalTypedCEMV2,
    SEEDS,
    TypedEvolutionV2,
    V22_PARAMETERS,
    _ProposalGenerationFailure,
    _ValidationStageBlocked,
    _balanced_lane_choice,
    _checkpoint_allocation,
    _checkpoint_resume_order,
    _evaluation_audit_fields,
    _export_policy,
    _frozen_validation_due,
    _load_checkpoint,
    _metrics_rows,
    _new_campaign_state,
    _payload_sha,
    _initial_policies,
    _validate_economic_search_surface,
    run_frozen_validation_stage,
    _write_checkpoint,
)
from alphafactory_crypto.instrument_capability.mapping import CROSS_SECTIONAL_ZERO_NET


def test_each_broad_mechanism_has_an_explicit_canonical_mapping_class() -> None:
    expected_families = {
        *MECHANISM_FAMILIES,
        *(f"CONDITIONAL_{value}" for value in CONDITIONAL_SEMANTIC_TUPLES),
    }
    assert set(MECHANISM_MAPPING_CLASS) == expected_families
    for mechanism_family in sorted(expected_families):
        assert (
            MECHANISM_MAPPING_CLASS[mechanism_family]
            == CROSS_SECTIONAL_RELATIVE
        )
        assert mapping_id_for_mechanism_family(mechanism_family) == (
            MECHANISM_MAPPING[CROSS_SECTIONAL_RELATIVE]
        )
    with pytest.raises(ValueError, match="unknown Broad mechanism family"):
        mapping_id_for_mechanism_family("UNREGISTERED_EVENT_MECHANISM")


def test_working_set_trim_is_thresholded_but_mandatory_at_lane_boundary() -> None:
    assert not _working_set_trim_due(
        current_rss=805_306_367, lane_index=3, lane_count=8
    )
    assert _working_set_trim_due(
        current_rss=805_306_368, lane_index=3, lane_count=8
    )
    assert _working_set_trim_due(current_rss=1, lane_index=7, lane_count=8)


def _role_complete_registry() -> TypedExpressionRegistry:
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


def test_rolling_scale_never_reads_future() -> None:
    registry = TypedExpressionRegistry((FieldContract("x", "RETURN", "dimensionless"),))
    expression = Expression(
        "RollingZScore", (Expression.raw("x"),), parameters={"window": 3}
    )
    original = np.arange(16, dtype=float).reshape(2, 8)
    changed = original.copy()
    changed[:, 5:] = 1e9
    left = materialize_expression(expression, registry=registry, field_reader=lambda _: original)
    right = materialize_expression(expression, registry=registry, field_reader=lambda _: changed)
    assert np.allclose(left[:, :5], right[:, :5], equal_nan=True)


def test_cross_asset_transform_excludes_ineligible_asset() -> None:
    registry = TypedExpressionRegistry((FieldContract("x", "RATIO", "dimensionless"),))
    expression = Expression("CrossSectionalRank", (Expression.raw("x"),))
    fields = np.array([[1.0], [2.0], [999999.0]])
    eligible = np.array([[True], [True], [False]])
    result = materialize_expression(
        expression,
        registry=registry,
        field_reader=lambda _: fields,
        eligible_mask=eligible,
    )
    assert result[0, 0] == 0.0
    assert result[1, 0] == 1.0
    assert np.isnan(result[2, 0])


def test_dag_limits_and_unit_checks_fail_closed() -> None:
    registry = TypedExpressionRegistry(
        (
            FieldContract("price", "PRICE", "quote_per_base"),
            FieldContract("volume", "VOLUME", "base_asset"),
        )
    )
    with pytest.raises(ValueError, match="incompatible units"):
        registry.validate(Expression("SafeAdd", (Expression.raw("price"), Expression.raw("volume"))))
    deep = Expression.raw("price")
    for _ in range(4):
        deep = Expression("SignedLog", (deep,))
    with pytest.raises(ValueError, match="depth"):
        registry.validate(deep)


def test_matched_control_retains_raw_inputs_and_support() -> None:
    registry = TypedExpressionRegistry(
        (
            FieldContract("a", "RATIO", "dimensionless"),
            FieldContract("b", "RATIO", "dimensionless"),
        )
    )
    primary = Expression("RatioInteraction", (Expression.raw("a"), Expression.raw("b")))
    control = ablate_expression(primary)
    assert registry.validate(primary).raw_fields == registry.validate(control).raw_fields
    fields = {"a": np.array([[1.0, 2.0]]), "b": np.array([[3.0, np.nan]])}
    p = materialize_expression(primary, registry=registry, field_reader=fields.__getitem__)
    c = materialize_expression(control, registry=registry, field_reader=fields.__getitem__)
    assert np.array_equal(np.isfinite(p), np.isfinite(c))


def test_all_forty_skeletons_generate_typed_matched_pairs() -> None:
    registry = _role_complete_registry()
    rng = random.Random(20260716)
    candidates = [
        generate_candidate(registry, skeleton=skeleton, rng=rng)
        for skeleton in skeleton_registry()
    ]
    assert len(candidates) == 40
    assert len({candidate.skeleton_id for candidate in candidates}) == 40
    for candidate in candidates:
        assert registry.validate(candidate.expression).raw_fields == registry.validate(
            candidate.control
        ).raw_fields


def test_current_price_levels_are_reachable_without_new_skeletons() -> None:
    contracts = tuple(_role_complete_registry().fields.values()) + (
        FieldContract("trade_close", "PRICE", "quote_per_base", 1, "CURRENT_FIELD_SURFACE_BINDING"),
        FieldContract("index_open", "PRICE", "quote_per_base", 1, "CURRENT_FIELD_SURFACE_BINDING"),
        FieldContract("index_high", "PRICE", "quote_per_base", 1, "CURRENT_FIELD_SURFACE_BINDING"),
        FieldContract("index_low", "PRICE", "quote_per_base", 1, "CURRENT_FIELD_SURFACE_BINDING"),
    )
    coverage = field_role_coverage(contracts)
    assert coverage["all_fields_reachable"] is True
    for field_id in ("trade_close", "index_open", "index_high", "index_low"):
        assert field_id in coverage["roles"]["local"]
        assert field_id not in coverage["roles"]["price_return"]


class _FakeStore:
    def __init__(self) -> None:
        rng = np.random.default_rng(7)
        self.shape = (6, 400)
        self._fields = {
            "a": rng.normal(size=self.shape),
            "b": rng.normal(size=self.shape),
        }
        self._eligible = np.ones(self.shape, dtype=bool)
        self._target = 0.001 * self._fields["a"] + rng.normal(scale=0.0005, size=self.shape)
        start = np.datetime64("2023-07-01T00:00:00", "ns").astype(np.int64)
        self.timestamp_ns = start + np.arange(self.shape[1], dtype=np.int64) * 3_600_000_000_000

    def field(self, name: str) -> np.ndarray:
        return self._fields[name]

    def base_eligible(self) -> np.ndarray:
        return self._eligible

    def target_return(self, horizon: int) -> np.ndarray:
        assert horizon == 1
        return self._target

    @property
    def target_metadata(self) -> dict[str, object]:
        return {
            "venue": "BINANCE_USD_M",
            "source": "TEST_BINANCE_OPEN",
            "price_field": "open_price",
            "formula": "log(open_price[t+2+h] / open_price[t+2])",
            "execution_delay_hours": 2,
            "horizons_hours": [1, 4],
            "positive_price_required": True,
            "missing_value_fill": None,
            "identity_sha256": "B" * 64,
        }

    def block_slice(self, start: str, end: str) -> slice:
        return slice(0, self.shape[1])


def test_incremental_sleeve_is_recomputed_from_delta_weights() -> None:
    registry = TypedExpressionRegistry(
        (
            FieldContract("a", "RATIO", "dimensionless"),
            FieldContract("b", "RATIO", "dimensionless"),
        )
    )
    primary = Expression("RatioInteraction", (Expression.raw("a"), Expression.raw("b")))
    control = ablate_expression(primary)
    assurance = registry.validate(primary)
    spec = CandidateSpec(
        "candidate",
        "skeleton",
        "OI_ACTIVITY_INTERACTION",
        primary,
        control,
        1,
        CROSS_SECTIONAL_ZERO_NET,
        assurance.raw_fields,
        ("family_a", "family_b"),
        assurance.rolling_windows,
        assurance.depth,
        "RatioInteraction(Raw,Raw)",
    )
    result = evaluate_pair(
        store=_FakeStore(),
        registry=registry,
        candidate=spec,
        block_start="2023-07-01T00:00:00Z",
        block_end="2024-07-01T00:00:00Z",
        block_role="DEVELOPMENT_ADAPTIVE_FEEDBACK",
    )
    assert result["delta_weight_sha256"] == result["incremental"]["weight_sha256"]
    assert result["incremental"]["turnover_mean"] >= 0.0
    assert result["scalar_net_delta_diagnostic"] != result["pair_reward"]


def test_train_orientation_is_consumed_and_persisted_when_receipt_is_bound() -> None:
    registry = TypedExpressionRegistry(
        (
            FieldContract("a", "RATIO", "dimensionless"),
            FieldContract("b", "RATIO", "dimensionless"),
        )
    )
    primary = Expression(
        "RatioInteraction",
        (Expression.raw("a"), Expression.raw("b")),
    )
    control = ablate_expression(primary)
    assurance = registry.validate(primary)
    spec = CandidateSpec(
        "candidate",
        "skeleton",
        "OI_ACTIVITY_INTERACTION",
        primary,
        control,
        1,
        CROSS_SECTIONAL_ZERO_NET,
        assurance.raw_fields,
        ("family_a", "family_b"),
        assurance.rolling_windows,
        assurance.depth,
        "RatioInteraction(Raw,Raw)",
    )
    start = "2023-07-01T00:00:00Z"
    end = "2024-07-01T00:00:00Z"
    result = evaluate_pair(
        store=_FakeStore(),
        registry=registry,
        candidate=spec,
        block_start=start,
        block_end=end,
        block_role="FRESH_DEVELOPMENT_TRAIN_ONLY",
        economic_receipt={
            "receipt_sha256": "A" * 64,
            "train": {"start": start, "end_exclusive": end},
            "direction": {"rule": "TRAIN_FROZEN_SIGN_ORIENTATION"},
            "portfolio": {"mapping_id": CROSS_SECTIONAL_ZERO_NET},
            "cost": {"cost_bps": 7.0},
            "execution": {
                **_FakeStore().target_metadata,
                "target_cache_identity_sha256": "B" * 64,
                "partition_tail_purge_hours": 6,
            },
        },
    )
    assert result["train_orientation"] in {-1.0, 1.0}
    assert result["economic_receipt_sha256"] == "A" * 64
    assert result["cost_bps"] == 7.0
    assert result["partition_tail_purge_hours"] == 6
    assert (
        result["effective_block_end_exclusive"]
        == "2024-06-30T18:00:00Z"
    )
    assert result["primary"]["cost_bps"] == 7.0
    assert result["incremental"]["cost_bps"] == 7.0


def test_validation_consumes_frozen_train_orientation_without_refit() -> None:
    registry = TypedExpressionRegistry(
        (
            FieldContract("a", "RATIO", "dimensionless"),
            FieldContract("b", "RATIO", "dimensionless"),
        )
    )
    primary = Expression(
        "RatioInteraction",
        (Expression.raw("a"), Expression.raw("b")),
    )
    assurance = registry.validate(primary)
    spec = CandidateSpec(
        "candidate-validation",
        "skeleton",
        "OI_ACTIVITY_INTERACTION",
        primary,
        ablate_expression(primary),
        1,
        CROSS_SECTIONAL_ZERO_NET,
        assurance.raw_fields,
        ("family_a", "family_b"),
        assurance.rolling_windows,
        assurance.depth,
        "RatioInteraction(Raw,Raw)",
    )
    train_start = "2023-07-01T00:00:00Z"
    train_end = "2023-08-01T00:00:00Z"
    validation_start = train_end
    validation_end = "2023-09-01T00:00:00Z"
    result = evaluate_pair(
        store=_FakeStore(),
        registry=registry,
        candidate=spec,
        block_start=validation_start,
        block_end=validation_end,
        block_role="FRESH_DEVELOPMENT_VALIDATION_KILL_LINE",
        economic_receipt={
            "receipt_sha256": "A" * 64,
            "train": {"start": train_start, "end_exclusive": train_end},
            "validation": {
                "role": "FRESH_DEVELOPMENT_VALIDATION_KILL_LINE",
                "start": validation_start,
                "end_exclusive": validation_end,
                "optimizer_feedback_allowed": False,
                "policy_memory_write_allowed": False,
                "candidate_generation_allowed": False,
            },
            "direction": {
                "rule": "TRAIN_FROZEN_SIGN_ORIENTATION",
                "allowed_values": [-1, 1],
            },
            "portfolio": {"mapping_id": CROSS_SECTIONAL_ZERO_NET},
            "cost": {"cost_bps": 7.0},
            "execution": {
                **_FakeStore().target_metadata,
                "target_cache_identity_sha256": "B" * 64,
                "partition_tail_purge_hours": 6,
            },
        },
        frozen_train_orientation=-1.0,
        include_validation_paths=True,
    )
    assert result["train_orientation"] == -1.0
    assert result["train_orientation_fitted"] is False
    assert result["evaluation_partition"] == "validation"
    assert result["partition_tail_purge_hours"] == 6
    assert (
        result["effective_block_end_exclusive"]
        == "2023-08-31T18:00:00Z"
    )
    assert result["_validation_paths"]["primary_net"].shape == (400,)
    with pytest.raises(
        ValueError,
        match="ECONOMIC_RECEIPT_VALIDATION_REQUIRES_FROZEN_ORIENTATION",
    ):
        evaluate_pair(
            store=_FakeStore(),
            registry=registry,
            candidate=spec,
            block_start=validation_start,
            block_end=validation_end,
            block_role="FRESH_DEVELOPMENT_VALIDATION_KILL_LINE",
            economic_receipt={
                "receipt_sha256": "A" * 64,
                "train": {"start": train_start, "end_exclusive": train_end},
                "validation": {
                    "role": "FRESH_DEVELOPMENT_VALIDATION_KILL_LINE",
                    "start": validation_start,
                    "end_exclusive": validation_end,
                    "optimizer_feedback_allowed": False,
                    "policy_memory_write_allowed": False,
                    "candidate_generation_allowed": False,
                },
                "direction": {
                    "rule": "TRAIN_FROZEN_SIGN_ORIENTATION",
                    "allowed_values": [-1, 1],
                },
                "portfolio": {"mapping_id": CROSS_SECTIONAL_ZERO_NET},
                "cost": {"cost_bps": 7.0},
                "execution": {
                    **_FakeStore().target_metadata,
                    "target_cache_identity_sha256": "B" * 64,
                    "partition_tail_purge_hours": 6,
                },
            },
        )


def test_frozen_validation_stage_stops_failed_arm_and_restores_exactly(
    tmp_path: Path,
) -> None:
    registry = _role_complete_registry()
    arms = (
        "canonical_typed_random",
        "hierarchical_typed_cem_v2",
        "typed_evolution_v2",
    )
    source_sha = "a" * 40
    frozen_hash = "b" * 64
    state = _new_campaign_state(source_sha, frozen_hash, arms=arms, seeds=SEEDS)
    state["next_checkpoint_index"] = 1
    policies = _initial_policies(registry, arms=arms, seeds=SEEDS)
    policy_hash_before = _payload_sha(
        {
            key: _export_policy(policy)
            for key, policy in sorted(policies.items())
        }
    )
    archive = BehaviorArchive()
    candidate = generate_candidate(
        registry,
        skeleton=skeleton_registry()[0],
        rng=random.Random(19),
    )
    train_ledger = []
    for arm in arms:
        for ordinal in range(1, 129):
            local = CandidateSpec(
                f"{arm}-{ordinal:03d}",
                candidate.skeleton_id,
                candidate.mechanism_family,
                candidate.expression,
                candidate.control,
                1 if ordinal <= 64 else 4,
                candidate.mapping_id,
                candidate.raw_fields,
                candidate.field_families,
                candidate.rolling_windows,
                candidate.expression_depth,
                candidate.operator_path,
            )
            train_ledger.append(
                {
                    "arm": arm,
                    "arm_completion_ordinal": ordinal,
                    "candidate_id": local.candidate_id,
                    "candidate_spec_json": json.dumps(
                        local.to_dict(), sort_keys=True
                    ),
                    "search_reward": float(ordinal),
                    "search_reward_authority": SEARCH_REWARD_AUTHORITY,
                        "search_reward_matched_limiting_component": (
                            "primary_minus_left_control"
                        ),
                        "train_orientation": 1.0,
                        "train_orientation_fitted": True,
                        "evaluation_partition": "train",
                        "economic_receipt_sha256": "R" * 64,
                }
            )

    def evaluate_validation(candidate_spec, frozen_orientation):
        failed = candidate_spec.candidate_id.startswith(
            "hierarchical_typed_cem_v2"
        )
        primary = -0.001 if failed else 0.001
        matched = -0.0005 if failed else 0.0005
        return {
            "candidate_id": candidate_spec.candidate_id,
            "horizon_hours": candidate_spec.horizon_hours,
            "train_orientation": frozen_orientation,
            "train_orientation_fitted": False,
            "evaluation_partition": "validation",
            "effective_block_end_exclusive": "2025-12-31T18:00:00Z",
            "partition_tail_purge_hours": 6,
            "_validation_paths": {
                "primary_net": np.full(48, primary),
                "control_net": {
                    "left": np.zeros(48),
                    "right": np.zeros(48),
                },
                "matched_component_net": {
                    "primary_minus_left_control": np.full(48, matched),
                    "primary_minus_right_control": np.full(48, matched),
                },
            },
        }

    receipt = {
        "receipt_sha256": "R" * 64,
        "execution": {
            "execution_delay_hours": 2,
            "horizons_hours": [1, 4],
            "partition_tail_purge_hours": 6,
        },
        "validation": {
            "role": "FRESH_DEVELOPMENT_VALIDATION_KILL_LINE",
            "start": "2025-11-01T00:00:00Z",
            "end_exclusive": "2026-01-01T00:00:00Z",
            "optimizer_feedback_allowed": False,
            "policy_memory_write_allowed": False,
            "candidate_generation_allowed": False,
        },
        "validation_kill_line": {
            "orchestration_campaign": "crypto_search_economic_v1",
            "trigger_after_train_checkpoint_index": 0,
            "minimum_evaluated_per_active_arm": 128,
            "evaluated_per_active_arm": 128,
            "required_horizons_hours": [1, 4],
            "evaluated_per_arm_per_horizon": 64,
            "candidate_selection": (
                "TOP_TRAIN_SEARCH_REWARD_PER_REQUIRED_HORIZON_"
                "THEN_COMPLETION_ORDINAL"
            ),
            "arm_aggregation": (
                "WORST_HORIZON_EQUAL_WEIGHT_FROZEN_CANDIDATE_ENSEMBLE"
            ),
        },
    }
    identities = {
        "raw_cache": {"identity_sha256": "C" * 64},
        "compiler_identity": {"sha256": "D" * 64},
    }
    (
        restored_state,
        restored_policies,
        restored_ledger,
        restored_archive,
        restored_metrics,
        result,
    ) = run_frozen_validation_stage(
        runtime_root=tmp_path,
        store=_FakeStore(),
        registry=registry,
        state=state,
        policies=policies,
        train_ledger=train_ledger,
        archive=archive,
        train_metrics=[],
        identities=identities,
        economic_receipt=receipt,
        evaluation_runner=evaluate_validation,
    )
    assert result["resumed"] is False
    assert result["matched_evaluated_counts"] == {
        arm: 128 for arm in arms
    }
    metrics_frame = pd.read_parquet(
        tmp_path / "validation_arm_metrics.parquet"
    )
    assert set(metrics_frame["required_horizons_hours_json"]) == {"[1,4]"}
    assert restored_state["arm_states"]["hierarchical_typed_cem_v2"] == "EXITED"
    assert restored_state["arm_states"]["canonical_typed_random"] == "ACTIVE"
    assert restored_state["arm_states"]["typed_evolution_v2"] == "ACTIVE"
    next_allocation = _checkpoint_allocation(
        1, restored_state["arm_states"]
    )
    assert next_allocation["hierarchical_typed_cem_v2"] == 0
    assert next_allocation["canonical_typed_random"] >= 400
    assert restored_state["generation_attempts"] == 0
    assert (
        restored_state["validation_stage"]["candidate_generation_performed"]
        is False
    )
    assert restored_archive.state_hash() == archive.state_hash()
    assert _payload_sha(
        {
            key: _export_policy(policy)
            for key, policy in sorted(restored_policies.items())
        }
    ) == policy_hash_before
    assert restored_ledger == train_ledger
    assert restored_metrics == []
    assert (
        tmp_path / "checkpoints" / "checkpoint_validation" / "manifest.json"
    ).is_file()
    assert (tmp_path / "validation_candidate_ledger.parquet").is_file()
    assert (tmp_path / "validation_arm_metrics.parquet").is_file()

    def must_not_reevaluate(*_args):
        raise AssertionError("restored validation checkpoint must not reevaluate")

    (tmp_path / "validation_candidate_ledger.parquet").unlink()
    (tmp_path / "validation_arm_metrics.parquet").unlink()
    (tmp_path / "validation_decisions.json").unlink()
    resumed = run_frozen_validation_stage(
        runtime_root=tmp_path,
        store=_FakeStore(),
        registry=registry,
        state=state,
        policies=policies,
        train_ledger=train_ledger,
        archive=archive,
        train_metrics=[],
        identities=identities,
        economic_receipt=receipt,
        evaluation_runner=must_not_reevaluate,
    )
    assert resumed[-1]["resumed"] is True
    assert resumed[0]["validation_stage"] == restored_state["validation_stage"]
    assert (tmp_path / "validation_candidate_ledger.parquet").is_file()
    assert (tmp_path / "validation_arm_metrics.parquet").is_file()
    assert (tmp_path / "validation_decisions.json").is_file()


def _minimal_validation_failure_inputs(
    tmp_path: Path,
) -> dict[str, object]:
    registry = _role_complete_registry()
    arms = ("canonical_typed_random",)
    source_sha = "a" * 40
    frozen_hash = "b" * 64
    state = _new_campaign_state(source_sha, frozen_hash, arms=arms, seeds=SEEDS)
    state["next_checkpoint_index"] = 1
    policies = _initial_policies(registry, arms=arms, seeds=SEEDS)
    archive = BehaviorArchive()
    candidate = generate_candidate(
        registry,
        skeleton=skeleton_registry()[0],
        rng=random.Random(29),
    )
    train_ledger = []
    for ordinal, horizon in enumerate((1, 4), start=1):
        local = CandidateSpec(
            f"validation-failure-{horizon}h",
            candidate.skeleton_id,
            candidate.mechanism_family,
            candidate.expression,
            candidate.control,
            horizon,
            candidate.mapping_id,
            candidate.raw_fields,
            candidate.field_families,
            candidate.rolling_windows,
            candidate.expression_depth,
            candidate.operator_path,
        )
        train_ledger.append(
            {
                "arm": arms[0],
                "arm_completion_ordinal": ordinal,
                "candidate_id": local.candidate_id,
                "candidate_spec_json": json.dumps(
                    local.to_dict(), sort_keys=True
                ),
                "search_reward": float(3 - ordinal),
                "search_reward_authority": SEARCH_REWARD_AUTHORITY,
                "search_reward_matched_limiting_component": (
                    "primary_minus_left_control"
                ),
                "train_orientation": 1.0,
                "train_orientation_fitted": True,
                "evaluation_partition": "train",
                "economic_receipt_sha256": "R" * 64,
            }
        )
    return {
        "runtime_root": tmp_path,
        "store": _FakeStore(),
        "registry": registry,
        "state": state,
        "policies": policies,
        "train_ledger": train_ledger,
        "archive": archive,
        "train_metrics": [],
        "identities": {
            "raw_cache": {"identity_sha256": "C" * 64},
            "compiler_identity": {"sha256": "D" * 64},
        },
        "economic_receipt": {
            "receipt_sha256": "R" * 64,
            "execution": {
                "horizons_hours": [1, 4],
                "partition_tail_purge_hours": 6,
            },
            "validation": {
                "optimizer_feedback_allowed": False,
                "policy_memory_write_allowed": False,
                "candidate_generation_allowed": False,
            },
            "validation_kill_line": {
                "minimum_evaluated_per_active_arm": 2,
                "evaluated_per_active_arm": 2,
                "required_horizons_hours": [1, 4],
                "evaluated_per_arm_per_horizon": 1,
                "candidate_selection": (
                    "TOP_TRAIN_SEARCH_REWARD_PER_REQUIRED_HORIZON_"
                    "THEN_COMPLETION_ORDINAL"
                ),
                "arm_aggregation": (
                    "WORST_HORIZON_EQUAL_WEIGHT_FROZEN_CANDIDATE_ENSEMBLE"
                ),
            },
        },
    }


def test_frozen_validation_constructibility_failure_is_typed_and_side_effect_free(
    tmp_path: Path,
) -> None:
    inputs = _minimal_validation_failure_inputs(tmp_path)
    state_before = deepcopy(inputs["state"])
    policy_hash_before = _payload_sha(
        {
            key: _export_policy(policy)
            for key, policy in sorted(inputs["policies"].items())
        }
    )
    archive_hash_before = inputs["archive"].state_hash()

    def reject_degenerate_control(*_args):
        raise ValueError("CONTROL_BEHAVIOR_EQUALS_PRIMARY")

    with pytest.raises(_ValidationStageBlocked) as captured:
        run_frozen_validation_stage(
            **inputs,
            evaluation_runner=reject_degenerate_control,
        )

    assert captured.value.to_dict() == {
        "reason": "CONTROL_BEHAVIOR_EQUALS_PRIMARY",
        "arm": "canonical_typed_random",
        "candidate_id": "validation-failure-1h",
        "horizon_hours": 1,
        "selection_rank": 1,
    }
    assert inputs["state"] == state_before
    assert inputs["archive"].state_hash() == archive_hash_before
    assert _payload_sha(
        {
            key: _export_policy(policy)
            for key, policy in sorted(inputs["policies"].items())
        }
    ) == policy_hash_before
    assert not (tmp_path / "checkpoints").exists()
    assert not (tmp_path / "validation_candidate_ledger.parquet").exists()


def test_frozen_validation_unexpected_value_error_still_propagates(
    tmp_path: Path,
) -> None:
    inputs = _minimal_validation_failure_inputs(tmp_path)

    def reject_unexpected(*_args):
        raise ValueError("UNEXPECTED_VALIDATION_DEFECT")

    with pytest.raises(ValueError, match="UNEXPECTED_VALIDATION_DEFECT"):
        run_frozen_validation_stage(
            **inputs,
            evaluation_runner=reject_unexpected,
        )
    assert not (tmp_path / "checkpoints").exists()


def test_frozen_validation_trigger_precedes_reachable_next_allocation() -> None:
    receipt = {
        "validation_kill_line": {
            "orchestration_campaign": "crypto_search_economic_v1",
            "trigger_after_train_checkpoint_index": 0,
        }
    }
    state = {
        "next_checkpoint_index": 0,
        "arm_states": {
            "canonical_typed_random": "ACTIVE",
            "hierarchical_typed_cem_v2": "ACTIVE",
            "typed_evolution_v2": "ACTIVE",
        },
    }
    assert not _frozen_validation_due(
        campaign="crypto_search_economic_v1",
        state=state,
        economic_receipt=receipt,
    )
    state["next_checkpoint_index"] = 1
    assert _frozen_validation_due(
        campaign="crypto_search_economic_v1",
        state=state,
        economic_receipt=receipt,
    )
    state["validation_stage"] = {"status": "VALIDATION_STAGE_COMPLETE"}
    state["arm_states"]["hierarchical_typed_cem_v2"] = "EXITED"
    assert not _frozen_validation_due(
        campaign="crypto_search_economic_v1",
        state=state,
        economic_receipt=receipt,
    )
    next_allocation = _checkpoint_allocation(1, state["arm_states"])
    assert next_allocation["hierarchical_typed_cem_v2"] == 0
    assert sum(next_allocation.values()) == 2_000
    with pytest.raises(
        RuntimeError,
        match="ECONOMIC_RECEIPT_VALIDATION_CAMPAIGN_CHANGED",
    ):
        _frozen_validation_due(
            campaign="legacy",
            state=state,
            economic_receipt=receipt,
        )


def test_checkpoint_resume_order_prefers_validation_only_at_same_progress(
    tmp_path: Path,
) -> None:
    checkpoints = tmp_path / "checkpoints"
    paths = {}
    for name, next_index in (
        ("checkpoint_000", 1),
        ("checkpoint_validation", 1),
        ("checkpoint_001", 2),
    ):
        path = checkpoints / name
        path.mkdir(parents=True)
        (path / "state.json").write_text(
            json.dumps({"next_checkpoint_index": next_index}),
            encoding="utf-8",
        )
        paths[name] = path
    assert max(
        (paths["checkpoint_000"], paths["checkpoint_validation"]),
        key=_checkpoint_resume_order,
    ).name == "checkpoint_validation"
    assert max(paths.values(), key=_checkpoint_resume_order).name == (
        "checkpoint_001"
    )


def test_economic_search_surface_is_exactly_receipt_bound() -> None:
    contracts = tuple(_role_complete_registry().fields.values())
    receipt = {
        "evidence_partition": {
            "train": {
                "start": "2025-08-29T07:00:00Z",
                "end_exclusive": "2025-11-01T00:00:00Z",
            }
        },
        "search_campaign": {
            "runner_campaign": "crypto_search_economic_v1",
            "carrier_id": (
                "OI_MARK_RANKS51_200_X_AGGTRADES_TOP200_ALIGNED"
            ),
            "carrier_cache_identity_sha256": "C" * 64,
            "carrier_manifest": "runtime/carrier.json",
            "field_count": len(contracts),
            "strict_evaluated_target": 20_000,
            "checkpoint_size": 2_000,
            "checkpoint_count": 10,
        }
    }
    identities = {
        "raw_cache": {
            "root": ".cache/carrier",
            "identity_sha256": "C" * 64,
        },
        "aligned_carrier_manifest": {"path": "runtime/carrier.json"},
        "behavior_contract_window": {
            "start": "2025-08-29T07:00:00Z",
            "end_exclusive": "2025-11-01T00:00:00Z",
            "authority": "ECONOMIC_RECEIPT_TRAIN_ONLY",
            "validation_read": False,
            "holdout_read": False,
        },
    }
    assert _validate_economic_search_surface(
        receipt=receipt,
        identities=identities,
        contracts=contracts,
    ) == "OI_MARK_RANKS51_200_X_AGGTRADES_TOP200_ALIGNED"
    changed = deepcopy(receipt)
    changed["search_campaign"]["field_count"] += 1
    with pytest.raises(
        RuntimeError,
        match="ECONOMIC_SEARCH_SURFACE_BINDING_CHANGED:field_count",
    ):
        _validate_economic_search_surface(
            receipt=changed,
            identities=identities,
            contracts=contracts,
        )


def test_report_only_metrics_are_not_policy_feedback() -> None:
    contract = feedback_contract_payload()
    assert contract["report_only_metrics_visible_to_policy"] is False
    assert contract["authoritative_search_feedback"] == SEARCH_REWARD_AUTHORITY
    assert contract["matched_attribution_feedback"].startswith("incremental sleeve")
    assert contract["matched_attribution_is_search_ordering_authority"] is False


def test_unvisited_candidate_cannot_receive_feedback() -> None:
    policy = LanePolicy("canonical_typed_random", 20260716, _role_complete_registry())
    candidate, _ = policy.propose()
    other = CandidateSpec(
        "not-visited",
        candidate.skeleton_id,
        candidate.mechanism_family,
        candidate.expression,
        candidate.control,
        candidate.horizon_hours,
        candidate.mapping_id,
        candidate.raw_fields,
        candidate.field_families,
        candidate.rolling_windows,
        candidate.expression_depth,
        candidate.operator_path,
    )
    with pytest.raises(PermissionError, match="unvisited"):
        policy.update(other, 1.0)


def test_policy_private_state_and_deterministic_replay() -> None:
    registry = _role_complete_registry()
    first = LanePolicy("cem_diversity_v2", 20260716, registry)
    second = LanePolicy("cem_diversity_v2", 20260716, registry)
    for _ in range(12):
        left, _ = first.propose()
        right, _ = second.propose()
        assert left.candidate_id == right.candidate_id
        first.update(left, 0.25)
        second.update(right, 0.25)
    isolated = LanePolicy("uct_ucb_like", 20260716, registry)
    isolated_hash = isolated.state_hash()
    candidate, _ = first.propose()
    first.update(candidate, 1.0)
    assert isolated.state_hash() == isolated_hash


def test_candidate_gene_roundtrip_preserves_identity() -> None:
    registry = _role_complete_registry()
    original = generate_candidate(
        registry, skeleton=skeleton_registry()[3], rng=random.Random(20260720)
    )
    rebuilt = candidate_from_genes(
        registry,
        skeleton=skeleton_registry()[3],
        genes=original.generation_genes,
    )
    assert rebuilt.candidate_id == original.candidate_id
    assert rebuilt.to_dict() == original.to_dict()


def test_typed_mutation_changes_one_gene_and_receipt_detects_tampering() -> None:
    registry = _role_complete_registry()
    parent = generate_candidate(
        registry, skeleton=skeleton_registry()[3], rng=random.Random(20260720)
    )
    child, receipt = typed_mutate_candidate(
        registry, parent=parent, rng=random.Random(20260721)
    )
    assert parent.candidate_id != child.candidate_id
    changed = {
        key
        for key in parent.generation_genes
        if parent.generation_genes[key] != child.generation_genes[key]
    }
    assert changed == {receipt["changed_gene"]}
    assert registry.validate(child.expression).raw_fields == registry.validate(
        child.control
    ).raw_fields
    assert verify_typed_mutation_receipt(registry, parent, child, receipt) is True
    tampered = dict(receipt)
    tampered["after"] = "not-the-child-value"
    assert verify_typed_mutation_receipt(registry, parent, child, tampered) is False


def test_real_cem_updates_only_on_complete_generation_and_replays() -> None:
    registry = _role_complete_registry()
    params = {
        "generation_size": 4,
        "elite_fraction": 0.25,
        "smoothing": 0.5,
        "minimum_probability": 0.005,
        "duplicate_resample_limit": 16,
    }
    first = LanePolicy("cem_distribution_v1", 20260720, registry, params)
    second = LanePolicy("cem_distribution_v1", 20260720, registry, params)
    initial_hash = first.distribution_hash()
    for step in range(5):
        left, left_meta = first.propose()
        right, right_meta = second.propose()
        assert left.candidate_id == right.candidate_id
        assert left_meta["policy_diagnostics"] == right_meta["policy_diagnostics"]
        first.update(left, float(step))
        second.update(right, float(step))
        if step < 3:
            assert first.distribution_hash() == initial_hash
    assert first.cem_update_count == 1
    assert first.distribution_hash() != initial_hash
    for probabilities in first.cem_probabilities.values():
        assert sum(probabilities.values()) == pytest.approx(1.0)
        assert min(probabilities.values()) >= 0.005
    assert first.state_hash() == second.state_hash()


def test_real_typed_evolution_replays_and_verifies_every_mutation() -> None:
    registry = _role_complete_registry()
    params = {
        "warmup": 4,
        "exploration_probability": 0.0,
        "tournament_size": 3,
        "duplicate_resample_limit": 16,
    }
    first = LanePolicy("evolutionary_typed_v1", 20260720, registry, params)
    second = LanePolicy("evolutionary_typed_v1", 20260720, registry, params)
    mutation_count = 0
    for step in range(10):
        left, left_meta = first.propose()
        right, right_meta = second.propose()
        assert left.candidate_id == right.candidate_id
        assert left_meta == right_meta
        if left_meta["mutation_receipt"] is not None:
            mutation_count += 1
            parent = first.candidates[left_meta["parent_id"]]
            assert left_meta["mutation_receipt_verified"] is True
            assert verify_typed_mutation_receipt(
                registry, parent, left, left_meta["mutation_receipt"]
            )
        reward = float(step % 3)
        first.update(left, reward)
        second.update(right, reward)
    assert mutation_count == 6
    assert first.state_hash() == second.state_hash()


def test_real_typed_evolution_survives_all_formal_seeds_for_128_steps() -> None:
    registry = _role_complete_registry()
    params = {
        "warmup": 16,
        "exploration_probability": 0.25,
        "tournament_size": 4,
        "duplicate_resample_limit": 16,
    }
    for seed in (20260716, 20260717, 20260718, 20260719):
        policy = LanePolicy("evolutionary_typed_v1", seed, registry, params)
        for step in range(128):
            candidate, metadata = policy.propose()
            if metadata["mutation_receipt"] is not None:
                parent = policy.candidates[metadata["parent_id"]]
                assert verify_typed_mutation_receipt(
                    registry, parent, candidate, metadata["mutation_receipt"]
                )
            policy.update(candidate, float(step % 7))


def test_frozen_config_keeps_sealed_reads_and_promotion_disabled() -> None:
    config = json.loads(
        (Path(__file__).parents[1] / "config" / "crypto_18m_compositional_broad_search_v1.json").read_text()
    )
    assert config["boundaries"]["sealed_reads_allowed"] is False
    assert config["boundaries"]["candidate_promotion"] is False
    assert config["boundaries"]["formal_performance_search"] is False
    assert config["budget"]["stage_a_pairs"] == 4096


def test_current_field_continuation_binds_broad_39_and_original_policies() -> None:
    repo_root = Path(__file__).parents[1]
    config = json.loads(
        (
            repo_root
            / "config"
            / "crypto_18m_current_field_four_policy_continuation_v1.json"
        ).read_text()
    )
    _validate_config(config)
    binding, fields = _current_field_surface_binding(repo_root, config)
    assert len(fields or ()) == 39
    assert binding is not None
    assert binding["view_counts"] == {"asset_local": 38, "market_state": 1}
    assert binding["excluded_contexts"] == ["CORE3_MICROSTRUCTURE_PILOT"]
    assert binding["generator_role_coverage"]["all_fields_reachable"] is True
    assert config["budget"]["policies"] == [
        "canonical_typed_random",
        "cem_diversity_v2",
        "uct_ucb_like",
        "evolutionary",
    ]
    assert config["budget"]["stage_b_activation"] == "FROZEN_FULL_BUDGET"
    assert config["fresh_policy_state"] is True
    assert config["boundaries"]["sealed_reads_allowed"] is False
    assert config["boundaries"]["candidate_promotion"] is False


def test_policy_productivity_gate_uses_seed_matched_random_controls() -> None:
    rows = []
    for seed in (20260716, 20260717):
        rows.extend(
            [
                {
                    "policy": "canonical_typed_random",
                    "seed": seed,
                    "candidate_id": f"random-parent-{seed}",
                    "parent_id": None,
                    "search_reward": 0.0,
                    "pair_reward": 0.0,
                    "matched_positive": False,
                    "skeleton_id": "random-a",
                    "mechanism_family": "OI_PRICE_DIVERGENCE",
                    "mutation_receipt_json": "null",
                    "cache_hit": False,
                },
                {
                    "policy": "canonical_typed_random",
                    "seed": seed,
                    "candidate_id": f"random-child-{seed}",
                    "parent_id": None,
                    "search_reward": 0.1,
                    "pair_reward": 0.1,
                    "matched_positive": True,
                    "skeleton_id": "random-b",
                    "mechanism_family": "OI_ACTIVITY_INTERACTION",
                    "mutation_receipt_json": "null",
                    "cache_hit": False,
                },
                {
                    "policy": "cem_diversity_v2",
                    "seed": seed,
                    "candidate_id": f"cem-{seed}",
                    "parent_id": None,
                    "search_reward": 0.5,
                    "pair_reward": 0.5,
                    "matched_positive": True,
                    "skeleton_id": "cem-a",
                    "mechanism_family": "BASIS_PREMIUM_STATE",
                    "mutation_receipt_json": "null",
                    "cache_hit": False,
                },
                {
                    "policy": "evolutionary",
                    "seed": seed,
                    "candidate_id": f"evo-parent-{seed}",
                    "parent_id": None,
                    "search_reward": 0.2,
                    "pair_reward": 0.2,
                    "matched_positive": True,
                    "skeleton_id": "evo-a",
                    "mechanism_family": "PRICE_ACTIVITY_RESPONSE",
                    "mutation_receipt_json": "{}",
                    "cache_hit": False,
                },
                {
                    "policy": "evolutionary",
                    "seed": seed,
                    "candidate_id": f"evo-child-{seed}",
                    "parent_id": f"evo-parent-{seed}",
                    "search_reward": 0.6,
                    "pair_reward": 0.6,
                    "matched_positive": True,
                    "skeleton_id": "evo-b",
                    "mechanism_family": "STATE_REGIME_MODULATION",
                    "mutation_receipt_json": "{}",
                    "cache_hit": False,
                },
            ]
        )
    audit = _policy_audit(rows, minimum_positive_seed_count=2)
    decisions = audit["post_search_upgrade_qualification"]
    assert (
        decisions["cem_diversity_v2"]["decision"]
        == "ELIGIBLE_FOR_DISTRIBUTION_SEARCH_UPGRADE"
    )
    assert (
        decisions["evolutionary"]["decision"]
        == "ELIGIBLE_FOR_TYPED_MUTATION_UPGRADE"
    )
    assert decisions["current_run_feedback"] is False


def test_raw_cache_bundle_excludes_run_logs_and_checkpoints(tmp_path: Path) -> None:
    (tmp_path / "fields").mkdir()
    metadata = {"field_ids": ["x"]}
    (tmp_path / "metadata.json").write_text(json.dumps(metadata))
    for name in (
        "timestamp_ns.npy",
        "observed.npy",
        "base_eligible.npy",
        "source_segment.npy",
        "target_return_1h.npy",
        "target_return_4h.npy",
    ):
        np.save(tmp_path / name, np.array([0]))
    np.save(tmp_path / "fields" / "x.npy", np.array([1.0]))
    before = _directory_bundle(tmp_path)
    (tmp_path / "formal_run.stdout.log").write_text("runtime log")
    (tmp_path / "expressivity_checkpoint.json").write_text("{}")
    assert _directory_bundle(tmp_path) == before


def test_current_continuation_exact_budget_fails_closed() -> None:
    repo_root = Path(__file__).parents[1]
    config = json.loads(
        (
            repo_root
            / "config"
            / "crypto_18m_current_field_four_policy_continuation_v1.json"
        ).read_text()
    )
    changed = deepcopy(config)
    changed["budget"]["maximum_stage_b_pairs"] = 2048
    with pytest.raises(ValueError, match="frozen budget"):
        _validate_config(changed)


def _fake_search_evaluation(candidate: CandidateSpec, family_id: str, reward: float) -> dict:
    behavior = {
        "behavior_family_id": family_id,
        "coordinate_data_binding_id": "C" * 64,
        "rank_descriptor_id": "R" * 64,
        "selected_asset_overlap_id": "S" * 64,
        "mapped_weight_descriptor_id": "W" * 64,
        "turnover_path_descriptor_id": "T" * 64,
        "pit_regime_descriptor_id": "P" * 64,
        "descriptor_contract_sha256": "D" * 64,
        "descriptor_schema_version": "CRYPTO_SEARCH_BEHAVIOR_DESCRIPTOR_V1",
        "identity_excludes": [
            "gross",
            "net",
            "cost",
            "search_reward",
            "pair_reward",
        ],
    }
    return {
        "candidate_id": candidate.candidate_id,
        "search_reward": reward,
        "search_reward_authority": SEARCH_REWARD_AUTHORITY,
        "pair_reward": reward,
        "matched_positive": reward > 0.0,
        "incremental": {"gross_mean": 0.0, "net_mean": 0.0, "cost_mean": 0.0},
        "behavior": behavior,
    }


def _valid_active_universe_series() -> np.ndarray:
    active = np.full((3, 8), np.nan, dtype=float)
    counts = (3, 3, 2, 2, 3, 1, 2, 3)
    for column, count in enumerate(counts):
        active[:count, column] = float(count)
    return active


def test_search_behavior_descriptor_is_frozen_coarse_and_outcome_free() -> None:
    active = _valid_active_universe_series()
    contract = freeze_search_behavior_contract(active, np.isfinite(active))
    signal = np.asarray(
        [[1, 2, 3, 4, 5, 6, 7, 8], [2, 1, 4, 3, 6, 5, 8, 7], [3, 3, 2, 2, 1, 1, 0, 0]],
        dtype=float,
    )
    weights = np.sign(signal - np.nanmean(signal, axis=0)) * 0.25
    kwargs = {
        "signal": signal,
        "weights": weights,
        "eligible_mask": np.ones_like(signal, dtype=bool),
        "month_labels": np.asarray(["2023-07"] * 4 + ["2023-08"] * 4),
        "timestamp_ns": np.arange(8, dtype=np.int64),
        "active_universe_size": active,
        "horizon_hours": 1,
        "mapping_id": CROSS_SECTIONAL_ZERO_NET,
        "contract": contract,
    }
    first = search_behavior_descriptor(**kwargs)
    second = search_behavior_descriptor(**kwargs)
    assert first == second
    assert first["behavior_family_id"]
    assert first["identity_excludes"] == [
        "gross",
        "net",
        "cost",
        "search_reward",
        "pair_reward",
    ]
    changed_contract = deepcopy(contract)
    changed_contract["mapped_weight_quantization_step"] = 0.01
    with pytest.raises(ValueError, match="contract identity"):
        search_behavior_descriptor(**{**kwargs, "contract": changed_contract})


def test_behavior_contract_rejects_partition_local_universe_counts() -> None:
    broken = np.ones((3, 8), dtype=float)
    with pytest.raises(ValueError, match="active_universe_size"):
        freeze_search_behavior_contract(broken, np.ones_like(broken, dtype=bool))


def test_panel_context_fields_are_rebuilt_after_source_join() -> None:
    observed = np.asarray(
        [
            [True, True, True, True, True, True],
            [True, True, True, True, True, True],
            [False, False, True, True, True, True],
        ],
        dtype=bool,
    )
    listing_age_hours = np.asarray(
        [
            [100, 101, 102, 103, 104, 105],
            [100, 101, 102, 103, 104, 105],
            [np.nan, np.nan, 1, 2, 3, 4],
        ],
        dtype=float,
    )
    rebuilt = rebuild_panel_context_fields(
        observed=observed,
        listing_age_hours=listing_age_hours,
    )
    active = rebuilt["active_universe_size"]
    history = rebuilt["history_length_hours"]
    percentile = rebuilt["age_percentile_active_universe"]
    assert active[:, 0][np.isfinite(active[:, 0])].tolist() == [2.0, 2.0]
    assert active[:, 2].tolist() == [3.0, 3.0, 3.0]
    assert history[0].tolist() == pytest.approx([1, 2, 3, 4, 5, 6])
    assert history[2, 2:].tolist() == pytest.approx([1, 2, 3, 4])
    assert np.isnan(history[2, :2]).all()
    assert percentile[:2, 0].tolist() == pytest.approx([0.75, 0.75])
    assert percentile[:, 2].tolist() == pytest.approx(
        [2.5 / 3.0, 2.5 / 3.0, 1.0 / 3.0]
    )


def test_horizon_aware_lcb_accounts_for_overlapping_return_dependence() -> None:
    values = np.repeat(np.linspace(-1.0, 1.0, 64), 4)
    _, iid_se, iid_lcb, _ = _mean_lcb(values, dependency_lags=0)
    _, hac_se, hac_lcb, _ = _mean_lcb(values, dependency_lags=3)
    assert hac_se > iid_se
    assert hac_lcb < iid_lcb


def test_hac_preserves_missing_hour_coordinates() -> None:
    values = np.asarray([-1.0, -1.0, np.nan, 1.0, 1.0])
    _, se_with_gap, _, _ = _mean_lcb(values, dependency_lags=1)
    _, se_if_compressed, _, _ = _mean_lcb(
        values[np.isfinite(values)],
        dependency_lags=1,
    )
    assert se_with_gap > se_if_compressed


def test_monthly_metrics_preserve_gross_cost_net_waterfall() -> None:
    metrics = _series_metrics(
        weights=np.asarray([[1.0, 1.0, 1.0, 1.0]]),
        target=np.asarray([[0.01, 0.01, 0.01, 0.01]]),
        months=np.asarray(["2024-01"] * 4),
        evaluation_mask=np.asarray([True, True, True, True]),
        horizon=1,
    )
    month = metrics["month_metrics"][0]
    assert month["gross_mean"] - month["cost_mean"] == pytest.approx(
        month["net_mean"]
    )


def test_evaluation_audit_fields_preserve_matched_waterfall_and_cost_meaning() -> None:
    section = {
        "gross_mean": 0.001,
        "net_mean": -0.001,
        "net_lcb": -0.002,
        "net_standard_error": 0.0001,
        "net_standard_error_method": "NEWEY_WEST_BARTLETT",
        "net_standard_error_lags": 3,
        "monthly_block_lcb": -0.003,
        "turnover_mean": 0.2,
        "cost_mean": 0.0001,
        "support": 1.0,
        "month_metrics": [{"month": "2023-07", "net_mean": -0.001}],
    }
    evaluation = {
        "primary": {**section, "net_mean": 0.001},
        "control": {**section, "gross_mean": 0.0},
        "incremental": section,
        "scalar_net_delta_diagnostic": 0.002,
        "feedback": {"violations": ["NET_LCB"]},
    }
    fields = _evaluation_audit_fields(evaluation)
    assert fields["cost_killed"] is True
    assert fields["gross_positive_cost_sign_killed"] is True
    assert fields["cost_threshold_violated"] is False
    assert fields["turnover_killed"] is False
    assert fields["scalar_net_delta_diagnostic"] == pytest.approx(0.002)
    assert json.loads(fields["primary_month_metrics_json"])[0]["month"] == "2023-07"
    assert json.loads(fields["control_month_metrics_json"])[0]["net_mean"] == pytest.approx(
        -0.001
    )


def test_hierarchical_cem_v2_samples_legal_order_and_roundtrips_state() -> None:
    registry = _role_complete_registry()
    policy = HierarchicalTypedCEMV2(20260721, registry)
    rows = []
    for index in range(48):
        candidate, metadata = policy.propose()
        assert metadata["operation"] == "HIERARCHICAL_TYPED_CEM_SAMPLE"
        assert _role_complete_registry().validate(candidate.expression)
        rows.append(
            {
                "search_reward": float(index % 7),
                "search_reward_authority": SEARCH_REWARD_AUTHORITY,
                "pair_reward": float(index % 7),
                "new_behavior_family_at_completion": index % 2 == 0,
                "candidate_id": candidate.candidate_id,
                "candidate_spec_json": json.dumps(candidate.to_dict(), sort_keys=True),
            }
        )
    policy.update(rows)
    assert policy.update_count == 1
    assert policy.tables["mechanism_family"]["G"]["observations"] > 0
    assert all(value >= 0.0 for value in policy.entropy_summary().values())
    restored = HierarchicalTypedCEMV2.from_state(registry, policy.export_state())
    assert restored.state_hash() == policy.state_hash()
    left, _ = policy.propose()
    right, _ = restored.propose()
    assert left.candidate_id == right.candidate_id


def test_typed_evolution_v2_receipts_cover_genes_skeleton_and_crossover() -> None:
    registry = _role_complete_registry()
    policy = TypedEvolutionV2(20260721, registry)
    first = generate_candidate(
        registry, skeleton=skeleton_registry()[0], rng=random.Random(101)
    )
    second = generate_candidate(
        registry, skeleton=skeleton_registry()[1], rng=random.Random(202)
    )
    mutated, mutation_receipt = policy._mutate_genes(first)
    assert policy.verify_receipt((first,), mutated, mutation_receipt)
    assert 1 <= len(mutation_receipt["changed_genes"]) <= 3
    remapped, skeleton_receipt = policy._mutate_skeleton(first)
    assert policy.verify_receipt((first,), remapped, skeleton_receipt)
    crossed, crossover_receipt = policy._crossover(first, second)
    assert policy.verify_receipt((first, second), crossed, crossover_receipt)
    assert crossover_receipt["gene_order"] == [
        "left_field",
        "right_field",
        "left_window",
        "right_window",
        "left_normalizer",
        "right_normalizer",
        "horizon_hours",
    ]


def test_v12_balanced_lane_choice_finishes_all_seed_lanes_together() -> None:
    lanes = [
        f"{arm}|{seed}"
        for arm in ("canonical_typed_random", "collision_controlled_evolution_v2_2")
        for seed in (20260716, 20260717, 20260718, 20260719)
    ]
    targets = {lane: 2 for lane in lanes}
    completed = {lane: 0 for lane in lanes}
    cursor = 0
    batches: list[list[str]] = []
    failed_once = False
    while any(completed[lane] < targets[lane] for lane in lanes):
        proposals: list[dict[str, str]] = []
        while len(proposals) < len(lanes):
            lane, cursor = _balanced_lane_choice(
                lane_order=lanes,
                lane_completed=completed,
                proposals=proposals,
                target_by_lane=targets,
                scheduler_cursor=cursor,
            )
            assert lane is not None
            if lane == lanes[0] and not failed_once:
                failed_once = True
                continue
            proposals.append({"policy_key": lane})
        batches.append([row["policy_key"] for row in proposals])
        cursor += 1
        for lane in batches[-1]:
            completed[lane] += 1
    assert len(batches) == 2
    assert all(set(batch) == set(lanes) for batch in batches)
    assert batches[0] != batches[1]
    assert completed == targets


def test_v22_collision_transition_memory_blocks_and_restores() -> None:
    registry = _role_complete_registry()
    parameters = {
        **V22_PARAMETERS["collision_controlled_evolution_v2_2"],
        "warmup": 1,
    }
    policy = TypedEvolutionV2(20260721, registry, parameters)
    parent = generate_candidate(
        registry, skeleton=skeleton_registry()[0], rng=random.Random(303)
    )
    policy.observe(
        parent,
        {
            "behavior_family_id": "PARENT_FAMILY",
            "search_reward": 0.0,
            "search_reward_authority": SEARCH_REWARD_AUTHORITY,
            "pair_reward": 0.0,
            "parent_ids": [],
            "operation": "TYPED_RANDOM_WARMUP",
            "new_policy_local_behavior_family_at_completion": True,
        },
    )
    archive = BehaviorArchive()
    child, receipt, transition_key = policy._mutate_skeleton_with_transition(
        parent,
        parent_behavior_family_id="PARENT_FAMILY",
        blocked_transition_keys=archive.blocked_transition_keys,
    )
    archive.observe_transition(
        transition_key=transition_key,
        new_family=False,
        block_after_collisions=1,
    )
    assert policy.verify_receipt((parent,), child, receipt)
    assert transition_key in archive.blocked_transition_keys
    assert archive.transition_productivity[transition_key] == {
        "trials": 1,
        "new_families": 0,
        "collisions": 1,
    }
    restored = TypedEvolutionV2.from_state(registry, policy.export_state())
    assert restored.state_hash() == policy.state_hash()
    restored_archive = BehaviorArchive()
    restored_archive.restore_transition_state(archive.transition_state())
    assert restored_archive.state_hash() == archive.state_hash()
    assert policy._skeleton_transition_key(
        parent_behavior_family_id="PARENT_FAMILY",
        source_skeleton_id=parent.skeleton_id,
        target_skeleton_id=child.skeleton_id,
        remapped_genome_sha256="A",
    ) != policy._skeleton_transition_key(
        parent_behavior_family_id="PARENT_FAMILY",
        source_skeleton_id=parent.skeleton_id,
        target_skeleton_id=child.skeleton_id,
        remapped_genome_sha256="B",
    )
    next_child, _, next_transition_key = restored._mutate_skeleton_with_transition(
        parent,
        parent_behavior_family_id="PARENT_FAMILY",
        blocked_transition_keys=restored_archive.blocked_transition_keys,
    )
    assert next_child.candidate_id != child.candidate_id
    assert next_transition_key != transition_key
    assert restored.blocked_transition_skips >= 1


def test_v22_blocked_transition_scans_remain_compile_valid() -> None:
    registry = _role_complete_registry()
    policy = TypedEvolutionV2(
        20260721,
        registry,
        V22_PARAMETERS["collision_controlled_evolution_v2_2"],
    )
    parent = generate_candidate(
        registry, skeleton=skeleton_registry()[0], rng=random.Random(404)
    )
    source = next(
        item
        for item in skeleton_registry()
        if item.skeleton_id == parent.skeleton_id
    )
    targets = [
        item
        for item in skeleton_registry()
        if item.mechanism_family == source.mechanism_family
        and item.skeleton_id != source.skeleton_id
        and item.field_roles == source.field_roles
    ]
    blocked = set()
    for target in targets:
        child = candidate_from_genes(
            registry,
            skeleton=target,
            genes=dict(parent.generation_genes),
        )
        blocked.add(
            policy._skeleton_transition_key(
                parent_behavior_family_id="PARENT_FAMILY",
                source_skeleton_id=source.skeleton_id,
                target_skeleton_id=target.skeleton_id,
                remapped_genome_sha256=_payload_sha(
                    child.generation_genes
                ),
            )
        )
    with pytest.raises(_ProposalGenerationFailure) as captured:
        policy._mutate_skeleton_with_transition(
            parent,
            parent_behavior_family_id="PARENT_FAMILY",
            blocked_transition_keys=blocked,
        )
    assert captured.value.raw_attempts == len(targets)
    assert captured.value.compile_valid_attempts == len(targets)


def test_behavior_archive_keeps_one_reward_champion_per_family() -> None:
    registry = _role_complete_registry()
    first = generate_candidate(
        registry, skeleton=skeleton_registry()[0], rng=random.Random(11)
    )
    second = generate_candidate(
        registry, skeleton=skeleton_registry()[0], rng=random.Random(12)
    )
    archive = BehaviorArchive()
    archive.observe(
        candidate=first,
        evaluation=_fake_search_evaluation(first, "FAMILY", -1.0),
        arm="canonical_typed_random",
        seed=1,
        completion_ordinal=1,
        checkpoint_index=0,
    )
    champion, new_family = archive.observe(
        candidate=second,
        evaluation=_fake_search_evaluation(second, "FAMILY", 0.5),
        arm="typed_evolution_v2",
        seed=1,
        completion_ordinal=2,
        checkpoint_index=0,
    )
    assert new_family is False
    assert champion["is_family_champion"] is True
    assert sum(bool(row["is_family_champion"]) for row in archive.rows) == 1
    assert archive.summary_rows()[0]["champion_exact_expression_id"] == second.candidate_id
    assert archive.duplicate_replacements == 1


def test_search_checkpoint_is_atomic_and_restores_policy_archive_and_rng(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry = _role_complete_registry()
    candidate = generate_candidate(
        registry, skeleton=skeleton_registry()[0], rng=random.Random(41)
    )
    archive = BehaviorArchive()
    archive.observe(
        candidate=candidate,
        evaluation=_fake_search_evaluation(candidate, "FAMILY", 0.25),
        arm="canonical_typed_random",
        seed=20260716,
        completion_ordinal=1,
        checkpoint_index=0,
    )
    policy = HierarchicalTypedCEMV2(20260716, registry)
    policy.propose()
    state = _new_campaign_state("a" * 40, "B" * 64)
    state["attempted_exact_ids"] = [candidate.candidate_id]
    identities = {
        "raw_cache": {"identity_sha256": "C" * 64},
        "compiler_identity": {"bundle_sha256": "D" * 64},
    }
    real_replace = os.replace
    replace_observations: list[bool] = []

    def checked_replace(source: str | Path, target: str | Path) -> None:
        if Path(source).is_dir():
            manifest = json.loads((Path(source) / "manifest.json").read_text())
            replace_observations.append(bool(manifest["restore_verified"]))
        real_replace(source, target)

    monkeypatch.setattr(
        "alphafactory_crypto.broad_search.search_engine_v1.os.replace",
        checked_replace,
    )
    checkpoint = _write_checkpoint(
        runtime_root=tmp_path,
        label="checkpoint_000",
        checkpoint_index=0,
        registry=registry,
        state=state,
        policies={"hierarchical_typed_cem_v2|20260716": policy},
        ledger=[{"candidate_id": candidate.candidate_id, "receipt_json": None}],
        archive=archive,
        metrics=[{"checkpoint_index": 0, "arm": "__campaign__"}],
        identities=identities,
    )
    assert checkpoint.is_dir()
    assert replace_observations == [True]
    assert json.loads((checkpoint / "manifest.json").read_text())[
        "restore_verified"
    ] is True
    assert not list((tmp_path / "checkpoints").glob(".checkpoint_000.tmp-*"))
    restored_state, restored_policies, ledger, restored_archive, _ = _load_checkpoint(
        checkpoint_path=checkpoint,
        registry=registry,
        expected_source_sha="a" * 40,
        expected_frozen_hash="B" * 64,
        expected_identities=identities,
    )
    assert restored_state["attempted_exact_ids"] == [candidate.candidate_id]
    assert ledger[0]["candidate_id"] == candidate.candidate_id
    assert restored_archive.state_hash() == archive.state_hash()
    restored_policy = restored_policies["hierarchical_typed_cem_v2|20260716"]
    assert restored_policy.state_hash() == policy.state_hash()
    assert _checkpoint_allocation(0, state["arm_states"]) == {
        arm: 400
        for arm in (
            "canonical_typed_random",
            "cem_distribution_v1",
            "evolutionary_typed_v1",
            "hierarchical_typed_cem_v2",
            "typed_evolution_v2",
        )
    }


def test_metrics_use_valid_exact_unique_counter_for_cpu_density() -> None:
    state = _new_campaign_state("a" * 40, "B" * 64)
    state["exact_unique"] = 9
    state["arm_counters"]["canonical_typed_random"]["exact_unique"] = 9
    state["arm_counters"]["canonical_typed_random"]["cpu_seconds"] = 3600.0
    ledger = [
        {
            "arm": "canonical_typed_random",
            "checkpoint_index": 0,
            "behavior_family_id": "FAMILY",
            "search_reward": -1.0,
            "pair_reward": -1.0,
            "candidate_id": "CANDIDATE",
            "matched_positive": False,
            "new_behavior_family_at_completion": True,
            "operation": "CANONICAL_TYPED_RANDOM_SAMPLE",
            "receipt_verified": None,
            "cost_killed": False,
            "turnover_killed": False,
            "arm_completion_ordinal": 1,
        }
    ]
    rows = _metrics_rows(
        checkpoint_index=0,
        ledger=ledger,
        archive=BehaviorArchive(),
        state=state,
        policies={},
    )
    random_arm = next(
        row for row in rows if row["arm"] == "canonical_typed_random"
    )
    campaign = next(row for row in rows if row["arm"] == "__campaign__")
    assert random_arm["valid_exact_unique_per_cpu_hour"] == pytest.approx(9.0)
    assert campaign["valid_exact_unique_per_cpu_hour"] == pytest.approx(9.0)
