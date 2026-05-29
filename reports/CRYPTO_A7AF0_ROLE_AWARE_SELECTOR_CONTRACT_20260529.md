# CRYPTO A7AF-0 ROLE-AWARE SELECTOR CONTRACT

Generated: 2026-05-29T08:17:56Z

## Decision

`PASS_A7AF0_ROLE_AWARE_SELECTOR_CONTRACT_READY_FOR_A7AF1`

A7AF-0 rewrites selector policy after A7AE label adequacy review. It separates ordinary alpha, neutralized alpha diagnostics, and downside/risk-defense queues. It does not generate formulas, search, train, or authorize proof.

## Manifest

```json
{
  "authorizes_a7af1_role_aware_selector_dryrun": true,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7AF0_ROLE_AWARE_SELECTOR_CONTRACT_READY_FOR_A7AF1",
  "executes_contract_only": true,
  "executes_formula_generation": false,
  "executes_search": false,
  "executes_selector_dryrun": false,
  "executes_training": false,
  "generated_at": "2026-05-29T08:17:56Z",
  "seed_field_count": 14,
  "selector_tier_count": 3,
  "source_a7ae2_decision": "PASS_A7AE2_LABEL_ADEQUACY_ROLES_READY_FOR_SELECTOR_REWRITE_REVIEW",
  "stage": "A7AF-0",
  "uses_may": false
}
```

## Selector Tiers

| selector_tier                    | feature_role                         | allowed_labels                                                                                                                                        | allowed_next_use                           | queue_cap   | requires                                                                              |
|:---------------------------------|:-------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------|:-------------------------------------------|:------------|:--------------------------------------------------------------------------------------|
| T0_raw_relative_alpha            | raw_relative_signal_candidate        | L0_raw_forward_return\|L1_cross_sectional_relative_return\|L2_BTC_ETH_beta_residual_return\|L3_liquidity_tier_relative_return\|L5_vol_adjusted_return | ordinary_alpha_candidate_contract_only     | 6           | raw_or_relative_candidate_count_gt_0\|control_ratio_lt_1\|lag_ok\|premay_all_positive |
| T1_beta_neutral_alpha_diagnostic | beta_or_neutralized_signal_candidate | L2_BTC_ETH_beta_residual_return\|L3_liquidity_tier_relative_return\|L5_vol_adjusted_return                                                            | neutralized_alpha_diagnostic_contract_only | 8           | beta_neutral_candidate_count_gt_0\|control_ratio_lt_1\|lag_ok\|premay_all_positive    |
| T2_downside_risk_defense         | downside_avoidance_signal_candidate  | L6_downside_avoidance                                                                                                                                 | risk_defense_downside_contract_only        | 10          | downside_candidate_count_gt_0\|control_ratio_lt_1\|lag_ok\|premay_all_positive        |

## Score Features

| score_feature            | definition                                                     |
|:-------------------------|:---------------------------------------------------------------|
| candidate_role_priority  | T0 > T1 > T2 for ordinary alpha; T2 separated from alpha queue |
| premay_split_consistency | validation/test/recent all oriented positive                   |
| control_margin           | 1 - max wrong-lag/stale/random control ratio                   |
| one_bar_lag_survival     | recent one-bar-lag oriented spread survives                    |
| nonoverlap_robust_tstat  | minimum oriented pre-May non-overlap tstat                     |
| field_family_diversity   | cap per field family inside each tier                          |

## Hard Gates

| gate                               | rule                                                                              |
|:-----------------------------------|:----------------------------------------------------------------------------------|
| seed_field_must_be_in_a7ae2_policy | field_name in a7ae2_selector_seed_policy.csv                                      |
| role_label_match                   | label family must match feature role tier                                         |
| control_ratio_lt_1                 | control_ratio_premay_max < 1.0                                                    |
| premay_all_positive                | validation/test/recent all oriented positive                                      |
| lag_ok                             | one_bar_lag_recent_oriented positive and >= 25pct of recent                       |
| no_may                             | May not used in selector score, threshold, mutation, generation, or authorization |
| downside_not_ordinary_alpha        | L6 downside queue cannot authorize ordinary alpha search                          |

## Role Caps

```json
{
  "max_downside_share_in_combined_review": 0.5,
  "max_per_field": 3,
  "max_per_field_family_per_tier": 4,
  "max_selected_total": 18,
  "min_beta_neutral_for_neutralized_contract": 3,
  "min_downside_for_risk_defense_contract": 4,
  "min_raw_relative_for_ordinary_alpha_contract": 2
}
```

## Allowed Seed Fields

