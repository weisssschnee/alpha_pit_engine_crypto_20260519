# CRYPTO A7FF-25R3S04 EXPANDED NUMERIC PROBE

Generated: 2026-05-30T08:35:14Z

## Decision

`PASS_A7FF25R3S04_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH`

A7FF-25R3S04 materializes the A7FF-7E selected blueprint queue and evaluates label response, controls, non-overlap statistics, and a dry portfolio marginal proxy. It is not formula search or alpha proof.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FF25R3S04_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH",
  "executes_generation": false,
  "executes_numeric_probe": true,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T08:35:14Z",
  "input_blueprint_count": 200,
  "label_response_rows": 3320,
  "materialized_activity_ok_count": 166,
  "non_l7_numeric_clue_rows": 98,
  "plan": {
    "control_probe_cap": 256,
    "controls": [
      "wrong_lag_future",
      "wrong_lag_stale",
      "time_shuffle",
      "symbol_shuffle",
      "sign_flip",
      "same_family_placebo"
    ],
    "deep_audit_cap": 64,
    "fast_numeric_probe_cap": 256,
    "horizons": [
      "1h",
      "4h",
      "8h",
      "24h"
    ],
    "input_blueprint_source": "runtime/a7ff7e_expanded_derivation_probe_contract/a7ff7e_expanded_blueprint_pool.csv",
    "labels": [
      "L0_raw_forward_return",
      "L1_cross_sectional_relative_return",
      "L3_liquidity_tier_relative_return",
      "L5_vol_adjusted_return",
      "L7_ranked_future_return_diagnostic_only"
    ],
    "materialize_cap": 384,
    "portfolio_marginal_probe_cap": 128,
    "promotion_blockers": [
      "L7-only cannot promote",
      "control_ratio >= 1.0 blocks",
      "single semantic_pair > 35pct blocks",
      "single skeleton > 15pct blocks",
      "numeric replay required before any search authorization"
    ],
    "required_outputs": [
      "a7ff8_materialization_metrics.csv",
      "a7ff8_label_response_metrics.csv",
      "a7ff8_control_dominance_metrics.csv",
      "a7ff8_nonoverlap_stats.csv",
      "a7ff8_portfolio_marginal_proxy.csv",
      "a7ff8_decision_record.json"
    ],
    "selected_blueprints": 384,
    "stage": "A7FF-8",
    "status": "contract_only_not_executed"
  },
  "portfolio_queue_count": 71,
  "queue_limit": 200,
  "queue_offset": 0,
  "queue_path": "D:\\HermesWorker\\GDrive\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519_remote\\runtime\\a7ff24r_dry_generation_plan\\a7ff24r_company_shard_04_queue.csv",
  "queue_total_rows": 200,
  "rank_label_diagnostic_clue_rows": 112,
  "selected_portfolio_queue_count": 8,
  "stage": "A7FF-25R3S04",
  "uses_may": false
}
```

## Decision Counts

```text
                              decision                       label_family  count
              A7FF25R3S04_NUMERIC_CLUE              L0_raw_forward_return     24
              A7FF25R3S04_NUMERIC_CLUE L1_cross_sectional_relative_return     23
              A7FF25R3S04_NUMERIC_CLUE  L3_liquidity_tier_relative_return     26
              A7FF25R3S04_NUMERIC_CLUE             L5_vol_adjusted_return     25
