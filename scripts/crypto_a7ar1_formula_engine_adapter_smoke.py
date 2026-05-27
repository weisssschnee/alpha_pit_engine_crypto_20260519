from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

CRYPTO_ROOT = Path(__file__).resolve().parents[1]
if str(CRYPTO_ROOT) not in sys.path:
    sys.path.insert(0, str(CRYPTO_ROOT))

from alphafactory_crypto.engines.formula_gen_v2_adapter import (
    CryptoFormulaGenV2Adapter,
    validate_expression,
)


DATE_TAG = "20260527"
REPORT_DIR = CRYPTO_ROOT / "reports"
RUNTIME_DIR = CRYPTO_ROOT / "runtime" / "a7ar1_formula_engine_adapter_smoke"
CONFIG_PATH = CRYPTO_ROOT / "config" / "crypto_formula_gen_v2_motif_pack_v1.json"
MEMORY_POLICY_PATH = CRYPTO_ROOT / "config" / "crypto_search_memory_policy_v1.json"
N_CANDIDATES = 1000


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


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def candidate_rows(adapter: CryptoFormulaGenV2Adapter) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    config = load_json(CONFIG_PATH)
    rows: list[dict[str, Any]] = []
    audit_rows: list[dict[str, Any]] = []
    seen_expressions: set[str] = set()
    index = 0
    max_attempts = N_CANDIDATES * 30
    while len(rows) < N_CANDIDATES and index < max_attempts:
        candidate = adapter.generate(index=index)
        index += 1
        if candidate.expression in seen_expressions:
            continue
        seen_expressions.add(candidate.expression)
        validation = validate_expression(candidate.expression, adapter.allowed_fields, config)
        rows.append(
            {
                "candidate_id": candidate.candidate_id,
                "expression": candidate.expression,
                "family": candidate.family,
                "field_families": "|".join(candidate.field_families),
                "fields": "|".join(candidate.fields),
                "operators": "|".join(candidate.operators),
                "windows": "|".join(str(value) for value in candidate.windows),
                "cn_memory_payload_inherited": str(candidate.metadata["cn_memory_payload_inherited"]),
                "cn_reward_payload_inherited": str(candidate.metadata["cn_reward_payload_inherited"]),
            }
        )
        audit_rows.append(
            {
                "candidate_id": candidate.candidate_id,
                "passed": validation["passed"],
                "reasons": "|".join(validation["reasons"]),
                "has_cn_memory_payload": candidate.metadata["cn_memory_payload_inherited"],
                "has_cn_reward_payload": candidate.metadata["cn_reward_payload_inherited"],
            }
        )
    return rows, audit_rows


def count_rows(rows: list[dict[str, Any]], key: str, sep: str | None = None) -> list[dict[str, Any]]:
    counts: Counter[str] = Counter()
    for row in rows:
        value = str(row.get(key, ""))
        if sep:
            for item in [part for part in value.split(sep) if part]:
                counts[item] += 1
        else:
            counts[value] += 1
    return [{"name": name, "count": count} for name, count in sorted(counts.items())]


def memory_reset_audit() -> list[dict[str, Any]]:
    policy = load_json(MEMORY_POLICY_PATH)
    initial = policy.get("initial_state") or {}
    return [
        {
            "check": "fresh_memory_required",
            "status": "pass" if initial.get("fresh_memory_required") is True else "fail",
            "detail": str(initial.get("fresh_memory_required")),
        },
        {
            "check": "expression_keys_empty",
            "status": "pass" if initial.get("expression_keys") == [] else "fail",
            "detail": str(len(initial.get("expression_keys") or [])),
        },
        {
            "check": "skeleton_keys_empty",
            "status": "pass" if initial.get("skeleton_keys") == [] else "fail",
            "detail": str(len(initial.get("skeleton_keys") or [])),
        },
        {
            "check": "records_empty",
            "status": "pass" if initial.get("records") == [] else "fail",
            "detail": str(len(initial.get("records") or [])),
        },
        {
            "check": "inherited_paths_empty",
            "status": "pass" if initial.get("inherited_paths") == [] else "fail",
            "detail": str(len(initial.get("inherited_paths") or [])),
        },
    ]


