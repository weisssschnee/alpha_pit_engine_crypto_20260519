# CRYPTO A7FF-12S06 EXPANDED NUMERIC PROBE

Generated: 2026-05-30T04:04:37Z

## Decision

`PASS_A7FF12S06_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH`

A7FF-12S06 materializes the A7FF-7E selected blueprint queue and evaluates label response, controls, non-overlap statistics, and a dry portfolio marginal proxy. It is not formula search or alpha proof.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FF12S06_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH",
  "executes_generation": false,
  "executes_numeric_probe": true,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T04:04:37Z",
  "input_blueprint_count": 90,
  "label_response_rows": 1800,
  "materialized_activity_ok_count": 90,
  "non_l7_numeric_clue_rows": 20,
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
  "portfolio_queue_count": 17,
  "queue_limit": 90,
  "queue_offset": 540,
  "queue_path": "D:\\HermesWorker\\GDrive\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519_remote\\runtime\\a7ff12_numeric_wave_queue_contract\\a7ff12_numeric_wave_queue.csv",
  "queue_total_rows": 720,
  "rank_label_diagnostic_clue_rows": 11,
  "selected_portfolio_queue_count": 11,
  "stage": "A7FF-12S06",
  "uses_may": false
}
```

## Decision Counts

```text
                            decision                       label_family  count
              A7FF12S06_NUMERIC_CLUE              L0_raw_forward_return      3
              A7FF12S06_NUMERIC_CLUE L1_cross_sectional_relative_return      4
              A7FF12S06_NUMERIC_CLUE  L3_liquidity_tier_relative_return      5
              A7FF12S06_NUMERIC_CLUE             L5_vol_adjusted_return      8
A7FF12S06_RANK_LABEL_DIAGNOSTIC_CLUE            L7_ranked_future_return     11
    HOLD_A7FF12S06_CONTROL_DOMINATED              L0_raw_forward_return     86
    HOLD_A7FF12S06_CONTROL_DOMINATED L1_cross_sectional_relative_return     87
    HOLD_A7FF12S06_CONTROL_DOMINATED  L3_liquidity_tier_relative_return     77
    HOLD_A7FF12S06_CONTROL_DOMINATED             L5_vol_adjusted_return     91
    HOLD_A7FF12S06_CONTROL_DOMINATED            L7_ranked_future_return     98
  HOLD_A7FF12S06_COST2_PROXY_FRAGILE              L0_raw_forward_return      1
  HOLD_A7FF12S06_ONE_BAR_LAG_FRAGILE              L0_raw_forward_return     20
  HOLD_A7FF12S06_ONE_BAR_LAG_FRAGILE L1_cross_sectional_relative_return     19
  HOLD_A7FF12S06_ONE_BAR_LAG_FRAGILE  L3_liquidity_tier_relative_return     18
  HOLD_A7FF12S06_ONE_BAR_LAG_FRAGILE             L5_vol_adjusted_return     26
  HOLD_A7FF12S06_ONE_BAR_LAG_FRAGILE            L7_ranked_future_return     37
     HOLD_A7FF12S06_PRE_MAY_UNSTABLE              L0_raw_forward_return    250
     HOLD_A7FF12S06_PRE_MAY_UNSTABLE L1_cross_sectional_relative_return    250
     HOLD_A7FF12S06_PRE_MAY_UNSTABLE  L3_liquidity_tier_relative_return    260
     HOLD_A7FF12S06_PRE_MAY_UNSTABLE             L5_vol_adjusted_return    235
     HOLD_A7FF12S06_PRE_MAY_UNSTABLE            L7_ranked_future_return    214
```

## Family Summary

```text
                        semantic_pair                             decision  count
