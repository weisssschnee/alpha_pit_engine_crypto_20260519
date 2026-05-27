# Crypto A7P-4 Productivity Forensic

- generated_at: `2026-05-20T18:46:16Z`
- source_checkpoint: `A7P3_W2PILOT`
- decision: `HOLD_A7P4_PRODUCTIVITY_TOO_LOW`
- executes_search: `False`
- executes_replay: `False`
- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`
- blockers: `['post_may_eligible_rate_below_15pct', 'non_may_rank_inverted_vs_post_may_stress']`

## Summary

A7P-4 explains the A7P-3 protected W2 pilot productivity gap. The pilot had `192` deep-audit rows and `13` post-May eligible rows, for an eligible rate of `0.0677` versus the `0.15` continuation target.

May remains stress-only in this forensic. It is used only for post-selection attribution and does not enter ranking, generation, allocation, mutation, threshold tuning, or surrogate targets.

## Decision Counts

| candidate_decision             |   count |     share |
|:-------------------------------|--------:|----------:|
| A7O_PILOT_MAY_VETOED_NEAR_MISS |     166 | 0.864583  |
| A7O_PILOT_RESEARCH_CANDIDATE   |      13 | 0.0677083 |
| A7O_PILOT_PRE_MAY_NEAR_MISS    |       7 | 0.0364583 |
| A7O_PILOT_REJECTED             |       6 | 0.03125   |

## May Gate Failure Summary

| gate                               |   fail_count |   fail_rate |
|:-----------------------------------|-------------:|------------:|
| fail_raw_may_severe                |          121 |    0.630208 |
| fail_residual_funding_may_negative |          107 |    0.557292 |
| fail_residual_gross                |           53 |    0.276042 |
| fail_raw_gross                     |           53 |    0.276042 |
| fail_residual_active_hours         |           53 |    0.276042 |
| fail_raw_active_hours              |           53 |    0.276042 |

## Eligible vs Ineligible Median Metrics

| group                 |   count |   raw_10bp__fresh_forward_2026May |   residual_vs_funding_10bp__fresh_forward_2026May |   raw_10bp__recent_oos_2025H2_2026Apr |   raw_20bp__recent_oos_2025H2_2026Apr |   execution_lag_1bar_raw_10bp__recent_oos_2025H2_2026Apr |   min_fold_component |   positive_fold_rate |   mean_turnover |   mean_gross_exposure |   pilot_rank_score |
|:----------------------|--------:|----------------------------------:|--------------------------------------------------:|--------------------------------------:|--------------------------------------:|---------------------------------------------------------:|---------------------:|---------------------:|----------------:|----------------------:|-------------------:|
| post_may_eligible     |      13 |                           7.19125 |                                          11.3125  |                               2.81825 |                               2.66855 |                                                  2.86369 |            -0.845534 |             0.923077 |       0.0208653 |              0.40018  |          0.0755236 |
| not_post_may_eligible |     179 |                          -6.18304 |                                          -3.14886 |                               2.76581 |                               2.56176 |                                                  2.75164 |             0.345607 |             1        |       0.0126306 |              0.345576 |          1.34341   |

## Non-May Rank vs Post-May Eligibility

|   rank_decile |   rows |   post_may_eligible_count |   may_vetoed_count |   median_rank_score |   median_raw_may |   median_residual_funding_may |   median_raw_recent |   post_may_eligible_rate |
|--------------:|-------:|--------------------------:|-------------------:|--------------------:|-----------------:|------------------------------:|--------------------:|-------------------------:|
|             1 |     20 |                         0 |                 20 |            2.99715  |        -14.6554  |                      -9.95385 |            4.53641  |                0         |
|             2 |     19 |                         0 |                 19 |            2.81375  |        -11.8702  |                      -8.14215 |            4.51238  |                0         |
|             3 |     19 |                         1 |                 18 |            2.21613  |        -10.311   |                      -6.67708 |            3.6242   |                0.0526316 |
|             4 |     19 |                         0 |                 19 |            1.84899  |         -8.09187 |                      -4.74606 |            3.38938  |                0         |
|             5 |     19 |                         1 |                 18 |            1.39085  |         -7.4523  |                      -4.92062 |            3.00106  |                0.0526316 |
|             6 |     19 |                         2 |                 17 |            1.01599  |          0       |                       0       |            1.82796  |                0.105263  |
|             7 |     19 |                         0 |                 19 |            0.797878 |          0       |                       0       |            1.34329  |                0         |
|             8 |     19 |                         0 |                 18 |            0.513277 |          0       |                       0       |            1.39628  |                0         |
|             9 |     19 |                         4 |                 11 |            0.153156 |         -1.37647 |                       0       |            0.958276 |                0.210526  |
|            10 |     20 |                         5 |                  7 |           -1.00772  |          0       |                       0       |            0.976025 |                0.25      |

## Top Reject Reasons

| candidate_decision             | reason                                     |   count |
|:-------------------------------|:-------------------------------------------|--------:|
| A7O_PILOT_MAY_VETOED_NEAR_MISS | may_stress_severe_fail                     |     116 |
| A7O_PILOT_MAY_VETOED_NEAR_MISS | may_residual_funding_negative              |     103 |
| A7O_PILOT_MAY_VETOED_NEAR_MISS | may_stress_no_raw_activity                 |      48 |
| A7O_PILOT_MAY_VETOED_NEAR_MISS | may_stress_no_residual_activity            |      48 |
| A7O_PILOT_MAY_VETOED_NEAR_MISS | may_stress_raw_active_hours_below_min      |      48 |
| A7O_PILOT_MAY_VETOED_NEAR_MISS | may_stress_residual_active_hours_below_min |      48 |
| A7O_PILOT_RESEARCH_CANDIDATE   | none                                       |      13 |
| A7O_PILOT_REJECTED             | cost20_recent_nonpositive                  |       6 |
| A7O_PILOT_REJECTED             | raw_recent_nonpositive                     |       6 |
| A7O_PILOT_REJECTED             | lag1_recent_nonpositive                    |       4 |
| A7O_PILOT_REJECTED             | may_stress_no_raw_activity                 |       4 |
| A7O_PILOT_REJECTED             | may_stress_no_residual_activity            |       4 |
| A7O_PILOT_REJECTED             | may_stress_raw_active_hours_below_min      |       4 |
| A7O_PILOT_REJECTED             | may_stress_residual_active_hours_below_min |       4 |
| A7O_PILOT_REJECTED             | residual_funding_recent_nonpositive        |       4 |
| A7O_PILOT_PRE_MAY_NEAR_MISS    | cost20_recent_nonpositive                  |       3 |
| A7O_PILOT_PRE_MAY_NEAR_MISS    | may_residual_funding_negative              |       3 |
| A7O_PILOT_PRE_MAY_NEAR_MISS    | may_stress_severe_fail                     |       3 |
| A7O_PILOT_PRE_MAY_NEAR_MISS    | raw_validation_nonpositive                 |       3 |
| A7O_PILOT_MAY_VETOED_NEAR_MISS | may_stress_material_fail                   |       2 |

## Fold Failure Summary

| fold_id                    |   rows |   negative_count |   median_ann |   mean_ann |   p10_ann |   p90_ann |   median_active_hours |   median_gross |   negative_rate | series                   |
|:---------------------------|-------:|-----------------:|-------------:|-----------:|----------:|----------:|----------------------:|---------------:|----------------:|:-------------------------|
| F11_cross_symbol_crowding  |   1536 |              756 |    0.0666157 |   0.115499 |  -3.27378 |   3.80786 |                  3463 |       0.390558 |        0.492188 | raw_10bp                 |
| F4_basis_dislocation       |   1536 |              708 |    0.219683  |   0.235272 |  -2.61594 |   3.18864 |                  3463 |       0.388886 |        0.460938 | raw_10bp                 |
| F1_high_realized_vol       |   1536 |              685 |    0.324422  |   0.275703 |  -4.87601 |   4.6136  |                  3463 |       0.347361 |        0.445964 | raw_10bp                 |
| F3_high_liquidity_high_vol |   1536 |              665 |    0.246222  |   0.257031 |  -5.14447 |   5.16246 |                  3341 |       0.362324 |        0.432943 | raw_10bp                 |
| F6_cross_symbol_dispersion |   1536 |              618 |    0.419168  |   0.63822  |  -2.46518 |   4.23579 |                  3463 |       0.331477 |        0.402344 | raw_10bp                 |
| F5_funding_neutral         |   1536 |              576 |    0.484361  |   0.704316 |  -2.3318  |   3.92015 |                  5775 |       0.409414 |        0.375    | raw_10bp                 |
| F2_low_liquidity           |   1536 |              559 |    0.557203  |   1.06071  |  -2.0799  |   4.64481 |                  3463 |       0.410929 |        0.363932 | raw_10bp                 |
| F0_validation_2025H1       |   1536 |              551 |    0.868222  |   1.21261  |  -2.39023 |   5.46859 |                  4296 |       0.320905 |        0.358724 | raw_10bp                 |
| F8_low_vol_high_liquidity  |   1536 |              545 |    0.925919  |   1.99217  |  -4.87881 |   9.7924  |                   478 |       0.390123 |        0.354818 | raw_10bp                 |
| F9_liquidity_shock         |   1536 |              538 |    0.649419  |   0.747806 |  -1.90036 |   3.55233 |                  2886 |       0.382871 |        0.35026  | raw_10bp                 |
| F10_volatility_compression |   1536 |              514 |    0.90884   |   1.11895  |  -1.90196 |   4.60716 |                  4041 |       0.383008 |        0.334635 | raw_10bp                 |
| F7_trend_reversal          |   1536 |              497 |    0.865633  |   1.05251  |  -1.99014 |   4.31243 |                  4178 |       0.377785 |        0.323568 | raw_10bp                 |
| F0_recent_2025H2_2026Apr   |   1536 |              495 |    0.698416  |   0.851824 |  -1.82603 |   3.74841 |                  7248 |       0.41165  |        0.322266 | raw_10bp                 |
| F11_cross_symbol_crowding  |   1536 |              696 |    0.267224  |   0.448693 |  -4.72287 |   5.51016 |                  3463 |       0.390558 |        0.453125 | residual_vs_funding_10bp |
| F1_high_realized_vol       |   1536 |              658 |    0.618412  |   0.657423 |  -6.15448 |   6.72953 |                  3463 |       0.347361 |        0.428385 | residual_vs_funding_10bp |
| F4_basis_dislocation       |   1536 |              657 |    0.522573  |   0.592555 |  -3.95144 |   5.30653 |                  3463 |       0.388886 |        0.427734 | residual_vs_funding_10bp |
| F3_high_liquidity_high_vol |   1536 |              628 |    0.482389  |   0.572196 |  -6.08744 |   6.96594 |                  3341 |       0.362324 |        0.408854 | residual_vs_funding_10bp |
| F6_cross_symbol_dispersion |   1536 |              627 |    0.605447  |   0.980284 |  -3.96915 |   6.66516 |                  3463 |       0.331477 |        0.408203 | residual_vs_funding_10bp |
| F5_funding_neutral         |   1536 |              608 |    0.62395   |   1.01643  |  -3.88511 |   6.62096 |                  5775 |       0.409414 |        0.395833 | residual_vs_funding_10bp |
| F9_liquidity_shock         |   1536 |              597 |    0.692333  |   1.00375  |  -3.10705 |   5.92579 |                  2886 |       0.382871 |        0.388672 | residual_vs_funding_10bp |
| F0_validation_2025H1       |   1536 |              580 |    1.00113   |   1.47939  |  -3.66818 |   7.87534 |                  4296 |       0.320905 |        0.377604 | residual_vs_funding_10bp |
| F0_recent_2025H2_2026Apr   |   1536 |              550 |    0.803769  |   1.20684  |  -3.27715 |   6.66019 |                  7248 |       0.41165  |        0.358073 | residual_vs_funding_10bp |
| F10_volatility_compression |   1536 |              545 |    1.07378   |   1.54702  |  -3.25964 |   7.52834 |                  4041 |       0.383008 |        0.354818 | residual_vs_funding_10bp |
| F8_low_vol_high_liquidity  |   1536 |              543 |    0.812185  |   1.95487  |  -5.66102 |  10.5624  |                   478 |       0.390123 |        0.353516 | residual_vs_funding_10bp |
| F7_trend_reversal          |   1536 |              538 |    0.973776  |   1.373    |  -3.1798  |   6.92267 |                  4178 |       0.377785 |        0.35026  | residual_vs_funding_10bp |
| F2_low_liquidity           |   1536 |              474 |    1.16081   |   1.46634  |  -3.13762 |   6.47129 |                  3463 |       0.410929 |        0.308594 | residual_vs_funding_10bp |
| F11_cross_symbol_crowding  |   1536 |              698 |    0.255196  |   0.428955 |  -4.73201 |   5.47003 |                  3463 |       0.390558 |        0.454427 | residual_vs_core4_10bp   |
| F4_basis_dislocation       |   1536 |              666 |    0.497622  |   0.562153 |  -4.00336 |   5.23527 |                  3463 |       0.388886 |        0.433594 | residual_vs_core4_10bp   |
| F1_high_realized_vol       |   1536 |              659 |    0.609807  |   0.630914 |  -6.13116 |   6.71923 |                  3463 |       0.347361 |        0.429036 | residual_vs_core4_10bp   |
| F6_cross_symbol_dispersion |   1536 |              629 |    0.595773  |   0.972701 |  -3.98528 |   6.65058 |                  3463 |       0.331477 |        0.409505 | residual_vs_core4_10bp   |

## Top Group Productivity

### hypothesis

| hypothesis_family                           |   deep_count |   post_may_eligible_count |   may_vetoed_count |   pre_may_near_miss_count |   rejected_count |   avg_rank_score |   avg_raw_may |   avg_residual_funding_may |   avg_raw_recent |   avg_cost20_recent |   avg_lag1_recent |   avg_min_fold |   avg_positive_fold_rate |   post_may_eligible_rate | summary_name   |
|:--------------------------------------------|-------------:|--------------------------:|-------------------:|--------------------------:|-----------------:|-----------------:|--------------:|---------------------------:|-----------------:|--------------------:|------------------:|---------------:|-------------------------:|-------------------------:|:---------------|
| H12_horizon_ensemble_stability              |           15 |                         3 |                 12 |                         0 |                0 |         0.522832 |     -5.03904  |                   -3.21608 |          1.5794  |             1.33749 |           1.57066 |    -0.426378   |                 0.955897 |                0.2       | hypothesis     |
| H06_liquidity_structure_ex_realized_vol_mul |           24 |                         2 |                 19 |                         1 |                2 |         1.22604  |     -9.19842  |                   -6.14983 |          3.2952  |             3.05401 |           3.28309 |     0.255444   |                 0.976923 |                0.0833333 | hypothesis     |
| H14_open_ast_cem_diversity                  |            9 |                         2 |                  5 |                         0 |                2 |         0.312407 |      1.23141  |                    1.47679 |          1.7913  |             1.69794 |           1.80863 |    -0.517169   |                 0.832479 |                0.222222  | hypothesis     |
| H05_volatility_structure_ex_liquidity_mul   |           30 |                         1 |                 27 |                         2 |                0 |         1.52461  |     -6.35422  |                   -5.01646 |          3.06599 |             2.84193 |           3.05625 |     0.568235   |                 0.962564 |                0.0333333 | hypothesis     |
| H02_cross_symbol_dispersion_reversal        |           21 |                         1 |                 20 |                         0 |                0 |         1.73938  |     -8.53068  |                   -5.93523 |          3.36587 |             3.23076 |           3.34856 |     0.768121   |                 0.975092 |                0.047619  | hypothesis     |
| H07_taker_flow_lag_stable                   |           21 |                         1 |                 19 |                         1 |                0 |         1.35788  |     -9.82187  |                   -7.22771 |          3.90874 |             3.78553 |           3.85947 |     0.403614   |                 0.957509 |                0.047619  | hypothesis     |
| H00_low_turnover_robust                     |           12 |                         1 |                 10 |                         1 |                0 |         1.29798  |     -5.72151  |                   -1.8836  |          2.8801  |             2.78942 |           2.88396 |     0.382496   |                 0.917949 |                0.0833333 | hypothesis     |
| H01_cross_symbol_relative_strength          |            9 |                         1 |                  7 |                         1 |                0 |         0.924034 |     -9.06316  |                   -6.67503 |          4.23747 |             4.11484 |           4.20544 |     0.00602056 |                 0.921368 |                0.111111  | hypothesis     |
| H13_symbol_tier_relative                    |            6 |                         1 |                  5 |                         0 |                0 |         1.08272  |     -0.706786 |                    1.7594  |          2.32079 |             2.16487 |           2.30063 |     0.125435   |                 0.961538 |                0.166667  | hypothesis     |
| H10_range_breakout_failure                  |           15 |                         0 |                 15 |                         0 |                0 |         1.43813  |     -8.7303   |                   -5.49107 |          2.48598 |             2.35228 |           2.4625  |     0.466577   |                 0.975385 |                0         | hypothesis     |

### feature_family

| feature_family_set       |   deep_count |   post_may_eligible_count |   may_vetoed_count |   pre_may_near_miss_count |   rejected_count |   avg_rank_score |   avg_raw_may |   avg_residual_funding_may |   avg_raw_recent |   avg_cost20_recent |   avg_lag1_recent |   avg_min_fold |   avg_positive_fold_rate |   post_may_eligible_rate | summary_name   |
|:-------------------------|-------------:|--------------------------:|-------------------:|--------------------------:|-----------------:|-----------------:|--------------:|---------------------------:|-----------------:|--------------------:|------------------:|---------------:|-------------------------:|-------------------------:|:---------------|
| P3_trade_size            |           24 |                         6 |                 14 |                         2 |                2 |         0.613753 |       2.04033 |                    2.6901  |          1.82851 |             1.72889 |           1.85766 |      -0.264038 |                 0.880769 |                0.25      | feature_family |
| P0_price_return          |           15 |                         3 |                 12 |                         0 |                0 |         1.72743  |      -7.53463 |                   -4.1402  |          3.62697 |             3.40598 |           3.57566 |       0.748542 |                 0.984615 |                0.2       | feature_family |
| P14_horizon_spread       |           24 |                         1 |                 22 |                         1 |                0 |         1.44238  |     -10.8572  |                   -7.38222 |          3.14993 |             2.99294 |           3.11963 |       0.477238 |                 0.969231 |                0.0416667 | feature_family |
| P7_cross_symbol_relative |           15 |                         1 |                  9 |                         2 |                3 |         0.165009 |      -3.70064 |                   -2.43093 |          1.46778 |             1.16783 |           1.45954 |      -0.72687  |                 0.900513 |                0.0666667 | feature_family |
| P2_liquidity             |            6 |                         1 |                  5 |                         0 |                0 |         0.347362 |       3.03868 |                    4.43306 |          1.25382 |             1.20354 |           1.22615 |      -0.481743 |                 0.830769 |                0.166667  | feature_family |
| P5_basis_premium         |            6 |                         1 |                  5 |                         0 |                0 |         2.19015  |      -6.86602 |                   -5.99754 |          4.67863 |             4.48241 |           4.63868 |       1.19576  |                 1        |                0.166667  | feature_family |
| P1_range_volatility      |           33 |                         0 |                 33 |                         0 |                0 |         1.91439  |     -11.6684  |                   -8.43749 |          3.49009 |             3.32682 |           3.4562  |       0.92521  |                 0.993473 |                0         | feature_family |
| P11_volatility_basis     |           24 |                         0 |                 23 |                         0 |                1 |         1.80994  |      -7.35253 |                   -4.33645 |          3.11444 |             2.95723 |           3.1147  |       0.856587 |                 0.957692 |                0         | feature_family |
| P10_price_liquidity      |           18 |                         0 |                 17 |                         1 |                0 |         0.829348 |      -6.91465 |                   -6.4958  |          2.68038 |             2.51816 |           2.68981 |      -0.108013 |                 0.94188  |                0         | feature_family |
| P12_liquidity_flow       |            6 |                         0 |                  5 |                         1 |                0 |        -0.300353 |      -6.27488 |                   -6.05837 |          3.1441  |             3.03857 |           3.13579 |      -1.08216  |                 0.784615 |                0         | feature_family |

### horizon

| temporal_horizon_class   |   deep_count |   post_may_eligible_count |   may_vetoed_count |   pre_may_near_miss_count |   rejected_count |   avg_rank_score |   avg_raw_may |   avg_residual_funding_may |   avg_raw_recent |   avg_cost20_recent |   avg_lag1_recent |   avg_min_fold |   avg_positive_fold_rate |   post_may_eligible_rate | summary_name   |
|:-------------------------|-------------:|--------------------------:|-------------------:|--------------------------:|-----------------:|-----------------:|--------------:|---------------------------:|-----------------:|--------------------:|------------------:|---------------:|-------------------------:|-------------------------:|:---------------|
| H72                      |           57 |                         5 |                 47 |                         3 |                2 |          1.14099 |      -8.88202 |                  -7.12367  |          3.3957  |             3.22514 |           3.37818 |       0.219284 |                 0.926316 |                0.0877193 | horizon        |
| H48                      |           30 |                         5 |                 22 |                         0 |                3 |          1.16877 |      -2.45063 |                  -0.681421 |          2.63356 |             2.43981 |           2.63746 |       0.233634 |                 0.940513 |                0.166667  | horizon        |
| spread_6_vs_24           |           21 |                         1 |                 19 |                         1 |                0 |          1.55691 |      -6.91803 |                  -3.83698  |          2.95303 |             2.82411 |           2.94072 |       0.615213 |                 0.945055 |                0.047619  | horizon        |
| ensemble_6_12_24_48      |           15 |                         1 |                 13 |                         1 |                0 |          1.11413 |      -6.675   |                  -3.59989  |          3.33972 |             3.21197 |           3.34469 |       0.171882 |                 0.945641 |                0.0666667 | horizon        |
| H12                      |            9 |                         1 |                  8 |                         0 |                0 |          1.16962 |      -2.78185 |                  -1.25325  |          1.21386 |             1.09414 |           1.21231 |       0.193611 |                 0.979487 |                0.111111  | horizon        |
| H24                      |           27 |                         0 |                 26 |                         1 |                0 |          1.14885 |      -3.5368  |                  -1.53558  |          1.78131 |             1.58011 |           1.75208 |       0.212338 |                 0.94245  |                0         | horizon        |
| mixed_12_48              |           12 |                         0 |                 12 |                         0 |                0 |          1.84298 |     -11.5939  |                  -8.52261  |          3.65869 |             3.46403 |           3.65404 |       0.853007 |                 0.994872 |                0         | horizon        |
| mixed_6_24               |           12 |                         0 |                 12 |                         0 |                0 |          2.14734 |     -12.6725  |                  -9.35454  |          3.80311 |             3.69643 |           3.74891 |       1.15014  |                 1        |                0         | horizon        |
| spread_12_vs_48          |            9 |                         0 |                  7 |                         1 |                1 |          1.03743 |      -7.02068 |                  -5.44731  |          2.18813 |             2.03128 |           2.18368 |       0.137883 |                 0.904274 |                0         | horizon        |

### operator

| operator_motif   |   deep_count |   post_may_eligible_count |   may_vetoed_count |   pre_may_near_miss_count |   rejected_count |   avg_rank_score |   avg_raw_may |   avg_residual_funding_may |   avg_raw_recent |   avg_cost20_recent |   avg_lag1_recent |   avg_min_fold |   avg_positive_fold_rate |   post_may_eligible_rate | summary_name   |
|:-----------------|-------------:|--------------------------:|-------------------:|--------------------------:|-----------------:|-----------------:|--------------:|---------------------------:|-----------------:|--------------------:|------------------:|---------------:|-------------------------:|-------------------------:|:---------------|
| SafeDivZScore    |           21 |                         4 |                 14 |                         1 |                2 |         0.238076 |      -5.23302 |                 -3.59947   |          2.07294 |            1.80152  |           2.03456 |     -0.695394  |                 0.940659 |                0.190476  | operator       |
| TSStdZScore      |           21 |                         2 |                 19 |                         0 |                0 |         1.49737  |      -2.83117 |                  0.0242969 |          2.43621 |            2.29669  |           2.40644 |      0.564936  |                 0.936264 |                0.0952381 | operator       |
| WinsorZScore     |            6 |                         2 |                  4 |                         0 |                0 |         1.67861  |      -5.9055  |                 -3.00356   |          3.93007 |            3.79588  |           3.96602 |      0.710264  |                 0.971795 |                0.333333  | operator       |
| ZScore           |            6 |                         2 |                  3 |                         1 |                0 |         0.827193 |       1.63209 |                  2.90264   |          2.37864 |            2.27929  |           2.40642 |     -0.0622357 |                 0.892308 |                0.333333  | operator       |
| RollingMaxRank   |           15 |                         1 |                 14 |                         0 |                0 |         1.71561  |      -6.10424 |                 -2.9739    |          3.71937 |            3.58918  |           3.69856 |      0.73478   |                 0.984615 |                0.0666667 | operator       |
| DecayZScore      |            9 |                         1 |                  7 |                         1 |                0 |         0.709595 |      -3.60946 |                 -3.10599   |          2.11844 |            1.93542  |           2.10351 |     -0.223901  |                 0.938462 |                0.111111  | operator       |
| ClipRank         |            6 |                         1 |                  4 |                         1 |                0 |         0.823636 |      -1.95132 |                 -0.756319  |          1.0463  |            0.947039 |           1.02494 |     -0.0376322 |                 0.864103 |                0.166667  | operator       |
| NegRank          |           15 |                         0 |                 15 |                         0 |                0 |         1.94986  |     -10.5352  |                 -7.39789   |          2.78303 |            2.55894  |           2.7472  |      0.955987  |                 1        |                0         | operator       |
| AddZScore        |           12 |                         0 |                 12 |                         0 |                0 |         1.53297  |      -8.08635 |                 -5.53975   |          3.06967 |            2.82457  |           3.05424 |      0.56026   |                 0.979487 |                0         | operator       |
| RollingMinRank   |           12 |                         0 |                 10 |                         0 |                2 |         1.67017  |      -8.40272 |                 -4.77654   |          3.88849 |            3.79754  |           3.88474 |      0.748335  |                 0.924359 |                0         | operator       |

### feature_operator_horizon

| feature_family_set       | operator_motif   | temporal_horizon_class   |   deep_count |   post_may_eligible_count |   may_vetoed_count |   pre_may_near_miss_count |   rejected_count |   avg_rank_score |   avg_raw_may |   avg_residual_funding_may |   avg_raw_recent |   avg_cost20_recent |   avg_lag1_recent |   avg_min_fold |   avg_positive_fold_rate |   post_may_eligible_rate | summary_name             |
|:-------------------------|:-----------------|:-------------------------|-------------:|--------------------------:|-------------------:|--------------------------:|-----------------:|-----------------:|--------------:|---------------------------:|-----------------:|--------------------:|------------------:|---------------:|-------------------------:|-------------------------:|:-------------------------|
| P0_price_return          | SafeDivZScore    | H72                      |            3 |                         3 |                  0 |                         0 |                0 |        -1.08954  |      1.58903  |                    1.59686 |         0.882837 |            0.387376 |          0.839598 |     -2         |                 0.923077 |                 1        | feature_operator_horizon |
| P3_trade_size            | WinsorZScore     | H48                      |            3 |                         2 |                  1 |                         0 |                0 |         0.360006 |      3.69422  |                    4.43037 |         3.84923  |            3.69352  |          3.91084  |     -0.579472  |                 0.94359  |                 0.666667 | feature_operator_horizon |
| P14_horizon_spread       | ClipRank         | H12                      |            3 |                         1 |                  2 |                         0 |                0 |         0.934318 |     -3.90264  |                   -1.51264 |         1.16802  |            1.00258  |          1.11687  |     -0.0250644 |                 0.964103 |                 0.333333 | feature_operator_horizon |
| P2_liquidity             | TSStdZScore      | H72                      |            3 |                         1 |                  2 |                         0 |                0 |         0.228299 |      6.07736  |                    8.86612 |         0.955542 |            0.903654 |          0.939472 |     -0.606064  |                 0.835897 |                 0.333333 | feature_operator_horizon |
| P3_trade_size            | DecayZScore      | ensemble_6_12_24_48      |            3 |                         1 |                  2 |                         0 |                0 |         0.119437 |      2.66055  |                    3.79891 |         1.91512  |            1.78727  |          1.90381  |     -0.800039  |                 0.923077 |                 0.333333 | feature_operator_horizon |
| P3_trade_size            | TSStdZScore      | H48                      |            3 |                         1 |                  2 |                         0 |                0 |         0.919114 |      6.70365  |                    7.48619 |         1.37565  |            1.25294  |          1.39735  |     -0.0255651 |                 0.948718 |                 0.333333 | feature_operator_horizon |
| P3_trade_size            | ZScore           | H72                      |            3 |                         1 |                  2 |                         0 |                0 |         0.617649 |      2.39708  |                    2.65161 |         1.98897  |            1.87775  |          1.99757  |     -0.235352  |                 0.85641  |                 0.333333 | feature_operator_horizon |
| P3_trade_size            | ZScore           | spread_6_vs_24           |            3 |                         1 |                  1 |                         1 |                0 |         1.03674  |      0.867103 |                    3.15368 |         2.76831  |            2.68083  |          2.81528  |      0.11088   |                 0.928205 |                 0.333333 | feature_operator_horizon |
| P5_basis_premium         | RollingMaxRank   | H48                      |            3 |                         1 |                  2 |                         0 |                0 |         1.56325  |      3.32896  |                    5.13265 |         4.36526  |            4.26159  |          4.34451  |      0.566321  |                 1        |                 0.333333 | feature_operator_horizon |
| P7_cross_symbol_relative | SafeDivZScore    | H48                      |            3 |                         1 |                  0 |                         0 |                2 |        -0.902502 |     -2.2428   |                    1.09252 |         0.972906 |            0.584737 |          0.965666 |     -1.79973   |                 0.907692 |                 0.333333 | feature_operator_horizon |

### cell

| cell_id   | hypothesis_family                           | feature_family_set       | operator_motif   | temporal_horizon_class   |   deep_count |   post_may_eligible_count |   may_vetoed_count |   pre_may_near_miss_count |   rejected_count |   avg_rank_score |   avg_raw_may |   avg_residual_funding_may |   avg_raw_recent |   avg_cost20_recent |   avg_lag1_recent |   avg_min_fold |   avg_positive_fold_rate |   post_may_eligible_rate | summary_name   |
|:----------|:--------------------------------------------|:-------------------------|:-----------------|:-------------------------|-------------:|--------------------------:|-------------------:|--------------------------:|-----------------:|-----------------:|--------------:|---------------------------:|-----------------:|--------------------:|------------------:|---------------:|-------------------------:|-------------------------:|:---------------|
| C0078     | H12_horizon_ensemble_stability              | P0_price_return          | SafeDivZScore    | H72                      |            3 |                         3 |                  0 |                         0 |                0 |        -1.08954  |      1.58903  |                    1.59686 |         0.882837 |            0.387376 |          0.839598 |     -2         |                 0.923077 |                 1        | cell           |
| C0169     | H14_open_ast_cem_diversity                  | P3_trade_size            | WinsorZScore     | H48                      |            3 |                         2 |                  1 |                         0 |                0 |         0.360006 |      3.69422  |                    4.43037 |         3.84923  |            3.69352  |          3.91084  |     -0.579472  |                 0.94359  |                 0.666667 | cell           |
| C0017     | H00_low_turnover_robust                     | P2_liquidity             | TSStdZScore      | H72                      |            3 |                         1 |                  2 |                         0 |                0 |         0.228299 |      6.07736  |                    8.86612 |         0.955542 |            0.903654 |          0.939472 |     -0.606064  |                 0.835897 |                 0.333333 | cell           |
| C0036     | H06_liquidity_structure_ex_realized_vol_mul | P3_trade_size            | TSStdZScore      | H48                      |            3 |                         1 |                  2 |                         0 |                0 |         0.919114 |      6.70365  |                    7.48619 |         1.37565  |            1.25294  |          1.39735  |     -0.0255651 |                 0.948718 |                 0.333333 | cell           |
| C0050     | H05_volatility_structure_ex_liquidity_mul   | P3_trade_size            | ZScore           | spread_6_vs_24           |            3 |                         1 |                  1 |                         1 |                0 |         1.03674  |      0.867103 |                    3.15368 |         2.76831  |            2.68083  |          2.81528  |      0.11088   |                 0.928205 |                 0.333333 | cell           |
| C0137     | H06_liquidity_structure_ex_realized_vol_mul | P7_cross_symbol_relative | SafeDivZScore    | H48                      |            3 |                         1 |                  0 |                         0 |                2 |        -0.902502 |     -2.2428   |                    1.09252 |         0.972906 |            0.584737 |          0.965666 |     -1.79973   |                 0.907692 |                 0.333333 | cell           |
| C0147     | H02_cross_symbol_dispersion_reversal        | P3_trade_size            | ZScore           | H72                      |            3 |                         1 |                  2 |                         0 |                0 |         0.617649 |      2.39708  |                    2.65161 |         1.98897  |            1.87775  |          1.99757  |     -0.235352  |                 0.85641  |                 0.333333 | cell           |
| C0164     | H01_cross_symbol_relative_strength          | P14_horizon_spread       | ClipRank         | H12                      |            3 |                         1 |                  2 |                         0 |                0 |         0.934318 |     -3.90264  |                   -1.51264 |         1.16802  |            1.00258  |          1.11687  |     -0.0250644 |                 0.964103 |                 0.333333 | cell           |
| C0238     | H13_symbol_tier_relative                    | P3_trade_size            | DecayZScore      | ensemble_6_12_24_48      |            3 |                         1 |                  2 |                         0 |                0 |         0.119437 |      2.66055  |                    3.79891 |         1.91512  |            1.78727  |          1.90381  |     -0.800039  |                 0.923077 |                 0.333333 | cell           |
| C0355     | H07_taker_flow_lag_stable                   | P5_basis_premium         | RollingMaxRank   | H48                      |            3 |                         1 |                  2 |                         0 |                0 |         1.56325  |      3.32896  |                    5.13265 |         4.36526  |            4.26159  |          4.34451  |      0.566321  |                 1        |                 0.333333 | cell           |

### return_corr_cluster

| return_corr_cluster   |   deep_count |   post_may_eligible_count |   may_vetoed_count |   pre_may_near_miss_count |   rejected_count |   avg_rank_score |   avg_raw_may |   avg_residual_funding_may |   avg_raw_recent |   avg_cost20_recent |   avg_lag1_recent |   avg_min_fold |   avg_positive_fold_rate |   post_may_eligible_rate | summary_name        |
|:----------------------|-------------:|--------------------------:|-------------------:|--------------------------:|-----------------:|-----------------:|--------------:|---------------------------:|-----------------:|--------------------:|------------------:|---------------:|-------------------------:|-------------------------:|:--------------------|
| rc_040                |            3 |                         3 |                  0 |                         0 |                0 |       -1.08954   |      1.58903  |                    1.59686 |         0.882837 |            0.387376 |          0.839598 |   -2           |                 0.923077 |                        1 | return_corr_cluster |
| rc_075                |            3 |                         3 |                  0 |                         0 |                0 |        0.0598131 |     11.3125   |                   11.3125  |         4.2237   |            4.13847  |          4.26563  |   -0.861006    |                 0.923077 |                        1 | return_corr_cluster |
| rc_008                |            1 |                         1 |                  0 |                         0 |                0 |       -0.231587  |     18.2321   |                   26.5984  |         1.66025  |            1.56703  |          1.64989  |   -1.18297     |                 0.953846 |                        1 | return_corr_cluster |
| rc_020                |            1 |                         1 |                  0 |                         0 |                0 |        0.977445  |     20.111    |                   22.4586  |         2.12708  |            1.90989  |          2.23133  |   -0.000948484 |                 0.984615 |                        1 | return_corr_cluster |
| rc_032                |            1 |                         1 |                  0 |                         0 |                0 |        1.02224   |      6.10501  |                   11.7135  |         5.01315  |            4.95785  |          5.02989  |    0.0236087   |                 1        |                        1 | return_corr_cluster |
| rc_061                |            1 |                         1 |                  0 |                         0 |                0 |       -1.08781   |      2.62064  |                    7.18757 |         3.59461  |            3.18106  |          3.49861  |   -2           |                 0.923077 |                        1 | return_corr_cluster |
| rc_065                |            1 |                         1 |                  0 |                         0 |                0 |        0.277632  |      7.19125  |                    7.95482 |         2.81825  |            2.66855  |          2.86369  |   -0.595429    |                 0.876923 |                        1 | return_corr_cluster |
| rc_069                |            1 |                         1 |                  0 |                         0 |                0 |        1.60501   |      0.342141 |                    1.6313  |         1.56911  |            1.3571   |          1.49796  |    0.611003    |                 1        |                        1 | return_corr_cluster |
| rc_112                |            1 |                         1 |                  0 |                         0 |                0 |        2.21613   |     33.784    |                   33.784   |         4.35316  |            4.16006  |          4.34235  |    1.22135     |                 1        |                        1 | return_corr_cluster |
| rc_015                |           18 |                         0 |                 18 |                         0 |                0 |        2.55343   |    -14.2736   |                   -9.38394 |         4.01882  |            3.88459  |          4.00676  |    1.55677     |                 1        |                        0 | return_corr_cluster |

## Interpretation

- The protected W2 registry is control-clean on this pilot: no strict negative-control research-like rows, no dominance failures, and no placebo/null research candidates.
- The blocker is productivity, not pipeline safety. The post-May eligible pool is below the continuation threshold.
- The non-May rank is inverted against the stress label: the top rank decile has no post-May eligible rows while the bottom rank decile has the highest eligible rate. This is forensic evidence only; May remains forbidden for ranking or training.
- Full L1 continuation is not authorized from this result. The next valid step is either a second protected pilot only after an explicit authorization record, or a search-cell redesign focused on non-May fold productivity and May activity coverage.

## Output Files

| path                                                                              |
|:----------------------------------------------------------------------------------|
| runtime\a7p4_productivity_forensic\a7p4_cell_productivity.csv                     |
| runtime\a7p4_productivity_forensic\a7p4_decision_counts.csv                       |
| runtime\a7p4_productivity_forensic\a7p4_eligible_vs_ineligible_median_metrics.csv |
| runtime\a7p4_productivity_forensic\a7p4_feature_family_productivity.csv           |
| runtime\a7p4_productivity_forensic\a7p4_feature_operator_horizon_productivity.csv |
| runtime\a7p4_productivity_forensic\a7p4_fold_failure_summary.csv                  |
| runtime\a7p4_productivity_forensic\a7p4_horizon_productivity.csv                  |
| runtime\a7p4_productivity_forensic\a7p4_hypothesis_productivity.csv               |
| runtime\a7p4_productivity_forensic\a7p4_may_gate_candidate_flags.csv              |
| runtime\a7p4_productivity_forensic\a7p4_may_gate_failure_summary.csv              |
| runtime\a7p4_productivity_forensic\a7p4_operator_productivity.csv                 |
| runtime\a7p4_productivity_forensic\a7p4_rank_decile_post_may_alignment.csv        |
| runtime\a7p4_productivity_forensic\a7p4_reject_reason_counts.csv                  |
| runtime\a7p4_productivity_forensic\a7p4_return_corr_cluster_productivity.csv      |
| runtime\a7p4_productivity_forensic\a7p4_top_post_may_eligible_candidates.csv      |