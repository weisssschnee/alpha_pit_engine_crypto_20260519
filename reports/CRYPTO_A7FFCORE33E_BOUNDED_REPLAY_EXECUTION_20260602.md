# CRYPTO A7FF-CORE33E BOUNDED REPLAY EXECUTION

Generated: 2026-06-01T19:23:41Z

## Decision

`HOLD_A7FFCORE33E_BOUNDED_REPLAY_INSUFFICIENT`

CORE33E executes bounded replay diagnostics only. It does not execute formula search, large search, alpha proof, shadow, paper, or live.

## Summary

- candidate_count: `21`
- replay_result_rows: `756`
- survivor_count: `0`
- survivor_family_count: `0`

## Dataset Summary

| dataset                       |    rows |   symbols | timestamp_min             | timestamp_max             |
|:------------------------------|--------:|----------:|:--------------------------|:--------------------------|
| core12_aggtrades_all_features |  796123 |        39 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |
| top498_replay_v2              | 6650298 |       498 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |

## Family Summary

| family_id                         |   candidate_count |   survivor_count |   median_control_ratio |   median_net_spread |
|:----------------------------------|------------------:|-----------------:|-----------------------:|--------------------:|
| F1a_aggtrades_flow_microstructure |                 7 |                0 |               0.747379 |        -0.000183566 |
| F1b_taker_flow_market_panel       |                 6 |                1 |               2.52904  |        -9.44e-05    |
| F2a_basis_funding_independent     |                 8 |                0 |               2.54824  |        -7.98865e-05 |

## Survivors

`<empty>`

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core34_arbitration": false,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "candidate_count": 21,
  "decision": "HOLD_A7FFCORE33E_BOUNDED_REPLAY_INSUFFICIENT",
  "executes_bounded_replay": true,
  "executes_search": false,
  "generated_at": "2026-06-01T19:23:41Z",
  "next_allowed": "CORE33E replay forensic / repair",
  "replay_result_rows": 756,
  "source_decision": "PASS_A7FFCORE33_BOUNDED_REPLAY_CONTRACT_READY_FOR_CORE33E",
  "source_stage": "A7FF-CORE33",
  "stage": "A7FF-CORE33E",
  "survivor_count": 0,
  "survivor_family_count": 0
}
```
