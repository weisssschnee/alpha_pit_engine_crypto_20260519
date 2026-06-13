# CRYPTO A7V3S0 Reward Sharded Aggregate 20260613

Decision: `PASS_A7V3S0_REWARD_SHARDED_AGGREGATE_READY`

## Counts

- expected_shards: `64`
- manifest_count: `64`
- accepted_rows: `40`
- accepted_unique_blueprints: `17`
- accepted_expression_missing: `0`
- reward_rows: `4096`
- split_metric_rows: `122880`
- eval_error_rows: `0`
- launcher_status_conflicts: `75`

## Accepted By Semantic Pair

| semantic_pair               |   count |
|:----------------------------|--------:|
| age\|positioning            |      15 |
| positioning\|universe_state |      15 |
| open_interest\|positioning  |       6 |
| open_interest\|regime       |       2 |
| positioning\|positioning    |       2 |

## Accepted By Motif

| motif                      |   count |
|:---------------------------|--------:|
| smooth_mul                 |      11 |
| safe_div_abs               |      10 |
| state_conditioned_signed   |      10 |
| spread_rank                |       4 |
| state_conditioned_rank_mul |       3 |
| signed_rank_gate           |       2 |

## Accepted By Horizon

|   horizon_h |   count |
|------------:|--------:|
|           4 |      15 |
|          24 |      14 |
|           8 |      11 |

## Top Accepted With Full Formula

