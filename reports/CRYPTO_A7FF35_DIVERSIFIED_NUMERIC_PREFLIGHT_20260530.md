# CRYPTO A7FF-35 DIVERSIFIED NUMERIC PREFLIGHT

Generated: 2026-05-30T11:26:28Z

## Decision

`PASS_A7FF35_DIVERSIFIED_NUMERIC_PREFLIGHT_COMPLETED_NO_SEARCH_AUTH`

A7FF-35 samples the A7FF-33 family-diversified queue and runs the existing numeric probe adapter. It is a bounded numeric preflight only: no replay, no search, no alpha proof, no shadow/paper/live.

## Manifest

```json
{
  "activity_ok_count": 110,
  "authorizes_a7ff36_forensic_or_repair": true,
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "control_rows": 46200,
  "decision": "PASS_A7FF35_DIVERSIFIED_NUMERIC_PREFLIGHT_COMPLETED_NO_SEARCH_AUTH",
  "eval_failure_count": 0,
  "eval_success_count": 140,
  "executes_numeric_probe": true,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T11:26:28Z",
  "label_response_rows": 2200,
  "non_l7_numeric_clue_rows": 40,
  "numeric_probe_decision": "PASS_A7FF35_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH",
  "process_exit_code": 0,
  "rank_label_diagnostic_clue_rows": 39,
  "sample_family_count": 7,
  "sample_motif_count": 10,
  "sample_rows": 140,
  "selected_portfolio_queue_count": 9,
  "source_a7ff34_decision": "PASS_A7FF34_FAMILY_QUEUE_COVERAGE_ACCEPTABLE_READY_FOR_A7FF35_NUMERIC_PREFLIGHT_NO_SEARCH_AUTH",
  "stage": "A7FF-35",
  "started_at": "2026-05-30T11:17:00Z",
  "timed_out": false,
  "timeout_seconds": 2400,
  "uses_may": false
}
```

## Sample Coverage

