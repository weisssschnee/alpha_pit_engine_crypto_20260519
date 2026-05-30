# CRYPTO A7FF-19S00 EXPANDED NUMERIC PROBE

Generated: 2026-05-30T05:06:09Z

## Decision

`PASS_A7FF19S00_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH`

A7FF-19S00 materializes the A7FF-7E selected blueprint queue and evaluates label response, controls, non-overlap statistics, and a dry portfolio marginal proxy. It is not formula search or alpha proof.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FF19S00_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH",
  "executes_generation": false,
  "executes_numeric_probe": true,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T05:06:09Z",
  "input_blueprint_count": 28,
  "label_response_rows": 560,
  "materialized_activity_ok_count": 28,
  "non_l7_numeric_clue_rows": 130,
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
  "queue_offset": 0,
  "queue_path": "D:\\HermesWorker\\GDrive\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519_remote\\runtime\\a7ff19_external_selector_confirmation_contract\\a7ff19_execution_queue.csv",
  "queue_total_rows": 56,
  "rank_label_diagnostic_clue_rows": 28,
  "selected_portfolio_queue_count": 20,
  "stage": "A7FF-19S00",
  "uses_may": false
}
```

## Decision Counts

```text
                            decision                       label_family  count
              A7FF19S00_NUMERIC_CLUE              L0_raw_forward_return     23
              A7FF19S00_NUMERIC_CLUE L1_cross_sectional_relative_return     26
              A7FF19S00_NUMERIC_CLUE  L3_liquidity_tier_relative_return     29
              A7FF19S00_NUMERIC_CLUE             L5_vol_adjusted_return     52
A7FF19S00_RANK_LABEL_DIAGNOSTIC_CLUE            L7_ranked_future_return     28
    HOLD_A7FF19S00_CONTROL_DOMINATED              L0_raw_forward_return     31
    HOLD_A7FF19S00_CONTROL_DOMINATED L1_cross_sectional_relative_return     28
    HOLD_A7FF19S00_CONTROL_DOMINATED  L3_liquidity_tier_relative_return     26
    HOLD_A7FF19S00_CONTROL_DOMINATED             L5_vol_adjusted_return     18
    HOLD_A7FF19S00_CONTROL_DOMINATED            L7_ranked_future_return      7
  HOLD_A7FF19S00_COST2_PROXY_FRAGILE              L0_raw_forward_return      1
  HOLD_A7FF19S00_COST2_PROXY_FRAGILE L1_cross_sectional_relative_return      1
  HOLD_A7FF19S00_COST2_PROXY_FRAGILE  L3_liquidity_tier_relative_return      1
  HOLD_A7FF19S00_ONE_BAR_LAG_FRAGILE              L0_raw_forward_return      9
  HOLD_A7FF19S00_ONE_BAR_LAG_FRAGILE L1_cross_sectional_relative_return      9
  HOLD_A7FF19S00_ONE_BAR_LAG_FRAGILE  L3_liquidity_tier_relative_return     11
  HOLD_A7FF19S00_ONE_BAR_LAG_FRAGILE             L5_vol_adjusted_return      7
  HOLD_A7FF19S00_ONE_BAR_LAG_FRAGILE            L7_ranked_future_return     35
     HOLD_A7FF19S00_PRE_MAY_UNSTABLE              L0_raw_forward_return     48
     HOLD_A7FF19S00_PRE_MAY_UNSTABLE L1_cross_sectional_relative_return     48
     HOLD_A7FF19S00_PRE_MAY_UNSTABLE  L3_liquidity_tier_relative_return     45
     HOLD_A7FF19S00_PRE_MAY_UNSTABLE             L5_vol_adjusted_return     35
     HOLD_A7FF19S00_PRE_MAY_UNSTABLE            L7_ranked_future_return     42
```

## Family Summary

```text
                        semantic_pair                             decision  count
