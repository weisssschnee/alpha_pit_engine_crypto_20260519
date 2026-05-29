# CRYPTO A7AA-2 FEATURE ROLE CLASSIFICATION

Generated: 2026-05-29T05:30:56Z

## Decision

`PASS_A7AA2_FEATURE_ROLES_READY_FOR_SELECTOR_REWRITE_CONTRACT`

A7AA-2 classifies primitive fields by observed response role. It does not authorize formula search.

## Manifest

```json
{
  "authorizes_a7aa3_selector_rewrite_contract": true,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7AA2_FEATURE_ROLES_READY_FOR_SELECTOR_REWRITE_CONTRACT",
  "executes_role_classification": true,
  "executes_search": false,
  "executes_training": false,
  "field_count": 24,
  "generated_at": "2026-05-29T05:30:56Z",
  "signal_candidate_field_count": 5,
  "source_a7aa1_decision": "PASS_A7AA1_PRIMITIVE_RESPONSE_CANDIDATES_FOUND_FORMULA_SEARCH_STILL_HOLD",
  "stage": "A7AA-2",
  "uses_may": false
}
```

## Selector Seed Fields

| field_name           | field_family   | feature_role                | reason                                             |   total_tests |   primitive_response_candidate_count |   premay_stable_count |   control_like_count |   lag_fragile_count |   premay_unstable_count | best_label_families                                       | best_horizons   | best_transforms   |
|:---------------------|:---------------|:----------------------------|:---------------------------------------------------|--------------:|-------------------------------------:|----------------------:|---------------------:|--------------------:|------------------------:|:----------------------------------------------------------|:----------------|:------------------|
| trade_return_1h      | price_return   | predictive_signal_candidate | has_control_clean_lag_surviving_primitive_response |            27 |                                    4 |                    21 |                   13 |                   4 |                       6 | L7_ranked_future_return                                   | 1\|4            | cs_rank\|level    |
| realized_vol_24h     | volatility     | predictive_signal_candidate | has_control_clean_lag_surviving_primitive_response |            27 |                                    2 |                    23 |                   21 |                   0 |                       4 | L7_ranked_future_return                                   | 1               | cs_rank\|level    |
| mark_index_basis_bps | basis_premium  | predictive_signal_candidate | has_control_clean_lag_surviving_primitive_response |            27 |                                    2 |                    16 |                    7 |                   7 |                      11 | L0_raw_forward_return\|L1_cross_sectional_relative_return | 1               | delta_24h         |
| realized_vol_168h    | volatility     | predictive_signal_candidate | has_control_clean_lag_surviving_primitive_response |            27 |                                    2 |                    16 |                   14 |                   0 |                      11 | L7_ranked_future_return                                   | 1               | cs_rank\|level    |
| premium_close_bps    | basis_premium  | predictive_signal_candidate | has_control_clean_lag_surviving_primitive_response |            27 |                                    1 |                    12 |                    9 |                   2 |                      15 | L7_ranked_future_return                                   | 1               | delta_24h         |

## Family Role Summary

| field_family              |   field_count |   signal_candidate_fields |   risk_or_control_fields |   weak_fields |
|:--------------------------|--------------:|--------------------------:|-------------------------:|--------------:|
| basis_premium             |             5 |                         2 |                        0 |             2 |
| volatility                |             2 |                         2 |                        0 |             0 |
| price_return              |             2 |                         1 |                        1 |             0 |
| funding                   |             3 |                         0 |                        0 |             3 |
| liquidity                 |             3 |                         0 |                        0 |             3 |
| open_interest             |             3 |                         0 |                        3 |             0 |
| positioning               |             3 |                         0 |                        3 |             0 |
| taker_flow                |             2 |                         0 |                        0 |             0 |
| open_interest_interaction |             1 |                         0 |                        1 |             0 |

## Feature Role Ledger

