# CRYPTO A7FF-CORE14E BOUNDED REPLAY EXECUTION

Generated: 2026-06-01T06:12:54Z

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
  "generated_at": "2026-06-01T06:12:54Z",
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
| liquidity_like\|volatility_like      | liquidity_shock    |                 2 |                  -0.00068108  |                1.56464 |                       0 |
| open_interest_like\|positioning_like | delta_x_divergence |                 2 |                  -0.000667807 |                2.46654 |                       0 |
| taker_flow_like\|basis_premium_like  | gated_sign         |                 2 |                  -0.000477232 |                2.15365 |                       0 |
| taker_flow_like\|open_interest_like  | flow_x_leverage    |                 2 |                  -0.0131069   |                1.47639 |                       0 |

## Candidate Summary

| candidate_id                   | semantic_bucket                      | motif_bucket       |   replay_rows |   median_spread |   median_cost_adjusted_spread |   max_tstat |   min_control_ratio |   validation_recent_clean_splits | replay_clean   |
|:-------------------------------|:-------------------------------------|:-------------------|--------------:|----------------:|------------------------------:|------------:|--------------------:|---------------------------------:|:---------------|
| a7ffcore11e_786722cdd2764b2c2b | taker_flow_like\|open_interest_like  | flow_x_leverage    |            12 |    -0.00737708  |                  -0.00807708  |   2.10653   |            1.10909  |                                0 | False          |
| a7ffcore11e_5ba23f43a8b1fe6632 | taker_flow_like\|basis_premium_like  | gated_sign         |            12 |    -0.000220232 |                  -0.000697547 |   1.80217   |            1.90382  |                                0 | False          |
| a7ffcore11e_78fc00f4702d1eb00f | taker_flow_like\|basis_premium_like  | gated_sign         |            12 |     0.000420398 |                  -0.000317859 |   1.48645   |            1.47801  |                                0 | False          |
| a7ffcore11e_378937c1d066186b94 | liquidity_like\|volatility_like      | liquidity_shock    |            12 |     7.11869e-05 |                  -0.00068108  |   1.32037   |            0.980416 |                                0 | False          |
| a7ffcore11e_75b2088e35389d3ce8 | open_interest_like\|positioning_like | delta_x_divergence |            12 |     0.000302841 |                  -0.000485551 |   1.16411   |            1.52598  |                                0 | False          |
| a7ffcore11e_4818a1b365e426cb4f | liquidity_like\|volatility_like      | liquidity_shock    |            12 |     0.000209823 |                  -0.000609321 |   1.04016   |            0.804895 |                                0 | False          |
| a7ffcore11e_2dd63f13fdbb9a227d | taker_flow_like\|open_interest_like  | flow_x_leverage    |            12 |    -0.0168368   |                  -0.0175368   |   0.861548  |            0.568359 |                                1 | False          |
| a7ffcore11e_a556c4fd6dec7dc783 | open_interest_like\|positioning_like | delta_x_divergence |            12 |    -0.000104009 |                  -0.0010059   |  -0.0647252 |            1.92332  |                                0 | False          |

## Boundary

```text
bounded replay: true
formula search / large search: false
promotion: false
alpha proof / shadow / paper / live: false
```
