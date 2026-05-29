# CRYPTO A7FF-10 COMPANY PARALLEL NUMERIC AGGREGATE

Generated: 2026-05-29T19:59:27Z

## Decision

`PASS_A7FF10_COMPANY_PARALLEL_NUMERIC_AGGREGATE_BUILT`

A7FF-10 aggregates company-machine parallel numeric-probe shards. It is not generation, replay, search, alpha proof, shadow, paper, or live execution.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FF10_COMPANY_PARALLEL_NUMERIC_AGGREGATE_BUILT",
  "generated_at": "2026-05-29T19:59:27Z",
  "missing_manifests": [],
  "shard_count_complete": 4,
  "shard_count_expected": 4,
  "stage": "A7FF-10-COMPANY-PARALLEL-AGGREGATE",
  "total_input_blueprints": 384,
  "total_label_response_rows": 7680,
  "total_materialized_activity_ok": 384,
  "total_non_l7_numeric_clue_rows": 237,
  "total_portfolio_queue_count": 80,
  "total_rank_label_diagnostic_clue_rows": 66,
  "total_selected_portfolio_queue_count": 40,
  "uses_may": false
}
```

## Shards

```text
shard      stage                                                decision  input_blueprint_count  queue_offset  queue_limit  materialized_activity_ok_count  label_response_rows  non_l7_numeric_clue_rows  rank_label_diagnostic_clue_rows  portfolio_queue_count  selected_portfolio_queue_count  uses_may  authorizes_search
   00 A7FF-10S00 PASS_A7FF10S00_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH                     96             0           96                              96                 1920                        87                               14                     21                               8     False              False
   01 A7FF-10S01 PASS_A7FF10S01_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH                     96            96           96                              96                 1920                       112                               23                     35                              14     False              False
   02 A7FF-10S02 PASS_A7FF10S02_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH                     96           192           96                              96                 1920                        19                                3                      6                               5     False              False
   03 A7FF-10S03 PASS_A7FF10S03_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH                     96           288           96                              96                 1920                        19                               26                     18                              13     False              False
```

## Non-L7 Clue Summary

```text
                         semantic_pair                       label_family  label_horizon_h  count
   basis_premium_like\|volatility_like  L3_liquidity_tier_relative_return                1     24
   basis_premium_like\|volatility_like L1_cross_sectional_relative_return                1     18
   basis_premium_like\|volatility_like              L0_raw_forward_return                1     18
   basis_premium_like\|volatility_like             L5_vol_adjusted_return                1     15
  basis_premium_like\|positioning_like              L0_raw_forward_return                1     10
  basis_premium_like\|positioning_like             L5_vol_adjusted_return                1     10
  basis_premium_like\|positioning_like L1_cross_sectional_relative_return                1     10
  basis_premium_like\|positioning_like L1_cross_sectional_relative_return                4      6
   basis_premium_like\|volatility_like              L0_raw_forward_return                4      6
   basis_premium_like\|volatility_like             L5_vol_adjusted_return                8      6
  basis_premium_like\|positioning_like  L3_liquidity_tier_relative_return                1      6
   basis_premium_like\|volatility_like L1_cross_sectional_relative_return                4      5
   basis_premium_like\|volatility_like  L3_liquidity_tier_relative_return                4      5
  basis_premium_like\|positioning_like              L0_raw_forward_return                4      5
  basis_premium_like\|positioning_like  L3_liquidity_tier_relative_return                4      5
   basis_premium_like\|volatility_like             L5_vol_adjusted_return                4      5
                    basis_premium_like              L0_raw_forward_return                1      4
                    basis_premium_like L1_cross_sectional_relative_return                1      4
basis_premium_like\|basis_premium_like  L3_liquidity_tier_relative_return                4      4
                    basis_premium_like  L3_liquidity_tier_relative_return                1      4
basis_premium_like\|basis_premium_like             L5_vol_adjusted_return                4      4
   basis_premium_like\|volatility_like  L3_liquidity_tier_relative_return                8      4
        basis_premium_like\|price_like             L5_vol_adjusted_return                1      3
  basis_premium_like\|positioning_like             L5_vol_adjusted_return                8      3
basis_premium_like\|basis_premium_like             L5_vol_adjusted_return                1      3
basis_premium_like\|basis_premium_like              L0_raw_forward_return                1      3
basis_premium_like\|basis_premium_like L1_cross_sectional_relative_return                4      3
basis_premium_like\|basis_premium_like L1_cross_sectional_relative_return                1      3
                    basis_premium_like             L5_vol_adjusted_return                1      3
basis_premium_like\|basis_premium_like L1_cross_sectional_relative_return                8      3
                    basis_premium_like              L0_raw_forward_return                4      2
                    basis_premium_like L1_cross_sectional_relative_return                4      2
                    basis_premium_like  L3_liquidity_tier_relative_return                4      2
                    basis_premium_like             L5_vol_adjusted_return                8      2
basis_premium_like\|basis_premium_like              L0_raw_forward_return                4      2
basis_premium_like\|basis_premium_like  L3_liquidity_tier_relative_return                1      2
   basis_premium_like\|volatility_like L1_cross_sectional_relative_return                8      2
  basis_premium_like\|positioning_like             L5_vol_adjusted_return                4      2
  basis_premium_like\|positioning_like L1_cross_sectional_relative_return                8      2
   basis_premium_like\|volatility_like              L0_raw_forward_return                8      2
  basis_premium_like\|positioning_like              L0_raw_forward_return                8      2
basis_premium_like\|basis_premium_like             L5_vol_adjusted_return                8      2
  basis_premium_like\|positioning_like  L3_liquidity_tier_relative_return                8      2
                    basis_premium_like              L0_raw_forward_return                8      1
basis_premium_like\|basis_premium_like              L0_raw_forward_return                8      1
                    basis_premium_like L1_cross_sectional_relative_return                8      1
                    basis_premium_like  L3_liquidity_tier_relative_return                8      1
                    basis_premium_like             L5_vol_adjusted_return                4      1
basis_premium_like\|basis_premium_like  L3_liquidity_tier_relative_return                8      1
        basis_premium_like\|price_like L1_cross_sectional_relative_return                1      1
        basis_premium_like\|price_like  L3_liquidity_tier_relative_return                1      1
        basis_premium_like\|price_like              L0_raw_forward_return                1      1
```

## Boundary

```text
No May/post-selection stress is used in scoring or authorization.
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
This stage only scales numeric probing across the A7FF-7E blueprint queue.
```
