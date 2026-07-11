from __future__ import annotations

import json
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from alphafactory_crypto.negative_controls import audit_future_wrong_lag


RUNTIME = REPO / "runtime" / "a7b0_future_wrong_lag_control_20260711"
REPORT = REPO / "reports" / "CRYPTO_B0_FUTURE_WRONG_LAG_CONTROL_20260711.md"


def build() -> dict[str, object]:
    clean = audit_future_wrong_lag(1.2, -0.1)
    leakage = audit_future_wrong_lag(0.8, 1.5)
    payload: dict[str, object] = {
        "decision": "PASS_B0_FUTURE_WRONG_LAG_CONTROL_HARNESS",
        "variant": "future_wrong_lag_24h",
        "clean_fixture": clean.__dict__,
        "leakage_fixture": leakage.__dict__,
        "production_control_status": "IMPLEMENTED_NOT_EXECUTED_DURING_HOLD_RESEARCH",
        "search_started": False,
        "forward_performance_read": False,
        "authorizes_candidate_feedback": False,
    }
    if clean.future_dominates or not leakage.future_dominates:
        raise RuntimeError("future wrong-lag harness failed to distinguish clean and leakage fixtures")
    RUNTIME.mkdir(parents=True, exist_ok=True)
    (RUNTIME / "future_wrong_lag_audit_summary.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(
        "\n".join(
            [
                "# Crypto B0 Future Wrong-Lag Negative Control",
                "",
                f"Decision: `{payload['decision']}`",
                "",
                "`future_wrong_lag_24h` applies the signal from t+24h at t, leaving the final 24 hours unavailable. It is deliberately impossible under PIT semantics.",
                "",
                f"- clean fixture: `{clean.status}`",
                f"- leakage fixture: `{leakage.status}`",
                "- strict reward integration: implemented",
                "- production execution: not run during HOLD_RESEARCH",
                "- candidate feedback authorization: false",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
