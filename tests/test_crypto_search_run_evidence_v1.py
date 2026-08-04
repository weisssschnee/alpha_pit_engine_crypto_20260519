from __future__ import annotations

from pathlib import Path

from alphafactory_crypto.broad_search.compositional18m import CandidateSpec
from alphafactory_crypto.broad_search.expression import Expression
from alphafactory_crypto.broad_search.pair18m import mechanism_realization_provenance
from alphafactory_crypto.broad_search.experiment_authority import (
    resolve_search_economic_receipt,
)
from alphafactory_crypto.broad_search.search_engine_v1 import (
    SEARCH_EVIDENCE_V1_ARMS,
    SEARCH_EVIDENCE_V1_CAMPAIGN,
    SEARCH_EVIDENCE_V1_SEEDS,
    _economic_campaign_seeds,
    _load_search_evidence_v1_contract,
    _search_evidence_v1_expected_checkpoint_allocations,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def _comparison(equal: bool, difference_fraction: float) -> dict[str, object]:
    return {
        "stages": {"SIGNAL": {"equal": equal}},
        "signal_difference_fraction": difference_fraction,
    }


def test_hierarchical_mechanism_realization_uses_ablation_axes() -> None:
    candidate = CandidateSpec(
        candidate_id="candidate",
        skeleton_id="skeleton",
        mechanism_family="CONDITIONAL_TEST",
        expression=Expression(
            "StateModulation",
            (
                Expression(
                    "RatioInteraction",
                    (Expression.raw("a"), Expression.raw("b")),
                ),
                Expression.raw("c"),
            ),
        ),
        control=Expression.raw("a"),
        horizon_hours=1,
        mapping_id="CROSS_SECTIONAL_ZERO_NET",
        raw_fields=("a", "b", "c"),
        field_families=("a", "b", "c"),
        rolling_windows=(),
        expression_depth=3,
        operator_path="StateModulation(RatioInteraction(Raw,Raw),Raw)",
    )
    provenance = {
        "comparisons": {
            "primary_vs_left_control": _comparison(False, 0.25),
            "primary_vs_right_control": _comparison(False, 0.50),
            "ab_vs_interaction_left_control": _comparison(False, 0.75),
            "ab_vs_interaction_right_control": _comparison(True, 0.0),
        }
    }

    result = mechanism_realization_provenance(
        candidate=candidate,
        hierarchical_three_axis=True,
        control_provenance=provenance,
    )

    assert result["declared_axis_count"] == 3
    assert result["active_axis_count"] == 2
    assert result["status"] == "PARTIAL_DECLARED_AXES_ACTIVE"
    assert result["condition_effect_rate"] == 0.25
    assert [row["active"] for row in result["axes"]] == [False, True, True]
    assert len(str(result["provenance_sha256"])) == 64


def test_evidence_campaign_reuses_v23_policy_with_new_fresh_seeds() -> None:
    config, catalog, _ = _load_search_evidence_v1_contract(REPO_ROOT)
    allocations = _search_evidence_v1_expected_checkpoint_allocations(
        stages=config["stages"],
        seeds=SEARCH_EVIDENCE_V1_SEEDS,
    )

    assert len(catalog) > 0
    assert _economic_campaign_seeds(SEARCH_EVIDENCE_V1_CAMPAIGN) == (
        SEARCH_EVIDENCE_V1_SEEDS
    )
    assert set(allocations) == {0, 1, 2, 3}
    assert all(
        allocation == {arm: 1000 for arm in SEARCH_EVIDENCE_V1_ARMS}
        for allocation in allocations.values()
    )
    assert config["validation"]["authorized"] is False
    assert config["evidence_contract"]["passive_diagnostics_only"] is True
    assert config["boundaries"]["search_policy_change"] is False


def test_evidence_campaign_receipt_is_hash_bound_and_authorized_once() -> None:
    receipt = resolve_search_economic_receipt(
        REPO_ROOT,
        "config/crypto_search_run_evidence_v1_receipt.json",
    )

    assert receipt["result"] == "RUN_AUTHORIZED_CONDITIONAL_DEVELOPMENT"
    assert receipt["run_authorized"] is True
    assert receipt["search_campaign"]["runner_campaign"] == (
        SEARCH_EVIDENCE_V1_CAMPAIGN
    )
    assert receipt["validation"]["role"] == "NOT_AUTHORIZED"
    assert receipt["holdout"]["read_allowed"] is False
