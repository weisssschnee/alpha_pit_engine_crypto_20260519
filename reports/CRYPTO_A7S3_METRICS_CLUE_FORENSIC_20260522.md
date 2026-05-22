# Crypto A7S-3 Metrics Clue Forensic

- generated_at: `2026-05-22T09:08:05Z`
- decision: `PASS_A7S3_CROWDING_CLUE_FORENSIC_COMPLETE_HOLD_PROMOTION`
- executes_search: `False`
- executes_replay: `forensic_on_a7s2m_clues_only`
- alpha proof / expanded replay / full search / shadow / paper / live: `NOT_AUTHORIZED`

## Scope

A7S-3 audits the two A7S-2M clean clues. They share the same formula and differ only by horizon, so the first question is independence and concentration, not promotion.

May remains post-selection stress-only and is not used for ranking or threshold tuning.

## Split Metrics

| split                     | expression                                               |   horizon |   orientation |   base_train_ic |   active_hours |      net10 |      net20 |   lag1_net10 |   lag2_net10 |   lag3_net10 |   turnover_mean |   gross_exposure_mean |
|:--------------------------|:---------------------------------------------------------|----------:|--------------:|----------------:|---------------:|-----------:|-----------:|-------------:|-------------:|-------------:|----------------:|----------------------:|
| train_2024                | Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 |            -1 |     -0.00384522 |           8751 |  -7.93851  |  -9.03135  |    -7.22796  |    -6.70067  |    -6.29145  |       0.124554  |              0.997379 |
| validation_2025H1         | Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 |            -1 |     -0.00384522 |           4344 |   0.503662 |  -0.152838 |     0.669108 |     0.695569 |     0.762743 |       0.151128  |              1        |
| recent_oos_2025H2_2026Apr | Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 |            -1 |     -0.00384522 |           7294 |   0.948899 |   0.122899 |     1.056    |     1.12174  |     1.23089  |       0.113213  |              0.999726 |
| fresh_may_2026            | Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 |            -1 |     -0.00384522 |            480 |   0.588787 |   0.550454 |     0.615107 |     0.649916 |     0.658911 |       0.0759076 |              0.950495 |
| train_2024                | Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 |            -1 |     -0.00051143 |           8751 | -11.386    | -12.4788   |   -11.046    |   -10.6065   |   -10.2152   |       0.124554  |              0.997379 |
| validation_2025H1         | Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 |            -1 |     -0.00051143 |           4344 |   1.11734  |   0.460841 |     1.20582  |     1.21288  |     1.23611  |       0.151128  |              1        |
| recent_oos_2025H2_2026Apr | Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 |            -1 |     -0.00051143 |           7294 |   1.38927  |   0.563268 |     1.37804  |     1.31922  |     1.26529  |       0.113213  |              0.999726 |
| fresh_may_2026            | Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 |            -1 |     -0.00051143 |            456 |   0.730215 |   0.693215 |     0.716902 |     0.708137 |     0.726767 |       0.0732673 |              0.90297  |

## Control Detail

