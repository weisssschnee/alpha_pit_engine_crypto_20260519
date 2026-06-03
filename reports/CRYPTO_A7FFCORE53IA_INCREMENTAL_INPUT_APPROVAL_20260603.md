# CRYPTO A7FF-CORE53IA INCREMENTAL INPUT APPROVAL

Generated: 2026-06-03T02:05:51Z

## Decision

`PASS_A7FFCORE53IA_INCREMENTAL_INPUT_APPROVAL_BUILT`

CORE53IA approves or blocks field inputs before queue construction. It audits incremental information directly at the field/factor-input layer; it does not execute replay, generation, search, proof, or promotion.

## Manifest

```json
{
  "approved_signal_input_count": 26,
  "authorizes_alpha_proof": false,
  "authorizes_core54_queue_builder": true,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "blocked_input_count": 6,
  "condition_only_input_count": 4,
  "decision": "PASS_A7FFCORE53IA_INCREMENTAL_INPUT_APPROVAL_BUILT",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-03T02:05:51Z",
  "high_corr_pair_count_abs_ge_0_95": 23,
  "large_info_cluster_count": 7,
  "numeric_field_count": 36,
  "sample_rows": 1353903,
  "sample_timestamps": 4096,
  "source_decision": "HOLD_A7FFCORE53I_FACTOR_INPUT_REDUNDANCY_RISK",
  "source_stage": "A7FF-CORE53I",
  "stage": "A7FF-CORE53IA"
}
```

## Approval Summary

| semantic_type      | input_approval                                 |   field_count |
|:-------------------|:-----------------------------------------------|--------------:|
| basis_premium_like | approved_incremental_signal_input              |             2 |
| basis_premium_like | approved_redundant_cluster_member_requires_cap |             2 |
| funding_like       | blocked_low_coverage                           |             4 |
| liquidity_like     | approved_incremental_signal_input              |             5 |
| liquidity_like     | approved_redundant_cluster_member_requires_cap |             2 |
| liquidity_like     | blocked_low_cross_sectional_variation          |             2 |
| positioning_like   | approved_redundant_cluster_member_requires_cap |             4 |
| price_like         | approved_redundant_cluster_member_requires_cap |             6 |
| price_like         | approved_incremental_signal_input              |             2 |
| state_or_taxonomy  | approved_condition_or_neutralizer_only         |             4 |
| volatility_like    | approved_incremental_signal_input              |             3 |

## Field Approval Ledger

