from __future__ import annotations

import ast
from pathlib import Path

import numpy as np
import pytest

from alphafactory_crypto.broad_search.audit import (
    freeze_search_behavior_contract,
    search_behavior_descriptor,
    turnover_path,
)
from alphafactory_crypto.broad_search.compositional18m import CandidateSpec
from alphafactory_crypto.broad_search.expression import (
    Expression,
    FieldContract,
    TypedExpressionRegistry,
    ablate_expression,
    materialize_expression,
)
from alphafactory_crypto.broad_search.pair18m import (
    ControlBehaviorDegeneracyError,
    FIXED_COST_BPS,
    SEARCH_REWARD_AUTHORITY,
    SEARCH_REWARD_COMPONENT_AUTHORITY,
    SEARCH_REWARD_UNCERTAINTY_CONTRACT,
    _stationary_bootstrap_indices,
    pair_contract_payload,
    _series_metrics,
    control_degeneracy_provenance,
    evaluate_pair,
)
from alphafactory_crypto.instrument_capability.mapping import (
    CROSS_SECTIONAL_ZERO_NET,
    DEFAULT_MAPPING_CONTRACTS,
    map_portfolio,
)


def _active_universe(asset_count: int, hour_count: int) -> np.ndarray:
    return np.full((asset_count, hour_count), float(asset_count), dtype=float)


