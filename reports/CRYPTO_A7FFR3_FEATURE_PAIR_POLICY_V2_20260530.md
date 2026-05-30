# CRYPTO A7FF-R3 FEATURE PAIR POLICY V2

Generated: 2026-05-30T05:51:47Z

## Decision

`PASS_A7FFR3_FEATURE_PAIR_POLICY_READY`

## Manifest

```json
{
  "allow_high_priority_pairs": 132,
  "authorizes_a7ffr4": true,
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "decision": "PASS_A7FFR3_FEATURE_PAIR_POLICY_READY",
  "executes_generation": false,
  "executes_search": false,
  "generated_at": "2026-05-30T05:51:47Z",
  "pair_count": 3003,
  "probe_high_priority_pairs": 705,
  "seed_field_count": 78,
  "stage": "A7FF-R3-FEATURE-PAIR-POLICY-V2"
}
```

## Pair Policy Summary

| semantic_pair                          | pair_policy_v2             |   pair_count |
|:---------------------------------------|:---------------------------|-------------:|
| basis_premium_like\|positioning_like   | probe_high_priority        |          281 |
| basis_premium_like\|liquidity_like     | diagnostic_or_low_priority |          205 |
| basis_premium_like\|basis_premium_like | diagnostic_or_low_priority |          176 |
| basis_premium_like\|generic_numeric    | diagnostic_or_low_priority |          174 |
| liquidity_like\|positioning_like       | diagnostic_or_low_priority |          165 |
| basis_premium_like\|state_or_taxonomy  | diagnostic_or_low_priority |          154 |
| generic_numeric\|positioning_like      | diagnostic_or_low_priority |          135 |
| positioning_like\|state_or_taxonomy    | diagnostic_or_low_priority |          120 |
| basis_premium_like\|funding_like       | probe_high_priority        |          118 |
| basis_premium_like\|volatility_like    | probe_high_priority        |          110 |
| positioning_like\|positioning_like     | diagnostic_or_low_priority |          105 |
| generic_numeric\|liquidity_like        | diagnostic_or_low_priority |           99 |
| funding_like\|positioning_like         | probe_high_priority        |           90 |
| liquidity_like\|state_or_taxonomy      | diagnostic_or_low_priority |           88 |
| positioning_like\|volatility_like      | diagnostic_or_low_priority |           78 |
| generic_numeric\|state_or_taxonomy     | diagnostic_or_low_priority |           72 |
| funding_like\|liquidity_like           | diagnostic_or_low_priority |           66 |
| liquidity_like\|liquidity_like         | diagnostic_or_low_priority |           55 |
| funding_like\|generic_numeric          | diagnostic_or_low_priority |           54 |
| basis_premium_like\|price_like         | probe_high_priority        |           54 |
| liquidity_like\|volatility_like        | probe_high_priority        |           52 |
| generic_numeric\|volatility_like       | diagnostic_or_low_priority |           48 |
| funding_like\|state_or_taxonomy        | diagnostic_or_low_priority |           48 |
| positioning_like\|price_like           | diagnostic_or_low_priority |           45 |
| state_or_taxonomy\|volatility_like     | diagnostic_or_low_priority |           44 |
| generic_numeric\|generic_numeric       | diagnostic_or_low_priority |           36 |
| funding_like\|volatility_like          | diagnostic_or_low_priority |           34 |
| liquidity_like\|price_like             | diagnostic_or_low_priority |           31 |
| state_or_taxonomy\|state_or_taxonomy   | diagnostic_or_low_priority |           28 |
| generic_numeric\|price_like            | diagnostic_or_low_priority |           27 |
| price_like\|state_or_taxonomy          | diagnostic_or_low_priority |           24 |
| basis_premium_like\|positioning_like   | allow_high_priority        |           19 |
| funding_like\|price_like               | diagnostic_or_low_priority |           18 |
| basis_premium_like\|liquidity_like     | allow_high_priority        |           15 |
| funding_like\|funding_like             | diagnostic_or_low_priority |           15 |
| liquidity_like\|volatility_like        | allow_high_priority        |           14 |
| basis_premium_like\|basis_premium_like | allow_high_priority        |           14 |
| price_like\|volatility_like            | diagnostic_or_low_priority |           12 |
| positioning_like\|volatility_like      | allow_high_priority        |           12 |
| basis_premium_like\|volatility_like    | allow_high_priority        |           10 |
| volatility_like\|volatility_like       | diagnostic_or_low_priority |            8 |
| volatility_like\|volatility_like       | allow_high_priority        |            7 |
| basis_premium_like\|price_like         | allow_high_priority        |            6 |
| basis_premium_like\|generic_numeric    | allow_high_priority        |            6 |
| basis_premium_like\|state_or_taxonomy  | allow_high_priority        |            6 |
| generic_numeric\|volatility_like       | allow_high_priority        |            6 |
| price_like\|volatility_like            | allow_high_priority        |            6 |
| state_or_taxonomy\|volatility_like     | allow_high_priority        |            4 |
| basis_premium_like\|funding_like       | allow_high_priority        |            2 |
| liquidity_like\|price_like             | allow_high_priority        |            2 |
| funding_like\|volatility_like          | allow_high_priority        |            2 |
| price_like\|price_like                 | diagnostic_or_low_priority |            2 |
| price_like\|price_like                 | allow_high_priority        |            1 |

