from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from alphafactory_crypto.broad_search import pair18m
from alphafactory_crypto.broad_search.compositional18m import CandidateSpec
from alphafactory_crypto.broad_search.expression import Expression
from alphafactory_crypto.broad_search.pair18m import _development_block_robust_ordering
from alphafactory_crypto.broad_search.search_engine_v1 import MechanismEvolutionV2


ROOT = Path(__file__).resolve().parents[1]
V1 = json.loads(
    (ROOT / "config/crypto_search_replication_aware_gate_v1.json").read_text(
        encoding="utf-8"
    )
)["block_robust_contract"]
V2 = json.loads(
    (ROOT / "config/crypto_p1_g2_block_robust_ordering_v2.json").read_text(
        encoding="utf-8"
    )
)
TIMESTAMPS = pd.date_range(
    "2025-08-29T07:00:00Z",
    "2025-11-01T00:00:00Z",
    freq="h",
    inclusive="left",
).asi8


def _candidate(*, hierarchical: bool) -> CandidateSpec:
    expression = Expression.raw("synthetic")
    return CandidateSpec(
        "p1-g2-hierarchical" if hierarchical else "binary-regression",
        "synthetic",
        "CONDITIONAL_V2_P1" if hierarchical else "OI_ACTIVITY_INTERACTION",
        expression,
        expression,
        4,
        "CROSS_SECTIONAL_ZERO_NET",
        ("synthetic",),
        ("synthetic",),
        (),
        1,
        "Raw",
        (
            {"matched_control_schema": "HIERARCHICAL_A_B_AB_ABC", "semantic_generation": 2}
            if hierarchical
            else {}
        ),
    )


def _arguments(candidate: CandidateSpec, contract: dict[str, object]) -> dict[str, object]:
    hours = len(TIMESTAMPS)
    return {
        "candidate": candidate,
        "primary_weight": np.repeat(np.array([[0.5], [-0.5]]), hours, axis=1),
        "left_delta_weight": np.repeat(np.array([[0.2], [-0.2]]), hours, axis=1),
        "right_delta_weight": np.repeat(np.array([[0.3], [-0.3]]), hours, axis=1),
        "target": np.repeat(np.array([[0.001], [-0.001]]), hours, axis=1),
        "evaluation_mask": np.ones(hours, dtype=bool),
        "timestamp_ns": TIMESTAMPS,
        "cost_bps": 5.0,
        "full_block_start": "2025-08-29T07:00:00Z",
        "full_block_end": "2025-11-01T00:00:00Z",
        "contract": contract,
        "economic_receipt": {"execution": {"partition_tail_purge_hours": 6}},
    }


def test_v1_binary_is_unchanged_and_v2_binary_is_numerically_identical() -> None:
    candidate = _candidate(hierarchical=False)
    v1 = _development_block_robust_ordering(**_arguments(candidate, V1))
    v2 = _development_block_robust_ordering(**_arguments(candidate, V2))
    aggregate = (
        "replicated_positive_block_count",
        "replicated_candidate",
        "all_three_blocks_positive",
        "worst_block_min_matched_net_mean",
        "median_block_joint_search_reward",
        "max_required_mean_one_way_turnover",
        "min_required_support",
    )
    per_block = (
        "primary_gross_mean",
        "primary_net_mean",
        "left_gross_mean",
        "left_net_mean",
        "right_gross_mean",
        "right_net_mean",
        "both_matched_net_positive",
        "min_matched_net_mean",
        "joint_search_reward",
        "max_required_mean_one_way_turnover",
        "min_required_support",
    )
    assert {name: v2[name] for name in aggregate} == {
        name: v1[name] for name in aggregate
    }
    assert [
        {name: row[name] for name in per_block} for row in v2["blocks"]
    ] == [{name: row[name] for name in per_block} for row in v1["blocks"]]
    assert v1 == _development_block_robust_ordering(**_arguments(candidate, V1))
    assert v2["required_matched_components"] == [
        "primary_minus_left_control",
        "primary_minus_right_control",
    ]


def _block_values(values: tuple[float, float, float]) -> np.ndarray:
    result = np.zeros((1, len(TIMESTAMPS)), dtype=float)
    for value, block in zip(values, V2["blocks"], strict=True):
        start = pd.Timestamp(block["start"]).value
        stop = pd.Timestamp(block["end_exclusive"]).value
        result[:, (TIMESTAMPS >= start) & (TIMESTAMPS < stop)] = value
    return result


