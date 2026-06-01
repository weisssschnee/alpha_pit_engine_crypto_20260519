# CRYPTO A7FF-CORE14E BOUNDED REPLAY EXECUTION

Generated: 2026-06-01T06:19:57Z

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
  "generated_at": "2026-06-01T06:19:57Z",
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
| open_interest_like\|positioning_like | delta_x_divergence |                 3 |                  -0.00032748  |                2.70847 |                       0 |
| liquidity_like\|volatility_like      | liquidity_shock    |                 2 |                  -0.00101995  |                1.81274 |                       0 |
| taker_flow_like\|basis_premium_like  | gated_sign         |                 2 |                   0.00423533  |                3.33437 |                       0 |
| liquidity_like                       | single             |                 1 |                  -0.000887171 |                5.04795 |                       0 |

## Candidate Summary

| candidate_id                   | semantic_bucket                      | motif_bucket       |   replay_rows |   median_spread |   median_cost_adjusted_spread |   max_tstat |   min_control_ratio |   validation_recent_clean_splits | replay_clean   |
|:-------------------------------|:-------------------------------------|:-------------------|--------------:|----------------:|------------------------------:|------------:|--------------------:|---------------------------------:|:---------------|
| a7ffcore11e_20eecb5636ab8e3aa6 | taker_flow_like\|basis_premium_like  | gated_sign         |            12 |     0.0195556   |                   0.0188556   |    1.47555  |            1.95689  |                                0 | False          |
| a7ffcore11e_3ec57ea3f99c39e17e | liquidity_like\|volatility_like      | liquidity_shock    |            12 |     0.000131022 |                  -0.000640472 |    1.4611   |            0.75584  |                                0 | False          |
| a7ffcore11e_00be7384a5748c067d | open_interest_like\|positioning_like | delta_x_divergence |            12 |     0.000366438 |                  -0.000516665 |    1.30111  |            0.744891 |                                0 | False          |
| a7ffcore11e_569efbd1f4836d446c | open_interest_like\|positioning_like | delta_x_divergence |            12 |     0.000154943 |                  -0.000507698 |    1.21242  |            2.42661  |                                0 | False          |
| a7ffcore11e_620048b49bc3dfd43f | taker_flow_like\|basis_premium_like  | gated_sign         |            12 |    -9.20697e-05 |                  -0.000537917 |    1.16573  |            1.84745  |                                0 | False          |
| a7ffcore11e_7036d028e1478c3480 | liquidity_like                       | single             |            12 |    -0.000160239 |                  -0.000887171 |    0.746512 |            2.1902   |                                0 | False          |
| a7ffcore11e_3f9b525882214df808 | liquidity_like\|volatility_like      | liquidity_shock    |            12 |    -0.00173941  |                  -0.00243941  |    0.586729 |            0.973382 |                                0 | False          |
| a7ffcore11e_420e99b8a278dc4c8e | open_interest_like\|positioning_like | delta_x_divergence |            12 |     0.00464957  |                   0.00346078  |    0.539059 |            2.1591   |                                0 | False          |

## Boundary

```text
bounded replay: true
formula search / large search: false
promotion: false
alpha proof / shadow / paper / live: false
```
