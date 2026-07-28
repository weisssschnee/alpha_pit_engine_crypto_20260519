from __future__ import annotations

import json

import pandas as pd

from alphafactory_crypto.broad_search.failure_decomposition_v14 import (
    _augment_ledger,
    _constraint_bottleneck_rows,
    _decision_rows,
    _economic_waterfall_rows,
)


def _candidate_spec(*, hierarchical: bool, horizon: int = 4) -> str:
    fields = (
        [
            "bybit__open_interest_last",
            "signed_aggressor_notional",
            "bybit__funding_rate_last",
        ]
        if hierarchical
        else ["bybit__open_interest_last", "signed_aggressor_notional"]
    )
    genes = {
        "left_field": fields[0],
        "right_field": fields[1],
        "left_window": 24,
        "right_window": 48,
        "left_normalizer": "RollingZScore",
        "right_normalizer": "HistoricalPercentile",
        "horizon_hours": horizon,
    }
    if hierarchical:
        genes.update(
            {
                "condition_field": fields[2],
                "condition_window": 168,
                "condition_normalizer": "VolatilityScale",
                "semantic_tuple": (
                    "CROSS_VENUE_OI_X_FLOW_IMBALANCE_GIVEN_FUNDING"
                ),
            }
        )
    return json.dumps(
        {
            "horizon_hours": horizon,
            "generation_genes": genes,
        }
    )


def _frames() -> tuple[pd.DataFrame, pd.DataFrame]:
    ledger = pd.DataFrame(
        [
            {
                "candidate_id": "H1",
                "stage": "STAGE_B",
                "checkpoint_index": 0,
                "pair_reward": -0.5,
                "hierarchical_three_axis": True,
                "candidate_spec_json": _candidate_spec(hierarchical=True),
                "semantic_tuple": (
                    "CROSS_VENUE_OI_X_FLOW_IMBALANCE_GIVEN_FUNDING"
                ),
                "raw_fields_json": json.dumps(
                    [
                        "bybit__open_interest_last",
                        "signed_aggressor_notional",
                        "bybit__funding_rate_last",
                    ]
                ),
                "net_mean": -0.0001,
                "cost_mean": 0.0002,
                "turnover_mean": 0.4,
                "support": 0.9,
                "interaction_left_distance": -0.5,
                "interaction_right_distance": -0.2,
                "conditional_distance": -0.1,
            },
            {
                "candidate_id": "B1",
                "stage": "STAGE_B",
                "checkpoint_index": 0,
                "pair_reward": -2.0,
                "hierarchical_three_axis": False,
                "candidate_spec_json": _candidate_spec(hierarchical=False),
                "semantic_tuple": None,
                "raw_fields_json": json.dumps(
                    [
                        "bybit__open_interest_last",
                        "signed_aggressor_notional",
                    ]
                ),
                "net_mean": -0.0001,
                "cost_mean": 0.0002,
                "turnover_mean": 0.4,
                "support": 0.9,
                "interaction_left_distance": None,
                "interaction_right_distance": None,
                "conditional_distance": None,
            },
        ]
    )
    archive = pd.DataFrame(
        [
            {
                "exact_expression_id": "H1",
                "gross_mean_annotation": 0.0001,
            },
            {
                "exact_expression_id": "B1",
                "gross_mean_annotation": 0.0001,
            },
        ]
    )
    return ledger, archive


def test_decomposition_marks_unpersisted_waterfall_without_fabrication() -> None:
    ledger, archive = _frames()
    frame = _augment_ledger(ledger, archive)
    constraint = pd.DataFrame(_constraint_bottleneck_rows(frame))
    hierarchical = constraint.loc[
        constraint["candidate_class"].eq("HIERARCHICAL")
    ]
    ab_a = hierarchical.loc[
        hierarchical["sleeve_or_increment"].eq("AB_MINUS_A")
    ].iloc[0]
    assert ab_a["availability"] == "PERSISTED_DISTANCE_ONLY"
    assert ab_a["deterministic_bottleneck_count"] == 1
    assert ab_a["net_lcb"] == "NOT_PERSISTED"
    standalone = hierarchical.loc[
        hierarchical["sleeve_or_increment"].eq("A")
    ].iloc[0]
    assert standalone["availability"] == "NOT_PERSISTED_STANDALONE"


def test_economic_waterfall_uses_only_final_increment_annotations() -> None:
    ledger, archive = _frames()
    frame = _augment_ledger(ledger, archive)
    waterfall = pd.DataFrame(_economic_waterfall_rows(frame))
    final = waterfall.loc[
        waterfall["sleeve_or_increment"].eq("ABC_MINUS_AB")
    ].iloc[0]
    assert final["availability"] == "PERSISTED_FINAL_INCREMENT_ANNOTATIONS"
    assert final["gross_positive_count"] == 1
    assert final["net_positive_count"] == 0
    assert final["cost_sign_killed_count"] == 1
    ab = waterfall.loc[
        waterfall["candidate_class"].eq("HIERARCHICAL")
        & waterfall["sleeve_or_increment"].eq("AB")
    ].iloc[0]
    assert ab["availability"] == "NOT_PERSISTED"
    assert pd.isna(ab["gross_positive_count"])


def test_fail_closed_decision_blocks_adaptive_policy() -> None:
    ledger, archive = _frames()
    frame = _augment_ledger(ledger, archive)
    learnability = [
        {
            "dimension": "horizon_hours",
            "dimension_checkpoint_rank_correlation_median": 1.0,
        }
    ]
    rows, decision = _decision_rows(
        frame=frame,
        learnability_rows=learnability,
        target_facts={
            "venue_shares": {"bybit": 1.0},
            "assets_with_multiple_priority_venues": 1,
        },
    )
    triggered = {row["branch"] for row in rows if row["triggered"]}
    assert "TARGET_EXECUTION_CONTRACT_REPAIR" in triggered
    assert "MAPPING_HOLDING_TURNOVER_REPAIR" in triggered
    assert "SMALL_ADAPTIVE_V1_4B" not in triggered
    assert decision["adaptive_v1_4b_authorized"] is False
    assert decision["new_market_candidate_evaluations"] == 0
