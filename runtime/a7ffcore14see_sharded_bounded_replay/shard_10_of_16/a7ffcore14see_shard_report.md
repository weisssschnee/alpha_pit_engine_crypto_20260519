# CRYPTO A7FF-CORE14E BOUNDED REPLAY EXECUTION

Generated: 2026-06-01T06:44:56Z

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
  "generated_at": "2026-06-01T06:44:56Z",
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
| taker_flow_like\|basis_premium_like  | gated_sign         |                 2 |                  -0.000467346 |                7.30042 |                       0 |
| taker_flow_like\|open_interest_like  | flow_x_leverage    |                 2 |                   0.00387359  |                4.31853 |                       0 |
| liquidity_like                       | single             |                 1 |                  -0.000937774 |                7.70865 |                       0 |
| liquidity_like\|volatility_like      | liquidity_shock    |                 1 |                   0.0154992   |                1.92237 |                       0 |
| open_interest_like                   | single             |                 1 |                  -0.000818321 |                2.40047 |                       0 |
| open_interest_like\|positioning_like | delta_x_divergence |                 1 |                  -0.000835734 |                6.15774 |                       0 |

## Candidate Summary

| candidate_id                   | semantic_bucket                      | motif_bucket       |   replay_rows |   median_spread |   median_cost_adjusted_spread |   max_tstat |   min_control_ratio |   validation_recent_clean_splits | replay_clean   |
|:-------------------------------|:-------------------------------------|:-------------------|--------------:|----------------:|------------------------------:|------------:|--------------------:|---------------------------------:|:---------------|
| a7ffcore11e_4010809000c2176ff9 | taker_flow_like\|basis_premium_like  | gated_sign         |            12 |     0.000401278 |                  -0.000467346 |   3.36882   |             1.62642 |                                0 | False          |
| a7ffcore11e_7572ab199d54ee55bd | taker_flow_like\|open_interest_like  | flow_x_leverage    |            12 |     0.00201552  |                   0.00131552  |   2.21375   |             1.33843 |                                0 | False          |
| a7ffcore11e_1a7a1b7524df8afa77 | taker_flow_like\|open_interest_like  | flow_x_leverage    |            12 |     0.00773166  |                   0.00703166  |   1.63107   |             1.42914 |                                0 | False          |
| a7ffcore11e_808636e7cc38f48be5 | taker_flow_like\|basis_premium_like  | gated_sign         |            12 |     0.000105135 |                  -0.000398169 |   1.09235   |             3.27975 |                                0 | False          |
| a7ffcore11e_49f6cb873f83ad1d4b | liquidity_like\|volatility_like      | liquidity_shock    |            12 |     0.0161992   |                   0.0154992   |   0.807675  |             1.17386 |                                0 | False          |
| a7ffcore11e_01b7a408bae766f6b9 | open_interest_like                   | single             |            12 |     0.000102613 |                  -0.000818321 |   0.801498  |             1.64301 |                                0 | False          |
| a7ffcore11e_94fc8621dfeb133185 | liquidity_like                       | single             |            12 |     8.28713e-05 |                  -0.000937774 |   0.398906  |             2.65244 |                                0 | False          |
| a7ffcore11e_0479a53abe29d8b423 | open_interest_like\|positioning_like | delta_x_divergence |            12 |    -7.78962e-05 |                  -0.000835734 |   0.0314819 |             3.07177 |                                0 | False          |

## Boundary

```text
bounded replay: true
formula search / large search: false
promotion: false
alpha proof / shadow / paper / live: false
```
