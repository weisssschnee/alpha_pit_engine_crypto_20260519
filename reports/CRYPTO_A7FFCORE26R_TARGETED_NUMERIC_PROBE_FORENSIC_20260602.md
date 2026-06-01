# CRYPTO A7FF-CORE26R TARGETED NUMERIC PROBE FORENSIC

Generated: 2026-06-01T17:44:55Z

## Decision

`PASS_A7FFCORE26R_TARGETED_NUMERIC_FORENSIC_COMPLETE_READY_FOR_CORE26C`

CORE26R freezes the targeted numeric probe hold. It does not authorize replay, search, large search, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core26c_contract": true,
  "authorizes_formula_generation": false,
  "authorizes_large_search": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "no_three_split_executable_candidates",
    "near_miss_lane_count_lt_3"
  ],
  "decision": "PASS_A7FFCORE26R_TARGETED_NUMERIC_FORENSIC_COMPLETE_READY_FOR_CORE26C",
  "dominant_failure": "split_consistency_failure_after_targeted_generation",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T17:44:55Z",
  "near_miss_lane_count": 2,
  "next_allowed": "A7FF-CORE26C coverage-aware numeric probe repair contract",
  "source_decision": "HOLD_A7FFCORE26E_TARGETED_NUMERIC_PROBE_INSUFFICIENT",
  "source_stage": "A7FF-CORE26E",
  "stage": "A7FF-CORE26R",
  "three_split_clean_count": 0,
  "two_split_near_miss_count": 7,
  "zero_sample_candidate_count": 0
}
```

## Diagnosis

| finding                       | value                                               | interpretation                                  |
|:------------------------------|:----------------------------------------------------|:------------------------------------------------|
| three_split_clean_count       | 0                                                   | strict executable clean supply                  |
| two_split_near_miss_count     | 7                                                   | near-miss supply if one split fails             |
| lane_with_two_split_near_miss | 2                                                   | near-miss lane breadth                          |
| zero_sample_candidate_count   | 0                                                   | coverage/materialization holes in sampled probe |
| dominant_failure              | split_consistency_failure_after_targeted_generation | why CORE26E cannot advance                      |

## Lane Forensic

| seed_lane                      |   candidates |   pass_3_split |   pass_2_split |   pass_spread_3_split |   median_control |   median_spread |
|:-------------------------------|-------------:|---------------:|---------------:|----------------------:|-----------------:|----------------:|
| S0_positioning_price_basis     |          160 |              0 |              3 |                    14 |          4.69565 |    -0.000443243 |
| S1_liquidity_basis_positioning |          160 |              0 |              0 |                     5 |          4.19148 |    -0.00142368  |
| S2_taker_flow_liquidity_oi     |           80 |              0 |              0 |                     0 |         10.3456  |    -0.000557736 |
| S3_cross_family_bridge         |           80 |              0 |              4 |                     6 |          7.77357 |     0.000206658 |

## Label Forensic

| label_family                       |   candidates |   pass_3_split |   pass_2_split |   median_control |   median_spread |
|:-----------------------------------|-------------:|---------------:|---------------:|-----------------:|----------------:|
| L0_raw_forward_return              |          220 |              0 |              2 |          4.88491 |    -0.000844661 |
| L1_cross_sectional_relative_return |          130 |              0 |              2 |          5.66822 |    -0.000552588 |
| L3_liquidity_tier_relative_return  |          115 |              0 |              3 |          5.29331 |    -0.000494724 |
| L5_vol_adjusted_return             |           15 |              0 |              0 |         14.2698  |    -0.0390049   |

## Top Near Miss Candidates

| candidate_id                                      | seed_lane                  | label_family                       |   label_horizon_h |   pass_both_splits |   pass_spread_splits |   pass_control_splits |   min_spread |   mean_spread |   max_control_ratio |   min_sample_rows |
|:--------------------------------------------------|:---------------------------|:-----------------------------------|------------------:|-------------------:|---------------------:|----------------------:|-------------:|--------------:|--------------------:|------------------:|
| core25e_S0_positioning_price_basis_0922438f201b00 | S0_positioning_price_basis | L3_liquidity_tier_relative_return  |                24 |                  2 |                    2 |                     2 | -0.000777221 |   0.00205674  |             5.21163 |             47000 |
| core25e_S0_positioning_price_basis_fd2adbe6c63150 | S0_positioning_price_basis | L1_cross_sectional_relative_return |                24 |                  2 |                    2 |                     2 | -0.000373975 |   0.00108097  |           109.073   |             46926 |
| core25e_S3_cross_family_bridge_4c3e1a6b33e744     | S3_cross_family_bridge     | L3_liquidity_tier_relative_return  |                24 |                  2 |                    2 |                     2 | -0.00170522  |   0.000820464 |             1.34429 |             46993 |
| core25e_S3_cross_family_bridge_a0cc466d3bf517     | S3_cross_family_bridge     | L0_raw_forward_return              |                 8 |                  2 |                    2 |                     2 | -0.000237459 |   0.000639912 |            15.2135  |             46995 |
| core25e_S3_cross_family_bridge_f01ddde3e97efa     | S3_cross_family_bridge     | L0_raw_forward_return              |                 8 |                  2 |                    2 |                     2 | -0.000237459 |   0.000639912 |            15.2135  |             46995 |
| core25e_S3_cross_family_bridge_91ab2fc8d2ef2d     | S3_cross_family_bridge     | L1_cross_sectional_relative_return |                24 |                  2 |                    2 |                     2 | -0.00175909  |   0.00062929  |             1.42512 |             46993 |
| core25e_S0_positioning_price_basis_287dccc7c00486 | S0_positioning_price_basis | L3_liquidity_tier_relative_return  |                24 |                  2 |                    2 |                     2 | -0.00126709  |   0.00044833  |             2.02286 |             47064 |

## Recommended Actions

| next_stage                  | action                                       | rationale                                                                                                               | authorized   |
|:----------------------------|:---------------------------------------------|:------------------------------------------------------------------------------------------------------------------------|:-------------|
| A7FF-CORE26C                | coverage-aware numeric probe repair contract | CORE26E produced eval-success but zero strict clean; repair must separate coverage holes from genuine split instability | True         |
| A7FF-CORE27 replay contract | blocked                                      | no three-split executable candidates                                                                                    | False        |
