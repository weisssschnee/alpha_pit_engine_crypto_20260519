# CRYPTO A7SOURCE6 Incremental Validation Pack

Generated: `2026-07-06T05:44:37Z`

## Decision

`PASS_A7SOURCE6_INCREMENTAL_EVIDENCE_FOUND`

This validates whether A7SOURCE5 accepted survivors add information beyond single-leg and nearby-operator baselines. It is not alpha proof and does not authorize shadow, paper, live, or production portfolio construction.

## Counts

- compressed_unique_blueprints: `6`
- validation_queue_rows: `81`
- reward_rows: `324`
- accepted_rows: `5`
- accepted_unique_blueprints: `5`
- eval_error_rows: `0`
- incremental_source_count: `5`
- non_unique_source_count: `0`
- canonical_failed_source_count: `1`

## Validation Group Summary

| validation_group   |   candidates |   gate_pass_rows |   accepted_unique |   max_recent_sortino |   max_min_oos_floor_sortino |
|:-------------------|-------------:|-----------------:|------------------:|---------------------:|----------------------------:|
| canonical          |            6 |                5 |                 5 |              18.3882 |                    8.6339   |
| single_leg         |           48 |                0 |                 0 |              14.873  |                    3.03433  |
| operator_neighbor  |           27 |                0 |                 0 |              17.0673 |                    0.513588 |

## Source Decisions

| source_blueprint_id                                  |   source_rank |   canonical_accepted_rows |   single_leg_accepted_rows |   operator_neighbor_accepted_rows |   accepted_rows | decision                              |
|:-----------------------------------------------------|--------------:|--------------------------:|---------------------------:|----------------------------------:|----------------:|:--------------------------------------|
| a7search7_vp_a7search7_1e4d0178e8251298_24_canonical |             4 |                         0 |                          0 |                                 0 |               0 | HOLD_CANONICAL_DID_NOT_REPASS         |
| a7search7_vp_a7search7_3ac1a9eafa18b95f_8_canonical  |             1 |                         1 |                          0 |                                 0 |               1 | PASS_INCREMENTAL_INTERACTION_EVIDENCE |
| a7search7_vp_a7search7_dec97465aedf9ce9_8_canonical  |             2 |                         1 |                          0 |                                 0 |               1 | PASS_INCREMENTAL_INTERACTION_EVIDENCE |
| a7search7_vp_a7search7_1c97b872a07e39dc_24_canonical |             3 |                         1 |                          0 |                                 0 |               1 | PASS_INCREMENTAL_INTERACTION_EVIDENCE |
| a7search7_vp_a7search7_58ba8c206cc57999_24_canonical |             5 |                         1 |                          0 |                                 0 |               1 | PASS_INCREMENTAL_INTERACTION_EVIDENCE |
| a7search7_vp_a7search7_3e5555ac440970e9_24_canonical |             6 |                         1 |                          0 |                                 0 |               1 | PASS_INCREMENTAL_INTERACTION_EVIDENCE |

## Accepted Validation Rows

| source_blueprint_id                                  | validation_group   | blueprint_id                                                                |   horizon_h |   rows |   train_sortino |   validation_sortino |   test_sortino |   recent_sortino |   min_oos_floor_sortino |   stress_floor_sortino |   recent_shuffle_control_ratio | formula                                                                                                     |
|:-----------------------------------------------------|:-------------------|:----------------------------------------------------------------------------|------------:|-------:|----------------:|---------------------:|---------------:|-----------------:|------------------------:|-----------------------:|-------------------------------:|:------------------------------------------------------------------------------------------------------------|
| a7search7_vp_a7search7_3ac1a9eafa18b95f_8_canonical  | canonical          | a7search6_vp_a7search7_vp_a7search7_3ac1a9eafa18b95f_8_canonical_canonical  |           8 |      1 |        2.44731  |             15.8815  |       11.8745  |         18.3882  |                8.50321  |               1.27322  |                      0.398843  | CSRank(SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72))))) |
| a7search7_vp_a7search7_dec97465aedf9ce9_8_canonical  | canonical          | a7search6_vp_a7search7_vp_a7search7_dec97465aedf9ce9_8_canonical_canonical  |           8 |      1 |        2.22076  |              7.78013 |        8.33728 |          4.08333 |                2.11649  |               0.860626 |                      0.880889  | SafeDiv(TSRank(open_interest_value_mean,240),Abs(TSRank(global_long_short_account_ratio_last,24)))          |
| a7search7_vp_a7search7_1c97b872a07e39dc_24_canonical | canonical          | a7search6_vp_a7search7_vp_a7search7_1c97b872a07e39dc_24_canonical_canonical |          24 |      1 |        3.19775  |              3.43001 |        9.55872 |         12.0121  |                0.497889 |               6.40622  |                      0.0730941 | Mul(CSRank(CSRank(Delta(open_interest_value_mean,240))),Sign(Decay(mark_index_basis_bps,72)))               |
| a7search7_vp_a7search7_3e5555ac440970e9_24_canonical | canonical          | a7search6_vp_a7search7_vp_a7search7_3e5555ac440970e9_24_canonical_canonical |          24 |      1 |        0.997506 |              4.20618 |        4.95853 |         12.6676  |                0.318659 |               7.40948  |                      0.488939  | Mul(CSRank(CSRank(Delta(open_interest_value_mean,240))),Sign(CSRank(Delta(mark_index_basis_bps,12))))       |
| a7search7_vp_a7search7_58ba8c206cc57999_24_canonical | canonical          | a7search6_vp_a7search7_vp_a7search7_58ba8c206cc57999_24_canonical_canonical |          24 |      1 |        0.944611 |              4.20618 |        4.95853 |         12.6676  |                0.318659 |               7.40948  |                      0.107433  | Mul(CSRank(Delta(open_interest_value_mean,240)),Sign(TSRank(premium_abs_state,504)))                        |

## Field Timing Risk Summary

| field_family        | timing_risk_note                                          |   fields |   source_blueprints |
|:--------------------|:----------------------------------------------------------|---------:|--------------------:|
| open_interest       | requires OI snapshot timestamp and no same-bar fill proof |        2 |                   6 |
| basis_premium       | mark/index/premium bar-close alignment proof required     |        2 |                   4 |
| event_dense_funding | requires funding publication timestamp / ffill-age proof  |        1 |                   1 |
| positioning         | requires account/position ratio publication lag proof     |        1 |                   1 |

## Rejection Summary

`<empty>`

## Boundary

- This stage can authorize seed triage only.
- It does not authorize alpha proof, shadow, paper, live, or deployment.
