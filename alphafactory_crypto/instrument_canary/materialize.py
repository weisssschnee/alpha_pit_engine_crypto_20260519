"""Authorized field representation, canonical primitive, and mapping bridge."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Callable, Mapping

import numpy as np

from alphafactory_crypto.instrument_capability.mapping import (
    DEFAULT_MAPPING_CONTRACTS,
    MappingResult,
    map_portfolio,
    mapping_contract_sha256,
)
from alphafactory_crypto.instrument_capability.primitives import (
    CANONICAL_PRIMITIVES,
    evaluate_primitive,
)

from .admission import (
    AUTHORIZATION_ID,
    CandidateAuthorizationReceipt,
    _AUTHORIZATION_RULES,
    _sha256,
    real_data_feedback_contract_payload,
)
from .evaluator import array_sha256
from .grammar import FrozenGrammar


def apply_frozen_representation(
    representation_id: str, values: np.ndarray, *, value_domain: str
) -> np.ndarray:
    """Apply one formula named by the frozen grammar representation registry."""

    source = np.asarray(values, dtype=float)
    if source.ndim != 2 or source.shape[0] == 0 or source.shape[1] == 0:
        raise ValueError("field reader must return nonempty [asset,time] values")
    _validate_value_domain(source, value_domain)
    if representation_id == "identity":
        return source.copy()

    if representation_id == "log1p_nonnegative":
        return np.log1p(source)
    elif representation_id == "log_positive":
        return np.log(np.maximum(source, 1e-12))
    elif representation_id == "signed_log1p_abs":
        return np.sign(source) * np.log1p(np.abs(source))
    elif representation_id == "atanh_clip_0_999":
        clipped = source.copy()
        clipped[source == -1.0] = -0.999
        clipped[source == 1.0] = 0.999
        return np.arctanh(clipped)
    elif representation_id == "logit_clip_1e6":
        clipped = source.copy()
        clipped[source == 0.0] = 1e-6
        clipped[source == 1.0] = 1.0 - 1e-6
        return np.log(clipped / (1.0 - clipped))
    else:
        raise ValueError(f"unknown frozen representation: {representation_id}")


def _validate_value_domain(source: np.ndarray, value_domain: str) -> None:
    if not np.isfinite(source).all():
        raise ValueError("authorized release field contains non-finite values")
    if value_domain == "NON_NEGATIVE":
        valid = source >= 0.0
    elif value_domain == "STRICT_POSITIVE":
        valid = source > 0.0
    elif value_domain == "BOUNDED_SIGNED":
        valid = (source >= -1.0) & (source <= 1.0)
    elif value_domain == "UNIT_INTERVAL":
        valid = (source >= 0.0) & (source <= 1.0)
    elif value_domain == "SIGNED":
        valid = np.ones(source.shape, dtype=bool)
    else:
        raise ValueError(f"unknown frozen value domain: {value_domain}")
    if not bool(np.all(valid)):
        raise ValueError(f"authorized release field violates {value_domain} domain")


def _endpoint_clip_count(
    representation_id: str, source: np.ndarray
) -> int:
    if representation_id == "atanh_clip_0_999":
        return int(np.count_nonzero((source == -1.0) | (source == 1.0)))
    if representation_id == "logit_clip_1e6":
        return int(np.count_nonzero((source == 0.0) | (source == 1.0)))
    return 0


def _readonly(values: np.ndarray, *, dtype: Any = float) -> np.ndarray:
    result = np.asarray(values, dtype=dtype).copy()
    result.setflags(write=False)
    return result


def _current_representation_contract(
    grammar: FrozenGrammar, receipt: CandidateAuthorizationReceipt
) -> dict[str, Any]:
    for field in grammar.field_specs:
        if field.field_id != receipt.field_id:
            continue
        for representation in field.representations:
            if representation.representation_id == receipt.representation_id:
                return {
                    "field_id": field.field_id,
                    "value_domain": field.value_domain,
                    "representation_id": representation.representation_id,
                    "formula": representation.formula,
                    "input_domain": representation.input_domain,
                    "nonlinear": representation.nonlinear,
                }
    raise ValueError("authorization receipt representation is no longer canonical")


def verify_materialization_authority(receipt: CandidateAuthorizationReceipt) -> None:
    """Recheck every executable authority before invoking a field reader."""

    if not isinstance(receipt, CandidateAuthorizationReceipt):
        raise TypeError("materialization requires CandidateAuthorizationReceipt")
    receipt.verify_integrity()
    if receipt.authorization_id != AUTHORIZATION_ID:
        raise ValueError("authorization receipt has the wrong authorization scope")

    grammar = FrozenGrammar.default()
    grammar.validate(receipt.genome)
    if receipt.grammar_contract_sha256 != grammar.contract_sha256:
        raise ValueError("authorization receipt grammar authority is stale")
    if grammar.mapping_for(receipt.genome) != receipt.mapping_id:
        raise ValueError("authorization receipt mapping is not genome-derived")

    expected_parameters = {
        "window": receipt.genome.window,
        "long_window": receipt.genome.long_window,
        "threshold": receipt.genome.threshold,
    }
    if dict(receipt.primitive_parameters) != expected_parameters:
        raise ValueError("authorization receipt primitive parameters mismatch")
    primitive = CANONICAL_PRIMITIVES.get(receipt.primitive_id)
    if primitive is None or _sha256(primitive.to_dict()) != receipt.primitive_contract_sha256:
        raise ValueError("authorization receipt primitive authority is stale")

    representation = _current_representation_contract(grammar, receipt)
    if (
        representation != dict(receipt.representation_contract)
        or _sha256(representation) != receipt.representation_contract_sha256
    ):
        raise ValueError("authorization receipt representation authority is stale")

    mapping = DEFAULT_MAPPING_CONTRACTS.get(receipt.mapping_id)
    if mapping is None or mapping_contract_sha256(mapping) != receipt.mapping_contract_sha256:
        raise ValueError("authorization receipt mapping authority is stale")
    if _sha256(dict(receipt.target_contract)) != receipt.target_contract_sha256:
        raise ValueError("authorization receipt target contract is corrupt")
    if _sha256(dict(receipt.pit_lag_contract)) != receipt.pit_lag_contract_sha256:
        raise ValueError("authorization receipt PIT/lag contract is corrupt")
    if _sha256(dict(receipt.cost_contract)) != receipt.cost_contract_sha256:
        raise ValueError("authorization receipt cost contract is corrupt")
    if (
        dict(receipt.feedback_contract) != real_data_feedback_contract_payload()
        or _sha256(dict(receipt.feedback_contract))
        != receipt.feedback_contract_sha256
    ):
        raise ValueError("authorization receipt feedback authority is stale")
    if _sha256(_AUTHORIZATION_RULES) != receipt.authorization_contract_sha256:
        raise ValueError("authorization receipt admission contract is stale")


def _evaluate_receipt_primitive(
    receipt: CandidateAuthorizationReceipt, represented_values: np.ndarray
) -> np.ndarray:
    # Omit N/A values so canonical defaults satisfy its positive-window API.
    # The canonical windowless primitive ignores those omitted defaults; its
    # threshold remains explicit whenever the frozen grammar defines one.
    parameters: dict[str, Any] = {}
    if receipt.genome.window is not None:
        parameters["window"] = receipt.genome.window
    if receipt.genome.long_window is not None:
        parameters["long_window"] = receipt.genome.long_window
    if receipt.genome.threshold is not None:
        parameters["threshold"] = receipt.genome.threshold
    return evaluate_primitive(
        receipt.primitive_id, represented_values, **parameters
    )


@dataclass(frozen=True, slots=True)
class MaterializedCandidate:
    receipt: CandidateAuthorizationReceipt
    field_values: np.ndarray
    represented_values: np.ndarray
    signal: np.ndarray
    mapped: MappingResult
    endpoint_clip_count: int
    field_array_sha256: str
    represented_array_sha256: str
    signal_array_sha256: str
    weight_array_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.receipt.candidate_id,
            "cache_key": self.receipt.cache_key,
            "field_id": self.receipt.field_id,
            "representation_id": self.receipt.representation_id,
            "primitive_id": self.receipt.primitive_id,
            "mapping_id": self.mapped.portfolio_mapping_id,
            "mapping_contract_sha256": self.mapped.contract_sha256,
            "shape": list(self.signal.shape),
            "endpoint_clip_count": self.endpoint_clip_count,
            "field_array_sha256": self.field_array_sha256,
            "represented_array_sha256": self.represented_array_sha256,
            "signal_array_sha256": self.signal_array_sha256,
            "weight_array_sha256": self.weight_array_sha256,
            "mapping_diagnostics": dict(self.mapped.diagnostics),
        }


def materialize_authorized(
    receipt: CandidateAuthorizationReceipt,
    *,
    field_reader: Callable[[str], np.ndarray],
) -> MaterializedCandidate:
    """Read exactly one authorized field and call canonical execution routes."""

    verify_materialization_authority(receipt)
    if not callable(field_reader):
        raise TypeError("field_reader must be callable")

    field_values = np.asarray(field_reader(receipt.field_id), dtype=float).copy()
    if field_values.ndim != 2 or not all(size > 0 for size in field_values.shape):
        raise ValueError("field reader must return nonempty [asset,time] values")
    represented = apply_frozen_representation(
        receipt.representation_id,
        field_values,
        value_domain=str(receipt.representation_contract["value_domain"]),
    )
    signal = _evaluate_receipt_primitive(receipt, represented)

    mapping_contract = DEFAULT_MAPPING_CONTRACTS[receipt.mapping_id]
    mapped = map_portfolio(signal, mapping_contract)
    if mapped.contract_sha256 != receipt.mapping_contract_sha256:
        raise ValueError("runtime mapping contract differs from authorization receipt")
    field_values = _readonly(field_values)
    represented = _readonly(represented)
    signal = _readonly(signal)
    mapped = MappingResult(
        portfolio_mapping_id=mapped.portfolio_mapping_id,
        contract_sha256=mapped.contract_sha256,
        weights=_readonly(mapped.weights),
        feasible=_readonly(mapped.feasible, dtype=bool),
        transition_reasons=tuple(tuple(row) for row in mapped.transition_reasons),
        diagnostics=MappingProxyType(dict(mapped.diagnostics)),
    )
    return MaterializedCandidate(
        receipt=receipt,
        field_values=field_values,
        represented_values=represented,
        signal=signal,
        mapped=mapped,
        endpoint_clip_count=_endpoint_clip_count(
            receipt.representation_id, field_values
        ),
        field_array_sha256=array_sha256(field_values),
        represented_array_sha256=array_sha256(represented),
        signal_array_sha256=array_sha256(signal),
        weight_array_sha256=array_sha256(mapped.weights),
    )


__all__ = [
    "MaterializedCandidate",
    "apply_frozen_representation",
    "materialize_authorized",
    "verify_materialization_authority",
]
