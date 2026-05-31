# CRYPTO A7FF-55D-S01P EXPANDED NUMERIC PROBE

Generated: 2026-05-31T09:15:29Z

## Decision

`PASS_A7FF55DS01P_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH`

A7FF-55D-S01P materializes the A7FF-7E selected blueprint queue and evaluates label response, controls, non-overlap statistics, and a dry portfolio marginal proxy. It is not formula search or alpha proof.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FF55DS01P_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH",
  "executes_generation": false,
  "executes_numeric_probe": true,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-31T09:15:29Z",
  "input_blueprint_count": 150,
  "label_response_rows": 1800,
  "labels": [
    "L0_raw_forward_return",
    "L1_cross_sectional_relative_return",
    "L3_liquidity_tier_relative_return"
  ],
  "materialized_activity_ok_count": 150,
  "non_l7_numeric_clue_rows": 7,
  "plan": {
    "authorizes_execution": false,
    "authorizes_replay": false,
    "authorizes_search": false,
    "hard_reject": [
      "label_family == L7_ranked_future_return for replay promotion",
      "diagnostic_only_low_activity family as primary replay row",
      "control_ratio >= 0.80",
      "decision not in NUMERIC_CLUE for non-L7 rows",
      "missing primary label quota",
      "top motif share > 0.30",
      "top semantic pair share > 0.30"
    ],
    "purpose": "repair selector target before any replay preflight",
    "score_inputs_allowed": [
      "non_l7_primary_label_indicator",
      "control_margin",
      "premay_split_stability",
      "one_bar_lag_survival",
      "nonoverlap_robustness",
      "cost_proxy_survival",
      "family_diversity_bonus",
      "motif_diversity_bonus"
    ],
    "score_inputs_forbidden": [
      "May pass/fail",
      "May return",
      "L7 ranked label as primary proof",
      "raw score without control margin",
      "stale selected queue from A7FF-54"
    ],
    "source": "A7FF-54",
    "stage": "A7FF-55",
    "target_queue": {
      "L5_allowed_only_after_primary_quota": true,
      "L7_diagnostic_only": true,
      "motif_min_count": 4,
      "primary_label_families_present": [
        "L0_raw_forward_return",
        "L1_cross_sectional_relative_return",
        "L3_liquidity_tier_relative_return"
      ],
      "primary_label_min_rows_total": 12,
      "selected_rows": "32 to 64",
      "semantic_pair_min_count": 4
    }
  },
  "portfolio_queue_count": 4,
  "queue_limit": 150,
  "queue_offset": 150,
  "queue_path": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ff53e_numeric_response_execution\\a7ff53e_numeric_queue.csv",
  "queue_total_rows": 1200,
  "rank_label_diagnostic_clue_rows": 0,
  "selected_portfolio_queue_count": 4,
  "stage": "A7FF-55D-S01P",
  "uses_may": false,
  "writes_control_detail": false
}
```

## Decision Counts

| decision                             | label_family                       |   count |
|:-------------------------------------|:-----------------------------------|--------:|
| A7FF55DS01P_NUMERIC_CLUE             | L0_raw_forward_return              |       3 |
| A7FF55DS01P_NUMERIC_CLUE             | L1_cross_sectional_relative_return |       1 |
| A7FF55DS01P_NUMERIC_CLUE             | L3_liquidity_tier_relative_return  |       3 |
| HOLD_A7FF55DS01P_CONTROL_DOMINATED   | L0_raw_forward_return              |     139 |
| HOLD_A7FF55DS01P_CONTROL_DOMINATED   | L1_cross_sectional_relative_return |     141 |
| HOLD_A7FF55DS01P_CONTROL_DOMINATED   | L3_liquidity_tier_relative_return  |     133 |
| HOLD_A7FF55DS01P_COST2_PROXY_FRAGILE | L1_cross_sectional_relative_return |       1 |
| HOLD_A7FF55DS01P_ONE_BAR_LAG_FRAGILE | L0_raw_forward_return              |       1 |
| HOLD_A7FF55DS01P_PRE_MAY_UNSTABLE    | L0_raw_forward_return              |     457 |
| HOLD_A7FF55DS01P_PRE_MAY_UNSTABLE    | L1_cross_sectional_relative_return |     457 |
| HOLD_A7FF55DS01P_PRE_MAY_UNSTABLE    | L3_liquidity_tier_relative_return  |     464 |

## Family Summary

| semantic_pair                    | decision                             |   count |
|:---------------------------------|:-------------------------------------|--------:|
| liquidity_like|price_return_like | A7FF55DS01P_NUMERIC_CLUE             |       7 |
| liquidity_like|price_return_like | HOLD_A7FF55DS01P_CONTROL_DOMINATED   |     413 |
| liquidity_like|price_return_like | HOLD_A7FF55DS01P_COST2_PROXY_FRAGILE |       1 |
| liquidity_like|price_return_like | HOLD_A7FF55DS01P_ONE_BAR_LAG_FRAGILE |       1 |
| liquidity_like|price_return_like | HOLD_A7FF55DS01P_PRE_MAY_UNSTABLE    |    1378 |

## Control Summary

| control              |   median_ratio |   max_ratio |   rows |
|:---------------------|---------------:|------------:|-------:|
| one_bar_lag          |       0.958936 |     280.364 |   5400 |
| same_family_placebo  |       0.504541 |    3365.73  |   5400 |
| sign_flip            |       1.00217  |     279.26  |   5400 |
| symbol_shuffle       |       0.735577 |    1927.35  |   5400 |
| time_shuffle         |       0.655852 |    2168.46  |   5400 |
| wrong_lag_future_24h |       2.46849  |    8182.54  |   5400 |
| wrong_lag_stale_168h |       0.820275 |    1585.89  |   5400 |

## Selected Portfolio Queue

| blueprint_id             | expression                                                                                            | semantic_pair                    | motif         | label_family                       |   label_horizon_h |   orientation_from_train |   premay_positive_split_count | premay_all_positive   |   control_ratio_premay_max |   one_bar_lag_recent_oriented | lag_ok   |   robust_median_tstat_floor |   robust_min_tstat_floor | robust_ok   |   cost2_recent_oriented |   cost5_recent_oriented |   cost10_recent_oriented |   avg_n_obs_recent | decision                 |   train_2024_n |   train_2024_mean_spread |   train_2024_tstat |   train_2024_nonoverlap_median_tstat |   train_2024_nonoverlap_min_tstat |   train_2024_positive_rate |   validation_2025H1_n |   validation_2025H1_mean_spread |   validation_2025H1_tstat |   validation_2025H1_nonoverlap_median_tstat |   validation_2025H1_nonoverlap_min_tstat |   validation_2025H1_positive_rate |   test_2025H2_n |   test_2025H2_mean_spread |   test_2025H2_tstat |   test_2025H2_nonoverlap_median_tstat |   test_2025H2_nonoverlap_min_tstat |   test_2025H2_positive_rate |   recent_oos_2026JanApr_n |   recent_oos_2026JanApr_mean_spread |   recent_oos_2026JanApr_tstat |   recent_oos_2026JanApr_nonoverlap_median_tstat |   recent_oos_2026JanApr_nonoverlap_min_tstat |   recent_oos_2026JanApr_positive_rate |   non_l7_bonus |   score_no_may | skeleton_key          |   finite_share |   nonzero_share |
|:-------------------------|:------------------------------------------------------------------------------------------------------|:---------------------------------|:--------------|:-----------------------------------|------------------:|-------------------------:|------------------------------:|:----------------------|---------------------------:|------------------------------:|:---------|----------------------------:|-------------------------:|:------------|------------------------:|------------------------:|-------------------------:|-------------------:|:-------------------------|---------------:|-------------------------:|-------------------:|-------------------------------------:|----------------------------------:|---------------------------:|----------------------:|--------------------------------:|--------------------------:|--------------------------------------------:|-----------------------------------------:|----------------------------------:|----------------:|--------------------------:|--------------------:|--------------------------------------:|-----------------------------------:|----------------------------:|--------------------------:|------------------------------------:|------------------------------:|------------------------------------------------:|---------------------------------------------:|--------------------------------------:|---------------:|---------------:|:----------------------|---------------:|----------------:|
| a7ff51e_8f78a0dc80a12fed | Sub(Delta(liquidity_rank_active_universe,1),CSRank(trade_return_1h))                                  | liquidity_like|price_return_like | sub           | L0_raw_forward_return              |                 4 |                        1 |                             3 | True                  |                   0.587026 |                   0.00030632  | True     |                    0.90629  |                -0.852334 | True        |              0.00068567 |             8.56703e-05 |              -0.00091433 |            95.4667 | A7FF55DS01P_NUMERIC_CLUE |            715 |              0.00210222  |            4.28741 |                             1.89826  |                          1.05189  |                   0.59021  |                   716 |                     0.000769475 |                  2.40776  |                                    1.18602  |                                 0.858609 |                          0.568436 |             716 |               0.00151057  |             4.18172 |                              1.99455  |                           1.37109  |                    0.614525 |                       716 |                          0.00108567 |                       1.56242 |                                         0.90629 |                                    -0.852334 |                              0.581006 |              1 |        6.49864 | skel_272ca17c2b96a62b |       0.827061 |        1        |
| a7ff51e_81ac5c644fbe93ea | Mul(Sub(liquidity_rank_active_universe,CSRank(trade_return_1h)),Sign(liquidity_rank_active_universe)) | liquidity_like|price_return_like | signed_spread | L1_cross_sectional_relative_return |                 1 |                        1 |                             3 | True                  |                   0.805801 |                   0.000324581 | True     |                    1.06986  |                 1.06986  | True        |              0.00015503 |            -0.00044497  |              -0.00144497 |            95.8667 | A7FF55DS01P_NUMERIC_CLUE |            719 |              0.000550971 |            2.33244 |                             2.33244  |                          2.33244  |                   0.581363 |                   719 |                     0.000149898 |                  1.06986  |                                    1.06986  |                                 1.06986  |                          0.521558 |             719 |               0.000198622 |             1.42438 |                              1.42438  |                           1.42438  |                    0.552156 |                       719 |                          0.00055503 |                       2.00531 |                                         2.00531 |                                     2.00531  |                              0.584145 |              1 |        6.1942  | skel_c4b94806dc7db90f |       0.827348 |        0.999765 |
| a7ff51e_fe3df4155b810948 | Sub(liquidity_rank_active_universe,CSRank(trade_return_1h))                                           | liquidity_like|price_return_like | sub           | L0_raw_forward_return              |                 1 |                        1 |                             3 | True                  |                   0.805801 |                   0.000324581 | True     |                    1.06986  |                 1.06986  | True        |              0.00015503 |            -0.00044497  |              -0.00144497 |            95.8667 | A7FF55DS01P_NUMERIC_CLUE |            719 |              0.000550971 |            2.33244 |                             2.33244  |                          2.33244  |                   0.581363 |                   719 |                     0.000149898 |                  1.06986  |                                    1.06986  |                                 1.06986  |                          0.521558 |             719 |               0.000198622 |             1.42438 |                              1.42438  |                           1.42438  |                    0.552156 |                       719 |                          0.00055503 |                       2.00531 |                                         2.00531 |                                     2.00531  |                              0.584145 |              1 |        6.1942  | skel_4ddceb2e74bece3a |       0.827348 |        0.999765 |
| a7ff51e_d260bd085c38b524 | Sub(Delta(liquidity_rank_active_universe,1),Delta(trade_return_1h,1))                                 | liquidity_like|price_return_like | sub           | L0_raw_forward_return              |                 4 |                        1 |                             3 | True                  |                   0.933613 |                   0.00131658  | True     |                    0.539089 |                -0.81741  | True        |              0.00049934 |            -0.00010066  |              -0.00110066 |            95.4667 | A7FF55DS01P_NUMERIC_CLUE |            715 |              0.000789161 |            1.70036 |                             0.872836 |                         -0.691539 |                   0.531469 |                   716 |                     0.00028204  |                  0.982727 |                                    0.539089 |                                -0.659107 |                          0.51676  |             716 |               0.00048118  |             1.35798 |                              0.713864 |                          -0.446772 |                    0.558659 |                       716 |                          0.00089934 |                       1.32622 |                                         1.09578 |                                    -0.81741  |                              0.536313 |              1 |        6.06639 | skel_6676b216f779b99e |       0.827061 |        0.997131 |

## Boundary

```text
No May/post-selection stress is used in scoring or authorization.
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
L7 ranked-return rows remain diagnostic-only and cannot promote without non-L7 support.
```
