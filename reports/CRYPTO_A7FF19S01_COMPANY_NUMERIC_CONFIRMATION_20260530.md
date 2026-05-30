# CRYPTO A7FF-19S01 EXPANDED NUMERIC PROBE

Generated: 2026-05-30T05:06:08Z

## Decision

`PASS_A7FF19S01_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH`

A7FF-19S01 materializes the A7FF-7E selected blueprint queue and evaluates label response, controls, non-overlap statistics, and a dry portfolio marginal proxy. It is not formula search or alpha proof.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FF19S01_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH",
  "executes_generation": false,
  "executes_numeric_probe": true,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T05:06:08Z",
  "input_blueprint_count": 28,
  "label_response_rows": 560,
  "materialized_activity_ok_count": 28,
  "non_l7_numeric_clue_rows": 146,
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
  "portfolio_queue_count": 28,
  "queue_limit": 28,
  "queue_offset": 28,
  "queue_path": "D:\\HermesWorker\\GDrive\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519_remote\\runtime\\a7ff19_external_selector_confirmation_contract\\a7ff19_execution_queue.csv",
  "queue_total_rows": 56,
  "rank_label_diagnostic_clue_rows": 28,
  "selected_portfolio_queue_count": 21,
  "stage": "A7FF-19S01",
  "uses_may": false
}
```

## Decision Counts

```text
                            decision                       label_family  count
              A7FF19S01_NUMERIC_CLUE              L0_raw_forward_return     36
              A7FF19S01_NUMERIC_CLUE L1_cross_sectional_relative_return     37
              A7FF19S01_NUMERIC_CLUE  L3_liquidity_tier_relative_return     34
              A7FF19S01_NUMERIC_CLUE             L5_vol_adjusted_return     39
A7FF19S01_RANK_LABEL_DIAGNOSTIC_CLUE            L7_ranked_future_return     28
    HOLD_A7FF19S01_CONTROL_DOMINATED              L0_raw_forward_return     36
    HOLD_A7FF19S01_CONTROL_DOMINATED L1_cross_sectional_relative_return     35
    HOLD_A7FF19S01_CONTROL_DOMINATED  L3_liquidity_tier_relative_return     29
    HOLD_A7FF19S01_CONTROL_DOMINATED             L5_vol_adjusted_return     31
    HOLD_A7FF19S01_CONTROL_DOMINATED            L7_ranked_future_return     11
  HOLD_A7FF19S01_COST2_PROXY_FRAGILE  L3_liquidity_tier_relative_return      1
  HOLD_A7FF19S01_ONE_BAR_LAG_FRAGILE  L3_liquidity_tier_relative_return      1
  HOLD_A7FF19S01_ONE_BAR_LAG_FRAGILE             L5_vol_adjusted_return     10
  HOLD_A7FF19S01_ONE_BAR_LAG_FRAGILE            L7_ranked_future_return     34
     HOLD_A7FF19S01_PRE_MAY_UNSTABLE              L0_raw_forward_return     40
     HOLD_A7FF19S01_PRE_MAY_UNSTABLE L1_cross_sectional_relative_return     40
     HOLD_A7FF19S01_PRE_MAY_UNSTABLE  L3_liquidity_tier_relative_return     47
     HOLD_A7FF19S01_PRE_MAY_UNSTABLE             L5_vol_adjusted_return     32
     HOLD_A7FF19S01_PRE_MAY_UNSTABLE            L7_ranked_future_return     39
```

## Family Summary

```text
                        semantic_pair                             decision  count
