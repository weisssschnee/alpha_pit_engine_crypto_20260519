from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
AL2I = REPO / "runtime" / "a7al2i_replay_preflight" / "a7al2i_manifest.json"
AL0R = REPO / "runtime" / "a7al0r_code_feature_regime_readiness_audit" / "a7al0r_feature_lineage_ledger.csv"
AL0F = REPO / "runtime" / "a7al0f_derived_feature_engineering_contract" / "a7al0f_feature_generation_contract.csv"
AS0 = REPO / "runtime" / "a7as0_v2_data_acceptance" / "a7as0_manifest.json"
OUT_DIR = REPO / "runtime" / "a7al2j_derived_tolerant_search_reset"
REPORT = REPO / "reports" / "CRYPTO_A7AL2J_DERIVED_TOLERANT_SEARCH_RESET_20260527.md"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    try:
        return df.head(max_rows).to_markdown(index=False)
    except Exception:
        return "```\n" + df.head(max_rows).to_string(index=False) + "\n```"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    al2i = read_json(AL2I)
    as0 = read_json(AS0)
    lineage = pd.read_csv(AL0R) if AL0R.exists() else pd.DataFrame()
    contract = pd.read_csv(AL0F) if AL0F.exists() else pd.DataFrame()

    derived = lineage[
        lineage.get("feature_class", pd.Series(dtype=str)).astype(str).str.startswith("derived")
        & lineage.get("allowed_for_search", pd.Series(dtype=bool)).astype(bool)
    ].copy() if not lineage.empty else pd.DataFrame()

    feature_roles = pd.DataFrame(
        [
            {
                "role": "first_class_derived_signal",
                "feature_classes": "derived_rolling|derived_interaction|derived_cross_section",
                "selector_policy": "allow_generation_and_selector_entry",
                "direct_rank_policy": "allowed only after matched-control dominance",
            },
            {
                "role": "regime_state_feature",
                "feature_classes": "derived_latent_state|upper_regime_state",
                "selector_policy": "allow interaction and conditioning",
                "direct_rank_policy": "not direct standalone alpha rank",
            },
            {
                "role": "overlay_diagnostic_feature",
                "feature_classes": "cross_exchange_30d_overlay",
                "selector_policy": "diagnostic only; no full-history proof",
                "direct_rank_policy": "not direct standalone alpha rank",
            },
            {
                "role": "label_or_forbidden",
                "feature_classes": "derived_label|future_return|forward_*",
                "selector_policy": "blocked",
                "direct_rank_policy": "blocked",
            },
        ]
    )

    generator_cells = pd.DataFrame(
        [
            {
                "cell": "J0_oi_derived_state",
                "inputs": "open_interest_change_24h|open_interest_zscore_168h|oi_x_price_move_24h",
                "objective": "test leverage-flow state without direct OI level rank",
                "budget_share": 0.18,
            },
            {
                "cell": "J1_vol_range_structure",
                "inputs": "range_bps|realized_vol_24h|realized_vol_168h|vol_compression",
                "objective": "test price/range derived structure beyond stale controls",
                "budget_share": 0.18,
            },
            {
                "cell": "J2_liquidity_lifecycle",
                "inputs": "trade_count|log_quote_volume_168h|liquidity_rank_active_universe|age_x_liquidity",
                "objective": "test lifecycle/liquidity interaction, not raw activity rank",
                "budget_share": 0.16,
            },
            {
                "cell": "J3_basis_funding_derived",
                "inputs": "basis_abs_168h|premium_abs_168h|funding_rate_abs_168h|funding_rate_mean_168h",
                "objective": "retest crowded dislocation as state interaction only",
                "budget_share": 0.14,
            },
            {
                "cell": "J4_upper_regime_interaction",
                "inputs": "R3_liquidity_cycle|R4_leverage_crowding|R5_basis_dislocation|R10_stress_proxy",
                "objective": "condition formulas on train-frozen upper regimes",
                "budget_share": 0.14,
            },
            {
                "cell": "J5_cross_exchange_overlay_diagnostic",
                "inputs": "okx_binance_spread|funding_spread|oi_spread|basis_spread",
                "objective": "30d diagnostic only; no proof promotion",
                "budget_share": 0.08,
            },
            {
                "cell": "J6_controls_placebo",
                "inputs": "wrong_lag|shuffle|random|same_family_placebo",
                "objective": "negative controls",
                "budget_share": 0.12,
            },
        ]
    )

    relaxed_selector = pd.DataFrame(
        [
            {"rule": "generation_cap", "value": "8000", "reason": "more tolerance for derived-field exploration"},
            {"rule": "selector_cap", "value": "768", "reason": "do not over-prune before replay"},
            {"rule": "strict_replay_cap", "value": "192", "reason": "small but broader than previous 128"},
            {"rule": "deep_audit_cap", "value": "48", "reason": "reserve only for post-control survivors"},
            {"rule": "min_selected_skeleton_count", "value": "40", "reason": "avoid formula motif collapse"},
            {"rule": "top_field_family_share_cap", "value": "0.30", "reason": "looser than proof, still prevents domination"},
            {"rule": "matched_control_required", "value": "true", "reason": "controls are not relaxed"},
            {"rule": "one_bar_lag_required", "value": "true", "reason": "native latency stress is retained"},
        ]
    )

    blockers = []
    if as0.get("decision") != "PASS_A7AS0_V2_DATA_ACCEPTANCE_READY_FOR_A7AL2G":
        blockers.append("a7as0_not_passed")
    if al2i.get("decision") not in {"HOLD_A7AL2I_NO_CLUES", "PASS_A7AL2I_REPLAY_PREFLIGHT_CLUES_FOUND_EXECUTION_HOLD"}:
        blockers.append("a7al2i_missing_or_invalid")
    if derived.empty:
        blockers.append("derived_lineage_empty")

    decision = "PASS_A7AL2J_DERIVED_TOLERANT_RESET_READY_FOR_A7AL2K" if not blockers else "HOLD_A7AL2J_DERIVED_RESET_BLOCKED"
    manifest = {
        "generated_at": utc_now(),
        "decision": decision,
        "input_a7al2i_decision": al2i.get("decision"),
        "input_a7as0_decision": as0.get("decision"),
        "derived_searchable_field_count": int(len(derived)),
        "generator_cells": int(len(generator_cells)),
        "blockers": blockers,
        "authorizes_a7al2k_generator_smoke": not blockers,
        "authorizes_formula_search_execution": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "policy": "derived fields are first-class if lineage/PIT/control requirements are explicit; controls remain mandatory",
    }

    feature_roles.to_csv(OUT_DIR / "a7al2j_feature_roles.csv", index=False)
    generator_cells.to_csv(OUT_DIR / "a7al2j_generator_cells.csv", index=False)
    relaxed_selector.to_csv(OUT_DIR / "a7al2j_relaxed_selector_policy.csv", index=False)
    derived.head(300).to_csv(OUT_DIR / "a7al2j_searchable_derived_field_sample.csv", index=False)
    contract.to_csv(OUT_DIR / "a7al2j_input_derived_contract.csv", index=False)
    write_json(OUT_DIR / "a7al2j_manifest.json", manifest)

    report = f"""# CRYPTO A7AL-2J Derived-Tolerant Search Reset

Generated: {manifest["generated_at"]}

## Decision

```text
{decision}
```

This stage responds to A7AL-2I: the old 15-candidate selector pool did not produce clean clues, so the next generator must treat derived fields as first-class search inputs. This is still a contract/reset stage, not formula search execution.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Feature Roles

{md_table(feature_roles, 80)}

## Generator Cells

{md_table(generator_cells, 80)}

## Relaxed Selector Policy

{md_table(relaxed_selector, 80)}

## Boundary

```text
Relaxed:
  derived fields can enter generation/selector more freely.

Not relaxed:
  matched-control dominance
  one-bar-lag stress
  label/PIT isolation
  no alpha proof / shadow / paper / live
```
"""
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
