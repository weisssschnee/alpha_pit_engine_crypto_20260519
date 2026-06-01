# CRYPTO A7FF-CORE45R ORTHOGONAL BOOK REPLAY FORENSIC

Generated: 2026-06-01T20:56:55Z

## Decision

`PASS_A7FFCORE45R_ORTHOGONAL_BOOK_REPLAY_FORENSIC_READY_FOR_CORE46_ROUTE_ARBITRATION`

Dominant failure: `orthogonal_book_replay_control_dominated_zero_survivors`.

CORE45R is forensic only. It does not authorize formula generation, large search, alpha proof, shadow, paper, live, or promotion.

## Objective Forensic

| objective_id                      |   replay_rows |   positive_rows |   control_clean_rows |   median_net_book_return |   median_control_ratio | failure_mode      |
|:----------------------------------|--------------:|----------------:|---------------------:|-------------------------:|-----------------------:|:------------------|
| OB1_cross_sectional_relative_book |           150 |              62 |                   13 |             -0.000535428 |                3.31741 | control_dominated |
| OB2_market_beta_residual_book     |           150 |              62 |                   13 |             -0.000535428 |                3.31741 | control_dominated |
| OB3_liquidity_tier_relative_book  |           150 |              71 |                   18 |             -0.00020749  |                3.59816 | control_dominated |
| OB4_vol_adjusted_book             |           150 |              79 |                   17 |              0.00944912  |                3.66072 | control_dominated |

## Family Forensic

| family_id                         |   candidate_count |   survivor_count |   median_net_book_return |   median_control_ratio | failure_mode                  |
|:----------------------------------|------------------:|-----------------:|-------------------------:|-----------------------:|:------------------------------|
| F1a_aggtrades_flow_microstructure |                 7 |                0 |             -0.000885987 |                2.54262 | control_dominated_no_survivor |
| F1b_taker_flow_market_panel       |                 6 |                0 |             -0.000636285 |               10.2163  | control_dominated_no_survivor |
| F2a_basis_funding_independent     |                 8 |                0 |              0.00114791  |                4.46114 | control_dominated_no_survivor |

## Route Options

| route_id                     | decision   | reason                                                                                                          |
|:-----------------------------|:-----------|:----------------------------------------------------------------------------------------------------------------|
| R0_expand_current_candidates | REJECT     | CORE45E has zero survivors after full-universe residual control orthogonalization                               |
| R1_large_search              | REJECT     | book objective remains control dominated; search would amplify control-like structures                          |
| R2_same_family_rerun         | REJECT     | F1a/F1b/F2a all have zero survivors and median control ratio above one                                          |
| R3_route_arbitration         | SELECT     | freeze current orthogonal book replay failure and choose between label/control redesign or new objective family |

## Candidate Forensic

