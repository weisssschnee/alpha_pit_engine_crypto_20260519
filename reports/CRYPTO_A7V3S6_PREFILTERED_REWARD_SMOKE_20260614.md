# CRYPTO A7V3S6 Prefiltered Reward Smoke - 20260614

## Decision

`HOLD_A7V3S6_PREFILTERED_REWARD_SMOKE_ZERO_ACCEPTED`

A7V3S6 ran a bounded strict-reward smoke on the A7V3S5 prefiltered queue. The run executed cleanly but produced zero accepted candidates.

This does not authorize a full reward wave, alpha proof, shadow, paper, or live.

## Scope

- Input queue: `a7v3s5_prefiltered_reward_prequeue.csv`
- Remote run root: `D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7v3s6_prefiltered_reward_smoke_720h_20260613`
- Aggregate runtime: `runtime/a7v3s6_prefiltered_reward_smoke_aggregate_20260614`
- Smoke shards executed: `16`
- Rows per shard: `16`
- Candidate rows tested: `256`
- Reward rows tested: `1024`
- Eval error rows: `0`
- Accepted rows: `0`

The generic sharded aggregate manifest reports `expected_shards = 186` because the shard plan was built for the full 2,963-row prefiltered queue. A7V3S6 intentionally authorized only the first 16 shards as a smoke. Therefore the important result is not aggregate PASS/HOLD status; it is zero accepted with zero eval errors.

## Rejection Reasons

| reason | count |
| --- | ---: |
| `oos_nonoverlap_floor_not_positive` | 1021 |
| `oos_net_mean_not_all_positive` | 998 |
| `stress_floor_not_positive` | 951 |
| `oos_control_dominated` | 888 |
| `oos_lag_stale_dominated` | 845 |
| `train_orientation_no_positive_edge` | 806 |
| `oos_shuffle_dominated` | 734 |
| `recent_sortino_non_positive` | 674 |
| `shuffle_control_dominated_recent` | 671 |

## Top Recent Winners Still Failed

The highest recent-window candidates were not close to promotion. They showed large recent Sortino but collapsed on OOS floor, stress floor, and control/lag-stale checks.

Examples:

| semantic_pair | motif | horizon | recent_sortino | min_oos_floor_sortino | stress_floor_sortino | failure |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| liquidity\|liquidity | signed_rank_gate | 24 | 29.02 | -4.33 | -2.36 | OOS floor, stress, control, lag-stale |
| liquidity\|liquidity | signed_rank_gate | 24 | 28.99 | -4.30 | -2.33 | OOS floor, stress, control, lag-stale |
| liquidity\|liquidity | smooth_mul | 24 | 27.83 | -5.10 | -3.20 | OOS floor, stress, control, lag-stale |
| liquidity\|taker_flow | spread_rank | 24 | 22.77 | -7.56 | -2.64 | OOS floor, stress, control, lag-stale |
| liquidity\|positioning | smooth_mul | 24 | 19.72 | -6.97 | -5.75 | OOS floor, stress, control, lag-stale |

## What Improved

A7V3S4/A7V3S5 did improve governance:

- the old A7V3S3 queue was stopped instead of blindly continued;
- known control/stale-dominated pair-motif structures were removed before reward;
- the A7V3S5 queue preserved breadth: 42 semantic pairs, 10 motifs, 2,695 skeletons.

## What Did Not Improve

The prefiltered queue still failed the strict reward gate:

- zero accepted rows;
- OOS floor failures remain nearly universal;
- stress floor failures remain dominant;
- many recent winners still fail control and lag/stale checks.

This means the problem is no longer only bad queue governance. The current formula space itself is still producing recent-window artifacts rather than portable mechanisms.

## Interpretation

Continuing the A7V3S5 queue into a full reward wave would waste compute. The filter reduced obvious pollution but did not produce reward-eligible candidates.

The next project move should not be to relax the reward gate. The next move should change candidate construction:

- reduce direct liquidity-volume self-products and same-family rank gates;
- require pre-reward OOS proxy evidence before reward evaluation;
- bias generation toward regime-conditioned mechanisms with explicit crisis-state diversity;
- build small batches from new construction rules, then run the same strict smoke.

## Authorization

Allowed next:

- A7V3S7 candidate construction redesign,
- pre-reward OOS proxy filter,
- small strict reward smoke on a newly constructed queue.

Not authorized:

- full A7V3S5 reward wave,
- continuing the A7V3S6 shard plan beyond smoke,
- alpha proof,
- shadow / paper / live.

