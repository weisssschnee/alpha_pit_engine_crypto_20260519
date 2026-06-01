# CRYPTO A7FF-CORE41ER BOOK CONTROL REPAIR FORENSIC

Generated: 2026-06-01T20:28:59Z

## Decision

`PASS_A7FFCORE41ER_BOOK_CONTROL_REPAIR_FORENSIC_READY_FOR_CORE42`

CORE41ER freezes the CORE41E repair result. It does not run generation, search, large search, alpha proof, shadow, paper, or live.

## Main Finding

`single_family_weak_partial_survivor_after_control_repair`

CORE41E found one partial survivor, but it is a single F1b candidate and remains weak because OOS tail and control instability persist. It is not expansion evidence.

## Partial Survivor Snapshot

| candidate_id   | family_id                   |   train_pass_count |   train_median_repaired_net_book_return |   train_median_repaired_control_ratio |   oos_split_count |   oos_positive_split_count |   oos_control_clean_split_count |   oos_min_repaired_net_book_return |   oos_worst_repaired_control_ratio | repair_survivor   | survivor_quality      |
|:---------------|:----------------------------|-------------------:|----------------------------------------:|--------------------------------------:|------------------:|---------------------------:|--------------------------------:|-----------------------------------:|-----------------------------------:|:------------------|:----------------------|
| a7ffcore33_019 | F1b_taker_flow_market_panel |                  5 |                               0.0554675 |                              0.962044 |                 3 |                          2 |                               2 |                          -0.977796 |                            3.74763 | True              | weak_partial_survivor |

## Failure Counts

| family_id                         | forensic_class          |   candidate_count |
|:----------------------------------|:------------------------|------------------:|
| F1a_aggtrades_flow_microstructure | train_control_dominated |                 7 |
| F1b_taker_flow_market_panel       | train_control_dominated |                 5 |
| F1b_taker_flow_market_panel       | partial_survivor        |                 1 |
| F2a_basis_funding_independent     | train_control_dominated |                 8 |

## Authorization Matrix

| task                                                         | status                   | reason                                                                                     |
|:-------------------------------------------------------------|:-------------------------|:-------------------------------------------------------------------------------------------|
| A7FF-CORE42 book-control route arbitration / freeze contract | AUTHORIZED_CONTRACT_ONLY | CORE41E produced only one weak partial survivor in one family; expansion is not authorized |
| F1b survivor expansion                                       | NOT_AUTHORIZED           | single weak survivor, OOS tail and control still unstable                                  |
| formula_search                                               | NOT_AUTHORIZED           | no multi-family strict book survivor                                                       |
| large_search                                                 | NOT_AUTHORIZED           | no multi-family strict book survivor                                                       |
| alpha_proof / shadow / paper / live                          | NOT_AUTHORIZED           | no proof object                                                                            |

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core42_contract": true,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "candidate_count": 21,
  "decision": "PASS_A7FFCORE41ER_BOOK_CONTROL_REPAIR_FORENSIC_READY_FOR_CORE42",
  "dominant_failure": "single_family_weak_partial_survivor_after_control_repair",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T20:28:59Z",
  "next_allowed": "A7FF-CORE42 book-control route arbitration / freeze contract",
  "partial_survivor_count": 1,
  "partial_survivor_family_count": 1,
  "source_decision": "HOLD_A7FFCORE41E_BOOK_CONTROL_REPAIR_INSUFFICIENT",
  "source_stage": "A7FF-CORE41E",
  "stage": "A7FF-CORE41ER"
}
```
