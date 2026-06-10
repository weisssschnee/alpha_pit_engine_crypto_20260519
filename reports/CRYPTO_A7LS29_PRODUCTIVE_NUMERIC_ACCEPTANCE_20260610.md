# CRYPTO A7LS29 Productive Numeric Acceptance 20260610

## Decision

`PASS_A7LS29_PRODUCTIVE_NUMERIC_ACCEPTED_NO_SEARCH_AUTH`

A7LS29 completed all 12 company-machine numeric shards and fixes the A7LS28B portfolio-queue collapse. This is numeric evidence and queue validation only. It does not authorize alpha proof, search promotion, shadow, paper, or live execution.

## Counts

- queue_rows: 6144
- shard_count: 12
- pass_count: 12
- hold_count: 0
- input_blueprint_count_total: 6144
- activity_ok_total: 6123
- missing_numeric_field_shards: 0
- materialization_eval_fail_count: 0
- non_l7_numeric_clue_rows_total: 11023
- rank_label_diagnostic_clue_rows_total: 6531
- portfolio_queue_rows_total: 3882
- selected_portfolio_queue_rows_total: 291
- selected_skeleton_unique: 161
- selected_top_skeleton_share: 0.0137

## Shard Summary

| shard_id        | decision                                                            |   materialized_activity_ok_count |   non_l7_numeric_clue_rows |   rank_label_diagnostic_clue_rows |   portfolio_queue_count |   selected_portfolio_queue_count |
|:----------------|:--------------------------------------------------------------------|---------------------------------:|---------------------------:|----------------------------------:|------------------------:|---------------------------------:|
| a7ls29_num_s000 | PASS_A7LS29a7ls29_num_s000_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                              512 |                        964 |                               335 |                     352 |                               24 |
| a7ls29_num_s001 | PASS_A7LS29a7ls29_num_s001_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                              512 |                       1056 |                               321 |                     345 |                               24 |
| a7ls29_num_s002 | PASS_A7LS29a7ls29_num_s002_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                              512 |                        977 |                               256 |                     294 |                               24 |
| a7ls29_num_s003 | PASS_A7LS29a7ls29_num_s003_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                              512 |                        268 |                                14 |                     131 |                               13 |
| a7ls29_num_s004 | PASS_A7LS29a7ls29_num_s004_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                              512 |                        734 |                               142 |                     301 |                               30 |
| a7ls29_num_s005 | PASS_A7LS29a7ls29_num_s005_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                              512 |                        690 |                                 5 |                     301 |                               17 |
| a7ls29_num_s006 | PASS_A7LS29a7ls29_num_s006_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                              512 |                        486 |                                 4 |                     224 |                               17 |
| a7ls29_num_s007 | PASS_A7LS29a7ls29_num_s007_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                              512 |                       1015 |                               698 |                     320 |                               35 |
| a7ls29_num_s008 | PASS_A7LS29a7ls29_num_s008_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                              512 |                        965 |                              1340 |                     417 |                               24 |
| a7ls29_num_s009 | PASS_A7LS29a7ls29_num_s009_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                              506 |                       1338 |                              1298 |                     407 |                               37 |
| a7ls29_num_s010 | PASS_A7LS29a7ls29_num_s010_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                              497 |                       1956 |                              1565 |                     478 |                               24 |
| a7ls29_num_s011 | PASS_A7LS29a7ls29_num_s011_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                              512 |                        574 |                               553 |                     312 |                               22 |

## Selected Family Summary

