# CRYPTO A7FF-12S03 EXPANDED NUMERIC PROBE

Generated: 2026-05-30T03:50:07Z

## Decision

`PASS_A7FF12S03_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH`

A7FF-12S03 materializes the A7FF-7E selected blueprint queue and evaluates label response, controls, non-overlap statistics, and a dry portfolio marginal proxy. It is not formula search or alpha proof.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FF12S03_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH",
  "executes_generation": false,
  "executes_numeric_probe": true,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T03:50:07Z",
  "input_blueprint_count": 90,
  "label_response_rows": 1800,
  "materialized_activity_ok_count": 90,
  "non_l7_numeric_clue_rows": 59,
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
  "portfolio_queue_count": 16,
  "queue_limit": 90,
  "queue_offset": 270,
  "queue_path": "D:\\HermesWorker\\GDrive\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519_remote\\runtime\\a7ff12_numeric_wave_queue_contract\\a7ff12_numeric_wave_queue.csv",
  "queue_total_rows": 720,
  "rank_label_diagnostic_clue_rows": 15,
  "selected_portfolio_queue_count": 10,
  "stage": "A7FF-12S03",
  "uses_may": false
}
```

## Decision Counts

```text
                            decision                       label_family  count
              A7FF12S03_NUMERIC_CLUE              L0_raw_forward_return     12
              A7FF12S03_NUMERIC_CLUE L1_cross_sectional_relative_return     12
              A7FF12S03_NUMERIC_CLUE  L3_liquidity_tier_relative_return     14
              A7FF12S03_NUMERIC_CLUE             L5_vol_adjusted_return     21
A7FF12S03_RANK_LABEL_DIAGNOSTIC_CLUE            L7_ranked_future_return     15
    HOLD_A7FF12S03_CONTROL_DOMINATED              L0_raw_forward_return     94
    HOLD_A7FF12S03_CONTROL_DOMINATED L1_cross_sectional_relative_return     92
    HOLD_A7FF12S03_CONTROL_DOMINATED  L3_liquidity_tier_relative_return     81
    HOLD_A7FF12S03_CONTROL_DOMINATED             L5_vol_adjusted_return     90
    HOLD_A7FF12S03_CONTROL_DOMINATED            L7_ranked_future_return    103
  HOLD_A7FF12S03_COST2_PROXY_FRAGILE              L0_raw_forward_return      1
  HOLD_A7FF12S03_COST2_PROXY_FRAGILE L1_cross_sectional_relative_return      2
  HOLD_A7FF12S03_COST2_PROXY_FRAGILE  L3_liquidity_tier_relative_return      1
  HOLD_A7FF12S03_ONE_BAR_LAG_FRAGILE              L0_raw_forward_return     17
  HOLD_A7FF12S03_ONE_BAR_LAG_FRAGILE L1_cross_sectional_relative_return     18
  HOLD_A7FF12S03_ONE_BAR_LAG_FRAGILE  L3_liquidity_tier_relative_return     21
  HOLD_A7FF12S03_ONE_BAR_LAG_FRAGILE             L5_vol_adjusted_return     30
  HOLD_A7FF12S03_ONE_BAR_LAG_FRAGILE            L7_ranked_future_return     43
     HOLD_A7FF12S03_PRE_MAY_UNSTABLE              L0_raw_forward_return    236
     HOLD_A7FF12S03_PRE_MAY_UNSTABLE L1_cross_sectional_relative_return    236
     HOLD_A7FF12S03_PRE_MAY_UNSTABLE  L3_liquidity_tier_relative_return    243
     HOLD_A7FF12S03_PRE_MAY_UNSTABLE             L5_vol_adjusted_return    219
     HOLD_A7FF12S03_PRE_MAY_UNSTABLE            L7_ranked_future_return    199
```

## Family Summary

```text
                        semantic_pair                             decision  count
