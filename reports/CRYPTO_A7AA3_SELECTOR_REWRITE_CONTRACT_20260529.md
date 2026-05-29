# CRYPTO A7AA-3 SELECTOR REWRITE CONTRACT

Generated: 2026-05-29T05:31:49Z

## Decision

`PASS_A7AA3_SELECTOR_REWRITE_CONTRACT_READY_FOR_A7AB0`

A7AA-3 rewrites the selector target from expression-family-first to primitive-response-first. It does not authorize formula search.

## Manifest

```json
{
  "authorizes_a7ab0_selector_rewrite_dryrun_contract": true,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "blocked_field_count": 19,
  "decision": "PASS_A7AA3_SELECTOR_REWRITE_CONTRACT_READY_FOR_A7AB0",
  "executes_contract_only": true,
  "executes_search": false,
  "executes_training": false,
  "generated_at": "2026-05-29T05:31:49Z",
  "seed_field_count": 5,
  "stage": "A7AA-3",
  "uses_may": false
}
```

## Selector Rules

```json
{
  "allowed_horizon_focus": [
    1,
    4
  ],
  "allowed_label_focus": [
    "L0_raw_forward_return",
    "L1_cross_sectional_relative_return",
    "L7_ranked_future_return"
  ],
  "allowed_next_stage": "A7AB0_selector_rewrite_dryrun_contract_only",
  "allowed_primary_families": [
    "basis_premium",
    "price_return",
    "volatility"
  ],
  "allowed_primary_seed_fields": [
    "trade_return_1h",
    "realized_vol_24h",
    "mark_index_basis_bps",
    "realized_vol_168h",
    "premium_close_bps"
  ],
  "not_authorized": [
    "formula_search_execution",
    "large_search",
    "alpha_proof",
    "shadow_paper_live"
  ],
  "required_pre_generation_filters": [
    "seed_field_must_have_A7AA1_primitive_response_candidate",
    "label_family_must_match_seed_evidence",
    "horizon_must_match_seed_evidence_or_be_adjacent_short_horizon",
    "wrong_lag_and_random_controls_attached",
    "no_May_in_selector_generation_mutation"
  ],
  "selector_target": "primitive_response_first"
}
```

## Allowed Seed Fields

| field_name           | field_family   | feature_role                | reason                                             |   total_tests |   primitive_response_candidate_count |   premay_stable_count |   control_like_count |   lag_fragile_count |   premay_unstable_count | best_label_families                                       | best_horizons   | best_transforms   |
|:---------------------|:---------------|:----------------------------|:---------------------------------------------------|--------------:|-------------------------------------:|----------------------:|---------------------:|--------------------:|------------------------:|:----------------------------------------------------------|:----------------|:------------------|
| trade_return_1h      | price_return   | predictive_signal_candidate | has_control_clean_lag_surviving_primitive_response |            27 |                                    4 |                    21 |                   13 |                   4 |                       6 | L7_ranked_future_return                                   | 1\|4            | cs_rank\|level    |
| realized_vol_24h     | volatility     | predictive_signal_candidate | has_control_clean_lag_surviving_primitive_response |            27 |                                    2 |                    23 |                   21 |                   0 |                       4 | L7_ranked_future_return                                   | 1               | cs_rank\|level    |
| mark_index_basis_bps | basis_premium  | predictive_signal_candidate | has_control_clean_lag_surviving_primitive_response |            27 |                                    2 |                    16 |                    7 |                   7 |                      11 | L0_raw_forward_return\|L1_cross_sectional_relative_return | 1               | delta_24h         |
| realized_vol_168h    | volatility     | predictive_signal_candidate | has_control_clean_lag_surviving_primitive_response |            27 |                                    2 |                    16 |                   14 |                   0 |                      11 | L7_ranked_future_return                                   | 1               | cs_rank\|level    |
| premium_close_bps    | basis_premium  | predictive_signal_candidate | has_control_clean_lag_surviving_primitive_response |            27 |                                    1 |                    12 |                    9 |                   2 |                      15 | L7_ranked_future_return                                   | 1               | delta_24h         |

## Blocked Primary Fields

| field_name                           |
|:-------------------------------------|
| mark_trade_basis_bps                 |
| trade_return_24h                     |
| open_interest_last                   |
| taker_buy_sell_volume_ratio_last     |
| global_long_short_account_ratio_last |
| kline_taker_buy_quote_share          |
| oi_x_price_move_24h                  |
| top_long_short_position_ratio_last   |
| open_interest_change_24h             |
| open_interest_value_last             |
| top_long_short_account_ratio_last    |
| trade_quote_volume                   |
| basis_abs_168h                       |
| premium_abs_168h                     |
| liquidity_rank_active_universe       |
| trade_count                          |
| funding_rate                         |
| funding_rate_abs_168h                |
| funding_rate_mean_168h               |

## Boundary

```text
A7AA-3 only authorizes A7AB0 contract/dryrun design.
Formula search execution remains not authorized.
```
