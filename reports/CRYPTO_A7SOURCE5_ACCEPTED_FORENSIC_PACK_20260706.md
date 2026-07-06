# CRYPTO A7SOURCE5 Accepted Forensic Pack

Generated: `2026-07-06T04:41:04Z`

## Decision

`PASS_A7SOURCE5_ACCEPTED_FORENSIC_PACK_BUILT_NARROW_SURVIVOR_SET`

## Counts

- accepted_rows: `6`
- accepted_unique_blueprints: `6`
- reward_rows: `1196`
- accepted_rate: `0.005017`
- source_lag_pass_rows: `47`
- top_pair_share: `0.500`
- top_field_semantic_share: `0.333`
- top_skeleton_share: `0.167`
- narrow_flags: `none`

## Accepted Candidates

| blueprint_id                                         | semantic_pair               | motif                                         |   horizon_h | formula                                                                                                     |   train_sortino |   validation_sortino |   test_sortino |   recent_sortino |   min_oos_floor_sortino |   stress_sortino |   stress_floor_sortino |   recent_shuffle_control_ratio | source_lag_gate                  |
|:-----------------------------------------------------|:----------------------------|:----------------------------------------------|------------:|:------------------------------------------------------------------------------------------------------------|----------------:|---------------------:|---------------:|-----------------:|------------------------:|-----------------:|-----------------------:|-------------------------------:|:---------------------------------|
| a7search7_vp_a7search7_3ac1a9eafa18b95f_8_canonical  | funding_dense|open_interest | shadow_selected_rank_wrap_strict_validation   |           8 | CSRank(SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72))))) |        2.44731  |             15.8815  |       11.8745  |         18.3882  |                8.50321  |          6.50004 |               1.27322  |                       0.398843 | PASS_SOURCE_LAG_1H_2H_DIAGNOSTIC |
| a7search7_vp_a7search7_dec97465aedf9ce9_8_canonical  | open_interest|positioning   | positive_prior_safe_div_abs_strict_validation |           8 | SafeDiv(TSRank(open_interest_value_mean,240),Abs(TSRank(global_long_short_account_ratio_last,24)))          |        2.22076  |              7.78013 |        8.33728 |          4.08333 |                2.11649  |          8.84355 |               0.860626 |                       0.510444 | PASS_SOURCE_LAG_1H_2H_DIAGNOSTIC |
| a7search7_vp_a7search7_1c97b872a07e39dc_24_canonical | basis|open_interest         | positive_prior_signed_rank_strict_validation  |          24 | Mul(CSRank(CSRank(Delta(open_interest_value_mean,240))),Sign(Decay(mark_index_basis_bps,72)))               |        3.19775  |              3.43001 |        9.55872 |         12.0121  |                0.497889 |         10.7251  |               6.40622  |                       0.30089  | PASS_SOURCE_LAG_1H_2H_DIAGNOSTIC |
| a7search7_vp_a7search7_1e4d0178e8251298_24_canonical | basis|open_interest         | positive_prior_safe_div_abs_strict_validation |          24 | SafeDiv(Delta(open_interest_value_mean,240),Abs(Decay(mark_index_basis_bps,96)))                            |        0.984233 |              5.18092 |        5.15588 |         11.3385  |                0.488027 |          8.15858 |               3.42081  |                       0.243151 | PASS_SOURCE_LAG_1H_2H_DIAGNOSTIC |
| a7search7_vp_a7search7_58ba8c206cc57999_24_canonical | open_interest|premium       | positive_prior_signed_rank_strict_validation  |          24 | Mul(CSRank(Delta(open_interest_value_mean,240)),Sign(TSRank(premium_abs_state,504)))                        |        0.944611 |              4.20618 |        4.95853 |         12.6676  |                0.318659 |         13.8177  |               7.40948  |                       0.107433 | PASS_SOURCE_LAG_1H_2H_DIAGNOSTIC |
| a7search7_vp_a7search7_3e5555ac440970e9_24_canonical | basis|open_interest         | positive_prior_signed_rank_strict_validation  |          24 | Mul(CSRank(CSRank(Delta(open_interest_value_mean,240))),Sign(CSRank(Delta(mark_index_basis_bps,12))))       |        0.997506 |              4.20618 |        4.95853 |         12.6676  |                0.318659 |         13.8177  |               7.40948  |                       0.198853 | PASS_SOURCE_LAG_1H_2H_DIAGNOSTIC |

