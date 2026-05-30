# CRYPTO A7FF-25R1 NUMERIC ADAPTER PARITY SMOKE

Generated: 2026-05-30T07:24:04Z

## Decision

`PASS_A7FF25R1_NUMERIC_ADAPTER_PARITY_SMOKE`

A7FF-25R1 samples 2 company shards, 50 formulas per shard, and runs the existing numeric probe adapter on 100 formulas. It checks adapter/evaluator/label/control plumbing only. It does not authorize full 12-shard execution, search, or alpha proof.

## Wrapper Manifest

```json
{
  "activity_ok_count": 16,
  "authorizes_a7ff25r2_one_shard_numeric_wave": true,
  "authorizes_alpha_proof": false,
  "authorizes_full_12_shard_numeric": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "control_rows": 6720,
  "decision": "PASS_A7FF25R1_NUMERIC_ADAPTER_PARITY_SMOKE",
  "eval_failure_count": 0,
  "eval_success_count": 20,
  "executes_numeric_probe": true,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T07:24:04Z",
  "label_response_rows": 320,
  "non_l7_numeric_clue_rows": 4,
  "numeric_probe_decision": "HOLD_A7FF25R1_PORTFOLIO_QUEUE_TOO_SMALL",
  "process_exit_code": 0,
  "rank_label_diagnostic_clue_rows": 0,
  "sample_policy": {
    "full_100_rows_recommended_on_company_machine": true,
    "intended_full_adapter_smoke_rows": 100,
    "rows_per_shard": 10,
    "shards": 2
  },
  "sample_rows": 20,
  "sample_shards": [
    "shard_00",
    "shard_01"
  ],
  "source_a7ff25r0_decision": "PASS_A7FF25R0_COMPANY_QUEUE_COVERAGE_ACCEPTABLE_WITH_WARNINGS",
  "stage": "A7FF-25R1-NUMERIC-ADAPTER-PARITY-SMOKE",
  "started_at": "2026-05-30T07:19:09Z",
  "timed_out": false,
  "timeout_seconds": 900,
  "uses_may": false
}
```

