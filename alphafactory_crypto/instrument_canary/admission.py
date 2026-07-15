"""Fail-closed candidate authorization for the real-data canary.

This module is deliberately data-blind.  It binds a legal structural genome to
the approved development-view identity and to the canonical primitive, mapping,
target, lag, cost, and source-code contracts before a caller may read a field.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any, Callable, Mapping

from alphafactory_crypto.instrument_capability.mapping import (
    DEFAULT_MAPPING_CONTRACTS,
    mapping_contract_sha256,
)
from alphafactory_crypto.instrument_capability.feedback import (
    FEASIBILITY_DIRECTIONS,
    FEASIBILITY_NORMALIZATION,
    FEASIBILITY_ORDER,
    FEASIBILITY_THRESHOLDS,
    feedback_contract_payload,
)
from alphafactory_crypto.instrument_capability.primitives import CANONICAL_PRIMITIVES

from .contracts import CandidateGenome, canonical_json_bytes
from .grammar import FrozenGrammar


AUTHORIZATION_ID = "BOUNDED_EXISTING_RELEASE_DEVELOPMENT_CANARY"
RECEIPT_SCHEMA_VERSION = 1
_HEX_40 = re.compile(r"^[0-9a-fA-F]{40}$")
_HEX_64 = re.compile(r"^[0-9a-fA-F]{64}$")

_PIT_LAG_CONTRACT = {
    "feature_bucket_coordinate": "t",
    "feature_observable_offset_hours": 1,
    "feature_observable_time": "t+1h",
    "execution_offset_hours": 2,
    "execution_time": "t+2h",
    "execution_delay_after_observable_hours": 1,
    "source_lag_seconds": 0,
    "partial_current_hour": "PROHIBITED",
    "no_fill": True,
}

_AUTHORIZATION_RULES = {
    "authorization_id": AUTHORIZATION_ID,
    "data_role": "DEVELOPMENT_TRAIN_ONLY",
    "field_authority": "release searchable whitelist AND FrozenGrammar",
    "primitive_authority": (
        "alphafactory_crypto.instrument_capability.primitives.CANONICAL_PRIMITIVES"
    ),
    "mapping_authority": (
        "FrozenGrammar.mapping_for -> "
        "alphafactory_crypto.instrument_capability.mapping.DEFAULT_MAPPING_CONTRACTS"
    ),
    "mapping_is_search_gene": False,
    "deprecated_aliases_allowed": False,
    "target_entry_offset_hours": 2,
    "materialization_before_authorization": "FORBIDDEN",
}

_DEFAULT_CANARY_COST = {
    "model_id": "FULL_L1_FIXED_5BPS_WITH_INITIAL_AND_TERMINAL",
    "cost_bps": 5.0,
    "initial_establishment_charged": True,
    "terminal_liquidation_charged": True,
}


def _sha256(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest().upper()


def real_data_feedback_contract_payload() -> dict[str, Any]:
    """Frozen scope supersession for applying strict feedback to real dev data."""

    synthetic = feedback_contract_payload()
    return {
        "schema_version": 1,
        "id": "REAL_DATA_TRAIN_ONLY_STRICT_FEASIBILITY_FEEDBACK_V1",
        "numerical_rule_source_sha256": _sha256(synthetic),
        "method": synthetic["method"],
        "hard_blocks_before_strict": list(synthetic["hard_blocks_before_strict"]),
        "axis_order": list(FEASIBILITY_ORDER),
        "thresholds": dict(FEASIBILITY_THRESHOLDS),
        "directions": dict(FEASIBILITY_DIRECTIONS),
        "normalization": dict(FEASIBILITY_NORMALIZATION),
        "scope": "REAL_EXISTING_RELEASE_DEVELOPMENT_TRAIN_ONLY_CANARY",
        "adaptive_role": "POLICY_UPDATE_WITHIN_THIS_CANARY_ONLY",
        "oos_role": False,
        "economic_alpha_claim": False,
        "legacy_gross_proxy_role": "DIAGNOSTIC_ONLY_NOT_IN_ORDERING",
    }


def _json_copy(value: Mapping[str, Any]) -> dict[str, Any]:
    """Copy a JSON contract while rejecting non-finite/non-serializable state."""

    return json.loads(
        json.dumps(
            dict(value),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
    )


def _require_sha256(value: Any, name: str) -> str:
    result = str(value)
    if not _HEX_64.fullmatch(result):
        raise ValueError(f"{name} must be a 64-character SHA256")
    return result.upper()


def _representation_contract(
    grammar: FrozenGrammar, genome: CandidateGenome
) -> dict[str, Any]:
    for field in grammar.field_specs:
        if field.field_id != genome.field_id:
            continue
        for representation in field.representations:
            if representation.representation_id == genome.representation_id:
                return {
                    "field_id": field.field_id,
                    "value_domain": field.value_domain,
                    "representation_id": representation.representation_id,
                    "formula": representation.formula,
                    "input_domain": representation.input_domain,
                    "nonlinear": representation.nonlinear,
                }
    raise ValueError("field/representation has no frozen representation contract")


@dataclass(frozen=True, slots=True)
class CandidateAuthorizationReceipt:
    """Immutable authorization identity required by materialization."""

    authorization_id: str
    candidate_id: str
    genome: CandidateGenome
    field_id: str
    representation_id: str
    representation_contract: Mapping[str, Any]
    primitive_id: str
    primitive_parameters: Mapping[str, Any]
    mechanism_family: str
    mapping_id: str
    mapping_contract_sha256: str
    target_horizon_hours: int
    target_contract: Mapping[str, Any]
    target_execution_offset_hours: int
    pit_lag_contract: Mapping[str, Any]
    cost_contract: Mapping[str, Any]
    feedback_contract: Mapping[str, Any]
    release_id: str
    development_view_id: str
    release_view_sha256: str
    release_manifest_sha256: str
    parent_release_content_sha256: str
    source_bundle_sha256: str
    output_bundle_sha256: str
    source_code_sha: str
    grammar_contract_sha256: str
    representation_contract_sha256: str
    primitive_contract_sha256: str
    target_contract_sha256: str
    pit_lag_contract_sha256: str
    cost_contract_sha256: str
    feedback_contract_sha256: str
    authorization_contract_sha256: str
    cache_key: str
    receipt_sha256: str

    def _integrity_payload(self) -> dict[str, Any]:
        return {
            "schema_version": RECEIPT_SCHEMA_VERSION,
            "authorization_id": self.authorization_id,
            "candidate_id": self.candidate_id,
            "genome": self.genome.canonical_dict(),
            "field": {
                "field_id": self.field_id,
                "representation_id": self.representation_id,
                "representation_contract": dict(self.representation_contract),
            },
            "primitive": {
                "primitive_id": self.primitive_id,
                "parameters": dict(self.primitive_parameters),
            },
            "mechanism_family": self.mechanism_family,
            "mapping": {
                "mapping_id": self.mapping_id,
                "contract_sha256": self.mapping_contract_sha256,
            },
            "target": {
                "horizon_hours": self.target_horizon_hours,
                "execution_offset_hours": self.target_execution_offset_hours,
                "contract": dict(self.target_contract),
            },
            "pit_lag_contract": dict(self.pit_lag_contract),
            "cost_contract": dict(self.cost_contract),
            "feedback_contract": dict(self.feedback_contract),
            "release": {
                "release_id": self.release_id,
                "development_view_id": self.development_view_id,
                "development_view_sha256": self.release_view_sha256,
                "release_manifest_sha256": self.release_manifest_sha256,
                "parent_release_content_sha256": self.parent_release_content_sha256,
                "source_bundle_sha256": self.source_bundle_sha256,
                "output_bundle_sha256": self.output_bundle_sha256,
            },
            "source_code_sha": self.source_code_sha,
            "contracts": {
                "grammar_sha256": self.grammar_contract_sha256,
                "representation_sha256": self.representation_contract_sha256,
                "primitive_sha256": self.primitive_contract_sha256,
                "mapping_sha256": self.mapping_contract_sha256,
                "target_sha256": self.target_contract_sha256,
                "pit_lag_sha256": self.pit_lag_contract_sha256,
                "cost_sha256": self.cost_contract_sha256,
                "feedback_sha256": self.feedback_contract_sha256,
                "authorization_sha256": self.authorization_contract_sha256,
            },
            "cache_key": self.cache_key,
        }

    def verify_integrity(self) -> None:
        if self.candidate_id != self.genome.candidate_id:
            raise ValueError("authorization receipt candidate identity mismatch")
        if self.field_id != self.genome.field_id:
            raise ValueError("authorization receipt field identity mismatch")
        if self.representation_id != self.genome.representation_id:
            raise ValueError("authorization receipt representation identity mismatch")
        if self.primitive_id != self.genome.primitive_id:
            raise ValueError("authorization receipt primitive identity mismatch")
        if self.mechanism_family != self.genome.mechanism_family:
            raise ValueError("authorization receipt mechanism identity mismatch")
        if self.target_horizon_hours != self.genome.target_horizon_hours:
            raise ValueError("authorization receipt target horizon mismatch")
        expected_cache_key = _sha256(
            {
                "candidate_id": self.candidate_id,
                "release_view_sha256": self.release_view_sha256,
                "source_code_sha": self.source_code_sha,
                "contracts": {
                    "grammar": self.grammar_contract_sha256,
                    "representation": self.representation_contract_sha256,
                    "primitive": self.primitive_contract_sha256,
                    "mapping": self.mapping_contract_sha256,
                    "target": self.target_contract_sha256,
                    "pit_lag": self.pit_lag_contract_sha256,
                    "cost": self.cost_contract_sha256,
                    "feedback": self.feedback_contract_sha256,
                    "authorization": self.authorization_contract_sha256,
                },
            }
        )
        if self.cache_key != expected_cache_key:
            raise ValueError("authorization receipt cache identity mismatch")
        if self.receipt_sha256 != _sha256(self._integrity_payload()):
            raise ValueError("authorization receipt integrity hash mismatch")
        if self.feedback_contract_sha256 != _sha256(dict(self.feedback_contract)):
            raise ValueError("authorization receipt feedback contract hash mismatch")

    def to_dict(self) -> dict[str, Any]:
        payload = self._integrity_payload()
        payload["receipt_sha256"] = self.receipt_sha256
        return payload


def _validate_release(
    release_manifest: Mapping[str, Any], expected_release: Mapping[str, Any]
) -> dict[str, str]:
    manifest = _json_copy(release_manifest)
    recorded_manifest_sha = _require_sha256(
        manifest.get("manifest_sha256"), "release manifest hash"
    )
    hash_payload = dict(manifest)
    del hash_payload["manifest_sha256"]
    if _sha256(hash_payload) != recorded_manifest_sha:
        raise ValueError("release manifest content hash mismatch")

    exact_identity = {
        "release_id": "parent_release_id",
        "development_view_id": "development_view_id",
        "parent_release_content_sha256": "parent_release_content_sha256",
        "source_bundle_sha256": "expected_source_bundle_sha256",
        "output_bundle_sha256": "expected_output_bundle_sha256",
    }
    for manifest_key, expected_key in exact_identity.items():
        if str(manifest.get(manifest_key)) != str(expected_release.get(expected_key)):
            raise ValueError(f"release identity/hash mismatch: {manifest_key}")
    for name in (
        "parent_release_content_sha256",
        "source_bundle_sha256",
        "output_bundle_sha256",
    ):
        _require_sha256(manifest[name], name)

    view_sha = _require_sha256(
        manifest.get("development_view_sha256"), "development view hash"
    )
    configured_view_sha = expected_release.get("development_view_sha256")
    if configured_view_sha is not None and view_sha != _require_sha256(
        configured_view_sha, "expected development view hash"
    ):
        raise ValueError("release identity/hash mismatch: development_view_sha256")

    expected_fields = tuple(str(value) for value in expected_release["searchable_fields"])
    manifest_fields = tuple(str(value) for value in manifest.get("searchable_fields", []))
    if not expected_fields or manifest_fields != expected_fields:
        raise ValueError("release searchable field whitelist mismatch")
    if manifest.get("target_only_fields") != ["close_price"]:
        raise ValueError("release target-only field contract mismatch")
    if "symbols" in expected_release or "months" in expected_release:
        expected_assets = [str(value) for value in expected_release.get("symbols", [])]
        expected_months = [str(value) for value in expected_release.get("months", [])]
        if (
            manifest.get("assets") != expected_assets
            or manifest.get("months") != expected_months
            or not expected_assets
            or not expected_months
        ):
            raise ValueError("release asset/month coordinate contract mismatch")
        computed_view_sha = _sha256(
            {
                "release_id": str(manifest["release_id"]),
                "assets": expected_assets,
                "months": expected_months,
                "source_bundle_sha256": str(manifest["source_bundle_sha256"]),
                "output_bundle_sha256": str(manifest["output_bundle_sha256"]),
                "searchable_fields": list(manifest_fields),
                "target_only_fields": ["close_price"],
            }
        )
        if view_sha != computed_view_sha:
            raise ValueError("release development-view content hash mismatch")
    if manifest.get("data_role") != "DEVELOPMENT_TRAIN_ONLY":
        raise PermissionError("release is not development-train-only")
    if int(manifest.get("sealed_reads", -1)) != 0:
        raise PermissionError("release manifest records sealed-role reads")
    if manifest.get("challenge_path_enumerated") is not False:
        raise PermissionError("release manifest does not prove challenge non-enumeration")

    pit = manifest.get("pit_contract")
    if not isinstance(pit, Mapping):
        raise ValueError("release PIT contract is missing")
    expected_pit = {
        "observable_time": "timestamp + 1h",
        "maturity": "timestamp + 1h",
        "source_lag_seconds": 0,
        "partial_current_hour": "PROHIBITED",
        "no_fill": True,
    }
    if any(pit.get(key) != value for key, value in expected_pit.items()):
        raise ValueError("release PIT/lag contract mismatch")

    return {
        "manifest_sha256": recorded_manifest_sha,
        "view_sha256": view_sha,
        "release_id": str(manifest["release_id"]),
        "development_view_id": str(manifest["development_view_id"]),
        "parent_release_content_sha256": str(
            manifest["parent_release_content_sha256"]
        ).upper(),
        "source_bundle_sha256": str(manifest["source_bundle_sha256"]).upper(),
        "output_bundle_sha256": str(manifest["output_bundle_sha256"]).upper(),
    }


def _validate_target(
    target_contract: Mapping[str, Any],
    release_manifest: Mapping[str, Any],
    horizon_hours: int,
) -> dict[str, Any]:
    target = _json_copy(target_contract)
    manifest_target = release_manifest.get("target_horizon_contract")
    if not isinstance(manifest_target, Mapping) or _json_copy(manifest_target) != target:
        raise ValueError("target contract differs from the qualified release manifest")
    required = {
        "feature_bucket_coordinate": "t",
        "feature_observable_time": "t+1h",
        "execution_time": "t+2h",
        "execution_delay_after_observable_hours": 1,
        "formula": "log(close[t+2h+horizon] / close[t+2h])",
        "all_metrics_role": "DEVELOPMENT_TRAIN_ONLY",
    }
    if any(target.get(key) != value for key, value in required.items()):
        raise ValueError("target PIT/lag is not the frozen t+2 execution contract")
    horizons = target.get("horizons_hours")
    if not isinstance(horizons, list) or horizon_hours not in horizons:
        raise ValueError("candidate target horizon is absent from the frozen target contract")
    if "close_price" not in str(target.get("price_source", "")):
        raise ValueError("target-only close price authority is missing")
    return target


def authorize_candidate(
    genome: CandidateGenome,
    *,
    grammar: FrozenGrammar,
    release_manifest: Mapping[str, Any],
    expected_release: Mapping[str, Any],
    target_contract: Mapping[str, Any],
    source_code_sha: str,
    cost_contract: Mapping[str, Any] | None = None,
    expected_mapping_id: str | None = None,
    reader_callback: Callable[[], Any] | None = None,
) -> CandidateAuthorizationReceipt:
    """Authorize one candidate without reading any market-data field.

    ``reader_callback`` is an audit seam: it runs only after every check and
    after the receipt has passed its own integrity check.  Production callers
    normally omit it and pass a field reader to ``materialize_authorized``.
    """

    if not isinstance(grammar, FrozenGrammar):
        raise TypeError("authorization requires FrozenGrammar")
    if grammar.contract_sha256 != FrozenGrammar.default().contract_sha256:
        raise ValueError("authorization requires the frozen canary grammar contract")
    grammar.validate(genome)

    if genome.primitive_id not in CANONICAL_PRIMITIVES:
        raise ValueError("candidate primitive is not canonical")
    release = _validate_release(release_manifest, expected_release)
    release_fields = tuple(str(value) for value in expected_release["searchable_fields"])
    if genome.field_id not in release_fields:
        raise ValueError("candidate field is outside the approved release whitelist")

    mapping_id = grammar.mapping_for(genome)
    if expected_mapping_id is not None and expected_mapping_id != mapping_id:
        raise ValueError("requested mapping does not equal the grammar-derived mapping")
    if mapping_id not in DEFAULT_MAPPING_CONTRACTS:
        raise ValueError("grammar-derived mapping has no canonical contract")
    mapping_sha = mapping_contract_sha256(DEFAULT_MAPPING_CONTRACTS[mapping_id])

    target = _validate_target(
        target_contract, release_manifest, genome.target_horizon_hours
    )
    source_sha = str(source_code_sha).lower()
    if not _HEX_40.fullmatch(source_sha):
        raise ValueError("source_code_sha must be a full 40-character Git SHA")

    representation = _representation_contract(grammar, genome)
    primitive = CANONICAL_PRIMITIVES[genome.primitive_id].to_dict()
    bound_cost = _json_copy(
        cost_contract if cost_contract is not None else _DEFAULT_CANARY_COST
    )
    bound_feedback = real_data_feedback_contract_payload()
    required_cost = {
        "model_id": "FULL_L1_FIXED_5BPS_WITH_INITIAL_AND_TERMINAL",
        "cost_bps": 5.0,
        "initial_establishment_charged": True,
        "terminal_liquidation_charged": True,
    }
    if any(bound_cost.get(key) != value for key, value in required_cost.items()):
        raise ValueError(
            "canary cost contract must bind full-L1 fixed 5 bps with initial and terminal"
        )

    contract_hashes = {
        "grammar": grammar.contract_sha256,
        "representation": _sha256(representation),
        "primitive": _sha256(primitive),
        "mapping": mapping_sha,
        "target": _sha256(target),
        "pit_lag": _sha256(_PIT_LAG_CONTRACT),
        "cost": _sha256(bound_cost),
        "feedback": _sha256(bound_feedback),
        "authorization": _sha256(_AUTHORIZATION_RULES),
    }
    cache_key = _sha256(
        {
            "candidate_id": genome.candidate_id,
            "release_view_sha256": release["view_sha256"],
            "source_code_sha": source_sha,
            "contracts": contract_hashes,
        }
    )

    arguments: dict[str, Any] = {
        "authorization_id": AUTHORIZATION_ID,
        "candidate_id": genome.candidate_id,
        "genome": genome,
        "field_id": genome.field_id,
        "representation_id": genome.representation_id,
        "representation_contract": representation,
        "primitive_id": genome.primitive_id,
        "primitive_parameters": {
            "window": genome.window,
            "long_window": genome.long_window,
            "threshold": genome.threshold,
        },
        "mechanism_family": genome.mechanism_family,
        "mapping_id": mapping_id,
        "mapping_contract_sha256": mapping_sha,
        "target_horizon_hours": genome.target_horizon_hours,
        "target_contract": target,
        "target_execution_offset_hours": 2,
        "pit_lag_contract": dict(_PIT_LAG_CONTRACT),
        "cost_contract": bound_cost,
        "feedback_contract": bound_feedback,
        "release_id": release["release_id"],
        "development_view_id": release["development_view_id"],
        "release_view_sha256": release["view_sha256"],
        "release_manifest_sha256": release["manifest_sha256"],
        "parent_release_content_sha256": release[
            "parent_release_content_sha256"
        ],
        "source_bundle_sha256": release["source_bundle_sha256"],
        "output_bundle_sha256": release["output_bundle_sha256"],
        "source_code_sha": source_sha,
        "grammar_contract_sha256": contract_hashes["grammar"],
        "representation_contract_sha256": contract_hashes["representation"],
        "primitive_contract_sha256": contract_hashes["primitive"],
        "target_contract_sha256": contract_hashes["target"],
        "pit_lag_contract_sha256": contract_hashes["pit_lag"],
        "cost_contract_sha256": contract_hashes["cost"],
        "feedback_contract_sha256": contract_hashes["feedback"],
        "authorization_contract_sha256": contract_hashes["authorization"],
        "cache_key": cache_key,
    }
    provisional = CandidateAuthorizationReceipt(**arguments, receipt_sha256="")
    receipt = CandidateAuthorizationReceipt(
        **arguments, receipt_sha256=_sha256(provisional._integrity_payload())
    )
    receipt.verify_integrity()
    if reader_callback is not None:
        reader_callback()
    return receipt


__all__ = [
    "AUTHORIZATION_ID",
    "CandidateAuthorizationReceipt",
    "RECEIPT_SCHEMA_VERSION",
    "authorize_candidate",
    "real_data_feedback_contract_payload",
]
