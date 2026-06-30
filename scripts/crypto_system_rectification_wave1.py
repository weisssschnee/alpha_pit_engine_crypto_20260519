from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "system_rectification_20260630"
REPORTS = REPO / "reports"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(cmd, cwd=REPO, text=True, stderr=subprocess.STDOUT).strip()
    except Exception as exc:
        return f"ERROR: {exc}"


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def md_table(rows: list[dict[str, Any]], columns: list[str], limit: int = 60) -> str:
    if not rows:
        return "`<empty>`"
    out = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows[:limit]:
        out.append("| " + " | ".join(str(row.get(col, "")).replace("|", "\\|") for col in columns) + " |")
    return "\n".join(out)


def classify_file(path: Path) -> dict[str, str]:
    rel = path.relative_to(REPO).as_posix()
    name = path.name
    text = rel.lower()
    subsystem = "unknown"
    status = "legacy_reference"
    evidence = ""

    if rel.startswith("alphafactory_crypto/engines/search_memory"):
        subsystem, status = "search_memory", "keep_core"
        evidence = "A7MEM-0/1 pass; imported by search generation"
    elif rel.startswith("alphafactory_crypto/engines/formula_gen"):
        subsystem, status = "formula_generation", "wrap_with_contract"
        evidence = "formula adapter exists; needs stable queue contract"
    elif "reward1_portfolio_reward_model" in name:
        subsystem, status = "reward_validation", "keep_core"
        evidence = "strict reward gate used by A7SEARCH5/A7SEARCH6"
    elif "a7v3s9_prereward_oos_control_proxy" in name:
        subsystem, status = "proxy_evaluation", "keep_core"
        evidence = "proxy evaluator used by large search waves"
    elif "a7v3s9_proxy_aggregate" in name or "reward_sharded_aggregate" in name:
        subsystem, status = "aggregation_reporting", "wrap_with_contract"
        evidence = "aggregate scripts are source-of-truth producers"
    elif "a7search6" in name:
        subsystem, status = "search_generation", "wrap_with_contract"
        evidence = "current running search; mechanism-seeded queue generator"
    elif "a7search1" in name:
        subsystem, status = "search_generation", "legacy_reference"
        evidence = "mixed CEM/UCT/AST generator; useful patterns but not current core"
    elif "a7mem" in name:
        subsystem, status = "search_memory", "wrap_with_contract"
        evidence = "memory registry scripts produce current prior"
    elif "a7ai" in text or "field" in text:
        subsystem, status = "field_contracts", "archive_only"
        evidence = "prior governance evidence; not all scripts are runtime core"
    elif "a7aa" in text or "response" in text:
        subsystem, status = "feature_response", "archive_only"
        evidence = "response profiling evidence"
    elif "a7ff" in text:
        subsystem, status = "feature_factory", "legacy_reference"
        evidence = "large feature experiments; requires core extraction review"
    elif "a7search" in text:
        subsystem, status = "search_generation", "legacy_reference"
        evidence = "historical search line"
    elif rel.startswith("reports/"):
        subsystem, status = "reports", "source_of_truth_evidence"
        evidence = "human decision artifact"
    elif rel.startswith("runtime/"):
        subsystem, status = "runtime_artifacts", "source_of_truth_evidence"
        evidence = "machine-readable evidence or manifest"
    elif rel.startswith(".planning/"):
        subsystem, status = "planning", "keep_core"
        evidence = "current planning source of truth"
    return {"path": rel, "subsystem": subsystem, "status": status, "evidence": evidence}


def inventory() -> list[dict[str, str]]:
    paths: list[Path] = []
    for root in ["alphafactory_crypto", "scripts", "reports", "runtime", ".planning"]:
        base = REPO / root
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".py", ".md", ".json", ".csv", ".ps1"}:
                paths.append(path)
    return [classify_file(path) for path in sorted(paths)]


