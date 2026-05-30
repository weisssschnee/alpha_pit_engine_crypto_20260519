# CRYPTO A7FF-23R DERIVED FACTOR EXPANSION CONTRACT

Generated: 2026-05-30T06:05:39Z

## Decision

`PASS_A7FF23R_DERIVED_FACTOR_EXPANSION_CONTRACT_READY_FOR_A7FF24R_PLAN`

A7FF-23R replaces the old A7FF-23 execution path. It defines a heavier derived factor expansion from the A7FF-R ontology/operator/pair/promotion redesign. It does not execute generation, replay, search, or alpha proof.

## Manifest

```json
{
  "allowed_pair_count": 837,
  "authorizes_a7ff24r_company_execution_plan_contract": true,
  "authorizes_alpha_proof": false,
  "authorizes_old_a7ff23_execution": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FF23R_DERIVED_FACTOR_EXPANSION_CONTRACT_READY_FOR_A7FF24R_PLAN",
  "executes_generation": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T06:05:39Z",
  "generation_budget": {
    "company_numeric_shard_size": 200,
    "company_numeric_shards": 12,
    "company_numeric_wave_blueprints": 2400,
    "deep_diagnostic_target": 128,
    "external_label_balanced_selector_target_rows": 640,
    "generated_blueprints_target": 24000,
    "materialization_target": 3000,
    "max_parallel_company_shards": 4,
    "minimum_selected_label_families": 4,
    "minimum_selected_semantic_families": 4,
    "minimum_selected_signal_vector_clusters": 8
  },
  "seed_route_counts": {
    "exploratory_signal_seed": 4,
    "modifier_only_seed": 73,
    "primary_signal_seed": 1
  },
  "source_r5_decision": "PASS_A7FFR5_PROMOTION_REDESIGN_READY_BUT_SEARCH_STILL_HOLD",
  "source_seed_preview_rows": 78,
  "source_signal_semantic_family_count": 3,
  "stage": "A7FF-23R-DERIVED-FACTOR-EXPANSION-CONTRACT",
  "uses_may": false
}
```

## Generation Budget

```json
{
  "company_numeric_shard_size": 200,
  "company_numeric_shards": 12,
  "company_numeric_wave_blueprints": 2400,
  "deep_diagnostic_target": 128,
  "external_label_balanced_selector_target_rows": 640,
  "generated_blueprints_target": 24000,
  "materialization_target": 3000,
  "max_parallel_company_shards": 4,
  "minimum_selected_label_families": 4,
  "minimum_selected_semantic_families": 4,
  "minimum_selected_signal_vector_clusters": 8
}
```

## Generation Levels

| level                          |   target_blueprints | source                                           | purpose                                                                 |
|:-------------------------------|--------------------:|:-------------------------------------------------|:------------------------------------------------------------------------|
| L1_single_field_transform      |                5000 | ordinary_alpha_seed + exploratory_signal_seed    | probe whether single-source transforms have non-L7 response             |
| L2_typed_two_field_interaction |               12000 | A7FF-R3 allow/probe priority pairs               | expand OI/funding/liquidity/vol/price interactions without open grammar |
| L3_state_conditioned_feature   |                5000 | modifier_only_seed as condition/neutralizer only | test regime/state conditioning without standalone state alpha           |
| L4_factor_candidate_probe      |                2000 | response-backed candidates from L1-L3            | produce selector-ready factor probes                                    |

## Seed Family Summary

| semantic_type_v3   | a7ff23r_seed_route      |   field_count |   standalone_alpha_allowed |   interaction_allowed |   non_l7_candidate_rows |   primitive_candidate_rows |   best_control_ratio |
|:-------------------|:------------------------|--------------:|---------------------------:|----------------------:|------------------------:|---------------------------:|---------------------:|
| basis_premium_like | exploratory_signal_seed |             1 |                          0 |                     1 |                       0 |                          1 |             0.791438 |
| price_like         | exploratory_signal_seed |             1 |                          0 |                     1 |                       0 |                          4 |             0.254317 |
| volatility_like    | exploratory_signal_seed |             2 |                          0 |                     2 |                       0 |                          4 |             0.879498 |
| basis_premium_like | modifier_only_seed      |            18 |                          0 |                    18 |                       0 |                          0 |             0.107775 |
| funding_like       | modifier_only_seed      |             6 |                          0 |                     6 |                       0 |                          0 |             0.607009 |
| generic_numeric    | modifier_only_seed      |             9 |                          0 |                     9 |                       0 |                          0 |           nan        |
| liquidity_like     | modifier_only_seed      |            11 |                          0 |                    11 |                       0 |                          0 |             2.14076  |
| positioning_like   | modifier_only_seed      |            15 |                          0 |                    15 |                       0 |                          0 |             0.688118 |
| price_like         | modifier_only_seed      |             2 |                          0 |                     2 |                       0 |                          0 |             6.21288  |
| state_or_taxonomy  | modifier_only_seed      |             8 |                          0 |                     8 |                       0 |                          0 |             0.997123 |
| volatility_like    | modifier_only_seed      |             4 |                          0 |                     4 |                       0 |                          0 |           nan        |
| basis_premium_like | primary_signal_seed     |             1 |                          1 |                     1 |                       2 |                          2 |             0.141289 |