def test_hierarchical_v2_uses_all_exact_sleeves_and_replication_rules(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen_components: list[tuple[str, ...]] = []

    def fake_series_metrics(*, weights: np.ndarray, **_: object) -> dict[str, object]:
        value = float(np.mean(weights))
        support = 100.0 - abs(value) * 10.0
        return {
            "gross_mean": value,
            "net_mean": value,
            "support": support,
            "_objective_net_path": np.full(weights.shape[1], value),
            "_objective_turnover_path": np.full(weights.shape[1], abs(value)),
            "_objective_mask": np.ones(weights.shape[1], dtype=bool),
        }

    def fake_joint(*, components: dict[str, dict[str, np.ndarray]], **_: object) -> dict[str, object]:
        seen_components.append(tuple(components))
        return {
            "search_reward": sum(float(np.mean(value["net"])) for value in components.values()),
            "component_objectives": {
                name: {"mean_one_way_turnover": abs(float(np.mean(value["net"])))}
                for name, value in components.items()
            },
        }

    monkeypatch.setattr(pair18m, "_series_metrics", fake_series_metrics)
    monkeypatch.setattr(pair18m, "_joint_portfolio_search_reward", fake_joint)
    arguments = _arguments(_candidate(hierarchical=True), V2)
    arguments["primary_weight"] = _block_values((0.5, 0.5, 0.5))
    arguments["matched_component_weights"] = {
        "interaction_ab_minus_a": _block_values((1.0, 1.0, 1.0)),
        "interaction_ab_minus_b": _block_values((2.0, 2.0, 2.0)),
        "conditional_abc_minus_ab": _block_values((3.0, 3.0, -3.0)),
    }
    result = _development_block_robust_ordering(**arguments)

    expected = (
        "primary",
        "interaction_ab_minus_a",
        "interaction_ab_minus_b",
        "conditional_abc_minus_ab",
    )
    assert seen_components == [expected, expected, expected]
    assert result["required_matched_components"] == list(expected[1:])
    assert [row["all_required_matched_net_positive"] for row in result["blocks"]] == [
        True,
        True,
        False,
    ]
    assert result["blocks"][2]["conditional_abc_minus_ab_net_mean"] == -3.0
    assert result["replicated_positive_block_count"] == 2
    assert result["replicated_candidate"] is True
    assert result["all_three_blocks_positive"] is False
    assert result["worst_block_min_matched_net_mean"] == -3.0
    assert result["max_required_mean_one_way_turnover"] == 3.0
    assert result["min_required_support"] == 70.0

    arguments["matched_component_weights"] = {
        **arguments["matched_component_weights"],
        "conditional_abc_minus_ab": _block_values((3.0, 3.0, 3.0)),
    }
    all_positive = _development_block_robust_ordering(**arguments)
    assert all_positive["replicated_positive_block_count"] == 3
    assert all_positive["all_three_blocks_positive"] is True


def test_hierarchical_p1_g2_passes_v2_but_remains_rejected_by_v1() -> None:
    candidate = _candidate(hierarchical=True)
    arguments = _arguments(candidate, V2)
    arguments["matched_component_weights"] = {
        "interaction_ab_minus_a": arguments["left_delta_weight"],
        "interaction_ab_minus_b": arguments["right_delta_weight"],
        "conditional_abc_minus_ab": arguments["left_delta_weight"],
    }
    result = _development_block_robust_ordering(**arguments)
    assert result["authority"] == "DEVELOPMENT_THREE_BLOCK_ROBUST_ORDERING_V2"
    assert result["mechanism_shape"] == "HIERARCHICAL_THREE_AXIS"
    with pytest.raises(ValueError, match="BLOCK_ROBUST_ORDERING_REQUIRES_BINARY_MECHANISM"):
        _development_block_robust_ordering(**_arguments(candidate, V1))


def test_evolution_v2_selection_authority_uses_unchanged_lexicographic_order() -> None:
    policy = object.__new__(MechanismEvolutionV2)
    policy.parameters = {
        "selection_authority": "DEVELOPMENT_THREE_BLOCK_ROBUST_ORDERING_V2"
    }

    def record(replicated: int, reward: float) -> dict[str, object]:
        return {
            "search_reward": reward,
            "block_robust_ordering": {
                "authority": "DEVELOPMENT_THREE_BLOCK_ROBUST_ORDERING_V2",
                "replicated_positive_block_count": replicated,
                "worst_block_min_matched_net_mean": -1.0,
                "median_block_joint_search_reward": -1.0,
                "max_required_mean_one_way_turnover": 1.0,
                "min_required_support": 10.0,
            },
        }

    assert policy._selection_key(
        "replicated", record(2, -10.0), include_family_count=False
    ) < policy._selection_key("reward", record(1, 10.0), include_family_count=False)
    with pytest.raises(ValueError, match="block-robust Evolution observation is unbound"):
        policy._selection_key(
            "legacy",
            {
                **record(3, 1.0),
                "block_robust_ordering": {
                    **record(3, 1.0)["block_robust_ordering"],
                    "authority": "DEVELOPMENT_THREE_BLOCK_ROBUST_ORDERING_V1",
                },
            },
            include_family_count=False,
        )


def test_v2_contract_preserves_frozen_development_boundaries() -> None:
    assert V2["blocks"] == V1["blocks"]
    assert V2["partition_tail_purge_hours"] == V1["partition_tail_purge_hours"] == 6
    assert V2["feature_warmup"] == V1["feature_warmup"]
    assert V2["position_boundary"] == V1["position_boundary"]
    assert V2["required_matched_component_rule"] == (
        "ALL_REQUIRED_MATCHED_COMPONENTS_PER_BLOCK"
    )
