# Epoch-2 Compact Result

Decision: `FROZEN_DEVELOPMENT_EPOCH2_PARTIALLY_COMPLETED`
Recommendation: `REVISE_BLOCKER_DIRECTED_SEARCH_AND_REPEAT`

The frozen strict execution completed all 2,304 logical rows. A post-strict report schema omission was repaired without a new performance query.

| admission_policy         |   rows |   exact_identities |   survivors |   near_misses |   positive_net_lcb |   behaviour_clusters |   n_eff |   top_cluster_share |   hypotheses |   mechanisms |
|:-------------------------|-------:|-------------------:|------------:|--------------:|-------------------:|---------------------:|--------:|--------------------:|-------------:|-------------:|
| GLOBAL_QUALITY           |    768 |                768 |           0 |           153 |                  4 |                  517 |  80.82  |          0.0664062  |           33 |           11 |
| HYBRID_QUALITY_DIVERSITY |    768 |                768 |           0 |            53 |                  2 |                  698 | 524.754 |          0.0169271  |           26 |            9 |
| STRATIFIED_DIVERSITY     |    768 |                768 |           0 |            31 |                  2 |                  715 | 624.814 |          0.00651042 |           20 |            3 |

| adaptive_lane       | control_lane                |   adaptive_rows |   control_rows |   adaptive_survivor_rate |   control_survivor_rate |   adaptive_near_miss_rate |   control_near_miss_rate |   adaptive_blocker_delta_median |   control_blocker_delta_median |   adaptive_behaviour_clusters |   control_behaviour_clusters | verdict             |
|:--------------------|:----------------------------|----------------:|---------------:|-------------------------:|------------------------:|--------------------------:|-------------------------:|--------------------------------:|-------------------------------:|------------------------------:|-----------------------------:|:--------------------|
| evolutionary_repair | evolutionary_random_control |             394 |            345 |                        0 |                       0 |                 0.119289  |                 0.263768 |                    -4.05413e-05 |                   -2.262e-05   |                           245 |                          170 | NO_ADAPTIVE_SUCCESS |
| local_mcts_repair   | local_mcts_random_control   |             426 |            132 |                        0 |                       0 |                 0.0539906 |                 0.227273 |                    -5.06199e-05 |                   -3.03417e-05 |                           248 |                           79 | NO_ADAPTIVE_SUCCESS |
| llm_typed_repair    | llm_random_repair_control   |             125 |             79 |                        0 |                       0 |                 0.104     |                 0.35443  |                    -3.42095e-05 |                   -1.21372e-05 |                            68 |                           42 | NO_ADAPTIVE_SUCCESS |

- Shared exact evaluation queries: 1488 / 2304 logical strict rows
- Median parent-to-child blocker distance delta: -3.7225299e-05
- Local MCTS top mechanism/primitive concentration: 0.343841
- Hybrid admitted-identity 60/40 contract preserved: False
- Hybrid results must not be described as a valid 60/40 control because quality share was applied before exact-identity dedup.
- Bias audit: `HOLD_RESEARCH`; all comparisons are development-only and OOS grade is NONE.
- `FORWARD_SEALED`
- `NO_CANDIDATE_PROMOTION`
- `NO_CROSS_EPOCH_ADAPTIVE_MEMORY`
