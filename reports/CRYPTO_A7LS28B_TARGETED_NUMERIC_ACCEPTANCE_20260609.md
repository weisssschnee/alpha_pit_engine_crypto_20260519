# CRYPTO A7LS28B Targeted Numeric Acceptance 20260609

## Decision

`HOLD_A7LS28B_NO_PASS_SHARDS_PORTFOLIO_QUEUE_TOO_SMALL`

A7LS28B finished on the company machine. It did not crash and had no missing-field shards, but every shard ended HOLD, mostly because selected portfolio queues were too small.

## Counts

- queue_rows: 2836
- shard_count: 12
- pass_count: 0
- hold_count: 12
- missing_count: 0
- activity_ok_total: 2730
- non_l7_numeric_clue_rows_total: 3847
- rank_label_diagnostic_clue_rows_total: 1715
- selected_portfolio_queue_rows_total: 12

## Shard Summary

| shard_id         | decision                                               |   materialized_activity_ok_count |   non_l7_numeric_clue_rows |   rank_label_diagnostic_clue_rows |   selected_portfolio_queue_count | missing_numeric_fields   |
|:-----------------|:-------------------------------------------------------|---------------------------------:|---------------------------:|----------------------------------:|---------------------------------:|:-------------------------|
| a7ls28b_num_s000 | HOLD_A7LS28Ba7ls28b_num_s000_PORTFOLIO_QUEUE_TOO_SMALL |                              256 |                        508 |                               154 |                                1 | []                       |
| a7ls28b_num_s001 | HOLD_A7LS28Ba7ls28b_num_s001_PORTFOLIO_QUEUE_TOO_SMALL |                              256 |                        413 |                                91 |                                1 | []                       |
| a7ls28b_num_s002 | HOLD_A7LS28Ba7ls28b_num_s002_PORTFOLIO_QUEUE_TOO_SMALL |                              256 |                        492 |                               273 |                                1 | []                       |
| a7ls28b_num_s003 | HOLD_A7LS28Ba7ls28b_num_s003_PORTFOLIO_QUEUE_TOO_SMALL |                              256 |                        437 |                               458 |                                1 | []                       |
| a7ls28b_num_s004 | HOLD_A7LS28Ba7ls28b_num_s004_PORTFOLIO_QUEUE_TOO_SMALL |                              256 |                        359 |                               140 |                                1 | []                       |
| a7ls28b_num_s005 | HOLD_A7LS28Ba7ls28b_num_s005_PORTFOLIO_QUEUE_TOO_SMALL |                              256 |                        151 |                                69 |                                1 | []                       |
| a7ls28b_num_s006 | HOLD_A7LS28Ba7ls28b_num_s006_PORTFOLIO_QUEUE_TOO_SMALL |                              256 |                        185 |                                60 |                                1 | []                       |
| a7ls28b_num_s007 | HOLD_A7LS28Ba7ls28b_num_s007_PORTFOLIO_QUEUE_TOO_SMALL |                              256 |                        264 |                               149 |                                1 | []                       |
| a7ls28b_num_s008 | HOLD_A7LS28Ba7ls28b_num_s008_PORTFOLIO_QUEUE_TOO_SMALL |                              230 |                        354 |                                81 |                                1 | []                       |
| a7ls28b_num_s009 | HOLD_A7LS28Ba7ls28b_num_s009_PORTFOLIO_QUEUE_TOO_SMALL |                              192 |                        504 |                               184 |                                1 | []                       |
| a7ls28b_num_s010 | HOLD_A7LS28Ba7ls28b_num_s010_PORTFOLIO_QUEUE_TOO_SMALL |                              240 |                        180 |                                55 |                                1 | []                       |
| a7ls28b_num_s011 | HOLD_A7LS28Ba7ls28b_num_s011_NO_NON_L7_NUMERIC_CLUES   |                               20 |                          0 |                                 1 |                                1 | []                       |

## Non-L7 Family Summary

