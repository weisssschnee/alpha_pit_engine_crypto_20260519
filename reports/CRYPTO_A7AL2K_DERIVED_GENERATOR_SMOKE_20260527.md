# CRYPTO A7AL-2K Derived Generator Smoke

Generated: 2026-05-27T10:35:01Z

## Decision

```text
PASS_A7AL2K_DERIVED_GENERATOR_SMOKE_READY_FOR_A7AL2L
```

## Summary

```json
{
  "authorizes_a7al2l_replay_preflight": true,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search_execution": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "control_rows": 4608,
  "decision": "PASS_A7AL2K_DERIVED_GENERATOR_SMOKE_READY_FOR_A7AL2L",
  "executes_formula_generation": true,
  "executes_replay": false,
  "generated_at": "2026-05-27T10:35:01Z",
  "generated_candidates": 8000,
  "policy": "derived formulas are allowed broadly; label/PIT/control requirements are not relaxed",
  "selected_cell_count": 5,
  "selected_field_family_count": 6,
  "selected_for_a7al2l_replay_preflight": 768,
  "selected_skeleton_count": 47,
  "selector_cap": 768
}
```

## Cell Quotas

| cell                                 |   generated |   static_valid |   selected |   diagnostic_only |
|:-------------------------------------|------------:|---------------:|-----------:|------------------:|
| J0_oi_derived_state                  |        2400 |           2400 |        138 |                 0 |
| J1_vol_range_structure               |        1440 |           1440 |        185 |                 0 |
| J2_liquidity_lifecycle               |        1280 |           1280 |        138 |                 0 |
| J3_basis_funding_derived             |        1120 |           1120 |        154 |                 0 |
| J4_upper_regime_interaction          |        1120 |           1120 |        153 |                 0 |
| J5_cross_exchange_overlay_diagnostic |         640 |            640 |          0 |               640 |

## Selector Trace

| selector_reason                          |   count |
|:-----------------------------------------|--------:|
| diagnostic_overlay_not_historical_replay |     640 |
| eligible_not_selected_by_budget_or_caps  |    6592 |
| selected_diversity_capped                |     768 |

## Diversity

| metric                       | top_value                                                             |   top_count |      share |   cap | pass   |
|:-----------------------------|:----------------------------------------------------------------------|------------:|-----------:|------:|:-------|
| top_skeleton_share           | skeleton-377d45dadd905908                                             |          24 | 0.03125    |  0.15 | True   |
| top_production_key_share     | a7al2k_derived_generator::derived_vol_range_state::volatility::48|168 |           7 | 0.00911458 |  0.2  | True   |
| top_cell_share               | J1_vol_range_structure                                                |         185 | 0.240885   |  0.3  | True   |
| top_field_family_token_share | open_interest                                                         |         230 | 0.188216   |  0.3  | True   |

## Feature Lineage Audit

| check                                                 | status   | detail                                              |
|:------------------------------------------------------|:---------|:----------------------------------------------------|
| a7al2j_ready                                          | PASS     | PASS_A7AL2J_DERIVED_TOLERANT_RESET_READY_FOR_A7AL2K |
| base_schema_available                                 | PASS     | 54                                                  |
| overlay_schema_available                              | PASS     | 65                                                  |
| label_future_field_block                              | PASS     | 0                                                   |
| diagnostic_overlay_excluded_from_historical_selection | PASS     | 0                                                   |

## Control Attachment

| check                       | status   | detail               |
|:----------------------------|:---------|:---------------------|
| selected_candidates         | PASS     | 768                  |
| matched_control_rows        | PASS     | 4608                 |
| one_bar_lag_attached        | PASS     | one_bar_lag          |
| wrong_lag_future_attached   | PASS     | wrong_lag_future_24h |
| same_family_random_attached | PASS     | same_family_random   |

## Boundary

```text
This stage executes formula generation only.
It does not execute replay, alpha proof, shadow, paper, or live.

Derived-field tolerance is intentionally high:
  rolling / interaction / cross-sectional / upper-regime proxy formulas are allowed.

Not relaxed:
  no forward labels as features
  matched controls required
  one-bar-lag control required
  30d cross-exchange overlay excluded from historical replay selection
```