| expression                                               |   horizon | control_mode   | split                     |      net10 |   active_hours |
|:---------------------------------------------------------|----------:|:---------------|:--------------------------|-----------:|---------------:|
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 | sign_flip      | train_2024                |  5.75285   |           8751 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 | sign_flip      | validation_2025H1         | -1.81666   |           4344 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 | sign_flip      | recent_oos_2025H2_2026Apr | -2.6009    |           7294 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 | sign_flip      | fresh_may_2026            | -0.665454  |            480 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 | wrong_lag      | train_2024                | -4.81358   |           8727 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 | wrong_lag      | validation_2025H1         | -0.421204  |           4344 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 | wrong_lag      | recent_oos_2025H2_2026Apr | -0.196203  |           7292 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 | wrong_lag      | fresh_may_2026            |  0.298789  |            480 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 | row_shuffle    | train_2024                | -5.63868   |           8751 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 | row_shuffle    | validation_2025H1         | -2.38195   |           4344 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 | row_shuffle    | recent_oos_2025H2_2026Apr | -4.53307   |           7294 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 | row_shuffle    | fresh_may_2026            | -0.444242  |            480 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 | time_shuffle   | train_2024                | -7.31427   |           8739 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 | time_shuffle   | validation_2025H1         | -1.73798   |           4342 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 | time_shuffle   | recent_oos_2025H2_2026Apr | -4.38923   |           7284 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 | time_shuffle   | fresh_may_2026            | -0.465758  |            479 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 | sign_flip      | train_2024                |  9.20034   |           8751 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 | sign_flip      | validation_2025H1         | -2.43034   |           4344 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 | sign_flip      | recent_oos_2025H2_2026Apr | -3.04127   |           7294 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 | sign_flip      | fresh_may_2026            | -0.804215  |            456 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 | wrong_lag      | train_2024                | -4.25585   |           8727 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 | wrong_lag      | validation_2025H1         | -0.639665  |           4344 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 | wrong_lag      | recent_oos_2025H2_2026Apr | -0.0877866 |           7292 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 | wrong_lag      | fresh_may_2026            |  0.552825  |            456 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 | row_shuffle    | train_2024                | -6.02461   |           8751 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 | row_shuffle    | validation_2025H1         | -2.23641   |           4344 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 | row_shuffle    | recent_oos_2025H2_2026Apr | -5.57691   |           7294 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 | row_shuffle    | fresh_may_2026            | -0.12155   |            456 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 | time_shuffle   | train_2024                | -3.47249   |           8743 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 | time_shuffle   | validation_2025H1         | -3.11989   |           4339 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 | time_shuffle   | recent_oos_2025H2_2026Apr | -7.45106   |           7283 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 | time_shuffle   | fresh_may_2026            | -0.390731  |            456 |

## Baseline Comparison

