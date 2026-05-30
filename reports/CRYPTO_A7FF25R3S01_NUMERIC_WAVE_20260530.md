# CRYPTO A7FF-25R3S01 EXPANDED NUMERIC PROBE

Generated: 2026-05-30T08:22:09Z

## Decision

`PASS_A7FF25R3S01_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH`

A7FF-25R3S01 materializes the A7FF-7E selected blueprint queue and evaluates label response, controls, non-overlap statistics, and a dry portfolio marginal proxy. It is not formula search or alpha proof.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FF25R3S01_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH",
  "executes_generation": false,
  "executes_numeric_probe": true,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T08:22:09Z",
  "input_blueprint_count": 200,
  "label_response_rows": 2980,
  "materialized_activity_ok_count": 149,
  "non_l7_numeric_clue_rows": 31,
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
  "portfolio_queue_count": 45,
  "queue_limit": 200,
  "queue_offset": 0,
  "queue_path": "D:\\HermesWorker\\GDrive\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519_remote\\runtime\\a7ff24r_dry_generation_plan\\a7ff24r_company_shard_01_queue.csv",
  "queue_total_rows": 200,
  "rank_label_diagnostic_clue_rows": 60,
  "selected_portfolio_queue_count": 9,
  "stage": "A7FF-25R3S01",
  "uses_may": false
}
```

## Decision Counts

```text
                              decision                       label_family  count
              A7FF25R3S01_NUMERIC_CLUE              L0_raw_forward_return      8
              A7FF25R3S01_NUMERIC_CLUE L1_cross_sectional_relative_return      8
              A7FF25R3S01_NUMERIC_CLUE  L3_liquidity_tier_relative_return      9
              A7FF25R3S01_NUMERIC_CLUE             L5_vol_adjusted_return      6
A7FF25R3S01_RANK_LABEL_DIAGNOSTIC_CLUE            L7_ranked_future_return     60
    HOLD_A7FF25R3S01_CONTROL_DOMINATED              L0_raw_forward_return    125
    HOLD_A7FF25R3S01_CONTROL_DOMINATED L1_cross_sectional_relative_return    124
    HOLD_A7FF25R3S01_CONTROL_DOMINATED  L3_liquidity_tier_relative_return    128
    HOLD_A7FF25R3S01_CONTROL_DOMINATED             L5_vol_adjusted_return    116
    HOLD_A7FF25R3S01_CONTROL_DOMINATED            L7_ranked_future_return    211
  HOLD_A7FF25R3S01_COST2_PROXY_FRAGILE              L0_raw_forward_return      1
  HOLD_A7FF25R3S01_COST2_PROXY_FRAGILE L1_cross_sectional_relative_return      1
  HOLD_A7FF25R3S01_COST2_PROXY_FRAGILE  L3_liquidity_tier_relative_return      1
  HOLD_A7FF25R3S01_ONE_BAR_LAG_FRAGILE              L0_raw_forward_return     25
  HOLD_A7FF25R3S01_ONE_BAR_LAG_FRAGILE L1_cross_sectional_relative_return     26
  HOLD_A7FF25R3S01_ONE_BAR_LAG_FRAGILE  L3_liquidity_tier_relative_return     30
  HOLD_A7FF25R3S01_ONE_BAR_LAG_FRAGILE             L5_vol_adjusted_return     34
  HOLD_A7FF25R3S01_ONE_BAR_LAG_FRAGILE            L7_ranked_future_return     54
     HOLD_A7FF25R3S01_PRE_MAY_UNSTABLE              L0_raw_forward_return    437
     HOLD_A7FF25R3S01_PRE_MAY_UNSTABLE L1_cross_sectional_relative_return    437
     HOLD_A7FF25R3S01_PRE_MAY_UNSTABLE  L3_liquidity_tier_relative_return    428
     HOLD_A7FF25R3S01_PRE_MAY_UNSTABLE             L5_vol_adjusted_return    440
     HOLD_A7FF25R3S01_PRE_MAY_UNSTABLE            L7_ranked_future_return    271
```

## Family Summary

```text
                        semantic_pair                               decision  count
basis_premium_like|basis_premium_like               A7FF25R3S01_NUMERIC_CLUE     31
basis_premium_like|basis_premium_like A7FF25R3S01_RANK_LABEL_DIAGNOSTIC_CLUE     60
basis_premium_like|basis_premium_like     HOLD_A7FF25R3S01_CONTROL_DOMINATED    704
basis_premium_like|basis_premium_like   HOLD_A7FF25R3S01_COST2_PROXY_FRAGILE      3
basis_premium_like|basis_premium_like   HOLD_A7FF25R3S01_ONE_BAR_LAG_FRAGILE    169
basis_premium_like|basis_premium_like      HOLD_A7FF25R3S01_PRE_MAY_UNSTABLE   2013
```

## Control Summary

```text
             control  median_ratio     max_ratio  rows
         one_bar_lag      0.831395   9159.000000  8940
 same_family_placebo      0.360128   8815.000000  8940
           sign_flip      0.997249  16784.000000  8940
      symbol_shuffle      0.533371  16176.000000  8940
        time_shuffle      0.508841  31681.983003  8940
