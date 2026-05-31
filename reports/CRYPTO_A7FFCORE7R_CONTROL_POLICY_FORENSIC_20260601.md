# CRYPTO A7FF-CORE7R CONTROL POLICY FORENSIC

Generated: 2026-05-31T23:08:53Z

## Decision

`PASS_A7FFCORE7R_CONTROL_POLICY_REPAIR_REQUIRED_READY_FOR_CORE7ER`

A7FF-CORE7R does not run search, replay, promotion, alpha proof, shadow, paper, or live. It audits whether CORE7E's control policy mechanically blocked all numeric clues.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core7er": true,
  "authorizes_core8": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE7R_CONTROL_POLICY_REPAIR_REQUIRED_READY_FOR_CORE7ER",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-31T23:08:53Z",
  "next_allowed": "A7FF-CORE7ER repaired numeric-response rerun with sign_flip diagnostic-only policy",
  "non_sign_controls": [
    "time_shuffle",
    "symbol_shuffle",
    "same_family_placebo",
    "wrong_lag_future",
    "wrong_lag_stale"
  ],
  "primary_non_l7_repaired_clue_rows": 942,
  "repaired_candidate_count": 472,
  "repaired_numeric_clue_rows": 942,
  "response_rows": 40960,
  "sign_flip_policy": "diagnostic_only_not_allowed_in_abs_max_control_score",
  "sign_flip_tautology_share": 1.0,
  "source_decision": "HOLD_A7FFCORE7E_NUMERIC_RESPONSE_WEAK",
  "source_numeric_clue_rows": 0,
  "source_stage": "A7FF-CORE7E",
  "stage": "A7FF-CORE7R"
}
```

## Control Summary

| control             |   median_ratio |   p90_ratio |   ratio_ge_1_share |
|:--------------------|---------------:|------------:|-------------------:|
| time_shuffle        |       0.595091 |     3.52318 |           0.34917  |
| symbol_shuffle      |       0.393279 |     2.47586 |           0.258911 |
| same_family_placebo |       0.393554 |     2.70616 |           0.266309 |
| wrong_lag_future    |       1.38483  |     8.68647 |           0.672632 |
| wrong_lag_stale     |       0.86103  |     3.09733 |           0.398071 |
| sign_flip           |       1        |     1       |           1        |

## Repaired Label Summary

| label_id                           |   horizon |   rows |   repaired_numeric_clues |   original_numeric_clues |   median_original_control_ratio |   median_non_sign_control_ratio |   median_sign_flip_ratio |
|:-----------------------------------|----------:|-------:|-------------------------:|-------------------------:|--------------------------------:|--------------------------------:|-------------------------:|
| L3_liquidity_tier_relative_return  |         4 |   2048 |                      114 |                        0 |                         2.70505 |                         2.70505 |                        1 |
| L1_cross_sectional_relative_return |         4 |   2048 |                      101 |                        0 |                         2.75671 |                         2.75671 |                        1 |
| L1_cross_sectional_relative_return |        24 |   2048 |                       92 |                        0 |                         1.84512 |                         1.84512 |                        1 |
| L5_vol_adjusted_return             |         8 |   2048 |                       88 |                        0 |                         1.69884 |                         1.69884 |                        1 |
| L3_liquidity_tier_relative_return  |         8 |   2048 |                       88 |                        0 |                         2.62558 |                         2.62558 |                        1 |
| L1_cross_sectional_relative_return |         8 |   2048 |                       85 |                        0 |                         2.86087 |                         2.86087 |                        1 |
| L3_liquidity_tier_relative_return  |        24 |   2048 |                       74 |                        0 |                         2.11695 |                         2.11695 |                        1 |
| L5_vol_adjusted_return             |         4 |   2048 |                       69 |                        0 |                         2.0205  |                         2.0205  |                        1 |
| L3_liquidity_tier_relative_return  |         1 |   2048 |                       67 |                        0 |                         3.7056  |                         3.7056  |                        1 |
| L1_cross_sectional_relative_return |         1 |   2048 |                       63 |                        0 |                         2.96904 |                         2.96904 |                        1 |
| L5_vol_adjusted_return             |        24 |   2048 |                       59 |                        0 |                         2.09001 |                         2.09001 |                        1 |
| L5_vol_adjusted_return             |         1 |   2048 |                       42 |                        0 |                         3.19629 |                         3.19629 |                        1 |
| L7_ranked_future_return            |        24 |   2048 |                        0 |                        0 |                         1.00251 |                         1.00251 |                        1 |
| L7_ranked_future_return            |         4 |   2048 |                        0 |                        0 |                         1.02774 |                         1.02774 |                        1 |
| L7_ranked_future_return            |         8 |   2048 |                        0 |                        0 |                         1.03334 |                         1.03334 |                        1 |
| L7_ranked_future_return            |         1 |   2048 |                        0 |                        0 |                         1.69764 |                         1.69764 |                        1 |
| L0_raw_forward_return              |        24 |   2048 |                        0 |                        0 |                         1.84164 |                         1.84164 |                        1 |
| L0_raw_forward_return              |         8 |   2048 |                        0 |                        0 |                         1.93618 |                         1.93618 |                        1 |
| L0_raw_forward_return              |         4 |   2048 |                        0 |                        0 |                         1.99069 |                         1.99069 |                        1 |
| L0_raw_forward_return              |         1 |   2048 |                        0 |                        0 |                         2.83077 |                         2.83077 |                        1 |

## Repaired Family Summary

| semantic_bucket                      | motif_bucket        |   rows |   candidate_count |   repaired_numeric_clues |   original_numeric_clues |   median_non_sign_control_ratio |   median_sign_flip_ratio |
|:-------------------------------------|:--------------------|-------:|------------------:|-------------------------:|-------------------------:|--------------------------------:|-------------------------:|
| liquidity_like\|volatility_like      | safe_div_abs        |   6400 |               320 |                      312 |                        0 |                         1.6993  |                        1 |
| liquidity_like\|volatility_like      | liquidity_shock     |   7400 |               370 |                      246 |                        0 |                         1.87675 |                        1 |
| taker_flow_like\|open_interest_like  | flow_x_leverage     |   3840 |               192 |                      127 |                        0 |                         1.91941 |                        1 |
| open_interest_like\|price_like       | mean_reversion_gate |   2960 |               148 |                      124 |                        0 |                         1.95026 |                        1 |
| liquidity_like\|volatility_like      | mean_reversion_gate |   7200 |               360 |                       39 |                        0 |                         2.05209 |                        1 |
| taker_flow_like                      | single              |    760 |                38 |                       33 |                        0 |                         2.53507 |                        1 |
| liquidity_like                       | single              |   1960 |                98 |                       17 |                        0 |                         1.26515 |                        1 |
| taker_flow_like\|basis_premium_like  | gated_sign          |   3840 |               192 |                       16 |                        0 |                         3.05538 |                        1 |
| open_interest_like                   | single              |    400 |                20 |                        9 |                        0 |                         2.15033 |                        1 |
| volatility_like                      | single              |    280 |                14 |                        6 |                        0 |                         1.59267 |                        1 |
| liquidity_like                       | liquidity_shock     |    200 |                10 |                        5 |                        0 |                         1.38178 |                        1 |
| open_interest_like                   | delta_x_divergence  |    400 |                20 |                        4 |                        0 |                         1.40592 |                        1 |
| open_interest_like\|positioning_like | delta_x_divergence  |   3840 |               192 |                        2 |                        0 |                         4.93406 |                        1 |
| open_interest_like\|price_like       | delta_x_divergence  |    880 |                44 |                        2 |                        0 |                         7.18699 |                        1 |
| taker_flow_like                      | flow_x_leverage     |    200 |                10 |                        0 |                        0 |                         2.15173 |                        1 |
| open_interest_like                   | flow_x_leverage     |    400 |                20 |                        0 |                        0 |                         2.64814 |                        1 |

## Top Repaired Candidate Summary

| candidate_id                 | semantic_bucket                     | motif_bucket        |   clue_rows |   best_abs_corr |   best_original_score |   min_non_sign_control_ratio |
|:-----------------------------|:------------------------------------|:--------------------|------------:|----------------:|----------------------:|-----------------------------:|
| a7ffcore5_f408fcf92eed3e3cea | liquidity_like\|volatility_like     | safe_div_abs        |           9 |      0.011576   |            0.82509    |                     0.289414 |
| a7ffcore5_b14219288b18bf0b0c | liquidity_like\|volatility_like     | safe_div_abs        |           9 |      0.00541693 |            0.332745   |                     0.317358 |
| a7ffcore5_fe6ab6fb0843878019 | liquidity_like\|volatility_like     | safe_div_abs        |           7 |      0.00989569 |            0.121985   |                     0.11754  |
| a7ffcore5_1f8c481e4c787863b8 | liquidity_like\|volatility_like     | safe_div_abs        |           7 |      0.00520631 |            0.0726522  |                     0.228618 |
| a7ffcore5_f414f2621b03d718f6 | open_interest_like\|price_like      | mean_reversion_gate |           7 |      0.00701415 |            0.697434   |                     0.336401 |
| a7ffcore5_291837028072641a1c | liquidity_like\|volatility_like     | safe_div_abs        |           7 |      0.00947722 |            0.00947722 |                     0.452409 |
| a7ffcore5_89d456568ed9db84c6 | liquidity_like\|volatility_like     | liquidity_shock     |           7 |      0.00714392 |            0.00714392 |                     0.454497 |
| a7ffcore5_55d479db927df299ef | liquidity_like\|volatility_like     | liquidity_shock     |           7 |      0.00909346 |            0.00909346 |                     0.456325 |
| a7ffcore5_e49456a170f19eb240 | liquidity_like\|volatility_like     | liquidity_shock     |           6 |      0.00849883 |            0.00849883 |                     0.239753 |
| a7ffcore5_0df84c13bb1ed0cc5e | liquidity_like\|volatility_like     | safe_div_abs        |           6 |      0.00604326 |            0.188748   |                     0.250641 |
| a7ffcore5_4a1f7c7ea34e49f970 | liquidity_like\|volatility_like     | liquidity_shock     |           6 |      0.00965827 |            0.00965827 |                     0.286232 |
| a7ffcore5_0d36019628d9445207 | liquidity_like\|volatility_like     | safe_div_abs        |           6 |      0.010176   |            0.010176   |                     0.293924 |
| a7ffcore5_2785be37d31870a000 | open_interest_like\|price_like      | mean_reversion_gate |           6 |      0.00911111 |            0.421912   |                     0.333168 |
| a7ffcore5_0460706c8101b16f2f | liquidity_like\|volatility_like     | liquidity_shock     |           6 |      0.00932367 |            0.00932367 |                     0.337376 |
| a7ffcore5_6f285061a4d5fa2922 | liquidity_like\|volatility_like     | liquidity_shock     |           6 |      0.00880079 |            0.00880079 |                     0.344398 |
| a7ffcore5_11903004dcea88bab8 | liquidity_like\|volatility_like     | liquidity_shock     |           6 |      0.00693098 |            0.00693098 |                     0.357396 |
| a7ffcore5_134c181d2d0d0a7a0d | liquidity_like\|volatility_like     | liquidity_shock     |           6 |      0.00688011 |            0.00688011 |                     0.374323 |
| a7ffcore5_056264aa1859f3ac7b | liquidity_like\|volatility_like     | liquidity_shock     |           6 |      0.00721778 |            0.00721778 |                     0.398326 |
| a7ffcore5_347cfd7114f3a1ae41 | liquidity_like\|volatility_like     | liquidity_shock     |           6 |      0.0071799  |            0.0071799  |                     0.453217 |
| a7ffcore5_fdc24ebd7772041b83 | open_interest_like\|price_like      | mean_reversion_gate |           6 |      0.00839055 |            0.421912   |                     0.490987 |
| a7ffcore5_155172eb90a4ffee4e | liquidity_like\|volatility_like     | liquidity_shock     |           6 |      0.0092243  |            0.0092243  |                     0.498733 |
| a7ffcore5_e8b09c1c628442bb96 | liquidity_like\|volatility_like     | safe_div_abs        |           6 |      0.00339047 |            0.170332   |                     0.516392 |
| a7ffcore5_c5ecfea1d2af189266 | open_interest_like\|price_like      | mean_reversion_gate |           6 |      0.00702791 |            0.697434   |                     0.556763 |
| a7ffcore5_f12228440913b31bb1 | liquidity_like\|volatility_like     | liquidity_shock     |           6 |      0.00584148 |            0.00584148 |                     0.578649 |
| a7ffcore5_a895511071d86b79ed | liquidity_like\|volatility_like     | liquidity_shock     |           5 |      0.00860811 |            0.00860811 |                     0.232383 |
| a7ffcore5_74192e756c0281059e | liquidity_like\|volatility_like     | safe_div_abs        |           5 |      0.00673664 |            0.21761    |                     0.250737 |
| a7ffcore5_2545209b43e8b162b7 | taker_flow_like\|open_interest_like | flow_x_leverage     |           5 |      0.0152397  |            0.0152397  |                     0.254719 |
| a7ffcore5_7f1edcbee2c722cdf1 | liquidity_like\|volatility_like     | safe_div_abs        |           5 |      0.00888354 |            0.0841855  |                     0.258469 |
| a7ffcore5_25b2704821ce1d532b | taker_flow_like\|basis_premium_like | gated_sign          |           5 |      0.00747045 |            0.00747045 |                     0.357002 |
| a7ffcore5_a3af6b68eb21e4cf8a | open_interest_like\|price_like      | mean_reversion_gate |           5 |      0.0071903  |            0.0071903  |                     0.357297 |
| a7ffcore5_b39e253ad9a5084d9a | taker_flow_like\|open_interest_like | flow_x_leverage     |           5 |      0.0168127  |            0.0168127  |                     0.36899  |
| a7ffcore5_c3c0979a0680ff0e0b | liquidity_like\|volatility_like     | safe_div_abs        |           5 |      0.00503813 |            0.147796   |                     0.410584 |
| a7ffcore5_7b644717231e2e4c0f | liquidity_like\|volatility_like     | liquidity_shock     |           5 |      0.00632988 |            0.00632988 |                     0.484305 |
| a7ffcore5_bfdcfe65197b45a109 | liquidity_like\|volatility_like     | safe_div_abs        |           5 |      0.00491546 |            0.129248   |                     0.486849 |
| a7ffcore5_f30aafe4b28c1858df | liquidity_like\|volatility_like     | safe_div_abs        |           5 |      0.00598654 |            0.00598654 |                     0.52623  |
| a7ffcore5_c4c5f31eb4497fe49b | liquidity_like\|volatility_like     | liquidity_shock     |           5 |      0.00693801 |            0.00693801 |                     0.593013 |
| a7ffcore5_4a41bd8402951175d2 | liquidity_like\|volatility_like     | safe_div_abs        |           4 |      0.00721602 |            0.00721602 |                     0.259146 |
| a7ffcore5_d2f366c1206f978251 | liquidity_like\|volatility_like     | liquidity_shock     |           4 |      0.0080723  |            0.0080723  |                     0.290393 |
| a7ffcore5_f6b68337053909c984 | liquidity_like\|volatility_like     | safe_div_abs        |           4 |      0.00895004 |            0.00895004 |                     0.293338 |
| a7ffcore5_63939f40a439f34abb | taker_flow_like\|open_interest_like | flow_x_leverage     |           4 |      0.0164627  |            0.0164627  |                     0.306389 |

## Boundary

```text
sign_flip is retained only as an orientation diagnostic.
sign_flip is not eligible for absolute max-control dominance because abs(score(sign_flip)) is mechanically equal to abs(score(original)).
This stage only authorizes a repaired numeric-response rerun; it does not authorize replay/search/promotion.
```
