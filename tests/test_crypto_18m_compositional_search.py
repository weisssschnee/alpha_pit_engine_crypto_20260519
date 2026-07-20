from __future__ import annotations

import json
import random
from copy import deepcopy
from pathlib import Path

import numpy as np
import pytest

from alphafactory_crypto.broad_search.compositional18m import (
    CandidateSpec,
    candidate_from_genes,
    field_role_coverage,
    generate_candidate,
    skeleton_registry,
    typed_mutate_candidate,
    verify_typed_mutation_receipt,
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
from alphafactory_crypto.broad_search.runner18m import (
    LanePolicy,
    _current_field_surface_binding,
    _directory_bundle,
    _policy_audit,
    _validate_config,
)
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
