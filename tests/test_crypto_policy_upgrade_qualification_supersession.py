from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from scripts.crypto_policy_upgrade_qualification_supersession import qualify_audit


ROOT = Path(__file__).parents[1]


def _inputs() -> tuple[dict, dict]:
    audit = json.loads(
        (ROOT / "runtime/crypto_policy_upgrade_canary_v1_20260720/POLICY_UPGRADE_BEHAVIOR_AUDIT.json").read_text()
    )
    config = json.loads((ROOT / "config/crypto_policy_upgrade_canary_v1.json").read_text())
    return audit, config


def test_known_lite_diagnostics_do_not_invalidate_real_upgrades() -> None:
    audit, config = _inputs()
    decisions = qualify_audit(audit, config)
    assert decisions["cem_distribution_v1"]["positive_seed_count_vs_random_and_lite"] == 4
    assert decisions["evolutionary_typed_v1"]["positive_seed_count_vs_random_and_lite"] == 3
    assert {row["decision"] for row in decisions.values()} == {"KEEP_FOR_FUTURE_NEW_DATA_ARENA"}


def test_any_unexpected_implementation_error_fails_closed() -> None:
    audit, config = _inputs()
    changed = deepcopy(audit)
    changed["implementation_errors"].append("RESOURCE:WORKER_RSS")
    with pytest.raises(ValueError, match="unexpected implementation errors"):
        qualify_audit(changed, config)
    changed = deepcopy(audit)
    changed["matched_seed_comparisons"]["cem_distribution_v1"][0]["jointly_positive"] = False
    with pytest.raises(ValueError, match="joint comparison flag mismatch"):
        qualify_audit(changed, config)