basis_premium_like|basis_premium_like               A7FF12S06_NUMERIC_CLUE      5
basis_premium_like|basis_premium_like A7FF12S06_RANK_LABEL_DIAGNOSTIC_CLUE      8
basis_premium_like|basis_premium_like     HOLD_A7FF12S06_CONTROL_DOMINATED    137
basis_premium_like|basis_premium_like   HOLD_A7FF12S06_ONE_BAR_LAG_FRAGILE     39
basis_premium_like|basis_premium_like      HOLD_A7FF12S06_PRE_MAY_UNSTABLE    311
  basis_premium_like|positioning_like               A7FF12S06_NUMERIC_CLUE      9
  basis_premium_like|positioning_like A7FF12S06_RANK_LABEL_DIAGNOSTIC_CLUE      2
  basis_premium_like|positioning_like     HOLD_A7FF12S06_CONTROL_DOMINATED    140
  basis_premium_like|positioning_like   HOLD_A7FF12S06_COST2_PROXY_FRAGILE      1
  basis_premium_like|positioning_like   HOLD_A7FF12S06_ONE_BAR_LAG_FRAGILE     43
  basis_premium_like|positioning_like      HOLD_A7FF12S06_PRE_MAY_UNSTABLE    405
        basis_premium_like|price_like     HOLD_A7FF12S06_CONTROL_DOMINATED     54
        basis_premium_like|price_like      HOLD_A7FF12S06_PRE_MAY_UNSTABLE    146
   basis_premium_like|volatility_like               A7FF12S06_NUMERIC_CLUE      6
   basis_premium_like|volatility_like A7FF12S06_RANK_LABEL_DIAGNOSTIC_CLUE      1
   basis_premium_like|volatility_like     HOLD_A7FF12S06_CONTROL_DOMINATED    108
   basis_premium_like|volatility_like   HOLD_A7FF12S06_ONE_BAR_LAG_FRAGILE     38
   basis_premium_like|volatility_like      HOLD_A7FF12S06_PRE_MAY_UNSTABLE    347
```

## Control Summary

```text
             control  median_ratio   max_ratio  rows
         one_bar_lag      0.799032 1393.166846  5400
 same_family_placebo      0.342271 1823.014500  5400
           sign_flip      0.997326  343.057958  5400
      symbol_shuffle      0.461477 1316.731799  5400
        time_shuffle      0.459866 1905.228708  5400
wrong_lag_future_24h      1.619489 5825.262846  5400
wrong_lag_stale_168h      0.564468  726.904500  5400
```

## Selected Portfolio Queue

```text
           blueprint_id                                                                                                            expression                         semantic_pair              motif            label_family  label_horizon_h  orientation_from_train  premay_positive_split_count  premay_all_positive  control_ratio_premay_max  one_bar_lag_recent_oriented  lag_ok  robust_median_tstat_floor  robust_min_tstat_floor  robust_ok  cost2_recent_oriented  cost5_recent_oriented  cost10_recent_oriented  avg_n_obs_recent                             decision  train_2024_n  train_2024_mean_spread  train_2024_tstat  train_2024_nonoverlap_median_tstat  train_2024_nonoverlap_min_tstat  train_2024_positive_rate  validation_2025H1_n  validation_2025H1_mean_spread  validation_2025H1_tstat  validation_2025H1_nonoverlap_median_tstat  validation_2025H1_nonoverlap_min_tstat  validation_2025H1_positive_rate  test_2025H2_n  test_2025H2_mean_spread  test_2025H2_tstat  test_2025H2_nonoverlap_median_tstat  test_2025H2_nonoverlap_min_tstat  test_2025H2_positive_rate  recent_oos_2026JanApr_n  recent_oos_2026JanApr_mean_spread  recent_oos_2026JanApr_tstat  recent_oos_2026JanApr_nonoverlap_median_tstat  recent_oos_2026JanApr_nonoverlap_min_tstat  recent_oos_2026JanApr_positive_rate  non_l7_bonus  score_no_may          skeleton_key  finite_share  nonzero_share
