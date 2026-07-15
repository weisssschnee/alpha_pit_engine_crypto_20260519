"""Frozen 18-month compositional skeletons and deterministic proposal grammar."""

from __future__ import annotations

import hashlib
import json
import random
import statistics
import time
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

import numpy as np

from alphafactory_crypto.instrument_capability.mapping import (
    CROSS_SECTIONAL_ZERO_NET,
    DEFAULT_MAPPING_CONTRACTS,
    mapping_contract_sha256,
)
from scipy.stats import rankdata

from .expression import (
    Expression,
    FieldContract,
    TypedExpressionRegistry,
    ablate_expression,
    materialize_expression,
)
from .panel18m import RawPanelStore, infer_family


WINDOWS = (6, 12, 24, 48, 72, 168, 336, 720)
HORIZONS = (1, 4)
MECHANISM_FAMILIES = (
    "OI_PRICE_DIVERGENCE",
    "OI_ACTIVITY_INTERACTION",
    "BASIS_PREMIUM_STATE",
    "TOP_GLOBAL_CROWDING",
    "ACCOUNT_POSITION_DIVERGENCE",
    "PRICE_ACTIVITY_RESPONSE",
    "CROSS_ASSET_RELATIVE_STATE",
    "STATE_REGIME_MODULATION",
)


def _payload_sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str
        ).encode("utf-8")
    ).hexdigest().upper()


def expression_from_dict(payload: Mapping[str, Any]) -> Expression:
    return Expression(
        str(payload["operator"]),
        tuple(expression_from_dict(value) for value in payload.get("inputs", [])),
        payload.get("field_id"),
        dict(payload.get("parameters", {})),
    )


def operator_path(expression: Expression) -> str:
    return expression.operator + (
        "(" + ",".join(operator_path(value) for value in expression.inputs) + ")"
        if expression.inputs
        else ""
    )


@dataclass(frozen=True, slots=True)
class Skeleton:
    skeleton_id: str
    mechanism_family: str
    variant: int
    financial_hypothesis: str
    field_roles: tuple[str, ...]
    matched_ablation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "skeleton_id": self.skeleton_id,
            "mechanism_family": self.mechanism_family,
            "variant": self.variant,
            "financial_hypothesis": self.financial_hypothesis,
            "field_roles": list(self.field_roles),
            "field_family_constraints": list(self.field_roles),
            "operator_DAG": _variant_operator(self.mechanism_family, self.variant),
            "unit_signature": "typed registry validated",
            "observable_lag": "maximum raw-input lag",
            "warm_up": "maximum rolling window and 168h dynamic-universe minimum",
            "eligible_universe_rule": "point-in-time observed, required fields finite, no future survival filter",
            "matched_ablation": self.matched_ablation,
            "maximum_depth": 4,
        }


@dataclass(frozen=True, slots=True)
class CandidateSpec:
    candidate_id: str
    skeleton_id: str
    mechanism_family: str
    expression: Expression
    control: Expression
    horizon_hours: int
    mapping_id: str
    raw_fields: tuple[str, ...]
    field_families: tuple[str, ...]
    rolling_windows: tuple[int, ...]
    expression_depth: int
    operator_path: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "skeleton_id": self.skeleton_id,
            "mechanism_family": self.mechanism_family,
            "expression": self.expression.canonical_dict(),
            "control": self.control.canonical_dict(),
            "horizon_hours": self.horizon_hours,
            "mapping_id": self.mapping_id,
            "raw_fields": list(self.raw_fields),
            "field_families": list(self.field_families),
            "rolling_windows": list(self.rolling_windows),
            "expression_depth": self.expression_depth,
            "operator_path": self.operator_path,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "CandidateSpec":
        return cls(
            str(payload["candidate_id"]),
            str(payload["skeleton_id"]),
            str(payload["mechanism_family"]),
            expression_from_dict(payload["expression"]),
            expression_from_dict(payload["control"]),
            int(payload["horizon_hours"]),
            str(payload["mapping_id"]),
            tuple(payload["raw_fields"]),
            tuple(payload["field_families"]),
            tuple(int(value) for value in payload["rolling_windows"]),
            int(payload["expression_depth"]),
            str(payload["operator_path"]),
        )


