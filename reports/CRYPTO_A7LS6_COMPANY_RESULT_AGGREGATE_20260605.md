# CRYPTO A7LS-6 COMPANY DEEP RESULT AGGREGATE

Generated: 2026-06-05T12:38:20Z

## Decision

`PASS_A7LS6_DEEP_NUMERIC_AGGREGATED_CLUES_FOUND_NO_SEARCH_AUTH`

## Summary

- expected_shards: 11
- completed_shards: 11
- pass_shards: 7
- hours_per_split: 2160
- response_rows: 11580
- materialized_activity_ok_total: 579
- non_l7_numeric_clue_rows: 40
- rank_label_diagnostic_rows: 230
- shortlist_rows: 40
- top_non_l7_semantic_pair_share: 0.300
- nonbasis_non_l7_clue_rows: 39
- blockers: <none>

## Shard Summary

| shard   | manifest_path                                                                                             | decision                                                | blockers                | missing_numeric_fields   |   input_blueprint_count |   hours_per_split |   materialized_activity_ok_count |   label_response_rows |   non_l7_numeric_clue_rows |   rank_label_diagnostic_clue_rows |   portfolio_queue_count |   selected_portfolio_queue_count | generated_at         |
|:--------|:----------------------------------------------------------------------------------------------------------|:--------------------------------------------------------|:------------------------|:-------------------------|------------------------:|------------------:|---------------------------------:|----------------------:|---------------------------:|----------------------------------:|------------------------:|---------------------------------:|:---------------------|
| s000    | G:\AlphaFactory_CryptoData\research_runtime\a7ls6_company_deep_numeric\shard_000\a7ls6_s000_manifest.json | PASS_A7LS6S000_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                         |                          |                      64 |              2160 |                               56 |                  1120 |                          1 |                                16 |                      11 |                                9 | 2026-06-05T12:07:08Z |
| s001    | G:\AlphaFactory_CryptoData\research_runtime\a7ls6_company_deep_numeric\shard_001\a7ls6_s001_manifest.json | HOLD_A7LS6S001_NO_NON_L7_NUMERIC_CLUES                  | no_non_l7_numeric_clues |                          |                      64 |              2160 |                               62 |                  1240 |                          0 |                                24 |                      14 |                                9 | 2026-06-05T12:08:37Z |
| s002    | G:\AlphaFactory_CryptoData\research_runtime\a7ls6_company_deep_numeric\shard_002\a7ls6_s002_manifest.json | HOLD_A7LS6S002_NO_NON_L7_NUMERIC_CLUES                  | no_non_l7_numeric_clues |                          |                      64 |              2160 |                               40 |                   800 |                          0 |                                 2 |                       1 |                                1 | 2026-06-05T12:03:29Z |
| s003    | G:\AlphaFactory_CryptoData\research_runtime\a7ls6_company_deep_numeric\shard_003\a7ls6_s003_manifest.json | PASS_A7LS6S003_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                         |                          |                      64 |              2160 |                               64 |                  1280 |                          4 |                                15 |                       7 |                                7 | 2026-06-05T12:08:57Z |
| s004    | G:\AlphaFactory_CryptoData\research_runtime\a7ls6_company_deep_numeric\shard_004\a7ls6_s004_manifest.json | PASS_A7LS6S004_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                         |                          |                      64 |              2160 |                               64 |                  1280 |                          1 |                                16 |                       7 |                                6 | 2026-06-05T12:16:04Z |
| s005    | G:\AlphaFactory_CryptoData\research_runtime\a7ls6_company_deep_numeric\shard_005\a7ls6_s005_manifest.json | HOLD_A7LS6S005_PORTFOLIO_QUEUE_TOO_SMALL                | portfolio_selected_lt_4 |                          |                      64 |              2160 |                               46 |                   920 |                          6 |                                 6 |                       3 |                                3 | 2026-06-05T12:16:54Z |
| s006    | G:\AlphaFactory_CryptoData\research_runtime\a7ls6_company_deep_numeric\shard_006\a7ls6_s006_manifest.json | HOLD_A7LS6S006_PORTFOLIO_QUEUE_TOO_SMALL                | portfolio_selected_lt_4 |                          |                      64 |              2160 |                               46 |                   920 |                          1 |                                 1 |                       2 |                                2 | 2026-06-05T12:19:08Z |
| s007    | G:\AlphaFactory_CryptoData\research_runtime\a7ls6_company_deep_numeric\shard_007\a7ls6_s007_manifest.json | PASS_A7LS6S007_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                         |                          |                      64 |              2160 |                               60 |                  1200 |                          2 |                                 7 |                       5 |                                5 | 2026-06-05T12:22:35Z |
| s008    | G:\AlphaFactory_CryptoData\research_runtime\a7ls6_company_deep_numeric\shard_008\a7ls6_s008_manifest.json | PASS_A7LS6S008_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                         |                          |                      64 |              2160 |                               60 |                  1200 |                          6 |                                48 |                      15 |                               13 | 2026-06-05T12:28:31Z |
| s009    | G:\AlphaFactory_CryptoData\research_runtime\a7ls6_company_deep_numeric\shard_009\a7ls6_s009_manifest.json | PASS_A7LS6S009_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                         |                          |                      64 |              2160 |                               62 |                  1240 |                         12 |                                83 |                      27 |                               13 | 2026-06-05T12:29:45Z |
| s010    | G:\AlphaFactory_CryptoData\research_runtime\a7ls6_company_deep_numeric\shard_010\a7ls6_s010_manifest.json | PASS_A7LS6S010_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                         |                          |                      19 |              2160 |                               19 |                   380 |                          7 |                                12 |                       7 |                                6 | 2026-06-05T12:23:36Z |

