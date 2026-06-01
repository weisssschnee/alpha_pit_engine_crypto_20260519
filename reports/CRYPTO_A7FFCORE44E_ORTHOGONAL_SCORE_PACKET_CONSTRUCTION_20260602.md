# CRYPTO A7FF-CORE44E ORTHOGONAL SCORE PACKET CONSTRUCTION

Generated: 2026-06-01T20:47:57Z

## Decision

`PASS_A7FFCORE44E_ORTHOGONAL_SCORE_PACKET_READY_FOR_CORE45_CONTRACT`

CORE44E constructs a bounded orthogonal book-input packet from CORE43E full-universe residual score vectors. It does not run book replay, generation, search, alpha proof, shadow, paper, or live.

## Dataset Summary

| dataset                       |   vector_rows |   candidate_count |   symbol_count |   timestamp_count |
|:------------------------------|--------------:|------------------:|---------------:|------------------:|
| core12_aggtrades_all_features |         13104 |                 7 |             39 |               136 |
| top498_replay_v2              |        242132 |                14 |            498 |               338 |

## Packet Quality Gate

| metric                             |     value | pass   |
|:-----------------------------------|----------:|:-------|
| packet_rows                        | 22600     | True   |
| candidate_count                    |    21     | True   |
| required_packet_columns_present    |    20     | True   |
| missing_book_score_rate            |     0     | True   |
| max_abs_book_weight                |     0.025 | True   |
| long_short_presence_all_candidates |    21     | True   |

## Candidate Packet Quality

| candidate_id   | dataset                       | family_id                         |   packet_rows |   timestamp_count |   symbol_count |   long_rows |   short_rows |   mean_abs_weight |   max_abs_weight |
|:---------------|:------------------------------|:----------------------------------|--------------:|------------------:|---------------:|------------:|-------------:|------------------:|-----------------:|
| a7ffcore33_000 | top498_replay_v2              | F1b_taker_flow_market_panel       |          3118 |                48 |            489 |        1559 |         1559 |         0.0232842 |            0.025 |
| a7ffcore33_001 | top498_replay_v2              | F1b_taker_flow_market_panel       |            18 |                 9 |             15 |           9 |            9 |         0.025     |            0.025 |
| a7ffcore33_002 | top498_replay_v2              | F2a_basis_funding_independent     |            18 |                 9 |             17 |           9 |            9 |         0.025     |            0.025 |
| a7ffcore33_003 | top498_replay_v2              | F2a_basis_funding_independent     |          3114 |                48 |            467 |        1557 |         1557 |         0.023298  |            0.025 |
| a7ffcore33_004 | top498_replay_v2              | F2a_basis_funding_independent     |            18 |                 9 |             18 |           9 |            9 |         0.025     |            0.025 |
| a7ffcore33_005 | top498_replay_v2              | F2a_basis_funding_independent     |          3108 |                48 |            482 |        1554 |         1554 |         0.0232947 |            0.025 |
| a7ffcore33_006 | top498_replay_v2              | F1b_taker_flow_market_panel       |          3108 |                48 |            399 |        1554 |         1554 |         0.0232947 |            0.025 |
| a7ffcore33_007 | core12_aggtrades_all_features | F1a_aggtrades_flow_microstructure |            96 |                48 |              5 |          48 |           48 |         0.025     |            0.025 |
| a7ffcore33_008 | core12_aggtrades_all_features | F1a_aggtrades_flow_microstructure |            96 |                48 |              5 |          48 |           48 |         0.025     |            0.025 |
| a7ffcore33_009 | top498_replay_v2              | F2a_basis_funding_independent     |            28 |                14 |             20 |          14 |           14 |         0.025     |            0.025 |
| a7ffcore33_010 | top498_replay_v2              | F2a_basis_funding_independent     |            14 |                 7 |             14 |           7 |            7 |         0.025     |            0.025 |
| a7ffcore33_011 | top498_replay_v2              | F2a_basis_funding_independent     |          3116 |                48 |            488 |        1558 |         1558 |         0.0232831 |            0.025 |
| a7ffcore33_012 | top498_replay_v2              | F1b_taker_flow_market_panel       |          3116 |                48 |            483 |        1558 |         1558 |         0.0232831 |            0.025 |
| a7ffcore33_013 | top498_replay_v2              | F2a_basis_funding_independent     |          3114 |                48 |            466 |        1557 |         1557 |         0.023298  |            0.025 |
| a7ffcore33_014 | top498_replay_v2              | F1b_taker_flow_market_panel       |            14 |                 7 |             12 |           7 |            7 |         0.025     |            0.025 |
| a7ffcore33_015 | core12_aggtrades_all_features | F1a_aggtrades_flow_microstructure |            96 |                48 |              5 |          48 |           48 |         0.025     |            0.025 |
| a7ffcore33_016 | core12_aggtrades_all_features | F1a_aggtrades_flow_microstructure |            96 |                48 |              5 |          48 |           48 |         0.025     |            0.025 |
| a7ffcore33_017 | core12_aggtrades_all_features | F1a_aggtrades_flow_microstructure |            96 |                48 |              5 |          48 |           48 |         0.025     |            0.025 |
| a7ffcore33_018 | core12_aggtrades_all_features | F1a_aggtrades_flow_microstructure |            96 |                48 |              5 |          48 |           48 |         0.025     |            0.025 |
| a7ffcore33_019 | top498_replay_v2              | F1b_taker_flow_market_panel       |            24 |                12 |             19 |          12 |           12 |         0.025     |            0.025 |
| a7ffcore33_020 | core12_aggtrades_all_features | F1a_aggtrades_flow_microstructure |            96 |                48 |              5 |          48 |           48 |         0.025     |            0.025 |

## External Artifact

| artifact                     | path                                                                                                                                      | committed_to_git   |   rows |   columns |   bytes |
|:-----------------------------|:------------------------------------------------------------------------------------------------------------------------------------------|:-------------------|-------:|----------:|--------:|
| orthogonal_book_input_packet | G:/AlphaFactory_CryptoData/research_runtime/a7ffcore44e_orthogonal_score_packet_20260602/a7ffcore44e_orthogonal_book_input_packet.parquet | False              |  22600 |        21 | 1661106 |

## Authorization

```json
{
  "authorized": {
    "A7FF-CORE45 bounded orthogonal book replay contract": true
  },
  "not_authorized": {
    "alpha_proof": true,
    "book_replay_execution": true,
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
  "authorizes_core45_contract": true,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "candidate_count": 21,
  "decision": "PASS_A7FFCORE44E_ORTHOGONAL_SCORE_PACKET_READY_FOR_CORE45_CONTRACT",
  "executes_new_generation": false,
  "executes_replay": false,
  "executes_search": false,
  "external_packet_path": "G:/AlphaFactory_CryptoData/research_runtime/a7ffcore44e_orthogonal_score_packet_20260602/a7ffcore44e_orthogonal_book_input_packet.parquet",
  "generated_at": "2026-06-01T20:47:57Z",
  "next_allowed": "A7FF-CORE45 bounded orthogonal book replay contract",
  "packet_rows": 22600,
  "source_decision": "PASS_A7FFCORE44_ORTHOGONAL_SCORE_PACKET_CONTRACT_READY_FOR_CORE44E",
  "source_stage": "A7FF-CORE44",
  "source_vector_rows": 255236,
  "stage": "A7FF-CORE44E"
}
```
