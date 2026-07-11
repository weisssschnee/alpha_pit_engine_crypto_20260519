from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from alphafactory_crypto.funding_events import (
    audit_cashflow_semantics,
    audit_funding_event_detection,
    canonicalize_funding_events,
)


RUNTIME = REPO / "runtime" / "a7b0_funding_event_contract_20260711"
REPORT = REPO / "reports" / "CRYPTO_B0_FUNDING_EVENT_CONTRACT_20260711.md"


def build() -> dict[str, object]:
    expected_raw = pd.DataFrame(
        {
            "symbol": ["BTCUSDT"] * 4,
            "funding_time": [
                "2026-01-01 00:00Z",
                "2026-01-01 08:00Z",
                "2026-01-01 16:00Z",
                "2026-01-02 00:00Z",
            ],
            "funding_rate": [0.0001, -0.0001, 0.0002, 0.0001],
        }
    )
    expected = canonicalize_funding_events(expected_raw)
    detected = expected.iloc[[0, 1, 3]].copy().reset_index(drop=True)
    detected.loc[1, "funding_time_utc"] += pd.Timedelta("20m")
    audit = audit_funding_event_detection(expected, detected, tolerance="30m")
    cashflow = audit_cashflow_semantics(expected)
    summary: dict[str, object] = {
        "decision": "PASS_B0_FUNDING_EVENT_CONTRACT_AND_AUDIT_HARNESS",
        "fixture_scope": "synthetic contract fixture only",
        "production_recall_status": "UNMEASURED_NO_NEW_FORWARD_READ",
        "event_audit": audit.summary,
        "cashflow_audit": cashflow,
        "search_started": False,
        "forward_performance_read": False,
        "authorizes_generator": False,
        "authorizes_reward": False,
    }
    RUNTIME.mkdir(parents=True, exist_ok=True)
    expected.to_csv(RUNTIME / "expected_events.csv", index=False)
    detected.to_csv(RUNTIME / "detected_events.csv", index=False)
    audit.matches.to_csv(RUNTIME / "event_matches.csv", index=False)
    audit.missed.to_csv(RUNTIME / "event_misses.csv", index=False)
    audit.false_positives.to_csv(RUNTIME / "event_false_positives.csv", index=False)
    (RUNTIME / "funding_event_audit_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(
        "\n".join(
            [
                "# Crypto B0 Funding Event Contract",
                "",
                f"Decision: `{summary['decision']}`",
                "",
                "Native venue settlement time defines event identity. Repeated last-known rates are state, not events. Missing native event time fails closed.",
                "",
                "Positive funding rate means long pays and short receives; long and short cashflow rates must sum to zero.",
                "",
                "## Synthetic Audit Harness",
                "",
                f"- expected events: `{audit.summary['expected_events']}`",
                f"- detected events: `{audit.summary['detected_events']}`",
                f"- matched events: `{audit.summary['matched_events']}`",
                f"- missed events: `{audit.summary['missed_events']}`",
                f"- recall: `{audit.summary['recall']}`",
                f"- precision: `{audit.summary['precision']}`",
                f"- tolerance seconds: `{audit.summary['tolerance_seconds']}`",
                f"- max absolute timing error seconds: `{audit.summary['timing_error_abs_seconds_max']}`",
                f"- cashflow semantics pass: `{cashflow['pass']}`",
                "",
                "Production recall remains unmeasured because B0 does not authorize new forward reads or an unsealed truth set.",
                "",
                "This contract authorizes audit and Feature/State Fabric input design only. It does not authorize generator, reward, memory, or search use.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return summary


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
