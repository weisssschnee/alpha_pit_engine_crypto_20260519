from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff32_family_diversification_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FF32_FAMILY_DIVERSIFICATION_CONTRACT_20260530.md"

A7FF31 = REPO / "runtime" / "a7ff31_portfolio_forensic" / "a7ff31_manifest.json"
A7FF31_REVIEW = REPO / "runtime" / "a7ff31_portfolio_forensic" / "a7ff31_candidate_factor_review.csv"
A7FF24R3 = REPO / "runtime" / "a7ff24r3_dense_materializer_preflight" / "a7ff24r3_manifest.json"


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

    f31 = read_json(A7FF31)
    f24r3 = read_json(A7FF24R3)
    if not f31.get("authorizes_a7ff32_family_diversification_contract"):
        raise SystemExit(f"A7FF-31 does not authorize A7FF-32: {f31.get('decision')}")

    review = pd.read_csv(A7FF31_REVIEW) if A7FF31_REVIEW.exists() else pd.DataFrame()
    current_family_summary = (
        review.groupby(["feature_family", "nearest_known_family"], dropna=False)
        .size()
        .reset_index(name="held_candidate_count")
        .sort_values("held_candidate_count", ascending=False)
        if not review.empty
        else pd.DataFrame(columns=["feature_family", "nearest_known_family", "held_candidate_count"])
    )
    current_family_summary.to_csv(RUNTIME / "a7ff32_current_concentrated_family_summary.csv", index=False)

    allowed = pd.DataFrame(
        [
            {
                "family_id": "D0_basis_premium_reference",
                "root_family": "basis_premium_like",
                "role": "reference_family_only",
                "min_generation_share": 0.05,
                "max_generation_share": 0.25,
                "max_selected_share": 0.20,
                "notes": "Existing clue root; cannot dominate next pool.",
            },
            {
                "family_id": "D1_open_interest_positioning",
                "root_family": "open_interest_like|positioning_like",
                "role": "primary_diversification_target",
                "min_generation_share": 0.15,
                "max_generation_share": 0.35,
                "max_selected_share": 0.30,
                "notes": "OI/positioning interaction, not direct OI-price rerun.",
            },
            {
                "family_id": "D2_taker_flow_leverage",
                "root_family": "taker_flow_like|open_interest_like",
                "role": "primary_diversification_target",
                "min_generation_share": 0.10,
                "max_generation_share": 0.25,
                "max_selected_share": 0.25,
                "notes": "Aggressive taker flow under leverage expansion/contraction.",
            },
            {
                "family_id": "D3_liquidity_volatility_state",
                "root_family": "liquidity_like|volatility_like",
                "role": "primary_diversification_target",
                "min_generation_share": 0.10,
                "max_generation_share": 0.25,
                "max_selected_share": 0.25,
                "notes": "Liquidity/volatility state with strict control dominance gate.",
            },
            {
                "family_id": "D4_regime_relative_value",
                "root_family": "regime_state|price_return_like",
                "role": "primary_diversification_target",
                "min_generation_share": 0.10,
                "max_generation_share": 0.25,
                "max_selected_share": 0.25,
                "notes": "Upper-regime conditioned relative-value, not direct regime-as-alpha.",
            },
            {
                "family_id": "D5_funding_dense_state",
                "root_family": "funding_like|basis_premium_like",
                "role": "dense_materializer_target",
                "min_generation_share": 0.10,
                "max_generation_share": 0.25,
                "max_selected_share": 0.25,
                "notes": "Only dense funding fields; raw funding_rate tail is blocked.",
            },
            {
                "family_id": "D6_listing_latent_lifecycle",
                "root_family": "listing_age_like|latent_state",
                "role": "diagnostic_to_signal_bridge",
                "min_generation_share": 0.05,
                "max_generation_share": 0.15,
                "max_selected_share": 0.15,
                "notes": "Age/latent lifecycle interactions; must survive neutralization.",
            },
        ]
    )
    allowed.to_csv(RUNTIME / "a7ff32_allowed_family_quota.csv", index=False)

    blocked = pd.DataFrame(
        [
            {"pattern": "basis_premium_root_only_pool", "rule": "basis_premium_like selected share > 0.20 blocks progression"},
            {"pattern": "raw_funding_rate_tail", "rule": "raw funding_rate cannot be used in repaired tail; use dense funding state fields"},
            {"pattern": "same_skeleton_cluster", "rule": "single skeleton selected share > 0.15 blocks progression"},
            {"pattern": "SafeDiv_unbounded", "rule": "SafeDiv requires denominator guard and winsor/clip audit"},
            {"pattern": "L7_ranked_label_only", "rule": "ranked-return-only evidence remains diagnostic-only"},
            {"pattern": "control_dominated", "rule": "control_ratio >= 1.00 rejects; 0.80-1.00 warns"},
            {"pattern": "May_in_selector", "rule": "May cannot enter generation, selector, ranking, weight update, or mutation"},
            {"pattern": "direct_OI_price_rerun", "rule": "direct OI-price remains weak prior; no same-objective rerun"},
        ]
    )
    blocked.to_csv(RUNTIME / "a7ff32_blocked_patterns.csv", index=False)

    scale_policy = {
        "stage": "A7FF-33",
        "type": "family_diversified_dry_generation_plan",
        "generated_blueprint_target": 24000,
        "materialization_queue_target": 6000,
        "company_wave_queue_target": 3600,
        "company_shard_count": 18,
        "min_non_basis_generation_share": 0.65,
        "min_non_basis_company_wave_share": 0.65,
        "min_root_family_count": 6,
        "min_motif_count": 10,
        "executes_numeric_probe": False,
        "executes_replay": False,
        "executes_search": False,
        "notes": "Scale is deliberately larger than A7FF-24R, but it is still dry generation / asset construction only.",
    }
    selector_policy = {
        "max_selected_basis_premium_root_share": 0.20,
        "max_selected_single_root_family_share": 0.30,
        "max_selected_single_skeleton_share": 0.15,
        "max_selected_single_production_key_share": 0.10,
        "min_selected_root_family_count": 5,
        "min_selected_signal_vector_cluster_count": 8,
        "must_use_response_backed_field_roles": True,
        "must_log_field_roles": True,
        "must_attach_negative_controls": True,
        "must_not_use_may": True,
    }
    write_json(RUNTIME / "a7ff32_generation_scale_policy.json", scale_policy)
    write_json(RUNTIME / "a7ff32_selector_diversity_policy.json", selector_policy)

    blockers: list[str] = []
    warnings: list[str] = []
    if f31.get("decision", "").startswith("HOLD_"):
        warnings.append("source_A7FF31_is_hold_by_design")
    if f24r3 and not str(f24r3.get("decision", "")).startswith("PASS_"):
        warnings.append("dense_materializer_preflight_not_passed")
    if not review.empty and review["nearest_known_family"].astype(str).eq("basis_premium_root").mean() >= 1.0:
        warnings.append("current_clue_pool_all_basis_premium_root")

    decision = "PASS_A7FF32_FAMILY_DIVERSIFICATION_CONTRACT_READY_FOR_A7FF33_DRY_GENERATION_NO_SEARCH_AUTH" if not blockers else "HOLD_A7FF32_CONTRACT_BLOCKED"
    manifest = {
        "stage": "A7FF-32",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "warnings": warnings,
        "source_a7ff31_decision": f31.get("decision"),
        "source_a7ff24r3_decision": f24r3.get("decision"),
        "current_candidate_count": int(f31.get("candidate_count", 0) or 0),
        "current_max_pairwise_corr_abs": f31.get("max_pairwise_corr_abs"),
        "current_top_symbol_contribution_share": f31.get("top_symbol_contribution_share"),
        "allowed_family_count": int(len(allowed)),
        "blocked_pattern_count": int(len(blocked)),
        "executes_generation": False,
        "executes_numeric_probe": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_a7ff33_family_diversified_dry_generation": not blockers,
        "authorizes_numeric_probe": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff32_manifest.json", manifest)
    write_json(RUNTIME / "a7ff32_decision_record.json", manifest)
    write_json(
        RUNTIME / "a7ff32_authorization_matrix.json",
        {
            "A7FF-33_family_diversified_dry_generation": {"authorized": not blockers, "execution_type": "dry_generation_only"},
            "numeric_probe": {"authorized": False},
            "formula_search": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof": {"authorized": False},
            "shadow_paper_live": {"authorized": False},
        },
    )

    report = f"""# CRYPTO A7FF-32 FAMILY DIVERSIFICATION CONTRACT

Generated: {manifest["generated_at"]}

## Decision

`{decision}`

A7FF-32 responds to A7FF-31: the portfolio clue is not single-symbol or single-month dominated, but it is structurally concentrated in the basis/premium root with very high pairwise correlation. This contract allows a larger dry-generation asset build only if the next pool is root-family diversified.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Current Concentrated Families

{md_table(current_family_summary)}

## Allowed Family Quotas

{md_table(allowed)}

## Blocked Patterns

{md_table(blocked)}

## Generation Scale Policy

```json
{json.dumps(scale_policy, indent=2, sort_keys=True)}
```

## Selector Diversity Policy

```json
{json.dumps(selector_policy, indent=2, sort_keys=True)}
```

## Boundary

```text
dry generation authorized: A7FF-33 only
numeric probe authorized: false
replay authorized: false
search authorized: false
alpha proof / shadow / paper / live: false
May usage: forbidden in generation, selector, ranking, mutation, and weight update
```
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
