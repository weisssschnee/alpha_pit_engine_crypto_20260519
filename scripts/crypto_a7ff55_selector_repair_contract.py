from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff55_selector_repair_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FF55_SELECTOR_REPAIR_CONTRACT_20260531.md"
A7FF54 = REPO / "runtime" / "a7ff54_numeric_clue_consolidation"

PRIMARY_LABELS = ["L0_raw_forward_return", "L1_cross_sectional_relative_return", "L3_liquidity_tier_relative_return"]
SECONDARY_LABELS = ["L5_vol_adjusted_return"]
DIAGNOSTIC_LABELS = ["L7_ranked_future_return"]


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


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

    m54 = read_json(A7FF54 / "a7ff54_manifest.json")
    if not m54.get("authorizes_a7ff55_selector_repair_contract"):
        raise SystemExit(f"A7FF-54 does not authorize A7FF-55: {m54.get('decision')}")

    selected_labels = read_csv(A7FF54 / "a7ff54_selected_label_distribution.csv")
    selected_family_labels = read_csv(A7FF54 / "a7ff54_selected_family_label_distribution.csv")
    selected_motifs = read_csv(A7FF54 / "a7ff54_selected_motif_distribution.csv")

    label_quota = pd.DataFrame(
        [
            {
                "label_family": label,
                "role": "primary",
                "min_selected_rows": 4,
                "max_selected_share": 0.35,
                "selection_rule": "must compete before L5/L7 rows; cannot be backfilled by L5",
            }
            for label in PRIMARY_LABELS
        ]
        + [
            {
                "label_family": "L5_vol_adjusted_return",
                "role": "secondary",
                "min_selected_rows": 0,
                "max_selected_share": 0.35,
                "selection_rule": "allowed only after primary-label quota is met",
            },
            {
                "label_family": "L7_ranked_future_return",
                "role": "diagnostic_only",
                "min_selected_rows": 0,
                "max_selected_share": 0.25,
                "selection_rule": "never promotes replay; diagnostic coverage only",
            },
        ]
    )
    label_quota.to_csv(RUNTIME / "a7ff55_label_quota_policy.csv", index=False)

    cap_policy = pd.DataFrame(
        [
            {"cap": "top_semantic_pair_share", "limit": 0.30, "action": "downrank_or_reject_after_cap"},
            {"cap": "top_motif_share", "limit": 0.30, "action": "downrank_or_reject_after_cap"},
            {"cap": "top_label_family_share", "limit": 0.35, "action": "downrank_or_reject_after_cap"},
            {"cap": "L5_share_without_primary_rows", "limit": 0.00, "action": "reject_queue"},
            {"cap": "L7_replay_promotion_share", "limit": 0.00, "action": "diagnostic_only"},
        ]
    )
    cap_policy.to_csv(RUNTIME / "a7ff55_family_motif_cap_policy.csv", index=False)

    required_inputs = pd.DataFrame(
        [
            {
                "artifact": "A7FF-53E label response metrics",
                "required_columns": "blueprint_id,label_family,label_horizon_h,semantic_pair,motif,decision,score_no_may",
                "status": "required_for_selector_repair_execution",
                "reason": "A7FF-54 compact selected queue lacks primary-label candidates; rerank must start from full response rows or a compact clue table with L0/L1/L3 rows",
            },
            {
                "artifact": "A7FF-53E control metrics",
                "required_columns": "blueprint_id,label_family,label_horizon_h,control_ratio_premay_max,decision",
                "status": "required_for_selector_repair_execution",
                "reason": "selector cannot select control-dominated rows",
            },
            {
                "artifact": "A7FF-53E materialization metrics",
                "required_columns": "blueprint_id,semantic_pair,motif,finite_share,nonzero_share,activity_ok",
                "status": "required_for_selector_repair_execution",
                "reason": "low-activity and diagnostic-only families must be excluded from primary replay queue",
            },
        ]
    )
    required_inputs.to_csv(RUNTIME / "a7ff55_required_inputs.csv", index=False)

    selector_policy = {
        "stage": "A7FF-55",
        "source": "A7FF-54",
        "purpose": "repair selector target before any replay preflight",
        "hard_reject": [
            "label_family == L7_ranked_future_return for replay promotion",
            "diagnostic_only_low_activity family as primary replay row",
            "control_ratio >= 0.80",
            "decision not in NUMERIC_CLUE for non-L7 rows",
            "missing primary label quota",
            "top motif share > 0.30",
            "top semantic pair share > 0.30",
        ],
        "score_inputs_allowed": [
            "non_l7_primary_label_indicator",
            "control_margin",
            "premay_split_stability",
            "one_bar_lag_survival",
            "nonoverlap_robustness",
            "cost_proxy_survival",
            "family_diversity_bonus",
            "motif_diversity_bonus",
        ],
        "score_inputs_forbidden": [
            "May pass/fail",
            "May return",
            "L7 ranked label as primary proof",
            "raw score without control margin",
            "stale selected queue from A7FF-54",
        ],
        "target_queue": {
            "selected_rows": "32 to 64",
            "primary_label_min_rows_total": 12,
            "primary_label_families_present": PRIMARY_LABELS,
            "semantic_pair_min_count": 4,
            "motif_min_count": 4,
            "L5_allowed_only_after_primary_quota": True,
            "L7_diagnostic_only": True,
        },
        "authorizes_execution": False,
        "authorizes_replay": False,
        "authorizes_search": False,
    }
    write_json(RUNTIME / "a7ff55_selector_policy.json", selector_policy)

    current_failure = {
        "a7ff54_decision": m54.get("decision"),
        "a7ff54_blockers": m54.get("blockers", []),
        "selected_primary_L0_L1_L3_count": m54.get("selected_primary_L0_L1_L3_count"),
        "selected_non_l7_count": m54.get("selected_non_l7_count"),
        "selected_l5_count": m54.get("selected_l5_count"),
        "top_selected_motif_share": m54.get("top_selected_motif_share"),
        "top_selected_family_share": m54.get("top_selected_family_share"),
    }
    write_json(RUNTIME / "a7ff55_current_failure_snapshot.json", current_failure)

    manifest = {
        "stage": "A7FF-55",
        "generated_at": now_utc(),
        "decision": "PASS_A7FF55_SELECTOR_REPAIR_CONTRACT_READY_NO_EXECUTION_AUTH",
        "source_a7ff54_decision": m54.get("decision"),
        "blockers": [],
        "warnings": [
            "contract_only_no_selector_execution",
            "A7FF-54 selected queue remains blocked for replay",
            "selector repair requires full or compact primary-label response rows",
        ],
        "executes_selector": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_a7ff55e_selector_repair_execution": False,
        "authorizes_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff55_manifest.json", manifest)

    report = f"""# CRYPTO A7FF-55 SELECTOR REPAIR CONTRACT

Generated: {manifest["generated_at"]}

## Decision

`{manifest["decision"]}`

A7FF-55 converts the A7FF-54 selected-queue failure into a selector repair contract. It does not execute selector repair, replay, search, alpha proof, shadow, paper, or live trading.

## Current Failure Snapshot

```json
{json.dumps(current_failure, indent=2, sort_keys=True)}
```

## Label Quota Policy

{md_table(label_quota, 20)}

## Family / Motif Cap Policy

{md_table(cap_policy, 20)}

## Required Inputs For Future Execution

{md_table(required_inputs, 20)}

## Current Selected Label Distribution

{md_table(selected_labels, 40)}

## Current Selected Family / Label Distribution

{md_table(selected_family_labels, 80)}

## Current Selected Motif Distribution

{md_table(selected_motifs.sort_values("selected_count", ascending=False), 40)}

## Selector Policy

```json
{json.dumps(selector_policy, indent=2, sort_keys=True)}
```

## Boundary

```text
selector repair executed: false
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
