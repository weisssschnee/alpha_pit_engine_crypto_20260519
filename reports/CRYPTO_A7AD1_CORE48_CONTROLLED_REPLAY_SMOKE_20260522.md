# CRYPTO A7AD-1 Core48 Controlled Replay Smoke

Generated: 2026-05-22T14:41:52Z

## Decision

```text
HOLD_A7AD1_NO_CONTROL_CLEAN_PRE_MAY_CLUE
```

This stage is a small controlled replay smoke on the core48 common window. It is not formula search, not large search, and not alpha proof.

## Summary

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_shadow_paper_live": false,
  "control_rows": 624,
  "decision": "HOLD_A7AD1_NO_CONTROL_CLEAN_PRE_MAY_CLUE",
  "executes_replay": true,
  "executes_search": false,
  "generated_at": "2026-05-22T14:41:52Z",
  "generated_candidates": 156,
  "negative_control_research_like": 38,
  "output_dir": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ad1_core48_controlled_replay_smoke",
  "panel": "G:\\AlphaFactory_CryptoData\\gold\\panels\\crypto_core48_1h_with_metrics_candidate_v1.parquet",
  "report": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\reports\\CRYPTO_A7AD1_CORE48_CONTROLLED_REPLAY_SMOKE_20260522.md",
  "research_clues_pre_may_only": 0,
  "scoreboard_rows": 156,
  "symbols": 48,
  "timestamps": 18612
}
```

## Authorization

```json
{
  "authorizes_a7ad2_forensic_or_contract_revision": true,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "HOLD_A7AD1_NO_CONTROL_CLEAN_PRE_MAY_CLUE",
  "may_policy": "May unavailable in core48 common window; future May/backfilled stress remains post-selection only",
  "warnings": [
    "no_may_stress_available_for_core48_common_window",
    "this_is_controlled_smoke_not_formula_search",
    "matched_negative_controls_research_like_present_candidates_demoted",
    "no_pre_may_research_clues_after_controls"
  ]
}
```

## Family Summary

| family                             | decision       |   count |
|:-----------------------------------|:---------------|--------:|
| F0_low_turnover_price_basis        | A7AD1_REJECTED |      42 |
| F1_funding_residual_controls       | A7AD1_REJECTED |      12 |
| F2_metrics_crowding_oi_interaction | A7AD1_REJECTED |      74 |
| F3_cross_symbol_relative_strength  | A7AD1_REJECTED |      12 |
| F4_volatility_liquidity_capped     | A7AD1_REJECTED |      16 |

## Control Summary

| family                             | control_mode        | control_research_like   |   count |
|:-----------------------------------|:--------------------|:------------------------|--------:|
| F0_low_turnover_price_basis        | row_shuffle         | False                   |      42 |
| F0_low_turnover_price_basis        | sign_flip           | False                   |      42 |
| F0_low_turnover_price_basis        | time_shuffle        | False                   |      42 |
| F0_low_turnover_price_basis        | wrong_lag_stale_24h | False                   |      42 |
| F1_funding_residual_controls       | row_shuffle         | False                   |      12 |
| F1_funding_residual_controls       | sign_flip           | False                   |      11 |
| F1_funding_residual_controls       | sign_flip           | True                    |       1 |
| F1_funding_residual_controls       | time_shuffle        | False                   |      12 |
| F1_funding_residual_controls       | wrong_lag_stale_24h | False                   |       8 |
| F1_funding_residual_controls       | wrong_lag_stale_24h | True                    |       4 |
| F2_metrics_crowding_oi_interaction | row_shuffle         | False                   |      74 |
| F2_metrics_crowding_oi_interaction | sign_flip           | False                   |      74 |
| F2_metrics_crowding_oi_interaction | time_shuffle        | False                   |      74 |
| F2_metrics_crowding_oi_interaction | wrong_lag_stale_24h | False                   |      55 |
| F2_metrics_crowding_oi_interaction | wrong_lag_stale_24h | True                    |      19 |
| F3_cross_symbol_relative_strength  | row_shuffle         | False                   |      12 |
| F3_cross_symbol_relative_strength  | sign_flip           | False                   |      12 |
| F3_cross_symbol_relative_strength  | time_shuffle        | False                   |      12 |
| F3_cross_symbol_relative_strength  | wrong_lag_stale_24h | False                   |       7 |
| F3_cross_symbol_relative_strength  | wrong_lag_stale_24h | True                    |       5 |
| F4_volatility_liquidity_capped     | row_shuffle         | False                   |      16 |
| F4_volatility_liquidity_capped     | sign_flip           | False                   |       9 |
| F4_volatility_liquidity_capped     | sign_flip           | True                    |       7 |
| F4_volatility_liquidity_capped     | time_shuffle        | False                   |      16 |
| F4_volatility_liquidity_capped     | wrong_lag_stale_24h | False                   |      14 |
| F4_volatility_liquidity_capped     | wrong_lag_stale_24h | True                    |       2 |

## Top Raw Recent Candidates

| candidate_id                                             | family                             | expression                                                                                        |   horizon |   raw_validation_2025H1_ann_10bps_lag0 |   raw_recent_2025H2_2026Apr_ann_10bps_lag0 |   raw_recent_2025H2_2026Apr_ann_20bps_lag0 |   raw_recent_2025H2_2026Apr_ann_10bps_lag1 |   residual_funding_recent_2025H2_2026Apr_ann_10bps_lag0 |   residual_core4_recent_2025H2_2026Apr_ann_10bps_lag0 |   control_research_like_count | decision       | reject_reasons                                            |
|:---------------------------------------------------------|:-----------------------------------|:--------------------------------------------------------------------------------------------------|----------:|---------------------------------------:|-------------------------------------------:|-------------------------------------------:|-------------------------------------------:|--------------------------------------------------------:|------------------------------------------------------:|------------------------------:|:---------------|:----------------------------------------------------------|
| a7ad1_F2_metrics_crowding_oi_interaction_48_594bcd22578e | F2_metrics_crowding_oi_interaction | Mul(ZScore(open_interest_value_zscore_168h),Rank(realized_vol_24))                                |        48 |                              30.8468   |                                   26.4602  |                                   24.9745  |                                   26.4357  |                                                22.7722  |                                              23.928   |                             1 | A7AD1_REJECTED | ;negative_control_not_dominated                           |
| a7ad1_F2_metrics_crowding_oi_interaction_48_e286a5ba0381 | F2_metrics_crowding_oi_interaction | Mul(ZScore(open_interest_value_zscore_168h),Rank(ret_24))                                         |        48 |                              12.1185   |                                   20.7304  |                                   18.7194  |                                   20.6505  |                                                18.6427  |                                              18.4451  |                             1 | A7AD1_REJECTED | ;negative_control_not_dominated                           |
| a7ad1_F4_volatility_liquidity_capped_48_3aa22e494ac3     | F4_volatility_liquidity_capped     | Mul(Rank(open_interest_value_zscore_168h),Rank(realized_vol_24))                                  |        48 |                               7.16838  |                                   16.2506  |                                   14.995   |                                   16.058   |                                                15.6901  |                                              15.714   |                             1 | A7AD1_REJECTED | ;negative_control_not_dominated                           |
| a7ad1_F2_metrics_crowding_oi_interaction_48_afc30c00e56f | F2_metrics_crowding_oi_interaction | Mul(ZScore(open_interest_zscore_168h),Rank(realized_vol_24))                                      |        48 |                              21.2211   |                                   15.5141  |                                   14.1854  |                                   15.4242  |                                                14.0869  |                                              14.0307  |                             1 | A7AD1_REJECTED | ;negative_control_not_dominated                           |
| a7ad1_F2_metrics_crowding_oi_interaction_48_105456a9a4c3 | F2_metrics_crowding_oi_interaction | Mul(ZScore(open_interest_change_24h),Rank(ret_24))                                                |        48 |                              19.9014   |                                   15.4506  |                                   13.0519  |                                   16.1277  |                                                21.0247  |                                              18.9777  |                             1 | A7AD1_REJECTED | ;negative_control_not_dominated                           |
| a7ad1_F2_metrics_crowding_oi_interaction_48_0860c4f1ca07 | F2_metrics_crowding_oi_interaction | Mul(ZScore(open_interest_value_zscore_168h),Rank(premium_index))                                  |        48 |                               3.07617  |                                   14.7922  |                                    9.96903 |                                   14.5803  |                                                12.4486  |                                              12.4183  |                             1 | A7AD1_REJECTED | ;negative_control_not_dominated                           |
| a7ad1_F2_metrics_crowding_oi_interaction_48_c8c698935a31 | F2_metrics_crowding_oi_interaction | Mul(ZScore(open_interest_change_24h),Rank(realized_vol_24))                                       |        48 |                              18.7391   |                                   14.5842  |                                   12.6429  |                                   15.2873  |                                                19.4536  |                                              18.6556  |                             1 | A7AD1_REJECTED | ;negative_control_not_dominated                           |
| a7ad1_F2_metrics_crowding_oi_interaction_48_48e6f7e4cc77 | F2_metrics_crowding_oi_interaction | Mul(ZScore(open_interest_zscore_168h),Rank(ret_24))                                               |        48 |                              15.7089   |                                   14.4826  |                                   12.5559  |                                   14.2378  |                                                13.5753  |                                              12.6028  |                             1 | A7AD1_REJECTED | ;negative_control_not_dominated                           |
| a7ad1_F3_cross_symbol_relative_strength_48_f6abf388e45c  | F3_cross_symbol_relative_strength  | CrossSymbolRank(open_interest_value_zscore_168h)                                                  |        48 |                               8.27099  |                                   13.5793  |                                   12.2595  |                                   13.4165  |                                                12.2568  |                                              12.6938  |                             1 | A7AD1_REJECTED | ;negative_control_not_dominated                           |
| a7ad1_F2_metrics_crowding_oi_interaction_48_a0589f0c7d54 | F2_metrics_crowding_oi_interaction | Mul(ZScore(open_interest_value_zscore_168h),Rank(mark_index_ratio))                               |        48 |                               4.09887  |                                   13.5384  |                                    9.04378 |                                   13.2789  |                                                10.9046  |                                              11.0523  |                             1 | A7AD1_REJECTED | ;negative_control_not_dominated                           |
| a7ad1_F2_metrics_crowding_oi_interaction_48_713d50344766 | F2_metrics_crowding_oi_interaction | Mul(ZScore(open_interest_change_24h),Rank(mark_index_ratio))                                      |        48 |                               0.919718 |                                   13.1009  |                                    7.96112 |                                   13.1088  |                                                13.132   |                                              13.1556  |                             1 | A7AD1_REJECTED | ;negative_control_not_dominated                           |
| a7ad1_F3_cross_symbol_relative_strength_48_c8a1eca0553f  | F3_cross_symbol_relative_strength  | Mul(CrossSymbolRank(ret_24),CrossSymbolRank(open_interest_value_zscore_168h))                     |        48 |                               0.544219 |                                   12.5764  |                                   10.4402  |                                   12.5829  |                                                12.3855  |                                              12.0611  |                             1 | A7AD1_REJECTED | ;negative_control_not_dominated                           |
| a7ad1_F2_metrics_crowding_oi_interaction_24_594bcd22578e | F2_metrics_crowding_oi_interaction | Mul(ZScore(open_interest_value_zscore_168h),Rank(realized_vol_24))                                |        24 |                              13.6387   |                                   12.5162  |                                   11.0304  |                                   12.0891  |                                                12.0846  |                                              11.6638  |                             1 | A7AD1_REJECTED | ;negative_control_not_dominated                           |
| a7ad1_F2_metrics_crowding_oi_interaction_48_2305747e3836 | F2_metrics_crowding_oi_interaction | Mul(ZScore(open_interest_change_24h),Rank(premium_index))                                         |        48 |                               0.285759 |                                   11.9928  |                                    6.53159 |                                   11.977   |                                                11.6641  |                                              11.348   |                             1 | A7AD1_REJECTED | ;negative_control_not_dominated                           |
| a7ad1_F2_metrics_crowding_oi_interaction_48_df959f20337c | F2_metrics_crowding_oi_interaction | Mul(Neg(ZScore(top_long_short_position_ratio_zscore_168h)),Rank(open_interest_value_zscore_168h)) |        48 |                              -3.47536  |                                   11.1555  |                                    9.49368 |                                   11.2165  |                                                 8.44677 |                                               8.5791  |                             0 | A7AD1_REJECTED | raw_validation_nonpositive;negative_control_not_dominated |
| a7ad1_F2_metrics_crowding_oi_interaction_48_bd7f27054e3d | F2_metrics_crowding_oi_interaction | Mul(Neg(ZScore(top_long_short_position_ratio_zscore_168h)),Rank(open_interest_zscore_168h))       |        48 |                              -5.85554  |                                    9.70055 |                                    8.10572 |                                    9.75986 |                                                 7.32844 |                                               7.1564  |                             0 | A7AD1_REJECTED | raw_validation_nonpositive;negative_control_not_dominated |
| a7ad1_F2_metrics_crowding_oi_interaction_24_e286a5ba0381 | F2_metrics_crowding_oi_interaction | Mul(ZScore(open_interest_value_zscore_168h),Rank(ret_24))                                         |        24 |                               4.05568  |                                    9.19158 |                                    7.18065 |                                    8.61766 |                                                 9.16131 |                                               8.38551 |                             1 | A7AD1_REJECTED | ;negative_control_not_dominated                           |
| a7ad1_F2_metrics_crowding_oi_interaction_48_026dae3232b6 | F2_metrics_crowding_oi_interaction | Mul(Neg(ZScore(top_long_short_position_ratio_zscore_168h)),Rank(open_interest_change_24h))        |        48 |                               1.20856  |                                    9.12706 |                                    7.26749 |                                    9.29237 |                                                 6.97831 |                                               6.81173 |                             0 | A7AD1_REJECTED | ;negative_control_not_dominated                           |
| a7ad1_F4_volatility_liquidity_capped_24_3aa22e494ac3     | F4_volatility_liquidity_capped     | Mul(Rank(open_interest_value_zscore_168h),Rank(realized_vol_24))                                  |        24 |                               4.12539  |                                    8.38238 |                                    7.12676 |                                    8.08544 |                                                 9.20476 |                                               8.4632  |                             1 | A7AD1_REJECTED | ;negative_control_not_dominated                           |
| a7ad1_F2_metrics_crowding_oi_interaction_24_afc30c00e56f | F2_metrics_crowding_oi_interaction | Mul(ZScore(open_interest_zscore_168h),Rank(realized_vol_24))                                      |        24 |                              11.327    |                                    7.78398 |                                    6.4553  |                                    7.45621 |                                                 7.9256  |                                               7.40118 |                             1 | A7AD1_REJECTED | ;negative_control_not_dominated                           |
| a7ad1_F2_metrics_crowding_oi_interaction_48_d7481036181c | F2_metrics_crowding_oi_interaction | Mul(ZScore(open_interest_zscore_168h),Rank(mark_index_ratio))                                     |        48 |                               5.9444   |                                    7.54807 |                                    3.16918 |                                    7.23086 |                                                 6.25106 |                                               5.94681 |                             1 | A7AD1_REJECTED | ;negative_control_not_dominated                           |
| a7ad1_F3_cross_symbol_relative_strength_24_f6abf388e45c  | F3_cross_symbol_relative_strength  | CrossSymbolRank(open_interest_value_zscore_168h)                                                  |        24 |                               3.0292   |                                    7.33131 |                                    6.01158 |                                    7.04138 |                                                 6.79546 |                                               6.6161  |                             1 | A7AD1_REJECTED | ;negative_control_not_dominated                           |
| a7ad1_F4_volatility_liquidity_capped_48_9de0a97808d4     | F4_volatility_liquidity_capped     | Mul(Rank(quote_volume_mean_24),Rank(realized_vol_24))                                             |        48 |                               1.70678  |                                    7.3268  |                                    6.52068 |                                    7.47858 |                                                 6.8929  |                                               5.57437 |                             0 | A7AD1_REJECTED | ;negative_control_not_dominated                           |
| a7ad1_F2_metrics_crowding_oi_interaction_24_48e6f7e4cc77 | F2_metrics_crowding_oi_interaction | Mul(ZScore(open_interest_zscore_168h),Rank(ret_24))                                               |        24 |                               7.58096  |                                    7.26857 |                                    5.3418  |                                    6.89252 |                                                 7.50528 |                                               6.44922 |                             1 | A7AD1_REJECTED | ;negative_control_not_dominated                           |
| a7ad1_F2_metrics_crowding_oi_interaction_24_0860c4f1ca07 | F2_metrics_crowding_oi_interaction | Mul(ZScore(open_interest_value_zscore_168h),Rank(premium_index))                                  |        24 |                              -2.21824  |                                    6.67411 |                                    1.85094 |                                    6.34742 |                                                 5.28146 |                                               5.04727 |                             0 | A7AD1_REJECTED | raw_validation_nonpositive                                |
| a7ad1_F4_volatility_liquidity_capped_48_e07b6322525c     | F4_volatility_liquidity_capped     | Mul(Rank(quote_asset_volume),Rank(realized_vol_24))                                               |        48 |                               0.237949 |                                    6.46315 |                                    4.80387 |                                    6.53178 |                                                 6.01052 |                                               4.98038 |                             0 | A7AD1_REJECTED | ;negative_control_not_dominated                           |
| a7ad1_F2_metrics_crowding_oi_interaction_24_713d50344766 | F2_metrics_crowding_oi_interaction | Mul(ZScore(open_interest_change_24h),Rank(mark_index_ratio))                                      |        24 |                              -3.49894  |                                    6.44283 |                                    1.30303 |                                    6.11846 |                                                 7.32023 |                                               7.34529 |                             0 | A7AD1_REJECTED | raw_validation_nonpositive                                |
| a7ad1_F2_metrics_crowding_oi_interaction_24_a0589f0c7d54 | F2_metrics_crowding_oi_interaction | Mul(ZScore(open_interest_value_zscore_168h),Rank(mark_index_ratio))                               |        24 |                              -1.48806  |                                    6.3411  |                                    1.84646 |                                    5.98534 |                                                 4.81873 |                                               4.74925 |                             0 | A7AD1_REJECTED | raw_validation_nonpositive                                |
| a7ad1_F2_metrics_crowding_oi_interaction_48_5304ba3e486b | F2_metrics_crowding_oi_interaction | Mul(ZScore(open_interest_zscore_168h),Rank(premium_index))                                        |        48 |                               3.41007  |                                    6.21568 |                                    1.5214  |                                    5.93012 |                                                 5.21203 |                                               4.64196 |                             1 | A7AD1_REJECTED | ;negative_control_not_dominated                           |
| a7ad1_F3_cross_symbol_relative_strength_24_c8a1eca0553f  | F3_cross_symbol_relative_strength  | Mul(CrossSymbolRank(ret_24),CrossSymbolRank(open_interest_value_zscore_168h))                     |        24 |                              -2.43303  |                                    6.19588 |                                    4.05965 |                                    5.69723 |                                                 5.85859 |                                               5.418   |                             0 | A7AD1_REJECTED | raw_validation_nonpositive                                |

## Pre-May Research Clue Shortlist

`<empty>`

## Boundary

- May is unavailable for the core48 common window and is not used.
- Matched controls are evaluated and any control-like pass demotes the candidate.
- FundingCore/Core4 are residual benchmarks only.
- Any shortlist item is `pre-May-only research clue`, not alpha proof and not shadow/paper/live eligible.
