# CRYPTO A7AB-9 SURVIVOR FREEZE CONTRACT

Generated: 2026-05-29T06:38:52Z

## Decision

`PASS_A7AB9_SURVIVOR_FREEZE_REPRESENTATIVE_POOL_WITH_WARNINGS`

A7AB-9 freezes A7AB-8 forensic survivors into a representative pool. It does not authorize formula search, large search, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_a7ac0_representative_forensic_contract": true,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search_execution": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7AB9_SURVIVOR_FREEZE_REPRESENTATIVE_POOL_WITH_WARNINGS",
  "executes_contract_only": true,
  "executes_replay": false,
  "executes_search": false,
  "executes_training": false,
  "generated_at": "2026-05-29T06:38:52Z",
  "input_a7ab8_decision": "PASS_A7AB8_FORENSIC_SURVIVORS_FOUND_EXECUTION_HOLD",
  "representative_rows": 8,
  "stage": "A7AB-9",
  "survivor_candidates": 14,
  "survivor_clusters": 8,
  "survivor_rows": 15,
  "top_cluster_share": 0.4,
  "top_label_share": 1.0,
  "uses_may": false,
  "warnings": [
    "top_return_corr_cluster_share_gt_35pct",
    "single_label_family_dominates"
  ]
}
```

## Survivor Label Audit

| label_family            |   horizon_h |   survivor_rows |   survivor_candidates |   median_control_ratio |   median_recent_spread |
|:------------------------|------------:|----------------:|----------------------:|-----------------------:|-----------------------:|
| L7_ranked_future_return |           1 |               9 |                     9 |               0.861079 |              0.0320244 |
| L7_ranked_future_return |           4 |               6 |                     6 |               0.669442 |              0.0322281 |

## Survivor Cluster Audit

|   return_corr_cluster |   survivor_rows |   survivor_candidates |   median_control_ratio |   median_recent_spread |
|----------------------:|----------------:|----------------------:|-----------------------:|-----------------------:|
|                     1 |               6 |                     6 |               0.95529  |              0.0335111 |
|                     0 |               2 |                     2 |               0.669442 |              0.0361178 |
|                     4 |               2 |                     2 |               0.326569 |              0.0170707 |
|                     2 |               1 |                     1 |               0.931427 |              0.0601275 |
|                     3 |               1 |                     1 |               0.359941 |              0.0285744 |
|                     5 |               1 |                     1 |               0.623753 |              0.0284546 |
|                    15 |               1 |                     1 |               0.789442 |              0.0117063 |
|                    19 |               1 |                     1 |               0.603111 |              0.0147868 |

## Representative Survivor Pool

|   representative_rank | candidate_id           | label_family            |   horizon_h |   orientation_from_train |   oriented_validation_spread |   oriented_test_spread |   oriented_recent_spread |   one_bar_lag_recent_oriented |   control_ratio_premay_max | control_ratio_warning_ge_0_80   |   turnover_proxy |   cost10_recent_oriented |   top_symbol_abs_contribution_share | top_symbol   |   top_month_abs_contribution_share | top_month   | decision                | clue_key                                           |   return_corr_cluster |   representative_score |
|----------------------:|:-----------------------|:------------------------|------------:|-------------------------:|-----------------------------:|-----------------------:|-------------------------:|------------------------------:|---------------------------:|:--------------------------------|-----------------:|-------------------------:|------------------------------------:|:-------------|-----------------------------------:|:------------|:------------------------|:---------------------------------------------------|----------------------:|-----------------------:|
|                     1 | a7ab3_6e301587da1c1fa3 | L7_ranked_future_return |           4 |                       -1 |                   0.0505124  |             0.0550301  |                0.0601275 |                     0.0593572 |                   0.931427 | True                            |         0.158994 |                0.0599685 |                           0.0476837 | BTCUSDT      |                          0.0666756 | 2025-08     | A7AB8_FORENSIC_SURVIVOR | a7ab3_6e301587da1c1fa3\|L7_ranked_future_return\|4 |                     2 |              0.156197  |
|                     2 | a7ab3_6e301587da1c1fa3 | L7_ranked_future_return |           1 |                       -1 |                   0.0325732  |             0.0358993  |                0.0320244 |                     0.0301622 |                   0.843594 | True                            |         0.159099 |                0.0318653 |                           0.0469047 | BTCUSDT      |                          0.0663701 | 2025-08     | A7AB8_FORENSIC_SURVIVOR | a7ab3_6e301587da1c1fa3\|L7_ranked_future_return\|1 |                     1 |              0.0919019 |
|                     3 | a7ab3_4092255ee6888704 | L7_ranked_future_return |           4 |                       -1 |                   0.0237295  |             0.0317847  |                0.0358818 |                     0.0363595 |                   0.671699 | False                           |         1.17076  |                0.034711  |                           0.0297737 | 1000RATSUSDT |                          0.065268  | 2025-10     | A7AB8_FORENSIC_SURVIVOR | a7ab3_4092255ee6888704\|L7_ranked_future_return\|4 |                     0 |              0.0835082 |
|                     4 | a7ab3_0bc78809db3a1428 | L7_ranked_future_return |           4 |                       -1 |                   0.0185042  |             0.0240427  |                0.0284546 |                     0.0252509 |                   0.623753 | False                           |         0.355817 |                0.0280988 |                           0.0349647 | 1000RATSUSDT |                          0.0666161 | 2025-10     | A7AB8_FORENSIC_SURVIVOR | a7ab3_0bc78809db3a1428\|L7_ranked_future_return\|4 |                     5 |              0.0644081 |
|                     5 | a7ab3_165c7d8966b27a17 | L7_ranked_future_return |           4 |                       -1 |                   0.0169971  |             0.0171859  |                0.0285744 |                     0.0240342 |                   0.359941 | False                           |         0.731921 |                0.0278425 |                           0.0341902 | 1000RATSUSDT |                          0.0663118 | 2025-10     | A7AB8_FORENSIC_SURVIVOR | a7ab3_165c7d8966b27a17\|L7_ranked_future_return\|4 |                     3 |              0.0584262 |
|                     6 | a7ab3_6eb23cd8ce4aeef1 | L7_ranked_future_return |           1 |                        1 |                   0.01496    |             0.0163893  |                0.0176457 |                     0.0164682 |                   0.324949 | False                           |         0.337518 |                0.0173082 |                           0.0344432 | 1000RATSUSDT |                          0.0667769 | 2025-10     | A7AB8_FORENSIC_SURVIVOR | a7ab3_6eb23cd8ce4aeef1\|L7_ranked_future_return\|1 |                     4 |              0.0454081 |
|                     7 | a7ab3_04daf24ce962db97 | L7_ranked_future_return |           1 |                       -1 |                   0.0132668  |             0.0115049  |                0.0147868 |                     0.0136108 |                   0.603111 | False                           |         0.281515 |                0.0145053 |                           0.0259285 | 1000RATSUSDT |                          0.0665965 | 2025-10     | A7AB8_FORENSIC_SURVIVOR | a7ab3_04daf24ce962db97\|L7_ranked_future_return\|1 |                    19 |              0.0332458 |
|                     8 | a7ab3_2ad4a9e8d3c38900 | L7_ranked_future_return |           4 |                        1 |                   0.00609494 |             0.00553958 |                0.0117063 |                     0.010573  |                   0.789442 | False                           |         1.31266  |                0.0103937 |                           0.0427526 | 1000RATSUSDT |                          0.0663998 | 2026-01     | A7AB8_FORENSIC_SURVIVOR | a7ab3_2ad4a9e8d3c38900\|L7_ranked_future_return\|4 |                    15 |              0.0141337 |
