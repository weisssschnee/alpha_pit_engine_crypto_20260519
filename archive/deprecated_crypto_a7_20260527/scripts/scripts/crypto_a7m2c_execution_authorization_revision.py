from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from crypto_a7_validation_utils import REPORT_DIR, RUNTIME_DIR, stable_hash


DATE_TAG = "20260520"
A7M2_DIR = RUNTIME_DIR / "a7m2_inherited_engine_bakeoff_protocol"
A7M2A_DIR = RUNTIME_DIR / "a7m2a_ast_repair_adapter"
A7M2B_DIR = RUNTIME_DIR / "a7m2b_cem_adapter"
A7M2C_DIR = RUNTIME_DIR / "a7m2c_execution_authorization_revision"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def revised_engine_matrix(original: list[dict[str, str]], a_pass: bool, b_pass: bool) -> list[dict[str, Any]]:
    rows = []
    for row in original:
        out: dict[str, Any] = dict(row)
        if row.get("engine_id") == "E3" and a_pass:
            out["readiness"] = "adapter_ready"
            out["hard_blocker"] = ""
            out["revision_note"] = "A7M-2A AST repair adapter preflight passed."
        elif row.get("engine_id") == "E4" and b_pass:
            out["readiness"] = "adapter_ready"
            out["hard_blocker"] = ""
            out["revision_note"] = "A7M-2B CEM adaptive grammar preflight passed."
        elif row.get("engine_id") == "E5":
            out["revision_note"] = "Surrogate sampler may be tested as equal-budget arm only; cannot allocate budgets."
        else:
            out["revision_note"] = ""
        rows.append(out)
    return rows


def blocker_reclassification(a_pass: bool, b_pass: bool) -> list[dict[str, Any]]:
    return [
        {
            "blocker": "A7M1B_surrogate_cross_source_hold",
            "old_classification": "execution_blocker",
            "new_classification": "allocation_mode_blocker",
            "blocks_equal_budget_bakeoff": False,
            "blocks_adaptive_allocation": True,
            "status_after_revision": "active_for_adaptive_allocation_only",
            "detail": "Surrogate can be tested as E5 equal-budget engine, but cannot drive other engines' budgets.",
        },
        {
            "blocker": "E3_AST_failure_aware_repair_not_executable",
            "old_classification": "hard_execution_blocker",
            "new_classification": "resolved" if a_pass else "hard_execution_blocker",
            "blocks_equal_budget_bakeoff": not a_pass,
            "blocks_adaptive_allocation": not a_pass,
            "status_after_revision": "resolved" if a_pass else "active",
            "detail": "Resolved by PASS_A7M2A_AST_REPAIR_ADAPTER_PREFLIGHT." if a_pass else "A7M-2A did not pass.",
        },
        {
            "blocker": "E4_CEM_adaptive_grammar_not_executable",
            "old_classification": "hard_execution_blocker",
            "new_classification": "resolved" if b_pass else "hard_execution_blocker",
            "blocks_equal_budget_bakeoff": not b_pass,
            "blocks_adaptive_allocation": not b_pass,
            "status_after_revision": "resolved" if b_pass else "active",
            "detail": "Resolved by PASS_A7M2B_CEM_ADAPTIVE_GRAMMAR_PREFLIGHT." if b_pass else "A7M-2B did not pass.",
        },
    ]


def authorization_rows(equal_budget_authorized: bool) -> list[dict[str, Any]]:
    return [
        {
            "capability": "A7M-2_equal_budget_inherited_engine_bakeoff",
            "authorized": equal_budget_authorized,
            "scope": "8 engines x 4 seeds x 5000 generated; strict replay 4096; deep audit 512; if user starts separately",
        },
        {
            "capability": "surrogate_driven_budget_allocation",
            "authorized": False,
            "scope": "blocked by A7M-1B cross-source HOLD",
        },
        {
            "capability": "adaptive_large_search",
            "authorized": False,
            "scope": "requires later A7M-2 results and separate authorization",
        },
        {
            "capability": "alpha_proof",
            "authorized": False,
            "scope": "not authorized",
        },
        {
            "capability": "shadow_paper_live",
            "authorized": False,
            "scope": "not authorized",
        },
    ]


