# CRYPTO A7AL-2X7HF HEAVY REPLAY PREFLIGHT FORENSIC

Generated: 2026-05-29T03:19:43Z

## Decision

`HOLD_A7AL2X7F_OBJECTIVE_FAMILY_NUMERIC_EVIDENCE_WEAK`

X7F is a forensic audit over existing X7 artifacts. It does not generate formulas, run search, train a model, or authorize replay promotion.

## Manifest

```json
{
  "allowed_next": [
    "objective-family redesign away from current OI/positioning pool",
    "broader non-OI objective family contract if additional exploration is authorized"
  ],
  "authorizes_alpha_proof": false,
  "authorizes_formula_generation": false,
  "authorizes_full_numeric_replay": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "no_stress_clean_preflight_clues",
    "matched_controls_often_dominate",
    "some_families_sparse_under_smoke_subset"
  ],
  "candidate_count": 56,
  "control_dominated_count": 41,
  "decision": "HOLD_A7AL2X7F_OBJECTIVE_FAMILY_NUMERIC_EVIDENCE_WEAK",
  "executes_formula_generation": false,
  "executes_replay": false,
  "executes_search": false,
  "executes_training": false,
  "generated_at": "2026-05-29T03:19:43Z",
  "missing_or_sparse_count": 16,
  "pre_may_all_positive_count": 4,
  "source_decision": "HOLD_A7AL2X7_NO_CLEAN_NUMERIC_PREFLIGHT_CLUES",
  "source_stage": "A7AL-2X7H",
  "stage": "A7AL-2X7HF",
  "stress_clean_preflight_clue_count": 0
}
```

## Failure Roots

| failure_root                          |   candidate_count |
|:--------------------------------------|------------------:|
| pre_may_direction_unstable            |                36 |
| metric_missing_or_sparse_smoke_window |                16 |
| matched_control_dominated             |                 4 |

## Split Alignment

| split                 |   candidate_count |   finite_count |   positive_count |   positive_rate |   median_oriented_spread |   mean_oriented_spread |
|:----------------------|------------------:|---------------:|-----------------:|----------------:|-------------------------:|-----------------------:|
| validation_2025H1     |                56 |             40 |               26 |        0.464286 |              0.000354554 |            0.000783426 |
| test_2025H2           |                56 |             41 |               13 |        0.232143 |             -0.000901683 |           -0.00108452  |
| recent_oos_2026JanApr |                56 |             40 |               13 |        0.232143 |             -0.00143611  |           -0.00120073  |
| known_may2026_stress  |                56 |             33 |               13 |        0.232143 |             -0.000498201 |           -0.000706931 |

## Objective Family Summary

| objective_family                   |   candidate_count |   pre_may_all_positive |   may_stress_clean |   control_dominated |   missing_or_sparse |   median_max_control_ratio |   median_recent_oriented_spread | failure_roots                                         |
|:-----------------------------------|------------------:|-----------------------:|-------------------:|--------------------:|--------------------:|---------------------------:|--------------------------------:|:------------------------------------------------------|
| F0_OI_delta_price_interaction      |                 8 |                      1 |                  3 |                   8 |                   0 |                    8.02125 |                      0.00039282 | matched_control_dominated\|pre_may_direction_unstable |
| F1_OI_basis_premium_interaction    |                 8 |                      0 |                  0 |                   8 |                   0 |                    2.09697 |                     -0.00495448 | pre_may_direction_unstable                            |
| F2_OI_funding_crowding_interaction |                 8 |                      0 |                  0 |                   0 |                   8 |                  nan       |                    nan          | metric_missing_or_sparse_smoke_window                 |
| F3_positioning_divergence          |                 8 |                      3 |                  5 |                   8 |                   0 |                   30.9644  |                      0.00130341 | matched_control_dominated\|pre_may_direction_unstable |
| F4_OI_taker_flow_interaction       |                 8 |                      0 |                  5 |                   8 |                   0 |                   10.4132  |                     -0.00025624 | pre_may_direction_unstable                            |
| F5_OI_upper_regime_interaction     |                 8 |                      0 |                  0 |                   8 |                   0 |                   13.6079  |                     -0.00148087 | pre_may_direction_unstable                            |
| F6_OI_latent_state_interaction     |                 8 |                      0 |                  0 |                   1 |                   8 |                   45.9885  |                    nan          | metric_missing_or_sparse_smoke_window                 |

