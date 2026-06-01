# CRYPTO A7FF-CORE12E MATERIALIZATION PREFLIGHT

Generated: 2026-06-01T01:45:14Z

## Decision

`PASS_A7FFCORE12E_MATERIALIZATION_PREFLIGHT_READY_FOR_CORE13`

A7FF-CORE12E materializes a 512-row temp-subgraph sample. It does not run numeric response, replay, search, promotion, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core13": true,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FFCORE12E_MATERIALIZATION_PREFLIGHT_READY_FOR_CORE13",
  "eval_error_count": 0,
  "executes_materialization": true,
  "executes_numeric": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T01:45:14Z",
  "low_activity_count": 0,
  "next_allowed": "A7FF-CORE13 numeric response contract",
  "ok_count": 416,
  "queue_count": 416,
  "source_decision": "PASS_A7FFCORE12_TEMP_SUBGRAPH_REGISTRY_READY_FOR_CORE12E",
  "source_stage": "A7FF-CORE12",
  "stage": "A7FF-CORE12E"
}
```

## Materialization Summary

| semantic_bucket                      | motif_bucket       | generation_mode        |   candidate_count |   ok_count |   eval_error_count |   median_non_null_ratio |   median_active_ratio |
|:-------------------------------------|:-------------------|:-----------------------|------------------:|-----------:|-------------------:|------------------------:|----------------------:|
| liquidity_like\|volatility_like      | liquidity_shock    | seed_field_mul_delta   |                80 |         80 |                  0 |                0.996417 |              0.995795 |
| taker_flow_like\|open_interest_like  | flow_x_leverage    | seed_field_mul_delta   |                80 |         80 |                  0 |                0.995891 |              0.995766 |
| liquidity_like                       | single             | seed_field_mul_delta   |                70 |         70 |                  0 |                0.973271 |              0.972679 |
| open_interest_like\|positioning_like | delta_x_divergence | seed_field_mul_delta   |                70 |         70 |                  0 |                0.996217 |              0.995982 |
| taker_flow_like\|basis_premium_like  | gated_sign         | seed_field_mul_delta   |                35 |         35 |                  0 |                0.997309 |              0.997167 |
| taker_flow_like\|basis_premium_like  | gated_sign         | seed_field_rank_spread |                35 |         35 |                  0 |                0.99738  |              0.949834 |
| open_interest_like                   | single             | seed_field_mul_delta   |                16 |         16 |                  0 |                0.971113 |              0.970426 |
| liquidity_like                       | single             | seed_field_rank_spread |                10 |         10 |                  0 |                0.975887 |              0.564121 |
| open_interest_like\|positioning_like | delta_x_divergence | seed_field_rank_spread |                10 |         10 |                  0 |                0.996529 |              0.839443 |
| taker_flow_like\|basis_premium_like  | gated_sign         | seed_field_safe_div    |                10 |         10 |                  0 |                0.995588 |              0.993354 |

## Error Summary

`<empty>`