| family_id                     | motif               |   sample_count |
|:------------------------------|:--------------------|---------------:|
| D0_basis_premium_reference    | gated_sign          |              2 |
| D0_basis_premium_reference    | mean_reversion_gate |              2 |
| D0_basis_premium_reference    | mul                 |              2 |
| D0_basis_premium_reference    | relative_shock      |              2 |
| D0_basis_premium_reference    | safe_div_clip       |              2 |
| D0_basis_premium_reference    | signed_spread       |              2 |
| D0_basis_premium_reference    | smooth_mul          |              2 |
| D0_basis_premium_reference    | spread_rank         |              2 |
| D0_basis_premium_reference    | sub                 |              2 |
| D0_basis_premium_reference    | zspread             |              2 |
| D1_open_interest_positioning  | gated_sign          |              2 |
| D1_open_interest_positioning  | mean_reversion_gate |              2 |
| D1_open_interest_positioning  | mul                 |              2 |
| D1_open_interest_positioning  | relative_shock      |              2 |
| D1_open_interest_positioning  | safe_div_clip       |              2 |
| D1_open_interest_positioning  | signed_spread       |              2 |
| D1_open_interest_positioning  | smooth_mul          |              2 |
| D1_open_interest_positioning  | spread_rank         |              2 |
| D1_open_interest_positioning  | sub                 |              2 |
| D1_open_interest_positioning  | zspread             |              2 |
| D2_taker_flow_leverage        | gated_sign          |              2 |
| D2_taker_flow_leverage        | mean_reversion_gate |              2 |
| D2_taker_flow_leverage        | mul                 |              2 |
| D2_taker_flow_leverage        | relative_shock      |              2 |
| D2_taker_flow_leverage        | safe_div_clip       |              2 |
| D2_taker_flow_leverage        | signed_spread       |              2 |
| D2_taker_flow_leverage        | smooth_mul          |              2 |
| D2_taker_flow_leverage        | spread_rank         |              2 |
| D2_taker_flow_leverage        | sub                 |              2 |
| D2_taker_flow_leverage        | zspread             |              2 |
| D3_liquidity_volatility_state | gated_sign          |              2 |
| D3_liquidity_volatility_state | mean_reversion_gate |              2 |
| D3_liquidity_volatility_state | mul                 |              2 |
| D3_liquidity_volatility_state | relative_shock      |              2 |
| D3_liquidity_volatility_state | safe_div_clip       |              2 |
| D3_liquidity_volatility_state | signed_spread       |              2 |
| D3_liquidity_volatility_state | smooth_mul          |              2 |
| D3_liquidity_volatility_state | spread_rank         |              2 |
| D3_liquidity_volatility_state | sub                 |              2 |
| D3_liquidity_volatility_state | zspread             |              2 |
| D4_regime_relative_value      | gated_sign          |              2 |
| D4_regime_relative_value      | mean_reversion_gate |              2 |
| D4_regime_relative_value      | mul                 |              2 |
| D4_regime_relative_value      | relative_shock      |              2 |
| D4_regime_relative_value      | safe_div_clip       |              2 |
| D4_regime_relative_value      | signed_spread       |              2 |
| D4_regime_relative_value      | smooth_mul          |              2 |
| D4_regime_relative_value      | spread_rank         |              2 |
| D4_regime_relative_value      | sub                 |              2 |
| D4_regime_relative_value      | zspread             |              2 |
| D5_funding_dense_state        | gated_sign          |              2 |
| D5_funding_dense_state        | mean_reversion_gate |              2 |
| D5_funding_dense_state        | mul                 |              2 |
| D5_funding_dense_state        | relative_shock      |              2 |
| D5_funding_dense_state        | safe_div_clip       |              2 |
| D5_funding_dense_state        | signed_spread       |              2 |
| D5_funding_dense_state        | smooth_mul          |              2 |
| D5_funding_dense_state        | spread_rank         |              2 |
| D5_funding_dense_state        | sub                 |              2 |
| D5_funding_dense_state        | zspread             |              2 |
| D6_listing_latent_lifecycle   | gated_sign          |              2 |
| D6_listing_latent_lifecycle   | mean_reversion_gate |              2 |
| D6_listing_latent_lifecycle   | mul                 |              2 |
| D6_listing_latent_lifecycle   | relative_shock      |              2 |
| D6_listing_latent_lifecycle   | safe_div_clip       |              2 |
| D6_listing_latent_lifecycle   | signed_spread       |              2 |
| D6_listing_latent_lifecycle   | smooth_mul          |              2 |
| D6_listing_latent_lifecycle   | spread_rank         |              2 |
| D6_listing_latent_lifecycle   | sub                 |              2 |
| D6_listing_latent_lifecycle   | zspread             |              2 |

## Family Materialization Summary

| family_id                     | root_family                           |   rows |   eval_success |   activity_ok |   finite_share_median |   nonzero_share_median |
|:------------------------------|:--------------------------------------|-------:|---------------:|--------------:|----------------------:|-----------------------:|
| D0_basis_premium_reference    | basis_premium_like|basis_premium_like |     20 |             20 |            16 |              0.999425 |               0.98741  |
| D1_open_interest_positioning  | open_interest_like|positioning_like   |     20 |             20 |            20 |              0.999713 |               0.999979 |
| D2_taker_flow_leverage        | taker_flow_like|open_interest_like    |     20 |             20 |            20 |              0.999713 |               0.999798 |
| D3_liquidity_volatility_state | liquidity_like|volatility_like        |     20 |             20 |            20 |              0.827061 |               1        |
| D4_regime_relative_value      | regime_state|price_return_like        |     20 |             20 |            14 |              0.826774 |               0.993717 |
| D5_funding_dense_state        | funding_like|basis_premium_like       |     20 |             20 |            20 |              0.82772  |               0.992155 |
| D6_listing_latent_lifecycle   | listing_age_like|latent_state         |     20 |             20 |             0 |              0        |               0        |

## Selected Portfolio Queue

