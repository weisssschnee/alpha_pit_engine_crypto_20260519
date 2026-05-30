# CRYPTO A7FF-R9 REFERENCE / REGIME REPAIR

Generated: 2026-05-30T18:27:37Z

## Decision

`PASS_A7FFR9_REFERENCE_REGIME_REPAIR_READY_FOR_A7FF45_BOUNDED_DEEP_REPLAY_NO_SEARCH_AUTH`

A7FF-R9 does not generate formulas, run numeric probes, or run replay. It repairs the A7FF-44 bounded queue by capping the basis self-pair reference family and restoring strict regime/price candidates from the A7FF-42 strict non-L7 pool.

## Manifest

```json
{
  "authorizes_a7ff45_bounded_deep_replay": true,
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FFR9_REFERENCE_REGIME_REPAIR_READY_FOR_A7FF45_BOUNDED_DEEP_REPLAY_NO_SEARCH_AUTH",
  "executes_generation": false,
  "executes_numeric_probe": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T18:27:37Z",
  "reference_policy": "basis self-pair capped as reference-only diagnostic",
  "regime_repair_blueprints": 3,
  "regime_repair_rows": 3,
  "repaired_queue_count": 7,
  "repaired_queue_family_count": 2,
  "repaired_queue_top_family_share": 0.5714285714285714,
  "source_a7ff44_decision": "HOLD_A7FF44_DEEP_FORENSIC_CONCENTRATION_OR_BREADTH_FAIL",
  "stage": "A7FF-R9",
  "uses_may": false,
  "warnings": []
}
```

## Reference Cap Policy

| semantic_pair                         |   rows | policy                           | counts_as_replay_family   |   max_share_in_bounded_replay | reason                                                                                          |
|:--------------------------------------|-------:|:---------------------------------|:--------------------------|------------------------------:|:------------------------------------------------------------------------------------------------|
| basis_premium_like|basis_premium_like |      6 | reference_only_capped_diagnostic | False                     |                             0 | basis self-pair confirms reference response but cannot be used as a non-reference replay family |

## Regime Repair Summary

| metric                          |   value |
|:--------------------------------|--------:|
| regime_total_strict_pool_rows   |      35 |
| regime_strict_repair_rows       |       3 |
| regime_strict_repair_blueprints |       3 |

## Repaired Queue Family Summary

| semantic_pair                   |   rows |   blueprints |   motifs |   labels |   median_control_ratio |   max_control_ratio |   min_cost10 |   min_robust_floor |
|:--------------------------------|-------:|-------------:|---------:|---------:|-----------------------:|--------------------:|-------------:|-------------------:|
| funding_like|basis_premium_like |      4 |            4 |        2 |        1 |               0.442237 |            0.621534 |    0.10639   |            5.35796 |
| regime_state|price_return_like  |      3 |            3 |        2 |        1 |               0.766697 |            0.786398 |    0.0467692 |            1.5982  |

## Repaired Candidate Queue

