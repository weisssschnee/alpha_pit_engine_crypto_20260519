# CRYPTO A7LS Field Gate 1 Contract Backfill 20260609

## Decision

`PASS_A7LS_FIELD_GATE1_BACKFILL_PACKAGE_BUILT`

This package backfills the 17 A7LS-FIELD-GATE-0 drift fields into explicit field-contract rows. It does not run numeric compute, replay, search, or alpha proof.

## Counts

- input_drift_field_count: 17
- backfill_field_count: 17
- unresolved_backfill_count: 0
- a7aif3_append_rows: 17
- ontology_patch_rows: 17
- runner_upper_alias_count: 5
- runner_derived_dependency_count: 4
- authorizes_current_running_wave_to_continue: true
- authorizes_next_search_expansion_if_registry_consumed: true

## Critical Rule

These fields are backfilled as regime / neutralizer / diagnostic / interaction inputs. They are not promoted to ordinary-alpha primary seeds. Ordinary-alpha promotion still requires response-backed non-L7 evidence.

## Route Summary

| route                 | semantic_role                     | compiler_role_v3                    |   field_count |   formula_usage_count |
|:----------------------|:----------------------------------|:------------------------------------|--------------:|----------------------:|
| latent_schema         | regime_state_or_interaction_input | regime_neutralizer_interaction_seed |             3 |                   583 |
| derived_dep_generated | risk_exposure_or_control_like     | regime_neutralizer_interaction_seed |             2 |                   466 |
| upper_alias           | regime_state_or_interaction_input | state_conditioning_only             |             5 |                   455 |
| latent_schema         | risk_exposure_or_control_like     | regime_neutralizer_interaction_seed |             5 |                   185 |
| derived_dep_generated | regime_state_or_interaction_input | regime_neutralizer_interaction_seed |             1 |                    58 |
| derived_dep_generated | regime_state_or_interaction_input | exploratory_interaction_seed        |             1 |                     5 |

## Backfill Fields

