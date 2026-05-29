# CRYPTO A7AA-1 PRIMITIVE FEATURE RESPONSE MAP

Generated: 2026-05-29T05:29:37Z

## Decision

`PASS_A7AA1_PRIMITIVE_RESPONSE_CANDIDATES_FOUND_FORMULA_SEARCH_STILL_HOLD`

A7AA-1 maps primitive field/transform response across label families and horizons. It does not generate formulas, search, train, or authorize proof.

## Manifest

```json
{
  "authorizes_a7aa2_feature_role_classification": true,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7AA1_PRIMITIVE_RESPONSE_CANDIDATES_FOUND_FORMULA_SEARCH_STILL_HOLD",
  "executes_formula_generation": false,
  "executes_primitive_response_map": true,
  "executes_search": false,
  "executes_training": false,
  "feature_count": 24,
  "full_timestamps_before_subset": 21025,
  "generated_at": "2026-05-29T05:29:37Z",
  "label_family_count": 3,
  "label_horizon_count": 3,
  "missing_fields_excluded": [],
  "primitive_response_candidate_count": 11,
  "response_rows": 648,
  "stage": "A7AA-1",
  "symbols_loaded": 96,
  "timestamps": 3481,
  "transform_count": 3,
  "uses_may": false
}
```

## Decision Counts

| decision                           |   count |
|:-----------------------------------|--------:|
| HOLD_A7AA1_PRE_MAY_UNSTABLE        |     416 |
| HOLD_A7AA1_CONTROL_LIKE            |     193 |
| HOLD_A7AA1_LAG_FRAGILE             |      28 |
| A7AA1_PRIMITIVE_RESPONSE_CANDIDATE |      11 |

## Primitive Response Candidates