| blueprint_id            | expression                                                                                    | semantic_pair                   | motif       | label_family           |   label_horizon_h |   control_ratio_premay_max |   cost10_recent_oriented |   one_bar_lag_recent_oriented |   robust_min_tstat_floor |   robust_median_tstat_floor | repair_source                    | r9_role                               |
|:------------------------|:----------------------------------------------------------------------------------------------|:--------------------------------|:------------|:-----------------------|------------------:|---------------------------:|-------------------------:|------------------------------:|-------------------------:|----------------------------:|:---------------------------------|:--------------------------------------|
| a7ff33_43985dd6fcd563f5 | Sub(funding_rate_state_last_ffill_8h,Delta(mark_index_basis_bps,12))                          | funding_like|basis_premium_like | sub         | L5_vol_adjusted_return |                 1 |                   0.290047 |                0.135148  |                     0.0545467 |                  6.57954 |                     6.57954 | a7ff44_bounded_queue             | carry_forward_funding_basis_candidate |
| a7ff33_eda87df62c06d036 | Sub(ZScore(funding_rate_state_last_ffill_8h),ZScore(Clip(ZScore(mark_index_basis_bps),-3,3))) | funding_like|basis_premium_like | zspread     | L5_vol_adjusted_return |                 1 |                   0.235123 |                0.121763  |                     0.0373996 |                  5.82468 |                     5.82468 | a7ff44_bounded_queue             | carry_forward_funding_basis_candidate |
| a7ff33_c4e35734432be936 | Sub(funding_rate_state_last_ffill_8h,Delta(mark_index_basis_bps,168))                         | funding_like|basis_premium_like | sub         | L5_vol_adjusted_return |                 1 |                   0.594426 |                0.108484  |                     0.0571994 |                  5.35796 |                     5.35796 | a7ff44_bounded_queue             | carry_forward_funding_basis_candidate |
| a7ff33_757d3c59e04d21f8 | Sub(funding_rate_state_last_ffill_8h,Delta(mark_index_basis_bps,72))                          | funding_like|basis_premium_like | sub         | L5_vol_adjusted_return |                 1 |                   0.621534 |                0.10639   |                     0.02988   |                  5.41414 |                     5.41414 | a7ff44_bounded_queue             | carry_forward_funding_basis_candidate |
| a7ff33_80c2b011fb504ed3 | Sub(CSRank(rolling_coverage_168h),CSRank(Delta(trade_return_1h,12)))                          | regime_state|price_return_like  | spread_rank | L5_vol_adjusted_return |                 1 |                   0.706707 |                0.0691669 |                     0.0352078 |                  1.5982  |                     1.5982  | a7ff42_strict_non_l7_regime_pool | repaired_regime_candidate             |
| a7ff33_5199304844c4d2af | Sub(rolling_coverage_168h,Delta(trade_return_1h,12))                                          | regime_state|price_return_like  | sub         | L5_vol_adjusted_return |                 1 |                   0.786398 |                0.0691669 |                     0.0352078 |                  1.5982  |                     1.5982  | a7ff42_strict_non_l7_regime_pool | repaired_regime_candidate             |
| a7ff33_ab416bf651b9dfeb | Sub(CSRank(rolling_coverage_168h),CSRank(Delta(trade_return_1h,8)))                           | regime_state|price_return_like  | spread_rank | L5_vol_adjusted_return |                 1 |                   0.766697 |                0.0467692 |                     0.0272127 |                  1.77492 |                     1.77492 | a7ff42_strict_non_l7_regime_pool | repaired_regime_candidate             |

## Regime Repair Candidates

