# Crypto A7O-2C3 Field-Pair Semantic Repair Audit

- generated_at: `2026-05-20T13:44:13Z`
- decision: `HOLD_A7O2C3_SEMANTIC_OR_HORIZON_FEASIBILITY_FAIL`
- executes_search: `False`
- executes_replay: `False`
- executes_large_backtest: `False`
- authorizes_l1_execution: `False`
- ready_for_a7o2d_authorization_record: `False`
- blockers: `['raw_unique_expr_ratio', 'effective_unique_ratio_after_horizon_bucketing']`

## Effective Uniqueness

| metric                                         |    value |   threshold | pass   |
|:-----------------------------------------------|---------:|------------:|:-------|
| raw_unique_expr_ratio                          | 0.850245 |        0.9  | False  |
| effective_unique_ratio_after_horizon_bucketing | 0.814871 |        0.85 | False  |
| simplified_effective_unique_ratio_after_bucket | 0.814871 |        0.75 | True   |

## Horizon Parameter Distribution

| metric                           |   value |   threshold | pass   |
|:---------------------------------|--------:|------------:|:-------|
| max_window                       |      97 |         144 | True   |
| p95_window                       |      96 |          96 | True   |
| p50_window                       |      36 |             | True   |
| horizon_bucket_count             |       6 |           6 | True   |
| continuous_window_inflation_flag |      23 |         144 | True   |

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
| F0_validation_2025H1       | 4296 |                    0.977421 |                    0.977654 |                       0.99162  |                   0 | True   |
| F0_recent_2025H2_2026Apr   | 7248 |                    0.986617 |                    0.986755 |                       0.995033 |                   0 | True   |
| F1_high_realized_vol       | 3463 |                    0.97199  |                    0.972278 |                       0.989604 |                   0 | True   |
| F2_low_liquidity           | 3463 |                    0.97199  |                    0.972278 |                       0.989604 |                   0 | True   |
| F3_high_liquidity_high_vol | 3341 |                    0.970967 |                    0.971266 |                       0.989225 |                   0 | True   |
| F4_basis_dislocation       | 3463 |                    0.97199  |                    0.972278 |                       0.989604 |                   0 | True   |
| F5_funding_neutral         | 5775 |                    0.983203 |                    0.983377 |                       0.993766 |                   0 | True   |
| F6_cross_symbol_dispersion | 3463 |                    0.97199  |                    0.972278 |                       0.989604 |                   0 | True   |
| F7_trend_reversal          | 4178 |                    0.976783 |                    0.977022 |                       0.991383 |                   0 | True   |
| F8_low_vol_high_liquidity  |  478 |                    0.797071 |                    0.799163 |                       0.924686 |                   0 | True   |
| F9_liquidity_shock         | 2886 |                    0.966389 |                    0.966736 |                       0.987526 |                   0 | True   |
| F10_volatility_compression | 4041 |                    0.975996 |                    0.976244 |                       0.991091 |                   0 | True   |
| F11_cross_symbol_crowding  | 3463 |                    0.97199  |                    0.972278 |                       0.989604 |                   0 | True   |

## Decision

A7O2C3 does not authorize L1. If it passes, a separate A7O-2D authorization record is still required.