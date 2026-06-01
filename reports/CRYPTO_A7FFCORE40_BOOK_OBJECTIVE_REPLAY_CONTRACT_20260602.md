# CRYPTO A7FF-CORE40 BOOK OBJECTIVE REPLAY CONTRACT

Generated: 2026-06-01T20:22:30Z

## Decision

`PASS_A7FFCORE40_BOOK_OBJECTIVE_REPLAY_CONTRACT_READY_FOR_CORE40E`

CORE40 authorizes bounded book-objective replay execution over the CORE39E symbol-level packet sample. It does not authorize new generation, formula search, large search, alpha proof, shadow, paper, or live.

## Book Objectives

| book_objective                | label_column                | primary   |
|:------------------------------|:----------------------------|:----------|
| B1_cross_sectional_rank_book  | cs_relative_return          | True      |
| B2_market_beta_residual_book  | market_beta_residual_return | True      |
| B3_vol_adjusted_rank_book     | vol_adjusted_return         | True      |
| B4_liquidity_cost_capped_book | cs_relative_return          | True      |

## Replay Gates

| gate                    | rule                                                                | hard_gate   |
|:------------------------|:--------------------------------------------------------------------|:------------|
| original_control_margin | original book spread must beat stale and sign_flip controls         | True        |
| split_balance           | validation/test/recent cannot be all negative after train positive  | True        |
| family_diversity        | selected survivors must span >=2 families before any next expansion | True        |
| candidate_count         | selected survivors >=4 for any expansion contract                   | True        |
| cost_cap                | sample uses 5bps; full execution contract must include 2/5/10bps    | False       |
| packet_reconciliation   | book replay must be reproducible from CORE39E packet path           | True        |

## Execution Scope

| stage        | input                                                                                                                                    | action                                                                               | executes_new_generation   | executes_search   | executes_alpha_proof   |
|:-------------|:-----------------------------------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------|:--------------------------|:------------------|:-----------------------|
| A7FF-CORE40E | G:/AlphaFactory_CryptoData/research_runtime/a7ffcore39e_symbol_level_book_packet_20260602/a7ffcore39e_symbol_level_packet_sample.parquet | aggregate symbol-level weights and labels into bounded book-objective replay metrics | False                     | False             | False                  |

## Source Packet Quality

| metric                          |           value | pass   |
|:--------------------------------|----------------:|:-------|
| packet_sample_rows              | 623160          | True   |
| candidate_count_in_sample       |     21          | True   |
| label_count_in_sample           |      4          | True   |
| control_variant_count_in_sample |      3          | True   |
| required_field_count            |     24          | True   |
| missing_label_rate              |      0.00899801 | True   |

## Authorization

```json
{
  "authorized": {
    "A7FF-CORE40E bounded book-objective replay execution": true
  },
  "not_authorized": {
    "alpha_proof": true,
    "formula_search": true,
    "large_search": true,
    "new_generation": true,
    "shadow_paper_live": true
  }
}
```

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core40e_execution": true,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE40_BOOK_OBJECTIVE_REPLAY_CONTRACT_READY_FOR_CORE40E",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T20:22:30Z",
  "next_allowed": "A7FF-CORE40E bounded book-objective replay execution",
  "packet_sample_path": "G:/AlphaFactory_CryptoData/research_runtime/a7ffcore39e_symbol_level_book_packet_20260602/a7ffcore39e_symbol_level_packet_sample.parquet",
  "packet_sample_rows": 623160,
  "source_decision": "PASS_A7FFCORE39E_SYMBOL_LEVEL_PACKET_SAMPLE_READY_FOR_CORE40_CONTRACT",
  "source_stage": "A7FF-CORE39E",
  "stage": "A7FF-CORE40"
}
```
