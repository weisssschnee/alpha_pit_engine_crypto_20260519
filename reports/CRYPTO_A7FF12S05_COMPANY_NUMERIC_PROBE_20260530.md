# CRYPTO A7FF-12S05 EXPANDED NUMERIC PROBE

Generated: 2026-05-30T03:59:05Z

## Decision

`PASS_A7FF12S05_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH`

A7FF-12S05 materializes the A7FF-7E selected blueprint queue and evaluates label response, controls, non-overlap statistics, and a dry portfolio marginal proxy. It is not formula search or alpha proof.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FF12S05_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH",
  "executes_generation": false,
  "executes_numeric_probe": true,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T03:59:05Z",
  "input_blueprint_count": 90,
  "label_response_rows": 1800,
  "materialized_activity_ok_count": 90,
  "non_l7_numeric_clue_rows": 40,
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
  "portfolio_queue_count": 18,
  "queue_limit": 90,
  "queue_offset": 450,
  "queue_path": "D:\\HermesWorker\\GDrive\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519_remote\\runtime\\a7ff12_numeric_wave_queue_contract\\a7ff12_numeric_wave_queue.csv",
  "queue_total_rows": 720,
  "rank_label_diagnostic_clue_rows": 12,
  "selected_portfolio_queue_count": 13,
  "stage": "A7FF-12S05",
  "uses_may": false
}
```

## Decision Counts

```text
                            decision                       label_family  count
              A7FF12S05_NUMERIC_CLUE              L0_raw_forward_return     10
              A7FF12S05_NUMERIC_CLUE L1_cross_sectional_relative_return     10
              A7FF12S05_NUMERIC_CLUE  L3_liquidity_tier_relative_return     10
              A7FF12S05_NUMERIC_CLUE             L5_vol_adjusted_return     10
A7FF12S05_RANK_LABEL_DIAGNOSTIC_CLUE            L7_ranked_future_return     12
    HOLD_A7FF12S05_CONTROL_DOMINATED              L0_raw_forward_return     89
    HOLD_A7FF12S05_CONTROL_DOMINATED L1_cross_sectional_relative_return     89
    HOLD_A7FF12S05_CONTROL_DOMINATED  L3_liquidity_tier_relative_return     77
    HOLD_A7FF12S05_CONTROL_DOMINATED             L5_vol_adjusted_return     92
    HOLD_A7FF12S05_CONTROL_DOMINATED            L7_ranked_future_return    103
  HOLD_A7FF12S05_ONE_BAR_LAG_FRAGILE              L0_raw_forward_return     21
  HOLD_A7FF12S05_ONE_BAR_LAG_FRAGILE L1_cross_sectional_relative_return     21
  HOLD_A7FF12S05_ONE_BAR_LAG_FRAGILE  L3_liquidity_tier_relative_return     22
  HOLD_A7FF12S05_ONE_BAR_LAG_FRAGILE             L5_vol_adjusted_return     32
  HOLD_A7FF12S05_ONE_BAR_LAG_FRAGILE            L7_ranked_future_return     47
     HOLD_A7FF12S05_PRE_MAY_UNSTABLE              L0_raw_forward_return    240
     HOLD_A7FF12S05_PRE_MAY_UNSTABLE L1_cross_sectional_relative_return    240
     HOLD_A7FF12S05_PRE_MAY_UNSTABLE  L3_liquidity_tier_relative_return    251
     HOLD_A7FF12S05_PRE_MAY_UNSTABLE             L5_vol_adjusted_return    226
     HOLD_A7FF12S05_PRE_MAY_UNSTABLE            L7_ranked_future_return    198
```

## Family Summary

```text
                        semantic_pair                             decision  count
