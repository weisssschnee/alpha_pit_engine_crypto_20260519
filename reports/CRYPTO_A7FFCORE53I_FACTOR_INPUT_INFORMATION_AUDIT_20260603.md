# CRYPTO A7FF-CORE53I FACTOR INPUT INFORMATION AUDIT

Generated: 2026-06-03T01:44:40Z

## Decision

`HOLD_A7FFCORE53I_FACTOR_INPUT_REDUNDANCY_RISK`

CORE53I audits factor input information overlap before repaired-target replay. It does not execute replay, generation, search, proof, or promotion.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core53e_preflight": false,
  "authorizes_factor_input_repair": true,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "base_field_count": 39,
  "blockers": [
    "strict_input_type_breadth_low"
  ],
  "candidate_count": 384,
  "decision": "HOLD_A7FFCORE53I_FACTOR_INPUT_REDUNDANCY_RISK",
  "diagnostic_clue_count": 35,
  "diagnostic_field_set_count": 28,
  "diagnostic_input_type_count": 18,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-03T01:44:40Z",
  "input_type_count": 8,
  "source_decision": "PASS_A7FFCORE53_REPLAY_TARGET_REPAIR_CONTRACT_READY_FOR_CORE53E",
  "source_stage": "A7FF-CORE53",
  "stage": "A7FF-CORE53I",
  "strict_clue_count": 1,
  "strict_input_type_count": 1,
  "top_base_field_share": 0.15625,
  "top_input_field_set_share": 0.028645833333333332,
  "top_input_type_share": 0.4348958333333333
}
```

## Base Field Usage

| field                                |   candidate_count | field_type         |   candidate_share |
|:-------------------------------------|------------------:|:-------------------|------------------:|
| funding_rate                         |                60 | funding_like       |        0.15625    |
| global_long_short_account_ratio_last |                58 | positioning_like   |        0.151042   |
| trade_close                          |                53 | price_like         |        0.138021   |
| kline_taker_buy_quote_share          |                47 | liquidity_like     |        0.122396   |
| index_close                          |                44 | price_like         |        0.114583   |
| trade_return_1h                      |                41 | price_like         |        0.106771   |
| trade_high                           |                34 | price_like         |        0.0885417  |
| taker_buy_quote_volume               |                31 | liquidity_like     |        0.0807292  |
| realized_vol_24h                     |                30 | volatility_like    |        0.078125   |
| realized_vol_168h                    |                27 | volatility_like    |        0.0703125  |
| mark_trade_basis_bps                 |                25 | basis_premium_like |        0.0651042  |
| trade_open                           |                24 | price_like         |        0.0625     |
| age_percentile_active_universe       |                22 | state_or_taxonomy  |        0.0572917  |
| funding_rate_abs_168h                |                22 | funding_like       |        0.0572917  |
| age_x_volatility                     |                21 | volatility_like    |        0.0546875  |
| listing_age_days                     |                19 | state_or_taxonomy  |        0.0494792  |
| global_long_short_account_ratio_mean |                17 | positioning_like   |        0.0442708  |
| history_length_hours                 |                13 | generic_numeric    |        0.0338542  |
| taker_buy_sell_volume_ratio_last     |                13 | liquidity_like     |        0.0338542  |
| mark_index_basis_bps                 |                12 | basis_premium_like |        0.03125    |
| trade_quote_volume                   |                11 | liquidity_like     |        0.0286458  |
| mark_close                           |                10 | price_like         |        0.0260417  |
| trade_count                          |                10 | liquidity_like     |        0.0260417  |
| age_x_funding_abs                    |                 8 | funding_like       |        0.0208333  |
| trade_return_24h                     |                 8 | price_like         |        0.0208333  |
| open_interest_mean                   |                 6 | positioning_like   |        0.015625   |
| open_interest_last                   |                 5 | positioning_like   |        0.0130208  |
| execution_time                       |                 4 | generic_numeric    |        0.0104167  |
| premium_close_bps                    |                 4 | basis_premium_like |        0.0104167  |
| source_metrics                       |                 3 | state_or_taxonomy  |        0.0078125  |
| trade_low                            |                 3 | price_like         |        0.0078125  |
| premium_close                        |                 2 | basis_premium_like |        0.00520833 |
| source_market_funding                |                 2 | funding_like       |        0.00520833 |
| taker_buy_sell_volume_ratio_mean     |                 2 | liquidity_like     |        0.00520833 |
| funding_rate_mean_168h               |                 1 | funding_like       |        0.00260417 |
| gap_hours_recent_168h                |                 1 | liquidity_like     |        0.00260417 |
| rolling_coverage_168h                |                 1 | liquidity_like     |        0.00260417 |
| sqrt_listing_age_days                |                 1 | state_or_taxonomy  |        0.00260417 |
| trade_volume                         |                 1 | liquidity_like     |        0.00260417 |

## Field Type Usage

| field_type         |   candidate_count |   candidate_share |
|:-------------------|------------------:|------------------:|
| price_like         |               167 |         0.434896  |
| liquidity_like     |               112 |         0.291667  |
| funding_like       |                83 |         0.216146  |
| positioning_like   |                77 |         0.200521  |
| volatility_like    |                66 |         0.171875  |
| state_or_taxonomy  |                44 |         0.114583  |
| basis_premium_like |                40 |         0.104167  |
| generic_numeric    |                17 |         0.0442708 |

## Input Type Redundancy

| input_type_key                       |   candidate_count |   diagnostic_clue_count |   strict_clue_count |   median_control_ratio |   semantic_pair_count |   operator_count |
|:-------------------------------------|------------------:|------------------------:|--------------------:|-----------------------:|----------------------:|-----------------:|
| price_like                           |                79 |                       6 |                   0 |                1.08712 |                     8 |                7 |
| liquidity_like|price_like            |                38 |                       1 |                   0 |                1.10826 |                     8 |                7 |
| funding_like                         |                21 |                       1 |                   0 |                1.06326 |                     2 |                7 |
| funding_like|liquidity_like          |                18 |                       3 |                   0 |                1.55026 |                     3 |                7 |
| positioning_like                     |                17 |                       1 |                   0 |                1.00023 |                     2 |                5 |
| liquidity_like|state_or_taxonomy     |                15 |                       3 |                   1 |                2.02507 |                     3 |                7 |
| liquidity_like                       |                15 |                       1 |                   0 |                1.00199 |                     5 |                7 |
| volatility_like                      |                15 |                       0 |                   0 |                1.31708 |                     2 |                7 |
| basis_premium_like|price_like        |                13 |                       3 |                   0 |                1.05134 |                     2 |                7 |
| positioning_like|price_like          |                13 |                       1 |                   0 |                1.46962 |                     2 |                6 |
| price_like|volatility_like           |                13 |                       0 |                   0 |                1.37076 |                     3 |                6 |
| basis_premium_like                   |                12 |                       4 |                   0 |                1.00415 |                     2 |                3 |
| liquidity_like|positioning_like      |                12 |                       1 |                   0 |                1.41788 |                     2 |                6 |
| funding_like|positioning_like        |                11 |                       2 |                   0 |                1.01341 |                     1 |                7 |
| funding_like|volatility_like         |                11 |                       2 |                   0 |                1.52101 |                     1 |                7 |
| positioning_like|volatility_like     |                 9 |                       0 |                   0 |                2.87877 |                     1 |                5 |
| funding_like|price_like              |                 8 |                       1 |                   0 |                1.34539 |                     1 |                7 |
| liquidity_like|volatility_like       |                 8 |                       0 |                   0 |                1.61025 |                     2 |                7 |
| generic_numeric|positioning_like     |                 7 |                       0 |                   0 |                1.00654 |                     1 |                4 |
| positioning_like|state_or_taxonomy   |                 6 |                       2 |                   0 |                1.01129 |                     1 |                5 |
| basis_premium_like|liquidity_like    |                 6 |                       1 |                   0 |                1.9082  |                     2 |                2 |
| funding_like|generic_numeric         |                 6 |                       0 |                   0 |                1.02465 |                     1 |                6 |
| funding_like|state_or_taxonomy       |                 6 |                       0 |                   0 |                1.06159 |                     1 |                6 |
| state_or_taxonomy|volatility_like    |                 6 |                       0 |                   0 |                1.34552 |                     2 |                5 |
| generic_numeric|state_or_taxonomy    |                 4 |                       1 |                   0 |                3.3019  |                     1 |                3 |
| basis_premium_like|volatility_like   |                 4 |                       0 |                   0 |                2.22958 |                     1 |                2 |
| state_or_taxonomy                    |                 3 |                       1 |                   0 |                1.39674 |                     2 |                2 |
| price_like|state_or_taxonomy         |                 3 |                       0 |                   0 |                1.28072 |                     1 |                3 |
| basis_premium_like|funding_like      |                 2 |                       0 |                   0 |                2.35915 |                     1 |                1 |
| basis_premium_like|positioning_like  |                 2 |                       0 |                   0 |                2.18376 |                     1 |                2 |
| basis_premium_like|state_or_taxonomy |                 1 |                       0 |                   0 |                5.06788 |                     1 |                1 |

## Field Set Redundancy

| input_field_key                                                           |   candidate_count |   diagnostic_clue_count |   strict_clue_count |   median_control_ratio |   median_clean_label_count | example_expression                                                                                          |
|:--------------------------------------------------------------------------|------------------:|------------------------:|--------------------:|-----------------------:|---------------------------:|:------------------------------------------------------------------------------------------------------------|
| trade_close|trade_open                                                    |                11 |                       1 |                   0 |               1.31692  |                          0 | Mul(Abs(Delta(trade_close,24)),Sign(Delta(trade_open,24)))                                                  |
| trade_high|trade_open                                                     |                10 |                       1 |                   0 |               1.35365  |                          0 | Mul(Abs(Delta(trade_high,24)),Sign(Delta(trade_open,24)))                                                   |
| index_close|mark_index_basis_bps                                          |                 9 |                       3 |                   0 |               1.00341  |                          0 | Mul(Abs(Delta(index_close,4)),Sign(Delta(mark_index_basis_bps,4)))                                          |
| funding_rate|funding_rate_abs_168h                                        |                 9 |                       1 |                   0 |               1.3926   |                          0 | Mul(Abs(Delta(funding_rate,168)),Sign(Delta(funding_rate_abs_168h,168)))                                    |
| funding_rate|taker_buy_quote_volume                                       |                 9 |                       1 |                   0 |               1.79459  |                          0 | Mul(Abs(Delta(funding_rate,168)),Sign(Delta(taker_buy_quote_volume,168)))                                   |
| global_long_short_account_ratio_last|global_long_short_account_ratio_mean |                 9 |                       1 |                   0 |               1.1269   |                          0 | Mul(Abs(Delta(global_long_short_account_ratio_last,8)),Sign(Delta(global_long_short_account_ratio_mean,8))) |
| trade_close|trade_high                                                    |                 9 |                       1 |                   0 |               1.23167  |                          0 | Mul(Abs(Delta(trade_close,24)),Sign(Delta(trade_high,24)))                                                  |
| global_long_short_account_ratio_last|history_length_hours                 |                 7 |                       0 |                   0 |               1.00654  |                          0 | Mul(Abs(Delta(global_long_short_account_ratio_last,8)),Sign(Delta(history_length_hours,8)))                 |
| index_close|realized_vol_24h                                              |                 7 |                       0 |                   0 |               1.69925  |                          0 | Mul(Abs(Delta(index_close,8)),Sign(Delta(realized_vol_24h,8)))                                              |
| kline_taker_buy_quote_share                                               |                 7 |                       0 |                   0 |               1        |                          0 | Abs(Delta(kline_taker_buy_quote_share,4))                                                                   |
| funding_rate|kline_taker_buy_quote_share                                  |                 6 |                       2 |                   0 |               2.59447  |                          0 | Mul(Abs(Delta(funding_rate,168)),Sign(Delta(kline_taker_buy_quote_share,168)))                              |
| age_percentile_active_universe|kline_taker_buy_quote_share                |                 6 |                       1 |                   1 |               2.02536  |                          0 | Mul(Abs(Delta(age_percentile_active_universe,168)),Sign(Delta(kline_taker_buy_quote_share,168)))            |
| age_percentile_active_universe|taker_buy_quote_volume                     |                 6 |                       1 |                   0 |               3.08795  |                          0 | Mul(Abs(Delta(age_percentile_active_universe,4)),Sign(Delta(taker_buy_quote_volume,4)))                     |
| funding_rate|realized_vol_168h                                            |                 6 |                       1 |                   0 |               1.38072  |                          0 | Mul(Abs(Delta(funding_rate,168)),Sign(Delta(realized_vol_168h,168)))                                        |
| kline_taker_buy_quote_share|trade_return_1h                               |                 6 |                       1 |                   0 |               1.00079  |                          0 | Mul(Abs(Delta(kline_taker_buy_quote_share,4)),Sign(Delta(trade_return_1h,4)))                               |
| trade_close|trade_return_1h                                               |                 6 |                       1 |                   0 |               1.00221  |                          0 | Mul(Abs(Delta(trade_close,24)),Sign(Delta(trade_return_1h,24)))                                             |
| age_x_volatility|kline_taker_buy_quote_share                              |                 6 |                       0 |                   0 |               1.49341  |                          0 | Mul(Abs(Delta(age_x_volatility,4)),Sign(Delta(kline_taker_buy_quote_share,4)))                              |
| age_x_volatility|realized_vol_24h                                         |                 6 |                       0 |                   0 |               1.19853  |                          0 | Mul(Abs(Delta(age_x_volatility,4)),Sign(Delta(realized_vol_24h,4)))                                         |
| funding_rate                                                              |                 6 |                       0 |                   0 |               1.06145  |                          0 | Abs(Delta(funding_rate,8))                                                                                  |
| funding_rate|history_length_hours                                         |                 6 |                       0 |                   0 |               1.02465  |                          0 | Mul(Abs(Delta(funding_rate,8)),Sign(Delta(history_length_hours,8)))                                         |
| global_long_short_account_ratio_last                                      |                 6 |                       0 |                   0 |               1.00012  |                          0 | Abs(Delta(global_long_short_account_ratio_last,4))                                                          |
| global_long_short_account_ratio_last|realized_vol_24h                     |                 6 |                       0 |                   0 |               2.47302  |                          0 | Mul(Abs(Delta(global_long_short_account_ratio_last,4)),Sign(Delta(realized_vol_24h,4)))                     |
| trade_close                                                               |                 6 |                       0 |                   0 |               1.06596  |                          0 | Abs(Delta(trade_close,24))                                                                                  |
| trade_high                                                                |                 6 |                       0 |                   0 |               1.19518  |                          0 | Abs(Delta(trade_high,24))                                                                                   |
| trade_high|trade_quote_volume                                             |                 6 |                       0 |                   0 |               1.07728  |                          0 | Mul(Abs(Delta(trade_high,24)),Sign(Delta(trade_quote_volume,24)))                                           |
| trade_return_1h                                                           |                 6 |                       0 |                   0 |               1.00334  |                          0 | Abs(Delta(trade_return_1h,4))                                                                               |
| age_x_funding_abs|trade_return_1h                                         |                 5 |                       1 |                   0 |               1.60528  |                          0 | Mul(Abs(Delta(age_x_funding_abs,4)),Sign(Delta(trade_return_1h,4)))                                         |
| index_close|open_interest_mean                                            |                 5 |                       1 |                   0 |               3.50444  |                          0 | Mul(Abs(Delta(index_close,4)),Sign(Delta(open_interest_mean,4)))                                            |
| mark_close|trade_return_1h                                                |                 5 |                       1 |                   0 |               1.00056  |                          0 | Mul(Abs(Delta(mark_close,8)),Sign(Delta(trade_return_1h,8)))                                                |
| trade_close|trade_return_24h                                              |                 5 |                       1 |                   0 |               1.1603   |                          0 | Mul(Abs(Delta(trade_close,4)),Sign(Delta(trade_return_24h,4)))                                              |
| age_x_volatility|realized_vol_168h                                        |                 5 |                       0 |                   0 |               1.31708  |                          0 | Mul(Abs(Delta(age_x_volatility,4)),Sign(Delta(realized_vol_168h,4)))                                        |
| funding_rate|global_long_short_account_ratio_last                         |                 5 |                       0 |                   0 |               0.995669 |                          0 | Mul(Abs(Delta(funding_rate,168)),Sign(Delta(global_long_short_account_ratio_last,168)))                     |
| funding_rate|listing_age_days                                             |                 5 |                       0 |                   0 |               1.01958  |                          0 | Mul(Abs(Delta(funding_rate,4)),Sign(Delta(listing_age_days,4)))                                             |
| global_long_short_account_ratio_last|kline_taker_buy_quote_share          |                 5 |                       0 |                   0 |               1.35272  |                          0 | Mul(Abs(Delta(global_long_short_account_ratio_last,4)),Sign(Delta(kline_taker_buy_quote_share,4)))          |
| index_close|kline_taker_buy_quote_share                                   |                 5 |                       0 |                   0 |               2.43604  |                          0 | Mul(Abs(Delta(index_close,4)),Sign(Delta(kline_taker_buy_quote_share,4)))                                   |
| index_close|taker_buy_quote_volume                                        |                 5 |                       0 |                   0 |               1.0244   |                          0 | Mul(Abs(Delta(index_close,4)),Sign(Delta(taker_buy_quote_volume,4)))                                        |
| mark_close                                                                |                 5 |                       0 |                   0 |               1.28187  |                          0 | CSRank(Delta(mark_close,4))                                                                                 |
| mark_trade_basis_bps                                                      |                 4 |                       4 |                   0 |               1.00183  |                          4 | CSRank(mark_trade_basis_bps)                                                                                |
| funding_rate|global_long_short_account_ratio_mean                         |                 4 |                       2 |                   0 |               1.17015  |                          1 | Mul(CSRank(funding_rate),Sign(Delta(global_long_short_account_ratio_mean,4)))                               |
| age_percentile_active_universe|execution_time                             |                 4 |                       1 |                   0 |               3.3019   |                          0 | Mul(CSRank(Delta(age_percentile_active_universe,4)),Sign(Delta(execution_time,4)))                          |
| global_long_short_account_ratio_last|taker_buy_quote_volume               |                 4 |                       1 |                   0 |               1.39858  |                          0 | Mul(Abs(Delta(global_long_short_account_ratio_last,4)),Sign(Delta(taker_buy_quote_volume,4)))               |
| mark_trade_basis_bps|taker_buy_quote_volume                               |                 4 |                       1 |                   0 |               1.58472  |                          0 | Mul(CSRank(mark_trade_basis_bps),Sign(Delta(taker_buy_quote_volume,4)))                                     |
| age_x_volatility|listing_age_days                                         |                 4 |                       0 |                   0 |               1.57991  |                          0 | Mul(Abs(Delta(age_x_volatility,4)),Sign(Delta(listing_age_days,4)))                                         |
| global_long_short_account_ratio_last|listing_age_days                     |                 4 |                       0 |                   0 |               1.00654  |                          0 | Mul(Abs(Delta(global_long_short_account_ratio_last,4)),Sign(Delta(listing_age_days,4)))                     |
| global_long_short_account_ratio_last|trade_return_1h                      |                 4 |                       0 |                   0 |               1.03917  |                          0 | Mul(CSRank(global_long_short_account_ratio_last),Sign(Delta(trade_return_1h,4)))                            |
| index_close                                                               |                 4 |                       0 |                   0 |               1.31168  |                          0 | Abs(Delta(index_close,4))                                                                                   |
| trade_close|trade_quote_volume                                            |                 4 |                       0 |                   0 |               1.12285  |                          0 | Mul(CSRank(trade_close),Sign(Delta(trade_quote_volume,4)))                                                  |
| taker_buy_sell_volume_ratio_last                                          |                 3 |                       1 |                   0 |               3.18819  |                          0 | CSRank(taker_buy_sell_volume_ratio_last)                                                                    |
| age_x_funding_abs                                                         |                 3 |                       0 |                   0 |               0.987163 |                          0 | Abs(Delta(age_x_funding_abs,4))                                                                             |
| funding_rate|realized_vol_24h                                             |                 3 |                       0 |                   0 |               1.52101  |                          0 | Mul(CSRank(funding_rate),Sign(Delta(realized_vol_24h,4)))                                                   |
| global_long_short_account_ratio_last|realized_vol_168h                    |                 3 |                       0 |                   0 |               4.47227  |                          0 | Mul(Abs(Delta(global_long_short_account_ratio_last,24)),Sign(Delta(realized_vol_168h,24)))                  |
| index_close|listing_age_days                                              |                 3 |                       0 |                   0 |               1.28072  |                          0 | Mul(Abs(Delta(index_close,4)),Sign(Delta(listing_age_days,4)))                                              |
| index_close|open_interest_last                                            |                 3 |                       0 |                   0 |               1.40101  |                          0 | Mul(Abs(Delta(index_close,24)),Sign(Delta(open_interest_last,24)))                                          |
| mark_trade_basis_bps|premium_close_bps                                    |                 3 |                       0 |                   0 |               1.05086  |                          0 | Mul(CSRank(mark_trade_basis_bps),Sign(Delta(premium_close_bps,72)))                                         |
| mark_trade_basis_bps|realized_vol_24h                                     |                 3 |                       0 |                   0 |               1.55116  |                          0 | Mul(CSRank(mark_trade_basis_bps),Sign(Delta(realized_vol_24h,4)))                                           |
| realized_vol_24h                                                          |                 3 |                       0 |                   0 |               2.85008  |                          0 | CSRank(realized_vol_24h)                                                                                    |
| trade_close|trade_count                                                   |                 3 |                       0 |                   0 |               1.00354  |                          0 | Mul(Abs(Delta(trade_close,24)),Sign(Delta(trade_count,24)))                                                 |
| age_percentile_active_universe                                            |                 2 |                       1 |                   0 |               2.73657  |                          1 | CSRank(Delta(age_percentile_active_universe,4))                                                             |
| funding_rate_abs_168h                                                     |                 2 |                       0 |                   0 |               0.999413 |                          0 | CSRank(funding_rate_abs_168h)                                                                               |
| funding_rate_abs_168h|global_long_short_account_ratio_last                |                 2 |                       0 |                   0 |               1.23785  |                          0 | Mul(Delta(funding_rate_abs_168h,168),ZScore(Delta(global_long_short_account_ratio_last,168)))               |

## Skeleton Redundancy

| expression_skeleton                                     |   candidate_count |   input_field_set_count |   diagnostic_clue_count | example_expression                                                                     |
|:--------------------------------------------------------|------------------:|------------------------:|------------------------:|:---------------------------------------------------------------------------------------|
| Mul(CSRank(Delta(F,4)),Sign(Delta(F,4)))                |                29 |                      29 |                       1 | Mul(CSRank(Delta(index_close,4)),Sign(Delta(mark_index_basis_bps,4)))                  |
| Mul(ZScore(F),Sign(Delta(F,4)))                         |                26 |                      26 |                       6 | Mul(ZScore(index_close),Sign(Delta(mark_index_basis_bps,4)))                           |
| Mul(Clip(ZScore(Delta(F,4)),-3,3),Sign(Delta(F,4)))     |                26 |                      26 |                       4 | Mul(Clip(ZScore(Delta(index_close,4)),-3,3),Sign(Delta(mark_index_basis_bps,4)))       |
| Mul(CSRank(F),Sign(Delta(F,4)))                         |                26 |                      26 |                       3 | Mul(CSRank(mark_trade_basis_bps),Sign(Delta(taker_buy_quote_volume,4)))                |
| Mul(Abs(Delta(F,4)),Sign(Delta(F,4)))                   |                25 |                      25 |                       0 | Mul(Abs(Delta(index_close,4)),Sign(Delta(mark_index_basis_bps,4)))                     |
| Mul(Delta(F,4),ZScore(Delta(F,4)))                      |                23 |                      23 |                       1 | Mul(Delta(mark_trade_basis_bps,4),ZScore(Delta(premium_close_bps,4)))                  |
| Sub(ZScore(Mean(F,4)),ZScore(Mean(F,16)))               |                21 |                      21 |                       2 | Sub(ZScore(Mean(mark_close,4)),ZScore(Mean(mark_close,16)))                            |
| Mul(Clip(ZScore(Delta(F,8)),-3,3),Sign(Delta(F,8)))     |                13 |                      13 |                       1 | Mul(Clip(ZScore(Delta(index_close,8)),-3,3),Sign(Delta(taker_buy_quote_volume,8)))     |
| CSRank(F)                                               |                11 |                      11 |                       1 | CSRank(mark_trade_basis_bps)                                                           |
| Mul(Abs(Delta(F,24)),Sign(Delta(F,24)))                 |                11 |                      11 |                       1 | Mul(Abs(Delta(index_close,24)),Sign(Delta(mark_index_basis_bps,24)))                   |
| Mul(Delta(F,24),ZScore(Delta(F,24)))                    |                11 |                      11 |                       0 | Mul(Delta(mark_trade_basis_bps,24),ZScore(Delta(premium_close_bps,24)))                |
| Mul(CSRank(Delta(F,8)),Sign(Delta(F,8)))                |                10 |                      10 |                       1 | Mul(CSRank(Delta(funding_rate,8)),Sign(Delta(history_length_hours,8)))                 |
| Mul(CSRank(Delta(F,24)),Sign(Delta(F,24)))              |                 9 |                       9 |                       0 | Mul(CSRank(Delta(index_close,24)),Sign(Delta(open_interest_last,24)))                  |
| Mul(Delta(F,168),ZScore(Delta(F,168)))                  |                 9 |                       9 |                       0 | Mul(Delta(mark_trade_basis_bps,168),ZScore(Delta(source_market_funding,168)))          |
| ZScore(F)                                               |                 8 |                       8 |                       1 | ZScore(mark_trade_basis_bps)                                                           |
| CSRank(Delta(F,4))                                      |                 8 |                       8 |                       0 | CSRank(Delta(mark_close,4))                                                            |
| Clip(ZScore(Delta(F,4)),-3,3)                           |                 8 |                       8 |                       0 | Clip(ZScore(Delta(mark_close,4)),-3,3)                                                 |
| Mul(CSRank(F),Sign(Delta(F,8)))                         |                 8 |                       8 |                       0 | Mul(CSRank(mark_trade_basis_bps),Sign(Delta(taker_buy_quote_volume,8)))                |
| Mul(ZScore(F),Sign(Delta(F,8)))                         |                 8 |                       8 |                       0 | Mul(ZScore(index_close),Sign(Delta(open_interest_mean,8)))                             |
| Mul(Abs(Delta(F,168)),Sign(Delta(F,168)))               |                 7 |                       7 |                       2 | Mul(Abs(Delta(funding_rate,168)),Sign(Delta(funding_rate_abs_168h,168)))               |
| Mul(Clip(ZScore(Delta(F,24)),-3,3),Sign(Delta(F,24)))   |                 7 |                       7 |                       1 | Mul(Clip(ZScore(Delta(index_close,24)),-3,3),Sign(Delta(realized_vol_168h,24)))        |
| Mul(ZScore(F),Sign(Delta(F,24)))                        |                 6 |                       6 |                       3 | Mul(ZScore(taker_buy_sell_volume_ratio_last),Sign(Delta(trade_open,24)))               |
| Abs(Delta(F,4))                                         |                 6 |                       6 |                       0 | Abs(Delta(index_close,4))                                                              |
| Mul(Abs(Delta(F,8)),Sign(Delta(F,8)))                   |                 6 |                       6 |                       0 | Mul(Abs(Delta(mark_close,8)),Sign(Delta(trade_return_1h,8)))                           |
| Mul(CSRank(F),Sign(Delta(F,24)))                        |                 6 |                       6 |                       0 | Mul(CSRank(mark_trade_basis_bps),Sign(Delta(trade_close,24)))                          |
| Sub(ZScore(Mean(F,8)),ZScore(Mean(F,32)))               |                 6 |                       6 |                       0 | Sub(ZScore(Mean(mark_close,8)),ZScore(Mean(trade_return_1h,32)))                       |
| Delta(F,4)                                              |                 5 |                       5 |                       1 | Delta(mark_index_basis_bps,4)                                                          |
| Clip(ZScore(Delta(F,24)),-3,3)                          |                 4 |                       4 |                       1 | Clip(ZScore(Delta(index_close,24)),-3,3)                                               |
| CSRank(Delta(F,8))                                      |                 4 |                       4 |                       0 | CSRank(Delta(funding_rate,8))                                                          |
| Sub(ZScore(Mean(F,72)),ZScore(Mean(F,288)))             |                 4 |                       4 |                       0 | Sub(ZScore(Mean(funding_rate,72)),ZScore(Mean(taker_buy_quote_volume,288)))            |
| Mul(Clip(ZScore(Delta(F,168)),-3,3),Sign(Delta(F,168))) |                 3 |                       3 |                       2 | Mul(Clip(ZScore(Delta(funding_rate,168)),-3,3),Sign(Delta(funding_rate_abs_168h,168))) |
| Mul(CSRank(F),Sign(Delta(F,72)))                        |                 3 |                       3 |                       0 | Mul(CSRank(mark_trade_basis_bps),Sign(Delta(premium_close_bps,72)))                    |
| Mul(Delta(F,8),ZScore(Delta(F,8)))                      |                 3 |                       3 |                       0 | Mul(Delta(funding_rate_abs_168h,8),ZScore(Delta(trade_close,8)))                       |
| Sub(ZScore(Mean(F,168)),ZScore(Mean(F,336)))            |                 3 |                       3 |                       0 | Sub(ZScore(Mean(funding_rate,168)),ZScore(Mean(funding_rate,336)))                     |
| Delta(F,8)                                              |                 2 |                       2 |                       1 | Delta(mark_trade_basis_bps,8)                                                          |
| Abs(Delta(F,24))                                        |                 2 |                       2 |                       0 | Abs(Delta(trade_close,24))                                                             |
| Abs(Delta(F,8))                                         |                 2 |                       2 |                       0 | Abs(Delta(funding_rate,8))                                                             |
| CSRank(Delta(F,24))                                     |                 2 |                       2 |                       0 | CSRank(Delta(index_close,24))                                                          |
| Mul(CSRank(Delta(F,168)),Sign(Delta(F,168)))            |                 2 |                       2 |                       0 | Mul(CSRank(Delta(index_close,168)),Sign(Delta(mark_index_basis_bps,168)))              |
| Mul(Clip(ZScore(Delta(F,72)),-3,3),Sign(Delta(F,72)))   |                 2 |                       2 |                       0 | Mul(Clip(ZScore(Delta(index_close,72)),-3,3),Sign(Delta(mark_index_basis_bps,72)))     |

## Clue Pair Overlap

| seed_id_left      | seed_id_right     |   field_jaccard | same_input_type_key   | same_skeleton   | left_semantic_pair                    | right_semantic_pair                   | left_operator   | right_operator   |
|:------------------|:------------------|----------------:|:----------------------|:----------------|:--------------------------------------|:--------------------------------------|:----------------|:-----------------|
| a7ffcore48se_0001 | a7ffcore48se_0545 |        1        | True                  | False           | basis_premium_like                    | basis_premium_like                    | CSRank          | Delta            |
| a7ffcore48se_0001 | a7ffcore48se_1355 |        1        | True                  | False           | basis_premium_like                    | basis_premium_like                    | CSRank          | Identity         |
| a7ffcore48se_0001 | a7ffcore48se_0274 |        1        | True                  | False           | basis_premium_like                    | basis_premium_like                    | CSRank          | Delta            |
| a7ffcore48se_0545 | a7ffcore48se_1355 |        1        | True                  | False           | basis_premium_like                    | basis_premium_like                    | Delta           | Identity         |
| a7ffcore48se_0545 | a7ffcore48se_0274 |        1        | True                  | False           | basis_premium_like                    | basis_premium_like                    | Delta           | Delta            |
| a7ffcore48se_1355 | a7ffcore48se_0274 |        1        | True                  | False           | basis_premium_like                    | basis_premium_like                    | Identity        | Delta            |
| a7ffcore48se_0010 | a7ffcore48se_0824 |        1        | True                  | False           | basis_premium_like|basis_premium_like | basis_premium_like|basis_premium_like | Identity        | Identity         |
| a7ffcore48se_0010 | a7ffcore48se_0013 |        1        | True                  | False           | basis_premium_like|basis_premium_like | basis_premium_like|basis_premium_like | Identity        | WinsorZ          |
| a7ffcore48se_0824 | a7ffcore48se_0013 |        1        | True                  | False           | basis_premium_like|basis_premium_like | basis_premium_like|basis_premium_like | Identity        | WinsorZ          |
| a7ffcore48se_1446 | a7ffcore48se_1704 |        1        | True                  | False           | funding_like|positioning_like         | funding_like|positioning_like         | Identity        | WinsorZ          |
| a7ffcore48se_1188 | a7ffcore48se_0381 |        1        | True                  | False           | funding_like|state_or_taxonomy        | funding_like|state_or_taxonomy        | AbsDelta        | SignedRankDelta  |
| a7ffcore48se_0001 | a7ffcore48se_0029 |        0.5      | False                 | False           | basis_premium_like                    | basis_premium_like|liquidity_like     | CSRank          | CSRank           |
| a7ffcore48se_0545 | a7ffcore48se_0029 |        0.5      | False                 | False           | basis_premium_like                    | basis_premium_like|liquidity_like     | Delta           | CSRank           |
| a7ffcore48se_1355 | a7ffcore48se_0029 |        0.5      | False                 | False           | basis_premium_like                    | basis_premium_like|liquidity_like     | Identity        | CSRank           |
| a7ffcore48se_0029 | a7ffcore48se_0274 |        0.5      | False                 | False           | basis_premium_like|liquidity_like     | basis_premium_like                    | CSRank          | Delta            |
| a7ffcore48se_0681 | a7ffcore48se_0785 |        0.5      | False                 | False           | generic_numeric|state_or_taxonomy     | state_or_taxonomy                     | WinsorZ         | WinsorZ          |
| a7ffcore48se_1509 | a7ffcore48se_0785 |        0.5      | False                 | False           | liquidity_like|state_or_taxonomy      | state_or_taxonomy                     | SpreadShortLong | WinsorZ          |
| a7ffcore48se_1249 | a7ffcore48se_0785 |        0.5      | False                 | False           | liquidity_like|state_or_taxonomy      | state_or_taxonomy                     | WinsorZ         | WinsorZ          |
| a7ffcore48se_0740 | a7ffcore48se_0785 |        0.5      | False                 | False           | positioning_like|state_or_taxonomy    | state_or_taxonomy                     | Identity        | WinsorZ          |
| a7ffcore48se_1540 | a7ffcore48se_0785 |        0.5      | False                 | False           | positioning_like|state_or_taxonomy    | state_or_taxonomy                     | Identity        | WinsorZ          |
| a7ffcore48se_0785 | a7ffcore48se_0248 |        0.5      | False                 | False           | state_or_taxonomy                     | state_or_taxonomy|state_or_taxonomy   | WinsorZ         | SignedRankDelta  |
| a7ffcore48se_1397 | a7ffcore48se_0219 |        0.333333 | True                  | True            | basis_premium_like|price_like         | price_like|price_like                 | Identity        | Identity         |
| a7ffcore48se_0671 | a7ffcore48se_0775 |        0.333333 | True                  | True            | generic_numeric|price_like            | price_like|volatility_like            | Identity        | Identity         |
| a7ffcore48se_0219 | a7ffcore48se_1557 |        0.333333 | True                  | True            | price_like|price_like                 | price_like|price_like                 | Identity        | Identity         |
| a7ffcore48se_0090 | a7ffcore48se_1188 |        0.333333 | True                  | False           | funding_like|liquidity_like           | funding_like|state_or_taxonomy        | WinsorZ         | AbsDelta         |
| a7ffcore48se_0090 | a7ffcore48se_0381 |        0.333333 | True                  | False           | funding_like|liquidity_like           | funding_like|state_or_taxonomy        | WinsorZ         | SignedRankDelta  |
| a7ffcore48se_0671 | a7ffcore48se_0682 |        0.333333 | True                  | False           | generic_numeric|price_like            | generic_numeric|volatility_like       | Identity        | AbsDelta         |
| a7ffcore48se_0671 | a7ffcore48se_0219 |        0.333333 | True                  | False           | generic_numeric|price_like            | price_like|price_like                 | Identity        | Identity         |
| a7ffcore48se_0671 | a7ffcore48se_1557 |        0.333333 | True                  | False           | generic_numeric|price_like            | price_like|price_like                 | Identity        | Identity         |
| a7ffcore48se_0682 | a7ffcore48se_0775 |        0.333333 | True                  | False           | generic_numeric|volatility_like       | price_like|volatility_like            | AbsDelta        | Identity         |
| a7ffcore48se_1509 | a7ffcore48se_1249 |        0.333333 | True                  | False           | liquidity_like|state_or_taxonomy      | liquidity_like|state_or_taxonomy      | SpreadShortLong | WinsorZ          |
| a7ffcore48se_1509 | a7ffcore48se_0248 |        0.333333 | True                  | False           | liquidity_like|state_or_taxonomy      | state_or_taxonomy|state_or_taxonomy   | SpreadShortLong | SignedRankDelta  |
| a7ffcore48se_1249 | a7ffcore48se_0248 |        0.333333 | True                  | False           | liquidity_like|state_or_taxonomy      | state_or_taxonomy|state_or_taxonomy   | WinsorZ         | SignedRankDelta  |
| a7ffcore48se_0740 | a7ffcore48se_1540 |        0.333333 | True                  | False           | positioning_like|state_or_taxonomy    | positioning_like|state_or_taxonomy    | Identity        | Identity         |
| a7ffcore48se_0219 | a7ffcore48se_0775 |        0.333333 | True                  | False           | price_like|price_like                 | price_like|volatility_like            | Identity        | Identity         |
| a7ffcore48se_1557 | a7ffcore48se_0775 |        0.333333 | True                  | False           | price_like|price_like                 | price_like|volatility_like            | Identity        | Identity         |
| a7ffcore48se_0013 | a7ffcore48se_1393 |        0.333333 | False                 | True            | basis_premium_like|basis_premium_like | basis_premium_like|positioning_like   | WinsorZ         | WinsorZ          |
| a7ffcore48se_0029 | a7ffcore48se_0147 |        0.333333 | False                 | True            | basis_premium_like|liquidity_like     | liquidity_like|positioning_like       | CSRank          | CSRank           |
| a7ffcore48se_1446 | a7ffcore48se_1540 |        0.333333 | False                 | True            | funding_like|positioning_like         | positioning_like|state_or_taxonomy    | Identity        | Identity         |
| a7ffcore48se_1188 | a7ffcore48se_1195 |        0.333333 | False                 | True            | funding_like|state_or_taxonomy        | funding_like|volatility_like          | AbsDelta        | AbsDelta         |
| a7ffcore48se_0147 | a7ffcore48se_0182 |        0.333333 | False                 | True            | liquidity_like|positioning_like       | positioning_like|positioning_like     | CSRank          | CSRank           |
| a7ffcore48se_1397 | a7ffcore48se_1557 |        0        | True                  | True            | basis_premium_like|price_like         | price_like|price_like                 | Identity        | Identity         |
| a7ffcore48se_1397 | a7ffcore48se_0671 |        0        | True                  | False           | basis_premium_like|price_like         | generic_numeric|price_like            | Identity        | Identity         |
| a7ffcore48se_1397 | a7ffcore48se_0682 |        0        | True                  | False           | basis_premium_like|price_like         | generic_numeric|volatility_like       | Identity        | AbsDelta         |
| a7ffcore48se_1397 | a7ffcore48se_0775 |        0        | True                  | False           | basis_premium_like|price_like         | price_like|volatility_like            | Identity        | Identity         |
| a7ffcore48se_1195 | a7ffcore48se_1466 |        0        | True                  | False           | funding_like|volatility_like          | funding_like|volatility_like          | AbsDelta        | Delta            |
| a7ffcore48se_0682 | a7ffcore48se_0219 |        0        | True                  | False           | generic_numeric|volatility_like       | price_like|price_like                 | AbsDelta        | Identity         |
| a7ffcore48se_0682 | a7ffcore48se_1557 |        0        | True                  | False           | generic_numeric|volatility_like       | price_like|price_like                 | AbsDelta        | Identity         |
| a7ffcore48se_0010 | a7ffcore48se_1397 |        0        | False                 | True            | basis_premium_like|basis_premium_like | basis_premium_like|price_like         | Identity        | Identity         |
| a7ffcore48se_0010 | a7ffcore48se_1446 |        0        | False                 | True            | basis_premium_like|basis_premium_like | funding_like|positioning_like         | Identity        | Identity         |
| a7ffcore48se_0010 | a7ffcore48se_1540 |        0        | False                 | True            | basis_premium_like|basis_premium_like | positioning_like|state_or_taxonomy    | Identity        | Identity         |
| a7ffcore48se_0010 | a7ffcore48se_0219 |        0        | False                 | True            | basis_premium_like|basis_premium_like | price_like|price_like                 | Identity        | Identity         |
| a7ffcore48se_0010 | a7ffcore48se_1557 |        0        | False                 | True            | basis_premium_like|basis_premium_like | price_like|price_like                 | Identity        | Identity         |
| a7ffcore48se_0013 | a7ffcore48se_0090 |        0        | False                 | True            | basis_premium_like|basis_premium_like | funding_like|liquidity_like           | WinsorZ         | WinsorZ          |
| a7ffcore48se_0013 | a7ffcore48se_1456 |        0        | False                 | True            | basis_premium_like|basis_premium_like | funding_like|price_like               | WinsorZ         | WinsorZ          |
| a7ffcore48se_0029 | a7ffcore48se_0182 |        0        | False                 | True            | basis_premium_like|liquidity_like     | positioning_like|positioning_like     | CSRank          | CSRank           |
| a7ffcore48se_1393 | a7ffcore48se_0090 |        0        | False                 | True            | basis_premium_like|positioning_like   | funding_like|liquidity_like           | WinsorZ         | WinsorZ          |
| a7ffcore48se_1393 | a7ffcore48se_1456 |        0        | False                 | True            | basis_premium_like|positioning_like   | funding_like|price_like               | WinsorZ         | WinsorZ          |
| a7ffcore48se_1397 | a7ffcore48se_1446 |        0        | False                 | True            | basis_premium_like|price_like         | funding_like|positioning_like         | Identity        | Identity         |
| a7ffcore48se_1397 | a7ffcore48se_1540 |        0        | False                 | True            | basis_premium_like|price_like         | positioning_like|state_or_taxonomy    | Identity        | Identity         |
| a7ffcore48se_1159 | a7ffcore48se_1249 |        0        | False                 | True            | funding_like|funding_like             | liquidity_like|state_or_taxonomy      | WinsorZ         | WinsorZ          |
| a7ffcore48se_0090 | a7ffcore48se_1456 |        0        | False                 | True            | funding_like|liquidity_like           | funding_like|price_like               | WinsorZ         | WinsorZ          |
| a7ffcore48se_1446 | a7ffcore48se_0219 |        0        | False                 | True            | funding_like|positioning_like         | price_like|price_like                 | Identity        | Identity         |
| a7ffcore48se_1446 | a7ffcore48se_1557 |        0        | False                 | True            | funding_like|positioning_like         | price_like|price_like                 | Identity        | Identity         |
| a7ffcore48se_0671 | a7ffcore48se_0740 |        0        | False                 | True            | generic_numeric|price_like            | positioning_like|state_or_taxonomy    | Identity        | Identity         |
| a7ffcore48se_1509 | a7ffcore48se_1566 |        0        | False                 | True            | liquidity_like|state_or_taxonomy      | price_like|state_or_taxonomy          | SpreadShortLong | SpreadShortLong  |
| a7ffcore48se_0740 | a7ffcore48se_0775 |        0        | False                 | True            | positioning_like|state_or_taxonomy    | price_like|volatility_like            | Identity        | Identity         |
| a7ffcore48se_1540 | a7ffcore48se_0219 |        0        | False                 | True            | positioning_like|state_or_taxonomy    | price_like|price_like                 | Identity        | Identity         |
| a7ffcore48se_1540 | a7ffcore48se_1557 |        0        | False                 | True            | positioning_like|state_or_taxonomy    | price_like|price_like                 | Identity        | Identity         |

## Authorization

```json
{
  "authorized": {
    "A7FF-CORE53E repaired target preflight": false,
    "A7FF-CORE53IR factor input repair contract": true
  },
  "not_authorized": {
    "alpha_proof": true,
    "formula_search": true,
    "large_search": true,
    "promotion": true,
    "shadow_paper_live": true
  }
}
```
