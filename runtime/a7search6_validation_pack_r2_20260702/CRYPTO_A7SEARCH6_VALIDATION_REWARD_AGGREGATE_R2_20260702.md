# CRYPTO A7V3S0 Reward Sharded Aggregate 20260613

Decision: `PASS_A7V3S0_REWARD_SHARDED_AGGREGATE_READY`

## Counts

- expected_shards: `19`
- manifest_count: `19`
- accepted_rows: `18`
- accepted_unique_blueprints: `15`
- accepted_expression_missing: `0`
- reward_rows: `1180`
- split_metric_rows: `35400`
- eval_error_rows: `0`
- launcher_status_conflicts: `0`

## Accepted By Semantic Pair

| semantic_pair                |   count |
|:-----------------------------|--------:|
| open_interest\|positioning   |       7 |
| open_interest\|premium       |       3 |
| positioning\|regime          |       3 |
| funding_dense\|open_interest |       2 |
| basis\|positioning           |       1 |
| liquidity\|positioning       |       1 |
| open_interest\|taker_flow    |       1 |

## Accepted By Motif

| motif                               |   count |
|:------------------------------------|--------:|
| safe_div_abs_validation             |       5 |
| adjacent_signed_rank_validation     |       3 |
| adjacent_spread_rank_validation     |       2 |
| adjacent_safe_div_csrank_validation |       2 |
| regime_signed_validation            |       2 |
| scaled_spread_abs_validation        |       2 |
| adjacent_mul_validation             |       1 |
| adjacent_safe_div_abs_validation    |       1 |

## Accepted By Horizon

|   horizon_h |   count |
|------------:|--------:|
|           4 |      10 |
|          24 |       5 |
|           8 |       3 |

## Top Accepted With Full Formula

