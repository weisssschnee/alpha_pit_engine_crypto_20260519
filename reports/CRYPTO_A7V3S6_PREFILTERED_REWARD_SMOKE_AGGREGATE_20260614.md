# CRYPTO A7V3S0 Reward Sharded Aggregate 20260613

Decision: `HOLD_A7V3S0_REWARD_SHARDED_AGGREGATE_INCOMPLETE_OR_DIRTY`

## Counts

- expected_shards: `186`
- manifest_count: `16`
- accepted_rows: `0`
- accepted_unique_blueprints: `0`
- accepted_expression_missing: `0`
- reward_rows: `1024`
- split_metric_rows: `30720`
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
| oos_nonoverlap_floor_not_positive  |    1021 |
| oos_net_mean_not_all_positive      |     998 |
| stress_floor_not_positive          |     951 |
| oos_control_dominated              |     888 |
| oos_lag_stale_dominated            |     845 |
| train_orientation_no_positive_edge |     806 |
| oos_shuffle_dominated              |     734 |
| recent_sortino_non_positive        |     674 |
| shuffle_control_dominated_recent   |     671 |

## Shard Decisions

| decision                                    |   count |
|:--------------------------------------------|--------:|
| HOLD_A7REWARD1_REWARD_MODEL_OR_QUEUE_FAILED |      16 |

## Notes

- This is a reward-gate aggregate, not alpha proof.
- Full formula is taken from the candidate `expression` column and backfilled from shard queues when needed.
- Launcher status conflicts are diagnostic because shard manifests are the source of truth.
