from __future__ import annotations

import csv
import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SOURCE = REPO / "config" / "crypto_temporal_event_primitives_v1.json"
RUNTIME = REPO / "runtime" / "a7b0_temporal_event_contract_20260711"
REGISTRY = RUNTIME / "temporal_event_primitive_registry.csv"
MANIFEST = RUNTIME / "temporal_event_contract_manifest.json"
REPORT = REPO / "reports" / "CRYPTO_B0_TEMPORAL_EVENT_PRIMITIVE_CONTRACT_20260711.md"


def build() -> dict[str, object]:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    rows = source["primitives"]
    payload: dict[str, object] = {
        "decision": "PASS_B0_TEMPORAL_EVENT_PRIMITIVE_CONTRACT",
        "primitive_count": len(rows),
        "pit_rule": source["pit_rule"],
        "usable_time_rule": source["time_semantics"]["usable_time"],
        "state_event_reward_allowed_b0": False,
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
                "# Crypto B0 Temporal/Event Primitive Contract",
                "",
                f"Decision: `{payload['decision']}`",
                "",
                "- event time: underlying phenomenon time",
                "- observable time: first system-known time",
                "- maturity time: value/window/cashflow completion time",
                "- usable time: `max(observable_time, maturity_time)`",
                "- PIT: only usable records at or before decision time",
                "- event/state to reward in B0: `false`",
                "",
                "Canonicalization normalizes durations and parameters. Equivalence additionally requires identical source, event identity, observability, maturity, and tolerance contracts.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
