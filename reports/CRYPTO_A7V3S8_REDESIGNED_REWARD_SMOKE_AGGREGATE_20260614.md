# CRYPTO A7V3S0 Reward Sharded Aggregate 20260613

Decision: `HOLD_A7V3S0_REWARD_SHARDED_AGGREGATE_INCOMPLETE_OR_DIRTY`

## Counts

- expected_shards: `64`
- manifest_count: `32`
- accepted_rows: `0`
- accepted_unique_blueprints: `0`
- accepted_expression_missing: `0`
- reward_rows: `2048`
- split_metric_rows: `61440`
- eval_error_rows: `0`
- launcher_status_conflicts: `0`

## Accepted By Semantic Pair

`<empty>`

## Accepted By Motif

`<empty>`

## Accepted By Horizon

`<empty>`

## Top Accepted With Full Formula

`<missing columns>`

## Rejection Reasons

| hard_reject_reason                 |   count |
|:-----------------------------------|--------:|
| oos_nonoverlap_floor_not_positive  |    1998 |
| oos_net_mean_not_all_positive      |    1911 |
| oos_control_dominated              |    1672 |
| stress_floor_not_positive          |    1671 |
| oos_lag_stale_dominated            |    1609 |
| oos_shuffle_dominated              |    1375 |
| shuffle_control_dominated_recent   |    1188 |
| train_orientation_no_positive_edge |    1114 |
| recent_sortino_non_positive        |    1062 |
| non_finite_diagnostic_composite    |     240 |

## Shard Decisions

| decision                                    |   count |
|:--------------------------------------------|--------:|
| HOLD_A7REWARD1_REWARD_MODEL_OR_QUEUE_FAILED |      32 |

## Notes

- This is a reward-gate aggregate, not alpha proof.
- Full formula is taken from the candidate `expression` column and backfilled from shard queues when needed.
- Launcher status conflicts are diagnostic because shard manifests are the source of truth.