basis_premium_like|basis_premium_like               A7FF19S00_NUMERIC_CLUE     61
basis_premium_like|basis_premium_like A7FF19S00_RANK_LABEL_DIAGNOSTIC_CLUE     13
basis_premium_like|basis_premium_like     HOLD_A7FF19S00_CONTROL_DOMINATED     66
basis_premium_like|basis_premium_like   HOLD_A7FF19S00_ONE_BAR_LAG_FRAGILE     55
basis_premium_like|basis_premium_like      HOLD_A7FF19S00_PRE_MAY_UNSTABLE    105
  basis_premium_like|positioning_like               A7FF19S00_NUMERIC_CLUE     37
  basis_premium_like|positioning_like A7FF19S00_RANK_LABEL_DIAGNOSTIC_CLUE      9
  basis_premium_like|positioning_like     HOLD_A7FF19S00_CONTROL_DOMINATED     31
  basis_premium_like|positioning_like   HOLD_A7FF19S00_ONE_BAR_LAG_FRAGILE      7
  basis_premium_like|positioning_like      HOLD_A7FF19S00_PRE_MAY_UNSTABLE     76
   basis_premium_like|volatility_like               A7FF19S00_NUMERIC_CLUE     32
   basis_premium_like|volatility_like A7FF19S00_RANK_LABEL_DIAGNOSTIC_CLUE      6
   basis_premium_like|volatility_like     HOLD_A7FF19S00_CONTROL_DOMINATED     13
   basis_premium_like|volatility_like   HOLD_A7FF19S00_COST2_PROXY_FRAGILE      3
   basis_premium_like|volatility_like   HOLD_A7FF19S00_ONE_BAR_LAG_FRAGILE      9
   basis_premium_like|volatility_like      HOLD_A7FF19S00_PRE_MAY_UNSTABLE     37
```

## Control Summary

```text
             control  median_ratio  max_ratio  rows
         one_bar_lag      0.418720 106.999866  1680
 same_family_placebo      0.174997 103.651076  1680
           sign_flip      0.989430  12.655369  1680
      symbol_shuffle      0.193600  69.834976  1680
        time_shuffle      0.201583  59.743922  1680
wrong_lag_future_24h      0.364180 150.566026  1680
wrong_lag_stale_168h      0.250581  99.303063  1680
```

## Selected Portfolio Queue

```text
           blueprint_id                                                                                            expression                         semantic_pair              motif           label_family  label_horizon_h  orientation_from_train  premay_positive_split_count  premay_all_positive  control_ratio_premay_max  one_bar_lag_recent_oriented  lag_ok  robust_median_tstat_floor  robust_min_tstat_floor  robust_ok  cost2_recent_oriented  cost5_recent_oriented  cost10_recent_oriented  avg_n_obs_recent               decision  train_2024_n  train_2024_mean_spread  train_2024_tstat  train_2024_nonoverlap_median_tstat  train_2024_nonoverlap_min_tstat  train_2024_positive_rate  validation_2025H1_n  validation_2025H1_mean_spread  validation_2025H1_tstat  validation_2025H1_nonoverlap_median_tstat  validation_2025H1_nonoverlap_min_tstat  validation_2025H1_positive_rate  test_2025H2_n  test_2025H2_mean_spread  test_2025H2_tstat  test_2025H2_nonoverlap_median_tstat  test_2025H2_nonoverlap_min_tstat  test_2025H2_positive_rate  recent_oos_2026JanApr_n  recent_oos_2026JanApr_mean_spread  recent_oos_2026JanApr_tstat  recent_oos_2026JanApr_nonoverlap_median_tstat  recent_oos_2026JanApr_nonoverlap_min_tstat  recent_oos_2026JanApr_positive_rate  non_l7_bonus  score_no_may          skeleton_key  finite_share  nonzero_share