| split                     | expression                                               |   horizon |   orientation |   base_train_ic |   active_hours |       net10 |      net20 |   lag1_net10 |   lag2_net10 |   lag3_net10 |   turnover_mean |   gross_exposure_mean |
|:--------------------------|:---------------------------------------------------------|----------:|--------------:|----------------:|---------------:|------------:|-----------:|-------------:|-------------:|-------------:|----------------:|----------------------:|
| train_2024                | ZScore(global_long_short_account_ratio_zscore_168h)      |        24 |             1 |      0.00384522 |           8751 |  -7.93851   |  -9.03135  |   -7.22796   |   -6.70067   |   -6.29145   |       0.124554  |              0.997379 |
| validation_2025H1         | ZScore(global_long_short_account_ratio_zscore_168h)      |        24 |             1 |      0.00384522 |           4344 |   0.503662  |  -0.152838 |    0.669108  |    0.695569  |    0.762743  |       0.151128  |              1        |
| recent_oos_2025H2_2026Apr | ZScore(global_long_short_account_ratio_zscore_168h)      |        24 |             1 |      0.00384522 |           7294 |   0.948899  |   0.122899 |    1.056     |    1.12174   |    1.23089   |       0.113213  |              0.999726 |
| fresh_may_2026            | ZScore(global_long_short_account_ratio_zscore_168h)      |        24 |             1 |      0.00384522 |            480 |   0.588787  |   0.550454 |    0.615107  |    0.649916  |    0.658911  |       0.0759076 |              0.950495 |
| train_2024                | ZScore(global_long_short_account_ratio_zscore_168h)      |        48 |             1 |      0.00051143 |           8751 | -11.386     | -12.4788   |  -11.046     |  -10.6065    |  -10.2152    |       0.124554  |              0.997379 |
| validation_2025H1         | ZScore(global_long_short_account_ratio_zscore_168h)      |        48 |             1 |      0.00051143 |           4344 |   1.11734   |   0.460841 |    1.20582   |    1.21288   |    1.23611   |       0.151128  |              1        |
| recent_oos_2025H2_2026Apr | ZScore(global_long_short_account_ratio_zscore_168h)      |        48 |             1 |      0.00051143 |           7294 |   1.38927   |   0.563268 |    1.37804   |    1.31922   |    1.26529   |       0.113213  |              0.999726 |
| fresh_may_2026            | ZScore(global_long_short_account_ratio_zscore_168h)      |        48 |             1 |      0.00051143 |            456 |   0.730215  |   0.693215 |    0.716902  |    0.708137  |    0.726767  |       0.0732673 |              0.90297  |
| train_2024                | Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 |            -1 |     -0.00384522 |           8751 |  -7.93851   |  -9.03135  |   -7.22796   |   -6.70067   |   -6.29145   |       0.124554  |              0.997379 |
| validation_2025H1         | Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 |            -1 |     -0.00384522 |           4344 |   0.503662  |  -0.152838 |    0.669108  |    0.695569  |    0.762743  |       0.151128  |              1        |
| recent_oos_2025H2_2026Apr | Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 |            -1 |     -0.00384522 |           7294 |   0.948899  |   0.122899 |    1.056     |    1.12174   |    1.23089   |       0.113213  |              0.999726 |
| fresh_may_2026            | Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 |            -1 |     -0.00384522 |            480 |   0.588787  |   0.550454 |    0.615107  |    0.649916  |    0.658911  |       0.0759076 |              0.950495 |
| train_2024                | Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 |            -1 |     -0.00051143 |           8751 | -11.386     | -12.4788   |  -11.046     |  -10.6065    |  -10.2152    |       0.124554  |              0.997379 |
| validation_2025H1         | Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 |            -1 |     -0.00051143 |           4344 |   1.11734   |   0.460841 |    1.20582   |    1.21288   |    1.23611   |       0.151128  |              1        |
| recent_oos_2025H2_2026Apr | Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 |            -1 |     -0.00051143 |           7294 |   1.38927   |   0.563268 |    1.37804   |    1.31922   |    1.26529   |       0.113213  |              0.999726 |
| fresh_may_2026            | Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 |            -1 |     -0.00051143 |            456 |   0.730215  |   0.693215 |    0.716902  |    0.708137  |    0.726767  |       0.0732673 |              0.90297  |
| train_2024                | Rank(global_long_short_account_ratio_zscore_168h)        |        24 |             1 |      0.00384522 |           8751 |  -7.93851   |  -9.03135  |   -7.22796   |   -6.70067   |   -6.29145   |       0.124554  |              0.997379 |
| validation_2025H1         | Rank(global_long_short_account_ratio_zscore_168h)        |        24 |             1 |      0.00384522 |           4344 |   0.503662  |  -0.152838 |    0.669108  |    0.695569  |    0.762743  |       0.151128  |              1        |
| recent_oos_2025H2_2026Apr | Rank(global_long_short_account_ratio_zscore_168h)        |        24 |             1 |      0.00384522 |           7294 |   0.948899  |   0.122899 |    1.056     |    1.12174   |    1.23089   |       0.113213  |              0.999726 |
| fresh_may_2026            | Rank(global_long_short_account_ratio_zscore_168h)        |        24 |             1 |      0.00384522 |            480 |   0.588787  |   0.550454 |    0.615107  |    0.649916  |    0.658911  |       0.0759076 |              0.950495 |
| train_2024                | Rank(global_long_short_account_ratio_zscore_168h)        |        48 |             1 |      0.00051143 |           8751 | -11.386     | -12.4788   |  -11.046     |  -10.6065    |  -10.2152    |       0.124554  |              0.997379 |
| validation_2025H1         | Rank(global_long_short_account_ratio_zscore_168h)        |        48 |             1 |      0.00051143 |           4344 |   1.11734   |   0.460841 |    1.20582   |    1.21288   |    1.23611   |       0.151128  |              1        |
| recent_oos_2025H2_2026Apr | Rank(global_long_short_account_ratio_zscore_168h)        |        48 |             1 |      0.00051143 |           7294 |   1.38927   |   0.563268 |    1.37804   |    1.31922   |    1.26529   |       0.113213  |              0.999726 |
| fresh_may_2026            | Rank(global_long_short_account_ratio_zscore_168h)        |        48 |             1 |      0.00051143 |            456 |   0.730215  |   0.693215 |    0.716902  |    0.708137  |    0.726767  |       0.0732673 |              0.90297  |
| train_2024                | Neg(ZScore(global_long_short_account_ratio_change_24h))  |        24 |             1 |      0.00715846 |           8750 |   3.77786   |   2.27719  |    3.2155    |    2.78519   |    2.59624   |       0.171036  |              0.997265 |
| validation_2025H1         | Neg(ZScore(global_long_short_account_ratio_change_24h))  |        24 |             1 |      0.00715846 |           4344 |  -3.55396   |  -4.39312  |   -3.6584    |   -3.81547   |   -3.80956   |       0.193178  |              1        |
| recent_oos_2025H2_2026Apr | Neg(ZScore(global_long_short_account_ratio_change_24h))  |        24 |             1 |      0.00715846 |           7294 |  -2.2411    |  -3.38193  |   -2.51309   |   -2.79486   |   -2.98563   |       0.156364  |              0.999726 |
| fresh_may_2026            | Neg(ZScore(global_long_short_account_ratio_change_24h))  |        24 |             1 |      0.00715846 |            480 |  -0.272531  |  -0.336198 |   -0.375355  |   -0.465576  |   -0.533726  |       0.126073  |              0.950495 |
| train_2024                | Neg(ZScore(global_long_short_account_ratio_change_24h))  |        48 |             1 |      0.0156284  |           8750 |  13.5343    |  12.0336   |   13.5776    |   13.3324    |   13.3213    |       0.171036  |              0.997265 |
| validation_2025H1         | Neg(ZScore(global_long_short_account_ratio_change_24h))  |        48 |             1 |      0.0156284  |           4344 |  -4.81738   |  -5.65654  |   -5.05483   |   -5.26097   |   -5.18011   |       0.193178  |              1        |
| recent_oos_2025H2_2026Apr | Neg(ZScore(global_long_short_account_ratio_change_24h))  |        48 |             1 |      0.0156284  |           7294 |  -4.21467   |  -5.35551  |   -4.17157   |   -4.04751   |   -4.05208   |       0.156364  |              0.999726 |
| fresh_may_2026            | Neg(ZScore(global_long_short_account_ratio_change_24h))  |        48 |             1 |      0.0156284  |            456 |  -0.0747575 |  -0.134257 |   -0.0583177 |   -0.0368315 |    0.0271677 |       0.117822  |              0.90297  |
| train_2024                | Neg(ZScore(top_long_short_account_ratio_zscore_168h))    |        24 |             1 |      0.00144169 |           8751 |   5.93617   |   4.80134  |    5.61671   |    5.57728   |    5.56011   |       0.12934   |              0.997379 |
| validation_2025H1         | Neg(ZScore(top_long_short_account_ratio_zscore_168h))    |        24 |             1 |      0.00144169 |           4344 |  -1.06457   |  -1.72274  |   -1.07848   |   -1.21545   |   -1.31063   |       0.151512  |              1        |
| recent_oos_2025H2_2026Apr | Neg(ZScore(top_long_short_account_ratio_zscore_168h))    |        24 |             1 |      0.00144169 |           7294 |  -1.46603   |  -2.31586  |   -1.65449   |   -1.82304   |   -1.89299   |       0.116479  |              0.999726 |
| fresh_may_2026            | Neg(ZScore(top_long_short_account_ratio_zscore_168h))    |        24 |             1 |      0.00144169 |            480 |  -0.187304  |  -0.227304 |   -0.248414  |   -0.323638  |   -0.391952  |       0.0792079 |              0.950495 |
| train_2024                | Neg(ZScore(top_long_short_account_ratio_zscore_168h))    |        48 |             1 |      0.00871189 |           8751 |  12.5075    |  11.3726   |   12.3514    |   12.2266    |   12.1791    |       0.12934   |              0.997379 |
| validation_2025H1         | Neg(ZScore(top_long_short_account_ratio_zscore_168h))    |        48 |             1 |      0.00871189 |           4344 |  -0.476636  |  -1.1348   |   -0.395315  |   -0.539079  |   -0.502418  |       0.151512  |              1        |
| recent_oos_2025H2_2026Apr | Neg(ZScore(top_long_short_account_ratio_zscore_168h))    |        48 |             1 |      0.00871189 |           7294 |  -1.02536   |  -1.87519  |   -1.15217   |   -1.19093   |   -1.14128   |       0.116479  |              0.999726 |
| fresh_may_2026            | Neg(ZScore(top_long_short_account_ratio_zscore_168h))    |        48 |             1 |      0.00871189 |            456 |  -0.718869  |  -0.757202 |   -0.74695   |   -0.79429   |   -0.837099  |       0.0759076 |              0.90297  |
| train_2024                | Neg(ZScore(top_long_short_position_ratio_zscore_168h))   |        24 |             1 |      0.0166297  |           8751 |  -0.481731  |  -1.33873  |   -0.687177  |   -0.84148   |   -0.762801  |       0.0976749 |              0.997379 |
| validation_2025H1         | Neg(ZScore(top_long_short_position_ratio_zscore_168h))   |        24 |             1 |      0.0166297  |           4344 |  -0.708296  |  -1.2118   |   -0.963448  |   -1.14772   |   -1.25064   |       0.115907  |              1        |
| recent_oos_2025H2_2026Apr | Neg(ZScore(top_long_short_position_ratio_zscore_168h))   |        24 |             1 |      0.0166297  |           7294 |   5.85429   |   5.04046  |    5.46503   |    5.1569    |    4.85017   |       0.111545  |              0.999726 |
| fresh_may_2026            | Neg(ZScore(top_long_short_position_ratio_zscore_168h))   |        24 |             1 |      0.0166297  |            480 |  -1.14529   |  -1.18512  |   -1.15465   |   -1.15508   |   -1.14808   |       0.0788779 |              0.950495 |
| train_2024                | Neg(ZScore(top_long_short_position_ratio_zscore_168h))   |        48 |             1 |      0.0189661  |           8751 |   4.14526   |   3.28826  |    4.16397   |    4.15208   |    4.23629   |       0.0976749 |              0.997379 |
| validation_2025H1         | Neg(ZScore(top_long_short_position_ratio_zscore_168h))   |        48 |             1 |      0.0189661  |           4344 |  -3.48218   |  -3.98568  |   -3.69215   |   -3.87582   |   -4.10562   |       0.115907  |              1        |
| recent_oos_2025H2_2026Apr | Neg(ZScore(top_long_short_position_ratio_zscore_168h))   |        48 |             1 |      0.0189661  |           7294 |   7.72432   |   6.91049  |    7.1218    |    6.62327   |    6.21935   |       0.111545  |              0.999726 |
| fresh_may_2026            | Neg(ZScore(top_long_short_position_ratio_zscore_168h))   |        48 |             1 |      0.0189661  |            456 |  -2.62672   |  -2.66355  |   -2.66799   |   -2.72958   |   -2.76694   |       0.0729373 |              0.90297  |
| train_2024                | Neg(ZScore(open_interest_zscore_168h))                   |        24 |             1 |      0.00397246 |           8751 |   0.352475  |  -0.455691 |    0.7037    |    0.827705  |    0.875313  |       0.0921093 |              0.997379 |
| validation_2025H1         | Neg(ZScore(open_interest_zscore_168h))                   |        24 |             1 |      0.00397246 |           4344 |  -3.37148   |  -3.82164  |   -3.41636   |   -3.4806    |   -3.46098   |       0.10363   |              1        |
| recent_oos_2025H2_2026Apr | Neg(ZScore(open_interest_zscore_168h))                   |        24 |             1 |      0.00397246 |           7294 |   1.15884   |   0.558171 |    1.08464   |    1.05026   |    1.06841   |       0.0823282 |              0.999726 |
| fresh_may_2026            | Neg(ZScore(open_interest_zscore_168h))                   |        24 |             1 |      0.00397246 |            480 |  -0.961911  |  -0.993411 |   -0.948239  |   -0.947577  |   -0.957202  |       0.0623762 |              0.950495 |
| train_2024                | Neg(ZScore(open_interest_zscore_168h))                   |        48 |            -1 |     -0.00105243 |           8751 |  -0.690225  |  -1.49839  |   -0.857961  |   -0.946085  |   -0.898008  |       0.0921093 |              0.997379 |
| validation_2025H1         | Neg(ZScore(open_interest_zscore_168h))                   |        48 |            -1 |     -0.00105243 |           4344 |   3.65604   |   3.20587  |    3.67793   |    3.72744   |    3.91016   |       0.10363   |              1        |
| recent_oos_2025H2_2026Apr | Neg(ZScore(open_interest_zscore_168h))                   |        48 |            -1 |     -0.00105243 |           7294 |  -7.02841   |  -7.62908  |   -7.2311    |   -7.50713   |   -7.589     |       0.0823282 |              0.999726 |
| fresh_may_2026            | Neg(ZScore(open_interest_zscore_168h))                   |        48 |            -1 |     -0.00105243 |            456 |   2.01298   |   1.98348  |    2.03941   |    2.06364   |    2.10156   |       0.0584158 |              0.90297  |

