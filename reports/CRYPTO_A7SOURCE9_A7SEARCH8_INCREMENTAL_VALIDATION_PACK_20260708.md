# CRYPTO A7SOURCE6 Incremental Validation Pack

Generated: `2026-07-07T18:33:26Z`

## Decision

`PASS_A7SOURCE6_INCREMENTAL_EVIDENCE_FOUND`

This validates whether A7SOURCE5 accepted survivors add information beyond single-leg and nearby-operator baselines. It is not alpha proof and does not authorize shadow, paper, live, or production portfolio construction.

## Counts

- compressed_unique_blueprints: `11`
- validation_queue_rows: `146`
- reward_rows: `584`
- accepted_rows: `11`
- accepted_unique_blueprints: `11`
- eval_error_rows: `0`
- incremental_source_count: `11`
- non_unique_source_count: `0`
- canonical_failed_source_count: `0`

## Validation Group Summary

| validation_group   |   candidates |   gate_pass_rows |   accepted_unique |   max_recent_sortino |   max_min_oos_floor_sortino |
|:-------------------|-------------:|-----------------:|------------------:|---------------------:|----------------------------:|
| canonical          |           11 |               11 |                11 |              18.3882 |                     8.6339  |
| single_leg         |           88 |                0 |                 0 |              14.873  |                     3.03433 |
| operator_neighbor  |           47 |                0 |                 0 |              17.0673 |                     0.59982 |

## Source Decisions

| source_blueprint_id        |   source_rank |   canonical_accepted_rows |   single_leg_accepted_rows |   operator_neighbor_accepted_rows |   accepted_rows | decision                              |
|:---------------------------|--------------:|--------------------------:|---------------------------:|----------------------------------:|----------------:|:--------------------------------------|
| a7search7_9168babaa32dc76c |             1 |                         1 |                          0 |                                 0 |               1 | PASS_INCREMENTAL_INTERACTION_EVIDENCE |
| a7search7_1579560a060d20ec |             2 |                         1 |                          0 |                                 0 |               1 | PASS_INCREMENTAL_INTERACTION_EVIDENCE |
| a7search7_fa2bcb9f82277249 |             3 |                         1 |                          0 |                                 0 |               1 | PASS_INCREMENTAL_INTERACTION_EVIDENCE |
| a7search7_f57e92c650f903b6 |             4 |                         1 |                          0 |                                 0 |               1 | PASS_INCREMENTAL_INTERACTION_EVIDENCE |
| a7search7_4e22e196bfeb8bce |             5 |                         1 |                          0 |                                 0 |               1 | PASS_INCREMENTAL_INTERACTION_EVIDENCE |
| a7search7_52353a2ad0ece8e8 |             6 |                         1 |                          0 |                                 0 |               1 | PASS_INCREMENTAL_INTERACTION_EVIDENCE |
| a7search7_e7180b1ba6a1df1a |             7 |                         1 |                          0 |                                 0 |               1 | PASS_INCREMENTAL_INTERACTION_EVIDENCE |
| a7search7_d404a68b39d27dbd |             8 |                         1 |                          0 |                                 0 |               1 | PASS_INCREMENTAL_INTERACTION_EVIDENCE |
| a7search7_124582cf9a6d54a0 |             9 |                         1 |                          0 |                                 0 |               1 | PASS_INCREMENTAL_INTERACTION_EVIDENCE |
| a7search7_8ecc4a9a053a0d59 |            10 |                         1 |                          0 |                                 0 |               1 | PASS_INCREMENTAL_INTERACTION_EVIDENCE |
| a7search7_b2e42dec52899bd0 |            11 |                         1 |                          0 |                                 0 |               1 | PASS_INCREMENTAL_INTERACTION_EVIDENCE |

## Accepted Validation Rows

