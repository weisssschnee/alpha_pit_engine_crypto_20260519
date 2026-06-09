# CRYPTO A7LS29 Productive Family Queue 20260609

## Decision

`PASS_A7LS29_PRODUCTIVE_FAMILY_QUEUE_BUILT_NO_NUMERIC_EXECUTION`

A7LS29 compiles a larger queue from A7LS28B productive non-L7 families. It consumes A7LS-FIELD-GATE-1 registry and adds explicit `skeleton_key` values so the portfolio proxy does not collapse the selected queue to one item per shard.

## Counts

- input_non_l7_rows: 3847
- strong_parent_rows: 3134
- candidate_rows: 129226
- queue_rows: 6144
- rows_per_shard: 512
- shard_count: 12
- skeleton_count: 241
- field_gate1_field_count: 17

## Family Coverage

| semantic_pair                                          |   target_rows |   candidate_rows |   selected_rows |   motif_count |   skeleton_count |
|:-------------------------------------------------------|--------------:|-----------------:|----------------:|--------------:|-----------------:|
| basis_premium_like\|positioning_like                   |          2304 |            76485 |            2304 |             5 |              103 |
| open_interest_like\|positioning_like\|regime_state     |          1536 |            17328 |            1536 |             1 |               17 |
| open_interest_like\|positioning_like\|listing_age_like |          1024 |            10305 |            1024 |             1 |               63 |
| basis_premium_like\|age_x_volatility\|positioning_like |           768 |            16584 |             768 |             2 |               35 |
| open_interest_like\|positioning_like                   |           512 |             8524 |             512 |             2 |               23 |

## Mutation Summary

| mutation_kind        |   rows |
|:---------------------|-------:|
| window_grid          |   4000 |
| same_type_field_swap |   1116 |
| wrapper_probe        |    759 |
| direction_probe      |     96 |
| magnitude_probe      |     94 |
| parent_identity      |     79 |

## Family Summary

| semantic_pair                                          | motif               | parent_label_family                |   rows |
|:-------------------------------------------------------|:--------------------|:-----------------------------------|-------:|
| open_interest_like\|positioning_like\|regime_state     | seed_gated_sign     | L3_liquidity_tier_relative_return  |   1536 |
| open_interest_like\|positioning_like\|listing_age_like | seed_sub            | L3_liquidity_tier_relative_return  |    878 |
| basis_premium_like\|positioning_like                   | spread_rank         | L3_liquidity_tier_relative_return  |    382 |
| basis_premium_like\|positioning_like                   | mean_reversion_gate | L5_vol_adjusted_return             |    370 |
| basis_premium_like\|positioning_like                   | sub                 | L5_vol_adjusted_return             |    309 |
| basis_premium_like\|positioning_like                   | signed_spread       | L3_liquidity_tier_relative_return  |    300 |
| open_interest_like\|positioning_like                   | smooth_mul          | L5_vol_adjusted_return             |    241 |
| basis_premium_like\|age_x_volatility\|positioning_like | seed_mul            | L1_cross_sectional_relative_return |    194 |
| basis_premium_like\|positioning_like                   | safe_div_abs        | L3_liquidity_tier_relative_return  |    161 |
| basis_premium_like\|age_x_volatility\|positioning_like | seed_sub            | L0_raw_forward_return              |    139 |
| basis_premium_like\|age_x_volatility\|positioning_like | seed_sub            | L3_liquidity_tier_relative_return  |    126 |
| basis_premium_like\|positioning_like                   | safe_div_abs        | L1_cross_sectional_relative_return |    126 |
| basis_premium_like\|age_x_volatility\|positioning_like | seed_mul            | L3_liquidity_tier_relative_return  |    126 |
| basis_premium_like\|positioning_like                   | spread_rank         | L1_cross_sectional_relative_return |    125 |
| basis_premium_like\|age_x_volatility\|positioning_like | seed_sub            | L1_cross_sectional_relative_return |    119 |
| open_interest_like\|positioning_like\|listing_age_like | seed_sub            | L0_raw_forward_return              |    112 |
| basis_premium_like\|positioning_like                   | safe_div_abs        | L5_vol_adjusted_return             |    112 |
| basis_premium_like\|positioning_like                   | signed_spread       | L0_raw_forward_return              |    107 |
| basis_premium_like\|positioning_like                   | mean_reversion_gate | L3_liquidity_tier_relative_return  |     91 |
| open_interest_like\|positioning_like                   | safe_div_abs        | L1_cross_sectional_relative_return |     86 |
| open_interest_like\|positioning_like                   | safe_div_abs        | L5_vol_adjusted_return             |     75 |
| open_interest_like\|positioning_like                   | safe_div_abs        | L0_raw_forward_return              |     66 |
| basis_premium_like\|age_x_volatility\|positioning_like | seed_mul            | L0_raw_forward_return              |     64 |
| basis_premium_like\|positioning_like                   | spread_rank         | L5_vol_adjusted_return             |     62 |
| basis_premium_like\|positioning_like                   | safe_div_abs        | L0_raw_forward_return              |     62 |
| open_interest_like\|positioning_like\|listing_age_like | seed_sub            | L1_cross_sectional_relative_return |     34 |
| basis_premium_like\|positioning_like                   | spread_rank         | L0_raw_forward_return              |     34 |
| basis_premium_like\|positioning_like                   | signed_spread       | L1_cross_sectional_relative_return |     32 |
| basis_premium_like\|positioning_like                   | signed_spread       | L5_vol_adjusted_return             |     31 |
| open_interest_like\|positioning_like                   | safe_div_abs        | L3_liquidity_tier_relative_return  |     29 |
| open_interest_like\|positioning_like                   | smooth_mul          | L1_cross_sectional_relative_return |     15 |

## Outputs

- `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7ls29_productive_family_queue_20260609\a7ls29_productive_family_queue.csv`
- `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7ls29_productive_family_queue_20260609\a7ls29_shard_plan.csv`
- `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7ls29_productive_family_queue_20260609\a7ls29_family_coverage.csv`
- `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7ls29_productive_family_queue_20260609\a7ls29_family_summary.csv`
- `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7ls29_productive_family_queue_20260609\a7ls29_mutation_summary.csv`
- `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7ls29_productive_family_queue_20260609\a7ls29_manifest.json`