## Pair Policy Preview

| left_field                           | right_field                          | left_semantic_type   | right_semantic_type   | semantic_pair                        | left_role                           | right_role                          | pair_policy_v2             |
|:-------------------------------------|:-------------------------------------|:---------------------|:----------------------|:-------------------------------------|:------------------------------------|:------------------------------------|:---------------------------|
| funding_rate                         | global_long_short_account_ratio_last | funding_like         | positioning_like      | funding_like\|positioning_like       | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| funding_rate                         | global_long_short_account_ratio_mean | funding_like         | positioning_like      | funding_like\|positioning_like       | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| funding_rate                         | index_close                          | funding_like         | basis_premium_like    | basis_premium_like\|funding_like     | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| funding_rate                         | mark_close                           | funding_like         | basis_premium_like    | basis_premium_like\|funding_like     | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| funding_rate                         | mark_high                            | funding_like         | basis_premium_like    | basis_premium_like\|funding_like     | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| funding_rate                         | mark_index_basis_bps                 | funding_like         | basis_premium_like    | basis_premium_like\|funding_like     | regime_neutralizer_interaction_seed | ordinary_alpha_seed                 | probe_high_priority        |
| funding_rate                         | mark_low                             | funding_like         | basis_premium_like    | basis_premium_like\|funding_like     | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| funding_rate                         | mark_trade_basis_bps                 | funding_like         | basis_premium_like    | basis_premium_like\|funding_like     | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| funding_rate                         | open_interest_last                   | funding_like         | positioning_like      | funding_like\|positioning_like       | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| funding_rate                         | open_interest_mean                   | funding_like         | positioning_like      | funding_like\|positioning_like       | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| funding_rate                         | open_interest_value_last             | funding_like         | positioning_like      | funding_like\|positioning_like       | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| funding_rate                         | open_interest_value_mean             | funding_like         | positioning_like      | funding_like\|positioning_like       | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| funding_rate                         | premium_close                        | funding_like         | basis_premium_like    | basis_premium_like\|funding_like     | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| funding_rate                         | premium_close_bps                    | funding_like         | basis_premium_like    | basis_premium_like\|funding_like     | regime_neutralizer_interaction_seed | exploratory_signal_seed             | probe_high_priority        |
| funding_rate                         | taker_buy_quote_volume               | funding_like         | liquidity_like        | funding_like\|liquidity_like         | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| funding_rate                         | taker_buy_sell_volume_ratio_last     | funding_like         | positioning_like      | funding_like\|positioning_like       | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| funding_rate                         | taker_buy_sell_volume_ratio_mean     | funding_like         | positioning_like      | funding_like\|positioning_like       | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| funding_rate                         | top_long_short_account_ratio_last    | funding_like         | positioning_like      | funding_like\|positioning_like       | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| funding_rate                         | top_long_short_account_ratio_mean    | funding_like         | positioning_like      | funding_like\|positioning_like       | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| funding_rate                         | top_long_short_position_ratio_last   | funding_like         | positioning_like      | funding_like\|positioning_like       | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| funding_rate                         | top_long_short_position_ratio_mean   | funding_like         | positioning_like      | funding_like\|positioning_like       | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| funding_rate                         | trade_close                          | funding_like         | price_like            | funding_like\|price_like             | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| funding_rate                         | trade_count                          | funding_like         | liquidity_like        | funding_like\|liquidity_like         | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| funding_rate                         | trade_high                           | funding_like         | volatility_like       | funding_like\|volatility_like        | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| funding_rate                         | trade_low                            | funding_like         | volatility_like       | funding_like\|volatility_like        | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| funding_rate                         | trade_quote_volume                   | funding_like         | liquidity_like        | funding_like\|liquidity_like         | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| funding_rate                         | trade_volume                         | funding_like         | liquidity_like        | funding_like\|liquidity_like         | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| funding_rate                         | funding_rate_abs_168h                | funding_like         | funding_like          | funding_like\|funding_like           | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| funding_rate                         | funding_rate_mean_168h               | funding_like         | funding_like          | funding_like\|funding_like           | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| funding_rate                         | gap_hours_recent_168h                | funding_like         | generic_numeric       | funding_like\|generic_numeric        | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| funding_rate                         | history_length_hours                 | funding_like         | generic_numeric       | funding_like\|generic_numeric        | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| funding_rate                         | index_count                          | funding_like         | basis_premium_like    | basis_premium_like\|funding_like     | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| funding_rate                         | index_high                           | funding_like         | basis_premium_like    | basis_premium_like\|funding_like     | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| funding_rate                         | index_low                            | funding_like         | basis_premium_like    | basis_premium_like\|funding_like     | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| funding_rate                         | index_open                           | funding_like         | basis_premium_like    | basis_premium_like\|funding_like     | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| funding_rate                         | is_forward_only                      | funding_like         | generic_numeric       | funding_like\|generic_numeric        | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| funding_rate                         | is_historical_backfill               | funding_like         | generic_numeric       | funding_like\|generic_numeric        | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| funding_rate                         | kline_taker_buy_quote_share          | funding_like         | state_or_taxonomy     | funding_like\|state_or_taxonomy      | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| funding_rate                         | liquidity_rank_active_universe       | funding_like         | liquidity_like        | funding_like\|liquidity_like         | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| funding_rate                         | listing_age_days                     | funding_like         | state_or_taxonomy     | funding_like\|state_or_taxonomy      | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| funding_rate                         | listing_age_hours                    | funding_like         | state_or_taxonomy     | funding_like\|state_or_taxonomy      | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| funding_rate                         | log1p_listing_age_days               | funding_like         | state_or_taxonomy     | funding_like\|state_or_taxonomy      | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| funding_rate                         | log_quote_volume_168h                | funding_like         | liquidity_like        | funding_like\|liquidity_like         | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| funding_rate                         | mark_count                           | funding_like         | basis_premium_like    | basis_premium_like\|funding_like     | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| funding_rate                         | mark_open                            | funding_like         | basis_premium_like    | basis_premium_like\|funding_like     | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| funding_rate                         | median_quote_volume_168h             | funding_like         | liquidity_like        | funding_like\|liquidity_like         | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| funding_rate                         | metrics_n_5m                         | funding_like         | positioning_like      | funding_like\|positioning_like       | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| funding_rate                         | oi_x_price_move_24h                  | funding_like         | positioning_like      | funding_like\|positioning_like       | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| funding_rate                         | open_interest_change_24h             | funding_like         | positioning_like      | funding_like\|positioning_like       | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| funding_rate                         | premium_abs_168h                     | funding_like         | basis_premium_like    | basis_premium_like\|funding_like     | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| funding_rate                         | premium_count                        | funding_like         | basis_premium_like    | basis_premium_like\|funding_like     | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| funding_rate                         | premium_high                         | funding_like         | basis_premium_like    | basis_premium_like\|funding_like     | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| funding_rate                         | premium_low                          | funding_like         | basis_premium_like    | basis_premium_like\|funding_like     | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| funding_rate                         | premium_open                         | funding_like         | basis_premium_like    | basis_premium_like\|funding_like     | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| funding_rate                         | raw_latent_state_id                  | funding_like         | state_or_taxonomy     | funding_like\|state_or_taxonomy      | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| funding_rate                         | realized_vol_168h                    | funding_like         | volatility_like       | funding_like\|volatility_like        | regime_neutralizer_interaction_seed | exploratory_signal_seed             | diagnostic_or_low_priority |
| funding_rate                         | realized_vol_24h                     | funding_like         | volatility_like       | funding_like\|volatility_like        | regime_neutralizer_interaction_seed | exploratory_signal_seed             | diagnostic_or_low_priority |
| funding_rate                         | realized_vol_72h                     | funding_like         | volatility_like       | funding_like\|volatility_like        | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| funding_rate                         | rolling_coverage_168h                | funding_like         | state_or_taxonomy     | funding_like\|state_or_taxonomy      | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| funding_rate                         | source_market_funding                | funding_like         | funding_like          | funding_like\|funding_like           | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| funding_rate                         | source_metrics                       | funding_like         | generic_numeric       | funding_like\|generic_numeric        | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| funding_rate                         | source_trade_klines                  | funding_like         | generic_numeric       | funding_like\|generic_numeric        | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| funding_rate                         | sqrt_listing_age_days                | funding_like         | state_or_taxonomy     | funding_like\|state_or_taxonomy      | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| funding_rate                         | taker_buy_volume                     | funding_like         | liquidity_like        | funding_like\|liquidity_like         | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| funding_rate                         | trade_count_168h                     | funding_like         | liquidity_like        | funding_like\|liquidity_like         | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| funding_rate                         | trade_open                           | funding_like         | generic_numeric       | funding_like\|generic_numeric        | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| funding_rate                         | trade_return_1h                      | funding_like         | price_like            | funding_like\|price_like             | regime_neutralizer_interaction_seed | exploratory_signal_seed             | diagnostic_or_low_priority |
| funding_rate                         | trade_return_24h                     | funding_like         | price_like            | funding_like\|price_like             | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| funding_rate                         | volume_volatility_ratio_168h         | funding_like         | liquidity_like        | funding_like\|liquidity_like         | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| global_long_short_account_ratio_last | global_long_short_account_ratio_mean | positioning_like     | positioning_like      | positioning_like\|positioning_like   | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| global_long_short_account_ratio_last | index_close                          | positioning_like     | basis_premium_like    | basis_premium_like\|positioning_like | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| global_long_short_account_ratio_last | mark_close                           | positioning_like     | basis_premium_like    | basis_premium_like\|positioning_like | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| global_long_short_account_ratio_last | mark_high                            | positioning_like     | basis_premium_like    | basis_premium_like\|positioning_like | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| global_long_short_account_ratio_last | mark_index_basis_bps                 | positioning_like     | basis_premium_like    | basis_premium_like\|positioning_like | regime_neutralizer_interaction_seed | ordinary_alpha_seed                 | probe_high_priority        |
| global_long_short_account_ratio_last | mark_low                             | positioning_like     | basis_premium_like    | basis_premium_like\|positioning_like | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| global_long_short_account_ratio_last | mark_trade_basis_bps                 | positioning_like     | basis_premium_like    | basis_premium_like\|positioning_like | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| global_long_short_account_ratio_last | open_interest_last                   | positioning_like     | positioning_like      | positioning_like\|positioning_like   | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| global_long_short_account_ratio_last | open_interest_mean                   | positioning_like     | positioning_like      | positioning_like\|positioning_like   | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| global_long_short_account_ratio_last | open_interest_value_last             | positioning_like     | positioning_like      | positioning_like\|positioning_like   | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| global_long_short_account_ratio_last | open_interest_value_mean             | positioning_like     | positioning_like      | positioning_like\|positioning_like   | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| global_long_short_account_ratio_last | premium_close                        | positioning_like     | basis_premium_like    | basis_premium_like\|positioning_like | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| global_long_short_account_ratio_last | premium_close_bps                    | positioning_like     | basis_premium_like    | basis_premium_like\|positioning_like | regime_neutralizer_interaction_seed | exploratory_signal_seed             | probe_high_priority        |
| global_long_short_account_ratio_last | taker_buy_quote_volume               | positioning_like     | liquidity_like        | liquidity_like\|positioning_like     | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| global_long_short_account_ratio_last | taker_buy_sell_volume_ratio_last     | positioning_like     | positioning_like      | positioning_like\|positioning_like   | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| global_long_short_account_ratio_last | taker_buy_sell_volume_ratio_mean     | positioning_like     | positioning_like      | positioning_like\|positioning_like   | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| global_long_short_account_ratio_last | top_long_short_account_ratio_last    | positioning_like     | positioning_like      | positioning_like\|positioning_like   | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| global_long_short_account_ratio_last | top_long_short_account_ratio_mean    | positioning_like     | positioning_like      | positioning_like\|positioning_like   | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| global_long_short_account_ratio_last | top_long_short_position_ratio_last   | positioning_like     | positioning_like      | positioning_like\|positioning_like   | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| global_long_short_account_ratio_last | top_long_short_position_ratio_mean   | positioning_like     | positioning_like      | positioning_like\|positioning_like   | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| global_long_short_account_ratio_last | trade_close                          | positioning_like     | price_like            | positioning_like\|price_like         | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| global_long_short_account_ratio_last | trade_count                          | positioning_like     | liquidity_like        | liquidity_like\|positioning_like     | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| global_long_short_account_ratio_last | trade_high                           | positioning_like     | volatility_like       | positioning_like\|volatility_like    | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| global_long_short_account_ratio_last | trade_low                            | positioning_like     | volatility_like       | positioning_like\|volatility_like    | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| global_long_short_account_ratio_last | trade_quote_volume                   | positioning_like     | liquidity_like        | liquidity_like\|positioning_like     | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| global_long_short_account_ratio_last | trade_volume                         | positioning_like     | liquidity_like        | liquidity_like\|positioning_like     | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| global_long_short_account_ratio_last | history_length_hours                 | positioning_like     | generic_numeric       | generic_numeric\|positioning_like    | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| global_long_short_account_ratio_last | index_count                          | positioning_like     | basis_premium_like    | basis_premium_like\|positioning_like | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| global_long_short_account_ratio_last | index_high                           | positioning_like     | basis_premium_like    | basis_premium_like\|positioning_like | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| global_long_short_account_ratio_last | index_low                            | positioning_like     | basis_premium_like    | basis_premium_like\|positioning_like | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| global_long_short_account_ratio_last | index_open                           | positioning_like     | basis_premium_like    | basis_premium_like\|positioning_like | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| global_long_short_account_ratio_last | is_forward_only                      | positioning_like     | generic_numeric       | generic_numeric\|positioning_like    | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| global_long_short_account_ratio_last | is_historical_backfill               | positioning_like     | generic_numeric       | generic_numeric\|positioning_like    | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| global_long_short_account_ratio_last | kline_taker_buy_quote_share          | positioning_like     | state_or_taxonomy     | positioning_like\|state_or_taxonomy  | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| global_long_short_account_ratio_last | liquidity_rank_active_universe       | positioning_like     | liquidity_like        | liquidity_like\|positioning_like     | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| global_long_short_account_ratio_last | listing_age_days                     | positioning_like     | state_or_taxonomy     | positioning_like\|state_or_taxonomy  | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| global_long_short_account_ratio_last | listing_age_hours                    | positioning_like     | state_or_taxonomy     | positioning_like\|state_or_taxonomy  | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| global_long_short_account_ratio_last | log1p_listing_age_days               | positioning_like     | state_or_taxonomy     | positioning_like\|state_or_taxonomy  | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| global_long_short_account_ratio_last | log_quote_volume_168h                | positioning_like     | liquidity_like        | liquidity_like\|positioning_like     | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| global_long_short_account_ratio_last | mark_count                           | positioning_like     | basis_premium_like    | basis_premium_like\|positioning_like | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| global_long_short_account_ratio_last | mark_open                            | positioning_like     | basis_premium_like    | basis_premium_like\|positioning_like | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| global_long_short_account_ratio_last | median_quote_volume_168h             | positioning_like     | liquidity_like        | liquidity_like\|positioning_like     | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| global_long_short_account_ratio_last | metrics_n_5m                         | positioning_like     | positioning_like      | positioning_like\|positioning_like   | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| global_long_short_account_ratio_last | oi_x_price_move_24h                  | positioning_like     | positioning_like      | positioning_like\|positioning_like   | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| global_long_short_account_ratio_last | open_interest_change_24h             | positioning_like     | positioning_like      | positioning_like\|positioning_like   | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
| global_long_short_account_ratio_last | premium_abs_168h                     | positioning_like     | basis_premium_like    | basis_premium_like\|positioning_like | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| global_long_short_account_ratio_last | premium_count                        | positioning_like     | basis_premium_like    | basis_premium_like\|positioning_like | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| global_long_short_account_ratio_last | premium_high                         | positioning_like     | basis_premium_like    | basis_premium_like\|positioning_like | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| global_long_short_account_ratio_last | premium_low                          | positioning_like     | basis_premium_like    | basis_premium_like\|positioning_like | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| global_long_short_account_ratio_last | premium_open                         | positioning_like     | basis_premium_like    | basis_premium_like\|positioning_like | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | probe_high_priority        |
| global_long_short_account_ratio_last | raw_latent_state_id                  | positioning_like     | state_or_taxonomy     | positioning_like\|state_or_taxonomy  | regime_neutralizer_interaction_seed | regime_neutralizer_interaction_seed | diagnostic_or_low_priority |
