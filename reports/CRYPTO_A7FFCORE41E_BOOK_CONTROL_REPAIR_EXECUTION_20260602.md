# CRYPTO A7FF-CORE41E BOOK CONTROL REPAIR EXECUTION

Generated: 2026-06-01T20:27:49Z

## Decision

`HOLD_A7FFCORE41E_BOOK_CONTROL_REPAIR_INSUFFICIENT`

CORE41E applies train-only orientation and control repair over existing CORE40E book replay variants. It does not run generation, formula search, large search, alpha proof, shadow, paper, or live.

## Summary

- candidate_count: `21`
- survivor_count: `1`
- survivor_family_count: `1`

## Family Summary

| family_id                         |   candidate_count |   survivor_count |   median_train_net |   median_train_control_ratio |   median_oos_min_net |   median_oos_worst_control_ratio |
|:----------------------------------|------------------:|-----------------:|-------------------:|-----------------------------:|---------------------:|---------------------------------:|
| F1a_aggtrades_flow_microstructure |                 7 |                0 |          0.018461  |                      3.34567 |         -0.000143061 |                          3.48848 |
| F1b_taker_flow_market_panel       |                 6 |                1 |          0.0594005 |                      1.32887 |         -0.371526    |                          2.9344  |
| F2a_basis_funding_independent     |                 8 |                0 |          0.0275131 |                      1.94397 |         -0.100709    |                          2.37458 |

## Survivors

| candidate_id   | family_id                   |   train_pass_count |   train_median_repaired_net_book_return |   train_median_repaired_control_ratio |   oos_split_count |   oos_positive_split_count |   oos_control_clean_split_count |   oos_min_repaired_net_book_return |   oos_worst_repaired_control_ratio | repair_survivor   |
|:---------------|:----------------------------|-------------------:|----------------------------------------:|--------------------------------------:|------------------:|---------------------------:|--------------------------------:|-----------------------------------:|-----------------------------------:|:------------------|
| a7ffcore33_019 | F1b_taker_flow_market_panel |                  5 |                               0.0554675 |                              0.962044 |                 3 |                          2 |                               2 |                          -0.977796 |                            3.74763 | True              |

## Candidate Summary

