from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "runtime" / "a7al2x2r_family_balanced_repair_contract"
REPORT_R0 = ROOT / "reports" / "CRYPTO_A7AL2X2R0_FAMILY_BALANCED_GENERATOR_REPAIR_CONTRACT_20260529.md"
REPORT_R1 = ROOT / "reports" / "CRYPTO_A7AL2X2R1_SHARED_POOL_REBUILD_CONTRACT_20260529.md"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT_R0.parent.mkdir(parents=True, exist_ok=True)

    generated_at = now_utc()

    family_quota = pd.DataFrame(
        [
            {
                "family_id": "F0_OI_delta_price_interaction",
                "family_status": "allowed_contract_only",
                "dry_generation_min_candidates": 384,
                "dry_generation_max_share": 0.20,
                "preflight_min_candidates": 32,
                "shared_pool_min_candidates": 32,
                "historical_source_required": True,
                "standalone_allowed": False,
                "notes": "Must use OI delta/value delta with price move; direct level gap remains weak prior.",
            },
            {
                "family_id": "F1_OI_basis_premium_interaction",
                "family_status": "allowed_contract_only",
                "dry_generation_min_candidates": 256,
                "dry_generation_max_share": 0.18,
                "preflight_min_candidates": 24,
                "shared_pool_min_candidates": 24,
                "historical_source_required": True,
                "standalone_allowed": False,
                "notes": "Use Binance historical premium/basis fields only; no raw OKX/Binance price comparison.",
            },
            {
                "family_id": "F2_OI_funding_crowding_interaction",
                "family_status": "allowed_contract_only",
                "dry_generation_min_candidates": 256,
                "dry_generation_max_share": 0.18,
                "preflight_min_candidates": 24,
                "shared_pool_min_candidates": 24,
                "historical_source_required": True,
                "standalone_allowed": False,
                "notes": "Use OI change with funding level/abs/persistence; funding-only wrapper forbidden.",
            },
            {
                "family_id": "F3_positioning_divergence",
                "family_status": "allowed_contract_only",
                "dry_generation_min_candidates": 256,
                "dry_generation_max_share": 0.16,
                "preflight_min_candidates": 24,
                "shared_pool_min_candidates": 24,
                "historical_source_required": True,
                "standalone_allowed": False,
                "notes": "Must use Binance historical long-short/account/position fields, not J5 OKX 30d overlay.",
            },
            {
                "family_id": "F4_OI_taker_flow_interaction",
                "family_status": "allowed_contract_only",
                "dry_generation_min_candidates": 256,
                "dry_generation_max_share": 0.16,
                "preflight_min_candidates": 24,
                "shared_pool_min_candidates": 24,
                "historical_source_required": True,
                "standalone_allowed": False,
                "notes": "Use OI change with taker buy/sell ratio or historical taker flow fields.",
            },
            {
                "family_id": "F5_OI_upper_regime_interaction",
                "family_status": "allowed_contract_only",
                "dry_generation_min_candidates": 256,
                "dry_generation_max_share": 0.16,
                "preflight_min_candidates": 24,
                "shared_pool_min_candidates": 24,
                "historical_source_required": True,
                "standalone_allowed": False,
                "notes": "Use train-frozen upper-regime state fields as interaction context, not standalone rank.",
            },
            {
                "family_id": "F6_OI_latent_state_interaction",
                "family_status": "allowed_contract_only",
                "dry_generation_min_candidates": 256,
                "dry_generation_max_share": 0.16,
                "preflight_min_candidates": 24,
                "shared_pool_min_candidates": 24,
                "historical_source_required": True,
                "standalone_allowed": False,
                "notes": "Add explicit generator templates for listing-age latent/liquidity-tier/meme/multiplier OI interactions.",
            },
        ]
    )

    field_contract = pd.DataFrame(
        [
            ("F0_OI_delta_price_interaction", "open_interest_last", "binance_metrics_history", "raw_source", "timestamp_plus_1h_primary", True),
            ("F0_OI_delta_price_interaction", "open_interest_mean", "binance_metrics_history", "raw_source", "timestamp_plus_1h_primary", True),
            ("F0_OI_delta_price_interaction", "open_interest_value_last", "binance_metrics_history", "raw_source", "timestamp_plus_1h_primary", True),
            ("F0_OI_delta_price_interaction", "open_interest_value_mean", "binance_metrics_history", "raw_source", "timestamp_plus_1h_primary", True),
            ("F0_OI_delta_price_interaction", "trade_close|mark_close|index_close", "binance_market_history", "raw_source", "timestamp_plus_1h_primary", True),
            ("F1_OI_basis_premium_interaction", "premium_close|premium_close_bps", "binance_premium_history", "raw_source", "timestamp_plus_1h_primary", True),
            ("F1_OI_basis_premium_interaction", "mark_index_basis_bps|mark_trade_basis_bps|binance_internal_mark_index_basis_bps", "binance_market_history", "derived_historical", "timestamp_plus_1h_primary", True),
            ("F2_OI_funding_crowding_interaction", "funding_rate", "binance_funding_history", "raw_source", "timestamp_plus_1h_primary", True),
            ("F2_OI_funding_crowding_interaction", "funding_rate_abs_168h|funding_rate_mean_168h", "a7ak_lv1_derived", "derived_rolling", "timestamp_plus_1h_primary", True),
            ("F3_positioning_divergence", "global_long_short_account_ratio_last|global_long_short_account_ratio_mean", "binance_metrics_history", "raw_source", "timestamp_plus_1h_primary", True),
            ("F3_positioning_divergence", "top_long_short_account_ratio_last|top_long_short_account_ratio_mean", "binance_metrics_history", "raw_source", "timestamp_plus_1h_primary", True),
            ("F3_positioning_divergence", "top_long_short_position_ratio_last|top_long_short_position_ratio_mean", "binance_metrics_history", "raw_source", "timestamp_plus_1h_primary", True),
            ("F4_OI_taker_flow_interaction", "taker_buy_sell_volume_ratio_last|taker_buy_sell_volume_ratio_mean", "binance_metrics_history", "raw_source", "timestamp_plus_1h_primary", True),
            ("F4_OI_taker_flow_interaction", "taker_buy_quote_volume|kline_taker_buy_quote_share", "binance_market_history", "raw_source_or_derived", "timestamp_plus_1h_primary", True),
            ("F5_OI_upper_regime_interaction", "R4_leverage_crowding_state|R5_basis_premium_dislocation_state|R6_positioning_crowding_state|R10_stress_proxy_state", "a7al0g_upper_regime", "train_only_state", "timestamp_plus_1h_primary", True),
            ("F5_OI_upper_regime_interaction", "R0_market_trend_state|R2_market_breadth_state|R3_liquidity_cycle_state|R9_alt_vs_major_dispersion_state", "a7al0g_upper_regime", "train_only_state", "timestamp_plus_1h_primary", True),
            ("F6_OI_latent_state_interaction", "raw_latent_state_id|listing_age_days|liquidity_rank_active_universe", "a7ak_lv1_latent", "train_only_or_observable_state", "timestamp_plus_1h_primary", True),
            ("F6_OI_latent_state_interaction", "meme_contract_group|is_multiplier_contract|is_major|liquidity_tier", "a7ak_taxonomy", "observable_taxonomy", "timestamp_plus_1h_primary", True),
        ],
        columns=["family_id", "field_or_group", "source_contract", "field_class", "pit_policy", "allowed_for_historical_dry_generation"],
    )

    template_requirements = pd.DataFrame(
        [
            ("F0_OI_delta_price_interaction", "Mul(Sign(Delta(OI,w1)),Rank(Delta(price,w2)))", "Delta|Mul|Rank|Sign|ZScore", "4|8|12|24|48|72|96|168|336", "must include OI delta/value delta and price move"),
            ("F1_OI_basis_premium_interaction", "Mul(Sign(Delta(OI,w1)),Rank(Mean(premium_abs,w2)))", "Delta|Mean|Mul|Rank|ZScore|Sub", "12|24|48|72|96|168|336", "must include OI and premium/basis dislocation"),
            ("F2_OI_funding_crowding_interaction", "Mul(Sign(Delta(OI,w1)),Rank(Mean(funding_abs,w2)))", "Delta|Mean|Mul|Rank|ZScore|Sub", "12|24|48|72|96|168|336", "funding-only expression forbidden"),
            ("F3_positioning_divergence", "Sub(Rank(top_position_ratio),Rank(global_account_ratio))", "Delta|Mean|Rank|Sub|ZScore|Mul", "12|24|48|72|96|168|336", "must use at least two positioning fields or positioning x price state"),
            ("F4_OI_taker_flow_interaction", "Mul(Sign(Delta(OI,w1)),Rank(Delta(taker_ratio,w2)))", "Delta|Mean|Mul|Rank|Sign|ZScore", "4|8|12|24|48|72|96|168", "must include OI change and taker/flow field"),
            ("F5_OI_upper_regime_interaction", "Mul(Rank(Delta(OI,w1)),RegimeState(Rk))", "Delta|Mul|Rank|ZScore|StateMask", "24|48|72|96|168|336", "state thresholds must be train-frozen; state alone cannot rank"),
            ("F6_OI_latent_state_interaction", "LatentNeutralRank(Delta(OI,w1)) or OI x latent state", "Delta|Rank|ZScore|Neutralize|Mul", "24|48|72|96|168|336", "latent mapping frozen before validation/test"),
        ],
        columns=["family_id", "template_pattern", "allowed_operator_motif", "allowed_windows", "hard_requirement"],
    )

    forbidden = pd.DataFrame(
        [
            ("same_direct_oi_price_rerun", "forbid", "A7AL-2P2 direct OI-price was superseded and stress-vetoed."),
            ("direct_oi_price_level_gap_standalone", "forbid", "May/control failure; weak prior only."),
            ("funding_only_wrapper", "forbid", "Must interact with OI/positioning and pass residual/control gates."),
            ("basis_only_wrapper", "forbid", "Must interact with OI/positioning and pass residual/control gates."),
            ("liquidity_volatility_old_family", "forbid", "Old A7M/A7O collapse family."),
            ("a7v_activity_liquidity_self_reproduction", "forbid", "A7V family failed after source trace pass."),
            ("j5_cross_exchange_overlay_historical_proof", "forbid", "30d overlay diagnostic only; no historical proof."),
            ("raw_okx_binance_direct_price_comparison", "forbid", "Canonical contract-unit fields required."),
            ("may_in_selector_or_generation", "forbid", "May stress-only; veto/attribution only."),
        ],
        columns=["item", "policy", "reason"],
    )

    ledger_schema = pd.DataFrame(
        [
            ("candidate_id", "string", "stable unique id"),
            ("expression", "string", "formula expression"),
            ("objective_family", "enum:F0-F6", "A7AL-2X objective family"),
            ("source_stage", "string", "generator/preflight/shared-pool source"),
            ("field_families", "string", "pipe-delimited field families"),
            ("fields", "string", "pipe-delimited concrete fields"),
            ("operator_signature", "string", "operator motif"),
            ("window_signature", "string", "lookback windows"),
            ("skeleton_key", "string", "structure dedup key"),
            ("production_key", "string", "family/field/window key"),
            ("historical_source_ok", "bool", "no overlay-only historical proof field"),
            ("field_lineage_ok", "bool", "all fields in lineage ledger"),
            ("pit_policy_ok", "bool", "field-native latency valid"),
            ("negative_control_attached", "bool", "matched controls available before replay"),
            ("selected_for_family_balanced_preflight", "bool", "quota-based preflight selection"),
            ("preflight_decision", "string", "empty before replay"),
            ("shared_pool_stage", "string", "current stage"),
        ],
        columns=["column_name", "dtype", "description"],
    )

    shared_pool_policy = pd.DataFrame(
        [
            ("source_of_truth", "A7AL-2X shared candidate ledger only; no direct single-stage CSV reads"),
            ("family_min_coverage", "F0-F6 must each have shared-pool candidates if generated historically"),
            ("quota_selection", "family-balanced first, then skeleton/production diversity"),
            ("signal_vector_cap", "selected top signal-vector cluster share <= 0.35; max pairwise corr <= 0.80"),
            ("skeleton_cap", "same skeleton share <= 0.25"),
            ("production_cap", "same production key share <= 0.20"),
            ("control_gate", "control_ratio >= 1.0 hard reject; 0.80-1.0 warning"),
            ("may_policy", "May cannot enter generation/selector/ranking/mutation; veto/attribution only"),
        ],
        columns=["policy_key", "policy_value"],
    )

    authorization = {
        "decision": "PASS_A7AL2X2R_GENERATOR_AND_SHARED_POOL_REPAIR_CONTRACT_READY_FOR_A7AL2X3_REVIEW",
        "executes_generation": False,
        "executes_replay": False,
        "executes_search": False,
        "executes_training": False,
        "authorizes_a7al2x3_family_balanced_dry_generation": "READY_FOR_REVIEW_NOT_EXECUTION_AUTHORIZED",
        "authorizes_a7al2y_generation": "NOT_AUTHORIZED",
        "authorizes_large_search": "NOT_AUTHORIZED",
        "authorizes_alpha_proof": "NOT_AUTHORIZED",
        "authorizes_shadow_paper_live": "NOT_AUTHORIZED",
        "requires_before_a7al2x3": [
            "implement family-balanced generator quotas",
            "replace F3 overlay-only positioning with Binance historical positioning fields",
            "add F6 latent-state templates",
            "write shared-pool ledger from family-balanced dry generation output",
        ],
    }

    manifest = {
        "decision": authorization["decision"],
        "generated_at": generated_at,
        "executes_generation": False,
        "executes_replay": False,
        "executes_search": False,
        "executes_training": False,
        "family_count": int(family_quota.shape[0]),
        "field_contract_rows": int(field_contract.shape[0]),
        "forbidden_items": int(forbidden.shape[0]),
        "authorizes_a7al2x3_family_balanced_dry_generation": False,
        "authorizes_a7al2y_generation": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }

    family_quota.to_csv(RUNTIME / "a7al2x2r_family_min_quota_policy.csv", index=False)
    field_contract.to_csv(RUNTIME / "a7al2x2r_historical_field_source_contract.csv", index=False)
    template_requirements.to_csv(RUNTIME / "a7al2x2r_generator_template_requirements.csv", index=False)
    forbidden.to_csv(RUNTIME / "a7al2x2r_forbidden_fallbacks.csv", index=False)
    ledger_schema.to_csv(RUNTIME / "a7al2x2r_shared_pool_ledger_schema.csv", index=False)
    shared_pool_policy.to_csv(RUNTIME / "a7al2x2r_shared_pool_rebuild_policy.csv", index=False)
    write_json(RUNTIME / "a7al2x2r_authorization_matrix.json", authorization)
    write_json(RUNTIME / "a7al2x2r_manifest.json", manifest)

    r0 = f"""# CRYPTO A7AL-2X2R0 Family-Balanced Generator Repair Contract

Generated: {generated_at}

## Decision

```text
{authorization["decision"]}
```

This is an implementation contract only. It executes no generation, no replay, no training, and no search.

## Family Quota Policy

{md_table(family_quota)}

## Historical Field Source Contract

{md_table(field_contract)}

## Generator Template Requirements

{md_table(template_requirements)}

## Forbidden Fallbacks

{md_table(forbidden)}

## Authorization Boundary

```json
{json.dumps(authorization, indent=2, sort_keys=True)}
```

## Required Next Action

```text
If approved, implement A7AL-2X3 as family-balanced dry generation smoke only.
A7AL-2X3 may generate candidates and write a shared ledger, but must not replay, search, or promote.
```
"""

    r1 = f"""# CRYPTO A7AL-2X2R1 Shared-Pool Rebuild Contract

Generated: {generated_at}

## Decision

```text
{authorization["decision"]}
```

This contract fixes the A7AR-7 source-of-truth gap: the next shared pool must be family-balanced and must include F0-F6 coverage where historical fields exist.

## Shared-Pool Ledger Schema

{md_table(ledger_schema)}

## Shared-Pool Rebuild Policy

{md_table(shared_pool_policy)}

## Source-Of-Truth Rules

```text
1. A7AL-2X3 output ledger becomes the only source for any later dry rerank.
2. A7AL-2P2/A7AL-2Q local OI-price pools remain superseded diagnostic artifacts.
3. No direct reads from stale A7AL-2L/P1/P1R/P2 single-stage artifacts are allowed.
4. J5 overlay-only fields cannot enter historical replay/proof paths.
5. May remains post-selection veto / attribution only.
```

## Authorization Boundary

```json
{json.dumps(authorization, indent=2, sort_keys=True)}
```
"""

    REPORT_R0.write_text(r0, encoding="utf-8")
    REPORT_R1.write_text(r1, encoding="utf-8")


if __name__ == "__main__":
    main()
