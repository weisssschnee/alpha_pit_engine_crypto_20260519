from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7aif4_response_backed_field_promotion"
REPORT = REPO / "reports" / "CRYPTO_A7AIF4_RESPONSE_BACKED_FIELD_PROMOTION_20260529.md"

A7PM0 = REPO / "runtime" / "a7pm0_source_of_truth_registry" / "a7pm0_manifest.json"
A7AIF2 = REPO / "runtime" / "a7aif2_field_enforcement_regression" / "a7aif2_manifest.json"
A7AIF3 = REPO / "runtime" / "a7aif3_materialization_evaluator_parity" / "a7aif3_manifest.json"
A7AA4 = REPO / "runtime" / "a7aa4_response_readiness_handoff" / "a7aa4_manifest.json"
RESPONSE_MAP = REPO / "runtime" / "a7aa1_primitive_response_map" / "a7aa1_primitive_response_map.csv"
RESPONSE_CANDIDATES = REPO / "runtime" / "a7aa1_primitive_response_map" / "a7aa1_primitive_response_candidates.csv"
ROLE_LEDGER = REPO / "runtime" / "a7aa2_feature_role_classification" / "a7aa2_feature_role_ledger.csv"
ENFORCEMENT_LEDGER = REPO / "runtime" / "a7aif0_field_contract_enforcement_ledger" / "a7aif0_semantic_field_enforcement_ledger.csv"
FIELD_MATERIALIZATION = REPO / "runtime" / "a7aif3_materialization_evaluator_parity" / "a7aif3_field_materialization_matrix.csv"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def require_pass(stage: str, path: Path, expected_prefix: str = "PASS_") -> str:
    payload = read_json(path)
    decision = str(payload.get("decision", "MISSING"))
    if not decision.startswith(expected_prefix):
        raise SystemExit(f"{stage} not pass-like: {decision}")
    return decision


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    prereq = pd.DataFrame(
        [
            {"stage": "A7PM-0", "decision": require_pass("A7PM-0", A7PM0)},
            {"stage": "A7AI-F2", "decision": require_pass("A7AI-F2", A7AIF2)},
            {"stage": "A7AI-F3", "decision": require_pass("A7AI-F3", A7AIF3)},
            {"stage": "A7AA-4", "decision": require_pass("A7AA-4", A7AA4)},
        ]
    )
    aa4 = read_json(A7AA4)
    active_non_l7 = {
        label
        for label in aa4.get("active_label_families", [])
        if str(label) != "L7_ranked_future_return"
    }

    response = pd.read_csv(RESPONSE_MAP)
    candidates = pd.read_csv(RESPONSE_CANDIDATES)
    roles = pd.read_csv(ROLE_LEDGER)
    enforcement = pd.read_csv(ENFORCEMENT_LEDGER)
    materialization = pd.read_csv(FIELD_MATERIALIZATION)

    merged = response.merge(
        roles[["field_name", "feature_role", "reason"]],
        on="field_name",
        how="left",
        suffixes=("", "_a7aa2"),
    ).merge(
        enforcement[
            [
                "field_name",
                "semantic_role",
                "enforcement_status",
                "ordinary_alpha_allowed",
                "uses_future",
                "uses_label",
                "timing_ok",
                "must_attach_controls",
            ]
        ],
        on="field_name",
        how="left",
    ).merge(
        materialization[["field_name", "resolution"]],
        on="field_name",
        how="left",
    )

    merged["is_response_candidate"] = merged["decision"].eq("A7AA1_PRIMITIVE_RESPONSE_CANDIDATE")
    merged["is_non_l7_active_label"] = merged["label_family"].isin(active_non_l7)
    merged["control_clean_lt_1"] = pd.to_numeric(merged["control_ratio_premay_max"], errors="coerce") < 1.0
    merged["control_promotion_lt_0_8"] = pd.to_numeric(merged["control_ratio_premay_max"], errors="coerce") < 0.8
    merged["lag_survives"] = merged["lag_ok"].apply(truthy)
    merged["premay_stable"] = merged["premay_all_positive"].apply(truthy)
    merged["materialized"] = merged["resolution"].eq("resolved")
    merged["contract_clean"] = (
        merged["enforcement_status"].eq("OK_ORDINARY_ALPHA")
        & merged["ordinary_alpha_allowed"].apply(truthy)
        & ~merged["uses_future"].apply(truthy)
        & ~merged["uses_label"].apply(truthy)
        & merged["timing_ok"].apply(truthy)
    )
    merged["promotion_eligible"] = (
        merged["is_response_candidate"]
        & merged["is_non_l7_active_label"]
        & merged["control_clean_lt_1"]
        & merged["control_promotion_lt_0_8"]
        & merged["lag_survives"]
        & merged["premay_stable"]
        & merged["materialized"]
        & merged["contract_clean"]
    )
    merged["promotion_decision"] = "BLOCK"
    merged.loc[merged["is_response_candidate"] & ~merged["is_non_l7_active_label"], "promotion_decision"] = "HOLD_L7_ONLY"
    merged.loc[merged["is_response_candidate"] & merged["is_non_l7_active_label"] & ~merged["control_clean_lt_1"], "promotion_decision"] = "HOLD_CONTROL_DOMINATED"
    merged.loc[merged["is_response_candidate"] & merged["is_non_l7_active_label"] & merged["control_clean_lt_1"] & ~merged["control_promotion_lt_0_8"], "promotion_decision"] = "HOLD_CONTROL_MARGIN_WEAK"
    merged.loc[merged["is_response_candidate"] & merged["is_non_l7_active_label"] & merged["control_promotion_lt_0_8"] & ~merged["contract_clean"], "promotion_decision"] = "HOLD_CONTRACT_NOT_ORDINARY_ALPHA"
    merged.loc[merged["promotion_eligible"], "promotion_decision"] = "PROMOTE_ORDINARY_ALPHA_SEED"

    promotion_cols = [
        "field_name",
        "field_family",
        "source_family",
        "feature_class",
        "transform",
        "label_family",
        "label_horizon_h",
        "control_ratio_premay_max",
        "lag_ok",
        "premay_all_positive",
        "resolution",
        "semantic_role",
        "enforcement_status",
        "promotion_decision",
    ]
    promotion_audit = merged.loc[merged["is_response_candidate"], promotion_cols].copy()
    promoted = merged.loc[merged["promotion_eligible"], promotion_cols].drop_duplicates().copy()
    blocked = promotion_audit.loc[promotion_audit["promotion_decision"] != "PROMOTE_ORDINARY_ALPHA_SEED"].copy()

    role_transition = (
        promotion_audit.groupby(["field_name", "promotion_decision"], dropna=False)
        .size()
        .reset_index(name="evidence_rows")
    )
    ledger_preview = enforcement.copy()
    promoted_keys = set(zip(promoted["field_name"], promoted["transform"]))
    promoted_fields = set(promoted["field_name"])
    ledger_preview["a7aif4_promoted_ordinary_alpha_seed"] = ledger_preview["field_name"].isin(promoted_fields)
    ledger_preview["a7aif4_promotion_basis"] = ledger_preview["field_name"].map(
        lambda field: "|".join(sorted({f"{row.transform}:{row.label_family}:{row.label_horizon_h}" for row in promoted.itertuples() if row.field_name == field}))
    )

    blockers: list[str] = []
    if promoted.empty:
        blockers.append("no_response_backed_alpha_fields")
    if not promoted.empty and not promoted["label_family"].ne("L7_ranked_future_return").all():
        blockers.append("l7_only_promotion_detected")
    if not promoted.empty and not (pd.to_numeric(promoted["control_ratio_premay_max"], errors="coerce") < 1.0).all():
        blockers.append("control_dominated_promotion_detected")

    if blockers:
        if "l7_only_promotion_detected" in blockers:
            decision = "HOLD_A7AIF4_ONLY_L7_RANKED_LABEL_EVIDENCE"
        elif "control_dominated_promotion_detected" in blockers:
            decision = "HOLD_A7AIF4_CONTROL_DOMINATED_RESPONSE"
        else:
            decision = "HOLD_A7AIF4_NO_RESPONSE_BACKED_ALPHA_FIELDS"
    else:
        decision = "PASS_A7AIF4_ORDINARY_ALPHA_SEEDS_FOUND"

    promotion_audit.to_csv(RUNTIME / "a7aif4_candidate_field_promotion.csv", index=False)
    promoted.to_csv(RUNTIME / "a7aif4_promoted_ordinary_alpha_fields.csv", index=False)
    blocked.to_csv(RUNTIME / "a7aif4_demoted_or_blocked_fields.csv", index=False)
    role_transition.to_csv(RUNTIME / "a7aif4_role_transition_audit.csv", index=False)
    ledger_preview.to_csv(RUNTIME / "a7aif4_enforcement_ledger_v2_preview.csv", index=False)
    prereq.to_csv(RUNTIME / "a7aif4_prerequisite_audit.csv", index=False)

    manifest = {
        "stage": "A7AI-F4",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "executes_generation": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "active_non_l7_labels": sorted(active_non_l7),
        "response_candidate_rows": int(len(candidates)),
        "promotion_audit_rows": int(len(promotion_audit)),
        "promoted_field_count": int(promoted["field_name"].nunique()) if not promoted.empty else 0,
        "promoted_evidence_rows": int(len(promoted)),
        "authorizes_a7pool0": decision.startswith("PASS_"),
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7aif4_manifest.json", manifest)

    lines = [
        "# CRYPTO A7AI-F4 RESPONSE-BACKED FIELD PROMOTION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7AI-F4 promotes fields only when non-L7 primitive response evidence is control-clean, lag-surviving, materialized, and ordinary-alpha contract clean.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Promoted Ordinary-Alpha Fields",
        "",
        md_table(promoted, 40),
        "",
        "## Blocked Response Candidates",
        "",
        md_table(blocked, 80),
        "",
        "## Boundary",
        "",
        "```text",
        "A7AI-F4 does not generate formulas, replay candidates, or authorize alpha proof.",
        "Risk-defense and diagnostic-only fields are not promoted as standalone ordinary-alpha seeds.",
        "L7 ranked-return-only evidence is insufficient for ordinary-alpha promotion.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