def interface_contracts() -> dict[str, Any]:
    return {
        "DataPanelContract": {
            "required": ["symbol", "timestamp", "trade_close", "trade_quote_volume"],
            "optional_current": ["open_interest_value_last", "top_long_short_account_ratio_last", "funding_rate", "mark_index_basis_bps"],
            "fail_closed_on": ["missing_timestamp", "duplicate_symbol_timestamp", "future_feature_available_time", "unregistered_panel"],
            "authorizes": ["field_materialization"],
        },
        "FieldContractRegistry": {
            "required": ["field", "semantic_type", "role", "pit_status", "latency_status", "allowed_routes"],
            "fail_closed_on": ["missing_contract", "label_or_future_field", "same_bar_timing_violation"],
            "authorizes": ["formula_queue_generation"],
        },
        "FormulaCandidateQueue": {
            "required": ["blueprint_id", "expression", "semantic_pair", "motif", "horizon_h", "skeleton_key"],
            "fail_closed_on": ["missing_expression", "memory_reject", "forbidden_field", "unsupported_operator"],
            "authorizes": ["proxy_evaluation_only"],
        },
        "ProxyEvaluationResult": {
            "required": ["blueprint_id", "proxy_score", "proxy_strict_pass", "proxy_near_miss", "proxy_selectable", "hard_reject_reasons"],
            "fail_closed_on": ["eval_error_rows_nonzero", "missing_shards", "selected_rows_zero"],
            "authorizes": ["bounded_full_reward"],
        },
        "RewardGateResult": {
            "required": ["train_sortino", "validation_sortino", "test_sortino", "recent_sortino", "min_oos_floor_sortino", "stress_floor_sortino", "recent_shuffle_control_ratio"],
            "fail_closed_on": ["train_orientation_no_positive_edge", "oos_floor_not_positive", "control_dominated", "lag_stale_dominated", "shuffle_dominated"],
            "authorizes": ["validation_pack"],
        },
        "ValidationPackResult": {
            "required": ["canonical_accepted_rows", "single_leg_accepted_rows", "operator_ablation_accepted_rows", "decision"],
            "fail_closed_on": ["eval_error_rows_nonzero", "single_leg_dominates", "canonical_failed"],
            "authorizes": ["memory_triage_only"],
        },
        "SearchMemoryUpdate": {
            "required": ["candidate_memory", "cluster_memory", "pair_motif_prior", "rejection_memory", "decision"],
            "fail_closed_on": ["missing_rejection_memory", "missing_cluster_caps", "not_required_for_next_large_search"],
            "authorizes": ["next_queue_generation"],
        },
        "RunManifest": {
            "required": ["stage", "decision", "generated_at", "runtime", "report", "authorizes_alpha_proof", "authorizes_shadow_paper_live"],
            "fail_closed_on": ["missing_decision", "authorization_conflict", "stale_source_of_truth"],
            "authorizes": ["next_stage_if_explicit"],
        },
    }


