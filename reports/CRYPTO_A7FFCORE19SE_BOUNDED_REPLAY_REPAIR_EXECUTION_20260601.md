# CRYPTO A7FF-CORE19SE BOUNDED REPLAY REPAIR EXECUTION

Generated: 2026-06-01T15:04:09Z

## Decision

`HOLD_A7FFCORE19SE_REPLAY_REPAIR_INSUFFICIENT`

CORE19SE performs cost/lag/label/lane replay repair attribution using existing CORE19E replay rows. It does not execute formula generation, search, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core20": false,
  "authorizes_formula_generation": false,
  "authorizes_large_search": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "best_clean_candidate_count": 4,
  "best_clean_seed_lane_count": 2,
  "clean_2bps_candidate_count": 4,
  "clean_5bps_candidate_count": 2,
  "decision": "HOLD_A7FFCORE19SE_REPLAY_REPAIR_INSUFFICIENT",
  "executes_replay_repair": true,
  "executes_search": false,
  "generated_at": "2026-06-01T15:04:09Z",
  "next_allowed": "A7FF-CORE19SER replay repair forensic",
  "source_decision": "PASS_A7FFCORE19S_BOUNDED_REPLAY_REPAIR_CONTRACT_READY_FOR_CORE19SE",
  "source_stage": "A7FF-CORE19S",
  "stage": "A7FF-CORE19SE"
}
```

## Cost Tier Clean Summary

|   cost_bps |   clean_candidate_count |   clean_seed_lane_count |   clean_non_l5_share |
|-----------:|------------------------:|------------------------:|---------------------:|
|          2 |                       4 |                       2 |                 0.75 |
|          5 |                       2 |                       2 |                 0.5  |
|         10 |                       1 |                       1 |                 0    |
|         20 |                       1 |                       1 |                 0    |

## Diagnosis

| diagnosis                   | evidence                                                                        |   value |
|:----------------------------|:--------------------------------------------------------------------------------|--------:|
| cost_dominant_failure       | 2bps clean count improves over 5bps but remains below replay-clean breadth gate |       4 |
| lane_breadth_insufficient   | best-cost clean lane count remains below 3                                      |       2 |
| clean_clues_diagnostic_only | clean rows exist but are too few for search-readiness                           |       4 |

## 2bps Diagnostic Clean Clues

| candidate_id                                                                                                                                                            | seed_lane                  | second_pass_family     | label_family                       |   label_horizon_h |   replay_rows |   median_cost_adjusted_spread |   min_cost_adjusted_spread |   max_tstat |   min_control_ratio |   median_control_ratio |   min_one_bar_lag_spread |   clean_premay_split_count | replay_clean   |
|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------------------------|:-----------------------|:-----------------------------------|------------------:|--------------:|------------------------------:|---------------------------:|------------:|--------------------:|-----------------------:|-------------------------:|---------------------------:|:---------------|
| core16he_H3_cross_family_bridge_top_long_short_position_ratio_last_spread_short_long_SafeDiv_open_interest_value_last_zscore_168h|L3_liquidity_tier_relative_return|24  | S3_cross_family_bridge     | H3_cross_family_bridge | L3_liquidity_tier_relative_return  |                24 |            16 |                   0.000494357 |                -0.00277772 |     4.61578 |            0.705794 |               0.705794 |               0.00127761 |                          3 | True           |
| core16he_H2_I4_near_miss_repair_taker_buy_sell_volume_ratio_last_shock_24h_SafeDiv_open_interest_last_zscore_168h|L5_vol_adjusted_return|24                             | S2_taker_flow_liquidity_oi | H2_I4_near_miss_repair | L5_vol_adjusted_return             |                24 |            16 |                   0.0660384   |                 0.0311824  |     2.24352 |            0.94762  |               0.94762  |               0.0444341  |                          3 | True           |
| core16he_H3_cross_family_bridge_top_long_short_position_ratio_last_spread_short_long_SafeDiv_open_interest_value_last_zscore_168h|L0_raw_forward_return|24              | S3_cross_family_bridge     | H3_cross_family_bridge | L0_raw_forward_return              |                24 |            16 |                   0.000186352 |                -0.00301673 |     5.13683 |            0.697463 |               0.697463 |               0.00102329 |                          2 | False          |
| core16he_H3_cross_family_bridge_top_long_short_position_ratio_last_spread_short_long_SafeDiv_open_interest_value_last_zscore_168h|L1_cross_sectional_relative_return|24 | S3_cross_family_bridge     | H3_cross_family_bridge | L1_cross_sectional_relative_return |                24 |            16 |                   0.000186352 |                -0.00301673 |     5.13683 |            0.697463 |               0.697463 |               0.00102329 |                          2 | False          |