def skeleton_registry() -> tuple[Skeleton, ...]:
    hypotheses = {
        "OI_PRICE_DIVERGENCE": "Open-interest change unsupported by price response identifies crowded or fragile positioning.",
        "OI_ACTIVITY_INTERACTION": "Open-interest state has different meaning when participation or quote activity changes.",
        "BASIS_PREMIUM_STATE": "Persistent or transitioning basis changes the interpretation of subsequent price response.",
        "TOP_GLOBAL_CROWDING": "Top-account positioning relative to the global account population measures crowding asymmetry.",
        "ACCOUNT_POSITION_DIVERGENCE": "Account and position ratios diverge when participant counts and capital concentration disagree.",
        "PRICE_ACTIVITY_RESPONSE": "Weak price response to high activity can indicate absorption or exhaustion without claiming native order flow.",
        "CROSS_ASSET_RELATIVE_STATE": "An asset-local state is informative only relative to the contemporaneously eligible market cross-section.",
        "STATE_REGIME_MODULATION": "Market or maturity state modulates an otherwise local observable mechanism.",
    }
    roles = {
        "OI_PRICE_DIVERGENCE": ("oi_change", "price_return"),
        "OI_ACTIVITY_INTERACTION": ("oi", "activity"),
        "BASIS_PREMIUM_STATE": ("basis", "price_return"),
        "TOP_GLOBAL_CROWDING": ("top_account", "global_account"),
        "ACCOUNT_POSITION_DIVERGENCE": ("position", "account"),
        "PRICE_ACTIVITY_RESPONSE": ("price_return", "activity"),
        "CROSS_ASSET_RELATIVE_STATE": ("local", "market_context"),
        "STATE_REGIME_MODULATION": ("payload", "state"),
    }
    ablations = {
        "OI_PRICE_DIVERGENCE": "divergence to one component axis",
        "OI_ACTIVITY_INTERACTION": "interaction to single-axis payload",
        "BASIS_PREMIUM_STATE": "basis relation to one component axis",
        "TOP_GLOBAL_CROWDING": "top-global relation to top axis",
        "ACCOUNT_POSITION_DIVERGENCE": "account-position relation to one axis",
        "PRICE_ACTIVITY_RESPONSE": "response interaction to price axis",
        "CROSS_ASSET_RELATIVE_STATE": "cross-asset relative to asset-local payload",
        "STATE_REGIME_MODULATION": "state modulation or gate to unmodulated payload",
    }
    return tuple(
        Skeleton(
            f"{family.lower()}_v{variant}",
            family,
            variant,
            hypotheses[family],
            roles[family],
            ablations[family],
        )
        for family in MECHANISM_FAMILIES
        for variant in range(1, 6)
    )


def _variant_operator(family: str, variant: int) -> str:
    table = {
        "OI_PRICE_DIVERGENCE": ("NormalizedDifference", "SafeSub", "RatioInteraction", "Residual", "SafeMul"),
        "OI_ACTIVITY_INTERACTION": ("SafeMul", "SafeDiv", "RatioInteraction", "NormalizedDifference", "Residual"),
        "BASIS_PREMIUM_STATE": ("StateModulation", "SafeMul", "NormalizedDifference", "SafeSub", "RatioInteraction"),
        "TOP_GLOBAL_CROWDING": ("SafeSub", "NormalizedDifference", "Residual", "RatioInteraction", "SafeMul"),
        "ACCOUNT_POSITION_DIVERGENCE": ("NormalizedDifference", "SafeSub", "Residual", "RatioInteraction", "SafeMul"),
        "PRICE_ACTIVITY_RESPONSE": ("SafeDiv", "SafeMul", "RatioInteraction", "NormalizedDifference", "Residual"),
        "CROSS_ASSET_RELATIVE_STATE": ("CrossAssetRelative",) * 5,
        "STATE_REGIME_MODULATION": ("ConditionGate", "StateModulation", "SafeMul", "RatioInteraction", "ConditionGate"),
    }
    return table[family][variant - 1]


