# CRYPTO A7FF-31 PORTFOLIO FORENSIC

Generated: 2026-05-30T10:30:27Z

## Decision

`HOLD_A7FF31_PORTFOLIO_FORENSIC_CONCENTRATED_CLUE_NO_SEARCH_AUTH`

A7FF-31 reviews the A7FF-30A ensemble clues as candidate factors. The result remains a concentrated research clue, not alpha proof.

## Experiment Record

```text
experiment_id: 20260530_a7ff31_portfolio_forensic
objective: determine whether A7FF-30A ensemble clues are diversified enough for expansion
inputs: A7FF-30A outputs, A7FF-30 frozen queue, strict_full_history universe
parameters: no generation, no search, candidate factor review, pairwise signal corr, symbol/month contribution
```

## Manifest

```json
{
  "authorizes_a7ff24r2_queue_repair": true,
  "authorizes_a7ff32_family_diversification_contract": true,
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "candidate_count": 6,
  "decision": "HOLD_A7FF31_PORTFOLIO_FORENSIC_CONCENTRATED_CLUE_NO_SEARCH_AUTH",
  "executes_generation": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T10:30:27Z",
  "max_pairwise_corr_abs": 0.9999999999999998,
  "mean_pairwise_corr_abs": 0.5111626544210106,
  "recent_month_positive_rate": 1.0,
  "selected_ensemble_clue_rows": 12,
  "stage": "A7FF-31",
  "top_symbol_contribution_share": 0.05521294374079854,
  "warnings": [
    "all_candidates_have_basis_premium_root",
    "safe_div_outlier_risk_present",
    "ensemble_is_basis_premium_root_concentrated",
    "candidate_pairwise_corr_gt_0_80",
    "basis_premium_root_concentration_requires_family_diversification_before_search"
  ]
}
```

## Candidate Factor Review

