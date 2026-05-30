# CRYPTO A7FF-25R3S07 EXPANDED NUMERIC PROBE

Generated: 2026-05-30T08:35:09Z

## Decision

`PASS_A7FF25R3S07_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH`

A7FF-25R3S07 materializes the A7FF-7E selected blueprint queue and evaluates label response, controls, non-overlap statistics, and a dry portfolio marginal proxy. It is not formula search or alpha proof.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FF25R3S07_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH",
  "executes_generation": false,
  "executes_numeric_probe": true,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T08:35:09Z",
  "input_blueprint_count": 200,
  "label_response_rows": 3400,
  "materialized_activity_ok_count": 170,
  "non_l7_numeric_clue_rows": 25,
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
  "portfolio_queue_count": 54,
  "queue_limit": 200,
  "queue_offset": 0,
  "queue_path": "D:\\HermesWorker\\GDrive\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519_remote\\runtime\\a7ff24r_dry_generation_plan\\a7ff24r_company_shard_07_queue.csv",
  "queue_total_rows": 200,
  "rank_label_diagnostic_clue_rows": 104,
  "selected_portfolio_queue_count": 10,
  "stage": "A7FF-25R3S07",
  "uses_may": false
}
```

## Decision Counts

```text
                              decision                       label_family  count
              A7FF25R3S07_NUMERIC_CLUE              L0_raw_forward_return      3
              A7FF25R3S07_NUMERIC_CLUE L1_cross_sectional_relative_return      7
              A7FF25R3S07_NUMERIC_CLUE  L3_liquidity_tier_relative_return      6
              A7FF25R3S07_NUMERIC_CLUE             L5_vol_adjusted_return      9
A7FF25R3S07_RANK_LABEL_DIAGNOSTIC_CLUE            L7_ranked_future_return    104
    HOLD_A7FF25R3S07_CONTROL_DOMINATED              L0_raw_forward_return    259
    HOLD_A7FF25R3S07_CONTROL_DOMINATED L1_cross_sectional_relative_return    257
    HOLD_A7FF25R3S07_CONTROL_DOMINATED  L3_liquidity_tier_relative_return    269
    HOLD_A7FF25R3S07_CONTROL_DOMINATED             L5_vol_adjusted_return    156
    HOLD_A7FF25R3S07_CONTROL_DOMINATED            L7_ranked_future_return    346
  HOLD_A7FF25R3S07_COST2_PROXY_FRAGILE              L0_raw_forward_return      2
  HOLD_A7FF25R3S07_ONE_BAR_LAG_FRAGILE              L0_raw_forward_return      3
  HOLD_A7FF25R3S07_ONE_BAR_LAG_FRAGILE L1_cross_sectional_relative_return      3
  HOLD_A7FF25R3S07_ONE_BAR_LAG_FRAGILE  L3_liquidity_tier_relative_return      4
  HOLD_A7FF25R3S07_ONE_BAR_LAG_FRAGILE             L5_vol_adjusted_return      1
  HOLD_A7FF25R3S07_ONE_BAR_LAG_FRAGILE            L7_ranked_future_return     27
     HOLD_A7FF25R3S07_PRE_MAY_UNSTABLE              L0_raw_forward_return    413
     HOLD_A7FF25R3S07_PRE_MAY_UNSTABLE L1_cross_sectional_relative_return    413
     HOLD_A7FF25R3S07_PRE_MAY_UNSTABLE  L3_liquidity_tier_relative_return    401
     HOLD_A7FF25R3S07_PRE_MAY_UNSTABLE             L5_vol_adjusted_return    514
     HOLD_A7FF25R3S07_PRE_MAY_UNSTABLE            L7_ranked_future_return    203
