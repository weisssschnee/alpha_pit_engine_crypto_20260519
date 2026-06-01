# CRYPTO A7FF-CORE33ER BOUNDED REPLAY FORENSIC

Generated: 2026-06-01T19:24:49Z

## Decision

`PASS_A7FFCORE33ER_FORENSIC_READY_FOR_CORE34_ORIENTATION_REPAIR_CONTRACT`

CORE33ER freezes the bounded replay failure. It does not execute replay, search, large search, alpha proof, shadow, paper, or live.

## Summary

- orientation_repair_candidate_count: `6`
- control_repair_candidate_count: `8`

## Family Diagnostic

| family_id                         |   candidate_count |   survivor_count |   median_control_ratio |   median_net_spread | dominant_failure                                              |
|:----------------------------------|------------------:|-----------------:|-----------------------:|--------------------:|:--------------------------------------------------------------|
| F1a_aggtrades_flow_microstructure |                 7 |                0 |               0.747379 |        -0.000183566 | direction_or_orientation_mismatch_with_control_clean_response |
| F1b_taker_flow_market_panel       |                 6 |                1 |               2.52904  |        -9.44e-05    | control_dominated_bounded_replay                              |
| F2a_basis_funding_independent     |                 8 |                0 |               2.54824  |        -7.98865e-05 | control_dominated_bounded_replay                              |

## Candidate Diagnostic Preview

| replay_candidate_id   | family_id                         |   positive_net_count |   control_clean_count |   median_control_ratio |   median_net_spread |   max_tstat |   eval_rows | orientation_repair_candidate   | control_repair_candidate   |
|:----------------------|:----------------------------------|---------------------:|----------------------:|-----------------------:|--------------------:|------------:|------------:|:-------------------------------|:---------------------------|
| a7ffcore33_006        | F1b_taker_flow_market_panel       |                   18 |                    12 |               2.79078  |        -3.60091e-06 |    11.3357  |     1916135 | False                          | True                       |
| a7ffcore33_010        | F2a_basis_funding_independent     |                   16 |                    17 |               1.03857  |        -6.38836e-05 |     5.96412 |      437875 | False                          | True                       |
| a7ffcore33_005        | F2a_basis_funding_independent     |                   16 |                    12 |               3.54048  |        -1.9923e-05  |    12.8636  |     1916135 | False                          | True                       |
| a7ffcore33_001        | F1b_taker_flow_market_panel       |                   15 |                    17 |               1.03583  |        -4.01809e-05 |     6.17149 |      439068 | False                          | True                       |
| a7ffcore33_002        | F2a_basis_funding_independent     |                   15 |                    17 |               1.05066  |        -6.49614e-05 |     6.11314 |      439068 | False                          | True                       |
| a7ffcore33_011        | F2a_basis_funding_independent     |                   14 |                    12 |               3.47901  |        -4.83681e-05 |     8.17792 |     1923659 | False                          | True                       |
| a7ffcore33_012        | F1b_taker_flow_market_panel       |                   14 |                    12 |               4.1506   |        -6.79842e-05 |     6.89391 |     1923659 | False                          | True                       |
| a7ffcore33_013        | F2a_basis_funding_independent     |                   14 |                    12 |               5.66474  |        -9.48116e-05 |     6.86986 |     1920858 | False                          | True                       |
| a7ffcore33_014        | F1b_taker_flow_market_panel       |                   11 |                    17 |               1.05849  |        -0.000120816 |     6.02542 |      437875 | False                          | False                      |
| a7ffcore33_004        | F2a_basis_funding_independent     |                   10 |                    18 |               1.00401  |        -0.000355119 |     6.06522 |      439068 | False                          | False                      |
| a7ffcore33_009        | F2a_basis_funding_independent     |                   10 |                    13 |               1.61747  |        -0.000497238 |     4.09626 |      438716 | False                          | False                      |
| a7ffcore33_016        | F1a_aggtrades_flow_microstructure |                    9 |                    22 |               0.672973 |        -0.000146226 |     5.92532 |      105192 | True                           | False                      |
| a7ffcore33_008        | F1a_aggtrades_flow_microstructure |                    8 |                    22 |               0.747379 |        -0.000163599 |     4.12931 |      105192 | True                           | False                      |
| a7ffcore33_020        | F1a_aggtrades_flow_microstructure |                    8 |                    20 |               0.581048 |        -0.000183566 |     4.20793 |      105240 | True                           | False                      |
| a7ffcore33_017        | F1a_aggtrades_flow_microstructure |                    7 |                    19 |               0.89882  |        -0.000195411 |     4.25764 |      105240 | True                           | False                      |
| a7ffcore33_018        | F1a_aggtrades_flow_microstructure |                    7 |                    18 |               0.976737 |        -0.000163813 |     4.85196 |      105000 | True                           | False                      |
| a7ffcore33_015        | F1a_aggtrades_flow_microstructure |                    5 |                    20 |               0.714535 |        -0.000220182 |     4.48931 |      105192 | True                           | False                      |
| a7ffcore33_007        | F1a_aggtrades_flow_microstructure |                    4 |                    14 |               1.58743  |        -0.000218281 |     2.91432 |      105000 | False                          | False                      |
| a7ffcore33_000        | F1b_taker_flow_market_panel       |                    4 |                    12 |              10.5412   |        -0.000138533 |     6.74817 |     1925221 | False                          | False                      |
| a7ffcore33_019        | F1b_taker_flow_market_panel       |                    3 |                    13 |               2.2673   |        -0.000929142 |     0.8098  |      438716 | False                          | False                      |
| a7ffcore33_003        | F2a_basis_funding_independent     |                    1 |                    11 |               6.35044  |        -0.000172581 |     1.55392 |     1920108 | False                          | False                      |

## Repair Plan

| repair                    | target                                    | rule                                                                           | authorized_next   |
|:--------------------------|:------------------------------------------|:-------------------------------------------------------------------------------|:------------------|
| train_only_orientation    | F1a control-clean but negative net spread | fit sign on train_2024 only, freeze sign, then evaluate validation/test/recent | True              |
| control_dominance_filter  | F1b/F2a control-dominated candidates      | drop or down-rank candidates with train control_ratio >= 1 before replay queue | True              |
| cost_turnover_sensitivity | all bounded replay candidates             | report 2/5/10bps net spread and turnover by split before replay promotion      | True              |
| large_search              | none                                      | not authorized until repaired bounded replay survivors exist                   | False             |

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core34_contract": true,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "control_repair_candidate_count": 8,
  "decision": "PASS_A7FFCORE33ER_FORENSIC_READY_FOR_CORE34_ORIENTATION_REPAIR_CONTRACT",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T19:24:49Z",
  "next_allowed": "A7FF-CORE34 train-only orientation/control repair contract",
  "orientation_repair_candidate_count": 6,
  "source_decision": "HOLD_A7FFCORE33E_BOUNDED_REPLAY_INSUFFICIENT",
  "source_stage": "A7FF-CORE33E",
  "stage": "A7FF-CORE33ER"
}
```
