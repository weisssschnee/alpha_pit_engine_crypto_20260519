# CRYPTO A7FF-42 FAMILY-BALANCED CONTROL-STRICT NUMERIC

Generated: 2026-05-30T15:40:54Z

## Decision

`HOLD_A7FF42_FAMILY_BALANCED_NUMERIC_SELECTED_TOO_THIN`

A7FF-42 runs a family-balanced numeric follow-up from the A7FF-R7 repaired operator-pair policy. It is numeric-only: no formula search, no replay promotion, and no alpha proof authorization.

## Manifest

```json
{
  "activity_ok_count": 333,
  "authorizes_a7ff43_deep_forensic": false,
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "control_strict_non_l7_clue_family_count": 3,
  "control_strict_non_l7_clue_rows": 173,
  "decision": "HOLD_A7FF42_FAMILY_BALANCED_NUMERIC_SELECTED_TOO_THIN",
  "eval_failure_count": 0,
  "eval_success_count": 361,
  "executes_generation": false,
  "executes_numeric_probe": true,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T15:40:54Z",
  "numeric_probe_decision": "PASS_A7FF42_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH",
  "numeric_sample_count": 361,
  "process_exit_code": 0,
  "queue_count": 361,
  "selected_control_strict_non_l7_count": 4,
  "selected_control_strict_non_l7_family_count": 1,
  "selected_count": 12,
  "source_a7ffr7_decision": "PASS_A7FFR7_OPERATOR_PAIR_REPAIR_READY_FOR_A7FF42_FAMILY_BALANCED_NUMERIC_NO_SEARCH_AUTH",
  "stage": "A7FF-42",
  "started_at": "2026-05-30T14:57:42Z",
  "timed_out": false,
  "uses_may": false,
  "warnings": [
    "selected_control_strict_non_l7_family_count_below_2"
  ]
}
```

## Queue Summary

| a7ff42_queue_role           | semantic_pair                         | motif         |   queue_count |   skeleton_count |
|:----------------------------|:--------------------------------------|:--------------|--------------:|-----------------:|
| family_balanced_candidate   | funding_like|basis_premium_like       | spread_rank   |            52 |                6 |
| family_balanced_candidate   | regime_state|price_return_like        | spread_rank   |            52 |                5 |
| family_balanced_candidate   | funding_like|basis_premium_like       | sub           |            52 |                6 |
| family_balanced_candidate   | regime_state|price_return_like        | sub           |            52 |                5 |
| capped_reference_diagnostic | basis_premium_like|basis_premium_like | safe_div_clip |            51 |                6 |
| family_balanced_candidate   | funding_like|basis_premium_like       | mul           |            51 |                6 |
| family_balanced_candidate   | funding_like|basis_premium_like       | zspread       |            51 |                6 |

## Control-Strict Summary

