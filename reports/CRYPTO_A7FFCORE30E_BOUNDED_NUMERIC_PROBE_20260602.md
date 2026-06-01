# CRYPTO A7FF-CORE30E BOUNDED NUMERIC PROBE

Generated: 2026-06-01T18:51:43Z

## Decision

`PASS_A7FFCORE30E_NUMERIC_PROBE_CLUES_READY_FOR_CORE31_CONTRACT`

CORE30E executes a bounded numeric probe only. It does not execute replay, search, large search, alpha proof, shadow, paper, or live.

## Summary

- candidate_count: `240`
- numeric_result_rows: `2160`
- clean_candidate_count: `113`
- clean_family_count: `3`

## Dataset Summary

| dataset                       |    rows |   sample_rows |   symbols |   sample_timestamps |   field_count |
|:------------------------------|--------:|--------------:|----------:|--------------------:|--------------:|
| core12_aggtrades_all_features |  815818 |         29951 |        39 |                 768 |             8 |
| top498_replay_v2              | 6949596 |        253871 |       498 |                 768 |             8 |

## Family Summary

| family_id                         |   candidate_count |   clean_candidate_count |   median_control_ratio |   median_max_ic |
|:----------------------------------|------------------:|------------------------:|-----------------------:|----------------:|
| F1a_aggtrades_flow_microstructure |                80 |                      56 |               0.483831 |      0.0172636  |
| F1b_taker_flow_market_panel       |                80 |                      34 |               1.28566  |      0.00784512 |
| F2a_basis_funding_independent     |                80 |                      42 |               0.862632 |      0.00614785 |

## Selected Numeric Clues

