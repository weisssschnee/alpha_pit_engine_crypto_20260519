# CRYPTO A7LS-5 FOLLOWUP QUEUE CONTRACT

Generated: 2026-06-05T11:07:51Z

## Decision

`PASS_A7LS5_FOLLOWUP_QUEUE_READY_FOR_COMPANY_NUMERIC_NO_SEARCH_AUTH`

## Summary

- seed_rows: 28
- full_generated_pool_rows: 531
- company_numeric_queue_rows: 531
- company_shard_count: 9
- followup_family_count: 4
- semantic_pair_count: 7
- motif_count: 3

## Seed Summary

| semantic_pair                     | label_family                       |   seed_rows |
|:----------------------------------|:-----------------------------------|------------:|
| low_prior_axes|basis_premium_like | L5_vol_adjusted_return             |          10 |
| basis_premium_like                | L5_vol_adjusted_return             |           8 |
| price_like                        | L5_vol_adjusted_return             |           2 |
| basis_premium_like                | L3_liquidity_tier_relative_return  |           2 |
| basis_premium_like                | L1_cross_sectional_relative_return |           1 |
| basis_premium_like                | L0_raw_forward_return              |           1 |
| listing_age_like                  | L3_liquidity_tier_relative_return  |           1 |
| listing_age_like                  | L1_cross_sectional_relative_return |           1 |
| open_interest_like                | L3_liquidity_tier_relative_return  |           1 |
| volatility_like                   | L3_liquidity_tier_relative_return  |           1 |

## Family Summary

| followup_family              |   rows |   semantic_pair_count |   motif_count |   skeleton_count |   source_seed_count |
|:-----------------------------|-------:|----------------------:|--------------:|-----------------:|--------------------:|
| basis_followup               |    249 |                     1 |             3 |               46 |                   1 |
| listing_lifecycle_followup   |    106 |                     2 |             2 |               66 |                   1 |
| oi_positioning_control_probe |     96 |                     2 |             2 |               60 |                   1 |
| volatility_relative_followup |     80 |                     2 |             2 |               39 |                   1 |

## Shard Plan

| company_numeric_shard   |   rows |   family_count |   semantic_pair_count |   motif_count |
|:------------------------|-------:|---------------:|----------------------:|--------------:|
| a7ls5_s000              |     64 |              1 |                     1 |             3 |
| a7ls5_s001              |     64 |              1 |                     1 |             3 |
| a7ls5_s002              |     64 |              1 |                     1 |             3 |
| a7ls5_s003              |     64 |              2 |                     3 |             3 |
| a7ls5_s004              |     64 |              1 |                     2 |             2 |
| a7ls5_s005              |     64 |              2 |                     4 |             2 |
| a7ls5_s006              |     64 |              1 |                     2 |             2 |
| a7ls5_s007              |     64 |              2 |                     3 |             2 |
| a7ls5_s008              |     19 |              1 |                     2 |             2 |

## Authorization

- Authorizes company numeric probe only if decision is PASS.
- Does not authorize formula search, large search, alpha proof, shadow, paper, or live.
- May is not used in generation or ranking.