# CRYPTO A7AL-2X Objective Family Reset Contract

Generated: 2026-05-28T16:15:49Z

## Decision

```text
PASS_A7AL2X_OBJECTIVE_FAMILY_RESET_CONTRACT_READY_FOR_A7AL2X1
```

This is an objective-family reset contract. It executes no generation, no replay, no training, and no proof.

## Manifest

```json
{
  "allowed_objective_family_count": 7,
  "authorizes_a7al2q_local_execution": false,
  "authorizes_a7al2x1_dry_rerank": true,
  "authorizes_a7al2y_generation": false,
  "authorizes_alpha_proof": false,
  "authorizes_direct_oi_price_expansion": false,
  "authorizes_large_search": false,
  "authorizes_same_objective_rerun": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7AL2X_OBJECTIVE_FAMILY_RESET_CONTRACT_READY_FOR_A7AL2X1",
  "direct_oi_price_status": "stress_vetoed_weak_prior_not_standalone_objective",
  "executes_replay": false,
  "executes_search": false,
  "executes_training": false,
  "forbidden_objective_count": 11,
  "generated_at": "2026-05-28T16:15:49Z",
  "source_of_truth": "A7AR-7 shared candidate pool plus A7AR-8 clusters plus A7AL-2W repair plus A7AL-2X0 authorization",
  "uses_may_for_generation": false,
  "uses_may_for_mutation": false,
  "uses_may_for_selector": false,
  "uses_may_for_veto_or_attribution": true,
  "uses_may_for_weight_update": false
}
```

## Core Reset

```text
direct OI x price:
  status = stress-vetoed weak prior
  not standalone objective
  not eligible for same-objective rerun
  not eligible for direct expansion
```

## Allowed Objective Families

| family_id                          | status                | field_scope                                                                                                 | economic_role                                                   | example_patterns                                                                     | standalone_allowed   | requires_control_gate   | requires_signal_vector_cap   |
|:-----------------------------------|:----------------------|:------------------------------------------------------------------------------------------------------------|:----------------------------------------------------------------|:-------------------------------------------------------------------------------------|:---------------------|:------------------------|:-----------------------------|
| F0_OI_delta_price_interaction      | allowed_contract_only | open_interest_delta\|open_interest_value_delta\|price_move                                                  | leverage expansion or contraction under price move              | Delta(OI,w)*Delta(price,w); Delta(OI_value,w)*price_move                             | False                | True                    | True                         |
| F1_OI_basis_premium_interaction    | allowed_contract_only | OI\|OI_change\|premium_abs\|basis_dislocation                                                               | leverage change under basis or premium dislocation              | Delta(OI,w)*premium_abs; OI_change*basis_dislocation_state                           | False                | True                    | True                         |
| F2_OI_funding_crowding_interaction | allowed_contract_only | OI\|OI_change\|funding_abs\|funding_persistence\|funding_neutral_state                                      | leverage under funding crowding or neutral funding state        | Delta(OI,w)*funding_abs; OI_change*funding_persistence                               | False                | True                    | True                         |
| F3_positioning_divergence          | allowed_contract_only | global_long_short\|top_account_long_short\|top_position_long_short\|account_position_divergence             | crowding divergence between accounts and position size          | Sub(top_position_ratio,global_account_ratio); Delta(top_account_ratio,w)*price_state | False                | True                    | True                         |
| F4_OI_taker_flow_interaction       | allowed_contract_only | OI_change\|taker_buy_sell_volume_ratio\|aggressive_flow_reversal                                            | aggressive flow under leverage expansion or contraction         | Delta(OI,w)*taker_buy_sell_ratio; OI_contraction*flow_reversal                       | False                | True                    | True                         |
| F5_OI_upper_regime_interaction     | allowed_contract_only | OI_features\|leverage_crowding_state\|basis_dislocation_state\|stress_proxy_state\|breadth\|liquidity_cycle | OI behavior conditional on upper market regime                  | OI_change*leverage_crowding_state; OI_value_delta*stress_proxy_state                 | False                | True                    | True                         |
| F6_OI_latent_state_interaction     | allowed_contract_only | OI\|positioning\|listing_age_latent\|liquidity_tier\|meme_multiplier_major_neutral_state                    | OI/positioning within latent lifecycle and symbol-state buckets | latent_neutral_rank(OI_change); OI_state*meme_neutral_state                          | False                | True                    | True                         |

## Forbidden Objective Families / Paths

| item                                                      | status    | reason                                                           |
|:----------------------------------------------------------|:----------|:-----------------------------------------------------------------|
| same_direct_OI_price_objective_rerun                      | forbidden | superseded by A7AL-2X0 and zero stress-clean selected candidates |
| direct_OI_price_expansion                                 | forbidden | direct OI x price is stress-vetoed weak prior only               |
| funding_only_wrapper                                      | forbidden | must be interaction, not standalone wrapper                      |
| basis_only_wrapper                                        | forbidden | must be interaction, not standalone wrapper                      |
| liquidity_volatility_old_family                           | forbidden | previous crypto path produced cluster/stress failures            |
| A7V_activity_liquidity_self_reproduction_family           | forbidden | A7V family failed control/May attribution                        |
| stale_J5_overlay_aliases                                  | forbidden | canonical alias audit required; no stale fallback                |
| raw_OKX_Binance_direct_price_comparison                   | forbidden | contract-unit canonical fields only                              |
| full_open_FormulaGenV2_grammar                            | forbidden | A7AL-2X is not an open grammar search                            |
| May_informed_regime_mask                                  | forbidden | May stress-only policy                                           |
| May_in_ranking_selector_mutation_generation_weight_update | forbidden | May allowed only for post-selection veto/attribution             |