| factor_id                | name                                                | formula                                                               | provenance                                            | operator_path           | raw_fields                             | feature_family                        | nearest_known_family   | overlap_assessment   | family_diversity_impact                                        | cluster_coverage      | keep_list_decision   | required_next_action                                                    |
|:-------------------------|:----------------------------------------------------|:----------------------------------------------------------------------|:------------------------------------------------------|:------------------------|:---------------------------------------|:--------------------------------------|:-----------------------|:---------------------|:---------------------------------------------------------------|:----------------------|:---------------------|:------------------------------------------------------------------------|
| a7ff24r_858ff2210f276fcf | basis_premium_like::single                          | Delta(mark_index_basis_bps,12)                                        | generated_by_A7FF_24R_then_filtered_by_A7FF28A_A7FF29 | Delta                   | mark_index_basis_bps                   | basis_premium_like                    | basis_premium_root     | high_family_overlap  | reduces_breadth_because_all_candidates_keep_basis_premium_root | skel_1d39996e97d5ace0 | HOLD_RESEARCH        | portfolio_forensic_and_outlier_winsorized_replay_before_any_keep_review |
| a7ff24r_650915032f2a5979 | basis_premium_like|volatility_like::gated_sign      | Mul(Delta(mark_index_basis_bps,12),Sign(realized_vol_24h))            | generated_by_A7FF_24R_then_filtered_by_A7FF28A_A7FF29 | Mul|Delta|Sign          | mark_index_basis_bps|realized_vol_24h  | basis_premium_like|volatility_like    | basis_premium_root     | high_family_overlap  | reduces_breadth_because_all_candidates_keep_basis_premium_root | skel_136259b72205469f | HOLD_RESEARCH        | portfolio_forensic_and_outlier_winsorized_replay_before_any_keep_review |
| a7ff24r_bcc3435cf539d883 | basis_premium_like|basis_premium_like::sub          | Sub(mark_index_basis_bps,Mean(premium_close_bps,12))                  | generated_by_A7FF_24R_then_filtered_by_A7FF28A_A7FF29 | Sub|Mean                | mark_index_basis_bps|premium_close_bps | basis_premium_like|basis_premium_like | basis_premium_root     | high_family_overlap  | reduces_breadth_because_all_candidates_keep_basis_premium_root | skel_f8484b844efd270f | HOLD_RESEARCH        | portfolio_forensic_and_outlier_winsorized_replay_before_any_keep_review |
| a7ff24r_389e925b81a0c645 | basis_premium_like|volatility_like::smooth_mul      | Mean(Mul(Delta(mark_index_basis_bps,1),realized_vol_168h),4)          | generated_by_A7FF_24R_then_filtered_by_A7FF28A_A7FF29 | Mean|Mul|Delta          | mark_index_basis_bps|realized_vol_168h | basis_premium_like|volatility_like    | basis_premium_root     | high_family_overlap  | reduces_breadth_because_all_candidates_keep_basis_premium_root | skel_8184698cb7b24c02 | HOLD_RESEARCH        | portfolio_forensic_and_outlier_winsorized_replay_before_any_keep_review |
| a7ff24r_c223ee324263786f | basis_premium_like|volatility_like::safe_div_abs    | SafeDiv(premium_close_bps,Abs(realized_vol_168h))                     | generated_by_A7FF_24R_then_filtered_by_A7FF28A_A7FF29 | SafeDiv|Abs             | premium_close_bps|realized_vol_168h    | basis_premium_like|volatility_like    | basis_premium_root     | high_family_overlap  | reduces_breadth_because_all_candidates_keep_basis_premium_root | skel_d9d4f69744bac825 | HOLD_RESEARCH        | portfolio_forensic_and_outlier_winsorized_replay_before_any_keep_review |
| a7ff24r_145e2d58adad4f4a | basis_premium_like|basis_premium_like::safe_div_abs | SafeDiv(mark_index_basis_bps,Abs(ZScore(Mean(premium_close_bps,12)))) | generated_by_A7FF_24R_then_filtered_by_A7FF28A_A7FF29 | SafeDiv|Abs|ZScore|Mean | mark_index_basis_bps|premium_close_bps | basis_premium_like|basis_premium_like | basis_premium_root     | high_family_overlap  | reduces_breadth_because_all_candidates_keep_basis_premium_root | skel_c80f62c274b367a9 | HOLD_RESEARCH        | portfolio_forensic_and_outlier_winsorized_replay_before_any_keep_review |

## Signal Correlation

| left                     | right                    |   pairwise_corr |
|:-------------------------|:-------------------------|----------------:|
| a7ff24r_858ff2210f276fcf | a7ff24r_650915032f2a5979 |        1        |
| a7ff24r_bcc3435cf539d883 | a7ff24r_145e2d58adad4f4a |        0.618453 |
| a7ff24r_bcc3435cf539d883 | a7ff24r_389e925b81a0c645 |        0.597483 |
| a7ff24r_650915032f2a5979 | a7ff24r_bcc3435cf539d883 |        0.577199 |
| a7ff24r_858ff2210f276fcf | a7ff24r_bcc3435cf539d883 |        0.571482 |
| a7ff24r_c223ee324263786f | a7ff24r_145e2d58adad4f4a |        0.515939 |
| a7ff24r_bcc3435cf539d883 | a7ff24r_c223ee324263786f |        0.461251 |
| a7ff24r_650915032f2a5979 | a7ff24r_389e925b81a0c645 |        0.449969 |
| a7ff24r_858ff2210f276fcf | a7ff24r_389e925b81a0c645 |        0.449969 |
| a7ff24r_650915032f2a5979 | a7ff24r_c223ee324263786f |        0.424307 |
| a7ff24r_858ff2210f276fcf | a7ff24r_c223ee324263786f |        0.424307 |
| a7ff24r_650915032f2a5979 | a7ff24r_145e2d58adad4f4a |        0.399889 |
| a7ff24r_389e925b81a0c645 | a7ff24r_c223ee324263786f |        0.398956 |
| a7ff24r_858ff2210f276fcf | a7ff24r_145e2d58adad4f4a |        0.396815 |
| a7ff24r_389e925b81a0c645 | a7ff24r_145e2d58adad4f4a |        0.381423 |

