# CRYPTO A7V3S9 Pre-Reward OOS/Control Proxy Aggregate 20260614

Decision: `PASS_A7V3S9_PROXY_AGGREGATE_SELECTED`

## Counts

- expected_shards: `32`
- manifest_count: `32`
- leaderboard_rows: `2048`
- eval_error_rows: `0`
- strict_pass_rows: `2`
- near_miss_rows: `4`
- selected_rows: `4`

## Bucket Summary

| proxy_bucket    |   count |
|:----------------|--------:|
| proxy_reject    |    2044 |
| proxy_near_miss |       2 |
| proxy_pass      |       2 |

## Selected Pairs

| semantic_pair         |   count |
|:----------------------|--------:|
| basis|positioning     |       1 |
| basis|premium         |       1 |
| liquidity|positioning |       1 |
| positioning|regime    |       1 |

## Selected Motifs

| motif                    |   count |
|:-------------------------|--------:|
| smooth_mul               |       2 |
| signed_rank_gate         |       1 |
| state_conditioned_signed |       1 |

## Top Selected

| blueprint_id            | semantic_pair         | motif                    |   horizon_h | proxy_bucket    |   proxy_score |   recent_sortino |   min_oos_floor_sortino |   stress_floor_sortino |   recent_shuffle_control_ratio | expression                                                                                              |
|:------------------------|:----------------------|:-------------------------|------------:|:----------------|--------------:|-----------------:|------------------------:|-----------------------:|-------------------------------:|:--------------------------------------------------------------------------------------------------------|
| a7v3s0_37b921db0b74a15a | basis|premium         | smooth_mul               |          24 | proxy_pass      |     13.8558   |          1.81475 |              0.85222    |              6.49772   |                     0.00938999 | Mul(Decay(premium_abs_state,336),Abs(ZScore(Mean(mark_trade_basis_bps,168))))                           |
| a7v3s0_cd8127836444fa33 | basis|positioning     | smooth_mul               |           8 | proxy_pass      |      4.79738  |          2.99284 |              0.00663191 |              0.0745033 |                     0.251774   | Mul(ZScore(Mean(global_long_short_account_ratio_last,168)),Abs(ZScore(Mean(mark_index_basis_bps,168)))) |
| a7v3s0_42d6257363202824 | liquidity|positioning | signed_rank_gate         |           8 | proxy_near_miss |      6.91635  |         15.3962  |              0.216118   |             -0.460189  |                     0.149481   | Mul(CSRank(ZScore(Mean(account_position_divergence,3))),Sign(Abs(ZScore(Mean(quote_volume_z_168h,6))))) |
| a7v3s0_9be96eb06dd2c5b6 | positioning|regime    | state_conditioned_signed |           8 | proxy_near_miss |     -0.170667 |          5.36289 |             -0.419656   |             -0.48887   |                     0.467142   | Mul(Decay(global_long_short_account_ratio_last,168),Sign(Decay(liquidity_cycle_state,336)))             |

## Boundary

This aggregate can authorize only bounded full reward on the selected proxy queue. It does not authorize alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_bounded_full_reward": true,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7V3S9_PROXY_AGGREGATE_SELECTED",
  "eval_error_rows": 0,
  "expected_shards": 32,
  "generated_at": "2026-06-14T13:45:03Z",
  "leaderboard_rows": 2048,
  "manifest_count": 32,
  "near_miss_rows": 4,
  "report": "D:\\HermesWorker\\GDrive\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519_remote\\reports\\CRYPTO_A7V3S9_PREREWARD_OOS_CONTROL_PROXY_AGGREGATE_20260614.md",
  "run_root": "D:\\HermesWorker\\GDrive\\AlphaFactory_CryptoData\\research_runtime\\a7v3s9_prereward_oos_control_proxy_20260614",
  "runtime": "D:\\HermesWorker\\GDrive\\AlphaFactory_CryptoData\\research_runtime\\a7v3s9_prereward_oos_control_proxy_aggregate_20260614",
  "selected_queue": "D:\\HermesWorker\\GDrive\\AlphaFactory_CryptoData\\research_runtime\\a7v3s9_prereward_oos_control_proxy_aggregate_20260614\\a7v3s9_proxy_selected_for_reward.csv",
  "selected_rows": 4,
  "selected_unique_blueprints": 4,
  "stage": "A7V3S9_PROXY_AGGREGATE",
  "strict_pass_rows": 2
}
```
