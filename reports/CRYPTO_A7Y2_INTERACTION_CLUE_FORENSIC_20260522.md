# Crypto A7Y-2 Interaction Clue Forensic

- generated_at: `2026-05-22T09:35:14Z`
- decision: `HOLD_A7Y2_INTERACTION_CLUES_NOT_ROBUST`
- executes_search: `False`
- executes_replay: `forensic_on_a7y1_clues_only`
- alpha proof / expanded replay / full search / shadow / paper / live: `NOT_AUTHORIZED`

## Scope

A7Y-2 audits the four A7Y-1 interaction clues. It does not generate new formulas and keeps core12 and core3 lanes separate.

## Robustness Summary

| candidate_id                                                         | lane              |   horizon |   validation_net10 |   validation_net20 |   recent_net10 |   recent_net20 |   may_net10 |   lag1_recent_net10 |   recent_symbol_loo_positive_rate |   recent_min_symbol_loo_net10 |   recent_month_loo_positive_rate |   recent_min_month_loo_net10 |   recent_control_positive_count | passes_20bps   | passes_lag1   | passes_symbol_loo   | passes_month_loo   | passes_controls   | passes_may   |
|:---------------------------------------------------------------------|:------------------|----------:|-------------------:|-------------------:|---------------:|---------------:|------------:|--------------------:|----------------------------------:|------------------------------:|---------------------------------:|-----------------------------:|--------------------------------:|:---------------|:--------------|:--------------------|:-------------------|:------------------|:-------------|
| a7y1_core12_metrics_F1_oi_state_interaction_24_f0b406c8bad6          | core12_metrics    |        24 |           2.56756  |           1.92823  |       1.59631  |      0.620982  |    0.156709 |            1.29537  |                          0.916667 |                     -0.568083 |                              0.9 |                    -0.451854 |                               0 | True           | True          | False               | False              | True              | True         |
| a7y1_core3_agg_metrics_F3_metrics_crowding_x_aggflow_24_a1460b56acfb | core3_agg_metrics |        24 |           1.16566  |           0.700655 |       0.651874 |      0.0123744 |    0.671452 |            0.463562 |                          0.666667 |                     -1.01501  |                              0.8 |                    -2.5082   |                               0 | True           | True          | False               | False              | True              | True         |
| a7y1_core3_agg_metrics_F4_oi_x_aggflow_24_1c5043146de8               | core3_agg_metrics |        24 |           0.61974  |          -0.19676  |       1.82249  |      0.521494  |    1.0286   |            1.55342  |                          0.666667 |                     -1.31264  |                              1   |                     0.539684 |                               0 | False          | True          | False               | True               | True              | True         |
| a7y1_core3_agg_metrics_F4_oi_x_aggflow_24_348654b50bf4               | core3_agg_metrics |        24 |           0.417551 |          -0.419949 |       1.69428  |      0.367777  |    1.22361  |            1.49084  |                          0.666667 |                     -1.34291  |                              1   |                     0.289388 |                               0 | False          | True          | False               | True               | True              | True         |

## Split Metrics

