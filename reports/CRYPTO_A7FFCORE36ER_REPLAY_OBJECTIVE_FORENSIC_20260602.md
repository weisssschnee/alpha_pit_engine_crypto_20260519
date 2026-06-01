# CRYPTO A7FF-CORE36ER REPLAY OBJECTIVE RESET FORENSIC

Generated: 2026-06-01T19:43:07Z

## Decision

`PASS_A7FFCORE36ER_REPLAY_OBJECTIVE_FORENSIC_COMPLETE_READY_FOR_CORE37X`

CORE36ER freezes the CORE36E failure. It does not run replay, formula search, large search, alpha proof, shadow, paper, or live.

## Main Finding

`train_to_oos_executable_spread_instability_after_control_gating`

Only F1a produced train objective pass rows, and those rows failed OOS split balance. F1b/F2a are primarily train objective/control failures under the executable-spread-first reset.

## Global Failure Counts

| failure_reason         |   candidate_count |
|:-----------------------|------------------:|
| train_objective_fail   |                18 |
| oos_split_balance_fail |                 3 |

## Family Diagnosis

| family_id                         |   candidate_count |   train_objective_pass_count |   selected_count |   strict_survivor_count |   median_train_net_spread |   median_train_control_ratio |   median_oos_min_split_net_spread |   median_oos_worst_control_ratio | diagnosis                             |
|:----------------------------------|------------------:|-----------------------------:|-----------------:|------------------------:|--------------------------:|-----------------------------:|----------------------------------:|---------------------------------:|:--------------------------------------|
| F1a_aggtrades_flow_microstructure |                 7 |                            3 |                0 |                       0 |               0.00156803  |                      1.07996 |                        -0.0050861 |                          1.14556 | train_positive_but_oos_split_unstable |
| F1b_taker_flow_market_panel       |                 6 |                            0 |                0 |                       0 |               0.000965976 |                      2.9462  |                        -0.0197957 |                          3.58846 | train_objective_control_fail          |
| F2a_basis_funding_independent     |                 8 |                            0 |                0 |                       0 |               0.00106681  |                      2.75882 |                        -0.0171136 |                          3.09909 | train_objective_control_fail          |

## Train-Pass OOS Failure Detail

| replay_candidate_id   | family_id                         | dataset                       | motif              | operator   | primary_field                      | partner_field        |   train_median_net_spread |   train_median_control_ratio |   oos_split_pass_count |   oos_min_split_net_spread |   oos_worst_control_ratio | failure_reason         |
|:----------------------|:----------------------------------|:------------------------------|:-------------------|:-----------|:-----------------------------------|:---------------------|--------------------------:|-----------------------------:|-----------------------:|---------------------------:|--------------------------:|:-----------------------|
| a7ffcore33_016        | F1a_aggtrades_flow_microstructure | core12_aggtrades_all_features | flow_x_dislocation | TSRank     | agg_large_notional_ratio_100k_plus | agg_price_range_bps  |               0.00271869  |                     0.346388 |                      1 |                -0.00339471 |                  3.08533  | oos_split_balance_fail |
| a7ffcore33_015        | F1a_aggtrades_flow_microstructure | core12_aggtrades_all_features | flow_reversal      | TSRank     | agg_signed_aggressor_notional      | mark_index_basis_bps |               0.00238931  |                     0.830265 |                      0 |                -0.00456838 |                  1.03382  | oos_split_balance_fail |
| a7ffcore33_017        | F1a_aggtrades_flow_microstructure | core12_aggtrades_all_features | flow_x_dislocation | TSRank     | agg_large_notional_ratio_100k_plus | premium_index_bps    |               0.000444061 |                     0.972145 |                      0 |                -0.00538005 |                  0.548205 | oos_split_balance_fail |

## Split Forensic Summary

| family_id                         | split             |   candidate_count |   split_pass_count |   median_net_spread |   median_control_ratio |   median_positive_rows |   median_control_clean_rows |
|:----------------------------------|:------------------|------------------:|-------------------:|--------------------:|-----------------------:|-----------------------:|----------------------------:|
| F1a_aggtrades_flow_microstructure | recent_2026JanApr |                 7 |                  0 |        -0.0050861   |               1.14556  |                    0   |                         2   |
| F1a_aggtrades_flow_microstructure | test_2025H2       |                 7 |                  0 |        -0.00014564  |               0.500438 |                    1   |                         3   |
| F1a_aggtrades_flow_microstructure | train_2024        |                 7 |                  3 |         0.00156803  |               1.07996  |                    2   |                         2   |
| F1a_aggtrades_flow_microstructure | validation_2025H1 |                 7 |                  2 |        -9.94448e-05 |               0.148461 |                    1   |                         4   |
| F1b_taker_flow_market_panel       | recent_2026JanApr |                 6 |                  1 |        -0.0197957   |               1.05589  |                    0.5 |                         2   |
| F1b_taker_flow_market_panel       | test_2025H2       |                 6 |                  2 |         0.00126957  |               3.14031  |                    2   |                         2   |
| F1b_taker_flow_market_panel       | train_2024        |                 6 |                  0 |         0.000965976 |               2.9462   |                    2   |                         2   |
| F1b_taker_flow_market_panel       | validation_2025H1 |                 6 |                  0 |        -0.009574    |               2.3796   |                    0   |                         2.5 |
| F2a_basis_funding_independent     | recent_2026JanApr |                 8 |                  1 |        -0.0166805   |               1.19714  |                    1   |                         2   |
| F2a_basis_funding_independent     | test_2025H2       |                 8 |                  3 |         0.00200316  |               1.51895  |                    2   |                         2   |
| F2a_basis_funding_independent     | train_2024        |                 8 |                  0 |         0.00106681  |               2.75882  |                    2   |                         2   |
| F2a_basis_funding_independent     | validation_2025H1 |                 8 |                  0 |        -0.00772508  |               1.77321  |                    0   |                         2   |

## Authorization Matrix

| task                                                                      | status                   | reason                                                                                                    |
|:--------------------------------------------------------------------------|:-------------------------|:----------------------------------------------------------------------------------------------------------|
| A7FF-CORE37X replay-objective failure freeze / route arbitration contract | AUTHORIZED_CONTRACT_ONLY | CORE36E found no executable survivors after objective reset; route decision is needed before any new work |
| same CORE33/34/36 queue rerun                                             | NOT_AUTHORIZED           | CORE36E exhausted executable-spread-first rescoring without survivors                                     |
| formula_search                                                            | NOT_AUTHORIZED           | no executable replay survivor and no family with stable train-to-OOS translation                          |
| large_search                                                              | NOT_AUTHORIZED           | numeric/preflight response still fails executable replay translation                                      |
| alpha_proof / shadow / paper / live                                       | NOT_AUTHORIZED           | no alpha proof object or replay survivor                                                                  |

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core37x_contract": true,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "candidate_count": 21,
  "decision": "PASS_A7FFCORE36ER_REPLAY_OBJECTIVE_FORENSIC_COMPLETE_READY_FOR_CORE37X",
  "dominant_failure": "train_to_oos_executable_spread_instability_after_control_gating",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T19:43:07Z",
  "next_allowed": "A7FF-CORE37X replay-objective failure freeze / route arbitration contract",
  "selected_count": 0,
  "source_decision": "HOLD_A7FFCORE36E_REPLAY_OBJECTIVE_RESET_NO_EXECUTABLE_SURVIVORS",
  "source_stage": "A7FF-CORE36E",
  "stage": "A7FF-CORE36ER",
  "strict_survivor_count": 0,
  "train_objective_pass_count": 3
}
```