| field_name                           | field_family              | source_family                   | feature_class         | feature_role                         | reason                                       | total_tests   | candidate_count   | raw_relative_candidate_count   | beta_neutral_candidate_count   | downside_candidate_count   | rank_candidate_count   | premay_stable_count   | control_like_count   | lag_fragile_count   | premay_unstable_count   | best_label_families                                                                                                                                   | best_horizons   | best_transforms           |
|:-------------------------------------|:--------------------------|:--------------------------------|:----------------------|:-------------------------------------|:---------------------------------------------|:--------------|:------------------|:-------------------------------|:-------------------------------|:---------------------------|:-----------------------|:----------------------|:---------------------|:--------------------|:------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------|:----------------|:--------------------------|
| mark_index_basis_bps                 | basis_premium             | mark_index_premium              | raw_source            | raw_relative_signal_candidate        | has_raw_or_cross_sectional_relative_response | 63            | 7                 | 2                              | 5                              | 0                          | 0                      | 33                    | 15                   | 11                  | 30                      | L0_raw_forward_return\|L1_cross_sectional_relative_return\|L2_BTC_ETH_beta_residual_return\|L3_liquidity_tier_relative_return\|L5_vol_adjusted_return | 1               | cs_rank\|delta_24h\|level |
| trade_return_1h                      | price_return              | derived_replay_base             | derived_rolling       | beta_or_neutralized_signal_candidate | has_beta_liquidity_or_vol_adjusted_response  | 63            | 12                | 0                              | 4                              | 4                          | 4                      | 50                    | 30                   | 8                   | 13                      | L2_BTC_ETH_beta_residual_return\|L3_liquidity_tier_relative_return\|L6_downside_avoidance\|L7_ranked_future_return                                    | 1\|4            | cs_rank\|level            |
| liquidity_rank_active_universe       | liquidity                 | trade_ohlcv                     | derived_cross_section | beta_or_neutralized_signal_candidate | has_beta_liquidity_or_vol_adjusted_response  | 63            | 2                 | 0                              | 2                              | 0                          | 0                      | 17                    | 15                   | 0                   | 46                      | L2_BTC_ETH_beta_residual_return                                                                                                                       | 4               | cs_rank\|level            |
| premium_close_bps                    | basis_premium             | derived_replay_base             | derived_rolling       | beta_or_neutralized_signal_candidate | has_beta_liquidity_or_vol_adjusted_response  | 63            | 2                 | 0                              | 1                              | 0                          | 1                      | 32                    | 28                   | 2                   | 31                      | L5_vol_adjusted_return\|L7_ranked_future_return                                                                                                       | 1               | delta_24h                 |
| oi_x_price_move_24h                  | open_interest_interaction | metrics_positioning,trade_ohlcv | derived_interaction   | downside_avoidance_signal_candidate  | has_downside_avoidance_response_only         | 63            | 4                 | 0                              | 0                              | 4                          | 0                      | 18                    | 14                   | 0                   | 45                      | L6_downside_avoidance                                                                                                                                 | 1\|4            | cs_rank\|level            |
| open_interest_last                   | open_interest             | metrics_positioning             | raw_source            | downside_avoidance_signal_candidate  | has_downside_avoidance_response_only         | 63            | 4                 | 0                              | 0                              | 4                          | 0                      | 32                    | 28                   | 0                   | 31                      | L6_downside_avoidance                                                                                                                                 | 1\|4            | cs_rank\|level            |
| trade_count                          | liquidity                 | trade_ohlcv                     | raw_source            | downside_avoidance_signal_candidate  | has_downside_avoidance_response_only         | 63            | 4                 | 0                              | 0                              | 4                          | 0                      | 21                    | 17                   | 0                   | 42                      | L6_downside_avoidance                                                                                                                                 | 1\|4            | cs_rank\|level            |
| realized_vol_24h                     | volatility                | trade_ohlcv                     | derived_rolling       | downside_avoidance_signal_candidate  | has_downside_avoidance_response_only         | 63            | 4                 | 0                              | 0                              | 2                          | 2                      | 47                    | 43                   | 0                   | 16                      | L6_downside_avoidance\|L7_ranked_future_return                                                                                                        | 1\|24           | cs_rank\|level            |
| global_long_short_account_ratio_last | positioning               | metrics_positioning             | raw_source            | downside_avoidance_signal_candidate  | has_downside_avoidance_response_only         | 63            | 2                 | 0                              | 0                              | 2                          | 0                      | 29                    | 27                   | 0                   | 34                      | L6_downside_avoidance                                                                                                                                 | 1\|4            | delta_24h                 |
| kline_taker_buy_quote_share          | taker_flow                | trade_ohlcv                     | raw_source            | downside_avoidance_signal_candidate  | has_downside_avoidance_response_only         | 63            | 2                 | 0                              | 0                              | 2                          | 0                      | 23                    | 19                   | 2                   | 40                      | L6_downside_avoidance                                                                                                                                 | 1               | cs_rank\|level            |
| top_long_short_account_ratio_last    | positioning               | metrics_positioning             | raw_source            | downside_avoidance_signal_candidate  | has_downside_avoidance_response_only         | 63            | 2                 | 0                              | 0                              | 2                          | 0                      | 16                    | 14                   | 0                   | 47                      | L6_downside_avoidance                                                                                                                                 | 1\|4            | delta_24h                 |
| realized_vol_168h                    | volatility                | trade_ohlcv                     | derived_rolling       | downside_avoidance_signal_candidate  | has_downside_avoidance_response_only         | 63            | 3                 | 0                              | 0                              | 1                          | 2                      | 31                    | 28                   | 0                   | 32                      | L6_downside_avoidance\|L7_ranked_future_return                                                                                                        | 1\|4            | cs_rank\|delta_24h\|level |
| premium_abs_168h                     | basis_premium             | mark_index_premium              | derived_rolling       | downside_avoidance_signal_candidate  | has_downside_avoidance_response_only         | 63            | 1                 | 0                              | 0                              | 1                          | 0                      | 13                    | 12                   | 0                   | 50                      | L6_downside_avoidance                                                                                                                                 | 1               | delta_24h                 |
| top_long_short_position_ratio_last   | positioning               | metrics_positioning             | raw_source            | downside_avoidance_signal_candidate  | has_downside_avoidance_response_only         | 63            | 1                 | 0                              | 0                              | 1                          | 0                      | 20                    | 19                   | 0                   | 43                      | L6_downside_avoidance                                                                                                                                 | 1               | delta_24h                 |

## Boundary

```text
A7AF-0 only authorizes A7AF-1 role-aware selector dryrun.
Formula search remains not authorized.
Downside/risk-defense response must not be treated as ordinary alpha.
May is not used.
```
