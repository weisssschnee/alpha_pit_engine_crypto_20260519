# CRYPTO A7AL-2X3 Family-Balanced Dry Generation Smoke

Generated: 2026-05-29T00:09:43Z

## Decision

```text
PASS_A7AL2X3_FAMILY_BALANCED_DRY_GENERATION_LEDGER_READY_FOR_PREFLIGHT_REVIEW
```

This stage executes dry candidate generation and shared-ledger construction only. It performs no replay, no selector scoring, no training, and no alpha proof.

## Manifest

```json
{
  "authorizes_a7al2y_generation": false,
  "authorizes_alpha_proof": false,
  "authorizes_large_search": false,
  "authorizes_replay": false,
  "authorizes_shadow_paper_live": false,
  "base_panel_schema_fields": 54,
  "blockers": [],
  "decision": "PASS_A7AL2X3_FAMILY_BALANCED_DRY_GENERATION_LEDGER_READY_FOR_PREFLIGHT_REVIEW",
  "executes_generation": true,
  "executes_replay": false,
  "executes_search": false,
  "executes_training": false,
  "family_count": 7,
  "generated_at": "2026-05-29T00:09:43Z",
  "generated_count": 1920,
  "selected_for_future_preflight_count": 176,
  "static_valid_count": 1920
}
```

## Family Quota Audit

| objective_family                   |   generated_count |   static_valid_count |   selected_for_preflight_count |   unique_skeleton_count |   unique_production_count | family_id                          |   dry_generation_min_candidates |   dry_generation_max_share |   preflight_min_candidates |   generated_share | quota_pass   |
|:-----------------------------------|------------------:|---------------------:|-------------------------------:|------------------------:|--------------------------:|:-----------------------------------|--------------------------------:|---------------------------:|---------------------------:|------------------:|:-------------|
| F0_OI_delta_price_interaction      |               384 |                  384 |                             32 |                       7 |                       216 | F0_OI_delta_price_interaction      |                             384 |                       0.2  |                         32 |          0.2      | True         |
| F1_OI_basis_premium_interaction    |               256 |                  256 |                             24 |                       6 |                       154 | F1_OI_basis_premium_interaction    |                             256 |                       0.18 |                         24 |          0.133333 | True         |
| F2_OI_funding_crowding_interaction |               256 |                  256 |                             24 |                       6 |                       154 | F2_OI_funding_crowding_interaction |                             256 |                       0.18 |                         24 |          0.133333 | True         |
| F3_positioning_divergence          |               256 |                  256 |                             24 |                       7 |                       226 | F3_positioning_divergence          |                             256 |                       0.16 |                         24 |          0.133333 | True         |
| F4_OI_taker_flow_interaction       |               256 |                  256 |                             24 |                       6 |                       148 | F4_OI_taker_flow_interaction       |                             256 |                       0.16 |                         24 |          0.133333 | True         |
| F5_OI_upper_regime_interaction     |               256 |                  256 |                             24 |                      16 |                       192 | F5_OI_upper_regime_interaction     |                             256 |                       0.16 |                         24 |          0.133333 | True         |
| F6_OI_latent_state_interaction     |               256 |                  256 |                             24 |                      10 |                       166 | F6_OI_latent_state_interaction     |                             256 |                       0.16 |                         24 |          0.133333 | True         |

## Skeleton Diversity Audit

| objective_family                   |   candidate_count |   skeleton_count |   production_count |   top_skeleton_count |   top_production_count |   top_skeleton_share |   top_production_share | diversity_pass   |
|:-----------------------------------|------------------:|-----------------:|-------------------:|---------------------:|-----------------------:|---------------------:|-----------------------:|:-----------------|
| F0_OI_delta_price_interaction      |               384 |                7 |                216 |                   55 |                      2 |             0.143229 |             0.00520833 | True             |
| F1_OI_basis_premium_interaction    |               256 |                6 |                154 |                   43 |                      2 |             0.167969 |             0.0078125  | True             |
| F2_OI_funding_crowding_interaction |               256 |                6 |                154 |                   43 |                      2 |             0.167969 |             0.0078125  | True             |
| F3_positioning_divergence          |               256 |                7 |                226 |                   37 |                      2 |             0.144531 |             0.0078125  | True             |
| F4_OI_taker_flow_interaction       |               256 |                6 |                148 |                   43 |                      2 |             0.167969 |             0.0078125  | True             |
| F5_OI_upper_regime_interaction     |               256 |               16 |                192 |                   16 |                      2 |             0.0625   |             0.0078125  | True             |
| F6_OI_latent_state_interaction     |               256 |               10 |                166 |                   26 |                      5 |             0.101562 |             0.0195312  | True             |

