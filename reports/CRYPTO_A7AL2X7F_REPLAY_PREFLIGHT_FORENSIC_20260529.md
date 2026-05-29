# CRYPTO A7AL-2X7F REPLAY PREFLIGHT FORENSIC

Generated: 2026-05-29T02:09:20Z

## Decision

`HOLD_A7AL2X7F_OBJECTIVE_FAMILY_NUMERIC_EVIDENCE_WEAK`

X7F is a forensic audit over existing X7 artifacts. It does not generate formulas, run search, train a model, or authorize replay promotion.

## Manifest

```json
{
  "allowed_next": [
    "A7AL-2X7F forensic expansion on company machine",
    "objective-family redesign away from current OI/positioning pool"
  ],
  "authorizes_alpha_proof": false,
  "authorizes_formula_generation": false,
  "authorizes_full_numeric_replay": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "no_stress_clean_preflight_clues",
    "pre_may_alignment_too_sparse",
    "matched_controls_often_dominate",
    "some_families_sparse_under_smoke_subset"
  ],
  "candidate_count": 14,
  "control_dominated_count": 11,
  "decision": "HOLD_A7AL2X7F_OBJECTIVE_FAMILY_NUMERIC_EVIDENCE_WEAK",
  "executes_formula_generation": false,
  "executes_replay": false,
  "executes_search": false,
  "executes_training": false,
  "generated_at": "2026-05-29T02:09:20Z",
  "missing_or_sparse_count": 2,
  "pre_may_all_positive_count": 1,
  "source_decision": "HOLD_A7AL2X7_NO_CLEAN_NUMERIC_PREFLIGHT_CLUES",
  "source_stage": "A7AL-2X7",
  "stage": "A7AL-2X7F",
  "stress_clean_preflight_clue_count": 0
}
```

## Failure Roots

| failure_root                          |   candidate_count |
|:--------------------------------------|------------------:|
| pre_may_direction_unstable            |                11 |
| metric_missing_or_sparse_smoke_window |                 2 |
| matched_control_dominated             |                 1 |

## Split Alignment

| split                 |   candidate_count |   finite_count |   positive_count |   positive_rate |   median_oriented_spread |   mean_oriented_spread |
|:----------------------|------------------:|---------------:|-----------------:|----------------:|-------------------------:|-----------------------:|
| validation_2025H1     |                14 |             12 |                4 |        0.285714 |             -0.000742727 |           -0.000599741 |
| test_2025H2           |                14 |             12 |                4 |        0.285714 |             -0.000739107 |           -1.36498e-05 |
| recent_oos_2026JanApr |                14 |             12 |                8 |        0.571429 |              0.00073813  |           -7.59889e-05 |
| known_may2026_stress  |                14 |             10 |                5 |        0.357143 |              0.00048928  |           -0.000334368 |

## Objective Family Summary

| objective_family                   |   candidate_count |   pre_may_all_positive |   may_stress_clean |   control_dominated |   missing_or_sparse |   median_max_control_ratio |   median_recent_oriented_spread | failure_roots                                         |
|:-----------------------------------|------------------:|-----------------------:|-------------------:|--------------------:|--------------------:|---------------------------:|--------------------------------:|:------------------------------------------------------|
| F0_OI_delta_price_interaction      |                 2 |                      0 |                  1 |                   2 |                   0 |                    7.12567 |                    -0.00265945  | pre_may_direction_unstable                            |
| F1_OI_basis_premium_interaction    |                 2 |                      1 |                  1 |                   2 |                   0 |                    7.41084 |                     0.00238711  | matched_control_dominated\|pre_may_direction_unstable |
| F2_OI_funding_crowding_interaction |                 2 |                      0 |                  0 |                   0 |                   2 |                  nan       |                   nan           | metric_missing_or_sparse_smoke_window                 |
| F3_positioning_divergence          |                 2 |                      0 |                  0 |                   2 |                   0 |                   16.5684  |                    -0.00507454  | pre_may_direction_unstable                            |
| F4_OI_taker_flow_interaction       |                 2 |                      0 |                  2 |                   2 |                   0 |                   17.7813  |                     0.00194816  | pre_may_direction_unstable                            |
| F5_OI_upper_regime_interaction     |                 2 |                      0 |                  0 |                   2 |                   0 |                    6.34974 |                     0.00285841  | pre_may_direction_unstable                            |
| F6_OI_latent_state_interaction     |                 2 |                      0 |                  1 |                   1 |                   0 |                   40.1726  |                     8.43799e-05 | pre_may_direction_unstable                            |