## Selector Feature Contract

```json
{
  "allowed_selector_features": {
    "control_dominance": [
      "matched_control_margin",
      "wrong_lag_margin",
      "shuffle_control_margin"
    ],
    "diversity": [
      "signal_vector_cluster_id",
      "field_family_pair",
      "skeleton_key",
      "production_key"
    ],
    "latency_cost": [
      "one_bar_lag_survival",
      "cost_proxy_survival",
      "turnover_proxy"
    ],
    "neutralization": [
      "timevarying_latent_neutral_survival",
      "liquidity_tier_neutral_survival",
      "meme_multiplier_neutral_survival"
    ],
    "replay_alignment": [
      "pre_may_replay_alignment",
      "label_entry_alignment",
      "split_dispersion"
    ],
    "robust_statistics": [
      "newey_west_tstat",
      "block_bootstrap_tstat",
      "nonoverlap_offset_tstat"
    ]
  },
  "forbidden_selector_features": [
    "May_return",
    "May_residual",
    "May_pass_fail",
    "May_stress_margin",
    "May_tuned_threshold",
    "promotion_label",
    "alpha_proof_label",
    "shadow_paper_live_label"
  ],
  "hard_gates": {
    "control_ratio_ge_1": "reject",
    "same_signal_vector_cluster_over_cap": "reject_or_downrank",
    "same_skeleton_over_cap": "reject_or_downrank",
    "timevarying_latent_neutral_fail": "reject",
    "wrong_lag_or_shuffle_control_stronger": "reject"
  },
  "uses_may_for_selector": false
}
```

## Signal-Vector Cap Policy

```json
{
  "same_field_family_pair_share": "<= 0.35",
  "same_production_key_share": "<= 0.20",
  "same_skeleton_share": "<= 0.25",
  "selected_max_pairwise_corr": "<= 0.80",
  "selected_signal_vector_clusters": ">= min(selected_count, 4)",
  "selected_top_signal_vector_cluster_share": "<= 0.35",
  "small_pool_rule": "for selected_count <= 4, selected candidates should be in distinct signal-vector clusters unless no eligible alternatives exist",
  "uses_may_for_cluster": false
}
```

## Source of Truth

```json
{
  "a7al2p2_status": "SUPERSEDED_DIAGNOSTIC_CONTRACT",
  "a7al2q_local_execution": "NOT_AUTHORIZED",
  "forbidden_inputs": [
    "direct A7AL-2P2 seed pool reads",
    "direct stale A7AL-2L or A7AL-2O single-stage artifact reads",
    "selector bypassing A7AR-7 shared candidate pool"
  ],
  "required_inputs": {
    "authorization_arbitration": "runtime\\a7al2x0_authorization_arbitration\\a7al2x0_authorization_matrix.json",
    "selector_diversity_repair_manifest": "runtime\\a7al2w_signal_vector_selector_repair\\a7al2w_manifest.json",
    "shared_candidate_pool": "runtime\\a7ar7_shared_candidate_pool\\a7ar7_shared_candidate_pool.csv",
    "signal_vector_cluster_registry": "runtime\\a7ar8_signal_vector_cluster_registry\\a7ar8_signal_cluster_registry.csv"
  }
}
```

## May Policy

```json
{
  "allowed": [
    "post_selection_veto",
    "failure_attribution",
    "stress_report_label"
  ],
  "forbidden": [
    "ranking",
    "selector_score",
    "threshold_tuning",
    "weight_selection",
    "generation",
    "mutation",
    "lane_allocation",
    "training_target",
    "regime_mask"
  ],
  "policy_source": "A7AL-2X0 authorization arbitration"
}
```

## Authorization

```json
{
  "a7al2q_local_execution": "NOT_AUTHORIZED",
  "a7al2x1_dry_rerank": "AUTHORIZED",
  "a7al2y_generation": "NOT_AUTHORIZED",
  "alpha_proof": "NOT_AUTHORIZED",
  "decision": "PASS_A7AL2X_OBJECTIVE_FAMILY_RESET_CONTRACT_READY_FOR_A7AL2X1",
  "direct_oi_price_expansion": "NOT_AUTHORIZED",
  "large_formula_search": "NOT_AUTHORIZED",
  "same_objective_rerun": "NOT_AUTHORIZED",
  "shadow_paper_live": "NOT_AUTHORIZED"
}
```

## Next Stage

```text
A7AL-2X1 dry rerank:
  authorized after this contract
  no generation
  no replay
  no search
  no alpha proof
```