## Numeric Probe Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "portfolio_selected_lt_4"
  ],
  "decision": "HOLD_A7FF25R1_PORTFOLIO_QUEUE_TOO_SMALL",
  "executes_generation": false,
  "executes_numeric_probe": true,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T07:24:04Z",
  "input_blueprint_count": 20,
  "label_response_rows": 320,
  "materialized_activity_ok_count": 16,
  "non_l7_numeric_clue_rows": 4,
  "plan": {
    "control_probe_cap": 256,
    "controls": [
      "wrong_lag_future",
      "wrong_lag_stale",
      "time_shuffle",
      "symbol_shuffle",
      "sign_flip",
      "same_family_placebo"
    ],
    "deep_audit_cap": 64,
    "fast_numeric_probe_cap": 256,
    "horizons": [
      "1h",
      "4h",
      "8h",
      "24h"
    ],
    "input_blueprint_source": "runtime/a7ff7e_expanded_derivation_probe_contract/a7ff7e_expanded_blueprint_pool.csv",
    "labels": [
      "L0_raw_forward_return",
      "L1_cross_sectional_relative_return",
      "L3_liquidity_tier_relative_return",
      "L5_vol_adjusted_return",
      "L7_ranked_future_return_diagnostic_only"
    ],
    "materialize_cap": 384,
    "portfolio_marginal_probe_cap": 128,
    "promotion_blockers": [
      "L7-only cannot promote",
      "control_ratio >= 1.0 blocks",
      "single semantic_pair > 35pct blocks",
      "single skeleton > 15pct blocks",
      "numeric replay required before any search authorization"
    ],
    "required_outputs": [
      "a7ff8_materialization_metrics.csv",
      "a7ff8_label_response_metrics.csv",
      "a7ff8_control_dominance_metrics.csv",
      "a7ff8_nonoverlap_stats.csv",
      "a7ff8_portfolio_marginal_proxy.csv",
      "a7ff8_decision_record.json"
    ],
    "selected_blueprints": 384,
    "stage": "A7FF-8",
    "status": "contract_only_not_executed"
  },
  "portfolio_queue_count": 1,
  "queue_limit": 20,
  "queue_offset": 0,
  "queue_path": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ff25r1_numeric_adapter_parity_smoke\\a7ff25r1_sample_queue.csv",
  "queue_total_rows": 20,
  "rank_label_diagnostic_clue_rows": 0,
  "selected_portfolio_queue_count": 1,
  "stage": "A7FF-25R1",
  "uses_may": false
}
```

## Adapter Parity Summary

| check                   |   value | pass   |
|:------------------------|--------:|:-------|
| process_exit_code       |       0 | True   |
| timed_out               |   False | True   |
| sample_rows             |      20 | True   |
| eval_failure_count      |       0 | True   |
| activity_ok_count       |      16 | True   |
| missing_field_blocker   |   False | True   |
| role_violation          |   False | True   |
| label_leakage_violation |   False | True   |
| response_rows           |     320 | True   |
| control_rows            |    6720 | True   |

## Materialization Summary

| blueprint_id             | expression                                                                    | semantic_pair                          | motif      | skeleton_key          | eval_success   |   finite_share |   nonzero_share | activity_ok   |       min_value |   max_value |   std_value |   error |
|:-------------------------|:------------------------------------------------------------------------------|:---------------------------------------|:-----------|:----------------------|:---------------|---------------:|----------------:|:--------------|----------------:|------------:|------------:|--------:|
| a7ff24r_547c0ff8380f3778 | Abs(ZScore(Mean(mark_index_basis_bps,8)))                                     | basis_premium_like                     | single     | skel_1926552988410ac0 | True           |       0.997702 |        1        | True          |     1.38225e-06 |     9.63887 |    0.766947 |     nan |
| a7ff24r_7f71b2e363dddbd6 | Abs(ZScore(Mean(mark_index_basis_bps,168)))                                   | basis_premium_like                     | single     | skel_1926552988410ac0 | True           |       0.993393 |        1        | True          |     6.36318e-08 |     8.80569 |    0.773575 |     nan |
| a7ff24r_d7ef0776f1dae5df | Abs(ZScore(Mean(mark_index_basis_bps,24)))                                    | basis_premium_like                     | single     | skel_1926552988410ac0 | True           |       0.993105 |        1        | True          |     3.96309e-06 |     9.5095  |    0.776655 |     nan |
| a7ff24r_e582d2a2908a95d8 | Abs(ZScore(Mean(mark_index_basis_bps,72)))                                    | basis_premium_like                     | single     | skel_1926552988410ac0 | True           |       0.993393 |        1        | True          |     1.0316e-06  |     9.1412  |    0.778193 |     nan |
| a7ff24r_1313bae0f47d683a | Mean(mark_index_basis_bps,168)                                                | basis_premium_like                     | single     | skel_1d39996e97d5ace0 | True           |       0.993393 |        1        | True          |  -137.281       |    39.0109  |    8.02876  |     nan |
| a7ff24r_1c3b5e472e010cc0 | Mean(mark_index_basis_bps,4)                                                  | basis_premium_like                     | single     | skel_1d39996e97d5ace0 | True           |       0.998851 |        0.999745 | True          |  -956.417       |    98.6259  |   12.0729   |     nan |
| a7ff24r_3c18085739c75d99 | Decay(mark_index_basis_bps,168)                                               | basis_premium_like                     | single     | skel_1d39996e97d5ace0 | True           |       0.993393 |        1        | True          |  -122.824       |    40.9138  |    8.13087  |     nan |
| a7ff24r_49df8a5d77c3bce5 | Mean(mark_index_basis_bps,24)                                                 | basis_premium_like                     | single     | skel_1d39996e97d5ace0 | True           |       0.993105 |        1        | True          |  -375.182       |    52.2237  |    9.79931  |     nan |
| a7ff24r_57e00327a34e91e3 | Delta(mark_index_basis_bps,24)                                                | basis_premium_like                     | single     | skel_1d39996e97d5ace0 | True           |       0.992818 |        0.997742 | True          | -2221.88        |  2219.99    |   18.4127   |     nan |
| a7ff24r_5e3756c09dd9800d | Mean(mark_index_basis_bps,1)                                                  | basis_premium_like                     | single     | skel_1d39996e97d5ace0 | True           |       0        |        0        | False         |   nan           |   nan       |  nan        |     nan |
| a7ff24r_8a9039b769e90dec | Mean(Mul(ZScore(Mean(mark_index_basis_bps,2)),Mean(premium_close_bps,4)),4)   | basis_premium_like\|basis_premium_like | smooth_mul | skel_5e59fd0ac881977f | True           |       0.997989 |        0.960432 | True          |   -49.9702      |  7203.61    |   66.4625   |     nan |
| a7ff24r_902df794e2b7a361 | Mean(Mul(ZScore(Mean(mark_index_basis_bps,1)),Mean(premium_close_bps,8)),4)   | basis_premium_like\|basis_premium_like | smooth_mul | skel_5e59fd0ac881977f | True           |       0        |        0        | False         |   nan           |   nan       |  nan        |     nan |
| a7ff24r_960517509172d6c7 | Mean(Mul(ZScore(Mean(mark_index_basis_bps,2)),Delta(premium_close_bps,2)),4)  | basis_premium_like\|basis_premium_like | smooth_mul | skel_5e59fd0ac881977f | True           |       0.998276 |        0.951064 | True          | -5397.18        |  6158.73    |   40.9216   |     nan |
| a7ff24r_983a5ca49e1bfb63 | Mean(Mul(ZScore(Mean(mark_index_basis_bps,8)),Delta(premium_close_bps,2)),4)  | basis_premium_like\|basis_premium_like | smooth_mul | skel_5e59fd0ac881977f | True           |       0.99684  |        0.950997 | True          | -5787.95        |  6021.01    |   40.7602   |     nan |
| a7ff24r_9e64895261bc01a7 | Mean(Mul(ZScore(Mean(mark_index_basis_bps,12)),Delta(premium_close_bps,1)),4) | basis_premium_like\|basis_premium_like | smooth_mul | skel_5e59fd0ac881977f | True           |       0.995691 |        0.937311 | True          | -4897.64        |  4890.63    |   23.6226   |     nan |
| a7ff24r_9f4b04274d183e7a | Mean(Mul(ZScore(Mean(mark_index_basis_bps,1)),Delta(premium_close_bps,12)),4) | basis_premium_like\|basis_premium_like | smooth_mul | skel_5e59fd0ac881977f | True           |       0        |        0        | False         |   nan           |   nan       |  nan        |     nan |
| a7ff24r_a00c6554f3b344dc | Mean(Mul(ZScore(Mean(mark_index_basis_bps,12)),Mean(premium_close_bps,4)),4)  | basis_premium_like\|basis_premium_like | smooth_mul | skel_5e59fd0ac881977f | True           |       0.995691 |        0.96035  | True          |  -157.532       |  7231.77    |   68.3028   |     nan |
| a7ff24r_a03780c9c21b21b0 | Mean(Mul(ZScore(Mean(mark_index_basis_bps,8)),Delta(premium_close_bps,1)),4)  | basis_premium_like\|basis_premium_like | smooth_mul | skel_5e59fd0ac881977f | True           |       0.99684  |        0.937359 | True          | -5008.64        |  5093.66    |   24.6958   |     nan |
| a7ff24r_a6a4653a40029d9d | Mean(Mul(ZScore(Mean(mark_index_basis_bps,1)),Delta(premium_close_bps,2)),4)  | basis_premium_like\|basis_premium_like | smooth_mul | skel_5e59fd0ac881977f | True           |       0        |        0        | False         |   nan           |   nan       |  nan        |     nan |
| a7ff24r_aa4cd59292b51653 | Mean(Mul(ZScore(Mean(mark_index_basis_bps,4)),Mean(premium_close_bps,12)),4)  | basis_premium_like\|basis_premium_like | smooth_mul | skel_5e59fd0ac881977f | True           |       0.995691 |        0.986827 | True          |  -151.942       |  3791.85    |   55.8672   |     nan |

## Boundary

```text
numeric probe executed: true, sample only
replay executed: false
search executed: false
May used: false
full 12-shard numeric execution authorized: false
next allowed if PASS: A7FF-25R2 one-shard numeric wave
```
