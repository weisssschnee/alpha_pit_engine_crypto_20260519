# CRYPTO A7FF-16 COMPANY NUMERIC FOLLOWUP AGGREGATE

Generated: 2026-05-30T04:48:16Z

## Decision

`PASS_A7FF16_COMPANY_NUMERIC_FOLLOWUP_AGGREGATE_BUILT`

A7FF-16 aggregates the company-machine numeric confirmation shards over the A7FF-16 cost-tiered execution queue. It is bounded numeric confirmation, not formula generation, alpha search, alpha proof, shadow, paper, or live execution.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FF16_COMPANY_NUMERIC_FOLLOWUP_AGGREGATE_BUILT",
  "executes_generation": false,
  "executes_search": false,
  "generated_at": "2026-05-30T04:48:16Z",
  "missing_manifests": [],
  "non_l7_label_families": 4,
  "shard_count_complete": 2,
  "shard_count_expected": 2,
  "stage": "A7FF-16-COMPANY-NUMERIC-FOLLOWUP-AGGREGATE",
  "total_input_blueprints": 96,
  "total_label_response_rows": 1920,
  "total_materialized_activity_ok": 96,
  "total_non_l7_numeric_clue_rows": 402,
  "total_portfolio_queue_count": 95,
  "total_rank_label_diagnostic_clue_rows": 81,
  "total_selected_portfolio_queue_count": 59,
  "uses_may": false
}
```

## Shards

|   shard | stage      | decision                                                |   input_blueprint_count | queue_path                                                                                                                                                         |   queue_offset |   queue_limit |   materialized_activity_ok_count |   label_response_rows |   non_l7_numeric_clue_rows |   rank_label_diagnostic_clue_rows |   portfolio_queue_count |   selected_portfolio_queue_count | uses_may   | authorizes_search   |
|--------:|:-----------|:--------------------------------------------------------|------------------------:|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------:|--------------:|---------------------------------:|----------------------:|---------------------------:|----------------------------------:|------------------------:|---------------------------------:|:-----------|:--------------------|
|      00 | A7FF-16S00 | PASS_A7FF16S00_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                      48 | D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote\runtime\a7ff16_cost_tiered_numeric_followup_contract\a7ff16_execution_queue.csv |              0 |            48 |                               48 |                   960 |                        203 |                                47 |                      48 |                               33 | False      | False               |
|      01 | A7FF-16S01 | PASS_A7FF16S01_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                      48 | D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote\runtime\a7ff16_cost_tiered_numeric_followup_contract\a7ff16_execution_queue.csv |             48 |            48 |                               48 |                   960 |                        199 |                                34 |                      47 |                               26 | False      | False               |

## Non-L7 Label Summary

| label_family                       |   label_horizon_h |   clue_rows |   unique_blueprints |   median_control_ratio |   median_cost2 |   median_cost5 |   median_cost10 |
|:-----------------------------------|------------------:|------------:|--------------------:|-----------------------:|---------------:|---------------:|----------------:|
| L0_raw_forward_return              |                 1 |          68 |                  68 |               0.416451 |    0.000698371 |    9.83707e-05 |    -0.000901629 |
| L0_raw_forward_return              |                 4 |          20 |                  20 |               0.763523 |    0.00245372  |    0.00185372  |     0.000853719 |
| L0_raw_forward_return              |                 8 |           4 |                   4 |               0.818806 |    0.000917975 |    0.000317975 |    -0.000682025 |
| L1_cross_sectional_relative_return |                 1 |          67 |                  67 |               0.368946 |    0.00070292  |    0.00010292  |    -0.00089708  |
| L1_cross_sectional_relative_return |                 4 |          25 |                  25 |               0.763523 |    0.00245257  |    0.00185257  |     0.000852569 |
| L1_cross_sectional_relative_return |                 8 |           5 |                   5 |               0.97432  |    0.000731492 |    0.000131492 |    -0.000868508 |
| L3_liquidity_tier_relative_return  |                 1 |          69 |                  69 |               0.414705 |    0.000730858 |    0.000130858 |    -0.000869142 |
| L3_liquidity_tier_relative_return  |                 4 |          20 |                  20 |               0.91798  |    0.0023871   |    0.0017871   |     0.000787101 |
| L3_liquidity_tier_relative_return  |                 8 |           2 |                   2 |               0.81374  |    0.000667088 |    6.70881e-05 |    -0.000932912 |
| L5_vol_adjusted_return             |                 1 |          68 |                  68 |               0.317602 |    0.12476     |    0.12416     |     0.12316     |
| L5_vol_adjusted_return             |                 4 |          31 |                  31 |               0.664389 |    0.273078    |    0.272478    |     0.271478    |
| L5_vol_adjusted_return             |                 8 |          23 |                  23 |               0.640765 |    0.385681    |    0.385081    |     0.384081    |

## Non-L7 Semantic / Label Summary

| semantic_pair                          | label_family                       |   label_horizon_h |   count |
|:---------------------------------------|:-----------------------------------|------------------:|--------:|
| basis_premium_like\|positioning_like   | L0_raw_forward_return              |                 1 |      27 |
| basis_premium_like\|positioning_like   | L1_cross_sectional_relative_return |                 1 |      27 |
| basis_premium_like\|positioning_like   | L3_liquidity_tier_relative_return  |                 1 |      27 |
| basis_premium_like\|basis_premium_like | L5_vol_adjusted_return             |                 1 |      22 |
| basis_premium_like\|volatility_like    | L5_vol_adjusted_return             |                 1 |      22 |
| basis_premium_like\|volatility_like    | L3_liquidity_tier_relative_return  |                 1 |      21 |
| basis_premium_like\|volatility_like    | L1_cross_sectional_relative_return |                 1 |      20 |
| basis_premium_like\|volatility_like    | L0_raw_forward_return              |                 1 |      20 |
| basis_premium_like\|positioning_like   | L5_vol_adjusted_return             |                 1 |      16 |
| basis_premium_like\|basis_premium_like | L0_raw_forward_return              |                 1 |      14 |
| basis_premium_like\|basis_premium_like | L3_liquidity_tier_relative_return  |                 1 |      14 |
| basis_premium_like\|basis_premium_like | L1_cross_sectional_relative_return |                 1 |      13 |
| basis_premium_like\|positioning_like   | L5_vol_adjusted_return             |                 4 |      10 |
| basis_premium_like\|volatility_like    | L5_vol_adjusted_return             |                 4 |       9 |
| basis_premium_like\|basis_premium_like | L5_vol_adjusted_return             |                 4 |       9 |
| basis_premium_like\|basis_premium_like | L5_vol_adjusted_return             |                 8 |       9 |
| basis_premium_like\|price_like         | L5_vol_adjusted_return             |                 1 |       8 |
| basis_premium_like\|basis_premium_like | L0_raw_forward_return              |                 4 |       7 |
| basis_premium_like\|volatility_like    | L5_vol_adjusted_return             |                 8 |       7 |
| basis_premium_like\|basis_premium_like | L1_cross_sectional_relative_return |                 4 |       7 |
| basis_premium_like\|price_like         | L1_cross_sectional_relative_return |                 1 |       7 |
| basis_premium_like\|price_like         | L0_raw_forward_return              |                 1 |       7 |
| basis_premium_like\|price_like         | L3_liquidity_tier_relative_return  |                 1 |       7 |
| basis_premium_like\|volatility_like    | L1_cross_sectional_relative_return |                 4 |       7 |
| basis_premium_like\|positioning_like   | L1_cross_sectional_relative_return |                 4 |       6 |
| basis_premium_like\|positioning_like   | L3_liquidity_tier_relative_return  |                 4 |       6 |
| basis_premium_like\|basis_premium_like | L3_liquidity_tier_relative_return  |                 4 |       6 |
| basis_premium_like\|volatility_like    | L3_liquidity_tier_relative_return  |                 4 |       5 |
| basis_premium_like\|price_like         | L1_cross_sectional_relative_return |                 4 |       5 |
| basis_premium_like\|positioning_like   | L0_raw_forward_return              |                 4 |       5 |
| basis_premium_like\|price_like         | L0_raw_forward_return              |                 4 |       4 |
| basis_premium_like\|price_like         | L5_vol_adjusted_return             |                 8 |       4 |
| basis_premium_like\|volatility_like    | L0_raw_forward_return              |                 4 |       4 |
| basis_premium_like\|price_like         | L3_liquidity_tier_relative_return  |                 4 |       3 |
| basis_premium_like\|price_like         | L5_vol_adjusted_return             |                 4 |       3 |
| basis_premium_like\|positioning_like   | L5_vol_adjusted_return             |                 8 |       3 |
| basis_premium_like\|volatility_like    | L1_cross_sectional_relative_return |                 8 |       2 |
| basis_premium_like\|volatility_like    | L0_raw_forward_return              |                 8 |       2 |
| basis_premium_like\|positioning_like   | L1_cross_sectional_relative_return |                 8 |       2 |
| basis_premium_like\|basis_premium_like | L0_raw_forward_return              |                 8 |       1 |
| basis_premium_like\|basis_premium_like | L1_cross_sectional_relative_return |                 8 |       1 |
| basis_premium_like\|positioning_like   | L3_liquidity_tier_relative_return  |                 8 |       1 |
| basis_premium_like\|positioning_like   | L0_raw_forward_return              |                 8 |       1 |
| basis_premium_like\|volatility_like    | L3_liquidity_tier_relative_return  |                 8 |       1 |

## Boundary

```text
No May/post-selection stress is used in scoring or authorization.
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
```
