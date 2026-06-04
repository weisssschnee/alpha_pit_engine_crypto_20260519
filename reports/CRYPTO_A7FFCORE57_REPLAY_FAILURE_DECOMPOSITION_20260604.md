# CRYPTO A7FF-CORE57 REPLAY FAILURE DECOMPOSITION

Generated: 2026-06-04T12:30:20Z

## Decision

`PASS_A7FFCORE57_FAILURE_DECOMPOSITION_BUILT`

CORE57 decomposes CORE56 bounded replay failures. It does not generate formulas, run replay, or authorize alpha promotion.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core58_failure_aware_queue_rebuild": true,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers_inherited_from_core56": [
    "core56_clean_candidate_count_zero"
  ],
  "control_dominated_rows": 612,
  "cost5_fragile_rows": 14,
  "decision": "PASS_A7FFCORE57_FAILURE_DECOMPOSITION_BUILT",
  "decision_count": 4,
  "empty_premay_label_families": [
    "L3_liquidity_relative"
  ],
  "empty_premay_label_family_count": 1,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-04T12:30:20Z",
  "input_candidate_count": 114,
  "input_replay_rows": 1824,
  "motif_count": 8,
  "premay_unstable_rows": 1189,
  "semantic_pair_count": 9,
  "source_decision": "HOLD_A7FFCORE56_BOUNDED_REPLAY_PREFLIGHT",
  "source_stage": "A7FF-CORE56",
  "stage": "A7FF-CORE57",
  "stale_lag_fragile_rows": 9,
  "uses_may": false
}
```

## Decision Summary

| decision                      |   row_count |   candidate_count |   median_control_ratio |   median_positive_split_count |   max_recent_spread |   median_cost5_recent |
|:------------------------------|------------:|------------------:|-----------------------:|------------------------------:|--------------------:|----------------------:|
| HOLD_CORE56_PREMAY_UNSTABLE   |        1189 |               114 |               1.7268   |                             0 |         0.19402     |          -0.00198382  |
| HOLD_CORE56_CONTROL_DOMINATED |         612 |               107 |               1.00401  |                             3 |         0.291769    |          -0.000356133 |
| HOLD_CORE56_STALE_LAG_FRAGILE |           9 |                 7 |               0.997188 |                             3 |         0.0732224   |           0.0142807   |
| HOLD_CORE56_COST5_FRAGILE     |          14 |                 5 |               0.999459 |                             3 |         0.000876713 |          -0.000257811 |

## Failure By Label / Horizon

| label_family          |   label_horizon_h | decision                      |   row_count |   candidate_count |   median_control_ratio |   median_positive_split_count |   max_recent_spread |   median_cost5_recent |
|:----------------------|------------------:|:------------------------------|------------:|------------------:|-----------------------:|------------------------------:|--------------------:|----------------------:|
| L3_liquidity_relative |                 1 | HOLD_CORE56_PREMAY_UNSTABLE   |         114 |               114 |             nan        |                             0 |       nan           |         nan           |
| L3_liquidity_relative |                 4 | HOLD_CORE56_PREMAY_UNSTABLE   |         114 |               114 |             nan        |                             0 |       nan           |         nan           |
| L3_liquidity_relative |                 8 | HOLD_CORE56_PREMAY_UNSTABLE   |         114 |               114 |             nan        |                             0 |       nan           |         nan           |
| L3_liquidity_relative |                24 | HOLD_CORE56_PREMAY_UNSTABLE   |         114 |               114 |             nan        |                             0 |       nan           |         nan           |
| L5_vol_adjusted       |                 1 | HOLD_CORE56_CONTROL_DOMINATED |          97 |                97 |               1.00197  |                             3 |         0.0979445   |           0.0259371   |
| L0_raw                |                 1 | HOLD_CORE56_CONTROL_DOMINATED |          87 |                87 |               1.00227  |                             3 |         0.00101837  |          -0.000715476 |
| L0_raw                |                24 | HOLD_CORE56_PREMAY_UNSTABLE   |          87 |                87 |               1.51013  |                             1 |         0.00151276  |          -0.00205956  |
| L1_xs                 |                 1 | HOLD_CORE56_CONTROL_DOMINATED |          87 |                87 |               1.00227  |                             3 |         0.00101837  |          -0.000715476 |
| L1_xs                 |                24 | HOLD_CORE56_PREMAY_UNSTABLE   |          87 |                87 |               1.51013  |                             1 |         0.00151276  |          -0.00205956  |
| L5_vol_adjusted       |                24 | HOLD_CORE56_PREMAY_UNSTABLE   |          86 |                86 |               2.5253   |                             1 |         0.19402     |          -0.0609826   |
| L0_raw                |                 8 | HOLD_CORE56_PREMAY_UNSTABLE   |          72 |                72 |               1.39774  |                             1 |         0.00172351  |          -0.00166773  |
| L1_xs                 |                 8 | HOLD_CORE56_PREMAY_UNSTABLE   |          72 |                72 |               1.39774  |                             1 |         0.00172351  |          -0.00166773  |
| L5_vol_adjusted       |                 8 | HOLD_CORE56_PREMAY_UNSTABLE   |          72 |                72 |               2.70811  |                             1 |         0.0846985   |          -0.0451608   |
| L0_raw                |                 4 | HOLD_CORE56_PREMAY_UNSTABLE   |          68 |                68 |               1.65342  |                             1 |         0.000892467 |          -0.00136021  |
| L1_xs                 |                 4 | HOLD_CORE56_PREMAY_UNSTABLE   |          68 |                68 |               1.65342  |                             1 |         0.000892468 |          -0.00136021  |
| L5_vol_adjusted       |                 4 | HOLD_CORE56_CONTROL_DOMINATED |          58 |                58 |               1.00281  |                             3 |         0.0914783   |           0.0281558   |
| L5_vol_adjusted       |                 4 | HOLD_CORE56_PREMAY_UNSTABLE   |          55 |                55 |               2.0279   |                             1 |         0.0322984   |          -0.022898    |
| L0_raw                |                 4 | HOLD_CORE56_CONTROL_DOMINATED |          43 |                43 |               1.00275  |                             3 |         0.00132561  |          -0.000607714 |
| L1_xs                 |                 4 | HOLD_CORE56_CONTROL_DOMINATED |          43 |                43 |               1.00275  |                             3 |         0.00132561  |          -0.000607714 |
| L5_vol_adjusted       |                 8 | HOLD_CORE56_CONTROL_DOMINATED |          41 |                41 |               1.01332  |                             3 |         0.0985627   |           0.030973    |
| L0_raw                |                 8 | HOLD_CORE56_CONTROL_DOMINATED |          38 |                38 |               1.02371  |                             3 |         0.00220316  |          -0.000585241 |
| L1_xs                 |                 8 | HOLD_CORE56_CONTROL_DOMINATED |          38 |                38 |               1.02371  |                             3 |         0.00220316  |          -0.000585241 |
| L5_vol_adjusted       |                24 | HOLD_CORE56_CONTROL_DOMINATED |          28 |                28 |               1.20572  |                             3 |         0.291769    |           0.0481669   |
| L0_raw                |                 1 | HOLD_CORE56_PREMAY_UNSTABLE   |          27 |                27 |               4.16442  |                             2 |         7.41208e-05 |          -0.00105063  |
| L1_xs                 |                 1 | HOLD_CORE56_PREMAY_UNSTABLE   |          27 |                27 |               4.16442  |                             2 |         7.41208e-05 |          -0.00105063  |
| L0_raw                |                24 | HOLD_CORE56_CONTROL_DOMINATED |          26 |                26 |               1.01205  |                             3 |         0.00740984  |          -0.000211434 |
| L1_xs                 |                24 | HOLD_CORE56_CONTROL_DOMINATED |          26 |                26 |               1.01205  |                             3 |         0.00740984  |          -0.000211434 |
| L5_vol_adjusted       |                 1 | HOLD_CORE56_PREMAY_UNSTABLE   |          12 |                12 |               3.17277  |                             2 |         0.0126228   |           0.00220471  |
| L5_vol_adjusted       |                 1 | HOLD_CORE56_STALE_LAG_FRAGILE |           5 |                 5 |               0.99904  |                             3 |         0.0732224   |           0.0183261   |
| L0_raw                |                 4 | HOLD_CORE56_COST5_FRAGILE     |           3 |                 3 |               0.998948 |                             3 |         0.000742189 |          -0.000257811 |
| L0_raw                |                 8 | HOLD_CORE56_COST5_FRAGILE     |           3 |                 3 |               0.999459 |                             3 |         0.000876713 |          -0.000123287 |
| L1_xs                 |                 4 | HOLD_CORE56_COST5_FRAGILE     |           3 |                 3 |               0.998948 |                             3 |         0.000742189 |          -0.000257811 |
| L1_xs                 |                 8 | HOLD_CORE56_COST5_FRAGILE     |           3 |                 3 |               0.999459 |                             3 |         0.000876713 |          -0.000123287 |
| L0_raw                |                 8 | HOLD_CORE56_STALE_LAG_FRAGILE |           1 |                 1 |               0.997188 |                             3 |         0.00016874  |          -0.00083126  |
| L0_raw                |                24 | HOLD_CORE56_COST5_FRAGILE     |           1 |                 1 |               0.999753 |                             3 |         0.000743045 |          -0.000256955 |
| L1_xs                 |                 8 | HOLD_CORE56_STALE_LAG_FRAGILE |           1 |                 1 |               0.997188 |                             3 |         0.00016874  |          -0.00083126  |
| L1_xs                 |                24 | HOLD_CORE56_COST5_FRAGILE     |           1 |                 1 |               0.999753 |                             3 |         0.000743045 |          -0.000256955 |
| L5_vol_adjusted       |                 4 | HOLD_CORE56_STALE_LAG_FRAGILE |           1 |                 1 |               0.999615 |                             3 |         0.0146653   |           0.0136653   |
| L5_vol_adjusted       |                 8 | HOLD_CORE56_STALE_LAG_FRAGILE |           1 |                 1 |               0.992312 |                             3 |         0.0152807   |           0.0142807   |

## Label Observation Audit

| label_family          |   label_horizon_h |   row_count |   train_2024_obs_median |   train_2024_obs_positive_rows |   validation_2025H1_obs_median |   validation_2025H1_obs_positive_rows |   test_2025H2_obs_median |   test_2025H2_obs_positive_rows |   recent_oos_2026JanApr_obs_median |   recent_oos_2026JanApr_obs_positive_rows | premay_label_observation_status   |
|:----------------------|------------------:|------------:|------------------------:|-------------------------------:|-------------------------------:|--------------------------------------:|-------------------------:|--------------------------------:|-----------------------------------:|------------------------------------------:|:----------------------------------|
| L3_liquidity_relative |                 1 |         114 |                       0 |                              0 |                              0 |                                     0 |                        0 |                               0 |                                  0 |                                         0 | LABEL_OBS_EMPTY                   |
| L3_liquidity_relative |                 4 |         114 |                       0 |                              0 |                              0 |                                     0 |                        0 |                               0 |                                  0 |                                         0 | LABEL_OBS_EMPTY                   |
| L3_liquidity_relative |                 8 |         114 |                       0 |                              0 |                              0 |                                     0 |                        0 |                               0 |                                  0 |                                         0 | LABEL_OBS_EMPTY                   |
| L3_liquidity_relative |                24 |         114 |                       0 |                              0 |                              0 |                                     0 |                        0 |                               0 |                                  0 |                                         0 | LABEL_OBS_EMPTY                   |
| L0_raw                |                 1 |         114 |                    8773 |                            114 |                           4344 |                                   114 |                     4416 |                             114 |                               2880 |                                       114 | LABEL_OBS_OK                      |
| L0_raw                |                 4 |         114 |                    8773 |                            114 |                           4344 |                                   114 |                     4416 |                             114 |                               2880 |                                       114 | LABEL_OBS_OK                      |
| L0_raw                |                 8 |         114 |                    8773 |                            114 |                           4344 |                                   114 |                     4416 |                             114 |                               2880 |                                       114 | LABEL_OBS_OK                      |
| L0_raw                |                24 |         114 |                    8773 |                            114 |                           4344 |                                   114 |                     4416 |                             114 |                               2880 |                                       114 | LABEL_OBS_OK                      |
| L1_xs                 |                 1 |         114 |                    8773 |                            114 |                           4344 |                                   114 |                     4416 |                             114 |                               2880 |                                       114 | LABEL_OBS_OK                      |
| L1_xs                 |                 4 |         114 |                    8773 |                            114 |                           4344 |                                   114 |                     4416 |                             114 |                               2880 |                                       114 | LABEL_OBS_OK                      |
| L1_xs                 |                 8 |         114 |                    8773 |                            114 |                           4344 |                                   114 |                     4416 |                             114 |                               2880 |                                       114 | LABEL_OBS_OK                      |
| L1_xs                 |                24 |         114 |                    8773 |                            114 |                           4344 |                                   114 |                     4416 |                             114 |                               2880 |                                       114 | LABEL_OBS_OK                      |
| L5_vol_adjusted       |                 1 |         114 |                    8736 |                            114 |                           4344 |                                   114 |                     4416 |                             114 |                               2880 |                                       114 | LABEL_OBS_OK                      |
| L5_vol_adjusted       |                 4 |         114 |                    8736 |                            114 |                           4344 |                                   114 |                     4416 |                             114 |                               2880 |                                       114 | LABEL_OBS_OK                      |
| L5_vol_adjusted       |                 8 |         114 |                    8736 |                            114 |                           4344 |                                   114 |                     4416 |                             114 |                               2880 |                                       114 | LABEL_OBS_OK                      |
| L5_vol_adjusted       |                24 |         114 |                    8736 |                            114 |                           4344 |                                   114 |                     4416 |                             114 |                               2880 |                                       114 | LABEL_OBS_OK                      |

## Failure By Semantic Pair

| semantic_pair                         |   row_count |   candidate_count |   median_control_ratio |   median_positive_split_count |   max_recent_spread |   median_cost5_recent |
|:--------------------------------------|------------:|------------------:|-----------------------:|------------------------------:|--------------------:|----------------------:|
| basis_premium_like|price_like         |         512 |                32 |                1.45544 |                             1 |           0.12507   |          -0.0010478   |
| basis_premium_like|volatility_like    |         432 |                27 |                1.34382 |                             2 |           0.0791922 |          -0.00109837  |
| basis_premium_like|basis_premium_like |         384 |                24 |                1.20505 |                             1 |           0.291769  |          -0.000581663 |
| price_like|volatility_like            |         160 |                10 |                1.32181 |                             2 |           0.0919536 |          -0.000469785 |
| basis_premium_like                    |         128 |                 8 |                1       |                             2 |           0.0794718 |          -0.000699279 |
| price_like                            |          96 |                 6 |                1.79519 |                             2 |           0.049393  |          -0.000707794 |
| basis_premium_like|positioning_like   |          64 |                 4 |                1.01557 |                             3 |           0.117643  |          -2.76294e-05 |
| liquidity_like|volatility_like        |          32 |                 2 |                1.68649 |                             1 |           0.0398796 |          -0.000425275 |
| volatility_like                       |          16 |                 1 |                1.41908 |                             1 |           0.0135552 |          -0.00121365  |

## Control Source Decomposition

| strongest_control_kind   | strongest_control_split   | decision                      |   row_count |   candidate_count |   median_control_ratio |   median_positive_split_count |   max_recent_spread |   median_cost5_recent |
|:-------------------------|:--------------------------|:------------------------------|------------:|------------------:|-----------------------:|------------------------------:|--------------------:|----------------------:|
| stale                    | validation_2025H1         | HOLD_CORE56_PREMAY_UNSTABLE   |         464 |               114 |               1.35296  |                             0 |         0.0028981   |          -0.000622149 |
| sign_flip                | validation_2025H1         | HOLD_CORE56_CONTROL_DOMINATED |         234 |                86 |               1.00889  |                             3 |         0.0547611   |          -0.000590705 |
| stale                    | recent_oos_2026JanApr     | HOLD_CORE56_PREMAY_UNSTABLE   |         380 |                62 |               1.53541  |                             1 |         0.19402     |          -0.00266268  |
| sign_flip                | test_2025H2               | HOLD_CORE56_CONTROL_DOMINATED |         142 |                45 |               1        |                             3 |         0.0455553   |          -0.00052226  |
| sign_flip                | recent_oos_2026JanApr     | HOLD_CORE56_CONTROL_DOMINATED |         170 |                42 |               1.00319  |                             3 |         0.117643    |           0.000800536 |
| sign_flip                | validation_2025H1         | HOLD_CORE56_PREMAY_UNSTABLE   |          78 |                31 |               2.32815  |                             2 |         0.0233607   |          -0.00109092  |
| sign_flip                | recent_oos_2026JanApr     | HOLD_CORE56_PREMAY_UNSTABLE   |          61 |                23 |               1.51013  |                             2 |         0.12507     |          -0.000319979 |
| time_shuffle             | test_2025H2               | HOLD_CORE56_PREMAY_UNSTABLE   |          51 |                21 |               1.90415  |                             1 |         0.0480426   |          -0.000996798 |
| stale                    | test_2025H2               | HOLD_CORE56_PREMAY_UNSTABLE   |          31 |                21 |               1.64303  |                             1 |         0.0295007   |          -0.0946251   |
| stale                    | recent_oos_2026JanApr     | HOLD_CORE56_CONTROL_DOMINATED |          38 |                17 |               1.23321  |                             3 |         0.0862278   |           0.00086272  |
| sign_flip                | test_2025H2               | HOLD_CORE56_PREMAY_UNSTABLE   |          34 |                15 |               2.47685  |                             2 |         0.0135552   |          -0.00104605  |
| time_shuffle             | recent_oos_2026JanApr     | HOLD_CORE56_PREMAY_UNSTABLE   |          43 |                14 |               2.35738  |                             1 |         0.0203864   |          -0.00152768  |
| symbol_shuffle           | recent_oos_2026JanApr     | HOLD_CORE56_PREMAY_UNSTABLE   |          23 |                11 |               5.04308  |                             2 |         8.47541e-05 |          -0.00166236  |
| symbol_shuffle           | test_2025H2               | HOLD_CORE56_PREMAY_UNSTABLE   |          17 |                10 |               4.72591  |                             2 |         0.076772    |          -0.000235282 |
| time_shuffle             | test_2025H2               | HOLD_CORE56_CONTROL_DOMINATED |           8 |                 7 |               2.55924  |                             3 |         0.291769    |           0.0270059   |
| time_shuffle             | recent_oos_2026JanApr     | HOLD_CORE56_CONTROL_DOMINATED |           9 |                 6 |               2.59415  |                             3 |         0.0169947   |          -0.00073594  |
| stale                    | test_2025H2               | HOLD_CORE56_CONTROL_DOMINATED |           7 |                 6 |               1.52248  |                             3 |         0.283757    |           0.0184494   |
| sign_flip                | recent_oos_2026JanApr     | HOLD_CORE56_COST5_FRAGILE     |          12 |                 4 |               0.999459 |                             3 |         0.000876713 |          -0.000257811 |
| sign_flip                | validation_2025H1         | HOLD_CORE56_STALE_LAG_FRAGILE |           4 |                 4 |               0.996578 |                             3 |         0.0228879   |           0.0177165   |
| time_shuffle             | validation_2025H1         | HOLD_CORE56_PREMAY_UNSTABLE   |           7 |                 3 |               2.9873   |                             2 |         0.0259797   |          -0.00104333  |
| sign_flip                | test_2025H2               | HOLD_CORE56_STALE_LAG_FRAGILE |           4 |                 2 |               0.997188 |                             3 |         0.0152807   |           0.00641702  |
| symbol_shuffle           | test_2025H2               | HOLD_CORE56_CONTROL_DOMINATED |           2 |                 2 |               2.38291  |                             3 |         0.0473666   |           0.0356036   |
| sign_flip                | test_2025H2               | HOLD_CORE56_COST5_FRAGILE     |           2 |                 1 |               0.999753 |                             3 |         0.000743045 |          -0.000256955 |
| sign_flip                | recent_oos_2026JanApr     | HOLD_CORE56_STALE_LAG_FRAGILE |           1 |                 1 |               0.999545 |                             3 |         0.0732224   |           0.0722224   |
| symbol_shuffle           | recent_oos_2026JanApr     | HOLD_CORE56_CONTROL_DOMINATED |           1 |                 1 |              42.8879   |                             3 |         0.00284651  |           0.00184651  |
| time_shuffle             | validation_2025H1         | HOLD_CORE56_CONTROL_DOMINATED |           1 |                 1 |               1.09442  |                             3 |         0.0112081   |           0.0102081   |

## Split Stability Decomposition

|   premay_positive_split_count | premay_sign_pattern   | decision                      |   row_count |   candidate_count |   median_control_ratio |   median_positive_split_count |   max_recent_spread |   median_cost5_recent |
|------------------------------:|:----------------------|:------------------------------|------------:|------------------:|-----------------------:|------------------------------:|--------------------:|----------------------:|
|                             0 | 000                   | HOLD_CORE56_PREMAY_UNSTABLE   |         456 |               114 |             nan        |                             0 |       nan           |         nan           |
|                             3 | +++                   | HOLD_CORE56_CONTROL_DOMINATED |         612 |               107 |               1.00401  |                             3 |         0.291769    |          -0.000356133 |
|                             1 | +--                   | HOLD_CORE56_PREMAY_UNSTABLE   |         247 |                53 |               1.68223  |                             1 |        -4.3329e-05  |          -0.00294101  |
|                             0 | ---                   | HOLD_CORE56_PREMAY_UNSTABLE   |         151 |                52 |               1.33361  |                             0 |        -6.95147e-05 |          -0.00765507  |
|                             2 | ++-                   | HOLD_CORE56_PREMAY_UNSTABLE   |         174 |                48 |               2.14592  |                             2 |        -4.13432e-06 |          -0.00132575  |
|                             2 | +-+                   | HOLD_CORE56_PREMAY_UNSTABLE   |          77 |                28 |               2.30074  |                             2 |         0.19402     |           0.000512765 |
|                             2 | -++                   | HOLD_CORE56_PREMAY_UNSTABLE   |          28 |                12 |               2.50744  |                             2 |         0.076772    |          -0.000259362 |
|                             1 | --+                   | HOLD_CORE56_PREMAY_UNSTABLE   |          41 |                10 |               1.83205  |                             1 |         0.12507     |          -0.000413721 |
|                             1 | -+-                   | HOLD_CORE56_PREMAY_UNSTABLE   |          15 |                 9 |               2.37064  |                             1 |        -6.45153e-05 |          -0.0010991   |
|                             3 | +++                   | HOLD_CORE56_STALE_LAG_FRAGILE |           9 |                 7 |               0.997188 |                             3 |         0.0732224   |           0.0142807   |
|                             3 | +++                   | HOLD_CORE56_COST5_FRAGILE     |          14 |                 5 |               0.999459 |                             3 |         0.000876713 |          -0.000257811 |

## Repair Policy Preview

| policy_scope   | key                                   | action                       | reason                                                               |   candidate_count |   median_control_ratio |   median_positive_split_count |
|:---------------|:--------------------------------------|:-----------------------------|:---------------------------------------------------------------------|------------------:|-----------------------:|------------------------------:|
| semantic_pair  | basis_premium_like|price_like         | downweight_or_block_as_alpha | median_control_ratio_ge_1|premay_split_instability|cost5_nonpositive |                32 |                1.45544 |                             1 |
| semantic_pair  | basis_premium_like|volatility_like    | downweight_or_block_as_alpha | median_control_ratio_ge_1|cost5_nonpositive                          |                27 |                1.34382 |                             2 |
| semantic_pair  | basis_premium_like|basis_premium_like | downweight_or_block_as_alpha | median_control_ratio_ge_1|premay_split_instability|cost5_nonpositive |                24 |                1.20505 |                             1 |
| semantic_pair  | price_like|volatility_like            | downweight_or_block_as_alpha | median_control_ratio_ge_1|cost5_nonpositive                          |                10 |                1.32181 |                             2 |
| semantic_pair  | basis_premium_like                    | downweight_or_block_as_alpha | median_control_ratio_ge_1|cost5_nonpositive                          |                 8 |                1       |                             2 |
| semantic_pair  | price_like                            | downweight_or_block_as_alpha | median_control_ratio_ge_1|cost5_nonpositive                          |                 6 |                1.79519 |                             2 |
| semantic_pair  | basis_premium_like|positioning_like   | downweight_or_block_as_alpha | median_control_ratio_ge_1|cost5_nonpositive                          |                 4 |                1.01557 |                             3 |
| semantic_pair  | liquidity_like|volatility_like        | downweight_or_block_as_alpha | median_control_ratio_ge_1|premay_split_instability|cost5_nonpositive |                 2 |                1.68649 |                             1 |
| semantic_pair  | volatility_like                       | downweight_or_block_as_alpha | median_control_ratio_ge_1|premay_split_instability|cost5_nonpositive |                 1 |                1.41908 |                             1 |
| motif          | safe_div_abs                          | downweight_or_block_as_alpha | median_control_ratio_ge_1|premay_split_instability                   |                38 |                1.43914 |                             1 |
| motif          | mul                                   | downweight_or_block_as_alpha | median_control_ratio_ge_1                                            |                17 |                1.78467 |                             2 |
| motif          | single                                | downweight_or_block_as_alpha | median_control_ratio_ge_1                                            |                15 |                1.10248 |                             2 |
| motif          | gated_sign                            | downweight_or_block_as_alpha | median_control_ratio_ge_1                                            |                14 |                1.0771  |                             2 |
| motif          | sub                                   | downweight_or_block_as_alpha | median_control_ratio_ge_1                                            |                12 |                1.00615 |                             2 |
| motif          | spread_rank                           | downweight_or_block_as_alpha | median_control_ratio_ge_1                                            |                11 |                1.00934 |                             3 |
| motif          | smooth_mul                            | downweight_or_block_as_alpha | median_control_ratio_ge_1                                            |                 6 |                1.64303 |                             2 |
| motif          | signed_spread                         | downweight_or_block_as_alpha | median_control_ratio_ge_1|premay_split_instability                   |                 1 |                1.76625 |                             1 |

## Boundary

```text
search executed: false
replay executed: false
May used: false
large search / alpha proof / shadow / paper / live: false
```
