# CRYPTO A7FF-CORE14E BOUNDED REPLAY EXECUTION

Generated: 2026-06-01T06:42:14Z

## Decision

`HOLD_A7FFCORE14E_BOUNDED_REPLAY_INSUFFICIENT`

A7FF-CORE14E executes bounded replay over the CORE14 128-candidate packet. It does not execute formula search, large search, promotion, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core15_contract": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "clean_candidate_count_lt_24",
    "clean_semantic_bucket_count_lt_4",
    "clean_motif_bucket_count_lt_4"
  ],
  "candidate_count": 8,
  "clean_rule": "validation and recent both positive at 5bps with max non-signflip control_ratio < 1.0",
  "controls": [
    "wrong_lag_future",
    "wrong_lag_stale",
    "time_shuffle",
    "symbol_shuffle",
    "same_family_placebo"
  ],
  "decision": "HOLD_A7FFCORE14E_BOUNDED_REPLAY_INSUFFICIENT",
  "eval_error_count": 0,
  "executes_replay": true,
  "executes_search": false,
  "generated_at": "2026-06-01T06:42:14Z",
  "next_allowed": "A7FF-CORE14R replay failure forensic",
  "replay_clean_candidate_count": 0,
  "replay_clean_motif_bucket_count": 0,
  "replay_clean_semantic_bucket_count": 0,
  "replay_rows": 96,
  "sample_rows": 511589,
  "sample_timestamp_count": 1536,
  "source_decision": "PASS_A7FFCORE14_REPLAY_PREFLIGHT_CONTRACT_READY_FOR_CORE14E",
  "source_stage": "A7FF-CORE14",
  "stage": "A7FF-CORE14E"
}
```

## Family Summary

| semantic_bucket                      | motif_bucket       |   candidate_count |   median_cost_adjusted_spread |   median_control_ratio |   clean_candidate_count |
|:-------------------------------------|:-------------------|------------------:|------------------------------:|-----------------------:|------------------------:|
| taker_flow_like\|open_interest_like  | flow_x_leverage    |                 4 |                  -0.000783953 |                2.3371  |                       0 |
| liquidity_like                       | single             |                 2 |                  -0.00144     |                4.2082  |                       0 |
| open_interest_like                   | single             |                 1 |                  -0.000610185 |                3.0913  |                       0 |
| open_interest_like\|positioning_like | delta_x_divergence |                 1 |                  -0.000524212 |                1.45247 |                       0 |

## Candidate Summary

| candidate_id                   | semantic_bucket                      | motif_bucket       |   replay_rows |   median_spread |   median_cost_adjusted_spread |   max_tstat |   min_control_ratio |   validation_recent_clean_splits | replay_clean   |
|:-------------------------------|:-------------------------------------|:-------------------|--------------:|----------------:|------------------------------:|------------:|--------------------:|---------------------------------:|:---------------|
| a7ffcore11e_5eeb3173819f50e614 | taker_flow_like\|open_interest_like  | flow_x_leverage    |            12 |     0.0055785   |                   0.0048785   |    2.38918  |            1.30453  |                                0 | False          |
| a7ffcore11e_1bcf38afa05684b577 | open_interest_like                   | single             |            12 |     0.000293459 |                  -0.000610185 |    1.67578  |            1.38306  |                                0 | False          |
| a7ffcore11e_bd0ecbd08308313888 | open_interest_like\|positioning_like | delta_x_divergence |            12 |     0.000125041 |                  -0.000524212 |    1.6288   |            0.872207 |                                0 | False          |
| a7ffcore11e_6a9a26e403c6125043 | taker_flow_like\|open_interest_like  | flow_x_leverage    |            12 |    -0.00496892  |                  -0.00566892  |    1.29215  |            1.3983   |                                0 | False          |
| a7ffcore11e_3f3c7ae2e99bb0f5b8 | taker_flow_like\|open_interest_like  | flow_x_leverage    |            12 |    -1.43027e-05 |                  -0.000652456 |    1.18873  |            1.92237  |                                0 | False          |
| a7ffcore11e_649733921153c9d703 | liquidity_like                       | single             |            12 |    -0.0026948   |                  -0.0033948   |    0.844908 |            2.61539  |                                0 | False          |
| a7ffcore11e_401dba8a0d92d2b684 | taker_flow_like\|open_interest_like  | flow_x_leverage    |            12 |    -0.000149314 |                  -0.00080879  |    0.834921 |            1.1463   |                                0 | False          |
| a7ffcore11e_1c294ee13a07d9e36a | liquidity_like                       | single             |            12 |     0.000170893 |                  -0.000903385 |    0.583497 |            2.48949  |                                0 | False          |

## Boundary

```text
bounded replay: true
formula search / large search: false
promotion: false
alpha proof / shadow / paper / live: false
```
