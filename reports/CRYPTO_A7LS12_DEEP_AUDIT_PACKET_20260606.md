# CRYPTO A7LS-12 DEEP AUDIT PACKET

Generated: 2026-06-06T01:46:18Z

## Decision

`PASS_A7LS12_DEEP_AUDIT_PACKET_READY_FOR_COMPANY_EXECUTION_NO_SEARCH_AUTH`

## Summary

- deep_audit_queue_rows: 93
- deep_audit_shard_count: 4
- rows_per_shard_target: 24
- hours_per_split: 0 (full available timestamps per split)
- alias_rewrite_rows: 0
- source_info_axis_count: 4
- label_family_count: 4
- next_wave_family_count: 8

A7LS-12 packages A7LS-11 promoted non-L7 clues for company-machine deep audit. It does not generate new formulas and does not authorize search or alpha proof.

## Shard Plan

| a7ls12_deep_shard   |   queue_rows |   unique_source_axis |   unique_label_family |   unique_semantic_pair |   unique_skeleton |   rows_per_shard_target |   hours_per_split |
|:--------------------|-------------:|---------------------:|----------------------:|-----------------------:|------------------:|------------------------:|------------------:|
| a7ls12_s000         |           24 |                    3 |                     4 |                      7 |                12 |                      24 |                 0 |
| a7ls12_s001         |           24 |                    3 |                     4 |                      9 |                17 |                      24 |                 0 |
| a7ls12_s002         |           24 |                    4 |                     4 |                      9 |                14 |                      24 |                 0 |
| a7ls12_s003         |           21 |                    4 |                     3 |                     10 |                15 |                      24 |                 0 |

## Source Axis Summary

| source_info_axis       |   deep_audit_rows |
|:-----------------------|------------------:|
| listing_x_basis_regime |                 5 |
| positioning_x_basis    |                21 |
| raw_multi_axis         |                29 |
| vol_liquidity_x_basis  |                38 |

## Label Summary

| label_family                       |   deep_audit_rows |
|:-----------------------------------|------------------:|
| L0_raw_forward_return              |                30 |
| L1_cross_sectional_relative_return |                34 |
| L3_liquidity_tier_relative_return  |                20 |
| L5_vol_adjusted_return             |                 9 |

## Field Alias Audit

| old_field    | replacement_field   |   queue_rows_rewritten | status               |
|:-------------|:--------------------|-----------------------:|:---------------------|
| quote_volume | trade_quote_volume  |                      0 | ACTIVE_ALIAS_REWRITE |

## Authorization

- company deep audit execution: authorized
- new generation / formula search / large search: not authorized
- alpha proof / shadow / paper / live: not authorized
