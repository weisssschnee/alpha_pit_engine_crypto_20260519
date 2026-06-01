# CRYPTO A7FF-CORE26CE SPLIT-CONSISTENCY REPAIR PROBE

Generated: 2026-06-01T18:01:18Z

## Decision

`HOLD_A7FFCORE26CE_SPLIT_REPAIR_INSUFFICIENT`

CORE26CE executes a bounded S0/S3 split-consistency repair numeric probe. It does not authorize search, large search, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core27_contract": false,
  "authorizes_formula_generation": false,
  "authorizes_large_search": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "three_split_clean_count_lt_6",
    "three_split_clean_lane_count_lt_3"
  ],
  "decision": "HOLD_A7FFCORE26CE_SPLIT_REPAIR_INSUFFICIENT",
  "eval_error_count": 0,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T18:01:18Z",
  "next_allowed": "A7FF-CORE26CER split repair forensic",
  "numeric_rows": 2880,
  "repair_pool_count": 360,
  "source_decision": "PASS_A7FFCORE26C_SPLIT_CONSISTENCY_REPAIR_CONTRACT_READY_FOR_CORE26CE",
  "source_stage": "A7FF-CORE26C",
  "stage": "A7FF-CORE26CE",
  "three_split_clean_count": 4,
  "three_split_clean_lane_count": 1,
  "two_split_near_miss_count": 20
}
```

## Lane Summary

| seed_lane                  |   candidates |   clean_3_split |   near_2_split |   median_control |   median_spread |
|:---------------------------|-------------:|----------------:|---------------:|-----------------:|----------------:|
| S0_positioning_price_basis |          180 |               4 |             20 |          3.03872 |    -0.000165727 |
| S3_cross_family_bridge     |          180 |               0 |              4 |          5.44    |    -0.000422158 |

## Clean Candidates

| blueprint_id                                       | seed_lane                  | label_family                       |   label_horizon_h | left_field                         | left_transform   | operator   | right_field       | right_transform   | expression                                                                   | candidate_role                 |
|:---------------------------------------------------|:---------------------------|:-----------------------------------|------------------:|:-----------------------------------|:-----------------|:-----------|:------------------|:------------------|:-----------------------------------------------------------------------------|:-------------------------------|
| core26ce_S0_positioning_price_basis_fd2adbe6c63150 | S0_positioning_price_basis | L1_cross_sectional_relative_return |                24 | top_long_short_position_ratio_last | delta_4h         | Sub        | trade_return_24h  | decay_24h         | Sub(Delta(top_long_short_position_ratio_last,4),Decay(trade_return_24h,24))  | split_consistency_repair_probe |
| core26ce_S0_positioning_price_basis_b2aaec2e9d5c81 | S0_positioning_price_basis | L3_liquidity_tier_relative_return  |                24 | top_long_short_position_ratio_last | delta_4h         | Sub        | trade_return_24h  | decay_24h         | Sub(Delta(top_long_short_position_ratio_last,4),Decay(trade_return_24h,24))  | split_consistency_repair_probe |
| core26ce_S0_positioning_price_basis_fd9e9666407b90 | S0_positioning_price_basis | L3_liquidity_tier_relative_return  |                 8 | top_long_short_position_ratio_last | delta_4h         | Sub        | premium_close_bps | decay_24h         | Sub(Delta(top_long_short_position_ratio_last,4),Decay(premium_close_bps,24)) | split_consistency_repair_probe |
| core26ce_S0_positioning_price_basis_136ffaf2705ce8 | S0_positioning_price_basis | L1_cross_sectional_relative_return |                 8 | top_long_short_position_ratio_last | delta_4h         | Sub        | premium_close_bps | zscore_168h       | Sub(Delta(top_long_short_position_ratio_last,4),ZScore(premium_close_bps))   | split_consistency_repair_probe |

## Near Miss Candidates

| blueprint_id                                       | seed_lane                  | label_family                       |   label_horizon_h | left_field                         | left_transform   | operator   | right_field          | right_transform   | expression                                                                                  | candidate_role                 |
|:---------------------------------------------------|:---------------------------|:-----------------------------------|------------------:|:-----------------------------------|:-----------------|:-----------|:---------------------|:------------------|:--------------------------------------------------------------------------------------------|:-------------------------------|
| core26ce_S0_positioning_price_basis_1572b807bf8d0c | S0_positioning_price_basis | L1_cross_sectional_relative_return |                24 | top_long_short_position_ratio_last | delta_4h         | Sub        | trade_return_24h     | delta_4h          | Sub(Delta(top_long_short_position_ratio_last,4),Delta(trade_return_24h,4))                  | split_consistency_repair_probe |
| core26ce_S0_positioning_price_basis_dbd1f8858fb841 | S0_positioning_price_basis | L0_raw_forward_return              |                24 | top_long_short_position_ratio_last | delta_4h         | Sub        | trade_return_24h     | delta_4h          | Sub(Delta(top_long_short_position_ratio_last,4),Delta(trade_return_24h,4))                  | split_consistency_repair_probe |
| core26ce_S0_positioning_price_basis_19256ade752751 | S0_positioning_price_basis | L1_cross_sectional_relative_return |                24 | top_long_short_position_ratio_last | delta_4h         | Sub        | trade_return_24h     | decay_72h         | Sub(Delta(top_long_short_position_ratio_last,4),Decay(trade_return_24h,72))                 | split_consistency_repair_probe |
| core26ce_S0_positioning_price_basis_79b945756f4d0d | S0_positioning_price_basis | L3_liquidity_tier_relative_return  |                24 | top_long_short_position_ratio_last | delta_4h         | Sub        | trade_return_24h     | decay_72h         | Sub(Delta(top_long_short_position_ratio_last,4),Decay(trade_return_24h,72))                 | split_consistency_repair_probe |
| core26ce_S0_positioning_price_basis_d943e251dc1b0c | S0_positioning_price_basis | L1_cross_sectional_relative_return |                24 | top_long_short_position_ratio_last | delta_4h         | Sub        | trade_return_24h     | zscore_168h       | Sub(Delta(top_long_short_position_ratio_last,4),ZScore(trade_return_24h))                   | split_consistency_repair_probe |
| core26ce_S0_positioning_price_basis_0922438f201b00 | S0_positioning_price_basis | L3_liquidity_tier_relative_return  |                24 | top_long_short_position_ratio_last | delta_4h         | Sub        | trade_return_24h     | zscore_168h       | Sub(Delta(top_long_short_position_ratio_last,4),ZScore(trade_return_24h))                   | split_consistency_repair_probe |
| core26ce_S0_positioning_price_basis_7bdd72b98aaa04 | S0_positioning_price_basis | L0_raw_forward_return              |                24 | top_long_short_position_ratio_last | delta_4h         | Sub        | trade_return_24h     | zscore_168h       | Sub(Delta(top_long_short_position_ratio_last,4),ZScore(trade_return_24h))                   | split_consistency_repair_probe |
| core26ce_S0_positioning_price_basis_2978693a972bc6 | S0_positioning_price_basis | L1_cross_sectional_relative_return |                24 | top_long_short_position_ratio_last | delta_4h         | Sub        | premium_close_bps    | delta_8h          | Sub(Delta(top_long_short_position_ratio_last,4),Delta(premium_close_bps,8))                 | split_consistency_repair_probe |
| core26ce_S0_positioning_price_basis_84ab6bfe2edb1e | S0_positioning_price_basis | L1_cross_sectional_relative_return |                 8 | top_long_short_position_ratio_last | delta_4h         | Sub        | premium_close_bps    | decay_24h         | Sub(Delta(top_long_short_position_ratio_last,4),Decay(premium_close_bps,24))                | split_consistency_repair_probe |
| core26ce_S0_positioning_price_basis_56873693af9391 | S0_positioning_price_basis | L1_cross_sectional_relative_return |                 8 | top_long_short_position_ratio_last | delta_4h         | Sub        | premium_close_bps    | decay_72h         | Sub(Delta(top_long_short_position_ratio_last,4),Decay(premium_close_bps,72))                | split_consistency_repair_probe |
| core26ce_S0_positioning_price_basis_e4809f4af7260a | S0_positioning_price_basis | L3_liquidity_tier_relative_return  |                 8 | top_long_short_position_ratio_last | delta_4h         | Sub        | premium_close_bps    | decay_72h         | Sub(Delta(top_long_short_position_ratio_last,4),Decay(premium_close_bps,72))                | split_consistency_repair_probe |
| core26ce_S0_positioning_price_basis_0bd45457514a47 | S0_positioning_price_basis | L3_liquidity_tier_relative_return  |                 8 | top_long_short_position_ratio_last | delta_4h         | Sub        | premium_close_bps    | zscore_168h       | Sub(Delta(top_long_short_position_ratio_last,4),ZScore(premium_close_bps))                  | split_consistency_repair_probe |
| core26ce_S0_positioning_price_basis_915af98d31e3cc | S0_positioning_price_basis | L0_raw_forward_return              |                24 | top_long_short_position_ratio_last | delta_4h         | Sub        | mark_trade_basis_bps | abs_zscore_168h   | Sub(Delta(top_long_short_position_ratio_last,4),Abs(ZScore(mark_trade_basis_bps)))          | split_consistency_repair_probe |
| core26ce_S0_positioning_price_basis_690bbc8108e16f | S0_positioning_price_basis | L1_cross_sectional_relative_return |                24 | top_long_short_position_ratio_last | delta_4h         | Sub        | mark_index_basis_bps | delta_24h         | Sub(Delta(top_long_short_position_ratio_last,4),Delta(mark_index_basis_bps,24))             | split_consistency_repair_probe |
| core26ce_S0_positioning_price_basis_d059531af1ab68 | S0_positioning_price_basis | L1_cross_sectional_relative_return |                24 | top_long_short_position_ratio_last | delta_4h         | Sub        | mark_index_basis_bps | decay_24h         | Sub(Delta(top_long_short_position_ratio_last,4),Decay(mark_index_basis_bps,24))             | split_consistency_repair_probe |
| core26ce_S0_positioning_price_basis_c53643e4fabd13 | S0_positioning_price_basis | L3_liquidity_tier_relative_return  |                24 | top_long_short_position_ratio_last | delta_4h         | Sub        | mark_index_basis_bps | decay_24h         | Sub(Delta(top_long_short_position_ratio_last,4),Decay(mark_index_basis_bps,24))             | split_consistency_repair_probe |
| core26ce_S3_cross_family_bridge_04bcda6c9d4973     | S3_cross_family_bridge     | L0_raw_forward_return              |                 8 | top_long_short_position_ratio_last | delta_8h         | SafeDiv    | mark_trade_basis_bps | delta_24h         | SafeDiv(Delta(top_long_short_position_ratio_last,8),Abs(Delta(mark_trade_basis_bps,24)))    | split_consistency_repair_probe |
| core26ce_S3_cross_family_bridge_ac414fa5f2efc8     | S3_cross_family_bridge     | L0_raw_forward_return              |                 8 | top_long_short_position_ratio_last | delta_8h         | SafeDiv    | mark_trade_basis_bps | abs_zscore_168h   | SafeDiv(Delta(top_long_short_position_ratio_last,8),Abs(Abs(ZScore(mark_trade_basis_bps)))) | split_consistency_repair_probe |
| core26ce_S3_cross_family_bridge_b9afe68d0b3ade     | S3_cross_family_bridge     | L0_raw_forward_return              |                 8 | top_long_short_position_ratio_last | delta_8h         | SafeDiv    | basis_abs_168h       | decay_72h         | SafeDiv(Delta(top_long_short_position_ratio_last,8),Abs(Decay(basis_abs_168h,72)))          | split_consistency_repair_probe |
| core26ce_S3_cross_family_bridge_1409db830695e3     | S3_cross_family_bridge     | L1_cross_sectional_relative_return |                24 | top_long_short_position_ratio_last | delta_8h         | Mul        | mark_trade_basis_bps | zscore_168h       | Mul(Delta(top_long_short_position_ratio_last,8),ZScore(mark_trade_basis_bps))               | split_consistency_repair_probe |
