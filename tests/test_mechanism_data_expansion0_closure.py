from pathlib import Path

import pytest

import scripts.crypto_mechanism_data_expansion0_closure as closure


def valid_payloads():
    inventory = {"new_performance_queries": 0, "forward_read": False, "selection_used_performance": False}
    release = {"performance_queries": 0, "performance_values_read": False, "return_labels_read": False, "forward_read": False,
               "candidate_promotion": False, "memory_updated": False, "reproducible": True, "interpolation_used": False}
    benchmark = {"fixed_evaluations": 164, "forward_read": False, "spent_evaluation_read": False, "candidate_promotion": False,
                 "memory_update": False, "complex_search_participation": False, "additional_budget": False}
    bbo = {"performance_queries": 0, "forward_read": False, "accepted_identity_used": False}
    return inventory, release, benchmark, bbo


def test_closure_boundaries_pass_for_fixed_evidence() -> None:
    closure.validate_boundaries(*valid_payloads())


def test_closure_boundaries_fail_on_promotion_or_forward() -> None:
    inventory, release, benchmark, bbo = valid_payloads()
    benchmark["candidate_promotion"] = True
    with pytest.raises(PermissionError):
        closure.validate_boundaries(inventory, release, benchmark, bbo)
    benchmark["candidate_promotion"] = False
    bbo["forward_read"] = True
    with pytest.raises(PermissionError):
        closure.validate_boundaries(inventory, release, benchmark, bbo)


def test_closure_code_does_not_invoke_evaluator() -> None:
    source = Path(closure.__file__).read_text(encoding="utf-8")
    for forbidden in ("multiobjective_evaluate(", "development_feedback(", "load_main_panel("):
        assert forbidden not in source