| field_name           | field_family   | source_family       | feature_class   | transform   | label_family                       |   label_horizon_h |   orientation_from_train |   premay_positive_split_count | premay_all_positive   |   control_ratio_premay_max |   one_bar_lag_recent_oriented | lag_ok   | decision                           |   train_2024_n |   train_2024_mean_spread |   train_2024_tstat |   train_2024_nonoverlap_median_tstat |   train_2024_nonoverlap_min_tstat |   train_2024_positive_rate |   validation_2025H1_n |   validation_2025H1_mean_spread |   validation_2025H1_tstat |   validation_2025H1_nonoverlap_median_tstat |   validation_2025H1_nonoverlap_min_tstat |   validation_2025H1_positive_rate |   test_2025H2_n |   test_2025H2_mean_spread |   test_2025H2_tstat |   test_2025H2_nonoverlap_median_tstat |   test_2025H2_nonoverlap_min_tstat |   test_2025H2_positive_rate |   recent_oos_2026JanApr_n |   recent_oos_2026JanApr_mean_spread |   recent_oos_2026JanApr_tstat |   recent_oos_2026JanApr_nonoverlap_median_tstat |   recent_oos_2026JanApr_nonoverlap_min_tstat |   recent_oos_2026JanApr_positive_rate |   avg_n_obs_recent | error   |
|:---------------------|:---------------|:--------------------|:----------------|:------------|:-----------------------------------|------------------:|-------------------------:|------------------------------:|:----------------------|---------------------------:|------------------------------:|:---------|:-----------------------------------|---------------:|-------------------------:|-------------------:|-------------------------------------:|----------------------------------:|---------------------------:|----------------------:|--------------------------------:|--------------------------:|--------------------------------------------:|-----------------------------------------:|----------------------------------:|----------------:|--------------------------:|--------------------:|--------------------------------------:|-----------------------------------:|----------------------------:|--------------------------:|------------------------------------:|------------------------------:|------------------------------------------------:|---------------------------------------------:|--------------------------------------:|-------------------:|:--------|
| mark_index_basis_bps | basis_premium  | mark_index_premium  | raw_source      | delta_24h   | L0_raw_forward_return              |                 1 |                       -1 |                             3 | True                  |                   0.785786 |                   0.000478731 | True     | A7AA1_PRIMITIVE_RESPONSE_CANDIDATE |            695 |             -0.000382177 |           -2.07024 |                             -2.07024 |                          -2.07024 |                   0.444604 |                   719 |                     -0.00059771 |                  -5.66206 |                                    -5.66206 |                                 -5.66206 |                          0.383866 |             719 |               -0.00114686 |            -7.28676 |                              -7.28676 |                           -7.28676 |                    0.346314 |                       719 |                         -0.00133079 |                      -4.09822 |                                        -4.09822 |                                     -4.09822 |                              0.443672 |            95.8667 |         |
| mark_index_basis_bps | basis_premium  | mark_index_premium  | raw_source      | delta_24h   | L1_cross_sectional_relative_return |                 1 |                       -1 |                             3 | True                  |                   0.785786 |                   0.000478731 | True     | A7AA1_PRIMITIVE_RESPONSE_CANDIDATE |            695 |             -0.000382177 |           -2.07024 |                             -2.07024 |                          -2.07024 |                   0.444604 |                   719 |                     -0.00059771 |                  -5.66206 |                                    -5.66206 |                                 -5.66206 |                          0.383866 |             719 |               -0.00114686 |            -7.28676 |                              -7.28676 |                           -7.28676 |                    0.346314 |                       719 |                         -0.00133079 |                      -4.09822 |                                        -4.09822 |                                     -4.09822 |                              0.443672 |            95.8667 |         |
| premium_close_bps    | basis_premium  | derived_replay_base | derived_rolling | delta_24h   | L7_ranked_future_return            |                 1 |                       -1 |                             3 | True                  |                   0.791438 |                   0.0157945   | True     | A7AA1_PRIMITIVE_RESPONSE_CANDIDATE |            695 |             -0.0172559   |           -2.91861 |                             -2.91861 |                          -2.91861 |                   0.447482 |                   719 |                     -0.0258756  |                  -4.69187 |                                    -4.69187 |                                 -4.69187 |                          0.428373 |             719 |               -0.0324203  |            -6.14436 |                              -6.14436 |                           -6.14436 |                    0.421419 |                       719 |                         -0.0112483  |                      -2.10327 |                                        -2.10327 |                                     -2.10327 |                              0.47427  |            95.8667 |         |
| trade_return_1h      | price_return   | derived_replay_base | derived_rolling | level       | L7_ranked_future_return            |                 1 |                       -1 |                             3 | True                  |                   0.254317 |                   0.0216275   | True     | A7AA1_PRIMITIVE_RESPONSE_CANDIDATE |            719 |             -0.0726951   |           -9.42436 |                             -9.42436 |                          -9.42436 |                   0.358832 |                   719 |                     -0.0413886  |                  -5.82858 |                                    -5.82858 |                                 -5.82858 |                          0.381085 |             719 |               -0.0615909  |            -9.3133  |                              -9.3133  |                           -9.3133  |                    0.344924 |                       719 |                         -0.0708109  |                     -10.6033  |                                       -10.6033  |                                    -10.6033  |                              0.333797 |            95.8667 |         |
| trade_return_1h      | price_return   | derived_replay_base | derived_rolling | cs_rank     | L7_ranked_future_return            |                 1 |                       -1 |                             3 | True                  |                   0.254317 |                   0.0216275   | True     | A7AA1_PRIMITIVE_RESPONSE_CANDIDATE |            719 |             -0.0726951   |           -9.42436 |                             -9.42436 |                          -9.42436 |                   0.358832 |                   719 |                     -0.0413886  |                  -5.82858 |                                    -5.82858 |                                 -5.82858 |                          0.381085 |             719 |               -0.0615909  |            -9.3133  |                              -9.3133  |                           -9.3133  |                    0.344924 |                       719 |                         -0.0708109  |                     -10.6033  |                                       -10.6033  |                                    -10.6033  |                              0.333797 |            95.8667 |         |
| trade_return_1h      | price_return   | derived_replay_base | derived_rolling | level       | L7_ranked_future_return            |                 4 |                       -1 |                             3 | True                  |                   0.267545 |                   0.0208287   | True     | A7AA1_PRIMITIVE_RESPONSE_CANDIDATE |            716 |             -0.0639458   |           -8.253   |                             -4.03131 |                          -5.92657 |                   0.386872 |                   716 |                     -0.0496189  |                  -6.95252 |                                    -3.49625 |                                 -4.02451 |                          0.400838 |             716 |               -0.0584543  |            -8.91628 |                              -4.2745  |                           -5.69718 |                    0.384078 |                       716 |                         -0.054937   |                      -8.35652 |                                        -4.50086 |                                     -4.94291 |                              0.385475 |            95.4667 |         |
| trade_return_1h      | price_return   | derived_replay_base | derived_rolling | cs_rank     | L7_ranked_future_return            |                 4 |                       -1 |                             3 | True                  |                   0.267545 |                   0.0208287   | True     | A7AA1_PRIMITIVE_RESPONSE_CANDIDATE |            716 |             -0.0639458   |           -8.253   |                             -4.03131 |                          -5.92657 |                   0.386872 |                   716 |                     -0.0496189  |                  -6.95252 |                                    -3.49625 |                                 -4.02451 |                          0.400838 |             716 |               -0.0584543  |            -8.91628 |                              -4.2745  |                           -5.69718 |                    0.384078 |                       716 |                         -0.054937   |                      -8.35652 |                                        -4.50086 |                                     -4.94291 |                              0.385475 |            95.4667 |         |
| realized_vol_168h    | volatility     | trade_ohlcv         | derived_rolling | level       | L7_ranked_future_return            |                 1 |                       -1 |                             3 | True                  |                   0.879498 |                   0.0347142   | True     | A7AA1_PRIMITIVE_RESPONSE_CANDIDATE |            719 |             -0.0361797   |           -3.86379 |                             -3.86379 |                          -3.86379 |                   0.429764 |                   719 |                     -0.0245258  |                  -2.58608 |                                    -2.58608 |                                 -2.58608 |                          0.449235 |             719 |               -0.0289143  |            -4.08761 |                              -4.08761 |                           -4.08761 |                    0.425591 |                       719 |                         -0.0361537  |                      -4.95528 |                                        -4.95528 |                                     -4.95528 |                              0.417246 |            95.8667 |         |
| realized_vol_168h    | volatility     | trade_ohlcv         | derived_rolling | cs_rank     | L7_ranked_future_return            |                 1 |                       -1 |                             3 | True                  |                   0.879498 |                   0.0347142   | True     | A7AA1_PRIMITIVE_RESPONSE_CANDIDATE |            719 |             -0.0361797   |           -3.86379 |                             -3.86379 |                          -3.86379 |                   0.429764 |                   719 |                     -0.0245258  |                  -2.58608 |                                    -2.58608 |                                 -2.58608 |                          0.449235 |             719 |               -0.0289143  |            -4.08761 |                              -4.08761 |                           -4.08761 |                    0.425591 |                       719 |                         -0.0361537  |                      -4.95528 |                                        -4.95528 |                                     -4.95528 |                              0.417246 |            95.8667 |         |
| realized_vol_24h     | volatility     | trade_ohlcv         | derived_rolling | level       | L7_ranked_future_return            |                 1 |                       -1 |                             3 | True                  |                   0.939508 |                   0.0310904   | True     | A7AA1_PRIMITIVE_RESPONSE_CANDIDATE |            719 |             -0.0424399   |           -4.49541 |                             -4.49541 |                          -4.49541 |                   0.418637 |                   719 |                     -0.0204831  |                  -2.20909 |                                    -2.20909 |                                 -2.20909 |                          0.450626 |             719 |               -0.0265494  |            -3.47539 |                              -3.47539 |                           -3.47539 |                    0.429764 |                       719 |                         -0.0345867  |                      -4.75172 |                                        -4.75172 |                                     -4.75172 |                              0.438108 |            95.8667 |         |
| realized_vol_24h     | volatility     | trade_ohlcv         | derived_rolling | cs_rank     | L7_ranked_future_return            |                 1 |                       -1 |                             3 | True                  |                   0.939508 |                   0.0310904   | True     | A7AA1_PRIMITIVE_RESPONSE_CANDIDATE |            719 |             -0.0424399   |           -4.49541 |                             -4.49541 |                          -4.49541 |                   0.418637 |                   719 |                     -0.0204831  |                  -2.20909 |                                    -2.20909 |                                 -2.20909 |                          0.450626 |             719 |               -0.0265494  |            -3.47539 |                              -3.47539 |                           -3.47539 |                    0.429764 |                       719 |                         -0.0345867  |                      -4.75172 |                                        -4.75172 |                                     -4.75172 |                              0.438108 |            95.8667 |         |