def _field_roles(contracts: Sequence[FieldContract]) -> dict[str, list[str]]:
    fields = [item.field_id for item in contracts]
    families = {field: infer_family(field) for field in fields}
    role_map = {
        "oi_change": [field for field in fields if families[field].startswith("open_interest") and ("change" in field or "zscore" in field)],
        "oi": [field for field in fields if families[field].startswith("open_interest")],
        "price_return": [field for field in fields if families[field] == "price_return"],
        "activity": [field for field in fields if families[field] == "quote_volume_activity"],
        "basis": [field for field in fields if families[field] == "basis_premium"],
        "top_account": [field for field in fields if field.startswith("top_long_short_account")],
        "global_account": [field for field in fields if field.startswith("global_long_short_account")],
        "position": [field for field in fields if families[field] in {"position_crowding", "account_position_divergence"}],
        "account": [field for field in fields if families[field] in {"account_crowding", "account_position_divergence"}],
        "state": [field for field in fields if families[field] in {"listing_age_context", "cross_asset_market_state", "funding"}],
    }
    role_map["local"] = [field for field in fields if families[field] not in {"price_level", "listing_age_context", "cross_asset_market_state"}]
    role_map["market_context"] = role_map["local"]
    role_map["payload"] = [field for field in role_map["local"] if families[field] != "funding"]
    for role, values in role_map.items():
        if not values:
            raise ValueError(f"admitted field registry cannot satisfy skeleton role: {role}")
    return role_map


def _normalized(
    field: str, window: int, *, mode: str, cross: bool = False
) -> Expression:
    if mode not in {"RollingZScore", "VolatilityScale", "HistoricalPercentile"}:
        raise ValueError(f"unsupported normalized representation: {mode}")
    node = Expression(mode, (Expression.raw(field),), parameters={"window": window})
    return Expression("CrossSectionalRobustZScore", (node,)) if cross else node


def _state_expression(field: str, window: int) -> Expression:
    family = infer_family(field)
    if family == "cross_asset_market_state":
        return Expression(
            "RollingZScore", (Expression.raw(field),), parameters={"window": window}
        )
    if family == "listing_age_context":
        return Expression("CrossSectionalRobustZScore", (Expression.raw(field),))
    return Expression(
        "RollingZScore", (Expression.raw(field),), parameters={"window": window}
    )


def _build_expression(
    skeleton: Skeleton,
    *,
    left_field: str,
    right_field: str,
    left_window: int,
    right_window: int,
    beta: float,
    left_normalizer: str,
    right_normalizer: str,
) -> Expression:
    left = _normalized(left_field, left_window, mode=left_normalizer)
    right = _normalized(right_field, right_window, mode=right_normalizer)
    operator = _variant_operator(skeleton.mechanism_family, skeleton.variant)
    if skeleton.mechanism_family == "CROSS_ASSET_RELATIVE_STATE":
        # Only the relation itself consumes the contemporaneous eligible cross-section.
        return Expression("CrossAssetRelative", (left, right))
    if skeleton.mechanism_family == "STATE_REGIME_MODULATION":
        state = _state_expression(right_field, right_window)
        if operator == "ConditionGate":
            return Expression(operator, (left, state), parameters={"threshold": 0.0})
        return Expression(operator, (left, state))
    if operator == "Residual":
        return Expression(operator, (left, right), parameters={"beta": beta})
    if operator == "StateModulation":
        state = _state_expression(right_field, right_window)
        return Expression(operator, (left, state))
    return Expression(operator, (left, right))


def generate_candidate(
    registry: TypedExpressionRegistry,
    *,
    skeleton: Skeleton,
    rng: random.Random,
    roles: Mapping[str, Sequence[str]] | None = None,
) -> CandidateSpec:
    roles = roles or _field_roles(tuple(registry.fields.values()))
    left_field = rng.choice(roles[skeleton.field_roles[0]])
    right_options = roles[skeleton.field_roles[1]]
    distinct = [field for field in right_options if field != left_field]
    right_field = rng.choice(distinct or right_options)
    left_window = rng.choice(WINDOWS)
    right_window = rng.choice(WINDOWS)
    beta = rng.choice((-1.0, -0.5, 0.5, 1.0))
    left_normalizer = rng.choice(("RollingZScore", "VolatilityScale", "HistoricalPercentile"))
    right_normalizer = rng.choice(("RollingZScore", "VolatilityScale", "HistoricalPercentile"))
    expression = _build_expression(
        skeleton,
        left_field=left_field,
        right_field=right_field,
        left_window=left_window,
        right_window=right_window,
        beta=beta,
        left_normalizer=left_normalizer,
        right_normalizer=right_normalizer,
    )
    assurance = registry.validate(expression)
    control = ablate_expression(expression)
    control_assurance = registry.validate(control)
    if assurance.raw_fields != control_assurance.raw_fields:
        raise AssertionError("matched control changed the raw-input contract")
    horizon = rng.choice(HORIZONS)
    payload = {
        "skeleton_id": skeleton.skeleton_id,
        "expression": expression.canonical_dict(),
        "control": control.canonical_dict(),
        "horizon_hours": horizon,
        "mapping_id": CROSS_SECTIONAL_ZERO_NET,
    }
    candidate_id = _payload_sha(payload)
    raw_fields = assurance.raw_fields
    return CandidateSpec(
        candidate_id,
        skeleton.skeleton_id,
        skeleton.mechanism_family,
        expression,
        control,
        horizon,
        CROSS_SECTIONAL_ZERO_NET,
        raw_fields,
        tuple(infer_family(field) for field in raw_fields),
        assurance.rolling_windows,
        assurance.depth,
        operator_path(expression),
    )