basis_premium_like|basis_premium_like               A7FF19S01_NUMERIC_CLUE     13
basis_premium_like|basis_premium_like A7FF19S01_RANK_LABEL_DIAGNOSTIC_CLUE      4
basis_premium_like|basis_premium_like     HOLD_A7FF19S01_CONTROL_DOMINATED     11
basis_premium_like|basis_premium_like   HOLD_A7FF19S01_ONE_BAR_LAG_FRAGILE      2
basis_premium_like|basis_premium_like      HOLD_A7FF19S01_PRE_MAY_UNSTABLE     10
  basis_premium_like|positioning_like               A7FF19S01_NUMERIC_CLUE     60
  basis_premium_like|positioning_like A7FF19S01_RANK_LABEL_DIAGNOSTIC_CLUE     11
  basis_premium_like|positioning_like     HOLD_A7FF19S01_CONTROL_DOMINATED     61
  basis_premium_like|positioning_like   HOLD_A7FF19S01_COST2_PROXY_FRAGILE      1
  basis_premium_like|positioning_like   HOLD_A7FF19S01_ONE_BAR_LAG_FRAGILE     22
  basis_premium_like|positioning_like      HOLD_A7FF19S01_PRE_MAY_UNSTABLE     85
        basis_premium_like|price_like               A7FF19S01_NUMERIC_CLUE     28
        basis_premium_like|price_like A7FF19S01_RANK_LABEL_DIAGNOSTIC_CLUE      6
        basis_premium_like|price_like     HOLD_A7FF19S01_CONTROL_DOMINATED     22
        basis_premium_like|price_like   HOLD_A7FF19S01_ONE_BAR_LAG_FRAGILE      5
        basis_premium_like|price_like      HOLD_A7FF19S01_PRE_MAY_UNSTABLE     19
   basis_premium_like|volatility_like               A7FF19S01_NUMERIC_CLUE     45
   basis_premium_like|volatility_like A7FF19S01_RANK_LABEL_DIAGNOSTIC_CLUE      7
   basis_premium_like|volatility_like     HOLD_A7FF19S01_CONTROL_DOMINATED     48
   basis_premium_like|volatility_like   HOLD_A7FF19S01_ONE_BAR_LAG_FRAGILE     16
   basis_premium_like|volatility_like      HOLD_A7FF19S01_PRE_MAY_UNSTABLE     84
```

## Control Summary

```text
             control  median_ratio   max_ratio  rows
         one_bar_lag      0.404977  764.515989  1680
 same_family_placebo      0.158140  364.869767  1680
           sign_flip      1.004245  110.590068  1680
      symbol_shuffle      0.177029 3577.244099  1680
        time_shuffle      0.195587  388.166324  1680
wrong_lag_future_24h      0.405906 4935.573098  1680
wrong_lag_stale_168h      0.244983  617.022667  1680
```

## Selected Portfolio Queue

```text
           blueprint_id                                                                                                        expression                         semantic_pair        motif                       label_family  label_horizon_h  orientation_from_train  premay_positive_split_count  premay_all_positive  control_ratio_premay_max  one_bar_lag_recent_oriented  lag_ok  robust_median_tstat_floor  robust_min_tstat_floor  robust_ok  cost2_recent_oriented  cost5_recent_oriented  cost10_recent_oriented  avg_n_obs_recent               decision  train_2024_n  train_2024_mean_spread  train_2024_tstat  train_2024_nonoverlap_median_tstat  train_2024_nonoverlap_min_tstat  train_2024_positive_rate  validation_2025H1_n  validation_2025H1_mean_spread  validation_2025H1_tstat  validation_2025H1_nonoverlap_median_tstat  validation_2025H1_nonoverlap_min_tstat  validation_2025H1_positive_rate  test_2025H2_n  test_2025H2_mean_spread  test_2025H2_tstat  test_2025H2_nonoverlap_median_tstat  test_2025H2_nonoverlap_min_tstat  test_2025H2_positive_rate  recent_oos_2026JanApr_n  recent_oos_2026JanApr_mean_spread  recent_oos_2026JanApr_tstat  recent_oos_2026JanApr_nonoverlap_median_tstat  recent_oos_2026JanApr_nonoverlap_min_tstat  recent_oos_2026JanApr_positive_rate  non_l7_bonus  score_no_may          skeleton_key  finite_share  nonzero_share
