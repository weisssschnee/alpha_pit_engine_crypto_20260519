from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from alphafactory_crypto.benchmarks import BenchmarkRegistry, make_spec


SOURCE = REPO / "config" / "crypto_benchmark_registry_v1.json"
RUNTIME = REPO / "runtime" / "a7b0_benchmark_registry_20260711"
REGISTRY = RUNTIME / "benchmark_registry.csv"
MANIFEST = RUNTIME / "benchmark_registry_manifest.json"
REPORT = REPO / "reports" / "CRYPTO_B0_BENCHMARK_REGISTRY_20260711.md"


def build() -> dict[str, object]:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    registry = BenchmarkRegistry()
    for row in source["definitions"]:
        registry.register(make_spec(row))
    rows = []
    for spec in registry.values():
        rows.append(
            {
                "benchmark_id": spec.benchmark_id,
                "version": spec.version,
                "kind": spec.kind,
                "input_fields": ";".join(spec.input_fields),
                "input_roles": ";".join(spec.input_roles),
                "evaluation_space": spec.evaluation_space,
                "feedback_permission": spec.feedback_permission,
                "execution_allowed_b0": False,
                "positive_memory_allowed": False,
                "description": spec.description,
            }
        )
    payload: dict[str, object] = {
        "decision": "PASS_B0_BENCHMARK_REGISTRY_INTERFACE",
        "definition_count": len(rows),
        "executed_benchmark_count": 0,
        "observation_feedback_permission": "REPORT_ONLY",
        "positive_memory_allowed": False,
        "search_started": False,
        "forward_performance_read": False,
    }
    RUNTIME.mkdir(parents=True, exist_ok=True)
    with REGISTRY.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    MANIFEST.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(
        "\n".join(
            [
                "# Crypto B0 Benchmark Registry",
                "",
                f"Decision: `{payload['decision']}`",
                "",
                f"- definitions: `{len(rows)}`",
                "- executed benchmarks: `0`",
                "- inputs: `benchmark-only`",
                "- observation feedback: `REPORT_ONLY`",
                "- positive memory allowed: `false`",
                "",
                "B0 registers interfaces only and does not read or rank performance.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
