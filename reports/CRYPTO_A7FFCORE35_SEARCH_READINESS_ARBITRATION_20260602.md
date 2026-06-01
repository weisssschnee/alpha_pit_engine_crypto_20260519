# CRYPTO A7FF-CORE35 SEARCH READINESS ARBITRATION

Generated: 2026-06-01T19:32:11Z

## Decision

`HOLD_A7FFCORE35_SEARCH_NOT_READY_REPLAY_TRANSLATION_FAILURE`

CORE35 arbitrates search readiness after independent-family numeric/preflight/replay repair. It does not execute replay, search, large search, alpha proof, shadow, paper, or live.

## Evidence Matrix

| stage                    | decision                                                       | positive_evidence                         | negative_evidence                                            |
|:-------------------------|:---------------------------------------------------------------|:------------------------------------------|:-------------------------------------------------------------|
| CORE30E numeric probe    | PASS_A7FFCORE30E_NUMERIC_PROBE_CLUES_READY_FOR_CORE31_CONTRACT | 113 clean numeric clues across 3 families | numeric-only; no portfolio/replay proof                      |
| CORE32E replay preflight | PASS_A7FFCORE32E_REPLAY_PREFLIGHT_READY_FOR_CORE33_CONTRACT    | 21 preflight candidates across 3 families | preflight only; no tradable replay                           |
| CORE33E bounded replay   | HOLD_A7FFCORE33E_BOUNDED_REPLAY_INSUFFICIENT                   | bounded replay executed                   | survivor_count=0                                             |
| CORE34E/34ER repair      | PASS_A7FFCORE34ER_REPAIR_FORENSIC_READY_FOR_CORE35_ARBITRATION | repair failure diagnosed                  | train_control_fail_count=12; OOS positive still insufficient |

## Family Failure Snapshot

| family_id                         | failure_mode                                 |   candidate_count |
|:----------------------------------|:---------------------------------------------|------------------:|
| F1a_aggtrades_flow_microstructure | orientation_repair_oos_positive_insufficient |                 2 |
| F1a_aggtrades_flow_microstructure | train_control_filter_fail                    |                 4 |
| F1b_taker_flow_market_panel       | train_control_filter_fail                    |                 3 |
| F2a_basis_funding_independent     | train_control_filter_fail                    |                 5 |

## Authorization Matrix

| task                                                        | status                   | reason                                                                      |
|:------------------------------------------------------------|:-------------------------|:----------------------------------------------------------------------------|
| large_search                                                | NOT_AUTHORIZED           | bounded replay and repair survivor_count=0                                  |
| formula_search                                              | NOT_AUTHORIZED           | numeric/preflight clues did not survive replay proxy                        |
| same_queue_rerun                                            | NOT_AUTHORIZED           | CORE34E exhausted train-only orientation/control repair                     |
| alpha_proof                                                 | NOT_AUTHORIZED           | no replay survivor/proof object                                             |
| shadow_paper_live                                           | NOT_AUTHORIZED           | no alpha proof and no replay survivor                                       |
| A7FF-CORE36 replay-objective/portfolio-proxy reset contract | AUTHORIZED_CONTRACT_ONLY | failure moved from numeric feature response to replay/portfolio translation |

## Next Contract Requirements

| contract_item                  | required_change                                                                                        |
|:-------------------------------|:-------------------------------------------------------------------------------------------------------|
| label_portfolio_alignment      | separate IC-like numeric response from executable spread; define portfolio objective before generation |
| train_only_orientation_policy  | orientation can be used only if train control clean and OOS split coverage survives                    |
| control_first_replay_queue     | control ratio must gate replay candidates before score ranking                                         |
| family_specific_response_roles | F1a may be regime/hedge-like; F1b/F2a need stronger control dominance filter                           |

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core36_contract": true,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "HOLD_A7FFCORE35_SEARCH_NOT_READY_REPLAY_TRANSLATION_FAILURE",
  "dominant_failure": "numeric_response_does_not_translate_to_bounded_replay_survivors",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T19:32:11Z",
  "next_allowed": "A7FF-CORE36 replay-objective/portfolio-proxy reset contract",
  "source_decision": "PASS_A7FFCORE34ER_REPAIR_FORENSIC_READY_FOR_CORE35_ARBITRATION",
  "source_stage": "A7FF-CORE34ER",
  "stage": "A7FF-CORE35"
}
```
