# CRYPTO A7FF-25R3S03 EXPANDED NUMERIC PROBE

Generated: 2026-05-30T08:22:36Z

## Decision

`PASS_A7FF25R3S03_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH`

A7FF-25R3S03 materializes the A7FF-7E selected blueprint queue and evaluates label response, controls, non-overlap statistics, and a dry portfolio marginal proxy. It is not formula search or alpha proof.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FF25R3S03_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH",
  "executes_generation": false,
  "executes_numeric_probe": true,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T08:22:36Z",
  "input_blueprint_count": 200,
  "label_response_rows": 3120,
  "materialized_activity_ok_count": 156,
  "non_l7_numeric_clue_rows": 8,
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
  "portfolio_queue_count": 48,
  "queue_limit": 200,
  "queue_offset": 0,
  "queue_path": "D:\\HermesWorker\\GDrive\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519_remote\\runtime\\a7ff24r_dry_generation_plan\\a7ff24r_company_shard_03_queue.csv",
  "queue_total_rows": 200,
  "rank_label_diagnostic_clue_rows": 94,
  "selected_portfolio_queue_count": 9,
  "stage": "A7FF-25R3S03",
  "uses_may": false
}
```

## Decision Counts

```text
                              decision                       label_family  count
              A7FF25R3S03_NUMERIC_CLUE              L0_raw_forward_return      2
              A7FF25R3S03_NUMERIC_CLUE L1_cross_sectional_relative_return      1
              A7FF25R3S03_NUMERIC_CLUE  L3_liquidity_tier_relative_return      2
              A7FF25R3S03_NUMERIC_CLUE             L5_vol_adjusted_return      3
A7FF25R3S03_RANK_LABEL_DIAGNOSTIC_CLUE            L7_ranked_future_return     94
    HOLD_A7FF25R3S03_CONTROL_DOMINATED              L0_raw_forward_return     76
    HOLD_A7FF25R3S03_CONTROL_DOMINATED L1_cross_sectional_relative_return     77
    HOLD_A7FF25R3S03_CONTROL_DOMINATED  L3_liquidity_tier_relative_return     68
    HOLD_A7FF25R3S03_CONTROL_DOMINATED             L5_vol_adjusted_return     65
    HOLD_A7FF25R3S03_CONTROL_DOMINATED            L7_ranked_future_return    187
  HOLD_A7FF25R3S03_COST2_PROXY_FRAGILE L1_cross_sectional_relative_return      1
  HOLD_A7FF25R3S03_COST2_PROXY_FRAGILE  L3_liquidity_tier_relative_return      1
  HOLD_A7FF25R3S03_ONE_BAR_LAG_FRAGILE              L0_raw_forward_return      3
  HOLD_A7FF25R3S03_ONE_BAR_LAG_FRAGILE L1_cross_sectional_relative_return      2
  HOLD_A7FF25R3S03_ONE_BAR_LAG_FRAGILE  L3_liquidity_tier_relative_return      2
  HOLD_A7FF25R3S03_ONE_BAR_LAG_FRAGILE             L5_vol_adjusted_return      3
  HOLD_A7FF25R3S03_ONE_BAR_LAG_FRAGILE            L7_ranked_future_return      4
     HOLD_A7FF25R3S03_PRE_MAY_UNSTABLE              L0_raw_forward_return    543
     HOLD_A7FF25R3S03_PRE_MAY_UNSTABLE L1_cross_sectional_relative_return    543
     HOLD_A7FF25R3S03_PRE_MAY_UNSTABLE  L3_liquidity_tier_relative_return    551
     HOLD_A7FF25R3S03_PRE_MAY_UNSTABLE             L5_vol_adjusted_return    553
     HOLD_A7FF25R3S03_PRE_MAY_UNSTABLE            L7_ranked_future_return    339
```

## Family Summary

```text
                semantic_pair                               decision  count
basis_premium_like|price_like               A7FF25R3S03_NUMERIC_CLUE      8
basis_premium_like|price_like A7FF25R3S03_RANK_LABEL_DIAGNOSTIC_CLUE     94
basis_premium_like|price_like     HOLD_A7FF25R3S03_CONTROL_DOMINATED    473
basis_premium_like|price_like   HOLD_A7FF25R3S03_COST2_PROXY_FRAGILE      2
basis_premium_like|price_like   HOLD_A7FF25R3S03_ONE_BAR_LAG_FRAGILE     14
basis_premium_like|price_like      HOLD_A7FF25R3S03_PRE_MAY_UNSTABLE   2529
```

## Control Summary

```text
             control  median_ratio    max_ratio  rows
         one_bar_lag      0.895003  2208.770965  9360
 same_family_placebo      0.351294  1542.868529  9360
           sign_flip      0.972986   583.628457  9360
      symbol_shuffle      0.514249  5111.386986  9360
        time_shuffle      0.420092  1655.264841  9360
