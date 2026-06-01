# CRYPTO A7FF-CORE16ME BROADER H2 REPAIR EXECUTION

Generated: 2026-06-01T14:32:07Z

## Decision

`PASS_A7FFCORE16ME_H2_FLOOR_REPAIRED_READY_FOR_CORE16L`

CORE16ME executes the broader checkpointed H2/I4 strict-floor repair authorized by CORE16M. It does not execute replay, search, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "added_strict_h2_count": 1,
  "authorizes_alpha_proof": false,
  "authorizes_core16l": true,
  "authorizes_core17": false,
  "authorizes_formula_generation": false,
  "authorizes_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blueprint_count": 180,
  "chunk_count_completed": 6,
  "decision": "PASS_A7FFCORE16ME_H2_FLOOR_REPAIRED_READY_FOR_CORE16L",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T14:32:07Z",
  "h2_repair_candidate_count": 10,
  "next_allowed": "A7FF-CORE16L strict pre-seed queue lock audit",
  "repaired_queue_h2_count": 12,
  "repaired_queue_size": 96,
  "response_rows": 2880,
  "source_decision": "PASS_A7FFCORE16M_H2_FLOOR_RETAINED_READY_FOR_CORE16ME",
  "source_stage": "A7FF-CORE16M",
  "stage": "A7FF-CORE16ME"
}
```

## Decision Counts

| decision                                     |   count |
|:---------------------------------------------|--------:|
| HOLD_A7FFCORE16ME_PREMAY_UNSTABLE            |    2428 |
| HOLD_A7FFCORE16ME_CONTROL_LIKE               |     417 |
| A7FFCORE16ME_NEAR_MISS_CONTROL_MARGIN        |      25 |
| A7FFCORE16ME_H2_REPAIR_CANDIDATE_LAG_FRAGILE |       6 |
| A7FFCORE16ME_H2_REPAIR_CANDIDATE_LAG_OK      |       4 |

## Family Summary

| left_family   | right_family   | operator   |   response_rows |   blueprint_count |   candidate_count |   near_miss_count |   median_control_ratio |
|:--------------|:---------------|:-----------|----------------:|------------------:|------------------:|------------------:|-----------------------:|
| taker_flow    | liquidity      | SafeDiv    |             960 |                60 |                 6 |                 8 |                5.39306 |
| taker_flow    | liquidity      | Mul        |             960 |                60 |                 3 |                10 |                4.72077 |
| taker_flow    | open_interest  | SafeDiv    |             480 |                30 |                 1 |                 5 |                5.22543 |
| taker_flow    | open_interest  | Mul        |             480 |                30 |                 0 |                 2 |                5.4508  |

## Added Strict H2 Rows

| second_pass_family     | left_field                  | left_family   | right_field              | right_family   | left_transform   | right_transform   | operator   | priority_wave   | blueprint_id                                                                               | label_family                      |   label_horizon_h |   orientation_from_train |   premay_positive_split_count | premay_all_positive   |   control_ratio_premay_max |   one_bar_lag_recent_oriented | lag_ok   | h2_repair_candidate   | near_miss   | decision                                |   train_2024_n |   train_2024_mean_spread |   train_2024_tstat |   train_2024_nonoverlap_median_tstat |   train_2024_nonoverlap_min_tstat |   train_2024_positive_rate |   validation_2025H1_n |   validation_2025H1_mean_spread |   validation_2025H1_tstat |   validation_2025H1_nonoverlap_median_tstat |   validation_2025H1_nonoverlap_min_tstat |   validation_2025H1_positive_rate |   test_2025H2_n |   test_2025H2_mean_spread |   test_2025H2_tstat |   test_2025H2_nonoverlap_median_tstat |   test_2025H2_nonoverlap_min_tstat |   test_2025H2_positive_rate |   recent_oos_2026JanApr_n |   recent_oos_2026JanApr_mean_spread |   recent_oos_2026JanApr_tstat |   recent_oos_2026JanApr_nonoverlap_median_tstat |   recent_oos_2026JanApr_nonoverlap_min_tstat |   recent_oos_2026JanApr_positive_rate |   avg_n_obs_recent |   error |   lag_bonus |   non_l5_bonus |   priority_bonus |   selection_score | queue_role       |
|:-----------------------|:----------------------------|:--------------|:-------------------------|:---------------|:-----------------|:------------------|:-----------|:----------------|:-------------------------------------------------------------------------------------------|:----------------------------------|------------------:|-------------------------:|------------------------------:|:----------------------|---------------------------:|------------------------------:|:---------|:----------------------|:------------|:----------------------------------------|---------------:|-------------------------:|-------------------:|-------------------------------------:|----------------------------------:|---------------------------:|----------------------:|--------------------------------:|--------------------------:|--------------------------------------------:|-----------------------------------------:|----------------------------------:|----------------:|--------------------------:|--------------------:|--------------------------------------:|-----------------------------------:|----------------------------:|--------------------------:|------------------------------------:|------------------------------:|------------------------------------------------:|---------------------------------------------:|--------------------------------------:|-------------------:|--------:|------------:|---------------:|-----------------:|------------------:|:-----------------|
| H2_I4_near_miss_repair | kline_taker_buy_quote_share | taker_flow    | median_quote_volume_168h | liquidity      | delta_2h         | delta_1h          | SafeDiv    | True            | core16me_H2_kline_taker_buy_quote_share_delta_2h_SafeDiv_median_quote_volume_168h_delta_1h | L3_liquidity_tier_relative_return |                24 |                       -1 |                             3 | True                  |                   0.512878 |                   0.000554851 | True     | True                  | False       | A7FFCORE16ME_H2_REPAIR_CANDIDATE_LAG_OK |            546 |             -8.92335e-05 |          -0.111793 |                             0.107954 |                          -3.14754 |                        0.5 |                   543 |                    -0.000703791 |                   -1.1603 |                                   -0.153683 |                                 -2.26712 |                          0.484346 |             565 |               -0.00112522 |            -1.36848 |                             -0.234336 |                           -1.84759 |                    0.502655 |                       658 |                        -0.000876607 |                      -0.78933 |                                       -0.253882 |                                     -2.13561 |                              0.465046 |            45.6944 |     nan |           1 |              1 |                1 |           16.4871 | strict_candidate |