## Candidate Forensic Detail

| candidate_id             | objective_family                   | pre_may_sign_pattern   |   pre_may_positive_splits |   recent_oriented_spread |   one_bar_recent_retention |   cost10_recent_proxy |   max_control_ratio_premay | max_control_variant   | max_control_split     |   may_oriented_spread | failure_root                          |
|:-------------------------|:-----------------------------------|:-----------------------|--------------------------:|-------------------------:|---------------------------:|----------------------:|---------------------------:|:----------------------|:----------------------|----------------------:|:--------------------------------------|
| a7al2x3_c6d040e141ee4a7a | F0_OI_delta_price_interaction      | -/-/+                  |                         1 |              0.00237831  |                   1.28032  |           0.000378309 |                    5.18361 | wrong_lag_future_24h  | recent_oos_2026JanApr |           0.000978559 | pre_may_direction_unstable            |
| a7al2x3_a685d04007266d3e | F0_OI_delta_price_interaction      | +/+/-                  |                         2 |             -0.00769721  |                   1.02863  |          -0.00969721  |                    9.06772 | wrong_lag_future_24h  | validation_2025H1     |          -0.00415499  | pre_may_direction_unstable            |
| a7al2x3_8943bb8dd3c5f640 | F1_OI_basis_premium_interaction    | -/-/+                  |                         1 |              0.000811039 |                   1.23809  |          -0.00118896  |                   12.9969  | wrong_lag_future_24h  | recent_oos_2026JanApr |           0.00144417  | pre_may_direction_unstable            |
| a7al2x3_8133b78c17250336 | F1_OI_basis_premium_interaction    | +/+/+                  |                         3 |              0.00396317  |                   1.00885  |           0.00196317  |                    1.82482 | symbol_shuffle        | validation_2025H1     |          -0.00162817  | matched_control_dominated             |
| a7al2x3_dcf6359c32accfb4 | F2_OI_funding_crowding_interaction | NA/NA/NA               |                         0 |            nan           |                 nan        |         nan           |                  nan       |                       |                       |         nan           | metric_missing_or_sparse_smoke_window |
| a7al2x3_0bd3d497403b3991 | F2_OI_funding_crowding_interaction | NA/NA/NA               |                         0 |            nan           |                 nan        |         nan           |                  nan       |                       |                       |         nan           | metric_missing_or_sparse_smoke_window |
| a7al2x3_93725c2d40077dd9 | F3_positioning_divergence          | -/-/-                  |                         0 |             -0.00996163  |                   0.996177 |          -0.0119616   |                    4.88344 | wrong_lag_future_24h  | validation_2025H1     |          -0.00253265  | pre_may_direction_unstable            |
| a7al2x3_afebb1f45f8929ea | F3_positioning_divergence          | -/-/-                  |                         0 |             -0.000187455 |                   0.888156 |          -0.00218745  |                   28.2533  | symbol_shuffle        | recent_oos_2026JanApr |          -0.00360569  | pre_may_direction_unstable            |
| a7al2x3_1fd71f89fcb97240 | F4_OI_taker_flow_interaction       | -/-/+                  |                         1 |              0.000665222 |                   1.15353  |          -0.00133478  |                   31.5666  | symbol_shuffle        | test_2025H2           |           0.00154124  | pre_may_direction_unstable            |
| a7al2x3_a551e0d946a6abf3 | F4_OI_taker_flow_interaction       | +/-/+                  |                         2 |              0.00323109  |                   0.920123 |           0.00123109  |                    3.996   | symbol_shuffle        | test_2025H2           |           0.00158998  | pre_may_direction_unstable            |
| a7al2x3_9add29eae207e174 | F5_OI_upper_regime_interaction     | -/+/+                  |                         2 |              0.00285841  |                   1.07607  |           0.000858415 |                    6.34974 | wrong_lag_future_24h  | recent_oos_2026JanApr |         nan           | pre_may_direction_unstable            |
| a7al2x3_d294deb3ca25cf27 | F5_OI_upper_regime_interaction     | -/+/+                  |                         2 |              0.00285841  |                   1.07607  |           0.000858415 |                    6.34974 | wrong_lag_future_24h  | recent_oos_2026JanApr |         nan           | pre_may_direction_unstable            |
| a7al2x3_6425856b9df4b997 | F6_OI_latent_state_interaction     | -/-/-                  |                         0 |              0           |                 nan        |          -0.002       |                  nan       |                       |                       |           0           | pre_may_direction_unstable            |
| a7al2x3_f726e8031e11a5c6 | F6_OI_latent_state_interaction     | +/-/+                  |                         2 |              0.00016876  |                   0.781442 |          -0.00183124  |                   40.1726  | wrong_lag_future_24h  | recent_oos_2026JanApr |           0.00302386  | pre_may_direction_unstable            |

