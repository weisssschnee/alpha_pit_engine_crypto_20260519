# CRYPTO A7V3S0 Reward Sharded Aggregate 20260613

Decision: `PASS_A7V3S0_REWARD_SHARDED_AGGREGATE_READY`

## Counts

- expected_shards: `1`
- manifest_count: `1`
- accepted_rows: `1`
- accepted_unique_blueprints: `1`
- accepted_expression_missing: `0`
- reward_rows: `16`
- split_metric_rows: `480`
- eval_error_rows: `0`
- launcher_status_conflicts: `0`

## Accepted By Semantic Pair

| semantic_pair   |   count |
|:----------------|--------:|
| basis\|premium  |       1 |

## Accepted By Motif

| motif      |   count |
|:-----------|--------:|
| smooth_mul |       1 |

## Accepted By Horizon

|   horizon_h |   count |
|------------:|--------:|
|          24 |       1 |

## Top Accepted With Full Formula

| blueprint_id            | semantic_pair   | motif      |   horizon_h |   min_oos_floor_sortino |   min_oos_sortino |   recent_sortino |   recent_shuffle_control_ratio | formula                                                                       |
|:------------------------|:----------------|:-----------|------------:|------------------------:|------------------:|-----------------:|-------------------------------:|:------------------------------------------------------------------------------|
| a7v3s0_37b921db0b74a15a | basis\|premium  | smooth_mul |          24 |                 0.85222 |           1.81475 |          1.81475 |                       0.356316 | Mul(Decay(premium_abs_state,336),Abs(ZScore(Mean(mark_trade_basis_bps,168)))) |

## Rejection Reasons

| hard_reject_reason                 |   count |
|:-----------------------------------|--------:|
| oos_control_dominated              |      15 |
| oos_lag_stale_dominated            |      13 |
| stress_floor_not_positive          |      11 |
| shuffle_control_dominated_recent   |       8 |
| oos_shuffle_dominated              |       6 |
| oos_nonoverlap_floor_not_positive  |       3 |
| train_orientation_no_positive_edge |       2 |

## Shard Decisions

| decision                                          |   count |
|:--------------------------------------------------|--------:|
| PASS_A7REWARD1_PORTFOLIO_REWARD_LEADERBOARD_BUILT |       1 |

## Notes

- This is a reward-gate aggregate, not alpha proof.
- Full formula is taken from the candidate `expression` column and backfilled from shard queues when needed.
- Launcher status conflicts are diagnostic because shard manifests are the source of truth.
