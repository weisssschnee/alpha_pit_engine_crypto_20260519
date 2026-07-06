# CRYPTO A7V3S0 Reward Sharded Aggregate 20260613

Decision: `PASS_A7V3S0_REWARD_SHARDED_AGGREGATE_READY`

## Counts

- expected_shards: `6`
- manifest_count: `6`
- accepted_rows: `5`
- accepted_unique_blueprints: `5`
- accepted_expression_missing: `0`
- reward_rows: `324`
- split_metric_rows: `9720`
- eval_error_rows: `0`
- launcher_status_conflicts: `0`

## Accepted By Semantic Pair

| semantic_pair                |   count |
|:-----------------------------|--------:|
| basis\|open_interest         |       2 |
| funding_dense\|open_interest |       1 |
| open_interest\|positioning   |       1 |
| open_interest\|premium       |       1 |

## Accepted By Motif

| motif                                                    |   count |
|:---------------------------------------------------------|--------:|
| positive_prior_signed_rank_strict_validation_validation  |       3 |
| positive_prior_safe_div_abs_strict_validation_validation |       1 |
| shadow_selected_rank_wrap_strict_validation_validation   |       1 |

## Accepted By Horizon

|   horizon_h |   count |
|------------:|--------:|
|          24 |       3 |
|           8 |       2 |

## Top Accepted With Full Formula

| blueprint_id                                                                | semantic_pair                | motif                                                    |   horizon_h |   min_oos_floor_sortino |   min_oos_sortino |   recent_sortino |   recent_shuffle_control_ratio | formula                                                                                                     |
|:----------------------------------------------------------------------------|:-----------------------------|:---------------------------------------------------------|------------:|------------------------:|------------------:|-----------------:|-------------------------------:|:------------------------------------------------------------------------------------------------------------|
| a7search6_vp_a7search7_vp_a7search7_3ac1a9eafa18b95f_8_canonical_canonical  | funding_dense\|open_interest | shadow_selected_rank_wrap_strict_validation_validation   |           8 |                8.50321  |          11.8745  |         18.3882  |                      0.398843  | CSRank(SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72))))) |
| a7search6_vp_a7search7_vp_a7search7_dec97465aedf9ce9_8_canonical_canonical  | open_interest\|positioning   | positive_prior_safe_div_abs_strict_validation_validation |           8 |                2.11649  |           4.08333 |          4.08333 |                      0.880889  | SafeDiv(TSRank(open_interest_value_mean,240),Abs(TSRank(global_long_short_account_ratio_last,24)))          |
| a7search6_vp_a7search7_vp_a7search7_1c97b872a07e39dc_24_canonical_canonical | basis\|open_interest         | positive_prior_signed_rank_strict_validation_validation  |          24 |                0.497889 |           3.43001 |         12.0121  |                      0.0730941 | Mul(CSRank(CSRank(Delta(open_interest_value_mean,240))),Sign(Decay(mark_index_basis_bps,72)))               |
| a7search6_vp_a7search7_vp_a7search7_58ba8c206cc57999_24_canonical_canonical | open_interest\|premium       | positive_prior_signed_rank_strict_validation_validation  |          24 |                0.318659 |           4.20618 |         12.6676  |                      0.107433  | Mul(CSRank(Delta(open_interest_value_mean,240)),Sign(TSRank(premium_abs_state,504)))                        |
| a7search6_vp_a7search7_vp_a7search7_3e5555ac440970e9_24_canonical_canonical | basis\|open_interest         | positive_prior_signed_rank_strict_validation_validation  |          24 |                0.318659 |           4.20618 |         12.6676  |                      0.488939  | Mul(CSRank(CSRank(Delta(open_interest_value_mean,240))),Sign(CSRank(Delta(mark_index_basis_bps,12))))       |

## Rejection Reasons

| hard_reject_reason                 |   count |
|:-----------------------------------|--------:|
| oos_nonoverlap_floor_not_positive  |     286 |
| oos_net_mean_not_all_positive      |     260 |
| oos_control_dominated              |     252 |
| source_lag_required_not_proven     |     248 |
| oos_lag_stale_dominated            |     245 |
| stress_floor_not_positive          |     194 |
| oos_shuffle_dominated              |     186 |
| shuffle_control_dominated_recent   |     142 |
| train_sortino_non_positive         |     122 |
| train_orientation_no_positive_edge |     118 |
| recent_sortino_non_positive        |      58 |
| train_sortino_overfit_gap          |      11 |

## Shard Decisions

| decision                                          |   count |
|:--------------------------------------------------|--------:|
| PASS_A7REWARD1_PORTFOLIO_REWARD_LEADERBOARD_BUILT |       4 |
| HOLD_A7REWARD1_REWARD_MODEL_OR_QUEUE_FAILED       |       2 |

## Notes

- This is a reward-gate aggregate, not alpha proof.
- Full formula is taken from the candidate `expression` column and backfilled from shard queues when needed.
- Launcher status conflicts are diagnostic because shard manifests are the source of truth.
