# CRYPTO A7FF-CORE16 PRIMITIVE REPLAY-STABILITY ATLAS

Generated: 2026-06-01T08:16:46Z

## Decision

`HOLD_A7FFCORE16_PRIMITIVE_ATLAS_INSUFFICIENT`

A7FF-CORE16 rebuilds an objective atlas from primitive response and replay-stability evidence. It does not execute replay, formula generation, search, promotion, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "atlas_candidate_count": 2,
  "authorizes_alpha_proof": false,
  "authorizes_core17": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "atlas_candidate_count_lt_64",
    "field_family_count_lt_6",
    "transform_count_lt_5",
    "top_family_share_gt_30pct"
  ],
  "decision": "HOLD_A7FFCORE16_PRIMITIVE_ATLAS_INSUFFICIENT",
  "executes_replay": false,
  "executes_search": false,
  "field_family_count": 1,
  "generated_at": "2026-06-01T08:16:46Z",
  "next_allowed": "A7FF-CORE16R primitive atlas supply repair",
  "source_decision": "PASS_A7FFCORE15YR_SURFACE_FAILURE_REPAIR_READY_FOR_CORE16_ATLAS",
  "source_stage": "A7FF-CORE15YR",
  "stage": "A7FF-CORE16",
  "top_family_share": 1.0,
  "transform_count": 1
}
```

## Field Type By Label/Horizon Stability

| field_family              | label_family                       |   rows |   strict_primitive_count |   relaxed_primitive_count |   atlas_candidate_count |   median_control_ratio |
|:--------------------------|:-----------------------------------|-------:|-------------------------:|--------------------------:|------------------------:|-----------------------:|
| basis_premium             | L0_raw_forward_return              |     45 |                        1 |                         7 |                       1 |                6.6826  |
| basis_premium             | L1_cross_sectional_relative_return |     45 |                        1 |                         7 |                       1 |                6.6826  |
| basis_premium             | L7_ranked_future_return            |     45 |                        1 |                        10 |                       0 |                2.28817 |
| price_return              | L7_ranked_future_return            |     18 |                        4 |                         4 |                       0 |                6.21288 |
| volatility                | L7_ranked_future_return            |     18 |                        4 |                         4 |                       0 |                1.40169 |
| taker_flow                | L7_ranked_future_return            |     18 |                        0 |                         3 |                       0 |                2.74249 |
| price_return              | L0_raw_forward_return              |     18 |                        0 |                         2 |                       0 |               40.1024  |
| price_return              | L1_cross_sectional_relative_return |     18 |                        0 |                         2 |                       0 |               40.1024  |
| funding                   | L0_raw_forward_return              |     27 |                        0 |                         0 |                       0 |               12.3662  |
| funding                   | L1_cross_sectional_relative_return |     27 |                        0 |                         0 |                       0 |               12.3662  |
| funding                   | L7_ranked_future_return            |     27 |                        0 |                         0 |                       0 |                1.07473 |
| liquidity                 | L0_raw_forward_return              |     27 |                        0 |                         0 |                       0 |               12.6964  |
| liquidity                 | L1_cross_sectional_relative_return |     27 |                        0 |                         0 |                       0 |               12.6964  |
| liquidity                 | L7_ranked_future_return            |     27 |                        0 |                         0 |                       0 |                4.74644 |
| open_interest             | L0_raw_forward_return              |     27 |                        0 |                         0 |                       0 |               19.6493  |
| open_interest             | L1_cross_sectional_relative_return |     27 |                        0 |                         0 |                       0 |               19.6493  |
| open_interest             | L7_ranked_future_return            |     27 |                        0 |                         0 |                       0 |                8.1372  |
| open_interest_interaction | L0_raw_forward_return              |      9 |                        0 |                         0 |                       0 |               17.2277  |
| open_interest_interaction | L1_cross_sectional_relative_return |      9 |                        0 |                         0 |                       0 |               17.2277  |
| open_interest_interaction | L7_ranked_future_return            |      9 |                        0 |                         0 |                       0 |                3.52762 |
| positioning               | L0_raw_forward_return              |     27 |                        0 |                         0 |                       0 |                8.81808 |
| positioning               | L1_cross_sectional_relative_return |     27 |                        0 |                         0 |                       0 |                8.81808 |
| positioning               | L7_ranked_future_return            |     27 |                        0 |                         0 |                       0 |                4.29308 |
| taker_flow                | L0_raw_forward_return              |     18 |                        0 |                         0 |                       0 |               12.0454  |
| taker_flow                | L1_cross_sectional_relative_return |     18 |                        0 |                         0 |                       0 |               12.0454  |
| volatility                | L0_raw_forward_return              |     18 |                        0 |                         0 |                       0 |               14.3634  |
| volatility                | L1_cross_sectional_relative_return |     18 |                        0 |                         0 |                       0 |               14.3634  |

## Candidate Objective Atlas

| field_name           | field_family   | source_family      | feature_class   | transform   | label_family                       |   label_horizon_h |   orientation_from_train |   premay_positive_split_count | premay_all_positive   |   control_ratio_premay_max |   one_bar_lag_recent_oriented | lag_ok   | decision                           |   train_2024_n |   train_2024_mean_spread |   train_2024_tstat |   train_2024_nonoverlap_median_tstat |   train_2024_nonoverlap_min_tstat |   train_2024_positive_rate |   validation_2025H1_n |   validation_2025H1_mean_spread |   validation_2025H1_tstat |   validation_2025H1_nonoverlap_median_tstat |   validation_2025H1_nonoverlap_min_tstat |   validation_2025H1_positive_rate |   test_2025H2_n |   test_2025H2_mean_spread |   test_2025H2_tstat |   test_2025H2_nonoverlap_median_tstat |   test_2025H2_nonoverlap_min_tstat |   test_2025H2_positive_rate |   recent_oos_2026JanApr_n |   recent_oos_2026JanApr_mean_spread |   recent_oos_2026JanApr_tstat |   recent_oos_2026JanApr_nonoverlap_median_tstat |   recent_oos_2026JanApr_nonoverlap_min_tstat |   recent_oos_2026JanApr_positive_rate |   avg_n_obs_recent |   error | lag_ok_bool   | premay_all_positive_bool   | strict_primitive   | relaxed_primitive   | non_l7   | atlas_candidate   | objective_id                                                                              |
|:---------------------|:---------------|:-------------------|:----------------|:------------|:-----------------------------------|------------------:|-------------------------:|------------------------------:|:----------------------|---------------------------:|------------------------------:|:---------|:-----------------------------------|---------------:|-------------------------:|-------------------:|-------------------------------------:|----------------------------------:|---------------------------:|----------------------:|--------------------------------:|--------------------------:|--------------------------------------------:|-----------------------------------------:|----------------------------------:|----------------:|--------------------------:|--------------------:|--------------------------------------:|-----------------------------------:|----------------------------:|--------------------------:|------------------------------------:|------------------------------:|------------------------------------------------:|---------------------------------------------:|--------------------------------------:|-------------------:|--------:|:--------------|:---------------------------|:-------------------|:--------------------|:---------|:------------------|:------------------------------------------------------------------------------------------|
| mark_index_basis_bps | basis_premium  | mark_index_premium | raw_source      | delta_24h   | L0_raw_forward_return              |                 1 |                       -1 |                             3 | True                  |                   0.785786 |                   0.000478731 | True     | A7AA1_PRIMITIVE_RESPONSE_CANDIDATE |            695 |             -0.000382177 |           -2.07024 |                             -2.07024 |                          -2.07024 |                   0.444604 |                   719 |                     -0.00059771 |                  -5.66206 |                                    -5.66206 |                                 -5.66206 |                          0.383866 |             719 |               -0.00114686 |            -7.28676 |                              -7.28676 |                           -7.28676 |                    0.346314 |                       719 |                         -0.00133079 |                      -4.09822 |                                        -4.09822 |                                     -4.09822 |                              0.443672 |            95.8667 |     nan | True          | True                       | True               | True                | True     | True              | core16_basis_premium_mark_index_basis_bps_delta_24h_L0_raw_forward_return_h1              |
| mark_index_basis_bps | basis_premium  | mark_index_premium | raw_source      | delta_24h   | L1_cross_sectional_relative_return |                 1 |                       -1 |                             3 | True                  |                   0.785786 |                   0.000478731 | True     | A7AA1_PRIMITIVE_RESPONSE_CANDIDATE |            695 |             -0.000382177 |           -2.07024 |                             -2.07024 |                          -2.07024 |                   0.444604 |                   719 |                     -0.00059771 |                  -5.66206 |                                    -5.66206 |                                 -5.66206 |                          0.383866 |             719 |               -0.00114686 |            -7.28676 |                              -7.28676 |                           -7.28676 |                    0.346314 |                       719 |                         -0.00133079 |                      -4.09822 |                                        -4.09822 |                                     -4.09822 |                              0.443672 |            95.8667 |     nan | True          | True                       | True               | True                | True     | True              | core16_basis_premium_mark_index_basis_bps_delta_24h_L1_cross_sectional_relative_return_h1 |

## Replay Surface Family Map

| semantic_bucket                      | motif_bucket       |   surface_rows |   surface_candidates |   median_surface_score |   median_control_ratio |
|:-------------------------------------|:-------------------|---------------:|---------------------:|-----------------------:|-----------------------:|
| liquidity_like\|volatility_like      | liquidity_shock    |             52 |                    3 |               1.05825  |                1.64444 |
| taker_flow_like\|basis_premium_like  | gated_sign         |             38 |                    1 |              -0.713828 |                2.99934 |
| open_interest_like\|positioning_like | delta_x_divergence |             52 |                    0 |              -1.28168  |                3.1955  |
| taker_flow_like\|open_interest_like  | flow_x_leverage    |             48 |                    0 |              -1.11587  |                2.67225 |
| liquidity_like                       | single             |             32 |                    0 |              -2.14533  |                4.05275 |
| open_interest_like                   | single             |              7 |                    0 |              -1.59898  |                3.9522  |
