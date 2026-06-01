# CRYPTO A7FF-CORE39 SYMBOL-LEVEL BOOK PACKET CONTRACT

Generated: 2026-06-01T19:54:55Z

## Decision

`PASS_A7FFCORE39_SYMBOL_LEVEL_BOOK_PACKET_CONTRACT_READY_FOR_CORE39E`

CORE39 defines the symbol-level packet required to compute CORE38 portfolio/book objectives. It does not run replay, generation, search, alpha proof, shadow, paper, or live.

## Packet Schema

| field                          | required   | role               | note                                       |
|:-------------------------------|:-----------|:-------------------|:-------------------------------------------|
| candidate_id                   | True       | key                | stable candidate id                        |
| timestamp                      | True       | key                | feature timestamp / decision timestamp     |
| feature_available_time         | True       | timing             | must be <= execution timestamp             |
| execution_time                 | True       | timing             | book entry timestamp                       |
| symbol                         | True       | key                | instrument id                              |
| split                          | True       | evaluation         | train/validation/test/recent               |
| family_id                      | True       | candidate_metadata | data family / motif group                  |
| cluster_key                    | True       | candidate_metadata | diversity and dedup key                    |
| label_id                       | True       | label              | L1/L2/L3/L5 primary labels                 |
| horizon_h                      | True       | label              | book horizon                               |
| candidate_score                | True       | signal             | symbol-level formula score before ranking  |
| candidate_rank                 | True       | signal             | cross-sectional rank at timestamp          |
| raw_weight                     | True       | portfolio          | top/bottom book weight before caps         |
| capped_weight                  | True       | portfolio          | after symbol/liquidity/family caps         |
| side                           | True       | portfolio          | long/short/flat                            |
| forward_return                 | True       | label              | raw return                                 |
| cs_relative_return             | True       | label              | cross-sectional relative return            |
| market_beta_residual_return    | True       | label              | BTC/ETH/market residual                    |
| liquidity_tier_relative_return | True       | label              | within liquidity tier                      |
| vol_adjusted_return            | True       | label              | return normalized by realized vol          |
| quote_volume                   | True       | cost_capacity      | liquidity cap input                        |
| turnover_proxy                 | True       | cost_capacity      | turnover/cost proxy                        |
| cost_bps                       | True       | cost_capacity      | 2/5/10 bps variants                        |
| control_variant                | True       | control            | original/wrong_lag/stale/shuffle/sign_flip |

## Build Requirements

| requirement                  | description                                                                       | hard_gate   |
|:-----------------------------|:----------------------------------------------------------------------------------|:------------|
| symbol_level_materialization | candidate_score must be emitted per candidate/timestamp/symbol before aggregation | True        |
| point_in_time_timing         | feature_available_time and execution_time must be explicit                        | True        |
| book_weight_trace            | raw and capped weights must be retained for every selected symbol                 | True        |
| primary_label_panel          | L1/L2/L3/L5 labels must be available at symbol level                              | True        |
| control_packet               | wrong-lag/stale/shuffle/sign-flip controls must be materialized with same schema  | True        |
| aggregation_reproducibility  | aggregate spread rows must be reproducible from the symbol-level packet           | True        |

## Expected Outputs

| artifact                                        | purpose                                           |
|:------------------------------------------------|:--------------------------------------------------|
| a7ffcore39e_symbol_level_score_packet.parquet   | raw symbol-level candidate scores and labels      |
| a7ffcore39e_book_weight_trace.parquet           | long/short/capped weights and cost inputs         |
| a7ffcore39e_control_packet.parquet              | matched control variants with identical schema    |
| a7ffcore39e_aggregate_replay_reconciliation.csv | prove aggregate replay can be reconstructed       |
| a7ffcore39e_packet_quality_audit.csv            | missingness, NaN/inf, timing, coverage, cap audit |

## Execution Plan

| stage        | action                                                                      | scope                                                          |
|:-------------|:----------------------------------------------------------------------------|:---------------------------------------------------------------|
| A7FF-CORE39E | construct a bounded symbol-level packet for existing CORE33 candidate queue | existing candidates only; no new formula generation; no search |
| A7FF-CORE40  | if CORE39E packet passes, define bounded book-objective replay execution    | contract only until explicitly authorized                      |

## Authorization

```json
{
  "authorized": {
    "A7FF-CORE39E symbol-level book packet construction audit": true
  },
  "not_authorized": {
    "alpha_proof": true,
    "book_objective_replay_execution": true,
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
  "authorizes_core39e_packet_audit": true,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE39_SYMBOL_LEVEL_BOOK_PACKET_CONTRACT_READY_FOR_CORE39E",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T19:54:55Z",
  "next_allowed": "A7FF-CORE39E symbol-level book packet construction audit",
  "required_packet_fields": 24,
  "source_decision": "HOLD_A7FFCORE38E_BOOK_OBJECTIVE_AUDIT_REQUIRES_SYMBOL_LEVEL_REPLAY_INPUT",
  "source_stage": "A7FF-CORE38E",
  "stage": "A7FF-CORE39"
}
```
