# CRYPTO A7FF-CORE26DE NON-S0 LANE REPAIR PROBE

Generated: 2026-06-01T18:18:48Z

## Decision

`HOLD_A7FFCORE26DE_NON_S0_REPAIR_INSUFFICIENT`

CORE26DE executes a bounded S3/S1 non-S0 lane repair numeric probe. S0 is calibration-only. It does not authorize search, large search, alpha proof, shadow, paper, or live.

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
    "three_split_clean_lane_count_lt_3",
    "two_split_near_miss_count_lt_12"
  ],
  "decision": "HOLD_A7FFCORE26DE_NON_S0_REPAIR_INSUFFICIENT",
  "eval_error_count": 0,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T18:18:48Z",
  "next_allowed": "A7FF-CORE26DER non-S0 repair forensic",
  "numeric_rows": 2880,
  "repair_pool_count": 360,
  "source_decision": "PASS_A7FFCORE26D_NON_S0_LANE_REPAIR_CONTRACT_READY_FOR_CORE26DE",
  "source_stage": "A7FF-CORE26D",
  "stage": "A7FF-CORE26DE",
  "three_split_clean_count": 0,
  "three_split_clean_lane_count": 0,
  "two_split_near_miss_count": 9
}
```

## Lane Summary

| seed_lane                      |   candidates |   clean_3_split |   near_2_split |   median_control |   median_spread |
|:-------------------------------|-------------:|----------------:|---------------:|-----------------:|----------------:|
| S1_liquidity_basis_positioning |          180 |               0 |              7 |          3.77657 |    -0.000517831 |
| S3_cross_family_bridge         |          180 |               0 |              2 |          5.89386 |    -0.000391979 |

## Clean Candidates

`<empty>`

## Near Miss Candidates

| blueprint_id                                           | seed_lane                      | label_family                       |   label_horizon_h | left_field                         | left_transform   | operator   | right_field                        | right_transform   | expression                                                                           | candidate_role                 |
|:-------------------------------------------------------|:-------------------------------|:-----------------------------------|------------------:|:-----------------------------------|:-----------------|:-----------|:-----------------------------------|:------------------|:-------------------------------------------------------------------------------------|:-------------------------------|
| core26de_S3_cross_family_bridge_9d79f9c67790ef         | S3_cross_family_bridge         | L0_raw_forward_return              |                 8 | top_long_short_position_ratio_last | delta_8h         | SafeDiv    | basis_abs_168h                     | decay_24h         | SafeDiv(Delta(top_long_short_position_ratio_last,8),Abs(Decay(basis_abs_168h,24)))   | split_consistency_repair_probe |
| core26de_S3_cross_family_bridge_b9afe68d0b3ade         | S3_cross_family_bridge         | L0_raw_forward_return              |                 8 | top_long_short_position_ratio_last | delta_8h         | SafeDiv    | basis_abs_168h                     | decay_72h         | SafeDiv(Delta(top_long_short_position_ratio_last,8),Abs(Decay(basis_abs_168h,72)))   | split_consistency_repair_probe |
| core26de_S1_liquidity_basis_positioning_ad281d1bc8460d | S1_liquidity_basis_positioning | L1_cross_sectional_relative_return |                 8 | median_quote_volume_168h           | delta_24h        | Mul        | mark_index_basis_bps               | delta_8h          | Mul(Delta(median_quote_volume_168h,24),Delta(mark_index_basis_bps,8))                | split_consistency_repair_probe |
| core26de_S1_liquidity_basis_positioning_d61299d8e7ab49 | S1_liquidity_basis_positioning | L1_cross_sectional_relative_return |                24 | median_quote_volume_168h           | delta_24h        | Mul        | mark_index_basis_bps               | zscore_168h       | Mul(Delta(median_quote_volume_168h,24),ZScore(mark_index_basis_bps))                 | split_consistency_repair_probe |
| core26de_S1_liquidity_basis_positioning_a8f9b1a6e9430b | S1_liquidity_basis_positioning | L1_cross_sectional_relative_return |                 8 | median_quote_volume_168h           | delta_24h        | Mul        | premium_close_bps                  | decay_24h         | Mul(Delta(median_quote_volume_168h,24),Decay(premium_close_bps,24))                  | split_consistency_repair_probe |
| core26de_S1_liquidity_basis_positioning_e2d03d4eff4dc0 | S1_liquidity_basis_positioning | L0_raw_forward_return              |                 8 | median_quote_volume_168h           | delta_24h        | Mul        | premium_close_bps                  | zscore_168h       | Mul(Delta(median_quote_volume_168h,24),ZScore(premium_close_bps))                    | split_consistency_repair_probe |
| core26de_S1_liquidity_basis_positioning_4d4f4d3be0cc16 | S1_liquidity_basis_positioning | L1_cross_sectional_relative_return |                24 | median_quote_volume_168h           | delta_24h        | Mul        | top_long_short_position_ratio_last | delta_24h         | Mul(Delta(median_quote_volume_168h,24),Delta(top_long_short_position_ratio_last,24)) | split_consistency_repair_probe |
| core26de_S1_liquidity_basis_positioning_a6ac32effc76ae | S1_liquidity_basis_positioning | L3_liquidity_tier_relative_return  |                24 | median_quote_volume_168h           | delta_24h        | Mul        | top_long_short_position_ratio_last | delta_24h         | Mul(Delta(median_quote_volume_168h,24),Delta(top_long_short_position_ratio_last,24)) | split_consistency_repair_probe |
| core26de_S1_liquidity_basis_positioning_716139f1b09e69 | S1_liquidity_basis_positioning | L0_raw_forward_return              |                24 | median_quote_volume_168h           | delta_24h        | Mul        | top_long_short_position_ratio_last | delta_24h         | Mul(Delta(median_quote_volume_168h,24),Delta(top_long_short_position_ratio_last,24)) | split_consistency_repair_probe |
