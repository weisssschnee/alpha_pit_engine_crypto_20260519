from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from crypto_a7ffcore48e_null_first_dry_seed_generation import expression


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore48se_repaired_null_first_dry_generation"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE48SE_REPAIRED_NULL_FIRST_DRY_GENERATION_20260602.md"
CORE48S = REPO / "runtime" / "a7ffcore48s_operator_null_coverage_repair_contract" / "a7ffcore48s_manifest.json"
ONTOLOGY = REPO / "runtime" / "a7ffr1_field_ontology_v3" / "a7ffr1_field_ontology_v3.csv"
OPERATOR_RESPONSE = REPO / "runtime" / "a7ffr2_operator_probing_v2" / "a7ffr2_observed_operator_response.csv"
PAIR_POLICY = REPO / "runtime" / "a7ffr3_feature_pair_policy_v2" / "a7ffr3_feature_pair_policy_v2.csv"
REPAIR_SET = REPO / "runtime" / "a7ffcore48s_operator_null_coverage_repair_contract" / "a7ffcore48s_operator_repair_set.csv"

WINDOWS = [4, 8, 24, 72, 168]
MAX_SEEDS = 1800
MAX_OPERATOR_SHARE = 0.25
MAX_FAMILY_SHARE = 0.35


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


def native_margin(op_response: pd.DataFrame, semantic: str, operator: str) -> float | None:
    sub = op_response[op_response["semantic_type_v3"].astype(str).eq(semantic)]
    exact = sub[sub["operator"].astype(str).eq(operator)]
    if not exact.empty:
        return float(pd.to_numeric(exact["min_control_ratio"], errors="coerce").min())
    if sub.empty:
        return None
    return float(pd.to_numeric(sub["min_control_ratio"], errors="coerce").min())


def field_margin(field: pd.Series) -> float:
    val = pd.to_numeric(field.get("best_control_ratio"), errors="coerce")
    return float(val) if pd.notna(val) else 99.0


def repaired_expression(operator: str, left: str, right: str | None, window: int) -> str:
    if operator == "AbsDelta":
        if right:
            return f"Mul(Abs(Delta({left},{window})),Sign(Delta({right},{window})))"
        return f"Abs(Delta({left},{window}))"
    if operator == "SignedRankDelta":
        if right:
            return f"Mul(CSRank(Delta({left},{window})),Sign(Delta({right},{window})))"
        return f"CSRank(Delta({left},{window}))"
    return expression(operator, left, right, window)


def status_for(role: str, margin: float, evidence: str) -> tuple[str, str]:
    if "forbidden" in role or "blocked" in role:
        return "rejected", "role_forbidden"
    if evidence == "weak_or_pending":
        return "diagnostic_pending", "weak_response_or_control_margin"
    if margin >= 1.0:
        return "diagnostic_pending", "control_margin_not_clean"
    if role in {"ordinary_alpha_seed", "exploratory_signal_seed"}:
        return "eligible_null_first_seed", "pass"
    if role == "regime_neutralizer_interaction_seed":
        return "eligible_interaction_seed", "pass_interaction_only"
    return "diagnostic_pending", "unknown_role"


def evidence_for(field: pd.Series, margin: float) -> str:
    non_l7 = pd.to_numeric(field.get("non_l7_candidate_count"), errors="coerce")
    if pd.notna(non_l7) and float(non_l7) > 0:
        return "direct_non_l7_response"
    if margin < 1.0:
        return "operator_or_field_control_clean_nearmiss"
    return "weak_or_pending"