| semantic_pair                                          | motif               | label_family                       |   non_l7_rows |
|:-------------------------------------------------------|:--------------------|:-----------------------------------|--------------:|
| open_interest_like\|positioning_like\|regime_state     | seed_gated_sign     | L3_liquidity_tier_relative_return  |           575 |
| basis_premium_like\|positioning_like                   | spread_rank         | L5_vol_adjusted_return             |           256 |
| basis_premium_like\|positioning_like                   | signed_spread       | L5_vol_adjusted_return             |           239 |
| basis_premium_like\|positioning_like                   | spread_rank         | L1_cross_sectional_relative_return |           233 |
| basis_premium_like\|positioning_like                   | spread_rank         | L0_raw_forward_return              |           230 |
| basis_premium_like\|positioning_like                   | spread_rank         | L3_liquidity_tier_relative_return  |           218 |
| open_interest_like\|positioning_like\|listing_age_like | seed_sub            | L3_liquidity_tier_relative_return  |           210 |
| basis_premium_like\|positioning_like                   | signed_spread       | L3_liquidity_tier_relative_return  |           173 |
| basis_premium_like\|positioning_like                   | signed_spread       | L1_cross_sectional_relative_return |           167 |
| basis_premium_like\|positioning_like                   | signed_spread       | L0_raw_forward_return              |           165 |
| basis_premium_like\|positioning_like                   | safe_div_abs        | L5_vol_adjusted_return             |           145 |
| basis_premium_like\|age_x_volatility\|positioning_like | seed_mul            | L0_raw_forward_return              |           104 |
| basis_premium_like\|age_x_volatility\|positioning_like | seed_mul            | L1_cross_sectional_relative_return |           104 |
| basis_premium_like\|positioning_like                   | safe_div_abs        | L1_cross_sectional_relative_return |            93 |
| basis_premium_like\|positioning_like                   | safe_div_abs        | L0_raw_forward_return              |            93 |
| open_interest_like\|positioning_like\|listing_age_like | seed_sub            | L1_cross_sectional_relative_return |            83 |
| open_interest_like\|positioning_like                   | safe_div_abs        | L1_cross_sectional_relative_return |            80 |
| basis_premium_like\|age_x_volatility\|positioning_like | seed_sub            | L0_raw_forward_return              |            79 |
| open_interest_like\|positioning_like\|listing_age_like | seed_sub            | L0_raw_forward_return              |            79 |
| basis_premium_like\|positioning_like                   | safe_div_abs        | L3_liquidity_tier_relative_return  |            78 |
| basis_premium_like\|age_x_volatility\|positioning_like | seed_sub            | L1_cross_sectional_relative_return |            75 |
| open_interest_like\|positioning_like                   | safe_div_abs        | L0_raw_forward_return              |            71 |
| basis_premium_like\|age_x_volatility\|positioning_like | seed_mul            | L3_liquidity_tier_relative_return  |            64 |
| basis_premium_like\|age_x_volatility\|positioning_like | seed_sub            | L3_liquidity_tier_relative_return  |            44 |
| open_interest_like\|positioning_like                   | smooth_mul          | L5_vol_adjusted_return             |            41 |
| open_interest_like\|positioning_like                   | safe_div_abs        | L3_liquidity_tier_relative_return  |            29 |
| open_interest_like\|positioning_like                   | smooth_mul          | L1_cross_sectional_relative_return |            23 |
| open_interest_like\|positioning_like                   | smooth_mul          | L0_raw_forward_return              |            22 |
| basis_premium_like\|positioning_like                   | mean_reversion_gate | L5_vol_adjusted_return             |            18 |
| basis_premium_like\|positioning_like                   | mean_reversion_gate | L0_raw_forward_return              |            14 |
| basis_premium_like\|positioning_like                   | mean_reversion_gate | L3_liquidity_tier_relative_return  |            12 |
| basis_premium_like\|positioning_like                   | sub                 | L5_vol_adjusted_return             |            11 |
| basis_premium_like\|positioning_like                   | mean_reversion_gate | L1_cross_sectional_relative_return |             7 |
| open_interest_like\|positioning_like                   | safe_div_abs        | L5_vol_adjusted_return             |             5 |
| open_interest_like\|positioning_like                   | smooth_mul          | L3_liquidity_tier_relative_return  |             3 |
| open_interest_like\|positioning_like\|regime_state     | seed_gated_sign     | L1_cross_sectional_relative_return |             3 |
| open_interest_like\|positioning_like\|regime_state     | seed_gated_sign     | L0_raw_forward_return              |             1 |

## Selected Family Summary

| semantic_pair                        | motif         |   selected_rows |
|:-------------------------------------|:--------------|----------------:|
| basis_premium_like\|positioning_like | spread_rank   |               5 |
| open_interest_like\|positioning_like | safe_div_abs  |               3 |
| basis_premium_like\|positioning_like | signed_spread |               2 |
| basis_premium_like\|positioning_like | safe_div_abs  |               2 |

## Interpretation

The wave was not??: it evaluated all 12 shards and produced thousands of non-L7 response rows. The failure is downstream selection strength/portfolio queue size, not field materialization or missing fields. Next expansion should consume A7LS-FIELD-GATE-1 registry and either relax portfolio queue minimums for targeted diagnostic waves or compile a larger queue from the productive non-L7 families.

## Outputs

- `G:\AlphaFactory_CryptoData\research_runtime\a7ls28b_targeted_numeric_acceptance_20260609\a7ls28b_shard_manifest_summary.csv`
- `G:\AlphaFactory_CryptoData\research_runtime\a7ls28b_targeted_numeric_acceptance_20260609\a7ls28b_non_l7_family_summary.csv`
- `G:\AlphaFactory_CryptoData\research_runtime\a7ls28b_targeted_numeric_acceptance_20260609\a7ls28b_selected_family_summary.csv`
- `G:\AlphaFactory_CryptoData\research_runtime\a7ls28b_targeted_numeric_acceptance_20260609\a7ls28b_non_l7_top120.csv`
- `G:\AlphaFactory_CryptoData\research_runtime\a7ls28b_targeted_numeric_acceptance_20260609\a7ls28b_selected_top80.csv`
- `G:\AlphaFactory_CryptoData\manifests\a7ls28b_targeted_numeric_acceptance_20260609_manifest.json`
