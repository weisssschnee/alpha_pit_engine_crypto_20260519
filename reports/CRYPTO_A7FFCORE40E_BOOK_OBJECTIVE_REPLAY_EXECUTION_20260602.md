# CRYPTO A7FF-CORE40E BOOK OBJECTIVE REPLAY EXECUTION

Generated: 2026-06-01T20:23:52Z

## Decision

`HOLD_A7FFCORE40E_BOOK_OBJECTIVE_REPLAY_INSUFFICIENT`

CORE40E executes bounded book-objective replay over the CORE39E symbol-level sample packet. It does not run formula search, large search, alpha proof, shadow, paper, or live.

## Summary

- packet_rows: `623160`
- book_replay_rows: `672`
- survivor_count: `0`
- survivor_family_count: `0`

## Objective Summary

| objective_id                  |   replay_rows |   positive_rows |   control_clean_rows |   median_net_book_return |   median_control_ratio |
|:------------------------------|--------------:|----------------:|---------------------:|-------------------------:|-----------------------:|
| B1_cross_sectional_rank_book  |           168 |              88 |                   46 |               0.0040954  |                1.56025 |
| B2_market_beta_residual_book  |           168 |              86 |                   47 |               0.00315561 |                1.58252 |
| B3_vol_adjusted_rank_book     |           168 |              87 |                   47 |               0.14006    |                1.33276 |
| B4_liquidity_cost_capped_book |           168 |              95 |                   50 |               0.0012116  |                1.39518 |

## Family Summary

| family_id                         |   candidate_count |   survivor_count |   median_net_book_return |   median_control_ratio |   median_oos_min_net_book_return |   median_oos_worst_control_ratio |
|:----------------------------------|------------------:|-----------------:|-------------------------:|-----------------------:|---------------------------------:|---------------------------------:|
| F1a_aggtrades_flow_microstructure |                 7 |                0 |               0.00472295 |                1.48325 |                       -0.0136958 |                          3.21025 |
| F1b_taker_flow_market_panel       |                 6 |                0 |              -0.014868   |                1.54539 |                       -0.0426096 |                          4.08863 |
| F2a_basis_funding_independent     |                 8 |                0 |               0.00901798 |                1.7126  |                       -0.0793763 |                          3.5474  |

## Survivors

`<empty>`

## Candidate Summary Preview

