from __future__ import annotations

import inspect
import json
from pathlib import Path

import numpy as np

from alphafactory_crypto.broad_search.qualification18m import (
    FINAL_CLASSIFICATIONS,
    _classify,
    _matched_occupancy_weights,
)
from alphafactory_crypto.broad_search.runner18m import build_evidence


REPO_ROOT = Path(__file__).parents[1]
CONFIG_PATH = (
    REPO_ROOT / "config" / "crypto_localized_mechanism_qualification_v1.json"
)


def test_qualification_config_keeps_every_search_boundary_closed() -> None:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    boundaries = config["boundaries"]
    assert boundaries["new_proposals"] is False
    assert boundaries["search_or_tuning"] is False
    assert boundaries["candidate_pack_changes"] is False
    assert boundaries["sealed_reads"] is False
    assert boundaries["formal_search"] is False
    assert boundaries["candidate_promotion"] is False
    assert boundaries["forward"] == "SEALED"
    assert config["fixed_ablation"]["variants"] == [
        "A_FULL_CANDIDATE",
        "B_BASE_SIGNAL_ONLY",
        "C_REGIME_ONLY",
        "D_NEUTRAL_REGIME",
        "E_TIME_SHUFFLED_REGIME",
        "F_LAGGED_REGIME",
        "G_MATCHED_OCCUPANCY_PLACEBO",
    ]


def test_matched_occupancy_relabels_without_changing_exposure() -> None:
    reference = np.array(
        [
            [-0.2, 0.0],
            [-0.1, -0.2],
            [0.0, -0.1],
            [0.1, 0.1],
            [0.2, 0.2],
        ]
    )
    signal = np.array(
        [
            [5.0, 1.0],
            [4.0, 2.0],
            [3.0, 3.0],
            [2.0, 4.0],
            [1.0, 5.0],
        ]
    )
    support = np.ones_like(reference, dtype=bool)
    result = _matched_occupancy_weights(reference, signal, support)
    assert np.array_equal(
        np.sum(np.abs(result) > 1e-12, axis=0),
        np.sum(np.abs(reference) > 1e-12, axis=0),
    )
    assert np.allclose(
        np.sum(np.abs(result), axis=0),
        np.sum(np.abs(reference), axis=0),
    )
    assert np.allclose(np.sum(result, axis=0), np.sum(reference, axis=0))
    assert np.max(np.abs(result)) == np.max(np.abs(reference))


def test_source_runner_exposes_report_only_metrics_to_stage_b_gate() -> None:
    source = inspect.getsource(build_evidence)
    assert source.index("stage_a_challenge = _parallel_challenge") < source.index(
        "stage_b, stage_b_resources = _parallel_lanes"
    )
    assert 'counts_a["challenge_positive_clusters"] >= 5' in source
    assert 'counts_a["maximum_family_challenge_yield"] > 0.005' in source


def test_independence_failures_prevent_challenger_classification() -> None:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    identity = {
        "formula_identity": {
            "expression_id": "A",
            "control_expression_id": "B",
        },
        "artifact_identity_reuse_error": False,
        "blocks": [
            {
                "primary_control": {"portfolio_exact_equality": False},
                "native_metrics": {"incremental": {"net_lcb": 1.0}},
            },
            {
                "primary_control": {"portfolio_exact_equality": False},
                "native_metrics": {
                    "incremental": {"net_lcb": -0.1, "net_mean": 0.1}
                },
            },
        ],
    }
    independence = {
        "cluster_threshold": {
            "report_only_metrics_visible_to_stage_b_gate": True
        },
        "selection": {"adaptive_months_reused_in_robust_statistic": 12},
    }
    a_row = {
        "variant": "A_FULL_CANDIDATE",
        "comparison_to_A": {"portfolio_exact_equality_to_A": True},
    }
    b_row = {
        "variant": "B_BASE_SIGNAL_ONLY",
        "comparison_to_A": {"portfolio_exact_equality_to_A": False},
    }
    ablation = {
        "blocks": {
            "adaptive": [a_row, b_row],
            "report_only": [a_row, b_row],
        },
        "economic_concentration": {
            "accidental_concentration": False,
            "breaches": {},
        },
        "combined_18m_monthly_robustness": {
            "A_FULL_CANDIDATE": {"robust_positive": True},
            "C_REGIME_ONLY": {"robust_positive": True},
            "G_MATCHED_OCCUPANCY_PLACEBO": {"robust_positive": False},
        },
    }
    cross_seed = {"independent_mechanism_replications": 0}
    classification, evidence = _classify(
        config, identity, independence, ablation, cross_seed
    )
    assert classification in FINAL_CLASSIFICATIONS
    assert classification == "INSUFFICIENT_INDEPENDENT_EVIDENCE"
    assert evidence["insufficient_independent_evidence"] is True
