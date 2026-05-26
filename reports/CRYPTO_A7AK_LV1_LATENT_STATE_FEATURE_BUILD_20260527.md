# CRYPTO A7AK-LV1 Latent State Feature Build

Generated: 2026-05-26T16:33:10Z

## Decision

```text
PASS_A7AK_LV1_LATENT_STATE_FEATURES_READY
```

This stage builds observable listing-age latent-state features and train-only initial raw states. It does not compute response-based merges, run replay, or run search.

## Summary

```json
{
  "age_lt30_fixed_quota_minimum": 0.1,
  "age_lt30_rows": 358955,
  "age_lt30_symbols": 498,
  "authorizes_alpha_proof": false,
  "authorizes_lv2_response_merge_audit": true,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "columns": 48,
  "decision": "PASS_A7AK_LV1_LATENT_STATE_FEATURES_READY",
  "executes_replay": false,
  "executes_search": false,
  "executes_state_construction": true,
  "generated_at": "2026-05-26T16:33:10Z",
  "input_panel_root": "G:\\AlphaFactory_CryptoData\\gold\\features\\binance_universe498_replay_1h_v1_20260525",
  "input_symbol_classification": "G:\\AlphaFactory_CryptoData\\gold\\metadata\\binance_universe498_replay_1h_v1_symbol_classification_20260526.csv",
  "output_panel": "G:\\AlphaFactory_CryptoData\\gold\\features\\binance_universe498_latent_state_features_v1_20260527.parquet",
  "raw_latent_states": 825,
  "rows": 6650298,
  "symbols": 498,
  "train_seen_states": 653,
  "unseen_state_row_share": 0.18593482577773207,
  "unseen_state_rows": 1236522,
  "warnings": [
    "LV1 uses interpretable train-only bucketized raw states, not response-merged states",
    "Short-history symbols can contribute to lifecycle state research but not primary proof",
    "May 2026 rows are unavailable in the input panel",
    "Raw latent states unseen in train are flagged and require LV2/LV3 handling before use"
  ]
}
```

## Split Summary

| split                 |    rows |   symbols |   raw_states |   rows_state_seen_in_train |   state_seen_in_train_rate | may_allowed_for_ranking   |
|:----------------------|--------:|----------:|-------------:|---------------------------:|---------------------------:|:--------------------------|
| train_2024            | 1880549 |       276 |          653 |                    1880549 |                   1        | True                      |
| validation_2025H1     | 1410769 |       374 |          441 |                    1178585 |                   0.83542  | True                      |
| recent_2025H2_2026Apr | 3358980 |       498 |          464 |                    2354642 |                   0.700999 | True                      |
| may_2026_unavailable  |       0 |         0 |            0 |                          0 |                 nan        | False                     |

## Train-Only Thresholds

| field_name            |   quantile |    threshold | fit_split   |   fit_rows |
|:----------------------|-----------:|-------------:|:------------|-----------:|
| log_quote_volume_168h |       0.33 | 13.1358      | train_2024  |    1874201 |
| log_quote_volume_168h |       0.66 | 14.5103      | train_2024  |    1874201 |
| realized_vol_168h     |       0.33 |  0.0090373   | train_2024  |    1867312 |
| realized_vol_168h     |       0.66 |  0.0131015   | train_2024  |    1867312 |
| funding_rate_abs_168h |       0.5  |  6.29029e-05 | train_2024  |     655080 |
| funding_rate_abs_168h |       0.8  |  0.000157767 | train_2024  |     655080 |
| basis_abs_168h        |       0.5  |  6.03377     | train_2024  |    1871779 |
| basis_abs_168h        |       0.8  |  8.61419     | train_2024  |    1871779 |
| rolling_coverage_168h |       0.9  |  1           | train_2024  |    1874201 |
| rolling_coverage_168h |       0.99 |  1           | train_2024  |    1874201 |

## Largest Raw States

