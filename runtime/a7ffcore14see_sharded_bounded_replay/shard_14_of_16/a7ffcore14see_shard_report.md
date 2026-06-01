# CRYPTO A7FF-CORE14E BOUNDED REPLAY EXECUTION

Generated: 2026-06-01T06:52:39Z

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
  "generated_at": "2026-06-01T06:52:39Z",
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
| taker_flow_like\|basis_premium_like  | gated_sign         |                 3 |                  -0.000152959 |               4.8728   |                       0 |
| liquidity_like                       | single             |                 1 |                  -0.000880395 |               4.37414  |                       0 |
| liquidity_like\|volatility_like      | liquidity_shock    |                 1 |                  -0.000583494 |               1.51909  |                       0 |
| open_interest_like                   | single             |                 1 |                  -0.0587929   |               0.854668 |                       0 |
| open_interest_like\|positioning_like | delta_x_divergence |                 1 |                  -0.000519232 |               4.00075  |                       0 |
| taker_flow_like\|open_interest_like  | flow_x_leverage    |                 1 |                  -0.00962536  |               0.796203 |                       0 |

## Candidate Summary

| candidate_id                   | semantic_bucket                      | motif_bucket       |   replay_rows |   median_spread |   median_cost_adjusted_spread |   max_tstat |   min_control_ratio |   validation_recent_clean_splits | replay_clean   |
|:-------------------------------|:-------------------------------------|:-------------------|--------------:|----------------:|------------------------------:|------------:|--------------------:|---------------------------------:|:---------------|
| a7ffcore11e_4b1d4e93461662a639 | taker_flow_like\|basis_premium_like  | gated_sign         |            12 |     0.00053725  |                  -0.000263926 |   3.02787   |            0.723134 |                                0 | False          |
| a7ffcore11e_53398432f11d66ec78 | liquidity_like\|volatility_like      | liquidity_shock    |            12 |     0.000134706 |                  -0.000583494 |   1.87452   |            0.368664 |                                0 | False          |
| a7ffcore11e_c21abf533e137c4adb | taker_flow_like\|basis_premium_like  | gated_sign         |            12 |     0.00026114  |                  -0.000276485 |   1.58812   |            0.815163 |                                0 | False          |
| a7ffcore11e_a4af4b33c8e3583f45 | open_interest_like\|positioning_like | delta_x_divergence |            12 |     0.000250226 |                  -0.000519232 |   1.33872   |            2.06675  |                                0 | False          |
| a7ffcore11e_243f32b909d9469672 | liquidity_like                       | single             |            12 |    -0.00019274  |                  -0.000880395 |   0.782625  |            1.67452  |                                0 | False          |
| a7ffcore11e_232dfcce9285c35713 | taker_flow_like\|basis_premium_like  | gated_sign         |            12 |     0.0149586   |                   0.0142586   |   0.646868  |            2.08532  |                                0 | False          |
| a7ffcore11e_7ac5f3f71a00807f00 | taker_flow_like\|open_interest_like  | flow_x_leverage    |            12 |    -0.00892536  |                  -0.00962536  |   0.520648  |            0.542422 |                                0 | False          |
| a7ffcore11e_249d2f15f6613eda70 | open_interest_like                   | single             |            12 |    -0.0580929   |                  -0.0587929   |   0.0337921 |            0.646125 |                                0 | False          |

## Boundary

```text
bounded replay: true
formula search / large search: false
promotion: false
alpha proof / shadow / paper / live: false
```
