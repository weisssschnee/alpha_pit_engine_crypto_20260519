# CRYPTO A7AB-0 SELECTOR REWRITE DRYRUN CONTRACT

Generated: 2026-05-29T05:36:23Z

## Decision

`PASS_A7AB0_SELECTOR_REWRITE_DRYRUN_CONTRACT_READY_FOR_A7AB1`

A7AB-0 defines the selector rewrite dryrun. It does not generate formulas or run search.

## Manifest

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
  "allowed_primary_seed_fields": [
    "trade_return_1h",
    "realized_vol_24h",
    "mark_index_basis_bps",
    "realized_vol_168h",
    "premium_close_bps"
  ],
  "authorizes_a7ab1_selector_rewrite_dryrun": true,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7AB0_SELECTOR_REWRITE_DRYRUN_CONTRACT_READY_FOR_A7AB1",
  "executes_contract_only": true,
  "executes_formula_generation": false,
  "executes_search": false,
  "executes_selector_dryrun": false,
  "executes_training": false,
  "generated_at": "2026-05-29T05:36:23Z",
  "seed_field_count": 5,
  "stage": "A7AB-0",
  "uses_may": false
}
```

## Selector Score Features

| feature                  | source                                         |   weight |
|:-------------------------|:-----------------------------------------------|---------:|
| premay_split_consistency | A7AA1 primitive response map                   |     0.3  |
| control_margin           | 1 - max wrong-lag/stale/random control ratio   |     0.25 |
| one_bar_lag_survival     | A7AA1 one_bar_lag_recent_oriented              |     0.2  |
| nonoverlap_robust_tstat  | minimum oriented pre-May non-overlap statistic |     0.15 |
| seed_family_diversity    | field family cap                               |     0.1  |

## Hard Gates

| gate                             | rule                                                               |
|:---------------------------------|:-------------------------------------------------------------------|
| primary_field_must_be_a7aa2_seed | field in A7AA2 predictive_signal_candidate set                     |
| control_ratio_lt_1               | control_ratio_premay_max < 1.0                                     |
| premay_all_positive              | validation/test/recent all oriented positive                       |
| lag_ok                           | one_bar_lag_recent_oriented positive and >= 25pct of recent        |
| label_and_horizon_focus          | label/horizon must be supported by A7AA1 evidence                  |
| no_may                           | May not used in selector score, generation, mutation, or threshold |

## Allowed Seed Fields

| field_name           | field_family   | feature_role                | reason                                             |   total_tests |   primitive_response_candidate_count |   premay_stable_count |   control_like_count |   lag_fragile_count |   premay_unstable_count | best_label_families                                       | best_horizons   | best_transforms   |
|:---------------------|:---------------|:----------------------------|:---------------------------------------------------|--------------:|-------------------------------------:|----------------------:|---------------------:|--------------------:|------------------------:|:----------------------------------------------------------|:----------------|:------------------|
| trade_return_1h      | price_return   | predictive_signal_candidate | has_control_clean_lag_surviving_primitive_response |            27 |                                    4 |                    21 |                   13 |                   4 |                       6 | L7_ranked_future_return                                   | 1\|4            | cs_rank\|level    |
| realized_vol_24h     | volatility     | predictive_signal_candidate | has_control_clean_lag_surviving_primitive_response |            27 |                                    2 |                    23 |                   21 |                   0 |                       4 | L7_ranked_future_return                                   | 1               | cs_rank\|level    |
| mark_index_basis_bps | basis_premium  | predictive_signal_candidate | has_control_clean_lag_surviving_primitive_response |            27 |                                    2 |                    16 |                    7 |                   7 |                      11 | L0_raw_forward_return\|L1_cross_sectional_relative_return | 1               | delta_24h         |
| realized_vol_168h    | volatility     | predictive_signal_candidate | has_control_clean_lag_surviving_primitive_response |            27 |                                    2 |                    16 |                   14 |                   0 |                      11 | L7_ranked_future_return                                   | 1               | cs_rank\|level    |
| premium_close_bps    | basis_premium  | predictive_signal_candidate | has_control_clean_lag_surviving_primitive_response |            27 |                                    1 |                    12 |                    9 |                   2 |                      15 | L7_ranked_future_return                                   | 1               | delta_24h         |