## Pair Family Summary

| semantic_pair                          | a7ff23r_pair_route              |   pair_count |   modifier_guard_pairs |
|:---------------------------------------|:--------------------------------|-------------:|-----------------------:|
| basis_premium_like\|positioning_like   | exploratory_generation_priority |          281 |                    281 |
| basis_premium_like\|funding_like       | exploratory_generation_priority |          118 |                    118 |
| basis_premium_like\|volatility_like    | exploratory_generation_priority |          110 |                    110 |
| funding_like\|positioning_like         | exploratory_generation_priority |           90 |                     90 |
| basis_premium_like\|price_like         | exploratory_generation_priority |           54 |                     54 |
| liquidity_like\|volatility_like        | exploratory_generation_priority |           52 |                     52 |
| basis_premium_like\|positioning_like   | generation_priority             |           19 |                     19 |
| basis_premium_like\|liquidity_like     | generation_priority             |           15 |                     15 |
| liquidity_like\|volatility_like        | generation_priority             |           14 |                     14 |
| basis_premium_like\|basis_premium_like | generation_priority             |           14 |                     13 |
| positioning_like\|volatility_like      | generation_priority             |           12 |                     12 |
| basis_premium_like\|volatility_like    | generation_priority             |           10 |                      6 |
| volatility_like\|volatility_like       | generation_priority             |            7 |                      6 |
| price_like\|volatility_like            | generation_priority             |            6 |                      4 |
| basis_premium_like\|generic_numeric    | generation_priority             |            6 |                      6 |
| basis_premium_like\|price_like         | generation_priority             |            6 |                      4 |
| generic_numeric\|volatility_like       | generation_priority             |            6 |                      6 |
| basis_premium_like\|state_or_taxonomy  | generation_priority             |            6 |                      6 |
| state_or_taxonomy\|volatility_like     | generation_priority             |            4 |                      4 |
| basis_premium_like\|funding_like       | generation_priority             |            2 |                      2 |
| funding_like\|volatility_like          | generation_priority             |            2 |                      2 |
| liquidity_like\|price_like             | generation_priority             |            2 |                      2 |
| price_like\|price_like                 | generation_priority             |            1 |                      1 |

## Selector Policy

```json
{
  "allowed_labels": [
    "L0_raw_forward_return",
    "L1_cross_sectional_relative_return",
    "L2_BTC_ETH_beta_residual_return",
    "L3_liquidity_tier_relative_return",
    "L4_latent_state_relative_return",
    "L5_vol_adjusted_return",
    "L6_downside_avoidance_or_crash_beta"
  ],
  "control_ratio_diagnostic_gate": 1.0,
  "control_ratio_promotion_gate": 0.8,
  "forbidden_selector": [
    "A7FF8_internal_selected_queue",
    "raw_pass_count_only",
    "L7_only_rank_label"
  ],
  "max_top_label_share": 0.25,
  "max_top_motif_share": 0.3,
  "max_top_pair_family_share": 0.3,
  "max_top_semantic_family_share": 0.35,
  "min_non_l7_selected_share": 0.75,
  "ranked_label_policy": "L7 diagnostic only; cannot be sole promotion evidence",
  "selector": "external_label_balanced_selector_v2",
  "uses_may_in_selector": false
}
```

## Blocked Policy

```json
{
  "allowed_next": [
    "A7FF24R_company_execution_plan_contract",
    "A7FF24R_dry_generation_plan"
  ],
  "blocked": [
    "old_A7FF23_direct_expansion_execution",
    "full_open_formula_search",
    "A7FF8_internal_queue_as_source_of_truth",
    "L7_ranked_future_return_only_promotion",
    "risk_or_regime_field_as_standalone_alpha",
    "May_in_generation_selector_mutation_or_thresholds",
    "alpha_proof_shadow_paper_live"
  ]
}
```

## Reproducibility

```json
{
  "commands": [
    "G:\\PythonProject\\.venv\\Scripts\\python.exe scripts\\crypto_a7ff23r_derived_factor_expansion_contract.py"
  ],
  "continuation": "Implement A7FF24R company execution plan only from this contract; do not execute old A7FF23.",
  "experiment_id": "20260530_a7ff23r_derived_factor_expansion_contract",
  "input_files": [
    "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ffr1_field_ontology_v3\\a7ffr1_field_ontology_v3.csv",
    "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ffr2_operator_probing_v2\\a7ffr2_operator_probe_policy.csv",
    "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ffr3_feature_pair_policy_v2\\a7ffr3_feature_pair_policy_v2.csv",
    "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ffr4_coarse_to_fine_generation_redesign\\a7ffr4_generation_levels.csv",
    "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ffr5_response_backed_promotion_redesign\\a7ffr5_seed_preview.csv"
  ],
  "mode": "contract_only",
  "objective": "define heavier R-policy-derived feature-to-factor expansion without executing search",
  "reproducible": "yes"
}
```

## Boundary

- Executes generation: `false`
- Executes replay: `false`
- Executes search: `false`
- Uses May in selector/generation: `false`
- Authorizes old A7FF-23 execution: `false`
- Authorizes alpha proof / shadow / paper / live: `false`
- Authorizes next step: `A7FF-24R company execution plan contract`
