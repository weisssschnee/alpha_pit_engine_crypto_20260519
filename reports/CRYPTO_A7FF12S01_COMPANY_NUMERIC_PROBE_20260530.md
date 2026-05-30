# CRYPTO A7FF-12S01 EXPANDED NUMERIC PROBE

Generated: 2026-05-30T03:39:26Z

## Decision

`PASS_A7FF12S01_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH`

A7FF-12S01 materializes the A7FF-7E selected blueprint queue and evaluates label response, controls, non-overlap statistics, and a dry portfolio marginal proxy. It is not formula search or alpha proof.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FF12S01_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH",
  "executes_generation": false,
  "executes_numeric_probe": true,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T03:39:26Z",
  "input_blueprint_count": 90,
  "label_response_rows": 1800,
  "materialized_activity_ok_count": 90,
  "non_l7_numeric_clue_rows": 160,
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
  "portfolio_queue_count": 33,
  "queue_limit": 90,
  "queue_offset": 90,
  "queue_path": "D:\\HermesWorker\\GDrive\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519_remote\\runtime\\a7ff12_numeric_wave_queue_contract\\a7ff12_numeric_wave_queue.csv",
  "queue_total_rows": 720,
  "rank_label_diagnostic_clue_rows": 41,
  "selected_portfolio_queue_count": 12,
  "stage": "A7FF-12S01",
  "uses_may": false
}
```

## Decision Counts

```text
                            decision                       label_family  count
              A7FF12S01_NUMERIC_CLUE              L0_raw_forward_return     33
              A7FF12S01_NUMERIC_CLUE L1_cross_sectional_relative_return     35
              A7FF12S01_NUMERIC_CLUE  L3_liquidity_tier_relative_return     36
              A7FF12S01_NUMERIC_CLUE             L5_vol_adjusted_return     56
A7FF12S01_RANK_LABEL_DIAGNOSTIC_CLUE            L7_ranked_future_return     41
    HOLD_A7FF12S01_CONTROL_DOMINATED              L0_raw_forward_return     90
    HOLD_A7FF12S01_CONTROL_DOMINATED L1_cross_sectional_relative_return     90
    HOLD_A7FF12S01_CONTROL_DOMINATED  L3_liquidity_tier_relative_return     90
    HOLD_A7FF12S01_CONTROL_DOMINATED             L5_vol_adjusted_return     89
    HOLD_A7FF12S01_CONTROL_DOMINATED            L7_ranked_future_return     83
  HOLD_A7FF12S01_COST2_PROXY_FRAGILE              L0_raw_forward_return      1
  HOLD_A7FF12S01_ONE_BAR_LAG_FRAGILE              L0_raw_forward_return     14
  HOLD_A7FF12S01_ONE_BAR_LAG_FRAGILE L1_cross_sectional_relative_return     13
  HOLD_A7FF12S01_ONE_BAR_LAG_FRAGILE  L3_liquidity_tier_relative_return     15
  HOLD_A7FF12S01_ONE_BAR_LAG_FRAGILE             L5_vol_adjusted_return     19
  HOLD_A7FF12S01_ONE_BAR_LAG_FRAGILE            L7_ranked_future_return     53
     HOLD_A7FF12S01_PRE_MAY_UNSTABLE              L0_raw_forward_return    222
     HOLD_A7FF12S01_PRE_MAY_UNSTABLE L1_cross_sectional_relative_return    222
     HOLD_A7FF12S01_PRE_MAY_UNSTABLE  L3_liquidity_tier_relative_return    219
     HOLD_A7FF12S01_PRE_MAY_UNSTABLE             L5_vol_adjusted_return    196
     HOLD_A7FF12S01_PRE_MAY_UNSTABLE            L7_ranked_future_return    183
```

## Family Summary

```text
                        semantic_pair                             decision  count
