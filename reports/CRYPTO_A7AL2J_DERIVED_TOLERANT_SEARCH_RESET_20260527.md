# CRYPTO A7AL-2J Derived-Tolerant Search Reset

Generated: 2026-05-27T10:18:53Z

## Decision

```text
PASS_A7AL2J_DERIVED_TOLERANT_RESET_READY_FOR_A7AL2K
```

This stage responds to A7AL-2I: the old 15-candidate selector pool did not produce clean clues, so the next generator must treat derived fields as first-class search inputs. This is still a contract/reset stage, not formula search execution.

## Manifest

```json
{
  "authorizes_a7al2k_generator_smoke": true,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search_execution": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7AL2J_DERIVED_TOLERANT_RESET_READY_FOR_A7AL2K",
  "derived_searchable_field_count": 26,
  "generated_at": "2026-05-27T10:18:53Z",
  "generator_cells": 7,
  "input_a7al2i_decision": "HOLD_A7AL2I_NO_CLUES",
  "input_a7as0_decision": "PASS_A7AS0_V2_DATA_ACCEPTANCE_READY_FOR_A7AL2G",
  "policy": "derived fields are first-class if lineage/PIT/control requirements are explicit; controls remain mandatory"
}
```

## Feature Roles

| role                       | feature_classes                                           | selector_policy                        | direct_rank_policy                           |
|:---------------------------|:----------------------------------------------------------|:---------------------------------------|:---------------------------------------------|
| first_class_derived_signal | derived_rolling|derived_interaction|derived_cross_section | allow_generation_and_selector_entry    | allowed only after matched-control dominance |
| regime_state_feature       | derived_latent_state|upper_regime_state                   | allow interaction and conditioning     | not direct standalone alpha rank             |
| overlay_diagnostic_feature | cross_exchange_30d_overlay                                | diagnostic only; no full-history proof | not direct standalone alpha rank             |
| label_or_forbidden         | derived_label|future_return|forward_*                     | blocked                                | blocked                                      |

## Generator Cells

| cell                                 | inputs                                                                           | objective                                                   |   budget_share |
|:-------------------------------------|:---------------------------------------------------------------------------------|:------------------------------------------------------------|---------------:|
| J0_oi_derived_state                  | open_interest_change_24h|open_interest_zscore_168h|oi_x_price_move_24h           | test leverage-flow state without direct OI level rank       |           0.18 |
| J1_vol_range_structure               | range_bps|realized_vol_24h|realized_vol_168h|vol_compression                     | test price/range derived structure beyond stale controls    |           0.18 |
| J2_liquidity_lifecycle               | trade_count|log_quote_volume_168h|liquidity_rank_active_universe|age_x_liquidity | test lifecycle/liquidity interaction, not raw activity rank |           0.16 |
| J3_basis_funding_derived             | basis_abs_168h|premium_abs_168h|funding_rate_abs_168h|funding_rate_mean_168h     | retest crowded dislocation as state interaction only        |           0.14 |
| J4_upper_regime_interaction          | R3_liquidity_cycle|R4_leverage_crowding|R5_basis_dislocation|R10_stress_proxy    | condition formulas on train-frozen upper regimes            |           0.14 |
| J5_cross_exchange_overlay_diagnostic | okx_binance_spread|funding_spread|oi_spread|basis_spread                         | 30d diagnostic only; no proof promotion                     |           0.08 |
| J6_controls_placebo                  | wrong_lag|shuffle|random|same_family_placebo                                     | negative controls                                           |           0.12 |

## Relaxed Selector Policy

| rule                        | value   | reason                                       |
|:----------------------------|:--------|:---------------------------------------------|
| generation_cap              | 8000    | more tolerance for derived-field exploration |
| selector_cap                | 768     | do not over-prune before replay              |
| strict_replay_cap           | 192     | small but broader than previous 128          |
| deep_audit_cap              | 48      | reserve only for post-control survivors      |
| min_selected_skeleton_count | 40      | avoid formula motif collapse                 |
| top_field_family_share_cap  | 0.30    | looser than proof, still prevents domination |
| matched_control_required    | true    | controls are not relaxed                     |
| one_bar_lag_required        | true    | native latency stress is retained            |

## Boundary

```text
Relaxed:
  derived fields can enter generation/selector more freely.

Not relaxed:
  matched-control dominance
  one-bar-lag stress
  label/PIT isolation
  no alpha proof / shadow / paper / live
```
