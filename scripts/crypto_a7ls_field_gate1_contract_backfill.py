from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
DATE = "20260609"
STAGE = "A7LS-FIELD-GATE-1"

GATE0 = REPO / "runtime" / "a7ls_field_gate_current_queue_20260609"
DRIFT_FIELDS = GATE0 / "a7ls_field_gate_contract_drift_fields.csv"
FIELD_ROUTE_MAP = GATE0 / "a7ls_field_gate_field_route_map.csv"
ONTOLOGY_V3 = REPO / "runtime" / "a7ffr1_field_ontology_v3" / "a7ffr1_field_ontology_v3.csv"
F3_MATRIX = (
    REPO
    / "runtime"
    / "a7aif3_materialization_evaluator_parity"
    / "a7aif3_field_materialization_matrix.csv"
)
RUNTIME = REPO / "runtime" / "a7ls_field_gate1_contract_backfill_20260609"
REPORT = REPO / "reports" / f"CRYPTO_A7LS_FIELD_GATE1_CONTRACT_BACKFILL_{DATE}.md"


FIELD_POLICY: dict[str, dict[str, Any]] = {
    "account_position_divergence": {
        "semantic_type_v3": "positioning_like",
        "data_behavior_v3": "slow_moving",
        "compiler_role_v3": "regime_neutralizer_interaction_seed",
        "allowed_roles_v3": "regime|neutralizer|interaction_modifier",
        "semantic_role": "risk_exposure_or_control_like",
        "source_family": "derived_positioning",
        "feature_class": "derived_cross_positioning_spread",
        "ordinary_alpha_allowed": False,
        "diagnostic_allowed": True,
        "risk_defense_allowed": True,
    },
    "top_global_account_divergence": {
        "semantic_type_v3": "positioning_like",
        "data_behavior_v3": "slow_moving",
        "compiler_role_v3": "regime_neutralizer_interaction_seed",
        "allowed_roles_v3": "regime|neutralizer|interaction_modifier",
        "semantic_role": "risk_exposure_or_control_like",
        "source_family": "derived_positioning",
        "feature_class": "derived_cross_positioning_spread",
        "ordinary_alpha_allowed": False,
        "diagnostic_allowed": True,
        "risk_defense_allowed": True,
    },
    "open_interest_value_change_24h": {
        "semantic_type_v3": "open_interest_like",
        "data_behavior_v3": "slow_moving",
        "compiler_role_v3": "exploratory_interaction_seed",
        "allowed_roles_v3": "diagnostic|interaction_modifier",
        "semantic_role": "regime_state_or_interaction_input",
        "source_family": "derived_open_interest",
        "feature_class": "derived_delta",
        "ordinary_alpha_allowed": False,
        "diagnostic_allowed": True,
        "risk_defense_allowed": False,
    },
    "premium_abs_state": {
        "semantic_type_v3": "basis_premium_like",
        "data_behavior_v3": "continuous_panel",
        "compiler_role_v3": "regime_neutralizer_interaction_seed",
        "allowed_roles_v3": "regime|diagnostic|interaction_modifier",
        "semantic_role": "regime_state_or_interaction_input",
        "source_family": "derived_basis_premium",
        "feature_class": "derived_abs_state",
        "ordinary_alpha_allowed": False,
        "diagnostic_allowed": True,
        "risk_defense_allowed": False,
    },
}

LATENT_POLICY = {
    "age_percentile_active_universe": ("listing_age_like", "listing_age_sensitive", "risk_exposure_or_control_like"),
    "age_x_volatility": ("age_x_volatility", "listing_age_sensitive", "regime_state_or_interaction_input"),
    "basis_abs_168h": ("basis_premium_like", "slow_moving", "regime_state_or_interaction_input"),
    "listing_age_days": ("listing_age_like", "listing_age_sensitive", "risk_exposure_or_control_like"),
    "log1p_listing_age_days": ("listing_age_like", "listing_age_sensitive", "risk_exposure_or_control_like"),
    "premium_abs_168h": ("basis_premium_like", "slow_moving", "regime_state_or_interaction_input"),
    "rolling_coverage_168h": ("coverage_like", "missingness_sensitive", "risk_exposure_or_control_like"),
    "sqrt_listing_age_days": ("listing_age_like", "listing_age_sensitive", "risk_exposure_or_control_like"),
}

