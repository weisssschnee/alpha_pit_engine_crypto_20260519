# CRYPTO A7FF-CORE63 DICE EXECUTION AUDIT

Generated: 2026-06-04T17:09:48Z

## Decision

`HOLD_CORE63_DICE_EXECUTION_REPAIRS_REQUIRED`

CORE63 executes the CORE62 dice batch as an audit: it scores target near-miss rows and diagnoses materialization blockers. It does not run formula search, replay promotion, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core64_materialization_fix": true,
  "authorizes_core64_retest_package": true,
  "authorizes_search": false,
  "blockers": [
    "materialization_repairs_required"
  ],
  "core62b_rows": 45,
  "core62c_pair_diagnosis_rows": 2,
  "decision": "HOLD_CORE63_DICE_EXECUTION_REPAIRS_REQUIRED",
  "executes_replay": false,
  "executes_search": false,
  "funding_sparse_state_alignment_pair_count": 2,
  "generated_at": "2026-06-04T17:09:48Z",
  "input_dice_rows": 47,
  "materialization_repair_pair_count": 2,
  "selected_numeric_retest_rows": 24,
  "selected_semantic_pair_count": 4,
  "stage": "A7FF-CORE63"
}
```

## Target Near-Miss Summary

| semantic_pair                         | core63_action                   |   rows |   selected |   median_repair_score |   median_control_ratio |   min_cost10 |   max_cost10 |
|:--------------------------------------|:--------------------------------|-------:|-----------:|----------------------:|-----------------------:|-------------:|-------------:|
| basis_premium_like|price_like         | entry_lag_repair_numeric_retest |     17 |         10 |              0.736203 |               0.62375  |  0.0309657   |  0.133736    |
| basis_premium_like|basis_premium_like | entry_lag_repair_numeric_retest |     16 |          7 |              0.686073 |               0.570307 |  0.0347346   |  0.13636     |
| basis_premium_like|volatility_like    | entry_lag_repair_numeric_retest |      8 |          5 |              0.781449 |               0.495024 |  0.0495287   |  0.134581    |
| basis_premium_like                    | entry_lag_repair_numeric_retest |      2 |          2 |              0.788739 |               0.47907  |  0.13034     |  0.134581    |
| basis_premium_like|basis_premium_like | target_gate_retest              |      2 |          0 |              0.388817 |               0.593715 |  0.000226096 |  0.000302848 |

## Selected Retest Queue

| blueprint_id             | semantic_pair                         | motif        | label_family           |   label_horizon_h | core61_reason                 |   repair_score |   control_ratio |    cost10 | expression                                                            |
|:-------------------------|:--------------------------------------|:-------------|:-----------------------|------------------:|:------------------------------|---------------:|----------------:|----------:|:----------------------------------------------------------------------|
| a7ff24r_2809983f46ab7d37 | basis_premium_like|basis_premium_like | sub          | L5_vol_adjusted_return |                 1 | near_miss_one_bar_lag_fragile |       0.87647  |        0.164387 | 0.125786  | Sub(mark_index_basis_bps,Mean(premium_close_bps,4))                   |
| a7ff24r_55f0d29bc064638b | basis_premium_like|volatility_like    | safe_div_abs | L5_vol_adjusted_return |                 1 | near_miss_one_bar_lag_fragile |       0.839696 |        0.211248 | 0.10307   | SafeDiv(mark_index_basis_bps,Abs(ZScore(Mean(realized_vol_168h,2))))  |
| a7ff24r_0bb7454738389fdf | basis_premium_like|price_like         | safe_div_abs | L5_vol_adjusted_return |                 1 | near_miss_one_bar_lag_fragile |       0.838921 |        0.215974 | 0.103713  | SafeDiv(mark_index_basis_bps,Abs(Mean(trade_return_1h,8)))            |
| a7ff24r_fad5886189793630 | basis_premium_like                    | single       | L5_vol_adjusted_return |                 1 | near_miss_one_bar_lag_fragile |       0.83501  |        0.331902 | 0.134581  | Delta(mark_index_basis_bps,8)                                         |
| a7ff24r_0b842e7d57714bb0 | basis_premium_like|volatility_like    | gated_sign   | L5_vol_adjusted_return |                 1 | near_miss_one_bar_lag_fragile |       0.83501  |        0.331902 | 0.134581  | Mul(Delta(mark_index_basis_bps,8),Sign(realized_vol_24h))             |
| a7ff24r_5e93346f70a68d33 | basis_premium_like|volatility_like    | gated_sign   | L5_vol_adjusted_return |                 1 | near_miss_one_bar_lag_fragile |       0.83501  |        0.331902 | 0.134581  | Mul(Delta(mark_index_basis_bps,8),Sign(realized_vol_168h))            |
| a7ff24r_52a6ae8f1116e35c | basis_premium_like|price_like         | safe_div_abs | L5_vol_adjusted_return |                 1 | near_miss_one_bar_lag_fragile |       0.833318 |        0.188606 | 0.0898997 | SafeDiv(mark_index_basis_bps,Abs(ZScore(Mean(trade_return_1h,8))))    |
| a7ff24r_58cd9af618657156 | basis_premium_like|volatility_like    | mul          | L5_vol_adjusted_return |                 1 | near_miss_one_bar_lag_fragile |       0.828595 |        0.220251 | 0.0946703 | Mul(Delta(mark_index_basis_bps,2),realized_vol_24h)                   |
| a7ff24r_41899ad2dd939b91 | basis_premium_like|price_like         | safe_div_abs | L5_vol_adjusted_return |                 1 | near_miss_one_bar_lag_fragile |       0.820195 |        0.296589 | 0.109172  | SafeDiv(mark_index_basis_bps,Abs(Mean(trade_return_1h,12)))           |
| a7ff24r_16a015591ba6cab1 | basis_premium_like|basis_premium_like | spread_rank  | L5_vol_adjusted_return |                 1 | near_miss_one_bar_lag_fragile |       0.813083 |        0.233555 | 0.0831497 | Sub(CSRank(mark_index_basis_bps),CSRank(Mean(premium_close_bps,8)))   |
| a7ff24r_1de5ef954b835313 | basis_premium_like|basis_premium_like | safe_div_abs | L5_vol_adjusted_return |                 1 | near_miss_one_bar_lag_fragile |       0.809419 |        0.286131 | 0.0952585 | SafeDiv(mark_index_basis_bps,Abs(ZScore(Mean(premium_close_bps,2))))  |
| a7ff24r_3fab392f9c9b9117 | basis_premium_like|basis_premium_like | spread_rank  | L5_vol_adjusted_return |                 1 | near_miss_one_bar_lag_fragile |       0.804514 |        0.212299 | 0.0682034 | Sub(CSRank(mark_index_basis_bps),CSRank(Delta(premium_close_bps,12))) |
| a7ff24r_4df75107da3300e3 | basis_premium_like|basis_premium_like | safe_div_abs | L5_vol_adjusted_return |                 1 | near_miss_one_bar_lag_fragile |       0.803294 |        0.284052 | 0.0885092 | SafeDiv(mark_index_basis_bps,Abs(Mean(premium_close_bps,4)))          |
| a7ff24r_16c27a7264d3bf28 | basis_premium_like|price_like         | safe_div_abs | L5_vol_adjusted_return |                 1 | near_miss_one_bar_lag_fragile |       0.79378  |        0.359498 | 0.10163   | SafeDiv(mark_index_basis_bps,Abs(Delta(trade_return_1h,1)))           |
| a7ff24r_7b68fb1f6c2a4885 | basis_premium_like|price_like         | safe_div_abs | L5_vol_adjusted_return |                 1 | near_miss_one_bar_lag_fragile |       0.787884 |        0.321436 | 0.0843147 | SafeDiv(mark_index_basis_bps,Abs(ZScore(Mean(trade_return_1h,4))))    |
| a7ff24r_14eb7b2a6dbac47a | basis_premium_like|price_like         | safe_div_abs | L5_vol_adjusted_return |                 1 | near_miss_one_bar_lag_fragile |       0.787275 |        0.291724 | 0.0747923 | SafeDiv(Delta(mark_index_basis_bps,2),Abs(trade_return_1h))           |
| a7ff24r_857b34a691777ebd | basis_premium_like|basis_premium_like | sub          | L5_vol_adjusted_return |                 1 | near_miss_one_bar_lag_fragile |       0.774166 |        0.540646 | 0.13636   | Sub(mark_index_basis_bps,ZScore(Mean(premium_close_bps,8)))           |
| a7ff24r_0976d19eda31e7f3 | basis_premium_like|basis_premium_like | safe_div_abs | L5_vol_adjusted_return |                 1 | near_miss_one_bar_lag_fragile |       0.773425 |        0.388999 | 0.0901245 | SafeDiv(Delta(mark_index_basis_bps,2),Abs(premium_close_bps))         |
| a7ff24r_3150667d0a336319 | basis_premium_like|price_like         | sub          | L5_vol_adjusted_return |                 1 | near_miss_one_bar_lag_fragile |       0.749577 |        0.602653 | 0.130373  | Sub(mark_index_basis_bps,Mean(trade_return_1h,8))                     |
| a7ff24r_09b35fe95cd05cef | basis_premium_like                    | single       | L5_vol_adjusted_return |                 1 | near_miss_one_bar_lag_fragile |       0.742468 |        0.626238 | 0.13034   | mark_index_basis_bps                                                  |
| a7ff24r_158a51cba747edb0 | basis_premium_like|price_like         | sub          | L5_vol_adjusted_return |                 1 | near_miss_one_bar_lag_fragile |       0.740374 |        0.62375  | 0.127499  | Sub(mark_index_basis_bps,Delta(trade_return_1h,4))                    |
| a7ff24r_82f9cbcbe2bc7d31 | basis_premium_like|price_like         | sub          | L5_vol_adjusted_return |                 1 | near_miss_one_bar_lag_fragile |       0.736203 |        0.629034 | 0.124914  | Sub(mark_index_basis_bps,Mean(trade_return_1h,2))                     |
| a7ff24r_28ad710f94ed7607 | basis_premium_like|price_like         | sub          | L5_vol_adjusted_return |                 1 | near_miss_one_bar_lag_fragile |       0.734656 |        0.645141 | 0.128198  | Sub(mark_index_basis_bps,Mean(trade_return_1h,12))                    |
| a7ff24r_258f236cd1332bb2 | basis_premium_like|volatility_like    | sub          | L5_vol_adjusted_return |                 1 | near_miss_one_bar_lag_fragile |       0.734302 |        0.658145 | 0.131746  | Sub(mark_index_basis_bps,realized_vol_168h)                           |

## Materialization Pair Diagnosis

| semantic_pair                   |   formulas |   rows |   eval_success_rate |   activity_ok_rows |   median_finite_share |   median_nonzero_share |   zero_finite_rate |   low_finite_rate |   uses_funding_rate |   uses_positioning | diagnosis                            | core63_repair                                                          |
|:--------------------------------|-----------:|-------:|--------------------:|-------------------:|----------------------:|-----------------------:|-------------------:|------------------:|--------------------:|-------------------:|:-------------------------------------|:-----------------------------------------------------------------------|
| basis_premium_like|funding_like |        360 |    360 |                   1 |                  0 |           0.000670305 |               0.958106 |           0.247222 |          0.830556 |                   1 |                  0 | funding_event_sparse_state_alignment | build PIT funding_state carry contract and retest funding interactions |
| funding_like|positioning_like   |         13 |     13 |                   1 |                  0 |           0.00326475  |               0.900716 |           0.230769 |          0.846154 |                   1 |                  1 | funding_event_sparse_state_alignment | build PIT funding_state carry contract and retest funding interactions |

## Materialization Formula Samples

| blueprint_id             | semantic_pair                   | motif               | expression                                                               |   finite_share |   nonzero_share |   std_value | activity_ok   |   error |
|:-------------------------|:--------------------------------|:--------------------|:-------------------------------------------------------------------------|---------------:|----------------:|------------:|:--------------|--------:|
| a7ff24r_193c23c778f33c29 | basis_premium_like|funding_like | mean_reversion_gate | Mul(Neg(ZScore(funding_rate)),Sign(index_close))                         |      0.129219  |        1        | 0.990647    | False         |     nan |
| a7ff24r_0da227d205e178ac | basis_premium_like|funding_like | mean_reversion_gate | Mul(Neg(ZScore(funding_rate)),Sign(ZScore(Mean(mark_close,2))))          |      0.128932  |        1        | 0.990623    | False         |     nan |
| a7ff24r_1aea30c74119dcdf | basis_premium_like|funding_like | mean_reversion_gate | Mul(Neg(ZScore(funding_rate)),Sign(ZScore(Mean(mark_close,4))))          |      0.128932  |        1        | 0.990623    | False         |     nan |
| a7ff24r_284dc20ea98bbb0f | basis_premium_like|funding_like | mean_reversion_gate | Mul(Neg(ZScore(funding_rate)),Sign(Mean(index_close,2)))                 |      0.128932  |        1        | 0.990638    | False         |     nan |
| a7ff24r_2a0c7c6aefc932a9 | basis_premium_like|funding_like | mean_reversion_gate | Mul(Neg(ZScore(funding_rate)),Sign(Delta(index_close,4)))                |      0.128932  |        0.999582 | 0.990598    | False         |     nan |
| a7ff24r_37d1d783fe9bda1a | basis_premium_like|funding_like | mean_reversion_gate | Mul(Neg(ZScore(funding_rate)),Sign(ZScore(Mean(index_close,4))))         |      0.128932  |        1        | 0.990623    | False         |     nan |
| a7ff24r_41a4132ece88bfea | basis_premium_like|funding_like | mean_reversion_gate | Mul(Neg(ZScore(funding_rate)),Sign(Delta(mark_close,1)))                 |      0.128932  |        0.99371  | 0.988097    | False         |     nan |
| a7ff24r_4620a26dc0b5c95d | basis_premium_like|funding_like | mean_reversion_gate | Mul(Neg(ZScore(funding_rate)),Sign(Delta(index_close,2)))                |      0.128932  |        0.999141 | 0.990174    | False         |     nan |
| a7ff24r_4f5b7ca54402a0af | basis_premium_like|funding_like | mean_reversion_gate | Mul(Neg(ZScore(funding_rate)),Sign(Delta(mark_close,2)))                 |      0.128932  |        0.995637 | 0.988956    | False         |     nan |
| a7ff24r_69c59c4138d4d405 | basis_premium_like|funding_like | mean_reversion_gate | Mul(Neg(ZScore(funding_rate)),Sign(Delta(mark_close,4)))                 |      0.128932  |        0.997029 | 0.990033    | False         |     nan |
| a7ff24r_7dc8efdb8624f089 | basis_premium_like|funding_like | mean_reversion_gate | Mul(Neg(ZScore(funding_rate)),Sign(Mean(index_close,4)))                 |      0.128932  |        1        | 0.990638    | False         |     nan |
| a7ff24r_272ed3672fb338ef | basis_premium_like|funding_like | mean_reversion_gate | Mul(Neg(ZScore(funding_rate)),Sign(Mean(index_close,8)))                 |      0.128872  |        1        | 0.990645    | False         |     nan |
| a7ff24r_32041f96444778a3 | basis_premium_like|funding_like | mean_reversion_gate | Mul(Neg(ZScore(funding_rate)),Sign(Delta(mark_close,8)))                 |      0.128872  |        0.998073 | 0.989668    | False         |     nan |
| a7ff24r_5ba56baccaeff778 | basis_premium_like|funding_like | mean_reversion_gate | Mul(Neg(ZScore(funding_rate)),Sign(ZScore(Mean(index_close,8))))         |      0.128872  |        1        | 0.99063     | False         |     nan |
| a7ff24r_202cd7051e9f71d9 | basis_premium_like|funding_like | mean_reversion_gate | Mul(Neg(ZScore(Delta(funding_rate,8))),Sign(Mean(index_close,4)))        |      0.128869  |        1        | 0.990692    | False         |     nan |
| a7ff24r_3c4b3c3459ac1b05 | basis_premium_like|funding_like | mean_reversion_gate | Mul(Neg(ZScore(Delta(funding_rate,8))),Sign(Mean(index_close,2)))        |      0.128869  |        1        | 0.990692    | False         |     nan |
| a7ff24r_663541efd2bc8130 | basis_premium_like|funding_like | mean_reversion_gate | Mul(Neg(ZScore(Delta(funding_rate,8))),Sign(index_close))                |      0.128869  |        1        | 0.990692    | False         |     nan |
| a7ff24r_5127541d55a7915e | basis_premium_like|funding_like | mean_reversion_gate | Mul(Neg(ZScore(funding_rate)),Sign(Mean(mark_close,12)))                 |      0.128585  |        1        | 0.990636    | False         |     nan |
| a7ff24r_01061e9da6c57340 | basis_premium_like|funding_like | relative_shock      | Mul(Delta(Delta(funding_rate,4),4),ZScore(ZScore(Mean(mark_close,4))))   |      0.0529481 |        0.621793 | 0.000101792 | False         |     nan |
| a7ff24r_121da44f010e6f04 | basis_premium_like|funding_like | relative_shock      | Mul(Delta(Delta(funding_rate,4),4),ZScore(Delta(index_close,8)))         |      0.0529481 |        0.621793 | 0.000101738 | False         |     nan |
| a7ff24r_1f850d01b74bf891 | basis_premium_like|funding_like | relative_shock      | Mul(Delta(Delta(funding_rate,4),4),ZScore(ZScore(Mean(mark_close,2))))   |      0.0529481 |        0.621793 | 0.00010179  | False         |     nan |
| a7ff24r_25649f8f4308a4ae | basis_premium_like|funding_like | relative_shock      | Mul(Delta(Delta(funding_rate,4),4),ZScore(Mean(index_close,2)))          |      0.0529481 |        0.621793 | 0.00010179  | False         |     nan |
| a7ff24r_2c83ab7f28ee6508 | basis_premium_like|funding_like | relative_shock      | Mul(Delta(Delta(funding_rate,4),4),ZScore(Delta(mark_close,1)))          |      0.0529481 |        0.621793 | 0.000108798 | False         |     nan |
| a7ff24r_36e8eb089d742dba | basis_premium_like|funding_like | relative_shock      | Mul(Delta(Delta(funding_rate,4),4),ZScore(mark_close))                   |      0.0529481 |        0.621793 | 0.000101789 | False         |     nan |
| a7ff24r_3b1cf74218132e08 | basis_premium_like|funding_like | relative_shock      | Mul(Delta(Delta(funding_rate,4),4),ZScore(Delta(index_close,4)))         |      0.0529481 |        0.621793 | 0.00010743  | False         |     nan |
| a7ff24r_53a20c0ae6e107e8 | basis_premium_like|funding_like | relative_shock      | Mul(Delta(Delta(funding_rate,4),4),ZScore(Delta(mark_close,8)))          |      0.0529481 |        0.621793 | 0.000103971 | False         |     nan |
| a7ff24r_54a51f0b5be98030 | basis_premium_like|funding_like | relative_shock      | Mul(Delta(Delta(funding_rate,4),4),ZScore(ZScore(Mean(mark_close,8))))   |      0.0529481 |        0.621793 | 0.000101793 | False         |     nan |
| a7ff24r_56b9f2c776bcbb4b | basis_premium_like|funding_like | relative_shock      | Mul(Delta(Delta(funding_rate,4),4),ZScore(Mean(index_close,4)))          |      0.0529481 |        0.621793 | 0.000101791 | False         |     nan |
| a7ff24r_6915d91d2854479b | basis_premium_like|funding_like | relative_shock      | Mul(Delta(Delta(funding_rate,4),4),ZScore(ZScore(Mean(index_close,4))))  |      0.0529481 |        0.621793 | 0.000101791 | False         |     nan |
| a7ff24r_698830203142c4fc | basis_premium_like|funding_like | relative_shock      | Mul(Delta(Delta(funding_rate,4),4),ZScore(index_close))                  |      0.0529481 |        0.621793 | 0.000101788 | False         |     nan |
| a7ff24r_6a3a66f83a7a1d2b | basis_premium_like|funding_like | relative_shock      | Mul(Delta(Delta(funding_rate,4),4),ZScore(Delta(index_close,1)))         |      0.0529481 |        0.621793 | 0.000109479 | False         |     nan |
| a7ff24r_6d45123575deb480 | basis_premium_like|funding_like | relative_shock      | Mul(Delta(Delta(funding_rate,4),4),ZScore(ZScore(Mean(index_close,2))))  |      0.0529481 |        0.621793 | 0.00010179  | False         |     nan |
| a7ff24r_31c2104c0961f35f | basis_premium_like|funding_like | relative_shock      | Mul(Delta(Delta(funding_rate,4),4),ZScore(ZScore(Mean(index_close,12)))) |      0.0528883 |        0.621365 | 0.000101849 | False         |     nan |
| a7ff24r_11f0ae1cb18dcca7 | basis_premium_like|funding_like | relative_shock      | Mul(Delta(Delta(funding_rate,8),4),ZScore(Delta(index_close,12)))        |      0.0528105 |        0.664041 | 8.65372e-05 | False         |     nan |
| a7ff24r_1bf1d30f01ce2eb9 | basis_premium_like|funding_like | relative_shock      | Mul(Delta(Delta(funding_rate,8),4),ZScore(ZScore(Mean(index_close,8))))  |      0.0528105 |        0.664041 | 8.64881e-05 | False         |     nan |
| a7ff24r_320e9878ac73f27a | basis_premium_like|funding_like | relative_shock      | Mul(Delta(Delta(funding_rate,8),4),ZScore(ZScore(Mean(index_close,12)))) |      0.0528105 |        0.664041 | 8.64908e-05 | False         |     nan |
| a7ff24r_32ccc276fd8c7856 | basis_premium_like|funding_like | relative_shock      | Mul(Delta(Delta(funding_rate,8),4),ZScore(Mean(mark_close,8)))           |      0.0528105 |        0.664041 | 8.6489e-05  | False         |     nan |
| a7ff24r_388f893048c51c90 | basis_premium_like|funding_like | relative_shock      | Mul(Delta(Delta(funding_rate,8),4),ZScore(ZScore(Mean(mark_close,8))))   |      0.0528105 |        0.664041 | 8.6489e-05  | False         |     nan |
| a7ff24r_4e1af7c9fbf9c6dc | basis_premium_like|funding_like | relative_shock      | Mul(Delta(Delta(funding_rate,8),4),ZScore(Mean(mark_close,4)))           |      0.0528105 |        0.664041 | 8.64868e-05 | False         |     nan |
| a7ff24r_51e323e575b9c369 | basis_premium_like|funding_like | relative_shock      | Mul(Delta(Delta(funding_rate,8),4),ZScore(Mean(index_close,12)))         |      0.0528105 |        0.664041 | 8.64908e-05 | False         |     nan |