| candidate_id   | family_id                         |   replay_rows |   positive_rows |   control_clean_rows |   split_pass_rows |   median_net_book_return |   median_control_ratio |   max_abs_net_book_return |   train_split_pass_count |   train_median_net_book_return |   train_median_control_ratio |   oos_split_count |   oos_positive_split_count |   oos_control_clean_split_count |   oos_min_net_book_return |   oos_worst_control_ratio | book_survivor   |
|:---------------|:----------------------------------|--------------:|----------------:|---------------------:|------------------:|-------------------------:|-----------------------:|--------------------------:|-------------------------:|-------------------------------:|-----------------------------:|------------------:|---------------------------:|--------------------------------:|--------------------------:|--------------------------:|:----------------|
| a7ffcore33_000 | F1b_taker_flow_market_panel       |            32 |              11 |                   10 |                 0 |             -0.0083748   |               1.50652  |                   5.36506 |                        0 |                    0.0114073   |                     1.51958  |                 3 |                          0 |                               1 |              -0.0494197   |                   5.26427 | False           |
| a7ffcore33_001 | F1b_taker_flow_market_panel       |            32 |              15 |                   11 |                 8 |             -0.000153826 |               1.25692  |                  28.4564  |                        1 |                   -0.0966908   |                     1.00304  |                 3 |                          2 |                               1 |              -0.00858156  |                  12.412   | False           |
| a7ffcore33_002 | F2a_basis_funding_independent     |            32 |              21 |                    9 |                 9 |              0.022776    |               1.89632  |                  27.9264  |                        1 |                   -0.00226815  |                     1.28404  |                 3 |                          2 |                               1 |              -0.000781739 |                   4.89006 | False           |
| a7ffcore33_003 | F2a_basis_funding_independent     |            32 |              13 |                   12 |                 0 |             -0.00690958  |               1.42048  |                   7.13059 |                        0 |                   -0.0737529   |                     0.902999 |                 3 |                          2 |                               1 |              -0.047203    |                   3.64271 | False           |
| a7ffcore33_004 | F2a_basis_funding_independent     |            32 |              14 |                    5 |                 1 |             -0.00855288  |               1.89065  |                  15.1203  |                        0 |                    0.00053955  |                     2.79463  |                 3 |                          1 |                               0 |              -0.165142    |                   2.22961 | False           |
| a7ffcore33_005 | F2a_basis_funding_independent     |            32 |              12 |                   10 |                 0 |             -0.0322403   |               1.28646  |                   3.77654 |                        0 |                   -0.0667132   |                     1.18402  |                 3 |                          2 |                               1 |              -0.113392    |                   1.7661  | False           |
| a7ffcore33_006 | F1b_taker_flow_market_panel       |            32 |               8 |                    6 |                 0 |             -0.029461    |               1.42704  |                   6.40031 |                        0 |                   -0.0175295   |                     6.58389  |                 3 |                          0 |                               0 |              -0.0357995   |                   1.73296 | False           |
| a7ffcore33_007 | F1a_aggtrades_flow_microstructure |            32 |              14 |                   19 |                 8 |             -0.00182164  |               0.743855 |                  31.0105  |                        0 |                   -0.137043    |                     0.637892 |                 3 |                          2 |                               2 |              -0.0350124   |                   6.66525 | False           |
| a7ffcore33_008 | F1a_aggtrades_flow_microstructure |            32 |              19 |                   10 |                 5 |              0.00472295  |               1.64119  |                  17.7018  |                        1 |                    0.0142754   |                     5.73248  |                 3 |                          2 |                               1 |              -0.147242    |                   2.27295 | False           |
| a7ffcore33_009 | F2a_basis_funding_independent     |            32 |              23 |                    6 |                 2 |              0.0306107   |               1.8906   |                   8.54359 |                        0 |                    0.0195085   |                     1.17629  |                 3 |                          3 |                               0 |               0.00309534  |                   5.58639 | False           |
| a7ffcore33_010 | F2a_basis_funding_independent     |            32 |              15 |                    6 |                 6 |             -0.00474005  |               1.53459  |                  19.0146  |                        0 |                   -0.000170383 |                     1.72516  |                 3 |                          1 |                               1 |              -0.195596    |                   3.80008 | False           |
| a7ffcore33_011 | F2a_basis_funding_independent     |            32 |              26 |                    3 |                 3 |              0.0251678   |               2.01373  |                   6.55341 |                        0 |                    0.0287323   |                     1.71241  |                 3 |                          2 |                               0 |              -0.0069708   |                   3.4521  | False           |
| a7ffcore33_012 | F1b_taker_flow_market_panel       |            32 |              16 |                    5 |                 0 |              0.000319288 |               1.58427  |                   5.06245 |                        0 |                    0.0311947   |                     2.14114  |                 3 |                          0 |                               0 |              -0.0278191   |                   2.12118 | False           |
| a7ffcore33_013 | F2a_basis_funding_independent     |            32 |              17 |                   10 |                 0 |              0.0263767   |               1.19955  |                  10.8204  |                        0 |                    0.192417    |                     1.19439  |                 3 |                          1 |                               1 |              -0.11155     |                   1.38288 | False           |
| a7ffcore33_014 | F1b_taker_flow_market_panel       |            32 |              12 |                   12 |                 4 |             -0.0213613   |               1.85302  |                  18.0067  |                        0 |                   -0.167067    |                     0.883894 |                 3 |                          1 |                               0 |              -0.186263    |                   2.91298 | False           |
| a7ffcore33_015 | F1a_aggtrades_flow_microstructure |            32 |               9 |                   14 |                 3 |             -0.0249926   |               1.13355  |                  42.3285  |                        0 |                   -0.23184     |                     0.484852 |                 3 |                          1 |                               0 |              -0.0566273   |                   2.99995 | False           |
| a7ffcore33_016 | F1a_aggtrades_flow_microstructure |            32 |              14 |                    5 |                 2 |             -0.00047662  |               1.84988  |                  15.1066  |                        0 |                    0.00271649  |                     3.57868  |                 3 |                          0 |                               0 |              -0.0136958   |                   3.21025 | False           |
| a7ffcore33_017 | F1a_aggtrades_flow_microstructure |            32 |              25 |                   10 |                 7 |              0.0239908   |               1.48325  |                  15.0701  |                        2 |                    0.095908    |                     1.31754  |                 3 |                          3 |                               1 |               0.000176814 |                   5.10705 | False           |
| a7ffcore33_018 | F1a_aggtrades_flow_microstructure |            32 |              32 |                   14 |                14 |              0.0346601   |               1.15704  |                   9.78128 |                        0 |                    0.0165677   |                     4.6227   |                 3 |                          3 |                               2 |               0.0342742   |                   1.24326 | False           |
| a7ffcore33_019 | F1b_taker_flow_market_panel       |            32 |              10 |                    5 |                 0 |             -0.0418419   |               1.66835  |                  30.7462  |                        0 |                   -0.0530655   |                     1.03952  |                 3 |                          1 |                               0 |              -0.567946    |                  10.5021  | False           |
| a7ffcore33_020 | F1a_aggtrades_flow_microstructure |            32 |              30 |                    8 |                 8 |              0.046785    |               1.9394   |                  15.779   |                        0 |                    0.046785    |                     3.0025   |                 3 |                          3 |                               1 |               0.00903037  |                   3.48848 | False           |

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core40er_forensic": true,
  "authorizes_core41_arbitration": false,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "book_replay_rows": 672,
  "decision": "HOLD_A7FFCORE40E_BOOK_OBJECTIVE_REPLAY_INSUFFICIENT",
  "executes_replay": true,
  "executes_search": false,
  "generated_at": "2026-06-01T20:23:52Z",
  "next_allowed": "A7FF-CORE40ER book-objective replay forensic",
  "packet_rows": 623160,
  "source_decision": "PASS_A7FFCORE40_BOOK_OBJECTIVE_REPLAY_CONTRACT_READY_FOR_CORE40E",
  "source_stage": "A7FF-CORE40",
  "stage": "A7FF-CORE40E",
  "survivor_count": 0,
  "survivor_family_count": 0
}
```
