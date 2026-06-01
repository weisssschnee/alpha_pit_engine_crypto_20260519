# CRYPTO A7FF-CORE14E BOUNDED REPLAY EXECUTION

Generated: 2026-06-01T06:33:58Z

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
  "generated_at": "2026-06-01T06:33:58Z",
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
| taker_flow_like\|open_interest_like  | flow_x_leverage    |                 3 |                  -0.000427335 |                2.57058 |                       0 |
| liquidity_like                       | single             |                 2 |                  -0.0419708   |                2.96473 |                       0 |
| open_interest_like\|positioning_like | delta_x_divergence |                 2 |                  -0.000133515 |                2.30637 |                       0 |
| liquidity_like\|volatility_like      | liquidity_shock    |                 1 |                   0.0151586   |                1.4244  |                       0 |

## Candidate Summary

| candidate_id                   | semantic_bucket                      | motif_bucket       |   replay_rows |   median_spread |   median_cost_adjusted_spread |   max_tstat |   min_control_ratio |   validation_recent_clean_splits | replay_clean   |
|:-------------------------------|:-------------------------------------|:-------------------|--------------:|----------------:|------------------------------:|------------:|--------------------:|---------------------------------:|:---------------|
| a7ffcore11e_d1dbc4fba532ff5c83 | open_interest_like\|positioning_like | delta_x_divergence |            12 |     0.000128277 |                  -0.000531619 |   1.55513   |            1.01708  |                                0 | False          |
| a7ffcore11e_3ff6e83f7edc4df79d | taker_flow_like\|open_interest_like  | flow_x_leverage    |            12 |     0.000142088 |                  -0.000431455 |   1.39651   |            1.83416  |                                0 | False          |
| a7ffcore11e_54790864840dc185ed | taker_flow_like\|open_interest_like  | flow_x_leverage    |            12 |     0.0144981   |                   0.0137981   |   1.07141   |            1.55189  |                                0 | False          |
| a7ffcore11e_0e361fe8b6d1b5a25e | liquidity_like                       | single             |            12 |    -0.0561813   |                  -0.0568813   |   0.925085  |            1.54359  |                                0 | False          |
| a7ffcore11e_7b72349fd51af1e863 | taker_flow_like\|open_interest_like  | flow_x_leverage    |            12 |    -0.000102918 |                  -0.000693149 |   0.861787  |            2.57058  |                                0 | False          |
| a7ffcore11e_1912a535f0533e1786 | liquidity_like\|volatility_like      | liquidity_shock    |            12 |     0.0158586   |                   0.0151586   |   0.682708  |            0.775577 |                                0 | False          |
| a7ffcore11e_7ba27cc9e55fb01b78 | open_interest_like\|positioning_like | delta_x_divergence |            12 |     0.00271734  |                   0.00201734  |   0.415922  |            2.68455  |                                0 | False          |
| a7ffcore11e_0dc6c3e8b869e22675 | liquidity_like                       | single             |            12 |    -0.0257602   |                  -0.0264602   |   0.0452648 |            1.03787  |                                0 | False          |

## Boundary

```text
bounded replay: true
formula search / large search: false
promotion: false
alpha proof / shadow / paper / live: false
```