| field_name                     | route                 | semantic_type_v3         | semantic_role                     | compiler_role_v3                    | allowed_roles_v3                          | ordinary_alpha_allowed   | diagnostic_allowed   | risk_defense_allowed   |   formula_usage_count | backfill_decision       |
|:-------------------------------|:----------------------|:-------------------------|:----------------------------------|:------------------------------------|:------------------------------------------|:-------------------------|:---------------------|:-----------------------|----------------------:|:------------------------|
| account_position_divergence    | derived_dep_generated | positioning_like         | risk_exposure_or_control_like     | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier | False                    | True                 | True                   |                   362 | PASS_BACKFILL_ROW_READY |
| open_interest_value_change_24h | derived_dep_generated | open_interest_like       | regime_state_or_interaction_input | exploratory_interaction_seed        | diagnostic\|interaction_modifier          | False                    | True                 | False                  |                     5 | PASS_BACKFILL_ROW_READY |
| premium_abs_state              | derived_dep_generated | basis_premium_like       | regime_state_or_interaction_input | regime_neutralizer_interaction_seed | regime\|diagnostic\|interaction_modifier  | False                    | True                 | False                  |                    58 | PASS_BACKFILL_ROW_READY |
| top_global_account_divergence  | derived_dep_generated | positioning_like         | risk_exposure_or_control_like     | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier | False                    | True                 | True                   |                   104 | PASS_BACKFILL_ROW_READY |
| age_percentile_active_universe | latent_schema         | listing_age_like         | risk_exposure_or_control_like     | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier | False                    | True                 | True                   |                    18 | PASS_BACKFILL_ROW_READY |
| age_x_volatility               | latent_schema         | age_x_volatility         | regime_state_or_interaction_input | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier | False                    | True                 | False                  |                   303 | PASS_BACKFILL_ROW_READY |
| basis_abs_168h                 | latent_schema         | basis_premium_like       | regime_state_or_interaction_input | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier | False                    | True                 | False                  |                   212 | PASS_BACKFILL_ROW_READY |
| listing_age_days               | latent_schema         | listing_age_like         | risk_exposure_or_control_like     | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier | False                    | True                 | True                   |                    28 | PASS_BACKFILL_ROW_READY |
| log1p_listing_age_days         | latent_schema         | listing_age_like         | risk_exposure_or_control_like     | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier | False                    | True                 | True                   |                    18 | PASS_BACKFILL_ROW_READY |
| premium_abs_168h               | latent_schema         | basis_premium_like       | regime_state_or_interaction_input | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier | False                    | True                 | False                  |                    68 | PASS_BACKFILL_ROW_READY |
| rolling_coverage_168h          | latent_schema         | coverage_like            | risk_exposure_or_control_like     | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier | False                    | True                 | True                   |                   113 | PASS_BACKFILL_ROW_READY |
| sqrt_listing_age_days          | latent_schema         | listing_age_like         | risk_exposure_or_control_like     | regime_neutralizer_interaction_seed | regime\|neutralizer\|interaction_modifier | False                    | True                 | True                   |                     8 | PASS_BACKFILL_ROW_READY |
| basis_dislocation_state        | upper_alias           | basis_dislocation_regime | regime_state_or_interaction_input | state_conditioning_only             | regime\|neutralizer\|interaction_modifier | False                    | True                 | True                   |                    79 | PASS_BACKFILL_ROW_READY |
| leverage_crowding_state        | upper_alias           | leverage_crowding_regime | regime_state_or_interaction_input | state_conditioning_only             | regime\|neutralizer\|interaction_modifier | False                    | True                 | True                   |                    66 | PASS_BACKFILL_ROW_READY |
| liquidity_cycle_state          | upper_alias           | liquidity_regime         | regime_state_or_interaction_input | state_conditioning_only             | regime\|neutralizer\|interaction_modifier | False                    | True                 | True                   |                   103 | PASS_BACKFILL_ROW_READY |
| market_breadth_state           | upper_alias           | market_breadth_regime    | regime_state_or_interaction_input | state_conditioning_only             | regime\|neutralizer\|interaction_modifier | False                    | True                 | True                   |                    94 | PASS_BACKFILL_ROW_READY |
| stress_proxy_state             | upper_alias           | stress_regime            | regime_state_or_interaction_input | state_conditioning_only             | regime\|neutralizer\|interaction_modifier | False                    | True                 | True                   |                   113 | PASS_BACKFILL_ROW_READY |

## Search Authorization

| stage             | decision                                     | authorizes_current_running_wave_to_continue   | authorizes_next_search_expansion_if_registry_consumed   | authorizes_alpha_proof   | hard_rules                                                                                                                                                                                                                                                                                                                                                         |
|:------------------|:---------------------------------------------|:----------------------------------------------|:--------------------------------------------------------|:-------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| A7LS-FIELD-GATE-1 | PASS_A7LS_FIELD_GATE1_BACKFILL_PACKAGE_BUILT | True                                          | True                                                    | False                    | ['backfilled fields remain interaction/regime/diagnostic inputs, not ordinary-alpha primary seeds', 'next queue builder must consume a7ls_field_gate1_runner_extension_registry.json or equivalent shared registry rows', 'any new unresolved field returns to BLOCK_UNRESOLVED_FIELD', 'ordinary_alpha promotion still requires response-backed non-L7 evidence'] |

## Outputs

- `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7ls_field_gate1_contract_backfill_20260609\a7ls_field_gate1_manifest.json`
- `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7ls_field_gate1_contract_backfill_20260609\a7ls_field_gate1_backfill_field_contract.csv`
- `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7ls_field_gate1_contract_backfill_20260609\a7ls_field_gate1_a7aif3_matrix_append.csv`
- `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7ls_field_gate1_contract_backfill_20260609\a7ls_field_gate1_ontology_v3_patch.csv`
- `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7ls_field_gate1_contract_backfill_20260609\a7ls_field_gate1_runner_extension_registry.json`
- `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7ls_field_gate1_contract_backfill_20260609\a7ls_field_gate1_search_authorization.json`
