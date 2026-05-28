# CRYPTO A7AL-2X2 Objective-Family Coverage Gap Audit

Generated: 2026-05-28T16:51:53Z

## Decision

```text
HOLD_A7AL2X2_OBJECTIVE_FAMILY_COVERAGE_GAP_REQUIRES_GENERATOR_AND_SHARED_POOL_REPAIR
```

This audit executes no generation, no replay, no training, and no search. It reconciles A7AL-2K generated candidates, A7AL-2L fast replay preflight, A7AR-7 shared pool, and A7AL-2X1 dry rerank against the A7AL-2X objective-family reset contract.

## Manifest

```json
{
  "allowed_family_generated_total": 2625,
  "allowed_family_shared_pool_total": 2998,
  "allowed_family_x1_non_rejected_total": 0,
  "authorizes_a7al2x3_generation": false,
  "authorizes_a7al2y_generation": false,
  "authorizes_alpha_proof": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "no_a7al2x_allowed_family_candidate_survives_x1_dry_rerank",
    "f1_f6_absent_from_a7ar7_shared_pool_source_of_truth",
    "f1_f6_absent_from_a7al2l_target_replay",
    "positioning_family_generated_only_as_j5_overlay_diagnostic",
    "latent_state_interaction_family_not_generated"
  ],
  "decision": "HOLD_A7AL2X2_OBJECTIVE_FAMILY_COVERAGE_GAP_REQUIRES_GENERATOR_AND_SHARED_POOL_REPAIR",
  "executes_generation": false,
  "executes_replay": false,
  "executes_search": false,
  "executes_training": false,
  "generated_at": "2026-05-28T16:51:53Z",
  "input_generated_candidates": 8000,
  "input_shared_pool_candidates": 4000
}
```

## Stage Funnel By Family

| family_id                          |   generated_count |   historical_generated_count |   selected_for_a7al2l_count |   selected_historical_for_a7al2l_count |   a7al2l_replayed_count |   a7al2l_clue_count |   shared_pool_count |   shared_fast_replay_count |   x1_non_rejected_count |   x1_selected_count |   generated_share | gap_stage                                  | recommended_repair                                                            |
|:-----------------------------------|------------------:|-----------------------------:|----------------------------:|---------------------------------------:|------------------------:|--------------------:|--------------------:|---------------------------:|------------------------:|--------------------:|------------------:|:-------------------------------------------|:------------------------------------------------------------------------------|
| F0_OI_delta_price_interaction      |              2053 |                         1819 |                         104 |                                    104 |                       0 |                   0 |                2998 |                        103 |                       0 |                   0 |          0.256625 | a7al2l_target_replay_mode_excluded         | run_family_balanced_preflight_instead_of_two_target_replay                    |
| F1_OI_basis_premium_interaction    |                85 |                           85 |                           7 |                                      7 |                       0 |                   0 |                   0 |                          0 |                       0 |                   0 |          0.010625 | a7al2l_target_replay_mode_excluded         | run_family_balanced_preflight_instead_of_two_target_replay                    |
| F2_OI_funding_crowding_interaction |                77 |                           77 |                          13 |                                     13 |                       0 |                   0 |                   0 |                          0 |                       0 |                   0 |          0.009625 | a7al2l_target_replay_mode_excluded         | run_family_balanced_preflight_instead_of_two_target_replay                    |
| F3_positioning_divergence          |                67 |                            0 |                           0 |                                      0 |                       0 |                   0 |                   0 |                          0 |                       0 |                   0 |          0.008375 | generated_only_as_overlay_or_nonhistorical | replace_overlay_only_fields_with_historical_binance_fields_or_contract_source |
| F4_OI_taker_flow_interaction       |               126 |                          126 |                          23 |                                     23 |                       0 |                   0 |                   0 |                          0 |                       0 |                   0 |          0.01575  | a7al2l_target_replay_mode_excluded         | run_family_balanced_preflight_instead_of_two_target_replay                    |
| F5_OI_upper_regime_interaction     |               217 |                          217 |                          39 |                                     39 |                       0 |                   0 |                   0 |                          0 |                       0 |                   0 |          0.027125 | a7al2l_target_replay_mode_excluded         | run_family_balanced_preflight_instead_of_two_target_replay                    |
| F6_OI_latent_state_interaction     |                 0 |                            0 |                           0 |                                      0 |                       0 |                   0 |                   0 |                          0 |                       0 |                   0 |          0        | not_generated                              | add_family_to_generator_templates                                             |
| DIRECT_OI_PRICE_WEAK_PRIOR         |               660 |                          660 |                          44 |                                     44 |                       2 |                   2 |                1002 |                         25 |                       0 |                   0 |          0.0825   | x1_control_or_contract_rejected            | repair_control_dominance_or_keep_as_rejected_family                           |
| UNMAPPED_OR_FORBIDDEN              |              4715 |                         4376 |                         538 |                                    538 |                       0 |                   0 |                   0 |                          0 |                       0 |                   0 |          0.589375 | a7al2l_target_replay_mode_excluded         | run_family_balanced_preflight_instead_of_two_target_replay                    |

