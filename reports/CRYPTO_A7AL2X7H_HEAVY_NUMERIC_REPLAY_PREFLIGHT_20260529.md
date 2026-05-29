# CRYPTO A7AL-2X7H HEAVY NUMERIC REPLAY PREFLIGHT

Generated: 2026-05-29T03:18:23Z

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
  "bottom_bucket_rule": "rank_pct <= 0.10",
  "candidate_count": 56,
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
  "generated_at": "2026-05-29T03:18:23Z",
  "hours_per_split": 720,
  "label": "log_trade_close_t_plus_24h_minus_log_trade_close_t",
  "metric_rows": 1960,
  "orientation": "train_2024_original_spread_sign_only",
  "pre_may_clue_may_veto_count": 0,
  "spread_bucket_method": "cross_sectional_rank_pct_top_bottom_decile",
  "stage": "A7AL-2X7H",
  "stress_clean_clue_count": 0,
  "symbols_loaded": 96,
  "timestamps": 3481,
  "top_bucket_rule": "rank_pct >= 0.90"
}
```

## Decision Counts

| decision                       |   count |
|:-------------------------------|--------:|
| HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |      52 |
| HOLD_A7AL2X7_CONTROL_DOMINATED |       4 |

## Candidate Decisions

| candidate_id             | objective_family                   |   orientation_from_train |   oriented_validation_spread |   oriented_test_spread |   oriented_recent_spread |   oriented_may_stress_spread |   one_bar_lag_recent_oriented |   cost10_recent_proxy |   control_dominance_ratio_premay_max | pre_may_positive   | lag_ok   | may_stress_clean   | decision                       |
|:-------------------------|:-----------------------------------|-------------------------:|-----------------------------:|-----------------------:|-------------------------:|-----------------------------:|------------------------------:|----------------------:|-------------------------------------:|:-------------------|:---------|:-------------------|:-------------------------------|
| a7al2x3_c6d040e141ee4a7a | F0_OI_delta_price_interaction      |                       -1 |                 -0.00010092  |           -0.00246052  |              0.00341551  |                 -0.000346211 |                   0.003925    |           0.00141551  |                             19.2522  | False              | True     | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_a685d04007266d3e | F0_OI_delta_price_interaction      |                        1 |                  0.00162782  |           -0.000901683 |             -0.00447011  |                 -0.00179973  |                  -0.00472705  |          -0.00647011  |                              8.89742 | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_7ea2d37cbc880c31 | F0_OI_delta_price_interaction      |                       -1 |                 -0.0017345   |           -0.00217641  |              0.00286847  |                  0.00550339  |                   0.00328886  |           0.000868474 |                              7.14507 | False              | True     | True               | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_e2d80967eacd522d | F0_OI_delta_price_interaction      |                       -1 |                 -0.000486928 |            0.00227295  |              0.00533601  |                 -0.000568339 |                   0.00507227  |           0.00333601  |                             28.676   | False              | True     | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_66e1442493b16731 | F0_OI_delta_price_interaction      |                        1 |                 -0.00217252  |            0.00363313  |             -0.00107016  |                 -0.00181247  |                  -0.0010568   |          -0.00307016  |                              2.57109 | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_93c3678f22a08669 | F0_OI_delta_price_interaction      |                        1 |                 -0.000599962 |            0.00433474  |             -0.00388543  |                  5.71463e-05 |                  -0.00422599  |          -0.00588543  |                              4.04964 | False              | False    | True               | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_4cd7689ef5bcda11 | F0_OI_delta_price_interaction      |                        1 |                  0.000407642 |            0.00382777  |              0.00142155  |                  0.000272181 |                   0.00135508  |          -0.000578451 |                              6.73362 | True               | True     | True               | HOLD_A7AL2X7_CONTROL_DOMINATED |
| a7al2x3_035db391f91d7640 | F0_OI_delta_price_interaction      |                       -1 |                 -0.000138447 |           -0.000924539 |             -0.00063591  |                 -0.000984561 |                  -0.000785774 |          -0.00263591  |                             13.3256  | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_8943bb8dd3c5f640 | F1_OI_basis_premium_interaction    |                        1 |                  0.00237402  |           -0.00632791  |             -0.00678376  |                 -0.00579553  |                  -0.0064809   |          -0.00878376  |                              1.56168 | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_8133b78c17250336 | F1_OI_basis_premium_interaction    |                       -1 |                  0.00378307  |           -0.00423047  |             -0.00558154  |                 -0.00261723  |                  -0.00555136  |          -0.00758154  |                              1.68284 | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_23f49936bc301294 | F1_OI_basis_premium_interaction    |                        1 |                  0.0016235   |           -0.00594009  |             -0.00432741  |                 -0.0071082   |                  -0.00420963  |          -0.00632741  |                              2.00809 | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_4529f2a727b6c66c | F1_OI_basis_premium_interaction    |                        1 |                  0.00226663  |           -0.00278772  |             -0.00232642  |                 -0.00349867  |                  -0.00213148  |          -0.00432642  |                              1.48908 | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_35d4fbc6ca2699b6 | F1_OI_basis_premium_interaction    |                        1 |                  0.00225312  |           -0.00634725  |             -0.00297288  |                 -0.00190896  |                  -0.00281188  |          -0.00497288  |                              2.18586 | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_c4069bf78415ab2e | F1_OI_basis_premium_interaction    |                        1 |                  0.0012585   |           -0.00465068  |             -0.00774894  |                 -0.00206576  |                  -0.00812667  |          -0.00974894  |                              4.16374 | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_4059c8d99e2021eb | F1_OI_basis_premium_interaction    |                        1 |                  0.00137447  |           -0.00543118  |             -0.00861511  |                 -0.00185371  |                  -0.00869269  |          -0.0106151   |                              2.87787 | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_9733cada7099c087 | F1_OI_basis_premium_interaction    |                        1 |                  0.00265368  |           -0.00376632  |             -0.00110775  |                 -0.00262022  |                  -0.00121472  |          -0.00310775  |                             10.3384  | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_dcf6359c32accfb4 | F2_OI_funding_crowding_interaction |                        1 |                nan           |          nan           |            nan           |                nan           |                 nan           |         nan           |                            nan       | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_0bd3d497403b3991 | F2_OI_funding_crowding_interaction |                        1 |                nan           |          nan           |            nan           |                nan           |                 nan           |         nan           |                            nan       | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_49318bc4563b3038 | F2_OI_funding_crowding_interaction |                        1 |                nan           |          nan           |            nan           |                nan           |                 nan           |         nan           |                            nan       | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_2a3e04a7ef01524d | F2_OI_funding_crowding_interaction |                        1 |                nan           |          nan           |            nan           |                nan           |                 nan           |         nan           |                            nan       | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_03902ab9f8781dff | F2_OI_funding_crowding_interaction |                        1 |                nan           |          nan           |            nan           |                nan           |                 nan           |         nan           |                            nan       | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_9794f9f4dde82087 | F2_OI_funding_crowding_interaction |                        1 |                nan           |          nan           |            nan           |                nan           |                 nan           |         nan           |                            nan       | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_4ffc6837ac0783ef | F2_OI_funding_crowding_interaction |                        1 |                nan           |          nan           |            nan           |                nan           |                 nan           |         nan           |                            nan       | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_3453ef7a612e7a2f | F2_OI_funding_crowding_interaction |                        1 |                nan           |          nan           |            nan           |                nan           |                 nan           |         nan           |                            nan       | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_93725c2d40077dd9 | F3_positioning_divergence          |                       -1 |                 -9.33293e-05 |           -0.00225509  |             -0.00707209  |                 -0.00322062  |                  -0.0067415   |          -0.00907209  |                            140.095   | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_afebb1f45f8929ea | F3_positioning_divergence          |                       -1 |                 -0.000117489 |            0.000987799 |             -0.00139135  |                 -0.0025042   |                  -0.00146487  |          -0.00339135  |                             17.4465  | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_0cff1969d14056bc | F3_positioning_divergence          |                       -1 |                  0.00159394  |            0.0028063   |              0.00977765  |                 -0.00094508  |                   0.00977837  |           0.00777765  |                              5.77899 | True               | True     | False              | HOLD_A7AL2X7_CONTROL_DOMINATED |
| a7al2x3_5d6c524b5728d76d | F3_positioning_divergence          |                       -1 |                  0.000380945 |           -0.00126415  |             -0.00480062  |                  0.00301746  |                  -0.00475265  |          -0.00680062  |                              4.21029 | False              | False    | True               | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_90f96f99f826374d | F3_positioning_divergence          |                        1 |                  0.00216466  |            0.000117617 |              0.00399817  |                  0.00414578  |                   0.00372821  |           0.00199817  |                             81.0716  | True               | True     | True               | HOLD_A7AL2X7_CONTROL_DOMINATED |
| a7al2x3_6f9b57cfb28def3d | F3_positioning_divergence          |                        1 |                 -0.00112565  |            0.00189573  |              0.00791554  |                  0.00067311  |                   0.00776522  |           0.00591554  |                             12.5131  | False              | True     | True               | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_da77f7acad8f2253 | F3_positioning_divergence          |                        1 |                  0.000255011 |            7.90848e-05 |              0.00687252  |                  0.000207004 |                   0.00661434  |           0.00487252  |                            102.39    | True               | True     | True               | HOLD_A7AL2X7_CONTROL_DOMINATED |
| a7al2x3_8cd55bb4dcd9ea8d | F3_positioning_divergence          |                       -1 |                 -0.000395036 |            0.000216268 |             -0.00776444  |                  0.000693213 |                  -0.00696776  |          -0.00976444  |                             44.4823  | False              | False    | True               | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_1fd71f89fcb97240 | F4_OI_taker_flow_interaction       |                       -1 |                 -0.000633213 |           -9.89247e-05 |              0.00114308  |                  0.000789696 |                   0.00119042  |          -0.000856922 |                             12.8398  | False              | True     | True               | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_a551e0d946a6abf3 | F4_OI_taker_flow_interaction       |                       -1 |                 -0.000565645 |            0.00121839  |              0.000998019 |                  2.55579e-05 |                   0.00078344  |          -0.00100198  |                             10.6493  | False              | True     | True               | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_9d7989b8d4655bf1 | F4_OI_taker_flow_interaction       |                        1 |                  0.000612324 |           -0.000898716 |             -0.00148785  |                 -0.000449228 |                  -0.00162743  |          -0.00348785  |                              4.65743 | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_e5af54998a54bc71 | F4_OI_taker_flow_interaction       |                        1 |                  0.000328164 |            0.00158688  |             -0.000832883 |                 -0.000940755 |                  -0.00131369  |          -0.00283288  |                              6.12659 | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_694ea01b8dc33dd4 | F4_OI_taker_flow_interaction       |                       -1 |                 -0.00114736  |            0.000408002 |              0.000279197 |                  0.000690802 |                   0.00015185  |          -0.0017208   |                             10.1772  | False              | True     | True               | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_d44b1d21d537c838 | F4_OI_taker_flow_interaction       |                       -1 |                 -0.000284843 |           -0.000751725 |              0.00108857  |                  0.00145201  |                   0.000945384 |          -0.000911427 |                             10.7647  | False              | True     | True               | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_907e3c49019029cc | F4_OI_taker_flow_interaction       |                       -1 |                  0.000781608 |           -0.000157121 |             -0.000791677 |                 -0.000222631 |                  -0.000603307 |          -0.00279168  |                             25.4355  | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_7f6ff1bafbd2c316 | F4_OI_taker_flow_interaction       |                       -1 |                  0.00079828  |           -0.002682    |             -0.00085371  |                  0.000904223 |                  -0.000837268 |          -0.00285371  |                              3.99523 | False              | False    | True               | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_9add29eae207e174 | F5_OI_upper_regime_interaction     |                        1 |                  0.000275838 |           -0.00160991  |             -0.00148087  |                nan           |                  -0.00128097  |          -0.00348087  |                             13.6079  | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_d294deb3ca25cf27 | F5_OI_upper_regime_interaction     |                        1 |                  0.000275838 |           -0.00160991  |             -0.00148087  |                nan           |                  -0.00128097  |          -0.00348087  |                             13.6079  | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_c23082c0a63a46bd | F5_OI_upper_regime_interaction     |                        1 |                  0.000275838 |           -0.00160991  |             -0.00148087  |                nan           |                  -0.00128097  |          -0.00348087  |                             13.6079  | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_5e16028aa4a04eb5 | F5_OI_upper_regime_interaction     |                        1 |                  0.000275838 |           -0.00160991  |             -0.00148087  |                nan           |                  -0.00128097  |          -0.00348087  |                             13.6079  | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_eeff378890468230 | F5_OI_upper_regime_interaction     |                        1 |                  0.00183926  |           -0.000167945 |             -0.00332708  |                nan           |                  -0.0036028   |          -0.00532708  |                             35.5124  | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_49640239a5937d81 | F5_OI_upper_regime_interaction     |                        1 |                  0.00362502  |           -0.00263991  |              0.000362343 |                nan           |                   0.00047425  |          -0.00163766  |                             47.0752  | False              | True     | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_2fce75f307a1b1c7 | F5_OI_upper_regime_interaction     |                        1 |                  0.00462807  |           -0.00377027  |             -0.00456118  |                nan           |                  -0.00456848  |          -0.00656118  |                              6.85282 | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_54f5361a609798fc | F5_OI_upper_regime_interaction     |                        1 |                  0.0031998   |           -0.000533409 |             -0.00517394  |                nan           |                  -0.00477953  |          -0.00717394  |                              4.91468 | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_6425856b9df4b997 | F6_OI_latent_state_interaction     |                        1 |                nan           |          nan           |            nan           |                nan           |                 nan           |         nan           |                            nan       | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_f726e8031e11a5c6 | F6_OI_latent_state_interaction     |                        1 |                nan           |          nan           |            nan           |                nan           |                 nan           |         nan           |                            nan       | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_bc8ed4094566ea5e | F6_OI_latent_state_interaction     |                       -1 |                nan           |           -0.000246426 |            nan           |                 -0.000498201 |                 nan           |         nan           |                             45.9885  | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_67d3a9b6da05c211 | F6_OI_latent_state_interaction     |                        1 |                nan           |          nan           |            nan           |                nan           |                 nan           |         nan           |                            nan       | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_3cb1db3cafe85fa0 | F6_OI_latent_state_interaction     |                        1 |                nan           |          nan           |            nan           |                nan           |                 nan           |         nan           |                            nan       | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_aaa82dfd8a7c3555 | F6_OI_latent_state_interaction     |                        1 |                nan           |          nan           |            nan           |                nan           |                 nan           |         nan           |                            nan       | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_c73e0ebc3866e01e | F6_OI_latent_state_interaction     |                        1 |                nan           |          nan           |            nan           |                nan           |                 nan           |         nan           |                            nan       | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |
| a7al2x3_42246afae2fc6cd4 | F6_OI_latent_state_interaction     |                        1 |                nan           |          nan           |            nan           |                nan           |                 nan           |         nan           |                            nan       | False              | False    | False              | HOLD_A7AL2X7_PRE_MAY_UNSTABLE  |

## Metrics Preview

| candidate_id             | variant              | split                 |   n_dates |   avg_n_obs |   mean_spread_24h |   naive_tstat |   nonoverlap_median_tstat |   nonoverlap_min_tstat |   positive_spread_rate |
|:-------------------------|:---------------------|:----------------------|----------:|------------:|------------------:|--------------:|--------------------------:|-----------------------:|-----------------------:|
| a7al2x3_c6d040e141ee4a7a | original             | train_2024            |       684 |          96 |      -0.00118298  |    -1.27289   |               -0.377073   |              -2.39946  |               0.45614  |
| a7al2x3_c6d040e141ee4a7a | original             | validation_2025H1     |       696 |          96 |       0.00010092  |     0.198809  |                0.250423   |              -1.73944  |               0.502874 |
| a7al2x3_c6d040e141ee4a7a | original             | test_2025H2           |       696 |          96 |       0.00246052  |     3.83878   |                0.93371    |              -1.17859  |               0.564655 |
| a7al2x3_c6d040e141ee4a7a | original             | recent_oos_2026JanApr |       696 |          96 |      -0.00341551  |    -3.64126   |               -0.754591   |              -2.26735  |               0.420977 |
| a7al2x3_c6d040e141ee4a7a | original             | known_may2026_stress  |       576 |          96 |       0.000346211 |     0.532091  |                0.0601609  |              -2.3194   |               0.513889 |
| a7al2x3_c6d040e141ee4a7a | one_bar_lag          | train_2024            |       683 |          96 |      -0.00113941  |    -1.23051   |               -0.264881   |              -1.69643  |               0.449488 |
| a7al2x3_c6d040e141ee4a7a | one_bar_lag          | validation_2025H1     |       696 |          96 |      -1.43233e-05 |    -0.0282338 |                0.0788199  |              -2.2943   |               0.502874 |
| a7al2x3_c6d040e141ee4a7a | one_bar_lag          | test_2025H2           |       696 |          96 |       0.00235751  |     3.65973   |                0.841577   |              -0.736028 |               0.561782 |
| a7al2x3_c6d040e141ee4a7a | one_bar_lag          | recent_oos_2026JanApr |       696 |          96 |      -0.003925    |    -4.25928   |               -1.00088    |              -2.01051  |               0.422414 |
| a7al2x3_c6d040e141ee4a7a | one_bar_lag          | known_may2026_stress  |       576 |          96 |       0.000100177 |     0.15256   |               -0.295138   |              -2.29758  |               0.515625 |
| a7al2x3_c6d040e141ee4a7a | time_shuffle         | train_2024            |       694 |          96 |       0.000580132 |     0.690387  |                0.237184   |              -1.99989  |               0.508646 |
| a7al2x3_c6d040e141ee4a7a | time_shuffle         | validation_2025H1     |       693 |          96 |       0.000599354 |     1.32679   |                0.183838   |              -2.9735   |               0.505051 |
| a7al2x3_c6d040e141ee4a7a | time_shuffle         | test_2025H2           |       692 |          96 |       6.65688e-05 |     0.121549  |               -0.0623838  |              -1.37849  |               0.518786 |
| a7al2x3_c6d040e141ee4a7a | time_shuffle         | recent_oos_2026JanApr |       694 |          96 |      -0.000140226 |    -0.236972  |               -0.369827   |              -2.79512  |               0.478386 |
| a7al2x3_c6d040e141ee4a7a | time_shuffle         | known_may2026_stress  |       575 |          96 |      -7.63545e-05 |    -0.14503   |                0.0126043  |              -2.19272  |               0.502609 |
| a7al2x3_c6d040e141ee4a7a | symbol_shuffle       | train_2024            |       684 |          96 |       0.00109009  |     2.03103   |                0.489019   |              -1.95315  |               0.527778 |
| a7al2x3_c6d040e141ee4a7a | symbol_shuffle       | validation_2025H1     |       696 |          96 |      -0.000140442 |    -0.330949  |                0.14603    |              -1.88623  |               0.49569  |
| a7al2x3_c6d040e141ee4a7a | symbol_shuffle       | test_2025H2           |       696 |          96 |      -0.00182842  |    -2.97199   |               -0.679009   |              -2.56512  |               0.409483 |
| a7al2x3_c6d040e141ee4a7a | symbol_shuffle       | recent_oos_2026JanApr |       696 |          96 |      -0.000475888 |    -0.436916  |               -0.440884   |              -1.39264  |               0.527299 |
| a7al2x3_c6d040e141ee4a7a | symbol_shuffle       | known_may2026_stress  |       576 |          96 |      -0.00145243  |    -2.35184   |               -0.566005   |              -2.02332  |               0.458333 |
| a7al2x3_c6d040e141ee4a7a | same_family_random   | train_2024            |       696 |          96 |      -0.000503356 |    -0.797422  |               -0.253136   |              -2.58917  |               0.491379 |
| a7al2x3_c6d040e141ee4a7a | same_family_random   | validation_2025H1     |       696 |          96 |      -0.000365465 |    -0.958652  |                0.146388   |              -2.60667  |               0.508621 |
| a7al2x3_c6d040e141ee4a7a | same_family_random   | test_2025H2           |       696 |          96 |       0.000367201 |     0.810722  |                0.244375   |              -1.57896  |               0.488506 |
| a7al2x3_c6d040e141ee4a7a | same_family_random   | recent_oos_2026JanApr |       696 |          96 |       0.000909608 |     1.10337   |                0.0226276  |              -2.14419  |               0.522989 |
| a7al2x3_c6d040e141ee4a7a | same_family_random   | known_may2026_stress  |       576 |          96 |       0.00166843  |     2.57309   |                0.480923   |              -1.44793  |               0.574653 |
| a7al2x3_c6d040e141ee4a7a | wrong_lag_future_24h | train_2024            |       684 |          96 |      -0.00465645  |    -4.2565    |               -0.841746   |              -3.02609  |               0.451754 |
| a7al2x3_c6d040e141ee4a7a | wrong_lag_future_24h | validation_2025H1     |       696 |          96 |      -0.00194293  |    -3.17359   |               -0.85958    |              -2.25714  |               0.479885 |
| a7al2x3_c6d040e141ee4a7a | wrong_lag_future_24h | test_2025H2           |       696 |          96 |       0.00165316  |     1.81198   |                0.387962   |              -1.05329  |               0.475575 |
| a7al2x3_c6d040e141ee4a7a | wrong_lag_future_24h | recent_oos_2026JanApr |       696 |          96 |       0.00277403  |     1.48468   |                0.194567   |              -1.26542  |               0.497126 |
| a7al2x3_c6d040e141ee4a7a | wrong_lag_future_24h | known_may2026_stress  |       576 |          96 |      -0.000222458 |    -0.202528  |                0.156222   |              -1.38374  |               0.493056 |
| a7al2x3_c6d040e141ee4a7a | wrong_lag_stale_168h | train_2024            |       516 |          96 |      -0.00013969  |    -0.174103  |                0.0927135  |              -2.50213  |               0.486434 |
| a7al2x3_c6d040e141ee4a7a | wrong_lag_stale_168h | validation_2025H1     |       696 |          96 |       0.000254486 |     0.613269  |                0.0462744  |              -1.84408  |               0.524425 |
| a7al2x3_c6d040e141ee4a7a | wrong_lag_stale_168h | test_2025H2           |       696 |          96 |      -0.001626    |    -3.02372   |               -0.643621   |              -3.74207  |               0.456897 |
| a7al2x3_c6d040e141ee4a7a | wrong_lag_stale_168h | recent_oos_2026JanApr |       696 |          96 |      -0.00176009  |    -2.22204   |               -0.420196   |              -3.01323  |               0.436782 |
| a7al2x3_c6d040e141ee4a7a | wrong_lag_stale_168h | known_may2026_stress  |       576 |          96 |      -0.000785547 |    -1.40464   |               -0.272855   |              -1.50007  |               0.482639 |
| a7al2x3_a685d04007266d3e | original             | train_2024            |       684 |          96 |       0.000170026 |     0.210094  |               -0.0734668  |              -1.55224  |               0.5      |
| a7al2x3_a685d04007266d3e | original             | validation_2025H1     |       696 |          96 |       0.00162782  |     3.47939   |                0.569925   |              -0.709568 |               0.548851 |
| a7al2x3_a685d04007266d3e | original             | test_2025H2           |       696 |          96 |      -0.000901683 |    -1.46615   |               -0.329101   |              -1.21834  |               0.405172 |
| a7al2x3_a685d04007266d3e | original             | recent_oos_2026JanApr |       696 |          96 |      -0.00447011  |    -4.48706   |               -0.846495   |              -2.02049  |               0.429598 |
| a7al2x3_a685d04007266d3e | original             | known_may2026_stress  |       576 |          96 |      -0.00179973  |    -2.55777   |               -0.551183   |              -1.87747  |               0.460069 |
| a7al2x3_a685d04007266d3e | one_bar_lag          | train_2024            |       683 |          96 |       0.000154519 |     0.189411  |               -0.0326507  |              -1.27026  |               0.491947 |
| a7al2x3_a685d04007266d3e | one_bar_lag          | validation_2025H1     |       696 |          96 |       0.00174264  |     3.68992   |                0.706868   |              -0.339203 |               0.553161 |
| a7al2x3_a685d04007266d3e | one_bar_lag          | test_2025H2           |       696 |          96 |      -0.000863141 |    -1.38044   |               -0.237781   |              -1.47518  |               0.41523  |
| a7al2x3_a685d04007266d3e | one_bar_lag          | recent_oos_2026JanApr |       696 |          96 |      -0.00472705  |    -4.7258    |               -1.0887     |              -2.66572  |               0.435345 |
| a7al2x3_a685d04007266d3e | one_bar_lag          | known_may2026_stress  |       576 |          96 |      -0.00183906  |    -2.65163   |               -0.579314   |              -1.772    |               0.475694 |
| a7al2x3_a685d04007266d3e | time_shuffle         | train_2024            |       694 |          96 |       0.00024745  |     0.363731  |                0.0392586  |              -0.931117 |               0.491354 |
| a7al2x3_a685d04007266d3e | time_shuffle         | validation_2025H1     |       690 |          96 |      -0.00010137  |    -0.243654  |                0.0394474  |              -2.05574  |               0.511594 |
| a7al2x3_a685d04007266d3e | time_shuffle         | test_2025H2           |       694 |          96 |      -0.000526257 |    -1.04293   |               -0.0818184  |              -2.92297  |               0.461095 |
| a7al2x3_a685d04007266d3e | time_shuffle         | recent_oos_2026JanApr |       696 |          96 |      -0.00161085  |    -2.14724   |               -0.418993   |              -3.23749  |               0.448276 |
| a7al2x3_a685d04007266d3e | time_shuffle         | known_may2026_stress  |       575 |          96 |       0.000799973 |     1.34273   |                0.449164   |              -2.5442   |               0.509565 |
| a7al2x3_a685d04007266d3e | symbol_shuffle       | train_2024            |       684 |          96 |      -0.000380209 |    -0.619113  |               -0.19259    |              -1.33439  |               0.523392 |
| a7al2x3_a685d04007266d3e | symbol_shuffle       | validation_2025H1     |       696 |          96 |       0.000181287 |     0.447258  |                0.0336561  |              -0.791452 |               0.508621 |
| a7al2x3_a685d04007266d3e | symbol_shuffle       | test_2025H2           |       696 |          96 |       0.00231223  |     4.5683    |                0.832328   |              -0.632168 |               0.557471 |
| a7al2x3_a685d04007266d3e | symbol_shuffle       | recent_oos_2026JanApr |       696 |          96 |       0.00108391  |     0.986739  |                0.0582638  |              -1.65412  |               0.471264 |
| a7al2x3_a685d04007266d3e | symbol_shuffle       | known_may2026_stress  |       576 |          96 |       0.00027101  |     0.41233   |               -0.00449343 |              -1.26641  |               0.517361 |
| a7al2x3_a685d04007266d3e | same_family_random   | train_2024            |       696 |          96 |       0.00131416  |     1.94723   |                0.471799   |              -1.16042  |               0.527299 |
| a7al2x3_a685d04007266d3e | same_family_random   | validation_2025H1     |       696 |          96 |       9.99957e-05 |     0.250826  |               -0.0525108  |              -1.60829  |               0.492816 |
| a7al2x3_a685d04007266d3e | same_family_random   | test_2025H2           |       696 |          96 |      -0.000679083 |    -1.34699   |               -0.300832   |              -2.67974  |               0.5      |
| a7al2x3_a685d04007266d3e | same_family_random   | recent_oos_2026JanApr |       696 |          96 |      -0.000492694 |    -0.680461  |                0.00312968 |              -2.08392  |               0.479885 |
| a7al2x3_a685d04007266d3e | same_family_random   | known_may2026_stress  |       576 |          96 |       8.90904e-05 |     0.141875  |               -0.109825   |              -2.30939  |               0.510417 |
| a7al2x3_a685d04007266d3e | wrong_lag_future_24h | train_2024            |       684 |          96 |       0.0128714   |    16.2889    |                3.23407    |               1.76249  |               0.739766 |
| a7al2x3_a685d04007266d3e | wrong_lag_future_24h | validation_2025H1     |       696 |          96 |       0.00833111  |    15.7031    |                3.20267    |               1.91757  |               0.71408  |
| a7al2x3_a685d04007266d3e | wrong_lag_future_24h | test_2025H2           |       696 |          96 |       0.00802265  |    10.1615    |                2.08028    |               1.01525  |               0.637931 |
| a7al2x3_a685d04007266d3e | wrong_lag_future_24h | recent_oos_2026JanApr |       696 |          96 |       0.0249767   |    15.8726    |                3.44554    |               2.48658  |               0.79454  |
| a7al2x3_a685d04007266d3e | wrong_lag_future_24h | known_may2026_stress  |       576 |          96 |       0.0165832   |    18.6603    |                3.97017    |               2.62224  |               0.784722 |
| a7al2x3_a685d04007266d3e | wrong_lag_stale_168h | train_2024            |       516 |          96 |       0.000433072 |     0.616449  |                0.199469   |              -1.27725  |               0.474806 |
| a7al2x3_a685d04007266d3e | wrong_lag_stale_168h | validation_2025H1     |       696 |          96 |       0.000681126 |     1.43155   |                0.275126   |              -1.63055  |               0.533046 |
| a7al2x3_a685d04007266d3e | wrong_lag_stale_168h | test_2025H2           |       696 |          96 |      -0.00236351  |    -5.08497   |               -0.737951   |              -4.04011  |               0.395115 |
| a7al2x3_a685d04007266d3e | wrong_lag_stale_168h | recent_oos_2026JanApr |       696 |          96 |      -0.00159991  |    -2.30708   |               -0.154843   |              -2.53265  |               0.494253 |
| a7al2x3_a685d04007266d3e | wrong_lag_stale_168h | known_may2026_stress  |       576 |          96 |      -0.000232902 |    -0.375537  |                0.0653437  |              -1.47713  |               0.479167 |
| a7al2x3_7ea2d37cbc880c31 | original             | train_2024            |       684 |          96 |      -0.000351152 |    -0.393288  |               -0.0777011  |              -1.15495  |               0.460526 |
| a7al2x3_7ea2d37cbc880c31 | original             | validation_2025H1     |       696 |          96 |       0.0017345   |     3.30524   |                0.588429   |              -1.06984  |               0.534483 |
| a7al2x3_7ea2d37cbc880c31 | original             | test_2025H2           |       696 |          96 |       0.00217641  |     3.34796   |                0.621441   |              -0.359643 |               0.478448 |
| a7al2x3_7ea2d37cbc880c31 | original             | recent_oos_2026JanApr |       696 |          96 |      -0.00286847  |    -3.12781   |               -0.854069   |              -1.6328   |               0.446839 |
| a7al2x3_7ea2d37cbc880c31 | original             | known_may2026_stress  |       576 |          96 |      -0.00550339  |    -8.59928   |               -1.66338    |              -3.45372  |               0.383681 |
| a7al2x3_7ea2d37cbc880c31 | one_bar_lag          | train_2024            |       683 |          96 |      -0.000571942 |    -0.650428  |               -0.124258   |              -1.2402   |               0.471449 |
| a7al2x3_7ea2d37cbc880c31 | one_bar_lag          | validation_2025H1     |       696 |          96 |       0.00145467  |     2.7436    |                0.679754   |              -1.00741  |               0.515805 |
| a7al2x3_7ea2d37cbc880c31 | one_bar_lag          | test_2025H2           |       696 |          96 |       0.00190129  |     2.92842   |                0.520785   |              -0.818792 |               0.477011 |
| a7al2x3_7ea2d37cbc880c31 | one_bar_lag          | recent_oos_2026JanApr |       696 |          96 |      -0.00328886  |    -3.64992   |               -0.822805   |              -1.97165  |               0.445402 |
| a7al2x3_7ea2d37cbc880c31 | one_bar_lag          | known_may2026_stress  |       576 |          96 |      -0.00517092  |    -8.06747   |               -1.56767    |              -2.95643  |               0.376736 |

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
