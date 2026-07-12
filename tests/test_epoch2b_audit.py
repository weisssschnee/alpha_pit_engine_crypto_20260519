import json
from pathlib import Path

import pandas as pd
import pytest

import scripts.crypto_epoch2b_audit as audit


def test_contract_forbids_new_performance_queries():
    config = json.loads(audit.CONFIG.read_text(encoding="utf-8"))
    assert config["performance_queries_allowed"] == 0
    source = Path(audit.__file__).read_text(encoding="utf-8")
    for forbidden in ("materialize_program(", "multiobjective_evaluate(", "development_feedback(", "load_main_panel("):
        assert forbidden not in source


def test_gross_lcb_proxy_uses_existing_summary_only():
    frame = pd.DataFrame({"net_lcb": [-.00005, .00001], "cost_drag_mean": [.00002, .00003]})
    assert audit.gross_lcb_proxy(frame).tolist() == pytest.approx([-.00003, .00004])


def test_gate_funnel_is_monotonic():
    rows = pd.DataFrame({
        "epoch": ["E"] * 3,
        "panel_id": ["main"] * 3,
        "mechanism_id": ["m"] * 3,
        "lane_id": ["l"] * 3,
        "admission_policy": ["p"] * 3,
        "gross_mean": [.1, .1, -.1],
        "net_lcb": [.01, -.02, -.03],
        "cost_drag_mean": [.01, .01, .01],
        "ic_mean": [.1] * 3,
        "ic_lcb": [.1] * 3,
        "net_mean": [.01, -.01, -.01],
        "worst_horizon_net_mean": [0.] * 3,
        "time_block_stability": [1.] * 3,
        "turnover_mean": [.1] * 3,
        "max_weight_mean": [.1] * 3,
        "benchmark_incremental_lcb": [.01] * 3,
        "hard_gate_pass": [True] * 3,
    })
    funnel = audit.build_funnel(audit.gate_frame(rows), "TEST")
    row = funnel[funnel.group_type == "PANEL"].iloc[0]
    stages = [row[column] for column in ("all_strict", "positive_gross", "positive_gross_lcb_proxy", "positive_net", "positive_net_lcb", "stable_worst_block", "benchmark_incremental", "survivor")]
    assert stages == sorted(stages, reverse=True)


def test_bootstrap_is_deterministic():
    first = audit.bootstrap_ci([1., 2., 3.], resamples=200, seed=7)
    second = audit.bootstrap_ci([1., 2., 3.], resamples=200, seed=7)
    assert first == second


def test_hybrid_replay_applies_quota_after_exact_dedup():
    rows = []
    for ordinal in range(20):
        rows.append({
            "panel_id": "main", "exact_identity": f"e{ordinal}", "near_score": 20 - ordinal,
            "quality": 20 - ordinal, "proposal_id": f"c{ordinal}", "full_behaviour_cluster": f"b{ordinal % 8}",
            "mechanism_id": f"m{ordinal % 4}", "hypothesis": f"h{ordinal % 3}", "near_miss": ordinal < 2,
            "net_lcb": .1 if ordinal == 0 else -.1, "gate_survivor": False,
        })
    assignments = pd.DataFrame([
        {"panel_id": "main", "admission_policy": policy, "exact_identity": f"e{ordinal}"}
        for policy in ("GLOBAL_QUALITY", "STRATIFIED_DIVERSITY") for ordinal in range(10)
    ])
    replay, summary = audit.hybrid_replay(pd.DataFrame(rows), assignments, {"hybrid_report_only_replay": {"quality_share": .6, "diversity_share": .4}})
    panel = summary["panels"][0]
    assert len(replay) == 10 and panel["quality_rows"] == 6 and panel["diversity_rows"] == 4
    assert replay.exact_identity.nunique() == 10 and summary["new_performance_queries"] == 0


def test_route_priority_keeps_main_new_mechanism_as_only_primary_route():
    config = json.loads(audit.CONFIG.read_text(encoding="utf-8"))
    unique = pd.DataFrame({
        "epoch": ["EPOCH0"] * 100,
        "panel_id": ["main"] * 100,
        "gate_positive_gross_lcb_proxy": [True] * 3 + [False] * 97,
        "gate_positive_net_lcb": [False] * 100,
        "near_miss": [True] * 10 + [False] * 90,
        "failed_gates_audit": ["NET_LCB"] * 100,
    })
    parents = pd.DataFrame({"classification": ["NO_ECONOMIC_EDGE"] * 70 + ["PORTFOLIO_TRANSFORM_REQUIRED"] * 30})
    benchmarks = pd.DataFrame({"panel_id": ["main"], "net_lcb": [-.01], "turnover_mean": [.1]})
    bbo = pd.DataFrame({
        "full_behaviour_cluster": ["b1", "b2"], "field_a": ["spread", "spread"],
        "field_b": ["bid_qty", "ask_qty"], "primitive": ["Slope", "Duration"], "interaction": ["residual", "residual"],
    })
    decision = audit.select_route(unique, parents, benchmarks, bbo, {"coordinate_coverage_ratio": .82}, config)
    assert decision["main_recommendation"] == "PIVOT_TO_NEW_MECHANISM_OR_DATA"
    assert decision["secondary_line"] == "BBO_DEVELOPMENT_COVERAGE_ACQUISITION_PLAN_ONLY"
