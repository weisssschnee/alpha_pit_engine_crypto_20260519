"""Deterministic planted-mechanism capability harness.

The harness contains no market observations.  It asks whether a small search
instrument can express, map, cost, rank, and retain known planted mechanisms
against matched structural decoys.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from types import MappingProxyType
from typing import Any, Mapping

import numpy as np

from .evaluator import CapabilityEvaluationError, evaluate_mapping_result
from .feedback import FeedbackDecision, StrictMetrics, aligned_feedback
from .mapping import (
    CROSS_SECTIONAL_ZERO_NET,
    DEFAULT_MAPPING_CONTRACTS,
    SPARSE_EVENT_OR_CARRY,
    TIME_SERIES_DIRECTIONAL_STATEFUL,
    MappingContract,
    MappingResult,
    map_portfolio,
    mapping_contract_sha256,
    turnover_decomposition,
)
from .primitives import CANONICAL_PRIMITIVES, evaluate_primitive
from .search import SUPPORTED_ALGORITHMS as ALGORITHMS, SearchOutcome, run_search


FAMILY_IDS = (
    "CROSS_SECTIONAL_RELATIVE_ALPHA",
    "MARKET_DIRECTIONAL_ALPHA",
    "PERSISTENT_LOW_TURNOVER_ALPHA",
    "SPARSE_EVENT_ALPHA",
    "STATEFUL_HOLD_ALPHA",
    "FUNDING_CARRY_ALPHA",
    "REGIME_CONDITIONED_ALPHA",
)
VARIANTS = (
    "positive",
    "matched_null",
    "wrong_lag",
    "high_gross_high_cost",
    "high_gross_high_concentration",
    "single_time_block",
    "negative_benchmark_increment",
    "mapping_mismatch",
    "primitive_alias",
)

PROPOSAL_GRAMMAR_ID = "crypto-instrument-capability-proposal-grammar-v1"


@dataclass(frozen=True, slots=True)
class ProposalGrammarRule:
    """One immutable structural production in the capability grammar.

    ``evidence_label`` is reporting metadata.  Admission is derived only from
    the remaining structural fields, so relabelling a proposal cannot turn an
    invalid lag or deprecated primitive into an admitted candidate.
    """

    role_id: str
    evidence_label: str
    signal_recipe: str
    primitive_request: str
    applied_output_lag: int
    mapping_role: str


PROPOSAL_GRAMMAR = (
    ProposalGrammarRule("CANONICAL_PLANTED", "positive", "CANONICAL", "CANONICAL", 0, "INTENDED"),
    ProposalGrammarRule("MATCHED_NULL", "matched_null", "MATCHED_NULL", "CANONICAL", 0, "INTENDED"),
    ProposalGrammarRule("WRONG_LAG", "wrong_lag", "CANONICAL_WRONG_LAG", "CANONICAL", 7, "INTENDED"),
    ProposalGrammarRule("HIGH_COST", "high_gross_high_cost", "HIGH_COST", "CANONICAL", 0, "HIGH_COST"),
    ProposalGrammarRule(
        "HIGH_CONCENTRATION",
        "high_gross_high_concentration",
        "HIGH_CONCENTRATION",
        "CANONICAL",
        0,
        "HIGH_CONCENTRATION",
    ),
    ProposalGrammarRule("SINGLE_BLOCK", "single_time_block", "SINGLE_BLOCK", "CANONICAL", 0, "INTENDED"),
    ProposalGrammarRule(
        "NEGATIVE_BENCHMARK_INCREMENT",
        "negative_benchmark_increment",
        "CANONICAL",
        "CANONICAL",
        0,
        "LOW_EXPOSURE",
    ),
    ProposalGrammarRule("MAPPING_MISMATCH", "mapping_mismatch", "CANONICAL", "CANONICAL", 0, "WRONG_MAPPING"),
    ProposalGrammarRule(
        "PRIMITIVE_ALIAS",
        "primitive_alias",
        "CANONICAL",
        "DEPRECATED_ALIAS",
        0,
        "INTENDED",
    ),
)

_GRAMMAR_BY_ROLE = MappingProxyType({rule.role_id: rule for rule in PROPOSAL_GRAMMAR})

if tuple(rule.evidence_label for rule in PROPOSAL_GRAMMAR) != VARIANTS:
    raise AssertionError("frozen proposal grammar and evidence variants diverged")
if len({rule.role_id for rule in PROPOSAL_GRAMMAR}) != len(PROPOSAL_GRAMMAR):
    raise AssertionError("proposal grammar role ids must be unique")


@dataclass(frozen=True)
class FamilyContract:
    family_id: str
    primitive_id: str
    portfolio_mapping_id: str
    window: int
    long_window: int
    threshold: float
    generator_transform: str
    planted_semantics: str


@dataclass(frozen=True, slots=True)
class ProposalContract:
    """Frozen, structural proposal handed to admission and search."""

    schema_version: int
    grammar_id: str
    grammar_identity: str
    family_id: str
    role_id: str
    evidence_label: str
    signal_recipe: str
    requested_primitive_id: str
    required_primitive_id: str
    primitive_authority: str
    applied_output_lag: int
    required_output_lag: int
    portfolio_mapping_id: str
    mapping_contract_sha256: str


@dataclass(frozen=True)
class SyntheticCase:
    family: FamilyContract
    observable: np.ndarray
    canonical_signal: np.ndarray
    target_return: np.ndarray
    benchmark_net: np.ndarray
    positive_mapping: MappingResult
    signals: Mapping[str, np.ndarray]
    contracts: Mapping[str, MappingContract]
    proposals: tuple[ProposalContract, ...]
    signals_by_grammar_identity: Mapping[str, np.ndarray]
    contracts_by_grammar_identity: Mapping[str, MappingContract]


@dataclass(frozen=True)
class CandidateEvidence:
    candidate_id: str
    family_id: str
    variant: str
    primitive_id: str
    portfolio_mapping_id: str
    mapping_contract_sha256: str
    legal: bool
    wrong_lag: bool
    primitive_alias_conflict: bool
    entered_strict: bool
    metrics: StrictMetrics
    feedback: FeedbackDecision
    evaluator_details: Mapping[str, Any]
    weight_sha256: str | None
    behavior_identity: str | None
    turnover_decomposition: Mapping[str, Any] | None
    proposal_receipt: Mapping[str, Any]
    admission_receipt: Mapping[str, Any]


FAMILY_CONTRACTS: Mapping[str, FamilyContract] = {
    "CROSS_SECTIONAL_RELATIVE_ALPHA": FamilyContract(
        "CROSS_SECTIONAL_RELATIVE_ALPHA", "Delta", CROSS_SECTIONAL_ZERO_NET,
        4, 12, 0.0, "identity", "stable cross-sectional relative trend",
    ),
    "MARKET_DIRECTIONAL_ALPHA": FamilyContract(
        "MARKET_DIRECTIONAL_ALPHA", "Slope", TIME_SERIES_DIRECTIONAL_STATEFUL,
        6, 12, 0.0, "absolute_confidence_scale", "common-mode directional trend",
    ),
    "PERSISTENT_LOW_TURNOVER_ALPHA": FamilyContract(
        "PERSISTENT_LOW_TURNOVER_ALPHA", "Persistence", TIME_SERIES_DIRECTIONAL_STATEFUL,
        6, 12, 0.0, "absolute_confidence_scale", "persistent raw-threshold state",
    ),
    "SPARSE_EVENT_ALPHA": FamilyContract(
        "SPARSE_EVENT_ALPHA", "Transition", SPARSE_EVENT_OR_CARRY,
        4, 12, 0.0, "positive_event_pulse", "sparse rising events with fixed hold",
    ),
    "STATEFUL_HOLD_ALPHA": FamilyContract(
        "STATEFUL_HOLD_ALPHA", "Duration", TIME_SERIES_DIRECTIONAL_STATEFUL,
        4, 12, 0.0, "active_confidence", "entry, hysteresis hold, explicit exit",
    ),
    "FUNDING_CARRY_ALPHA": FamilyContract(
        "FUNDING_CARRY_ALPHA", "FirstHit", SPARSE_EVENT_OR_CARRY,
        4, 12, 0.0, "positive_event_pulse", "settlement-aligned one-shot carry events",
    ),
    "REGIME_CONDITIONED_ALPHA": FamilyContract(
        "REGIME_CONDITIONED_ALPHA", "MultiScaleRelation", TIME_SERIES_DIRECTIONAL_STATEFUL,
        4, 12, 0.0, "signed_confidence", "direction conditioned on slow regime",
    ),
}


def _hash_array(values: np.ndarray) -> str:
    source = np.asarray(values, dtype=float)
    digest = hashlib.sha256()
    digest.update(np.isfinite(source).tobytes())
    digest.update(np.nan_to_num(source, nan=0.0).tobytes())
    return digest.hexdigest().upper()


def _behavior_identity(weights: np.ndarray) -> str:
    source = np.asarray(weights, dtype=float)
    active = np.abs(source) > 1e-12
    sign = np.sign(source).astype(np.int8)
    digest = hashlib.sha256(active.tobytes() + sign.tobytes()).hexdigest().upper()
    return "behavior:" + digest[:24]


def _contract(base_id: str, **changes: Any) -> MappingContract:
    base = DEFAULT_MAPPING_CONTRACTS[base_id]
    parameters = {**base.parameters, **changes}
    return MappingContract(
        base.portfolio_mapping_id,
        parameters,
        base.rebalance_cadence,
        base.hold_semantics,
        base.cost_model,
    )


def _observable(family_id: str, assets: int, periods: int) -> np.ndarray:
    time = np.arange(periods, dtype=float)
    offsets = np.linspace(-0.3, 0.3, assets)[:, None]
    if family_id == "CROSS_SECTIONAL_RELATIVE_ALPHA":
        slopes = np.linspace(-0.09, 0.09, assets)[:, None]
        return offsets + slopes * time + 0.01 * np.sin(time / 7.0)[None, :]
    if family_id == "MARKET_DIRECTIONAL_ALPHA":
        return offsets + 0.06 * time[None, :] + 0.01 * np.sin(time / 5.0)[None, :]
    if family_id == "PERSISTENT_LOW_TURNOVER_ALPHA":
        return np.ones((assets, periods), dtype=float) + offsets + 0.05 * np.sin(time / 9.0)[None, :]
    if family_id == "SPARSE_EVENT_ALPHA":
        result = np.full((assets, periods), -1.0, dtype=float)
        for index, coordinate in enumerate((4, 28, 52, 76)):
            asset = index % assets
            result[asset, coordinate : coordinate + 2] = 1.0
        return result
    if family_id == "STATEFUL_HOLD_ALPHA":
        result = np.full((assets, periods), -1.0, dtype=float)
        for start, stop in ((2, 23), (26, 47), (50, 71), (74, 95)):
            result[:, start:stop] = 1.0 + offsets
        return result
    if family_id == "FUNDING_CARRY_ALPHA":
        result = np.full((assets, periods), -1.0, dtype=float)
        for asset, coordinate in enumerate((4, 28, 52, 76)):
            result[asset, coordinate : coordinate + 2] = 1.0
        return result
    if family_id == "REGIME_CONDITIONED_ALPHA":
        direction = np.where((time // 24).astype(int) % 2 == 0, 1.0, -1.0)
        level = np.cumsum(direction * 0.08)
        return offsets + level[None, :] + 0.01 * np.sin(time / 3.0)[None, :]
    raise KeyError(family_id)


def _canonical_signal(contract: FamilyContract, observable: np.ndarray) -> np.ndarray:
    signal = evaluate_primitive(
        contract.primitive_id,
        observable,
        window=contract.window,
        long_window=contract.long_window,
        threshold=contract.threshold,
    )
    if contract.generator_transform == "identity":
        return signal
    if contract.generator_transform == "positive_event_pulse":
        return np.where(np.isfinite(signal), np.maximum(signal, 0.0), np.nan)
    if contract.generator_transform == "active_confidence":
        return np.where(np.isfinite(signal), np.where(signal > 0.0, 0.95, 0.0), np.nan)
    if contract.generator_transform == "signed_confidence":
        return np.where(np.isfinite(signal), np.sign(signal) * 0.95, np.nan)
    if contract.generator_transform == "absolute_confidence_scale":
        finite = np.abs(signal[np.isfinite(signal)])
        scale = float(np.quantile(finite, 0.90)) if finite.size else 0.0
        if scale <= 1e-12:
            return np.full(signal.shape, np.nan, dtype=float)
        return np.clip(signal / scale * 0.95, -1.0, 1.0)
    raise AssertionError(contract.generator_transform)


def _high_cost_signal(mapping_id: str, assets: int, periods: int) -> np.ndarray:
    alternating = np.where(np.arange(periods) % 2 == 0, 1.0, -1.0)
    if mapping_id == CROSS_SECTIONAL_ZERO_NET:
        base = np.linspace(-1.0, 1.0, assets)[:, None]
        return base * alternating[None, :]
    if mapping_id == TIME_SERIES_DIRECTIONAL_STATEFUL:
        return np.ones((assets, 1), dtype=float) * alternating[None, :]
    signal = np.ones((assets, 1), dtype=float) * alternating[None, :]
    return signal


def _concentrated_signal(mapping_id: str, base_signal: np.ndarray) -> np.ndarray:
    if mapping_id == CROSS_SECTIONAL_ZERO_NET:
        result = np.full(base_signal.shape, -0.2, dtype=float)
        result[0, :] = 2.0
        return result
    result = np.zeros(base_signal.shape, dtype=float)
    result[0, :] = 1.0
    return result


def _mapping_role_contracts(mapping_id: str) -> dict[str, MappingContract]:
    intended = DEFAULT_MAPPING_CONTRACTS[mapping_id]
    if mapping_id == CROSS_SECTIONAL_ZERO_NET:
        high_concentration = _contract(mapping_id, position_cap=0.50)
        low_exposure = _contract(mapping_id, gross_target=0.02, position_cap=0.004)
        wrong_mapping = DEFAULT_MAPPING_CONTRACTS[TIME_SERIES_DIRECTIONAL_STATEFUL]
        high_cost = intended
    elif mapping_id == TIME_SERIES_DIRECTIONAL_STATEFUL:
        high_concentration = _contract(mapping_id, maximum_position=0.50)
        low_exposure = _contract(mapping_id, maximum_position=0.01, gross_cap=0.06)
        wrong_mapping = DEFAULT_MAPPING_CONTRACTS[CROSS_SECTIONAL_ZERO_NET]
        high_cost = intended
    else:
        high_concentration = _contract(mapping_id, maximum_position=0.50)
        low_exposure = _contract(mapping_id, maximum_position=0.01, gross_cap=0.06)
        wrong_mapping = DEFAULT_MAPPING_CONTRACTS[CROSS_SECTIONAL_ZERO_NET]
        high_cost = _contract(mapping_id, fixed_holding_period=1)
    return {
        "INTENDED": intended,
        "HIGH_COST": high_cost,
        "HIGH_CONCENTRATION": high_concentration,
        "LOW_EXPOSURE": low_exposure,
        "WRONG_MAPPING": wrong_mapping,
    }


def _proposal_identity_payload(
    *,
    family_id: str,
    role_id: str,
    signal_recipe: str,
    requested_primitive_id: str,
    required_primitive_id: str,
    primitive_authority: str,
    applied_output_lag: int,
    required_output_lag: int,
    mapping_contract: MappingContract,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "grammar_id": PROPOSAL_GRAMMAR_ID,
        "family_id": family_id,
        "role_id": role_id,
        "signal_recipe": signal_recipe,
        "requested_primitive_id": requested_primitive_id,
        "required_primitive_id": required_primitive_id,
        "primitive_authority": primitive_authority,
        "applied_output_lag": applied_output_lag,
        "required_output_lag": required_output_lag,
        "portfolio_mapping_id": mapping_contract.portfolio_mapping_id,
        "mapping_contract_sha256": mapping_contract_sha256(mapping_contract),
    }


def _proposal_identity(payload: Mapping[str, Any]) -> str:
    digest = hashlib.sha256(
        json.dumps(dict(payload), sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return "proposal-grammar:" + digest[:24]


def _build_proposals(
    family: FamilyContract,
    mapping_roles: Mapping[str, MappingContract],
) -> tuple[ProposalContract, ...]:
    deprecated_aliases = CANONICAL_PRIMITIVES[family.primitive_id].deprecated_aliases
    if not deprecated_aliases:
        raise AssertionError(f"{family.primitive_id} needs a frozen deprecated-alias decoy")
    proposals: list[ProposalContract] = []
    for rule in PROPOSAL_GRAMMAR:
        requested_primitive_id = (
            family.primitive_id
            if rule.primitive_request == "CANONICAL"
            else deprecated_aliases[0]
        )
        primitive_authority = (
            "CANONICAL_AUTHORITY"
            if rule.primitive_request == "CANONICAL"
            else "LEGACY_REFERENCE"
        )
        mapping_contract = mapping_roles[rule.mapping_role]
        payload = _proposal_identity_payload(
            family_id=family.family_id,
            role_id=rule.role_id,
            signal_recipe=rule.signal_recipe,
            requested_primitive_id=requested_primitive_id,
            required_primitive_id=family.primitive_id,
            primitive_authority=primitive_authority,
            applied_output_lag=rule.applied_output_lag,
            required_output_lag=0,
            mapping_contract=mapping_contract,
        )
        proposals.append(
            ProposalContract(
                schema_version=1,
                grammar_id=PROPOSAL_GRAMMAR_ID,
                grammar_identity=_proposal_identity(payload),
                family_id=family.family_id,
                role_id=rule.role_id,
                evidence_label=rule.evidence_label,
                signal_recipe=rule.signal_recipe,
                requested_primitive_id=requested_primitive_id,
                required_primitive_id=family.primitive_id,
                primitive_authority=primitive_authority,
                applied_output_lag=rule.applied_output_lag,
                required_output_lag=0,
                portfolio_mapping_id=mapping_contract.portfolio_mapping_id,
                mapping_contract_sha256=mapping_contract_sha256(mapping_contract),
            )
        )
    if len({proposal.grammar_identity for proposal in proposals}) != len(proposals):
        raise AssertionError("structural proposal identities must be unique")
    return tuple(proposals)


def build_synthetic_case(family_id: str, seed: int, assets: int = 6, periods: int = 96) -> SyntheticCase:
    if family_id not in FAMILY_CONTRACTS:
        raise KeyError(family_id)
    if periods < 48 or periods % 4:
        raise ValueError("synthetic periods must be >=48 and divisible by four")
    family = FAMILY_CONTRACTS[family_id]
    observable = _observable(family_id, assets, periods)
    canonical = _canonical_signal(family, observable)
    mapping_roles = _mapping_role_contracts(family.portfolio_mapping_id)
    proposals = _build_proposals(family, mapping_roles)
    high_cost = _high_cost_signal(family.portfolio_mapping_id, assets, periods)
    concentrated = _concentrated_signal(family.portfolio_mapping_id, canonical)
    single_block = np.zeros(canonical.shape, dtype=float)
    single_block[:, periods // 4 : periods // 2] = np.nan_to_num(
        canonical[:, periods // 4 : periods // 2], nan=0.0
    )
    wrong_lag = np.full(canonical.shape, np.nan, dtype=float)
    lag = 7
    wrong_lag[:, lag:] = canonical[:, :-lag]
    rng = np.random.default_rng(seed + sum(ord(character) for character in family_id))
    matched_null = rng.normal(0.0, 0.01, size=canonical.shape)
    signals_by_recipe = {
        "CANONICAL": canonical,
        "MATCHED_NULL": matched_null,
        "CANONICAL_WRONG_LAG": wrong_lag,
        "HIGH_COST": high_cost,
        "HIGH_CONCENTRATION": concentrated,
        "SINGLE_BLOCK": single_block,
    }
    signals = {
        rule.evidence_label: signals_by_recipe[rule.signal_recipe]
        for rule in PROPOSAL_GRAMMAR
    }
    contracts = {
        rule.evidence_label: mapping_roles[rule.mapping_role]
        for rule in PROPOSAL_GRAMMAR
    }
    signals_by_identity = {
        proposal.grammar_identity: signals_by_recipe[proposal.signal_recipe]
        for proposal in proposals
    }
    contracts_by_identity = {
        proposal.grammar_identity: mapping_roles[_GRAMMAR_BY_ROLE[proposal.role_id].mapping_role]
        for proposal in proposals
    }
    positive_mapping = map_portfolio(canonical, mapping_roles["INTENDED"])
    high_cost_mapping = map_portfolio(high_cost, mapping_roles["HIGH_COST"])
    concentrated_mapping = map_portfolio(concentrated, mapping_roles["HIGH_CONCENTRATION"])
    if family.portfolio_mapping_id == SPARSE_EVENT_OR_CARRY:
        alpha, beta, gamma = 0.050, 0.020, 0.020
    else:
        alpha, beta, gamma = 0.030, 0.020, 0.020
    time = np.arange(periods, dtype=float)
    noise = 0.00001 * np.sin((np.arange(assets)[:, None] + 1.0) * (time[None, :] + 1.0) / 11.0)
    target = (
        alpha * positive_mapping.weights
        + beta * high_cost_mapping.weights
        + gamma * concentrated_mapping.weights
        + noise
    )
    benchmark = np.full(periods, 0.00050, dtype=float)
    return SyntheticCase(
        family, observable, canonical, target, benchmark, positive_mapping,
        signals, contracts, proposals, signals_by_identity, contracts_by_identity,
    )


def _dummy_metrics() -> StrictMetrics:
    return StrictMetrics(*(float("nan") for _ in range(9)), finite=False)


def _proposal_receipt(proposal: ProposalContract) -> dict[str, Any]:
    return {
        "schema_version": proposal.schema_version,
        "grammar_id": proposal.grammar_id,
        "grammar_identity": proposal.grammar_identity,
        "identity_kind": "STRUCTURAL_SPEC_SHA256_PREFIX",
        "identity_excludes_evidence_label": True,
        "family_id": proposal.family_id,
        "role_id": proposal.role_id,
        "evidence_label": proposal.evidence_label,
        "signal_recipe": proposal.signal_recipe,
        "requested_primitive_id": proposal.requested_primitive_id,
        "required_primitive_id": proposal.required_primitive_id,
        "primitive_authority": proposal.primitive_authority,
        "applied_output_lag": proposal.applied_output_lag,
        "required_output_lag": proposal.required_output_lag,
        "portfolio_mapping_id": proposal.portfolio_mapping_id,
        "mapping_contract_sha256": proposal.mapping_contract_sha256,
    }


def _admission_receipt(
    case: SyntheticCase,
    proposal: ProposalContract,
) -> tuple[dict[str, Any], MappingContract | None]:
    rule = _GRAMMAR_BY_ROLE.get(proposal.role_id)
    contract = case.contracts_by_grammar_identity.get(proposal.grammar_identity)
    identity_payload = None
    if contract is not None:
        identity_payload = _proposal_identity_payload(
            family_id=proposal.family_id,
            role_id=proposal.role_id,
            signal_recipe=proposal.signal_recipe,
            requested_primitive_id=proposal.requested_primitive_id,
            required_primitive_id=proposal.required_primitive_id,
            primitive_authority=proposal.primitive_authority,
            applied_output_lag=proposal.applied_output_lag,
            required_output_lag=proposal.required_output_lag,
            mapping_contract=contract,
        )
    identity_valid = bool(
        identity_payload is not None
        and proposal.grammar_identity == _proposal_identity(identity_payload)
    )
    grammar_member = bool(
        rule is not None
        and proposal.grammar_id == PROPOSAL_GRAMMAR_ID
        and proposal.schema_version == 1
        and proposal.family_id == case.family.family_id
        and proposal.signal_recipe == rule.signal_recipe
        and proposal.applied_output_lag == rule.applied_output_lag
        and proposal.required_output_lag == 0
        and proposal.required_primitive_id == case.family.primitive_id
        and contract is not None
        and proposal.portfolio_mapping_id == contract.portfolio_mapping_id
        and proposal.mapping_contract_sha256 == mapping_contract_sha256(contract)
    )
    requested_is_canonical = proposal.requested_primitive_id in CANONICAL_PRIMITIVES
    primitive_exact = bool(
        requested_is_canonical
        and proposal.primitive_authority == "CANONICAL_AUTHORITY"
        and proposal.requested_primitive_id == proposal.required_primitive_id
    )
    deprecated_refs = CANONICAL_PRIMITIVES[proposal.required_primitive_id].deprecated_aliases
    primitive_resolution = (
        "CANONICAL_AUTHORITY"
        if primitive_exact
        else "DEPRECATED_ALIAS_REFERENCE"
        if proposal.requested_primitive_id in deprecated_refs
        else "UNKNOWN_OR_WRONG_PRIMITIVE"
    )
    lag_exact = proposal.applied_output_lag == proposal.required_output_lag
    blockers: list[str] = []
    if not grammar_member or not identity_valid:
        blockers.append("INVALID_PROPOSAL_CONTRACT")
    if not lag_exact:
        blockers.append("WRONG_LAG")
    if not primitive_exact:
        blockers.append("PRIMITIVE_ALIAS_CONFLICT")
    receipt = {
        "result": "PASS" if not blockers else "BLOCKED",
        "blockers": blockers,
        "grammar": {
            "result": "PASS" if grammar_member and identity_valid else "FAIL",
            "member": grammar_member,
            "identity_valid": identity_valid,
        },
        "lag_receipt": {
            "result": "PASS" if lag_exact else "FAIL",
            "required_output_lag": proposal.required_output_lag,
            "applied_output_lag": proposal.applied_output_lag,
        },
        "primitive_receipt": {
            "result": "PASS" if primitive_exact else "FAIL",
            "authority": primitive_resolution,
            "declared_authority": proposal.primitive_authority,
            "requested_primitive_id": proposal.requested_primitive_id,
            "required_primitive_id": proposal.required_primitive_id,
            "deprecated_alias_reference": proposal.requested_primitive_id in deprecated_refs,
        },
        "mapping_receipt": {
            "result": "PASS" if contract is not None else "FAIL",
            "portfolio_mapping_id": proposal.portfolio_mapping_id,
            "mapping_contract_sha256": proposal.mapping_contract_sha256,
        },
    }
    return receipt, contract


def evaluate_proposal(case: SyntheticCase, proposal: ProposalContract) -> CandidateEvidence:
    """Evaluate a structural proposal; reporting labels never control admission."""

    proposal_receipt = _proposal_receipt(proposal)
    admission_receipt, contract = _admission_receipt(case, proposal)
    legal = admission_receipt["grammar"]["result"] == "PASS"
    wrong_lag = admission_receipt["lag_receipt"]["result"] != "PASS"
    alias_conflict = admission_receipt["primitive_receipt"]["result"] != "PASS"
    mapping_present = admission_receipt["mapping_receipt"]["result"] == "PASS"
    if not legal or wrong_lag or alias_conflict or not mapping_present:
        metrics = _dummy_metrics()
        feedback = aligned_feedback(
            metrics,
            legal=legal,
            mapping_present=mapping_present,
            wrong_lag=wrong_lag,
            primitive_alias_conflict=alias_conflict,
        )
        return CandidateEvidence(
            proposal.grammar_identity,
            case.family.family_id,
            proposal.evidence_label,
            proposal.requested_primitive_id,
            proposal.portfolio_mapping_id,
            proposal.mapping_contract_sha256,
            legal,
            wrong_lag,
            alias_conflict,
            False,
            metrics,
            feedback,
            {"admission": feedback.reason, "strict_evaluator_called": False},
            None,
            None,
            None,
            proposal_receipt,
            admission_receipt,
        )
    assert contract is not None
    try:
        signal = case.signals_by_grammar_identity[proposal.grammar_identity]
        mapped = map_portfolio(signal, contract)
        metrics, details = evaluate_mapping_result(mapped, case.target_return, case.benchmark_net)
        feedback = aligned_feedback(
            metrics,
            legal=True,
            mapping_present=True,
            wrong_lag=False,
            primitive_alias_conflict=False,
        )
        return CandidateEvidence(
            proposal.grammar_identity, case.family.family_id, proposal.evidence_label,
            proposal.requested_primitive_id, contract.portfolio_mapping_id,
            mapped.contract_sha256, True, False, False,
            True, metrics, feedback, details, _hash_array(mapped.weights),
            _behavior_identity(mapped.weights),
            turnover_decomposition(signal, mapped.weights),
            proposal_receipt,
            admission_receipt,
        )
    except (CapabilityEvaluationError, ValueError) as error:
        metrics = _dummy_metrics()
        feedback = aligned_feedback(
            metrics,
            legal=False,
            mapping_present=True,
            wrong_lag=False,
            primitive_alias_conflict=False,
        )
        return CandidateEvidence(
            proposal.grammar_identity, case.family.family_id, proposal.evidence_label,
            proposal.requested_primitive_id, contract.portfolio_mapping_id,
            mapping_contract_sha256(contract), False,
            False, False, True, metrics, feedback,
            {"evaluation_error": str(error), "strict_evaluator_called": True},
            None, None, None, proposal_receipt, admission_receipt,
        )


def evaluate_candidate(case: SyntheticCase, variant: str) -> CandidateEvidence:
    """Compatibility lookup by evidence label; evaluation uses structural spec."""

    proposals = [proposal for proposal in case.proposals if proposal.evidence_label == variant]
    if len(proposals) != 1:
        raise KeyError(variant)
    return evaluate_proposal(case, proposals[0])


def _serialize_metrics(metrics: StrictMetrics) -> dict[str, Any]:
    payload = asdict(metrics)
    for key, value in list(payload.items()):
        if isinstance(value, float) and not np.isfinite(value):
            payload[key] = None
    return payload


def _serialize_feedback(decision: FeedbackDecision) -> dict[str, Any]:
    return {
        "blocked": decision.blocked,
        "feasible": decision.feasible,
        "violations": list(decision.violations),
        "distance": decision.distance,
        "sort_key": list(decision.sort_key),
        "reason": decision.reason,
    }


def serialize_candidate(row: CandidateEvidence) -> dict[str, Any]:
    return {
        "candidate_id": row.candidate_id,
        "family_id": row.family_id,
        "variant": row.variant,
        "primitive_id": row.primitive_id,
        "portfolio_mapping_id": row.portfolio_mapping_id,
        "mapping_contract_sha256": row.mapping_contract_sha256,
        "legal": row.legal,
        "wrong_lag": row.wrong_lag,
        "primitive_alias_conflict": row.primitive_alias_conflict,
        "entered_strict": row.entered_strict,
        "metrics": _serialize_metrics(row.metrics),
        "feedback": _serialize_feedback(row.feedback),
        "evaluator_details": row.evaluator_details,
        "weight_sha256": row.weight_sha256,
        "behavior_identity": row.behavior_identity,
        "turnover_decomposition": row.turnover_decomposition,
        "proposal_receipt": row.proposal_receipt,
        "admission_receipt": row.admission_receipt,
    }


def _reason_set(mapped: MappingResult) -> set[str]:
    return {reason for coordinate in mapped.transition_reasons for reason in coordinate}


def _mapping_preservation_receipt(case: SyntheticCase) -> dict[str, Any]:
    """Check the information each family claims to preserve, not mere activity."""

    weights = np.asarray(case.positive_mapping.weights, dtype=float)
    signal = np.asarray(case.canonical_signal, dtype=float)
    active = np.abs(weights) > 1e-12
    reasons = _reason_set(case.positive_mapping)
    family_id = case.family.family_id
    checks: dict[str, bool]
    details: dict[str, Any]

    if family_id == "CROSS_SECTIONAL_RELATIVE_ALPHA":
        active_coordinates = np.any(active, axis=0)
        alignment = np.nansum(weights * signal, axis=0)
        checks = {
            "zero_net_on_active_coordinates": bool(
                np.all(np.abs(np.sum(weights[:, active_coordinates], axis=0)) <= 1e-12)
            ),
            "positive_cross_sectional_order_alignment": bool(
                active_coordinates.any() and np.all(alignment[active_coordinates] > 0.0)
            ),
            "multiple_assets_represented": bool(
                np.all(np.sum(active[:, active_coordinates], axis=0) >= 3)
            ),
        }
        details = {"active_coordinates": int(np.sum(active_coordinates))}
        check_id = "CROSS_SECTIONAL_ORDER_AND_ZERO_NET_PRESERVED"
    elif family_id == "MARKET_DIRECTIONAL_ALPHA":
        checks = {
            "common_mode_not_demeaned": bool(case.positive_mapping.diagnostics["common_mode_preserved"]),
            "direction_sign_preserved": bool(np.all(np.sign(weights[active]) == np.sign(signal[active]))),
            "directional_exposure_exists": bool(np.any(np.abs(np.sum(weights, axis=0)) > 1e-12)),
        }
        details = {"active_weight_coordinates": int(np.sum(active))}
        check_id = "COMMON_MODE_DIRECTION_PRESERVED"
    elif family_id == "PERSISTENT_LOW_TURNOVER_ALPHA":
        full_l1_turnover = float(
            np.sum(np.abs(weights[:, 0])) + np.sum(np.abs(np.diff(weights, axis=1)))
        )
        checks = {
            "persistent_direction_preserved": bool(np.all(np.sign(weights[active]) == np.sign(signal[active]))),
            "hold_state_observed": "HOLD" in reasons,
            "only_initial_establishment_turnover": full_l1_turnover <= 1.0 + 1e-12,
        }
        details = {"full_l1_turnover": full_l1_turnover}
        check_id = "PERSISTENT_STATE_AND_LOW_TURNOVER_PRESERVED"
    elif family_id in {"SPARSE_EVENT_ALPHA", "FUNDING_CARRY_ALPHA"}:
        diagnostics = case.positive_mapping.diagnostics
        entry_count = int(diagnostics["event_entry_count"])
        opportunity_count = int(diagnostics["event_opportunity_count"])
        hold_period = int(case.contracts["positive"].parameters["fixed_holding_period"])
        checks = {
            "all_eligible_events_entered": entry_count > 0 and entry_count == opportunity_count,
            "singleton_events_preserved": bool(diagnostics["singleton_preserved"]),
            "fixed_holding_period_preserved": int(np.sum(active)) == entry_count * hold_period,
            "explicit_exit_observed": "EXPLICIT_HOLD_EXIT" in reasons,
        }
        details = {
            "entry_count": entry_count,
            "opportunity_count": opportunity_count,
            "fixed_holding_period": hold_period,
        }
        check_id = (
            "SPARSE_EVENT_ENTRY_HOLD_EXIT_PRESERVED"
            if family_id == "SPARSE_EVENT_ALPHA"
            else "SETTLEMENT_CARRY_ENTRY_HOLD_EXIT_PRESERVED"
        )
    elif family_id == "STATEFUL_HOLD_ALPHA":
        active_coordinates = np.any(active, axis=0)
        repeated_hold = bool(np.any(active_coordinates[:-1] & active_coordinates[1:]))
        checks = {
            "entry_observed": "ENTRY" in reasons,
            "stateful_hold_observed": "HOLD" in reasons and repeated_hold,
            "explicit_exit_observed": "EXIT_THRESHOLD" in reasons,
            "active_direction_preserved": bool(np.all(np.sign(weights[active]) == np.sign(signal[active]))),
        }
        details = {"active_coordinates": int(np.sum(active_coordinates))}
        check_id = "STATEFUL_ENTRY_HOLD_EXIT_PRESERVED"
    elif family_id == "REGIME_CONDITIONED_ALPHA":
        active_signs = set(int(value) for value in np.unique(np.sign(weights[active])))
        checks = {
            "both_regime_directions_preserved": active_signs == {-1, 1},
            "regime_sign_alignment": bool(np.all(np.sign(weights[active]) == np.sign(signal[active]))),
            "regime_reversal_observed": "REVERSAL" in reasons,
        }
        details = {"active_weight_signs": sorted(active_signs)}
        check_id = "REGIME_DIRECTION_AND_REVERSAL_PRESERVED"
    else:  # pragma: no cover - family registry is frozen above
        raise AssertionError(f"unhandled family mapping semantics: {family_id}")

    return {
        "check_id": check_id,
        "family_id": family_id,
        "result": "PASS" if all(checks.values()) else "FAIL",
        "invariants": checks,
        "details": details,
    }


def qualify_family(family_id: str, seed: int, search_budget: int = 27) -> dict[str, Any]:
    case = build_synthetic_case(family_id, seed)
    evaluated = [evaluate_proposal(case, proposal) for proposal in case.proposals]
    candidates = {row.variant: row for row in evaluated}
    by_role = {proposal.role_id: candidates[proposal.evidence_label] for proposal in case.proposals}
    candidate_ids = [proposal.grammar_identity for proposal in case.proposals]
    by_id = {row.candidate_id: row.feedback for row in candidates.values()}
    variant_by_id = {row.candidate_id: row.variant for row in candidates.values()}
    searches: dict[str, SearchOutcome] = {
        algorithm: run_search(algorithm, candidate_ids, by_id, seed=seed, budget=search_budget)
        for algorithm in ALGORITHMS
    }
    positive = by_role["CANONICAL_PLANTED"]
    null = by_role["MATCHED_NULL"]
    mapping_preservation = _mapping_preservation_receipt(case)
    grammar_identities = {proposal.grammar_identity for proposal in case.proposals}
    checks = {
        "proposal_generated_from_frozen_grammar": bool(
            len(case.proposals) == len(PROPOSAL_GRAMMAR)
            and set(candidate_ids) == grammar_identities
            and all(row.admission_receipt["grammar"]["result"] == "PASS" for row in evaluated)
        ),
        "positive_candidate_reachable": all(positive.candidate_id in outcome.proposal_order for outcome in searches.values()),
        "positive_search_access_is_grammar_identity": bool(
            positive.candidate_id == positive.proposal_receipt["grammar_identity"]
            and all(set(outcome.proposal_order) <= grammar_identities for outcome in searches.values())
        ),
        "positive_candidate_legal": positive.legal,
        "positive_candidate_receives_finite_feedback": positive.metrics.finite,
        "positive_candidate_enters_strict_evaluation": positive.entered_strict,
        "positive_candidate_strict_feasible": positive.feedback.feasible,
        "positive_candidate_ranks_above_matched_null": positive.feedback.sort_key > null.feedback.sort_key,
        "positive_candidate_survives": all(variant_by_id[outcome.survivor_id] == "positive" for outcome in searches.values()),
        "wrong_lag_rejected_before_strict": candidates["wrong_lag"].feedback.blocked and not candidates["wrong_lag"].entered_strict,
        "high_cost_decoy_rejected_or_downgraded": candidates["high_gross_high_cost"].feedback.sort_key < positive.feedback.sort_key,
        "high_concentration_decoy_rejected_or_downgraded": candidates["high_gross_high_concentration"].feedback.sort_key < positive.feedback.sort_key,
        "single_time_block_decoy_rejected_or_downgraded": candidates["single_time_block"].feedback.sort_key < positive.feedback.sort_key,
        "negative_benchmark_increment_decoy_rejected_or_downgraded": candidates["negative_benchmark_increment"].feedback.sort_key < positive.feedback.sort_key,
        "mapping_mismatch_rejected_or_downgraded": candidates["mapping_mismatch"].feedback.sort_key < positive.feedback.sort_key,
        "primitive_alias_rejected_before_strict": candidates["primitive_alias"].feedback.blocked and not candidates["primitive_alias"].entered_strict,
        "mapping_preserves_intended_information": mapping_preservation["result"] == "PASS",
        "survivor_selected_only_from_visited_feedback": all(
            outcome.survivor_id in outcome.proposal_order for outcome in searches.values()
        ),
    }
    return {
        "family_contract": asdict(case.family),
        "proposal_grammar": {
            "grammar_id": PROPOSAL_GRAMMAR_ID,
            "frozen_rule_count": len(PROPOSAL_GRAMMAR),
            "proposal_identities": candidate_ids,
        },
        "seed": seed,
        "observable_sha256": _hash_array(case.observable),
        "canonical_signal_sha256": _hash_array(case.canonical_signal),
        "target_sha256": _hash_array(case.target_return),
        "positive_behavior_identity": _behavior_identity(case.positive_mapping.weights),
        "mapping_preservation_receipt": mapping_preservation,
        "candidates": {variant: serialize_candidate(row) for variant, row in candidates.items()},
        "searches": {algorithm: outcome.to_dict(variant_by_id) for algorithm, outcome in searches.items()},
        "qualification_checks": checks,
        "qualified": all(checks.values()),
    }


def run_qualification(seeds: tuple[int, ...] = (20260715, 20260716), search_budget: int = 27) -> dict[str, Any]:
    runs = [qualify_family(family_id, seed, search_budget) for seed in seeds for family_id in FAMILY_IDS]
    cross_seed: dict[str, Any] = {}
    for family_id in FAMILY_IDS:
        family_runs = [row for row in runs if row["family_contract"]["family_id"] == family_id]
        survivor_variants = {
            algorithm: [row["searches"][algorithm]["survivor_variant"] for row in family_runs]
            for algorithm in ALGORITHMS
        }
        exact = len({row["canonical_signal_sha256"] for row in family_runs}) == 1
        canonical = all(all(value == "positive" for value in variants) for variants in survivor_variants.values())
        behavior = len({row["positive_behavior_identity"] for row in family_runs}) == 1
        cross_seed[family_id] = {
            "exact_reproduction": exact,
            "canonical_mechanism_reproduction": canonical,
            "behavior_reproduction": behavior,
            "survivor_variants_by_algorithm": survivor_variants,
        }
    independent_hashes = {
        algorithm: {row["searches"][algorithm]["behavior_hash"] for row in runs}
        for algorithm in ALGORITHMS
    }
    all_qualified = all(row["qualified"] for row in runs)
    cross_seed_qualified = all(
        row["canonical_mechanism_reproduction"] and row["behavior_reproduction"]
        for row in cross_seed.values()
    )
    return {
        "schema_version": 1,
        "scope": "deterministic synthetic capability only; no market or sealed data",
        "seeds": list(seeds),
        "search_budget_per_family_algorithm_seed": search_budget,
        "algorithms": list(ALGORITHMS),
        "families": list(FAMILY_IDS),
        "runs": runs,
        "cross_seed_reproduction": cross_seed,
        "algorithm_behavior_hashes": {key: sorted(value) for key, value in independent_hashes.items()},
        "all_runs_qualified": all_qualified,
        "cross_seed_qualified": cross_seed_qualified,
        "qualification": "QUALIFIED" if all_qualified and cross_seed_qualified else "PARTIALLY_QUALIFIED",
    }


__all__ = [
    "CandidateEvidence",
    "FAMILY_CONTRACTS",
    "FAMILY_IDS",
    "FamilyContract",
    "PROPOSAL_GRAMMAR",
    "PROPOSAL_GRAMMAR_ID",
    "ProposalContract",
    "ProposalGrammarRule",
    "SyntheticCase",
    "VARIANTS",
    "build_synthetic_case",
    "evaluate_candidate",
    "evaluate_proposal",
    "qualify_family",
    "run_qualification",
    "serialize_candidate",
]