| raw_latent_state_id   | raw_latent_state_label                                                                |   rows |   symbols | state_seen_in_train   |   rows_train_2024 |   symbols_train_2024 |   rows_validation_2025H1 |   symbols_validation_2025H1 |   rows_recent_2025H2_2026Apr |   symbols_recent_2025H2_2026Apr |   rows_may_2026_unavailable |   symbols_may_2026_unavailable |
|:----------------------|:--------------------------------------------------------------------------------------|-------:|----------:|:----------------------|------------------:|---------------------:|-------------------------:|----------------------------:|-----------------------------:|--------------------------------:|----------------------------:|-------------------------------:|
| lv_4ec6957e53         | age_180_365d|liq_low|vol_low|funding_abs_state_missing|basis_mid|cov_high|nonmajor    |  75261 |        90 | True                  |             75248 |                   89 |                        0 |                           0 |                           13 |                               1 |                           0 |                              0 |
| lv_8326775b3e         | age_180_365d|liq_low|vol_low|funding_abs_state_missing|basis_low|cov_high|nonmajor    |  50183 |        86 | True                  |             50183 |                   86 |                        0 |                           0 |                            0 |                               0 |                           0 |                              0 |
| lv_ff73f4b914         | age_180_365d|liq_low|vol_mid|funding_abs_state_missing|basis_mid|cov_high|nonmajor    |  39244 |        83 | True                  |             39244 |                   83 |                        0 |                           0 |                            0 |                               0 |                           0 |                              0 |
| lv_7553b9a623         | age_180_365d|liq_high|vol_mid|funding_abs_state_missing|basis_low|cov_high|nonmajor   |  38696 |        59 | True                  |             38696 |                   59 |                        0 |                           0 |                            0 |                               0 |                           0 |                              0 |
| lv_9f1ab41e4d         | age_180_365d|liq_high|vol_high|funding_abs_state_missing|basis_low|cov_high|nonmajor  |  36698 |        75 | True                  |             36698 |                   75 |                        0 |                           0 |                            0 |                               0 |                           0 |                              0 |
| lv_2fdbf42dff         | age_180_365d|liq_high|vol_low|funding_abs_state_missing|basis_low|cov_high|nonmajor   |  34617 |        38 | True                  |             34617 |                   38 |                        0 |                           0 |                            0 |                               0 |                           0 |                              0 |
| lv_0bb87ba9f4         | age_180_365d|liq_mid|vol_low|funding_abs_state_missing|basis_low|cov_high|nonmajor    |  34468 |        62 | True                  |             34468 |                   62 |                        0 |                           0 |                            0 |                               0 |                           0 |                              0 |
| lv_cde4f27dfc         | age_90_180d|liq_low|vol_low|funding_abs_state_missing|basis_low|cov_high|nonmajor     |  32527 |        77 | True                  |             32527 |                   77 |                        0 |                           0 |                            0 |                               0 |                           0 |                              0 |
| lv_36cbe89323         | age_30_90d|liq_high|vol_high|funding_abs_state_missing|basis_high|cov_high|nonmajor   |  29828 |        90 | True                  |             29828 |                   90 |                        0 |                           0 |                            0 |                               0 |                           0 |                              0 |
| lv_1083ea2d53         | age_180_365d|liq_mid|vol_mid|funding_abs_state_missing|basis_low|cov_high|nonmajor    |  29541 |        86 | True                  |             29541 |                   86 |                        0 |                           0 |                            0 |                               0 |                           0 |                              0 |
| lv_fd823dbade         | age_180_365d|liq_low|vol_low|funding_abs_state_missing|basis_high|cov_high|nonmajor   |  29606 |        65 | True                  |             27678 |                   64 |                        0 |                           0 |                         1928 |                               1 |                           0 |                              0 |
| lv_0f94c8a4e6         | age_30_90d|liq_mid|vol_high|funding_abs_state_missing|basis_high|cov_high|nonmajor    |  26143 |        82 | True                  |             26036 |                   80 |                       18 |                           1 |                           89 |                               1 |                           0 |                              0 |
| lv_9c7069e440         | age_180_365d|liq_high|vol_high|funding_abs_state_missing|basis_mid|cov_high|nonmajor  |  25490 |        74 | True                  |             25490 |                   74 |                        0 |                           0 |                            0 |                               0 |                           0 |                              0 |
| lv_4b159564c7         | age_180_365d|liq_low|vol_mid|funding_abs_state_missing|basis_low|cov_high|nonmajor    |  25124 |        80 | True                  |             25124 |                   80 |                        0 |                           0 |                            0 |                               0 |                           0 |                              0 |
| lv_519b0cb5df         | age_90_180d|liq_mid|vol_low|funding_abs_state_missing|basis_low|cov_high|nonmajor     |  24730 |        70 | True                  |             24730 |                   70 |                        0 |                           0 |                            0 |                               0 |                           0 |                              0 |
| lv_f947a5a9b1         | age_90_180d|liq_mid|vol_mid|fund_low|basis_low|cov_high|nonmajor                      |  35021 |       110 | True                  |             24394 |                   60 |                     6329 |                          39 |                         4298 |                              26 |                           0 |                              0 |
| lv_f8ce3748ed         | age_180_365d|liq_mid|vol_high|funding_abs_state_missing|basis_high|cov_high|nonmajor  |  23916 |        83 | True                  |             23916 |                   83 |                        0 |                           0 |                            0 |                               0 |                           0 |                              0 |
| lv_6c581ab375         | age_90_180d|liq_low|vol_low|funding_abs_state_missing|basis_mid|cov_high|nonmajor     |  23777 |        75 | True                  |             23615 |                   74 |                        0 |                           0 |                          162 |                               1 |                           0 |                              0 |
| lv_eb465cc404         | age_180_365d|liq_mid|vol_mid|fund_low|basis_low|cov_high|nonmajor                     |  45297 |       108 | True                  |             20088 |                   53 |                    11549 |                          35 |                        13660 |                              49 |                           0 |                              0 |
| lv_b925379230         | age_180_365d|liq_mid|vol_high|funding_abs_state_missing|basis_mid|cov_high|nonmajor   |  19417 |        96 | True                  |             19417 |                   96 |                        0 |                           0 |                            0 |                               0 |                           0 |                              0 |
| lv_9cc294e930         | age_30_90d|liq_low|vol_low|funding_abs_state_missing|basis_low|cov_high|nonmajor      |  18799 |        65 | True                  |             18799 |                   65 |                        0 |                           0 |                            0 |                               0 |                           0 |                              0 |
| lv_0ede6e85cf         | age_90_180d|liq_mid|vol_mid|funding_abs_state_missing|basis_low|cov_high|nonmajor     |  18438 |        85 | True                  |             18438 |                   85 |                        0 |                           0 |                            0 |                               0 |                           0 |                              0 |
| lv_5cff5dfa54         | age_90_180d|liq_high|vol_low|funding_abs_state_missing|basis_low|cov_high|nonmajor    |  18340 |        37 | True                  |             18340 |                   37 |                        0 |                           0 |                            0 |                               0 |                           0 |                              0 |
| lv_9b315c2b7c         | age_180_365d|liq_mid|vol_high|funding_abs_state_missing|basis_low|cov_high|nonmajor   |  18198 |        87 | True                  |             18198 |                   87 |                        0 |                           0 |                            0 |                               0 |                           0 |                              0 |
| lv_4b3f9f9ec5         | age_90_180d|liq_high|vol_mid|funding_abs_state_missing|basis_low|cov_high|nonmajor    |  18066 |        54 | True                  |             18066 |                   54 |                        0 |                           0 |                            0 |                               0 |                           0 |                              0 |
| lv_465a3e381d         | age_90_180d|liq_high|vol_high|funding_abs_state_missing|basis_low|cov_high|nonmajor   |  17895 |        63 | True                  |             17895 |                   63 |                        0 |                           0 |                            0 |                               0 |                           0 |                              0 |
| lv_3d8dcec701         | age_180_365d|liq_low|vol_mid|funding_abs_state_missing|basis_high|cov_high|nonmajor   |  17759 |        72 | True                  |             17598 |                   71 |                        0 |                           0 |                          161 |                               1 |                           0 |                              0 |
| lv_2240e20986         | age_180_365d|liq_high|vol_low|funding_abs_state_missing|basis_low|cov_high|major      |  16720 |         5 | True                  |             16720 |                    5 |                        0 |                           0 |                            0 |                               0 |                           0 |                              0 |
| lv_937ea0833b         | age_180_365d|liq_low|vol_low|fund_low|basis_low|cov_high|nonmajor                     |  60524 |       127 | True                  |             16518 |                   37 |                     4926 |                          30 |                        39080 |                              81 |                           0 |                              0 |
| lv_e31e381c83         | age_180_365d|liq_low|vol_mid|fund_low|basis_low|cov_high|nonmajor                     |  62124 |       147 | True                  |             16283 |                   45 |                    11008 |                          47 |                        34833 |                              95 |                           0 |                              0 |
| lv_ff96829b05         | age_90_180d|liq_low|vol_mid|funding_abs_state_missing|basis_low|cov_high|nonmajor     |  16124 |        63 | True                  |             16124 |                   63 |                        0 |                           0 |                            0 |                               0 |                           0 |                              0 |
| lv_0a84bf23ad         | age_180_365d|liq_mid|vol_mid|funding_abs_state_missing|basis_mid|cov_high|nonmajor    |  16052 |        84 | True                  |             16052 |                   84 |                        0 |                           0 |                            0 |                               0 |                           0 |                              0 |
| lv_8a37a4f4e5         | age_180_365d|liq_mid|vol_high|fund_mid|basis_mid|cov_high|nonmajor                    |  23516 |       106 | True                  |             15481 |                   46 |                     3453 |                          27 |                         4582 |                              45 |                           0 |                              0 |
| lv_259a761921         | age_30_90d|liq_mid|vol_mid|funding_abs_state_missing|basis_high|cov_high|nonmajor     |  14612 |        84 | True                  |             14612 |                   84 |                        0 |                           0 |                            0 |                               0 |                           0 |                              0 |
| lv_06e9ff0a93         | age_180_365d|liq_high|vol_high|fund_low|basis_low|cov_high|nonmajor                   |  31209 |        65 | True                  |             14309 |                   36 |                     9896 |                          26 |                         7004 |                              23 |                           0 |                              0 |
| lv_4e98d13d2f         | age_90_180d|liq_high|vol_high|fund_low|basis_low|cov_high|nonmajor                    |  25356 |        74 | True                  |             14297 |                   37 |                     7745 |                          28 |                         3314 |                              15 |                           0 |                              0 |
| lv_51666577b4         | age_90_180d|liq_low|vol_mid|funding_abs_state_missing|basis_mid|cov_high|nonmajor     |  14248 |        65 | True                  |             14169 |                   64 |                        0 |                           0 |                           79 |                               1 |                           0 |                              0 |
| lv_c36eedbeb8         | age_180_365d|liq_high|vol_high|funding_abs_state_missing|basis_high|cov_high|nonmajor |  13892 |        81 | True                  |             13892 |                   81 |                        0 |                           0 |                            0 |                               0 |                           0 |                              0 |
| lv_dbcfc4ac24         | age_180_365d|liq_low|vol_low|fund_low|basis_mid|cov_high|nonmajor                     |  48535 |       150 | True                  |             13613 |                   34 |                     6741 |                          37 |                        28181 |                             110 |                           0 |                              0 |
| lv_1746c0d893         | age_180_365d|liq_mid|vol_high|fund_low|basis_low|cov_high|nonmajor                    |  36755 |       122 | True                  |             13460 |                   51 |                    12659 |                          40 |                        10636 |                              61 |                           0 |                              0 |

