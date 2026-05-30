# CRYPTO A7FF-22 LABEL-BALANCED EXPANSION CONTRACT

Generated: 2026-05-30T05:15:14Z

## Decision

`PASS_A7FF22_LABEL_BALANCED_EXPANSION_CONTRACT_READY_FOR_A7FF23`

A7FF-22 defines a larger label-balanced expansion route based on the confirmed A7FF-21 external selector. It does not execute generation, replay, or search. It only authorizes the next contract stage for controlled A7FF-23 generation planning.

## Manifest

```json
{
  "authorizes_a7ff23_label_balanced_generation_contract": true,
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FF22_LABEL_BALANCED_EXPANSION_CONTRACT_READY_FOR_A7FF23",
  "executes_generation": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T05:15:14Z",
  "generation_budget": {
    "company_numeric_shard_size": 120,
    "company_numeric_shards": 8,
    "company_numeric_wave_blueprints": 960,
    "deep_diagnostic_target": 64,
    "external_selector_label_quota": 60,
    "external_selector_target_rows": 240,
    "generated_blueprints_target": 9600,
    "materialization_target": 960,
    "max_parallel_company_shards": 2
  },
  "seed_rows": 64,
  "seed_unique_blueprints": 39,
  "source_a7ff21_decision": "PASS_A7FF21_EXTERNAL_CONFIRMATION_SELECTOR_READY_FOR_A7FF22_WITH_BLUEPRINT_DIVERSITY_WARNING",
  "stage": "A7FF-22-LABEL-BALANCED-EXPANSION-CONTRACT",
  "uses_may": false
}
```

## Generation Budget

```json
{
  "company_numeric_shard_size": 120,
  "company_numeric_shards": 8,
  "company_numeric_wave_blueprints": 960,
  "deep_diagnostic_target": 64,
  "external_selector_label_quota": 60,
  "external_selector_target_rows": 240,
  "generated_blueprints_target": 9600,
  "materialization_target": 960,
  "max_parallel_company_shards": 2
}
```

## Selector Policy

```json
{
  "forbid_a7ff8_internal_selected_queue_as_source_of_truth": true,
  "l3_policy": "cost5_or_better_allowed; strict_cost10_preferred_but_not_required",
  "label_families": [
    "L0_raw_forward_return",
    "L1_cross_sectional_relative_return",
    "L3_liquidity_tier_relative_return",
    "L5_vol_adjusted_return"
  ],
  "label_quota_share": 0.25,
  "max_top_label_share": 0.3,
  "max_top_motif_share": 0.35,
  "max_top_semantic_share": 0.35,
  "min_cost5_or_better_share": 0.75,
  "min_strict_cost10_rows_after_selection": 80,
  "min_unique_blueprints_after_selection": 120,
  "must_use_external_label_balanced_selector": true
}
```

## Label Policy

| label_family                       |   seed_rows |   unique_blueprints |   strict_cost10_rows |   cost5_or_better_rows |
|:-----------------------------------|------------:|--------------------:|---------------------:|-----------------------:|
| L0_raw_forward_return              |          16 |                  14 |                    6 |                     16 |
| L1_cross_sectional_relative_return |          16 |                  16 |                    8 |                     16 |
| L3_liquidity_tier_relative_return  |          16 |                  16 |                    0 |                     16 |
| L5_vol_adjusted_return             |          16 |                  14 |                   16 |                     16 |

## Semantic Policy

| semantic_pair                          |   seed_rows |   unique_blueprints |
|:---------------------------------------|------------:|--------------------:|
| basis_premium_like\|volatility_like    |          20 |                  12 |
| basis_premium_like\|positioning_like   |          19 |                  12 |
| basis_premium_like\|basis_premium_like |          17 |                  11 |
| basis_premium_like\|price_like         |           8 |                   4 |

## Motif Policy

| motif        |   seed_rows |   unique_blueprints |
|:-------------|------------:|--------------------:|
| sub          |          20 |                  10 |
| safe_div_abs |          19 |                  12 |
| gated_sign   |          10 |                   6 |
| spread_rank  |           8 |                   7 |
| mul          |           7 |                   4 |

## Allowed Families

```json
[
  {
    "family": "G0_basis_premium_volatility",
    "label_targets": [
      "L0_raw_forward_return",
      "L1_cross_sectional_relative_return",
      "L3_liquidity_tier_relative_return",
      "L5_vol_adjusted_return"
    ],
    "motifs": [
      "sub",
      "safe_div_abs",
      "gated_sign",
      "spread_rank",
      "mul"
    ],
    "semantic_pairs": [
      "basis_premium_like|volatility_like"
    ]
  },
  {
    "family": "G1_basis_premium_positioning",
    "label_targets": [
      "L0_raw_forward_return",
      "L1_cross_sectional_relative_return",
      "L3_liquidity_tier_relative_return",
      "L5_vol_adjusted_return"
    ],
    "motifs": [
      "safe_div_abs",
      "sub",
      "gated_sign",
      "spread_rank",
      "mul"
    ],
    "semantic_pairs": [
      "basis_premium_like|positioning_like"
    ]
  },
  {
    "family": "G2_basis_premium_relative_value",
    "label_targets": [
      "L0_raw_forward_return",
      "L1_cross_sectional_relative_return",
      "L3_liquidity_tier_relative_return",
      "L5_vol_adjusted_return"
    ],
    "motifs": [
      "sub",
      "spread_rank",
      "safe_div_abs",
      "gated_sign"
    ],
    "semantic_pairs": [
      "basis_premium_like|basis_premium_like"
    ]
  },
  {
    "family": "G3_basis_premium_price_state",
    "label_targets": [
      "L0_raw_forward_return",
      "L1_cross_sectional_relative_return",
      "L3_liquidity_tier_relative_return",
      "L5_vol_adjusted_return"
    ],
    "motifs": [
      "sub",
      "gated_sign",
      "mul",
      "safe_div_abs"
    ],
    "semantic_pairs": [
      "basis_premium_like|price_like"
    ]
  }
]
```

## Forbidden

```json
[
  "A7FF8_internal_selected_queue_as_final_selector",
  "L5_only_selector_target",
  "L7_ranked_future_return_as_alpha_proof_label",
  "May_in_generation_or_selector_or_mutation",
  "full_open_formula_search",
  "alpha_proof_shadow_paper_live"
]
```

## Boundary

- Uses May: `false`
- Executes generation: `false`
- Executes replay: `false`
- Executes search: `false`
- Authorizes alpha proof / shadow / paper / live: `false`
