# CRYPTO A7FF-CORE52F DIAGNOSTIC CLUE FORENSIC

Generated: 2026-06-02T09:48:13Z

## Decision

`HOLD_A7FFCORE52F_LABEL_REDUNDANCY_AND_THIN_CONTROL_MARGIN`

CORE52F explains why CORE52 diagnostic clues are insufficient for search. It does not execute replay, generation, proof, or promotion.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core53_replay_target_repair_contract": true,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "HOLD_A7FFCORE52F_LABEL_REDUNDANCY_AND_THIN_CONTROL_MARGIN",
  "diagnostic_clue_count": 35,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-02T09:48:13Z",
  "redundant_l0_l1_horizon_count": 4,
  "single_horizon_clue_count": 25,
  "source_decision": "HOLD_A7FFCORE52_DIAGNOSTIC_CLUES_INSUFFICIENT_FOR_SEARCH",
  "source_stage": "A7FF-CORE52",
  "stage": "A7FF-CORE52F",
  "strict_replay_clue_count": 1,
  "thin_control_margin_clue_count": 34
}
```

## Label Redundancy

| horizon   |   common_seed_count |   max_abs_diff_original_spread_mean |   median_abs_diff_original_spread_mean |   max_abs_diff_original_tstat |   median_abs_diff_original_tstat |   max_abs_diff_control_ratio |   median_abs_diff_control_ratio |   max_abs_diff_stale_spread_mean |   median_abs_diff_stale_spread_mean |   max_abs_diff_time_shuffle_spread_mean |   median_abs_diff_time_shuffle_spread_mean |   max_abs_diff_symbol_shuffle_spread_mean |   median_abs_diff_symbol_shuffle_spread_mean |   max_abs_diff_sign_flip_spread_mean |   median_abs_diff_sign_flip_spread_mean | is_redundant_for_decile_spread   |
|:----------|--------------------:|------------------------------------:|---------------------------------------:|------------------------------:|---------------------------------:|-----------------------------:|--------------------------------:|---------------------------------:|------------------------------------:|----------------------------------------:|-------------------------------------------:|------------------------------------------:|---------------------------------------------:|-------------------------------------:|----------------------------------------:|:---------------------------------|
| 1h        |                 384 |                         3.7404e-11  |                            7.03811e-13 |                   9.65218e-08 |                      2.12471e-08 |                  0.00740198  |                     9.61483e-09 |                      3.35741e-11 |                         7.49464e-13 |                             1.91574e-11 |                                8.40413e-13 |                               2.70892e-11 |                                  8.07263e-13 |                          3.7404e-11  |                             7.33613e-13 | True                             |
| 4h        |                 384 |                         1.49458e-10 |                            1.92051e-12 |                   1.59904e-07 |                      2.90995e-08 |                  0.000166433 |                     6.63962e-09 |                      1.46271e-10 |                         1.85738e-12 |                             8.95463e-11 |                                1.46765e-12 |                               3.35516e-11 |                                  1.48914e-12 |                          1.49458e-10 |                             1.76844e-12 | True                             |
| 8h        |                 384 |                         1.51838e-10 |                            2.0693e-12  |                   1.158e-07   |                      2.32132e-08 |                  0.000663025 |                     4.38065e-09 |                      9.73064e-11 |                         2.1153e-12  |                             8.89452e-11 |                                2.1183e-12  |                               8.53579e-11 |                                  1.63419e-12 |                          1.51838e-10 |                             2.07048e-12 | True                             |
| 24h       |                 384 |                         1.55772e-10 |                            3.718e-12   |                   9.78431e-08 |                      2.276e-08   |                  0.00814273  |                     6.7714e-09  |                      1.93192e-10 |                         4.01144e-12 |                             1.26599e-10 |                                3.62952e-12 |                               1.00969e-10 |                                  3.06142e-12 |                          1.55772e-10 |                             3.6685e-12  | True                             |

## Control Margin Forensic

| seed_id           | arbitration_status   | semantic_pair                         | operator        |   clean_label_count |   clean_horizons |   median_control_ratio |   control_margin | thin_control_margin   |
|:------------------|:---------------------|:--------------------------------------|:----------------|--------------------:|-----------------:|-----------------------:|-----------------:|:----------------------|
| a7ffcore48se_0219 | diagnostic_clue      | price_like|price_like                 | Identity        |                   8 |                4 |               0.995587 |      0.00441341  | True                  |
| a7ffcore48se_1397 | diagnostic_clue      | basis_premium_like|price_like         | Identity        |                   8 |                4 |               0.99657  |      0.00343021  | True                  |
| a7ffcore48se_0248 | strict_replay_clue   | state_or_taxonomy|state_or_taxonomy   | SignedRankDelta |                   6 |                3 |               0.882984 |      0.117016    | False                 |
| a7ffcore48se_1159 | diagnostic_clue      | funding_like|funding_like             | WinsorZ         |                   6 |                3 |               0.968402 |      0.0315983   | True                  |
| a7ffcore48se_0824 | diagnostic_clue      | basis_premium_like|basis_premium_like | Identity        |                   6 |                3 |               0.998515 |      0.00148521  | True                  |
| a7ffcore48se_0545 | diagnostic_clue      | basis_premium_like                    | Delta           |                   6 |                3 |               0.999442 |      0.000558444 | True                  |
| a7ffcore48se_0274 | diagnostic_clue      | basis_premium_like                    | Delta           |                   6 |                3 |               0.999513 |      0.00048732  | True                  |
| a7ffcore48se_1446 | diagnostic_clue      | funding_like|positioning_like         | Identity        |                   4 |                2 |               0.964986 |      0.0350139   | True                  |
| a7ffcore48se_1540 | diagnostic_clue      | positioning_like|state_or_taxonomy    | Identity        |                   4 |                2 |               1.01603  |     -0.0160331   | True                  |
| a7ffcore48se_1456 | diagnostic_clue      | funding_like|price_like               | WinsorZ         |                   4 |                2 |               2.94719  |     -1.94719     | True                  |
| a7ffcore48se_1566 | diagnostic_clue      | price_like|state_or_taxonomy          | SpreadShortLong |                   2 |                1 |               1        |     -7.05125e-08 | True                  |
| a7ffcore48se_0010 | diagnostic_clue      | basis_premium_like|basis_premium_like | Identity        |                   2 |                1 |               1.00032  |     -0.000319931 | True                  |
| a7ffcore48se_0013 | diagnostic_clue      | basis_premium_like|basis_premium_like | WinsorZ         |                   2 |                1 |               1.00341  |     -0.00341265  | True                  |
| a7ffcore48se_0001 | diagnostic_clue      | basis_premium_like                    | CSRank          |                   2 |                1 |               1.00415  |     -0.00415434  | True                  |
| a7ffcore48se_1355 | diagnostic_clue      | basis_premium_like                    | Identity        |                   2 |                1 |               1.00415  |     -0.00415434  | True                  |
| a7ffcore48se_1557 | diagnostic_clue      | price_like|price_like                 | Identity        |                   2 |                1 |               1.01117  |     -0.0111659   | True                  |
| a7ffcore48se_1509 | diagnostic_clue      | liquidity_like|state_or_taxonomy      | SpreadShortLong |                   2 |                1 |               1.01228  |     -0.0122844   | True                  |
| a7ffcore48se_0090 | diagnostic_clue      | funding_like|liquidity_like           | WinsorZ         |                   2 |                1 |               1.01298  |     -0.012981    | True                  |
| a7ffcore48se_1188 | diagnostic_clue      | funding_like|state_or_taxonomy        | AbsDelta        |                   2 |                1 |               1.03271  |     -0.0327098   | True                  |
| a7ffcore48se_0147 | diagnostic_clue      | liquidity_like|positioning_like       | CSRank          |                   2 |                1 |               1.05273  |     -0.052728    | True                  |
| a7ffcore48se_0740 | diagnostic_clue      | positioning_like|state_or_taxonomy    | Identity        |                   2 |                1 |               1.05459  |     -0.0545851   | True                  |
| a7ffcore48se_0029 | diagnostic_clue      | basis_premium_like|liquidity_like     | CSRank          |                   2 |                1 |               1.13293  |     -0.132933    | True                  |
| a7ffcore48se_1704 | diagnostic_clue      | funding_like|positioning_like         | WinsorZ         |                   2 |                1 |               1.18111  |     -0.181107    | True                  |
| a7ffcore48se_0671 | diagnostic_clue      | generic_numeric|price_like            | Identity        |                   2 |                1 |               1.31692  |     -0.316924    | True                  |
| a7ffcore48se_0775 | diagnostic_clue      | price_like|volatility_like            | Identity        |                   2 |                1 |               1.33002  |     -0.330022    | True                  |
| a7ffcore48se_1195 | diagnostic_clue      | funding_like|volatility_like          | AbsDelta        |                   2 |                1 |               1.62696  |     -0.626965    | True                  |
| a7ffcore48se_1249 | diagnostic_clue      | liquidity_like|state_or_taxonomy      | WinsorZ         |                   2 |                1 |               1.88148  |     -0.881482    | True                  |
| a7ffcore48se_0176 | diagnostic_clue      | positioning_like                      | Delta           |                   2 |                1 |               2.19935  |     -1.19935     | True                  |
| a7ffcore48se_0682 | diagnostic_clue      | generic_numeric|volatility_like       | AbsDelta        |                   2 |                1 |               3.14704  |     -2.14704     | True                  |
| a7ffcore48se_1393 | diagnostic_clue      | basis_premium_like|positioning_like   | WinsorZ         |                   2 |                1 |               3.50444  |     -2.50444     | True                  |
| a7ffcore48se_0681 | diagnostic_clue      | generic_numeric|state_or_taxonomy     | WinsorZ         |                   2 |                1 |               4.07641  |     -3.07641     | True                  |
| a7ffcore48se_0785 | diagnostic_clue      | state_or_taxonomy                     | WinsorZ         |                   2 |                1 |               4.07641  |     -3.07641     | True                  |
| a7ffcore48se_0381 | diagnostic_clue      | funding_like|state_or_taxonomy        | SignedRankDelta |                   2 |                1 |               4.28157  |     -3.28157     | True                  |
| a7ffcore48se_1466 | diagnostic_clue      | funding_like|volatility_like          | Delta           |                   2 |                1 |               5.73168  |     -4.73168     | True                  |
| a7ffcore48se_0182 | diagnostic_clue      | positioning_like|positioning_like     | CSRank          |                   2 |                1 |              16.2623   |    -15.2623      | True                  |

## Family Forensic

| semantic_pair                         | operator        |   clue_count |   strict_count |   thin_control_margin_count |   median_control_margin |   median_clean_horizons |   max_original_spread |   max_original_tstat |
|:--------------------------------------|:----------------|-------------:|---------------:|----------------------------:|------------------------:|------------------------:|----------------------:|---------------------:|
| state_or_taxonomy|state_or_taxonomy   | SignedRankDelta |            1 |              1 |                           0 |             0.117016    |                     3   |           0.000337505 |             3.11815  |
| basis_premium_like|basis_premium_like | Identity        |            2 |              0 |                           2 |             0.000582638 |                     2   |           0.000371488 |            10.6182   |
| basis_premium_like                    | Delta           |            2 |              0 |                           2 |             0.000522882 |                     3   |           0.000757053 |            23.4406   |
| price_like|price_like                 | Identity        |            2 |              0 |                           2 |            -0.00337624  |                     2.5 |           0.000273973 |             2.32394  |
| positioning_like|state_or_taxonomy    | Identity        |            2 |              0 |                           2 |            -0.0353091   |                     1.5 |           0.00128928  |             8.36816  |
| funding_like|positioning_like         | Identity        |            1 |              0 |                           1 |             0.0350139   |                     2   |           0.00136525  |             3.47264  |
| funding_like|funding_like             | WinsorZ         |            1 |              0 |                           1 |             0.0315983   |                     3   |           0.0018563   |             3.59327  |
| basis_premium_like|price_like         | Identity        |            1 |              0 |                           1 |             0.00343021  |                     4   |           0.000274678 |             2.30602  |
| price_like|state_or_taxonomy          | SpreadShortLong |            1 |              0 |                           1 |            -7.05125e-08 |                     1   |           0.000432629 |             2.67504  |
| basis_premium_like|basis_premium_like | WinsorZ         |            1 |              0 |                           1 |            -0.00341265  |                     1   |           0.000605271 |             5.11022  |
| basis_premium_like                    | CSRank          |            1 |              0 |                           1 |            -0.00415434  |                     1   |           0.000887805 |            29.4943   |
| basis_premium_like                    | Identity        |            1 |              0 |                           1 |            -0.00415434  |                     1   |           0.000887805 |            29.4943   |
| liquidity_like|state_or_taxonomy      | SpreadShortLong |            1 |              0 |                           1 |            -0.0122844   |                     1   |           0.000430644 |             1.9717   |
| funding_like|liquidity_like           | WinsorZ         |            1 |              0 |                           1 |            -0.012981    |                     1   |           0.00153237  |             2.61347  |
| funding_like|state_or_taxonomy        | AbsDelta        |            1 |              0 |                           1 |            -0.0327098   |                     1   |           0.00101503  |             2.17237  |
| liquidity_like|positioning_like       | CSRank          |            1 |              0 |                           1 |            -0.052728    |                     1   |           0.000116716 |             1.2571   |
| basis_premium_like|liquidity_like     | CSRank          |            1 |              0 |                           1 |            -0.132933    |                     1   |           0.000210253 |             1.76354  |
| funding_like|positioning_like         | WinsorZ         |            1 |              0 |                           1 |            -0.181107    |                     1   |           0.00108751  |             1.72286  |
| generic_numeric|price_like            | Identity        |            1 |              0 |                           1 |            -0.316924    |                     1   |           0.000207717 |             1.43364  |
| price_like|volatility_like            | Identity        |            1 |              0 |                           1 |            -0.330022    |                     1   |           0.000370956 |             2.57253  |
| funding_like|volatility_like          | AbsDelta        |            1 |              0 |                           1 |            -0.626965    |                     1   |           0.000453388 |             1.49229  |
| liquidity_like|state_or_taxonomy      | WinsorZ         |            1 |              0 |                           1 |            -0.881482    |                     1   |           8.13583e-05 |             1.16947  |
| positioning_like                      | Delta           |            1 |              0 |                           1 |            -1.19935     |                     1   |           9.86036e-05 |             1.2068   |
| funding_like|price_like               | WinsorZ         |            1 |              0 |                           1 |            -1.94719     |                     2   |           0.000257703 |             1.24363  |
| generic_numeric|volatility_like       | AbsDelta        |            1 |              0 |                           1 |            -2.14704     |                     1   |           9.30069e-06 |             0.141479 |
| basis_premium_like|positioning_like   | WinsorZ         |            1 |              0 |                           1 |            -2.50444     |                     1   |           0.000135809 |             1.13607  |
| generic_numeric|state_or_taxonomy     | WinsorZ         |            1 |              0 |                           1 |            -3.07641     |                     1   |           0.000471575 |             1.12557  |
| state_or_taxonomy                     | WinsorZ         |            1 |              0 |                           1 |            -3.07641     |                     1   |           0.000471575 |             1.12557  |
| funding_like|state_or_taxonomy        | SignedRankDelta |            1 |              0 |                           1 |            -3.28157     |                     1   |           0.00013508  |             0.470888 |
| funding_like|volatility_like          | Delta           |            1 |              0 |                           1 |            -4.73168     |                     1   |           0.000176387 |             1.39241  |
| positioning_like|positioning_like     | CSRank          |            1 |              0 |                           1 |           -15.2623      |                     1   |           7.35149e-05 |             2.31441  |

## Replay Target Repair Requirements

```json
{
  "required_repairs": [
    "do_not_count_L0_raw_and_L1_xs_as_independent_for_top_bottom_spread",
    "add_non_redundant_label_targets_before_next_replay_wave",
    "require_control_margin_not_just_control_ratio_below_one",
    "separate_diagnostic_clues_from_strict_replay_clues",
    "do_not_expand_formula_search_from_current_35_diagnostic_clues"
  ],
  "suggested_label_targets": [
    "BTC_ETH_beta_residual_return",
    "liquidity_tier_relative_return",
    "latent_state_relative_return",
    "vol_adjusted_return",
    "ranked_future_return_diagnostic_only",
    "portfolio_top_bottom_net_spread_proxy"
  ]
}
```

## Authorization

```json
{
  "authorized": {
    "A7FF-CORE53 replay target repair contract": true
  },
  "not_authorized": {
    "alpha_proof": true,
    "deep_audit": true,
    "formula_search": true,
    "large_search": true,
    "promotion": true,
    "shadow_paper_live": true
  }
}
```
