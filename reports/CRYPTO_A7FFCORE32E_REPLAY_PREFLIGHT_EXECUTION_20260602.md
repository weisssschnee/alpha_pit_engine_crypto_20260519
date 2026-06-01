# CRYPTO A7FF-CORE32E REPLAY PREFLIGHT EXECUTION

Generated: 2026-06-01T19:05:07Z

## Decision

`PASS_A7FFCORE32E_REPLAY_PREFLIGHT_READY_FOR_CORE33_CONTRACT`

CORE32E executes replay-preflight diagnostics only. It does not execute tradable replay, search, large search, alpha proof, shadow, paper, or live.

## Summary

- candidate_count: `24`
- preflight_result_rows: `360`
- selected_preflight_candidate_count: `21`
- selected_family_count: `3`

## Dataset Summary

| dataset                       |    rows |   sample_rows |   symbols |   sample_timestamps |
|:------------------------------|--------:|--------------:|----------:|--------------------:|
| core12_aggtrades_all_features |  815818 |         39935 |        39 |                1024 |
| top498_replay_v2              | 6949596 |        338493 |       498 |                1024 |

## Family Summary

| family_id                         |   candidate_count |   non_l7_clean_candidate_count |   median_control_ratio |   median_abs_ic |
|:----------------------------------|------------------:|-------------------------------:|-----------------------:|----------------:|
| F1a_aggtrades_flow_microstructure |                 8 |                              7 |               0.117322 |       0.0123551 |
| F1b_taker_flow_market_panel       |                 8 |                              6 |               0.58584  |       0.0102329 |
| F2a_basis_funding_independent     |                 8 |                              8 |               0.226403 |       0.0128131 |

## Selected Preflight Candidates

| preflight_candidate_id   | numeric_probe_id   | family_id                         |   max_abs_ic |   max_abs_spread |   min_control_ratio |   non_l7_clean_rows |   l7_clean_rows |   eval_rows |
|:-------------------------|:-------------------|:----------------------------------|-------------:|-----------------:|--------------------:|--------------------:|----------------:|------------:|
| a7ffcore32_008           | a7ffcore30_0134    | F1b_taker_flow_market_panel       |   0.0406095  |        0.101315  |           0.513661  |                  12 |               3 |      337260 |
| a7ffcore32_012           | a7ffcore30_0094    | F1b_taker_flow_market_panel       |   0.0185618  |        0.136678  |           0.0141414 |                  12 |               3 |       66348 |
| a7ffcore32_020           | a7ffcore30_0201    | F2a_basis_funding_independent     |   0.0175978  |        0.0785861 |           0.210195  |                  12 |               3 |       66348 |
| a7ffcore32_021           | a7ffcore30_0187    | F2a_basis_funding_independent     |   0.0159636  |        0.0835975 |           0.214964  |                  12 |               3 |      336973 |
| a7ffcore32_017           | a7ffcore30_0163    | F2a_basis_funding_independent     |   0.0152978  |        0.0765553 |           0.180123  |                  12 |               3 |       66348 |
| a7ffcore32_018           | a7ffcore30_0195    | F2a_basis_funding_independent     |   0.0118417  |        0.0696548 |           0.418207  |                  12 |               3 |      335886 |
| a7ffcore32_014           | a7ffcore30_0123    | F1b_taker_flow_market_panel       |   0.0112295  |        0.0584909 |           0.658019  |                  12 |               3 |      335886 |
| a7ffcore32_007           | a7ffcore30_0051    | F1a_aggtrades_flow_microstructure |   0.0167541  |        0.215732  |           0.0136915 |                  11 |               3 |       11841 |
| a7ffcore32_005           | a7ffcore30_0041    | F1a_aggtrades_flow_microstructure |   0.020876   |        0.0928238 |           0.179445  |                   8 |               2 |       11853 |
| a7ffcore32_022           | a7ffcore30_0233    | F2a_basis_funding_independent     |   0.0137844  |        0.0595847 |           0.161448  |                   8 |               2 |       66305 |
| a7ffcore32_019           | a7ffcore30_0222    | F2a_basis_funding_independent     |   0.0101673  |        0.0318114 |           0.554471  |                   8 |               2 |       66201 |
| a7ffcore32_023           | a7ffcore30_0203    | F2a_basis_funding_independent     |   0.00774844 |        0.0559217 |           0.237843  |                   8 |               2 |      337441 |
| a7ffcore32_010           | a7ffcore30_0113    | F1b_taker_flow_market_panel       |   0.0042023  |        0.0309615 |           0.384108  |                   8 |               2 |      337441 |
| a7ffcore32_016           | a7ffcore30_0183    | F2a_basis_funding_independent     |   0.00338079 |        0.0311221 |           0.329188  |                   8 |               2 |      337089 |
| a7ffcore32_013           | a7ffcore30_0095    | F1b_taker_flow_market_panel       |   0.0110418  |        0.0765059 |           0.672046  |                   7 |               2 |       66201 |
| a7ffcore32_004           | a7ffcore30_0011    | F1a_aggtrades_flow_microstructure |   0.00889689 |        0.0414554 |           0.615915  |                   5 |               1 |       12045 |
| a7ffcore32_001           | a7ffcore30_0031    | F1a_aggtrades_flow_microstructure |   0.0148567  |        0.0353452 |           0.0791233 |                   4 |               1 |       12045 |
| a7ffcore32_000           | a7ffcore30_0028    | F1a_aggtrades_flow_microstructure |   0.0125352  |        0.0693793 |           0.0104259 |                   4 |               1 |       11853 |
| a7ffcore32_002           | a7ffcore30_0014    | F1a_aggtrades_flow_microstructure |   0.012175   |        0.0480651 |           0.155522  |                   4 |               1 |       12033 |
| a7ffcore32_015           | a7ffcore30_0138    | F1b_taker_flow_market_panel       |   0.00942396 |        0.122856  |           0.105082  |                   4 |               1 |       66305 |
| a7ffcore32_003           | a7ffcore30_0008    | F1a_aggtrades_flow_microstructure |   0.00807632 |        0.0699417 |           0.0229927 |                   4 |               1 |       12045 |

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core33_contract": true,
  "authorizes_large_search": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "authorizes_tradable_replay": false,
  "candidate_count": 24,
  "decision": "PASS_A7FFCORE32E_REPLAY_PREFLIGHT_READY_FOR_CORE33_CONTRACT",
  "executes_replay_preflight": true,
  "executes_search": false,
  "executes_tradable_replay": false,
  "generated_at": "2026-06-01T19:05:07Z",
  "next_allowed": "A7FF-CORE33 bounded replay contract",
  "preflight_result_rows": 360,
  "selected_family_count": 3,
  "selected_preflight_candidate_count": 21,
  "source_decision": "PASS_A7FFCORE32_REPLAY_PREFLIGHT_CONTRACT_READY_FOR_CORE32E",
  "source_stage": "A7FF-CORE32",
  "stage": "A7FF-CORE32E"
}
```
