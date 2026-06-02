# CRYPTO A7FF-CORE52 COMPANY REPLAY ARBITRATION

Generated: 2026-06-02T09:43:13Z

## Decision

`HOLD_A7FFCORE52_DIAGNOSTIC_CLUES_INSUFFICIENT_FOR_SEARCH`

CORE52 arbitrates the imported CORE51PXE company-sharded replay. It does not execute replay, generation, search, proof, or promotion.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core52f_forensic": true,
  "authorizes_core53_deep_audit_contract": false,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "HOLD_A7FFCORE52_DIAGNOSTIC_CLUES_INSUFFICIENT_FOR_SEARCH",
  "diagnostic_clue_count": 35,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-02T09:43:13Z",
  "label_count": 8,
  "metric_rows": 3072,
  "operator_count": 7,
  "seed_count": 384,
  "semantic_pair_count": 39,
  "source_decision": "PASS_A7FFCORE51PXE_COMPANY_RESULTS_IMPORTED_READY_FOR_CORE52_ARBITRATION",
  "source_stage": "A7FF-CORE51PXE-IMPORT",
  "stage": "A7FF-CORE52",
  "strict_replay_clue_count": 1,
  "strict_replay_clue_semantic_pair_count": 1
}
```

## Label Arbitration

| label_key   |   row_count |   seed_count |   control_clean_positive_count |   median_control_ratio |   median_original_spread |
|:------------|------------:|-------------:|-------------------------------:|-----------------------:|-------------------------:|
| L0_raw_1h   |         384 |          384 |                             17 |                1.07807 |             -1.83747e-05 |
| L0_raw_24h  |         384 |          384 |                             14 |                1.11992 |             -6.07262e-05 |
| L0_raw_4h   |         384 |          384 |                             11 |                1.13561 |             -4.16569e-05 |
| L0_raw_8h   |         384 |          384 |                             12 |                1.07944 |             -4.42174e-05 |
| L1_xs_1h    |         384 |          384 |                             17 |                1.07807 |             -1.83747e-05 |
| L1_xs_24h   |         384 |          384 |                             14 |                1.11992 |             -6.07262e-05 |
| L1_xs_4h    |         384 |          384 |                             11 |                1.13561 |             -4.16569e-05 |
| L1_xs_8h    |         384 |          384 |                             12 |                1.07944 |             -4.42174e-05 |

## Top Diagnostic Clues

| seed_id           | arbitration_status   | semantic_pair                         | operator        |   clean_label_count |   clean_horizons |   min_control_ratio |   median_control_ratio |   max_original_spread |
|:------------------|:---------------------|:--------------------------------------|:----------------|--------------------:|-----------------:|--------------------:|-----------------------:|----------------------:|
| a7ffcore48se_0219 | diagnostic_clue      | price_like|price_like                 | Identity        |                   8 |                4 |            0.993992 |               0.995587 |           0.000273973 |
| a7ffcore48se_1397 | diagnostic_clue      | basis_premium_like|price_like         | Identity        |                   8 |                4 |            0.992908 |               0.99657  |           0.000274678 |
| a7ffcore48se_0248 | strict_replay_clue   | state_or_taxonomy|state_or_taxonomy   | SignedRankDelta |                   6 |                3 |            0.788013 |               0.882984 |           0.000337505 |
| a7ffcore48se_1159 | diagnostic_clue      | funding_like|funding_like             | WinsorZ         |                   6 |                3 |            0.944448 |               0.968402 |           0.0018563   |
| a7ffcore48se_0824 | diagnostic_clue      | basis_premium_like|basis_premium_like | Identity        |                   6 |                3 |            0.996146 |               0.998515 |           0.000371488 |
| a7ffcore48se_0545 | diagnostic_clue      | basis_premium_like                    | Delta           |                   6 |                3 |            0.998864 |               0.999442 |           0.00064032  |
| a7ffcore48se_0274 | diagnostic_clue      | basis_premium_like                    | Delta           |                   6 |                3 |            0.99883  |               0.999513 |           0.000757053 |
| a7ffcore48se_1446 | diagnostic_clue      | funding_like|positioning_like         | Identity        |                   4 |                2 |            0.715899 |               0.964986 |           0.00136525  |
| a7ffcore48se_1540 | diagnostic_clue      | positioning_like|state_or_taxonomy    | Identity        |                   4 |                2 |            0.943449 |               1.01603  |           0.00128928  |
| a7ffcore48se_1456 | diagnostic_clue      | funding_like|price_like               | WinsorZ         |                   4 |                2 |            0.977276 |               2.94719  |           0.000257703 |
| a7ffcore48se_1566 | diagnostic_clue      | price_like|state_or_taxonomy          | SpreadShortLong |                   2 |                1 |            0.999465 |               1        |           0.000432629 |
| a7ffcore48se_0010 | diagnostic_clue      | basis_premium_like|basis_premium_like | Identity        |                   2 |                1 |            0.998129 |               1.00032  |           0.000221683 |
| a7ffcore48se_0013 | diagnostic_clue      | basis_premium_like|basis_premium_like | WinsorZ         |                   2 |                1 |            0.999264 |               1.00341  |           0.000605271 |
| a7ffcore48se_0001 | diagnostic_clue      | basis_premium_like                    | CSRank          |                   2 |                1 |            0.997298 |               1.00415  |           0.000887805 |
| a7ffcore48se_1355 | diagnostic_clue      | basis_premium_like                    | Identity        |                   2 |                1 |            0.997298 |               1.00415  |           0.000887805 |
| a7ffcore48se_1557 | diagnostic_clue      | price_like|price_like                 | Identity        |                   2 |                1 |            0.997327 |               1.01117  |           0.000171494 |
| a7ffcore48se_1509 | diagnostic_clue      | liquidity_like|state_or_taxonomy      | SpreadShortLong |                   2 |                1 |            0.999812 |               1.01228  |           0.000430644 |
| a7ffcore48se_0090 | diagnostic_clue      | funding_like|liquidity_like           | WinsorZ         |                   2 |                1 |            0.998084 |               1.01298  |           0.00153237  |
| a7ffcore48se_1188 | diagnostic_clue      | funding_like|state_or_taxonomy        | AbsDelta        |                   2 |                1 |            0.980167 |               1.03271  |           0.00101503  |
| a7ffcore48se_0147 | diagnostic_clue      | liquidity_like|positioning_like       | CSRank          |                   2 |                1 |            0.999934 |               1.05273  |           0.000116716 |
| a7ffcore48se_0740 | diagnostic_clue      | positioning_like|state_or_taxonomy    | Identity        |                   2 |                1 |            0.949673 |               1.05459  |           0.000945796 |
| a7ffcore48se_0029 | diagnostic_clue      | basis_premium_like|liquidity_like     | CSRank          |                   2 |                1 |            0.95858  |               1.13293  |           0.000210253 |
| a7ffcore48se_1704 | diagnostic_clue      | funding_like|positioning_like         | WinsorZ         |                   2 |                1 |            0.947725 |               1.18111  |           0.00108751  |
| a7ffcore48se_0671 | diagnostic_clue      | generic_numeric|price_like            | Identity        |                   2 |                1 |            0.983468 |               1.31692  |           0.000207717 |
| a7ffcore48se_0775 | diagnostic_clue      | price_like|volatility_like            | Identity        |                   2 |                1 |            0.999804 |               1.33002  |           0.000370956 |
| a7ffcore48se_1195 | diagnostic_clue      | funding_like|volatility_like          | AbsDelta        |                   2 |                1 |            0.871725 |               1.62696  |           0.000453388 |
| a7ffcore48se_1249 | diagnostic_clue      | liquidity_like|state_or_taxonomy      | WinsorZ         |                   2 |                1 |            0.796933 |               1.88148  |           8.13583e-05 |
| a7ffcore48se_0176 | diagnostic_clue      | positioning_like                      | Delta           |                   2 |                1 |            0.9996   |               2.19935  |           9.86036e-05 |
| a7ffcore48se_0682 | diagnostic_clue      | generic_numeric|volatility_like       | AbsDelta        |                   2 |                1 |            0.954066 |               3.14704  |           9.30069e-06 |
| a7ffcore48se_1393 | diagnostic_clue      | basis_premium_like|positioning_like   | WinsorZ         |                   2 |                1 |            0.999616 |               3.50444  |           0.000135809 |
| a7ffcore48se_0681 | diagnostic_clue      | generic_numeric|state_or_taxonomy     | WinsorZ         |                   2 |                1 |            0.779151 |               4.07641  |           0.000471575 |
| a7ffcore48se_0785 | diagnostic_clue      | state_or_taxonomy                     | WinsorZ         |                   2 |                1 |            0.779151 |               4.07641  |           0.000471575 |
| a7ffcore48se_0381 | diagnostic_clue      | funding_like|state_or_taxonomy        | SignedRankDelta |                   2 |                1 |            0.786296 |               4.28157  |           0.00013508  |
| a7ffcore48se_1466 | diagnostic_clue      | funding_like|volatility_like          | Delta           |                   2 |                1 |            0.996693 |               5.73168  |           0.000176387 |
| a7ffcore48se_0182 | diagnostic_clue      | positioning_like|positioning_like     | CSRank          |                   2 |                1 |            0.998709 |              16.2623   |           7.35149e-05 |

## Family Arbitration

| semantic_pair                         | operator        |   seed_count |   diagnostic_seed_count |   strict_seed_count |   median_clean_label_count |   median_control_ratio |   max_original_spread |
|:--------------------------------------|:----------------|-------------:|------------------------:|--------------------:|---------------------------:|-----------------------:|----------------------:|
| state_or_taxonomy|state_or_taxonomy   | SignedRankDelta |            2 |                       0 |                   1 |                          3 |               1.13986  |           0.000337505 |
| basis_premium_like|basis_premium_like | Identity        |            2 |                       2 |                   0 |                          4 |               0.999417 |           0.000371488 |
| basis_premium_like                    | Delta           |            4 |                       2 |                   0 |                          3 |               0.999756 |           0.000757053 |
| price_like|price_like                 | Identity        |            2 |                       2 |                   0 |                          5 |               1.00338  |           0.000273973 |
| positioning_like|state_or_taxonomy    | Identity        |            2 |                       2 |                   0 |                          3 |               1.03531  |           0.00128928  |
| funding_like|positioning_like         | Identity        |            1 |                       1 |                   0 |                          4 |               0.964986 |           0.00136525  |
| funding_like|funding_like             | WinsorZ         |            1 |                       1 |                   0 |                          6 |               0.968402 |           0.0018563   |
| basis_premium_like|price_like         | Identity        |            1 |                       1 |                   0 |                          8 |               0.99657  |           0.000274678 |
| price_like|state_or_taxonomy          | SpreadShortLong |            1 |                       1 |                   0 |                          2 |               1        |           0.000432629 |
| liquidity_like|state_or_taxonomy      | SpreadShortLong |            1 |                       1 |                   0 |                          2 |               1.01228  |           0.000430644 |
| funding_like|state_or_taxonomy        | AbsDelta        |            2 |                       1 |                   0 |                          1 |               1.01301  |           0.00101503  |
| funding_like|liquidity_like           | WinsorZ         |            2 |                       1 |                   0 |                          1 |               1.01927  |           0.00213138  |
| liquidity_like|positioning_like       | CSRank          |            1 |                       1 |                   0 |                          2 |               1.05273  |           0.000116716 |
| funding_like|positioning_like         | WinsorZ         |            1 |                       1 |                   0 |                          2 |               1.18111  |           0.00108751  |
| basis_premium_like                    | Identity        |            2 |                       1 |                   0 |                          1 |               1.2451   |           0.00254778  |
| funding_like|volatility_like          | AbsDelta        |            2 |                       1 |                   0 |                          1 |               1.28866  |           0.000453388 |
| basis_premium_like|basis_premium_like | WinsorZ         |            2 |                       1 |                   0 |                          1 |               1.39007  |           0.000605271 |
| basis_premium_like                    | CSRank          |            3 |                       1 |                   0 |                          0 |               1.48692  |           0.00254778  |
| basis_premium_like|liquidity_like     | CSRank          |            2 |                       1 |                   0 |                          1 |               1.5019   |           0.000210253 |
| price_like|volatility_like            | Identity        |            2 |                       1 |                   0 |                          1 |               1.58828  |           0.000370956 |
| generic_numeric|price_like            | Identity        |            2 |                       1 |                   0 |                          1 |               1.74243  |           0.000207717 |
| liquidity_like|state_or_taxonomy      | WinsorZ         |            1 |                       1 |                   0 |                          2 |               1.88148  |           8.13583e-05 |
| generic_numeric|volatility_like       | AbsDelta        |            2 |                       1 |                   0 |                          1 |               2.13219  |           0.000205153 |
| positioning_like                      | Delta           |            1 |                       1 |                   0 |                          2 |               2.19935  |           9.86036e-05 |
| state_or_taxonomy                     | WinsorZ         |            2 |                       1 |                   0 |                          1 |               2.5382   |           0.000471575 |
| funding_like|state_or_taxonomy        | SignedRankDelta |            2 |                       1 |                   0 |                          1 |               2.69301  |           0.000712632 |
| funding_like|price_like               | WinsorZ         |            1 |                       1 |                   0 |                          4 |               2.94719  |           0.000257703 |
| basis_premium_like|positioning_like   | WinsorZ         |            2 |                       1 |                   0 |                          1 |               2.9962   |           0.000317054 |
| funding_like|volatility_like          | Delta           |            2 |                       1 |                   0 |                          1 |               3.42793  |           0.000176387 |
| generic_numeric|state_or_taxonomy     | WinsorZ         |            1 |                       1 |                   0 |                          2 |               4.07641  |           0.000471575 |
| positioning_like|positioning_like     | CSRank          |            2 |                       1 |                   0 |                          1 |              19.8662   |           7.35149e-05 |
| basis_premium_like|positioning_like   | CSRank          |            1 |                       0 |                   0 |                          0 |               0.909537 |          -6.9684e-05  |
| funding_like|price_like               | AbsDelta        |            1 |                       0 |                   0 |                          0 |               0.96713  |          -3.83328e-05 |
| liquidity_like|volatility_like        | AbsDelta        |            1 |                       0 |                   0 |                          0 |               0.992065 |          -2.14731e-05 |
| price_like                            | Delta           |            1 |                       0 |                   0 |                          0 |               0.997132 |          -0.000129448 |
| positioning_like|price_like           | SignedRankDelta |            1 |                       0 |                   0 |                          0 |               0.999585 |          -7.94208e-05 |
| price_like|state_or_taxonomy          | AbsDelta        |            1 |                       0 |                   0 |                          0 |               0.999982 |          -5.52122e-05 |
| basis_premium_like|basis_premium_like | AbsDelta        |            2 |                       0 |                   0 |                          0 |               1        |          -0.000141714 |
| basis_premium_like|liquidity_like     | SignedRankDelta |            1 |                       0 |                   0 |                          0 |               1        |          -6.66492e-05 |
| basis_premium_like|liquidity_like     | SpreadShortLong |            1 |                       0 |                   0 |                          0 |               1        |           0.00107544  |
| basis_premium_like|price_like         | SpreadShortLong |            1 |                       0 |                   0 |                          0 |               1        |           0.000859414 |
| funding_like                          | Delta           |            1 |                       0 |                   0 |                          0 |               1        |          -7.07749e-05 |
| funding_like|generic_numeric          | SpreadShortLong |            1 |                       0 |                   0 |                          0 |               1        |           0.0222555   |
| funding_like|liquidity_like           | Delta           |            1 |                       0 |                   0 |                          0 |               1        |          -5.03679e-05 |
| funding_like|positioning_like         | SpreadShortLong |            1 |                       0 |                   0 |                          0 |               1        |           0.0324441   |
| funding_like|price_like               | SpreadShortLong |            1 |                       0 |                   0 |                          0 |               1        |           0.00278824  |
| generic_numeric|positioning_like      | Delta           |            1 |                       0 |                   0 |                          0 |               1        |          -2.06218e-05 |
| liquidity_like|price_like             | SpreadShortLong |            1 |                       0 |                   0 |                          0 |               1        |           0.00117336  |
| positioning_like                      | SpreadShortLong |            1 |                       0 |                   0 |                          0 |               1        |          -5.85934e-05 |
| positioning_like|positioning_like     | AbsDelta        |            2 |                       0 |                   0 |                          0 |               1        |          -3.60709e-05 |
| positioning_like|positioning_like     | SpreadShortLong |            1 |                       0 |                   0 |                          0 |               1        |          -2.36407e-05 |
| price_like|price_like                 | SpreadShortLong |            1 |                       0 |                   0 |                          0 |               1        |           0.000863244 |
| state_or_taxonomy                     | AbsDelta        |            1 |                       0 |                   0 |                          0 |               1        |           0.000497195 |
| state_or_taxonomy                     | CSRank          |            1 |                       0 |                   0 |                          0 |               1        |          -0.00012645  |
| state_or_taxonomy                     | Delta           |            1 |                       0 |                   0 |                          0 |               1        |          -7.44653e-05 |
| state_or_taxonomy                     | Identity        |            1 |                       0 |                   0 |                          0 |               1        |          -0.00012645  |
| state_or_taxonomy                     | SpreadShortLong |            1 |                       0 |                   0 |                          0 |               1        |          -4.2068e-05  |
| state_or_taxonomy|volatility_like     | Delta           |            1 |                       0 |                   0 |                          0 |               1        |           0.000471003 |
| positioning_like|price_like           | SpreadShortLong |            1 |                       0 |                   0 |                          0 |               1.00003  |           0.000466109 |
| liquidity_like|price_like             | WinsorZ         |            2 |                       0 |                   0 |                          0 |               1.00004  |          -2.99516e-05 |
| positioning_like                      | SignedRankDelta |            2 |                       0 |                   0 |                          0 |               1.00012  |          -2.97378e-05 |
| basis_premium_like|volatility_like    | SignedRankDelta |            2 |                       0 |                   0 |                          0 |               1.0003   |          -4.98742e-05 |
| price_like|state_or_taxonomy          | SignedRankDelta |            1 |                       0 |                   0 |                          0 |               1.0004   |          -2.83569e-05 |
| basis_premium_like|price_like         | WinsorZ         |            1 |                       0 |                   0 |                          0 |               1.00056  |          -6.41164e-05 |
| funding_like|funding_like             | Delta           |            1 |                       0 |                   0 |                          0 |               1.00067  |           0.0068533   |
| generic_numeric|volatility_like       | SignedRankDelta |            2 |                       0 |                   0 |                          0 |               1.00076  |          -5.02667e-05 |
| generic_numeric|volatility_like       | WinsorZ         |            2 |                       0 |                   0 |                          0 |               1.00091  |          -2.78498e-05 |
| price_like|state_or_taxonomy          | CSRank          |            1 |                       0 |                   0 |                          0 |               1.00118  |          -4.66884e-05 |
| liquidity_like|positioning_like       | Identity        |            1 |                       0 |                   0 |                          0 |               1.00199  |          -3.35074e-05 |
| generic_numeric|price_like            | WinsorZ         |            2 |                       0 |                   0 |                          0 |               1.00263  |          -2.58234e-05 |
| generic_numeric|volatility_like       | Delta           |            1 |                       0 |                   0 |                          0 |               1.003    |           0.00288725  |
| generic_numeric|positioning_like      | SignedRankDelta |            2 |                       0 |                   0 |                          0 |               1.00327  |          -2.73672e-05 |
| generic_numeric|positioning_like      | WinsorZ         |            2 |                       0 |                   0 |                          0 |               1.00327  |          -2.73672e-05 |
| positioning_like|state_or_taxonomy    | SignedRankDelta |            2 |                       0 |                   0 |                          0 |               1.00327  |           1.86479e-05 |
| liquidity_like|price_like             | AbsDelta        |            1 |                       0 |                   0 |                          0 |               1.00354  |          -3.46052e-05 |
| price_like                            | Identity        |            2 |                       0 |                   0 |                          0 |               1.00439  |          -6.52125e-05 |
| price_like                            | CSRank          |            2 |                       0 |                   0 |                          0 |               1.00446  |          -6.52125e-05 |
| basis_premium_like|price_like         | SignedRankDelta |            1 |                       0 |                   0 |                          0 |               1.00476  |          -7.79258e-05 |
| price_like                            | SignedRankDelta |            3 |                       0 |                   0 |                          0 |               1.00737  |           0.000133448 |
| positioning_like                      | WinsorZ         |            2 |                       0 |                   0 |                          0 |               1.0087   |          -1.44617e-05 |

## Authorization

```json
{
  "authorized": {
    "A7FF-CORE52F diagnostic clue forensic": true,
    "A7FF-CORE53 deep audit contract": false
  },
  "not_authorized": {
    "alpha_proof": true,
    "formula_search": true,
    "large_search": true,
    "promotion": true,
    "shadow_paper_live": true
  }
}
```