## Concentration Summary

|   horizon |   recent_positive_symbols |   recent_top_symbol_abs_share |   recent_top_month_abs_share |   recent_months_positive |   recent_months_total |
|----------:|--------------------------:|------------------------------:|-----------------------------:|-------------------------:|----------------------:|
|        24 |                         7 |                      0.248329 |                     0.315771 |                        4 |                    10 |
|        48 |                         7 |                      0.211951 |                     0.255575 |                        6 |                    10 |

## Recent Symbol Contribution

| expression                                               |   horizon | split                     | symbol   |      net10 |     gross |       fee |   active_hours |
|:---------------------------------------------------------|----------:|:--------------------------|:---------|-----------:|----------:|----------:|---------------:|
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 | recent_oos_2025H2_2026Apr | SOLUSDT  |  2.82643   |  2.88818  | 0.06175   |           3363 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 | recent_oos_2025H2_2026Apr | BCHUSDT  |  1.47031   |  1.53822  | 0.0679167 |           3907 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 | recent_oos_2025H2_2026Apr | LTCUSDT  |  0.706689  |  0.779272 | 0.0725833 |           3903 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 | recent_oos_2025H2_2026Apr | BTCUSDT  |  0.393831  |  0.447414 | 0.0535833 |           3727 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 | recent_oos_2025H2_2026Apr | ADAUSDT  |  0.377104  |  0.45077  | 0.0736667 |           3033 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 | recent_oos_2025H2_2026Apr | ETHUSDT  |  0.238463  |  0.303546 | 0.0650833 |           3538 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 | recent_oos_2025H2_2026Apr | LINKUSDT |  0.152533  |  0.219616 | 0.0670833 |           4127 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 | recent_oos_2025H2_2026Apr | BNBUSDT  | -0.170153  | -0.100153 | 0.07      |           3774 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 | recent_oos_2025H2_2026Apr | DOGEUSDT | -0.661162  | -0.576162 | 0.085     |           2981 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 | recent_oos_2025H2_2026Apr | SUIUSDT  | -0.830982  | -0.753566 | 0.0774167 |           3289 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 | recent_oos_2025H2_2026Apr | XRPUSDT  | -0.855608  | -0.777108 | 0.0785    |           3195 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 | recent_oos_2025H2_2026Apr | AVAXUSDT | -2.69856   | -2.64514  | 0.0534167 |           4927 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 | recent_oos_2025H2_2026Apr | SOLUSDT  |  4.36364   |  4.42539  | 0.06175   |           3363 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 | recent_oos_2025H2_2026Apr | ETHUSDT  |  1.9426    |  2.00769  | 0.0650833 |           3538 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 | recent_oos_2025H2_2026Apr | BCHUSDT  |  1.86659   |  1.93451  | 0.0679167 |           3907 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 | recent_oos_2025H2_2026Apr | LTCUSDT  |  1.59439   |  1.66698  | 0.0725833 |           3903 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 | recent_oos_2025H2_2026Apr | BTCUSDT  |  0.960002  |  1.01359  | 0.0535833 |           3727 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 | recent_oos_2025H2_2026Apr | BNBUSDT  |  0.196061  |  0.266061 | 0.07      |           3774 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 | recent_oos_2025H2_2026Apr | SUIUSDT  |  0.0653073 |  0.142724 | 0.0774167 |           3289 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 | recent_oos_2025H2_2026Apr | ADAUSDT  | -0.175766  | -0.102099 | 0.0736667 |           3033 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 | recent_oos_2025H2_2026Apr | LINKUSDT | -0.767686  | -0.700602 | 0.0670833 |           4127 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 | recent_oos_2025H2_2026Apr | DOGEUSDT | -2.33669   | -2.25169  | 0.085     |           2981 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 | recent_oos_2025H2_2026Apr | XRPUSDT  | -2.84595   | -2.76745  | 0.0785    |           3195 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 | recent_oos_2025H2_2026Apr | AVAXUSDT | -3.47323   | -3.41981  | 0.0534167 |           4927 |

