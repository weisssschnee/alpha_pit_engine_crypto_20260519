# CRYPTO A7FF-CORE23E EXECUTABLE-HORIZON DIAGNOSTIC AUDIT

Generated: 2026-06-01T15:34:18Z

## Decision

`HOLD_A7FFCORE23E_EXECUTABLE_HORIZON_SUPPLY_INSUFFICIENT`

CORE23E audits whether the locked packet translates into lower-turnover executable evidence. It reuses existing CORE19E replay rows and does not execute formula generation, search, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core24_contract": false,
  "authorizes_formula_generation": false,
  "authorizes_large_search": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "best_cost_bps": 2,
  "best_executable_h4_plus_clean_candidate_count": 4,
  "best_executable_h4_plus_clean_lane_count": 2,
  "best_executable_h4_plus_label_family_count": 4,
  "best_executable_h4_plus_non_l5_count": 3,
  "blockers": [
    "executable_h4_plus_clean_count_lt_6",
    "executable_h4_plus_clean_lane_count_lt_3"
  ],
  "decision": "HOLD_A7FFCORE23E_EXECUTABLE_HORIZON_SUPPLY_INSUFFICIENT",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T15:34:18Z",
  "next_allowed": "A7FF-CORE23R executable-horizon forensic",
  "source_decision": "PASS_A7FFCORE23_EXECUTABLE_HORIZON_REDESIGN_CONTRACT_READY_FOR_CORE23E",
  "source_stage": "A7FF-CORE23",
  "stage": "A7FF-CORE23E"
}
```

## Diagnosis

| finding                                       |   value | interpretation                                              |
|:----------------------------------------------|--------:|:------------------------------------------------------------|
| best_executable_h4_plus_clean_candidate_count |       4 | primary lower-turnover executable clean supply              |
| best_executable_h4_plus_clean_lane_count      |       2 | lane breadth after one-bar executable cost gate             |
| best_executable_h4_plus_label_family_count    |       4 | label breadth after one-bar executable cost gate            |
| best_executable_h4_plus_non_l5_count          |       3 | non-L5 executable translation supply                        |
| best_cost_bps                                 |       2 | best cost tier remains diagnostic unless breadth gates pass |

## Executable Horizon Matrix

| policy                      |   cost_bps |   min_horizon_h |   clean_candidate_count |   clean_lane_count |   clean_label_family_count |   non_l5_candidate_count |   non_l5_share | horizon_buckets                        |
|:----------------------------|-----------:|----------------:|------------------------:|-------------------:|---------------------------:|-------------------------:|---------------:|:---------------------------------------|
| one_bar_any_horizon         |          2 |               1 |                       4 |                  2 |                          4 |                        3 |       0.75     | H24_low_turnover                       |
| one_bar_executable_h4_plus  |          2 |               4 |                       4 |                  2 |                          4 |                        3 |       0.75     | H24_low_turnover                       |
| one_bar_low_turnover_h24    |          2 |              24 |                       4 |                  2 |                          4 |                        3 |       0.75     | H24_low_turnover                       |
| same_bar_diagnostic_h4_plus |          2 |               4 |                       7 |                  3 |                          4 |                        5 |       0.714286 | H24_low_turnover,H4_H8_medium_turnover |
| one_bar_any_horizon         |          5 |               1 |                       4 |                  2 |                          4 |                        3 |       0.75     | H24_low_turnover                       |
| one_bar_executable_h4_plus  |          5 |               4 |                       4 |                  2 |                          4 |                        3 |       0.75     | H24_low_turnover                       |
| one_bar_low_turnover_h24    |          5 |              24 |                       4 |                  2 |                          4 |                        3 |       0.75     | H24_low_turnover                       |
| same_bar_diagnostic_h4_plus |          5 |               4 |                       3 |                  2 |                          2 |                        1 |       0.333333 | H24_low_turnover,H4_H8_medium_turnover |
| one_bar_any_horizon         |         10 |               1 |                       1 |                  1 |                          1 |                        0 |       0        | H24_low_turnover                       |
| one_bar_executable_h4_plus  |         10 |               4 |                       1 |                  1 |                          1 |                        0 |       0        | H24_low_turnover                       |
| one_bar_low_turnover_h24    |         10 |              24 |                       1 |                  1 |                          1 |                        0 |       0        | H24_low_turnover                       |
| same_bar_diagnostic_h4_plus |         10 |               4 |                       2 |                  2 |                          1 |                        0 |       0        | H24_low_turnover,H4_H8_medium_turnover |
| one_bar_any_horizon         |         20 |               1 |                       1 |                  1 |                          1 |                        0 |       0        | H24_low_turnover                       |
| one_bar_executable_h4_plus  |         20 |               4 |                       1 |                  1 |                          1 |                        0 |       0        | H24_low_turnover                       |
| one_bar_low_turnover_h24    |         20 |              24 |                       1 |                  1 |                          1 |                        0 |       0        | H24_low_turnover                       |
| same_bar_diagnostic_h4_plus |         20 |               4 |                       2 |                  2 |                          1 |                        0 |       0        | H24_low_turnover,H4_H8_medium_turnover |

## Best Executable Clean Candidates

| candidate_id                                                                                                                                                            | seed_lane                  | second_pass_family     | label_family                       |   label_horizon_h | left_field                         | left_transform    | operator   | right_field              | right_transform   |   control_ratio_premay_max |
|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------------------------|:-----------------------|:-----------------------------------|------------------:|:-----------------------------------|:------------------|:-----------|:-------------------------|:------------------|---------------------------:|
| core16he_H2_I4_near_miss_repair_taker_buy_sell_volume_ratio_last_shock_24h_SafeDiv_open_interest_last_zscore_168h|L5_vol_adjusted_return|24                             | S2_taker_flow_liquidity_oi | H2_I4_near_miss_repair | L5_vol_adjusted_return             |                24 | taker_buy_sell_volume_ratio_last   | shock_24h         | SafeDiv    | open_interest_last       | zscore_168h       |                   0.94762  |
| core16he_H3_cross_family_bridge_top_long_short_position_ratio_last_spread_short_long_SafeDiv_open_interest_value_last_zscore_168h|L0_raw_forward_return|24              | S3_cross_family_bridge     | H3_cross_family_bridge | L0_raw_forward_return              |                24 | top_long_short_position_ratio_last | spread_short_long | SafeDiv    | open_interest_value_last | zscore_168h       |                   0.697463 |
| core16he_H3_cross_family_bridge_top_long_short_position_ratio_last_spread_short_long_SafeDiv_open_interest_value_last_zscore_168h|L1_cross_sectional_relative_return|24 | S3_cross_family_bridge     | H3_cross_family_bridge | L1_cross_sectional_relative_return |                24 | top_long_short_position_ratio_last | spread_short_long | SafeDiv    | open_interest_value_last | zscore_168h       |                   0.697463 |
| core16he_H3_cross_family_bridge_top_long_short_position_ratio_last_spread_short_long_SafeDiv_open_interest_value_last_zscore_168h|L3_liquidity_tier_relative_return|24  | S3_cross_family_bridge     | H3_cross_family_bridge | L3_liquidity_tier_relative_return  |                24 | top_long_short_position_ratio_last | spread_short_long | SafeDiv    | open_interest_value_last | zscore_168h       |                   0.705794 |

## Clean By Lane

| seed_lane                  |   clean_candidate_count |   label_family_count |
|:---------------------------|------------------------:|---------------------:|
| S2_taker_flow_liquidity_oi |                       1 |                    1 |
| S3_cross_family_bridge     |                       3 |                    3 |

## Clean By Label

| label_family                       |   clean_candidate_count |   lane_count |
|:-----------------------------------|------------------------:|-------------:|
| L0_raw_forward_return              |                       1 |            1 |
| L1_cross_sectional_relative_return |                       1 |            1 |
| L3_liquidity_tier_relative_return  |                       1 |            1 |
| L5_vol_adjusted_return             |                       1 |            1 |