| field                                | semantic_type      | info_cluster_id   |   cluster_size |   coverage |   unique_count |   median_xs_std |   active_xs_share | input_approval                                 | approval_reason                     |
|:-------------------------------------|:-------------------|:------------------|---------------:|-----------:|---------------:|----------------:|------------------:|:-----------------------------------------------|:------------------------------------|
| age_percentile_active_universe       | state_or_taxonomy  | ic_007            |              1 |   0.956964 |          31395 |     0.259583    |         0.961426  | approved_condition_or_neutralizer_only         | state_taxonomy_not_standalone_alpha |
| age_x_funding_abs                    | funding_like       | ic_002            |              2 |   0.55777  |         697525 |     0.00117507  |         0.967041  | blocked_low_coverage                           | coverage_below_70pct                |
| age_x_volatility                     | volatility_like    | ic_008            |              1 |   0.953435 |        1290112 |     0.0236728   |         0.968994  | approved_incremental_signal_input              | incremental_enough                  |
| funding_rate                         | funding_like       | ic_009            |              1 |   0.195481 |          63040 |     0.000435483 |         0.515381  | blocked_low_coverage                           | coverage_below_70pct                |
| funding_rate_abs_168h                | funding_like       | ic_002            |              2 |   0.55777  |         407823 |     0.000261101 |         0.967041  | blocked_low_coverage                           | coverage_below_70pct                |
| funding_rate_mean_168h               | funding_like       | ic_010            |              1 |   0.55777  |         461079 |     0.000274661 |         0.967041  | blocked_low_coverage                           | coverage_below_70pct                |
| gap_hours_recent_168h                | liquidity_like     | ic_011            |              1 |   0.955236 |              6 |     0           |         0.0639648 | blocked_low_cross_sectional_variation          | low_cross_sectional_variation       |
| global_long_short_account_ratio_last | positioning_like   | ic_003            |              2 |   0.999094 |        1119484 |     0.790512    |         0.999512  | approved_redundant_cluster_member_requires_cap | high_corr_cluster_member            |
| global_long_short_account_ratio_mean | positioning_like   | ic_003            |              2 |   0.999094 |        1352518 |     0.789469    |         0.999512  | approved_redundant_cluster_member_requires_cap | high_corr_cluster_member            |
| history_length_hours                 | state_or_taxonomy  | ic_001            |              3 |   0.956964 |          19748 |  3661.52        |         0.961426  | approved_condition_or_neutralizer_only         | state_taxonomy_not_standalone_alpha |
| index_close                          | price_like         | ic_000            |              6 |   0.998203 |        1312576 |  4635.74        |         0.999756  | approved_redundant_cluster_member_requires_cap | high_corr_cluster_member            |
| kline_taker_buy_quote_share          | liquidity_like     | ic_012            |              1 |   0.998841 |        1352334 |     0.0601802   |         0.999512  | approved_incremental_signal_input              | incremental_enough                  |
| listing_age_days                     | state_or_taxonomy  | ic_001            |              3 |   0.956964 |          19748 |   152.563       |         0.961426  | approved_condition_or_neutralizer_only         | state_taxonomy_not_standalone_alpha |
| mark_close                           | price_like         | ic_000            |              6 |   0.999315 |         903561 |  4633.31        |         0.999756  | approved_redundant_cluster_member_requires_cap | high_corr_cluster_member            |
| mark_index_basis_bps                 | basis_premium_like | ic_013            |              1 |   0.997885 |        1326802 |     8.68093     |         0.999756  | approved_incremental_signal_input              | incremental_enough                  |
| mark_trade_basis_bps                 | basis_premium_like | ic_014            |              1 |   0.999315 |         851618 |     4.52134     |         0.999756  | approved_incremental_signal_input              | incremental_enough                  |
| open_interest_last                   | positioning_like   | ic_004            |              2 |   0.999094 |        1348952 |     9.10555e+09 |         0.999512  | approved_redundant_cluster_member_requires_cap | high_corr_cluster_member            |
| open_interest_mean                   | positioning_like   | ic_004            |              2 |   0.999094 |        1352397 |     9.10612e+09 |         0.999512  | approved_redundant_cluster_member_requires_cap | high_corr_cluster_member            |
| premium_close                        | basis_premium_like | ic_005            |              2 |   0.998929 |         318522 |     0.000690607 |         0.999756  | approved_redundant_cluster_member_requires_cap | high_corr_cluster_member            |
| premium_close_bps                    | basis_premium_like | ic_005            |              2 |   0.998929 |         321480 |     6.90607     |         0.999756  | approved_redundant_cluster_member_requires_cap | high_corr_cluster_member            |
| realized_vol_168h                    | volatility_like    | ic_015            |              1 |   0.953435 |        1290106 |     0.00565772  |         0.968994  | approved_incremental_signal_input              | incremental_enough                  |
| realized_vol_24h                     | volatility_like    | ic_016            |              1 |   0.956012 |        1293520 |     0.00604242  |         0.970703  | approved_incremental_signal_input              | incremental_enough                  |
| rolling_coverage_168h                | liquidity_like     | ic_017            |              1 |   0.955236 |            165 |     0           |         0.283203  | blocked_low_cross_sectional_variation          | low_cross_sectional_variation       |
| sqrt_listing_age_days                | state_or_taxonomy  | ic_001            |              3 |   0.956964 |          19748 |     5.49404     |         0.961426  | approved_condition_or_neutralizer_only         | state_taxonomy_not_standalone_alpha |
| taker_buy_quote_volume               | liquidity_like     | ic_006            |              2 |   0.999632 |        1352304 |     1.80517e+07 |         0.999512  | approved_redundant_cluster_member_requires_cap | high_corr_cluster_member            |
| taker_buy_sell_volume_ratio_last     | liquidity_like     | ic_018            |              1 |   0.999094 |        1060586 |     1.35257     |         0.999512  | approved_incremental_signal_input              | incremental_enough                  |
| taker_buy_sell_volume_ratio_mean     | liquidity_like     | ic_019            |              1 |   0.999094 |        1319551 |     0.921572    |         0.999512  | approved_incremental_signal_input              | incremental_enough                  |
| trade_close                          | price_like         | ic_000            |              6 |   0.999632 |         211055 |  4630.56        |         0.999756  | approved_redundant_cluster_member_requires_cap | high_corr_cluster_member            |
| trade_count                          | liquidity_like     | ic_020            |              1 |   0.999632 |         110111 | 32111.6         |         0.999512  | approved_incremental_signal_input              | incremental_enough                  |
| trade_high                           | price_like         | ic_000            |              6 |   0.999632 |         209530 |  4645.67        |         0.999756  | approved_redundant_cluster_member_requires_cap | high_corr_cluster_member            |
| trade_low                            | price_like         | ic_000            |              6 |   0.999632 |         206451 |  4617.29        |         0.999756  | approved_redundant_cluster_member_requires_cap | high_corr_cluster_member            |
| trade_open                           | price_like         | ic_000            |              6 |   0.999632 |         211638 |  4629.16        |         0.999756  | approved_redundant_cluster_member_requires_cap | high_corr_cluster_member            |
| trade_quote_volume                   | liquidity_like     | ic_006            |              2 |   0.999632 |        1352326 |     3.61299e+07 |         0.999512  | approved_redundant_cluster_member_requires_cap | high_corr_cluster_member            |
| trade_return_1h                      | price_like         | ic_021            |              1 |   0.999448 |         838764 |     0.00931955  |         0.999268  | approved_incremental_signal_input              | incremental_enough                  |
| trade_return_24h                     | price_like         | ic_022            |              1 |   0.955203 |        1100999 |     0.0467318   |         0.970215  | approved_incremental_signal_input              | incremental_enough                  |
| trade_volume                         | liquidity_like     | ic_023            |              1 |   0.999632 |        1304394 |     1.37828e+09 |         0.999512  | approved_incremental_signal_input              | incremental_enough                  |