## May Symbol Contribution

| expression                                               |   horizon | split          | symbol   |       net10 |        gross |        fee |   active_hours |
|:---------------------------------------------------------|----------:|:---------------|:---------|------------:|-------------:|-----------:|---------------:|
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 | fresh_may_2026 | SUIUSDT  |  0.766329   |  0.769912    | 0.00358333 |            170 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 | fresh_may_2026 | LINKUSDT |  0.306601   |  0.310268    | 0.00375    |            247 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 | fresh_may_2026 | AVAXUSDT |  0.161649   |  0.165232    | 0.00366667 |            320 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 | fresh_may_2026 | BCHUSDT  |  0.143524   |  0.146691    | 0.00325    |            185 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 | fresh_may_2026 | ADAUSDT  |  0.131625   |  0.134125    | 0.0025     |            229 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 | fresh_may_2026 | ETHUSDT  |  0.0241629  |  0.0273296   | 0.00316667 |            163 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 | fresh_may_2026 | BTCUSDT  | -0.00144394 |  0.000389396 | 0.00183333 |            274 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 | fresh_may_2026 | XRPUSDT  | -0.0417684  | -0.0372684   | 0.0045     |            160 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 | fresh_may_2026 | BNBUSDT  | -0.0522391  | -0.0497391   | 0.00258333 |            408 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 | fresh_may_2026 | LTCUSDT  | -0.117791   | -0.114374    | 0.0035     |            173 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 | fresh_may_2026 | DOGEUSDT | -0.234552   | -0.230969    | 0.00358333 |            204 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        24 | fresh_may_2026 | SOLUSDT  | -0.49681    | -0.494476    | 0.00241667 |            347 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 | fresh_may_2026 | SUIUSDT  |  1.16027    |  1.16377     | 0.00358333 |            166 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 | fresh_may_2026 | AVAXUSDT |  0.512771   |  0.516188    | 0.0035     |            297 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 | fresh_may_2026 | ADAUSDT  |  0.374864   |  0.377114    | 0.00233333 |            221 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 | fresh_may_2026 | BCHUSDT  |  0.230035   |  0.233201    | 0.00325    |            161 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 | fresh_may_2026 | LINKUSDT |  0.142786   |  0.146369    | 0.00358333 |            246 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 | fresh_may_2026 | ETHUSDT  |  0.141827   |  0.144661    | 0.00283333 |            148 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 | fresh_may_2026 | XRPUSDT  |  0.0785636  |  0.0828969   | 0.00433333 |            159 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 | fresh_may_2026 | BNBUSDT  | -0.081687   | -0.0793536   | 0.00241667 |            387 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 | fresh_may_2026 | BTCUSDT  | -0.220565   | -0.218732    | 0.00183333 |            274 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 | fresh_may_2026 | LTCUSDT  | -0.311952   | -0.308536    | 0.0035     |            149 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 | fresh_may_2026 | DOGEUSDT | -0.397672   | -0.394088    | 0.00358333 |            204 |
| Neg(ZScore(global_long_short_account_ratio_zscore_168h)) |        48 | fresh_may_2026 | SOLUSDT  | -0.898527   | -0.896277    | 0.00225    |            324 |

