from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore43_control_orthogonalization_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE43_CONTROL_ORTHOGONALIZATION_CONTRACT_20260602.md"
CORE42 = REPO / "runtime" / "a7ffcore42_book_control_route_arbitration" / "a7ffcore42_manifest.json"


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
    source = read_json(CORE42)
    if source.get("decision") != "PASS_A7FFCORE42_ROUTE_ARBITRATION_READY_FOR_CORE43_CONTROL_ORTHOGONALIZATION_CONTRACT":
        raise SystemExit(f"CORE42 not ready for CORE43: {source.get('decision')}")

    orthogonalization_policy = pd.DataFrame(
        [
            {
                "policy_id": "O0_full_universe_score_required",
                "description": "orthogonalization must occur before top/bottom book selection, so full timestamp-symbol candidate scores are required",
                "hard_requirement": True,
            },
            {
                "policy_id": "O1_stale_score_residual",
                "description": "residualize candidate_score against stale_score by candidate/timestamp cross-section",
                "hard_requirement": True,
            },
            {
                "policy_id": "O2_sign_arbitrariness_filter",
                "description": "reject candidate/objective if original and sign-flip produce symmetric book results after residualization",
                "hard_requirement": True,
            },
            {
                "policy_id": "O3_shuffle_null_margin",
                "description": "book objective must beat row/time/symbol shuffle null variants with margin",
                "hard_requirement": True,
            },
            {
                "policy_id": "O4_no_search",
                "description": "no new formula generation or large search before control-orthogonal packet passes",
                "hard_requirement": True,
            },
        ]
    )
    required_packet = pd.DataFrame(
        [
            {"field": "candidate_score_original", "level": "full_universe", "required": True},
            {"field": "candidate_score_stale", "level": "full_universe", "required": True},
            {"field": "candidate_score_sign_flip", "level": "full_universe", "required": True},
            {"field": "candidate_score_shuffle_time", "level": "full_universe", "required": True},
            {"field": "candidate_score_shuffle_symbol", "level": "full_universe", "required": True},
            {"field": "residual_score_stale_orthogonal", "level": "full_universe", "required": True},
            {"field": "residual_score_null_orthogonal", "level": "full_universe", "required": True},
            {"field": "book_weight_from_residual_score", "level": "selected_book", "required": True},
        ]
    )
    input_audit = pd.DataFrame(
        [
            {
                "artifact": "CORE39E selected book packet sample",
                "status": "INSUFFICIENT_FOR_ORTHOGONALIZATION",
                "reason": "contains selected top/bottom rows, not full-universe score vectors",
            },
            {
                "artifact": "CORE33 candidate queue",
                "status": "SUFFICIENT_AS_CANDIDATE_SOURCE",
                "reason": "expressions and fields are available for rebuilding full-universe score vectors",
            },
        ]
    )
    execution_plan = pd.DataFrame(
        [
            {
                "stage": "A7FF-CORE43E",
                "action": "audit whether full-universe score/control vectors can be rebuilt from existing candidates and panels",
                "executes_new_generation": False,
                "executes_search": False,
            },
            {
                "stage": "A7FF-CORE44",
                "action": "if CORE43E passes, define full-universe orthogonal score packet construction",
                "executes_new_generation": False,
                "executes_search": False,
            },
        ]
    )
    authorization = {
        "authorized": {"A7FF-CORE43E full-universe control-vector rebuild audit": True},
        "not_authorized": {
            "formula_search": True,
            "large_search": True,
            "alpha_proof": True,
            "shadow_paper_live": True,
            "F1b_partial_survivor_expansion": True,
        },
    }
    decision = "PASS_A7FFCORE43_CONTROL_ORTHOGONALIZATION_CONTRACT_READY_FOR_CORE43E"
    manifest = {
        "stage": "A7FF-CORE43",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE42",
        "source_decision": source.get("decision"),
        "decision": decision,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core43e_audit": True,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE43E full-universe control-vector rebuild audit",
    }
    orthogonalization_policy.to_csv(RUNTIME / "a7ffcore43_orthogonalization_policy.csv", index=False)
    required_packet.to_csv(RUNTIME / "a7ffcore43_required_control_vector_packet.csv", index=False)
    input_audit.to_csv(RUNTIME / "a7ffcore43_current_input_audit.csv", index=False)
    execution_plan.to_csv(RUNTIME / "a7ffcore43_execution_plan.csv", index=False)
    write_json(RUNTIME / "a7ffcore43_authorization_matrix.json", authorization)
    write_json(RUNTIME / "a7ffcore43_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE43 CONTROL ORTHOGONALIZATION CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE43 defines the control-orthogonalization layer after CORE42 rejected expansion of a weak single-family partial survivor. It does not run generation, search, large search, alpha proof, shadow, paper, or live.",
        "",
        "## Orthogonalization Policy",
        "",
        md_table(orthogonalization_policy),
        "",
        "## Required Control Vector Packet",
        "",
        md_table(required_packet),
        "",
        "## Current Input Audit",
        "",
        md_table(input_audit),
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