| field_name                           | field_family              | feature_role                      | reason                                             |   total_tests |   primitive_response_candidate_count |   premay_stable_count |   control_like_count |   lag_fragile_count |   premay_unstable_count | best_label_families                                       | best_horizons   | best_transforms   |
|:-------------------------------------|:--------------------------|:----------------------------------|:---------------------------------------------------|--------------:|-------------------------------------:|----------------------:|---------------------:|--------------------:|------------------------:|:----------------------------------------------------------|:----------------|:------------------|
| trade_return_1h                      | price_return              | predictive_signal_candidate       | has_control_clean_lag_surviving_primitive_response |            27 |                                    4 |                    21 |                   13 |                   4 |                       6 | L7_ranked_future_return                                   | 1\|4            | cs_rank\|level    |
| realized_vol_24h                     | volatility                | predictive_signal_candidate       | has_control_clean_lag_surviving_primitive_response |            27 |                                    2 |                    23 |                   21 |                   0 |                       4 | L7_ranked_future_return                                   | 1               | cs_rank\|level    |
| mark_index_basis_bps                 | basis_premium             | predictive_signal_candidate       | has_control_clean_lag_surviving_primitive_response |            27 |                                    2 |                    16 |                    7 |                   7 |                      11 | L0_raw_forward_return\|L1_cross_sectional_relative_return | 1               | delta_24h         |
| realized_vol_168h                    | volatility                | predictive_signal_candidate       | has_control_clean_lag_surviving_primitive_response |            27 |                                    2 |                    16 |                   14 |                   0 |                      11 | L7_ranked_future_return                                   | 1               | cs_rank\|level    |
| premium_close_bps                    | basis_premium             | predictive_signal_candidate       | has_control_clean_lag_surviving_primitive_response |            27 |                                    1 |                    12 |                    9 |                   2 |                      15 | L7_ranked_future_return                                   | 1               | delta_24h         |
| mark_trade_basis_bps                 | basis_premium             | regime_state_or_interaction_input | premay_stable_without_clean_candidate_gate         |            27 |                                    0 |                    22 |                   10 |                  12 |                       5 |                                                           |                 |                   |
| trade_return_24h                     | price_return              | control_like_or_risk_exposure     | premay_stable_but_control_like                     |            27 |                                    0 |                    19 |                   19 |                   0 |                       8 |                                                           |                 |                   |
| open_interest_last                   | open_interest             | control_like_or_risk_exposure     | premay_stable_but_control_like                     |            27 |                                    0 |                    16 |                   16 |                   0 |                      11 |                                                           |                 |                   |
| taker_buy_sell_volume_ratio_last     | taker_flow                | regime_state_or_interaction_input | premay_stable_without_clean_candidate_gate         |            27 |                                    0 |                    12 |                   11 |                   1 |                      15 |                                                           |                 |                   |
| global_long_short_account_ratio_last | positioning               | control_like_or_risk_exposure     | premay_stable_but_control_like                     |            27 |                                    0 |                    10 |                   10 |                   0 |                      17 |                                                           |                 |                   |
| kline_taker_buy_quote_share          | taker_flow                | regime_state_or_interaction_input | premay_stable_without_clean_candidate_gate         |            27 |                                    0 |                    10 |                    8 |                   2 |                      17 |                                                           |                 |                   |
| oi_x_price_move_24h                  | open_interest_interaction | control_like_or_risk_exposure     | premay_stable_but_control_like                     |            27 |                                    0 |                     9 |                    9 |                   0 |                      18 |                                                           |                 |                   |
| top_long_short_position_ratio_last   | positioning               | control_like_or_risk_exposure     | premay_stable_but_control_like                     |            27 |                                    0 |                     8 |                    8 |                   0 |                      19 |                                                           |                 |                   |
| open_interest_change_24h             | open_interest             | control_like_or_risk_exposure     | premay_stable_but_control_like                     |            27 |                                    0 |                     7 |                    7 |                   0 |                      20 |                                                           |                 |                   |
| open_interest_value_last             | open_interest             | control_like_or_risk_exposure     | premay_stable_but_control_like                     |            27 |                                    0 |                     7 |                    7 |                   0 |                      20 |                                                           |                 |                   |
| top_long_short_account_ratio_last    | positioning               | control_like_or_risk_exposure     | premay_stable_but_control_like                     |            27 |                                    0 |                     6 |                    6 |                   0 |                      21 |                                                           |                 |                   |
| trade_quote_volume                   | liquidity                 | weak_or_unstable                  | mostly_premay_unstable                             |            27 |                                    0 |                     5 |                    5 |                   0 |                      22 |                                                           |                 |                   |
| basis_abs_168h                       | basis_premium             | weak_or_unstable                  | mostly_premay_unstable                             |            27 |                                    0 |                     4 |                    4 |                   0 |                      23 |                                                           |                 |                   |
| premium_abs_168h                     | basis_premium             | weak_or_unstable                  | mostly_premay_unstable                             |            27 |                                    0 |                     4 |                    4 |                   0 |                      23 |                                                           |                 |                   |
| liquidity_rank_active_universe       | liquidity                 | weak_or_unstable                  | mostly_premay_unstable                             |            27 |                                    0 |                     2 |                    2 |                   0 |                      25 |                                                           |                 |                   |
| trade_count                          | liquidity                 | weak_or_unstable                  | mostly_premay_unstable                             |            27 |                                    0 |                     2 |                    2 |                   0 |                      25 |                                                           |                 |                   |
| funding_rate                         | funding                   | weak_or_unstable                  | mostly_premay_unstable                             |            27 |                                    0 |                     1 |                    1 |                   0 |                      26 |                                                           |                 |                   |
| funding_rate_abs_168h                | funding                   | weak_or_unstable                  | mostly_premay_unstable                             |            27 |                                    0 |                     0 |                    0 |                   0 |                      27 |                                                           |                 |                   |
| funding_rate_mean_168h               | funding                   | weak_or_unstable                  | mostly_premay_unstable                             |            27 |                                    0 |                     0 |                    0 |                   0 |                      27 |                                                           |                 |                   |

## Boundary

```text
Formula search remains not authorized.
Fields without primitive response evidence are blocked from being primary selector seeds.
```
