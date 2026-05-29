# CRYPTO A7FF-5 FIELD-TO-FACTOR COMPILER

Generated: 2026-05-29T16:16:58Z

## Decision

`PASS_A7FF5_FACTOR_BLUEPRINTS_READY_FOR_PORTFOLIO_DRYRUN`

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "blockers": [],
  "compiled_blueprint_count": 13,
  "compiled_factor_family_count": 4,
  "decision": "PASS_A7FF5_FACTOR_BLUEPRINTS_READY_FOR_PORTFOLIO_DRYRUN",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-29T16:16:58Z",
  "stage": "A7FF-5"
}
```

## Compiled Factor Blueprints

| factor_blueprint_id    | source_blueprint_id    | layer                          | primary_field        | secondary_field                      | operator          | pair_policy                          | factor_family                          | status                    |
|:-----------------------|:-----------------------|:-------------------------------|:---------------------|:-------------------------------------|:------------------|:-------------------------------------|:---------------------------------------|:--------------------------|
| a7ff5_449ce14bfd93ebc1 | a7ff3_52a424927039bc9a | F1_single_field_transform      | mark_index_basis_bps |                                      | Delta             |                                      | basis_premium_like                     | compiled_factor_blueprint |
| a7ff5_0459bb72908046d2 | a7ff3_18a60aea9a31bed9 | F2_typed_two_field_interaction | mark_index_basis_bps | global_long_short_account_ratio_last | Mul\|Sub\|SafeDiv | cross_cluster_high_prior_interaction | basis_premium_like\|positioning_like   | compiled_factor_blueprint |
| a7ff5_45b37ccd842aa212 | a7ff3_799fb499d3b3d318 | F2_typed_two_field_interaction | mark_index_basis_bps | mark_trade_basis_bps                 | Mul\|Sub\|SafeDiv | within_cluster_refinement            | basis_premium_like\|basis_premium_like | compiled_factor_blueprint |
| a7ff5_cef19ce298e669ae | a7ff3_2e2b9645c81374ae | F2_typed_two_field_interaction | mark_index_basis_bps | oi_x_price_move_24h                  | Mul\|Sub\|SafeDiv | cross_cluster_high_prior_interaction | basis_premium_like\|positioning_like   | compiled_factor_blueprint |
| a7ff5_364a8a6521477d81 | a7ff3_0304c7028aa7ebc5 | F2_typed_two_field_interaction | mark_index_basis_bps | open_interest_change_24h             | Mul\|Sub\|SafeDiv | cross_cluster_high_prior_interaction | basis_premium_like\|positioning_like   | compiled_factor_blueprint |
| a7ff5_4d9456342ef352f8 | a7ff3_899a457e28f528d4 | F2_typed_two_field_interaction | mark_index_basis_bps | open_interest_last                   | Mul\|Sub\|SafeDiv | cross_cluster_high_prior_interaction | basis_premium_like\|positioning_like   | compiled_factor_blueprint |
| a7ff5_492574cf6aa8db51 | a7ff3_b30254a2254b52b6 | F2_typed_two_field_interaction | mark_index_basis_bps | open_interest_value_last             | Mul\|Sub\|SafeDiv | cross_cluster_high_prior_interaction | basis_premium_like\|positioning_like   | compiled_factor_blueprint |
| a7ff5_6b187cb748d3fd22 | a7ff3_0bf274f3cdb3af2c | F2_typed_two_field_interaction | mark_index_basis_bps | premium_close_bps                    | Mul\|Sub\|SafeDiv | within_cluster_refinement            | basis_premium_like\|basis_premium_like | compiled_factor_blueprint |
| a7ff5_ca01cf453210eced | a7ff3_ce4dad588617e535 | F2_typed_two_field_interaction | mark_index_basis_bps | realized_vol_168h                    | Mul\|Sub\|SafeDiv | cross_cluster_high_prior_interaction | basis_premium_like\|volatility_like    | compiled_factor_blueprint |
| a7ff5_d56c5df1f1997a4c | a7ff3_338c80f2bd076462 | F2_typed_two_field_interaction | mark_index_basis_bps | realized_vol_24h                     | Mul\|Sub\|SafeDiv | cross_cluster_high_prior_interaction | basis_premium_like\|volatility_like    | compiled_factor_blueprint |
| a7ff5_dfebdab50b31975e | a7ff3_5395d7b8567bf996 | F2_typed_two_field_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last     | Mul\|Sub\|SafeDiv | cross_cluster_high_prior_interaction | basis_premium_like\|positioning_like   | compiled_factor_blueprint |
| a7ff5_2d39dca31628eecf | a7ff3_cc70ac4a170dea77 | F2_typed_two_field_interaction | mark_index_basis_bps | top_long_short_account_ratio_last    | Mul\|Sub\|SafeDiv | cross_cluster_high_prior_interaction | basis_premium_like\|positioning_like   | compiled_factor_blueprint |
| a7ff5_346ec9dc5357c80d | a7ff3_1a0c21ed45ef74b0 | F2_typed_two_field_interaction | mark_index_basis_bps | top_long_short_position_ratio_last   | Mul\|Sub\|SafeDiv | cross_cluster_high_prior_interaction | basis_premium_like\|positioning_like   | compiled_factor_blueprint |

## Blocked Factor Blueprints

| factor_blueprint_id    | source_blueprint_id    | layer                          | primary_field        | secondary_field        | operator          | pair_policy                          | factor_family                 | status              |
|:-----------------------|:-----------------------|:-------------------------------|:---------------------|:-----------------------|:------------------|:-------------------------------------|:------------------------------|:--------------------|
| a7ff5_219c8da59dadee37 | a7ff3_8d8da05459cdc63b | F2_typed_two_field_interaction | mark_index_basis_bps | funding_rate           | Mul\|Sub\|SafeDiv | cross_cluster_high_prior_interaction | basis_premium_like\|rate_like | blocked_role_policy |
| a7ff5_1237bcdf3f98acfe | a7ff3_b6b90fa62c5e380e | F2_typed_two_field_interaction | mark_index_basis_bps | funding_rate_abs_168h  | Mul\|Sub\|SafeDiv | cross_cluster_high_prior_interaction | basis_premium_like\|rate_like | blocked_role_policy |
| a7ff5_f8feee95dfddec12 | a7ff3_a8dc0fc50702f65b | F2_typed_two_field_interaction | mark_index_basis_bps | funding_rate_mean_168h | Mul\|Sub\|SafeDiv | cross_cluster_high_prior_interaction | basis_premium_like\|rate_like | blocked_role_policy |
