# CRYPTO A7LS-3HR COMPANY RESULT AGGREGATE

Generated: 2026-06-05T08:19:31Z

## Decision

`PASS_A7LS3HR_COMPANY_RESULTS_AGGREGATED_READY_FOR_FORENSIC`

## Summary

- external: `G:\AlphaFactory_CryptoData\research_runtime\a7ls3hr_company_numeric`
- expected_shards: 16
- completed_shards: 16
- missing_shards: 0
- combined_clue_rows: 45
- combined_response_rows: 33280
- combined_portfolio_rows: 143
- stress_clean_clue_count_observed: 0

Expected primary shards from handoff plan: 16 rows in shard plan.

## Key Findings

- Company execution did run successfully: all 16 shards returned manifests.
- 7 shards returned `NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH`.
- 3 shards failed with `missing_numeric_fields`; root cause is company/local `binance_universe498_replay_1h_v2_20260527` lacks listing-age fields such as `sqrt_listing_age_days`, `age_percentile_active_universe`, `log_listing_age_days`, and `listing_age_days`.
- Combined clue rows: 45. Label split: `L7_ranked_future_return` 23, `L5_vol_adjusted_return` 20, `L3_liquidity_tier_relative_return` 2.
- Combined clue semantic pairs: `low_prior_axes|basis_premium_like` 17, `basis_premium_like` 11, `liquidity_like` 7, `open_interest_like` 7, `price_like` 3.
- Combined response map still shows a large unstable/control-dominated surface; this is a numeric clue harvest, not search authorization.

## Decision Counts

| decision                                                  |   count |
|:----------------------------------------------------------|--------:|
| HOLD_A7LS3HRS000_PORTFOLIO_QUEUE_TOO_SMALL                |       1 |
| HOLD_A7LS3HRS001_NO_NON_L7_NUMERIC_CLUES                  |       1 |
| HOLD_A7LS3HRS002_PORTFOLIO_QUEUE_TOO_SMALL                |       1 |
| HOLD_A7LS3HRS003_PORTFOLIO_QUEUE_TOO_SMALL                |       1 |
| HOLD_A7LS3HRS004_NO_NON_L7_NUMERIC_CLUES                  |       1 |
| PASS_A7LS3HRS005_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |       1 |
| PASS_A7LS3HRS006_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |       1 |
| HOLD_A7LS3HRS007_MISSING_FIELDS                           |       1 |
| HOLD_A7LS3HRS008_PORTFOLIO_QUEUE_TOO_SMALL                |       1 |
| PASS_A7LS3HRS009_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |       1 |
| PASS_A7LS3HRS010_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |       1 |
| PASS_A7LS3HRS011_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |       1 |
| PASS_A7LS3HRS012_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |       1 |
| HOLD_A7LS3HRS013_MISSING_FIELDS                           |       1 |
| HOLD_A7LS3HRS014_MISSING_FIELDS                           |       1 |
| HOLD_A7LS3HRS015_NO_NON_L7_NUMERIC_CLUES                  |       1 |

## Missing Shards

_none_

## Authorization

- Aggregation only.
- Does not execute numeric probe, search, alpha proof, shadow, paper, or live.
