from __future__ import annotations

from typing import Any, Mapping


ROLE_VALUES = {"primary", "interaction-only", "condition-only", "state-only", "benchmark-only", "blocked"}


def truthy(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def classify_input_role(row: Mapping[str, Any]) -> tuple[str, str]:
    compiler = str(row.get("compiler_role_v3", ""))
    semantic = str(row.get("semantic_type_v3", ""))
    allowed = str(row.get("allowed_roles_v3", ""))
    feature_role = str(row.get("feature_role", "")).lower()
    economic_role = str(row.get("economic_role", "")).lower()
    field = str(row.get("field_name", ""))

    if truthy(row.get("uses_future")) or truthy(row.get("uses_label")) or not truthy(row.get("timing_ok", True)):
        return "blocked", "future_label_or_timing"
    if compiler in {"blocked_or_unlicensed", "forbidden_label_future_or_timing"} or allowed == "none":
        return "blocked", "compiler_or_license_block"
    if semantic == "state_or_taxonomy" or any(token in feature_role for token in ("state", "taxonomy", "regime")):
        return "state-only", "state_or_taxonomy_semantics"
    if semantic == "price_like" or field in {"trade_close", "mark_close", "index_close"}:
        return "benchmark-only", "price_reference_semantics"
    if compiler in {"ordinary_alpha_seed", "exploratory_signal_seed"}:
        return "primary", "static_signal_role_contract"
    if any(token in economic_role for token in ("risk", "quality", "control")):
        return "condition-only", "risk_or_quality_condition"
    if not truthy(row.get("generator_allowed_any_mode")) and ("regime" in allowed or "neutralizer" in allowed):
        return "condition-only", "condition_without_generator_license"
    if "interaction_modifier" in allowed or "interaction" in allowed:
        return "interaction-only", "interaction_modifier_contract"
    if "regime" in allowed or "neutralizer" in allowed:
        return "condition-only", "regime_or_neutralizer_contract"
    return "blocked", "no_unambiguous_static_role"


def validate_registry_rows(rows: list[dict[str, Any]], ontology_fields: set[str]) -> None:
    fields = [str(row.get("field_name", "")) for row in rows]
    if len(fields) != len(set(fields)):
        raise ValueError("A7INPUT0-v2 contains duplicate fields")
    if set(fields) != ontology_fields:
        raise ValueError("A7INPUT0-v2 must cover the ontology exactly")
    invalid = sorted({str(row.get("input_role", "")) for row in rows}.difference(ROLE_VALUES))
    if invalid:
        raise ValueError(f"invalid A7INPUT0-v2 roles: {invalid}")
    if any(truthy(row.get("generator_enabled_b0")) for row in rows):
        raise ValueError("B0 cannot enable any field in generator")
    if any(row["input_role"] == "blocked" and truthy(row.get("primary_generator_eligible_after_b0")) for row in rows):
        raise ValueError("blocked fields cannot become primary-generator eligible")
