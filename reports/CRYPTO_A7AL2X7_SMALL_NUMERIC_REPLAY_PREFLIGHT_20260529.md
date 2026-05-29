# CRYPTO A7AL-2X7 SMALL NUMERIC REPLAY PREFLIGHT

Generated: 2026-05-29T01:56:26Z

## Decision

`HOLD_A7AL2X7_NO_CLEAN_NUMERIC_PREFLIGHT_CLUES`

This is a bounded numeric replay preflight. It is not full replay, formula search, alpha proof, or production-readiness evidence.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_formula_generation": false,
  "authorizes_full_numeric_replay": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "no_replay_preflight_clues"
  ],
  "candidate_count": 14,
  "controls": [
    "one_bar_lag",
    "wrong_lag_future_24h",
    "wrong_lag_stale_168h",
    "time_shuffle",
    "symbol_shuffle",
    "same_family_random"
  ],
  "decision": "HOLD_A7AL2X7_NO_CLEAN_NUMERIC_PREFLIGHT_CLUES",
  "eval_error_count": 0,
  "executes_formula_generation": false,
  "executes_search": false,
  "executes_small_numeric_replay_preflight": true,
  "executes_training": false,
  "full_timestamps_before_smoke_subset": 21025,
  "generated_at": "2026-05-29T01:56:26Z",
  "hours_per_split": 720,
  "label": "log_trade_close_t_plus_24h_minus_log_trade_close_t",
  "metric_rows": 490,
  "orientation": "train_2024_original_spread_sign_only",
  "pre_may_clue_may_veto_count": 0,
  "stage": "A7AL-2X7",
  "stress_clean_clue_count": 0,
  "symbols_loaded": 32,
  "timestamps": 3481
}
```

## Decision Counts

| decision                       |   count |
|:-------------------------------|--------:|
| HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |      13 |
| HOLD_A7AL2X7_CONTROL_DOMINATED |       1 |

## Candidate Decisions

| candidate_id             | objective_family                   |   orientation_from_train |   oriented_validation_spread |   oriented_test_spread |   oriented_recent_spread |   oriented_may_stress_spread |   one_bar_lag_recent_oriented |   cost10_recent_proxy |   control_dominance_ratio_premay_max | pre_may_positive   | lag_ok   | may_stress_clean   | decision                       |
|:-------------------------|:-----------------------------------|-------------------------:|-----------------------------:|-----------------------:|-------------------------:|-----------------------------:|------------------------------:|----------------------:|-------------------------------------:|:-------------------|:---------|:-------------------|:-------------------------------|
| a7al2x3_c6d040e141ee4a7a | F0_OI_delta_price_interaction      |                       -1 |                 -0.00259586  |           -0.00554553  |              0.00237831  |                  0.000978559 |                   0.00304499  |           0.000378309 |                              5.18361 | False              | True     | True               | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_a685d04007266d3e | F0_OI_delta_price_interaction      |                        1 |                  0.00044484  |            0.00418236  |             -0.00769721  |                 -0.00415499  |                  -0.00791762  |          -0.00969721  |                              9.06772 | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_8943bb8dd3c5f640 | F1_OI_basis_premium_interaction    |                        1 |                 -0.00179297  |           -0.00515948  |              0.000811039 |                  0.00144417  |                   0.00100414  |          -0.00118896  |                             12.9969  | False              | True     | True               | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_8133b78c17250336 | F1_OI_basis_premium_interaction    |                       -1 |                  0.00218379  |            0.00393689  |              0.00396317  |                 -0.00162817  |                   0.00399827  |           0.00196317  |                              1.82482 | True               | True     | False              | HOLD_A7AL2X7_CONTROL_DOMINATED |
| a7al2x3_dcf6359c32accfb4 | F2_OI_funding_crowding_interaction |                        1 |                nan           |          nan           |            nan           |                nan           |                 nan           |         nan           |                            nan       | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_0bd3d497403b3991 | F2_OI_funding_crowding_interaction |                        1 |                nan           |          nan           |            nan           |                nan           |                 nan           |         nan           |                            nan       | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_93725c2d40077dd9 | F3_positioning_divergence          |                       -1 |                 -0.00199746  |           -0.00233003  |             -0.00996163  |                 -0.00253265  |                  -0.00992355  |          -0.0119616   |                              4.88344 | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_afebb1f45f8929ea | F3_positioning_divergence          |                       -1 |                 -0.000537762 |           -0.00132427  |             -0.000187455 |                 -0.00360569  |                  -0.000166489 |          -0.00218745  |                             28.2533  | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_1fd71f89fcb97240 | F4_OI_taker_flow_interaction       |                       -1 |                 -0.000947691 |           -0.000153943 |              0.000665222 |                  0.00154124  |                   0.000767356 |          -0.00133478  |                             31.5666  | False              | True     | True               | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_a551e0d946a6abf3 | F4_OI_taker_flow_interaction       |                       -1 |                  0.000761644 |           -0.00144779  |              0.00323109  |                  0.00158998  |                   0.00297301  |           0.00123109  |                              3.996   | False              | True     | True               | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_9add29eae207e174 | F5_OI_upper_regime_interaction     |                        1 |                 -0.00177117  |            0.00459959  |              0.00285841  |                nan           |                   0.00307585  |           0.000858415 |                              6.34974 | False              | True     | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_d294deb3ca25cf27 | F5_OI_upper_regime_interaction     |                        1 |                 -0.00177117  |            0.00459959  |              0.00285841  |                nan           |                   0.00307585  |           0.000858415 |                              6.34974 | False              | True     | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_6425856b9df4b997 | F6_OI_latent_state_interaction     |                        1 |                  0           |            0           |              0           |                  0           |                   0           |          -0.002       |                            nan       | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_f726e8031e11a5c6 | F6_OI_latent_state_interaction     |                        1 |                  0.000826908 |           -0.00152119  |              0.00016876  |                  0.00302386  |                   0.000131876 |          -0.00183124  |                             40.1726  | False              | True     | True               | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |

## Metrics Preview

| candidate_id             | variant              | split                 |   n_dates |   avg_n_obs |   mean_spread_24h |   naive_tstat |   nonoverlap_median_tstat |   nonoverlap_min_tstat |   positive_spread_rate |
|:-------------------------|:---------------------|:----------------------|----------:|------------:|------------------:|--------------:|--------------------------:|-----------------------:|-----------------------:|
| a7al2x3_c6d040e141ee4a7a | original             | train_2024            |       684 |          32 |      -0.000171574 |    -0.137908  |                 0.112989  |             -1.75569   |               0.494152 |
| a7al2x3_c6d040e141ee4a7a | original             | validation_2025H1     |       696 |          32 |       0.00259586  |     3.82749   |                 0.522914  |             -1.23674   |               0.545977 |
| a7al2x3_c6d040e141ee4a7a | original             | test_2025H2           |       696 |          32 |       0.00554553  |     4.25465   |                 1.00987   |             -1.69643   |               0.541667 |
| a7al2x3_c6d040e141ee4a7a | original             | recent_oos_2026JanApr |       696 |          32 |      -0.00237831  |    -1.78839   |                -0.366283  |             -1.76435   |               0.482759 |
| a7al2x3_c6d040e141ee4a7a | original             | known_may2026_stress  |       576 |          32 |      -0.000978559 |    -1.2101    |                -0.125525  |             -2.35125   |               0.465278 |
| a7al2x3_c6d040e141ee4a7a | one_bar_lag          | train_2024            |       683 |          32 |      -0.000316844 |    -0.255396  |                 0.122091  |             -1.8007    |               0.500732 |
| a7al2x3_c6d040e141ee4a7a | one_bar_lag          | validation_2025H1     |       696 |          32 |       0.00252336  |     3.74974   |                 0.560887  |             -1.07756   |               0.554598 |
| a7al2x3_c6d040e141ee4a7a | one_bar_lag          | test_2025H2           |       696 |          32 |       0.00485392  |     3.74177   |                 0.602983  |             -2.10685   |               0.528736 |
| a7al2x3_c6d040e141ee4a7a | one_bar_lag          | recent_oos_2026JanApr |       696 |          32 |      -0.00304499  |    -2.28558   |                -0.380101  |             -2.21201   |               0.478448 |
| a7al2x3_c6d040e141ee4a7a | one_bar_lag          | known_may2026_stress  |       576 |          32 |      -0.00150607  |    -1.82149   |                -0.295918  |             -2.6665    |               0.461806 |
| a7al2x3_c6d040e141ee4a7a | time_shuffle         | train_2024            |       694 |          32 |      -0.00155277  |    -1.31866   |                -0.182218  |             -2.91988   |               0.481268 |
| a7al2x3_c6d040e141ee4a7a | time_shuffle         | validation_2025H1     |       693 |          32 |       0.00128615  |     1.96332   |                 0.400981  |             -1.4182    |               0.516595 |
| a7al2x3_c6d040e141ee4a7a | time_shuffle         | test_2025H2           |       692 |          32 |      -0.000529539 |    -0.638339  |                 0.141664  |             -2.10545   |               0.501445 |
| a7al2x3_c6d040e141ee4a7a | time_shuffle         | recent_oos_2026JanApr |       694 |          32 |       0.000398191 |     0.338566  |                -0.222573  |             -1.9103    |               0.504323 |
| a7al2x3_c6d040e141ee4a7a | time_shuffle         | known_may2026_stress  |       575 |          32 |       0.000445087 |     0.64131   |                 0.102004  |             -2.21029   |               0.504348 |
| a7al2x3_c6d040e141ee4a7a | symbol_shuffle       | train_2024            |       684 |          32 |       0.00178664  |     1.74745   |                 0.204675  |             -1.15171   |               0.523392 |
| a7al2x3_c6d040e141ee4a7a | symbol_shuffle       | validation_2025H1     |       696 |          32 |      -0.000844331 |    -1.37174   |                -0.505729  |             -2.03006   |               0.466954 |
| a7al2x3_c6d040e141ee4a7a | symbol_shuffle       | test_2025H2           |       696 |          32 |       0.00195371  |     2.56441   |                 0.609741  |             -1.28049   |               0.548851 |
| a7al2x3_c6d040e141ee4a7a | symbol_shuffle       | recent_oos_2026JanApr |       696 |          32 |       0.00178769  |     1.42939   |                 0.505542  |             -1.6881    |               0.530172 |
| a7al2x3_c6d040e141ee4a7a | symbol_shuffle       | known_may2026_stress  |       576 |          32 |       0.00013314  |     0.170015  |                 0.357642  |             -2.32943   |               0.501736 |
| a7al2x3_c6d040e141ee4a7a | same_family_random   | train_2024            |       696 |          32 |      -0.000237656 |    -0.241345  |                -0.0964573 |             -1.83105   |               0.488506 |
| a7al2x3_c6d040e141ee4a7a | same_family_random   | validation_2025H1     |       696 |          32 |      -0.000251346 |    -0.412099  |                -0.218005  |             -1.5336    |               0.502874 |
| a7al2x3_c6d040e141ee4a7a | same_family_random   | test_2025H2           |       696 |          32 |       0.000708411 |     0.858071  |                 0.181757  |             -1.46165   |               0.517241 |
| a7al2x3_c6d040e141ee4a7a | same_family_random   | recent_oos_2026JanApr |       696 |          32 |      -0.00234667  |    -2.16476   |                -0.833041  |             -3.01689   |               0.477011 |
| a7al2x3_c6d040e141ee4a7a | same_family_random   | known_may2026_stress  |       576 |          32 |       6.98354e-05 |     0.0821404 |                 0.119771  |             -2.03626   |               0.498264 |
| a7al2x3_c6d040e141ee4a7a | wrong_lag_future_24h | train_2024            |       684 |          32 |       0.00124196  |     0.759282  |                 0.335347  |             -1.51629   |               0.502924 |
| a7al2x3_c6d040e141ee4a7a | wrong_lag_future_24h | validation_2025H1     |       696 |          32 |      -0.00455968  |    -4.76077   |                -0.855853  |             -3.4755    |               0.428161 |
| a7al2x3_c6d040e141ee4a7a | wrong_lag_future_24h | test_2025H2           |       696 |          32 |       0.0070954   |     4.69858   |                 1.19525   |             -0.332416  |               0.522989 |
| a7al2x3_c6d040e141ee4a7a | wrong_lag_future_24h | recent_oos_2026JanApr |       696 |          32 |       0.0123282   |     5.34207   |                 1.08945   |             -0.0734775 |               0.533046 |
| a7al2x3_c6d040e141ee4a7a | wrong_lag_future_24h | known_may2026_stress  |       576 |          32 |       0.0022977   |     2.06057   |                 0.612531  |             -2.23197   |               0.548611 |
| a7al2x3_c6d040e141ee4a7a | wrong_lag_stale_168h | train_2024            |       516 |          32 |       0.000749009 |     0.538944  |                 0.114433  |             -1.48402   |               0.484496 |
| a7al2x3_c6d040e141ee4a7a | wrong_lag_stale_168h | validation_2025H1     |       696 |          32 |       0.000120215 |     0.211207  |                 0.0237026 |             -1.40821   |               0.479885 |
| a7al2x3_c6d040e141ee4a7a | wrong_lag_stale_168h | test_2025H2           |       696 |          32 |      -0.00191827  |    -2.30547   |                -0.514176  |             -1.70575   |               0.477011 |
| a7al2x3_c6d040e141ee4a7a | wrong_lag_stale_168h | recent_oos_2026JanApr |       696 |          32 |      -0.00395143  |    -3.51252   |                -0.711305  |             -2.44007   |               0.49569  |
| a7al2x3_c6d040e141ee4a7a | wrong_lag_stale_168h | known_may2026_stress  |       576 |          32 |      -0.000288309 |    -0.403144  |                -0.296737  |             -2.12837   |               0.506944 |
| a7al2x3_a685d04007266d3e | original             | train_2024            |       684 |          32 |       0.000744882 |     0.582699  |                -0.0798884 |             -1.39481   |               0.49269  |
| a7al2x3_a685d04007266d3e | original             | validation_2025H1     |       696 |          32 |       0.00044484  |     0.753682  |                 0.059463  |             -1.46927   |               0.525862 |
| a7al2x3_a685d04007266d3e | original             | test_2025H2           |       696 |          32 |       0.00418236  |     3.0949    |                 0.576253  |             -0.417274  |               0.478448 |
| a7al2x3_a685d04007266d3e | original             | recent_oos_2026JanApr |       696 |          32 |      -0.00769721  |    -5.38607   |                -1.0576    |             -2.16801   |               0.435345 |
| a7al2x3_a685d04007266d3e | original             | known_may2026_stress  |       576 |          32 |      -0.00415499  |    -4.61317   |                -0.789893  |             -2.26372   |               0.432292 |
| a7al2x3_a685d04007266d3e | one_bar_lag          | train_2024            |       683 |          32 |       0.000763312 |     0.596063  |                -0.0819879 |             -1.2531    |               0.509517 |
| a7al2x3_a685d04007266d3e | one_bar_lag          | validation_2025H1     |       696 |          32 |       0.000327909 |     0.546094  |                 0.0426261 |             -1.71947   |               0.50431  |
| a7al2x3_a685d04007266d3e | one_bar_lag          | test_2025H2           |       696 |          32 |       0.00370753  |     2.73614   |                 0.548173  |             -0.693636  |               0.474138 |
| a7al2x3_a685d04007266d3e | one_bar_lag          | recent_oos_2026JanApr |       696 |          32 |      -0.00791762  |    -5.47819   |                -1.16256   |             -2.22947   |               0.458333 |
| a7al2x3_a685d04007266d3e | one_bar_lag          | known_may2026_stress  |       576 |          32 |      -0.00380226  |    -4.23011   |                -0.710681  |             -2.31946   |               0.421875 |
| a7al2x3_a685d04007266d3e | time_shuffle         | train_2024            |       693 |          32 |       0.000529363 |     0.472406  |                -0.123275  |             -1.7131    |               0.487734 |
| a7al2x3_a685d04007266d3e | time_shuffle         | validation_2025H1     |       694 |          32 |       0.000848503 |     1.43606   |                 0.406289  |             -1.39526   |               0.514409 |
| a7al2x3_a685d04007266d3e | time_shuffle         | test_2025H2           |       691 |          32 |       0.00168323  |     1.87756   |                 0.565062  |             -1.97691   |               0.51809  |
| a7al2x3_a685d04007266d3e | time_shuffle         | recent_oos_2026JanApr |       694 |          32 |       0.00131186  |     1.18869   |                 0.511506  |             -1.52209   |               0.517291 |
| a7al2x3_a685d04007266d3e | time_shuffle         | known_may2026_stress  |       575 |          32 |      -0.000784604 |    -0.909545  |                -0.278331  |             -2.19197   |               0.486957 |
| a7al2x3_a685d04007266d3e | symbol_shuffle       | train_2024            |       684 |          32 |       0.00148906  |     1.5533    |                 0.0958424 |             -2.08996   |               0.511696 |
| a7al2x3_a685d04007266d3e | symbol_shuffle       | validation_2025H1     |       696 |          32 |       0.000278937 |     0.423474  |                -0.166996  |             -1.49949   |               0.479885 |
| a7al2x3_a685d04007266d3e | symbol_shuffle       | test_2025H2           |       696 |          32 |      -0.00210155  |    -2.31592   |                -0.228431  |             -1.91073   |               0.454023 |
| a7al2x3_a685d04007266d3e | symbol_shuffle       | recent_oos_2026JanApr |       696 |          32 |      -0.00285584  |    -2.27372   |                -0.531918  |             -2.97033   |               0.456897 |
| a7al2x3_a685d04007266d3e | symbol_shuffle       | known_may2026_stress  |       576 |          32 |       0.00156902  |     1.99867   |                 0.323726  |             -0.953704  |               0.517361 |
| a7al2x3_a685d04007266d3e | same_family_random   | train_2024            |       696 |          32 |      -0.000199307 |    -0.204315  |                -0.178257  |             -1.03196   |               0.497126 |
| a7al2x3_a685d04007266d3e | same_family_random   | validation_2025H1     |       696 |          32 |       0.00037876  |     0.558745  |                 0.163808  |             -1.73302   |               0.484195 |
| a7al2x3_a685d04007266d3e | same_family_random   | test_2025H2           |       696 |          32 |       0.000216098 |     0.213381  |                -0.0447212 |             -1.58854   |               0.489943 |
| a7al2x3_a685d04007266d3e | same_family_random   | recent_oos_2026JanApr |       696 |          32 |      -0.000878556 |    -0.776632  |                -0.376463  |             -1.92111   |               0.497126 |
| a7al2x3_a685d04007266d3e | same_family_random   | known_may2026_stress  |       576 |          32 |      -5.20898e-05 |    -0.0622425 |                -0.186068  |             -1.71901   |               0.489583 |
| a7al2x3_a685d04007266d3e | wrong_lag_future_24h | train_2024            |       684 |          32 |       0.0168339   |    13.1357    |                 2.60447   |              1.54112   |               0.717836 |
| a7al2x3_a685d04007266d3e | wrong_lag_future_24h | validation_2025H1     |       696 |          32 |       0.00403369  |     5.71629   |                 1.28004   |             -0.432463  |               0.53592  |
| a7al2x3_a685d04007266d3e | wrong_lag_future_24h | test_2025H2           |       696 |          32 |       0.0120903   |     7.88474   |                 1.71871   |              0.573902  |               0.573276 |
| a7al2x3_a685d04007266d3e | wrong_lag_future_24h | recent_oos_2026JanApr |       696 |          32 |       0.0207551   |    10.9825    |                 2.3582    |              1.28915   |               0.686782 |
| a7al2x3_a685d04007266d3e | wrong_lag_future_24h | known_may2026_stress  |       576 |          32 |       0.0103393   |    10.4452    |                 2.16133   |             -0.0948087 |               0.651042 |
| a7al2x3_a685d04007266d3e | wrong_lag_stale_168h | train_2024            |       516 |          32 |      -0.000895182 |    -0.663243  |                -0.223403  |             -1.37892   |               0.45155  |
| a7al2x3_a685d04007266d3e | wrong_lag_stale_168h | validation_2025H1     |       696 |          32 |      -0.000668043 |    -1.01323   |                -0.172461  |             -2.71951   |               0.481322 |
| a7al2x3_a685d04007266d3e | wrong_lag_stale_168h | test_2025H2           |       696 |          32 |      -0.0020117   |    -2.73901   |                -0.367437  |             -3.15339   |               0.458333 |
| a7al2x3_a685d04007266d3e | wrong_lag_stale_168h | recent_oos_2026JanApr |       696 |          32 |      -0.00257919  |    -2.31206   |                -0.624167  |             -1.91199   |               0.501437 |
| a7al2x3_a685d04007266d3e | wrong_lag_stale_168h | known_may2026_stress  |       576 |          32 |       0.00371312  |     4.01849   |                 0.789816  |             -1.31315   |               0.543403 |
| a7al2x3_8943bb8dd3c5f640 | original             | train_2024            |       528 |          32 |       0.00941848  |     5.65238   |                 1.25917   |              0.36902   |               0.575758 |
| a7al2x3_8943bb8dd3c5f640 | original             | validation_2025H1     |       696 |          32 |      -0.00179297  |    -2.183     |                -0.506468  |             -1.05617   |               0.487069 |
| a7al2x3_8943bb8dd3c5f640 | original             | test_2025H2           |       696 |          32 |      -0.00515948  |    -3.84845   |                -0.759348  |             -1.57052   |               0.400862 |
| a7al2x3_8943bb8dd3c5f640 | original             | recent_oos_2026JanApr |       696 |          32 |       0.000811039 |     0.559569  |                 0.144076  |             -0.130014  |               0.454023 |
| a7al2x3_8943bb8dd3c5f640 | original             | known_may2026_stress  |       576 |          32 |       0.00144417  |     1.59039   |                 0.315947  |             -0.0333598 |               0.552083 |
| a7al2x3_8943bb8dd3c5f640 | one_bar_lag          | train_2024            |       527 |          32 |       0.00955211  |     5.72608   |                 1.29467   |              0.381826  |               0.586338 |
| a7al2x3_8943bb8dd3c5f640 | one_bar_lag          | validation_2025H1     |       696 |          32 |      -0.00164223  |    -2.01613   |                -0.444378  |             -1.13652   |               0.485632 |
| a7al2x3_8943bb8dd3c5f640 | one_bar_lag          | test_2025H2           |       696 |          32 |      -0.00553964  |    -4.22289   |                -0.847406  |             -1.49486   |               0.400862 |
| a7al2x3_8943bb8dd3c5f640 | one_bar_lag          | recent_oos_2026JanApr |       696 |          32 |       0.00100414  |     0.691469  |                 0.166042  |             -0.148139  |               0.45977  |
| a7al2x3_8943bb8dd3c5f640 | one_bar_lag          | known_may2026_stress  |       576 |          32 |       0.00161432  |     1.77429   |                 0.344511  |             -0.0949626 |               0.552083 |

## Boundary

```text
Allowed interpretation:
  X7 can produce replay-preflight clues or holds only.

Not authorized:
  full numeric replay
  formula generation/search
  alpha proof
  shadow / paper / live
```