a7ff7e_f05cfb85e23e4866                                      Sub(Delta(mark_index_basis_bps,12),CSRank(taker_buy_sell_volume_ratio_last))   basis_premium_like|positioning_like          sub             L5_vol_adjusted_return                8                    -1.0                            3                 True                  0.608480                     0.248405    True                   0.487614                2.259681       True               0.391766               0.391166                0.390166         94.933333 A7FF19S01_NUMERIC_CLUE           700               -0.010969         -0.372441                           -0.180336                        -1.485012                  0.482857                  712                      -0.051710                -1.893768                                  -0.487614                               -2.456957                         0.449438            712                -0.145430          -3.522668                            -1.352877                         -2.259681                   0.450843                      712                          -0.392166                    -5.538064                                      -2.358803                                   -3.320284                             0.407303           1.0    397.557992 skel_136259b72205469f      0.996265       1.000000
a7ff7e_b5ca9f3f6b8f16d6                                               Mul(Delta(mark_index_basis_bps,12),Sign(CSRank(premium_close_bps))) basis_premium_like|basis_premium_like   gated_sign             L5_vol_adjusted_return                8                    -1.0                            3                 True                  0.619643                     0.247474    True                   0.626901                2.325739       True               0.389848               0.389248                0.388248         94.933333 A7FF19S01_NUMERIC_CLUE           700               -0.015016         -0.519622                           -0.175288                        -1.634500                  0.480000                  712                      -0.055726                -2.018783                                  -0.626901                               -2.526720                         0.441011            712                -0.137832          -3.261929                            -1.329647                         -2.325739                   0.450843                      712                          -0.390248                    -5.507264                                      -2.333339                                   -3.278556                             0.411517           1.0    395.628179 skel_069f2015163fa7ef      0.996265       0.998429
a7ff7e_f8a8d6cf8b654e64                     SafeDiv(Delta(mark_index_basis_bps,12),Abs(Sign(Delta(taker_buy_sell_volume_ratio_last,24))))   basis_premium_like|positioning_like safe_div_abs             L5_vol_adjusted_return                8                    -1.0                            3                 True                  0.949478                     0.247474    True                   0.626901                2.325739       True               0.389848               0.389248                0.388248         94.933333 A7FF19S01_NUMERIC_CLUE           688               -0.010310         -0.356333                           -0.086228                        -1.421863                  0.482558                  712                      -0.055726                -2.018783                                  -0.626901                               -2.526720                         0.441011            712                -0.137832          -3.261929                            -1.329647                         -2.325739                   0.450843                      712                          -0.390248                    -5.507264                                      -2.333339                                   -3.278556                             0.411517           1.0    395.298343 skel_156d0fafafecde17      0.992818       0.998424
a7ff7e_bddf5c5d29f96eb6                                       SafeDiv(Delta(mark_index_basis_bps,12),Abs(Abs(ZScore(realized_vol_168h))))    basis_premium_like|volatility_like safe_div_abs             L5_vol_adjusted_return                8                    -1.0                            3                 True                  0.951985                     0.148118    True                   0.605819                1.660845       True               0.282372               0.281772                0.280772         94.933333 A7FF19S01_NUMERIC_CLUE           700               -0.038305         -1.653403                           -0.731959                        -2.225679                  0.468571                  712                      -0.041159                -1.770665                                  -0.605819                               -1.660845                         0.471910            712                -0.142467          -3.501255                            -1.353236                         -2.476762                   0.438202                      712                          -0.282772                    -4.108667                                      -1.381269                                   -2.667281                             0.436798           1.0    287.820245 skel_3d008dc9486239b2      0.823901       0.998297
a7ff7e_6445196984a5b167                                 SafeDiv(Delta(mark_index_basis_bps,12),Abs(Clip(ZScore(realized_vol_168h),-3,3)))    basis_premium_like|volatility_like safe_div_abs             L5_vol_adjusted_return                8                    -1.0                            3                 True                  0.818697                     0.147583    True                   0.605819                1.660845       True               0.281496               0.280896                0.279896         94.933333 A7FF19S01_NUMERIC_CLUE           700               -0.039019         -1.681025                           -0.715018                        -2.352851                  0.467143                  712                      -0.041566                -1.787552                                  -0.605819                               -1.660845                         0.471910            712                -0.143515          -3.528527                            -1.353236                         -2.571248                   0.436798                      712                          -0.281896                    -4.094412                                      -1.387993                                   -2.633692                             0.436798           1.0    287.077139 skel_6a3533b4d89c4d45      0.823901       0.998297
a7ff7e_3a7e3ddbe5462bea                                                     Sub(Delta(mark_index_basis_bps,12),Delta(trade_return_24h,1))         basis_premium_like|price_like          sub             L5_vol_adjusted_return                4                    -1.0                            3                 True                  0.458478                     0.139516    True                   0.843150                2.306915       True               0.273078               0.272478                0.271478         95.466667 A7FF19S01_NUMERIC_CLUE           704               -0.013531         -0.646727                           -0.135300                        -1.195968                  0.485795                  716                      -0.049791                -2.693710                                  -0.843150                               -3.055159                         0.460894            716                -0.096765          -3.176256                            -1.547708                         -2.306915                   0.409218                      716                          -0.273478                    -6.028896                                      -3.147858                                   -3.603667                             0.410615           1.0    279.019648 skel_8727d93aac220fc6      0.823901       0.999866
a7ff7e_ae49260ddd504924                                                              Mul(Delta(mark_index_basis_bps,12),realized_vol_24h)    basis_premium_like|volatility_like          mul             L5_vol_adjusted_return                4                    -1.0                            3                 True                  0.987466                     0.147043    True                   0.940767                1.334051       True               0.264030               0.263430                0.262430         95.466667 A7FF19S01_NUMERIC_CLUE           704               -0.016082         -0.718913                           -0.380529                        -0.923709                  0.480114                  716                      -0.050011                -2.465644                                  -0.957866                               -2.902237                         0.442737            716                -0.061287          -1.927214                            -0.940767                         -1.334051                   0.435754                      716                          -0.264430                    -5.568483                                      -2.757257                                   -3.329419                             0.434358           1.0    269.442581 skel_0994b3a36a4d53ba      0.823901       0.998297
a7ff7e_66fc9f6699584033                              SafeDiv(Clip(ZScore(mark_index_basis_bps),-3,3),Abs(Abs(ZScore(realized_vol_168h))))    basis_premium_like|volatility_like safe_div_abs             L5_vol_adjusted_return                4                    -1.0                            3                 True                  0.665608                     0.085539    True                   1.405437                1.999702       True               0.209207               0.208607                0.207607         95.466667 A7FF19S01_NUMERIC_CLUE           716               -0.000216         -0.012746                            0.025978                        -0.996203                  0.502793                  716                      -0.045001                -2.295061                                  -1.405437                               -1.999702                         0.430168            716                -0.135576          -4.389153                            -2.264323                         -4.005079                   0.389665                      716                          -0.209607                    -4.837209                                      -2.507846                                   -2.831217                             0.452514           1.0    214.941163 skel_79b46e3bec19bc64      0.827348       1.000000
a7ff7e_ffdab637dbab0125                                       SafeDiv(mark_index_basis_bps,Abs(CSRank(taker_buy_sell_volume_ratio_last)))   basis_premium_like|positioning_like safe_div_abs             L5_vol_adjusted_return                4                    -1.0                            3                 True                  0.892075                     0.051286    True                   1.330573                2.527708       True               0.180422               0.179822                0.178822         95.466667 A7FF19S01_NUMERIC_CLUE           716               -0.004460         -0.243583                           -0.358945                        -1.113859                  0.474860                  716                      -0.064687                -3.116657                                  -1.330573                               -3.509182                         0.416201            716                -0.090435          -3.097455                            -1.868217                         -2.527708                   0.459497                      716                          -0.180822                    -4.886136                                      -2.141755                                   -3.705698                             0.417598           1.0    185.929606 skel_06aed53e0aa5366a      0.999713       0.987410
a7ff7e_42cf23f63bb0ad8d                                                         Mul(CSRank(mark_index_basis_bps),CSRank(trade_return_1h))         basis_premium_like|price_like          mul             L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.573783                     0.060421    True                   6.650899                6.650899       True               0.175552               0.174952                0.173952         95.866667 A7FF19S01_NUMERIC_CLUE           719               -0.049667         -3.747982                           -3.747982                        -3.747982                  0.418637                  719                      -0.078454                -6.650899                                  -6.650899                               -6.650899                         0.368567            719                -0.125210          -8.186964                            -8.186964                         -8.186964                   0.333797                      719                          -0.175952                    -7.844688                                      -7.844688                                   -7.844688                             0.371349           1.0    181.378325 skel_293cae94cfd91548      0.999425       1.000000
a7ff7e_306cf26692372a73                                           Sub(Delta(mark_index_basis_bps,12),Clip(ZScore(realized_vol_24h),-3,3))    basis_premium_like|volatility_like          sub             L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.281159                     0.054148    True                   6.556910                6.556910       True               0.143395               0.142795                0.141795         95.866667 A7FF19S01_NUMERIC_CLUE           707               -0.016754         -1.565542                           -1.565542                        -1.565542                  0.463932                  719                      -0.079821                -8.701856                                  -8.701856                               -8.701856                         0.375522            719                -0.117926          -8.818725                            -8.818725                         -8.818725                   0.344924                      719                          -0.143795                    -6.556910                                      -6.556910                                   -6.556910                             0.400556           1.0    149.513348 skel_fb9325ceddb1ac6f      0.823901       1.000000
a7ff7e_77ca3b839d710afd Sub(CSRank(Clip(ZScore(mark_index_basis_bps),-3,3)),CSRank(Clip(ZScore(top_long_short_account_ratio_last),-3,3)))   basis_premium_like|positioning_like  spread_rank             L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.281607                     0.047626    True                   4.851260                4.851260       True               0.139320               0.138720                0.137720         95.866667 A7FF19S01_NUMERIC_CLUE           719               -0.007650         -0.729779                           -0.729779                        -0.729779                  0.499305                  719                      -0.053729                -4.851260                                  -4.851260                               -4.851260                         0.393602            719                -0.097653          -7.489557                            -7.489557                         -7.489557                   0.360223                      719                          -0.139720                    -6.480026                                      -6.480026                                   -6.480026                             0.408901           1.0    145.438714 skel_3d2988e4547fbd95      0.999713       0.987281
a7ff7e_ca3c03329ffd2edb                                                                Mul(CSRank(mark_index_basis_bps),realized_vol_24h)    basis_premium_like|volatility_like          mul             L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.894735                     0.041170    True                   5.504428                5.504428       True               0.127007               0.126407                0.125407         95.866667 A7FF19S01_NUMERIC_CLUE           719               -0.025653         -2.201339                           -2.201339                        -2.201339                  0.463143                  719                      -0.076344                -7.139759                                  -7.139759                               -7.139759                         0.344924            719                -0.112694          -8.160433                            -8.160433                         -8.160433                   0.351878                      719                          -0.127407                    -5.504428                                      -5.504428                                   -5.504428                             0.440890           1.0    132.512654 skel_37ba6246678096b3      0.827348       1.000000
a7ff7e_5201f3314c5dae1a                                            SafeDiv(mark_index_basis_bps,Abs(Clip(ZScore(realized_vol_24h),-3,3)))    basis_premium_like|volatility_like safe_div_abs             L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.355105                     0.031363    True                   6.804910                6.804910       True               0.123839               0.123239                0.122239         95.866667 A7FF19S01_NUMERIC_CLUE           719               -0.004231         -0.426981                           -0.426981                        -0.426981                  0.467316                  719                      -0.081079                -8.573577                                  -8.573577                               -8.573577                         0.331015            719                -0.100386          -7.746042                            -7.746042                         -7.746042                   0.360223                      719                          -0.124239                    -6.804910                                      -6.804910                                   -6.804910                             0.376912           1.0    129.884117 skel_1c4b9d5957f9af9c      0.827348       0.987109
a7ff7e_42b9aa89029367d2                                                    SafeDiv(mark_index_basis_bps,Abs(Delta(realized_vol_168h,24)))    basis_premium_like|volatility_like safe_div_abs             L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.245246                     0.030430    True                   7.280667                7.280667       True               0.106999               0.106399                0.105399         95.866667 A7FF19S01_NUMERIC_CLUE           695               -0.003147         -0.289641                           -0.289641                        -0.289641                  0.480576                  719                      -0.077038                -8.237201                                  -8.237201                               -8.237201                         0.369958            719                -0.105477          -8.113440                            -8.113440                         -8.113440                   0.357441                      719                          -0.107399                    -7.280667                                      -7.280667                                   -7.280667                             0.368567           1.0    113.153284 skel_a2f58ee62d9e7ad2      0.820454       0.987023
a7ff7e_01654e884fbd77b8                     Sub(CSRank(Delta(mark_index_basis_bps,12)),CSRank(Delta(taker_buy_sell_volume_ratio_last,1)))   basis_premium_like|positioning_like  spread_rank             L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.299274                     0.040971    True                   5.386232                5.386232       True               0.080219               0.079619                0.078619         95.866667 A7FF19S01_NUMERIC_CLUE           707               -0.016545         -1.749413                           -1.749413                        -1.749413                  0.463932                  719                      -0.055585                -6.269572                                  -6.269572                               -6.269572                         0.394993            719                -0.076832          -6.506852                            -6.506852                         -6.506852                   0.393602                      719                          -0.080619                    -5.386232                                      -5.386232                                   -5.386232                             0.415855           1.0     86.320023 skel_bcb165b7818f5d85      0.996265       0.988733
a7ff7e_058a55fa679948ae                        SafeDiv(Clip(ZScore(mark_index_basis_bps),-3,3),Abs(Clip(ZScore(realized_vol_168h),-3,3)))    basis_premium_like|volatility_like safe_div_abs L1_cross_sectional_relative_return                1                    -1.0                            3                 True                  0.169131                     0.000326    True                   4.534610                4.534610       True               0.000727               0.000127               -0.000873         95.866667 A7FF19S01_NUMERIC_CLUE           719               -0.000176         -1.239030                           -1.239030                        -1.239030                  0.454798                  719                      -0.000734                -9.189801                                  -9.189801                               -9.189801                         0.343533            719                -0.001026          -8.298438                            -8.298438                         -8.298438                   0.329624                      719                          -0.001127                    -4.534610                                      -4.534610                                   -4.534610                             0.397775           1.0      6.957523 skel_f5a350b26e95f33f      0.827348       1.000000
a7ff7e_72d1bbd3a38254c0                             SafeDiv(CSRank(mark_index_basis_bps),Abs(Delta(taker_buy_sell_volume_ratio_last,12)))   basis_premium_like|positioning_like safe_div_abs              L0_raw_forward_return                1                    -1.0                            3                 True                  0.379018                     0.000476    True                   3.807888                3.807888       True               0.000640               0.000040               -0.000960         95.866667 A7FF19S01_NUMERIC_CLUE           707               -0.000211         -1.273380                           -1.273380                        -1.273380                  0.478076                  719                      -0.000447                -4.423726                                  -4.423726                               -4.423726                         0.420028            719                -0.000560          -4.200016                            -4.200016                         -4.200016                   0.389430                      719                          -0.001040                    -3.807888                                      -3.807888                                   -3.807888                             0.453408           1.0      6.660852 skel_1a1b3fb29dff7328      0.996259       1.000000
a7ff7e_e6d01e672425fc7c                    SafeDiv(Clip(ZScore(mark_index_basis_bps),-3,3),Abs(CSRank(taker_buy_sell_volume_ratio_last)))   basis_premium_like|positioning_like safe_div_abs  L3_liquidity_tier_relative_return                1                    -1.0                            3                 True                  0.612349                     0.000305    True                   3.990189                3.990189       True               0.000813               0.000213               -0.000787         95.866667 A7FF19S01_NUMERIC_CLUE           719               -0.000304         -1.902954                           -1.902954                        -1.902954                  0.484006                  719                      -0.000677                -7.308636                                  -7.308636                               -7.308636                         0.374131            719                -0.000987          -7.103692                            -7.103692                         -7.103692                   0.351878                      719                          -0.001213                    -3.990189                                      -3.990189                                   -3.990189                             0.449235           1.0      6.600467 skel_99250fb0b3bee329      0.999713       1.000000
a7ff7e_0c7cd03187d0a1be                                                Sub(mark_index_basis_bps,CSRank(taker_buy_sell_volume_ratio_last))   basis_premium_like|positioning_like          sub  L3_liquidity_tier_relative_return                1                    -1.0                            3                 True                  0.698038                     0.000294    True                   3.611575                3.611575       True               0.000735               0.000135               -0.000865         95.866667 A7FF19S01_NUMERIC_CLUE           719               -0.000201         -1.203953                           -1.203953                        -1.203953                  0.481224                  719                      -0.000725                -6.983896                                  -6.983896                               -6.983896                         0.374131            719                -0.001133          -7.555773                            -7.555773                         -7.555773                   0.349096                      719                          -0.001135                    -3.611575                                      -3.611575                                   -3.611575                             0.450626           1.0      6.436617 skel_d9d4f69744bac825      0.999713       0.999997
a7ff7e_ddea9f3dc39ed8de                                                        Sub(mark_index_basis_bps,taker_buy_sell_volume_ratio_last)   basis_premium_like|positioning_like          sub  L3_liquidity_tier_relative_return                1                    -1.0                            3                 True                  0.829632                     0.000337    True                   3.316798                3.316798       True               0.000643               0.000043               -0.000957         95.866667 A7FF19S01_NUMERIC_CLUE           719               -0.000179         -1.086034                           -1.086034                        -1.086034                  0.479833                  719                      -0.000679                -6.638748                                  -6.638748                               -6.638748                         0.365786            719                -0.001034          -6.971260                            -6.971260                         -6.971260                   0.354659                      719                          -0.001043                    -3.316798                                      -3.316798                                   -3.316798                             0.453408           1.0      6.213269 skel_337820bc5afcf6cc      0.999713       0.999991
```

## Boundary

```text
No May/post-selection stress is used in scoring or authorization.
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
L7 ranked-return rows remain diagnostic-only and cannot promote without non-L7 support.
```
