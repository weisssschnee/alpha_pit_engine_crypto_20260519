from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore41_book_control_repair_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE41_BOOK_CONTROL_REPAIR_CONTRACT_20260602.md"
CORE40ER = REPO / "runtime" / "a7ffcore40er_book_replay_forensic" / "a7ffcore40er_manifest.json"
CORE40ER_OBJECTIVE = REPO / "runtime" / "a7ffcore40er_book_replay_forensic" / "a7ffcore40er_objective_forensic.csv"


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
    source = read_json(CORE40ER)
    if source.get("decision") != "PASS_A7FFCORE40ER_BOOK_REPLAY_FORENSIC_READY_FOR_CORE41_CONTRACT":
        raise SystemExit(f"CORE40ER not ready for CORE41: {source.get('decision')}")

    objective_snapshot = pd.read_csv(CORE40ER_OBJECTIVE)
    repair_policy = pd.DataFrame(
        [
            {
                "policy_id": "C0_stale_dominance_hard_reject",
                "description": "reject objective/candidate rows where stale control absolute net return >= original absolute net return",
                "allowed": True,
            },
            {
                "policy_id": "C1_train_only_orientation",
                "description": "allow sign orientation only from train split and freeze it before OOS; no OOS/May orientation",
                "allowed": True,
            },
            {
                "policy_id": "C2_sign_flip_indistinguishable_reject",
                "description": "if original and sign_flip both survive similarly, mark as orientation-arbitrary and reject for alpha",
                "allowed": True,
            },
            {
                "policy_id": "C3_objective_family_reweighting",
                "description": "downweight objectives with median control ratio >= 1.0; do not select solely by positive net return",
                "allowed": True,
            },
            {
                "policy_id": "C4_search",
                "description": "new formula generation or large search",
                "allowed": False,
            },
        ]
    )
    gate_contract = pd.DataFrame(
        [
            {"gate": "train_oriented_net_positive", "rule": "train repaired original net > 0", "hard_gate": True},
            {"gate": "train_control_margin", "rule": "train repaired control_ratio < 0.8 preferred, <1.0 required", "hard_gate": True},
            {"gate": "oos_split_balance", "rule": ">=2 OOS splits positive and control-clean", "hard_gate": True},
            {"gate": "orientation_arbitrary", "rule": "reject if sign-flip is equally strong after train orientation", "hard_gate": True},
            {"gate": "stale_dominance", "rule": "reject if stale control dominates original in train or OOS", "hard_gate": True},
            {"gate": "family_breadth", "rule": ">=2 families and >=4 candidates before expansion", "hard_gate": True},
        ]
    )
    execution_scope = pd.DataFrame(
        [
            {
                "stage": "A7FF-CORE41E",
                "input": "runtime/a7ffcore40e_book_objective_replay_execution/a7ffcore40e_book_replay_all_variants.csv",
                "action": "apply train-only orientation and control dominance repair to existing book replay variants",
                "executes_new_generation": False,
                "executes_search": False,
            }
        ]
    )
    authorization = {
        "authorized": {"A7FF-CORE41E book control repair execution": True},
        "not_authorized": {
            "formula_search": True,
            "large_search": True,
            "alpha_proof": True,
            "shadow_paper_live": True,
            "new_generation": True,
        },
    }
    decision = "PASS_A7FFCORE41_BOOK_CONTROL_REPAIR_CONTRACT_READY_FOR_CORE41E"
    manifest = {
        "stage": "A7FF-CORE41",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE40ER",
        "source_decision": source.get("decision"),
        "decision": decision,
        "dominant_failure": source.get("dominant_failure"),
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core41e_execution": True,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE41E book control repair execution",
    }
    objective_snapshot.to_csv(RUNTIME / "a7ffcore41_source_objective_forensic_snapshot.csv", index=False)
    repair_policy.to_csv(RUNTIME / "a7ffcore41_control_repair_policy.csv", index=False)
    gate_contract.to_csv(RUNTIME / "a7ffcore41_gate_contract.csv", index=False)
    execution_scope.to_csv(RUNTIME / "a7ffcore41_execution_scope.csv", index=False)
    write_json(RUNTIME / "a7ffcore41_authorization_matrix.json", authorization)
    write_json(RUNTIME / "a7ffcore41_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE41 BOOK CONTROL REPAIR CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE41 defines control repair after CORE40ER found book-objective control dominance. It does not run generation, search, large search, alpha proof, shadow, paper, or live.",
        "",
        "## Source Objective Forensic",
        "",
        md_table(objective_snapshot),
        "",
        "## Control Repair Policy",
        "",
        md_table(repair_policy),
        "",
        "## Gate Contract",
        "",
        md_table(gate_contract),
        "",
        "## Execution Scope",
        "",
        md_table(execution_scope),
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
