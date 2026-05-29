from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7aif0_field_contract_enforcement_ledger"
REPORT = REPO / "reports" / "CRYPTO_A7AIF0_FIELD_CONTRACT_ENFORCEMENT_LEDGER_20260529.md"

LINEAGE = REPO / "runtime" / "a7al0r_code_feature_regime_readiness_audit" / "a7al0r_feature_lineage_ledger.csv"
ROLE_LEDGER = REPO / "runtime" / "a7aa2_feature_role_classification" / "a7aa2_feature_role_ledger.csv"
TIMING = REPO / "runtime" / "a7al0_top498_alpha_search_contract" / "a7al_field_timing_contract.csv"
A7AR2_FIELD_AUDIT = REPO / "runtime" / "a7ar2_feature_algebra_parity_smoke" / "a7ar2_field_contract_audit.csv"
MOTIF_PACK = REPO / "config" / "crypto_formula_gen_v2_motif_pack_v1.json"

ORDINARY_LABELS = {"L0_raw_forward_return", "L1_cross_sectional_relative_return"}
METADATA_FIELDS = {"symbol", "timestamp"}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def boolish(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if pd.isna(value):
        return False
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def val(row: dict[str, Any], key: str, default: Any = "") -> Any:
    value = row.get(key, default)
    if pd.isna(value):
        return default
    return value


def as_set(pipe_string: Any) -> set[str]:
    if pd.isna(pipe_string):
        return set()
    text = str(pipe_string).strip()
    if not text:
        return set()
    return {part for part in text.split("|") if part}


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def dict_by_field(frame: pd.DataFrame) -> dict[str, dict[str, Any]]:
    if frame.empty or "field_name" not in frame.columns:
        return {}
    return {
        str(row["field_name"]): row.to_dict()
        for _, row in frame.drop_duplicates("field_name", keep="last").iterrows()
    }


def motif_field_rows(config: dict[str, Any]) -> tuple[dict[str, str], pd.DataFrame]:
    field_to_family: dict[str, str] = {}
    family_rows: list[dict[str, Any]] = []
    for family, fields in (config.get("field_families") or {}).items():
        for field in fields:
            field_name = str(field)
            field_to_family[field_name] = str(family)
            family_rows.append({"field_name": field_name, "motif_field_family": str(family)})
    return field_to_family, pd.DataFrame(family_rows)


def classify_semantic_role(
    field_name: str,
    lineage: dict[str, Any],
    role: dict[str, Any],
    in_motif_pack: bool,
) -> str:
    if field_name in METADATA_FIELDS:
        return "metadata_key"
    if boolish(lineage.get("uses_future")) or boolish(lineage.get("uses_label")) or boolish(lineage.get("allowed_for_label")):
        return "label_only_or_future_dependent"
    feature_class = str(val(lineage, "feature_class", ""))
    source_family = str(val(lineage, "source_family", ""))
    if feature_class == "metadata" or source_family == "key":
        return "metadata_key"
    feature_role = str(val(role, "feature_role", ""))
    labels = as_set(role.get("best_label_families", ""))
    if feature_role == "predictive_signal_candidate" and labels.intersection(ORDINARY_LABELS):
        return "ordinary_signal_candidate"
    if feature_role == "predictive_signal_candidate":
        return "diagnostic_rank_or_nonordinary_signal"
    if feature_role == "regime_state_or_interaction_input":
        return "regime_state_or_interaction_input"
    if feature_role == "control_like_or_risk_exposure":
        return "risk_exposure_or_control_like"
    if feature_role == "weak_or_unstable":
        return "weak_or_unstable"
    if in_motif_pack and lineage:
        return "unclassified_generator_ingredient"
    return "unclassified"


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    lineage_df = read_csv(LINEAGE)
    role_df = read_csv(ROLE_LEDGER)
    timing_df = read_csv(TIMING)
    a7ar2_df = read_csv(A7AR2_FIELD_AUDIT)
    motif_pack = read_json(MOTIF_PACK)
    motif_fields, motif_field_df = motif_field_rows(motif_pack)

    lineage = dict_by_field(lineage_df)
    roles = dict_by_field(role_df)
    timing = dict_by_field(timing_df)
    a7ar2 = dict_by_field(a7ar2_df)

    all_fields = sorted(set(lineage) | set(roles) | set(timing) | set(a7ar2) | set(motif_fields))
    rows: list[dict[str, Any]] = []
    for field_name in all_fields:
        lin = lineage.get(field_name, {})
        role = roles.get(field_name, {})
        time = timing.get(field_name, {})
        ar2 = a7ar2.get(field_name, {})
        in_motif = field_name in motif_fields
        semantic_role = classify_semantic_role(field_name, lin, role, in_motif)

        contract_present = bool(lin) or bool(time) or bool(ar2)
        search_allowed = boolish(lin.get("allowed_for_search"))
        regime_allowed = boolish(lin.get("allowed_for_regime"))
        rank_allowed = boolish(lin.get("allowed_for_rank"))
        neutralize_allowed = boolish(lin.get("allowed_for_neutralization"))
        no_label_leakage = not boolish(lin.get("uses_future")) and not boolish(lin.get("uses_label"))
        fixed_delay_required = boolish(lin.get("fixed_delay_stress_required")) or boolish(time.get("fixed_delay_stress_required")) or boolish(ar2.get("fixed_delay_stress_required"))
        same_bar_allowed = boolish(time.get("same_bar_execution_allowed")) or boolish(ar2.get("same_bar_execution_allowed"))
        ar2_in_contract = boolish(ar2.get("in_contract")) if ar2 else False
        timing_ok = contract_present and no_label_leakage and not fixed_delay_required and not same_bar_allowed

        ordinary_alpha_allowed = (
            semantic_role == "ordinary_signal_candidate"
            and search_allowed
            and timing_ok
        )
        diagnostic_allowed = (
            semantic_role in {
                "diagnostic_rank_or_nonordinary_signal",
                "regime_state_or_interaction_input",
                "unclassified_generator_ingredient",
            }
            and no_label_leakage
            and timing_ok
            and (search_allowed or regime_allowed or in_motif)
        )
        risk_defense_allowed = (
            semantic_role == "risk_exposure_or_control_like"
            and no_label_leakage
            and timing_ok
            and (search_allowed or neutralize_allowed or regime_allowed or in_motif)
        )
        generator_allowed_any_mode = ordinary_alpha_allowed or diagnostic_allowed or risk_defense_allowed
        if semantic_role in {"label_only_or_future_dependent", "metadata_key"}:
            enforcement_status = "FORBID"
            enforcement_reason = semantic_role
        elif in_motif and not contract_present:
            enforcement_status = "HOLD_CONTRACT_MISSING"
            enforcement_reason = "motif_field_missing_lineage_or_timing_contract"
        elif in_motif and (fixed_delay_required or same_bar_allowed):
            enforcement_status = "HOLD_TIMING_POLICY"
            enforcement_reason = "fixed_delay_or_same_bar_policy_incompatible"
        elif ordinary_alpha_allowed:
            enforcement_status = "OK_ORDINARY_ALPHA"
            enforcement_reason = "ordinary_label_response_and_contract_clean"
        elif diagnostic_allowed:
            enforcement_status = "OK_DIAGNOSTIC_OR_REGIME"
            enforcement_reason = "nonordinary_response_or_regime_input_contract_clean"
        elif risk_defense_allowed:
            enforcement_status = "OK_RISK_DEFENSE_OR_NEUTRALIZER"
            enforcement_reason = "control_like_or_risk_exposure_not_primary_alpha"
        elif semantic_role == "weak_or_unstable":
            enforcement_status = "HOLD_WEAK_RESPONSE"
            enforcement_reason = "primitive_response_map_weak_or_unstable"
        else:
            enforcement_status = "HOLD_UNCLASSIFIED"
            enforcement_reason = "no_role_or_mode_specific_allowance"

        rows.append(
            {
                "field_name": field_name,
                "source_field_names": val(lin, "source_field_names", ""),
                "source_family": val(lin, "source_family", val(role, "field_family", "")),
                "feature_class": val(lin, "feature_class", ""),
                "feature_role": val(role, "feature_role", ""),
                "semantic_role": semantic_role,
                "motif_field_family": motif_fields.get(field_name, ""),
                "in_motif_pack": in_motif,
                "contract_present": contract_present,
                "a7ar2_in_contract": ar2_in_contract,
                "uses_future": boolish(lin.get("uses_future")),
                "uses_label": boolish(lin.get("uses_label")),
                "allowed_for_rank": rank_allowed,
                "allowed_for_regime": regime_allowed,
                "allowed_for_search": search_allowed,
                "allowed_for_label": boolish(lin.get("allowed_for_label")),
                "allowed_for_neutralization": neutralize_allowed,
                "pit_lag_required": val(lin, "pit_lag_required", ""),
                "feature_available_time_primary": val(time, "feature_available_time_primary", val(ar2, "feature_available_time_primary", "")),
                "same_bar_execution_allowed": same_bar_allowed,
                "fixed_delay_stress_required": fixed_delay_required,
                "latency_audit_required": boolish(lin.get("latency_audit_required")) or bool(time) or bool(ar2),
                "timing_ok": timing_ok,
                "ordinary_alpha_allowed": ordinary_alpha_allowed,
                "diagnostic_allowed": diagnostic_allowed,
                "risk_defense_allowed": risk_defense_allowed,
                "generator_allowed_any_mode": generator_allowed_any_mode,
                "selector_primary_allowed": ordinary_alpha_allowed,
                "selector_diagnostic_allowed": diagnostic_allowed or risk_defense_allowed,
                "must_attach_controls": generator_allowed_any_mode,
                "best_label_families": val(role, "best_label_families", ""),
                "best_horizons": val(role, "best_horizons", ""),
                "best_transforms": val(role, "best_transforms", ""),
                "primitive_response_candidate_count": val(role, "primitive_response_candidate_count", 0),
                "economic_role": val(lin, "economic_role", ""),
                "caveat": val(lin, "caveat", ""),
                "enforcement_status": enforcement_status,
                "enforcement_reason": enforcement_reason,
            }
        )

    ledger = pd.DataFrame(rows).sort_values(["in_motif_pack", "field_name"], ascending=[False, True])
    motif_audit = ledger[ledger["in_motif_pack"]].copy()
    motif_summary = (
        motif_audit.groupby("motif_field_family", dropna=False)
        .agg(
            field_count=("field_name", "count"),
            ordinary_allowed=("ordinary_alpha_allowed", "sum"),
            diagnostic_allowed=("diagnostic_allowed", "sum"),
            risk_defense_allowed=("risk_defense_allowed", "sum"),
            forbidden=("enforcement_status", lambda s: int((s == "FORBID").sum())),
            contract_missing=("enforcement_status", lambda s: int((s == "HOLD_CONTRACT_MISSING").sum())),
            timing_policy_hold=("enforcement_status", lambda s: int((s == "HOLD_TIMING_POLICY").sum())),
            weak_or_unclassified=("enforcement_status", lambda s: int(s.astype(str).str.startswith("HOLD_").sum())),
        )
        .reset_index()
        .sort_values(["forbidden", "contract_missing", "weak_or_unclassified", "field_count"], ascending=[False, False, False, False])
    )
    status_summary = (
        ledger.groupby(["in_motif_pack", "enforcement_status"], dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values(["in_motif_pack", "count"], ascending=[False, False])
    )

    motif_forbidden_count = int((motif_audit["enforcement_status"] == "FORBID").sum())
    motif_contract_missing_count = int((motif_audit["enforcement_status"] == "HOLD_CONTRACT_MISSING").sum())
    motif_timing_hold_count = int((motif_audit["enforcement_status"] == "HOLD_TIMING_POLICY").sum())
    motif_label_leak_count = int((motif_audit["uses_future"] | motif_audit["uses_label"] | motif_audit["allowed_for_label"]).sum())
    warning_count = int(motif_audit["enforcement_status"].astype(str).str.startswith("HOLD_").sum())
    hard_blockers = []
    if motif_forbidden_count:
        hard_blockers.append("motif_fields_include_forbidden_or_label_fields")
    if motif_contract_missing_count:
        hard_blockers.append("motif_fields_missing_contract")
    if motif_timing_hold_count:
        hard_blockers.append("motif_fields_have_timing_policy_hold")
    if motif_label_leak_count:
        hard_blockers.append("motif_fields_have_label_or_future_leakage")

    decision = (
        "PASS_A7AIF0_FIELD_CONTRACT_ENFORCEMENT_LEDGER_READY_FOR_A7AIF1"
        if not hard_blockers
        else "HOLD_A7AIF0_FIELD_CONTRACT_ENFORCEMENT_BLOCKERS"
    )
    manifest = {
        "stage": "A7AI-F0",
        "generated_at": now_utc(),
        "decision": decision,
        "executes_search": False,
        "executes_replay": False,
        "executes_training": False,
        "uses_may": False,
        "input_artifacts": {
            "lineage": str(LINEAGE.relative_to(REPO)),
            "feature_role": str(ROLE_LEDGER.relative_to(REPO)),
            "timing": str(TIMING.relative_to(REPO)),
            "a7ar2_field_audit": str(A7AR2_FIELD_AUDIT.relative_to(REPO)),
            "motif_pack": str(MOTIF_PACK.relative_to(REPO)),
        },
        "field_count": int(len(ledger)),
        "motif_field_count": int(len(motif_audit)),
        "ordinary_alpha_allowed_motif_fields": int(motif_audit["ordinary_alpha_allowed"].sum()),
        "diagnostic_allowed_motif_fields": int(motif_audit["diagnostic_allowed"].sum()),
        "risk_defense_allowed_motif_fields": int(motif_audit["risk_defense_allowed"].sum()),
        "motif_warning_count": warning_count,
        "hard_blockers": hard_blockers,
        "authorizes_a7aif1_engine_enforcement_gap_audit": not hard_blockers,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    authorization = {
        "A7AI-F0": {"status": decision},
        "A7AI-F1_engine_enforcement_gap_audit": {"authorized": not hard_blockers},
        "formula_search": {"authorized": False},
        "large_search": {"authorized": False},
        "alpha_proof": {"authorized": False},
        "shadow_paper_live": {"authorized": False},
    }
    blocker_matrix = {
        "hard_blockers": hard_blockers,
        "warnings": {
            "motif_warning_count": warning_count,
            "weak_or_unclassified_motif_fields": int(
                motif_audit["enforcement_status"].isin(["HOLD_WEAK_RESPONSE", "HOLD_UNCLASSIFIED"]).sum()
            ),
        },
    }

    ledger.to_csv(RUNTIME / "a7aif0_semantic_field_enforcement_ledger.csv", index=False)
    motif_audit.to_csv(RUNTIME / "a7aif0_generator_field_family_enforcement.csv", index=False)
    motif_summary.to_csv(RUNTIME / "a7aif0_motif_family_enforcement_summary.csv", index=False)
    status_summary.to_csv(RUNTIME / "a7aif0_enforcement_summary.csv", index=False)
    write_json(RUNTIME / "a7aif0_blocker_matrix.json", blocker_matrix)
    write_json(RUNTIME / "a7aif0_authorization_matrix.json", authorization)
    write_json(RUNTIME / "a7aif0_manifest.json", manifest)

    lines = [
        "# CRYPTO A7AI-F0 FIELD CONTRACT ENFORCEMENT LEDGER",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7AI-F0 converts lineage, primitive response roles, timing contracts, and the generator motif pack into a machine-readable enforcement ledger. It does not run search, replay, training, or proof.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Motif Family Enforcement Summary",
        "",
        md_table(motif_summary, 80),
        "",
        "## Enforcement Status Summary",
        "",
        md_table(status_summary, 80),
        "",
        "## Generator Field Enforcement",
        "",
        md_table(motif_audit[[
            "field_name",
            "motif_field_family",
            "semantic_role",
            "feature_role",
            "ordinary_alpha_allowed",
            "diagnostic_allowed",
            "risk_defense_allowed",
            "enforcement_status",
            "enforcement_reason",
        ]], 120),
        "",
        "## Boundary",
        "",
        "```text",
        "No formula search is authorized.",
        "Fields can be available to the generator in different modes without being primary ordinary-alpha selector seeds.",
        "Label/future-dependent fields, same-bar fields, fixed-delay stress fields, and missing-contract motif fields are hard blockers.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
