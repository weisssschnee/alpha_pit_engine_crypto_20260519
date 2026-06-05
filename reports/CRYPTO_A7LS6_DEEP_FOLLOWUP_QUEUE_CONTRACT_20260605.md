# CRYPTO A7LS-6 DEEP FOLLOWUP QUEUE CONTRACT

Generated: 2026-06-05T11:48:37Z

## Decision

`PASS_A7LS6_DEEP_FOLLOWUP_QUEUE_READY_FOR_COMPANY_NUMERIC_NO_SEARCH_AUTH`

## Summary

- seed_rows: 99
- full_generated_pool_rows: 797
- company_numeric_queue_rows: 659
- company_shard_count: 11
- rows_per_shard: 64
- target hours_per_split: 2160
- followup_family_count: 4
- semantic_pair_count: 16
- motif_count: 7

## Seed Summary

| semantic_pair      | label_family                       |   seed_rows |
|:-------------------|:-----------------------------------|------------:|
| basis_premium_like | L5_vol_adjusted_return             |          31 |
| basis_premium_like | L1_cross_sectional_relative_return |          22 |
| basis_premium_like | L3_liquidity_tier_relative_return  |          20 |
| basis_premium_like | L0_raw_forward_return              |          19 |
| listing_age_like   | L3_liquidity_tier_relative_return  |           2 |
| volatility_like    | L3_liquidity_tier_relative_return  |           2 |
| listing_age_like   | L1_cross_sectional_relative_return |           1 |
| volatility_like    | L0_raw_forward_return              |           1 |
| volatility_like    | L1_cross_sectional_relative_return |           1 |

## Family Summary

| followup_family              |   rows |   semantic_pair_count |   motif_count |   skeleton_count |   source_seed_count |
|:-----------------------------|-------:|----------------------:|--------------:|-----------------:|--------------------:|
| basis_deep                   |    250 |                     5 |             6 |               88 |                   1 |
| oi_positioning_reserved_deep |    192 |                     4 |             5 |              120 |                   1 |
| listing_lifecycle_deep       |    109 |                     2 |             4 |               58 |                   1 |
| volatility_relative_deep     |    108 |                     5 |             4 |               45 |                   1 |

## Shard Plan

| company_numeric_shard   |   rows |   family_count |   semantic_pair_count |   motif_count |
|:------------------------|-------:|---------------:|----------------------:|--------------:|
| a7ls6_s000              |     64 |              1 |                     1 |             4 |
| a7ls6_s001              |     64 |              1 |                     1 |             4 |
| a7ls6_s002              |     64 |              1 |                     4 |             4 |
| a7ls6_s003              |     64 |              2 |                     3 |             4 |
| a7ls6_s004              |     64 |              1 |                     2 |             4 |
| a7ls6_s005              |     64 |              2 |                     2 |             2 |
| a7ls6_s006              |     64 |              1 |                     2 |             2 |
| a7ls6_s007              |     64 |              1 |                     2 |             5 |
| a7ls6_s008              |     64 |              2 |                     3 |             4 |
| a7ls6_s009              |     64 |              1 |                     4 |             3 |
| a7ls6_s010              |     19 |              1 |                     2 |             1 |

## Authorization

- Authorizes company numeric deep follow-up only if decision is PASS.
- Does not authorize formula search, large search, alpha proof, shadow, paper, or live.
- May is not used in generation, ranking, mutation, or selector scoring.