UPPER_POLICY = {
    "market_breadth_state": "market_breadth_regime",
    "liquidity_cycle_state": "liquidity_regime",
    "leverage_crowding_state": "leverage_crowding_regime",
    "basis_dislocation_state": "basis_dislocation_regime",
    "stress_proxy_state": "stress_regime",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 60) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    try:
        return view.to_markdown(index=False)
    except ImportError:
        return "```text\n" + view.to_string(index=False) + "\n```"


def bool_str(value: Any) -> bool:
    return str(value).lower() in {"true", "1", "yes"}


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    if pd.isna(value):
        return ""
    text = str(value).strip()
    return "" if text.lower() == "nan" else text


def split_deps(value: Any) -> list[str]:
    return [x for x in clean_text(value).split(";") if x]


def policy_for(row: pd.Series) -> dict[str, Any]:
    field = str(row["field"])
    route = str(row["route"])
    if field in FIELD_POLICY:
        return dict(FIELD_POLICY[field])
    if route == "upper_alias":
        return {
            "semantic_type_v3": UPPER_POLICY.get(field, "regime_state"),
            "data_behavior_v3": "categorical_state",
            "compiler_role_v3": "state_conditioning_only",
            "allowed_roles_v3": "regime|neutralizer|interaction_modifier",
            "semantic_role": "regime_state_or_interaction_input",
            "source_family": "upper_regime_state",
            "feature_class": "upper_regime_alias",
            "ordinary_alpha_allowed": False,
            "diagnostic_allowed": True,
            "risk_defense_allowed": True,
        }
    if field in LATENT_POLICY:
        semantic_type, behavior, role = LATENT_POLICY[field]
        return {
            "semantic_type_v3": semantic_type,
            "data_behavior_v3": behavior,
            "compiler_role_v3": "regime_neutralizer_interaction_seed",
            "allowed_roles_v3": "regime|neutralizer|interaction_modifier",
            "semantic_role": role,
            "source_family": "latent_state_features",
            "feature_class": "latent_numeric_state",
            "ordinary_alpha_allowed": False,
            "diagnostic_allowed": True,
            "risk_defense_allowed": role == "risk_exposure_or_control_like",
        }
    return {
        "semantic_type_v3": "unknown",
        "data_behavior_v3": "unknown",
        "compiler_role_v3": "blocked_until_manual_review",
        "allowed_roles_v3": "forbidden",
        "semantic_role": "forbidden",
        "source_family": "unknown",
        "feature_class": "unknown",
        "ordinary_alpha_allowed": False,
        "diagnostic_allowed": False,
        "risk_defense_allowed": False,
    }


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    if not DRIFT_FIELDS.exists():
        raise FileNotFoundError(DRIFT_FIELDS)

    drift = pd.read_csv(DRIFT_FIELDS)
    field_route = pd.read_csv(FIELD_ROUTE_MAP) if FIELD_ROUTE_MAP.exists() else pd.DataFrame()
    ontology = pd.read_csv(ONTOLOGY_V3) if ONTOLOGY_V3.exists() else pd.DataFrame()
    f3 = pd.read_csv(F3_MATRIX) if F3_MATRIX.exists() else pd.DataFrame()

    f3_fields = set(f3["field_name"].astype(str)) if "field_name" in f3.columns else set()
    ontology_fields = set(ontology["field_name"].astype(str)) if "field_name" in ontology.columns else set()

    backfill_rows: list[dict[str, Any]] = []
    f3_rows: list[dict[str, Any]] = []
    ontology_rows: list[dict[str, Any]] = []
    registry: dict[str, Any] = {
        "stage": STAGE,
        "generated_at": now_iso(),
        "upper_aliases": {},
        "derived_dependencies": {},
        "dense_funding_fields": [],
        "field_roles": {},
    }

    for raw in drift.sort_values(["route", "field"]).to_dict("records"):
        row = pd.Series(raw)
        field = str(raw["field"])
        policy = policy_for(row)
        in_f3 = field in f3_fields
        in_ontology = field in ontology_fields
        dependencies = clean_text(raw.get("dependencies", ""))
        canonical = clean_text(raw.get("canonical_field", field)) or field
        route = clean_text(raw.get("route", ""))
        dependency_status = clean_text(raw.get("dependency_status", ""))

        backfill_decision = "PASS_BACKFILL_ROW_READY"
        if policy["allowed_roles_v3"] == "forbidden" or dependency_status.startswith("deps_missing"):
            backfill_decision = "BLOCK_MANUAL_REVIEW_REQUIRED"

        base = {
            "field_name": field,
            "canonical_field": canonical,
            "route": route,
            "dependencies": dependencies,
            "dependency_status": dependency_status,
            "already_in_a7aif3_matrix": in_f3,
            "already_in_ontology_v3": in_ontology,
            "formula_usage_count": int(raw.get("formula_usage_count", 0)),
            "source_field_names": dependencies if dependencies else canonical,
            "pit_lag_required": "+1h primary",
            "feature_available_time_primary": "timestamp + 1h",
            "same_bar_execution_allowed": False,
            "timing_ok": True,
            "allowed_for_search": True,
            "allowed_for_label": False,
            "selector_primary_allowed": False,
            "selector_diagnostic_allowed": True,
            "must_attach_controls": True,
            "enforcement_status": "OK_CONTRACT_BACKFILL_INTERACTION_ONLY",
            "enforcement_reason": "resolved_by_schema_or_runner_extension_but_not_in_shared_field_contract",
            "backfill_decision": backfill_decision,
            **policy,
        }
        backfill_rows.append(base)

        f3_rows.append(
            {
                "field_name": field,
                "semantic_role": policy["semantic_role"],
                "ordinary_alpha_allowed": policy["ordinary_alpha_allowed"],
                "diagnostic_allowed": policy["diagnostic_allowed"],
                "risk_defense_allowed": policy["risk_defense_allowed"],
                "resolution": "resolved_backfill",
                "error": "",
            }
        )

        ontology_rows.append(
            {
                "field_name": field,
                "source_field_names": base["source_field_names"],
                "source_family": policy["source_family"],
                "feature_class": policy["feature_class"],
                "feature_role": "contract_backfill_interaction_only",
                "semantic_role": policy["semantic_role"],
                "contract_present": True,
                "uses_future": False,
                "uses_label": False,
                "allowed_for_rank": True,
                "allowed_for_regime": True,
                "allowed_for_search": True,
                "allowed_for_label": False,
                "allowed_for_neutralization": policy["risk_defense_allowed"],
                "pit_lag_required": "+1h primary",
                "feature_available_time_primary": "timestamp + 1h",
                "same_bar_execution_allowed": False,
                "timing_ok": True,
                "ordinary_alpha_allowed": policy["ordinary_alpha_allowed"],
                "diagnostic_allowed": policy["diagnostic_allowed"],
                "risk_defense_allowed": policy["risk_defense_allowed"],
                "generator_allowed_any_mode": True,
                "selector_primary_allowed": False,
                "selector_diagnostic_allowed": True,
                "must_attach_controls": True,
                "semantic_type_v3": policy["semantic_type_v3"],
                "data_behavior_v3": policy["data_behavior_v3"],
                "compiler_role_v3": policy["compiler_role_v3"],
                "allowed_roles_v3": policy["allowed_roles_v3"],
                "enforcement_status": "OK_CONTRACT_BACKFILL_INTERACTION_ONLY",
                "enforcement_reason": "backfilled_from_a7ls_field_gate0_contract_drift",
            }
        )

        registry["field_roles"][field] = {
            "canonical_field": canonical,
            "route": route,
            "dependencies": [x for x in dependencies.split(";") if x],
            "semantic_type_v3": policy["semantic_type_v3"],
            "compiler_role_v3": policy["compiler_role_v3"],
            "allowed_roles_v3": policy["allowed_roles_v3"],
            "ordinary_alpha_allowed": policy["ordinary_alpha_allowed"],
            "diagnostic_allowed": policy["diagnostic_allowed"],
            "risk_defense_allowed": policy["risk_defense_allowed"],
        }
        if route == "upper_alias":
            registry["upper_aliases"][field] = canonical
        if route == "derived_dep_generated":
            registry["derived_dependencies"][field] = split_deps(dependencies)

    backfill = pd.DataFrame(backfill_rows)
    f3_append = pd.DataFrame(f3_rows)
    ontology_patch = pd.DataFrame(ontology_rows)

    unresolved = backfill[backfill["backfill_decision"].eq("BLOCK_MANUAL_REVIEW_REQUIRED")]
    route_summary = (
        backfill.groupby(["route", "semantic_role", "compiler_role_v3"], dropna=False)
        .agg(field_count=("field_name", "count"), formula_usage_count=("formula_usage_count", "sum"))
        .reset_index()
        .sort_values("formula_usage_count", ascending=False)
    )
    role_summary = (
        backfill.groupby(["ordinary_alpha_allowed", "diagnostic_allowed", "risk_defense_allowed"], dropna=False)
        .agg(field_count=("field_name", "count"), formula_usage_count=("formula_usage_count", "sum"))
        .reset_index()
    )

    backfill.to_csv(RUNTIME / "a7ls_field_gate1_backfill_field_contract.csv", index=False)
    f3_append.to_csv(RUNTIME / "a7ls_field_gate1_a7aif3_matrix_append.csv", index=False)
    ontology_patch.to_csv(RUNTIME / "a7ls_field_gate1_ontology_v3_patch.csv", index=False)
    route_summary.to_csv(RUNTIME / "a7ls_field_gate1_route_summary.csv", index=False)
    role_summary.to_csv(RUNTIME / "a7ls_field_gate1_role_summary.csv", index=False)
    write_json(RUNTIME / "a7ls_field_gate1_runner_extension_registry.json", registry)

    decision = (
        "BLOCK_A7LS_FIELD_GATE1_BACKFILL_UNRESOLVED"
        if not unresolved.empty
        else "PASS_A7LS_FIELD_GATE1_BACKFILL_PACKAGE_BUILT"
    )
    authorization = {
        "stage": STAGE,
        "decision": decision,
        "authorizes_current_running_wave_to_continue": True,
        "authorizes_next_search_expansion_if_registry_consumed": unresolved.empty,
        "authorizes_alpha_proof": False,
        "hard_rules": [
            "backfilled fields remain interaction/regime/diagnostic inputs, not ordinary-alpha primary seeds",
            "next queue builder must consume a7ls_field_gate1_runner_extension_registry.json or equivalent shared registry rows",
            "any new unresolved field returns to BLOCK_UNRESOLVED_FIELD",
            "ordinary_alpha promotion still requires response-backed non-L7 evidence",
        ],
    }
    write_json(RUNTIME / "a7ls_field_gate1_search_authorization.json", authorization)

    manifest = {
        "stage": STAGE,
        "decision": decision,
        "generated_at": now_iso(),
        "input_drift_field_count": int(len(drift)),
        "backfill_field_count": int(len(backfill)),
        "unresolved_backfill_count": int(len(unresolved)),
        "a7aif3_append_rows": int(len(f3_append)),
        "ontology_patch_rows": int(len(ontology_patch)),
        "runner_upper_alias_count": len(registry["upper_aliases"]),
        "runner_derived_dependency_count": len(registry["derived_dependencies"]),
        "authorizes_current_running_wave_to_continue": True,
        "authorizes_next_search_expansion_if_registry_consumed": unresolved.empty,
        "authorizes_alpha_proof": False,
        "executes_numeric_compute": False,
        "executes_search": False,
    }
    write_json(RUNTIME / "a7ls_field_gate1_manifest.json", manifest)

    report = f"""# CRYPTO A7LS Field Gate 1 Contract Backfill {DATE}

## Decision

`{decision}`

This package backfills the 17 A7LS-FIELD-GATE-0 drift fields into explicit field-contract rows. It does not run numeric compute, replay, search, or alpha proof.

## Counts

- input_drift_field_count: {len(drift)}
- backfill_field_count: {len(backfill)}
- unresolved_backfill_count: {len(unresolved)}
- a7aif3_append_rows: {len(f3_append)}
- ontology_patch_rows: {len(ontology_patch)}
- runner_upper_alias_count: {len(registry["upper_aliases"])}
- runner_derived_dependency_count: {len(registry["derived_dependencies"])}
- authorizes_current_running_wave_to_continue: true
- authorizes_next_search_expansion_if_registry_consumed: {str(unresolved.empty).lower()}

## Critical Rule

These fields are backfilled as regime / neutralizer / diagnostic / interaction inputs. They are not promoted to ordinary-alpha primary seeds. Ordinary-alpha promotion still requires response-backed non-L7 evidence.

## Route Summary

{md_table(route_summary, 80)}

## Backfill Fields

{md_table(backfill[["field_name", "route", "semantic_type_v3", "semantic_role", "compiler_role_v3", "allowed_roles_v3", "ordinary_alpha_allowed", "diagnostic_allowed", "risk_defense_allowed", "formula_usage_count", "backfill_decision"]], 80)}

## Search Authorization

{md_table(pd.DataFrame([authorization]), 10)}

## Outputs

- `{RUNTIME / "a7ls_field_gate1_manifest.json"}`
- `{RUNTIME / "a7ls_field_gate1_backfill_field_contract.csv"}`
- `{RUNTIME / "a7ls_field_gate1_a7aif3_matrix_append.csv"}`
- `{RUNTIME / "a7ls_field_gate1_ontology_v3_patch.csv"}`
- `{RUNTIME / "a7ls_field_gate1_runner_extension_registry.json"}`
- `{RUNTIME / "a7ls_field_gate1_search_authorization.json"}`
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
