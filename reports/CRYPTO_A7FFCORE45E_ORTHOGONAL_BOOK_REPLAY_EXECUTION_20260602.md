# CRYPTO A7FF-CORE45E ORTHOGONAL BOOK REPLAY EXECUTION

Generated: 2026-06-01T20:54:34Z

## Decision

`HOLD_A7FFCORE45E_ORTHOGONAL_BOOK_REPLAY_INSUFFICIENT`

CORE45E executes bounded book replay over CORE43E/CORE44E orthogonal score inputs. It does not run formula generation, formula search, large search, alpha proof, shadow, paper, live, or promotion.

## Summary

- vector_rows: `255236`
- packet_variant_rows: `171086`
- book_replay_rows: `600`
- survivor_count: `0`
- survivor_family_count: `0`

## Objective Summary

| objective_id                      |   replay_rows |   positive_rows |   control_clean_rows |   median_net_book_return |   median_control_ratio |
|:----------------------------------|--------------:|----------------:|---------------------:|-------------------------:|-----------------------:|
| OB1_cross_sectional_relative_book |           150 |              62 |                   13 |             -0.000535428 |                3.31741 |
| OB2_market_beta_residual_book     |           150 |              62 |                   13 |             -0.000535428 |                3.31741 |
| OB3_liquidity_tier_relative_book  |           150 |              71 |                   18 |             -0.00020749  |                3.59816 |
| OB4_vol_adjusted_book             |           150 |              79 |                   17 |              0.00944912  |                3.66072 |

## Family Summary

| family_id                         |   candidate_count |   survivor_count |   median_net_book_return |   median_control_ratio |
|:----------------------------------|------------------:|-----------------:|-------------------------:|-----------------------:|
| F1a_aggtrades_flow_microstructure |                 7 |                0 |             -0.000885987 |                2.54262 |
| F1b_taker_flow_market_panel       |                 6 |                0 |             -0.000636285 |               10.2163  |
| F2a_basis_funding_independent     |                 8 |                0 |              0.00114791  |                4.46114 |

## Survivors

`<empty>`

## Candidate Summary

