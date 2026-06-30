# CRYPTO A7SEARCH5 Validation Pack 20260630

Generated: `2026-06-30T07:42:14Z`

## Decision

`HOLD_A7SEARCH5_CANONICAL_NOT_UNIQUE_INCREMENT`

This validates whether the A7SEARCH5 accepted OI/positioning structure has incremental evidence over single-leg and operator-ablation baselines. It is not alpha proof and does not authorize shadow, paper, or live trading.

## Counts

- queue_rows: `16`
- leaderboard_rows: `64`
- accepted_rows: `11`
- accepted_unique_blueprints: `6`
- eval_error_rows: `0`
- canonical_accepted_rows: `2`
- single_leg_accepted_rows: `0`
- operator_ablation_accepted_rows: `4`

## Group Summary

| validation_group   |   candidates |   accepted_rows |   max_recent_sortino |   max_min_oos_floor_sortino |
|:-------------------|-------------:|----------------:|---------------------:|----------------------------:|
| robustness_variant |            2 |               5 |              12.6125 |                    4.91999  |
| operator_ablation  |            6 |               4 |              18.3725 |                    5.39198  |
| canonical          |            2 |               2 |              12.6551 |                    5.39198  |
| single_leg         |            6 |               0 |              18.6599 |                    0.082274 |

## Accepted Summary

| validation_group   | blueprint_id                   |   horizon_h |   rows |   train_sortino |   validation_sortino |   test_sortino |   recent_sortino |   min_oos_floor_sortino |   stress_floor_sortino |   recent_shuffle_control_ratio |
|:-------------------|:-------------------------------|------------:|-------:|----------------:|---------------------:|---------------:|-----------------:|------------------------:|-----------------------:|-------------------------------:|
| canonical          | a7search5_vp_canonical_last    |           4 |      1 |         1.56339 |              5.71825 |        8.08573 |          10.8199 |                 5.39198 |                4.11008 |                       0.632433 |
| operator_ablation  | a7search5_vp_no_abs_denom_last |           4 |      1 |         1.56339 |              5.71825 |        8.08573 |          10.8199 |                 5.39198 |                4.11008 |                       0.761485 |
| operator_ablation  | a7search5_vp_no_abs_denom_mean |           4 |      1 |         1.60181 |              5.78371 |        8.10643 |          10.7932 |                 5.28175 |                4.13497 |                       0.639774 |
| robustness_variant | a7search5_vp_smooth_168_last   |           4 |      1 |         1.65877 |              5.21338 |        8.19799 |          10.573  |                 4.91999 |                4.14603 |                       0.618273 |
| operator_ablation  | a7search5_vp_no_abs_denom_last |           8 |      1 |         1.60807 |              6.11791 |        7.27067 |          11.5445 |                 4.06419 |                3.26946 |                       0.273005 |
| canonical          | a7search5_vp_canonical_mean    |           8 |      1 |         1.65894 |              6.19733 |        7.2882  |          11.5284 |                 4.04352 |                3.2753  |                       0.433069 |
| operator_ablation  | a7search5_vp_no_abs_denom_mean |           8 |      1 |         1.65894 |              6.19733 |        7.2882  |          11.5284 |                 4.04352 |                3.2753  |                       0.260499 |
| robustness_variant | a7search5_vp_smooth_168_last   |           8 |      1 |         1.71527 |              5.61395 |        7.47411 |          11.3586 |                 3.59041 |                3.31644 |                       0.455478 |
| robustness_variant | a7search5_vp_smooth_168_mean   |           8 |      1 |         1.71295 |              5.60719 |        7.47591 |          11.3585 |                 3.58491 |                3.31146 |                       0.270447 |
| robustness_variant | a7search5_vp_smooth_168_last   |          24 |      1 |         1.51101 |              8.09632 |       11.9547  |          12.6125 |                 2.51955 |                1.51283 |                       0.179989 |
| robustness_variant | a7search5_vp_smooth_168_mean   |          24 |      1 |         1.50959 |              8.0825  |       11.9409  |          12.5821 |                 2.50386 |                1.51722 |                       0.291877 |

## Interpretation

- Canonical structure passed, but at least one single-leg or operator-ablation baseline also passed. Treat this as non-unique information until deduped or neutralized.

## Outputs

- `queue`: `H:\AlphaFactory_CryptoData_archive\a7search5_validation_pack_20260630\a7search5_validation_ablation_queue.csv`
- `leaderboard`: `H:\AlphaFactory_CryptoData_archive\a7search5_validation_pack_20260630\reward_runtime\a7reward1_candidate_reward_leaderboard.csv`
- `accepted`: `H:\AlphaFactory_CryptoData_archive\a7search5_validation_pack_20260630\reward_runtime\a7reward1_accepted_for_next_search.csv`
- `rejections`: `H:\AlphaFactory_CryptoData_archive\a7search5_validation_pack_20260630\reward_runtime\a7reward1_validation_gate_rejections.csv`
- `errors`: `H:\AlphaFactory_CryptoData_archive\a7search5_validation_pack_20260630\reward_runtime\a7reward1_eval_errors.csv`
- `metrics`: `H:\AlphaFactory_CryptoData_archive\a7search5_validation_pack_20260630\reward_runtime\a7reward1_split_reward_metrics.csv`
- `accepted_summary`: `H:\AlphaFactory_CryptoData_archive\a7search5_validation_pack_20260630\a7search5_validation_accepted_summary.csv`
- `group_summary`: `H:\AlphaFactory_CryptoData_archive\a7search5_validation_pack_20260630\a7search5_validation_group_summary.csv`
- `manifest`: `H:\AlphaFactory_CryptoData_archive\a7search5_validation_pack_20260630\a7search5_validation_manifest.json`