## Information Clusters

| info_cluster_id   |   field_count | semantic_types     |   approved_signal_count |   condition_only_count |   blocked_count | fields                                                                    |
|:------------------|--------------:|:-------------------|------------------------:|-----------------------:|----------------:|:--------------------------------------------------------------------------|
| ic_000            |             6 | price_like         |                       0 |                      0 |               0 | index_close|mark_close|trade_close|trade_high|trade_low|trade_open        |
| ic_001            |             3 | state_or_taxonomy  |                       0 |                      3 |               0 | history_length_hours|listing_age_days|sqrt_listing_age_days               |
| ic_002            |             2 | funding_like       |                       0 |                      0 |               2 | age_x_funding_abs|funding_rate_abs_168h                                   |
| ic_003            |             2 | positioning_like   |                       0 |                      0 |               0 | global_long_short_account_ratio_last|global_long_short_account_ratio_mean |
| ic_004            |             2 | positioning_like   |                       0 |                      0 |               0 | open_interest_last|open_interest_mean                                     |
| ic_005            |             2 | basis_premium_like |                       0 |                      0 |               0 | premium_close|premium_close_bps                                           |
| ic_006            |             2 | liquidity_like     |                       0 |                      0 |               0 | taker_buy_quote_volume|trade_quote_volume                                 |
| ic_008            |             1 | volatility_like    |                       1 |                      0 |               0 | age_x_volatility                                                          |
| ic_012            |             1 | liquidity_like     |                       1 |                      0 |               0 | kline_taker_buy_quote_share                                               |
| ic_013            |             1 | basis_premium_like |                       1 |                      0 |               0 | mark_index_basis_bps                                                      |
| ic_014            |             1 | basis_premium_like |                       1 |                      0 |               0 | mark_trade_basis_bps                                                      |
| ic_015            |             1 | volatility_like    |                       1 |                      0 |               0 | realized_vol_168h                                                         |
| ic_016            |             1 | volatility_like    |                       1 |                      0 |               0 | realized_vol_24h                                                          |
| ic_018            |             1 | liquidity_like     |                       1 |                      0 |               0 | taker_buy_sell_volume_ratio_last                                          |
| ic_019            |             1 | liquidity_like     |                       1 |                      0 |               0 | taker_buy_sell_volume_ratio_mean                                          |
| ic_020            |             1 | liquidity_like     |                       1 |                      0 |               0 | trade_count                                                               |
| ic_021            |             1 | price_like         |                       1 |                      0 |               0 | trade_return_1h                                                           |
| ic_022            |             1 | price_like         |                       1 |                      0 |               0 | trade_return_24h                                                          |
| ic_023            |             1 | liquidity_like     |                       1 |                      0 |               0 | trade_volume                                                              |
| ic_007            |             1 | state_or_taxonomy  |                       0 |                      1 |               0 | age_percentile_active_universe                                            |
| ic_009            |             1 | funding_like       |                       0 |                      0 |               1 | funding_rate                                                              |
| ic_010            |             1 | funding_like       |                       0 |                      0 |               1 | funding_rate_mean_168h                                                    |
| ic_011            |             1 | liquidity_like     |                       0 |                      0 |               1 | gap_hours_recent_168h                                                     |
| ic_017            |             1 | liquidity_like     |                       0 |                      0 |               1 | rolling_coverage_168h                                                     |

