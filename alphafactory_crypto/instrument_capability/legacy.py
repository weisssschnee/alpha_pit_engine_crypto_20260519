"""Pinned legacy semantics for fixed parity and non-market compatibility only.

This module deliberately does not make historical implementations canonical.
It verifies the accepted closure tag, reads three historical Python modules with
``git show`` at the exact accepted commit, and executes them with the two small
dependency stubs they require.  It never checks out historical code and never
loads market data.

The fixed proposal coordinates below were selected mechanically: within
``panel_id=main``, ``lane_id=typed_random_fresh`` and ``legal=True``, take the
minimum ``(seed, ordinal, proposal_id)`` for each audited primitive.  No score,
return, survivor, or other performance field participated in selection.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
import types
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType, ModuleType
from typing import Mapping

import numpy as np


CLOSURE_TAG = "crypto-frontier-provenance-closure-20260714"
EXPECTED_CLOSURE_SHA = "4726795f61052470d56e2d1475e4f6da9d262943"
RAW_PROPOSALS_SOURCE = "runtime/nextgen_epoch0_20260711/raw_proposals.csv"

LEGACY_SOURCE_PATHS: Mapping[str, str] = MappingProxyType(
    {
        "temporal_program": "alphafactory_crypto/temporal_program.py",
        "b1s_canary": "alphafactory_crypto/b1s_canary.py",
        "nextgen_epoch": "alphafactory_crypto/nextgen_epoch.py",
    }
)


@dataclass(frozen=True)
class LegacyModules:
    """Historical modules loaded from the exact accepted closure."""

    temporal_program: ModuleType
    b1s_canary: ModuleType
    nextgen_epoch: ModuleType
    closure_sha: str
    source_sha256: Mapping[str, str]


@dataclass(frozen=True)
class RawProposalCoordinate:
    """Structural coordinate for a fixed historical parity replay."""

    primitive: str
    proposal_id: str
    canonical_identity: str
    panel_id: str
    lane_id: str
    algorithm: str
    seed: int
    ordinal: int
    lane_ordinal: int
    mechanism_id: str
    field_a: str
    field_b: str
    secondary_primitive: str
    interaction: str
    window: int
    long_window: int
    threshold: float
    direction: int


FIXED_RAW_PROPOSAL_COORDINATES: tuple[RawProposalCoordinate, ...] = (
    RawProposalCoordinate(
        "Delta", "epoch-candidate:33c831a16da758aa12ede49c",
        "typed-program:7fbb384415b7618a6d78cc1801b3f207c1bd3b34009ff1e5b1b83ebc04f1dc28",
        "main", "typed_random_fresh", "typed_random", 2701, 16, 16,
        "volatility_regime", "asset_return", "volatility_burst", "Delta",
        "residual", 48, 72, -1.0, 1,
    ),
    RawProposalCoordinate(
        "Slope", "epoch-candidate:1f814d359bd380402235ce7e",
        "typed-program:0024a1cffa86426f8a913ddb835dd7b2a163cf295baa08d95f80672367983359",
        "main", "typed_random_fresh", "typed_random", 2701, 23, 23,
        "volatility_regime", "volatility_burst", "asset_return", "Identity",
        "product", 8, 12, -0.5, 1,
    ),
    RawProposalCoordinate(
        "Acceleration", "epoch-candidate:4602f42715b5afaab5b5f958",
        "typed-program:e466cf0e97b44cc89da620e9701a6cba88d58e34121641518708166c4e4e951c",
        "main", "typed_random_fresh", "typed_random", 2701, 32, 32,
        "oi_inventory", "oi_change", "oi", "PathShape", "product", 12, 48, 0.0, -1,
    ),
    RawProposalCoordinate(
        "Persistence", "epoch-candidate:7d6517f858a5ab9242d5dbd5",
        "typed-program:f3b2f04c01dbb85fd7b4acbf9cc98b00fea5ca1fd7cfdab71c80ba0c5d83ac32",
        "main", "typed_random_fresh", "typed_random", 2701, 37, 37,
        "basis_dislocation_convergence", "funding", "basis_abs", "Delta", "none",
        48, 168, -0.5, 1,
    ),
    RawProposalCoordinate(
        "Duration", "epoch-candidate:e061ee2539e6222209dfe24f",
        "typed-program:dacb86e8e9c639fb3d5d3b1d9d7b152ff15b6ec46537c2f6e1768fc0e4bfe599",
        "main", "typed_random_fresh", "typed_random", 2701, 8, 8,
        "funding_dynamics", "funding", "funding_event_age", "Transition", "condition",
        24, 168, -1.0, -1,
    ),
    RawProposalCoordinate(
        "StateAge", "epoch-candidate:b63ed5f2258420737e9615a7",
        "typed-program:24bc61571703b76ea1dda3f5e79e70f75eae8e52fa00e2b65f5c4206d0208aff",
        "main", "typed_random_fresh", "typed_random", 2701, 65, 65,
        "session_time", "taker", "session_sin", "Delta", "none",
        12, 24, 1.0, 1,
    ),
    RawProposalCoordinate(
        "TimeSince", "epoch-candidate:f7a8b8f06ff45f801a3c6b04",
        "typed-program:3556be90a586a33378d01fc2fe68425f327744a51798efe69a1426cf94cd7110",
        "main", "typed_random_fresh", "typed_random", 2701, 129, 129,
        "temporal_state_path", "basis", "oi_change", "Delta", "residual",
        12, 24, 1.0, -1,
    ),
    RawProposalCoordinate(
        "FirstHit", "epoch-candidate:3346c4655ce3d585c50c877d",
        "typed-program:bdfb9993e1a2851569bc16c1e181b8d911fb831576c26ce3f819f4392c8c764f",
        "main", "typed_random_fresh", "typed_random", 2701, 162, 162,
        "temporal_state_path", "taker", "oi_change", "Transition", "none",
        8, 168, -0.5, -1,
    ),
    RawProposalCoordinate(
        "LastHit", "epoch-candidate:08a720cf058cd1f524f28162",
        "typed-program:47acdad0e36424bce0d4f1c662f19977f0a6dd9f2bf6cf6cfcc3e93d1a3f3ad1",
        "main", "typed_random_fresh", "typed_random", 2701, 199, 199,
        "temporal_state_path", "volatility_burst", "taker", "Delta", "condition",
        8, 12, 1.0, 1,
    ),
    RawProposalCoordinate(
        "Transition", "epoch-candidate:8720931c2d1ddf1b69a1a8ee",
        "typed-program:b90d3731c1f63e8dfd8ca4f926e172419906fa3f610193ead0ca88cf66fb2c1a",
        "main", "typed_random_fresh", "typed_random", 2701, 0, 0,
        "mark_index_deviation", "asset_return", "mark_index_deviation", "Delta",
        "condition", 8, 24, 1.0, -1,
    ),
    RawProposalCoordinate(
        "PathShape", "epoch-candidate:0ca730a98eefc0f6d6cce51a",
        "typed-program:e09b2535e511f14b76be8c54963facc326b2601ba9a94b84ad0c71c792aa3188",
        "main", "typed_random_fresh", "typed_random", 2701, 2, 2,
        "basis_dislocation_convergence", "basis", "basis", "PathShape", "condition",
        48, 168, -0.5, -1,
    ),
    RawProposalCoordinate(
        "EventWindow", "epoch-candidate:371b8d989d946a698c7168ee",
        "typed-program:161183887ac5f97c01fce1b1549fc6b0c6c706592fba52630a43c4e9f0df9d6d",
        "main", "typed_random_fresh", "typed_random", 2701, 7, 7,
        "funding_dynamics", "funding", "funding_event_age", "Delta", "product",
        12, 168, 1.0, -1,
    ),
    RawProposalCoordinate(
        "MultiScaleRelation", "epoch-candidate:0205e101f4349cf8b97e54bc",
        "typed-program:4ccf201f5c531992a1e27b5b0b23b3f691cb46a155699ed0607714759f988665",
        "main", "typed_random_fresh", "typed_random", 2701, 6, 6,
        "temporal_state_path", "volatility_burst", "oi_change",
        "Delta", "residual", 72, 168, -1.0, 1,
    ),
)


@dataclass(frozen=True)
class LegacyAlias:
    source: str
    name: str
    legacy_id: str
    status: str
    canonical_id: str


def _alias(
    source: str,
    name: str,
    legacy_id: str,
    status: str,
    canonical_id: str,
) -> LegacyAlias:
    return LegacyAlias(source, name, legacy_id, status, canonical_id)


_ALIASES = (
    # temporal_program: raw-threshold/PIT Series implementation.
    _alias("temporal_program", "Delta", "legacy.temporal.delta.v1", "EXACT_PARITY", "Delta"),
    _alias("temporal_program", "Slope", "legacy.temporal.ols_slope.v1", "EXACT_PARITY", "Slope"),
    _alias("temporal_program", "Acceleration", "legacy.temporal.acceleration.v1", "EXACT_PARITY", "Acceleration"),
    _alias("temporal_program", "Persistence", "legacy.temporal.raw_state_persistence.v1", "CONDITIONAL_PARITY_FINITE_FULL_WINDOW", "Persistence"),
    _alias("temporal_program", "Duration", "legacy.temporal.active_run_length.v1", "CONDITIONAL_PARITY_FINITE_SEGMENT", "Duration"),
    _alias("temporal_program", "StateAge", "legacy.temporal.active_run_length.v1", "LEGACY_BEHAVIOR_DEPRECATED_COLLAPSED_ALIAS", "StateAge"),
    _alias("temporal_program", "TimeSince", "legacy.temporal.age_since_active_sample.v1", "EXPECTED_SEMANTIC_CHANGE", "TimeSince"),
    _alias("temporal_program", "FirstHit", "legacy.temporal.raw_state_rising_pulse.v1", "LEGACY_BEHAVIOR_DEPRECATED_COLLAPSED_ALIAS", "FirstHit"),
    _alias("temporal_program", "LastHit", "legacy.temporal.last_active_coordinate.v1", "EXPECTED_SEMANTIC_CHANGE", "LastHit"),
    _alias("temporal_program", "Transition", "legacy.temporal.raw_state_rising_pulse.v1", "EXPECTED_SEMANTIC_CHANGE", "Transition"),
    _alias("temporal_program", "PathShape", "legacy.temporal.path_thirds_contrast.v1", "EXACT_PARITY", "PathShape"),
    _alias("temporal_program", "EventWindow", "legacy.temporal.active_state_count_partial.v1", "EXPECTED_SEMANTIC_CHANGE", "EventWindow"),
    _alias("temporal_program", "MultiScaleRelation", "legacy.temporal.multiscale_mean_difference.v1", "EXACT_PARITY", "MultiScaleRelation"),

    # nextgen_epoch: actual Epoch-1/Epoch-1R/Epoch-2 primitive dispatcher.
    _alias("nextgen_epoch", "Delta", "legacy.nextgen.delta.v1", "EXACT_PARITY", "Delta"),
    _alias("nextgen_epoch", "Slope", "legacy.nextgen.endpoint_secant_slope.v1", "EXPECTED_SEMANTIC_CHANGE", "Slope"),
    _alias("nextgen_epoch", "Acceleration", "legacy.nextgen.acceleration.v1", "EXACT_PARITY", "Acceleration"),
    _alias("nextgen_epoch", "Persistence", "legacy.nextgen.zstate_persistence_partial.v1", "EXPECTED_SEMANTIC_CHANGE", "Persistence"),
    _alias("nextgen_epoch", "Duration", "legacy.nextgen.zstate_active_run.v1", "EXPECTED_SEMANTIC_CHANGE", "Duration"),
    _alias("nextgen_epoch", "StateAge", "legacy.nextgen.age_since_zstate_entry.v1", "LEGACY_BEHAVIOR_DEPRECATED_COLLAPSED_ALIAS", "StateAge"),
    _alias("nextgen_epoch", "TimeSince", "legacy.nextgen.age_since_zstate_entry.v1", "LEGACY_BEHAVIOR_DEPRECATED_COLLAPSED_ALIAS", "TimeSince"),
    _alias("nextgen_epoch", "FirstHit", "legacy.nextgen.zstate_rising_pulse.v1", "LEGACY_BEHAVIOR_DEPRECATED_COLLAPSED_ALIAS", "FirstHit"),
    _alias("nextgen_epoch", "LastHit", "legacy.nextgen.age_since_zstate_entry.v1", "LEGACY_BEHAVIOR_DEPRECATED_COLLAPSED_ALIAS", "LastHit"),
    _alias("nextgen_epoch", "Transition", "legacy.nextgen.zstate_rising_pulse.v1", "EXPECTED_SEMANTIC_CHANGE", "Transition"),
    _alias("nextgen_epoch", "PathShape", "legacy.nextgen.partial_multiscale_mean_difference.v1", "LEGACY_BEHAVIOR_DEPRECATED_COLLAPSED_ALIAS", "PathShape"),
    _alias("nextgen_epoch", "EventWindow", "legacy.nextgen.zstate_transition_rate_partial.v1", "EXPECTED_SEMANTIC_CHANGE", "EventWindow"),
    _alias("nextgen_epoch", "MultiScaleRelation", "legacy.nextgen.partial_multiscale_mean_difference.v1", "CONDITIONAL_PARITY_FULL_MATURITY", "MultiScaleRelation"),

    # b1s_canary: lowercase operator surface; absent names are not fabricated.
    _alias("b1s_canary", "delta", "legacy.b1s.delta.v1", "EXACT_PARITY", "Delta"),
    _alias("b1s_canary", "momentum", "legacy.b1s.delta.v1", "EXACT_PARITY_ALIAS", "Delta"),
    _alias("b1s_canary", "slope", "legacy.b1s.endpoint_secant_slope.v1", "EXPECTED_SEMANTIC_CHANGE", "Slope"),
    _alias("b1s_canary", "acceleration", "legacy.b1s.acceleration.v1", "EXACT_PARITY", "Acceleration"),
    _alias("b1s_canary", "persistence", "legacy.b1s.positive_state_persistence_partial.v1", "CONDITIONAL_PARITY_THRESHOLD_ZERO_FULL_MATURITY", "Persistence"),
    _alias("b1s_canary", "event_age", "legacy.b1s.numeric_change_age.v1", "EXPECTED_SEMANTIC_CHANGE", "StateAge"),
    _alias("b1s_canary", "transition", "legacy.b1s.any_numeric_change_pulse.v1", "EXPECTED_SEMANTIC_CHANGE", "Transition"),
    _alias("b1s_canary", "event_window", "legacy.b1s.numeric_change_rate_partial.v1", "EXPECTED_SEMANTIC_CHANGE", "EventWindow"),
    _alias("b1s_canary", "multiscale", "legacy.b1s.implicit_quarter_scale_difference.v1", "CONDITIONAL_PARITY_EXPLICIT_SCALE_ADAPTER", "MultiScaleRelation"),
)

LEGACY_ALIAS_REGISTRY: Mapping[tuple[str, str], LegacyAlias] = MappingProxyType(
    {(item.source, item.name): item for item in _ALIASES}
)

NON_PERFORMANCE_SELECTION_RULES: tuple[str, ...] = (
    "Coordinates are bound to the accepted closure commit and raw_proposals artifact path.",
    "Filter panel_id=main, lane_id=typed_random_fresh, and legal=True before selection.",
    "For each required primitive, select minimum (seed, ordinal, proposal_id).",
    "Use only structural identity and legality fields; never inspect score, return, survivor, or rank.",
    "Missing or identity-drifted coordinates fail closed; no replacement is selected.",
    "Legacy replay is fixed parity evidence only and cannot authorize a canonical definition.",
    "No legacy result may open sealed data, start performance search, or support promotion.",
)


def _git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        encoding="utf-8",
        errors="strict",
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {detail}")
    return completed.stdout.strip()


def _validated_repo(repo: str | Path) -> Path:
    candidate = Path(repo).expanduser().resolve()
    if not candidate.is_dir():
        raise ValueError(f"repository directory does not exist: {candidate}")
    root = Path(_git(candidate, "rev-parse", "--show-toplevel")).resolve()
    actual = _git(root, "rev-parse", f"{CLOSURE_TAG}^{{commit}}")
    if actual != EXPECTED_CLOSURE_SHA:
        raise RuntimeError(
            f"closure tag drift: expected {EXPECTED_CLOSURE_SHA}, observed {actual}"
        )
    return root


def _blob(repo: Path, path: str) -> str:
    # Use the verified commit, rather than the tag name, after the identity check.
    return _git(repo, "show", f"{EXPECTED_CLOSURE_SHA}:{path}") + "\n"


def _activation_identity(active: object, **kwargs: object) -> str:
    digest = hashlib.sha256(np.asarray(active, dtype=bool).tobytes())
    for key in sorted(kwargs):
        digest.update(key.encode("utf-8"))
        digest.update(np.asarray(kwargs[key]).tobytes())
    return "synthetic-activation:" + digest.hexdigest()[:24]


def _canonical_weight_hash(values: object) -> str:
    return hashlib.sha256(np.asarray(values, dtype=float).tobytes()).hexdigest()


def load_legacy_modules(repo: str | Path) -> LegacyModules:
    """Load pinned historical primitive modules without checkout or market reads.

    The temporary ``sys.modules`` entries exist only while the historical source
    is compiled.  Previous entries are restored even if loading fails.
    """

    root = _validated_repo(repo)
    sources = {name: _blob(root, path) for name, path in LEGACY_SOURCE_PATHS.items()}
    source_sha256 = MappingProxyType(
        {name: hashlib.sha256(text.encode("utf-8")).hexdigest().upper() for name, text in sources.items()}
    )

    identity = types.ModuleType("alphafactory_crypto.identity_registry")
    identity.activation_identity = _activation_identity
    behaviour = types.ModuleType("alphafactory_crypto.signal_behaviour")
    behaviour.canonical_weight_hash = _canonical_weight_hash

    b1s = types.ModuleType("alphafactory_crypto.b1s_canary")
    nextgen = types.ModuleType("alphafactory_crypto.nextgen_epoch")
    temporal = types.ModuleType("alphafactory_crypto.temporal_program")
    modules = {
        identity.__name__: identity,
        behaviour.__name__: behaviour,
        b1s.__name__: b1s,
        nextgen.__name__: nextgen,
        temporal.__name__: temporal,
    }
    previous = {name: sys.modules.get(name) for name in modules}
    try:
        sys.modules.update(modules)
        for name, module in (
            ("b1s_canary", b1s),
            ("nextgen_epoch", nextgen),
            ("temporal_program", temporal),
        ):
            path = LEGACY_SOURCE_PATHS[name]
            module.__file__ = f"{EXPECTED_CLOSURE_SHA}:{path}"
            module.__package__ = "alphafactory_crypto"
            exec(compile(sources[name], module.__file__, "exec"), module.__dict__)
    finally:
        for name, old_module in previous.items():
            if old_module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = old_module

    return LegacyModules(
        temporal_program=temporal,
        b1s_canary=b1s,
        nextgen_epoch=nextgen,
        closure_sha=EXPECTED_CLOSURE_SHA,
        source_sha256=source_sha256,
    )


def resolve_legacy_alias(source: str, name: str) -> LegacyAlias:
    """Resolve an explicit historical alias; unknown names fail closed."""

    try:
        return LEGACY_ALIAS_REGISTRY[(source, name)]
    except KeyError as exc:
        raise KeyError(f"unregistered legacy primitive alias: {source}:{name}") from exc


if len(FIXED_RAW_PROPOSAL_COORDINATES) != 13:
    raise AssertionError("fixed parity coordinate count drifted")
if len({item.primitive for item in FIXED_RAW_PROPOSAL_COORDINATES}) != 13:
    raise AssertionError("fixed parity primitive coordinates are not unique")
if len(LEGACY_ALIAS_REGISTRY) != len(_ALIASES):
    raise AssertionError("duplicate legacy alias registry key")


__all__ = [
    "CLOSURE_TAG",
    "EXPECTED_CLOSURE_SHA",
    "FIXED_RAW_PROPOSAL_COORDINATES",
    "LEGACY_ALIAS_REGISTRY",
    "LEGACY_SOURCE_PATHS",
    "NON_PERFORMANCE_SELECTION_RULES",
    "RAW_PROPOSALS_SOURCE",
    "LegacyAlias",
    "LegacyModules",
    "RawProposalCoordinate",
    "load_legacy_modules",
    "resolve_legacy_alias",
]
