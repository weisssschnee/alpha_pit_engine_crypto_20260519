# Crypto A7O-L1 Pilot Shard Checkpoint

- generated_at: `2026-05-20T15:47:13Z`
- decision: `PASS_A7O_L1_PILOT_CHECKPOINT_READY_FOR_NEXT_64_CELLS`
- pilot_only: `True`
- executes_search: `True`
- executes_replay: `True`
- authorizes_next_64_cell_checkpoint: `True`
- authorizes_full_l1_without_checkpoint: `False`
- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`
- blockers: `[]`

## Checkpoint Metrics

| metric                                      | value                                 |
|:--------------------------------------------|:--------------------------------------|
| generated                                   | 131072                                |
| strict_replay_selected                      | 1536                                  |
| deep_audit_selected                         | 192                                   |
| eval_failure_count                          | 0                                     |
| fold_metric_missing_rate                    | 0.0                                   |
| deep_selection_policy                       | global_liquidity_volatility_cap_15pct |
| liquidity_volatility_deep_share             | 0.14583333333333334                   |
| liquidity_volatility_deep_count             | 28                                    |
| liquidity_volatility_deep_cap               | 28                                    |
| liquidity_volatility_deep_forced_fill_count | 0                                     |
| single_horizon_deep_share                   | 0.16666666666666666                   |
| single_return_corr_cluster_share            | 0.052083333333333336                  |
| active_cells_with_valid_deep_audit          | 62                                    |
| post_may_eligible_deep_survivors            | 49                                    |
| placebo_or_null_research_candidates         | 0                                     |
| single_hypothesis_family_share              | 0.125                                 |
| single_feature_operator_horizon_motif_share | 0.03125                               |

## Generation Funnel

| stage                      |   count |
|:---------------------------|--------:|
| generated                  |  131072 |
| unique_expression          |  120406 |
| selected_for_strict_replay |    1536 |
| evaluated_without_failure  |    1536 |
| selected_for_deep_audit    |     192 |
| post_may_eligible_pool     |      49 |

## Deep Audit Decision Counts

| candidate_decision             |   count |
|:-------------------------------|--------:|
| A7O_PILOT_MAY_VETOED_NEAR_MISS |      80 |
| A7O_PILOT_RESEARCH_CANDIDATE   |      49 |
| A7O_PILOT_REJECTED             |      37 |
| A7O_PILOT_PRE_MAY_NEAR_MISS    |      14 |
| NEGATIVE_CONTROL               |      12 |

## Boundary

This pilot checkpoint can only authorize the next 64-cell checkpoint. It cannot authorize alpha proof, shadow, paper, live, L2, or L3.