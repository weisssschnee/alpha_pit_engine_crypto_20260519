# CRYPTO A7FF-CORE14E BOUNDED REPLAY EXECUTION

Generated: 2026-06-01T05:58:31Z

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
  "generated_at": "2026-06-01T05:58:31Z",
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
| liquidity_like                       | single             |                 3 |                  -0.00148996  |                3.55721 |                       0 |
| liquidity_like\|volatility_like      | liquidity_shock    |                 2 |                   0.00932595  |                1.85227 |                       0 |
| taker_flow_like\|open_interest_like  | flow_x_leverage    |                 2 |                  -0.00179276  |                4.58579 |                       0 |
| open_interest_like\|positioning_like | delta_x_divergence |                 1 |                  -0.000902673 |               13.5817  |                       0 |

## Candidate Summary

| candidate_id                   | semantic_bucket                      | motif_bucket       |   replay_rows |   median_spread |   median_cost_adjusted_spread |   max_tstat |   min_control_ratio |   validation_recent_clean_splits | replay_clean   |
|:-------------------------------|:-------------------------------------|:-------------------|--------------:|----------------:|------------------------------:|------------:|--------------------:|---------------------------------:|:---------------|
| a7ffcore11e_0d3de62849361e5bec | taker_flow_like\|open_interest_like  | flow_x_leverage    |            12 |    -0.00163112  |                  -0.00233112  |   2.31593   |            0.659589 |                                0 | False          |
| a7ffcore11e_2a2d48956a572ac1ab | liquidity_like\|volatility_like      | liquidity_shock    |            12 |     0.0372133   |                   0.0365133   |   1.18513   |            0.782685 |                                1 | False          |
| a7ffcore11e_4c67508333214e808c | liquidity_like\|volatility_like      | liquidity_shock    |            12 |     7.04152e-05 |                  -0.000674967 |   0.982738  |            1.33623  |                                0 | False          |
| a7ffcore11e_e75225abf06a144055 | liquidity_like                       | single             |            12 |    -0.00345519  |                  -0.00415519  |   0.848162  |            3.46429  |                                0 | False          |
| a7ffcore11e_043dc762c9529bb4ea | taker_flow_like\|open_interest_like  | flow_x_leverage    |            12 |     4.56011e-05 |                  -0.000654399 |   0.291011  |            1.09093  |                                0 | False          |
| a7ffcore11e_a48ad1e36a600830e7 | open_interest_like\|positioning_like | delta_x_divergence |            12 |     6.75439e-05 |                  -0.000902673 |   0.227243  |            2.00933  |                                0 | False          |
| a7ffcore11e_dbe18bd5192060448c | liquidity_like                       | single             |            12 |    -0.000583909 |                  -0.00148996  |   0.181555  |            0.877088 |                                0 | False          |
| a7ffcore11e_62177b4a351f23dee9 | liquidity_like                       | single             |            12 |    -0.00014967  |                  -0.00107373  |  -0.0488746 |            1.93965  |                                0 | False          |

## Boundary

```text
bounded replay: true
formula search / large search: false
promotion: false
alpha proof / shadow / paper / live: false
```
