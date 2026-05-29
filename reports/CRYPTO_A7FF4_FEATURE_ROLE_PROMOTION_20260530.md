# CRYPTO A7FF-4 FIELD-TO-FACTOR COMPILER

Generated: 2026-05-29T16:16:58Z

## Decision

`PASS_A7FF4_ROLE_PROMOTION_MAP_READY`

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "blockers": [],
  "decision": "PASS_A7FF4_ROLE_PROMOTION_MAP_READY",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-29T16:16:58Z",
  "regime_or_interaction_input_count": 14,
  "signal_candidate_count": 1,
  "stage": "A7FF-4"
}
```

## Transition Policy

| new_factor_role                        | transition_reason                           |   field_count |
|:---------------------------------------|:--------------------------------------------|--------------:|
| demote_to_control_like                 | median_control_ratio_ge_1                   |             9 |
| forbidden                              | label_or_future                             |             1 |
| promote_to_regime_or_interaction_input | allowed_pair_policy_but_no_standalone_alpha |            14 |
| promote_to_signal_candidate            | non_l7_control_clean_response_backed        |             1 |
| weak_response_hold                     | insufficient_non_l7_control_clean_evidence  |            56 |

## Promotions

| field_name                           | semantic_type      | compiler_role                | new_factor_role                        | transition_reason                           |   primitive_candidate_count |   non_l7_candidate_count |   median_control_ratio |
|:-------------------------------------|:-------------------|:-----------------------------|:---------------------------------------|:--------------------------------------------|----------------------------:|-------------------------:|-----------------------:|
| global_long_short_account_ratio_last | positioning_like   | risk_exposure_or_neutralizer | promote_to_regime_or_interaction_input | allowed_pair_policy_but_no_standalone_alpha |                           0 |                        0 |                9.71654 |
| mark_index_basis_bps                 | basis_premium_like | signal_seed_candidate        | promote_to_signal_candidate            | non_l7_control_clean_response_backed        |                           2 |                        2 |                2.33917 |
| mark_trade_basis_bps                 | basis_premium_like | regime_or_diagnostic_input   | promote_to_regime_or_interaction_input | allowed_pair_policy_but_no_standalone_alpha |                           0 |                        0 |                1.13586 |
| open_interest_last                   | positioning_like   | risk_exposure_or_neutralizer | promote_to_regime_or_interaction_input | allowed_pair_policy_but_no_standalone_alpha |                           0 |                        0 |                3.68935 |
| open_interest_value_last             | positioning_like   | risk_exposure_or_neutralizer | promote_to_regime_or_interaction_input | allowed_pair_policy_but_no_standalone_alpha |                           0 |                        0 |                5.33155 |
| premium_close_bps                    | basis_premium_like | regime_or_diagnostic_input   | promote_to_regime_or_interaction_input | allowed_pair_policy_but_no_standalone_alpha |                           1 |                        0 |                2.66789 |
| taker_buy_sell_volume_ratio_last     | positioning_like   | regime_or_diagnostic_input   | promote_to_regime_or_interaction_input | allowed_pair_policy_but_no_standalone_alpha |                           0 |                        0 |               16.8931  |
| top_long_short_account_ratio_last    | positioning_like   | risk_exposure_or_neutralizer | promote_to_regime_or_interaction_input | allowed_pair_policy_but_no_standalone_alpha |                           0 |                        0 |                7.54007 |
| top_long_short_position_ratio_last   | positioning_like   | risk_exposure_or_neutralizer | promote_to_regime_or_interaction_input | allowed_pair_policy_but_no_standalone_alpha |                           0 |                        0 |                6.87374 |
| oi_x_price_move_24h                  | positioning_like   | risk_exposure_or_neutralizer | promote_to_regime_or_interaction_input | allowed_pair_policy_but_no_standalone_alpha |                           0 |                        0 |               10.3046  |
| open_interest_change_24h             | positioning_like   | risk_exposure_or_neutralizer | promote_to_regime_or_interaction_input | allowed_pair_policy_but_no_standalone_alpha |                           0 |                        0 |               19.6493  |
| realized_vol_168h                    | volatility_like    | regime_or_diagnostic_input   | promote_to_regime_or_interaction_input | allowed_pair_policy_but_no_standalone_alpha |                           2 |                        0 |               10.571   |
| realized_vol_24h                     | volatility_like    | regime_or_diagnostic_input   | promote_to_regime_or_interaction_input | allowed_pair_policy_but_no_standalone_alpha |                           2 |                        0 |               12.8068  |
| trade_return_1h                      | price_like         | regime_or_diagnostic_input   | promote_to_regime_or_interaction_input | allowed_pair_policy_but_no_standalone_alpha |                           4 |                        0 |                1.35152 |
| trade_return_24h                     | price_like         | risk_exposure_or_neutralizer | promote_to_regime_or_interaction_input | allowed_pair_policy_but_no_standalone_alpha |                           0 |                        0 |               50.6843  |
