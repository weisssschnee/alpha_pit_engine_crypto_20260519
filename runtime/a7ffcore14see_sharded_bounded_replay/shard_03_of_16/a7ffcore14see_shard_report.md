# CRYPTO A7FF-CORE14E BOUNDED REPLAY EXECUTION

Generated: 2026-06-01T06:12:06Z

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
  "generated_at": "2026-06-01T06:12:06Z",
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
| taker_flow_like\|basis_premium_like  | gated_sign         |                 3 |                   0.000354268 |                1.7992  |                       0 |
| liquidity_like\|volatility_like      | liquidity_shock    |                 2 |                  -0.000389365 |                1.77864 |                       0 |
| liquidity_like                       | single             |                 1 |                  -0.000896871 |                3.0752  |                       0 |
| open_interest_like\|positioning_like | delta_x_divergence |                 1 |                  -0.000503451 |               11.2773  |                       0 |
| taker_flow_like\|open_interest_like  | flow_x_leverage    |                 1 |                  -0.000799921 |                3.0154  |                       0 |

## Candidate Summary

| candidate_id                   | semantic_bucket                      | motif_bucket       |   replay_rows |   median_spread |   median_cost_adjusted_spread |   max_tstat |   min_control_ratio |   validation_recent_clean_splits | replay_clean   |
|:-------------------------------|:-------------------------------------|:-------------------|--------------:|----------------:|------------------------------:|------------:|--------------------:|---------------------------------:|:---------------|
| a7ffcore11e_afb3749ca25350c738 | taker_flow_like\|basis_premium_like  | gated_sign         |            12 |     0.000626608 |                  -8.71655e-05 |   3.01303   |            1.27167  |                                0 | False          |
| a7ffcore11e_c6c5696a8e9141f9bf | taker_flow_like\|basis_premium_like  | gated_sign         |            12 |     0.00060992  |                  -0.000300686 |   1.99737   |            0.9247   |                                0 | False          |
| a7ffcore11e_300ef9b90098b89b58 | liquidity_like\|volatility_like      | liquidity_shock    |            12 |    -4.20995e-05 |                  -0.000546197 |   1.96415   |            1.15891  |                                0 | False          |
| a7ffcore11e_29f4f627799a6dfed5 | taker_flow_like\|basis_premium_like  | gated_sign         |            12 |     0.0155865   |                   0.0148865   |   1.57602   |            0.490049 |                                0 | False          |
| a7ffcore11e_8591d2d9607675777e | open_interest_like\|positioning_like | delta_x_divergence |            12 |     0.000138159 |                  -0.000503451 |   1.15618   |            2.54262  |                                0 | False          |
| a7ffcore11e_7f4ddd6ba1891e3a2c | liquidity_like                       | single             |            12 |    -7.23436e-05 |                  -0.000896871 |   1.15422   |            2.13067  |                                0 | False          |
| a7ffcore11e_1318fb133c8f705c5b | liquidity_like\|volatility_like      | liquidity_shock    |            12 |     0.00166337  |                   0.000963369 |   0.769249  |            0.980346 |                                0 | False          |
| a7ffcore11e_435b102c039df90f17 | taker_flow_like\|open_interest_like  | flow_x_leverage    |            12 |    -8.20634e-05 |                  -0.000799921 |   0.0800148 |            1.24108  |                                0 | False          |

## Boundary

```text
bounded replay: true
formula search / large search: false
promotion: false
alpha proof / shadow / paper / live: false
```