## Authorization

```json
{
  "authorizes_a7s4_small_robustness": true,
  "authorizes_alpha_proof": false,
  "authorizes_expanded_replay": false,
  "authorizes_full_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "clue_count": 2,
  "decision": "PASS_A7S3_CROWDING_CLUE_FORENSIC_COMPLETE_HOLD_PROMOTION",
  "executes_replay": "forensic_on_a7s2m_clues_only",
  "executes_search": false,
  "generated_at": "2026-05-22T09:08:05Z",
  "may_control_positive_count": 2,
  "may_policy": "stress_only_not_ranking_threshold_or_selection",
  "recent_control_positive_count": 0,
  "required_next": [
    "Treat A7S2M clues as one global-long-short crowding motif",
    "A7S-4 small robustness only if continuing: symbol/month LOO and stronger matched controls",
    "No expanded search or proof promotion"
  ],
  "unique_family_count": 1,
  "unique_formula_count": 1,
  "warnings": [
    "single_formula_two_horizons_not_independent",
    "single_family_crowding_motif",
    "may_control_positive_stress_only"
  ]
}
```

## Required Next

- Treat the clue as one crowding motif, not two independent candidates.
- If continued, run a small A7S-4 crowding-only robustness audit with symbol/month LOO and stricter controls.
- Do not run expanded search or alpha proof from A7S-3 alone.
