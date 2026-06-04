# CRYPTO A7FF-CORE59F NON-L7 CLUE FORENSIC

Generated: 2026-06-04T15:50:49Z

## Decision

`HOLD_CORE59F_THIN_OR_CONTROL_FRAGILE`

CORE59F audits the six non-L7 numeric clues from CORE59. It does not search, replay, or promote candidates.

## Decision Record

```json
{
  "all_cost10_positive": false,
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "blockers": [
    "control_ratio_ge_0_8"
  ],
  "decision": "HOLD_CORE59F_THIN_OR_CONTROL_FRAGILE",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-04T15:50:49Z",
  "input_core59_decision": "HOLD_A7FFCORE59_NUMERIC_REPAIR_EXECUTION",
  "max_control_ratio": 0.9049114010773984,
  "min_cost10_recent_oriented": -0.0015739941020676,
  "non_l7_clue_rows": 6,
  "non_l7_semantic_pair_count": 2,
  "non_l7_unique_blueprints": 6,
  "stage": "A7FF-CORE59F",
  "symbol_state_concentration_auditable": false,
  "top_semantic_pair_share": 0.8333333333333334
}
```

## Non-L7 Clue Table

| core59_shard   | blueprint_id             | semantic_pair                      | motif        | label_family                       |   label_horizon_h | decision                   |   control_ratio_premay_max |   control_margin |   cost2_recent_oriented |   cost5_recent_oriented |   cost10_recent_oriented |   robust_median_tstat_floor |   one_bar_lag_recent_oriented |   premay_positive_split_count | expression                                                  |
|:---------------|:-------------------------|:-----------------------------------|:-------------|:-----------------------------------|------------------:|:---------------------------|---------------------------:|-----------------:|------------------------:|------------------------:|-------------------------:|----------------------------:|------------------------------:|------------------------------:|:------------------------------------------------------------|
| s04            | a7ff24r_14eb7b2a6dbac47a | basis_premium_like|price_like      | safe_div_abs | L0_raw_forward_return              |                 4 | A7FFCORE59S04_NUMERIC_CLUE |                   0.526637 |        0.473363  |             0.000514103 |            -8.58967e-05 |              -0.0010859  |                    0.723367 |                   0.00027382  |                             3 | SafeDiv(Delta(mark_index_basis_bps,2),Abs(trade_return_1h)) |
| s05            | a7ff24r_7ffaf7bf0d76b7aa | basis_premium_like|price_like      | mul          | L1_cross_sectional_relative_return |                 1 | A7FFCORE59S05_NUMERIC_CLUE |                   0.904911 |        0.0950886 |             6.57406e-05 |            -0.000534259 |              -0.00153426 |                    0.718156 |                   0.000936717 |                             3 | Mul(mark_index_basis_bps,Delta(trade_return_1h,4))          |
| s05            | a7ff24r_5b64bd43e2dd09cb | basis_premium_like|price_like      | sub          | L3_liquidity_tier_relative_return  |                 1 | A7FFCORE59S05_NUMERIC_CLUE |                   0.78751  |        0.21249   |             2.60059e-05 |            -0.000573994 |              -0.00157399 |                    1.38375  |                   0.000408685 |                             3 | Sub(Delta(premium_close_bps,4),trade_return_1h)             |
| s05            | a7ff24r_3f478db63b994f6e | basis_premium_like|price_like      | safe_div_abs | L5_vol_adjusted_return             |                 1 | A7FFCORE59S05_NUMERIC_CLUE |                   0.835225 |        0.164775  |             0.0251159   |             0.0245159   |               0.0235159  |                    1.5592   |                   0.0131959   |                             3 | SafeDiv(Delta(premium_close_bps,2),Abs(trade_return_1h))    |
| s05            | a7ff24r_6406e38adf63bddf | basis_premium_like|price_like      | safe_div_abs | L5_vol_adjusted_return             |                 1 | A7FFCORE59S05_NUMERIC_CLUE |                   0.842278 |        0.157722  |             0.0512386   |             0.0506386   |               0.0496386  |                    1.40157  |                   0.0178209   |                             3 | SafeDiv(Mean(premium_close_bps,2),Abs(trade_return_1h))     |
| s05            | a7ff24r_58cd9af618657156 | basis_premium_like|volatility_like | mul          | L0_raw_forward_return              |                24 | A7FFCORE59S05_NUMERIC_CLUE |                   0.904002 |        0.0959982 |             0.00160626  |             0.00100626  |               6.2609e-06 |                    0.210272 |                   0.00130332  |                             3 | Mul(Delta(mark_index_basis_bps,2),realized_vol_24h)         |