a7ff7e_31a152b5a6d123af     SafeDiv(Delta(mark_index_basis_bps,12),Abs(Sign(Delta(global_long_short_account_ratio_last,24))))   basis_premium_like|positioning_like       safe_div_abs L5_vol_adjusted_return                8                    -1.0                            3                 True                  0.692402                     0.247699    True                   0.626901                2.325739       True               0.390019               0.389419                0.388419         94.929167 A7FF19S00_NUMERIC_CLUE           688               -0.010205         -0.352775                           -0.086228                        -1.421863                  0.482558                  712                      -0.055726                -2.018783                                  -0.626901                               -2.526720                         0.441011            712                -0.137832          -3.261929                            -1.329647                         -2.325739                   0.450843                      712                          -0.390419                    -5.509103                                      -2.335963                                   -3.278556                             0.411517           1.0    395.726273 skel_156d0fafafecde17      0.992788       0.998424
a7ff7e_b0946aa9e40dd3c9                              Mul(Delta(mark_index_basis_bps,12),Sign(Abs(ZScore(premium_close_bps)))) basis_premium_like|basis_premium_like         gated_sign L5_vol_adjusted_return                8                    -1.0                            3                 True                  0.619643                     0.247474    True                   0.626901                2.325739       True               0.389848               0.389248                0.388248         94.933333 A7FF19S00_NUMERIC_CLUE           700               -0.015016         -0.519622                           -0.175288                        -1.634500                  0.480000                  712                      -0.055726                -2.018783                                  -0.626901                               -2.526720                         0.441011            712                -0.137832          -3.261929                            -1.329647                         -2.325739                   0.450843                      712                          -0.390248                    -5.507264                                      -2.333339                                   -3.278556                             0.411517           1.0    395.628179 skel_3d008dc9486239b2      0.996265       0.998429
a7ff7e_2c50d60ccb24722c                                       Sub(Delta(mark_index_basis_bps,12),Delta(realized_vol_168h,24))    basis_premium_like|volatility_like                sub L5_vol_adjusted_return                8                    -1.0                            3                 True                  0.638089                     0.247068    True                   0.626901                2.325739       True               0.389268               0.388668                0.387668         94.933333 A7FF19S00_NUMERIC_CLUE           688               -0.010310         -0.356333                           -0.086228                        -1.421863                  0.482558                  712                      -0.056236                -2.036143                                  -0.626901                               -2.565855                         0.441011            712                -0.137671          -3.258004                            -1.328774                         -2.325739                   0.450843                      712                          -0.389668                    -5.498857                                      -2.330712                                   -3.278556                             0.412921           1.0    395.030246 skel_8727d93aac220fc6      0.820454       1.000000
a7ff7e_c879e0a27e94f6b7                                          Sub(Delta(mark_index_basis_bps,12),CSRank(realized_vol_24h))    basis_premium_like|volatility_like                sub L5_vol_adjusted_return                8                    -1.0                            3                 True                  0.671094                     0.244966    True                   0.543121                2.318543       True               0.387687               0.387087                0.386087         94.933333 A7FF19S00_NUMERIC_CLUE           700               -0.017126         -0.580250                           -0.201316                        -1.685120                  0.477143                  712                      -0.057869                -2.108071                                  -0.543121                               -2.563666                         0.439607            712                -0.140714          -3.324555                            -1.381689                         -2.318543                   0.450843                      712                          -0.388087                    -5.492536                                      -2.246279                                   -3.206974                             0.405899           1.0    393.415943 skel_136259b72205469f      0.823901       1.000000
a7ff7e_0f6554ac44a17024                           Sub(Delta(mark_index_basis_bps,12),Clip(ZScore(mark_trade_basis_bps),-3,3)) basis_premium_like|basis_premium_like                sub L5_vol_adjusted_return                8                    -1.0                            3                 True                  0.599667                     0.226480    True                   0.751315                2.221377       True               0.385681               0.385081                0.384081         94.933333 A7FF19S00_NUMERIC_CLUE           700               -0.018284         -0.616888                           -0.078530                        -1.509996                  0.484286                  712                      -0.060393                -2.278161                                  -0.751315                               -2.221377                         0.448034            712                -0.158897          -3.673913                            -1.290752                         -2.724723                   0.426966                      712                          -0.386081                    -5.433012                                      -2.293434                                   -3.334452                             0.396067           1.0    391.481047 skel_fb9325ceddb1ac6f      0.996265       1.000000
a7ff7e_3f3c420268049cb3                      Sub(CSRank(Delta(mark_index_basis_bps,12)),CSRank(CSRank(mark_trade_basis_bps))) basis_premium_like|basis_premium_like        spread_rank L5_vol_adjusted_return                8                    -1.0                            3                 True                  0.428738                     0.132145    True                   0.475748                2.158152       True               0.340987               0.340387                0.339387         94.933333 A7FF19S00_NUMERIC_CLUE           700               -0.000932         -0.032870                           -0.118851                        -0.891975                  0.495714                  712                      -0.066930                -2.336239                                  -0.475748                               -2.158152                         0.418539            712                -0.215373          -5.396408                            -2.016033                         -3.345147                   0.397472                      712                          -0.341387                    -5.532203                                      -2.181330                                   -3.267341                             0.410112           1.0    346.957947 skel_9505754fb4b5368b      0.996265       0.990929
a7ff7e_77104f0e768df207           Sub(CSRank(Delta(mark_index_basis_bps,12)),CSRank(Clip(ZScore(mark_trade_basis_bps),-3,3))) basis_premium_like|basis_premium_like        spread_rank L5_vol_adjusted_return                8                    -1.0                            3                 True                  0.428738                     0.132145    True                   0.475748                2.158152       True               0.340987               0.340387                0.339387         94.933333 A7FF19S00_NUMERIC_CLUE           700               -0.000932         -0.032870                           -0.118851                        -0.891975                  0.495714                  712                      -0.066930                -2.336239                                  -0.475748                               -2.158152                         0.418539            712                -0.215373          -5.396408                            -2.016033                         -3.345147                   0.397472                      712                          -0.341387                    -5.532203                                      -2.181330                                   -3.267341                             0.410112           1.0    346.957947 skel_00fa107e5b1b71eb      0.996265       0.990944
a7ff7e_b38081e93d4f200f                              Sub(CSRank(Delta(mark_index_basis_bps,12)),CSRank(mark_trade_basis_bps)) basis_premium_like|basis_premium_like        spread_rank L5_vol_adjusted_return                8                    -1.0                            3                 True                  0.790538                     0.132145    True                   0.475748                2.158152       True               0.340987               0.340387                0.339387         94.933333 A7FF19S00_NUMERIC_CLUE           700               -0.000932         -0.032870                           -0.118851                        -0.891975                  0.495714                  712                      -0.066930                -2.336239                                  -0.475748                               -2.158152                         0.418539            712                -0.215373          -5.396408                            -2.016033                         -3.345147                   0.397472                      712                          -0.341387                    -5.532203                                      -2.181330                                   -3.267341                             0.410112           1.0    346.596147 skel_51c2bb588b20fa9e      0.996265       0.990929
a7ff7e_f93323f3cf580b67                                  Mul(Delta(mark_index_basis_bps,12),taker_buy_sell_volume_ratio_last)   basis_premium_like|positioning_like                mul L5_vol_adjusted_return                8                    -1.0                            3                 True                  0.745670                     0.185748    True                   0.512304                2.502628       True               0.294959               0.294359                0.293359         94.933333 A7FF19S00_NUMERIC_CLUE           700               -0.002182         -0.078151                           -0.186917                        -0.815609                  0.470000                  712                      -0.048243                -1.758751                                  -0.512304                               -2.502628                         0.457865            712                -0.118933          -3.584934                            -1.269983                         -2.878909                   0.428371                      712                          -0.295359                    -4.525352                                      -1.803903                                   -3.028427                             0.439607           1.0    300.613066 skel_0994b3a36a4d53ba      0.996265       0.998060
a7ff7e_0ebc522cfac9064b                     SafeDiv(Delta(mark_index_basis_bps,12),Abs(Clip(ZScore(premium_close_bps),-3,3))) basis_premium_like|basis_premium_like       safe_div_abs L5_vol_adjusted_return                4                    -1.0                            3                 True                  0.997896                     0.102259    True                   1.295311                1.667949       True               0.193275               0.192675                0.191675         95.466667 A7FF19S00_NUMERIC_CLUE           704               -0.040838         -2.127787                           -1.511689                        -1.869664                  0.485795                  716                      -0.035651                -1.847020                                  -1.389664                               -2.524597                         0.449721            716                -0.054064          -2.184369                            -1.295311                         -1.667949                   0.439944                      716                          -0.193675                    -5.775073                                      -2.780379                                   -3.859204                             0.416201           1.0    198.677192 skel_6a3533b4d89c4d45      0.996265       0.998429
a7ff7e_6318fc22f34b1456                       Sub(CSRank(Delta(mark_index_basis_bps,12)),CSRank(Delta(premium_close_bps,12))) basis_premium_like|basis_premium_like        spread_rank L5_vol_adjusted_return                8                    -1.0                            3                 True                  0.741674                     0.090997    True                   0.572675                2.200832       True               0.184265               0.183665                0.182665         94.933333 A7FF19S00_NUMERIC_CLUE           700               -0.040588         -1.668882                           -0.840188                        -1.478184                  0.461429                  712                      -0.056623                -2.159453                                  -0.572675                               -3.350153                         0.476124            712                -0.156435          -4.374829                            -1.528226                         -2.200832                   0.436798                      712                          -0.184665                    -3.591511                                      -1.254889                                   -2.695353                             0.453652           1.0    189.923454 skel_bcb165b7818f5d85      0.996265       0.959129
a7ff7e_e0cb06581d22fb61                         Sub(mark_index_basis_bps,Clip(ZScore(taker_buy_sell_volume_ratio_last),-3,3))   basis_premium_like|positioning_like                sub L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.642732                     0.032863    True                   6.025311                6.025311       True               0.127933               0.127333                0.126333         95.866667 A7FF19S00_NUMERIC_CLUE           719               -0.011330         -1.066932                           -1.066932                        -1.066932                  0.479833                  719                      -0.086212                -8.804028                                  -8.804028                               -8.804028                         0.342142            719                -0.132774          -9.090372                            -9.090372                         -9.090372                   0.342142                      719                          -0.128333                    -6.025311                                      -6.025311                                   -6.025311                             0.403338           1.0    133.690447 skel_593666ed3f85046b      0.999713       1.000000
a7ff7e_2959fcddf1a8a931                                      SafeDiv(mark_index_basis_bps,Abs(Abs(ZScore(realized_vol_24h))))    basis_premium_like|volatility_like       safe_div_abs L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.354593                     0.031876    True                   6.826407                6.826407       True               0.124334               0.123734                0.122734         95.866667 A7FF19S00_NUMERIC_CLUE           719               -0.004464         -0.450112                           -0.450112                        -0.450112                  0.467316                  719                      -0.081165                -8.568455                                  -8.568455                               -8.568455                         0.331015            719                -0.103338          -8.021103                            -8.021103                         -8.021103                   0.358832                      719                          -0.124734                    -6.826407                                      -6.826407                                   -6.826407                             0.378303           1.0    130.379462 skel_6a4becaf6b891485      0.827348       0.987109
a7ff7e_5b5909ab9ba6fc5e Sub(CSRank(Delta(mark_index_basis_bps,12)),CSRank(Sign(Delta(top_long_short_account_ratio_last,24))))   basis_premium_like|positioning_like        spread_rank L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.334456                     0.029661    True                   5.745658                5.745658       True               0.101550               0.100950                0.099950         95.866667 A7FF19S00_NUMERIC_CLUE           695               -0.027903         -3.031020                           -3.031020                        -3.031020                  0.453237                  719                      -0.057077                -5.811238                                  -5.811238                               -5.811238                         0.397775            719                -0.077482          -6.234647                            -6.234647                         -6.234647                   0.378303                      719                          -0.101950                    -5.745658                                      -5.745658                                   -5.745658                             0.378303           1.0    107.615523 skel_af8c1327eb17d836      0.992818       0.994867
a7ff7e_c0ec1785df986116                                    Mul(Abs(ZScore(mark_index_basis_bps)),Delta(premium_close_bps,12)) basis_premium_like|basis_premium_like                mul L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.332143                     0.043854    True                   3.610145                3.610145       True               0.093948               0.093348                0.092348         95.866667 A7FF19S00_NUMERIC_CLUE           707               -0.013096         -1.178605                           -1.178605                        -1.178605                  0.473833                  719                      -0.038034                -3.610145                                  -3.610145                               -3.610145                         0.426982            719                -0.064606          -4.679916                            -4.679916                         -4.679916                   0.401947                      719                          -0.094348                    -4.394518                                      -4.394518                                   -4.394518                             0.433936           1.0    100.015442 skel_7c564c472f890218      0.996265       0.826542
a7ff7e_620758ad5441a864                             Mul(Clip(ZScore(mark_index_basis_bps),-3,3),CSRank(mark_trade_basis_bps)) basis_premium_like|basis_premium_like                mul L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.748871                     0.027455    True                   4.241249                4.241249       True               0.090032               0.089432                0.088432         95.866667 A7FF19S00_NUMERIC_CLUE           719               -0.016005         -1.610707                           -1.610707                        -1.610707                  0.482615                  719                      -0.070059                -7.012271                                  -7.012271                               -7.012271                         0.360223            719                -0.073390          -5.562723                            -5.562723                         -5.562723                   0.400556                      719                          -0.090432                    -4.241249                                      -4.241249                                   -4.241249                             0.438108           1.0     95.683587 skel_3363cfb4025bd87d      0.999713       1.000000
a7ff7e_a3368f0b979e0c23               SafeDiv(Delta(mark_index_basis_bps,12),Abs(Delta(taker_buy_sell_volume_ratio_last,12)))   basis_premium_like|positioning_like       safe_div_abs L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.371587                     0.041190    True                   4.147947                4.147947       True               0.084211               0.083611                0.082611         95.866667 A7FF19S00_NUMERIC_CLUE           707               -0.011862         -1.224594                           -1.224594                        -1.224594                  0.473833                  719                      -0.046191                -4.348240                                  -4.348240                               -4.348240                         0.426982            719                -0.073660          -5.668908                            -5.668908                         -5.668908                   0.390821                      719                          -0.084611                    -4.147947                                      -4.147947                                   -4.147947                             0.438108           1.0     90.239608 skel_3afee12eb6a9078f      0.996259       0.998429
a7ff7e_10e4997b8ce12a81                              Mean(Mul(Delta(mark_index_basis_bps,12),CSRank(mark_trade_basis_bps)),4) basis_premium_like|basis_premium_like smooth_interaction L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.580525                     0.046330    True                   2.240008                2.240008       True               0.082158               0.081558                0.080558         95.866667 A7FF19S00_NUMERIC_CLUE           704               -0.006686         -0.636954                           -0.636954                        -0.636954                  0.495739                  719                      -0.029241                -2.865254                                  -2.865254                               -2.865254                         0.449235            719                -0.029475          -2.240008                            -2.240008                         -2.240008                   0.440890                      719                          -0.082558                    -3.954551                                      -3.954551                                   -3.954551                             0.439499           1.0     87.976984 skel_1128a9bc5ebfee1a      0.995404       0.999985
a7ff7e_6dd372cacc5ae787                                         Sub(CSRank(mark_index_basis_bps),Delta(premium_close_bps,12)) basis_premium_like|basis_premium_like                sub L5_vol_adjusted_return                1                     1.0                            3                 True                  0.559107                     0.044630    True                   2.700944                2.700944       True               0.078540               0.077940                0.076940         95.866667 A7FF19S00_NUMERIC_CLUE           707                0.017746          1.574785                            1.574785                         1.574785                  0.553041                  719                       0.027773                 2.700944                                   2.700944                                2.700944                         0.542420            719                 0.039069           2.898787                             2.898787                          2.898787                   0.575800                      719                           0.078940                     3.883992                                       3.883992                                    3.883992                             0.564673           1.0     84.381180 skel_e47b3d7310e98dd5      0.996265       1.000000
a7ff7e_600569f7d9453450                              Sub(Clip(ZScore(mark_index_basis_bps),-3,3),Delta(premium_close_bps,12)) basis_premium_like|basis_premium_like                sub L5_vol_adjusted_return                1                     1.0                            3                 True                  0.562065                     0.042518    True                   2.381781                2.381781       True               0.074772               0.074172                0.073172         95.866667 A7FF19S00_NUMERIC_CLUE           707                0.007699          0.706371                            0.706371                         0.706371                  0.550212                  719                       0.024502                 2.381781                                   2.381781                                2.381781                         0.534075            719                 0.033989           2.564809                             2.564809                          2.564809                   0.568846                      719                           0.075172                     3.706909                                       3.706909                                    3.706909                             0.561892           1.0     80.609616 skel_b04640f9c6171dfc      0.996265       1.000000
```

## Boundary

```text
No May/post-selection stress is used in scoring or authorization.
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
L7 ranked-return rows remain diagnostic-only and cannot promote without non-L7 support.
```
