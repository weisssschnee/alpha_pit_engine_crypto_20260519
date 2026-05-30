# CRYPTO A7FF-25R3S00 EXPANDED NUMERIC PROBE

Generated: 2026-05-30T08:22:34Z

## Decision

`PASS_A7FF25R3S00_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH`

A7FF-25R3S00 materializes the A7FF-7E selected blueprint queue and evaluates label response, controls, non-overlap statistics, and a dry portfolio marginal proxy. It is not formula search or alpha proof.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FF25R3S00_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH",
  "executes_generation": false,
  "executes_numeric_probe": true,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T08:22:34Z",
  "input_blueprint_count": 200,
  "label_response_rows": 3140,
  "materialized_activity_ok_count": 157,
  "non_l7_numeric_clue_rows": 77,
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
  "portfolio_queue_count": 46,
  "queue_limit": 200,
  "queue_offset": 0,
  "queue_path": "D:\\HermesWorker\\GDrive\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519_remote\\runtime\\a7ff24r_dry_generation_plan\\a7ff24r_company_shard_00_queue.csv",
  "queue_total_rows": 200,
  "rank_label_diagnostic_clue_rows": 56,
  "selected_portfolio_queue_count": 8,
  "stage": "A7FF-25R3S00",
  "uses_may": false
}
```

## Decision Counts

```text
                              decision                       label_family  count
              A7FF25R3S00_NUMERIC_CLUE              L0_raw_forward_return     17
              A7FF25R3S00_NUMERIC_CLUE L1_cross_sectional_relative_return     20
              A7FF25R3S00_NUMERIC_CLUE  L3_liquidity_tier_relative_return     17
              A7FF25R3S00_NUMERIC_CLUE             L5_vol_adjusted_return     23
A7FF25R3S00_RANK_LABEL_DIAGNOSTIC_CLUE            L7_ranked_future_return     56
    HOLD_A7FF25R3S00_CONTROL_DOMINATED              L0_raw_forward_return    119
    HOLD_A7FF25R3S00_CONTROL_DOMINATED L1_cross_sectional_relative_return    116
    HOLD_A7FF25R3S00_CONTROL_DOMINATED  L3_liquidity_tier_relative_return    110
    HOLD_A7FF25R3S00_CONTROL_DOMINATED             L5_vol_adjusted_return    110
    HOLD_A7FF25R3S00_CONTROL_DOMINATED            L7_ranked_future_return    173
  HOLD_A7FF25R3S00_COST2_PROXY_FRAGILE              L0_raw_forward_return      3
  HOLD_A7FF25R3S00_COST2_PROXY_FRAGILE L1_cross_sectional_relative_return      3
  HOLD_A7FF25R3S00_COST2_PROXY_FRAGILE  L3_liquidity_tier_relative_return      5
  HOLD_A7FF25R3S00_ONE_BAR_LAG_FRAGILE              L0_raw_forward_return     10
  HOLD_A7FF25R3S00_ONE_BAR_LAG_FRAGILE L1_cross_sectional_relative_return     10
  HOLD_A7FF25R3S00_ONE_BAR_LAG_FRAGILE  L3_liquidity_tier_relative_return     14
  HOLD_A7FF25R3S00_ONE_BAR_LAG_FRAGILE             L5_vol_adjusted_return     27
  HOLD_A7FF25R3S00_ONE_BAR_LAG_FRAGILE            L7_ranked_future_return     53
     HOLD_A7FF25R3S00_PRE_MAY_UNSTABLE              L0_raw_forward_return    479
     HOLD_A7FF25R3S00_PRE_MAY_UNSTABLE L1_cross_sectional_relative_return    479
     HOLD_A7FF25R3S00_PRE_MAY_UNSTABLE  L3_liquidity_tier_relative_return    482
     HOLD_A7FF25R3S00_PRE_MAY_UNSTABLE             L5_vol_adjusted_return    468
     HOLD_A7FF25R3S00_PRE_MAY_UNSTABLE            L7_ranked_future_return    346
```

## Family Summary

```text
                        semantic_pair                               decision  count
                   basis_premium_like               A7FF25R3S00_NUMERIC_CLUE     43
                   basis_premium_like A7FF25R3S00_RANK_LABEL_DIAGNOSTIC_CLUE      7
                   basis_premium_like     HOLD_A7FF25R3S00_CONTROL_DOMINATED    143
                   basis_premium_like   HOLD_A7FF25R3S00_COST2_PROXY_FRAGILE      1
                   basis_premium_like   HOLD_A7FF25R3S00_ONE_BAR_LAG_FRAGILE     36
                   basis_premium_like      HOLD_A7FF25R3S00_PRE_MAY_UNSTABLE    510