def select_balanced(pool: pd.DataFrame) -> pd.DataFrame:
    eligible = pool[pool["candidate_status"].isin(["eligible_null_first_seed", "eligible_interaction_seed"])].copy()
    eligible = eligible.sort_values(["operator_null_margin", "semantic_pair", "operator", "lane_id"])
    max_per_operator = int(MAX_SEEDS * MAX_OPERATOR_SHARE)
    max_per_family = int(MAX_SEEDS * MAX_FAMILY_SHARE)
    max_repair = int(MAX_SEEDS * 0.55)
    selected: list[pd.Series] = []
    op_counts: dict[str, int] = {}
    fam_counts: dict[str, int] = {}
    seen_expr: set[str] = set()
    repair_count = 0
    groups = [
        group.reset_index(drop=True)
        for _, group in eligible.groupby(["semantic_pair", "operator"], sort=True)
    ]
    positions = [0 for _ in groups]
    progressed = True
    while progressed and len(selected) < MAX_SEEDS:
        progressed = False
        for i, group in enumerate(groups):
            while positions[i] < group.shape[0]:
                row = group.iloc[positions[i]]
                positions[i] += 1
                op = str(row["operator"])
                fam = str(row["semantic_pair"])
                expr = str(row["expression"])
                is_repair = str(row.get("operator_origin", "")) == "repaired_native_proxy"
                if expr in seen_expr:
                    continue
                if op_counts.get(op, 0) >= max_per_operator:
                    continue
                if fam_counts.get(fam, 0) >= max_per_family:
                    continue
                if is_repair and repair_count >= max_repair:
                    continue
                selected.append(row)
                seen_expr.add(expr)
                op_counts[op] = op_counts.get(op, 0) + 1
                fam_counts[fam] = fam_counts.get(fam, 0) + 1
                repair_count += int(is_repair)
                progressed = True
                break
            if len(selected) >= MAX_SEEDS:
                break
    return pd.DataFrame(selected).reset_index(drop=True) if selected else pd.DataFrame(columns=pool.columns)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    source = read_json(CORE48S)
    if source.get("decision") != "PASS_A7FFCORE48S_OPERATOR_NULL_COVERAGE_REPAIR_CONTRACT_READY_FOR_CORE48SE":
        raise SystemExit(f"CORE48S not ready for CORE48SE: {source.get('decision')}")

    ontology = pd.read_csv(ONTOLOGY)
    op_response = pd.read_csv(OPERATOR_RESPONSE)
    pair_policy = pd.read_csv(PAIR_POLICY)
    repair_set = pd.read_csv(REPAIR_SET)
    fields = ontology[
        ontology["compiler_role_v3"].astype(str).isin(
            ["ordinary_alpha_seed", "exploratory_signal_seed", "regime_neutralizer_interaction_seed"]
        )
    ].copy()
    native_ops = sorted(op_response["operator"].astype(str).unique().tolist())
    repair_ops = sorted(repair_set["operator"].astype(str).unique().tolist())
    all_ops = sorted(set(native_ops).union(repair_ops))
    rows: list[dict[str, Any]] = []

    for _, field in fields.iterrows():
        left = str(field["field_name"])
        semantic = str(field["semantic_type_v3"])
        role = str(field["compiler_role_v3"])
        for op in all_ops:
            margin_base = native_margin(op_response, semantic, op)
            margin = min(field_margin(field), margin_base if margin_base is not None else field_margin(field))
            evidence = evidence_for(field, margin)
            status, reason = status_for(role, margin, evidence)
            op_origin = "native" if op in native_ops else "repaired_native_proxy"
            for window in WINDOWS:
                rows.append(
                    {
                        "lane_id": "N0_single_field_operator_seed" if op in native_ops else "N3_control_repair_seed",
                        "field_primary": left,
                        "field_partner": "",
                        "semantic_type_primary": semantic,
                        "semantic_type_partner": "",
                        "semantic_pair": semantic,
                        "operator": op,
                        "operator_origin": op_origin,
                        "window_h": window,
                        "expression": repaired_expression(op, left, None, window),
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
    field_rows = {str(r["field_name"]): r for _, r in fields.iterrows()}
    for _, pair in pair_policy.iterrows():
        left = str(pair["left_field"])
        right = str(pair["right_field"])
        if left not in field_role or right not in field_role:
            continue
        left_sem = str(field_semantic[left])
        right_sem = str(field_semantic[right])
        role = str(field_role[left])
        pair_lane = "N2_regime_conditioned_seed" if "regime" in str(field_role[right]) else "N1_role_compatible_pair_seed"
        for op in all_ops:
            margin_base = native_margin(op_response, left_sem, op)
            margin = min(field_margin(field_rows[left]), margin_base if margin_base is not None else field_margin(field_rows[left]))
            evidence = evidence_for(field_rows[left], margin)
            status, reason = status_for(role, margin, evidence)
            op_origin = "native" if op in native_ops else "repaired_native_proxy"
            for window in WINDOWS:
                rows.append(
                    {
                        "lane_id": pair_lane,
                        "field_primary": left,
                        "field_partner": right,
                        "semantic_type_primary": left_sem,
                        "semantic_type_partner": right_sem,
                        "semantic_pair": str(pair["semantic_pair"]),
                        "operator": op,
                        "operator_origin": op_origin,
                        "window_h": window,
                        "expression": repaired_expression(op, left, right, window),
                        "compiler_role": role,
                        "non_l7_evidence": evidence,
                        "operator_null_margin": margin,
                        "role_gate_status": "pass" if status != "rejected" else "fail",
                        "reject_reason": reason,
                        "candidate_status": status,
                    }
                )

    pool = pd.DataFrame(rows).drop_duplicates(subset=["lane_id", "expression"]).reset_index(drop=True)
    selected = select_balanced(pool)
    selected.insert(0, "seed_id", [f"a7ffcore48se_{i:04d}" for i in range(selected.shape[0])])
    selected["family_cap_status"] = "pass"
    selected["motif_cap_status"] = "pass"
    op_share = selected["operator"].value_counts(normalize=True) if not selected.empty else pd.Series(dtype=float)
    fam_share = selected["semantic_pair"].value_counts(normalize=True) if not selected.empty else pd.Series(dtype=float)
    repair_share = float(selected["operator_origin"].eq("repaired_native_proxy").mean()) if not selected.empty else 0.0
    quality = pd.DataFrame(
        [
            {"metric": "generated_seed_count", "value": int(pool.shape[0]), "pass": bool(pool.shape[0] >= 1200)},
            {"metric": "eligible_seed_count", "value": int(selected.shape[0]), "pass": bool(selected.shape[0] >= 360)},
            {"metric": "semantic_family_count", "value": int(selected["semantic_pair"].nunique()) if not selected.empty else 0, "pass": bool(not selected.empty and selected["semantic_pair"].nunique() >= 8)},
            {"metric": "operator_count", "value": int(selected["operator"].nunique()) if not selected.empty else 0, "pass": bool(not selected.empty and selected["operator"].nunique() >= 5)},
            {"metric": "motif_cap_violation_count", "value": int((op_share > MAX_OPERATOR_SHARE).sum()) if not op_share.empty else 0, "pass": bool(op_share.empty or (op_share <= MAX_OPERATOR_SHARE).all())},
            {"metric": "family_cap_violation_count", "value": int((fam_share > MAX_FAMILY_SHARE).sum()) if not fam_share.empty else 0, "pass": bool(fam_share.empty or (fam_share <= MAX_FAMILY_SHARE).all())},
            {"metric": "role_violation_count", "value": int(selected["role_gate_status"].eq("fail").sum()) if not selected.empty else 0, "pass": bool(selected.empty or selected["role_gate_status"].eq("fail").sum() == 0)},
            {"metric": "repair_operator_share", "value": repair_share, "pass": bool(repair_share <= 0.55)},
        ]
    )
    operator_summary = (
        selected.groupby(["operator", "operator_origin"], as_index=False)
        .agg(seed_count=("seed_id", "count"), semantic_family_count=("semantic_pair", "nunique"), min_null_margin=("operator_null_margin", "min"))
        .sort_values("seed_count", ascending=False)
    )
    family_summary = (
        selected.groupby("semantic_pair", as_index=False)
        .agg(seed_count=("seed_id", "count"), operator_count=("operator", "nunique"), min_null_margin=("operator_null_margin", "min"))
        .sort_values("seed_count", ascending=False)
    )
    decision = (
        "PASS_A7FFCORE48SE_REPAIRED_DRY_SEEDS_READY_FOR_CORE49_CONTRACT"
        if bool(quality["pass"].all())
        else "HOLD_A7FFCORE48SE_REPAIRED_DRY_SEEDS_INSUFFICIENT"
    )
    authorization = {
        "authorized": {
            "A7FF-CORE49 full-universe null-vector preflight contract": decision.startswith("PASS"),
            "A7FF-CORE48SER repaired dry seed forensic": not decision.startswith("PASS"),
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
        "stage": "A7FF-CORE48SE",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE48S",
        "source_decision": source.get("decision"),
        "decision": decision,
        "generated_seed_count": int(pool.shape[0]),
        "eligible_seed_count": int(selected.shape[0]),
        "eligible_semantic_family_count": int(selected["semantic_pair"].nunique()) if not selected.empty else 0,
        "eligible_operator_count": int(selected["operator"].nunique()) if not selected.empty else 0,
        "repair_operator_share": repair_share,
        "executes_generation": True,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core49_contract": decision.startswith("PASS"),
        "authorizes_core48ser_forensic": not decision.startswith("PASS"),
        "authorizes_numeric_replay": False,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE49 full-universe null-vector preflight contract" if decision.startswith("PASS") else "A7FF-CORE48SER repaired dry seed forensic",
    }
    pool.to_csv(RUNTIME / "a7ffcore48se_full_repaired_seed_pool.csv", index=False)
    selected.to_csv(RUNTIME / "a7ffcore48se_eligible_seed_queue.csv", index=False)
    quality.to_csv(RUNTIME / "a7ffcore48se_quality_gate.csv", index=False)
    operator_summary.to_csv(RUNTIME / "a7ffcore48se_operator_summary.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ffcore48se_family_summary.csv", index=False)
    write_json(RUNTIME / "a7ffcore48se_authorization_matrix.json", authorization)
    write_json(RUNTIME / "a7ffcore48se_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE48SE REPAIRED NULL-FIRST DRY GENERATION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE48SE runs bounded repaired dry seed generation after CORE48S. It does not run numeric replay, formula search, large search, proof, shadow, paper, live, or promotion.",
        "",
        "## Quality Gate",
        "",
        md_table(quality),
        "",
        "## Operator Summary",
        "",
        md_table(operator_summary),
        "",
        "## Family Summary",
        "",
        md_table(family_summary),
        "",
        "## Eligible Seed Preview",
        "",
        md_table(selected.head(80)),
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