## High Correlation Field Pairs

| field_left                           | field_right                          |   abs_corr |     corr | semantic_left      | semantic_right     |
|:-------------------------------------|:-------------------------------------|-----------:|---------:|:-------------------|:-------------------|
| premium_close                        | premium_close_bps                    |   1        | 1        | basis_premium_like | basis_premium_like |
| mark_close                           | trade_close                          |   1        | 1        | price_like         | price_like         |
| history_length_hours                 | listing_age_days                     |   1        | 1        | state_or_taxonomy  | state_or_taxonomy  |
| index_close                          | mark_close                           |   1        | 1        | price_like         | price_like         |
| index_close                          | trade_close                          |   1        | 1        | price_like         | price_like         |
| mark_close                           | trade_high                           |   0.999993 | 0.999993 | price_like         | price_like         |
| trade_close                          | trade_high                           |   0.999993 | 0.999993 | price_like         | price_like         |
| index_close                          | trade_high                           |   0.999993 | 0.999993 | price_like         | price_like         |
| index_close                          | trade_low                            |   0.999993 | 0.999993 | price_like         | price_like         |
| mark_close                           | trade_low                            |   0.999992 | 0.999992 | price_like         | price_like         |
| trade_close                          | trade_low                            |   0.999992 | 0.999992 | price_like         | price_like         |
| trade_high                           | trade_open                           |   0.999992 | 0.999992 | price_like         | price_like         |
| trade_low                            | trade_open                           |   0.99999  | 0.99999  | price_like         | price_like         |
| mark_close                           | trade_open                           |   0.999988 | 0.999988 | price_like         | price_like         |
| trade_close                          | trade_open                           |   0.999988 | 0.999988 | price_like         | price_like         |
| index_close                          | trade_open                           |   0.999988 | 0.999988 | price_like         | price_like         |
| trade_high                           | trade_low                            |   0.999985 | 0.999985 | price_like         | price_like         |
| open_interest_last                   | open_interest_mean                   |   0.999866 | 0.999866 | positioning_like   | positioning_like   |
| global_long_short_account_ratio_last | global_long_short_account_ratio_mean |   0.999124 | 0.999124 | positioning_like   | positioning_like   |
| taker_buy_quote_volume               | trade_quote_volume                   |   0.996679 | 0.996679 | liquidity_like     | liquidity_like     |
| listing_age_days                     | sqrt_listing_age_days                |   0.976677 | 0.976677 | state_or_taxonomy  | state_or_taxonomy  |
| history_length_hours                 | sqrt_listing_age_days                |   0.976676 | 0.976676 | state_or_taxonomy  | state_or_taxonomy  |
| age_x_funding_abs                    | funding_rate_abs_168h                |   0.950289 | 0.950289 | funding_like       | funding_like       |

## Authorization

```json
{
  "authorized": {
    "A7FF-CORE54 queue builder using input approval ledger": true
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
