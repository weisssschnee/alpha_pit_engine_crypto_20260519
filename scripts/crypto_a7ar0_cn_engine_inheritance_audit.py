from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any


DATE_TAG = "20260527"
CRYPTO_ROOT = Path(__file__).resolve().parents[1]
CN_ROOT = Path(r"G:/Project_V7_Rotation/alpha_pit_engine_project_20260511")
REPORT_DIR = CRYPTO_ROOT / "reports"
RUNTIME_DIR = CRYPTO_ROOT / "runtime" / "a7ar0_cn_engine_inheritance_audit"
CONFIG_DIR = CRYPTO_ROOT / "config"


def sha16(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def exists_text(path: Path) -> str:
    return "yes" if path.exists() else "no"


def write_csv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def component_inventory() -> list[dict[str, Any]]:
    specs = [
        {
            "component": "formula_gen_v2_sampler",
            "cn_path": "src/our_system_phase2/formula_gen_v2/sampler.py",
            "crypto_reference_path": "cn_reference/formula_gen_v2/sampler.py",
            "role": "role-based motif formula generation and repair expansion",
            "inheritance_action": "port into crypto namespace with crypto field/operator adapter",
            "priority": "P0",
        },
        {
            "component": "typed_ast_and_macros",
            "cn_path": "src/our_system_phase2/formula_gen_v2/typed_ast.py",
            "crypto_reference_path": "cn_reference/formula_gen_v2/typed_ast.py",
            "role": "AST parsing, structural hashing, windows, operators, formula candidate metadata",
            "inheritance_action": "port with crypto-safe operator registry and timing checks",
            "priority": "P0",
        },
        {
            "component": "freeform_and_ablation_sampler",
            "cn_path": "src/our_system_phase2/formula_gen_v2/freeform_sampler.py",
            "crypto_reference_path": "cn_reference/formula_gen_v2/freeform_sampler.py",
            "role": "freeform AST exploration and paired ablation patterns",
            "inheritance_action": "port after FormulaGenV2 adapter parity",
            "priority": "P1",
        },
        {
            "component": "motif_packs",
            "cn_path": "src/our_system_phase2/formula_gen_v2/motif_pack_core.yaml",
            "crypto_reference_path": "cn_reference/formula_gen_v2/motif_pack_core.yaml",
            "role": "role templates, motif families, windows, constraints",
            "inheritance_action": "translate motif structure only; replace all CN stock fields",
            "priority": "P0",
        },
        {
            "component": "feature_algebra",
            "cn_path": "src/our_system_phase2/services/feature_algebra.py",
            "crypto_reference_path": "",
            "role": "formula evaluation semantics and feature composition",
            "inheritance_action": "port minimal crypto operator evaluator before formula search",
            "priority": "P0",
        },
        {
            "component": "variation_and_fingerprint",
            "cn_path": "src/our_system_phase2/services/variation.py",
            "crypto_reference_path": "",
            "role": "canonicalization, skeleton extraction, complexity, duplicate control",
            "inheritance_action": "port for crypto formula dedup and memory keys",
            "priority": "P0",
        },
        {
            "component": "search_memory_schema",
            "cn_path": "src/our_system_phase2/services/search_memory.py",
            "crypto_reference_path": "",
            "role": "expression/skeleton memory, production keys, reward proxy schema",
            "inheritance_action": "inherit schema only; initialize blank crypto memory",
            "priority": "P0",
        },
        {
            "component": "ledger_policy_and_bandit",
            "cn_path": "src/our_system_phase2/services/stock_pit_ledger_policy.py",
            "crypto_reference_path": "",
            "role": "search control policy, motif/operator allowlists, bandit state",
            "inheritance_action": "port policy mechanics; replace motif allowlists with crypto taxonomy",
            "priority": "P1",
        },
        {
            "component": "replay_ranker",
            "cn_path": "src/our_system_phase2/services/stock_pit_replay_ranker.py",
            "crypto_reference_path": "",
            "role": "pre-replay feature matrix, leakage guard, ranker calibration",
            "inheritance_action": "port only pre-replay matrix logic; replace target labels",
            "priority": "P1",
        },
        {
            "component": "selector_stack",
            "cn_path": "src/our_system_phase2/services/phase3e_selectors.py",
            "crypto_reference_path": "",
            "role": "candidate selection, diversity, cluster and book-aware scoring",
            "inheritance_action": "port after A7AL-1 baseline establishes field-family signal",
            "priority": "P2",
        },
        {
            "component": "vector_selector",
            "cn_path": "src/our_system_phase2/services/phase3g_vector_selector.py",
            "crypto_reference_path": "",
            "role": "vectorized selector and turnover/guard variants",
            "inheritance_action": "port after selector stack parity",
            "priority": "P2",
        },
        {
            "component": "real_market_validation",
            "cn_path": "src/our_system_phase2/services/real_market_validation.py",
            "crypto_reference_path": "",
            "role": "strict panel expression validation, audit, tradability checks",
            "inheritance_action": "adapt as crypto strict replay parity target, not direct run",
            "priority": "P1",
        },
        {
            "component": "proof_suite",
            "cn_path": "src/our_system_phase2/services/stock_pit_proof_suite.py",
            "crypto_reference_path": "",
            "role": "proof-stage reporting and locked validation suite",
            "inheritance_action": "defer until crypto research candidate pool exists",
            "priority": "P3",
        },
        {
            "component": "large_search_supervisor_worker",
            "cn_path": "src/our_system_phase2/runtime/stock_pit_large_search_supervisor.py",
            "crypto_reference_path": "",
            "role": "multi-worker large search orchestration",
            "inheritance_action": "port after generator/ranker parity and fresh crypto memory",
            "priority": "P2",
        },
        {
            "component": "runtime_state_registry",
            "cn_path": "src/our_system_phase2/services/runtime_state_registry.py",
            "crypto_reference_path": "",
            "role": "locked runtime state registry and forward state discipline",
            "inheritance_action": "port schema after alpha candidate freeze, not before",
            "priority": "P3",
        },
    ]
    rows: list[dict[str, Any]] = []
    for spec in specs:
        cn_path = CN_ROOT / spec["cn_path"]
        ref_path = CRYPTO_ROOT / spec["crypto_reference_path"] if spec["crypto_reference_path"] else Path("")
        rows.append(
            {
                **spec,
                "cn_exists": exists_text(cn_path),
                "crypto_reference_exists": exists_text(ref_path) if spec["crypto_reference_path"] else "no",
                "cn_sha16": sha16(cn_path),
                "crypto_reference_sha16": sha16(ref_path) if spec["crypto_reference_path"] else "",
                "crypto_executable_adapter_status": "missing_or_dry_only",
            }
        )
    return rows


def gap_matrix(inventory: list[dict[str, Any]]) -> list[dict[str, Any]]:
    status_by_component = {
        "formula_gen_v2_sampler": ("partial_reference_only", "no importable crypto package; current scripts use simplified generator"),
        "typed_ast_and_macros": ("partial_reference_only", "reference copied but no crypto field/operator adapter package"),
        "freeform_and_ablation_sampler": ("partial_reference_only", "reference copied but not active in crypto search"),
        "motif_packs": ("partial_reference_only", "CN pack copied; crypto pack is small and not equivalent"),
        "feature_algebra": ("missing", "no crypto equivalent found as reusable package"),
        "variation_and_fingerprint": ("missing", "dedup exists ad hoc in scripts, not inherited engine service"),
        "search_memory_schema": ("missing", "memory policy not active; no CN payload should be inherited"),
        "ledger_policy_and_bandit": ("missing", "A7M surrogate exists but not CN ledger policy"),
        "replay_ranker": ("missing", "A7M surrogate is empirical diagnostic; CN replay ranker not ported"),
        "selector_stack": ("missing", "stage scripts have caps but not CN selector stack"),
        "vector_selector": ("missing", "not ported"),
        "real_market_validation": ("partial_crypto_specific", "crypto has fast replay scripts; no reusable CN-style validation service"),
        "proof_suite": ("missing", "crypto proof suite not authorized"),
        "large_search_supervisor_worker": ("missing", "A7O wave runner is purpose-built; CN supervisor/worker not ported"),
        "runtime_state_registry": ("missing", "forward telemetry contracts exist; no CN runtime registry port"),
    }
    rows: list[dict[str, Any]] = []
    for item in inventory:
        status, detail = status_by_component[item["component"]]
        rows.append(
            {
                "component": item["component"],
                "priority": item["priority"],
                "gap_status": status,
                "gap_detail": detail,
                "must_port_before_a7al2_formula_search": "yes" if item["priority"] in {"P0", "P1"} else "no",
                "safe_to_copy_directly": "no",
                "required_crypto_adapter": item["inheritance_action"],
            }
        )
    return rows


def memory_policy_rows() -> list[dict[str, Any]]:
    return [
        {
            "policy_item": "schema",
            "inherit_from_cn": "yes",
            "inherit_payload": "no",
            "crypto_action": "Use LocalSearchMemory keying ideas and schema shape under crypto namespace.",
        },
        {
            "policy_item": "expression_keys",
            "inherit_from_cn": "no",
            "inherit_payload": "no",
            "crypto_action": "Initialize empty set; populate only from crypto candidates.",
        },
        {
            "policy_item": "skeleton_keys",
            "inherit_from_cn": "no",
            "inherit_payload": "no",
            "crypto_action": "Initialize empty set; avoid suppressing crypto formulas due to CN stock memory.",
        },
        {
            "policy_item": "production_rule_key",
            "inherit_from_cn": "yes",
            "inherit_payload": "no",
            "crypto_action": "Adapt context fields to engine/cell/horizon/neutralization namespace.",
        },
        {
            "policy_item": "reward_proxy",
            "inherit_from_cn": "structure_only",
            "inherit_payload": "no",
            "crypto_action": "Replace IC/OOS/replay components with A7AL pre-replay and neutralized metrics.",
        },
        {
            "policy_item": "candidate_records",
            "inherit_from_cn": "no",
            "inherit_payload": "no",
            "crypto_action": "Do not import CN candidate ledgers, retained flags, cluster ids, or replay metrics.",
        },
    ]


def adapter_plan_rows() -> list[dict[str, Any]]:
    return [
        {
            "stage": "A7AR-1",
            "name": "formula_engine_import_smoke",
            "objective": "Create importable crypto FormulaGenV2/typed AST adapter package.",
            "success_gate": "Generate 1000 crypto field-safe expressions with zero CN field references.",
            "authorized_search": "no",
        },
        {
            "stage": "A7AR-2",
            "name": "feature_algebra_parity_smoke",
            "objective": "Evaluate a fixed operator set on a tiny top498 slice with +1h/+2h timing.",
            "success_gate": "Operator parity, NaN/inf, activity, and timing checks pass.",
            "authorized_search": "no",
        },
        {
            "stage": "A7AR-3",
            "name": "fresh_memory_and_dedup_smoke",
            "objective": "Initialize crypto memory empty and test expression/skeleton/family dedup.",
            "success_gate": "Memory starts empty; duplicate control works only on crypto-generated formulas.",
            "authorized_search": "no",
        },
        {
            "stage": "A7AR-4",
            "name": "pre_replay_ranker_adapter_smoke",
            "objective": "Build CN-style pre-replay matrix from crypto-safe columns only.",
            "success_gate": "Forbidden post-replay and future/stress columns excluded mechanically.",
            "authorized_search": "no",
        },
        {
            "stage": "A7AR-5",
            "name": "a7al1_field_family_baseline_with_engine_services",
            "objective": "Run field-family baseline smoke using inherited dedup/ranker/selector services.",
            "success_gate": "A7AL-1 gates define whether A7AL-2 formula search can start.",
            "authorized_search": "field_family_smoke_only",
        },
    ]


def forbidden_rows() -> list[dict[str, Any]]:
    return [
        {
            "forbidden_item": "CN search_memory.json",
            "reason": "Would suppress or bias crypto search with stock candidate history.",
        },
        {
            "forbidden_item": "CN candidate_ledger.json records",
            "reason": "Stock candidate outcomes are not crypto evidence.",
        },
        {
            "forbidden_item": "CN expression_keys/skeleton_keys payload",
            "reason": "Only keying logic is reusable; payload is market-specific memory.",
        },
        {
            "forbidden_item": "CN stock fields and motif field lists",
            "reason": "Crypto fields require PIT/timing/venue-specific semantics.",
        },
        {
            "forbidden_item": "CN reward weights direct use",
            "reason": "Crypto needs neutralized top498, cost/lag, beta/liquidity/meme controls.",
        },
        {
            "forbidden_item": "CN runtime baselines as crypto proof",
            "reason": "Baselines are useful as chain-lock patterns, not crypto alpha evidence.",
        },
    ]


def make_report(
    inventory: list[dict[str, Any]],
    gaps: list[dict[str, Any]],
    memory_rows: list[dict[str, Any]],
    adapter_rows: list[dict[str, Any]],
) -> str:
    p0_missing = [row for row in gaps if row["priority"] == "P0" and row["gap_status"] in {"missing", "partial_reference_only"}]
    return "\n".join(
        [
            "# Crypto A7AR-0 CN Engine Inheritance Audit",
            "",
            "## Decision",
            "",
            "PASS_A7AR0_CN_ENGINE_FLOW_UNDERSTOOD_ADAPTER_REQUIRED",
            "",
            "## Boundary",
            "",
            "- CN repo was read-only for this audit.",
            "- Crypto may inherit engine structure and schema ideas.",
            "- Crypto must not inherit CN search memory payloads, candidate ledgers, cluster ids, retained flags, or reward outcomes.",
            "- This audit does not authorize A7AL-2 formula search, alpha proof, shadow, paper, or live.",
            "",
            "## Finding",
            "",
            "Crypto currently has many stage scripts and contracts, but the mature CN engine is only partially present as references.",
            "The missing execution services are material: feature algebra, search memory, ledger policy, replay ranker, selector stack, and large-search orchestration.",
            "",
            "## P0/P1 Components Required Before Formula Search",
            "",
            *[
                f"- {row['component']}: {row['gap_status']} - {row['gap_detail']}"
                for row in gaps
                if row["must_port_before_a7al2_formula_search"] == "yes"
            ],
            "",
            "## Memory Policy",
            "",
            *[
                f"- {row['policy_item']}: inherit_from_cn={row['inherit_from_cn']}, inherit_payload={row['inherit_payload']}; {row['crypto_action']}"
                for row in memory_rows
            ],
            "",
            "## Adapter Sequence",
            "",
            *[
                f"- {row['stage']} {row['name']}: {row['objective']} Gate: {row['success_gate']}"
                for row in adapter_rows
            ],
            "",
            "## Blockers",
            "",
            "- A7AL-2 formula search remains blocked until A7AR-1 through A7AR-4 pass.",
            "- Any non-empty CN memory import is a hard failure.",
            "- Any CN stock field in generated crypto expressions is a hard failure.",
            "",
            "## Summary Counts",
            "",
            f"- inventory_components: {len(inventory)}",
            f"- p0_or_p1_required_gaps: {len([row for row in gaps if row['must_port_before_a7al2_formula_search'] == 'yes'])}",
            f"- p0_missing_or_reference_only: {len(p0_missing)}",
        ]
    )


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)

    inventory = component_inventory()
    gaps = gap_matrix(inventory)
    memory_rows = memory_policy_rows()
    adapter_rows = adapter_plan_rows()
    forbidden = forbidden_rows()

    write_csv(
        RUNTIME_DIR / "a7ar0_cn_component_inventory.csv",
        inventory,
        [
            "component",
            "priority",
            "role",
            "cn_path",
            "cn_exists",
            "cn_sha16",
            "crypto_reference_path",
            "crypto_reference_exists",
            "crypto_reference_sha16",
            "crypto_executable_adapter_status",
            "inheritance_action",
        ],
    )
    write_csv(
        RUNTIME_DIR / "a7ar0_crypto_gap_matrix.csv",
        gaps,
        [
            "component",
            "priority",
            "gap_status",
            "gap_detail",
            "must_port_before_a7al2_formula_search",
            "safe_to_copy_directly",
            "required_crypto_adapter",
        ],
    )
    write_csv(
        RUNTIME_DIR / "a7ar0_memory_policy.csv",
        memory_rows,
        ["policy_item", "inherit_from_cn", "inherit_payload", "crypto_action"],
    )
    write_csv(
        RUNTIME_DIR / "a7ar0_adapter_plan.csv",
        adapter_rows,
        ["stage", "name", "objective", "success_gate", "authorized_search"],
    )
    write_csv(
        RUNTIME_DIR / "a7ar0_forbidden_inheritance.csv",
        forbidden,
        ["forbidden_item", "reason"],
    )

    decision = {
        "decision": "PASS_A7AR0_CN_ENGINE_FLOW_UNDERSTOOD_ADAPTER_REQUIRED",
        "created_at": DATE_TAG,
        "cn_repo_read_only": True,
        "modify_cn_repo_authorized": False,
        "inherit_engine_structure": True,
        "inherit_cn_memory_payloads": False,
        "a7al2_formula_search_authorized": False,
        "alpha_proof_authorized": False,
        "shadow_paper_live_authorized": False,
        "required_next_stages": ["A7AR-1", "A7AR-2", "A7AR-3", "A7AR-4"],
        "outputs": {
            "component_inventory": str(RUNTIME_DIR / "a7ar0_cn_component_inventory.csv"),
            "gap_matrix": str(RUNTIME_DIR / "a7ar0_crypto_gap_matrix.csv"),
            "memory_policy": str(RUNTIME_DIR / "a7ar0_memory_policy.csv"),
            "adapter_plan": str(RUNTIME_DIR / "a7ar0_adapter_plan.csv"),
            "forbidden_inheritance": str(RUNTIME_DIR / "a7ar0_forbidden_inheritance.csv"),
        },
    }
    write_json(RUNTIME_DIR / "a7ar0_decision_record.json", decision)
    write_json(
        RUNTIME_DIR / "a7ar0_manifest.json",
        {
            "object_id": "crypto_a7ar0_cn_engine_inheritance_audit",
            "decision": decision["decision"],
            "cn_root": str(CN_ROOT),
            "crypto_root": str(CRYPTO_ROOT),
            "cn_repo_read_only": True,
            "config_files": [
                str(CONFIG_DIR / "crypto_cn_engine_inheritance_v1.json"),
                str(CONFIG_DIR / "crypto_search_memory_policy_v1.json"),
            ],
            "component_count": len(inventory),
            "gap_count": len(gaps),
        },
    )

    report = make_report(inventory, gaps, memory_rows, adapter_rows)
    (REPORT_DIR / f"CRYPTO_A7AR0_CN_ENGINE_INHERITANCE_AUDIT_{DATE_TAG}.md").write_text(report, encoding="utf-8")
    print(decision["decision"])


if __name__ == "__main__":
    main()