wrong_lag_future_24h      1.288239  76657.000000  8940
wrong_lag_stale_168h      0.630945 110323.000001  8940
```

## Selected Portfolio Queue

```text
            blueprint_id                                                                                   expression                         semantic_pair       motif            label_family  label_horizon_h  orientation_from_train  premay_positive_split_count  premay_all_positive  control_ratio_premay_max  one_bar_lag_recent_oriented  lag_ok  robust_median_tstat_floor  robust_min_tstat_floor  robust_ok  cost2_recent_oriented  cost5_recent_oriented  cost10_recent_oriented  avg_n_obs_recent                               decision  train_2024_n  train_2024_mean_spread  train_2024_tstat  train_2024_nonoverlap_median_tstat  train_2024_nonoverlap_min_tstat  train_2024_positive_rate  validation_2025H1_n  validation_2025H1_mean_spread  validation_2025H1_tstat  validation_2025H1_nonoverlap_median_tstat  validation_2025H1_nonoverlap_min_tstat  validation_2025H1_positive_rate  test_2025H2_n  test_2025H2_mean_spread  test_2025H2_tstat  test_2025H2_nonoverlap_median_tstat  test_2025H2_nonoverlap_min_tstat  test_2025H2_positive_rate  recent_oos_2026JanApr_n  recent_oos_2026JanApr_mean_spread  recent_oos_2026JanApr_tstat  recent_oos_2026JanApr_nonoverlap_median_tstat  recent_oos_2026JanApr_nonoverlap_min_tstat  recent_oos_2026JanApr_positive_rate  non_l7_bonus  score_no_may          skeleton_key  finite_share  nonzero_share
