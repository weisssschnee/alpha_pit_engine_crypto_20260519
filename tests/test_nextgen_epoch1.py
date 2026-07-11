from __future__ import annotations

from collections import Counter

import pandas as pd

import scripts.crypto_nextgen_epoch1 as epoch1


def test_epoch1_frozen_budget_shape_and_matched_controls() -> None:
    config = epoch1.load_json(epoch1.CONFIG)
    epoch1.validate_config(config)
    assert len(epoch1.MAIN_LANES) == 12
    assert len(epoch1.BBO_LANES) == 1
    assert sum({lane: 2560 for lane in epoch1.MAIN_LANES}.values()) + 2048 == 32768
    assert sum({lane: 120 for lane in epoch1.MAIN_LANES}.values()) + 96 == 1536
    assert set(epoch1.MATCHED) == set(epoch1.ADAPTIVE)


def test_matched_controls_have_identical_root_program_distributions() -> None:
    registry = epoch1.load_json(epoch1.MECHANISMS)
    for adaptive, control in epoch1.MATCHED.items():
        adaptive_roots = [epoch1.canonical_program_json(epoch1._program_for_lane(registry, adaptive, "main", 3701, i)) for i in range(64)]
        control_roots = [epoch1.canonical_program_json(epoch1._program_for_lane(registry, control, "main", 3701, i)) for i in range(64)]
        assert Counter(adaptive_roots) == Counter(control_roots)


def test_bbo_offline_replay_removes_mechanical_family_cap() -> None:
    raw = pd.read_csv(epoch1.EPOCH0_ROOT / "raw_proposals.csv", low_memory=False)
    bbo = raw[(raw.panel_id == "bbo_micro") & raw.legal].sort_values(["ordinal", "proposal_id"])
    rows = [{
        "proposal_id": row.proposal_id,
        "full_exact_identity": row.exact_identity,
        "mechanism_id": row.mechanism_id,
        "parent_identity": row.parent_identity,
        "behaviour_cluster": row.behaviour_cluster,
        "ordinal": int(row.ordinal),
    } for row in bbo.itertuples()]
    outcome = epoch1.admit_full_identity(rows, 128)
    assert outcome.plan.family_cap == 128
    assert outcome.plan.feasible_quota == 128
    assert len(outcome.admitted_ids) == 128


def test_smoke_contract_has_no_performance_or_forward_access() -> None:
    config = epoch1.load_json(epoch1.CONFIG)
    assert config["throughput_smoke"]["reads_performance"] is False
    assert any("forward" in item for item in config["prohibited"])
    assert config["admission_contract"]["full_identity_before_strict_assignment"] is True
    assert config["admission_contract"]["one_exact_identity_one_vote"] is True
