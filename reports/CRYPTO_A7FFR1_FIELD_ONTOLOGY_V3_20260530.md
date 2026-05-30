# CRYPTO A7FF-R1 FIELD ONTOLOGY V3

Generated: 2026-05-30T05:51:45Z

## Decision

`PASS_A7FFR1_FIELD_ONTOLOGY_V3_BUILT`

## Manifest

```json
{
  "authorizes_a7ffr2": true,
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "decision": "PASS_A7FFR1_FIELD_ONTOLOGY_V3_BUILT",
  "executes_generation": false,
  "executes_search": false,
  "exploratory_signal_seed_count": 4,
  "field_count": 81,
  "generated_at": "2026-05-30T05:51:45Z",
  "ordinary_alpha_seed_count": 1,
  "regime_neutralizer_interaction_seed_count": 73,
  "semantic_type_count": 8,
  "stage": "A7FF-R1-FIELD-ONTOLOGY-V3"
}
```

## Semantic / Role Summary

| semantic_type_v3   | compiler_role_v3                    |   field_count |
|:-------------------|:------------------------------------|--------------:|
| basis_premium_like | exploratory_signal_seed             |             1 |
| basis_premium_like | ordinary_alpha_seed                 |             1 |
| basis_premium_like | regime_neutralizer_interaction_seed |            18 |
| funding_like       | regime_neutralizer_interaction_seed |             6 |
| generic_numeric    | blocked_or_unlicensed               |             2 |
| generic_numeric    | regime_neutralizer_interaction_seed |             9 |
| liquidity_like     | regime_neutralizer_interaction_seed |            11 |
| positioning_like   | regime_neutralizer_interaction_seed |            15 |
| price_like         | exploratory_signal_seed             |             1 |
| price_like         | forbidden_label_future_or_timing    |             1 |
| price_like         | regime_neutralizer_interaction_seed |             2 |
| state_or_taxonomy  | regime_neutralizer_interaction_seed |             8 |
| volatility_like    | exploratory_signal_seed             |             2 |
| volatility_like    | regime_neutralizer_interaction_seed |             4 |

## Ontology Preview

| field_name                           | semantic_type_v3   | compiler_role_v3                    | allowed_roles_v3                                            |   non_l7_candidate_count |   primitive_candidate_count |
|:-------------------------------------|:-------------------|:------------------------------------|:------------------------------------------------------------|-------------------------:|----------------------------:|
| funding_rate                         | funding_like       | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| global_long_short_account_ratio_last | positioning_like   | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| global_long_short_account_ratio_mean | positioning_like   | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| index_close                          | basis_premium_like | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| mark_close                           | basis_premium_like | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| mark_high                            | basis_premium_like | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| mark_index_basis_bps                 | basis_premium_like | ordinary_alpha_seed                 | signal\|interaction\|selector                               |                        2 |                           2 |
| mark_low                             | basis_premium_like | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| mark_trade_basis_bps                 | basis_premium_like | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| open_interest_last                   | positioning_like   | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| open_interest_mean                   | positioning_like   | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| open_interest_value_last             | positioning_like   | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| open_interest_value_mean             | positioning_like   | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| premium_close                        | basis_premium_like | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| premium_close_bps                    | basis_premium_like | exploratory_signal_seed             | diagnostic_signal\|interaction\|selector_after_confirmation |                        0 |                           1 |
| taker_buy_quote_volume               | liquidity_like     | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| taker_buy_sell_volume_ratio_last     | positioning_like   | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| taker_buy_sell_volume_ratio_mean     | positioning_like   | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| top_long_short_account_ratio_last    | positioning_like   | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| top_long_short_account_ratio_mean    | positioning_like   | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| top_long_short_position_ratio_last   | positioning_like   | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| top_long_short_position_ratio_mean   | positioning_like   | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| trade_close                          | price_like         | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| trade_count                          | liquidity_like     | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| trade_high                           | volatility_like    | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| trade_low                            | volatility_like    | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| trade_quote_volume                   | liquidity_like     | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| trade_volume                         | liquidity_like     | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| age_percentile_active_universe       | state_or_taxonomy  | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| age_x_funding_abs                    | funding_like       | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| age_x_liquidity                      | liquidity_like     | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| age_x_volatility                     | volatility_like    | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| basis_abs_168h                       | basis_premium_like | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| execution_time                       | generic_numeric    | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| feature_available_time               | generic_numeric    | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| forward_trade_return_1h              | price_like         | forbidden_label_future_or_timing    | none                                                        |                        0 |                           0 |
| funding_interval_hours               | funding_like       | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| funding_rate_abs_168h                | funding_like       | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| funding_rate_mean_168h               | funding_like       | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| gap_hours_recent_168h                | generic_numeric    | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| history_length_hours                 | generic_numeric    | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| index_count                          | basis_premium_like | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| index_high                           | basis_premium_like | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| index_low                            | basis_premium_like | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| index_open                           | basis_premium_like | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| is_forward_only                      | generic_numeric    | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| is_historical_backfill               | generic_numeric    | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| kline_taker_buy_quote_share          | state_or_taxonomy  | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| liquidity_rank_active_universe       | liquidity_like     | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| listing_age_days                     | state_or_taxonomy  | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| listing_age_hours                    | state_or_taxonomy  | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| log1p_listing_age_days               | state_or_taxonomy  | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| log_quote_volume_168h                | liquidity_like     | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| mark_count                           | basis_premium_like | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| mark_open                            | basis_premium_like | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| median_quote_volume_168h             | liquidity_like     | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| metrics_n_5m                         | positioning_like   | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| oi_x_price_move_24h                  | positioning_like   | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| open_interest_change_24h             | positioning_like   | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| premium_abs_168h                     | basis_premium_like | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| premium_count                        | basis_premium_like | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| premium_high                         | basis_premium_like | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| premium_low                          | basis_premium_like | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| premium_open                         | basis_premium_like | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| raw_latent_state_id                  | state_or_taxonomy  | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| realized_vol_168h                    | volatility_like    | exploratory_signal_seed             | diagnostic_signal\|interaction\|selector_after_confirmation |                        0 |                           2 |
| realized_vol_24h                     | volatility_like    | exploratory_signal_seed             | diagnostic_signal\|interaction\|selector_after_confirmation |                        0 |                           2 |
| realized_vol_72h                     | volatility_like    | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| rolling_coverage_168h                | state_or_taxonomy  | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| source_market_funding                | funding_like       | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| source_metrics                       | generic_numeric    | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| source_trade_klines                  | generic_numeric    | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| sqrt_listing_age_days                | state_or_taxonomy  | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| symbol                               | generic_numeric    | blocked_or_unlicensed               | none                                                        |                        0 |                           0 |
| taker_buy_volume                     | liquidity_like     | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| timestamp                            | generic_numeric    | blocked_or_unlicensed               | none                                                        |                        0 |                           0 |
| trade_count_168h                     | liquidity_like     | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| trade_open                           | generic_numeric    | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| trade_return_1h                      | price_like         | exploratory_signal_seed             | diagnostic_signal\|interaction\|selector_after_confirmation |                        0 |                           4 |
| trade_return_24h                     | price_like         | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
| volume_volatility_ratio_168h         | liquidity_like     | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier                   |                        0 |                           0 |
