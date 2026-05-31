from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff55r_selector_field_family_repair_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FF55R_SELECTOR_FIELD_FAMILY_REPAIR_CONTRACT_20260531.md"
A7FF55F = REPO / "runtime" / "a7ff55f_full_primary_input_rebuild" / "a7ff55f_manifest.json"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


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
    m55f = read_json(A7FF55F)
    if m55f.get("decision") != "HOLD_A7FF55F_FULL_PRIMARY_SELECTOR_INPUT_REPAIR_REQUIRED":
        raise SystemExit(f"A7FF-55F is not in the expected repair-required state: {m55f.get('decision')}")

    family = read_csv(REPO / "runtime" / "a7ff55f_full_primary_input_rebuild" / "a7ff55f_selected_family_summary.csv")
    motif = read_csv(REPO / "runtime" / "a7ff55f_full_primary_input_rebuild" / "a7ff55f_selected_motif_summary.csv")
    candidates = read_csv(REPO / "runtime" / "a7ff55f_full_primary_input_rebuild" / "a7ff55f_candidate_family_summary.csv")

    selected_rows = int(m55f.get("selected_rows", 0))
    family["selected_share"] = pd.to_numeric(family.get("selected_count", 0), errors="coerce") / max(1, selected_rows) if not family.empty else []
    motif["selected_share"] = pd.to_numeric(motif.get("selected_count", 0), errors="coerce") / max(1, selected_rows) if not motif.empty else []
    family.to_csv(RUNTIME / "a7ff55r_prior_selected_family_exposure.csv", index=False)
    motif.to_csv(RUNTIME / "a7ff55r_prior_selected_motif_exposure.csv", index=False)

    repair_actions = pd.DataFrame(
        [
            {
                "repair_id": "R0_primary_label_balance_keep",
                "target": "label_family",
                "rule": "keep L0/L1/L3 minimum 4 rows each; L5/L7 remain excluded from alpha-selector queue",
                "reason": "A7FF55F solved label absence; retain this constraint",
            },
            {
                "repair_id": "R1_family_anti_concentration",
                "target": "semantic_pair",
                "rule": "hard cap per selected semantic_pair <= 0.25 until at least 5 families are selected",
                "reason": "A7FF55F top semantic pair share was 0.40",
            },
            {
                "repair_id": "R2_motif_anti_concentration",
                "target": "motif",
                "rule": "hard cap spread_rank <= 0.25 and require at least 5 motifs before any replay-preflight contract",
                "reason": "A7FF55F spread_rank share was 0.5333",
            },
            {
                "repair_id": "R3_underrepresented_family_boost",
                "target": "input_generation",
                "rule": "supplemental primary-label inputs must over-sample open_interest, positioning, liquidity, volatility, and taker-flow families",
                "reason": "A7FF55F had only 1-3 selected rows in those families",
            },
            {
                "repair_id": "R4_duplicate_economic_core_downrank",
                "target": "selector_score",
                "rule": "down-rank repeated price_return interactions after each family reaches 4 rows",
                "reason": "current selected queue is price-return-core dominated",
            },
            {
                "repair_id": "R5_control_margin_preserve",
                "target": "hard_gate",
                "rule": "keep control_ratio_premay_max < 0.80 and wrong-lag/shuffle weaker than original",
                "reason": "do not solve diversity by admitting control-like rows",
            },
        ]
    )
    supplemental_quota = pd.DataFrame(
        [
            {"field_family": "open_interest_like", "min_primary_candidates": 12, "preferred_labels": "L0,L1,L3", "allowed_role": "ordinary_or_mixed_alpha_only"},
            {"field_family": "positioning_like", "min_primary_candidates": 12, "preferred_labels": "L0,L1,L3", "allowed_role": "ordinary_or_mixed_alpha_only"},
            {"field_family": "liquidity_like", "min_primary_candidates": 10, "preferred_labels": "L0,L1,L3", "allowed_role": "ordinary_or_mixed_alpha_only"},
            {"field_family": "volatility_like", "min_primary_candidates": 10, "preferred_labels": "L0,L1,L3", "allowed_role": "ordinary_or_mixed_alpha_only"},
            {"field_family": "taker_flow_like", "min_primary_candidates": 8, "preferred_labels": "L0,L1,L3", "allowed_role": "ordinary_or_mixed_alpha_only"},
            {"field_family": "basis_premium_like", "min_primary_candidates": 0, "preferred_labels": "L0,L1,L3", "allowed_role": "cap_only_no_boost"},
            {"field_family": "regime_state", "min_primary_candidates": 0, "preferred_labels": "L0,L1,L3", "allowed_role": "cap_only_no_boost"},
        ]
    )
    next_runner_contract = {
        "stage": "A7FF-55R1",
        "description": "family-diverse supplemental primary-label input generation and dry selector rerun",
        "executes_replay": False,
        "executes_search": False,
        "max_new_primary_response_rows": 12000,
        "required_labels": ["L0_raw_forward_return", "L1_cross_sectional_relative_return", "L3_liquidity_tier_relative_return"],
        "blocked_labels": ["L7_ranked_future_return"],
        "family_caps": {
            "selected_semantic_pair_max_share": 0.25,
            "selected_motif_max_share": 0.25,
            "selected_label_max_share": 0.35,
        },
        "minimums": {
            "selected_rows": 24,
            "selected_semantic_pairs": 5,
            "selected_motifs": 5,
            "primary_label_rows_each": 4,
        },
    }
    repair_actions.to_csv(RUNTIME / "a7ff55r_repair_actions.csv", index=False)
    supplemental_quota.to_csv(RUNTIME / "a7ff55r_supplemental_family_quota.csv", index=False)
    write_json(RUNTIME / "a7ff55r_next_runner_contract.json", next_runner_contract)

    manifest = {
        "stage": "A7FF-55R",
        "generated_at": now_utc(),
        "decision": "PASS_A7FF55R_SELECTOR_FIELD_FAMILY_REPAIR_CONTRACT_READY_NO_EXECUTION_AUTH",
        "source_stage": "A7FF-55F",
        "source_decision": m55f.get("decision"),
        "source_blockers": m55f.get("blockers", []),
        "repair_action_count": int(len(repair_actions)),
        "supplemental_family_quota_rows": int(len(supplemental_quota)),
        "authorizes_next_execution": False,
        "authorizes_next_contract": True,
        "next_allowed": "A7FF-55R1 family-diverse supplemental primary-label input generation, if explicitly executed",
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff55r_manifest.json", manifest)

    report = f"""# CRYPTO A7FF-55R SELECTOR FIELD-FAMILY REPAIR CONTRACT

Generated: {manifest["generated_at"]}

## Decision

`{manifest["decision"]}`

A7FF-55R converts the A7FF-55F failure into a concrete repair contract. It does not run replay or search.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Prior Selected Family Exposure

{md_table(family, 40)}

## Prior Selected Motif Exposure

{md_table(motif, 40)}

## Repair Actions

{md_table(repair_actions, 40)}

## Supplemental Family Quota

{md_table(supplemental_quota, 40)}

## Candidate Family Evidence

{md_table(candidates.sort_values("candidate_rows", ascending=False), 80)}

## Boundary

```text
contract written: true
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
