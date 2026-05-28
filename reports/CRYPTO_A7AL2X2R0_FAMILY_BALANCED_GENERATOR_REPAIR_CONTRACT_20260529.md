# CRYPTO A7AL-2X2R0 Family-Balanced Generator Repair Contract

Generated: 2026-05-28T17:37:15Z

## Decision

```text
PASS_A7AL2X2R_GENERATOR_AND_SHARED_POOL_REPAIR_CONTRACT_READY_FOR_A7AL2X3_REVIEW
```

This is an implementation contract only. It executes no generation, no replay, no training, and no search.

## Family Quota Policy

| family_id                          | family_status         |   dry_generation_min_candidates |   dry_generation_max_share |   preflight_min_candidates |   shared_pool_min_candidates | historical_source_required   | standalone_allowed   | notes                                                                                                   |
|:-----------------------------------|:----------------------|--------------------------------:|---------------------------:|---------------------------:|-----------------------------:|:-----------------------------|:---------------------|:--------------------------------------------------------------------------------------------------------|
| F0_OI_delta_price_interaction      | allowed_contract_only |                             384 |                       0.2  |                         32 |                           32 | True                         | False                | Must use OI delta/value delta with price move; direct level gap remains weak prior.                     |
| F1_OI_basis_premium_interaction    | allowed_contract_only |                             256 |                       0.18 |                         24 |                           24 | True                         | False                | Use Binance historical premium/basis fields only; no raw OKX/Binance price comparison.                  |
| F2_OI_funding_crowding_interaction | allowed_contract_only |                             256 |                       0.18 |                         24 |                           24 | True                         | False                | Use OI change with funding level/abs/persistence; funding-only wrapper forbidden.                       |
| F3_positioning_divergence          | allowed_contract_only |                             256 |                       0.16 |                         24 |                           24 | True                         | False                | Must use Binance historical long-short/account/position fields, not J5 OKX 30d overlay.                 |
| F4_OI_taker_flow_interaction       | allowed_contract_only |                             256 |                       0.16 |                         24 |                           24 | True                         | False                | Use OI change with taker buy/sell ratio or historical taker flow fields.                                |
| F5_OI_upper_regime_interaction     | allowed_contract_only |                             256 |                       0.16 |                         24 |                           24 | True                         | False                | Use train-frozen upper-regime state fields as interaction context, not standalone rank.                 |
| F6_OI_latent_state_interaction     | allowed_contract_only |                             256 |                       0.16 |                         24 |                           24 | True                         | False                | Add explicit generator templates for listing-age latent/liquidity-tier/meme/multiplier OI interactions. |

## Historical Field Source Contract

| family_id                          | field_or_group                                                                                                        | source_contract         | field_class                    | pit_policy                | allowed_for_historical_dry_generation   |
|:-----------------------------------|:----------------------------------------------------------------------------------------------------------------------|:------------------------|:-------------------------------|:--------------------------|:----------------------------------------|
| F0_OI_delta_price_interaction      | open_interest_last                                                                                                    | binance_metrics_history | raw_source                     | timestamp_plus_1h_primary | True                                    |
| F0_OI_delta_price_interaction      | open_interest_mean                                                                                                    | binance_metrics_history | raw_source                     | timestamp_plus_1h_primary | True                                    |
| F0_OI_delta_price_interaction      | open_interest_value_last                                                                                              | binance_metrics_history | raw_source                     | timestamp_plus_1h_primary | True                                    |
| F0_OI_delta_price_interaction      | open_interest_value_mean                                                                                              | binance_metrics_history | raw_source                     | timestamp_plus_1h_primary | True                                    |
| F0_OI_delta_price_interaction      | trade_close\|mark_close\|index_close                                                                                  | binance_market_history  | raw_source                     | timestamp_plus_1h_primary | True                                    |
| F1_OI_basis_premium_interaction    | premium_close\|premium_close_bps                                                                                      | binance_premium_history | raw_source                     | timestamp_plus_1h_primary | True                                    |
| F1_OI_basis_premium_interaction    | mark_index_basis_bps\|mark_trade_basis_bps\|binance_internal_mark_index_basis_bps                                     | binance_market_history  | derived_historical             | timestamp_plus_1h_primary | True                                    |
| F2_OI_funding_crowding_interaction | funding_rate                                                                                                          | binance_funding_history | raw_source                     | timestamp_plus_1h_primary | True                                    |
| F2_OI_funding_crowding_interaction | funding_rate_abs_168h\|funding_rate_mean_168h                                                                         | a7ak_lv1_derived        | derived_rolling                | timestamp_plus_1h_primary | True                                    |
| F3_positioning_divergence          | global_long_short_account_ratio_last\|global_long_short_account_ratio_mean                                            | binance_metrics_history | raw_source                     | timestamp_plus_1h_primary | True                                    |
| F3_positioning_divergence          | top_long_short_account_ratio_last\|top_long_short_account_ratio_mean                                                  | binance_metrics_history | raw_source                     | timestamp_plus_1h_primary | True                                    |
| F3_positioning_divergence          | top_long_short_position_ratio_last\|top_long_short_position_ratio_mean                                                | binance_metrics_history | raw_source                     | timestamp_plus_1h_primary | True                                    |
| F4_OI_taker_flow_interaction       | taker_buy_sell_volume_ratio_last\|taker_buy_sell_volume_ratio_mean                                                    | binance_metrics_history | raw_source                     | timestamp_plus_1h_primary | True                                    |
| F4_OI_taker_flow_interaction       | taker_buy_quote_volume\|kline_taker_buy_quote_share                                                                   | binance_market_history  | raw_source_or_derived          | timestamp_plus_1h_primary | True                                    |
| F5_OI_upper_regime_interaction     | R4_leverage_crowding_state\|R5_basis_premium_dislocation_state\|R6_positioning_crowding_state\|R10_stress_proxy_state | a7al0g_upper_regime     | train_only_state               | timestamp_plus_1h_primary | True                                    |
| F5_OI_upper_regime_interaction     | R0_market_trend_state\|R2_market_breadth_state\|R3_liquidity_cycle_state\|R9_alt_vs_major_dispersion_state            | a7al0g_upper_regime     | train_only_state               | timestamp_plus_1h_primary | True                                    |
| F6_OI_latent_state_interaction     | raw_latent_state_id\|listing_age_days\|liquidity_rank_active_universe                                                 | a7ak_lv1_latent         | train_only_or_observable_state | timestamp_plus_1h_primary | True                                    |
| F6_OI_latent_state_interaction     | meme_contract_group\|is_multiplier_contract\|is_major\|liquidity_tier                                                 | a7ak_taxonomy           | observable_taxonomy            | timestamp_plus_1h_primary | True                                    |

