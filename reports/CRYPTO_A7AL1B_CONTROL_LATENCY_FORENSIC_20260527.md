# CRYPTO A7AL-1B Control / Latency Forensic

Generated: 2026-05-27T09:27:28Z

## Decision

```text
HOLD_A7AL1B_WRONG_LAG_CONTAMINATION_CONFIRMED
```

This audit does not run formula generation or replay. It interprets A7AL-1 negative controls before any A7AL-2 search contract.

## Manifest

```json
{
  "authorizes_a7al2_formula_search_execution": false,
  "authorizes_alpha_proof": false,
  "authorizes_shadow_paper_live": false,
  "blocking_controls": [
    "wrong_lag_future_24h",
    "wrong_lag_stale_168h"
  ],
  "control_blocked_signal_count": 4,
  "decision": "HOLD_A7AL1B_WRONG_LAG_CONTAMINATION_CONFIRMED",
  "diagnostic_field_families": 4,
  "executes_formula_generation": false,
  "executes_formula_search": false,
  "generated_at": "2026-05-27T09:27:28Z",
  "input_a7al1_decision": "HOLD_A7AL1_CONTROL_CONTAMINATION",
  "recommended_next": "repair A7AL-2 contract to require matched-control dominance; keep slow level fields as regime/state inputs only"
}
```

## Control Blockers

| field_family                   | signal_name       | blocking_controls                         |   max_abs_vs_original_ratio |   max_abs_control_spread |   min_valid_row_share |
|:-------------------------------|:------------------|:------------------------------------------|----------------------------:|-------------------------:|----------------------:|
| liquidity_volume               | trade_count_level | wrong_lag_future_24h                      |                   14.2756   |               0.0148372  |              0.995245 |
| listing_age_latent_interaction | age_x_volatility  | wrong_lag_stale_168h                      |                    0.913341 |               0.00358772 |              0.984706 |
| open_interest                  | oi_level_log      | wrong_lag_stale_168h                      |                    1.39161  |               0.00261308 |              0.986198 |
| price_volatility_interaction   | range_bps         | wrong_lag_future_24h|wrong_lag_stale_168h |                    5.3037   |               0.0167249  |              0.98701  |

## Signal Policy Recommendations

