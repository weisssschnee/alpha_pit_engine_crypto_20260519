# CRYPTO A7FF-CORE14R REPLAY FAILURE FORENSIC

Generated: 2026-06-01T04:39:57Z

## Decision

`PASS_A7FFCORE14R_FAILURE_ATTRIBUTION_COMPLETE_READY_FOR_CORE14S`

A7FF-CORE14R diagnoses the CORE14E bounded replay collapse. It does not rerun replay, execute formula search, promote candidates, or authorize alpha proof.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core14s_contract": true,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE14R_FAILURE_ATTRIBUTION_COMPLETE_READY_FOR_CORE14S",
  "dominant_blocker": "control_and_cost_collapse",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T04:39:57Z",
  "max_strict_candidates_under_sensitivity": 12,
  "near_miss_candidate_count": 9,
  "next_allowed": "A7FF-CORE14S replay-packet/objective repair contract",
  "source_candidate_count": 128,
  "source_decision": "HOLD_A7FFCORE14E_BOUNDED_REPLAY_INSUFFICIENT",
  "source_replay_clean_candidate_count": 2,
  "source_stage": "A7FF-CORE14E",
  "stage": "A7FF-CORE14R"
}
```

## Gate Sensitivity

|   cost_bps |   control_ratio_threshold |   either_validation_or_recent_candidates |   both_validation_and_recent_candidates |   both_semantic_count |   both_motif_count |
|-----------:|--------------------------:|-----------------------------------------:|----------------------------------------:|----------------------:|-------------------:|
|          0 |                       0.8 |                                       14 |                                       2 |                     1 |                  1 |
|          0 |                       1   |                                       29 |                                       5 |                     2 |                  2 |
|          0 |                       1.5 |                                       50 |                                       9 |                     2 |                  2 |
|          0 |                       2   |                                       64 |                                      12 |                     2 |                  2 |
|          2 |                       0.8 |                                        8 |                                       2 |                     1 |                  1 |
|          2 |                       1   |                                       21 |                                       5 |                     2 |                  2 |
|          2 |                       1.5 |                                       35 |                                       9 |                     2 |                  2 |
|          2 |                       2   |                                       43 |                                      11 |                     2 |                  2 |
|          5 |                       0.8 |                                        4 |                                       0 |                     0 |                  0 |
|          5 |                       1   |                                       11 |                                       2 |                     1 |                  1 |
|          5 |                       1.5 |                                       16 |                                       4 |                     2 |                  2 |
|          5 |                       2   |                                       17 |                                       4 |                     2 |                  2 |
|         10 |                       0.8 |                                        2 |                                       0 |                     0 |                  0 |
|         10 |                       1   |                                        4 |                                       0 |                     0 |                  0 |
|         10 |                       1.5 |                                        5 |                                       0 |                     0 |                  0 |
|         10 |                       2   |                                        5 |                                       0 |                     0 |                  0 |

## Split Gate Summary

| split      | semantic_bucket                      | motif_bucket       |   candidate_count |   positive_count |   control_clean_count |   strict_gate_rows |   median_spread |   median_cost_adjusted_spread |   median_control_ratio |
|:-----------|:-------------------------------------|:-------------------|------------------:|-----------------:|----------------------:|-------------------:|----------------:|------------------------------:|-----------------------:|
| recent     | liquidity_like\|volatility_like      | liquidity_shock    |                28 |                6 |                     8 |                  4 |     6.26133e-05 |                  -0.000937387 |                1.55069 |
| recent     | taker_flow_like\|basis_premium_like  | gated_sign         |                24 |                3 |                     4 |                  3 |     0.000467248 |                  -0.000532752 |                3.49694 |
| validation | liquidity_like\|volatility_like      | liquidity_shock    |                28 |                7 |                     7 |                  2 |     0.000269133 |                  -0.000730867 |                1.35187 |
| recent     | taker_flow_like\|open_interest_like  | flow_x_leverage    |                24 |                2 |                     3 |                  1 |    -8.96439e-05 |                  -0.00108964  |                3.22223 |
| validation | taker_flow_like\|basis_premium_like  | gated_sign         |                24 |                2 |                     8 |                  1 |     0.000574023 |                  -0.000425977 |                1.57336 |
| validation | liquidity_like                       | single             |                20 |                1 |                     2 |                  1 |     0.000100853 |                  -0.000899147 |                5.85136 |
| recent     | open_interest_like                   | single             |                 4 |                1 |                     1 |                  1 |     9.86314e-05 |                  -0.000901369 |                7.42009 |
| recent     | open_interest_like\|positioning_like | delta_x_divergence |                28 |                0 |                     4 |                  0 |     0.000113578 |                  -0.000886422 |                5.21801 |
| train      | liquidity_like\|volatility_like      | liquidity_shock    |                28 |                4 |                     5 |                  0 |    -0.000147517 |                  -0.00114752  |                1.51095 |
| train      | open_interest_like\|positioning_like | delta_x_divergence |                28 |                0 |                     2 |                  0 |     0.000292697 |                  -0.000707303 |                1.93036 |
| validation | open_interest_like\|positioning_like | delta_x_divergence |                28 |                1 |                     0 |                  0 |     3.96294e-05 |                  -0.000960371 |                5.04628 |
| train      | taker_flow_like\|basis_premium_like  | gated_sign         |                24 |                0 |                     0 |                  0 |    -4.438e-05   |                  -0.00104438  |                7.82901 |
| train      | taker_flow_like\|open_interest_like  | flow_x_leverage    |                24 |                6 |                     3 |                  0 |    -6.46903e-06 |                  -0.00100647  |                3.5097  |
| validation | taker_flow_like\|open_interest_like  | flow_x_leverage    |                24 |                4 |                     3 |                  0 |    -5.5345e-05  |                  -0.00105534  |                1.90514 |
| recent     | liquidity_like                       | single             |                20 |                0 |                     0 |                  0 |     0.000126882 |                  -0.000873118 |                3.3943  |
| train      | liquidity_like                       | single             |                20 |                0 |                     6 |                  0 |    -0.000615191 |                  -0.00161519  |                2.04481 |
| train      | open_interest_like                   | single             |                 4 |                0 |                     0 |                  0 |    -0.00021029  |                  -0.00121029  |                6.67774 |
| validation | open_interest_like                   | single             |                 4 |                0 |                     0 |                  0 |    -0.000139295 |                  -0.00113929  |                3.20487 |

## Control Dominance Summary

| dominant_control           | semantic_bucket                      | motif_bucket       |   row_count |   candidate_count |   median_control_ratio |   median_cost_adjusted_spread |
|:---------------------------|:-------------------------------------|:-------------------|------------:|------------------:|-----------------------:|------------------------------:|
| wrong_lag_future_spread    | taker_flow_like\|basis_premium_like  | gated_sign         |          60 |                24 |               3.70427  |                  -0.000725351 |
| wrong_lag_future_spread    | liquidity_like                       | single             |          45 |                18 |               5.04795  |                  -0.000954736 |
| wrong_lag_future_spread    | open_interest_like\|positioning_like | delta_x_divergence |          42 |                22 |               7.17237  |                  -0.00109656  |
| wrong_lag_future_spread    | liquidity_like\|volatility_like      | liquidity_shock    |          33 |                21 |               1.75883  |                  -0.0011461   |
| wrong_lag_future_spread    | taker_flow_like\|open_interest_like  | flow_x_leverage    |          33 |                21 |               3.22015  |                  -0.00110292  |
| same_family_placebo_spread | liquidity_like\|volatility_like      | liquidity_shock    |          22 |                19 |               1.52353  |                  -0.000883965 |
| wrong_lag_stale_spread     | liquidity_like\|volatility_like      | liquidity_shock    |          17 |                14 |               1.04372  |                  -0.00104834  |
| time_shuffle_spread        | open_interest_like\|positioning_like | delta_x_divergence |          15 |                 9 |               3.75762  |                  -0.000827349 |
| wrong_lag_stale_spread     | open_interest_like\|positioning_like | delta_x_divergence |          15 |                12 |               1.39103  |                  -0.000678378 |
| wrong_lag_stale_spread     | taker_flow_like\|open_interest_like  | flow_x_leverage    |          12 |                 9 |               2.70213  |                  -0.00105252  |
| time_shuffle_spread        | taker_flow_like\|open_interest_like  | flow_x_leverage    |          10 |                 9 |               1.37322  |                  -0.00104663  |
| time_shuffle_spread        | liquidity_like\|volatility_like      | liquidity_shock    |           9 |                 8 |               0.876423 |                  -8.64066e-05 |
| symbol_shuffle_spread      | taker_flow_like\|open_interest_like  | flow_x_leverage    |           9 |                 8 |               2.10313  |                  -0.000808473 |
| same_family_placebo_spread | taker_flow_like\|basis_premium_like  | gated_sign         |           8 |                 6 |               1.48667  |                  -0.00033282  |
| same_family_placebo_spread | taker_flow_like\|open_interest_like  | flow_x_leverage    |           8 |                 8 |               2.44422  |                  -0.000906633 |
| same_family_placebo_spread | open_interest_like\|positioning_like | delta_x_divergence |           7 |                 6 |               1.36935  |                  -0.00086607  |
| wrong_lag_future_spread    | open_interest_like                   | single             |           7 |                 4 |               3.44798  |                  -0.00114232  |
| same_family_placebo_spread | liquidity_like                       | single             |           6 |                 6 |               1.00067  |                  -0.00131967  |
| symbol_shuffle_spread      | open_interest_like\|positioning_like | delta_x_divergence |           5 |                 4 |               1.8176   |                  -0.000586497 |
| wrong_lag_stale_spread     | liquidity_like                       | single             |           5 |                 4 |               0.98088  |                  -0.00123603  |
| wrong_lag_stale_spread     | taker_flow_like\|basis_premium_like  | gated_sign         |           4 |                 4 |               1.06169  |                  -0.000785917 |
| symbol_shuffle_spread      | liquidity_like\|volatility_like      | liquidity_shock    |           3 |                 3 |               2.51076  |                  -0.00102734  |
| time_shuffle_spread        | liquidity_like                       | single             |           3 |                 3 |               1.64921  |                  -0.00121442  |
| time_shuffle_spread        | open_interest_like                   | single             |           2 |                 2 |             100.454    |                  -0.000984078 |
| wrong_lag_stale_spread     | open_interest_like                   | single             |           2 |                 2 |               4.64849  |                  -0.00125151  |
| symbol_shuffle_spread      | liquidity_like                       | single             |           1 |                 1 |               2.06776  |                  -0.00116416  |
| same_family_placebo_spread | open_interest_like                   | single             |           1 |                 1 |              11.3922   |                  -0.00114424  |

## Near Miss Candidates

| candidate_id                   | semantic_bucket                     | motif_bucket    |   replay_rows |   median_spread |   median_cost_adjusted_spread |   max_tstat |   min_control_ratio |   validation_recent_clean_splits | replay_clean   |
|:-------------------------------|:------------------------------------|:----------------|--------------:|----------------:|------------------------------:|------------:|--------------------:|---------------------------------:|:---------------|
| a7ffcore11e_a8d20b6bdd9fb53e86 | taker_flow_like\|basis_premium_like | gated_sign      |            12 |     0.00102972  |                  -3.83035e-05 |     2.85705 |            0.832834 |                                1 | False          |
| a7ffcore11e_ce389ddfa48b59e0f7 | taker_flow_like\|basis_premium_like | gated_sign      |            12 |     0.000329079 |                  -0.0002081   |     2.75121 |            0.844464 |                                1 | False          |
| a7ffcore11e_108bca7372512beafd | taker_flow_like\|basis_premium_like | gated_sign      |            12 |     0.000788985 |                  -0.000224956 |     2.71713 |            0.681327 |                                1 | False          |
| a7ffcore11e_55aaf9f22b9764a1a2 | taker_flow_like\|basis_premium_like | gated_sign      |            12 |     0.000873399 |                  -7.53749e-05 |     2.44686 |            0.79794  |                                1 | False          |
| a7ffcore11e_4ce0c8b245d5808abe | liquidity_like\|volatility_like     | liquidity_shock |            12 |     0.00112935  |                   0.000333791 |     1.90956 |            0.91164  |                                1 | False          |
| a7ffcore11e_7d56c9ecbc9ab9d958 | taker_flow_like\|open_interest_like | flow_x_leverage |            12 |     0.0078873   |                   0.0071873   |     1.88105 |            0.658309 |                                1 | False          |
| a7ffcore11e_a632ea315826e6f709 | liquidity_like                      | single          |            12 |    -0.000665921 |                  -0.00128854  |     1.65606 |            0.62564  |                                1 | False          |
| a7ffcore11e_1942160ee15398d457 | open_interest_like                  | single          |            12 |     7.89736e-06 |                  -0.00037444  |     1.48582 |            0.914855 |                                1 | False          |
| a7ffcore11e_2a2d48956a572ac1ab | liquidity_like\|volatility_like     | liquidity_shock |            12 |     0.0372133   |                   0.0365133   |     1.18513 |            0.93515  |                                1 | False          |

## Boundary

```text
replay rerun: false
formula search / large search: false
promotion: false
alpha proof / shadow / paper / live: false
```
