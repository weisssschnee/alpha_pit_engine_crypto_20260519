from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff51_compact_non_l5_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FF51_COMPACT_NON_L5_CONTRACT_20260531.md"


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

    r11 = read_json(REPO / "runtime" / "a7ffr11_feature_label_objective_reset" / "a7ffr11_manifest.json")
    if not r11.get("authorizes_a7ff51_contract"):
        raise SystemExit(f"A7FF-R11 does not authorize A7FF-51 contract: {r11.get('decision')}")

    contract = {
        "stage": "A7FF-51",
        "name": "compact non-L5-first derived generation contract",
        "decision": "PASS_A7FF51_COMPACT_CONTRACT_READY",
        "purpose": "define the next large generation execution without starting it",
        "source": "A7FF-R11",
        "contract_scope": {
            "primary_objective": "build non-reference, non-L5 candidate supply",
            "primary_labels": ["L0_raw_forward_return", "L1_cross_sectional_relative_return", "L3_liquidity_tier_relative_return"],
            "supporting_only_labels": ["L5_vol_adjusted_return", "L7_ranked_future_return"],
            "reference_family_cannot_count_as_primary": True,
        },
        "execution_budget_if_later_approved": {
            "blueprint_target": 50000,
            "max_runtime_tables": 3,
            "max_reports": 1,
            "max_scripts": 1,
        },
        "generation_rules": {
            "must_include_semantic_families": [
                "funding_like|basis_premium_like",
                "regime_state|price_return_like",
                "basis_premium_like|price_return_like",
                "positioning_like|price_return_like",
                "open_interest_like|price_return_like",
                "taker_flow_like|basis_premium_like",
                "liquidity_like|price_return_like",
                "volatility_like|basis_premium_like",
            ],
            "forbidden_primary_family": ["basis_premium_like|basis_premium_like"],
            "family_cap": 0.30,
            "motif_cap": 0.25,
            "require_non_l5_first_scoring": True,
        },
        "pre_replay_gates": {
            "min_non_reference_non_l5_static_candidates": 200,
            "min_semantic_families": 6,
            "top_family_share_max": 0.30,
            "reference_family_rows_count_as_primary": False,
        },
        "hard_stop_before": [
            "numeric replay",
            "formula search",
            "alpha proof",
            "shadow/paper/live",
        ],
        "authorizes_generation_execution": False,
        "authorizes_numeric_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }

    manifest = {
        "stage": "A7FF-51",
        "generated_at": now_utc(),
        "decision": "PASS_A7FF51_COMPACT_NON_L5_CONTRACT_READY_NO_EXECUTION_AUTH",
        "source_a7ffr11_decision": r11.get("decision"),
        "blockers": [],
        "warnings": ["contract_only_no_generation_execution"],
        "contract": contract,
        "executes_generation": False,
        "executes_numeric_probe": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_generation_execution": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff51_manifest.json", manifest)

    report = f"""# CRYPTO A7FF-51 COMPACT NON-L5 CONTRACT

Generated: {manifest["generated_at"]}

## Decision

`{manifest["decision"]}`

This is a contract-only stage. It defines the next non-L5-first large generation execution but does not start it.

## Contract

```json
{json.dumps(contract, indent=2, sort_keys=True)}
```

## Boundary

```text
generation executed: false
numeric replay executed: false
search executed: false
alpha proof / shadow / paper / live: false
```
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
