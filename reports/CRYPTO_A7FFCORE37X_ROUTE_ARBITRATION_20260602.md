# CRYPTO A7FF-CORE37X ROUTE ARBITRATION

Generated: 2026-06-01T19:45:16Z

## Decision

`PASS_A7FFCORE37X_ROUTE_ARBITRATION_READY_FOR_CORE38_CONTRACT`

CORE37X arbitrates the route after CORE36E/36ER froze the replay-objective reset failure. It does not run replay, generation, search, alpha proof, shadow, paper, or live.

## Selected Route

`R3_portfolio_label_objective_contract`

The current independent-family chain has numeric response and preflight evidence, but it does not translate into executable spread survivors. The next allowed work is a contract for executable portfolio-label objectives, not more formula generation.

## Evidence Matrix

| evidence_id                   | stage        | decision                                                        | positive                                                               | negative                                                                       |
|:------------------------------|:-------------|:----------------------------------------------------------------|:-----------------------------------------------------------------------|:-------------------------------------------------------------------------------|
| E0_numeric_response           | CORE30E      | PASS_A7FFCORE30E_NUMERIC_PROBE_CLUES_READY_FOR_CORE31_CONTRACT  | 113 clean numeric clues across 3 independent families                  | numeric response did not translate to bounded replay survivors                 |
| E1_replay_preflight           | CORE32E      | PASS_A7FFCORE32E_REPLAY_PREFLIGHT_READY_FOR_CORE33_CONTRACT     | 21 replay-preflight candidates across 3 families                       | preflight evidence remained weaker than executable spread replay               |
| E2_bounded_replay             | CORE33E      | HOLD_A7FFCORE33E_BOUNDED_REPLAY_INSUFFICIENT                    | bounded replay executed over existing candidates                       | survivor_count=0                                                               |
| E3_orientation_control_repair | CORE34E      | HOLD_A7FFCORE34E_REPAIR_INSUFFICIENT                            | train-only orientation/control repair executed                         | survivor_count=0 after repair                                                  |
| E4_replay_objective_reset     | CORE36E/36ER | HOLD_A7FFCORE36E_REPLAY_OBJECTIVE_RESET_NO_EXECUTABLE_SURVIVORS | executable-spread-first rescoring isolated 3 train-pass F1a candidates | selected_count=0; F1a OOS split unstable; F1b/F2a train objective/control fail |

## Route Scorecard

| route                                 | status                  | reason                                                                                                                                  | authorizes_next   |
|:--------------------------------------|:------------------------|:----------------------------------------------------------------------------------------------------------------------------------------|:------------------|
| R0_same_queue_rerun                   | REJECT                  | CORE34E and CORE36E already exhausted orientation/control and executable-objective rescoring                                            | False             |
| R1_large_formula_search               | REJECT                  | large search would amplify numeric-positive/replay-negative structures without executable translation                                   | False             |
| R2_more_independent_family_generation | HOLD                    | independent data families show numeric response, but replay objective/label book still fails                                            | False             |
| R3_portfolio_label_objective_contract | AUTHORIZE_CONTRACT_ONLY | failure is in label/book/executable spread translation, so next step must define executable portfolio-label objective before generation | True              |

## Frozen Paths

| path                                   | status   | reason                                            |
|:---------------------------------------|:---------|:--------------------------------------------------|
| CORE33/34/36 same candidate queue      | FROZEN   | zero selected executable survivors                |
| same direct numeric-response objective | FROZEN   | numeric response does not survive bounded replay  |
| search before executable objective     | BLOCKED  | selector target would reward non-executable clues |
| alpha proof / shadow / paper / live    | BLOCKED  | no replay survivor or proof object                |

## Authorized Next

| task                                                      | status                   | scope                                                                                             |
|:----------------------------------------------------------|:-------------------------|:--------------------------------------------------------------------------------------------------|
| A7FF-CORE38 executable portfolio-label objective contract | AUTHORIZED_CONTRACT_ONLY | define labels/book proxies/cost/control gates for executable translation; no generation or replay |

## Family Diagnosis Snapshot

| family_id                         |   candidate_count |   train_objective_pass_count |   selected_count |   strict_survivor_count |   median_train_net_spread |   median_train_control_ratio |   median_oos_min_split_net_spread |   median_oos_worst_control_ratio | diagnosis                             |
|:----------------------------------|------------------:|-----------------------------:|-----------------:|------------------------:|--------------------------:|-----------------------------:|----------------------------------:|---------------------------------:|:--------------------------------------|
| F1a_aggtrades_flow_microstructure |                 7 |                            3 |                0 |                       0 |               0.00156803  |                      1.07996 |                        -0.0050861 |                          1.14556 | train_positive_but_oos_split_unstable |
| F1b_taker_flow_market_panel       |                 6 |                            0 |                0 |                       0 |               0.000965976 |                      2.9462  |                        -0.0197957 |                          3.58846 | train_objective_control_fail          |
| F2a_basis_funding_independent     |                 8 |                            0 |                0 |                       0 |               0.00106681  |                      2.75882 |                        -0.0171136 |                          3.09909 | train_objective_control_fail          |

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core38_contract": true,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE37X_ROUTE_ARBITRATION_READY_FOR_CORE38_CONTRACT",
  "dominant_failure": "train_to_oos_executable_spread_instability_after_control_gating",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T19:45:16Z",
  "next_allowed": "A7FF-CORE38 executable portfolio-label objective contract",
  "selected_route": "R3_portfolio_label_objective_contract",
  "source_decision": "PASS_A7FFCORE36ER_REPLAY_OBJECTIVE_FORENSIC_COMPLETE_READY_FOR_CORE37X",
  "source_stage": "A7FF-CORE36ER",
  "stage": "A7FF-CORE37X"
}
```