| candidate_id   | family_id                         |   replay_rows |   positive_rows |   control_clean_rows |   split_pass_rows |   median_net_book_return |   median_control_ratio |   train_split_pass_count |   train_median_net_book_return |   train_median_control_ratio |   oos_split_count |   oos_positive_split_count |   oos_control_clean_split_count |   oos_min_net_book_return |   oos_worst_control_ratio | book_survivor   |
|:---------------|:----------------------------------|--------------:|----------------:|---------------------:|------------------:|-------------------------:|-----------------------:|-------------------------:|-------------------------------:|-----------------------------:|------------------:|---------------------------:|--------------------------------:|--------------------------:|--------------------------:|:----------------|
| a7ffcore33_000 | F1b_taker_flow_market_panel       |            32 |              15 |                   12 |                 4 |             -0.00584817  |                1.40082 |                        1 |                    0.0339455   |                      1.83295 |                 3 |                          2 |                               1 |              -0.05323     |                   2.62369 | False           |
| a7ffcore33_001 | F1b_taker_flow_market_panel       |            24 |              18 |                    0 |                 0 |              0.000286374 |               75.088   |                      nan |                  nan           |                    nan       |                 3 |                          2 |                               0 |              -0.000600503 |                 111.124   | False           |
| a7ffcore33_002 | F2a_basis_funding_independent     |            24 |              19 |                    0 |                 0 |              0.00116024  |                8.7907  |                      nan |                  nan           |                    nan       |                 3 |                          2 |                               0 |              -0.00341264  |                  31.1875  | False           |
| a7ffcore33_003 | F2a_basis_funding_independent     |            32 |              21 |                    1 |                 1 |              0.0202444   |                1.87575 |                        0 |                   -0.0735536   |                      1.76061 |                 3 |                          3 |                               0 |               0.0200071   |                   4.28757 | False           |
| a7ffcore33_004 | F2a_basis_funding_independent     |            24 |              12 |                    0 |                 0 |              0.000107316 |               23.6101  |                      nan |                  nan           |                    nan       |                 3 |                          1 |                               0 |              -0.00075024  |                  53.0315  | False           |
| a7ffcore33_005 | F2a_basis_funding_independent     |            32 |              22 |                    0 |                 0 |              0.0234557   |                2.52188 |                        0 |                    0.0416172   |                      1.79181 |                 3 |                          2 |                               0 |              -0.00764537  |                  11.3788  | False           |
| a7ffcore33_006 | F1b_taker_flow_market_panel       |            32 |              22 |                    6 |                 0 |              0.0157591   |                1.49959 |                        0 |                    0.0557247   |                      1.54178 |                 3 |                          2 |                               1 |              -0.0787517   |                   6.34914 | False           |
| a7ffcore33_007 | F1a_aggtrades_flow_microstructure |            32 |               8 |                    4 |                 2 |             -0.000885987 |                3.71292 |                        0 |                   -0.00517605  |                      4.15665 |                 3 |                          1 |                               0 |              -0.00133408  |                   5.2834  | False           |
| a7ffcore33_008 | F1a_aggtrades_flow_microstructure |            32 |              11 |                    6 |                 1 |             -0.000684119 |                2.03359 |                        1 |                   -0.00260552  |                      3.20884 |                 3 |                          1 |                               0 |              -0.00300195  |                   2.99597 | False           |
| a7ffcore33_009 | F2a_basis_funding_independent     |            24 |              15 |                    0 |                 0 |              0.00113557  |               17.0483  |                      nan |                  nan           |                    nan       |                 3 |                          2 |                               0 |              -0.00250975  |                  62.5938  | False           |
| a7ffcore33_010 | F2a_basis_funding_independent     |            16 |               5 |                    0 |                 0 |             -0.00559506  |                5.77732 |                      nan |                  nan           |                    nan       |                 2 |                          1 |                               0 |              -0.0154167   |                  70.9573  | False           |
| a7ffcore33_011 | F2a_basis_funding_independent     |            32 |              10 |                    6 |                 1 |             -0.00859581  |                3.14496 |                        0 |                   -0.0963467   |                      1.07486 |                 3 |                          1 |                               0 |              -0.010238    |                   9.57441 | False           |
| a7ffcore33_012 | F1b_taker_flow_market_panel       |            32 |              17 |                    5 |                 1 |              0.00836853  |                2.78239 |                        0 |                   -0.00712218  |                      4.68744 |                 3 |                          2 |                               0 |              -0.0187337   |                   3.48311 | False           |
| a7ffcore33_013 | F2a_basis_funding_independent     |            32 |              18 |                    0 |                 0 |              0.01864     |                1.76568 |                        0 |                   -0.0493936   |                      3.00174 |                 3 |                          2 |                               0 |              -0.0291002   |                   4.51271 | False           |
| a7ffcore33_014 | F1b_taker_flow_market_panel       |            16 |               8 |                    0 |                 0 |             -0.00155894  |               17.6503  |                      nan |                  nan           |                    nan       |                 2 |                          1 |                               0 |              -0.005677    |                  23.074   | False           |
| a7ffcore33_015 | F1a_aggtrades_flow_microstructure |            32 |               3 |                    6 |                 0 |             -0.00163446  |                2.13159 |                        0 |                   -0.00148505  |                      6.67563 |                 3 |                          0 |                               0 |              -0.00275816  |                   2.83321 | False           |
| a7ffcore33_016 | F1a_aggtrades_flow_microstructure |            32 |              18 |                    1 |                 0 |              0.000112761 |                4.12155 |                        0 |                    0.000525461 |                      6.41593 |                 3 |                          2 |                               0 |              -0.0015922   |                   6.92943 | False           |
| a7ffcore33_017 | F1a_aggtrades_flow_microstructure |            32 |               8 |                    8 |                 2 |             -0.00193945  |                1.75552 |                        0 |                   -0.00308438  |                      3.72191 |                 3 |                          1 |                               0 |              -0.00230809  |                   2.10393 | False           |
| a7ffcore33_018 | F1a_aggtrades_flow_microstructure |            32 |               8 |                    3 |                 0 |             -0.000629548 |                3.40841 |                        0 |                   -0.000383799 |                      6.31851 |                 3 |                          0 |                               0 |              -0.00139602  |                   4.77162 | False           |
| a7ffcore33_019 | F1b_taker_flow_market_panel       |            24 |              11 |                    0 |                 0 |             -0.00177772  |               18.0762  |                      nan |                  nan           |                    nan       |                 3 |                          1 |                               0 |              -0.00404733  |                  34.356   | False           |
| a7ffcore33_020 | F1a_aggtrades_flow_microstructure |            32 |               5 |                    3 |                 1 |             -0.00169555  |                2.54262 |                        0 |                   -0.00485666  |                      2.55175 |                 3 |                          0 |                               0 |              -0.00295601  |                   9.0234  | False           |

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core45r_forensic": true,
  "authorizes_core46_arbitration": false,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "book_replay_rows": 600,
  "decision": "HOLD_A7FFCORE45E_ORTHOGONAL_BOOK_REPLAY_INSUFFICIENT",
  "executes_replay": true,
  "executes_search": false,
  "generated_at": "2026-06-01T20:54:34Z",
  "next_allowed": "A7FF-CORE45R orthogonal book replay forensic",
  "packet_variant_rows": 171086,
  "source_decision": "PASS_A7FFCORE45_ORTHOGONAL_BOOK_REPLAY_CONTRACT_READY_FOR_CORE45E",
  "source_stage": "A7FF-CORE45",
  "stage": "A7FF-CORE45E",
  "survivor_count": 0,
  "survivor_family_count": 0,
  "vector_rows": 255236
}
```
