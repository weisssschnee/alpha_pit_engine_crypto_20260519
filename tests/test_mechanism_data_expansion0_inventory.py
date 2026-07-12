from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

import scripts.crypto_mechanism_data_expansion0_inventory as inventory


def test_inventory_manifest_fails_closed_on_prohibited_access() -> None:
    valid = {"performance_queries": 0, "row_data_read": False, "sealed_paths_footer_read": False, "reproducible": True}
    inventory.validate_inventory_manifest(valid)
    for key, value in (("performance_queries", 1), ("row_data_read", True), ("sealed_paths_footer_read", True), ("reproducible", False)):
        invalid = dict(valid)
        invalid[key] = value
        with pytest.raises((PermissionError, ValueError)):
            inventory.validate_inventory_manifest(invalid)


def test_recent_and_probe_paths_are_not_historical_sources() -> None:
    tokens = ["recent", "source_probes", "30d", "202605"]
    assert inventory.path_role("raw/source_probes/cross_exchange_20260522", tokens) == "INELIGIBLE_EVALUATION_OR_SHORT_PROBE"
    assert inventory.path_role("silver/okx_recent30d", tokens) == "INELIGIBLE_EVALUATION_OR_SHORT_PROBE"
    assert inventory.path_role("raw/binance_vision/aggTrades/2024-01.zip", tokens) == "INVENTORY_ELIGIBLE"


def test_release_choice_uses_eligible_physical_capacity_only() -> None:
    rows = pd.DataFrame([
        {"source_id": "recent_high_score", "inventory_status": "UNAVAILABLE_NO_VERIFIED_HISTORICAL_SOURCE", "physical_split_possible": False, "release_priority": 0},
        {"source_id": "aggtrades", "inventory_status": "DISCOVERED_REQUIRES_RELEASE_QUALIFICATION", "physical_split_possible": True, "release_priority": 1},
        {"source_id": "later", "inventory_status": "DISCOVERED_REQUIRES_RELEASE_QUALIFICATION", "physical_split_possible": True, "release_priority": 2},
    ])
    assert inventory.choose_first_release(rows) == "aggtrades"


def test_inventory_code_contains_no_evaluator_or_label_loader() -> None:
    source = Path(inventory.__file__).read_text(encoding="utf-8")
    for forbidden in ("multiobjective_evaluate(", "development_feedback(", "load_main_panel(", "strict_evaluations.csv"):
        assert forbidden not in source