## Age Quota Audit

| split                 | age_bucket   |    rows |   symbols |   row_share | may_allowed_for_ranking   |   fixed_quota_minimum | quota_available   |
|:----------------------|:-------------|--------:|----------:|------------:|:--------------------------|----------------------:|:------------------|
| train_2024            | age_lt30d    |  191459 |       276 |  0.10181    | True                      |                   0.1 | True              |
| train_2024            | age_30_90d   |  344876 |       252 |  0.183391   | True                      |                 nan   | True              |
| train_2024            | age_90_180d  |  470250 |       232 |  0.25006    | True                      |                 nan   | True              |
| train_2024            | age_180_365d |  869916 |       211 |  0.462586   | True                      |                 nan   | True              |
| train_2024            | age_ge365d   |    4048 |       176 |  0.00215256 | True                      |                 nan   | True              |
| validation_2025H1     | age_lt30d    |   73793 |       122 |  0.0523069  | True                      |                   0.1 | True              |
| validation_2025H1     | age_30_90d   |  147475 |       129 |  0.104535   | True                      |                 nan   | True              |
| validation_2025H1     | age_90_180d  |  176568 |       114 |  0.125157   | True                      |                 nan   | True              |
| validation_2025H1     | age_180_365d |  163273 |       100 |  0.115733   | True                      |                 nan   | True              |
| validation_2025H1     | age_ge365d   |  849660 |       211 |  0.602267   | True                      |                 nan   | True              |
| recent_2025H2_2026Apr | age_lt30d    |   93703 |       137 |  0.0278963  | True                      |                   0.1 | True              |
| recent_2025H2_2026Apr | age_30_90d   |  224769 |       173 |  0.0669158  | True                      |                 nan   | True              |
| recent_2025H2_2026Apr | age_90_180d  |  397115 |       222 |  0.118225   | True                      |                 nan   | True              |
| recent_2025H2_2026Apr | age_180_365d |  732574 |       254 |  0.218094   | True                      |                 nan   | True              |
| recent_2025H2_2026Apr | age_ge365d   | 1910819 |       340 |  0.568869   | True                      |                 nan   | True              |
| may_2026_unavailable  | age_lt30d    |       0 |         0 |  0          | False                     |                   0.1 | False             |
| may_2026_unavailable  | age_30_90d   |       0 |         0 |  0          | False                     |                 nan   | True              |
| may_2026_unavailable  | age_90_180d  |       0 |         0 |  0          | False                     |                 nan   | True              |
| may_2026_unavailable  | age_180_365d |       0 |         0 |  0          | False                     |                 nan   | True              |
| may_2026_unavailable  | age_ge365d   |       0 |         0 |  0          | False                     |                 nan   | True              |