## Control Dominance Rollup

| variant              | split                 |   finite_ratio_count |   dominance_count |   median_control_abs_ratio |   max_control_abs_ratio |
|:---------------------|:----------------------|---------------------:|------------------:|---------------------------:|------------------------:|
| wrong_lag_future_24h | test_2025H2           |                   11 |                 9 |                   1.3201   |               17.0182   |
| wrong_lag_future_24h | recent_oos_2026JanApr |                   11 |                 8 |                   5.18361  |               40.1726   |
| wrong_lag_future_24h | validation_2025H1     |                   11 |                 7 |                   1.79585  |                9.06772  |
| wrong_lag_stale_168h | validation_2025H1     |                   11 |                 7 |                   1.26134  |                2.19312  |
| wrong_lag_stale_168h | test_2025H2           |                   11 |                 6 |                   1.38352  |               18.9812   |
| symbol_shuffle       | validation_2025H1     |                   11 |                 6 |                   1.19738  |                5.07747  |
| symbol_shuffle       | test_2025H2           |                   11 |                 4 |                   0.846323 |               31.5666   |
| wrong_lag_stale_168h | recent_oos_2026JanApr |                   11 |                 4 |                   0.335081 |               21.3954   |
| time_shuffle         | recent_oos_2026JanApr |                   11 |                 4 |                   0.330116 |                7.05189  |
| symbol_shuffle       | recent_oos_2026JanApr |                   11 |                 3 |                   0.445138 |               28.2533   |
| same_family_random   | recent_oos_2026JanApr |                   11 |                 3 |                   0.821079 |               18.9059   |
| time_shuffle         | validation_2025H1     |                   11 |                 2 |                   0.46745  |                1.90744  |
| same_family_random   | test_2025H2           |                   11 |                 2 |                   0.19274  |                1.20141  |
| time_shuffle         | test_2025H2           |                   11 |                 1 |                   0.368773 |                2.73457  |
| same_family_random   | validation_2025H1     |                   11 |                 0 |                   0.158415 |                0.851453 |

## Highest Control Ratios