## Missing Family Gap Audit

| family_id                          | in_a7al2x_contract   | has_generated_candidates   | has_historical_generated_candidates   | has_a7al2l_replay   | has_shared_pool_candidates   | has_x1_eligible_candidates   | primary_gap                                | required_action                                                               |
|:-----------------------------------|:---------------------|:---------------------------|:--------------------------------------|:--------------------|:-----------------------------|:-----------------------------|:-------------------------------------------|:------------------------------------------------------------------------------|
| F0_OI_delta_price_interaction      | True                 | True                       | True                                  | False               | True                         | False                        | a7al2l_target_replay_mode_excluded         | run_family_balanced_preflight_instead_of_two_target_replay                    |
| F1_OI_basis_premium_interaction    | True                 | True                       | True                                  | False               | False                        | False                        | a7al2l_target_replay_mode_excluded         | run_family_balanced_preflight_instead_of_two_target_replay                    |
| F2_OI_funding_crowding_interaction | True                 | True                       | True                                  | False               | False                        | False                        | a7al2l_target_replay_mode_excluded         | run_family_balanced_preflight_instead_of_two_target_replay                    |
| F3_positioning_divergence          | True                 | True                       | False                                 | False               | False                        | False                        | generated_only_as_overlay_or_nonhistorical | replace_overlay_only_fields_with_historical_binance_fields_or_contract_source |
| F4_OI_taker_flow_interaction       | True                 | True                       | True                                  | False               | False                        | False                        | a7al2l_target_replay_mode_excluded         | run_family_balanced_preflight_instead_of_two_target_replay                    |
| F5_OI_upper_regime_interaction     | True                 | True                       | True                                  | False               | False                        | False                        | a7al2l_target_replay_mode_excluded         | run_family_balanced_preflight_instead_of_two_target_replay                    |
| F6_OI_latent_state_interaction     | True                 | False                      | False                                 | False               | False                        | False                        | not_generated                              | add_family_to_generator_templates                                             |

## Source-Of-Truth Gap

| artifact                    |   candidate_count |   family_count | top_family                    |   top_family_share | source_of_truth_role             |
|:----------------------------|------------------:|---------------:|:------------------------------|-------------------:|:---------------------------------|
| a7al2k_generated_pool       |              8000 |              8 | UNMAPPED_OR_FORBIDDEN         |           0.589375 | generator_broad_pool             |
| a7al2l_replayed_target_pool |                 2 |              1 | DIRECT_OI_PRICE_WEAK_PRIOR    |           1        | downstream_stage                 |
| a7ar7_shared_candidate_pool |              4000 |              2 | F0_OI_delta_price_interaction |           0.7495   | current_selector_source_of_truth |
| a7al2x1_dry_rerank_trace    |              4000 |              3 | F0_OI_delta_price_interaction |           0.49775  | downstream_stage                 |

## Repair Plan

| step       | name                                               | description                                                                                                      | executes_generation   | executes_replay   | authorizes_search   |
|:-----------|:---------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------|:----------------------|:------------------|:--------------------|
| A7AL-2X2R0 | family-balanced generator coverage repair contract | Add explicit quotas for F1-F6 historical fields before any selector or replay.                                   | False                 | False             | False               |
| A7AL-2X2R1 | shared-pool ledger rebuild contract                | Define a new shared pool source-of-truth that includes all A7AL-2X families, not only local OI-price candidates. | False                 | False             | False               |
| A7AL-2X3   | family-balanced dry generation smoke               | Only after R0/R1, generate a small balanced candidate pool and stop before replay.                               | True                  | False             | False               |

## Interpretation

```text
The current shared pool is not an A7AL-2X broad OI/positioning interaction pool.
It is a local OI-price lineage pool inherited from A7AL-2P2/A7AL-2Q.

A7AL-2K did generate some F1/F2/F4/F5-like structures, but A7AL-2L ran in two-target replay mode and did not replay those families.
F3 positioning is present only through J5 cross-exchange overlay diagnostics, not as a historical proof-grade Binance metrics family.
F6 latent-state interaction is not generated.

Therefore A7AL-2Y remains not authorized.
The next valid work is a family-balanced generator/shared-pool repair contract, not replay or search execution.
```

## Boundary

```text
No generation.
No replay.
No search.
No May in selector/ranking/mutation/generation.
No alpha proof / shadow / paper / live.
```