wrong_lag_future_24h      1.697831 22305.231693  9360
wrong_lag_stale_168h      0.625769  2477.725275  9360
```

## Selected Portfolio Queue

```text
            blueprint_id                                                                 expression                 semantic_pair        motif            label_family  label_horizon_h  orientation_from_train  premay_positive_split_count  premay_all_positive  control_ratio_premay_max  one_bar_lag_recent_oriented  lag_ok  robust_median_tstat_floor  robust_min_tstat_floor  robust_ok  cost2_recent_oriented  cost5_recent_oriented  cost10_recent_oriented  avg_n_obs_recent                               decision  train_2024_n  train_2024_mean_spread  train_2024_tstat  train_2024_nonoverlap_median_tstat  train_2024_nonoverlap_min_tstat  train_2024_positive_rate  validation_2025H1_n  validation_2025H1_mean_spread  validation_2025H1_tstat  validation_2025H1_nonoverlap_median_tstat  validation_2025H1_nonoverlap_min_tstat  validation_2025H1_positive_rate  test_2025H2_n  test_2025H2_mean_spread  test_2025H2_tstat  test_2025H2_nonoverlap_median_tstat  test_2025H2_nonoverlap_min_tstat  test_2025H2_positive_rate  recent_oos_2026JanApr_n  recent_oos_2026JanApr_mean_spread  recent_oos_2026JanApr_tstat  recent_oos_2026JanApr_nonoverlap_median_tstat  recent_oos_2026JanApr_nonoverlap_min_tstat  recent_oos_2026JanApr_positive_rate  non_l7_bonus  score_no_may          skeleton_key  finite_share  nonzero_share
