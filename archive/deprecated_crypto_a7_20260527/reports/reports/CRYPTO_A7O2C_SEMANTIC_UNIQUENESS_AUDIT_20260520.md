# Crypto A7O-2C Semantic Uniqueness Audit

- generated_at: `2026-05-20T13:18:48Z`
- decision: `HOLD_A7O2C_SEMANTIC_OR_HORIZON_FEASIBILITY_FAIL`
- executes_search: `False`
- executes_replay: `False`
- executes_large_backtest: `False`
- authorizes_l1_execution: `False`
- blockers: `['raw_unique_expr_ratio', 'effective_unique_ratio_after_horizon_bucketing', 'simplified_effective_unique_ratio_after_bucket', 'max_window', 'p95_window', 'continuous_window_inflation_flag', 'F8_low_vol_high_liquidity_p05_effective_sample_rate']`

## Effective Uniqueness

| metric                                         |    value |   threshold | pass   |
|:-----------------------------------------------|---------:|------------:|:-------|
| raw_unique_expr_ratio                          | 0.871429 |        0.9  | False  |
| effective_unique_ratio_after_horizon_bucketing | 0.307409 |        0.85 | False  |
| simplified_effective_unique_ratio_after_bucket | 0.307409 |        0.75 | False  |

## Horizon Parameter Distribution

| metric                           |   value |   threshold | pass   |
|:---------------------------------|--------:|------------:|:-------|
| max_window                       |    1000 |         144 | False  |
| p95_window                       |     937 |          96 | False  |
| p50_window                       |     454 |             | True   |
| horizon_bucket_count             |       7 |           6 | True   |
| continuous_window_inflation_flag |     652 |         144 | False  |

## Economic Motif Uniqueness

| metric                                           |        value |   threshold | pass   |
|:-------------------------------------------------|-------------:|------------:|:-------|
| economic_cell_unique_ratio                       |  1           |        0.8  | True   |
| top_economic_motif_share                         |  0.000976562 |        0.1  | True   |
| top_feature_family_operator_horizon_triple_share |  0.00390625  |        0.08 | True   |
| feature_family_set_count                         | 16           |       16    | True   |
| operator_motif_count                             | 24           |       24    | True   |
| horizon_class_count                              | 10           |       10    | True   |

## Fold Coverage Feasibility

| fold_id                    |    n |   min_effective_sample_rate |   p05_effective_sample_rate |   median_effective_sample_rate |   share_below_60pct | pass   |
|:---------------------------|-----:|----------------------------:|----------------------------:|-------------------------------:|--------------------:|:-------|
| F0_validation_2025H1       | 4296 |                    0.767225 |                    0.78189  |                      0.89432   |            0        | True   |
| F0_recent_2025H2_2026Apr   | 7248 |                    0.862031 |                    0.870723 |                      0.937362  |            0        | True   |
| F1_high_realized_vol       | 3463 |                    0.711233 |                    0.729425 |                      0.8689    |            0        | True   |
| F2_low_liquidity           | 3463 |                    0.711233 |                    0.729425 |                      0.8689    |            0        | True   |
| F3_high_liquidity_high_vol | 3341 |                    0.700688 |                    0.719545 |                      0.864113  |            0        | True   |
| F4_basis_dislocation       | 3463 |                    0.711233 |                    0.729425 |                      0.8689    |            0        | True   |
| F5_funding_neutral         | 5775 |                    0.82684  |                    0.837749 |                      0.921385  |            0        | True   |
| F6_cross_symbol_dispersion | 3463 |                    0.711233 |                    0.729425 |                      0.8689    |            0        | True   |
| F7_trend_reversal          | 4178 |                    0.760651 |                    0.77573  |                      0.891336  |            0        | True   |
| F8_low_vol_high_liquidity  |  478 |                    0        |                    0        |                      0.0502092 |            0.839634 | False  |
| F9_liquidity_shock         | 2886 |                    0.6535   |                    0.675329 |                      0.842689  |            0        | True   |
| F10_volatility_compression | 4041 |                    0.752537 |                    0.768127 |                      0.887652  |            0        | True   |
| F11_cross_symbol_crowding  | 3463 |                    0.711233 |                    0.729425 |                      0.8689    |            0        | True   |

## Decision

A7O-L1 remains unauthorized unless A7O-2C passes and a separate A7O-2D authorization record is written.