## Family / Label Summary

| field_family              | label_family                       |   label_horizon_h |   combos |   candidate_count |   pre_may_stable_count |   median_control_ratio |
|:--------------------------|:-----------------------------------|------------------:|---------:|------------------:|-----------------------:|-----------------------:|
| volatility                | L7_ranked_future_return            |                 1 |        6 |                 4 |                      6 |               0.939508 |
| price_return              | L7_ranked_future_return            |                 4 |        6 |                 2 |                      6 |               4.48066  |
| price_return              | L7_ranked_future_return            |                 1 |        6 |                 2 |                      6 |               3.7822   |
| basis_premium             | L1_cross_sectional_relative_return |                 1 |       15 |                 1 |                      9 |               1.80571  |
| basis_premium             | L0_raw_forward_return              |                 1 |       15 |                 1 |                      9 |               1.80571  |
| basis_premium             | L7_ranked_future_return            |                 1 |       15 |                 1 |                     13 |               0.950724 |
| basis_premium             | L1_cross_sectional_relative_return |                 4 |       15 |                 0 |                      6 |               2.66789  |
| basis_premium             | L0_raw_forward_return              |                24 |       15 |                 0 |                      2 |              15.3728   |
| basis_premium             | L0_raw_forward_return              |                 4 |       15 |                 0 |                      6 |               2.66789  |
| funding                   | L0_raw_forward_return              |                 1 |        9 |                 0 |                      0 |              49.7434   |
| funding                   | L0_raw_forward_return              |                 4 |        9 |                 0 |                      0 |              12.3662   |
| funding                   | L0_raw_forward_return              |                24 |        9 |                 0 |                      0 |               3.11786  |
| funding                   | L1_cross_sectional_relative_return |                 1 |        9 |                 0 |                      0 |              49.7434   |
| funding                   | L1_cross_sectional_relative_return |                 4 |        9 |                 0 |                      0 |              12.3662   |
| basis_premium             | L1_cross_sectional_relative_return |                24 |       15 |                 0 |                      2 |              15.3728   |
| basis_premium             | L7_ranked_future_return            |                 4 |       15 |                 0 |                      7 |               2.28817  |
| basis_premium             | L7_ranked_future_return            |                24 |       15 |                 0 |                      4 |               2.76686  |
| funding                   | L7_ranked_future_return            |                 4 |        9 |                 0 |                      0 |               0.878273 |
| funding                   | L7_ranked_future_return            |                 1 |        9 |                 0 |                      0 |               2.29103  |
| funding                   | L1_cross_sectional_relative_return |                24 |        9 |                 0 |                      0 |               3.11786  |
| funding                   | L7_ranked_future_return            |                24 |        9 |                 0 |                      1 |               1.07473  |
| liquidity                 | L1_cross_sectional_relative_return |                 1 |        9 |                 0 |                      1 |              10.6951   |
| liquidity                 | L0_raw_forward_return              |                 1 |        9 |                 0 |                      1 |              10.6951   |
| liquidity                 | L0_raw_forward_return              |                 4 |        9 |                 0 |                      0 |               9.8463   |
| liquidity                 | L0_raw_forward_return              |                24 |        9 |                 0 |                      0 |              21.3078   |
| liquidity                 | L7_ranked_future_return            |                 4 |        9 |                 0 |                      3 |               3.90805  |
| liquidity                 | L7_ranked_future_return            |                24 |        9 |                 0 |                      2 |               8.20488  |
| open_interest             | L0_raw_forward_return              |                 1 |        9 |                 0 |                      1 |              20.8864   |
| open_interest             | L0_raw_forward_return              |                 4 |        9 |                 0 |                      3 |              15.6281   |
| open_interest             | L0_raw_forward_return              |                24 |        9 |                 0 |                      3 |               8.5007   |
| liquidity                 | L1_cross_sectional_relative_return |                 4 |        9 |                 0 |                      0 |               9.8463   |
| liquidity                 | L1_cross_sectional_relative_return |                24 |        9 |                 0 |                      0 |              21.3078   |
| liquidity                 | L7_ranked_future_return            |                 1 |        9 |                 0 |                      2 |               5.19194  |
| open_interest             | L7_ranked_future_return            |                 1 |        9 |                 0 |                      4 |               8.99362  |
| open_interest             | L7_ranked_future_return            |                 4 |        9 |                 0 |                      6 |               9.90159  |
| open_interest             | L7_ranked_future_return            |                24 |        9 |                 0 |                      6 |               7.63567  |
| open_interest_interaction | L0_raw_forward_return              |                 1 |        3 |                 0 |                      0 |               6.78564  |
| open_interest_interaction | L0_raw_forward_return              |                 4 |        3 |                 0 |                      0 |              17.6323   |
| open_interest_interaction | L0_raw_forward_return              |                24 |        3 |                 0 |                      0 |              63.3344   |
| open_interest_interaction | L1_cross_sectional_relative_return |                 1 |        3 |                 0 |                      0 |               6.78564  |
| open_interest_interaction | L1_cross_sectional_relative_return |                 4 |        3 |                 0 |                      0 |              17.6323   |
| open_interest_interaction | L1_cross_sectional_relative_return |                24 |        3 |                 0 |                      0 |              63.3344   |
| open_interest_interaction | L7_ranked_future_return            |                 1 |        3 |                 0 |                      3 |               3.05966  |
| open_interest_interaction | L7_ranked_future_return            |                 4 |        3 |                 0 |                      3 |               1.79112  |
| open_interest_interaction | L7_ranked_future_return            |                24 |        3 |                 0 |                      3 |               3.52762  |
| positioning               | L0_raw_forward_return              |                 1 |        9 |                 0 |                      1 |               7.54007  |
| open_interest             | L1_cross_sectional_relative_return |                 1 |        9 |                 0 |                      1 |              20.8864   |
| open_interest             | L1_cross_sectional_relative_return |                 4 |        9 |                 0 |                      3 |              15.6281   |
| open_interest             | L1_cross_sectional_relative_return |                24 |        9 |                 0 |                      3 |               8.5007   |
| positioning               | L1_cross_sectional_relative_return |                 1 |        9 |                 0 |                      1 |               7.54007  |
| positioning               | L0_raw_forward_return              |                24 |        9 |                 0 |                      2 |              10.3646   |
| positioning               | L0_raw_forward_return              |                 4 |        9 |                 0 |                      3 |               6.08279  |
| positioning               | L1_cross_sectional_relative_return |                 4 |        9 |                 0 |                      3 |               6.08279  |
| positioning               | L7_ranked_future_return            |                24 |        9 |                 0 |                      0 |               5.59093  |
| price_return              | L0_raw_forward_return              |                 1 |        6 |                 0 |                      5 |              32.0334   |
| positioning               | L7_ranked_future_return            |                 1 |        9 |                 0 |                      6 |               3.76301  |
| positioning               | L1_cross_sectional_relative_return |                24 |        9 |                 0 |                      2 |              10.3646   |
| price_return              | L0_raw_forward_return              |                24 |        6 |                 0 |                      3 |             989.337    |
| price_return              | L0_raw_forward_return              |                 4 |        6 |                 0 |                      3 |              26.2457   |
| price_return              | L1_cross_sectional_relative_return |                 4 |        6 |                 0 |                      3 |              26.2457   |
| price_return              | L1_cross_sectional_relative_return |                 1 |        6 |                 0 |                      5 |              32.0334   |
| price_return              | L1_cross_sectional_relative_return |                24 |        6 |                 0 |                      3 |             989.337    |
| price_return              | L7_ranked_future_return            |                24 |        6 |                 0 |                      6 |              12.9545   |
| taker_flow                | L0_raw_forward_return              |                 1 |        6 |                 0 |                      5 |              11.4335   |
| positioning               | L7_ranked_future_return            |                 4 |        9 |                 0 |                      6 |               4.71899  |
| taker_flow                | L0_raw_forward_return              |                 4 |        6 |                 0 |                      0 |               7.00042  |
| taker_flow                | L0_raw_forward_return              |                24 |        6 |                 0 |                      2 |              22.5022   |
| taker_flow                | L1_cross_sectional_relative_return |                 4 |        6 |                 0 |                      0 |               7.00042  |
| taker_flow                | L1_cross_sectional_relative_return |                 1 |        6 |                 0 |                      5 |              11.4335   |
| taker_flow                | L7_ranked_future_return            |                 1 |        6 |                 0 |                      5 |               1.20593  |
| taker_flow                | L7_ranked_future_return            |                 4 |        6 |                 0 |                      3 |               2.37309  |
| taker_flow                | L7_ranked_future_return            |                24 |        6 |                 0 |                      0 |              52.8683   |
| taker_flow                | L1_cross_sectional_relative_return |                24 |        6 |                 0 |                      2 |              22.5022   |
| volatility                | L0_raw_forward_return              |                 1 |        6 |                 0 |                      4 |              20.7099   |
| volatility                | L0_raw_forward_return              |                 4 |        6 |                 0 |                      2 |              14.3634   |
| volatility                | L1_cross_sectional_relative_return |                 1 |        6 |                 0 |                      4 |              20.7099   |
| volatility                | L0_raw_forward_return              |                24 |        6 |                 0 |                      5 |               6.67139  |
| volatility                | L1_cross_sectional_relative_return |                 4 |        6 |                 0 |                      2 |              14.3634   |
| volatility                | L1_cross_sectional_relative_return |                24 |        6 |                 0 |                      5 |               6.67139  |
| volatility                | L7_ranked_future_return            |                 4 |        6 |                 0 |                      6 |               1.53191  |
| volatility                | L7_ranked_future_return            |                24 |        6 |                 0 |                      5 |               1.40169  |

## Boundary

```text
Formula search remains not authorized.
This stage only identifies primitive response candidates and feature roles.
```