| numeric_probe_id   | family_id                         |   max_oriented_ic |   max_oriented_spread |   min_control_ratio |   clean_label_count |   eval_rows |
|:-------------------|:----------------------------------|------------------:|----------------------:|--------------------:|--------------------:|------------:|
| a7ffcore30_0134    | F1b_taker_flow_market_panel       |        0.0398347  |            0.120055   |           0.573142  |                   9 |      252906 |
| a7ffcore30_0019    | F1a_aggtrades_flow_microstructure |        0.0338372  |            0.143456   |           0.390003  |                   9 |        8886 |
| a7ffcore30_0028    | F1a_aggtrades_flow_microstructure |        0.0330341  |            0.0853606  |           0.181799  |                   9 |        8886 |
| a7ffcore30_0031    | F1a_aggtrades_flow_microstructure |        0.0320523  |            0.192387   |           0.229452  |                   9 |        9030 |
| a7ffcore30_0008    | F1a_aggtrades_flow_microstructure |        0.0224852  |            0.0388048  |           0.0548475 |                   9 |        9030 |
| a7ffcore30_0011    | F1a_aggtrades_flow_microstructure |        0.0220621  |            0.0671471  |           0.0605304 |                   9 |        9030 |
| a7ffcore30_0014    | F1a_aggtrades_flow_microstructure |        0.0217793  |            0.135965   |           0.0384799 |                   9 |        9030 |
| a7ffcore30_0051    | F1a_aggtrades_flow_microstructure |        0.0203867  |            0.0494303  |           0.18374   |                   9 |        8886 |
| a7ffcore30_0102    | F1b_taker_flow_market_panel       |        0.0188396  |            0.0765715  |           0.217774  |                   9 |       36812 |
| a7ffcore30_0041    | F1a_aggtrades_flow_microstructure |        0.0172383  |            0.0650903  |           0.0489872 |                   9 |        8886 |
| a7ffcore30_0163    | F2a_basis_funding_independent     |        0.0158873  |            0.0285665  |           0.295654  |                   9 |       49044 |
| a7ffcore30_0095    | F1b_taker_flow_market_panel       |        0.0150535  |            0.0759986  |           0.501775  |                   9 |       48940 |
| a7ffcore30_0222    | F2a_basis_funding_independent     |        0.0133018  |            0.0851465  |           0.417903  |                   9 |       48940 |
| a7ffcore30_0068    | F1a_aggtrades_flow_microstructure |        0.0132501  |            0.0843192  |           0.207682  |                   9 |        7428 |
| a7ffcore30_0094    | F1b_taker_flow_market_panel       |        0.0125441  |            0.0874071  |           0.276778  |                   9 |       49044 |
| a7ffcore30_0201    | F2a_basis_funding_independent     |        0.0121664  |            0.0578484  |           0.404108  |                   9 |       49044 |
| a7ffcore30_0195    | F2a_basis_funding_independent     |        0.0120862  |            0.0877237  |           0.391856  |                   9 |      251782 |
| a7ffcore30_0123    | F1b_taker_flow_market_panel       |        0.0120529  |            0.0700904  |           0.740268  |                   9 |      251782 |
| a7ffcore30_0187    | F2a_basis_funding_independent     |        0.0118174  |            0.0565328  |           0.415256  |                   9 |      252566 |
| a7ffcore30_0113    | F1b_taker_flow_market_panel       |        0.00997094 |            0.0728295  |           0.178204  |                   9 |      252918 |
| a7ffcore30_0057    | F1a_aggtrades_flow_microstructure |        0.00826881 |            0.0261307  |           0.512176  |                   9 |        9030 |
| a7ffcore30_0092    | F1b_taker_flow_market_panel       |        0.00527051 |            0.031496   |           0.126942  |                   9 |      251387 |
| a7ffcore30_0183    | F2a_basis_funding_independent     |        0.00511623 |            0.0559739  |           0.0313792 |                   9 |      252652 |
| a7ffcore30_0071    | F1a_aggtrades_flow_microstructure |        0.0386704  |            0.0590064  |           0.0613578 |                   6 |        9006 |
| a7ffcore30_0069    | F1a_aggtrades_flow_microstructure |        0.0282853  |            0.00370078 |           0.495547  |                   6 |        8967 |
| a7ffcore30_0010    | F1a_aggtrades_flow_microstructure |        0.0270941  |            0.0481854  |           0.272791  |                   6 |        7428 |
| a7ffcore30_0056    | F1a_aggtrades_flow_microstructure |        0.0267525  |            0.0510077  |           0.155577  |                   6 |        7428 |
| a7ffcore30_0026    | F1a_aggtrades_flow_microstructure |        0.0259883  |            0.126546   |           0.434064  |                   6 |        8994 |
| a7ffcore30_0017    | F1a_aggtrades_flow_microstructure |        0.0213167  |            0.0679959  |           0.0145547 |                   6 |        8967 |
| a7ffcore30_0137    | F1b_taker_flow_market_panel       |        0.0206055  |            0.0463903  |           0.287306  |                   6 |       36812 |
| a7ffcore30_0115    | F1b_taker_flow_market_panel       |        0.0196401  |            0.143176   |           0.467398  |                   6 |       48610 |
| a7ffcore30_0062    | F1a_aggtrades_flow_microstructure |        0.0186713  |            0.0300838  |           0.129553  |                   6 |        7428 |
| a7ffcore30_0047    | F1a_aggtrades_flow_microstructure |        0.0186127  |            0.0596697  |           0.172867  |                   6 |        8910 |
| a7ffcore30_0040    | F1a_aggtrades_flow_microstructure |        0.0185522  |            0.123129   |           0.209205  |                   6 |        8886 |
| a7ffcore30_0061    | F1a_aggtrades_flow_microstructure |        0.0183255  |            0.153344   |           0.270308  |                   6 |        9030 |
| a7ffcore30_0009    | F1a_aggtrades_flow_microstructure |        0.0178916  |            0.0985483  |           0.578734  |                   6 |        9030 |
| a7ffcore30_0138    | F1b_taker_flow_market_panel       |        0.0172539  |            0.179017   |           0.170604  |                   6 |       49010 |
| a7ffcore30_0099    | F1b_taker_flow_market_panel       |        0.0168088  |            0.261821   |           0.477416  |                   6 |       48572 |
| a7ffcore30_0016    | F1a_aggtrades_flow_microstructure |        0.0168078  |            0.0626621  |           0.256573  |                   6 |        7428 |
| a7ffcore30_0140    | F1b_taker_flow_market_panel       |        0.0158938  |            0.0911484  |           0.412818  |                   6 |       36812 |

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core31_contract": true,
  "authorizes_large_search": false,
  "authorizes_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "candidate_count": 240,
  "clean_candidate_count": 113,
  "clean_family_count": 3,
  "decision": "PASS_A7FFCORE30E_NUMERIC_PROBE_CLUES_READY_FOR_CORE31_CONTRACT",
  "executes_numeric": true,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T18:51:43Z",
  "next_allowed": "A7FF-CORE31 independent family clue consolidation contract",
  "numeric_result_rows": 2160,
  "source_decision": "PASS_A7FFCORE30_NUMERIC_PROBE_CONTRACT_READY_FOR_CORE30E",
  "source_stage": "A7FF-CORE30",
  "stage": "A7FF-CORE30E"
}
```