def main() -> int:
    A7M2C_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_now()

    a_manifest = read_json(A7M2A_DIR / f"crypto_a7m2a_manifest_{DATE_TAG}.json")
    b_manifest = read_json(A7M2B_DIR / f"crypto_a7m2b_manifest_{DATE_TAG}.json")
    a_pass = str(a_manifest.get("decision", "")).startswith("PASS_A7M2A")
    b_pass = str(b_manifest.get("decision", "")).startswith("PASS_A7M2B")
    original_engines = read_csv(A7M2_DIR / "a7m2_engine_matrix.csv")
    revised_engines = revised_engine_matrix(original_engines, a_pass, b_pass)
    blockers = blocker_reclassification(a_pass, b_pass)
    equal_budget_authorized = a_pass and b_pass
    authorization = authorization_rows(equal_budget_authorized)

    decision = (
        "PASS_A7M2C_EQUAL_BUDGET_BAKEOFF_AUTHORIZATION_REVISION"
        if equal_budget_authorized
        else "HOLD_A7M2C_ENGINE_ADAPTER_BLOCKERS_REMAIN"
    )

    write_csv(A7M2C_DIR / "a7m2c_revised_engine_matrix.csv", revised_engines, ["engine_id", "engine_name", "source", "readiness", "generated_per_seed", "strict_replay_top_per_seed", "deep_audit_top_per_seed", "purpose", "hard_blocker", "revision_note"])
    write_csv(A7M2C_DIR / "a7m2c_blocker_reclassification.csv", blockers, ["blocker", "old_classification", "new_classification", "blocks_equal_budget_bakeoff", "blocks_adaptive_allocation", "status_after_revision", "detail"])
    write_csv(A7M2C_DIR / "a7m2c_authorization_matrix.csv", authorization, ["capability", "authorized", "scope"])

    manifest = {
        "generated_at": now,
        "decision": decision,
        "alpha_proof_status": "NOT_ALPHA_PROOF",
        "executes_search": False,
        "executes_replay": False,
        "a7m2a_decision": a_manifest.get("decision"),
        "a7m2b_decision": b_manifest.get("decision"),
        "resolved_blockers": [row["blocker"] for row in blockers if row["status_after_revision"] == "resolved"],
        "reclassified_blockers": [row["blocker"] for row in blockers if row["new_classification"] == "allocation_mode_blocker"],
        "authorizes_equal_budget_a7m2_bakeoff": equal_budget_authorized,
        "authorizes_surrogate_driven_allocation": False,
        "authorizes_adaptive_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "may_policy": {
            "allowed": ["post_selection_stress_label", "veto", "failure_attribution"],
            "forbidden": ["ranking", "reward", "threshold_tuning", "weight_selection", "candidate_selection", "generator_tuning", "arm_allocation", "mutation_prior"],
        },
        "planned_if_user_starts_equal_budget_bakeoff": {
            "engines": 8,
            "seeds": 4,
            "generated_per_engine_seed": 5000,
            "total_generated": 160000,
            "strict_replay_total": 4096,
            "deep_audit_total": 512,
        },
        "outputs": {
            "revised_engine_matrix": str(A7M2C_DIR / "a7m2c_revised_engine_matrix.csv"),
            "blocker_reclassification": str(A7M2C_DIR / "a7m2c_blocker_reclassification.csv"),
            "authorization_matrix": str(A7M2C_DIR / "a7m2c_authorization_matrix.csv"),
        },
    }
    manifest["stable_manifest_hash"] = stable_hash({k: v for k, v in manifest.items() if k not in {"generated_at", "stable_manifest_hash"}})
    write_json(A7M2C_DIR / f"crypto_a7m2c_manifest_{DATE_TAG}.json", manifest)

    report = REPORT_DIR / f"CRYPTO_A7M2C_EXECUTION_AUTHORIZATION_REVISION_{DATE_TAG}.md"
    lines = [
        "# Crypto A7M-2C Execution Authorization Revision",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{decision}`",
        "- alpha_proof_status: `NOT_ALPHA_PROOF`",
        "- executes_search: `False`",
        "- executes_replay: `False`",
        f"- authorizes_equal_budget_a7m2_bakeoff: `{equal_budget_authorized}`",
        "- authorizes_surrogate_driven_allocation: `False`",
        "- authorizes_adaptive_large_search: `False`",
        "- authorizes_alpha_proof: `False`",
        f"- stable_manifest_hash: `{manifest['stable_manifest_hash']}`",
        "",
        "## Blocker Reclassification",
        "",
        "| blocker | new_classification | blocks_equal_budget | blocks_adaptive_allocation |",
        "|---|---|---|---|",
    ]
    for row in blockers:
        lines.append(f"| `{row['blocker']}` | `{row['new_classification']}` | `{row['blocks_equal_budget_bakeoff']}` | `{row['blocks_adaptive_allocation']}` |")
    lines += [
        "",
        "## Confirmed",
        "",
        "- A7M-1B surrogate cross-source HOLD blocks adaptive allocation, not equal-budget bakeoff.",
        "- E5 surrogate-prioritized sampler can only be tested as an equal-budget engine arm.",
        "- May remains stress-only and cannot enter ranking/reward/generator tuning/arm allocation.",
        "",
        "## Still Not Authorized",
        "",
        "- Adaptive large search.",
        "- Alpha proof.",
        "- Shadow, paper, live, or production deployment.",
    ]
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")

    decision_path = REPORT_DIR / f"CRYPTO_A7M2C_DECISION_RECORD_{DATE_TAG}.md"
    decision_path.write_text(
        "\n".join(
            [
                "# Crypto A7M-2C Decision Record",
                "",
                f"- decision: `{decision}`",
                "- alpha_proof_status: `NOT_ALPHA_PROOF`",
                "- search_executed: `False`",
                "- replay_executed: `False`",
                f"- authorizes_equal_budget_a7m2_bakeoff: `{equal_budget_authorized}`",
                "- authorizes_adaptive_large_search: `False`",
                "",
                "## Resolved / Reclassified",
                "",
                "- E3 AST repair adapter blocker is resolved if A7M-2A passed.",
                "- E4 CEM adaptive grammar blocker is resolved if A7M-2B passed.",
                "- A7M-1B surrogate cross-source HOLD is reclassified as allocation-mode blocker.",
                "",
                "## Boundary",
                "",
                "- Equal-budget A7M-2, if run later, remains an engine bakeoff and not alpha proof.",
                "- Surrogate cannot allocate budgets until cross-source generalization is fixed.",
                "- No shadow, paper, live, production, or adaptive large search authorization.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
