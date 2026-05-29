from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7aa2_feature_role_classification"
REPORT = REPO / "reports" / "CRYPTO_A7AA2_FEATURE_ROLE_CLASSIFICATION_20260529.md"
A7AA1_MANIFEST = REPO / "runtime" / "a7aa1_primitive_response_map" / "a7aa1_manifest.json"
A7AA1_RESPONSE = REPO / "runtime" / "a7aa1_primitive_response_map" / "a7aa1_primitive_response_map.csv"
A7AA1_CANDIDATES = REPO / "runtime" / "a7aa1_primitive_response_map" / "a7aa1_primitive_response_candidates.csv"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def classify_role(candidate_count: int, stable_count: int, control_like_count: int, total: int) -> tuple[str, str]:
    if candidate_count > 0:
        return "predictive_signal_candidate", "has_control_clean_lag_surviving_primitive_response"
    if stable_count >= max(3, total // 4) and control_like_count >= stable_count:
        return "control_like_or_risk_exposure", "premay_stable_but_control_like"
    if stable_count >= max(3, total // 4):
        return "regime_state_or_interaction_input", "premay_stable_without_clean_candidate_gate"
    return "weak_or_unstable", "mostly_premay_unstable"


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    manifest1 = read_json(A7AA1_MANIFEST)
    if not manifest1.get("authorizes_a7aa2_feature_role_classification"):
        raise SystemExit("A7AA-1 does not authorize A7AA-2")
    response = pd.read_csv(A7AA1_RESPONSE)
    candidates = pd.read_csv(A7AA1_CANDIDATES) if A7AA1_CANDIDATES.exists() else pd.DataFrame()

    field_rows = []
    for field, group in response.groupby("field_name", dropna=False):
        total = int(len(group))
        candidate_count = int(group["decision"].eq("A7AA1_PRIMITIVE_RESPONSE_CANDIDATE").sum())
        stable_count = int(group["premay_all_positive"].astype(str).str.lower().isin(["true", "1"]).sum())
        control_like_count = int(group["decision"].eq("HOLD_A7AA1_CONTROL_LIKE").sum())
        lag_fragile_count = int(group["decision"].eq("HOLD_A7AA1_LAG_FRAGILE").sum())
        unstable_count = int(group["decision"].eq("HOLD_A7AA1_PRE_MAY_UNSTABLE").sum())
        role, reason = classify_role(candidate_count, stable_count, control_like_count, total)
        field_rows.append(
            {
                "field_name": field,
                "field_family": group["field_family"].dropna().astype(str).iloc[0] if len(group) else "",
                "feature_role": role,
                "reason": reason,
                "total_tests": total,
                "primitive_response_candidate_count": candidate_count,
                "premay_stable_count": stable_count,
                "control_like_count": control_like_count,
                "lag_fragile_count": lag_fragile_count,
                "premay_unstable_count": unstable_count,
                "best_label_families": "|".join(sorted(group.loc[group["decision"].eq("A7AA1_PRIMITIVE_RESPONSE_CANDIDATE"), "label_family"].dropna().astype(str).unique())),
                "best_horizons": "|".join(map(str, sorted(group.loc[group["decision"].eq("A7AA1_PRIMITIVE_RESPONSE_CANDIDATE"), "label_horizon_h"].dropna().astype(int).unique()))),
                "best_transforms": "|".join(sorted(group.loc[group["decision"].eq("A7AA1_PRIMITIVE_RESPONSE_CANDIDATE"), "transform"].dropna().astype(str).unique())),
            }
        )
    field_roles = pd.DataFrame(field_rows).sort_values(
        ["primitive_response_candidate_count", "premay_stable_count", "field_name"],
        ascending=[False, False, True],
    )
    family_roles = (
        field_roles.groupby("field_family", dropna=False)
        .agg(
            field_count=("field_name", "count"),
            signal_candidate_fields=("feature_role", lambda s: int((s == "predictive_signal_candidate").sum())),
            risk_or_control_fields=("feature_role", lambda s: int((s == "control_like_or_risk_exposure").sum())),
            weak_fields=("feature_role", lambda s: int((s == "weak_or_unstable").sum())),
        )
        .reset_index()
        .sort_values(["signal_candidate_fields", "field_count"], ascending=[False, False])
    )
    selector_seeds = field_roles[field_roles["feature_role"].eq("predictive_signal_candidate")].copy()
    selector_policy = {
        "selector_rewrite_status": "primitive_response_first",
        "allowed_seed_fields": selector_seeds["field_name"].tolist(),
        "allowed_label_focus": sorted(candidates["label_family"].dropna().astype(str).unique().tolist()) if not candidates.empty else [],
        "allowed_horizon_focus": sorted(map(int, candidates["label_horizon_h"].dropna().astype(int).unique().tolist())) if not candidates.empty else [],
        "blocked_until_response_evidence": field_roles.loc[~field_roles["feature_role"].eq("predictive_signal_candidate"), "field_name"].tolist(),
        "formula_search_authorized": False,
        "large_search_authorized": False,
        "alpha_proof_authorized": False,
    }
    candidate_fields = int((field_roles["feature_role"] == "predictive_signal_candidate").sum())
    decision = (
        "PASS_A7AA2_FEATURE_ROLES_READY_FOR_SELECTOR_REWRITE_CONTRACT"
        if candidate_fields > 0
        else "HOLD_A7AA2_NO_SIGNAL_CANDIDATE_FIELDS"
    )
    manifest = {
        "stage": "A7AA-2",
        "generated_at": now_utc(),
        "decision": decision,
        "executes_role_classification": True,
        "executes_search": False,
        "executes_training": False,
        "authorizes_a7aa3_selector_rewrite_contract": candidate_fields > 0,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "source_a7aa1_decision": manifest1.get("decision"),
        "field_count": int(len(field_roles)),
        "signal_candidate_field_count": candidate_fields,
        "uses_may": False,
    }
    field_roles.to_csv(RUNTIME / "a7aa2_feature_role_ledger.csv", index=False)
    family_roles.to_csv(RUNTIME / "a7aa2_family_role_summary.csv", index=False)
    selector_seeds.to_csv(RUNTIME / "a7aa2_selector_seed_fields.csv", index=False)
    write_json(RUNTIME / "a7aa2_selector_rewrite_seed_policy.json", selector_policy)
    write_json(RUNTIME / "a7aa2_manifest.json", manifest)
    write_json(
        RUNTIME / "a7aa2_authorization_matrix.json",
        {
            "A7AA-2": {"status": decision},
            "a7aa3_selector_rewrite_contract": {"authorized": candidate_fields > 0},
            "formula_search": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof_shadow_paper_live": {"authorized": False},
        },
    )
    lines = [
        "# CRYPTO A7AA-2 FEATURE ROLE CLASSIFICATION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7AA-2 classifies primitive fields by observed response role. It does not authorize formula search.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Selector Seed Fields",
        "",
        md_table(selector_seeds, 80),
        "",
        "## Family Role Summary",
        "",
        md_table(family_roles, 80),
        "",
        "## Feature Role Ledger",
        "",
        md_table(field_roles, 80),
        "",
        "## Boundary",
        "",
        "```text",
        "Formula search remains not authorized.",
        "Fields without primitive response evidence are blocked from being primary selector seeds.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