basis_premium_like|basis_premium_like               A7FF12S05_NUMERIC_CLUE      5
basis_premium_like|basis_premium_like A7FF12S05_RANK_LABEL_DIAGNOSTIC_CLUE      5
basis_premium_like|basis_premium_like     HOLD_A7FF12S05_CONTROL_DOMINATED    122
basis_premium_like|basis_premium_like   HOLD_A7FF12S05_ONE_BAR_LAG_FRAGILE     65
basis_premium_like|basis_premium_like      HOLD_A7FF12S05_PRE_MAY_UNSTABLE    323
  basis_premium_like|positioning_like               A7FF12S05_NUMERIC_CLUE     26
  basis_premium_like|positioning_like A7FF12S05_RANK_LABEL_DIAGNOSTIC_CLUE      5
  basis_premium_like|positioning_like     HOLD_A7FF12S05_CONTROL_DOMINATED    150
  basis_premium_like|positioning_like   HOLD_A7FF12S05_ONE_BAR_LAG_FRAGILE     36
  basis_premium_like|positioning_like      HOLD_A7FF12S05_PRE_MAY_UNSTABLE    323
        basis_premium_like|price_like A7FF12S05_RANK_LABEL_DIAGNOSTIC_CLUE      1
        basis_premium_like|price_like     HOLD_A7FF12S05_CONTROL_DOMINATED     58
        basis_premium_like|price_like   HOLD_A7FF12S05_ONE_BAR_LAG_FRAGILE      2
        basis_premium_like|price_like      HOLD_A7FF12S05_PRE_MAY_UNSTABLE    139
   basis_premium_like|volatility_like               A7FF12S05_NUMERIC_CLUE      9
   basis_premium_like|volatility_like A7FF12S05_RANK_LABEL_DIAGNOSTIC_CLUE      1
   basis_premium_like|volatility_like     HOLD_A7FF12S05_CONTROL_DOMINATED    120
   basis_premium_like|volatility_like   HOLD_A7FF12S05_ONE_BAR_LAG_FRAGILE     40
   basis_premium_like|volatility_like      HOLD_A7FF12S05_PRE_MAY_UNSTABLE    370
```

## Control Summary

```text
             control  median_ratio   max_ratio  rows
         one_bar_lag      0.736292 1914.226122  5400
 same_family_placebo      0.348974 1644.109306  5400
           sign_flip      0.999059  448.943034  5400
      symbol_shuffle      0.463954  377.157689  5400
        time_shuffle      0.479579 1530.449086  5400
wrong_lag_future_24h      1.472869 3034.178420  5400
wrong_lag_stale_168h      0.555837 1310.128853  5400
```

## Selected Portfolio Queue

```text
           blueprint_id                                                                                                        expression                         semantic_pair              motif                      label_family  label_horizon_h  orientation_from_train  premay_positive_split_count  premay_all_positive  control_ratio_premay_max  one_bar_lag_recent_oriented  lag_ok  robust_median_tstat_floor  robust_min_tstat_floor  robust_ok  cost2_recent_oriented  cost5_recent_oriented  cost10_recent_oriented  avg_n_obs_recent                             decision  train_2024_n  train_2024_mean_spread  train_2024_tstat  train_2024_nonoverlap_median_tstat  train_2024_nonoverlap_min_tstat  train_2024_positive_rate  validation_2025H1_n  validation_2025H1_mean_spread  validation_2025H1_tstat  validation_2025H1_nonoverlap_median_tstat  validation_2025H1_nonoverlap_min_tstat  validation_2025H1_positive_rate  test_2025H2_n  test_2025H2_mean_spread  test_2025H2_tstat  test_2025H2_nonoverlap_median_tstat  test_2025H2_nonoverlap_min_tstat  test_2025H2_positive_rate  recent_oos_2026JanApr_n  recent_oos_2026JanApr_mean_spread  recent_oos_2026JanApr_tstat  recent_oos_2026JanApr_nonoverlap_median_tstat  recent_oos_2026JanApr_nonoverlap_min_tstat  recent_oos_2026JanApr_positive_rate  non_l7_bonus  score_no_may          skeleton_key  finite_share  nonzero_share