## Generator Template Requirements

| family_id                          | template_pattern                                         | allowed_operator_motif               | allowed_windows                    | hard_requirement                                                      |
|:-----------------------------------|:---------------------------------------------------------|:-------------------------------------|:-----------------------------------|:----------------------------------------------------------------------|
| F0_OI_delta_price_interaction      | Mul(Sign(Delta(OI,w1)),Rank(Delta(price,w2)))            | Delta\|Mul\|Rank\|Sign\|ZScore       | 4\|8\|12\|24\|48\|72\|96\|168\|336 | must include OI delta/value delta and price move                      |
| F1_OI_basis_premium_interaction    | Mul(Sign(Delta(OI,w1)),Rank(Mean(premium_abs,w2)))       | Delta\|Mean\|Mul\|Rank\|ZScore\|Sub  | 12\|24\|48\|72\|96\|168\|336       | must include OI and premium/basis dislocation                         |
| F2_OI_funding_crowding_interaction | Mul(Sign(Delta(OI,w1)),Rank(Mean(funding_abs,w2)))       | Delta\|Mean\|Mul\|Rank\|ZScore\|Sub  | 12\|24\|48\|72\|96\|168\|336       | funding-only expression forbidden                                     |
| F3_positioning_divergence          | Sub(Rank(top_position_ratio),Rank(global_account_ratio)) | Delta\|Mean\|Rank\|Sub\|ZScore\|Mul  | 12\|24\|48\|72\|96\|168\|336       | must use at least two positioning fields or positioning x price state |
| F4_OI_taker_flow_interaction       | Mul(Sign(Delta(OI,w1)),Rank(Delta(taker_ratio,w2)))      | Delta\|Mean\|Mul\|Rank\|Sign\|ZScore | 4\|8\|12\|24\|48\|72\|96\|168      | must include OI change and taker/flow field                           |
| F5_OI_upper_regime_interaction     | Mul(Rank(Delta(OI,w1)),RegimeState(Rk))                  | Delta\|Mul\|Rank\|ZScore\|StateMask  | 24\|48\|72\|96\|168\|336           | state thresholds must be train-frozen; state alone cannot rank        |
| F6_OI_latent_state_interaction     | LatentNeutralRank(Delta(OI,w1)) or OI x latent state     | Delta\|Rank\|ZScore\|Neutralize\|Mul | 24\|48\|72\|96\|168\|336           | latent mapping frozen before validation/test                          |

## Forbidden Fallbacks

| item                                       | policy   | reason                                                             |
|:-------------------------------------------|:---------|:-------------------------------------------------------------------|
| same_direct_oi_price_rerun                 | forbid   | A7AL-2P2 direct OI-price was superseded and stress-vetoed.         |
| direct_oi_price_level_gap_standalone       | forbid   | May/control failure; weak prior only.                              |
| funding_only_wrapper                       | forbid   | Must interact with OI/positioning and pass residual/control gates. |
| basis_only_wrapper                         | forbid   | Must interact with OI/positioning and pass residual/control gates. |
| liquidity_volatility_old_family            | forbid   | Old A7M/A7O collapse family.                                       |
| a7v_activity_liquidity_self_reproduction   | forbid   | A7V family failed after source trace pass.                         |
| j5_cross_exchange_overlay_historical_proof | forbid   | 30d overlay diagnostic only; no historical proof.                  |
| raw_okx_binance_direct_price_comparison    | forbid   | Canonical contract-unit fields required.                           |
| may_in_selector_or_generation              | forbid   | May stress-only; veto/attribution only.                            |

## Authorization Boundary

```json
{
  "authorizes_a7al2x3_family_balanced_dry_generation": "READY_FOR_REVIEW_NOT_EXECUTION_AUTHORIZED",
  "authorizes_a7al2y_generation": "NOT_AUTHORIZED",
  "authorizes_alpha_proof": "NOT_AUTHORIZED",
  "authorizes_large_search": "NOT_AUTHORIZED",
  "authorizes_shadow_paper_live": "NOT_AUTHORIZED",
  "decision": "PASS_A7AL2X2R_GENERATOR_AND_SHARED_POOL_REPAIR_CONTRACT_READY_FOR_A7AL2X3_REVIEW",
  "executes_generation": false,
  "executes_replay": false,
  "executes_search": false,
  "executes_training": false,
  "requires_before_a7al2x3": [
    "implement family-balanced generator quotas",
    "replace F3 overlay-only positioning with Binance historical positioning fields",
    "add F6 latent-state templates",
    "write shared-pool ledger from family-balanced dry generation output"
  ]
}
```

## Required Next Action

```text
If approved, implement A7AL-2X3 as family-balanced dry generation smoke only.
A7AL-2X3 may generate candidates and write a shared ledger, but must not replay, search, or promote.
```