| candidate_id                                                         | lane              | production_family             | expression                                                                                          |   horizon | split                     |   orientation |     train_ic |   active_hours |     net10 |      net20 |   lag1_net10 |   turnover_mean |   gross_exposure_mean |
|:---------------------------------------------------------------------|:------------------|:------------------------------|:----------------------------------------------------------------------------------------------------|----------:|:--------------------------|--------------:|-------------:|---------------:|----------:|-----------:|-------------:|----------------:|----------------------:|
| a7y1_core12_metrics_F1_oi_state_interaction_24_f0b406c8bad6          | core12_metrics    | F1_oi_state_interaction       | Mul(ZScore(open_interest_change_24h),Rank(realized_vol_24))                                         |        24 | train_2024                |             1 |   0.00181213 |           8748 | -2.88188  | -4.15155   |    -3.48027  |       0.144543  |              0.995902 |
| a7y1_core12_metrics_F1_oi_state_interaction_24_f0b406c8bad6          | core12_metrics    | F1_oi_state_interaction       | Mul(ZScore(open_interest_change_24h),Rank(realized_vol_24))                                         |        24 | validation_2025H1         |             1 |   0.00181213 |           4343 |  2.56756  |  1.92823   |     2.68891  |       0.147176  |              0.99977  |
| a7y1_core12_metrics_F1_oi_state_interaction_24_f0b406c8bad6          | core12_metrics    | F1_oi_state_interaction       | Mul(ZScore(open_interest_change_24h),Rank(realized_vol_24))                                         |        24 | recent_oos_2025H2_2026Apr |             1 |   0.00181213 |           7292 |  1.59631  |  0.620982  |     1.29537  |       0.133681  |              0.999452 |
| a7y1_core12_metrics_F1_oi_state_interaction_24_f0b406c8bad6          | core12_metrics    | F1_oi_state_interaction       | Mul(ZScore(open_interest_change_24h),Rank(realized_vol_24))                                         |        24 | fresh_may_2026            |             1 |   0.00181213 |            480 |  0.156709 |  0.0967094 |     0.130668 |       0.118812  |              0.950495 |
| a7y1_core3_agg_metrics_F3_metrics_crowding_x_aggflow_24_a1460b56acfb | core3_agg_metrics | F3_metrics_crowding_x_aggflow | Mul(Neg(ZScore(global_long_short_account_ratio_zscore_168h)),Rank(agg_flow_imbalance_notional_24h)) |        24 | train_2024                |             1 | nan          |           8751 | 11.3768   | 10.6048    |    11.0219   |       0.0878871 |              0.996243 |
| a7y1_core3_agg_metrics_F3_metrics_crowding_x_aggflow_24_a1460b56acfb | core3_agg_metrics | F3_metrics_crowding_x_aggflow | Mul(Neg(ZScore(global_long_short_account_ratio_zscore_168h)),Rank(agg_flow_imbalance_notional_24h)) |        24 | validation_2025H1         |             1 | nan          |           4344 |  1.16566  |  0.700655  |     1.08583  |       0.107044  |              1        |
| a7y1_core3_agg_metrics_F3_metrics_crowding_x_aggflow_24_a1460b56acfb | core3_agg_metrics | F3_metrics_crowding_x_aggflow | Mul(Neg(ZScore(global_long_short_account_ratio_zscore_168h)),Rank(agg_flow_imbalance_notional_24h)) |        24 | recent_oos_2025H2_2026Apr |             1 | nan          |           7294 |  0.651874 |  0.0123744 |     0.463562 |       0.0876508 |              0.999726 |
| a7y1_core3_agg_metrics_F3_metrics_crowding_x_aggflow_24_a1460b56acfb | core3_agg_metrics | F3_metrics_crowding_x_aggflow | Mul(Neg(ZScore(global_long_short_account_ratio_zscore_168h)),Rank(agg_flow_imbalance_notional_24h)) |        24 | fresh_may_2026            |             1 | nan          |            480 |  0.671452 |  0.641452  |     0.645186 |       0.0594059 |              0.950495 |
| a7y1_core3_agg_metrics_F4_oi_x_aggflow_24_348654b50bf4               | core3_agg_metrics | F4_oi_x_aggflow               | Mul(ZScore(open_interest_change_24h),Rank(agg_cross_symbol_signed_flow_share))                      |        24 | train_2024                |             1 | nan          |           8745 |  2.9586   |  1.3056    |     2.12195  |       0.188183  |              0.99556  |
| a7y1_core3_agg_metrics_F4_oi_x_aggflow_24_348654b50bf4               | core3_agg_metrics | F4_oi_x_aggflow               | Mul(ZScore(open_interest_change_24h),Rank(agg_cross_symbol_signed_flow_share))                      |        24 | validation_2025H1         |             1 | nan          |           4342 |  0.417551 | -0.419949  |     0.367624 |       0.192795  |              0.99954  |
| a7y1_core3_agg_metrics_F4_oi_x_aggflow_24_348654b50bf4               | core3_agg_metrics | F4_oi_x_aggflow               | Mul(ZScore(open_interest_change_24h),Rank(agg_cross_symbol_signed_flow_share))                      |        24 | recent_oos_2025H2_2026Apr |             1 | nan          |           7292 |  1.69428  |  0.367777  |     1.49084  |       0.181812  |              0.999452 |
| a7y1_core3_agg_metrics_F4_oi_x_aggflow_24_348654b50bf4               | core3_agg_metrics | F4_oi_x_aggflow               | Mul(ZScore(open_interest_change_24h),Rank(agg_cross_symbol_signed_flow_share))                      |        24 | fresh_may_2026            |             1 | nan          |            480 |  1.22361  |  1.15211   |     1.20445  |       0.141584  |              0.950495 |
| a7y1_core3_agg_metrics_F4_oi_x_aggflow_24_1c5043146de8               | core3_agg_metrics | F4_oi_x_aggflow               | Mul(ZScore(open_interest_change_24h),Rank(agg_signed_flow_z_24h))                                   |        24 | train_2024                |             1 | nan          |           8745 |  3.30293  |  1.68543   |     2.53147  |       0.184142  |              0.99556  |
| a7y1_core3_agg_metrics_F4_oi_x_aggflow_24_1c5043146de8               | core3_agg_metrics | F4_oi_x_aggflow               | Mul(ZScore(open_interest_change_24h),Rank(agg_signed_flow_z_24h))                                   |        24 | validation_2025H1         |             1 | nan          |           4342 |  0.61974  | -0.19676   |     0.714952 |       0.18796   |              0.99954  |
| a7y1_core3_agg_metrics_F4_oi_x_aggflow_24_1c5043146de8               | core3_agg_metrics | F4_oi_x_aggflow               | Mul(ZScore(open_interest_change_24h),Rank(agg_signed_flow_z_24h))                                   |        24 | recent_oos_2025H2_2026Apr |             1 | nan          |           7292 |  1.82249  |  0.521494  |     1.55342  |       0.178317  |              0.999452 |
| a7y1_core3_agg_metrics_F4_oi_x_aggflow_24_1c5043146de8               | core3_agg_metrics | F4_oi_x_aggflow               | Mul(ZScore(open_interest_change_24h),Rank(agg_signed_flow_z_24h))                                   |        24 | fresh_may_2026            |             1 | nan          |            480 |  1.0286   |  0.960598  |     1.00224  |       0.134653  |              0.950495 |

