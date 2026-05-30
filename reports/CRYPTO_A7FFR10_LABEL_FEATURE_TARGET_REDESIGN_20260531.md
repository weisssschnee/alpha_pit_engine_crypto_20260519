# CRYPTO A7FF-R10 LABEL / FEATURE TARGET REDESIGN

Generated: 2026-05-30T18:38:02Z

## Decision

`PASS_A7FFR10_LABEL_FEATURE_TARGET_REDESIGN_READY_FOR_A7FF49_NO_SEARCH_AUTH`

A7FF-R10 converts the A7FF-47 L5-only hold into a stricter target policy. It does not generate formulas, run replay, or search.

## Manifest

```json
{
  "authorizes_a7ff49_existing_map_non_l5_mining": true,
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FFR10_LABEL_FEATURE_TARGET_REDESIGN_READY_FOR_A7FF49_NO_SEARCH_AUTH",
  "executes_generation": false,
  "executes_numeric_probe": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T18:38:02Z",
  "source_a7ff47_decision": "HOLD_A7FF47_LABEL_TRANSLATION_FAIL_L5_ONLY",
  "stage": "A7FF-R10",
  "uses_may": false,
  "warnings": [
    "current_frozen_pool_is_l5_only_diagnostic"
  ]
}
```

## Failure Attribution

| failure_layer   | evidence                                                                     | impact                                                                                              | required_repair                                                       |
|:----------------|:-----------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------|
| label_target    | strict translations exist only on L5_vol_adjusted_return                     | current frozen pool is diagnostic-only and cannot become alpha/search input                         | non-L5-first candidate mining from existing numeric maps              |
| selector_reward | bounded replay rows are control-clean but L5-only                            | selector can over-reward volatility-adjusted labels while raw/relative return translation is absent | hard require L0/L1/L3 evidence before replay promotion                |
| feature_role    | basis/funding and regime/price clues behave as risk/vol-adjusted diagnostics | do not treat L5-only clues as ordinary-alpha candidates                                             | demote L5-only features to diagnostic or risk-adjusted state features |

## Label Target Policy

| label_family                       | required_for_promotion   | role                                |   minimum_rows |
|:-----------------------------------|:-------------------------|:------------------------------------|---------------:|
| L0_raw_forward_return              | True                     | primary_non_l5_translation          |              2 |
| L1_cross_sectional_relative_return | True                     | primary_non_l5_translation          |              2 |
| L3_liquidity_tier_relative_return  | True                     | primary_non_l5_translation          |              2 |
| L5_vol_adjusted_return             | False                    | supporting_risk_adjusted_diagnostic |              0 |
| L7_ranked_future_return            | False                    | diagnostic_only_not_alpha_proof     |              0 |

## Allowed Source Maps

| source_stage   | path                                                                          | allowed   | use                                                  |
|:---------------|:------------------------------------------------------------------------------|:----------|:-----------------------------------------------------|
| A7FF-42        | runtime/a7ff42_family_balanced_numeric/a7ff42_control_strict_non_l7_clues.csv | True      | mine existing non-L5 strict clues without generation |
| A7FF-45        | runtime/a7ff45_bounded_deep_replay/a7ff45_label_response_metrics.csv          | True      | negative reference for L5-only frozen pool           |
| A7FF-47        | runtime/a7ff47_portfolio_microreplay/a7ff47_label_translation_map.csv         | True      | label translation failure attribution                |

## A7FF-47 Label Summary

| label_family                       |   rows |   blueprints |   numeric_clues |   strict_translations |   non_l5_strict_translations |   median_control_ratio |   min_cost10 |   max_cost10 |   min_robust_floor |
|:-----------------------------------|-------:|-------------:|----------------:|----------------------:|-----------------------------:|-----------------------:|-------------:|-------------:|-------------------:|
| L5_vol_adjusted_return             |     28 |            7 |               9 |                     8 |                            0 |               1.8799   |   -0.601691  |  0.442532    |           -2.62562 |
| L0_raw_forward_return              |     28 |            7 |               7 |                     0 |                            0 |               1.63847  |   -0.01118   |  0.00116388  |           -2.31907 |
| L1_cross_sectional_relative_return |     28 |            7 |               8 |                     0 |                            0 |               1.51658  |   -0.01118   |  0.00116388  |           -2.31907 |
| L3_liquidity_tier_relative_return  |     28 |            7 |               6 |                     0 |                            0 |               1.48722  |   -0.0104918 |  0.000946879 |           -2.5923  |
| L7_ranked_future_return            |     28 |            7 |               0 |                     0 |                            0 |               0.512817 |   -0.0164685 |  0.0540406   |           -2.11586 |

