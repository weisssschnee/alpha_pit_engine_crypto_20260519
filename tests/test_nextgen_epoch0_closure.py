from __future__ import annotations

import importlib.util
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("crypto_nextgen_epoch0_closure", REPO / "scripts/crypto_nextgen_epoch0_closure.py")
assert SPEC and SPEC.loader
closure = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(closure)


def test_recommendation_prioritizes_search_engine_when_no_survivor() -> None:
    assert closure.select_recommendation(
        survivors=0, adaptive_basin_rate=0.0, bbo_stratified_fill=1.0, semantic_exact_conversion=0.8,
    ) == "REVISE_SEARCH_ENGINE_AND_REPEAT_DEVELOPMENT_EPOCH"


def test_recommendation_prioritizes_hypothesis_space_only_after_engine_gates_pass() -> None:
    assert closure.select_recommendation(
        survivors=3, adaptive_basin_rate=0.0, bbo_stratified_fill=1.0, semantic_exact_conversion=0.1,
    ) == "REVISE_HYPOTHESIS_SPACE_AND_REPEAT_DEVELOPMENT_EPOCH"


def test_current_epoch_outputs_pass_independent_closure_validation() -> None:
    result = closure.validate()
    assert result["decision"] == "FROZEN_DEVELOPMENT_EPOCH_COMPLETED"
    assert result["recommendation"] == "REVISE_SEARCH_ENGINE_AND_REPEAT_DEVELOPMENT_EPOCH"
    assert result["proposal_rows"] == 32768
    assert result["total_development_strict_evaluations"] == 1801
    assert result["development_survivors"] == 0
    assert result["rerun_required"] is False
    assert result["no_new_evaluation_block_read"] is True
