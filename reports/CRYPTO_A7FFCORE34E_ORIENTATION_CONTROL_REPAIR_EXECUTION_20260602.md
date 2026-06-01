# CRYPTO A7FF-CORE34E ORIENTATION/CONTROL REPAIR EXECUTION

Generated: 2026-06-01T19:30:07Z

## Decision

`HOLD_A7FFCORE34E_REPAIR_INSUFFICIENT`

CORE34E applies train-only orientation and train control filtering to bounded replay repair candidates. It does not execute search, large search, alpha proof, shadow, paper, or live.

## Summary

- repair_candidate_count: `14`
- survivor_count: `0`
- survivor_family_count: `0`

## Family Summary

| family_id                         |   repair_candidate_count |   survivor_count |   median_oos_positive_count |   median_oos_control_clean_count |   median_repaired_net_spread |
|:----------------------------------|-------------------------:|-----------------:|----------------------------:|---------------------------------:|-----------------------------:|
| F1a_aggtrades_flow_microstructure |                        6 |                0 |                         3.5 |                             15.5 |                 -0.000173689 |
| F1b_taker_flow_market_panel       |                        3 |                0 |                        11   |                              9   |                 -4.01809e-05 |
| F2a_basis_funding_independent     |                        5 |                0 |                        11   |                              9   |                 -6.38836e-05 |

## Survivors

`<empty>`

## Candidate Summary Preview

| replay_candidate_id   | family_id                         | train_control_filter_pass   |   orientation_sign |   repaired_positive_count |   repaired_control_clean_count |   oos_positive_count |   oos_control_clean_count |   median_repaired_net_spread |   train_median_control_ratio |   recent_2026JanApr |   test_2025H2 |   train_2024 |   validation_2025H1 | all_oos_splits_positive   |
|:----------------------|:----------------------------------|:----------------------------|-------------------:|--------------------------:|-------------------------------:|---------------------:|--------------------------:|-----------------------------:|-----------------------------:|--------------------:|--------------:|-------------:|--------------------:|:--------------------------|
| a7ffcore33_010        | F2a_basis_funding_independent     | False                       |                  1 |                        16 |                             17 |                   13 |                        14 |                 -6.38836e-05 |                     2.45333  |                   4 |             9 |            3 |                   0 | False                     |
| a7ffcore33_006        | F1b_taker_flow_market_panel       | False                       |                  1 |                        18 |                             12 |                   13 |                         9 |                 -3.60091e-06 |                     1.72987  |                   7 |             3 |            5 |                   3 | True                      |
| a7ffcore33_005        | F2a_basis_funding_independent     | False                       |                  1 |                        16 |                             12 |                   13 |                         9 |                 -1.9923e-05  |                     3.13778  |                   7 |             3 |            3 |                   3 | True                      |
| a7ffcore33_002        | F2a_basis_funding_independent     | False                       |                  1 |                        15 |                             17 |                   11 |                        15 |                 -6.49614e-05 |                     3.4921   |                   2 |             9 |            4 |                   0 | False                     |
| a7ffcore33_001        | F1b_taker_flow_market_panel       | False                       |                  1 |                        15 |                             17 |                   11 |                        14 |                 -4.01809e-05 |                     1.52304  |                   2 |             9 |            4 |                   0 | False                     |
| a7ffcore33_011        | F2a_basis_funding_independent     | False                       |                  1 |                        14 |                             12 |                   11 |                         9 |                 -4.83681e-05 |                     1.47611  |                   5 |             3 |            3 |                   3 | True                      |
| a7ffcore33_012        | F1b_taker_flow_market_panel       | False                       |                  1 |                        14 |                             12 |                   11 |                         9 |                 -6.79842e-05 |                     2.11123  |                   5 |             3 |            3 |                   3 | True                      |
| a7ffcore33_013        | F2a_basis_funding_independent     | False                       |                  1 |                        14 |                             12 |                   11 |                         9 |                 -9.48116e-05 |                     5.15591  |                   5 |             3 |            3 |                   3 | True                      |
| a7ffcore33_020        | F1a_aggtrades_flow_microstructure | False                       |                  1 |                         8 |                             20 |                    5 |                        17 |                 -0.000183566 |                     1.90546  |                   0 |             1 |            3 |                   4 | False                     |
| a7ffcore33_008        | F1a_aggtrades_flow_microstructure | False                       |                  1 |                         8 |                             22 |                    4 |                        18 |                 -0.000163599 |                     1.07996  |                   0 |             2 |            4 |                   2 | False                     |
| a7ffcore33_016        | F1a_aggtrades_flow_microstructure | True                        |                  1 |                         9 |                             22 |                    4 |                        15 |                 -0.000146226 |                     0.346388 |                   0 |             0 |            5 |                   4 | False                     |
| a7ffcore33_018        | F1a_aggtrades_flow_microstructure | False                       |                  1 |                         7 |                             18 |                    3 |                        15 |                 -0.000163813 |                     1.5357   |                   0 |             1 |            4 |                   2 | False                     |
| a7ffcore33_017        | F1a_aggtrades_flow_microstructure | False                       |                  1 |                         7 |                             19 |                    3 |                        15 |                 -0.000195411 |                     1.01569  |                   0 |             2 |            4 |                   1 | False                     |
| a7ffcore33_015        | F1a_aggtrades_flow_microstructure | True                        |                  1 |                         5 |                             20 |                    1 |                        16 |                 -0.000220182 |                     0.830265 |                   0 |             1 |            4 |                   0 | False                     |

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core35_arbitration": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "HOLD_A7FFCORE34E_REPAIR_INSUFFICIENT",
  "executes_replay_repair": true,
  "executes_search": false,
  "generated_at": "2026-06-01T19:30:07Z",
  "next_allowed": "CORE34E repair forensic",
  "repair_candidate_count": 14,
  "source_decision": "PASS_A7FFCORE34_ORIENTATION_CONTROL_REPAIR_CONTRACT_READY_FOR_CORE34E",
  "source_stage": "A7FF-CORE34",
  "stage": "A7FF-CORE34E",
  "survivor_count": 0,
  "survivor_family_count": 0
}
```
