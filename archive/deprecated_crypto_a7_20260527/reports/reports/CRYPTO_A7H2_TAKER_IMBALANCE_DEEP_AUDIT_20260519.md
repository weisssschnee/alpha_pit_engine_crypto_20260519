# Crypto A7H-2 Taker Imbalance Deep Audit

- generated_at: `2026-05-19T15:10:54Z`
- decision: `HOLD_A7H2_TAKER_IMBALANCE_UNRESOLVED`
- evidence_level: `deep_candidate_audit_only_not_alpha_proof`
- blockers: `['standalone_raw_10bp_negative_recent_or_may', 'standalone_recent_symbol_contribution_weak', 'standalone_may_symbol_contribution_weak']`
- warnings: `['minor_taker_field_missing_rows', 'raw_20bp_recent_not_positive', 'raw_20bp_may_not_positive']`

## Candidate

- candidate_id: `a7h_flow_rank_taker_imbalance_h6`
- expression: `Rank(taker_imbalance)`
- horizon: `6`

## Timing Contract

- feature_before_execution_violations: `0`
- taker_field_missing_rows: `12`
- min_feature_to_execution_ms: `1.0`

## Split Metrics

| series | split | ann mean | DD | hit rate | turnover |
|---|---|---:|---:|---:|---:|
| `raw_10bp` | `train_2024` | -3.5357 | -0.9736 | 0.432 | 0.3632 |
| `raw_10bp` | `validation_2025H1` | -3.0673 | -0.7825 | 0.429 | 0.3670 |
| `raw_10bp` | `recent_oos_2025H2_2026Apr` | -3.3143 | -0.9363 | 0.409 | 0.3554 |
| `raw_10bp` | `fresh_forward_2026May` | -2.9743 | -0.1272 | 0.362 | 0.3548 |
| `raw_20bp` | `train_2024` | -6.7177 | -0.9989 | 0.369 | 0.3632 |
| `raw_20bp` | `validation_2025H1` | -6.2823 | -0.9551 | 0.365 | 0.3670 |
| `raw_20bp` | `recent_oos_2025H2_2026Apr` | -6.4276 | -0.9952 | 0.322 | 0.3554 |
| `raw_20bp` | `fresh_forward_2026May` | -6.0824 | -0.2392 | 0.255 | 0.3548 |
| `residual_vs_funding_10bp` | `train_2024` | 0.0000 | -0.4615 | 0.513 | 0.3632 |
| `residual_vs_funding_10bp` | `validation_2025H1` | 0.4687 | -0.1679 | 0.507 | 0.3670 |
| `residual_vs_funding_10bp` | `recent_oos_2025H2_2026Apr` | 0.2214 | -0.2711 | 0.516 | 0.3554 |
| `residual_vs_funding_10bp` | `fresh_forward_2026May` | 0.5604 | -0.0300 | 0.513 | 0.3548 |
| `residual_vs_core4_10bp` | `train_2024` | 0.0000 | -0.4611 | 0.514 | 0.3632 |
| `residual_vs_core4_10bp` | `validation_2025H1` | 0.4733 | -0.1673 | 0.507 | 0.3670 |
| `residual_vs_core4_10bp` | `recent_oos_2025H2_2026Apr` | 0.2233 | -0.2714 | 0.515 | 0.3554 |
| `residual_vs_core4_10bp` | `fresh_forward_2026May` | 0.5425 | -0.0302 | 0.510 | 0.3548 |

## Placebo / Wrong-Lag

| mode | split | ann mean | DD | hit rate |
|---|---|---:|---:|---:|
| `original` | `validation_2025H1` | -3.0673 | -0.7825 | 0.429 |
| `original` | `recent_oos_2025H2_2026Apr` | -3.3143 | -0.9363 | 0.409 |
| `original` | `fresh_forward_2026May` | -2.9743 | -0.1272 | 0.362 |
| `sign_flip` | `validation_2025H1` | -3.3626 | -0.8128 | 0.432 |
| `sign_flip` | `recent_oos_2025H2_2026Apr` | -2.9122 | -0.9137 | 0.403 |
| `sign_flip` | `fresh_forward_2026May` | -3.2419 | -0.1520 | 0.390 |
| `wrong_lag_stale_24h` | `validation_2025H1` | -3.0158 | -0.7776 | 0.435 |
| `wrong_lag_stale_24h` | `recent_oos_2025H2_2026Apr` | -3.1525 | -0.9284 | 0.397 |
| `wrong_lag_stale_24h` | `fresh_forward_2026May` | -3.9614 | -0.1709 | 0.372 |
| `wrong_lag_future_24h_diagnostic` | `validation_2025H1` | -4.2940 | -0.8814 | 0.401 |
| `wrong_lag_future_24h_diagnostic` | `recent_oos_2025H2_2026Apr` | -3.4396 | -0.9429 | 0.397 |
| `wrong_lag_future_24h_diagnostic` | `fresh_forward_2026May` | -4.8565 | -0.1976 | 0.349 |
| `row_shuffle` | `validation_2025H1` | -3.3799 | -0.8134 | 0.423 |
| `row_shuffle` | `recent_oos_2025H2_2026Apr` | -3.3814 | -0.9399 | 0.392 |
| `row_shuffle` | `fresh_forward_2026May` | -2.8444 | -0.1215 | 0.395 |
| `time_shuffle` | `validation_2025H1` | -4.1087 | -0.8694 | 0.413 |
| `time_shuffle` | `recent_oos_2025H2_2026Apr` | -3.4854 | -0.9451 | 0.401 |
| `time_shuffle` | `fresh_forward_2026May` | -3.7430 | -0.1587 | 0.337 |

## Stability Summary

- month_loo_positive_rate: `1.0`
- month_loo_min_ann: `0.12288744454923069`
- recent_symbol_positive_rate: `0.0`
- may_symbol_positive_rate: `0.3333333333333333`

## Decision Boundary

- PASS here means the single taker-imbalance candidate deserves a future locked-forward/replay design audit as an alpha candidate.
- If raw standalone performance is broadly negative while only residual performance is positive, classify it as a hedge/overlay clue, not an alpha candidate.
- It does not authorize generator bakeoff, alpha shadow proof, paper, live, or production claims.
