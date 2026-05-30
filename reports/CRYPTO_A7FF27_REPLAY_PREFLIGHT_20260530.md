# CRYPTO A7FF-27 EXPANDED NUMERIC PROBE

Generated: 2026-05-30T09:27:25Z

## Decision

`PASS_A7FF27_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH`

A7FF-27 materializes the A7FF-7E selected blueprint queue and evaluates label response, controls, non-overlap statistics, and a dry portfolio marginal proxy. It is not formula search or alpha proof.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FF27_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH",
  "executes_generation": false,
  "executes_numeric_probe": true,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T09:27:25Z",
  "input_blueprint_count": 14,
  "label_response_rows": 280,
  "materialized_activity_ok_count": 14,
  "non_l7_numeric_clue_rows": 49,
  "plan": {
    "control_probe_cap": 256,
    "controls": [
      "wrong_lag_future",
      "wrong_lag_stale",
      "time_shuffle",
      "symbol_shuffle",
      "sign_flip",
      "same_family_placebo"
    ],
    "deep_audit_cap": 64,
    "fast_numeric_probe_cap": 256,
    "horizons": [
      "1h",
      "4h",
      "8h",
      "24h"
    ],
    "input_blueprint_source": "runtime/a7ff7e_expanded_derivation_probe_contract/a7ff7e_expanded_blueprint_pool.csv",
    "labels": [
      "L0_raw_forward_return",
      "L1_cross_sectional_relative_return",
      "L3_liquidity_tier_relative_return",
      "L5_vol_adjusted_return",
      "L7_ranked_future_return_diagnostic_only"
    ],
    "materialize_cap": 384,
    "portfolio_marginal_probe_cap": 128,
    "promotion_blockers": [
      "L7-only cannot promote",
      "control_ratio >= 1.0 blocks",
      "single semantic_pair > 35pct blocks",
      "single skeleton > 15pct blocks",
      "numeric replay required before any search authorization"
    ],
    "required_outputs": [
      "a7ff8_materialization_metrics.csv",
      "a7ff8_label_response_metrics.csv",
      "a7ff8_control_dominance_metrics.csv",
      "a7ff8_nonoverlap_stats.csv",
      "a7ff8_portfolio_marginal_proxy.csv",
      "a7ff8_decision_record.json"
    ],
    "selected_blueprints": 384,
    "stage": "A7FF-8",
    "status": "contract_only_not_executed"
  },
  "portfolio_queue_count": 14,
  "queue_limit": 14,
  "queue_offset": 0,
  "queue_path": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ff26_numeric_clue_forensic\\a7ff26_promotion_candidate_queue.csv",
  "queue_total_rows": 14,
  "rank_label_diagnostic_clue_rows": 14,
  "selected_portfolio_queue_count": 8,
  "stage": "A7FF-27",
  "uses_may": false
}
```

## Decision Counts

| decision                          | label_family                       |   count |
|:----------------------------------|:-----------------------------------|--------:|
| A7FF27_NUMERIC_CLUE               | L0_raw_forward_return              |      10 |
| A7FF27_NUMERIC_CLUE               | L1_cross_sectional_relative_return |      11 |
| A7FF27_NUMERIC_CLUE               | L3_liquidity_tier_relative_return  |       9 |
| A7FF27_NUMERIC_CLUE               | L5_vol_adjusted_return             |      19 |
| A7FF27_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |      14 |
| HOLD_A7FF27_CONTROL_DOMINATED     | L0_raw_forward_return              |      14 |
| HOLD_A7FF27_CONTROL_DOMINATED     | L1_cross_sectional_relative_return |      14 |
| HOLD_A7FF27_CONTROL_DOMINATED     | L3_liquidity_tier_relative_return  |      14 |
| HOLD_A7FF27_CONTROL_DOMINATED     | L5_vol_adjusted_return             |       7 |
| HOLD_A7FF27_CONTROL_DOMINATED     | L7_ranked_future_return            |       9 |
| HOLD_A7FF27_COST2_PROXY_FRAGILE   | L0_raw_forward_return              |       1 |
| HOLD_A7FF27_COST2_PROXY_FRAGILE   | L1_cross_sectional_relative_return |       1 |
| HOLD_A7FF27_COST2_PROXY_FRAGILE   | L3_liquidity_tier_relative_return  |       1 |
| HOLD_A7FF27_ONE_BAR_LAG_FRAGILE   | L0_raw_forward_return              |       2 |
| HOLD_A7FF27_ONE_BAR_LAG_FRAGILE   | L1_cross_sectional_relative_return |       1 |
| HOLD_A7FF27_ONE_BAR_LAG_FRAGILE   | L3_liquidity_tier_relative_return  |       3 |
| HOLD_A7FF27_ONE_BAR_LAG_FRAGILE   | L5_vol_adjusted_return             |       2 |
| HOLD_A7FF27_ONE_BAR_LAG_FRAGILE   | L7_ranked_future_return            |      12 |
| HOLD_A7FF27_PRE_MAY_UNSTABLE      | L0_raw_forward_return              |      29 |
| HOLD_A7FF27_PRE_MAY_UNSTABLE      | L1_cross_sectional_relative_return |      29 |
| HOLD_A7FF27_PRE_MAY_UNSTABLE      | L3_liquidity_tier_relative_return  |      29 |
| HOLD_A7FF27_PRE_MAY_UNSTABLE      | L5_vol_adjusted_return             |      28 |
| HOLD_A7FF27_PRE_MAY_UNSTABLE      | L7_ranked_future_return            |      21 |

## Family Summary

| semantic_pair                         | decision                          |   count |
|:--------------------------------------|:----------------------------------|--------:|
| basis_premium_like                    | A7FF27_NUMERIC_CLUE               |       7 |
| basis_premium_like                    | A7FF27_RANK_LABEL_DIAGNOSTIC_CLUE |       2 |
| basis_premium_like                    | HOLD_A7FF27_CONTROL_DOMINATED     |       5 |
| basis_premium_like                    | HOLD_A7FF27_ONE_BAR_LAG_FRAGILE   |       1 |
| basis_premium_like                    | HOLD_A7FF27_PRE_MAY_UNSTABLE      |       5 |
| basis_premium_like|basis_premium_like | A7FF27_NUMERIC_CLUE               |      12 |
| basis_premium_like|basis_premium_like | A7FF27_RANK_LABEL_DIAGNOSTIC_CLUE |       4 |
| basis_premium_like|basis_premium_like | HOLD_A7FF27_CONTROL_DOMINATED     |      30 |
| basis_premium_like|basis_premium_like | HOLD_A7FF27_COST2_PROXY_FRAGILE   |       3 |
| basis_premium_like|basis_premium_like | HOLD_A7FF27_ONE_BAR_LAG_FRAGILE   |      12 |
| basis_premium_like|basis_premium_like | HOLD_A7FF27_PRE_MAY_UNSTABLE      |      59 |
| basis_premium_like|price_like         | A7FF27_NUMERIC_CLUE               |       6 |
| basis_premium_like|price_like         | A7FF27_RANK_LABEL_DIAGNOSTIC_CLUE |       1 |
| basis_premium_like|price_like         | HOLD_A7FF27_CONTROL_DOMINATED     |       3 |
| basis_premium_like|price_like         | HOLD_A7FF27_PRE_MAY_UNSTABLE      |      30 |
| basis_premium_like|volatility_like    | A7FF27_NUMERIC_CLUE               |      20 |
| basis_premium_like|volatility_like    | A7FF27_RANK_LABEL_DIAGNOSTIC_CLUE |       5 |
| basis_premium_like|volatility_like    | HOLD_A7FF27_CONTROL_DOMINATED     |      13 |
| basis_premium_like|volatility_like    | HOLD_A7FF27_ONE_BAR_LAG_FRAGILE   |       4 |
| basis_premium_like|volatility_like    | HOLD_A7FF27_PRE_MAY_UNSTABLE      |      38 |
| price_like|volatility_like            | A7FF27_NUMERIC_CLUE               |       4 |
| price_like|volatility_like            | A7FF27_RANK_LABEL_DIAGNOSTIC_CLUE |       2 |
| price_like|volatility_like            | HOLD_A7FF27_CONTROL_DOMINATED     |       7 |
| price_like|volatility_like            | HOLD_A7FF27_ONE_BAR_LAG_FRAGILE   |       3 |
| price_like|volatility_like            | HOLD_A7FF27_PRE_MAY_UNSTABLE      |       4 |

## Control Summary

| control              |   median_ratio |   max_ratio |   rows |
|:---------------------|---------------:|------------:|-------:|
| one_bar_lag          |       0.554576 |    177.667  |    840 |
| same_family_placebo  |       0.209278 |    297.05   |    840 |
| sign_flip            |       0.996704 |     74.4284 |    840 |
| symbol_shuffle       |       0.264593 |    239.683  |    840 |
| time_shuffle         |       0.311971 |    178.796  |    840 |
| wrong_lag_future_24h |       0.678209 |    434.074  |    840 |
| wrong_lag_stale_168h |       0.350337 |    354.346  |    840 |

## Selected Portfolio Queue

| blueprint_id             | expression                                                            | semantic_pair                         | motif        | label_family           |   label_horizon_h |   orientation_from_train |   premay_positive_split_count | premay_all_positive   |   control_ratio_premay_max |   one_bar_lag_recent_oriented | lag_ok   |   robust_median_tstat_floor |   robust_min_tstat_floor | robust_ok   |   cost2_recent_oriented |   cost5_recent_oriented |   cost10_recent_oriented |   avg_n_obs_recent | decision            |   train_2024_n |   train_2024_mean_spread |   train_2024_tstat |   train_2024_nonoverlap_median_tstat |   train_2024_nonoverlap_min_tstat |   train_2024_positive_rate |   validation_2025H1_n |   validation_2025H1_mean_spread |   validation_2025H1_tstat |   validation_2025H1_nonoverlap_median_tstat |   validation_2025H1_nonoverlap_min_tstat |   validation_2025H1_positive_rate |   test_2025H2_n |   test_2025H2_mean_spread |   test_2025H2_tstat |   test_2025H2_nonoverlap_median_tstat |   test_2025H2_nonoverlap_min_tstat |   test_2025H2_positive_rate |   recent_oos_2026JanApr_n |   recent_oos_2026JanApr_mean_spread |   recent_oos_2026JanApr_tstat |   recent_oos_2026JanApr_nonoverlap_median_tstat |   recent_oos_2026JanApr_nonoverlap_min_tstat |   recent_oos_2026JanApr_positive_rate |   non_l7_bonus |   score_no_may | skeleton_key          |   finite_share |   nonzero_share |
|:-------------------------|:----------------------------------------------------------------------|:--------------------------------------|:-------------|:-----------------------|------------------:|-------------------------:|------------------------------:|:----------------------|---------------------------:|------------------------------:|:---------|----------------------------:|-------------------------:|:------------|------------------------:|------------------------:|-------------------------:|-------------------:|:--------------------|---------------:|-------------------------:|-------------------:|-------------------------------------:|----------------------------------:|---------------------------:|----------------------:|--------------------------------:|--------------------------:|--------------------------------------------:|-----------------------------------------:|----------------------------------:|----------------:|--------------------------:|--------------------:|--------------------------------------:|-----------------------------------:|----------------------------:|--------------------------:|------------------------------------:|------------------------------:|------------------------------------------------:|---------------------------------------------:|--------------------------------------:|---------------:|---------------:|:----------------------|---------------:|----------------:|
| a7ff24r_858ff2210f276fcf | Delta(mark_index_basis_bps,12)                                        | basis_premium_like                    | single       | L5_vol_adjusted_return |                 8 |                       -1 |                             3 | True                  |                   0.619643 |                     0.247474  | True     |                   0.626901  |                  2.32574 | True        |               0.389848  |               0.389248  |                0.388248  |            94.9333 | A7FF27_NUMERIC_CLUE |            700 |              -0.0150161  |          -0.519622 |                           -0.175288  |                         -1.6345   |                   0.48     |                   712 |                      -0.0557262 |                  -2.01878 |                                   -0.626901 |                                 -2.52672 |                          0.441011 |             712 |                -0.137832  |            -3.26193 |                            -1.32965   |                           -2.32574 |                    0.450843 |                       712 |                          -0.390248  |                      -5.50726 |                                        -2.33334 |                                     -3.27856 |                              0.411517 |              1 |       395.628  | skel_1d39996e97d5ace0 |       0.996265 |        0.998429 |
| a7ff24r_650915032f2a5979 | Mul(Delta(mark_index_basis_bps,12),Sign(realized_vol_24h))            | basis_premium_like|volatility_like    | gated_sign   | L5_vol_adjusted_return |                 8 |                       -1 |                             3 | True                  |                   0.640765 |                     0.247474  | True     |                   0.626901  |                  2.32574 | True        |               0.389848  |               0.389248  |                0.388248  |            94.9333 | A7FF27_NUMERIC_CLUE |            700 |              -0.0150161  |          -0.519622 |                           -0.175288  |                         -1.6345   |                   0.48     |                   712 |                      -0.0557262 |                  -2.01878 |                                   -0.626901 |                                 -2.52672 |                          0.441011 |             712 |                -0.137832  |            -3.26193 |                            -1.32965   |                           -2.32574 |                    0.450843 |                       712 |                          -0.390248  |                      -5.50726 |                                        -2.33334 |                                     -3.27856 |                              0.411517 |              1 |       395.607  | skel_136259b72205469f |       0.823901 |        0.998297 |
| a7ff24r_389e925b81a0c645 | Mean(Mul(Delta(mark_index_basis_bps,1),realized_vol_168h),4)          | basis_premium_like|volatility_like    | smooth_mul   | L5_vol_adjusted_return |                 8 |                       -1 |                             3 | True                  |                   0.971788 |                     0.11202   | True     |                   0.0839626 |                  2.51434 | True        |               0.193082  |               0.192482  |                0.191482  |            94.9333 | A7FF27_NUMERIC_CLUE |            708 |              -0.00884337 |          -0.316081 |                            0.0329389 |                         -1.21486  |                   0.491525 |                   712 |                      -0.0544469 |                  -1.80874 |                                   -0.669007 |                                 -2.51434 |                          0.463483 |             712 |                -0.078245  |            -1.95104 |                            -0.0839626 |                           -3.60801 |                    0.457865 |                       712 |                          -0.193482  |                      -3.06255 |                                        -1.42325 |                                     -4.55331 |                              0.457865 |              1 |       198.51   | skel_8184698cb7b24c02 |       0.826199 |        0.99983  |
| a7ff24r_bcc3435cf539d883 | Sub(mark_index_basis_bps,Mean(premium_close_bps,12))                  | basis_premium_like|basis_premium_like | sub          | L5_vol_adjusted_return |                 1 |                       -1 |                             3 | True                  |                   0.191548 |                     0.0416174 | True     |                   7.11992   |                  7.11992 | True        |               0.152806  |               0.152206  |                0.151206  |            95.8667 | A7FF27_NUMERIC_CLUE |            708 |              -0.0229398  |          -2.02448  |                           -2.02448   |                         -2.02448  |                   0.475989 |                   719 |                      -0.0920096 |                  -9.10063 |                                   -9.10063  |                                 -9.10063 |                          0.340751 |             719 |                -0.142002  |            -9.7445  |                            -9.7445    |                           -9.7445  |                    0.301808 |                       719 |                          -0.153206  |                      -7.11992 |                                        -7.11992 |                                     -7.11992 |                              0.369958 |              1 |       159.014  | skel_f8484b844efd270f |       0.996553 |        0.999111 |
| a7ff24r_145e2d58adad4f4a | SafeDiv(mark_index_basis_bps,Abs(ZScore(Mean(premium_close_bps,12)))) | basis_premium_like|basis_premium_like | safe_div_abs | L5_vol_adjusted_return |                 4 |                       -1 |                             3 | True                  |                   0.924745 |                     0.0448436 | True     |                   0.513295  |                  2.27988 | True        |               0.136893  |               0.136293  |                0.135293  |            95.4667 | A7FF27_NUMERIC_CLUE |            705 |              -0.0111151  |          -0.632373 |                           -0.342037  |                         -1.50377  |                   0.485106 |                   716 |                      -0.0304805 |                  -1.44335 |                                   -0.513295 |                                 -2.37201 |                          0.446927 |             716 |                -0.0811605 |            -2.66647 |                            -1.58901   |                           -2.27988 |                    0.432961 |                       716 |                          -0.137293  |                      -4.06937 |                                        -2.22091 |                                     -2.38512 |                              0.438547 |              1 |       142.369  | skel_c80f62c274b367a9 |       0.996553 |        0.987385 |
| a7ff24r_09dc2d7e51641cb0 | Sub(Delta(mark_index_basis_bps,8),premium_close_bps)                  | basis_premium_like|basis_premium_like | sub          | L5_vol_adjusted_return |                 1 |                       -1 |                             3 | True                  |                   0.590707 |                     0.0271568 | True     |                   4.24674   |                  4.24674 | True        |               0.0856884 |               0.0850884 |                0.0840884 |            95.8667 | A7FF27_NUMERIC_CLUE |            711 |              -0.00537184 |          -0.549633 |                           -0.549633  |                         -0.549633 |                   0.49789  |                   719 |                      -0.0629903 |                  -5.91118 |                                   -5.91118  |                                 -5.91118 |                          0.410292 |             719 |                -0.103456  |            -7.63857 |                            -7.63857   |                           -7.63857 |                    0.357441 |                       719 |                          -0.0860884 |                      -4.24674 |                                        -4.24674 |                                     -4.24674 |                              0.415855 |              1 |        91.4977 | skel_0994b3a36a4d53ba |       0.997415 |        0.997849 |
| a7ff24r_c223ee324263786f | SafeDiv(premium_close_bps,Abs(realized_vol_168h))                     | basis_premium_like|volatility_like    | safe_div_abs | L5_vol_adjusted_return |                 1 |                       -1 |                             3 | True                  |                   0.9186   |                     0.039465  | True     |                   2.53115   |                  2.53115 | True        |               0.0857199 |               0.0851199 |                0.0841199 |            95.8667 | A7FF27_NUMERIC_CLUE |            715 |              -0.0234352  |          -1.86784  |                           -1.86784   |                         -1.86784  |                   0.454545 |                   668 |                      -0.056895  |                  -3.17894 |                                   -3.17894  |                                 -3.17894 |                          0.411677 |             713 |                -0.0502258 |            -2.53115 |                            -2.53115   |                           -2.53115 |                    0.441795 |                       719 |                          -0.0861199 |                      -3.36867 |                                        -3.36867 |                                     -3.36867 |                              0.438108 |              1 |        91.2013 | skel_d9d4f69744bac825 |       0.827348 |        0.672833 |
| a7ff24r_14bb4d389b4b94f0 | Sub(ZScore(Mean(mark_index_basis_bps,8)),premium_close_bps)           | basis_premium_like|basis_premium_like | sub          | L5_vol_adjusted_return |                 1 |                        1 |                             3 | True                  |                   0.798537 |                     0.0258773 | True     |                   3.71359   |                  3.71359 | True        |               0.0802787 |               0.0796787 |                0.0786787 |            95.8667 | A7FF27_NUMERIC_CLUE |            712 |               0.0247355  |           2.34597  |                            2.34597   |                          2.34597  |                   0.557584 |                   719 |                       0.0445687 |                   4.05844 |                                    4.05844  |                                  4.05844 |                          0.566064 |             719 |                 0.0505816 |             3.71359 |                             3.71359   |                            3.71359 |                    0.556328 |                       719 |                           0.0806787 |                       3.94638 |                                         3.94638 |                                      3.94638 |                              0.557719 |              1 |        85.8802 | skel_97ea9710bb50e137 |       0.997702 |        1        |

## Boundary

```text
No May/post-selection stress is used in scoring or authorization.
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
L7 ranked-return rows remain diagnostic-only and cannot promote without non-L7 support.
```
