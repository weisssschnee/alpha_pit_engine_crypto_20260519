from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from alphafactory_crypto.b1s_canary import FrozenPanel
from alphafactory_crypto.search_revision import (
    ADMISSION_RESULT_SCHEMA,
    adaptive_verdict,
    admission_result_frame,
    admit_full_identity,
    concentration_metrics,
    development_feedback,
    epoch0_failure_matrix,
    partition_exact_identity_owners,
    quota_plan,
)


REPO = Path(__file__).resolve().parents[1]


def row(index: int, family: str = "bbo") -> dict[str, object]:
    return {
        "proposal_id": f"p:{index}", "full_exact_identity": f"exact:{index}",
        "mechanism_id": family, "parent_identity": f"parent:{index % 40}",
        "behaviour_cluster": f"behaviour:{index % 70}", "ordinal": index,
    }


def test_quota_feasibility_does_not_mechanically_cap_single_family_bbo() -> None:
    rows = [row(index) for index in range(200)]
    plan = quota_plan(rows, 128)
    assert plan.family_cap == 128
    assert plan.feasible_quota == 128
    result = admit_full_identity(rows, 128)
    assert len(result.admitted_ids) == 128
    assert not result.plan.natural_underfill


def test_full_identity_dedup_precedes_final_assignment() -> None:
    rows = [row(index) for index in range(100)]
    rows += [dict(row(index + 100), full_exact_identity=f"exact:{index}") for index in range(100)]
    result = admit_full_identity(rows, 128)
    assert len(result.admitted_ids) == 100
    assert result.plan.identity_capacity == 100
    assert result.plan.natural_underfill == 28


def test_development_feedback_penalizes_cost_and_instability_before_novelty() -> None:
    rng = np.random.default_rng(11)
    timestamps = pd.date_range("2024-01-01", periods=720, freq="h", tz="UTC")
    target = rng.normal(0, 0.001, size=(6, len(timestamps)))
    panel = FrozenPanel("main", tuple("ABCDEF"), timestamps, {}, target, "bucket_start_plus_1h", "bucket_close", "MAIN_ONLY")
    weights = np.tile(np.array([-.2, -.2, -.1, .1, .2, .2])[:, None], (1, len(timestamps)))
    feedback = development_feedback(weights, panel, np.zeros(len(timestamps)))
    assert feedback.observations == 720
    assert np.isfinite(feedback.net_lcb)
    assert "novelty" not in feedback.__dict__
    assert isinstance(feedback.early_gate_pass, bool)


def test_adaptive_failure_rule_requires_survivor_gain_and_diversity() -> None:
    control = {"near_miss_per_strict": .02, "survivor_per_strict": 0.0, "cluster_yield": .9, "top_concentration": .2, "runtime_per_proposal": 1.0, "benchmark_increment_median": 0.0}
    proxy_only = {"near_miss_per_strict": .02, "survivor_per_strict": 0.0, "cluster_yield": .95, "top_concentration": .15, "runtime_per_proposal": 1.2, "benchmark_increment_median": 0.0}
    improved = dict(proxy_only, near_miss_per_strict=.04)
    assert adaptive_verdict(proxy_only, control) == "ADAPTIVE_FAILURE_NO_SURVIVOR_GAIN"
    assert adaptive_verdict(improved, control) == "ADAPTIVE_SUCCESS"


def test_epoch0_failure_matrix_preserves_fixed_root_causes() -> None:
    strict = pd.read_csv(REPO / "runtime/nextgen_epoch0_20260711/strict_evaluations.csv")
    matrix = epoch0_failure_matrix(strict)
    values = matrix.set_index("failure_axis")["affected_rows"].to_dict()
    assert values["identity_dedup_timing"] == 103
    assert values["cost_turnover"] == 995
    assert values["adaptive_proxy_basin"] == 1


def test_concentration_metrics_report_entropy_and_top_decile_share() -> None:
    frame = pd.DataFrame({
        "legal": [True] * 20, "development_scalar": list(range(20)),
        "mechanism_id": ["m1"] * 10 + ["m2"] * 10,
        "primitive": ["p1", "p2"] * 10,
        "behaviour_cluster": [f"b{i % 5}" for i in range(20)],
    })
    metrics = concentration_metrics(frame)
    assert 0 <= metrics["mechanism_entropy"] <= 1
    assert metrics["top_decile_mechanism_share"] == 1.0


def assert_empty_outcome(result, rows, requested: int = 32) -> None:
    assert result.admitted_ids == ()
    assert result.capacity.feasible_capacity == 0
    assert result.capacity.assigned_capacity == 0
    assert result.capacity.natural_underfill is True
    assert result.capacity.reason == "NO_LEGAL_EXACT_IDENTITIES"
    assert tuple(admission_result_frame(result, rows).columns) == ADMISSION_RESULT_SCHEMA


def test_columnless_empty_dataframe_is_standard_zero_capacity() -> None:
    rows = pd.DataFrame()
    assert_empty_outcome(admit_full_identity(rows, 32), rows)