| semantic_pair                         | motif         | label_family                       |   clue_rows |   blueprints |   min_control_ratio |   median_control_ratio |
|:--------------------------------------|:--------------|:-----------------------------------|------------:|-------------:|--------------------:|-----------------------:|
| basis_premium_like|basis_premium_like | safe_div_clip | L3_liquidity_tier_relative_return  |          15 |           13 |            0.213787 |               0.340308 |
| basis_premium_like|basis_premium_like | safe_div_clip | L5_vol_adjusted_return             |          14 |           11 |            0.287628 |               0.4836   |
| basis_premium_like|basis_premium_like | safe_div_clip | L0_raw_forward_return              |          13 |           10 |            0.181577 |               0.450267 |
| basis_premium_like|basis_premium_like | safe_div_clip | L1_cross_sectional_relative_return |          13 |           10 |            0.268642 |               0.450267 |
| funding_like|basis_premium_like       | spread_rank   | L1_cross_sectional_relative_return |          12 |            8 |            0.222637 |               0.617193 |
| funding_like|basis_premium_like       | spread_rank   | L0_raw_forward_return              |          11 |            8 |            0.283261 |               0.652913 |
| funding_like|basis_premium_like       | spread_rank   | L3_liquidity_tier_relative_return  |          10 |            8 |            0.20048  |               0.442339 |
| funding_like|basis_premium_like       | zspread       | L3_liquidity_tier_relative_return  |           7 |            7 |            0.374095 |               0.560757 |
| funding_like|basis_premium_like       | sub           | L5_vol_adjusted_return             |           7 |            6 |            0.200322 |               0.605056 |
| funding_like|basis_premium_like       | zspread       | L0_raw_forward_return              |           6 |            6 |            0.461761 |               0.570211 |
| funding_like|basis_premium_like       | zspread       | L1_cross_sectional_relative_return |           6 |            6 |            0.404554 |               0.570211 |
| regime_state|price_return_like        | spread_rank   | L3_liquidity_tier_relative_return  |           6 |            6 |            0.485797 |               0.554115 |
| regime_state|price_return_like        | sub           | L0_raw_forward_return              |           6 |            6 |            0.440454 |               0.563973 |
| regime_state|price_return_like        | sub           | L1_cross_sectional_relative_return |           6 |            6 |            0.43998  |               0.71692  |
| regime_state|price_return_like        | sub           | L3_liquidity_tier_relative_return  |           6 |            6 |            0.591728 |               0.676634 |
| funding_like|basis_premium_like       | sub           | L0_raw_forward_return              |           7 |            5 |            0.328438 |               0.526042 |
| funding_like|basis_premium_like       | sub           | L1_cross_sectional_relative_return |           6 |            5 |            0.419373 |               0.584372 |
| funding_like|basis_premium_like       | zspread       | L5_vol_adjusted_return             |           5 |            5 |            0.235123 |               0.473591 |
| regime_state|price_return_like        | spread_rank   | L0_raw_forward_return              |           5 |            5 |            0.385759 |               0.543163 |
| funding_like|basis_premium_like       | sub           | L3_liquidity_tier_relative_return  |           3 |            3 |            0.311511 |               0.396257 |
| regime_state|price_return_like        | spread_rank   | L1_cross_sectional_relative_return |           3 |            3 |            0.426227 |               0.569095 |
| funding_like|basis_premium_like       | spread_rank   | L5_vol_adjusted_return             |           2 |            2 |            0.596357 |               0.649425 |
| regime_state|price_return_like        | spread_rank   | L5_vol_adjusted_return             |           2 |            2 |            0.706707 |               0.736702 |
| funding_like|basis_premium_like       | mul           | L0_raw_forward_return              |           1 |            1 |            0.753324 |               0.753324 |
| regime_state|price_return_like        | sub           | L5_vol_adjusted_return             |           1 |            1 |            0.786398 |               0.786398 |

## Selected Forensic