## A7FF-47 Family Label Summary

| semantic_pair                   | label_family                       |   rows |   blueprints |   strict_translations |   non_l5_strict_translations |   median_control_ratio |   min_cost10 |   max_cost10 |
|:--------------------------------|:-----------------------------------|-------:|-------------:|----------------------:|-----------------------------:|-----------------------:|-------------:|-------------:|
| funding_like|basis_premium_like | L0_raw_forward_return              |     16 |            4 |                     0 |                            0 |               2.57503  | -0.01118     |  0.00116388  |
| funding_like|basis_premium_like | L1_cross_sectional_relative_return |     16 |            4 |                     0 |                            0 |               2.67818  | -0.01118     |  0.00116388  |
| funding_like|basis_premium_like | L3_liquidity_tier_relative_return  |     16 |            4 |                     0 |                            0 |               2.59116  | -0.0104918   |  0.000946879 |
| funding_like|basis_premium_like | L5_vol_adjusted_return             |     16 |            4 |                     5 |                            0 |               2.10608  | -0.601691    |  0.442532    |
| funding_like|basis_premium_like | L7_ranked_future_return            |     16 |            4 |                     0 |                            0 |               0.918862 | -0.0164685   |  0.0540406   |
| regime_state|price_return_like  | L0_raw_forward_return              |     12 |            3 |                     0 |                            0 |               1.29629  | -0.00193049  | -0.000673995 |
| regime_state|price_return_like  | L1_cross_sectional_relative_return |     12 |            3 |                     0 |                            0 |               0.966281 | -0.00193049  | -0.000673995 |
| regime_state|price_return_like  | L3_liquidity_tier_relative_return  |     12 |            3 |                     0 |                            0 |               1.11618  | -0.0018322   | -0.000721642 |
| regime_state|price_return_like  | L5_vol_adjusted_return             |     12 |            3 |                     3 |                            0 |               1.55112  | -0.000668797 |  0.0742942   |
| regime_state|price_return_like  | L7_ranked_future_return            |     12 |            3 |                     0 |                            0 |               0.473399 |  0.0195092   |  0.0508103   |

## Next Contract: A7FF-49

```json
{
  "allowed_inputs": [
    {
      "allowed": true,
      "path": "runtime/a7ff42_family_balanced_numeric/a7ff42_control_strict_non_l7_clues.csv",
      "source_stage": "A7FF-42",
      "use": "mine existing non-L5 strict clues without generation"
    },
    {
      "allowed": true,
      "path": "runtime/a7ff45_bounded_deep_replay/a7ff45_label_response_metrics.csv",
      "source_stage": "A7FF-45",
      "use": "negative reference for L5-only frozen pool"
    },
    {
      "allowed": true,
      "path": "runtime/a7ff47_portfolio_microreplay/a7ff47_label_translation_map.csv",
      "source_stage": "A7FF-47",
      "use": "label translation failure attribution"
    }
  ],
  "name": "existing-map non-L5 candidate mining",
  "not_authorized": [
    "formula_search",
    "large_search",
    "alpha_proof",
    "shadow",
    "paper",
    "live"
  ],
  "requirements": {
    "allow_l5_only_as_diagnostic": true,
    "control_ratio_max": 0.8,
    "min_candidate_rows": 6,
    "min_semantic_families": 2,
    "no_new_generation": true,
    "no_search": true,
    "require_non_l5_labels": [
      "L0_raw_forward_return",
      "L1_cross_sectional_relative_return",
      "L3_liquidity_tier_relative_return"
    ]
  },
  "stage": "A7FF-49"
}
```

## Boundary

```text
generation executed: false
numeric probe executed: false
replay executed: false
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```