## Candidate Forensic Detail

| candidate_id             | objective_family                   | pre_may_sign_pattern   |   pre_may_positive_splits |   recent_oriented_spread |   one_bar_recent_retention |   cost10_recent_proxy |   max_control_ratio_premay | max_control_variant   | max_control_split     |   may_oriented_spread | failure_root                          |
|:-------------------------|:-----------------------------------|:-----------------------|--------------------------:|-------------------------:|---------------------------:|----------------------:|---------------------------:|:----------------------|:----------------------|----------------------:|:--------------------------------------|
| a7al2x3_c6d040e141ee4a7a | F0_OI_delta_price_interaction      | -/-/+                  |                         1 |              0.00341551  |                   1.14917  |           0.00141551  |                   19.2522  | wrong_lag_future_24h  | validation_2025H1     |          -0.000346211 | pre_may_direction_unstable            |
| a7al2x3_a685d04007266d3e | F0_OI_delta_price_interaction      | +/-/-                  |                         1 |             -0.00447011  |                   1.05748  |          -0.00647011  |                    8.89742 | wrong_lag_future_24h  | test_2025H2           |          -0.00179973  | pre_may_direction_unstable            |
| a7al2x3_7ea2d37cbc880c31 | F0_OI_delta_price_interaction      | -/-/+                  |                         1 |              0.00286847  |                   1.14655  |           0.000868474 |                    7.14507 | wrong_lag_future_24h  | recent_oos_2026JanApr |           0.00550339  | pre_may_direction_unstable            |
| a7al2x3_e2d80967eacd522d | F0_OI_delta_price_interaction      | -/+/+                  |                         2 |              0.00533601  |                   0.950573 |           0.00333601  |                   28.676   | wrong_lag_future_24h  | validation_2025H1     |          -0.000568339 | pre_may_direction_unstable            |
| a7al2x3_66e1442493b16731 | F0_OI_delta_price_interaction      | -/+/-                  |                         1 |             -0.00107016  |                   0.987519 |          -0.00307016  |                    2.57109 | wrong_lag_future_24h  | recent_oos_2026JanApr |          -0.00181247  | pre_may_direction_unstable            |
| a7al2x3_93c3678f22a08669 | F0_OI_delta_price_interaction      | -/+/-                  |                         1 |             -0.00388543  |                   1.08765  |          -0.00588543  |                    4.04964 | symbol_shuffle        | validation_2025H1     |           5.71463e-05 | pre_may_direction_unstable            |
| a7al2x3_4cd7689ef5bcda11 | F0_OI_delta_price_interaction      | +/+/+                  |                         3 |              0.00142155  |                   0.953241 |          -0.000578451 |                    6.73362 | wrong_lag_future_24h  | validation_2025H1     |           0.000272181 | matched_control_dominated             |
| a7al2x3_035db391f91d7640 | F0_OI_delta_price_interaction      | -/-/-                  |                         0 |             -0.00063591  |                   1.23567  |          -0.00263591  |                   13.3256  | wrong_lag_future_24h  | validation_2025H1     |          -0.000984561 | pre_may_direction_unstable            |
| a7al2x3_8943bb8dd3c5f640 | F1_OI_basis_premium_interaction    | +/-/-                  |                         1 |             -0.00678376  |                   0.955356 |          -0.00878376  |                    1.56168 | wrong_lag_future_24h  | validation_2025H1     |          -0.00579553  | pre_may_direction_unstable            |
| a7al2x3_8133b78c17250336 | F1_OI_basis_premium_interaction    | +/-/-                  |                         1 |             -0.00558154  |                   0.994593 |          -0.00758154  |                    1.68284 | wrong_lag_future_24h  | validation_2025H1     |          -0.00261723  | pre_may_direction_unstable            |
| a7al2x3_23f49936bc301294 | F1_OI_basis_premium_interaction    | +/-/-                  |                         1 |             -0.00432741  |                   0.972781 |          -0.00632741  |                    2.00809 | wrong_lag_stale_168h  | validation_2025H1     |          -0.0071082   | pre_may_direction_unstable            |
| a7al2x3_4529f2a727b6c66c | F1_OI_basis_premium_interaction    | +/-/-                  |                         1 |             -0.00232642  |                   0.916207 |          -0.00432642  |                    1.48908 | wrong_lag_stale_168h  | recent_oos_2026JanApr |          -0.00349867  | pre_may_direction_unstable            |
| a7al2x3_35d4fbc6ca2699b6 | F1_OI_basis_premium_interaction    | +/-/-                  |                         1 |             -0.00297288  |                   0.945844 |          -0.00497288  |                    2.18586 | wrong_lag_future_24h  | validation_2025H1     |          -0.00190896  | pre_may_direction_unstable            |
| a7al2x3_c4069bf78415ab2e | F1_OI_basis_premium_interaction    | +/-/-                  |                         1 |             -0.00774894  |                   1.04875  |          -0.00974894  |                    4.16374 | wrong_lag_future_24h  | recent_oos_2026JanApr |          -0.00206576  | pre_may_direction_unstable            |
| a7al2x3_4059c8d99e2021eb | F1_OI_basis_premium_interaction    | +/-/-                  |                         1 |             -0.00861511  |                   1.00901  |          -0.0106151   |                    2.87787 | wrong_lag_future_24h  | recent_oos_2026JanApr |          -0.00185371  | pre_may_direction_unstable            |
| a7al2x3_9733cada7099c087 | F1_OI_basis_premium_interaction    | +/-/-                  |                         1 |             -0.00110775  |                   1.09656  |          -0.00310775  |                   10.3384  | wrong_lag_future_24h  | recent_oos_2026JanApr |          -0.00262022  | pre_may_direction_unstable            |
| a7al2x3_dcf6359c32accfb4 | F2_OI_funding_crowding_interaction | NA/NA/NA               |                         0 |            nan           |                 nan        |         nan           |                  nan       |                       |                       |         nan           | metric_missing_or_sparse_smoke_window |
| a7al2x3_0bd3d497403b3991 | F2_OI_funding_crowding_interaction | NA/NA/NA               |                         0 |            nan           |                 nan        |         nan           |                  nan       |                       |                       |         nan           | metric_missing_or_sparse_smoke_window |
| a7al2x3_49318bc4563b3038 | F2_OI_funding_crowding_interaction | NA/NA/NA               |                         0 |            nan           |                 nan        |         nan           |                  nan       |                       |                       |         nan           | metric_missing_or_sparse_smoke_window |
| a7al2x3_2a3e04a7ef01524d | F2_OI_funding_crowding_interaction | NA/NA/NA               |                         0 |            nan           |                 nan        |         nan           |                  nan       |                       |                       |         nan           | metric_missing_or_sparse_smoke_window |
| a7al2x3_03902ab9f8781dff | F2_OI_funding_crowding_interaction | NA/NA/NA               |                         0 |            nan           |                 nan        |         nan           |                  nan       |                       |                       |         nan           | metric_missing_or_sparse_smoke_window |
| a7al2x3_9794f9f4dde82087 | F2_OI_funding_crowding_interaction | NA/NA/NA               |                         0 |            nan           |                 nan        |         nan           |                  nan       |                       |                       |         nan           | metric_missing_or_sparse_smoke_window |
| a7al2x3_4ffc6837ac0783ef | F2_OI_funding_crowding_interaction | NA/NA/NA               |                         0 |            nan           |                 nan        |         nan           |                  nan       |                       |                       |         nan           | metric_missing_or_sparse_smoke_window |
| a7al2x3_3453ef7a612e7a2f | F2_OI_funding_crowding_interaction | NA/NA/NA               |                         0 |            nan           |                 nan        |         nan           |                  nan       |                       |                       |         nan           | metric_missing_or_sparse_smoke_window |
| a7al2x3_93725c2d40077dd9 | F3_positioning_divergence          | -/-/-                  |                         0 |             -0.00707209  |                   0.953253 |          -0.00907209  |                  140.095   | wrong_lag_future_24h  | validation_2025H1     |          -0.00322062  | pre_may_direction_unstable            |
| a7al2x3_afebb1f45f8929ea | F3_positioning_divergence          | -/+/-                  |                         1 |             -0.00139135  |                   1.05284  |          -0.00339135  |                   17.4465  | symbol_shuffle        | validation_2025H1     |          -0.0025042   | pre_may_direction_unstable            |
| a7al2x3_0cff1969d14056bc | F3_positioning_divergence          | +/+/+                  |                         3 |              0.00977765  |                   1.00007  |           0.00777765  |                    5.77899 | wrong_lag_future_24h  | validation_2025H1     |          -0.00094508  | matched_control_dominated             |
| a7al2x3_5d6c524b5728d76d | F3_positioning_divergence          | +/-/-                  |                         1 |             -0.00480062  |                   0.990006 |          -0.00680062  |                    4.21029 | symbol_shuffle        | validation_2025H1     |           0.00301746  | pre_may_direction_unstable            |
| a7al2x3_90f96f99f826374d | F3_positioning_divergence          | +/+/+                  |                         3 |              0.00399817  |                   0.932479 |           0.00199817  |                   81.0716  | wrong_lag_future_24h  | test_2025H2           |           0.00414578  | matched_control_dominated             |
| a7al2x3_6f9b57cfb28def3d | F3_positioning_divergence          | -/+/+                  |                         2 |              0.00791554  |                   0.981009 |           0.00591554  |                   12.5131  | wrong_lag_future_24h  | validation_2025H1     |           0.00067311  | pre_may_direction_unstable            |
| a7al2x3_da77f7acad8f2253 | F3_positioning_divergence          | +/+/+                  |                         3 |              0.00687252  |                   0.962432 |           0.00487252  |                  102.39    | wrong_lag_future_24h  | test_2025H2           |           0.000207004 | matched_control_dominated             |
| a7al2x3_8cd55bb4dcd9ea8d | F3_positioning_divergence          | -/+/-                  |                         1 |             -0.00776444  |                   0.897394 |          -0.00976444  |                   44.4823  | wrong_lag_future_24h  | test_2025H2           |           0.000693213 | pre_may_direction_unstable            |
| a7al2x3_1fd71f89fcb97240 | F4_OI_taker_flow_interaction       | -/-/+                  |                         1 |              0.00114308  |                   1.04142  |          -0.000856922 |                   12.8398  | wrong_lag_future_24h  | test_2025H2           |           0.000789696 | pre_may_direction_unstable            |
| a7al2x3_a551e0d946a6abf3 | F4_OI_taker_flow_interaction       | -/+/+                  |                         2 |              0.000998019 |                   0.784995 |          -0.00100198  |                   10.6493  | wrong_lag_future_24h  | recent_oos_2026JanApr |           2.55579e-05 | pre_may_direction_unstable            |
| a7al2x3_9d7989b8d4655bf1 | F4_OI_taker_flow_interaction       | +/-/-                  |                         1 |             -0.00148785  |                   1.09382  |          -0.00348785  |                    4.65743 | wrong_lag_future_24h  | recent_oos_2026JanApr |          -0.000449228 | pre_may_direction_unstable            |
| a7al2x3_e5af54998a54bc71 | F4_OI_taker_flow_interaction       | +/+/-                  |                         2 |             -0.000832883 |                   1.57728  |          -0.00283288  |                    6.12659 | wrong_lag_future_24h  | recent_oos_2026JanApr |          -0.000940755 | pre_may_direction_unstable            |
| a7al2x3_694ea01b8dc33dd4 | F4_OI_taker_flow_interaction       | -/+/+                  |                         2 |              0.000279197 |                   0.543882 |          -0.0017208   |                   10.1772  | wrong_lag_future_24h  | test_2025H2           |           0.000690802 | pre_may_direction_unstable            |
| a7al2x3_d44b1d21d537c838 | F4_OI_taker_flow_interaction       | -/-/+                  |                         1 |              0.00108857  |                   0.868462 |          -0.000911427 |                   10.7647  | wrong_lag_future_24h  | validation_2025H1     |           0.00145201  | pre_may_direction_unstable            |
| a7al2x3_907e3c49019029cc | F4_OI_taker_flow_interaction       | +/-/-                  |                         1 |             -0.000791677 |                   0.762061 |          -0.00279168  |                   25.4355  | wrong_lag_future_24h  | test_2025H2           |          -0.000222631 | pre_may_direction_unstable            |
| a7al2x3_7f6ff1bafbd2c316 | F4_OI_taker_flow_interaction       | +/-/-                  |                         1 |             -0.00085371  |                   0.980741 |          -0.00285371  |                    3.99523 | symbol_shuffle        | recent_oos_2026JanApr |           0.000904223 | pre_may_direction_unstable            |
| a7al2x3_9add29eae207e174 | F5_OI_upper_regime_interaction     | +/-/-                  |                         1 |             -0.00148087  |                   0.86501  |          -0.00348087  |                   13.6079  | wrong_lag_future_24h  | validation_2025H1     |         nan           | pre_may_direction_unstable            |
| a7al2x3_d294deb3ca25cf27 | F5_OI_upper_regime_interaction     | +/-/-                  |                         1 |             -0.00148087  |                   0.86501  |          -0.00348087  |                   13.6079  | wrong_lag_future_24h  | validation_2025H1     |         nan           | pre_may_direction_unstable            |
| a7al2x3_c23082c0a63a46bd | F5_OI_upper_regime_interaction     | +/-/-                  |                         1 |             -0.00148087  |                   0.86501  |          -0.00348087  |                   13.6079  | wrong_lag_future_24h  | validation_2025H1     |         nan           | pre_may_direction_unstable            |
| a7al2x3_5e16028aa4a04eb5 | F5_OI_upper_regime_interaction     | +/-/-                  |                         1 |             -0.00148087  |                   0.86501  |          -0.00348087  |                   13.6079  | wrong_lag_future_24h  | validation_2025H1     |         nan           | pre_may_direction_unstable            |
| a7al2x3_eeff378890468230 | F5_OI_upper_regime_interaction     | +/-/-                  |                         1 |             -0.00332708  |                   1.08287  |          -0.00532708  |                   35.5124  | wrong_lag_future_24h  | test_2025H2           |         nan           | pre_may_direction_unstable            |
| a7al2x3_49640239a5937d81 | F5_OI_upper_regime_interaction     | +/-/+                  |                         2 |              0.000362343 |                   1.30884  |          -0.00163766  |                   47.0752  | wrong_lag_future_24h  | recent_oos_2026JanApr |         nan           | pre_may_direction_unstable            |
| a7al2x3_2fce75f307a1b1c7 | F5_OI_upper_regime_interaction     | +/-/-                  |                         1 |             -0.00456118  |                   1.0016   |          -0.00656118  |                    6.85282 | wrong_lag_future_24h  | recent_oos_2026JanApr |         nan           | pre_may_direction_unstable            |
| a7al2x3_54f5361a609798fc | F5_OI_upper_regime_interaction     | +/-/-                  |                         1 |             -0.00517394  |                   0.92377  |          -0.00717394  |                    4.91468 | wrong_lag_stale_168h  | test_2025H2           |         nan           | pre_may_direction_unstable            |
| a7al2x3_6425856b9df4b997 | F6_OI_latent_state_interaction     | NA/NA/NA               |                         0 |            nan           |                 nan        |         nan           |                  nan       |                       |                       |         nan           | metric_missing_or_sparse_smoke_window |
| a7al2x3_f726e8031e11a5c6 | F6_OI_latent_state_interaction     | NA/NA/NA               |                         0 |            nan           |                 nan        |         nan           |                  nan       |                       |                       |         nan           | metric_missing_or_sparse_smoke_window |
| a7al2x3_bc8ed4094566ea5e | F6_OI_latent_state_interaction     | NA/-/NA                |                         0 |            nan           |                 nan        |         nan           |                   45.9885  | wrong_lag_future_24h  | test_2025H2           |          -0.000498201 | metric_missing_or_sparse_smoke_window |
| a7al2x3_67d3a9b6da05c211 | F6_OI_latent_state_interaction     | NA/NA/NA               |                         0 |            nan           |                 nan        |         nan           |                  nan       |                       |                       |         nan           | metric_missing_or_sparse_smoke_window |
| a7al2x3_3cb1db3cafe85fa0 | F6_OI_latent_state_interaction     | NA/NA/NA               |                         0 |            nan           |                 nan        |         nan           |                  nan       |                       |                       |         nan           | metric_missing_or_sparse_smoke_window |
| a7al2x3_aaa82dfd8a7c3555 | F6_OI_latent_state_interaction     | NA/NA/NA               |                         0 |            nan           |                 nan        |         nan           |                  nan       |                       |                       |         nan           | metric_missing_or_sparse_smoke_window |
| a7al2x3_c73e0ebc3866e01e | F6_OI_latent_state_interaction     | NA/NA/NA               |                         0 |            nan           |                 nan        |         nan           |                  nan       |                       |                       |         nan           | metric_missing_or_sparse_smoke_window |
| a7al2x3_42246afae2fc6cd4 | F6_OI_latent_state_interaction     | NA/NA/NA               |                         0 |            nan           |                 nan        |         nan           |                  nan       |                       |                       |         nan           | metric_missing_or_sparse_smoke_window |

