from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff24r4_repaired_numeric_wave_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FF24R4_REPAIRED_NUMERIC_WAVE_CONTRACT_20260531.md"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    r3 = read_json(REPO / "runtime" / "a7ff24r3_dense_materializer_preflight" / "a7ff24r3_manifest.json")
    if not r3.get("authorizes_repaired_queue_numeric_wave_contract"):
        raise SystemExit(f"A7FF-24R3 does not authorize 24R4 contract: {r3.get('decision')}")

    contract = {
        "stage": "A7FF-24R4",
        "name": "repaired queue numeric wave execution contract",
        "decision": "PASS_A7FF24R4_CONTRACT_READY",
        "purpose": "define repaired 2400-row numeric wave without starting it",
        "source": "A7FF-24R3",
        "preconditions_confirmed": {
            "dense_materializer_preflight_pass": True,
            "eval_failure_count": r3.get("eval_failure_count"),
            "dense_tail_activity_ok_count": r3.get("dense_tail_activity_ok_count"),
            "raw_funding_rate_tail_rows": r3.get("raw_funding_rate_tail_rows"),
        },
        "execution_budget_if_later_approved": {
            "queue_rows": 2400,
            "shards": 12,
            "max_reports": 1,
            "max_runtime_tables": 3,
            "max_scripts": 1,
        },
        "hard_gates": {
            "eval_failure_count": 0,
            "missing_numeric_fields": 0,
            "tail_raw_funding_rate_rows": 0,
            "non_l7_numeric_clue_rows": "> 0",
            "control_ratio_max_for_candidates": "< 0.80",
        },
        "hard_stop_before": ["formula search", "alpha proof", "shadow/paper/live"],
        "authorizes_numeric_wave_execution": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }

    manifest = {
        "stage": "A7FF-24R4",
        "generated_at": now_utc(),
        "decision": "PASS_A7FF24R4_REPAIRED_NUMERIC_WAVE_CONTRACT_READY_NO_EXECUTION_AUTH",
        "source_a7ff24r3_decision": r3.get("decision"),
        "blockers": [],
        "warnings": ["contract_only_no_numeric_wave_execution"],
        "contract": contract,
        "executes_generation": False,
        "executes_numeric_probe": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_numeric_wave_execution": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff24r4_manifest.json", manifest)

    report = f"""# CRYPTO A7FF-24R4 REPAIRED NUMERIC WAVE CONTRACT

Generated: {manifest["generated_at"]}

## Decision

`{manifest["decision"]}`

This is a contract-only stage. It defines the repaired 2400-row numeric wave but does not start it.

## Contract

```json
{json.dumps(contract, indent=2, sort_keys=True)}
```

## Boundary

```text
numeric wave executed: false
search executed: false
alpha proof / shadow / paper / live: false
```
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