| candidate_id             | variant              | split                 |   original_oriented_spread |   control_oriented_spread |   control_abs_ratio | control_dominates   |
|:-------------------------|:---------------------|:----------------------|---------------------------:|--------------------------:|--------------------:|:--------------------|
| a7al2x3_f726e8031e11a5c6 | wrong_lag_future_24h | recent_oos_2026JanApr |                0.00016876  |               0.00677952  |            40.1726  | True                |
| a7al2x3_1fd71f89fcb97240 | symbol_shuffle       | test_2025H2           |               -0.000153943 |               0.00485945  |            31.5666  | True                |
| a7al2x3_afebb1f45f8929ea | symbol_shuffle       | recent_oos_2026JanApr |               -0.000187455 |               0.00529622  |            28.2533  | True                |
| a7al2x3_afebb1f45f8929ea | wrong_lag_stale_168h | recent_oos_2026JanApr |               -0.000187455 |               0.00401067  |            21.3954  | True                |
| a7al2x3_1fd71f89fcb97240 | wrong_lag_stale_168h | test_2025H2           |               -0.000153943 |              -0.00292202  |            18.9812  | True                |
| a7al2x3_afebb1f45f8929ea | same_family_random   | recent_oos_2026JanApr |               -0.000187455 |              -0.003544    |            18.9059  | True                |
| a7al2x3_1fd71f89fcb97240 | wrong_lag_future_24h | test_2025H2           |               -0.000153943 |              -0.00261982  |            17.0182  | True                |
| a7al2x3_afebb1f45f8929ea | wrong_lag_future_24h | recent_oos_2026JanApr |               -0.000187455 |               0.00252577  |            13.474   | True                |
| a7al2x3_8943bb8dd3c5f640 | wrong_lag_future_24h | recent_oos_2026JanApr |                0.000811039 |               0.010541    |            12.9969  | True                |
| a7al2x3_f726e8031e11a5c6 | wrong_lag_stale_168h | recent_oos_2026JanApr |                0.00016876  |              -0.00195105  |            11.5611  | True                |
| a7al2x3_1fd71f89fcb97240 | symbol_shuffle       | recent_oos_2026JanApr |                0.000665222 |              -0.00618502  |             9.29768 | True                |
| a7al2x3_a685d04007266d3e | wrong_lag_future_24h | validation_2025H1     |                0.00044484  |               0.00403369  |             9.06772 | True                |
| a7al2x3_f726e8031e11a5c6 | same_family_random   | recent_oos_2026JanApr |                0.00016876  |               0.00121584  |             7.20459 | True                |
| a7al2x3_f726e8031e11a5c6 | time_shuffle         | recent_oos_2026JanApr |                0.00016876  |              -0.00119007  |             7.05189 | True                |
| a7al2x3_f726e8031e11a5c6 | symbol_shuffle       | recent_oos_2026JanApr |                0.00016876  |               0.00116214  |             6.88636 | True                |
| a7al2x3_d294deb3ca25cf27 | wrong_lag_future_24h | recent_oos_2026JanApr |                0.00285841  |               0.0181502   |             6.34974 | True                |
| a7al2x3_9add29eae207e174 | wrong_lag_future_24h | recent_oos_2026JanApr |                0.00285841  |               0.0181502   |             6.34974 | True                |
| a7al2x3_afebb1f45f8929ea | time_shuffle         | recent_oos_2026JanApr |               -0.000187455 |               0.00112725  |             6.01343 | True                |
| a7al2x3_c6d040e141ee4a7a | wrong_lag_future_24h | recent_oos_2026JanApr |                0.00237831  |              -0.0123282   |             5.18361 | True                |
| a7al2x3_afebb1f45f8929ea | symbol_shuffle       | validation_2025H1     |               -0.000537762 |              -0.00273047  |             5.07747 | True                |
| a7al2x3_afebb1f45f8929ea | wrong_lag_stale_168h | test_2025H2           |               -0.00132427  |               0.00654027  |             4.93877 | True                |
| a7al2x3_93725c2d40077dd9 | wrong_lag_future_24h | validation_2025H1     |               -0.00199746  |               0.00975449  |             4.88344 | True                |
| a7al2x3_1fd71f89fcb97240 | wrong_lag_future_24h | validation_2025H1     |               -0.000947691 |              -0.00390508  |             4.12062 | True                |
| a7al2x3_a551e0d946a6abf3 | symbol_shuffle       | test_2025H2           |               -0.00144779  |              -0.00578536  |             3.996   | True                |
| a7al2x3_afebb1f45f8929ea | wrong_lag_future_24h | test_2025H2           |               -0.00132427  |               0.00432255  |             3.2641  | True                |
| a7al2x3_afebb1f45f8929ea | symbol_shuffle       | test_2025H2           |               -0.00132427  |              -0.00397548  |             3.00202 | True                |
| a7al2x3_f726e8031e11a5c6 | wrong_lag_stale_168h | test_2025H2           |               -0.00152119  |              -0.00444678  |             2.92322 | True                |
| a7al2x3_a685d04007266d3e | wrong_lag_future_24h | test_2025H2           |                0.00418236  |               0.0120903   |             2.89078 | True                |
| a7al2x3_1fd71f89fcb97240 | time_shuffle         | test_2025H2           |               -0.000153943 |               0.000420966 |             2.73457 | True                |
| a7al2x3_a685d04007266d3e | wrong_lag_future_24h | recent_oos_2026JanApr |               -0.00769721  |               0.0207551   |             2.69645 | True                |

## Interpretation

```text
Main finding:
  X7 HOLD is not caused by evaluator failure. Existing numeric artifacts are complete enough for this forensic.

Observed failure pattern:
  Most selected OI/positioning interaction candidates do not keep the same oriented sign across validation, test, and recent OOS.
  The only all-positive pre-May candidate is dominated by matched controls and is May-negative.
  Wrong-lag / shuffle / same-family controls are often stronger than the original signals.

Allowed next action:
  forensic expansion or objective-family redesign only.

Not authorized:
  full replay
  new formula generation
  large search
  alpha proof
  shadow / paper / live
```
