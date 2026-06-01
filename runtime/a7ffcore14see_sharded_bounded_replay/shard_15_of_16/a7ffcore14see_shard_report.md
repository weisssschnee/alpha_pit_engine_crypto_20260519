# CRYPTO A7FF-CORE14E BOUNDED REPLAY EXECUTION

Generated: 2026-06-01T06:54:36Z

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
  "generated_at": "2026-06-01T06:54:36Z",
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
| liquidity_like                       | single             |                 2 |                  -0.00619715  |                6.00964 |                       0 |
| taker_flow_like\|basis_premium_like  | gated_sign         |                 2 |                  -0.00018062  |                2.27075 |                       0 |
| taker_flow_like\|open_interest_like  | flow_x_leverage    |                 2 |                  -0.00919176  |                1.90734 |                       0 |
| liquidity_like\|volatility_like      | liquidity_shock    |                 1 |                   0.000183431 |                1.26066 |                       0 |
| open_interest_like\|positioning_like | delta_x_divergence |                 1 |                  -0.000218633 |                1.27004 |                       0 |

## Candidate Summary

| candidate_id                   | semantic_bucket                      | motif_bucket       |   replay_rows |   median_spread |   median_cost_adjusted_spread |   max_tstat |   min_control_ratio |   validation_recent_clean_splits | replay_clean   |
|:-------------------------------|:-------------------------------------|:-------------------|--------------:|----------------:|------------------------------:|------------:|--------------------:|---------------------------------:|:---------------|
| a7ffcore11e_55201ad5e75aa11f6b | taker_flow_like\|basis_premium_like  | gated_sign         |            12 |     0.000795738 |                  -4.78236e-05 |    2.89672  |            1.20009  |                                0 | False          |
| a7ffcore11e_72b29b5706d6db936b | taker_flow_like\|open_interest_like  | flow_x_leverage    |            12 |    -0.0246667   |                  -0.0253667   |    1.72926  |            0.802399 |                                1 | False          |
| a7ffcore11e_a00dcc5b97bfdd5d9c | open_interest_like\|positioning_like | delta_x_divergence |            12 |     0.000286622 |                  -0.000218633 |    1.51785  |            1.02663  |                                0 | False          |
| a7ffcore11e_a01a8daf0ec6df52a7 | taker_flow_like\|open_interest_like  | flow_x_leverage    |            12 |    -0.00788238  |                  -0.00858238  |    1.29029  |            1.28462  |                                0 | False          |
| a7ffcore11e_b22e934b8b01b76133 | taker_flow_like\|basis_premium_like  | gated_sign         |            12 |     0.000227412 |                  -0.000328586 |    1.20301  |            1.45422  |                                0 | False          |
| a7ffcore11e_128fbfeb466690f7c9 | liquidity_like\|volatility_like      | liquidity_shock    |            12 |     0.0010253   |                   0.000183431 |    1.20161  |            0.775325 |                                1 | False          |
| a7ffcore11e_5547922f53cc90e0a1 | liquidity_like                       | single             |            12 |    -0.000248833 |                  -0.000943595 |    0.703068 |            1.42748  |                                0 | False          |
| a7ffcore11e_5fcd7ebabb6db4aee5 | liquidity_like                       | single             |            12 |    -0.0141285   |                  -0.0148285   |   -0.906241 |            7.18351  |                                0 | False          |

## Boundary

```text
bounded replay: true
formula search / large search: false
promotion: false
alpha proof / shadow / paper / live: false
```