basis_premium_like|basis_premium_like               A7FF12S01_NUMERIC_CLUE     61
basis_premium_like|basis_premium_like A7FF12S01_RANK_LABEL_DIAGNOSTIC_CLUE     16
basis_premium_like|basis_premium_like     HOLD_A7FF12S01_CONTROL_DOMINATED    135
basis_premium_like|basis_premium_like   HOLD_A7FF12S01_ONE_BAR_LAG_FRAGILE     66
basis_premium_like|basis_premium_like      HOLD_A7FF12S01_PRE_MAY_UNSTABLE    242
  basis_premium_like|positioning_like               A7FF12S01_NUMERIC_CLUE     33
  basis_premium_like|positioning_like A7FF12S01_RANK_LABEL_DIAGNOSTIC_CLUE      8
  basis_premium_like|positioning_like     HOLD_A7FF12S01_CONTROL_DOMINATED     91
  basis_premium_like|positioning_like   HOLD_A7FF12S01_COST2_PROXY_FRAGILE      1
  basis_premium_like|positioning_like   HOLD_A7FF12S01_ONE_BAR_LAG_FRAGILE     20
  basis_premium_like|positioning_like      HOLD_A7FF12S01_PRE_MAY_UNSTABLE    267
        basis_premium_like|price_like               A7FF12S01_NUMERIC_CLUE     25
        basis_premium_like|price_like A7FF12S01_RANK_LABEL_DIAGNOSTIC_CLUE      6
        basis_premium_like|price_like     HOLD_A7FF12S01_CONTROL_DOMINATED    114
        basis_premium_like|price_like   HOLD_A7FF12S01_ONE_BAR_LAG_FRAGILE     22
        basis_premium_like|price_like      HOLD_A7FF12S01_PRE_MAY_UNSTABLE    253
   basis_premium_like|volatility_like               A7FF12S01_NUMERIC_CLUE     41
   basis_premium_like|volatility_like A7FF12S01_RANK_LABEL_DIAGNOSTIC_CLUE     11
   basis_premium_like|volatility_like     HOLD_A7FF12S01_CONTROL_DOMINATED    102
   basis_premium_like|volatility_like   HOLD_A7FF12S01_ONE_BAR_LAG_FRAGILE      6
   basis_premium_like|volatility_like      HOLD_A7FF12S01_PRE_MAY_UNSTABLE    280
```

## Control Summary

```text
             control  median_ratio   max_ratio  rows
         one_bar_lag      0.633229 1116.876471  5400
 same_family_placebo      0.285221 1023.380025  5400
           sign_flip      1.004660  213.752941  5400
      symbol_shuffle      0.344050 3976.870397  5400
        time_shuffle      0.338697 1807.589981  5400
wrong_lag_future_24h      0.975038 7181.848623  5400
wrong_lag_stale_168h      0.421571 5222.921553  5400
```

## Selected Portfolio Queue

```text
           blueprint_id                                                                                       expression                         semantic_pair              motif            label_family  label_horizon_h  orientation_from_train  premay_positive_split_count  premay_all_positive  control_ratio_premay_max  one_bar_lag_recent_oriented  lag_ok  robust_median_tstat_floor  robust_min_tstat_floor  robust_ok  cost2_recent_oriented  cost5_recent_oriented  cost10_recent_oriented  avg_n_obs_recent                             decision  train_2024_n  train_2024_mean_spread  train_2024_tstat  train_2024_nonoverlap_median_tstat  train_2024_nonoverlap_min_tstat  train_2024_positive_rate  validation_2025H1_n  validation_2025H1_mean_spread  validation_2025H1_tstat  validation_2025H1_nonoverlap_median_tstat  validation_2025H1_nonoverlap_min_tstat  validation_2025H1_positive_rate  test_2025H2_n  test_2025H2_mean_spread  test_2025H2_tstat  test_2025H2_nonoverlap_median_tstat  test_2025H2_nonoverlap_min_tstat  test_2025H2_positive_rate  recent_oos_2026JanApr_n  recent_oos_2026JanApr_mean_spread  recent_oos_2026JanApr_tstat  recent_oos_2026JanApr_nonoverlap_median_tstat  recent_oos_2026JanApr_nonoverlap_min_tstat  recent_oos_2026JanApr_positive_rate  non_l7_bonus  score_no_may          skeleton_key  finite_share  nonzero_share
