# CRYPTO A7FF-CORE14E BOUNDED REPLAY EXECUTION

Generated: 2026-06-01T06:25:04Z

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
  "generated_at": "2026-06-01T06:25:04Z",
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

| semantic_bucket                     | motif_bucket    |   candidate_count |   median_cost_adjusted_spread |   median_control_ratio |   clean_candidate_count |
|:------------------------------------|:----------------|------------------:|------------------------------:|-----------------------:|------------------------:|
| liquidity_like\|volatility_like     | liquidity_shock |                 3 |                  -0.000661807 |                1.30593 |                       0 |
| taker_flow_like\|basis_premium_like | gated_sign      |                 3 |                  -0.000417062 |                2.99934 |                       0 |
| taker_flow_like\|open_interest_like | flow_x_leverage |                 2 |                  -0.00057562  |                3.79772 |                       0 |

## Candidate Summary

| candidate_id                   | semantic_bucket                     | motif_bucket    |   replay_rows |   median_spread |   median_cost_adjusted_spread |   max_tstat |   min_control_ratio |   validation_recent_clean_splits | replay_clean   |
|:-------------------------------|:------------------------------------|:----------------|--------------:|----------------:|------------------------------:|------------:|--------------------:|---------------------------------:|:---------------|
| a7ffcore11e_123c59e7517b7ef3c6 | taker_flow_like\|basis_premium_like | gated_sign      |            12 |     0.000352472 |                  -0.000243024 |    1.86718  |            0.489802 |                                0 | False          |
| a7ffcore11e_05014af14def66a014 | liquidity_like\|volatility_like     | liquidity_shock |            12 |     0.000130347 |                  -0.000672623 |    1.59392  |            0.826878 |                                0 | False          |
| a7ffcore11e_2e9ceddde79416ef0f | taker_flow_like\|basis_premium_like | gated_sign      |            12 |    -9.92464e-05 |                  -0.000590856 |    1.55728  |            1.51876  |                                0 | False          |
| a7ffcore11e_4394e65d4ffa374dcd | taker_flow_like\|basis_premium_like | gated_sign      |            12 |     0.00034577  |                  -0.000351159 |    1.55374  |            2.05139  |                                0 | False          |
| a7ffcore11e_4ee210eb705472cf94 | liquidity_like\|volatility_like     | liquidity_shock |            12 |    -7.44274e-05 |                  -0.000506729 |    1.15309  |            0.494123 |                                0 | False          |
| a7ffcore11e_7bd1bb9089595953e0 | taker_flow_like\|open_interest_like | flow_x_leverage |            12 |     0.000448477 |                  -0.000251523 |    0.924556 |            1.25665  |                                0 | False          |
| a7ffcore11e_5797ede140d362ffce | taker_flow_like\|open_interest_like | flow_x_leverage |            12 |     0.000328059 |                  -0.000635829 |    0.533524 |            2.78454  |                                0 | False          |
| a7ffcore11e_3170d54fa686383546 | liquidity_like\|volatility_like     | liquidity_shock |            12 |    -0.00018349  |                  -0.000862767 |   -0.214797 |            0.326772 |                                0 | False          |

## Boundary

```text
bounded replay: true
formula search / large search: false
promotion: false
alpha proof / shadow / paper / live: false
```
