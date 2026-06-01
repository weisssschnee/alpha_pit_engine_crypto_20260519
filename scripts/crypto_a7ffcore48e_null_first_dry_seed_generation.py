from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore48e_null_first_dry_seed_generation"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE48E_NULL_FIRST_DRY_SEED_GENERATION_20260602.md"
CORE48 = REPO / "runtime" / "a7ffcore48_null_first_seed_generation_contract" / "a7ffcore48_manifest.json"
ONTOLOGY = REPO / "runtime" / "a7ffr1_field_ontology_v3" / "a7ffr1_field_ontology_v3.csv"
OPERATOR_RESPONSE = REPO / "runtime" / "a7ffr2_operator_probing_v2" / "a7ffr2_observed_operator_response.csv"
PAIR_POLICY = REPO / "runtime" / "a7ffr3_feature_pair_policy_v2" / "a7ffr3_feature_pair_policy_v2.csv"

WINDOWS = [4, 8, 24, 72, 168]
MAX_SEEDS = 1200
REPAIR_OPERATORS = ["SpreadShortLong", "WinsorZ"]


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
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


def expression(operator: str, left: str, right: str | None, window: int) -> str:
    if right is None or right == "":
        if operator == "Delta":
            return f"Delta({left},{window})"
        if operator == "CSRank":
            return f"CSRank({left})"
        if operator == "Identity":
            return f"ZScore({left})"
        if operator == "SpreadShortLong":
            return f"Sub(ZScore(Mean({left},{window})),ZScore(Mean({left},{min(window * 4, 336)})))"
        if operator == "WinsorZ":
            return f"Clip(ZScore(Delta({left},{window})),-3,3)"
        return f"{operator}({left},{window})"
    if operator == "Delta":
        return f"Mul(Delta({left},{window}),ZScore(Delta({right},{window})))"
    if operator == "CSRank":
        return f"Mul(CSRank({left}),Sign(Delta({right},{window})))"
    if operator == "Identity":
        return f"Mul(ZScore({left}),Sign(Delta({right},{window})))"
    if operator == "SpreadShortLong":
        return f"Sub(ZScore(Mean({left},{window})),ZScore(Mean({right},{min(window * 4, 336)})))"
    if operator == "WinsorZ":
        return f"Mul(Clip(ZScore(Delta({left},{window})),-3,3),Sign(Delta({right},{window})))"
    return f"Mul({operator}({left},{window}),ZScore(Delta({right},{window})))"


def evidence_tag(row: pd.Series, op_row: pd.Series | None) -> tuple[str, float]:
    best_control = pd.to_numeric(row.get("best_control_ratio"), errors="coerce")
    non_l7 = pd.to_numeric(row.get("non_l7_candidate_count"), errors="coerce")
    op_margin = float(op_row["min_control_ratio"]) if op_row is not None and "min_control_ratio" in op_row else float("nan")
    if pd.notna(non_l7) and float(non_l7) > 0:
        return "direct_non_l7_response", float(min(best_control if pd.notna(best_control) else 99, op_margin if pd.notna(op_margin) else 99))
    if pd.notna(best_control) and float(best_control) < 1.0:
        return "field_control_clean_nearmiss", float(best_control)
    if pd.notna(op_margin) and float(op_margin) < 1.0:
        return "operator_control_clean_nearmiss", float(op_margin)
    return "weak_or_pending", float(best_control) if pd.notna(best_control) else 99.0