a7ff7e_f05cfb85e23e4866                     Sub(Delta(mark_index_basis_bps,12),CSRank(taker_buy_sell_volume_ratio_last))   basis_premium_like|positioning_like                sub  L5_vol_adjusted_return                8                    -1.0                            3                 True                  0.608480                     0.248405    True                   0.487614                2.259681       True               0.391766               0.391166                0.390166         94.933333               A7FF12S01_NUMERIC_CLUE           700               -0.010969         -0.372441                           -0.180336                        -1.485012                  0.482857                  712                      -0.051710                -1.893768                                  -0.487614                               -2.456957                         0.449438            712                -0.145430          -3.522668                            -1.352877                         -2.259681                   0.450843                      712                          -0.392166                    -5.538064                                      -2.358803                                   -3.320284                             0.407303           1.0    397.557992 skel_136259b72205469f      0.996265       1.000000
a7ff7e_f484f2e1a7036ff4                           Mul(Delta(mark_index_basis_bps,12),Sign(CSRank(mark_trade_basis_bps))) basis_premium_like|basis_premium_like         gated_sign  L5_vol_adjusted_return                8                    -1.0                            3                 True                  0.619643                     0.247474    True                   0.626901                2.325739       True               0.389848               0.389248                0.388248         94.933333               A7FF12S01_NUMERIC_CLUE           700               -0.015016         -0.519622                           -0.175288                        -1.634500                  0.480000                  712                      -0.055726                -2.018783                                  -0.626901                               -2.526720                         0.441011            712                -0.137832          -3.261929                            -1.329647                         -2.325739                   0.450843                      712                          -0.390248                    -5.507264                                      -2.333339                                   -3.278556                             0.411517           1.0    395.628179 skel_069f2015163fa7ef      0.996265       0.998429
a7ff7e_3a7e3ddbe5462bea                                    Sub(Delta(mark_index_basis_bps,12),Delta(trade_return_24h,1))         basis_premium_like|price_like                sub  L5_vol_adjusted_return                8                    -1.0                            3                 True                  0.638897                     0.247887    True                   0.626901                2.332895       True               0.388314               0.387714                0.386714         94.933333               A7FF12S01_NUMERIC_CLUE           700               -0.012884         -0.445439                           -0.060329                        -1.610053                  0.481429                  712                      -0.055484                -2.010813                                  -0.626901                               -2.514402                         0.441011            712                -0.138167          -3.267058                            -1.339118                         -2.332895                   0.450843                      712                          -0.388714                    -5.493157                                      -2.301439                                   -3.286543                             0.411517           1.0    394.074754 skel_8727d93aac220fc6      0.823901       0.999866
a7ff7e_0f6554ac44a17024                      Sub(Delta(mark_index_basis_bps,12),Clip(ZScore(mark_trade_basis_bps),-3,3)) basis_premium_like|basis_premium_like                sub  L5_vol_adjusted_return                8                    -1.0                            3                 True                  0.660834                     0.226480    True                   0.751315                2.221377       True               0.385681               0.385081                0.384081         94.933333               A7FF12S01_NUMERIC_CLUE           700               -0.018284         -0.616888                           -0.078530                        -1.509996                  0.484286                  712                      -0.060393                -2.278161                                  -0.751315                               -2.221377                         0.448034            712                -0.158897          -3.673913                            -1.290752                         -2.724723                   0.426966                      712                          -0.386081                    -5.433012                                      -2.293434                                   -3.334452                             0.396067           1.0    391.419880 skel_fb9325ceddb1ac6f      0.996265       1.000000
a7ff7e_a5d58d0a148c1372 SafeDiv(Delta(mark_index_basis_bps,12),Abs(Clip(ZScore(taker_buy_sell_volume_ratio_last),-3,3)))   basis_premium_like|positioning_like       safe_div_abs  L5_vol_adjusted_return                4                    -1.0                            3                 True                  0.997919                     0.129596    True                   0.658549                1.717598       True               0.219414               0.218814                0.217814         95.466667               A7FF12S01_NUMERIC_CLUE           704               -0.017797         -0.889396                           -0.468551                        -1.230708                  0.495739                  716                      -0.030331                -1.637442                                  -0.658549                               -1.717598                         0.476257            716                -0.059559          -1.977204                            -0.926936                         -1.773526                   0.446927                      716                          -0.219814                    -5.089589                                      -2.727109                                   -3.433866                             0.446927           1.0    224.816267 skel_6a3533b4d89c4d45      0.996265       0.998429
a7ff7e_620758ad5441a864                        Mul(Clip(ZScore(mark_index_basis_bps),-3,3),CSRank(mark_trade_basis_bps)) basis_premium_like|basis_premium_like                mul  L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.748871                     0.027455    True                   4.241249                4.241249       True               0.090032               0.089432                0.088432         95.866667               A7FF12S01_NUMERIC_CLUE           719               -0.016005         -1.610707                           -1.610707                        -1.610707                  0.482615                  719                      -0.070059                -7.012271                                  -7.012271                               -7.012271                         0.360223            719                -0.073390          -5.562723                            -5.562723                         -5.562723                   0.400556                      719                          -0.090432                    -4.241249                                      -4.241249                                   -4.241249                             0.438108           1.0     95.683587 skel_3363cfb4025bd87d      0.999713       1.000000
a7ff7e_a3368f0b979e0c23          SafeDiv(Delta(mark_index_basis_bps,12),Abs(Delta(taker_buy_sell_volume_ratio_last,12)))   basis_premium_like|positioning_like       safe_div_abs  L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.280504                     0.041190    True                   4.147947                4.147947       True               0.084211               0.083611                0.082611         95.866667               A7FF12S01_NUMERIC_CLUE           707               -0.011862         -1.224594                           -1.224594                        -1.224594                  0.473833                  719                      -0.046191                -4.348240                                  -4.348240                               -4.348240                         0.426982            719                -0.073660          -5.668908                            -5.668908                         -5.668908                   0.390821                      719                          -0.084611                    -4.147947                                      -4.147947                                   -4.147947                             0.438108           1.0     90.330691 skel_3afee12eb6a9078f      0.996259       0.998429
a7ff7e_10e4997b8ce12a81                         Mean(Mul(Delta(mark_index_basis_bps,12),CSRank(mark_trade_basis_bps)),4) basis_premium_like|basis_premium_like smooth_interaction  L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.580525                     0.046330    True                   2.240008                2.240008       True               0.082158               0.081558                0.080558         95.866667               A7FF12S01_NUMERIC_CLUE           704               -0.006686         -0.636954                           -0.636954                        -0.636954                  0.495739                  719                      -0.029241                -2.865254                                  -2.865254                               -2.865254                         0.449235            719                -0.029475          -2.240008                            -2.240008                         -2.240008                   0.440890                      719                          -0.082558                    -3.954551                                      -3.954551                                   -3.954551                             0.439499           1.0     87.976984 skel_1128a9bc5ebfee1a      0.995404       0.999985
a7ff7e_ee5c7c19146e781f     Sub(CSRank(Delta(mark_index_basis_bps,12)),CSRank(CSRank(taker_buy_sell_volume_ratio_last)))   basis_premium_like|positioning_like        spread_rank  L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.236964                     0.032839    True                   3.903938                3.903938       True               0.062838               0.062238                0.061238         95.866667               A7FF12S01_NUMERIC_CLUE           707               -0.014191         -1.507964                           -1.507964                        -1.507964                  0.459689                  719                      -0.046213                -5.219320                                  -5.219320                               -5.219320                         0.390821            719                -0.076679          -6.646303                            -6.646303                         -6.646303                   0.378303                      719                          -0.063238                    -3.903938                                      -3.903938                                   -3.903938                             0.443672           1.0     69.001177 skel_9505754fb4b5368b      0.996265       0.988673
a7ff7e_3a7fd6027d1b52ff                     Mul(CSRank(mark_index_basis_bps),Sign(Clip(ZScore(premium_close_bps),-3,3))) basis_premium_like|basis_premium_like         gated_sign  L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.699426                     0.024745    True                   3.405571                3.405571       True               0.062054               0.061454                0.060454         95.866667               A7FF12S01_NUMERIC_CLUE           719               -0.011180         -1.185717                           -1.185717                        -1.185717                  0.478442                  719                      -0.049157                -4.574638                                  -4.574638                               -4.574638                         0.392211            719                -0.061617          -4.957567                            -4.957567                         -4.957567                   0.425591                      719                          -0.062454                    -3.405571                                      -3.405571                                   -3.405571                             0.438108           1.0     67.754681 skel_8ee95cdec48a7c8f      0.999713       1.000000
a7ff7e_b973542a7bbecc8a                    Mean(Mul(CSRank(mark_index_basis_bps),Clip(ZScore(realized_vol_24h),-3,3)),4)    basis_premium_like|volatility_like smooth_interaction L7_ranked_future_return                1                    -1.0                            3                 True                  0.925021                     0.029030    True                   1.769101                1.769101       True               0.028250               0.027650                0.026650         95.866667 A7FF12S01_RANK_LABEL_DIAGNOSTIC_CLUE           716               -0.034451         -3.772193                           -3.772193                        -3.772193                  0.431564                  719                      -0.016299                -1.769101                                  -1.769101                               -1.769101                         0.464534            719                -0.024702          -3.203805                            -3.203805                         -3.203805                   0.424200                      719                          -0.028650                    -4.103006                                      -4.103006                                   -4.103006                             0.442281           0.0     32.725320 skel_3556a63fd42ae167      0.826487       1.000000
a7ff7e_949f0db2f2737f09                   Mul(Delta(Delta(mark_index_basis_bps,12),4),ZScore(CSRank(premium_close_bps))) basis_premium_like|basis_premium_like     relative_shock L7_ranked_future_return                8                    -1.0                            3                 True                  0.938302                     0.005707    True                   0.784750                1.512813       True               0.012637               0.012037                0.011037         94.933333 A7FF12S01_RANK_LABEL_DIAGNOSTIC_CLUE           696               -0.009190         -1.753968                           -0.594458                        -2.365346                  0.498563                  712                      -0.009808                -2.007570                                  -1.118356                               -1.512813                         0.471910            712                -0.012216          -2.220103                            -1.079622                         -1.567001                   0.449438                      712                          -0.013037                    -2.356450                                      -0.784750                                   -2.537980                             0.471910           0.0     17.099112 skel_3a90084955c27d13      0.995116       0.999308
```

## Boundary

```text
No May/post-selection stress is used in scoring or authorization.
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
L7 ranked-return rows remain diagnostic-only and cannot promote without non-L7 support.
```
