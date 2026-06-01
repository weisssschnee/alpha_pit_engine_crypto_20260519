# CRYPTO A7FF-CORE34 ORIENTATION/CONTROL REPAIR CONTRACT

Generated: 2026-06-01T19:25:47Z

## Decision

`PASS_A7FFCORE34_ORIENTATION_CONTROL_REPAIR_CONTRACT_READY_FOR_CORE34E`

CORE34 defines a train-only orientation and control repair path after CORE33E bounded replay failed. It does not execute new generation, search, large search, alpha proof, shadow, paper, or live.

## Gate Audit

| gate                   | threshold   |   observed | pass   |
|:-----------------------|:------------|-----------:|:-------|
| repair_candidate_count | >= 6        |         14 | True   |
| repair_family_count    | >= 2        |          3 | True   |
| orientation_candidates | >= 1        |          6 | True   |

## Family Summary

| family_id                         | repair_mode            |   candidate_count |
|:----------------------------------|:-----------------------|------------------:|
| F1a_aggtrades_flow_microstructure | train_only_orientation |                 6 |
| F1b_taker_flow_market_panel       | control_filter         |                 3 |
| F2a_basis_funding_independent     | control_filter         |                 5 |

## Repair Protocol

| step                  | rule                                                                             | blocking   |
|:----------------------|:---------------------------------------------------------------------------------|:-----------|
| train_orientation_fit | fit sign only on train_2024 using L1/L5 net spread; freeze sign for later splits | True       |
| control_filter        | reject candidate if train_2024 stale-control ratio >= 1.0 after orientation      | True       |
| multi_cost_report     | report 2/5/10bps net spread by split and label                                   | True       |
| no_test_orientation   | validation/test/recent may evaluate only; cannot set sign or thresholds          | True       |
| no_search             | repair execution is bounded replay repair only, not formula generation/search    | True       |

## Repair Candidate Queue

| replay_candidate_id   | family_id                         | repair_mode            |   positive_net_count |   control_clean_count |   median_control_ratio |   median_net_spread |
|:----------------------|:----------------------------------|:-----------------------|---------------------:|----------------------:|-----------------------:|--------------------:|
| a7ffcore33_006        | F1b_taker_flow_market_panel       | control_filter         |                   18 |                    12 |               2.79078  |        -3.60091e-06 |
| a7ffcore33_010        | F2a_basis_funding_independent     | control_filter         |                   16 |                    17 |               1.03857  |        -6.38836e-05 |
| a7ffcore33_005        | F2a_basis_funding_independent     | control_filter         |                   16 |                    12 |               3.54048  |        -1.9923e-05  |
| a7ffcore33_001        | F1b_taker_flow_market_panel       | control_filter         |                   15 |                    17 |               1.03583  |        -4.01809e-05 |
| a7ffcore33_002        | F2a_basis_funding_independent     | control_filter         |                   15 |                    17 |               1.05066  |        -6.49614e-05 |
| a7ffcore33_011        | F2a_basis_funding_independent     | control_filter         |                   14 |                    12 |               3.47901  |        -4.83681e-05 |
| a7ffcore33_012        | F1b_taker_flow_market_panel       | control_filter         |                   14 |                    12 |               4.1506   |        -6.79842e-05 |
| a7ffcore33_013        | F2a_basis_funding_independent     | control_filter         |                   14 |                    12 |               5.66474  |        -9.48116e-05 |
| a7ffcore33_016        | F1a_aggtrades_flow_microstructure | train_only_orientation |                    9 |                    22 |               0.672973 |        -0.000146226 |
| a7ffcore33_008        | F1a_aggtrades_flow_microstructure | train_only_orientation |                    8 |                    22 |               0.747379 |        -0.000163599 |
| a7ffcore33_020        | F1a_aggtrades_flow_microstructure | train_only_orientation |                    8 |                    20 |               0.581048 |        -0.000183566 |
| a7ffcore33_017        | F1a_aggtrades_flow_microstructure | train_only_orientation |                    7 |                    19 |               0.89882  |        -0.000195411 |
| a7ffcore33_018        | F1a_aggtrades_flow_microstructure | train_only_orientation |                    7 |                    18 |               0.976737 |        -0.000163813 |
| a7ffcore33_015        | F1a_aggtrades_flow_microstructure | train_only_orientation |                    5 |                    20 |               0.714535 |        -0.000220182 |

## Authorization

```json
{
  "authorized": {
    "A7FF-CORE34E train-only orientation/control repair execution": true
  },
  "not_authorized": {
    "alpha_proof": true,
    "large_search": true,
    "new_formula_generation": true,
    "shadow_paper_live": true
  }
}
```

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core34e_execution": true,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE34_ORIENTATION_CONTROL_REPAIR_CONTRACT_READY_FOR_CORE34E",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T19:25:47Z",
  "next_allowed": "A7FF-CORE34E train-only orientation/control repair execution",
  "repair_candidate_count": 14,
  "repair_family_count": 3,
  "source_decision": "PASS_A7FFCORE33ER_FORENSIC_READY_FOR_CORE34_ORIENTATION_REPAIR_CONTRACT",
  "source_stage": "A7FF-CORE33ER",
  "stage": "A7FF-CORE34"
}
```
