# CRYPTO A7AH-1 ORDINARY ALPHA OBJECTIVE REWRITE CONTRACT

Generated: 2026-05-29T08:59:32Z

## Decision

`PASS_A7AH1_ORDINARY_ALPHA_OBJECTIVE_REWRITE_CONTRACT_READY_FOR_DRY_RERANK`

A7AH-1 rewrites the ordinary-alpha selector target after A7AG5 found no L0/L1 translation. It is contract-only and does not execute search or replay.

## Manifest

```json
{
  "authorizes_a7ah1d_dry_rerank": true,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search_execution": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7AH1_ORDINARY_ALPHA_OBJECTIVE_REWRITE_CONTRACT_READY_FOR_DRY_RERANK",
  "executes_contract_only": true,
  "executes_formula_generation": false,
  "executes_replay": false,
  "executes_search": false,
  "executes_training": false,
  "generated_at": "2026-05-29T08:59:32Z",
  "input_a7ah0_decision": "PASS_A7AH0_POST_A7AG_ROLE_SPLIT_READY_FOR_A7AH1_A7AH2_CONTRACTS",
  "stage": "A7AH-1",
  "uses_may": false
}
```

## Label Policy

```json
{
  "diagnostic_only_labels": [
    "L5_vol_adjusted_return"
  ],
  "forbidden_as_primary_alpha_labels": [
    "L5_vol_adjusted_return",
    "L6_downside_avoidance",
    "L7_ranked_future_return"
  ],
  "ordinary_alpha_candidate_requires": [
    "positive_L0_or_L1_response",
    "control_ratio_lt_1_in_each_pre_may_split",
    "one_bar_lag_survival",
    "cost5_proxy_survival",
    "nonoverlap_median_tstat_floor_gt_0",
    "not_concentration_dominated"
  ],
  "primary_alpha_labels": [
    "L0_raw_forward_return",
    "L1_cross_sectional_relative_return"
  ],
  "risk_defense_only_labels": [
    "L6_downside_avoidance"
  ],
  "secondary_diagnostic_labels": [
    "L2_BTC_ETH_beta_residual_return",
    "L3_liquidity_tier_relative_return"
  ]
}
```

## Selector Policy

```json
{
  "dry_rerank_input": "existing A7AG2/A7AG3 queue and metrics only",
  "hard_reject": [
    "no_L0_or_L1_positive_split",
    "control_ratio_ge_1",
    "wrong_lag_or_shuffle_control_stronger",
    "same_skeleton_over_cap",
    "same_field_family_over_cap"
  ],
  "score_components_allowed": [
    "L0_L1_oriented_spread",
    "matched_control_margin",
    "one_bar_lag_survival",
    "cost5_proxy_survival",
    "nonoverlap_robustness",
    "field_family_diversity",
    "skeleton_diversity"
  ],
  "score_components_forbidden": [
    "L5_as_primary_reward",
    "L6_as_primary_reward",
    "May",
    "ranked_label_only_reward"
  ]
}
```

## Objective Families

| objective_id                            | allowed_seed_families                  | primary_labels                                            | diagnostic_labels                                                                          | forbidden_primary_labels                                               | status                      |
|:----------------------------------------|:---------------------------------------|:----------------------------------------------------------|:-------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------|:----------------------------|
| O0_basis_premium_ordinary_alpha         | basis_premium                          | L0_raw_forward_return\|L1_cross_sectional_relative_return | L2_BTC_ETH_beta_residual_return\|L3_liquidity_tier_relative_return\|L5_vol_adjusted_return | L5_vol_adjusted_return\|L6_downside_avoidance\|L7_ranked_future_return | allowed_for_dry_rerank_only |
| O1_positioning_ordinary_alpha           | positioning\|open_interest_interaction | L0_raw_forward_return\|L1_cross_sectional_relative_return | L2_BTC_ETH_beta_residual_return\|L3_liquidity_tier_relative_return                         | L6_downside_avoidance\|L7_ranked_future_return                         | allowed_for_dry_rerank_only |
| O2_vol_adjusted_to_ordinary_translation | basis_premium\|volatility              | L0_raw_forward_return\|L1_cross_sectional_relative_return | L5_vol_adjusted_return                                                                     | L5_vol_adjusted_return                                                 | translation_diagnostic_only |

## Boundary

```text
A7AH-1 restores ordinary alpha discipline: L0/L1 must be primary.
Vol-adjusted/downside/ranked labels can diagnose but cannot carry ordinary alpha promotion.
No formula search, large search, alpha proof, shadow, paper, or live is authorized.
```