basis_premium_like|basis_premium_like               A7FF12S03_NUMERIC_CLUE      7
basis_premium_like|basis_premium_like A7FF12S03_RANK_LABEL_DIAGNOSTIC_CLUE      1
basis_premium_like|basis_premium_like     HOLD_A7FF12S03_CONTROL_DOMINATED    113
basis_premium_like|basis_premium_like   HOLD_A7FF12S03_COST2_PROXY_FRAGILE      1
basis_premium_like|basis_premium_like   HOLD_A7FF12S03_ONE_BAR_LAG_FRAGILE     66
basis_premium_like|basis_premium_like      HOLD_A7FF12S03_PRE_MAY_UNSTABLE    232
  basis_premium_like|positioning_like               A7FF12S03_NUMERIC_CLUE     21
  basis_premium_like|positioning_like A7FF12S03_RANK_LABEL_DIAGNOSTIC_CLUE      9
  basis_premium_like|positioning_like     HOLD_A7FF12S03_CONTROL_DOMINATED    113
  basis_premium_like|positioning_like   HOLD_A7FF12S03_COST2_PROXY_FRAGILE      3
  basis_premium_like|positioning_like   HOLD_A7FF12S03_ONE_BAR_LAG_FRAGILE     30
  basis_premium_like|positioning_like      HOLD_A7FF12S03_PRE_MAY_UNSTABLE    344
        basis_premium_like|price_like               A7FF12S03_NUMERIC_CLUE      1
        basis_premium_like|price_like     HOLD_A7FF12S03_CONTROL_DOMINATED    101
        basis_premium_like|price_like   HOLD_A7FF12S03_ONE_BAR_LAG_FRAGILE     20
        basis_premium_like|price_like      HOLD_A7FF12S03_PRE_MAY_UNSTABLE    238
   basis_premium_like|volatility_like               A7FF12S03_NUMERIC_CLUE     30
   basis_premium_like|volatility_like A7FF12S03_RANK_LABEL_DIAGNOSTIC_CLUE      5
   basis_premium_like|volatility_like     HOLD_A7FF12S03_CONTROL_DOMINATED    133
   basis_premium_like|volatility_like   HOLD_A7FF12S03_ONE_BAR_LAG_FRAGILE     13
   basis_premium_like|volatility_like      HOLD_A7FF12S03_PRE_MAY_UNSTABLE    319
```

## Control Summary

```text
             control  median_ratio   max_ratio  rows
         one_bar_lag      0.732294 2035.466369  5400
 same_family_placebo      0.351333 1036.828968  5400
           sign_flip      1.006420 1289.881830  5400
      symbol_shuffle      0.432400 1871.236814  5400
        time_shuffle      0.448917  888.232977  5400
wrong_lag_future_24h      1.323019 3816.606060  5400
wrong_lag_stale_168h      0.542873 1950.317880  5400
```

## Selected Portfolio Queue

```text
           blueprint_id                                                                                              expression                         semantic_pair              motif                       label_family  label_horizon_h  orientation_from_train  premay_positive_split_count  premay_all_positive  control_ratio_premay_max  one_bar_lag_recent_oriented  lag_ok  robust_median_tstat_floor  robust_min_tstat_floor  robust_ok  cost2_recent_oriented  cost5_recent_oriented  cost10_recent_oriented  avg_n_obs_recent                             decision  train_2024_n  train_2024_mean_spread  train_2024_tstat  train_2024_nonoverlap_median_tstat  train_2024_nonoverlap_min_tstat  train_2024_positive_rate  validation_2025H1_n  validation_2025H1_mean_spread  validation_2025H1_tstat  validation_2025H1_nonoverlap_median_tstat  validation_2025H1_nonoverlap_min_tstat  validation_2025H1_positive_rate  test_2025H2_n  test_2025H2_mean_spread  test_2025H2_tstat  test_2025H2_nonoverlap_median_tstat  test_2025H2_nonoverlap_min_tstat  test_2025H2_positive_rate  recent_oos_2026JanApr_n  recent_oos_2026JanApr_mean_spread  recent_oos_2026JanApr_tstat  recent_oos_2026JanApr_nonoverlap_median_tstat  recent_oos_2026JanApr_nonoverlap_min_tstat  recent_oos_2026JanApr_positive_rate  non_l7_bonus  score_no_may          skeleton_key  finite_share  nonzero_share