A7FF25R3S04_RANK_LABEL_DIAGNOSTIC_CLUE            L7_ranked_future_return    112
    HOLD_A7FF25R3S04_CONTROL_DOMINATED              L0_raw_forward_return    200
    HOLD_A7FF25R3S04_CONTROL_DOMINATED L1_cross_sectional_relative_return    201
    HOLD_A7FF25R3S04_CONTROL_DOMINATED  L3_liquidity_tier_relative_return    183
    HOLD_A7FF25R3S04_CONTROL_DOMINATED             L5_vol_adjusted_return    171
    HOLD_A7FF25R3S04_CONTROL_DOMINATED            L7_ranked_future_return    322
  HOLD_A7FF25R3S04_COST2_PROXY_FRAGILE  L3_liquidity_tier_relative_return      4
  HOLD_A7FF25R3S04_ONE_BAR_LAG_FRAGILE              L0_raw_forward_return     16
  HOLD_A7FF25R3S04_ONE_BAR_LAG_FRAGILE L1_cross_sectional_relative_return     16
  HOLD_A7FF25R3S04_ONE_BAR_LAG_FRAGILE  L3_liquidity_tier_relative_return     19
  HOLD_A7FF25R3S04_ONE_BAR_LAG_FRAGILE             L5_vol_adjusted_return     36
  HOLD_A7FF25R3S04_ONE_BAR_LAG_FRAGILE            L7_ranked_future_return     61
     HOLD_A7FF25R3S04_PRE_MAY_UNSTABLE              L0_raw_forward_return    424
     HOLD_A7FF25R3S04_PRE_MAY_UNSTABLE L1_cross_sectional_relative_return    424
     HOLD_A7FF25R3S04_PRE_MAY_UNSTABLE  L3_liquidity_tier_relative_return    432
     HOLD_A7FF25R3S04_PRE_MAY_UNSTABLE             L5_vol_adjusted_return    432
     HOLD_A7FF25R3S04_PRE_MAY_UNSTABLE            L7_ranked_future_return    169
```

## Family Summary

```text
                     semantic_pair                               decision  count
     basis_premium_like|price_like               A7FF25R3S04_NUMERIC_CLUE     39
     basis_premium_like|price_like A7FF25R3S04_RANK_LABEL_DIAGNOSTIC_CLUE     80
     basis_premium_like|price_like     HOLD_A7FF25R3S04_CONTROL_DOMINATED    662
     basis_premium_like|price_like   HOLD_A7FF25R3S04_COST2_PROXY_FRAGILE      1
     basis_premium_like|price_like   HOLD_A7FF25R3S04_ONE_BAR_LAG_FRAGILE     75
     basis_premium_like|price_like      HOLD_A7FF25R3S04_PRE_MAY_UNSTABLE   1063
basis_premium_like|volatility_like               A7FF25R3S04_NUMERIC_CLUE     59
basis_premium_like|volatility_like A7FF25R3S04_RANK_LABEL_DIAGNOSTIC_CLUE     32
basis_premium_like|volatility_like     HOLD_A7FF25R3S04_CONTROL_DOMINATED    415
basis_premium_like|volatility_like   HOLD_A7FF25R3S04_COST2_PROXY_FRAGILE      3
basis_premium_like|volatility_like   HOLD_A7FF25R3S04_ONE_BAR_LAG_FRAGILE     73
basis_premium_like|volatility_like      HOLD_A7FF25R3S04_PRE_MAY_UNSTABLE    818
```

## Control Summary

```text
             control  median_ratio    max_ratio  rows
         one_bar_lag      0.914857  5580.630004  9960
 same_family_placebo      0.312014 11574.050688  9960
           sign_flip      0.993486  3816.617256  9960
      symbol_shuffle      0.423993  7512.480051  9960
        time_shuffle      0.438864  4737.154530  9960
