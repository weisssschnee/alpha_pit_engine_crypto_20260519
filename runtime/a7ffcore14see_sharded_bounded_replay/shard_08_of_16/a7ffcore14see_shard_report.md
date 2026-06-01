# CRYPTO A7FF-CORE14E BOUNDED REPLAY EXECUTION

Generated: 2026-06-01T06:37:03Z

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
  "generated_at": "2026-06-01T06:37:03Z",
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
| liquidity_like\|volatility_like      | liquidity_shock    |                 2 |                  -0.00126624  |                1.7164  |                       0 |
| open_interest_like\|positioning_like | delta_x_divergence |                 2 |                  -0.0007723   |                3.56033 |                       0 |
| taker_flow_like\|basis_premium_like  | gated_sign         |                 2 |                  -0.0003726   |                5.06509 |                       0 |
| liquidity_like                       | single             |                 1 |                  -0.000711118 |                3.13809 |                       0 |
| taker_flow_like\|open_interest_like  | flow_x_leverage    |                 1 |                  -0.00720682  |                1.81607 |                       0 |

## Candidate Summary

| candidate_id                   | semantic_bucket                      | motif_bucket       |   replay_rows |   median_spread |   median_cost_adjusted_spread |   max_tstat |   min_control_ratio |   validation_recent_clean_splits | replay_clean   |
|:-------------------------------|:-------------------------------------|:-------------------|--------------:|----------------:|------------------------------:|------------:|--------------------:|---------------------------------:|:---------------|
| a7ffcore11e_0e0f0e07398f95176c | taker_flow_like\|basis_premium_like  | gated_sign         |            12 |     0.000324298 |                  -0.000495959 |    2.77688  |            2.34297  |                                0 | False          |
| a7ffcore11e_609ef14715bcbaddaa | taker_flow_like\|basis_premium_like  | gated_sign         |            12 |     0.00017395  |                  -0.00025332  |    2.00695  |            1.89983  |                                0 | False          |
| a7ffcore11e_e4eff4e076eb8cbc67 | open_interest_like\|positioning_like | delta_x_divergence |            12 |     0.000132462 |                  -0.000408368 |    1.60829  |            2.04893  |                                0 | False          |
| a7ffcore11e_9bd6c6bf10234667f4 | liquidity_like                       | single             |            12 |    -0.000233038 |                  -0.000711118 |    1.43999  |            2.23174  |                                0 | False          |
| a7ffcore11e_5d75bda63e8f7deae8 | taker_flow_like\|open_interest_like  | flow_x_leverage    |            12 |    -0.00650682  |                  -0.00720682  |    1.40206  |            1.8057   |                                0 | False          |
| a7ffcore11e_ef8ceadfa18fba4a43 | open_interest_like\|positioning_like | delta_x_divergence |            12 |    -0.000401964 |                  -0.000997588 |    0.534901 |            3.24476  |                                0 | False          |
| a7ffcore11e_1a890ab9e1ac037f7e | liquidity_like\|volatility_like      | liquidity_shock    |            12 |    -0.0407416   |                  -0.0414416   |    0.51156  |            1.3587   |                                0 | False          |
| a7ffcore11e_1f4cb6abf09e6f74da | liquidity_like\|volatility_like      | liquidity_shock    |            12 |    -0.000263064 |                  -0.000893247 |   -0.532293 |            0.912659 |                                0 | False          |

## Boundary

```text
bounded replay: true
formula search / large search: false
promotion: false
alpha proof / shadow / paper / live: false
```