def test_four_hour_behavior_uses_t_minus_four_not_t_minus_one() -> None:
    weights = np.asarray(
        [[0.0, 1.0, 0.0, 0.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]
    )

    path, attribution = turnover_path(weights, 4)

    assert path[5] == pytest.approx(0.5)
    assert path[6] == pytest.approx(0.0)
    assert attribution["entry_l1"] == pytest.approx(0.5)
    assert attribution["transition_exit_l1"] == pytest.approx(0.5)
    assert attribution["total_turnover_l1"] == pytest.approx(float(path.sum()))


def test_control_degeneracy_provenance_finds_rank_as_first_equal_stage() -> None:
    primary_signal = np.tile(
        np.asarray([[-1.0], [0.0], [1.0], [2.0]], dtype=float),
        (1, 48),
    )
    control_signal = primary_signal + 20.0
    mapping = DEFAULT_MAPPING_CONTRACTS[CROSS_SECTIONAL_ZERO_NET]
    primary = map_portfolio(
        primary_signal,
        mapping,
        include_behavior_provenance=True,
    )
    control = map_portfolio(
        control_signal,
        mapping,
        include_behavior_provenance=True,
    )
    timestamps = np.arange(48, dtype=np.int64) * 3_600_000_000_000

    provenance = control_degeneracy_provenance(
        primary_signal=primary_signal,
        control_signal=control_signal,
        primary_mapping=primary,
        control_mapping=control,
        timestamp_ns=timestamps,
        primary_label="primary",
        control_label="left_control",
    )

    assert provenance["final_weight_equal"] is True
    assert provenance["first_equal_stage"] == "RANK"
    assert provenance["stages"]["SIGNAL"]["equal"] is False
    assert provenance["stages"]["RANK"]["equal"] is True
    assert provenance["rank_comparison"]["mean_spearman"] == pytest.approx(1.0)
    assert provenance["rank_comparison"]["top_bucket_overlap_mean"] == pytest.approx(1.0)
    assert provenance["rank_comparison"]["bottom_bucket_overlap_mean"] == pytest.approx(1.0)
    assert "target_ic" in provenance["identity_excludes"]
    assert len(provenance["provenance_sha256"]) == 64


def test_control_degeneracy_does_not_mislabel_feasibility_suppression_as_cap() -> None:
    primary_signal = np.asarray([[0.0], [1.0]])
    control_signal = np.asarray([[1.0], [0.0]])
    mapping = DEFAULT_MAPPING_CONTRACTS[CROSS_SECTIONAL_ZERO_NET]
    primary = map_portfolio(
        primary_signal,
        mapping,
        include_behavior_provenance=True,
    )
    control = map_portfolio(
        control_signal,
        mapping,
        include_behavior_provenance=True,
    )

    provenance = control_degeneracy_provenance(
        primary_signal=primary_signal,
        control_signal=control_signal,
        primary_mapping=primary,
        control_mapping=control,
        timestamp_ns=np.asarray([0], dtype=np.int64),
        primary_label="primary",
        control_label="left_control",
    )

    assert provenance["stages"]["CAPPED_WEIGHT"]["equal"] is False
    assert provenance["stages"]["MAPPED_WEIGHT"]["equal"] is True
    assert provenance["first_equal_stage"] == "MAPPED_WEIGHT"


def test_control_behavior_degeneracy_error_preserves_kill_line_and_provenance() -> None:
    failure = ControlBehaviorDegeneracyError(
        "CONTROL_BEHAVIOR_EQUALS_PRIMARY",
        {
            "schema_version": "CRYPTO_CONTROL_DEGENERACY_PROVENANCE_V1",
            "first_equal_stage": "MAPPED_WEIGHT",
            "provenance_sha256": "A" * 64,
        },
    )

    assert isinstance(failure, ValueError)
    assert str(failure) == "CONTROL_BEHAVIOR_EQUALS_PRIMARY"
    assert failure.provenance["first_equal_stage"] == "MAPPED_WEIGHT"


def test_behavior_turnover_exactly_matches_evaluator_turnover() -> None:
    weights = np.asarray(
        [
            [0.0, 0.4, 0.0, 0.0, 0.2, -0.3, 0.0, 0.0, 0.1, 0.0, 0.0, 0.0],
            [0.0, -0.4, 0.0, 0.0, -0.2, 0.3, 0.0, 0.0, -0.1, 0.0, 0.0, 0.0],
        ],
        dtype=float,
    )
    signal = weights.copy()
    eligible = np.ones_like(weights, dtype=bool)
    months = np.asarray(["2023-07"] * weights.shape[1])
    active_universe = _active_universe(*weights.shape)
    contract = freeze_search_behavior_contract(active_universe, eligible)

    descriptor = search_behavior_descriptor(
        signal=signal,
        weights=weights,
        eligible_mask=eligible,
        month_labels=months,
        timestamp_ns=np.arange(weights.shape[1], dtype=np.int64),
        active_universe_size=active_universe,
        horizon_hours=4,
        mapping_id=CROSS_SECTIONAL_ZERO_NET,
        contract=contract,
    )
    metrics = _series_metrics(
        weights=weights,
        target=np.zeros_like(weights),
        months=months,
        evaluation_mask=np.ones(weights.shape[1], dtype=bool),
        horizon=4,
    )
    path, attribution = turnover_path(weights, 4)

    assert descriptor["turnover_path_sha256"] == metrics["turnover_path_sha256"]
    assert metrics["total_turnover_l1"] == pytest.approx(float(path.sum()))
    assert metrics["total_turnover_l1"] == pytest.approx(
        attribution["total_turnover_l1"]
    )


def test_train_portfolio_search_reward_is_deterministic_and_cost_consistent() -> None:
    hour_count = 72
    weights = np.vstack(
        (
            np.full(hour_count, 0.5, dtype=float),
            np.full(hour_count, -0.5, dtype=float),
        )
    )
    alpha = np.concatenate(
        (
            np.full(24, 0.0010),
            np.full(24, -0.0005),
            np.full(24, 0.0010),
        )
    )
    target = np.vstack((alpha, -alpha))
    months = np.asarray(["2023-07"] * hour_count)
    timestamps = (
        np.datetime64("2023-07-01T00:00:00", "ns").astype(np.int64)
        + np.arange(hour_count, dtype=np.int64) * 3_600_000_000_000
    )
    kwargs = {
        "weights": weights,
        "target": target,
        "months": months,
        "evaluation_mask": np.ones(hour_count, dtype=bool),
        "horizon": 1,
        "timestamp_ns": timestamps,
        "search_reward_seed": 20260729,
    }

    first = _series_metrics(**kwargs)
    second = _series_metrics(**kwargs)
    objective = first["portfolio_search_objective"]

    assert first["portfolio_search_objective"] == second[
        "portfolio_search_objective"
    ]
    assert objective["authority"] == SEARCH_REWARD_COMPONENT_AUTHORITY
    assert objective["uncertainty_contract"] == SEARCH_REWARD_UNCERTAINTY_CONTRACT
    assert objective["train_day_count"] == 3
    assert objective["train_day_bootstrap_draws"] > 0
    assert objective["train_day_bootstrap_requested_draws"] == 600
    assert objective["train_day_bootstrap_expected_block_length"] == 2
    assert objective["train_worst_horizon_day_sortino"] is None
    assert objective["worst_horizon_term_removed"] is True
    assert objective["mean_one_way_turnover"] == pytest.approx(
        0.5 * objective["mean_full_l1_turnover"]
    )
    assert first["cost_mean"] == pytest.approx(
        objective["mean_full_l1_turnover"] * FIXED_COST_BPS / 10_000.0
    )
    assert first["cost_mean"] == pytest.approx(
        2.0
        * objective["mean_one_way_turnover"]
        * FIXED_COST_BPS
        / 10_000.0
    )


def test_stationary_bootstrap_is_deterministic_and_order_aware() -> None:
    first, first_meta = _stationary_bootstrap_indices(
        16, seed=20260730, draws=64
    )
    second, second_meta = _stationary_bootstrap_indices(
        16, seed=20260730, draws=64
    )

    assert np.array_equal(first, second)
    assert first_meta == second_meta
    assert first_meta["contract"] == SEARCH_REWARD_UNCERTAINTY_CONTRACT
    assert first_meta["method"] == "STATIONARY_BOOTSTRAP"
    assert first_meta["expected_block_length"] >= 2
    continued = first[:, 1:] == (first[:, :-1] + 1) % 16
    assert bool(np.any(continued))
    assert bool(np.any(~continued))


def test_pair_contract_is_crypto_only_and_has_joint_matched_reward() -> None:
    contract = pair_contract_payload()

    assert contract["schema_version"] == 5
    assert contract["market_semantics"]["asset_class"] == "CRYPTO"
    assert contract["market_semantics"]["calendar"] == "CONTINUOUS_UTC"
    assert contract["market_semantics"]["a_share_constraints_applied"] is False
    objective = contract["search_objective"]
    assert objective["authority"] == SEARCH_REWARD_AUTHORITY
    assert objective["uncertainty_contract"] == SEARCH_REWARD_UNCERTAINTY_CONTRACT
    assert "matched incremental" in objective["portfolio"]
    assert "counted twice" in objective["selected_horizon_scope"]


def test_active_crypto_economic_chain_has_no_cn_runtime_imports() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    active_paths = (
        "alphafactory_crypto/broad_search/pair18m.py",
        "alphafactory_crypto/broad_search/search_engine_v1.py",
        "alphafactory_crypto/broad_search/experiment_authority.py",
        "alphafactory_crypto/instrument_capability/mapping.py",
    )
    forbidden_prefixes = (
        "our_system_phase2",
        "alpha_pit_true1min",
        "a_share",
    )
    imported: list[str] = []
    for relative in active_paths:
        tree = ast.parse((repo_root / relative).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.append(node.module)
    assert not [
        name
        for name in imported
        if name.startswith(forbidden_prefixes)
    ]


class _BehaviorStore:
    def __init__(self) -> None:
        self.shape = (3, 12)
        hours = np.arange(self.shape[1], dtype=float)
        self._fields = {
            "a": np.vstack((hours + 1.0, 13.0 - hours, 2.0 + (hours % 3.0))),
            "b": np.vstack(
                (
                    np.where(hours % 2.0 == 0.0, 2.0, -1.0),
                    np.where(hours % 3.0 == 0.0, -2.0, 1.5),
                    np.where(hours % 4.0 < 2.0, 0.5, -2.5),
                )
            ),
            "active_universe_size": _active_universe(*self.shape),
        }
        self._eligible = np.ones(self.shape, dtype=bool)
        self._target = np.zeros(self.shape, dtype=float)
        start = np.datetime64("2023-07-01T00:00:00", "ns").astype(np.int64)
        self.timestamp_ns = (
            start
            + np.arange(self.shape[1], dtype=np.int64) * 3_600_000_000_000
        )

    def field(self, name: str) -> np.ndarray:
        return self._fields[name]

    def base_eligible(self) -> np.ndarray:
        return self._eligible

    def target_return(self, horizon: int) -> np.ndarray:
        assert horizon == 1
        return self._target

    def block_slice(self, start: str, end: str) -> slice:
        return slice(0, self.shape[1])


def test_behavior_family_uses_incremental_delta_weights() -> None:
    store = _BehaviorStore()
    registry = TypedExpressionRegistry(
        (
            FieldContract("a", "RATIO", "dimensionless"),
            FieldContract("b", "RATIO", "dimensionless"),
        )
    )
    primary_expression = Expression(
        "RatioInteraction", (Expression.raw("a"), Expression.raw("b"))
    )
    control_expression = ablate_expression(primary_expression)
    assurance = registry.validate(primary_expression)
    candidate = CandidateSpec(
        "candidate",
        "skeleton",
        "OI_ACTIVITY_INTERACTION",
        primary_expression,
        control_expression,
        1,
        CROSS_SECTIONAL_ZERO_NET,
        assurance.raw_fields,
        ("family_a", "family_b"),
        assurance.rolling_windows,
        assurance.depth,
        "RatioInteraction(Raw,Raw)",
    )
    active_universe = store.field("active_universe_size")
    contract = freeze_search_behavior_contract(
        active_universe, store.base_eligible()
    )
    result = evaluate_pair(
        store=store,
        registry=registry,
        candidate=candidate,
        block_start="2023-07-01T00:00:00Z",
        block_end="2023-07-01T12:00:00Z",
        block_role="DEVELOPMENT_ADAPTIVE_FEEDBACK",
        behavior_contract=contract,
        include_control_provenance=True,
    )

    provenance = result["control_degeneracy_provenance"]
    assert provenance["schema_version"] == "CRYPTO_PAIR_CONTROL_PROVENANCE_V1"
    assert set(provenance["comparisons"]) == {
        "primary_vs_left_control",
        "primary_vs_right_control",
    }
    assert all(
        comparison["final_weight_equal"] is False
        and comparison["first_equal_stage"] is None
        for comparison in provenance["comparisons"].values()
    )
    assert "target_ic" in provenance["identity_excludes"]

    raw = {"a": store.field("a"), "b": store.field("b")}
    primary_signal = materialize_expression(
        primary_expression,
        registry=registry,
        field_reader=raw.__getitem__,
        eligible_mask=store.base_eligible(),
    )
    control_signal = materialize_expression(
        control_expression,
        registry=registry,
        field_reader=raw.__getitem__,
        eligible_mask=store.base_eligible(),
    )
    mapping = DEFAULT_MAPPING_CONTRACTS[CROSS_SECTIONAL_ZERO_NET]
    primary_weight = np.asarray(map_portfolio(primary_signal, mapping).weights)
    control_weight = np.asarray(map_portfolio(control_signal, mapping).weights)
    descriptor_kwargs = {
        "eligible_mask": store.base_eligible(),
        "month_labels": np.asarray(["2023-07"] * store.shape[1]),
        "timestamp_ns": store.timestamp_ns,
        "active_universe_size": active_universe,
        "horizon_hours": 1,
        "mapping_id": CROSS_SECTIONAL_ZERO_NET,
        "contract": contract,
    }
    primary_behavior = search_behavior_descriptor(
        signal=primary_signal,
        weights=primary_weight,
        **descriptor_kwargs,
    )
    control_behavior = search_behavior_descriptor(
        signal=control_signal,
        weights=control_weight,
        **descriptor_kwargs,
    )
    incremental_behavior = search_behavior_descriptor(
        signal=primary_signal - control_signal,
        weights=primary_weight - control_weight,
        **descriptor_kwargs,
    )

    behavior = result["behavior"]
    objective = result["search_reward_feedback"]
    assert objective["authority"] == SEARCH_REWARD_AUTHORITY
    assert objective["uncertainty_contract"] == SEARCH_REWARD_UNCERTAINTY_CONTRACT
    assert objective["joint_rule"] == "MIN_PRIMARY_AND_ALL_REQUIRED_MATCHED_COMPONENTS"
    assert objective["component_order"] == [
        "primary",
        "primary_minus_left_control",
        "primary_minus_right_control",
    ]
    assert objective["search_reward"] == min(
        component["search_reward"]
        for component in objective["component_objectives"].values()
    )
    assert result["search_reward"] == objective["search_reward"]
    assert behavior["primary_behavior_id"] == primary_behavior["behavior_family_id"]
    assert behavior["control_behavior_id"] == control_behavior["behavior_family_id"]
    assert (
        behavior["incremental_behavior_id"]
        == incremental_behavior["behavior_family_id"]
    )
    assert behavior["behavior_family_id"] == behavior["incremental_behavior_id"]
    assert (
        behavior["mapped_weight_descriptor_id"]
        == incremental_behavior["mapped_weight_descriptor_id"]
    )
    assert (
        behavior["turnover_path_descriptor_id"]
        == incremental_behavior["turnover_path_descriptor_id"]
    )
    assert behavior["identity_excludes"] == [
        "gross",
        "net",
        "cost",
        "search_reward",
        "pair_reward",
    ]


def test_behavior_contract_rejects_self_proving_partial_active_support() -> None:
    observed_support = np.ones((3, 4), dtype=bool)
    active_universe = np.asarray(
        [
            [2.0, 2.0, 2.0, 2.0],
            [2.0, 2.0, 2.0, 2.0],
            [np.nan, np.nan, np.nan, np.nan],
        ]
    )

    with pytest.raises(ValueError, match="must exactly match observed_support"):
        freeze_search_behavior_contract(active_universe, observed_support)


def test_behavior_contract_rejects_stale_active_values_outside_observed_support() -> None:
    observed_support = np.asarray(
        [
            [True, True, True, True],
            [True, True, True, True],
            [False, False, False, False],
        ]
    )
    active_universe = np.full((3, 4), 2.0, dtype=float)

    with pytest.raises(ValueError, match="must exactly match observed_support"):
        freeze_search_behavior_contract(active_universe, observed_support)
