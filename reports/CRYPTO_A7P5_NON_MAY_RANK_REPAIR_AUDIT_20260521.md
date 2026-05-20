# Crypto A7P-5 Non-May Rank Repair Audit

- generated_at: `2026-05-20T18:48:21Z`
- source_checkpoint: `A7P3_W2PILOT`
- decision: `HOLD_A7P5_NON_MAY_STRESS_ANALOG_WEAK`
- executes_search: `False`
- executes_replay: `False`
- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`
- blockers: `['stress_analog_top_decile_not_better_than_original', 'stress_analog_top_decile_below_overall_rate']`

## Purpose

A7P-5 tests a non-May stress-analog rank computed only from difficult validation/recent fold metrics. May is used only after ranking for attribution.

## Metrics

|   overall_post_may_eligible_rate |   original_top_decile_post_may_eligible_rate |   stress_analog_top_decile_post_may_eligible_rate |
|---------------------------------:|---------------------------------------------:|--------------------------------------------------:|
|                        0.0677083 |                                            0 |                                                 0 |

## Original Rank Deciles

|   rank_decile |   rows |   post_may_eligible_count |   may_vetoed_count |   median_score |   median_raw_may |   median_residual_funding_may |   median_raw_recent |   post_may_eligible_rate | score_name       |
|--------------:|-------:|--------------------------:|-------------------:|---------------:|-----------------:|------------------------------:|--------------------:|-------------------------:|:-----------------|
|             1 |     20 |                         0 |                 20 |       2.99715  |        -14.6554  |                      -9.95385 |            4.53641  |                0         | pilot_rank_score |
|             2 |     19 |                         0 |                 19 |       2.81375  |        -11.8702  |                      -8.14215 |            4.51238  |                0         | pilot_rank_score |
|             3 |     19 |                         1 |                 18 |       2.21613  |        -10.311   |                      -6.67708 |            3.6242   |                0.0526316 | pilot_rank_score |
|             4 |     19 |                         0 |                 19 |       1.84899  |         -8.09187 |                      -4.74606 |            3.38938  |                0         | pilot_rank_score |
|             5 |     19 |                         1 |                 18 |       1.39085  |         -7.4523  |                      -4.92062 |            3.00106  |                0.0526316 | pilot_rank_score |
|             6 |     19 |                         2 |                 17 |       1.01599  |          0       |                       0       |            1.82796  |                0.105263  | pilot_rank_score |
|             7 |     19 |                         0 |                 19 |       0.797878 |          0       |                       0       |            1.34329  |                0         | pilot_rank_score |
|             8 |     19 |                         0 |                 18 |       0.513277 |          0       |                       0       |            1.39628  |                0         | pilot_rank_score |
|             9 |     19 |                         4 |                 11 |       0.153156 |         -1.37647 |                       0       |            0.958276 |                0.210526  | pilot_rank_score |
|            10 |     20 |                         5 |                  7 |      -1.00772  |          0       |                       0       |            0.976025 |                0.25      | pilot_rank_score |

## Stress-Analog Rank Deciles

|   rank_decile |   rows |   post_may_eligible_count |   may_vetoed_count |   median_score |   median_raw_may |   median_residual_funding_may |   median_raw_recent |   post_may_eligible_rate | score_name          |
|--------------:|-------:|--------------------------:|-------------------:|---------------:|-----------------:|------------------------------:|--------------------:|-------------------------:|:--------------------|
|             1 |     20 |                         0 |                 20 |      4.23129   |        -14.1441  |                     -9.27654  |             5.35577 |                0         | stress_analog_score |
|             2 |     19 |                         2 |                 16 |      3.19496   |         -8.02636 |                     -2.0472   |             3.18225 |                0.105263  | stress_analog_score |
|             3 |     19 |                         0 |                 17 |      2.74253   |        -12.5874  |                     -7.36464  |             4.18606 |                0         | stress_analog_score |
|             4 |     19 |                         0 |                 19 |      2.10246   |        -14.1867  |                    -10.4495   |             2.78587 |                0         | stress_analog_score |
|             5 |     19 |                         0 |                 19 |      1.70996   |         -8.44374 |                     -4.05203  |             3.37621 |                0         | stress_analog_score |
|             6 |     19 |                         1 |                 18 |      1.3119    |         -3.195   |                     -0.212598 |             3.16657 |                0.0526316 | stress_analog_score |
|             7 |     19 |                         3 |                 16 |      0.98852   |         -1.20526 |                      0        |             1.74033 |                0.157895  | stress_analog_score |
|             8 |     19 |                         3 |                 16 |      0.425056  |          0       |                      0        |             2.12708 |                0.157895  | stress_analog_score |
|             9 |     19 |                         0 |                 14 |     -0.0777172 |          0       |                      0        |             1.1836  |                0         | stress_analog_score |
|            10 |     20 |                         4 |                 11 |     -0.646382  |         -3.77884 |                     -1.14141  |             1.88282 |                0.2       | stress_analog_score |

## Interpretation

This audit does not authorize new search. A PASS only means a non-May stress-analog score has directional information worth converting into a future objective contract. A HOLD means rank repair needs a different non-May proxy or the W2 registry remains too weak.