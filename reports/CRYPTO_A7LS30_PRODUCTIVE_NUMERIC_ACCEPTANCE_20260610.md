# CRYPTO A7LS30 Productive Numeric Acceptance 20260610

## Decision

`PASS_A7LS30_PRODUCTIVE_NUMERIC_ACCEPTED_NO_SEARCH_AUTH`

A7LS30 completed all 16 company-machine numeric shards. This is numeric evidence and queue validation only. It does not authorize alpha proof, formula search promotion, shadow, paper, or live execution.

## Counts

- queue_rows: 8192
- shard_count: 16
- pass_count: 16
- hold_count: 0
- input_blueprint_count_total: 8192
- activity_ok_total: 8181
- missing_numeric_field_shards: 0
- materialization_eval_fail_count: 0
- non_l7_numeric_clue_rows_total: 11859
- rank_label_diagnostic_clue_rows_total: 3936
- portfolio_queue_rows_total: 4586
- selected_portfolio_queue_rows_total: 425
- selected_skeleton_unique: 280
- selected_top_skeleton_share: 0.0094

## Best Current Formula

```text
SafeDiv(SafeDiv(ZScore(Mean(open_interest_value_last,4)),Abs(Mean(account_position_divergence,96))),Abs(ZScore(Mean(open_interest_last,168))))
```

## Shard Summary

| shard_id        | decision                                                            |   materialized_activity_ok_count |   non_l7_numeric_clue_rows |   rank_label_diagnostic_clue_rows |   portfolio_queue_count |   selected_portfolio_queue_count |
|:----------------|:--------------------------------------------------------------------|---------------------------------:|---------------------------:|----------------------------------:|------------------------:|---------------------------------:|
| a7ls30_num_s000 | PASS_A7LS30a7ls30_num_s000_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                              512 |                       1233 |                               431 |                     275 |                               22 |
| a7ls30_num_s001 | PASS_A7LS30a7ls30_num_s001_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                              512 |                       1066 |                               306 |                     374 |                               24 |
| a7ls30_num_s002 | PASS_A7LS30a7ls30_num_s002_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                              512 |                       1157 |                               430 |                     422 |                               24 |
| a7ls30_num_s003 | PASS_A7LS30a7ls30_num_s003_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                              512 |                        331 |                               112 |                     181 |                               24 |
| a7ls30_num_s004 | PASS_A7LS30a7ls30_num_s004_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                              512 |                        633 |                                28 |                     287 |                               24 |
| a7ls30_num_s005 | PASS_A7LS30a7ls30_num_s005_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                              512 |                        583 |                                70 |                     291 |                               24 |
| a7ls30_num_s006 | PASS_A7LS30a7ls30_num_s006_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                              512 |                        746 |                                 4 |                     326 |                               24 |
| a7ls30_num_s007 | PASS_A7LS30a7ls30_num_s007_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                              512 |                        698 |                                17 |                     308 |                               24 |
| a7ls30_num_s008 | PASS_A7LS30a7ls30_num_s008_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                              512 |                        556 |                               205 |                     240 |                               24 |
| a7ls30_num_s009 | PASS_A7LS30a7ls30_num_s009_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                              512 |                        374 |                               271 |                     213 |                               24 |
| a7ls30_num_s010 | PASS_A7LS30a7ls30_num_s010_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                              506 |                       1081 |                               628 |                     289 |                               33 |
| a7ls30_num_s011 | PASS_A7LS30a7ls30_num_s011_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                              507 |                        944 |                               766 |                     357 |                               34 |
| a7ls30_num_s012 | PASS_A7LS30a7ls30_num_s012_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                              512 |                        565 |                                42 |                     223 |                               24 |
| a7ls30_num_s013 | PASS_A7LS30a7ls30_num_s013_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                              512 |                        520 |                               178 |                     233 |                               24 |
| a7ls30_num_s014 | PASS_A7LS30a7ls30_num_s014_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                              512 |                        727 |                               261 |                     302 |                               48 |
| a7ls30_num_s015 | PASS_A7LS30a7ls30_num_s015_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                              512 |                        645 |                               187 |                     265 |                               24 |