## Label / Target Breakdown

| label_family                       |   label_horizon_h | decision                   |   row_count |
|:-----------------------------------|------------------:|:---------------------------|------------:|
| L5_vol_adjusted_return             |                 1 | A7FFCORE59S05_NUMERIC_CLUE |           2 |
| L0_raw_forward_return              |                 4 | A7FFCORE59S04_NUMERIC_CLUE |           1 |
| L0_raw_forward_return              |                24 | A7FFCORE59S05_NUMERIC_CLUE |           1 |
| L1_cross_sectional_relative_return |                 1 | A7FFCORE59S05_NUMERIC_CLUE |           1 |
| L3_liquidity_tier_relative_return  |                 1 | A7FFCORE59S05_NUMERIC_CLUE |           1 |

## Semantic Pair Breakdown

| semantic_pair                      | motif        |   row_count |
|:-----------------------------------|:-------------|------------:|
| basis_premium_like|price_like      | safe_div_abs |           3 |
| basis_premium_like|price_like      | mul          |           1 |
| basis_premium_like|price_like      | sub          |           1 |
| basis_premium_like|volatility_like | mul          |           1 |

## Control Margin Audit

| semantic_pair                      | label_family                       |   label_horizon_h |   rows |   unique_blueprints |   median_control_ratio |   max_control_ratio |    min_cost5 |   min_cost10 |   median_recent_spread |   robust_ok_rate |   lag_ok_rate |
|:-----------------------------------|:-----------------------------------|------------------:|-------:|--------------------:|-----------------------:|--------------------:|-------------:|-------------:|-----------------------:|-----------------:|--------------:|
| basis_premium_like|price_like      | L5_vol_adjusted_return             |                 1 |      2 |                   2 |               0.838752 |            0.842278 |  0.0245159   |   0.0235159  |           -0.0385773   |                1 |             1 |
| basis_premium_like|price_like      | L0_raw_forward_return              |                 4 |      1 |                   1 |               0.526637 |            0.526637 | -8.58967e-05 |  -0.0010859  |           -0.000914103 |                1 |             1 |
| basis_premium_like|price_like      | L1_cross_sectional_relative_return |                 1 |      1 |                   1 |               0.904911 |            0.904911 | -0.000534259 |  -0.00153426 |            0.000465741 |                1 |             1 |
| basis_premium_like|price_like      | L3_liquidity_tier_relative_return  |                 1 |      1 |                   1 |               0.78751  |            0.78751  | -0.000573994 |  -0.00157399 |           -0.000426006 |                1 |             1 |
| basis_premium_like|volatility_like | L0_raw_forward_return              |                24 |      1 |                   1 |               0.904002 |            0.904002 |  0.00100626  |   6.2609e-06 |           -0.00200626  |                1 |             1 |

## Cost Net Audit

| semantic_pair                      | label_family                       |   rows |   cost2_positive_rate |   cost5_positive_rate |   cost10_positive_rate |   min_cost10 |
|:-----------------------------------|:-----------------------------------|-------:|----------------------:|----------------------:|-----------------------:|-------------:|
| basis_premium_like|price_like      | L0_raw_forward_return              |      1 |                     1 |                     0 |                      0 |  -0.0010859  |
| basis_premium_like|price_like      | L1_cross_sectional_relative_return |      1 |                     1 |                     0 |                      0 |  -0.00153426 |
| basis_premium_like|price_like      | L3_liquidity_tier_relative_return  |      1 |                     1 |                     0 |                      0 |  -0.00157399 |
| basis_premium_like|price_like      | L5_vol_adjusted_return             |      2 |                     1 |                     1 |                      1 |   0.0235159  |
| basis_premium_like|volatility_like | L0_raw_forward_return              |      1 |                     1 |                     1 |                      1 |   6.2609e-06 |

## State Concentration Caveat

| audit_item                 | status                               | reason                                                                                                                   | fallback_used                                   |
|:---------------------------|:-------------------------------------|:-------------------------------------------------------------------------------------------------------------------------|:------------------------------------------------|
| symbol_state_concentration | UNAVAILABLE_IN_CORE59_NUMERIC_OUTPUT | CORE59 shard outputs do not include symbol_id, latent_state_id, meme, liquidity_tier, or per-row state exposure columns. | semantic_pair/motif/skeleton concentration only |
