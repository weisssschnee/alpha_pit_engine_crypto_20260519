# Crypto A7O-2 Dry Cartography Audit

- generated_at: `2026-05-20T12:49:20Z`
- decision: `HOLD_A7O2_DRY_CARTOGRAPHY`
- authorizes_l1_execution: `False`
- executes_large_backtest: `False`

## Dry Summary

| metric                           |          value | pass   |
|:---------------------------------|---------------:|:-------|
| target_cells                     |   1024         | True   |
| total_dry_generated              | 524288         | True   |
| active_cells                     |   1024         | True   |
| unique_expr_ratio                |      0.525484  | False  |
| simplified_unique_ratio          |      0.525484  | False  |
| zero_activity_predicted_share    |      0         | True   |
| unsupported_operator_count       |      0         | True   |
| may_dependency_count             |      0         | True   |
| liquidity_volatility_motif_share |      0.0798912 | True   |
| feature_family_combo_count       |    384         | True   |
| operator_motif_count             |     24         | True   |
| horizon_class_count              |     10         | True   |

## Static Funnel

| stage                      |   count |
|:---------------------------|--------:|
| dry_generated              |  524288 |
| static_valid               |  524288 |
| may_dependency_free        |  524288 |
| predicted_nonzero_activity |  524288 |


L1 remains blocked until explicit review despite L0/L1 kernel results. This run does not authorize alpha proof, shadow, paper, or live execution.