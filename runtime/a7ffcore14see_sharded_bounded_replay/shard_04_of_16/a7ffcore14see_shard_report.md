# CRYPTO A7FF-CORE14E BOUNDED REPLAY EXECUTION

Generated: 2026-06-01T06:24:56Z

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
  "generated_at": "2026-06-01T06:24:56Z",
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
| liquidity_like                       | single             |                 2 |                  -0.000669928 |               1.70627  |                       0 |
| open_interest_like\|positioning_like | delta_x_divergence |                 2 |                   6.56686e-05 |               9.6075   |                       0 |
| liquidity_like\|volatility_like      | liquidity_shock    |                 1 |                  -0.000715077 |               0.847449 |                       0 |
| open_interest_like                   | single             |                 1 |                  -0.00037444  |               3.9522   |                       0 |
| taker_flow_like\|basis_premium_like  | gated_sign         |                 1 |                  -0.000346648 |               2.73274  |                       0 |
| taker_flow_like\|open_interest_like  | flow_x_leverage    |                 1 |                   0.00276947  |               3.70477  |                       0 |

## Candidate Summary

| candidate_id                   | semantic_bucket                      | motif_bucket       |   replay_rows |   median_spread |   median_cost_adjusted_spread |   max_tstat |   min_control_ratio |   validation_recent_clean_splits | replay_clean   |
|:-------------------------------|:-------------------------------------|:-------------------|--------------:|----------------:|------------------------------:|------------:|--------------------:|---------------------------------:|:---------------|
| a7ffcore11e_a8bc245f20ba6f090e | taker_flow_like\|basis_premium_like  | gated_sign         |            12 |     0.000538126 |                  -0.000346648 |    3.55001  |            1.81321  |                                0 | False          |
| a7ffcore11e_1f85f8127767a83261 | liquidity_like                       | single             |            12 |     0.000410273 |                  -0.000599889 |    1.59168  |            0.333835 |                                0 | False          |
| a7ffcore11e_1942160ee15398d457 | open_interest_like                   | single             |            12 |     7.89736e-06 |                  -0.00037444  |    1.48582  |            0.914855 |                                1 | False          |
| a7ffcore11e_c30d25ca3e543dc63a | open_interest_like\|positioning_like | delta_x_divergence |            12 |     9.29973e-05 |                  -0.000513308 |    1.3607   |            2.03558  |                                0 | False          |
| a7ffcore11e_6754f84bb859b65abb | taker_flow_like\|open_interest_like  | flow_x_leverage    |            12 |     0.00346947  |                   0.00276947  |    1.33156  |            1.174    |                                0 | False          |
| a7ffcore11e_0dd21d80949fec5fb7 | liquidity_like                       | single             |            12 |    -0.000126744 |                  -0.000928274 |    1.14401  |            2.00929  |                                0 | False          |
| a7ffcore11e_548540ad19aff09f23 | liquidity_like\|volatility_like      | liquidity_shock    |            12 |     6.11804e-05 |                  -0.000715077 |    0.950799 |            0.638545 |                                0 | False          |
| a7ffcore11e_45c8c5bf57c2d17bea | open_interest_like\|positioning_like | delta_x_divergence |            12 |     0.00274379  |                   0.00204379  |    0.502769 |            1.89741  |                                0 | False          |

## Boundary

```text
bounded replay: true
formula search / large search: false
promotion: false
alpha proof / shadow / paper / live: false
```
