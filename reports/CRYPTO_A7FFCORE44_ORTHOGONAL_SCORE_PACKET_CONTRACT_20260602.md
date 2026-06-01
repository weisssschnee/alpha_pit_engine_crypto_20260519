# CRYPTO A7FF-CORE44 ORTHOGONAL SCORE PACKET CONTRACT

Generated: 2026-06-01T20:44:47Z

## Decision

`PASS_A7FFCORE44_ORTHOGONAL_SCORE_PACKET_CONTRACT_READY_FOR_CORE44E`

CORE44 defines how to turn CORE43E full-universe control vectors into an orthogonal score packet. It is a contract only and does not execute replay, generation, search, proof, shadow, paper, or live.

## Input Contract

| input_id                                       | path                                                                                                                                     | required   | status    | notes                                                                  |
|:-----------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------|:-----------|:----------|:-----------------------------------------------------------------------|
| I0_core43e_full_universe_control_vector_sample | G:/AlphaFactory_CryptoData/research_runtime/a7ffcore43e_control_vectors_20260602/a7ffcore43e_full_universe_control_vector_sample.parquet | True       | AVAILABLE | external parquet remains outside git; committed manifest references it |
| I1_core33_candidate_queue                      | runtime/a7ffcore33_bounded_replay_contract/a7ffcore33_replay_candidate_queue.csv                                                         | True       | AVAILABLE | candidate metadata source; no stale selected packet reuse              |

## Packet Schema

| field                           | level            | required   |
|:--------------------------------|:-----------------|:-----------|
| candidate_id                    | key              | True       |
| dataset                         | key              | True       |
| family_id                       | key              | True       |
| cluster_key                     | key              | True       |
| timestamp                       | key              | True       |
| symbol                          | key              | True       |
| split                           | key              | True       |
| quote_volume                    | liquidity        | True       |
| candidate_score_original        | control_vector   | True       |
| candidate_score_stale           | control_vector   | True       |
| candidate_score_sign_flip       | control_vector   | True       |
| candidate_score_shuffle_time    | control_vector   | True       |
| candidate_score_shuffle_symbol  | control_vector   | True       |
| residual_score_stale_orthogonal | orthogonal_score | True       |
| residual_score_null_orthogonal  | orthogonal_score | True       |
| selected_score_variant          | policy           | True       |
| book_rank                       | book_input       | True       |
| book_side                       | book_input       | True       |
| book_weight                     | book_input       | True       |
| control_margin_metadata         | diagnostic       | True       |

## Construction Policy

| policy_id                         | description                                                                                                         | hard_requirement   |
|:----------------------------------|:--------------------------------------------------------------------------------------------------------------------|:-------------------|
| P0_full_universe_before_selection | compute residual scores over full timestamp-symbol universe before any top/bottom selection                         | True               |
| P1_primary_score_variant          | use residual_score_null_orthogonal as primary book ranking score; stale-only residual is diagnostic fallback only   | True               |
| P2_train_only_orientation         | if orientation is required, fit sign only on train_2024 and apply unchanged to validation/test/recent               | True               |
| P3_control_margin_required        | book packet must retain original/stale/sign/shuffle score ranks for control dominance checks                        | True               |
| P4_no_selected_packet_backfill    | CORE39E selected top/bottom packet must not be used as orthogonalization input                                      | True               |
| P5_no_search                      | CORE44 and CORE44E do not authorize formula generation, formula search, large search, proof, shadow, paper, or live | True               |

## Execution Plan

| stage        | action                                                                       | executes_new_generation   | executes_search   | writes_large_artifact_to_git   |
|:-------------|:-----------------------------------------------------------------------------|:--------------------------|:------------------|:-------------------------------|
| A7FF-CORE44E | construct bounded orthogonal score packet from CORE43E full-universe vectors | False                     | False             | False                          |
| A7FF-CORE45  | if CORE44E passes, define bounded orthogonal book replay contract            | False                     | False             | False                          |

## Authorization

```json
{
  "authorized": {
    "A7FF-CORE44E orthogonal score packet construction audit": true
  },
  "not_authorized": {
    "alpha_proof": true,
    "formula_search": true,
    "large_search": true,
    "new_generation": true,
    "selected_packet_control_orthogonalization": true,
    "shadow_paper_live": true
  }
}
```

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core44e_packet_construction": true,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE44_ORTHOGONAL_SCORE_PACKET_CONTRACT_READY_FOR_CORE44E",
  "executes_new_generation": false,
  "executes_search": false,
  "generated_at": "2026-06-01T20:44:47Z",
  "next_allowed": "A7FF-CORE44E orthogonal score packet construction audit",
  "source_decision": "PASS_A7FFCORE43E_CONTROL_VECTOR_REBUILD_READY_FOR_CORE44",
  "source_external_sample_path": "G:/AlphaFactory_CryptoData/research_runtime/a7ffcore43e_control_vectors_20260602/a7ffcore43e_full_universe_control_vector_sample.parquet",
  "source_stage": "A7FF-CORE43E",
  "source_vector_sample_columns": 18,
  "source_vector_sample_rows": 255236,
  "stage": "A7FF-CORE44"
}
```