def architecture() -> tuple[list[dict[str, str]], list[dict[str, str]], str]:
    nodes = [
        {"id": "data", "label": "DataPanelContract", "type": "contract"},
        {"id": "fields", "label": "FieldContractRegistry", "type": "contract"},
        {"id": "formula", "label": "FormulaCandidateQueue", "type": "queue"},
        {"id": "proxy", "label": "ProxyEvaluationResult", "type": "evaluation"},
        {"id": "reward", "label": "RewardGateResult", "type": "validation"},
        {"id": "validation", "label": "ValidationPackResult", "type": "validation"},
        {"id": "memory", "label": "SearchMemoryUpdate", "type": "governance"},
        {"id": "orchestration", "label": "CompanyMachineSupervisor", "type": "runtime"},
        {"id": "reports", "label": "ReportsAndManifests", "type": "source_of_truth"},
    ]
    edges = [
        {"from": "data", "to": "fields", "relation": "materializes_registered_fields"},
        {"from": "fields", "to": "formula", "relation": "authorizes_field_roles"},
        {"from": "memory", "to": "formula", "relation": "enforces_prior_and_caps"},
        {"from": "formula", "to": "proxy", "relation": "evaluated_by_proxy"},
        {"from": "proxy", "to": "reward", "relation": "selected_queue_if_proxy_pass"},
        {"from": "reward", "to": "validation", "relation": "accepted_queue_requires_ablation"},
        {"from": "validation", "to": "memory", "relation": "triage_updates_prior"},
        {"from": "orchestration", "to": "proxy", "relation": "runs_sharded_workers"},
        {"from": "proxy", "to": "reports", "relation": "writes_manifest"},
        {"from": "reward", "to": "reports", "relation": "writes_manifest"},
        {"from": "validation", "to": "reports", "relation": "writes_manifest"},
        {"from": "memory", "to": "reports", "relation": "writes_registry"},
    ]
    mermaid = """```mermaid
flowchart LR
  data["DataPanelContract"]
  fields["FieldContractRegistry"]
  memory["SearchMemoryUpdate"]
  formula["FormulaCandidateQueue"]
  proxy["ProxyEvaluationResult"]
  reward["RewardGateResult"]
  validation["ValidationPackResult"]
  orchestration["CompanyMachineSupervisor"]
  reports["ReportsAndManifests"]

  data -->|"materializes registered fields"| fields
  fields -->|"field roles and PIT gates"| formula
  memory -->|"prior, rejection, cluster caps"| formula
  formula -->|"proxy queue"| proxy
  orchestration -->|"sharded workers"| proxy
  proxy -->|"selected proxy queue"| reward
  reward -->|"accepted candidates"| validation
  validation -->|"triage only"| memory
  proxy --> reports
  reward --> reports
  validation --> reports
  memory --> reports
```
"""
    return nodes, edges, mermaid


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    generated_at = now_utc()
    head = run(["git", "rev-parse", "--short", "HEAD"])
    origin = run(["git", "rev-parse", "--short", "origin/main"])
    status = run(["git", "status", "--short"])

    state = {
        "stage": "SYSTEM-RECTIFICATION-WAVE1",
        "generated_at": generated_at,
        "decision": "PASS_SYSTEM_RECTIFICATION_WAVE1_BUILT",
        "local_head": head,
        "origin_main": origin,
        "git_status_short": status,
        "active_run_root": r"H:\AlphaFactory_CryptoData_archive\a7search6_mechanism_memory_seed_proxy_65k_20260630",
        "active_tasks": [
            "job_20260630_155424_765773",
            "job_20260630_160107_15cb00",
            "job_20260630_160408_46f4d8",
        ],
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "system_state_manifest.json", state)

    inv = inventory()
    inv_cols = ["path", "subsystem", "status", "evidence"]
    write_csv(RUNTIME / "core_inventory.csv", inv, inv_cols)
    summary_counter = Counter((row["subsystem"], row["status"]) for row in inv)
    summary = [
        {"subsystem": subsystem, "status": status_value, "count": count}
        for (subsystem, status_value), count in sorted(summary_counter.items())
    ]
    write_csv(RUNTIME / "core_status_summary.csv", summary, ["subsystem", "status", "count"])

    contracts = interface_contracts()
    write_json(RUNTIME / "core_interface_contracts.json", contracts)

    nodes, edges, mermaid = architecture()
    write_csv(RUNTIME / "architecture_nodes.csv", nodes, ["id", "label", "type"])
    write_csv(RUNTIME / "architecture_edges.csv", edges, ["from", "to", "relation"])

    (REPORTS / "CRYPTO_SYSTEM_RECTIFICATION_STATE_FREEZE_20260630.md").write_text(
        "\n".join(
            [
                "# CRYPTO SYSTEM RECTIFICATION STATE FREEZE 20260630",
                "",
                f"Generated: `{generated_at}`",
                "",
                "## Decision",
                "",
                "`PASS_SYSTEM_RECTIFICATION_STATE_FREEZE_BUILT`",
                "",
                "## Git",
                "",
                f"- local HEAD: `{head}`",
                f"- origin/main: `{origin}`",
                f"- git status short: `{status or '<clean>'}`",
                "",
                "## Active Remote Search",
                "",
                f"- run root: `{state['active_run_root']}`",
                f"- task ids: `{', '.join(state['active_tasks'])}`",
                "- boundary: proxy/research only; no alpha proof or deployment authorization.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    (REPORTS / "CRYPTO_SYSTEM_CORE_INVENTORY_20260630.md").write_text(
        "\n".join(
            [
                "# CRYPTO SYSTEM CORE INVENTORY 20260630",
                "",
                f"Generated: `{generated_at}`",
                "",
                "## Decision",
                "",
                "`PASS_SYSTEM_CORE_INVENTORY_BUILT`",
                "",
                "## Summary",
                "",
                md_table(summary, ["subsystem", "status", "count"], 100),
                "",
                "## Key Core Candidates",
                "",
                md_table([row for row in inv if row["status"] in {"keep_core", "wrap_with_contract"}], inv_cols, 80),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    contract_rows = [
        {
            "interface": name,
            "required": ", ".join(value["required"]),
            "fail_closed_on": ", ".join(value["fail_closed_on"]),
            "authorizes": ", ".join(value["authorizes"]),
        }
        for name, value in contracts.items()
    ]
    (REPORTS / "CRYPTO_SYSTEM_CORE_INTERFACE_CONTRACTS_20260630.md").write_text(
        "\n".join(
            [
                "# CRYPTO SYSTEM CORE INTERFACE CONTRACTS 20260630",
                "",
                f"Generated: `{generated_at}`",
                "",
                "## Decision",
                "",
                "`PASS_SYSTEM_CORE_INTERFACE_CONTRACTS_BUILT`",
                "",
                md_table(contract_rows, ["interface", "required", "fail_closed_on", "authorizes"], 40),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    (REPORTS / "CRYPTO_SYSTEM_ARCHITECTURE_BLUEPRINT_20260630.md").write_text(
        "\n".join(
            [
                "# CRYPTO SYSTEM ARCHITECTURE BLUEPRINT 20260630",
                "",
                f"Generated: `{generated_at}`",
                "",
                "## Decision",
                "",
                "`PASS_SYSTEM_ARCHITECTURE_BLUEPRINT_BUILT`",
                "",
                "## Target Verified-Core Flow",
                "",
                mermaid,
                "",
                "## Nodes",
                "",
                md_table(nodes, ["id", "label", "type"], 50),
                "",
                "## Edges",
                "",
                md_table(edges, ["from", "to", "relation"], 80),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    manifest = {
        **state,
        "outputs": {
            "state_freeze_report": str(REPORTS / "CRYPTO_SYSTEM_RECTIFICATION_STATE_FREEZE_20260630.md"),
            "core_inventory_report": str(REPORTS / "CRYPTO_SYSTEM_CORE_INVENTORY_20260630.md"),
            "interface_contract_report": str(REPORTS / "CRYPTO_SYSTEM_CORE_INTERFACE_CONTRACTS_20260630.md"),
            "architecture_blueprint_report": str(REPORTS / "CRYPTO_SYSTEM_ARCHITECTURE_BLUEPRINT_20260630.md"),
            "core_inventory": str(RUNTIME / "core_inventory.csv"),
            "core_status_summary": str(RUNTIME / "core_status_summary.csv"),
            "core_interface_contracts": str(RUNTIME / "core_interface_contracts.json"),
            "architecture_nodes": str(RUNTIME / "architecture_nodes.csv"),
            "architecture_edges": str(RUNTIME / "architecture_edges.csv"),
        },
    }
    write_json(RUNTIME / "wave1_manifest.json", manifest)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
