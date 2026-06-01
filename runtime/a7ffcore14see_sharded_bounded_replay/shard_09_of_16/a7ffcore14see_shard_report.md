# CRYPTO A7FF-CORE14E BOUNDED REPLAY EXECUTION

Generated: 2026-06-01T06:37:06Z

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
  "generated_at": "2026-06-01T06:37:06Z",
  "next_allowed": "A7FF-CORE14R replay failure forensic",
  "replay_clean_candidate_count": 1,
  "replay_clean_motif_bucket_count": 1,
  "replay_clean_semantic_bucket_count": 1,
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
| taker_flow_like\|basis_premium_like  | gated_sign         |                 2 |                  -0.000100513 |                2.67457 |                       1 |
| liquidity_like\|volatility_like      | liquidity_shock    |                 2 |                   0.0076839   |                2.0789  |                       0 |
| open_interest_like\|positioning_like | delta_x_divergence |                 2 |                  -0.0003354   |                2.05033 |                       0 |
| liquidity_like                       | single             |                 1 |                  -0.00101797  |                6.25767 |                       0 |
| open_interest_like                   | single             |                 1 |                  -0.0138623   |                8.73703 |                       0 |

## Candidate Summary

| candidate_id                   | semantic_bucket                      | motif_bucket       |   replay_rows |   median_spread |   median_cost_adjusted_spread |   max_tstat |   min_control_ratio |   validation_recent_clean_splits | replay_clean   |
|:-------------------------------|:-------------------------------------|:-------------------|--------------:|----------------:|------------------------------:|------------:|--------------------:|---------------------------------:|:---------------|
| a7ffcore11e_a8d20b6bdd9fb53e86 | taker_flow_like\|basis_premium_like  | gated_sign         |            12 |     0.00102972  |                  -3.83035e-05 |    2.85705  |            0.660905 |                                2 | True           |
| a7ffcore11e_deb04a6b50a738278b | taker_flow_like\|basis_premium_like  | gated_sign         |            12 |     0.000321356 |                  -0.000272976 |    1.83048  |            2.18565  |                                0 | False          |
| a7ffcore11e_55b15e2549d259e1de | open_interest_like\|positioning_like | delta_x_divergence |            12 |     0.00011269  |                  -0.000475311 |    1.15448  |            2.40341  |                                0 | False          |
| a7ffcore11e_0c92d2de8de14dfa9b | open_interest_like\|positioning_like | delta_x_divergence |            12 |     0.000349974 |                  -0.000225971 |    0.809664 |            1.42678  |                                0 | False          |
| a7ffcore11e_cfcfbc2592d847facd | liquidity_like                       | single             |            12 |    -0.000109224 |                  -0.00101797  |    0.484445 |            2.70768  |                                0 | False          |
| a7ffcore11e_5232b14de4a03ae851 | liquidity_like\|volatility_like      | liquidity_shock    |            12 |     0.0103518   |                   0.00931365  |    0.435261 |            1.00246  |                                0 | False          |
| a7ffcore11e_578b81923bbfd24556 | liquidity_like\|volatility_like      | liquidity_shock    |            12 |     0.0074468   |                   0.0067468   |    0.372495 |            1.66301  |                                0 | False          |
| a7ffcore11e_0dd768582f272b13e9 | open_interest_like                   | single             |            12 |    -0.0131623   |                  -0.0138623   |   -0.169639 |            0.848136 |                                0 | False          |

## Boundary

```text
bounded replay: true
formula search / large search: false
promotion: false
alpha proof / shadow / paper / live: false
```