basis_premium_like|basis_premium_like               A7FF25R3S00_NUMERIC_CLUE     34
basis_premium_like|basis_premium_like A7FF25R3S00_RANK_LABEL_DIAGNOSTIC_CLUE     49
basis_premium_like|basis_premium_like     HOLD_A7FF25R3S00_CONTROL_DOMINATED    485
basis_premium_like|basis_premium_like   HOLD_A7FF25R3S00_COST2_PROXY_FRAGILE     10
basis_premium_like|basis_premium_like   HOLD_A7FF25R3S00_ONE_BAR_LAG_FRAGILE     78
basis_premium_like|basis_premium_like      HOLD_A7FF25R3S00_PRE_MAY_UNSTABLE   1744
```

## Control Summary

```text
             control  median_ratio    max_ratio  rows
         one_bar_lag      0.927250  3668.088688  9420
 same_family_placebo      0.328801  1414.078042  9420
           sign_flip      0.997966   513.538111  9420
      symbol_shuffle      0.498301  2197.673175  9420
        time_shuffle      0.516871  1254.678157  9420
wrong_lag_future_24h      1.275558 11099.252164  9420
wrong_lag_stale_168h      0.666451  1971.713303  9420
```

## Selected Portfolio Queue

```text
            blueprint_id                                                                          expression                         semantic_pair        motif            label_family  label_horizon_h  orientation_from_train  premay_positive_split_count  premay_all_positive  control_ratio_premay_max  one_bar_lag_recent_oriented  lag_ok  robust_median_tstat_floor  robust_min_tstat_floor  robust_ok  cost2_recent_oriented  cost5_recent_oriented  cost10_recent_oriented  avg_n_obs_recent                               decision  train_2024_n  train_2024_mean_spread  train_2024_tstat  train_2024_nonoverlap_median_tstat  train_2024_nonoverlap_min_tstat  train_2024_positive_rate  validation_2025H1_n  validation_2025H1_mean_spread  validation_2025H1_tstat  validation_2025H1_nonoverlap_median_tstat  validation_2025H1_nonoverlap_min_tstat  validation_2025H1_positive_rate  test_2025H2_n  test_2025H2_mean_spread  test_2025H2_tstat  test_2025H2_nonoverlap_median_tstat  test_2025H2_nonoverlap_min_tstat  test_2025H2_positive_rate  recent_oos_2026JanApr_n  recent_oos_2026JanApr_mean_spread  recent_oos_2026JanApr_tstat  recent_oos_2026JanApr_nonoverlap_median_tstat  recent_oos_2026JanApr_nonoverlap_min_tstat  recent_oos_2026JanApr_positive_rate  non_l7_bonus  score_no_may          skeleton_key  finite_share  nonzero_share
