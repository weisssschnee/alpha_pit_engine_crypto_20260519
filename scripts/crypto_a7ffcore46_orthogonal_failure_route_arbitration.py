from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore46_orthogonal_failure_route_arbitration"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE46_ORTHOGONAL_FAILURE_ROUTE_ARBITRATION_20260602.md"
CORE45R = REPO / "runtime" / "a7ffcore45r_orthogonal_book_replay_forensic" / "a7ffcore45r_manifest.json"


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
    source = read_json(CORE45R)
    if source.get("decision") != "PASS_A7FFCORE45R_ORTHOGONAL_BOOK_REPLAY_FORENSIC_READY_FOR_CORE46_ROUTE_ARBITRATION":
        raise SystemExit(f"CORE45R not ready for CORE46: {source.get('decision')}")

    route_options = pd.DataFrame(
        [
            {
                "route_id": "R0_expand_current_core33_candidates",
                "decision": "REJECT",
                "reason": "CORE45E/45R found zero survivors after full-universe control orthogonalization",
                "authorizes_next": False,
            },
            {
                "route_id": "R1_large_formula_search",
                "decision": "REJECT",
                "reason": "current objective surface remains control dominated; large search would scale the wrong target",
                "authorizes_next": False,
            },
            {
                "route_id": "R2_same_family_rerun",
                "decision": "REJECT",
                "reason": "F1a/F1b/F2a all failed under residual-null book replay",
                "authorizes_next": False,
            },
            {
                "route_id": "R3_control_null_aware_factor_compiler_contract",
                "decision": "SELECT",
                "reason": "next work must redesign feature-to-factor generation around control-null separation before new candidates enter replay",
                "authorizes_next": True,
            },
        ]
    )
    freeze_matrix = pd.DataFrame(
        [
            {"item": "CORE33 candidate expansion", "status": "NOT_AUTHORIZED"},
            {"item": "F1a/F1b/F2a same-family rerun", "status": "NOT_AUTHORIZED"},
            {"item": "large formula search", "status": "NOT_AUTHORIZED"},
            {"item": "alpha proof", "status": "NOT_AUTHORIZED"},
            {"item": "shadow/paper/live", "status": "NOT_AUTHORIZED"},
            {"item": "A7FF-CORE47 control-null-aware factor compiler contract", "status": "AUTHORIZED_CONTRACT_ONLY"},
        ]
    )
    selected_route = {
        "selected_route": "R3_control_null_aware_factor_compiler_contract",
        "next_stage": "A7FF-CORE47",
        "next_stage_name": "control-null-aware feature-to-factor compiler contract",
        "executes_generation": False,
        "executes_replay": False,
        "executes_search": False,
        "goal": "define how future feature/factor generation must optimize original-vs-null separability before replay",
    }
    authorization = {
        "authorized": {
            "A7FF-CORE47 control-null-aware feature-to-factor compiler contract": True
        },
        "not_authorized": {
            "current_candidate_expansion": True,
            "same_family_rerun": True,
            "formula_search": True,
            "large_search": True,
            "alpha_proof": True,
            "shadow_paper_live": True,
        },
    }
    decision = "PASS_A7FFCORE46_ROUTE_ARBITRATION_READY_FOR_CORE47_CONTRACT"
    manifest = {
        "stage": "A7FF-CORE46",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE45R",
        "source_decision": source.get("decision"),
        "source_dominant_failure": source.get("dominant_failure"),
        "decision": decision,
        "selected_route": selected_route["selected_route"],
        "executes_generation": False,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core47_contract": True,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE47 control-null-aware feature-to-factor compiler contract",
    }
    route_options.to_csv(RUNTIME / "a7ffcore46_route_options.csv", index=False)
    freeze_matrix.to_csv(RUNTIME / "a7ffcore46_freeze_matrix.csv", index=False)
    write_json(RUNTIME / "a7ffcore46_selected_route.json", selected_route)
    write_json(RUNTIME / "a7ffcore46_authorization_matrix.json", authorization)
    write_json(RUNTIME / "a7ffcore46_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE46 ORTHOGONAL FAILURE ROUTE ARBITRATION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE46 freezes the zero-survivor, control-dominated orthogonal replay result and selects the next non-search route. It does not authorize formula generation, large search, alpha proof, shadow, paper, or live.",
        "",
        "## Route Options",
        "",
        md_table(route_options),
        "",
        "## Freeze Matrix",
        "",
        md_table(freeze_matrix),
        "",
        "## Selected Route",
        "",
        "```json",
        json.dumps(selected_route, indent=2, sort_keys=True),
        "```",
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
