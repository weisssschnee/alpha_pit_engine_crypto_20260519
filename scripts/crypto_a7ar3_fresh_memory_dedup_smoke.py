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

from alphafactory_crypto.engines.search_memory import CryptoSearchMemory


DATE_TAG = "20260527"
REPORT_DIR = CRYPTO_ROOT / "reports"
RUNTIME_DIR = CRYPTO_ROOT / "runtime" / "a7ar3_fresh_memory_dedup_smoke"
A7AR1_CANDIDATES = CRYPTO_ROOT / "runtime" / "a7ar1_formula_engine_adapter_smoke" / "a7ar1_generated_candidates.csv"
MEMORY_POLICY = CRYPTO_ROOT / "config" / "crypto_search_memory_policy_v1.json"


def read_csv_dict(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


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


def make_report(summary: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Crypto A7AR-3 Fresh Memory And Dedup Smoke",
            "",
            "## Decision",
            "",
            summary["decision"],
            "",
            "## Scope",
            "",
            "- Initializes a fresh crypto search memory namespace.",
            "- Ingests A7AR-1 generated formulas only.",
            "- Tests expression-key, skeleton-key, and production-key bookkeeping.",
            "- Does not inherit CN memory payloads and does not run replay/search.",
            "",
            "## Results",
            "",
            f"- initial_inherited_paths: {summary['initial_inherited_paths']}",
            f"- initial_expression_keys: {summary['initial_expression_keys']}",
            f"- initial_skeleton_keys: {summary['initial_skeleton_keys']}",
            f"- input_candidates: {summary['input_candidates']}",
            f"- accepted_records: {summary['accepted_records']}",
            f"- duplicate_events: {summary['duplicate_events']}",
            f"- skeleton_repeat_events_soft: {summary['skeleton_repeat_events']}",
            f"- expression_key_count: {summary['expression_key_count']}",
            f"- skeleton_key_count: {summary['skeleton_key_count']}",
            f"- production_key_count: {summary['production_key_count']}",
            "",
            "## Authorization",
            "",
            "- A7AR-4 pre-replay ranker adapter smoke is authorized if this decision is PASS.",
            "- A7AL-2 formula search remains not authorized.",
        ]
    )


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    policy = json.loads(MEMORY_POLICY.read_text(encoding="utf-8"))
    namespace = policy["crypto_namespace"]["memory_namespace"]
    candidates = read_csv_dict(A7AR1_CANDIDATES)
    memory = CryptoSearchMemory.fresh(namespace=namespace)

    initial = {
        "initial_inherited_paths": len(memory.inherited_paths),
        "initial_expression_keys": len(memory.expression_keys),
        "initial_skeleton_keys": len(memory.skeleton_keys),
    }
    accepted = 0
    for row in candidates:
        if memory.add_candidate(row):
            accepted += 1
    payload = memory.to_payload()
    records = payload["records"]
    production_counts = Counter(record["production_key"] for record in records)
    family_counts = Counter(record["family"] for record in records)

    summary = {
        "decision": "",
        **initial,
        "input_candidates": len(candidates),
        "accepted_records": accepted,
        "duplicate_events": len(payload["duplicate_events"]),
        "skeleton_repeat_events": len(payload["skeleton_repeat_events"]),
        "expression_key_count": len(payload["expression_keys"]),
        "skeleton_key_count": len(payload["skeleton_keys"]),
        "production_key_count": len(production_counts),
        "cn_memory_payload_inherited": payload["cn_memory_payload_inherited"],
        "a7ar4_authorized": False,
        "a7al2_formula_search_authorized": False,
        "alpha_proof_authorized": False,
        "shadow_paper_live_authorized": False,
    }
    passed = (
        summary["initial_inherited_paths"] == 0
        and summary["initial_expression_keys"] == 0
        and summary["initial_skeleton_keys"] == 0
        and summary["input_candidates"] == 1000
        and summary["accepted_records"] >= 950
        and summary["duplicate_events"] == 0
        and summary["cn_memory_payload_inherited"] is False
    )
    summary["decision"] = "PASS_A7AR3_FRESH_MEMORY_DEDUP_SMOKE" if passed else "HOLD_A7AR3_FRESH_MEMORY_DEDUP_SMOKE"
    summary["a7ar4_authorized"] = passed

    memory.write(RUNTIME_DIR / "crypto_search_memory_fresh_v1.json")
    write_csv(
        RUNTIME_DIR / "a7ar3_memory_records.csv",
        records,
        [
            "candidate_id",
            "expression",
            "family",
            "field_families",
            "expression_key",
            "skeleton_key",
            "production_key",
            "operator_signature",
            "horizon_signature",
        ],
    )
    write_csv(
        RUNTIME_DIR / "a7ar3_duplicate_events.csv",
        payload["duplicate_events"],
        ["candidate_id", "duplicate_type", "key"],
    )
    write_csv(
        RUNTIME_DIR / "a7ar3_skeleton_repeat_events_soft.csv",
        payload["skeleton_repeat_events"],
        ["candidate_id", "duplicate_type", "key"],
    )
    write_csv(
        RUNTIME_DIR / "a7ar3_production_key_counts.csv",
        [{"production_key": key, "count": value} for key, value in sorted(production_counts.items())],
        ["production_key", "count"],
    )
    write_csv(
        RUNTIME_DIR / "a7ar3_family_counts.csv",
        [{"family": key, "count": value} for key, value in sorted(family_counts.items())],
        ["family", "count"],
    )
    write_json(RUNTIME_DIR / "a7ar3_decision_record.json", summary)
    write_json(
        RUNTIME_DIR / "a7ar3_manifest.json",
        {
            "object_id": "crypto_a7ar3_fresh_memory_dedup_smoke",
            "decision": summary["decision"],
            "memory_policy": str(MEMORY_POLICY),
            "memory_output": str(RUNTIME_DIR / "crypto_search_memory_fresh_v1.json"),
        },
    )
    (REPORT_DIR / f"CRYPTO_A7AR3_FRESH_MEMORY_DEDUP_SMOKE_{DATE_TAG}.md").write_text(make_report(summary), encoding="utf-8")
    print(summary["decision"])


if __name__ == "__main__":
    main()