## Recent Symbol Contribution

| symbol      | split                 |   top_count |   bottom_count |   top_label_sum |   bottom_label_sum |   net_label_sum |   abs_label_sum |   abs_contribution_share |
|:------------|:----------------------|------------:|---------------:|----------------:|-------------------:|----------------:|----------------:|-------------------------:|
| HIGHUSDT    | recent_oos_2026JanApr |         111 |            223 |        380.597  |          182.381   |        198.216  |        562.977  |               0.0552129  |
| JOEUSDT     | recent_oos_2026JanApr |         114 |            126 |        306.784  |          -25.0995  |        331.884  |        331.884  |               0.0325489  |
| ORDIUSDT    | recent_oos_2026JanApr |          48 |             29 |        236.812  |           -5.69651 |        242.508  |        242.508  |               0.0237835  |
| BLURUSDT    | recent_oos_2026JanApr |          85 |            109 |        205.995  |           -3.61832 |        209.614  |        209.614  |               0.0205575  |
| CTSIUSDT    | recent_oos_2026JanApr |          96 |            166 |        137.633  |           66.8099  |         70.8228 |        204.443  |               0.0200503  |
| RUNEUSDT    | recent_oos_2026JanApr |          97 |            108 |        113.059  |           89.0612  |         23.9976 |        202.12   |               0.0198225  |
| THETAUSDT   | recent_oos_2026JanApr |         153 |            184 |        140.61   |           46.6263  |         93.9837 |        187.236  |               0.0183628  |
| ETHWUSDT    | recent_oos_2026JanApr |          38 |            181 |        -25.8634 |          147.853   |       -173.716  |        173.716  |               0.0170369  |
| ENJUSDT     | recent_oos_2026JanApr |         109 |            100 |        154.216  |           12.6301  |        141.586  |        166.847  |               0.0163632  |
| EDUUSDT     | recent_oos_2026JanApr |         108 |            126 |        108.267  |          -56.0813  |        164.348  |        164.348  |               0.0161181  |
| AXSUSDT     | recent_oos_2026JanApr |          81 |             29 |        132.282  |          -31.7303  |        164.012  |        164.012  |               0.0160852  |
| CHRUSDT     | recent_oos_2026JanApr |         100 |            142 |         73.9173 |           90.0122  |        -16.0949 |        163.93   |               0.0160771  |
| XVGUSDT     | recent_oos_2026JanApr |          50 |            130 |         10.7702 |         -148.105   |        158.875  |        158.875  |               0.0155814  |
| ALICEUSDT   | recent_oos_2026JanApr |          87 |            137 |        130.437  |          -27.2608  |        157.697  |        157.697  |               0.0154659  |
| XVSUSDT     | recent_oos_2026JanApr |         110 |            175 |         55.3361 |          -78.8194  |        134.155  |        134.155  |               0.0131571  |
| GTCUSDT     | recent_oos_2026JanApr |         156 |            237 |         80.4587 |           52.0541  |         28.4046 |        132.513  |               0.0129959  |
| SUPERUSDT   | recent_oos_2026JanApr |         133 |             65 |        121.514  |            7.64996 |        113.864  |        129.164  |               0.0126675  |
| SFPUSDT     | recent_oos_2026JanApr |         111 |             77 |        106.057  |          -15.0936  |        121.151  |        121.151  |               0.0118817  |
| RIFUSDT     | recent_oos_2026JanApr |          26 |            153 |         40.234  |           75.0133  |        -34.7793 |        115.247  |               0.0113027  |
| CRVUSDT     | recent_oos_2026JanApr |         110 |            148 |         80.2263 |          -34.8283  |        115.055  |        115.055  |               0.0112838  |
| SSVUSDT     | recent_oos_2026JanApr |          93 |             41 |        101.468  |          -10.7167  |        112.185  |        112.185  |               0.0110023  |
| WIFUSDT     | recent_oos_2026JanApr |         139 |            202 |         35.8201 |           75.4855  |        -39.6654 |        111.306  |               0.0109161  |
| 1000XECUSDT | recent_oos_2026JanApr |         105 |             91 |         72.3032 |          -30.5757  |        102.879  |        102.879  |               0.0100897  |
| AUCTIONUSDT | recent_oos_2026JanApr |          82 |             55 |         66.4537 |           35.6863  |         30.7675 |        102.14   |               0.0100172  |
| MASKUSDT    | recent_oos_2026JanApr |         105 |             68 |         82.3006 |           19.4058  |         62.8948 |        101.706  |               0.00997467 |
| BANDUSDT    | recent_oos_2026JanApr |         120 |            156 |        -27.4172 |           72.7324  |       -100.15   |        100.15   |               0.00982198 |
| MOVRUSDT    | recent_oos_2026JanApr |          87 |            108 |         87.0686 |          -12.7187  |         99.7873 |         99.7873 |               0.00978646 |
| SNXUSDT     | recent_oos_2026JanApr |         149 |            128 |         61.9472 |          -37.3435  |         99.2907 |         99.2907 |               0.00973775 |
| API3USDT    | recent_oos_2026JanApr |          88 |             62 |         68.0123 |           30.0556  |         37.9566 |         98.0679 |               0.00961783 |
| HFTUSDT     | recent_oos_2026JanApr |         140 |            194 |         38.8624 |          -57.6332  |         96.4956 |         96.4956 |               0.00946362 |

