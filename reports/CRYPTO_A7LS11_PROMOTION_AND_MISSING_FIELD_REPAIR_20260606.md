# CRYPTO A7LS-11 PROMOTION AND MISSING FIELD REPAIR

Generated: 2026-06-06T01:20:22Z

## Decision

`PASS_A7LS11_PROMOTION_AND_FIELD_REPAIR_READY_NO_SEARCH_AUTH`

## Summary

- input_non_l7_numeric_clue_rows: 339
- eligible_non_l7_promotion_rows: 141
- immediate_deep_audit_rows: 93
- eligible_source_info_axis_count: 4
- eligible_next_wave_family_count: 8
- missing_field_repair_rows: 2
- quote_volume_alias_repair_ready: True

A7LS-11 does not run search, replay, or alpha proof. It converts the A7LS-10 company numeric output into a repairable deep-audit queue and fixes the known missing-field route.

## Eligible Family Summary

| source_info_axis       | next_wave_family                |   eligible_rows |   median_control_ratio |   max_deep_followup_score |   unique_skeletons |   unique_semantic_pairs |
|:-----------------------|:--------------------------------|----------------:|-----------------------:|--------------------------:|-------------------:|------------------------:|
| raw_multi_axis         | raw_multi_axis_probe            |              37 |               0.61336  |                   836.419 |                 13 |                       3 |
| vol_liquidity_x_basis  | basis_context_interaction       |              35 |               0.616876 |                   665.491 |                  9 |                       1 |
| vol_liquidity_x_basis  | vol_liquidity_interaction       |              31 |               0.715117 |                   595.96  |                  8 |                       3 |
| positioning_x_basis    | positioning_context_interaction |              24 |               0.709726 |                   527.419 |                  9 |                       2 |
| vol_liquidity_x_basis  | vol_liquidity_deep              |               6 |               0.703954 |                   527.787 |                  1 |                       1 |
| listing_x_basis_regime | listing_state_interaction       |               6 |               0.722494 |                   400.114 |                  3 |                       1 |
| vol_liquidity_x_basis  | basis_crowding_deep             |               1 |               0.647853 |                  1189.41  |                  1 |                       1 |
| positioning_x_basis    | positioning_flow_recovery       |               1 |               0.741917 |                   385.28  |                  1 |                       1 |

## Label Summary

| label_family                       |   non_l7_clue_rows |
|:-----------------------------------|-------------------:|
| L0_raw_forward_return              |                122 |
| L1_cross_sectional_relative_return |                126 |
| L3_liquidity_tier_relative_return  |                 69 |
| L5_vol_adjusted_return             |                 22 |

## Missing Field Repair Plan

| shard   | missing_field   | repair_action               | replacement_field   | status                                      |   blocked_input_blueprint_count | blocked_reason         |
|:--------|:----------------|:----------------------------|:--------------------|:--------------------------------------------|--------------------------------:|:-----------------------|
| s035    | quote_volume    | alias_to_trade_quote_volume | trade_quote_volume  | REPAIR_READY_ALIAS_EXISTS_IN_UNIVERSE498_V2 |                              64 | missing_numeric_fields |
| s036    | quote_volume    | alias_to_trade_quote_volume | trade_quote_volume  | REPAIR_READY_ALIAS_EXISTS_IN_UNIVERSE498_V2 |                              64 | missing_numeric_fields |

## Blocked Next Tasks

| blocked_task                     | reason                                                                       |
|:---------------------------------|:-----------------------------------------------------------------------------|
| large_search                     | A7LS10 is numeric clue aggregation, not replay or alpha proof                |
| alpha_proof_shadow_paper_live    | no portfolio/deep replay authorization and no live-forward proof             |
| reuse_quote_volume_without_alias | quote_volume is not in universe498 v2; use trade_quote_volume alias or block |
| rank_label_only_promotion        | ranked label diagnostics remain separate from non-L7 promotion               |

## Authorization

- A7LS-12 deep-audit contract: authorized
- new formula search / large search: not authorized
- alpha proof / shadow / paper / live: not authorized