## Control Dominance Rollup

| variant              | split                 |   finite_ratio_count |   dominance_count |   median_control_abs_ratio |   max_control_abs_ratio |
|:---------------------|:----------------------|---------------------:|------------------:|---------------------------:|------------------------:|
| wrong_lag_future_24h | validation_2025H1     |                   40 |                37 |                   4.35837  |               140.095   |
| wrong_lag_future_24h | recent_oos_2026JanApr |                   40 |                27 |                   3.24269  |                47.0752  |
| wrong_lag_stale_168h | validation_2025H1     |                   40 |                24 |                   1.37554  |                11.9376  |
| wrong_lag_future_24h | test_2025H2           |                   41 |                20 |                   0.917057 |               102.39    |
| symbol_shuffle       | validation_2025H1     |                   40 |                17 |                   0.756098 |                17.4465  |
| wrong_lag_stale_168h | test_2025H2           |                   40 |                16 |                   0.720964 |                19.8788  |
| symbol_shuffle       | test_2025H2           |                   41 |                14 |                   0.603951 |                20.8676  |
| wrong_lag_stale_168h | recent_oos_2026JanApr |                   40 |                13 |                   0.541227 |                11.6783  |
| symbol_shuffle       | recent_oos_2026JanApr |                   40 |                13 |                   0.797568 |                 5.98345 |
| time_shuffle         | validation_2025H1     |                   40 |                11 |                   0.522747 |                 5.93892 |
| time_shuffle         | test_2025H2           |                   41 |                 8 |                   0.493875 |                19.2558  |
| same_family_random   | test_2025H2           |                   41 |                 8 |                   0.164437 |                 5.17691 |
| same_family_random   | validation_2025H1     |                   40 |                 7 |                   0.285036 |                 4.50017 |
| same_family_random   | recent_oos_2026JanApr |                   40 |                 6 |                   0.226864 |                 6.08471 |
| time_shuffle         | recent_oos_2026JanApr |                   40 |                 4 |                   0.27755  |                 4.17315 |