| blueprint_id            | expression                                                                    | motif       | label_family                       |   label_horizon_h |   control_ratio_premay_max |   cost10_recent_oriented |   one_bar_lag_recent_oriented |   robust_min_tstat_floor | repair_class                   |
|:------------------------|:------------------------------------------------------------------------------|:------------|:-----------------------------------|------------------:|---------------------------:|-------------------------:|------------------------------:|-------------------------:|:-------------------------------|
| a7ff33_80c2b011fb504ed3 | Sub(CSRank(rolling_coverage_168h),CSRank(Delta(trade_return_1h,12)))          | spread_rank | L5_vol_adjusted_return             |                 1 |                   0.706707 |              0.0691669   |                   0.0352078   |                 1.5982   | strict_regime_repair_candidate |
| a7ff33_5199304844c4d2af | Sub(rolling_coverage_168h,Delta(trade_return_1h,12))                          | sub         | L5_vol_adjusted_return             |                 1 |                   0.786398 |              0.0691669   |                   0.0352078   |                 1.5982   | strict_regime_repair_candidate |
| a7ff33_ab416bf651b9dfeb | Sub(CSRank(rolling_coverage_168h),CSRank(Delta(trade_return_1h,8)))           | spread_rank | L5_vol_adjusted_return             |                 1 |                   0.766697 |              0.0467692   |                   0.0272127   |                 1.77492  | strict_regime_repair_candidate |
| a7ff33_fe3e0c6a7b32a1d7 | Sub(CSRank(rolling_coverage_168h),CSRank(Delta(trade_return_1h,1)))           | spread_rank | L1_cross_sectional_relative_return |                 4 |                   0.660976 |             -0.000806804 |                   0.00160093  |                -0.473212 | regime_hold                    |
| a7ff33_422ab8547a1abf40 | Sub(rolling_coverage_168h,Delta(trade_return_1h,1))                           | sub         | L1_cross_sectional_relative_return |                 4 |                   0.753911 |             -0.000806804 |                   0.00160093  |                -0.473212 | regime_hold                    |
| a7ff33_422ab8547a1abf40 | Sub(rolling_coverage_168h,Delta(trade_return_1h,1))                           | sub         | L0_raw_forward_return              |                 4 |                   0.660976 |             -0.000806804 |                   0.00160093  |                -0.473212 | regime_hold                    |
| a7ff33_422ab8547a1abf40 | Sub(rolling_coverage_168h,Delta(trade_return_1h,1))                           | sub         | L3_liquidity_tier_relative_return  |                 4 |                   0.74212  |             -0.000886122 |                   0.00152665  |                -0.443912 | regime_hold                    |
| a7ff33_fe3e0c6a7b32a1d7 | Sub(CSRank(rolling_coverage_168h),CSRank(Delta(trade_return_1h,1)))           | spread_rank | L3_liquidity_tier_relative_return  |                 4 |                   0.744007 |             -0.000886122 |                   0.00152665  |                -0.443912 | regime_hold                    |
| a7ff33_8f587010df0608c7 | Sub(rolling_coverage_168h,trade_return_1h)                                    | sub         | L0_raw_forward_return              |                 4 |                   0.6585   |             -0.000945927 |                   0.000323744 |                -0.776422 | regime_hold                    |
| a7ff33_8f587010df0608c7 | Sub(rolling_coverage_168h,trade_return_1h)                                    | sub         | L1_cross_sectional_relative_return |                 4 |                   0.485192 |             -0.000945927 |                   0.000323744 |                -0.776422 | regime_hold                    |
| a7ff33_e0fd95b0f8d8f369 | Sub(CSRank(rolling_coverage_168h),CSRank(trade_return_1h))                    | spread_rank | L0_raw_forward_return              |                 4 |                   0.385759 |             -0.000946544 |                   0.000324315 |                -0.776422 | regime_hold                    |
| a7ff33_eca284fc23696e2a | Sub(CSRank(rolling_coverage_168h),CSRank(Clip(ZScore(trade_return_1h),-3,3))) | spread_rank | L0_raw_forward_return              |                 4 |                   0.39246  |             -0.000946544 |                   0.000324315 |                -0.776422 | regime_hold                    |
| a7ff33_970a15df43592d87 | Sub(rolling_coverage_168h,Rank(trade_return_1h))                              | sub         | L0_raw_forward_return              |                 4 |                   0.440454 |             -0.000946544 |                   0.000324315 |                -0.776422 | regime_hold                    |
| a7ff33_a23e4aaed43083ba | Sub(rolling_coverage_168h,Clip(ZScore(trade_return_1h),-3,3))                 | sub         | L0_raw_forward_return              |                 4 |                   0.460727 |             -0.000946544 |                   0.000324315 |                -0.776422 | regime_hold                    |
| a7ff33_aa7f647e1c08045a | Sub(rolling_coverage_168h,CSRank(trade_return_1h))                            | sub         | L0_raw_forward_return              |                 4 |                   0.469446 |             -0.000946544 |                   0.000324315 |                -0.776422 | regime_hold                    |
| a7ff33_521f71d0dc53f59d | Sub(CSRank(rolling_coverage_168h),CSRank(CSRank(trade_return_1h)))            | spread_rank | L0_raw_forward_return              |                 4 |                   0.543163 |             -0.000946544 |                   0.000324315 |                -0.776422 | regime_hold                    |
| a7ff33_8b4ec72ddb682249 | Sub(CSRank(rolling_coverage_168h),CSRank(Rank(trade_return_1h)))              | spread_rank | L0_raw_forward_return              |                 4 |                   0.643429 |             -0.000946544 |                   0.000324315 |                -0.776422 | regime_hold                    |
| a7ff33_521f71d0dc53f59d | Sub(CSRank(rolling_coverage_168h),CSRank(CSRank(trade_return_1h)))            | spread_rank | L1_cross_sectional_relative_return |                 4 |                   0.426227 |             -0.000946544 |                   0.000324315 |                -0.776422 | regime_hold                    |
| a7ff33_a23e4aaed43083ba | Sub(rolling_coverage_168h,Clip(ZScore(trade_return_1h),-3,3))                 | sub         | L1_cross_sectional_relative_return |                 4 |                   0.43998  |             -0.000946544 |                   0.000324315 |                -0.776422 | regime_hold                    |
| a7ff33_8b4ec72ddb682249 | Sub(CSRank(rolling_coverage_168h),CSRank(Rank(trade_return_1h)))              | spread_rank | L1_cross_sectional_relative_return |                 4 |                   0.569095 |             -0.000946544 |                   0.000324315 |                -0.776422 | regime_hold                    |
| a7ff33_aa7f647e1c08045a | Sub(rolling_coverage_168h,CSRank(trade_return_1h))                            | sub         | L1_cross_sectional_relative_return |                 4 |                   0.735915 |             -0.000946544 |                   0.000324315 |                -0.776422 | regime_hold                    |
| a7ff33_970a15df43592d87 | Sub(rolling_coverage_168h,Rank(trade_return_1h))                              | sub         | L1_cross_sectional_relative_return |                 4 |                   0.776702 |             -0.000946544 |                   0.000324315 |                -0.776422 | regime_hold                    |
| a7ff33_8f587010df0608c7 | Sub(rolling_coverage_168h,trade_return_1h)                                    | sub         | L3_liquidity_tier_relative_return  |                 4 |                   0.606998 |             -0.00096066  |                   0.000321765 |                -0.948479 | regime_hold                    |
| a7ff33_e0fd95b0f8d8f369 | Sub(CSRank(rolling_coverage_168h),CSRank(trade_return_1h))                    | spread_rank | L3_liquidity_tier_relative_return  |                 4 |                   0.485797 |             -0.000961034 |                   0.000322723 |                -0.948479 | regime_hold                    |
| a7ff33_521f71d0dc53f59d | Sub(CSRank(rolling_coverage_168h),CSRank(CSRank(trade_return_1h)))            | spread_rank | L3_liquidity_tier_relative_return  |                 4 |                   0.485797 |             -0.000961034 |                   0.000322723 |                -0.948479 | regime_hold                    |
| a7ff33_eca284fc23696e2a | Sub(CSRank(rolling_coverage_168h),CSRank(Clip(ZScore(trade_return_1h),-3,3))) | spread_rank | L3_liquidity_tier_relative_return  |                 4 |                   0.485797 |             -0.000961034 |                   0.000322723 |                -0.948479 | regime_hold                    |
| a7ff33_aa7f647e1c08045a | Sub(rolling_coverage_168h,CSRank(trade_return_1h))                            | sub         | L3_liquidity_tier_relative_return  |                 4 |                   0.591728 |             -0.000961034 |                   0.000322723 |                -0.948479 | regime_hold                    |
| a7ff33_970a15df43592d87 | Sub(rolling_coverage_168h,Rank(trade_return_1h))                              | sub         | L3_liquidity_tier_relative_return  |                 4 |                   0.624091 |             -0.000961034 |                   0.000322723 |                -0.948479 | regime_hold                    |
| a7ff33_8b4ec72ddb682249 | Sub(CSRank(rolling_coverage_168h),CSRank(Rank(trade_return_1h)))              | spread_rank | L3_liquidity_tier_relative_return  |                 4 |                   0.676751 |             -0.000961034 |                   0.000322723 |                -0.948479 | regime_hold                    |
| a7ff33_a23e4aaed43083ba | Sub(rolling_coverage_168h,Clip(ZScore(trade_return_1h),-3,3))                 | sub         | L3_liquidity_tier_relative_return  |                 4 |                   0.738264 |             -0.000961034 |                   0.000322723 |                -0.948479 | regime_hold                    |
| a7ff33_80c2b011fb504ed3 | Sub(CSRank(rolling_coverage_168h),CSRank(Delta(trade_return_1h,12)))          | spread_rank | L3_liquidity_tier_relative_return  |                 1 |                   0.622432 |             -0.00101493  |                   0.000525884 |                 1.27662  | regime_hold                    |
| a7ff33_5199304844c4d2af | Sub(rolling_coverage_168h,Delta(trade_return_1h,12))                          | sub         | L3_liquidity_tier_relative_return  |                 1 |                   0.729176 |             -0.00101493  |                   0.000525884 |                 1.27662  | regime_hold                    |
| a7ff33_80c2b011fb504ed3 | Sub(CSRank(rolling_coverage_168h),CSRank(Delta(trade_return_1h,12)))          | spread_rank | L0_raw_forward_return              |                 1 |                   0.702025 |             -0.00104027  |                   0.000658782 |                 1.08933  | regime_hold                    |
| a7ff33_5199304844c4d2af | Sub(rolling_coverage_168h,Delta(trade_return_1h,12))                          | sub         | L0_raw_forward_return              |                 1 |                   0.762822 |             -0.00104027  |                   0.000658782 |                 1.08933  | regime_hold                    |
| a7ff33_5199304844c4d2af | Sub(rolling_coverage_168h,Delta(trade_return_1h,12))                          | sub         | L1_cross_sectional_relative_return |                 1 |                   0.697925 |             -0.00104027  |                   0.000658782 |                 1.08933  | regime_hold                    |

## Boundary

```text
numeric probe executed: false
replay executed: false
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```
