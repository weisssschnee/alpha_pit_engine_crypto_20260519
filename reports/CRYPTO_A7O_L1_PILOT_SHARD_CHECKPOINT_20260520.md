# Crypto A7O-L1 Pilot Shard Checkpoint

- generated_at: `2026-05-20T15:07:12Z`
- decision: `HOLD_A7O_L1_PILOT_CHECKPOINT`
- pilot_only: `True`
- executes_search: `True`
- executes_replay: `True`
- authorizes_next_64_cell_checkpoint: `False`
- authorizes_full_l1_without_checkpoint: `False`
- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`
- blockers: `['liquidity_volatility_deep_share']`

## Checkpoint Metrics

| metric                                      |          value |
|:--------------------------------------------|---------------:|
| generated                                   | 131072         |
| strict_replay_selected                      |   1536         |
| deep_audit_selected                         |    192         |
| eval_failure_count                          |      0         |
| fold_metric_missing_rate                    |      0         |
| liquidity_volatility_deep_share             |      0.1875    |
| single_horizon_deep_share                   |      0.171875  |
| single_return_corr_cluster_share            |      0.0520833 |
| active_cells_with_valid_deep_audit          |     64         |
| post_may_eligible_deep_survivors            |     49         |
| placebo_or_null_research_candidates         |      0         |
| single_hypothesis_family_share              |      0.125     |
| single_feature_operator_horizon_motif_share |      0.015625  |

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
| A7O_PILOT_MAY_VETOED_NEAR_MISS |      77 |
| A7O_PILOT_RESEARCH_CANDIDATE   |      49 |
| A7O_PILOT_REJECTED             |      38 |
| A7O_PILOT_PRE_MAY_NEAR_MISS    |      16 |
| NEGATIVE_CONTROL               |      12 |

## Boundary

This pilot checkpoint can only authorize the next 64-cell checkpoint. It cannot authorize alpha proof, shadow, paper, live, L2, or L3.