| blueprint_id            | expression                                                                                      | semantic_pair                         | motif         | label_family            |   label_horizon_h |   orientation_from_train |   premay_positive_split_count | premay_all_positive   |   control_ratio_premay_max |   one_bar_lag_recent_oriented | lag_ok   |   robust_median_tstat_floor |   robust_min_tstat_floor | robust_ok   |   cost2_recent_oriented |   cost5_recent_oriented |   cost10_recent_oriented |   avg_n_obs_recent | decision                          |   train_2024_n |   train_2024_mean_spread |   train_2024_tstat |   train_2024_nonoverlap_median_tstat |   train_2024_nonoverlap_min_tstat |   train_2024_positive_rate |   validation_2025H1_n |   validation_2025H1_mean_spread |   validation_2025H1_tstat |   validation_2025H1_nonoverlap_median_tstat |   validation_2025H1_nonoverlap_min_tstat |   validation_2025H1_positive_rate |   test_2025H2_n |   test_2025H2_mean_spread |   test_2025H2_tstat |   test_2025H2_nonoverlap_median_tstat |   test_2025H2_nonoverlap_min_tstat |   test_2025H2_positive_rate |   recent_oos_2026JanApr_n |   recent_oos_2026JanApr_mean_spread |   recent_oos_2026JanApr_tstat |   recent_oos_2026JanApr_nonoverlap_median_tstat |   recent_oos_2026JanApr_nonoverlap_min_tstat |   recent_oos_2026JanApr_positive_rate |   non_l7_bonus |   score_no_may | skeleton_key          |   finite_share |   nonzero_share | is_non_l7   | is_control_strict   | a7ff42_role                    |
|:------------------------|:------------------------------------------------------------------------------------------------|:--------------------------------------|:--------------|:------------------------|------------------:|-------------------------:|------------------------------:|:----------------------|---------------------------:|------------------------------:|:---------|----------------------------:|-------------------------:|:------------|------------------------:|------------------------:|-------------------------:|-------------------:|:----------------------------------|---------------:|-------------------------:|-------------------:|-------------------------------------:|----------------------------------:|---------------------------:|----------------------:|--------------------------------:|--------------------------:|--------------------------------------------:|-----------------------------------------:|----------------------------------:|----------------:|--------------------------:|--------------------:|--------------------------------------:|-----------------------------------:|----------------------------:|--------------------------:|------------------------------------:|------------------------------:|------------------------------------------------:|---------------------------------------------:|--------------------------------------:|---------------:|---------------:|:----------------------|---------------:|----------------:|:------------|:--------------------|:-------------------------------|
| a7ff33_cbeab61121c2f170 | Clip(SafeDiv(mark_index_basis_bps,Abs(Mean(mark_index_basis_bps,24))),-5,5)                     | basis_premium_like|basis_premium_like | safe_div_clip | L5_vol_adjusted_return  |                 8 |                       -1 |                             3 | True                  |                   0.866934 |                     0.220374  | True     |                    1.23816  |                2.13628   | True        |               0.378901  |               0.378301  |                0.377301  |            94.9333 | A7FF42_NUMERIC_CLUE               |            673 |              -0.00949645 |          -0.354149 |                          -0.51121    |                         -1.21659  |                   0.491828 |                   712 |                      -0.0889733 |                  -3.02325 |                                   -1.23816  |                               -2.13628   |                          0.438202 |             712 |                -0.121595  |            -2.99478 |                             -1.31048  |                         -2.30957   |                    0.441011 |                       712 |                          -0.379301  |                      -5.65607 |                                        -2.05216 |                                    -4.06078  |                              0.426966 |              1 |       384.434  | skel_6badd2926fa2941d |       0.993105 |        0.987345 | True        | False               | selected_other                 |
| a7ff33_43985dd6fcd563f5 | Sub(funding_rate_state_last_ffill_8h,Delta(mark_index_basis_bps,12))                            | funding_like|basis_premium_like       | sub           | L5_vol_adjusted_return  |                 8 |                        1 |                             3 | True                  |                   0.916697 |                     0.228051  | True     |                    0.734567 |               -0.804198  | True        |               0.36285   |               0.36225   |                0.36125   |            94.9333 | A7FF42_NUMERIC_CLUE               |            700 |               0.0108357  |           0.368366 |                           0.00579681 |                         -0.771762 |                   0.517143 |                   712 |                       0.0568177 |                   2.12138 |                                    0.734567 |                               -0.804198  |                          0.553371 |             712 |                 0.131355  |             3.28019 |                              1.10952  |                         -0.0558444 |                    0.56882  |                       712 |                           0.36325   |                       5.33369 |                                         2.36663 |                                    -0.184564 |                              0.587079 |              1 |       368.333  | skel_f8484b844efd270f |       0.82456  |        0.999996 | True        | False               | selected_other                 |
| a7ff33_0c0da14842542e13 | Sub(ZScore(funding_rate_state_last_ffill_8h),ZScore(mark_index_basis_bps))                      | funding_like|basis_premium_like       | zspread       | L5_vol_adjusted_return  |                 1 |                        1 |                             3 | True                  |                   0.288989 |                     0.0342378 | True     |                    5.48711  |                5.48711   | True        |               0.123516  |               0.122916  |                0.121916  |            95.8667 | A7FF42_NUMERIC_CLUE               |            719 |               0.0168323  |           1.55056  |                           1.55056    |                          1.55056  |                   0.515994 |                   719 |                       0.0588513 |                   5.48711 |                                    5.48711  |                                5.48711   |                          0.606398 |             719 |                 0.114742  |             7.88518 |                              7.88518  |                          7.88518   |                    0.64395  |                       719 |                           0.123916  |                       5.84124 |                                         5.84124 |                                     5.84124  |                              0.599444 |              1 |       129.627  | skel_293cae94cfd91548 |       0.828007 |        1        | True        | True                | selected_control_strict_non_l7 |
| a7ff33_eda87df62c06d036 | Sub(ZScore(funding_rate_state_last_ffill_8h),ZScore(Clip(ZScore(mark_index_basis_bps),-3,3)))   | funding_like|basis_premium_like       | zspread       | L5_vol_adjusted_return  |                 1 |                        1 |                             3 | True                  |                   0.235123 |                     0.0373996 | True     |                    5.82468  |                5.82468   | True        |               0.123363  |               0.122763  |                0.121763  |            95.8667 | A7FF42_NUMERIC_CLUE               |            719 |               0.0183237  |           1.69468  |                           1.69468    |                          1.69468  |                   0.527121 |                   719 |                       0.062169  |                   5.82468 |                                    5.82468  |                                5.82468   |                          0.61057  |             719 |                 0.114444  |             7.83688 |                              7.83688  |                          7.83688   |                    0.649513 |                       719 |                           0.123763  |                       5.83419 |                                         5.83419 |                                     5.83419  |                              0.600834 |              1 |       129.528  | skel_8ee95cdec48a7c8f |       0.828007 |        1        | True        | True                | selected_control_strict_non_l7 |
| a7ff33_e47466b4dff6534a | Sub(CSRank(funding_rate_state_last_ffill_8h),CSRank(Rank(mark_index_basis_bps)))                | funding_like|basis_premium_like       | spread_rank   | L5_vol_adjusted_return  |                 4 |                        1 |                             3 | True                  |                   0.702493 |                     0.0327683 | True     |                    1.04002  |               -0.0320945 | True        |               0.120379  |               0.119779  |                0.118779  |            95.4667 | A7FF42_NUMERIC_CLUE               |            716 |               0.0102568  |           0.566096 |                           0.203871   |                         -0.44883  |                   0.52095  |                   716 |                       0.0363112 |                   1.69628 |                                    1.04002  |                               -0.0320945 |                          0.557263 |             716 |                 0.0949996 |             3.64945 |                              1.88823  |                          1.0265    |                    0.571229 |                       716 |                           0.120779  |                       3.20528 |                                         1.93152 |                                     0.212583 |                              0.561453 |              1 |       126.077  | skel_897201905b87a210 |       0.828007 |        0.984073 | True        | True                | selected_control_strict_non_l7 |
| a7ff33_0f11f1f312e75801 | Sub(ZScore(funding_rate_state_last_ffill_8h),ZScore(Delta(mark_index_basis_bps,12)))            | funding_like|basis_premium_like       | zspread       | L5_vol_adjusted_return  |                 1 |                        1 |                             3 | True                  |                   0.517418 |                     0.0626258 | True     |                    4.21137  |                4.21137   | True        |               0.110888  |               0.110288  |                0.109288  |            95.8667 | A7FF42_NUMERIC_CLUE               |            707 |               0.0122248  |           1.13418  |                           1.13418    |                          1.13418  |                   0.527581 |                   719 |                       0.0462945 |                   4.21137 |                                    4.21137  |                                4.21137   |                          0.59249  |             719 |                 0.0915294 |             6.69868 |                              6.69868  |                          6.69868   |                    0.634214 |                       719 |                           0.111288  |                       5.50754 |                                         5.50754 |                                     5.50754  |                              0.582754 |              1 |       116.771  | skel_1a1b3fb29dff7328 |       0.82456  |        1        | True        | True                | selected_control_strict_non_l7 |
| a7ff33_749bb59c8d5f88e0 | Sub(funding_rate_state_last_ffill_8h,ZScore(Mean(mark_index_basis_bps,2)))                      | funding_like|basis_premium_like       | sub           | L5_vol_adjusted_return  |                 1 |                        1 |                             3 | True                  |                   0.95048  |                     0.03122   | True     |                    4.35586  |                4.35586   | True        |               0.106684  |               0.106084  |                0.105084  |            95.8667 | A7FF42_NUMERIC_CLUE               |            718 |               0.00316302 |           0.318373 |                           0.318373   |                          0.318373 |                   0.508357 |                   719 |                       0.0432613 |                   4.35586 |                                    4.35586  |                                4.35586   |                          0.595271 |             719 |                 0.109751  |             7.5078  |                              7.5078   |                          7.5078    |                    0.620306 |                       719 |                           0.107084  |                       5.17991 |                                         5.17991 |                                     5.17991  |                              0.553547 |              1 |       112.134  | skel_a2f58ee62d9e7ad2 |       0.82772  |        1        | True        | False               | selected_other                 |
| a7ff33_8f587010df0608c7 | Sub(rolling_coverage_168h,trade_return_1h)                                                      | regime_state|price_return_like        | sub           | L7_ranked_future_return |                 1 |                        1 |                             3 | True                  |                   0.235941 |                     0.023036  | True     |                    6.23942  |                6.23942   | True        |               0.0724315 |               0.0718315 |                0.0708315 |            95.8667 | A7FF42_RANK_LABEL_DIAGNOSTIC_CLUE |            719 |               0.0742998  |           9.6597   |                           9.6597     |                          9.6597   |                   0.632823 |                   719 |                       0.0447364 |                   6.23942 |                                    6.23942  |                                6.23942   |                          0.620306 |             719 |                 0.0634821 |             9.62007 |                              9.62007  |                          9.62007   |                    0.670376 |                       719 |                           0.0728315 |                      10.8065  |                                        10.8065  |                                    10.8065   |                              0.666203 |              0 |        77.5956 | skel_337820bc5afcf6cc |       0.827348 |        1        | False       | True                | selected_rank_label_diagnostic |
| a7ff33_a23e4aaed43083ba | Sub(rolling_coverage_168h,Clip(ZScore(trade_return_1h),-3,3))                                   | regime_state|price_return_like        | sub           | L7_ranked_future_return |                 1 |                        1 |                             3 | True                  |                   0.235941 |                     0.023051  | True     |                    6.23942  |                6.23942   | True        |               0.0723824 |               0.0717824 |                0.0707824 |            95.8667 | A7FF42_RANK_LABEL_DIAGNOSTIC_CLUE |            719 |               0.0742998  |           9.6597   |                           9.6597     |                          9.6597   |                   0.632823 |                   719 |                       0.0447364 |                   6.23942 |                                    6.23942  |                                6.23942   |                          0.620306 |             719 |                 0.0634821 |             9.62007 |                              9.62007  |                          9.62007   |                    0.670376 |                       719 |                           0.0727824 |                      10.8026  |                                        10.8026  |                                    10.8026   |                              0.666203 |              0 |        77.5465 | skel_593666ed3f85046b |       0.827348 |        1        | False       | True                | selected_rank_label_diagnostic |
| a7ff33_aa7f647e1c08045a | Sub(rolling_coverage_168h,CSRank(trade_return_1h))                                              | regime_state|price_return_like        | sub           | L7_ranked_future_return |                 1 |                        1 |                             3 | True                  |                   0.235941 |                     0.023051  | True     |                    6.23942  |                6.23942   | True        |               0.0723824 |               0.0717824 |                0.0707824 |            95.8667 | A7FF42_RANK_LABEL_DIAGNOSTIC_CLUE |            719 |               0.0742998  |           9.6597   |                           9.6597     |                          9.6597   |                   0.632823 |                   719 |                       0.0447364 |                   6.23942 |                                    6.23942  |                                6.23942   |                          0.620306 |             719 |                 0.0634821 |             9.62007 |                              9.62007  |                          9.62007   |                    0.670376 |                       719 |                           0.0727824 |                      10.8026  |                                        10.8026  |                                    10.8026   |                              0.666203 |              0 |        77.5465 | skel_d9d4f69744bac825 |       0.827348 |        0.989583 | False       | True                | selected_rank_label_diagnostic |
| a7ff33_e6580c90109deb50 | Sub(ZScore(funding_rate_state_last_ffill_8h),ZScore(ZScore(Mean(mark_index_basis_bps,2))))      | funding_like|basis_premium_like       | zspread       | L5_vol_adjusted_return  |                 1 |                        1 |                             3 | True                  |                   0.96855  |                     0.0322552 | True     |                    2.39124  |                2.39124   | True        |               0.0707622 |               0.0701622 |                0.0691622 |            95.8667 | A7FF42_NUMERIC_CLUE               |            718 |               0.00517533 |           0.472599 |                           0.472599   |                          0.472599 |                   0.51532  |                   719 |                       0.0270855 |                   2.39124 |                                    2.39124  |                                2.39124   |                          0.560501 |             719 |                 0.0796302 |             5.46263 |                              5.46263  |                          5.46263   |                    0.606398 |                       719 |                           0.0711622 |                       3.32748 |                                         3.32748 |                                     3.32748  |                              0.553547 |              1 |        76.1936 | skel_a923757a8885923c |       0.82772  |        1        | True        | False               | selected_other                 |
| a7ff33_519c72e5a1d4478a | Sub(ZScore(funding_rate_state_last_ffill_8h),ZScore(Abs(ZScore(Mean(mark_index_basis_bps,8))))) | funding_like|basis_premium_like       | zspread       | L7_ranked_future_return |                 4 |                        1 |                             3 | True                  |                   0.717824 |                     0.030545  | True     |                    0.864417 |                0.782364  | True        |               0.0304726 |               0.0298726 |                0.0288726 |            95.4667 | A7FF42_RANK_LABEL_DIAGNOSTIC_CLUE |            709 |               0.00844736 |           1.5287   |                           0.728565   |                         -0.597285 |                   0.527504 |                   716 |                       0.0167566 |                   3.3101  |                                    1.4909   |                                1.07464   |                          0.560056 |             716 |                 0.0106886 |             1.76219 |                              0.864417 |                          0.782364  |                    0.50838  |                       716 |                           0.0308726 |                       4.91208 |                                         2.54665 |                                     1.49543  |                              0.581006 |              0 |        35.1548 | skel_659159e2769f3db5 |       0.825996 |        1        | False       | True                | selected_rank_label_diagnostic |

