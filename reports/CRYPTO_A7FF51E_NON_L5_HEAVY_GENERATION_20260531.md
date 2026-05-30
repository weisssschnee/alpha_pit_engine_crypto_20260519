# CRYPTO A7FF-51E NON-L5 HEAVY GENERATION

Generated: 2026-05-30T19:34:13Z

## Decision

`PASS_A7FF51E_NON_L5_HEAVY_GENERATION_STATIC_READY`

A7FF-51E executes the approved non-L5-first static blueprint generation. It does not run numeric replay or formula search.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_numeric_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "blueprint_rows": 50000,
  "decision": "PASS_A7FF51E_NON_L5_HEAVY_GENERATION_STATIC_READY",
  "duplicate_expression_count": 7772,
  "duplicate_production_key_count": 0,
  "executes_generation": true,
  "executes_numeric_probe": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T19:34:13Z",
  "missing_primary_fields": [],
  "missing_secondary_fields": [],
  "semantic_pair_families": 8,
  "stage": "A7FF-51E",
  "target_label_families": [
    "L0_raw_forward_return",
    "L1_cross_sectional_relative_return",
    "L3_liquidity_tier_relative_return"
  ],
  "top_family_share": 0.138,
  "unsupported_operators": [],
  "used_operators": [
    "Abs",
    "CSRank",
    "Delta",
    "Mean",
    "Mul",
    "SafeDiv",
    "Sign",
    "Sub",
    "ZScore"
  ],
  "uses_may": false,
  "warnings": [
    "expression_duplicates_are_label_horizon_variants"
  ]
}
```

## Static Audit

| metric                                 |     value |   threshold | pass   |
|:---------------------------------------|----------:|------------:|:-------|
| blueprint_rows                         | 50000     |     50000   | True   |
| semantic_pair_families                 |     8     |         6   | True   |
| top_family_share                       |     0.138 |         0.3 | True   |
| non_reference_non_l5_static_candidates | 50000     |       200   | True   |
| primary_label_family_count             |     3     |         3   | True   |
| reference_family_primary_rows          |     0     |         0   | True   |
| missing_primary_fields                 |     0     |         0   | True   |
| missing_secondary_fields               |     0     |         0   | True   |
| unsupported_operator_count             |     0     |         0   | True   |
| duplicate_expression_count             |  7772     |     12500   | True   |
| duplicate_production_key_count         |     0     |         0   | True   |

## Coverage Summary

| semantic_pair                        | motif               | target_label_family                |   rows |   unique_primary_fields |   unique_secondary_fields |   skeletons |   productions |
|:-------------------------------------|:--------------------|:-----------------------------------|-------:|------------------------:|--------------------------:|------------:|--------------:|
| funding_like|basis_premium_like      | sub                 | L0_raw_forward_return              |    329 |                       1 |                         9 |         100 |           329 |
| funding_like|basis_premium_like      | spread_rank         | L1_cross_sectional_relative_return |    329 |                       1 |                         9 |         100 |           329 |
| funding_like|basis_premium_like      | safe_div_abs        | L0_raw_forward_return              |    329 |                       1 |                         9 |         100 |           329 |
| funding_like|basis_premium_like      | signed_spread       | L1_cross_sectional_relative_return |    329 |                       1 |                         9 |         100 |           329 |
| funding_like|basis_premium_like      | signed_spread       | L0_raw_forward_return              |    329 |                       1 |                         9 |         100 |           329 |
| funding_like|basis_premium_like      | spread_rank         | L3_liquidity_tier_relative_return  |    329 |                       1 |                         9 |         100 |           329 |
| funding_like|basis_premium_like      | mean_reversion_gate | L3_liquidity_tier_relative_return  |    329 |                       1 |                         9 |         100 |           329 |
| funding_like|basis_premium_like      | mean_reversion_gate | L0_raw_forward_return              |    329 |                       1 |                         9 |         100 |           329 |
| funding_like|basis_premium_like      | smooth_mul          | L0_raw_forward_return              |    329 |                       1 |                         9 |         100 |           329 |
| funding_like|basis_premium_like      | smooth_mul          | L3_liquidity_tier_relative_return  |    329 |                       1 |                         9 |         100 |           329 |
| funding_like|basis_premium_like      | relative_shock      | L3_liquidity_tier_relative_return  |    329 |                       1 |                         9 |         100 |           329 |
| funding_like|basis_premium_like      | relative_shock      | L1_cross_sectional_relative_return |    329 |                       1 |                         9 |         100 |           329 |
| funding_like|basis_premium_like      | sub                 | L1_cross_sectional_relative_return |    329 |                       1 |                         9 |         100 |           329 |
| funding_like|basis_premium_like      | safe_div_abs        | L1_cross_sectional_relative_return |    328 |                       1 |                         9 |         100 |           328 |
| funding_like|basis_premium_like      | mean_reversion_gate | L1_cross_sectional_relative_return |    328 |                       1 |                         9 |         100 |           328 |
| funding_like|basis_premium_like      | relative_shock      | L0_raw_forward_return              |    328 |                       1 |                         9 |         100 |           328 |
| funding_like|basis_premium_like      | spread_rank         | L0_raw_forward_return              |    328 |                       1 |                         9 |         100 |           328 |
| funding_like|basis_premium_like      | signed_spread       | L3_liquidity_tier_relative_return  |    328 |                       1 |                         9 |         100 |           328 |
| funding_like|basis_premium_like      | sub                 | L3_liquidity_tier_relative_return  |    328 |                       1 |                         9 |         100 |           328 |
| funding_like|basis_premium_like      | smooth_mul          | L1_cross_sectional_relative_return |    328 |                       1 |                         9 |         100 |           328 |
| funding_like|basis_premium_like      | safe_div_abs        | L3_liquidity_tier_relative_return  |    327 |                       1 |                         9 |         100 |           327 |
| basis_premium_like|price_return_like | relative_shock      | L3_liquidity_tier_relative_return  |    298 |                       5 |                         2 |         100 |           298 |
| basis_premium_like|price_return_like | relative_shock      | L1_cross_sectional_relative_return |    298 |                       5 |                         2 |         100 |           298 |
| basis_premium_like|price_return_like | safe_div_abs        | L0_raw_forward_return              |    298 |                       5 |                         2 |         100 |           298 |
| basis_premium_like|price_return_like | sub                 | L0_raw_forward_return              |    298 |                       5 |                         2 |         100 |           298 |
| basis_premium_like|price_return_like | spread_rank         | L3_liquidity_tier_relative_return  |    298 |                       5 |                         2 |         100 |           298 |
| basis_premium_like|price_return_like | sub                 | L1_cross_sectional_relative_return |    298 |                       5 |                         2 |         100 |           298 |
| basis_premium_like|price_return_like | smooth_mul          | L0_raw_forward_return              |    298 |                       5 |                         2 |         100 |           298 |
| basis_premium_like|price_return_like | signed_spread       | L0_raw_forward_return              |    298 |                       5 |                         2 |         100 |           298 |
| basis_premium_like|price_return_like | smooth_mul          | L3_liquidity_tier_relative_return  |    298 |                       5 |                         2 |         100 |           298 |
| basis_premium_like|price_return_like | signed_spread       | L1_cross_sectional_relative_return |    298 |                       5 |                         2 |         100 |           298 |
| basis_premium_like|price_return_like | spread_rank         | L1_cross_sectional_relative_return |    298 |                       5 |                         2 |         100 |           298 |
| liquidity_like|price_return_like     | safe_div_abs        | L1_cross_sectional_relative_return |    298 |                       5 |                         2 |         100 |           298 |
| liquidity_like|price_return_like     | smooth_mul          | L0_raw_forward_return              |    298 |                       5 |                         2 |         100 |           298 |
| liquidity_like|price_return_like     | relative_shock      | L3_liquidity_tier_relative_return  |    298 |                       5 |                         2 |         100 |           298 |
| liquidity_like|price_return_like     | relative_shock      | L0_raw_forward_return              |    298 |                       5 |                         2 |         100 |           298 |
| liquidity_like|price_return_like     | mean_reversion_gate | L1_cross_sectional_relative_return |    298 |                       5 |                         2 |         100 |           298 |
| liquidity_like|price_return_like     | mean_reversion_gate | L0_raw_forward_return              |    298 |                       5 |                         2 |         100 |           298 |
| basis_premium_like|price_return_like | mean_reversion_gate | L3_liquidity_tier_relative_return  |    298 |                       5 |                         2 |         100 |           298 |
| basis_premium_like|price_return_like | mean_reversion_gate | L0_raw_forward_return              |    298 |                       5 |                         2 |         100 |           298 |
| taker_flow_like|basis_premium_like   | smooth_mul          | L3_liquidity_tier_relative_return  |    298 |                       1 |                         9 |         100 |           298 |
| taker_flow_like|basis_premium_like   | spread_rank         | L1_cross_sectional_relative_return |    298 |                       1 |                         9 |         100 |           298 |
| taker_flow_like|basis_premium_like   | smooth_mul          | L0_raw_forward_return              |    298 |                       1 |                         9 |         100 |           298 |
| positioning_like|price_return_like   | smooth_mul          | L0_raw_forward_return              |    298 |                       5 |                         2 |         100 |           298 |
| positioning_like|price_return_like   | signed_spread       | L3_liquidity_tier_relative_return  |    298 |                       5 |                         2 |         100 |           298 |
| positioning_like|price_return_like   | signed_spread       | L1_cross_sectional_relative_return |    298 |                       5 |                         2 |         100 |           298 |
| positioning_like|price_return_like   | safe_div_abs        | L1_cross_sectional_relative_return |    298 |                       5 |                         2 |         100 |           298 |
| positioning_like|price_return_like   | relative_shock      | L3_liquidity_tier_relative_return  |    298 |                       5 |                         2 |         100 |           298 |
| liquidity_like|price_return_like     | smooth_mul          | L1_cross_sectional_relative_return |    298 |                       5 |                         2 |         100 |           298 |
| liquidity_like|price_return_like     | signed_spread       | L1_cross_sectional_relative_return |    298 |                       5 |                         2 |         100 |           298 |
| liquidity_like|price_return_like     | signed_spread       | L3_liquidity_tier_relative_return  |    298 |                       5 |                         2 |         100 |           298 |
| open_interest_like|price_return_like | relative_shock      | L1_cross_sectional_relative_return |    298 |                       5 |                         2 |         100 |           298 |
| liquidity_like|price_return_like     | sub                 | L1_cross_sectional_relative_return |    298 |                       5 |                         2 |         100 |           298 |
| liquidity_like|price_return_like     | sub                 | L3_liquidity_tier_relative_return  |    298 |                       5 |                         2 |         100 |           298 |
| liquidity_like|price_return_like     | spread_rank         | L3_liquidity_tier_relative_return  |    298 |                       5 |                         2 |         100 |           298 |
| liquidity_like|price_return_like     | spread_rank         | L0_raw_forward_return              |    298 |                       5 |                         2 |         100 |           298 |
| open_interest_like|price_return_like | safe_div_abs        | L3_liquidity_tier_relative_return  |    298 |                       5 |                         2 |         100 |           298 |
| open_interest_like|price_return_like | relative_shock      | L0_raw_forward_return              |    298 |                       5 |                         2 |         100 |           298 |
| open_interest_like|price_return_like | mean_reversion_gate | L3_liquidity_tier_relative_return  |    298 |                       5 |                         2 |         100 |           298 |
| open_interest_like|price_return_like | mean_reversion_gate | L1_cross_sectional_relative_return |    298 |                       5 |                         2 |         100 |           298 |
| positioning_like|price_return_like   | spread_rank         | L3_liquidity_tier_relative_return  |    298 |                       5 |                         2 |         100 |           298 |
| positioning_like|price_return_like   | mean_reversion_gate | L1_cross_sectional_relative_return |    298 |                       5 |                         2 |         100 |           298 |
| positioning_like|price_return_like   | mean_reversion_gate | L0_raw_forward_return              |    298 |                       5 |                         2 |         100 |           298 |
| positioning_like|price_return_like   | relative_shock      | L0_raw_forward_return              |    298 |                       5 |                         2 |         100 |           298 |
| open_interest_like|price_return_like | sub                 | L0_raw_forward_return              |    298 |                       5 |                         2 |         100 |           298 |
| open_interest_like|price_return_like | sub                 | L3_liquidity_tier_relative_return  |    298 |                       5 |                         2 |         100 |           298 |
| open_interest_like|price_return_like | spread_rank         | L1_cross_sectional_relative_return |    298 |                       5 |                         2 |         100 |           298 |
| open_interest_like|price_return_like | spread_rank         | L0_raw_forward_return              |    298 |                       5 |                         2 |         100 |           298 |
| open_interest_like|price_return_like | smooth_mul          | L1_cross_sectional_relative_return |    298 |                       5 |                         2 |         100 |           298 |
| open_interest_like|price_return_like | smooth_mul          | L3_liquidity_tier_relative_return  |    298 |                       5 |                         2 |         100 |           298 |
| open_interest_like|price_return_like | signed_spread       | L3_liquidity_tier_relative_return  |    298 |                       5 |                         2 |         100 |           298 |
| open_interest_like|price_return_like | signed_spread       | L0_raw_forward_return              |    298 |                       5 |                         2 |         100 |           298 |
| positioning_like|price_return_like   | sub                 | L1_cross_sectional_relative_return |    298 |                       5 |                         2 |         100 |           298 |
| positioning_like|price_return_like   | spread_rank         | L0_raw_forward_return              |    298 |                       5 |                         2 |         100 |           298 |
| positioning_like|price_return_like   | smooth_mul          | L1_cross_sectional_relative_return |    298 |                       5 |                         2 |         100 |           298 |
| volatility_like|basis_premium_like   | smooth_mul          | L1_cross_sectional_relative_return |    298 |                       1 |                         9 |         100 |           298 |
| taker_flow_like|basis_premium_like   | spread_rank         | L3_liquidity_tier_relative_return  |    298 |                       1 |                         9 |         100 |           298 |
| volatility_like|basis_premium_like   | mean_reversion_gate | L3_liquidity_tier_relative_return  |    298 |                       1 |                         9 |         100 |           298 |
| taker_flow_like|basis_premium_like   | sub                 | L1_cross_sectional_relative_return |    298 |                       1 |                         9 |         100 |           298 |
| taker_flow_like|basis_premium_like   | sub                 | L0_raw_forward_return              |    298 |                       1 |                         9 |         100 |           298 |
| taker_flow_like|basis_premium_like   | signed_spread       | L1_cross_sectional_relative_return |    298 |                       1 |                         9 |         100 |           298 |
| volatility_like|basis_premium_like   | relative_shock      | L1_cross_sectional_relative_return |    298 |                       1 |                         9 |         100 |           298 |
| volatility_like|basis_premium_like   | mean_reversion_gate | L1_cross_sectional_relative_return |    298 |                       1 |                         9 |         100 |           298 |
| volatility_like|basis_premium_like   | spread_rank         | L1_cross_sectional_relative_return |    298 |                       1 |                         9 |         100 |           298 |
| volatility_like|basis_premium_like   | sub                 | L0_raw_forward_return              |    298 |                       1 |                         9 |         100 |           298 |
| volatility_like|basis_premium_like   | signed_spread       | L3_liquidity_tier_relative_return  |    298 |                       1 |                         9 |         100 |           298 |
| volatility_like|basis_premium_like   | signed_spread       | L0_raw_forward_return              |    298 |                       1 |                         9 |         100 |           298 |
| volatility_like|basis_premium_like   | safe_div_abs        | L3_liquidity_tier_relative_return  |    298 |                       1 |                         9 |         100 |           298 |
| volatility_like|basis_premium_like   | sub                 | L3_liquidity_tier_relative_return  |    298 |                       1 |                         9 |         100 |           298 |
| volatility_like|basis_premium_like   | spread_rank         | L0_raw_forward_return              |    298 |                       1 |                         9 |         100 |           298 |
| volatility_like|basis_premium_like   | smooth_mul          | L3_liquidity_tier_relative_return  |    298 |                       1 |                         9 |         100 |           298 |
| taker_flow_like|basis_premium_like   | signed_spread       | L0_raw_forward_return              |    298 |                       1 |                         9 |         100 |           298 |
| taker_flow_like|basis_premium_like   | safe_div_abs        | L0_raw_forward_return              |    298 |                       1 |                         9 |         100 |           298 |
| taker_flow_like|basis_premium_like   | mean_reversion_gate | L3_liquidity_tier_relative_return  |    298 |                       1 |                         9 |         100 |           298 |
| taker_flow_like|basis_premium_like   | relative_shock      | L1_cross_sectional_relative_return |    298 |                       1 |                         9 |         100 |           298 |
| positioning_like|price_return_like   | sub                 | L3_liquidity_tier_relative_return  |    298 |                       5 |                         2 |         100 |           298 |
| volatility_like|basis_premium_like   | relative_shock      | L0_raw_forward_return              |    298 |                       1 |                         9 |         100 |           298 |
| taker_flow_like|basis_premium_like   | relative_shock      | L3_liquidity_tier_relative_return  |    298 |                       1 |                         9 |         100 |           298 |
| taker_flow_like|basis_premium_like   | mean_reversion_gate | L0_raw_forward_return              |    298 |                       1 |                         9 |         100 |           298 |
| basis_premium_like|price_return_like | signed_spread       | L3_liquidity_tier_relative_return  |    297 |                       5 |                         2 |         100 |           297 |

## Boundary

```text
blueprint generation executed: true
numeric replay executed: false
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```