a7ff24r_858ff2210f276fcf                                                      Delta(mark_index_basis_bps,12)                    basis_premium_like       single  L5_vol_adjusted_return                8                    -1.0                            3                 True                  0.664665                     0.247474    True                   0.626901                2.325739       True               0.389848               0.389248                0.388248         94.933333               A7FF25R3S00_NUMERIC_CLUE           700               -0.015016         -0.519622                           -0.175288                        -1.634500                  0.480000                  712                      -0.055726                -2.018783                                  -0.626901                               -2.526720                         0.441011            712                -0.137832          -3.261929                            -1.329647                         -2.325739                   0.450843                      712                          -0.390248                    -5.507264                                      -2.333339                                   -3.278556                             0.411517           1.0    395.583156 skel_1d39996e97d5ace0      0.996265       0.998429
a7ff24r_145e2d58adad4f4a               SafeDiv(mark_index_basis_bps,Abs(ZScore(Mean(premium_close_bps,12)))) basis_premium_like|basis_premium_like safe_div_abs  L5_vol_adjusted_return                4                    -1.0                            3                 True                  0.787660                     0.044844    True                   0.513295                2.279881       True               0.136893               0.136293                0.135293         95.466667               A7FF25R3S00_NUMERIC_CLUE           705               -0.011115         -0.632373                           -0.342037                        -1.503770                  0.485106                  716                      -0.030480                -1.443350                                  -0.513295                               -2.372006                         0.446927            716                -0.081160          -2.666467                            -1.589011                         -2.279881                   0.432961                      716                          -0.137293                    -4.069370                                      -2.220906                                   -2.385119                             0.438547           1.0    142.505654 skel_c80f62c274b367a9      0.996553       0.987385
a7ff24r_0ba14c1c756fb529                       SafeDiv(Delta(mark_index_basis_bps,8),Abs(premium_close_bps)) basis_premium_like|basis_premium_like safe_div_abs  L5_vol_adjusted_return                4                    -1.0                            3                 True                  0.934919                     0.048834    True                   0.461102                0.897190       True               0.120234               0.119634                0.118634         57.825000               A7FF25R3S00_NUMERIC_CLUE           708               -0.026589         -1.244563                           -0.657334                        -1.019452                  0.457627                  716                      -0.027335                -1.018749                                  -0.461102                               -0.897190                         0.460894            716                -0.046880          -1.623782                            -0.570312                         -1.895117                   0.449721                      716                          -0.120634                    -2.888008                                      -1.599563                                   -2.447467                             0.458101           1.0    125.698703 skel_136259b72205469f      0.662352       0.999729
a7ff24r_8d906801b8dec4c0                                 Mul(mark_index_basis_bps,Mean(premium_close_bps,2)) basis_premium_like|basis_premium_like          mul  L5_vol_adjusted_return                1                     1.0                            3                 True                  0.600993                     0.029630    True                   4.122856                4.122856       True               0.113528               0.112928                0.111928         95.866667               A7FF25R3S00_NUMERIC_CLUE           717                0.000108          0.010153                            0.010153                         0.010153                  0.524407                  718                       0.050202                 4.122856                                   4.122856                                4.122856                         0.594708            716                 0.093472           5.488338                             5.488338                          5.488338                   0.608939                      707                           0.113928                     4.513616                                       4.513616                                    4.513616                             0.567185           1.0    119.326996 skel_f8484b844efd270f      0.999425       0.811898
a7ff24r_48f9f812cd8214e5                           Mul(mark_index_basis_bps,Sign(Mean(premium_close_bps,8))) basis_premium_like|basis_premium_like   gated_sign  L5_vol_adjusted_return                1                     1.0                            3                 True                  0.836802                     0.024887    True                   4.496317                4.496317       True               0.095457               0.094857                0.093857         95.866667               A7FF25R3S00_NUMERIC_CLUE           712                0.013278          1.338968                            1.338968                         1.338968                  0.533708                  719                       0.071753                 6.942543                                   6.942543                                6.942543                         0.625869            719                 0.115425           8.165801                             8.165801                          8.165801                   0.646732                      719                           0.095857                     4.496317                                       4.496317                                    4.496317                             0.570236           1.0    101.019721 skel_a2f58ee62d9e7ad2      0.997702       0.956366
a7ff24r_f695d065dec8c1ad                                Mul(Delta(mark_index_basis_bps,8),premium_close_bps) basis_premium_like|basis_premium_like          mul  L5_vol_adjusted_return                1                     1.0                            3                 True                  0.643964                     0.015352    True                   2.283887                2.283887       True               0.043097               0.042497                0.041497         95.866667               A7FF25R3S00_NUMERIC_CLUE           711                0.029548          2.516762                            2.516762                         2.516762                  0.524613                  719                       0.033611                 3.163210                                   3.163210                                3.163210                         0.543811            719                 0.043765           3.222499                             3.222499                          3.222499                   0.570236                      719                           0.043497                     2.283887                                       2.283887                                    2.283887                             0.539638           1.0     48.853284 skel_0994b3a36a4d53ba      0.997415       0.663888
a7ff24r_0140b036cf90c55c                 Mean(Mul(mark_index_basis_bps,ZScore(Mean(premium_close_bps,8))),4) basis_premium_like|basis_premium_like   smooth_mul L7_ranked_future_return                8                    -1.0                            3                 True                  0.510543                     0.037930    True                   1.196284                2.044749       True               0.041943               0.041343                0.040343         94.933333 A7FF25R3S00_RANK_LABEL_DIAGNOSTIC_CLUE           702               -0.020115         -3.601300                           -1.381890                        -2.046424                  0.457265                  712                      -0.036052                -6.982102                                  -2.557805                               -3.180831                         0.407303            712                -0.018745          -3.166497                            -1.196284                         -2.044749                   0.460674                      712                          -0.042343                    -7.385557                                      -2.711475                                   -3.206557                             0.363764           0.0     46.832931 skel_44a246af570899bb      0.996840       0.999751
a7ff24r_1897e3e44a9baba5 Mean(Mul(ZScore(Mean(mark_index_basis_bps,2)),ZScore(Mean(premium_close_bps,8))),4) basis_premium_like|basis_premium_like   smooth_mul L7_ranked_future_return                1                    -1.0                            3                 True                  0.757668                     0.010269    True                   1.882861                1.882861       True               0.022484               0.021884                0.020884         95.866667 A7FF25R3S00_RANK_LABEL_DIAGNOSTIC_CLUE           709               -0.002232         -0.417235                           -0.417235                        -0.417235                  0.495063                  719                      -0.011672                -2.263784                                  -2.263784                               -2.263784                         0.452017            719                -0.011158          -1.882861                            -1.882861                         -1.882861                   0.481224                      719                          -0.022884                    -4.077405                                      -4.077405                                   -4.077405                             0.433936           0.0     27.126482 skel_23144da521f368b4      0.996840       1.000000
```

## Boundary

```text
No May/post-selection stress is used in scoring or authorization.
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
L7 ranked-return rows remain diagnostic-only and cannot promote without non-L7 support.
```
