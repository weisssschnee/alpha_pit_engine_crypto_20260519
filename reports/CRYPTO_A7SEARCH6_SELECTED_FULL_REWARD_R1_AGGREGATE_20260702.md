# CRYPTO A7SEARCH6 Selected Full Reward R1 Aggregate 20260702

Decision: `PASS_A7V3S0_REWARD_SHARDED_AGGREGATE_READY`

Boundary: this is a bounded full reward aggregate on the A7SEARCH6 proxy-selected queue. The reward input excluded 2 rows from suspect proxy shards `a7search6_proxy_s019`, `a7search6_proxy_s020`, and `a7search6_proxy_s022`; 185 clean selected rows were evaluated. This authorizes validation-pack and triage work only. It does not authorize alpha proof, shadow, paper, live, or production portfolio construction.

## Counts

- expected_shards: `12`
- manifest_count: `12`
- accepted_rows: `27`
- accepted_unique_blueprints: `22`
- accepted_expression_missing: `0`
- reward_rows: `732`
- split_metric_rows: `22200`
- eval_error_rows: `0`
- launcher_status_conflicts: `0`

## Accepted By Semantic Pair

| semantic_pair                |   count |
|:-----------------------------|--------:|
| open_interest\|positioning   |       9 |
| open_interest\|taker_flow    |       4 |
| open_interest\|premium       |       4 |
| positioning\|regime          |       3 |
| funding_dense\|open_interest |       2 |
| liquidity\|positioning       |       2 |
| basis\|open_interest         |       1 |
| basis\|positioning           |       1 |
| positioning\|taker_flow      |       1 |

## Accepted By Motif

| motif                    |   count |
|:-------------------------|--------:|
| safe_div_abs             |       6 |
| adjacent_spread_rank     |       5 |
| adjacent_signed_rank     |       4 |
| adjacent_mul             |       3 |
| adjacent_safe_div_csrank |       2 |
| adjacent_safe_div_abs    |       2 |
| regime_signed            |       2 |
| scaled_spread_abs        |       2 |
| z_safe_div_abs_csrank    |       1 |

## Accepted By Horizon

|   horizon_h |   count |
|------------:|--------:|
|           4 |      11 |
|           8 |      10 |
|          24 |       6 |

## Top Accepted With Full Formula

