# CRYPTO A7FF-CORE6 MATERIALIZATION PREFLIGHT CONTRACT

Generated: 2026-05-31T18:10:52Z

## Decision

`PASS_A7FFCORE6_MATERIALIZATION_PREFLIGHT_CONTRACT_READY_FOR_CORE6E`

A7FF-CORE6 defines the materialization preflight contract for the CORE5 gate-native queue. It does not execute materialization, numeric response, replay, search, or promotion.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core6e": true,
  "authorizes_numeric": false,
  "authorizes_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FFCORE6_MATERIALIZATION_PREFLIGHT_CONTRACT_READY_FOR_CORE6E",
  "executes_materialization": false,
  "executes_numeric": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-31T18:10:52Z",
  "input_queue_rows": 2048,
  "next_allowed": "A7FF-CORE6E gate-native materialization preflight execution",
  "preflight_check_count": 8,
  "required_field_count": 35,
  "shard_count": 8,
  "shard_size": 256,
  "source_decision": "PASS_A7FFCORE5_GATE_NATIVE_DRYRUN_READY_FOR_CORE6",
  "source_stage": "A7FF-CORE5",
  "stage": "A7FF-CORE6",
  "uses_may": false
}
```

## Shard Plan

| shard_id   |   start_index |   end_index_exclusive |   candidate_count |   semantic_bucket_count |   motif_bucket_count |   raw_field_count | expected_output                                                                 |
|:-----------|--------------:|----------------------:|------------------:|------------------------:|---------------------:|------------------:|:--------------------------------------------------------------------------------|
| S00        |             0 |                   256 |               256 |                       2 |                    2 |                13 | runtime/a7ffcore6e_materialization_preflight/a7ffcore6e_S00_materialization.csv |
| S01        |           256 |                   512 |               256 |                       3 |                    4 |                14 | runtime/a7ffcore6e_materialization_preflight/a7ffcore6e_S01_materialization.csv |
| S02        |           512 |                   768 |               256 |                       3 |                    4 |                12 | runtime/a7ffcore6e_materialization_preflight/a7ffcore6e_S02_materialization.csv |
| S03        |           768 |                  1024 |               256 |                       3 |                    3 |                13 | runtime/a7ffcore6e_materialization_preflight/a7ffcore6e_S03_materialization.csv |
| S04        |          1024 |                  1280 |               256 |                       3 |                    3 |                11 | runtime/a7ffcore6e_materialization_preflight/a7ffcore6e_S04_materialization.csv |
| S05        |          1280 |                  1536 |               256 |                       1 |                    2 |                 5 | runtime/a7ffcore6e_materialization_preflight/a7ffcore6e_S05_materialization.csv |
| S06        |          1536 |                  1792 |               256 |                       1 |                    2 |                 5 | runtime/a7ffcore6e_materialization_preflight/a7ffcore6e_S06_materialization.csv |
| S07        |          1792 |                  2048 |               256 |                       1 |                    1 |                 5 | runtime/a7ffcore6e_materialization_preflight/a7ffcore6e_S07_materialization.csv |

## Required Field Plan

| raw_field                            |   candidate_count | semantic_buckets                                                                                                           | required_in_panel   | missing_policy            |
|:-------------------------------------|------------------:|:---------------------------------------------------------------------------------------------------------------------------|:--------------------|:--------------------------|
| age_x_liquidity                      |                12 | liquidity_like                                                                                                             | True                | fail_closed_for_candidate |
| age_x_volatility                     |               282 | liquidity_like\|volatility_like                                                                                            | True                | fail_closed_for_candidate |
| global_long_short_account_ratio_last |                49 | open_interest_like\|positioning_like                                                                                       | True                | fail_closed_for_candidate |
| global_long_short_account_ratio_mean |                49 | open_interest_like\|positioning_like                                                                                       | True                | fail_closed_for_candidate |
| index_close                          |                45 | taker_flow_like\|basis_premium_like                                                                                        | True                | fail_closed_for_candidate |
| liquidity_rank_active_universe       |                12 | liquidity_like                                                                                                             | True                | fail_closed_for_candidate |
| log_quote_volume_168h                |                12 | liquidity_like                                                                                                             | True                | fail_closed_for_candidate |
| mark_close                           |                51 | taker_flow_like\|basis_premium_like                                                                                        | True                | fail_closed_for_candidate |
| mark_high                            |                55 | taker_flow_like\|basis_premium_like                                                                                        | True                | fail_closed_for_candidate |
| mark_index_basis_bps                 |                 9 | taker_flow_like\|basis_premium_like                                                                                        | True                | fail_closed_for_candidate |
| mark_low                             |                32 | taker_flow_like\|basis_premium_like                                                                                        | True                | fail_closed_for_candidate |
| median_quote_volume_168h             |                12 | liquidity_like                                                                                                             | True                | fail_closed_for_candidate |
| open_interest_change_24h             |                12 | open_interest_like                                                                                                         | True                | fail_closed_for_candidate |
| open_interest_last                   |               371 | open_interest_like;open_interest_like\|positioning_like;open_interest_like\|price_like;taker_flow_like\|open_interest_like | True                | fail_closed_for_candidate |
| open_interest_mean                   |               155 | open_interest_like;open_interest_like\|price_like;taker_flow_like\|open_interest_like                                      | True                | fail_closed_for_candidate |
| open_interest_value_last             |                53 | open_interest_like;taker_flow_like\|open_interest_like                                                                     | True                | fail_closed_for_candidate |
| open_interest_value_mean             |                45 | open_interest_like;taker_flow_like\|open_interest_like                                                                     | True                | fail_closed_for_candidate |
| realized_vol_168h                    |               183 | liquidity_like\|volatility_like;volatility_like                                                                            | True                | fail_closed_for_candidate |
| realized_vol_24h                     |                12 | volatility_like                                                                                                            | True                | fail_closed_for_candidate |
| taker_buy_quote_volume               |               396 | taker_flow_like;taker_flow_like\|basis_premium_like;taker_flow_like\|open_interest_like                                    | True                | fail_closed_for_candidate |
| taker_buy_sell_volume_ratio_last     |                12 | taker_flow_like                                                                                                            | True                | fail_closed_for_candidate |
| taker_buy_sell_volume_ratio_mean     |                12 | taker_flow_like                                                                                                            | True                | fail_closed_for_candidate |
| taker_buy_volume                     |                12 | taker_flow_like                                                                                                            | True                | fail_closed_for_candidate |
| top_long_short_account_ratio_last    |                55 | open_interest_like\|positioning_like                                                                                       | True                | fail_closed_for_candidate |
| top_long_short_account_ratio_mean    |                39 | open_interest_like\|positioning_like                                                                                       | True                | fail_closed_for_candidate |
| trade_close                          |               135 | open_interest_like\|price_like                                                                                             | True                | fail_closed_for_candidate |
| trade_count                          |              1064 | liquidity_like;liquidity_like\|volatility_like                                                                             | True                | fail_closed_for_candidate |
| trade_count_168h                     |                12 | liquidity_like                                                                                                             | True                | fail_closed_for_candidate |
| trade_high                           |               291 | liquidity_like\|volatility_like                                                                                            | True                | fail_closed_for_candidate |
| trade_low                            |               296 | liquidity_like\|volatility_like                                                                                            | True                | fail_closed_for_candidate |
| trade_quote_volume                   |                12 | liquidity_like                                                                                                             | True                | fail_closed_for_candidate |
| trade_return_1h                      |                42 | open_interest_like\|price_like                                                                                             | True                | fail_closed_for_candidate |
| trade_return_24h                     |                15 | open_interest_like\|price_like                                                                                             | True                | fail_closed_for_candidate |
| trade_volume                         |                12 | liquidity_like                                                                                                             | True                | fail_closed_for_candidate |
| volume_volatility_ratio_168h         |                12 | liquidity_like                                                                                                             | True                | fail_closed_for_candidate |

## Preflight Checks

| check_id                   | rule                                                                                         | hard_gate   |
|:---------------------------|:---------------------------------------------------------------------------------------------|:------------|
| C00_input_queue_integrity  | candidate_id/root_subgraph_id unique, gate_allowed=true for all rows                         | True        |
| C01_panel_field_presence   | all raw_inputs exist in experiment panel or candidate fails closed                           | True        |
| C02_operator_support       | expression operators supported by FeatureAlgebra before evaluation                           | True        |
| C03_materialization_finite | finite ratio and active coverage emitted per candidate                                       | True        |
| C04_no_label_or_may        | no label, future, May stress, or pass/fail tokens in materialized expression                 | True        |
| C05_no_return_scoring      | preflight does not compute labels, returns, IC, spread, replay, selector score, or promotion | True        |
| C06_shard_manifest         | each shard writes manifest with failure counts and reject reasons                            | True        |
| C07_role_preservation      | diagnostic roots remain diagnostic; ordinary alpha remains unauthorized                      | True        |

## Execution Contract

```json
{
  "allowed_actions": [
    "load panel",
    "evaluate expressions for finite/activity/materialization only",
    "emit per-candidate finite/activity/missing/operator status",
    "emit shard manifests"
  ],
  "candidate_count": 2048,
  "forbidden_actions": [
    "compute forward returns",
    "compute labels",
    "compute IC/spread/PnL",
    "run replay",
    "run selector",
    "run search",
    "promote candidates",
    "use May stress labels or pass/fail"
  ],
  "input_queue": "runtime\\a7ffcore5_gate_native_generation_dryrun\\a7ffcore5_gate_native_candidate_queue.csv",
  "pass_conditions": {
    "eval_failure_rate_max": 0.02,
    "label_or_may_token_count": 0,
    "missing_field_rate_max": 0.01,
    "ordinary_alpha_leak_count": 0,
    "role_violation_count": 0
  },
  "shard_count": 8,
  "shard_size": 256,
  "stage": "A7FF-CORE6E"
}
```

## Boundary

```text
materialization executed: false
numeric execution: false
replay executed: false
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```