## Non-L7 By Label

| label_family                       |   rows |
|:-----------------------------------|-------:|
| L1_cross_sectional_relative_return |     15 |
| L0_raw_forward_return              |     13 |
| L3_liquidity_tier_relative_return  |      8 |
| L5_vol_adjusted_return             |      4 |

## Non-L7 By Semantic Pair

| semantic_pair                                   |   rows |
|:------------------------------------------------|-------:|
| volatility_like                                 |     12 |
| volatility_like|premium_close_bps               |      7 |
| listing_age_like|regime_state                   |      6 |
| volatility_like|age_percentile_active_universe  |      6 |
| basis_premium_like|realized_vol_168h            |      3 |
| open_interest_like|positioning_like             |      2 |
| basis_premium_like                              |      1 |
| open_interest_like|mark_index_basis_bps         |      1 |
| basis_premium_like|volume_volatility_ratio_168h |      1 |
| listing_age_like                                |      1 |

## Response Blockers

| blocker_family             |   rows |
|:---------------------------|-------:|
| pre_may_unstable           |   7885 |
| control_dominated          |   3008 |
| lag_fragile                |    408 |
| rank_label_diagnostic_clue |    230 |
| numeric_clue               |     40 |
| cost_fragile               |      9 |

## Shortlist

| blueprint_id           | expression                                                                                               | semantic_pair                                   | motif             | label_family                       |   label_horizon_h |   control_ratio_premay_max |   cost10_recent_oriented |   deep_followup_score |
|:-----------------------|:---------------------------------------------------------------------------------------------------------|:------------------------------------------------|:------------------|:-----------------------------------|------------------:|---------------------------:|-------------------------:|----------------------:|
| a7ls6_4ec71bffe30b07a9 | Mul(ZScore(Mean(volume_volatility_ratio_168h,168)),Sign(ZScore(Mean(premium_close_bps,168))))            | volatility_like|premium_close_bps               | typed_gate        | L5_vol_adjusted_return             |                24 |                   0.605178 |              0.198674    |             447.78    |
| a7ls6_28acead2e0f4e624 | Delta(mark_index_basis_bps,168)                                                                          | basis_premium_like                              | delta             | L5_vol_adjusted_return             |                 1 |                   0.647853 |              0.113457    |             185.974   |
| a7ls6_1588bade75e26e54 | Mul(ZScore(Mean(realized_vol_168h,168)),Sign(ZScore(Mean(premium_close_bps,168))))                       | volatility_like|premium_close_bps               | typed_gate        | L5_vol_adjusted_return             |                 8 |                   0.994964 |              0.0610941   |             126.755   |
| a7ls6_c4f84c645720612a | Mul(Delta(mark_index_basis_bps,24),ZScore(Mean(volume_volatility_ratio_168h,24)))                        | basis_premium_like|volume_volatility_ratio_168h | typed_interaction | L3_liquidity_tier_relative_return  |                 1 |                   0.398079 |             -0.00121759  |              64.3211  |
| a7ls6_704f70fa6c166248 | ZScore(Mean(volume_volatility_ratio_168h,24))                                                            | volatility_like                                 | zmean             | L0_raw_forward_return              |                24 |                   0.553766 |              0.00373434  |              54.4255  |
| a7ls6_704f70fa6c166248 | ZScore(Mean(volume_volatility_ratio_168h,24))                                                            | volatility_like                                 | zmean             | L1_cross_sectional_relative_return |                24 |                   0.553766 |              0.00373434  |              54.4255  |
| a7ls6_59f0c559993f8406 | Mul(ZScore(Mean(volume_volatility_ratio_168h,24)),Sign(ZScore(Mean(age_percentile_active_universe,24)))) | volatility_like|age_percentile_active_universe  | typed_gate        | L1_cross_sectional_relative_return |                24 |                   0.590789 |              0.00374158  |              50.8364  |
| a7ls6_59f0c559993f8406 | Mul(ZScore(Mean(volume_volatility_ratio_168h,24)),Sign(ZScore(Mean(age_percentile_active_universe,24)))) | volatility_like|age_percentile_active_universe  | typed_gate        | L0_raw_forward_return              |                24 |                   0.692871 |              0.00374158  |              40.6283  |
| a7ls6_2bd140b190452ccd | ZScore(Mean(volume_volatility_ratio_168h,12))                                                            | volatility_like                                 | zmean             | L1_cross_sectional_relative_return |                24 |                   0.786722 |              0.00486314  |              33.5068  |
| a7ls6_2bd140b190452ccd | ZScore(Mean(volume_volatility_ratio_168h,12))                                                            | volatility_like                                 | zmean             | L0_raw_forward_return              |                24 |                   0.786722 |              0.00486314  |              33.5068  |
| a7ls6_5a69ac2d3d0954dd | Mul(ZScore(Mean(premium_close_bps,168)),Sign(ZScore(Mean(realized_vol_168h,168))))                       | basis_premium_like|realized_vol_168h            | typed_gate        | L3_liquidity_tier_relative_return  |                24 |                   0.697477 |             -0.000851595 |              31.4012  |
| a7ls6_8ba492d7173045bc | Mul(ZScore(Mean(top_long_short_account_ratio_last,4)),Sign(ZScore(Mean(mark_index_basis_bps,4))))        | open_interest_like|mark_index_basis_bps         | typed_gate        | L5_vol_adjusted_return             |                 1 |                   0.961118 |              0.01775     |              30.5566  |
| a7ls6_cbc157eb34ecc74e | Mul(ZScore(Mean(age_x_volatility,24)),Sign(ZScore(Mean(premium_abs_168h,24))))                           | listing_age_like|regime_state                   | typed_gate        | L0_raw_forward_return              |                 8 |                   0.721134 |             -0.00119133  |              29.9275  |
| a7ls6_cbc157eb34ecc74e | Mul(ZScore(Mean(age_x_volatility,24)),Sign(ZScore(Mean(premium_abs_168h,24))))                           | listing_age_like|regime_state                   | typed_gate        | L1_cross_sectional_relative_return |                 8 |                   0.721134 |             -0.00119133  |              29.9275  |
| a7ls6_cbc157eb34ecc74e | Mul(ZScore(Mean(age_x_volatility,24)),Sign(ZScore(Mean(premium_abs_168h,24))))                           | listing_age_like|regime_state                   | typed_gate        | L3_liquidity_tier_relative_return  |                 8 |                   0.723853 |             -0.00128441  |              29.4497  |
| a7ls6_4ec71bffe30b07a9 | Mul(ZScore(Mean(volume_volatility_ratio_168h,168)),Sign(ZScore(Mean(premium_close_bps,168))))            | volatility_like|premium_close_bps               | typed_gate        | L1_cross_sectional_relative_return |                 8 |                   0.751121 |             -0.00139953  |              26.4573  |
| a7ls6_21c0f89afdd37ca0 | ZScore(Mean(taker_buy_sell_volume_ratio_last,72))                                                        | open_interest_like|positioning_like             | zmean             | L3_liquidity_tier_relative_return  |                24 |                   0.80387  |              0.00140221  |              24.3516  |
| a7ls6_21c0f89afdd37ca0 | ZScore(Mean(taker_buy_sell_volume_ratio_last,72))                                                        | open_interest_like|positioning_like             | zmean             | L3_liquidity_tier_relative_return  |                 8 |                   0.791347 |             -0.000758864 |              22.3914  |
| a7ls6_cbc157eb34ecc74e | Mul(ZScore(Mean(age_x_volatility,24)),Sign(ZScore(Mean(premium_abs_168h,24))))                           | listing_age_like|regime_state                   | typed_gate        | L0_raw_forward_return              |                 4 |                   0.802026 |             -0.00151544  |              21.3557  |
| a7ls6_cbc157eb34ecc74e | Mul(ZScore(Mean(age_x_volatility,24)),Sign(ZScore(Mean(premium_abs_168h,24))))                           | listing_age_like|regime_state                   | typed_gate        | L1_cross_sectional_relative_return |                 4 |                   0.802026 |             -0.00151544  |              21.3557  |
| a7ls6_5cc8a20f941a59e2 | ZScore(Mean(volume_volatility_ratio_168h,72))                                                            | volatility_like                                 | zmean             | L0_raw_forward_return              |                 8 |                   0.813625 |             -0.000369281 |              20.9534  |
| a7ls6_5cc8a20f941a59e2 | ZScore(Mean(volume_volatility_ratio_168h,72))                                                            | volatility_like                                 | zmean             | L1_cross_sectional_relative_return |                 8 |                   0.813625 |             -0.000369281 |              20.9534  |
| a7ls6_2f08b2d1eae777bb | Mul(ZScore(Mean(volume_volatility_ratio_168h,72)),Sign(ZScore(Mean(age_percentile_active_universe,72)))) | volatility_like|age_percentile_active_universe  | typed_gate        | L1_cross_sectional_relative_return |                 8 |                   0.837651 |             -0.000384587 |              18.4163  |
| a7ls6_2f08b2d1eae777bb | Mul(ZScore(Mean(volume_volatility_ratio_168h,72)),Sign(ZScore(Mean(age_percentile_active_universe,72)))) | volatility_like|age_percentile_active_universe  | typed_gate        | L0_raw_forward_return              |                 8 |                   0.837651 |             -0.000384587 |              18.4163  |
| a7ls6_c31b98e75e807c19 | Mul(ZScore(Mean(realized_vol_24h,168)),Sign(ZScore(Mean(premium_close_bps,168))))                        | volatility_like|premium_close_bps               | typed_gate        | L0_raw_forward_return              |                24 |                   0.852686 |             -0.000139239 |              16.5953  |
| a7ls6_c31b98e75e807c19 | Mul(ZScore(Mean(realized_vol_24h,168)),Sign(ZScore(Mean(premium_close_bps,168))))                        | volatility_like|premium_close_bps               | typed_gate        | L1_cross_sectional_relative_return |                24 |                   0.852686 |             -0.000139239 |              16.5953  |
| a7ls6_5cc8a20f941a59e2 | ZScore(Mean(volume_volatility_ratio_168h,72))                                                            | volatility_like                                 | zmean             | L0_raw_forward_return              |                 4 |                   0.860002 |             -0.00113887  |              15.8626  |
| a7ls6_c31b98e75e807c19 | Mul(ZScore(Mean(realized_vol_24h,168)),Sign(ZScore(Mean(premium_close_bps,168))))                        | volatility_like|premium_close_bps               | typed_gate        | L3_liquidity_tier_relative_return  |                24 |                   0.869855 |             -0.000367699 |              14.6105  |
| a7ls6_5a69ac2d3d0954dd | Mul(ZScore(Mean(premium_close_bps,168)),Sign(ZScore(Mean(realized_vol_168h,168))))                       | basis_premium_like|realized_vol_168h            | typed_gate        | L1_cross_sectional_relative_return |                24 |                   0.877345 |             -0.000586944 |              13.6827  |
| a7ls6_cbc157eb34ecc74e | Mul(ZScore(Mean(age_x_volatility,24)),Sign(ZScore(Mean(premium_abs_168h,24))))                           | listing_age_like|regime_state                   | typed_gate        | L3_liquidity_tier_relative_return  |                 4 |                   0.889567 |             -0.00156532  |              12.462   |
| a7ls6_4a5cfd2698ece591 | CSRank(age_x_liquidity)                                                                                  | listing_age_like                                | rank              | L3_liquidity_tier_relative_return  |                24 |                   0.899488 |             -0.000669867 |              12.2882  |
| a7ls6_5265ad24b18b20e2 | ZScore(Mean(realized_vol_24h,336))                                                                       | volatility_like                                 | zmean             | L0_raw_forward_return              |                24 |                   0.953964 |              0.00148227  |              10.9748  |
| a7ls6_5265ad24b18b20e2 | ZScore(Mean(realized_vol_24h,336))                                                                       | volatility_like                                 | zmean             | L1_cross_sectional_relative_return |                24 |                   0.953964 |              0.00148227  |              10.9748  |
| a7ls6_5265ad24b18b20e2 | ZScore(Mean(realized_vol_24h,336))                                                                       | volatility_like                                 | zmean             | L0_raw_forward_return              |                 8 |                   0.925343 |             -0.000635381 |              10.4591  |
| a7ls6_5265ad24b18b20e2 | ZScore(Mean(realized_vol_24h,336))                                                                       | volatility_like                                 | zmean             | L1_cross_sectional_relative_return |                 8 |                   0.925343 |             -0.000635381 |              10.4591  |
| a7ls6_2f08b2d1eae777bb | Mul(ZScore(Mean(volume_volatility_ratio_168h,72)),Sign(ZScore(Mean(age_percentile_active_universe,72)))) | volatility_like|age_percentile_active_universe  | typed_gate        | L0_raw_forward_return              |                 4 |                   0.93752  |             -0.00115676  |               7.94445 |
| a7ls6_2f08b2d1eae777bb | Mul(ZScore(Mean(volume_volatility_ratio_168h,72)),Sign(ZScore(Mean(age_percentile_active_universe,72)))) | volatility_like|age_percentile_active_universe  | typed_gate        | L1_cross_sectional_relative_return |                 4 |                   0.93752  |             -0.00115676  |               7.94445 |
| a7ls6_5a69ac2d3d0954dd | Mul(ZScore(Mean(premium_close_bps,168)),Sign(ZScore(Mean(realized_vol_168h,168))))                       | basis_premium_like|realized_vol_168h            | typed_gate        | L0_raw_forward_return              |                24 |                   0.939376 |             -0.000586944 |               7.47958 |
| a7ls6_4ec71bffe30b07a9 | Mul(ZScore(Mean(volume_volatility_ratio_168h,168)),Sign(ZScore(Mean(premium_close_bps,168))))            | volatility_like|premium_close_bps               | typed_gate        | L1_cross_sectional_relative_return |                24 |                   0.965881 |              0.000374349 |               7.17504 |
| a7ls6_5cc8a20f941a59e2 | ZScore(Mean(volume_volatility_ratio_168h,72))                                                            | volatility_like                                 | zmean             | L1_cross_sectional_relative_return |                 4 |                   0.949119 |             -0.00113887  |               6.95093 |

## Authorization

- This aggregate does not authorize formula search, large search, alpha proof, shadow, paper, or live.
- May is not used.