def test_schema_empty_dataframe_is_standard_zero_capacity() -> None:
    rows = pd.DataFrame(columns=["proposal_id", "full_exact_identity", "mechanism_id", "parent_identity", "behaviour_cluster", "ordinal"])
    assert_empty_outcome(admit_full_identity(rows, 32), rows)


def test_one_identity_assigns_once() -> None:
    result = admit_full_identity([row(1)], 32)
    assert result.admitted_ids == ("p:1",)
    assert result.capacity.feasible_capacity == result.capacity.assigned_capacity == 1
    assert result.capacity.reason == "LEGAL_EXACT_IDENTITY_CAPACITY"


def test_alias_rows_without_representative_are_zero_capacity() -> None:
    rows = [dict(row(i), full_exact_identity="") for i in range(5)]
    assert_empty_outcome(admit_full_identity(rows, 32), rows)


def test_single_and_multiple_mechanisms_are_supported() -> None:
    single = admit_full_identity([row(i, "one") for i in range(20)], 16)
    multiple = admit_full_identity([row(i, f"m{i % 4}") for i in range(20)], 16)
    assert len(single.admitted_ids) == 16
    assert len(multiple.admitted_ids) == 16
    assert single.plan.mechanism_family_count == 1
    assert multiple.plan.mechanism_family_count == 4


def test_feasible_capacity_below_and_equal_to_quota() -> None:
    below = admit_full_identity([row(i) for i in range(7)], 10)
    equal = admit_full_identity([row(i) for i in range(10)], 10)
    assert below.capacity.feasible_capacity == below.capacity.assigned_capacity == 7
    assert below.capacity.natural_underfill
    assert equal.capacity.feasible_capacity == equal.capacity.assigned_capacity == 10
    assert not equal.capacity.natural_underfill


def test_bbo_single_mechanism_capacity_is_not_redistributed() -> None:
    bbo = admit_full_identity([row(i, "bbo") for i in range(128)], 128)
    assert bbo.plan.family_cap == 128
    assert bbo.capacity.assigned_capacity == 128


def test_empty_lane_does_not_change_other_lane_quota() -> None:
    empty = admit_full_identity([], 32)
    normal = admit_full_identity([row(i, "normal") for i in range(32)], 32)
    assert empty.capacity.assigned_capacity == 0
    assert normal.capacity.assigned_capacity == 32
    assert empty.capacity.assigned_capacity + normal.capacity.assigned_capacity == 32


def test_all_lanes_empty_return_complete_schema() -> None:
    outcomes = [admit_full_identity(pd.DataFrame(), quota) for quota in (32, 64, 96)]
    assert all(outcome.capacity.reason == "NO_LEGAL_EXACT_IDENTITIES" for outcome in outcomes)
    assert all(tuple(admission_result_frame(outcome, []).columns) == ADMISSION_RESULT_SCHEMA for outcome in outcomes)


def test_input_order_does_not_change_assignment() -> None:
    rows = [row(i, f"m{i % 3}") for i in range(30)]
    forward = admit_full_identity(rows, 20)
    reverse = admit_full_identity(list(reversed(rows)), 20)
    assert forward.admitted_ids == reverse.admitted_ids
    assert forward.capacity == reverse.capacity


def test_natural_underfill_never_reallocates_budget() -> None:
    lanes = {
        "empty": admit_full_identity([], 10),
        "limited": admit_full_identity([row(i, "limited") for i in range(3)], 10),
        "full": admit_full_identity([row(i, "full") for i in range(10)], 10),
    }
    assert {key: value.capacity.assigned_capacity for key, value in lanes.items()} == {"empty": 0, "limited": 3, "full": 10}
    assert sum(value.capacity.assigned_capacity for value in lanes.values()) == 13


def test_shared_exact_identities_are_owned_fairly_without_duplicate_votes() -> None:
    shared = [row(i, "shared") for i in range(12)]
    lane_rows = {"adaptive": shared, "control": list(reversed(shared))}
    owned = partition_exact_identity_owners(lane_rows, {"adaptive": 6, "control": 6}, ("adaptive", "control"))
    assert len(owned["adaptive"]) == 6
    assert len(owned["control"]) == 6
    identities = [item["full_exact_identity"] for rows in owned.values() for item in rows]
    assert len(identities) == len(set(identities)) == 12


def test_fair_identity_ownership_is_order_invariant_and_does_not_move_quota() -> None:
    lane_rows = {
        "empty": [],
        "left": [row(i, "shared") for i in range(8)],
        "right": [row(i, "shared") for i in reversed(range(8))],
    }
    quotas = {"empty": 4, "left": 4, "right": 4}
    first = partition_exact_identity_owners(lane_rows, quotas, ("empty", "left", "right"))
    second = partition_exact_identity_owners({key: list(reversed(value)) for key, value in lane_rows.items()}, quotas, ("empty", "left", "right"))
    assert first == second
    assert first["empty"] == []
    assert len(first["left"]) == len(first["right"]) == 4
