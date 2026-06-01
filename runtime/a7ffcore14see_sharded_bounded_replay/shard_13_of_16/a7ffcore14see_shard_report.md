# CRYPTO A7FF-CORE14E BOUNDED REPLAY EXECUTION

Generated: 2026-06-01T06:48:00Z

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
  "generated_at": "2026-06-01T06:48:00Z",
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
| liquidity_like                       | single             |                 3 |                  -0.0017482   |               6.75544  |                       0 |
| taker_flow_like\|open_interest_like  | flow_x_leverage    |                 2 |                  -0.000292209 |               2.31937  |                       0 |
| liquidity_like\|volatility_like      | liquidity_shock    |                 1 |                   0.0104251   |               2.03307  |                       0 |
| open_interest_like\|positioning_like | delta_x_divergence |                 1 |                  -0.000299444 |               0.59575  |                       0 |
| taker_flow_like\|basis_premium_like  | gated_sign         |                 1 |                  -0.0321486   |               0.795178 |                       0 |

## Candidate Summary

| candidate_id                   | semantic_bucket                      | motif_bucket       |   replay_rows |   median_spread |   median_cost_adjusted_spread |   max_tstat |   min_control_ratio |   validation_recent_clean_splits | replay_clean   |
|:-------------------------------|:-------------------------------------|:-------------------|--------------:|----------------:|------------------------------:|------------:|--------------------:|---------------------------------:|:---------------|
| a7ffcore11e_4e7b517b4c814fa61d | taker_flow_like\|open_interest_like  | flow_x_leverage    |            12 |     0.0170135   |                   0.0163135   |   3.39132   |            0.917464 |                                0 | False          |
| a7ffcore11e_51a74f307e719e43d3 | liquidity_like\|volatility_like      | liquidity_shock    |            12 |     0.0111251   |                   0.0104251   |   2.51255   |            1.34111  |                                0 | False          |
| a7ffcore11e_a4d5de17fe7d2743f6 | open_interest_like\|positioning_like | delta_x_divergence |            12 |     0.000319619 |                  -0.000299444 |   2.45004   |            0.538978 |                                1 | False          |
| a7ffcore11e_98aa19f1e45c8bab15 | taker_flow_like\|open_interest_like  | flow_x_leverage    |            12 |     0.000169211 |                  -0.000721968 |   0.995598  |            1.76302  |                                0 | False          |
| a7ffcore11e_b50799eaf4f797bc7c | liquidity_like                       | single             |            12 |     0.000225797 |                  -0.000501103 |   0.759929  |            4.07865  |                                0 | False          |
| a7ffcore11e_9f7d56ec455eafc3b3 | taker_flow_like\|basis_premium_like  | gated_sign         |            12 |    -0.0314486   |                  -0.0321486   |   0.558678  |            0.686716 |                                0 | False          |
| a7ffcore11e_72425732c25c5581c6 | liquidity_like                       | single             |            12 |    -0.00072219  |                  -0.0014662   |   0.0868485 |            0.893692 |                                0 | False          |
| a7ffcore11e_b83343f0b5d2a912a3 | liquidity_like                       | single             |            12 |    -0.0123485   |                  -0.0130625   |  -0.902559  |            6.75544  |                                0 | False          |

## Boundary

```text
bounded replay: true
formula search / large search: false
promotion: false
alpha proof / shadow / paper / live: false
```
