from __future__ import annotations

import json
import random
from pathlib import Path

import numpy as np
import pytest

from alphafactory_crypto.broad_search.compositional18m import (
    CandidateSpec,
    generate_candidate,
    skeleton_registry,
)
from alphafactory_crypto.broad_search.expression import (
    Expression,
    FieldContract,
    TypedExpressionRegistry,
    ablate_expression,
    materialize_expression,
)
from alphafactory_crypto.broad_search.pair18m import (
    evaluate_pair,
    feedback_contract_payload,
)
from alphafactory_crypto.broad_search.runner18m import LanePolicy
from alphafactory_crypto.instrument_capability.mapping import CROSS_SECTIONAL_ZERO_NET


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


def test_report_only_metrics_are_not_policy_feedback() -> None:
    contract = feedback_contract_payload()
    assert contract["report_only_metrics_visible_to_policy"] is False
    assert contract["authoritative_feedback"].startswith("incremental sleeve")


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


def test_frozen_config_keeps_sealed_reads_and_promotion_disabled() -> None:
    config = json.loads(
        (Path(__file__).parents[1] / "config" / "crypto_18m_compositional_broad_search_v1.json").read_text()
    )
    assert config["boundaries"]["sealed_reads_allowed"] is False
    assert config["boundaries"]["candidate_promotion"] is False
    assert config["boundaries"]["formal_performance_search"] is False
    assert config["budget"]["stage_a_pairs"] == 4096
