# CRYPTO A7LS-4R COMPANY RETRY FORENSIC

Generated: 2026-06-05T10:31:18Z

## Decision

`PASS_A7LS4R_RETRY_MISSING_FIELDS_RESOLVED_WITH_NON_L7_CLUES`

## Summary

- retry_shards: s007, s013, s014
- missing_resolved_shards: 3 / 3
- pass_retry_shards: 2
- retry_response_rows: 3820
- retry_materialized_activity_ok_count: 191
- retry_non_l7_numeric_clue_rows: 6
- retry_rank_label_diagnostic_rows: 36
- original_a7ls4_non_l7_clue_rows: 22
- original_a7ls4_shortlist_rows: 22

## Retry Shards

| shard   | decision_before             | decision_after                                            | blockers_after          | missing_numeric_fields_after   |   materialized_activity_ok_count |   label_response_rows |   non_l7_numeric_clue_rows |   rank_label_diagnostic_clue_rows |   portfolio_queue_count |   selected_portfolio_queue_count | generated_at         |
|:--------|:----------------------------|:----------------------------------------------------------|:------------------------|:-------------------------------|---------------------------------:|----------------------:|---------------------------:|----------------------------------:|------------------------:|---------------------------------:|:---------------------|
| s007    | HOLD_A7LS3HR_MISSING_FIELDS | PASS_A7LS3HRS007_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                         |                                |                               64 |                  1280 |                          3 |                                10 |                      11 |                                6 | 2026-06-05T10:26:20Z |
| s013    | HOLD_A7LS3HR_MISSING_FIELDS | PASS_A7LS3HRS013_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                         |                                |                               64 |                  1280 |                          3 |                                21 |                      15 |                                7 | 2026-06-05T10:26:42Z |
| s014    | HOLD_A7LS3HR_MISSING_FIELDS | HOLD_A7LS3HRS014_NO_NON_L7_NUMERIC_CLUES                  | no_non_l7_numeric_clues |                                |                               63 |                  1260 |                          0 |                                 5 |                       5 |                                2 | 2026-06-05T10:26:29Z |

## Non-L7 Clues By Label

| label_family                       |   rows |
|:-----------------------------------|-------:|
| L3_liquidity_tier_relative_return  |      3 |
| L1_cross_sectional_relative_return |      2 |
| L0_raw_forward_return              |      1 |

## Non-L7 Clues By Semantic Pair

| semantic_pair      |   rows |
|:-------------------|-------:|
| basis_premium_like |      3 |
| listing_age_like   |      2 |
| volatility_like    |      1 |

## Non-L7 Clues By Pair And Label

| semantic_pair      | label_family                       |   rows |
|:-------------------|:-----------------------------------|-------:|
| basis_premium_like | L0_raw_forward_return              |      1 |
| basis_premium_like | L1_cross_sectional_relative_return |      1 |
| basis_premium_like | L3_liquidity_tier_relative_return  |      1 |
| listing_age_like   | L1_cross_sectional_relative_return |      1 |
| listing_age_like   | L3_liquidity_tier_relative_return  |      1 |
| volatility_like    | L3_liquidity_tier_relative_return  |      1 |

## New Non-L7 Clues

| shard   | blueprint_id           | expression                                           | semantic_pair      | motif      | label_family                       |   label_horizon_h |   control_ratio_premay_max |   robust_min_tstat_floor |   cost10_recent_oriented |   one_bar_lag_recent_oriented | decision                 |
|:--------|:-----------------------|:-----------------------------------------------------|:-------------------|:-----------|:-----------------------------------|------------------:|---------------------------:|-------------------------:|-------------------------:|------------------------------:|:-------------------------|
| s007    | a7ls1_3c36d00c9e737a31 | ZScore(Mean(age_x_volatility,168))                   | listing_age_like   | single     | L1_cross_sectional_relative_return |                 8 |                   0.95133  |                 0.805951 |             -0.000864825 |                   0.00115958  | A7LS3HRS007_NUMERIC_CLUE |
| s007    | a7ls1_b6803784df87ed01 | ZScore(Mean(age_x_volatility,72))                    | listing_age_like   | single     | L3_liquidity_tier_relative_return  |                 8 |                   0.972278 |                 0.817632 |             -0.000221383 |                   0.00164656  | A7LS3HRS007_NUMERIC_CLUE |
| s007    | a7ls1_4a98a63b7c1e3dca | Mean(realized_vol_168h,72)                           | volatility_like    | single     | L3_liquidity_tier_relative_return  |                 8 |                   0.991222 |                 0.795082 |             -0.000219521 |                   0.00164908  | A7LS3HRS007_NUMERIC_CLUE |
| s013    | a7ls1_5b62d6fed83d1c18 | Mul(mark_index_basis_bps,Sign(mark_trade_basis_bps)) | basis_premium_like | gated_sign | L0_raw_forward_return              |                 1 |                   0.343552 |                 2.71276  |             -0.00114818  |                   0.000403424 | A7LS3HRS013_NUMERIC_CLUE |
| s013    | a7ls1_5b62d6fed83d1c18 | Mul(mark_index_basis_bps,Sign(mark_trade_basis_bps)) | basis_premium_like | gated_sign | L1_cross_sectional_relative_return |                 1 |                   0.316392 |                 2.71276  |             -0.00114818  |                   0.000403424 | A7LS3HRS013_NUMERIC_CLUE |
| s013    | a7ls1_5b62d6fed83d1c18 | Mul(mark_index_basis_bps,Sign(mark_trade_basis_bps)) | basis_premium_like | gated_sign | L3_liquidity_tier_relative_return  |                 1 |                   0.269364 |                 3.03239  |             -0.00110544  |                   0.000324266 | A7LS3HRS013_NUMERIC_CLUE |

## Authorization

- Retry forensic only.
- This does not authorize search, alpha proof, shadow, paper, or live.
- If passed, it only authorizes drafting A7LS-5 follow-up / repair contract.