| signal_name                   | field_family                   | diagnostic_decision                     | blocking_controls                         | a7al2_policy            | policy_reason                                                                                                       |
|:------------------------------|:-------------------------------|:----------------------------------------|:------------------------------------------|:------------------------|:--------------------------------------------------------------------------------------------------------------------|
| age_x_volatility              | listing_age_latent_interaction | FIELD_FAMILY_STRUCTURE_FOUND_DIAGNOSTIC | wrong_lag_stale_168h                      | REGIME_OR_STATE_ONLY    | stale wrong-lag control is comparable; use as slow state/neutralization input, not as standalone alpha rank         |
| range_bps                     | price_volatility_interaction   | FIELD_FAMILY_STRUCTURE_FOUND_DIAGNOSTIC | wrong_lag_future_24h|wrong_lag_stale_168h | BLOCK_DIRECT_ALPHA_RANK | future wrong-lag control dominates; keep only for diagnostics until a matched-control dominance gate is implemented |
| lev_high_oi_change_24h        | upper_regime_interaction       | NO_STABLE_FIELD_FAMILY_STRUCTURE        |                                           | DO_NOT_PROMOTE          | no stable neutralized field-family structure                                                                        |
| funding_abs_168h              | funding                        | NO_STABLE_FIELD_FAMILY_STRUCTURE        |                                           | DO_NOT_PROMOTE          | no stable neutralized field-family structure                                                                        |
| trade_count_level             | liquidity_volume               | FIELD_FAMILY_STRUCTURE_FOUND_DIAGNOSTIC | wrong_lag_future_24h                      | BLOCK_DIRECT_ALPHA_RANK | future wrong-lag control dominates; keep only for diagnostics until a matched-control dominance gate is implemented |
| oi_level_log                  | open_interest                  | FIELD_FAMILY_STRUCTURE_FOUND_DIAGNOSTIC | wrong_lag_stale_168h                      | REGIME_OR_STATE_ONLY    | stale wrong-lag control is comparable; use as slow state/neutralization input, not as standalone alpha rank         |
| premium_abs_bps               | premium_basis                  | HOLD_A7AL1_STATE_OR_GROUP_BIAS          |                                           | DO_NOT_PROMOTE          | no stable neutralized field-family structure                                                                        |
| top_position_long_short_level | long_short_positioning         | NO_STABLE_FIELD_FAMILY_STRUCTURE        |                                           | DO_NOT_PROMOTE          | no stable neutralized field-family structure                                                                        |
| taker_buy_sell_level          | taker_buy_sell_volume_ratio    | NO_STABLE_FIELD_FAMILY_STRUCTURE        |                                           | DO_NOT_PROMOTE          | no stable neutralized field-family structure                                                                        |
| oi_change_24h_lv1             | open_interest                  | STAGE1_ONLY_NOT_SHORTLISTED             |                                           | DO_NOT_PROMOTE          | no stable neutralized field-family structure                                                                        |
| oi_value_level_log            | open_interest                  | STAGE1_ONLY_NOT_SHORTLISTED             |                                           | DO_NOT_PROMOTE          | no stable neutralized field-family structure                                                                        |
| oi_x_price_move_24h           | open_interest                  | STAGE1_ONLY_NOT_SHORTLISTED             |                                           | DO_NOT_PROMOTE          | no stable neutralized field-family structure                                                                        |
| global_long_short_level       | long_short_positioning         | STAGE1_ONLY_NOT_SHORTLISTED             |                                           | DO_NOT_PROMOTE          | no stable neutralized field-family structure                                                                        |
| top_account_long_short_level  | long_short_positioning         | STAGE1_ONLY_NOT_SHORTLISTED             |                                           | DO_NOT_PROMOTE          | no stable neutralized field-family structure                                                                        |
| premium_level_bps             | premium_basis                  | STAGE1_ONLY_NOT_SHORTLISTED             |                                           | DO_NOT_PROMOTE          | no stable neutralized field-family structure                                                                        |
| premium_abs_168h              | premium_basis                  | STAGE1_ONLY_NOT_SHORTLISTED             |                                           | DO_NOT_PROMOTE          | no stable neutralized field-family structure                                                                        |
| basis_level_bps               | premium_basis                  | STAGE1_ONLY_NOT_SHORTLISTED             |                                           | DO_NOT_PROMOTE          | no stable neutralized field-family structure                                                                        |
| basis_abs_bps                 | premium_basis                  | STAGE1_ONLY_NOT_SHORTLISTED             |                                           | DO_NOT_PROMOTE          | no stable neutralized field-family structure                                                                        |
| basis_abs_168h                | premium_basis                  | STAGE1_ONLY_NOT_SHORTLISTED             |                                           | DO_NOT_PROMOTE          | no stable neutralized field-family structure                                                                        |
| funding_level                 | funding                        | STAGE1_ONLY_NOT_SHORTLISTED             |                                           | DO_NOT_PROMOTE          | no stable neutralized field-family structure                                                                        |
| funding_abs                   | funding                        | STAGE1_ONLY_NOT_SHORTLISTED             |                                           | DO_NOT_PROMOTE          | no stable neutralized field-family structure                                                                        |
| funding_mean_168h             | funding                        | STAGE1_ONLY_NOT_SHORTLISTED             |                                           | DO_NOT_PROMOTE          | no stable neutralized field-family structure                                                                        |
| ret_x_vol                     | price_volatility_interaction   | STAGE1_ONLY_NOT_SHORTLISTED             |                                           | DO_NOT_PROMOTE          | no stable neutralized field-family structure                                                                        |
| vol_compression               | price_volatility_interaction   | STAGE1_ONLY_NOT_SHORTLISTED             |                                           | DO_NOT_PROMOTE          | no stable neutralized field-family structure                                                                        |
| liquidity_level_log_quote     | liquidity_volume               | STAGE1_ONLY_NOT_SHORTLISTED             |                                           | DO_NOT_PROMOTE          | no stable neutralized field-family structure                                                                        |
| liquidity_log_quote_168h      | liquidity_volume               | STAGE1_ONLY_NOT_SHORTLISTED             |                                           | DO_NOT_PROMOTE          | no stable neutralized field-family structure                                                                        |
| liquidity_rank_active         | liquidity_volume               | STAGE1_ONLY_NOT_SHORTLISTED             |                                           | DO_NOT_PROMOTE          | no stable neutralized field-family structure                                                                        |
| age_x_liquidity               | listing_age_latent_interaction | STAGE1_ONLY_NOT_SHORTLISTED             |                                           | DO_NOT_PROMOTE          | no stable neutralized field-family structure                                                                        |
| age_x_funding_abs             | listing_age_latent_interaction | STAGE1_ONLY_NOT_SHORTLISTED             |                                           | DO_NOT_PROMOTE          | no stable neutralized field-family structure                                                                        |
| basis_high_basis_abs          | upper_regime_interaction       | STAGE1_ONLY_NOT_SHORTLISTED             |                                           | DO_NOT_PROMOTE          | no stable neutralized field-family structure                                                                        |
| liq_contracting_volume_level  | upper_regime_interaction       | STAGE1_ONLY_NOT_SHORTLISTED             |                                           | DO_NOT_PROMOTE          | no stable neutralized field-family structure                                                                        |
| stress_high_low_vol           | upper_regime_interaction       | STAGE1_ONLY_NOT_SHORTLISTED             |                                           | DO_NOT_PROMOTE          | no stable neutralized field-family structure                                                                        |

## Family Policy Summary

| field_family                   |   signals |   diagnostic_pass_signals |   control_blocked_signals |   recommended_direct_alpha |   regime_or_state_only |   blocked_direct_rank |
|:-------------------------------|----------:|--------------------------:|--------------------------:|---------------------------:|-----------------------:|----------------------:|
| funding                        |         4 |                         0 |                         0 |                          0 |                      0 |                     0 |
| liquidity_volume               |         4 |                         1 |                         1 |                          0 |                      0 |                     1 |
| listing_age_latent_interaction |         3 |                         1 |                         1 |                          0 |                      1 |                     0 |
| long_short_positioning         |         3 |                         0 |                         0 |                          0 |                      0 |                     0 |
| open_interest                  |         4 |                         1 |                         1 |                          0 |                      1 |                     0 |
| premium_basis                  |         6 |                         0 |                         0 |                          0 |                      0 |                     0 |
| price_volatility_interaction   |         3 |                         1 |                         1 |                          0 |                      0 |                     1 |
| taker_buy_sell_volume_ratio    |         1 |                         0 |                         0 |                          0 |                      0 |                     0 |
| upper_regime_interaction       |         4 |                         0 |                         0 |                          0 |                      0 |                     0 |

## Boundary

```text
AUTHORIZED:
  A7AL-2 contract repair only.

NOT AUTHORIZED:
  A7AL-2 formula search execution
  alpha proof
  shadow / paper / live
```