| blueprint_id               | semantic_pair                | motif                    |   horizon_h |   min_oos_floor_sortino |   min_oos_sortino |   recent_sortino |   recent_shuffle_control_ratio | formula                                                                                                                                                                   |
|:---------------------------|:-----------------------------|:-------------------------|------------:|------------------------:|------------------:|-----------------:|-------------------------------:|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| a7search6_afa93f504b4c29d0 | funding_dense\|open_interest | adjacent_safe_div_csrank |           4 |                8.6339   |          10.1639  |         13.5427  |                       0.559468 | SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72))))                                                                       |
| a7search6_afa93f504b4c29d0 | funding_dense\|open_interest | adjacent_safe_div_csrank |           8 |                8.50321  |          11.8745  |         18.3882  |                       0.2087   | SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72))))                                                                       |
| a7search6_84f74066182786e3 | open_interest\|positioning   | safe_div_abs             |           4 |                7.98112  |           8.75552 |         10.5157  |                       0.685472 | SafeDiv(ZScore(Mean(open_interest_value_mean,8)),Abs(global_long_short_account_ratio_last))                                                                               |
| a7search6_06c5d4a2d2ce5d98 | open_interest\|positioning   | safe_div_abs             |           4 |                7.5507   |           8.01097 |         10.702   |                       0.690606 | SafeDiv(ZScore(Mean(open_interest_value_mean,504)),Abs(global_long_short_account_ratio_last))                                                                             |
| a7search6_5be6987af4a13e67 | open_interest\|positioning   | safe_div_abs             |           4 |                5.72329  |           7.46779 |          7.85899 |                       0.734119 | SafeDiv(Abs(CSRank(open_interest_value_change_24h)),Abs(Decay(account_position_divergence,8)))                                                                            |
| a7search6_4c8a38ddff3fb132 | open_interest\|positioning   | safe_div_abs             |          24 |                5.71299  |           9.73968 |         17.6279  |                       0.35608  | SafeDiv(CSRank(Delta(open_interest_value_last,96)),Abs(Decay(account_position_divergence,48)))                                                                            |
| a7search6_e7ee64f0ef980aca | open_interest\|positioning   | safe_div_abs             |           4 |                5.03834  |           5.27179 |         14.7101  |                       0.283521 | SafeDiv(TSRank(open_interest_value_last,504),Abs(Mean(top_long_short_account_ratio_last,8)))                                                                              |
| a7search6_351a19252c9ff820 | open_interest\|positioning   | z_safe_div_abs_csrank    |           8 |                4.89608  |           6.33586 |          8.85333 |                       0.651941 | SafeDiv(ZScore(TSRank(open_interest_value_last,336)),Abs(CSRank(ZScore(Mean(top_long_short_account_ratio_last,24)))))                                                     |
| a7search6_5a326bbdc99cd2b9 | open_interest\|positioning   | scaled_spread_abs        |           4 |                4.89019  |           5.53742 |         14.1914  |                       0.411634 | SafeDiv(Sub(CSRank(TSRank(open_interest_value_mean,504)),CSRank(CSRank(global_long_short_account_ratio_last))),Abs(CSRank(CSRank(global_long_short_account_ratio_last)))) |
| a7search6_e7ee64f0ef980aca | open_interest\|positioning   | safe_div_abs             |           8 |                4.66778  |           6.16543 |         17.9742  |                       0.346736 | SafeDiv(TSRank(open_interest_value_last,504),Abs(Mean(top_long_short_account_ratio_last,8)))                                                                              |
| a7search6_5a326bbdc99cd2b9 | open_interest\|positioning   | scaled_spread_abs        |           8 |                4.12518  |           6.01743 |         17.6046  |                       0.103516 | SafeDiv(Sub(CSRank(TSRank(open_interest_value_mean,504)),CSRank(CSRank(global_long_short_account_ratio_last))),Abs(CSRank(CSRank(global_long_short_account_ratio_last)))) |
| a7search6_8185d7e38fbfef0a | basis\|open_interest         | adjacent_signed_rank     |          24 |                2.16634  |           3.66468 |          5.93082 |                       0.180967 | Mul(CSRank(ZScore(Mean(open_interest_mean,12))),Sign(Decay(mark_index_basis_bps,336)))                                                                                    |
| a7search6_370b9d993902426e | open_interest\|taker_flow    | adjacent_spread_rank     |           4 |                2.12792  |           2.88422 |         13.6746  |                       0.365145 | Sub(CSRank(TSRank(open_interest_value_last,504)),CSRank(Mean(taker_buy_sell_volume_ratio_last,72)))                                                                       |
| a7search6_229924c832dd5901 | open_interest\|premium       | adjacent_signed_rank     |          24 |                1.90384  |           2.92514 |          5.9645  |                       0.427901 | Mul(CSRank(Mean(open_interest_mean,8)),Sign(Mean(premium_close_bps,48)))                                                                                                  |
| a7search6_5a7a41644c28a05a | open_interest\|premium       | adjacent_signed_rank     |          24 |                1.73821  |           3.10159 |          5.80861 |                       0.465944 | Mul(CSRank(Mean(open_interest_mean,12)),Sign(Mean(premium_close_bps,48)))                                                                                                 |
| a7search6_0159a7544af64b1d | basis\|positioning           | adjacent_spread_rank     |          24 |                1.68071  |           2.89055 |          8.60733 |                       0.250599 | Sub(CSRank(ZScore(Mean(account_position_divergence,24))),CSRank(Decay(mark_index_basis_bps,336)))                                                                         |
| a7search6_2e796ac0b2a688c4 | open_interest\|premium       | adjacent_mul             |          24 |                1.36465  |           2.44163 |          2.44163 |                       0.877144 | Mul(open_interest_last,Mean(premium_close_bps,504))                                                                                                                       |
| a7search6_370b9d993902426e | open_interest\|taker_flow    | adjacent_spread_rank     |           8 |                1.02761  |           3.07172 |         17.3861  |                       0.160125 | Sub(CSRank(TSRank(open_interest_value_last,504)),CSRank(Mean(taker_buy_sell_volume_ratio_last,72)))                                                                       |
| a7search6_54fa70ba1036adfc | open_interest\|taker_flow    | adjacent_spread_rank     |           4 |                0.974086 |           1.64815 |         14.9238  |                       0.556387 | Sub(CSRank(TSRank(open_interest_value_last,504)),CSRank(Decay(taker_buy_sell_volume_ratio_mean,72)))                                                                      |
| a7search6_40090b5c3ec8edfc | positioning\|taker_flow      | adjacent_mul             |           8 |                0.486828 |           1.63327 |         15.2285  |                       0.509209 | Mul(ZScore(top_long_short_account_ratio_last),Decay(taker_buy_sell_volume_ratio_mean,8))                                                                                  |

## Rejection Reasons

| hard_reject_reason                 |   count |
|:-----------------------------------|--------:|
| oos_control_dominated              |     606 |
| oos_lag_stale_dominated            |     553 |
| shuffle_control_dominated_recent   |     293 |
| oos_shuffle_dominated              |     279 |
| oos_nonoverlap_floor_not_positive  |     273 |
| stress_floor_not_positive          |     231 |
| train_orientation_no_positive_edge |     107 |
| train_sortino_non_positive         |     106 |
| oos_net_mean_not_all_positive      |      97 |
| recent_sortino_non_positive        |      32 |

## Shard Decisions

| decision                                          |   count |
|:--------------------------------------------------|--------:|
| PASS_A7REWARD1_PORTFOLIO_REWARD_LEADERBOARD_BUILT |       7 |
| HOLD_A7REWARD1_REWARD_MODEL_OR_QUEUE_FAILED       |       5 |

## Notes

- This is a reward-gate aggregate, not alpha proof.
- Full formula is taken from the candidate `expression` column and backfilled from shard queues when needed.
- Launcher status conflicts are diagnostic because shard manifests are the source of truth.
