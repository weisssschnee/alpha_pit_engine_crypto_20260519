# CRYPTO A7FF-CORE11E SMALL DRY GENERATION

Generated: 2026-06-01T00:21:33Z

## Decision

`PASS_A7FFCORE11E_BLUEPRINTS_READY_FOR_CORE12_REGISTRATION`

A7FF-CORE11E generates expansion blueprints from replay-clean seeds. New expressions are not materialization-ready until CORE12 registers/gates them.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core12_registration": true,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blueprint_count": 3995,
  "decision": "PASS_A7FFCORE11E_BLUEPRINTS_READY_FOR_CORE12_REGISTRATION",
  "executes_materialization": false,
  "executes_numeric": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T00:21:33Z",
  "motif_bucket_count": 6,
  "next_allowed": "A7FF-CORE12 blueprint subgraph registration / gate audit",
  "parent_seed_count": 23,
  "risk_flags": [],
  "semantic_bucket_count": 8,
  "source_decision": "PASS_A7FFCORE11_SMALL_EXPANSION_CONTRACT_READY_FOR_CORE11E",
  "source_stage": "A7FF-CORE11",
  "stage": "A7FF-CORE11E"
}
```

## Family Generation Summary

| semantic_bucket                      | motif_bucket       | generation_mode        |   candidate_count |
|:-------------------------------------|:-------------------|:-----------------------|------------------:|
| liquidity_like\|volatility_like      | liquidity_shock    | seed_field_mul_delta   |               245 |
| liquidity_like\|volatility_like      | liquidity_shock    | seed_field_rank_spread |               245 |
| liquidity_like\|volatility_like      | liquidity_shock    | seed_field_safe_div    |               245 |
| liquidity_like\|volatility_like      | liquidity_shock    | seed_field_z_add       |               238 |
| liquidity_like\|volatility_like      | liquidity_shock    | seed_field_z_spread    |               238 |
| taker_flow_like\|open_interest_like  | flow_x_leverage    | seed_field_mul_delta   |               140 |
| taker_flow_like\|open_interest_like  | flow_x_leverage    | seed_field_rank_spread |               140 |
| taker_flow_like\|open_interest_like  | flow_x_leverage    | seed_field_z_add       |               140 |
| taker_flow_like\|open_interest_like  | flow_x_leverage    | seed_field_safe_div    |               140 |
| taker_flow_like\|open_interest_like  | flow_x_leverage    | seed_field_z_spread    |               136 |
| open_interest_like                   | single             | seed_field_mul_delta   |               105 |
| open_interest_like                   | single             | seed_field_rank_spread |               105 |
| open_interest_like                   | single             | seed_field_z_add       |               105 |
| open_interest_like                   | single             | seed_field_safe_div    |               105 |
| open_interest_like                   | single             | seed_field_z_spread    |               102 |
| volatility_like                      | single             | seed_field_mul_delta   |                70 |
| volatility_like                      | single             | seed_field_safe_div    |                70 |
| liquidity_like                       | single             | seed_field_rank_spread |                70 |
| liquidity_like                       | single             | seed_field_safe_div    |                70 |
| liquidity_like                       | single             | seed_field_z_add       |                70 |
| liquidity_like                       | single             | seed_field_mul_delta   |                70 |
| volatility_like                      | single             | seed_field_z_add       |                70 |
| volatility_like                      | single             | seed_field_rank_spread |                70 |
| open_interest_like\|positioning_like | delta_x_divergence | seed_field_safe_div    |                70 |
| open_interest_like\|positioning_like | delta_x_divergence | seed_field_rank_spread |                70 |
| open_interest_like\|positioning_like | delta_x_divergence | seed_field_z_add       |                70 |
| open_interest_like\|positioning_like | delta_x_divergence | seed_field_mul_delta   |                70 |
| open_interest_like\|positioning_like | delta_x_divergence | seed_field_z_spread    |                68 |
| liquidity_like                       | single             | seed_field_z_spread    |                68 |
| volatility_like                      | single             | seed_field_z_spread    |                68 |
| liquidity_like\|volatility_like      | safe_div_abs       | seed_field_safe_div    |                35 |
| liquidity_like\|volatility_like      | safe_div_abs       | seed_field_mul_delta   |                35 |
| liquidity_like\|volatility_like      | safe_div_abs       | seed_field_rank_spread |                35 |
| liquidity_like\|volatility_like      | safe_div_abs       | seed_field_z_add       |                35 |
| taker_flow_like                      | single             | seed_field_mul_delta   |                35 |
| taker_flow_like                      | single             | seed_field_rank_spread |                35 |
| taker_flow_like                      | single             | seed_field_safe_div    |                35 |
| taker_flow_like\|basis_premium_like  | gated_sign         | seed_field_safe_div    |                35 |
| taker_flow_like                      | single             | seed_field_z_add       |                35 |
| taker_flow_like\|basis_premium_like  | gated_sign         | seed_field_rank_spread |                35 |
| taker_flow_like\|basis_premium_like  | gated_sign         | seed_field_mul_delta   |                35 |
| taker_flow_like\|basis_premium_like  | gated_sign         | seed_field_z_add       |                35 |
| liquidity_like\|volatility_like      | safe_div_abs       | seed_field_z_spread    |                34 |
| taker_flow_like\|basis_premium_like  | gated_sign         | seed_field_z_spread    |                34 |
| taker_flow_like                      | single             | seed_field_z_spread    |                34 |

## Parent Seed Summary

| parent_candidate_id          |   candidate_count | semantic_bucket                      | motif_bucket       |
|:-----------------------------|------------------:|:-------------------------------------|:-------------------|
| a7ffcore5_24de13cbccf306e9bd |               174 | open_interest_like\|positioning_like | delta_x_divergence |
| a7ffcore5_20349c393fc8912b86 |               174 | taker_flow_like                      | single             |
| a7ffcore5_1f8c481e4c787863b8 |               174 | liquidity_like\|volatility_like      | safe_div_abs       |
| a7ffcore5_89d2049d11221f570d |               174 | volatility_like                      | single             |
| a7ffcore5_74463938d5563b479a |               174 | taker_flow_like\|open_interest_like  | flow_x_leverage    |
| a7ffcore5_6527a26f6a35191da1 |               174 | open_interest_like\|positioning_like | delta_x_divergence |
| a7ffcore5_636578f5c6f8790d3d |               174 | open_interest_like                   | single             |
| a7ffcore5_ff02da2fd4f0d8e0e9 |               174 | open_interest_like                   | single             |
| a7ffcore5_be5c080d95c8a13e44 |               174 | taker_flow_like\|open_interest_like  | flow_x_leverage    |
| a7ffcore5_d495bcdff277541a9d |               174 | open_interest_like                   | single             |
| a7ffcore5_e87b3041b2d66982dc |               174 | taker_flow_like\|open_interest_like  | flow_x_leverage    |
| a7ffcore5_9e4293913b29d39f8d |               174 | liquidity_like                       | single             |
| a7ffcore5_b4246145a5fe0becc1 |               174 | taker_flow_like\|open_interest_like  | flow_x_leverage    |
| a7ffcore5_b594b57d1ee90136c4 |               174 | volatility_like                      | single             |
| a7ffcore5_b9beb4fd43cf7914e2 |               174 | taker_flow_like\|basis_premium_like  | gated_sign         |
| a7ffcore5_f8f5a7d388d98ddbee |               174 | liquidity_like                       | single             |
| a7ffcore5_056264aa1859f3ac7b |               173 | liquidity_like\|volatility_like      | liquidity_shock    |
| a7ffcore5_11903004dcea88bab8 |               173 | liquidity_like\|volatility_like      | liquidity_shock    |
| a7ffcore5_155172eb90a4ffee4e |               173 | liquidity_like\|volatility_like      | liquidity_shock    |
| a7ffcore5_55d479db927df299ef |               173 | liquidity_like\|volatility_like      | liquidity_shock    |
| a7ffcore5_89d456568ed9db84c6 |               173 | liquidity_like\|volatility_like      | liquidity_shock    |
| a7ffcore5_e49456a170f19eb240 |               173 | liquidity_like\|volatility_like      | liquidity_shock    |
| a7ffcore5_f12228440913b31bb1 |               173 | liquidity_like\|volatility_like      | liquidity_shock    |

## Boundary

```text
blueprint generation: true
materialization / numeric / replay execution: false
formula search / large search: false
CORE2 registration required before materialization.
```