def generate_structural_pool(
    registry: TypedExpressionRegistry,
    *,
    attempts: int,
    seed: int,
    retain: int = 60000,
) -> tuple[list[CandidateSpec], dict[str, Any]]:
    if attempts < 200000:
        raise ValueError("expressivity audit requires at least 200,000 attempts")
    skeletons = skeleton_registry()
    roles = _field_roles(tuple(registry.fields.values()))
    rng = random.Random(seed)
    exact: set[str] = set()
    retained: list[CandidateSpec] = []
    legal = 0
    failures: dict[str, int] = {}
    arities: list[int] = []
    started = time.perf_counter()
    for attempt in range(attempts):
        skeleton = skeletons[attempt % len(skeletons)]
        try:
            candidate = generate_candidate(registry, skeleton=skeleton, rng=rng, roles=roles)
        except (ValueError, AssertionError) as error:
            token = type(error).__name__ + ":" + str(error)
            failures[token] = failures.get(token, 0) + 1
            continue
        legal += 1
        arities.append(len(candidate.raw_fields))
        exact_identity = candidate.expression.expression_id
        if exact_identity in exact:
            continue
        exact.add(exact_identity)
        if len(retained) < retain:
            retained.append(candidate)
    summary = {
        "proposal_attempts": attempts,
        "grammar_legal": legal,
        "exact_unique": len(exact),
        "distinct_skeletons": len({item.skeleton_id for item in retained}),
        "median_field_arity": float(statistics.median(arities)) if arities else 0.0,
        "cross_field_interaction_rate": float(np.mean(np.asarray(arities) >= 2)) if arities else 0.0,
        "retained_for_numeric_audit": len(retained),
        "rejections": failures,
        "elapsed_seconds": time.perf_counter() - started,
    }
    return retained, summary


def _array_identity(values: np.ndarray, *, ranks: bool = False) -> str:
    array = np.asarray(values, dtype=float)
    if ranks:
        array = np.apply_along_axis(
            lambda column: np.where(
                np.isfinite(column),
                np.argsort(np.argsort(np.where(np.isfinite(column), column, np.inf))),
                -1,
            ),
            0,
            array,
        )
    quantized = np.nan_to_num(np.round(array, 6), nan=9.87654321e37).astype("<f4")
    return hashlib.sha256(quantized.tobytes(order="C")).hexdigest().upper()


def _rank_behavior(values: np.ndarray) -> np.ndarray:
    ranked = rankdata(values, axis=0, method="average", nan_policy="omit")
    count = np.isfinite(values).sum(axis=0)
    denominator = np.maximum(count - 1, 1)
    return (ranked - 1.0) / denominator[None, :]