## Selected Family Summary

| semantic_pair                                          | motif               | label_family                       |   selected_rows |
|:-------------------------------------------------------|:--------------------|:-----------------------------------|----------------:|
| open_interest_like\|positioning_like\|regime_state     | seed_gated_sign     | L3_liquidity_tier_relative_return  |              62 |
| open_interest_like\|positioning_like                   | smooth_mul          | L5_vol_adjusted_return             |              54 |
| basis_premium_like\|positioning_like                   | spread_rank         | L5_vol_adjusted_return             |              41 |
| basis_premium_like\|positioning_like                   | safe_div_abs        | L5_vol_adjusted_return             |              38 |
| basis_premium_like\|positioning_like                   | signed_spread       | L5_vol_adjusted_return             |              32 |
| open_interest_like\|positioning_like\|listing_age_like | seed_sub            | L7_ranked_future_return            |              29 |
| open_interest_like\|positioning_like\|regime_state     | seed_gated_sign     | L7_ranked_future_return            |              29 |
| basis_premium_like\|positioning_like                   | sub                 | L5_vol_adjusted_return             |              27 |
| open_interest_like\|positioning_like\|listing_age_like | seed_sub            | L3_liquidity_tier_relative_return  |              26 |
| open_interest_like\|positioning_like                   | safe_div_abs        | L7_ranked_future_return            |              18 |
| open_interest_like\|positioning_like                   | safe_div_abs        | L5_vol_adjusted_return             |              15 |
| open_interest_like\|positioning_like\|listing_age_like | seed_sub            | L0_raw_forward_return              |               8 |
| basis_premium_like\|age_x_volatility\|positioning_like | seed_mul            | L7_ranked_future_return            |               8 |
| basis_premium_like\|age_x_volatility\|positioning_like | seed_mul            | L0_raw_forward_return              |               7 |
| open_interest_like\|positioning_like\|listing_age_like | seed_sub            | L1_cross_sectional_relative_return |               6 |
| basis_premium_like\|age_x_volatility\|positioning_like | seed_sub            | L7_ranked_future_return            |               4 |
| open_interest_like\|positioning_like\|regime_state     | seed_gated_sign     | L1_cross_sectional_relative_return |               4 |
| basis_premium_like\|positioning_like                   | mean_reversion_gate | L5_vol_adjusted_return             |               3 |
| basis_premium_like\|age_x_volatility\|positioning_like | seed_mul            | L3_liquidity_tier_relative_return  |               2 |
| basis_premium_like\|age_x_volatility\|positioning_like | seed_sub            | L1_cross_sectional_relative_return |               2 |
| basis_premium_like\|age_x_volatility\|positioning_like | seed_mul            | L1_cross_sectional_relative_return |               2 |
| open_interest_like\|positioning_like                   | safe_div_abs        | L0_raw_forward_return              |               2 |
| open_interest_like\|positioning_like                   | safe_div_abs        | L1_cross_sectional_relative_return |               2 |
| open_interest_like\|positioning_like                   | smooth_mul          | L7_ranked_future_return            |               2 |
| basis_premium_like\|positioning_like                   | sub                 | L7_ranked_future_return            |               1 |
| open_interest_like\|positioning_like\|regime_state     | seed_gated_sign     | L0_raw_forward_return              |               1 |

## Selected Label Summary

| label_family                       |   label_horizon_h |   selected_rows |
|:-----------------------------------|------------------:|----------------:|
| L3_liquidity_tier_relative_return  |                24 |              87 |
| L5_vol_adjusted_return             |                 4 |              79 |
| L5_vol_adjusted_return             |                 1 |              50 |
| L5_vol_adjusted_return             |                24 |              48 |
| L7_ranked_future_return            |                24 |              40 |
| L5_vol_adjusted_return             |                 8 |              33 |
| L7_ranked_future_return            |                 8 |              32 |
| L1_cross_sectional_relative_return |                24 |              14 |
| L7_ranked_future_return            |                 1 |              13 |
| L0_raw_forward_return              |                24 |              12 |
| L0_raw_forward_return              |                 8 |               6 |
| L7_ranked_future_return            |                 4 |               6 |
| L3_liquidity_tier_relative_return  |                 4 |               3 |
| L1_cross_sectional_relative_return |                 8 |               2 |