## Field Usage

| field                                | semantic      |   formula_count |   blueprint_count |
|:-------------------------------------|:--------------|----------------:|------------------:|
| open_interest_value_mean             | open_interest |               5 |                 5 |
| mark_index_basis_bps                 | basis         |               3 |                 3 |
| funding_rate_delta_state_24h         | funding_dense |               1 |                 1 |
| global_long_short_account_ratio_last | positioning   |               1 |                 1 |
| open_interest_value_last             | open_interest |               1 |                 1 |
| premium_abs_state                    | premium       |               1 |                 1 |

## Semantic Pair Summary

| semantic_pair               |   count |    share |
|:----------------------------|--------:|---------:|
| basis|open_interest         |       3 | 0.5      |
| funding_dense|open_interest |       1 | 0.166667 |
| open_interest|positioning   |       1 | 0.166667 |
| open_interest|premium       |       1 | 0.166667 |

## Motif Summary

| motif                                         |   count |    share |
|:----------------------------------------------|--------:|---------:|
| positive_prior_signed_rank_strict_validation  |       3 | 0.5      |
| positive_prior_safe_div_abs_strict_validation |       2 | 0.333333 |
| shadow_selected_rank_wrap_strict_validation   |       1 | 0.166667 |

## Source Lag Join

| blueprint_id                                         |   horizon_h |   sortino_original |   sortino_source_lag_1h |   sortino_source_lag_2h |   sortino_source_lag_4h |   nonoverlap_floor_sortino_original |   nonoverlap_floor_sortino_source_lag_1h |   nonoverlap_floor_sortino_source_lag_2h |
|:-----------------------------------------------------|------------:|-------------------:|------------------------:|------------------------:|------------------------:|------------------------------------:|-----------------------------------------:|-----------------------------------------:|
| a7search7_vp_a7search7_3ac1a9eafa18b95f_8_canonical  |           8 |            9.79819 |                 7.46497 |                 6.57066 |                 4.48947 |                             6.80552 |                                 4.56265  |                                 4.07075  |
| a7search7_vp_a7search7_dec97465aedf9ce9_8_canonical  |           8 |            6.87236 |                 5.959   |                 5.21804 |                 1.67162 |                             1.23647 |                                 0.700132 |                                 0.885184 |
| a7search7_vp_a7search7_1c97b872a07e39dc_24_canonical |          24 |           17.4998  |                17.5657  |                17.7609  |                18.0601  |                             9.53599 |                                10.0015   |                                10.9006   |
| a7search7_vp_a7search7_1e4d0178e8251298_24_canonical |          24 |           13.4426  |                13.5173  |                13.7724  |                13.9132  |                             6.64758 |                                 9.22056  |                                 8.3446   |
| a7search7_vp_a7search7_58ba8c206cc57999_24_canonical |          24 |           17.2523  |                17.1727  |                17.2623  |                17.2581  |                            12.1261  |                                10.7957   |                                11.5657   |
| a7search7_vp_a7search7_3e5555ac440970e9_24_canonical |          24 |           17.2523  |                17.1727  |                17.2623  |                17.2581  |                            12.1261  |                                10.7957   |                                11.5657   |

## Rejection Context

| hard_reject_reason                 |   count |
|:-----------------------------------|--------:|
| oos_control_dominated              |     989 |
| source_lag_required_not_proven     |     955 |
| oos_lag_stale_dominated            |     952 |
| oos_nonoverlap_floor_not_positive  |     931 |
| oos_net_mean_not_all_positive      |     820 |
| oos_shuffle_dominated              |     696 |
| stress_floor_not_positive          |     651 |
| shuffle_control_dominated_recent   |     507 |
| train_sortino_non_positive         |     395 |
| train_orientation_no_positive_edge |     394 |
| recent_sortino_non_positive        |     290 |
| train_sortino_overfit_gap          |      44 |
| missing_train_oos_consistency      |      16 |
| non_finite_diagnostic_composite    |      16 |

## Boundary

This pack is forensic validation evidence only. It does not authorize alpha proof, shadow, paper, or live.
