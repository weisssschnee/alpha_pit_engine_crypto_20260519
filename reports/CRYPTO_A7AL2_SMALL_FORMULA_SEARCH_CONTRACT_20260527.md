# CRYPTO A7AL-2 Small Formula Search Contract

Generated: 2026-05-27T09:28:53Z

## Decision

```text
PASS_A7AL2_CONTROL_DOMINANCE_CONTRACT_DRAFTED_EXECUTION_HOLD
```

This is a contract only. It does not execute formula generation or search.

## Manifest

```json
{
  "allowed_mutation_source_count": 4,
  "authorizes_a7al2_execution": false,
  "authorizes_alpha_proof": false,
  "authorizes_shadow_paper_live": false,
  "blockers_to_execution": [
    "a7al1b_control_latency_hold_requires_contract_repair"
  ],
  "decision": "PASS_A7AL2_CONTROL_DOMINANCE_CONTRACT_DRAFTED_EXECUTION_HOLD",
  "executes_formula_generation": false,
  "executes_formula_search": false,
  "execution_plan": {
    "deep_audit_cap": 32,
    "generated_cap": 5000,
    "latency_policy": "field_native_only; fixed +2h stress prohibited",
    "portfolio_proxy": "top/bottom cross-sectional spread only at contract stage",
    "selector_cap": 512,
    "strict_replay_cap": 128,
    "universe_diagnostic": "U1_listing_aware",
    "universe_primary": "U0_strict_full_history"
  },
  "generated_at": "2026-05-27T09:28:53Z",
  "input_a7al1b_decision": "HOLD_A7AL1B_WRONG_LAG_CONTAMINATION_CONFIRMED"
}
```

## Allowed Feature Roles

| signal_name       | field_family                   | a7al2_role                  | direct_rank_allowed   | mutation_allowed   | required_control                                                |
|:------------------|:-------------------------------|:----------------------------|:----------------------|:-------------------|:----------------------------------------------------------------|
| age_x_volatility  | listing_age_latent_interaction | regime_state_or_neutralizer | False                 | True               | matched wrong_lag_stale_168h dominance                          |
| range_bps         | price_volatility_interaction   | mutation_source_only        | False                 | True               | matched wrong_lag_future_24h and wrong_lag_stale_168h dominance |
| trade_count_level | liquidity_volume               | mutation_source_only        | False                 | True               | matched wrong_lag_future_24h and wrong_lag_stale_168h dominance |
| oi_level_log      | open_interest                  | regime_state_or_neutralizer | False                 | True               | matched wrong_lag_stale_168h dominance                          |

## Matched-Control Plan

| control              | applies_to             | pass_rule                                                                                              |
|:---------------------|:-----------------------|:-------------------------------------------------------------------------------------------------------|
| wrong_lag_future_24h | every selected formula | candidate validation/recent robust score must exceed matched control by margin and same sign stability |
| wrong_lag_stale_168h | every selected formula | candidate must not be return-correlated or score-equivalent to stale control                           |
| time_shuffle         | top replay shortlist   | shuffle score materially weaker than original                                                          |
| symbol_shuffle       | top replay shortlist   | shuffle score materially weaker than original                                                          |
| same_family_random   | per field family       | family placebo must not produce comparable candidate                                                   |

## Input Family Policy Summary

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
  Contract review / selector wiring repair.

NOT AUTHORIZED:
  A7AL-2 formula search execution
  alpha proof
  shadow / paper / live
```