| candidate_id   | family_id                         |   train_pass_count |   train_median_repaired_net_book_return |   train_median_repaired_control_ratio |   oos_split_count |   oos_positive_split_count |   oos_control_clean_split_count |   oos_min_repaired_net_book_return |   oos_worst_repaired_control_ratio | repair_survivor   |
|:---------------|:----------------------------------|-------------------:|----------------------------------------:|--------------------------------------:|------------------:|---------------------------:|--------------------------------:|-----------------------------------:|-----------------------------------:|:------------------|
| a7ffcore33_000 | F1b_taker_flow_market_panel       |                  1 |                             0.0552586   |                              1.51958  |                 3 |                          1 |                               0 |                       -0.0116846   |                            2.11045 | False             |
| a7ffcore33_001 | F1b_taker_flow_market_panel       |                  2 |                             0.113499    |                              1.13816  |                 3 |                          0 |                               0 |                       -0.735354    |                            1.58815 | False             |
| a7ffcore33_002 | F2a_basis_funding_independent     |                  4 |                             0.026161    |                              1.10971  |                 3 |                          1 |                               0 |                       -0.408736    |                            2.08616 | False             |
| a7ffcore33_003 | F2a_basis_funding_independent     |                  0 |                             0.0344789   |                              2.17554  |                 3 |                          1 |                               0 |                       -0.0898684   |                            3.35263 | False             |
| a7ffcore33_004 | F2a_basis_funding_independent     |                  0 |                             0.00681165  |                              3.78902  |                 3 |                          1 |                               0 |                       -0.137033    |                            2.0877  | False             |
| a7ffcore33_005 | F2a_basis_funding_independent     |                  1 |                             0.0288653   |                              2.62746  |                 3 |                          1 |                               2 |                       -0.0467312   |                            1.38817 | False             |
| a7ffcore33_006 | F1b_taker_flow_market_panel       |                  0 |                             0.0244849   |                              6.42521  |                 3 |                          2 |                               0 |                       -0.0312933   |                            3.76211 | False             |
| a7ffcore33_007 | F1a_aggtrades_flow_microstructure |                  1 |                             0.018461    |                              3.34567  |                 3 |                          1 |                               0 |                       -0.0330421   |                            5.79377 | False             |
| a7ffcore33_008 | F1a_aggtrades_flow_microstructure |                  1 |                             0.0142754   |                              5.73248  |                 3 |                          2 |                               1 |                       -0.147242    |                            2.27295 | False             |
| a7ffcore33_009 | F2a_basis_funding_independent     |                  0 |                             0.0195085   |                              1.56716  |                 3 |                          1 |                               1 |                       -0.0171334   |                            4.64394 | False             |
| a7ffcore33_010 | F2a_basis_funding_independent     |                  0 |                             0.00953131  |                              5.20582  |                 3 |                          1 |                               1 |                       -0.385591    |                            2.66147 | False             |
| a7ffcore33_011 | F2a_basis_funding_independent     |                  1 |                             0.0541349   |                              1.71241  |                 3 |                          2 |                               0 |                       -0.0069708   |                            4.56589 | False             |
| a7ffcore33_012 | F1b_taker_flow_market_panel       |                  0 |                             0.0633335   |                              2.50848  |                 3 |                          3 |                               0 |                        0.000319288 |                            2.12118 | False             |
| a7ffcore33_013 | F2a_basis_funding_independent     |                  0 |                             0.192417    |                              1.19439  |                 3 |                          1 |                               1 |                       -0.11155     |                            1.38288 | False             |
| a7ffcore33_014 | F1b_taker_flow_market_panel       |                  1 |                             0.148349    |                              1.13136  |                 3 |                          0 |                               2 |                       -0.711759    |                            4.97363 | False             |
| a7ffcore33_015 | F1a_aggtrades_flow_microstructure |                  0 |                            -0.000206272 |                              2.48085  |                 3 |                          2 |                               0 |                       -0.000143061 |                            4.39024 | False             |
| a7ffcore33_016 | F1a_aggtrades_flow_microstructure |                  0 |                             0.0379317   |                              3.57868  |                 3 |                          1 |                               0 |                       -0.0135762   |                            2.66205 | False             |
| a7ffcore33_017 | F1a_aggtrades_flow_microstructure |                  2 |                             0.109022    |                              1.46182  |                 3 |                          3 |                               1 |                        0.00188527  |                            4.64301 | False             |
| a7ffcore33_018 | F1a_aggtrades_flow_microstructure |                  1 |                             0.0168755   |                              4.6227   |                 3 |                          3 |                               1 |                        0.0342742   |                            1.49068 | False             |
| a7ffcore33_019 | F1b_taker_flow_market_panel       |                  5 |                             0.0554675   |                              0.962044 |                 3 |                          2 |                               2 |                       -0.977796    |                            3.74763 | True              |
| a7ffcore33_020 | F1a_aggtrades_flow_microstructure |                  0 |                             0.046785    |                              3.0025   |                 3 |                          3 |                               1 |                        0.00903037  |                            3.48848 | False             |

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core41er_forensic": true,
  "authorizes_core42_arbitration": false,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "candidate_count": 21,
  "decision": "HOLD_A7FFCORE41E_BOOK_CONTROL_REPAIR_INSUFFICIENT",
  "executes_replay_repair": true,
  "executes_search": false,
  "generated_at": "2026-06-01T20:27:49Z",
  "next_allowed": "A7FF-CORE41ER book control repair forensic",
  "source_decision": "PASS_A7FFCORE41_BOOK_CONTROL_REPAIR_CONTRACT_READY_FOR_CORE41E",
  "source_stage": "A7FF-CORE41",
  "stage": "A7FF-CORE41E",
  "survivor_count": 1,
  "survivor_family_count": 1
}
```
