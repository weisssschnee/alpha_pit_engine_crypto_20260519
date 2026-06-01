# CRYPTO A7FF-CORE16FE NON-BASIS ATLAS EXECUTION

Generated: 2026-06-01T09:21:46Z

## Decision

`HOLD_A7FFCORE16FE_NON_BASIS_ATLAS_SUPPLY_INSUFFICIENT`

CORE16FE executes the non-basis primitive/operator atlas reclassification authorized by CORE16F. It reuses the expanded response rows, applies non-basis family floors and near-miss lanes, and does not execute replay, formula generation, search, promotion, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core17": false,
  "authorizes_formula_generation": false,
  "authorizes_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "non_basis_candidate_count_lt_32",
    "non_basis_field_family_count_lt_4",
    "top_non_basis_family_share_gt_50pct"
  ],
  "decision": "HOLD_A7FFCORE16FE_NON_BASIS_ATLAS_SUPPLY_INSUFFICIENT",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T09:21:46Z",
  "near_miss_non_basis_count": 46,
  "next_allowed": "A7FF-CORE16FER non-basis atlas forensic / family-native repair",
  "response_rows": 2560,
  "source_decision": "PASS_A7FFCORE16F_NON_BASIS_SUPPLY_REPAIR_CONTRACT_READY_FOR_CORE16FE",
  "source_stage": "A7FF-CORE16F",
  "stage": "A7FF-CORE16FE",
  "strict_non_basis_candidate_count": 5,
  "strict_non_basis_field_family_count": 2,
  "top_non_basis_family_share": 0.8
}
```

## Family Supply Summary

| field_family   |   rows |   strict_candidate_count |   near_miss_count |   transform_count |   label_family_count |   median_control_ratio |
|:---------------|-------:|-------------------------:|------------------:|------------------:|---------------------:|-----------------------:|
| price_return   |    320 |                        4 |                37 |                10 |                    4 |               13.67    |
| positioning    |    480 |                        1 |                 2 |                10 |                    4 |               11.1439  |
| open_interest  |    480 |                        0 |                 6 |                10 |                    4 |               13.6725  |
| taker_flow     |    320 |                        0 |                 1 |                10 |                    4 |                5.02514 |
| liquidity      |    640 |                        0 |                 0 |                10 |                    4 |                9.97512 |
| volatility     |    320 |                        0 |                 0 |                10 |                    4 |               26.0082  |

## Strict Candidate Sample

| field_name                         | field_family   | transform         | label_family                       |   label_horizon_h |   control_ratio_premay_max | lag_ok   |
|:-----------------------------------|:---------------|:------------------|:-----------------------------------|------------------:|---------------------------:|:---------|
| top_long_short_position_ratio_last | positioning    | spread_short_long | L3_liquidity_tier_relative_return  |                24 |                   0.983348 | True     |
| trade_return_1h                    | price_return   | level             | L0_raw_forward_return              |                 4 |                   0.533585 | False    |
| trade_return_1h                    | price_return   | level             | L1_cross_sectional_relative_return |                 4 |                   0.533585 | False    |
| trade_return_1h                    | price_return   | level             | L3_liquidity_tier_relative_return  |                 4 |                   0.645321 | False    |
| trade_return_1h                    | price_return   | zscore_72h        | L3_liquidity_tier_relative_return  |                 1 |                   0.982173 | True     |

## Near Miss Sample

| field_name                         | field_family   | transform         | label_family                       |   label_horizon_h |   control_ratio_premay_max |   premay_positive_split_count |
|:-----------------------------------|:---------------|:------------------|:-----------------------------------|------------------:|---------------------------:|------------------------------:|
| open_interest_last                 | open_interest  | level             | L0_raw_forward_return              |                 8 |                    1.16816 |                             3 |
| open_interest_last                 | open_interest  | level             | L1_cross_sectional_relative_return |                 8 |                    1.16816 |                             3 |
| open_interest_last                 | open_interest  | level             | L3_liquidity_tier_relative_return  |                 8 |                    1.33392 |                             3 |
| open_interest_last                 | open_interest  | level             | L0_raw_forward_return              |                24 |                    1.17007 |                             3 |
| open_interest_last                 | open_interest  | level             | L1_cross_sectional_relative_return |                24 |                    1.17007 |                             3 |
| open_interest_last                 | open_interest  | level             | L3_liquidity_tier_relative_return  |                24 |                    1.14402 |                             3 |
| top_long_short_position_ratio_last | positioning    | spread_short_long | L0_raw_forward_return              |                24 |                    1.28778 |                             3 |
| top_long_short_position_ratio_last | positioning    | spread_short_long | L1_cross_sectional_relative_return |                24 |                    1.28778 |                             3 |
| trade_return_1h                    | price_return   | level             | L0_raw_forward_return              |                 1 |                    1.34143 |                             3 |
| trade_return_1h                    | price_return   | level             | L1_cross_sectional_relative_return |                 1 |                    1.34143 |                             3 |
| trade_return_1h                    | price_return   | level             | L3_liquidity_tier_relative_return  |                 1 |                    1.14918 |                             3 |
| trade_return_1h                    | price_return   | level             | L5_vol_adjusted_return             |                 1 |                    1.27518 |                             3 |
| trade_return_1h                    | price_return   | level             | L5_vol_adjusted_return             |                 4 |                    1.09896 |                             3 |
| trade_return_1h                    | price_return   | delta_1h          | L5_vol_adjusted_return             |                 1 |                    1.10505 |                             3 |
| trade_return_1h                    | price_return   | delta_1h          | L0_raw_forward_return              |                 4 |                    1.09957 |                             3 |
| trade_return_1h                    | price_return   | delta_1h          | L1_cross_sectional_relative_return |                 4 |                    1.09957 |                             3 |
| trade_return_1h                    | price_return   | delta_1h          | L3_liquidity_tier_relative_return  |                 4 |                    1.1667  |                             3 |
| trade_return_1h                    | price_return   | delta_1h          | L5_vol_adjusted_return             |                 4 |                    1.12453 |                             3 |
| trade_return_1h                    | price_return   | delta_24h         | L0_raw_forward_return              |                 1 |                    1.43724 |                             3 |
| trade_return_1h                    | price_return   | delta_24h         | L1_cross_sectional_relative_return |                 1 |                    1.43724 |                             3 |
| trade_return_1h                    | price_return   | delta_24h         | L3_liquidity_tier_relative_return  |                 1 |                    1.45865 |                             3 |
| trade_return_1h                    | price_return   | delta_24h         | L5_vol_adjusted_return             |                 1 |                    1.3964  |                             3 |
| trade_return_1h                    | price_return   | delta_24h         | L3_liquidity_tier_relative_return  |                 8 |                    1.1973  |                             3 |
| trade_return_1h                    | price_return   | zscore_72h        | L0_raw_forward_return              |                 1 |                    1.13499 |                             3 |
| trade_return_1h                    | price_return   | zscore_72h        | L1_cross_sectional_relative_return |                 1 |                    1.13499 |                             3 |
| trade_return_1h                    | price_return   | zscore_72h        | L5_vol_adjusted_return             |                 1 |                    1.12545 |                             3 |
| trade_return_1h                    | price_return   | zscore_168h       | L0_raw_forward_return              |                 1 |                    1.39641 |                             3 |
| trade_return_1h                    | price_return   | zscore_168h       | L1_cross_sectional_relative_return |                 1 |                    1.39641 |                             3 |
| trade_return_1h                    | price_return   | zscore_168h       | L3_liquidity_tier_relative_return  |                 1 |                    1.14435 |                             3 |
| trade_return_1h                    | price_return   | tsrank_72h        | L0_raw_forward_return              |                 1 |                    1.36467 |                             3 |
| trade_return_1h                    | price_return   | tsrank_72h        | L1_cross_sectional_relative_return |                 1 |                    1.36467 |                             3 |
| trade_return_1h                    | price_return   | tsrank_72h        | L3_liquidity_tier_relative_return  |                 1 |                    1.0818  |                             3 |
| trade_return_1h                    | price_return   | tsrank_72h        | L5_vol_adjusted_return             |                 1 |                    1.39299 |                             3 |
| trade_return_1h                    | price_return   | tsrank_168h       | L0_raw_forward_return              |                 1 |                    1.45587 |                             3 |
| trade_return_1h                    | price_return   | tsrank_168h       | L1_cross_sectional_relative_return |                 1 |                    1.45587 |                             3 |
| trade_return_1h                    | price_return   | tsrank_168h       | L3_liquidity_tier_relative_return  |                 1 |                    1.16836 |                             3 |
| trade_return_1h                    | price_return   | tsrank_168h       | L0_raw_forward_return              |                 4 |                    1.21203 |                             3 |
| trade_return_1h                    | price_return   | tsrank_168h       | L1_cross_sectional_relative_return |                 4 |                    1.21203 |                             3 |
| trade_return_1h                    | price_return   | tsrank_168h       | L3_liquidity_tier_relative_return  |                 4 |                    1.20686 |                             3 |
| trade_return_1h                    | price_return   | tsrank_168h       | L5_vol_adjusted_return             |                 4 |                    1.3529  |                             3 |