def audit_numeric_expressivity(
    *,
    store: RawPanelStore,
    registry: TypedExpressionRegistry,
    candidates: Sequence[CandidateSpec],
    structural: Mapping[str, Any],
    maximum_candidates: int = 50000,
) -> dict[str, Any]:
    sample = list(candidates[:maximum_candidates])
    if not sample:
        raise ValueError("numeric expressivity audit has no candidates")
    probe_start = min(168, max(0, store.shape[1] - 1))
    time_slice = slice(probe_start, min(probe_start + 1008, store.shape[1]))
    base = np.asarray(store.base_eligible()[:, time_slice], dtype=bool)
    asset_indices = np.argsort(base.sum(axis=1), kind="mergesort")[-min(12, store.shape[0]) :]
    eligible = base[asset_indices]
    probe_fields = {
        field: np.asarray(store.field(field)[asset_indices, time_slice], dtype=float)
        for field in sorted({name for candidate in sample for name in candidate.raw_fields})
    }
    numeric: set[str] = set()
    ranks: set[str] = set()
    behaviors: set[str] = set()
    controls_valid = 0
    failures: dict[str, int] = {}
    attempted_by_skeleton: dict[str, int] = {}
    valid_by_skeleton: dict[str, int] = {}
    failures_by_skeleton: dict[str, dict[str, int]] = {}
    mapping = DEFAULT_MAPPING_CONTRACTS[CROSS_SECTIONAL_ZERO_NET]
    leaf_cache: dict[str, np.ndarray] = {}
    checkpoint_path = store.cache_root / "expressivity_checkpoint.json"
    checkpoint_identity = _payload_sha(
        {
            "candidate_count": len(sample),
            "first_candidate": sample[0].candidate_id,
            "last_candidate": sample[-1].candidate_id,
            "probe_start": probe_start,
            "probe_hours": eligible.shape[1],
            "probe_assets": asset_indices.tolist(),
            "behavior": "CROSS_SECTIONAL_RANK_DELTA_V1",
        }
    )
    completed = 0
    if checkpoint_path.is_file():
        checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        if checkpoint.get("identity") == checkpoint_identity:
            completed = int(checkpoint.get("completed", 0))
            numeric.update(checkpoint.get("numeric", []))
            ranks.update(checkpoint.get("ranks", []))
            behaviors.update(checkpoint.get("behaviors", []))
            controls_valid = int(checkpoint.get("controls_valid", 0))
            failures.update({str(key): int(value) for key, value in checkpoint.get("failures", {}).items()})
            attempted_by_skeleton.update(
                {str(key): int(value) for key, value in checkpoint.get("attempted_by_skeleton", {}).items()}
            )
            valid_by_skeleton.update(
                {str(key): int(value) for key, value in checkpoint.get("valid_by_skeleton", {}).items()}
            )
            failures_by_skeleton.update(
                {
                    str(key): {str(reason): int(count) for reason, count in value.items()}
                    for key, value in checkpoint.get("failures_by_skeleton", {}).items()
                }
            )
    started = time.perf_counter()
    for ordinal, candidate in enumerate(sample, start=1):
        if ordinal <= completed:
            continue
        attempted_by_skeleton[candidate.skeleton_id] = (
            attempted_by_skeleton.get(candidate.skeleton_id, 0) + 1
        )
        raw = {field: probe_fields[field] for field in candidate.raw_fields}
        support = eligible.copy()
        for values in raw.values():
            support &= np.isfinite(values)
        try:
            local_cache: dict[str, np.ndarray] = {}
            for child in (*candidate.expression.inputs, *candidate.control.inputs):
                if child.expression_id not in leaf_cache:
                    leaf_cache[child.expression_id] = materialize_expression(
                        child,
                        registry=registry,
                        field_reader=raw.__getitem__,
                        eligible_mask=eligible,
                    )
                local_cache[child.expression_id] = leaf_cache[child.expression_id]
            primary = materialize_expression(
                candidate.expression,
                registry=registry,
                field_reader=raw.__getitem__,
                eligible_mask=eligible,
                candidate_cache=dict(local_cache),
            )
            control = materialize_expression(
                candidate.control,
                registry=registry,
                field_reader=raw.__getitem__,
                eligible_mask=eligible,
                candidate_cache=dict(local_cache),
            )
            primary = np.where(support, primary, np.nan)
            control = np.where(support, control, np.nan)
            primary_rank = _rank_behavior(primary)
            control_rank = _rank_behavior(control)
            if np.allclose(primary_rank, control_rank, equal_nan=True, atol=0.0, rtol=0.0):
                raise ValueError("CONTROL_BEHAVIOR_EQUALS_PRIMARY")
            numeric.add(_array_identity(primary))
            ranks.add(_array_identity(primary_rank))
            behavior = primary_rank - control_rank
            behaviors.add(_array_identity(behavior))
            controls_valid += 1
            valid_by_skeleton[candidate.skeleton_id] = (
                valid_by_skeleton.get(candidate.skeleton_id, 0) + 1
            )
        except (ValueError, FloatingPointError) as error:
            token = str(error)
            failures[token] = failures.get(token, 0) + 1
            local = failures_by_skeleton.setdefault(candidate.skeleton_id, {})
            local[token] = local.get(token, 0) + 1
        if ordinal % 5000 == 0:
            checkpoint_path.write_text(
                json.dumps(
                    {
                        "identity": checkpoint_identity,
                        "completed": ordinal,
                        "numeric": sorted(numeric),
                        "ranks": sorted(ranks),
                        "behaviors": sorted(behaviors),
                        "controls_valid": controls_valid,
                        "failures": failures,
                        "attempted_by_skeleton": attempted_by_skeleton,
                        "valid_by_skeleton": valid_by_skeleton,
                        "failures_by_skeleton": failures_by_skeleton,
                    },
                    sort_keys=True,
                ),
                encoding="utf-8",
            )
            print(
                json.dumps(
                    {
                        "event": "18m_expressivity_progress",
                        "evaluated": ordinal,
                        "numeric_unique": len(numeric),
                        "behavior_unique": len(behaviors),
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
    evaluated = len(sample)
    exact_unique = int(structural["exact_unique"])
    behavior_ratio = len(behaviors) / max(1, evaluated)
    control_rate = controls_valid / max(1, evaluated)
    gates = {
        "distinct_skeletons": int(structural["distinct_skeletons"]) >= 40,
        "median_field_arity": float(structural["median_field_arity"]) >= 2.0,
        "cross_field_interaction_rate": float(structural["cross_field_interaction_rate"]) >= 0.60,
        "exact_unique": exact_unique >= 50000,
        "full_generation_exact_unique": exact_unique >= 100000,
        "behavior_unique_over_audited_exact": behavior_ratio >= 0.30,
        "behavior_diverse_target": len(behaviors) >= 25000,
        "matched_control_valid_rate": control_rate >= 0.90,
    }
    if not gates["distinct_skeletons"] or not gates["median_field_arity"]:
        status = "COMPOSITIONAL_GENERATOR_TEMPLATE_COLLAPSE"
    elif not gates["cross_field_interaction_rate"]:
        status = "FIELD_COMBINATION_UNDERCOVERAGE"
    elif not gates["exact_unique"] or not gates["full_generation_exact_unique"]:
        status = "COMPOSITIONAL_GENERATOR_TEMPLATE_COLLAPSE"
    elif not gates["behavior_unique_over_audited_exact"] or not gates["behavior_diverse_target"]:
        status = "SEMANTIC_ALIAS_COLLAPSE"
    elif not gates["matched_control_valid_rate"]:
        status = "MATCHED_CONTROL_CONSTRUCTION_BOTTLENECK"
    else:
        status = "PASS"
    return {
        "schema_version": 1,
        "status": status,
        "structural": dict(structural),
        "numeric_audit_candidates": evaluated,
        "numeric_unique": len(numeric),
        "rank_unique": len(ranks),
        "behavior_unique": len(behaviors),
        "behavior_unique_over_audited_exact": behavior_ratio,
        "matched_control_valid": controls_valid,
        "matched_control_valid_rate": control_rate,
        "mapping_id": CROSS_SECTIONAL_ZERO_NET,
        "mapping_hash": mapping_contract_sha256(mapping),
        "probe": {
            "assets": eligible.shape[0],
            "hours": eligible.shape[1],
            "start_coordinate": probe_start,
            "selection": "highest observed eligibility for representation audit only; never a search universe",
            "economic_evaluation": False,
            "shared_leaf_cache_entries": len(leaf_cache),
            "behavior_fingerprint": "quantized primary minus control cross-sectional rank; exact portfolio mapping is qualified in the 64-pair preflight",
        },
        "gates": gates,
        "failures": failures,
        "matched_control_by_skeleton": [
            {
                "skeleton_id": skeleton_id,
                "attempted": attempted_by_skeleton.get(skeleton_id, 0),
                "valid": valid_by_skeleton.get(skeleton_id, 0),
                "valid_rate": valid_by_skeleton.get(skeleton_id, 0)
                / max(1, attempted_by_skeleton.get(skeleton_id, 0)),
                "failures": failures_by_skeleton.get(skeleton_id, {}),
            }
            for skeleton_id in sorted(attempted_by_skeleton)
        ],
        "elapsed_seconds": time.perf_counter() - started,
    }


def skeleton_payload() -> dict[str, Any]:
    rows = [item.to_dict() for item in skeleton_registry()]
    return {
        "schema_version": 1,
        "skeleton_count": len(rows),
        "mechanism_families": list(MECHANISM_FAMILIES),
        "skeletons": rows,
        "skeleton_registry_sha256": _payload_sha(rows),
    }


__all__ = [
    "CandidateSpec",
    "HORIZONS",
    "MECHANISM_FAMILIES",
    "Skeleton",
    "audit_numeric_expressivity",
    "expression_from_dict",
    "generate_candidate",
    "generate_structural_pool",
    "operator_path",
    "skeleton_payload",
    "skeleton_registry",
]