def make_report(summary: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Crypto A7AR-1 Formula Engine Adapter Smoke",
            "",
            "## Decision",
            "",
            summary["decision"],
            "",
            "## Scope",
            "",
            "- Importable crypto FormulaGenV2-style adapter package was created.",
            "- The adapter inherits CN engine structure only: role/motif generation, typed metadata, and validation shape.",
            "- It does not inherit CN search memory, candidate ledgers, clusters, retained flags, or reward payloads.",
            "- This smoke does not run replay and does not authorize formula search beyond the adapter gate.",
            "",
            "## Results",
            "",
            f"- generated_candidates: {summary['generated_candidates']}",
            f"- validation_passed: {summary['validation_passed']}",
            f"- validation_failed: {summary['validation_failed']}",
            f"- unique_expressions: {summary['unique_expressions']}",
            f"- cn_memory_payload_violations: {summary['cn_memory_payload_violations']}",
            f"- cn_reward_payload_violations: {summary['cn_reward_payload_violations']}",
            f"- cn_stock_field_violations: {summary['cn_stock_field_violations']}",
            f"- memory_reset_checks_failed: {summary['memory_reset_checks_failed']}",
            "",
            "## Next Gate",
            "",
            "A7AR-2 must adapt feature algebra and operator evaluation before any replay or formula search.",
        ]
    )


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    adapter = CryptoFormulaGenV2Adapter.from_path(CONFIG_PATH, seed="a7ar1_crypto_formula_adapter")
    rows, audit_rows = candidate_rows(adapter)
    memory_rows = memory_reset_audit()

    unique_expressions = len({row["expression"] for row in rows})
    validation_failed = sum(1 for row in audit_rows if str(row["passed"]) != "True")
    memory_failed = sum(1 for row in memory_rows if row["status"] != "pass")
    cn_memory_violations = sum(1 for row in rows if row["cn_memory_payload_inherited"] != "False")
    cn_reward_violations = sum(1 for row in rows if row["cn_reward_payload_inherited"] != "False")
    cn_stock_violations = sum(1 for row in audit_rows if "banned_cn_token" in row["reasons"])

    passed = (
        len(rows) == N_CANDIDATES
        and validation_failed == 0
        and unique_expressions >= 950
        and cn_memory_violations == 0
        and cn_reward_violations == 0
        and cn_stock_violations == 0
        and memory_failed == 0
    )
    decision = "PASS_A7AR1_FORMULA_ENGINE_ADAPTER_SMOKE" if passed else "HOLD_A7AR1_FORMULA_ENGINE_ADAPTER_SMOKE"
    summary = {
        "decision": decision,
        "generated_candidates": len(rows),
        "validation_passed": len(rows) - validation_failed,
        "validation_failed": validation_failed,
        "unique_expressions": unique_expressions,
        "cn_memory_payload_violations": cn_memory_violations,
        "cn_reward_payload_violations": cn_reward_violations,
        "cn_stock_field_violations": cn_stock_violations,
        "memory_reset_checks_failed": memory_failed,
        "a7al2_formula_search_authorized": False,
        "alpha_proof_authorized": False,
        "shadow_paper_live_authorized": False,
    }

    write_csv(
        RUNTIME_DIR / "a7ar1_generated_candidates.csv",
        rows,
        [
            "candidate_id",
            "expression",
            "family",
            "field_families",
            "fields",
            "operators",
            "windows",
            "cn_memory_payload_inherited",
            "cn_reward_payload_inherited",
        ],
    )
    write_csv(RUNTIME_DIR / "a7ar1_validation_audit.csv", audit_rows, ["candidate_id", "passed", "reasons", "has_cn_memory_payload", "has_cn_reward_payload"])
    write_csv(RUNTIME_DIR / "a7ar1_family_counts.csv", count_rows(rows, "family"), ["name", "count"])
    write_csv(RUNTIME_DIR / "a7ar1_field_family_counts.csv", count_rows(rows, "field_families", sep="|"), ["name", "count"])
    write_csv(RUNTIME_DIR / "a7ar1_operator_counts.csv", count_rows(rows, "operators", sep="|"), ["name", "count"])
    write_csv(RUNTIME_DIR / "a7ar1_memory_reset_audit.csv", memory_rows, ["check", "status", "detail"])
    write_json(RUNTIME_DIR / "a7ar1_decision_record.json", summary)
    write_json(
        RUNTIME_DIR / "a7ar1_manifest.json",
        {
            "object_id": "crypto_a7ar1_formula_engine_adapter_smoke",
            "decision": decision,
            "config": str(CONFIG_PATH),
            "memory_policy": str(MEMORY_POLICY_PATH),
            "outputs": {
                "generated_candidates": str(RUNTIME_DIR / "a7ar1_generated_candidates.csv"),
                "validation_audit": str(RUNTIME_DIR / "a7ar1_validation_audit.csv"),
                "memory_reset_audit": str(RUNTIME_DIR / "a7ar1_memory_reset_audit.csv"),
            },
        },
    )
    (REPORT_DIR / f"CRYPTO_A7AR1_FORMULA_ENGINE_ADAPTER_SMOKE_{DATE_TAG}.md").write_text(make_report(summary), encoding="utf-8")
    print(decision)


if __name__ == "__main__":
    main()
