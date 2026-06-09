# CRYPTO A7LS Field Gate Current Queue 20260609

## Decision

`HOLD_A7LS_FIELD_GATE_CONTRACT_DRIFT_BACKFILL_REQUIRED`

This is a field ingress gate for the current A7LS28B queue. It does not run numeric compute, replay, search, or alpha proof.

## Counts

- queue_rows: 2836
- expression_field_count: 34
- total_field_count_including_system: 36
- unresolved_field_count: 0
- contract_drift_field_count: 17
- blocked_formula_count: 0
- contract_drift_formula_count: 1506
- authorizes_current_running_wave_to_continue: true
- authorizes_next_search_expansion: false

## Interpretation

Unresolved fields block execution. Fields resolved only through runner-local aliases or derived dependency code are not immediate execution blockers, but they are contract drift until they are backfilled into the shared field registry / A7AIF materialization matrix.

## Route Summary

| route                 | contract_status                                      |   field_count |   formula_usage_count |
|:----------------------|:-----------------------------------------------------|--------------:|----------------------:|
| base_schema           | OK_IN_A7AIF3_CONTRACT                                |            16 |                  4153 |
| latent_schema         | OK_IN_A7AIF3_CONTRACT                                |             3 |                    42 |
| latent_schema         | OK_SCHEMA_DIRECT_NOT_IN_A7AIF3                       |             8 |                   768 |
| derived_dep_generated | RESOLVED_BY_RUNNER_EXTENSION_NEEDS_REGISTRY_BACKFILL |             4 |                   529 |
| upper_alias           | RESOLVED_BY_RUNNER_EXTENSION_NEEDS_REGISTRY_BACKFILL |             5 |                   455 |

## Drift Fields

| field                          | route                 | canonical_field                    | dependencies                                                           |   formula_usage_count | contract_status                                      |
|:-------------------------------|:----------------------|:-----------------------------------|:-----------------------------------------------------------------------|----------------------:|:-----------------------------------------------------|
| account_position_divergence    | derived_dep_generated | account_position_divergence        | top_long_short_account_ratio_last;top_long_short_position_ratio_last   |                   362 | RESOLVED_BY_RUNNER_EXTENSION_NEEDS_REGISTRY_BACKFILL |
| age_percentile_active_universe | latent_schema         | age_percentile_active_universe     |                                                                        |                    18 | OK_SCHEMA_DIRECT_NOT_IN_A7AIF3                       |
| age_x_volatility               | latent_schema         | age_x_volatility                   |                                                                        |                   303 | OK_SCHEMA_DIRECT_NOT_IN_A7AIF3                       |
| basis_abs_168h                 | latent_schema         | basis_abs_168h                     |                                                                        |                   212 | OK_SCHEMA_DIRECT_NOT_IN_A7AIF3                       |
| basis_dislocation_state        | upper_alias           | R5_basis_premium_dislocation_state |                                                                        |                    79 | RESOLVED_BY_RUNNER_EXTENSION_NEEDS_REGISTRY_BACKFILL |
| leverage_crowding_state        | upper_alias           | R4_leverage_crowding_state         |                                                                        |                    66 | RESOLVED_BY_RUNNER_EXTENSION_NEEDS_REGISTRY_BACKFILL |
| liquidity_cycle_state          | upper_alias           | R3_liquidity_cycle_state           |                                                                        |                   103 | RESOLVED_BY_RUNNER_EXTENSION_NEEDS_REGISTRY_BACKFILL |
| listing_age_days               | latent_schema         | listing_age_days                   |                                                                        |                    28 | OK_SCHEMA_DIRECT_NOT_IN_A7AIF3                       |
| log1p_listing_age_days         | latent_schema         | log1p_listing_age_days             |                                                                        |                    18 | OK_SCHEMA_DIRECT_NOT_IN_A7AIF3                       |
| market_breadth_state           | upper_alias           | R2_market_breadth_state            |                                                                        |                    94 | RESOLVED_BY_RUNNER_EXTENSION_NEEDS_REGISTRY_BACKFILL |
| open_interest_value_change_24h | derived_dep_generated | open_interest_value_change_24h     | open_interest_value_last                                               |                     5 | RESOLVED_BY_RUNNER_EXTENSION_NEEDS_REGISTRY_BACKFILL |
| premium_abs_168h               | latent_schema         | premium_abs_168h                   |                                                                        |                    68 | OK_SCHEMA_DIRECT_NOT_IN_A7AIF3                       |
| premium_abs_state              | derived_dep_generated | premium_abs_state                  | premium_close_bps                                                      |                    58 | RESOLVED_BY_RUNNER_EXTENSION_NEEDS_REGISTRY_BACKFILL |
| rolling_coverage_168h          | latent_schema         | rolling_coverage_168h              |                                                                        |                   113 | OK_SCHEMA_DIRECT_NOT_IN_A7AIF3                       |
| sqrt_listing_age_days          | latent_schema         | sqrt_listing_age_days              |                                                                        |                     8 | OK_SCHEMA_DIRECT_NOT_IN_A7AIF3                       |
| stress_proxy_state             | upper_alias           | R10_stress_proxy_state             |                                                                        |                   113 | RESOLVED_BY_RUNNER_EXTENSION_NEEDS_REGISTRY_BACKFILL |
| top_global_account_divergence  | derived_dep_generated | top_global_account_divergence      | global_long_short_account_ratio_last;top_long_short_account_ratio_last |                   104 | RESOLVED_BY_RUNNER_EXTENSION_NEEDS_REGISTRY_BACKFILL |

## Blocked Fields

`<empty>`

## Formula Gate Summary

| gate_decision                         | semantic_pair                                          |   formula_count |
|:--------------------------------------|:-------------------------------------------------------|----------------:|
| PASS                                  | basis_premium_like\|positioning_like                   |            1247 |
| HOLD_CONTRACT_DRIFT_BACKFILL_REQUIRED | open_interest_like\|positioning_like\|regime_state     |             568 |
| HOLD_CONTRACT_DRIFT_BACKFILL_REQUIRED | basis_premium_like\|positioning_like                   |             459 |
| HOLD_CONTRACT_DRIFT_BACKFILL_REQUIRED | open_interest_like\|positioning_like\|listing_age_like |             196 |
| HOLD_CONTRACT_DRIFT_BACKFILL_REQUIRED | basis_premium_like\|age_x_volatility\|positioning_like |             179 |
| HOLD_CONTRACT_DRIFT_BACKFILL_REQUIRED | open_interest_like\|positioning_like                   |             104 |
| PASS                                  | open_interest_like\|positioning_like                   |              83 |

## Outputs

- `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7ls_field_gate_current_queue_20260609\a7ls_field_gate_manifest.json`
- `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7ls_field_gate_current_queue_20260609\a7ls_field_gate_field_route_map.csv`
- `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7ls_field_gate_current_queue_20260609\a7ls_field_gate_formula_audit.csv`
- `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7ls_field_gate_current_queue_20260609\a7ls_field_gate_contract_drift_fields.csv`
- `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7ls_field_gate_current_queue_20260609\a7ls_field_gate_blocked_fields.csv`
- `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7ls_field_gate_current_queue_20260609\a7ls_field_gate_route_summary.csv`
- `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7ls_field_gate_current_queue_20260609\a7ls_field_gate_formula_gate_summary.csv`