## Recent Month Contribution

| month   | split                 |   hour_count |   mean_spread |   tstat |   positive_rate |
|:--------|:----------------------|-------------:|--------------:|--------:|----------------:|
| 2026-04 | recent_oos_2026JanApr |          712 |       0.31714 | 7.56481 |        0.610955 |

## Leave-One-Out Focus

| portfolio_name                                 | label_family           |   label_horizon_h |   orientation_from_train |   premay_positive_split_count | premay_all_positive   |   avg_active_symbols_recent |   cost2_recent_oriented |   cost5_recent_oriented |   cost10_recent_oriented |   train_2024_n |   train_2024_mean_spread |   train_2024_tstat |   train_2024_nonoverlap_median_tstat |   train_2024_nonoverlap_min_tstat |   train_2024_positive_rate |   validation_2025H1_n |   validation_2025H1_mean_spread |   validation_2025H1_tstat |   validation_2025H1_nonoverlap_median_tstat |   validation_2025H1_nonoverlap_min_tstat |   validation_2025H1_positive_rate |   test_2025H2_n |   test_2025H2_mean_spread |   test_2025H2_tstat |   test_2025H2_nonoverlap_median_tstat |   test_2025H2_nonoverlap_min_tstat |   test_2025H2_positive_rate |   recent_oos_2026JanApr_n |   recent_oos_2026JanApr_mean_spread |   recent_oos_2026JanApr_tstat |   recent_oos_2026JanApr_nonoverlap_median_tstat |   recent_oos_2026JanApr_nonoverlap_min_tstat |   recent_oos_2026JanApr_positive_rate |   delta_recent_vs_ensemble |
|:-----------------------------------------------|:-----------------------|------------------:|-------------------------:|------------------------------:|:----------------------|----------------------------:|------------------------:|------------------------:|-------------------------:|---------------:|-------------------------:|-------------------:|-------------------------------------:|----------------------------------:|---------------------------:|----------------------:|--------------------------------:|--------------------------:|--------------------------------------------:|-----------------------------------------:|----------------------------------:|----------------:|--------------------------:|--------------------:|--------------------------------------:|-----------------------------------:|----------------------------:|--------------------------:|------------------------------------:|------------------------------:|------------------------------------------------:|---------------------------------------------:|--------------------------------------:|---------------------------:|
| leave_one_out_without_a7ff24r_858ff2210f276fcf | L5_vol_adjusted_return |                 8 |                        1 |                             3 | True                  |                     178.989 |                0.290077 |                0.289477 |                 0.288477 |            712 |                0.0189554 |           0.878007 |                            0.141935  |                         -1.21529  |                   0.536517 |                   712 |                       0.0580022 |                   2.55996 |                                    0.83744  |                                0.309445  |                          0.580056 |             712 |                  0.112233 |             3.81245 |                               1.08168 |                         -0.115782  |                    0.554775 |                       712 |                            0.290477 |                       7.23276 |                                         2.81136 |                                     0.947651 |                              0.610955 |                -0.0266626  |
| leave_one_out_without_a7ff24r_650915032f2a5979 | L5_vol_adjusted_return |                 8 |                        1 |                             3 | True                  |                     178.989 |                0.290077 |                0.289477 |                 0.288477 |            712 |                0.0189554 |           0.878007 |                            0.141935  |                         -1.21529  |                   0.536517 |                   712 |                       0.0580022 |                   2.55996 |                                    0.83744  |                                0.309445  |                          0.580056 |             712 |                  0.112233 |             3.81245 |                               1.08168 |                         -0.115782  |                    0.554775 |                       712 |                            0.290477 |                       7.23276 |                                         2.81136 |                                     0.947651 |                              0.610955 |                -0.0266626  |
| leave_one_out_without_a7ff24r_bcc3435cf539d883 | L5_vol_adjusted_return |                 8 |                        1 |                             3 | True                  |                     178.989 |                0.28719  |                0.28659  |                 0.28559  |            712 |                0.0270646 |           1.22196  |                            0.271435  |                         -1.54343  |                   0.549157 |                   712 |                       0.0472783 |                   2.22864 |                                    0.862141 |                               -0.329334  |                          0.557584 |             712 |                  0.109334 |             3.874   |                               1.3683  |                         -0.19736   |                    0.558989 |                       712 |                            0.28759  |                       6.65203 |                                         2.77011 |                                     1.06341  |                              0.606742 |                -0.0295501  |
| leave_one_out_without_a7ff24r_389e925b81a0c645 | L5_vol_adjusted_return |                 8 |                        1 |                             3 | True                  |                     178.989 |                0.299836 |                0.299236 |                 0.298236 |            712 |                0.0132036 |           0.579811 |                            0.2642    |                         -0.999823 |                   0.509831 |                   712 |                       0.045431  |                   2.02725 |                                    0.668307 |                               -0.0707753 |                          0.56882  |             712 |                  0.136965 |             4.60959 |                               1.59154 |                         -0.0594799 |                    0.570225 |                       712 |                            0.300236 |                       7.1357  |                                         2.91371 |                                     1.29159  |                              0.605337 |                -0.0169035  |
| leave_one_out_without_a7ff24r_c223ee324263786f | L5_vol_adjusted_return |                 8 |                        1 |                             3 | True                  |                     178.989 |                0.317924 |                0.317324 |                 0.316324 |            708 |                0.0125657 |           0.578001 |                           -0.0335378 |                         -0.639032 |                   0.519774 |                   712 |                       0.058446  |                   2.68056 |                                    0.812875 |                                0.40858   |                          0.567416 |             712 |                  0.121322 |             4.35611 |                               1.7369  |                         -0.155827  |                    0.570225 |                       712 |                            0.318324 |                       7.48874 |                                         3.41766 |                                     0.397655 |                              0.608146 |                 0.00118391 |
| leave_one_out_without_a7ff24r_145e2d58adad4f4a | L5_vol_adjusted_return |                 8 |                        1 |                             3 | True                  |                     178.989 |                0.306453 |                0.305853 |                 0.304853 |            712 |                0.014985  |           0.6685   |                            0.202077  |                         -1.00454  |                   0.518258 |                   712 |                       0.0613062 |                   2.82714 |                                    0.942729 |                                0.0157189 |                          0.55618  |             712 |                  0.119291 |             3.89913 |                               1.27579 |                          0.0386504 |                    0.55618  |                       712 |                            0.306853 |                       7.06325 |                                         2.64827 |                                     0.851124 |                              0.617978 |                -0.0102864  |

## Boundary

```text
A7FF-31 explicitly holds the current portfolio clue as concentrated.
It authorizes only queue repair/family diversification contracts, not formula search or promotion.
No alpha proof, shadow, paper, or live execution is authorized.
```
