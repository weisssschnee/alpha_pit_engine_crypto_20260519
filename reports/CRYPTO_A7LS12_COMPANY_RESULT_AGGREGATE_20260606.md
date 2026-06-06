# CRYPTO A7LS-12 COMPANY RESULT AGGREGATE

Generated: 2026-06-06T03:05:13Z

## Decision

`PASS_A7LS12_DEEP_AUDIT_AGGREGATED_CLUES_FOUND_NO_SEARCH_AUTH`

## Summary

- expected_shards: 4
- completed_shards: 4
- pass_shards: 4
- hours_per_split: 0
- response_rows: 1860
- materialized_activity_ok_total: 93
- non_l7_numeric_clue_rows: 244
- rank_label_diagnostic_rows: 162
- shortlist_rows: 120
- non_l7_next_wave_family_count: 7
- non_l7_source_info_axis_count: 4
- non_l7_label_family_count: 4
- top_non_l7_semantic_pair_share: 0.242
- top_non_l7_next_family_share: 0.373
- top_non_l7_source_axis_share: 0.553
- blockers: <none>

A7LS-12 is a full-timestamp deep audit of A7LS-11 promoted non-L7 clues. It does not authorize search, alpha proof, shadow, paper, or live.

## Shard Summary

| shard   | manifest_path                                                                                             | decision                                                 | blockers   | missing_numeric_fields   |   input_blueprint_count |   hours_per_split |   materialized_activity_ok_count |   label_response_rows |   non_l7_numeric_clue_rows |   rank_label_diagnostic_clue_rows |   portfolio_queue_count |   selected_portfolio_queue_count | generated_at         |
|:--------|:----------------------------------------------------------------------------------------------------------|:---------------------------------------------------------|:-----------|:-------------------------|------------------------:|------------------:|---------------------------------:|----------------------:|---------------------------:|----------------------------------:|------------------------:|---------------------------------:|:---------------------|
| s000    | G:\AlphaFactory_CryptoData\research_runtime\a7ls12_company_deep_audit\shard_000\a7ls12_s000_manifest.json | PASS_A7LS12S000_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |            |                          |                      24 |                 0 |                               24 |                   480 |                         76 |                                60 |                      21 |                                9 | 2026-06-06T02:09:25Z |
| s001    | G:\AlphaFactory_CryptoData\research_runtime\a7ls12_company_deep_audit\shard_001\a7ls12_s001_manifest.json | PASS_A7LS12S001_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |            |                          |                      24 |                 0 |                               24 |                   480 |                         64 |                                32 |                      17 |                               13 | 2026-06-06T02:09:39Z |
| s002    | G:\AlphaFactory_CryptoData\research_runtime\a7ls12_company_deep_audit\shard_002\a7ls12_s002_manifest.json | PASS_A7LS12S002_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |            |                          |                      24 |                 0 |                               24 |                   480 |                         41 |                                28 |                      14 |                                9 | 2026-06-06T02:20:39Z |
| s003    | G:\AlphaFactory_CryptoData\research_runtime\a7ls12_company_deep_audit\shard_003\a7ls12_s003_manifest.json | PASS_A7LS12S003_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |            |                          |                      21 |                 0 |                               21 |                   420 |                         63 |                                42 |                      16 |                               10 | 2026-06-06T02:19:18Z |

## Non-L7 By Label

| label_family                       |   rows |
|:-----------------------------------|-------:|
| L1_cross_sectional_relative_return |     90 |
| L0_raw_forward_return              |     87 |
| L3_liquidity_tier_relative_return  |     59 |
| L5_vol_adjusted_return             |      8 |

## Non-L7 By Source Info Axis

| source_info_axis       |   rows |
|:-----------------------|-------:|
| vol_liquidity_x_basis  |    135 |
| raw_multi_axis         |     91 |
| listing_x_basis_regime |     15 |
| positioning_x_basis    |      3 |

## Non-L7 By Next Wave Family

| next_wave_family                |   rows |
|:--------------------------------|-------:|
| raw_multi_axis_probe            |     91 |
| vol_liquidity_interaction       |     65 |
| basis_context_interaction       |     50 |
| vol_liquidity_deep              |     20 |
| listing_state_interaction       |     15 |
| positioning_context_interaction |      2 |
| positioning_flow_recovery       |      1 |

## Response By Blocker Family

| blocker_family             |   rows |
|:---------------------------|-------:|
| control_dominated          |    952 |
| pre_may_unstable           |    455 |
| numeric_clue               |    244 |
| rank_label_diagnostic_clue |    162 |
| cost_fragile               |     40 |
| lag_fragile                |      7 |

## Authorization

- A7LS-13 consolidation / replay packet contract: allowed if non-L7 clues remain after review
- new formula search / large search: not authorized
- alpha proof / shadow / paper / live: not authorized
