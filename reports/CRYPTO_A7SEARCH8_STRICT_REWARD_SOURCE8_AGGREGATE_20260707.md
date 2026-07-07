# CRYPTO A7V3S0 Reward Sharded Aggregate 20260613

Decision: `PASS_A7V3S0_REWARD_SHARDED_AGGREGATE_READY`

## Counts

- expected_shards: `7`
- manifest_count: `7`
- accepted_rows: `11`
- accepted_unique_blueprints: `11`
- accepted_expression_missing: `0`
- reward_rows: `396`
- split_metric_rows: `12240`
- eval_error_rows: `0`
- launcher_status_conflicts: `0`

## Accepted By Semantic Pair

| semantic_pair                |   count |
|:-----------------------------|--------:|
| funding_dense\|open_interest |      10 |
| open_interest\|positioning   |       1 |

## Accepted By Motif

| motif                       |   count |
|:----------------------------|--------:|
| shadow_selected_exact_probe |       5 |
| shadow_selected_rank_wrap   |       5 |
| positive_prior_safe_div_abs |       1 |

## Accepted By Horizon

|   horizon_h |   count |
|------------:|--------:|
|          24 |       7 |
|           8 |       4 |

## Top Accepted With Full Formula

| blueprint_id               | semantic_pair                | motif                       |   horizon_h |   min_oos_floor_sortino |   min_oos_sortino |   recent_sortino |   recent_shuffle_control_ratio | formula                                                                                                             |
|:---------------------------|:-----------------------------|:----------------------------|------------:|------------------------:|------------------:|-----------------:|-------------------------------:|:--------------------------------------------------------------------------------------------------------------------|
| a7search7_9168babaa32dc76c | funding_dense\|open_interest | shadow_selected_rank_wrap   |           8 |                8.50321  |          11.8745  |         18.3882  |                      0.31691   | CSRank(CSRank(SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72)))))) |
| a7search7_1579560a060d20ec | funding_dense\|open_interest | shadow_selected_exact_probe |           8 |                8.50321  |          11.8745  |         18.3882  |                      0.398843  | CSRank(SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72)))))         |
| a7search7_fa2bcb9f82277249 | funding_dense\|open_interest | shadow_selected_exact_probe |           8 |                2.11649  |           4.08333 |          4.08333 |                      0.842827  | SafeDiv(TSRank(open_interest_value_mean,240),Abs(TSRank(global_long_short_account_ratio_last,24)))                  |
| a7search7_f57e92c650f903b6 | funding_dense\|open_interest | shadow_selected_rank_wrap   |           8 |                2.11649  |           4.08333 |          4.08333 |                      0.972092  | CSRank(SafeDiv(TSRank(open_interest_value_mean,240),Abs(TSRank(global_long_short_account_ratio_last,24))))          |
| a7search7_4e22e196bfeb8bce | open_interest\|positioning   | positive_prior_safe_div_abs |          24 |                1.06354  |           3.60958 |         16.2218  |                      0.246905  | SafeDiv(Delta(open_interest_value_last,240),Abs(ZScore(Mean(global_long_short_account_ratio_last,96))))             |
| a7search7_52353a2ad0ece8e8 | funding_dense\|open_interest | shadow_selected_rank_wrap   |          24 |                0.497889 |           3.43001 |         12.0121  |                      0.0730941 | CSRank(Mul(CSRank(CSRank(Delta(open_interest_value_mean,240))),Sign(Decay(mark_index_basis_bps,72))))               |
| a7search7_e7180b1ba6a1df1a | funding_dense\|open_interest | shadow_selected_exact_probe |          24 |                0.497889 |           3.43001 |         12.0121  |                      0.30089   | Mul(CSRank(CSRank(Delta(open_interest_value_mean,240))),Sign(Decay(mark_index_basis_bps,72)))                       |
| a7search7_d404a68b39d27dbd | funding_dense\|open_interest | shadow_selected_exact_probe |          24 |                0.318659 |           4.20618 |         12.6676  |                      0.171326  | Mul(CSRank(CSRank(Delta(open_interest_value_mean,240))),Sign(CSRank(Delta(mark_index_basis_bps,12))))               |
| a7search7_124582cf9a6d54a0 | funding_dense\|open_interest | shadow_selected_rank_wrap   |          24 |                0.318659 |           4.20618 |         12.6676  |                      0.177144  | CSRank(Mul(CSRank(CSRank(Delta(open_interest_value_mean,240))),Sign(CSRank(Delta(mark_index_basis_bps,12)))))       |
| a7search7_8ecc4a9a053a0d59 | funding_dense\|open_interest | shadow_selected_rank_wrap   |          24 |                0.318659 |           4.20618 |         12.6676  |                      0.204427  | CSRank(Mul(CSRank(Delta(open_interest_value_mean,240)),Sign(TSRank(premium_abs_state,504))))                        |
| a7search7_b2e42dec52899bd0 | funding_dense\|open_interest | shadow_selected_exact_probe |          24 |                0.318659 |           4.20618 |         12.6676  |                      0.293501  | Mul(CSRank(Delta(open_interest_value_mean,240)),Sign(TSRank(premium_abs_state,504)))                                |

## Rejection Reasons

| hard_reject_reason                 |   count |
|:-----------------------------------|--------:|
| source_lag_required_not_proven     |     372 |
| oos_control_dominated              |     325 |
| oos_lag_stale_dominated            |     302 |
| oos_shuffle_dominated              |     165 |
| oos_nonoverlap_floor_not_positive  |     154 |
| shuffle_control_dominated_recent   |     143 |
| stress_floor_not_positive          |      82 |
| oos_net_mean_not_all_positive      |      61 |
| train_sortino_non_positive         |      52 |
| train_orientation_no_positive_edge |      51 |
| recent_sortino_non_positive        |       3 |

## Shard Decisions

| decision                                          |   count |
|:--------------------------------------------------|--------:|
| HOLD_A7REWARD1_REWARD_MODEL_OR_QUEUE_FAILED       |       5 |
| PASS_A7REWARD1_PORTFOLIO_REWARD_LEADERBOARD_BUILT |       2 |

## Notes

- This is a reward-gate aggregate, not alpha proof.
- Full formula is taken from the candidate `expression` column and backfilled from shard queues when needed.
- Launcher status conflicts are diagnostic because shard manifests are the source of truth.
