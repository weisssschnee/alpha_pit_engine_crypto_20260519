# CRYPTO A7FF-CORE7ER REPAIRED NUMERIC RESPONSE

Generated: 2026-05-31T23:10:22Z

## Decision

`PASS_A7FFCORE7ER_REPAIRED_NUMERIC_RESPONSE_READY_FOR_CORE8`

A7FF-CORE7ER is a reclassification of CORE7E response rows under the CORE7R repaired control policy. It does not run portfolio replay, search, promotion, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core8_contract": true,
  "authorizes_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE7ER_REPAIRED_NUMERIC_RESPONSE_READY_FOR_CORE8",
  "executes_numeric_reclassification": true,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-31T23:10:22Z",
  "label_family_count_with_clues": 3,
  "next_allowed": "A7FF-CORE8 numeric clue consolidation / replay-preflight contract",
  "numeric_clue_candidate_count": 472,
  "numeric_clue_rows": 942,
  "primary_non_l7_clue_rows": 942,
  "response_rows": 40960,
  "semantic_bucket_count_with_clues": 9,
  "sign_flip_policy": "diagnostic_only_excluded_from_abs_max_control",
  "source_decision": "PASS_A7FFCORE7R_CONTROL_POLICY_REPAIR_REQUIRED_READY_FOR_CORE7ER",
  "source_stage": "A7FF-CORE7R",
  "stage": "A7FF-CORE7ER"
}
```

## Label Summary

| label_id                           |   horizon |   rows |   numeric_clues |   candidate_count |   median_abs_corr |   median_control_ratio |   median_sign_flip_diagnostic_ratio |
|:-----------------------------------|----------:|-------:|----------------:|------------------:|------------------:|-----------------------:|------------------------------------:|
| L3_liquidity_tier_relative_return  |         4 |   2048 |             114 |              2048 |        0.00209748 |                2.70505 |                                   1 |
| L1_cross_sectional_relative_return |         4 |   2048 |             101 |              2048 |        0.00240584 |                2.75671 |                                   1 |
| L1_cross_sectional_relative_return |        24 |   2048 |              92 |              2048 |        0.00225949 |                1.84512 |                                   1 |
| L5_vol_adjusted_return             |         8 |   2048 |              88 |              2048 |        0.00219428 |                1.69884 |                                   1 |
| L3_liquidity_tier_relative_return  |         8 |   2048 |              88 |              2048 |        0.00236324 |                2.62558 |                                   1 |
| L1_cross_sectional_relative_return |         8 |   2048 |              85 |              2048 |        0.00212835 |                2.86087 |                                   1 |
| L3_liquidity_tier_relative_return  |        24 |   2048 |              74 |              2048 |        0.00222545 |                2.11695 |                                   1 |
| L5_vol_adjusted_return             |         4 |   2048 |              69 |              2048 |        0.00262764 |                2.0205  |                                   1 |
| L3_liquidity_tier_relative_return  |         1 |   2048 |              67 |              2048 |        0.00218463 |                3.7056  |                                   1 |
| L1_cross_sectional_relative_return |         1 |   2048 |              63 |              2048 |        0.00279358 |                2.96904 |                                   1 |
| L5_vol_adjusted_return             |        24 |   2048 |              59 |              2048 |        0.00165209 |                2.09001 |                                   1 |
| L5_vol_adjusted_return             |         1 |   2048 |              42 |              2048 |        0.00224189 |                3.19629 |                                   1 |
| L7_ranked_future_return            |        24 |   2048 |               0 |              2048 |        0.00496372 |                1.00251 |                                   1 |
| L7_ranked_future_return            |         4 |   2048 |               0 |              2048 |        0.00380063 |                1.02774 |                                   1 |
| L7_ranked_future_return            |         8 |   2048 |               0 |              2048 |        0.00371876 |                1.03334 |                                   1 |
| L7_ranked_future_return            |         1 |   2048 |               0 |              2048 |        0.00331615 |                1.69764 |                                   1 |
| L0_raw_forward_return              |        24 |   2048 |               0 |              2048 |        0.00220993 |                1.84164 |                                   1 |
| L0_raw_forward_return              |         8 |   2048 |               0 |              2048 |        0.00232868 |                1.93618 |                                   1 |
| L0_raw_forward_return              |         4 |   2048 |               0 |              2048 |        0.00282683 |                1.99069 |                                   1 |
| L0_raw_forward_return              |         1 |   2048 |               0 |              2048 |        0.00295127 |                2.83077 |                                   1 |

## Family Summary

| semantic_bucket                      | motif_bucket        |   rows |   candidate_count |   numeric_clues |   median_control_ratio |   median_sign_flip_diagnostic_ratio |
|:-------------------------------------|:--------------------|-------:|------------------:|----------------:|-----------------------:|------------------------------------:|
| liquidity_like\|volatility_like      | safe_div_abs        |   6400 |               320 |             312 |                1.6993  |                                   1 |
| liquidity_like\|volatility_like      | liquidity_shock     |   7400 |               370 |             246 |                1.87675 |                                   1 |
| taker_flow_like\|open_interest_like  | flow_x_leverage     |   3840 |               192 |             127 |                1.91941 |                                   1 |
| open_interest_like\|price_like       | mean_reversion_gate |   2960 |               148 |             124 |                1.95026 |                                   1 |
| liquidity_like\|volatility_like      | mean_reversion_gate |   7200 |               360 |              39 |                2.05209 |                                   1 |
| taker_flow_like                      | single              |    760 |                38 |              33 |                2.53507 |                                   1 |
| liquidity_like                       | single              |   1960 |                98 |              17 |                1.26515 |                                   1 |
| taker_flow_like\|basis_premium_like  | gated_sign          |   3840 |               192 |              16 |                3.05538 |                                   1 |
| open_interest_like                   | single              |    400 |                20 |               9 |                2.15033 |                                   1 |
| volatility_like                      | single              |    280 |                14 |               6 |                1.59267 |                                   1 |
| liquidity_like                       | liquidity_shock     |    200 |                10 |               5 |                1.38178 |                                   1 |
| open_interest_like                   | delta_x_divergence  |    400 |                20 |               4 |                1.40592 |                                   1 |
| open_interest_like\|positioning_like | delta_x_divergence  |   3840 |               192 |               2 |                4.93406 |                                   1 |
| open_interest_like\|price_like       | delta_x_divergence  |    880 |                44 |               2 |                7.18699 |                                   1 |
| taker_flow_like                      | flow_x_leverage     |    200 |                10 |               0 |                2.15173 |                                   1 |
| open_interest_like                   | flow_x_leverage     |    400 |                20 |               0 |                2.64814 |                                   1 |

## Candidate Queue Preview

| candidate_id                 | semantic_bucket                     | motif_bucket        |   clue_rows |   label_count |   horizon_count |   best_abs_corr |   best_original_score |   min_control_ratio |
|:-----------------------------|:------------------------------------|:--------------------|------------:|--------------:|----------------:|----------------:|----------------------:|--------------------:|
| a7ffcore5_f408fcf92eed3e3cea | liquidity_like\|volatility_like     | safe_div_abs        |           9 |             3 |               4 |      0.011576   |            0.82509    |            0.289414 |
| a7ffcore5_b14219288b18bf0b0c | liquidity_like\|volatility_like     | safe_div_abs        |           9 |             3 |               3 |      0.00541693 |            0.332745   |            0.317358 |
| a7ffcore5_fe6ab6fb0843878019 | liquidity_like\|volatility_like     | safe_div_abs        |           7 |             3 |               3 |      0.00989569 |            0.121985   |            0.11754  |
| a7ffcore5_1f8c481e4c787863b8 | liquidity_like\|volatility_like     | safe_div_abs        |           7 |             3 |               4 |      0.00520631 |            0.0726522  |            0.228618 |
| a7ffcore5_f414f2621b03d718f6 | open_interest_like\|price_like      | mean_reversion_gate |           7 |             3 |               3 |      0.00701415 |            0.697434   |            0.336401 |
| a7ffcore5_291837028072641a1c | liquidity_like\|volatility_like     | safe_div_abs        |           7 |             2 |               4 |      0.00947722 |            0.00947722 |            0.452409 |
| a7ffcore5_89d456568ed9db84c6 | liquidity_like\|volatility_like     | liquidity_shock     |           7 |             2 |               4 |      0.00714392 |            0.00714392 |            0.454497 |
| a7ffcore5_55d479db927df299ef | liquidity_like\|volatility_like     | liquidity_shock     |           7 |             2 |               4 |      0.00909346 |            0.00909346 |            0.456325 |
| a7ffcore5_0df84c13bb1ed0cc5e | liquidity_like\|volatility_like     | safe_div_abs        |           6 |             3 |               3 |      0.00604326 |            0.188748   |            0.250641 |
| a7ffcore5_2785be37d31870a000 | open_interest_like\|price_like      | mean_reversion_gate |           6 |             3 |               3 |      0.00911111 |            0.421912   |            0.333168 |
| a7ffcore5_fdc24ebd7772041b83 | open_interest_like\|price_like      | mean_reversion_gate |           6 |             3 |               3 |      0.00839055 |            0.421912   |            0.490987 |
| a7ffcore5_e8b09c1c628442bb96 | liquidity_like\|volatility_like     | safe_div_abs        |           6 |             3 |               3 |      0.00339047 |            0.170332   |            0.516392 |
| a7ffcore5_c5ecfea1d2af189266 | open_interest_like\|price_like      | mean_reversion_gate |           6 |             3 |               3 |      0.00702791 |            0.697434   |            0.556763 |
| a7ffcore5_e49456a170f19eb240 | liquidity_like\|volatility_like     | liquidity_shock     |           6 |             2 |               3 |      0.00849883 |            0.00849883 |            0.239753 |
| a7ffcore5_4a1f7c7ea34e49f970 | liquidity_like\|volatility_like     | liquidity_shock     |           6 |             2 |               3 |      0.00965827 |            0.00965827 |            0.286232 |
| a7ffcore5_0d36019628d9445207 | liquidity_like\|volatility_like     | safe_div_abs        |           6 |             2 |               3 |      0.010176   |            0.010176   |            0.293924 |
| a7ffcore5_0460706c8101b16f2f | liquidity_like\|volatility_like     | liquidity_shock     |           6 |             2 |               3 |      0.00932367 |            0.00932367 |            0.337376 |
| a7ffcore5_6f285061a4d5fa2922 | liquidity_like\|volatility_like     | liquidity_shock     |           6 |             2 |               3 |      0.00880079 |            0.00880079 |            0.344398 |
| a7ffcore5_11903004dcea88bab8 | liquidity_like\|volatility_like     | liquidity_shock     |           6 |             2 |               3 |      0.00693098 |            0.00693098 |            0.357396 |
| a7ffcore5_134c181d2d0d0a7a0d | liquidity_like\|volatility_like     | liquidity_shock     |           6 |             2 |               3 |      0.00688011 |            0.00688011 |            0.374323 |
| a7ffcore5_056264aa1859f3ac7b | liquidity_like\|volatility_like     | liquidity_shock     |           6 |             2 |               3 |      0.00721778 |            0.00721778 |            0.398326 |
| a7ffcore5_347cfd7114f3a1ae41 | liquidity_like\|volatility_like     | liquidity_shock     |           6 |             2 |               3 |      0.0071799  |            0.0071799  |            0.453217 |
| a7ffcore5_155172eb90a4ffee4e | liquidity_like\|volatility_like     | liquidity_shock     |           6 |             2 |               3 |      0.0092243  |            0.0092243  |            0.498733 |
| a7ffcore5_f12228440913b31bb1 | liquidity_like\|volatility_like     | liquidity_shock     |           6 |             2 |               4 |      0.00584148 |            0.00584148 |            0.578649 |
| a7ffcore5_74192e756c0281059e | liquidity_like\|volatility_like     | safe_div_abs        |           5 |             3 |               3 |      0.00673664 |            0.21761    |            0.250737 |
| a7ffcore5_7f1edcbee2c722cdf1 | liquidity_like\|volatility_like     | safe_div_abs        |           5 |             3 |               3 |      0.00888354 |            0.0841855  |            0.258469 |
| a7ffcore5_c3c0979a0680ff0e0b | liquidity_like\|volatility_like     | safe_div_abs        |           5 |             3 |               3 |      0.00503813 |            0.147796   |            0.410584 |
| a7ffcore5_bfdcfe65197b45a109 | liquidity_like\|volatility_like     | safe_div_abs        |           5 |             3 |               3 |      0.00491546 |            0.129248   |            0.486849 |
| a7ffcore5_a895511071d86b79ed | liquidity_like\|volatility_like     | liquidity_shock     |           5 |             2 |               3 |      0.00860811 |            0.00860811 |            0.232383 |
| a7ffcore5_2545209b43e8b162b7 | taker_flow_like\|open_interest_like | flow_x_leverage     |           5 |             2 |               3 |      0.0152397  |            0.0152397  |            0.254719 |
| a7ffcore5_25b2704821ce1d532b | taker_flow_like\|basis_premium_like | gated_sign          |           5 |             2 |               3 |      0.00747045 |            0.00747045 |            0.357002 |
| a7ffcore5_a3af6b68eb21e4cf8a | open_interest_like\|price_like      | mean_reversion_gate |           5 |             2 |               3 |      0.0071903  |            0.0071903  |            0.357297 |
| a7ffcore5_b39e253ad9a5084d9a | taker_flow_like\|open_interest_like | flow_x_leverage     |           5 |             2 |               4 |      0.0168127  |            0.0168127  |            0.36899  |
| a7ffcore5_7b644717231e2e4c0f | liquidity_like\|volatility_like     | liquidity_shock     |           5 |             2 |               3 |      0.00632988 |            0.00632988 |            0.484305 |
| a7ffcore5_f30aafe4b28c1858df | liquidity_like\|volatility_like     | safe_div_abs        |           5 |             2 |               3 |      0.00598654 |            0.00598654 |            0.52623  |
| a7ffcore5_c4c5f31eb4497fe49b | liquidity_like\|volatility_like     | liquidity_shock     |           5 |             2 |               3 |      0.00693801 |            0.00693801 |            0.593013 |
| a7ffcore5_1caefe1090deb89fed | open_interest_like\|price_like      | mean_reversion_gate |           4 |             3 |               2 |      0.00319912 |            0.285611   |            0.497927 |
| a7ffcore5_1366945af1d14e8e7b | open_interest_like\|price_like      | mean_reversion_gate |           4 |             3 |               2 |      0.00319912 |            0.285611   |            0.512087 |
| a7ffcore5_f705fad1a710ad28f0 | taker_flow_like                     | single              |           4 |             3 |               3 |      0.00583624 |            0.394925   |            0.589722 |
| a7ffcore5_c0a1717103dfa241aa | liquidity_like\|volatility_like     | liquidity_shock     |           4 |             3 |               2 |      0.0238237  |            0.461055   |            0.705735 |
| a7ffcore5_4a41bd8402951175d2 | liquidity_like\|volatility_like     | safe_div_abs        |           4 |             2 |               2 |      0.00721602 |            0.00721602 |            0.259146 |
| a7ffcore5_d2f366c1206f978251 | liquidity_like\|volatility_like     | liquidity_shock     |           4 |             2 |               2 |      0.0080723  |            0.0080723  |            0.290393 |
| a7ffcore5_f6b68337053909c984 | liquidity_like\|volatility_like     | safe_div_abs        |           4 |             2 |               2 |      0.00895004 |            0.00895004 |            0.293338 |
| a7ffcore5_63939f40a439f34abb | taker_flow_like\|open_interest_like | flow_x_leverage     |           4 |             2 |               3 |      0.0164627  |            0.0164627  |            0.306389 |
| a7ffcore5_da74c58e23ee9194a0 | liquidity_like\|volatility_like     | safe_div_abs        |           4 |             2 |               4 |      0.011498   |            0.011498   |            0.334251 |
| a7ffcore5_7bbbc611697574863a | open_interest_like\|price_like      | mean_reversion_gate |           4 |             2 |               2 |      0.00918235 |            0.00918235 |            0.385487 |
| a7ffcore5_0c7553f528852f7b80 | liquidity_like\|volatility_like     | safe_div_abs        |           4 |             2 |               2 |      0.00608585 |            0.00608585 |            0.402096 |
| a7ffcore5_ac1bc78121a46a2130 | liquidity_like\|volatility_like     | liquidity_shock     |           4 |             2 |               2 |      0.0110218  |            0.0110218  |            0.431459 |
| a7ffcore5_1f43d8b7466f67685b | taker_flow_like\|open_interest_like | flow_x_leverage     |           4 |             2 |               3 |      0.0172685  |            0.0172685  |            0.434151 |
| a7ffcore5_319bd70753eb1b3dd5 | liquidity_like\|volatility_like     | liquidity_shock     |           4 |             2 |               2 |      0.00877802 |            0.00877802 |            0.462667 |
| a7ffcore5_140f73cd68cce7fa93 | liquidity_like\|volatility_like     | safe_div_abs        |           4 |             2 |               2 |      0.006408   |            0.006408   |            0.479526 |
| a7ffcore5_98a14a14e827fb72fc | liquidity_like\|volatility_like     | liquidity_shock     |           4 |             2 |               2 |      0.00848868 |            0.00848868 |            0.487967 |
| a7ffcore5_de531765e26fffdd63 | liquidity_like\|volatility_like     | liquidity_shock     |           4 |             2 |               2 |      0.00509489 |            0.00509489 |            0.568682 |
| a7ffcore5_ecd4842409aef0a3d8 | liquidity_like\|volatility_like     | liquidity_shock     |           4 |             2 |               2 |      0.00842033 |            0.00842033 |            0.625949 |
| a7ffcore5_ffef9b7e4d278d80f8 | liquidity_like\|volatility_like     | liquidity_shock     |           4 |             2 |               2 |      0.00842033 |            0.00842033 |            0.625949 |
| a7ffcore5_62b8cb67b35dfdc506 | liquidity_like\|volatility_like     | safe_div_abs        |           3 |             3 |               2 |      0.00538413 |            0.0693335  |            0.22637  |
| a7ffcore5_3d1036bce80ff6e4e8 | taker_flow_like\|open_interest_like | flow_x_leverage     |           3 |             3 |               3 |      0.0100538  |            0.0274715  |            0.330462 |
| a7ffcore5_4ebc4ef80f2bd8372b | liquidity_like\|volatility_like     | safe_div_abs        |           3 |             3 |               2 |      0.00685762 |            0.135205   |            0.546728 |
| a7ffcore5_c9d694b8d10cbddcb0 | liquidity_like\|volatility_like     | liquidity_shock     |           3 |             3 |               2 |      0.0220456  |            0.12294    |            0.564833 |
| a7ffcore5_b594b57d1ee90136c4 | volatility_like                     | single              |           3 |             3 |               2 |      0.0293408  |            0.635793   |            0.566096 |

## Boundary

```text
numeric response reclassified: true
portfolio replay: false
search: false
promotion: false
sign_flip: diagnostic-only, excluded from absolute max-control dominance
```
