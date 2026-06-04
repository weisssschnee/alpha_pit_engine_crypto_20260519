# CRYPTO A7FF-CORE61 INTEGRATED REPAIR PLAN

Generated: 2026-06-04T16:31:04Z

## Decision

`HOLD_CORE61_REPAIR_PLAN_REQUIRES_MATERIALIZATION_AND_TARGET_FIX`

CORE61 converts CORE60B/C/D bottleneck audits into a concrete repair queue preview and selector/materialization/target policies. It does not search, replay, or promote candidates.

## Decision Record

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core62a_non_l7_selector_dryrun": false,
  "authorizes_core62b_target_near_miss_dryrun": true,
  "authorizes_core62c_materialization_repair_dryrun": true,
  "authorizes_search": false,
  "blockers": [
    "exact_clean_non_l7_lt_4",
    "materialization_zero_activity_pairs_present"
  ],
  "decision": "HOLD_CORE61_REPAIR_PLAN_REQUIRES_MATERIALIZATION_AND_TARGET_FIX",
  "exact_clean_non_l7_rows": 3,
  "exact_non_l7_rows": 6,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-04T16:31:04Z",
  "inactive_semantic_pair_count": 2,
  "near_miss_rows": 313,
  "repair_candidate_rows": 319,
  "repair_semantic_pair_count": 6,
  "source_core60b_decision": "HOLD_CORE60B_TARGET_ADEQUACY_REPAIR_REQUIRED",
  "source_core60c_decision": "HOLD_CORE60C_MATERIALIZATION_REPAIR_REQUIRED",
  "source_core60d_decision": "HOLD_CORE60D_SELECTOR_STILL_RANK_BIASED",
  "stage": "A7FF-CORE61"
}
```

## Route Summary

| core61_route                           | core61_reason                 |   rows |   unique_blueprints |   semantic_pair_count |   median_control_ratio |   min_cost10 |   max_cost10 |
|:---------------------------------------|:------------------------------|-------:|--------------------:|----------------------:|-----------------------:|-------------:|-------------:|
| CORE62A_non_l7_selector_target_dryrun  | exact_non_l7_clue             |      6 |                   6 |                     2 |               0.838752 |  -0.00157399 |    0.0496386 |
| CORE62B_target_near_miss_repair_dryrun | near_miss_one_bar_lag_fragile |    174 |                  49 |                     6 |               0.651733 |  -0.00160536 |    0.149738  |
| CORE62B_target_near_miss_repair_dryrun | near_miss_control_dominated   |    109 |                  63 |                     6 |               1.13711  |  -0.00182533 |    0.270001  |
| CORE62B_target_near_miss_repair_dryrun | near_miss_pre_may_unstable    |     30 |                  17 |                     2 |               1.08992  |  -0.00246542 |    0.153963  |

## Repair Candidate Queue Preview

| blueprint_id             | core59_shard   | core61_route                           | core61_reason                 | core61_blocked   | semantic_pair                         | motif        | label_family                       |   label_horizon_h | decision                               |   premay_positive_split_count |   control_ratio |       cost10 | robust_ok   | lag_ok   | expression                                                                                  |
|:-------------------------|:---------------|:---------------------------------------|:------------------------------|:-----------------|:--------------------------------------|:-------------|:-----------------------------------|------------------:|:---------------------------------------|------------------------------:|----------------:|-------------:|:------------|:---------|:--------------------------------------------------------------------------------------------|
| a7ff24r_14eb7b2a6dbac47a | s04            | CORE62A_non_l7_selector_target_dryrun  | exact_non_l7_clue             | False            | basis_premium_like|price_like         | safe_div_abs | L0_raw_forward_return              |                 4 | A7FFCORE59S04_NUMERIC_CLUE             |                             3 |        0.526637 | -0.0010859   | True        | True     | SafeDiv(Delta(mark_index_basis_bps,2),Abs(trade_return_1h))                                 |
| a7ff24r_5b64bd43e2dd09cb | s05            | CORE62A_non_l7_selector_target_dryrun  | exact_non_l7_clue             | False            | basis_premium_like|price_like         | sub          | L3_liquidity_tier_relative_return  |                 1 | A7FFCORE59S05_NUMERIC_CLUE             |                             3 |        0.78751  | -0.00157399  | True        | True     | Sub(Delta(premium_close_bps,4),trade_return_1h)                                             |
| a7ff24r_3f478db63b994f6e | s05            | CORE62A_non_l7_selector_target_dryrun  | exact_non_l7_clue             | False            | basis_premium_like|price_like         | safe_div_abs | L5_vol_adjusted_return             |                 1 | A7FFCORE59S05_NUMERIC_CLUE             |                             3 |        0.835225 |  0.0235159   | True        | True     | SafeDiv(Delta(premium_close_bps,2),Abs(trade_return_1h))                                    |
| a7ff24r_6406e38adf63bddf | s05            | CORE62A_non_l7_selector_target_dryrun  | exact_non_l7_clue             | False            | basis_premium_like|price_like         | safe_div_abs | L5_vol_adjusted_return             |                 1 | A7FFCORE59S05_NUMERIC_CLUE             |                             3 |        0.842278 |  0.0496386   | True        | True     | SafeDiv(Mean(premium_close_bps,2),Abs(trade_return_1h))                                     |
| a7ff24r_58cd9af618657156 | s05            | CORE62A_non_l7_selector_target_dryrun  | exact_non_l7_clue             | False            | basis_premium_like|volatility_like    | mul          | L0_raw_forward_return              |                24 | A7FFCORE59S05_NUMERIC_CLUE             |                             3 |        0.904002 |  6.2609e-06  | True        | True     | Mul(Delta(mark_index_basis_bps,2),realized_vol_24h)                                         |
| a7ff24r_7ffaf7bf0d76b7aa | s05            | CORE62A_non_l7_selector_target_dryrun  | exact_non_l7_clue             | False            | basis_premium_like|price_like         | mul          | L1_cross_sectional_relative_return |                 1 | A7FFCORE59S05_NUMERIC_CLUE             |                             3 |        0.904911 | -0.00153426  | True        | True     | Mul(mark_index_basis_bps,Delta(trade_return_1h,4))                                          |
| a7ff24r_2809983f46ab7d37 | s04            | CORE62B_target_near_miss_repair_dryrun | near_miss_one_bar_lag_fragile | False            | basis_premium_like|basis_premium_like | sub          | L5_vol_adjusted_return             |                 1 | HOLD_A7FFCORE59S04_ONE_BAR_LAG_FRAGILE |                             3 |        0.164387 |  0.125786    | True        | False    | Sub(mark_index_basis_bps,Mean(premium_close_bps,4))                                         |
| a7ff24r_52a6ae8f1116e35c | s05            | CORE62B_target_near_miss_repair_dryrun | near_miss_one_bar_lag_fragile | False            | basis_premium_like|price_like         | safe_div_abs | L5_vol_adjusted_return             |                 1 | HOLD_A7FFCORE59S05_ONE_BAR_LAG_FRAGILE |                             3 |        0.188606 |  0.0898997   | True        | False    | SafeDiv(mark_index_basis_bps,Abs(ZScore(Mean(trade_return_1h,8))))                          |
| a7ff24r_2809983f46ab7d37 | s04            | CORE62B_target_near_miss_repair_dryrun | near_miss_one_bar_lag_fragile | False            | basis_premium_like|basis_premium_like | sub          | L1_cross_sectional_relative_return |                 1 | HOLD_A7FFCORE59S04_ONE_BAR_LAG_FRAGILE |                             3 |        0.195751 | -0.00110903  | True        | False    | Sub(mark_index_basis_bps,Mean(premium_close_bps,4))                                         |
| a7ff24r_16c27a7264d3bf28 | s04            | CORE62B_target_near_miss_repair_dryrun | near_miss_one_bar_lag_fragile | False            | basis_premium_like|price_like         | safe_div_abs | L1_cross_sectional_relative_return |                 1 | HOLD_A7FFCORE59S04_ONE_BAR_LAG_FRAGILE |                             3 |        0.200118 | -0.00100232  | True        | False    | SafeDiv(mark_index_basis_bps,Abs(Delta(trade_return_1h,1)))                                 |
| a7ff24r_55f0d29bc064638b | s05            | CORE62B_target_near_miss_repair_dryrun | near_miss_one_bar_lag_fragile | False            | basis_premium_like|volatility_like    | safe_div_abs | L5_vol_adjusted_return             |                 1 | HOLD_A7FFCORE59S05_ONE_BAR_LAG_FRAGILE |                             3 |        0.211248 |  0.10307     | True        | False    | SafeDiv(mark_index_basis_bps,Abs(ZScore(Mean(realized_vol_168h,2))))                        |
| a7ff24r_3fab392f9c9b9117 | s05            | CORE62B_target_near_miss_repair_dryrun | near_miss_one_bar_lag_fragile | False            | basis_premium_like|basis_premium_like | spread_rank  | L5_vol_adjusted_return             |                 1 | HOLD_A7FFCORE59S05_ONE_BAR_LAG_FRAGILE |                             3 |        0.212299 |  0.0682034   | True        | False    | Sub(CSRank(mark_index_basis_bps),CSRank(Delta(premium_close_bps,12)))                       |
| a7ff24r_0bb7454738389fdf | s04            | CORE62B_target_near_miss_repair_dryrun | near_miss_one_bar_lag_fragile | False            | basis_premium_like|price_like         | safe_div_abs | L5_vol_adjusted_return             |                 1 | HOLD_A7FFCORE59S04_ONE_BAR_LAG_FRAGILE |                             3 |        0.215974 |  0.103713    | True        | False    | SafeDiv(mark_index_basis_bps,Abs(Mean(trade_return_1h,8)))                                  |
| a7ff24r_58cd9af618657156 | s05            | CORE62B_target_near_miss_repair_dryrun | near_miss_one_bar_lag_fragile | False            | basis_premium_like|volatility_like    | mul          | L5_vol_adjusted_return             |                 1 | HOLD_A7FFCORE59S05_ONE_BAR_LAG_FRAGILE |                             3 |        0.220251 |  0.0946703   | True        | False    | Mul(Delta(mark_index_basis_bps,2),realized_vol_24h)                                         |
| a7ff24r_2809983f46ab7d37 | s04            | CORE62B_target_near_miss_repair_dryrun | near_miss_one_bar_lag_fragile | False            | basis_premium_like|basis_premium_like | sub          | L0_raw_forward_return              |                 1 | HOLD_A7FFCORE59S04_ONE_BAR_LAG_FRAGILE |                             3 |        0.222565 | -0.00110903  | True        | False    | Sub(mark_index_basis_bps,Mean(premium_close_bps,4))                                         |
| a7ff24r_16a015591ba6cab1 | s04            | CORE62B_target_near_miss_repair_dryrun | near_miss_one_bar_lag_fragile | False            | basis_premium_like|basis_premium_like | spread_rank  | L5_vol_adjusted_return             |                 1 | HOLD_A7FFCORE59S04_ONE_BAR_LAG_FRAGILE |                             3 |        0.233555 |  0.0831497   | True        | False    | Sub(CSRank(mark_index_basis_bps),CSRank(Mean(premium_close_bps,8)))                         |
| a7ff24r_41899ad2dd939b91 | s05            | CORE62B_target_near_miss_repair_dryrun | near_miss_one_bar_lag_fragile | False            | basis_premium_like|price_like         | safe_div_abs | L3_liquidity_tier_relative_return  |                 1 | HOLD_A7FFCORE59S05_ONE_BAR_LAG_FRAGILE |                             3 |        0.240415 | -0.000958152 | True        | False    | SafeDiv(mark_index_basis_bps,Abs(Mean(trade_return_1h,12)))                                 |
| a7ff24r_58cd9af618657156 | s05            | CORE62B_target_near_miss_repair_dryrun | near_miss_one_bar_lag_fragile | False            | basis_premium_like|volatility_like    | mul          | L3_liquidity_tier_relative_return  |                 1 | HOLD_A7FFCORE59S05_ONE_BAR_LAG_FRAGILE |                             3 |        0.258396 | -0.00115944  | True        | False    | Mul(Delta(mark_index_basis_bps,2),realized_vol_24h)                                         |
| a7ff24r_4df75107da3300e3 | s05            | CORE62B_target_near_miss_repair_dryrun | near_miss_one_bar_lag_fragile | False            | basis_premium_like|basis_premium_like | safe_div_abs | L5_vol_adjusted_return             |                 1 | HOLD_A7FFCORE59S05_ONE_BAR_LAG_FRAGILE |                             3 |        0.284052 |  0.0885092   | True        | False    | SafeDiv(mark_index_basis_bps,Abs(Mean(premium_close_bps,4)))                                |
| a7ff24r_1de5ef954b835313 | s04            | CORE62B_target_near_miss_repair_dryrun | near_miss_one_bar_lag_fragile | False            | basis_premium_like|basis_premium_like | safe_div_abs | L5_vol_adjusted_return             |                 1 | HOLD_A7FFCORE59S04_ONE_BAR_LAG_FRAGILE |                             3 |        0.286131 |  0.0952585   | True        | False    | SafeDiv(mark_index_basis_bps,Abs(ZScore(Mean(premium_close_bps,2))))                        |
| a7ff24r_1de5ef954b835313 | s04            | CORE62B_target_near_miss_repair_dryrun | near_miss_one_bar_lag_fragile | False            | basis_premium_like|basis_premium_like | safe_div_abs | L3_liquidity_tier_relative_return  |                 1 | HOLD_A7FFCORE59S04_ONE_BAR_LAG_FRAGILE |                             3 |        0.289999 | -0.00111557  | True        | False    | SafeDiv(mark_index_basis_bps,Abs(ZScore(Mean(premium_close_bps,2))))                        |
| a7ff24r_14eb7b2a6dbac47a | s04            | CORE62B_target_near_miss_repair_dryrun | near_miss_one_bar_lag_fragile | False            | basis_premium_like|price_like         | safe_div_abs | L5_vol_adjusted_return             |                 1 | HOLD_A7FFCORE59S04_ONE_BAR_LAG_FRAGILE |                             3 |        0.291724 |  0.0747923   | True        | False    | SafeDiv(Delta(mark_index_basis_bps,2),Abs(trade_return_1h))                                 |
| a7ff24r_41899ad2dd939b91 | s05            | CORE62B_target_near_miss_repair_dryrun | near_miss_one_bar_lag_fragile | False            | basis_premium_like|price_like         | safe_div_abs | L1_cross_sectional_relative_return |                 1 | HOLD_A7FFCORE59S05_ONE_BAR_LAG_FRAGILE |                             3 |        0.292357 | -0.000941045 | True        | False    | SafeDiv(mark_index_basis_bps,Abs(Mean(trade_return_1h,12)))                                 |
| a7ff24r_41899ad2dd939b91 | s05            | CORE62B_target_near_miss_repair_dryrun | near_miss_one_bar_lag_fragile | False            | basis_premium_like|price_like         | safe_div_abs | L5_vol_adjusted_return             |                 1 | HOLD_A7FFCORE59S05_ONE_BAR_LAG_FRAGILE |                             3 |        0.296589 |  0.109172    | True        | False    | SafeDiv(mark_index_basis_bps,Abs(Mean(trade_return_1h,12)))                                 |
| a7ff24r_16a015591ba6cab1 | s04            | CORE62B_target_near_miss_repair_dryrun | near_miss_one_bar_lag_fragile | False            | basis_premium_like|basis_premium_like | spread_rank  | L3_liquidity_tier_relative_return  |                 1 | HOLD_A7FFCORE59S04_ONE_BAR_LAG_FRAGILE |                             3 |        0.30757  | -0.00121562  | True        | False    | Sub(CSRank(mark_index_basis_bps),CSRank(Mean(premium_close_bps,8)))                         |
| a7ff24r_16c27a7264d3bf28 | s04            | CORE62B_target_near_miss_repair_dryrun | near_miss_one_bar_lag_fragile | False            | basis_premium_like|price_like         | safe_div_abs | L3_liquidity_tier_relative_return  |                 1 | HOLD_A7FFCORE59S04_ONE_BAR_LAG_FRAGILE |                             3 |        0.321003 | -0.00100089  | True        | False    | SafeDiv(mark_index_basis_bps,Abs(Delta(trade_return_1h,1)))                                 |
| a7ff24r_7b68fb1f6c2a4885 | s05            | CORE62B_target_near_miss_repair_dryrun | near_miss_one_bar_lag_fragile | False            | basis_premium_like|price_like         | safe_div_abs | L5_vol_adjusted_return             |                 1 | HOLD_A7FFCORE59S05_ONE_BAR_LAG_FRAGILE |                             3 |        0.321436 |  0.0843147   | True        | False    | SafeDiv(mark_index_basis_bps,Abs(ZScore(Mean(trade_return_1h,4))))                          |
| a7ff24r_16a015591ba6cab1 | s04            | CORE62B_target_near_miss_repair_dryrun | near_miss_one_bar_lag_fragile | False            | basis_premium_like|basis_premium_like | spread_rank  | L0_raw_forward_return              |                 1 | HOLD_A7FFCORE59S04_ONE_BAR_LAG_FRAGILE |                             3 |        0.33112  | -0.00122628  | True        | False    | Sub(CSRank(mark_index_basis_bps),CSRank(Mean(premium_close_bps,8)))                         |
| a7ff24r_4df75107da3300e3 | s05            | CORE62B_target_near_miss_repair_dryrun | near_miss_one_bar_lag_fragile | False            | basis_premium_like|basis_premium_like | safe_div_abs | L3_liquidity_tier_relative_return  |                 1 | HOLD_A7FFCORE59S05_ONE_BAR_LAG_FRAGILE |                             3 |        0.331863 | -0.00109224  | True        | False    | SafeDiv(mark_index_basis_bps,Abs(Mean(premium_close_bps,4)))                                |
| a7ff24r_fad5886189793630 | s03            | CORE62B_target_near_miss_repair_dryrun | near_miss_one_bar_lag_fragile | False            | basis_premium_like                    | single       | L5_vol_adjusted_return             |                 1 | HOLD_A7FFCORE59S03_ONE_BAR_LAG_FRAGILE |                             3 |        0.331902 |  0.134581    | True        | False    | Delta(mark_index_basis_bps,8)                                                               |
| a7ff24r_0b842e7d57714bb0 | s04            | CORE62B_target_near_miss_repair_dryrun | near_miss_one_bar_lag_fragile | False            | basis_premium_like|volatility_like    | gated_sign   | L5_vol_adjusted_return             |                 1 | HOLD_A7FFCORE59S04_ONE_BAR_LAG_FRAGILE |                             3 |        0.331902 |  0.134581    | True        | False    | Mul(Delta(mark_index_basis_bps,8),Sign(realized_vol_24h))                                   |
| a7ff24r_5e93346f70a68d33 | s05            | CORE62B_target_near_miss_repair_dryrun | near_miss_one_bar_lag_fragile | False            | basis_premium_like|volatility_like    | gated_sign   | L5_vol_adjusted_return             |                 1 | HOLD_A7FFCORE59S05_ONE_BAR_LAG_FRAGILE |                             3 |        0.331902 |  0.134581    | True        | False    | Mul(Delta(mark_index_basis_bps,8),Sign(realized_vol_168h))                                  |
| a7ff24r_55f0d29bc064638b | s05            | CORE62B_target_near_miss_repair_dryrun | near_miss_one_bar_lag_fragile | False            | basis_premium_like|volatility_like    | safe_div_abs | L0_raw_forward_return              |                 1 | HOLD_A7FFCORE59S05_ONE_BAR_LAG_FRAGILE |                             3 |        0.332281 | -0.00101139  | True        | False    | SafeDiv(mark_index_basis_bps,Abs(ZScore(Mean(realized_vol_168h,2))))                        |
| a7ff24r_1de5ef954b835313 | s04            | CORE62B_target_near_miss_repair_dryrun | near_miss_one_bar_lag_fragile | False            | basis_premium_like|basis_premium_like | safe_div_abs | L1_cross_sectional_relative_return |                 1 | HOLD_A7FFCORE59S04_ONE_BAR_LAG_FRAGILE |                             3 |        0.332864 | -0.00115024  | True        | False    | SafeDiv(mark_index_basis_bps,Abs(ZScore(Mean(premium_close_bps,2))))                        |
| a7ff24r_14eb7b2a6dbac47a | s04            | CORE62B_target_near_miss_repair_dryrun | near_miss_one_bar_lag_fragile | False            | basis_premium_like|price_like         | safe_div_abs | L1_cross_sectional_relative_return |                 1 | HOLD_A7FFCORE59S04_ONE_BAR_LAG_FRAGILE |                             3 |        0.347135 | -0.00135877  | True        | False    | SafeDiv(Delta(mark_index_basis_bps,2),Abs(trade_return_1h))                                 |
| a7ff24r_14eb7b2a6dbac47a | s04            | CORE62B_target_near_miss_repair_dryrun | near_miss_one_bar_lag_fragile | False            | basis_premium_like|price_like         | safe_div_abs | L0_raw_forward_return              |                 1 | HOLD_A7FFCORE59S04_ONE_BAR_LAG_FRAGILE |                             3 |        0.347135 | -0.00135877  | True        | False    | SafeDiv(Delta(mark_index_basis_bps,2),Abs(trade_return_1h))                                 |
| a7ff24r_16a015591ba6cab1 | s04            | CORE62B_target_near_miss_repair_dryrun | near_miss_one_bar_lag_fragile | False            | basis_premium_like|basis_premium_like | spread_rank  | L1_cross_sectional_relative_return |                 4 | HOLD_A7FFCORE59S04_ONE_BAR_LAG_FRAGILE |                             3 |        0.350734 | -0.00107798  | True        | False    | Sub(CSRank(mark_index_basis_bps),CSRank(Mean(premium_close_bps,8)))                         |
| a7ff24r_16a015591ba6cab1 | s04            | CORE62B_target_near_miss_repair_dryrun | near_miss_one_bar_lag_fragile | False            | basis_premium_like|basis_premium_like | spread_rank  | L0_raw_forward_return              |                 4 | HOLD_A7FFCORE59S04_ONE_BAR_LAG_FRAGILE |                             3 |        0.350734 | -0.00107798  | True        | False    | Sub(CSRank(mark_index_basis_bps),CSRank(Mean(premium_close_bps,8)))                         |
| a7ff24r_1dc128f3e9169a7f | s04            | CORE62B_target_near_miss_repair_dryrun | near_miss_one_bar_lag_fragile | False            | basis_premium_like|basis_premium_like | spread_rank  | L0_raw_forward_return              |                 1 | HOLD_A7FFCORE59S04_ONE_BAR_LAG_FRAGILE |                             3 |        0.357842 | -0.00145325  | True        | False    | Sub(CSRank(ZScore(Mean(mark_index_basis_bps,2))),CSRank(ZScore(Mean(premium_close_bps,8)))) |
| a7ff24r_16c27a7264d3bf28 | s04            | CORE62B_target_near_miss_repair_dryrun | near_miss_one_bar_lag_fragile | False            | basis_premium_like|price_like         | safe_div_abs | L5_vol_adjusted_return             |                 1 | HOLD_A7FFCORE59S04_ONE_BAR_LAG_FRAGILE |                             3 |        0.359498 |  0.10163     | True        | False    | SafeDiv(mark_index_basis_bps,Abs(Delta(trade_return_1h,1)))                                 |

## Target Repair Policy

| policy_id                 | rule                                                                                                      | threshold                                         |
|:--------------------------|:----------------------------------------------------------------------------------------------------------|:--------------------------------------------------|
| T0_non_l7_first           | CORE62 selector dryrun must score non-L7 labels first and treat L7 as diagnostic-only evidence            | selected_l7_share <= 0.40                         |
| T1_premay_stability_split | separate pre_may_unstable into split-sign instability vs weak magnitude; do not loosen pass gate globally | non_l7_target_count >= 4 before numeric expansion |
| T2_control_margin_floor   | non-L7 exact clue or near-miss must retain control_ratio < 1.0 for selector queue                         | hard reject control_ratio >= 1.0                  |
| T3_cost_floor             | cost10 negative candidates can only enter target forensic, not selector queue                             | selector cost10_recent_oriented > 0               |

## Materialization Repair Policy

| repair_item                       | affected_semantic_pairs                                       | evidence                                                 | action                                                                                          | next_stage                            |
|:----------------------------------|:--------------------------------------------------------------|:---------------------------------------------------------|:------------------------------------------------------------------------------------------------|:--------------------------------------|
| funding_positioning_zero_activity | basis_premium_like|funding_like;funding_like|positioning_like | CORE60C activity_ok_rows=0 for funding related pairs     | do not send these pairs to selector until panel availability / transform activity repair passes | CORE62C_materialization_repair_dryrun |
| basis_funding_sparse_finite_share | basis_premium_like|funding_like                               | median_finite_share near zero despite nonzero_share high | audit funding_rate timestamp/coverage and transform windows before any numeric expansion        | CORE62C_materialization_repair_dryrun |

## Selector Policy

```json
{
  "allowed_next": [
    "CORE62A non-L7 selector target dryrun on exact clean subset",
    "CORE62B target near-miss repair dryrun",
    "CORE62C materialization repair dryrun"
  ],
  "forbidden": [
    "formula search",
    "large search",
    "alpha proof",
    "shadow/paper/live"
  ],
  "hard_caps": {
    "selected_l7_share_max": 0.4,
    "selected_non_l7_min": 12,
    "selected_semantic_pair_min": 4,
    "top_semantic_pair_share_max": 0.35
  },
  "hard_reject": [
    "control_ratio >= 1.0",
    "cost10_recent_oriented <= 0 for selector route",
    "zero_activity_semantic_pair",
    "missing materialization contract"
  ],
  "selector_mode": "non_l7_first_repair_dryrun",
  "stage": "A7FF-CORE61"
}
```
