# CRYPTO A7FF-CORE14E BOUNDED REPLAY EXECUTION

Generated: 2026-06-01T06:12:38Z

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
  "generated_at": "2026-06-01T06:12:38Z",
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
| liquidity_like\|volatility_like      | liquidity_shock    |                 4 |                  -0.000625265 |                1.80512 |                       0 |
| taker_flow_like\|basis_premium_like  | gated_sign         |                 2 |                  -0.000224956 |                1.75986 |                       0 |
| open_interest_like\|positioning_like | delta_x_divergence |                 1 |                   0.00242149  |                1.26715 |                       0 |
| taker_flow_like\|open_interest_like  | flow_x_leverage    |                 1 |                  -0.000908212 |                1.43132 |                       0 |

## Candidate Summary

| candidate_id                   | semantic_bucket                      | motif_bucket       |   replay_rows |   median_spread |   median_cost_adjusted_spread |   max_tstat |   min_control_ratio |   validation_recent_clean_splits | replay_clean   |
|:-------------------------------|:-------------------------------------|:-------------------|--------------:|----------------:|------------------------------:|------------:|--------------------:|---------------------------------:|:---------------|
| a7ffcore11e_108bca7372512beafd | taker_flow_like\|basis_premium_like  | gated_sign         |            12 |     0.000788985 |                  -0.000224956 |    2.71713  |            0.689223 |                                1 | False          |
| a7ffcore11e_ec26834009da0d5054 | taker_flow_like\|basis_premium_like  | gated_sign         |            12 |     0.000380049 |                  -0.000205858 |    1.938    |            1.5816   |                                0 | False          |
| a7ffcore11e_1a0c13e0697780faa7 | liquidity_like\|volatility_like      | liquidity_shock    |            12 |     0.000153212 |                  -0.000595055 |    1.64029  |            0.618296 |                                0 | False          |
| a7ffcore11e_4eb5978085468b9ad6 | taker_flow_like\|open_interest_like  | flow_x_leverage    |            12 |    -0.000409261 |                  -0.000908212 |    1.25679  |            1.2227   |                                0 | False          |
| a7ffcore11e_304ee6a37c57dbed99 | liquidity_like\|volatility_like      | liquidity_shock    |            12 |    -6.83119e-05 |                  -0.000635496 |    1.07906  |            1.74612  |                                0 | False          |
| a7ffcore11e_209eed7b9edd873a00 | liquidity_like\|volatility_like      | liquidity_shock    |            12 |     1.59564e-05 |                  -0.000577886 |    0.911145 |            1.09307  |                                0 | False          |
| a7ffcore11e_1ca2fdf47a1754478f | liquidity_like\|volatility_like      | liquidity_shock    |            12 |    -0.000238429 |                  -0.000778429 |    0.836462 |            1.35535  |                                0 | False          |
| a7ffcore11e_c992169ade0f4c15f9 | open_interest_like\|positioning_like | delta_x_divergence |            12 |     0.00312149  |                   0.00242149  |    0.790118 |            0.958674 |                                0 | False          |

## Boundary

```text
bounded replay: true
formula search / large search: false
promotion: false
alpha proof / shadow / paper / live: false
```
