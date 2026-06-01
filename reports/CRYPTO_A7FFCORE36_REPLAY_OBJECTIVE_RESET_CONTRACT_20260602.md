# CRYPTO A7FF-CORE36 REPLAY OBJECTIVE RESET CONTRACT

Generated: 2026-06-01T19:34:08Z

## Decision

`PASS_A7FFCORE36_REPLAY_OBJECTIVE_RESET_CONTRACT_READY_FOR_CORE36E`

CORE36 resets the replay objective after CORE35 determined search is not ready. It does not execute search, large search, alpha proof, shadow, paper, or live.

## Objective Reset Policy

| objective_id               | description                                                                           | allowed   | forbidden                                                           |
|:---------------------------|:--------------------------------------------------------------------------------------|:----------|:--------------------------------------------------------------------|
| R0_executable_spread_first | rank candidates by train executable spread after cost before IC-like response         | True      | IC-only or numeric-only ranking                                     |
| R1_control_margin_first    | require train stale/control margin before queue inclusion                             | True      | post-hoc control filtering after selected queue                     |
| R2_oos_split_balance       | score requires validation/test/recent split presence, not aggregate pass count        | True      | single-split or train-only success                                  |
| R3_family_role_specific    | treat flow/microstructure as directional or hedge-like depending on train spread role | True      | same objective for all data families                                |
| R4_search                  | formula or large search                                                               | False     | any search before replay-objective reset execution proves survivors |

## Metric Contract

| metric                              | role                         |
|:------------------------------------|:-----------------------------|
| train_net_spread_after_cost         | orientation and primary gate |
| train_control_ratio                 | hard reject if >= 1.0        |
| oos_min_split_net_spread            | split-balance gate           |
| oos_control_clean_count             | control survival gate        |
| turnover_cost_sensitivity_2_5_10bps | cost fragility check         |
| family_cluster_diversity            | queue concentration cap      |

## Execution Plan

| stage        | action                                                                       | executes_new_generation   | executes_search   |
|:-------------|:-----------------------------------------------------------------------------|:--------------------------|:------------------|
| A7FF-CORE36E | re-score existing CORE33 queue using replay-objective reset metrics          | False                     | False             |
| A7FF-CORE37  | only if CORE36E finds survivors, write bounded replay repair/replay contract | False                     | False             |

## Authorization

```json
{
  "authorized": {
    "A7FF-CORE36E replay-objective reset execution": true
  },
  "not_authorized": {
    "alpha_proof": true,
    "formula_search": true,
    "large_search": true,
    "shadow_paper_live": true
  }
}
```

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core36e_execution": true,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE36_REPLAY_OBJECTIVE_RESET_CONTRACT_READY_FOR_CORE36E",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T19:34:08Z",
  "next_allowed": "A7FF-CORE36E replay-objective reset execution",
  "source_decision": "HOLD_A7FFCORE35_SEARCH_NOT_READY_REPLAY_TRANSLATION_FAILURE",
  "source_stage": "A7FF-CORE35",
  "stage": "A7FF-CORE36"
}
```