| semantic_pair                                          | motif               | label_family                      |   selected_rows |
|:-------------------------------------------------------|:--------------------|:----------------------------------|----------------:|
| open_interest_like\|positioning_like\|listing_age_like | seed_sub            | L7_ranked_future_return           |              68 |
| open_interest_like\|positioning_like\|regime_state     | seed_gated_sign     | L3_liquidity_tier_relative_return |              55 |
| basis_premium_like\|positioning_like                   | spread_rank         | L5_vol_adjusted_return            |              36 |
| basis_premium_like\|positioning_like                   | safe_div_abs        | L5_vol_adjusted_return            |              26 |
| basis_premium_like\|age_x_volatility\|positioning_like | seed_sub            | L7_ranked_future_return           |              25 |
| basis_premium_like\|positioning_like                   | signed_spread       | L5_vol_adjusted_return            |              15 |
| basis_premium_like\|age_x_volatility\|positioning_like | seed_mul            | L7_ranked_future_return           |              14 |
| basis_premium_like\|positioning_like                   | sub                 | L5_vol_adjusted_return            |              13 |
| open_interest_like\|positioning_like                   | smooth_mul          | L5_vol_adjusted_return            |              12 |
| basis_premium_like\|positioning_like                   | mean_reversion_gate | L5_vol_adjusted_return            |              11 |
| open_interest_like\|positioning_like                   | safe_div_abs        | L7_ranked_future_return           |               7 |
| basis_premium_like\|positioning_like                   | spread_rank         | L7_ranked_future_return           |               3 |
| open_interest_like\|positioning_like                   | safe_div_abs        | L5_vol_adjusted_return            |               3 |
| open_interest_like\|positioning_like\|regime_state     | seed_gated_sign     | L7_ranked_future_return           |               3 |

## Selected Label Summary

| label_family                      |   label_horizon_h |   selected_rows |
|:----------------------------------|------------------:|----------------:|
| L7_ranked_future_return           |                24 |             112 |
| L5_vol_adjusted_return            |                 4 |              53 |
| L3_liquidity_tier_relative_return |                24 |              53 |
| L5_vol_adjusted_return            |                24 |              30 |
| L5_vol_adjusted_return            |                 8 |              27 |
| L5_vol_adjusted_return            |                 1 |               6 |
| L7_ranked_future_return           |                 1 |               3 |
| L7_ranked_future_return           |                 4 |               3 |
| L7_ranked_future_return           |                 8 |               2 |
| L3_liquidity_tier_relative_return |                 8 |               1 |
| L3_liquidity_tier_relative_return |                 4 |               1 |

## Top Selected Queue