| candidate_id   | family_id                         |   replay_rows |   positive_rows |   control_clean_rows |   split_pass_rows |   median_net_book_return |   median_control_ratio |   train_split_pass_count |   train_median_net_book_return |   train_median_control_ratio |   oos_split_count |   oos_positive_split_count |   oos_control_clean_split_count |   oos_min_net_book_return |   oos_worst_control_ratio | book_survivor   | failure_mode      |
|:---------------|:----------------------------------|--------------:|----------------:|---------------------:|------------------:|-------------------------:|-----------------------:|-------------------------:|-------------------------------:|-----------------------------:|------------------:|---------------------------:|--------------------------------:|--------------------------:|--------------------------:|:----------------|:------------------|
| a7ffcore33_000 | F1b_taker_flow_market_panel       |            32 |              15 |                   12 |                 4 |             -0.00584817  |                1.40082 |                        1 |                    0.0339455   |                      1.83295 |                 3 |                          2 |                               1 |              -0.05323     |                   2.62369 | False           | control_dominated |
| a7ffcore33_001 | F1b_taker_flow_market_panel       |            24 |              18 |                    0 |                 0 |              0.000286374 |               75.088   |                      nan |                  nan           |                    nan       |                 3 |                          2 |                               0 |              -0.000600503 |                 111.124   | False           | control_dominated |
| a7ffcore33_002 | F2a_basis_funding_independent     |            24 |              19 |                    0 |                 0 |              0.00116024  |                8.7907  |                      nan |                  nan           |                    nan       |                 3 |                          2 |                               0 |              -0.00341264  |                  31.1875  | False           | control_dominated |
| a7ffcore33_003 | F2a_basis_funding_independent     |            32 |              21 |                    1 |                 1 |              0.0202444   |                1.87575 |                        0 |                   -0.0735536   |                      1.76061 |                 3 |                          3 |                               0 |               0.0200071   |                   4.28757 | False           | control_dominated |
| a7ffcore33_004 | F2a_basis_funding_independent     |            24 |              12 |                    0 |                 0 |              0.000107316 |               23.6101  |                      nan |                  nan           |                    nan       |                 3 |                          1 |                               0 |              -0.00075024  |                  53.0315  | False           | control_dominated |
| a7ffcore33_005 | F2a_basis_funding_independent     |            32 |              22 |                    0 |                 0 |              0.0234557   |                2.52188 |                        0 |                    0.0416172   |                      1.79181 |                 3 |                          2 |                               0 |              -0.00764537  |                  11.3788  | False           | control_dominated |
| a7ffcore33_006 | F1b_taker_flow_market_panel       |            32 |              22 |                    6 |                 0 |              0.0157591   |                1.49959 |                        0 |                    0.0557247   |                      1.54178 |                 3 |                          2 |                               1 |              -0.0787517   |                   6.34914 | False           | control_dominated |
| a7ffcore33_007 | F1a_aggtrades_flow_microstructure |            32 |               8 |                    4 |                 2 |             -0.000885987 |                3.71292 |                        0 |                   -0.00517605  |                      4.15665 |                 3 |                          1 |                               0 |              -0.00133408  |                   5.2834  | False           | control_dominated |
| a7ffcore33_008 | F1a_aggtrades_flow_microstructure |            32 |              11 |                    6 |                 1 |             -0.000684119 |                2.03359 |                        1 |                   -0.00260552  |                      3.20884 |                 3 |                          1 |                               0 |              -0.00300195  |                   2.99597 | False           | control_dominated |
| a7ffcore33_009 | F2a_basis_funding_independent     |            24 |              15 |                    0 |                 0 |              0.00113557  |               17.0482  |                      nan |                  nan           |                    nan       |                 3 |                          2 |                               0 |              -0.00250975  |                  62.5938  | False           | control_dominated |
| a7ffcore33_010 | F2a_basis_funding_independent     |            16 |               5 |                    0 |                 0 |             -0.00559506  |                5.77732 |                      nan |                  nan           |                    nan       |                 2 |                          1 |                               0 |              -0.0154167   |                  70.9573  | False           | control_dominated |
| a7ffcore33_011 | F2a_basis_funding_independent     |            32 |              10 |                    6 |                 1 |             -0.00859581  |                3.14496 |                        0 |                   -0.0963467   |                      1.07486 |                 3 |                          1 |                               0 |              -0.010238    |                   9.57441 | False           | control_dominated |
| a7ffcore33_012 | F1b_taker_flow_market_panel       |            32 |              17 |                    5 |                 1 |              0.00836853  |                2.78239 |                        0 |                   -0.00712218  |                      4.68744 |                 3 |                          2 |                               0 |              -0.0187337   |                   3.48311 | False           | control_dominated |
| a7ffcore33_013 | F2a_basis_funding_independent     |            32 |              18 |                    0 |                 0 |              0.01864     |                1.76568 |                        0 |                   -0.0493936   |                      3.00175 |                 3 |                          2 |                               0 |              -0.0291002   |                   4.51271 | False           | control_dominated |
| a7ffcore33_014 | F1b_taker_flow_market_panel       |            16 |               8 |                    0 |                 0 |             -0.00155894  |               17.6503  |                      nan |                  nan           |                    nan       |                 2 |                          1 |                               0 |              -0.005677    |                  23.074   | False           | control_dominated |
| a7ffcore33_015 | F1a_aggtrades_flow_microstructure |            32 |               3 |                    6 |                 0 |             -0.00163446  |                2.13159 |                        0 |                   -0.00148505  |                      6.67563 |                 3 |                          0 |                               0 |              -0.00275816  |                   2.83321 | False           | control_dominated |
| a7ffcore33_016 | F1a_aggtrades_flow_microstructure |            32 |              18 |                    1 |                 0 |              0.000112761 |                4.12155 |                        0 |                    0.000525461 |                      6.41593 |                 3 |                          2 |                               0 |              -0.0015922   |                   6.92943 | False           | control_dominated |
| a7ffcore33_017 | F1a_aggtrades_flow_microstructure |            32 |               8 |                    8 |                 2 |             -0.00193945  |                1.75552 |                        0 |                   -0.00308438  |                      3.72191 |                 3 |                          1 |                               0 |              -0.00230809  |                   2.10393 | False           | control_dominated |
| a7ffcore33_018 | F1a_aggtrades_flow_microstructure |            32 |               8 |                    3 |                 0 |             -0.000629548 |                3.40841 |                        0 |                   -0.000383799 |                      6.31851 |                 3 |                          0 |                               0 |              -0.00139602  |                   4.77162 | False           | control_dominated |
| a7ffcore33_019 | F1b_taker_flow_market_panel       |            24 |              11 |                    0 |                 0 |             -0.00177772  |               18.0762  |                      nan |                  nan           |                    nan       |                 3 |                          1 |                               0 |              -0.00404733  |                  34.356   | False           | control_dominated |
| a7ffcore33_020 | F1a_aggtrades_flow_microstructure |            32 |               5 |                    3 |                 1 |             -0.00169555  |                2.54262 |                        0 |                   -0.00485666  |                      2.55175 |                 3 |                          0 |                               0 |              -0.00295601  |                   9.0234  | False           | control_dominated |

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core46_route_arbitration": true,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE45R_ORTHOGONAL_BOOK_REPLAY_FORENSIC_READY_FOR_CORE46_ROUTE_ARBITRATION",
  "dominant_failure": "orthogonal_book_replay_control_dominated_zero_survivors",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T20:56:55Z",
  "next_allowed": "A7FF-CORE46 orthogonal replay failure route arbitration",
  "source_decision": "HOLD_A7FFCORE45E_ORTHOGONAL_BOOK_REPLAY_INSUFFICIENT",
  "source_stage": "A7FF-CORE45E",
  "stage": "A7FF-CORE45R",
  "survivor_count": 0,
  "survivor_family_count": 0
}
```
