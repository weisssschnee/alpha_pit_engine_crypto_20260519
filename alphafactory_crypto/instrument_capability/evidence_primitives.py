"""Compact deterministic evidence renderers for canonical primitive qualification.

The functions return JSON-serializable values, write nothing, and use no market
data.  Historical comparisons are bound to the accepted closure by ``legacy``.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from .legacy import LEGACY_ALIAS_REGISTRY, load_legacy_modules
from .mapping import (
    CROSS_SECTIONAL_ZERO_NET,
    DEFAULT_MAPPING_CONTRACTS,
    map_portfolio,
)
from .primitives import CANONICAL_PRIMITIVES, evaluate_primitive


SEQUENCE_IDS = (
    "MONOTONIC_RISE",
    "MONOTONIC_FALL",
    "CONSTANT",
    "LINEAR_TREND",
    "STEP",
    "SINGLE_EVENT",
    "REPEATED_EVENT",
    "PERSISTENT_STATE",
    "SPARSE_STATE",
    "REVERSAL",
    "OSCILLATION",
    "MULTISCALE_PATH",
    "MISSING_SEGMENT",
)
PRIMITIVE_IDS = tuple(CANONICAL_PRIMITIVES)
SAMPLE_COORDINATES = (0, 3, 4, 7, 8, 11, 12, 13, 15, 16, 20, 23)
COMPATIBILITY_CLASSIFICATIONS = {
    "EXACT_PARITY",
    "CONDITIONAL_PARITY",
    "EXPECTED_SEMANTIC_CHANGE",
    "LEGACY_BEHAVIOR_DEPRECATED",
}


@dataclass(frozen=True)
class _FixedLegalCoordinate:
    primitive: str
    proposal_id: str
    canonical_identity: str
    seed: int
    ordinal: int
    window: int
    long_window: int
    threshold: float


# First legal=True occurrence per primitive in pinned Epoch-0 raw_proposals file
# order.  Selection used no score, return, survivor, or rank field.
_FIXED_LEGAL_NEXTGEN_COORDINATES = (
    _FixedLegalCoordinate("Delta", "epoch-candidate:33c831a16da758aa12ede49c", "typed-program:7fbb384415b7618a6d78cc1801b3f207c1bd3b34009ff1e5b1b83ebc04f1dc28", 2701, 16, 48, 72, -1.0),
    _FixedLegalCoordinate("Slope", "epoch-candidate:1f814d359bd380402235ce7e", "typed-program:0024a1cffa86426f8a913ddb835dd7b2a163cf295baa08d95f80672367983359", 2701, 23, 8, 12, -0.5),
    _FixedLegalCoordinate("Acceleration", "epoch-candidate:4602f42715b5afaab5b5f958", "typed-program:e466cf0e97b44cc89da620e9701a6cba88d58e34121641518708166c4e4e951c", 2701, 32, 12, 48, 0.0),
    _FixedLegalCoordinate("Persistence", "epoch-candidate:7d6517f858a5ab9242d5dbd5", "typed-program:f3b2f04c01dbb85fd7b4acbf9cc98b00fea5ca1fd7cfdab71c80ba0c5d83ac32", 2701, 37, 48, 168, -0.5),
    _FixedLegalCoordinate("Duration", "epoch-candidate:e061ee2539e6222209dfe24f", "typed-program:dacb86e8e9c639fb3d5d3b1d9d7b152ff15b6ec46537c2f6e1768fc0e4bfe599", 2701, 8, 24, 168, -1.0),
    _FixedLegalCoordinate("StateAge", "epoch-candidate:b63ed5f2258420737e9615a7", "typed-program:24bc61571703b76ea1dda3f5e79e70f75eae8e52fa00e2b65f5c4206d0208aff", 2701, 65, 12, 24, 1.0),
    _FixedLegalCoordinate("TimeSince", "epoch-candidate:f7a8b8f06ff45f801a3c6b04", "typed-program:3556be90a586a33378d01fc2fe68425f327744a51798efe69a1426cf94cd7110", 2701, 129, 12, 24, 1.0),
    _FixedLegalCoordinate("FirstHit", "epoch-candidate:3346c4655ce3d585c50c877d", "typed-program:bdfb9993e1a2851569bc16c1e181b8d911fb831576c26ce3f819f4392c8c764f", 2701, 162, 8, 168, -0.5),
    _FixedLegalCoordinate("LastHit", "epoch-candidate:08a720cf058cd1f524f28162", "typed-program:47acdad0e36424bce0d4f1c662f19977f0a6dd9f2bf6cf6cfcc3e93d1a3f3ad1", 2701, 199, 8, 12, 1.0),
    _FixedLegalCoordinate("Transition", "epoch-candidate:8720931c2d1ddf1b69a1a8ee", "typed-program:b90d3731c1f63e8dfd8ca4f926e172419906fa3f610193ead0ca88cf66fb2c1a", 2701, 0, 8, 24, 1.0),
    _FixedLegalCoordinate("PathShape", "epoch-candidate:0ca730a98eefc0f6d6cce51a", "typed-program:e09b2535e511f14b76be8c54963facc326b2601ba9a94b84ad0c71c792aa3188", 2701, 2, 48, 168, -0.5),
    _FixedLegalCoordinate("EventWindow", "epoch-candidate:371b8d989d946a698c7168ee", "typed-program:161183887ac5f97c01fce1b1549fc6b0c6c706592fba52630a43c4e9f0df9d6d", 2701, 7, 12, 168, 1.0),
    _FixedLegalCoordinate("MultiScaleRelation", "epoch-candidate:0205e101f4349cf8b97e54bc", "typed-program:4ccf201f5c531992a1e27b5b0b23b3f691cb46a155699ed0607714759f988665", 2701, 6, 72, 168, -1.0),
)


def _synthetic_matrix(length: int = 24) -> np.ndarray:
    if length < 24:
        raise ValueError("synthetic sequence length must be at least 24")
    t = np.arange(length, dtype=float)
    midpoint = length // 2
    single = np.full(length, -1.0); single[midpoint] = 2.0
    repeated = np.full(length, -1.0)
    repeated[np.arange(4, length, max(4, length // 6))] = 2.0
    persistent = np.full(length, -1.0); persistent[3:] = 1.0
    sparse = np.full(length, -1.0); sparse[[length // 3, 2 * length // 3]] = 1.0
    reversal = 1.0 - np.abs(t - midpoint) / max(1.0, midpoint / 2.0)
    missing = -1.5 + 3.0 * t / max(1.0, length - 1)
    missing[length // 3 : length // 3 + 3] = np.nan
    return np.vstack(
        [
            -2.0 + 4.0 * t / (length - 1),
            2.0 - 4.0 * t / (length - 1),
            np.full(length, 0.25),
            -1.0 + 0.25 * t,
            np.where(t < midpoint, -1.0, 1.0),
            single,
            repeated,
            persistent,
            sparse,
            reversal,
            np.sin(2.0 * np.pi * t / 6.0),
            0.02 * t + 0.6 * np.sin(2.0 * np.pi * t / 5.0),
            missing,
        ]
    )


def _cross_asset_rank(values: np.ndarray) -> np.ndarray:
    result = np.full(values.shape, np.nan, dtype=float)
    for column in range(values.shape[1]):
        finite_index = np.flatnonzero(np.isfinite(values[:, column]))
        if not len(finite_index):
            continue
        finite_values = values[finite_index, column]
        order = np.argsort(finite_values, kind="mergesort")
        local = np.empty(len(order), dtype=float)
        start = 0
        while start < len(order):
            end = start + 1
            while end < len(order) and finite_values[order[end]] == finite_values[order[start]]:
                end += 1
            local[order[start:end]] = 0.5 * (start + 1 + end) / len(order)
            start = end
        result[finite_index, column] = local
    return result


def _identity(prefix: str, values: np.ndarray) -> str:
    array = np.asarray(values, dtype=float)
    finite = np.isfinite(array)
    normalized = np.where(finite, array, 0.0)
    normalized[normalized == 0.0] = 0.0
    digest = hashlib.sha256()
    digest.update(json.dumps(array.shape, separators=(",", ":")).encode("ascii"))
    digest.update(finite.astype(np.uint8).tobytes())
    digest.update(normalized.astype("<f8", copy=False).tobytes())
    return f"{prefix}:" + digest.hexdigest()


def _json_number(value: float) -> float | None:
    return float(value) if np.isfinite(value) else None


def _compact_numeric(values: np.ndarray, coordinates: Iterable[int] = SAMPLE_COORDINATES) -> dict[str, Any]:
    finite = np.isfinite(values)
    selected = [index for index in coordinates if index < values.shape[1]]
    finite_values = values[finite]
    return {
        "identity": _identity("numeric", values),
        "finite_count": int(finite.sum()),
        "minimum": float(np.min(finite_values)) if len(finite_values) else None,
        "maximum": float(np.max(finite_values)) if len(finite_values) else None,
        "sample_time_coordinates": selected,
        "sample_by_sequence": {
            name: [_json_number(values[row, column]) for column in selected]
            for row, name in enumerate(SEQUENCE_IDS)
        },
    }


def _finite_summary(values: np.ndarray) -> dict[str, Any]:
    mask = np.isfinite(values)
    return {
        "identity": _identity("finite-mask", mask.astype(float)),
        "finite_count": int(mask.sum()),
        "missing_count": int(mask.size - mask.sum()),
        "finite_by_sequence": {name: int(mask[row].sum()) for row, name in enumerate(SEQUENCE_IDS)},
    }


def _activation_summary(values: np.ndarray) -> dict[str, Any]:
    active = np.isfinite(values) & (np.abs(values) > 1e-12)
    coordinates = np.argwhere(active)
    samples = [[SEQUENCE_IDS[int(row)], int(column)] for row, column in coordinates[:32]]
    return {
        "identity": _identity("activation", active.astype(float)),
        "count": int(len(coordinates)),
        "coordinate_sample": samples,
        "truncated": bool(len(coordinates) > len(samples)),
    }


def _behaviour_identity(values: np.ndarray) -> str:
    ranks = _cross_asset_rank(values)
    active = np.isfinite(values) & (np.abs(values) > 1e-12)
    digest = hashlib.sha256(
        (_identity("rank", ranks) + "|" + _identity("activation", active.astype(float))).encode("ascii")
    ).hexdigest()
    return "synthetic-primitive-behaviour:" + digest


def _check(name: str, condition: bool) -> dict[str, str]:
    return {"invariant": name, "result": "PASS" if bool(condition) else "FAIL"}


def _regressions(primitive: str, output: np.ndarray, source: np.ndarray) -> list[dict[str, str]]:
    row = {name: index for index, name in enumerate(SEQUENCE_IDS)}
    checks = [_check("missing input coordinate never emits a value", np.isnan(output[row["MISSING_SEGMENT"], 8:11]).all())]
    if primitive == "Delta":
        checks += [_check("constant delta is zero", np.allclose(output[row["CONSTANT"], 4:], 0.0)), _check("monotonic signs are preserved", np.all(output[row["MONOTONIC_RISE"], 4:] > 0) and np.all(output[row["MONOTONIC_FALL"], 4:] < 0))]
    elif primitive == "Slope":
        checks += [_check("linear OLS slope is exact", np.allclose(output[row["LINEAR_TREND"], 3:], 0.25)), _check("constant slope is zero", np.allclose(output[row["CONSTANT"], 3:], 0.0))]
    elif primitive == "Acceleration":
        checks += [_check("linear acceleration is zero", np.allclose(output[row["LINEAR_TREND"], 8:], 0.0)), _check("step produces nonzero acceleration", np.any(np.abs(output[row["STEP"]][np.isfinite(output[row["STEP"]])]) > 0))]
    elif primitive == "Persistence":
        finite = output[np.isfinite(output)]
        checks += [_check("persistence is bounded", bool(len(finite)) and np.all((finite >= 0) & (finite <= 1))), _check("persistent state reaches one", output[row["PERSISTENT_STATE"], -1] == 1.0)]
    elif primitive == "Duration":
        checks += [_check("inactive duration is zero", output[row["PERSISTENT_STATE"], 2] == 0.0), _check("active duration increments", output[row["PERSISTENT_STATE"], -1] == source.shape[1] - 3)]
    elif primitive == "StateAge":
        duration = evaluate_primitive("Duration", source, threshold=0.0)
        checks += [_check("state change resets age", output[row["STEP"], source.shape[1] // 2] == 0.0), _check("StateAge is not Duration", not np.array_equal(np.nan_to_num(output), np.nan_to_num(duration)))]
    elif primitive == "TimeSince":
        middle = source.shape[1] // 2
        checks += [_check("event resets time-since", output[row["SINGLE_EVENT"], middle] == 0.0), _check("time-since increments after event", output[row["SINGLE_EVENT"], middle + 1] == 1.0)]
    elif primitive == "FirstHit":
        checks += [_check("only one first hit per finite segment", np.nansum(output[row["REPEATED_EVENT"]]) == 1.0)]
    elif primitive == "LastHit":
        middle = source.shape[1] // 2
        checks += [_check("last hit stores event coordinate", output[row["SINGLE_EVENT"], middle] == middle), _check("last hit is held", output[row["SINGLE_EVENT"], middle + 2] == middle)]
    elif primitive == "Transition":
        middle = source.shape[1] // 2
        checks += [_check("rising transition is positive", output[row["SINGLE_EVENT"], middle] == 1.0), _check("falling transition is negative", output[row["SINGLE_EVENT"], middle + 1] == -1.0)]
    elif primitive == "PathShape":
        multiscale = evaluate_primitive("MultiScaleRelation", source, window=4, long_window=8)
        common = np.isfinite(output) & np.isfinite(multiscale)
        checks += [_check("constant path shape is zero", np.allclose(output[row["CONSTANT"], 3:], 0.0)), _check("PathShape is not MultiScaleRelation", common.any() and not np.allclose(output[common], multiscale[common]))]
    elif primitive == "EventWindow":
        middle = source.shape[1] // 2
        checks += [_check("singleton event count is one", np.all(output[row["SINGLE_EVENT"], middle : middle + 4] == 1.0)), _check("event expires after window", output[row["SINGLE_EVENT"], middle + 4] == 0.0)]
    elif primitive == "MultiScaleRelation":
        checks += [_check("constant multiscale relation is zero", np.allclose(output[row["CONSTANT"], 7:], 0.0)), _check("long-window warm-up is enforced", np.isnan(output[:, :7]).all())]
    return checks


def primitive_synthetic_parity_payload() -> dict[str, Any]:
    """Render compact, deterministic evidence for all thirteen primitives."""

    source = _synthetic_matrix()
    primitive_rows: list[dict[str, Any]] = []
    for primitive in PRIMITIVE_IDS:
        output = evaluate_primitive(primitive, source, window=4, long_window=8, threshold=0.0)
        ranks = _cross_asset_rank(output)
        regressions = _regressions(primitive, output, source)
        primitive_rows.append(
            {
                "primitive_id": primitive,
                "parameters": {"window": 4, "long_window": 8, "threshold": 0.0},
                "raw_numeric": _compact_numeric(output),
                "finite_mask": _finite_summary(output),
                "cross_asset_rank": _compact_numeric(ranks),
                "activation_coordinates": _activation_summary(output),
                "behavior_identity": _behaviour_identity(output),
                "key_regressions": regressions,
                "regression_result": "PASS" if all(item["result"] == "PASS" for item in regressions) else "FAIL",
            }
        )
    return {
        "schema_version": 1,
        "scope": "deterministic non-market primitive semantics",
        "sequence_count": len(SEQUENCE_IDS),
        "primitive_count": len(PRIMITIVE_IDS),
        "sequences": [
            {
                "sequence_id": name,
                "input_identity": _identity("synthetic-input", source[index : index + 1]),
                "sample": [_json_number(value) for value in source[index, :24]],
            }
            for index, name in enumerate(SEQUENCE_IDS)
        ],
        "primitives": primitive_rows,
        "overall_result": "PASS" if all(row["regression_result"] == "PASS" for row in primitive_rows) else "FAIL",
    }


def implementation_authority_rows() -> list[dict[str, Any]]:
    """Return canonical authority rows followed by explicit legacy aliases."""

    rows: list[dict[str, Any]] = []
    for primitive, contract in CANONICAL_PRIMITIVES.items():
        rows.append(
            {
                "row_type": "CANONICAL",
                "source": "alphafactory_crypto.instrument_capability.primitives",
                "name": primitive,
                "primitive_id": primitive,
                "canonical_id": primitive,
                "legacy_id": None,
                "authority_status": "ACTIVE_CANONICAL",
                "compatibility_status": "NOT_APPLICABLE",
                **contract.to_dict(),
            }
        )
    for key in sorted(LEGACY_ALIAS_REGISTRY):
        alias = LEGACY_ALIAS_REGISTRY[key]
        if alias.status.startswith("CONDITIONAL"):
            authority_status = "CONDITIONAL_COMPATIBILITY"
        elif alias.status.startswith("EXACT"):
            authority_status = "DEPRECATED_EXACT_COMPATIBILITY"
        else:
            authority_status = "DEPRECATED"
        rows.append(
            {
                "row_type": "LEGACY_ALIAS",
                "source": alias.source,
                "name": alias.name,
                "primitive_id": alias.legacy_id,
                "canonical_id": alias.canonical_id,
                "legacy_id": alias.legacy_id,
                "authority_status": authority_status,
                "compatibility_status": alias.status,
                "canonical_authority": "alphafactory_crypto.instrument_capability.primitives.evaluate_primitive",
            }
        )
    return rows


def _array_equal(left: np.ndarray, right: np.ndarray) -> bool:
    return np.array_equal(np.isfinite(left), np.isfinite(right)) and np.allclose(left, right, equal_nan=True, rtol=1e-10, atol=1e-12)


def _shared_equal(left: np.ndarray, right: np.ndarray) -> tuple[bool, int]:
    shared = np.isfinite(left) & np.isfinite(right)
    return bool(shared.any() and np.allclose(left[shared], right[shared], rtol=1e-10, atol=1e-12)), int(shared.sum())


def _comparison_classification(primitive: str, old: np.ndarray, new: np.ndarray) -> str:
    alias = LEGACY_ALIAS_REGISTRY[("nextgen_epoch", primitive)]
    if "COLLAPSED_ALIAS" in alias.status:
        return "LEGACY_BEHAVIOR_DEPRECATED"
    if _array_equal(old, new):
        return "EXACT_PARITY"
    shared_equal, _ = _shared_equal(old, new)
    if shared_equal:
        return "CONDITIONAL_PARITY"
    return "EXPECTED_SEMANTIC_CHANGE"


def _comparison_fields(prefix: str, values: np.ndarray) -> dict[str, Any]:
    ranks = _cross_asset_rank(values)
    active = np.isfinite(values) & (np.abs(values) > 1e-12)
    return {
        f"{prefix}_raw_numeric_identity": _identity("numeric", values),
        f"{prefix}_finite_mask_identity": _identity("finite-mask", np.isfinite(values).astype(float)),
        f"{prefix}_finite_coordinates": int(np.isfinite(values).sum()),
        f"{prefix}_rank_identity": _identity("rank", ranks),
        f"{prefix}_activation_identity": _identity("activation", active.astype(float)),
        f"{prefix}_activation_coordinates": int(active.sum()),
        f"{prefix}_behavior_identity": _behaviour_identity(values),
    }


def legacy_compatibility_rows(repo: str | Path) -> list[dict[str, Any]]:
    """Compare pinned nextgen semantics and old rank mapping to new authorities."""

    loaded = load_legacy_modules(repo)
    source = _synthetic_matrix(384)
    rows: list[dict[str, Any]] = []
    for coordinate in _FIXED_LEGAL_NEXTGEN_COORDINATES:
        old = loaded.nextgen_epoch._primitive(
            source,
            coordinate.primitive,
            coordinate.window,
            coordinate.long_window,
            coordinate.threshold,
        )
        new = evaluate_primitive(
            coordinate.primitive,
            source,
            window=coordinate.window,
            long_window=coordinate.long_window,
            threshold=coordinate.threshold,
        )
        old_ranks, new_ranks = _cross_asset_rank(old), _cross_asset_rank(new)
        shared_equal, shared_count = _shared_equal(old, new)
        classification = _comparison_classification(coordinate.primitive, old, new)
        if classification not in COMPATIBILITY_CLASSIFICATIONS:
            raise AssertionError(f"unsupported compatibility classification: {classification}")
        rows.append(
            {
                "comparison_kind": "PRIMITIVE",
                "source": "nextgen_epoch",
                "closure_sha": loaded.closure_sha,
                **asdict(coordinate),
                "selection_rule": "first recorded legal=True occurrence in pinned file order; no score, return, survivor, or rank used",
                "classification": classification,
                "shared_finite_coordinates": shared_count,
                "raw_equal_on_shared_coordinates": shared_equal,
                "finite_mask_equal": bool(np.array_equal(np.isfinite(old), np.isfinite(new))),
                "rank_equal": _array_equal(old_ranks, new_ranks),
                "activation_equal": bool(np.array_equal(np.isfinite(old) & (np.abs(old) > 1e-12), np.isfinite(new) & (np.abs(new) > 1e-12))),
                "behavior_equal": _behaviour_identity(old) == _behaviour_identity(new),
                **_comparison_fields("old", old),
                **_comparison_fields("new", new),
            }
        )

    fixed_signal = np.asarray(
        [
            [-3.0, -2.0, -1.0, 0.0],
            [-2.0, -1.0, 0.0, 1.0],
            [-1.0, 0.0, 1.0, 2.0],
            [1.0, 2.0, 3.0, 4.0],
            [2.0, 3.0, 4.0, 5.0],
            [3.0, 4.0, 5.0, 6.0],
        ],
        dtype=float,
    )
    old_weights = loaded.b1s_canary.rank_weights(fixed_signal, max_abs_weight=0.20)
    new_result = map_portfolio(fixed_signal, DEFAULT_MAPPING_CONTRACTS[CROSS_SECTIONAL_ZERO_NET])
    new_weights = new_result.weights
    mapping_classification = "EXACT_PARITY" if _array_equal(old_weights, new_weights) else "EXPECTED_SEMANTIC_CHANGE"
    rows.append(
        {
            "comparison_kind": "PORTFOLIO_MAPPING",
            "source": "b1s_canary.rank_weights",
            "closure_sha": loaded.closure_sha,
            "proposal_id": "NOT_APPLICABLE_FIXED_NON_MARKET_MAPPING_CASE",
            "primitive": "NOT_APPLICABLE",
            "classification": mapping_classification,
            "case_id": "FIXED_CS_CAP_AND_RENORMALIZATION_V1",
            "selection_rule": "predeclared six-asset rank geometry; no target, return, or score",
            "old_mapping_id": "LEGACY_IMPLICIT_RANK_ZERO_NET_CLIP_RENORMALIZE",
            "new_mapping_id": CROSS_SECTIONAL_ZERO_NET,
            "old_max_abs_weight": float(np.max(np.abs(old_weights))),
            "new_max_abs_weight": float(np.max(np.abs(new_weights))),
            "declared_position_cap": 0.20,
            "old_cap_pass": bool(np.max(np.abs(old_weights)) <= 0.20 + 1e-12),
            "new_cap_pass": bool(np.max(np.abs(new_weights)) <= 0.20 + 1e-12),
            "old_finite_coordinates": int(np.isfinite(old_weights).sum()),
            "new_finite_coordinates": int(np.isfinite(new_weights).sum()),
            "old_rank_identity": _identity("rank-weight", old_weights),
            "new_rank_identity": _identity("rank-weight", new_weights),
            "old_activation_identity": _identity("activation", (np.abs(old_weights) > 1e-12).astype(float)),
            "new_activation_identity": _identity("activation", (np.abs(new_weights) > 1e-12).astype(float)),
            "old_behavior_identity": _behaviour_identity(old_weights),
            "new_behavior_identity": _behaviour_identity(new_weights),
            "behavior_equal": _behaviour_identity(old_weights) == _behaviour_identity(new_weights),
            "key_regression": "PASS" if (np.max(np.abs(old_weights)) > 0.20 + 1e-12 and np.max(np.abs(new_weights)) <= 0.20 + 1e-12) else "FAIL",
        }
    )
    return rows


if len(SEQUENCE_IDS) != 13 or len(PRIMITIVE_IDS) != 13:
    raise AssertionError("synthetic sequence or primitive count drifted")
if len(_FIXED_LEGAL_NEXTGEN_COORDINATES) != 13:
    raise AssertionError("fixed legal nextgen coordinate count drifted")


__all__ = [
    "implementation_authority_rows",
    "legacy_compatibility_rows",
    "primitive_synthetic_parity_payload",
]
