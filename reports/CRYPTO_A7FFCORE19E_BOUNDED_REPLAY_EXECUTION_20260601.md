# CRYPTO A7FF-CORE19E BOUNDED REPLAY EXECUTION

Generated: 2026-06-01T14:57:52Z

## Decision

`HOLD_A7FFCORE19E_BOUNDED_REPLAY_INSUFFICIENT`

CORE19E executes bounded replay over the locked 96-row packet. It does not execute formula generation, search expansion, large search, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core20_contract": false,
  "authorizes_formula_generation": false,
  "authorizes_large_search": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "replay_clean_candidate_count_lt_12",
    "replay_clean_seed_lane_count_lt_3"
  ],
  "candidate_count": 96,
  "clean_rule": "validation/test/recent all positive at 5bps, control_ratio < 1.0, one_bar_lag positive",
  "decision": "HOLD_A7FFCORE19E_BOUNDED_REPLAY_INSUFFICIENT",
  "eval_error_count": 0,
  "executes_replay": true,
  "executes_search": false,
  "full_timestamps_before_subset": 21025,
  "generated_at": "2026-06-01T14:57:52Z",
  "next_allowed": "A7FF-CORE19R bounded replay forensic",
  "replay_clean_candidate_count": 2,
  "replay_clean_non_l5_share": 0.5,
  "replay_clean_seed_lane_count": 2,
  "replay_rows": 1536,
  "source_decision": "PASS_A7FFCORE19_BOUNDED_REPLAY_CONTRACT_READY_FOR_CORE19E",
  "source_stage": "A7FF-CORE19",
  "stage": "A7FF-CORE19E",
  "symbols_loaded": 96,
  "timestamps": 3481
}
```

## Family Summary

| seed_lane                      | second_pass_family     |   candidate_count |   replay_clean_candidate_count |   label_family_count |   median_control_ratio |
|:-------------------------------|:-----------------------|------------------:|-------------------------------:|---------------------:|-----------------------:|
| S3_cross_family_bridge         | H3_cross_family_bridge |                20 |                              1 |                    4 |               0.718261 |
| S2_taker_flow_liquidity_oi     | H2_I4_near_miss_repair |                12 |                              1 |                    4 |               1.72135  |
| S1_liquidity_basis_positioning | H1_I5_deconcentration  |                33 |                              0 |                    3 |               0.718864 |
| S0_positioning_price_basis     | H0_I3_deconcentration  |                31 |                              0 |                    3 |               0.557232 |

## Replay Clean Candidates

| candidate_id                                                                                                                                                           | seed_lane                  | second_pass_family     | label_family                      |   label_horizon_h |   replay_rows |   median_cost_adjusted_spread |   min_cost_adjusted_spread |   max_tstat |   min_control_ratio |   median_control_ratio |   min_one_bar_lag_spread |   clean_premay_split_count | replay_clean   |
|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------------------------|:-----------------------|:----------------------------------|------------------:|--------------:|------------------------------:|---------------------------:|------------:|--------------------:|-----------------------:|-------------------------:|---------------------------:|:---------------|
| core16he_H3_cross_family_bridge_top_long_short_position_ratio_last_spread_short_long_SafeDiv_open_interest_value_last_zscore_168h|L3_liquidity_tier_relative_return|24 | S3_cross_family_bridge     | H3_cross_family_bridge | L3_liquidity_tier_relative_return |                24 |            16 |                   0.000494357 |                -0.00277772 |     4.61578 |            0.705794 |               0.705794 |               0.00127761 |                          3 | True           |
| core16he_H2_I4_near_miss_repair_taker_buy_sell_volume_ratio_last_shock_24h_SafeDiv_open_interest_last_zscore_168h|L5_vol_adjusted_return|24                            | S2_taker_flow_liquidity_oi | H2_I4_near_miss_repair | L5_vol_adjusted_return            |                24 |            16 |                   0.0660384   |                 0.0311824  |     2.24352 |            0.94762  |               0.94762  |               0.0444341  |                          3 | True           |
