# CRYPTO A7FF-3 FIELD-TO-FACTOR COMPILER

Generated: 2026-05-29T16:16:58Z

## Decision

`PASS_A7FF3_COARSE_TO_FINE_BLUEPRINTS_READY`

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "blockers": [],
  "blueprint_count": 16,
  "decision": "PASS_A7FF3_COARSE_TO_FINE_BLUEPRINTS_READY",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-29T16:16:58Z",
  "layer_count": 2,
  "stage": "A7FF-3"
}
```

## Blueprints

| blueprint_id           | layer                          | primary_field        | secondary_field                      | operator          | semantic_type                          | pair_policy                          | status            |
|:-----------------------|:-------------------------------|:---------------------|:-------------------------------------|:------------------|:---------------------------------------|:-------------------------------------|:------------------|
| a7ff3_52a424927039bc9a | F1_single_field_transform      | mark_index_basis_bps |                                      | Delta             | basis_premium_like                     |                                      | allowed_blueprint |
| a7ff3_8d8da05459cdc63b | F2_typed_two_field_interaction | mark_index_basis_bps | funding_rate                         | Mul\|Sub\|SafeDiv | basis_premium_like\|rate_like          | cross_cluster_high_prior_interaction | allowed_blueprint |
| a7ff3_b6b90fa62c5e380e | F2_typed_two_field_interaction | mark_index_basis_bps | funding_rate_abs_168h                | Mul\|Sub\|SafeDiv | basis_premium_like\|rate_like          | cross_cluster_high_prior_interaction | allowed_blueprint |
| a7ff3_a8dc0fc50702f65b | F2_typed_two_field_interaction | mark_index_basis_bps | funding_rate_mean_168h               | Mul\|Sub\|SafeDiv | basis_premium_like\|rate_like          | cross_cluster_high_prior_interaction | allowed_blueprint |
| a7ff3_18a60aea9a31bed9 | F2_typed_two_field_interaction | mark_index_basis_bps | global_long_short_account_ratio_last | Mul\|Sub\|SafeDiv | basis_premium_like\|positioning_like   | cross_cluster_high_prior_interaction | allowed_blueprint |
| a7ff3_799fb499d3b3d318 | F2_typed_two_field_interaction | mark_index_basis_bps | mark_trade_basis_bps                 | Mul\|Sub\|SafeDiv | basis_premium_like\|basis_premium_like | within_cluster_refinement            | allowed_blueprint |
| a7ff3_2e2b9645c81374ae | F2_typed_two_field_interaction | mark_index_basis_bps | oi_x_price_move_24h                  | Mul\|Sub\|SafeDiv | basis_premium_like\|positioning_like   | cross_cluster_high_prior_interaction | allowed_blueprint |
| a7ff3_0304c7028aa7ebc5 | F2_typed_two_field_interaction | mark_index_basis_bps | open_interest_change_24h             | Mul\|Sub\|SafeDiv | basis_premium_like\|positioning_like   | cross_cluster_high_prior_interaction | allowed_blueprint |
| a7ff3_899a457e28f528d4 | F2_typed_two_field_interaction | mark_index_basis_bps | open_interest_last                   | Mul\|Sub\|SafeDiv | basis_premium_like\|positioning_like   | cross_cluster_high_prior_interaction | allowed_blueprint |
| a7ff3_b30254a2254b52b6 | F2_typed_two_field_interaction | mark_index_basis_bps | open_interest_value_last             | Mul\|Sub\|SafeDiv | basis_premium_like\|positioning_like   | cross_cluster_high_prior_interaction | allowed_blueprint |
| a7ff3_0bf274f3cdb3af2c | F2_typed_two_field_interaction | mark_index_basis_bps | premium_close_bps                    | Mul\|Sub\|SafeDiv | basis_premium_like\|basis_premium_like | within_cluster_refinement            | allowed_blueprint |
| a7ff3_ce4dad588617e535 | F2_typed_two_field_interaction | mark_index_basis_bps | realized_vol_168h                    | Mul\|Sub\|SafeDiv | basis_premium_like\|volatility_like    | cross_cluster_high_prior_interaction | allowed_blueprint |
| a7ff3_338c80f2bd076462 | F2_typed_two_field_interaction | mark_index_basis_bps | realized_vol_24h                     | Mul\|Sub\|SafeDiv | basis_premium_like\|volatility_like    | cross_cluster_high_prior_interaction | allowed_blueprint |
| a7ff3_5395d7b8567bf996 | F2_typed_two_field_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last     | Mul\|Sub\|SafeDiv | basis_premium_like\|positioning_like   | cross_cluster_high_prior_interaction | allowed_blueprint |
| a7ff3_cc70ac4a170dea77 | F2_typed_two_field_interaction | mark_index_basis_bps | top_long_short_account_ratio_last    | Mul\|Sub\|SafeDiv | basis_premium_like\|positioning_like   | cross_cluster_high_prior_interaction | allowed_blueprint |
| a7ff3_1a0c21ed45ef74b0 | F2_typed_two_field_interaction | mark_index_basis_bps | top_long_short_position_ratio_last   | Mul\|Sub\|SafeDiv | basis_premium_like\|positioning_like   | cross_cluster_high_prior_interaction | allowed_blueprint |

## Layer Policy

```json
{
  "F1_single_field_transform": {
    "allowed": true,
    "requires": [
      "field_ontology",
      "operator_probe_allowed",
      "non_l7_response_evidence"
    ]
  },
  "F2_typed_two_field_interaction": {
    "allowed": true,
    "requires": [
      "one_promoted_signal_seed",
      "allowed_feature_pair_policy",
      "controls_attached"
    ]
  },
  "F3_state_conditioned_or_neutralized": {
    "allowed": "contract_only",
    "requires": [
      "frozen_regime_state",
      "neutralization_policy",
      "no_label_or_future_state"
    ]
  },
  "F4_portfolio_candidate": {
    "allowed": "not_yet",
    "requires": [
      "numeric_replay",
      "marginal_contribution",
      "cluster_registry"
    ]
  }
}
```