## Field Source Audit

| field_name                            | source_contract         | field_class                    | pit_policy                | in_base_panel_schema   | allowed_for_historical_dry_generation   |
|:--------------------------------------|:------------------------|:-------------------------------|:--------------------------|:-----------------------|:----------------------------------------|
| R0_market_trend_state                 | a7al0g_upper_regime     | train_only_state               | timestamp_plus_1h_primary | False                  | True                                    |
| R10_stress_proxy_state                | a7al0g_upper_regime     | train_only_state               | timestamp_plus_1h_primary | False                  | True                                    |
| R2_market_breadth_state               | a7al0g_upper_regime     | train_only_state               | timestamp_plus_1h_primary | False                  | True                                    |
| R3_liquidity_cycle_state              | a7al0g_upper_regime     | train_only_state               | timestamp_plus_1h_primary | False                  | True                                    |
| R4_leverage_crowding_state            | a7al0g_upper_regime     | train_only_state               | timestamp_plus_1h_primary | False                  | True                                    |
| R5_basis_premium_dislocation_state    | a7al0g_upper_regime     | train_only_state               | timestamp_plus_1h_primary | False                  | True                                    |
| R6_positioning_crowding_state         | a7al0g_upper_regime     | train_only_state               | timestamp_plus_1h_primary | False                  | True                                    |
| R9_alt_vs_major_dispersion_state      | a7al0g_upper_regime     | train_only_state               | timestamp_plus_1h_primary | False                  | True                                    |
| binance_internal_mark_index_basis_bps | binance_market_history  | derived_historical             | timestamp_plus_1h_primary | False                  | True                                    |
| funding_rate                          | binance_funding_history | raw_source                     | timestamp_plus_1h_primary | True                   | True                                    |
| funding_rate_abs_168h                 | a7ak_lv1_derived        | derived_rolling                | timestamp_plus_1h_primary | False                  | True                                    |
| funding_rate_mean_168h                | a7ak_lv1_derived        | derived_rolling                | timestamp_plus_1h_primary | False                  | True                                    |
| global_long_short_account_ratio_last  | binance_metrics_history | raw_source                     | timestamp_plus_1h_primary | True                   | True                                    |
| global_long_short_account_ratio_mean  | binance_metrics_history | raw_source                     | timestamp_plus_1h_primary | True                   | True                                    |
| index_close                           | binance_market_history  | raw_source                     | timestamp_plus_1h_primary | True                   | True                                    |
| is_major                              | a7ak_taxonomy           | observable_taxonomy            | timestamp_plus_1h_primary | False                  | True                                    |
| is_multiplier_contract                | a7ak_taxonomy           | observable_taxonomy            | timestamp_plus_1h_primary | False                  | True                                    |
| kline_taker_buy_quote_share           | binance_market_history  | raw_source_or_derived          | timestamp_plus_1h_primary | True                   | True                                    |
| liquidity_rank_active_universe        | a7ak_lv1_latent         | train_only_or_observable_state | timestamp_plus_1h_primary | False                  | True                                    |
| liquidity_tier                        | a7ak_taxonomy           | observable_taxonomy            | timestamp_plus_1h_primary | False                  | True                                    |
| listing_age_days                      | a7ak_lv1_latent         | train_only_or_observable_state | timestamp_plus_1h_primary | False                  | True                                    |
| mark_close                            | binance_market_history  | raw_source                     | timestamp_plus_1h_primary | True                   | True                                    |
| mark_index_basis_bps                  | binance_market_history  | derived_historical             | timestamp_plus_1h_primary | True                   | True                                    |
| mark_trade_basis_bps                  | binance_market_history  | derived_historical             | timestamp_plus_1h_primary | True                   | True                                    |
| meme_contract_group                   | a7ak_taxonomy           | observable_taxonomy            | timestamp_plus_1h_primary | False                  | True                                    |
| open_interest_last                    | binance_metrics_history | raw_source                     | timestamp_plus_1h_primary | True                   | True                                    |
| open_interest_mean                    | binance_metrics_history | raw_source                     | timestamp_plus_1h_primary | True                   | True                                    |
| open_interest_value_last              | binance_metrics_history | raw_source                     | timestamp_plus_1h_primary | True                   | True                                    |
| open_interest_value_mean              | binance_metrics_history | raw_source                     | timestamp_plus_1h_primary | True                   | True                                    |
| premium_close                         | binance_premium_history | raw_source                     | timestamp_plus_1h_primary | True                   | True                                    |
| premium_close_bps                     | binance_premium_history | raw_source                     | timestamp_plus_1h_primary | True                   | True                                    |
| raw_latent_state_id                   | a7ak_lv1_latent         | train_only_or_observable_state | timestamp_plus_1h_primary | False                  | True                                    |
| taker_buy_quote_volume                | binance_market_history  | raw_source_or_derived          | timestamp_plus_1h_primary | True                   | True                                    |
| taker_buy_sell_volume_ratio_last      | binance_metrics_history | raw_source                     | timestamp_plus_1h_primary | True                   | True                                    |
| taker_buy_sell_volume_ratio_mean      | binance_metrics_history | raw_source                     | timestamp_plus_1h_primary | True                   | True                                    |
| top_long_short_account_ratio_last     | binance_metrics_history | raw_source                     | timestamp_plus_1h_primary | True                   | True                                    |
| top_long_short_account_ratio_mean     | binance_metrics_history | raw_source                     | timestamp_plus_1h_primary | True                   | True                                    |
| top_long_short_position_ratio_last    | binance_metrics_history | raw_source                     | timestamp_plus_1h_primary | True                   | True                                    |
| top_long_short_position_ratio_mean    | binance_metrics_history | raw_source                     | timestamp_plus_1h_primary | True                   | True                                    |
| trade_close                           | binance_market_history  | raw_source                     | timestamp_plus_1h_primary | True                   | True                                    |