## Decision Counts

| decision                          | label_family                       |   count |
|:----------------------------------|:-----------------------------------|--------:|
| A7FF42_NUMERIC_CLUE               | L0_raw_forward_return              |      64 |
| A7FF42_NUMERIC_CLUE               | L1_cross_sectional_relative_return |      62 |
| A7FF42_NUMERIC_CLUE               | L3_liquidity_tier_relative_return  |      76 |
| A7FF42_NUMERIC_CLUE               | L5_vol_adjusted_return             |      50 |
| A7FF42_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |     238 |
| HOLD_A7FF42_CONTROL_DOMINATED     | L0_raw_forward_return              |     373 |
| HOLD_A7FF42_CONTROL_DOMINATED     | L1_cross_sectional_relative_return |     370 |
| HOLD_A7FF42_CONTROL_DOMINATED     | L3_liquidity_tier_relative_return  |     371 |
| HOLD_A7FF42_CONTROL_DOMINATED     | L5_vol_adjusted_return             |     415 |
| HOLD_A7FF42_CONTROL_DOMINATED     | L7_ranked_future_return            |     491 |
| HOLD_A7FF42_COST2_PROXY_FRAGILE   | L0_raw_forward_return              |       4 |
| HOLD_A7FF42_COST2_PROXY_FRAGILE   | L1_cross_sectional_relative_return |       5 |
| HOLD_A7FF42_COST2_PROXY_FRAGILE   | L3_liquidity_tier_relative_return  |       4 |
| HOLD_A7FF42_ONE_BAR_LAG_FRAGILE   | L0_raw_forward_return              |      18 |
| HOLD_A7FF42_ONE_BAR_LAG_FRAGILE   | L1_cross_sectional_relative_return |      22 |
| HOLD_A7FF42_ONE_BAR_LAG_FRAGILE   | L3_liquidity_tier_relative_return  |      25 |
| HOLD_A7FF42_ONE_BAR_LAG_FRAGILE   | L5_vol_adjusted_return             |      61 |
| HOLD_A7FF42_ONE_BAR_LAG_FRAGILE   | L7_ranked_future_return            |     102 |
| HOLD_A7FF42_PRE_MAY_UNSTABLE      | L0_raw_forward_return              |     873 |
| HOLD_A7FF42_PRE_MAY_UNSTABLE      | L1_cross_sectional_relative_return |     873 |
| HOLD_A7FF42_PRE_MAY_UNSTABLE      | L3_liquidity_tier_relative_return  |     856 |
| HOLD_A7FF42_PRE_MAY_UNSTABLE      | L5_vol_adjusted_return             |     806 |
| HOLD_A7FF42_PRE_MAY_UNSTABLE      | L7_ranked_future_return            |     501 |