wrong_lag_future_24h      1.510169 49824.198509  9960
wrong_lag_stale_168h      0.517221  1971.713303  9960
```

## Selected Portfolio Queue

```text
            blueprint_id                                                                                 expression                      semantic_pair       motif            label_family  label_horizon_h  orientation_from_train  premay_positive_split_count  premay_all_positive  control_ratio_premay_max  one_bar_lag_recent_oriented  lag_ok  robust_median_tstat_floor  robust_min_tstat_floor  robust_ok  cost2_recent_oriented  cost5_recent_oriented  cost10_recent_oriented  avg_n_obs_recent                               decision  train_2024_n  train_2024_mean_spread  train_2024_tstat  train_2024_nonoverlap_median_tstat  train_2024_nonoverlap_min_tstat  train_2024_positive_rate  validation_2025H1_n  validation_2025H1_mean_spread  validation_2025H1_tstat  validation_2025H1_nonoverlap_median_tstat  validation_2025H1_nonoverlap_min_tstat  validation_2025H1_positive_rate  test_2025H2_n  test_2025H2_mean_spread  test_2025H2_tstat  test_2025H2_nonoverlap_median_tstat  test_2025H2_nonoverlap_min_tstat  test_2025H2_positive_rate  recent_oos_2026JanApr_n  recent_oos_2026JanApr_mean_spread  recent_oos_2026JanApr_tstat  recent_oos_2026JanApr_nonoverlap_median_tstat  recent_oos_2026JanApr_nonoverlap_min_tstat  recent_oos_2026JanApr_positive_rate  non_l7_bonus  score_no_may          skeleton_key  finite_share  nonzero_share
