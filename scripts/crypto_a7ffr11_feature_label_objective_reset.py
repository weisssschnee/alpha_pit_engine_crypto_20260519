from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffr11_feature_label_objective_reset"
REPORT = REPO / "reports" / "CRYPTO_A7FFR11_FEATURE_LABEL_OBJECTIVE_RESET_20260531.md"

A7FF49_MANIFEST = REPO / "runtime" / "a7ff49_existing_map_non_l5_mining" / "a7ff49_manifest.json"
A7FF49_SUMMARY = REPO / "runtime" / "a7ff49_existing_map_non_l5_mining" / "a7ff49_non_l5_candidate_summary.csv"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    try:
        return view.to_markdown(index=False)
    except ImportError:
        return "```text\n" + view.to_string(index=False) + "\n```"


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    f49 = read_json(A7FF49_MANIFEST)
    if f49.get("decision") != "HOLD_A7FF49_NO_NON_REFERENCE_NON_L5_CANDIDATES":
        raise SystemExit(f"A7FF-49 state does not require R11 reset: {f49.get('decision')}")

    summary = read_csv(A7FF49_SUMMARY)
    compact_policy = pd.DataFrame(
        [
            {
                "policy_area": "artifact_hygiene",
                "rule": "future A7FF stages should emit one report, one manifest, and only essential machine tables",
                "reason": "avoid runtime sprawl and preserve source-of-truth clarity",
            },
            {
                "policy_area": "label_target",
                "rule": "promotion requires non-reference evidence on L0/L1/L3 before L5 can support a clue",
                "reason": "current frozen pool is L5-only and does not translate to raw or relative labels",
            },
            {
                "policy_area": "reference_family",
                "rule": "basis_premium self-pair is reference-only until confirmed by non-self semantic pair",
                "reason": "A7FF-49 found all non-L5 evidence only inside the reference family",
            },
            {
                "policy_area": "next_execution",
                "rule": "authorize only a compact A7FF-51 non-L5-first generation contract; no search execution",
                "reason": "existing numeric maps do not contain a usable non-reference non-L5 pool",
            },
        ]
    )
    compact_policy.to_csv(RUNTIME / "a7ffr11_compact_reset_policy.csv", index=False)

    next_contract = {
        "stage": "A7FF-51",
        "name": "non-L5-first derived generation contract",
        "authorized": True,
        "execution_type": "contract_only",
        "no_search": True,
        "artifact_budget": {
            "max_new_reports": 1,
            "max_new_runtime_tables": 3,
            "required_manifest": True,
        },
        "hard_requirements": {
            "primary_labels": ["L0_raw_forward_return", "L1_cross_sectional_relative_return", "L3_liquidity_tier_relative_return"],
            "reference_family_cannot_count_as_primary": True,
            "control_ratio_max": 0.80,
            "min_non_reference_rows_before_replay": 6,
            "min_non_reference_families_before_replay": 2,
        },
        "blocked": ["formula_search", "large_search", "alpha_proof", "shadow", "paper", "live"],
    }

    manifest = {
        "stage": "A7FF-R11",
        "generated_at": now_utc(),
        "decision": "PASS_A7FFR11_FEATURE_LABEL_OBJECTIVE_RESET_READY_FOR_A7FF51_CONTRACT_NO_SEARCH_AUTH",
        "source_a7ff49_decision": f49.get("decision"),
        "blockers": [],
        "warnings": ["artifact_budget_enforced_for_future_a7ff_stages"],
        "reason": "A7FF-49 found zero non-reference non-L5 candidates in existing maps",
        "next_contract": next_contract,
        "executes_generation": False,
        "executes_numeric_probe": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_a7ff51_contract": True,
        "authorizes_generation_execution": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ffr11_manifest.json", manifest)

    report = f"""# CRYPTO A7FF-R11 FEATURE / LABEL OBJECTIVE RESET

Generated: {manifest["generated_at"]}

## Decision

`{manifest["decision"]}`

A7FF-R11 is a compact reset stage. It converts the A7FF-49 hold into a stricter non-L5-first objective policy and adds an artifact budget for future A7FF work.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Compact Reset Policy

{md_table(compact_policy)}

## A7FF-49 Non-L5 Summary

{md_table(summary)}

## Boundary

```text
generation executed: false
numeric probe executed: false
replay executed: false
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