## Family Summary

| semantic_pair                         | decision                          |   count |
|:--------------------------------------|:----------------------------------|--------:|
| basis_premium_like|basis_premium_like | A7FF42_NUMERIC_CLUE               |      72 |
| basis_premium_like|basis_premium_like | A7FF42_RANK_LABEL_DIAGNOSTIC_CLUE |      13 |
| basis_premium_like|basis_premium_like | HOLD_A7FF42_CONTROL_DOMINATED     |      61 |
| basis_premium_like|basis_premium_like | HOLD_A7FF42_ONE_BAR_LAG_FRAGILE   |      82 |
| basis_premium_like|basis_premium_like | HOLD_A7FF42_PRE_MAY_UNSTABLE      |     712 |
| funding_like|basis_premium_like       | A7FF42_NUMERIC_CLUE               |     123 |
| funding_like|basis_premium_like       | A7FF42_RANK_LABEL_DIAGNOSTIC_CLUE |     103 |
| funding_like|basis_premium_like       | HOLD_A7FF42_CONTROL_DOMINATED     |     847 |
| funding_like|basis_premium_like       | HOLD_A7FF42_COST2_PROXY_FRAGILE   |      13 |
| funding_like|basis_premium_like       | HOLD_A7FF42_ONE_BAR_LAG_FRAGILE   |     107 |
| funding_like|basis_premium_like       | HOLD_A7FF42_PRE_MAY_UNSTABLE      |    2607 |
| regime_state|price_return_like        | A7FF42_NUMERIC_CLUE               |      57 |
| regime_state|price_return_like        | A7FF42_RANK_LABEL_DIAGNOSTIC_CLUE |     122 |
| regime_state|price_return_like        | HOLD_A7FF42_CONTROL_DOMINATED     |    1112 |
| regime_state|price_return_like        | HOLD_A7FF42_ONE_BAR_LAG_FRAGILE   |      39 |
| regime_state|price_return_like        | HOLD_A7FF42_PRE_MAY_UNSTABLE      |     590 |

## Next Actions

| route                              | status              | reason                                                                      |
|:-----------------------------------|:--------------------|:----------------------------------------------------------------------------|
| A7FF-43_deep_forensic              | not_authorized      | requires selected control-strict non-L7 evidence across at least 2 families |
| A7FF-R8_selector_objective_rewrite | recommended_if_hold | family-balanced input still cannot produce selected multifamily evidence    |
| formula_search                     | blocked             | A7FF-42 is numeric only and never authorizes search                         |

## Boundary

```text
numeric probe executed: true
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```
