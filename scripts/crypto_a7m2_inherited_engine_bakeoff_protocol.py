from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from crypto_a7_validation_utils import REPORT_DIR, RUNTIME_DIR, stable_hash


DATE_TAG = "20260520"
A7M1B_DIR = RUNTIME_DIR / "a7m1b_surrogate_engine_readiness"
A7M2_DIR = RUNTIME_DIR / "a7m2_inherited_engine_bakeoff_protocol"


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


def engine_matrix(inventory: list[dict[str, str]]) -> list[dict[str, Any]]:
    status = {row["engine"]: row["status"] for row in inventory}
    return [
        {
            "engine_id": "E0",
            "engine_name": "current_A7L_manual_generator",
            "source": "crypto_native_manual_generator",
            "readiness": "executable",
            "generated_per_seed": 5000,
            "strict_replay_top_per_seed": 128,
            "deep_audit_top_per_seed": 16,
            "purpose": "Control arm representing current manual A7L generator space.",
            "hard_blocker": "",
        },
        {
            "engine_id": "E1",
            "engine_name": "FormulaGenV2_crypto_adapter",
            "source": "CN FormulaGenV2 inherited reference",
            "readiness": "adapter_ready" if status.get("FormulaGenV2_crypto_adapter") == "adapter_ready" else "blocked",
            "generated_per_seed": 5000,
            "strict_replay_top_per_seed": 128,
            "deep_audit_top_per_seed": 16,
            "purpose": "Test typed motif formula generation with crypto field dictionary.",
            "hard_blocker": "" if status.get("FormulaGenV2_crypto_adapter") == "adapter_ready" else "missing crypto adapter",
        },
        {
            "engine_id": "E2",
            "engine_name": "typed_AST_sampler_crypto_adapter",
            "source": "CN typed AST sampler inherited reference",
            "readiness": "adapter_ready" if status.get("typed_AST_sampler_crypto_adapter") == "adapter_ready" else "blocked",
            "generated_per_seed": 5000,
            "strict_replay_top_per_seed": 128,
            "deep_audit_top_per_seed": 16,
            "purpose": "Test typed AST expression diversity under crypto field/operator contract.",
            "hard_blocker": "" if status.get("typed_AST_sampler_crypto_adapter") == "adapter_ready" else "missing crypto adapter",
        },
        {
            "engine_id": "E3",
            "engine_name": "AST_failure_aware_repair",
            "source": "CN phase3 repair engine",
            "readiness": "blocked_adapter_needed",
            "generated_per_seed": 5000,
            "strict_replay_top_per_seed": 128,
            "deep_audit_top_per_seed": 16,
            "purpose": "Repair failed crypto candidates using failure taxonomy.",
            "hard_blocker": "requires crypto failure taxonomy and repair-action adapter preflight",
        },
        {
            "engine_id": "E4",
            "engine_name": "CEM_adaptive_grammar_crypto",
            "source": "CN CEM adaptive grammar ledger",
            "readiness": "blocked_adapter_needed",
            "generated_per_seed": 5000,
            "strict_replay_top_per_seed": 128,
            "deep_audit_top_per_seed": 16,
            "purpose": "Learn grammar production weights from non-May failure labels.",
            "hard_blocker": "requires crypto CEM ledger, production weights, and May-exclusion preflight",
        },
        {
            "engine_id": "E5",
            "engine_name": "surrogate_prioritized_sampler",
            "source": "A7M-1 empirical surrogate",
            "readiness": "adapter_ready" if status.get("surrogate_prioritized_sampler") == "adapter_ready" else "blocked",
            "generated_per_seed": 5000,
            "strict_replay_top_per_seed": 128,
            "deep_audit_top_per_seed": 16,
            "purpose": "Use non-May surrogate scores for cheap filtering and diversity-aware selection.",
            "hard_blocker": "" if status.get("surrogate_prioritized_sampler") == "adapter_ready" else "missing sampler interface",
        },
        {
            "engine_id": "E6",
            "engine_name": "placebo_random_control",
            "source": "negative control",
            "readiness": "executable",
            "generated_per_seed": 5000,
            "strict_replay_top_per_seed": 128,
            "deep_audit_top_per_seed": 16,
            "purpose": "Detect false-positive replay/gate behavior.",
            "hard_blocker": "",
        },
        {
            "engine_id": "E7",
            "engine_name": "adversarial_null_wrong_lag_control",
            "source": "negative control",
            "readiness": "executable",
            "generated_per_seed": 5000,
            "strict_replay_top_per_seed": 128,
            "deep_audit_top_per_seed": 16,
            "purpose": "Detect wrong-lag/future-sensitive artifact behavior.",
            "hard_blocker": "",
        },
    ]


