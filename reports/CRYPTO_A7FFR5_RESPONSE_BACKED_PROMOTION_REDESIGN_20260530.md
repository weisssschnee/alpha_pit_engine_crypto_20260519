# CRYPTO A7FF-R5 RESPONSE BACKED PROMOTION REDESIGN

Generated: 2026-05-30T05:51:47Z

## Decision

`PASS_A7FFR5_PROMOTION_REDESIGN_READY_BUT_SEARCH_STILL_HOLD`

## Manifest

```json
{
  "authorizes_a7ff23r_contract": true,
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFR5_PROMOTION_REDESIGN_READY_BUT_SEARCH_STILL_HOLD",
  "executes_generation": false,
  "executes_search": false,
  "generated_at": "2026-05-30T05:51:47Z",
  "pair_policy_rows": 3003,
  "seed_preview_rows": 78,
  "signal_semantic_family_count": 3,
  "stage": "A7FF-R5-RESPONSE-BACKED-PROMOTION-REDESIGN"
}
```

## Promotion Gates

| gate                  | threshold                                               | hard   |
|:----------------------|:--------------------------------------------------------|:-------|
| non_l7_label_evidence | >=1 non-L7 candidate row                                | True   |
| control_clean         | control_ratio < 0.80 for promotion; <1.0 for diagnostic | True   |
| lag_and_timing        | lag_ok and timing_ok                                    | True   |
| cost_survival         | cost5-or-better for diagnostic; cost10 preferred        | False  |
| role_integrity        | risk/regime fields cannot become standalone alpha       | True   |
| field_family_breadth  | >=3 semantic families before search authorization       | True   |
| selector_policy       | external label-balanced selector only                   | True   |

## Seed Preview

