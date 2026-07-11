from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from alphafactory_crypto.b1s_canary import FrozenPanel
from alphafactory_crypto.nextgen_epoch import (
    BBO_LANES,
    MAIN_LANES,
    UCTProgramPolicy,
    canonical_program,
    cem_preference,
    make_program,
    materialize_program,
    multiobjective_evaluate,
    pareto_front,
    program_identity,
    signal_record,
    surrogate_rank,
    validate_epoch_contract,
    validate_mechanism_registry,
)


REPO = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((REPO / "config/crypto_nextgen_mechanism_registry_v1.json").read_text(encoding="utf-8"))
CONFIG = json.loads((REPO / "config/crypto_nextgen_epoch0_v1.json").read_text(encoding="utf-8"))


def panel() -> FrozenPanel:
    rng = np.random.default_rng(7)
    timestamps = pd.date_range("2024-01-01", periods=240, freq="h", tz="UTC")
    shape = (6, len(timestamps))
    base = rng.normal(size=shape).cumsum(axis=1)
    fields = {
        "funding": rng.normal(scale=0.001, size=shape),
        "funding_change": rng.normal(scale=0.0002, size=shape),
        "funding_surprise": rng.normal(size=shape),
        "funding_event_age": np.tile(np.arange(len(timestamps)) % 8, (6, 1)).astype(float),
        "basis": rng.normal(size=shape),
        "basis_abs": np.abs(rng.normal(size=shape)),
        "oi": np.abs(base) + 10,
        "oi_change": rng.normal(scale=0.01, size=shape),
        "asset_return": rng.normal(scale=0.01, size=shape),
        "relative_market_return": rng.normal(scale=0.01, size=shape),
        "mark_index_deviation": rng.normal(size=shape),
        "taker": rng.normal(size=shape),
        "liquidity": np.abs(base),
        "volatility": np.abs(rng.normal(size=shape)),
        "volatility_burst": rng.normal(size=shape),
        "session_sin": np.tile(np.sin(np.arange(len(timestamps)) * np.pi / 12), (6, 1)),
        "session_cos": np.tile(np.cos(np.arange(len(timestamps)) * np.pi / 12), (6, 1)),
        "market_return": rng.normal(scale=0.01, size=shape),
        "cross_confirmation": rng.choice([-1.0, 1.0], size=shape),
    }
    target = rng.normal(scale=0.01, size=shape)
    return FrozenPanel("main", tuple(f"S{i}" for i in range(6)), timestamps, fields, target, "bucket_start_plus_1h", "bucket_close", "MAIN_ONLY")


def test_contract_and_registry_define_real_mechanism_volume() -> None:
    families = validate_mechanism_registry(REGISTRY)
    validate_epoch_contract(CONFIG, REGISTRY)
    assert len(families) == 11
    assert tuple(CONFIG["lanes"]["main"]) == MAIN_LANES
    assert tuple(CONFIG["lanes"]["bbo_micro"]) == BBO_LANES
    assert sum(int(item["semantic_volume_estimate"]) for item in families) > 50_000
    assert all(item["expected_failure_modes"] for item in families)


def test_program_canonicalization_and_materialization_are_deterministic() -> None:
    spec = make_program(REGISTRY, lane_id="typed_ast", panel_id="main", algorithm="typed_ast", seed=11, ordinal=5)
    first = materialize_program(spec, panel())
    second = materialize_program(spec, panel())
    np.testing.assert_allclose(first, second, equal_nan=True)
    assert program_identity(spec) == program_identity(replace(spec, raw_template="neutral alias", repaired=True))
    payload = canonical_program(spec)
    assert payload["pit_rule"] == "usable_time_lte_decision_time"
    assert payload["maturity_rule"] == "max(source_maturity,completed_past_window)"


def test_disabled_or_unavailable_capability_cannot_materialize() -> None:
    spec = make_program(REGISTRY, lane_id="typed_ast", panel_id="main", algorithm="typed_ast", seed=13, ordinal=7)
    invalid = replace(spec, field_a="liquidation_notional")
    with pytest.raises((PermissionError, KeyError)):
        materialize_program(invalid, panel())


def test_uct_is_multistep_and_cem_freezes_a_distribution() -> None:
    policy = UCTProgramPolicy(REGISTRY, panel_id="main", lane_id="uct_mcts", seed=17)
    specs = []
    scores = []
    for ordinal in range(48):
        spec = policy.propose(ordinal)
        score = float((ordinal % 9) - 4)
        policy.update(ordinal, score)
        specs.append(spec)
        scores.append(score)
    assert all(len(path) == 4 for path in policy.paths.values())
    assert policy.visits[()] == 48
    assert policy.frozen_preference()["mechanism_id"]
    preference = cem_preference(specs, scores)
    assert set(preference) == {"mechanism_id", "primitive", "interaction", "window"}
    assert all(preference.values())


def test_surrogate_selects_unique_programs_without_target_access() -> None:
    train = [make_program(REGISTRY, lane_id="surrogate", panel_id="main", algorithm="surrogate", seed=19, ordinal=i) for i in range(32)]
    scores = [float(i % 7) for i in range(32)]
    pool = [make_program(REGISTRY, lane_id="surrogate", panel_id="main", algorithm="surrogate", seed=23, ordinal=i + 100) for i in range(256)]
    selected = surrogate_rank(train, scores, pool, 40)
    assert len(selected) == 40
    assert len({program_identity(spec) for spec in selected}) == 40


def test_signal_and_multiobjective_vector_keep_noncompensating_gates() -> None:
    frozen = panel()
    spec = make_program(REGISTRY, lane_id="typed_ast", panel_id="main", algorithm="typed_ast", seed=29, ordinal=3)
    signal = materialize_program(spec, frozen)
    record, weights = signal_record(spec, signal, frozen, np.arange(len(frozen.timestamps)) % 4 == 0)
    assert record.exact_identity.startswith("exact-signal:")
    benchmark = np.zeros(len(frozen.timestamps), dtype=float)
    vector = multiobjective_evaluate(
        weights, frozen, complexity=3, behaviour_novelty=1.0, benchmark_net=benchmark,
        cost_bps=5.0, minimum_assets=5,
    )
    assert vector.observations > 100
    assert 0.0 <= vector.coordinate_coverage <= 1.0
    assert vector.complexity == 3
    assert isinstance(vector.hard_gate_pass, bool)


def test_pareto_archive_uses_full_vector_not_single_scalar() -> None:
    base = {
        "hard_gate_pass": True, "ic_lcb": 0.01, "net_lcb": 0.001,
        "worst_horizon_net_mean": 0.0, "time_block_stability": 0.5,
        "behaviour_novelty": 1.0, "benchmark_incremental_lcb": 0.0,
        "turnover_mean": 1.0, "concentration_hhi_mean": 0.2, "complexity": 2,
        "placebo_ic_abs": 0.01,
    }
    rows = [
        base | {"proposal_id": "a", "ic_lcb": 0.02, "turnover_mean": 1.5},
        base | {"proposal_id": "b", "ic_lcb": 0.01, "turnover_mean": 0.5},
        base | {"proposal_id": "c", "ic_lcb": 0.0, "turnover_mean": 2.0},
        base | {"proposal_id": "d", "hard_gate_pass": False, "ic_lcb": 1.0},
    ]
    assert pareto_front(rows) == ["a", "b"]
