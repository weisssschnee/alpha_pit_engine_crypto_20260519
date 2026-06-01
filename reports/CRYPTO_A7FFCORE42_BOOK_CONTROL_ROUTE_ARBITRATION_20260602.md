# CRYPTO A7FF-CORE42 BOOK CONTROL ROUTE ARBITRATION

Generated: 2026-06-01T20:30:53Z

## Decision

`PASS_A7FFCORE42_ROUTE_ARBITRATION_READY_FOR_CORE43_CONTROL_ORTHOGONALIZATION_CONTRACT`

CORE42 arbitrates the route after CORE41ER found only a single weak partial survivor. It does not run replay, generation, search, alpha proof, shadow, paper, or live.

## Selected Route

`R3_control_orthogonalization_contract`

The current queue is frozen. The next valid work is a control/null-model redesign, not expansion of the weak F1b survivor.

## Route Scorecard

| route                                 | status                  | reason                                                                      | authorizes_next   |
|:--------------------------------------|:------------------------|:----------------------------------------------------------------------------|:------------------|
| R0_expand_F1b_partial_survivor        | REJECT                  | only one weak partial survivor; OOS tail and control instability remain     | False             |
| R1_large_search                       | REJECT                  | search would optimize toward control-dominated book responses               | False             |
| R2_same_packet_rerun                  | REJECT                  | CORE40E/41E already consumed the current packet and controls                | False             |
| R3_control_orthogonalization_contract | AUTHORIZE_CONTRACT_ONLY | next valid work is to redesign controls/orthogonalization before any search | True              |

## Partial Survivor Snapshot

| candidate_id   | family_id                   |   train_pass_count |   train_median_repaired_net_book_return |   train_median_repaired_control_ratio |   oos_split_count |   oos_positive_split_count |   oos_control_clean_split_count |   oos_min_repaired_net_book_return |   oos_worst_repaired_control_ratio | repair_survivor   | survivor_quality      |
|:---------------|:----------------------------|-------------------:|----------------------------------------:|--------------------------------------:|------------------:|---------------------------:|--------------------------------:|-----------------------------------:|-----------------------------------:|:------------------|:----------------------|
| a7ffcore33_019 | F1b_taker_flow_market_panel |                  5 |                               0.0554675 |                              0.962044 |                 3 |                          2 |                               2 |                          -0.977796 |                            3.74763 | True              | weak_partial_survivor |

## Frozen Paths

| path                                | status   | reason                               |
|:------------------------------------|:---------|:-------------------------------------|
| CORE33-41 current candidate queue   | FROZEN   | no multi-family strict survivor      |
| F1b partial survivor expansion      | BLOCKED  | single weak survivor only            |
| large search / formula search       | BLOCKED  | book responses are control-dominated |
| alpha proof / shadow / paper / live | BLOCKED  | no proof object                      |

## Authorized Next

| task                                                        | status                   | scope                                                                                                                        |
|:------------------------------------------------------------|:-------------------------|:-----------------------------------------------------------------------------------------------------------------------------|
| A7FF-CORE43 control orthogonalization / null-model contract | AUTHORIZED_CONTRACT_ONLY | define control-orthogonal score residuals, stale dominance decomposition, and sign-arbitrariness rejection before generation |

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core43_contract": true,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE42_ROUTE_ARBITRATION_READY_FOR_CORE43_CONTROL_ORTHOGONALIZATION_CONTRACT",
  "dominant_failure": "single_family_weak_partial_survivor_after_control_repair",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T20:30:53Z",
  "next_allowed": "A7FF-CORE43 control orthogonalization / null-model contract",
  "selected_route": "R3_control_orthogonalization_contract",
  "source_decision": "PASS_A7FFCORE41ER_BOOK_CONTROL_REPAIR_FORENSIC_READY_FOR_CORE42",
  "source_stage": "A7FF-CORE41ER",
  "stage": "A7FF-CORE42"
}
```
