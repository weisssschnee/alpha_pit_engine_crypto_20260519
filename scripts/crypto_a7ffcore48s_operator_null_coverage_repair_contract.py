from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore48s_operator_null_coverage_repair_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE48S_OPERATOR_NULL_COVERAGE_REPAIR_CONTRACT_20260602.md"
CORE48R = REPO / "runtime" / "a7ffcore48r_dry_seed_generation_forensic" / "a7ffcore48r_manifest.json"


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


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    source = read_json(CORE48R)
    if source.get("decision") != "PASS_A7FFCORE48R_DRY_SEED_FORENSIC_READY_FOR_CORE48S_OPERATOR_REPAIR":
        raise SystemExit(f"CORE48R not ready for CORE48S: {source.get('decision')}")

    repair_policy = pd.DataFrame(
        [
            {
                "policy_id": "P0_repair_operator_breadth_not_field_breadth",
                "description": "CORE48E already has 1200 eligible seeds and 12 semantic families; repair target is operator/motif breadth",
                "hard_requirement": True,
            },
            {
                "policy_id": "P1_no_unprobed_operator_promotion",
                "description": "new operators may enter repaired queue only if assigned native null-margin proxy and marked repaired_native",
                "hard_requirement": True,
            },
            {
                "policy_id": "P2_keep_null_first_gate",
                "description": "operators do not bypass original-vs-null margin, role, family, or motif gates",
                "hard_requirement": True,
            },
            {
                "policy_id": "P3_no_replay_search",
                "description": "CORE48S/48SE do not authorize numeric replay, formula search, large search, proof, shadow, paper, live, or promotion",
                "hard_requirement": True,
            },
        ]
    )
    operator_repair_set = pd.DataFrame(
        [
            {
                "operator": "SpreadShortLong",
                "repair_status": "authorized_for_repaired_native_probe",
                "economic_role": "relative-value / slow-fast dislocation",
                "null_margin_proxy": "base semantic-type best native operator margin, capped by field best_control_ratio",
            },
            {
                "operator": "WinsorZ",
                "repair_status": "authorized_for_repaired_native_probe",
                "economic_role": "shock clipping / robust delta state",
                "null_margin_proxy": "base semantic-type best native operator margin, capped by field best_control_ratio",
            },
            {
                "operator": "AbsDelta",
                "repair_status": "authorized_for_repaired_native_probe",
                "economic_role": "magnitude dislocation without sign assumption",
                "null_margin_proxy": "Delta margin if available, otherwise field best_control_ratio",
            },
            {
                "operator": "SignedRankDelta",
                "repair_status": "authorized_for_repaired_native_probe",
                "economic_role": "cross-sectional ranked delta with sign preservation",
                "null_margin_proxy": "CSRank and Delta margin minimum if available",
            },
        ]
    )
    repaired_gate = pd.DataFrame(
        [
            {"gate": "generated_seed_count", "threshold": ">= 1200"},
            {"gate": "eligible_seed_count", "threshold": ">= 360"},
            {"gate": "semantic_family_count", "threshold": ">= 8"},
            {"gate": "operator_count", "threshold": ">= 5"},
            {"gate": "motif_cap_violation_count", "threshold": "0"},
            {"gate": "family_cap_violation_count", "threshold": "0"},
            {"gate": "role_violation_count", "threshold": "0"},
            {"gate": "repair_operator_share", "threshold": "<= 0.55"},
        ]
    )
    execution_plan = pd.DataFrame(
        [
            {
                "stage": "A7FF-CORE48SE",
                "action": "run bounded repaired null-first dry generation with expanded operator set",
                "executes_generation": True,
                "executes_replay": False,
                "executes_search": False,
                "max_seed_count": 1800,
            },
            {
                "stage": "A7FF-CORE49",
                "action": "if CORE48SE passes, define full-universe null-vector preflight contract",
                "executes_generation": False,
                "executes_replay": False,
                "executes_search": False,
                "max_seed_count": None,
            },
        ]
    )
    authorization = {
        "authorized": {"A7FF-CORE48SE repaired null-first dry seed generation": True},
        "not_authorized": {
            "numeric_replay": True,
            "formula_search": True,
            "large_search": True,
            "alpha_proof": True,
            "shadow_paper_live": True,
            "promotion": True,
        },
    }
    decision = "PASS_A7FFCORE48S_OPERATOR_NULL_COVERAGE_REPAIR_CONTRACT_READY_FOR_CORE48SE"
    manifest = {
        "stage": "A7FF-CORE48S",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE48R",
        "source_decision": source.get("decision"),
        "source_dominant_failure": source.get("dominant_failure"),
        "decision": decision,
        "executes_generation": False,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core48se_repaired_dry_generation": True,
        "authorizes_numeric_replay": False,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE48SE repaired null-first dry seed generation",
    }
    repair_policy.to_csv(RUNTIME / "a7ffcore48s_repair_policy.csv", index=False)
    operator_repair_set.to_csv(RUNTIME / "a7ffcore48s_operator_repair_set.csv", index=False)
    repaired_gate.to_csv(RUNTIME / "a7ffcore48s_repaired_gate.csv", index=False)
    execution_plan.to_csv(RUNTIME / "a7ffcore48s_execution_plan.csv", index=False)
    write_json(RUNTIME / "a7ffcore48s_authorization_matrix.json", authorization)
    write_json(RUNTIME / "a7ffcore48s_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE48S OPERATOR-NULL COVERAGE REPAIR CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE48S targets the CORE48E failure mode: operator breadth and motif concentration after successful seed supply. It is contract-only and does not execute replay, search, proof, shadow, paper, live, or promotion.",
        "",
        "## Repair Policy",
        "",
        md_table(repair_policy),
        "",
        "## Operator Repair Set",
        "",
        md_table(operator_repair_set),
        "",
        "## Repaired Gate",
        "",
        md_table(repaired_gate),
        "",
        "## Execution Plan",
        "",
        md_table(execution_plan),
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
