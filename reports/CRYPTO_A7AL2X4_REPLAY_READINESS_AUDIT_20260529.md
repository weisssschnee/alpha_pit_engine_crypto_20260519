# CRYPTO A7AL-2X4 Replay Readiness Audit

Generated: 2026-05-29T00:09:47Z

## Decision

```text
HOLD_A7AL2X4_REPLAY_PREFLIGHT_NOT_READY_MATERIALIZATION_REQUIRED
```

This stage audits whether the A7AL-2X3 family-balanced selected queue can be evaluated by the existing fast replay engine. It executes no numeric replay, no generation, no training, and no search.

## Manifest

```json
{
  "authorizes_a7al2y_generation": false,
  "authorizes_alpha_proof": false,
  "authorizes_large_search": false,
  "authorizes_numeric_replay_preflight": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "state_or_derived_fields_not_materialized_for_fast_replay",
    "operators_not_supported_by_existing_fast_replay"
  ],
  "blocking_field_count": 7,
  "blocking_operator_count": 4,
  "decision": "HOLD_A7AL2X4_REPLAY_PREFLIGHT_NOT_READY_MATERIALIZATION_REQUIRED",
  "executes_generation": false,
  "executes_replay": false,
  "executes_search": false,
  "executes_training": false,
  "field_count": 13,
  "generated_at": "2026-05-29T00:09:47Z",
  "operator_count": 14,
  "selected_candidate_count": 176
}
```

## Family Readiness

| objective_family                   |   selected_count |   unique_fields |   unique_ops | blocking_fields                                                                                                   | blocking_operators         | ready_for_current_fast_replay   |
|:-----------------------------------|-----------------:|----------------:|-------------:|:------------------------------------------------------------------------------------------------------------------|:---------------------------|:--------------------------------|
| F0_OI_delta_price_interaction      |               32 |               2 |            8 |                                                                                                                   | Winsor                     | False                           |
| F1_OI_basis_premium_interaction    |               24 |               2 |           10 |                                                                                                                   | Clip                       | False                           |
| F2_OI_funding_crowding_interaction |               24 |               2 |           11 | funding_rate_abs_168h                                                                                             | Clip                       | False                           |
| F3_positioning_divergence          |               24 |               3 |            7 |                                                                                                                   |                            | True                            |
| F4_OI_taker_flow_interaction       |               24 |               2 |           10 |                                                                                                                   | Clip                       | False                           |
| F5_OI_upper_regime_interaction     |               24 |               5 |            3 | R2_market_breadth_state\|R3_liquidity_cycle_state\|R4_leverage_crowding_state\|R5_basis_premium_dislocation_state | GroupNeutralize            | False                           |
| F6_OI_latent_state_interaction     |               24 |               3 |            7 | is_major\|liquidity_tier                                                                                          | GroupNeutralize\|StateMask | False                           |

## Field Materialization Audit

| field_name                           | status                                   | source                | in_base_panel_schema   | blocking_for_current_fast_replay   |
|:-------------------------------------|:-----------------------------------------|:----------------------|:-----------------------|:-----------------------------------|
| R2_market_breadth_state              | requires_upper_regime_materialization    | a7al0g_upper_regime   | False                  | True                               |
| R3_liquidity_cycle_state             | requires_upper_regime_materialization    | a7al0g_upper_regime   | False                  | True                               |
| R4_leverage_crowding_state           | requires_upper_regime_materialization    | a7al0g_upper_regime   | False                  | True                               |
| R5_basis_premium_dislocation_state   | requires_upper_regime_materialization    | a7al0g_upper_regime   | False                  | True                               |
| funding_rate_abs_168h                | requires_derived_feature_materialization | a7ak_lv1_derived      | False                  | True                               |
| global_long_short_account_ratio_last | ready_in_base_panel                      | base_panel            | True                   | False                              |
| index_close                          | ready_in_base_panel                      | base_panel            | True                   | False                              |
| is_major                             | unknown_missing_field                    | unknown               | False                  | True                               |
| kline_taker_buy_quote_share          | ready_in_base_panel                      | base_panel            | True                   | False                              |
| liquidity_tier                       | requires_latent_taxonomy_materialization | a7ak_lv/a7ak_taxonomy | False                  | True                               |
| mark_index_basis_bps                 | ready_in_base_panel                      | base_panel            | True                   | False                              |
| open_interest_last                   | ready_in_base_panel                      | base_panel            | True                   | False                              |
| top_long_short_account_ratio_last    | ready_in_base_panel                      | base_panel            | True                   | False                              |

## Operator Support Audit

| operator        | status                                | blocking_for_current_fast_replay   |
|:----------------|:--------------------------------------|:-----------------------------------|
| Abs             | ready_in_existing_fast_evaluator      | False                              |
| Add             | ready_in_existing_fast_evaluator      | False                              |
| Clip            | needs_small_evaluator_extension       | True                               |
| Delta           | ready_in_existing_fast_evaluator      | False                              |
| GroupNeutralize | needs_state_aware_evaluator_extension | True                               |
| Mean            | ready_in_existing_fast_evaluator      | False                              |
| Mul             | ready_in_existing_fast_evaluator      | False                              |
| Neg             | ready_in_existing_fast_evaluator      | False                              |
| Rank            | ready_in_existing_fast_evaluator      | False                              |
| Sign            | ready_in_existing_fast_evaluator      | False                              |
| StateMask       | needs_state_aware_evaluator_extension | True                               |
| Sub             | ready_in_existing_fast_evaluator      | False                              |
| Winsor          | needs_small_evaluator_extension       | True                               |
| ZScore          | ready_in_existing_fast_evaluator      | False                              |

## Materialization Plan

| step       | name                                 | action                                                                                                               | executes_replay   | authorizes_alpha   |
|:-----------|:-------------------------------------|:---------------------------------------------------------------------------------------------------------------------|:------------------|:-------------------|
| A7AL-2X4M0 | operator extension                   | Add Clip/Winsor and state-aware StateMask/GroupNeutralize/LatentNeutralRank support to a crypto replay evaluator.    | False             | False              |
| A7AL-2X4M1 | upper-regime materialization         | Materialize A7AL-0G train-frozen regime states into a replay matrix aligned by timestamp.                            | False             | False              |
| A7AL-2X4M2 | latent/taxonomy materialization      | Materialize A7AK LV1/LV2 latent state ids plus meme/multiplier/major/liquidity-tier taxonomy into symbol-time panel. | False             | False              |
| A7AL-2X4M3 | family-balanced replay authorization | Only after M0-M2 pass, authorize numeric replay preflight on the 176 selected candidates.                            | False             | False              |

## Authorization

```json
{
  "a7al2y_generation": "NOT_AUTHORIZED",
  "alpha_proof": "NOT_AUTHORIZED",
  "decision": "HOLD_A7AL2X4_REPLAY_PREFLIGHT_NOT_READY_MATERIALIZATION_REQUIRED",
  "large_formula_search": "NOT_AUTHORIZED",
  "numeric_replay_preflight": "NOT_AUTHORIZED",
  "reason": "Current fast replay cannot honestly evaluate X3 family-balanced selected candidates until state fields and operators are materialized.",
  "shadow_paper_live": "NOT_AUTHORIZED"
}
```

## Boundary

```text
No numeric replay executed.
No search.
No selector scoring.
No May in generation/ranking/selector/mutation.
No alpha proof / shadow / paper / live.
```
