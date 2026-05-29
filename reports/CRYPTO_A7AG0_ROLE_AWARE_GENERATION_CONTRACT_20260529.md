# CRYPTO A7AG-0 ROLE-AWARE GENERATION CONTRACT

Generated: 2026-05-29T08:22:01Z

## Decision

`PASS_A7AG0_ROLE_AWARE_GENERATION_CONTRACT_READY_FOR_A7AG1_BLUEPRINT_DRYRUN`

A7AG-0 defines a role-aware generation contract from the A7AF selector queue. It does not generate formulas, run numeric replay, search, train, or authorize proof.

## Manifest

```json
{
  "authorizes_a7ag1_static_blueprint_dryrun": true,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search_execution": false,
  "authorizes_large_search": false,
  "authorizes_numeric_replay": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7AG0_ROLE_AWARE_GENERATION_CONTRACT_READY_FOR_A7AG1_BLUEPRINT_DRYRUN",
  "executes_contract_only": true,
  "executes_formula_search": false,
  "executes_numeric_replay": false,
  "executes_static_blueprint_generation": false,
  "executes_training": false,
  "generated_at": "2026-05-29T08:22:01Z",
  "selected_queue_rows": 18,
  "source_a7af1_decision": "PASS_A7AF1_ROLE_AWARE_SELECTOR_DRYRUN_READY_FOR_A7AG0_CONTRACT",
  "stage": "A7AG-0",
  "track_count": 3,
  "uses_may": false
}
```

## Generation Tracks

| track_id                        | source_selector_tier             | status        | primary_fields                                                                             | allowed_labels                                                                             | allowed_transforms                        | allowed_interactions                                                                                | forbidden                                                                                                | max_static_blueprints   | authorizes_execution   |
|:--------------------------------|:---------------------------------|:--------------|:-------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------|:------------------------------------------|:----------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------|:------------------------|:-----------------------|
| G0_ordinary_alpha_basis_premium | T0_raw_relative_alpha            | contract_only | mark_index_basis_bps                                                                       | L0_raw_forward_return\|L1_cross_sectional_relative_return\|L5_vol_adjusted_return          | level\|delta_24h\|cs_rank\|clip\|winsor   | basis_delta_x_vol_state\|basis_delta_x_liquidity_tier\|basis_delta_x_market_breadth                 | funding_only_wrapper\|liquidity_volatility_old_family\|direct_raw_okx_binance_price_comparison\|May_mask | 128                     | False                  |
| G1_neutralized_alpha_diagnostic | T1_beta_neutral_alpha_diagnostic | contract_only | trade_return_1h\|liquidity_rank_active_universe\|premium_close_bps                         | L2_BTC_ETH_beta_residual_return\|L3_liquidity_tier_relative_return\|L5_vol_adjusted_return | level\|delta_24h\|cs_rank\|ts_zscore_168h | price_reversal_x_liquidity_rank\|premium_delta_x_vol_adjusted\|liquidity_rank_x_major_beta_residual | ordinary_alpha_promotion_without_L0_L1_translation\|May_mask\|full_open_grammar                          | 192                     | False                  |
| G2_downside_risk_defense        | T2_downside_risk_defense         | contract_only | trade_count\|realized_vol_24h\|open_interest_last\|oi_x_price_move_24h\|positioning_ratios | L6_downside_avoidance                                                                      | level\|delta_24h\|cs_rank\|ts_zscore_168h | risk_state_x_positioning_delta\|vol_state_x_trade_count\|oi_price_move_x_downside_state             | ordinary_alpha_promotion\|rank_label_only_promotion\|May_mask\|large_search                              | 256                     | False                  |

## Source Queue Summary

| selector_tier                    | selected   | unique_fields   | unique_families   | max_control_ratio   | min_robust_tstat_floor   |
|:---------------------------------|:-----------|:----------------|:------------------|:--------------------|:-------------------------|
| T0_raw_relative_alpha            | 3          | 1               | 1                 | 0.8310629993440081  | 4.098221868779841        |
| T1_beta_neutral_alpha_diagnostic | 6          | 3               | 3                 | 0.986634721522299   | 1.1818188186115688       |
| T2_downside_risk_defense         | 9          | 5               | 4                 | 0.8733738051380588  | 2.334510991572852        |

## Track Rules

| rule                     | detail                                                                                      |
|:-------------------------|:--------------------------------------------------------------------------------------------|
| source_queue_only        | A7AG inputs must come from A7AF1 selected queue                                             |
| role_label_alignment     | track labels must match selector tier role                                                  |
| no_cross_track_promotion | downside/risk-defense results cannot count as ordinary alpha                                |
| control_first            | matched wrong-lag/stale/random controls must be attached before any numeric replay contract |
| latency_native           | same-bar field-native timing policy remains; no artificial +2h stress                       |
| no_may                   | May not used in generation, selector score, threshold, mutation, or authorization           |
| no_full_grammar          | FormulaGenV2 open grammar remains disabled; only typed role-aware blueprints allowed        |

## Blueprint Budget

```json
{
  "a7ag1_executes_formula_search": false,
  "a7ag1_executes_numeric_replay": false,
  "a7ag1_static_blueprint_dryrun_authorized": true,
  "combined_max_static_blueprints": 576,
  "g0_max_static_blueprints": 128,
  "g1_max_static_blueprints": 192,
  "g2_max_static_blueprints": 256,
  "numeric_replay_after_a7ag1": "requires_separate_A7AG2_contract"
}
```

## Boundary

```text
A7AG-0 only authorizes A7AG-1 static blueprint dryrun.
Numeric replay and formula search execution remain not authorized.
Downside/risk-defense remains separate from ordinary alpha.
May is not used.
```
