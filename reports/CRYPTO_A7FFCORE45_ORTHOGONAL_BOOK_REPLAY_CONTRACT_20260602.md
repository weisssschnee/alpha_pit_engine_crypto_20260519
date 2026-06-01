# CRYPTO A7FF-CORE45 ORTHOGONAL BOOK REPLAY CONTRACT

Generated: 2026-06-01T20:52:31Z

## Decision

`PASS_A7FFCORE45_ORTHOGONAL_BOOK_REPLAY_CONTRACT_READY_FOR_CORE45E`

CORE45 defines bounded book replay over the CORE44E orthogonal score packet. It does not execute replay itself and does not authorize formula generation, large search, alpha proof, shadow, paper, live, or promotion.

## Replay Objectives

| objective_id                      | label_column                   | description                                                  | primary   |
|:----------------------------------|:-------------------------------|:-------------------------------------------------------------|:----------|
| OB1_cross_sectional_relative_book | cs_relative_return             | long/short book return using cross-sectional relative return | True      |
| OB2_market_beta_residual_book     | market_beta_residual_return    | book return after BTC/ETH market residual label              | True      |
| OB3_liquidity_tier_relative_book  | liquidity_tier_relative_return | book return relative to timestamp liquidity tier             | True      |
| OB4_vol_adjusted_book             | vol_adjusted_return            | vol-adjusted book return diagnostic                          | False     |

## Horizon Policy

|   horizon_h | role                  | description                                                                |
|------------:|:----------------------|:---------------------------------------------------------------------------|
|           8 | primary_short_horizon | shorter executable horizon used by prior CORE39/40 book packet diagnostics |
|          24 | primary_slow_horizon  | slower executable horizon used by prior CORE39/40 book packet diagnostics  |

## Replay Policy

| policy_id                      | description                                                                                            | hard_requirement   |
|:-------------------------------|:-------------------------------------------------------------------------------------------------------|:-------------------|
| P0_use_core44e_packet_only     | CORE45E must use CORE44E orthogonal packet and must not use CORE39E selected packet                    | True               |
| P1_recompute_labels_from_panel | CORE45E must attach labels from panel data at replay time; CORE44E packet contains scores/weights only | True               |
| P2_split_separated_reporting   | report train/validation/test/recent separately before any aggregate metric                             | True               |
| P3_control_rank_margin         | compare residual book against original/stale/sign/shuffle rank books where possible                    | True               |
| P4_no_search_or_promotion      | CORE45/CORE45E do not authorize formula generation, search, proof, shadow, paper, or live              | True               |

## Pass Gate

| gate                     | threshold                                                    |
|:-------------------------|:-------------------------------------------------------------|
| packet_rows_positive     | packet_rows > 0                                              |
| candidate_count_positive | candidate_count >= 4                                         |
| split_coverage           | train/validation/test/recent reported separately             |
| net_book_positive        | median net book return > 0 in at least two pre-recent splits |
| control_margin           | residual book must beat stale/sign/shuffle controls          |
| family_breadth           | survivors from >=2 families required for any later expansion |

## Execution Plan

| stage        | action                                                       | executes_replay   | executes_search   | writes_large_artifact_to_git   |
|:-------------|:-------------------------------------------------------------|:------------------|:------------------|:-------------------------------|
| A7FF-CORE45E | bounded orthogonal book replay execution over CORE44E packet | True              | False             | False                          |
| A7FF-CORE45R | if CORE45E holds, classify replay/control failure            | False             | False             | False                          |

## Authorization

```json
{
  "authorized": {
    "A7FF-CORE45E bounded orthogonal book replay execution": true
  },
  "not_authorized": {
    "alpha_proof": true,
    "formula_search": true,
    "large_search": true,
    "new_generation": true,
    "promotion": true,
    "shadow_paper_live": true
  }
}
```

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core45e_replay_execution": true,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE45_ORTHOGONAL_BOOK_REPLAY_CONTRACT_READY_FOR_CORE45E",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T20:52:31Z",
  "next_allowed": "A7FF-CORE45E bounded orthogonal book replay execution",
  "source_decision": "PASS_A7FFCORE44E_ORTHOGONAL_SCORE_PACKET_READY_FOR_CORE45_CONTRACT",
  "source_external_packet_path": "G:/AlphaFactory_CryptoData/research_runtime/a7ffcore44e_orthogonal_score_packet_20260602/a7ffcore44e_orthogonal_book_input_packet.parquet",
  "source_packet_rows": 22600,
  "source_stage": "A7FF-CORE44E",
  "stage": "A7FF-CORE45"
}
```