a7ff24r_b74c05b6f58309a0           SafeDiv(premium_close_bps,Abs(ZScore(Mean(trade_return_1h,12)))) basis_premium_like|price_like safe_div_abs  L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.503320                     0.056338    True                   1.679926                1.679926       True               0.081557               0.080957                0.079957         95.866667               A7FF25R3S03_NUMERIC_CLUE           705               -0.018100         -1.547476                           -1.547476                        -1.547476                  0.466667                  668                      -0.056021                -3.234562                                  -3.234562                               -3.234562                         0.401198            713                -0.030835          -1.679926                            -1.679926                         -1.679926                   0.468443                      719                          -0.081957                    -3.819753                                      -3.819753                                   -3.819753                             0.428373           1.0     87.453581 skel_c80f62c274b367a9      0.993105       0.663907
a7ff24r_89f2b5ee0732b53d                            SafeDiv(premium_close_bps,Abs(trade_return_1h)) basis_premium_like|price_like safe_div_abs  L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.474289                     0.038370    True                   1.492904                1.492904       True               0.049030               0.048430                0.047430         90.784722               A7FF25R3S03_NUMERIC_CLUE           715               -0.024603         -1.952882                           -1.952882                        -1.952882                  0.446154                  669                      -0.052593                -2.992473                                  -2.992473                               -2.992473                         0.397608            714                -0.027552          -1.492904                            -1.492904                         -1.492904                   0.487395                      719                          -0.049430                    -2.232619                                      -2.232619                                   -2.232619                             0.456189           1.0     54.955800 skel_d9d4f69744bac825      0.963896       0.671458
a7ff24r_a4bf0717964ee0c0            Mean(Mul(premium_close_bps,ZScore(Mean(trade_return_1h,12))),4) basis_premium_like|price_like   smooth_mul L7_ranked_future_return                8                     1.0                            3                 True                  0.778386                     0.043904    True                   2.450697                1.532784       True               0.045824               0.045224                0.044224         94.933333 A7FF25R3S03_RANK_LABEL_DIAGNOSTIC_CLUE           698                0.004397          0.630355                            0.485904                        -0.768788                  0.531519                  712                       0.075624                11.044040                                   4.002375                                2.810781                         0.657303            712                 0.061279           9.269077                             3.262811                          2.374527                   0.609551                      712                           0.046224                     7.039947                                       2.450697                                    1.532784                             0.617978           0.0     50.445978 skel_44a246af570899bb      0.991382       0.916709
a7ff24r_29eac44dbcefb3ff Sub(CSRank(ZScore(Mean(mark_index_basis_bps,12))),CSRank(trade_return_1h)) basis_premium_like|price_like  spread_rank L7_ranked_future_return                1                     1.0                            3                 True                  0.356726                     0.019725    True                   4.194783                4.194783       True               0.044352               0.043752                0.042752         95.866667 A7FF25R3S03_RANK_LABEL_DIAGNOSTIC_CLUE           708                0.058258          8.834852                            8.834852                         8.834852                  0.618644                  719                       0.026545                 4.194783                                   4.194783                                4.194783                         0.573018            719                 0.038248           6.086633                             6.086633                          6.086633                   0.575800                      719                           0.044752                     7.216051                                       7.216051                                    7.216051                             0.616134           0.0     49.395320 skel_206e713fb3d9a164      0.996265       0.987889
a7ff24r_5e142f8ad925552c Mean(Mul(Mean(mark_index_basis_bps,12),ZScore(Mean(trade_return_1h,2))),4) basis_premium_like|price_like   smooth_mul L7_ranked_future_return                8                     1.0                            3                 True                  0.563950                     0.035109    True                   1.989535                0.116336       True               0.041481               0.040881                0.039881         94.933333 A7FF25R3S03_RANK_LABEL_DIAGNOSTIC_CLUE           698                0.001271          0.180145                            0.084933                        -0.345176                  0.512894                  712                       0.063109                 9.620261                                   3.275347                                2.333990                         0.647472            712                 0.049056           8.176957                             3.292025                          0.116336                   0.609551                      712                           0.041881                     6.638700                                       1.989535                                    0.963965                             0.601124           0.0     46.316805 skel_bb02868db9f6b779      0.994255       1.000000
a7ff24r_444747afe5aaa768                          Mean(Mul(mark_index_basis_bps,trade_return_1h),4) basis_premium_like|price_like   smooth_mul L7_ranked_future_return                8                     1.0                            3                 True                  0.489672                     0.029580    True                   2.185897                0.364093       True               0.039542               0.038942                0.037942         94.933333 A7FF25R3S03_RANK_LABEL_DIAGNOSTIC_CLUE           709                0.016701          2.681622                            0.326493                        -0.276420                  0.558533                  712                       0.043246                 7.057455                                   2.627871                                0.404974                         0.617978            712                 0.034513           5.806646                             2.185897                          0.364093                   0.549157                      712                           0.039942                     6.371895                                       2.234761                                    1.828125                             0.615169           0.0     44.452506 skel_356a5f3fab58eb27      0.997702       0.998734
a7ff24r_73cc9640f10344e1                     Mean(Mul(Mean(premium_close_bps,8),trade_return_1h),4) basis_premium_like|price_like   smooth_mul L7_ranked_future_return                8                     1.0                            3                 True                  0.457118                     0.030908    True                   2.194721                0.068710       True               0.039209               0.038609                0.037609         94.933333 A7FF25R3S03_RANK_LABEL_DIAGNOSTIC_CLUE           702                0.001317          0.202150                           -0.021509                        -0.639744                  0.507123                  712                       0.046698                 7.650560                                   2.585002                                1.966290                         0.632022            712                 0.048155           8.322245                             3.015416                          1.787053                   0.623596                      712                           0.039609                     5.807398                                       2.194721                                    0.068710                             0.605337           0.0     44.151751 skel_8184698cb7b24c02      0.995691       0.978289
a7ff24r_2e64d53505b570ae                    Mean(Mul(premium_close_bps,Mean(trade_return_1h,12)),4) basis_premium_like|price_like   smooth_mul L7_ranked_future_return                8                     1.0                            3                 True                  0.818493                     0.038630    True                   1.843136                1.094182       True               0.037976               0.037376                0.036376         94.933333 A7FF25R3S03_RANK_LABEL_DIAGNOSTIC_CLUE           698                0.000251          0.038808                           -0.184190                        -1.099766                  0.502865                  712                       0.062071                10.088468                                   3.518680                                2.715902                         0.627809            712                 0.056496           8.992486                             3.060903                          2.246786                   0.625000                      712                           0.038376                     5.883690                                       1.843136                                    1.094182                             0.581461           0.0     42.557821 skel_644ba0ee0d0e38ee      0.991382       0.916697
a7ff24r_4c66631806425fac             Sub(CSRank(premium_close_bps),CSRank(Mean(trade_return_1h,8))) basis_premium_like|price_like  spread_rank L7_ranked_future_return                8                     1.0                            3                 True                  0.804293                     0.027841    True                   2.012278                0.819982       True               0.035509               0.034909                0.033909         94.933333 A7FF25R3S03_RANK_LABEL_DIAGNOSTIC_CLUE           705                0.034872          5.057991                            1.484001                         0.236154                  0.578723                  712                       0.053346                 8.318137                                   3.180984                                0.983649                         0.615169            712                 0.045436           7.704582                             2.959366                          1.300816                   0.622191                      712                           0.035909                     5.679846                                       2.012278                                    0.819982                             0.567416           0.0     40.105188 skel_1a1b3fb29dff7328      0.995404       0.990103
```

## Boundary

```text
No May/post-selection stress is used in scoring or authorization.
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
L7 ranked-return rows remain diagnostic-only and cannot promote without non-L7 support.
```