## Feature Quality Worst Missing

| field_name                     |   non_null_rate |   nan_count |   inf_count |          min |              max |
|:-------------------------------|----------------:|------------:|------------:|-------------:|-----------------:|
| funding_rate_mean_168h         |        0.582854 |     2774147 |           0 | -0.0130921   |      0.00225977  |
| funding_rate_abs_168h          |        0.582854 |     2774147 |           0 |  1.23801e-05 |      0.0130986   |
| age_x_funding_abs              |        0.582854 |     2774147 |           0 |  3.61204e-05 |      0.0494056   |
| volume_volatility_ratio_168h   |        0.995828 |       27744 |           0 |  0           | 932530           |
| open_interest_change_24h       |        0.996353 |       24252 |           0 | -1.34888     |      3.56595     |
| oi_x_price_move_24h            |        0.996353 |       24252 |           0 | -7.743       |      2.50439     |
| age_x_volatility               |        0.996406 |       23904 |           0 |  0           |      1.40244     |
| realized_vol_168h              |        0.996406 |       23904 |           0 |  0           |      0.409696    |
| basis_abs_168h                 |        0.996559 |       22885 |           0 |  0.188348    |    597.122       |
| premium_abs_168h               |        0.99766  |       15562 |           0 |  0           |    601.151       |
| realized_vol_72h               |        0.998203 |       11952 |           0 |  0           |      0.622392    |
| trade_return_24h               |        0.998203 |       11952 |           0 | -3.34922     |      2.03482     |
| rolling_coverage_168h          |        0.998278 |       11454 |           0 |  0           |      1           |
| log_quote_volume_168h          |        0.998278 |       11454 |           0 |  0           |     20.9133      |
| gap_hours_recent_168h          |        0.998278 |       11454 |           0 |  0           |     17           |
| median_quote_volume_168h       |        0.998278 |       11454 |           0 |  0           |      1.20933e+09 |
| liquidity_rank_active_universe |        0.998278 |       11454 |           0 |  0.00200803  |      1           |
| trade_count_168h               |        0.998278 |       11454 |           0 |  0           |      2.26223e+06 |
| age_x_liquidity                |        0.998278 |       11454 |           0 |  0.00137162  |      6.74754     |
| realized_vol_24h               |        0.999101 |        5976 |           0 |  0           |      1.06319     |
| age_percentile_active_universe |        1        |           0 |           0 |  0.00200803  |      0.824297    |
| sqrt_listing_age_days          |        1        |           0 |           0 |  0           |     29.1712      |
| log1p_listing_age_days         |        1        |           0 |           0 |  0           |      6.74754     |
| listing_age_days               |        1        |           0 |           0 |  0           |    850.958       |

## Boundary

```text
AUTHORIZED NEXT:
  A7AK-LV2 train-only response vector and state merge audit

NOT AUTHORIZED:
  search
  replay promotion
  alpha proof
  shadow / paper / live

LEAKAGE RULE:
  thresholds/scalers are fit on train_2024 only
  May rows are unavailable in this panel
  validation/recent only receive frozen bucket mapping
```