| blueprint_id                                      | semantic_pair                | motif                               |   horizon_h |   min_oos_floor_sortino |   min_oos_sortino |   recent_sortino |   recent_shuffle_control_ratio | formula                                                                                                                                                                   |
|:--------------------------------------------------|:-----------------------------|:------------------------------------|------------:|------------------------:|------------------:|-----------------:|-------------------------------:|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| a7search6_vp_a7search6_afa93f504b4c29d0_canonical | funding_dense\|open_interest | adjacent_safe_div_csrank_validation |           4 |                8.6339   |         10.1639   |         13.5427  |                      0.768606  | SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72))))                                                                       |
| a7search6_vp_a7search6_afa93f504b4c29d0_canonical | funding_dense\|open_interest | adjacent_safe_div_csrank_validation |           8 |                8.50321  |         11.8745   |         18.3882  |                      0.398843  | SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72))))                                                                       |
| a7search6_vp_a7search6_4c8a38ddff3fb132_canonical | open_interest\|positioning   | safe_div_abs_validation             |           4 |                7.69971  |          7.88304  |         12.8057  |                      0.354104  | SafeDiv(CSRank(Delta(open_interest_value_last,96)),Abs(Decay(account_position_divergence,48)))                                                                            |
| a7search6_vp_a7search6_06c5d4a2d2ce5d98_canonical | open_interest\|positioning   | safe_div_abs_validation             |           4 |                7.5507   |          8.01097  |         10.702   |                      0.659038  | SafeDiv(ZScore(Mean(open_interest_value_mean,504)),Abs(global_long_short_account_ratio_last))                                                                             |
| a7search6_vp_a7search6_5be6987af4a13e67_canonical | open_interest\|positioning   | safe_div_abs_validation             |           4 |                5.72329  |          7.46779  |          7.85899 |                      0.971161  | SafeDiv(Abs(CSRank(open_interest_value_change_24h)),Abs(Decay(account_position_divergence,8)))                                                                            |
| a7search6_vp_a7search6_4c8a38ddff3fb132_canonical | open_interest\|positioning   | safe_div_abs_validation             |          24 |                5.71299  |          9.73968  |         17.6279  |                      0.0809608 | SafeDiv(CSRank(Delta(open_interest_value_last,96)),Abs(Decay(account_position_divergence,48)))                                                                            |
| a7search6_vp_a7search6_e7ee64f0ef980aca_canonical | open_interest\|positioning   | safe_div_abs_validation             |           4 |                5.03834  |          5.27179  |         14.7101  |                      0.321052  | SafeDiv(TSRank(open_interest_value_last,504),Abs(Mean(top_long_short_account_ratio_last,8)))                                                                              |
| a7search6_vp_a7search6_5a326bbdc99cd2b9_canonical | open_interest\|positioning   | scaled_spread_abs_validation        |           4 |                4.89019  |          5.53742  |         14.1914  |                      0.508094  | SafeDiv(Sub(CSRank(TSRank(open_interest_value_mean,504)),CSRank(CSRank(global_long_short_account_ratio_last))),Abs(CSRank(CSRank(global_long_short_account_ratio_last)))) |
| a7search6_vp_a7search6_5a326bbdc99cd2b9_canonical | open_interest\|positioning   | scaled_spread_abs_validation        |           8 |                4.12518  |          6.01743  |         17.6046  |                      0.236695  | SafeDiv(Sub(CSRank(TSRank(open_interest_value_mean,504)),CSRank(CSRank(global_long_short_account_ratio_last))),Abs(CSRank(CSRank(global_long_short_account_ratio_last)))) |
| a7search6_vp_a7search6_370b9d993902426e_canonical | open_interest\|taker_flow    | adjacent_spread_rank_validation     |           4 |                2.12792  |          2.88422  |         13.6746  |                      0.375933  | Sub(CSRank(TSRank(open_interest_value_last,504)),CSRank(Mean(taker_buy_sell_volume_ratio_last,72)))                                                                       |
| a7search6_vp_a7search6_229924c832dd5901_canonical | open_interest\|premium       | adjacent_signed_rank_validation     |          24 |                1.90384  |          2.92514  |          5.9645  |                      0.427901  | Mul(CSRank(Mean(open_interest_mean,8)),Sign(Mean(premium_close_bps,48)))                                                                                                  |
| a7search6_vp_a7search6_5a7a41644c28a05a_canonical | open_interest\|premium       | adjacent_signed_rank_validation     |          24 |                1.73821  |          3.10159  |          5.80861 |                      0.188398  | Mul(CSRank(Mean(open_interest_mean,12)),Sign(Mean(premium_close_bps,48)))                                                                                                 |
| a7search6_vp_a7search6_0159a7544af64b1d_canonical | basis\|positioning           | adjacent_spread_rank_validation     |          24 |                1.68071  |          2.89055  |          8.60733 |                      0.220905  | Sub(CSRank(ZScore(Mean(account_position_divergence,24))),CSRank(Decay(mark_index_basis_bps,336)))                                                                         |
| a7search6_vp_a7search6_2e796ac0b2a688c4_canonical | open_interest\|premium       | adjacent_mul_validation             |          24 |                1.36465  |          2.44163  |          2.44163 |                      0.845688  | Mul(open_interest_last,Mean(premium_close_bps,504))                                                                                                                       |
| a7search6_vp_a7search6_05d9f75e309aa068_canonical | positioning\|regime          | regime_signed_validation            |           4 |                0.4619   |          1.00227  |         14.873   |                      0.644717  | Mul(ZScore(global_long_short_account_ratio_last),Sign(Decay(stress_proxy_state,336)))                                                                                     |
| a7search6_vp_a7search6_215546fe5dfda21c_canonical | positioning\|regime          | adjacent_signed_rank_validation     |           4 |                0.4619   |          1.00227  |         14.873   |                      0.452678  | Mul(CSRank(Abs(CSRank(global_long_short_account_ratio_last))),Sign(Decay(stress_proxy_state,336)))                                                                        |
| a7search6_vp_a7search6_8d74bccf1d25af11_canonical | liquidity\|positioning       | adjacent_safe_div_abs_validation    |           8 |                0.18029  |          0.949114 |         17.7061  |                      0.133306  | SafeDiv(Decay(top_long_short_account_ratio_last,12),Abs(ZScore(Mean(quote_volume_z_168h,504))))                                                                           |
| a7search6_vp_a7search6_9115fe1cea3feca0_canonical | positioning\|regime          | regime_signed_validation            |           4 |                0.082274 |          0.508013 |         14.3523  |                      0.264436  | Mul(ZScore(top_long_short_account_ratio_last),Sign(Decay(stress_proxy_state,336)))                                                                                        |

## Rejection Reasons

| hard_reject_reason                 |   count |
|:-----------------------------------|--------:|
| oos_nonoverlap_floor_not_positive  |     983 |
| oos_control_dominated              |     971 |
| oos_lag_stale_dominated            |     927 |
| oos_net_mean_not_all_positive      |     868 |
| stress_floor_not_positive          |     750 |
| oos_shuffle_dominated              |     713 |
| shuffle_control_dominated_recent   |     545 |
| train_sortino_non_positive         |     479 |
| train_orientation_no_positive_edge |     478 |
| recent_sortino_non_positive        |     408 |
| train_sortino_overfit_gap          |      67 |
| non_finite_diagnostic_composite    |      48 |
| missing_train_oos_consistency      |      48 |

## Shard Decisions

| decision                                          |   count |
|:--------------------------------------------------|--------:|
| PASS_A7REWARD1_PORTFOLIO_REWARD_LEADERBOARD_BUILT |      14 |
| HOLD_A7REWARD1_REWARD_MODEL_OR_QUEUE_FAILED       |       5 |

## Notes

- This is a reward-gate aggregate, not alpha proof.
- Full formula is taken from the candidate `expression` column and backfilled from shard queues when needed.
- Launcher status conflicts are diagnostic because shard manifests are the source of truth.