## Highest Control Ratios

| candidate_id             | variant              | split                 |   original_oriented_spread |   control_oriented_spread |   control_abs_ratio | control_dominates   |
|:-------------------------|:---------------------|:----------------------|---------------------------:|--------------------------:|--------------------:|:--------------------|
| a7al2x3_93725c2d40077dd9 | wrong_lag_future_24h | validation_2025H1     |               -9.33293e-05 |                0.0130749  |            140.095  | True                |
| a7al2x3_da77f7acad8f2253 | wrong_lag_future_24h | test_2025H2           |                7.90848e-05 |               -0.00809748 |            102.39   | True                |
| a7al2x3_90f96f99f826374d | wrong_lag_future_24h | test_2025H2           |                0.000117617 |               -0.00953543 |             81.0716 | True                |
| a7al2x3_49640239a5937d81 | wrong_lag_future_24h | recent_oos_2026JanApr |                0.000362343 |                0.0170573  |             47.0752 | True                |
| a7al2x3_bc8ed4094566ea5e | wrong_lag_future_24h | test_2025H2           |               -0.000246426 |                0.0113328  |             45.9885 | True                |
| a7al2x3_8cd55bb4dcd9ea8d | wrong_lag_future_24h | test_2025H2           |                0.000216268 |                0.00962011 |             44.4823 | True                |
| a7al2x3_da77f7acad8f2253 | wrong_lag_future_24h | validation_2025H1     |                0.000255011 |               -0.0099017  |             38.8284 | True                |
| a7al2x3_eeff378890468230 | wrong_lag_future_24h | test_2025H2           |               -0.000167945 |                0.00596413 |             35.5124 | True                |
| a7al2x3_e2d80967eacd522d | wrong_lag_future_24h | validation_2025H1     |               -0.000486928 |                0.0139631  |             28.676  | True                |
| a7al2x3_8cd55bb4dcd9ea8d | wrong_lag_future_24h | validation_2025H1     |               -0.000395036 |                0.0103018  |             26.0782 | True                |
| a7al2x3_907e3c49019029cc | wrong_lag_future_24h | test_2025H2           |               -0.000157121 |               -0.00399645 |             25.4355 | True                |
| a7al2x3_da77f7acad8f2253 | symbol_shuffle       | test_2025H2           |                7.90848e-05 |               -0.00165031 |             20.8676 | True                |
| a7al2x3_da77f7acad8f2253 | wrong_lag_stale_168h | test_2025H2           |                7.90848e-05 |                0.00157211 |             19.8788 | True                |
| a7al2x3_bc8ed4094566ea5e | time_shuffle         | test_2025H2           |               -0.000246426 |               -0.00474514 |             19.2558 | True                |
| a7al2x3_c6d040e141ee4a7a | wrong_lag_future_24h | validation_2025H1     |               -0.00010092  |                0.00194293 |             19.2522 | True                |
| a7al2x3_afebb1f45f8929ea | symbol_shuffle       | validation_2025H1     |               -0.000117489 |                0.00204978 |             17.4465 | True                |
| a7al2x3_907e3c49019029cc | symbol_shuffle       | test_2025H2           |               -0.000157121 |               -0.00215739 |             13.7308 | True                |
| a7al2x3_c23082c0a63a46bd | wrong_lag_future_24h | validation_2025H1     |                0.000275838 |                0.00375359 |             13.6079 | True                |
| a7al2x3_d294deb3ca25cf27 | wrong_lag_future_24h | validation_2025H1     |                0.000275838 |                0.00375359 |             13.6079 | True                |
| a7al2x3_9add29eae207e174 | wrong_lag_future_24h | validation_2025H1     |                0.000275838 |                0.00375359 |             13.6079 | True                |
| a7al2x3_5e16028aa4a04eb5 | wrong_lag_future_24h | validation_2025H1     |                0.000275838 |                0.00375359 |             13.6079 | True                |
| a7al2x3_eeff378890468230 | wrong_lag_future_24h | recent_oos_2026JanApr |               -0.00332708  |                0.0452623  |             13.6042 | True                |
| a7al2x3_eeff378890468230 | wrong_lag_stale_168h | test_2025H2           |               -0.000167945 |               -0.00226692 |             13.498  | True                |
| a7al2x3_035db391f91d7640 | wrong_lag_future_24h | validation_2025H1     |               -0.000138447 |                0.00184488 |             13.3256 | True                |
| a7al2x3_1fd71f89fcb97240 | wrong_lag_future_24h | test_2025H2           |               -9.89247e-05 |               -0.00127017 |             12.8398 | True                |
| a7al2x3_6f9b57cfb28def3d | wrong_lag_future_24h | validation_2025H1     |               -0.00112565  |               -0.0140853  |             12.5131 | True                |
| a7al2x3_c23082c0a63a46bd | wrong_lag_future_24h | recent_oos_2026JanApr |               -0.00148087  |                0.0180991  |             12.2219 | True                |
| a7al2x3_5e16028aa4a04eb5 | wrong_lag_future_24h | recent_oos_2026JanApr |               -0.00148087  |                0.0180991  |             12.2219 | True                |
| a7al2x3_d294deb3ca25cf27 | wrong_lag_future_24h | recent_oos_2026JanApr |               -0.00148087  |                0.0180991  |             12.2219 | True                |
| a7al2x3_9add29eae207e174 | wrong_lag_future_24h | recent_oos_2026JanApr |               -0.00148087  |                0.0180991  |             12.2219 | True                |

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
