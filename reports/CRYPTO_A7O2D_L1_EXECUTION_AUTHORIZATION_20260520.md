# Crypto A7O-2D L1 Execution Authorization

- generated_at: `2026-05-20T13:54:34Z`
- decision: `AUTHORIZED_A7O_L1_PROTECTED_PILOT_AND_CONDITIONAL_FULL_RUN`
- executes_search: `False`
- executes_replay: `False`
- authorizes_l1_pilot_execution: `True`
- authorizes_full_l1_continuation_after_pilot_pass: `True`
- authorizes_unconditional_full_l1_execution: `False`
- authorizes_l2_execution: `False`
- authorizes_l3_execution: `False`
- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`

## Authorization Matrix

| scope                                     | authorized   | reason                                               |
|:------------------------------------------|:-------------|:-----------------------------------------------------|
| A7O-L1 pilot shard                        | True         | A7O-2C4 semantic/horizon/fold gates passed           |
| A7O-L1 full continuation after pilot pass | True         | conditional on pilot shard checkpoint gates          |
| A7O-L1 unconditional full run             | False        | pilot shard and every-64-cell checkpoint required    |
| A7O-L2                                    | False        | requires L1 eligible pool and diversity pass         |
| A7O-L3                                    | False        | contract-only, not authorized                        |
| alpha proof                               | False        | A7O-L1 can only produce research candidate pool      |
| shadow/paper/live                         | False        | requires future alpha proof and execution validation |

## Execution Plan

| stage                     |   cells |   generated_per_cell |   total_generated |   strict_replay_per_cell |   strict_replay_total |   deep_audit_per_cell |   deep_audit_total | checkpoint     |
|:--------------------------|--------:|---------------------:|------------------:|-------------------------:|----------------------:|----------------------:|-------------------:|:---------------|
| A7O-L1 pilot shard        |      64 |                 2048 |            131072 |                       24 |                  1536 |                     3 |                192 | after pilot    |
| A7O-L1 full protected run |    1024 |                 2048 |           2097152 |                       24 |                 24576 |                     3 |               3072 | every 64 cells |

## Checkpoint Stop Rules

| gate                                | threshold              | action                            |
|:------------------------------------|:-----------------------|:----------------------------------|
| may_leakage_violations              | 0                      | stop                              |
| fold_metric_missing_rate            | <= 0.01                | stop_or_repair                    |
| liquidity_volatility_deep_share     | <= 0.15                | stop_if_exceeded_after_checkpoint |
| single_horizon_deep_share           | <= 0.35                | stop_if_exceeded_after_checkpoint |
| single_return_corr_cluster_share    | <= 0.35                | stop_if_exceeded_after_checkpoint |
| placebo_or_null_research_candidates | 0                      | stop                              |
| post_may_eligible_deep_survivors    | >= 24 for full L1 pass | hold_if_not_met                   |

## Decision

A7O-L1 may start only as a protected pilot shard. Full L1 continuation requires pilot checkpoint review and then every-64-cell checkpoint monitoring. A7O-L1 can only produce a research candidate pool.