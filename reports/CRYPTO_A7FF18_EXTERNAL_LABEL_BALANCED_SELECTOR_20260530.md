# CRYPTO A7FF-18 EXTERNAL LABEL-BALANCED SELECTOR

Generated: 2026-05-30T04:55:34Z

## Decision

`PASS_A7FF18_EXTERNAL_LABEL_BALANCED_SELECTOR_READY_FOR_A7FF19`

A7FF-18 replaces the A7FF-8 internal selected queue with an external label-balanced selector over the A7FF-16 numeric clue surface. It is a selector repair stage, not generation, replay, search, alpha proof, shadow, paper, or live execution.

## Manifest

```json
{
  "authorizes_a7ff19_external_selector_confirmation_contract": true,
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "candidate_rows": 402,
  "candidate_unique_blueprints": 94,
  "decision": "PASS_A7FF18_EXTERNAL_LABEL_BALANCED_SELECTOR_READY_FOR_A7FF19",
  "executes_generation": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T04:55:34Z",
  "selected_cost5_or_better_rows": 80,
  "selected_label_families": 4,
  "selected_rows": 80,
  "selected_strict_cost10_rows": 41,
  "selected_top_label_share": 0.25,
  "selected_top_motif_share": 0.3125,
  "selected_top_semantic_share": 0.3125,
  "selected_unique_blueprints": 56,
  "source_a7ff17_decision": "HOLD_A7FF17_INTERNAL_SELECTOR_LABEL_CONCENTRATION_PERSISTS",
  "stage": "A7FF-18-EXTERNAL-LABEL-BALANCED-SELECTOR",
  "uses_may": false
}
```

## Candidate Label / Cost Tier Summary

| label_family                       | cost_tier                |   rows |   unique_blueprints |
|:-----------------------------------|:-------------------------|-------:|--------------------:|
| L0_raw_forward_return              | cost2_numeric_diagnostic |     34 |                  32 |
| L0_raw_forward_return              | cost5_followup           |     47 |                  45 |
| L0_raw_forward_return              | strict_cost10            |     11 |                  11 |
| L1_cross_sectional_relative_return | cost2_numeric_diagnostic |     34 |                  32 |
| L1_cross_sectional_relative_return | cost5_followup           |     52 |                  46 |
| L1_cross_sectional_relative_return | strict_cost10            |     11 |                  11 |
| L3_liquidity_tier_relative_return  | cost2_numeric_diagnostic |     40 |                  39 |
| L3_liquidity_tier_relative_return  | cost5_followup           |     49 |                  47 |
| L3_liquidity_tier_relative_return  | strict_cost10            |      2 |                   2 |
| L5_vol_adjusted_return             | cost2_numeric_diagnostic |     11 |                  10 |
| L5_vol_adjusted_return             | cost5_followup           |     11 |                  11 |
| L5_vol_adjusted_return             | strict_cost10            |    100 |                  66 |

## Selected Label / Cost Tier Summary

| label_family                       | cost_tier      |   rows |   unique_blueprints |
|:-----------------------------------|:---------------|-------:|--------------------:|
| L0_raw_forward_return              | cost5_followup |      9 |                   9 |
| L0_raw_forward_return              | strict_cost10  |     11 |                  11 |
| L1_cross_sectional_relative_return | cost5_followup |     10 |                  10 |
| L1_cross_sectional_relative_return | strict_cost10  |     10 |                  10 |
| L3_liquidity_tier_relative_return  | cost5_followup |     20 |                  20 |
| L5_vol_adjusted_return             | strict_cost10  |     20 |                  20 |

## Selected Semantic Summary

| semantic_pair                          |   rows |
|:---------------------------------------|-------:|
| basis_premium_like\|positioning_like   |     25 |
| basis_premium_like\|volatility_like    |     25 |
| basis_premium_like\|basis_premium_like |     23 |
| basis_premium_like\|price_like         |      7 |

## Selected Motif Summary

| motif              |   rows |
|:-------------------|-------:|
| sub                |     25 |
| safe_div_abs       |     25 |
| mul                |     10 |
| gated_sign         |     10 |
| spread_rank        |      9 |
| smooth_interaction |      1 |

## Boundary

- Uses May: `false`
- Executes generation: `false`
- Executes replay: `false`
- Executes search: `false`
- Authorizes alpha proof / shadow / paper / live: `false`