a7ff24r_2fff7c49f91def0b                         Sub(CSRank(mark_index_basis_bps),CSRank(Delta(premium_close_bps,4))) basis_premium_like|basis_premium_like spread_rank  L5_vol_adjusted_return                4                    -1.0                            3                 True                  0.753570                     0.122466    True                   0.857107                1.207524       True               0.161775               0.161175                0.160175         95.466667               A7FF25R3S01_NUMERIC_CLUE           712               -0.000484         -0.026417                           -0.086786                        -0.775330                  0.511236                  716                      -0.035042                -1.537089                                  -0.857107                               -1.207524                         0.477654            716                -0.082813          -2.929820                            -1.368809                         -1.982736                   0.449721                      716                          -0.162175                    -4.279175                                      -2.191685                                   -3.717857                             0.460894           1.0    167.421608 skel_1a1b3fb29dff7328      0.998564       0.976670
a7ff24r_09dc2d7e51641cb0                                         Sub(Delta(mark_index_basis_bps,8),premium_close_bps) basis_premium_like|basis_premium_like         sub  L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.590707                     0.027157    True                   4.246743                4.246743       True               0.085688               0.085088                0.084088         95.866667               A7FF25R3S01_NUMERIC_CLUE           711               -0.005372         -0.549633                           -0.549633                        -0.549633                  0.497890                  719                      -0.062990                -5.911178                                  -5.911178                               -5.911178                         0.410292            719                -0.103456          -7.638571                            -7.638571                         -7.638571                   0.357441                      719                          -0.086088                    -4.246743                                      -4.246743                                   -4.246743                             0.415855           1.0     91.497682 skel_0994b3a36a4d53ba      0.997415       0.997849
a7ff24r_14bb4d389b4b94f0                                  Sub(ZScore(Mean(mark_index_basis_bps,8)),premium_close_bps) basis_premium_like|basis_premium_like         sub  L5_vol_adjusted_return                1                     1.0                            3                 True                  0.798537                     0.025877    True                   3.713592                3.713592       True               0.080279               0.079679                0.078679         95.866667               A7FF25R3S01_NUMERIC_CLUE           712                0.024736          2.345967                            2.345967                         2.345967                  0.557584                  719                       0.044569                 4.058438                                   4.058438                                4.058438                         0.566064            719                 0.050582           3.713592                             3.713592                          3.713592                   0.556328                      719                           0.080679                     3.946381                                       3.946381                                    3.946381                             0.557719           1.0     85.880186 skel_97ea9710bb50e137      0.997702       1.000000
a7ff24r_74bac53380235423                 Mean(Mul(Mean(mark_index_basis_bps,2),ZScore(Mean(premium_close_bps,12))),4) basis_premium_like|basis_premium_like  smooth_mul L7_ranked_future_return                8                    -1.0                            3                 True                  0.878264                     0.047770    True                   0.850856                1.597016       True               0.050562               0.049962                0.048962         94.933333 A7FF25R3S01_RANK_LABEL_DIAGNOSTIC_CLUE           698               -0.014237         -2.484986                           -0.782867                        -1.336468                  0.468481                  712                      -0.031786                -6.284066                                  -2.294183                               -3.424573                         0.411517            712                -0.012530          -2.036186                            -0.850856                         -1.597016                   0.459270                      712                          -0.050962                    -8.527866                                      -3.005991                                   -3.631776                             0.365169           0.0     55.083262 skel_bb02868db9f6b779      0.995691       0.999892
a7ff24r_83fba2ff544d6c2c                  Sub(CSRank(mark_index_basis_bps),CSRank(ZScore(Mean(premium_close_bps,8)))) basis_premium_like|basis_premium_like spread_rank L7_ranked_future_return                4                    -1.0                            3                 True                  0.350274                     0.007835    True                   2.277401                3.208589       True               0.024867               0.024267                0.023267         95.466667 A7FF25R3S01_RANK_LABEL_DIAGNOSTIC_CLUE           709               -0.017024         -3.006290                           -1.380432                        -2.217610                  0.455571                  716                      -0.032592                -5.963950                                  -2.987869                               -3.208589                         0.406425            716                -0.039129          -7.270477                            -3.465546                         -5.043283                   0.391061                      716                          -0.025267                    -4.389010                                      -2.277401                                   -3.342908                             0.446927           0.0     29.917200 skel_a923757a8885923c      0.997702       0.974329
a7ff24r_de4d4f32c64589a1         Sub(CSRank(Delta(mark_index_basis_bps,1)),CSRank(ZScore(Mean(premium_close_bps,4)))) basis_premium_like|basis_premium_like spread_rank L7_ranked_future_return                4                    -1.0                            3                 True                  0.550539                     0.013675    True                   2.109830                2.979628       True               0.024141               0.023541                0.022541         95.466667 A7FF25R3S01_RANK_LABEL_DIAGNOSTIC_CLUE           713               -0.015588         -2.788821                           -1.527806                        -1.686563                  0.447405                  716                      -0.032327                -6.233317                                  -2.793987                               -4.489324                         0.403631            716                -0.026254          -4.842137                            -2.459947                         -3.219033                   0.435754                      716                          -0.024541                    -4.431304                                      -2.109830                                   -2.979628                             0.424581           0.0     28.990806 skel_af8c1327eb17d836      0.998851       0.987082
a7ff24r_09e584f1f393b596                          Sub(CSRank(Mean(mark_index_basis_bps,8)),CSRank(premium_close_bps)) basis_premium_like|basis_premium_like spread_rank L7_ranked_future_return               24                     1.0                            3                 True                  0.726542                     0.021409    True                   0.559407               -1.985629       True               0.023746               0.023146                0.022146         92.800000 A7FF25R3S01_RANK_LABEL_DIAGNOSTIC_CLUE           689                0.003019          0.495408                            0.089422                        -1.864349                  0.535559                  696                       0.011688                 2.121869                                   0.559407                               -1.985629                         0.534483            696                 0.043962           7.232634                             1.300221                          0.531342                   0.600575                      696                           0.024146                     4.075354                                       0.938220                                   -0.526018                             0.568966           0.0     28.419129 skel_51c2bb588b20fa9e      0.997702       0.978558
a7ff24r_c3947ce389442b47 Sub(CSRank(ZScore(Mean(mark_index_basis_bps,12))),CSRank(ZScore(Mean(premium_close_bps,2)))) basis_premium_like|basis_premium_like spread_rank L7_ranked_future_return                1                     1.0                            3                 True                  0.930251                     0.017280    True                   1.462326                1.462326       True               0.020656               0.020056                0.019056         95.866667 A7FF25R3S01_RANK_LABEL_DIAGNOSTIC_CLUE           708                0.016417          2.689850                            2.689850                         2.689850                  0.555085                  719                       0.008724                 1.462326                                   1.462326                                1.462326                         0.527121            719                 0.020544           3.615265                             3.615265                          3.615265                   0.542420                      719                           0.021056                     3.710234                                       3.710234                                    3.710234                             0.566064           0.0     25.125490 skel_f4061a64df347a31      0.996553       0.974182
a7ff24r_e4dadb1d3812b09b                  Sub(CSRank(ZScore(Mean(mark_index_basis_bps,8))),CSRank(premium_close_bps)) basis_premium_like|basis_premium_like spread_rank L7_ranked_future_return                1                     1.0                            3                 True                  0.776032                     0.009229    True                   3.325774                3.325774       True               0.019462               0.018862                0.017862         95.866667 A7FF25R3S01_RANK_LABEL_DIAGNOSTIC_CLUE           712                0.014465          2.436324                            2.436324                         2.436324                  0.537921                  719                       0.020095                 3.619772                                   3.619772                                3.619772                         0.532684            719                 0.020959           3.500766                             3.500766                          3.500766                   0.564673                      719                           0.019862                     3.325774                                       3.325774                                    3.325774                             0.550765           0.0     24.086003 skel_206e713fb3d9a164      0.997702       0.978558
```

## Boundary

```text
No May/post-selection stress is used in scoring or authorization.
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
L7 ranked-return rows remain diagnostic-only and cannot promote without non-L7 support.
```