def candidate_status(role: str, evidence: str, operator_native: bool, margin: float) -> tuple[str, str]:
    if "forbidden" in role or "blocked" in role:
        return "rejected", "role_forbidden"
    if evidence == "weak_or_pending":
        return "diagnostic_pending", "weak_response_or_control_margin"
    if not operator_native:
        return "diagnostic_pending", "operator_not_natively_probed"
    if margin >= 1.0:
        return "diagnostic_pending", "control_margin_not_clean"
    if role in {"ordinary_alpha_seed", "exploratory_signal_seed"}:
        return "eligible_null_first_seed", "pass"
    if role == "regime_neutralizer_interaction_seed":
        return "eligible_interaction_seed", "pass_interaction_only"
    return "diagnostic_pending", "unknown_role"


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    source = read_json(CORE48)
    if source.get("decision") != "PASS_A7FFCORE48_NULL_FIRST_SEED_GENERATION_CONTRACT_READY_FOR_CORE48E":
        raise SystemExit(f"CORE48 not ready for CORE48E: {source.get('decision')}")

    ontology = pd.read_csv(ONTOLOGY)
    operator_response = pd.read_csv(OPERATOR_RESPONSE)
    pair_policy = pd.read_csv(PAIR_POLICY)
    op_lookup = {
        (str(r["semantic_type_v3"]), str(r["operator"])): r
        for _, r in operator_response.iterrows()
    }
    fields = ontology[
        ontology["compiler_role_v3"].astype(str).isin(
            ["ordinary_alpha_seed", "exploratory_signal_seed", "regime_neutralizer_interaction_seed"]
        )
    ].copy()
    rows: list[dict[str, Any]] = []

    # N0 single-field seeds.
    for _, field in fields.iterrows():
        semantic = str(field["semantic_type_v3"])
        role = str(field["compiler_role_v3"])
        operators = sorted({op for (stype, op) in op_lookup if stype == semantic})
        for operator in operators:
            op_row = op_lookup.get((semantic, operator))
            evidence, margin = evidence_tag(field, op_row)
            status, reason = candidate_status(role, evidence, True, margin)
            for window in WINDOWS:
                rows.append(
                    {
                        "lane_id": "N0_single_field_operator_seed",
                        "field_primary": field["field_name"],
                        "field_partner": "",
                        "semantic_type_primary": semantic,
                        "semantic_type_partner": "",
                        "semantic_pair": semantic,
                        "operator": operator,
                        "window_h": window,
                        "expression": expression(operator, str(field["field_name"]), None, window),
                        "compiler_role": role,
                        "non_l7_evidence": evidence,
                        "operator_null_margin": margin,
                        "role_gate_status": "pass" if status != "rejected" else "fail",
                        "reject_reason": reason,
                        "candidate_status": status,
                    }
                )
        # Repair operators are generated but not eligible until operator probing catches up.
        for operator in REPAIR_OPERATORS:
            evidence, margin = evidence_tag(field, None)
            status, reason = candidate_status(role, evidence, False, margin)
            for window in WINDOWS:
                rows.append(
                    {
                        "lane_id": "N3_control_repair_seed",
                        "field_primary": field["field_name"],
                        "field_partner": "",
                        "semantic_type_primary": semantic,
                        "semantic_type_partner": "",
                        "semantic_pair": semantic,
                        "operator": operator,
                        "window_h": window,
                        "expression": expression(operator, str(field["field_name"]), None, window),
                        "compiler_role": role,
                        "non_l7_evidence": evidence,
                        "operator_null_margin": margin,
                        "role_gate_status": "pass" if status != "rejected" else "fail",
                        "reject_reason": reason,
                        "candidate_status": status,
                    }
                )

    field_role = fields.set_index("field_name")["compiler_role_v3"].to_dict()
    field_semantic = fields.set_index("field_name")["semantic_type_v3"].to_dict()
    # N1/N2 pair seeds.
    for _, pair in pair_policy.iterrows():
        left = str(pair["left_field"])
        right = str(pair["right_field"])
        if left not in field_role or right not in field_role:
            continue
        left_sem = str(field_semantic[left])
        right_sem = str(field_semantic[right])
        role = str(field_role[left])
        operators = sorted({op for (stype, op) in op_lookup if stype == left_sem})
        pair_lane = "N2_regime_conditioned_seed" if "regime" in str(field_role[right]) else "N1_role_compatible_pair_seed"
        left_row = fields[fields["field_name"].eq(left)].iloc[0]
        for operator in operators:
            op_row = op_lookup.get((left_sem, operator))
            evidence, margin = evidence_tag(left_row, op_row)
            status, reason = candidate_status(role, evidence, True, margin)
            for window in WINDOWS:
                rows.append(
                    {
                        "lane_id": pair_lane,
                        "field_primary": left,
                        "field_partner": right,
                        "semantic_type_primary": left_sem,
                        "semantic_type_partner": right_sem,
                        "semantic_pair": str(pair["semantic_pair"]),
                        "operator": operator,
                        "window_h": window,
                        "expression": expression(operator, left, right, window),
                        "compiler_role": role,
                        "non_l7_evidence": evidence,
                        "operator_null_margin": margin,
                        "role_gate_status": "pass" if status != "rejected" else "fail",
                        "reject_reason": reason,
                        "candidate_status": status,
                    }
                )

    pool = pd.DataFrame(rows).drop_duplicates(subset=["lane_id", "expression"]).reset_index(drop=True)
    if pool.shape[0] > MAX_SEEDS:
        eligible_first = pool.assign(
            _priority=pool["candidate_status"].map(
                {"eligible_null_first_seed": 0, "eligible_interaction_seed": 1, "diagnostic_pending": 2, "rejected": 3}
            ).fillna(9)
        ).sort_values(["_priority", "operator_null_margin", "semantic_pair", "operator"])
        pool = eligible_first.head(MAX_SEEDS).drop(columns=["_priority"]).reset_index(drop=True)
    pool.insert(0, "seed_id", [f"a7ffcore48e_{i:04d}" for i in range(pool.shape[0])])

    eligible_mask = pool["candidate_status"].isin(["eligible_null_first_seed", "eligible_interaction_seed"])
    eligible = pool[eligible_mask].copy()
    family_counts = eligible["semantic_pair"].value_counts(normalize=True) if not eligible.empty else pd.Series(dtype=float)
    motif_counts = eligible["operator"].value_counts(normalize=True) if not eligible.empty else pd.Series(dtype=float)
    pool["family_cap_status"] = pool["semantic_pair"].map(lambda x: "pass" if family_counts.get(x, 0.0) <= 0.35 else "cap_warning")
    summary = pd.DataFrame(
        [
            {"metric": "generated_seed_count", "value": int(pool.shape[0]), "pass": bool(pool.shape[0] >= 400)},
            {"metric": "eligible_seed_count", "value": int(eligible.shape[0]), "pass": bool(eligible.shape[0] >= 120)},
            {"metric": "semantic_family_count", "value": int(eligible["semantic_pair"].nunique()) if not eligible.empty else 0, "pass": bool(not eligible.empty and eligible["semantic_pair"].nunique() >= 5)},
            {"metric": "operator_count", "value": int(eligible["operator"].nunique()) if not eligible.empty else 0, "pass": bool(not eligible.empty and eligible["operator"].nunique() >= 4)},
            {"metric": "role_violation_count", "value": int(pool["role_gate_status"].eq("fail").sum()), "pass": bool(pool["role_gate_status"].eq("fail").sum() == 0)},
            {"metric": "missing_contract_count", "value": 0, "pass": True},
            {"metric": "family_cap_violation_count", "value": int((family_counts > 0.35).sum()) if not family_counts.empty else 0, "pass": bool(family_counts.empty or (family_counts <= 0.35).all())},
            {"metric": "motif_cap_violation_count", "value": int((motif_counts > 0.25).sum()) if not motif_counts.empty else 0, "pass": bool(motif_counts.empty or (motif_counts <= 0.25).all())},
        ]
    )
    reject_summary = (
        pool.groupby(["candidate_status", "reject_reason"], as_index=False)
        .agg(seed_count=("seed_id", "count"))
        .sort_values("seed_count", ascending=False)
    )
    family_operator_summary = (
        pool.groupby(["semantic_pair", "operator", "candidate_status"], as_index=False)
        .agg(seed_count=("seed_id", "count"), min_null_margin=("operator_null_margin", "min"))
        .sort_values(["candidate_status", "seed_count"], ascending=[True, False])
    )
    decision = (
        "PASS_A7FFCORE48E_NULL_FIRST_DRY_SEEDS_READY_FOR_CORE49_CONTRACT"
        if bool(summary["pass"].all())
        else "HOLD_A7FFCORE48E_NULL_FIRST_DRY_SEEDS_INSUFFICIENT"
    )
    authorization = {
        "authorized": {
            "A7FF-CORE49 full-universe null-vector preflight contract": decision.startswith("PASS"),
            "A7FF-CORE48R dry seed generation forensic": not decision.startswith("PASS"),
        },
        "not_authorized": {
            "numeric_replay": True,
            "formula_search": True,
            "large_search": True,
            "alpha_proof": True,
            "shadow_paper_live": True,
            "promotion": True,
        },
    }
    manifest = {
        "stage": "A7FF-CORE48E",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE48",
        "source_decision": source.get("decision"),
        "decision": decision,
        "generated_seed_count": int(pool.shape[0]),
        "eligible_seed_count": int(eligible.shape[0]),
        "eligible_semantic_family_count": int(eligible["semantic_pair"].nunique()) if not eligible.empty else 0,
        "eligible_operator_count": int(eligible["operator"].nunique()) if not eligible.empty else 0,
        "executes_generation": True,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core49_contract": decision.startswith("PASS"),
        "authorizes_core48r_forensic": not decision.startswith("PASS"),
        "authorizes_numeric_replay": False,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE49 full-universe null-vector preflight contract"
        if decision.startswith("PASS")
        else "A7FF-CORE48R dry seed generation forensic",
    }
    pool.to_csv(RUNTIME / "a7ffcore48e_generated_seed_pool.csv", index=False)
    eligible.to_csv(RUNTIME / "a7ffcore48e_eligible_seed_queue.csv", index=False)
    summary.to_csv(RUNTIME / "a7ffcore48e_quality_gate.csv", index=False)
    reject_summary.to_csv(RUNTIME / "a7ffcore48e_reject_reason_summary.csv", index=False)
    family_operator_summary.to_csv(RUNTIME / "a7ffcore48e_family_operator_summary.csv", index=False)
    write_json(RUNTIME / "a7ffcore48e_authorization_matrix.json", authorization)
    write_json(RUNTIME / "a7ffcore48e_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE48E NULL-FIRST DRY SEED GENERATION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE48E performs bounded dry seed generation under the null-first contract. It does not run numeric replay, formula search, large search, proof, shadow, paper, live, or promotion.",
        "",
        "## Quality Gate",
        "",
        md_table(summary),
        "",
        "## Reject Reason Summary",
        "",
        md_table(reject_summary),
        "",
        "## Family Operator Summary",
        "",
        md_table(family_operator_summary),
        "",
        "## Eligible Seed Preview",
        "",
        md_table(eligible.head(80)),
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