| blueprint_id            | semantic_pair               | motif                      |   horizon_h |   min_oos_floor_sortino |   min_oos_sortino |   recent_sortino |   recent_shuffle_control_ratio | formula                                                                                               |
|:------------------------|:----------------------------|:---------------------------|------------:|------------------------:|------------------:|-----------------:|-------------------------------:|:------------------------------------------------------------------------------------------------------|
| a7v3s0_3ca94bc0070251af | age\|positioning            | safe_div_abs               |          24 |                 6.41663 |           8.18344 |         24.7706  |                       0.12484  | SafeDiv(Sign(TSRank(listing_age_days,8)),Abs(Decay(account_position_divergence,3)))                   |
| a7v3s0_6a69bfab2eae84f8 | age\|positioning            | safe_div_abs               |          24 |                 6.41663 |           8.18344 |         24.7706  |                       0.175533 | SafeDiv(Sign(TSRank(sqrt_listing_age_days,8)),Abs(Decay(account_position_divergence,3)))              |
| a7v3s0_6a69bfab2eae84f8 | age\|positioning            | safe_div_abs               |           8 |                 4.30808 |           6.06759 |         18.569   |                       0.280914 | SafeDiv(Sign(TSRank(sqrt_listing_age_days,8)),Abs(Decay(account_position_divergence,3)))              |
| a7v3s0_3ca94bc0070251af | age\|positioning            | safe_div_abs               |           8 |                 4.30808 |           6.06759 |         18.569   |                       0.47386  | SafeDiv(Sign(TSRank(listing_age_days,8)),Abs(Decay(account_position_divergence,3)))                   |
| a7v3s0_6a69bfab2eae84f8 | age\|positioning            | safe_div_abs               |           4 |                 3.29368 |           4.92299 |         14.8535  |                       0.626812 | SafeDiv(Sign(TSRank(sqrt_listing_age_days,8)),Abs(Decay(account_position_divergence,3)))              |
| a7v3s0_3ca94bc0070251af | age\|positioning            | safe_div_abs               |           4 |                 3.29368 |           4.92299 |         14.8535  |                       0.693282 | SafeDiv(Sign(TSRank(listing_age_days,8)),Abs(Decay(account_position_divergence,3)))                   |
| a7v3s0_e963df5fb6bbf714 | age\|positioning            | state_conditioned_signed   |           4 |                 2.66725 |           3.4908  |         15.677   |                       0.618854 | Mul(ZScore(Mean(account_position_divergence,3)),Sign(CSRank(log1p_listing_age_days)))                 |
| a7v3s0_814c94c49814ca36 | positioning\|universe_state | smooth_mul                 |           4 |                 2.66725 |           3.4908  |         15.677   |                       0.47458  | Mul(ZScore(Mean(account_position_divergence,3)),CSRank(active_universe_size))                         |
| a7v3s0_640ff34abc50d93a | positioning\|universe_state | state_conditioned_signed   |           4 |                 2.66725 |           3.4908  |         15.677   |                       0.682208 | Mul(ZScore(Mean(account_position_divergence,3)),Sign(Sign(TSRank(active_universe_size,6))))           |
| a7v3s0_93fc86066fa283e2 | positioning\|universe_state | spread_rank                |           4 |                 2.66725 |           3.4908  |         15.677   |                       0.651853 | Sub(CSRank(Sign(TSRank(active_universe_size,6))),CSRank(ZScore(Mean(account_position_divergence,3)))) |
| a7v3s0_213b4211c299271b | positioning\|universe_state | state_conditioned_signed   |           4 |                 2.59032 |           3.51993 |         15.6103  |                       0.589164 | Mul(Decay(account_position_divergence,3),Sign(CSRank(active_universe_size)))                          |
| a7v3s0_3df8b6fe945cb8d3 | positioning\|universe_state | state_conditioned_rank_mul |           4 |                 2.59032 |           3.51993 |         15.6103  |                       0.327495 | Mul(CSRank(Decay(account_position_divergence,3)),CSRank(CSRank(active_universe_size)))                |
| a7v3s0_043becf950a92ed6 | open_interest\|positioning  | smooth_mul                 |           4 |                 2.54495 |           3.28553 |         15.028   |                       0.619522 | Mul(Decay(account_position_divergence,3),Abs(ZScore(Mean(open_interest_value_mean,4))))               |
| a7v3s0_fa0f17d41e8adb0f | age\|positioning            | smooth_mul                 |           4 |                 2.54337 |           3.36815 |         15.5909  |                       0.473492 | Mul(Decay(log1p_listing_age_days,3),Decay(account_position_divergence,3))                             |
| a7v3s0_1472c56cba9ece8d | open_interest\|positioning  | safe_div_abs               |           4 |                 1.86521 |           2.96558 |         12.3428  |                       0.113104 | SafeDiv(ZScore(Mean(account_position_divergence,3)),Abs(Abs(ZScore(Mean(open_interest_mean,3)))))     |
| a7v3s0_cb342fafc984f5ee | open_interest\|regime       | safe_div_abs               |           4 |                 1.79882 |           2.42302 |          4.33158 |                       0.501499 | SafeDiv(Abs(ZScore(Mean(open_interest_value_last,336))),Abs(Decay(basis_dislocation_state,720)))      |
| a7v3s0_043becf950a92ed6 | open_interest\|positioning  | smooth_mul                 |          24 |                 1.63022 |           4.03113 |         16.8661  |                       0.227286 | Mul(Decay(account_position_divergence,3),Abs(ZScore(Mean(open_interest_value_mean,4))))               |
| a7v3s0_fa0f17d41e8adb0f | age\|positioning            | smooth_mul                 |          24 |                 1.54468 |           3.46782 |         16.5207  |                       0.380118 | Mul(Decay(log1p_listing_age_days,3),Decay(account_position_divergence,3))                             |
| a7v3s0_e963df5fb6bbf714 | age\|positioning            | state_conditioned_signed   |          24 |                 1.4949  |           3.40922 |         16.3447  |                       0.242684 | Mul(ZScore(Mean(account_position_divergence,3)),Sign(CSRank(log1p_listing_age_days)))                 |
| a7v3s0_814c94c49814ca36 | positioning\|universe_state | smooth_mul                 |          24 |                 1.4949  |           3.40922 |         16.3447  |                       0.380474 | Mul(ZScore(Mean(account_position_divergence,3)),CSRank(active_universe_size))                         |

## Rejection Reasons

| hard_reject_reason                 |   count |
|:-----------------------------------|--------:|
| oos_nonoverlap_floor_not_positive  |    4016 |
| oos_net_mean_not_all_positive      |    3902 |
| shuffle_control_dominated_recent   |    2643 |
| train_orientation_no_positive_edge |    2333 |
| recent_sortino_non_positive        |    2225 |
| non_finite_diagnostic_composite    |     176 |

## Shard Decisions

| decision                                          |   count |
|:--------------------------------------------------|--------:|
| HOLD_A7REWARD1_REWARD_MODEL_OR_QUEUE_FAILED       |      53 |
| PASS_A7REWARD1_PORTFOLIO_REWARD_LEADERBOARD_BUILT |      11 |

## Notes

- This is a reward-gate aggregate, not alpha proof.
- Full formula is taken from the candidate `expression` column and backfilled from shard queues when needed.
- Launcher status conflicts are diagnostic because shard manifests are the source of truth.
