# CRYPTO A7FF-CORE16KE H2 STRICT-FLOOR EXECUTION

Generated: 2026-06-01T13:56:44Z

## Decision

`HOLD_A7FFCORE16KE_H2_STRICT_FLOOR_REPAIR_INSUFFICIENT`

CORE16KE executes a narrow H2/I4 strict-floor repair around the excluded near-miss field pair only. It does not execute open grammar formula generation, replay, search, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "added_strict_h2_count": 2,
  "authorizes_alpha_proof": false,
  "authorizes_core16l": false,
  "authorizes_core17": false,
  "authorizes_formula_generation": false,
  "authorizes_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blueprint_count": 75,
  "chunk_count_completed": 5,
  "decision": "HOLD_A7FFCORE16KE_H2_STRICT_FLOOR_REPAIR_INSUFFICIENT",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T13:56:44Z",
  "h2_repair_candidate_count": 2,
  "next_allowed": "A7FF-CORE16KR H2 repair forensic",
  "repaired_queue_h2_count": 11,
  "repaired_queue_size": 95,
  "response_rows": 1200,
  "source_decision": "PASS_A7FFCORE16K_H2_STRICT_FLOOR_REPAIR_CONTRACT_READY_FOR_CORE16KE",
  "source_stage": "A7FF-CORE16K",
  "stage": "A7FF-CORE16KE"
}
```

## Decision Counts

| decision                                     |   count |
|:---------------------------------------------|--------:|
| HOLD_A7FFCORE16KE_PREMAY_UNSTABLE            |    1010 |
| HOLD_A7FFCORE16KE_CONTROL_LIKE               |     181 |
| A7FFCORE16KE_NEAR_MISS_CONTROL_MARGIN        |       7 |
| A7FFCORE16KE_H2_REPAIR_CANDIDATE_LAG_FRAGILE |       2 |

## Added Strict H2 Rows

| second_pass_family     | left_field                  | left_transform   | operator   | right_field              | right_transform   | blueprint_id                                                                               | label_family                       |   label_horizon_h |   orientation_from_train |   premay_positive_split_count | premay_all_positive   |   control_ratio_premay_max |   one_bar_lag_recent_oriented | lag_ok   | h2_repair_candidate   | near_miss   | decision                                     |   train_2024_n |   train_2024_mean_spread |   train_2024_tstat |   train_2024_nonoverlap_median_tstat |   train_2024_nonoverlap_min_tstat |   train_2024_positive_rate |   validation_2025H1_n |   validation_2025H1_mean_spread |   validation_2025H1_tstat |   validation_2025H1_nonoverlap_median_tstat |   validation_2025H1_nonoverlap_min_tstat |   validation_2025H1_positive_rate |   test_2025H2_n |   test_2025H2_mean_spread |   test_2025H2_tstat |   test_2025H2_nonoverlap_median_tstat |   test_2025H2_nonoverlap_min_tstat |   test_2025H2_positive_rate |   recent_oos_2026JanApr_n |   recent_oos_2026JanApr_mean_spread |   recent_oos_2026JanApr_tstat |   recent_oos_2026JanApr_nonoverlap_median_tstat |   recent_oos_2026JanApr_nonoverlap_min_tstat |   recent_oos_2026JanApr_positive_rate |   avg_n_obs_recent |   error |   lag_bonus |   non_l5_bonus |   selection_score | queue_role       |
|:-----------------------|:----------------------------|:-----------------|:-----------|:-------------------------|:------------------|:-------------------------------------------------------------------------------------------|:-----------------------------------|------------------:|-------------------------:|------------------------------:|:----------------------|---------------------------:|------------------------------:|:---------|:----------------------|:------------|:---------------------------------------------|---------------:|-------------------------:|-------------------:|-------------------------------------:|----------------------------------:|---------------------------:|----------------------:|--------------------------------:|--------------------------:|--------------------------------------------:|-----------------------------------------:|----------------------------------:|----------------:|--------------------------:|--------------------:|--------------------------------------:|-----------------------------------:|----------------------------:|--------------------------:|------------------------------------:|------------------------------:|------------------------------------------------:|---------------------------------------------:|--------------------------------------:|-------------------:|--------:|------------:|---------------:|------------------:|:-----------------|
| H2_I4_near_miss_repair | kline_taker_buy_quote_share | delta_2h         | SafeDiv    | median_quote_volume_168h | delta_2h          | core16ke_H2_kline_taker_buy_quote_share_delta_2h_SafeDiv_median_quote_volume_168h_delta_2h | L0_raw_forward_return              |                 4 |                       -1 |                             3 | True                  |                    0.95275 |                    3.1851e-05 | False    | True                  | False       | A7FFCORE16KE_H2_REPAIR_CANDIDATE_LAG_FRAGILE |            671 |             -0.000230907 |          -0.793152 |                            -0.555865 |                         -0.792865 |                   0.457526 |                   668 |                    -0.000123174 |                 -0.460113 |                                   -0.242664 |                                 -1.08426 |                          0.495509 |             667 |              -0.000362074 |            -1.84648 |                             -0.837892 |                           -1.62378 |                    0.472264 |                       711 |                         -0.00076301 |                      -2.09354 |                                        -1.04339 |                                     -1.34922 |                              0.455696 |            62.5139 |     nan |           0 |              1 |           4.04725 | strict_candidate |
| H2_I4_near_miss_repair | kline_taker_buy_quote_share | delta_2h         | SafeDiv    | median_quote_volume_168h | delta_2h          | core16ke_H2_kline_taker_buy_quote_share_delta_2h_SafeDiv_median_quote_volume_168h_delta_2h | L1_cross_sectional_relative_return |                 4 |                       -1 |                             3 | True                  |                    0.95275 |                    3.1851e-05 | False    | True                  | False       | A7FFCORE16KE_H2_REPAIR_CANDIDATE_LAG_FRAGILE |            671 |             -0.000230907 |          -0.793152 |                            -0.555865 |                         -0.792865 |                   0.457526 |                   668 |                    -0.000123174 |                 -0.460113 |                                   -0.242664 |                                 -1.08426 |                          0.495509 |             667 |              -0.000362074 |            -1.84648 |                             -0.837892 |                           -1.62378 |                    0.472264 |                       711 |                         -0.00076301 |                      -2.09354 |                                        -1.04339 |                                     -1.34922 |                              0.455696 |            62.5139 |     nan |           0 |              1 |           4.04725 | strict_candidate |