```

## Family Summary

```text
                  semantic_pair                               decision  count
             basis_premium_like               A7FF25R3S07_NUMERIC_CLUE      7
             basis_premium_like A7FF25R3S07_RANK_LABEL_DIAGNOSTIC_CLUE      4
             basis_premium_like     HOLD_A7FF25R3S07_CONTROL_DOMINATED    191
             basis_premium_like   HOLD_A7FF25R3S07_COST2_PROXY_FRAGILE      1
             basis_premium_like   HOLD_A7FF25R3S07_ONE_BAR_LAG_FRAGILE      7
             basis_premium_like      HOLD_A7FF25R3S07_PRE_MAY_UNSTABLE    590
                     price_like               A7FF25R3S07_NUMERIC_CLUE     15
                     price_like A7FF25R3S07_RANK_LABEL_DIAGNOSTIC_CLUE     55
                     price_like     HOLD_A7FF25R3S07_CONTROL_DOMINATED    345
                     price_like   HOLD_A7FF25R3S07_COST2_PROXY_FRAGILE      1
                     price_like   HOLD_A7FF25R3S07_ONE_BAR_LAG_FRAGILE     17
                     price_like      HOLD_A7FF25R3S07_PRE_MAY_UNSTABLE    207
     price_like|volatility_like A7FF25R3S07_RANK_LABEL_DIAGNOSTIC_CLUE      4
     price_like|volatility_like     HOLD_A7FF25R3S07_CONTROL_DOMINATED    217
     price_like|volatility_like   HOLD_A7FF25R3S07_ONE_BAR_LAG_FRAGILE     14
     price_like|volatility_like      HOLD_A7FF25R3S07_PRE_MAY_UNSTABLE    385
                volatility_like               A7FF25R3S07_NUMERIC_CLUE      3
                volatility_like A7FF25R3S07_RANK_LABEL_DIAGNOSTIC_CLUE     30
                volatility_like     HOLD_A7FF25R3S07_CONTROL_DOMINATED    379
                volatility_like      HOLD_A7FF25R3S07_PRE_MAY_UNSTABLE    488
volatility_like|volatility_like A7FF25R3S07_RANK_LABEL_DIAGNOSTIC_CLUE     11
volatility_like|volatility_like     HOLD_A7FF25R3S07_CONTROL_DOMINATED    155
volatility_like|volatility_like      HOLD_A7FF25R3S07_PRE_MAY_UNSTABLE    274
```

## Control Summary

```text
             control  median_ratio    max_ratio  rows
         one_bar_lag      0.977407   823.778172 10200
 same_family_placebo      0.262572  1349.249258 10200
           sign_flip      1.037931   338.091481 10200
      symbol_shuffle      0.439470   745.892063 10200
        time_shuffle      0.432629  1301.258210 10200
wrong_lag_future_24h      2.772844 14175.382604 10200
wrong_lag_stale_168h      0.496121   585.407338 10200
```

## Selected Portfolio Queue

```text
            blueprint_id                                                      expression                   semantic_pair      motif            label_family  label_horizon_h  orientation_from_train  premay_positive_split_count  premay_all_positive  control_ratio_premay_max  one_bar_lag_recent_oriented  lag_ok  robust_median_tstat_floor  robust_min_tstat_floor  robust_ok  cost2_recent_oriented  cost5_recent_oriented  cost10_recent_oriented  avg_n_obs_recent                               decision  train_2024_n  train_2024_mean_spread  train_2024_tstat  train_2024_nonoverlap_median_tstat  train_2024_nonoverlap_min_tstat  train_2024_positive_rate  validation_2025H1_n  validation_2025H1_mean_spread  validation_2025H1_tstat  validation_2025H1_nonoverlap_median_tstat  validation_2025H1_nonoverlap_min_tstat  validation_2025H1_positive_rate  test_2025H2_n  test_2025H2_mean_spread  test_2025H2_tstat  test_2025H2_nonoverlap_median_tstat  test_2025H2_nonoverlap_min_tstat  test_2025H2_positive_rate  recent_oos_2026JanApr_n  recent_oos_2026JanApr_mean_spread  recent_oos_2026JanApr_tstat  recent_oos_2026JanApr_nonoverlap_median_tstat  recent_oos_2026JanApr_nonoverlap_min_tstat  recent_oos_2026JanApr_positive_rate  non_l7_bonus  score_no_may          skeleton_key  finite_share  nonzero_share
