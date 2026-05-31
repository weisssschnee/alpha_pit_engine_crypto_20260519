# CRYPTO A7FF-55R3 REPAIRED ATLAS DRY GENERATION

Generated: 2026-05-31T12:00:34Z

## Decision

`PASS_A7FF55R3_REPAIRED_ATLAS_DRY_GENERATION_READY_FOR_COVERAGE_AUDIT`

A7FF-55R3 executes dry generation only. It produces a repaired formula atlas and materialization queue, but does not run numeric evaluation, replay, or search.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_numeric": false,
  "authorizes_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FF55R3_REPAIRED_ATLAS_DRY_GENERATION_READY_FOR_COVERAGE_AUDIT",
  "executes_generation": true,
  "executes_numeric": false,
  "executes_replay": false,
  "executes_search": false,
  "formula_count": 9240,
  "generated_at": "2026-05-31T12:00:34Z",
  "next_allowed": "A7FF-55R4 repaired atlas coverage audit",
  "queue_count": 2400,
  "queue_motif_count": 9,
  "queue_semantic_pair_count": 8,
  "required_pairs_present": [
    "liquidity_like|volatility_like",
    "open_interest_like|positioning_like",
    "taker_flow_like|open_interest_like"
  ],
  "stage": "A7FF-55R3",
  "uses_may": false
}
```

## Formula Family Summary

| semantic_pair                        | motif               |   formula_count |
|:-------------------------------------|:--------------------|----------------:|
| open_interest_like\|price_like       | smooth_mul          |             450 |
| open_interest_like\|price_like       | mean_reversion_gate |             450 |
| open_interest_like\|price_like       | delta_x_divergence  |             450 |
| taker_flow_like\|basis_premium_like  | safe_div_abs        |             450 |
| taker_flow_like\|basis_premium_like  | smooth_mul          |             450 |
| taker_flow_like\|basis_premium_like  | gated_sign          |             450 |
| taker_flow_like\|basis_premium_like  | relative_shock      |             450 |
| open_interest_like\|price_like       | spread_rank         |             450 |
| liquidity_like\|volatility_like      | liquidity_shock     |             360 |
| liquidity_like\|volatility_like      | mean_reversion_gate |             360 |
| liquidity_like\|volatility_like      | safe_div_abs        |             360 |
| taker_flow_like\|open_interest_like  | relative_shock      |             360 |
| open_interest_like\|positioning_like | spread_rank         |             360 |
| open_interest_like\|positioning_like | safe_div_abs        |             360 |
| open_interest_like\|positioning_like | smooth_mul          |             360 |
| open_interest_like\|positioning_like | delta_x_divergence  |             360 |
| liquidity_like\|volatility_like      | spread_rank         |             360 |
| liquidity_like\|volatility_like      | smooth_mul          |             360 |
| open_interest_like\|positioning_like | signed_spread       |             360 |
| taker_flow_like\|open_interest_like  | smooth_mul          |             360 |
| taker_flow_like\|open_interest_like  | safe_div_abs        |             360 |
| taker_flow_like\|open_interest_like  | flow_x_leverage     |             360 |
| taker_flow_like\|open_interest_like  | gated_sign          |             360 |
| liquidity_like                       | single              |             108 |
| open_interest_like                   | single              |              60 |
| taker_flow_like                      | single              |              48 |
| volatility_like                      | single              |              24 |

## Queue Summary

| semantic_pair                        | motif               |   queue_count |
|:-------------------------------------|:--------------------|--------------:|
| liquidity_like\|volatility_like      | liquidity_shock     |           308 |
| open_interest_like\|positioning_like | delta_x_divergence  |           308 |
| taker_flow_like\|open_interest_like  | flow_x_leverage     |           308 |
| open_interest_like\|positioning_like | safe_div_abs        |           292 |
| liquidity_like\|volatility_like      | mean_reversion_gate |           292 |
| open_interest_like\|price_like       | mean_reversion_gate |           174 |
| taker_flow_like\|open_interest_like  | relative_shock      |           169 |
| open_interest_like\|price_like       | delta_x_divergence  |           163 |
| taker_flow_like\|open_interest_like  | gated_sign          |           123 |
| liquidity_like                       | single              |           108 |
| open_interest_like\|price_like       | smooth_mul          |           103 |
| open_interest_like                   | single              |            28 |
| taker_flow_like                      | single              |            16 |
| volatility_like                      | single              |             8 |

## Boundary

```text
dry generation executed: true
numeric execution: false
replay executed: false
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```