a7ff7e_a48e09102d74d50c                  Sub(CSRank(Delta(mark_index_basis_bps,12)),CSRank(Sign(Delta(taker_buy_sell_volume_ratio_last,24))))   basis_premium_like|positioning_like        spread_rank  L5_vol_adjusted_return                4                    -1.0                            3                 True                  0.729971                     0.091010    True                   1.430730                1.750881       True               0.151933               0.151333                0.150333         95.466667               A7FF12S06_NUMERIC_CLUE           692               -0.010347         -0.544753                           -0.034757                        -2.044138                  0.486994                  716                      -0.061471                -3.317503                                  -1.626024                               -2.917019                         0.452514            716                -0.069949          -2.448783                            -1.430730                         -1.750881                   0.453911                      716                          -0.152333                    -4.406307                                      -2.223129                                   -2.712880                             0.434358           1.0    157.602856 skel_af8c1327eb17d836      0.992818       0.994768
a7ff7e_6e74b01b225fb089                                   Sub(CSRank(Delta(mark_index_basis_bps,1)),CSRank(taker_buy_sell_volume_ratio_last))   basis_premium_like|positioning_like        spread_rank  L5_vol_adjusted_return               24                    -1.0                            3                 True                  0.990454                     0.097689    True                   0.250621                1.607551       True               0.146461               0.145861                0.144861         92.800000               A7FF12S06_NUMERIC_CLUE           695               -0.059604         -1.393783                           -0.236761                        -2.475805                  0.496403                  696                      -0.075239                -1.664106                                  -0.250621                               -1.725076                         0.472701            696                -0.120729          -1.974459                            -0.791943                         -2.060035                   0.464080                      696                          -0.146861                    -1.365937                                      -0.347856                                   -1.607551                             0.468391           1.0    151.870200 skel_51c2bb588b20fa9e      0.999425       0.988467
a7ff7e_2959fcddf1a8a931                                                      SafeDiv(mark_index_basis_bps,Abs(Abs(ZScore(realized_vol_24h))))    basis_premium_like|volatility_like       safe_div_abs  L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.354593                     0.031876    True                   6.826407                6.826407       True               0.124334               0.123734                0.122734         95.866667               A7FF12S06_NUMERIC_CLUE           719               -0.004464         -0.450112                           -0.450112                        -0.450112                  0.467316                  719                      -0.081165                -8.568455                                  -8.568455                               -8.568455                         0.331015            719                -0.103338          -8.021103                            -8.021103                         -8.021103                   0.358832                      719                          -0.124734                    -6.826407                                      -6.826407                                   -6.826407                             0.378303           1.0    130.379462 skel_6a4becaf6b891485      0.827348       0.987109
a7ff7e_3f00678c83674dd0                                                                           Mul(mark_index_basis_bps,premium_close_bps) basis_premium_like|basis_premium_like                mul  L5_vol_adjusted_return                1                     1.0                            3                 True                  0.840804                     0.117828    True                   1.079350                1.079350       True               0.076334               0.075734                0.074734         95.866667               A7FF12S06_NUMERIC_CLUE           630                0.005566          0.416083                            0.416083                         0.416083                  0.509524                  484                       0.045514                 2.242658                                   2.242658                                2.242658                         0.570248            356                 0.042267           1.079350                             1.079350                          1.079350                   0.558989                      345                           0.076734                     1.345500                                       1.345500                                    1.345500                             0.547826           1.0     81.893128 skel_337820bc5afcf6cc      0.999713       0.663114
a7ff7e_4a9c51c5031a59db                                    Sub(CSRank(Delta(mark_index_basis_bps,12)),CSRank(Abs(ZScore(premium_close_bps)))) basis_premium_like|basis_premium_like        spread_rank  L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.825144                     0.031786    True                   1.690097                1.690097       True               0.071549               0.070949                0.069949         95.866667               A7FF12S06_NUMERIC_CLUE           707               -0.013823         -1.301791                           -1.301791                        -1.301791                  0.479491                  719                      -0.017196                -1.690097                                  -1.690097                               -1.690097                         0.456189            719                -0.056734          -4.305873                            -4.305873                         -4.305873                   0.413074                      719                          -0.071949                    -3.369512                                      -3.369512                                   -3.369512                             0.429764           1.0     77.123451 skel_9469c26a042e7c04      0.996265       0.990535
a7ff7e_763aa78353f27ef2                        Sub(CSRank(Abs(ZScore(mark_index_basis_bps))),CSRank(Clip(ZScore(mark_trade_basis_bps),-3,3))) basis_premium_like|basis_premium_like        spread_rank L7_ranked_future_return                4                    -1.0                            3                 True                  0.249798                     0.011893    True                   3.521694                4.931660       True               0.044350               0.043750                0.042750         95.466667 A7FF12S06_RANK_LABEL_DIAGNOSTIC_CLUE           716               -0.012919         -2.422440                           -1.364219                        -2.090699                  0.462291                  716                      -0.037836                -7.473166                                  -3.521694                               -5.565278                         0.396648            716                -0.056112         -11.155889                            -5.554062                         -6.234217                   0.344972                      716                          -0.044750                    -8.236315                                      -3.964894                                   -4.931660                             0.382682           0.0     49.500326 skel_0920ca84b1bf8265      0.999713       0.991089
a7ff7e_6b5025690f81f80e                                 Sub(CSRank(Abs(ZScore(mark_index_basis_bps))),CSRank(Delta(mark_trade_basis_bps,12))) basis_premium_like|basis_premium_like        spread_rank L7_ranked_future_return                8                    -1.0                            3                 True                  0.490700                     0.017889    True                   1.770868                3.678114       True               0.040193               0.039593                0.038593         94.933333 A7FF12S06_RANK_LABEL_DIAGNOSTIC_CLUE           700               -0.010423         -1.892051                           -0.757850                        -1.806642                  0.474286                  712                      -0.023564                -4.515095                                  -1.770868                               -3.678114                         0.449438            712                -0.040238          -7.980080                            -2.932742                         -4.265574                   0.389045                      712                          -0.040593                    -7.081780                                      -2.303539                                   -4.653532                             0.390449           0.0     45.101877 skel_ad33410941dac81e      0.996265       0.989758
a7ff7e_a8ea0c957a144109                                    Mean(Mul(Abs(ZScore(mark_index_basis_bps)),Clip(ZScore(realized_vol_24h),-3,3)),4)    basis_premium_like|volatility_like smooth_interaction L7_ranked_future_return                1                    -1.0                            3                 True                  0.919391                     0.025356    True                   1.987709                1.987709       True               0.029676               0.029076                0.028076         95.866667 A7FF12S06_RANK_LABEL_DIAGNOSTIC_CLUE           716               -0.038839         -4.757147                           -4.757147                        -4.757147                  0.423184                  719                      -0.016165                -1.987709                                  -1.987709                               -1.987709                         0.474270            719                -0.020242          -3.019323                            -3.019323                         -3.019323                   0.464534                      719                          -0.030076                    -4.693135                                      -4.693135                                   -4.693135                             0.422809           0.0     34.156300 skel_e43d9a5532e53e6c      0.826487       1.000000
a7ff7e_f837c3c0cf719a34                                              Mean(Mul(CSRank(mark_index_basis_bps),Abs(ZScore(premium_close_bps))),4) basis_premium_like|basis_premium_like smooth_interaction L7_ranked_future_return                1                    -1.0                            3                 True                  0.707479                     0.011858    True                   2.859051                2.859051       True               0.015189               0.014589                0.013589         95.866667 A7FF12S06_RANK_LABEL_DIAGNOSTIC_CLUE           716               -0.007804         -1.375717                           -1.375717                        -1.375717                  0.483240                  719                      -0.018156                -3.407005                                  -3.407005                               -3.407005                         0.439499            719                -0.022141          -4.193253                            -4.193253                         -4.193253                   0.435327                      719                          -0.015589                    -2.859051                                      -2.859051                                   -2.859051                             0.456189           0.0     19.881704 skel_32071dde7bd0d434      0.998851       1.000000
a7ff7e_2649bc60f060f7bc                                     Mul(Delta(CSRank(mark_index_basis_bps),4),ZScore(Abs(ZScore(premium_close_bps)))) basis_premium_like|basis_premium_like     relative_shock L7_ranked_future_return                8                     1.0                            3                 True                  0.945016                     0.008411    True                   0.463238               -1.609379       True               0.012286               0.011686                0.010686         94.933333 A7FF12S06_RANK_LABEL_DIAGNOSTIC_CLUE           708                0.003871          0.739911                            0.007185                        -0.786170                  0.512712                  712                       0.004350                 0.879965                                   0.463238                               -1.609379                         0.518258            712                 0.010777           1.999671                             0.924420                         -0.292304                   0.529494                      712                           0.012686                     2.517639                                       0.979344                                   -0.176281                             0.525281           0.0     16.740610 skel_212ff8a4592ba496      0.998564       0.976086
a7ff7e_4af893d8e65aae33 Mul(Delta(Clip(ZScore(mark_index_basis_bps),-3,3),4),ZScore(Clip(ZScore(global_long_short_account_ratio_last),-3,3)))   basis_premium_like|positioning_like     relative_shock L7_ranked_future_return                8                    -1.0                            3                 True                  0.998600                     0.004109    True                   0.572584                1.686241       True               0.011971               0.011371                0.010371         94.933333 A7FF12S06_RANK_LABEL_DIAGNOSTIC_CLUE           708               -0.008205         -1.507227                           -0.572880                        -2.315845                  0.490113                  712                      -0.016809                -3.298820                                  -1.259176                               -2.162062                         0.439607            712                -0.006526          -1.200175                            -0.572584                         -2.038750                   0.470506                      712                          -0.012371                    -2.184019                                      -0.733455                                   -1.686241                             0.480337           0.0     16.372086 skel_aa3d13111ce1711c      0.998564       0.998861
```

## Boundary

```text
No May/post-selection stress is used in scoring or authorization.
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
L7 ranked-return rows remain diagnostic-only and cannot promote without non-L7 support.
```
