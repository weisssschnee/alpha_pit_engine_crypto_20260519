# CRYPTO A7LS30 Productive Follow-Up Queue 20260610

## Decision

`PASS_A7LS30_PRODUCTIVE_FOLLOWUP_QUEUE_BUILT_NO_SEARCH_AUTH`

A7LS30 compiles an 8192-row numeric-probe queue from A7LS29 accepted evidence. It is deliberately larger than A7LS29, but it keeps family quotas so the next run expands productive information axes instead of only repeating basis/premium variants.

## Counts

- queue_rows: 8192
- shard_count: 16
- rows_per_shard: 512
- parent_rows_loaded: 2127
- candidate_rows_before_balance: 52560

## Family Summary

| semantic_pair                                          | motif               |   queue_rows |
|:-------------------------------------------------------|:--------------------|-------------:|
| open_interest_like\|positioning_like\|regime_state     | seed_gated_sign     |         2048 |
| open_interest_like\|positioning_like\|listing_age_like | seed_sub            |         1235 |
| open_interest_like\|positioning_like                   | smooth_mul          |          902 |
| basis_premium_like\|positioning_like                   | sub                 |          678 |
| basis_premium_like\|positioning_like                   | spread_rank         |          678 |
| basis_premium_like\|positioning_like                   | signed_spread       |          678 |
| basis_premium_like\|positioning_like                   | safe_div_abs        |          678 |
| open_interest_like\|positioning_like                   | safe_div_abs        |          634 |
| basis_premium_like\|age_x_volatility\|positioning_like | seed_mul            |          514 |
| basis_premium_like\|positioning_like                   | mean_reversion_gate |           92 |
| basis_premium_like\|age_x_volatility\|positioning_like | seed_sub            |           55 |

## Mutation Summary

| mutation_kind        | mutation_detail                                                |   queue_rows |
|:---------------------|:---------------------------------------------------------------|-------------:|
| interaction_probe    | gate_top_global_divergence_24                                  |          213 |
| interaction_probe    | gate_account_divergence_24                                     |          207 |
| wrapper_probe        | wrap_sign                                                      |          200 |
| wrapper_probe        | wrap_abs                                                       |          199 |
| wrapper_probe        | wrap_clip                                                      |          180 |
| wrapper_probe        | wrap_csrank                                                    |          176 |
| wrapper_probe        | wrap_neg                                                       |          174 |
| wrapper_probe        | wrap_zscore                                                    |          166 |
| interaction_probe    | gate_leverage_crowding                                         |          160 |
| interaction_probe    | gate_liquidity_cycle                                           |          158 |
| interaction_probe    | oi_residual_24                                                 |          129 |
| interaction_probe    | oi_scale_168                                                   |          129 |
| parent_identity      | keep                                                           |          105 |
| same_type_field_swap | field_swap_positioning_to_top_global_account_divergence        |          100 |
| same_type_field_swap | field_swap_positioning_to_top_long_short_position_ratio_mean   |          100 |
| same_type_field_swap | field_swap_positioning_to_top_long_short_account_ratio_mean    |           97 |
| same_type_field_swap | field_swap_positioning_to_top_long_short_account_ratio_last    |           87 |
| same_type_field_swap | field_swap_positioning_to_global_long_short_account_ratio_last |           86 |
| same_type_field_swap | field_swap_positioning_to_top_long_short_position_ratio_last   |           79 |
| same_type_field_swap | field_swap_positioning_to_account_position_divergence          |           78 |
| window_grid          | window_48_to_8                                                 |           76 |
| window_grid          | window_48_to_6                                                 |           76 |
| window_grid          | window_48_to_168                                               |           76 |
| window_grid          | window_48_to_3                                                 |           76 |
| window_grid          | window_48_to_720                                               |           75 |
| window_grid          | window_48_to_96                                                |           75 |
| window_grid          | window_48_to_72                                                |           75 |
| window_grid          | window_48_to_12                                                |           75 |
| window_grid          | window_48_to_336                                               |           75 |
| window_grid          | window_48_to_4                                                 |           75 |
| window_grid          | window_48_to_504                                               |           75 |
| window_grid          | window_48_to_16                                                |           75 |
| window_grid          | window_48_to_120                                               |           75 |
| window_grid          | window_48_to_240                                               |           75 |
| window_grid          | window_48_to_24                                                |           75 |
| same_type_field_swap | field_swap_basis_to_premium_close_bps                          |           73 |
| same_type_field_swap | field_swap_basis_to_mark_trade_basis_bps                       |           72 |
| same_type_field_swap | field_swap_basis_to_premium_abs_168h                           |           71 |
| window_grid          | window_48_to_36                                                |           69 |
| same_type_field_swap | field_swap_basis_to_basis_abs_168h                             |           61 |
| same_type_field_swap | field_swap_positioning_to_global_long_short_account_ratio_mean |           57 |
| window_grid          | window_168_to_12                                               |           45 |
| window_grid          | window_168_to_720                                              |           44 |
| window_grid          | window_168_to_120                                              |           44 |
| window_grid          | window_168_to_336                                              |           44 |
| window_grid          | window_168_to_16                                               |           44 |
| window_grid          | window_168_to_8                                                |           43 |
| window_grid          | window_168_to_48                                               |           43 |
| window_grid          | window_168_to_6                                                |           43 |
| window_grid          | window_168_to_72                                               |           43 |
| window_grid          | window_168_to_240                                              |           43 |
| window_grid          | window_168_to_24                                               |           42 |
| window_grid          | window_168_to_3                                                |           42 |
| window_grid          | window_168_to_4                                                |           42 |
| window_grid          | window_168_to_504                                              |           41 |
| window_grid          | window_168_to_36                                               |           41 |
| window_grid          | window_168_to_96                                               |           40 |
| window_grid          | window_4_to_72                                                 |           34 |
| window_grid          | window_4_to_720                                                |           34 |
| window_grid          | window_4_to_36                                                 |           34 |

## Shard Plan

| target_shard     |   queue_rows |
|:-----------------|-------------:|
| a7ls30_prod_s000 |          512 |
| a7ls30_prod_s001 |          512 |
| a7ls30_prod_s002 |          512 |
| a7ls30_prod_s003 |          512 |
| a7ls30_prod_s004 |          512 |
| a7ls30_prod_s005 |          512 |
| a7ls30_prod_s006 |          512 |
| a7ls30_prod_s007 |          512 |
| a7ls30_prod_s008 |          512 |
| a7ls30_prod_s009 |          512 |
| a7ls30_prod_s010 |          512 |
| a7ls30_prod_s011 |          512 |
| a7ls30_prod_s012 |          512 |
| a7ls30_prod_s013 |          512 |
| a7ls30_prod_s014 |          512 |
| a7ls30_prod_s015 |          512 |

## Boundary

```text
This queue authorizes numeric probes only after field gate PASS.
It does not authorize formula search, alpha proof, shadow, paper, or live.
```

## Outputs

- `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7ls30_productive_followup_queue_20260610\a7ls30_productive_followup_queue.csv`
- `G:\AlphaFactory_CryptoData\research_runtime\a7ls30_productive_followup_queue_20260610\a7ls30_productive_followup_queue.csv`
