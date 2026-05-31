# CRYPTO A7FF-CORE5 GATE-NATIVE GENERATION DRYRUN

Generated: 2026-05-31T18:04:10Z

## Decision

`PASS_A7FFCORE5_GATE_NATIVE_DRYRUN_READY_FOR_CORE6`

A7FF-CORE5 builds a gate-native diagnostic queue from CORE2/CORE3 registered root subgraphs. It emits root subgraph references and gate metadata only; it does not create ad hoc raw expressions and does not execute numeric evaluation, replay, search, or promotion.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core6": true,
  "authorizes_numeric": false,
  "authorizes_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FFCORE5_GATE_NATIVE_DRYRUN_READY_FOR_CORE6",
  "executes_gate_native_dryrun": true,
  "executes_numeric": false,
  "executes_replay": false,
  "executes_search": false,
  "gate_pass_count": 2048,
  "generated_at": "2026-05-31T18:04:10Z",
  "motif_bucket_count": 7,
  "next_allowed": "A7FF-CORE6 gate-native materialization preflight contract",
  "ordinary_alpha_allowed_count": 0,
  "queue_rows": 2048,
  "queue_target": 2048,
  "reusable_subgraph_rows": 2820,
  "root_registry_rows": 9240,
  "semantic_bucket_count": 9,
  "source_decision": "PASS_A7FFCORE4_GATE_IMPLEMENTATION_REGRESSION_READY_FOR_CORE5",
  "source_stage": "A7FF-CORE4",
  "stage": "A7FF-CORE5",
  "uses_may": false,
  "uses_raw_expression_construction": false
}
```

## Queue Coverage

| metric                       |   value |
|:-----------------------------|--------:|
| queue_rows                   |    2048 |
| root_registry_rows           |    9240 |
| reusable_subgraph_rows       |    2820 |
| semantic_bucket_count        |       9 |
| motif_bucket_count           |       7 |
| raw_field_count              |      35 |
| gate_pass_count              |    2048 |
| ordinary_alpha_allowed_count |       0 |

## Gate Summary

| gate_allowed   | gate_reason                 | ordinary_alpha_allowed   | ordinary_alpha_reject_reason     |   candidates |
|:---------------|:----------------------------|:-------------------------|:---------------------------------|-------------:|
| True           | approved_diagnostic_root_id | False                    | subgraph_id_not_allowed_for_mode |         2048 |

## Family Summary

| semantic_bucket                      | motif_bucket        |   candidates |   raw_field_count |   gate_pass |
|:-------------------------------------|:--------------------|-------------:|------------------:|------------:|
| liquidity_like\|volatility_like      | liquidity_shock     |          370 |                 5 |         370 |
| liquidity_like\|volatility_like      | mean_reversion_gate |          360 |                 5 |         360 |
| liquidity_like\|volatility_like      | safe_div_abs        |          320 |                 5 |         320 |
| open_interest_like\|positioning_like | delta_x_divergence  |          192 |                 5 |         192 |
| taker_flow_like\|basis_premium_like  | gated_sign          |          192 |                 6 |         192 |
| taker_flow_like\|open_interest_like  | flow_x_leverage     |          192 |                 5 |         192 |
| open_interest_like\|price_like       | mean_reversion_gate |          148 |                 5 |         148 |
| liquidity_like                       | single              |           98 |                 9 |          98 |
| open_interest_like\|price_like       | delta_x_divergence  |           44 |                 5 |          44 |
| taker_flow_like                      | single              |           38 |                 4 |          38 |
| open_interest_like                   | delta_x_divergence  |           20 |                 2 |          20 |
| open_interest_like                   | flow_x_leverage     |           20 |                 2 |          20 |
| open_interest_like                   | single              |           20 |                 5 |          20 |
| volatility_like                      | single              |           14 |                 2 |          14 |
| liquidity_like                       | liquidity_shock     |           10 |                 1 |          10 |
| taker_flow_like                      | flow_x_leverage     |           10 |                 1 |          10 |

## Boundary

```text
gate-native dryrun: true
raw expression construction: false
numeric execution: false
replay executed: false
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```