## Top Selected Queue

| blueprint_id            | semantic_pair                        | motif         | label_family           |   label_horizon_h |   score_no_may |   control_ratio_premay_max |   cost10_recent_oriented |   robust_median_tstat_floor | skeleton_key                                                      | expression                                                                                                                                                            |
|:------------------------|:-------------------------------------|:--------------|:-----------------------|------------------:|---------------:|---------------------------:|-------------------------:|----------------------------:|:------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| a7ls30_c139d322017158f7 | open_interest_like\|positioning_like | safe_div_abs  | L5_vol_adjusted_return |                24 |        428.357 |                   0.973294 |                 0.421331 |                    1.0707   | open_interest_like\|positioning_like\|safe_div_abs\|c35df304e3ff  | SafeDiv(SafeDiv(ZScore(Mean(open_interest_value_last,4)),Abs(Mean(account_position_divergence,96))),Abs(ZScore(Mean(open_interest_last,168))))                        |
| a7ls30_1e8278c16afb1f4c | basis_premium_like\|positioning_like | safe_div_abs  | L5_vol_adjusted_return |                24 |        358.889 |                   0.935527 |                 0.351825 |                    0.685817 | basis_premium_like\|positioning_like\|safe_div_abs\|e740a0aa371c  | Neg(SafeDiv(TSRank(mark_index_basis_bps,16),Abs(Decay(account_position_divergence,168))))                                                                             |
| a7ls30_0d2e45e57b9c1939 | basis_premium_like\|positioning_like | safe_div_abs  | L5_vol_adjusted_return |                24 |        330.463 |                   0.834837 |                 0.323298 |                    0.71099  | basis_premium_like\|positioning_like\|safe_div_abs\|d40239548165  | Mul(SafeDiv(TSRank(mark_index_basis_bps,6),Abs(Decay(account_position_divergence,504))),Sign(Decay(liquidity_cycle_state,24)))                                        |
| a7ls30_f091c7b12b8adf50 | basis_premium_like\|positioning_like | safe_div_abs  | L5_vol_adjusted_return |                24 |        328.687 |                   0.741036 |                 0.321428 |                    0.59263  | basis_premium_like\|positioning_like\|safe_div_abs\|33984dc41fa6  | Abs(Neg(SafeDiv(TSRank(mark_index_basis_bps,8),Abs(Decay(account_position_divergence,168)))))                                                                         |
| a7ls30_a67871543b537c93 | basis_premium_like\|positioning_like | safe_div_abs  | L5_vol_adjusted_return |                24 |        328.687 |                   0.741036 |                 0.321428 |                    0.59263  | basis_premium_like\|positioning_like\|safe_div_abs\|a3e212bc238d  | ZScore(ZScore(SafeDiv(TSRank(mark_index_basis_bps,8),Abs(Decay(account_position_divergence,168)))))                                                                   |
| a7ls30_32f8844234cc65fc | open_interest_like\|positioning_like | safe_div_abs  | L5_vol_adjusted_return |                24 |        324.451 |                   0.886711 |                 0.317338 |                    0.785718 | open_interest_like\|positioning_like\|safe_div_abs\|7946a7d9baa2  | SafeDiv(ZScore(Mean(open_interest_value_last,504)),Abs(Mean(account_position_divergence,96)))                                                                         |
| a7ls30_c667865bf98b0175 | open_interest_like\|positioning_like | safe_div_abs  | L5_vol_adjusted_return |                24 |        321.193 |                   0.874638 |                 0.314068 |                    0.398977 | open_interest_like\|positioning_like\|safe_div_abs\|cc4d01d2849f  | SafeDiv(Abs(ZScore(Mean(open_interest_mean,168))),Abs(Decay(account_position_divergence,168)))                                                                        |
| a7ls30_904c73cae9c357bd | basis_premium_like\|positioning_like | safe_div_abs  | L5_vol_adjusted_return |                24 |        320.347 |                   0.624449 |                 0.312972 |                    0.511821 | basis_premium_like\|positioning_like\|safe_div_abs\|044c7da54852  | SafeDiv(TSRank(mark_index_basis_bps,6),Abs(Decay(account_position_divergence,120)))                                                                                   |
| a7ls30_8654e39d790613a4 | basis_premium_like\|positioning_like | safe_div_abs  | L5_vol_adjusted_return |                24 |        316.852 |                   0.842905 |                 0.309695 |                    0.73207  | basis_premium_like\|positioning_like\|safe_div_abs\|255e9dd67c24  | Abs(SafeDiv(TSRank(mark_index_basis_bps,6),Abs(Decay(account_position_divergence,504))))                                                                              |
| a7ls30_05ebe7975ee30996 | basis_premium_like\|positioning_like | safe_div_abs  | L5_vol_adjusted_return |                24 |        316.813 |                   0.882302 |                 0.309695 |                    0.73207  | basis_premium_like\|positioning_like\|safe_div_abs\|a9e1fabae300  | CSRank(SafeDiv(TSRank(mark_index_basis_bps,6),Abs(Decay(account_position_divergence,504))))                                                                           |
| a7ls30_ce04d4304027e465 | basis_premium_like\|positioning_like | safe_div_abs  | L5_vol_adjusted_return |                24 |        316.751 |                   0.944223 |                 0.309695 |                    0.73207  | basis_premium_like\|positioning_like\|safe_div_abs\|a92a45f756ed  | ZScore(SafeDiv(TSRank(mark_index_basis_bps,6),Abs(Decay(account_position_divergence,504))))                                                                           |
| a7ls30_1b3475a75dd7dcb3 | basis_premium_like\|positioning_like | safe_div_abs  | L5_vol_adjusted_return |                24 |        299.638 |                   0.928356 |                 0.292566 |                    0.745463 | basis_premium_like\|positioning_like\|safe_div_abs\|6cf4ca98f728  | Clip(SafeDiv(TSRank(mark_index_basis_bps,6),Abs(Decay(account_position_divergence,504))),-3,3)                                                                        |
| a7ls30_304c5715fb98ad55 | basis_premium_like\|positioning_like | safe_div_abs  | L5_vol_adjusted_return |                24 |        291.054 |                   0.976873 |                 0.284031 |                    0.750495 | basis_premium_like\|positioning_like\|safe_div_abs\|a9e1fabae300  | CSRank(SafeDiv(TSRank(mark_index_basis_bps,8),Abs(Decay(account_position_divergence,504))))                                                                           |
| a7ls30_e8b114ed70485e4c | basis_premium_like\|positioning_like | safe_div_abs  | L5_vol_adjusted_return |                24 |        291.054 |                   0.976873 |                 0.284031 |                    0.750495 | basis_premium_like\|positioning_like\|safe_div_abs\|255e9dd67c24  | Abs(SafeDiv(TSRank(mark_index_basis_bps,8),Abs(Decay(account_position_divergence,504))))                                                                              |
| a7ls30_8c44296a4594b755 | open_interest_like\|positioning_like | safe_div_abs  | L5_vol_adjusted_return |                24 |        281.16  |                   0.980187 |                 0.27414  |                    0.391593 | open_interest_like\|positioning_like\|safe_div_abs\|1c24f2bbe951  | CSRank(SafeDiv(Abs(ZScore(Mean(open_interest_last,24))),Abs(Decay(account_position_divergence,120))))                                                                 |
| a7ls30_c94e14bb2b98e5b3 | open_interest_like\|positioning_like | safe_div_abs  | L5_vol_adjusted_return |                24 |        272.087 |                   0.726734 |                 0.264814 |                    0.55307  | open_interest_like\|positioning_like\|safe_div_abs\|ede788b53b6e  | ZScore(SafeDiv(Abs(ZScore(Mean(open_interest_last,48))),Abs(Decay(account_position_divergence,120))))                                                                 |
| a7ls30_c94e306c3e19bd08 | open_interest_like\|positioning_like | safe_div_abs  | L5_vol_adjusted_return |                24 |        270.869 |                   0.711122 |                 0.26358  |                    0.975795 | open_interest_like\|positioning_like\|safe_div_abs\|7946a7d9baa2  | SafeDiv(ZScore(Mean(open_interest_value_last,240)),Abs(Mean(account_position_divergence,72)))                                                                         |
| a7ls30_fa77c59f98cd8837 | open_interest_like\|positioning_like | safe_div_abs  | L5_vol_adjusted_return |                24 |        268.751 |                   0.741782 |                 0.261493 |                    0.890204 | open_interest_like\|positioning_like\|safe_div_abs\|650a16a484ae  | SafeDiv(SafeDiv(Abs(ZScore(Mean(open_interest_last,240))),Abs(Decay(account_position_divergence,96))),Abs(ZScore(Mean(open_interest_last,168))))                      |
| a7ls30_e255e6987a8176ab | open_interest_like\|positioning_like | safe_div_abs  | L5_vol_adjusted_return |                24 |        257.024 |                   0.954347 |                 0.249979 |                    0.515137 | open_interest_like\|positioning_like\|safe_div_abs\|cc4d01d2849f  | SafeDiv(Abs(ZScore(Mean(open_interest_last,504))),Abs(Decay(account_position_divergence,120)))                                                                        |
| a7ls30_f82e6338a9d33426 | basis_premium_like\|positioning_like | signed_spread | L5_vol_adjusted_return |                 8 |        227.425 |                   0.929702 |                 0.220355 |                    0.951157 | basis_premium_like\|positioning_like\|signed_spread\|efbfa119cac1 | CSRank(Mul(Sub(CSRank(Delta(mark_index_basis_bps,48)),CSRank(Decay(global_long_short_account_ratio_mean,6))),Sign(Decay(global_long_short_account_ratio_mean,6))))    |
| a7ls30_9254be7c7479597f | basis_premium_like\|positioning_like | signed_spread | L5_vol_adjusted_return |                 8 |        227.425 |                   0.929702 |                 0.220355 |                    0.951157 | basis_premium_like\|positioning_like\|signed_spread\|d8a4b8811704 | Clip(Mul(Sub(CSRank(Delta(mark_index_basis_bps,48)),CSRank(Decay(global_long_short_account_ratio_mean,6))),Sign(Decay(global_long_short_account_ratio_mean,6))),-3,3) |
| a7ls30_d18787649d48e83a | basis_premium_like\|positioning_like | spread_rank   | L5_vol_adjusted_return |                 8 |        227.425 |                   0.929702 |                 0.220355 |                    0.951157 | basis_premium_like\|positioning_like\|spread_rank\|f6895cda2696   | Sub(CSRank(Delta(mark_index_basis_bps,48)),CSRank(Decay(global_long_short_account_ratio_mean,6)))                                                                     |
| a7ls30_a293b5f986477e96 | basis_premium_like\|positioning_like | signed_spread | L5_vol_adjusted_return |                 8 |        226.772 |                   0.925242 |                 0.219697 |                    0.943408 | basis_premium_like\|positioning_like\|signed_spread\|5ac72a6cc73f | ZScore(Mul(Sub(CSRank(Delta(mark_index_basis_bps,48)),CSRank(Decay(global_long_short_account_ratio_mean,6))),Sign(Decay(global_long_short_account_ratio_mean,6))))    |
| a7ls30_58ec3503a85df3e6 | basis_premium_like\|positioning_like | spread_rank   | L5_vol_adjusted_return |                 8 |        225.469 |                   0.966445 |                 0.218435 |                    0.789743 | basis_premium_like\|positioning_like\|spread_rank\|3706452569c1   | Sub(CSRank(Delta(mark_index_basis_bps,48)),CSRank(Mean(global_long_short_account_ratio_mean,4)))                                                                      |
| a7ls30_c265afff72fae726 | basis_premium_like\|positioning_like | signed_spread | L5_vol_adjusted_return |                 8 |        224.085 |                   0.825187 |                 0.21691  |                    0.744839 | basis_premium_like\|positioning_like\|signed_spread\|39537d3da263 | Mul(Sub(CSRank(Delta(mark_index_basis_bps,48)),CSRank(Decay(global_long_short_account_ratio_mean,4))),Sign(Decay(global_long_short_account_ratio_mean,6)))            |
| a7ls30_c737c948fecd9074 | basis_premium_like\|positioning_like | spread_rank   | L5_vol_adjusted_return |                 8 |        221.079 |                   0.838005 |                 0.213917 |                    0.797113 | basis_premium_like\|positioning_like\|spread_rank\|f953fb4d68c7   | Sub(CSRank(Delta(mark_index_basis_bps,48)),CSRank(ZScore(Mean(global_long_short_account_ratio_mean,3))))                                                              |
| a7ls30_bd52ea384fe0bc53 | basis_premium_like\|positioning_like | spread_rank   | L5_vol_adjusted_return |                 8 |        218.519 |                   0.770961 |                 0.21129  |                    0.573739 | basis_premium_like\|positioning_like\|spread_rank\|3706452569c1   | Sub(CSRank(Delta(mark_index_basis_bps,48)),CSRank(Mean(global_long_short_account_ratio_mean,2)))                                                                      |
| a7ls30_26fc82f959a87fb9 | basis_premium_like\|positioning_like | spread_rank   | L5_vol_adjusted_return |                 8 |        216.416 |                   0.950708 |                 0.209367 |                    0.6638   | basis_premium_like\|positioning_like\|spread_rank\|d76fa02dc03b   | Sub(CSRank(Delta(mark_index_basis_bps,48)),CSRank(global_long_short_account_ratio_mean))                                                                              |
| a7ls30_1157a8790b3c6405 | basis_premium_like\|positioning_like | spread_rank   | L5_vol_adjusted_return |                 8 |        210.237 |                   0.958701 |                 0.203196 |                    0.958575 | basis_premium_like\|positioning_like\|spread_rank\|3cf33e2c3b2c   | Mul(Sub(CSRank(Delta(mark_index_basis_bps,168)),CSRank(global_long_short_account_ratio_mean)),Sign(Decay(liquidity_cycle_state,24)))                                  |
| a7ls30_dd3ad1effb4058b4 | open_interest_like\|positioning_like | safe_div_abs  | L5_vol_adjusted_return |                24 |        205.402 |                   0.894967 |                 0.198297 |                    0.391464 | open_interest_like\|positioning_like\|safe_div_abs\|86f0a779e1d0  | Neg(ZScore(SafeDiv(Abs(ZScore(Mean(open_interest_last,240))),Abs(Decay(account_position_divergence,120)))))                                                           |

## Interpretation

A7LS30 improved over A7LS29: selected portfolio rows increased from 291 to 425, all shards passed, and the best current formula moved from a pure basis/positioning variant to an open-interest-value / positioning-scale structure. This suggests the previous bottleneck was not only field scarcity; the prior search neighborhood was too centered on basis/positioning.

## Boundary

```text
No alpha proof is authorized.
No shadow, paper, or live execution is authorized.
Next work should use lightly governed large-space raw search, not another narrow productive-parent mutation.
```

## Outputs

- `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7ls30_productive_numeric_acceptance_20260610`
- `G:\AlphaFactory_CryptoData\research_runtime\a7ls30_productive_numeric_acceptance_20260610`
- `G:\AlphaFactory_CryptoData\manifests\a7ls30_productive_numeric_acceptance_20260610_manifest.json`
