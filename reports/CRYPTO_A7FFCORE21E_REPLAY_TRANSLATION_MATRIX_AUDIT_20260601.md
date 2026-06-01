# CRYPTO A7FF-CORE21E REPLAY TRANSLATION MATRIX AUDIT

Generated: 2026-06-01T15:16:45Z

## Decision

`HOLD_A7FFCORE21E_TRANSLATION_MATRIX_INSUFFICIENT`

CORE21E audits label/cost/lag/lane translation using existing CORE19E replay rows. It does not execute formula generation, search, large search, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core22_contract": false,
  "authorizes_formula_generation": false,
  "authorizes_large_search": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "best_label_cost_clean_candidate_count": 1,
  "best_lane_cost_clean_candidate_count": 3,
  "blockers": [
    "best_label_cost_clean_lt_6",
    "current_replay_clean_lanes_lt_3"
  ],
  "current_replay_clean_lanes": 2,
  "decision": "HOLD_A7FFCORE21E_TRANSLATION_MATRIX_INSUFFICIENT",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T15:16:45Z",
  "l5_clean_2bps": 1,
  "next_allowed": "A7FF-CORE21R translation matrix forensic",
  "non_l5_clean_2bps": 3,
  "source_decision": "PASS_A7FFCORE21_REPLAY_TRANSLATION_RESET_CONTRACT_READY_FOR_CORE21E",
  "source_stage": "A7FF-CORE21",
  "stage": "A7FF-CORE21E"
}
```

## Diagnosis

| finding               |   value | interpretation                                     |
|:----------------------|--------:|:---------------------------------------------------|
| best_label_cost_clean |       1 | max clean candidates by label/cost bucket          |
| best_lane_cost_clean  |       3 | max clean candidates by lane/cost bucket           |
| non_l5_clean_2bps     |       3 | non-L5 translation at lowest cost tier             |
| l5_clean_2bps         |       1 | L5 diagnostic-only translation at lowest cost tier |
| current_clean_lanes   |       2 | lane breadth under original CORE19E clean rule     |

## Best Label/Cost Buckets

| label_family                       |   cost_bps |   candidate_count |   median_cost_adjusted_spread |   median_control_ratio |   median_lag_spread |   clean_candidate_count |
|:-----------------------------------|-----------:|------------------:|------------------------------:|-----------------------:|--------------------:|------------------------:|
| L0_raw_forward_return              |          2 |                31 |                   0.000227911 |               0.697463 |         0.000192655 |                       1 |
| L1_cross_sectional_relative_return |          2 |                31 |                   0.000227911 |               0.697463 |         0.000192655 |                       1 |
| L3_liquidity_tier_relative_return  |          2 |                24 |                   0.000317619 |               0.706598 |         0.000173929 |                       1 |
| L3_liquidity_tier_relative_return  |          5 |                24 |                  -0.000282381 |               0.706598 |         0.000173929 |                       1 |
| L5_vol_adjusted_return             |          2 |                10 |                   0.0402234   |               0.698473 |         0.000213154 |                       1 |
| L5_vol_adjusted_return             |          5 |                10 |                   0.0396234   |               0.698473 |         0.000213154 |                       1 |
| L5_vol_adjusted_return             |         10 |                10 |                   0.0386234   |               0.698473 |         0.000213154 |                       1 |
| L5_vol_adjusted_return             |         20 |                10 |                   0.0366234   |               0.698473 |         0.000213154 |                       1 |
| L0_raw_forward_return              |          5 |                31 |                  -0.000372089 |               0.697463 |         0.000192655 |                       0 |
| L0_raw_forward_return              |         10 |                31 |                  -0.00137209  |               0.697463 |         0.000192655 |                       0 |

## Best Lane/Cost Buckets

| seed_lane                      |   cost_bps |   candidate_count |   median_cost_adjusted_spread |   median_control_ratio |   median_lag_spread |   clean_candidate_count |
|:-------------------------------|-----------:|------------------:|------------------------------:|-----------------------:|--------------------:|------------------------:|
| S3_cross_family_bridge         |          2 |                20 |                   0.00106399  |               0.718261 |         0.00077341  |                       3 |
| S3_cross_family_bridge         |          5 |                20 |                   0.000463994 |               0.718261 |         0.00077341  |                       1 |
| S2_taker_flow_liquidity_oi     |          2 |                12 |                   1.37956e-05 |               1.72135  |         2.97622e-06 |                       1 |
| S2_taker_flow_liquidity_oi     |          5 |                12 |                  -0.000586204 |               1.72135  |         2.97622e-06 |                       1 |
| S2_taker_flow_liquidity_oi     |         10 |                12 |                  -0.0015862   |               1.72135  |         2.97622e-06 |                       1 |
| S2_taker_flow_liquidity_oi     |         20 |                12 |                  -0.0035862   |               1.72135  |         2.97622e-06 |                       1 |
| S1_liquidity_basis_positioning |          2 |                33 |                   0.000436059 |               0.718864 |         0.000228789 |                       0 |
| S1_liquidity_basis_positioning |          5 |                33 |                  -0.000163941 |               0.718864 |         0.000228789 |                       0 |
| S1_liquidity_basis_positioning |         10 |                33 |                  -0.00116394  |               0.718864 |         0.000228789 |                       0 |
| S1_liquidity_basis_positioning |         20 |                33 |                  -0.00316394  |               0.718864 |         0.000228789 |                       0 |

## Lag Gate Matrix

| label_family                       |   cost_bps |   clean_candidate_count |   clean_without_lag_gate |   lag_gate_loss |
|:-----------------------------------|-----------:|------------------------:|-------------------------:|----------------:|
| L0_raw_forward_return              |          2 |                       1 |                       17 |              16 |
| L1_cross_sectional_relative_return |          2 |                       1 |                       17 |              16 |
| L3_liquidity_tier_relative_return  |          2 |                       1 |                       13 |              12 |
| L5_vol_adjusted_return             |          2 |                       1 |                        8 |               7 |
| L5_vol_adjusted_return             |          5 |                       1 |                        8 |               7 |
| L5_vol_adjusted_return             |         10 |                       1 |                        8 |               7 |
| L5_vol_adjusted_return             |         20 |                       1 |                        8 |               7 |
| L3_liquidity_tier_relative_return  |          5 |                       1 |                        1 |               0 |
| L0_raw_forward_return              |          5 |                       0 |                      nan |               0 |
| L0_raw_forward_return              |         10 |                       0 |                      nan |               0 |
| L0_raw_forward_return              |         20 |                       0 |                      nan |               0 |
| L1_cross_sectional_relative_return |          5 |                       0 |                      nan |               0 |
| L1_cross_sectional_relative_return |         10 |                       0 |                      nan |               0 |
| L1_cross_sectional_relative_return |         20 |                       0 |                      nan |               0 |
| L3_liquidity_tier_relative_return  |         10 |                       0 |                      nan |               0 |
| L3_liquidity_tier_relative_return  |         20 |                       0 |                      nan |               0 |