| field_name                           | semantic_type_v3   | compiler_role_v3                    |   non_l7_candidate_count |   primitive_candidate_count |   best_control_ratio | allowed_roles_v3                                            |
|:-------------------------------------|:-------------------|:------------------------------------|-------------------------:|----------------------------:|---------------------:|:------------------------------------------------------------|
| funding_rate                         | funding_like       | regime_neutralizer_interaction_seed |                        0 |                           0 |             1.07473  | regime\|neutralizer\|interaction_modifier                   |
| global_long_short_account_ratio_last | positioning_like   | regime_neutralizer_interaction_seed |                        0 |                           0 |             2.2572   | regime\|neutralizer\|interaction_modifier                   |
| global_long_short_account_ratio_mean | positioning_like   | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| index_close                          | basis_premium_like | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| mark_close                           | basis_premium_like | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| mark_high                            | basis_premium_like | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| mark_index_basis_bps                 | basis_premium_like | ordinary_alpha_seed                 |                        2 |                           2 |             0.141289 | signal\|interaction\|selector                               |
| mark_low                             | basis_premium_like | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| mark_trade_basis_bps                 | basis_premium_like | regime_neutralizer_interaction_seed |                        0 |                           0 |             0.107775 | regime\|neutralizer\|interaction_modifier                   |
| open_interest_last                   | positioning_like   | regime_neutralizer_interaction_seed |                        0 |                           0 |             1.11232  | regime\|neutralizer\|interaction_modifier                   |
| open_interest_mean                   | positioning_like   | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| open_interest_value_last             | positioning_like   | regime_neutralizer_interaction_seed |                        0 |                           0 |             2.31152  | regime\|neutralizer\|interaction_modifier                   |
| open_interest_value_mean             | positioning_like   | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| premium_close                        | basis_premium_like | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| premium_close_bps                    | basis_premium_like | exploratory_signal_seed             |                        0 |                           1 |             0.791438 | diagnostic_signal\|interaction\|selector_after_confirmation |
| taker_buy_quote_volume               | liquidity_like     | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| taker_buy_sell_volume_ratio_last     | positioning_like   | regime_neutralizer_interaction_seed |                        0 |                           0 |             0.688118 | regime\|neutralizer\|interaction_modifier                   |
| taker_buy_sell_volume_ratio_mean     | positioning_like   | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| top_long_short_account_ratio_last    | positioning_like   | regime_neutralizer_interaction_seed |                        0 |                           0 |             1.78409  | regime\|neutralizer\|interaction_modifier                   |
| top_long_short_account_ratio_mean    | positioning_like   | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| top_long_short_position_ratio_last   | positioning_like   | regime_neutralizer_interaction_seed |                        0 |                           0 |             3.08939  | regime\|neutralizer\|interaction_modifier                   |
| top_long_short_position_ratio_mean   | positioning_like   | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| trade_close                          | price_like         | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| trade_count                          | liquidity_like     | regime_neutralizer_interaction_seed |                        0 |                           0 |             3.36459  | regime\|neutralizer\|interaction_modifier                   |
| trade_high                           | volatility_like    | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| trade_low                            | volatility_like    | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| trade_quote_volume                   | liquidity_like     | regime_neutralizer_interaction_seed |                        0 |                           0 |             3.89734  | regime\|neutralizer\|interaction_modifier                   |
| trade_volume                         | liquidity_like     | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| age_percentile_active_universe       | state_or_taxonomy  | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| age_x_funding_abs                    | funding_like       | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| age_x_liquidity                      | liquidity_like     | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| age_x_volatility                     | volatility_like    | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| basis_abs_168h                       | basis_premium_like | regime_neutralizer_interaction_seed |                        0 |                           0 |             1.3929   | regime\|neutralizer\|interaction_modifier                   |
| execution_time                       | generic_numeric    | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| feature_available_time               | generic_numeric    | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| funding_interval_hours               | funding_like       | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| funding_rate_abs_168h                | funding_like       | regime_neutralizer_interaction_seed |                        0 |                           0 |             0.607009 | regime\|neutralizer\|interaction_modifier                   |
| funding_rate_mean_168h               | funding_like       | regime_neutralizer_interaction_seed |                        0 |                           0 |             0.826288 | regime\|neutralizer\|interaction_modifier                   |
| gap_hours_recent_168h                | generic_numeric    | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| history_length_hours                 | generic_numeric    | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| index_count                          | basis_premium_like | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| index_high                           | basis_premium_like | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| index_low                            | basis_premium_like | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| index_open                           | basis_premium_like | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| is_forward_only                      | generic_numeric    | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| is_historical_backfill               | generic_numeric    | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| kline_taker_buy_quote_share          | state_or_taxonomy  | regime_neutralizer_interaction_seed |                        0 |                           0 |             0.997123 | regime\|neutralizer\|interaction_modifier                   |
| liquidity_rank_active_universe       | liquidity_like     | regime_neutralizer_interaction_seed |                        0 |                           0 |             2.14076  | regime\|neutralizer\|interaction_modifier                   |
| listing_age_days                     | state_or_taxonomy  | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| listing_age_hours                    | state_or_taxonomy  | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| log1p_listing_age_days               | state_or_taxonomy  | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| log_quote_volume_168h                | liquidity_like     | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| mark_count                           | basis_premium_like | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| mark_open                            | basis_premium_like | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| median_quote_volume_168h             | liquidity_like     | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| metrics_n_5m                         | positioning_like   | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| oi_x_price_move_24h                  | positioning_like   | regime_neutralizer_interaction_seed |                        0 |                           0 |             1.79112  | regime\|neutralizer\|interaction_modifier                   |
| open_interest_change_24h             | positioning_like   | regime_neutralizer_interaction_seed |                        0 |                           0 |             6.54461  | regime\|neutralizer\|interaction_modifier                   |
| premium_abs_168h                     | basis_premium_like | regime_neutralizer_interaction_seed |                        0 |                           0 |             2.32717  | regime\|neutralizer\|interaction_modifier                   |
| premium_count                        | basis_premium_like | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| premium_high                         | basis_premium_like | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| premium_low                          | basis_premium_like | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| premium_open                         | basis_premium_like | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| raw_latent_state_id                  | state_or_taxonomy  | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| realized_vol_168h                    | volatility_like    | exploratory_signal_seed             |                        0 |                           2 |             0.879498 | diagnostic_signal\|interaction\|selector_after_confirmation |
| realized_vol_24h                     | volatility_like    | exploratory_signal_seed             |                        0 |                           2 |             0.939508 | diagnostic_signal\|interaction\|selector_after_confirmation |
| realized_vol_72h                     | volatility_like    | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| rolling_coverage_168h                | state_or_taxonomy  | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| source_market_funding                | funding_like       | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| source_metrics                       | generic_numeric    | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| source_trade_klines                  | generic_numeric    | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| sqrt_listing_age_days                | state_or_taxonomy  | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| taker_buy_volume                     | liquidity_like     | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| trade_count_168h                     | liquidity_like     | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| trade_open                           | generic_numeric    | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
| trade_return_1h                      | price_like         | exploratory_signal_seed             |                        0 |                           4 |             0.254317 | diagnostic_signal\|interaction\|selector_after_confirmation |
| trade_return_24h                     | price_like         | regime_neutralizer_interaction_seed |                        0 |                           0 |             6.21288  | regime\|neutralizer\|interaction_modifier                   |
| volume_volatility_ratio_168h         | liquidity_like     | regime_neutralizer_interaction_seed |                        0 |                           0 |           nan        | regime\|neutralizer\|interaction_modifier                   |
