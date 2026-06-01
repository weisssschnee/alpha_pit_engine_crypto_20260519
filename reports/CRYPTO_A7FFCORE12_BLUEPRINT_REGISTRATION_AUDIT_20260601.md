# CRYPTO A7FF-CORE12 BLUEPRINT REGISTRATION AUDIT

Generated: 2026-06-01T00:28:41Z

## Decision

`PASS_A7FFCORE12_TEMP_SUBGRAPH_REGISTRY_READY_FOR_CORE12E`

A7FF-CORE12 parses CORE11E blueprints into a temporary subgraph registry. It does not modify CORE2 registry, materialize formulas, run numeric response, replay, search, promotion, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "approved_temp_subgraph_count": 3995,
  "authorizes_alpha_proof": false,
  "authorizes_core12e": true,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blueprint_count": 3995,
  "decision": "PASS_A7FFCORE12_TEMP_SUBGRAPH_REGISTRY_READY_FOR_CORE12E",
  "executes_materialization": false,
  "executes_numeric": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T00:28:41Z",
  "motif_bucket_count": 6,
  "next_allowed": "A7FF-CORE12E temp-subgraph materialization preflight",
  "parent_seed_count": 23,
  "parse_error_count": 0,
  "rejected_count": 0,
  "risk_flags": [],
  "semantic_bucket_count": 8,
  "source_decision": "PASS_A7FFCORE11E_BLUEPRINTS_READY_FOR_CORE12_REGISTRATION",
  "source_stage": "A7FF-CORE11E",
  "stage": "A7FF-CORE12"
}
```

## Family Summary

| semantic_bucket                      | motif_bucket       |   candidate_count |   parent_count |   generation_mode_count |
|:-------------------------------------|:-------------------|------------------:|---------------:|------------------------:|
| liquidity_like\|volatility_like      | liquidity_shock    |              1211 |              7 |                       5 |
| taker_flow_like\|open_interest_like  | flow_x_leverage    |               696 |              4 |                       5 |
| open_interest_like                   | single             |               522 |              3 |                       5 |
| liquidity_like                       | single             |               348 |              2 |                       5 |
| open_interest_like\|positioning_like | delta_x_divergence |               348 |              2 |                       5 |
| volatility_like                      | single             |               348 |              2 |                       5 |
| liquidity_like\|volatility_like      | safe_div_abs       |               174 |              1 |                       5 |
| taker_flow_like\|basis_premium_like  | gated_sign         |               174 |              1 |                       5 |
| taker_flow_like                      | single             |               174 |              1 |                       5 |

## Operator Summary

| generation_mode        |   candidate_count |   median_node_count |   median_depth |
|:-----------------------|------------------:|--------------------:|---------------:|
| seed_field_mul_delta   |               805 |                  16 |              7 |
| seed_field_rank_spread |               805 |                  15 |              6 |
| seed_field_safe_div    |               805 |                  16 |              6 |
| seed_field_z_add       |               798 |                  17 |              7 |
| seed_field_z_spread    |               782 |                  17 |              7 |

## Boundary

```text
temporary registration audit: true
CORE2 registry modified: false
materialization / numeric / replay / search: false
```