| blueprint_id            | expression                                                                                              | semantic_pair                         | motif         | label_family            |   label_horizon_h |   orientation_from_train |   premay_positive_split_count | premay_all_positive   |   control_ratio_premay_max |   one_bar_lag_recent_oriented | lag_ok   |   robust_median_tstat_floor |   robust_min_tstat_floor | robust_ok   |   cost2_recent_oriented |   cost5_recent_oriented |   cost10_recent_oriented |   avg_n_obs_recent | decision                          |   train_2024_n |   train_2024_mean_spread |   train_2024_tstat |   train_2024_nonoverlap_median_tstat |   train_2024_nonoverlap_min_tstat |   train_2024_positive_rate |   validation_2025H1_n |   validation_2025H1_mean_spread |   validation_2025H1_tstat |   validation_2025H1_nonoverlap_median_tstat |   validation_2025H1_nonoverlap_min_tstat |   validation_2025H1_positive_rate |   test_2025H2_n |   test_2025H2_mean_spread |   test_2025H2_tstat |   test_2025H2_nonoverlap_median_tstat |   test_2025H2_nonoverlap_min_tstat |   test_2025H2_positive_rate |   recent_oos_2026JanApr_n |   recent_oos_2026JanApr_mean_spread |   recent_oos_2026JanApr_tstat |   recent_oos_2026JanApr_nonoverlap_median_tstat |   recent_oos_2026JanApr_nonoverlap_min_tstat |   recent_oos_2026JanApr_positive_rate |   non_l7_bonus |   score_no_may | skeleton_key          |   finite_share |   nonzero_share |
|:------------------------|:--------------------------------------------------------------------------------------------------------|:--------------------------------------|:--------------|:------------------------|------------------:|-------------------------:|------------------------------:|:----------------------|---------------------------:|------------------------------:|:---------|----------------------------:|-------------------------:|:------------|------------------------:|------------------------:|-------------------------:|-------------------:|:----------------------------------|---------------:|-------------------------:|-------------------:|-------------------------------------:|----------------------------------:|---------------------------:|----------------------:|--------------------------------:|--------------------------:|--------------------------------------------:|-----------------------------------------:|----------------------------------:|----------------:|--------------------------:|--------------------:|--------------------------------------:|-----------------------------------:|----------------------------:|--------------------------:|------------------------------------:|------------------------------:|------------------------------------------------:|---------------------------------------------:|--------------------------------------:|---------------:|---------------:|:----------------------|---------------:|----------------:|
| a7ff33_c8b780256ff30837 | Sub(funding_rate_state_last_ffill_8h,Delta(mark_index_basis_bps,1))                                     | funding_like|basis_premium_like       | sub           | L5_vol_adjusted_return  |                 8 |                        1 |                             3 | True                  |                   0.548552 |                     0.0878674 | True     |                    0.624079 |               -0.295747  | True        |               0.174563  |               0.173963  |                0.172963  |            94.9333 | A7FF35_NUMERIC_CLUE               |            711 |                0.0398373 |            1.47901 |                             0.445761 |                         0.0569356 |                   0.513361 |                   712 |                       0.0925015 |                  3.06433  |                                    1.14822  |                                -0.106646 |                          0.567416 |             712 |                 0.0907614 |             2.32253 |                              0.624079 |                          -0.295747 |                    0.566011 |                       712 |                           0.174963  |                       2.87696 |                                        1.30019  |                                   -0.229888  |                              0.542135 |              1 |       180.414  | skel_f8484b844efd270f |       0.82772  |        0.999993 |
| a7ff33_0c0da14842542e13 | Sub(ZScore(funding_rate_state_last_ffill_8h),ZScore(mark_index_basis_bps))                              | funding_like|basis_premium_like       | zspread       | L5_vol_adjusted_return  |                 1 |                        1 |                             3 | True                  |                   0.261017 |                     0.0342378 | True     |                    5.48711  |                5.48711   | True        |               0.123516  |               0.122916  |                0.121916  |            95.8667 | A7FF35_NUMERIC_CLUE               |            719 |                0.0168323 |            1.55056 |                             1.55056  |                         1.55056   |                   0.515994 |                   719 |                       0.0588513 |                  5.48711  |                                    5.48711  |                                 5.48711  |                          0.606398 |             719 |                 0.114742  |             7.88518 |                              7.88518  |                           7.88518  |                    0.64395  |                       719 |                           0.123916  |                       5.84124 |                                        5.84124  |                                    5.84124   |                              0.599444 |              1 |       129.655  | skel_293cae94cfd91548 |       0.828007 |        1        |
| a7ff33_fe3e0c6a7b32a1d7 | Sub(CSRank(rolling_coverage_168h),CSRank(Delta(trade_return_1h,1)))                                     | regime_state|price_return_like        | spread_rank   | L5_vol_adjusted_return  |                 4 |                        1 |                             3 | True                  |                   0.852468 |                     0.0845602 | True     |                    0.294993 |                0.0283068 | True        |               0.0978618 |               0.0972618 |                0.0962618 |            95.4667 | A7FF35_NUMERIC_CLUE               |            715 |                0.0480605 |            1.80386 |                             1.34206  |                        -1.20694   |                   0.535664 |                   716 |                       0.0249224 |                  0.942533 |                                    0.294993 |                                 0.212595 |                          0.534916 |             716 |                 0.0612191 |             1.83018 |                              0.93161  |                           0.310265 |                    0.565642 |                       716 |                           0.0982618 |                       1.88219 |                                        0.934575 |                                    0.0283068 |                              0.540503 |              1 |       103.409  | skel_1a1b3fb29dff7328 |       0.827061 |        0.999928 |
| a7ff33_8f587010df0608c7 | Sub(rolling_coverage_168h,trade_return_1h)                                                              | regime_state|price_return_like        | sub           | L7_ranked_future_return |                 1 |                        1 |                             3 | True                  |                   0.235941 |                     0.023036  | True     |                    6.23942  |                6.23942   | True        |               0.0724315 |               0.0718315 |                0.0708315 |            95.8667 | A7FF35_RANK_LABEL_DIAGNOSTIC_CLUE |            719 |                0.0742998 |            9.6597  |                             9.6597   |                         9.6597    |                   0.632823 |                   719 |                       0.0447364 |                  6.23942  |                                    6.23942  |                                 6.23942  |                          0.620306 |             719 |                 0.0634821 |             9.62007 |                              9.62007  |                           9.62007  |                    0.670376 |                       719 |                           0.0728315 |                      10.8065  |                                       10.8065   |                                   10.8065    |                              0.666203 |              0 |        77.5956 | skel_337820bc5afcf6cc |       0.827348 |        1        |
| a7ff33_dcdd07a710d41c9f | Clip(SafeDiv(mark_index_basis_bps,Abs(Delta(mark_index_basis_bps,1))),-5,5)                             | basis_premium_like|basis_premium_like | safe_div_clip | L5_vol_adjusted_return  |                 1 |                       -1 |                             3 | True                  |                   0.366579 |                     0.0277235 | True     |                    3.27293  |                3.27293   | True        |               0.0714899 |               0.0708899 |                0.0698899 |            95.6417 | A7FF35_NUMERIC_CLUE               |            490 |               -0.0125342 |           -1.3388  |                            -1.3388   |                        -1.3388    |                   0.461224 |                   401 |                      -0.0599513 |                 -4.89388  |                                   -4.89388  |                                -4.89388  |                          0.369077 |             385 |                -0.0758867 |            -4.78919 |                             -4.78919  |                          -4.78919  |                    0.384416 |                       415 |                          -0.0718899 |                      -3.27293 |                                       -3.27293  |                                   -3.27293   |                              0.426506 |              1 |        77.5233 | skel_6badd2926fa2941d |       0.997974 |        0.988732 |
| a7ff33_eccdfecdad4a4b5d | Mul(Sub(CSRank(rolling_coverage_168h),CSRank(trade_return_1h)),Sign(trade_return_1h))                   | regime_state|price_return_like        | signed_spread | L7_ranked_future_return |                 8 |                        1 |                             3 | True                  |                   0.754188 |                     0.0551701 | True     |                    1.5268   |                0.742179  | True        |               0.0563636 |               0.0557636 |                0.0547636 |            94.9333 | A7FF35_RANK_LABEL_DIAGNOSTIC_CLUE |            712 |                0.047357  |            7.17586 |                             2.47106  |                         1.03872   |                   0.615169 |                   712 |                       0.029498  |                  4.34841  |                                    1.5268   |                                 0.742179 |                          0.55618  |             712 |                 0.0432641 |             7.12803 |                              2.3659   |                           2.0354   |                    0.599719 |                       712 |                           0.0567636 |                       8.95929 |                                        3.10533  |                                    2.42789   |                              0.641854 |              0 |        61.0094 | skel_e001e287e8d9140a |       0.827348 |        0.964146 |
| a7ff33_93a54d44f21957f9 | Mean(Mul(rolling_coverage_168h,trade_return_1h),4)                                                      | regime_state|price_return_like        | smooth_mul    | L7_ranked_future_return |                 4 |                       -1 |                             3 | True                  |                   0.484123 |                     0.0279718 | True     |                    3.205    |                3.92684   | True        |               0.0536623 |               0.0530623 |                0.0520623 |            95.4667 | A7FF35_RANK_LABEL_DIAGNOSTIC_CLUE |            713 |               -0.0673585 |           -8.66875 |                            -3.97716  |                        -6.05439   |                   0.371669 |                   716 |                      -0.0459314 |                 -6.33422  |                                   -3.205    |                                -3.92684  |                          0.402235 |             716 |                -0.0504243 |            -7.29009 |                             -3.52434  |                          -4.67591  |                    0.410615 |                       716 |                          -0.0540623 |                      -7.50716 |                                       -3.83389  |                                   -4.32976   |                              0.395251 |              0 |        58.5782 | skel_356a5f3fab58eb27 |       0.826487 |        0.999312 |
| a7ff33_20f0d2c26a4f61a2 | Mul(Sub(CSRank(rolling_coverage_168h),CSRank(Delta(trade_return_1h,1))),Sign(Delta(trade_return_1h,1))) | regime_state|price_return_like        | signed_spread | L7_ranked_future_return |                 8 |                        1 |                             3 | True                  |                   0.757201 |                     0.0546979 | True     |                    1.06166  |                0.603132  | True        |               0.0519368 |               0.0513368 |                0.0503368 |            94.9333 | A7FF35_RANK_LABEL_DIAGNOSTIC_CLUE |            711 |                0.0474509 |            7.45153 |                             2.72068  |                         0.865473  |                   0.603376 |                   712 |                       0.0218891 |                  3.39846  |                                    1.06166  |                                 0.603132 |                          0.549157 |             712 |                 0.0409105 |             6.78726 |                              2.29241  |                           1.51809  |                    0.581461 |                       712 |                           0.0523368 |                       8.4077  |                                        2.76082  |                                    1.94942   |                              0.602528 |              0 |        56.5796 | skel_ab37051588d52fcc |       0.827061 |        0.994193 |
| a7ff33_31b8b42aa76b1572 | Mean(Mul(rolling_coverage_168h,Delta(trade_return_1h,1)),4)                                             | regime_state|price_return_like        | smooth_mul    | L7_ranked_future_return |                 1 |                       -1 |                             3 | True                  |                   0.341654 |                     0.016946  | True     |                    3.18484  |                3.18484   | True        |               0.04519   |               0.04459   |                0.04359   |            95.8667 | A7FF35_RANK_LABEL_DIAGNOSTIC_CLUE |            715 |               -0.0463369 |           -6.0986  |                            -6.0986   |                        -6.0986    |                   0.415385 |                   719 |                      -0.0221868 |                 -3.18484  |                                   -3.18484  |                                -3.18484  |                          0.447844 |             719 |                -0.0462369 |            -7.0142  |                             -7.0142   |                          -7.0142   |                    0.401947 |                       719 |                          -0.04559   |                      -6.84352 |                                       -6.84352  |                                   -6.84352   |                              0.368567 |              0 |        50.2483 | skel_644ba0ee0d0e38ee |       0.826199 |        0.993241 |

## Boundary

```text
numeric probe executed: true, bounded sample only
replay executed: false
search executed: false
May used: false
```
