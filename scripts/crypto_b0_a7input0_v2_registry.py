from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from alphafactory_crypto.input_roles import classify_input_role, truthy, validate_registry_rows


ONTOLOGY = REPO / "runtime" / "a7ffr1_field_ontology_v3" / "a7ffr1_field_ontology_v3.csv"
RUNTIME = REPO / "runtime" / "a7input0_v2_field_roles_20260711"
REGISTRY = RUNTIME / "a7input0_v2_field_role_registry.csv"
MANIFEST = RUNTIME / "a7input0_v2_manifest.json"
REPORT = REPO / "reports" / "CRYPTO_B0_A7INPUT0_V2_FIELD_ROLES_20260711.md"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def build() -> dict[str, object]:
    ontology = read_csv(ONTOLOGY)
    rows = []
    for source in ontology:
        role, reason = classify_input_role(source)
        rows.append(
            {
                "field_name": source["field_name"],
                "input_role": role,
                "role_reason": reason,
                "semantic_type": source.get("semantic_type_v3", ""),
                "compiler_role": source.get("compiler_role_v3", ""),
                "allowed_roles": source.get("allowed_roles_v3", ""),
                "pit_lag_required": source.get("pit_lag_required", ""),
                "feature_available_time_primary": source.get("feature_available_time_primary", ""),
                "same_bar_execution_allowed": source.get("same_bar_execution_allowed", ""),
                "generator_enabled_b0": False,
                "primary_generator_eligible_after_b0": role == "primary" and truthy(source.get("timing_ok")),
                "decision_basis": "static ontology and timing contract only; no accepted family or OOS metric",
            }
        )
    validate_registry_rows(rows, {row["field_name"] for row in ontology})
    counts = Counter(row["input_role"] for row in rows)
    payload: dict[str, object] = {
        "decision": "PASS_A7INPUT0_V2_COMPLETE_ROLE_REGISTRY",
        "ontology_rows": len(ontology),
        "registry_rows": len(rows),
        "role_counts": dict(sorted(counts.items())),
        "generator_enabled_rows_b0": 0,
        "uses_accepted_family_or_oos_rank": False,
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
                "# Crypto B0 A7INPUT0-v2 Field Role Registry",
                "",
                f"Decision: `{payload['decision']}`",
                "",
                f"- ontology rows: `{len(ontology)}`",
                f"- registry rows: `{len(rows)}`",
                f"- role counts: `{dict(sorted(counts.items()))}`",
                "- generator enabled rows in B0: `0`",
                "- accepted-family/OOS ranking inputs: `false`",
                "",
                "Role assignment is structural and independent of current accepted candidates. `primary` is a role classification, not a B0 generator authorization.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