a7ff7e_31a152b5a6d123af                 SafeDiv(Delta(mark_index_basis_bps,12),Abs(Sign(Delta(global_long_short_account_ratio_last,24))))   basis_premium_like|positioning_like       safe_div_abs            L5_vol_adjusted_return                4                    -1.0                            3                 True                  0.746835                     0.139103    True                   0.852616                2.303467       True               0.273528               0.272928                0.271928         95.462500               A7FF12S05_NUMERIC_CLUE           692               -0.008721         -0.418314                           -0.185058                        -0.998054                  0.485549                  716                      -0.049945                -2.699969                                  -0.852616                               -3.055159                         0.460894            716                -0.096646          -3.171834                            -1.543866                         -2.303467                   0.409218                      716                          -0.273928                    -6.033278                                      -3.139373                                   -3.609319                             0.412011           1.0    279.181661 skel_156d0fafafecde17      0.992788       0.998424
a7ff7e_66fc9f6699584033                              SafeDiv(Clip(ZScore(mark_index_basis_bps),-3,3),Abs(Abs(ZScore(realized_vol_168h))))    basis_premium_like|volatility_like       safe_div_abs            L5_vol_adjusted_return                4                    -1.0                            3                 True                  0.573227                     0.085539    True                   1.405437                1.999702       True               0.209207               0.208607                0.207607         95.466667               A7FF12S05_NUMERIC_CLUE           716               -0.000216         -0.012746                            0.025978                        -0.996203                  0.502793                  716                      -0.045001                -2.295061                                  -1.405437                               -1.999702                         0.430168            716                -0.135576          -4.389153                            -2.264323                         -4.005079                   0.389665                      716                          -0.209607                    -4.837209                                      -2.507846                                   -2.831217                             0.452514           1.0    215.033544 skel_79b46e3bec19bc64      0.827348       1.000000
a7ff7e_77ca3b839d710afd Sub(CSRank(Clip(ZScore(mark_index_basis_bps),-3,3)),CSRank(Clip(ZScore(top_long_short_account_ratio_last),-3,3)))   basis_premium_like|positioning_like        spread_rank            L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.313789                     0.047626    True                   4.851260                4.851260       True               0.139320               0.138720                0.137720         95.866667               A7FF12S05_NUMERIC_CLUE           719               -0.007650         -0.729779                           -0.729779                        -0.729779                  0.499305                  719                      -0.053729                -4.851260                                  -4.851260                               -4.851260                         0.393602            719                -0.097653          -7.489557                            -7.489557                         -7.489557                   0.360223                      719                          -0.139720                    -6.480026                                      -6.480026                                   -6.480026                             0.408901           1.0    145.406533 skel_3d2988e4547fbd95      0.999713       0.987281
a7ff7e_e0cb06581d22fb61                                     Sub(mark_index_basis_bps,Clip(ZScore(taker_buy_sell_volume_ratio_last),-3,3))   basis_premium_like|positioning_like                sub            L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.642732                     0.032863    True                   6.025311                6.025311       True               0.127933               0.127333                0.126333         95.866667               A7FF12S05_NUMERIC_CLUE           719               -0.011330         -1.066932                           -1.066932                        -1.066932                  0.479833                  719                      -0.086212                -8.804028                                  -8.804028                               -8.804028                         0.342142            719                -0.132774          -9.090372                            -9.090372                         -9.090372                   0.342142                      719                          -0.128333                    -6.025311                                      -6.025311                                   -6.025311                             0.403338           1.0    133.690447 skel_593666ed3f85046b      0.999713       1.000000
a7ff7e_5201f3314c5dae1a                                            SafeDiv(mark_index_basis_bps,Abs(Clip(ZScore(realized_vol_24h),-3,3)))    basis_premium_like|volatility_like       safe_div_abs            L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.355105                     0.031363    True                   6.804910                6.804910       True               0.123839               0.123239                0.122239         95.866667               A7FF12S05_NUMERIC_CLUE           719               -0.004231         -0.426981                           -0.426981                        -0.426981                  0.467316                  719                      -0.081079                -8.573577                                  -8.573577                               -8.573577                         0.331015            719                -0.100386          -7.746042                            -7.746042                         -7.746042                   0.360223                      719                          -0.124239                    -6.804910                                      -6.804910                                   -6.804910                             0.376912           1.0    129.884117 skel_1c4b9d5957f9af9c      0.827348       0.987109
a7ff7e_329eb175f2d1969f                                                          Mul(Abs(ZScore(mark_index_basis_bps)),premium_close_bps) basis_premium_like|basis_premium_like                mul            L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.983450                     0.036799    True                   3.117177                3.117177       True               0.096619               0.096019                0.095019         95.866667               A7FF12S05_NUMERIC_CLUE           715               -0.027633         -2.212105                           -2.212105                        -2.212105                  0.464336                  668                      -0.066064                -3.867171                                  -3.867171                               -3.867171                         0.410180            713                -0.062798          -3.117177                            -3.117177                         -3.117177                   0.417952                      719                          -0.097019                    -3.504731                                      -3.504731                                   -3.504731                             0.439499           1.0    102.035118 skel_7be1b7a1db5c1738      0.999713       0.664509
a7ff7e_d6cdc6fa12328929                                     Sub(Clip(ZScore(mark_index_basis_bps),-3,3),taker_buy_sell_volume_ratio_last)   basis_premium_like|positioning_like                sub            L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.443536                     0.020964    True                   4.151821                4.151821       True               0.079334               0.078734                0.077734         95.866667               A7FF12S05_NUMERIC_CLUE           719               -0.008222         -0.823361                           -0.823361                        -0.823361                  0.484006                  719                      -0.055052                -5.669687                                  -5.669687                               -5.669687                         0.393602            719                -0.078192          -6.005020                            -6.005020                         -6.005020                   0.386648                      719                          -0.079734                    -4.151821                                      -4.151821                                   -4.151821                             0.420028           1.0     85.290823 skel_2ea572aa7aa431a9      0.999713       1.000000
a7ff7e_e1ed56d08d58ea65                                          Mean(Mul(Abs(ZScore(mark_index_basis_bps)),CSRank(premium_close_bps)),4) basis_premium_like|basis_premium_like smooth_interaction            L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.657830                     0.024614    True                   1.307831                1.307831       True               0.052133               0.051533                0.050533         95.866667               A7FF12S05_NUMERIC_CLUE           716               -0.005633         -0.600504                           -0.600504                        -0.600504                  0.502793                  719                      -0.018196                -1.307831                                  -1.307831                               -1.307831                         0.460362            719                -0.021806          -1.586690                            -1.586690                         -1.586690                   0.475661                      719                          -0.052533                    -2.625998                                      -2.625998                                   -2.625998                             0.418637           1.0     57.874842 skel_ec07cc6961c03640      0.998851       1.000000
a7ff7e_ea526c0f52d74776                               Sub(CSRank(Abs(ZScore(mark_index_basis_bps))),CSRank(CSRank(mark_trade_basis_bps))) basis_premium_like|basis_premium_like        spread_rank           L7_ranked_future_return                4                    -1.0                            3                 True                  0.277927                     0.011893    True                   3.521694                4.931660       True               0.044350               0.043750                0.042750         95.466667 A7FF12S05_RANK_LABEL_DIAGNOSTIC_CLUE           716               -0.012919         -2.422440                           -1.364219                        -2.090699                  0.462291                  716                      -0.037836                -7.473166                                  -3.521694                               -5.565278                         0.396648            716                -0.056112         -11.155889                            -5.554062                         -6.234217                   0.344972                      716                          -0.044750                    -8.236315                                      -3.964894                                   -4.931660                             0.382682           0.0     49.472198 skel_e0a634aafe6954a4      0.999713       0.991077
a7ff7e_0741d6d61ad0a226                                    Mean(Mul(ZScore(mark_index_basis_bps),Clip(ZScore(premium_close_bps),-3,3)),4) basis_premium_like|basis_premium_like smooth_interaction           L7_ranked_future_return                1                    -1.0                            3                 True                  0.898431                     0.005571    True                   1.959583                1.959583       True               0.016391               0.015791                0.014791         95.866667 A7FF12S05_RANK_LABEL_DIAGNOSTIC_CLUE           716               -0.003248         -0.594768                           -0.594768                        -0.594768                  0.476257                  719                      -0.010004                -1.959583                                  -1.959583                               -1.959583                         0.460362            719                -0.022805          -4.138204                            -4.138204                         -4.138204                   0.425591                      719                          -0.016791                    -3.022689                                      -3.022689                                   -3.022689                             0.465925           0.0     20.892830 skel_3556a63fd42ae167      0.998851       1.000000
a7ff7e_26fc134c0a00583a         Mean(Mul(Clip(ZScore(mark_index_basis_bps),-3,3),Clip(ZScore(top_long_short_account_ratio_last),-3,3)),4)   basis_premium_like|positioning_like smooth_interaction           L7_ranked_future_return                4                    -1.0                            3                 True                  0.785132                     0.015615    True                   1.229276                1.521113       True               0.014006               0.013406                0.012406         95.466667 A7FF12S05_RANK_LABEL_DIAGNOSTIC_CLUE           713               -0.009527         -1.800920                           -0.769743                        -1.536374                  0.464236                  716                      -0.015216                -2.868839                                  -1.345710                               -2.243208                         0.449721            716                -0.016574          -3.079398                            -1.548162                         -1.910507                   0.435754                      716                          -0.014406                    -2.529672                                      -1.229276                                   -1.521113                             0.449721           0.0     18.620630 skel_46576aa3f9f39de0      0.998851       1.000000
a7ff7e_89299c07c96214bf                                   Sub(CSRank(Abs(ZScore(mark_index_basis_bps))),CSRank(Delta(trade_return_1h,1)))         basis_premium_like|price_like        spread_rank           L7_ranked_future_return                1                     1.0                            3                 True                  0.810981                     0.008434    True                   2.152246                2.152246       True               0.011884               0.011284                0.010284         95.866667 A7FF12S05_RANK_LABEL_DIAGNOSTIC_CLUE           718                0.014336          2.232866                            2.232866                         2.232866                  0.544568                  719                       0.019115                 3.063312                                   3.063312                                3.063312                         0.543811            719                 0.028322           4.906529                             4.906529                          4.906529                   0.557719                      719                           0.012284                     2.152246                                       2.152246                                    2.152246                             0.538248           0.0     16.472563 skel_ad33410941dac81e      0.998851       0.988097
a7ff7e_4346ffb98ebf72fd         Mul(Delta(Clip(ZScore(mark_index_basis_bps),-3,3),4),ZScore(Clip(ZScore(open_interest_value_last),-3,3)))   basis_premium_like|positioning_like     relative_shock L3_liquidity_tier_relative_return                1                     1.0                            3                 True                  0.230605                     0.000386    True                   3.262374                3.262374       True               0.000500              -0.000100               -0.001100         95.866667               A7FF12S05_NUMERIC_CLUE           715                0.000151          1.032206                            1.032206                         1.032206                  0.509091                  719                       0.000554                 5.723471                                   5.723471                                5.723471                         0.650904            719                 0.000995           7.752874                             7.752874                          7.752874                   0.678720                      719                           0.000900                     3.262374                                       3.262374                                    3.262374                             0.552156           1.0      6.769395 skel_aa3d13111ce1711c      0.998564       0.998861
```

## Boundary

```text
No May/post-selection stress is used in scoring or authorization.
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
L7 ranked-return rows remain diagnostic-only and cannot promote without non-L7 support.
```
