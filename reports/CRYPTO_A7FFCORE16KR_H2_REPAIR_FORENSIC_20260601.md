# CRYPTO A7FF-CORE16KR H2 REPAIR FORENSIC

Generated: 2026-06-01T13:59:24Z

## Decision

`PASS_A7FFCORE16KR_H2_REPAIR_FORENSIC_COMPLETE_READY_FOR_CORE16M`

CORE16KR freezes the CORE16KE result. It does not execute replay, search, promotion, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "added_strict_h2_count": 2,
  "authorizes_alpha_proof": false,
  "authorizes_core16l": false,
  "authorizes_core16m": true,
  "authorizes_core17": false,
  "authorizes_formula_generation": false,
  "authorizes_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE16KR_H2_REPAIR_FORENSIC_COMPLETE_READY_FOR_CORE16M",
  "dominant_failure": "strict_h2_floor_short_by_one_after_repair",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T13:59:24Z",
  "h2_repair_candidate_count": 2,
  "h2_rows_needed": 1,
  "next_allowed": "A7FF-CORE16M H2 floor arbitration contract",
  "queue_rows_needed": 1,
  "repaired_queue_h2_count": 11,
  "repaired_queue_size": 95,
  "response_rows": 1200,
  "source_decision": "HOLD_A7FFCORE16KE_H2_STRICT_FLOOR_REPAIR_INSUFFICIENT",
  "source_stage": "A7FF-CORE16KE",
  "stage": "A7FF-CORE16KR"
}
```

## CORE16KE Decision Counts

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

## Candidate Transform Summary

| left_transform   | operator   | right_transform   |   candidate_rows |   label_family_count |   min_control_ratio |   lag_ok_count |
|:-----------------|:-----------|:------------------|-----------------:|---------------------:|--------------------:|---------------:|
| delta_2h         | SafeDiv    | delta_2h          |                2 |                    2 |             0.95275 |              0 |

## Recommended Actions

| action_id                            | action                                                                                          | reason                                                                            |
|:-------------------------------------|:------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------|
| A0_no_core16l                        | do not lock the strict pre-seed queue                                                           | CORE16KE repaired queue is still below size and H2 floors                         |
| A1_core16m_floor_arbitration         | write a floor arbitration contract before any further execution                                 | the gap is one row, but weakening the floor silently would corrupt governance     |
| A2_core16me_optional_broader_h2_wave | if strict floor is retained, run a broader H2 wave with additional transforms and checkpointing | current narrow wave found 2 of 3 required rows and the remaining gap is localized |
