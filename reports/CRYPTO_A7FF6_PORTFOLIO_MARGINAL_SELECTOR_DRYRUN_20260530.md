# CRYPTO A7FF-6 FIELD-TO-FACTOR COMPILER

Generated: 2026-05-29T16:16:58Z

## Decision

`HOLD_A7FF6_PORTFOLIO_MARGINAL_DRYRUN_NOT_PROMOTABLE`

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "portfolio_marginal_reward_requires_numeric_replay"
  ],
  "decision": "HOLD_A7FF6_PORTFOLIO_MARGINAL_DRYRUN_NOT_PROMOTABLE",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-29T16:16:58Z",
  "queue_count": 13,
  "selected_count": 4,
  "stage": "A7FF-6",
  "uses_may": false
}
```

## Portfolio Marginal Queue

| factor_blueprint_id    | layer                          | primary_field        | secondary_field                      | factor_family                          |   marginal_proxy_no_may |   cluster_novelty_proxy | requires_numeric_replay   | selected_for_future_numeric_probe   |
|:-----------------------|:-------------------------------|:---------------------|:-------------------------------------|:---------------------------------------|------------------------:|------------------------:|:--------------------------|:------------------------------------|
| a7ff5_0459bb72908046d2 | F2_typed_two_field_interaction | mark_index_basis_bps | global_long_short_account_ratio_last | basis_premium_like\|positioning_like   |                    3    |                    1    | True                      | True                                |
| a7ff5_2d39dca31628eecf | F2_typed_two_field_interaction | mark_index_basis_bps | top_long_short_account_ratio_last    | basis_premium_like\|positioning_like   |                    3    |                    1    | True                      | False                               |
| a7ff5_346ec9dc5357c80d | F2_typed_two_field_interaction | mark_index_basis_bps | top_long_short_position_ratio_last   | basis_premium_like\|positioning_like   |                    3    |                    1    | True                      | False                               |
| a7ff5_364a8a6521477d81 | F2_typed_two_field_interaction | mark_index_basis_bps | open_interest_change_24h             | basis_premium_like\|positioning_like   |                    3    |                    1    | True                      | False                               |
| a7ff5_45b37ccd842aa212 | F2_typed_two_field_interaction | mark_index_basis_bps | mark_trade_basis_bps                 | basis_premium_like\|basis_premium_like |                    3    |                    1    | True                      | True                                |
| a7ff5_492574cf6aa8db51 | F2_typed_two_field_interaction | mark_index_basis_bps | open_interest_value_last             | basis_premium_like\|positioning_like   |                    3    |                    1    | True                      | False                               |
| a7ff5_4d9456342ef352f8 | F2_typed_two_field_interaction | mark_index_basis_bps | open_interest_last                   | basis_premium_like\|positioning_like   |                    3    |                    1    | True                      | False                               |
| a7ff5_6b187cb748d3fd22 | F2_typed_two_field_interaction | mark_index_basis_bps | premium_close_bps                    | basis_premium_like\|basis_premium_like |                    3    |                    1    | True                      | False                               |
| a7ff5_ca01cf453210eced | F2_typed_two_field_interaction | mark_index_basis_bps | realized_vol_168h                    | basis_premium_like\|volatility_like    |                    3    |                    1    | True                      | True                                |
| a7ff5_cef19ce298e669ae | F2_typed_two_field_interaction | mark_index_basis_bps | oi_x_price_move_24h                  | basis_premium_like\|positioning_like   |                    3    |                    1    | True                      | False                               |
| a7ff5_d56c5df1f1997a4c | F2_typed_two_field_interaction | mark_index_basis_bps | realized_vol_24h                     | basis_premium_like\|volatility_like    |                    3    |                    1    | True                      | False                               |
| a7ff5_dfebdab50b31975e | F2_typed_two_field_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last     | basis_premium_like\|positioning_like   |                    3    |                    1    | True                      | False                               |
| a7ff5_449ce14bfd93ebc1 | F1_single_field_transform      | mark_index_basis_bps |                                      | basis_premium_like                     |                    2.25 |                    0.25 | True                      | True                                |

## Selected Dryrun Queue

| factor_blueprint_id    | layer                          | primary_field        | secondary_field                      | factor_family                          |   marginal_proxy_no_may |   cluster_novelty_proxy | requires_numeric_replay   | selected_for_future_numeric_probe   |
|:-----------------------|:-------------------------------|:---------------------|:-------------------------------------|:---------------------------------------|------------------------:|------------------------:|:--------------------------|:------------------------------------|
| a7ff5_0459bb72908046d2 | F2_typed_two_field_interaction | mark_index_basis_bps | global_long_short_account_ratio_last | basis_premium_like\|positioning_like   |                    3    |                    1    | True                      | True                                |
| a7ff5_45b37ccd842aa212 | F2_typed_two_field_interaction | mark_index_basis_bps | mark_trade_basis_bps                 | basis_premium_like\|basis_premium_like |                    3    |                    1    | True                      | True                                |
| a7ff5_ca01cf453210eced | F2_typed_two_field_interaction | mark_index_basis_bps | realized_vol_168h                    | basis_premium_like\|volatility_like    |                    3    |                    1    | True                      | True                                |
| a7ff5_449ce14bfd93ebc1 | F1_single_field_transform      | mark_index_basis_bps |                                      | basis_premium_like                     |                    2.25 |                    0.25 | True                      | True                                |

## Boundary

No numeric replay was executed. Portfolio marginal reward remains a dry proxy and cannot authorize search.
