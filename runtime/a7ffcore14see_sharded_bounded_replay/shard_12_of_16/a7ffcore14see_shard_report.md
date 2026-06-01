# CRYPTO A7FF-CORE14E BOUNDED REPLAY EXECUTION

Generated: 2026-06-01T06:42:19Z

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
  "generated_at": "2026-06-01T06:42:19Z",
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
| open_interest_like\|positioning_like | delta_x_divergence |                 4 |                  -7.81923e-05 |                3.30486 |                       0 |
| liquidity_like                       | single             |                 3 |                  -0.000820278 |                5.07464 |                       0 |
| taker_flow_like\|open_interest_like  | flow_x_leverage    |                 1 |                  -0.0238989   |                1.5771  |                       0 |

## Candidate Summary

| candidate_id                   | semantic_bucket                      | motif_bucket       |   replay_rows |   median_spread |   median_cost_adjusted_spread |   max_tstat |   min_control_ratio |   validation_recent_clean_splits | replay_clean   |
|:-------------------------------|:-------------------------------------|:-------------------|--------------:|----------------:|------------------------------:|------------:|--------------------:|---------------------------------:|:---------------|
| a7ffcore11e_fc6bdefcaa18d8c47f | open_interest_like\|positioning_like | delta_x_divergence |            12 |     0.000192334 |                  -0.000269317 |    2.40363  |            0.687067 |                                1 | False          |
| a7ffcore11e_af11f81ccebb87b897 | open_interest_like\|positioning_like | delta_x_divergence |            12 |     0.000174208 |                  -0.000566276 |    1.95341  |            0.726445 |                                0 | False          |
| a7ffcore11e_ddc7af9711beac20b7 | open_interest_like\|positioning_like | delta_x_divergence |            12 |     7.87649e-05 |                  -0.000402089 |    1.71832  |            0.880021 |                                1 | False          |
| a7ffcore11e_465f7bfa7dc84e38bc | taker_flow_like\|open_interest_like  | flow_x_leverage    |            12 |    -0.0231989   |                  -0.0238989   |    0.811147 |            0.909154 |                                1 | False          |
| a7ffcore11e_6dfea25769981420cd | liquidity_like                       | single             |            12 |     0.000129675 |                  -0.000515837 |    0.787119 |            4.22491  |                                0 | False          |
| a7ffcore11e_31ccb7f2f91aa7e9d2 | open_interest_like\|positioning_like | delta_x_divergence |            12 |     0.00442058  |                   0.00378423  |    0.596897 |            3.41625  |                                0 | False          |
| a7ffcore11e_ceecd13760f1f015e9 | liquidity_like                       | single             |            12 |    -0.000657455 |                  -0.00150117  |    0.445758 |            0.991123 |                                0 | False          |
| a7ffcore11e_e1c2883b278209d9b5 | liquidity_like                       | single             |            12 |     0.000566278 |                  -0.000133722 |    0.374974 |            2.03097  |                                0 | False          |

## Boundary

```text
bounded replay: true
formula search / large search: false
promotion: false
alpha proof / shadow / paper / live: false
```