| source_blueprint_id        | validation_group   | blueprint_id                                      |   horizon_h |   rows |   train_sortino |   validation_sortino |   test_sortino |   recent_sortino |   min_oos_floor_sortino |   stress_floor_sortino |   recent_shuffle_control_ratio | formula                                                                                                             |
|:---------------------------|:-------------------|:--------------------------------------------------|------------:|-------:|----------------:|---------------------:|---------------:|-----------------:|------------------------:|-----------------------:|-------------------------------:|:--------------------------------------------------------------------------------------------------------------------|
| a7search7_1579560a060d20ec | canonical          | a7search6_vp_a7search7_1579560a060d20ec_canonical |           8 |      1 |        2.44731  |             15.8815  |       11.8745  |         18.3882  |                8.50321  |               1.27322  |                      0.355241  | CSRank(SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72)))))         |
| a7search7_9168babaa32dc76c | canonical          | a7search6_vp_a7search7_9168babaa32dc76c_canonical |           8 |      1 |        2.44731  |             15.8815  |       11.8745  |         18.3882  |                8.50321  |               1.27322  |                      0.398843  | CSRank(CSRank(SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72)))))) |
| a7search7_f57e92c650f903b6 | canonical          | a7search6_vp_a7search7_f57e92c650f903b6_canonical |           8 |      1 |        2.22076  |              7.78013 |        8.33728 |          4.08333 |                2.11649  |               0.860626 |                      0.510444  | CSRank(SafeDiv(TSRank(open_interest_value_mean,240),Abs(TSRank(global_long_short_account_ratio_last,24))))          |
| a7search7_fa2bcb9f82277249 | canonical          | a7search6_vp_a7search7_fa2bcb9f82277249_canonical |           8 |      1 |        2.22076  |              7.78013 |        8.33728 |          4.08333 |                2.11649  |               0.860626 |                      0.458351  | SafeDiv(TSRank(open_interest_value_mean,240),Abs(TSRank(global_long_short_account_ratio_last,24)))                  |
| a7search7_4e22e196bfeb8bce | canonical          | a7search6_vp_a7search7_4e22e196bfeb8bce_canonical |          24 |      1 |        1.89712  |              3.60958 |        5.47024 |         16.2218  |                1.06354  |               8.19878  |                      0.58279   | SafeDiv(Delta(open_interest_value_last,240),Abs(ZScore(Mean(global_long_short_account_ratio_last,96))))             |
| a7search7_52353a2ad0ece8e8 | canonical          | a7search6_vp_a7search7_52353a2ad0ece8e8_canonical |          24 |      1 |        3.19775  |              3.43001 |        9.55872 |         12.0121  |                0.497889 |               6.40622  |                      0.28347   | CSRank(Mul(CSRank(CSRank(Delta(open_interest_value_mean,240))),Sign(Decay(mark_index_basis_bps,72))))               |
| a7search7_e7180b1ba6a1df1a | canonical          | a7search6_vp_a7search7_e7180b1ba6a1df1a_canonical |          24 |      1 |        3.19775  |              3.43001 |        9.55872 |         12.0121  |                0.497889 |               6.40622  |                      0.240769  | Mul(CSRank(CSRank(Delta(open_interest_value_mean,240))),Sign(Decay(mark_index_basis_bps,72)))                       |
| a7search7_124582cf9a6d54a0 | canonical          | a7search6_vp_a7search7_124582cf9a6d54a0_canonical |          24 |      1 |        0.997506 |              4.20618 |        4.95853 |         12.6676  |                0.318659 |               7.40948  |                      0.0671119 | CSRank(Mul(CSRank(CSRank(Delta(open_interest_value_mean,240))),Sign(CSRank(Delta(mark_index_basis_bps,12)))))       |
| a7search7_8ecc4a9a053a0d59 | canonical          | a7search6_vp_a7search7_8ecc4a9a053a0d59_canonical |          24 |      1 |        0.944611 |              4.20618 |        4.95853 |         12.6676  |                0.318659 |               7.40948  |                      0.127296  | CSRank(Mul(CSRank(Delta(open_interest_value_mean,240)),Sign(TSRank(premium_abs_state,504))))                        |
| a7search7_b2e42dec52899bd0 | canonical          | a7search6_vp_a7search7_b2e42dec52899bd0_canonical |          24 |      1 |        0.944611 |              4.20618 |        4.95853 |         12.6676  |                0.318659 |               7.40948  |                      0.497411  | Mul(CSRank(Delta(open_interest_value_mean,240)),Sign(TSRank(premium_abs_state,504)))                                |
| a7search7_d404a68b39d27dbd | canonical          | a7search6_vp_a7search7_d404a68b39d27dbd_canonical |          24 |      1 |        0.997506 |              4.20618 |        4.95853 |         12.6676  |                0.318659 |               7.40948  |                      0.177144  | Mul(CSRank(CSRank(Delta(open_interest_value_mean,240))),Sign(CSRank(Delta(mark_index_basis_bps,12))))               |

## Field Timing Risk Summary

| field_family        | timing_risk_note                                          |   fields |   source_blueprints |
|:--------------------|:----------------------------------------------------------|---------:|--------------------:|
| open_interest       | requires OI snapshot timestamp and no same-bar fill proof |        2 |                  11 |
| basis_premium       | mark/index/premium bar-close alignment proof required     |        2 |                   6 |
| positioning         | requires account/position ratio publication lag proof     |        1 |                   3 |
| event_dense_funding | requires funding publication timestamp / ffill-age proof  |        1 |                   2 |

## Rejection Summary

`<empty>`

## Boundary

- This stage can authorize seed triage only.
- It does not authorize alpha proof, shadow, paper, live, or deployment.