a7ff7e_5610169eff30fab5                                Mul(Delta(mark_index_basis_bps,12),Sign(Abs(ZScore(realized_vol_168h))))    basis_premium_like|volatility_like         gated_sign             L5_vol_adjusted_return                8                    -1.0                            3                 True                  0.843416                     0.247474    True                   0.626901                2.325739       True               0.389848               0.389248                0.388248         94.933333               A7FF12S03_NUMERIC_CLUE           700               -0.015016         -0.519622                           -0.175288                        -1.634500                  0.480000                  712                      -0.055726                -2.018783                                  -0.626901                               -2.526720                         0.441011            712                -0.137832          -3.261929                            -1.329647                         -2.325739                   0.450843                      712                          -0.390248                    -5.507264                                      -2.333339                                   -3.278556                             0.411517           1.0    395.404406 skel_3d008dc9486239b2      0.823901       0.998297
a7ff7e_ae49260ddd504924                                                    Mul(Delta(mark_index_basis_bps,12),realized_vol_24h)    basis_premium_like|volatility_like                mul             L5_vol_adjusted_return                8                    -1.0                            3                 True                  0.824680                     0.209536    True                   0.320641                2.048357       True               0.347793               0.347193                0.346193         94.933333               A7FF12S03_NUMERIC_CLUE           700               -0.006470         -0.214954                           -0.074921                        -1.512027                  0.482857                  712                      -0.042293                -1.496830                                  -0.320641                               -2.048357                         0.464888            712                -0.102009          -2.390572                            -0.909347                         -2.314570                   0.464888                      712                          -0.348193                    -4.856691                                      -1.878343                                   -3.133763                             0.428371           1.0    353.368211 skel_0994b3a36a4d53ba      0.823901       0.998297
a7ff7e_77104f0e768df207             Sub(CSRank(Delta(mark_index_basis_bps,12)),CSRank(Clip(ZScore(mark_trade_basis_bps),-3,3))) basis_premium_like|basis_premium_like        spread_rank             L5_vol_adjusted_return                8                    -1.0                            3                 True                  0.659917                     0.132145    True                   0.475748                2.158152       True               0.340987               0.340387                0.339387         94.933333               A7FF12S03_NUMERIC_CLUE           700               -0.000932         -0.032870                           -0.118851                        -0.891975                  0.495714                  712                      -0.066930                -2.336239                                  -0.475748                               -2.158152                         0.418539            712                -0.215373          -5.396408                            -2.016033                         -3.345147                   0.397472                      712                          -0.341387                    -5.532203                                      -2.181330                                   -3.267341                             0.410112           1.0    346.726768 skel_00fa107e5b1b71eb      0.996265       0.990944
a7ff7e_f8a8d6cf8b654e64           SafeDiv(Delta(mark_index_basis_bps,12),Abs(Sign(Delta(taker_buy_sell_volume_ratio_last,24))))   basis_premium_like|positioning_like       safe_div_abs             L5_vol_adjusted_return                4                    -1.0                            3                 True                  0.746835                     0.139179    True                   0.852616                2.303467       True               0.273511               0.272911                0.271911         95.466667               A7FF12S03_NUMERIC_CLUE           692               -0.008704         -0.417590                           -0.185058                        -0.998054                  0.485549                  716                      -0.049945                -2.699969                                  -0.852616                               -3.055159                         0.460894            716                -0.096646          -3.171834                            -1.543866                         -2.303467                   0.409218                      716                          -0.273911                    -6.032953                                      -3.139373                                   -3.609319                             0.412011           1.0    279.164572 skel_156d0fafafecde17      0.992818       0.998424
a7ff7e_ca3c03329ffd2edb                                                      Mul(CSRank(mark_index_basis_bps),realized_vol_24h)    basis_premium_like|volatility_like                mul             L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.894735                     0.041170    True                   5.504428                5.504428       True               0.127007               0.126407                0.125407         95.866667               A7FF12S03_NUMERIC_CLUE           719               -0.025653         -2.201339                           -2.201339                        -2.201339                  0.463143                  719                      -0.076344                -7.139759                                  -7.139759                               -7.139759                         0.344924            719                -0.112694          -8.160433                            -8.160433                         -8.160433                   0.351878                      719                          -0.127407                    -5.504428                                      -5.504428                                   -5.504428                             0.440890           1.0    132.512654 skel_37ba6246678096b3      0.827348       1.000000
a7ff7e_c0ec1785df986116                                      Mul(Abs(ZScore(mark_index_basis_bps)),Delta(premium_close_bps,12)) basis_premium_like|basis_premium_like                mul             L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.356331                     0.043854    True                   3.610145                3.610145       True               0.093948               0.093348                0.092348         95.866667               A7FF12S03_NUMERIC_CLUE           707               -0.013096         -1.178605                           -1.178605                        -1.178605                  0.473833                  719                      -0.038034                -3.610145                                  -3.610145                               -3.610145                         0.426982            719                -0.064606          -4.679916                            -4.679916                         -4.679916                   0.401947                      719                          -0.094348                    -4.394518                                      -4.394518                                   -4.394518                             0.433936           1.0     99.991253 skel_7c564c472f890218      0.996265       0.826542
a7ff7e_5426d008450afbae                                               Mul(mark_index_basis_bps,Sign(Delta(trade_return_24h,1)))         basis_premium_like|price_like         gated_sign             L5_vol_adjusted_return                4                     1.0                            3                 True                  0.861261                     0.076243    True                   0.820937               -0.619410       True               0.077777               0.077177                0.076177         95.466667               A7FF12S03_NUMERIC_CLUE           715                0.011964          0.581043                            0.413190                        -0.321024                  0.514685                  716                       0.049927                 2.377012                                   1.024596                                0.747480                         0.541899            716                 0.039947           1.388662                             0.820937                         -0.619410                   0.532123                      716                           0.078177                     1.928210                                       0.957257                                    0.351641                             0.551676           1.0     83.316188 skel_a2f58ee62d9e7ad2      0.827061       0.981772
a7ff7e_aaa881efcbbebaf4                          Sub(Abs(ZScore(mark_index_basis_bps)),Clip(ZScore(mark_trade_basis_bps),-3,3)) basis_premium_like|basis_premium_like                sub            L7_ranked_future_return                8                    -1.0                            3                 True                  0.322801                     0.012596    True                   2.842406                3.989350       True               0.048858               0.048258                0.047258         94.933333 A7FF12S03_RANK_LABEL_DIAGNOSTIC_CLUE           712               -0.008112         -1.454282                           -0.421429                        -1.897992                  0.460674                  712                      -0.040713                -7.987836                                  -2.842406                               -3.989350                         0.384831            712                -0.065008         -12.034659                            -4.334938                         -5.469672                   0.321629                      712                          -0.049258                    -9.000025                                      -3.115441                                   -4.236640                             0.362360           0.0     53.934719 skel_26519c5fcf83ddd8      0.999713       1.000000
a7ff7e_1bf75643c8d5b7f5 Mul(Clip(ZScore(mark_index_basis_bps),-3,3),Sign(Clip(ZScore(top_long_short_account_ratio_last),-3,3)))   basis_premium_like|positioning_like         gated_sign            L7_ranked_future_return                4                    -1.0                            3                 True                  0.513585                     0.013174    True                   1.373191                3.134775       True               0.024451               0.023851                0.022851         95.466667 A7FF12S03_RANK_LABEL_DIAGNOSTIC_CLUE           716               -0.006657         -1.360496                           -0.650623                        -1.817603                  0.481844                  716                      -0.026820                -5.232289                                  -2.610761                               -3.350737                         0.414804            716                -0.017499          -3.456492                            -1.373191                         -3.134775                   0.448324                      716                          -0.024851                    -4.269511                                      -2.134754                                   -3.266617                             0.423184           0.0     29.337389 skel_f5a350b26e95f33f      0.999713       1.000000
a7ff7e_70cf3a2ac620cf9e                          Mean(Mul(Clip(ZScore(mark_index_basis_bps),-3,3),CSRank(premium_close_bps)),4) basis_premium_like|basis_premium_like smooth_interaction L1_cross_sectional_relative_return                1                    -1.0                            3                 True                  0.729431                     0.000148    True                   1.685657                1.685657       True               0.000146              -0.000454               -0.001454         95.866667               A7FF12S03_NUMERIC_CLUE           716               -0.000122         -0.730434                           -0.730434                        -0.730434                  0.498603                  719                      -0.000197                -1.685657                                  -1.685657                               -1.685657                         0.431154            719                -0.000404          -3.259487                            -3.259487                         -3.259487                   0.454798                      719                          -0.000546                    -2.189662                                      -2.189662                                   -2.189662                             0.453408           1.0      6.270569 skel_5b0c70d11e8773f7      0.998851       1.000000
```

## Boundary

```text
No May/post-selection stress is used in scoring or authorization.
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
L7 ranked-return rows remain diagnostic-only and cannot promote without non-L7 support.
```