a7ff24r_650915032f2a5979                                 Mul(Delta(mark_index_basis_bps,12),Sign(realized_vol_24h)) basis_premium_like|volatility_like  gated_sign  L5_vol_adjusted_return                8                    -1.0                            3                 True                  0.777635                     0.247474    True                   0.626901                2.325739       True               0.389848               0.389248                0.388248         94.933333               A7FF25R3S04_NUMERIC_CLUE           700               -0.015016         -0.519622                           -0.175288                        -1.634500                  0.480000                  712                      -0.055726                -2.018783                                  -0.626901                               -2.526720                         0.441011            712                -0.137832          -3.261929                            -1.329647                         -2.325739                   0.450843                      712                          -0.390248                    -5.507264                                      -2.333339                                   -3.278556                             0.411517           1.0    395.470187 skel_136259b72205469f      0.823901       0.998297
a7ff24r_d629e7fa3c03d92b                                        Sub(Delta(mark_index_basis_bps,12),trade_return_1h)      basis_premium_like|price_like         sub  L5_vol_adjusted_return                8                    -1.0                            3                 True                  0.914750                     0.247017    True                   0.656947                2.332895       True               0.387430               0.386830                0.385830         94.933333               A7FF25R3S04_NUMERIC_CLUE           700               -0.015074         -0.521867                           -0.166086                        -1.609672                  0.478571                  712                      -0.056967                -2.061710                                  -0.656947                               -2.565855                         0.441011            712                -0.137869          -3.260510                            -1.329647                         -2.332895                   0.450843                      712                          -0.387830                    -5.480878                                      -2.306638                                   -3.286543                             0.412921           1.0    392.914996 skel_0994b3a36a4d53ba      0.995978       0.999648
a7ff24r_0c84dc458dd14f07 Sub(CSRank(ZScore(Mean(mark_index_basis_bps,12))),CSRank(ZScore(Mean(trade_return_1h,2))))      basis_premium_like|price_like spread_rank L7_ranked_future_return                1                     1.0                            3                 True                  0.402297                     0.018093    True                   4.219579                4.219579       True               0.046374               0.045774                0.044774         95.866667 A7FF25R3S04_RANK_LABEL_DIAGNOSTIC_CLUE           708                0.055043          8.406676                            8.406676                         8.406676                  0.649718                  719                       0.027477                 4.219579                                   4.219579                                4.219579                         0.545202            719                 0.039649           6.177989                             6.177989                          6.177989                   0.598053                      719                           0.046774                     7.678783                                       7.678783                                    7.678783                             0.625869           0.0     51.371854 skel_f4061a64df347a31      0.995978       0.987706
a7ff24r_b019af9f134d20a4                            Sub(CSRank(Mean(premium_close_bps,12)),CSRank(trade_return_1h))      basis_premium_like|price_like spread_rank L7_ranked_future_return                1                     1.0                            3                 True                  0.215622                     0.018126    True                   4.509760                4.509760       True               0.044603               0.044003                0.043003         95.866667 A7FF25R3S04_RANK_LABEL_DIAGNOSTIC_CLUE           708                0.051548          7.966347                            7.966347                         7.966347                  0.621469                  719                       0.028721                 4.509760                                   4.509760                                4.509760                         0.575800            719                 0.039719           6.443706                             6.443706                          6.443706                   0.606398                      719                           0.045003                     6.945584                                       6.945584                                    6.945584                             0.606398           0.0     49.787199 skel_51c2bb588b20fa9e      0.996265       0.987781
a7ff24r_8e7ce8282d0b19f1                             Mul(premium_close_bps,Sign(ZScore(Mean(realized_vol_168h,2)))) basis_premium_like|volatility_like  gated_sign L7_ranked_future_return               24                     1.0                            3                 True                  0.777499                     0.041287    True                   0.878663               -0.427900       True               0.044881               0.044281                0.043281         92.800000 A7FF25R3S04_RANK_LABEL_DIAGNOSTIC_CLUE           695                0.003374          0.597474                            0.442953                        -2.004509                  0.519424                  696                       0.030108                 4.360403                                   0.878663                               -0.427900                         0.566092            696                 0.032094           6.051311                             1.169770                         -0.369185                   0.574713                      696                           0.045281                     6.904230                                       1.355918                                   -0.069990                             0.603448           0.0     49.503573 skel_c80f62c274b367a9      0.827061       0.672807
a7ff24r_dc05f323852f172e                    Sub(CSRank(ZScore(Mean(premium_close_bps,12))),CSRank(trade_return_1h))      basis_premium_like|price_like spread_rank L7_ranked_future_return                1                     1.0                            3                 True                  0.514221                     0.018126    True                   4.509760                4.509760       True               0.044603               0.044003                0.043003         95.866667 A7FF25R3S04_RANK_LABEL_DIAGNOSTIC_CLUE           708                0.051548          7.966347                            7.966347                         7.966347                  0.621469                  719                       0.028721                 4.509760                                   4.509760                                4.509760                         0.575800            719                 0.039719           6.443706                             6.443706                          6.443706                   0.606398                      719                           0.045003                     6.945584                                       6.945584                                    6.945584                             0.606398           0.0     49.488600 skel_206e713fb3d9a164      0.996265       0.987781
a7ff24r_b3a2aafee6dc89a2                     Sub(CSRank(premium_close_bps),CSRank(ZScore(Mean(trade_return_1h,8))))      basis_premium_like|price_like spread_rank L7_ranked_future_return                8                     1.0                            3                 True                  0.804293                     0.027841    True                   2.012278                0.819982       True               0.035509               0.034909                0.033909         94.933333 A7FF25R3S04_RANK_LABEL_DIAGNOSTIC_CLUE           705                0.034872          5.057991                            1.484001                         0.236154                  0.578723                  712                       0.053346                 8.318137                                   3.180984                                0.983649                         0.615169            712                 0.045436           7.704582                             2.959366                          1.300816                   0.622191                      712                           0.035909                     5.679846                                       2.012278                                    0.819982                             0.567416           0.0     40.105188 skel_a923757a8885923c      0.995404       0.990103
a7ff24r_62044809f67b688d                                     Sub(CSRank(premium_close_bps),CSRank(trade_return_1h))      basis_premium_like|price_like spread_rank L7_ranked_future_return                1                     1.0                            3                 True                  0.532719                     0.017393    True                   0.958639                0.958639       True               0.032362               0.031762                0.030762         95.866667 A7FF25R3S04_RANK_LABEL_DIAGNOSTIC_CLUE           719                0.038818          6.097998                            6.097998                         6.097998                  0.600834                  719                       0.006140                 0.958639                                   0.958639                                0.958639                         0.521558            719                 0.023096           3.898756                             3.898756                          3.898756                   0.556328                      719                           0.032762                     5.299912                                       5.299912                                    5.299912                             0.577191           0.0     37.229047 skel_293cae94cfd91548      0.999425       0.989745
```

## Boundary

```text
No May/post-selection stress is used in scoring or authorization.
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
L7 ranked-return rows remain diagnostic-only and cannot promote without non-L7 support.
```