## Recent Symbol Contribution

| candidate_id                                                         | lane              |   horizon | split                     | symbol   |      net10 |   active_hours |
|:---------------------------------------------------------------------|:------------------|----------:|:--------------------------|:---------|-----------:|---------------:|
| a7y1_core12_metrics_F1_oi_state_interaction_24_f0b406c8bad6          | core12_metrics    |        24 | recent_oos_2025H2_2026Apr | DOGEUSDT |  2.1644    |           4870 |
| a7y1_core12_metrics_F1_oi_state_interaction_24_f0b406c8bad6          | core12_metrics    |        24 | recent_oos_2025H2_2026Apr | BNBUSDT  |  1.49438   |           1584 |
| a7y1_core12_metrics_F1_oi_state_interaction_24_f0b406c8bad6          | core12_metrics    |        24 | recent_oos_2025H2_2026Apr | ADAUSDT  |  1.35616   |           4784 |
| a7y1_core12_metrics_F1_oi_state_interaction_24_f0b406c8bad6          | core12_metrics    |        24 | recent_oos_2025H2_2026Apr | XRPUSDT  |  1.09296   |           3381 |
| a7y1_core12_metrics_F1_oi_state_interaction_24_f0b406c8bad6          | core12_metrics    |        24 | recent_oos_2025H2_2026Apr | SUIUSDT  |  0.376619  |           5009 |
| a7y1_core12_metrics_F1_oi_state_interaction_24_f0b406c8bad6          | core12_metrics    |        24 | recent_oos_2025H2_2026Apr | LTCUSDT  |  0.192544  |           3238 |
| a7y1_core12_metrics_F1_oi_state_interaction_24_f0b406c8bad6          | core12_metrics    |        24 | recent_oos_2025H2_2026Apr | BCHUSDT  | -0.343556  |           3156 |
| a7y1_core12_metrics_F1_oi_state_interaction_24_f0b406c8bad6          | core12_metrics    |        24 | recent_oos_2025H2_2026Apr | AVAXUSDT | -0.48023   |           4958 |
| a7y1_core12_metrics_F1_oi_state_interaction_24_f0b406c8bad6          | core12_metrics    |        24 | recent_oos_2025H2_2026Apr | LINKUSDT | -0.943201  |           4557 |
| a7y1_core12_metrics_F1_oi_state_interaction_24_f0b406c8bad6          | core12_metrics    |        24 | recent_oos_2025H2_2026Apr | ETHUSDT  | -1.04722   |           3217 |
| a7y1_core12_metrics_F1_oi_state_interaction_24_f0b406c8bad6          | core12_metrics    |        24 | recent_oos_2025H2_2026Apr | SOLUSDT  | -1.06503   |           4145 |
| a7y1_core12_metrics_F1_oi_state_interaction_24_f0b406c8bad6          | core12_metrics    |        24 | recent_oos_2025H2_2026Apr | BTCUSDT  | -1.20151   |            853 |
| a7y1_core3_agg_metrics_F3_metrics_crowding_x_aggflow_24_a1460b56acfb | core3_agg_metrics |        24 | recent_oos_2025H2_2026Apr | ETHUSDT  |  1.66689   |           5155 |
| a7y1_core3_agg_metrics_F3_metrics_crowding_x_aggflow_24_a1460b56acfb | core3_agg_metrics |        24 | recent_oos_2025H2_2026Apr | SOLUSDT  |  0.0102733 |           4734 |
| a7y1_core3_agg_metrics_F3_metrics_crowding_x_aggflow_24_a1460b56acfb | core3_agg_metrics |        24 | recent_oos_2025H2_2026Apr | BTCUSDT  | -1.02528   |           4699 |
| a7y1_core3_agg_metrics_F4_oi_x_aggflow_24_1c5043146de8               | core3_agg_metrics |        24 | recent_oos_2025H2_2026Apr | SOLUSDT  |  3.13513   |           5371 |
| a7y1_core3_agg_metrics_F4_oi_x_aggflow_24_1c5043146de8               | core3_agg_metrics |        24 | recent_oos_2025H2_2026Apr | ETHUSDT  |  0.175472  |           4822 |
| a7y1_core3_agg_metrics_F4_oi_x_aggflow_24_1c5043146de8               | core3_agg_metrics |        24 | recent_oos_2025H2_2026Apr | BTCUSDT  | -1.48811   |           4391 |
| a7y1_core3_agg_metrics_F4_oi_x_aggflow_24_348654b50bf4               | core3_agg_metrics |        24 | recent_oos_2025H2_2026Apr | SOLUSDT  |  3.03719   |           5372 |
| a7y1_core3_agg_metrics_F4_oi_x_aggflow_24_348654b50bf4               | core3_agg_metrics |        24 | recent_oos_2025H2_2026Apr | ETHUSDT  | -0.245336  |           4794 |
| a7y1_core3_agg_metrics_F4_oi_x_aggflow_24_348654b50bf4               | core3_agg_metrics |        24 | recent_oos_2025H2_2026Apr | BTCUSDT  | -1.09758   |           4418 |

## Authorization

```json
{
  "authorizes_a7y3_small_replay_review": false,
  "authorizes_alpha_proof": false,
  "authorizes_expanded_replay": false,
  "authorizes_full_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "no_interaction_clue_passes_robustness"
  ],
  "clue_count": 4,
  "decision": "HOLD_A7Y2_INTERACTION_CLUES_NOT_ROBUST",
  "executes_replay": "forensic_on_a7y1_clues_only",
  "executes_search": false,
  "generated_at": "2026-05-22T09:35:14Z",
  "required_next": [
    "If robust clues exist, run A7Y-3 small replay review only",
    "Do not combine core12 and core3 lanes into a single proof object",
    "No alpha proof or full search"
  ],
  "robust_clue_count": 0,
  "warnings": [
    "symbol_loo_weak_for_some_clues",
    "month_loo_weak_for_some_clues"
  ]
}
```