| blueprint_id            | semantic_pair                        | motif         | label_family           |   label_horizon_h |   score_no_may |   control_ratio_premay_max |   cost10_recent_oriented |   robust_median_tstat_floor | skeleton_key                                                      | expression                                                                                                                                                            |
|:------------------------|:-------------------------------------|:--------------|:-----------------------|------------------:|---------------:|---------------------------:|-------------------------:|----------------------------:|:------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| a7ls29_d4af9426b9fa5cf6 | basis_premium_like\|positioning_like | safe_div_abs  | L5_vol_adjusted_return |                24 |        330.637 |                   0.7086   |                 0.323345 |                    0.692637 | basis_premium_like\|positioning_like\|safe_div_abs\|e740a0aa371c  | Neg(SafeDiv(TSRank(mark_index_basis_bps,8),Abs(Decay(account_position_divergence,168))))                                                                              |
| a7ls29_22ca233fe0f59e3a | basis_premium_like\|positioning_like | safe_div_abs  | L5_vol_adjusted_return |                24 |        328.687 |                   0.741036 |                 0.321428 |                    0.59263  | basis_premium_like\|positioning_like\|safe_div_abs\|a92a45f756ed  | ZScore(SafeDiv(TSRank(mark_index_basis_bps,8),Abs(Decay(account_position_divergence,168))))                                                                           |
| a7ls29_3d8242e194d7ab89 | basis_premium_like\|positioning_like | safe_div_abs  | L5_vol_adjusted_return |                24 |        316.852 |                   0.842905 |                 0.309695 |                    0.73207  | basis_premium_like\|positioning_like\|safe_div_abs\|044c7da54852  | SafeDiv(TSRank(mark_index_basis_bps,6),Abs(Decay(account_position_divergence,504)))                                                                                   |
| a7ls29_9f3fc9dd327a93c2 | basis_premium_like\|positioning_like | safe_div_abs  | L5_vol_adjusted_return |                24 |        283.401 |                   0.645869 |                 0.276047 |                    1.01098  | basis_premium_like\|positioning_like\|safe_div_abs\|044c7da54852  | SafeDiv(TSRank(mark_index_basis_bps,24),Abs(Decay(account_position_divergence,36)))                                                                                   |
| a7ls29_083be2c2aa178e01 | open_interest_like\|positioning_like | safe_div_abs  | L5_vol_adjusted_return |                24 |        277.224 |                   0.534764 |                 0.269759 |                    0.33635  | open_interest_like\|positioning_like\|safe_div_abs\|ede788b53b6e  | ZScore(SafeDiv(Abs(ZScore(Mean(open_interest_last,8))),Abs(Decay(account_position_divergence,120))))                                                                  |
| a7ls29_ecad2b755fb4f7de | open_interest_like\|positioning_like | safe_div_abs  | L5_vol_adjusted_return |                24 |        272.01  |                   0.803253 |                 0.264814 |                    0.55307  | open_interest_like\|positioning_like\|safe_div_abs\|cc4d01d2849f  | SafeDiv(Abs(ZScore(Mean(open_interest_last,48))),Abs(Decay(account_position_divergence,120)))                                                                         |
| a7ls29_6c34df4b090ce558 | basis_premium_like\|positioning_like | spread_rank   | L5_vol_adjusted_return |                 8 |        227.564 |                   0.915092 |                 0.220479 |                    0.803788 | basis_premium_like\|positioning_like\|spread_rank\|121a81cf1af0   | Sub(CSRank(TSRank(mark_index_basis_bps,72)),CSRank(ZScore(Mean(global_long_short_account_ratio_mean,4))))                                                             |
| a7ls29_dbc460a86fefc277 | basis_premium_like\|positioning_like | signed_spread | L5_vol_adjusted_return |                 8 |        227.425 |                   0.929702 |                 0.220355 |                    0.951157 | basis_premium_like\|positioning_like\|signed_spread\|efbfa119cac1 | CSRank(Mul(Sub(CSRank(Delta(mark_index_basis_bps,48)),CSRank(Decay(global_long_short_account_ratio_mean,6))),Sign(Decay(global_long_short_account_ratio_mean,6))))    |
| a7ls29_a209b2962c40485e | basis_premium_like\|positioning_like | spread_rank   | L5_vol_adjusted_return |                 8 |        227.425 |                   0.929702 |                 0.220355 |                    0.951157 | basis_premium_like\|positioning_like\|spread_rank\|f6895cda2696   | Sub(CSRank(Delta(mark_index_basis_bps,48)),CSRank(Decay(global_long_short_account_ratio_mean,6)))                                                                     |
| a7ls29_5abc27db3da42c1c | basis_premium_like\|positioning_like | signed_spread | L5_vol_adjusted_return |                 8 |        227.425 |                   0.929702 |                 0.220355 |                    0.951157 | basis_premium_like\|positioning_like\|signed_spread\|39537d3da263 | Mul(Sub(CSRank(Delta(mark_index_basis_bps,48)),CSRank(Decay(global_long_short_account_ratio_mean,6))),Sign(Decay(global_long_short_account_ratio_mean,6)))            |
| a7ls29_7a33109eade5fea8 | basis_premium_like\|positioning_like | signed_spread | L5_vol_adjusted_return |                 8 |        227.425 |                   0.929702 |                 0.220355 |                    0.951157 | basis_premium_like\|positioning_like\|signed_spread\|d8a4b8811704 | Clip(Mul(Sub(CSRank(Delta(mark_index_basis_bps,48)),CSRank(Decay(global_long_short_account_ratio_mean,6))),Sign(Decay(global_long_short_account_ratio_mean,6))),-3,3) |
| a7ls29_d5057db39b3c0605 | basis_premium_like\|positioning_like | spread_rank   | L5_vol_adjusted_return |                 8 |        226.803 |                   0.881226 |                 0.219685 |                    1.14828  | basis_premium_like\|positioning_like\|spread_rank\|2807c7910579   | Sub(CSRank(TSRank(mark_index_basis_bps,96)),CSRank(Decay(global_long_short_account_ratio_last,3)))                                                                    |
| a7ls29_e8ea6562f5afd636 | basis_premium_like\|positioning_like | signed_spread | L5_vol_adjusted_return |                 8 |        226.772 |                   0.925242 |                 0.219697 |                    0.943408 | basis_premium_like\|positioning_like\|signed_spread\|5ac72a6cc73f | ZScore(Mul(Sub(CSRank(Delta(mark_index_basis_bps,48)),CSRank(Decay(global_long_short_account_ratio_mean,6))),Sign(Decay(global_long_short_account_ratio_mean,6))))    |
| a7ls29_927562e2c9ef4445 | basis_premium_like\|positioning_like | signed_spread | L5_vol_adjusted_return |                 8 |        226.274 |                   0.926066 |                 0.2192   |                    0.797831 | basis_premium_like\|positioning_like\|signed_spread\|39537d3da263 | Mul(Sub(CSRank(Delta(mark_index_basis_bps,48)),CSRank(Decay(global_long_short_account_ratio_last,6))),Sign(Decay(global_long_short_account_ratio_last,6)))            |
| a7ls29_0a02dd89c1e9524e | basis_premium_like\|positioning_like | spread_rank   | L5_vol_adjusted_return |                 8 |        225.469 |                   0.966445 |                 0.218435 |                    0.789743 | basis_premium_like\|positioning_like\|spread_rank\|3706452569c1   | Sub(CSRank(Delta(mark_index_basis_bps,48)),CSRank(Mean(global_long_short_account_ratio_mean,4)))                                                                      |
| a7ls29_2d2d9f7153d2d870 | basis_premium_like\|positioning_like | spread_rank   | L5_vol_adjusted_return |                 8 |        221.079 |                   0.838005 |                 0.213917 |                    0.797113 | basis_premium_like\|positioning_like\|spread_rank\|f953fb4d68c7   | Sub(CSRank(Delta(mark_index_basis_bps,48)),CSRank(ZScore(Mean(global_long_short_account_ratio_mean,3))))                                                              |
| a7ls29_f504225b0ea27301 | basis_premium_like\|positioning_like | spread_rank   | L5_vol_adjusted_return |                 8 |        219.208 |                   0.955425 |                 0.212163 |                    0.559501 | basis_premium_like\|positioning_like\|spread_rank\|19e517383a3a   | ZScore(Sub(CSRank(Delta(mark_index_basis_bps,48)),CSRank(Mean(global_long_short_account_ratio_mean,2))))                                                              |
| a7ls29_9005e95755f39673 | basis_premium_like\|positioning_like | spread_rank   | L5_vol_adjusted_return |                 8 |        218.519 |                   0.770961 |                 0.21129  |                    0.573739 | basis_premium_like\|positioning_like\|spread_rank\|5e7d4146f221   | Clip(Sub(CSRank(Delta(mark_index_basis_bps,48)),CSRank(Mean(global_long_short_account_ratio_mean,2))),-3,3)                                                           |
| a7ls29_205f451bff6abe46 | basis_premium_like\|positioning_like | spread_rank   | L5_vol_adjusted_return |                 8 |        217.437 |                   0.87012  |                 0.210307 |                    0.650763 | basis_premium_like\|positioning_like\|spread_rank\|f953fb4d68c7   | Sub(CSRank(Delta(mark_index_basis_bps,48)),CSRank(ZScore(Mean(global_long_short_account_ratio_last,3))))                                                              |
| a7ls29_ab2a9032008bd91c | basis_premium_like\|positioning_like | spread_rank   | L5_vol_adjusted_return |                 8 |        216.464 |                   0.902925 |                 0.209367 |                    0.6638   | basis_premium_like\|positioning_like\|spread_rank\|d76fa02dc03b   | Sub(CSRank(Delta(mark_index_basis_bps,48)),CSRank(global_long_short_account_ratio_mean))                                                                              |
| a7ls29_f35724f25926262a | basis_premium_like\|positioning_like | safe_div_abs  | L5_vol_adjusted_return |                 8 |        212.685 |                   0.678321 |                 0.205363 |                    0.551512 | basis_premium_like\|positioning_like\|safe_div_abs\|a9e1fabae300  | CSRank(SafeDiv(TSRank(mark_index_basis_bps,24),Abs(Decay(account_position_divergence,336))))                                                                          |
| a7ls29_6ec00bfcaee26ff6 | basis_premium_like\|positioning_like | safe_div_abs  | L5_vol_adjusted_return |                 8 |        212.632 |                   0.731229 |                 0.205363 |                    0.551512 | basis_premium_like\|positioning_like\|safe_div_abs\|a92a45f756ed  | ZScore(SafeDiv(TSRank(mark_index_basis_bps,24),Abs(Decay(account_position_divergence,336))))                                                                          |
| a7ls29_8541c45fa7fda4b4 | basis_premium_like\|positioning_like | signed_spread | L5_vol_adjusted_return |                 8 |        212.286 |                   0.947191 |                 0.205233 |                    0.480187 | basis_premium_like\|positioning_like\|signed_spread\|39537d3da263 | Mul(Sub(CSRank(Delta(mark_index_basis_bps,48)),CSRank(Decay(global_long_short_account_ratio_mean,48))),Sign(Decay(top_long_short_account_ratio_mean,48)))             |
| a7ls29_58aa4ae107ccfbff | basis_premium_like\|positioning_like | spread_rank   | L5_vol_adjusted_return |                 8 |        209.665 |                   0.69059  |                 0.202355 |                    0.573048 | basis_premium_like\|positioning_like\|spread_rank\|85b385f48d6a   | Neg(Sub(CSRank(Delta(mark_index_basis_bps,48)),CSRank(Mean(global_long_short_account_ratio_mean,2))))                                                                 |
| a7ls29_eb675c19311165d9 | basis_premium_like\|positioning_like | safe_div_abs  | L5_vol_adjusted_return |                 8 |        209.001 |                   0.548125 |                 0.201549 |                    0.577612 | basis_premium_like\|positioning_like\|safe_div_abs\|6cf4ca98f728  | Clip(SafeDiv(TSRank(mark_index_basis_bps,24),Abs(Decay(account_position_divergence,336))),-3,3)                                                                       |

## Interpretation

A7LS29 is materially better than A7LS28B: the skeleton key problem is repaired, selected portfolio queue rows increased from 12 to 291, and the field/materialization layer stayed clean. The best current structures remain basis/positioning and OI/positioning variants, with useful L5 and L3 non-L7 evidence. The next wave should expand these productive families while forcing OI/positioning/regime/listing-age quotas so the search does not collapse back to basis-only.

## Boundary

```text
No formula search promotion is authorized by this file.
No alpha proof / shadow / paper / live is authorized.
A7LS30 may run numeric probes only, with field gate first.
```

## Outputs

- `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7ls29_productive_numeric_acceptance_20260610`
- `G:\AlphaFactory_CryptoData\research_runtime\a7ls29_productive_numeric_acceptance_20260610`
- `G:\AlphaFactory_CryptoData\manifests\a7ls29_productive_numeric_acceptance_20260610_manifest.json`