## Forbidden Fallback Audit

| forbidden_item                             | policy   |   candidate_hit_count |
|:-------------------------------------------|:---------|----------------------:|
| same_direct_oi_price_rerun                 | forbid   |                     0 |
| direct_oi_price_level_gap_standalone       | forbid   |                     0 |
| funding_only_wrapper                       | forbid   |                     0 |
| basis_only_wrapper                         | forbid   |                     0 |
| liquidity_volatility_old_family            | forbid   |                     0 |
| a7v_activity_liquidity_self_reproduction   | forbid   |                     0 |
| j5_cross_exchange_overlay_historical_proof | forbid   |                     0 |
| raw_okx_binance_direct_price_comparison    | forbid   |                     0 |
| may_in_selector_or_generation              | forbid   |                     0 |

## Authorization

```json
{
  "a7al2x4_family_balanced_replay_preflight": "READY_FOR_REVIEW_NOT_AUTHORIZED",
  "a7al2y_generation": "NOT_AUTHORIZED",
  "alpha_proof": "NOT_AUTHORIZED",
  "decision": "PASS_A7AL2X3_FAMILY_BALANCED_DRY_GENERATION_LEDGER_READY_FOR_PREFLIGHT_REVIEW",
  "large_formula_search": "NOT_AUTHORIZED",
  "reason": "A7AL-2X3 is dry generation and ledger construction only; replay/preflight requires a separate authorization record.",
  "shadow_paper_live": "NOT_AUTHORIZED"
}
```

## Boundary

```text
No replay.
No search execution.
No May in generation / ranking / selector / mutation.
No alpha proof / shadow / paper / live.

A7AL-2X4 family-balanced replay preflight requires a separate authorization record.
```