def budget_plan(engines: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for seed in [1, 2, 3, 4]:
        for engine in engines:
            rows.append(
                {
                    "seed": seed,
                    "engine_id": engine["engine_id"],
                    "engine_name": engine["engine_name"],
                    "readiness": engine["readiness"],
                    "generated": engine["generated_per_seed"],
                    "strict_replay_top": engine["strict_replay_top_per_seed"],
                    "deep_audit_top": engine["deep_audit_top_per_seed"],
                    "execution_allowed_now": False,
                    "reason": "protocol_only_not_authorized",
                }
            )
    return rows


def gate_policy_rows() -> list[dict[str, Any]]:
    return [
        {"gate": "coverage_activity", "stage": "preselection", "policy": "required", "may_related": False},
        {"gate": "raw_validation_recent", "stage": "preselection", "policy": "required", "may_related": False},
        {"gate": "residual_vs_FundingCore_Core4", "stage": "preselection", "policy": "required", "may_related": False},
        {"gate": "cost20_validation_recent", "stage": "preselection", "policy": "required", "may_related": False},
        {"gate": "lag1_validation_recent", "stage": "preselection", "policy": "required", "may_related": False},
        {"gate": "family_duplicate_cap", "stage": "selection", "policy": "required", "may_related": False},
        {"gate": "return_corr_cluster_dedup", "stage": "selection_or_deep_audit", "policy": "required", "may_related": False},
        {"gate": "May_stress_label", "stage": "post_selection", "policy": "veto_or_failure_attribution_only", "may_related": True},
        {"gate": "placebo_null_strength", "stage": "aggregate", "policy": "hard_stop_if_nonzero_research_candidate", "may_related": False},
    ]


def success_stop_rows() -> list[dict[str, Any]]:
    return [
        {"metric": "non_may_preselection_pass_rate", "minimum": 0.10, "scope": "per engine and global", "action_if_fail": "do_not_escalate"},
        {"metric": "near_miss_nonplacebo_count", "minimum": 20, "scope": "global", "action_if_fail": "hold_engine_bakeoff"},
        {"metric": "near_miss_family_count", "minimum": 4, "scope": "global", "action_if_fail": "hold_engine_bakeoff"},
        {"metric": "research_candidate_count", "minimum": 2, "scope": "global", "action_if_fail": "no_alpha_proof_keep_method_hold"},
        {"metric": "placebo_research_candidate_count", "maximum": 0, "scope": "placebo/null engines", "action_if_fail": "fail_pipeline"},
        {"metric": "wrong_lag_research_candidate_count", "maximum": 0, "scope": "adversarial null", "action_if_fail": "fail_pipeline"},
        {"metric": "same_family_shortlist_share", "maximum": 0.25, "scope": "selected shortlist", "action_if_fail": "hold_due_concentration"},
        {"metric": "selected_may_severe_fail_share", "maximum": 0.75, "scope": "selected stress label", "action_if_fail": "warning_or_hold_no_escalation"},
        {"metric": "return_corr_cluster_count_growth", "minimum": "positive_vs_A7K", "scope": "selected/deep audit", "action_if_fail": "hold_due_no_diversity_growth"},
    ]


def execution_blockers(engines: list[dict[str, Any]], a7m1b_manifest: dict[str, Any]) -> list[dict[str, Any]]:
    blockers = [
        {
            "blocker": "A7M1B_surrogate_cross_source_hold",
            "status": "active",
            "detail": f"leave_source_out_near_miss_lift_min={a7m1b_manifest.get('leave_source_out_near_miss_lift_min')}",
            "required_resolution": "protocol may be written, but execution needs explicit user approval and should treat surrogate as weak prior",
        }
    ]
    for engine in engines:
        if str(engine["readiness"]).startswith("blocked"):
            blockers.append(
                {
                    "blocker": f"{engine['engine_id']}_{engine['engine_name']}_not_executable",
                    "status": "active",
                    "detail": engine["hard_blocker"],
                    "required_resolution": "adapter preflight required before engine can enter executable bakeoff",
                }
            )
    return blockers


def main() -> int:
    A7M2_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_now()
    a7m1b_manifest = read_json(A7M1B_DIR / f"crypto_a7m1b_manifest_{DATE_TAG}.json")
    inventory = read_csv(A7M1B_DIR / "a7m1b_inherited_engine_inventory.csv")
    engines = engine_matrix(inventory)
    budgets = budget_plan(engines)
    gates = gate_policy_rows()
    stops = success_stop_rows()
    blockers = execution_blockers(engines, a7m1b_manifest)
    executable_engines = [e for e in engines if e["readiness"] in {"executable", "adapter_ready"}]

    protocol = {
        "protocol_id": "CRYPTO_A7M2_INHERITED_ENGINE_BAKEOFF_PROTOCOL_V1",
        "generated_at": now,
        "decision": "PASS_A7M2_INHERITED_ENGINE_BAKEOFF_PROTOCOL",
        "alpha_proof_status": "NOT_ALPHA_PROOF",
        "executes_search": False,
        "executes_replay": False,
        "authorizes_a7m2_execution": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "source_a7m1b_decision": a7m1b_manifest.get("decision"),
        "source_a7m1b_hold_reason": "cross_source_surrogate_generalization_weak",
        "engine_count": len(engines),
        "executable_or_adapter_ready_engine_count": len(executable_engines),
        "planned_if_authorized": {
            "engines": len(engines),
            "seeds": 4,
            "generated_per_engine_seed": 5000,
            "total_generated": sum(int(row["generated"]) for row in budgets),
            "strict_replay_total": sum(int(row["strict_replay_top"]) for row in budgets),
            "deep_audit_total": sum(int(row["deep_audit_top"]) for row in budgets),
        },
        "may_policy": {
            "allowed": ["post_selection_stress_label", "veto", "failure_attribution"],
            "forbidden": ["ranking", "reward", "threshold_tuning", "arm_allocation", "generator_weight_update", "mutation_prior_update"],
        },
        "highest_possible_label_if_run": "A7M_RESEARCH_CANDIDATE_POOL",
        "blocked_labels": ["ALPHA_PROOF", "SHADOW_READY", "PAPER_READY", "LIVE_READY", "PRODUCTION_READY"],
        "engines": engines,
        "gates": gates,
        "success_stop_rules": stops,
        "execution_blockers": blockers,
    }
    protocol["stable_protocol_hash"] = stable_hash({k: v for k, v in protocol.items() if k not in {"generated_at", "stable_protocol_hash"}})

    protocol_path = A7M2_DIR / f"crypto_a7m2_protocol_{DATE_TAG}.json"
    manifest_path = A7M2_DIR / f"crypto_a7m2_manifest_{DATE_TAG}.json"
    write_json(protocol_path, protocol)

    write_csv(A7M2_DIR / "a7m2_engine_matrix.csv", engines, ["engine_id", "engine_name", "source", "readiness", "generated_per_seed", "strict_replay_top_per_seed", "deep_audit_top_per_seed", "purpose", "hard_blocker"])
    write_csv(A7M2_DIR / "a7m2_budget_plan.csv", budgets, ["seed", "engine_id", "engine_name", "readiness", "generated", "strict_replay_top", "deep_audit_top", "execution_allowed_now", "reason"])
    write_csv(A7M2_DIR / "a7m2_gate_policy.csv", gates, ["gate", "stage", "policy", "may_related"])
    write_csv(A7M2_DIR / "a7m2_success_stop_rules.csv", stops, ["metric", "minimum", "maximum", "scope", "action_if_fail"])
    write_csv(A7M2_DIR / "a7m2_execution_blockers.csv", blockers, ["blocker", "status", "detail", "required_resolution"])

    manifest = {
        "generated_at": now,
        "decision": protocol["decision"],
        "alpha_proof_status": "NOT_ALPHA_PROOF",
        "executes_search": False,
        "executes_replay": False,
        "authorizes_a7m2_execution": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "protocol": str(protocol_path),
        "stable_protocol_hash": protocol["stable_protocol_hash"],
        "planned_total_generated_if_authorized": protocol["planned_if_authorized"]["total_generated"],
        "planned_strict_replay_total_if_authorized": protocol["planned_if_authorized"]["strict_replay_total"],
        "planned_deep_audit_total_if_authorized": protocol["planned_if_authorized"]["deep_audit_total"],
        "active_execution_blockers": len(blockers),
    }
    write_json(manifest_path, manifest)

    report = REPORT_DIR / f"CRYPTO_A7M2_INHERITED_ENGINE_BAKEOFF_PROTOCOL_{DATE_TAG}.md"
    lines = [
        "# Crypto A7M-2 Inherited-Engine Bakeoff Protocol",
        "",
        f"- generated_at: `{now}`",
        "- decision: `PASS_A7M2_INHERITED_ENGINE_BAKEOFF_PROTOCOL`",
        "- alpha_proof_status: `NOT_ALPHA_PROOF`",
        "- executes_search: `False`",
        "- executes_replay: `False`",
        "- authorizes_a7m2_execution: `False`",
        "- authorizes_large_search: `False`",
        f"- stable_protocol_hash: `{protocol['stable_protocol_hash']}`",
        "",
        "## Planned Budget If Separately Authorized",
        "",
        f"- engines: `{protocol['planned_if_authorized']['engines']}`",
        "- seeds: `4`",
        "- generated_per_engine_seed: `5000`",
        f"- total_generated: `{protocol['planned_if_authorized']['total_generated']}`",
        f"- strict_replay_total: `{protocol['planned_if_authorized']['strict_replay_total']}`",
        f"- deep_audit_total: `{protocol['planned_if_authorized']['deep_audit_total']}`",
        "",
        "## Engine Matrix",
        "",
        "| engine | readiness | purpose | blocker |",
        "|---|---|---|---|",
    ]
    for engine in engines:
        lines.append(f"| `{engine['engine_id']} {engine['engine_name']}` | `{engine['readiness']}` | {engine['purpose']} | {engine['hard_blocker']} |")
    lines += [
        "",
        "## Execution Blockers",
        "",
    ]
    for blocker in blockers:
        lines.append(f"- `{blocker['blocker']}`: {blocker['detail']}")
    lines += [
        "",
        "## Boundary",
        "",
        "- May remains stress-only and cannot enter ranking, reward, arm allocation, generator weights, or mutation priors.",
        "- A7M-2 protocol does not authorize running the bakeoff.",
        "- Highest possible output if later run is `A7M_RESEARCH_CANDIDATE_POOL`, not alpha proof.",
    ]
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")

    decision = REPORT_DIR / f"CRYPTO_A7M2_DECISION_RECORD_{DATE_TAG}.md"
    decision.write_text(
        "\n".join(
            [
                "# Crypto A7M-2 Decision Record",
                "",
                "- decision: `PASS_A7M2_INHERITED_ENGINE_BAKEOFF_PROTOCOL`",
                "- alpha_proof_status: `NOT_ALPHA_PROOF`",
                "- search_executed: `False`",
                "- replay_executed: `False`",
                "- authorizes_a7m2_execution: `False`",
                "- authorizes_large_search: `False`",
                "",
                "## Confirmed",
                "",
                "- A7M-2 inherited-engine bakeoff protocol is specified.",
                "- Engine matrix, budget plan, gate policy, stop rules, and execution blockers are explicit.",
                "- A7M-1B HOLD is preserved; surrogate is treated as weak prior, not allocation authority.",
                "",
                "## Not Confirmed",
                "",
                "- No bakeoff execution.",
                "- No adaptive large search.",
                "- No research candidate, alpha proof, shadow, paper, live, or production readiness.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
