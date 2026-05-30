from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff52_materialization_preflight_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FF52_MATERIALIZATION_PREFLIGHT_CONTRACT_20260531.md"


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

    e51 = read_json(REPO / "runtime" / "a7ff51e_non_l5_heavy_generation" / "a7ff51e_manifest.json")
    if e51.get("decision") != "PASS_A7FF51E_NON_L5_HEAVY_GENERATION_STATIC_READY":
        raise SystemExit(f"A7FF51E is not static-ready: {e51.get('decision')}")

    contract = {
        "stage": "A7FF-52",
        "name": "materialization preflight contract for A7FF51E blueprints",
        "decision": "PASS_A7FF52_CONTRACT_READY",
        "source": "A7FF-51E",
        "purpose": "define bounded materialization preflight before any numeric replay",
        "input_queue": "runtime/a7ff51e_non_l5_heavy_generation/a7ff51e_blueprint_queue.csv",
        "execution_budget_if_later_approved": {
            "sample_rows": 1200,
            "family_balanced": True,
            "min_rows_per_semantic_family": 100,
            "max_reports": 1,
            "max_runtime_tables": 3,
            "max_scripts": 1,
        },
        "hard_gates": {
            "eval_failure_count": 0,
            "missing_field_count": 0,
            "unsupported_operator_count": 0,
            "activity_ok_rate": ">= 0.60",
            "families_retained": ">= 6",
            "reference_family_primary_rows": 0,
        },
        "hard_stop_before": ["numeric replay", "formula search", "alpha proof", "shadow/paper/live"],
        "authorizes_materialization_preflight_execution": False,
        "authorizes_numeric_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    manifest = {
        "stage": "A7FF-52",
        "generated_at": now_utc(),
        "decision": "PASS_A7FF52_MATERIALIZATION_PREFLIGHT_CONTRACT_READY_NO_EXECUTION_AUTH",
        "source_a7ff51e_decision": e51.get("decision"),
        "blockers": [],
        "warnings": ["contract_only_no_materialization_execution"],
        "contract": contract,
        "executes_generation": False,
        "executes_materialization": False,
        "executes_numeric_probe": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_materialization_preflight_execution": False,
        "authorizes_numeric_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff52_manifest.json", manifest)
    report = f"""# CRYPTO A7FF-52 MATERIALIZATION PREFLIGHT CONTRACT

Generated: {manifest["generated_at"]}

## Decision

`{manifest["decision"]}`

This is a contract-only stage for the A7FF51E 50,000-blueprint queue. It does not start materialization, numeric replay, or search.

## Contract

```json
{json.dumps(contract, indent=2, sort_keys=True)}
```

## Boundary

```text
materialization executed: false
numeric replay executed: false
search executed: false
alpha proof / shadow / paper / live: false
```
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
