# CRYPTO A7FF-19 COMPANY NUMERIC CONFIRMATION AGGREGATE

Generated: 2026-05-30T05:08:21Z

## Decision

`PASS_A7FF19_COMPANY_NUMERIC_CONFIRMATION_AGGREGATE_BUILT`

A7FF-19 aggregates company-machine numeric confirmation shards over the A7FF-19 external-selector execution queue. It is bounded numeric confirmation, not formula generation, alpha search, alpha proof, shadow, paper, or live execution.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FF19_COMPANY_NUMERIC_CONFIRMATION_AGGREGATE_BUILT",
  "executes_generation": false,
  "executes_search": false,
  "generated_at": "2026-05-30T05:08:21Z",
  "missing_manifests": [],
  "non_l7_label_families": 4,
  "shard_count_complete": 2,
  "shard_count_expected": 2,
  "stage": "A7FF-19-COMPANY-NUMERIC-CONFIRMATION-AGGREGATE",
  "total_input_blueprints": 56,
  "total_label_response_rows": 1120,
  "total_materialized_activity_ok": 56,
  "total_non_l7_numeric_clue_rows": 276,
  "total_portfolio_queue_count": 56,
  "total_rank_label_diagnostic_clue_rows": 56,
  "total_selected_portfolio_queue_count": 41,
  "uses_may": false
}
```

## Shards

|   shard | stage      | decision                                                |   input_blueprint_count | queue_path                                                                                                                                                           |   queue_offset |   queue_limit |   materialized_activity_ok_count |   label_response_rows |   non_l7_numeric_clue_rows |   rank_label_diagnostic_clue_rows |   portfolio_queue_count |   selected_portfolio_queue_count | uses_may   | authorizes_search   |
|--------:|:-----------|:--------------------------------------------------------|------------------------:|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------:|--------------:|---------------------------------:|----------------------:|---------------------------:|----------------------------------:|------------------------:|---------------------------------:|:-----------|:--------------------|
|      00 | A7FF-19S00 | PASS_A7FF19S00_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                      28 | D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote\runtime\a7ff19_external_selector_confirmation_contract\a7ff19_execution_queue.csv |              0 |            28 |                               28 |                   560 |                        130 |                                28 |                      28 |                               20 | False      | False               |
|      01 | A7FF-19S01 | PASS_A7FF19S01_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                      28 | D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote\runtime\a7ff19_external_selector_confirmation_contract\a7ff19_execution_queue.csv |             28 |            28 |                               28 |                   560 |                        146 |                                28 |                      28 |                               21 | False      | False               |

## Non-L7 Label Summary

| label_family                       |   label_horizon_h |   clue_rows |   unique_blueprints |   median_control_ratio |   median_cost2 |   median_cost5 |   median_cost10 |
|:-----------------------------------|------------------:|------------:|--------------------:|-----------------------:|---------------:|---------------:|----------------:|
| L0_raw_forward_return              |                 1 |          43 |                  43 |               0.361347 |    0.00076721  |    0.00016721  |    -0.00083279  |
| L0_raw_forward_return              |                 4 |          11 |                  11 |               0.763523 |    0.0023833   |    0.0017833   |     0.000783295 |
| L0_raw_forward_return              |                 8 |           5 |                   5 |               0.991964 |    0.00110446  |    0.000504459 |    -0.000495541 |
| L1_cross_sectional_relative_return |                 1 |          43 |                  43 |               0.331963 |    0.00076721  |    0.00016721  |    -0.00083279  |
| L1_cross_sectional_relative_return |                 4 |          15 |                  15 |               0.797096 |    0.00245245  |    0.00185245  |     0.000852452 |
| L1_cross_sectional_relative_return |                 8 |           5 |                   5 |               0.784453 |    0.00232959  |    0.00172959  |     0.000729595 |
| L3_liquidity_tier_relative_return  |                 1 |          46 |                  46 |               0.427942 |    0.000799432 |    0.000199432 |    -0.000800568 |
| L3_liquidity_tier_relative_return  |                 4 |          14 |                  14 |               0.877685 |    0.0023871   |    0.0017871   |     0.000787101 |
| L3_liquidity_tier_relative_return  |                 8 |           3 |                   3 |               0.907722 |    0.0020376   |    0.0014376   |     0.000437602 |
| L5_vol_adjusted_return             |                 1 |          43 |                  43 |               0.281159 |    0.137807    |    0.137207    |     0.136207    |
| L5_vol_adjusted_return             |                 4 |          25 |                  25 |               0.604733 |    0.273124    |    0.272524    |     0.271524    |
| L5_vol_adjusted_return             |                 8 |          23 |                  23 |               0.671094 |    0.385681    |    0.385081    |     0.384081    |

## Non-L7 Semantic / Label Summary

| semantic_pair                          | label_family                       |   label_horizon_h |   count |
|:---------------------------------------|:-----------------------------------|------------------:|--------:|
| basis_premium_like\|positioning_like   | L3_liquidity_tier_relative_return  |                 1 |      19 |
| basis_premium_like\|positioning_like   | L0_raw_forward_return              |                 1 |      18 |
| basis_premium_like\|positioning_like   | L1_cross_sectional_relative_return |                 1 |      18 |
| basis_premium_like\|positioning_like   | L5_vol_adjusted_return             |                 1 |      14 |
| basis_premium_like\|volatility_like    | L3_liquidity_tier_relative_return  |                 1 |      13 |
| basis_premium_like\|basis_premium_like | L5_vol_adjusted_return             |                 1 |      13 |
| basis_premium_like\|volatility_like    | L5_vol_adjusted_return             |                 1 |      12 |
| basis_premium_like\|volatility_like    | L0_raw_forward_return              |                 1 |      12 |
| basis_premium_like\|volatility_like    | L1_cross_sectional_relative_return |                 1 |      12 |
| basis_premium_like\|basis_premium_like | L5_vol_adjusted_return             |                 8 |      11 |
| basis_premium_like\|basis_premium_like | L3_liquidity_tier_relative_return  |                 1 |      10 |
| basis_premium_like\|basis_premium_like | L5_vol_adjusted_return             |                 4 |       9 |
| basis_premium_like\|basis_premium_like | L0_raw_forward_return              |                 1 |       9 |
| basis_premium_like\|basis_premium_like | L1_cross_sectional_relative_return |                 1 |       9 |
| basis_premium_like\|positioning_like   | L5_vol_adjusted_return             |                 4 |       7 |
| basis_premium_like\|volatility_like    | L5_vol_adjusted_return             |                 4 |       6 |
| basis_premium_like\|basis_premium_like | L3_liquidity_tier_relative_return  |                 4 |       5 |
| basis_premium_like\|positioning_like   | L3_liquidity_tier_relative_return  |                 4 |       5 |
| basis_premium_like\|volatility_like    | L5_vol_adjusted_return             |                 8 |       5 |
| basis_premium_like\|positioning_like   | L5_vol_adjusted_return             |                 8 |       5 |
| basis_premium_like\|price_like         | L5_vol_adjusted_return             |                 1 |       4 |
| basis_premium_like\|volatility_like    | L1_cross_sectional_relative_return |                 4 |       4 |
| basis_premium_like\|price_like         | L0_raw_forward_return              |                 1 |       4 |
| basis_premium_like\|basis_premium_like | L1_cross_sectional_relative_return |                 4 |       4 |
| basis_premium_like\|price_like         | L1_cross_sectional_relative_return |                 1 |       4 |
| basis_premium_like\|price_like         | L3_liquidity_tier_relative_return  |                 1 |       4 |
| basis_premium_like\|positioning_like   | L1_cross_sectional_relative_return |                 4 |       4 |
| basis_premium_like\|price_like         | L5_vol_adjusted_return             |                 4 |       3 |
| basis_premium_like\|volatility_like    | L0_raw_forward_return              |                 4 |       3 |
| basis_premium_like\|price_like         | L0_raw_forward_return              |                 4 |       3 |
| basis_premium_like\|volatility_like    | L3_liquidity_tier_relative_return  |                 4 |       3 |
| basis_premium_like\|volatility_like    | L1_cross_sectional_relative_return |                 8 |       3 |
| basis_premium_like\|positioning_like   | L0_raw_forward_return              |                 4 |       3 |
| basis_premium_like\|price_like         | L1_cross_sectional_relative_return |                 4 |       3 |
| basis_premium_like\|basis_premium_like | L0_raw_forward_return              |                 4 |       2 |
| basis_premium_like\|price_like         | L5_vol_adjusted_return             |                 8 |       2 |
| basis_premium_like\|volatility_like    | L3_liquidity_tier_relative_return  |                 8 |       2 |
| basis_premium_like\|volatility_like    | L0_raw_forward_return              |                 8 |       2 |
| basis_premium_like\|positioning_like   | L0_raw_forward_return              |                 8 |       2 |
| basis_premium_like\|basis_premium_like | L0_raw_forward_return              |                 8 |       1 |
| basis_premium_like\|basis_premium_like | L1_cross_sectional_relative_return |                 8 |       1 |
| basis_premium_like\|positioning_like   | L3_liquidity_tier_relative_return  |                 8 |       1 |
| basis_premium_like\|positioning_like   | L1_cross_sectional_relative_return |                 8 |       1 |
| basis_premium_like\|price_like         | L3_liquidity_tier_relative_return  |                 4 |       1 |

## Boundary

```text
No May/post-selection stress is used in scoring or authorization.
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
```
