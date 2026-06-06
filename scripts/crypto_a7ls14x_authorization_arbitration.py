from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ls14x_authorization_arbitration"
REPORT = REPO / "reports" / "CRYPTO_A7LS14X_AUTHORIZATION_ARBITRATION_20260606.md"
A7LS13 = REPO / "runtime" / "a7ls13_consolidation_replay_packet" / "a7ls13_manifest.json"
A7LS14 = REPO / "runtime" / "a7ls14_scaled_multi_axis_search_contract" / "a7ls14_manifest.json"
A7LS14_AUTH = REPO / "runtime" / "a7ls14_scaled_multi_axis_search_contract" / "a7ls14_authorization_matrix.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def build() -> dict[str, Any]:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    a7ls13 = read_json(A7LS13)
    a7ls14 = read_json(A7LS14)
    a7ls14_auth = read_json(A7LS14_AUTH)

    blockers: list[str] = []
    if a7ls13.get("decision") != "PASS_A7LS13_CONSOLIDATED_REPLAY_PACKET_READY_NO_SEARCH_AUTH":
        blockers.append("a7ls13_input_not_ready")
    if a7ls14.get("decision") != "PASS_A7LS14_SCALED_MULTI_AXIS_SEARCH_CONTRACT_READY":
        blockers.append("a7ls14_contract_not_ready")

    allowed_scope = pd.DataFrame(
        [
            {
                "scope_id": "A7LS15",
                "scope": "million_scale_multi_axis_blueprint_generation",
                "authorized": True,
                "heavy_compute": False,
                "limit": "generated_total <= 1,000,000",
                "checkpoint_required": True,
            },
            {
                "scope_id": "A7LS16",
                "scope": "local_preflight_and_materialization_smoke",
                "authorized": True,
                "heavy_compute": False,
                "limit": "local_light_preflight_rows = 512",
                "checkpoint_required": True,
            },
            {
                "scope_id": "A7LS17",
                "scope": "company_sharded_materialization",
                "authorized": True,
                "heavy_compute": True,
                "limit": "materialization_total <= 100,000",
                "checkpoint_required": True,
            },
            {
                "scope_id": "A7LS18",
                "scope": "company_sharded_numeric_wave",
                "authorized": True,
                "heavy_compute": True,
                "limit": "numeric_total <= 25,000; shards = 256; parallel = 3 default / 4 if memory allows",
                "checkpoint_required": True,
            },
            {
                "scope_id": "A7LS19",
                "scope": "checkpoint_arbitration_and_lane_resize",
                "authorized": True,
                "heavy_compute": False,
                "limit": "continue / kill / expand decisions only",
                "checkpoint_required": True,
            },
        ]
    )

    forbidden_scope = pd.DataFrame(
        [
            {"scope": "alpha_proof", "authorized": False, "reason": "A7LS14 is search infrastructure, not proof"},
            {"scope": "shadow_paper_live", "authorized": False, "reason": "no production or trading authorization"},
            {"scope": "May_in_selector_or_reward", "authorized": False, "reason": "May remains stress/failure attribution only"},
            {"scope": "unbounded_full_grammar", "authorized": False, "reason": "search is bounded by typed lanes and quota policy"},
            {"scope": "single_lane_budget_capture", "authorized": False, "reason": "axis quota and checkpoint policy required"},
            {"scope": "legacy_large_search_outside_A7LS14", "authorized": False, "reason": "old A7AL/A7FF large-search denials remain valid outside A7LS14 scope"},
        ]
    )

    supersession = pd.DataFrame(
        [
            {
                "superseded_rule": "global_large_search_not_authorized",
                "superseded_by": "A7LS-14X",
                "replacement": "large search authorized only inside A7LS14 checkpointed multi-axis A7LS15-A7LS18 path",
                "still_forbidden_outside_scope": True,
            },
            {
                "superseded_rule": "A7LS13_no_search_auth",
                "superseded_by": "A7LS-14 / A7LS-14X",
                "replacement": "A7LS13 packet promoted to A7LS14 seed map and scoped large-search contract",
                "still_forbidden_outside_scope": True,
            },
        ]
    )

    authorization = {
        "stage": "A7LS-14X",
        "decision": "PASS_A7LS14X_CHECKPOINT_LARGE_SEARCH_AUTHORIZATION_ARBITRATED" if not blockers else "HOLD_A7LS14X_INPUT_NOT_READY",
        "authorizes_scoped_large_search": not blockers,
        "authorizes_large_search": not blockers,
        "authorizes_a7ls15_generation": not blockers,
        "authorizes_a7ls16_local_preflight": not blockers,
        "authorizes_a7ls17_company_materialization": not blockers,
        "authorizes_a7ls18_company_numeric": not blockers,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "scope_boundary": "A7LS14 checkpointed multi-axis pipeline only",
        "supersedes_global_large_search_block": not blockers,
        "does_not_supersede_alpha_proof_block": True,
        "does_not_supersede_shadow_paper_live_block": True,
    }

    manifest = {
        "stage": "A7LS-14X",
        "generated_at": now_iso(),
        "decision": authorization["decision"],
        "blockers": blockers,
        "input_a7ls13_decision": a7ls13.get("decision"),
        "input_a7ls14_decision": a7ls14.get("decision"),
        "input_a7ls14_authorization_keys": sorted(a7ls14_auth.keys()),
        "generated_total": int(a7ls14.get("generated_total", 0)),
        "materialization_total": int(a7ls14.get("materialization_total", 0)),
        "numeric_total": int(a7ls14.get("numeric_total", 0)),
        "company_numeric_shard_target": int(a7ls14.get("company_numeric_shard_target", 0)),
        "authorizes_scoped_large_search": authorization["authorizes_scoped_large_search"],
        "authorizes_large_search": authorization["authorizes_large_search"],
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "uses_may": False,
    }

    allowed_scope.to_csv(RUNTIME / "a7ls14x_allowed_execution_scope.csv", index=False)
    forbidden_scope.to_csv(RUNTIME / "a7ls14x_forbidden_scope.csv", index=False)
    supersession.to_csv(RUNTIME / "a7ls14x_supersession_map.csv", index=False)
    write_json(RUNTIME / "a7ls14x_authorization_matrix.json", authorization)
    write_json(RUNTIME / "a7ls14x_manifest.json", manifest)

    report_lines = [
        "# CRYPTO A7LS-14X AUTHORIZATION ARBITRATION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "## Arbitration Result",
        "",
        "A7LS-14X resolves the source-of-truth conflict between older global `large_search = not authorized` records and the newer A7LS-14 scaled multi-axis search contract.",
        "",
        "The resolution is scoped: large search is authorized only for the checkpointed A7LS14 pipeline, namely A7LS15 blueprint generation, A7LS16 preflight, A7LS17 company materialization, and A7LS18 company numeric wave.",
        "",
        "This arbitration does not authorize alpha proof, shadow, paper, live, May-informed selector/reward use, unbounded grammar, or any legacy large-search path outside A7LS14.",
        "",
        "## Allowed Scope",
        "",
        md_table(allowed_scope),
        "",
        "## Forbidden Scope",
        "",
        md_table(forbidden_scope),
        "",
        "## Supersession",
        "",
        md_table(supersession),
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
    ]
    REPORT.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    return manifest


if __name__ == "__main__":
    result = build()
    print(json.dumps(result, indent=2, sort_keys=True))
