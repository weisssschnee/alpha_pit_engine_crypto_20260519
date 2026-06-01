# CRYPTO A7FF-CORE34ER REPAIR FORENSIC

Generated: 2026-06-01T19:31:17Z

## Decision

`PASS_A7FFCORE34ER_REPAIR_FORENSIC_READY_FOR_CORE35_ARBITRATION`

CORE34ER freezes the failed train-only orientation/control repair. It does not execute replay, search, large search, alpha proof, shadow, paper, or live.

## Summary

- train_control_fail_count: `12`
- oos_positive_fail_count_after_train_filter: `2`

## Family Failure Diagnostic

| family_id                         | failure_mode                                 |   candidate_count |
|:----------------------------------|:---------------------------------------------|------------------:|
| F1a_aggtrades_flow_microstructure | orientation_repair_oos_positive_insufficient |                 2 |
| F1a_aggtrades_flow_microstructure | train_control_filter_fail                    |                 4 |
| F1b_taker_flow_market_panel       | train_control_filter_fail                    |                 3 |
| F2a_basis_funding_independent     | train_control_filter_fail                    |                 5 |

## Split Failure Map

| family_id                         | split             |   median_positive_count |   median_control_clean_count |   median_repaired_net_spread |   median_control_ratio |
|:----------------------------------|:------------------|------------------------:|-----------------------------:|-----------------------------:|-----------------------:|
| F1a_aggtrades_flow_microstructure | recent_2026JanApr |                       0 |                          5.5 |                 -0.000249976 |               0.514443 |
| F1a_aggtrades_flow_microstructure | test_2025H2       |                       1 |                          4   |                 -0.000192721 |               1.48     |
| F1a_aggtrades_flow_microstructure | train_2024        |                       4 |                          4   |                 -0.00010251  |               1.41218  |
| F1a_aggtrades_flow_microstructure | validation_2025H1 |                       2 |                          7   |                 -0.000141884 |               0.363436 |
| F1b_taker_flow_market_panel       | recent_2026JanApr |                       5 |                          3   |                  1.78748e-05 |               1.90221  |
| F1b_taker_flow_market_panel       | test_2025H2       |                       3 |                          3   |                 -9.53123e-06 |               3.68733  |
| F1b_taker_flow_market_panel       | train_2024        |                       4 |                          3   |                 -6.09899e-06 |               3.36294  |
| F1b_taker_flow_market_panel       | validation_2025H1 |                       3 |                          3   |                 -7.54133e-05 |               9.56149  |
| F2a_basis_funding_independent     | recent_2026JanApr |                       5 |                          3   |                  2.58349e-05 |               1.55305  |
| F2a_basis_funding_independent     | test_2025H2       |                       3 |                          3   |                 -7.88389e-06 |               3.32309  |
| F2a_basis_funding_independent     | train_2024        |                       3 |                          3   |                 -6.29331e-05 |               5.17153  |
| F2a_basis_funding_independent     | validation_2025H1 |                       3 |                          3   |                 -8.15942e-05 |               5.60362  |

## Arbitration Inputs

| evidence                   | status   | detail                                                        |
|:---------------------------|:---------|:--------------------------------------------------------------|
| numeric_probe_response     | pass     | CORE30E produced 113 numeric clues across 3 families          |
| replay_preflight           | pass     | CORE32E selected 21 preflight candidates across 3 families    |
| bounded_replay             | hold     | CORE33E survivor_count=0                                      |
| orientation_control_repair | hold     | CORE34E survivor_count=0 after train-only sign/control repair |

## Next Policy

| next_action                              | authorized   | reason                                                                                               |
|:-----------------------------------------|:-------------|:-----------------------------------------------------------------------------------------------------|
| A7FF-CORE35 search-readiness arbitration | True         | must decide whether independent-family line can justify further bounded repair or should reset again |
| large_search                             | False        | bounded replay and repair produced zero survivors                                                    |
| same_queue_rerun                         | False        | same train-only orientation/control repair exhausted without survivors                               |
| alpha_proof_shadow_paper_live            | False        | no replay survivors and no proof object                                                              |

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core35_arbitration": true,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE34ER_REPAIR_FORENSIC_READY_FOR_CORE35_ARBITRATION",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T19:31:17Z",
  "next_allowed": "A7FF-CORE35 search-readiness arbitration",
  "oos_positive_fail_count": 2,
  "source_decision": "HOLD_A7FFCORE34E_REPAIR_INSUFFICIENT",
  "source_stage": "A7FF-CORE34E",
  "stage": "A7FF-CORE34ER",
  "train_control_fail_count": 12
}
```