a7ff24r_ff9b56ccd0b1474f                                        Delta(trade_return_1h,1)                      price_like     single  L5_vol_adjusted_return                4                    -1.0                            3                 True                  0.441506                     0.095397    True                   0.499166                1.483382       True               0.105258               0.104658                0.103658         95.466667               A7FF25R3S07_NUMERIC_CLUE           715               -0.042215         -1.580701                           -1.266817                        -1.655667                  0.475524                  716                      -0.035941                -1.363866                                  -0.499166                               -1.483382                         0.469274            716                -0.061034          -1.861506                            -0.969674                         -1.573748                   0.437151                      716                          -0.105658                    -2.053613                                      -0.974589                                   -1.939028                             0.473464           1.0    111.216504 skel_1d39996e97d5ace0      0.998851       0.994757
a7ff24r_de6173e06fb6a118                               ZScore(Mean(realized_vol_24h,12))                 volatility_like     single L7_ranked_future_return               24                    -1.0                            3                 True                  0.873040                     0.104874    True                   1.101003                1.571073       True               0.104549               0.103949                0.102949         92.800000 A7FF25R3S07_RANK_LABEL_DIAGNOSTIC_CLUE           685               -0.085948         -8.861622                           -1.826509                        -2.788256                  0.315328                  696                      -0.062443                -5.335309                                  -1.101003                               -1.571073                         0.422414            696                -0.064432          -8.513055                            -1.762526                         -2.654847                   0.366379                      696                          -0.104949                   -12.734213                                      -2.606367                                   -3.210732                             0.324713           0.0    109.075625 skel_a311ee3fdacdeca2      0.824188       1.000000
a7ff24r_41bb8c4f64c57222                         Mul(realized_vol_168h,realized_vol_24h) volatility_like|volatility_like        mul L7_ranked_future_return               24                    -1.0                            3                 True                  0.826419                     0.100474    True                   1.388970                1.686154       True               0.101627               0.101027                0.100027         92.800000 A7FF25R3S07_RANK_LABEL_DIAGNOSTIC_CLUE           696               -0.091723         -9.510549                           -2.083906                        -2.716032                  0.317529                  696                      -0.073596                -6.558286                                  -1.388970                               -1.686154                         0.413793            696                -0.076324         -10.755189                            -2.243658                         -3.111458                   0.347701                      696                          -0.102027                   -11.842271                                      -2.475328                                   -3.145445                             0.329023           0.0    106.200707 skel_337820bc5afcf6cc      0.827348       1.000000
a7ff24r_430b607aca8d7292                 Mean(Mul(realized_vol_168h,realized_vol_24h),4) volatility_like|volatility_like smooth_mul L7_ranked_future_return               24                    -1.0                            3                 True                  0.829780                     0.100656    True                   1.324358                1.787365       True               0.101289               0.100689                0.099689         92.800000 A7FF25R3S07_RANK_LABEL_DIAGNOSTIC_CLUE           693               -0.088292         -9.231104                           -1.984072                        -2.728192                  0.311688                  696                      -0.073815                -6.585940                                  -1.324358                               -1.787365                         0.428161            696                -0.074558         -10.376912                            -2.120322                         -3.211240                   0.346264                      696                          -0.101689                   -11.886628                                      -2.371676                                   -2.976063                             0.329023           0.0    105.859437 skel_356a5f3fab58eb27      0.826487       1.000000
a7ff24r_f71d4c2645b1f21b                              Clip(ZScore(trade_return_1h),-3,3)                      price_like     single L7_ranked_future_return                1                    -1.0                            3                 True                  0.254317                     0.021627    True                   5.828584                5.828584       True               0.070411               0.069811                0.068811         95.866667 A7FF25R3S07_RANK_LABEL_DIAGNOSTIC_CLUE           719               -0.072695         -9.424358                           -9.424358                        -9.424358                  0.358832                  719                      -0.041389                -5.828584                                  -5.828584                               -5.828584                         0.381085            719                -0.061591          -9.313300                            -9.313300                         -9.313300                   0.344924                      719                          -0.070811                   -10.603270                                     -10.603270                                  -10.603270                             0.333797           0.0     75.556595 skel_8a3e91f81074ce44      0.999425       1.000000
a7ff24r_fa589cfab1b7ea13                                         CSRank(trade_return_1h)                      price_like     single L7_ranked_future_return                1                    -1.0                            3                 True                  0.254317                     0.021627    True                   5.828584                5.828584       True               0.070411               0.069811                0.068811         95.866667 A7FF25R3S07_RANK_LABEL_DIAGNOSTIC_CLUE           719               -0.072695         -9.424358                           -9.424358                        -9.424358                  0.358832                  719                      -0.041389                -5.828584                                  -5.828584                               -5.828584                         0.381085            719                -0.061591          -9.313300                            -9.313300                         -9.313300                   0.344924                      719                          -0.070811                   -10.603270                                     -10.603270                                  -10.603270                             0.333797           0.0     75.556595 skel_f6a3f0b03e9258f2      0.999425       1.000000
a7ff24r_8ebedefc7d746058                                                 trade_return_1h                      price_like     single L7_ranked_future_return                1                    -1.0                            3                 True                  0.311912                     0.021627    True                   5.828584                5.828584       True               0.070411               0.069811                0.068811         95.866667 A7FF25R3S07_RANK_LABEL_DIAGNOSTIC_CLUE           719               -0.072695         -9.424358                           -9.424358                        -9.424358                  0.358832                  719                      -0.041389                -5.828584                                  -5.828584                               -5.828584                         0.381085            719                -0.061591          -9.313300                            -9.313300                         -9.313300                   0.344924                      719                          -0.070811                   -10.603270                                     -10.603270                                  -10.603270                             0.333797           0.0     75.498999 skel_ca36cd3eaf5a3a94      0.999425       0.964450
a7ff24r_387cb9fa56b98f16           Mean(Mul(Mean(realized_vol_24h,2),trade_return_1h),4)      price_like|volatility_like smooth_mul L7_ranked_future_return                4                    -1.0                            3                 True                  0.642982                     0.028142    True                   3.155802                3.976631       True               0.050319               0.049719                0.048719         95.466667 A7FF25R3S07_RANK_LABEL_DIAGNOSTIC_CLUE           712               -0.064455         -7.885652                           -3.821453                        -4.704746                  0.398876                  716                      -0.047535                -6.212522                                  -3.155802                               -3.976631                         0.405028            716                -0.049402          -7.114086                            -3.424597                         -4.640706                   0.400838                      716                          -0.050719                    -7.230546                                      -3.990365                                   -4.378094                             0.398045           0.0     55.075952 skel_8184698cb7b24c02      0.826199       0.999312
a7ff24r_4406baa85f52f7be                   Mul(realized_vol_168h,Sign(realized_vol_24h)) volatility_like|volatility_like gated_sign L7_ranked_future_return                1                    -1.0                            3                 True                  0.879498                     0.034714    True                   2.586084                2.586084       True               0.035754               0.035154                0.034154         95.866667 A7FF25R3S07_RANK_LABEL_DIAGNOSTIC_CLUE           719               -0.036180         -3.863790                           -3.863790                        -3.863790                  0.429764                  719                      -0.024526                -2.586084                                  -2.586084                               -2.586084                         0.449235            719                -0.028914          -4.087612                            -4.087612                         -4.087612                   0.425591                      719                          -0.036154                    -4.955280                                      -4.955280                                   -4.955280                             0.417246           0.0     40.274191 skel_d9d4f69744bac825      0.827348       1.000000
a7ff24r_45543c1709930636 Mean(Mul(realized_vol_168h,ZScore(Mean(realized_vol_24h,2))),4) volatility_like|volatility_like smooth_mul L7_ranked_future_return                1                    -1.0                            3                 True                  0.998945                     0.030604    True                   1.851876                1.851876       True               0.032736               0.032136                0.031136         95.866667 A7FF25R3S07_RANK_LABEL_DIAGNOSTIC_CLUE           715               -0.038522         -4.214043                           -4.214043                        -4.214043                  0.429371                  719                      -0.015636                -1.851876                                  -1.851876                               -1.851876                         0.471488            719                -0.020447          -2.816150                            -2.816150                         -2.816150                   0.449235                      719                          -0.033136                    -5.257271                                      -5.257271                                   -5.257271                             0.420028           0.0     37.136792 skel_44a246af570899bb      0.826199       1.000000
```

## Boundary

```text
No May/post-selection stress is used in scoring or authorization.
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
L7 ranked-return rows remain diagnostic-only and cannot promote without non-L7 support.
```
